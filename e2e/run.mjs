/* Browser tests: the built site (dist/) is served and driven in a real Chromium.
   - Python runs for real: Pyodide is served from dist/pyodide.
   - C++ and Java run for real too: requests to the Judge0 URL are answered by tests/helpers/fakeJudge0.ts,
     which compiles with the local g++ / javac.
   Run:  npm run build && npm run e2e        (set CHROMIUM_PATH to use a specific browser binary) */
import { readFileSync, existsSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { chromium } from 'playwright-core';
import { preview } from 'vite';
import { handleJudge0, hasToolchain } from '../tests/helpers/fakeJudge0.ts';

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
const browser = await chromium.launch({ executablePath: process.env.CHROMIUM_PATH || undefined, args: ['--no-sandbox'] });

let failed = 0;
const log = (ok, name, extra = '') => {
  console.log(`${ok ? 'ok  ' : 'FAIL'} ${name}${extra ? '  ' + extra : ''}`);
  if (!ok) failed++;
};
async function scenario(name, fn, { viewport, allowConsole } = {}) {
  const ctx = await browser.newContext({ viewport: viewport ?? { width: 1360, height: 900 } });
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
    await fn(page);
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
  await page.goto(base + (hash ? '#' + hash : ''));
  await page.waitForSelector('#view');
};
const setCode = async (page, code) => {
  const ta = page.locator('textarea');
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
  const ta = page.locator('textarea');
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
  await page.waitForSelector('textarea');
  if (!(await page.locator('textarea').inputValue()).includes('// my note')) throw new Error('code lost');
  expectEq(await page.locator('select[aria-label="Language"]').inputValue(), 'javascript', 'language remembered');
  await page.waitForSelector('.pv-tags .solved-badge');
  await page.click('a:has-text("All problems")');
  await page.waitForSelector('.dot.done');
  // switching language keeps each language's code separate
  await page.click('a.row:has-text("Two Sum")');
  await pickLang(page, 'python');
  if ((await page.locator('textarea').inputValue()).includes('// my note')) throw new Error('code leaked between languages');
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

await scenario('every problem page opens and has starter code', async (page) => {
  for (const p of problems) {
    await open(page, '/problem/' + p.id);
    await page.waitForSelector('textarea');
    const v = await page.locator('textarea').inputValue();
    if (!v.includes(p.fn)) throw new Error(`${p.id}: starter code lacks ${p.fn}`);
  }
});

await browser.close();
await server.close();
console.log(failed ? `\n${failed} browser scenario(s) failed` : '\nAll browser scenarios passed');
process.exit(failed ? 1 : 0);
