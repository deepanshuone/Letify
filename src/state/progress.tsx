import { createContext, useCallback, useContext, useMemo, useState, type ReactNode } from 'react';
import { store } from '../core/storage';
import type { Lang } from '../types';

export type SolvedMap = Record<string, { lang: Lang; at: number }>;

interface ProgressValue {
  solved: SolvedMap;
  markSolved(id: string, lang: Lang): void;
}

const Ctx = createContext<ProgressValue>({ solved: {}, markSolved: () => {} });
export const useProgress = () => useContext(Ctx);

/* Progress is saved in this browser today. When accounts arrive, only this provider needs to learn to sync. */
export function ProgressProvider({ children }: { children: ReactNode }) {
  const [solved, setSolved] = useState<SolvedMap>(() => store.get<SolvedMap>('solved', {}));
  const markSolved = useCallback((id: string, lang: Lang) => {
    setSolved((cur) => {
      const next = { ...cur, [id]: { lang, at: Date.now() } };
      store.set('solved', next);
      return next;
    });
  }, []);
  const value = useMemo(() => ({ solved, markSolved }), [solved, markSolved]);
  return <Ctx.Provider value={value}>{children}</Ctx.Provider>;
}
