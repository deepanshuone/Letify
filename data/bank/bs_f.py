"""Problems: binary search on peaks, mountains and unimodal sequences. See data/lib.py for the registry."""
from lib import add, rnd, CHECKS, VALIDATE, gen_arr  # noqa: F401

INT_MIN, INT_MAX = -(2 ** 31), 2 ** 31 - 1


def _mountain(r, n, p, lo, hi):
    """Strict mountain of length n (n >= 3) with its peak at index p (1 <= p <= n-2); values in [lo, hi]."""
    left = sorted(r.sample(range(lo, hi), p))
    right = sorted(r.sample(range(lo, hi), n - 1 - p), reverse=True)
    top = r.randint(max(left[-1], right[0]) + 1, hi)
    return left + [top] + right


def _is_mountain(a):
    n = len(a)
    i = 0
    while i + 1 < n and a[i] < a[i + 1]:
        i += 1
    if i == 0 or i == n - 1:
        return False
    while i + 1 < n and a[i] > a[i + 1]:
        i += 1
    return i == n - 1


def _rand_mountain(r, lo=-6, hi=6, nmax=9):
    n = r.randint(3, nmax)
    return _mountain(r, n, r.randint(1, n - 2), lo, hi)


# ---------------------------------------------------------------- EASY

p = add(
    id="peak-index-in-mountain-array", title="Peak Index in a Mountain Array", diff="Easy", topic="Binary Search",
    fn="peakIndex", params=[("nums", "int[]")], ret="int", cmp="exact",
    desc="<p>An array is a <em>mountain</em> if it has at least 3 elements and there is an index <code>p</code> with <code>0 &lt; p &lt; n - 1</code> such that <code>nums[0] &lt; nums[1] &lt; ... &lt; nums[p]</code> and <code>nums[p] &gt; nums[p + 1] &gt; ... &gt; nums[n - 1]</code>.</p><p>Given a mountain array <code>nums</code>, return the index <code>p</code> of its peak. Do better than a linear scan: an O(log n) solution exists.</p><p>For example, in <code>[1, 4, 9, 6, 2]</code> the peak is at index <code>2</code>.</p>",
    constraints=["3 &le; nums.length &le; 10,000", "-2<sup>31</sup> &le; nums[i] &le; 2<sup>31</sup> - 1", "nums is guaranteed to be a mountain array"],
    hints=["Scanning for the maximum is O(n). What does the mountain shape tell you about the elements to the left or right of any position?",
           "Look at one position <code>mid</code> and its right neighbour. If <code>nums[mid] &lt; nums[mid + 1]</code>, are you on the rising slope or the falling slope? Where can the peak be?",
           "Keep the range <code>[lo, hi]</code> that must contain the peak. If <code>nums[mid] &lt; nums[mid + 1]</code> the peak is strictly right of <code>mid</code>, so <code>lo = mid + 1</code>; otherwise the peak is at <code>mid</code> or left of it, so <code>hi = mid</code>. Stop when <code>lo == hi</code>."],
    editorial=["The question 'is position i still climbing?', that is <code>nums[i] &lt; nums[i + 1]</code>, is true for every index before the peak and false for the peak and everything after it. A predicate that flips exactly once is what a binary search needs.",
               "Maintain <code>lo = 0</code>, <code>hi = n - 1</code>. While <code>lo &lt; hi</code>, take <code>mid = (lo + hi) // 2</code>; <code>mid + 1</code> is always in range because <code>mid &lt; hi</code>. If the slope is rising, the peak is right of <code>mid</code>, so move <code>lo</code> to <code>mid + 1</code>. Otherwise <code>mid</code> could itself be the peak, so keep it and set <code>hi = mid</code>. The range halves each step and ends on the peak.",
               "That is O(log n) time and O(1) space. Because all neighbouring values differ (strict slopes), there is no plateau that could make the test ambiguous."],
    time="O(log n)", space="O(1)", tier="common",
    solution='''def peakIndex(nums):
    lo, hi = 0, len(nums) - 1
    while lo < hi:
        mid = (lo + hi) // 2
        if nums[mid] < nums[mid + 1]:
            lo = mid + 1
        else:
            hi = mid
    return lo
''',
    tests=[[[0, 1, 0]], [[0, 10, 5, 2]], [[3, 4, 5, 1]], [[24, 69, 100, 99, 79, 78, 67, 36, 26, 19]],
           [[1, 2, 3, 4, 5, 6, 7, 100, 0]], [[1, 100, 50, 40, 30, 20, 10, 0, -5]], [[INT_MIN, INT_MAX, INT_MIN + 1]],
           [[-9, -8, -7, -3, -4]], [[1, 3, 5, 7, 9, 8]], [[5, 9, 8, 7, 6, 4, 3, 2]]],
)
_r = rnd(8101)
p["tests"].append([_mountain(_r, 4000, 1, -10 ** 6, 10 ** 6)])
p["tests"].append([_mountain(_r, 4000, 3998, -10 ** 6, 10 ** 6)])
p["tests"].append([_mountain(_r, 5000, 2713, -10 ** 6, 10 ** 6)])


def b_peak_index(nums):
    return nums.index(max(nums))


def v_peak_index(tests):
    for t in tests:
        a = t["args"][0]
        assert 3 <= len(a) <= 10000 and _is_mountain(a)
        assert all(INT_MIN <= x <= INT_MAX for x in a)


CHECKS["peak-index-in-mountain-array"] = (b_peak_index, lambda r: [_rand_mountain(r)], "exact")
VALIDATE["peak-index-in-mountain-array"] = v_peak_index

p = add(
    id="minimum-of-v-shaped-array", title="Minimum of a V-Shaped Array", diff="Easy", topic="Binary Search",
    fn="vBottom", params=[("nums", "int[]")], ret="int", cmp="exact",
    desc="<p>A <em>V-shaped</em> array first strictly decreases and then strictly increases: there is an index <code>b</code> with <code>0 &lt; b &lt; n - 1</code> such that <code>nums[0] &gt; ... &gt; nums[b]</code> and <code>nums[b] &lt; ... &lt; nums[n - 1]</code>.</p><p>Given a V-shaped array, return its smallest value (the value at the bottom of the V) in O(log n) time.</p><p>For example, <code>[9, 4, 1, 3, 8]</code> has bottom value <code>1</code>.</p>",
    constraints=["3 &le; nums.length &le; 10,000", "-2<sup>31</sup> &le; nums[i] &le; 2<sup>31</sup> - 1", "nums is guaranteed to be V-shaped"],
    hints=["The smallest value sits where the array stops falling and starts rising.",
           "Compare <code>nums[mid]</code> with <code>nums[mid + 1]</code>. If it is smaller than its right neighbour, you are already on the rising side.",
           "If <code>nums[mid] &gt; nums[mid + 1]</code> the bottom is right of <code>mid</code> (<code>lo = mid + 1</code>); otherwise the bottom is at <code>mid</code> or left of it (<code>hi = mid</code>). Return <code>nums[lo]</code> at the end."],
    editorial=["This is the mirror image of finding the top of a mountain. The test <code>nums[i] &gt; nums[i + 1]</code> ('still falling') holds for every index before the bottom and fails from the bottom onwards, so binary search can find the boundary.",
               "With <code>lo = 0</code> and <code>hi = n - 1</code>, set <code>mid = (lo + hi) // 2</code>. A falling step means the bottom lies strictly to the right, so <code>lo = mid + 1</code>; a rising step means <code>mid</code> may be the bottom, so <code>hi = mid</code>. When the range shrinks to one index, that index is the bottom.",
               "The running time is O(log n) with O(1) space. The strict slopes matter: a flat stretch would make the 'falling or rising' test ambiguous."],
    time="O(log n)", space="O(1)", tier="common",
    solution='''def vBottom(nums):
    lo, hi = 0, len(nums) - 1
    while lo < hi:
        mid = (lo + hi) // 2
        if nums[mid] > nums[mid + 1]:
            lo = mid + 1
        else:
            hi = mid
    return nums[lo]
''',
    tests=[[[1, 0, 1]], [[9, 4, 1, 3, 8]], [[5, 4, 3, 2, 1, 2]], [[5, 1, 2, 3, 4, 5]], [[-1, -2, -3, -4, 0]],
           [[INT_MAX, INT_MIN, INT_MAX]], [[10, 7, 5, 4, 6, 9, 12]], [[0, -5, 3]], [[100, 50, 20, 10, 5, 4, 3, 2, 3]],
           [[7, 2, 3, 4, 5, 6]]],
)
_r = rnd(8102)
p["tests"].append([[-x for x in _mountain(_r, 4000, 2, -10 ** 6, 10 ** 6)]])
p["tests"].append([[-x for x in _mountain(_r, 4000, 3997, -10 ** 6, 10 ** 6)]])
p["tests"].append([[-x for x in _mountain(_r, 5000, 1888, -10 ** 6, 10 ** 6)]])


