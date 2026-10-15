"""Problems: binary search on the answer, k-th element and pair problems. See data/lib.py for the registry."""
from math import gcd

from lib import add, rnd, CHECKS, VALIDATE, gen_arr  # noqa: F401

INT_MIN, INT_MAX = -(2 ** 31), 2 ** 31 - 1
TOPIC = "Binary Search"
MOD = 10 ** 9 + 7


def _inc(r, n, lo, hi):
    """Strictly increasing list of n distinct integers from [lo, hi]."""
    return sorted(r.sample(range(lo, hi + 1), n))


def _primes(limit):
    sieve = [True] * (limit + 1)
    sieve[0] = sieve[1] = False
    for i in range(2, int(limit ** 0.5) + 1):
        if sieve[i]:
            for j in range(i * i, limit + 1, i):
                sieve[j] = False
    return [i for i, ok in enumerate(sieve) if ok]


# ---------------------------------------------------------------- EASY

p = add(
    id="kth-missing-positive-number", title="Kth Missing Positive Number", diff="Easy", topic=TOPIC, tier="common",
    fn="kthMissing", params=[("nums", "int[]"), ("k", "int")], ret="int", cmp="exact",
    desc="<p>The array <code>nums</code> holds positive integers in strictly increasing order. Imagine writing down the positive integers <code>1, 2, 3, ...</code> and crossing out every value that occurs in <code>nums</code>. Return the <code>k</code>-th integer that is <em>not</em> crossed out.</p><p>Example: for <code>nums = [2, 3, 4, 7, 11]</code> the missing positive integers are <code>1, 5, 6, 8, 9, 10, 12, ...</code>, so for <code>k = 5</code> the answer is <code>9</code>. A solution faster than counting one integer at a time exists.</p>",
    constraints=["1 &le; nums.length &le; 10,000", "1 &le; nums[0] &lt; nums[1] &lt; ... &le; 10<sup>9</sup>", "1 &le; k &le; 10<sup>9</sup>"],
    hints=["Walking through the positive integers one by one and skipping those in the array works when <code>k</code> is small, but <code>k</code> can be a billion.",
           "At index <code>i</code> there are exactly <code>nums[i] - (i + 1)</code> missing positive integers smaller than <code>nums[i]</code>. This count never decreases as <code>i</code> grows.",
           "Binary search the first index <code>idx</code> whose missing count is at least <code>k</code> (use <code>n</code> if there is none). The answer is then <code>idx + k</code>."],
    editorial=["Let <code>miss(i) = nums[i] - i - 1</code>, the number of absent positive integers below <code>nums[i]</code>. Because the array is strictly increasing, <code>miss</code> is non-decreasing, so it can be binary searched.",
               "Find the smallest index <code>idx</code> with <code>miss(idx) &ge; k</code>, or <code>n</code> if no index qualifies. Then exactly <code>idx</code> array elements lie below the answer, so the answer is the <code>k</code>-th integer after skipping those <code>idx</code> values: <code>idx + k</code>. This also covers the case where the answer lies beyond the last element.",
               "Time is O(log n) after reading the input, space O(1). The answer is at most <code>10<sup>9</sup> + 10<sup>4</sup></code>, which fits in a 32-bit integer."],
    time="O(log n)", space="O(1)",
    solution='''def kthMissing(nums, k):
    lo, hi = 0, len(nums)
    while lo < hi:
        mid = (lo + hi) // 2
        if nums[mid] - mid - 1 >= k:
            hi = mid
        else:
            lo = mid + 1
    return lo + k
''',
    tests=[[[2, 3, 4, 7, 11], 5], [[1, 2, 3, 4], 2], [[1], 1], [[2], 1], [[5, 6, 7], 4], [[5, 6, 7], 5], [[1, 2, 3], 10 ** 9],
           [[10 ** 9], 10 ** 9], [[10 ** 9], 10 ** 9 - 1], [[1, 3, 5, 7, 9], 3], [[3, 10], 2], [[1, 2, 4, 8, 16, 32], 20]],
)
_r = rnd(9501)
_a = _inc(_r, 3000, 1, 50000)
p["tests"].append([_a, 1])
p["tests"].append([_a, 35000])
p["tests"].append([_a, 46000])
_a = _inc(_r, 1500, 1, 10 ** 9)
p["tests"].append([_a, 10 ** 9])
p["tests"].append([_a, 123456789])


def b_kmiss(nums, k):
    have = set(nums)
    x = 0
    while k:
        x += 1
        if x not in have:
            k -= 1
    return x


def g_kmiss(r):
    n = r.randint(1, 7)
    return [_inc(r, n, 1, 20), r.randint(1, 25)]


def v_kmiss(tests):
    for t in tests:
        nums, k = t["args"]
        assert 1 <= len(nums) <= 10000 and 1 <= k <= 10 ** 9
        assert 1 <= nums[0] and nums[-1] <= 10 ** 9
        assert all(nums[i] < nums[i + 1] for i in range(len(nums) - 1))


CHECKS["kth-missing-positive-number"] = (b_kmiss, g_kmiss, "exact")
VALIDATE["kth-missing-positive-number"] = v_kmiss

p = add(
    id="kth-positive-not-divisible", title="Kth Positive Integer Not Divisible by D", diff="Easy", topic=TOPIC, tier="extra",
    fn="kthNotDivisible", params=[("k", "int"), ("d", "int")], ret="int", cmp="exact",
    desc="<p>List the positive integers <code>1, 2, 3, ...</code> and remove every multiple of <code>d</code>. Return the <code>k</code>-th integer that remains (1-indexed).</p><p>Example: for <code>d = 3</code> the remaining integers are <code>1, 2, 4, 5, 7, 8, ...</code>, so <code>k = 5</code> gives <code>7</code>.</p>",
    constraints=["1 &le; k &le; 10<sup>9</sup>", "2 &le; d &le; 10<sup>9</sup>"],
    hints=["Looping over the integers works for small <code>k</code>, but <code>k</code> can be a billion and the answer can be nearly 2&middot;10<sup>9</sup>.",
           "For a candidate value <code>x</code>, how many integers in <code>1..x</code> are <em>not</em> multiples of <code>d</code>? Multiples of <code>d</code> in that range are <code>x // d</code>.",
           "The count <code>x - x // d</code> never decreases as <code>x</code> grows. Binary search the smallest <code>x</code> whose count is at least <code>k</code>; the upper bound <code>2k</code> is always enough since <code>d &ge; 2</code>."],
    editorial=["Define <code>good(x) = x - x // d</code>, the number of integers in <code>1..x</code> that survive. It is non-decreasing in <code>x</code>, and it goes up by one exactly at the surviving integers. Therefore the smallest <code>x</code> with <code>good(x) &ge; k</code> is the <code>k</code>-th survivor.",
               "Since at least half of all integers survive when <code>d &ge; 2</code>, <code>good(2k) &ge; k</code> and the answer lies in <code>[k, 2k]</code>. Binary search over that range takes about 31 steps. The same count function appears in many harder problems (such as the next-number-divisible-by-A-or-B family), which is why binary search is the reusable technique here.",
               "There is also a closed form: every block of <code>d - 1</code> survivors is followed by one removed multiple, so the answer is <code>k + (k - 1) // (d - 1)</code>. Both approaches are O(1) memory; the search is O(log k), the formula O(1)."],
    time="O(log k)", space="O(1)",
    solution='''def kthNotDivisible(k, d):
    lo, hi = k, 2 * k
    while lo < hi:
        mid = (lo + hi) // 2
        if mid - mid // d >= k:
            hi = mid
        else:
            lo = mid + 1
    return lo
''',
    tests=[[5, 3], [1, 2], [2, 2], [3, 2], [4, 5], [5, 5], [6, 7], [7, 7], [1, 10 ** 9], [10 ** 9, 2], [10 ** 9, 10 ** 9],
           [10 ** 9 - 1, 10 ** 9], [123456789, 3], [999999937, 1000]],
)


