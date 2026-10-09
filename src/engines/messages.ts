import type { CaseResult } from '../types';

/* Messages between the page and the code-running Web Workers. */

export interface JsRunRequest {
  code: string;
  fn: string;
  tests: unknown[][];
}

export type JsWorkerMessage =
  | { type: 'compile_error'; message: string }
  | ({ type: 'case'; i: number } & CaseResult)
  | { type: 'done' };

export type PyRequest =
  | { type: 'init'; indexURL: string; harness: string }
  | { type: 'run'; code: string; fn: string; tests: string[] };

export type PyWorkerMessage =
  | { type: 'ready' }
  | { type: 'init_error'; message: string }
  | { type: 'compile_error'; message: string }
  | ({ type: 'case'; i: number } & CaseResult)
  | { type: 'done' };
