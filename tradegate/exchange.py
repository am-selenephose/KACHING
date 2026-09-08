from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Any

D = Decimal


@dataclass(frozen=True)
class ExchangeContractSnapshot:
    symbol: str
    status: str
    order_types: tuple[str, ...]
    quote_order_qty_market_allowed: bool
    min_notional: Decimal
    max_notional: Decimal | None
    source: str
    observed_at: str


@dataclass(frozen=True)
class ExchangeContractEvaluation:
    admissible: bool
    reasons: tuple[str, ...]
    checks: dict[str, bool]


def _finite_nonnegative(value: Any) -> bool:
    return isinstance(value, D) and value.is_finite() and value >= 0
def evaluate_contract(
    contract: ExchangeContractSnapshot,
    intent: Any,
    now: datetime,
    *,
    max_age_seconds: int = 60,
) -> ExchangeContractEvaluation:
    reasons: list[str] = []
    if not _finite_nonnegative(contract.min_notional):
        reasons.append('EXCHANGE_CONTRACT_INVALID')
    if contract.max_notional is not None and not _finite_nonnegative(contract.max_notional):
        reasons.append('EXCHANGE_CONTRACT_INVALID')
    if contract.max_notional is not None and contract.max_notional < contract.min_notional:
        reasons.append('EXCHANGE_CONTRACT_INVALID')
    if contract.symbol != intent.symbol:
        reasons.append('EXCHANGE_SYMBOL_MISMATCH')
    if contract.status != 'TRADING':
        reasons.append('EXCHANGE_SYMBOL_NOT_TRADING')
    if 'MARKET' not in contract.order_types:
        reasons.append('EXCHANGE_MARKET_ORDER_UNAVAILABLE')
    if contract.quote_order_qty_market_allowed is not True:
        reasons.append('EXCHANGE_QUOTE_ORDER_QTY_UNAVAILABLE')
    try:
        observed = datetime.fromisoformat(contract.observed_at.replace('Z', '+00:00'))
        age = (now - observed).total_seconds()
        if not 0 <= age <= max_age_seconds:
            reasons.append('EXCHANGE_CONTRACT_STALE')
    except (ValueError, TypeError, AttributeError):
        reasons.append('EXCHANGE_CONTRACT_INVALID')
    if _finite_nonnegative(contract.min_notional) and intent.requested_quote_notional < contract.min_notional:
        reasons.append('EXCHANGE_MIN_NOTIONAL')
    if contract.max_notional is not None and _finite_nonnegative(contract.max_notional):
        if intent.requested_quote_notional > contract.max_notional:
            reasons.append('EXCHANGE_MAX_NOTIONAL')
    reasons = list(dict.fromkeys(reasons))
    return ExchangeContractEvaluation(
        admissible=not reasons,
        reasons=tuple(reasons),
        checks={'Exchange contract': not reasons},
    )
