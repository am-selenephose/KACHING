import unittest
from datetime import datetime, timedelta, timezone
from decimal import Decimal as D
from unittest.mock import patch

from tradegate.binance_cli import BinanceCLI
from tradegate.exchange import ExchangeContractSnapshot, evaluate_contract
from tradegate.compiler import FinancialIntent

NOW = datetime(2026, 9, 8, 12, tzinfo=timezone.utc)


def valid_contract(**changes):
    values = dict(
        symbol='BNBUSDT', status='TRADING', order_types=('LIMIT', 'MARKET'),
        quote_order_qty_market_allowed=True, min_notional=D('5'), max_notional=None,
        source='fixture', observed_at=NOW.isoformat(),
    )
    values.update(changes)
    return ExchangeContractSnapshot(**values)


class ExchangeContractTests(unittest.TestCase):
    def setUp(self):
        self.intent = FinancialIntent('agent', 'BUY', 'BNBUSDT', D('10'))

    def test_valid_contract_is_admissible(self):
        result = evaluate_contract(valid_contract(), self.intent, NOW)
        self.assertTrue(result.admissible)
        self.assertEqual(result.reasons, ())

    def test_halted_or_unsupported_market_fails_closed(self):
        cases = [
            (valid_contract(status='BREAK'), 'EXCHANGE_SYMBOL_NOT_TRADING'),
            (valid_contract(order_types=('LIMIT',)), 'EXCHANGE_MARKET_ORDER_UNAVAILABLE'),
            (valid_contract(quote_order_qty_market_allowed=False), 'EXCHANGE_QUOTE_ORDER_QTY_UNAVAILABLE'),
        ]
        for contract, reason in cases:
            with self.subTest(reason=reason):
                result = evaluate_contract(contract, self.intent, NOW)
                self.assertFalse(result.admissible)
                self.assertIn(reason, result.reasons)
    def test_notional_and_freshness_are_enforced(self):
        low = evaluate_contract(valid_contract(min_notional=D('11')), self.intent, NOW)
        stale = evaluate_contract(
            valid_contract(observed_at=(NOW - timedelta(seconds=61)).isoformat()),
            self.intent, NOW,
        )
        self.assertIn('EXCHANGE_MIN_NOTIONAL', low.reasons)
        self.assertIn('EXCHANGE_CONTRACT_STALE', stale.reasons)

    def test_symbol_and_malformed_contract_fail_closed(self):
        mismatch = evaluate_contract(valid_contract(symbol='ETHUSDT'), self.intent, NOW)
        malformed = evaluate_contract(valid_contract(min_notional=D('NaN')), self.intent, NOW)
        self.assertIn('EXCHANGE_SYMBOL_MISMATCH', mismatch.reasons)
        self.assertIn('EXCHANGE_CONTRACT_INVALID', malformed.reasons)

    def test_exchange_info_parser_extracts_market_contract(self):
        payload = {'symbols': [{
            'symbol': 'BNBUSDT', 'status': 'TRADING',
            'orderTypes': ['LIMIT', 'MARKET'], 'quoteOrderQtyMarketAllowed': True,
            'filters': [{'filterType': 'NOTIONAL', 'minNotional': '5',
                         'maxNotional': '1000', 'applyMaxToMarket': True}],
        }]}
        with patch.object(BinanceCLI, '_rest', return_value=payload):
            contract = BinanceCLI().exchange_contract('BNBUSDT')
        self.assertEqual(contract.symbol, 'BNBUSDT')
        self.assertEqual(contract.min_notional, D('5'))
        self.assertEqual(contract.max_notional, D('1000'))
        self.assertEqual(contract.source, 'binance-rest-fallback:exchange-info')

    def test_exchange_info_parser_rejects_malformed_payload(self):
        with patch.object(BinanceCLI, '_rest', return_value={'symbols': []}):
            with self.assertRaises(Exception):
                BinanceCLI().exchange_contract('BNBUSDT')


if __name__ == '__main__':
    unittest.main()
