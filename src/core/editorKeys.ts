import type { Lang } from '../types';

/* Keyboard behaviour of the code editor: auto-close brackets and quotes, smart indent, Tab / Shift+Tab, comment toggle.
   Edits go through document.execCommand where possible so the browser's own undo/redo keeps working. */

function insertText(ta: HTMLTextAreaElement, text: string): void {
  ta.focus();
  let ok = false;
  try {
    ok = document.execCommand('insertText', false, text);
  } catch {
    /* not supported */
  }
  if (!ok) {
    ta.setRangeText(text, ta.selectionStart, ta.selectionEnd, 'end');
    ta.dispatchEvent(new Event('input', { bubbles: true }));
  }
}

function deleteRange(ta: HTMLTextAreaElement, s: number, e: number): void {
  ta.setSelectionRange(s, e);
  let ok = false;
  try {
    ok = document.execCommand('delete');
  } catch {
    /* not supported */
  }
  if (!ok) {
    ta.setRangeText('', s, e, 'end');
    ta.dispatchEvent(new Event('input', { bubbles: true }));
  }
}

const PAIRS: Record<string, string> = { '(': ')', '[': ']', '{': '}', '"': '"', "'": "'", '`': '`' };
const CLOSERS = new Set([')', ']', '}', '"', "'", '`']);

function lineBounds(ta: HTMLTextAreaElement): { ls: number; le: number } {
  const v = ta.value;
  const s = ta.selectionStart;
  const e = ta.selectionEnd;
  const ls = v.lastIndexOf('\n', s - 1) + 1;
  let le = v.indexOf('\n', e);
  if (le < 0) le = v.length;
  if (e > s && v.charAt(e - 1) === '\n') le = e - 1;
  return { ls, le };
}

function indentSelection(ta: HTMLTextAreaElement, outdent: boolean): void {
  const s = ta.selectionStart;
  const e = ta.selectionEnd;
  if (s === e && !outdent) {
    insertText(ta, '    ');
    return;
  }
  const b = lineBounds(ta);
  const lines = ta.value.slice(b.ls, b.le).split('\n');
  let first = 0;
  let total = 0;
  const res = lines.map((l, i) => {
    if (outdent) {
      const m = l.match(/^( {1,4}|\t)/);
      const d = m ? m[0].length : 0;
      if (i === 0) first = -Math.min(d, s - b.ls);
      total -= d;
      return l.slice(d);
    }
    if (i === 0) first = 4;
    total += 4;
    return '    ' + l;
  });
  ta.setSelectionRange(b.ls, b.le);
  insertText(ta, res.join('\n'));
  ta.setSelectionRange(Math.max(b.ls, s + first), e + total);
}

function toggleComment(ta: HTMLTextAreaElement, lang: Lang): void {
  const mark = lang === 'python' ? '#' : '//';
  const b = lineBounds(ta);
  const lines = ta.value.slice(b.ls, b.le).split('\n');
  const allCommented = lines.every((l) => !l.trim() || l.trim().startsWith(mark));
  const res = lines
    .map((l) => {
      if (!l.trim()) return l;
      const ind = l.match(/^\s*/)![0];
      const rest = l.slice(ind.length);
      return allCommented ? ind + rest.replace(new RegExp('^' + mark + ' ?'), '') : `${ind}${mark} ${rest}`;
    })
    .join('\n');
  ta.setSelectionRange(b.ls, b.le);
  insertText(ta, res);
  ta.setSelectionRange(b.ls, b.ls + res.length);
}

export interface EditorActions {
  lang: Lang;
  run(): void;
  submit(): void;
}

/** Handle a keydown in the editor textarea. Returns true when the key was consumed. */
export function handleEditorKey(e: KeyboardEvent, ta: HTMLTextAreaElement, a: EditorActions): boolean {
  const v = ta.value;
  const s = ta.selectionStart;
  const en = ta.selectionEnd;
  const mod = e.ctrlKey || e.metaKey;

  if (mod && e.key === 'Enter') {
    e.preventDefault();
    if (e.shiftKey) a.submit();
    else a.run();
    return true;
  }
  if (mod && e.key === '/') {
    e.preventDefault();
    toggleComment(ta, a.lang);
    return true;
  }
  if (e.key === 'Tab' && !mod) {
    e.preventDefault();
    indentSelection(ta, e.shiftKey);
    return true;
  }
  if (mod || e.altKey) return false;

  const prev = v.charAt(s - 1);
  const next = v.charAt(s);

  if (e.key === 'Enter' && !e.shiftKey) {
    const ls = v.lastIndexOf('\n', s - 1) + 1;
    const line = v.slice(ls, s);
    const indent = (line.match(/^[ \t]*/) ?? [''])[0];
    const t = line.replace(/\s+$/, '');
    const opens = /[{[(]$/.test(t) || (a.lang === 'python' && t.endsWith(':'));
    if (opens && PAIRS[prev] && PAIRS[prev] === next && prev !== '"' && prev !== "'") {
      e.preventDefault();
      insertText(ta, '\n' + indent + '    \n' + indent);
      const pos = s + 1 + indent.length + 4;
      ta.setSelectionRange(pos, pos);
      return true;
    }
    if (indent || opens) {
      e.preventDefault();
      insertText(ta, '\n' + indent + (opens ? '    ' : ''));
      return true;
    }
    return false;
  }

  if (e.key === 'Backspace' && s === en && s > 0 && PAIRS[prev] && PAIRS[prev] === next) {
    e.preventDefault();
    deleteRange(ta, s - 1, s + 1);
    return true;
  }

  const k = e.key;
  if (k.length !== 1) return false;
  if (CLOSERS.has(k) && next === k && s === en) {
    e.preventDefault();
    ta.setSelectionRange(s + 1, s + 1);
    return true;
  }
  if (PAIRS[k] && (k !== '`' || a.lang === 'javascript')) {
    if (s !== en) {
      e.preventDefault();
      const sel = v.slice(s, en);
      insertText(ta, k + sel + PAIRS[k]);
      ta.setSelectionRange(s + 1, s + 1 + sel.length);
      return true;
    }
    const quote = k === '"' || k === "'" || k === '`';
    const okNext = next === '' || /[\s)\]},;:]/.test(next);
    const okPrev = !quote || !/\w/.test(prev);
    if (okNext && okPrev) {
      e.preventDefault();
      insertText(ta, k + PAIRS[k]);
      ta.setSelectionRange(s + 1, s + 1);
      return true;
    }
  }
  return false;
}
