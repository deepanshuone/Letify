import { DEFAULT_JUDGE0_URL, STORAGE_PREFIX } from '../config';

/*
 * Small wrapper over localStorage. Storage can be missing, full or blocked (private windows, embedded previews),
 * so every access is guarded and values also live in memory for the current tab.
 */
const mem = new Map<string, unknown>();

export const store = {
  get<T>(key: string, fallback: T): T {
    try {
      const raw = localStorage.getItem(STORAGE_PREFIX + key);
      if (raw !== null) return JSON.parse(raw) as T;
    } catch {
      /* fall through to memory */
    }
    return mem.has(key) ? (mem.get(key) as T) : fallback;
  },
  set(key: string, value: unknown): void {
    mem.set(key, value);
    try {
      localStorage.setItem(STORAGE_PREFIX + key, JSON.stringify(value));
    } catch {
      /* storage unavailable: the value stays in memory */
    }
  },
};

export interface EngineConfig {
  url: string;
  token: string;
}

export function getEngine(): EngineConfig {
  const e = store.get<Partial<EngineConfig> | null>('engine', null) ?? {};
  return { url: typeof e.url === 'string' && e.url ? e.url : DEFAULT_JUDGE0_URL, token: typeof e.token === 'string' ? e.token : '' };
}

export function setEngine(c: EngineConfig): void {
  store.set('engine', c);
}
