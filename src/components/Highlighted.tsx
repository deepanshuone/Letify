import { memo } from 'react';
import { tokenize } from '../core/highlight';
import type { Lang } from '../types';

/** Source code with syntax colours. Built from text nodes and spans, never from raw HTML. */
export const Highlighted = memo(function Highlighted({ code, lang }: { code: string; lang: Lang }) {
  return (
    <>
      {tokenize(code, lang).map((t, i) =>
        t.cls ? (
          <span key={i} className={`tk-${t.cls}`}>
            {t.text}
          </span>
        ) : (
          <span key={i}>{t.text}</span>
        ),
      )}
    </>
  );
});
