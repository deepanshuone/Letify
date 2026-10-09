export type PType = 'int' | 'bool' | 'string' | 'int[]' | 'int[][]';
export type Cmp = 'exact' | 'flat' | 'rows';
export type Diff = 'Easy' | 'Medium' | 'Hard';
export type Lang = 'python' | 'javascript' | 'cpp' | 'java';

export type Value = number | boolean | string | number[] | number[][];

export interface TestCase {
  args: Value[];
  expected: Value;
}

export interface Problem {
  id: string;
  title: string;
  diff: Diff;
  topic: string;
  fn: string;
  params: [string, PType][];
  ret: PType;
  cmp: Cmp;
  /** Trusted HTML from data/problems.py (the build only allows plain formatting tags). */
  desc: string;
  constraints: string[];
  hints: string[];
  editorial: string[];
  time: string;
  space: string;
  /** Reference solution, Python. */
  solution: string;
  /** Number of cases Run uses (the first `visible` cases). */
  visible: number;
  testCount: number;
  samples: TestCase[];
}

/** What an engine reports for one test case. */
export interface CaseResult {
  ok: boolean;
  value?: unknown;
  error?: string;
  ms?: number;
  stdout?: string;
}

export type EngineResult =
  | { status: 'compile_error'; message: string }
  | { status: 'engine_error'; message: string }
  | {
      status: 'ok';
      cases: (CaseResult | undefined)[];
      timedOut?: boolean;
      fatal?: string;
      ms?: number;
      stdout?: string;
    };

export type Verdict =
  | { kind: 'ac'; passed: number; total: number; ms: number; stdout: string }
  | { kind: 'wa'; failIndex: number; passed: number; total: number; ms: number; actual: unknown; stdout: string }
  | { kind: 're'; failIndex: number; passed: number; total: number; ms: number; message: string; stdout: string }
  | { kind: 'tle'; failIndex: number; passed: number; total: number; ms: number; stdout: string }
  | { kind: 'ce'; message: string; total: number; passed: number }
  | { kind: 'engine'; message: string; total: number; passed: number };

export type Status = (text: string) => void;
