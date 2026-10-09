/* Runs JavaScript solutions. This file is loaded as its own Worker script, so the visitor's code never runs on the
   page itself, and an infinite loop can be stopped by terminating the worker. */
import type { JsRunRequest, JsWorkerMessage } from './messages';

const ctx = self as unknown as {
  onmessage: ((e: MessageEvent<JsRunRequest>) => void) | null;
  postMessage(m: JsWorkerMessage): void;
};

const show = (v: unknown): string => {
  if (typeof v === 'string') return v;
  try {
    return JSON.stringify(v);
  } catch {
    return String(v);
  }
};

ctx.onmessage = (e) => {
  const { code, fn, tests } = e.data;
  let logs: string[] = [];
  const log = (...a: unknown[]) => {
    logs.push(a.map(show).join(' '));
  };
  const fakeConsole = { log, info: log, warn: log, error: log, debug: log };

  let f: ((...a: unknown[]) => unknown) | null;
  try {
    f = new Function('console', `${code}\n;return (typeof ${fn} === "function") ? ${fn} : null;`)(fakeConsole);
  } catch (err) {
    const er = err as Error;
    ctx.postMessage({ type: 'compile_error', message: `${er.name}: ${er.message}` });
    return;
  }
  if (!f) {
    ctx.postMessage({ type: 'compile_error', message: `Function "${fn}" is not defined. Keep the function name exactly as given.` });
    return;
  }

  for (let i = 0; i < tests.length; i++) {
    logs = [];
    const t0 = performance.now();
    try {
      const r = f(...(tests[i] as unknown[]));
      const ms = performance.now() - t0;
      if (r === undefined) {
        ctx.postMessage({ type: 'case', i, ok: false, error: 'Your function returned undefined. Did you forget a return statement?', stdout: logs.join('\n'), ms });
        break;
      }
      ctx.postMessage({ type: 'case', i, ok: true, value: JSON.parse(JSON.stringify(r)), stdout: logs.join('\n').slice(0, 4000), ms });
    } catch (err) {
      const er = err as Error | undefined;
      const msg = (er && er.name ? er.name + ': ' : '') + (er && er.message ? er.message : String(err));
      ctx.postMessage({ type: 'case', i, ok: false, error: msg, stdout: logs.join('\n').slice(0, 4000), ms: 0 });
      break;
    }
  }
  ctx.postMessage({ type: 'done' });
};
