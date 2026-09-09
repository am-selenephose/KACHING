import test from 'node:test';
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';

test('one-command judge verification covers product and presentation gates without live mode', async () => {
  const script = await readFile(new URL('../../scripts/judge_verify.sh', import.meta.url), 'utf8');
  for (const command of [
    'python -m unittest discover -s tests -v',
    'python demo_attack_suite.py',
    'npm test --prefix ui',
    'npm run build --prefix ui',
    'npm test --prefix judge',
    'npm run build --prefix judge',
    'python scripts/release_safety_audit.py',
    'git diff --check',
  ]) assert.ok(script.includes(command), `missing ${command}`);
  assert.doesNotMatch(script, /--live/);
});
