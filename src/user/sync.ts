import { merge, normalize, sameData, type UserData } from './model';

/* Cloud sync that does not depend on any particular service: a small backend interface plus the merge loop.
   The Supabase backend is in supabase.ts; tests use an in-memory backend. */

export interface CloudUser {
  id: string;
  email: string;
}

export interface RemoteDoc {
  data: unknown;
  rev: number;
}

export interface CloudBackend {
  getUser(): Promise<CloudUser | null>;
  onAuthChange(cb: (u: CloudUser | null) => void): () => void;
  signInPassword(email: string, password: string): Promise<void>;
  /** Resolves with true when the account exists but the email has to be confirmed before signing in. */
  signUpPassword(email: string, password: string): Promise<{ needsConfirm: boolean }>;
  sendMagicLink(email: string): Promise<void>;
  signInOAuth(provider: string): Promise<void>;
  signOut(): Promise<void>;
  fetchDoc(): Promise<RemoteDoc | null>;
  /** Create the row if it does not exist yet (no error when it already does). */
  createDoc(data: UserData): Promise<void>;
  /** Save only if the stored revision still equals expectedRev. Returns the new revision, or null on a clash. */
  updateDoc(data: UserData, expectedRev: number): Promise<number | null>;
}

export type SyncStatus = { state: 'idle' } | { state: 'syncing' } | { state: 'synced'; at: number } | { state: 'error'; message: string };

export interface EngineHooks {
  /** The current local data. */
  local(): UserData;
  /** Called when the merge produced something different from local. */
  apply(merged: UserData): void;
  status(s: SyncStatus): void;
}

const MAX_ATTEMPTS = 5;

export class SyncEngine {
  private timer: ReturnType<typeof setTimeout> | undefined;
  private running: Promise<void> | null = null;
  private again = false;
  private stopped = false;

  constructor(
    private backend: CloudBackend,
    private hooks: EngineHooks,
    private delayMs = 2500,
  ) {}

  /** Pull, merge, push. Safe to call at any time: overlapping calls are folded into one more pass. */
  sync(): Promise<void> {
    if (this.stopped) return Promise.resolve();
    if (this.running) {
      this.again = true;
      return this.running;
    }
    this.running = (async () => {
      try {
        do {
          this.again = false;
          await this.pass();
        } while (this.again && !this.stopped);
      } finally {
        this.running = null;
      }
    })();
    return this.running;
  }

  /** Save soon: many quick changes become one request. */
  schedulePush(): void {
    if (this.stopped) return;
    clearTimeout(this.timer);
    this.timer = setTimeout(() => void this.sync(), this.delayMs);
  }

  stop(): void {
    this.stopped = true;
    clearTimeout(this.timer);
  }

  private async pass(): Promise<void> {
    this.hooks.status({ state: 'syncing' });
    try {
      for (let attempt = 0; attempt < MAX_ATTEMPTS; attempt++) {
        let remote = await this.backend.fetchDoc();
        if (!remote) {
          await this.backend.createDoc(this.hooks.local());
          remote = (await this.backend.fetchDoc()) ?? { data: {}, rev: 0 };
        }
        const theirs = normalize(remote.data);
        const merged = merge(this.hooks.local(), theirs);
        if (!sameData(merged, this.hooks.local())) this.hooks.apply(merged);
        if (sameData(merged, theirs)) {
          this.hooks.status({ state: 'synced', at: Date.now() });
          return;
        }
        const rev = await this.backend.updateDoc(merged, remote.rev);
        if (rev !== null) {
          this.hooks.status({ state: 'synced', at: Date.now() });
          return;
        }
        // Another device saved in between: fetch again and merge again.
      }
      throw new Error('Could not save because another device kept changing the data. Try again.');
    } catch (err) {
      this.hooks.status({ state: 'error', message: friendly(err) });
    }
  }
}

export function friendly(err: unknown): string {
  const m = String((err as { message?: string })?.message ?? err);
  if (/failed to fetch|networkerror|load failed/i.test(m)) return 'Could not reach the server. Your progress is safe in this browser and will sync later.';
  return m.slice(0, 200);
}
