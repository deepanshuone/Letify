import { describe, expect, it } from 'vitest';
import { PLANS, planIds } from '../src/data/plans';
import { BY_ID } from '../src/data';

describe('study plans', () => {
  it('every plan has at least 100 different problems, all of which exist', () => {
    for (const p of PLANS) {
      const ids = planIds(p);
      expect(ids.length, p.id).toBeGreaterThanOrEqual(100);
      for (const id of ids) expect(BY_ID.has(id), `${p.id}: ${id}`).toBe(true);
    }
  });
});
