"""Problems: Dynamic Programming, the longest-increasing-subsequence family. See data/lib.py for the registry."""
from itertools import combinations, permutations
from math import comb

from lib import add, rnd, CHECKS, VALIDATE, gen_arr  # noqa: F401

MOD = 10 ** 9 + 7
TOPIC = "Dynamic Programming"


def _subsets(a):
    """All index-ordered subsequences of a, as lists (small a only)."""
    n = len(a)
    for mask in range(1 << n):
        yield [a[i] for i in range(n) if mask >> i & 1]


# ---------------------------------------------------------------- EASY

_r = rnd(9101)
_nd1 = [_r.randint(0, 40) for _ in range(2500)]
_nd2 = [_r.randint(-10 ** 9, 10 ** 9) for _ in range(2500)]
_nd3 = sorted(_r.randint(0, 600) for _ in range(2400))
_nd4 = [(i * 7919) % 1000 for i in range(2500)]

add(
    id="longest-non-decreasing-subsequence", title="Longest Non-Decreasing Subsequence", diff="Easy", topic=TOPIC,
    fn="longestNonDecreasing", params=[("nums", "int[]")], ret="int", cmp="exact",
    desc="<p>A <em>subsequence</em> of <code>nums</code> is what remains after deleting any number of elements (possibly none) while keeping the order of the others.</p><p>Return the length of the longest subsequence of <code>nums</code> that is <em>non-decreasing</em>, that is, every element is greater than <strong>or equal to</strong> the one before it. For <code>nums = [4, 1, 2, 2, 3, 1]</code> the answer is <code>4</code> (the subsequence <code>1, 2, 2, 3</code>).</p>",
    constraints=["1 &le; nums.length &le; 2,500", "-10<sup>9</sup> &le; nums[i] &le; 10<sup>9</sup>"],
    hints=["Let best[i] be the length of the longest non-decreasing subsequence that ends exactly at index i. How does best[i] depend on the earlier indices?",
           "best[i] = 1 + the largest best[j] over all j &lt; i with nums[j] &le; nums[i] (or just 1 if there is no such j). The answer is the maximum over all i. That is O(n<sup>2</sup>), good enough here.",
           "For O(n log n), keep a sorted list <code>tails</code> where tails[L-1] is the smallest possible last value of a non-decreasing subsequence of length L. For each x, find the first tail strictly greater than x and overwrite it (or append x if none)."],
    editorial=["The straightforward DP defines <code>best[i]</code> as the longest non-decreasing subsequence ending at index i. It is 1 plus the best value among earlier indices j with <code>nums[j] &le; nums[i]</code>. Two nested loops give O(n<sup>2</sup>) time and O(n) space.",
               "The faster method keeps <code>tails</code>, where <code>tails[L-1]</code> is the smallest last value over all non-decreasing subsequences of length L seen so far. This list is always sorted. For a new value x, binary-search the first tail that is <em>strictly greater</em> than x (<code>bisect_right</code>) and replace it with x; if no tail is greater, x extends the longest subsequence, so append it. The final length of <code>tails</code> is the answer.",
               "The only difference from the strictly increasing version is the choice of binary search: <code>bisect_right</code> lets equal values stack up, while <code>bisect_left</code> would make them replace each other. Total cost is O(n log n) time and O(n) space."],
    time="O(n log n)", space="O(n)",
    solution='''from bisect import bisect_right

def longestNonDecreasing(nums):
    tails = []
    for x in nums:
        i = bisect_right(tails, x)
        if i == len(tails):
            tails.append(x)
        else:
            tails[i] = x
    return len(tails)
''',
    tests=[[[4, 1, 2, 2, 3, 1]], [[5, 5, 5, 5]], [[1]], [[3, 2, 1]], [[1, 2, 2, 3, 1, 2]],
           [[10, 9, 2, 5, 3, 7, 101, 18]], [[-3, -3, -5, -1, -1, -1, 0]], [[1, 3, 2, 3, 2, 3, 2, 3]],
           [[-1000000000, 1000000000, -1000000000, 1000000000]], [[2, 1]],
           [_nd1], [_nd2], [_nd3], [_nd4]],
)


def _b_nd(nums):
    best = 0
    for s in _subsets(nums):
        if all(x <= y for x, y in zip(s, s[1:])):
            best = max(best, len(s))
    return best


def _v_nd(tests):
    for t in tests:
        a = t["args"][0]
        assert 1 <= len(a) <= 2500 and all(-10 ** 9 <= x <= 10 ** 9 for x in a)


CHECKS["longest-non-decreasing-subsequence"] = (_b_nd, lambda r: [gen_arr(r, -3, 3, 1, 11)], "exact")
VALIDATE["longest-non-decreasing-subsequence"] = _v_nd


_r = rnd(9102)
_ms1 = [_r.randint(-10000, 10000) for _ in range(2500)]
_ms2 = [_r.randint(1, 9000) for _ in range(2500)]
_ms3 = sorted(_r.randint(-5000, 5000) for _ in range(2000))
_ms4 = [-1 - _r.randint(0, 50) for _ in range(2000)]
_ms5 = list(range(2500, 0, -1))

add(
    id="max-sum-increasing-subsequence", title="Maximum Sum Increasing Subsequence", diff="Easy", topic=TOPIC,
    fn="maxSumIncreasing", params=[("nums", "int[]")], ret="int", cmp="exact",
    desc="<p>Among all <strong>non-empty</strong> strictly increasing subsequences of <code>nums</code>, find the one whose elements add up to the largest total, and return that total.</p><p>A subsequence keeps the original order of the chosen elements. It may have length 1. Values can be negative, so a longer subsequence is not always better. For <code>nums = [1, 101, 2, 3, 100, 4, 5]</code> the answer is <code>106</code> (<code>1 + 2 + 3 + 100</code>).</p>",
    constraints=["1 &le; nums.length &le; 2,500", "-10,000 &le; nums[i] &le; 10,000"],
    hints=["Instead of the length, let total[i] be the best sum of a strictly increasing subsequence that ends exactly at index i.",
           "total[i] = nums[i] + the best total[j] among earlier j with nums[j] &lt; nums[i]; but if every such total[j] is negative (or there is no j), start fresh and use nums[i] alone.",
           "The answer is the maximum total[i] over all i. A Fenwick tree (prefix maximum over value ranks) speeds the O(n<sup>2</sup>) double loop up to O(n log n)."],
    editorial=["This is the longest increasing subsequence recurrence with a different quantity: instead of counting elements, add them. Let <code>total[i]</code> be the maximum sum of a strictly increasing subsequence whose last element is <code>nums[i]</code>. Then <code>total[i] = nums[i] + max(0, max total[j])</code> over indices <code>j &lt; i</code> with <code>nums[j] &lt; nums[i]</code>. The <code>max(0, ...)</code> handles both the case with no valid predecessor and the case where every predecessor sum is negative and extending would hurt.",
               "The answer is the largest <code>total[i]</code>; it must be taken over all i because the best subsequence can end anywhere. The two nested loops cost O(n<sup>2</sup>) time. To reach O(n log n), compress the values to ranks and keep a Fenwick tree that answers 'maximum total among values with rank below r' and supports point updates that keep the maximum."],
    time="O(n log n)", space="O(n)",
    solution='''from bisect import bisect_left

def maxSumIncreasing(nums):
    vals = sorted(set(nums))
    m = len(vals)
    NEG = -10 ** 18
    tree = [NEG] * (m + 1)
    best = NEG
    for x in nums:
        k = bisect_left(vals, x)          # ranks 1..k hold values smaller than x
        q = NEG
        i = k
        while i > 0:
            if tree[i] > q:
                q = tree[i]
            i -= i & -i
        cur = x + (q if q > 0 else 0)
        i = k + 1
        while i <= m:
            if tree[i] < cur:
                tree[i] = cur
            i += i & -i
        if cur > best:
            best = cur
    return best
''',
    tests=[[[1, 101, 2, 3, 100, 4, 5]], [[-5]], [[3, 2, 1]], [[-3, -1, -2]], [[10, 5, 4, 3]], [[1, 2, 3, 4]],
           [[-2, 5, -1, 6, -3, 7]], [[5, 5, 5]], [[10, -20, 11, -30, 12]], [[4, -1, 5, -2, 6, 0, 7]],
           [_ms1], [_ms2], [_ms3], [_ms4], [_ms5]],
)


