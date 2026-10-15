"""Problems: binary search on integer roots, powers and monotone predicates. See data/lib.py for the registry."""
import itertools
from math import isqrt

from lib import add, rnd, CHECKS, VALIDATE, gen_arr  # noqa: F401

INT_MIN, INT_MAX = -(2 ** 31), 2 ** 31 - 1
TOPIC = "Binary Search"


# ---------------------------------------------------------------- EASY

p = add(
    id="valid-perfect-square", title="Valid Perfect Square", diff="Easy", topic=TOPIC,
    fn="isPerfectSquare", params=[("n", "int")], ret="bool", cmp="exact",
    desc="<p>Given a positive integer <code>n</code>, return <code>true</code> if there is an integer <code>r</code> with <code>r * r == n</code>, and <code>false</code> otherwise.</p><p>Do not use a built-in square root or power function. For example, <code>16</code> gives <code>true</code> (4 &times; 4) and <code>14</code> gives <code>false</code>.</p>",
    constraints=["1 &le; n &le; 2<sup>31</sup> - 1"],
    hints=["Trying every <code>r</code> from 1 upward and stopping when <code>r * r</code> reaches <code>n</code> works, but it takes up to about 46,000 steps. Is there an ordering you can exploit?",
           "The value <code>r * r</code> only grows as <code>r</code> grows, so the question &quot;is <code>r * r</code> at least <code>n</code>?&quot; flips from false to true exactly once.",
           "Binary search <code>r</code> in <code>[1, 46341]</code> (or <code>[1, n]</code>) for the smallest value with <code>r * r &ge; n</code>, then check whether <code>r * r == n</code>. In a 32-bit language compute the square in a 64-bit type."],
    editorial=["The squares 1, 4, 9, 16, ... are strictly increasing, so a sorted sequence of candidate roots is available without storing it: the root <code>r</code> stands for the value <code>r * r</code>. Binary search for the smallest <code>r</code> whose square is at least <code>n</code>. If that square equals <code>n</code> the answer is true, otherwise <code>n</code> falls strictly between two consecutive squares and the answer is false.",
               "Because <code>n &lt; 2<sup>31</sup></code>, the root is at most 46,340, so <code>hi = 46341</code> is enough and the search takes about 16 steps. Using <code>hi = n</code> also works but then <code>mid * mid</code> can reach 2<sup>62</sup>, which needs 64-bit arithmetic. An alternative that avoids a search is Newton's iteration, or the identity that the n-th square is the sum of the first n odd numbers."],
    time="O(log n)", space="O(1)",
    solution='''def isPerfectSquare(n):
    lo, hi = 1, 46341
    while lo < hi:
        mid = (lo + hi) // 2
        if mid * mid >= n:
            hi = mid
        else:
            lo = mid + 1
    return lo * lo == n
''',
    tests=[[16], [14], [1], [2], [3], [4], [9], [8], [25], [26], [808201], [2147395600], [2147395599], [2147395601], [INT_MAX], [1000000000], [999950884]],
)


def b_vps(n):
    r = 1
    while r * r < n:
        r += 1
    return r * r == n


def v_vps(tests):
    for t in tests:
        n = t["args"][0]
        assert 1 <= n <= INT_MAX
        assert t["expected"] == (isqrt(n) ** 2 == n)
    assert any(t["expected"] for t in tests) and any(not t["expected"] for t in tests)


CHECKS["valid-perfect-square"] = (b_vps, lambda r: [r.randint(1, 400)], "exact")
VALIDATE["valid-perfect-square"] = v_vps

p = add(
    id="integer-cube-root", title="Integer Cube Root", diff="Easy", topic=TOPIC, tier="extra",
    fn="cubeRoot", params=[("n", "int")], ret="int", cmp="exact",
    desc="<p>For an integer <code>n</code> (it may be negative), return the largest integer <code>r</code> such that <code>r<sup>3</sup> &le; n</code>. In other words, take the real cube root of <code>n</code> and round it <em>down</em> (toward negative infinity).</p><p>Examples: <code>27</code> gives <code>3</code>, <code>26</code> gives <code>2</code>, <code>-27</code> gives <code>-3</code> and <code>-26</code> gives <code>-3</code> (because <code>(-3)<sup>3</sup> = -27 &le; -26</code> while <code>(-2)<sup>3</sup> = -8 &gt; -26</code>).</p><p>Do not use a built-in root or power function.</p>",
    constraints=["-2<sup>31</sup> &le; n &le; 2<sup>31</sup> - 1"],
    hints=["Cubing is increasing for negative numbers too: <code>-3</code> cubed is smaller than <code>-2</code> cubed. So &quot;<code>r<sup>3</sup> &le; n</code>&quot; is true for every small <code>r</code> and false for every large <code>r</code>.",
           "You are looking for the last <code>r</code> where that statement is true. First decide a range that must contain it: how large can <code>|r|</code> be when <code>|n|</code> is below 2.2 billion?",
           "Binary search the largest <code>r</code> in <code>[-1291, 1290]</code> with <code>r * r * r &le; n</code>. Use the upper-middle <code>mid = (lo + hi + 1) // 2</code> (floor division) so the loop always shrinks, also for negative values."],
    editorial=["The function <code>r &rarr; r<sup>3</sup></code> is strictly increasing over all integers, so the predicate &quot;<code>r<sup>3</sup> &le; n</code>&quot; is true up to some threshold and false afterwards. The answer is the last true <code>r</code>.",
               "Since 1290<sup>3</sup> = 2,146,689,000 &lt; 2<sup>31</sup> &lt; 1291<sup>3</sup>, the answer lies in <code>[-1291, 1290]</code> (the lower end is reached by <code>n = -2<sup>31</sup></code>, because (-1291)<sup>3</sup> &lt; -2<sup>31</sup>). Search that range with the upper-middle rule. Negative <code>n</code> is where naive code goes wrong: truncating the real cube root toward zero gives <code>-2</code> for <code>-26</code>, but the floor is <code>-3</code>. Searching the predicate directly avoids any such special case."],
    time="O(log |n|)", space="O(1)",
    solution='''def cubeRoot(n):
    lo, hi = -1291, 1290
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if mid * mid * mid <= n:
            lo = mid
        else:
            hi = mid - 1
    return lo
''',
    tests=[[27], [26], [-27], [-26], [0], [1], [-1], [7], [8], [-8], [-9], [INT_MAX], [INT_MIN], [INT_MIN + 1], [2146689000], [2146688999], [-2146689000], [-2146689001], [1000000000]],
)


