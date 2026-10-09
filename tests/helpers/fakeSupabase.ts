/* A small in-memory stand-in for a Supabase project: just the endpoints Letify uses.
   - Auth: password sign-in (any password for an address creates / matches that account), refresh, user, logout.
   - REST: the user_data table with the same row-level behaviour as supabase/schema.sql (a user sees only their own row).
   Several browser contexts can share one instance, which is how the e2e test checks syncing between two devices. */

export interface FakeResponse {
  status: number;
  headers?: Record<string, string>;
  json?: unknown;
}

interface Row {
  user_id: string;
  data: unknown;
  rev: number;
  updated_at: string;
}

const b64 = (o: unknown) => Buffer.from(JSON.stringify(o)).toString('base64url');

export class FakeSupabase {
  rows = new Map<string, Row>();
  /** Every update that was refused because its `rev` was stale (a clash between two devices). */
  clashes = 0;
  requests: string[] = [];
  private users = new Map<string, { id: string; email: string }>();

  private userFor(email: string) {
    const key = email.toLowerCase();
    let u = this.users.get(key);
    if (!u) {
      const n = this.users.size + 1;
      u = { id: `00000000-0000-4000-8000-${String(n).padStart(12, '0')}`, email: key };
      this.users.set(key, u);
    }
    return u;
  }

  private session(u: { id: string; email: string }) {
    const now = Math.floor(Date.now() / 1000);
    const claims = { sub: u.id, email: u.email, aud: 'authenticated', role: 'authenticated', iat: now, exp: now + 3600 };
    return {
      access_token: `${b64({ alg: 'HS256', typ: 'JWT' })}.${b64(claims)}.sig`,
      token_type: 'bearer',
      expires_in: 3600,
      expires_at: now + 3600,
      refresh_token: `r-${u.id}`,
      user: { id: u.id, aud: 'authenticated', role: 'authenticated', email: u.email, email_confirmed_at: new Date().toISOString(), app_metadata: {}, user_metadata: {}, created_at: new Date().toISOString() },
    };
  }

  private userOf(headers: Record<string, string>) {
    const m = /^Bearer (.+)$/i.exec(headers['authorization'] ?? '');
    const payload = m?.[1]?.split('.')[1];
    if (!payload) return null;
    try {
      const c = JSON.parse(Buffer.from(payload, 'base64url').toString()) as { sub: string; email: string };
      return { id: c.sub, email: c.email };
    } catch {
      return null;
    }
  }

  handle(method: string, rawUrl: string, headers: Record<string, string>, body: string | null): FakeResponse {
    const url = new URL(rawUrl);
    this.requests.push(`${method} ${url.pathname}${url.search}`);
    const json = () => (body ? (JSON.parse(body) as Record<string, any>) : {});

    if (url.pathname === '/auth/v1/token') {
      const grant = url.searchParams.get('grant_type');
      if (grant === 'password') {
        const b = json();
        if (!b.email || !b.password) return { status: 400, json: { code: 400, error_code: 'validation_failed', msg: 'missing credentials' } };
        return { status: 200, json: this.session(this.userFor(String(b.email))) };
      }
      if (grant === 'refresh_token') {
        const id = String(json().refresh_token ?? '').replace(/^r-/, '');
        const u = [...this.users.values()].find((x) => x.id === id);
        return u ? { status: 200, json: this.session(u) } : { status: 400, json: { code: 400, error_code: 'refresh_token_not_found', msg: 'Invalid Refresh Token' } };
      }
    }
    if (url.pathname === '/auth/v1/user') {
      const u = this.userOf(headers);
      return u ? { status: 200, json: this.session(u).user } : { status: 401, json: { code: 401, msg: 'invalid JWT' } };
    }
    if (url.pathname === '/auth/v1/logout') return { status: 204 };

    if (url.pathname === '/rest/v1/user_data') {
      const me = this.userOf(headers);
      if (!me) return { status: 401, json: { code: '42501', message: 'permission denied for table user_data' } };
      const eq = (k: string) => {
        const v = url.searchParams.get(k);
        return v?.startsWith('eq.') ? v.slice(3) : null;
      };
      if (method === 'GET') {
        const row = this.rows.get(me.id);
        return { status: 200, json: row && eq('user_id') === me.id ? [{ data: row.data, rev: row.rev }] : [] };
      }
      if (method === 'POST') {
        const b = json();
        if (b.user_id !== me.id) return { status: 403, json: { code: '42501', message: 'new row violates row-level security policy for table "user_data"' } };
        if (!this.rows.has(me.id)) this.rows.set(me.id, { user_id: me.id, data: b.data, rev: 0, updated_at: new Date().toISOString() });
        return { status: 201 };
      }
      if (method === 'PATCH') {
        const b = json();
        const row = this.rows.get(me.id);
        if (!row || eq('user_id') !== me.id) return { status: 200, json: [] };
        if (String(row.rev) !== eq('rev')) {
          this.clashes++;
          return { status: 200, json: [] };
        }
        row.data = b.data;
        row.rev = b.rev;
        row.updated_at = b.updated_at;
        return { status: 200, json: [{ rev: row.rev }] };
      }
    }
    return { status: 404, json: { message: `fake supabase: no route for ${method} ${url.pathname}` } };
  }
}