def _b_ms(nums):
    best = None
    for s in _subsets(nums):
        if s and all(x < y for x, y in zip(s, s[1:])):
            t = sum(s)
            if best is None or t > best:
                best = t
    return best


def _v_ms(tests):
    for t in tests:
        a = t["args"][0]
        assert 1 <= len(a) <= 2500 and all(-10000 <= x <= 10000 for x in a)


CHECKS["max-sum-increasing-subsequence"] = (_b_ms, lambda r: [gen_arr(r, -6, 8, 1, 11)], "exact")
VALIDATE["max-sum-increasing-subsequence"] = _v_ms


# ---------------------------------------------------------------- MEDIUM

def _smooth(limit, primes):
    out = {1}
    for p in primes:
        cur = sorted(out)
        for v in cur:
            while v * p <= limit:
                v *= p
                out.add(v)
    return sorted(out)


_r = rnd(9103)
_sm = _smooth(10 ** 9, [2, 3, 5, 7])
_ds1 = _r.sample(range(1, 30001), 1000)
_ds2 = _r.sample(_sm, min(1000, len(_sm)))
_ds3 = _r.sample([p for p in range(2, 8000) if all(p % q for q in range(2, int(p ** 0.5) + 1))], 900)
_ds4 = [2 ** i for i in range(30)] + [3 ** i for i in range(1, 19)]
_r.shuffle(_ds4)
_ds5 = _r.sample([v * 360360 for v in range(1, 2700)], 1000)
_ds5 = [v for v in _ds5 if v <= 10 ** 9]

add(
    id="largest-divisible-subset-size", title="Largest Divisible Subset", diff="Medium", topic=TOPIC,
    fn="largestDivisibleSubset", params=[("nums", "int[]")], ret="int", cmp="exact",
    desc="<p>The array <code>nums</code> contains distinct positive integers. A subset of its values is <em>divisible</em> if for every two numbers <code>a</code> and <code>b</code> in the subset, either <code>a</code> divides <code>b</code> or <code>b</code> divides <code>a</code>.</p><p>Return the number of elements in the largest divisible subset. A subset with one element is always divisible. For <code>nums = [4, 8, 10, 240]</code> the answer is <code>3</code> (<code>4, 8, 240</code>).</p>",
    constraints=["1 &le; nums.length &le; 1,000", "1 &le; nums[i] &le; 10<sup>9</sup>", "All values of nums are distinct"],
    hints=["Sort the array first. In a sorted divisible subset, which pairs do you really need to check?",
           "If a &lt; b &lt; c and a divides b and b divides c, then a divides c automatically. So a divisible subset is just a chain in which each element divides the next.",
           "Let size[i] be the longest chain ending at the i-th smallest value: size[i] = 1 + max size[j] over j &lt; i with nums[i] % nums[j] == 0. The answer is the maximum size[i]."],
    editorial=["Divisibility is transitive: if a divides b and b divides c then a divides c. After sorting ascending, a subset is divisible exactly when each element divides the next one in sorted order; then every earlier element divides every later one by transitivity. That turns the problem into a longest-chain problem, just like longest increasing subsequence with 'greater than' replaced by 'is a multiple of'.",
               "Define <code>size[i]</code> as the largest divisible subset whose biggest element is <code>nums[i]</code> (in sorted order). Then <code>size[i] = 1 + max(size[j])</code> over earlier j with <code>nums[i] % nums[j] == 0</code>, or 1 if there is none. The result is the maximum of all <code>size[i]</code>. The cost is O(n log n) for sorting plus O(n<sup>2</sup>) for the double loop, with O(n) memory.",
               "Because the values are distinct, a chain always has strictly increasing elements, so sorting never breaks a valid subset. (To print the subset itself, remember for each i the j that gave the maximum and walk back from the best index.)"],
    time="O(n^2)", space="O(n)",
    solution='''def largestDivisibleSubset(nums):
    a = sorted(nums)
    n = len(a)
    size = [1] * n
    for i in range(n):
        x = a[i]
        best = 1
        for j in range(i):
            if x % a[j] == 0 and size[j] + 1 > best:
                best = size[j] + 1
        size[i] = best
    return max(size)
''',
    tests=[[[1, 2, 3]], [[4, 8, 10, 240]], [[5]], [[2, 3, 5, 7]], [[1, 2, 4, 8, 16, 3, 9]], [[6, 3, 12, 24, 5, 10]],
           [[1000000000, 500000000, 250000000, 7]], [[9, 18, 54, 90, 108, 180, 360, 540, 720]], [[3, 7]],
           [_ds1], [_ds2], [_ds3], [_ds4], [_ds5]],
)


def _b_ds(nums):
    n = len(nums)
    best = 0
    for mask in range(1, 1 << n):
        s = [nums[i] for i in range(n) if mask >> i & 1]
        if len(s) > best and all(a % b == 0 or b % a == 0 for a, b in combinations(s, 2)):
            best = len(s)
    return best


def _g_ds(r):
    return r.sample(range(1, r.choice([12, 30, 60])), r.randint(1, 10))


def _v_ds(tests):
    for t in tests:
        a = t["args"][0]
        assert 1 <= len(a) <= 1000 and len(set(a)) == len(a) and all(1 <= x <= 10 ** 9 for x in a)


CHECKS["largest-divisible-subset-size"] = (_b_ds, lambda r: [_g_ds(r)], "exact")
VALIDATE["largest-divisible-subset-size"] = _v_ds


_r = rnd(9104)
_bt1 = [_r.randint(-10 ** 6, 10 ** 6) for _ in range(5000)]
_bt2 = list(range(1, 2501)) + list(range(2500, 0, -1))
_bt3 = [(i * 37) % 1009 for i in range(4000)]
_bt4 = [_r.randint(0, 30) for _ in range(5000)]

