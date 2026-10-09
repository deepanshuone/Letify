import { describe, expect, it } from 'vitest';
import { validJudge0Url } from '../src/components/EngineSettings';
import { parseHash, hrefFor } from '../src/router';

describe('Judge0 URL validation', () => {
  it('accepts https and local development servers', () => {
    expect(validJudge0Url('https://judge.example.org/')).toBe('https://judge.example.org');
    expect(validJudge0Url('https://judge.example.org/api/')).toBe('https://judge.example.org/api');
    expect(validJudge0Url('http://localhost:2358')).toBe('http://localhost:2358');
  });
  it('refuses plain http to the internet, other schemes and junk', () => {
    expect(validJudge0Url('http://judge.example.org')).toBeNull();
    expect(validJudge0Url('javascript:alert(1)')).toBeNull();
    expect(validJudge0Url('ftp://x.org')).toBeNull();
    expect(validJudge0Url('not a url')).toBeNull();
  });
});

describe('routes', () => {
  it('parses current and older links', () => {
    expect(parseHash('')).toEqual({ name: 'landing' });
    expect(parseHash('#/')).toEqual({ name: 'landing' });
    expect(parseHash('#/problems')).toEqual({ name: 'problems' });
    expect(parseHash('#problems')).toEqual({ name: 'problems' });
    expect(parseHash('#/problem/two-sum')).toEqual({ name: 'problem', id: 'two-sum' });
    expect(parseHash('#two-sum')).toEqual({ name: 'problem', id: 'two-sum' });
    expect(parseHash('#/problem/nope')).toEqual({ name: 'landing' });
  });
  it('round-trips', () => {
    for (const r of [{ name: 'landing' }, { name: 'problems' }, { name: 'problem', id: '3sum' }] as const) {
      expect(parseHash(hrefFor(r))).toEqual(r);
    }
  });
});
