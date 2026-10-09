import { useEffect, useRef, useState } from 'react';
import { BRAND } from '../config';
import { PROBLEMS } from '../data';
import { useAuthDialog } from '../state/authdialog';
import { useCloud } from '../state/cloud';
import { useContest } from '../state/contest';
import { useProgress } from '../state/userdata';
import { useTheme } from '../state/theme';
import { clock } from '../user/contest';
import { navigate, useRoute } from '../router';
import { Link, Logo, MoonIcon, SectionLink } from './common';

function syncText(s: ReturnType<typeof useCloud>['status']): string {
  if (s.state === 'syncing') return 'Saving...';
  if (s.state === 'synced') return 'All changes saved';
  if (s.state === 'error') return s.message;
  return '';
}

function Account() {
  const cloud = useCloud();
  const auth = useAuthDialog();
  const [open, setOpen] = useState(false);
  const box = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!open) return;
    const away = (e: MouseEvent) => !box.current?.contains(e.target as Node) && setOpen(false);
    const esc = (e: KeyboardEvent) => e.key === 'Escape' && setOpen(false);
    document.addEventListener('mousedown', away);
    document.addEventListener('keydown', esc);
    return () => {
      document.removeEventListener('mousedown', away);
      document.removeEventListener('keydown', esc);
    };
  }, [open]);

  if (!cloud.enabled) return null;
  if (!cloud.ready) return <span className="spin" aria-label="Checking sign-in" />;
  if (!cloud.user) {
    return (
      <button className="btn sm primary" onClick={auth.open}>
        Sign in
      </button>
    );
  }
  const initial = (cloud.user.email[0] ?? '?').toUpperCase();
  return (
    <div className="account" ref={box}>
      <button className="avatar" aria-haspopup="menu" aria-expanded={open} aria-label={`Account of ${cloud.user.email}`} onClick={() => setOpen((o) => !o)}>
        {initial}
        <i className={`sync-dot ${cloud.status.state}`} aria-hidden="true" />
      </button>
      {open && (
        <div className="menu" role="menu">
          <div className="menu-email">{cloud.user.email}</div>
          <div className={`menu-sync ${cloud.status.state}`} role="status">
            {syncText(cloud.status) || 'Signed in'}
          </div>
          <button role="menuitem" onClick={() => { setOpen(false); navigate({ name: 'profile' }); }}>
            Your profile
          </button>
          <button role="menuitem" onClick={() => void cloud.syncNow()}>
            Sync now
          </button>
          <button role="menuitem" onClick={() => { setOpen(false); void cloud.signOut(); }}>
            Sign out
          </button>
          <button role="menuitem" className="danger" onClick={() => { if (confirm('Sign out and remove your progress from this browser? It stays in your account.')) { setOpen(false); void cloud.signOut({ clearLocal: true }); } }}>
            Sign out and clear this browser
          </button>
        </div>
      )}
    </div>
  );
}

export function Header() {
  const { solved } = useProgress();
  const { toggle } = useTheme();
  const contest = useContest();
  const route = useRoute();
  const n = PROBLEMS.filter((p) => solved[p.id]).length;
  const cur = (name: string) => (route.name === name || (name === 'plans' && route.name === 'plan') ? 'page' : undefined);
  return (
    <header className="top">
      <div className="wrap">
        <Link className="brand" to={{ name: 'landing' }} aria-label={`${BRAND} home`}>
          <Logo />
          <span>{BRAND}</span>
        </Link>
        <nav className="nav" aria-label="Main">
          <Link to={{ name: 'problems' }} aria-current={cur('problems') ?? (route.name === 'problem' ? 'page' : undefined)}>
            Problems
          </Link>
          <Link to={{ name: 'plans' }} aria-current={cur('plans')}>
            Study plans
          </Link>
          <Link to={{ name: 'contest' }} aria-current={cur('contest')}>
            Contest
          </Link>
          <Link to={{ name: 'profile' }} aria-current={cur('profile')}>
            Profile
          </Link>
          <SectionLink id="faq">FAQ</SectionLink>
        </nav>
        <span className="grow" />
        {contest.active && (
          <Link className="contest-pill" to={{ name: 'contest' }} title="Contest in progress">
            <i aria-hidden="true" /> {clock(contest.active.end - contest.now)}
          </Link>
        )}
        <span className="count tnum">
          <b>{n}</b> of {PROBLEMS.length} solved
        </span>
        <Account />
        <button className="icon-btn" onClick={toggle} aria-label="Switch between light and dark theme" title="Switch theme">
          <MoonIcon />
        </button>
      </div>
    </header>
  );
}
