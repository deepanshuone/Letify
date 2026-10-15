"""Problems: arrays & hashing, sets and set operations. See data/lib.py for the registry."""
import heapq
from collections import Counter

from lib import add, rnd, CHECKS, VALIDATE, gen_arr  # noqa: F401

INT_MIN, INT_MAX = -(2 ** 31), 2 ** 31 - 1
TOPIC = "Arrays & Hashing"


# ---------------------------------------------------------------- EASY

p = add(
    id="intersection-of-two-arrays-unique", title="Intersection of Two Arrays", diff="Easy", topic=TOPIC,
    fn="intersectionUnique", params=[("a", "int[]"), ("b", "int[]")], ret="int[]", cmp="exact",
    desc="<p>Given two integer arrays <code>a</code> and <code>b</code>, return the values that occur in <strong>both</strong> arrays. Each common value must be reported exactly once, no matter how many copies of it the arrays contain, and the result must be sorted in increasing order.</p><p>For example, <code>a = [4, 9, 5, 9]</code> and <code>b = [9, 4, 9, 8, 4]</code> give <code>[4, 9]</code>. If there is no common value, return an empty array.</p>",
    constraints=["0 &le; a.length, b.length &le; 5,000", "-10<sup>9</sup> &le; a[i], b[i] &le; 10<sup>9</sup>", "The result is sorted ascending and has no repeated values"],
    hints=["Checking every pair of elements works but is O(n &middot; m). Which structure answers 'is this value in the other array?' in O(1)?",
           "Put one array into a hash set. Then scan the other array and keep the values found in the set.",
           "Repeats must disappear, so collect the matches in a set as well (or intersect two sets directly) and sort the final result."],
    editorial=["Convert both arrays to sets: this removes repeats immediately and gives O(1) membership tests. The set intersection <code>set(a) &amp; set(b)</code> contains exactly the values present in both arrays. Sorting that set produces the required output.",
               "Building the sets takes O(n + m) and sorting the result O(k log k) where k is the number of common values. If both inputs were already sorted, a two-pointer merge would find the common values without extra memory, but for unsorted input the hash set is the natural choice. Compare with the multiplicity-preserving variant, where a counter is needed instead of a set."],
    time="O(n + m + k log k)", space="O(n + m)",
    solution='''def intersectionUnique(a, b):
    return sorted(set(a) & set(b))
''',
    tests=[[[4, 9, 5, 9], [9, 4, 9, 8, 4]], [[1, 2, 2, 1], [2, 2]], [[], []], [[1, 2, 3], []], [[1, 2, 3], [4, 5, 6]],
           [[7], [7]], [[0, 0, 0], [0]], [[-5, -1, 3], [3, -1, -5]], [[1000000000, -1000000000], [-1000000000, 5]],
           [[5, 4, 3, 2, 1], [1, 3, 5, 7, 9]]],
)
_r = rnd(7201)
p["tests"].append([[_r.randint(0, 6000) for _ in range(3500)], [_r.randint(3000, 9000) for _ in range(3500)]])
p["tests"].append([[_r.randint(-10 ** 9, 10 ** 9) for _ in range(2500)] + [11, 22, 33], [11, 22, 33] + [_r.randint(-10 ** 9, 10 ** 9) for _ in range(2500)]])
_a = [_r.randint(-300, 300) for _ in range(4000)]
p["tests"].append([_a, _r.sample(_a, 3000)])


def b_inter_unique(a, b):
    out = []
    for x in sorted(a):
        if x in b and x not in out:
            out.append(x)
    return out


def v_inter_unique(tests):
    for t in tests:
        a, b = t["args"]
        assert len(a) <= 5000 and len(b) <= 5000
        assert t["expected"] == sorted(set(t["expected"]))
    assert any(t["expected"] == [] for t in tests)


CHECKS["intersection-of-two-arrays-unique"] = (b_inter_unique, lambda r: [gen_arr(r, -6, 6, 0, 9), gen_arr(r, -6, 6, 0, 9)], "exact")
VALIDATE["intersection-of-two-arrays-unique"] = v_inter_unique

p = add(
    id="difference-of-two-arrays", title="Difference of Two Arrays", diff="Easy", topic=TOPIC,
    fn="differenceOfArrays", params=[("a", "int[]"), ("b", "int[]")], ret="int[][]", cmp="exact",
    desc="<p>Given two integer arrays <code>a</code> and <code>b</code>, build two lists:</p><ul><li>the distinct values that occur in <code>a</code> but nowhere in <code>b</code>;</li><li>the distinct values that occur in <code>b</code> but nowhere in <code>a</code>.</li></ul><p>Return <code>[onlyA, onlyB]</code>, where each list is sorted in increasing order and contains no repeated value. A list may be empty.</p><p>For example, <code>a = [1, 2, 3, 3]</code> and <code>b = [2, 4, 6]</code> give <code>[[1, 3], [4, 6]]</code>.</p>",
    constraints=["0 &le; a.length, b.length &le; 5,000", "-10<sup>9</sup> &le; a[i], b[i] &le; 10<sup>9</sup>", "Both returned lists are sorted ascending without duplicates"],
    hints=["Think of each array as a set of values: you want the two one-sided set differences.",
           "Turn both arrays into hash sets. Then <code>A - B</code> and <code>B - A</code> are exactly the two answers (before sorting).",
           "Do not forget that the output lists must be sorted, and that duplicates inside one array must be reported only once, which a set takes care of."],
    editorial=["Build <code>sa = set(a)</code> and <code>sb = set(b)</code>. The values only in <code>a</code> are <code>sa - sb</code> and the values only in <code>b</code> are <code>sb - sa</code>. Sets already remove repeated values, and sorting each result gives the required order.",
               "Building the sets costs O(n + m) and sorting the outputs O(n log n + m log m) in the worst case. If both arrays were already sorted you could instead merge them with two pointers and avoid hashing, but with unsorted input the set approach is simplest."],
    time="O(n log n)", space="O(n)",
    solution='''def differenceOfArrays(a, b):
    sa, sb = set(a), set(b)
    return [sorted(sa - sb), sorted(sb - sa)]
''',
    tests=[[[1, 2, 3, 3], [2, 4, 6]], [[1, 2, 3], [1, 2, 3]], [[], []], [[5, 5, 5], []], [[], [-1, -1, 0]],
           [[1, 1, 2, 2], [3, 3, 4, 4]], [[0, -5, 7, 7, -5], [7, 8, 8, -9]], [[1000000000], [-1000000000]],
           [[3, 1, 2], [2, 3, 1]], [[1, 2, 3, 4, 5], [4, 5, 6, 7, 8, 9]]],
)
_r = rnd(7202)
p["tests"].append([[_r.randint(0, 8000) for _ in range(2500)], [_r.randint(4000, 12000) for _ in range(2500)]])
p["tests"].append([[_r.randint(-10 ** 9, 10 ** 9) for _ in range(1200)], [_r.randint(-10 ** 9, 10 ** 9) for _ in range(1200)]])
_a = [_r.randint(-500, 500) for _ in range(2000)]
p["tests"].append([_a, _a[::-1][1:] + [2000]])