add(
    id="longest-bitonic-subsequence", title="Longest Bitonic Subsequence", diff="Medium", topic=TOPIC,
    fn="longestBitonic", params=[("nums", "int[]")], ret="int", cmp="exact",
    desc="<p>A sequence is <em>bitonic</em> if it strictly increases up to some element (the peak) and then strictly decreases after it. Either side may be empty, so a strictly increasing sequence, a strictly decreasing sequence and a single element are all bitonic.</p><p>Return the length of the longest bitonic <em>subsequence</em> of <code>nums</code> (elements keep their original order but may be skipped). For <code>nums = [1, 11, 2, 10, 4, 5, 2, 1]</code> the answer is <code>6</code> (<code>1, 2, 10, 5, 2, 1</code>).</p>",
    constraints=["1 &le; nums.length &le; 5,000", "-10<sup>9</sup> &le; nums[i] &le; 10<sup>9</sup>"],
    hints=["Fix the peak at index i. The bitonic subsequence then splits into an increasing part ending at i and a decreasing part starting at i.",
           "Compute inc[i], the longest strictly increasing subsequence ending at i, and dec[i], the longest strictly decreasing subsequence starting at i. The two parts only share the peak element.",
           "The answer is the maximum of inc[i] + dec[i] - 1. Both arrays come from LIS in O(n log n): inc by a left-to-right pass, dec by running the same pass on the reversed array."],
    editorial=["Every bitonic subsequence has a peak, and once the peak at index i is fixed the two sides are independent: the left side is a strictly increasing subsequence ending at i, the right side a strictly decreasing subsequence starting at i. Their best lengths are <code>inc[i]</code> and <code>dec[i]</code>; the peak is counted in both, so the best bitonic subsequence with peak i has length <code>inc[i] + dec[i] - 1</code>.",
               "To compute <code>inc</code> use the tails technique: keep a sorted list of smallest tail values per length, and for each x find the slot with <code>bisect_left</code>; the slot index plus one is the length of the longest increasing subsequence ending at x. For <code>dec</code>, a decreasing subsequence starting at i is an increasing subsequence ending at i when you read the array from right to left, so run the same procedure on the reversed array and flip the result back.",
               "Two O(n log n) passes plus a linear scan: O(n log n) time and O(n) space. The O(n<sup>2</sup>) DP with two nested loops is also fine for n = 5,000 in compiled languages."],
    time="O(n log n)", space="O(n)",
    solution='''from bisect import bisect_left

def longestBitonic(nums):
    def ending_lengths(a):
        tails = []
        out = []
        for x in a:
            i = bisect_left(tails, x)
            if i == len(tails):
                tails.append(x)
            else:
                tails[i] = x
            out.append(i + 1)
        return out

    inc = ending_lengths(nums)
    dec = ending_lengths(nums[::-1])[::-1]
    return max(inc[i] + dec[i] - 1 for i in range(len(nums)))
''',
    tests=[[[1, 11, 2, 10, 4, 5, 2, 1]], [[1]], [[5, 4, 3, 2, 1]], [[1, 2, 3, 4]], [[3, 3, 3]],
           [[1, 3, 5, 4, 2]], [[2, 1, 2, 3, 1, 5, 0]], [[-5, -1, -3, -2, -8, -4]], [[1, 2, 1, 2, 1]],
           [[0, 8, 4, 12, 2, 10, 6, 14, 1, 9, 5, 13, 3, 11, 7, 15]],
           [_bt1], [_bt2], [_bt3], [_bt4]],
)


def _is_bitonic(s):
    k = 0
    while k + 1 < len(s) and s[k] < s[k + 1]:
        k += 1
    return all(s[i] > s[i + 1] for i in range(k, len(s) - 1))


def _b_bt(nums):
    best = 0
    for s in _subsets(nums):
        if len(s) > best and _is_bitonic(s):
            best = len(s)
    return best


def _v_bt(tests):
    for t in tests:
        a = t["args"][0]
        assert 1 <= len(a) <= 5000 and all(-10 ** 9 <= x <= 10 ** 9 for x in a)


CHECKS["longest-bitonic-subsequence"] = (_b_bt, lambda r: [gen_arr(r, -4, 4, 1, 11)], "exact")
VALIDATE["longest-bitonic-subsequence"] = _v_bt


_r = rnd(9105)


def _mountain_best(a):
    """Longest mountain subsequence (>= 3 elements, interior strict peak), 0 if none. O(n^2) helper."""
    n = len(a)
    inc = [1] * n
    dec = [1] * n
    for i in range(n):
        for j in range(i):
            if a[j] < a[i] and inc[j] + 1 > inc[i]:
                inc[i] = inc[j] + 1
    for i in range(n - 1, -1, -1):
        for j in range(i + 1, n):
            if a[j] < a[i] and dec[j] + 1 > dec[i]:
                dec[i] = dec[j] + 1
    best = 0
    for i in range(n):
        if inc[i] >= 2 and dec[i] >= 2:
            best = max(best, inc[i] + dec[i] - 1)
    return best


_mr1 = [_r.randint(1, 10 ** 6) for _ in range(4000)]
_mr2 = [min(i, 3000 - i) + _r.randint(0, 5) for i in range(3000)]
_mr3 = list(range(1, 2001)) + [1000]
_mr4 = [_r.randint(1, 40) for _ in range(5000)]

add(
    id="min-removals-to-make-mountain", title="Minimum Removals to Make a Mountain", diff="Medium", topic=TOPIC,
    fn="minRemovalsMountain", params=[("nums", "int[]")], ret="int", cmp="exact",
    desc="<p>An array is a <em>mountain</em> if it has at least 3 elements and there is an index <code>p</code> with <code>0 &lt; p &lt; length - 1</code> such that the values strictly increase up to <code>p</code> and strictly decrease after it. Both slopes must have at least one step, so the peak is never the first or last element.</p><p>Return the smallest number of elements you must delete from <code>nums</code> so that what remains is a mountain. The input is guaranteed to allow this. For <code>nums = [2, 1, 1, 5, 6, 2, 3, 1]</code> the answer is <code>3</code> (keep <code>1, 5, 6, 3, 1</code>).</p>",
    constraints=["3 &le; nums.length &le; 5,000", "1 &le; nums[i] &le; 10<sup>9</sup>", "A mountain can be obtained by deleting some elements"],
    hints=["Keeping as many elements as possible is the same as finding the longest mountain subsequence. Fix the peak index p.",
           "Let inc[p] be the longest strictly increasing subsequence ending at p, and dec[p] the longest strictly decreasing subsequence starting at p. A peak is only valid if both are at least 2.",
           "The longest mountain through p keeps inc[p] + dec[p] - 1 elements. Take the best valid p; the answer is n minus that. Compute inc and dec in O(n log n) with the tails technique, or in O(n<sup>2</sup>) with a double loop."],
    editorial=["The elements to keep must form a mountain, so we want the longest mountain subsequence. Choose its peak at index p. The part left of the peak is a strictly increasing subsequence ending at p; the part right of it is a strictly decreasing subsequence starting at p, and the two can be chosen independently. The best choices have lengths <code>inc[p]</code> and <code>dec[p]</code>, giving a mountain of <code>inc[p] + dec[p] - 1</code> elements.",
               "The only subtlety is the requirement of both slopes: a peak with <code>inc[p] = 1</code> (nothing before it) or <code>dec[p] = 1</code> (nothing after it) is not a mountain, so those indices must be skipped. This is the usual trap; a plain 'longest bitonic' formula would wrongly allow a sorted array to be kept completely.",
               "Compute <code>inc</code> and <code>dec</code> with the LIS tails technique (<code>bisect_left</code> for strictness) in O(n log n), then scan all valid p. The answer is <code>n - max(inc[p] + dec[p] - 1)</code>. Memory is O(n)."],
    time="O(n log n)", space="O(n)",
    solution='''from bisect import bisect_left

def minRemovalsMountain(nums):
    def ending_lengths(a):
        tails = []
        out = []
        for x in a:
            i = bisect_left(tails, x)
            if i == len(tails):
                tails.append(x)
            else:
                tails[i] = x
            out.append(i + 1)
        return out

    n = len(nums)
    inc = ending_lengths(nums)
    dec = ending_lengths(nums[::-1])[::-1]
    best = 0
    for p in range(n):
        if inc[p] >= 2 and dec[p] >= 2:
            best = max(best, inc[p] + dec[p] - 1)
    return n - best
''',
    tests=[[[2, 1, 1, 5, 6, 2, 3, 1]], [[1, 3, 1]], [[1, 2, 3, 4, 3]], [[4, 3, 1, 2, 5, 4, 1]],
           [[5, 1, 2, 3, 3, 3, 2, 1, 9]], [[1, 2, 1, 2, 1]], [[3, 1, 2, 1]], [[1, 5, 2, 5, 1, 5, 2]],
           [[1, 16, 1, 15, 2, 14, 3, 13, 4, 12]], [[7, 7, 1, 7, 7, 3, 7, 7]],
           [_mr1], [_mr2], [_mr3], [_mr4]],
)


