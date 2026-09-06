from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from .models import AccountSnapshot, MarketSnapshot, RiskDecision, TradeIntent, Verdict


@dataclass(frozen=True)
class RiskPolicy:
    version: str = "tradegate-0.2"
    max_quote_notional: Decimal = Decimal("250")
    max_spread_bps: Decimal = Decimal("18")
    review_spread_bps: Decimal = Decimal("10")
    max_abs_24h_move_pct: Decimal = Decimal("18")
    review_abs_24h_move_pct: Decimal = Decimal("10")
    min_depth_multiple: Decimal = Decimal("8")
    min_cash_buffer_usdt: Decimal = Decimal("25")
    max_balance_fraction: Decimal = Decimal("0.20")


class TradeGovernor:
    def __init__(self, policy: RiskPolicy | None = None) -> None:
        self.policy = policy or RiskPolicy()

    def evaluate(
        self,
        intent: TradeIntent,
        market: MarketSnapshot,
        account: AccountSnapshot,
    ) -> RiskDecision:
        intent = intent.normalized()
        blocking: list[str] = []
        review: list[str] = []

        if not account.authenticated:
            return self._block("ACCOUNT_AUTH_UNAVAILABLE", market, account)
        if market.symbol != intent.symbol:
            return self._block("SYMBOL_MISMATCH", market, account)
        if (
            market.bid <= 0
            or market.ask <= 0
            or market.last_price <= 0
            or market.ask < market.bid
        ):
            return self._block("INVALID_MARKET_SNAPSHOT", market, account)

        spread = market.spread_bps
        move = abs(market.price_change_pct_24h)
        side_depth = (
            market.ask_depth_usdt if intent.side == "BUY" else market.bid_depth_usdt
        )
        depth_multiple = (
            side_depth / intent.quote_notional
            if intent.quote_notional > 0
            else Decimal("0")
        )

        if spread > self.policy.max_spread_bps:
            blocking.append("SPREAD_TOO_WIDE")
        elif spread > self.policy.review_spread_bps:
            review.append("SPREAD_ELEVATED")

        if move > self.policy.max_abs_24h_move_pct:
            blocking.append("EXTREME_24H_MOVE")
        elif move > self.policy.review_abs_24h_move_pct:
            review.append("HIGH_24H_MOVE")

        if depth_multiple < self.policy.min_depth_multiple:
            blocking.append("INSUFFICIENT_VISIBLE_DEPTH")

        max_by_balance = max(
            Decimal("0"),
            min(
                account.free_usdt * self.policy.max_balance_fraction,
                account.free_usdt - self.policy.min_cash_buffer_usdt,
            ),
        )
        approved = min(
            intent.quote_notional,
            self.policy.max_quote_notional,
            max_by_balance,
        )

        if (
            intent.side == "BUY"
            and account.free_usdt
            < intent.quote_notional + self.policy.min_cash_buffer_usdt
        ):
            blocking.append("CASH_BUFFER_BREACH")
        if approved <= 0:
            blocking.append("NO_SAFE_NOTIONAL")

        metrics = {
            "spread_bps": f"{spread:.4f}",
            "abs_24h_move_pct": f"{move:.4f}",
            "visible_depth_multiple": f"{depth_multiple:.4f}",
            "free_usdt": str(account.free_usdt),
            "requested_quote_notional": str(intent.quote_notional),
            "approved_quote_notional": str(max(Decimal("0"), approved)),
        }

        if blocking:
            return RiskDecision(
                Verdict.BLOCK,
                Decimal("0"),
                tuple(blocking),
                self.policy.version,
                metrics,
            )

        if review or approved < intent.quote_notional:
            if approved < intent.quote_notional:
                review.append("SIZE_REDUCED_BY_POLICY")
            return RiskDecision(
                Verdict.REVIEW,
                approved,
                tuple(review) or ("HUMAN_REVIEW_REQUIRED",),
                self.policy.version,
                metrics,
            )

        return RiskDecision(
            Verdict.ALLOW,
            approved,
            ("ALL_CHECKS_PASSED",),
            self.policy.version,
            metrics,
        )

    def _block(
        self,
        reason: str,
        market: MarketSnapshot,
        account: AccountSnapshot,
    ) -> RiskDecision:
        return RiskDecision(
            Verdict.BLOCK,
            Decimal("0"),
            (reason,),
            self.policy.version,
            {
                "spread_bps": str(market.spread_bps),
                "free_usdt": str(account.free_usdt),
            },
        )