def b_difference(a, b):
    x = sorted({v for v in a if v not in b})
    y = sorted({v for v in b if v not in a})
    return [x, y]


def v_difference(tests):
    for t in tests:
        a, b = t["args"]
        assert len(a) <= 5000 and len(b) <= 5000
        for lst in t["expected"]:
            assert lst == sorted(set(lst))


CHECKS["difference-of-two-arrays"] = (b_difference, lambda r: [gen_arr(r, -6, 6, 0, 8), gen_arr(r, -6, 6, 0, 8)], "exact")
VALIDATE["difference-of-two-arrays"] = v_difference


# ---------------------------------------------------------------- MEDIUM

p = add(
    id="min-changes-for-consecutive-values", title="Make Values Consecutive", diff="Hard", topic=TOPIC, tier="common",
    fn="minChangesToConsecutive", params=[("nums", "int[]")], ret="int", cmp="exact",
    desc="<p>In one operation you may replace any single element of <code>nums</code> by any integer you like. Your goal is to make the array <em>continuous</em>: all elements distinct, and the difference between the largest and the smallest element equal to <code>nums.length - 1</code> (so the final values are exactly <code>x, x+1, ..., x+n-1</code> in some order, for some integer <code>x</code>).</p><p>Return the minimum number of operations needed.</p><p>For example, <code>[1, 2, 3, 5, 6]</code> gives <code>1</code> (replace 6 by 4), <code>[4, 2, 5, 3]</code> gives <code>0</code>, and <code>[1, 10, 100, 1000]</code> gives <code>3</code>.</p>",
    constraints=["1 &le; nums.length &le; 10,000", "-10<sup>9</sup> &le; nums[i] &le; 10<sup>9</sup>"],
    hints=["Decide which elements you will <em>not</em> touch. An untouched value is never useful twice, so repeats must be replaced anyway.",
           "If the final array is the block <code>x..x+n-1</code>, you keep one element for each distinct original value inside that block. Maximise the number of distinct original values that fit into some block of n consecutive integers.",
           "Sort the distinct values and slide a window: the window <code>[i, j]</code> is valid when <code>v[j] - v[i] &le; n - 1</code>. The answer is <code>n</code> minus the largest valid window size."],
    editorial=["Fix the final block of values <code>x..x+n-1</code>. Every original distinct value lying inside the block can stay (one copy of it), and every other element must be replaced, so the cost is <code>n</code> minus the number of distinct original values inside the block. Replacements can always fill the vacant slots, so nothing else is needed.",
               "We want the block that contains the most distinct original values. It can be assumed to start at one of the distinct values, so sort the distinct values <code>v</code> and use two pointers: for each right end j, move i forward while <code>v[j] - v[i] &gt; n - 1</code>. The best window size w gives the answer <code>n - w</code>. Sorting dominates: O(n log n) time and O(n) space for the set."],
    time="O(n log n)", space="O(n)",
    solution='''def minChangesToConsecutive(nums):
    n = len(nums)
    v = sorted(set(nums))
    best = 0
    i = 0
    for j in range(len(v)):
        while v[j] - v[i] > n - 1:
            i += 1
        best = max(best, j - i + 1)
    return n - best
''',
    tests=[[[1, 2, 3, 5, 6]], [[4, 2, 5, 3]], [[1, 10, 100, 1000]], [[7]], [[5, 5, 5, 5]], [[1, 1, 2, 2, 3, 3]],
           [[-3, -2, 0, 1, 2]], [[1000000000, -1000000000, 0]], [[8, 9, 10, 20, 21, 22, 23, 24]],
           [[1, 2, 3, 4, 5, 6, 7, 8, 100]], [[3, 3, 4, 6, 6, 9]]],
)
_r = rnd(7203)
_a = list(range(1000, 4000)); _r.shuffle(_a); _a[:300] = [_r.randint(-10 ** 9, 10 ** 9) for _ in range(300)]
p["tests"].append([_a])
p["tests"].append([[_r.randint(-10 ** 9, 10 ** 9) for _ in range(4000)]])
p["tests"].append([[_r.randint(0, 5000) for _ in range(5000)]])


def b_min_changes(nums):
    n = len(nums)
    s = set(nums)
    best = n
    for x in range(min(nums) - n, max(nums) + 1):
        keep = sum(1 for v in s if x <= v <= x + n - 1)
        best = min(best, n - keep)
    return best


def v_min_changes(tests):
    for t in tests:
        assert 1 <= len(t["args"][0]) <= 10000
        assert 0 <= t["expected"] < len(t["args"][0]) or len(t["args"][0]) == 1


CHECKS["min-changes-for-consecutive-values"] = (b_min_changes, lambda r: [gen_arr(r, -10, 10, 1, 9)], "exact")
VALIDATE["min-changes-for-consecutive-values"] = v_min_changes

