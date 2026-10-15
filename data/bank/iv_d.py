"""Problems: interval greedy and covering (arrows, stitching, taps, removal, covering ranges). See data/lib.py for the registry."""
from bisect import bisect_right
from itertools import combinations

from lib import add, rnd, CHECKS, VALIDATE, gen_arr  # noqa: F401

TOPIC = "Intervals"


def _closed(r, n, lo, hi, maxlen):
    """n random closed intervals [a, b] with lo <= a < b <= hi."""
    out = []
    for _ in range(n):
        a = r.randint(lo, hi - 1)
        out.append([a, min(hi, a + r.randint(1, maxlen))])
    return out


# ---------------------------------------------------------------- EASY

p = add(
    id="fewest-planks-to-cover-points", title="Fewest Planks to Cover Points", diff="Easy", topic=TOPIC,
    fn="fewestPlanks", params=[("points", "int[]"), ("length", "int")], ret="int", cmp="exact",
    desc="<p>Some leaks appear along a straight pipe at the positions listed in <code>points</code> (several leaks may share a position). You have an unlimited supply of identical repair planks, each of length <code>length</code>. A plank laid with its left end at position <code>x</code> seals every leak at positions from <code>x</code> to <code>x + length</code>, inclusive. Planks may be placed at any real position and may overlap.</p><p>Return the minimum number of planks needed to seal all leaks. If there are no leaks, return <code>0</code>.</p><pre>points = [4, 1, 9, 2, 6, 5], length = 3  -&gt;  3</pre><p>Planks at 1 (covers 1, 2, 4), at 5 (covers 5, 6) and at 9 (covers 9).</p>",
    constraints=["0 &le; points.length &le; 10,000", "0 &le; points[i] &le; 10<sup>9</sup>", "0 &le; length &le; 10<sup>9</sup>", "The points are in no particular order and may repeat"],
    hints=["Think about the leak that is furthest to the left. Some plank has to cover it. Where is the best place for that plank?",
           "Moving the plank further left never helps, because there is nothing to the left of that leak. So put the plank's left end exactly on the leftmost leak.",
           "Sort the points. Start a plank at the first unsealed point, skip every point up to <code>start + length</code>, and repeat with the next unsealed point."],
    editorial=["Sort the positions. The leftmost leak must be sealed by some plank, and sliding that plank to the right until its left end touches the leak can only make it cover more leaks on the right side without losing any (nothing lies left of the leak). So an optimal solution can always start with a plank whose left end is at the leftmost leak. That plank seals every leak up to <code>first + length</code>. Remove them and repeat: this exchange argument shows the greedy choice is safe at every step.",
               "Implementation: walk through the sorted array once with a pointer; whenever the current point is beyond the end of the last plank, open a new plank at this point and set its end to <code>point + length</code>. Sorting costs O(n log n), the scan is O(n)."],
    time="O(n log n)", space="O(n)",
    solution='''def fewestPlanks(points, length):
    count = 0
    covered_until = None
    for x in sorted(points):
        if covered_until is None or x > covered_until:
            count += 1
            covered_until = x + length
    return count
''',
    tests=[[[4, 1, 9, 2, 6, 5], 3], [[], 5], [[7], 0], [[3, 3, 3], 0], [[1, 2, 3, 4, 5], 0], [[1, 2, 3, 4, 5], 4], [[1, 5, 9], 3],
           [[1, 5, 9], 4], [[0, 1000000000], 999999999], [[0, 1000000000], 1000000000], [[10, 20, 30, 40, 50, 60], 15]],
)
_r = rnd(5101)
p["tests"].append([[_r.randint(0, 1000000) for _ in range(4000)], 300])
p["tests"].append([[_r.randint(0, 10 ** 9) for _ in range(3000)], 20000000])
p["tests"].append([[i * 3 for i in range(3500, 0, -1)], 7])


def b_planks(points, length):
    q = sorted(points)
    n = len(q)
    dp = [0] + [10 ** 9] * n
    for i in range(1, n + 1):
        for j in range(i):
            if q[i - 1] - q[j] <= length:
                dp[i] = min(dp[i], dp[j] + 1)
    return dp[n]


def g_planks(r):
    return [[r.randint(0, 20) for _ in range(r.randint(0, 10))], r.randint(0, 8)]


def v_planks(tests):
    for t in tests:
        pts, ln = t["args"]
        assert len(pts) <= 10000 and all(0 <= x <= 10 ** 9 for x in pts) and 0 <= ln <= 10 ** 9


CHECKS["fewest-planks-to-cover-points"] = (b_planks, g_planks, "exact")
VALIDATE["fewest-planks-to-cover-points"] = v_planks

# ------------------------------------------------------------------

p = add(
    id="count-intervals-not-covered-by-another", title="Intervals Not Covered by Another", diff="Easy", topic=TOPIC,
    fn="countUncovered", params=[("intervals", "int[][]")], ret="int", cmp="exact",
    desc="<p>Each interval <code>[a, b]</code> is a closed range with <code>a &lt; b</code>. Interval <code>[a, b]</code> is <em>covered</em> by interval <code>[c, d]</code> when <code>c &le; a</code> and <code>b &le; d</code>, that is, it lies completely inside the other one.</p><p>All intervals in the list are pairwise different. Return how many intervals are <strong>not</strong> covered by any other interval of the list.</p><pre>intervals = [[1, 4], [3, 6], [2, 8]]  -&gt;  2</pre><p><code>[3, 6]</code> lies inside <code>[2, 8]</code>; the other two are not covered by anything.</p>",
    constraints=["0 &le; intervals.length &le; 10,000", "intervals[i] = [a, b] with 0 &le; a &lt; b &le; 10<sup>9</sup>", "All intervals are distinct as pairs [a, b]"],
    hints=["Checking every pair is O(n<sup>2</sup>). Can an ordering of the intervals remove the need to compare all pairs?",
           "Sort by start ascending, and for equal starts by end <em>descending</em>. After that, any interval that could cover the current one comes earlier in the list.",
           "Walk through the sorted list while keeping the largest end seen so far. The current interval is covered exactly when its end does not exceed that maximum."],
    editorial=["After sorting by start ascending (ties: end descending), every interval that could cover interval <code>i</code> has start &le; <code>start[i]</code>, and if the starts are equal it has a larger end, so it appears before <code>i</code>. Therefore interval <code>i</code> is covered if and only if some earlier interval has end &ge; <code>end[i]</code>, which is the same as saying the running maximum end is &ge; <code>end[i]</code>.",
               "So one pass is enough: if <code>end &gt; max_end</code>, the interval is uncovered, count it, and update the maximum. Without the tie-break, two intervals with the same start and different ends would be handled in the wrong order. Time is O(n log n) for the sort, extra space O(n) for the sorted copy."],
    time="O(n log n)", space="O(n)",
    solution='''def countUncovered(intervals):
    ordered = sorted(intervals, key=lambda iv: (iv[0], -iv[1]))
    count = 0
    max_end = -1
    for a, b in ordered:
        if b > max_end:
            count += 1
            max_end = b
    return count
''',
    tests=[[[[1, 4], [3, 6], [2, 8]]], [[]], [[[1, 2]]], [[[1, 2], [1, 4], [3, 4]]], [[[1, 4], [2, 3]]], [[[1, 4], [1, 3], [1, 2]]],
           [[[1, 2], [2, 3], [3, 4]]], [[[1, 5], [2, 6], [3, 7], [4, 8]]], [[[0, 1000000000], [0, 999999999], [1, 1000000000]]],
           [[[5, 9], [1, 3], [2, 4], [1, 10]]]],
)
_r = rnd(5102)


