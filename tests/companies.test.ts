import { describe, expect, it } from 'vitest';
import { BY_ID } from '../src/data';
import { COMPANY_LISTS } from '../src/data/companies';

describe('company lists', () => {
  it('every id exists and no company repeats a problem', () => {
    for (const c of COMPANY_LISTS) {
      expect(c.ids.length, c.name).toBeGreaterThanOrEqual(10);
      expect(new Set(c.ids).size, c.name).toBe(c.ids.length);
      for (const id of c.ids) expect(BY_ID.has(id), `${c.name}: ${id}`).toBe(true);
    }
  });
});
