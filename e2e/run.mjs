/* Browser tests: the built site (dist/) is served and driven in a real Chromium.
   - Python runs for real: Pyodide is served from dist/pyodide.
   - C++ and Java run for real too: requests to the Judge0 URL are answered by tests/helpers/fakeJudge0.ts,
     which compiles with the local g++ / javac.
   Run:  npm run build && npm run e2e        (set CHROMIUM_PATH to use a specific browser binary) */
import { readFileSync, existsSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { chromium } from 'playwright-core';
import { build, preview } from 'vite';
import { handleJudge0, hasToolchain } from '../tests/helpers/fakeJudge0.ts';
import { FakeSupabase } from '../tests/helpers/fakeSupabase.ts';

const root = fileURLToPath(new URL('..', import.meta.url));
if (!existsSync(root + 'dist/index.html')) {
  console.error('dist/ is missing. Run `npm run build` first.');
  process.exit(1);
}
const problems = JSON.parse(readFileSync(root + 'src/data/problems.json', 'utf8'));
const byId = Object.fromEntries(problems.map((p) => [p.id, p]));
const fixture = (id, ext) => readFileSync(root + `tests/fixtures/${id}.${ext}`, 'utf8');

const JS_TWO_SUM = `function twoSum(nums, target) {
  const seen = new Map();
  for (let i = 0; i < nums.length; i++) {
    if (seen.has(target - nums[i])) return [seen.get(target - nums[i]), i];
    seen.set(nums[i], i);
  }
  return [];
}
`;

const server = await preview({ root, preview: { port: 0, host: '127.0.0.1' }, logLevel: 'error' });
const base = server.resolvedUrls.local[0];
let currentBase = base;

/* A second build of the site with accounts switched on, pointed at a fake Supabase project. */
const FAKE_SUPABASE = 'https://fake-project.supabase.test';
let cloudServer;
async function cloudBase() {
  if (!cloudServer) {
    process.env.VITE_SUPABASE_URL = FAKE_SUPABASE;
    process.env.VITE_SUPABASE_ANON_KEY = 'public-anon-key';
    process.env.VITE_AUTH_PROVIDERS = 'google';
    await build({ root, logLevel: 'error', build: { outDir: 'dist-cloud', emptyOutDir: true } });
    delete process.env.VITE_SUPABASE_URL;
    delete process.env.VITE_SUPABASE_ANON_KEY;
    delete process.env.VITE_AUTH_PROVIDERS;
    cloudServer = await preview({ root, build: { outDir: 'dist-cloud' }, preview: { port: 0, host: '127.0.0.1' }, logLevel: 'error' });
  }
  return cloudServer.resolvedUrls.local[0];
}
const cors = { 'access-control-allow-origin': '*', 'access-control-allow-headers': '*', 'access-control-allow-methods': '*', 'access-control-expose-headers': '*' };
async function attachSupabase(page, fake) {
  await page.route(FAKE_SUPABASE + '/**', async (route) => {
    const req = route.request();
    if (req.method() === 'OPTIONS') return route.fulfill({ status: 204, headers: cors });
    const r = fake.handle(req.method(), req.url(), req.headers(), req.postData());
    return route.fulfill({ status: r.status, headers: { ...cors, 'content-type': 'application/json', ...r.headers }, body: r.json === undefined ? '' : JSON.stringify(r.json) });
  });
}
const browser = await chromium.launch({ executablePath: process.env.CHROMIUM_PATH || undefined, args: ['--no-sandbox'] });

let failed = 0;
const log = (ok, name, extra = '') => {
  console.log(`${ok ? 'ok  ' : 'FAIL'} ${name}${extra ? '  ' + extra : ''}`);
  if (!ok) failed++;
};
async function scenario(name, fn, { viewport, allowConsole, cloud } = {}) {
  currentBase = cloud ? await cloudBase() : base;
  const ctx = await browser.newContext({ viewport: viewport ?? { width: 1360, height: 900 }, acceptDownloads: true });
  const page = await ctx.newPage();
  const problemsSeen = [];
  page.on('console', (m) => ['error', 'warning'].includes(m.type()) && problemsSeen.push(`[console.${m.type()}] ${m.text()}`));
  page.on('pageerror', (e) => problemsSeen.push(`[pageerror] ${e.message}`));
  // Fake Judge0
  await page.route('https://ce.judge0.com/**', async (route) => {
    const req = route.request();
    const cors = { 'access-control-allow-origin': '*', 'access-control-allow-headers': '*', 'access-control-allow-methods': '*' };
    if (req.method() === 'OPTIONS') return route.fulfill({ status: 204, headers: cors });
    const u = new URL(req.url());
    const r = handleJudge0(req.method(), u.pathname + u.search, req.postData());
    return route.fulfill({ status: r.status, headers: { ...cors, 'content-type': 'application/json' }, body: JSON.stringify(r.json) });
  });
  try {
    await fn(page, ctx);
    const bad = allowConsole ? problemsSeen.filter((m) => !allowConsole.test(m)) : problemsSeen;
    log(bad.length === 0, name, bad.join(' | '));
  } catch (e) {
    const where = (String(e.stack).match(/run\.mjs:(\d+)/) || [])[1];
    log(false, name, String(e.message).split('\n')[0] + (where ? ` (e2e/run.mjs:${where})` : ''));
  } finally {
    await ctx.close();
  }
}

const open = async (page, hash = '') => {
  await page.goto(currentBase + (hash ? '#' + hash : ''));
  await page.waitForSelector('#view');
};
const setCode = async (page, code) => {
  const ta = page.locator('.stack textarea');
  await ta.click();
  await page.keyboard.press('Control+A');
  await page.keyboard.insertText(code);
};
const pickLang = (page, lang) => page.selectOption('select[aria-label="Language"]', lang);
const verdict = async (page, timeout = 30000) => {
  await page.locator('.verdict h3').waitFor({ timeout });
  return (await page.locator('.verdict h3').innerText()).trim();
};
const expectEq = (a, b, what) => {
  if (a !== b) throw new Error(`${what}: expected ${JSON.stringify(b)}, got ${JSON.stringify(a)}`);
};

await scenario('landing page renders and navigates', async (page) => {
  await open(page);
  expectEq(await page.title(), 'Letify: free DSA practice', 'title');
  await page.waitForSelector('.hero h1');
  expectEq(await page.locator('.statline b').first().innerText(), String(problems.length), 'problem count');
  await page.click('.hero-cta a.primary');
  await page.waitForSelector('.table .row:not(.head)');
  expectEq(await page.locator('.table a.row').count(), problems.length, 'rows');
  await page.fill('input[type=search]', 'sum');
  const n = await page.locator('.table a.row').count();
  if (n < 2 || n >= problems.length) throw new Error('search did not filter: ' + n);
  await page.fill('input[type=search]', 'zzzz');
  await page.waitForSelector('.empty');
  await page.fill('input[type=search]', '');
  await page.click('.seg button:has-text("Hard")');
  expectEq(await page.locator('.table a.row').count(), problems.filter((p) => p.diff === 'Hard').length, 'hard rows');
});

await scenario('old-style links and unknown routes still work', async (page) => {
  await open(page, 'two-sum');
  await page.waitForSelector('.pv-head h1');
  await open(page, '/problem/does-not-exist');
  await page.waitForSelector('.hero h1');
});

await scenario('theme toggle persists', async (page) => {
  await open(page);
  await page.click('button[aria-label^="Switch between"]');
  const t = await page.evaluate(() => document.documentElement.dataset.theme);
  if (t !== 'dark' && t !== 'light') throw new Error('no theme set');
  await page.reload();
  expectEq(await page.evaluate(() => document.documentElement.dataset.theme), t, 'theme after reload');
});

await scenario('statement, hints and editorial tabs', async (page) => {
  await open(page, '/problem/two-sum');
  await page.waitForSelector('.pv-head h1');
  expectEq((await page.locator('.ex').count()), 2, 'examples');
  await page.click('[role=tab]:has-text("Hints")');
  await page.click('button:has-text("Show hint 1")');
  await page.click('button:has-text("Show hint 2")');
  expectEq(await page.locator('.hint').count(), 2, 'hints shown');
  await page.click('[role=tab]:has-text("Editorial")');
  expectEq(await page.locator('pre.block').count(), 0, 'solution hidden at first');
  await page.click('button:has-text("Show editorial")');
  await page.waitForSelector('text=Reference solution (Python)');
});

await scenario('editor: auto-close, indent, tab, comment toggle', async (page) => {
  await open(page, '/problem/two-sum');
  await pickLang(page, 'javascript');
  const ta = page.locator('.stack textarea');
  await ta.click();
  await page.keyboard.press('Control+A');
  await page.keyboard.press('Delete');
  await page.keyboard.type('if (a[0]) {');
  expectEq(await ta.inputValue(), 'if (a[0]) {}', 'auto-closed brackets');
  await page.keyboard.press('Enter');
  await page.keyboard.type('x = "hi');
  expectEq(await ta.inputValue(), 'if (a[0]) {\n    x = "hi"\n}', 'indent after { and quote closing');
  await page.keyboard.press('End');
  await page.keyboard.press('Control+/');
  expectEq((await ta.inputValue()).split('\n')[1], '    // x = "hi"', 'comment toggled on');
  await page.keyboard.press('Control+/');
  expectEq((await ta.inputValue()).split('\n')[1], '    x = "hi"', 'comment toggled off');
  await page.keyboard.press('Shift+Tab');
  expectEq((await ta.inputValue()).split('\n')[1], 'x = "hi"', 'outdent');
  await page.keyboard.press('Tab');
  expectEq((await ta.inputValue()).split('\n')[1], '    x = "hi"', 'indent');
  await page.keyboard.press('Control+Z');
  expectEq((await ta.inputValue()).split('\n')[1], 'x = "hi"', 'undo works');
  // syntax colours are drawn behind the text
  if ((await page.locator('.hl .tk-kw').count()) < 1) throw new Error('no highlighted keyword');
  // line numbers follow the text
  expectEq((await page.locator('.gutter').innerText()).split('\n').length, 3, 'gutter lines');
});

await scenario('JavaScript: run, wrong answer, runtime error, timeout, submit', async (page) => {
  await open(page, '/problem/two-sum');
  await pickLang(page, 'javascript');
  await setCode(page, JS_TWO_SUM);
  await page.click('#root button:has-text("Run")');
  expectEq(await verdict(page), 'Accepted', 'run verdict');
  expectEq(await page.locator('.cases button.pass').count(), 3, 'sample cases');

  await setCode(page, 'function twoSum(nums, target) { return [0, 0]; }');
  await page.keyboard.press('Control+Enter');
  expectEq(await verdict(page), 'Wrong Answer', 'wrong answer');
  await page.waitForSelector('text=Your output');

  await setCode(page, 'function twoSum(nums, target) { return nums.nope.x; }');
  await page.click('button:has-text("Run")');
  await page.waitForFunction(() => document.querySelector('.verdict h3')?.textContent === 'Runtime Error');

  await setCode(page, 'function twoSum(nums, target) { while (true) {} }');
  await page.click('button:has-text("Run")');
  await page.waitForFunction(() => document.querySelector('.verdict h3')?.textContent === 'Time Limit Exceeded', null, { timeout: 15000 });

  await setCode(page, 'function twoSum(nums, target) { return ; }');
  await page.click('button:has-text("Run")');
  await page.waitForFunction(() => document.querySelector('.verdict h3')?.textContent === 'Runtime Error');

  await setCode(page, 'function twoSum( {');
  await page.click('button:has-text("Run")');
  await page.waitForFunction(() => document.querySelector('.verdict h3')?.textContent === 'Error in your code');

  await setCode(page, JS_TWO_SUM);
  await page.click('button:has-text("Submit")');
  await page.waitForSelector('.toast');
  expectEq(await verdict(page), 'Accepted', 'submit verdict');
  await page.waitForSelector('.pv-tags .solved-badge');
  expectEq((await page.locator('.count').innerText()).trim(), `1 of ${problems.length} solved`, 'header count');
  await page.waitForSelector('a:has-text("Next:")');
});

await scenario('code and progress survive a reload', async (page) => {
  await open(page, '/problem/two-sum');
  await pickLang(page, 'javascript');
  await setCode(page, JS_TWO_SUM + '// my note\n');
  await page.click('button:has-text("Submit")');
  await verdict(page);
  await page.waitForTimeout(600);
  await page.reload();
  await page.waitForSelector('.stack textarea');
  if (!(await page.locator('.stack textarea').inputValue()).includes('// my note')) throw new Error('code lost');
  expectEq(await page.locator('select[aria-label="Language"]').inputValue(), 'javascript', 'language remembered');
  await page.waitForSelector('.pv-tags .solved-badge');
  await page.click('a:has-text("All problems")');
  await page.waitForSelector('.dot.done');
  // switching language keeps each language's code separate
  await page.click('a.row:has-text("Two Sum")');
  await pickLang(page, 'python');
  if ((await page.locator('.stack textarea').inputValue()).includes('// my note')) throw new Error('code leaked between languages');
});

await scenario('Python runs in the browser (Pyodide)', async (page) => {
  await open(page, '/problem/two-sum');
  await setCode(page, byId['two-sum'].solution);
  await page.click('button:has-text("Run")');
  expectEq(await verdict(page, 120000), 'Accepted', 'python run');
  await page.click('button:has-text("Submit")');
  await page.waitForFunction(() => /test cases passed/.test(document.querySelector('.verdict')?.textContent ?? ''), null, { timeout: 60000 });
  expectEq(await verdict(page), 'Accepted', 'python submit');
  await setCode(page, 'def twoSum(nums, target):\n    return nums[99]\n');
  await page.click('button:has-text("Run")');
  await page.waitForFunction(() => document.querySelector('.verdict h3')?.textContent === 'Runtime Error');
  await page.waitForSelector('pre.block:has-text("IndexError")');
  await setCode(page, 'def twoSum(nums, target):\n    while True: pass\n');
  await page.click('button:has-text("Run")');
  await page.waitForFunction(() => document.querySelector('.verdict h3')?.textContent === 'Time Limit Exceeded', null, { timeout: 20000 });
  // the runtime restarts after a timeout and works again
  await setCode(page, byId['two-sum'].solution);
  await page.click('button:has-text("Run")');
  await page.waitForFunction(() => document.querySelector('.verdict h3')?.textContent === 'Accepted', null, { timeout: 120000 });
});

if (hasToolchain.cpp && hasToolchain.java) {
  for (const [lang, ext, label] of [['cpp', 'cpp', 'C++'], ['java', 'java', 'Java']]) {
    await scenario(`${label}: compile + run through Judge0`, async (page) => {
      await open(page, '/problem/valid-parentheses');
      await pickLang(page, lang);
      await setCode(page, fixture('valid-parentheses', ext));
      await page.click('button:has-text("Submit")');
      expectEq(await verdict(page, 90000), 'Accepted', `${label} submit`);
      const bad = fixture('valid-parentheses', ext).replace('return', 'retrun');
      await setCode(page, bad);
      await page.click('button:has-text("Run")');
      await page.waitForFunction(() => document.querySelector('.verdict h3')?.textContent === 'Compile Error', null, { timeout: 60000 });
    });
  }
} else {
  console.log('skip C++ / Java scenarios (g++ / javac not installed)');
}

await scenario('engine settings: bad URL is refused, good URL is saved', async (page) => {
  await open(page, '/problem/two-sum');
  await page.click('button[aria-label="Engine settings"]');
  const url = page.locator('.settings input').first();
  await url.fill('http://evil.example.com');
  await page.click('.settings button:has-text("Save")');
  await page.waitForSelector('.settings [role=alert]');
  await url.fill('https://judge.example.org/');
  await page.click('.settings button:has-text("Save")');
  await page.waitForSelector('.toast');
  await page.reload();
  await page.click('button[aria-label="Engine settings"]');
  expectEq(await page.locator('.settings input').first().inputValue(), 'https://judge.example.org', 'saved URL');
});

await scenario('unreachable Judge0 server gives a readable message', async (page) => {
  await page.route('https://down.example.org/**', (r) => r.abort());
  await open(page, '/problem/two-sum');
  await page.click('button[aria-label="Engine settings"]');
  await page.locator('.settings input').first().fill('https://down.example.org');
  await page.click('.settings button:has-text("Save")');
  await pickLang(page, 'cpp');
  await page.click('button:has-text("Run")');
  expectEq(await verdict(page), 'Could not run', 'engine error');
  await page.waitForSelector('pre.block:has-text("Could not reach the Judge0 server")');
}, { allowConsole: /ERR_FAILED|Failed to load resource/ });

await scenario('phone layout: panes switch', async (page) => {
  await open(page, '/problem/two-sum');
  await page.waitForSelector('.mobile-seg');
  if (!(await page.locator('.pane.problem').isVisible())) throw new Error('problem pane hidden');
  if (await page.locator('.pane.code').isVisible()) throw new Error('code pane should be hidden');
  await page.click('.mobile-seg button:has-text("Code")');
  if (!(await page.locator('.pane.code').isVisible())) throw new Error('code pane not shown');
  const overflow = await page.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth);
  if (overflow > 0) throw new Error('horizontal scroll: ' + overflow);
}, { viewport: { width: 390, height: 800 } });


