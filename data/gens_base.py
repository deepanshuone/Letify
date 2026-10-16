"""Random case generators for the first 9 hand-written problems (they have no brute-force checker).

Used only to top up the test count in build.py; expected outputs still come from the reference solution.
"""
import random


def _nums(r, lo, hi, n_lo, n_hi):
    return [r.randint(lo, hi) for _ in range(r.randint(n_lo, n_hi))]


def _contains_duplicate(r):
    return [_nums(r, -10, 10, 1, 12)]


def _valid_anagram(r):
    base = "".join(r.choice("abc") for _ in range(r.randint(0, 8)))
    if r.random() < 0.5:
        t = list(base)
        r.shuffle(t)
        t = "".join(t)
    else:
        t = "".join(r.choice("abc") for _ in range(r.randint(0, 8)))
    return [base, t]


def _two_sum(r):
    while True:
        nums = r.sample(range(-20, 21), r.randint(2, 10))
        i, j = r.sample(range(len(nums)), 2)
        target = nums[i] + nums[j]
        pairs = sum(1 for a in range(len(nums)) for b in range(a + 1, len(nums)) if nums[a] + nums[b] == target)
        if pairs == 1:
            return [nums, target]


def _valid_parentheses(r):
    if r.random() < 0.5:
        out, stack = [], []
        for _ in range(r.randint(0, 5)):
            c = r.choice("([{")
            stack.append({"(": ")", "[": "]", "{": "}"}[c])
            out.append(c)
            if r.random() < 0.5 and stack:
                out.append(stack.pop())
        out += stack[::-1]
        return ["".join(out)]
    return ["".join(r.choice("()[]{}") for _ in range(r.randint(0, 10)))]


def _best_time(r):
    return [[r.randint(0, 10) for _ in range(r.randint(1, 10))]]


def _binary_search(r):
    nums = sorted(r.sample(range(-30, 31), r.randint(1, 12)))
    target = r.choice(nums) if r.random() < 0.6 else r.randint(-32, 32)
    return [nums, target]


def _climbing_stairs(r):
    return [r.randint(1, 30)]


def _merge_intervals(r):
    out = []
    for _ in range(r.randint(1, 8)):
        s = r.randint(0, 20)
        out.append([s, s + r.randint(0, 6)])
    return [out]


def _n_queens(r):
    return [r.randint(1, 9)]


GENS = {
    "contains-duplicate": _contains_duplicate,
    "valid-anagram": _valid_anagram,
    "two-sum": _two_sum,
    "valid-parentheses": _valid_parentheses,
    "best-time-to-buy-and-sell-stock": _best_time,
    "binary-search": _binary_search,
    "climbing-stairs": _climbing_stairs,
    "merge-intervals": _merge_intervals,
    "n-queens-ii": _n_queens,
}