def _is_mountain(s):
    if len(s) < 3:
        return False
    for p in range(1, len(s) - 1):
        if all(s[i] < s[i + 1] for i in range(p)) and all(s[i] > s[i + 1] for i in range(p, len(s) - 1)):
            return True
    return False


def _b_mr(nums):
    best = 0
    for s in _subsets(nums):
        if len(s) > best and _is_mountain(s):
            best = len(s)
    return len(nums) - best


def _g_mr(r):
    while True:
        a = [r.randint(1, r.choice([3, 5, 8])) for _ in range(r.randint(3, 11))]
        if _mountain_best(a) >= 3:
            return a


def _v_mr(tests):
    for t in tests:
        a = t["args"][0]
        assert 3 <= len(a) <= 5000 and all(1 <= x <= 10 ** 9 for x in a)
        assert _mountain_best(a) >= 3, "no mountain possible"


CHECKS["min-removals-to-make-mountain"] = (_b_mr, lambda r: [_g_mr(r)], "exact")
VALIDATE["min-removals-to-make-mountain"] = _v_mr


_r = rnd(9106)
_pt1 = [_r.randint(-10 ** 9, 10 ** 9) for _ in range(3000)]
_pt2 = list(range(3000, 0, -1))
_pt3 = [_r.randint(0, 20) for _ in range(4000)]
_pt4 = list(range(3000))
_pt5 = [(i * 53) % 977 for i in range(3500)]

add(
    id="min-increasing-subsequences-cover", title="Fewest Increasing Subsequences to Cover an Array", diff="Medium", topic=TOPIC,
    fn="minIncreasingGroups", params=[("nums", "int[]")], ret="int", cmp="exact",
    desc="<p>You must split the elements of <code>nums</code> into groups so that every element belongs to exactly one group and, inside each group, the elements taken in their original order are <strong>strictly increasing</strong>. The elements of a group do not have to be adjacent in <code>nums</code>.</p><p>Return the smallest possible number of groups. For <code>nums = [3, 1, 4, 1, 5, 9, 2, 6]</code> the answer is <code>3</code> (for example the groups <code>3, 4, 5, 9</code>, <code>1, 2, 6</code> and <code>1</code>), while for a strictly decreasing array of length n the answer is <code>n</code>.</p>",
    constraints=["1 &le; nums.length &le; 5,000", "-10<sup>9</sup> &le; nums[i] &le; 10<sup>9</sup>"],
    hints=["Think of building the groups one element at a time. Each new element either extends an existing group or starts a new one. Which group should it extend?",
           "An element x can extend a group whose last element is smaller than x. Extending the group with the largest such last element wastes the least: the groups with small ends stay available for small values.",
           "Keep the sorted list of group ends. For x, replace the largest end that is smaller than x with x, or insert x as a brand new end if no end is smaller. The size of the list is the answer (it equals the length of the longest non-increasing subsequence)."],
    editorial=["Process the array left to right and maintain the last element of every group in a sorted list <code>ends</code>. A new element x can join any group whose end is strictly smaller than x. Among those, joining the one with the <em>largest</em> end is never worse: it uses up the least flexible end and leaves the groups with smaller ends free for smaller future values (an exchange argument). If no end is smaller than x, a new group must start.",
               "With binary search, <code>i = bisect_left(ends, x)</code> is the number of ends smaller than x. If <code>i == 0</code> insert x at the front as a new group; otherwise overwrite <code>ends[i-1]</code> with x. The list stays sorted, and its final length is the answer. The cost is O(n log n) to search plus the list insertion at the front, fine for n = 5,000.",
               "There is a neat characterisation of the same number: it equals the length of the longest <em>non-increasing</em> subsequence. Such a subsequence can never fit into one increasing group (two of its elements would be in decreasing or equal order), so you need at least that many groups, and the greedy above shows that this many always suffice (this is Dilworth's theorem for this order)."],
    time="O(n log n)", space="O(n)",
    solution='''from bisect import bisect_left

def minIncreasingGroups(nums):
    ends = []
    for x in nums:
        i = bisect_left(ends, x)
        if i == 0:
            ends.insert(0, x)
        else:
            ends[i - 1] = x
    return len(ends)
''',
    tests=[[[3, 1, 4, 1, 5, 9, 2, 6]], [[1, 2, 3, 4]], [[5, 4, 3, 2, 1]], [[7]], [[2, 2, 2]], [[1, 3, 2, 4, 3, 5]],
           [[10, 1, 11, 2, 12, 3]], [[4, 3, 3, 2, 5, 1]], [[-1, -2, -3, 0, -4]], [[1, 5, 2, 6, 3, 7, 4, 8]],
           [_pt1], [_pt2], [_pt3], [_pt4], [_pt5]],
)


def _b_pt(nums):
    best = [len(nums)]
    groups = []

    def go(i):
        if len(groups) >= best[0]:
            return
        if i == len(nums):
            best[0] = len(groups)
            return
        x = nums[i]
        for g in range(len(groups)):
            if groups[g] < x:
                old = groups[g]
                groups[g] = x
                go(i + 1)
                groups[g] = old
        groups.append(x)
        go(i + 1)
        groups.pop()

    go(0)
    return best[0]


def _v_pt(tests):
    for t in tests:
        a = t["args"][0]
        assert 1 <= len(a) <= 5000 and all(-10 ** 9 <= x <= 10 ** 9 for x in a)


