import { describe, expect, it } from 'vitest';
import { parseArg } from '../src/core/custom';

describe('custom input parsing', () => {
  it('accepts valid values of every type', () => {
    expect(parseArg('5', 'int')).toEqual({ ok: true, value: 5 });
    expect(parseArg('-2147483648', 'int')).toMatchObject({ ok: true });
    expect(parseArg('true', 'bool')).toEqual({ ok: true, value: true });
    expect(parseArg('""', 'string')).toEqual({ ok: true, value: '' });
    expect(parseArg('"abc"', 'string')).toEqual({ ok: true, value: 'abc' });
    expect(parseArg('[]', 'int[]')).toEqual({ ok: true, value: [] });
    expect(parseArg(' [1, -2 , 3] ', 'int[]')).toEqual({ ok: true, value: [1, -2, 3] });
    expect(parseArg('[[1],[],[2,3]]', 'int[][]')).toEqual({ ok: true, value: [[1], [], [2, 3]] });
  });
  it('rejects wrong shapes with a readable message', () => {
    for (const [t, ty] of [['abc', 'int'], ['1.5', 'int'], ['2147483648', 'int'], ['1', 'bool'], ['5', 'string'], ['"a b"', 'string'], ['"a\\"b"', 'string'], ['[1.5]', 'int[]'], ['["1"]', 'int[]'], ['[1]', 'int[][]'], ['{"a":1}', 'int[]'], ['', 'int']] as const) {
      const r = parseArg(t, ty);
      expect(r.ok, `${ty} ${t}`).toBe(false);
      if (!r.ok) expect(r.error.length).toBeGreaterThan(5);
    }
  });
  it('limits the size', () => {
    expect(parseArg(JSON.stringify(Array(20_001).fill(1)), 'int[]').ok).toBe(false);
  });
});
