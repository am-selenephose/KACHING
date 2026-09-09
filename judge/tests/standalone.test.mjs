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
  assert.match(html, /x\.com\/Selenephose\/status\/2097472059890905444/);
  assert.match(html, /052af0841e17596958953f038c7b782ad4defe74/);
  assert.doesNotMatch(html, /2097465082141905231/);
  assert.match(html, /gitlab\.com\/am\.statementforge\/kaching/);
  assert.match(html, /github\.com\/am-selenephos\/KACHING/);
  assert.doesNotMatch(html, /fetch\s*\(/);
  assert.doesNotMatch(html, /<script[^>]+src=/);
  assert.doesNotMatch(html, /<link[^>]+stylesheet/);
});
