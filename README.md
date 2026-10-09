# Letify: free DSA practice

A free LeetCode-style practice site for data structures and algorithms. 26 problems in three stages (7 Easy, 13 Medium, 6 Hard), each with a statement, hidden tests, three hints, an editorial with Big-O and a reference solution. Everything is unlocked. Languages: Python, JavaScript, C++ and Java.

**Stack:** TypeScript, React and Vite for the site. Python (only for the build) generates the problem data. Python and JavaScript solutions run in the visitor's browser; C++ and Java run on a Judge0 server. It is a static site, so it can be hosted for free.

## Run it

```
npm install
npm run dev          # http://localhost:5173
```

```
npm test             # unit tests (real Pyodide, real g++ and javac)
npm run typecheck
npm run build        # production build in dist/
npm run e2e          # browser tests against dist/ (needs Chromium; see below)
```

## Publish it (GitHub Pages)

The workflow in `.github/workflows/ci.yml` tests, builds and deploys on every push to `main`.
One-time setup: **Settings → Pages → Build and deployment → Source: GitHub Actions.**

The build uses relative paths, so the same `dist/` also works on Cloudflare Pages, Netlify or any static host (no server rules are needed, routes use the URL hash).

## How code runs (and what is free)

| Language   | Where it runs                                              | Cost |
|------------|------------------------------------------------------------|------|
| JavaScript | A Web Worker in the visitor's browser                      | free |
| Python     | Pyodide (Python in WebAssembly), served from this site (about 10 MB, loaded on first use) | free |
| C++, Java  | A Judge0 server over HTTPS                                 | free public server, or self-host |

- Visitor code never runs on the page itself: it runs in a Web Worker, and an infinite loop is stopped by terminating the worker (3.5 s per case for JavaScript, 5 s for Python, 5 s CPU for C++ and Java).
- C++ and Java use Judge0 CE. The default is `https://ce.judge0.com`. Public servers can change their limits, so for a real launch run your own (https://github.com/judge0/judge0, Docker) and enter its URL under the gear icon on any problem. Only `https://` URLs (or `localhost`) are accepted.

## Security notes

- No secrets in the frontend. The Judge0 token, if you use one, is typed by the visitor and stays in their browser.
- A strict Content-Security-Policy is added to the production build: no inline or third-party scripts, fonts and Pyodide are served from the site itself. Visitor code runs in Web Workers loaded from files, so the page does not need `unsafe-eval`.
- Problem statements are HTML written in `data/problems.py`. The data build only allows plain formatting tags (`p`, `code`, `sup`, ...) and no attributes.
- Dependencies are pinned by `package-lock.json`. Pyodide is pinned to one version (`pyodide` in `package.json`).

## Add or change problems

Problems live in `data/problems.py`. Each one has a statement, test inputs and a **reference solution in Python**. Expected outputs come from running that reference, so answers are never typed by hand.

```
npm run data     # python3 data/build.py
```

`data/build.py` runs every reference, cross-checks 17 of them against brute force on 400 random small inputs each, checks that all numbers fit in 32-bit integers and writes `src/data/problems.json` plus one `src/data/tests/<id>.json` per problem. The generated files are committed, so the website builds without Python; CI re-runs the script and fails if they are out of date.

To add a problem, copy any `add(...)` block. Supported parameter and return types: `int`, `bool`, `string`, `int[]`, `int[][]`. Compare modes: `exact`, `flat` (order of a list does not matter), `rows` (order of rows and of numbers inside each row does not matter). Keep stress tests around 10,000 elements.

## Browser tests

`npm run e2e` serves `dist/` and drives a real Chromium: navigation, the editor, JavaScript, Python (real Pyodide), C++ and Java (a stand-in Judge0 that compiles with your local `g++` / `javac`), settings, persistence, the phone layout, and a check that nothing is blocked by the Content-Security-Policy. Set `CHROMIUM_PATH` to use a specific browser, or run `npx playwright-core install chromium` first.

## Project layout

```
data/            problem bank and generator (Python)
src/core/        types of code, drivers for C++/Java, verdicts, highlighter, editor keys, storage
src/engines/     JavaScript worker, Python worker (Pyodide), Judge0 client
src/components/  editor, results, tabs, header
src/pages/       landing, problem list, problem page
src/data/        generated problem data (do not edit by hand)
tests/           unit tests    e2e/  browser tests
```
