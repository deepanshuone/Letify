import { useEffect, useMemo, useRef } from 'react';
import { Heatmap } from '../components/Heatmap';
import { Link, Pill } from '../components/common';
import { fmtMs, timeAgo } from '../core/format';
import { BY_ID, PROBLEMS } from '../data';
import { useAuthDialog } from '../state/authdialog';
import { useCloud } from '../state/cloud';
import { useToast } from '../state/toast';
import { useUserData } from '../state/userdata';
import { activityByDay, badges, dayKey, levelFor, streaks, summarize } from '../user/stats';
import { LANGS } from '../core/languages';

const VERDICT_TEXT = { ac: 'Accepted', wa: 'Wrong Answer', re: 'Runtime Error', tle: 'Time Limit', ce: 'Compile Error' } as const;

function Bar({ label, value, total, tone }: { label: string; value: number; total: number; tone?: string }) {
  const pct = total ? Math.round((100 * value) / total) : 0;
  return (
    <div className="mbar">
      <div className="mbar-top">
        <span>{tone ? <Pill diff={tone as 'Easy'} /> : label}</span>
        <span className="tnum muted">
          {value} / {total}
        </span>
      </div>
      <div className="bar" role="progressbar" aria-valuemin={0} aria-valuemax={total} aria-valuenow={value} aria-label={label}>
        <i style={{ width: `${pct}%` }} />
      </div>
    </div>
  );
}

