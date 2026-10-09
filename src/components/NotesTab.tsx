import { useEffect, useRef, useState } from 'react';
import { LIMITS } from '../user/model';

/* Private notes, saved while you type. */
export function NotesTab({ value, onSave }: { value: string; onSave(text: string): void }) {
  const [text, setText] = useState(value);
  const timer = useRef<ReturnType<typeof setTimeout> | undefined>(undefined);
  const saved = useRef(value);
  const latest = useRef({ text, onSave });
  latest.current = { text, onSave };
  const save = (t: string) => {
    if (t === saved.current) return;
    saved.current = t;
    latest.current.onSave(t);
  };
  useEffect(
    () => () => {
      clearTimeout(timer.current);
      save(latest.current.text);
    },
    [], // eslint-disable-line react-hooks/exhaustive-deps
  );
  return (
    <>
      <p className="muted">Write down the idea, the trap, or what you would do differently. Only you can see this.</p>
      <textarea
        className="notes"
        aria-label="Notes for this problem"
        placeholder="For example: sort first, then two pointers. Watch out for duplicates."
        maxLength={LIMITS.note}
        value={text}
        onChange={(e) => {
          setText(e.target.value);
          clearTimeout(timer.current);
          const v = e.target.value;
          timer.current = setTimeout(() => save(v), 600);
        }}
        onBlur={() => {
          clearTimeout(timer.current);
          save(text);
        }}
      />
    </>
  );
}
