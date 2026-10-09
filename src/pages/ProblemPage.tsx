import { useCallback, useEffect, useRef, useState } from 'react';
import { Editor } from '../components/Editor';
import { EngineSettings } from '../components/EngineSettings';
import { Description, Editorial, Hints } from '../components/ProblemTabs';
import { Results, type RunState } from '../components/Results';
import { GearIcon, Link, Pill } from '../components/common';
import { LANGS, LANG_IDS, isLang, starter } from '../core/languages';
import { store } from '../core/storage';
import { makeVerdict } from '../core/verdict';
import { PROBLEMS, loadTests } from '../data';
import { ensurePython, runEngine } from '../engines';
import { useProgress } from '../state/progress';
import { useToast } from '../state/toast';
import type { Lang, Problem } from '../types';

type Tab = 'desc' | 'hints' | 'edit';
const TABS: [Tab, string][] = [
  ['desc', 'Description'],
  ['hints', 'Hints'],
  ['edit', 'Editorial'],
];

const clampFont = (n: number) => Math.min(20, Math.max(11, n));
const codeKey = (id: string, lang: Lang) => `code.${id}.${lang}`;

function savedLang(): Lang {
  const l = store.get<unknown>('lang', 'python');
  return isLang(l) ? l : 'python';
}

export function ProblemPage({ p }: { p: Problem }) {
  const toast = useToast();
  const { solved, markSolved } = useProgress();
  const idx = PROBLEMS.indexOf(p);
  const prev = PROBLEMS[idx - 1];
  const next = PROBLEMS[idx + 1];

  const [lang, setLang] = useState<Lang>(savedLang);
  const [code, setCode] = useState(() => store.get<string | null>(codeKey(p.id, savedLang()), null) || starter(p, savedLang()));
  const [tab, setTab] = useState<Tab>('desc');
  const [hints, setHints] = useState(0);
  const [pane, setPane] = useState<'problem' | 'code'>('problem');
  const [settings, setSettings] = useState(false);
  const [fs, setFs] = useState(() => clampFont(store.get('fs', 13.5)));
  const [run, setRun] = useState<RunState>({ kind: 'empty' });
  const [busy, setBusy] = useState(false);
  const [armedReset, setArmedReset] = useState(false);

  const runId = useRef(0);
  const alive = useRef(true);
  const saveTimer = useRef<ReturnType<typeof setTimeout> | undefined>(undefined);
  const latest = useRef({ code, lang });
  latest.current = { code, lang };

  useEffect(() => {
    alive.current = true;
    document.title = `${p.title} · Letify`;
    return () => {
      alive.current = false;
      clearTimeout(saveTimer.current);
      store.set(codeKey(p.id, latest.current.lang), latest.current.code); // keep the last edit
    };
  }, [p]);

  // Start loading the Python runtime early so the first Run is quick.
  useEffect(() => {
    if (lang === 'python') ensurePython().catch(() => {});
  }, [lang]);

  const edit = (value: string) => {
    setCode(value);
    clearTimeout(saveTimer.current);
    saveTimer.current = setTimeout(() => store.set(codeKey(p.id, lang), value), 400);
  };

  const changeLang = (next: Lang) => {
    clearTimeout(saveTimer.current);
    store.set(codeKey(p.id, lang), code);
    store.set('lang', next);
    setLang(next);
    setCode(store.get<string | null>(codeKey(p.id, next), null) || starter(p, next));
    setRun({ kind: 'empty' });
  };

  const resetCode = () => {
    if (!armedReset) {
      setArmedReset(true);
      setTimeout(() => setArmedReset(false), 3000);
      return;
    }
    setArmedReset(false);
    edit(starter(p, lang));
    toast('Starter code restored');
  };

  const changeFont = (d: number) => {
    const n = clampFont(fs + d);
    setFs(n);
    store.set('fs', n);
  };

  const execute = useCallback(
    async (mode: 'run' | 'submit') => {
      if (busy) return;
      const { code: src, lang: l } = latest.current;
      setBusy(true);
      store.set(codeKey(p.id, l), src);
      const status = (text: string) => alive.current && setRun({ kind: 'busy', text });
      status(l === 'cpp' || l === 'java' ? 'Preparing...' : 'Running...');
      let tests = p.samples;
      try {
        if (mode === 'submit') tests = await loadTests(p.id);
      } catch {
        if (alive.current) {
          setRun({ kind: 'done', id: ++runId.current, verdict: { kind: 'engine', message: 'The test cases could not be loaded. Check your connection and try again.', total: 0, passed: 0 }, tests: [], mode, lang: l });
          setBusy(false);
        }
        return;
      }
      let eng;
      try {
        eng = await runEngine(l, p, src, tests, status);
      } catch (err) {
        eng = { status: 'engine_error' as const, message: String((err as Error)?.message ?? err) };
      }
      if (!alive.current) return;
      const verdict = makeVerdict(p, tests, eng);
      setRun({ kind: 'done', id: ++runId.current, verdict, tests, mode, lang: l });
      if (mode === 'submit' && verdict.kind === 'ac') {
        markSolved(p.id, l);
        toast('Accepted. Marked as solved.');
      }
      setBusy(false);
    },
    [busy, p, markSolved, toast],
  );

  const showEditorial = () => {
    setTab('edit');
    setPane('problem');
  };

  const isSolved = !!solved[p.id];

  return (
    <>
      <div className="pv-head">
        <Link className="back" to={{ name: 'problems' }}>
          &larr; All problems
        </Link>
        <h1>
          {idx + 1}. {p.title}
        </h1>
        <span className="pv-tags">
          <Pill diff={p.diff} />
          <span className="chip">{p.topic}</span>
          {isSolved && <span className="solved-badge">Solved</span>}
        </span>
        <span className="pv-nav">
          {prev && (
            <Link className="btn sm" to={{ name: 'problem', id: prev.id }} title={prev.title}>
              &larr; Previous
            </Link>
          )}
          {next && (
            <Link className="btn sm" to={{ name: 'problem', id: next.id }} title={next.title}>
              Next &rarr;
            </Link>
          )}
        </span>
      </div>

      <div className="seg mobile-seg">
        <button aria-pressed={pane === 'problem'} onClick={() => setPane('problem')}>
          Problem
        </button>
        <button aria-pressed={pane === 'code'} onClick={() => setPane('code')}>
          Code
        </button>
      </div>

      <div className="workspace" data-pane={pane}>
        <section className="pane problem">
          <div className="tabs" role="tablist">
            {TABS.map(([id, label]) => (
              <button key={id} role="tab" aria-selected={tab === id} onClick={() => setTab(id)}>
                {label}
              </button>
            ))}
          </div>
          <div className="scroll" role="tabpanel">
            {tab === 'desc' && <Description p={p} />}
            {tab === 'hints' && <Hints p={p} shown={hints} onMore={() => setHints((h) => h + 1)} />}
            {tab === 'edit' && <Editorial p={p} />}
          </div>
        </section>

        <section className="pane code">
          <div className="toolbar">
            <select aria-label="Language" value={lang} onChange={(e) => changeLang(e.target.value as Lang)}>
              {LANG_IDS.map((k) => (
                <option key={k} value={k}>
                  {LANGS[k].label}
                </option>
              ))}
            </select>
            <button className="btn ghost sm" onClick={resetCode}>
              {armedReset ? 'Click again to reset' : 'Reset code'}
            </button>
            <button className="btn ghost sm" onClick={() => changeFont(-1)} aria-label="Smaller text" title="Smaller text">
              A-
            </button>
            <button className="btn ghost sm" onClick={() => changeFont(1)} aria-label="Larger text" title="Larger text">
              A+
            </button>
            <button className="icon-btn" style={{ width: 34, height: 34 }} onClick={() => setSettings((s) => !s)} aria-label="Engine settings" aria-expanded={settings} title="Engine settings">
              <GearIcon />
            </button>
            <span className="grow" />
            <button className="btn" disabled={busy} onClick={() => execute('run')} title="Ctrl/Cmd + Enter">
              Run
            </button>
            <button className="btn primary" disabled={busy} onClick={() => execute('submit')} title="Ctrl/Cmd + Shift + Enter">
              Submit
            </button>
          </div>
          {settings && <EngineSettings />}
          <Editor value={code} lang={lang} fontSize={fs} onChange={edit} onRun={() => execute('run')} onSubmit={() => execute('submit')} />
          <Results p={p} state={run} onSeeEditorial={showEditorial} />
        </section>
      </div>
    </>
  );
}
