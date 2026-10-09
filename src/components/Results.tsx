import { useState } from 'react';
import { PROBLEMS } from '../data';
import type { Lang, Problem, TestCase, Verdict } from '../types';
import { Link, fmtVal, short } from './common';

export type RunState =
  | { kind: 'empty' }
  | { kind: 'busy'; text: string }
  | { kind: 'done'; id: number; verdict: Verdict; tests: TestCase[]; mode: 'run' | 'submit'; lang: Lang };

export function Results({ p, state, onSeeEditorial }: { p: Problem; state: RunState; onSeeEditorial(): void }) {
  return (
    <div className="results" aria-live="polite">
      {state.kind === 'empty' && (
        <div className="res-empty">
          Run checks the {p.visible} sample cases. Submit checks all {p.testCount} cases, including hidden and large ones. Shortcuts: <kbd>Ctrl</kbd> + <kbd>Enter</kbd> to run, add <kbd>Shift</kbd> to submit.
        </div>
      )}
      {state.kind === 'busy' && (
        <div className="res-empty">
          <span className="spin" />
          {state.text}
        </div>
      )}
      {state.kind === 'done' && <Done key={state.id} p={p} state={state} onSeeEditorial={onSeeEditorial} />}
    </div>
  );
}

const TITLES = { ac: 'Accepted', wa: 'Wrong Answer', re: 'Runtime Error', tle: 'Time Limit Exceeded', engine: 'Could not run' } as const;

function Done({ p, state, onSeeEditorial }: { p: Problem; state: Extract<RunState, { kind: 'done' }>; onSeeEditorial(): void }) {
  const { verdict: v, tests, mode, lang } = state;
  const [detail, setDetail] = useState(() => ('failIndex' in v ? v.failIndex : 0));

  const title = v.kind === 'ce' ? (lang === 'python' || lang === 'javascript' ? 'Error in your code' : 'Compile Error') : TITLES[v.kind];
  const cls = v.kind === 'ac' ? 'ac' : v.kind === 'engine' || v.kind === 'tle' ? 'warn' : 'bad';

  let sub = '';
  if (v.kind === 'ac') sub = `${v.passed} of ${v.total}${mode === 'run' ? ' sample cases passed' : ' test cases passed'}${v.ms ? ` · ${Math.max(1, Math.round(v.ms))} ms` : ''}`;
  else if ('failIndex' in v) sub = `${v.passed} of ${v.total} passed · stopped at case ${v.failIndex + 1}`;

  const head = (
    <div className={`verdict ${cls}`}>
      <h3>{title}</h3>
      <span className="muted tnum">{sub}</span>
    </div>
  );

  if (v.kind === 'ce' || v.kind === 'engine') {
    return (
      <>
        {head}
        <pre className="block">{v.message}</pre>
      </>
    );
  }

  const failIndex = 'failIndex' in v ? v.failIndex : -1;
  const idx = PROBLEMS.indexOf(p);
  const nx = PROBLEMS[idx + 1];

  return (
    <>
      {head}
      <div className="cases" role="group" aria-label="Test cases">
        {tests.map((_, i) => {
          const st = v.kind === 'ac' ? 'pass' : i < failIndex ? 'pass' : i === failIndex ? 'fail' : 'skip';
          return (
            <button key={i} className={st} aria-pressed={i === detail} aria-label={`Case ${i + 1}${st === 'pass' ? ' passed' : st === 'fail' ? ' failed' : ' not run'}`} onClick={() => setDetail(i)}>
              {i + 1}
            </button>
          );
        })}
      </div>
      <Detail p={p} v={v} tests={tests} mode={mode} i={detail} />
      {v.kind === 'ac' && mode === 'submit' && (
        <p style={{ marginTop: 12 }}>
          {nx && (
            <>
              <Link className="btn sm primary" to={{ name: 'problem', id: nx.id }}>
                Next: {nx.title}
              </Link>{' '}
            </>
          )}
          <button className="btn sm" onClick={onSeeEditorial}>
            See the editorial
          </button>
        </p>
      )}
    </>
  );
}

function Detail({ p, v, tests, mode, i }: { p: Problem; v: Exclude<Verdict, { kind: 'ce' | 'engine' }>; tests: TestCase[]; mode: 'run' | 'submit'; i: number }) {
  const t = tests[i];
  if (!t) return null;
  const failIndex = 'failIndex' in v ? v.failIndex : -1;
  const failing = i === failIndex;
  const hidden = mode === 'submit' && i >= p.visible && !failing;
  if (hidden) {
    return <p className="muted">Case {i + 1} is a hidden test case{v.kind === 'ac' || i < failIndex ? ' and your solution passed it.' : ' and was not run.'}</p>;
  }
  if (!failing && v.kind !== 'ac' && i > failIndex) return <p className="muted">Not run, because an earlier case failed.</p>;

  const input = p.params.map((x, k) => `${x[0]} = ${fmtVal(t.args[k])}`).join('\n');
  return (
    <div className="kv">
      <div className="lab">Input</div>
      <pre className="block">{input}</pre>
      {failing && v.kind === 'wa' && (
        <>
          <div className="lab">Your output</div>
          <pre className="block">{fmtVal(v.actual)}</pre>
        </>
      )}
      {failing && v.kind === 're' && (
        <>
          <div className="lab">Error</div>
          <pre className="block">{v.message}</pre>
        </>
      )}
      {failing && v.kind === 'tle' && <p className="note">This case did not finish in time. Your approach is likely too slow for the input size. The hints and editorial describe a faster idea.</p>}
      {v.kind !== 'tle' && (
        <>
          <div className="lab">Expected output</div>
          <pre className="block">{fmtVal(t.expected)}</pre>
        </>
      )}
      {failing && 'stdout' in v && v.stdout && (
        <>
          <div className="lab">Your printed output</div>
          <pre className="block">{short(v.stdout, 1500)}</pre>
        </>
      )}
    </div>
  );
}