def b_vbottom(nums):
    return min(nums)


def v_vbottom(tests):
    for t in tests:
        a = t["args"][0]
        assert 3 <= len(a) <= 10000 and _is_mountain([-x for x in a])
        assert all(INT_MIN <= x <= INT_MAX for x in a)


CHECKS["minimum-of-v-shaped-array"] = (b_vbottom, lambda r: [[-x for x in _rand_mountain(r)]], "exact")
VALIDATE["minimum-of-v-shaped-array"] = v_vbottom

# ---------------------------------------------------------------- MEDIUM

p = add(
    id="flat-topped-mountain-width", title="Width of a Flat-Topped Mountain", diff="Medium", topic="Binary Search",
    fn="topWidth", params=[("nums", "int[]")], ret="int", cmp="exact",
    desc="<p>A <em>flat-topped mountain</em> consists of three consecutive parts: a non-empty strictly increasing run, then a plateau of one or more equal values (the top), then a non-empty strictly decreasing run. The plateau value is larger than the value before it and larger than the value after it.</p><p>Given such an array <code>nums</code>, return the width of the plateau, that is, how many elements are equal to the maximum.</p><p>For example, in <code>[1, 3, 7, 7, 7, 4, 2]</code> the plateau is <code>7, 7, 7</code>, so the answer is <code>3</code>. Aim for O(log n) time even when the plateau is huge.</p>",
    constraints=["3 &le; nums.length &le; 10,000", "-2<sup>31</sup> &le; nums[i] &le; 2<sup>31</sup> - 1", "nums consists of a strictly increasing run, a plateau of at least one element, and a strictly decreasing run; the two runs are not empty"],
    hints=["Counting the elements equal to the maximum is O(n). Since the plateau is a contiguous block, you only need to find where it starts and where it ends.",
           "The plateau starts at the first index <code>i</code> where <code>nums[i] &lt; nums[i + 1]</code> is no longer true. The plateau ends before the first index whose value is smaller than the plateau value.",
           "Run two binary searches. First find the start <code>s</code> (the climb test <code>nums[mid] &lt; nums[mid + 1]</code> is true before it, false from it). Then search the range <code>[s, n - 1]</code> for the first index <code>e</code> with <code>nums[e] &lt; nums[s]</code>; the width is <code>e - s</code>."],
    editorial=["Both ends of the plateau are boundaries of a predicate that changes value exactly once, so each is found by a binary search.",
               "Start of the plateau: the predicate 'nums[i] &lt; nums[i + 1]' (still climbing) is true on the increasing run and false at the first plateau element (and everywhere after). Binary search on <code>[0, n - 1]</code> with <code>lo = mid + 1</code> when it is true and <code>hi = mid</code> otherwise gives the first index where it is false, which is the plateau start <code>s</code>. Because the increasing run is strictly increasing and non-empty, and the plateau is followed by a strictly lower value, no other position can fool this test.",
               "End of the plateau: from index <code>s</code> on, the predicate 'nums[i] &lt; nums[s]' is false on the plateau and true after it, since the final run is strictly decreasing. A second binary search on <code>[s, n]</code> finds the first index <code>e</code> where it holds (or <code>n</code> if none), and the plateau has <code>e - s</code> elements.",
               "Total time is O(log n) and extra space O(1), independent of the plateau width. A linear count would degrade to O(n)."],
    time="O(log n)", space="O(1)", tier="extra",
    solution='''def topWidth(nums):
    n = len(nums)
    lo, hi = 0, n - 1
    while lo < hi:
        mid = (lo + hi) // 2
        if nums[mid] < nums[mid + 1]:
            lo = mid + 1
        else:
            hi = mid
    start = lo
    top = nums[start]
    lo, hi = start, n
    while lo < hi:
        mid = (lo + hi) // 2
        if nums[mid] < top:
            hi = mid
        else:
            lo = mid + 1
    return lo - start
''',
    tests=[[[1, 3, 7, 7, 7, 4, 2]], [[1, 2, 1]], [[1, 2, 2, 1]], [[0, 5, 5, 5, 5, 5, 5, 5, -1]], [[1, 2, 3, 9, 9, 0]],
           [[1, 9, 9, 8, 7, 6]], [[-5, -1, -1, -2]], [[INT_MIN, INT_MAX, INT_MAX, INT_MIN]],
           [[1, 2, 3, 4, 5, 5, 3]], [[3, 7, 7, 4]], [[2, 6, 6, 6, 1]]],
)
_r = rnd(8103)


def _flat(r, a, t, b, lo, hi):
    left = sorted(r.sample(range(lo, hi), a))
    right = sorted(r.sample(range(lo, hi), b), reverse=True)
    top = r.randint(max(left[-1], right[0]) + 1, hi)
    return left + [top] * t + right


p["tests"].append([_flat(_r, 1000, 3000, 1000, -10 ** 5, 10 ** 5)])
p["tests"].append([_flat(_r, 1, 4000, 1999, -10 ** 5, 10 ** 5)])
p["tests"].append([_flat(_r, 1998, 4001, 1, -10 ** 5, 10 ** 5)])


def b_top_width(nums):
    return nums.count(max(nums))


def g_top_width(r):
    return [_flat(r, r.randint(1, 4), r.randint(1, 4), r.randint(1, 4), -6, 6)]


def v_top_width(tests):
    for t in tests:
        a = t["args"][0]
        n = len(a)
        assert 3 <= n <= 10000
        i = 0
        while i + 1 < n and a[i] < a[i + 1]:
            i += 1
        assert i >= 1
        j = i
        while j + 1 < n and a[j] == a[j + 1]:
            j += 1
        assert j < n - 1
        while j + 1 < n and a[j] > a[j + 1]:
            j += 1
        assert j == n - 1


