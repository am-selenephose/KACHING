from decimal import Decimal
import unittest

from tradegate.evidence import build_evidence_packet, verify_evidence_packet
from tradegate.governor import TradeGovernor
from tradegate.models import AccountSnapshot, MarketSnapshot, TradeIntent, Verdict


def market(move="2.5", bid_depth="50000", ask_depth="50000"):
    return MarketSnapshot(
        symbol="BNBUSDT", bid=Decimal("750"), ask=Decimal("750.1"),
        last_price=Decimal("750.05"), price_change_pct_24h=Decimal(move),
        bid_depth_usdt=Decimal(bid_depth), ask_depth_usdt=Decimal(ask_depth),
        source="fixture", observed_at="2026-09-07T00:00:00Z",
    )


class TradeGateTests(unittest.TestCase):
    def test_missing_auth_blocks(self):
        decision = TradeGovernor().evaluate(
            TradeIntent("BNBUSDT", "BUY", Decimal("10")), market(),
            AccountSnapshot(Decimal("100"), authenticated=False),
        )
        self.assertEqual(decision.verdict, Verdict.BLOCK)
        self.assertIn("ACCOUNT_AUTH_UNAVAILABLE", decision.reasons)

    def test_cash_buffer_blocks(self):
        decision = TradeGovernor().evaluate(
            TradeIntent("BNBUSDT", "BUY", Decimal("10")), market(),
            AccountSnapshot(Decimal("0"), authenticated=True),
        )
        self.assertEqual(decision.verdict, Verdict.BLOCK)
        self.assertIn("CASH_BUFFER_BREACH", decision.reasons)

    def test_safe_small_intent_allows(self):
        decision = TradeGovernor().evaluate(
            TradeIntent("BNBUSDT", "BUY", Decimal("10")), market(),
            AccountSnapshot(Decimal("100"), authenticated=True),
        )
        self.assertEqual(decision.verdict, Verdict.ALLOW)
        self.assertEqual(decision.approved_quote_notional, Decimal("10"))

    def test_high_move_requires_review(self):
        decision = TradeGovernor().evaluate(
            TradeIntent("BNBUSDT", "BUY", Decimal("10")), market(move="12"),
            AccountSnapshot(Decimal("100"), authenticated=True),
        )
        self.assertEqual(decision.verdict, Verdict.REVIEW)
        self.assertIn("HIGH_24H_MOVE", decision.reasons)

    def test_low_depth_blocks(self):
        decision = TradeGovernor().evaluate(
            TradeIntent("BNBUSDT", "BUY", Decimal("10")), market(ask_depth="40"),
            AccountSnapshot(Decimal("100"), authenticated=True),
        )
        self.assertEqual(decision.verdict, Verdict.BLOCK)
        self.assertIn("INSUFFICIENT_VISIBLE_DEPTH", decision.reasons)

    def test_evidence_hash_detects_tampering(self):
        intent = TradeIntent("BNBUSDT", "BUY", Decimal("10"))
        account = AccountSnapshot(Decimal("100"), authenticated=True)
        decision = TradeGovernor().evaluate(intent, market(), account)
        packet = build_evidence_packet(intent, market(), account, decision)
        self.assertTrue(verify_evidence_packet(packet))
        packet["decision"]["verdict"] = "BLOCK"
        self.assertFalse(verify_evidence_packet(packet))


if __name__ == "__main__":
    unittest.main()
