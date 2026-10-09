import { useState } from 'react';
import { DEFAULT_JUDGE0_URL } from '../config';
import { getEngine, setEngine } from '../core/storage';
import { useToast } from '../state/toast';

/** Only an https URL (or a local one for development) is accepted, so the token is never sent in the clear over the internet. */
export function validJudge0Url(raw: string): string | null {
  try {
    const u = new URL(raw);
    const local = u.hostname === 'localhost' || u.hostname === '127.0.0.1';
    if (u.protocol === 'https:' || (u.protocol === 'http:' && local)) return u.origin + u.pathname.replace(/\/+$/, '');
  } catch {
    /* invalid */
  }
  return null;
}

export function EngineSettings() {
  const toast = useToast();
  const [cfg, setCfg] = useState(getEngine);
  const [err, setErr] = useState('');

  const save = () => {
    const url = cfg.url.trim() ? validJudge0Url(cfg.url.trim()) : DEFAULT_JUDGE0_URL;
    if (!url) {
      setErr('Enter a full https:// address, for example https://judge.example.com');
      return;
    }
    setErr('');
    const next = { url, token: cfg.token.trim() };
    setEngine(next);
    setCfg(next);
    toast('Engine settings saved');
  };

  return (
    <div className="settings">
      <div>
        <b>Engine settings</b>
        <div className="muted">Python and JavaScript run in your browser. C++ and Java are compiled by a Judge0 server. The free public one is the default; you can point this to your own Judge0 (free to self-host) instead.</div>
      </div>
      <label>
        Judge0 server URL
        <input value={cfg.url} autoComplete="off" onChange={(e) => setCfg({ ...cfg, url: e.target.value })} />
      </label>
      <label>
        API token (only if your server needs one)
        <input value={cfg.token} type="password" autoComplete="off" onChange={(e) => setCfg({ ...cfg, token: e.target.value })} />
      </label>
      {err && (
        <div className="note" role="alert" style={{ color: 'var(--bad)' }}>
          {err}
        </div>
      )}
      <div className="r">
        <button className="btn sm primary" onClick={save}>
          Save
        </button>
        <button
          className="btn sm"
          onClick={() => {
            const d = { url: DEFAULT_JUDGE0_URL, token: '' };
            setEngine(d);
            setCfg(d);
            setErr('');
            toast('Default server restored');
          }}
        >
          Use default
        </button>
      </div>
    </div>
  );
}
