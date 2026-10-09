/* Runs the real Python harness inside the real Pyodide (from node_modules) against every problem's reference
   solution and every test case, then judges the results with the same code the site uses. */
import { readFileSync } from 'node:fs';
import { createRequire } from 'node:module';
import { dirname } from 'node:path';
import { describe, expect, it } from 'vitest';
import { PROBLEMS, loadTests } from '../src/data';
import { makeVerdict } from '../src/core/verdict';
import { starter } from '../src/core/languages';
import type { CaseResult } from '../src/types';

const require = createRequire(import.meta.url);
const harness = readFileSync(new URL('../src/engines/harness.py', import.meta.url), 'utf8');

interface Py {
  runPython(c: string): unknown;
  globals: { get(n: string): (...a: string[]) => string };
}
let pyPromise: Promise<Py> | null = null;
function py(): Promise<Py> {
  pyPromise ??= (async () => {
    const { loadPyodide } = require('pyodide') as { loadPyodide(o: { indexURL: string }): Promise<Py> };
    const p = await loadPyodide({ indexURL: dirname(require.resolve('pyodide/package.json')) + '/' });
    p.runPython(harness);
    return p;
  })();
  return pyPromise;
}

async function run(code: string, fn: string, tests: { args: unknown[] }[]) {
  const p = await py();
  const prep = JSON.parse(p.globals.get('_prep')(code, fn)) as { type: string; message?: string };
  if (prep.type === 'compile_error') return { status: 'compile_error' as const, message: prep.message! };
  const cases: CaseResult[] = [];
  for (const t of tests) {
    const r = JSON.parse(p.globals.get('_run1')(JSON.stringify(t.args))) as CaseResult;
    cases.push(r);
    if (!r.ok) break;
  }
  return { status: 'ok' as const, cases };
}

describe('python harness in Pyodide', () => {
  it('accepts the reference solution of every problem on every test', async () => {
    for (const p of PROBLEMS) {
      const tests = await loadTests(p.id);
      const r = await run(p.solution, p.fn, tests);
      const v = makeVerdict(p, tests, r);
      expect(v, p.id).toMatchObject({ kind: 'ac', passed: tests.length });
      // The site stops a case after 5 s. The reference must stay far below that so ordinary solutions fit too.
      const slowest = r.status === 'ok' ? Math.max(...r.cases.map((c) => c.ms ?? 0)) : 0;
      if (slowest > 400) console.log(`slow reference: ${p.id} ${Math.round(slowest)} ms`);
      expect(slowest, `${p.id} slowest case`).toBeLessThan(1500);
    }
  }, 600_000);

  it('reports a wrong answer, a runtime error and a compile error', async () => {
    const p = PROBLEMS.find((x) => x.id === 'two-sum')!;
    const tests = (await loadTests(p.id)).slice(0, 3);
    const wrong = starter(p, 'python').replace('pass', 'return [0, 0]');
    expect(makeVerdict(p, tests, await run(wrong, p.fn, tests))).toMatchObject({ kind: 'wa', failIndex: 0 });
    const crash = starter(p, 'python').replace('pass', 'return nums[99]');
    const rv = makeVerdict(p, tests, await run(crash, p.fn, tests));
    expect(rv).toMatchObject({ kind: 're' });
    if (rv.kind === 're') expect(rv.message).toContain('IndexError');
    const bad = await run('def twoSum(:\n  pass', p.fn, tests);
    expect(bad).toMatchObject({ status: 'compile_error' });
    const missing = await run('def other():\n  pass', p.fn, tests);
    expect(missing).toMatchObject({ status: 'compile_error', message: expect.stringContaining('not defined') });
  }, 60_000);

  it('captures printed output', async () => {
    const p = PROBLEMS.find((x) => x.id === 'two-sum')!;
    const tests = (await loadTests(p.id)).slice(0, 1);
    const r = await run('def twoSum(nums, target):\n    print("hello")\n    return [0, 1]', p.fn, tests);
    expect(r.status === 'ok' && r.cases[0]?.stdout).toBe('hello\n');
  }, 60_000);

  it('also accepts a class-style Solution', async () => {
    const p = PROBLEMS.find((x) => x.id === 'two-sum')!;
    const tests = (await loadTests(p.id)).slice(0, 3);
    const src = 'class Solution:\n    def twoSum(self, nums, target):\n        d = {}\n        for i, x in enumerate(nums):\n            if target - x in d: return [d[target - x], i]\n            d[x] = i\n';
    expect(makeVerdict(p, tests, await run(src, p.fn, tests))).toMatchObject({ kind: 'ac' });
  }, 60_000);
});