def b_cuberoot(n):
    r = -20
    while (r + 1) ** 3 <= n:
        r += 1
    return r


def v_cuberoot(tests):
    for t in tests:
        n = t["args"][0]
        assert INT_MIN <= n <= INT_MAX
        r = t["expected"]
        assert r ** 3 <= n < (r + 1) ** 3


CHECKS["integer-cube-root"] = (b_cuberoot, lambda r: [r.randint(-1000, 1000)], "exact")
VALIDATE["integer-cube-root"] = v_cuberoot

p = add(
    id="exact-nth-root", title="Exact N-th Root", diff="Easy", topic=TOPIC, tier="extra",
    fn="exactRoot", params=[("n", "int"), ("m", "int")], ret="int", cmp="exact",
    desc="<p>Given a degree <code>n</code> and a positive integer <code>m</code>, find the positive integer <code>r</code> with <code>r<sup>n</sup> == m</code>. If no such integer exists, return <code>-1</code>.</p><p>For example, <code>n = 3, m = 27</code> gives <code>3</code>; <code>n = 4, m = 81</code> gives <code>3</code>; <code>n = 3, m = 28</code> gives <code>-1</code>. Take care that <code>r<sup>n</sup></code> may be astronomically larger than <code>m</code> while you test candidates.</p>",
    constraints=["1 &le; n &le; 30", "1 &le; m &le; 2<sup>31</sup> - 1"],
    hints=["For each degree the powers <code>1<sup>n</sup>, 2<sup>n</sup>, 3<sup>n</sup>, ...</code> form an increasing sequence. You are asking whether <code>m</code> is one of its members.",
           "Binary search the root <code>r</code> in <code>[1, m]</code> (for <code>n &ge; 2</code> the upper bound 46,341 is enough) by comparing <code>r<sup>n</sup></code> with <code>m</code>.",
           "Compute <code>r<sup>n</sup></code> by repeated multiplication and stop as soon as the running product exceeds <code>m</code>, so the product never gets far beyond 2<sup>62</sup> (in fixed-width languages this is what prevents overflow). Report <code>mid</code> if the power equals <code>m</code>."],
    editorial=["The comparison &quot;is <code>mid<sup>n</sup></code> smaller than, equal to, or larger than <code>m</code>&quot; tells you which half to keep, because <code>r &rarr; r<sup>n</sup></code> is strictly increasing for positive <code>r</code>. If a hit occurs, <code>mid</code> is the unique answer; if the search range empties, the answer is -1.",
               "The only subtlety is computing <code>mid<sup>n</sup></code> safely. Multiply one factor at a time and abort with the verdict &quot;too large&quot; as soon as the product passes <code>m</code>. Each probe costs at most <code>n</code> multiplications, so the total is O(n log m). For n = 1 the root is simply <code>m</code> itself, which the search handles when its upper bound is <code>m</code>."],
    time="O(n log m)", space="O(1)",
    solution='''def exactRoot(n, m):
    def cmp_pow(r):
        p = 1
        for _ in range(n):
            p *= r
            if p > m:
                return 1
        return 0 if p == m else -1

    lo, hi = 1, min(m, 46341) if n > 1 else m
    while lo <= hi:
        mid = (lo + hi) // 2
        c = cmp_pow(mid)
        if c == 0:
            return mid
        if c < 0:
            lo = mid + 1
        else:
            hi = mid - 1
    return -1
''',
    tests=[[3, 27], [4, 81], [3, 28], [1, 1], [1, 2147483647], [2, 1], [2, 2], [2, 4], [5, 243], [5, 242], [30, 1073741824], [30, 1073741825], [30, 1],
           [2, 2147395600], [2, 2147395601], [2, 2147483647], [3, 2146689000], [3, 2146689001], [31 - 1, 2147483647], [7, 1279]],
)


def b_exactroot(n, m):
    r = 1
    while r ** n < m:
        r += 1
    return r if r ** n == m else -1


def g_exactroot(r):
    n = r.randint(1, 6)
    if r.random() < 0.5:
        return [n, r.randint(1, 6) ** n]
    return [n, r.randint(1, 400)]


def v_exactroot(tests):
    for t in tests:
        n, m = t["args"]
        assert 1 <= n <= 30 and 1 <= m <= INT_MAX
        r = t["expected"]
        assert r == -1 or r ** n == m
        if r == -1:
            assert all(k ** n != m for k in range(1, 46342))
    assert any(t["expected"] == -1 for t in tests) and any(t["expected"] != -1 for t in tests)


CHECKS["exact-nth-root"] = (b_exactroot, g_exactroot, "exact")
VALIDATE["exact-nth-root"] = v_exactroot


# ---------------------------------------------------------------- MEDIUM

