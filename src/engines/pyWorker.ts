/* Runs Python solutions with Pyodide (CPython compiled to WebAssembly). Loaded as its own module Worker. */
import type { PyRequest, PyWorkerMessage } from './messages';

interface PyodideLike {
  runPython(code: string): unknown;
  globals: { get(name: string): (...a: string[]) => string };
}

const ctx = self as unknown as {
  onmessage: ((e: MessageEvent<PyRequest>) => void) | null;
  postMessage(m: PyWorkerMessage): void;
};

let py: PyodideLike | null = null;

ctx.onmessage = async (e) => {
  const m = e.data;
  if (m.type === 'init') {
    try {
      // The runtime is a separate file, so it is imported by URL at run time instead of being bundled.
      const mod = (await import(/* @vite-ignore */ m.indexURL + 'pyodide.mjs')) as {
        loadPyodide(o: { indexURL: string }): Promise<PyodideLike>;
      };
      py = await mod.loadPyodide({ indexURL: m.indexURL });
      py.runPython(m.harness);
      ctx.postMessage({ type: 'ready' });
    } catch (err) {
      ctx.postMessage({ type: 'init_error', message: String((err as Error)?.message ?? err) });
    }
    return;
  }
  if (!py) {
    ctx.postMessage({ type: 'init_error', message: 'The Python runtime is not loaded yet.' });
    return;
  }
  const prep = JSON.parse(py.globals.get('_prep')(m.code, m.fn)) as { type: string; message?: string };
  if (prep.type === 'compile_error') {
    ctx.postMessage({ type: 'compile_error', message: prep.message ?? 'Error in your code' });
    return;
  }
  const run1 = py.globals.get('_run1');
  for (let i = 0; i < m.tests.length; i++) {
    const r = JSON.parse(run1(m.tests[i]!)) as { ok: boolean; value?: unknown; error?: string; ms?: number; stdout?: string };
    ctx.postMessage({ type: 'case', i, ...r });
    if (!r.ok) break;
  }
  ctx.postMessage({ type: 'done' });
};
