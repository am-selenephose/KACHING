from __future__ import annotations

import json
import os
import shutil
import subprocess
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any

from .models import AccountSnapshot, MarketSnapshot
from .exchange import ExchangeContractSnapshot


class BinanceCLIError(RuntimeError):
    """Raised when Binance CLI or public REST observation fails."""


class BinanceCLI:
    def __init__(self, executable: str = "binance-cli") -> None:
        self.executable = executable

    def resolved_executable(self) -> str | None:
        found = shutil.which(self.executable)
        if found:
            return found

        cargo_bin = os.path.expanduser("~/.cargo/bin/binance-cli")
        if (
            self.executable == "binance-cli"
            and os.path.isfile(cargo_bin)
            and os.access(cargo_bin, os.X_OK)
        ):
            return cargo_bin
        return None

    def _run(self, *args: str) -> Any:
        executable = self.resolved_executable()
        if executable is None:
            raise BinanceCLIError("binance-cli not found")

        try:
            process = subprocess.run(
                [executable, *args],
                capture_output=True,
                text=True,
                stdin=subprocess.DEVNULL,
                timeout=8,
                check=False,
            )
        except subprocess.TimeoutExpired as exc:
            raise BinanceCLIError("binance-cli timed out") from exc

        if process.returncode != 0:
            raise BinanceCLIError("binance-cli failed; inspect private CLI diagnostics locally")

        try:
            return json.loads(process.stdout.strip())
        except json.JSONDecodeError as exc:
            raise BinanceCLIError("binance-cli returned invalid JSON") from exc

    @staticmethod
    def _unwrap(payload: Any) -> Any:
        if isinstance(payload, dict):
            for key in ("data", "result", "body"):
                if payload.get(key) is not None:
                    return payload[key]
        return payload

    @staticmethod
    def _rest(path: str, **params: str) -> Any:
        query = urllib.parse.urlencode(params)
        url = "https://api.binance.com" + path + ("?" + query if query else "")
        request = urllib.request.Request(
            url,
            headers={"User-Agent": "EvidenceBound-TradeGate/0.2"},
        )
        try:
            with urllib.request.urlopen(request, timeout=10) as response:
                return json.loads(response.read().decode("utf-8"))
        except Exception as exc:
            raise BinanceCLIError("Binance public observation unavailable") from exc

    def market_snapshot(self, symbol: str, depth_levels: int = 20) -> MarketSnapshot:
        symbol = symbol.upper()
        observed_at = datetime.now(timezone.utc).isoformat()
        try:
            book = self._unwrap(
                self._run("spot", "ticker-book-ticker", "--symbol", symbol)
            )
            ticker = self._unwrap(
                self._run("spot", "ticker24hr", "--symbol", symbol, "--rtype", "FULL")
            )
            depth = self._unwrap(
                self._run("spot", "depth", "--symbol", symbol, "--limit", str(depth_levels))
            )
            source = "binance-cli:spot"
        except BinanceCLIError:
            book = self._rest("/api/v3/ticker/bookTicker", symbol=symbol)
            ticker = self._rest("/api/v3/ticker/24hr", symbol=symbol)
            depth = self._rest("/api/v3/depth", symbol=symbol, limit=str(depth_levels))
            source = "binance-rest-fallback:spot"

        def side_depth(rows: list[list[str]]) -> Decimal:
            return sum(
                (Decimal(str(price)) * Decimal(str(qty)) for price, qty in rows),
                Decimal("0"),
            )

        return MarketSnapshot(
            symbol=symbol,
            bid=Decimal(str(book["bidPrice"])),
            ask=Decimal(str(book["askPrice"])),
            last_price=Decimal(str(ticker["lastPrice"])),
            price_change_pct_24h=Decimal(str(ticker["priceChangePercent"])),
            bid_depth_usdt=side_depth(depth.get("bids", [])),
            ask_depth_usdt=side_depth(depth.get("asks", [])),
            source=source,
            observed_at=observed_at,
        )

    def exchange_contract(self, symbol: str) -> ExchangeContractSnapshot:
        symbol = symbol.upper()
        observed_at = datetime.now(timezone.utc).isoformat()
        payload = self._rest("/api/v3/exchangeInfo", symbol=symbol)
        rows = payload.get("symbols") if isinstance(payload, dict) else None
        if not isinstance(rows, list) or len(rows) != 1 or not isinstance(rows[0], dict):
            raise BinanceCLIError("Malformed exchange contract observation")
        row = rows[0]
        if row.get("symbol") != symbol:
            raise BinanceCLIError("Exchange contract symbol mismatch")
        filters = row.get("filters")
        if not isinstance(filters, list):
            raise BinanceCLIError("Exchange filters missing")
        min_notional = Decimal("0")
        max_notional = None
        try:
            for item in filters:
                if not isinstance(item, dict):
                    continue
                kind = item.get("filterType")
                if kind == "NOTIONAL":
                    min_notional = Decimal(str(item.get("minNotional", "0")))
                    if item.get("applyMaxToMarket") is True:
                        max_notional = Decimal(str(item.get("maxNotional", "0")))
                elif kind == "MIN_NOTIONAL":
                    min_notional = Decimal(str(item.get("minNotional", "0")))
        except Exception as exc:
            raise BinanceCLIError("Malformed exchange notional filter") from exc
        order_types = row.get("orderTypes")
        if not isinstance(order_types, list) or not all(isinstance(v, str) for v in order_types):
            raise BinanceCLIError("Exchange order types missing")
        return ExchangeContractSnapshot(
            symbol=symbol, status=str(row.get("status", "")),
            order_types=tuple(order_types),
            quote_order_qty_market_allowed=row.get("quoteOrderQtyMarketAllowed") is True,
            min_notional=min_notional, max_notional=max_notional,
            source="binance-rest-fallback:exchange-info", observed_at=observed_at,
        )

    def account_snapshot(self) -> AccountSnapshot:
        payload = self._unwrap(
            self._run("spot", "get-account", "--omit-zero-balances", "false")
        )
        if not isinstance(payload, dict) or not isinstance(payload.get('balances'), list):
            raise BinanceCLIError('Malformed account observation')
        if not isinstance(payload.get('canTrade'), bool):
            raise BinanceCLIError('Account trading permission missing')
        balances = payload['balances']
        for row in balances:
            if row.get("asset") == "USDT":
                return AccountSnapshot(
                    free_usdt=Decimal(str(row.get("free", "0"))),
                    source="binance-cli:account",
                    trading_enabled=payload['canTrade'],
                )
        return AccountSnapshot(Decimal("0"), "binance-cli:account", trading_enabled=payload['canTrade'])

    def test_market_order(
        self,
        symbol: str,
        side: str,
        quote_order_qty: Decimal,
    ) -> Any:
        return self._run(
            "spot",
            "order-test",
            "--symbol",
            symbol.upper(),
            "--side",
            side.upper(),
            "--rtype",
            "MARKET",
            "--quote-order-qty",
            str(quote_order_qty),
            "--compute-commission-rates",
            "false",
        )