def _distinct(r, n, lo, hi, maxlen):
    seen = set()
    out = []
    while len(out) < n:
        a = r.randint(lo, hi - 1)
        b = min(hi, a + r.randint(1, maxlen))
        if (a, b) not in seen:
            seen.add((a, b))
            out.append([a, b])
    return out


p["tests"].append([_distinct(_r, 2200, 0, 1000000, 400)])
p["tests"].append([_distinct(_r, 2200, 0, 100000, 100000)])
_a = [[i * 5, i * 5 + _r.randint(1, 5)] for i in range(2000)]  # staircase: no interval covers another
_r.shuffle(_a)
p["tests"].append([_a])


def b_uncov(intervals):
    res = 0
    for i, (a, b) in enumerate(intervals):
        if not any(j != i and c <= a and b <= d for j, (c, d) in enumerate(intervals)):
            res += 1
    return res


def g_uncov(r):
    return [_distinct(r, r.randint(0, 7), 0, 9, 6)]


def v_uncov(tests):
    for t in tests:
        iv = t["args"][0]
        assert len(iv) <= 10000
        assert all(0 <= a < b <= 10 ** 9 for a, b in iv)
        assert len({(a, b) for a, b in iv}) == len(iv), "intervals must be distinct"


CHECKS["count-intervals-not-covered-by-another"] = (b_uncov, g_uncov, "exact")
VALIDATE["count-intervals-not-covered-by-another"] = v_uncov

# ---------------------------------------------------------------- MEDIUM

p = add(
    id="min-clips-to-cover-time", title="Fewest Clips to Cover the Timeline", diff="Medium", topic=TOPIC,
    fn="minClips", params=[("clips", "int[][]"), ("T", "int")], ret="int", cmp="exact",
    desc="<p>A highlight reel must show every moment of an event lasting <code>T</code> seconds, i.e. the whole time range <code>[0, T]</code>, without gaps. You are given recorded clips; clip <code>[s, e]</code> shows every moment from second <code>s</code> to second <code>e</code>, inclusive. Clips may overlap, and you may cut a clip into pieces (so using a clip simply means its whole range is available).</p><p>Return the minimum number of clips whose combined ranges cover all of <code>[0, T]</code>, or <code>-1</code> if this is impossible. Two clips that merely touch, such as <code>[0, 3]</code> and <code>[3, 5]</code>, leave no gap.</p><pre>clips = [[0, 3], [2, 6], [5, 9], [1, 4], [8, 12]], T = 12  -&gt;  4\nclips = [[0, 2], [3, 5]], T = 5                         -&gt;  -1</pre><p>In the second example the moment 2.5 is not shown by any clip.</p>",
    constraints=["1 &le; clips.length &le; 3,000", "clips[i] = [s, e] with 0 &le; s &lt; e &le; 10<sup>9</sup>", "1 &le; T &le; 10<sup>9</sup>"],
    hints=["Imagine you have already covered the timeline from 0 up to some moment <code>reach</code>. Which clips can you use next?",
           "Only clips with <code>s &le; reach</code> can extend the covered part without leaving a gap, and among those the one with the largest end is never worse than the others.",
           "This is the jump-game idea. Sort by start. Repeat: among all clips starting at or before the current reach take the largest end, count one clip, and move the reach there. Stop when the reach is at least <code>T</code>, or return -1 if the reach cannot grow."],
    editorial=["Let <code>reach</code> be the furthest moment such that <code>[0, reach]</code> is already covered (initially 0). Any clip that helps must start at or before <code>reach</code>; if none of them ends beyond <code>reach</code> the timeline cannot be completed. Among clips that start at or before <code>reach</code>, picking the one with the maximum end leaves us in a position at least as good as any other pick, because every later clip that is usable after another choice is also usable after this one. This is the usual exchange argument for interval covering.",
               "Sort clips by start time and scan with an index. In each round, advance the index over all clips with <code>s &le; reach</code> while recording the best end; if the best end does not exceed <code>reach</code>, return -1; otherwise count a clip and set <code>reach</code> to the best end. Stop as soon as <code>reach &ge; T</code>. Each clip is looked at once after sorting: O(n log n) time and O(n) space."],
    time="O(n log n)", space="O(n)",
    solution='''def minClips(clips, T):
    ordered = sorted(clips)
    n = len(ordered)
    reach = 0
    count = 0
    i = 0
    while reach < T:
        best = reach
        while i < n and ordered[i][0] <= reach:
            if ordered[i][1] > best:
                best = ordered[i][1]
            i += 1
        if best == reach:
            return -1
        count += 1
        reach = best
    return count
''',
    tests=[[[[0, 3], [2, 6], [5, 9], [1, 4], [8, 12]], 12], [[[0, 2], [3, 5]], 5], [[[0, 5]], 5], [[[0, 5]], 6], [[[1, 5]], 3],
           [[[0, 2], [2, 4], [4, 6]], 6], [[[0, 100], [0, 1], [99, 100]], 100], [[[0, 1], [1, 2], [2, 3], [0, 3]], 3],
           [[[0, 4], [3, 5], [4, 9], [8, 10], [2, 7]], 10], [[[0, 1000000000]], 1000000000], [[[0, 5], [6, 10]], 10],
           [[[5, 10], [0, 3], [2, 6]], 10]],
)
_r = rnd(5103)


def _chain(r, T, extra, step):
    """A feasible cover of [0, T] built as a random chain, plus noise clips (some may reach beyond T)."""
    out = []
    pos = 0
    while pos < T:
        s = max(0, pos - r.randint(0, step))
        e = min(T + r.randint(0, 3), pos + r.randint(1, step))
        e = max(e, pos + 1)
        out.append([s, e])
        pos = e
    for _ in range(extra):
        s = r.randint(0, T - 1)
        out.append([s, min(T + 2, s + r.randint(1, step))])
    r.shuffle(out)
    return out


p["tests"].append([_chain(_r, 60000, 800, 60), 60000])
_c = _chain(_r, 400000, 800, 400)
_c = [x for x in _c if not (x[0] <= 200000 < x[1])]  # a hole around 200000: infeasible
p["tests"].append([_c, 400000])
p["tests"].append([[[i, i + 2] for i in range(1500)] + [[0, 1], [1700, 1701]], 1501])


def b_clips(clips, T):
    INF = 10 ** 9
    f = [0] + [INF] * T
    for x in range(1, T + 1):
        for s, e in clips:
            if s <= x - 1 and e >= x and f[s] + 1 < f[x]:
                f[x] = f[s] + 1
    return f[T] if f[T] < INF else -1


def g_clips(r):
    T = r.randint(1, 10)
    return [_closed(r, r.randint(1, 7), 0, 12, 7), T]