def b_ndiv(k, d):
    x = 0
    while k:
        x += 1
        if x % d:
            k -= 1
    return x


def g_ndiv(r):
    return [r.randint(1, 30), r.randint(2, 9)]


def v_ndiv(tests):
    for t in tests:
        k, d = t["args"]
        assert 1 <= k <= 10 ** 9 and 2 <= d <= 10 ** 9
        assert t["expected"] % d != 0


CHECKS["kth-positive-not-divisible"] = (b_ndiv, g_ndiv, "exact")
VALIDATE["kth-positive-not-divisible"] = v_ndiv


# ---------------------------------------------------------------- MEDIUM

p = add(
    id="nth-magical-number", title="Nth Magical Number", diff="Medium", topic=TOPIC, tier="common",
    fn="nthMagical", params=[("n", "int"), ("a", "int"), ("b", "int")], ret="int", cmp="exact",
    desc="<p>A positive integer is <em>magical</em> if it is divisible by <code>a</code> or by <code>b</code> (or both). Return the <code>n</code>-th smallest magical number. The value can be huge, so return it modulo <code>10<sup>9</sup> + 7</code>.</p><p>Example: for <code>n = 4, a = 2, b = 3</code> the magical numbers are <code>2, 3, 4, 6, 8, ...</code>, so the answer is <code>6</code>.</p>",
    constraints=["1 &le; n &le; 10<sup>9</sup>", "2 &le; a, b &le; 40,000", "Return the answer modulo 1,000,000,007 (the true value is not reduced while searching)"],
    hints=["With <code>n</code> up to a billion you cannot step through the numbers. Think about how many magical numbers are at most a given <code>x</code>.",
           "Multiples of <code>a</code> up to <code>x</code>: <code>x // a</code>. Multiples of <code>b</code>: <code>x // b</code>. Numbers divisible by both were counted twice; they are the multiples of <code>lcm(a, b)</code>.",
           "<code>count(x) = x // a + x // b - x // lcm</code> is non-decreasing. Binary search the smallest <code>x</code> in <code>[1, n * min(a, b)]</code> with <code>count(x) &ge; n</code>, then take it modulo 10<sup>9</sup> + 7 only at the very end."],
    editorial=["By inclusion-exclusion, the number of magical integers in <code>1..x</code> is <code>x // a + x // b - x // L</code> with <code>L = lcm(a, b) = a * b / gcd(a, b)</code>. This count is non-decreasing in <code>x</code> and increases by one exactly at magical numbers, so the smallest <code>x</code> with count at least <code>n</code> is the <code>n</code>-th magical number.",
               "An upper bound is <code>n * min(a, b)</code>, since the first <code>n</code> multiples of the smaller number already give <code>n</code> magical values. That is at most about 4&middot;10<sup>13</sup>, so about 46 halvings suffice. The search must run on the true value; reducing modulo before comparing would break the monotonicity. Apply the modulus once, to the final answer.",
               "Time O(log(n * min(a, b))), space O(1). Alternatively, the pattern of magical numbers repeats every <code>L</code>, so you can also work out the answer by a direct period computation, but the binary search is the technique that generalizes (three divisors, kth in a union of arithmetic sequences)."],
    time="O(log(n * min(a, b)))", space="O(1)",
    solution='''def nthMagical(n, a, b):
    from math import gcd
    lcm = a // gcd(a, b) * b

    def count(x):
        return x // a + x // b - x // lcm

    lo, hi = 1, n * min(a, b)
    while lo < hi:
        mid = (lo + hi) // 2
        if count(mid) >= n:
            hi = mid
        else:
            lo = mid + 1
    return lo % (10 ** 9 + 7)
''',
    tests=[[1, 2, 3], [4, 2, 3], [5, 2, 4], [3, 6, 4], [1, 40000, 39999], [10, 3, 3], [7, 2, 7], [1000, 2, 3], [10 ** 9, 2, 3],
           [10 ** 9, 40000, 39999], [10 ** 9, 40000, 40000], [999999999, 12345, 6789], [10 ** 9, 2, 40000], [123456789, 7, 11]],
)


def b_magic(n, a, b):
    x = 0
    while n:
        x += 1
        if x % a == 0 or x % b == 0:
            n -= 1
    return x % MOD


def g_magic(r):
    return [r.randint(1, 40), r.randint(2, 9), r.randint(2, 9)]


def v_magic(tests):
    for t in tests:
        n, a, b = t["args"]
        assert 1 <= n <= 10 ** 9 and 2 <= a <= 40000 and 2 <= b <= 40000
        assert 0 <= t["expected"] < MOD
    assert any(t["args"][0] >= 10 ** 9 - 1 for t in tests)


CHECKS["nth-magical-number"] = (b_magic, g_magic, "exact")
VALIDATE["nth-magical-number"] = v_magic