const fnOf = (id) => byId[id].fn;
const submitJs = async (page, id, code) => {
  await pickLang(page, 'javascript');
  await setCode(page, code);
  await page.click('button:has-text("Submit")');
  return verdict(page);
};

await scenario('study plans: list, detail and start', async (page) => {
  await open(page, '/plans');
  await page.waitForSelector('.plan-card');
  if ((await page.locator('.plan-card').count()) < 5) throw new Error('too few plans');
  await page.click('.plan-card h2 a >> nth=0');
  await page.waitForSelector('.plan-section');
  expectEq(await page.locator('.plan-progress [role=progressbar]').getAttribute('aria-valuenow'), '0', 'nothing solved yet');
  await page.click('.plan-progress a.primary');
  await page.waitForSelector('.pv-head h1');
  // finishing a problem moves the plan forward
  const id = decodeURIComponent((await page.url()).split('/problem/')[1]);
  if (id === 'two-sum') {
    expectEq(await submitJs(page, id, JS_TWO_SUM), 'Accepted', 'plan problem');
    await page.goBack();
    await page.waitForSelector('.plan-progress');
    expectEq(await page.locator('.plan-progress [role=progressbar]').getAttribute('aria-valuenow'), '1', 'plan progress');
  }
});

await scenario('problems page: daily challenge, random problem, plans link', async (page) => {
  await open(page, '/problems');
  await page.waitForSelector('.daily');
  await page.click('.daily a.btn');
  await page.waitForSelector('.pv-head h1');
  await page.goBack();
  await page.click('button:has-text("Random problem")');
  await page.waitForSelector('.pv-head h1');
  await open(page, '/problems');
  await page.click('.intro-actions a:has-text("Study plans")');
  await page.waitForSelector('.plan-card');
});

