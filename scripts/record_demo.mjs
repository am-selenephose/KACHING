// Record the canonical KACHING! hackathon demo from the real local browser UI.
//
// The script starts an isolated fixture-only server with an ephemeral Ed25519
// issuer key, drives the production UI with Playwright, then converts the
// browser recording into an exact 98-second H.264 MP4. It never enables live
// observations and never calls a financial execution endpoint.

import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {spawn} from 'node:child_process';
import {once} from 'node:events';
import {access, copyFile, mkdir, mkdtemp, readFile, rm} from 'node:fs/promises';
import {tmpdir} from 'node:os';
import {dirname, join, resolve} from 'node:path';
import {fileURLToPath} from 'node:url';

const {chromium} = await import(process.env.KACHING_PLAYWRIGHT_MODULE || 'playwright');
const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const demoDir = join(root, 'docs', 'demo');
const outputPath = join(demoDir, 'KACHING-98s.mp4');
const thumbnailPath = join(demoDir, 'KACHING-98s-thumbnail.png');
const port = Number(process.env.KACHING_DEMO_PORT || '8891');
const url = `http://127.0.0.1:${port}`;
const targetDuration = 98;

if (!Number.isInteger(port) || port < 1024 || port > 65535) {
  throw new Error(`Invalid KACHING_DEMO_PORT: ${process.env.KACHING_DEMO_PORT}`);
}

await access(join(root, 'ui', 'dist', 'index.html'));
await mkdir(demoDir, {recursive: true});

function run(command, args, options = {}) {
  return new Promise((resolveRun, rejectRun) => {
    const child = spawn(command, args, {cwd: root, stdio: ['ignore', 'pipe', 'pipe'], ...options});
    let stdout = '';
    let stderr = '';
    child.stdout?.on('data', chunk => { stdout += chunk; });
    child.stderr?.on('data', chunk => { stderr += chunk; });
    child.on('error', rejectRun);
    child.on('close', code => {
      if (code === 0) resolveRun({stdout: stdout.trim(), stderr: stderr.trim()});
      else rejectRun(new Error(`${command} exited ${code}\n${stderr || stdout}`));
    });
  });
}

async function waitForServer(address, server, timeoutMs = 15000) {
  const deadline = Date.now() + timeoutMs;
  while (Date.now() < deadline) {
    if (server.exitCode !== null) throw new Error(`Fixture server exited ${server.exitCode}`);
    try {
      const response = await fetch(address);
      if (response.ok) return;
    } catch {
      // Expected while the loopback-only server is starting.
    }
    await new Promise(resolveWait => setTimeout(resolveWait, 100));
  }
  throw new Error(`Fixture server did not start at ${address}`);
}

async function uiSourceSha() {
  const result = await run('git', ['log', '-1', '--format=%H', '--', 'ui']);
  return result.stdout;
}

async function sha256(path) {
  return createHash('sha256').update(await readFile(path)).digest('hex');
}

async function probe(path) {
  const result = await run('ffprobe', [
    '-v', 'error',
    '-select_streams', 'v:0',
    '-show_entries', 'stream=codec_name,width,height,pix_fmt,r_frame_rate:format=duration',
    '-of', 'json',
    path,
  ]);
  return JSON.parse(result.stdout);
}

