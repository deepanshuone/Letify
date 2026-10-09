import { describe, expect, it } from 'vitest';
import { PROBLEMS } from '../src/data';
import { CONTEST_MINUTES, PENALTY_MINUTES, POINTS, SHAPE, applySubmission, clock, isOver, maxScore, mulberry32, pickProblems, standing, startContest, toResult } from '../src/user/contest';

const T0 = Date.UTC(2026, 0, 1, 10, 0, 0);
const min = (m: number) => T0 + m * 60_000;

describe('contest', () => {
  it('picks the same four problems for the same seed, with the right shape', () => {
    const a = pickProblems(PROBLEMS, {}, 42);
    expect(a).toEqual(pickProblems(PROBLEMS, {}, 42));
    expect(a.map((id) => PROBLEMS.find((p) => p.id === id)!.diff)).toEqual(SHAPE);
    expect(new Set(a).size).toBe(4);
    expect(pickProblems(PROBLEMS, {}, 43)).not.toEqual(a);
  });
  it('prefers unsolved problems and falls back when a level is used up', () => {
    const solved = Object.fromEntries(PROBLEMS.filter((p) => p.diff !== 'Hard').map((p) => [p.id, true]));
    const hardIds = PROBLEMS.filter((p) => p.diff === 'Hard').map((p) => p.id);
    const first = PROBLEMS.filter((p) => p.diff === 'Hard')[0]!;
    const almost = { ...solved, ...Object.fromEntries(hardIds.filter((id) => id !== first.id).map((id) => [id, true])) };
    // only one unsolved Hard problem is left: it must be chosen
    const ids = pickProblems(PROBLEMS, { ...almost, ...Object.fromEntries(PROBLEMS.filter((p) => p.diff === 'Easy').slice(1).map((p) => [p.id, true])) }, 7);
    expect(ids).toContain(first.id);
    // everything solved: still a full contest
    expect(pickProblems(PROBLEMS, Object.fromEntries(PROBLEMS.map((p) => [p.id, true])), 1)).toHaveLength(4);
  });
  it('random numbers are repeatable and in range', () => {
    const r = mulberry32(5);
    const r2 = mulberry32(5);
    for (let i = 0; i < 100; i++) {
      const v = r();
      expect(v).toBe(r2());
      expect(v).toBeGreaterThanOrEqual(0);
      expect(v).toBeLessThan(1);
    }
  });
  it('scores solves and charges penalties for wrong attempts before the accept', () => {
    const ids = pickProblems(PROBLEMS, {}, 1);
    let c = startContest(T0, ids);
    expect(c.end - c.start).toBe(CONTEST_MINUTES * 60_000);
    const [e, m1] = ids as [string, string, string, string];
    c = applySubmission(c, e, 'wa', min(5));
    c = applySubmission(c, e, 'tle', min(8));
    c = applySubmission(c, e, 'ac', min(12));
    c = applySubmission(c, m1, 'ac', min(40));
    c = applySubmission(c, m1, 'wa', min(41)); // after the accept: ignored
    const s = standing(c, PROBLEMS);
    expect(s).toEqual({ score: POINTS.Easy + POINTS.Medium, solvedCount: 2, minutes: 40 + 2 * PENALTY_MINUTES, penalty: 2 * PENALTY_MINUTES });
    expect(c.wrong[m1]).toBeUndefined();
    expect(toResult(c, PROBLEMS)).toMatchObject({ id: c.id, score: 8, penalty: 10 });
  });
  it('ignores submissions after the end, before the start, or for other problems', () => {
    const ids = pickProblems(PROBLEMS, {}, 2);
    const c = startContest(T0, ids);
    expect(applySubmission(c, ids[0]!, 'ac', c.end)).toBe(c);
    expect(applySubmission(c, ids[0]!, 'ac', T0 - 1)).toBe(c);
    expect(applySubmission(c, 'not-in-contest', 'ac', min(3))).toBe(c);
    expect(isOver(c, c.end - 1)).toBe(false);
    expect(isOver(c, c.end)).toBe(true);
  });
  it('wrong attempts on unsolved problems cost nothing', () => {
    const ids = pickProblems(PROBLEMS, {}, 3);
    let c = startContest(T0, ids);
    c = applySubmission(c, ids[3]!, 'wa', min(3));
    expect(standing(c, PROBLEMS)).toEqual({ score: 0, solvedCount: 0, minutes: 0, penalty: 0 });
  });
  it('max score and clock', () => {
    expect(maxScore(pickProblems(PROBLEMS, {}, 1), PROBLEMS)).toBe(3 + 5 + 5 + 8);
    expect(clock(90 * 60_000)).toBe('1:30:00');
    expect(clock(59_999)).toBe('01:00');
    expect(clock(-5)).toBe('00:00');
  });
});