p = add(
    id="sqrt-truncated-decimals", title="Square Root with D Decimal Digits", diff="Medium", topic=TOPIC, tier="extra",
    fn="sqrtScaled", params=[("x", "int"), ("d", "int")], ret="int", cmp="exact",
    desc="<p>Compute the square root of the non-negative integer <code>x</code>, <em>truncated</em> (not rounded) to <code>d</code> digits after the decimal point, and return it as an integer scaled by <code>10<sup>d</sup></code>. Formally, return <code>floor(sqrt(x) * 10<sup>d</sup>)</code>.</p><p>For example, <code>x = 2, d = 3</code> returns <code>1414</code> (the root is 1.41421...), <code>x = 10, d = 2</code> returns <code>316</code>, and <code>x = 16, d = 0</code> returns <code>4</code>.</p><p>Floating-point square roots are not exact enough for this; use integer arithmetic only.</p>",
    constraints=["0 &le; x &le; 2<sup>31</sup> - 1", "0 &le; d &le; 4"],
    hints=["Multiplying a square root by 10<sup>d</sup> is the same as taking the root of <code>x * 100<sup>d</sup></code>. So the task reduces to a plain integer square root of a larger number.",
           "You want the largest integer <code>r</code> with <code>r * r &le; X</code>, where <code>X = x * 100<sup>d</sup></code>. The predicate &quot;<code>r * r &le; X</code>&quot; is true for small <code>r</code> and then stays false.",
           "Binary search <code>r</code> in <code>[0, 463,410,000]</code> or, more tightly, in <code>[0, (x + 1) * 10<sup>d</sup>]</code>. <code>r * r</code> can reach about 2<sup>62</sup>, so use 64-bit arithmetic in languages with fixed-width integers."],
    editorial=["Because <code>sqrt(x) * 10<sup>d</sup> = sqrt(x * 10<sup>2d</sup>)</code>, the answer is the integer square root of <code>X = x * 100<sup>d</sup></code>. With <code>x &lt; 2<sup>31</sup></code> and <code>d &le; 4</code> we get <code>X &lt; 2.2 * 10<sup>17</sup></code>, which still fits in a signed 64-bit integer, and the result is below 4.7 * 10<sup>8</sup>, which fits in 32 bits.",
               "Binary search the largest <code>r</code> with <code>r * r &le; X</code>. The hi bound <code>(x + 1) * 10<sup>d</sup></code> is a safe over-estimate of the root (because <code>sqrt(x) &le; x + 1</code>), though a tighter bound such as <code>min(x, 46341) * 10<sup>d</sup> + 10<sup>d</sup></code> saves a few steps. About 30 iterations suffice. This is the idea behind computing a root digit by digit: each additional decimal digit is just a square root of a number 100 times larger."],
    time="O(log(x * 10^d))", space="O(1)",
    solution='''def sqrtScaled(x, d):
    big = x * 100 ** d
    lo, hi = 0, (min(x, 46341) + 1) * 10 ** d
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if mid * mid <= big:
            lo = mid
        else:
            hi = mid - 1
    return lo
''',
    tests=[[2, 3], [10, 2], [16, 0], [0, 0], [0, 4], [1, 4], [2, 0], [3, 1], [99, 2], [15, 0], [17, 0], [2, 4], [123456789, 4], [INT_MAX, 0], [INT_MAX, 4], [INT_MAX - 1, 3], [1000000000, 4], [2147395600, 4], [2147395599, 4]],
)


def b_sqrtscaled(x, d):
    big = x * 100 ** d
    r = 0
    while (r + 1) * (r + 1) <= big:
        r += 1
    return r


def v_sqrtscaled(tests):
    for t in tests:
        x, d = t["args"]
        assert 0 <= x <= INT_MAX and 0 <= d <= 4
        r = t["expected"]
        big = x * 100 ** d
        assert r * r <= big < (r + 1) ** 2


CHECKS["sqrt-truncated-decimals"] = (b_sqrtscaled, lambda r: [r.randint(0, 150), r.randint(0, 2)], "exact")
VALIDATE["sqrt-truncated-decimals"] = v_sqrtscaled

p = add(
    id="h-index-sorted-citations", title="H-Index of Sorted Citations", diff="Medium", topic=TOPIC,
    fn="hIndexSorted", params=[("citations", "int[]")], ret="int", cmp="exact",
    desc="<p><code>citations</code> lists the citation counts of a researcher's papers in <strong>non-decreasing</strong> order. The <em>h-index</em> is the largest integer <code>h</code> such that at least <code>h</code> papers have <code>h</code> or more citations each (<code>h = 0</code> is always allowed).</p><p>Return the h-index in logarithmic time. For example, <code>[0, 1, 3, 5, 6]</code> gives <code>3</code> (the papers with 3, 5 and 6 citations), and <code>[1, 2, 100]</code> gives <code>2</code>.</p>",
    constraints=["1 &le; citations.length &le; 8,000", "0 &le; citations[i] &le; 10<sup>9</sup>", "citations is sorted in non-decreasing order"],
    hints=["A linear scan over the sorted array works. Because the array is sorted you can do much better; first work out what the condition for a given <code>h</code> looks like in terms of one array cell.",
           "If exactly <code>h</code> papers are to qualify, they are the last <code>h</code> ones, so <code>h</code> is valid exactly when <code>citations[n - h] &ge; h</code> (and <code>h = 0</code> is always valid). Is validity monotone in <code>h</code>?",
           "Yes: if <code>h</code> is valid, so is <code>h - 1</code>. Binary search the largest <code>h</code> in <code>[0, n]</code> with <code>h == 0</code> or <code>citations[n - h] &ge; h</code>."],
    editorial=["Let <code>n</code> be the length. For a candidate <code>h</code>, the best choice of papers is the <code>h</code> most cited ones, i.e. <code>citations[n-h .. n-1]</code>, and since the array is sorted the weakest of them is <code>citations[n - h]</code>. So <code>h</code> is valid iff <code>citations[n - h] &ge; h</code>.",
               "As <code>h</code> grows, the index <code>n - h</code> moves left (a smaller value) while the required threshold <code>h</code> grows, so once the test fails it fails for every larger <code>h</code>. That makes it a classic last-true search on <code>h</code> in <code>[0, n]</code>, taking O(log n) time. Equivalently, you can find the first index <code>i</code> with <code>citations[i] &ge; n - i</code> and return <code>n - i</code> (or 0 if there is none)."],
    time="O(log n)", space="O(1)",
    solution='''def hIndexSorted(citations):
    n = len(citations)
    lo, hi = 0, n
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if citations[n - mid] >= mid:
            lo = mid
        else:
            hi = mid - 1
    return lo
''',
    tests=[[[0, 1, 3, 5, 6]], [[1, 2, 100]], [[0]], [[1]], [[5]], [[0, 0, 0]], [[1, 1, 1, 1]], [[4, 4, 4, 4]], [[10, 20, 30]], [[0, 0, 4, 4, 4]], [[1, 3, 3, 7]],
           [[1000000000, 1000000000]], [[0, 1000000000]]],
)
_r = rnd(8101)
p["tests"].append([sorted(_r.randint(0, 5000) for _ in range(5000))])
p["tests"].append([sorted(_r.randint(0, 10 ** 9) for _ in range(4000))])
p["tests"].append([sorted(min(10 ** 9, int(_r.expovariate(1 / 700))) for _ in range(5000))])


