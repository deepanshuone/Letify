import { createContext, useContext, useEffect, useMemo, useRef, useState, type FormEvent, type ReactNode } from 'react';
import { AUTH_PROVIDERS } from '../config';
import { friendly } from '../user/sync';
import { useCloud } from './cloud';

const Ctx = createContext<{ open(): void }>({ open: () => {} });
export const useAuthDialog = () => useContext(Ctx);

type Mode = 'signin' | 'signup' | 'link';

const PROVIDER_NAMES: Record<string, string> = { google: 'Google', github: 'GitHub', gitlab: 'GitLab', discord: 'Discord', apple: 'Apple' };

export function AuthDialogProvider({ children }: { children: ReactNode }) {
  const [isOpen, setOpen] = useState(false);
  const value = useMemo(() => ({ open: () => setOpen(true) }), []);
  return (
    <Ctx.Provider value={value}>
      {children}
      {isOpen && <AuthDialog onClose={() => setOpen(false)} />}
    </Ctx.Provider>
  );
}

function AuthDialog({ onClose }: { onClose(): void }) {
  const cloud = useCloud();
  const ref = useRef<HTMLDialogElement>(null);
  const [mode, setMode] = useState<Mode>('signin');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const [info, setInfo] = useState('');

  useEffect(() => {
    const d = ref.current;
    if (d && !d.open) d.showModal();
  }, []);

  // Close as soon as the sign-in worked.
  useEffect(() => {
    if (cloud.user) onClose();
  }, [cloud.user, onClose]);

  const submit = async (e: FormEvent) => {
    e.preventDefault();
    setError('');
    setInfo('');
    setBusy(true);
    try {
      if (mode === 'signin') await cloud.signIn(email.trim(), password);
      else if (mode === 'signup') {
        const r = await cloud.signUp(email.trim(), password);
        if (r.needsConfirm) setInfo('Account created. Open the email we sent you and confirm your address, then sign in.');
      } else {
        await cloud.magicLink(email.trim());
        setInfo('Check your inbox: we sent a sign-in link to ' + email.trim() + '.');
      }
    } catch (err) {
      setError(friendly(err));
    } finally {
      setBusy(false);
    }
  };

  const titles: Record<Mode, string> = { signin: 'Sign in', signup: 'Create your account', link: 'Get a sign-in link' };

  return (
    <dialog ref={ref} className="auth" aria-labelledby="auth-title" onClose={onClose} onClick={(e) => e.target === ref.current && onClose()}>
      <form onSubmit={submit} className="auth-form">
        <div className="auth-head">
          <h2 id="auth-title">{titles[mode]}</h2>
          <button type="button" className="icon-btn" aria-label="Close" onClick={onClose}>
            &times;
          </button>
        </div>
        <p className="muted" style={{ marginTop: 0 }}>
          An account saves your progress and code in the cloud so you can continue on any device. It stays free.
        </p>
        {AUTH_PROVIDERS.length > 0 && (
          <div className="auth-providers">
            {AUTH_PROVIDERS.map((p) => (
              <button key={p} type="button" className="btn" onClick={() => cloud.oauth(p).catch((err) => setError(friendly(err)))}>
                Continue with {PROVIDER_NAMES[p] ?? p}
              </button>
            ))}
            <div className="auth-or">or use your email</div>
          </div>
        )}
        <label>
          Email
          <input type="email" required autoComplete="email" value={email} onChange={(e) => setEmail(e.target.value)} />
        </label>
        {mode !== 'link' && (
          <label>
            Password
            <input type="password" required minLength={8} autoComplete={mode === 'signup' ? 'new-password' : 'current-password'} value={password} onChange={(e) => setPassword(e.target.value)} />
          </label>
        )}
        {error && (
          <div className="note auth-error" role="alert">
            {error}
          </div>
        )}
        {info && (
          <div className="note" role="status">
            {info}
          </div>
        )}
        <button className="btn primary lg" type="submit" disabled={busy || !cloud.ready}>
          {busy ? 'Please wait...' : mode === 'signin' ? 'Sign in' : mode === 'signup' ? 'Create account' : 'Email me a link'}
        </button>
        <div className="auth-switch">
          {mode !== 'signin' && (
            <button type="button" className="linklike" onClick={() => setMode('signin')}>
              I already have an account
            </button>
          )}
          {mode !== 'signup' && (
            <button type="button" className="linklike" onClick={() => setMode('signup')}>
              Create an account
            </button>
          )}
          {mode !== 'link' && (
            <button type="button" className="linklike" onClick={() => setMode('link')}>
              Email me a sign-in link
            </button>
          )}
        </div>
      </form>
    </dialog>
  );
}
