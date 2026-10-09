import { useEffect } from 'react';
import { BRAND, CLOUD_ENABLED } from '../config';
import { Link, Pill, SectionLink } from '../components/common';
import { Highlighted } from '../components/Highlighted';
import { BY_ID, PROBLEMS, TOPICS } from '../data';
import { PLANS } from '../data/plans';
import { navigate, takePendingSection } from '../router';
import { useFilters } from '../state/filters';
import { STAGES } from './stages';

export function Landing() {
  const { setFilters } = useFilters();
  const demo = BY_ID.get('two-sum') ?? PROBLEMS[0]!;
  const total = PROBLEMS.length;
  const tests = PROBLEMS.reduce((a, p) => a + p.testCount, 0);
  const hidden = PROBLEMS.reduce((a, p) => a + p.testCount - p.visible, 0);

  useEffect(() => {
    const id = takePendingSection();
    if (id) requestAnimationFrame(() => document.getElementById(id)?.scrollIntoView({ behavior: 'smooth', block: 'start' }));
  }, []);

  const openStage = (diff: (typeof STAGES)[number]['diff']) => {
    setFilters({ diff });
    navigate({ name: 'problems' });
  };

  return (
    <div id="landing">
      <section className="hero">
        <div>
          <span className="eyebrow">Free. Every feature unlocked.</span>
          <h1>Practice data structures and algorithms until they click.</h1>
          <p className="lede">
            {BRAND} gives you {total} problems, from your first hash map to hard dynamic programming. Write code in Python, JavaScript, C++ or Java and get judged on hidden test cases.
          </p>
          <div className="hero-cta">
            <Link className="btn primary lg" to={{ name: 'problems' }}>
              Start practicing
            </Link>
            <Link className="btn lg" to={{ name: 'plans' }}>
              Study plans
            </Link>
          </div>
          <p className="hero-note">Python and JavaScript run in your browser, so there is nothing to install.</p>
        </div>
        <div className="demo" aria-label="Example of a solved problem">
          <div className="demo-bar">
            <span>two_sum.py</span>
            <Pill diff="Easy" />
          </div>
          <pre className="code">
            <Highlighted code={demo.solution} lang="python" />
          </pre>
          <div className="demo-res">
            <b>Accepted</b>
            <span className="muted tnum">
              {demo.testCount} of {demo.testCount} test cases passed
            </span>
            <span className="chip big">Time {demo.time}</span>
            <span className="chip big">Space {demo.space}</span>
          </div>
        </div>
      </section>

      <div className="statline" role="list">
        <div role="listitem">
          <b className="tnum">{total}</b>
          <span>problems, Easy to Hard</span>
        </div>
        <div role="listitem">
          <b className="tnum">{tests}</b>
          <span>test cases, {hidden} of them hidden</span>
        </div>
        <div role="listitem">
          <b className="tnum">4</b>
          <span>languages</span>
        </div>
        <div role="listitem">
          <b className="tnum">{PLANS.length}</b>
          <span>study plans</span>
        </div>
        <div role="listitem">
          <b className="tnum">0</b>
          <span>locked problems</span>
        </div>
      </div>

      <section className="sec" id="how">
        <h2>How a session works</h2>
        <p className="sec-lede">The loop is the same on every problem, so you can focus on the idea instead of the tool.</p>
        <ol className="steps">
          <li>
            <h3>Pick a problem</h3>
            <p>Start with Easy or jump to a topic. Each problem lists its constraints and worked examples.</p>
          </li>
          <li>
            <h3>Write, run, submit</h3>
            <p>Run against the samples first, then submit against hidden and large inputs. Slow solutions time out, just as they would in an interview.</p>
          </li>
          <li>
            <h3>Learn from the result</h3>
            <p>Stuck? Open hints one at a time. Solved? Read the editorial to compare approaches and complexity.</p>
          </li>
        </ol>
      </section>

      <section className="sec" id="features">
        <h2>Everything is included</h2>
        <p className="sec-lede">The parts other sites keep behind a subscription are part of every problem here.</p>
        <div className="feats">
          <div className="feat">
            <h3>Hidden and large test cases</h3>
            <p>Edge cases, empty inputs and stress tests catch brute-force solutions that only pass the examples.</p>
          </div>
          <div className="feat">
            <h3>Hints that do not spoil</h3>
            <p>Three hints per problem, from a gentle nudge to the key idea. You choose how many to reveal.</p>
          </div>
          <div className="feat">
            <h3>Editorials with Big-O</h3>
            <p>A written explanation of the approach, its time and space complexity, and a reference solution.</p>
          </div>
          <div className="feat">
            <h3>Four languages</h3>
            <p>Python, JavaScript, C++ and Java, each with starter code in the right signature.</p>
          </div>
          <div className="feat">
            <h3>Runs in your browser</h3>
            <p>Python and JavaScript execute locally. C++ and Java are compiled on a Judge0 server you can change.</p>
          </div>
          <div className="feat">
            <h3>Study plans</h3>
            <p>Guided paths such as arrays first, then graphs and dynamic programming, with a progress bar for each plan.</p>
          </div>
          <div className="feat">
            <h3>Profile, streaks and badges</h3>
            <p>An activity heatmap, daily streak, XP levels and badges show how much you practiced, in the spirit of HackerRank and CodeChef.</p>
          </div>
          <div className="feat">
            <h3>Daily challenge</h3>
            <p>One problem a day, the same for everyone, so there is always an easy place to start.</p>
          </div>
          <div className="feat">
            <h3>Timed contests</h3>
            <p>Four problems, 90 minutes, points and time penalties like a real contest. Hints close until it ends.</p>
          </div>
          <div className="feat">
            <h3>Submissions, notes and stars</h3>
            <p>Every submission is kept with its code. Write private notes and star the problems you want to revisit.</p>
          </div>
          <div className="feat">
            <h3>Custom input</h3>
            <p>Run your code on any input you type and see what it returns, without an expected answer in the way.</p>
          </div>
          <div className="feat">
            <h3>{CLOUD_ENABLED ? 'Sync across devices' : 'Your progress stays with you'}</h3>
            <p>
              {CLOUD_ENABLED
                ? 'Create a free account and your progress, submissions and code follow you to any device. You can also export everything as a file.'
                : 'Progress and code are saved in your browser. Export them as a file any time, and import them on another device.'}
            </p>
          </div>
        </div>
      </section>

      <section className="sec" id="stages">
        <h2>A path from basic to advanced</h2>
        <p className="sec-lede">Three stages, each building on the last. Choose one to see its problems.</p>
        <div className="stages" style={{ marginBlock: '0 20px' }}>
          {STAGES.map((s) => {
            const n = PROBLEMS.filter((p) => p.diff === s.diff).length;
            return (
              <a
                key={s.diff}
                className="stage"
                href="#/problems"
                onClick={(e) => {
                  e.preventDefault();
                  openStage(s.diff);
                }}
              >
                <h3>{s.name}</h3>
                <div className="sub">{s.blurb}</div>
                <div className="meta tnum">
                  <span>{s.diff}</span>
                  <span>{n} problems</span>
                </div>
              </a>
            );
          })}
        </div>
        <div className="chips" aria-label="Topics covered">
          {TOPICS.map((t) => (
            <span className="chip" key={t}>
              {t}
            </span>
          ))}
        </div>
      </section>

      <section className="sec" id="faq">
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

      <section className="cta-band">
        <h2>Pick your first problem.</h2>
        <Link className="btn primary lg" to={{ name: 'problems' }}>
          Start practicing
        </Link>
      </section>

      <footer className="site-foot">
        <div>
          <b style={{ color: 'var(--ink)' }}>{BRAND}</b>
          <br />
          Free DSA practice. &copy; {new Date().getFullYear()}
        </div>
        <nav aria-label="Footer">
          <Link to={{ name: 'problems' }}>Problems</Link>
          <Link to={{ name: 'plans' }}>Study plans</Link>
          <Link to={{ name: 'contest' }}>Contest</Link>
          <SectionLink id="stages">Roadmap</SectionLink>
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
