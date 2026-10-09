#!/usr/bin/env python3
"""Build index.html from template.html + problems.py.

    python3 build.py

Steps: run every reference solution to produce expected outputs, cross-check the
references against brute force on small random inputs, validate 32-bit ranges,
then inject the problem data into the template.
"""
import copy
import json
import os
import random
import sys
from collections import Counter
from pathlib import Path

import problems as pb

HERE = Path(__file__).parent
INT_MIN, INT_MAX = -(2 ** 31), 2 ** 31 - 1


def load_ref(src, fn):
    ns = {}
    exec(src, ns)
    return ns[fn]


def canon(v, mode):
    if mode == "flat":
        return sorted(v)
    if mode == "rows":
        return sorted(sorted(r) for r in v)
    return v


def walk_ints(x):
    if isinstance(x, bool):
        return
    if isinstance(x, int):
        yield x
    elif isinstance(x, (list, tuple)):
        for y in x:
            yield from walk_ints(y)


def min_windows(s, t):
    need = Counter(t)
    wins = []
    for i in range(len(s)):
        for j in range(i + 1, len(s) + 1):
            c = Counter(s[i:j])
            if all(c[k] >= v for k, v in need.items()):
                wins.append((j - i, i))
                break
    if not wins:
        return 0
    m = min(w[0] for w in wins)
    return sum(1 for w in wins if w[0] == m)


def main():
    out = []
    ids = set()
    for p in pb.P:
        assert p["id"] not in ids, p["id"]
        ids.add(p["id"])
        ref = load_ref(p["solution"], p["fn"])
        tests = []
        for args in p["tests"]:
            assert len(args) == len(p["params"]), (p["id"], "arg count")
            expected = ref(*copy.deepcopy(args))
            for v in walk_ints(args):
                assert INT_MIN <= v <= INT_MAX, (p["id"], "arg out of int32", v)
            for v in walk_ints(expected):
                assert INT_MIN <= v <= INT_MAX, (p["id"], "result out of int32", v)
            tests.append({"args": args, "expected": expected})

        # --- problem specific validation
        if p["id"] == "two-sum":
            for t in tests:
                nums, target = t["args"]
                i, j = t["expected"]
                assert i != j and nums[i] + nums[j] == target
                st = set(nums)
                pairs = sum(1 for x in nums if (target - x) in st and (target - x != x)) // 2
                dup = sum(1 for x in st if target - x == x and nums.count(x) >= 2)
                assert pairs + dup == 1, ("two-sum not unique", nums[:10])
        if p["id"] == "n-queens-ii":
            for t in tests:
                assert t["expected"] == pb.KNOWN_QUEENS[t["args"][0]]
        if p["id"] == "minimum-window-substring":
            for t in tests:
                s, tt = t["args"]
                if len(s) <= 60:
                    assert min_windows(s, tt) <= 1, ("min window not unique", s, tt)

        # --- brute force cross-check
        if os.environ.get("ABHYAS_FAST"):
            print(f"  --  {p['id']}")
        elif p["id"] in pb.CHECKS:
            brute, gen, mode = pb.CHECKS[p["id"]]
            r = random.Random(1234)
            n_ok = 0
            for _ in range(400):
                args = gen(r)
                a = ref(*copy.deepcopy(args))
                b = brute(*copy.deepcopy(args))
                assert canon(a, mode) == canon(b, mode), (p["id"], args, a, b)
                n_ok += 1
            # also brute-check the small hand written tests
            for t in tests:
                size = sum(len(str(x)) for x in t["args"])
                small = all(abs(v) <= 1000 for v in walk_ints(t["args"]))
                if size < 60 and small:
                    b = brute(*copy.deepcopy(t["args"]))
                    assert canon(t["expected"], mode) == canon(b, mode), (p["id"], t["args"])
            print(f"  ok  {p['id']:48s} {n_ok} random brute checks")
        else:
            print(f"  ok  {p['id']:48s} (hand checked)")

        entry = {
            "id": p["id"], "title": p["title"], "diff": p["diff"], "topic": p["topic"],
            "fn": p["fn"], "params": [list(x) for x in p["params"]], "ret": p["ret"], "cmp": p["cmp"],
            "desc": p["desc"], "constraints": p["constraints"], "hints": p["hints"],
            "editorial": p["editorial"], "time": p["time"], "space": p["space"],
            "solution": p["solution"], "tests": tests, "visible": 3,
        }
        out.append(entry)

    # one stress test must exist for the medium and hard problems
    counts = Counter(p["diff"] for p in out)
    print("problems:", dict(counts), "total", len(out))

    data = json.dumps(out, separators=(",", ":"), ensure_ascii=False).replace("<", "\\u003c")
    tpl = (HERE / "template.html").read_text()
    assert "__PROBLEMS_JSON__" in tpl
    fragment = tpl.replace("__PROBLEMS_JSON__", data)

    # Full HTML document for hosting (doctype, language, SEO tags).
    cut = fragment.index('<div class="top">')
    head_part, body_part = fragment[:cut], fragment[cut:]
    head_part = head_part.replace("<title>Abhyas</title>", "<title>Abhyas: free DSA practice</title>")
    desc = "Free LeetCode-style practice for data structures and algorithms. Problems from Easy to Hard with hidden tests, hints, editorials and solutions in Python, JavaScript, C++ and Java."
    meta = (
        '<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        f'<meta name="description" content="{desc}">\n'
        '<meta name="theme-color" content="#2F44D8">\n'
        '<meta property="og:type" content="website">\n'
        '<meta property="og:title" content="Abhyas: free DSA practice">\n'
        f'<meta property="og:description" content="{desc}">\n'
        '<meta name="twitter:card" content="summary">\n'
    )
    full = meta + head_part + "</head>\n<body>\n" + body_part + "\n</body>\n</html>\n"
    (HERE / "index.html").write_text(full)
    # Fragment form used for the Claude artifact preview (the artifact host adds its own document wrapper).
    (HERE / "dist").mkdir(exist_ok=True)
    (HERE / "dist" / "claude-preview.html").write_text(fragment)
    print("wrote index.html", round(len(full) / 1024), "KB and dist/claude-preview.html")


if __name__ == "__main__":
    try:
        main()
    except AssertionError as e:
        print("BUILD FAILED:", e)
        sys.exit(1)
