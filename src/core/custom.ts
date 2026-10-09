import type { PType, Value } from '../types';

/* Parsing of the "custom input" box: one JSON value per parameter, checked against the parameter type. */

const INT_MIN = -(2 ** 31);
const INT_MAX = 2 ** 31 - 1;
const isInt = (x: unknown): x is number => typeof x === 'number' && Number.isInteger(x) && x >= INT_MIN && x <= INT_MAX;
const MAX_ITEMS = 20_000;

export function parseArg(text: string, type: PType): { ok: true; value: Value } | { ok: false; error: string } {
  let v: unknown;
  try {
    v = JSON.parse(text);
  } catch {
    return { ok: false, error: 'This is not valid JSON. Example: ' + example(type) };
  }
  switch (type) {
    case 'int':
      return isInt(v) ? { ok: true, value: v } : { ok: false, error: 'Expected a whole number between -2147483648 and 2147483647.' };
    case 'bool':
      return typeof v === 'boolean' ? { ok: true, value: v } : { ok: false, error: 'Expected true or false.' };
    case 'string':
      if (typeof v !== 'string') return { ok: false, error: 'Expected a string in double quotes, like "abc".' };
      if (/[\s"\\]/.test(v)) return { ok: false, error: 'Spaces, quotes and backslashes are not allowed in strings here.' };
      return { ok: true, value: v };
    case 'int[]':
      if (!Array.isArray(v) || !v.every(isInt)) return { ok: false, error: 'Expected a list of whole numbers, like [1, 2, 3].' };
      return v.length > MAX_ITEMS ? { ok: false, error: `At most ${MAX_ITEMS} numbers.` } : { ok: true, value: v };
    case 'int[][]':
      if (!Array.isArray(v) || !v.every((r) => Array.isArray(r) && r.every(isInt))) return { ok: false, error: 'Expected a list of lists of whole numbers, like [[1, 2], [3]].' };
      return (v as number[][]).reduce((a, r) => a + r.length + 1, 0) > MAX_ITEMS ? { ok: false, error: `At most ${MAX_ITEMS} numbers.` } : { ok: true, value: v as number[][] };
  }
}

export function example(type: PType): string {
  return { int: '5', bool: 'true', string: '"abc"', 'int[]': '[1, 2, 3]', 'int[][]': '[[1, 2], [3, 4]]' }[type];
}
