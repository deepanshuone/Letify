import { useState } from 'react';
import { TYPE } from '../core/languages';
import type { Problem } from '../types';
import { Rich, fmtVal } from './common';
import { useToast } from '../state/toast';

export function Description({ p }: { p: Problem }) {
  const modeNote = p.cmp === 'flat' ? 'The order of the returned values does not matter.' : p.cmp === 'rows' ? 'The order of the lists, and of the numbers inside each list, does not matter.' : '';
  return (
    <>
      <Rich html={p.desc} />
      {p.samples.slice(0, 2).map((t, i) => (
        <div className="ex" key={i}>
          <div className="ex-h">Example {i + 1}</div>
          <pre className="block">
            {p.params.map((x, k) => (
              <span key={k}>
                <span className="k">{x[0]} =</span> {fmtVal(t.args[k])}
                {'\n'}
              </span>
            ))}
            <span className="k">output:</span> {fmtVal(t.expected)}
          </pre>
        </div>
      ))}
      <h2>Constraints</h2>
      <ul>
        {p.constraints.map((c, i) => (
          <Rich key={i} as="li" html={c} />
        ))}
      </ul>
      {modeNote && <p className="note">{modeNote}</p>}
      <h2>Function to complete</h2>
      <p>
        <code>
          {p.fn}({p.params.map((x) => `${x[0]}: ${TYPE.py[x[1]]}`).join(', ')}) -&gt; {TYPE.py[p.ret]}
        </code>
      </p>
    </>
  );
}

export function Hints({ p, shown, onMore }: { p: Problem; shown: number; onMore(): void }) {
  return (
    <>
      <p className="muted">Try the problem for a few minutes first. Reveal one hint at a time, starting with the gentlest.</p>
      {p.hints.slice(0, shown).map((h, i) => (
        <div className="hint" key={i}>
          <b>
            Hint {i + 1} of {p.hints.length}
          </b>
          <Rich html={h} />
        </div>
      ))}
      {shown < p.hints.length ? (
        <button className="btn" onClick={onMore}>
          Show hint {shown + 1}
        </button>
      ) : (
        <p className="note">That is every hint. The editorial explains the full approach.</p>
      )}
    </>
  );
}

export function Editorial({ p }: { p: Problem }) {
  const [open, setOpen] = useState(false);
  const toast = useToast();
  const copy = async () => {
    try {
      await navigator.clipboard.writeText(p.solution);
      toast('Solution copied');
    } catch {
      toast('Select the code and press Ctrl/Cmd + C to copy');
    }
  };
  return (
    <>
      <p className="muted">Read this after you have tried the problem, or when you are stuck for good.</p>
      {open ? (
        <div>
          {p.editorial.map((t, i) => (
            <Rich key={i} as="p" html={t} />
          ))}
          <div className="cx">
            <span className="chip big">Time {p.time}</span>
            <span className="chip big">Space {p.space}</span>
          </div>
          <h2>Reference solution (Python)</h2>
          <pre className="block">{p.solution}</pre>
          <p style={{ marginTop: 10 }}>
            <button className="btn sm" onClick={copy}>
              Copy solution
            </button>
          </p>
        </div>
      ) : (
        <button className="btn" onClick={() => setOpen(true)}>
          Show editorial and solution
        </button>
      )}
    </>
  );
}
