import { useEffect } from 'react';
import { BRAND } from '../config';
import { Link, Pill } from '../components/common';
import { BY_ID } from '../data';
import { COMPANY_LISTS } from '../data/companies';
import { useUserData } from '../state/userdata';

/* Brand colour for the square tile on each card. Plain letters, no logos: company logos are trademarks. */
const TILE: Record<string, string> = {
  Google: '#1a73e8',
  Microsoft: '#0f6cbd',
  Amazon: '#232f3e',
  Meta: '#0866ff',
  Apple: '#1d1d1f',
  Uber: '#000000',
};

export function Companies() {
  const { data } = useUserData();
  useEffect(() => {
    document.title = `Company questions · ${BRAND}`;
  }, []);
  return (
    <>
      <section className="intro compact">
        <h1>Company questions</h1>
        <p className="lede">
          Problems that candidates commonly report in interviews at each company, most reported first. These lists are compiled from general knowledge and are not official. Companies change their questions, so use them as practice, not as a promise.
        </p>
      </section>
      <div className="co-grid">
        {COMPANY_LISTS.map((c) => {
          const problems = c.ids.map((id) => BY_ID.get(id)).filter((p): p is NonNullable<typeof p> => !!p);
          const done = problems.filter((p) => data.solved[p.id]).length;
          const pct = problems.length ? Math.round((100 * done) / problems.length) : 0;
          return (
            <article className="co-card" key={c.name} aria-labelledby={`co-${c.name}`}>
              <header className="co-head">
                <span className="co-tile" style={{ background: TILE[c.name] ?? 'var(--accent)' }} aria-hidden="true">
                  {c.name.charAt(0)}
                </span>
                <div>
                  <h2 id={`co-${c.name}`}>{c.name}</h2>
                  <small className="muted tnum">
                    {done} of {problems.length} solved
                  </small>
                </div>
              </header>
              <div className="bar" role="progressbar" aria-valuemin={0} aria-valuemax={problems.length} aria-valuenow={done} aria-label={`${c.name} progress`}>
                <i style={{ width: `${pct}%` }} />
              </div>
              <ol className="co-list">
                {problems.map((p) => (
                  <li key={p.id}>
                    <Link to={{ name: 'problem', id: p.id }} className="co-q">
                      <span className={data.solved[p.id] ? 'co-check on' : 'co-check'} aria-label={data.solved[p.id] ? 'solved' : 'not solved'} />
                      <span className="co-title">{p.title}</span>
                      <Pill diff={p.diff} />
                    </Link>
                  </li>
                ))}
              </ol>
            </article>
          );
        })}
      </div>
    </>
  );
}