async function injectPresentationLayer(page, sourceSha) {
  await page.addStyleTag({content: `
    #kaching-demo-caption {
      position: fixed; z-index: 2147483645; left: 50%; bottom: 24px;
      width: min(1320px, calc(100vw - 144px)); min-height: 76px;
      transform: translate(-50%, 18px); opacity: 0;
      display: grid; grid-template-columns: 230px 1fr auto; align-items: center;
      gap: 26px; padding: 15px 22px 14px;
      color: #ead7a4; background: linear-gradient(110deg, #001a1a 0%, #000909 58%, #001e1e 100%);
      border: 1px solid rgba(117, 234, 255, .34);
      box-shadow: 0 22px 58px rgba(0, 0, 0, .58), inset 0 1px rgba(234, 215, 164, .08);
      transition: opacity 260ms ease, transform 360ms cubic-bezier(.2,.8,.2,1);
      pointer-events: none; font-family: Newsreader, Georgia, serif;
    }
    #kaching-demo-caption::before {
      content: ''; position: absolute; left: 0; right: 0; top: -1px; height: 2px;
      background: linear-gradient(90deg, #67ffd2, #75eaff 24%, #aa85ef 49%, #e696d3 70%, #e6d09b 89%, #67ffd2);
      opacity: .82;
    }
    #kaching-demo-caption.demo-visible { opacity: 1; transform: translate(-50%, 0); }
    #kaching-demo-caption .demo-kicker {
      color: #75eaff; font: 600 17px/1.2 "IBM Plex Mono", monospace;
      letter-spacing: .08em; text-transform: uppercase;
    }
    #kaching-demo-caption .demo-line {
      color: #f0dfb1; font: 500 30px/1.18 Newsreader, Georgia, serif;
      letter-spacing: -.012em;
    }
    #kaching-demo-caption .demo-source {
      color: #b8ccbd; font: 500 17px/1.2 "IBM Plex Mono", monospace;
      letter-spacing: .045em; text-align: right; white-space: nowrap;
    }
    #kaching-demo-cursor {
      position: fixed; z-index: 2147483647; left: 80px; top: 80px;
      width: 28px; height: 34px; opacity: 0; pointer-events: none;
      transform: translate(-3px, -3px);
      filter: drop-shadow(0 3px 6px rgba(0,0,0,.75));
      transition: left 410ms cubic-bezier(.2,.8,.2,1), top 410ms cubic-bezier(.2,.8,.2,1), opacity 180ms ease;
    }
    #kaching-demo-cursor.demo-visible { opacity: 1; }
    .kaching-demo-ripple {
      position: fixed; z-index: 2147483646; width: 42px; height: 42px;
      margin: -21px 0 0 -21px; border: 2px solid #75eaff; border-radius: 50%;
      opacity: .8; transform: scale(.35); pointer-events: none;
      transition: transform 420ms cubic-bezier(.2,.8,.2,1), opacity 420ms ease;
    }
    .kaching-demo-ripple.demo-go { opacity: 0; transform: scale(1.35); }
    #kaching-demo-end {
      position: fixed; z-index: 2147483644; inset: 0; opacity: 0; pointer-events: none;
      display: grid; place-items: center; overflow: hidden;
      background:
        radial-gradient(ellipse at 50% 44%, rgba(19, 101, 82, .42), transparent 54%),
        linear-gradient(122deg, #000404, #000909 46%, #001e1e);
      transition: opacity 520ms ease;
      color: #ead7a4; font-family: Newsreader, Georgia, serif;
    }
    #kaching-demo-end.demo-visible { opacity: 1; pointer-events: auto; }
    #kaching-demo-end::before {
      content: ''; position: absolute; inset: 52px;
      border: 1px solid transparent;
      border-image: linear-gradient(118deg, #67ffd2, #75eaff 19%, #aa85ef 43%, #e696d3 65%, #e6d09b 87%, #67ffd2) 1;
      opacity: .58;
    }
    #kaching-demo-end .demo-end-inner { width: min(1200px, calc(100vw - 260px)); text-align: center; }
    #kaching-demo-end .demo-end-wordmark {
      margin: 0; font-size: 142px; line-height: .95; letter-spacing: -.055em;
      background: linear-gradient(105deg, #a8782e, #f4dfa5 30%, #c5943f 58%, #f2ddb0 76%, #92661e);
      background-clip: text; -webkit-background-clip: text; color: transparent;
      text-shadow: 0 18px 48px rgba(0,0,0,.35);
    }
    #kaching-demo-end .demo-end-thesis { margin: 30px 0 44px; color: #c4d6ca; font-size: 36px; }
    #kaching-demo-end .demo-end-action {
      color: #75eaff; font: 600 19px/1.2 "IBM Plex Mono", monospace;
      letter-spacing: .12em; text-transform: uppercase;
    }
    #kaching-demo-end .demo-end-url { margin-top: 13px; color: #f0dfb1; font-size: 38px; }
    #kaching-demo-end .demo-end-proof {
      margin-top: 38px; color: #98b5a5; font: 500 18px/1.5 "IBM Plex Mono", monospace;
    }
  `});

  await page.evaluate(({sourceSha}) => {
    const caption = document.createElement('div');
    caption.id = 'kaching-demo-caption';
    caption.innerHTML = '<div class="demo-kicker"></div><div class="demo-line"></div><div class="demo-source">OFFLINE FIXTURE · NO EXECUTION</div>';
    document.body.append(caption);

    const cursor = document.createElement('div');
    cursor.id = 'kaching-demo-cursor';
    cursor.innerHTML = '<svg width="28" height="34" viewBox="0 0 28 34" aria-hidden="true"><path d="M3 2 24 21l-10 1 5 9-5 2-5-10-6 7Z" fill="#ecd08a" stroke="#000909" stroke-width="2" stroke-linejoin="round"/></svg>';
    document.body.append(cursor);

    const end = document.createElement('div');
    end.id = 'kaching-demo-end';
    end.innerHTML = `<div class="demo-end-inner">
      <h2 class="demo-end-wordmark">KACHING!</h2>
      <p class="demo-end-thesis">LLMs propose. KACHING! authorizes.</p>
      <div class="demo-end-action">Review the evidence →</div>
      <div class="demo-end-url">github.com/am-selenephos/KACHING</div>
      <div class="demo-end-proof">OFFLINE FIXTURE · NO FINANCIAL EXECUTION<br>SOURCE UI ${sourceSha.slice(0, 7)}</div>
    </div>`;
    document.body.append(end);

    window.__kachingDemo = {
      caption(kicker, line) {
        caption.querySelector('.demo-kicker').textContent = kicker;
        caption.querySelector('.demo-line').textContent = line;
        caption.classList.add('demo-visible');
      },
      hideCaption() { caption.classList.remove('demo-visible'); },
      move(x, y) {
        cursor.style.left = `${x}px`;
        cursor.style.top = `${y}px`;
        cursor.classList.add('demo-visible');
      },
      pulse(x, y) {
        const ripple = document.createElement('div');
        ripple.className = 'kaching-demo-ripple';
        ripple.style.left = `${x}px`;
        ripple.style.top = `${y}px`;
        document.body.append(ripple);
        requestAnimationFrame(() => ripple.classList.add('demo-go'));
        setTimeout(() => ripple.remove(), 500);
      },
      hideCursor() { cursor.classList.remove('demo-visible'); },
      showEnd() {
        caption.classList.remove('demo-visible');
        cursor.classList.remove('demo-visible');
        end.classList.add('demo-visible');
      },
    };
  }, {sourceSha});
}

