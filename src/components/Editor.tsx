import { useEffect, useLayoutEffect, useMemo, useRef, useState, type CSSProperties } from 'react';
import { handleEditorKey } from '../core/editorKeys';
import type { Lang } from '../types';
import { Highlighted } from './Highlighted';

interface Props {
  value: string;
  lang: Lang;
  fontSize: number;
  onChange(code: string): void;
  onRun(): void;
  onSubmit(): void;
}

/* A textarea (for typing, selection, undo and accessibility) with a coloured copy of the code drawn behind it. */
export function Editor({ value, lang, fontSize, onChange, onRun, onSubmit }: Props) {
  const ta = useRef<HTMLTextAreaElement>(null);
  const hl = useRef<HTMLPreElement>(null);
  const gutter = useRef<HTMLPreElement>(null);
  const [pos, setPos] = useState({ ln: 1, col: 1 });

  // Always call the latest handlers from the native key listener.
  const actions = useRef({ lang, run: onRun, submit: onSubmit });
  actions.current = { lang, run: onRun, submit: onSubmit };

  const lines = useMemo(() => {
    const n = value.split('\n').length;
    return Array.from({ length: n }, (_, i) => i + 1).join('\n');
  }, [value]);

  const syncScroll = () => {
    const t = ta.current;
    if (!t) return;
    if (hl.current) {
      hl.current.scrollTop = t.scrollTop;
      hl.current.scrollLeft = t.scrollLeft;
    }
    if (gutter.current) gutter.current.scrollTop = t.scrollTop;
  };
  useLayoutEffect(syncScroll, [value, fontSize]);

  const updatePos = () => {
    const t = ta.current;
    if (!t) return;
    const upto = t.value.slice(0, t.selectionStart).split('\n');
    setPos({ ln: upto.length, col: (upto[upto.length - 1]?.length ?? 0) + 1 });
  };

  useEffect(() => {
    const t = ta.current;
    if (!t) return;
    const onKey = (e: KeyboardEvent) => {
      handleEditorKey(e, t, actions.current);
    };
    t.addEventListener('keydown', onKey);
    return () => t.removeEventListener('keydown', onKey);
  }, []);

  return (
    <>
      <div className="editor" style={{ '--ed-fs': `${fontSize}px` } as CSSProperties}>
        <pre className="gutter" ref={gutter} aria-hidden="true">
          {lines}
        </pre>
        <div className="stack">
          <pre className="hl" ref={hl} aria-hidden="true">
            <Highlighted code={value} lang={lang} />
            {'\n'}
          </pre>
          <textarea
            ref={ta}
            value={value}
            spellCheck={false}
            autoCapitalize="off"
            autoComplete="off"
            autoCorrect="off"
            wrap="off"
            aria-label="Code editor"
            onChange={(e) => {
              onChange(e.target.value);
              updatePos();
            }}
            onScroll={syncScroll}
            onKeyUp={updatePos}
            onClick={updatePos}
            onFocus={updatePos}
          />
        </div>
      </div>
      <div className="ed-status">
        <span>
          Ln {pos.ln}, Col {pos.col}
        </span>
        <span className="grow" />
        <span>4 spaces</span>
      </div>
    </>
  );
}
