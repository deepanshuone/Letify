import { BRAND } from '../config';
import { useEffect } from 'react';
import { Link, Pill } from '../components/common';
import { BY_ID, PROBLEMS } from '../data';
import { useContest } from '../state/contest';
import { useUserData } from '../state/userdata';
import { CONTEST_MINUTES, PENALTY_MINUTES, POINTS, clock, maxScore, standing } from '../user/contest';
import type { ContestResult } from '../user/model';

function ResultRow({ r }: { r: ContestResult }) {
  const s = standing(r, PROBLEMS);
  return (
    <tr>
      <td>{new Date(r.start).toLocaleString(undefined, { dateStyle: 'medium', timeStyle: 'short' })}</td>
      <td className="tnum">
        <b>{s.score}</b> / {maxScore(r.ids, PROBLEMS)}
      </td>
      <td className="tnum">
        {s.solvedCount} / {r.ids.length}
      </td>
      <td className="tnum">{s.solvedCount ? `${s.minutes} min` : '-'}</td>
    </tr>
  );
}

export function ContestPage() {
  const c = useContest();
  const { data } = useUserData();
  useEffect(() => {
    document.title = `Contest · ${BRAND}`;
  }, []);

  const history = Object.values(data.contests).sort((a, b) => b.start - a.start);
  const best = history.reduce((m, r) => Math.max(m, standing(r, PROBLEMS).score), 0);
  const last = c.lastFinished ? data.contests[c.lastFinished] : undefined;

  if (c.active) {
    const a = c.active;
    const left = a.end - c.now;
    const s = standing(a, PROBLEMS);
    return (
      <>
        <section className="intro compact">
          <h1>Contest in progress</h1>
          <div className="contest-clock tnum" role="timer" aria-label="Time left">
            {clock(left)}
          </div>
          <p className="lede">
            Score <b className="tnum">{s.score}</b> of {maxScore(a.ids, PROBLEMS)}. Hints and editorials are closed for these problems until the contest ends. Each wrong submission adds {PENALTY_MINUTES} minutes.
          </p>
        </section>
        <div className="table">
          {a.ids.map((id, i) => {
            const p = BY_ID.get(id)!;
            const solvedAt = a.solved[id];
            const wrong = a.wrong[id] ?? 0;
            return (
              <Link key={id} className="row contest-row" to={{ name: 'problem', id }}>
                <span className="contest-letter">{String.fromCharCode(65 + i)}</span>
                <span className="t">
                  <b>{p.title}</b>
                  <small>
                    {POINTS[p.diff]} points{wrong ? ` · ${wrong} wrong attempt${wrong > 1 ? 's' : ''}` : ''}
                  </small>
                </span>
                <span className="topic muted">{solvedAt !== undefined ? `Solved at ${Math.floor((solvedAt - a.start) / 60000)} min` : 'Not solved yet'}</span>
                <span>
                  <Pill diff={p.diff} />
                </span>
              </Link>
            );
          })}
        </div>
        <p style={{ marginTop: 18 }}>
          <button className="btn" onClick={() => confirm('End the contest now? Your score so far is saved.') && c.finish()}>
            End contest
          </button>
        </p>
      </>
    );
  }

  return (
    <>
      <section className="intro compact">
        <h1>Virtual contest</h1>
        <p className="lede">
          {CONTEST_MINUTES} minutes, four problems you have not solved yet (one Easy, two Medium, one Hard). Points are {POINTS.Easy} / {POINTS.Medium} / {POINTS.Hard} by level, and every wrong submission costs {PENALTY_MINUTES} minutes. It is a timed way to practise under pressure, and it runs on your own device.
        </p>
        <div className="intro-actions">
          <button className="btn primary lg" onClick={c.start}>
            Start a contest
          </button>
          {history.length > 0 && (
            <span className="muted">
              Best score: <b className="tnum">{best}</b>
            </span>
          )}
        </div>
      </section>

      {last && (
        <section className="card" aria-labelledby="h-last">
          <h2 id="h-last">Contest finished</h2>
          <p>
            You scored <b className="tnum">{standing(last, PROBLEMS).score}</b> of {maxScore(last.ids, PROBLEMS)} and solved {standing(last, PROBLEMS).solvedCount} of {last.ids.length}.
          </p>
          <div className="chips">
            {last.ids.map((id) => (
              <Link key={id} className={`chip link ${last.solved[id] !== undefined ? 'good' : ''}`} to={{ name: 'problem', id }}>
                {last.solved[id] !== undefined ? '✓ ' : ''}
                {BY_ID.get(id)?.title ?? id}
              </Link>
            ))}
          </div>
        </section>
      )}

      <section className="card" aria-labelledby="h-hist">
        <h2 id="h-hist">Your contests</h2>
        {history.length === 0 ? (
          <p className="muted">No contests yet.</p>
        ) : (
          <div className="sub-table-wrap">
            <table className="sub-table">
              <thead>
                <tr>
                  <th scope="col">Started</th>
                  <th scope="col">Score</th>
                  <th scope="col">Solved</th>
                  <th scope="col">Time with penalties</th>
                </tr>
              </thead>
              <tbody>
                {history.slice(0, 15).map((r) => (
                  <ResultRow key={r.id} r={r} />
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </>
  );
}
