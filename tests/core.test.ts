import { describe, expect, it } from 'vitest';
import { PROBLEMS, BY_ID, loadTests } from '../src/data';
import { buildStdin, cppProgram, fmtArg, javaProgram, MARK } from '../src/core/drivers';
import { tokenize } from '../src/core/highlight';
import { LANG_IDS, starter } from '../src/core/languages';
import { canon, makeVerdict, sameResult } from '../src/core/verdict';
import type { EngineResult, TestCase } from '../src/types';

const two = BY_ID.get('two-sum')!;

describe('problem data', () => {
  it('has unique ids, sensible sizes and a test file for each problem', async () => {
    expect(new Set(PROBLEMS.map((p) => p.id)).size).toBe(PROBLEMS.length);
    for (const p of PROBLEMS) {
      const tests = await loadTests(p.id);
      expect(tests.length, p.id).toBe(p.testCount);
      expect(p.samples, p.id).toEqual(tests.slice(0, p.visible));
      expect(tests.length, p.id).toBeGreaterThan(p.visible);
      for (const t of tests) expect(t.args.length, p.id).toBe(p.params.length);
      expect(p.hints.length, p.id).toBe(3);
    }
  }, 120_000);
  it('rejects an unknown problem', async () => {
    await expect(loadTests('nope')).rejects.toThrow();
  });
});

describe('starter code', () => {
  it('matches the function signature in every language', () => {
    expect(starter(two, 'python')).toContain('def twoSum(nums: list[int], target: int) -> list[int]:');
    expect(starter(two, 'javascript')).toContain('function twoSum(nums, target) {');
    expect(starter(two, 'javascript')).toContain('@param {number[]} nums');
    expect(starter(two, 'cpp')).toContain('vector<int> twoSum(vector<int>& nums, int target)');
    expect(starter(two, 'java')).toContain('public int[] twoSum(int[] nums, int target)');
  });
  it('exists for every problem and language', () => {
    for (const p of PROBLEMS) for (const l of LANG_IDS) expect(starter(p, l).length).toBeGreaterThan(20);
  });
});

describe('stdin format', () => {
  it('encodes each type', () => {
    expect(fmtArg(5, 'int')).toBe('5');
    expect(fmtArg(true, 'bool')).toBe('1');
    expect(fmtArg(false, 'bool')).toBe('0');
    expect(fmtArg('', 'string')).toBe('""');
    expect(fmtArg('abc', 'string')).toBe('abc');
    expect(fmtArg([], 'int[]')).toBe('0');
    expect(fmtArg([3, -1], 'int[]')).toBe('2 3 -1');
    expect(fmtArg([[1, 2], [], [3]], 'int[][]')).toBe('3\n2 1 2\n0\n1 3');
  });
  it('starts with the number of tests', () => {
    const s = buildStdin(two, [{ args: [[2, 7], 9] }]);
    expect(s).toBe('1\n2 2 7\n9\n');
  });
  it('builds a C++ and a Java program that call the right function', () => {
    expect(cppProgram(two, 'class Solution {};')).toContain('Solution().twoSum(p0, p1)');
    expect(javaProgram(two, 'class Solution {}')).toContain('new Solution().twoSum(p0, p1)');
    expect(cppProgram(two, 'X').split('\n').slice(0, 3).join('\n')).toBe('#include <bits/stdc++.h>\nusing namespace std;\n');
    expect(cppProgram(two, 'X')).toContain(MARK);
  });
});

describe('comparison', () => {
  it('canonicalises by mode', () => {
    expect(canon([3, 1, 2], 'flat')).toEqual([1, 2, 3]);
    expect(canon([[2, 1], [0, 5]], 'rows')).toEqual([[0, 5], [1, 2]]);
    expect(canon([3, 1, 2], 'exact')).toEqual([3, 1, 2]);
    expect(sameResult([2, 1], [1, 2], 'flat')).toBe(true);
    expect(sameResult([2, 1], [1, 2], 'exact')).toBe(false);
    expect(sameResult([[3, 2], [1]], [[1], [2, 3]], 'rows')).toBe(true);
    expect(sameResult('x', 'x', 'rows')).toBe(true);
    expect(sameResult([[2, 1], [1, 2]], [[1, 2], [2, 1]], 'rowset')).toBe(true);
    expect(sameResult([[1, 2], [1, 2]], [[1, 2], [2, 1]], 'rowset')).toBe(false);
  });
});

describe('verdicts', () => {
  const tests: TestCase[] = [1, 2, 3].map((n) => ({ args: [n], expected: n * 2 }));
  const p = { cmp: 'exact' } as const;
  const ok = (v: number) => ({ ok: true, value: v, ms: 1 });
  const run = (e: EngineResult) => makeVerdict(p, tests, e);

  it('accepts when every case matches', () => {
    expect(run({ status: 'ok', cases: [ok(2), ok(4), ok(6)] })).toMatchObject({ kind: 'ac', passed: 3, total: 3 });
  });
  it('reports the first wrong answer', () => {
    expect(run({ status: 'ok', cases: [ok(2), ok(5), ok(6)] })).toMatchObject({ kind: 'wa', failIndex: 1, passed: 1, actual: 5 });
  });
  it('reports a runtime error from a case', () => {
    expect(run({ status: 'ok', cases: [ok(2), { ok: false, error: 'boom' }] })).toMatchObject({ kind: 're', failIndex: 1, message: 'boom' });
  });
  it('reports a time limit when cases are missing and the engine timed out', () => {
    expect(run({ status: 'ok', cases: [ok(2)], timedOut: true })).toMatchObject({ kind: 'tle', failIndex: 1, passed: 1 });
  });
  it('reports a fatal error when cases are missing', () => {
    expect(run({ status: 'ok', cases: [], fatal: 'Segfault' })).toMatchObject({ kind: 're', failIndex: 0, message: 'Segfault' });
  });
  it('reports an engine problem when cases are missing without a reason', () => {
    expect(run({ status: 'ok', cases: [ok(2)] }).kind).toBe('engine');
  });
  it('passes compile and engine errors through', () => {
    expect(run({ status: 'compile_error', message: 'x' })).toMatchObject({ kind: 'ce', message: 'x' });
    expect(run({ status: 'engine_error', message: 'y' })).toMatchObject({ kind: 'engine', message: 'y' });
  });
});

describe('highlighter', () => {
  it('never loses or changes text, for every reference solution and language', () => {
    for (const p of PROBLEMS) {
      for (const lang of LANG_IDS) {
        const code = lang === 'python' ? p.solution : starter(p, lang) + '\n// note "unterminated\n/* open';
        expect(tokenize(code, lang).map((t) => t.text).join(''), `${p.id} ${lang}`).toBe(code);
      }
    }
  });
  it('colours keywords, strings, numbers, comments and calls', () => {
    const t = tokenize('def f(x):  # hi\n    return "a" + 42', 'python');
    const cls = (text: string) => t.find((x) => x.text === text)?.cls;
    expect(cls('def')).toBe('kw');
    expect(cls('f')).toBe('fn');
    expect(cls('# hi')).toBe('com');
    expect(cls('"a"')).toBe('str');
    expect(cls('42')).toBe('num');
  });
  it('handles C++ preprocessor lines and JavaScript template strings', () => {
    expect(tokenize('#include <x>\nint a;', 'cpp')[0]).toMatchObject({ cls: 'com' });
    expect(tokenize('const s = `a${b}c`;', 'javascript').some((x) => x.cls === 'str' && x.text.startsWith('`'))).toBe(true);
  });
});
