// Optional local release harness. Install Playwright separately or set
// KACHING_PLAYWRIGHT_MODULE to its module entry; system Chromium is used.
import assert from 'node:assert/strict';
import {mkdir, writeFile} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {readFile} from 'node:fs/promises';
import {resolve} from 'node:path';
import {pathToFileURL} from 'node:url';
const {chromium} = await import(process.env.KACHING_PLAYWRIGHT_MODULE || 'playwright');
const root = new URL('../', import.meta.url);
const output = process.env.KACHING_QA_OUTPUT
  ? pathToFileURL(`${resolve(process.env.KACHING_QA_OUTPUT)}/`)
  : new URL('docs/screenshots/', root);
const record = process.env.KACHING_QA_RECORD
  ? pathToFileURL(resolve(process.env.KACHING_QA_RECORD))
  : new URL('docs/browser-qa.json',root);
await mkdir(output, {recursive:true});
const browser = await chromium.launch({
  executablePath:process.env.CHROMIUM_PATH || '/usr/bin/chromium',
  headless:true,
  args:['--disable-gpu','--disable-dev-shm-usage'],
});
const context = await browser.newContext({viewport:{width:1920,height:1080},deviceScaleFactor:1});
const page = await context.newPage();
const screenshotNames = ['01-command-deck.png','02-block.png','03-review-safe-envelope.png','04-authorization-lease.png','05-enforcement-valid.png','06-seven-bypasses.png','07-receipt-tamper.png'];
const findings = {timestamp:new Date().toISOString(),browser:browser.version(),sourceHashes:{},artifactHashes:{},checks:[],viewports:[],console:[],networkFailures:[]};
for (const file of ['ui/src/main.tsx','ui/src/emerald.css','ui/src/style.css','ui/index.html']) findings.sourceHashes[file]=createHash('sha256').update(await readFile(new URL(file,root))).digest('hex');
page.on('console', msg=>{if(['warning','error'].includes(msg.type())) findings.console.push({type:msg.type(),text:msg.text()});});
page.on('pageerror', error=>findings.console.push({type:'pageerror',text:error.message}));
page.on('requestfailed', request=>findings.networkFailures.push({url:request.url(),error:request.failure()?.errorText}));
const check = (name, details) => {findings.checks.push({name,status:'PASS',details}); console.log('PASS',name,JSON.stringify(details ?? ''));};
const shot = async name => {
  const selector=name==='01-command-deck.png'?null:name.includes('enforcement')||name.includes('seven-bypasses')?'.enforcement-lab':'.deck';
  if(selector) await page.locator(selector).evaluate(el=>scrollTo(0,el.getBoundingClientRect().top+scrollY-24));
  await page.evaluate(()=>new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve))));
  await page.waitForTimeout(140);
  await page.screenshot({path:new URL(name,output).pathname});
};
const compile = async scenario => {
  await page.getByRole('button',{name:'Command deck',exact:true}).click();
  await page.getByLabel('Scenario',{exact:true}).selectOption(scenario);
  await page.getByRole('button',{name:'Compile financial intent'}).click();
  await page.locator('.verdict-word').filter({hasText:scenario.toUpperCase()}).waitFor();
};
try {
  const response=await page.goto(process.env.KACHING_QA_URL || 'http://127.0.0.1:8890');
  assert.equal(response.status(),200);
  await page.getByText('Local kernel connected',{exact:true}).waitFor();
  await page.evaluate(()=>document.fonts.ready);
  check('HTTP 200 and KACHING renders',await page.title());
  const fonts=await page.evaluate(async()=>{const families=['Gloock','Newsreader','IBM Plex Mono'];await Promise.all(families.map(f=>document.fonts.load(`16px "${f}"`)));return families.map(f=>({family:f,loaded:document.fonts.check(`16px "${f}"`)}));});
  assert(fonts.every(f=>f.loaded));check('Legal bundled fonts loaded',fonts);
  const visual=await page.evaluate(()=>{
    const root=getComputedStyle(document.documentElement);
    const panel=document.querySelector('.deck > section');
    return {
      night:root.getPropertyValue('--night').trim(),
      surface:root.getPropertyValue('--surface').trim(),
      prismFilm:root.getPropertyValue('--prism-film').trim(),
      panelRim:panel ? getComputedStyle(panel,'::after').borderImageSource : '',
      panelRimPointerEvents:panel ? getComputedStyle(panel,'::after').pointerEvents : '',
      rejectedObjects:document.querySelectorAll('.prism-field,.prism-shard,.prism-ray').length,
    };
  });
  assert.equal(visual.night,'#000909');
  assert.equal(visual.surface,'#001e1e');
  assert.match(visual.prismFilm,/#67ffd2/i);
  assert.notEqual(visual.panelRim,'none');
  assert.equal(visual.panelRimPointerEvents,'none');
  assert.equal(visual.rejectedObjects,0);
  await page.mouse.move(1580,260);
  const opticX=await page.locator('.instrument').evaluate(el=>getComputedStyle(el).getPropertyValue('--optic-x').trim());
  assert.notEqual(opticX,'50%');
  check('Rejected shard absent; cool-black palette and pointer-responsive prism locked',{...visual,opticX});
  await shot('01-command-deck.png');
  await compile('block');
  assert.equal(await page.locator('.authorization-lease').count(),0);
  assert.match(await page.locator('.receipt-fields').innerText(),/Authorized\s+0\.00 USDT/);
  check('BLOCK issues zero authority and no lease');
  await page.locator('.verdict-word').scrollIntoViewIfNeeded();
  await shot('02-block.png');
  await compile('review');
  assert.equal(await page.locator('.authorization-lease').count(),0);
  assert.match(await page.locator('.envelope').innerText(),/24\.37/);
  assert.match(await page.locator('.receipt-fields').innerText(),/Requested\s+100\.00 USDT[\s\S]*Authorized\s+0\.00 USDT/);
  await page.locator('.verdict-word').scrollIntoViewIfNeeded();
  await shot('03-review-safe-envelope.png');
  check('REVIEW 100.00 requested / 24.37 envelope / zero authority');
  await page.getByRole('button',{name:/Use admissible amount/}).click();
  assert.equal(await page.locator('.verdict-word').innerText(),'Draft');
  assert.equal(await page.locator('#quote').inputValue(),'24.37');
  assert.equal(await page.locator('.authorization-lease').count(),0);
  check('Applying admissible amount creates draft only');
  await compile('allow');
  await page.locator('.authorization-lease').waitFor();
  const leaseText=await page.locator('.authorization-lease').innerText();
  for (const label of ['KACHING!','Authorization lease','Action','Resource','Authorized ceiling','Audience','Policy','Valid for','Issuer','Ed25519']) assert(leaseText.includes(label),label);
  const clockBefore=await page.locator('.lease-clock').innerText();
  await page.waitForTimeout(1100);
  const clockAfter=await page.locator('.lease-clock').innerText();
  assert.notEqual(clockBefore,clockAfter);check('Lease fields and ticking countdown',{before:clockBefore,after:clockAfter});
  await page.locator('.authorization-lease').scrollIntoViewIfNeeded();
  await shot('04-authorization-lease.png');
  await page.getByLabel('Requested notional / USDT').fill('11');
  assert.equal(await page.locator('.verdict-word').innerText(),'Draft');
  assert.equal(await page.locator('.authorization-lease').count(),0,'Editing an ALLOW proposal must hide the prior lease');
  await page.getByRole('button',{name:'Enforcement lab',exact:true}).click();
  assert.equal(await page.locator('.enforcement-controls').count(),0,'Draft must not offer enforcement of a stale lease');
  check('ALLOW to edited draft hides previous authority');
  await compile('allow');
  await page.reload();
  await page.getByText('Local kernel connected',{exact:true}).waitFor();
  assert.equal(await page.locator('.authorization-lease').count(),0,'Reloaded draft must not display previous authority');
  check('Reload does not present a previous lease as current draft authority');
  await compile('allow');
  await page.getByRole('button',{name:'Open enforcement lab'}).click();
  await page.getByRole('button',{name:'Verify at enforcement boundary'}).click();
  await page.locator('.enforcement-result.pass').waitFor();
  assert.match(await page.locator('.enforcement-result').innerText(),/VALID/);
  check('Exact signed action VALID');
  await page.locator('.enforcement-lab').scrollIntoViewIfNeeded();
  await shot('05-enforcement-valid.png');
  for (const [mutation,reason] of [['amount','ACTION MISMATCH'],['resource','RESOURCE MISMATCH'],['audience','AUDIENCE MISMATCH'],['signature','SIGNATURE INVALID'],['replay','REPLAY DETECTED']]) {
    await compile('allow');
    await page.getByRole('button',{name:'Open enforcement lab'}).click();
    await page.getByLabel('Attempt',{exact:true}).selectOption(mutation);
    await page.getByRole('button',{name:'Verify at enforcement boundary'}).click();
    await page.locator('.enforcement-result.fail').waitFor();
    assert((await page.locator('.enforcement-result').innerText()).includes(reason));
    check(`${mutation} mutation rejected`,reason);
  }
  await page.getByRole('button',{name:'Run seven bypasses'}).click();
  await page.locator('.enforcement-gauntlet .arena-score').waitFor();
  assert.equal(await page.locator('.enforcement-gauntlet article .pass').count(),7);
  await page.locator('.enforcement-gauntlet').scrollIntoViewIfNeeded();
  await shot('06-seven-bypasses.png');
  check('Seven bypass gauntlet 7/7');
  await compile('block');
  await page.getByRole('button',{name:'Verify receipt',exact:false}).click();
  await page.waitForFunction(()=>document.querySelector('.integrity')?.textContent.includes('PASS'));
  await page.getByRole('button',{name:'Tamper copy'}).click();
  await page.waitForFunction(()=>document.querySelector('.integrity')?.textContent.includes('FAIL'));
  await page.locator('.integrity').scrollIntoViewIfNeeded();
  await shot('07-receipt-tamper.png');
  check('Original receipt PASS / tampered copy FAIL');
  await page.getByRole('button',{name:'Adversarial arena',exact:true}).click();
  await page.getByRole('button',{name:'Run five attacks'}).click();
  await page.locator('.arena .arena-score').waitFor();
  assert.equal(await page.locator('.arena article .pass').count(),5);check('Five policy attacks contained');
  await page.getByRole('button',{name:'Run judge demo'}).click();
  await page.waitForFunction(()=>document.querySelector('.notice')?.textContent.includes('7 / 7 —'),{},{timeout:30000});
  assert(await page.locator('.enforcement-lab').isVisible());
  check('Judge mode reaches 7/7 and lands in Enforcement Lab');
  await page.getByRole('button',{name:'Decision ledger',exact:true}).click();
  assert((await page.locator('.events details').count())>0);
  await page.locator('.events summary').first().click();
  assert(await page.locator('.events details[open] code').isVisible());check('Ledger event identity expands');
  await page.getByRole('button',{name:'Command deck',exact:true}).focus();
  await page.keyboard.press('Tab');
  const focus=await page.evaluate(()=>({text:document.activeElement.textContent,visible:document.activeElement.matches(':focus-visible'),outline:getComputedStyle(document.activeElement).outlineStyle}));
  assert(focus.visible);assert.notEqual(focus.outline,'none');check('Keyboard focus visible',focus);
  await page.emulateMedia({reducedMotion:'reduce'});
  await compile('allow');
  const reduced=await page.locator('.seal-trace rect').evaluate(el=>getComputedStyle(el).animationName);
  assert.equal(reduced,'none');check('Reduced motion disables seal animation');
  await page.getByRole('button',{name:'Run judge demo'}).click();
  await page.waitForFunction(()=>document.querySelector('.notice')?.textContent.includes('7 / 7 —'));
  check('Reduced-motion Judge mode completes');
  await page.emulateMedia({reducedMotion:'no-preference'});
  for (const width of [375,768,1280,1440,1920]) {
    await page.setViewportSize({width,height:width<768?812:1080});
    for(const panel of ['Command deck','Enforcement lab','Adversarial arena','Decision ledger']) {
      await page.getByRole('button',{name:panel,exact:true}).click();
      const geo=await page.evaluate(()=>({viewport:innerWidth,document:document.documentElement.scrollWidth,body:document.body.scrollWidth}));
      assert(geo.document<=width && geo.body<=width,`${panel} overflow at ${width}: ${JSON.stringify(geo)}`);
      findings.viewports.push({width,panel,...geo,status:'PASS'});
    }
    await page.getByRole('button',{name:'Command deck',exact:true}).click();
    await page.evaluate(()=>scrollTo(0,0));
  }
  check('Five widths, all four workspaces: no horizontal overflow');
  const privateLabels=await page.evaluate(()=>/free_usdt|api[_ ]?secret|api[_ ]?key|binance uid|private[_ ]?key|private balance/i.test(document.body.innerText));
  assert.equal(privateLabels,false);check('No private field labels rendered');
  assert.equal(findings.console.length,0);assert.equal(findings.networkFailures.length,0);check('Zero relevant console warnings/errors and failed requests');
  findings.status='PASS';
} catch(error) {findings.status='FAIL';findings.error=error.stack;console.error(error);process.exitCode=1;}
finally {
  for (const name of screenshotNames) {
    try {findings.artifactHashes[`docs/screenshots/${name}`]=createHash('sha256').update(await readFile(new URL(name,output))).digest('hex');}
    catch {/* A failed run may stop before all seven screenshots exist. */}
  }
  await writeFile(record,JSON.stringify(findings,null,2)+'\n');
  await browser.close();
}
