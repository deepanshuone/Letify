/* A stand-in for a Judge0 server that really compiles and runs C++ / Java with the local g++ and javac.
   Used by the unit tests and the browser tests so the whole C++/Java path is exercised without the network. */
import { spawnSync } from 'node:child_process';
import { mkdtempSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';

export const hasToolchain = (() => {
  const ok = (cmd: string, args: string[]) => spawnSync(cmd, args, { stdio: 'ignore' }).status === 0;
  return { cpp: ok('g++', ['--version']), java: ok('javac', ['-version']) && ok('java', ['-version']) };
})();

const b64 = (s: string) => Buffer.from(s, 'utf8').toString('base64');
const unb64 = (s: string) => Buffer.from(s, 'base64').toString('utf8');

interface Stored {
  stdout?: string;
  stderr?: string;
  compile_output?: string;
  time?: string;
}
const results = new Map<string, Stored & { statusId: number }>();
let counter = 0;

function judge(languageId: number, source: string, stdin: string) {
  const dir = mkdtempSync(join(tmpdir(), 'j0-'));
  try {
    const isCpp = languageId === 54;
    writeFileSync(join(dir, isCpp ? 'main.cpp' : 'Main.java'), source);
    const compile = isCpp
      ? spawnSync('g++', ['-O1', '-std=c++17', 'main.cpp', '-o', 'prog'], { cwd: dir, encoding: 'utf8' })
      : spawnSync('javac', ['Main.java'], { cwd: dir, encoding: 'utf8' });
    if (compile.status !== 0) {
      return { statusId: 6, compile_output: b64(compile.stderr || compile.stdout || 'compile failed') };
    }
    const t0 = Date.now();
    const run = isCpp
      ? spawnSync('./prog', [], { cwd: dir, input: stdin, encoding: 'utf8', timeout: 5000, maxBuffer: 64 << 20 })
      : spawnSync('java', ['Main'], { cwd: dir, input: stdin, encoding: 'utf8', timeout: 8000, maxBuffer: 64 << 20 });
    const time = ((Date.now() - t0) / 1000).toFixed(3);
    if (run.error && (run.error as NodeJS.ErrnoException).code === 'ETIMEDOUT') {
      return { statusId: 5, stdout: b64(run.stdout ?? ''), time };
    }
    if (run.status !== 0) {
      return { statusId: 11, stdout: b64(run.stdout ?? ''), stderr: b64(run.stderr ?? ''), time };
    }
    return { statusId: 3, stdout: b64(run.stdout ?? ''), time };
  } finally {
    rmSync(dir, { recursive: true, force: true });
  }
}

/** Handles the two Judge0 calls the site makes. Returns the HTTP status and JSON body. */
export function handleJudge0(method: string, path: string, body: string | null): { status: number; json: unknown } {
  if (method === 'POST' && path.startsWith('/submissions')) {
    const req = JSON.parse(body ?? '{}') as { source_code: string; language_id: number; stdin: string };
    const token = `tok-${++counter}`;
    results.set(token, judge(req.language_id, unb64(req.source_code), unb64(req.stdin)));
    return { status: 201, json: { token } };
  }
  const m = /^\/submissions\/([^?]+)/.exec(path);
  if (method === 'GET' && m) {
    const r = results.get(m[1]!);
    if (!r) return { status: 404, json: { error: 'unknown token' } };
    const { statusId, ...rest } = r;
    return { status: 200, json: { status: { id: statusId, description: `status ${statusId}` }, ...rest } };
  }
  return { status: 404, json: {} };
}

/** A fetch() replacement for unit tests. */
export const fakeFetch: typeof fetch = async (input, init) => {
  const u = new URL(typeof input === 'string' ? input : input instanceof URL ? input.href : input.url);
  const r = handleJudge0(init?.method ?? 'GET', u.pathname + u.search, (init?.body as string | undefined) ?? null);
  return new Response(JSON.stringify(r.json), { status: r.status, headers: { 'Content-Type': 'application/json' } });
};
