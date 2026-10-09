import { useState } from 'react';
import { example, parseArg } from '../core/custom';
import type { Problem, Value } from '../types';
import { fmtVal } from './common';

export type CustomResult = { kind: 'value'; value: unknown; stdout: string; ms: number } | { kind: 'error'; title: string; message: string };

/* Like the "test against custom input" box on HackerRank: run your code on any input and see what it returns. */
export function CustomInput({ p, busy, onRun }: { p: Problem; busy: boolean; onRun(args: Value[]): Promise<CustomResult> }) {
  const [texts, setTexts] = useState<string[]>(() => p.samples[0]!.args.map((a) => JSON.stringify(a)));
  const [errors, setErrors] = useState<(string | null)[]>([]);
  const [result, setResult] = useState<CustomResult | null>(null);
  const [running, setRunning] = useState(false);

  const run = async () => {
    const parsed = p.params.map(([, t], i) => parseArg(texts[i] ?? '', t));
    const errs = parsed.map((r) => (r.ok ? null : r.error));
    setErrors(errs);
    if (errs.some(Boolean)) return;
    setRunning(true);
    setResult(null);
    try {
      setResult(await onRun(parsed.map((r) => (r as { ok: true; value: Value }).value)));
    } finally {
      setRunning(false);
    }
  };

  return (
    <div className="custom">
      <p className="muted" style={{ marginTop: 0 }}>
        Type one JSON value per argument and run your code on it. No expected answer is checked.
      </p>
      {p.params.map(([name, type], i) => (
        <label key={name} className="custom-field">
          <span>
            <code>{name}</code> <span className="muted">({type}), e.g. {example(type)}</span>
          </span>
          <textarea
            rows={type === 'int[][]' ? 3 : 2}
            spellCheck={false}
            value={texts[i] ?? ''}
            aria-invalid={!!errors[i]}
            onChange={(e) => setTexts(texts.map((t, k) => (k === i ? e.target.value : t)))}
          />
          {errors[i] && (
            <span className="field-error" role="alert">
              {errors[i]}
            </span>
          )}
        </label>
      ))}
      <button className="btn primary" disabled={busy || running} onClick={() => void run()}>
        {running ? 'Running...' : 'Run on this input'}
      </button>
      {result?.kind === 'value' && (
        <div className="kv" style={{ marginTop: 12 }}>
          <div className="lab">Your output</div>
          <pre className="block">{fmtVal(result.value)}</pre>
          {result.stdout && (
            <>
              <div className="lab">Your printed output</div>
              <pre className="block">{result.stdout}</pre>
            </>
          )}
        </div>
      )}
      {result?.kind === 'error' && (
        <div className="kv" style={{ marginTop: 12 }}>
          <div className="lab">{result.title}</div>
          <pre className="block">{result.message}</pre>
        </div>
      )}
    </div>
  );
}
