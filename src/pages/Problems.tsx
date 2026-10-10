import { BRAND } from '../config';
import { Fragment, useEffect, useMemo, useRef, useState } from 'react';
import { Link } from '../components/common';
import { ProblemRow } from '../components/ProblemRow';
import { PROBLEMS, TOPICS } from '../data';
import { navigate } from '../router';
import { useFilters, type Filters } from '../state/filters';
import { useUserData } from '../state/userdata';
import type { Problem } from '../types';
import { dailyProblem, dayKey } from '../user/stats';
import { STAGES } from './stages';

const DIFFS: Filters['diff'][] = ['All', 'Easy', 'Medium', 'Hard'];
const STATUSES: Filters['status'][] = ['All', 'Todo', 'Solved', 'Starred'];
const RANK = { Easy: 0, Medium: 1, Hard: 2 } as const;
const PAGE = 60;
const MORE = 100;

const SORTS: Record<Filters['sort'], { label: string; cmp?: (a: Problem, b: Problem) => number }> = {
  roadmap: { label: 'Roadmap order' },
  easy: { label: 'Easiest first', cmp: (a, b) => RANK[a.diff] - RANK[b.diff] },
  hard: { label: 'Hardest first', cmp: (a, b) => RANK[b.diff] - RANK[a.diff] },
  title: { label: 'Title A to Z', cmp: (a, b) => a.title.localeCompare(b.title) },
};

