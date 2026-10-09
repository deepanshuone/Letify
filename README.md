# Letify: free DSA practice

A free LeetCode-style practice site for data structures and algorithms. 62 problems in three stages (16 Easy, 33 Medium, 13 Hard), each with a statement, hidden tests, three hints, an editorial with Big-O and a reference solution. Everything is unlocked. Languages: Python, JavaScript, C++ and Java.

**Features** (ideas taken from LeetCode, HackerRank and CodeChef; all problem statements are original)

- Study plans (7 guided paths with progress bars), daily challenge, random problem, topic and status filters, starred problems
- Profile with solved counts, day streak, activity heatmap, XP levels and 26 badges
- Every submission is kept with its code (restore it in one click); private notes per problem
- Custom input: run your code on any input you type
- Virtual contests: 4 problems, 90 minutes, points 3/5/8 and a 5-minute penalty per wrong submission, hints closed until it ends
- Optional free accounts: progress and code sync across devices (Supabase); export and import as a file works without any account

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

## Accounts and cloud sync (optional)

Without setup the site works fully and keeps everything in the visitor's browser. To add sign-in and sync:

1. Create a free project at https://supabase.com.
2. In the SQL editor, run `supabase/schema.sql` once. It creates one table and row-level-security rules, so a visitor can only read and write their own row.
3. In **Authentication → URL Configuration**, add your site URL (for example `https://<user>.github.io/Letify/`) to the allowed redirect URLs. Optionally switch on Google or GitHub under **Providers**.
4. In the GitHub repository open **Settings → Secrets and variables → Actions → Variables** and add `SUPABASE_URL` and `SUPABASE_ANON_KEY` (Project settings → API; the anon key is meant to be public). Add `AUTH_PROVIDERS` (for example `google,github`) if you enabled OAuth providers. Re-run the workflow.

For local work put `VITE_SUPABASE_URL`, `VITE_SUPABASE_ANON_KEY` and `VITE_AUTH_PROVIDERS` in `.env.local`.

Sync merges the data of two devices entry by entry (newest edit wins per problem, submissions are unioned), so nothing is lost when both are used offline. The browser tests run the real Supabase client against an in-memory fake of the endpoints (`tests/helpers/fakeSupabase.ts`); the SQL itself is not exercised by them, so run a first sign-in on your own project to confirm the setup.

There is no global leaderboard on purpose: scores that are checked in the visitor's own browser cannot be trusted.

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

Problems live in `data/problems.py` and `data/bank/*.py` (check one module with `python3 data/build.py --only bank.dp`). Each one has a statement, test inputs and a **reference solution in Python**. Expected outputs come from running that reference, so answers are never typed by hand.

```
npm run data     # python3 data/build.py
```

`data/build.py` runs every reference, cross-checks the ones that have a brute-force version against it on 400 random small inputs each, checks that all numbers fit in 32-bit integers and writes `src/data/problems.json` plus one `src/data/tests/<id>.json` per problem. The generated files are committed, so the website builds without Python; CI re-runs the script and fails if they are out of date.

To add a problem, copy any `add(...)` block. Supported parameter and return types: `int`, `bool`, `string`, `int[]`, `int[][]`. Compare modes: `exact`, `flat` (order of a list does not matter), `rows` (order of rows and of numbers inside each row does not matter), `rowset` (only the order of the rows does not matter). Keep stress tests around 10,000 elements.

## Browser tests

`npm run e2e` serves `dist/` and drives a real Chromium: navigation, the editor, JavaScript, Python (real Pyodide), C++ and Java (a stand-in Judge0 that compiles with your local `g++` / `javac`), settings, persistence, study plans, profile, contest, notes, custom input, sign-in and sync between two browsers (second build in `dist-cloud/` against a fake Supabase), the phone layout, and a check that nothing is blocked by the Content-Security-Policy. Set `CHROMIUM_PATH` to use a specific browser, or run `npx playwright-core install chromium` first.

## Project layout

```
data/            problem bank and generator (Python)
src/core/        types of code, drivers for C++/Java, verdicts, highlighter, editor keys, storage
src/engines/     JavaScript worker, Python worker (Pyodide), Judge0 client
src/user/        learner data model and merge, stats and badges, contest rules, cloud sync, Supabase client
src/state/       React providers (user data, cloud, contest, sign-in dialog)
src/components/  editor, results, tabs, header, heatmap
src/pages/       landing, problems, problem page, plans, profile, contest
src/data/        generated problem data (do not edit by hand) and study plans
data/bank/       problem bank split by topic (arrays, dp, graphs)
supabase/        schema.sql for the optional accounts
tests/           unit tests    e2e/  browser tests
```