p = add(
    id="kth-term-across-arithmetic-sequences", title="Kth Term Across Arithmetic Sequences", diff="Medium", topic=TOPIC, tier="extra",
    fn="kthTermAcross", params=[("seqs", "int[][]"), ("k", "int")], ret="int", cmp="exact",
    desc="<p>Each element <code>[s, d]</code> of <code>seqs</code> describes an infinite arithmetic sequence <code>s, s + d, s + 2d, ...</code>. Pour the terms of <em>all</em> sequences into one sorted list. A value that occurs in several sequences, or twice in one, appears in the list once for each occurrence. Return the <code>k</code>-th term (1-indexed) of this combined list.</p><p>Example: for <code>seqs = [[1, 3], [2, 5]]</code> the sequences are <code>1, 4, 7, 10, ...</code> and <code>2, 7, 12, ...</code>, the combined list begins <code>1, 2, 4, 7, 7, 10, 12, ...</code>, so <code>k = 5</code> gives <code>7</code>. The test data guarantees that the answer does not exceed <code>2 * 10<sup>9</sup></code>.</p>",
    constraints=["1 &le; seqs.length &le; 1,000", "1 &le; s &le; 10<sup>9</sup> and 1 &le; d &le; 10<sup>9</sup> for every sequence", "1 &le; k &le; 10<sup>9</sup>", "The answer is at most 2,000,000,000"],
    hints=["With <code>k</code> up to a billion you cannot generate terms one by one, and a heap over the sequences would need k steps.",
           "Fix a value <code>x</code>. A sequence <code>[s, d]</code> has exactly <code>(x - s) // d + 1</code> terms that are at most <code>x</code> when <code>x &ge; s</code>, and none otherwise.",
           "Summing over all sequences gives <code>count(x)</code>, which is non-decreasing. Binary search the smallest <code>x</code> in <code>[1, 2*10<sup>9</sup>]</code> with <code>count(x) &ge; k</code>."],
    editorial=["Let <code>count(x)</code> be the number of terms, over all sequences and counted with multiplicity, that are at most <code>x</code>. A sequence <code>[s, d]</code> contributes <code>(x - s) // d + 1</code> if <code>x &ge; s</code> and 0 otherwise. The sum is non-decreasing in <code>x</code>, and it increases exactly at values that are terms of some sequence (by the number of sequences that have that term).",
               "Therefore the smallest <code>x</code> with <code>count(x) &ge; k</code> is the k-th term of the combined list: at <code>x - 1</code> fewer than <code>k</code> terms are at most <code>x - 1</code>, and at <code>x</code> at least <code>k</code> are, so the k-th term equals <code>x</code>. The statement guarantees <code>x &le; 2&middot;10<sup>9</sup></code>, which gives about 31 iterations.",
               "Time is O(m log R) for m sequences and value range R, space O(1). This generalizes the nth magical number problem (two sequences <code>[a, a]</code> and <code>[b, b]</code> with duplicates counted once, handled by inclusion-exclusion). Here duplicates are counted with multiplicity, so no inclusion-exclusion is needed."],
    time="O(m log R)", space="O(1)",
    solution='''def kthTermAcross(seqs, k):
    def count(x):
        total = 0
        for s, d in seqs:
            if x >= s:
                total += (x - s) // d + 1
        return total

    lo, hi = 1, 2 * 10 ** 9
    while lo < hi:
        mid = (lo + hi) // 2
        if count(mid) >= k:
            hi = mid
        else:
            lo = mid + 1
    return lo
''',
    tests=[[[[1, 3], [2, 5]], 5], [[[1, 3], [2, 5]], 1], [[[1, 3], [2, 5]], 2], [[[7, 1]], 1], [[[7, 1]], 1000], [[[5, 10 ** 9]], 2],
           [[[10 ** 9, 10 ** 9]], 2], [[[3, 3], [3, 3], [3, 3]], 7], [[[1, 1], [1, 1]], 10 ** 9], [[[10 ** 9, 1], [2, 2]], 600000000],
           [[[1, 2], [2, 2]], 10 ** 9], [[[4, 6], [9, 4], [20, 1]], 15]],
)
_r = rnd(9503)


