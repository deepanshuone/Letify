import { createContext, useCallback, useContext, useEffect, useMemo, useRef, useState, type ReactNode } from 'react';
import { PROBLEMS } from '../data';
import { store } from '../core/storage';
import { applySubmission, isOver, pickProblems, startContest, toResult, type ActiveContest } from '../user/contest';
import type { SubVerdict } from '../user/model';
import { useUserData } from './userdata';

interface ContestApi {
  active: ActiveContest | null;
  /** Current time, refreshed every second while a contest runs. */
  now: number;
  /** Id of the contest that ended most recently in this visit. */
  lastFinished: string | null;
  start(): void;
  finish(): void;
  /** Tell the contest about a judged submission. */
  report(pid: string, verdict: SubVerdict): void;
  /** True for problems whose hints and editorial are closed because a contest is running. */
  locked(pid: string): boolean;
}

const Ctx = createContext<ContestApi | null>(null);
export function useContest(): ContestApi {
  const v = useContext(Ctx);
  if (!v) throw new Error('useContest must be used inside ContestProvider');
  return v;
}

const isNumMap = (m: unknown): m is Record<string, number> => typeof m === 'object' && m !== null && Object.values(m).every((x) => typeof x === 'number');

function loadActive(): ActiveContest | null {
  const c = store.get<Partial<ActiveContest> | null>('contest', null);
  if (!c || typeof c.id !== 'string' || typeof c.start !== 'number' || typeof c.end !== 'number') return null;
  if (!Array.isArray(c.ids) || !c.ids.every((x) => typeof x === 'string') || !isNumMap(c.solved) || !isNumMap(c.wrong)) return null;
  return { id: c.id, start: c.start, end: c.end, ids: c.ids, solved: c.solved, wrong: c.wrong };
}

export function ContestProvider({ children }: { children: ReactNode }) {
  const ud = useUserData();
  const udRef = useRef(ud);
  udRef.current = ud;
  const [active, setActive] = useState<ActiveContest | null>(loadActive);
  const activeRef = useRef(active);
  const [now, setNow] = useState(Date.now());
  const [lastFinished, setLastFinished] = useState<string | null>(null);

  const set = useCallback((c: ActiveContest | null) => {
    activeRef.current = c;
    setActive(c);
    store.set('contest', c);
  }, []);

  const finish = useCallback(() => {
    const c = activeRef.current;
    if (!c) return;
    udRef.current.recordContest(toResult(c, PROBLEMS));
    setLastFinished(c.id);
    set(null);
  }, [set]);

  useEffect(() => {
    if (!active) return;
    const tick = () => {
      const t = Date.now();
      setNow(t);
      if (activeRef.current && isOver(activeRef.current, t)) finish();
    };
    tick();
    const timer = setInterval(tick, 1000);
    return () => clearInterval(timer);
  }, [active?.id, finish]); // eslint-disable-line react-hooks/exhaustive-deps

  const api = useMemo<ContestApi>(
    () => ({
      active,
      now,
      lastFinished,
      start() {
        if (activeRef.current) return;
        const t = Date.now();
        set(startContest(t, pickProblems(PROBLEMS, udRef.current.getData().solved, t)));
        setNow(t);
        setLastFinished(null);
      },
      finish,
      report(pid, verdict) {
        const c = activeRef.current;
        if (!c) return;
        const next = applySubmission(c, pid, verdict, Date.now());
        if (next !== c) set(next);
      },
      locked: (pid) => !!active && active.ids.includes(pid) && now < active.end,
    }),
    [active, now, lastFinished, finish, set],
  );

  return <Ctx.Provider value={api}>{children}</Ctx.Provider>;
}
