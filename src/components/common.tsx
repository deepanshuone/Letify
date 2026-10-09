import type { AnchorHTMLAttributes, ReactNode } from 'react';
import { hrefFor, navigate, scrollToSection, type Route } from '../router';
import type { Diff } from '../types';

export function Logo() {
  return (
    <svg viewBox="0 0 26 26" aria-hidden="true">
      <path d="M13 1.5 23.5 7.5 13 13.5 2.5 7.5Z" fill="var(--logo-1,#7FE8C0)" />
      <path d="M2.5 7.5 13 13.5V24.5L2.5 18.5Z" fill="var(--logo-2,#7A5CFF)" />
      <path d="M23.5 7.5 13 13.5V24.5L23.5 18.5Z" fill="var(--logo-3,#4A3BD8)" />
    </svg>
  );
}

const svgProps = {
  viewBox: '0 0 24 24',
  fill: 'none',
  stroke: 'currentColor',
  strokeWidth: 2,
  strokeLinecap: 'round' as const,
  strokeLinejoin: 'round' as const,
  'aria-hidden': true,
};

export const MoonIcon = () => (
  <svg {...svgProps}>
    <path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z" />
  </svg>
);

export const GearIcon = () => (
  <svg {...svgProps}>
    <circle cx="12" cy="12" r="3" />
    <path d="M19.4 15a1.7 1.7 0 0 0 .3 1.8l.1.1a2 2 0 1 1-2.8 2.8l-.1-.1a1.7 1.7 0 0 0-1.8-.3 1.7 1.7 0 0 0-1 1.5V21a2 2 0 1 1-4 0v-.1a1.7 1.7 0 0 0-1.1-1.5 1.7 1.7 0 0 0-1.8.3l-.1.1a2 2 0 1 1-2.8-2.8l.1-.1a1.7 1.7 0 0 0 .3-1.8 1.7 1.7 0 0 0-1.5-1H3a2 2 0 1 1 0-4h.1a1.7 1.7 0 0 0 1.5-1.1 1.7 1.7 0 0 0-.3-1.8l-.1-.1a2 2 0 1 1 2.8-2.8l.1.1a1.7 1.7 0 0 0 1.8.3H9a1.7 1.7 0 0 0 1-1.5V3a2 2 0 1 1 4 0v.1a1.7 1.7 0 0 0 1 1.5 1.7 1.7 0 0 0 1.8-.3l.1-.1a2 2 0 1 1 2.8 2.8l-.1.1a1.7 1.7 0 0 0-.3 1.8V9a1.7 1.7 0 0 0 1.5 1H21a2 2 0 1 1 0 4h-.1a1.7 1.7 0 0 0-1.5 1z" />
  </svg>
);

export const CheckIcon = () => (
  <svg viewBox="0 0 12 12" fill="none" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
    <path d="M2 6.5l2.6 2.6L10 3.4" />
  </svg>
);

export function Pill({ diff }: { diff: Diff }) {
  return <span className={`pill ${diff}`}>{diff}</span>;
}

interface LinkProps extends Omit<AnchorHTMLAttributes<HTMLAnchorElement>, 'href' | 'onClick'> {
  to: Route;
  onNavigate?: () => void;
  children: ReactNode;
}

/** A link to another page. Plain clicks navigate without a reload; modified clicks open a new tab as usual. */
export function Link({ to, onNavigate, children, ...rest }: LinkProps) {
  return (
    <a
      {...rest}
      href={hrefFor(to)}
      onClick={(e) => {
        if (e.defaultPrevented || e.button !== 0 || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;
        e.preventDefault();
        onNavigate?.();
        navigate(to);
      }}
    >
      {children}
    </a>
  );
}

/** A link that scrolls to a section of the landing page. */
export function SectionLink({ id, children, ...rest }: { id: string; children: ReactNode } & Omit<AnchorHTMLAttributes<HTMLAnchorElement>, 'href' | 'onClick'>) {
  return (
    <a
      {...rest}
      href={`#${id}`}
      onClick={(e) => {
        e.preventDefault();
        scrollToSection(id);
      }}
    >
      {children}
    </a>
  );
}

/** Statement text from data/problems.py. The data build only lets plain formatting tags through, so this is safe. */
export function Rich({ html, as: Tag = 'div' }: { html: string; as?: 'div' | 'span' | 'li' | 'p' }) {
  return <Tag dangerouslySetInnerHTML={{ __html: html }} />;
}

export function short(s: string, n = 300): string {
  return s.length > n ? `${s.slice(0, n)}... (${s.length} characters in total)` : s;
}

export function fmtVal(v: unknown): string {
  return short(JSON.stringify(v) ?? 'undefined');
}