p = add(
    id="missing-ranges-in-interval", title="Missing Ranges in an Interval", diff="Medium", topic=TOPIC,
    fn="findMissingRanges", params=[("nums", "int[]"), ("lo", "int"), ("hi", "int")], ret="int[][]", cmp="exact",
    desc="<p>You are given an integer array <code>nums</code> and an inclusive interval <code>[lo, hi]</code>. The array is unsorted, may contain repeated values, and may contain values outside the interval, which must simply be ignored.</p><p>Every integer in <code>lo..hi</code> that does not occur in <code>nums</code> is <em>missing</em>. Group the missing integers into maximal blocks of consecutive integers and return them as a list of <code>[start, end]</code> pairs (both inclusive), sorted by <code>start</code>. If nothing is missing, return an empty list.</p><p>For example, <code>nums = [5, 3, 50, 9, 3, 75]</code>, <code>lo = 3</code>, <code>hi = 60</code> gives <code>[[4, 4], [6, 8], [10, 49], [51, 60]]</code>.</p>",
    constraints=["0 &le; nums.length &le; 10,000", "-2<sup>31</sup> &le; nums[i], lo, hi &le; 2<sup>31</sup> - 1", "lo &le; hi (the interval can be huge, so do not loop over all of its integers)"],
    hints=["The interval can contain billions of integers, so you cannot test them one by one. Work with the values that are present instead.",
           "Keep only the values inside <code>[lo, hi]</code>, remove repeats, and sort them. Missing blocks can only sit between neighbouring present values.",
           "Track <code>prev</code>, starting at <code>lo - 1</code>. For each present value <code>x</code> in order (and finally for <code>hi + 1</code> as a sentinel), if <code>x - prev &gt; 1</code> then <code>[prev + 1, x - 1]</code> is a missing block; then set <code>prev = x</code>."],
    editorial=["After filtering to the interval and deduplicating (a set does both jobs), sort the surviving values. The integers between two consecutive present values, and between the interval ends and the first or last present value, are exactly the missing blocks.",
               "Starting with <code>prev = lo - 1</code> and ending with the sentinel <code>hi + 1</code> unifies the three kinds of gaps into one rule: whenever the next value is more than one above <code>prev</code>, emit <code>[prev + 1, next - 1]</code>. The cost is dominated by sorting, O(n log n), and the output has at most n + 1 blocks. Because the interval may span the full 32-bit range, the algorithm must never iterate over the interval itself."],
    time="O(n log n)", space="O(n)",
    solution='''def findMissingRanges(nums, lo, hi):
    present = sorted(set(x for x in nums if lo <= x <= hi))
    out = []
    prev = lo - 1
    for x in present + [hi + 1]:
        if x - prev > 1:
            out.append([prev + 1, x - 1])
        prev = x
    return out
''',
    tests=[[[5, 3, 50, 9, 3, 75], 3, 60], [[], 1, 10], [[1, 2, 3, 4], 1, 4], [[5], 5, 5], [[5], 6, 6],
           [[0, 1, 3, 50, 75], 0, 99], [[-5, -3, 0, 2, 2, 4], -6, 5], [[10, 20, 30], 12, 28],
           [[INT_MIN, INT_MAX], INT_MIN, INT_MAX], [[7, 7, 7], 1, 7], [[-1, 100, 3], 0, 10],
           [[INT_MAX], INT_MAX - 3, INT_MAX], [[2, 4, 6, 8, 10], 1, 11]],
)
_r = rnd(7204)
_a = _r.sample(range(-10 ** 9, 10 ** 9), 2000)
p["tests"].append([_a, -5 * 10 ** 8, 6 * 10 ** 8])
p["tests"].append([[_r.randint(0, 9000) for _ in range(3000)], 100, 8900])
_a = list(range(0, 4000, 2)); _r.shuffle(_a)
p["tests"].append([_a, -3, 4003])


def b_missing_ranges(nums, lo, hi):
    out = []
    for v in range(lo, hi + 1):
        if v in nums:
            continue
        if out and out[-1][1] == v - 1:
            out[-1][1] = v
        else:
            out.append([v, v])
    return out


def g_missing_ranges(r):
    lo = r.randint(-8, 8)
    hi = lo + r.randint(0, 14)
    return [gen_arr(r, lo - 3, hi + 3, 0, 9), lo, hi]


def v_missing_ranges(tests):
    for t in tests:
        nums, lo, hi = t["args"]
        assert len(nums) <= 10000 and lo <= hi
        prev_end = lo - 1
        for s, e in t["expected"]:
            assert lo <= s <= e <= hi and s > prev_end + 1 - (1 if prev_end == lo - 1 else 0)
            assert s >= prev_end + 2 or prev_end == lo - 1
            prev_end = e


CHECKS["missing-ranges-in-interval"] = (b_missing_ranges, g_missing_ranges, "exact")
VALIDATE["missing-ranges-in-interval"] = v_missing_ranges

p = add(
    id="first-k-missing-positives", title="First K Missing Positives", diff="Medium", topic=TOPIC,
    fn="firstKMissingPositives", params=[("nums", "int[]"), ("k", "int")], ret="int[]", cmp="exact",
    desc="<p>Given an unsorted integer array <code>nums</code> (it may contain zero, negative numbers and repeats) and a positive integer <code>k</code>, return the <code>k</code> smallest positive integers that do <em>not</em> appear in <code>nums</code>, in increasing order.</p><p>For example, <code>nums = [3, -1, 4, 1]</code> and <code>k = 3</code> give <code>[2, 5, 6]</code>, because 1, 3 and 4 are present while 2, 5 and 6 are the first three absent positive integers.</p>",
    constraints=["0 &le; nums.length &le; 10,000", "-2<sup>31</sup> &le; nums[i] &le; 2<sup>31</sup> - 1", "1 &le; k &le; 10,000"],
    hints=["Positive integers are checked in order 1, 2, 3, ... Which data structure makes 'is v in nums?' a constant-time question?",
           "Put the values in a hash set, then count upward from 1 and collect each number that is not in the set.",
           "How far can the counter go? At most n numbers are blocked by the array, so the k-th missing positive is at most n + k, which means the loop is short enough to run directly."],
    editorial=["Insert all values into a set. Then iterate <code>c = 1, 2, 3, ...</code>; whenever <code>c</code> is not in the set, append it to the answer, and stop once k numbers are collected.",
               "The loop runs at most n + k times: among the integers 1..n+k at most n can be present in the array, so at least k are missing. The total cost is O(n + k) time and O(n) space. The classic follow-up places each value v in the range 1..n at index v - 1 by swapping (cyclic sort), which removes the set; the first indices where <code>nums[i] != i + 1</code> then reveal the missing numbers below n, and the rest are found by counting past n while skipping the displaced extra values."],
    time="O(n + k)", space="O(n)",
    solution='''def firstKMissingPositives(nums, k):
    present = set(nums)
    out = []
    c = 1
    while len(out) < k:
        if c not in present:
            out.append(c)
        c += 1
    return out
''',
    tests=[[[3, -1, 4, 1], 3], [[], 4], [[1, 2, 3], 2], [[2, 3, 4], 1], [[7, 8, 9], 3], [[1, 1, 1, 1], 5],
           [[-5, 0, 0, -1], 2], [[INT_MAX, INT_MIN, 2], 2], [[2, 2, 2, 2, 2, 2], 3],
           [[1, 2, 3, 4, 5, 6, 7, 8, 9, 10], 1], [[5, 3, 1], 4]],
)
_r = rnd(7205)
p["tests"].append([_r.sample(range(1, 6001), 4000), 3000])
p["tests"].append([[_r.randint(-10 ** 9, 10 ** 9) for _ in range(2500)], 5000])
_a = list(range(1, 3001)) + [_r.randint(4000, 10 ** 9) for _ in range(300)]; _r.shuffle(_a)
p["tests"].append([_a, 3000])


