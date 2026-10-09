# Abhyas: a free LeetCode-style DSA practice site

26 problems in three stages (7 Easy, 13 Medium, 6 Hard), each with a statement, hidden test cases, three hints, an editorial with Big-O, and a reference solution. Everything is unlocked. Languages: Python, JavaScript, C++, Java.

The whole site is one file: `index.html`. No backend, no database, no login. Progress and your code are saved in the visitor's browser (localStorage).

## Run it

Open `index.html` in a browser, or serve the folder:

```
python3 -m http.server 8000      # then open http://localhost:8000
```

## Publish it for free

Upload `index.html` to any static host: GitHub Pages, Cloudflare Pages, Netlify or Vercel. All have free plans. Nothing else is needed.

## How code runs (and what is free)

| Language   | Where it runs                          | Cost |
|------------|----------------------------------------|------|
| JavaScript | Web Worker in the visitor's browser    | free |
| Python     | Pyodide (Python in WebAssembly), loaded from the jsDelivr CDN on first use (~10 MB) | free |
| C++, Java  | A Judge0 server over HTTPS             | free public server, or self-host |

- Python and JavaScript need no server, so they cost nothing and cannot be rate-limited.
- C++ and Java use Judge0 CE. The default URL is `https://ce.judge0.com`. Public servers can change their limits, so for a real launch run your own: Judge0 CE is open source and has a Docker setup (https://github.com/judge0/judge0). Then open any problem, click the gear icon, and paste your server URL. Visitors can also change it themselves.
- Infinite loops are stopped by a time limit (3.5 s for JavaScript, 5 s for Python, 5 s CPU for C++/Java).

## Add or change problems

Problems live in `problems.py`. Each one has a statement, test inputs and a **reference solution in Python**. The expected outputs are produced by running that reference, so you never type answers by hand.

```
python3 build.py
```

`build.py` runs every reference, checks 17 of them against brute force on 400 random small inputs each, checks all numbers fit in 32-bit integers, and rewrites `index.html`.

To add a problem, copy any `add(...)` block in `problems.py`. Supported parameter and return types: `int`, `bool`, `string`, `int[]`, `int[][]`. Compare modes: `exact`, `flat` (order of a list does not matter), `rows` (order of rows and of numbers inside each row does not matter).

Keep stress tests around 10,000 elements. Larger tests make `index.html` heavy for visitors.

## Files

- `index.html`: the finished site, a complete HTML page with landing page and SEO tags (generated)
- `template.html`: all the design and JavaScript
- `problems.py`: the problem bank
- `build.py`: generates `index.html`
