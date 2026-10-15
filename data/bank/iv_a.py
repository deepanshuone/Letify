from lib import add, rnd, CHECKS, VALIDATE, gen_arr  # noqa: F401
from lib import P as _P
from bisect import bisect_left, bisect_right  # noqa: F401

"""Problems: intervals (merge, insert, intersect, subtract, union length, complement)."""

TOPIC = "Intervals"


def _rand_iv(r, n, lo, hi, maxlen, minlen=0):
    """n random intervals [s, e] with lo <= s, e <= hi and minlen <= e - s <= maxlen."""
    out = []
    for _ in range(n):
        ln = r.randint(minlen, maxlen)
        s = r.randint(lo, hi - ln)
        out.append([s, s + ln])
    return out


def _components(intervals, close):
    """Union-find on pairwise 'close' relation; returns a list of index groups."""
    n = len(intervals)
    par = list(range(n))

    def find(x):
        while par[x] != x:
            par[x] = par[par[x]]
            x = par[x]
        return x

    for i in range(n):
        for j in range(i + 1, n):
            if close(intervals[i], intervals[j]):
                par[find(i)] = find(j)
    groups = {}
    for i in range(n):
        groups.setdefault(find(i), []).append(i)
    return list(groups.values())


def _runs(points):
    """Group a set of integers into maximal runs of consecutive integers -> [first, last]."""
    res = []
    for x in sorted(points):
        if res and res[-1][1] == x - 1:
            res[-1][1] = x
        else:
            res.append([x, x])
    return res


# ---------------------------------------------------------------- EASY

add(
    id="total-covered-length", title="Total Covered Length", diff="Easy", topic=TOPIC,
    fn="coveredLength", params=[("intervals", "int[][]")], ret="int", cmp="exact",
    desc="<p>Each element <code>[start, end)</code> of <code>intervals</code> is a half-open stretch of the number line: it covers every point <code>x</code> with <code>start &le; x &lt; end</code>, so its length is <code>end - start</code>. The intervals come in no particular order and may overlap, nest or repeat.</p><p>Return the total length of the number line that is covered by at least one interval. Every point must be counted once, no matter how many intervals cover it.</p><pre>intervals = [[1, 5], [3, 8], [10, 12]]\nresult    = 9</pre><p>The first two intervals together cover <code>[1, 8)</code>, which has length 7, and the last one adds 2 more. Two intervals that only meet, such as <code>[1, 3)</code> and <code>[3, 5)</code>, simply add up to 4.</p>",
    constraints=["0 &le; intervals.length &le; 10,000", "0 &le; start &lt; end &le; 10<sup>9</sup>"],
    hints=["Adding up all lengths over-counts every point that lies in more than one interval. You need a way to count each point once.",
           "Sort the intervals by start. Then the part of an interval that is already covered by earlier intervals is exactly the part to the left of the furthest end seen so far.",
           "Keep <code>reach</code>, the largest end seen so far (start at 0). For each interval with <code>end &gt; reach</code>, add <code>end - max(start, reach)</code> and set <code>reach = end</code>; intervals with <code>end &le; reach</code> add nothing."],
    editorial=["After sorting by start, process the intervals from left to right and remember <code>reach</code>, the right-most point covered so far. The new part contributed by an interval is the portion lying beyond <code>reach</code>, which has length <code>end - max(start, reach)</code> when <code>end &gt; reach</code> and nothing otherwise. Afterwards <code>reach</code> becomes the new end. Each point of the line is counted exactly once, in the first interval (in sorted order) that reaches it.",
               "Sorting costs O(n log n) and the scan is linear. The same result comes from merging overlapping intervals first and summing the lengths of the merged blocks, but the running <code>reach</code> avoids building the merged list. The answer is at most 10<sup>9</sup>, so it fits in 32 bits."],
    time="O(n log n)", space="O(1) extra",
    solution='''def coveredLength(intervals):
    total = 0
    reach = 0
    for s, e in sorted(intervals):
        if e > reach:
            total += e - max(s, reach)
            reach = e
    return total
''',
    tests=[[[[1, 5], [3, 8], [10, 12]]], [[[1, 3], [3, 5]]], [[[0, 10], [2, 3], [4, 6]]], [[]], [[[7, 8]]],
           [[[2, 6], [2, 6], [2, 6]]], [[[5, 9], [0, 2], [3, 4]]], [[[0, 10 ** 9]]],
           [[[0, 500000000], [500000000, 10 ** 9], [1, 2]]], [[[4, 6], [1, 3], [8, 9], [0, 1], [3, 4]]]],
)
_r = rnd(2001)
_P[-1]["tests"].append([[[s, e + 1] for s, e in _rand_iv(_r, 1500, 0, 10 ** 9 - 2, 40000)]])
_P[-1]["tests"].append([[[s, e + 1] for s, e in _rand_iv(_r, 1800, 0, 10 ** 6 - 2, 2000)]])
_P[-1]["tests"].append([[[s, e + 1] for s, e in _rand_iv(_r, 1200, 0, 10 ** 9 - 2, 10 ** 9 - 2, 0)]])


def _b_covered(intervals):
    pts = set()
    for s, e in intervals:
        pts.update(range(s, e))
    return len(pts)


def _g_covered(r):
    return [[[s, e + 1] for s, e in _rand_iv(r, r.randint(0, 7), 0, 19, 8)]]


def _v_covered(tests):
    for t in tests:
        iv = t["args"][0]
        assert 0 <= len(iv) <= 10000
        assert all(0 <= s < e <= 10 ** 9 for s, e in iv)


CHECKS["total-covered-length"] = (_b_covered, lambda r: _g_covered(r), "exact")
VALIDATE["total-covered-length"] = _v_covered

add(
    id="count-contiguous-integer-blocks", title="Count Contiguous Integer Blocks", diff="Easy", topic=TOPIC, tier="extra",
    fn="countBlocks", params=[("intervals", "int[][]")], ret="int", cmp="exact",
    desc="<p>Each element <code>[l, r]</code> of <code>intervals</code> stands for the set of all integers from <code>l</code> to <code>r</code> inclusive. Put all those integers into one big set <code>S</code>.</p><p>Return the number of <em>blocks</em> of <code>S</code>: a block is a maximal run of consecutive integers <code>x, x+1, ..., y</code> that all belong to <code>S</code> (with <code>x - 1</code> and <code>y + 1</code> not in <code>S</code>). Note that intervals which do not overlap but sit directly next to each other, like <code>[1, 2]</code> and <code>[3, 4]</code>, form one block because 2 and 3 are consecutive integers.</p><pre>intervals = [[7, 9], [1, 2], [3, 4], [20, 20]]\nresult    = 3</pre><p>The blocks are <code>1..4</code>, <code>7..9</code> and <code>20..20</code>.</p>",
    constraints=["0 &le; intervals.length &le; 10,000", "-10<sup>9</sup> &le; l &le; r &le; 10<sup>9</sup>"],
    hints=["Listing all integers works only for tiny ranges. Think about how to decide, from the endpoints alone, whether two intervals belong to the same block.",
           "Sort by <code>l</code>. A new block starts exactly when the next interval begins after the current right-most covered integer, with a gap of at least one missing integer in between.",
           "Track <code>reach</code>, the largest <code>r</code> seen so far. If <code>l &gt; reach + 1</code>, a new block starts (count it); in any case set <code>reach = max(reach, r)</code>."],
    editorial=["Compared with ordinary interval merging, the only difference is what counts as 'connected'. Integer intervals <code>[a, b]</code> and <code>[c, d]</code> with <code>b + 1 = c</code> leave no integer uncovered between them, so they belong to the same block. That is why the test is <code>l &gt; reach + 1</code> instead of <code>l &gt; reach</code>.",
               "Sort the intervals by left end and sweep once while keeping the furthest right end. Each time the gap condition holds, a new block begins. Sorting dominates: O(n log n) time, O(1) extra space."],
    time="O(n log n)", space="O(1) extra",
    solution='''def countBlocks(intervals):
    count = 0
    reach = None
    for l, r in sorted(intervals):
        if reach is None or l > reach + 1:
            count += 1
            reach = r
        elif r > reach:
            reach = r
    return count
''',
    tests=[[[[7, 9], [1, 2], [3, 4], [20, 20]]], [[[1, 2], [4, 5]]], [[]], [[[5, 5]]], [[[-3, -1], [0, 0], [1, 1]]],
           [[[1, 10], [2, 3], [4, 5]]], [[[-10 ** 9, 0], [2, 10 ** 9]]], [[[-10 ** 9, 10 ** 9]]],
           [[[3, 3], [3, 3], [5, 5], [4, 4]]], [[[0, 1], [3, 4], [6, 7], [9, 10]]]],
)
_r = rnd(2002)
_P[-1]["tests"].append([_rand_iv(_r, 1500, -10 ** 9, 10 ** 9, 200000)])
_P[-1]["tests"].append([_rand_iv(_r, 2000, 0, 20000, 5)])
_P[-1]["tests"].append([_rand_iv(_r, 1500, -10 ** 6, 10 ** 6, 300)])