def b_first_k_missing(nums, k):
    out = []
    c = 0
    while len(out) < k:
        c += 1
        if nums.count(c) == 0:
            out.append(c)
    return out


def v_first_k_missing(tests):
    for t in tests:
        nums, k = t["args"]
        assert len(nums) <= 10000 and 1 <= k <= 10000
        assert len(t["expected"]) == k


CHECKS["first-k-missing-positives"] = (b_first_k_missing, lambda r: [gen_arr(r, -3, 10, 0, 10), r.randint(1, 6)], "exact")
VALIDATE["first-k-missing-positives"] = v_first_k_missing

p = add(
    id="max-mex-after-adding-multiples", title="Maximum MEX After Shifting by a Step", diff="Medium", topic=TOPIC, tier="extra",
    fn="maxMex", params=[("nums", "int[]"), ("step", "int")], ret="int", cmp="exact",
    desc="<p>You are given an integer array <code>nums</code> and a positive integer <code>step</code>. In one operation you pick any element and either add <code>step</code> to it or subtract <code>step</code> from it. You may perform any number of operations, on any elements, and elements are allowed to become negative.</p><p>The <em>MEX</em> of an array is the smallest non-negative integer that does not occur in it. Return the largest MEX you can obtain.</p><p>For example, <code>nums = [1, -10, 7, 13, 6, 8]</code> and <code>step = 5</code> give <code>4</code>: the elements can become <code>0, 1, 2, 3</code> (for instance <code>-10 &rarr; 0</code>, <code>1 &rarr; 1</code>, <code>7 &rarr; 2</code>, <code>13 &rarr; 3</code>), but no element is congruent to 4 modulo 5, so 4 can never appear.</p>",
    constraints=["1 &le; nums.length &le; 10,000", "1 &le; step &le; 10<sup>9</sup>", "-10<sup>9</sup> &le; nums[i] &le; 10<sup>9</sup>"],
    hints=["Adding or subtracting <code>step</code> never changes <code>x mod step</code>. So an element can become the target value <code>t</code> exactly when <code>x mod step == t mod step</code>.",
           "Count how many elements fall into each remainder class modulo <code>step</code> (use a non-negative remainder for negative numbers).",
           "To reach MEX m you need distinct elements for the targets 0, 1, ..., m-1. Go through the targets in order, spend one element from class <code>t mod step</code> for each, and stop at the first target whose class is empty."],
    editorial=["Because every move preserves the remainder modulo <code>step</code>, each element belongs forever to one class, and any non-negative target in its class is reachable. A target <code>t</code> is therefore coverable by any one element of class <code>t mod step</code>, and different targets need different elements.",
               "Greedily process targets 0, 1, 2, ... : decrement the count of class <code>t mod step</code> and continue while it was positive. The first target that finds an empty class is the MEX. Every success consumes one element, so the loop runs at most n + 1 times, giving O(n + step) time (or O(n) with a dictionary of counts) and one counter per class."],
    time="O(n)", space="O(n)",
    solution='''def maxMex(nums, step):
    cnt = {}
    for x in nums:
        r = x % step
        cnt[r] = cnt.get(r, 0) + 1
    mex = 0
    while cnt.get(mex % step, 0) > 0:
        cnt[mex % step] -= 1
        mex += 1
    return mex
''',
    tests=[[[1, -10, 7, 13, 6, 8], 5], [[1, -10, 7, 13, 6, 8], 7], [[0], 1], [[5], 3], [[0, 0, 0], 2],
           [[0, 1, 2, 3], 1000000000], [[-1, -2, -3], 3], [[2, 4, 6, 8], 2], [[3, 3, 3, 3, 3], 3],
           [[10 ** 9, -10 ** 9, 1, 2], 10 ** 9], [[7, 14, 21, 28, 35, 42], 7], [[1, 2, 3, 4, 5, 6], 4]],
)
_r = rnd(7206)
p["tests"].append([[_r.randint(-10 ** 9, 10 ** 9) for _ in range(5000)], 997])
p["tests"].append([[_r.randint(-10 ** 6, 10 ** 6) for _ in range(6000)], 1000])
p["tests"].append([[_r.randint(0, 5000) for _ in range(6000)], 6000])


def b_max_mex(nums, step):
    n = len(nums)
    rem = [x % step for x in nums]

    def can(m):
        used = [False] * n

        def go(t):
            if t == m:
                return True
            for i in range(n):
                if not used[i] and rem[i] == t % step:
                    used[i] = True
                    if go(t + 1):
                        return True
                    used[i] = False
            return False
        return go(0)

    m = 0
    while m < n and can(m + 1):
        m += 1
    return m


def g_max_mex(r):
    return [gen_arr(r, -12, 12, 1, 7), r.randint(1, 5)]


def v_max_mex(tests):
    for t in tests:
        assert 1 <= len(t["args"][0]) <= 10000 and 1 <= t["args"][1] <= 10 ** 9


CHECKS["max-mex-after-adding-multiples"] = (b_max_mex, g_max_mex, "exact")
VALIDATE["max-mex-after-adding-multiples"] = v_max_mex

