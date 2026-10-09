import { readFileSync } from 'node:fs';
import { describe, expect, it } from 'vitest';
import { BY_ID, loadTests } from '../src/data';
import { makeVerdict } from '../src/core/verdict';
import { b64, runJudge0, shiftLines, unb64 } from '../src/engines/judge0';
import { starter } from '../src/core/languages';
import { fakeFetch, hasToolchain } from './helpers/fakeJudge0';

const cfg = { url: 'https://judge.test', token: '' };
const deps = { fetch: fakeFetch, pollDelay: () => 0 };
const noStatus = () => {};
const SOLVED = ['two-sum', 'valid-parentheses', 'merge-intervals', 'subsets', 'number-of-islands', 'minimum-window-substring'];

describe('helpers', () => {
  it('base64 round-trips unicode', () => {
    expect(unb64(b64('héllo "x"\n日本'))).toBe('héllo "x"\n日本');
  });
  it('maps compiler line numbers back to the visitor code', () => {
    expect(shiftLines('main.cpp:7:3: error: x', 3)).toBe('line 4: error: x');
    expect(shiftLines('Main.java:5: error: y', 3)).toBe('line 2: error: y');
    expect(shiftLines('main.cpp:7:3: error\n    7 |   bad;', 3)).toBe('line 4: error\n    4 |   bad;');
  });
});

describe('error paths', () => {
  const p = BY_ID.get('two-sum')!;
  const tests = [{ args: [[2, 7], 9], expected: [0, 1] }];
  it('reports an unreachable server', async () => {
    const r = await runJudge0('cpp', p, 'x', tests, cfg, noStatus, { fetch: () => Promise.reject(new Error('net')), pollDelay: () => 0 });
    expect(r).toMatchObject({ status: 'engine_error' });
  });
  it('reports an HTTP error', async () => {
    const r = await runJudge0('cpp', p, 'x', tests, cfg, noStatus, { fetch: async () => new Response('slow down', { status: 429 }), pollDelay: () => 0 });
    expect(r).toMatchObject({ status: 'engine_error', message: expect.stringContaining('429') });
  });
  it('sends the auth token only when one is set', async () => {
    let seen: Record<string, string> = {};
    const f: typeof fetch = async (_u, init) => {
      seen = init?.headers as Record<string, string>;
      return new Response('{}', { status: 500 });
    };
    await runJudge0('cpp', p, 'x', tests, { ...cfg, token: 'secret' }, noStatus, { fetch: f, pollDelay: () => 0 });
    expect(seen['X-Auth-Token']).toBe('secret');
    await runJudge0('cpp', p, 'x', tests, cfg, noStatus, { fetch: f, pollDelay: () => 0 });
    expect(seen['X-Auth-Token']).toBeUndefined();
  });
});

describe.skipIf(!hasToolchain.cpp || !hasToolchain.java)('real compilers behind a fake Judge0', () => {
  for (const lang of ['cpp', 'java'] as const) {
    const ext = lang === 'cpp' ? 'cpp' : 'java';
    it(`${lang}: accepts correct solutions on every test of ${SOLVED.length} problems`, async () => {
      for (const id of SOLVED) {
        const p = BY_ID.get(id)!;
        const code = readFileSync(new URL(`./fixtures/${id}.${ext}`, import.meta.url), 'utf8');
        const tests = await loadTests(id);
        const eng = await runJudge0(lang, p, code, tests, cfg, noStatus, deps);
        const v = makeVerdict(p, tests, eng);
        expect(v, `${lang} ${id}`).toMatchObject({ kind: 'ac', passed: tests.length });
      }
    }, 240_000);

    it(`${lang}: reports a wrong answer`, async () => {
      const p = BY_ID.get('two-sum')!;
      const code = starter(p, lang).replace(
        '// Write your solution here',
        lang === 'cpp' ? 'return {0, 0};' : 'return new int[]{0, 0};',
      );
      const tests = (await loadTests('two-sum')).slice(0, 3);
      const v = makeVerdict(p, tests, await runJudge0(lang, p, code, tests, cfg, noStatus, deps));
      expect(v).toMatchObject({ kind: 'wa', failIndex: 0, actual: [0, 0] });
    }, 60_000);

    it(`${lang}: reports a compile error with the visitor's line number`, async () => {
      const p = BY_ID.get('two-sum')!;
      const code = starter(p, lang).replace('// Write your solution here', 'this is not valid code;');
      const tests = (await loadTests('two-sum')).slice(0, 3);
      const v = makeVerdict(p, tests, await runJudge0(lang, p, code, tests, cfg, noStatus, deps));
      expect(v.kind).toBe('ce');
      if (v.kind === 'ce') expect(v.message).toMatch(lang === 'cpp' ? /line 4/ : /line 3/);
    }, 60_000);
  }

  it('reports a crash as a runtime error', async () => {
    const p = BY_ID.get('two-sum')!;
    const code = starter(p, 'cpp').replace('// Write your solution here', 'vector<int> v; v.at(5); return v;');
    const tests = (await loadTests('two-sum')).slice(0, 3);
    const v = makeVerdict(p, tests, await runJudge0('cpp', p, code, tests, cfg, noStatus, deps));
    expect(v.kind).toBe('re');
  }, 60_000);
});
