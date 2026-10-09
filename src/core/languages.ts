import type { Lang, PType, Problem } from '../types';

export const LANGS: Record<Lang, { label: string }> = {
  python: { label: 'Python' },
  javascript: { label: 'JavaScript' },
  cpp: { label: 'C++' },
  java: { label: 'Java' },
};

export const LANG_IDS = Object.keys(LANGS) as Lang[];

export function isLang(x: unknown): x is Lang {
  return typeof x === 'string' && Object.prototype.hasOwnProperty.call(LANGS, x);
}

/** Judge0 CE language ids. */
export const JUDGE0_IDS = { cpp: 54, java: 62 } as const;

export const TYPE: Record<'py' | 'js' | 'cpp' | 'java', Record<PType, string>> = {
  py: { int: 'int', bool: 'bool', string: 'str', 'int[]': 'list[int]', 'int[][]': 'list[list[int]]' },
  js: { int: 'number', bool: 'boolean', string: 'string', 'int[]': 'number[]', 'int[][]': 'number[][]' },
  cpp: { int: 'int', bool: 'bool', string: 'string', 'int[]': 'vector<int>', 'int[][]': 'vector<vector<int>>' },
  java: { int: 'int', bool: 'boolean', string: 'String', 'int[]': 'int[]', 'int[][]': 'int[][]' },
};

const isArrayType = (t: PType) => t.endsWith(']');

/** Starter code for a problem in a language. */
export function starter(p: Pick<Problem, 'fn' | 'params' | 'ret'>, lang: Lang): string {
  const ps = p.params;
  if (lang === 'python') {
    const sig = ps.map(([n, t]) => `${n}: ${TYPE.py[t]}`).join(', ');
    return `def ${p.fn}(${sig}) -> ${TYPE.py[p.ret]}:\n    # Write your solution here\n    pass\n`;
  }
  if (lang === 'javascript') {
    const doc = ps.map(([n, t]) => ` * @param {${TYPE.js[t]}} ${n}`).join('\n');
    return `/**\n${doc}\n * @return {${TYPE.js[p.ret]}}\n */\nfunction ${p.fn}(${ps.map(([n]) => n).join(', ')}) {\n  // Write your solution here\n}\n`;
  }
  if (lang === 'cpp') {
    const sig = ps.map(([n, t]) => `${TYPE.cpp[t]}${isArrayType(t) ? '& ' : ' '}${n}`).join(', ');
    return `class Solution {\npublic:\n    ${TYPE.cpp[p.ret]} ${p.fn}(${sig}) {\n        // Write your solution here\n    }\n};\n`;
  }
  const sig = ps.map(([n, t]) => `${TYPE.java[t]} ${n}`).join(', ');
  return `class Solution {\n    public ${TYPE.java[p.ret]} ${p.fn}(${sig}) {\n        // Write your solution here\n    }\n}\n`;
}