p = add(
    id="values-in-at-least-m-arrays", title="Values Shared by At Least M Arrays", diff="Medium", topic=TOPIC, tier="extra",
    fn="valuesInAtLeastM", params=[("arrays", "int[][]"), ("m", "int")], ret="int[]", cmp="exact",
    desc="<p>You are given <code>k</code> integer arrays collected in <code>arrays</code> (a list of <code>k</code> lists, any of which may be empty or contain repeats) and an integer <code>m</code>.</p><p>Return, in increasing order and without repeats, every value that occurs in <strong>at least <code>m</code> different arrays</strong>. A value that appears several times inside one array still counts only once for that array.</p><p>For example, <code>arrays = [[1, 3, 3], [3, 4], [1, 3, 5]]</code> and <code>m = 2</code> give <code>[1, 3]</code>: the value 1 is in two arrays and 3 is in all three, while 4 and 5 are each in only one. With <code>m = k</code> this is the intersection of all arrays; with <code>m = 1</code> it is their union.</p>",
    constraints=["1 &le; k = arrays.length &le; 100", "1 &le; m &le; k", "0 &le; arrays[i].length and the total number of elements is at most 8,000", "-10<sup>9</sup> &le; arrays[i][j] &le; 10<sup>9</sup>"],
    hints=["For one value, what do you need to know to decide whether it belongs in the answer? How many arrays contain it.",
           "Make each array a set so that repeats inside the array disappear, then count how often each value shows up across all those sets.",
           "A <code>Counter</code> (hash map) updated with every set gives the number of arrays per value. Keep the values whose count is at least <code>m</code> and sort them."],
    editorial=["Replace each array by <code>set(array)</code>, so a value contributes at most once per array, and feed the sets into a frequency map. After all k sets are processed, <code>count[v]</code> is exactly the number of arrays containing <code>v</code>. The answer is the sorted list of keys with count &ge; m.",
               "This generalises both union (m = 1) and intersection (m = k) and covers the 'in at least two of three arrays' style of question. With N the total number of elements, the time is O(N + D log D) where D is the number of distinct values (the log factor comes from the final sort) and the space is O(D)."],
    time="O(N log N)", space="O(N)",
    solution='''def valuesInAtLeastM(arrays, m):
    count = {}
    for arr in arrays:
        for v in set(arr):
            count[v] = count.get(v, 0) + 1
    return sorted(v for v, c in count.items() if c >= m)
''',
    tests=[[[[1, 3, 3], [3, 4], [1, 3, 5]], 2], [[[1, 3, 3], [3, 4], [1, 3, 5]], 3], [[[1, 3, 3], [3, 4], [1, 3, 5]], 1],
           [[[5, 5, 5]], 1], [[[]], 1], [[[], [1, 2]], 1], [[[], [1, 2]], 2], [[[1, 2], [2, 3], [3, 1]], 2],
           [[[7, 7], [7], [7, 7, 7]], 3], [[[-1, 0], [0, 1], [], [0]], 3], [[[1000000000], [-1000000000], [1000000000]], 2],
           [[[4, 2, 9], [9, 4], [2, 9, 4, 4], [9]], 4]],
)
_r = rnd(7207)
p["tests"].append([[[_r.randint(0, 600) for _ in range(300)] for _ in range(20)], 7])
p["tests"].append([[[_r.randint(-10 ** 9, 10 ** 9) for _ in range(80)] + [5, -5, 123456789] for _ in range(60)], 60])
_arrs = [[_r.randint(0, 2000) for _ in range(_r.randint(0, 120))] for _ in range(60)]
p["tests"].append([_arrs, 12])


def b_values_m(arrays, m):
    allv = set()
    for a in arrays:
        allv.update(a)
    out = []
    for v in sorted(allv):
        if sum(1 for a in arrays if v in a) >= m:
            out.append(v)
    return out


def g_values_m(r):
    k = r.randint(1, 5)
    return [[gen_arr(r, -4, 4, 0, 6) for _ in range(k)], r.randint(1, k)]


def v_values_m(tests):
    for t in tests:
        arrays, m = t["args"]
        assert 1 <= len(arrays) <= 100 and 1 <= m <= len(arrays)
        assert sum(len(a) for a in arrays) <= 8000


CHECKS["values-in-at-least-m-arrays"] = (b_values_m, g_values_m, "exact")
VALIDATE["values-in-at-least-m-arrays"] = v_values_m

p = add(
    id="longest-run-with-k-insertions", title="Longest Run After K Insertions", diff="Medium", topic=TOPIC, tier="extra",
    fn="longestRunWithInsertions", params=[("nums", "int[]"), ("k", "int")], ret="int", cmp="exact",
    desc="<p>You have the integers of the array <code>nums</code> and may add up to <code>k</code> brand-new integers of your choice to the collection (a new integer may be any value, negative or very large, but adding a value that already exists gains nothing). Afterwards, look for the longest list of consecutive integers <code>x, x+1, ..., x+L-1</code> all of which are present in the collection. Return the largest <code>L</code> you can achieve.</p><p>For example, <code>nums = [1, 2, 4, 7]</code> and <code>k = 2</code> give <code>5</code>: add 3 and 5 to obtain the run <code>1, 2, 3, 4, 5</code>. With <code>k = 0</code> the question becomes the plain longest consecutive run; with an empty array the answer is simply <code>k</code>.</p>",
    constraints=["0 &le; nums.length &le; 10,000", "0 &le; k &le; 10,000", "-10<sup>9</sup> &le; nums[i] &le; 10<sup>9</sup>"],
    hints=["Repeats are irrelevant: work with the sorted list of distinct values <code>v</code>.",
           "If you choose to cover the stretch from <code>v[i]</code> to <code>v[j]</code>, the number of gaps you must fill is <code>(v[j] - v[i] + 1) - (j - i + 1)</code>. That must be at most <code>k</code>.",
           "Slide a window <code>[i, j]</code> over the distinct sorted values: shrink from the left while the needed fills exceed k. Any insertions you do not need can extend the run beyond the window, so the answer is the largest window size plus k."],
    editorial=["Let <code>v</code> be the sorted distinct values. A final run covers some stretch of integers; the original values inside it form a contiguous block <code>v[i..j]</code> of the sorted list, and every integer between <code>v[i]</code> and <code>v[j]</code> that is not in the array costs one insertion: exactly <code>v[j] - v[i] + 1 - (j - i + 1)</code> of them.",
               "Windows that fit within the budget k can be found with two pointers, because the cost never decreases when the window grows. For the best window of size w, the remaining budget can always be spent on integers just outside the window, extending the run, so the length is w + k. If the array is empty the answer is k. Time is O(n log n) for the sort and O(n) for the scan."],
    time="O(n log n)", space="O(n)",
    solution='''def longestRunWithInsertions(nums, k):
    v = sorted(set(nums))
    if not v:
        return k
    best = 0
    i = 0
    for j in range(len(v)):
        while v[j] - v[i] + 1 - (j - i + 1) > k:
            i += 1
        best = max(best, j - i + 1)
    return best + k
''',
    tests=[[[1, 2, 4, 7], 2], [[1, 2, 4, 7], 0], [[], 5], [[], 0], [[5], 3], [[1, 1, 1], 2], [[10, 20, 30], 1],
           [[10, 12, 14, 16], 3], [[-5, -3, 0, 1], 2], [[1, 100, 200, 300], 10000], [[1000000000, -1000000000], 4],
           [[3, 4, 5, 6], 0]],
)
_r = rnd(7208)
p["tests"].append([[_r.randint(-10 ** 9, 10 ** 9) for _ in range(4000)], 3000])
p["tests"].append([[_r.randint(0, 20000) for _ in range(6000)], 1500])
p["tests"].append([[_r.randint(0, 9000) for _ in range(4000)], 0])