def _b_blocks(intervals):
    s = set()
    for l, r in intervals:
        s.update(range(l, r + 1))
    return sum(1 for x in s if x - 1 not in s)


def _v_blocks(tests):
    for t in tests:
        iv = t["args"][0]
        assert 0 <= len(iv) <= 10000
        assert all(-10 ** 9 <= l <= r <= 10 ** 9 for l, r in iv)


CHECKS["count-contiguous-integer-blocks"] = (_b_blocks, lambda r: [_rand_iv(r, r.randint(0, 8), -8, 12, 4)], "exact")
VALIDATE["count-contiguous-integer-blocks"] = _v_blocks

# ---------------------------------------------------------------- MEDIUM

add(
    id="merge-intervals-within-gap", title="Merge Intervals Within a Gap", diff="Medium", topic=TOPIC,
    fn="mergeWithGap", params=[("intervals", "int[][]"), ("gap", "int")], ret="int[][]", cmp="exact",
    desc="<p>You get unsorted closed intervals <code>[start, end]</code> and a tolerance <code>gap</code>. Two intervals are <em>close</em> when the empty space between them is at most <code>gap</code>: that is, when they overlap, or when the later one starts at most <code>gap</code> units after the earlier one ends. Closeness is chained: if A is close to B and B is close to C, all three end up in the same block, even if A and C are far apart.</p><p>Replace every block of connected intervals by the single interval from the smallest start to the largest end in the block. Return these merged intervals sorted by start.</p><pre>intervals = [[1, 3], [6, 8], [2, 4], [20, 25], [11, 12]], gap = 3\nresult    = [[1, 12], [20, 25]]</pre><p>Here <code>[1,3]</code> and <code>[2,4]</code> overlap, <code>[6,8]</code> starts 2 after 4, <code>[11,12]</code> starts 3 after 8, but <code>[20,25]</code> starts 8 after 12. With <code>gap = 0</code> the task is the ordinary merge in which intervals sharing an endpoint are merged.</p>",
    constraints=["1 &le; intervals.length &le; 10,000", "0 &le; start &le; end &le; 10<sup>9</sup>", "0 &le; gap &le; 10<sup>9</sup>"],
    hints=["Process the intervals in order of start, so that each new interval can only be close to the block that was built last.",
           "To decide whether the new interval joins the last block, compare its start with the largest end in that block, not with the end of the previous interval.",
           "Sort by start. If <code>start - lastEnd &le; gap</code> extend <code>lastEnd = max(lastEnd, end)</code>; otherwise open a new block."],
    editorial=["This is the classic merge-intervals sweep with a different join condition. Sort by start. Keep the result list; for the next interval compare <code>start - blockEnd</code> with <code>gap</code>, where <code>blockEnd</code> is the right end of the last block (the maximum end of everything in it). If the distance is at most <code>gap</code> (negative or zero means overlap), the interval joins the block and <code>blockEnd = max(blockEnd, end)</code>; otherwise it starts a new block.",
               "Comparing against the block's maximum end is essential: an earlier long interval can still reach a late start even though the interval just before it ended early. After sorting, nothing later can reach back into a closed block, because starts only grow. Time O(n log n) for the sort, O(n) for the output."],
    time="O(n log n)", space="O(n)",
    solution='''def mergeWithGap(intervals, gap):
    res = []
    for s, e in sorted(intervals):
        if res and s - res[-1][1] <= gap:
            if e > res[-1][1]:
                res[-1][1] = e
        else:
            res.append([s, e])
    return res
''',
    tests=[[[[1, 3], [6, 8], [2, 4], [20, 25], [11, 12]], 3], [[[1, 4], [4, 5]], 0], [[[1, 2], [4, 5]], 1],
           [[[5, 5]], 7], [[[0, 100], [10, 20], [30, 40], [101, 102]], 0], [[[0, 100], [10, 20], [30, 40], [101, 102]], 1],
           [[[1, 1], [3, 3], [5, 5], [7, 7]], 1], [[[1, 1], [3, 3], [5, 5], [7, 7]], 2],
           [[[0, 0], [10 ** 9, 10 ** 9]], 10 ** 9 - 1], [[[0, 0], [10 ** 9, 10 ** 9]], 10 ** 9],
           [[[8, 9], [1, 2], [4, 5]], 2]],
)
_r = rnd(2003)
_P[-1]["tests"].append([_rand_iv(_r, 1200, 0, 10 ** 6, 400), 300])
_P[-1]["tests"].append([_rand_iv(_r, 1000, 0, 10 ** 9, 3000000), 0])
_P[-1]["tests"].append([_rand_iv(_r, 1000, 0, 10 ** 9, 100000), 60000])


def _b_gap(intervals, gap):
    def close(a, b):
        return max(a[0], b[0]) - min(a[1], b[1]) <= gap
    comps = _components(intervals, close)
    out = [[min(intervals[i][0] for i in c), max(intervals[i][1] for i in c)] for c in comps]
    return sorted(out)


def _g_gap(r):
    return [_rand_iv(r, r.randint(1, 8), 0, 30, 5), r.randint(0, 4)]


def _v_gap(tests):
    for t in tests:
        iv, gap = t["args"]
        assert 1 <= len(iv) <= 10000 and 0 <= gap <= 10 ** 9
        assert all(0 <= s <= e <= 10 ** 9 for s, e in iv)


CHECKS["merge-intervals-within-gap"] = (_b_gap, _g_gap, "exact")
VALIDATE["merge-intervals-within-gap"] = _v_gap