CHECKS["min-increasing-subsequences-cover"] = (_b_pt, lambda r: [gen_arr(r, -4, 4, 1, 8)], "exact")
VALIDATE["min-increasing-subsequences-cover"] = _v_pt


_r = rnd(9107)
_ck1 = ([_r.randint(1, 1000) for _ in range(800)], 8)
_ck2 = (list(range(1, 801)), 40)
_ck3 = ([_r.randint(1, 50) for _ in range(800)], 5)
_ck4 = ([_r.randint(1, 10 ** 9) for _ in range(800)], 30)
_ck5 = (list(range(800, 0, -1)), 2)
_ck6 = ([(i * 31) % 700 + 1 for i in range(800)], 25)

add(
    id="count-increasing-subsequences-of-length-k", title="Count Increasing Subsequences of Length K", diff="Medium", topic=TOPIC,
    fn="countIncreasingOfLengthK", params=[("nums", "int[]"), ("k", "int")], ret="int", cmp="exact",
    desc="<p>Count the strictly increasing subsequences of <code>nums</code> that have exactly <code>k</code> elements. Two subsequences are different when they use different sets of indices, even if they contain the same values.</p><p>The count can be huge, so return it modulo <code>1,000,000,007</code>. For <code>nums = [1, 3, 2, 4]</code> and <code>k = 3</code> the answer is <code>2</code> (<code>1, 3, 4</code> and <code>1, 2, 4</code>).</p>",
    constraints=["1 &le; nums.length &le; 800", "1 &le; nums[i] &le; 10<sup>9</sup>", "1 &le; k &le; 40"],
    hints=["Count by length. Let ways[l][i] be the number of strictly increasing subsequences of length l that end exactly at index i. What is ways[1][i]?",
           "ways[l][i] is the sum of ways[l-1][j] over all j &lt; i with nums[j] &lt; nums[i]. The answer is the sum of ways[k][i] over all i. Done naively that is O(k n<sup>2</sup>).",
           "For each level l, sweep i from left to right and keep a Fenwick tree indexed by value rank that holds ways[l-1][j] for the indices already seen. The inner sum is then a prefix query: O(k n log n) in total."],
    editorial=["Layer the DP by subsequence length. A subsequence of length 1 is any single element, so <code>ways[1][i] = 1</code>. A subsequence of length l ending at i is a subsequence of length l-1 ending at some earlier index j with a smaller value, followed by i. Hence <code>ways[l][i] = sum ways[l-1][j]</code> over <code>j &lt; i</code> and <code>nums[j] &lt; nums[i]</code>, and the answer is the sum of <code>ways[k][i]</code> over all i (modulo 1,000,000,007).",
               "Evaluating that sum with a loop is O(n) per cell, so O(k n<sup>2</sup>) overall. Instead process each level in one left-to-right sweep. Compress the values to ranks, and keep a Fenwick (binary indexed) tree where position <code>rank[j]</code> holds <code>ways[l-1][j]</code> for every j already visited. For index i, query the prefix of ranks strictly below <code>rank[i]</code> to get <code>ways[l][i]</code>, then insert <code>ways[l-1][i]</code> at <code>rank[i]</code>. Equal values never combine because the query excludes the own rank.",
               "Total time is O(k n log n) and memory O(n) (only the previous level is kept). If at some level every count is zero, the answer is 0 and the loop can stop early."],
    time="O(k n log n)", space="O(n)",
    solution='''from bisect import bisect_left

def countIncreasingOfLengthK(nums, k):
    M = 1000000007
    n = len(nums)
    if k > n:
        return 0
    vals = sorted(set(nums))
    m = len(vals)
    rank = [bisect_left(vals, x) + 1 for x in nums]
    prev = [1] * n
    for _ in range(k - 1):
        tree = [0] * (m + 1)
        cur = [0] * n
        for i in range(n):
            s = 0
            j = rank[i] - 1
            while j > 0:
                s += tree[j]
                j -= j & -j
            cur[i] = s % M
            v = prev[i]
            if v:
                j = rank[i]
                while j <= m:
                    tree[j] += v
                    j += j & -j
        prev = cur
        if not any(prev):
            return 0
    return sum(prev) % M
''',
    tests=[[[1, 3, 2, 4], 3], [[5, 4, 3, 2, 1], 1], [[2, 2, 2], 2], [[1, 2, 3, 4, 5], 5], [[3, 1, 2], 2],
           [[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30], 5],
           [[1, 1, 2, 2, 3, 3], 3], [[7], 2], [[4, 1, 5, 2, 6, 3, 7], 3], [[10, 20, 10, 30, 20, 40], 4],
           [_ck1[0], _ck1[1]], [_ck2[0], _ck2[1]], [_ck3[0], _ck3[1]], [_ck4[0], _ck4[1]], [_ck5[0], _ck5[1]], [_ck6[0], _ck6[1]]],
)


def _b_ck(nums, k):
    cnt = 0
    for idx in combinations(range(len(nums)), k):
        if all(nums[a] < nums[b] for a, b in zip(idx, idx[1:])):
            cnt += 1
    return cnt % MOD


def _g_ck(r):
    n = r.randint(1, 11)
    return [[r.randint(1, r.choice([4, 8, 12])) for _ in range(n)], r.randint(1, min(6, n + 1))]


def _v_ck(tests):
    for t in tests:
        a, k = t["args"]
        assert 1 <= len(a) <= 800 and all(1 <= x <= 10 ** 9 for x in a) and 1 <= k <= 40
        if len(set(a)) == len(a) and a == sorted(a):
            assert t["expected"] == comb(len(a), k) % MOD, "sorted distinct arrays must give C(n, k)"
        if a == sorted(a, reverse=True) and k >= 2:
            assert t["expected"] == 0


CHECKS["count-increasing-subsequences-of-length-k"] = (_b_ck, _g_ck, "exact")
VALIDATE["count-increasing-subsequences-of-length-k"] = _v_ck


_r = rnd(9108)
_lx1 = [_r.randint(-10 ** 6, 10 ** 6) for _ in range(3000)]
_lx2 = [_r.randint(1, 60) for _ in range(3000)]
_lx3 = [v for i in range(500) for v in (3 * i + 3, 3 * i + 1, 3 * i + 2)]
_lx4 = [(i * 41) % 2003 for i in range(2800)]
_lx5 = [v for i in range(400) for v in (2 * i + 2, 2 * i + 1)] + list(range(801, 1500))

