import { describe, expect, it } from 'vitest';
import { emptyData, merge, sameData, type UserData } from '../src/user/model';
import { SyncEngine, type CloudBackend, type RemoteDoc, type SyncStatus } from '../src/user/sync';

/** A server shared by several devices. Revisions work like the real table: a save only wins if the revision matches. */
class Server {
  doc: RemoteDoc | null = null;
  failNext = 0;
  calls = { fetch: 0, create: 0, update: 0 };
  /** Runs once, between a device's fetch and its save, to simulate another device saving first. */
  interfere: (() => void) | null = null;
  backend(): CloudBackend {
    return {
      getUser: async () => ({ id: 'u', email: 'a@b.c' }),
      onAuthChange: () => () => {},
      signInPassword: async () => {},
      signUpPassword: async () => ({ needsConfirm: false }),
      sendMagicLink: async () => {},
      signInOAuth: async () => {},
      signOut: async () => {},
      fetchDoc: async () => {
        this.calls.fetch++;
        if (this.failNext > 0) {
          this.failNext--;
          throw new Error('Failed to fetch');
        }
        return this.doc ? { data: structuredClone(this.doc.data), rev: this.doc.rev } : null;
      },
      createDoc: async (d) => {
        this.calls.create++;
        this.doc ??= { data: structuredClone(d), rev: 0 };
      },
      updateDoc: async (d, rev) => {
        this.calls.update++;
        if (this.interfere) {
          const f = this.interfere;
          this.interfere = null;
          f();
        }
        if (!this.doc || this.doc.rev !== rev) return null;
        this.doc = { data: structuredClone(d), rev: rev + 1 };
        return rev + 1;
      },
    };
  }
}

function device(server: Server, start: UserData = emptyData()) {
  const state = { data: start, status: { state: 'idle' } as SyncStatus };
  const engine = new SyncEngine(server.backend(), { local: () => state.data, apply: (m) => (state.data = m), status: (s) => (state.status = s) }, 5);
  return { state, engine };
}

const solvedData = (...ids: string[]): UserData => ({ ...emptyData(), solved: Object.fromEntries(ids.map((id, i) => [id, { lang: 'python' as const, at: 100 + i }])) });

describe('sync engine', () => {
  it('uploads the first device and downloads on the second', async () => {
    const s = new Server();
    const a = device(s, solvedData('x', 'y'));
    await a.engine.sync();
    expect(a.state.status.state).toBe('synced');
    expect(Object.keys((s.doc!.data as UserData).solved)).toEqual(['x', 'y']);
    const b = device(s);
    await b.engine.sync();
    expect(Object.keys(b.state.data.solved).sort()).toEqual(['x', 'y']);
  });

  it('merges two devices that worked offline and both end up identical', async () => {
    const s = new Server();
    const a = device(s, solvedData('a1'));
    const b = device(s, solvedData('b1'));
    await a.engine.sync();
    await b.engine.sync();
    await a.engine.sync();
    expect(sameData(a.state.data, b.state.data)).toBe(true);
    expect(Object.keys(a.state.data.solved).sort()).toEqual(['a1', 'b1']);
  });

  it('retries when another device saves between the read and the write', async () => {
    const s = new Server();
    const a = device(s, solvedData('a1'));
    await a.engine.sync();
    const b = device(s, solvedData('a1', 'b1'));
    const c = device(s);
    s.interfere = () => {
      // device c saves first
      s.doc = { data: merge(c.state.data, solvedData('c1')), rev: s.doc!.rev + 1 };
    };
    await b.engine.sync();
    expect(b.state.status.state).toBe('synced');
    expect(Object.keys((s.doc!.data as UserData).solved).sort()).toEqual(['a1', 'b1', 'c1']);
    expect(Object.keys(b.state.data.solved).sort()).toEqual(['a1', 'b1', 'c1']);
  });

  it('does not write when nothing changed', async () => {
    const s = new Server();
    const a = device(s, solvedData('x'));
    await a.engine.sync();
    const updates = s.calls.update;
    await a.engine.sync();
    expect(s.calls.update).toBe(updates);
  });

  it('reports a network failure and recovers on the next try', async () => {
    const s = new Server();
    const a = device(s, solvedData('x'));
    s.failNext = 1;
    await a.engine.sync();
    expect(a.state.status).toMatchObject({ state: 'error', message: expect.stringContaining('safe in this browser') });
    expect(a.state.data.solved.x).toBeDefined(); // local data untouched
    await a.engine.sync();
    expect(a.state.status.state).toBe('synced');
  });

  it('gives up with a clear message when the data keeps changing', async () => {
    const s = new Server();
    const a = device(s, solvedData('x'));
    await a.engine.sync();
    a.state.data = solvedData('x', 'z');
    const bump = () => {
      s.doc = { data: s.doc!.data, rev: s.doc!.rev + 1 };
      s.interfere = bump;
    };
    s.interfere = bump;
    await a.engine.sync();
    expect(a.state.status).toMatchObject({ state: 'error', message: expect.stringContaining('another device') });
  });

  it('folds many quick changes into one save', async () => {
    const s = new Server();
    const a = device(s, solvedData('x'));
    await a.engine.sync();
    a.state.data = solvedData('x', 'y');
    for (let i = 0; i < 20; i++) a.engine.schedulePush();
    await new Promise((r) => setTimeout(r, 60));
    expect(s.calls.update).toBe(1);
    expect(Object.keys((s.doc!.data as UserData).solved)).toContain('y');
  });

  it('stops syncing after stop()', async () => {
    const s = new Server();
    const a = device(s, solvedData('x'));
    a.engine.stop();
    await a.engine.sync();
    a.engine.schedulePush();
    await new Promise((r) => setTimeout(r, 30));
    expect(s.calls.fetch).toBe(0);
  });

  it('ignores damaged remote data', async () => {
    const s = new Server();
    s.doc = { data: { solved: 'nope', subs: 7 }, rev: 3 };
    const a = device(s, solvedData('x'));
    await a.engine.sync();
    expect(a.state.status.state).toBe('synced');
    expect(Object.keys((s.doc.data as UserData).solved)).toEqual(['x']);
    expect(s.doc.rev).toBe(4);
  });
});
