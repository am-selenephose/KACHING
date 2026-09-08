import contextlib
import copy
import importlib.util
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from decimal import Decimal

from tradegate import cli
from tradegate.models import AccountSnapshot
import test_compiler

HAS_SERVICE = importlib.util.find_spec('tradegate.service') is not None
if HAS_SERVICE:
    from tradegate.service import Service, arena


class ServiceTests(unittest.TestCase):
    def setUp(self):
        self.assertTrue(HAS_SERVICE, 'KACHING service is not implemented')
        self.service = Service()

    def test_default_is_fixture_block(self):
        state = self.service.compile({'scenario': 'block', 'quote': '10', 'mode': 'fixture'})
        self.assertEqual(state['receipt']['verdict'], 'BLOCK')
        self.assertTrue(state['verified'])
        self.assertFalse(state['live_enabled'])

    def test_live_requires_server_opt_in(self):
        with self.assertRaises(ValueError):
            self.service.compile({'mode': 'live', 'quote': '10'})

    def test_no_browser_policy_injection(self):
        with self.assertRaises(ValueError):
            self.service.compile({'mode': 'fixture', 'policy': {'max_quote_notional': '9999'}})

    def test_verify_uses_server_anchor(self):
        state = self.service.compile({'scenario': 'block'})
        receipt = state['receipt']
        receipt['verdict'] = 'ALLOW'
        self.assertFalse(self.service.verify(receipt))
        self.assertEqual(self.service.state()['receipt']['verdict'], 'BLOCK')

    def test_unknown_receipt_rejected(self):
        receipt = self.service.compile({})['receipt']
        receipt['proposal_id'] = 'unknown'
        self.assertFalse(self.service.verify(receipt))

    def test_returned_ledger_cannot_mutate_retained_events(self):
        state = self.service.compile({})
        state['ledger'][0]['verdict'] = 'ALLOW'
        self.assertEqual(self.service.state()['ledger'][0]['verdict'], 'BLOCK')

    def test_arena_really_contains_five(self):
        result = arena()
        self.assertEqual(result['passed'], 5)
        self.assertEqual(len(result['attacks']), 5)
        self.assertTrue(all(a['contained'] for a in result['attacks']))

    def test_ledger_and_anchors_bounded(self):
        for _ in range(110):
            self.service.compile({})
        self.assertLessEqual(len(self.service.state()['ledger']), 70)
        self.assertLessEqual(len(self.service.anchors), 100)

    def test_nondecimal_quote_rejected(self):
        for q in ('NaN', '1e999999', True, {'value': '10'}):
            with self.subTest(q=q), self.assertRaises(ValueError):
                self.service.compile({'quote': q})

    def test_http_origin_guard(self):
        self.assertTrue(self.service.valid_request('127.0.0.1:8890', 'http://127.0.0.1:8890', 8890))
        self.assertFalse(self.service.valid_request('evil.test:8890', 'http://evil.test:8890', 8890))
        self.assertFalse(self.service.valid_request('127.0.0.1:8890', 'https://evil.test', 8890))


class CLIBoundaryTests(unittest.TestCase):
    def test_review_refuses_order_test(self):
        case = test_compiler.CompilerTests()
        case.setUp()
        market = case.market
        account = AccountSnapshot(Decimal('121.85'), 'binance-cli:account')
        from dataclasses import replace
        from datetime import datetime, timezone
        market = replace(market, source='binance-cli:spot', observed_at=datetime.now(timezone.utc).isoformat())
        with tempfile.TemporaryDirectory() as tmp, patch('sys.argv', ['tradegate', '--quote', '30', '--order-test', '--evidence-out', str(Path(tmp)/'proof.json')]), patch.object(cli.BinanceCLI, 'market_snapshot', return_value=market), patch.object(cli.BinanceCLI, 'account_snapshot', return_value=account), patch.object(cli.BinanceCLI, 'test_market_order') as order_test, contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit):
                cli.main()
            order_test.assert_not_called()