add(
    id="lexicographically-smallest-longest-increasing", title="Lexicographically Smallest Longest Increasing Subsequence", diff="Medium", topic=TOPIC,
    fn="lexSmallestLis", params=[("nums", "int[]")], ret="int[]", cmp="exact",
    desc="<p>Many different subsequences of <code>nums</code> can share the maximum possible length among strictly increasing subsequences. Among all of them, return the one that is smallest when compared as a list of values from left to right (compare the first values; if equal, the second values; and so on). All the candidates have the same length, so there are no prefix ties.</p><p>Return that subsequence as an array of values. For <code>nums = [10, 9, 2, 5, 3, 7, 101, 18]</code> the longest strictly increasing subsequences have length 4, and the smallest of them is <code>[2, 3, 7, 18]</code>.</p>",
    constraints=["1 &le; nums.length &le; 3,000", "-10<sup>6</sup> &le; nums[i] &le; 10<sup>6</sup>"],
    hints=["First find the length L of the longest strictly increasing subsequence. Then think about which first elements can start a subsequence of length exactly L.",
           "Compute f[i], the length of the longest strictly increasing subsequence that <em>starts</em> at index i (run LIS on the reversed array with negated values). An element may be chosen at step t only if f[i] equals the number of elements still to choose.",
           "Build the answer greedily: for the remaining count c, among indices after the last chosen index, with f[i] == c and value greater than the last chosen value, take the smallest value (the earliest index among equal values). Group the indices by f to keep the total work linear."],
    editorial=["Let <code>f[i]</code> be the length of the longest strictly increasing subsequence starting at index i. It can be computed in O(n log n) by scanning the array from right to left and running the tails technique on the negated values (a strictly increasing run read right to left in the original is strictly increasing in the negated values). The longest length is <code>L = max f[i]</code>.",
               "Every longest subsequence has the form: element with <code>f = L</code>, then element with <code>f = L-1</code>, and so on down to <code>f = 1</code>. So the choice at each step is limited to indices whose <code>f</code> equals the count of elements still needed, with the usual constraints (later index, larger value than the previous pick). Any such candidate can still be completed to full length L, so greedily taking the smallest value is safe: a smaller value at the earliest position always wins the lexicographic comparison.",
               "Among equal values take the earliest index; it leaves a superset of the continuations of the later one. Bucket indices by their <code>f</code> value, so each step only scans its own bucket and the whole reconstruction is O(n). Total time O(n log n), memory O(n)."],
    time="O(n log n)", space="O(n)",
    solution='''from bisect import bisect_left

def lexSmallestLis(nums):
    n = len(nums)
    f = [0] * n
    tails = []
    for i in range(n - 1, -1, -1):
        y = -nums[i]
        p = bisect_left(tails, y)
        if p == len(tails):
            tails.append(y)
        else:
            tails[p] = y
        f[i] = p + 1
    L = len(tails)
    buckets = [[] for _ in range(L + 1)]
    for i in range(n):
        buckets[f[i]].append(i)
    result = []
    last_idx = -1
    last_val = None
    for level in range(L, 0, -1):
        best = -1
        for i in buckets[level]:
            if i > last_idx and (last_val is None or nums[i] > last_val):
                if best == -1 or nums[i] < nums[best]:
                    best = i
        result.append(nums[best])
        last_idx = best
        last_val = nums[best]
    return result
''',
    tests=[[[10, 9, 2, 5, 3, 7, 101, 18]], [[5]], [[3, 2, 1]], [[1, 2, 3]], [[2, 2, 2]], [[4, 10, 4, 3, 8, 9]],
           [[1, 3, 2, 4]], [[3, 4, 1, 2]], [[-1, 5, -3, 0, -2, 1]], [[5, 6, 1, 2, 3, 4, 0]], [[2, 1, 2, 1, 2, 3]],
           [_lx1], [_lx2], [_lx3], [_lx4], [_lx5]],
)


def _b_lx(nums):
    best = []
    for s in _subsets(nums):
        if all(x < y for x, y in zip(s, s[1:])):
            if len(s) > len(best) or (len(s) == len(best) and s < best):
                best = s
    return best


def _v_lx(tests):
    for t in tests:
        a = t["args"][0]
        assert 1 <= len(a) <= 3000 and all(-10 ** 6 <= x <= 10 ** 6 for x in a)
        e = t["expected"]
        assert all(x < y for x, y in zip(e, e[1:]))


CHECKS["lexicographically-smallest-longest-increasing"] = (_b_lx, lambda r: [gen_arr(r, -4, 4, 1, 11)], "exact")
VALIDATE["lexicographically-smallest-longest-increasing"] = _v_lx


# ---------------------------------------------------------------- HARD

_r = rnd(9109)
_cu1 = [[_r.randint(1, 10000) for _ in range(3)] for _ in range(500)]
_cu2 = [[_r.randint(1, 30) for _ in range(3)] for _ in range(500)]
_cu3 = [[i + 1, i + 1, i + 1] for i in range(500)]
_cu4 = [[_r.randint(1, 100), _r.randint(1, 100), _r.randint(1, 100)] for _ in range(300)]
_cu5 = [[500 - i, 1 + (i * 7) % 300, 1 + (i * 13) % 400] for i in range(450)]

add(
    id="stack-cuboids-max-height", title="Tallest Stack of Cuboids", diff="Hard", topic=TOPIC, tier="extra",
    fn="maxStackHeight", params=[("cuboids", "int[][]")], ret="int", cmp="exact",
    desc="<p>Each element of <code>cuboids</code> is a triple <code>[a, b, c]</code> of side lengths of a solid box. You may choose any subset of the boxes and stack them in a tower, rotating each box freely: any of its three sides may be used as the vertical side (its height) and the other two as width and depth.</p><p>Box <code>X</code> may be placed directly on box <code>Y</code> only if, in the orientations you picked, <code>width(X) &le; width(Y)</code>, <code>depth(X) &le; depth(Y)</code> and <code>height(X) &le; height(Y)</code>. Return the greatest possible total height of a tower. A tower of a single box is allowed. For <code>cuboids = [[50, 45, 20], [95, 37, 53], [45, 23, 12]]</code> the answer is <code>190</code> (stack all three boxes; standing each on its longest side gives heights 45 + 50 + 95).</p>",
    constraints=["1 &le; cuboids.length &le; 500", "cuboids[i].length == 3", "1 &le; cuboids[i][j] &le; 10,000"],
    hints=["A box has only 6 orientations, but you can avoid trying them all. If a box fits on another one in some orientation, what does that say about their sorted side lengths?",
           "Sort the three sides of every box: <code>x &le; y &le; z</code>. Then box X can go on box Y (in some orientations) exactly when the sorted sides of X are component-wise at most those of Y. So fix each box to its sorted orientation and always stand it on its longest side z.",
           "Sort all boxes lexicographically by their sorted sides. Now a box can only sit on boxes earlier in the list: dp[i] = z_i + max dp[j] over j &lt; i with x_j &le; x_i, y_j &le; y_i, z_j &le; z_i. The answer is the maximum dp[i]."],
    editorial=["If box X fits on box Y with some orientations, then sorting the sides of both keeps the component-wise comparison valid (the k-th smallest side of X is at most the k-th smallest side of Y, because a coordinate-wise dominance of one permutation over another implies dominance of the sorted versions). So the orientation question disappears: store every box with sorted sides <code>(x, y, z)</code>.",
               "A box's height contribution is maximised by using the largest side as the vertical one, and standing it that way never blocks anything: the placement rule is symmetric in the sides, so the chosen orientation only affects the height we gain. Hence we use the sorted orientation for every box in the tower and add the largest side <code>z</code>.",
               "Now the boxes form a partial order (component-wise <code>&le;</code>). Sorting lexicographically by (x, y, z) guarantees that any box that can sit on box i appears before it. Then it is a longest-chain DP with weights: <code>dp[i] = z_i + max(dp[j])</code> over earlier j that fit under the constraint. The answer is the largest <code>dp[i]</code>. This is O(n<sup>2</sup>) time and O(n) space, and it is the weighted analogue of the nested envelopes problem in three dimensions."],
    time="O(n^2)", space="O(n)",
    solution='''def maxStackHeight(cuboids):
    c = sorted(sorted(box) for box in cuboids)
    n = len(c)
    dp = [0] * n
    for i in range(n):
        a, b, h = c[i]
        best = 0
        for j in range(i):
            x, y, z = c[j]
            if x <= a and y <= b and z <= h and dp[j] > best:
                best = dp[j]
        dp[i] = best + h
    return max(dp)
''',
    tests=[[[[50, 45, 20], [95, 37, 53], [45, 23, 12]]], [[[7, 11, 17], [7, 17, 11], [11, 7, 17], [11, 17, 7], [17, 7, 11], [17, 11, 7]]],
           [[[38, 25, 45], [76, 35, 3]]], [[[1, 1, 1]]], [[[5, 5, 5], [5, 5, 5], [5, 5, 5]]], [[[10, 1, 1], [1, 10, 1], [1, 1, 10]]],
           [[[2, 3, 4], [3, 4, 5], [1, 1, 9], [6, 6, 6]]], [[[10000, 10000, 10000], [1, 1, 1]]],
           [[[3, 8, 2], [4, 9, 3], [5, 9, 4], [2, 2, 8], [6, 10, 7]]],
           [_cu1], [_cu2], [_cu3], [_cu4], [_cu5]],
)


