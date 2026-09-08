import copy
import os
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from decimal import Decimal as D
from pathlib import Path

from tradegate.authorization import AuthorizationIssuer, AuthorizationVerifier, ReplayCache, intent_sha256
from tradegate.compiler import Compiler, FinancialIntent
from tradegate.models import AccountSnapshot, MarketSnapshot

NOW = datetime(2026, 9, 8, 12, tzinfo=timezone.utc)


class AuthorizationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.key_path = Path(self.tmp.name) / 'issuer.pem'
        self.issuer = AuthorizationIssuer(self.key_path)
        self.verifier = AuthorizationVerifier(self.issuer.public_key_bytes, ReplayCache())
        self.intent = FinancialIntent('agent', 'BUY', 'BNBUSDT', D('10'))
        market = MarketSnapshot('BNBUSDT', D('750'), D('750.1'), D('750.05'), D('2.5'),
                                D('50000'), D('50000'), 'fixture', NOW.isoformat())
        account = AccountSnapshot(D('121.85'), 'fixture', True)
        self.receipt = Compiler().compile(self.intent, market, account, mode='fixture', now=NOW).receipt

    def tearDown(self):
        self.tmp.cleanup()

    def issue(self, **kwargs):
        return self.issuer.issue(self.receipt, self.intent, audience='binance.spot.newOrder', now=NOW, **kwargs)
    def test_intent_hash_binds_exact_financial_action(self):
        base = intent_sha256(self.intent, 'binance.spot.newOrder')
        variants = [
            FinancialIntent('agent', 'BUY', 'BNBUSDT', D('10.01')),
            FinancialIntent('agent', 'BUY', 'ETHUSDT', D('10')),
            FinancialIntent('human', 'BUY', 'BNBUSDT', D('10')),
        ]
        for variant in variants:
            self.assertNotEqual(base, intent_sha256(variant, 'binance.spot.newOrder'))
        self.assertNotEqual(base, intent_sha256(self.intent, 'other.tool'))

    def test_only_allow_can_issue_lease(self):
        for verdict in ('BLOCK', 'REVIEW'):
            with self.subTest(verdict=verdict):
                receipt = dict(self.receipt, verdict=verdict, authorized='0')
                with self.assertRaises(ValueError):
                    self.issuer.issue(receipt, self.intent, audience='binance.spot.newOrder', now=NOW)

    def test_allow_lease_verifies_with_trusted_public_key(self):
        lease = self.issue()
        result = self.verifier.verify(
            lease, self.intent, audience='binance.spot.newOrder',
            current_policy_sha256=self.receipt['policy_sha256'], now=NOW + timedelta(seconds=1))
        self.assertTrue(result.valid)
        self.assertEqual(result.reason, 'VALID')
        self.assertEqual(lease['schema'], 'kaching.authorization.v1')
        self.assertNotIn('private', str(lease).lower())

    def test_modified_signed_payload_is_rejected(self):
        lease = self.issue()
        changed = copy.deepcopy(lease)
        changed['maximum_authorized'] = '999'
        result = self.verifier.verify(changed, self.intent, audience='binance.spot.newOrder',
                                      current_policy_sha256=self.receipt['policy_sha256'], now=NOW)
        self.assertFalse(result.valid)
        self.assertEqual(result.reason, 'SIGNATURE_INVALID')
    def test_expiry_policy_drift_and_action_mismatch_reject(self):
        lease = self.issue(ttl_seconds=30)
        expired = self.verifier.verify(
            lease, self.intent, audience='binance.spot.newOrder',
            current_policy_sha256=self.receipt['policy_sha256'], now=NOW + timedelta(seconds=31))
        drift = self.verifier.verify(
            lease, self.intent, audience='binance.spot.newOrder',
            current_policy_sha256='0' * 64, now=NOW + timedelta(seconds=1))
        wrong_audience = self.verifier.verify(
            lease, self.intent, audience='other.tool',
            current_policy_sha256=self.receipt['policy_sha256'], now=NOW + timedelta(seconds=1))
        wrong_amount = self.verifier.verify(
            lease, FinancialIntent('agent', 'BUY', 'BNBUSDT', D('10.01')),
            audience='binance.spot.newOrder', current_policy_sha256=self.receipt['policy_sha256'],
            now=NOW + timedelta(seconds=1))
        self.assertEqual(expired.reason, 'AUTHORIZATION_EXPIRED')
        self.assertEqual(drift.reason, 'POLICY_DRIFT')
        self.assertEqual(wrong_audience.reason, 'AUDIENCE_MISMATCH')
        self.assertEqual(wrong_amount.reason, 'ACTION_MISMATCH')

    def test_wrong_issuer_and_replay_are_rejected(self):
        lease = self.issue()
        other = AuthorizationIssuer(Path(self.tmp.name) / 'other.pem')
        wrong = AuthorizationVerifier(other.public_key_bytes, ReplayCache()).verify(
            lease, self.intent, audience='binance.spot.newOrder',
            current_policy_sha256=self.receipt['policy_sha256'], now=NOW)
        self.assertEqual(wrong.reason, 'WRONG_ISSUER')
        first = self.verifier.verify(
            lease, self.intent, audience='binance.spot.newOrder',
            current_policy_sha256=self.receipt['policy_sha256'], now=NOW, consume=True)
        second = self.verifier.verify(
            lease, self.intent, audience='binance.spot.newOrder',
            current_policy_sha256=self.receipt['policy_sha256'], now=NOW, consume=True)
        self.assertTrue(first.valid)
        self.assertEqual(second.reason, 'REPLAY_DETECTED')

    def test_private_key_file_is_0600_and_not_serialized(self):
        lease = self.issue()
        self.assertEqual(os.stat(self.key_path).st_mode & 0o777, 0o600)
        text = str(lease)
        self.assertNotIn('BEGIN PRIVATE KEY', text)
        self.assertIn('issuer_key_fingerprint', lease)
        self.assertNotIn('issuer_private_key', lease)


if __name__ == '__main__':
    unittest.main()