def v_clips(tests):
    for t in tests:
        clips, T = t["args"]
        assert 1 <= len(clips) <= 3000 and 1 <= T <= 10 ** 9
        assert all(0 <= s < e <= 10 ** 9 for s, e in clips)
    res = [t["expected"] for t in tests]
    assert -1 in res and any(x > 1 for x in res)


CHECKS["min-clips-to-cover-time"] = (b_clips, g_clips, "exact")
VALIDATE["min-clips-to-cover-time"] = v_clips

# ------------------------------------------------------------------

p = add(
    id="fewest-intervals-covering-all-points", title="Fewest Intervals Covering All Points", diff="Medium", topic=TOPIC,
    fn="fewestIntervalsCovering", params=[("points", "int[]"), ("intervals", "int[][]")], ret="int", cmp="exact",
    desc="<p>You must pick some of the given closed intervals <code>[a, b]</code> so that every position in <code>points</code> lies inside at least one picked interval (a point on an end counts as inside). Return the smallest number of intervals you need, or <code>-1</code> if some point is not inside any interval at all.</p><pre>points = [1, 5, 9], intervals = [[0, 2], [1, 6], [4, 10], [8, 9]]  -&gt;  2</pre><p>Picking <code>[1, 6]</code> and <code>[4, 10]</code> covers all three points.</p>",
    constraints=["0 &le; points.length &le; 10,000", "1 &le; intervals.length &le; 10,000", "0 &le; points[i] &le; 10<sup>9</sup>", "intervals[i] = [a, b] with 0 &le; a &le; b &le; 10<sup>9</sup>", "Points may repeat"],
    hints=["Take the smallest point. Some picked interval must contain it. Which of the intervals containing it is the best choice?",
           "Among the intervals that contain the smallest uncovered point, the one with the largest right end covers the most points further to the right (everything to the left is already covered or is the point itself).",
           "Sort points and intervals. For each point not yet covered, look at all intervals starting at or before it, remember the largest end, check that the end reaches the point (else return -1), count one interval and skip all points up to that end."],
    editorial=["Process the points from left to right. When the current point <code>p</code> is not yet covered, some chosen interval must contain it. Intervals containing <code>p</code> have <code>a &le; p &le; b</code>. All points to the left of <code>p</code> are already covered, so only the right end matters, and the interval with the largest <code>b</code> is the best choice: whatever any other candidate covers to the right of <code>p</code>, this one covers too.",
               "Sort the intervals by start and keep a pointer that advances while <code>a &le; p</code>, maintaining the maximum end <code>best</code> seen so far. Because <code>p</code> only increases, a single pointer suffices and earlier intervals stay available. If <code>best &lt; p</code>, no interval contains <code>p</code>: return -1. Otherwise count one interval and skip every point &le; <code>best</code>. Total O((n + m) log(n + m)) for the sorts and linear scans after that."],
    time="O((n + m) log(n + m))", space="O(n + m)",
    solution='''def fewestIntervalsCovering(points, intervals):
    pts = sorted(points)
    ivs = sorted(intervals)
    m = len(ivs)
    j = 0
    best = -1
    covered_until = -1
    count = 0
    for x in pts:
        if x <= covered_until:
            continue
        while j < m and ivs[j][0] <= x:
            if ivs[j][1] > best:
                best = ivs[j][1]
            j += 1
        if best < x:
            return -1
        count += 1
        covered_until = best
    return count
''',
    tests=[[[1, 5, 9], [[0, 2], [1, 6], [4, 10], [8, 9]]], [[], [[1, 2]]], [[3], [[3, 3]]], [[3], [[4, 5], [0, 2]]], [[1, 2, 3], [[1, 1], [2, 2], [3, 3], [0, 4]]],
           [[1, 2, 3], [[1, 1], [2, 2], [3, 3]]], [[1, 1, 1], [[0, 1], [1, 5]]], [[0, 10, 20, 30], [[0, 5], [5, 12], [12, 22], [22, 30]]],
           [[5, 6, 7], [[0, 5], [7, 9]]], [[0, 1000000000], [[0, 1000000000]]], [[2, 4, 6, 8], [[1, 5], [3, 7], [5, 9], [0, 2]]]],
)
_r = rnd(5104)
_pts = [_r.randint(0, 1000000) for _ in range(1500)]
_iv = _closed(_r, 1500, 0, 1000000, 2400)
p["tests"].append([_pts, _iv])
_pts = [_r.randint(0, 10 ** 9) for _ in range(1200)]
_iv = _closed(_r, 1200, 0, 10 ** 9, 25000000)
p["tests"].append([_pts, _iv])
_pts = list(range(0, 2000, 2))
_iv = [[i, i + 3] for i in range(0, 2000, 2)]
p["tests"].append([_pts, _iv])


def b_fic(points, intervals):
    n = len(intervals)
    best = None
    for mask in range(1 << n):
        k = bin(mask).count("1")
        if best is not None and k >= best:
            continue
        ch = [intervals[i] for i in range(n) if mask >> i & 1]
        if all(any(a <= x <= b for a, b in ch) for x in points):
            best = k
    return -1 if best is None else best


def g_fic(r):
    return [[r.randint(0, 12) for _ in range(r.randint(0, 7))],
            [sorted([r.randint(0, 12), r.randint(0, 12)]) for _ in range(r.randint(1, 8))]]


def v_fic(tests):
    for t in tests:
        pts, iv = t["args"]
        assert len(pts) <= 10000 and 1 <= len(iv) <= 10000
        assert all(0 <= x <= 10 ** 9 for x in pts)
        assert all(0 <= a <= b <= 10 ** 9 for a, b in iv)
    res = [t["expected"] for t in tests]
    assert -1 in res and any(x > 1 for x in res)


CHECKS["fewest-intervals-covering-all-points"] = (b_fic, g_fic, "exact")
VALIDATE["fewest-intervals-covering-all-points"] = v_fic

# ------------------------------------------------------------------