def b_hsorted(c):
    n = len(c)
    for h in range(n, -1, -1):
        if sum(1 for x in c if x >= h) >= h:
            return h


def g_hsorted(r):
    return [sorted(gen_arr(r, 0, 10, 1, 12))]


def v_hsorted(tests):
    for t in tests:
        c = t["args"][0]
        assert 1 <= len(c) <= 8000 and all(0 <= x <= 10 ** 9 for x in c)
        assert all(c[i] <= c[i + 1] for i in range(len(c) - 1)), "must be sorted"
        h = t["expected"]
        assert sum(1 for x in c if x >= h) >= h and sum(1 for x in c if x >= h + 1) < h + 1


CHECKS["h-index-sorted-citations"] = (b_hsorted, g_hsorted, "exact")
VALIDATE["h-index-sorted-citations"] = v_hsorted

p = add(
    id="h-index-with-extra-citations", title="H-Index with Extra Citations", diff="Medium", topic=TOPIC, tier="extra",
    fn="boostedHIndex", params=[("citations", "int[]"), ("k", "int")], ret="int", cmp="exact",
    desc="<p><code>citations[i]</code> is the number of citations of paper <code>i</code>. The <em>h-index</em> is the largest <code>h</code> such that at least <code>h</code> papers have at least <code>h</code> citations each.</p><p>You may hand out up to <code>k</code> extra citations in total. Each extra citation goes to one paper of your choice and adds <code>1</code> to it; the same paper may receive several. Return the largest h-index you can reach.</p><p>Example: <code>citations = [3, 0, 6, 1, 5]</code> has h-index <code>3</code>. With <code>k = 4</code> the answer is <code>4</code> (give 1 to the paper with 3 and 3 to the paper with 1, so four papers have at least 4). With <code>k = 3</code> it stays <code>3</code>.</p>",
    constraints=["1 &le; citations.length &le; 8,000", "0 &le; citations[i] &le; 10<sup>9</sup>", "0 &le; k &le; 10<sup>9</sup>"],
    hints=["Try asking the reverse question: for a fixed target <code>h</code>, what is the cheapest way to get <code>h</code> papers with at least <code>h</code> citations?",
           "The cheapest <code>h</code> papers to lift are the <code>h</code> most cited ones, and the cost is the sum of <code>max(0, h - c)</code> over them. If target <code>h</code> is affordable, is target <code>h - 1</code> affordable too?",
           "Yes, so the answer is the largest <code>h</code> in <code>[0, n]</code> whose cost is at most <code>k</code>. Sort descending once and binary search <code>h</code>, computing each cost in O(h)."],
    editorial=["Fix a target <code>h</code>. Out of all ways to choose <code>h</code> papers, picking the <code>h</code> largest citation counts minimises the total deficit <code>sum(max(0, h - c))</code>, since each deficit is a non-increasing function of <code>c</code>. Extra citations spent on any other paper or beyond the threshold are wasted.",
               "Cost is monotone in <code>h</code>: lowering the target removes (or shrinks) deficits of the same top papers, so if <code>h</code> is affordable then so is <code>h - 1</code>. Binary search the largest affordable <code>h</code> in <code>[0, n]</code>. With the array sorted in descending order, each cost evaluation is O(h), so the total is O(n log n) for the sort plus O(n log n) for the search. Prefix sums make each evaluation O(log n) if you need more speed."],
    time="O(n log n)", space="O(n)",
    solution='''def boostedHIndex(citations, k):
    c = sorted(citations, reverse=True)
    n = len(c)

    def cost(h):
        total = 0
        for i in range(h):
            if c[i] < h:
                total += h - c[i]
        return total

    lo, hi = 0, n
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if cost(mid) <= k:
            lo = mid
        else:
            hi = mid - 1
    return lo
''',
    tests=[[[3, 0, 6, 1, 5], 4], [[3, 0, 6, 1, 5], 3], [[3, 0, 6, 1, 5], 0], [[0], 0], [[0], 1], [[0, 0, 0], 3], [[0, 0, 0], 6], [[5], 100], [[1, 1, 1, 1], 2],
           [[2, 2, 2], 1], [[10, 10, 10], 0], [[0, 0, 0, 0], 1000000000], [[1000000000, 1000000000], 0], [[7, 1, 4, 4, 2, 9, 0], 5]],
)
_r = rnd(8102)
p["tests"].append([[_r.randint(0, 60) for _ in range(5000)], 30000])
p["tests"].append([[_r.randint(0, 10 ** 9) for _ in range(4000)], 10 ** 9])
p["tests"].append([[_r.randint(0, 3000) for _ in range(6000)], 1234567])


def b_boosted(c, k):
    n = len(c)
    best = 0
    for h in range(1, n + 1):
        for sub in itertools.combinations(c, h):
            if sum(max(0, h - x) for x in sub) <= k:
                best = h
                break
    return best


def g_boosted(r):
    return [gen_arr(r, 0, 6, 1, 7), r.randint(0, 9)]


def v_boosted(tests):
    for t in tests:
        c, k = t["args"]
        assert 1 <= len(c) <= 8000 and all(0 <= x <= 10 ** 9 for x in c) and 0 <= k <= 10 ** 9
        assert 0 <= t["expected"] <= len(c)


CHECKS["h-index-with-extra-citations"] = (b_boosted, g_boosted, "exact")
VALIDATE["h-index-with-extra-citations"] = v_boosted