def _b_cu(cuboids):
    n = len(cuboids)
    orient = [list(set(permutations(c))) for c in cuboids]
    memo = {}

    def go(mask, o):  # tower so far ends (on top) with orientation o; best extra height above it
        key = (mask, o)
        if key in memo:
            return memo[key]
        best = 0
        for j in range(n):
            if not mask >> j & 1:
                for p in orient[j]:
                    if p[0] <= o[0] and p[1] <= o[1] and p[2] <= o[2]:
                        best = max(best, p[2] + go(mask | 1 << j, p))
        memo[key] = best
        return best

    ans = 0
    for i in range(n):
        for p in orient[i]:
            ans = max(ans, p[2] + go(1 << i, p))
    return ans


def _g_cu(r):
    hi = r.choice([3, 5, 9])
    return [[[r.randint(1, hi) for _ in range(3)] for _ in range(r.randint(1, 5))]]


def _v_cu(tests):
    for t in tests:
        c = t["args"][0]
        assert 1 <= len(c) <= 500 and all(len(b) == 3 and all(1 <= v <= 10000 for v in b) for b in c)


CHECKS["stack-cuboids-max-height"] = (_b_cu, _g_cu, "exact")
VALIDATE["stack-cuboids-max-height"] = _v_cu


_r = rnd(9110)


def _pool_case(n, bad_frac, extra, span, noise):
    """An increasing array where a fraction of positions is corrupted; the pool holds the lost values plus noise."""
    base = sorted(_r.sample(range(1, span), n))
    arr = base[:]
    lost = []
    for i in range(n):
        if _r.random() < bad_frac:
            lost.append(base[i])
            arr[i] = _r.randint(1, span) if noise else base[i] - 1
    pool = lost[: 300 - extra] + [_r.randint(1, span) for _ in range(extra)]
    _r.shuffle(pool)
    return arr, pool[:300]


_mk1 = _pool_case(900, 0.15, 60, 10 ** 6, True)
_mk2 = _pool_case(1000, 0.2, 100, 10 ** 9, True)
_mk3 = _pool_case(700, 0.3, 0, 10 ** 6, False)
_mk4 = ([i * 3 + 1 for i in range(1000)], [_r.randint(1, 3000) for _ in range(300)])
_mk5 = ([3000 - i for i in range(300)], list(range(1, 3001, 10)))

add(
    id="min-replacements-to-make-increasing-from-pool", title="Make Array Strictly Increasing from a Pool", diff="Hard", topic=TOPIC, tier="extra",
    fn="minReplacementsFromPool", params=[("arr", "int[]"), ("pool", "int[]")], ret="int", cmp="exact",
    desc="<p>In one operation you choose an index <code>i</code> of <code>arr</code> and a position <code>j</code> of <code>pool</code>, and overwrite <code>arr[i]</code> with <code>pool[j]</code>. Pool values can be used any number of times, and the same index may be overwritten more than once (although that is never useful).</p><p>Return the minimum number of operations needed to make <code>arr</code> strictly increasing, or <code>-1</code> if that is impossible. For <code>arr = [1, 5, 3, 6, 7]</code> and <code>pool = [1, 3, 2, 4]</code> the answer is <code>1</code> (replace the <code>5</code> with <code>2</code>).</p>",
    constraints=["1 &le; arr.length &le; 1,000", "1 &le; pool.length &le; 300", "0 &le; arr[i], pool[j] &le; 10<sup>9</sup>"],
    hints=["Process the array from left to right. What is the only thing about the already processed prefix that matters for the future?",
           "Only the value of the last element of the prefix matters (it must stay smaller than the next one). Keep a map from 'last value' to 'fewest operations used so far'.",
           "For the next element x and each state (last, ops): keep x if x &gt; last (cost ops), or replace it with the smallest pool value strictly greater than last, found by binary search in the sorted pool (cost ops + 1). The map never has more than len(pool) + 1 states. If it becomes empty, return -1."],
    editorial=["Scan <code>arr</code> from left to right and keep <code>best</code>, a dictionary from the possible value of the last element of the processed prefix to the minimum number of replacements that achieves it. Initially the 'last value' is minus infinity with 0 operations.",
               "For the next element x, every state <code>(last, ops)</code> has up to two successors. If <code>x &gt; last</code> we may keep x: the new last value is x, cost unchanged. We may also replace x by the <em>smallest</em> pool value strictly greater than <code>last</code> (found with <code>bisect_right</code> on the sorted pool), at cost <code>ops + 1</code>. Choosing the smallest feasible pool value is optimal because a smaller last value can only make the future easier. When two paths reach the same last value, keep the smaller cost.",
               "Every state's last value is either the current original element or a pool value, so there are at most <code>len(pool) + 1</code> states per step. The total time is O(n &middot; m log m) with n = len(arr) and m = len(pool), and memory is O(m). If at some point no states remain, the array cannot be fixed and the answer is -1; otherwise it is the minimum cost over the final states."],
    time="O(n m log m)", space="O(m)",
    solution='''from bisect import bisect_right

def minReplacementsFromPool(arr, pool):
    vals = sorted(set(pool))
    best = {-1: 0}
    for x in arr:
        nxt = {}
        for last, ops in best.items():
            if x > last:
                if nxt.get(x, 10 ** 9) > ops:
                    nxt[x] = ops
            i = bisect_right(vals, last)
            if i < len(vals):
                v = vals[i]
                if nxt.get(v, 10 ** 9) > ops + 1:
                    nxt[v] = ops + 1
        if not nxt:
            return -1
        best = nxt
    return min(best.values())
''',
    tests=[[[1, 5, 3, 6, 7], [1, 3, 2, 4]], [[1, 5, 3, 6, 7], [4, 3, 1]], [[1, 5, 3, 6, 7], [1, 6, 3, 3]], [[1, 2, 3], [5]],
           [[5], [1]], [[3, 3, 3], [4, 5, 6]], [[10, 9, 8, 7], [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]], [[0, 0], [0]],
           [[4, 4, 4], [1, 2, 3, 4, 5, 6]], [[1000000000, 1], [1000000000, 5]], [[7, 1, 8, 2, 9], [3, 4, 5]],
           list(_mk1), list(_mk2), list(_mk3), list(_mk4), list(_mk5)],
)


