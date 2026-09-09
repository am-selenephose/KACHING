import test from 'node:test';
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';

const source = await readFile(new URL('../src/main.tsx', import.meta.url), 'utf8');
const evidence = JSON.parse(await readFile(new URL('../public/evidence.json', import.meta.url), 'utf8'));

test('judge surface states the evidence boundary and KACHING thesis', () => {
  assert.match(source, /Before an AI can touch money/);
  assert.match(source, /Capability is not authorization/);
  assert.match(source, /RECORDED DETERMINISTIC FIXTURES/);
  assert.match(source, /NO WALLET/);
  assert.match(source, /NO MONEY MOVED/);
});

test('judge surface exposes source demo verification and all proof outcomes', () => {
  for (const text of ['Source', '98s demo', 'Verification', 'BLOCK', 'REVIEW', 'ALLOW']) {
    assert.ok(source.includes(text), `missing ${text}`);
  }
  assert.equal(evidence.policy_arena.passed, 5);
  assert.equal(evidence.enforcement_arena.passed, 7);
  assert.equal(evidence.enforcement_arena.bypasses.length, 7);
});
