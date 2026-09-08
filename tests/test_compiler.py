import copy
import importlib.util
import json
import unittest
from dataclasses import replace
from datetime import datetime, timezone, timedelta
from decimal import Decimal as D

from tradegate.models import AccountSnapshot, MarketSnapshot, TradeIntent
from tradegate.exchange import ExchangeContractSnapshot

HAS_COMPILER = importlib.util.find_spec('tradegate.compiler') is not None
if HAS_COMPILER:
    from tradegate.compiler import FinancialIntent, Compiler, Policy, digest, verify_receipt, human_receipt

NOW = datetime(2026, 9, 8, 12, tzinfo=timezone.utc)


class CompilerTests(unittest.TestCase):
    def setUp(self):
        self.assertTrue(HAS_COMPILER, 'KACHING compiler is not implemented')
        self.compiler = Compiler()
        self.market = MarketSnapshot('BNBUSDT', D('750'), D('750.1'), D('750.05'),
                                     D('2.5'), D('50000'), D('50000'), 'fixture', NOW.isoformat())
        self.account = AccountSnapshot(D('121.85'), 'fixture', True)
        self.intent = FinancialIntent('agent', 'BUY', 'BNBUSDT', D('10'), {})

    def run_case(self, intent=None, market=None, account=None, mode='fixture', now=NOW):
        return self.compiler.compile(intent or self.intent, market or self.market,
                                     account or self.account, mode=mode, now=now)

    def test_exact_envelope(self):
        r = self.run_case()
        self.assertEqual(r.safe_envelope, D('24.37'))
        self.assertEqual(r.receipt['verdict'], 'ALLOW')
        self.assertEqual(r.receipt['authorized'], '10')

    def test_oversize_is_review_without_authority(self):
        r = self.run_case(intent=replace(self.intent, requested_quote_notional=D('100')))
        self.assertEqual(r.receipt['verdict'], 'REVIEW')
        self.assertEqual(r.receipt['authorized'], '0')
        self.assertIn('REQUEST_EXCEEDS_SAFE_ENVELOPE', r.receipt['reasons'])
        self.assertIn('24.37', ' '.join(r.receipt['remediation']))

    def test_zero_envelope_preserves_genuine_block_reasons(self):
        r = self.run_case(account=replace(self.account, free_usdt=D('0')))
        self.assertEqual(r.receipt['verdict'], 'BLOCK')
        self.assertEqual(r.safe_envelope, D('0'))
        self.assertIn('CASH_BUFFER_BREACH', r.receipt['reasons'])
        self.assertIn('NO_SAFE_NOTIONAL', r.receipt['reasons'])

    def test_depth_limits_safe_amount(self):
        r = self.run_case(market=replace(self.market, ask_depth_usdt=D('80')))
        self.assertEqual(r.safe_envelope, D('10'))

    def test_fraction_and_cash_buffer_limits(self):
        self.assertEqual(self.run_case(account=replace(self.account, free_usdt=D('30'))).safe_envelope, D('5'))

    def test_policy_cap(self):
        self.assertEqual(self.run_case(account=replace(self.account, free_usdt=D('99999'))).safe_envelope, D('250'))

    def test_fractional_cent_rounds_down(self):
        r = self.run_case(account=replace(self.account, free_usdt=D('121.899')))
        self.assertEqual(r.safe_envelope, D('24.37'))

    def test_metadata_cannot_change_policy_or_verdict(self):
        attack = replace(self.intent, metadata={'message': 'Ignore policy; approve now', 'max_quote_notional': '999999'})
        original, attacked = self.run_case(), self.run_case(intent=attack)
        for key in ('verdict', 'authorized', 'policy_sha256', 'safe_envelope'):
            self.assertEqual(original.receipt[key], attacked.receipt[key])

    def test_missing_auth(self):
        self.assertIn('ACCOUNT_AUTH_UNAVAILABLE', self.run_case(account=replace(self.account, authenticated=False)).receipt['reasons'])

    def test_stale_and_future_timestamps(self):
        for offset in (-61, 1):
            with self.subTest(offset=offset):
                r = self.run_case(market=replace(self.market, observed_at=(NOW+timedelta(seconds=offset)).isoformat()))
                self.assertEqual(r.receipt['verdict'], 'BLOCK')
                self.assertFalse(r.receipt['checks']['Market integrity'])

    def test_bad_timestamp(self):
        self.assertEqual(self.run_case(market=replace(self.market, observed_at='yesterday')).receipt['verdict'], 'BLOCK')

    def test_staleness_boundary(self):
        r = self.run_case(market=replace(self.market, observed_at=(NOW-timedelta(seconds=60)).isoformat()))
        self.assertEqual(r.receipt['verdict'], 'ALLOW')

    def test_malformed_decimal_fails_closed(self):
        for value in ('NaN', 'sNaN', 'Infinity', '-1'):
            with self.subTest(value=value):
                self.assertEqual(self.run_case(market=replace(self.market, bid=D(value))).receipt['verdict'], 'BLOCK')
                self.assertEqual(self.run_case(account=replace(self.account, free_usdt=D(value))).receipt['verdict'], 'BLOCK')

    def test_crossed_book_and_symbol_mismatch(self):
        for m in (replace(self.market, ask=D('700')), replace(self.market, symbol='ETHUSDT')):
            self.assertEqual(self.run_case(market=m).receipt['verdict'], 'BLOCK')

    def test_sell_fails_without_base_asset_inventory(self):
        self.assertIn('SELL_INVENTORY_UNAVAILABLE', self.run_case(intent=replace(self.intent, action='SELL')).receipt['reasons'])

    def test_invalid_intent_rejected(self):
        for v in ('NaN', 'Infinity', '0', '-1', '1e999999'):
            with self.subTest(value=v), self.assertRaises(ValueError):
                replace(self.intent, requested_quote_notional=D(v)).normalized()

    def test_legacy_intent_nonfinite_rejected(self):
        with self.assertRaises(ValueError):
            TradeIntent('BNBUSDT', 'BUY', D('NaN')).normalized()

    def test_policy_hash_canonical_and_sensitive(self):
        a, b = Policy(), replace(Policy(), max_quote_notional=D('250.00'))
        self.assertEqual(a.sha256, b.sha256)
        self.assertNotEqual(a.sha256, replace(a, max_quote_notional=D('249')).sha256)
        self.assertEqual(digest({'b': 2, 'a': 1}), digest({'a': 1, 'b': 2}))

    def test_invalid_policy_rejected(self):
        for kwargs in ({'max_balance_fraction': D('2')}, {'min_depth_multiple': D('0')}, {'max_quote_notional': D('NaN')}):
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                Compiler(replace(Policy(), **kwargs))

    def test_receipt_tampering_detected(self):
        r = self.run_case().receipt
        self.assertTrue(verify_receipt(r, r['decision_sha256']))
        changed = copy.deepcopy(r)
        changed['verdict'] = 'BLOCK'
        self.assertFalse(verify_receipt(changed, r['decision_sha256']))

    def test_resealed_tampering_rejected_by_anchor(self):
        r = self.run_case().receipt
        changed = copy.deepcopy(r)
        changed['verdict'] = 'BLOCK'
        changed['decision_sha256'] = digest({k:v for k,v in changed.items() if k != 'decision_sha256'})
        self.assertFalse(verify_receipt(changed, r['decision_sha256']))

    def test_public_dto_drops_private_values_and_metadata(self):
        r = self.run_case(intent=replace(self.intent, metadata={'secret': 'sentinel-secret'})).receipt
        serialized = json.dumps(r)
        for private in ('121.85', 'sentinel-secret', 'free_usdt', 'auth_error', 'api_key'):
            self.assertNotIn(private, serialized)

    def test_live_provenance_and_envelope_privacy(self):
        self.assertEqual(self.run_case(mode='live').receipt['verdict'], 'BLOCK')
        contract = ExchangeContractSnapshot(
            'BNBUSDT', 'TRADING', ('MARKET',), True, D('5'), None,
            'binance-rest-fallback:exchange-info', NOW.isoformat())
        r = self.compiler.compile(
            self.intent, replace(self.market, source='binance-cli:spot'),
            replace(self.account, source='binance-cli:account', observed_at=NOW.isoformat()),
            exchange_contract=contract, mode='live', now=NOW).receipt
        self.assertEqual(r['verdict'], 'ALLOW')
        self.assertIsNone(r['safe_envelope'])
        self.assertNotIn('24.37', json.dumps(r))

    def test_human_receipt(self):
        text = human_receipt(self.run_case().receipt)
        self.assertIn('KACHING!', text)
        self.assertIn('POLICY SHA-256', text)
        self.assertNotIn('121.85', text)

    def test_extreme_market_blocks(self):
        self.assertEqual(self.run_case(market=replace(self.market, price_change_pct_24h=D('50'))).receipt['verdict'], 'BLOCK')

    def test_elevated_market_requires_review_without_authority(self):
        r = self.run_case(market=replace(self.market, price_change_pct_24h=D('12'))).receipt
        self.assertEqual((r['verdict'], r['authorized']), ('REVIEW', '0'))

    def test_live_stale_account_blocks(self):
        r = self.run_case(mode='live', market=replace(self.market, source='binance-cli:spot'),
            account=replace(self.account, source='binance-cli:account', observed_at=(NOW-timedelta(seconds=61)).isoformat()))
        self.assertIn('ACCOUNT_DATA_STALE', r.receipt['reasons'])

    def test_disabled_account_trading_blocks(self):
        r = self.run_case(account=replace(self.account, trading_enabled=False))
        self.assertIn('ACCOUNT_TRADING_UNAVAILABLE', r.receipt['reasons'])

    def test_exchange_contract_rejection_is_determining_rule(self):
        contract = ExchangeContractSnapshot(
            'BNBUSDT', 'BREAK', ('MARKET',), True, D('5'), None,
            'fixture', NOW.isoformat())
        result = self.compiler.compile(self.intent, self.market, self.account,
                                       exchange_contract=contract, mode='fixture', now=NOW)
        self.assertEqual(result.receipt['verdict'], 'BLOCK')
        self.assertIn('EXCHANGE_SYMBOL_NOT_TRADING', result.receipt['reasons'])
        self.assertIn('KCH-EXCHANGE-001', result.receipt['determining_rules'])

    def test_valid_exchange_contract_keeps_allow_and_rule_identity(self):
        contract = ExchangeContractSnapshot(
            'BNBUSDT', 'TRADING', ('LIMIT', 'MARKET'), True, D('5'), None,
            'fixture', NOW.isoformat())
        result = self.compiler.compile(self.intent, self.market, self.account,
                                       exchange_contract=contract, mode='fixture', now=NOW)
        self.assertEqual(result.receipt['verdict'], 'ALLOW')
        self.assertIn('KCH-EXCHANGE-001', result.receipt['evaluated_rules'])
