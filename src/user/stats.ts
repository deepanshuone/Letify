import type { Diff, Problem } from '../types';
import { PLANS, type Plan } from '../data/plans';
import type { UserData } from './model';

/* Everything on the profile page is computed from UserData here, so it can be tested without a browser. */

const DAY = 86_400_000;

/** Offset of the visitor's time zone from UTC in minutes (east is positive). */
export const localOffset = (at = Date.now()) => -new Date(at).getTimezoneOffset();

/** 'YYYY-MM-DD' of a moment in the given zone. */
export function dayKey(ms: number, offsetMin: number = localOffset(ms)): string {
  const d = new Date(ms + offsetMin * 60_000);
  return `${d.getUTCFullYear()}-${String(d.getUTCMonth() + 1).padStart(2, '0')}-${String(d.getUTCDate()).padStart(2, '0')}`;
}

const dayNumber = (key: string) => Math.round(Date.parse(key + 'T00:00:00Z') / DAY);

/** Number of submissions per day. */
export function activityByDay(data: UserData, offsetMin?: number): Record<string, number> {
  const out: Record<string, number> = {};
  for (const s of data.subs) {
    const k = dayKey(s.at, offsetMin);
    out[k] = (out[k] ?? 0) + 1;
  }
  return out;
}

export interface Streaks {
  current: number;
  longest: number;
  /** Days with at least one submission. */
  activeDays: number;
}

/** A streak is a run of consecutive days with a submission. It stays alive through today until midnight passes. */
export function streaks(activity: Record<string, number>, today: string): Streaks {
  const days = Object.keys(activity).map(dayNumber).sort((a, b) => a - b);
  let longest = 0;
  let run = 0;
  let prev = -Infinity;
  for (const d of days) {
    run = d === prev + 1 ? run + 1 : 1;
    longest = Math.max(longest, run);
    prev = d;
  }
  const t = dayNumber(today);
  const have = new Set(days);
  let cur = 0;
  let d = have.has(t) ? t : t - 1;
  while (have.has(d)) {
    cur++;
    d--;
  }
  return { current: cur, longest, activeDays: days.length };
}

export const XP: Record<Diff, number> = { Easy: 10, Medium: 25, Hard: 50 };

export const LEVELS = [
  { name: 'Rookie', xp: 0 },
  { name: 'Learner', xp: 30 },
  { name: 'Coder', xp: 100 },
  { name: 'Hacker', xp: 250 },
  { name: 'Pro', xp: 500 },
  { name: 'Expert', xp: 800 },
  { name: 'Master', xp: 1100 },
  { name: 'Grandmaster', xp: 1400 },
] as const;

export function levelFor(xp: number) {
  let i = 0;
  while (i + 1 < LEVELS.length && xp >= LEVELS[i + 1]!.xp) i++;
  const cur = LEVELS[i]!;
  const next = LEVELS[i + 1];
  return { index: i, name: cur.name, xp, from: cur.xp, to: next?.xp ?? null, nextName: next?.name ?? null };
}

export interface Summary {
  byDiff: Record<Diff, { solved: number; total: number }>;
  solved: number;
  total: number;
  xp: number;
  topics: { topic: string; solved: number; total: number }[];
}

export function summarize(data: UserData, problems: readonly Problem[]): Summary {
  const byDiff: Summary['byDiff'] = { Easy: { solved: 0, total: 0 }, Medium: { solved: 0, total: 0 }, Hard: { solved: 0, total: 0 } };
  const topics = new Map<string, { solved: number; total: number }>();
  let xp = 0;
  let solved = 0;
  for (const p of problems) {
    const done = !!data.solved[p.id];
    byDiff[p.diff].total++;
    const t = topics.get(p.topic) ?? { solved: 0, total: 0 };
    t.total++;
    if (done) {
      byDiff[p.diff].solved++;
      t.solved++;
      xp += XP[p.diff];
      solved++;
    }
    topics.set(p.topic, t);
  }
  return {
    byDiff,
    solved,
    total: problems.length,
    xp,
    topics: [...topics].map(([topic, v]) => ({ topic, ...v })).sort((a, b) => b.total - a.total || (a.topic < b.topic ? -1 : 1)),
  };
}

/** The same problem for everyone on a given day. */
export function dailyProblem(day: string, problems: readonly Problem[]): Problem {
  let h = 2166136261;
  for (let i = 0; i < day.length; i++) h = Math.imul(h ^ day.charCodeAt(i), 16777619) >>> 0;
  return problems[h % problems.length]!;
}

export interface PlanProgress {
  solved: number;
  total: number;
  sections: { title: string; solved: number; total: number }[];
}

export function planProgress(plan: Plan, data: UserData): PlanProgress {
  const sections = plan.sections.map((s) => ({ title: s.title, total: s.ids.length, solved: s.ids.filter((id) => data.solved[id]).length }));
  return { solved: sections.reduce((a, s) => a + s.solved, 0), total: sections.reduce((a, s) => a + s.total, 0), sections };
}

export interface BadgeContext {
  data: UserData;
  summary: Summary;
  streaks: Streaks;
  problems: readonly Problem[];
}

export interface Badge {
  id: string;
  name: string;
  blurb: string;
  earned: boolean;
  /** Progress towards the badge, for the ones still locked. */
  have: number;
  need: number;
}

function badge(id: string, name: string, blurb: string, have: number, need: number): Badge {
  return { id, name, blurb, have: Math.min(have, need), need, earned: have >= need };
}

export function badges(ctx: BadgeContext): Badge[] {
  const { summary: s, streaks: st, data } = ctx;
  const out: Badge[] = [
    badge('first', 'First solve', 'Get your first problem accepted.', s.solved, 1),
    badge('ten', 'Ten down', 'Solve 10 problems.', s.solved, 10),
    badge('twenty-five', 'Quarter century', 'Solve 25 problems.', s.solved, 25),
    badge('fifty', 'Half century', 'Solve 50 problems.', s.solved, 50),
    badge('easy-clear', 'Basics cleared', 'Solve every Easy problem.', s.byDiff.Easy.solved, s.byDiff.Easy.total),
    badge('medium-half', 'Getting serious', 'Solve half of the Medium problems.', s.byDiff.Medium.solved, Math.ceil(s.byDiff.Medium.total / 2)),
    badge('first-hard', 'Into the deep end', 'Solve your first Hard problem.', s.byDiff.Hard.solved, 1),
    badge('streak-3', 'Three in a row', 'Submit on 3 days in a row.', st.longest, 3),
    badge('streak-7', 'A full week', 'Submit on 7 days in a row.', st.longest, 7),
    badge('streak-30', 'Habit formed', 'Submit on 30 days in a row.', st.longest, 30),
  ];
  const langs = new Set(data.subs.filter((x) => x.verdict === 'ac').map((x) => x.lang));
  out.push(badge('polyglot', 'Polyglot', 'Get an accepted solution in all four languages.', langs.size, 4));
  for (const t of s.topics) {
    if (t.total >= 3) out.push(badge(`topic-${t.topic}`, `${t.topic} master`, `Solve every ${t.topic} problem.`, t.solved, t.total));
  }
  for (const plan of PLANS) {
    const p = planProgress(plan, data);
    out.push(badge(`plan-${plan.id}`, `${plan.title} finisher`, `Complete the ${plan.title} study plan.`, p.solved, p.total));
  }
  return out;
}