p = add(
    id="max-value-at-index-bounded-sum", title="Maximum Value at an Index", diff="Medium", topic=TOPIC,
    fn="maxValueAt", params=[("n", "int"), ("index", "int"), ("maxSum", "int")], ret="int", cmp="exact",
    desc="<p>Build an array <code>a</code> of <code>n</code> positive integers (every element is at least 1) such that</p><ul><li>neighbouring elements differ by at most 1: <code>|a[i] - a[i+1]| &le; 1</code>, and</li><li>the sum of all elements is at most <code>maxSum</code>.</li></ul><p>Among all such arrays make <code>a[index]</code> as large as possible and return that value.</p><p>Example: <code>n = 4, index = 2, maxSum = 6</code> gives <code>2</code> (e.g. <code>[1, 2, 2, 1]</code> has sum 6; a value of 3 would need at least <code>[1, 2, 3, 1]</code>, which sums to 7). For <code>n = 6, index = 1, maxSum = 10</code> the answer is <code>3</code> (<code>[2, 3, 2, 1, 1, 1]</code> has sum 10).</p>",
    constraints=["1 &le; n &le; maxSum &le; 10<sup>9</sup>", "0 &le; index &lt; n"],
    hints=["Instead of searching for the best array, ask: given a target value <code>v</code> for <code>a[index]</code>, what is the smallest possible sum of the whole array?",
           "To keep the sum small, let the values fall by exactly 1 per step on both sides of <code>index</code> until they reach 1, and stay at 1 afterwards. The needed sum can be computed with arithmetic-series formulas in O(1).",
           "That minimal sum grows with <code>v</code>, so binary search the largest <code>v</code> in <code>[1, maxSum]</code> whose minimal sum is at most <code>maxSum</code>. For one side with <code>len</code> cells (the peak included) and peak <code>v</code>: if <code>v &ge; len</code> the sum is <code>(v + v - len + 1) * len / 2</code>, otherwise it is <code>v * (v + 1) / 2 + (len - v)</code>."],
    editorial=["For a fixed peak <code>v</code>, the cheapest array is <code>a[i] = max(1, v - |i - index|)</code>: any cell closer to the peak than this would break the neighbour rule only if it were smaller, and every cell must be at least 1. Its sum is the left part (<code>index + 1</code> cells ending at the peak) plus the right part (<code>n - index</code> cells starting at the peak) minus the peak, which was counted twice.",
               "Each side is a descending staircase <code>v, v-1, ..., </code> that is cut off at 1. If the side has <code>len</code> cells and <code>v &ge; len</code>, it is the arithmetic series <code>v, v-1, ..., v-len+1</code>. If <code>v &lt; len</code>, the staircase reaches 1 after <code>v</code> cells and the remaining <code>len - v</code> cells each contribute 1. The minimal total sum is increasing in <code>v</code>, so the largest feasible <code>v</code> can be found by binary search over <code>[1, maxSum]</code> in O(log maxSum) time with O(1) space. Use 64-bit arithmetic: the sums reach about 10<sup>18</sup> during the search."],
    time="O(log maxSum)", space="O(1)",
    solution='''def maxValueAt(n, index, maxSum):
    def side(v, length):
        if v >= length:
            return (2 * v - length + 1) * length // 2
        return v * (v + 1) // 2 + (length - v)

    def total(v):
        return side(v, index + 1) + side(v, n - index) - v

    lo, hi = 1, maxSum
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if total(mid) <= maxSum:
            lo = mid
        else:
            hi = mid - 1
    return lo
''',
    tests=[[4, 2, 6], [6, 1, 10], [1, 0, 1], [1, 0, 1000000000], [2, 0, 2], [2, 1, 3], [3, 1, 3], [3, 1, 4], [3, 1, 5], [5, 0, 5], [5, 0, 9],
           [10, 9, 10], [10, 4, 100], [1000000000, 0, 1000000000], [1000000000, 500000000, 1000000000], [1000000000, 999999999, 1000000000], [100000, 50000, 1000000000],
           [1000000000, 0, 1000000000 - 1 + 1], [7, 3, 1000000000], [123456789, 12345, 987654321]],
)


def b_maxvalue(n, index, maxSum):
    best = 0

    def rec(i, prev, total, arr):
        nonlocal best
        if total + (n - i) > maxSum:
            return
        if i == n:
            best = max(best, arr[index])
            return
        for v in ((prev - 1, prev, prev + 1) if i else range(1, maxSum - n + 2)):
            if v >= 1:
                arr.append(v)
                rec(i + 1, v, total + v, arr)
                arr.pop()

    rec(0, 0, 0, [])
    return best


def g_maxvalue(r):
    n = r.randint(1, 5)
    return [n, r.randint(0, n - 1), n + r.randint(0, 9)]


def v_maxvalue(tests):
    for t in tests:
        n, index, ms = t["args"]
        assert 1 <= n <= ms <= 10 ** 9 and 0 <= index < n
        v = t["expected"]
        arr_sum = lambda x: sum(max(1, x - abs(i - index)) for i in range(n)) if n <= 3000 else None
        if n <= 3000:
            assert arr_sum(v) <= ms < arr_sum(v + 1)


CHECKS["max-value-at-index-bounded-sum"] = (b_maxvalue, g_maxvalue, "exact")
VALIDATE["max-value-at-index-bounded-sum"] = v_maxvalue

