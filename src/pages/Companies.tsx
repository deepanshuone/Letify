import { useEffect } from 'react';
import { BRAND } from '../config';
import { Link } from '../components/common';
import { ProblemRow } from '../components/ProblemRow';
import { BY_ID } from '../data';
import { COMPANY_LISTS, type CompanyList } from '../data/companies';
import { useUserData } from '../state/userdata';

/* Brand colour for the square tile on each card. Plain letters, no logos: company logos are trademarks. */
const TILE: Record<string, string> = {
  Google: '#1a73e8',
  Microsoft: '#0f6cbd',
  Amazon: '#232f3e',
  Meta: '#0866ff',
  Apple: '#1d1d1f',
  Uber: '#000000',
  Adobe: '#ff0000',
  Bloomberg: '#1f1f1f',
  Oracle: '#c74634',
  Netflix: '#b20710',
  Salesforce: '#00a1e0',
  'Goldman Sachs': '#3b6e8f',
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
                  <h2 id={`co-${c.name}`}>
                    <Link to={{ name: 'company', id: c.name }}>{c.name}</Link>
                  </h2>
                  <small className="muted tnum">
                    {done} of {problems.length} solved
                  </small>
                </div>
              </header>
              <div className="bar" role="progressbar" aria-valuemin={0} aria-valuemax={problems.length} aria-valuenow={done} aria-label={`${c.name} progress`}>
                <i style={{ width: `${pct}%` }} />
              </div>
              <Link to={{ name: 'company', id: c.name }} className="co-all">
                Open {c.name} questions ({problems.length}) →
              </Link>
            </article>
          );
        })}
      </div>
    </>
  );
}

export function CompanyPage({ id }: { id: string }) {
  const { data } = useUserData();
  const list: CompanyList = COMPANY_LISTS.find((c) => c.name === id) ?? COMPANY_LISTS[0]!;
  const problems = list.ids.map((x) => BY_ID.get(x)).filter((p): p is NonNullable<typeof p> => !!p);
  const done = problems.filter((p) => data.solved[p.id]).length;
  useEffect(() => {
    document.title = `${list.name} questions · ${BRAND}`;
  }, [list.name]);
  return (
    <>
      <section className="intro compact">
        <p className="muted">
          <Link to={{ name: 'companies' }}>All companies</Link>
        </p>
        <div className="co-head">
          <span className="co-tile" style={{ background: TILE[list.name] ?? 'var(--accent)' }} aria-hidden="true">
            {list.name.charAt(0)}
          </span>
          <h1>{list.name} questions</h1>
        </div>
        <p className="lede">
          {problems.length} problems commonly reported at {list.name}, most reported first. Not official. {done} of {problems.length} solved.
        </p>
      </section>
      <div className="bar" role="progressbar" aria-valuemin={0} aria-valuemax={problems.length} aria-valuenow={done} aria-label={`${list.name} progress`}>
        <i style={{ width: `${problems.length ? Math.round((100 * done) / problems.length) : 0}%` }} />
      </div>
      <div className="table" role="table" aria-label={`${list.name} questions`}>
        {problems.map((p, i) => (
          <ProblemRow key={p.id} p={p} number={i + 1} done={!!data.solved[p.id]} starred={!!data.stars[p.id]?.on} />
        ))}
      </div>
    </>
  );
}
