import { useEffect, useMemo } from 'react';
import { BRAND, CLOUD_ENABLED } from '../config';
import { Heatmap } from '../components/Heatmap';
import { HeroDemo } from '../components/landing/HeroDemo';
import { Link, Pill, Rich, SectionLink } from '../components/common';
import { BY_ID, PROBLEMS, TOPICS } from '../data';
import { PLANS } from '../data/plans';
import { navigate, takePendingSection } from '../router';
import { useFilters } from '../state/filters';
import { useUserData } from '../state/userdata';
import { CONTEST_MINUTES, POINTS, clock, mulberry32, pickProblems } from '../user/contest';
import { dayKey } from '../user/stats';

const DAY = 86_400_000;

/** Made-up activity for the example heatmap, always the same so the page does not flicker between visits. */
function sampleActivity(now: number): Record<string, number> {
  const rnd = mulberry32(11);
  const out: Record<string, number> = {};
  for (let d = 0; d < 230; d++) {
    const busy = d < 40 ? 0.8 : 0.5;
    if (rnd() < busy) out[dayKey(now - d * DAY)] = 1 + Math.floor(rnd() * 6);
  }
  return out;
}

const SAMPLE_PROGRESS = [100, 46, 17, 0];
const ORDER = { Easy: 0, Medium: 1, Hard: 2 } as const;