await scenario('submissions, notes, stars and the profile page', async (page) => {
  await open(page, '/problem/two-sum');
  expectEq(await submitJs(page, 'two-sum', JS_TWO_SUM), 'Accepted', 'first submit');
  await setCode(page, 'function twoSum(nums, target) { return [0, 0]; }');
  await page.click('button:has-text("Submit")');
  await page.waitForFunction(() => document.querySelector('.verdict h3')?.textContent === 'Wrong Answer');

  await page.click('[role=tab]:has-text("Submissions")');
  expectEq(await page.locator('.subs li').count(), 2, 'two submissions');
  expectEq(await page.locator('.subs li >> nth=0').locator('.vtag').innerText(), 'Wrong Answer', 'newest first');
  await page.click('.subs li >> nth=1 >> summary');
  await page.click('.subs li >> nth=1 >> button:has-text("Restore")');
  if (!(await page.locator('.stack textarea').inputValue()).includes('seen.has')) throw new Error('restore did not load the code');

  await page.click('[role=tab]:has-text("Notes")');
  await page.fill('textarea.notes', 'hash map: store the complement');
  await page.click('.star-btn');
  expectEq(await page.locator('.star-btn').getAttribute('aria-pressed'), 'true', 'starred');
  await page.waitForTimeout(800);
  await page.reload();
  await page.waitForSelector('.pv-head h1');
  await page.click('[role=tab]:has-text("Notes")');
  expectEq(await page.locator('textarea.notes').inputValue(), 'hash map: store the complement', 'note after reload');

  await open(page, '/problems');
  await page.selectOption('select[aria-label="Status"]', 'Starred');
  expectEq(await page.locator('.table a.row').count(), 1, 'starred filter');

  await open(page, '/profile');
  await page.waitForSelector('.tiles');
  const tiles = await page.locator('.tile b').allInnerTexts();
  if (!tiles[0].startsWith('1')) throw new Error('solved tile: ' + tiles[0]);
  expectEq(tiles[1].trim(), '1', 'streak tile');
  if ((await page.locator('.hm.hm1, .hm.hm2').count()) < 1) throw new Error('heatmap shows no activity');
  await page.waitForSelector('.badge.on:has-text("First solve")');
  expectEq(await page.locator('.sub-table tbody tr').count(), 2, 'submissions table');
  await page.waitForSelector('.chip.link:has-text("Two Sum")');

  const [dl] = await Promise.all([page.waitForEvent('download'), page.click('button:has-text("Export progress")')]);
  const exported = JSON.parse(readFileSync(await dl.path(), 'utf8'));
  if (!exported.solved['two-sum'] || exported.subs.length !== 2) throw new Error('export is missing data');
});

