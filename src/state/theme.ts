import { useCallback, useState } from 'react';
import { store } from '../core/storage';

type Theme = 'light' | 'dark';

function effective(): Theme {
  const t = document.documentElement.getAttribute('data-theme');
  if (t === 'light' || t === 'dark') return t;
  return window.matchMedia?.('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
}

/** Apply the saved theme before the first paint so there is no flash. */
export function initTheme(): void {
  const saved = store.get<Theme | null>('theme', null);
  if (saved === 'light' || saved === 'dark') document.documentElement.setAttribute('data-theme', saved);
}

export function useTheme(): { theme: Theme; toggle(): void } {
  const [theme, setTheme] = useState<Theme>(effective);
  const toggle = useCallback(() => {
    const next: Theme = effective() === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', next);
    store.set('theme', next);
    setTheme(next);
  }, []);
  return { theme, toggle };
}
