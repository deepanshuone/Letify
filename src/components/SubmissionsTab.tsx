import { fmtMs, timeAgo } from '../core/format';
import { LANGS } from '../core/languages';
import type { Lang } from '../types';
import type { Submission } from '../user/model';

const TEXT = { ac: 'Accepted', wa: 'Wrong Answer', re: 'Runtime Error', tle: 'Time Limit', ce: 'Compile Error' } as const;

export function SubmissionsTab({ subs, onRestore }: { subs: Submission[]; onRestore(lang: Lang, code: string): void }) {
  if (subs.length === 0) return <p className="muted">No submissions for this problem yet. Press Submit to check your code against every test case, and it will be listed here.</p>;
  return (
    <ul className="subs">
      {subs.map((s) => (
        <li key={s.id}>
          <details>
            <summary>
              <span className={`vtag ${s.verdict}`}>{TEXT[s.verdict]}</span>
              <span>{LANGS[s.lang].label}</span>
              <span className="muted tnum">
                {s.passed}/{s.total}
              </span>
              <span className="muted tnum">{fmtMs(s.ms)}</span>
              <span className="muted sub-when">{timeAgo(s.at)}</span>
            </summary>
            <pre className="block">{s.code}</pre>
            <p style={{ margin: '8px 0 0' }}>
              <button className="btn sm" onClick={() => onRestore(s.lang, s.code)}>
                Restore this code in the editor
              </button>
            </p>
          </details>
        </li>
      ))}
    </ul>
  );
}
