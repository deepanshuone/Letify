import { BRAND } from '../config';
import { useCallback, useEffect, useRef, useState } from 'react';
import { Editor } from '../components/Editor';
import { EngineSettings } from '../components/EngineSettings';
import { CustomInput, type CustomResult } from '../components/CustomInput';
import { NotesTab } from '../components/NotesTab';
import { Description, Editorial, Hints } from '../components/ProblemTabs';
import { Results, type RunState } from '../components/Results';
import { SubmissionsTab } from '../components/SubmissionsTab';
import { GearIcon, Link, Pill } from '../components/common';
import { LANGS, LANG_IDS, isLang, starter } from '../core/languages';
import { store } from '../core/storage';
import { makeVerdict } from '../core/verdict';
import { PROBLEMS, loadTests } from '../data';
import { ensurePython, runEngine } from '../engines';
import { useContest } from '../state/contest';
import { useToast } from '../state/toast';
import { useUserData } from '../state/userdata';
import type { Lang, Problem, Value } from '../types';
import { PENALTY_MINUTES, clock } from '../user/contest';

type Tab = 'desc' | 'hints' | 'edit' | 'subs' | 'notes';
const TABS: [Tab, string][] = [
  ['desc', 'Description'],
  ['hints', 'Hints'],
  ['edit', 'Editorial'],
  ['subs', 'Submissions'],
  ['notes', 'Notes'],
];

function ClosedNote({ what }: { what: string }) {
  return <p className="note">{what} are closed for this problem while your contest is running. They open again when it ends.</p>;
}

const clampFont = (n: number) => Math.min(20, Math.max(11, n));

function savedLang(): Lang {
  const l = store.get<unknown>('lang', 'python');
  return isLang(l) ? l : 'python';
}

function ContestBanner({ pid }: { pid: string }) {
  const c = useContest();
  const a = c.active;
  if (!a || !a.ids.includes(pid)) return null;
  const left = a.end - c.now;
  const solvedAt = a.solved[pid];
  const wrong = a.wrong[pid] ?? 0;
  return (
    <div className="contest-banner" role="status">
      <b>Contest running</b>
      <span className="tnum" role="timer" aria-label="Time left in the contest">
        {clock(left)}
      </span>
      <span className="muted">
        {solvedAt !== undefined ? 'Solved in this contest.' : wrong ? `${wrong} wrong attempt${wrong === 1 ? '' : 's'} (+${wrong * PENALTY_MINUTES} min)` : 'Hints and editorial are closed until the contest ends.'}
      </span>
      <Link className="btn sm" to={{ name: 'contest' }}>
        Contest page
      </Link>
    </div>
  );
}