CHECKS["flat-topped-mountain-width"] = (b_top_width, g_top_width, "exact")
VALIDATE["flat-topped-mountain-width"] = v_top_width

p = add(
    id="count-in-range-in-mountain-array", title="Count Values in a Range of a Mountain Array", diff="Medium", topic="Binary Search",
    fn="countInRange", params=[("nums", "int[]"), ("queries", "int[][]")], ret="int[]", cmp="exact",
    desc="<p>The array <code>nums</code> is a <em>mountain</em>: strictly increasing up to a peak, then strictly decreasing (the peak is neither the first nor the last element). Values may repeat between the two slopes.</p><p>Each query is a pair <code>[lo, hi]</code> with <code>lo &le; hi</code>. For every query, count how many elements <code>x</code> of <code>nums</code> satisfy <code>lo &le; x &le; hi</code>. Return the counts in query order.</p><p>With many queries, scanning the array per query is too slow in the worst case; answer each query in O(log n).</p>",
    constraints=["3 &le; nums.length &le; 5,000", "1 &le; queries.length &le; 1,000", "-10<sup>9</sup> &le; nums[i], lo, hi &le; 10<sup>9</sup>, and lo &le; hi", "nums is guaranteed to be a mountain array"],
    hints=["A count of values inside <code>[lo, hi]</code> equals (count of values &le; hi) minus (count of values &le; lo - 1). So one helper <code>countAtMost(x)</code> is enough.",
           "The mountain splits into two sorted pieces at the peak: an ascending left part and a descending right part. Find the peak first with a binary search, then count in each piece separately.",
           "In the ascending part, binary search the first index with value &gt; x; everything before it counts. In the descending part, binary search the first index with value &le; x; everything from it to the end counts."],
    editorial=["Turn the range count into a difference of two prefix-style counts: <code>countAtMost(hi) - countAtMost(lo - 1)</code>.",
               "Compute <code>countAtMost(x)</code> on the mountain in O(log n). First locate the peak once (the usual binary search comparing <code>nums[mid]</code> with <code>nums[mid + 1]</code>). The part <code>nums[0..peak]</code> is ascending, so the elements &le; x form a prefix; a binary search for the first value &gt; x gives its length. The part <code>nums[peak + 1..]</code> is descending, so the elements &le; x form a suffix; a binary search for the first value &le; x gives its start, and the suffix length is <code>n - start</code>. Add both.",
               "The peak search is done once, then each query costs O(log n). Total time is O(log n + q log n) and the extra space is O(1) besides the output."],
    time="O((n0 + q) log n)", space="O(1)", tier="common",
    solution='''def countInRange(nums, queries):
    n = len(nums)
    lo, hi = 0, n - 1
    while lo < hi:
        mid = (lo + hi) // 2
        if nums[mid] < nums[mid + 1]:
            lo = mid + 1
        else:
            hi = mid
    peak = lo

    def at_most(x):
        a, b = 0, peak + 1
        while a < b:
            m = (a + b) // 2
            if nums[m] <= x:
                a = m + 1
            else:
                b = m
        left = a
        a, b = peak + 1, n
        while a < b:
            m = (a + b) // 2
            if nums[m] <= x:
                b = m
            else:
                a = m + 1
        return left + (n - a)

    return [at_most(h) - at_most(l - 1) for l, h in queries]
''',
    tests=[[[1, 3, 5, 4, 2], [[2, 4], [0, 10], [6, 9], [5, 5]]], [[0, 1, 0], [[0, 0], [1, 1], [0, 1], [2, 3]]],
           [[1, 2, 3, 2, 1], [[2, 2], [1, 1], [3, 3], [1, 3]]], [[-5, 0, 4, 9, 6, 1, -3, -8], [[-10, -4], [-3, 1], [0, 9], [7, 8]]],
           [[10, 20, 30, 25, 5], [[11, 19], [20, 25], [5, 30]]], [[1, 100, 50, 10, 5, 2], [[3, 60], [100, 100], [-5, 0]]],
           [[-10 ** 9, 10 ** 9, -10 ** 9 + 1], [[-10 ** 9, 10 ** 9], [-10 ** 9, -10 ** 9], [10 ** 9, 10 ** 9]]],
           [[1, 2, 3, 4, 5, 6, 7, 8, 9, 0], [[0, 0], [1, 9], [4, 6]]], [[0, 9, 8, 7, 6, 5, 4, 3, 2, 1], [[0, 0], [1, 9], [4, 6]]]],
)
_r = rnd(8104)
for _n, _p in ((3000, 1200), (3500, 3498)):
    _nums = _mountain(_r, _n, _p, -10 ** 6, 10 ** 6)
    _qs = []
    for _ in range(700):
        _x, _y = sorted((_r.randint(-10 ** 6, 10 ** 6), _r.randint(-10 ** 6, 10 ** 6)))
        _qs.append([_x, _y])
    p["tests"].append([_nums, _qs])


def b_count_range(nums, queries):
    return [sum(1 for x in nums if l <= x <= h) for l, h in queries]


def g_count_range(r):
    nums = _rand_mountain(r)
    qs = []
    for _ in range(r.randint(1, 4)):
        a, b = sorted((r.randint(-8, 8), r.randint(-8, 8)))
        qs.append([a, b])
    return [nums, qs]


def v_count_range(tests):
    for t in tests:
        nums, qs = t["args"]
        assert 3 <= len(nums) <= 5000 and _is_mountain(nums)
        assert 1 <= len(qs) <= 1000
        assert all(len(q) == 2 and q[0] <= q[1] for q in qs)
        assert all(-10 ** 9 <= v <= 10 ** 9 for v in nums) and all(-10 ** 9 <= v <= 10 ** 9 for q in qs for v in q)


CHECKS["count-in-range-in-mountain-array"] = (b_count_range, g_count_range, "exact")
VALIDATE["count-in-range-in-mountain-array"] = v_count_range

