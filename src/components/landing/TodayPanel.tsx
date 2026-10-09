import { useMemo } from 'react';
import { Link, Pill } from '../common';
import { PROBLEMS } from '../../data';
import { useUserData } from '../../state/userdata';
import { activityByDay, dailyProblem, dayKey, streaks } from '../../user/stats';
import type { Diff } from '../../types';

const DAY = 86_400_000;
const DIFFS: Diff[] = ['Easy', 'Medium', 'Hard'];
const LETTERS = ['S', 'M', 'T', 'W', 'T', 'F', 'S'];

/** The hero card. Everything in it is the visitor's own data: a new visitor sees today's challenge and empty bars, never made-up progress. */
export function TodayPanel() {
  const { data } = useUserData();
  const now = useMemo(() => Date.now(), []);
  const today = dayKey(now);
  const activity = useMemo(() => activityByDay(data), [data]);
  const st = streaks(activity, today);
  const daily = dailyProblem(today, PROBLEMS);
  const dailyDone = !!data.solved[daily.id];
  const week = useMemo(
    () =>
      Array.from({ length: 7 }, (_, i) => {
        const day = dayKey(now - (6 - i) * DAY);
        return { day, letter: LETTERS[new Date(day + 'T00:00:00Z').getUTCDay()]!, n: activity[day] ?? 0, today: i === 6 };
      }),
    [now, activity],
  );
  const solvedTotal = PROBLEMS.filter((p) => data.solved[p.id]).length;
  const started = solvedTotal > 0 || st.activeDays > 0;

  return (
    <aside className="lp-demo lp-today" aria-label="Your day">
      <div className="lp-demo-bar">
        <span>Today</span>
        <span className="lp-lang">{started ? `${solvedTotal} of ${PROBLEMS.length} solved` : `${PROBLEMS.length} problems`}</span>
      </div>

      <div className="lp-daily">
        <div className="eyebrow">Daily challenge</div>
        <b className="lp-daily-title">{daily.title}</b>
        <div className="lp-daily-meta">
          <Pill diff={daily.diff} />
          <span>{daily.topic}</span>
        </div>
        {dailyDone ? (
          <span className="solved-badge">Done for today</span>
        ) : (
          <Link className="lp-btn main sm" to={{ name: 'problem', id: daily.id }}>
            Solve it
          </Link>
        )}
      </div>

      <div className="lp-week">
        <div className="lp-week-head">
          <b>{st.current > 0 ? `${st.current}-day streak` : 'No streak yet'}</b>
          <small>{st.current > 0 ? (activity[today] ? 'Today is counted' : 'Solve one today to keep it') : 'Solve one problem to start it'}</small>
        </div>
        <ol className="lp-week-days">
          {week.map((d) => (
            <li key={d.day} className={`${d.n > 0 ? 'on' : ''}${d.today ? ' today' : ''}`} aria-label={`${d.day}: ${d.n > 0 ? 'practiced' : 'no practice'}`}>
              <span aria-hidden="true" />
              <small aria-hidden="true">{d.letter}</small>
            </li>
          ))}
        </ol>
      </div>

      <div className="lp-levels">
        {DIFFS.map((df) => {
          const all = PROBLEMS.filter((p) => p.diff === df);
          const n = all.filter((p) => data.solved[p.id]).length;
          return (
            <div key={df} className="lp-level">
              <span className={`level ${df}`}>{df}</span>
              <span className="bar" aria-hidden="true">
                <i className={df} style={{ width: `${Math.round((100 * n) / all.length)}%` }} />
              </span>
              <small className="tnum">
                {n} / {all.length}
              </small>
            </div>
          );
        })}
      </div>
    </aside>
  );
}
