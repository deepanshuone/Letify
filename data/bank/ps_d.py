"""Problems: prefix sums with hashing, XOR and modulo. See data/lib.py for the registry."""
from lib import add, rnd, CHECKS, VALIDATE, gen_arr  # noqa: F401

T = "Prefix Sums"
MOD = 10 ** 9 + 7

# ---------------------------------------------------------------- 1. range XOR queries

p = add(
    id="range-xor-queries", title="Range XOR Queries", diff="Easy", topic=T, tier="common",
    fn="rangeXor", params=[("arr", "int[]"), ("queries", "int[][]")], ret="int[]", cmp="exact",
    desc="<p>You are given an array <code>arr</code> of non-negative integers and a list of queries. Each query is a pair <code>[l, r]</code> (0-indexed, both ends inclusive). For every query, compute the bitwise XOR of <code>arr[l], arr[l+1], ..., arr[r]</code>.</p><p>Return the answers in the order of the queries.</p><pre>arr = [1, 3, 4, 8], queries = [[0, 1], [1, 2], [0, 3], [3, 3]]\nanswers: 1^3 = 2,  3^4 = 7,  1^3^4^8 = 14,  8\nresult = [2, 7, 14, 8]</pre>",
    constraints=["1 &le; arr.length &le; 10,000", "1 &le; queries.length &le; 10,000", "0 &le; arr[i] &lt; 2<sup>30</sup>", "0 &le; l &le; r &lt; arr.length"],
    hints=["Answering each query by looping from <code>l</code> to <code>r</code> is O(n) per query. Can the work be shared between queries?",
           "Just as range sums use prefix sums, think about a prefix XOR: <code>px[i]</code> is the XOR of the first <code>i</code> elements.",
           "Since <code>x ^ x = 0</code>, <code>px[r+1] ^ px[l]</code> cancels the common prefix and leaves exactly the XOR of <code>arr[l..r]</code>."],
    editorial=["XOR is associative and every value is its own inverse, so it plays the same role that addition and subtraction play for sums. Let <code>px[0] = 0</code> and <code>px[i+1] = px[i] ^ arr[i]</code>. Then <code>px[r+1]</code> is the XOR of <code>arr[0..r]</code> and <code>px[l]</code> is the XOR of <code>arr[0..l-1]</code>; XOR-ing them cancels the first <code>l</code> elements and leaves <code>arr[l..r]</code>.",
               "Build the prefix array once in O(n) and answer each query with one XOR in O(1). Total time O(n + q), extra space O(n). The idea is the base of every XOR-with-prefix trick: two equal prefix values mean the block between them has XOR 0."],
    time="O(n + q)", space="O(n)",
    solution='''def rangeXor(arr, queries):
    px = [0] * (len(arr) + 1)
    for i, x in enumerate(arr):
        px[i + 1] = px[i] ^ x
    return [px[r + 1] ^ px[l] for l, r in queries]
''',
    tests=[[[1, 3, 4, 8], [[0, 1], [1, 2], [0, 3], [3, 3]]], [[4, 8, 2, 10], [[2, 3], [1, 3], [0, 0], [0, 3]]],
           [[5], [[0, 0]]], [[7, 7], [[0, 1], [0, 0], [1, 1]]], [[0, 0, 0], [[0, 2], [1, 1]]],
           [[1073741823, 1, 1073741822], [[0, 2], [0, 1], [1, 2]]], [[6, 6, 6, 6, 6], [[0, 4], [1, 4], [2, 3], [0, 3]]],
           [[1, 2, 4, 8, 16, 32], [[0, 5], [2, 4], [5, 5], [1, 3]]]],
)
_r = rnd(9401)
_n = 4000
_a = [_r.randint(0, 2 ** 30 - 1) for _ in range(_n)]
_q = []
for _ in range(2500):
    _l = _r.randint(0, _n - 1)
    _q.append([_l, _r.randint(_l, _n - 1)])
p["tests"].append([_a, _q])
_n = 6000
_a = [_r.randint(0, 255) for _ in range(_n)]
_q = []
for _ in range(2000):
    _l = _r.randint(0, _n - 1)
    _q.append([_l, _r.randint(_l, _n - 1)])
_q.append([0, _n - 1])
p["tests"].append([_a, _q])


def b_rangexor(arr, queries):
    out = []
    for l, r in queries:
        x = 0
        for i in range(l, r + 1):
            x ^= arr[i]
        out.append(x)
    return out


def g_rangexor(r):
    n = r.randint(1, 9)
    a = [r.randint(0, 15) for _ in range(n)]
    q = []
    for _ in range(r.randint(1, 6)):
        l = r.randint(0, n - 1)
        q.append([l, r.randint(l, n - 1)])
    return [a, q]


def v_rangexor(tests):
    for t in tests:
        a, q = t["args"]
        assert 1 <= len(a) <= 10000 and 1 <= len(q) <= 10000
        assert all(0 <= x < 2 ** 30 for x in a)
        assert all(0 <= l <= r < len(a) for l, r in q)


CHECKS["range-xor-queries"] = (b_rangexor, g_rangexor, "exact")
VALIDATE["range-xor-queries"] = v_rangexor

# ---------------------------------------------------------------- 2. pairs with sum divisible by k

