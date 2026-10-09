import { getEngine } from '../core/storage';
import type { EngineResult, Lang, Problem, Status, TestCase } from '../types';
import { runJS } from './js';
import { runJudge0 } from './judge0';
import { runPython } from './python';

export { ensurePython } from './python';

/** Run `code` against `tests` with the engine that belongs to the language. */
export function runEngine(lang: Lang, p: Problem, code: string, tests: TestCase[], onStatus: Status): Promise<EngineResult> {
  if (lang === 'javascript') return runJS(p, code, tests);
  if (lang === 'python') return runPython(p, code, tests, onStatus);
  return runJudge0(lang, p, code, tests, getEngine(), onStatus);
}
