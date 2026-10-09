import { createContext, useContext, useMemo, useState, type ReactNode } from 'react';
import type { Diff } from '../types';

export interface Filters {
  q: string;
  diff: 'All' | Diff;
  topic: string;
  status: 'All' | 'Todo' | 'Solved';
}

const initial: Filters = { q: '', diff: 'All', topic: 'All', status: 'All' };

interface FiltersValue {
  filters: Filters;
  setFilters(patch: Partial<Filters>): void;
}
const Ctx = createContext<FiltersValue>({ filters: initial, setFilters: () => {} });
export const useFilters = () => useContext(Ctx);

/* Kept above the pages so the filters survive opening a problem and coming back. */
export function FiltersProvider({ children }: { children: ReactNode }) {
  const [filters, set] = useState<Filters>(initial);
  const value = useMemo(() => ({ filters, setFilters: (patch: Partial<Filters>) => set((f) => ({ ...f, ...patch })) }), [filters]);
  return <Ctx.Provider value={value}>{children}</Ctx.Provider>;
}