def b_run_k(nums, k):
    if not nums:
        return k
    s = set(nums)
    best = 0
    for st in range(min(s) - k - 1, max(s) + 2):
        L = 0
        miss = 0
        x = st
        while True:
            if x not in s:
                if miss == k:
                    break
                miss += 1
            L += 1
            x += 1
            if x > max(s) + k + 2:
                break
        best = max(best, L)
    return best


def v_run_k(tests):
    for t in tests:
        assert len(t["args"][0]) <= 10000 and 0 <= t["args"][1] <= 10000


CHECKS["longest-run-with-k-insertions"] = (b_run_k, lambda r: [gen_arr(r, -8, 8, 0, 8), r.randint(0, 4)], "exact")
VALIDATE["longest-run-with-k-insertions"] = v_run_k


# ---------------------------------------------------------------- HARD

p = add(
    id="longest-run-after-each-insertion", title="Longest Run After Each Insertion", diff="Medium", topic=TOPIC, tier="extra",
    fn="longestRunAfterEach", params=[("nums", "int[]")], ret="int[]", cmp="exact",
    desc="<p>An initially empty collection of integers receives the values of <code>nums</code> one at a time, from left to right. Inserting a value that is already in the collection changes nothing.</p><p>After each insertion, look at the collection as a set and find the longest run of consecutive integers <code>x, x+1, ..., x+L-1</code> all contained in it. Return an array <code>res</code> of the same length as <code>nums</code> where <code>res[i]</code> is that longest length after inserting <code>nums[i]</code>.</p><p>For example, <code>nums = [5, 2, 4, 3, 3, 9]</code> gives <code>[1, 1, 1, 4, 4, 4]</code>: after 5 and 2 the best run has length 1, inserting 4 makes the run 4, 5 (length 2), and inserting 3 joins everything into 2, 3, 4, 5 (length 4).</p><p>Recomputing the answer from scratch after each insertion is too slow; aim for O(n) overall.</p>",
    constraints=["1 &le; nums.length &le; 8,000", "-10<sup>9</sup> &le; nums[i] &le; 10<sup>9</sup>"],
    hints=["Re-running the longest-consecutive-sequence scan after every insertion costs O(n<sup>2</sup>). The answer should be updated incrementally instead.",
           "A new value <code>x</code> can only merge the run ending at <code>x - 1</code> with the run starting at <code>x + 1</code>. The new run has length <code>left + 1 + right</code>.",
           "Store the run length in a map only at the two ends of each run. When inserting a new <code>x</code>, read <code>left = len[x-1]</code> and <code>right = len[x+1]</code>, then write the combined length at <code>x - left</code> and <code>x + right</code> (and at <code>x</code> itself to mark it as seen). Keep a running maximum."],
    editorial=["The key observation: when <code>x</code> is new, its neighbour <code>x - 1</code> (if present) is automatically the <em>right end</em> of its run, because <code>x</code> was not there to extend it. Likewise <code>x + 1</code> is the <em>left end</em> of its run. Maintaining a hash map from run endpoints to run length therefore gives both neighbouring lengths in O(1).",
               "On a new value, compute <code>total = left + right + 1</code>, store it at the new left end <code>x - left</code> and the new right end <code>x + right</code>, and mark <code>x</code> as present (its stored value may become stale if it is an interior point, but interior entries are never read as neighbours of a new value). Update the global maximum and append it to the output. Repeated values are skipped by a membership test. Total time O(n) and space O(n). A union-find over values achieves the same bound."],
    time="O(n)", space="O(n)",
    solution='''def longestRunAfterEach(nums):
    length = {}
    best = 0
    out = []
    for x in nums:
        if x not in length:
            left = length.get(x - 1, 0)
            right = length.get(x + 1, 0)
            total = left + right + 1
            length[x] = total
            length[x - left] = total
            length[x + right] = total
            if total > best:
                best = total
        out.append(best)
    return out
''',
    tests=[[[5, 2, 4, 3, 3, 9]], [[1]], [[1, 1, 1]], [[1, 2, 3, 4, 5]], [[5, 4, 3, 2, 1]], [[1, 3, 5, 7, 2, 4, 6]],
           [[10, 20, 30, 15, 25, 12, 14, 13]], [[-2, 2, -1, 1, 0]], [[1000000000, 999999999, -1000000000, -999999999]],
           [[4, 8, 6, 5, 7, 4, 6]], [[100, 102, 101, 99, 103, 98]]],
)
_r = rnd(7209)
_a = list(range(0, 4000)); _r.shuffle(_a)
p["tests"].append([_a])
p["tests"].append([[_r.randint(-10 ** 9, 10 ** 9) for _ in range(3000)]])
_a = [_r.randint(0, 3000) for _ in range(4000)]
p["tests"].append([_a])