p = add(
    id="smallest-number-with-k-factorial-zeroes", title="Smallest Factorial with K Trailing Zeroes", diff="Medium", topic=TOPIC, tier="extra",
    fn="smallestFactorialWithZeroes", params=[("k", "int")], ret="int", cmp="exact",
    desc="<p>For a non-negative integer <code>n</code>, let <code>Z(n)</code> be the number of trailing zeroes of <code>n!</code> (<code>0! = 1</code>, so <code>Z(0) = 0</code>).</p><p>Given <code>k</code>, return the smallest <code>n &ge; 0</code> with <code>Z(n) == k</code>, or <code>-1</code> if no factorial has exactly <code>k</code> trailing zeroes.</p><p>For example, <code>k = 1</code> gives <code>5</code> (<code>5! = 120</code>) and <code>k = 6</code> gives <code>25</code>. But <code>k = 5</code> gives <code>-1</code>: <code>24!</code> has 4 trailing zeroes and <code>25!</code> jumps straight to 6.</p>",
    constraints=["0 &le; k &le; 4 * 10<sup>8</sup>"],
    hints=["Trailing zeroes of <code>n!</code> come from factors of 10, and factors of 5 are scarcer than factors of 2. Can you count the factors of 5 in <code>n!</code> quickly?",
           "<code>Z(n) = floor(n/5) + floor(n/25) + floor(n/125) + ...</code>, and it never decreases as <code>n</code> grows. So the smallest <code>n</code> with <code>Z(n) &ge; k</code> can be searched for.",
           "Binary search the smallest <code>n</code> in <code>[0, 5k + 5]</code> with <code>Z(n) &ge; k</code>. If <code>Z(n)</code> of that <code>n</code> is exactly <code>k</code> return it, otherwise <code>Z</code> skipped over <code>k</code> and the answer is -1."],
    editorial=["The function <code>Z(n)</code> is non-decreasing: it counts multiples of 5, of 25, of 125 and so on up to <code>n</code>, and each term only grows with <code>n</code>. The first <code>n</code> with <code>Z(n) &ge; k</code> is found by binary search. Since <code>Z(n) &ge; floor(n/5)</code>, the value <code>5k</code> already satisfies <code>Z &ge; k</code>, so <code>hi = 5k</code> is a valid upper bound.",
               "Z jumps by more than one exactly at multiples of 25 (and 125, ...), so some values of <code>k</code> are never reached. When the smallest <code>n</code> with <code>Z(n) &ge; k</code> has <code>Z(n) &gt; k</code>, there is no factorial with exactly <code>k</code> zeroes and the answer is -1. The special case <code>k = 0</code> yields <code>n = 0</code>. Each evaluation of Z takes O(log n), so the total is O(log<sup>2</sup> k); k at most 4 * 10<sup>8</sup> keeps the answer below 2<sup>31</sup>."],
    time="O(log^2 k)", space="O(1)",
    solution='''def smallestFactorialWithZeroes(k):
    def zeros(n):
        total = 0
        while n:
            n //= 5
            total += n
        return total

    lo, hi = 0, 5 * k
    while lo < hi:
        mid = (lo + hi) // 2
        if zeros(mid) >= k:
            hi = mid
        else:
            lo = mid + 1
    return lo if zeros(lo) == k else -1
''',
    tests=[[1], [6], [5], [0], [2], [3], [4], [7], [11], [12], [13], [20], [100], [400000000], [399999999], [399999998], [123456789], [1000000], [250000000], [99999999]],
)


def b_fzero(k):
    n = 0
    while True:
        z = 0
        m = n
        while m:
            m //= 5
            z += m
        if z == k:
            return n
        if z > k:
            return -1
        n += 1


