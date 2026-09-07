from __future__ import annotations

import argparse
import json
from decimal import Decimal
from pathlib import Path

from .binance_cli import BinanceCLI, BinanceCLIError
from .evidence import build_evidence_packet, verify_evidence_packet
from .governor import TradeGovernor
from .models import AccountSnapshot, TradeIntent, Verdict


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(
        description="EvidenceBound TradeGate for Binance Agent OS"
    )
    result.add_argument("--symbol", default="BNBUSDT")
    result.add_argument("--side", choices=["BUY", "SELL"], default="BUY")
    result.add_argument("--quote", type=Decimal, required=True)
    result.add_argument(
        "--evidence-out",
        type=Path,
        default=Path("tradegate-evidence.json"),
    )
    result.add_argument("--order-test", action="store_true")
    return result


def main() -> int:
    args = parser().parse_args()
    intent = TradeIntent(args.symbol, args.side, args.quote).normalized()
    cli = BinanceCLI()

    try:
        market = cli.market_snapshot(intent.symbol)
    except BinanceCLIError as exc:
        parser().error(str(exc))

    try:
        account = cli.account_snapshot()
    except BinanceCLIError as exc:
        account = AccountSnapshot(
            Decimal("0"),
            "binance-cli:account-unavailable",
            False,
            str(exc),
        )

    decision = TradeGovernor().evaluate(intent, market, account)
    packet = build_evidence_packet(intent, market, account, decision)
    display_metrics = dict(decision.metrics)
    if "free_usdt" in display_metrics:
        display_metrics["free_usdt"] = "[REDACTED]"
    args.evidence_out.write_text(
        json.dumps(packet, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    print(
        json.dumps(
            {
                "verdict": decision.verdict.value,
                "approved_quote_notional": str(decision.approved_quote_notional),
                "reasons": list(decision.reasons),
                "metrics": display_metrics,
                "market_source": market.source,
                "account_source": account.source,
                "account_authenticated": account.authenticated,
                "evidence_sha256": packet["evidence_sha256"],
                "evidence_verified": verify_evidence_packet(packet),
                "evidence_file": str(args.evidence_out),
            },
            indent=2,
        )
    )

    if args.order_test:
        if decision.verdict == Verdict.BLOCK:
            parser().error(
                "risk governor blocked the intent; refusing Binance order-test"
            )
        try:
            result = cli.test_market_order(
                intent.symbol,
                intent.side,
                decision.approved_quote_notional,
            )
        except BinanceCLIError as exc:
            parser().error(str(exc))
        print(json.dumps({"binance_order_test": result}, indent=2))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
