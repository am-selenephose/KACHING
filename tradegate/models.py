from __future__ import annotations

from dataclasses import dataclass, asdict, field
from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum
from typing import Any
import re


class Verdict(str, Enum):
    ALLOW = "ALLOW"
    REVIEW = "REVIEW"
    BLOCK = "BLOCK"


@dataclass(frozen=True)
class TradeIntent:
    symbol: str
    side: str
    quote_notional: Decimal

    def normalized(self) -> "TradeIntent":
        symbol = self.symbol.upper().strip()
        side = self.side.upper().strip()
        if side not in {"BUY", "SELL"}:
            raise ValueError("side must be BUY or SELL")
        if not re.fullmatch(r"[A-Z0-9]{2,16}USDT", symbol):
            raise ValueError("v0.2 supports USDT quote symbols only")
        if (not isinstance(self.quote_notional, Decimal)
                or not self.quote_notional.is_finite()
                or not Decimal('0') < self.quote_notional <= Decimal('1000000000000')
                or len(self.quote_notional.as_tuple().digits) > 32
                or self.quote_notional.as_tuple().exponent < -18):
            raise ValueError("quote_notional must be positive")
        return TradeIntent(symbol=symbol, side=side, quote_notional=self.quote_notional)


@dataclass(frozen=True)
class MarketSnapshot:
    symbol: str
    bid: Decimal
    ask: Decimal
    last_price: Decimal
    price_change_pct_24h: Decimal
    bid_depth_usdt: Decimal
    ask_depth_usdt: Decimal
    source: str
    observed_at: str

    @property
    def mid(self) -> Decimal:
        return (self.bid + self.ask) / Decimal("2")

    @property
    def spread_bps(self) -> Decimal:
        if self.mid <= 0:
            return Decimal("999999")
        return ((self.ask - self.bid) / self.mid) * Decimal("10000")


@dataclass(frozen=True)
class AccountSnapshot:
    free_usdt: Decimal
    source: str = "unknown"
    authenticated: bool = True
    auth_error: str = ""
    trading_enabled: bool = True
    observed_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass(frozen=True)
class RiskDecision:
    verdict: Verdict
    approved_quote_notional: Decimal
    reasons: tuple[str, ...]
    policy_version: str
    metrics: dict[str, str]

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["verdict"] = self.verdict.value
        data["approved_quote_notional"] = str(self.approved_quote_notional)
        return data
