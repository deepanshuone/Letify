/** Names and defaults in one place, so renaming the site or changing a default is a one-line edit. */
export const BRAND = 'Letify';
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
