import { describe, expect, it } from 'vitest';
import { PLANS, planIds } from '../src/data/plans';
import { BY_ID, PROBLEMS } from '../src/data';
import { LIMITS, emptyData, merge, normalize, sameData, type Submission, type UserData } from '../src/user/model';
import { activityByDay, badges, dailyProblem, dayKey, levelFor, planProgress, streaks, summarize } from '../src/user/stats';

const sub = (id: string, pid: string, at: number, verdict: Submission['verdict'] = 'ac', lang: Submission['lang'] = 'python'): Submission => ({ id, pid, lang, verdict, passed: 1, total: 1, ms: 5, at, code: 'x' });
const data = (p: Partial<UserData>): UserData => ({ ...emptyData(), ...p });

describe('study plans', () => {
  it('only contain real problems, each at most once', () => {
    for (const plan of PLANS) {
      const ids = planIds(plan);
      expect(new Set(ids).size, plan.id).toBe(ids.length);
      for (const id of ids) expect(BY_ID.has(id), `${plan.id}: ${id}`).toBe(true);
      expect(ids.length, plan.id).toBeGreaterThanOrEqual(10);
    }
  });
  it('cover every problem at least once overall', () => {
    const all = new Set(PLANS.flatMap(planIds));
    for (const p of PROBLEMS) expect(all.has(p.id), p.id).toBe(true);
  });
  it('count progress per section', () => {
    const d = data({ solved: { 'contains-duplicate': { lang: 'python', at: 1 }, 'two-sum': { lang: 'python', at: 2 } } });
    const pr = planProgress(PLANS[0]!, d);
    expect(pr.solved).toBe(2);
    expect(pr.sections[0]).toMatchObject({ solved: 2, total: 6 });
  });
});

describe('merge', () => {
  const a = data({
    solved: { x: { lang: 'python', at: 50 } },
    subs: [sub('s1', 'x', 10), sub('s2', 'x', 20)],
    notes: { x: { text: 'old', at: 5 } },
    stars: { x: { on: true, at: 5 } },
    code: { 'x.python': { text: 'a', at: 5 } },
  });
  const b = data({
    solved: { x: { lang: 'java', at: 40 }, y: { lang: 'cpp', at: 9 } },
    subs: [sub('s2', 'x', 20), sub('s3', 'y', 30, 'wa')],
    notes: { x: { text: 'new', at: 9 } },
    stars: { x: { on: false, at: 8 } },
    code: { 'x.python': { text: 'b', at: 4 } },
  });
  it('keeps the earliest solve, all submissions and the newest edits', () => {
    const m = merge(a, b);
    expect(m.solved.x).toEqual({ lang: 'java', at: 40 });
    expect(m.solved.y).toBeDefined();
    expect(m.subs.map((s) => s.id).sort()).toEqual(['s1', 's2', 's3']);
    expect(m.notes.x!.text).toBe('new');
    expect(m.stars.x!.on).toBe(false);
    expect(m.code['x.python']!.text).toBe('a');
  });
  it('is commutative, associative and idempotent', () => {
    const c = data({ notes: { x: { text: 'zzz', at: 9 } }, subs: [sub('s4', 'z', 1)] });
    expect(sameData(merge(a, b), merge(b, a))).toBe(true);
    expect(sameData(merge(merge(a, b), c), merge(a, merge(b, c)))).toBe(true);
    expect(sameData(merge(a, a), a)).toBe(true);
    const m = merge(a, b);
    expect(sameData(merge(m, b), m)).toBe(true);
  });
  it('breaks ties the same way in both directions', () => {
    const x = data({ notes: { n: { text: 'aaa', at: 1 } } });
    const y = data({ notes: { n: { text: 'bbb', at: 1 } } });
    expect(merge(x, y).notes.n!.text).toBe(merge(y, x).notes.n!.text);
  });
  it('limits stored submissions', () => {
    const many = Array.from({ length: 50 }, (_, i) => sub('m' + i, 'p', i));
    expect(merge(data({ subs: many }), emptyData()).subs.length).toBe(LIMITS.subsPerProblem);
    const spread = Array.from({ length: 400 }, (_, i) => sub('q' + i, 'p' + (i % 40), i));
    expect(merge(data({ subs: spread }), emptyData()).subs.length).toBeLessThanOrEqual(LIMITS.subs);
  });
});