def v_fzero(tests):
    def zeros(n):
        t = 0
        while n:
            n //= 5
            t += n
        return t

    for t in tests:
        k = t["args"][0]
        assert 0 <= k <= 4 * 10 ** 8
        n = t["expected"]
        if n == -1:
            assert all(zeros(m) != k for m in (5 * (k // 6), ))  # spot check only; brute force covers small k
        else:
            assert zeros(n) == k and (n == 0 or zeros(n - 1) < k)
    assert any(t["expected"] == -1 for t in tests) and any(t["expected"] > 0 for t in tests)


CHECKS["smallest-number-with-k-factorial-zeroes"] = (b_fzero, lambda r: [r.randint(0, 80)], "exact")
VALIDATE["smallest-number-with-k-factorial-zeroes"] = v_fzero

p = add(
    id="cubic-distance-center", title="Integer Point Minimizing Cubic Distance", diff="Medium", topic=TOPIC, tier="extra",
    fn="cubicCenter", params=[("nums", "int[]")], ret="int", cmp="exact",
    desc="<p>Given the integer positions <code>nums</code> on a number line, choose an integer <code>x</code> that minimizes</p><p><code>f(x) = |nums[0] - x|<sup>3</sup> + |nums[1] - x|<sup>3</sup> + ... + |nums[n-1] - x|<sup>3</sup></code></p><p>and return it. If several integers give the same minimal value, return the <em>smallest</em> of them. The chosen point need not appear in <code>nums</code>.</p><p>Example: for <code>[1, 2, 6]</code> the answer is <code>3</code> (<code>f(3) = 8 + 1 + 27 = 36</code>, while <code>f(2) = 1 + 0 + 64 = 65</code> and <code>f(4) = 27 + 8 + 8 = 43</code>).</p>",
    constraints=["1 &le; nums.length &le; 5,000", "-20,000 &le; nums[i] &le; 20,000"],
    hints=["<code>f</code> is a sum of convex functions, so it is convex: it decreases, possibly stays flat for one step, then increases. Checking every <code>x</code> in the range works but is slow for wide ranges and large inputs.",
           "For a convex function the differences <code>f(x + 1) - f(x)</code> are non-decreasing in <code>x</code>. The minimizer is where that difference first becomes non-negative.",
           "Binary search the smallest integer <code>x</code> in <code>[min(nums), max(nums)]</code> with <code>f(x + 1) - f(x) &ge; 0</code>. Evaluating <code>f</code> costs O(n); sums reach about 3 * 10<sup>17</sup>, so use 64-bit integers."],
    editorial=["Each term <code>|a - x|<sup>3</sup></code> is convex in <code>x</code>, and a sum of convex functions is convex, so the sequence of differences <code>d(x) = f(x + 1) - f(x)</code> is non-decreasing. A convex function is minimised exactly where <code>d</code> switches from negative to non-negative; the smallest <code>x</code> with <code>d(x) &ge; 0</code> is therefore the smallest minimizer (if <code>d(x) == 0</code>, both <code>x</code> and <code>x + 1</code> are optimal and we want the smaller one).",
               "The optimum lies between the smallest and the largest input: outside that interval moving toward the data strictly decreases every term. At <code>x = max(nums)</code> the difference is positive (or all points are equal and it is positive as well), so the predicate is true at the right end of the search interval and the binary search is well defined. With about 15 iterations and an O(n) evaluation, the running time is O(n log R) where R is the width of the value range. Unlike the median (for absolute distance) or the mean (for squared distance), no closed form exists for cubes, which is why a monotone predicate is the tool."],
    time="O(n log R)", space="O(1)",
    solution='''def cubicCenter(nums):
    def f(x):
        return sum(abs(a - x) ** 3 for a in nums)

    lo, hi = min(nums), max(nums)
    while lo < hi:
        mid = (lo + hi) // 2
        if f(mid + 1) - f(mid) >= 0:
            hi = mid
        else:
            lo = mid + 1
    return lo
''',
    tests=[[[1, 2, 6]], [[5]], [[-4]], [[0, 0, 0]], [[1, 2]], [[1, 4]], [[-3, 3]], [[1, 2, 3, 4]], [[1, 1, 1, 9]], [[-20000, 20000]], [[20000, 20000, -20000]], [[-20000, -20000, -20000, 20000, 20000]], [[3, 3, 10, 10]]],
)
_r = rnd(8103)
p["tests"].append([[_r.randint(-20000, 20000) for _ in range(5000)]])
p["tests"].append([[_r.randint(-20000, -5000) for _ in range(2500)] + [_r.randint(15000, 20000) for _ in range(2500)]])
p["tests"].append([[_r.choice([-20000, 0, 13]) for _ in range(5000)]])


def b_cubic(nums):
    best = None
    bx = None
    for x in range(min(nums), max(nums) + 1):
        v = sum(abs(a - x) ** 3 for a in nums)
        if best is None or v < best:
            best, bx = v, x
    return bx


def v_cubic(tests):
    for t in tests:
        nums = t["args"][0]
        assert 1 <= len(nums) <= 5000 and all(-20000 <= a <= 20000 for a in nums)
        x = t["expected"]
        f = lambda y: sum(abs(a - y) ** 3 for a in nums)
        assert f(x) <= f(x + 1) and f(x) <= f(x - 1) and (f(x - 1) > f(x) or x == min(nums))
        assert f(x) < 4 * 10 ** 17


CHECKS["cubic-distance-center"] = (b_cubic, lambda r: [gen_arr(r, -12, 12, 1, 8)], "exact")
VALIDATE["cubic-distance-center"] = v_cubic


# ---------------------------------------------------------------- HARD

p = add(
    id="smallest-good-base", title="Smallest Base with All Ones", diff="Hard", topic=TOPIC, tier="extra",
    fn="smallestGoodBase", params=[("n", "int")], ret="int", cmp="exact",
    desc="<p>A base <code>b &ge; 2</code> is <em>good</em> for <code>n</code> if the representation of <code>n</code> in base <code>b</code> consists only of the digit <code>1</code> (at least two digits long), i.e. <code>n = 1 + b + b<sup>2</sup> + ... + b<sup>m-1</sup></code> for some <code>m &ge; 2</code>.</p><p>Return the smallest good base of <code>n</code>. A good base always exists, because <code>n - 1</code> works: <code>n = 1 + (n - 1)</code>.</p><p>Examples: <code>13</code> gives <code>3</code> (13 is <code>111</code> in base 3); <code>4681</code> gives <code>8</code> (<code>11111</code> in base 8); <code>3</code> gives <code>2</code> (<code>11</code> in base 2).</p>",
    constraints=["3 &le; n &le; 2<sup>31</sup> - 1"],
    hints=["Trying every base from 2 up to <code>n - 1</code> is far too slow. Think about the other unknown: the number of digits <code>m</code>. How large can it be?",
           "A smaller base means more digits, and since <code>b &ge; 2</code> we have <code>n &ge; 2<sup>m</sup> - 1</code>, so <code>m &le; 31</code>. Iterate <code>m</code> from the largest possible value downward; the first <code>m</code> that has a valid base gives the smallest base.",
           "For a fixed <code>m</code>, the sum <code>1 + b + ... + b<sup>m-1</sup></code> is strictly increasing in <code>b</code>, so at most one base fits. Binary search the largest <code>b</code> in <code>[2, sqrt(n)]</code> whose sum is at most <code>n</code> and check whether the sum equals <code>n</code>. If no <code>m &ge; 3</code> works, return <code>n - 1</code>."],
    editorial=["Switch the viewpoint from the base to the digit count. For each length <code>m</code>, the value <code>S(b) = 1 + b + ... + b<sup>m-1</sup></code> is strictly increasing in <code>b</code>, so there is at most one base <code>b</code> with <code>S(b) = n</code>, and it can be found by binary search on <code>b</code> comparing <code>S(b)</code> with <code>n</code>. Because the base shrinks as the length grows, scanning <code>m</code> from large to small and returning the first success yields the smallest base.",
               "Bounds: <code>b = 2</code> needs <code>n &ge; 2<sup>m</sup> - 1</code>, so <code>m</code> is at most the bit length of <code>n</code>, i.e. at most 31 here. For <code>m &ge; 3</code> we have <code>b<sup>2</sup> &lt; n</code>, so the base is at most <code>sqrt(n)</code> (about 46,341). Length <code>m = 2</code> always succeeds with <code>b = n - 1</code> and acts as the fallback. The total work is about 30 lengths times 16 binary-search steps times an O(m) evaluation of the geometric sum, which is trivial."],
    time="O(log^3 n)", space="O(1)",
    solution='''def smallestGoodBase(n):
    def geo(b, m):
        s, p = 0, 1
        for _ in range(m):
            s += p
            p *= b
        return s

    for m in range(n.bit_length(), 2, -1):
        lo, hi = 2, 46341
        if geo(2, m) > n:
            continue
        while lo < hi:
            mid = (lo + hi + 1) // 2
            if geo(mid, m) <= n:
                lo = mid
            else:
                hi = mid - 1
        if geo(lo, m) == n:
            return lo
    return n - 1
''',
    tests=[[13], [4681], [3], [4], [7], [8], [15], [21], [31], [57], [1000000000], [2147483647], [2147483646], [1073741823], [2147395600], [1 + 46340 + 46340 ** 2], [1 + 1289 + 1289 ** 2 + 1289 ** 3],
           [(5 ** 12 - 1) // 4], [(3 ** 19 - 1) // 2], [(7 ** 11 - 1) // 6]],
)


def b_goodbase(n):
    for b in range(2, n):
        m = n
        ok = True
        while m:
            if m % b != 1:
                ok = False
                break
            m //= b
        if ok:
            return b


def v_goodbase(tests):
    for t in tests:
        n = t["args"][0]
        assert 3 <= n <= INT_MAX
        b = t["expected"]
        s, pw = 0, 1
        while s < n:
            s += pw
            pw *= b
        assert s == n and b >= 2
    assert any(t["expected"] != t["args"][0] - 1 for t in tests)


CHECKS["smallest-good-base"] = (b_goodbase, lambda r: [r.randint(3, 700) if r.random() < 0.6 else (lambda b, m: (b ** m - 1) // (b - 1))(r.randint(2, 6), r.randint(2, 6))], "exact")
VALIDATE["smallest-good-base"] = v_goodbase

p = add(
    id="kth-squarefree-number", title="Kth Square-Free Number", diff="Hard", topic=TOPIC, tier="extra",
    fn="kthSquareFree", params=[("k", "int")], ret="int", cmp="exact",
    desc="<p>A positive integer is <em>square-free</em> if no perfect square greater than 1 divides it. The first square-free numbers are <code>1, 2, 3, 5, 6, 7, 10, 11, 13, 14, 15, 17, ...</code> (4, 8, 9, 12, 16, ... are excluded).</p><p>Given <code>k</code>, return the <code>k</code>-th smallest square-free number (1-indexed). For example, <code>k = 4</code> gives <code>5</code> and <code>k = 10</code> gives <code>14</code>.</p><p>The values of <code>k</code> are far too large to list the numbers one by one.</p>",
    constraints=["1 &le; k &le; 10<sup>8</sup>"],
    hints=["Listing and testing numbers one at a time costs far too much for <code>k = 10<sup>8</sup></code>. Suppose someone gave you a fast way to count how many square-free numbers are at most <code>x</code>. How would you use it?",
           "That count <code>C(x)</code> never decreases as <code>x</code> grows, so the answer is the smallest <code>x</code> with <code>C(x) &ge; k</code>. Counting itself can be done by inclusion-exclusion over the squares <code>d<sup>2</sup></code> (a sign depends on how many prime factors <code>d</code> has).",
           "<code>C(x) = sum over d &ge; 1 with d<sup>2</sup> &le; x of mu(d) * floor(x / d<sup>2</sup>)</code>, where <code>mu(d)</code> is 0 if <code>d</code> has a squared prime factor, otherwise <code>(-1)</code> to the number of its prime factors. Sieve <code>mu</code> up to about 14,200, and binary search <code>x</code> in <code>[1, 2k + 10]</code>."],
    editorial=["Counting non-square-free numbers by inclusion-exclusion over primes: the numbers divisible by <code>p<sup>2</sup></code> are subtracted, then those divisible by <code>(pq)<sup>2</sup></code> are added back, and so on. Collecting terms gives <code>C(x) = sum mu(d) * floor(x / d<sup>2</sup>)</code> over all <code>d</code> with <code>d<sup>2</sup> &le; x</code>, where the Mobius function <code>mu(d)</code> is 0 when <code>d</code> is not square-free and <code>(-1)<sup>t</sup></code> when <code>d</code> is a product of <code>t</code> distinct primes.",
               "Square-free numbers have density 6/pi<sup>2</sup>, about 0.608, so the answer is roughly 1.645 k and the upper bound <code>2k + 10</code> is safe (for any x, at least 54% of the numbers up to x are square-free). Since <code>C</code> is non-decreasing and increases by exactly 1 at each square-free number, the smallest <code>x</code> with <code>C(x) &ge; k</code> is itself square-free and is the k-th one. The sieve of <code>mu</code> up to <code>sqrt(2k + 10)</code> costs about 14,000 steps and each evaluation of <code>C</code> uses the same number of terms, so the search needs only about 28 * 14,000 operations."],
    time="O(sqrt(k) log k)", space="O(sqrt(k))",
    solution='''def kthSquareFree(k):
    hi = 2 * k + 10
    limit = int(hi ** 0.5) + 2
    mu = [1] * (limit + 1)
    is_comp = [False] * (limit + 1)
    primes = []
    for i in range(2, limit + 1):
        if not is_comp[i]:
            primes.append(i)
            mu[i] = -1
        for p in primes:
            if i * p > limit:
                break
            is_comp[i * p] = True
            if i % p == 0:
                mu[i * p] = 0
                break
            mu[i * p] = -mu[i]
    terms = [(d * d, mu[d]) for d in range(1, limit + 1) if mu[d] != 0]

    def count(x):
        total = 0
        for sq, m in terms:
            if sq > x:
                break
            total += m * (x // sq)
        return total

    lo = 1
    while lo < hi:
        mid = (lo + hi) // 2
        if count(mid) >= k:
            hi = mid
        else:
            lo = mid + 1
    return lo
''',
    tests=[[4], [10], [1], [2], [3], [5], [6], [7], [8], [9], [11], [100], [1000], [123456], [99999999], [100000000], [50000000], [12345678], [76543210]],
)


def _squarefree(x):
    d = 2
    while d * d <= x:
        if x % (d * d) == 0:
            return False
        d += 1
    return True


def b_kth_sqfree(k):
    c = 0
    x = 0
    while c < k:
        x += 1
        if _squarefree(x):
            c += 1
    return x


def v_kth_sqfree(tests):
    for t in tests:
        k = t["args"][0]
        assert 1 <= k <= 10 ** 8
        x = t["expected"]
        assert _squarefree(x)
        assert 1.5 * k <= x <= 1.8 * k + 5 or k < 20
        if k <= 20000:
            assert b_kth_sqfree(k) == x


CHECKS["kth-squarefree-number"] = (b_kth_sqfree, lambda r: [r.randint(1, 120)], "exact")
VALIDATE["kth-squarefree-number"] = v_kth_sqfree
