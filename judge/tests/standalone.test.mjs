import test from 'node:test';
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';

test('standalone judge artifact is self-contained and honest', async () => {
  const html = await readFile(new URL('../standalone.html', import.meta.url), 'utf8');
  assert.match(html, /Before an AI can touch money/);
  assert.match(html, /Capability is not authorization/);
  assert.match(html, /RECORDED DETERMINISTIC FIXTURES/);
  assert.match(html, /NO WALLET/);
  assert.match(html, /NO MONEY MOVED/);
  assert.match(html, /ACTION_MISMATCH/);
  assert.match(html, /REPLAY_DETECTED/);
  assert.doesNotMatch(html, /fetch\s*\(/);
  assert.doesNotMatch(html, /<script[^>]+src=/);
  assert.doesNotMatch(html, /<link[^>]+stylesheet/);
});