add(
    id="merged-block-index-of-each-interval", title="Merged Block Index of Each Interval", diff="Medium", topic=TOPIC, tier="extra",
    fn="blockIndices", params=[("intervals", "int[][]")], ret="int[]", cmp="exact",
    desc="<p>When overlapping closed intervals <code>[start, end]</code> are merged (intervals that share at least one point, such as <code>[1,4]</code> and <code>[4,5]</code>, are merged too), they form disjoint blocks. Number the blocks <code>0, 1, 2, ...</code> from left to right.</p><p>The input list is in no particular order. For every interval of the input, in the given order, return the number of the block it ends up in.</p><pre>intervals = [[8, 9], [1, 4], [4, 6], [2, 3], [6, 7], [20, 21]]\nresult    = [1, 0, 0, 0, 0, 2]</pre><p>The blocks are <code>[1,7]</code> (made of four intervals), <code>[8,9]</code> and <code>[20,21]</code>. The interval <code>[8,9]</code> does not share a point with <code>[6,7]</code>, so it forms its own block.</p>",
    constraints=["1 &le; intervals.length &le; 10,000", "0 &le; start &le; end &le; 10<sup>9</sup>", "Duplicate intervals are allowed"],
    hints=["Merging the intervals gives you the blocks, but sorting loses the original positions. What do you need to remember?",
           "Sort the <em>indices</em> of the intervals by start instead of sorting the intervals themselves.",
           "Sweep over the sorted indices with the usual merge rule. Keep the largest end of the current block; when an interval starts after it, increase the block counter. Write the current counter into <code>result[index]</code>."],
    editorial=["Sort the indices <code>0..n-1</code> by <code>(start, end)</code> and sweep. Maintain <code>block</code> (the number of the current block, starting at -1) and <code>reach</code> (the largest end in the current block). When the next interval's start is greater than <code>reach</code> (or there is no block yet), it opens a new block: increase <code>block</code> and set <code>reach = end</code>; otherwise update <code>reach = max(reach, end)</code>. Store <code>block</code> in <code>result[idx]</code>.",
               "Because the sweep visits intervals in order of start, blocks are numbered from left to right automatically, and an interval can never join a block that was closed earlier. Time O(n log n) for the sort, O(n) space for the answer. Sorting a list of (start, end, index) triples is an equivalent way to carry the positions along."],
    time="O(n log n)", space="O(n)",
    solution='''def blockIndices(intervals):
    n = len(intervals)
    order = sorted(range(n), key=lambda i: intervals[i][0])
    res = [0] * n
    block = -1
    reach = -1
    for i in order:
        s, e = intervals[i]
        if block < 0 or s > reach:
            block += 1
            reach = e
        elif e > reach:
            reach = e
        res[i] = block
    return res
''',
    tests=[[[[8, 9], [1, 4], [4, 6], [2, 3], [7, 7], [20, 21]]], [[[5, 5]]], [[[3, 4], [1, 2]]], [[[1, 2], [1, 2], [1, 2]]],
           [[[0, 10], [1, 2], [3, 4], [11, 12]]], [[[3, 3], [3, 3], [4, 4], [2, 3]]], [[[0, 0], [1, 1], [2, 2], [3, 3]]],
           [[[10, 20], [5, 15], [0, 7], [25, 30], [28, 29], [22, 24]]], [[[0, 10 ** 9], [5, 5]]]],
)
_r = rnd(2004)
_P[-1]["tests"].append([_rand_iv(_r, 1200, 0, 10 ** 6, 400)])
_P[-1]["tests"].append([_rand_iv(_r, 1000, 0, 10 ** 9, 700000)])
_P[-1]["tests"].append([[[x, x] for x in _r.sample(range(0, 3000), 2000)]])


def _b_blockidx(intervals):
    comps = _components(intervals, lambda a, b: a[0] <= b[1] and b[0] <= a[1])
    comps.sort(key=lambda c: min(intervals[i][0] for i in c))
    res = [0] * len(intervals)
    for k, c in enumerate(comps):
        for i in c:
            res[i] = k
    return res


def _v_blockidx(tests):
    for t in tests:
        iv = t["args"][0]
        assert 1 <= len(iv) <= 10000
        assert all(0 <= s <= e <= 10 ** 9 for s, e in iv)


CHECKS["merged-block-index-of-each-interval"] = (_b_blockidx, lambda r: [_rand_iv(r, r.randint(1, 9), 0, 25, 4)], "exact")
VALIDATE["merged-block-index-of-each-interval"] = _v_blockidx

add(
    id="uncovered-ranges-in-window", title="Uncovered Ranges in a Window", diff="Medium", topic=TOPIC,
    fn="uncoveredRanges", params=[("intervals", "int[][]"), ("lo", "int"), ("hi", "int")], ret="int[][]", cmp="exact",
    desc="<p>You are given a window <code>[lo, hi)</code> and a list of half-open intervals <code>[start, end)</code>, with integer endpoints. The intervals are unsorted, may overlap, and may stick out of the window on either side.</p><p>Return the parts of the window that are <em>not</em> covered by any interval, as a sorted list of half-open intervals. Every reported piece must be maximal (two reported pieces never touch) and non-empty. Note that <code>[1, 3)</code> and <code>[3, 5)</code> together leave no hole at 3.</p><pre>lo = 0, hi = 20\nintervals = [[2, 5], [4, 8], [12, 15], [18, 30], [-5, 1]]\nresult    = [[1, 2], [8, 12], [15, 18]]</pre><p>If the whole window is covered, return an empty list.</p>",
    constraints=["0 &le; intervals.length &le; 10,000", "-10<sup>9</sup> &le; start &lt; end &le; 10<sup>9</sup>", "-10<sup>9</sup> &le; lo &lt; hi &le; 10<sup>9</sup>", "The window can be huge, so do not walk through it one integer at a time"],
    hints=["Computing the complement of a union is easiest when the union is built in order from left to right.",
           "Sort the intervals by start and keep <code>reach</code>, the first point of the window that is not yet known to be covered. Initially <code>reach = lo</code>.",
           "For each interval in order: if <code>end &le; reach</code> skip it; if <code>start &gt; reach</code> then <code>[reach, min(start, hi))</code> is a hole; finally set <code>reach = end</code>. After the loop add <code>[reach, hi)</code> if <code>reach &lt; hi</code>."],
    editorial=["Sweep the sorted intervals while keeping <code>reach</code>, the left-most point of the window that is still unexplained. An interval entirely to the left of <code>reach</code> changes nothing. An interval that starts beyond <code>reach</code> proves that <code>[reach, start)</code> is uncovered, because every earlier interval (in sorted order) ends at or before <code>reach</code> and every later one starts even further right. After that, <code>reach</code> jumps to the interval's end.",
               "Clip at the window: stop as soon as <code>reach &ge; hi</code>, and clip a hole's right end to <code>hi</code>. Intervals ending before <code>lo</code> are skipped by the same <code>end &le; reach</code> rule, since <code>reach</code> starts at <code>lo</code>. Half-open ends make touching intervals leave no hole, and the reported holes are maximal automatically. O(n log n) time for the sort, O(1) extra space besides the result."],
    time="O(n log n)", space="O(1) extra",
    solution='''def uncoveredRanges(intervals, lo, hi):
    res = []
    reach = lo
    for s, e in sorted(intervals):
        if e <= reach:
            continue
        if s > reach:
            if s >= hi:
                break
            res.append([reach, s])
        reach = e
        if reach >= hi:
            return res
    if reach < hi:
        res.append([reach, hi])
    return res
''',
    tests=[[[[2, 5], [4, 8], [12, 15], [18, 30], [-5, 1]], 0, 20], [[], 3, 9], [[[0, 10]], 2, 8], [[[1, 3], [3, 5]], 0, 6],
           [[[-10, -1], [21, 30]], 0, 20], [[[5, 6]], 0, 10], [[[0, 4], [4, 8], [8, 12]], 0, 12],
           [[[-10 ** 9, 10 ** 9]], -10 ** 9, 10 ** 9], [[[0, 1]], -10 ** 9, 10 ** 9], [[[7, 9], [1, 3], [4, 6]], 2, 8],
           [[[3, 5], [3, 5], [2, 6]], 4, 5]],
)
_r = rnd(2005)
_P[-1]["tests"].append([[[s, e + 1] for s, e in _rand_iv(_r, 1500, -10 ** 6, 10 ** 6, 300)], -900000, 900000])
_P[-1]["tests"].append([[[s, e + 1] for s, e in _rand_iv(_r, 1000, -10 ** 9, 10 ** 9 - 1, 10 ** 7)], -10 ** 9 + 5, 10 ** 9 - 5])
_P[-1]["tests"].append([[[s, e + 1] for s, e in _rand_iv(_r, 1500, 0, 20000, 12)], 100, 19900])