const temp = await mkdtemp(join(tmpdir(), 'kaching-demo-'));
const keyPath = join(temp, 'issuer-ed25519.pem');
const recordingDir = join(temp, 'playwright-video');
await mkdir(recordingDir);

const serverCode = [
  'from pathlib import Path',
  'from tradegate.web import create_server',
  `server = create_server(${port}, False, Path(${JSON.stringify(keyPath)}))`,
  'print("KACHING_DEMO_SERVER_READY", flush=True)',
  'server.serve_forever()',
].join('; ');
const server = spawn(process.env.PYTHON || 'python', ['-u', '-c', serverCode], {
  cwd: root,
  stdio: ['ignore', 'pipe', 'pipe'],
});
let serverStderr = '';
server.stderr.on('data', chunk => { serverStderr += chunk; });

let browser;
let context;
let rawVideoPath;
const consoleProblems = [];
const networkFailures = [];

try {
  await waitForServer(url, server);
  const sourceSha = await uiSourceSha();
  assert.match(sourceSha, /^[0-9a-f]{40}$/);

  browser = await chromium.launch({
    executablePath: process.env.CHROMIUM_PATH || '/usr/bin/chromium',
    headless: true,
    args: ['--disable-gpu', '--disable-dev-shm-usage'],
  });

  // Warm the exact production bundle before the recorded page is created.
  const warmContext = await browser.newContext({viewport: {width: 1920, height: 1080}});
  const warmPage = await warmContext.newPage();
  const warmResponse = await warmPage.goto(url, {waitUntil: 'networkidle'});
  assert.equal(warmResponse?.status(), 200);
  await warmPage.getByText('Local kernel connected', {exact: true}).waitFor();
  await warmPage.evaluate(() => document.fonts.ready);
  await warmContext.close();

  context = await browser.newContext({
    viewport: {width: 1920, height: 1080},
    deviceScaleFactor: 1,
    colorScheme: 'dark',
    reducedMotion: 'no-preference',
    recordVideo: {dir: recordingDir, size: {width: 1920, height: 1080}},
  });
  const page = await context.newPage();
  page.on('console', message => {
    if (['warning', 'error'].includes(message.type())) consoleProblems.push(`${message.type()}: ${message.text()}`);
  });
  page.on('pageerror', error => consoleProblems.push(`pageerror: ${error.message}`));
  page.on('requestfailed', request => networkFailures.push(`${request.url()} — ${request.failure()?.errorText || 'failed'}`));

  const response = await page.goto(url, {waitUntil: 'networkidle'});
  assert.equal(response?.status(), 200);
  await page.getByText('Local kernel connected', {exact: true}).waitFor();
  await page.evaluate(() => document.fonts.ready);
  await injectPresentationLayer(page, sourceSha);

  const text = async locator => (await locator.innerText()).replace(/\s+/g, ' ').trim();
  const caption = (kicker, line) => page.evaluate(([a, b]) => window.__kachingDemo.caption(a, b), [kicker, line]);
  const hideCaption = () => page.evaluate(() => window.__kachingDemo.hideCaption());
  const start = performance.now();
  const holdUntil = async seconds => {
    const remaining = start + seconds * 1000 - performance.now();
    if (remaining > 0) await page.waitForTimeout(remaining);
  };
  const scrollToLocator = async (locator, top = 24) => {
    await locator.evaluate((element, topOffset) => {
      const box = element.getBoundingClientRect();
      window.scrollTo({top: window.scrollY + box.top - topOffset, behavior: 'smooth'});
    }, top);
    await page.waitForTimeout(650);
  };
  const point = async locator => {
    await locator.scrollIntoViewIfNeeded();
    const box = await locator.boundingBox();
    assert(box, 'Target is not visible for cursor choreography');
    const position = {x: box.x + box.width / 2, y: box.y + box.height / 2};
    await page.evaluate(({x, y}) => window.__kachingDemo.move(x, y), position);
    await page.waitForTimeout(440);
    return position;
  };
  const click = async locator => {
    const position = await point(locator);
    await page.evaluate(({x, y}) => window.__kachingDemo.pulse(x, y), position);
    await page.waitForTimeout(130);
    await locator.click();
    await page.waitForTimeout(260);
  };
  const choose = async (locator, value) => {
    const position = await point(locator);
    await page.evaluate(({x, y}) => window.__kachingDemo.pulse(x, y), position);
    await page.waitForTimeout(130);
    await locator.selectOption(value);
    await page.waitForTimeout(300);
  };

  // 00–08 — thesis / boundary.
  await caption('01 / BOUNDARY', 'Before money moves, authority must prove itself.');
  await page.evaluate(() => window.scrollTo({top: 0, behavior: 'smooth'}));
  await holdUntil(8);

  // 08–14 — untrusted intent.
  await caption('02 / UNTRUSTED INTENT', 'A proposal carries zero authority.');
  await scrollToLocator(page.locator('.deck'));
  assert.match(await text(page.locator('.raw-authority')), /Raw agent authority None\./i);
  await point(page.getByLabel('Requested notional / USDT'));
  await holdUntil(14);

  // 14–24 — compile BLOCK through the visible policy stages.
  await caption('03 / DETERMINISTIC POLICY', 'Seven stages compile intent into a verdict.');
  await click(page.getByRole('button', {name: 'Compile financial intent'}));
  await page.locator('.verdict-word').filter({hasText: 'BLOCK'}).waitFor();
  assert.equal(await page.locator('.authorization-lease').count(), 0);
  assert.match(await text(page.locator('.receipt-fields')), /Authorized 0\.00 USDT/);
  await holdUntil(24);

  // 24–34 — hold the fail-closed BLOCK evidence.
  await caption('04 / BLOCK', '0.00 USDT. No lease. No authority.');
  await scrollToLocator(page.locator('.deck'));
  await point(page.locator('.verdict-word'));
  await holdUntil(34);

  // 34–44 — REVIEW exposes an envelope but still issues zero authority.
  await caption('05 / REVIEW', '100 requested. 24.37 admissible. Zero authorized.');
  await choose(page.getByLabel('Scenario', {exact: true}), 'review');
  await click(page.getByRole('button', {name: 'Compile financial intent'}));
  await page.locator('.verdict-word').filter({hasText: 'REVIEW'}).waitFor();
  assert.equal(await page.locator('.authorization-lease').count(), 0);
  assert.match(await text(page.locator('.envelope')), /24\.37/);
  assert.match(await text(page.locator('.receipt-fields')), /Requested 100\.00 USDT Authorized 0\.00 USDT/);
  await scrollToLocator(page.locator('.deck'));
  await holdUntil(44);

  // 44–57 — ALLOW issues a real, short-lived Ed25519 lease.
  await caption('06 / SIGNED LEASE', 'Only ALLOW issues scoped Ed25519 authority.');
  await choose(page.getByLabel('Scenario', {exact: true}), 'allow');
  await click(page.getByRole('button', {name: 'Compile financial intent'}));
  await page.locator('.authorization-lease').waitFor();
  assert.match(await text(page.locator('.authorization-lease')), /Authorization lease/);
  assert.match(await text(page.locator('.authorization-lease')), /Ed25519 · signed/);
  await scrollToLocator(page.locator('.deck'));
  await holdUntil(51);
  await caption('06 / 30-SECOND LEASE', 'Action, ceiling, audience, policy, evidence.');
  await point(page.locator('.lease-clock'));
  await holdUntil(57);

  // 57–68 — exact signed action verifies at the local boundary.
  await caption('07 / ENFORCEMENT', 'Exact signed action verifies VALID.');
  await click(page.getByRole('button', {name: /Open enforcement lab/}).first());
  await page.locator('.enforcement-lab').waitFor();
  await scrollToLocator(page.locator('.enforcement-lab'));
  await click(page.getByRole('button', {name: /Verify at enforcement boundary/}));
  await page.locator('.enforcement-result.pass').waitFor();
  assert.match(await text(page.locator('.enforcement-result')), /VALID/);
  await holdUntil(63);
  await caption('07 / LOCAL VERIFIER', 'Verification grants no execution capability.');
  await point(page.locator('.enforcement-result'));
  await holdUntil(68);

  // 68–76 — original receipt PASS, modified copy FAIL.
  await caption('08 / RECEIPT INTEGRITY', 'Original passes. Modified copy fails.');
  await click(page.getByRole('button', {name: 'Command deck', exact: true}));
  await scrollToLocator(page.locator('.integrity'), 650);
  await click(page.getByRole('button', {name: /Verify receipt/}));
  await page.waitForFunction(() => document.querySelector('.integrity')?.textContent?.includes('PASS'));
  await holdUntil(72);
  await click(page.getByRole('button', {name: /Tamper copy/}));
  await page.waitForFunction(() => document.querySelector('.integrity')?.textContent?.includes('FAIL'));
  assert.match(await text(page.locator('.integrity')), /FAIL.*modified copy rejected.*Original retained/i);
  await holdUntil(76);

  // 76–87 — seven deterministic authorization bypasses are rejected.
  await caption('09 / AUTHORIZATION GAUNTLET', 'Seven bypasses attempted. Seven rejected.');
  await click(page.getByRole('button', {name: 'Enforcement lab', exact: true}));
  await scrollToLocator(page.locator('.enforcement-lab'));
  await click(page.getByRole('button', {name: /Run seven bypasses/}));
  await page.locator('.enforcement-gauntlet .arena-score').waitFor();
  assert.equal(await page.locator('.enforcement-gauntlet article .pass').count(), 7);
  assert.match(await text(page.locator('.enforcement-gauntlet')), /Baseline exact action: VALID/);
  await scrollToLocator(page.locator('.enforcement-gauntlet'));
  await holdUntil(81);
  await hideCaption();
  await page.evaluate(() => window.__kachingDemo.hideCursor());
  await holdUntil(87);

  // 87–93 — the separate policy-attack suite reports 5/5 contained.
  await caption('10 / POLICY ARENA', 'Five policy attacks. Five contained.');
  await click(page.getByRole('button', {name: 'Adversarial arena', exact: true}));
  await scrollToLocator(page.locator('.arena'));
  await click(page.getByRole('button', {name: /Run five attacks/}));
  await page.locator('.arena .arena-score').waitFor();
  assert.equal(await page.locator('.arena article .pass').count(), 5);
  await holdUntil(91);
  await hideCaption();
  await page.evaluate(() => window.__kachingDemo.hideCursor());
  await holdUntil(93);

  // 93–98 — one end action, repository evidence, explicit claim boundary.
  assert.match(await text(page.locator('.execution')), /No live execution path/i);
  const privateLabels = await page.evaluate(() => /free_usdt|api[_ ]?secret|api[_ ]?key|binance uid|private[_ ]?key|private balance/i.test(document.body.innerText));
  assert.equal(privateLabels, false, 'Private field labels must not appear in the recording');
  await page.evaluate(() => window.__kachingDemo.showEnd());
  await holdUntil(98.2);

  assert.deepEqual(consoleProblems, []);
  assert.deepEqual(networkFailures, []);
  rawVideoPath = await page.video().path();
  await context.close();
  context = undefined;
  await browser.close();
  browser = undefined;

  const rawProbe = await probe(rawVideoPath);
  const rawDuration = Number(rawProbe.format.duration);
  assert(Number.isFinite(rawDuration) && rawDuration > 90, `Unexpected raw duration: ${rawDuration}`);
  const trimStart = Math.max(0, rawDuration - targetDuration);

  await run('ffmpeg', [
    '-y', '-v', 'error',
    '-i', rawVideoPath,
    '-ss', trimStart.toFixed(6),
    '-vf', 'tpad=stop_mode=clone:stop_duration=3,format=yuv420p',
    '-t', String(targetDuration),
    '-r', '30', '-fps_mode', 'cfr',
    '-c:v', 'libx264', '-preset', 'medium', '-crf', '18',
    '-colorspace', 'bt709', '-color_primaries', 'bt709', '-color_trc', 'bt709',
    '-movflags', '+faststart', '-an',
    outputPath,
  ]);

  await run('ffmpeg', [
    '-y', '-v', 'error', '-ss', '4.5', '-i', outputPath,
    '-frames:v', '1', '-vf', 'scale=1280:720:flags=lanczos',
    thumbnailPath,
  ]);

  const finalProbe = await probe(outputPath);
  const stream = finalProbe.streams[0];
  const duration = Number(finalProbe.format.duration);
  assert.equal(stream.codec_name, 'h264');
  assert.equal(stream.width, 1920);
  assert.equal(stream.height, 1080);
  assert.equal(stream.pix_fmt, 'yuv420p');
  assert(Math.abs(duration - targetDuration) < 0.02, `Expected 98 seconds, got ${duration}`);

  console.log(JSON.stringify({
    status: 'PASS',
    source_ui_sha: sourceSha,
    server: 'fixture-only / ephemeral issuer key',
    output: outputPath,
    duration_seconds: duration,
    codec: stream.codec_name,
    resolution: `${stream.width}x${stream.height}`,
    pixel_format: stream.pix_fmt,
    frame_rate: stream.r_frame_rate,
    sha256: await sha256(outputPath),
    thumbnail: thumbnailPath,
    thumbnail_sha256: await sha256(thumbnailPath),
    raw_duration_seconds: rawDuration,
    trim_start_seconds: trimStart,
  }, null, 2));
} finally {
  if (context) await context.close().catch(() => {});
  if (browser) await browser.close().catch(() => {});
  if (server.exitCode === null) {
    server.kill('SIGTERM');
    await Promise.race([once(server, 'exit'), new Promise(resolveWait => setTimeout(resolveWait, 2000))]);
  }
  await rm(temp, {recursive: true, force: true});
  if (serverStderr.trim()) console.error(serverStderr.trim());
}