p = add(
    id="closest-value-in-mountain-array", title="Closest Value in a Mountain Array", diff="Medium", topic="Binary Search",
    fn="closestValue", params=[("nums", "int[]"), ("target", "int")], ret="int", cmp="exact",
    desc="<p>The array <code>nums</code> is a mountain: strictly increasing up to a peak (which is neither the first nor the last element), then strictly decreasing. The same value may occur once on each slope.</p><p>Return the element of <code>nums</code> that is closest to <code>target</code>, that is, the value <code>x</code> minimizing <code>|x - target|</code>. If two different values are equally close, return the smaller one.</p><p>For example, for <code>nums = [1, 4, 9, 6, 2]</code> and <code>target = 5</code> the values 4 and 6 are both at distance 1, so the answer is <code>4</code>. Use O(log n) time.</p>",
    constraints=["3 &le; nums.length &le; 10,000", "-10<sup>9</sup> &le; nums[i], target &le; 10<sup>9</sup>", "nums is guaranteed to be a mountain array"],
    hints=["If nums were sorted, the closest value would be one of the two neighbours of the insertion point of <code>target</code>. Can you make the mountain look sorted?",
           "The peak splits the mountain into an ascending part and a descending part. Each part is sorted, just in opposite directions.",
           "Find the peak by binary search. In each part find the insertion position of <code>target</code> and look at the element just before and just after it. Compare at most 4 candidates by the pair (distance, value)."],
    editorial=["Closest-value search in a sorted array only needs the neighbours of where the target would be inserted. A mountain is two sorted arrays glued at the peak, so do the same twice.",
               "First locate the peak index with the standard slope test. In the ascending part <code>nums[0..peak]</code> binary search the first index <code>a</code> with <code>nums[a] &ge; target</code>; the candidates are <code>nums[a - 1]</code> and <code>nums[a]</code> if they exist in that part. In the descending part <code>nums[peak + 1..]</code> binary search the first index <code>a</code> with <code>nums[a] &le; target</code>; again the candidates are <code>nums[a - 1]</code> and <code>nums[a]</code>.",
               "Among at most four candidates choose the one with the smallest key <code>(|x - target|, x)</code>, which implements the 'smaller value wins ties' rule. Three binary searches give O(log n) time and O(1) space."],
    time="O(log n)", space="O(1)", tier="extra",
    solution='''def closestValue(nums, target):
    n = len(nums)
    lo, hi = 0, n - 1
    while lo < hi:
        mid = (lo + hi) // 2
        if nums[mid] < nums[mid + 1]:
            lo = mid + 1
        else:
            hi = mid
    peak = lo
    best = None

    def consider(v):
        nonlocal best
        if best is None or (abs(v - target), v) < (abs(best - target), best):
            best = v

    a, b = 0, peak + 1
    while a < b:
        m = (a + b) // 2
        if nums[m] >= target:
            b = m
        else:
            a = m + 1
    for i in (a - 1, a):
        if 0 <= i <= peak:
            consider(nums[i])
    a, b = peak + 1, n
    while a < b:
        m = (a + b) // 2
        if nums[m] <= target:
            b = m
        else:
            a = m + 1
    for i in (a - 1, a):
        if peak + 1 <= i < n:
            consider(nums[i])
    return best
''',
    tests=[[[1, 4, 9, 6, 2], 5], [[1, 4, 9, 6, 2], 7], [[1, 4, 9, 6, 2], 100], [[1, 4, 9, 6, 2], -100], [[0, 5, 0], 3],
           [[0, 5, 0], 2], [[2, 6, 10, 8, 4], 7], [[2, 6, 10, 8, 4], 5], [[-10 ** 9, 10 ** 9, -10 ** 9 + 1], 0],
           [[-10 ** 9, 10 ** 9, -10 ** 9 + 1], 10 ** 9], [[1, 3, 5, 7, 9, 8, 6, 4, 2], 5], [[1, 3, 5, 7, 9, 8, 6, 4, 2], 6]],
)
_r = rnd(8105)
for _n, _p, _t in ((4000, 3000, 12345), (5000, 1, -7), (4500, 2200, 10 ** 6 + 17)):
    p["tests"].append([_mountain(_r, _n, _p, -10 ** 6, 10 ** 6), _t])


def b_closest(nums, target):
    return min(nums, key=lambda x: (abs(x - target), x))


def g_closest(r):
    return [_rand_mountain(r), r.randint(-9, 9)]


def v_closest(tests):
    for t in tests:
        nums, target = t["args"]
        assert 3 <= len(nums) <= 10000 and _is_mountain(nums)
        assert all(-10 ** 9 <= v <= 10 ** 9 for v in nums) and -10 ** 9 <= target <= 10 ** 9


CHECKS["closest-value-in-mountain-array"] = (b_closest, g_closest, "exact")
VALIDATE["closest-value-in-mountain-array"] = v_closest

p = add(
    id="shared-values-across-slopes", title="Values Shared by Both Slopes", diff="Medium", topic="Binary Search",
    fn="sharedSlopeValues", params=[("nums", "int[]")], ret="int", cmp="exact",
    desc="<p>The array <code>nums</code> is a <em>mountain</em>: strictly increasing up to a peak, then strictly decreasing (the peak is neither the first nor the last element). Split it into the <em>left slope</em> (every element before the peak) and the <em>right slope</em> (every element after the peak).</p><p>Return how many distinct values occur on <strong>both</strong> slopes. The peak itself is larger than every other element, so it never counts.</p><p>For example, in <code>[1, 3, 5, 9, 5, 4, 3, 0]</code> the left slope is <code>1, 3, 5</code> and the right slope is <code>5, 4, 3, 0</code>. The values <code>3</code> and <code>5</code> are on both, so the answer is <code>2</code>.</p><p>A solution with O(log n) steps per element of the shorter slope is expected.</p>",
    constraints=["3 &le; nums.length &le; 6,000", "-10<sup>9</sup> &le; nums[i] &le; 10<sup>9</sup>", "nums is guaranteed to be a mountain array"],
    hints=["Each slope has all-different values, so a value is shared exactly when it appears once on each slope. Where does the left slope end?",
           "Find the peak with a binary search on the test <code>nums[mid] &lt; nums[mid + 1]</code>. Now you have two sorted pieces, one ascending and one descending.",
           "Take every element of the shorter slope and binary search for it in the other slope (adapt the comparison for the descending side). Count the hits. The cost is O(min(a, b) * log max(a, b))."],
    editorial=["Both slopes consist of distinct values, so counting shared values is the same as counting the elements of one slope that also appear in the other. The peak is strictly bigger than everything else and can be left out.",
               "First locate the peak by binary search: the climbing test <code>nums[i] &lt; nums[i + 1]</code> is true before the peak and false from it on. The elements <code>nums[0..peak-1]</code> are sorted ascending and <code>nums[peak+1..n-1]</code> are sorted descending.",
               "Iterate over the shorter slope and look each value up in the longer one with a binary search (a normal one for the ascending slope, one with the inequality reversed for the descending slope). Every successful lookup is a shared value. This takes O(log n) for the peak plus O(min(a, b) log max(a, b)) for the lookups, with O(1) extra space. A two-pointer sweep over both slopes gives O(n), which is also fine, but the binary search version wins when one slope is short."],
    time="O(min(a, b) log max(a, b))", space="O(1)", tier="extra",
    solution='''def sharedSlopeValues(nums):
    n = len(nums)
    lo, hi = 0, n - 1
    while lo < hi:
        mid = (lo + hi) // 2
        if nums[mid] < nums[mid + 1]:
            lo = mid + 1
        else:
            hi = mid
    peak = lo
    left = (0, peak)          # ascending, indices [0, peak)
    right = (peak + 1, n)     # descending, indices [peak + 1, n)

    def found_asc(x, a, b):
        while a < b:
            m = (a + b) // 2
            if nums[m] < x:
                a = m + 1
            else:
                b = m
        return a < left[1] and nums[a] == x

    def found_desc(x, a, b):
        while a < b:
            m = (a + b) // 2
            if nums[m] > x:
                a = m + 1
            else:
                b = m
        return a < n and nums[a] == x

    count = 0
    if left[1] - left[0] <= right[1] - right[0]:
        for i in range(left[0], left[1]):
            if found_desc(nums[i], right[0], right[1]):
                count += 1
    else:
        for i in range(right[0], right[1]):
            if found_asc(nums[i], left[0], left[1]):
                count += 1
    return count
''',
    tests=[[[1, 3, 5, 9, 5, 4, 3, 0]], [[0, 1, 0]], [[1, 2, 1]], [[1, 2, 3, 2]],
           [[1, 2, 3, 4, 3, 2, 1]], [[1, 2, 3, 4, 7, 6, 5]], [[-5, -3, 0, 8, 0, -3, -5]], [[-10 ** 9, 10 ** 9, -10 ** 9]],
           [[2, 4, 6, 8, 10, 9, 7, 5, 3, 1]], [[1, 5, 9, 8, 7, 6, 5, 4, 3, 2, 1]], [[4, 6, 10, 7, 6, 4, 2, 1, 0, -1]]],
)
_r = rnd(8111)