await scenario('import merges progress into an empty browser', async (page) => {
  await open(page, '/profile');
  await page.waitForSelector('.tiles');
  const file = JSON.stringify({ v: 1, solved: { 'two-sum': { lang: 'python', at: 1700000000000 } }, subs: [], notes: {}, stars: {}, code: {}, contests: {} });
  await page.setInputFiles('input[type=file]', { name: 'p.json', mimeType: 'application/json', buffer: Buffer.from(file) });
  await page.waitForSelector('.toast:has-text("imported")');
  await page.waitForFunction(() => document.querySelector('.tile b')?.textContent?.startsWith('1'));
  await page.setInputFiles('input[type=file]', { name: 'bad.json', mimeType: 'application/json', buffer: Buffer.from('not json') });
  await page.waitForSelector('.toast:has-text("could not be read")');
});

await scenario('custom input runs your code on any input', async (page) => {
  await open(page, '/problem/two-sum');
  await pickLang(page, 'javascript');
  await setCode(page, JS_TWO_SUM);
  await page.click('.bottom-tabs button:has-text("Custom input")');
  const fields = page.locator('.custom-field textarea');
  expectEq(await fields.count(), 2, 'one field per argument');
  await fields.nth(0).fill('[1, 2, 3, 4]');
  await fields.nth(1).fill('7');
  await page.click('button:has-text("Run on this input")');
  await page.waitForSelector('.custom pre.block:has-text("[2,3]")');
  await fields.nth(0).fill('[1, 2');
  await page.click('button:has-text("Run on this input")');
  await page.waitForSelector('.field-error');
  await fields.nth(0).fill('[1, 2]');
  await setCode(page, 'function twoSum(nums, target) { throw new Error("boom"); }');
  await page.click('button:has-text("Run on this input")');
  await page.waitForSelector('.custom pre.block:has-text("boom")');
});