p = add(
    id="fewest-intervals-same-union", title="Fewest Intervals with the Same Union", diff="Medium", topic=TOPIC, tier="extra",
    fn="fewestSameUnion", params=[("intervals", "int[][]")], ret="int", cmp="exact",
    desc="<p>The <em>union</em> of a set of closed intervals <code>[a, b]</code> is the set of all real numbers that lie in at least one of them. You are given a list of intervals and want to throw away as many as possible without changing the union.</p><p>Return the minimum number of intervals you must keep so that their union is exactly the union of the whole list. Intervals that only touch, like <code>[1, 3]</code> and <code>[3, 5]</code>, join into one block <code>[1, 5]</code>.</p><pre>intervals = [[1, 4], [2, 3], [3, 7], [6, 9], [12, 15], [13, 14]]  -&gt;  4</pre><p>The union is <code>[1, 9]</code> together with <code>[12, 15]</code>. Keep <code>[1, 4]</code>, <code>[3, 7]</code>, <code>[6, 9]</code> and <code>[12, 15]</code>.</p>",
    constraints=["0 &le; intervals.length &le; 10,000", "intervals[i] = [a, b] with 0 &le; a &lt; b &le; 10<sup>9</sup>", "Intervals may repeat or contain each other"],
    hints=["Merging the intervals gives the blocks of the union. You need a cover for each block, and different blocks never help each other.",
           "Inside one block, think of covering it from left to right: at each step you need an interval that starts at or before the point already covered and reaches as far as possible.",
           "Sort by start. Keep <code>reach</code>. Scan all intervals with <code>a &le; reach</code> for the largest end; if that is larger than <code>reach</code>, keep one interval and move <code>reach</code> there. When no progress is possible, the block is finished and the next interval starts a new block."],
    editorial=["Blocks of the union are independent: an interval lies in exactly one block, and the chosen intervals of one block must cover that block alone. Within a block the problem is the classic minimum cover of a segment by intervals. Start with the leftmost point of the block; the chosen interval must start there, and the best one is the one with the maximum end. Then repeat with the covered part extended: pick, among the intervals with <code>a &le; reach</code>, the one with the largest <code>b</code>, as long as it extends the reach.",
               "In code: sort by start; outer loop starts a new block at the next unprocessed interval, with <code>reach = a</code>; inner loop consumes every interval with start &le; <code>reach</code> and takes the maximal end; if it exceeds <code>reach</code> count one more interval and continue, otherwise the block is complete. Every interval is consumed once, so after sorting the scan is linear: O(n log n) time, O(n) space."],
    time="O(n log n)", space="O(n)",
    solution='''def fewestSameUnion(intervals):
    ivs = sorted(intervals)
    n = len(ivs)
    i = 0
    count = 0
    while i < n:
        reach = ivs[i][0]
        while True:
            best = reach
            while i < n and ivs[i][0] <= reach:
                if ivs[i][1] > best:
                    best = ivs[i][1]
                i += 1
            if best == reach:
                break
            count += 1
            reach = best
    return count
''',
    tests=[[[[1, 4], [2, 3], [3, 7], [6, 9], [12, 15], [13, 14]]], [[]], [[[1, 2]]], [[[1, 3], [3, 5]]], [[[1, 3], [3, 5], [1, 5]]],
           [[[1, 3], [4, 6]]], [[[1, 10], [2, 3], [4, 5], [6, 7]]], [[[1, 3], [2, 4], [3, 5], [4, 6], [5, 7]]], [[[1, 3], [1, 3], [1, 3]]],
           [[[0, 1000000000], [1, 2], [999999999, 1000000000]]], [[[5, 8], [1, 6], [7, 9], [20, 21], [0, 2]]]],
)
_r = rnd(5105)
p["tests"].append([_closed(_r, 2000, 0, 300000, 300)])
p["tests"].append([_closed(_r, 1800, 0, 10 ** 9, 8000000)])
p["tests"].append([[[i * 2, i * 2 + 3] for i in range(2000)]])


def _sets(ivs):
    s = set()
    for a, b in ivs:
        s.update(range(a, b))
    return s


def b_same_union(intervals):
    n = len(intervals)
    target = _sets(intervals)
    for k in range(n + 1):
        for ch in combinations(intervals, k):
            if _sets(ch) == target:
                return k


def g_same_union(r):
    return [_closed(r, r.randint(0, 8), 0, 12, 6)]


def v_same_union(tests):
    for t in tests:
        iv = t["args"][0]
        assert len(iv) <= 10000 and all(0 <= a < b <= 10 ** 9 for a, b in iv)


CHECKS["fewest-intervals-same-union"] = (b_same_union, g_same_union, "exact")
VALIDATE["fewest-intervals-same-union"] = v_same_union

# ------------------------------------------------------------------

p = add(
    id="radio-towers-on-houses", title="Radio Towers on Houses", diff="Medium", topic=TOPIC,
    fn="minTowers", params=[("houses", "int[]"), ("r", "int")], ret="int", cmp="exact",
    desc="<p>Houses stand along a straight road at the positions listed in <code>houses</code> (several houses can share a position). A radio tower must be built <em>on top of a house</em> and reaches every house whose distance from the tower is at most <code>r</code>, in both directions. A house with a tower on it is, of course, covered.</p><p>Return the minimum number of towers needed so that every house is within reach of at least one tower.</p><pre>houses = [7, 2, 4, 6, 5, 9, 12, 11], r = 2  -&gt;  3</pre><p>Towers at 4 (covers 2 to 6), at 9 (covers 7 to 11) and at 12 give full coverage.</p>",
    constraints=["1 &le; houses.length &le; 10,000", "0 &le; houses[i] &le; 10<sup>9</sup>", "0 &le; r &le; 10<sup>9</sup>"],
    hints=["Look at the leftmost house that is not covered yet. It must be covered by a tower somewhere in the window <code>[x - r, x + r]</code>.",
           "Towers must stand on houses. Among the houses at positions up to <code>x + r</code>, which tower position reaches furthest to the right while still covering <code>x</code>?",
           "Choose the rightmost house that is at most <code>x + r</code> (it covers <code>x</code> because the distance is at most r). Then skip all houses up to <code>tower + r</code> and repeat. Sort first and use a binary search or two pointers."],
    editorial=["Sort the positions. Let <code>x</code> be the leftmost uncovered house. A tower that covers it sits on a house at position <code>t</code> with <code>x - r &le; t &le; x + r</code>, and since everything left of <code>x</code> is covered, the best tower is the one reaching furthest to the right, which means the largest <code>t</code> that is still a house position and at most <code>x + r</code>. That rightmost-feasible choice dominates all others by the usual exchange argument.",
               "After placing the tower at <code>t</code>, every house up to <code>t + r</code> is covered, so jump to the first house beyond it. With a sorted array and a pointer this is linear after sorting: first move the pointer forward while <code>houses[j] &le; x + r</code> to find the tower, then forward again while <code>houses[j] &le; t + r</code>. Total O(n log n) time and O(n) space."],
    time="O(n log n)", space="O(n)",
    solution='''def minTowers(houses, r):
    pos = sorted(houses)
    n = len(pos)
    i = 0
    towers = 0
    while i < n:
        x = pos[i]
        j = i
        while j + 1 < n and pos[j + 1] <= x + r:
            j += 1
        t = pos[j]
        towers += 1
        i = j + 1
        while i < n and pos[i] <= t + r:
            i += 1
    return towers
''',
    tests=[[[7, 2, 4, 6, 5, 9, 12, 11], 2], [[5], 0], [[5, 5, 5], 0], [[1, 2, 3, 4, 5], 0], [[1, 2, 3, 4, 5], 1], [[1, 2, 3, 4, 5], 2],
           [[1, 100], 98], [[1, 100], 99], [[0, 1000000000], 1000000000], [[1, 2, 4, 5, 8, 9, 10], 1], [[10, 1, 5, 12, 3, 7], 3]],
)
_r = rnd(5106)
p["tests"].append([[_r.randint(0, 1000000) for _ in range(4000)], 250])
p["tests"].append([[_r.randint(0, 10 ** 9) for _ in range(3000)], 3000000])
p["tests"].append([[i * 2 for i in range(3000, 0, -1)], 5])


def b_towers(houses, r):
    u = sorted(set(houses))
    n = len(u)
    for k in range(1, n + 1):
        for ch in combinations(u, k):
            if all(any(abs(h - t) <= r for t in ch) for h in u):
                return k


def g_towers(r):
    return [[r.randint(0, 20) for _ in range(r.randint(1, 9))], r.randint(0, 6)]


