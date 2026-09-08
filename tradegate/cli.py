from __future__ import annotations

import argparse
import json
import os
from decimal import Decimal
from pathlib import Path

from .binance_cli import BinanceCLI, BinanceCLIError
from .models import AccountSnapshot, TradeIntent
from .compiler import Compiler, FinancialIntent, human_receipt, verify_receipt


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(
        description="KACHING! — proof-carrying financial action firewall"
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
    result.add_argument("--human", action="store_true", help="Print sanitized human-readable receipt")
    return result


def main() -> int:
    args = parser().parse_args()
    try:
        intent = TradeIntent(args.symbol, args.side, args.quote).normalized()
    except ValueError:
        parser().error('Invalid financial intent')
    cli = BinanceCLI()

    try:
        market = cli.market_snapshot(intent.symbol)
    except (BinanceCLIError, ValueError, KeyError, TypeError):
        parser().error('Market observation unavailable; authorization refused')

    try:
        account = cli.account_snapshot()
    except (BinanceCLIError, ValueError, KeyError, TypeError):
        account = AccountSnapshot(
            Decimal("0"),
            "binance-cli:account-unavailable",
            False,
            "ACCOUNT_AUTH_UNAVAILABLE",
        )

    try:
        exchange_contract = cli.exchange_contract(intent.symbol)
    except (BinanceCLIError, ValueError, KeyError, TypeError):
        exchange_contract = None

    proposal = FinancialIntent('human', intent.side, intent.symbol, intent.quote_notional)
    result = Compiler().compile(proposal, market, account, exchange_contract=exchange_contract)
    receipt = result.receipt
    # Exclusive creation prevents clobbering existing evidence or following symlinks.
    try:
        fd = os.open(args.evidence_out, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except OSError:
        parser().error('Evidence path unavailable or already exists; choose a new private path')
    with os.fdopen(fd, 'w', encoding='utf-8') as stream:
        json.dump(result.private_evidence, stream, indent=2, sort_keys=True, allow_nan=False)
        stream.write('\n')
    print(human_receipt(receipt) if args.human else json.dumps({
        'receipt': receipt, 'evidence_verified': verify_receipt(receipt, receipt['decision_sha256'])}, indent=2))

    if args.order_test:
        if receipt['verdict'] != 'ALLOW':
            parser().error(
                "KACHING requires ALLOW; refusing Binance order-test"
            )
        try:
            result = cli.test_market_order(
                intent.symbol,
                intent.side,
                Decimal(receipt['authorized']),
            )
        except BinanceCLIError as exc:
            parser().error(str(exc))
        print(json.dumps({"binance_order_test": "VALIDATED_NON_EXECUTING"}))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
