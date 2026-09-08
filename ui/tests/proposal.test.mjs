import test from 'node:test';
import assert from 'node:assert/strict';
import {formatAmount, admissibleDraft} from '../src/proposal.mjs';

test('formatting preserves exact decimal digits without floating point', () => {
  assert.equal(formatAmount('123456789012.123456789012345678'), '123,456,789,012.123456789012345678');
});
test('formatting distinguishes missing amounts from zero', () => {
  assert.equal(formatAmount(null), '—');
  assert.equal(formatAmount('0'), '0.00');
  assert.equal(formatAmount('24.37'), '24.37');
});
test('review remediation produces only a draft amount', () => {
  const receipt = {mode:'fixture', verdict:'REVIEW', safe_envelope:'24.37', reasons:['REQUEST_EXCEEDS_SAFE_ENVELOPE']};
  assert.equal(admissibleDraft(receipt), '24.37');
  assert.equal(receipt.verdict, 'REVIEW');
});
test('live private envelope is never offered as a public draft', () => {
  assert.equal(admissibleDraft({mode:'live', verdict:'REVIEW', safe_envelope:'24.37', reasons:['REQUEST_EXCEEDS_SAFE_ENVELOPE']}), null);
});
test('blocked or absent evidence cannot generate a remediation draft', () => {
  assert.equal(admissibleDraft(null), null);
  assert.equal(admissibleDraft({mode:'fixture', verdict:'BLOCK', safe_envelope:'0', reasons:['NO_SAFE_NOTIONAL']}), null);
});
test('market review alone does not suggest reducing amount', () => {
  assert.equal(admissibleDraft({mode:'fixture', verdict:'REVIEW', safe_envelope:'24.37', reasons:['SPREAD_ELEVATED']}), null);
});
