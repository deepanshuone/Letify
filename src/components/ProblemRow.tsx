import { CheckIcon, Link, Pill } from './common';
import type { Problem } from '../types';

export function ProblemRow({ p, number, done, starred }: { p: Problem; number?: number; done: boolean; starred?: boolean }) {
  return (
    <Link className="row" to={{ name: 'problem', id: p.id }}>
      <span className={`dot${done ? ' done' : ''}`} title={done ? 'Solved' : 'Not solved yet'}>
        {done && <CheckIcon />}
      </span>
      <span className="t">
        <b>
          {number !== undefined ? `${number}. ` : ''}
          {p.title}
          {starred && (
            <span className="star-mark" title="Starred" aria-label="Starred">
              {' '}
              &#9733;
            </span>
          )}
        </b>
        <small>
          {p.fn}({p.params.map((x) => x[0]).join(', ')})
        </small>
      </span>
      <span className="topic muted">{p.topic}</span>
      <span>
        <Pill diff={p.diff} />
      </span>
    </Link>
  );
}
