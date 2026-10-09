import harness from './harness.py?raw';
import { PY_LIMIT_MS, pyodideUrl } from '../config';
import type { CaseResult, EngineResult, Problem, Status, TestCase } from '../types';
import type { PyRequest, PyWorkerMessage } from './messages';

const LOAD_LIMIT_MS = 120_000;

let worker: Worker | null = null;
let ready: Promise<Worker> | null = null;
let loaded = false;

function reset(): void {
  try {
    worker?.terminate();
  } catch {
    /* already gone */
  }
  worker = null;
  ready = null;
  loaded = false;
}

/** Start loading the Python runtime (about 10 MB, cached by the browser after the first time). */
export function ensurePython(): Promise<Worker> {
  if (ready) return ready;
  ready = new Promise<Worker>((resolve, reject) => {
    let w: Worker;
    try {
      w = new Worker(new URL('./pyWorker.ts', import.meta.url), { type: 'module' });
    } catch (err) {
      ready = null;
      reject(err);
      return;
    }
    worker = w;
    const fail = (err: Error) => {
      clearTimeout(t);
      reset();
      reject(err);
    };
    const t = setTimeout(() => fail(new Error('The Python runtime took too long to load.')), LOAD_LIMIT_MS);
    w.onmessage = (e: MessageEvent<PyWorkerMessage>) => {
      if (e.data.type === 'ready') {
        clearTimeout(t);
        loaded = true;
        resolve(w);
      } else if (e.data.type === 'init_error') fail(new Error(e.data.message));
    };
    w.onerror = (e) => fail(new Error(e.message || 'The worker failed to start.'));
    const req: PyRequest = { type: 'init', indexURL: pyodideUrl(), harness };
    w.postMessage(req);
  });
  return ready;
}

export async function runPython(p: Pick<Problem, 'fn'>, code: string, tests: TestCase[], onStatus: Status): Promise<EngineResult> {
  let w: Worker;
  try {
    if (!loaded) onStatus('Loading the Python runtime (first run only, about 10 MB)...');
    w = await ensurePython();
  } catch (err) {
    return {
      status: 'engine_error',
      message: `The in-browser Python runtime (Pyodide) could not load: ${(err as Error).message}\nPython runs in your browser, so it has to download its runtime once. Check your connection, or try JavaScript, C++ or Java.`,
    };
  }
  onStatus('Running...');
  return new Promise<EngineResult>((resolve) => {
    const cases: (CaseResult | undefined)[] = [];
    let timer: ReturnType<typeof setTimeout> | undefined;
    const done = (r: EngineResult) => {
      clearTimeout(timer);
      w.onmessage = null;
      resolve(r);
    };
    const arm = () => {
      clearTimeout(timer);
      timer = setTimeout(() => {
        reset(); // a stuck Python cannot be interrupted, so the runtime is thrown away and loads again next time
        resolve({ status: 'ok', cases, timedOut: true });
      }, PY_LIMIT_MS);
    };
    w.onmessage = (e: MessageEvent<PyWorkerMessage>) => {
      const m = e.data;
      if (m.type === 'compile_error') done({ status: 'compile_error', message: m.message });
      else if (m.type === 'case') {
        cases[m.i] = m;
        arm();
      } else if (m.type === 'done') done({ status: 'ok', cases });
    };
    arm();
    const req: PyRequest = { type: 'run', code, fn: p.fn, tests: tests.map((t) => JSON.stringify(t.args)) };
    w.postMessage(req);
  });
}
