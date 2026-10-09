import { BRAND } from '../config';
import { PROBLEMS } from '../data';
import { useProgress } from '../state/progress';
import { useTheme } from '../state/theme';
import { Link, Logo, MoonIcon, SectionLink } from './common';

export function Header() {
  const { solved } = useProgress();
  const { toggle } = useTheme();
  const n = PROBLEMS.filter((p) => solved[p.id]).length;
  return (
    <header className="top">
      <div className="wrap">
        <Link className="brand" to={{ name: 'landing' }} aria-label={`${BRAND} home`}>
          <Logo />
          <span>{BRAND}</span>
        </Link>
        <nav className="nav" aria-label="Main">
          <Link to={{ name: 'problems' }}>Problems</Link>
          <SectionLink id="stages">Roadmap</SectionLink>
          <SectionLink id="faq">FAQ</SectionLink>
        </nav>
        <span className="grow" />
        <span className="count tnum">
          <b>{n}</b> of {PROBLEMS.length} solved
        </span>
        <button className="icon-btn" onClick={toggle} aria-label="Switch between light and dark theme" title="Switch theme">
          <MoonIcon />
        </button>
      </div>
    </header>
  );
}
