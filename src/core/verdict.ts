import type { Cmp, EngineResult, Problem, TestCase, Verdict } from '../types';

function lexCmp(a: number[], b: number[]): number {
  const n = Math.min(a.length, b.length);
  for (let i = 0; i < n; i++) {
    if (a[i] !== b[i]) return a[i]! - b[i]!;
  }
  return a.length - b.length;
}

const numAsc = (a: number, b: number) => a - b;

/** Put a result in the form used for comparison, according to the problem's compare mode. */
export function canon(v: unknown, mode: Cmp): unknown {
  if (mode === 'flat' && Array.isArray(v)) return (v as number[]).slice().sort(numAsc);
  if (mode === 'rows' && Array.isArray(v) && v.every(Array.isArray)) {
    return (v as number[][]).map((r) => r.slice().sort(numAsc)).sort(lexCmp);
  }
  return v;
}

export function sameResult(a: unknown, b: unknown, mode: Cmp): boolean {
  return JSON.stringify(canon(a, mode)) === JSON.stringify(canon(b, mode));
}

/** Turn an engine report into a verdict for the tests that were sent. */
export function makeVerdict(p: Pick<Problem, 'cmp'>, tests: TestCase[], eng: EngineResult): Verdict {
  const total = tests.length;
  if (eng.status === 'compile_error') return { kind: 'ce', message: eng.message, total, passed: 0 };
  if (eng.status === 'engine_error') return { kind: 'engine', message: eng.message, total, passed: 0 };
  let passed = 0;
  let ms = 0;
  const base = eng.stdout ?? '';
  for (let i = 0; i < total; i++) {
    const c = eng.cases[i];
    if (!c) {
      if (eng.timedOut) return { kind: 'tle', failIndex: i, passed, total, ms, stdout: base };
      if (eng.fatal) return { kind: 're', failIndex: i, passed, total, ms, message: eng.fatal, stdout: base };
      return { kind: 'engine', message: 'The runner stopped before every test case finished. Try again.', total, passed };
    }
    ms += c.ms ?? 0;
    if (!c.ok) {
      return { kind: 're', failIndex: i, passed, total, ms, message: c.error ?? 'Runtime error', stdout: c.stdout || base };
    }
    if (!sameResult(c.value, tests[i]!.expected, p.cmp)) {
      return { kind: 'wa', failIndex: i, passed, total, ms, actual: c.value, stdout: c.stdout || base };
    }
    passed++;
  }
  return { kind: 'ac', passed, total, ms: eng.ms || ms, stdout: base };
}
