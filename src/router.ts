import { useSyncExternalStore } from 'react';
import { BY_ID } from './data';
import { PLAN_BY_ID } from './data/plans';

export type Route =
  | { name: 'landing' }
  | { name: 'problems' }
  | { name: 'problem'; id: string }
  | { name: 'plans' }
  | { name: 'plan'; id: string }
  | { name: 'profile' }
  | { name: 'contest' };

/** Routes live in the URL hash (#/problems, #/problem/two-sum), so the site works on any static host. */
export function parseHash(hash: string): Route {
  const h = hash.replace(/^#\/?/, '').replace(/\/+$/, '');
  if (h === 'problems') return { name: 'problems' };
  if (h === 'plans') return { name: 'plans' };
  if (h === 'profile') return { name: 'profile' };
  if (h === 'contest') return { name: 'contest' };
  const plan = /^plan\/(.+)$/.exec(h);
  if (plan) {
    const id = decodeURIComponent(plan[1]!);
    return PLAN_BY_ID.has(id) ? { name: 'plan', id } : { name: 'plans' };
  }
  const m = /^problem\/(.+)$/.exec(h);
  const id = m ? decodeURIComponent(m[1]!) : h; // a bare #two-sum is accepted too (older links)
  if (BY_ID.has(id)) return { name: 'problem', id };
  return { name: 'landing' };
}

export function hrefFor(r: Route): string {
  switch (r.name) {
    case 'problems':
    case 'plans':
    case 'profile':
    case 'contest':
      return `#/${r.name}`;
    case 'problem':
      return `#/problem/${encodeURIComponent(r.id)}`;
    case 'plan':
      return `#/plan/${encodeURIComponent(r.id)}`;
    default:
      return '#/';
  }
}

export function navigate(r: Route): void {
  const next = hrefFor(r);
  if (location.hash === next || (r.name === 'landing' && (location.hash === '' || location.hash === '#'))) {
    window.scrollTo(0, 0);
    return;
  }
  location.hash = next;
}

const subscribe = (cb: () => void) => {
  window.addEventListener('hashchange', cb);
  return () => window.removeEventListener('hashchange', cb);
};

const snapshot = () => location.hash;

/** The current route. Re-renders when the hash changes. */
export function useHash(): string {
  return useSyncExternalStore(subscribe, snapshot, () => '');
}

export function useRoute(): Route {
  return parseHash(useHash());
}

/** Stable key of a route, for effects that should run when the page changes. */
export const routeKey = (r: Route): string => hrefFor(r);

/** Landing-page sections are scrolled to by id; if another page is open, go home first. */
let pendingSection: string | null = null;
export function scrollToSection(id: string): void {
  const el = document.getElementById(id);
  if (el) {
    el.scrollIntoView({ behavior: 'smooth', block: 'start' });
    return;
  }
  pendingSection = id;
  navigate({ name: 'landing' });
}
export function takePendingSection(): string | null {
  const id = pendingSection;
  pendingSection = null;
  return id;
}
