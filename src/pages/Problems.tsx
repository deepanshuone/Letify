import { useEffect } from 'react';
import { CheckIcon, Link, Pill } from '../components/common';
import { PROBLEMS, TOPICS } from '../data';
import { navigate } from '../router';
import { useFilters, type Filters } from '../state/filters';
import { useProgress } from '../state/progress';
import { STAGES } from './stages';

const DIFFS: Filters['diff'][] = ['All', 'Easy', 'Medium', 'Hard'];
const STATUSES: Filters['status'][] = ['All', 'Todo', 'Solved'];

export function Problems() {
  const { filters: f, setFilters } = useFilters();
  const { solved } = useProgress();
  const done = PROBLEMS.filter((p) => solved[p.id]).length;
  const next = PROBLEMS.find((p) => !solved[p.id]);
  const q = f.q.trim().toLowerCase();

  const list = PROBLEMS.filter((p) => {
    if (f.diff !== 'All' && p.diff !== f.diff) return false;
    if (f.topic !== 'All' && p.topic !== f.topic) return false;
    if (f.status === 'Solved' && !solved[p.id]) return false;
    if (f.status === 'Todo' && solved[p.id]) return false;
    if (q && !`${p.title} ${p.topic}`.toLowerCase().includes(q)) return false;
    return true;
  });

  useEffect(() => {
    document.title = 'Problems · Letify';
  }, []);

  return (
    <>
      <section className="intro compact">
        <h1>Problems</h1>
        <p className="lede">{PROBLEMS.length} problems in three stages. Pick a stage, filter by topic, or continue where you left off.</p>
        <div className="intro-actions">
          {next ? (
            <button className="btn primary" onClick={() => navigate({ name: 'problem', id: next.id })}>
              {done ? 'Continue with ' : 'Start with '}
              {next.title}
            </button>
          ) : (
            <span className="solved-badge">Everything solved. Nice work.</span>
          )}
          <span className="muted" style={{ fontSize: '.88rem' }}>
            Progress and code are saved in this browser.
          </span>
        </div>
      </section>

      <section className="stages" aria-label="Stages">
        {STAGES.map((s) => {
          const inStage = PROBLEMS.filter((p) => p.diff === s.diff);
          const n = inStage.filter((p) => solved[p.id]).length;
          const on = f.diff === s.diff;
          return (
            <button
              key={s.diff}
              className={`stage${on ? ' on' : ''}`}
              aria-pressed={on}
              onClick={() => {
                setFilters({ diff: on ? 'All' : s.diff });
                document.getElementById('rows')?.scrollIntoView({ behavior: 'smooth', block: 'start' });
              }}
            >
              <h3>{s.name}</h3>
              <div className="sub">{s.blurb}</div>
              <div className="meta tnum">
                <span>
                  {s.diff} &middot; {inStage.length} problems
                </span>
                <span>{n} solved</span>
              </div>
              <div className="bar">
                <i style={{ width: `${inStage.length ? Math.round((100 * n) / inStage.length) : 0}%` }} />
              </div>
            </button>
          );
        })}
      </section>

      <section aria-label="Problem list">
        <div className="filters">
          <input type="search" placeholder="Search problems" aria-label="Search problems" value={f.q} onChange={(e) => setFilters({ q: e.target.value })} />
          <div className="seg">
            {DIFFS.map((d) => (
              <button key={d} aria-pressed={f.diff === d} onClick={() => setFilters({ diff: d })}>
                {d}
              </button>
            ))}
          </div>
          <select aria-label="Topic" value={f.topic} onChange={(e) => setFilters({ topic: e.target.value })}>
            <option>All</option>
            {TOPICS.map((t) => (
              <option key={t}>{t}</option>
            ))}
          </select>
          <select aria-label="Status" value={f.status} onChange={(e) => setFilters({ status: e.target.value as Filters['status'] })}>
            {STATUSES.map((t) => (
              <option key={t}>{t}</option>
            ))}
          </select>
        </div>
        <div className="table" id="rows">
          <div className="row head">
            <span />
            <span>Problem</span>
            <span className="topic">Topic</span>
            <span>Level</span>
          </div>
          {list.length === 0 && <div className="empty">No problems match these filters.</div>}
          {list.map((p) => {
            const isDone = !!solved[p.id];
            return (
              <Link key={p.id} className="row" to={{ name: 'problem', id: p.id }}>
                <span className={`dot${isDone ? ' done' : ''}`} title={isDone ? 'Solved' : 'Not solved yet'}>
                  {isDone && <CheckIcon />}
                </span>
                <span className="t">
                  <b>
                    {PROBLEMS.indexOf(p) + 1}. {p.title}
                  </b>
                  <small>
                    {p.fn}({p.params.map((x) => x[0]).join(', ')})
                  </small>
                </span>
                <span className="topic muted">{p.topic}</span>
                <span>
                  <Pill diff={p.diff} />
                </span>
              </Link>
            );
          })}
        </div>
      </section>
      <footer className="foot">Python and JavaScript run inside your browser. C++ and Java are compiled on a Judge0 server, which you can change in Engine settings on any problem.</footer>
    </>
  );
}
