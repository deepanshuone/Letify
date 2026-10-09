import { JS_LIMIT_MS } from '../config';
import type { CaseResult, EngineResult, Problem, TestCase } from '../types';
import type { JsRunRequest, JsWorkerMessage } from './messages';

/** Run a JavaScript solution in a throw-away Web Worker. The worker is killed when it finishes or runs too long. */
export function runJS(p: Pick<Problem, 'fn'>, code: string, tests: TestCase[]): Promise<EngineResult> {
  return new Promise((resolve) => {
    let w: Worker;
    try {
      w = new Worker(new URL('./jsWorker.ts', import.meta.url), { type: 'module' });
    } catch (err) {
      resolve({ status: 'engine_error', message: `This browser could not start a Web Worker: ${(err as Error).message}` });
      return;
    }
    const cases: (CaseResult | undefined)[] = [];
    let timer: ReturnType<typeof setTimeout> | undefined;
    const end = (r: EngineResult) => {
      clearTimeout(timer);
      w.terminate();
      resolve(r);
    };
    // The limit applies per test case: it restarts every time a case finishes.
    const arm = () => {
      clearTimeout(timer);
      timer = setTimeout(() => end({ status: 'ok', cases, timedOut: true }), JS_LIMIT_MS);
    };
    w.onmessage = (e: MessageEvent<JsWorkerMessage>) => {
      const m = e.data;
      if (m.type === 'compile_error') end({ status: 'compile_error', message: m.message });
      else if (m.type === 'case') {
        cases[m.i] = m;
        arm();
      } else end({ status: 'ok', cases });
    };
    w.onerror = (e) => end({ status: 'compile_error', message: e.message || 'The script could not run.' });
    arm();
    const req: JsRunRequest = { code, fn: p.fn, tests: tests.map((t) => t.args) };
    w.postMessage(req);
  });
}