def b_run_each(nums):
    seen = set()
    out = []
    for x in nums:
        seen.add(x)
        best = 0
        for y in seen:
            if y - 1 in seen:
                continue
            n = 1
            while y + n in seen:
                n += 1
            best = max(best, n)
        out.append(best)
    return out


def v_run_each(tests):
    for t in tests:
        nums = t["args"][0]
        assert 1 <= len(nums) <= 8000
        assert len(t["expected"]) == len(nums)
        assert all(a <= b for a, b in zip(t["expected"], t["expected"][1:]))


CHECKS["longest-run-after-each-insertion"] = (b_run_each, lambda r: [gen_arr(r, -6, 6, 1, 12)], "exact")
VALIDATE["longest-run-after-each-insertion"] = v_run_each

p = add(
    id="mex-after-each-update", title="MEX After Each Update", diff="Hard", topic=TOPIC, tier="extra",
    fn="mexAfterUpdates", params=[("nums", "int[]"), ("updates", "int[][]")], ret="int[]", cmp="exact",
    desc="<p>The <em>MEX</em> of a collection of non-negative integers is the smallest non-negative integer that does not occur in it (so the MEX of <code>[0, 1, 3]</code> is <code>2</code> and of <code>[1, 2]</code> is <code>0</code>).</p><p>You are given an array <code>nums</code> of non-negative integers and a list of <code>updates</code>, each a pair <code>[i, v]</code> meaning \"set <code>nums[i] = v</code>\". Apply the updates in order. Return an array with one entry per update: the MEX of the whole array right after that update.</p><p>For example, <code>nums = [0, 1, 2]</code> and <code>updates = [[1, 5], [0, 1], [2, 0]]</code> give <code>[1, 0, 2]</code>: the arrays become <code>[0, 5, 2]</code> (MEX 1), <code>[1, 5, 2]</code> (MEX 0), <code>[1, 5, 0]</code> (MEX 2).</p>",
    constraints=["1 &le; nums.length &le; 5,000", "1 &le; updates.length &le; 5,000", "0 &le; nums[i], v &le; 10<sup>9</sup>", "0 &le; i &lt; nums.length for every update"],
    hints=["The MEX of an array of length n is never larger than n, so values above n never matter.",
           "Keep a count for each value in <code>0..n</code>. An update changes only two counts: the old value's goes down and the new value's goes up.",
           "You need the smallest value whose count is zero, after every update. A min-heap of zero-count candidates with lazy deletion works: push a value when its count drops to zero, and when asking for the MEX pop the top while its count has become positive again."],
    editorial=["An array of n numbers can contain at most n distinct values, so among 0..n at least one value is absent and the MEX is at most n. Therefore track counts only for 0..n and ignore bigger values.",
               "Maintain a min-heap of values whose count may be zero. Initially push every value in 0..n with count zero. An update decrements the count of the replaced value (pushing it into the heap if it hits zero) and increments the count of the new value. To read the MEX, discard heap tops whose count is now positive; the first top that is still absent is the answer. Each value enters the heap once per time its count drops to zero, so there are O(n + q) pushes and pops of O(log n) each: O((n + q) log n) time, O(n + q) space. A segment tree over presence flags finding the first empty slot gives the same bound."],
    time="O((n + q) log n)", space="O(n + q)",
    solution='''import heapq

def mexAfterUpdates(nums, updates):
    nums = list(nums)
    n = len(nums)
    cnt = [0] * (n + 2)
    for x in nums:
        if x <= n:
            cnt[x] += 1
    heap = [v for v in range(n + 1) if cnt[v] == 0]
    heapq.heapify(heap)
    out = []
    for i, v in updates:
        old = nums[i]
        if old <= n:
            cnt[old] -= 1
            if cnt[old] == 0:
                heapq.heappush(heap, old)
        nums[i] = v
        if v <= n:
            cnt[v] += 1
        while cnt[heap[0]] > 0:
            heapq.heappop(heap)
        out.append(heap[0])
    return out
''',
    tests=[[[0, 1, 2], [[1, 5], [0, 1], [2, 0]]], [[0], [[0, 0], [0, 1], [0, 0]]], [[5], [[0, 5]]],
           [[0, 0, 0], [[0, 1], [1, 2], [2, 3], [0, 0]]], [[3, 1, 2, 0], [[0, 4], [3, 3], [0, 0], [1, 1]]],
           [[1, 1, 1, 1], [[0, 0], [1, 2], [2, 3], [3, 4], [0, 1]]],
           [[0, 1, 2, 3, 4], [[4, 1000000000], [3, 3], [4, 4], [0, 0], [0, 7]]],
           [[2, 2], [[0, 0], [1, 1], [0, 2], [1, 0]]], [[10 ** 9, 0], [[1, 1], [0, 0], [1, 10 ** 9]]],
           [[0, 1, 2, 3], [[3, 0], [2, 0], [1, 0], [0, 1], [1, 3]]]],
)
_r = rnd(7210)
_n = 2500
_a = list(range(_n)); _r.shuffle(_a)
p["tests"].append([_a, [[_r.randrange(_n), _r.randint(0, _n + 3)] for _ in range(2500)]])
_a = [_r.randint(0, 10 ** 9) for _ in range(2500)]
p["tests"].append([_a, [[_r.randrange(2500), _r.randint(0, 20)] for _ in range(2500)]])
_a = [_r.randint(0, 50) for _ in range(2000)]
p["tests"].append([_a, [[_r.randrange(2000), _r.randint(0, 2200)] for _ in range(2500)]])


def b_mex_updates(nums, updates):
    nums = list(nums)
    out = []
    for i, v in updates:
        nums[i] = v
        s = set(nums)
        m = 0
        while m in s:
            m += 1
        out.append(m)
    return out


def g_mex_updates(r):
    n = r.randint(1, 7)
    nums = [r.randint(0, n + 1) for _ in range(n)]
    ups = [[r.randrange(n), r.randint(0, n + 2)] for _ in range(r.randint(1, 8))]
    return [nums, ups]


def v_mex_updates(tests):
    for t in tests:
        nums, ups = t["args"]
        assert 1 <= len(nums) <= 5000 and 1 <= len(ups) <= 5000
        assert all(x >= 0 for x in nums)
        assert all(0 <= i < len(nums) and v >= 0 for i, v in ups)
        assert len(t["expected"]) == len(ups)


