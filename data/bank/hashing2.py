"""Problems: arrays & hashing (second batch). See data/lib.py for the registry."""
from collections import Counter

from lib import add, rnd, CHECKS, VALIDATE, gen_arr  # noqa: F401

INT_MIN, INT_MAX = -(2 ** 31), 2 ** 31 - 1


# ---------------------------------------------------------------- EASY

p = add(
    id="set-mismatch", title="Set Mismatch", diff="Easy", topic="Arrays & Hashing",
    fn="findMismatch", params=[("nums", "int[]")], ret="int[]", cmp="exact",
    desc="<p>A list originally held every integer from <code>1</code> to <code>n</code> exactly once. Due to a data error, one of the numbers was overwritten by a copy of another number, so one value now appears twice and one value is missing entirely. The result is the array <code>nums</code> of length <code>n</code>.</p><p>Return a two-element array <code>[duplicate, missing]</code>.</p><p>For example, <code>[1, 2, 2, 4]</code> gives <code>[2, 3]</code>.</p>",
    constraints=["2 &le; nums.length &le; 10,000", "1 &le; nums[i] &le; nums.length", "Exactly one value appears twice, exactly one value is missing, and every other value appears once"],
    hints=["Counting how many times each value in <code>1..n</code> shows up tells you both answers directly.",
           "You do not need a full map: a boolean marker per value (or a set of seen values) is enough to spot the repeat.",
           "Once you know the duplicate <code>d</code>, the array sum equals <code>n(n+1)/2 + d - missing</code>, so the missing value follows from the sums."],
    editorial=["Scan the array with a set. The first value that is already in the set is the duplicate. Because the array holds the numbers 1..n with the missing one replaced by the duplicate, <code>sum(nums) = n(n+1)/2 - missing + duplicate</code>, which gives <code>missing = n(n+1)/2 - sum(nums) + duplicate</code>.",
               "A frequency array of size n+1 works just as well: the index with count 2 is the duplicate and the index with count 0 is the missing number. Both approaches are O(n) time. The sign-marking trick (negate <code>nums[abs(x) - 1]</code> on each visit) brings the extra space down to O(1)."],
    time="O(n)", space="O(n)",
    solution='''def findMismatch(nums):
    n = len(nums)
    seen = set()
    dup = 0
    for x in nums:
        if x in seen:
            dup = x
        seen.add(x)
    missing = n * (n + 1) // 2 - sum(nums) + dup
    return [dup, missing]
''',
    tests=[[[1, 2, 2, 4]], [[1, 1]], [[2, 2]], [[3, 2, 3, 4, 6, 5]], [[1, 5, 3, 2, 2, 7, 6, 4]],
           [[2, 3, 2]], [[1, 3, 3]], [[4, 2, 4, 1]], [[1, 2, 3, 4, 5, 6, 7, 8, 9, 9]],
           [[9, 1, 2, 3, 4, 5, 6, 7, 1]]],
)


def _mk_mismatch(r, n):
    a = list(range(1, n + 1))
    r.shuffle(a)
    i, j = r.sample(range(n), 2)
    a[i] = a[j]
    return a


_r = rnd(2101)
p["tests"].append([_mk_mismatch(_r, 10000)])
p["tests"].append([_mk_mismatch(_r, 9999)])
p["tests"].append([_mk_mismatch(_r, 500)])
_a = list(range(1, 10001)); _a[9999] = 1
p["tests"].append([_a])
_a = list(range(1, 10001)); _a[0] = 10000
p["tests"].append([_a])


def b_mismatch(nums):
    n = len(nums)
    dup = miss = None
    for v in range(1, n + 1):
        c = nums.count(v)
        if c == 2:
            dup = v
        elif c == 0:
            miss = v
    return [dup, miss]


def g_mismatch(r):
    return [_mk_mismatch(r, r.randint(2, 12))]


def v_mismatch(tests):
    for t in tests:
        nums = t["args"][0]
        n = len(nums)
        assert 2 <= n <= 10000
        c = Counter(nums)
        assert all(1 <= v <= n for v in c)
        assert sorted(c.values()).count(2) == 1 and len(c) == n - 1


CHECKS["set-mismatch"] = (b_mismatch, g_mismatch, "exact")
VALIDATE["set-mismatch"] = v_mismatch