def _overlap_mountain(r, a, b, pool, shared):
    """Left slope of a values and right slope of b values drawn so that about `shared` values occur on both."""
    vals = r.sample(range(-pool, pool), a + b)
    left = sorted(vals[:a])
    k = min(shared, a, b)
    right = set(r.sample(left, k))
    for v in vals[a:]:
        if len(right) >= b:
            break
        if v not in left:
            right.add(v)
    right = sorted(right, reverse=True)
    top = max(left[-1], right[0]) + 1
    return left + [top] + right


p["tests"].append([_overlap_mountain(_r, 2900, 2900, 10 ** 6, 1200)])
p["tests"].append([_overlap_mountain(_r, 40, 5000, 10 ** 6, 40)])
p["tests"].append([_overlap_mountain(_r, 4500, 30, 10 ** 8, 0)])


def b_shared(nums):
    pk = nums.index(max(nums))
    return len(set(nums[:pk]) & set(nums[pk + 1:]))


def g_shared(r):
    return [_rand_mountain(r, -5, 5, 10)]


def v_shared(tests):
    for t in tests:
        a = t["args"][0]
        assert 3 <= len(a) <= 6000 and _is_mountain(a)
        assert all(-10 ** 9 <= x <= 10 ** 9 for x in a)
        assert t["expected"] == b_shared(a)


CHECKS["shared-values-across-slopes"] = (b_shared, lambda r: g_shared(r), "exact")
VALIDATE["shared-values-across-slopes"] = v_shared

p = add(
    id="minimum-of-convex-sequence", title="Minimum of a Convex Sequence", diff="Medium", topic="Binary Search",
    fn="convexMin", params=[("nums", "int[]")], ret="int", cmp="exact",
    desc="<p>An array <code>nums</code> is <em>convex</em> if its consecutive differences never decrease: <code>nums[i + 1] - nums[i] &le; nums[i + 2] - nums[i + 1]</code> for every valid <code>i</code>. Such an array may fall, then stay flat, then rise (any of the three phases may be empty), and flat stretches can occur only at the bottom.</p><p>Return the smallest value in <code>nums</code> using O(log n) comparisons.</p><p>For example, <code>[10, 6, 3, 1, 0, 0, 1, 3]</code> is convex (differences -4, -3, -2, -1, 0, 1, 2) and its minimum is <code>0</code>.</p>",
    constraints=["1 &le; nums.length &le; 10,000", "-10<sup>9</sup> &le; nums[i] &le; 10<sup>9</sup>", "nums[i + 1] - nums[i] &le; nums[i + 2] - nums[i + 1] for every valid i"],
    hints=["Look at the differences <code>d[i] = nums[i + 1] - nums[i]</code>. What does convexity say about the sequence <code>d</code>?",
           "<code>d</code> is sorted in non-decreasing order, so the sign of <code>d[i]</code> flips at most once: from negative to non-negative. The array keeps falling while <code>d[i] &lt; 0</code>.",
           "Binary search the first index <code>i</code> with <code>nums[i + 1] - nums[i] &ge; 0</code> (treat <code>i = n - 1</code> as true). Then <code>nums[i]</code> is the minimum."],
    editorial=["Convexity makes the sequence of differences sorted. Before the first non-negative difference the array strictly falls; from that point on it never falls again. So the minimum is at the first index <code>i</code> whose difference to the right is &ge; 0 (or at the last index if there is none).",
               "The predicate 'nums[i + 1] - nums[i] &ge; 0' is therefore monotone (false...false, true...true) and is searched with a standard lower-bound binary search over <code>[0, n - 1]</code>, where the last index counts as true. Flat stretches do no harm: they have difference 0, which is true, and because differences cannot decrease afterwards they can only sit at the minimum level.",
               "This is the discrete form of finding the minimum of a convex function by checking the slope. It takes O(log n) time and O(1) space. Plain unimodal arrays that are not convex can contain flat steps elsewhere, which would break this argument, so the convexity guarantee matters."],
    time="O(log n)", space="O(1)", tier="extra",
    solution='''def convexMin(nums):
    lo, hi = 0, len(nums) - 1
    while lo < hi:
        mid = (lo + hi) // 2
        if nums[mid + 1] - nums[mid] >= 0:
            hi = mid
        else:
            lo = mid + 1
    return nums[lo]
''',
    tests=[[[10, 6, 3, 1, 0, 0, 1, 3]], [[5]], [[3, 7]], [[7, 3]], [[1, 2, 4, 7, 11]], [[11, 7, 4, 2, 1]], [[4, 4, 4, 4]],
           [[9, 4, 1, 0, 1, 4, 9]], [[8, 5, 3, 2, 2, 2, 3]], [[0, 0, 1]], [[-10 ** 9, -10 ** 9, -10 ** 9 + 5]]],
)
_r = rnd(8106)


def _convex(r, n, dlo, dhi, start):
    d = sorted(r.randint(dlo, dhi) for _ in range(n - 1))
    a = [start]
    for x in d:
        a.append(a[-1] + x)
    return a


p["tests"].append([_convex(_r, 5000, -400, 600, 0)])
p["tests"].append([_convex(_r, 5000, -600, 0, 10 ** 6)])
p["tests"].append([_convex(_r, 5000, -3, 3, 0)])
p["tests"].append([_convex(_r, 5000, 0, 3, -50)])


def b_convex(nums):
    return min(nums)


def g_convex(r):
    return [_convex(r, r.randint(1, 9), -4, 4, r.randint(-6, 6))]


def v_convex(tests):
    for t in tests:
        a = t["args"][0]
        assert 1 <= len(a) <= 10000 and all(-10 ** 9 <= x <= 10 ** 9 for x in a)
        d = [a[i + 1] - a[i] for i in range(len(a) - 1)]
        assert all(d[i] <= d[i + 1] for i in range(len(d) - 1)), "not convex"


CHECKS["minimum-of-convex-sequence"] = (b_convex, g_convex, "exact")
VALIDATE["minimum-of-convex-sequence"] = v_convex

