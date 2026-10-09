import { isLang } from '../core/languages';
import type { Lang } from '../types';

/*
 * Everything the site remembers about a learner. One plain object that is saved in this browser and, when the
 * visitor signs in, in the cloud. Every entry carries a timestamp so two copies (for example a phone and a laptop)
 * can always be merged without losing work: see merge().
 */

export type SubVerdict = 'ac' | 'wa' | 're' | 'tle' | 'ce';
const SUB_VERDICTS: readonly string[] = ['ac', 'wa', 're', 'tle', 'ce'];

export interface Submission {
  id: string;
  pid: string;
  lang: Lang;
  verdict: SubVerdict;
  passed: number;
  total: number;
  ms: number;
  at: number;
  code: string;
}

export interface ContestResult {
  id: string;
  /** Start and end of the contest window, ms since epoch. */
  start: number;
  end: number;
  ids: string[];
  /** Problem id -> time of the accepted submission. */
  solved: Record<string, number>;
  /** Problem id -> wrong attempts before the accepted one (or in total when never solved). */
  wrong: Record<string, number>;
  score: number;
  /** Penalty minutes. */
  penalty: number;
}

export interface UserData {
  v: 1;
  solved: Record<string, { lang: Lang; at: number }>;
  subs: Submission[];
  notes: Record<string, { text: string; at: number }>;
  stars: Record<string, { on: boolean; at: number }>;
  code: Record<string, { text: string; at: number }>;
  contests: Record<string, ContestResult>;
}

export const LIMITS = {
  code: 60_000,
  subCode: 20_000,
  note: 20_000,
  subsPerProblem: 20,
  subs: 300,
  contests: 100,
  keys: 2_000,
} as const;

export const emptyData = (): UserData => ({ v: 1, solved: {}, subs: [], notes: {}, stars: {}, code: {}, contests: {} });

export const codeKey = (pid: string, lang: Lang) => `${pid}.${lang}`;

const isObj = (x: unknown): x is Record<string, unknown> => typeof x === 'object' && x !== null && !Array.isArray(x);
const num = (x: unknown, d = 0) => (typeof x === 'number' && Number.isFinite(x) ? x : d);
const str = (x: unknown, max: number) => (typeof x === 'string' ? x.slice(0, max) : '');
const safeKey = (k: string) => k.length > 0 && k.length <= 120 && k !== '__proto__' && k !== 'constructor' && k !== 'prototype';

function entries(x: unknown): [string, Record<string, unknown>][] {
  if (!isObj(x)) return [];
  return Object.entries(x)
    .filter(([k, v]) => safeKey(k) && isObj(v))
    .slice(0, LIMITS.keys) as [string, Record<string, unknown>][];
}

function normSub(x: unknown): Submission | null {
  if (!isObj(x)) return null;
  const id = str(x.id, 80);
  const pid = str(x.pid, 120);
  if (!id || !pid || !safeKey(pid) || !isLang(x.lang) || !SUB_VERDICTS.includes(x.verdict as string)) return null;
  return {
    id,
    pid,
    lang: x.lang,
    verdict: x.verdict as SubVerdict,
    passed: num(x.passed),
    total: num(x.total),
    ms: num(x.ms),
    at: num(x.at),
    code: str(x.code, LIMITS.subCode),
  };
}

function normContest(x: Record<string, unknown>, id: string): ContestResult {
  const mapNum = (m: unknown) => Object.fromEntries(entries(Object.fromEntries(Object.entries(isObj(m) ? m : {}).map(([k, v]) => [k, { n: v }]))).map(([k, v]) => [k, num(v.n)]));
  return {
    id,
    start: num(x.start),
    end: num(x.end),
    ids: Array.isArray(x.ids) ? x.ids.filter((s): s is string => typeof s === 'string' && safeKey(s)).slice(0, 12) : [],
    solved: mapNum(x.solved),
    wrong: mapNum(x.wrong),
    score: num(x.score),
    penalty: num(x.penalty),
  };
}

