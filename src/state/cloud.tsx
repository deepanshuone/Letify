import { createContext, useCallback, useContext, useEffect, useMemo, useRef, useState, type ReactNode } from 'react';
import { CLOUD_ENABLED } from '../config';
import { SyncEngine, friendly, type CloudBackend, type CloudUser, type SyncStatus } from '../user/sync';
import { useUserData } from './userdata';

export interface CloudApi {
  enabled: boolean;
  /** False until the saved session has been checked. */
  ready: boolean;
  user: CloudUser | null;
  status: SyncStatus;
  signIn(email: string, password: string): Promise<void>;
  signUp(email: string, password: string): Promise<{ needsConfirm: boolean }>;
  magicLink(email: string): Promise<void>;
  oauth(provider: string): Promise<void>;
  signOut(opts?: { clearLocal?: boolean }): Promise<void>;
  syncNow(): Promise<void>;
}

const off: CloudApi = {
  enabled: false,
  ready: true,
  user: null,
  status: { state: 'idle' },
  signIn: async () => {},
  signUp: async () => ({ needsConfirm: false }),
  magicLink: async () => {},
  oauth: async () => {},
  signOut: async () => {},
  syncNow: async () => {},
};

const Ctx = createContext<CloudApi>(off);
export const useCloud = () => useContext(Ctx);

const REFRESH_MS = 5 * 60_000;

export function CloudProvider({ children, backendFactory }: { children: ReactNode; backendFactory?: () => Promise<CloudBackend> }) {
  const enabled = CLOUD_ENABLED || !!backendFactory;
  const ud = useUserData();
  const udRef = useRef(ud);
  udRef.current = ud;

  const [backend, setBackend] = useState<CloudBackend | null>(null);
  const [ready, setReady] = useState(!enabled);
  const [user, setUser] = useState<CloudUser | null>(null);
  const [status, setStatus] = useState<SyncStatus>({ state: 'idle' });
  const engine = useRef<SyncEngine | null>(null);

  // Load the library and the saved session.
  useEffect(() => {
    if (!enabled) return;
    let dead = false;
    let unsub = () => {};
    (async () => {
      try {
        const make = backendFactory ?? (async () => (await import('../user/supabase')).createSupabaseBackend());
        const b = await make();
        if (dead) return;
        setBackend(b);
        unsub = b.onAuthChange((u) => !dead && setUser(u));
        const u = await b.getUser();
        if (!dead) setUser(u);
        // Leave no one-time login code in the address bar.
        const url = new URL(location.href);
        if (url.searchParams.has('code')) {
          url.searchParams.delete('code');
          history.replaceState(history.state, '', url.toString());
        }
      } catch (err) {
        if (!dead) setStatus({ state: 'error', message: friendly(err) });
      } finally {
        if (!dead) setReady(true);
      }
    })();
    return () => {
      dead = true;
      unsub();
    };
  }, [enabled, backendFactory]);

  // While signed in, keep this browser and the cloud in step.
  const uid = user?.id;
  useEffect(() => {
    if (!backend || !uid) {
      return;
    }
    const e = new SyncEngine(backend, { local: () => udRef.current.getData(), apply: (m) => udRef.current.applyMerged(m), status: setStatus });
    engine.current = e;
    void e.sync();
    const unsub = udRef.current.subscribe(() => e.schedulePush());
    const again = () => document.visibilityState !== 'hidden' && void e.sync();
    document.addEventListener('visibilitychange', again);
    window.addEventListener('online', again);
    const timer = setInterval(again, REFRESH_MS);
    return () => {
      e.stop();
      engine.current = null;
      unsub();
      document.removeEventListener('visibilitychange', again);
      window.removeEventListener('online', again);
      clearInterval(timer);
    };
  }, [backend, uid]);

  const need = useCallback(() => {
    if (!backend) throw new Error('Accounts are not ready yet. Try again in a moment.');
    return backend;
  }, [backend]);

  const api = useMemo<CloudApi>(() => {
    if (!enabled) return off;
    return {
      enabled: true,
      ready,
      user,
      status,
      signIn: (email, pw) => need().signInPassword(email, pw),
      signUp: (email, pw) => need().signUpPassword(email, pw),
      magicLink: (email) => need().sendMagicLink(email),
      oauth: (p) => need().signInOAuth(p),
      async signOut(opts) {
        await engine.current?.sync(); // last upload, so nothing is lost
        await need().signOut();
        setUser(null);
        setStatus({ state: 'idle' });
        if (opts?.clearLocal) udRef.current.clearAll();
      },
      syncNow: async () => void (await engine.current?.sync()),
    };
  }, [enabled, ready, user, status, need]);

  return <Ctx.Provider value={api}>{children}</Ctx.Provider>;
}
