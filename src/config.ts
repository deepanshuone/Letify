/** Names and defaults in one place, so renaming the site or changing a default is a one-line edit. */
export const BRAND = 'AlgoAdda';
export const TAGLINE = 'Free DSA practice';
export const DESCRIPTION =
  'Free LeetCode-style practice for data structures and algorithms. Problems from Easy to Hard with hidden tests, hints, editorials and solutions in Python, JavaScript, C++ and Java.';

/** Prefix of every key the site stores in the browser. */
export const STORAGE_PREFIX = 'letify.v1.';

export const DEFAULT_JUDGE0_URL = 'https://ce.judge0.com';

/** Where the Pyodide runtime is served from. Defaults to the copy shipped with the site. */
export function pyodideUrl(): string {
  const custom = import.meta.env.VITE_PYODIDE_URL as string | undefined;
  return custom ?? new URL('pyodide/', document.baseURI).href;
}

export const JS_LIMIT_MS = 3500;
export const PY_LIMIT_MS = 5000;

/* Cloud sync (optional). Set these when building to turn on accounts. The anon key is meant to be public:
   what a visitor can read and write is decided by the row-level-security rules in supabase/schema.sql. */
export const SUPABASE_URL = (import.meta.env.VITE_SUPABASE_URL as string | undefined)?.trim() || '';
export const SUPABASE_ANON_KEY = (import.meta.env.VITE_SUPABASE_ANON_KEY as string | undefined)?.trim() || '';
/** Comma separated OAuth providers switched on in your Supabase project, for example "google,github". */
export const AUTH_PROVIDERS: string[] = ((import.meta.env.VITE_AUTH_PROVIDERS as string | undefined) ?? '')
  .split(',')
  .map((s) => s.trim().toLowerCase())
  .filter((s) => /^[a-z]+$/.test(s));
export const CLOUD_ENABLED = !!SUPABASE_URL && !!SUPABASE_ANON_KEY;
