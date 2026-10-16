import { useEffect, useState } from 'react';
import { BRAND } from '../config';
import { Link } from '../components/common';
import { ProblemRow } from '../components/ProblemRow';
import { BY_ID } from '../data';
import { COMPANY_LISTS } from '../data/companies';
import { useUserData } from '../state/userdata';

export function Companies() {
  const { data } = useUserData();
  const [active, setActive] = useState(0);
  useEffect(() => {
    document.title = `Company questions · ${BRAND}`;
  }, []);
  const list = COMPANY_LISTS[active] ?? COMPANY_LISTS[0]!;
  const problems = list.ids.map((id) => BY_ID.get(id)).filter((p): p is NonNullable<typeof p> => !!p);
  const done = problems.filter((p) => data.solved[p.id]).length;
  return (
    <>
      <section className="intro compact">
        <h1>Company questions</h1>
        <p className="lede">
          Problems that candidates commonly report in interviews at each company, most reported first. These lists are compiled from general knowledge and are not official. Companies change their questions, so use them as practice, not as a promise.
        </p>
      </section>
      <div className="row-actions" role="tablist" aria-label="Company">
        {COMPANY_LISTS.map((c, i) => (
          <button
            key={c.name}
            role="tab"
            aria-selected={i === active}
            className={`btn sm${i === active ? ' primary' : ''}`}
            onClick={() => setActive(i)}
          >
            {c.name}
          </button>
        ))}
      </div>
      <p className="muted tnum">
        {done} of {problems.length} solved for {list.name}.{' '}
        <Link to={{ name: 'problems' }}>Browse all problems</Link>
      </p>
      <div className="table" role="table" aria-label={`${list.name} questions`}>
        {problems.map((p, i) => (
          <ProblemRow key={p.id} p={p} number={i + 1} done={!!data.solved[p.id]} starred={!!data.stars[p.id]?.on} />
        ))}
      </div>
    </>
  );
}