export function ProblemPage({ p }: { p: Problem }) {
  const toast = useToast();
  const ud = useUserData();
  const contest = useContest();
  const { solved, stars, subs: allSubs, notes } = ud.data;
  const idx = PROBLEMS.indexOf(p);
  const prev = PROBLEMS[idx - 1];
  const next = PROBLEMS[idx + 1];
  const locked = contest.locked(p.id);

  const [lang, setLang] = useState<Lang>(savedLang);
  const [code, setCode] = useState(() => ud.getCode(p.id, savedLang()) || starter(p, savedLang()));
  const [tab, setTab] = useState<Tab>('desc');
  const [hints, setHints] = useState(0);
  const [pane, setPane] = useState<'problem' | 'code'>('problem');
  const [settings, setSettings] = useState(false);
  const [bottom, setBottom] = useState<'results' | 'custom'>('results');
  const [fs, setFs] = useState(() => clampFont(store.get('fs', 13.5)));
  const [run, setRun] = useState<RunState>({ kind: 'empty' });
  const [busy, setBusy] = useState(false);
  const [armedReset, setArmedReset] = useState(false);

  const runId = useRef(0);
  const alive = useRef(true);
  const saveTimer = useRef<ReturnType<typeof setTimeout> | undefined>(undefined);
  const latest = useRef({ code, lang });
  latest.current = { code, lang };
  const udRef = useRef(ud);
  udRef.current = ud;
  const contestRef = useRef(contest);
  contestRef.current = contest;

  useEffect(() => {
    alive.current = true;
    document.title = `${p.title} · ${BRAND}`;
    return () => {
      alive.current = false;
      clearTimeout(saveTimer.current);
      udRef.current.setCode(p.id, latest.current.lang, latest.current.code); // keep the last edit
    };
  }, [p]);

  // Start loading the Python runtime early so the first Run is quick.
  useEffect(() => {
    if (lang === 'python') ensurePython().catch(() => {});
  }, [lang]);

  const edit = (value: string) => {
    setCode(value);
    clearTimeout(saveTimer.current);
    saveTimer.current = setTimeout(() => ud.setCode(p.id, lang, value), 400);
  };

  const switchTo = (next: Lang, nextCode?: string) => {
    clearTimeout(saveTimer.current);
    ud.setCode(p.id, lang, code);
    store.set('lang', next);
    setLang(next);
    const c = nextCode ?? (ud.getCode(p.id, next) || starter(p, next));
    setCode(c);
    if (nextCode !== undefined) ud.setCode(p.id, next, nextCode);
    setRun({ kind: 'empty' });
  };
  const changeLang = (next: Lang) => switchTo(next);

  const restore = (l: Lang, c: string) => {
    if (l === lang) edit(c);
    else switchTo(l, c);
    setPane('code');
    toast('Code restored in the editor');
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
      setBottom('results');
      clearTimeout(saveTimer.current);
      udRef.current.setCode(p.id, l, src);
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
      const verdict = makeVerdict(p, tests, eng);
      // A judged submission counts even when the learner has already moved to another page.
      if (mode === 'submit' && verdict.kind !== 'engine') {
        const wasSolved = !!udRef.current.getData().solved[p.id];
        udRef.current.recordSubmission({ pid: p.id, lang: l, verdict: verdict.kind, passed: verdict.passed, total: verdict.total, ms: 'ms' in verdict ? verdict.ms : 0, code: src });
        contestRef.current.report(p.id, verdict.kind);
        if (verdict.kind === 'ac' && alive.current) toast(wasSolved ? 'Accepted.' : 'Accepted. Marked as solved.');
      }
      if (!alive.current) return;
      setRun({ kind: 'done', id: ++runId.current, verdict, tests, mode, lang: l });
      setBusy(false);
    },
    [busy, p, toast],
  );

  const customRun = useCallback(
    async (args: Value[]): Promise<CustomResult> => {
      const { code: src, lang: l } = latest.current;
      setBusy(true);
      try {
        const eng = await runEngine(l, p, src, [{ args, expected: p.samples[0]!.expected }], () => {});
        if (eng.status === 'compile_error') return { kind: 'error', title: 'Compile error', message: eng.message };
        if (eng.status === 'engine_error') return { kind: 'error', title: 'The runner could not start', message: eng.message };
        const c = eng.cases[0];
        if (!c) return { kind: 'error', title: eng.timedOut ? 'Time limit exceeded' : 'No result', message: eng.fatal ?? (eng.timedOut ? 'Your code took too long on this input.' : 'The runner stopped before the case finished.') };
        if (!c.ok) return { kind: 'error', title: 'Runtime error', message: c.error ?? 'Runtime error' };
        return { kind: 'value', value: c.value, stdout: c.stdout ?? eng.stdout ?? '', ms: c.ms ?? 0 };
      } catch (err) {
        return { kind: 'error', title: 'The runner could not start', message: String((err as Error)?.message ?? err) };
      } finally {
        setBusy(false);
      }
    },
    [p],
  );

  const showEditorial = () => {
    setTab('edit');
    setPane('problem');
  };

  const isSolved = !!solved[p.id];
  const isStarred = !!stars[p.id]?.on;
  const mySubs = allSubs.filter((x) => x.pid === p.id);

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
          <button className={`star-btn${isStarred ? ' on' : ''}`} aria-pressed={isStarred} aria-label={isStarred ? 'Remove star' : 'Star this problem'} title={isStarred ? 'Remove star' : 'Star this problem'} onClick={() => ud.toggleStar(p.id)}>
            {isStarred ? '\u2605' : '\u2606'}
          </button>
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

      <ContestBanner pid={p.id} />

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
            {tab === 'hints' && (locked ? <ClosedNote what="Hints" /> : <Hints p={p} shown={hints} onMore={() => setHints((h) => h + 1)} />)}
            {tab === 'edit' && (locked ? <ClosedNote what="The editorial" /> : <Editorial p={p} />)}
            {tab === 'subs' && <SubmissionsTab subs={mySubs} onRestore={restore} />}
            {tab === 'notes' && <NotesTab key={p.id} value={notes[p.id]?.text ?? ''} onSave={(t) => ud.setNote(p.id, t)} />}
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
          <div className="bottom-tabs" role="tablist" aria-label="Output">
            <button role="tab" aria-selected={bottom === 'results'} onClick={() => setBottom('results')}>
              Results
            </button>
            <button role="tab" aria-selected={bottom === 'custom'} onClick={() => setBottom('custom')}>
              Custom input
            </button>
          </div>
          {bottom === 'results' ? <Results p={p} state={run} onSeeEditorial={showEditorial} /> : <CustomInput key={p.id} p={p} busy={busy} onRun={customRun} />}
        </section>
      </div>
    </>
  );
}
