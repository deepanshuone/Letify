import { CPP_PREFIX_LINES, JAVA_PREFIX_LINES, MARK, buildStdin, cppProgram, javaProgram } from '../core/drivers';
import { JUDGE0_IDS } from '../core/languages';
import type { EngineConfig } from '../core/storage';
import type { CaseResult, EngineResult, Problem, Status, TestCase } from '../types';

/* C++ and Java are compiled and run by a Judge0 server (open-source online judge). */

export function b64(s: string): string {
  const bytes = new TextEncoder().encode(s);
  let bin = '';
  for (let i = 0; i < bytes.length; i += 0x8000) bin += String.fromCharCode(...bytes.subarray(i, i + 0x8000));
  return btoa(bin);
}

export function unb64(s: string): string {
  const bin = atob(s);
  const bytes = new Uint8Array(bin.length);
  for (let i = 0; i < bin.length; i++) bytes[i] = bin.charCodeAt(i);
  return new TextDecoder().decode(bytes);
}

const sleep = (ms: number) => new Promise<void>((r) => setTimeout(r, ms));

/** Compiler messages mention lines of the wrapped program; subtract the lines the driver added. */
export function shiftLines(text: string, offset: number): string {
  return text
    .replace(/(?:main\.cpp|Main\.java|prog\.cpp)(?::(\d+))(?::\d+)?/g, (m, n: string) => {
      const k = parseInt(n, 10) - offset;
      return k > 0 ? `line ${k}` : m;
    })
    // g++ prints the offending source line with its number in the margin ("    7 |"); fix those numbers too
    .replace(/^( *)(\d+)( \|)/gm, (m, sp: string, n: string, bar: string) => {
      const k = parseInt(n, 10) - offset;
      return k > 0 ? sp + String(k).padStart(n.length) + bar : m;
    })
    .slice(0, 2500);
}

interface Judge0Result {
  status?: { id: number; description?: string };
  stdout?: string | null;
  stderr?: string | null;
  compile_output?: string | null;
  message?: string | null;
  time?: string | null;
}

export interface Judge0Deps {
  fetch: typeof fetch;
  /** Delay between polls; tests pass 0. */
  pollDelay?: (i: number) => number;
}

export async function runJudge0(
  lang: 'cpp' | 'java',
  p: Pick<Problem, 'fn' | 'params' | 'ret'>,
  code: string,
  tests: TestCase[],
  cfg: EngineConfig,
  onStatus: Status,
  deps: Judge0Deps = { fetch: (...a) => fetch(...a) },
): Promise<EngineResult> {
  const base = cfg.url.replace(/\/+$/, '');
  const headers: Record<string, string> = { 'Content-Type': 'application/json' };
  if (cfg.token) headers['X-Auth-Token'] = cfg.token;
  const src = lang === 'cpp' ? cppProgram(p, code) : javaProgram(p, code);
  const prefix = lang === 'cpp' ? CPP_PREFIX_LINES : JAVA_PREFIX_LINES;
  const body = JSON.stringify({
    source_code: b64(src),
    language_id: JUDGE0_IDS[lang],
    stdin: b64(buildStdin(p, tests)),
    cpu_time_limit: 5,
    wall_time_limit: 12,
    memory_limit: 256000,
  });
  const delay = deps.pollDelay ?? ((i: number) => (i < 3 ? 500 : 900));

  onStatus('Sending to the Judge0 server...');
  let res: Response;
  try {
    res = await deps.fetch(`${base}/submissions?base64_encoded=true&wait=false`, { method: 'POST', headers, body });
  } catch {
    return {
      status: 'engine_error',
      message: `Could not reach the Judge0 server at ${base}.\nC++ and Java are compiled on a Judge0 server, which needs a network connection and a host that allows requests from this site. Open Engine settings (gear icon) to change the server URL, or use Python / JavaScript, which run entirely in your browser.`,
    };
  }
  if (!res.ok) {
    const t = await res.text().catch(() => '');
    return { status: 'engine_error', message: `The Judge0 server answered with HTTP ${res.status}. ${t.slice(0, 200)}` };
  }
  const sub = (await res.json()) as { token: string };
  onStatus('Compiling and running...');

  for (let i = 0; i < 70; i++) {
    await sleep(delay(i));
    let r: Response;
    try {
      r = await deps.fetch(`${base}/submissions/${sub.token}?base64_encoded=true&fields=status,stdout,stderr,compile_output,message,time`, { headers });
    } catch {
      return { status: 'engine_error', message: 'Lost connection to the Judge0 server while waiting for the result.' };
    }
    if (!r.ok) return { status: 'engine_error', message: `Judge0 answered with HTTP ${r.status} while fetching the result.` };
    const d = (await r.json()) as Judge0Result;
    const sid = d.status?.id ?? 0;
    if (sid <= 2) continue; // queued or running

    const dec = (x?: string | null) => (x ? unb64(x) : '');
    const stdout = dec(d.stdout);
    const stderr = dec(d.stderr);
    const comp = dec(d.compile_output);
    const msg = dec(d.message);
    if (sid === 6) return { status: 'compile_error', message: shiftLines((comp || msg).trim(), prefix) };
    if (sid === 13 || sid === 14) return { status: 'engine_error', message: `Judge0 reported an internal error. ${msg.slice(0, 200)}` };

    const cases: CaseResult[] = [];
    const other: string[] = [];
    for (const line of stdout.split('\n')) {
      if (line.startsWith(MARK)) {
        try {
          cases.push({ ok: true, value: JSON.parse(line.slice(MARK.length)), ms: 0 });
        } catch {
          cases.push({ ok: false, error: 'Could not read the output of this test case.', ms: 0 });
        }
      } else if (line.length) other.push(line);
    }
    const eng: Extract<EngineResult, { status: 'ok' }> = {
      status: 'ok',
      cases,
      stdout: other.join('\n').slice(0, 4000),
      ms: parseFloat(d.time || '0') * 1000,
    };
    if (sid === 5) eng.timedOut = true;
    else if (sid >= 7 && sid <= 12) {
      eng.fatal = shiftLines((stderr || msg || d.status?.description || 'Runtime error').trim(), prefix).slice(0, 1500);
    }
    return eng;
  }
  return { status: 'engine_error', message: 'The Judge0 server took too long to answer. Try again in a moment.' };
}