p = add(
    id="intersect-arrays-with-multiplicity", title="Intersection of Two Arrays with Repeats", diff="Easy", topic="Arrays & Hashing",
    fn="intersectWithRepeats", params=[("a", "int[]"), ("b", "int[]")], ret="int[]", cmp="exact",
    desc="<p>Given two integer arrays <code>a</code> and <code>b</code>, return the elements they have in common, counting repeats: a value that appears <code>x</code> times in <code>a</code> and <code>y</code> times in <code>b</code> must appear <code>min(x, y)</code> times in the result.</p><p>Return the result sorted in ascending order. If nothing is shared, return an empty array.</p><p>For example, <code>a = [4, 9, 5, 9]</code> and <code>b = [9, 4, 9, 8, 4]</code> give <code>[4, 9, 9]</code>.</p>",
    constraints=["0 &le; a.length, b.length &le; 5,000", "-2<sup>31</sup> &le; a[i], b[i] &le; 2<sup>31</sup> - 1"],
    hints=["Plain sets lose the repeat counts. What structure remembers how many times each value occurred?",
           "Count the values of one array, then walk through the other array and consume from those counts.",
           "Whenever the current value of <code>b</code> still has a positive remaining count, output it and decrement the count. Sort the output at the end."],
    editorial=["Build a frequency map of <code>a</code>. Then scan <code>b</code>: if the map still holds a positive count for the current value, append the value to the result and decrement the count. Each shared copy is matched exactly once, so the number of copies kept per value is <code>min(count in a, count in b)</code>. Sort the result to produce the canonical order.",
               "Alternatively sort both arrays and walk them with two pointers, advancing the smaller side and emitting on equality. That needs no hash map and produces sorted output for free, at O(n log n) time."],
    time="O(n log n)", space="O(n)",
    solution='''def intersectWithRepeats(a, b):
    counts = {}
    for x in a:
        counts[x] = counts.get(x, 0) + 1
    out = []
    for x in b:
        if counts.get(x, 0) > 0:
            out.append(x)
            counts[x] -= 1
    out.sort()
    return out
''',
    tests=[[[4, 9, 5, 9], [9, 4, 9, 8, 4]], [[1, 2, 2, 1], [2, 2]], [[], []], [[1, 2, 3], []], [[], [5]],
           [[1, 2, 3], [4, 5, 6]], [[7, 7, 7], [7, 7]], [[0, 0, 0], [0]], [[-3, -3, 5, 5, 5], [5, -3, 5, 5, 5, -3, -3]],
           [[INT_MIN, INT_MAX, INT_MAX], [INT_MAX, INT_MAX, INT_MIN, INT_MIN]], [[3, 1, 2], [1, 2, 3]]],
)
_r = rnd(2102)
p["tests"].append([[_r.randint(-50, 50) for _ in range(5000)], [_r.randint(-50, 50) for _ in range(5000)]])
p["tests"].append([[_r.randint(-10 ** 9, 10 ** 9) for _ in range(5000)], [_r.randint(-10 ** 9, 10 ** 9) for _ in range(5000)]])
_pool = [_r.randint(-INT_MAX, INT_MAX) for _ in range(3000)]
p["tests"].append([[_r.choice(_pool) for _ in range(5000)], [_r.choice(_pool) for _ in range(4000)]])
p["tests"].append([[5] * 5000, [5] * 3000 + [6] * 2000])


def b_intersect(a, b):
    out = []
    for v in sorted(set(a)):
        out.extend([v] * min(a.count(v), b.count(v)))
    return out


def g_intersect(r):
    return [gen_arr(r, -4, 4, 0, 9), gen_arr(r, -4, 4, 0, 9)]


def v_intersect(tests):
    for t in tests:
        a, b = t["args"]
        assert len(a) <= 5000 and len(b) <= 5000
        assert t["expected"] == sorted(t["expected"])


CHECKS["intersect-arrays-with-multiplicity"] = (b_intersect, g_intersect, "exact")
VALIDATE["intersect-arrays-with-multiplicity"] = v_intersect

p = add(
    id="shortest-subarray-with-same-degree", title="Shortest Subarray with Same Degree", diff="Easy", topic="Arrays & Hashing",
    fn="shortestSameDegree", params=[("nums", "int[]")], ret="int", cmp="exact",
    desc="<p>The <em>degree</em> of an array is the highest number of times any single value occurs in it. For example, the degree of <code>[1, 3, 3, 2, 3, 1]</code> is 3, because the value 3 occurs three times.</p><p>Given a non-empty integer array <code>nums</code>, find the shortest contiguous subarray whose degree equals the degree of the whole array, and return its length.</p>",
    constraints=["1 &le; nums.length &le; 20,000", "-10<sup>9</sup> &le; nums[i] &le; 10<sup>9</sup>"],
    hints=["Compute the degree first. Which values reach that frequency?",
           "A shortest valid subarray can always be trimmed so that it starts and ends on an occurrence of a most frequent value.",
           "Record the first index, last index and count of every value in one pass. For each value whose count equals the degree, candidate length is <code>last - first + 1</code>; take the minimum."],
    editorial=["Any subarray with degree equal to the global degree <code>d</code> must contain some value <code>v</code> exactly <code>d</code> times, where <code>v</code> is one of the globally most frequent values. The shortest such window for a fixed <code>v</code> runs from its first occurrence to its last occurrence.",
               "So one pass recording <code>first[v]</code>, <code>last[v]</code> and <code>count[v]</code> is enough. The answer is the minimum of <code>last[v] - first[v] + 1</code> over all values with <code>count[v]</code> equal to the maximum count. The runtime is linear."],
    time="O(n)", space="O(n)",
    solution='''def shortestSameDegree(nums):
    first = {}
    last = {}
    cnt = {}
    for i, x in enumerate(nums):
        if x not in first:
            first[x] = i
        last[x] = i
        cnt[x] = cnt.get(x, 0) + 1
    deg = max(cnt.values())
    return min(last[x] - first[x] + 1 for x in cnt if cnt[x] == deg)
''',
    tests=[[[1, 2, 2, 3, 1]], [[1, 2, 2, 3, 1, 4, 2]], [[5]], [[7, 7]], [[1, 2, 3, 4]], [[1, 1, 2, 2, 3, 3]],
           [[3, 1, 2, 1, 3, 3, 2, 2]], [[-1, -1, 4, 4, -1, 4]], [[0, 0, 0, 0]], [[9, 8, 9, 7, 7, 8, 6]],
           [[1000000000, -1000000000, 1000000000]]],
)
_r = rnd(2103)
p["tests"].append([[_r.randint(-30, 30) for _ in range(20000)]])
p["tests"].append([[_r.randint(-10 ** 9, 10 ** 9) for _ in range(20000)]])
p["tests"].append([[1] + [_r.randint(2, 4000) for _ in range(9990)] + [1] + [_r.randint(2, 4000) for _ in range(9)]])
p["tests"].append([list(range(20000))])