p = add(
    id="minimize-upper-envelope-of-lines", title="Lowest Point of the Upper Envelope", diff="Medium", topic="Binary Search",
    fn="lowestEnvelope", params=[("lines", "int[][]"), ("lo", "int"), ("hi", "int")], ret="int", cmp="exact",
    desc="<p>Each element of <code>lines</code> is a pair <code>[m, c]</code> describing the function <code>f(x) = m * x + c</code>. Define <code>F(x)</code> as the maximum of all these functions at <code>x</code>:</p><p><code>F(x) = max over all lines of (m * x + c)</code>.</p><p>Choose an <em>integer</em> <code>x</code> with <code>lo &le; x &le; hi</code> that makes <code>F(x)</code> as small as possible, and return that smallest value of <code>F</code>.</p><p>For example, with lines <code>[1, 0]</code> and <code>[-1, 6]</code> (that is, <code>x</code> and <code>6 - x</code>) on the range <code>[0, 10]</code>, the best choice is <code>x = 3</code> and the answer is <code>3</code>.</p>",
    constraints=["1 &le; lines.length &le; 3,000", "-1000 &le; m, c &le; 1000", "-10<sup>5</sup> &le; lo &le; hi &le; 10<sup>5</sup>"],
    hints=["Trying every integer <code>x</code> costs O((hi - lo) * n), which is too slow when the range is wide and there are many lines. What shape does <code>F</code> have?",
           "The maximum of straight lines is a convex function: its slope only increases as <code>x</code> grows. A convex function decreases, then increases, like a valley.",
           "Binary search the first <code>x</code> in <code>[lo, hi - 1]</code> where <code>F(x + 1) - F(x) &ge; 0</code>; if there is none, the answer is at <code>hi</code>. Each evaluation of <code>F</code> costs O(n)."],
    editorial=["Each line is convex (it is linear), and the pointwise maximum of convex functions is convex. So <code>F</code> on the integers satisfies <code>F(x + 1) - F(x) &le; F(x + 2) - F(x + 1)</code>: its steps never decrease.",
               "Hence the predicate <code>F(x + 1) - F(x) &ge; 0</code> ('not going down any more') is false for small <code>x</code> and true from some point on, and the first <code>x</code> where it is true is a minimiser. Binary search for it on <code>[lo, hi]</code>, evaluating <code>F</code> at <code>mid</code> and <code>mid + 1</code> in O(n) each, and return <code>F</code> at the point found.",
               "There are about log(hi - lo) steps, each O(n), so the total is O(n log(hi - lo)) time with O(1) extra space. A ternary search would also work, but the slope test avoids trouble with flat stretches where <code>F</code> takes equal values."],
    time="O(n log R)", space="O(1)", tier="extra",
    solution='''def lowestEnvelope(lines, lo, hi):
    def F(x):
        return max(m * x + c for m, c in lines)

    a, b = lo, hi
    while a < b:
        mid = (a + b) // 2
        if F(mid + 1) - F(mid) >= 0:
            b = mid
        else:
            a = mid + 1
    return F(a)
''',
    tests=[[[[1, 0], [-1, 6]], 0, 10], [[[2, 3]], -5, 5], [[[2, 3]], 0, 0], [[[-3, 1]], -4, 7], [[[1, 0], [-1, 0]], -10, 10],
           [[[1, 0], [-1, 0], [0, 2]], -10, 10], [[[0, 5], [0, 7], [0, -1]], -3, 3], [[[1, 0], [-1, 6]], 5, 10],
           [[[1, 0], [-1, 6]], -20, 1], [[[3, -9], [-2, 8], [0, 1]], -100, 100], [[[1000, 1000], [-1000, 1000]], -10 ** 5, 10 ** 5]],
)
_r = rnd(8107)
p["tests"].append([[[_r.randint(-1000, 1000), _r.randint(-1000, 1000)] for _ in range(2500)], -10 ** 5, 10 ** 5])
p["tests"].append([[[_r.randint(0, 1000), _r.randint(-1000, 1000)] for _ in range(1500)] + [[-_r.randint(1, 1000), 1000] for _ in range(1500)], -10 ** 5, 10 ** 5])
p["tests"].append([[[_r.randint(-5, 1000), _r.randint(-1000, 0)] for _ in range(2000)], -10 ** 5, 99999])


def b_envelope(lines, lo, hi):
    return min(max(m * x + c for m, c in lines) for x in range(lo, hi + 1))


def g_envelope(r):
    lines = [[r.randint(-4, 4), r.randint(-9, 9)] for _ in range(r.randint(1, 5))]
    a, b = sorted((r.randint(-9, 9), r.randint(-9, 9)))
    return [lines, a, b]


def v_envelope(tests):
    for t in tests:
        lines, lo, hi = t["args"]
        assert 1 <= len(lines) <= 3000 and all(len(l) == 2 and -1000 <= l[0] <= 1000 and -1000 <= l[1] <= 1000 for l in lines)
        assert -10 ** 5 <= lo <= hi <= 10 ** 5
        if hi - lo <= 2000 and len(lines) <= 50:
            assert t["expected"] == b_envelope(lines, lo, hi)


CHECKS["minimize-upper-envelope-of-lines"] = (b_envelope, g_envelope, "exact")
VALIDATE["minimize-upper-envelope-of-lines"] = v_envelope

# ---------------------------------------------------------------- HARD

p = add(
    id="search-in-mountain-array", title="Search in a Mountain Array", diff="Hard", topic="Binary Search",
    fn="searchMountain", params=[("nums", "int[]"), ("target", "int")], ret="int", cmp="exact",
    desc="<p>The array <code>nums</code> is a mountain: strictly increasing up to a peak (neither the first nor the last element), then strictly decreasing.</p><p>Return the <em>smallest</em> index <code>i</code> such that <code>nums[i] == target</code>, or <code>-1</code> if the target does not occur. Because the same value can appear once on each slope, take care to prefer the left one. Use O(log n) time.</p><p>For example, in <code>[1, 3, 5, 4, 3, 1]</code> the target <code>3</code> occurs at indices 1 and 4, so the answer is <code>1</code>.</p>",
    constraints=["3 &le; nums.length &le; 10,000", "-2<sup>31</sup> &le; nums[i], target &le; 2<sup>31</sup> - 1", "nums is guaranteed to be a mountain array"],
    hints=["A normal binary search needs a sorted array, and a mountain is not sorted. But it consists of two sorted pieces.",
           "Step 1: find the peak with a binary search on the slope (<code>nums[mid] &lt; nums[mid + 1]</code>). Step 2: binary search the ascending part. Step 3: only if not found there, binary search the descending part.",
           "Searching the left part first guarantees the smallest index. In the descending part flip the comparison: if <code>nums[mid] &gt; target</code> go right, if it is smaller go left."],
    editorial=["The peak splits the mountain into <code>nums[0..peak]</code>, strictly ascending, and <code>nums[peak + 1..n - 1]</code>, strictly descending. Both are sorted, so they can be searched independently by ordinary binary search (with the comparison reversed on the descending side).",
               "Procedure: (1) find the peak in O(log n) by comparing <code>nums[mid]</code> with <code>nums[mid + 1]</code>; (2) binary search for <code>target</code> in <code>[0, peak]</code> and return the index if found; (3) otherwise binary search in <code>[peak + 1, n - 1]</code> using the descending order. Since every index of the left part is smaller than every index of the right part, answering from the left part first returns the smallest index.",
               "Three logarithmic searches give O(log n) time and O(1) space. A common mistake is to return the first hit found anywhere without checking the left slope first, which breaks when the target occurs on both slopes."],
    time="O(log n)", space="O(1)", tier="common",
    solution='''def searchMountain(nums, target):
    n = len(nums)
    lo, hi = 0, n - 1
    while lo < hi:
        mid = (lo + hi) // 2
        if nums[mid] < nums[mid + 1]:
            lo = mid + 1
        else:
            hi = mid
    peak = lo
    a, b = 0, peak + 1
    while a < b:
        m = (a + b) // 2
        if nums[m] < target:
            a = m + 1
        else:
            b = m
    if a <= peak and nums[a] == target:
        return a
    a, b = peak + 1, n
    while a < b:
        m = (a + b) // 2
        if nums[m] > target:
            a = m + 1
        else:
            b = m
    if a < n and nums[a] == target:
        return a
    return -1
''',
    tests=[[[1, 3, 5, 4, 3, 1], 3], [[1, 2, 3, 4, 5, 3, 1], 3], [[0, 1, 2, 4, 2, 1], 3], [[1, 5, 2], 2], [[1, 5, 2], 1],
           [[1, 5, 2], 5], [[1, 5, 2], 0], [[1, 2, 3, 4, 5, 6, 7, 0], 0], [[1, 2, 3, 4, 5, 6, 7, 0], 7],
           [[INT_MIN, INT_MAX, INT_MIN + 1], INT_MIN + 1], [[INT_MIN, INT_MAX, INT_MIN + 1], INT_MIN],
           [[-5, -2, 0, 3, 8, 6, 4, 1, -2, -9], -2], [[-5, -2, 0, 3, 8, 6, 4, 1, -2, -9], 5]],
)
_r = rnd(8108)
_a = _mountain(_r, 4000, 1700, -10 ** 6, 10 ** 6)
p["tests"].append([_a, _a[3500]])
p["tests"].append([_a, _a[400]])
_b = _mountain(_r, 5000, 4000, -10 ** 6, 10 ** 6)
_b[4500] = _b[1000]  # same value on both slopes? keep strict slopes: only valid if order is preserved
_b = _mountain(_r, 5000, 4000, -10 ** 6, 10 ** 6)
p["tests"].append([_b, -10 ** 6 - 1])