p = add(
    id="count-pairs-sum-divisible-by-k", title="Count Pairs with Sum Divisible by K", diff="Easy", topic=T, tier="common",
    fn="countPairs", params=[("nums", "int[]"), ("k", "int")], ret="int", cmp="exact",
    desc="<p>Given an array <code>nums</code> of positive integers and an integer <code>k</code>, count the pairs of indices <code>i &lt; j</code> such that <code>nums[i] + nums[j]</code> is divisible by <code>k</code>.</p><pre>nums = [30, 20, 150, 100, 40], k = 60\nmatching pairs: (30, 150), (20, 100), (20, 40)\nresult = 3</pre>",
    constraints=["1 &le; nums.length &le; 8,000", "1 &le; nums[i] &le; 10<sup>9</sup>", "1 &le; k &le; 1,000", "The answer fits in a 32-bit integer"],
    hints=["Checking every pair is O(n<sup>2</sup>). Only the remainders modulo <code>k</code> matter, not the values themselves.",
           "<code>a + b</code> is divisible by <code>k</code> exactly when <code>a % k</code> and <code>b % k</code> add up to <code>0</code> or to <code>k</code>. So the partner remainder of <code>r</code> is <code>(k - r) % k</code>.",
           "Scan left to right with a counter of remainders seen so far. For each element add <code>count[(k - r) % k]</code> to the answer, then record <code>r</code>."],
    editorial=["Replace every number by its remainder <code>r = x % k</code>. A pair is good when the remainders sum to a multiple of <code>k</code>, which means <code>r1 + r2 = 0</code> (both zero) or <code>r1 + r2 = k</code>. Equivalently, the partner of remainder <code>r</code> is <code>(k - r) % k</code>.",
               "Walk through the array keeping a counter (an array of size <code>k</code>) of earlier remainders. For the current element, every earlier element with the partner remainder forms one new pair; add that count and then record the current remainder. Because each pair is counted when its later element arrives, no pair is counted twice and a number is never paired with itself. This runs in O(n + k) time and O(k) space."],
    time="O(n + k)", space="O(k)",
    solution='''def countPairs(nums, k):
    cnt = [0] * k
    total = 0
    for x in nums:
        r = x % k
        total += cnt[(k - r) % k]
        cnt[r] += 1
    return total
''',
    tests=[[[30, 20, 150, 100, 40], 60], [[1, 2, 3, 4, 5], 3], [[5], 5], [[2, 2], 4], [[3, 3, 3], 1], [[1, 1, 1], 2],
           [[10, 20, 30, 40], 10], [[1000000000, 1000000000], 1000], [[7, 14, 21, 28, 35], 7], [[999999999, 1, 2, 3], 1000]],
)
_r = rnd(9402)
p["tests"].append([[_r.randint(1, 10 ** 9) for _ in range(8000)], 997])
p["tests"].append([[_r.randint(1, 50) for _ in range(8000)], 10])
p["tests"].append([[_r.choice([6, 12, 18, 7]) for _ in range(8000)], 6])


def b_pairsdiv(nums, k):
    c = 0
    for i in range(len(nums)):
        for j in range(i + 1, len(nums)):
            if (nums[i] + nums[j]) % k == 0:
                c += 1
    return c


def v_pairsdiv(tests):
    for t in tests:
        a, k = t["args"]
        assert 1 <= len(a) <= 8000 and all(1 <= x <= 10 ** 9 for x in a) and 1 <= k <= 1000


CHECKS["count-pairs-sum-divisible-by-k"] = (
    b_pairsdiv, lambda r: [[r.randint(1, 30) for _ in range(r.randint(1, 10))], r.randint(1, 9)], "exact")
VALIDATE["count-pairs-sum-divisible-by-k"] = v_pairsdiv

# ---------------------------------------------------------------- 3. can pair up with sums divisible by k

p = add(
    id="pair-up-sums-divisible-by-k", title="Pair Up Sums Divisible by K", diff="Easy", topic=T, tier="common",
    fn="canPairUp", params=[("arr", "int[]"), ("k", "int")], ret="bool", cmp="exact",
    desc="<p>The array <code>arr</code> has an even length. Decide whether its elements can be split into <code>arr.length / 2</code> pairs so that the sum of every pair is divisible by <code>k</code>. Every element must be used in exactly one pair.</p><p>Elements may be negative.</p><pre>arr = [1, 2, 3, 4, 5, 10, 6, 7, 8, 9], k = 5\npairs: (1, 9), (2, 8), (3, 7), (4, 6), (5, 10)\nresult = true</pre>",
    constraints=["2 &le; arr.length &le; 10,000 and arr.length is even", "-10<sup>9</sup> &le; arr[i] &le; 10<sup>9</sup>", "1 &le; k &le; 100,000"],
    hints=["Which numbers can be paired with a given number <code>x</code>? Only the ones whose remainder modulo <code>k</code> complements <code>x</code>'s remainder.",
           "Count how many elements have each remainder (made non-negative, e.g. <code>((x % k) + k) % k</code>). Remainder <code>r</code> needs partners with remainder <code>k - r</code>.",
           "The counts of <code>r</code> and <code>k - r</code> must be equal. Remainder <code>0</code> (and <code>k/2</code> when <code>k</code> is even) pairs with itself, so its count must be even."],
    editorial=["Only remainders modulo <code>k</code> matter. Count how many elements fall into each remainder class. An element with remainder <code>r &ne; 0</code> can only be paired with an element of remainder <code>k - r</code>, so those two classes must have exactly the same size.",
               "Two classes pair with themselves: remainder <code>0</code>, and remainder <code>k/2</code> if <code>k</code> is even. Their counts must be even. If every condition holds, a valid pairing exists by simply matching elements inside the paired classes. Languages whose <code>%</code> can return negative values need the normalisation <code>((x % k) + k) % k</code>. The solution runs in O(n + k) time."],
    time="O(n + k)", space="O(k)",
    solution='''def canPairUp(arr, k):
    cnt = [0] * k
    for x in arr:
        cnt[x % k] += 1
    if cnt[0] % 2:
        return False
    for r in range(1, k // 2 + 1):
        if r == k - r:
            if cnt[r] % 2:
                return False
        elif cnt[r] != cnt[k - r]:
            return False
    return True
''',
    tests=[[[1, 2, 3, 4, 5, 10, 6, 7, 8, 9], 5], [[1, 2, 3, 4, 5, 6], 7], [[1, 2, 3, 4, 5, 6], 10], [[-10, 10], 2],
           [[-1, 1, -2, 2], 3], [[3, 3], 6], [[3, 4], 6], [[1, 1], 2], [[1, 3, 5, 7], 4], [[2, 6, 4, 4], 8],
           [[5, 5, 5, 5], 10], [[-1000000000, 1000000000, 7, -7], 100000]],
)
_r = rnd(9403)