def v_towers(tests):
    for t in tests:
        h, rr = t["args"]
        assert 1 <= len(h) <= 10000 and all(0 <= x <= 10 ** 9 for x in h) and 0 <= rr <= 10 ** 9


CHECKS["radio-towers-on-houses"] = (b_towers, g_towers, "exact")
VALIDATE["radio-towers-on-houses"] = v_towers

# ------------------------------------------------------------------

p = add(
    id="min-segment-length-to-cover-points", title="Shortest Segments to Cover All Points", diff="Medium", topic=TOPIC,
    fn="minSegmentLength", params=[("points", "int[]"), ("k", "int")], ret="int", cmp="exact",
    desc="<p>You have exactly <code>k</code> identical painted strips, and every strip has the same length <code>L</code>. A strip placed with its left end at position <code>x</code> covers all positions from <code>x</code> to <code>x + L</code>, inclusive; strips may overlap and may be placed anywhere. All the positions listed in <code>points</code> must be covered by at least one strip.</p><p>Return the smallest non-negative integer <code>L</code> for which this is possible. (You are allowed to leave strips unused.)</p><pre>points = [1, 2, 3, 10, 11, 20], k = 2  -&gt;  9</pre><p>With <code>L = 9</code>, one strip covers 1 to 10 and the other covers 11 to 20. A shorter length would need a strip covering two far apart groups.</p>",
    constraints=["0 &le; points.length &le; 5,000", "0 &le; points[i] &le; 10<sup>9</sup>", "1 &le; k &le; 5,000", "Points may repeat"],
    hints=["If someone told you the length L, how would you count the strips needed? (Think of the leftmost uncovered point.)",
           "Making L larger never needs more strips. So the answer has a monotone yes/no structure that you can search.",
           "Binary search L between 0 and <code>max(points) - min(points)</code>. For each candidate L run the greedy: open a strip at the first uncovered point, skip everything within L, count strips, compare with k."],
    editorial=["For a fixed L the minimum number of strips is found greedily: sort the points, put a strip's left end at the first uncovered point and skip all points within <code>L</code> of it. The count is non-increasing in L, so the predicate \"L strips suffice with at most k strips\" is monotone and we can binary search the smallest L that makes it true.",
               "The upper bound <code>max - min</code> always works with one strip, and 0 works only when there are at most k distinct positions. The search needs about 30 iterations (coordinates up to 10<sup>9</sup>), each a linear scan of the sorted points: O(n log n + n log C) time where C is the coordinate range, O(n) space. An empty list needs no strips, so the answer is 0."],
    time="O(n log n + n log C)", space="O(n)",
    solution='''def minSegmentLength(points, k):
    pts = sorted(points)
    if not pts:
        return 0

    def strips(length):
        count = 0
        end = None
        for x in pts:
            if end is None or x > end:
                count += 1
                end = x + length
        return count

    lo, hi = 0, pts[-1] - pts[0]
    while lo < hi:
        mid = (lo + hi) // 2
        if strips(mid) <= k:
            hi = mid
        else:
            lo = mid + 1
    return lo
''',
    tests=[[[1, 2, 3, 10, 11, 20], 2], [[], 3], [[5], 1], [[5, 5, 5], 1], [[1, 2, 3, 4, 5], 5], [[1, 2, 3, 4, 5], 1], [[1, 2, 3, 4, 5], 2],
           [[1, 2, 3, 4, 5], 3], [[0, 1000000000], 1], [[0, 1000000000], 2], [[1, 100, 101, 200, 201, 300], 3], [[9, 1, 5, 3, 7], 2]],
)
_r = rnd(5108)
p["tests"].append([[_r.randint(0, 1000000) for _ in range(4000)], 7])
p["tests"].append([[_r.randint(0, 10 ** 9) for _ in range(3000)], 300])
p["tests"].append([[i * i % 1000003 for i in range(3500)], 50])


def b_seglen(points, k):
    if not points:
        return 0
    for L in range(0, max(points) - min(points) + 1):
        if b_planks(points, L) <= k:
            return L


def g_seglen(r):
    return [[r.randint(0, 30) for _ in range(r.randint(0, 9))], r.randint(1, 4)]


def v_seglen(tests):
    for t in tests:
        pts, k = t["args"]
        assert len(pts) <= 5000 and 1 <= k <= 5000 and all(0 <= x <= 10 ** 9 for x in pts)


CHECKS["min-segment-length-to-cover-points"] = (b_seglen, g_seglen, "exact")
VALIDATE["min-segment-length-to-cover-points"] = v_seglen

# ---------------------------------------------------------------- HARD

p = add(
    id="min-taps-to-water-garden", title="Fewest Taps to Water the Garden", diff="Medium", topic=TOPIC, tier="extra",
    fn="minTaps", params=[("n", "int"), ("ranges", "int[]")], ret="int", cmp="exact",
    desc="<p>A garden is the straight line from position <code>0</code> to position <code>n</code>. There is a tap at every integer position <code>0, 1, ..., n</code>. Tap <code>i</code> can be opened so that it waters the whole stretch from <code>i - ranges[i]</code> to <code>i + ranges[i]</code>, inclusive (a range of 0 waters just one point). The stretch may extend beyond the garden.</p><p>Return the minimum number of taps that must be opened to water every point of <code>[0, n]</code>, or <code>-1</code> if it cannot be done.</p><pre>n = 7, ranges = [1, 2, 1, 0, 2, 1, 0, 1]  -&gt;  3</pre><p>Taps 1 (waters -1 to 3), 4 (2 to 6) and 7 (6 to 8) cover everything. <code>ranges</code> has <code>n + 1</code> entries.</p>",
    constraints=["1 &le; n &le; 10,000", "ranges.length = n + 1", "0 &le; ranges[i] &le; 100"],
    hints=["Every tap covers an interval <code>[i - ranges[i], i + ranges[i]]</code>. The task is now a minimum cover of <code>[0, n]</code> by intervals.",
           "Process positions from left to right and remember, for every left end, the furthest right end of any interval starting there (clip left ends below 0 to 0).",
           "Jump-game style: keep the current reach and the furthest reach seen so far. When you pass the current reach, open one more tap (jump to the furthest seen); if the furthest is not beyond the current reach you are stuck, return -1."],
    editorial=["Convert each tap to the interval <code>[max(0, i - r), min(n, i + r)]</code> and store <code>far[left] = max(far[left], right)</code>. The problem is exactly the minimum number of jumps in a jump game: from any position <code>x</code> you may use an interval starting at or before <code>x</code> to get to its right end, and the interval with the largest right end among those starting at or before the covered prefix is the best choice.",
               "Scan <code>x</code> from 0 to <code>n - 1</code>, keeping <code>cur_end</code> (reach of the taps already opened), <code>furthest</code> (best reach among all intervals starting at or before <code>x</code>) and a counter. At <code>x == cur_end</code> you must open a tap: if <code>furthest &le; cur_end</code> there is a gap, return -1; otherwise count it and set <code>cur_end = furthest</code>. Linear time and O(n) space; the greedy is correct for the same exchange reason as the interval-cover problem."],
    time="O(n)", space="O(n)",
    solution='''def minTaps(n, ranges):
    far = list(range(n + 1))  # far[x] = furthest right end of a stretch starting at x (or before)
    for i, r in enumerate(ranges):
        left = max(0, i - r)
        right = min(n, i + r)
        if right > far[left]:
            far[left] = right
    taps = 0
    cur_end = 0
    furthest = 0
    for x in range(n):
        if far[x] > furthest:
            furthest = far[x]
        if x == cur_end:
            if furthest <= cur_end:
                return -1
            taps += 1
            cur_end = furthest
            if cur_end >= n:
                break
    return taps
''',
    tests=[[7, [1, 2, 1, 0, 2, 1, 0, 1]], [3, [0, 0, 0, 0]], [5, [3, 4, 1, 1, 0, 0]], [1, [0, 1]], [1, [1, 0]], [1, [0, 0]], [4, [2, 0, 0, 0, 2]],
           [4, [2, 0, 0, 0, 1]], [6, [1, 1, 1, 1, 1, 1, 1]], [6, [0, 1, 1, 1, 1, 1, 0]], [5, [0, 0, 5, 0, 0, 0]], [8, [0, 3, 0, 0, 0, 0, 0, 3, 0]]],
)
_r = rnd(5109)
p["tests"].append([8000, [_r.randint(0, 12) for _ in range(8001)]])
p["tests"].append([9000, [_r.choice([1, 1, 2, 3, 5]) for _ in range(9001)]])
_a = [_r.randint(1, 3) for _ in range(6001)]
for _i in range(2990, 3010):
    _a[_i] = 0