export function Profile() {
  const ud = useUserData();
  const cloud = useCloud();
  const auth = useAuthDialog();
  const toast = useToast();
  const file = useRef<HTMLInputElement>(null);
  const { data } = ud;
  useEffect(() => {
    document.title = 'Your profile · Letify';
  }, []);

  const now = Date.now();
  const today = dayKey(now);
  const summary = useMemo(() => summarize(data, PROBLEMS), [data]);
  const activity = useMemo(() => activityByDay(data), [data]);
  const st = useMemo(() => streaks(activity, today), [activity, today]);
  const lvl = levelFor(summary.xp);
  const list = useMemo(() => badges({ data, summary, streaks: st, problems: PROBLEMS }), [data, summary, st]);
  const earned = list.filter((b) => b.earned);
  const locked = list.filter((b) => !b.earned).sort((a, b) => b.have / b.need - a.have / a.need);
  const accepted = data.subs.filter((s) => s.verdict === 'ac').length;
  const levelPct = lvl.to === null ? 100 : Math.round((100 * (lvl.xp - lvl.from)) / (lvl.to - lvl.from));
  const recent = data.subs.slice(0, 12);
  const starred = PROBLEMS.filter((p) => data.stars[p.id]?.on);

  const exportFile = () => {
    const url = URL.createObjectURL(new Blob([ud.exportJson()], { type: 'application/json' }));
    const a = document.createElement('a');
    a.href = url;
    a.download = `letify-progress-${today}.json`;
    a.click();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
  };
  const importFile = async (f: File | undefined) => {
    if (!f) return;
    try {
      if (f.size > 5_000_000) throw new Error('too big');
      ud.importData(JSON.parse(await f.text()));
      toast('Progress imported and merged');
    } catch {
      toast('That file could not be read as Letify progress');
    }
    if (file.current) file.current.value = '';
  };

  return (
    <>
      <section className="profile-head">
        <div className="profile-id">
          <div className="avatar big" aria-hidden="true">
            {(cloud.user?.email[0] ?? 'Y').toUpperCase()}
          </div>
          <div>
            <h1>{cloud.user ? cloud.user.email : 'Your profile'}</h1>
            <div className="muted">
              {cloud.user
                ? cloud.status.state === 'synced'
                  ? 'Progress is saved to your account.'
                  : cloud.status.state === 'error'
                    ? cloud.status.message
                    : 'Syncing your progress...'
                : 'Progress is saved in this browser.'}
              {cloud.enabled && !cloud.user && cloud.ready && (
                <>
                  {' '}
                  <button className="linklike" onClick={auth.open}>
                    Sign in to keep it on every device
                  </button>
                </>
              )}
            </div>
          </div>
        </div>
        <div className="level-card">
          <div className="level-top">
            <b>{lvl.name}</b>
            <span className="muted tnum">{lvl.xp} XP</span>
          </div>
          <div className="bar" role="progressbar" aria-valuemin={0} aria-valuemax={100} aria-valuenow={levelPct} aria-label="Progress to the next level">
            <i style={{ width: `${levelPct}%` }} />
          </div>
          <div className="muted level-foot">{lvl.to === null ? 'Top level reached.' : `${lvl.to - lvl.xp} XP to ${lvl.nextName}`}</div>
        </div>
      </section>

      <section className="tiles" aria-label="Summary">
        <div className="tile">
          <b className="tnum">
            {summary.solved}
            <small> / {summary.total}</small>
          </b>
          <span>problems solved</span>
        </div>
        <div className="tile">
          <b className="tnum">{st.current}</b>
          <span>day streak</span>
        </div>
        <div className="tile">
          <b className="tnum">{st.longest}</b>
          <span>longest streak</span>
        </div>
        <div className="tile">
          <b className="tnum">{st.activeDays}</b>
          <span>active days</span>
        </div>
        <div className="tile">
          <b className="tnum">{data.subs.length ? `${Math.round((100 * accepted) / data.subs.length)}%` : '-'}</b>
          <span>acceptance rate</span>
        </div>
      </section>

      <div className="two-col">
        <section className="card" aria-labelledby="h-diff">
          <h2 id="h-diff">By difficulty</h2>
          {(['Easy', 'Medium', 'Hard'] as const).map((d) => (
            <Bar key={d} label={d} tone={d} value={summary.byDiff[d].solved} total={summary.byDiff[d].total} />
          ))}
        </section>
        <section className="card" aria-labelledby="h-topic">
          <h2 id="h-topic">By topic</h2>
          {summary.topics.map((t) => (
            <Bar key={t.topic} label={t.topic} value={t.solved} total={t.total} />
          ))}
        </section>
      </div>

      <section className="card" aria-labelledby="h-act">
        <h2 id="h-act">Activity</h2>
        <Heatmap activity={activity} today={today} />
      </section>

      <section className="card" aria-labelledby="h-badges">
        <h2 id="h-badges">
          Badges <span className="muted tnum">{earned.length} of {list.length}</span>
        </h2>
        <ul className="badges">
          {earned.map((b) => (
            <li key={b.id} className="badge on">
              <b>{b.name}</b>
              <span>{b.blurb}</span>
            </li>
          ))}
          {locked.map((b) => (
            <li key={b.id} className="badge">
              <b>{b.name}</b>
              <span>{b.blurb}</span>
              <span className="tnum badge-progress">
                {b.have} / {b.need}
              </span>
            </li>
          ))}
        </ul>
      </section>

      {starred.length > 0 && (
        <section className="card" aria-labelledby="h-star">
          <h2 id="h-star">Starred problems</h2>
          <div className="chips">
            {starred.map((p) => (
              <Link key={p.id} className="chip link" to={{ name: 'problem', id: p.id }}>
                {p.title}
              </Link>
            ))}
          </div>
        </section>
      )}

      <section className="card" aria-labelledby="h-sub">
        <h2 id="h-sub">Recent submissions</h2>
        {recent.length === 0 ? (
          <p className="muted">Nothing yet. Submit a solution and it shows up here.</p>
        ) : (
          <div className="sub-table-wrap">
            <table className="sub-table">
              <thead>
                <tr>
                  <th scope="col">Problem</th>
                  <th scope="col">Result</th>
                  <th scope="col">Language</th>
                  <th scope="col">Runtime</th>
                  <th scope="col">When</th>
                </tr>
              </thead>
              <tbody>
                {recent.map((s) => {
                  const p = BY_ID.get(s.pid);
                  return (
                    <tr key={s.id}>
                      <td>{p ? <Link to={{ name: 'problem', id: p.id }}>{p.title}</Link> : s.pid}</td>
                      <td>
                        <span className={`vtag ${s.verdict}`}>{VERDICT_TEXT[s.verdict]}</span>
                      </td>
                      <td>{LANGS[s.lang].label}</td>
                      <td className="tnum">{fmtMs(s.ms)}</td>
                      <td className="muted">{timeAgo(s.at, now)}</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </section>

      <section className="card" aria-labelledby="h-data">
        <h2 id="h-data">Your data</h2>
        <p className="muted">
          {cloud.user ? 'Your progress is kept in your account and in this browser.' : 'Your progress and code live in this browser. Export a copy to back it up or move it to another browser.'}
        </p>
        <div className="row-actions">
          <button className="btn" onClick={exportFile}>
            Export progress
          </button>
          <button className="btn" onClick={() => file.current?.click()}>
            Import progress
          </button>
          <input ref={file} type="file" accept="application/json,.json" hidden onChange={(e) => void importFile(e.target.files?.[0])} />
          {!cloud.user && (
            <button
              className="btn ghost"
              onClick={() => {
                if (confirm('Delete all progress and saved code from this browser? This cannot be undone.')) {
                  ud.clearAll();
                  toast('Local progress deleted');
                }
              }}
            >
              Delete local progress
            </button>
          )}
        </div>
      </section>
    </>
  );
}