def _mk_pairs(r, n, k, ok):
    a = []
    for _ in range(n // 2):
        x = r.randint(-10 ** 9, 10 ** 9)
        y = r.randint(-10 ** 9, 10 ** 9)
        y = y - (x + y) % k  # y + x is now divisible by k
        if not -10 ** 9 <= y <= 10 ** 9:
            y += k if y < -10 ** 9 else -k
        a += [x, y]
    if not ok:
        a[0] += 1 if a[0] < 10 ** 9 else -1
    r.shuffle(a)
    return a


p["tests"].append([_mk_pairs(_r, 4000, 99991, True), 99991])
p["tests"].append([_mk_pairs(_r, 4000, 99991, False), 99991])
p["tests"].append([[(i % 1000) * 7 for i in range(0, 5000)], 50])


def b_pairup(arr, k):
    def go(rest):
        if not rest:
            return True
        a = rest[0]
        for j in range(1, len(rest)):
            if (a + rest[j]) % k == 0 and go(rest[1:j] + rest[j + 1:]):
                return True
        return False
    return go(list(arr))


def g_pairup(r):
    k = r.randint(1, 7)
    n = 2 * r.randint(1, 4)
    if r.random() < 0.5:
        a = []
        for _ in range(n // 2):
            x = r.randint(-12, 12)
            a += [x, r.randint(-3, 3) * k - x]
        r.shuffle(a)
        return [a, k]
    return [[r.randint(-12, 12) for _ in range(n)], k]


def v_pairup(tests):
    for t in tests:
        a, k = t["args"]
        assert 2 <= len(a) <= 10000 and len(a) % 2 == 0
        assert all(-10 ** 9 <= x <= 10 ** 9 for x in a) and 1 <= k <= 100000
    assert any(t["expected"] for t in tests) and not all(t["expected"] for t in tests)


CHECKS["pair-up-sums-divisible-by-k"] = (b_pairup, g_pairup, "exact")
VALIDATE["pair-up-sums-divisible-by-k"] = v_pairup

# ---------------------------------------------------------------- 4. shortest subarray with sum divisible by k

p = add(
    id="shortest-subarray-sum-divisible-by-k", title="Shortest Subarray with Sum Divisible by K", diff="Medium", topic=T, tier="common",
    fn="shortestDivisible", params=[("nums", "int[]"), ("k", "int")], ret="int", cmp="exact",
    desc="<p>Given an integer array <code>nums</code> (values may be negative) and a positive integer <code>k</code>, return the length of the <strong>shortest</strong> non-empty contiguous subarray whose sum is divisible by <code>k</code>. If there is no such subarray, return <code>-1</code>.</p><pre>nums = [3, 1, 4, 2], k = 5\n[1, 4] sums to 5, no single element is divisible by 5\nresult = 2</pre>",
    constraints=["1 &le; nums.length &le; 5,000", "-10<sup>9</sup> &le; nums[i] &le; 10<sup>9</sup>", "1 &le; k &le; 10<sup>9</sup>"],
    hints=["A block <code>i..j-1</code> has sum divisible by <code>k</code> when its two prefix sums have the same remainder modulo <code>k</code>.",
           "For a fixed right end, the shortest block uses the <em>most recent</em> earlier prefix with the same remainder. Python's <code>%</code> already returns a non-negative remainder for negative sums.",
           "Keep a dictionary <code>last[remainder] = prefix index</code>, initialised with <code>{0: 0}</code> for the empty prefix. For each new prefix update the answer with <code>j - last[rem]</code> if present, then overwrite <code>last[rem] = j</code>."],
    editorial=["Let <code>P[j]</code> be the sum of the first <code>j</code> elements. The block between prefix positions <code>i &lt; j</code> has sum <code>P[j] - P[i]</code>, which is a multiple of <code>k</code> iff <code>P[i] &equiv; P[j] (mod k)</code>. So the task is: find two prefix positions with equal remainders that are as close together as possible.",
               "For a given <code>j</code> the best partner is the nearest earlier position with the same remainder, so a dictionary storing only the latest index per remainder is enough. Start with remainder 0 at index 0 (the empty prefix, which lets a prefix itself qualify). Overwriting the stored index after each lookup keeps it the latest. The scan is O(n) time and O(min(n, k)) space. Negative sums are handled by taking remainders that are always in <code>[0, k)</code>."],
    time="O(n)", space="O(min(n, k))",
    solution='''def shortestDivisible(nums, k):
    last = {0: 0}
    s = 0
    best = -1
    for j, x in enumerate(nums, 1):
        s = (s + x) % k
        if s in last:
            d = j - last[s]
            if best == -1 or d < best:
                best = d
        last[s] = j
    return best
''',
    tests=[[[3, 1, 4, 2], 5], [[4, 5, 0, -2, -3, 1], 5], [[1, 2, 3], 100], [[7], 7], [[7], 5], [[-6], 3], [[2, 2, 2, 2], 4],
           [[1, 1, 1, 1, 1], 3], [[5, -5], 10], [[1000000000, 1000000000, 1000000000], 1000000000], [[3, 4, 5], 1000000000]],
)
_r = rnd(9404)
p["tests"].append([[_r.randint(-10 ** 9, 10 ** 9) for _ in range(5000)], 4999])
p["tests"].append([[_r.randint(-10 ** 9, 10 ** 9) for _ in range(5000)], 1000000000])
p["tests"].append([[_r.randint(1, 9) for _ in range(5000)], 9973])


def b_shortdiv(nums, k):
    best = -1
    n = len(nums)
    for i in range(n):
        s = 0
        for j in range(i, n):
            s += nums[j]
            if s % k == 0:
                if best == -1 or j - i + 1 < best:
                    best = j - i + 1
                break
    return best


def v_shortdiv(tests):
    for t in tests:
        a, k = t["args"]
        assert 1 <= len(a) <= 5000 and all(-10 ** 9 <= x <= 10 ** 9 for x in a) and 1 <= k <= 10 ** 9
    assert any(t["expected"] == -1 for t in tests)


CHECKS["shortest-subarray-sum-divisible-by-k"] = (
    b_shortdiv, lambda r: [gen_arr(r, -9, 9, 1, 10), r.randint(1, 15)], "exact")
VALIDATE["shortest-subarray-sum-divisible-by-k"] = v_shortdiv

# ---------------------------------------------------------------- 5. longest subarray with sum divisible by k

p = add(
    id="longest-subarray-sum-divisible-by-k", title="Longest Subarray with Sum Divisible by K", diff="Medium", topic=T, tier="common",
    fn="longestDivisible", params=[("nums", "int[]"), ("k", "int")], ret="int", cmp="exact",
    desc="<p>Given an integer array <code>nums</code> (values may be negative) and a positive integer <code>k</code>, return the length of the <strong>longest</strong> contiguous subarray whose sum is divisible by <code>k</code>. If no non-empty subarray qualifies, return <code>0</code>.</p><pre>nums = [2, 7, 6, 1, 4, 5], k = 3\nthe block [7, 6, 1, 4] sums to 18, which is divisible by 3\nresult = 4</pre>",
    constraints=["1 &le; nums.length &le; 8,000", "-10<sup>6</sup> &le; nums[i] &le; 10<sup>6</sup>", "1 &le; k &le; 10<sup>6</sup>"],
    hints=["Equal prefix remainders modulo <code>k</code> mean the block between them has a sum divisible by <code>k</code>.",
           "To make a block as long as possible you want the <em>earliest</em> prefix with a given remainder, not the latest.",
           "Store <code>first[remainder]</code> the first time it appears (the empty prefix gives <code>first[0] = 0</code>). For later prefixes with the same remainder, candidate length is <code>j - first[remainder]</code>; never overwrite the stored index."],
    editorial=["Prefix remainders reduce the problem to: find two prefix positions <code>i &lt; j</code> with <code>P[i] % k == P[j] % k</code> and maximise <code>j - i</code>. For each remainder the best left end is its first occurrence, so remember the first index per remainder and compare each later occurrence against it.",
               "This is the mirror image of the shortest-subarray version: there you keep the latest index, here you keep the earliest. Seed the map with remainder 0 at index 0 so that prefixes starting at position 0 count. Time O(n), space O(min(n, k))."],
    time="O(n)", space="O(min(n, k))",
    solution='''def longestDivisible(nums, k):
    first = {0: 0}
    s = 0
    best = 0
    for j, x in enumerate(nums, 1):
        s = (s + x) % k
        if s in first:
            best = max(best, j - first[s])
        else:
            first[s] = j
    return best
''',
    tests=[[[2, 7, 6, 1, 4, 5], 3], [[1, 2, 3], 7], [[5], 5], [[5], 3], [[-1, 1], 5], [[1, 1, 1, 1], 2], [[3, 3, 3], 1],
           [[4, -1, -3, 8, 2], 6], [[1000000, 1000000, -1000000], 1000000], [[2, 4, 6, 8], 7]],
)
_r = rnd(9405)
p["tests"].append([[_r.randint(-10 ** 6, 10 ** 6) for _ in range(8000)], 99991])
p["tests"].append([[_r.randint(0, 3) for _ in range(8000)], 1000])
_a = [_r.randint(1, 5) for _ in range(6000)]
p["tests"].append([_a, 1000000])


def b_longdiv(nums, k):
    best = 0
    n = len(nums)
    for i in range(n):
        s = 0
        for j in range(i, n):
            s += nums[j]
            if s % k == 0:
                best = max(best, j - i + 1)
    return best


def v_longdiv(tests):
    for t in tests:
        a, k = t["args"]
        assert 1 <= len(a) <= 8000 and all(-10 ** 6 <= x <= 10 ** 6 for x in a) and 1 <= k <= 10 ** 6
    assert any(t["expected"] == 0 for t in tests)


CHECKS["longest-subarray-sum-divisible-by-k"] = (
    b_longdiv, lambda r: [gen_arr(r, -9, 9, 1, 10), r.randint(1, 15)], "exact")
VALIDATE["longest-subarray-sum-divisible-by-k"] = v_longdiv

# ---------------------------------------------------------------- 6. max sum with length multiple of k

p = add(
    id="max-sum-subarray-length-multiple-of-k", title="Max Sum Subarray with Length Multiple of K", diff="Medium", topic=T, tier="extra",
    fn="maxSumMultipleLength", params=[("nums", "int[]"), ("k", "int")], ret="int", cmp="exact",
    desc="<p>Given an integer array <code>nums</code> (values may be negative) and a positive integer <code>k</code>, find the maximum sum over all contiguous subarrays whose <strong>length is a multiple of k</strong> (<code>k</code>, <code>2k</code>, <code>3k</code>, ...).</p><p>Since <code>nums.length &ge; k</code>, at least one such subarray always exists.</p><pre>nums = [1, 2, -3, 4], k = 2\nlength 2: 3, -1, 1;   length 4: 4\nresult = 4</pre>",
    constraints=["1 &le; k &le; nums.length &le; 8,000", "-1,000 &le; nums[i] &le; 1,000"],
    hints=["Trying all start and end positions is O(n<sup>2</sup>). Express a subarray sum as a difference of two prefix sums.",
           "A subarray from prefix index <code>i</code> to <code>j</code> has length <code>j - i</code>, which is a multiple of <code>k</code> exactly when <code>i % k == j % k</code>.",
           "For each residue class of the prefix index keep the minimum prefix sum seen so far. For every <code>j</code>, the best subarray ending there is <code>P[j] - minPrefix[j % k]</code> (only when that class already has an earlier entry)."],
    editorial=["With prefix sums <code>P[0..n]</code>, the subarray covering positions <code>i..j-1</code> has sum <code>P[j] - P[i]</code> and length <code>j - i</code>. The length is a positive multiple of <code>k</code> iff <code>i &lt; j</code> and <code>i &equiv; j (mod k)</code>.",
               "So the prefix indices split into <code>k</code> classes by index modulo <code>k</code>, and within a class we want the largest difference <code>P[j] - P[i]</code> with <code>i &lt; j</code>. Scan <code>j</code> from 0 to <code>n</code>, maintain the minimum prefix sum of each class, and update the answer with <code>P[j] - min[class]</code> before updating that minimum. This is O(n) time and O(k) space. It is the 'best time to buy and sell' idea applied separately to each index residue."],
    time="O(n)", space="O(k)",
    solution='''def maxSumMultipleLength(nums, k):
    INF = float("inf")
    mn = [INF] * k
    best = -INF
    s = 0
    for j in range(len(nums) + 1):
        if j:
            s += nums[j - 1]
        c = j % k
        if mn[c] != INF:
            best = max(best, s - mn[c])
        if s < mn[c]:
            mn[c] = s
    return best
''',
    tests=[[[1, 2, -3, 4], 2], [[-5, 1, 2, -3, 4], 2], [[-1, -2, -3], 1], [[-1, -2, -3], 3], [[5], 1], [[4, -4, 4, -4], 4],
           [[-2, -2, 9, -1, -1], 3], [[1000, 1000, 1000], 2], [[-1000, -1000, -1000, -1000], 2], [[3, -1, 2, -1, 3, -4, 5], 3]],
)
_r = rnd(9406)
p["tests"].append([[_r.randint(-1000, 1000) for _ in range(8000)], 7])
p["tests"].append([[_r.randint(-1000, 1000) for _ in range(8000)], 1])
p["tests"].append([[_r.randint(-1000, 800) for _ in range(8000)], 4000])


def b_maxmult(nums, k):
    best = None
    n = len(nums)
    for i in range(n):
        s = 0
        for j in range(i, n):
            s += nums[j]
            if (j - i + 1) % k == 0 and (best is None or s > best):
                best = s
    return best


def v_maxmult(tests):
    for t in tests:
        a, k = t["args"]
        assert 1 <= k <= len(a) <= 8000 and all(-1000 <= x <= 1000 for x in a)


CHECKS["max-sum-subarray-length-multiple-of-k"] = (
    b_maxmult, lambda r: (lambda a: [a, r.randint(1, len(a))])(gen_arr(r, -9, 9, 1, 10)), "exact")
VALIDATE["max-sum-subarray-length-multiple-of-k"] = v_maxmult

# ---------------------------------------------------------------- 7. non-overlapping subarrays with sum target

p = add(
    id="max-disjoint-subarrays-with-target-sum", title="Maximum Disjoint Subarrays with Target Sum", diff="Medium", topic=T, tier="common",
    fn="maxDisjoint", params=[("nums", "int[]"), ("target", "int")], ret="int", cmp="exact",
    desc="<p>Given an integer array <code>nums</code> (values may be negative or zero) and an integer <code>target</code>, choose as many <strong>non-overlapping</strong> non-empty contiguous subarrays as possible such that each chosen subarray has a sum equal to <code>target</code>. Return the maximum number of subarrays you can choose.</p><pre>nums = [-1, 3, 5, 1, 4, 2, -9], target = 6\ndisjoint blocks with sum 6: [5, 1] and [4, 2]\nresult = 2</pre>",
    constraints=["1 &le; nums.length &le; 8,000", "-1,000 &le; nums[i] &le; 1,000", "-10<sup>6</sup> &le; target &le; 10<sup>6</sup>"],
    hints=["Finding every subarray with sum <code>target</code> is the easy part (prefix sums + hash set). The question is which of them to keep.",
           "This is like interval scheduling: among blocks that end earliest, taking the one that finishes first never hurts the future.",
           "Scan left to right with a set of prefix sums since the last chosen block (starting with <code>{0}</code>). When <code>running - target</code> is in the set, count a block and reset the set and the running sum."],
    editorial=["Each subarray with sum <code>target</code> is an interval. Choosing the maximum number of pairwise disjoint intervals is solved greedily by always taking the interval with the earliest right end: it leaves the most room for the rest.",
               "While scanning, keep the prefix sums observed since the end of the last chosen block (plus 0 for the empty start). At each position, if <code>running - target</code> is in that set then some block ending here has sum <code>target</code> and lies entirely after the last chosen block; it is the earliest-ending one available, so take it, increment the answer, and restart with an empty history. Otherwise record the running sum. The scan is O(n) time and O(n) space."],
    time="O(n)", space="O(n)",
    solution='''def maxDisjoint(nums, target):
    seen = {0}
    run = 0
    count = 0
    for x in nums:
        run += x
        if run - target in seen:
            count += 1
            seen = {0}
            run = 0
        else:
            seen.add(run)
    return count
''',
    tests=[[[-1, 3, 5, 1, 4, 2, -9], 6], [[1, 1, 1, 1, 1], 2], [[0, 0, 0], 0], [[5], 5], [[5], 4], [[1, -1, 1, -1], 0],
           [[2, 3, 1, 4], 10], [[3, 3, 3, 3], 6], [[1, 2, 3, 3, 0, 3], 3], [[-5, 5, -5, 5], 0], [[1000, -1000, 1000], 1000]],
)
_r = rnd(9407)
p["tests"].append([[_r.randint(-3, 3) for _ in range(8000)], 2])
p["tests"].append([[_r.randint(-1000, 1000) for _ in range(8000)], 1500])
p["tests"].append([[_r.randint(0, 2) for _ in range(8000)], 0])


def b_disjoint(nums, target):
    n = len(nums)
    pre = [0]
    for x in nums:
        pre.append(pre[-1] + x)
    dp = [0] * (n + 1)
    for j in range(1, n + 1):
        dp[j] = dp[j - 1]
        for i in range(j):
            if pre[j] - pre[i] == target:
                dp[j] = max(dp[j], dp[i] + 1)
    return dp[n]


def v_disjoint(tests):
    for t in tests:
        a, tg = t["args"]
        assert 1 <= len(a) <= 8000 and all(-1000 <= x <= 1000 for x in a) and -10 ** 6 <= tg <= 10 ** 6


CHECKS["max-disjoint-subarrays-with-target-sum"] = (
    b_disjoint, lambda r: [gen_arr(r, -3, 3, 1, 12), r.randint(-3, 4)], "exact")
VALIDATE["max-disjoint-subarrays-with-target-sum"] = v_disjoint

# ---------------------------------------------------------------- 8. max XOR per pop query

p = add(
    id="max-xor-per-pop-query", title="Maximum XOR per Pop Query", diff="Medium", topic=T, tier="extra",
    fn="maxXorQueries", params=[("nums", "int[]"), ("bits", "int")], ret="int[]", cmp="exact",
    desc="<p>You are given an array <code>nums</code> sorted in non-decreasing order, in which every value is smaller than <code>2<sup>bits</sup></code>. You run <code>n = nums.length</code> rounds. In each round:</p><ol><li>Choose an integer <code>k</code> with <code>0 &le; k &lt; 2<sup>bits</sup></code> that maximises the XOR of <code>k</code> with all elements currently in the array, and record <code>k</code>.</li><li>Remove the <strong>last</strong> element of the array.</li></ol><p>Return the list of recorded values <code>k</code>, one per round, in order.</p><pre>nums = [0, 1, 1, 3], bits = 2\nround 1: XOR of all = 0^1^1^3 = 3, best k = 0  (3^0 = 3)\nround 2: [0, 1, 1] XOR = 0, best k = 3\nround 3: [0, 1] XOR = 1, best k = 2\nround 4: [0] XOR = 0, best k = 3\nresult = [0, 3, 2, 3]</pre>",
    constraints=["1 &le; nums.length &le; 10,000", "1 &le; bits &le; 30", "0 &le; nums[i] &lt; 2<sup>bits</sup>", "nums is sorted in non-decreasing order"],
    hints=["Let <code>X</code> be the XOR of the current elements. You want to choose <code>k</code> so that <code>X ^ k</code> is as large as possible. What is the largest value below <code>2<sup>bits</sup></code>?",
           "The best <code>X ^ k</code> is all ones in the lowest <code>bits</code> positions, i.e. <code>2<sup>bits</sup> - 1</code>. That forces <code>k</code> to be the bitwise complement of <code>X</code> inside those bits.",
           "Compute the XOR of the whole array once, then for each round output <code>X ^ (2<sup>bits</sup> - 1)</code> and XOR away the removed last element to update <code>X</code>."],
    editorial=["For a fixed XOR value <code>X &lt; 2<sup>bits</sup></code>, the maximum of <code>X ^ k</code> over <code>k &lt; 2<sup>bits</sup></code> is the all-ones mask <code>M = 2<sup>bits</sup> - 1</code>, reached exactly when <code>k = X ^ M</code>. That choice of <code>k</code> is unique, so the answer is deterministic.",
               "The elements removed are always the last ones, so the XOR needed in round <code>i</code> is a prefix XOR of the array: the XOR of the first <code>n - i</code> elements. Compute the prefix XORs in one pass (or the total XOR and peel off elements from the end by XOR-ing them again) and map each to its complement. O(n) time, O(1) extra space besides the output."],
    time="O(n)", space="O(n)",
    solution='''def maxXorQueries(nums, bits):
    mask = (1 << bits) - 1
    x = 0
    for v in nums:
        x ^= v
    out = []
    for v in reversed(nums):
        out.append(x ^ mask)
        x ^= v
    return out
''',
    tests=[[[0, 1, 1, 3], 2], [[2, 3, 4, 7], 3], [[0, 1, 2, 2, 5, 7], 3], [[0], 1], [[1], 1], [[5, 5], 3], [[0, 0, 0], 4],
           [[1073741823], 30], [[0, 1073741823, 1073741823], 30], [[1, 2, 3, 4, 5, 6, 7], 3]],
)
_r = rnd(9408)
p["tests"].append([sorted(_r.randint(0, 2 ** 30 - 1) for _ in range(3500)), 30])
p["tests"].append([sorted(_r.randint(0, 2 ** 12 - 1) for _ in range(6000)), 12])


def b_maxxor(nums, bits):
    out = []
    for m in range(len(nums), 0, -1):
        x = 0
        for v in nums[:m]:
            x ^= v
        best = max(range(1 << bits), key=lambda k: (x ^ k, -k))
        out.append(best)
    return out


def g_maxxor(r):
    bits = r.randint(1, 5)
    return [sorted(r.randint(0, (1 << bits) - 1) for _ in range(r.randint(1, 8))), bits]


def v_maxxor(tests):
    for t in tests:
        a, b = t["args"]
        assert 1 <= len(a) <= 10000 and 1 <= b <= 30
        assert all(0 <= x < (1 << b) for x in a) and a == sorted(a)


CHECKS["max-xor-per-pop-query"] = (b_maxxor, g_maxxor, "exact")
VALIDATE["max-xor-per-pop-query"] = v_maxxor

# ---------------------------------------------------------------- 9. subarrays with more ones than zeros

p = add(
    id="count-subarrays-more-ones-than-zeros", title="Count Subarrays with More Ones Than Zeros", diff="Medium", topic=T, tier="extra",
    fn="countMoreOnes", params=[("bits", "int[]")], ret="int", cmp="exact",
    desc="<p>Given a binary array <code>bits</code> (each element is <code>0</code> or <code>1</code>), count the contiguous subarrays in which the number of <code>1</code>s is <strong>strictly greater</strong> than the number of <code>0</code>s.</p><pre>bits = [1, 0, 1]\nqualifying subarrays: [1] (first), [1] (last), [1, 0, 1]\nresult = 3</pre>",
    constraints=["1 &le; bits.length &le; 8,000", "bits[i] is 0 or 1", "The answer fits in a 32-bit integer"],
    hints=["Map each 1 to +1 and each 0 to -1. A subarray has more ones than zeros exactly when its mapped sum is positive.",
           "With prefix sums <code>P</code>, you need the number of pairs <code>i &lt; j</code> with <code>P[j] &gt; P[i]</code>. Counting them with a hash map and a sort or tree gives O(n log n) - but the prefix sum only changes by &plusmn;1 each step.",
           "Maintain <code>less</code>, the number of earlier prefixes smaller than the current prefix value. When the prefix goes up by one from <code>s</code>, add <code>count[s]</code> to <code>less</code>; when it goes down to <code>s-1</code>, subtract <code>count[s-1]</code>."],
    editorial=["After mapping 1 to +1 and 0 to -1 the problem asks for the number of pairs of prefix sums <code>P[i] &lt; P[j]</code> with <code>i &lt; j</code>. A naive count is O(n<sup>2</sup>), and a general counting structure (BIT or sorted list) gives O(n log n).",
               "Because consecutive prefix sums differ by exactly 1, we can maintain the number <code>less</code> of earlier prefix values that are strictly below the current value in O(1) per step. Going from value <code>s</code> to <code>s+1</code>, the earlier prefixes equal to <code>s</code> become 'less', so add <code>cnt[s]</code>; going from <code>s</code> to <code>s-1</code>, the earlier prefixes equal to <code>s-1</code> are no longer below, so subtract <code>cnt[s-1]</code>. After each step add <code>less</code> to the answer and increment <code>cnt</code> for the new value. The total is O(n) time and O(n) space."],
    time="O(n)", space="O(n)",
    solution='''def countMoreOnes(bits):
    cnt = {0: 1}
    s = 0
    less = 0
    total = 0
    for b in bits:
        if b:
            less += cnt.get(s, 0)
            s += 1
        else:
            s -= 1
            less -= cnt.get(s, 0)
        total += less
        cnt[s] = cnt.get(s, 0) + 1
    return total
''',
    tests=[[[1, 0, 1]], [[1, 1, 0, 0, 1]], [[1]], [[0]], [[0, 0, 0]], [[1, 1, 1, 1]], [[1, 0, 1, 0, 1, 0]], [[0, 1, 1, 0, 1, 1, 0]],
           [[1, 0]], [[0, 1]]],
)
_r = rnd(9409)
p["tests"].append([[_r.randint(0, 1) for _ in range(8000)]])
p["tests"].append([[1] * 8000])
p["tests"].append([[1 if _r.random() < 0.7 else 0 for _ in range(8000)]])
p["tests"].append([[0, 1] * 4000])


def b_moreones(bits):
    n = len(bits)
    c = 0
    for i in range(n):
        s = 0
        for j in range(i, n):
            s += 1 if bits[j] else -1
            if s > 0:
                c += 1
    return c


def v_moreones(tests):
    for t in tests:
        a = t["args"][0]
        assert 1 <= len(a) <= 8000 and all(x in (0, 1) for x in a)


CHECKS["count-subarrays-more-ones-than-zeros"] = (
    b_moreones, lambda r: [[r.randint(0, 1) for _ in range(r.randint(1, 12))]], "exact")
VALIDATE["count-subarrays-more-ones-than-zeros"] = v_moreones

# ---------------------------------------------------------------- 10. beautiful substrings

p = add(
    id="count-beautiful-substrings", title="Count Beautiful Substrings", diff="Hard", topic=T, tier="extra",
    fn="countBeautiful", params=[("s", "string"), ("k", "int")], ret="int", cmp="exact",
    desc="<p>You are given a lowercase string <code>s</code> and a positive integer <code>k</code>. The vowels are <code>a, e, i, o, u</code>; every other letter is a consonant.</p><p>A non-empty substring is <strong>beautiful</strong> if, with <code>v</code> vowels and <code>c</code> consonants in it, both conditions hold:</p><ul><li><code>v == c</code></li><li><code>(v * c) % k == 0</code></li></ul><p>Return the number of beautiful substrings of <code>s</code> (substrings at different positions are counted separately).</p><pre>s = \"baeyh\", k = 2\nbeautiful: \"baey\" (v=2, c=2) and \"aeyh\" (v=2, c=2); \"ba\" has v*c = 1, not divisible by 2\nresult = 2</pre>",
    constraints=["1 &le; s.length &le; 5,000", "1 &le; k &le; 1,000", "s consists of lowercase English letters"],
    hints=["Checking all substrings is O(n<sup>2</sup>) and may pass small cases. Start with the condition <code>v == c</code>: map vowels to +1, consonants to -1 and use prefix sums.",
           "Now the product condition: with <code>v == c == len / 2</code> it becomes <code>(len / 2)<sup>2</sup> % k == 0</code>, i.e. <code>len<sup>2</sup> % (4k) == 0</code>. This holds for all multiples of one fixed number <code>L</code>.",
           "Factorise <code>4k</code> as a product of <code>p<sup>e</sup></code>; then <code>L</code> is the product of <code>p<sup>ceil(e/2)</sup></code>. Count pairs of prefixes with the same <code>(balance, index % L)</code> using a hash map."],
    editorial=["Map each vowel to +1 and each consonant to -1; a substring has <code>v == c</code> iff its prefix balances at the two ends are equal. Then <code>len = 2v</code>, and the second condition <code>v<sup>2</sup> % k == 0</code> is the same as <code>len<sup>2</sup> % (4k) == 0</code>.",
               "For a prime power <code>p<sup>e</sup></code> dividing <code>4k</code>, <code>len<sup>2</sup></code> is divisible by it iff <code>len</code> is divisible by <code>p<sup>ceil(e/2)</sup></code>. So <code>len<sup>2</sup> % 4k == 0</code> iff <code>len % L == 0</code>, where <code>L</code> is the product of those prime powers. Two prefix positions <code>i &lt; j</code> then delimit a beautiful substring iff their balances are equal and <code>j &equiv; i (mod L)</code> (so <code>j - i</code> is a multiple of <code>L</code>; the length is automatically even because the balance is zero).",
               "Scan the string keeping a dictionary from <code>(balance, index mod L)</code> to the number of earlier prefixes with that key (the empty prefix is index 0 with balance 0). Each new prefix adds the stored count to the answer. Computing <code>L</code> takes O(sqrt(k)) and the scan is O(n) time and space; the brute-force alternative is O(n<sup>2</sup>)."],
    time="O(n + sqrt(k))", space="O(n)",
    solution='''def countBeautiful(s, k):
    m = 4 * k
    L = 1
    p = 2
    while p * p <= m:
        if m % p == 0:
            e = 0
            while m % p == 0:
                m //= p
                e += 1
            L *= p ** ((e + 1) // 2)
        p += 1
    if m > 1:
        L *= m
    cnt = {(0, 0): 1}
    bal = 0
    total = 0
    for i, ch in enumerate(s, 1):
        bal += 1 if ch in "aeiou" else -1
        key = (bal, i % L)
        total += cnt.get(key, 0)
        cnt[key] = cnt.get(key, 0) + 1
    return total
''',
    tests=[["baeyh", 2], ["abba", 1], ["bcdf", 1], ["a", 1], ["ab", 1], ["ab", 2], ["aabb", 4], ["aebc", 8],
           ["abababab", 4], ["aeiouxyzwvbcdfgh", 16], ["uuuuuuuu", 1], ["bcbcbcbc", 3]],
)
_r = rnd(9410)
p["tests"].append(["".join(_r.choice("abcdefghijklmnopqrstuvwxyz") for _ in range(5000)), 1])
p["tests"].append(["".join(_r.choice("aeiobcdf") for _ in range(5000)), 360])
p["tests"].append(["ab" * 2500, 1000])
p["tests"].append(["".join(_r.choice("ab") for _ in range(5000)), 7])


def b_beautiful(s, k):
    n = len(s)
    c = 0
    for i in range(n):
        v = 0
        cons = 0
        for j in range(i, n):
            if s[j] in "aeiou":
                v += 1
            else:
                cons += 1
            if v == cons and (v * cons) % k == 0:
                c += 1
    return c


def v_beautiful(tests):
    for t in tests:
        s, k = t["args"]
        assert 1 <= len(s) <= 5000 and 1 <= k <= 1000
        assert s.isalpha() and s.islower() and s.isascii()
    assert any(t["expected"] == 0 for t in tests) and any(t["expected"] > 100 for t in tests)


CHECKS["count-beautiful-substrings"] = (
    b_beautiful, lambda r: ["".join(r.choice("aebcd") for _ in range(r.randint(1, 16))), r.randint(1, 36)], "exact")
VALIDATE["count-beautiful-substrings"] = v_beautiful

# ---------------------------------------------------------------- 11. sum of all subarray XORs

p = add(
    id="sum-of-all-subarray-xors", title="Sum of All Subarray XORs", diff="Hard", topic=T, tier="extra",
    fn="sumSubarrayXors", params=[("nums", "int[]")], ret="int", cmp="exact",
    desc="<p>For every non-empty contiguous subarray of <code>nums</code>, compute the bitwise XOR of its elements. Return the <strong>sum</strong> of all these XOR values, modulo <code>1,000,000,007</code>.</p><pre>nums = [1, 2, 3]\nsubarray XORs: 1, 2, 3, 1^2 = 3, 2^3 = 1, 1^2^3 = 0\nsum = 10\nresult = 10</pre>",
    constraints=["1 &le; nums.length &le; 8,000", "0 &le; nums[i] &le; 10<sup>9</sup>"],
    hints=["There are n(n+1)/2 subarrays, so listing them is too slow for the largest inputs. Write each subarray XOR with prefix XORs.",
           "The XOR of the block between prefix positions <code>i &lt; j</code> is <code>P[i] ^ P[j]</code>, so you need the sum of <code>P[i] ^ P[j]</code> over all pairs of the <code>n + 1</code> prefix values.",
           "XOR works bit by bit. For each bit position, if <code>c</code> of the prefix values have that bit set, exactly <code>c * (n + 1 - c)</code> pairs differ in that bit, contributing <code>2<sup>bit</sup></code> each."],
    editorial=["Let <code>P[0] = 0</code> and <code>P[i]</code> the XOR of the first <code>i</code> elements. The XOR of the subarray occupying positions <code>i..j-1</code> is <code>P[i] ^ P[j]</code>, so the requested sum equals the sum of <code>P[i] ^ P[j]</code> over all unordered pairs of the <code>n + 1</code> prefix values.",
               "The XOR of two numbers has bit <code>b</code> set iff exactly one of them has it. If <code>c</code> prefix values have bit <code>b</code> set and <code>n + 1 - c</code> do not, then <code>c * (n + 1 - c)</code> pairs contribute <code>2<sup>b</sup></code>. Summing over the 30 relevant bits (values up to 10<sup>9</sup> fit in 30 bits) gives the answer modulo 10<sup>9</sup> + 7. This is O(30 n) time and O(n) space, compared with O(n<sup>2</sup>) for pairwise XORs."],
    time="O(n log V)", space="O(n)",
    solution='''def sumSubarrayXors(nums):
    MOD = 10**9 + 7
    px = [0]
    for x in nums:
        px.append(px[-1] ^ x)
    m = len(px)
    total = 0
    for b in range(30):
        c = 0
        for v in px:
            c += (v >> b) & 1
        total += c * (m - c) * (1 << b)
    return total % MOD
''',
    tests=[[[1, 2, 3]], [[5]], [[0]], [[7, 7]], [[1, 1, 1, 1]], [[4, 8, 12]], [[1000000000]], [[1000000000, 1000000000, 1]],
           [[0, 0, 0, 0, 0]], [[3, 5, 6, 9, 10]]],
)
_r = rnd(9411)
p["tests"].append([[_r.randint(0, 10 ** 9) for _ in range(3500)]])
p["tests"].append([[_r.randint(0, 1000) for _ in range(6000)]])
p["tests"].append([[10 ** 9 if i % 2 else 0 for i in range(3000)]])


def b_sumxors(nums):
    n = len(nums)
    t = 0
    for i in range(n):
        x = 0
        for j in range(i, n):
            x ^= nums[j]
            t += x
    return t % MOD


def v_sumxors(tests):
    for t in tests:
        a = t["args"][0]
        assert 1 <= len(a) <= 8000 and all(0 <= x <= 10 ** 9 for x in a)
        assert 0 <= t["expected"] < MOD
    # make sure the modulus actually matters in at least one test
    assert any(len(t["args"][0]) >= 1000 for t in tests)


CHECKS["sum-of-all-subarray-xors"] = (
    b_sumxors, lambda r: [[r.randint(0, 10 ** 9) for _ in range(r.randint(1, 10))]], "exact")
VALIDATE["sum-of-all-subarray-xors"] = v_sumxors