await scenario('virtual contest: start, locked help, wrong attempt, end', async (page) => {
  page.on('dialog', (d) => d.accept());
  await open(page, '/contest');
  await page.click('button:has-text("Start a contest")');
  await page.waitForSelector('[role=timer]');
  expectEq(await page.locator('.contest-row').count(), 4, 'four problems');
  await page.waitForSelector('.contest-pill');
  const href = await page.locator('.contest-row >> nth=0').getAttribute('href');
  const id = decodeURIComponent(href.split('/problem/')[1]);
  await page.click('.contest-row >> nth=0');
  await page.waitForSelector('.contest-banner');
  await page.click('[role=tab]:has-text("Hints")');
  await page.waitForSelector('text=closed for this problem');
  await pickLang(page, 'javascript');
  await setCode(page, `function ${fnOf(id)}() { return null; }`);
  await page.click('button:has-text("Submit")');
  await page.waitForFunction(() => /Wrong Answer|Runtime Error/.test(document.querySelector('.verdict h3')?.textContent ?? ''));
  await page.waitForSelector('.contest-banner:has-text("1 wrong attempt")');
  // the contest survives a reload
  await page.reload();
  await page.waitForSelector('.contest-banner');
  await page.click('.contest-banner a');
  await page.click('button:has-text("End contest")');
  await page.waitForSelector('text=Contest finished');
  await page.waitForSelector('.sub-table tbody tr');
  if (await page.locator('.contest-pill').count()) throw new Error('contest pill should be gone');
  // hints open again
  await open(page, '/problem/' + id);
  await page.click('[role=tab]:has-text("Hints")');
  await page.waitForSelector('button:has-text("Show hint 1")');
});