def _b_uncovered(intervals, lo, hi):
    cov = set()
    for s, e in intervals:
        cov.update(range(max(s, lo), min(e, hi)))
    return [[a, b + 1] for a, b in _runs(x for x in range(lo, hi) if x not in cov)]


def _g_uncovered(r):
    lo = r.randint(-3, 6)
    hi = lo + r.randint(1, 14)
    return [[[s, e + 1] for s, e in _rand_iv(r, r.randint(0, 6), -6, 20, 6)], lo, hi]


def _v_uncovered(tests):
    for t in tests:
        iv, lo, hi = t["args"]
        assert 0 <= len(iv) <= 10000 and -10 ** 9 <= lo < hi <= 10 ** 9
        assert all(-10 ** 9 <= s < e <= 10 ** 9 for s, e in iv)
        res = t["expected"]
        assert all(lo <= a < b <= hi for a, b in res)
        assert all(res[i][1] < res[i + 1][0] for i in range(len(res) - 1))


CHECKS["uncovered-ranges-in-window"] = (_b_uncovered, _g_uncovered, "exact")
VALIDATE["uncovered-ranges-in-window"] = _v_uncovered


def _gen_lists(r, k, per, spread, lo_len, hi_len, lo_gap, hi_gap, start_max):
    """k lists, each with up to `per` disjoint closed intervals separated by at least 1."""
    rows = []
    for j in range(k):
        cur = r.randint(0, start_max)
        for _ in range(per):
            s = cur + r.randint(lo_gap, hi_gap)
            e = s + r.randint(lo_len, hi_len)
            rows.append([j, s, e])
            cur = e + 1
    r.shuffle(rows)
    return rows


add(
    id="intersection-of-k-interval-lists", title="Common Part of K Interval Lists", diff="Medium", topic=TOPIC,
    fn="commonIntervals", params=[("k", "int"), ("intervals", "int[][]")], ret="int[][]", cmp="exact",
    desc="<p>There are <code>k</code> lists of closed intervals with integer endpoints, numbered <code>0</code> to <code>k - 1</code>. All their intervals are stored together in <code>intervals</code> as triples <code>[list, start, end]</code>, in arbitrary order. Inside one list the intervals are disjoint and do not even touch: if two of them belong to the same list, one ends strictly before the other starts. A list may have no triples at all.</p><p>Return the set of points (real numbers) that lie in <em>every</em> one of the <code>k</code> lists, as a sorted list of closed intervals <code>[a, b]</code> with <code>a &le; b</code>. A single shared point gives <code>[a, a]</code>.</p><pre>k = 2\nlist 0: [0,2] [5,10] [13,23] [24,25]\nlist 1: [1,5] [8,12] [15,24] [25,26]\nintervals = [[0,0,2], [0,5,10], [0,13,23], [0,24,25],\n             [1,1,5], [1,8,12], [1,15,24], [1,25,26]]\nresult    = [[1,2], [5,5], [8,10], [15,23], [24,24], [25,25]]</pre>",
    constraints=["1 &le; k &le; 10", "0 &le; intervals.length &le; 10,000", "0 &le; list &lt; k", "0 &le; start &le; end &le; 10<sup>9</sup>", "Within one list, the next start is greater than the previous end"],
    hints=["Intersecting two lists with two pointers is the standard approach. Is there a way to handle all k lists at once?",
           "Count, for a moving point, how many intervals cover it. Because the intervals of one list never overlap, the count equals the number of lists covering that point.",
           "Sweep over all start and end events sorted by position (starts before ends at the same position, since the intervals are closed). A common piece begins when the count reaches <code>k</code> and ends at the next end event while the count is <code>k</code>."],
    editorial=["Turn every interval into two events: a start at <code>start</code> and an end at <code>end</code>. Sort the events by position and, at equal positions, put starts before ends, because closed intervals that share an endpoint still share that point. Walk through the events with a counter of currently open intervals. Since the intervals of a single list are pairwise disjoint, no list can contribute more than one open interval at a time, so the counter is the number of lists that cover the current point.",
               "When a start event raises the counter to <code>k</code>, remember its position as the left end of a common piece. When an end event arrives while the counter equals <code>k</code>, the piece closes at that position; then decrement the counter. Pieces that merely touch cannot occur, because that would need some list to have two touching intervals. With m intervals in total the sort costs O(m log m); the sweep is linear. Folding the lists pairwise with the two-pointer intersection works as well but needs sorted lists first."],
    time="O(m log m)", space="O(m)",
    solution='''def commonIntervals(k, intervals):
    events = []
    for _, s, e in intervals:
        events.append((s, 0))
        events.append((e, 1))
    events.sort()
    count = 0
    begin = 0
    res = []
    for x, kind in events:
        if kind == 0:
            count += 1
            if count == k:
                begin = x
        else:
            if count == k:
                res.append([begin, x])
            count -= 1
    return res
''',
    tests=[[2, [[0, 0, 2], [0, 5, 10], [0, 13, 23], [0, 24, 25], [1, 1, 5], [1, 8, 12], [1, 15, 24], [1, 25, 26]]],
           [1, [[0, 5, 6], [0, 1, 2], [0, 9, 9]]],
           [3, [[0, 0, 10], [1, 2, 8], [2, 4, 6]]],
           [2, [[0, 1, 4]]],
           [2, [[0, 1, 3], [1, 3, 5]]],
           [2, [[0, 1, 3], [1, 4, 5]]],
           [3, [[0, 0, 5], [1, 0, 5], [2, 0, 5], [0, 7, 9], [1, 8, 12], [2, 8, 8]]],
           [2, [[0, 0, 10 ** 9], [1, 0, 10 ** 9]]],
           [4, [[0, 1, 9], [1, 2, 3], [1, 5, 8], [2, 0, 6], [2, 7, 10], [3, 3, 7]]],
           [2, []]],
)
_r = rnd(2006)
_P[-1]["tests"].append([3, _gen_lists(_r, 3, 400, 0, 5, 40, 1, 4, 20)])
_P[-1]["tests"].append([2, _gen_lists(_r, 2, 600, 0, 3, 120, 1, 60, 1000)])
_P[-1]["tests"].append([6, _gen_lists(_r, 6, 190, 0, 30, 90, 1, 6, 30)])


