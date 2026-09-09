import test from 'node:test';
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';

const readme = await readFile(new URL('../../README.md', import.meta.url), 'utf8');

const CORRECT_X = 'https://x.com/Selenephose/status/2097472059890905444';
const OLD_X_ID = '2097465082141905231';
const SUBMISSION_SHA = '052af0841e17596958953f038c7b782ad4defe74';

test('README points judges to the real submitted 98-second X video', () => {
  assert.ok(readme.includes(CORRECT_X));
  assert.ok(!readme.includes(OLD_X_ID));
  assert.match(readme, /KACHING-98s-thumbnail\.png/);
});

test('README preserves the pre-deadline submission snapshot boundary', () => {
  assert.ok(readme.includes(SUBMISSION_SHA));
  assert.match(readme, /submitted before the deadline/i);
  assert.match(readme, /judge-access|presentation/i);
});