for _i in range(2975, 2990):  # a gap that no tap near it can bridge
    _a[_i] = min(_a[_i], 1)
p["tests"].append([6000, _a])


def b_taps(n, ranges):
    m = n + 1
    best = None
    for mask in range(1 << m):
        k = bin(mask).count("1")
        if best is not None and k >= best:
            continue
        ok = True
        for u in range(n):  # unit segment [u, u + 1]
            if not any(mask >> i & 1 and i - ranges[i] <= u and u + 1 <= i + ranges[i] for i in range(m)):
                ok = False
                break
        if ok:
            best = k
    return -1 if best is None else best


def g_taps(r):
    n = r.randint(1, 8)
    return [n, [r.randint(0, 3) for _ in range(n + 1)]]


def v_taps(tests):
    for t in tests:
        n, rg = t["args"]
        assert 1 <= n <= 10000 and len(rg) == n + 1 and all(0 <= x <= 100 for x in rg)
    res = [t["expected"] for t in tests]
    assert -1 in res and any(x > 1 for x in res)


CHECKS["min-taps-to-water-garden"] = (b_taps, g_taps, "exact")
VALIDATE["min-taps-to-water-garden"] = v_taps

# ------------------------------------------------------------------

p = add(
    id="min-points-hit-each-interval-twice", title="Hit Every Interval Twice", diff="Hard", topic=TOPIC, tier="extra",
    fn="minPointsTwice", params=[("intervals", "int[][]")], ret="int", cmp="exact",
    desc="<p>Each interval <code>[a, b]</code> is a closed range of integers, containing <code>a, a + 1, ..., b</code>. Choose a set <code>S</code> of integers such that every interval contains <strong>at least two</strong> elements of <code>S</code>. Return the smallest possible size of <code>S</code>.</p><pre>intervals = [[1, 4], [2, 3], [6, 9]]  -&gt;  4</pre><p>For example <code>S = {2, 3, 8, 9}</code>: the first two intervals both contain 2 and 3, and the last contains 8 and 9. Three points are impossible, since <code>[2, 3]</code> and <code>[6, 9]</code> share no integer.</p>",
    constraints=["1 &le; intervals.length &le; 3,000", "intervals[i] = [a, b] with 0 &le; a &lt; b &le; 10<sup>8</sup>"],
    hints=["With one point per interval this is the minimum-arrows problem: sort by right end and place a point at the right end of the first unhit interval. What changes if two points are needed?",
           "Sort by right end ascending (ties: left end descending). Remember the last two chosen points and check how many of them lie in the next interval.",
           "If the interval contains neither of the two last points, add its two rightmost integers (<code>b - 1</code> and <code>b</code>). If it contains only the larger one, add <code>b</code>. If it contains both, do nothing."],
    editorial=["Sort by right end, ties by left end descending, and process in that order, always choosing points as far to the right as possible: for the first interval that is <code>b - 1</code> and <code>b</code>. A point placed at the right end of the interval being processed is the most useful one, since all later intervals have a right end at least as large and a right-most point has the greatest chance of lying in them (intervals that come later and start at or before the point contain it). This is the arrows argument applied twice.",
               "Keep the two largest chosen points <code>lo &lt; hi</code>. For a new interval <code>[a, b]</code>: if <code>a &gt; hi</code> neither point is inside, so add <code>b - 1</code> and <code>b</code> (cost 2). Else if <code>a &gt; lo</code>, only <code>hi</code> is inside, so add <code>b</code> (cost 1; the tie-break on the left end guarantees <code>b &gt; hi</code> here). Otherwise both chosen points lie inside and nothing is added. Sorting dominates: O(n log n), O(1) extra space."],
    time="O(n log n)", space="O(1)",
    solution='''def minPointsTwice(intervals):
    ordered = sorted(intervals, key=lambda iv: (iv[1], -iv[0]))
    lo = hi = -10
    count = 0
    for a, b in ordered:
        if a > hi:
            lo, hi = b - 1, b
            count += 2
        elif a > lo:
            lo, hi = hi, b
            count += 1
    return count
''',
    tests=[[[[1, 4], [2, 3], [6, 9]]], [[[1, 2]]], [[[1, 3], [3, 7], [5, 7], [7, 8]]], [[[1, 2], [1, 2], [1, 2]]], [[[1, 2], [2, 3], [3, 4]]],
           [[[1, 10], [2, 9], [3, 8], [4, 7]]], [[[0, 1], [0, 5], [4, 5]]], [[[1, 3], [2, 4], [3, 5], [4, 6]]],
           [[[0, 100000000], [99999999, 100000000]]], [[[1, 5], [1, 2], [4, 5]]], [[[2, 6], [1, 3], [5, 8], [7, 9]]]],
)
_r = rnd(5110)
p["tests"].append([_closed(_r, 2500, 0, 100000, 60)])
p["tests"].append([_closed(_r, 2500, 0, 10 ** 8, 4000000)])
p["tests"].append([[[i, i + 1 + (i * 7 % 5)] for i in range(2800)]])


def b_twice(intervals):
    lo = min(a for a, _ in intervals)
    hi = max(b for _, b in intervals)
    pts = list(range(lo, hi + 1))
    for k in range(2, len(pts) + 1):
        for ch in combinations(pts, k):
            if all(sum(1 for x in ch if a <= x <= b) >= 2 for a, b in intervals):
                return k


def g_twice(r):
    return [_closed(r, r.randint(1, 5), 0, 8, 5)]


def v_twice(tests):
    for t in tests:
        iv = t["args"][0]
        assert 1 <= len(iv) <= 3000 and all(0 <= a < b <= 10 ** 8 for a, b in iv)


CHECKS["min-points-hit-each-interval-twice"] = (b_twice, g_twice, "exact")
VALIDATE["min-points-hit-each-interval-twice"] = v_twice