def _b_common(k, intervals):
    if not intervals:
        return []
    lo = min(s for _, s, _ in intervals)
    hi = max(e for _, _, e in intervals)
    res = []
    cur = None
    for p in range(2 * lo, 2 * hi + 2):
        ok = all(any(t == j and 2 * s <= p <= 2 * e for t, s, e in intervals) for j in range(k))
        if ok:
            if cur is None:
                cur = [p, p]
            else:
                cur[1] = p
        elif cur is not None:
            res.append([cur[0] // 2, cur[1] // 2])
            cur = None
    return res


def _g_common(r):
    k = r.randint(1, 3)
    rows = []
    for j in range(k):
        cur = r.randint(0, 3)
        for _ in range(r.randint(0, 4)):
            s = cur + r.randint(0, 3)
            e = s + r.randint(0, 5)
            rows.append([j, s, e])
            cur = e + 1
    r.shuffle(rows)
    return [k, rows]


def _v_common(tests):
    for t in tests:
        k, iv = t["args"]
        assert 1 <= k <= 10 and 0 <= len(iv) <= 10000
        per = {}
        for j, s, e in iv:
            assert 0 <= j < k and 0 <= s <= e <= 10 ** 9
            per.setdefault(j, []).append((s, e))
        for lst in per.values():
            lst.sort()
            assert all(lst[i][1] < lst[i + 1][0] for i in range(len(lst) - 1)), "lists must be disjoint"
        res = t["expected"]
        assert all(a <= b for a, b in res) and all(res[i][1] < res[i + 1][0] for i in range(len(res) - 1))


CHECKS["intersection-of-k-interval-lists"] = (_b_common, _g_common, "exact")
VALIDATE["intersection-of-k-interval-lists"] = _v_common

add(
    id="interval-lists-symmetric-difference", title="Symmetric Difference of Two Interval Lists", diff="Medium", topic=TOPIC, tier="extra",
    fn="symmetricDifference", params=[("first", "int[][]"), ("second", "int[][]")], ret="int[][]", cmp="exact",
    desc="<p>Two lists of half-open intervals <code>[start, end)</code> with integer endpoints are given, each sorted by start and non-overlapping: every interval starts at or after the end of the previous one in the same list (so neighbours may touch). Each list describes a set of points: the points that lie in at least one of its intervals.</p><p>Return the set of points that belong to <em>exactly one</em> of the two sets, as a sorted list of half-open intervals. Report maximal pieces: no two reported pieces may touch or overlap, and none may be empty.</p><pre>first  = [[1, 5], [8, 10]]\nsecond = [[3, 9]]\nresult = [[1, 3], [5, 8], [9, 10]]</pre><p>The points of <code>[3,5)</code> and <code>[8,9)</code> are in both sets and are removed. In <code>[[0,4]]</code> versus <code>[[4,6]]</code> the two sets touch, and the result is the single piece <code>[[0,6]]</code>.</p>",
    constraints=["0 &le; first.length, second.length &le; 5,000", "0 &le; start &lt; end &le; 10<sup>9</sup>", "Within one list, start<sub>i+1</sub> &ge; end<sub>i</sub>"],
    hints=["A point is in the answer when it is in one set but not in the other. Think about the points where this status can change.",
           "The status only changes at interval endpoints. Merge all endpoints of both lists and keep two flags: 'inside the first set' and 'inside the second set'.",
           "Process endpoints in increasing position, applying <em>all</em> events at the same position before looking at the flags (touching intervals of one list then cancel out). The state 'exactly one flag is set' starts a piece when it turns on and closes it when it turns off."],
    editorial=["Collect events <code>(position, list, +1 or -1)</code> for every start and end, and sort them. Walk through the distinct positions; at each one, apply every event located there to the two counters, which are 0 or 1 once all events at that position are applied. Then <code>odd = (inFirst != inSecond)</code> describes the stretch to the right of this position.",
               "If <code>odd</code> turns true, remember the position as the start of a piece; if it turns false, close the piece at this position and append it. A state that stays true across a position (for example, a point where the first set ends and the second one starts) simply continues the same piece, which keeps the output maximal. Sorting is O((n + m) log(n + m)); a merge of the already sorted lists would make the sweep linear."],
    time="O((n + m) log(n + m))", space="O(n + m)",
    solution='''def symmetricDifference(first, second):
    events = []
    for s, e in first:
        events.append((s, 0, 1))
        events.append((e, 0, -1))
    for s, e in second:
        events.append((s, 1, 1))
        events.append((e, 1, -1))
    events.sort()
    inside = [0, 0]
    res = []
    start = None
    i = 0
    while i < len(events):
        x = events[i][0]
        while i < len(events) and events[i][0] == x:
            inside[events[i][1]] += events[i][2]
            i += 1
        odd = (inside[0] > 0) != (inside[1] > 0)
        if odd and start is None:
            start = x
        elif not odd and start is not None:
            res.append([start, x])
            start = None
    return res
''',
    tests=[[[[1, 5], [8, 10]], [[3, 9]]], [[[0, 4]], [[4, 6]]], [[], []], [[[2, 7]], []], [[], [[2, 7]]], [[[1, 5]], [[1, 5]]],
           [[[0, 3], [3, 6]], [[2, 4]]], [[[0, 10]], [[2, 3], [5, 6]]], [[[1, 2], [4, 5], [7, 8]], [[2, 4], [5, 7]]],
           [[[0, 10 ** 9]], [[1, 10 ** 9 - 1]]], [[[0, 5]], [[0, 3]]]],
)
_r = rnd(2007)


def _disjoint_half_open(r, n, gap_lo, gap_hi, len_lo, len_hi, start=0):
    out = []
    cur = start
    for _ in range(n):
        s = cur + r.randint(gap_lo, gap_hi)
        e = s + r.randint(len_lo, len_hi)
        out.append([s, e])
        cur = e
    return out


_P[-1]["tests"].append([_disjoint_half_open(_r, 1200, 0, 6, 1, 20), _disjoint_half_open(_r, 1200, 0, 6, 1, 20)])
_P[-1]["tests"].append([_disjoint_half_open(_r, 700, 1, 400000, 1, 500000), _disjoint_half_open(_r, 700, 1, 400000, 1, 500000)])


def _b_symdiff(first, second):
    a = set()
    b = set()
    for s, e in first:
        a.update(range(s, e))
    for s, e in second:
        b.update(range(s, e))
    return [[x, y + 1] for x, y in _runs(a ^ b)]


def _g_symdiff(r):
    return [_disjoint_half_open(r, r.randint(0, 4), 0, 3, 1, 5), _disjoint_half_open(r, r.randint(0, 4), 0, 3, 1, 5)]


def _v_symdiff(tests):
    for t in tests:
        for lst in t["args"]:
            assert 0 <= len(lst) <= 5000
            assert all(0 <= s < e <= 10 ** 9 for s, e in lst)
            assert all(lst[i][1] <= lst[i + 1][0] for i in range(len(lst) - 1))
        res = t["expected"]
        assert all(a < b for a, b in res) and all(res[i][1] < res[i + 1][0] for i in range(len(res) - 1))


CHECKS["interval-lists-symmetric-difference"] = (_b_symdiff, _g_symdiff, "exact")
VALIDATE["interval-lists-symmetric-difference"] = _v_symdiff

add(
    id="range-fully-covered-queries", title="Is the Range Fully Covered?", diff="Medium", topic=TOPIC,
    fn="coveredQueries", params=[("intervals", "int[][]"), ("queries", "int[][]")], ret="int[]", cmp="exact",
    desc="<p>Each element <code>[l, r]</code> of <code>intervals</code> covers all integers from <code>l</code> to <code>r</code> inclusive; the intervals are unsorted and may overlap. Each query <code>[a, b]</code> (with <code>a &le; b</code>) asks: is <em>every</em> integer from <code>a</code> to <code>b</code> covered by at least one interval?</p><p>The union may be built from several intervals, so a query can be covered even if no single interval contains it. For each query, in order, return <code>1</code> if it is fully covered and <code>0</code> otherwise.</p><pre>intervals = [[1, 3], [4, 6], [9, 12]]\nqueries   = [[2, 5], [1, 6], [6, 9], [10, 11], [0, 3]]\nresult    = [1, 1, 0, 1, 0]</pre><p>Notice that <code>[1,3]</code> and <code>[4,6]</code> do not overlap, but leave no integer in between, so <code>[1,6]</code> is covered. The query <code>[6,9]</code> fails because 7 and 8 are missing.</p>",
    constraints=["0 &le; intervals.length &le; 10,000", "1 &le; queries.length &le; 10,000", "-10<sup>9</sup> &le; l &le; r, a &le; b &le; 10<sup>9</sup>"],
    hints=["Checking every integer of a query is far too slow for big ranges, and testing the query against each interval separately misses unions.",
           "Build the merged blocks first. After merging, a query is covered exactly when it lies inside one single block.",
           "Merge sorted intervals when <code>l &le; blockEnd + 1</code> (adjacent integers leave no hole). For a query, binary-search the last block starting at or before <code>a</code> and check that its end is at least <code>b</code>."],
    editorial=["Sort the intervals by left end and merge them into disjoint blocks, joining two intervals whenever the next one starts at most one past the current end: <code>[1,3]</code> and <code>[4,6]</code> leave no integer uncovered, so they become <code>[1,6]</code>. After merging, there is a hole between any two blocks, so a query range is fully covered if and only if it fits entirely into a single block.",
               "For a query <code>[a, b]</code>, find the last block whose start is at most <code>a</code> with a binary search over the block starts; the query is covered exactly when that block exists and its end is at least <code>b</code>. Building costs O(n log n) and each query O(log n)."],
    time="O((n + q) log n)", space="O(n)",
    solution='''from bisect import bisect_right


def coveredQueries(intervals, queries):
    starts = []
    ends = []
    for l, r in sorted(intervals):
        if ends and l <= ends[-1] + 1:
            if r > ends[-1]:
                ends[-1] = r
        else:
            starts.append(l)
            ends.append(r)
    res = []
    for a, b in queries:
        i = bisect_right(starts, a) - 1
        res.append(1 if i >= 0 and ends[i] >= b else 0)
    return res
''',
    tests=[[[[1, 3], [4, 6], [9, 12]], [[2, 5], [1, 6], [6, 9], [10, 11], [0, 3]]], [[], [[0, 0], [5, 9]]],
           [[[5, 5]], [[5, 5], [4, 5], [5, 6]]], [[[0, 10 ** 9]], [[0, 10 ** 9], [3, 3]]],
           [[[-10 ** 9, -1], [0, 10 ** 9]], [[-10 ** 9, 10 ** 9], [-5, 5]]], [[[1, 2], [4, 5]], [[1, 5], [4, 5], [2, 4]]],
           [[[1, 10], [3, 4], [6, 7]], [[1, 10], [2, 9], [11, 11]]], [[[7, 8], [1, 2], [3, 6]], [[1, 8], [2, 7], [0, 8]]]],
)
_r = rnd(2008)


def _cov_queries(r, intervals, q, maxlen, lo, hi):
    out = []
    for _ in range(q):
        if intervals and r.random() < 0.6:
            l, rr = r.choice(intervals)
            a = r.randint(l, rr)
            b = min(hi, a + r.randint(0, maxlen))
        else:
            a = r.randint(lo, hi)
            b = min(hi, a + r.randint(0, maxlen))
        out.append([a, b])
    return out


_iv = _rand_iv(_r, 1000, 0, 10 ** 6, 600)
_P[-1]["tests"].append([_iv, _cov_queries(_r, _iv, 900, 3000, 0, 10 ** 6)])
_iv = _rand_iv(_r, 800, -10 ** 9, 10 ** 9, 2 * 10 ** 7)
_P[-1]["tests"].append([_iv, _cov_queries(_r, _iv, 800, 5 * 10 ** 7, -10 ** 9, 10 ** 9)])
_iv = [[x, x + _r.randint(0, 3)] for x in range(0, 3000, 3)]
_P[-1]["tests"].append([_iv, _cov_queries(_r, _iv, 700, 400, 0, 3000)])


def _b_covq(intervals, queries):
    s = set()
    for l, r in intervals:
        s.update(range(l, r + 1))
    return [1 if all(x in s for x in range(a, b + 1)) else 0 for a, b in queries]


def _g_covq(r):
    iv = _rand_iv(r, r.randint(0, 6), -5, 15, 4)
    qs = []
    for _ in range(r.randint(1, 6)):
        a = r.randint(-6, 16)
        qs.append([a, a + r.randint(0, 6)])
    return [iv, qs]


def _v_covq(tests):
    for t in tests:
        iv, qs = t["args"]
        assert 0 <= len(iv) <= 10000 and 1 <= len(qs) <= 10000
        assert all(-10 ** 9 <= l <= r <= 10 ** 9 for l, r in iv)
        assert all(-10 ** 9 <= a <= b <= 10 ** 9 for a, b in qs)


CHECKS["range-fully-covered-queries"] = (_b_covq, _g_covq, "exact")
VALIDATE["range-fully-covered-queries"] = _v_covq

# ---------------------------------------------------------------- HARD

add(
    id="covered-length-after-each-insertion", title="Covered Length After Each Insertion", diff="Hard", topic=TOPIC,
    fn="coveredAfterEach", params=[("intervals", "int[][]")], ret="int[]", cmp="exact",
    desc="<p>Half-open intervals <code>[start, end)</code> are painted onto an initially empty number line one after another, in the order given. Painting an interval covers every point <code>x</code> with <code>start &le; x &lt; end</code>; painting already painted points again changes nothing.</p><p>After each painting step, report the total length of the number line that is painted so far. Return these totals, one per interval.</p><pre>intervals = [[1, 5], [3, 8], [10, 12], [0, 20], [2, 4]]\nresult    = [4, 7, 9, 20, 20]</pre><p>After the first two steps <code>[1, 8)</code> is painted (length 7); the interval <code>[0, 20)</code> then swallows everything.</p>",
    constraints=["1 &le; intervals.length &le; 100,000", "0 &le; start &lt; end &le; 10<sup>9</sup>"],
    hints=["Recomputing the union from scratch after every step is O(n log n) per step. Painting is permanent, so what work can be reused?",
           "Each unit of length is painted for the first time exactly once. If you could jump directly over parts that are already painted, the total work would stay small.",
           "Compress all endpoints into sorted coordinates; the pieces between consecutive coordinates are 'elementary segments'. For each new interval visit only its still unpainted elementary segments, using a union-find 'next unpainted segment' pointer to skip painted ones."],
    editorial=["Collect every endpoint, sort and deduplicate them: <code>xs[0] &lt; xs[1] &lt; ...</code>. Between two neighbouring coordinates lies one elementary segment, and every interval is exactly a run of consecutive elementary segments. A segment is either painted or not, and once painted stays painted.",
               "Keep a union-find forest <code>nxt</code> where <code>find(i)</code> returns the first unpainted segment with index &ge; i. To paint the interval covering segments <code>[i0, i1)</code>, start at <code>i = find(i0)</code>; while <code>i &lt; i1</code>, add <code>xs[i+1] - xs[i]</code> to the running total, mark the segment painted by pointing it to <code>i + 1</code>, and continue at <code>find(i + 1)</code>. Every segment is painted at most once, so the total work is near-linear after the O(n log n) sort. An alternative is to keep the painted blocks in a sorted list and merge with binary search, which is simpler but can degrade to quadratic list shifting."],
    time="O(n log n)", space="O(n)",
    solution='''def coveredAfterEach(intervals):
    xs = sorted({x for iv in intervals for x in iv})
    idx = {x: i for i, x in enumerate(xs)}
    nxt = list(range(len(xs)))

    def find(i):
        root = i
        while nxt[root] != root:
            root = nxt[root]
        while nxt[i] != root:
            nxt[i], i = root, nxt[i]
        return root

    total = 0
    res = []
    for s, e in intervals:
        hi = idx[e]
        i = find(idx[s])
        while i < hi:
            total += xs[i + 1] - xs[i]
            nxt[i] = i + 1
            i = find(i + 1)
        res.append(total)
    return res
''',
    tests=[[[[1, 5], [3, 8], [10, 12], [0, 20], [2, 4]]], [[[4, 9]]], [[[0, 3], [3, 6], [6, 9]]], [[[2, 3], [2, 3], [2, 3]]],
           [[[10, 20], [0, 5], [5, 10], [20, 25]]], [[[0, 10 ** 9], [5, 6]]], [[[5, 6], [0, 10 ** 9]]],
           [[[1, 2], [3, 4], [5, 6], [7, 8], [2, 7], [0, 9]]], [[[0, 1], [10 ** 9 - 1, 10 ** 9], [1, 10 ** 9 - 1]]]],
)
_r = rnd(2009)
_P[-1]["tests"].append([[[s, e + 1] for s, e in _rand_iv(_r, 1500, 0, 10 ** 6 - 2, 300)]])
_P[-1]["tests"].append([[[s, e + 1] for s, e in _rand_iv(_r, 1200, 0, 10 ** 9 - 2, 40000000)]])
_P[-1]["tests"].append([[[s, e + 1] for s, e in _rand_iv(_r, 1500, 0, 100000, 4)]])


def _b_coveredafter(intervals):
    pts = set()
    out = []
    for s, e in intervals:
        pts.update(range(s, e))
        out.append(len(pts))
    return out


def _v_coveredafter(tests):
    for t in tests:
        iv = t["args"][0]
        assert 1 <= len(iv) <= 100000
        assert all(0 <= s < e <= 10 ** 9 for s, e in iv)


CHECKS["covered-length-after-each-insertion"] = (_b_coveredafter, lambda r: [[[s, e + 1] for s, e in _rand_iv(r, r.randint(1, 9), 0, 18, 7)]], "exact")
VALIDATE["covered-length-after-each-insertion"] = _v_coveredafter

add(
    id="tracked-ranges-add-remove-query", title="Tracked Ranges: Add, Remove, Query", diff="Hard", topic=TOPIC,
    fn="trackedRanges", params=[("ops", "int[][]")], ret="int[]", cmp="exact",
    desc="<p>A tracker remembers a set of integers, initially empty. You are given a list of operations <code>ops</code>; each operation is a triple <code>[type, a, b]</code> that refers to the half-open range <code>[a, b)</code>, i.e. the integers <code>a, a+1, ..., b-1</code> (so <code>a &lt; b</code>):</p><ul><li><code>type = 1</code>: start tracking every integer of the range (integers already tracked stay tracked).</li><li><code>type = 2</code>: stop tracking every integer of the range.</li><li><code>type = 3</code>: query. Is <em>every</em> integer of the range currently tracked?</li></ul><p>Process the operations in order. Return an array with one entry per <em>query</em> operation (in order): <code>1</code> if all integers of the range are tracked, else <code>0</code>. Operations of type 1 and 2 produce no output.</p><pre>ops = [[1,10,20], [3,14,16], [2,14,16], [3,10,14], [3,13,15], [3,16,17]]\nresult = [1, 1, 0, 1]</pre><p>After the removal of <code>[14,16)</code>, the range <code>[10,14)</code> is still fully tracked, <code>[13,15)</code> is not, and <code>[16,17)</code> is.</p>",
    constraints=["1 &le; ops.length &le; 100,000", "type &isin; {1, 2, 3}", "0 &le; a &lt; b &le; 10<sup>9</sup>", "There is at least one query operation"],
    hints=["Storing every tracked integer is impossible for ranges of size 10<sup>9</sup>. Store the tracked set as a few disjoint blocks instead.",
           "Keep two parallel sorted lists <code>starts</code> and <code>ends</code> of disjoint blocks, and locate the affected blocks with binary search. Blocks that touch should be fused, otherwise a query could be wrongly answered 0.",
           "Add: the blocks with <code>end &ge; a</code> and <code>start &le; b</code> are replaced by one block. Remove: the blocks overlapping <code>[a, b)</code> are cut, leaving at most a left remainder and a right remainder. Query: find the last block with <code>start &le; a</code> and test <code>end &ge; b</code>."],
    editorial=["Represent the tracked set as sorted, pairwise separated blocks <code>[s, e)</code> stored in two parallel lists, so <code>bisect</code> can locate them. Separated means that no two blocks overlap or touch; this canonical form makes queries trivial: a range is fully tracked exactly when a single block contains it.",
               "Add <code>[a, b)</code>: the blocks that overlap or touch it are exactly those with <code>end &ge; a</code> and <code>start &le; b</code>, which form a contiguous slice <code>[i, j)</code> found by two binary searches; replace the slice by one block from <code>min(a, starts[i])</code> to <code>max(b, ends[j-1])</code>. Remove <code>[a, b)</code>: the blocks with <code>end &gt; a</code> and <code>start &lt; b</code> are the overlapping slice; replace it with the part of its first block left of <code>a</code> and the part of its last block right of <code>b</code>, if they are non-empty. Query: take the last block with <code>start &le; a</code> and test <code>end &ge; b</code>. Each operation costs O(log n) for the searches plus the cost of the list splice; amortised, every block is created once and deleted at most once. A balanced tree or a sorted-container structure removes the memmove cost of the splice."],
    time="O(log n) searches + splice per operation", space="O(n)",
    solution='''from bisect import bisect_left, bisect_right


def trackedRanges(ops):
    starts = []
    ends = []
    res = []
    for t, a, b in ops:
        if t == 3:
            i = bisect_right(starts, a) - 1
            res.append(1 if i >= 0 and ends[i] >= b else 0)
        elif t == 1:
            i = bisect_left(ends, a)
            j = bisect_right(starts, b)
            if i < j:
                a = min(a, starts[i])
                b = max(b, ends[j - 1])
            starts[i:j] = [a]
            ends[i:j] = [b]
        else:
            i = bisect_right(ends, a)
            j = bisect_left(starts, b)
            ns = []
            ne = []
            if i < j:
                if starts[i] < a:
                    ns.append(starts[i])
                    ne.append(a)
                if ends[j - 1] > b:
                    ns.append(b)
                    ne.append(ends[j - 1])
            starts[i:j] = ns
            ends[i:j] = ne
    return res
''',
    tests=[[[[1, 10, 20], [3, 14, 16], [2, 14, 16], [3, 10, 14], [3, 13, 15], [3, 16, 17]]],
           [[[3, 0, 1]]],
           [[[1, 5, 10], [1, 10, 15], [3, 5, 15], [3, 4, 6]]],
           [[[1, 0, 10 ** 9], [2, 100, 200], [3, 0, 100], [3, 99, 101], [3, 200, 10 ** 9], [1, 150, 160], [3, 100, 200], [3, 150, 160]]],
           [[[1, 1, 3], [1, 5, 7], [1, 3, 5], [3, 1, 7], [2, 3, 5], [3, 1, 7], [3, 1, 3], [3, 5, 7]]],
           [[[1, 2, 4], [2, 0, 10], [3, 2, 3], [1, 2, 3], [3, 2, 3], [3, 2, 4]]],
           [[[1, 10, 20], [1, 30, 40], [1, 50, 60], [2, 15, 55], [3, 10, 15], [3, 55, 60], [3, 30, 40], [1, 15, 55], [3, 10, 60]]],
           [[[2, 5, 6], [3, 5, 6], [1, 5, 6], [2, 5, 6], [3, 5, 6]]],
           [[[1, 0, 5], [2, 5, 9], [3, 0, 5], [3, 0, 6], [1, 5, 9], [3, 0, 9], [2, 2, 3], [3, 0, 9], [3, 3, 9]]]],
)
_r = rnd(2010)


def _gen_ops(r, n, hi, add_len, rem_len, q_len):
    ops = []
    added = []
    for _ in range(n):
        x = r.random()
        if x < 0.35:
            ln = r.randint(1, add_len)
            a = r.randint(0, hi - ln)
            ops.append([1, a, a + ln])
            added.append((a, a + ln))
        elif x < 0.6:
            ln = r.randint(1, rem_len)
            a = r.randint(0, hi - ln)
            ops.append([2, a, a + ln])
        else:
            if added and r.random() < 0.6:
                s, e = r.choice(added)
                a = r.randint(s, e - 1)
                b = min(e, a + r.randint(1, q_len))
            else:
                ln = r.randint(1, q_len)
                a = r.randint(0, hi - ln)
                b = a + ln
            ops.append([3, a, b])
    ops.append([3, 0, 1])
    return ops


_P[-1]["tests"].append([_gen_ops(_r, 1500, 10 ** 6, 20000, 3000, 400)])
_P[-1]["tests"].append([_gen_ops(_r, 1500, 5000, 300, 60, 40)])
_P[-1]["tests"].append([_gen_ops(_r, 1200, 10 ** 9, 10 ** 8, 10 ** 7, 10 ** 6)])


def _b_tracked(ops):
    s = set()
    res = []
    for t, a, b in ops:
        if t == 1:
            s.update(range(a, b))
        elif t == 2:
            s.difference_update(range(a, b))
        else:
            res.append(1 if all(x in s for x in range(a, b)) else 0)
    return res


def _g_tracked(r):
    ops = []
    for _ in range(r.randint(1, 14)):
        t = r.choice([1, 1, 2, 3, 3])
        a = r.randint(0, 14)
        ops.append([t, a, a + r.randint(1, 6)])
    ops.append([3, r.randint(0, 10), r.randint(11, 16)])
    return [ops]


def _v_tracked(tests):
    for t in tests:
        ops = t["args"][0]
        assert 1 <= len(ops) <= 100000
        assert all(o[0] in (1, 2, 3) and 0 <= o[1] < o[2] <= 10 ** 9 for o in ops)
        assert any(o[0] == 3 for o in ops)
        assert len(t["expected"]) == sum(1 for o in ops if o[0] == 3)


CHECKS["tracked-ranges-add-remove-query"] = (_b_tracked, _g_tracked, "exact")
VALIDATE["tracked-ranges-add-remove-query"] = _v_tracked

add(
    id="max-union-after-removing-one-interval", title="Best Union After Removing One Interval", diff="Hard", topic=TOPIC, tier="extra",
    fn="bestUnionAfterRemoval", params=[("intervals", "int[][]")], ret="int", cmp="exact",
    desc="<p>You have a list of half-open intervals <code>[start, end)</code>. You must delete <em>exactly one</em> interval from the list. The remaining intervals cover some part of the number line; the total length of that covered part (every point counted once) is the value of the remaining list.</p><p>Return the largest value you can obtain by choosing the interval to delete well. If the list has only one interval, deleting it leaves nothing, so the answer is <code>0</code>.</p><pre>intervals = [[1, 5], [4, 8], [10, 12]]\nresult    = 7</pre><p>The union of all three has length 9. Deleting <code>[10,12)</code> loses 2 and leaves <code>[1,8)</code>, of length 7; deleting either of the others loses 3.</p>",
    constraints=["1 &le; intervals.length &le; 10,000", "0 &le; start &lt; end &le; 10<sup>9</sup>"],
    hints=["Recomputing the union length for every possible deletion costs O(n<sup>2</sup> log n). Instead ask: how much length do you lose when interval i disappears?",
           "You lose exactly the length that is covered by interval i <em>and by no other interval</em>. The answer is the total union length minus the smallest such 'private' length.",
           "Sweep over sorted start/end events. Between two consecutive event positions, if exactly one interval is active, add the stretch length to that interval's private total. To know which interval it is, keep the running sum of the ids of the active intervals."],
    editorial=["Let <code>U</code> be the length of the union of all intervals, and for each interval i let <code>excl[i]</code> be the length of the points covered by i alone. Deleting interval i removes exactly those points from the union, so the new value is <code>U - excl[i]</code>. The best choice is the interval with the smallest <code>excl[i]</code> (a fully redundant interval has 0), and the answer is <code>U - min(excl)</code>.",
               "Compute <code>U</code> and all <code>excl[i]</code> with one sweep. Create events <code>(position, +id)</code> at starts and <code>(position, -id)</code> at ends together with a counter of active intervals, and sort them. Walking through the events, the stretch between the previous and the current position is added to <code>U</code> if at least one interval is active; if exactly one is active, its id equals the running sum of active ids, so the stretch is credited to <code>excl[sum]</code>. Sorting makes it O(n log n) in total, with O(n) space."],
    time="O(n log n)", space="O(n)",
    solution='''def bestUnionAfterRemoval(intervals):
    n = len(intervals)
    events = []
    for i, (s, e) in enumerate(intervals):
        events.append((s, 1, i))
        events.append((e, -1, i))
    events.sort()
    excl = [0] * n
    union = 0
    count = 0
    idsum = 0
    prev = 0
    for x, d, i in events:
        if count >= 1:
            union += x - prev
            if count == 1:
                excl[idsum] += x - prev
        prev = x
        count += d
        idsum += d * i
    return union - min(excl)
''',
    tests=[[[[1, 5], [4, 8], [10, 12]]], [[[3, 9]]], [[[1, 4], [1, 4]]], [[[0, 10], [2, 3], [4, 5]]], [[[0, 5], [5, 10]]],
           [[[0, 10], [0, 10], [0, 10]]], [[[0, 4], [2, 6], [4, 8], [6, 10]]], [[[0, 10 ** 9], [1, 2]]],
           [[[0, 3], [10, 11], [20, 25]]], [[[5, 7], [1, 3], [2, 6]]]],
)
_r = rnd(2011)
_P[-1]["tests"].append([[[s, e + 1] for s, e in _rand_iv(_r, 1200, 0, 10 ** 6 - 2, 400)]])
_P[-1]["tests"].append([[[s, e + 1] for s, e in _rand_iv(_r, 1000, 0, 10 ** 9 - 2, 600000)]])
_P[-1]["tests"].append([[[s, e + 1] for s, e in _rand_iv(_r, 1500, 0, 4000, 6)]])


def _b_bestunion(intervals):
    best = 0
    for i in range(len(intervals)):
        pts = set()
        for j, (s, e) in enumerate(intervals):
            if j != i:
                pts.update(range(s, e))
        best = max(best, len(pts))
    return best


def _v_bestunion(tests):
    for t in tests:
        iv = t["args"][0]
        assert 1 <= len(iv) <= 10000
        assert all(0 <= s < e <= 10 ** 9 for s, e in iv)


CHECKS["max-union-after-removing-one-interval"] = (_b_bestunion, lambda r: [[[s, e + 1] for s, e in _rand_iv(r, r.randint(1, 7), 0, 18, 7)]], "exact")
VALIDATE["max-union-after-removing-one-interval"] = _v_bestunion