def b_search_mtn(nums, target):
    for i, x in enumerate(nums):
        if x == target:
            return i
    return -1


def g_search_mtn(r):
    return [_rand_mountain(r), r.randint(-7, 7)]


def v_search_mtn(tests):
    both = 0
    for t in tests:
        nums, target = t["args"]
        assert 3 <= len(nums) <= 10000 and _is_mountain(nums)
        assert all(INT_MIN <= v <= INT_MAX for v in nums) and INT_MIN <= target <= INT_MAX
        if nums.count(target) == 2:
            both += 1
    assert both >= 3, "need tests where the target occurs on both slopes"


CHECKS["search-in-mountain-array"] = (b_search_mtn, g_search_mtn, "exact")
VALIDATE["search-in-mountain-array"] = v_search_mtn

p = add(
    id="kth-smallest-in-mountain-array", title="K-th Smallest in a Mountain Array", diff="Hard", topic="Binary Search",
    fn="kthInMountain", params=[("nums", "int[]"), ("k", "int")], ret="int", cmp="exact",
    desc="<p>The array <code>nums</code> is a mountain: strictly increasing up to a peak (neither the first nor the last element), then strictly decreasing. The same value can occur once on each slope.</p><p>Return the <code>k</code>-th smallest element when all elements are sorted in non-decreasing order (counting duplicates, 1-based). Do it without sorting or merging the whole array: aim for O(log n * log V) where V is the value range.</p><p>For example, for <code>nums = [1, 4, 6, 5, 4, 2]</code> the sorted order is <code>1, 2, 4, 4, 5, 6</code>, so <code>k = 4</code> gives <code>4</code> and <code>k = 5</code> gives <code>5</code>.</p>",
    constraints=["3 &le; nums.length &le; 5,000", "1 &le; k &le; nums.length", "-10<sup>9</sup> &le; nums[i] &le; 10<sup>9</sup>", "nums is guaranteed to be a mountain array"],
    hints=["Sorting works in O(n log n). Think about binary searching the <em>value</em> instead: how many elements are &le; x for a given x?",
           "The answer is the smallest value <code>x</code> for which at least <code>k</code> elements are &le; <code>x</code>. The count never decreases as <code>x</code> grows.",
           "Count elements &le; x in O(log n): after locating the peak, the ascending part contributes a prefix (binary search the first value &gt; x) and the descending part contributes a suffix (binary search the first value &le; x). Binary search x between the smaller end of the array and the peak value."],
    editorial=["Define <code>count(x)</code> = the number of elements &le; <code>x</code>. It is non-decreasing in <code>x</code>, and the k-th smallest element is the smallest <code>x</code> with <code>count(x) &ge; k</code>; that <code>x</code> is necessarily an element of the array, because the count only jumps at array values.",
               "Computing <code>count(x)</code> uses the mountain structure. Find the peak once. On the ascending part <code>nums[0..peak]</code> the elements &le; x form a prefix, whose length is the first index with value &gt; x. On the descending part the elements &le; x form a suffix, which starts at the first index with value &le; x. The sum of both lengths is <code>count(x)</code>.",
               "Binary search <code>x</code> over <code>[min(nums[0], nums[n - 1]), nums[peak]]</code>, which takes about 31 rounds for 32-bit values. Each round costs two binary searches of O(log n), so the total is O(log n * log V) time and O(1) space. Merging the two slopes explicitly would take O(n)."],
    time="O(log n log V)", space="O(1)", tier="extra",
    solution='''def kthInMountain(nums, k):
    n = len(nums)
    lo, hi = 0, n - 1
    while lo < hi:
        mid = (lo + hi) // 2
        if nums[mid] < nums[mid + 1]:
            lo = mid + 1
        else:
            hi = mid
    peak = lo

    def count(x):
        a, b = 0, peak + 1
        while a < b:
            m = (a + b) // 2
            if nums[m] <= x:
                a = m + 1
            else:
                b = m
        left = a
        a, b = peak + 1, n
        while a < b:
            m = (a + b) // 2
            if nums[m] <= x:
                b = m
            else:
                a = m + 1
        return left + (n - a)

    lo, hi = min(nums[0], nums[-1]), nums[peak]
    while lo < hi:
        mid = (lo + hi) // 2
        if count(mid) >= k:
            hi = mid
        else:
            lo = mid + 1
    return lo
''',
    tests=[[[1, 4, 6, 5, 4, 2], 4], [[1, 4, 6, 5, 4, 2], 5], [[1, 4, 6, 5, 4, 2], 1], [[1, 4, 6, 5, 4, 2], 6], [[0, 1, 0], 2],
           [[0, 1, 0], 3], [[1, 2, 3, 4, 2], 3], [[5, 9, 8, 7, 6], 2], [[5, 9, 8, 7, 6], 4],
           [[-10 ** 9, 10 ** 9, -10 ** 9 + 1], 2], [[-10 ** 9, 10 ** 9, -10 ** 9 + 1], 3], [[2, 4, 6, 8, 7, 5, 3, 1], 4],
           [[2, 4, 6, 8, 7, 5, 3, 1], 5], [[3, 5, 3], 2]],
)
_r = rnd(8109)
p["tests"].append([_mountain(_r, 3000, 1000, -10 ** 6, 10 ** 6), 1500])
p["tests"].append([_mountain(_r, 4000, 3500, -10 ** 9, 10 ** 9), 3999])
p["tests"].append([_mountain(_r, 4500, 1500, -10 ** 6, 10 ** 6), 2250])


def b_kth_mtn(nums, k):
    return sorted(nums)[k - 1]


def g_kth_mtn(r):
    nums = _rand_mountain(r)
    return [nums, r.randint(1, len(nums))]