export function Landing() {
  const { setFilters } = useFilters();
  const { data } = useUserData();
  const total = PROBLEMS.length;
  const now = useMemo(() => Date.now(), []);
  const activity = useMemo(() => sampleActivity(now), [now]);
  const contestIds = useMemo(() => pickProblems(PROBLEMS, {}, 2024), []);
  const hint = BY_ID.get('two-sum')?.hints[0] ?? '';
  const byTopic = useMemo(
    () => TOPICS.map((t) => ({ topic: t, list: PROBLEMS.filter((p) => p.topic === t).sort((a, b) => ORDER[a.diff] - ORDER[b.diff]) })).sort((a, b) => b.list.length - a.list.length),
    [],
  );

  useEffect(() => {
    const id = takePendingSection();
    if (id) requestAnimationFrame(() => document.getElementById(id)?.scrollIntoView({ behavior: 'smooth', block: 'start' }));
  }, []);

  const openTopic = (topic: string) => {
    setFilters({ topic, diff: 'All', status: 'All', q: '' });
    navigate({ name: 'problems' });
  };

  return (
    <div id="landing">
      <section className="lp-hero">
        <div className="lp-wrap lp-hero-grid">
          <div className="lp-hero-text">
            <h1>Solve DSA problems. All of it is free.</h1>
            <p className="lede">
              {total} problems from Easy to Hard, checked against hidden tests in Python, JavaScript, C++ or Java. Hints, editorials, study plans and timed contests are included.
            </p>
            <div className="lp-cta">
              <Link className="lp-btn main cta-main" to={{ name: 'problems' }}>
                Start solving
              </Link>
              <Link className="lp-btn ghost" to={{ name: 'plans' }}>
                See study plans
              </Link>
            </div>
            <p className="lp-note">No sign-up needed. Python and JavaScript run right in your browser.</p>
          </div>
          <HeroDemo />
        </div>
      </section>

      <div className="lp-wrap">
        <section className="lp-sec" id="topics" aria-labelledby="h-topics">
          <h2 id="h-topics">Pick a topic</h2>
          <p className="sec-lede">
            Every square is one problem, coloured by level: green is Easy, amber is Medium, red is Hard. Squares fill in as you solve them.
          </p>
          <div className="lp-topics">
            {byTopic.map(({ topic, list }) => {
              const done = list.filter((p) => data.solved[p.id]).length;
              return (
                <a
                  key={topic}
                  className="lp-topic"
                  href="#/problems"
                  onClick={(e) => {
                    e.preventDefault();
                    openTopic(topic);
                  }}
                  aria-label={`${topic}: ${list.length} ${list.length === 1 ? 'problem' : 'problems'}, ${done} solved`}
                >
                  <b>{topic}</b>
                  <span className="lp-sq" aria-hidden="true">
                    {list.map((p) => (
                      <i key={p.id} className={`${p.diff}${data.solved[p.id] ? ' done' : ''}`} />
                    ))}
                  </span>
                  <small className="tnum">
                    {done > 0 ? `${done} of ${list.length} solved` : `${list.length} ${list.length === 1 ? 'problem' : 'problems'}`}
                  </small>
                </a>
              );
            })}
          </div>
        </section>

        <section className="lp-sec" id="features" aria-labelledby="h-features">
          <h2 id="h-features">What you get with every problem</h2>
          <p className="sec-lede">Nothing here is behind a paywall. The examples below use sample data.</p>
          <div className="lp-bento">
            <article className="lp-tile t3">
              <h3>Follow a study plan</h3>
              <p>{PLANS.length} ordered paths, from Foundations to Hard Mode. Each step says what it teaches.</p>
              <ul className="lp-plans">
                {PLANS.slice(0, 4).map((pl, k) => (
                  <li key={pl.id}>
                    <span>{pl.title}</span>
                    <span className={`level ${pl.level}`}>{pl.level}</span>
                    <span className="bar" aria-hidden="true">
                      <i style={{ width: `${SAMPLE_PROGRESS[k]}%` }} />
                    </span>
                    <small className="tnum">{SAMPLE_PROGRESS[k]}%</small>
                  </li>
                ))}
              </ul>
            </article>

            <article className="lp-tile t3">
              <h3>Keep a daily streak</h3>
              <p>Your profile shows streaks, XP levels, badges and a heatmap of every day you practiced.</p>
              <div className="lp-heat">
                <Heatmap activity={activity} today={dayKey(now)} bare />
              </div>
            </article>

            <article className="lp-tile t2">
              <h3>Race the clock</h3>
              <p>
                A virtual contest: {CONTEST_MINUTES} minutes, four problems, a penalty for each wrong try.
              </p>
              <div className="lp-clock tnum" aria-hidden="true">
                {clock(CONTEST_MINUTES * 60_000)}
              </div>
              <ol className="lp-rounds">
                {contestIds.map((id, k) => {
                  const p = BY_ID.get(id)!;
                  return (
                    <li key={id}>
                      <span className="lp-letter">{String.fromCharCode(65 + k)}</span>
                      <span className="lp-rt">{p.title}</span>
                      <Pill diff={p.diff} />
                      <small className="tnum">{POINTS[p.diff]} pts</small>
                    </li>
                  );
                })}
              </ol>
            </article>

            <article className="lp-tile t2">
              <h3>Stuck? Open one hint at a time</h3>
              <p>Three hints per problem, from a small nudge to the key idea. You decide how far to go.</p>
              <ol className="lp-hints">
                <li className="open">
                  <b>Hint 1</b>
                  <Rich as="span" html={hint} />
                </li>
                <li>
                  <b>Hint 2</b>
                  <span>Closed until you open it</span>
                </li>
                <li>
                  <b>Hint 3</b>
                  <span>Closed until you open it</span>
                </li>
              </ol>
            </article>

            <article className="lp-tile t2">
              <h3>Run it your way</h3>
              <p>Python and JavaScript run on your device. C++ and Java are compiled by a Judge0 server you can change. Try any input with Custom input.</p>
              <div className="lp-langs">
                <span>Python</span>
                <span>JavaScript</span>
                <span>C++</span>
                <span>Java</span>
              </div>
            </article>
          </div>
          <div className="chips lp-extras" aria-label="Also included">
            {['Editorials with Big-O', 'Hidden and large tests', 'Submission history', 'Notes and stars', 'Daily challenge', 'Export your progress', 'Light and dark theme'].map((t) => (
              <span className="chip" key={t}>
                {t}
              </span>
            ))}
          </div>
        </section>

      <section className="lp-sec" id="faq">
        <h2>Questions</h2>
        <div className="faq" style={{ marginTop: 24 }}>
          <details>
            <summary>Is it really free?</summary>
            <p>Yes. Every problem, hint, editorial and solution is open. There is no paid tier and nothing is locked.</p>
          </details>
          <details>
            <summary>Do I need an account?</summary>
            <p>
              {CLOUD_ENABLED
                ? 'No. Without one, progress and code stay in this browser. A free account adds cloud saving so you can switch devices.'
                : 'No. Your progress and code are saved in this browser. You can export them from your profile and import them anywhere.'}
            </p>
          </details>
          <details>
            <summary>How is my code run?</summary>
            <p>Python runs through Pyodide and JavaScript in a Web Worker, both inside your browser. C++ and Java are compiled by a Judge0 server, which is an open-source online judge.</p>
          </details>
          <details>
            <summary>Are the test cases the same as on other sites?</summary>
            <p>No. The problems are classics, but the statements, tests and solutions here are written for {BRAND}.</p>
          </details>
          <details>
            <summary>Can I use it offline?</summary>
            <p>JavaScript works offline once the page has loaded. Python needs to download its runtime once, and C++ and Java need a connection to the judge server.</p>
          </details>
        </div>
      </section>

        <section className="lp-cta-band">
          <h2>Pick a problem and run your first test.</h2>
          <Link className="lp-btn light" to={{ name: 'problems' }}>
            Start solving
          </Link>
        </section>
      </div>

      <footer className="site-foot lp-wrap">
        <div>
          <b style={{ color: 'var(--ink)' }}>{BRAND}</b>
          <br />
          Free DSA practice. &copy; {new Date().getFullYear()}
        </div>
        <nav aria-label="Footer">
          <Link to={{ name: 'problems' }}>Problems</Link>
          <Link to={{ name: 'plans' }}>Study plans</Link>
          <Link to={{ name: 'contest' }}>Contest</Link>
          <SectionLink id="topics">Topics</SectionLink>
          <SectionLink id="faq">FAQ</SectionLink>
        </nav>
        <div>
          Code runs on{' '}
          <a href="https://pyodide.org" target="_blank" rel="noopener noreferrer">
            Pyodide
          </a>{' '}
          and{' '}
          <a href="https://judge0.com" target="_blank" rel="noopener noreferrer">
            Judge0
          </a>
          .
        </div>
      </footer>
    </div>
  );
}
