import { createContext, useCallback, useContext, useEffect, useMemo, useRef, useState, type ReactNode } from 'react';
import type { Lang } from '../types';
import { clearLocal, loadLocal, saveCode, saveMain } from '../user/local';
import { LIMITS, capSubs, codeKey, emptyData, merge, normalize, type ContestResult, type Submission, type UserData } from '../user/model';

export interface SubmissionInput {
  pid: string;
  lang: Lang;
  verdict: Submission['verdict'];
  passed: number;
  total: number;
  ms: number;
  code: string;
}

export interface UserDataApi {
  data: UserData;
  /** Always the newest data, also inside callbacks that were created earlier. */
  getData(): UserData;
  recordSubmission(s: SubmissionInput): void;
  getCode(pid: string, lang: Lang): string | undefined;
  setCode(pid: string, lang: Lang, text: string): void;
  setNote(pid: string, text: string): void;
  toggleStar(pid: string): void;
  recordContest(r: ContestResult): void;
  /** Replace the data with a merged copy (used by cloud sync); does not trigger another upload. */
  applyMerged(d: UserData): void;
  importData(raw: unknown): void;
  exportJson(): string;
  clearAll(): void;
  /** Called after every change made by the learner. */
  subscribe(cb: () => void): () => void;
}

const Ctx = createContext<UserDataApi | null>(null);

export function useUserData(): UserDataApi {
  const v = useContext(Ctx);
  if (!v) throw new Error('useUserData must be used inside UserDataProvider');
  return v;
}

/** Shortcut used by pages that only need to know what is solved. */
export function useProgress() {
  const { data } = useUserData();
  return { solved: data.solved };
}

let counter = 0;
const newId = (at: number) => `${at.toString(36)}-${(counter++).toString(36)}${Math.random().toString(36).slice(2, 7)}`;

export function UserDataProvider({ children }: { children: ReactNode }) {
  const [data, setData] = useState<UserData>(loadLocal);
  const ref = useRef(data);
  const listeners = useRef(new Set<() => void>());
  const codeTimer = useRef<ReturnType<typeof setTimeout> | undefined>(undefined);

  const flushCode = useCallback(() => {
    clearTimeout(codeTimer.current);
    saveCode(ref.current);
  }, []);

  const commit = useCallback(
    (next: UserData, opts: { code?: boolean; silent?: boolean } = {}) => {
      ref.current = next;
      setData(next);
      if (opts.code) {
        clearTimeout(codeTimer.current);
        codeTimer.current = setTimeout(() => saveCode(ref.current), 500);
      } else {
        saveMain(next);
      }
      if (!opts.silent) listeners.current.forEach((cb) => cb());
    },
    [],
  );

  // Do not lose the last keystrokes when the tab is closed.
  useEffect(() => {
    const onHide = () => {
      flushCode();
      saveMain(ref.current);
    };
    window.addEventListener('pagehide', onHide);
    document.addEventListener('visibilitychange', onHide);
    return () => {
      window.removeEventListener('pagehide', onHide);
      document.removeEventListener('visibilitychange', onHide);
      onHide();
    };
  }, [flushCode]);

  // Another tab of the same site saved something: pick it up.
  useEffect(() => {
    const onStorage = (e: StorageEvent) => {
      if (!e.key || !/\.ud(code)?$/.test(e.key)) return;
      commit(merge(ref.current, loadLocal()), { silent: true, code: e.key.endsWith('udcode') });
    };
    window.addEventListener('storage', onStorage);
    return () => window.removeEventListener('storage', onStorage);
  }, [commit]);

  const api = useMemo<UserDataApi>(
    () => ({
      data,
      getData: () => ref.current,
      recordSubmission(s) {
        const d = ref.current;
        const at = Date.now();
        const sub: Submission = { id: newId(at), pid: s.pid, lang: s.lang, verdict: s.verdict, passed: s.passed, total: s.total, ms: Math.round(s.ms), at, code: s.code.slice(0, LIMITS.subCode) };
        const solved = s.verdict === 'ac' && !d.solved[s.pid] ? { ...d.solved, [s.pid]: { lang: s.lang, at } } : d.solved;
        commit({ ...d, solved, subs: capSubs([sub, ...d.subs]) });
      },
      getCode: (pid, lang) => ref.current.code[codeKey(pid, lang)]?.text,
      setCode(pid, lang, text) {
        const d = ref.current;
        const k = codeKey(pid, lang);
        if (d.code[k]?.text === text) return;
        commit({ ...d, code: { ...d.code, [k]: { text: text.slice(0, LIMITS.code), at: Date.now() } } }, { code: true });
      },
      setNote(pid, text) {
        const d = ref.current;
        commit({ ...d, notes: { ...d.notes, [pid]: { text: text.slice(0, LIMITS.note), at: Date.now() } } });
      },
      toggleStar(pid) {
        const d = ref.current;
        commit({ ...d, stars: { ...d.stars, [pid]: { on: !d.stars[pid]?.on, at: Date.now() } } });
      },
      recordContest(r) {
        const d = ref.current;
        commit({ ...d, contests: { ...d.contests, [r.id]: r } });
      },
      applyMerged(d) {
        commit(d, { silent: true });
        saveCode(d);
      },
      importData(raw) {
        commit(merge(ref.current, normalize(raw)));
        saveCode(ref.current);
      },
      exportJson: () => JSON.stringify({ app: 'letify', exportedAt: new Date().toISOString(), ...ref.current }, null, 2),
      clearAll() {
        clearTimeout(codeTimer.current);
        clearLocal();
        commit(emptyData(), { silent: true });
      },
      subscribe(cb) {
        listeners.current.add(cb);
        return () => listeners.current.delete(cb);
      },
    }),
    [data, commit],
  );

  return <Ctx.Provider value={api}>{children}</Ctx.Provider>;
}