describe('normalize', () => {
  it('accepts a good document unchanged', () => {
    const a = data({ solved: { x: { lang: 'python', at: 1 } }, subs: [sub('s', 'x', 1)], notes: { x: { text: 't', at: 1 } }, stars: { x: { on: true, at: 1 } }, code: { 'x.cpp': { text: 'c', at: 1 } } });
    expect(sameData(normalize(JSON.parse(JSON.stringify(a))), a)).toBe(true);
  });
  it('survives junk of every shape', () => {
    for (const junk of [null, undefined, 5, 'x', [], { solved: 5 }, { subs: [1, null, { id: 1 }], notes: [], stars: 'a' }, { solved: { x: { lang: 'cobol', at: 'now' } } }]) {
      const n = normalize(junk);
      expect(n.v).toBe(1);
      expect(Object.keys(n.solved).length).toBe(0);
      expect(n.subs).toEqual([]);
    }
  });
  it('drops prototype keys and oversize text', () => {
    const n = normalize(JSON.parse('{"notes":{"__proto__":{"text":"x","at":1},"ok":{"text":"' + 'a'.repeat(LIMITS.note + 10) + '","at":1}}}'));
    expect(Object.keys(n.notes)).toEqual(['ok']);
    expect(n.notes.ok!.text.length).toBe(LIMITS.note);
    expect(({} as Record<string, unknown>).text).toBeUndefined();
  });
});

describe('streaks and activity', () => {
  const UTC = 0;
  const day = (d: string) => Date.parse(d + 'T12:00:00Z');
  it('buckets by day in the given zone', () => {
    expect(dayKey(Date.parse('2026-03-01T23:30:00Z'), UTC)).toBe('2026-03-01');
    expect(dayKey(Date.parse('2026-03-01T23:30:00Z'), 330)).toBe('2026-03-02'); // India
    expect(dayKey(Date.parse('2026-03-01T01:00:00Z'), -300)).toBe('2026-02-28');
  });
  it('computes current and longest streaks', () => {
    const d = data({ subs: ['2026-03-01', '2026-03-02', '2026-03-03', '2026-03-05', '2026-03-06'].map((k, i) => sub('s' + i, 'p', day(k))) });
    const act = activityByDay(d, UTC);
    expect(streaks(act, '2026-03-06')).toEqual({ current: 2, longest: 3, activeDays: 5 });
    expect(streaks(act, '2026-03-07').current).toBe(2); // still alive until the day ends
    expect(streaks(act, '2026-03-08').current).toBe(0);
    expect(streaks({}, '2026-03-08')).toEqual({ current: 0, longest: 0, activeDays: 0 });
  });
  it('handles month and year boundaries', () => {
    const act = Object.fromEntries(['2025-12-30', '2025-12-31', '2026-01-01'].map((k) => [k, 1]));
    expect(streaks(act, '2026-01-01').current).toBe(3);
  });
});

describe('levels, summary, badges, daily problem', () => {
  it('maps xp to levels', () => {
    expect(levelFor(0).name).toBe('Rookie');
    expect(levelFor(29).name).toBe('Rookie');
    expect(levelFor(30)).toMatchObject({ name: 'Learner', nextName: 'Coder', to: 100 });
    expect(levelFor(99999)).toMatchObject({ name: 'Grandmaster', to: null });
  });
  it('summarises solved problems', () => {
    const easy = PROBLEMS.find((p) => p.diff === 'Easy')!;
    const hard = PROBLEMS.find((p) => p.diff === 'Hard')!;
    const s = summarize(data({ solved: { [easy.id]: { lang: 'python', at: 1 }, [hard.id]: { lang: 'python', at: 2 } } }), PROBLEMS);
    expect(s.solved).toBe(2);
    expect(s.xp).toBe(60);
    expect(s.byDiff.Easy.solved).toBe(1);
    expect(s.byDiff.Easy.total + s.byDiff.Medium.total + s.byDiff.Hard.total).toBe(PROBLEMS.length);
  });
  it('awards badges from real progress', () => {
    const solved = Object.fromEntries(PROBLEMS.filter((p) => p.diff === 'Easy').map((p) => [p.id, { lang: 'python' as const, at: 1 }]));
    const d = data({ solved, subs: (['python', 'java', 'cpp', 'javascript'] as const).map((l, i) => sub('s' + i, 'two-sum', i, 'ac', l)) });
    const list = badges({ data: d, summary: summarize(d, PROBLEMS), streaks: streaks({}, '2026-01-01'), problems: PROBLEMS });
    const get = (id: string) => list.find((b) => b.id === id)!;
    expect(get('first').earned).toBe(true);
    expect(get('easy-clear').earned).toBe(true);
    expect(get('polyglot').earned).toBe(true);
    expect(get('fifty').earned).toBe(false);
    expect(get('fifty').have).toBeLessThan(50);
    expect(new Set(list.map((b) => b.id)).size).toBe(list.length);
  });
  it('picks the same daily problem for everyone and varies by day', () => {
    expect(dailyProblem('2026-10-09', PROBLEMS).id).toBe(dailyProblem('2026-10-09', PROBLEMS).id);
    const picks = new Set(Array.from({ length: 60 }, (_, i) => dailyProblem(`2026-11-${String((i % 28) + 1).padStart(2, '0')}-${i}`, PROBLEMS).id));
    expect(picks.size).toBeGreaterThan(15);
  });
});