# ------------------------------------------------------------------

p = add(
    id="min-intervals-to-cover-each-query", title="Cover Each Query Range", diff="Hard", topic=TOPIC, tier="extra",
    fn="coverQueries", params=[("intervals", "int[][]"), ("queries", "int[][]")], ret="int[]", cmp="exact",
    desc="<p>You are given closed intervals <code>[a, b]</code> and a list of queries <code>[l, r]</code> with <code>l &le; r</code>. For each query, find the smallest number of the given intervals whose union contains every real number from <code>l</code> to <code>r</code>, or <code>-1</code> if no choice of intervals does that. Intervals that only touch leave no gap. Queries are independent. Return the answers in query order.</p><pre>intervals = [[0, 4], [3, 8], [7, 10], [10, 15]]\nqueries   = [[1, 9], [0, 10], [2, 3], [11, 14], [5, 12], [0, 15], [16, 17]]\nresult    = [3, 3, 1, 1, 3, 4, -1]</pre>",
    constraints=["1 &le; intervals.length &le; 3,000", "1 &le; queries.length &le; 3,000", "intervals[i] = [a, b] with 0 &le; a &lt; b &le; 10<sup>9</sup>", "queries[j] = [l, r] with 0 &le; l &le; r &le; 10<sup>9</sup>"],
    hints=["For a single query the greedy cover works: jump to the largest end among intervals starting at or before the current reach. Doing this from scratch for every query is too slow when answers are large (O(n) jumps each).",
           "The jump from a position does not depend on the query. Precompute <code>next[i]</code>: the state reached after one more greedy jump from state <code>i</code>.",
           "Use binary lifting: store <code>up[j][i]</code>, the state after 2<sup>j</sup> jumps. For a query, take jumps of decreasing power of two as long as the reach stays below <code>r</code>, then one final jump decides the answer or -1."],
    editorial=["Sort the intervals by start and let <code>best[i]</code> be the largest end among the first <code>i + 1</code> of them. State <code>i</code> means: \"everything up to <code>best[i]</code> is covered by the greedy chain\". One more greedy jump leads to state <code>nxt[i] = bisect_right(starts, best[i]) - 1</code>, i.e. the last interval whose start is at most the current reach, which is the correct next greedy choice. If <code>nxt[i] == i</code> the chain is stuck.",
               "For a query <code>[l, r]</code>: the first state is <code>s = bisect_right(starts, l) - 1</code> (no such interval, or <code>best[s] &lt; l</code>, means -1) and one interval is used. If <code>best[s] &ge; r</code> the answer is 1. Otherwise lift: for <code>j</code> from high to low, if the state <code>up[j][s]</code> still has <code>best &lt; r</code>, move there and add 2<sup>j</sup> intervals. A final jump to <code>up[0][s]</code> must reach <code>r</code> (answer = count + 1), otherwise the chain is stuck and the answer is -1. Preprocessing O(n log n), every query O(log n); memory O(n log n)."],
    time="O((n + q) log n)", space="O(n log n)",
    solution='''from bisect import bisect_right


def coverQueries(intervals, queries):
    ivs = sorted(intervals)
    n = len(ivs)
    starts = [a for a, _ in ivs]
    best = []
    cur = -1
    for _, b in ivs:
        if b > cur:
            cur = b
        best.append(cur)
    nxt = [bisect_right(starts, best[i]) - 1 for i in range(n)]
    LOG = max(1, n.bit_length())
    up = [nxt]
    for j in range(1, LOG):
        prev = up[-1]
        up.append([prev[prev[i]] for i in range(n)])
    out = []
    for l, r in queries:
        s = bisect_right(starts, l) - 1
        if s < 0 or best[s] < l:
            out.append(-1)
            continue
        cnt = 1
        if best[s] >= r:
            out.append(1)
            continue
        for j in range(LOG - 1, -1, -1):
            t = up[j][s]
            if best[t] < r:
                s = t
                cnt += 1 << j
        t = up[0][s]
        out.append(cnt + 1 if best[t] >= r else -1)
    return out
''',
    tests=[[[[0, 4], [3, 8], [7, 10], [10, 15]], [[1, 9], [0, 10], [2, 3], [11, 14], [5, 12], [0, 15], [16, 17]]],
           [[[1, 2]], [[1, 2], [0, 1], [1, 1], [2, 2], [2, 3]]],
           [[[0, 5], [6, 10]], [[0, 10], [0, 5], [6, 10], [5, 6], [3, 4]]],
           [[[0, 3], [3, 6], [6, 9], [9, 12]], [[0, 12], [1, 11], [3, 3], [3, 6], [2, 7], [0, 13]]],
           [[[0, 1000000000], [5, 6]], [[0, 1000000000], [5, 5], [7, 8]]],
           [[[2, 5], [0, 3], [4, 8], [1, 2], [8, 8 + 1]], [[0, 9], [0, 8], [1, 1], [2, 7], [9, 9], [0, 0]]],
           [[[0, 2], [1, 3], [2, 4], [3, 5], [4, 6], [5, 7]], [[0, 7], [0, 6], [1, 5], [2, 4], [0, 2], [6, 7]]],
           [[[0, 10], [10, 20], [20, 30]], [[5, 25], [10, 20], [0, 30], [31, 32]]],
           [[[0, 1], [2, 3]], [[0, 3], [0, 1], [2, 3], [1, 2]]],
           [[[0, 5], [1, 2], [3, 4]], [[0, 5], [1, 4], [0, 6]]]],
)
_r = rnd(5111)


def _qs(r, n, hi, maxlen):
    out = []
    for _ in range(n):
        l = r.randint(0, hi)
        out.append([l, min(10 ** 9, l + r.randint(0, maxlen))])
    return out


p["tests"].append([_closed(_r, 1200, 0, 100000, 400), _qs(_r, 1200, 100000, 20000)])
p["tests"].append([[[i * 3, i * 3 + 4] for i in range(1000)], _qs(_r, 1000, 3000, 3000)])
p["tests"].append([_closed(_r, 1000, 0, 10 ** 9, 45000000), _qs(_r, 1000, 10 ** 9, 400000000)])


def b_cover_q(intervals, queries):
    n = len(intervals)
    res = []
    for l, r in queries:
        best = None
        for mask in range(1 << n):
            k = bin(mask).count("1")
            if best is not None and k >= best:
                continue
            ch = [intervals[i] for i in range(n) if mask >> i & 1]
            if l == r:
                ok = any(a <= l <= b for a, b in ch)
            else:
                ok = all(any(a <= u and u + 1 <= b for a, b in ch) for u in range(l, r))
            if ok:
                best = k
        res.append(-1 if best is None else best)
    return res


def g_cover_q(r):
    iv = _closed(r, r.randint(1, 8), 0, 10, 6)
    qs = []
    for _ in range(r.randint(1, 5)):
        l = r.randint(0, 10)
        qs.append([l, min(12, l + r.randint(0, 8))])
    return [iv, qs]


def v_cover_q(tests):
    allres = []
    for t in tests:
        iv, qs = t["args"]
        assert 1 <= len(iv) <= 3000 and 1 <= len(qs) <= 3000
        assert all(0 <= a < b <= 10 ** 9 for a, b in iv)
        assert all(0 <= l <= r <= 10 ** 9 for l, r in qs)
        allres.extend(t["expected"])
    assert -1 in allres and max(allres) >= 4