/** Turn anything read from storage, the cloud or an import file into a valid UserData. Never throws. */
export function normalize(raw: unknown): UserData {
  const out = emptyData();
  if (!isObj(raw)) return out;
  for (const [k, v] of entries(raw.solved)) if (isLang(v.lang)) out.solved[k] = { lang: v.lang, at: num(v.at) };
  if (Array.isArray(raw.subs)) {
    const seen = new Set<string>();
    for (const s of raw.subs.slice(0, LIMITS.subs * 2)) {
      const n = normSub(s);
      if (n && !seen.has(n.id)) {
        seen.add(n.id);
        out.subs.push(n);
      }
    }
  }
  for (const [k, v] of entries(raw.notes)) out.notes[k] = { text: str(v.text, LIMITS.note), at: num(v.at) };
  for (const [k, v] of entries(raw.stars)) out.stars[k] = { on: v.on === true, at: num(v.at) };
  for (const [k, v] of entries(raw.code)) out.code[k] = { text: str(v.text, LIMITS.code), at: num(v.at) };
  for (const [k, v] of entries(raw.contests).slice(0, LIMITS.contests)) out.contests[k] = normContest(v, k);
  out.subs = capSubs(out.subs);
  return out;
}

/** Newest first; at most 20 per problem and 300 overall. */
export function capSubs(subs: Submission[]): Submission[] {
  const sorted = subs.slice().sort((a, b) => b.at - a.at || (a.id < b.id ? 1 : -1));
  const per = new Map<string, number>();
  const kept: Submission[] = [];
  for (const s of sorted) {
    const n = per.get(s.pid) ?? 0;
    if (n >= LIMITS.subsPerProblem) continue;
    per.set(s.pid, n + 1);
    kept.push(s);
    if (kept.length >= LIMITS.subs) break;
  }
  return kept;
}

function newest<T extends { at: number }>(a: Record<string, T>, b: Record<string, T>, tie: (x: T, y: T) => boolean): Record<string, T> {
  const out: Record<string, T> = { ...a };
  for (const [k, vb] of Object.entries(b)) {
    const va = out[k];
    out[k] = !va || vb.at > va.at || (vb.at === va.at && tie(vb, va)) ? vb : va;
  }
  return out;
}

/**
 * Combine two copies. The result does not depend on the order (merge(a,b) equals merge(b,a)) and merging the same
 * data again changes nothing, so devices can exchange data in any order and converge.
 *  - solved: the earliest accepted time wins
 *  - submissions: union by id
 *  - notes, stars, code: the most recent edit wins
 */
export function merge(a: UserData, b: UserData): UserData {
  const solved: UserData['solved'] = { ...a.solved };
  for (const [k, vb] of Object.entries(b.solved)) {
    const va = solved[k];
    solved[k] = !va || vb.at < va.at || (vb.at === va.at && vb.lang < va.lang) ? vb : va;
  }
  const subs = new Map<string, Submission>();
  for (const s of [...a.subs, ...b.subs]) if (!subs.has(s.id)) subs.set(s.id, s);
  const contests: UserData['contests'] = { ...a.contests };
  for (const [k, vb] of Object.entries(b.contests)) {
    const va = contests[k];
    contests[k] = !va || vb.score > va.score || (vb.score === va.score && JSON.stringify(vb) > JSON.stringify(va)) ? vb : va;
  }
  return {
    v: 1,
    solved,
    subs: capSubs([...subs.values()]),
    notes: newest(a.notes, b.notes, (x, y) => x.text > y.text),
    stars: newest(a.stars, b.stars, (x, y) => x.on && !y.on),
    code: newest(a.code, b.code, (x, y) => x.text > y.text),
    contests,
  };
}

/** True when two copies hold the same information. */
export function sameData(a: UserData, b: UserData): boolean {
  const m = merge(a, b);
  return JSON.stringify(canonical(m)) === JSON.stringify(canonical(a)) && JSON.stringify(canonical(m)) === JSON.stringify(canonical(b));
}

function canonical(d: UserData): unknown {
  const sortObj = (o: Record<string, unknown>) => Object.fromEntries(Object.entries(o).sort(([x], [y]) => (x < y ? -1 : 1)));
  return {
    solved: sortObj(d.solved),
    subs: d.subs.slice().sort((x, y) => (x.id < y.id ? -1 : 1)),
    notes: sortObj(d.notes),
    stars: sortObj(d.stars),
    code: sortObj(d.code),
    contests: sortObj(d.contests),
  };
}
