import type { SupabaseClient } from '@supabase/supabase-js';
import { SUPABASE_ANON_KEY, SUPABASE_URL } from '../config';
import type { UserData } from './model';
import type { CloudBackend, CloudUser, RemoteDoc } from './sync';

/* The Supabase implementation of CloudBackend. The library is loaded only when accounts are switched on,
   so visitors of a site without a Supabase project never download it. */

const redirect = () => location.origin + location.pathname;

export async function createSupabaseBackend(): Promise<CloudBackend> {
  const { createClient } = await import('@supabase/supabase-js');
  const client: SupabaseClient = createClient(SUPABASE_URL, SUPABASE_ANON_KEY, {
    // PKCE returns to the page with ?code=..., which does not clash with the #/ routes of this site.
    auth: { flowType: 'pkce', persistSession: true, autoRefreshToken: true, detectSessionInUrl: true },
  });

  const toUser = (u: { id: string; email?: string | null } | null | undefined): CloudUser | null => (u ? { id: u.id, email: u.email ?? '' } : null);
  const userId = async () => {
    const { data } = await client.auth.getSession();
    const id = data.session?.user.id;
    if (!id) throw new Error('You are signed out.');
    return id;
  };
  const check = (error: { message: string } | null) => {
    if (error) throw new Error(error.message);
  };

  return {
    async getUser() {
      const { data } = await client.auth.getSession();
      return toUser(data.session?.user);
    },
    onAuthChange(cb) {
      const { data } = client.auth.onAuthStateChange((_e, session) => cb(toUser(session?.user)));
      return () => data.subscription.unsubscribe();
    },
    async signInPassword(email, password) {
      check((await client.auth.signInWithPassword({ email, password })).error);
    },
    async signUpPassword(email, password) {
      const { data, error } = await client.auth.signUp({ email, password, options: { emailRedirectTo: redirect() } });
      check(error);
      return { needsConfirm: !data.session };
    },
    async sendMagicLink(email) {
      check((await client.auth.signInWithOtp({ email, options: { emailRedirectTo: redirect() } })).error);
    },
    async signInOAuth(provider) {
      check((await client.auth.signInWithOAuth({ provider: provider as 'google', options: { redirectTo: redirect() } })).error);
    },
    async signOut() {
      check((await client.auth.signOut()).error);
    },
    async fetchDoc(): Promise<RemoteDoc | null> {
      const id = await userId();
      const { data, error } = await client.from('user_data').select('data, rev').eq('user_id', id).maybeSingle();
      check(error);
      return data ? { data: data.data, rev: Number(data.rev) } : null;
    },
    async createDoc(doc: UserData) {
      const id = await userId();
      check((await client.from('user_data').upsert({ user_id: id, data: doc }, { onConflict: 'user_id', ignoreDuplicates: true })).error);
    },
    async updateDoc(doc: UserData, expectedRev: number) {
      const id = await userId();
      const { data, error } = await client
        .from('user_data')
        .update({ data: doc, rev: expectedRev + 1, updated_at: new Date().toISOString() })
        .eq('user_id', id)
        .eq('rev', expectedRev)
        .select('rev');
      check(error);
      return data && data.length > 0 ? Number(data[0]!.rev) : null;
    },
  };
}
