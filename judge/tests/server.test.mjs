import test from 'node:test';
import assert from 'node:assert/strict';
import {mkdtemp, writeFile, mkdir} from 'node:fs/promises';
import {tmpdir} from 'node:os';
import {join} from 'node:path';

import {createStaticServer} from '../server.mjs';

test('static judge server serves app evidence and health without exposing arbitrary files', async () => {
  const root = await mkdtemp(join(tmpdir(), 'kaching-static-'));
  await mkdir(join(root, 'assets'));
  await writeFile(join(root, 'index.html'), '<h1>KACHING!</h1>');
  await writeFile(join(root, 'evidence.json'), '{"mode":"fixture"}');
  await writeFile(join(root, 'assets', 'app.js'), 'console.log("ok")');

  const server = createStaticServer(root);
  await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
  const {port} = server.address();
  try {
    assert.equal((await fetch(`http://127.0.0.1:${port}/health`)).status, 200);
    assert.match(await (await fetch(`http://127.0.0.1:${port}/`)).text(), /KACHING/);
    assert.equal((await fetch(`http://127.0.0.1:${port}/evidence.json`)).status, 200);
    assert.equal((await fetch(`http://127.0.0.1:${port}/../package.json`)).status, 404);
  } finally {
    await new Promise(resolve => server.close(resolve));
  }
});