def b_degree(nums):
    n = len(nums)

    def deg(arr):
        return max(arr.count(x) for x in set(arr))

    d = deg(nums)
    best = n
    for i in range(n):
        for j in range(i, n):
            if j - i + 1 < best and deg(nums[i:j + 1]) == d:
                best = j - i + 1
    return best


def v_degree(tests):
    for t in tests:
        assert 1 <= len(t["args"][0]) <= 20000


CHECKS["shortest-subarray-with-same-degree"] = (b_degree, lambda r: [gen_arr(r, 0, 4, 1, 12)], "exact")
VALIDATE["shortest-subarray-with-same-degree"] = v_degree


# ---------------------------------------------------------------- MEDIUM

p = add(
    id="longest-balanced-binary-subarray", title="Longest Balanced Binary Subarray", diff="Medium", topic="Arrays & Hashing",
    fn="longestBalanced", params=[("bits", "int[]")], ret="int", cmp="exact",
    desc="<p>You are given a binary array <code>bits</code> containing only <code>0</code> and <code>1</code>. A contiguous subarray is <em>balanced</em> if it contains the same number of zeros and ones.</p><p>Return the length of the longest balanced subarray, or <code>0</code> if there is none.</p><p>For example, <code>[0, 1, 1, 0, 1, 1, 1, 0]</code> gives <code>4</code>.</p>",
    constraints=["0 &le; bits.length &le; 20,000", "bits[i] is 0 or 1"],
    hints=["Checking every subarray works in O(n<sup>2</sup>). What running quantity decides whether a subarray is balanced?",
           "Treat each 0 as -1 and each 1 as +1. A balanced subarray is exactly one whose sum is 0.",
           "A subarray sums to 0 when two prefix sums are equal. Store the earliest index at which each prefix sum occurred, and measure the distance to later repeats."],
    editorial=["Map 0 to -1 and 1 to +1 and keep a running prefix sum <code>s</code>. The subarray between positions <code>i</code> (exclusive) and <code>j</code> (inclusive) is balanced exactly when <code>prefix[i] == prefix[j]</code>.",
               "Keep a hash map from each prefix value to the first index where it appeared, seeded with <code>{0: -1}</code> for the empty prefix. At each index <code>j</code>, if the current prefix was seen before at <code>i</code>, the length <code>j - i</code> is a candidate; otherwise record <code>j</code>. Never overwrite an earlier index, since the earliest one gives the longest subarray. One pass, O(n) time."],
    time="O(n)", space="O(n)",
    solution='''def longestBalanced(bits):
    first = {0: -1}
    s = 0
    best = 0
    for j, b in enumerate(bits):
        s += 1 if b == 1 else -1
        if s in first:
            best = max(best, j - first[s])
        else:
            first[s] = j
    return best
''',
    tests=[[[0, 1]], [[0, 1, 0]], [[0, 1, 1, 0, 1, 1, 1, 0]], [[]], [[0]], [[1, 1, 1]], [[0, 0, 0, 1]],
           [[1, 0, 1, 0, 1, 0]], [[1, 1, 0, 0, 1]], [[0, 0, 1, 0, 0, 0, 1, 1]], [[1, 0, 0, 0, 1, 1, 0, 0]]],
)
_r = rnd(2104)
p["tests"].append([[_r.randint(0, 1) for _ in range(20000)]])
p["tests"].append([[1] * 19999 + [0]])
p["tests"].append([[0] * 10000 + [1] * 10000])
p["tests"].append([[1] * 15000 + [_r.randint(0, 1) for _ in range(5000)]])
p["tests"].append([[(i // 3) % 2 for i in range(20000)]])


def b_balanced(bits):
    best = 0
    for i in range(len(bits)):
        ones = 0
        for j in range(i, len(bits)):
            ones += bits[j]
            if ones * 2 == j - i + 1:
                best = max(best, j - i + 1)
    return best


def v_balanced(tests):
    for t in tests:
        a = t["args"][0]
        assert len(a) <= 20000 and all(x in (0, 1) for x in a)


CHECKS["longest-balanced-binary-subarray"] = (b_balanced, lambda r: [gen_arr(r, 0, 1, 0, 14)], "exact")
VALIDATE["longest-balanced-binary-subarray"] = v_balanced

p = add(
    id="count-subarrays-sum-divisible-by-k", title="Count Subarrays with Sum Divisible by K", diff="Medium", topic="Arrays & Hashing",
    fn="countDivisibleSubarrays", params=[("nums", "int[]"), ("k", "int")], ret="int", cmp="exact",
    desc="<p>Given an integer array <code>nums</code> (values may be negative) and a positive integer <code>k</code>, count the non-empty contiguous subarrays whose sum is divisible by <code>k</code>.</p><p>Subarrays at different positions count separately even if they hold the same values. A sum of <code>0</code> is divisible by every <code>k</code>.</p><p>For example, <code>nums = [4, 5, 0, -2, -3, 1]</code> and <code>k = 5</code> give <code>7</code>.</p>",
    constraints=["1 &le; nums.length &le; 10,000", "-10,000 &le; nums[i] &le; 10,000", "1 &le; k &le; 10,000"],
    hints=["Write a subarray sum as the difference of two prefix sums. When is that difference divisible by <code>k</code>?",
           "Two prefix sums give a divisible difference exactly when they leave the same remainder modulo <code>k</code>.",
           "Count how many earlier prefixes (including the empty one) share each remainder. Normalise negative remainders into <code>0..k-1</code> before counting."],
    editorial=["Let <code>P[i]</code> be the sum of the first <code>i</code> elements, with <code>P[0] = 0</code>. The subarray covering elements <code>i..j-1</code> has sum <code>P[j] - P[i]</code>, which is divisible by <code>k</code> iff <code>P[j] % k == P[i] % k</code>.",
               "Walk through the array keeping a counter of remainders of the prefixes seen so far, starting with remainder 0 counted once for the empty prefix. For each new prefix remainder <code>m</code>, add the current count of <code>m</code> to the answer, then increment it. In languages where <code>%</code> can return a negative value, use <code>((x % k) + k) % k</code>. With n prefixes that is O(n) time."],
    time="O(n + k)", space="O(k)",
    solution='''def countDivisibleSubarrays(nums, k):
    seen = {0: 1}
    s = 0
    total = 0
    for x in nums:
        s += x
        m = s % k
        total += seen.get(m, 0)
        seen[m] = seen.get(m, 0) + 1
    return total
''',
    tests=[[[4, 5, 0, -2, -3, 1], 5], [[5], 9], [[5], 5], [[0], 3], [[1, 2, 3], 1], [[-1, 2, 9], 2],
           [[-5, -5, 5], 10], [[3, -3, 3, -3], 3], [[7, 4, 3, 2], 6], [[-1, -2, -3, -4], 7],
           [[10000, -10000, 10000], 10000]],
)
_r = rnd(2105)
p["tests"].append([[0] * 10000, 7])
p["tests"].append([[_r.randint(-10000, 10000) for _ in range(10000)], 1])
p["tests"].append([[_r.randint(-10000, 10000) for _ in range(10000)], 97])
p["tests"].append([[_r.randint(-10000, 10000) for _ in range(10000)], 10000])
p["tests"].append([[10000] * 10000, 9999])
p["tests"].append([[(-1) ** i * _r.randint(0, 3) for i in range(10000)], 2])


def b_divisible(nums, k):
    n = len(nums)
    c = 0
    for i in range(n):
        s = 0
        for j in range(i, n):
            s += nums[j]
            if s % k == 0:
                c += 1
    return c


def v_divisible(tests):
    for t in tests:
        nums, k = t["args"]
        assert 1 <= len(nums) <= 10000 and 1 <= k <= 10000
        assert all(-10000 <= x <= 10000 for x in nums)


CHECKS["count-subarrays-sum-divisible-by-k"] = (b_divisible, lambda r: [gen_arr(r, -9, 9, 1, 12), r.randint(1, 7)], "exact")
VALIDATE["count-subarrays-sum-divisible-by-k"] = v_divisible

p = add(
    id="longest-subarray-with-sum-exactly-k", title="Longest Subarray with Sum K", diff="Medium", topic="Arrays & Hashing",
    fn="longestSubarraySumK", params=[("nums", "int[]"), ("k", "int")], ret="int", cmp="exact",
    desc="<p>Given an integer array <code>nums</code> that may contain negative numbers, zeros and positives, and an integer <code>k</code>, return the length of the longest contiguous subarray whose elements add up to exactly <code>k</code>.</p><p>If no subarray has that sum, return <code>0</code>.</p><p>For example, <code>nums = [1, -1, 5, -2, 3]</code> and <code>k = 3</code> give <code>4</code>, from the subarray <code>[1, -1, 5, -2]</code>.</p>",
    constraints=["1 &le; nums.length &le; 20,000", "-10,000 &le; nums[i] &le; 10,000", "-10<sup>9</sup> &le; k &le; 10<sup>9</sup>"],
    hints=["A sliding window needs non-negative numbers to know when to shrink. With mixed signs it fails, so think about prefix sums.",
           "A subarray sums to <code>k</code> when <code>prefix[j] - prefix[i] = k</code>. For the current prefix, which earlier prefix value are you looking for?",
           "Store, for each prefix sum, only its <em>first</em> index. At each position look up <code>prefix - k</code> and measure the distance."],
    editorial=["Let <code>prefix</code> be the running sum after the current element. A subarray that ends here and sums to <code>k</code> must start right after a position whose prefix sum was <code>prefix - k</code>. To make the subarray as long as possible we want the <em>earliest</em> such position.",
               "Keep a map from prefix sum to the first index at which it occurred, seeded with <code>{0: -1}</code>. For each index <code>j</code>, if <code>prefix - k</code> is in the map at index <code>i</code>, the candidate length is <code>j - i</code>. Insert the current prefix only if it is not already present, so earlier indices are never overwritten. This runs in O(n) time; a two-pointer window is not valid because negative values break monotonicity."],
    time="O(n)", space="O(n)",
    solution='''def longestSubarraySumK(nums, k):
    first = {0: -1}
    s = 0
    best = 0
    for j, x in enumerate(nums):
        s += x
        if s - k in first:
            best = max(best, j - first[s - k])
        if s not in first:
            first[s] = j
    return best
''',
    tests=[[[1, -1, 5, -2, 3], 3], [[-2, -1, 2, 1], 1], [[5], 5], [[5], 6], [[0, 0, 0], 0], [[1, 2, 3], 7],
           [[2, 0, 0, 3], 3], [[-3, 3, 0, 4, -4], 0], [[1, 1, 1, 1], 2], [[-5, -5, -5], -10],
           [[10000, -10000, 10000], 10000], [[3, 4, 7, 2, -3, 1, 4, 2], 7]],
)
_r = rnd(2106)
p["tests"].append([[_r.randint(-10000, 10000) for _ in range(20000)], 0])
p["tests"].append([[_r.randint(-10000, 10000) for _ in range(20000)], 123456])
p["tests"].append([[_r.randint(-3, 3) for _ in range(20000)], 5])
p["tests"].append([[0] * 20000, 0])
p["tests"].append([[10000] * 20000, 10 ** 9])
p["tests"].append([[1, -1] * 10000, 0])


def b_longest_k(nums, k):
    best = 0
    for i in range(len(nums)):
        s = 0
        for j in range(i, len(nums)):
            s += nums[j]
            if s == k:
                best = max(best, j - i + 1)
    return best


def v_longest_k(tests):
    for t in tests:
        nums, k = t["args"]
        assert 1 <= len(nums) <= 20000 and -10 ** 9 <= k <= 10 ** 9
        assert all(-10000 <= x <= 10000 for x in nums)


CHECKS["longest-subarray-with-sum-exactly-k"] = (b_longest_k, lambda r: [gen_arr(r, -5, 5, 1, 12), r.randint(-8, 8)], "exact")
VALIDATE["longest-subarray-with-sum-exactly-k"] = v_longest_k

p = add(
    id="four-array-sum-zero-count", title="Four Array Sum Zero Count", diff="Medium", topic="Arrays & Hashing",
    fn="countFourSumZero", params=[("a", "int[]"), ("b", "int[]"), ("c", "int[]"), ("d", "int[]")], ret="int", cmp="exact",
    desc="<p>You are given four integer arrays <code>a</code>, <code>b</code>, <code>c</code> and <code>d</code>, all of the same length <code>n</code>. Count the index tuples <code>(i, j, k, l)</code>, each index in <code>0..n-1</code>, such that</p><p><code>a[i] + b[j] + c[k] + d[l] == 0</code>.</p><p>Tuples that differ in any index are counted separately, even if the values are equal.</p><p>For example, <code>a = [1, 2]</code>, <code>b = [-2, -1]</code>, <code>c = [-1, 2]</code>, <code>d = [0, 2]</code> give <code>2</code>.</p>",
    constraints=["1 &le; n &le; 200 (all four arrays have length n)", "-2<sup>28</sup> &le; a[i], b[i], c[i], d[i] &le; 2<sup>28</sup>"],
    hints=["Four nested loops cost O(n<sup>4</sup>). That is far too slow for n = 200.",
           "Split the four arrays into two pairs. Every sum <code>a[i] + b[j]</code> must be cancelled by some <code>c[k] + d[l]</code>.",
           "Count all pair sums of <code>a</code> and <code>b</code> in a hash map. Then, for each pair sum of <code>c</code> and <code>d</code>, add the count stored for its negation."],
    editorial=["Meet in the middle. Enumerate all <code>n<sup>2</sup></code> sums <code>a[i] + b[j]</code> and store how many times each sum occurs in a hash map. Then enumerate all <code>n<sup>2</sup></code> sums <code>c[k] + d[l]</code>; each one pairs with exactly <code>map[-(c[k] + d[l])]</code> tuples from the first half.",
               "This takes O(n<sup>2</sup>) time and space instead of O(n<sup>4</sup>). Because the answer counts tuples, not distinct value combinations, the map must store multiplicities rather than just presence. For n = 200 the answer is at most 200<sup>4</sup> = 1.6 billion, which still fits in a 32-bit signed integer."],
    time="O(n^2)", space="O(n^2)",
    solution='''def countFourSumZero(a, b, c, d):
    pair = {}
    for x in a:
        for y in b:
            s = x + y
            pair[s] = pair.get(s, 0) + 1
    total = 0
    for x in c:
        for y in d:
            total += pair.get(-(x + y), 0)
    return total
''',
    tests=[[[1, 2], [-2, -1], [-1, 2], [0, 2]], [[0], [0], [0], [0]], [[1], [1], [1], [1]], [[1], [2], [3], [-6]],
           [[-1, -1], [-1, 1], [-1, 1], [1, 1]], [[0, 0], [0, 0], [0, 0], [0, 0]],
           [[5, -5, 5], [1, 2, 3], [-3, -2, -1], [-5, 5, 0]], [[268435456], [268435456], [-268435456], [-268435456]],
           [[-268435456, 268435456], [-268435456, 268435456], [268435456, -268435456], [268435456, -268435456]],
           [[1, 2, 3], [4, 5, 6], [7, 8, 9], [10, 11, 12]]],
)
_r = rnd(2107)
p["tests"].append([[0] * 200, [0] * 200, [0] * 200, [0] * 200])
p["tests"].append([[_r.randint(-5, 5) for _ in range(200)] for _ in range(4)])
p["tests"].append([[_r.randint(-2 ** 28, 2 ** 28) for _ in range(200)] for _ in range(4)])
_x = [_r.randint(-1000, 1000) for _ in range(200)]
p["tests"].append([_x, [-v for v in _x], _x[::-1], [-v for v in _x[::-1]]])
p["tests"].append([[_r.randint(-40, 40) for _ in range(150)] for _ in range(4)])


def b_foursum(a, b, c, d):
    t = 0
    for w in a:
        for x in b:
            for y in c:
                for z in d:
                    if w + x + y + z == 0:
                        t += 1
    return t


def g_foursum(r):
    n = r.randint(1, 6)
    return [[r.randint(-3, 3) for _ in range(n)] for _ in range(4)]


def v_foursum(tests):
    for t in tests:
        arrs = t["args"]
        n = len(arrs[0])
        assert 1 <= n <= 200 and all(len(x) == n for x in arrs)
        assert all(-2 ** 28 <= v <= 2 ** 28 for x in arrs for v in x)


CHECKS["four-array-sum-zero-count"] = (b_foursum, g_foursum, "exact")
VALIDATE["four-array-sum-zero-count"] = v_foursum

p = add(
    id="max-pair-sum-equal-digit-sum", title="Max Pair Sum with Equal Digit Sum", diff="Medium", topic="Arrays & Hashing",
    fn="maxPairSumByDigitSum", params=[("nums", "int[]")], ret="int", cmp="exact",
    desc="<p>The <em>digit sum</em> of a positive integer is the sum of its decimal digits, so the digit sum of <code>4807</code> is <code>19</code>.</p><p>From the array <code>nums</code> of positive integers, choose two elements at different indices whose digit sums are equal, so that their total value is as large as possible. Return that maximum total, or <code>-1</code> if no two elements share a digit sum.</p><p>For example, <code>[18, 43, 36, 13, 7]</code> gives <code>54</code>, from <code>18 + 36</code> (both have digit sum 9).</p>",
    constraints=["1 &le; nums.length &le; 20,000", "1 &le; nums[i] &le; 10<sup>9</sup>"],
    hints=["Comparing every pair is O(n<sup>2</sup>). Group numbers by something cheaper to compare.",
           "Numbers can only be paired if they have the same digit sum, so use the digit sum as a grouping key.",
           "Within one group only the two largest values matter. Track the best value seen per digit sum and combine it with each new number from that group."],
    editorial=["Compute the digit sum of each number. For each digit sum keep the largest value seen so far in a hash map. When a new number <code>x</code> with digit sum <code>s</code> arrives and the map already holds a best value <code>m</code> for <code>s</code>, then <code>x + m</code> is the best pair ending at <code>x</code>; update the global answer, then store <code>max(m, x)</code>.",
               "Since a pair needs two elements, the answer is only defined when some group has at least two numbers; otherwise return -1. Digit sums here are at most 81, so even a plain array of size 82 works as the map. Overall O(n log M) for digit extraction. The largest possible total is 2 * 10<sup>9</sup>, which fits in a signed 32-bit integer."],
    time="O(n log M)", space="O(1)",
    solution='''def maxPairSumByDigitSum(nums):
    best = {}
    ans = -1
    for x in nums:
        s = 0
        y = x
        while y:
            s += y % 10
            y //= 10
        if s in best:
            ans = max(ans, best[s] + x)
            if x > best[s]:
                best[s] = x
        else:
            best[s] = x
    return ans
''',
    tests=[[[18, 43, 36, 13, 7]], [[10, 12, 19, 14]], [[5]], [[5, 5]], [[1, 10, 100, 1000]], [[99, 909, 9, 18]],
           [[1000000000, 1000000000]], [[999999999, 999999999, 1]], [[123, 321, 132, 213]], [[4, 13, 22, 31, 40]],
           [[19, 28, 37, 100]]],
)
_r = rnd(2108)
p["tests"].append([[_r.randint(1, 10 ** 9) for _ in range(20000)]])
p["tests"].append([[_r.randint(1, 1000) for _ in range(20000)]])
p["tests"].append([[10 ** 9 - i for i in range(0, 20000, 1)]])
p["tests"].append([[10 ** 9] * 20000])
p["tests"].append([[i * 11 + 1 for i in range(20000)]])


def b_digit(nums):
    def ds(v):
        return sum(int(ch) for ch in str(v))

    ans = -1
    for i in range(len(nums)):
        for j in range(i + 1, len(nums)):
            if ds(nums[i]) == ds(nums[j]):
                ans = max(ans, nums[i] + nums[j])
    return ans


def v_digit(tests):
    for t in tests:
        a = t["args"][0]
        assert 1 <= len(a) <= 20000 and all(1 <= v <= 10 ** 9 for v in a)


CHECKS["max-pair-sum-equal-digit-sum"] = (b_digit, lambda r: [gen_arr(r, 1, 120, 1, 10)], "exact")
VALIDATE["max-pair-sum-equal-digit-sum"] = v_digit


# ---------------------------------------------------------------- HARD

p = add(
    id="subarrays-with-exactly-k-distinct", title="Subarrays with Exactly K Distinct Values", diff="Hard", topic="Arrays & Hashing",
    fn="countExactlyKDistinct", params=[("nums", "int[]"), ("k", "int")], ret="int", cmp="exact",
    desc="<p>Given an integer array <code>nums</code> and an integer <code>k</code>, count the contiguous subarrays that contain <em>exactly</em> <code>k</code> different values.</p><p>Subarrays are counted by position, so equal-looking subarrays at different places count separately.</p><p>For example, <code>nums = [1, 2, 1, 2, 3]</code> and <code>k = 2</code> give <code>7</code>.</p>",
    constraints=["1 &le; nums.length &le; 20,000", "1 &le; nums[i] &le; nums.length", "1 &le; k &le; nums.length"],
    hints=["Counting subarrays with <em>at most</em> k distinct values is much easier than counting exactly k, because a sliding window behaves monotonically.",
           "For a fixed right end, if a window of distinct count at most <code>k</code> is valid, every shorter window ending there is valid too. Count all of them at once.",
           "The answer is <code>atMost(k) - atMost(k - 1)</code>. Implement <code>atMost</code> with two pointers and a frequency map."],
    editorial=["Define <code>atMost(m)</code> as the number of subarrays with at most <code>m</code> distinct values. A subarray has exactly <code>k</code> distinct values iff it has at most <code>k</code> but not at most <code>k - 1</code>, so the answer is <code>atMost(k) - atMost(k - 1)</code>.",
               "Compute <code>atMost(m)</code> with a sliding window and a frequency map: for each right end, add the new element, and while the window has more than <code>m</code> distinct values advance the left end, decrementing counts and dropping values that reach zero. The window <code>[left, right]</code> then has at most <code>m</code> distinct values, and every start between <code>left</code> and <code>right</code> works, contributing <code>right - left + 1</code> subarrays. Each pointer moves at most n times, giving O(n) overall.",
               "The answer can reach about n<sup>2</sup>/2, which is 2 * 10<sup>8</sup> for n = 20,000 and fits in 32 bits."],
    time="O(n)", space="O(n)",
    solution='''def countExactlyKDistinct(nums, k):
    def at_most(m):
        if m == 0:
            return 0
        freq = {}
        left = 0
        total = 0
        for right, x in enumerate(nums):
            freq[x] = freq.get(x, 0) + 1
            while len(freq) > m:
                y = nums[left]
                freq[y] -= 1
                if freq[y] == 0:
                    del freq[y]
                left += 1
            total += right - left + 1
        return total
    return at_most(k) - at_most(k - 1)
''',
    tests=[[[1, 2, 1, 2, 3], 2], [[1, 2, 1, 3, 4], 3], [[1], 1], [[1, 1, 1], 1], [[1, 2, 3], 3], [[1, 2, 3], 1],
           [[2, 2, 1, 1, 2], 2], [[1, 2, 1, 2, 1, 2], 2], [[1, 2, 3, 1, 2, 3], 3], [[3, 3, 3, 3], 2],
           [[1, 2, 2, 1, 3, 3, 2], 2]],
)
_r = rnd(2109)
p["tests"].append([[_r.randint(1, 5) for _ in range(20000)], 3])
p["tests"].append([[_r.randint(1, 200) for _ in range(20000)], 50])
p["tests"].append([[_r.randint(1, 20000) for _ in range(20000)], 7])
p["tests"].append([[1] * 20000, 1])
p["tests"].append([list(range(1, 20001)), 20000])
p["tests"].append([[1 + (i // 2) % 30 for i in range(20000)], 10])
p["tests"].append([[_r.randint(1, 2) for _ in range(20000)], 2])


def b_kdistinct(nums, k):
    n = len(nums)
    c = 0
    for i in range(n):
        seen = set()
        for j in range(i, n):
            seen.add(nums[j])
            if len(seen) == k:
                c += 1
    return c


def g_kdistinct(r):
    n = r.randint(1, 12)
    return [[r.randint(1, n) for _ in range(n)], r.randint(1, n)]


def v_kdistinct(tests):
    for t in tests:
        nums, k = t["args"]
        n = len(nums)
        assert 1 <= n <= 20000 and 1 <= k <= n
        assert all(1 <= v <= n for v in nums)


CHECKS["subarrays-with-exactly-k-distinct"] = (b_kdistinct, g_kdistinct, "exact")
VALIDATE["subarrays-with-exactly-k-distinct"] = v_kdistinct

p = add(
    id="count-equal-012-subarrays", title="Count Subarrays with Equal 0s, 1s and 2s", diff="Hard", topic="Arrays & Hashing",
    fn="countEqualThree", params=[("nums", "int[]")], ret="int", cmp="exact",
    desc="<p>The array <code>nums</code> contains only the values <code>0</code>, <code>1</code> and <code>2</code>. Count the contiguous subarrays in which the number of <code>0</code>s, the number of <code>1</code>s and the number of <code>2</code>s are all equal.</p><p>Such a subarray must have a length divisible by 3. The empty subarray is not counted.</p><p>For example, <code>[0, 1, 2, 0, 1, 2]</code> gives <code>4</code>.</p>",
    constraints=["0 &le; nums.length &le; 20,000", "nums[i] is 0, 1 or 2"],
    hints=["For two symbols, a running difference of counts works. How can the same idea extend to three symbols?",
           "Keep prefix counts <code>c0, c1, c2</code>. A subarray is balanced iff the three prefix counts grew by the same amount between its two ends.",
           "Equal growth means the differences between counts stay unchanged, so use the pair <code>(c1 - c0, c2 - c1)</code> as a key. Two prefixes with the same pair delimit a balanced subarray; count equal keys in a hash map."],
    editorial=["Let <code>(c0, c1, c2)</code> be the number of each symbol in the prefix. A subarray between prefix <code>i</code> and prefix <code>j</code> has all three counts equal exactly when <code>c0[j] - c0[i] = c1[j] - c1[i] = c2[j] - c2[i]</code>. Rearranging, this is the same as <code>c1[j] - c0[j] = c1[i] - c0[i]</code> and <code>c2[j] - c1[j] = c2[i] - c1[i]</code>.",
               "So each prefix is summarised by the key <code>(c1 - c0, c2 - c1)</code>, and balanced subarrays correspond to pairs of prefixes with equal keys. Keep a hash map from key to the number of earlier prefixes with that key, seeded with the empty prefix key <code>(0, 0)</code>. For each position add the current count of its key to the answer, then increment it. The empty subarray is never counted because we only pair a prefix with strictly earlier ones.",
               "Time and space are O(n). The answer is at most about n<sup>2</sup>/6 and fits comfortably in 32 bits."],
    time="O(n)", space="O(n)",
    solution='''def countEqualThree(nums):
    seen = {(0, 0): 1}
    c = [0, 0, 0]
    total = 0
    for x in nums:
        c[x] += 1
        key = (c[1] - c[0], c[2] - c[1])
        total += seen.get(key, 0)
        seen[key] = seen.get(key, 0) + 1
    return total
''',
    tests=[[[0, 1, 2, 0, 1, 2]], [[]], [[0]], [[0, 1, 2]], [[2, 1, 0]], [[0, 0, 0]], [[0, 1, 1, 2, 0, 2]],
           [[0, 1, 2, 2, 1, 0]], [[1, 0, 2, 0, 1, 2, 1, 0, 2]], [[0, 1, 0, 1, 2, 2]], [[2, 2, 0, 1, 0, 1, 2, 1, 0]]],
)
_r = rnd(2110)
p["tests"].append([[_r.randint(0, 2) for _ in range(20000)]])
p["tests"].append([[i % 3 for i in range(20000)]])
p["tests"].append([[0] * 20000])
p["tests"].append([[(i // 4) % 3 for i in range(19998)]])
_blocks = []
for _ in range(6666):
    _b = [0, 1, 2]; _r.shuffle(_b); _blocks.extend(_b)
p["tests"].append([_blocks])
p["tests"].append([[_r.choice([0, 0, 1, 2]) for _ in range(20000)]])


def b_equal3(nums):
    n = len(nums)
    c = 0
    for i in range(n):
        for j in range(i + 3, n + 1, 3):
            seg = nums[i:j]
            if seg.count(0) == seg.count(1) == seg.count(2):
                c += 1
    return c


def v_equal3(tests):
    for t in tests:
        a = t["args"][0]
        assert len(a) <= 20000 and all(x in (0, 1, 2) for x in a)


CHECKS["count-equal-012-subarrays"] = (b_equal3, lambda r: [gen_arr(r, 0, 2, 0, 15)], "exact")
VALIDATE["count-equal-012-subarrays"] = v_equal3