CHECKS["min-intervals-to-cover-each-query"] = (b_cover_q, g_cover_q, "exact")
VALIDATE["min-intervals-to-cover-each-query"] = v_cover_q

# ------------------------------------------------------------------

p = add(
    id="fewest-arcs-to-cover-ring", title="Fewest Arcs to Cover the Ring", diff="Hard", topic=TOPIC, tier="extra",
    fn="fewestArcs", params=[("n", "int"), ("arcs", "int[][]")], ret="int", cmp="exact",
    desc="<p>A circular track has <code>n</code> cells numbered <code>0</code> to <code>n - 1</code> clockwise; after cell <code>n - 1</code> comes cell <code>0</code> again. An arc <code>[start, length]</code> covers <code>length</code> consecutive cells clockwise, beginning with cell <code>start</code>: the cells <code>start, start + 1, ...</code> taken modulo <code>n</code>. An arc with <code>length = n</code> covers the whole track.</p><p>Return the minimum number of arcs from the list that together cover every cell of the track, or <code>-1</code> if that is impossible.</p><pre>n = 10, arcs = [[0, 4], [3, 4], [6, 5], [8, 3]]  -&gt;  3\nn = 6,  arcs = [[0, 2], [3, 2]]                  -&gt;  -1</pre><p>In the first example the arcs <code>[0, 4]</code> (cells 0-3), <code>[3, 4]</code> (cells 3-6) and <code>[6, 5]</code> (cells 6, 7, 8, 9, 0) cover all ten cells. In the second, cells 2 and 5 are never covered.</p>",
    constraints=["1 &le; n &le; 5,000", "1 &le; arcs.length &le; 5,000", "arcs[i] = [start, length] with 0 &le; start &lt; n and 1 &le; length &le; n"],
    hints=["On a straight line this is the classic greedy: from the covered prefix, jump to the farthest end among arcs starting at or before it. What breaks on a circle?",
           "The circle has no left end. But some arc of an optimal answer starts at some cell; if you know which one, unroll the circle there and the line greedy applies. Duplicate every arc one lap further (start + n) so wrapping arcs become ordinary.",
           "Precompute <code>g[x]</code> = the farthest end reachable with arcs starting at or before <code>x</code> on the doubled line. For every possible starting cell <code>s</code> count the jumps needed to get from <code>s</code> to <code>s + n</code>. Doing that naively costs too much, so use binary lifting on <code>g</code> and take the minimum over all starting cells."],
    editorial=["Take an optimal cover and look at one of its arcs, which starts at cell <code>s</code>. Cut the circle at <code>s</code> and unroll it to the line <code>s .. s + n</code>. Add a copy of each arc shifted by <code>n</code> so that arcs that wrap around the cut appear as ordinary intervals on the doubled line <code>0 .. 2n</code>. Now we need the fewest intervals that cover <code>[s, s + n)</code>, which the greedy jump solves: from covered boundary <code>x</code>, the next boundary is <code>g[x]</code>, the largest end among intervals with start &le; <code>x</code>. We only need to try cuts at starting cells of arcs, as at least one arc of any minimal cover starts there.",
               "Running the jump greedy separately from each of up to n starting cells could take O(n) jumps each. Because <code>g</code> is a fixed function, precompute <code>up[j][x]</code>, the boundary after 2<sup>j</sup> jumps, and for each start <code>s</code> take the largest jumps that stay below <code>s + n</code>, then one more jump; if it does not reach <code>s + n</code> the chain is stuck. The minimum over all starts is the answer, or -1. Time O((n + m) log n) with m arcs, space O(n log n). Every chain of k jumps is a cover by at most k distinct arcs, so no start gives an impossible result, and the best start gives the optimum."],
    time="O((n + m) log n)", space="O(n log n)",
    solution='''def fewestArcs(n, arcs):
    m = 2 * n
    ends = [0] * (m + 1)
    starts = set()
    for s, length in arcs:
        starts.add(s)
        if s + length > ends[s]:
            ends[s] = s + length
        if s + n + length > ends[s + n]:
            ends[s + n] = s + n + length
    g = [0] * (m + 1)
    run = 0
    for x in range(m + 1):
        if ends[x] > run:
            run = ends[x]
        g[x] = min(m, max(x, run))
    LOG = max(1, n.bit_length() + 1)
    up = [g]
    for _ in range(1, LOG):
        prev = up[-1]
        up.append([prev[prev[x]] for x in range(m + 1)])
    INF = 10 ** 9
    best = INF
    for s in starts:
        target = s + n
        x = s
        cnt = 0
        for j in range(LOG - 1, -1, -1):
            y = up[j][x]
            if y < target:
                x = y
                cnt += 1 << j
        if g[x] >= target:
            best = min(best, cnt + 1)
    return -1 if best == INF else best
''',
    tests=[[10, [[0, 4], [3, 4], [6, 5], [8, 3]]], [6, [[0, 2], [3, 2]]], [1, [[0, 1]]], [5, [[2, 5]]], [5, [[3, 3], [0, 3]]], [5, [[3, 3], [0, 2]]],
           [8, [[6, 4], [2, 4]]], [8, [[6, 3], [2, 4]]], [7, [[5, 3], [1, 3], [3, 3], [0, 2]]], [9, [[0, 3], [3, 3], [6, 3], [4, 5], [7, 4]]],
           [12, [[0, 5], [4, 5], [8, 5], [10, 4], [2, 3]]], [4, [[0, 1], [1, 1], [2, 1], [3, 1]]]],
)
_r = rnd(5112)


def _arcs(r, n, m, maxlen):
    return [[r.randrange(n), r.randint(1, maxlen)] for _ in range(m)]


p["tests"].append([2000, _arcs(_r, 2000, 1500, 40)])
p["tests"].append([3000, _arcs(_r, 3000, 600, 15)])
p["tests"].append([4000, [[(i * 7) % 4000, 12] for i in range(1400)] + [[3990, 30], [100, 5]]])


def b_ring(n, arcs):
    m = len(arcs)
    cov = [sum(1 << ((s + i) % n) for i in range(length)) for s, length in arcs]
    full = (1 << n) - 1
    best = None
    for mask in range(1 << m):
        k = bin(mask).count("1")
        if best is not None and k >= best:
            continue
        c = 0
        for i in range(m):
            if mask >> i & 1:
                c |= cov[i]
        if c == full:
            best = k
    return -1 if best is None else best


def g_ring(r):
    n = r.randint(1, 9)
    return [n, [[r.randrange(n), r.randint(1, n)] for _ in range(r.randint(1, 8))]]


def v_ring(tests):
    for t in tests:
        n, arcs = t["args"]
        assert 1 <= n <= 5000 and 1 <= len(arcs) <= 5000
        assert all(0 <= s < n and 1 <= ln <= n for s, ln in arcs)
    res = [t["expected"] for t in tests]
    assert -1 in res and max(res) >= 5


CHECKS["fewest-arcs-to-cover-ring"] = (b_ring, g_ring, "exact")
VALIDATE["fewest-arcs-to-cover-ring"] = v_ring