await scenario('new pages fit a phone screen', async (page) => {
  for (const hash of ['/', '/problems', '/plans', '/plan/' + 'x', '/profile', '/contest', '/problem/two-sum']) {
    await open(page, hash);
    await page.waitForTimeout(150);
    const overflow = await page.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth);
    if (overflow > 0) throw new Error(`horizontal scroll ${overflow}px on ${hash}`);
  }
}, { viewport: { width: 390, height: 800 } });

await scenario('without accounts configured there is no sign-in button', async (page) => {
  await open(page);
  expectEq(await page.locator('button:has-text("Sign in")').count(), 0, 'sign-in button');
  await open(page, '/profile');
  expectEq(await page.locator('.linklike').count(), 0, 'sign-in link');
});

await scenario('accounts: sign in, progress syncs, second device gets it', async (page, ctx) => {
  const fake = new FakeSupabase();
  await attachSupabase(page, fake);
  await open(page, '/problem/two-sum');
  await page.click('header button:has-text("Sign in")');
  await page.waitForSelector('dialog.auth[open]');
  await page.fill('dialog input[type=email]', 'asha@example.com');
  await page.fill('dialog input[type=password]', 'correct horse battery');
  await page.click('dialog button[type=submit]');
  await page.waitForSelector('button.avatar');
  expectEq(await submitJs(page, 'two-sum', JS_TWO_SUM), 'Accepted', 'submit while signed in');
  await page.click('button.avatar');
  await page.waitForSelector('.menu-sync.synced', { timeout: 15000 });
  for (let i = 0; i < 60 && ![...fake.rows.values()][0]?.data.solved?.['two-sum']; i++) await page.waitForTimeout(250);
  const row = [...fake.rows.values()][0];
  if (!row || !row.data.solved['two-sum']) throw new Error('cloud row is missing the solve');
  if (!row.data.code['two-sum.javascript']) throw new Error('cloud row is missing the code');

  // a second browser, same account
  const other = await ctx.browser().newContext({ viewport: { width: 1360, height: 900 } });
  const p2 = await other.newPage();
  await attachSupabase(p2, fake);
  await p2.goto(currentBase + '#/problem/two-sum');
  await p2.waitForSelector('#view');
  await p2.click('header button:has-text("Sign in")');
  await p2.fill('dialog input[type=email]', 'asha@example.com');
  await p2.fill('dialog input[type=password]', 'correct horse battery');
  await p2.click('dialog button[type=submit]');
  await p2.waitForSelector('button.avatar');
  await p2.waitForSelector('.pv-tags .solved-badge', { timeout: 15000 });
  await p2.reload();
  await p2.waitForSelector('.pv-tags .solved-badge');
  // change something on the second device; the first one picks it up
  await p2.click('.star-btn');
  await p2.waitForFunction(() => document.querySelector('.star-btn')?.getAttribute('aria-pressed') === 'true');
  await p2.waitForTimeout(4000);
  if (![...fake.rows.values()][0].data.stars['two-sum']?.on) throw new Error('the star did not reach the cloud');
  await page.evaluate(() => window.dispatchEvent(new Event('online')));
  await page.waitForFunction(() => document.querySelector('.star-btn')?.getAttribute('aria-pressed') === 'true', null, { timeout: 15000 });
  // signing out leaves the progress in the account
  page.on('dialog', (d) => d.accept());
  if (!(await page.locator('.menu').count())) await page.click('button.avatar');
  await page.click('button:has-text("Sign out and clear")');
  await page.waitForSelector('header button:has-text("Sign in")');
  expectEq((await page.locator('.count').innerText()).trim(), `0 of ${problems.length} solved`, 'cleared in this browser');
  if (![...fake.rows.values()][0].data.solved['two-sum']) throw new Error('sign out must not delete cloud data');
  await other.close();
}, { cloud: true, allowConsole: /Failed to load resource/ });

await scenario('accounts: a down server never blocks practice', async (page) => {
  await page.route(FAKE_SUPABASE + '/**', (r) => r.abort());
  await open(page, '/problem/two-sum');
  expectEq(await submitJs(page, 'two-sum', JS_TWO_SUM), 'Accepted', 'works offline from the cloud');
  await page.waitForSelector('.pv-tags .solved-badge');
}, { cloud: true, allowConsole: /ERR_FAILED|Failed to load resource|Failed to fetch/ });

await scenario('every problem page opens and has starter code', async (page) => {
  for (const p of problems) {
    await open(page, '/problem/' + p.id);
    await page.waitForSelector('.stack textarea');
    const v = await page.locator('.stack textarea').inputValue();
    if (!v.includes(p.fn)) throw new Error(`${p.id}: starter code lacks ${p.fn}`);
  }
});

await browser.close();
await server.close();
await cloudServer?.close();
console.log(failed ? `\n${failed} browser scenario(s) failed` : '\nAll browser scenarios passed');
process.exit(failed ? 1 : 0);