export function Problems() {
  const { filters: f, setFilters } = useFilters();
  const { data } = useUserData();
  const { solved, stars } = data;
  const daily = useMemo(() => dailyProblem(dayKey(Date.now()), PROBLEMS), []);
  const dailyDone = !!solved[daily.id];
  const done = PROBLEMS.filter((p) => solved[p.id]).length;
  const next = PROBLEMS.find((p) => !solved[p.id]);
  const q = f.q.trim().toLowerCase();

  const numbers = useMemo(() => new Map(PROBLEMS.map((p, i) => [p.id, i + 1])), []);
  const byTopic = useMemo(() => {
    const m = new Map<string, { total: number; done: number }>();
    for (const t of TOPICS) m.set(t, { total: 0, done: 0 });
    for (const p of PROBLEMS) {
      const e = m.get(p.topic)!;
      e.total++;
      if (solved[p.id]) e.done++;
    }
    return m;
  }, [solved]);
  const mustTotal = useMemo(() => PROBLEMS.filter((p) => p.tier === 'must').length, []);
  const mustDone = PROBLEMS.filter((p) => p.tier === 'must' && solved[p.id]).length;

  const list = useMemo(() => {
    const out = PROBLEMS.filter((p) => {
      if (f.diff !== 'All' && p.diff !== f.diff) return false;
      if (f.topic !== 'All' && p.topic !== f.topic) return false;
      if (f.tier === 'must' && p.tier !== 'must') return false;
      if (f.tier === 'core' && p.tier === 'extra') return false;
      if (f.status === 'Solved' && !solved[p.id]) return false;
      if (f.status === 'Todo' && solved[p.id]) return false;
      if (f.status === 'Starred' && !stars[p.id]?.on) return false;
      if (q && !`${p.title} ${p.topic}`.toLowerCase().includes(q)) return false;
      return true;
    });
    const cmp = SORTS[f.sort].cmp;
    return cmp ? [...out].sort(cmp) : out;
  }, [f.diff, f.topic, f.tier, f.status, f.sort, q, solved, stars]);

  // Rendering is incremental so the page stays instant with thousands of problems.
  const [limit, setLimit] = useState(PAGE);
  useEffect(() => setLimit(PAGE), [f.diff, f.topic, f.tier, f.status, f.sort, q]);
  const shown = list.slice(0, limit);
  const grouped = f.sort === 'roadmap' && f.topic === 'All' && !q;
  const sentinel = useRef<HTMLDivElement>(null);
  useEffect(() => {
    const el = sentinel.current;
    if (!el || limit >= list.length || typeof IntersectionObserver === 'undefined') return;
    const io = new IntersectionObserver((e) => e[0]?.isIntersecting && setLimit((n) => n + MORE), { rootMargin: '600px' });
    io.observe(el);
    return () => io.disconnect();
  }, [limit, list.length]);

  useEffect(() => {
    document.title = `Problems · ${BRAND}`;
  }, []);

  const reset = () => setFilters({ diff: 'All', topic: 'All', status: 'All', tier: 'All', q: '' });
  const filtered = f.diff !== 'All' || f.topic !== 'All' || f.status !== 'All' || f.tier !== 'All' || !!q;

  return (
    <>
      <section className="intro compact">
        <h1>Problems</h1>
        <p className="lede">
          {PROBLEMS.length} problems laid out as a roadmap: topic by topic, easy to hard, with the interview classics marked <span className="tier-chip">Must know</span>. Start at the top, or jump to the topic you need.
        </p>
        <div className="intro-actions">
          {next ? (
            <button className="btn primary" onClick={() => navigate({ name: 'problem', id: next.id })}>
              {done ? 'Continue with ' : 'Start with '}
              {next.title}
            </button>
          ) : (
            <span className="solved-badge">Everything solved. Nice work.</span>
          )}
          <button
            className="btn"
            onClick={() => {
              const pool = PROBLEMS.filter((p) => !solved[p.id]);
              const pick = (pool.length ? pool : PROBLEMS)[Math.floor(Math.random() * (pool.length || PROBLEMS.length))]!;
              navigate({ name: 'problem', id: pick.id });
            }}
          >
            Random problem
          </button>
          <Link className="btn" to={{ name: 'plans' }}>
            Study plans
          </Link>
          <span className="muted" style={{ fontSize: '.88rem' }}>
            Progress and code are saved in this browser. Sign in to keep them in the cloud.
          </span>
        </div>
      </section>

      <section className="daily" aria-label="Daily challenge">
        <div>
          <div className="eyebrow">Daily challenge</div>
          <b>{daily.title}</b> <span className="muted">&middot; {daily.diff} &middot; {daily.topic}</span>
        </div>
        {dailyDone ? (
          <span className="solved-badge">Done for today</span>
        ) : (
          <Link className="btn primary sm" to={{ name: 'problem', id: daily.id }}>
            Solve it
          </Link>
        )}
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
        <div className="roadmap" role="group" aria-label="Topics in roadmap order">
          <button className="tchip" aria-pressed={f.topic === 'All'} onClick={() => setFilters({ topic: 'All' })}>
            All topics <small className="tnum">{PROBLEMS.length}</small>
          </button>
          {TOPICS.map((t) => {
            const e = byTopic.get(t)!;
            return (
              <button key={t} className="tchip" aria-pressed={f.topic === t} onClick={() => setFilters({ topic: f.topic === t ? 'All' : t })}>
                {t}{' '}
                <small className="tnum">
                  {e.done > 0 ? `${e.done}/${e.total}` : e.total}
                </small>
              </button>
            );
          })}
        </div>

        <div className="filters">
          <input type="search" placeholder="Search problems" aria-label="Search problems" value={f.q} onChange={(e) => setFilters({ q: e.target.value })} />
          <div className="seg">
            {DIFFS.map((d) => (
              <button key={d} aria-pressed={f.diff === d} onClick={() => setFilters({ diff: d })}>
                {d}
              </button>
            ))}
          </div>
          <select aria-label="Interview priority" value={f.tier} onChange={(e) => setFilters({ tier: e.target.value as Filters['tier'] })}>
            <option value="All">All priorities</option>
            <option value="must">Must know ({mustDone}/{mustTotal})</option>
            <option value="core">Must know + common</option>
          </select>
          <select aria-label="Status" value={f.status} onChange={(e) => setFilters({ status: e.target.value as Filters['status'] })}>
            {STATUSES.map((t) => (
              <option key={t}>{t}</option>
            ))}
          </select>
          <select aria-label="Sort" value={f.sort} onChange={(e) => setFilters({ sort: e.target.value as Filters['sort'] })}>
            {(Object.keys(SORTS) as Filters['sort'][]).map((k) => (
              <option key={k} value={k}>
                {SORTS[k].label}
              </option>
            ))}
          </select>
        </div>
        <div className="result-line muted" aria-live="polite">
          {list.length === PROBLEMS.length ? `${list.length} problems` : `${list.length} of ${PROBLEMS.length} problems`}
          {filtered && (
            <button className="linkish" onClick={reset}>
              Clear filters
            </button>
          )}
        </div>
        <div className="table" id="rows">
          <div className="row head">
            <span />
            <span>Problem</span>
            <span className="topic">Topic</span>
            <span>Level</span>
          </div>
          {list.length === 0 && <div className="empty">No problems match these filters.</div>}
          {shown.map((p, i) => {
            const newTopic = grouped && (i === 0 || shown[i - 1]!.topic !== p.topic);
            const e = byTopic.get(p.topic)!;
            return (
              <Fragment key={p.id}>
                {newTopic && (
                  <div className="row-group" role="presentation">
                    <b>{p.topic}</b>
                    <span className="muted tnum">
                      {e.done} of {e.total} solved
                    </span>
                  </div>
                )}
                <ProblemRow p={p} number={numbers.get(p.id)} done={!!solved[p.id]} starred={!!stars[p.id]?.on} />
              </Fragment>
            );
          })}
        </div>
        {limit < list.length && (
          <div className="more" ref={sentinel}>
            <button className="btn" onClick={() => setLimit((n) => n + MORE)}>
              Show {Math.min(MORE, list.length - limit)} more
            </button>
            <span className="muted tnum">
              {limit} of {list.length}
            </span>
          </div>
        )}
      </section>
      <footer className="foot">Python and JavaScript run inside your browser. C++ and Java are compiled on a Judge0 server, which you can change in Engine settings on any problem.</footer>
    </>
  );
}
