#!/usr/bin/env python3
"""Build the problem data the website reads (src/data/problems.json and src/data/tests/<id>.json).

    python3 data/build.py

Steps: run every reference solution to produce expected outputs, cross-check the
references against brute force on small random inputs, validate 32-bit ranges,
then write JSON. The generated files are committed, so the website builds without Python.
"""
import copy
import json
import os
import random
import re
import sys
from collections import Counter
from pathlib import Path

import lib

HERE = Path(__file__).parent
ROOT = HERE.parent
OUT = ROOT / "src" / "data"
TESTS = OUT / "tests"
VISIBLE = 3  # sample cases shown by Run and in the statement
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
    if mode == "rowset":
        return sorted(v)
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


ALLOWED_TAGS = {"p", "code", "sup", "sub", "em", "strong", "b", "i", "ul", "ol", "li", "br", "pre"}


def check_html(pid, fragments):
    """The site renders statements, hints and editorials as HTML. Only plain formatting tags are allowed."""
    for frag in fragments:
        for tag in re.findall(r"<\s*/?\s*([A-Za-z][A-Za-z0-9]*)", frag):
            assert tag.lower() in ALLOWED_TAGS, (pid, "tag not allowed in problem text", tag)
        assert not re.search(r"<[^>]*\s(on\w+|style|href|src)\s*=", frag, re.I), (pid, "attribute not allowed")


RANK = {"Easy": 0, "Medium": 1, "Hard": 2}


def main(only=None, write=True):
    """Validate every problem and (unless `only` is given) write the JSON for the site.

    python3 data/build.py                   build everything
    python3 data/build.py --only bank.dp    validate just one bank module, write nothing
    """
    if only:
        import importlib
        importlib.import_module(only)
        plist = list(lib.P)
        write = False
    else:
        import problems as pb  # registers every problem
        plist = list(pb.P)
    plist.sort(key=lambda p: RANK[p["diff"]])  # Easy, then Medium, then Hard; registration order inside each
    out = []
    all_tests = {}
    ids = set()
    for p in plist:
        assert p["id"] not in ids, p["id"]
        ids.add(p["id"])
        check_html(p["id"], [p["desc"], *p["constraints"], *p["hints"], *p["editorial"]])
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
                assert t["expected"] == {1: 1, 2: 0, 3: 0, 4: 2, 5: 10, 6: 4, 7: 40, 8: 92, 9: 352}[t["args"][0]]
        if p["id"] in lib.VALIDATE:
            lib.VALIDATE[p["id"]](tests)
        if p["id"] == "minimum-window-substring":
            for t in tests:
                s, tt = t["args"]
                if len(s) <= 60:
                    assert min_windows(s, tt) <= 1, ("min window not unique", s, tt)

        # --- brute force cross-check
        if os.environ.get("LETIFY_FAST"):
            print(f"  --  {p['id']}")
        elif p["id"] in lib.CHECKS:
            brute, gen, mode = lib.CHECKS[p["id"]]
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

        meta = {
            "id": p["id"], "title": p["title"], "diff": p["diff"], "topic": p["topic"],
            "fn": p["fn"], "params": [list(x) for x in p["params"]], "ret": p["ret"], "cmp": p["cmp"],
            "desc": p["desc"], "constraints": p["constraints"], "hints": p["hints"],
            "editorial": p["editorial"], "time": p["time"], "space": p["space"],
            "solution": p["solution"], "visible": VISIBLE, "testCount": len(tests),
            # sample cases ship with the problem; the full set (hidden and large cases) loads when needed
            "samples": tests[:VISIBLE],
        }
        out.append(meta)
        all_tests[p["id"]] = tests

    counts = Counter(p["diff"] for p in out)
    print("problems:", dict(counts), "total", len(out))

    def dump(obj):
        # "<" is escaped so the JSON can never end a script tag if it is ever inlined
        return json.dumps(obj, separators=(",", ":"), ensure_ascii=False).replace("<", "\\u003c")

    if not write:
        print("validated only (nothing written)")
        return
    OUT.mkdir(parents=True, exist_ok=True)
    TESTS.mkdir(parents=True, exist_ok=True)
    for old in TESTS.glob("*.json"):
        old.unlink()
    (OUT / "problems.json").write_text(dump(out) + "\n")
    for pid, tests in all_tests.items():
        (TESTS / f"{pid}.json").write_text(dump(tests) + "\n")
    total = sum(len(t) for t in all_tests.values())
    print(f"wrote {OUT.relative_to(ROOT)}/problems.json and {len(all_tests)} test files ({total} test cases)")


if __name__ == "__main__":
    try:
        only = sys.argv[sys.argv.index("--only") + 1] if "--only" in sys.argv else None
        main(only)
    except AssertionError as e:
        print("BUILD FAILED:", e)
        sys.exit(1)