CHECKS["mex-after-each-update"] = (b_mex_updates, g_mex_updates, "exact")
VALIDATE["mex-after-each-update"] = v_mex_updates

p = add(
    id="distinct-count-in-range-queries", title="Distinct Values in Range Queries", diff="Hard", topic=TOPIC, tier="extra",
    fn="distinctInRanges", params=[("nums", "int[]"), ("queries", "int[][]")], ret="int[]", cmp="exact",
    desc="<p>You are given an integer array <code>nums</code> and a list of <code>queries</code>. Each query is a pair <code>[l, r]</code> (0-indexed, both ends inclusive) asking: how many <em>different</em> values occur in the subarray <code>nums[l..r]</code>?</p><p>Return an array with the answer to each query, in the original order.</p><p>For example, <code>nums = [1, 2, 1, 3, 2]</code> and <code>queries = [[0, 4], [0, 2], [2, 3], [1, 1]]</code> give <code>[3, 2, 2, 1]</code>.</p><p>With thousands of queries, building a set for each subarray is too slow in the worst case (O(n) per query); look for something close to O((n + q) log n).</p>",
    constraints=["1 &le; nums.length &le; 5,000", "1 &le; queries.length &le; 5,000", "0 &le; l &le; r &lt; nums.length", "-10<sup>9</sup> &le; nums[i] &le; 10<sup>9</sup>"],
    hints=["A value counts for the query <code>[l, r]</code> once, no matter how many copies lie inside. Choose one 'representative' occurrence per value.",
           "Process the queries offline, sorted by right end <code>r</code>, while sweeping a pointer over the array. For a fixed sweep position, make the <em>last</em> occurrence of every value its representative.",
           "Keep a Fenwick tree (binary indexed tree) over positions with a 1 at each representative. When you reach position p with value x, remove the 1 at the previous occurrence of x (if any) and add a 1 at p. The answer to a query is the sum over positions <code>l..r</code>."],
    editorial=["Sort queries by right endpoint and sweep the array from left to right. After processing position r, mark exactly one position per value: its most recent occurrence at or before r. For a query <code>[l, r]</code>, a value occurs in the range exactly when its latest occurrence up to r is at index &ge; l, so the number of marked positions in <code>[l, r]</code> equals the number of distinct values.",
               "Marks change in O(1) positions per step: when moving to index p with value x, unmark the previous occurrence of x and mark p. A Fenwick tree supports these point updates and the prefix sums for range counting in O(log n). Total time is O((n + q) log n) plus sorting the queries, with O(n + q) space. The brute-force alternative of building a set for each query takes O(n) per query, up to O(nq) overall."],
    time="O((n + q) log n)", space="O(n + q)",
    solution='''def distinctInRanges(nums, queries):
    n = len(nums)
    tree = [0] * (n + 1)

    def update(i, d):
        i += 1
        while i <= n:
            tree[i] += d
            i += i & -i

    def prefix(i):
        # sum of positions 0..i (0 when i < 0)
        i += 1
        s = 0
        while i > 0:
            s += tree[i]
            i -= i & -i
        return s

    order = sorted(range(len(queries)), key=lambda q: queries[q][1])
    last = {}
    res = [0] * len(queries)
    p = 0
    for q in order:
        l, r = queries[q]
        while p <= r:
            x = nums[p]
            if x in last:
                update(last[x], -1)
            update(p, 1)
            last[x] = p
            p += 1
        res[q] = prefix(r) - prefix(l - 1)
    return res
''',
    tests=[[[1, 2, 1, 3, 2], [[0, 4], [0, 2], [2, 3], [1, 1]]], [[7], [[0, 0]]], [[5, 5, 5, 5], [[0, 3], [1, 2], [2, 2]]],
           [[1, 2, 3, 4, 5], [[0, 4], [1, 3], [2, 2], [0, 0]]], [[3, 1, 3, 1, 3], [[0, 4], [1, 3], [2, 4], [0, 1]]],
           [[-1, -1, 0, 0, -1], [[0, 4], [0, 1], [2, 3], [1, 4]]], [[10 ** 9, -10 ** 9, 10 ** 9], [[0, 2], [0, 1], [1, 2]]],
           [[4, 5, 4, 6, 5, 7, 4], [[0, 6], [2, 5], [3, 6], [1, 2], [4, 4], [0, 3]]],
           [[1, 1, 2, 2, 3, 3, 1], [[0, 6], [1, 4], [2, 3], [3, 6], [5, 6]]]],
)
_r = rnd(7211)
_a = [_r.randint(0, 800) for _ in range(3000)]
_qs = []
for _ in range(2000):
    _l = _r.randrange(3000); _rr = _r.randrange(_l, 3000)
    _qs.append([_l, _rr])
p["tests"].append([_a, _qs])
_a = [_r.randint(-10 ** 9, 10 ** 9) for _ in range(2000)]
_qs = []
for _ in range(1500):
    _l = _r.randrange(2000); _rr = _r.randrange(_l, 2000)
    _qs.append([_l, _rr])
p["tests"].append([_a, _qs])
_a = [_r.randint(0, 5) for _ in range(3000)]
_qs = [[_r.randrange(0, 50), _r.randrange(2950, 3000)] for _ in range(2500)]
p["tests"].append([_a, _qs])


def b_distinct_ranges(nums, queries):
    return [len(set(nums[l:r + 1])) for l, r in queries]


def g_distinct_ranges(r):
    n = r.randint(1, 10)
    nums = [r.randint(-3, 3) for _ in range(n)]
    qs = []
    for _ in range(r.randint(1, 8)):
        l = r.randrange(n)
        qs.append([l, r.randrange(l, n)])
    return [nums, qs]


def v_distinct_ranges(tests):
    for t in tests:
        nums, qs = t["args"]
        assert 1 <= len(nums) <= 5000 and 1 <= len(qs) <= 5000
        assert all(0 <= l <= r < len(nums) for l, r in qs)


CHECKS["distinct-count-in-range-queries"] = (b_distinct_ranges, g_distinct_ranges, "exact")
VALIDATE["distinct-count-in-range-queries"] = v_distinct_ranges