def v_kth_mtn(tests):
    for t in tests:
        nums, k = t["args"]
        assert 3 <= len(nums) <= 5000 and _is_mountain(nums)
        assert 1 <= k <= len(nums) and all(-10 ** 9 <= v <= 10 ** 9 for v in nums)


CHECKS["kth-smallest-in-mountain-array"] = (b_kth_mtn, g_kth_mtn, "exact")
VALIDATE["kth-smallest-in-mountain-array"] = v_kth_mtn

p = add(
    id="find-peak-in-grid", title="Find the Peak in a Grid", diff="Hard", topic="Binary Search",
    fn="gridPeak", params=[("grid", "int[][]")], ret="int[]", cmp="exact",
    desc="<p>In the <code>m x n</code> grid, all values are distinct. A cell is a <em>peak</em> if its value is strictly greater than the values of all its existing neighbours (up, down, left and right; cells outside the grid do not count).</p><p>The grid is guaranteed to contain <strong>exactly one</strong> peak. Return its position as <code>[row, col]</code>. A solution that inspects far fewer than <code>m * n</code> cells exists: aim for O(m log n) time.</p><p>For example, in <code>[[10, 20, 15], [21, 30, 14], [7, 16, 12]]</code> only the cell holding <code>30</code> is a peak, so the answer is <code>[1, 1]</code>.</p>",
    constraints=["1 &le; m, n &le; 60", "-10<sup>9</sup> &le; grid[i][j] &le; 10<sup>9</sup>, all values distinct", "The grid contains exactly one peak cell"],
    hints=["Checking every cell for being larger than its neighbours is O(m * n). In 1D you can binary search for a peak by following the larger neighbour. Can the same idea work on columns?",
           "Take the middle column and find the row of its maximum. Compare that cell with its left and right neighbours. If it beats both, it is a peak.",
           "If the left neighbour is bigger, a peak must exist in the columns to the left of the middle (discard the middle column and everything to its right); if the right neighbour is bigger, search to the right. Repeat on the shrinking column range."],
    editorial=["Walking uphill never gets stuck in a corner: from any cell, moving to a larger neighbour repeatedly must end in a peak, because the values are finite and strictly increase along the walk. The binary search uses this to throw away half of the columns each step.",
               "Look at the middle column <code>mid</code> and take the row <code>r</code> where that column is largest. Call the cell <code>X = grid[r][mid]</code>. Its up and down neighbours are smaller than <code>X</code> by the choice of <code>r</code>. If its left and right neighbours are also smaller, X is a peak. Otherwise one side holds a larger neighbour, say the left one. Walking uphill from that neighbour can never cross column <code>mid</code>, because to enter column <code>mid</code> it would have to pass through a cell larger than the neighbour, and every cell of that column is at most X, which is smaller than the neighbour. Hence a peak exists in the columns left of <code>mid</code>. The same argument works on the right.",
               "Each step halves the columns and costs O(m) to find the column maximum, so the total is O(m log n) time and O(1) space. The problem statement promises a single peak, which only makes the answer unique; the algorithm itself finds some peak of any grid with distinct neighbouring values."],
    time="O(m log n)", space="O(1)", tier="common",
    solution='''def gridPeak(grid):
    m, n = len(grid), len(grid[0])
    lo, hi = 0, n - 1
    NEG = float("-inf")
    while lo <= hi:
        mid = (lo + hi) // 2
        r = max(range(m), key=lambda i: grid[i][mid])
        v = grid[r][mid]
        left = grid[r][mid - 1] if mid > 0 else NEG
        right = grid[r][mid + 1] if mid < n - 1 else NEG
        if v > left and v > right:
            return [r, mid]
        if left > v:
            hi = mid - 1
        else:
            lo = mid + 1
    return [-1, -1]
''',
    tests=[[[[1]]], [[[1, 2], [3, 4]]], [[[10, 20, 15], [21, 30, 14], [7, 16, 12]]], [[[5, 3, 1]]], [[[1, 3, 5]]], [[[1], [9], [4]]],
           [[[9], [4], [1]]], [[[1, 2, 3], [6, 5, 4], [7, 8, 9]]], [[[1, 2, 3, 4], [12, 13, 14, 5], [11, 16, 15, 6], [10, 9, 8, 7]]],
           [[[-10 ** 9, 7], [3, 10 ** 9]]]],
)
_r = rnd(8110)


def _hill(r, m, n, lo, hi, snake):
    """Grid of distinct values with exactly one local maximum: every other cell has a larger neighbour."""
    vals = sorted(r.sample(range(lo, hi + 1), m * n), reverse=True)
    g = [[None] * n for _ in range(m)]
    sr, sc = r.randrange(m), r.randrange(n)
    g[sr][sc] = vals[0]
    k = 1
    fr = [(sr, sc)]
    while fr:
        idx = len(fr) - 1 if r.random() < snake else r.randrange(len(fr))
        fr[idx], fr[-1] = fr[-1], fr[idx]
        i, j = fr[-1]
        nb = [(x, y) for x, y in ((i + 1, j), (i - 1, j), (i, j + 1), (i, j - 1)) if 0 <= x < m and 0 <= y < n and g[x][y] is None]
        if not nb:
            fr.pop()
            continue
        x, y = r.choice(nb)
        g[x][y] = vals[k]
        k += 1
        fr.append((x, y))
    return g


p["tests"].append([_hill(_r, 1, 40, -10 ** 6, 10 ** 6, 0.5)])
p["tests"].append([_hill(_r, 40, 1, -10 ** 6, 10 ** 6, 0.5)])
p["tests"].append([_hill(_r, 60, 60, -10 ** 6, 10 ** 6, 0.0)])
p["tests"].append([_hill(_r, 60, 60, -10 ** 6, 10 ** 6, 0.98)])
p["tests"].append([_hill(_r, 55, 60, -10 ** 9, 10 ** 9, 0.9)])
p["tests"].append([_hill(_r, 60, 17, -10 ** 6, 10 ** 6, 0.95)])


def _peaks(g):
    m, n = len(g), len(g[0])
    out = []
    for i in range(m):
        for j in range(n):
            if all(g[i][j] > g[x][y] for x, y in ((i + 1, j), (i - 1, j), (i, j + 1), (i, j - 1)) if 0 <= x < m and 0 <= y < n):
                out.append([i, j])
    return out


def b_grid_peak(grid):
    return _peaks(grid)[0]


def g_grid_peak(r):
    return [_hill(r, r.randint(1, 5), r.randint(1, 5), -50, 50, r.choice((0.0, 0.5, 1.0)))]


def v_grid_peak(tests):
    for t in tests:
        g = t["args"][0]
        m, n = len(g), len(g[0])
        assert 1 <= m <= 60 and 1 <= n <= 60 and all(len(row) == n for row in g)
        flat = [v for row in g for v in row]
        assert len(set(flat)) == len(flat), "values must be distinct"
        assert all(-10 ** 9 <= v <= 10 ** 9 for v in flat)
        assert len(_peaks(g)) == 1, "exactly one peak required"
        assert t["expected"] == _peaks(g)[0]


CHECKS["find-peak-in-grid"] = (b_grid_peak, g_grid_peak, "exact")
VALIDATE["find-peak-in-grid"] = v_grid_peak
