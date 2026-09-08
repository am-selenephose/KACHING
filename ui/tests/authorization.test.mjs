import assert from 'node:assert/strict';
import test from 'node:test';

import {buildEnforcementRequest, leaseCountdown} from '../src/authorization.mjs';

const lease = Object.freeze({
  schema: 'kaching.authorization.v1', decision_id: 'abc', origin: 'agent',
  action: 'BUY', resource: 'BNBUSDT', audience: 'binance.spot.newOrder',
  requested: '10', maximum_authorized: '10', intent_sha256: 'a'.repeat(64),
  policy_version: 'kaching-v1', policy_sha256: 'b'.repeat(64),
  observation_commitment: 'c'.repeat(64), issued_at: '2026-09-08T12:00:00+00:00',
  expires_at: '2026-09-08T12:00:30+00:00', nonce: 'd'.repeat(32),
  issuer_key_fingerprint: 'e'.repeat(64), signature_algorithm: 'Ed25519',
  signature: 'signed-value',
});

test('lease countdown is bounded and deterministic', () => {
  assert.equal(leaseCountdown(lease, Date.parse('2026-09-08T12:00:01Z')), '29s');
  assert.equal(leaseCountdown(lease, Date.parse('2026-09-08T12:00:31Z')), 'expired');
});

test('enforcement request mutations never modify canonical lease', () => {
  const original = JSON.stringify(lease);
  const exact = buildEnforcementRequest(lease, 'exact');
  const amount = buildEnforcementRequest(lease, 'amount');
  const resource = buildEnforcementRequest(lease, 'resource');
  const audience = buildEnforcementRequest(lease, 'audience');
  const signature = buildEnforcementRequest(lease, 'signature');
  assert.equal(exact.quote, '10');
  assert.equal(amount.quote, '10.01');
  assert.equal(resource.symbol, 'BTCUSDT');
  assert.equal(audience.audience, 'other.tool');
  assert.notEqual(signature.lease.signature, lease.signature);
  assert.equal(JSON.stringify(lease), original);
  assert.equal(exact.lease, lease);
});