def _b_mk(arr, pool):
    ps = sorted(set(pool))
    best = [None]

    def go(i, last, ops):
        if best[0] is not None and ops >= best[0]:
            return
        if i == len(arr):
            best[0] = ops
            return
        if arr[i] > last:
            go(i + 1, arr[i], ops)
        for v in ps:
            if v > last:
                go(i + 1, v, ops + 1)

    go(0, -1, 0)
    return -1 if best[0] is None else best[0]


def _v_mk(tests):
    for t in tests:
        a, pl = t["args"]
        assert 1 <= len(a) <= 1000 and 1 <= len(pl) <= 300
        assert all(0 <= x <= 10 ** 9 for x in a + pl)


CHECKS["min-replacements-to-make-increasing-from-pool"] = (
    _b_mk, lambda r: [gen_arr(r, 0, 9, 1, 7), gen_arr(r, 0, 9, 1, 4)], "exact")
VALIDATE["min-replacements-to-make-increasing-from-pool"] = _v_mk


_r = rnd(9111)
_bs1 = ([_r.randint(1, 100000) for _ in range(4000)], 500)
_bs2 = ([_r.randint(1, 3000) for _ in range(4500)], 20)
_bs3 = ([(i * 37) % 100000 + 1 for i in range(3500)], 4000)
_bs4 = (list(range(1, 3001)), 1)
_bs5 = ([_r.randint(1, 100000) for _ in range(3000)], 100000)

add(
    id="longest-increasing-subsequence-bounded-step", title="Longest Increasing Subsequence With Bounded Step", diff="Hard", topic=TOPIC, tier="extra",
    fn="lisBoundedStep", params=[("nums", "int[]"), ("k", "int")], ret="int", cmp="exact",
    desc="<p>Find the longest subsequence of <code>nums</code> that is strictly increasing <em>and</em> in which every two neighbouring chosen elements differ by at most <code>k</code>. In other words, for consecutive chosen values <code>u</code> then <code>v</code> we need <code>0 &lt; v - u &le; k</code>.</p><p>Return its length. For <code>nums = [4, 2, 1, 4, 3, 4, 5, 8, 15]</code> and <code>k = 3</code> the answer is <code>5</code> (<code>1, 3, 4, 5, 8</code>).</p>",
    constraints=["1 &le; nums.length &le; 5,000", "1 &le; nums[i] &le; 100,000", "1 &le; k &le; 100,000"],
    hints=["Let best[i] be the longest valid subsequence that ends exactly at index i. Which earlier values can precede nums[i]?",
           "A predecessor must have a value in the range [nums[i] - k, nums[i] - 1]. So best[i] = 1 + the largest best[j] among earlier indices whose value lies in that range. The direct scan is O(n<sup>2</sup>).",
           "Keep a structure indexed by <em>value</em> that stores the best length of a subsequence ending with that value, and supports 'maximum over a range of values' plus 'raise one entry'. A segment tree on the compressed values gives O(log n) per element."],
    editorial=["Plain LIS only needs 'the largest length among smaller values', a prefix maximum that a tails array or Fenwick tree answers. Here the allowed predecessors form a <em>window</em> of values <code>[x - k, x - 1]</code>, which is not a prefix, so we need a range maximum query.",
               "Index a segment tree by value (compressed to the sorted distinct values). The entry at value v stores the best length of a valid subsequence processed so far that ends with v. For each element x in order, query the maximum over values in <code>[x - k, x - 1]</code>, set <code>cur = 1 + that maximum</code>, and raise the entry of x to at least <code>cur</code>. Equal values do not interact because the query window excludes x itself, and since elements are processed left to right, everything in the tree comes from earlier indices.",
               "The answer is the largest <code>cur</code> seen. Time is O(n log n) with an iterative segment tree, memory O(n). The O(n<sup>2</sup>) double loop would be too slow for large inputs in an interview setting, which is why the range structure is the heart of the problem."],
    time="O(n log n)", space="O(n)",
    solution='''from bisect import bisect_left

def lisBoundedStep(nums, k):
    vals = sorted(set(nums))
    m = len(vals)
    tree = [0] * (2 * m)
    best = 0
    for x in nums:
        lo = bisect_left(vals, x - k) + m
        hi = bisect_left(vals, x) + m
        res = 0
        while lo < hi:
            if lo & 1:
                if tree[lo] > res:
                    res = tree[lo]
                lo += 1
            if hi & 1:
                hi -= 1
                if tree[hi] > res:
                    res = tree[hi]
            lo >>= 1
            hi >>= 1
        cur = res + 1
        p = bisect_left(vals, x) + m
        if cur > tree[p]:
            tree[p] = cur
            p >>= 1
            while p >= 1:
                v = max(tree[2 * p], tree[2 * p + 1])
                if tree[p] == v:
                    break
                tree[p] = v
                p >>= 1
        if cur > best:
            best = cur
    return best
''',
    tests=[[[4, 2, 1, 4, 3, 4, 5, 8, 15], 3], [[7, 4, 5, 1, 8, 12, 4, 7], 5], [[1, 5], 3], [[9], 1], [[1, 2, 3, 4, 5], 1],
           [[5, 4, 3, 2, 1], 100], [[3, 3, 3], 2], [[1, 3, 5, 7, 9, 11], 2], [[10, 1, 20, 2, 30, 3, 40], 10],
           [[1, 100000, 50000, 99999], 100000],
           [_bs1[0], _bs1[1]], [_bs2[0], _bs2[1]], [_bs3[0], _bs3[1]], [_bs4[0], _bs4[1]], [_bs5[0], _bs5[1]]],
)


def _b_bs(nums, k):
    best = 0
    for s in _subsets(nums):
        if len(s) > best and all(0 < y - x <= k for x, y in zip(s, s[1:])):
            best = len(s)
    return best


def _g_bs(r):
    return [[r.randint(1, r.choice([6, 12, 20])) for _ in range(r.randint(1, 11))], r.randint(1, 6)]


def _v_bs(tests):
    for t in tests:
        a, k = t["args"]
        assert 1 <= len(a) <= 6000 and all(1 <= x <= 100000 for x in a) and 1 <= k <= 100000


CHECKS["longest-increasing-subsequence-bounded-step"] = (_b_bs, _g_bs, "exact")
VALIDATE["longest-increasing-subsequence-bounded-step"] = _v_bs
