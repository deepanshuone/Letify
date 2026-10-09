// Copies the Pyodide runtime (Python in WebAssembly) from node_modules into public/pyodide so the site serves it
// itself. That removes a third-party script dependency and lets Python work offline after the first visit.
import { cpSync, existsSync, mkdirSync, readFileSync, rmSync, writeFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = join(dirname(fileURLToPath(import.meta.url)), '..');
const src = join(root, 'node_modules', 'pyodide');
const dst = join(root, 'public', 'pyodide');

if (!existsSync(src)) {
  console.error('pyodide is not installed. Run `npm install` first.');
  process.exit(1);
}
const version = JSON.parse(readFileSync(join(src, 'package.json'), 'utf8')).version;
const stamp = join(dst, '.version');
if (existsSync(stamp) && readFileSync(stamp, 'utf8').trim() === version) process.exit(0);

rmSync(dst, { recursive: true, force: true });
mkdirSync(dst, { recursive: true });
// Only the files the loader needs; skip typings, sources and docs.
for (const f of ['pyodide.mjs', 'pyodide.asm.js', 'pyodide.asm.wasm', 'python_stdlib.zip', 'pyodide-lock.json']) {
  if (!existsSync(join(src, f))) {
    console.error(`Expected ${f} in node_modules/pyodide but it is missing (pyodide ${version}).`);
    process.exit(1);
  }
  cpSync(join(src, f), join(dst, f));
}
writeFileSync(stamp, version + '\n');
console.log(`Copied Pyodide ${version} to public/pyodide`);
