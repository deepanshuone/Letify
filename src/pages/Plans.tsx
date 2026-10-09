import { BRAND } from '../config';
import { useEffect } from 'react';
import { Link } from '../components/common';
import { ProblemRow } from '../components/ProblemRow';
import { BY_ID, PROBLEMS } from '../data';
import { PLANS, PLAN_BY_ID, planIds } from '../data/plans';
import { useUserData } from '../state/userdata';
import { planProgress } from '../user/stats';

export function Plans() {
  const { data } = useUserData();
  useEffect(() => {
    document.title = `Study plans · ${BRAND}`;
  }, []);
  return (
    <>
      <section className="intro compact">
        <h1>Study plans</h1>
        <p className="lede">Not sure what to solve next? Follow a plan. Each one is an ordered path through the problems, with a short note on what every step teaches.</p>
      </section>
      <div className="plans">
        {PLANS.map((plan) => {
          const pr = planProgress(plan, data);
          const next = planIds(plan).find((id) => !data.solved[id]);
          const pct = pr.total ? Math.round((100 * pr.solved) / pr.total) : 0;
          return (
            <article className="plan-card" key={plan.id}>
              <div className="plan-top">
                <span className={`level ${plan.level}`}>{plan.level}</span>
                <span className="muted tnum">{pr.total} problems</span>
              </div>
              <h2>
                <Link to={{ name: 'plan', id: plan.id }}>{plan.title}</Link>
              </h2>
              <p>{plan.blurb}</p>
              <div className="bar" role="progressbar" aria-valuemin={0} aria-valuemax={pr.total} aria-valuenow={pr.solved} aria-label={`${plan.title} progress`}>
                <i style={{ width: `${pct}%` }} />
              </div>
              <div className="plan-foot">
                <span className="muted tnum">
                  {pr.solved} of {pr.total} solved
                </span>
                <Link className="btn sm primary" to={next ? { name: 'problem', id: next } : { name: 'plan', id: plan.id }}>
                  {pr.solved === 0 ? 'Start' : next ? 'Continue' : 'Review'}
                </Link>
              </div>
            </article>
          );
        })}
      </div>
    </>
  );
}

export function PlanDetail({ id }: { id: string }) {
  const plan = PLAN_BY_ID.get(id)!;
  const { data } = useUserData();
  const pr = planProgress(plan, data);
  const next = planIds(plan).find((x) => !data.solved[x]);
  const pct = pr.total ? Math.round((100 * pr.solved) / pr.total) : 0;
  useEffect(() => {
    document.title = `${plan.title} · Study plans · ${BRAND}`;
  }, [plan.title]);
  return (
    <>
      <div className="pv-head">
        <Link className="back" to={{ name: 'plans' }}>
          &larr; All plans
        </Link>
      </div>
      <section className="intro compact" style={{ paddingTop: 6 }}>
        <span className={`level ${plan.level}`}>{plan.level}</span>
        <h1 style={{ marginTop: 10 }}>{plan.title}</h1>
        <p className="lede">{plan.blurb}</p>
        <div className="plan-progress">
          <div className="bar" role="progressbar" aria-valuemin={0} aria-valuemax={pr.total} aria-valuenow={pr.solved} aria-label="Plan progress">
            <i style={{ width: `${pct}%` }} />
          </div>
          <span className="tnum muted">
            {pr.solved} of {pr.total} solved
          </span>
          {next ? (
            <Link className="btn primary" to={{ name: 'problem', id: next }}>
              {pr.solved ? 'Continue: ' : 'Start: '}
              {BY_ID.get(next)!.title}
            </Link>
          ) : (
            <span className="solved-badge">Plan complete</span>
          )}
        </div>
      </section>
      {plan.sections.map((sec, i) => {
        const sp = pr.sections[i]!;
        return (
          <section className="plan-section" key={sec.title}>
            <div className="plan-section-head">
              <h2>
                <span className="muted tnum">{i + 1}.</span> {sec.title}
              </h2>
              <span className="muted tnum">
                {sp.solved}/{sp.total}
              </span>
            </div>
            <p className="muted">{sec.note}</p>
            <div className="table">
              {sec.ids.map((pid) => {
                const p = BY_ID.get(pid)!;
                return <ProblemRow key={pid} p={p} number={PROBLEMS.indexOf(p) + 1} done={!!data.solved[pid]} starred={data.stars[pid]?.on} />;
              })}
            </div>
          </section>
        );
      })}
    </>
  );
}