def _count_terms(seqs, x):
    return sum((x - s) // d + 1 for s, d in seqs if x >= s)


_sq = [[_r.randint(1, 10 ** 6), _r.randint(1, 3000)] for _ in range(1000)]
p["tests"].append([_sq, 1])
p["tests"].append([_sq, 10 ** 9])
p["tests"].append([_sq, 123456789])
_sq = [[_r.randint(1, 10 ** 9), _r.randint(1, 10 ** 9)] for _ in range(1000)]
_tot = _count_terms(_sq, 2 * 10 ** 9)
p["tests"].append([_sq, _tot])
p["tests"].append([_sq, _tot // 2])


def b_terms(seqs, k):
    terms = []
    for s, d in seqs:
        terms.extend(s + i * d for i in range(k))
    return sorted(terms)[k - 1]


def g_terms(r):
    return [[[r.randint(1, 12), r.randint(1, 7)] for _ in range(r.randint(1, 4))], r.randint(1, 25)]


def v_terms(tests):
    for t in tests:
        seqs, k = t["args"]
        assert 1 <= len(seqs) <= 1000 and 1 <= k <= 10 ** 9
        assert all(1 <= s <= 10 ** 9 and 1 <= d <= 10 ** 9 for s, d in seqs)
        assert 1 <= t["expected"] <= 2 * 10 ** 9
        assert _count_terms(seqs, t["expected"]) >= k > _count_terms(seqs, t["expected"] - 1)


CHECKS["kth-term-across-arithmetic-sequences"] = (b_terms, g_terms, "exact")
VALIDATE["kth-term-across-arithmetic-sequences"] = v_terms

p = add(
    id="kth-uncovered-integer", title="Kth Uncovered Integer", diff="Medium", topic=TOPIC, tier="extra",
    fn="kthUncovered", params=[("intervals", "int[][]"), ("k", "int")], ret="int", cmp="exact",
    desc="<p>Each element <code>[l, r]</code> of <code>intervals</code> covers all integers from <code>l</code> to <code>r</code> inclusive. The intervals are sorted by <code>l</code> and are pairwise disjoint: every interval starts strictly after the previous one ends (<code>l<sub>i+1</sub> &gt; r<sub>i</sub></code>). They may be adjacent, such as <code>[3, 3]</code> and <code>[4, 4]</code>.</p><p>Return the <code>k</code>-th smallest positive integer that is <em>not</em> covered by any interval.</p><p>Example: for <code>intervals = [[2, 3], [5, 5]]</code> the uncovered positive integers are <code>1, 4, 6, 7, ...</code>, so <code>k = 3</code> gives <code>6</code>.</p>",
    constraints=["1 &le; intervals.length &le; 10,000", "1 &le; l<sub>i</sub> &le; r<sub>i</sub> &le; 10<sup>9</sup> and l<sub>i+1</sub> &gt; r<sub>i</sub>", "1 &le; k &le; 10<sup>9</sup>"],
    hints=["Expanding every interval into its integers is impossible: an interval can contain a billion values. Work with counts.",
           "Before the start <code>l<sub>i</sub></code> of interval <code>i</code>, exactly <code>l<sub>i</sub> - 1 - (covered integers of earlier intervals)</code> positive integers are uncovered. Build this for every interval.",
           "That uncovered-before count never decreases with <code>i</code>. Binary search the first interval whose count is at least <code>k</code> (or none). Then the answer is <code>k</code> plus the total length of all intervals before it."],
    editorial=["Let <code>cov<sub>i</sub></code> be the total length of intervals <code>0..i-1</code>. Just before interval <code>i</code> begins, the integers <code>1..l<sub>i</sub> - 1</code> are free except for the <code>cov<sub>i</sub></code> covered ones, so <code>free<sub>i</sub> = l<sub>i</sub> - 1 - cov<sub>i</sub></code> positive integers are uncovered. Since intervals are disjoint and sorted, <code>free</code> is non-decreasing.",
               "Find the first interval index <code>j</code> with <code>free<sub>j</sub> &ge; k</code>, or <code>j = n</code> if every interval starts too early. All intervals before <code>j</code> lie entirely below the answer, and none of the later ones can interfere (the answer is below <code>l<sub>j</sub></code>), so the answer is the <code>k</code>-th uncovered integer after skipping <code>cov<sub>j</sub></code> covered ones: <code>k + cov<sub>j</sub></code>.",
               "Building the prefix arrays is O(n) and the search O(log n). The answer is at most <code>k</code> plus the covered total, i.e. at most 2&middot;10<sup>9</sup>, which fits in a signed 32-bit integer."],
    time="O(n)", space="O(n)",
    solution='''def kthUncovered(intervals, k):
    from bisect import bisect_left
    free = []
    cov = [0]
    for l, r in intervals:
        free.append(l - 1 - cov[-1])
        cov.append(cov[-1] + r - l + 1)
    j = bisect_left(free, k)
    return k + cov[j]
''',
    tests=[[[[2, 3], [5, 5]], 3], [[[2, 3], [5, 5]], 1], [[[2, 3], [5, 5]], 2], [[[1, 1]], 1], [[[1, 10]], 5], [[[5, 8]], 4], [[[5, 8]], 5],
           [[[1, 2], [4, 5], [7, 8]], 3], [[[3, 3], [4, 4], [6, 9]], 3], [[[1, 10 ** 9]], 10 ** 9], [[[10 ** 9, 10 ** 9]], 10 ** 9],
           [[[2, 10 ** 9 - 1]], 2], [[[1, 5], [10, 20], [30, 40]], 7]],
)
_r = rnd(9503)


def _intervals(r, n, gap_max, len_max):
    out, pos = [], r.randint(1, 3)
    for _ in range(n):
        ln = r.randint(1, len_max)
        out.append([pos, pos + ln - 1])
        pos += ln + r.randint(1, gap_max)
    return out


_iv = _intervals(_r, 2000, 5, 50)
_free_total = _iv[-1][0] - 1 - sum(b - a + 1 for a, b in _iv[:-1])
p["tests"].append([_iv, 1])
p["tests"].append([_iv, _free_total + 12345])
_iv = _intervals(_r, 1500, 100000, 100000)
p["tests"].append([_iv, 777777])
p["tests"].append([_iv, 2 * 10 ** 8])


def b_unc(intervals, k):
    covered = set()
    for l, r in intervals:
        covered.update(range(l, r + 1))
    x = 0
    while k:
        x += 1
        if x not in covered:
            k -= 1
    return x


def g_unc(r):
    n = r.randint(1, 5)
    return [_intervals(r, n, 3, 4), r.randint(1, 25)]


def v_unc(tests):
    for t in tests:
        iv, k = t["args"]
        assert 1 <= len(iv) <= 10000 and 1 <= k <= 10 ** 9
        for i, (l, r) in enumerate(iv):
            assert 1 <= l <= r <= 10 ** 9
            if i:
                assert l > iv[i - 1][1]


CHECKS["kth-uncovered-integer"] = (b_unc, g_unc, "exact")
VALIDATE["kth-uncovered-integer"] = v_unc

p = add(
    id="kth-smallest-subarray-sum", title="Kth Smallest Subarray Sum", diff="Medium", topic=TOPIC, tier="common",
    fn="kthSubarraySum", params=[("nums", "int[]"), ("k", "int")], ret="int", cmp="exact",
    desc="<p>The array <code>nums</code> contains positive integers. Every non-empty contiguous subarray has a sum; subarrays at different positions are counted separately even when their sums are equal. Sort all <code>n(n+1)/2</code> sums in non-decreasing order and return the <code>k</code>-th one (1-indexed).</p><p>Example: for <code>nums = [2, 1, 3]</code> the subarray sums are <code>2, 1, 3, 3, 4, 6</code>, sorted <code>1, 2, 3, 3, 4, 6</code>, so <code>k = 4</code> gives <code>3</code>.</p>",
    constraints=["1 &le; nums.length &le; 5,000", "1 &le; nums[i] &le; 10,000", "1 &le; k &le; n(n+1)/2"],
    hints=["Generating all O(n<sup>2</sup>) sums and sorting them is too much memory for n = 5000 in many settings. Think about the answer as a value.",
           "For a limit <code>S</code>, how many subarrays have sum at most <code>S</code>? All numbers are positive, so a sliding window with two pointers counts them in O(n).",
           "Binary search the smallest <code>S</code> between <code>min(nums)</code> and <code>sum(nums)</code> with at least <code>k</code> subarrays of sum &le; <code>S</code>."],
    editorial=["Because all elements are positive, extending a subarray always increases its sum, which makes the counting step easy. For a fixed limit <code>S</code>, sweep <code>right</code> across the array, maintaining the window sum; shrink from the left while the sum exceeds <code>S</code>. Every start index in <code>[left, right]</code> gives a valid subarray ending at <code>right</code>, so add <code>right - left + 1</code>. That is <code>count(S)</code> in O(n).",
               "<code>count(S)</code> is non-decreasing in <code>S</code>. The k-th smallest sum is the smallest <code>S</code> with <code>count(S) &ge; k</code>, and it is an actual subarray sum because <code>count</code> only increases at sums that exist. The search range is <code>[min(nums), sum(nums)]</code>, at most about 5&middot;10<sup>7</sup>, so around 26 iterations.",
               "Total time is O(n log(sum)) and space is O(1). Positivity is essential: with negative numbers the window sum is not monotone and the two-pointer count is invalid."],
    time="O(n log S)", space="O(1)",
    solution='''def kthSubarraySum(nums, k):
    def count(limit):
        total = left = window = 0
        for right, x in enumerate(nums):
            window += x
            while window > limit:
                window -= nums[left]
                left += 1
            total += right - left + 1
        return total

    lo, hi = min(nums), sum(nums)
    while lo < hi:
        mid = (lo + hi) // 2
        if count(mid) >= k:
            hi = mid
        else:
            lo = mid + 1
    return lo
''',
    tests=[[[2, 1, 3], 4], [[2, 1, 3], 1], [[2, 1, 3], 6], [[5], 1], [[1, 1, 1, 1], 5], [[1, 1, 1, 1], 10], [[4, 1, 1, 2, 1, 3], 8],
           [[10000, 10000], 2], [[10000, 10000], 3], [[3, 3, 3], 3], [[1, 2, 3, 4, 5], 9], [[9, 1], 2]],
)
_r = rnd(9504)
_a = [_r.randint(1, 10000) for _ in range(3000)]
p["tests"].append([_a, 1])
p["tests"].append([_a, 4501500])
p["tests"].append([_a, 2300000])
p["tests"].append([_a, 987654])
_a = [_r.randint(1, 5) for _ in range(3000)]
p["tests"].append([_a, 3500000])
p["tests"].append([[10000] * 3000, 4501500])


def b_ksub(nums, k):
    sums = []
    for i in range(len(nums)):
        s = 0
        for j in range(i, len(nums)):
            s += nums[j]
            sums.append(s)
    return sorted(sums)[k - 1]


def g_ksub(r):
    n = r.randint(1, 8)
    return [[r.randint(1, 6) for _ in range(n)], r.randint(1, n * (n + 1) // 2)]


def v_ksub(tests):
    for t in tests:
        nums, k = t["args"]
        n = len(nums)
        assert 1 <= n <= 5000 and all(1 <= x <= 10000 for x in nums)
        assert 1 <= k <= n * (n + 1) // 2


CHECKS["kth-smallest-subarray-sum"] = (b_ksub, g_ksub, "exact")
VALIDATE["kth-smallest-subarray-sum"] = v_ksub

p = add(
    id="kth-smallest-cross-array-distance", title="Kth Smallest Distance Between Two Arrays", diff="Medium", topic=TOPIC, tier="extra",
    fn="kthCrossDistance", params=[("a", "int[]"), ("b", "int[]"), ("k", "int")], ret="int", cmp="exact",
    desc="<p>Form every pair that takes one element from <code>a</code> and one from <code>b</code>; there are <code>a.length * b.length</code> such pairs. The <em>distance</em> of a pair is <code>|x - y|</code>. Pairs are counted separately even if they have equal distance.</p><p>Sort all pair distances in non-decreasing order and return the <code>k</code>-th one (1-indexed). The arrays are not sorted.</p><p>Example: for <code>a = [1, 5]</code>, <code>b = [2, 9]</code> the distances are <code>1, 8, 3, 4</code>, sorted <code>1, 3, 4, 8</code>, so <code>k = 3</code> gives <code>4</code>.</p>",
    constraints=["1 &le; a.length, b.length &le; 4,000", "-10<sup>9</sup> &le; a[i], b[j] &le; 10<sup>9</sup>", "1 &le; k &le; a.length * b.length"],
    hints=["With up to 16 million pairs, building and sorting all distances is wasteful. Search over the distance value instead.",
           "Sort <code>b</code>. For one element <code>x</code> of <code>a</code> and a limit <code>d</code>, the elements <code>y</code> with <code>|x - y| &le; d</code> form a contiguous block of the sorted <code>b</code>: those in <code>[x - d, x + d]</code>.",
           "Count that block with two binary searches (<code>bisect_right(b, x + d) - bisect_left(b, x - d)</code>), sum over <code>a</code>, and binary search the smallest <code>d</code> whose total is at least <code>k</code>."],
    editorial=["Let <code>count(d)</code> be the number of cross pairs with distance at most <code>d</code>. It is non-decreasing in <code>d</code>, and the smallest <code>d</code> with <code>count(d) &ge; k</code> is the k-th smallest distance (it is a real distance because the count only grows at values that occur).",
               "Sort <code>b</code> once. For each <code>x</code> in <code>a</code>, the partners within distance <code>d</code> are exactly the values of <code>b</code> in <code>[x - d, x + d]</code>, a contiguous range of the sorted array found with two binary searches. Summing gives <code>count(d)</code> in O(|a| log |b|).",
               "The distance range is <code>[0, max difference]</code>, which is at most 2&middot;10<sup>9</sup> and fits in a signed 32-bit integer; about 31 iterations are needed. Total time O((|a| + |b|) log |b| + |a| log |b| log R). Searching on the answer is the key idea; a heap over all pairs would cost O(k log) and is far slower for large <code>k</code>."],
    time="O(|a| log|b| log R)", space="O(|b|)",
    solution='''def kthCrossDistance(a, b, k):
    from bisect import bisect_left, bisect_right
    sb = sorted(b)
    hi = max(max(a) - sb[0], sb[-1] - min(a), 0)

    def count(d):
        return sum(bisect_right(sb, x + d) - bisect_left(sb, x - d) for x in a)

    lo = 0
    while lo < hi:
        mid = (lo + hi) // 2
        if count(mid) >= k:
            hi = mid
        else:
            lo = mid + 1
    return lo
''',
    tests=[[[1, 5], [2, 9], 3], [[1, 5], [2, 9], 1], [[1, 5], [2, 9], 4], [[7], [7], 1], [[0], [10 ** 9], 1], [[-10 ** 9], [10 ** 9], 1],
           [[3, 3, 3], [3, 3], 6], [[1, 2, 3], [10, 20], 4], [[5, 1, 9, 3], [4, 8, 2], 7], [[-5, 5], [-5, 5], 2], [[-5, 5], [-5, 5], 3],
           [[10 ** 9, -10 ** 9], [-10 ** 9, 10 ** 9], 4]],
)
_r = rnd(9505)
_a = [_r.randint(-10 ** 9, 10 ** 9) for _ in range(800)]
_b = [_r.randint(-10 ** 9, 10 ** 9) for _ in range(800)]
p["tests"].append([_a, _b, 1])
p["tests"].append([_a, _b, 640000])
p["tests"].append([_a, _b, 320000])
p["tests"].append([_a, _b, 123456])
_a = [_r.randint(0, 1000) for _ in range(1500)]
_b = [_r.randint(0, 1000) for _ in range(500)]
p["tests"].append([_a, _b, 750000])
p["tests"].append([_a, _b, 375000])


def b_cross(a, b, k):
    return sorted(abs(x - y) for x in a for y in b)[k - 1]


def g_cross(r):
    a = [r.randint(-12, 12) for _ in range(r.randint(1, 6))]
    b = [r.randint(-12, 12) for _ in range(r.randint(1, 6))]
    return [a, b, r.randint(1, len(a) * len(b))]


def v_cross(tests):
    for t in tests:
        a, b, k = t["args"]
        assert 1 <= len(a) <= 4000 and 1 <= len(b) <= 4000
        assert all(-10 ** 9 <= x <= 10 ** 9 for x in a + b)
        assert 1 <= k <= len(a) * len(b)


CHECKS["kth-smallest-cross-array-distance"] = (b_cross, g_cross, "exact")
VALIDATE["kth-smallest-cross-array-distance"] = v_cross

p = add(
    id="kth-element-of-two-sorted-arrays", title="Kth Element of Two Sorted Arrays", diff="Medium", topic=TOPIC, tier="common",
    fn="kthOfTwoSorted", params=[("a", "int[]"), ("b", "int[]"), ("k", "int")], ret="int", cmp="exact",
    desc="<p>The arrays <code>a</code> and <code>b</code> are each sorted in non-decreasing order (either may be empty, but not both). Imagine merging them into one sorted sequence of <code>a.length + b.length</code> values, keeping duplicates. Return the <code>k</code>-th value of that merged sequence (1-indexed), without actually building it.</p><p>Example: for <code>a = [1, 4, 7]</code>, <code>b = [2, 3, 9, 10]</code> the merged sequence is <code>1, 2, 3, 4, 7, 9, 10</code>, so <code>k = 4</code> gives <code>4</code>. Aim for O(log(min(a.length, b.length))) time.</p>",
    constraints=["0 &le; a.length, b.length &le; 5,000 and a.length + b.length &ge; 1", "-10<sup>9</sup> &le; a[i], b[j] &le; 10<sup>9</sup>", "Both arrays are sorted in non-decreasing order", "1 &le; k &le; a.length + b.length"],
    hints=["Merging with two pointers takes O(k). To be faster you must discard many elements at once.",
           "The k smallest values consist of some prefix of <code>a</code> with <code>i</code> elements and a prefix of <code>b</code> with <code>k - i</code> elements. Only <code>i</code> is unknown.",
           "A split is right when the last taken element of each array is not larger than the first untaken element of the other. If <code>a[i] &lt; b[k - i - 1]</code>, then <code>a[i]</code> must also be among the k smallest, so <code>i</code> is too small. Binary search <code>i</code>; the answer is the larger of the two last taken elements."],
    editorial=["Choose how many of the k smallest values come from <code>a</code>; call it <code>i</code>, so <code>j = k - i</code> come from <code>b</code>. The valid range is <code>max(0, k - |b|) &le; i &le; min(k, |a|)</code>. The split is correct exactly when <code>a[i-1] &le; b[j]</code> and <code>b[j-1] &le; a[i]</code> (missing elements count as infinity or minus infinity).",
               "If <code>a[i] &lt; b[j-1]</code>, then <code>a[i]</code> is smaller than a value we already took from <code>b</code>, so it belongs to the k smallest and we must take more from <code>a</code>: move the lower bound to <code>i + 1</code>. Otherwise the split is not too small and the upper bound moves to <code>i</code>. Swapping the arrays first so that <code>a</code> is the shorter one keeps the search to O(log min(|a|, |b|)).",
               "When the search ends the k smallest values are <code>a[0..i-1]</code> and <code>b[0..j-1]</code>, so the k-th is the larger of <code>a[i-1]</code> and <code>b[j-1]</code> (ignoring a side that contributes nothing). This is the building block of the classic median of two sorted arrays problem. Space is O(1)."],
    time="O(log min(m, n))", space="O(1)",
    solution='''def kthOfTwoSorted(a, b, k):
    if len(a) > len(b):
        a, b = b, a
    m, n = len(a), len(b)
    lo, hi = max(0, k - n), min(k, m)
    while lo < hi:
        i = (lo + hi) // 2
        j = k - i
        if a[i] < b[j - 1]:
            lo = i + 1
        else:
            hi = i
    i = lo
    j = k - i
    best = []
    if i > 0:
        best.append(a[i - 1])
    if j > 0:
        best.append(b[j - 1])
    return max(best)
''',
    tests=[[[1, 4, 7], [2, 3, 9, 10], 4], [[1, 4, 7], [2, 3, 9, 10], 1], [[1, 4, 7], [2, 3, 9, 10], 7], [[], [5], 1], [[5], [], 1], [[], [1, 2, 3, 4], 3],
           [[1, 2, 3, 4], [], 4], [[1, 2], [3, 4], 3], [[3, 4], [1, 2], 2], [[2, 2, 2], [2, 2], 4], [[-10 ** 9, 10 ** 9], [-10 ** 9, 10 ** 9], 2],
           [[-10 ** 9, 10 ** 9], [-10 ** 9, 10 ** 9], 3], [[1, 100], [2, 3, 4, 5, 6, 7], 5], [[1, 1, 1, 5], [1, 1, 5, 5], 6]],
)
_r = rnd(9502)
_a = sorted(_r.randint(-10 ** 9, 10 ** 9) for _ in range(1500))
_b = sorted(_r.randint(-10 ** 9, 10 ** 9) for _ in range(2000))
p["tests"].append([_a, _b, 1])
p["tests"].append([_a, _b, 3500])
p["tests"].append([_a, _b, 1750])
_a = sorted(_r.randint(0, 50) for _ in range(4000))
_b = sorted(_r.randint(0, 50) for _ in range(30))
p["tests"].append([_a, _b, 2500])


def b_kth2(a, b, k):
    return sorted(a + b)[k - 1]


def g_kth2(r):
    a = sorted(gen_arr(r, -8, 8, 0, 6))
    b = sorted(gen_arr(r, -8, 8, 0, 6))
    if not a and not b:
        b = [r.randint(-8, 8)]
    return [a, b, r.randint(1, len(a) + len(b))]


def v_kth2(tests):
    for t in tests:
        a, b, k = t["args"]
        assert 0 <= len(a) <= 5000 and 0 <= len(b) <= 5000 and len(a) + len(b) >= 1
        assert 1 <= k <= len(a) + len(b)
        assert all(-10 ** 9 <= x <= 10 ** 9 for x in a + b)
        assert a == sorted(a) and b == sorted(b)


CHECKS["kth-element-of-two-sorted-arrays"] = (b_kth2, g_kth2, "exact")
VALIDATE["kth-element-of-two-sorted-arrays"] = v_kth2


# ---------------------------------------------------------------- HARD

p = add(
    id="kth-number-divisible-by-one-of-three", title="Kth Number Divisible by A, B or C", diff="Hard", topic=TOPIC, tier="extra",
    fn="kthMultipleOfAny", params=[("n", "int"), ("a", "int"), ("b", "int"), ("c", "int")], ret="int", cmp="exact",
    desc="<p>Return the <code>n</code>-th smallest positive integer that is divisible by at least one of <code>a</code>, <code>b</code> and <code>c</code>.</p><p>Example: for <code>n = 5, a = 2, b = 3, c = 5</code> the qualifying numbers are <code>2, 3, 4, 5, 6, 8, ...</code>, so the answer is <code>6</code>.</p><p>The test data guarantees that the answer does not exceed <code>2 * 10<sup>9</sup></code>.</p>",
    constraints=["1 &le; n, a, b, c &le; 10<sup>9</sup>", "The answer is at most 2,000,000,000"],
    hints=["Counting by stepping through integers is far too slow. Count how many qualifying integers are at most a given <code>x</code> instead.",
           "Adding <code>x // a + x // b + x // c</code> counts numbers divisible by two of the values twice (or three times). Fix it with inclusion-exclusion using least common multiples.",
           "<code>count(x) = x//a + x//b + x//c - x//lcm(a,b) - x//lcm(b,c) - x//lcm(a,c) + x//lcm(a,b,c)</code>. It is non-decreasing; binary search the smallest <code>x</code> in <code>[1, 2*10<sup>9</sup>]</code> with <code>count(x) &ge; n</code>."],
    editorial=["The inclusion-exclusion principle gives the number of integers in <code>1..x</code> divisible by at least one of the three values: add single multiples, subtract pairwise-lcm multiples, add the multiples of the lcm of all three. All least common multiples are computed once with <code>lcm(u, v) = u / gcd(u, v) * v</code>. They can be as large as 10<sup>27</sup>; in languages with 64-bit integers cap them at something above the search limit (e.g. 2&middot;10<sup>9</sup> + 1), since a divisor larger than <code>x</code> contributes zero.",
               "The count is non-decreasing in <code>x</code> and increments exactly at qualifying numbers. The smallest <code>x</code> with <code>count(x) &ge; n</code> is therefore the answer, and the statement guarantees <code>x &le; 2&middot;10<sup>9</sup></code>, so the search range is <code>[1, 2&middot;10<sup>9</sup>]</code> (about 31 iterations).",
               "Time O(log 2&middot;10<sup>9</sup>) with a constant number of gcd computations, space O(1). The same idea extends to any number of divisors (with subsets), just with more terms."],
    time="O(log R)", space="O(1)",
    solution='''def kthMultipleOfAny(n, a, b, c):
    from math import gcd

    def lcm(u, v):
        return u // gcd(u, v) * v

    ab, bc, ac = lcm(a, b), lcm(b, c), lcm(a, c)
    abc = lcm(ab, c)

    def count(x):
        return x // a + x // b + x // c - x // ab - x // bc - x // ac + x // abc

    lo, hi = 1, 2 * 10 ** 9
    while lo < hi:
        mid = (lo + hi) // 2
        if count(mid) >= n:
            hi = mid
        else:
            lo = mid + 1
    return lo
''',
    tests=[[5, 2, 3, 5], [3, 2, 3, 5], [1, 7, 11, 13], [4, 2, 3, 4], [1000, 7, 7, 7], [10, 1, 5, 9], [100, 6, 10, 15], [2, 10 ** 9, 10 ** 9, 10 ** 9],
           [1, 10 ** 9, 10 ** 9 - 1, 10 ** 9 - 2], [10 ** 9, 2, 3, 5], [10 ** 9, 2, 2, 2], [600000000, 3, 6, 9], [999999999, 2, 4, 7],
           [500000000, 3, 5, 7], [1000, 999983, 999979, 999961]],
)


def b_any3(n, a, b, c):
    x = 0
    while n:
        x += 1
        if x % a == 0 or x % b == 0 or x % c == 0:
            n -= 1
    return x


def g_any3(r):
    return [r.randint(1, 40), r.randint(1, 9), r.randint(1, 9), r.randint(1, 9)]


def v_any3(tests):
    for t in tests:
        n, a, b, c = t["args"]
        assert all(1 <= v <= 10 ** 9 for v in (n, a, b, c))
        assert 1 <= t["expected"] <= 2 * 10 ** 9
        assert any(t["expected"] % v == 0 for v in (a, b, c))


CHECKS["kth-number-divisible-by-one-of-three"] = (b_any3, g_any3, "exact")
VALIDATE["kth-number-divisible-by-one-of-three"] = v_any3

p = add(
    id="kth-smallest-prime-fraction", title="Kth Smallest Prime Fraction", diff="Hard", topic=TOPIC, tier="common",
    fn="kthPrimeFraction", params=[("arr", "int[]"), ("k", "int")], ret="int[]", cmp="exact",
    desc="<p>The array <code>arr</code> is sorted in strictly increasing order. Its first element is <code>1</code> and every other element is a distinct prime number. For every pair of positions <code>i &lt; j</code> consider the fraction <code>arr[i] / arr[j]</code> (a value strictly between 0 and 1).</p><p>Sort all <code>n(n-1)/2</code> fractions by value and return the <code>k</code>-th smallest as the two-element array <code>[arr[i], arr[j]]</code> (numerator, denominator). Because 1 and the primes are pairwise coprime, all these fractions are distinct, so the answer is unique.</p><p>Example: for <code>arr = [1, 2, 3, 5]</code> the fractions in order are <code>1/5, 1/3, 2/5, 1/2, 3/5, 2/3</code>, so <code>k = 3</code> gives <code>[2, 5]</code>.</p>",
    constraints=["2 &le; arr.length &le; 2,000", "arr[0] = 1 and every other arr[i] is a prime number, 2 &le; arr[1] &lt; arr[2] &lt; ... &le; 30,000", "1 &le; k &le; n(n-1)/2"],
    hints=["Putting all roughly two million fractions in a sorted structure works for tiny inputs but is wasteful. Search over the fraction's <em>value</em>, a real number between 0 and 1.",
           "For a threshold <code>t</code>, count the pairs with <code>arr[i] / arr[j] &le; t</code>. For each numerator index <code>i</code> the matching <code>j</code> form a suffix, and the starting point of that suffix only moves right as <code>i</code> grows, so two pointers count in O(n).",
           "Binary search <code>t</code> in <code>(0, 1)</code>. During each count, also remember the largest fraction found that is &le; <code>t</code>. As soon as the count equals exactly <code>k</code>, that remembered fraction is the answer. Distinct fractions differ by at least about 10<sup>-9</sup>, so doubles are precise enough."],
    editorial=["For a threshold <code>t</code> in (0, 1), the fractions at most <code>t</code> are counted with two pointers. For numerator index <code>i</code>, let <code>j</code> be the smallest index with <code>arr[i] / arr[j] &le; t</code>; then all indices from <code>j</code> to <code>n - 1</code> work. Since <code>arr[i]</code> grows with <code>i</code>, a larger denominator is needed, so <code>j</code> never moves left. While counting we also track the largest qualifying fraction.",
               "Bisect on <code>t</code>: if the count is below <code>k</code> raise the lower bound, if above, lower the upper bound, and when the count is exactly <code>k</code> the largest tracked fraction is the k-th smallest. Termination is guaranteed because all fractions are distinct: there is a gap between consecutive fractions of at least <code>1 / (30000 &middot; 30000)</code>, about 1.1&middot;10<sup>-9</sup>, which is much larger than double rounding error, so some midpoint isolates exactly <code>k</code> fractions.",
               "Each count costs O(n); about 30-40 bisection steps are needed, for O(n log(1/eps)) time and O(1) space. A min-heap of the next fraction in each row gives O(k log n) instead, which is too slow when <code>k</code> is around n<sup>2</sup>/2."],
    time="O(n log(1/eps))", space="O(1)",
    solution='''def kthPrimeFraction(arr, k):
    n = len(arr)
    lo, hi = 0.0, 1.0
    while True:
        mid = (lo + hi) / 2
        count = 0
        best_num, best_den = 0, 1
        j = 1
        for i in range(n - 1):
            while j < n and arr[i] > mid * arr[j]:
                j += 1
            if j == n:
                break
            count += n - j
            if arr[i] * best_den > best_num * arr[j]:
                best_num, best_den = arr[i], arr[j]
        if count == k:
            return [best_num, best_den]
        if count < k:
            lo = mid
        else:
            hi = mid
''',
    tests=[[[1, 2, 3, 5], 3], [[1, 2, 3, 5], 1], [[1, 2, 3, 5], 6], [[1, 7], 1], [[1, 2], 1], [[1, 3, 7, 11], 4], [[1, 2, 3, 5, 7, 11], 8],
           [[1, 2, 3, 5, 7, 11], 15], [[1, 29983, 29989], 2], [[1, 2, 29983, 29989], 5]],
)
_r = rnd(9507)
_pr = _primes(30000)
_big = [1] + sorted(_r.sample(_pr, 1999))
p["tests"].append([_big, 1])
p["tests"].append([_big, 1999 * 2000 // 2])
p["tests"].append([_big, 999 * 1000])
p["tests"].append([_big, 1234567])
_mid = [1] + _pr[:1500]
p["tests"].append([_mid, 1000000])
p["tests"].append([_mid, 777])


def b_frac(arr, k):
    from fractions import Fraction
    prs = [(arr[i], arr[j]) for i in range(len(arr)) for j in range(i + 1, len(arr))]
    prs.sort(key=lambda q: Fraction(q[0], q[1]))
    return list(prs[k - 1])


_SMALL_PRIMES = _primes(60)


def g_frac(r):
    n = r.randint(2, 7)
    arr = [1] + sorted(r.sample(_SMALL_PRIMES, n - 1))
    return [arr, r.randint(1, n * (n - 1) // 2)]


def v_frac(tests):
    pset = set(_primes(30000))
    for t in tests:
        arr, k = t["args"]
        n = len(arr)
        assert 2 <= n <= 2000 and arr[0] == 1
        assert all(x in pset for x in arr[1:]) and all(arr[i] < arr[i + 1] for i in range(n - 1))
        assert 1 <= k <= n * (n - 1) // 2
        a_, b_ = t["expected"]
        assert a_ in arr and b_ in arr and a_ < b_


CHECKS["kth-smallest-prime-fraction"] = (b_frac, g_frac, "exact")
VALIDATE["kth-smallest-prime-fraction"] = v_frac

p = add(
    id="kth-smallest-product-of-two-sorted-arrays", title="Kth Smallest Product of Two Sorted Arrays", diff="Hard", topic=TOPIC, tier="extra",
    fn="kthProduct", params=[("a", "int[]"), ("b", "int[]"), ("k", "int")], ret="int", cmp="exact",
    desc="<p>Both arrays <code>a</code> and <code>b</code> are sorted in non-decreasing order and may contain negative numbers, zeros and duplicates. Form all <code>a.length * b.length</code> products <code>a[i] * b[j]</code>, sort them in non-decreasing order and return the <code>k</code>-th one (1-indexed). Equal products from different pairs are counted separately.</p><p>Example: for <code>a = [-2, 1, 3]</code> and <code>b = [-1, 4]</code> the products are <code>2, -8, -1, 4, -3, 12</code>, sorted <code>-8, -3, -1, 2, 4, 12</code>, so <code>k = 4</code> gives <code>2</code>.</p>",
    constraints=["1 &le; a.length, b.length &le; 5,000", "-40,000 &le; a[i], b[j] &le; 40,000 (so every product fits in a 32-bit integer)", "1 &le; k &le; a.length * b.length"],
    hints=["Up to 25 million products is too many to sort. Binary search the answer value <code>x</code> and count the products &le; <code>x</code>.",
           "For one fixed <code>a[i]</code>, the condition <code>a[i] * b[j] &le; x</code> depends on the sign of <code>a[i]</code>: for positive <code>a[i]</code> it holds for a prefix of <code>b</code>, for negative <code>a[i]</code> a suffix, and for zero it holds for all or none.",
           "Positive <code>v</code>: need <code>b[j] &le; floor(x / v)</code>. Negative <code>v</code>: need <code>b[j] &ge; ceil(x / v)</code>, which equals <code>-floor(x / (-v))</code>. Use floor division carefully and a bisect on <code>b</code>."],
    editorial=["Let <code>count(x)</code> be the number of pairs with product at most <code>x</code>; it is non-decreasing in <code>x</code> and the answer is the smallest <code>x</code> with <code>count(x) &ge; k</code>, searched in <code>[min product, max product]</code> (the extremes are among the four corner products of the sorted arrays).",
               "To compute <code>count(x)</code>, handle each <code>v = a[i]</code> by its sign. If <code>v &gt; 0</code>, the valid partners are <code>b[j] &le; floor(x / v)</code>, a prefix found with <code>bisect_right</code>. If <code>v &lt; 0</code>, dividing by a negative flips the inequality: <code>b[j] &ge; ceil(x / v)</code>, a suffix found with <code>bisect_left</code>; with integer floor division <code>ceil(x / v) = -floor(x / (-v))</code>. If <code>v = 0</code>, every product is 0, so all <code>|b|</code> pairs count when <code>x &ge; 0</code> and none otherwise.",
               "The search needs about 32 iterations of an O(|a| log |b|) count, so O(|a| log |b| log R) time and O(1) space. Iterating over the shorter array is faster, since the product is symmetric. The classic mistakes are floor/ceil on negative numbers and treating zero as a positive or negative value."],
    time="O(|a| log|b| log R)", space="O(1)",
    solution='''def kthProduct(a, b, k):
    from bisect import bisect_left, bisect_right
    if len(a) > len(b):
        a, b = b, a
    m = len(b)

    def count(x):
        total = 0
        for v in a:
            if v > 0:
                total += bisect_right(b, x // v)
            elif v < 0:
                total += m - bisect_left(b, -(x // -v))
            elif x >= 0:
                total += m
        return total

    corners = (a[0] * b[0], a[0] * b[-1], a[-1] * b[0], a[-1] * b[-1])
    lo, hi = min(corners), max(corners)
    while lo < hi:
        mid = (lo + hi) // 2
        if count(mid) >= k:
            hi = mid
        else:
            lo = mid + 1
    return lo
''',
    tests=[[[-2, 1, 3], [-1, 4], 4], [[-2, 1, 3], [-1, 4], 1], [[-2, 1, 3], [-1, 4], 6], [[5], [7], 1], [[0], [0], 1], [[-3], [4], 1],
           [[-4, -2, 0, 3], [-5, -1, 0, 2, 6], 9], [[-4, -2, 0, 3], [-5, -1, 0, 2, 6], 10], [[-4, -2, 0, 3], [-5, -1, 0, 2, 6], 20],
           [[0, 0, 0], [-7, 7], 3], [[1, 1, 1], [1, 1], 4], [[-40000, 40000], [-40000, 40000], 1], [[-40000, 40000], [-40000, 40000], 4],
           [[-40000, 40000], [-40000, 40000], 2], [[2, 3, 4], [-6, -5, -4, 5, 6], 8]],
)
_r = rnd(9508)
_a = sorted(_r.randint(-40000, 40000) for _ in range(1500))
_b = sorted(_r.randint(-40000, 40000) for _ in range(1500))
p["tests"].append([_a, _b, 1])
p["tests"].append([_a, _b, 2250000])
p["tests"].append([_a, _b, 1125000])
p["tests"].append([_a, _b, 1000001])
_a = sorted(_r.randint(-3, 3) for _ in range(2500))
_b = sorted(_r.randint(-3, 3) for _ in range(2500))
p["tests"].append([_a, _b, 3000000])
p["tests"].append([_a, _b, 3200000])


def b_prod(a, b, k):
    return sorted(x * y for x in a for y in b)[k - 1]


def g_prod(r):
    a = sorted(r.randint(-7, 7) for _ in range(r.randint(1, 6)))
    b = sorted(r.randint(-7, 7) for _ in range(r.randint(1, 6)))
    return [a, b, r.randint(1, len(a) * len(b))]


def v_prod(tests):
    for t in tests:
        a, b, k = t["args"]
        assert 1 <= len(a) <= 5000 and 1 <= len(b) <= 5000
        assert all(-40000 <= x <= 40000 for x in a + b)
        assert all(a[i] <= a[i + 1] for i in range(len(a) - 1)) and all(b[i] <= b[i + 1] for i in range(len(b) - 1))
        assert 1 <= k <= len(a) * len(b)


CHECKS["kth-smallest-product-of-two-sorted-arrays"] = (b_prod, g_prod, "exact")
VALIDATE["kth-smallest-product-of-two-sorted-arrays"] = v_prod
