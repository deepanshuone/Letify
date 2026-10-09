import type { Diff, Problem } from '../types';
import type { ContestResult, SubVerdict } from './model';

/* A virtual contest: four problems, a countdown, points per problem and a time penalty for wrong attempts
   (the same idea as the ICPC rules used on CodeChef and Codeforces). It runs on your own device. */

export const CONTEST_MINUTES = 90;
export const POINTS: Record<Diff, number> = { Easy: 3, Medium: 5, Hard: 8 };
export const PENALTY_MINUTES = 5;
/** One Easy, two Medium and one Hard. */
export const SHAPE: Diff[] = ['Easy', 'Medium', 'Medium', 'Hard'];

export interface ActiveContest {
  id: string;
  start: number;
  end: number;
  ids: string[];
  solved: Record<string, number>;
  wrong: Record<string, number>;
}

/** Small deterministic random numbers, so a seed always gives the same contest. */
export function mulberry32(seed: number): () => number {
  let a = seed >>> 0;
  return () => {
    a = (a + 0x6d2b79f5) >>> 0;
    let t = a;
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

/** Pick problems that are not solved yet; fall back to solved ones when a level has run out. */
export function pickProblems(problems: readonly Problem[], solved: Record<string, unknown>, seed: number): string[] {
  const rnd = mulberry32(seed);
  const used = new Set<string>();
  const out: string[] = [];
  for (const diff of SHAPE) {
    const level = problems.filter((p) => p.diff === diff && !used.has(p.id));
    const fresh = level.filter((p) => !solved[p.id]);
    const pool = fresh.length ? fresh : level;
    if (!pool.length) continue;
    const pick = pool[Math.floor(rnd() * pool.length)]!;
    used.add(pick.id);
    out.push(pick.id);
  }
  return out;
}

export function startContest(now: number, ids: string[]): ActiveContest {
  return { id: 'c' + now.toString(36), start: now, end: now + CONTEST_MINUTES * 60_000, ids, solved: {}, wrong: {} };
}

export const isOver = (c: ActiveContest, now: number) => now >= c.end;

/** Register a judged submission. Submissions after the end, for other problems or after an accept are ignored. */
export function applySubmission(c: ActiveContest, pid: string, verdict: SubVerdict, at: number): ActiveContest {
  if (at >= c.end || at < c.start || !c.ids.includes(pid) || c.solved[pid] !== undefined) return c;
  if (verdict === 'ac') return { ...c, solved: { ...c.solved, [pid]: at } };
  return { ...c, wrong: { ...c.wrong, [pid]: (c.wrong[pid] ?? 0) + 1 } };
}

export interface Standing {
  score: number;
  solvedCount: number;
  /** Minutes from the start to the last accepted solution, plus penalties. */
  minutes: number;
  penalty: number;
}

export function standing(c: ActiveContest | ContestResult, problems: readonly Problem[]): Standing {
  let score = 0;
  let last = 0;
  let penalty = 0;
  let solvedCount = 0;
  for (const [pid, at] of Object.entries(c.solved)) {
    const p = problems.find((x) => x.id === pid);
    if (!p) continue;
    score += POINTS[p.diff];
    solvedCount++;
    last = Math.max(last, Math.floor((at - c.start) / 60_000));
    penalty += PENALTY_MINUTES * (c.wrong[pid] ?? 0);
  }
  return { score, solvedCount, minutes: solvedCount ? last + penalty : 0, penalty };
}

export function toResult(c: ActiveContest, problems: readonly Problem[]): ContestResult {
  const s = standing(c, problems);
  return { id: c.id, start: c.start, end: c.end, ids: c.ids, solved: c.solved, wrong: c.wrong, score: s.score, penalty: s.penalty };
}

export const maxScore = (ids: string[], problems: readonly Problem[]) => ids.reduce((a, id) => a + (POINTS[problems.find((p) => p.id === id)?.diff ?? 'Easy'] ?? 0), 0);

/** mm:ss or h:mm:ss */
export function clock(ms: number): string {
  const s = Math.max(0, Math.ceil(ms / 1000));
  const h = Math.floor(s / 3600);
  const m = Math.floor((s % 3600) / 60);
  const r = s % 60;
  const two = (n: number) => String(n).padStart(2, '0');
  return h ? `${h}:${two(m)}:${two(r)}` : `${two(m)}:${two(r)}`;
}
