"""Problems: intervals, scheduling (meetings, rooms, free time). See data/lib.py for the registry."""
from itertools import combinations

from lib import add, rnd, CHECKS, VALIDATE, gen_arr  # noqa: F401

TOPIC = "Intervals"


def _ivs(r, n, lo, hi, maxlen):
    """n random half-open intervals [s, e) with lo <= s < e <= hi."""
    out = []
    for _ in range(n):
        s = r.randint(lo, hi - 1)
        out.append([s, min(hi, s + r.randint(1, maxlen))])
    return out


def _sched(r, T, n, maxgap, maxlen):
    """Up to n sorted, non-overlapping meetings inside [0, T] (touching allowed) as (starts, ends)."""
    st, en = [], []
    pos = 0
    for _ in range(n):
        s = pos + r.randint(0, maxgap)
        e = s + r.randint(1, maxlen)
        if e > T:
            break
        st.append(s)
        en.append(e)
        pos = e
    return st, en


def _sorted_disjoint(st, en, T):
    assert len(st) == len(en)
    prev = 0
    for s, e in zip(st, en):
        assert prev <= s < e <= T, "meetings must be sorted, disjoint and inside the day"
        prev = e


# ---------------------------------------------------------------- EASY

p = add(
    id="can-attend-all-meetings", title="Can Attend All Meetings", diff="Easy", topic=TOPIC, tier="must",
    fn="canAttendAll", params=[("meetings", "int[][]")], ret="bool", cmp="exact",
    desc="<p>Each meeting is a half-open time range <code>[start, end)</code>: it occupies every moment <code>t</code> with <code>start &le; t &lt; end</code>. A meeting that ends at time 10 and one that starts at time 10 do <em>not</em> clash.</p><p>You are a single person and cannot be in two meetings at the same moment. Given all the meetings (in no particular order), return <code>true</code> if you can attend every one of them, and <code>false</code> otherwise.</p><pre>meetings = [[0, 30], [5, 10], [15, 20]]  -&gt;  false\nmeetings = [[7, 10], [2, 4]]            -&gt;  true</pre>",
    constraints=["0 &le; meetings.length &le; 5,000", "meetings[i] = [start, end] with 0 &le; start &lt; end &le; 10<sup>9</sup>"],
    hints=["Two meetings clash exactly when each one starts before the other one ends. Comparing every pair works, but it is O(n<sup>2</sup>).",
           "If the meetings were listed by start time, which pairs would you actually have to look at?",
           "Sort by start time. Then a clash exists if and only if some meeting starts before the previous meeting in sorted order has ended."],
    editorial=["Sort the meetings by start time. Suppose two meetings clash, and let them be at positions <code>i &lt; j</code> in sorted order. Then <code>start[j] &lt; end[i]</code>. The meeting right after <code>i</code> has a start no later than <code>start[j]</code>, so it also starts before <code>end[i]</code>; hence it is enough to compare each meeting with its neighbour.",
               "Scan the sorted list and return <code>false</code> as soon as <code>start[i] &lt; end[i-1]</code>. Using a strict comparison makes back-to-back meetings legal. Sorting dominates: O(n log n) time, and O(n) space for the sorted copy."],
    time="O(n log n)", space="O(n)",
    solution='''def canAttendAll(meetings):
    ordered = sorted(meetings)
    for i in range(1, len(ordered)):
        if ordered[i][0] < ordered[i - 1][1]:
            return False
    return True
''',
    tests=[[[[0, 30], [5, 10], [15, 20]]], [[[7, 10], [2, 4]]], [[]], [[[1, 2]]], [[[1, 2], [2, 3], [3, 4]]], [[[1, 5], [1, 5]]],
           [[[1, 10], [2, 3]]], [[[5, 6], [1, 2], [3, 4], [2, 3]]], [[[0, 1000000000], [1000000000 - 1, 1000000000]]],
           [[[0, 3], [4, 9], [3, 4], [9, 10], [20, 30], [10, 20]]], [[[1, 4], [5, 8], [2, 3]]]],
)
_r = rnd(4101)
_pts = sorted(_r.sample(range(0, 200001), 3001))
_ok = [[_pts[2 * i], _pts[2 * i + 1]] for i in range(1500)]
_r.shuffle(_ok)
p["tests"].append([_ok])
_bad = [list(x) for x in _ok]
_k = max(range(len(_bad)), key=lambda i: _bad[i][1] - _bad[i][0])
_bad.append([_bad[_k][0] + 1, _bad[_k][1] + 1 if _bad[_k][1] + 1 <= 10 ** 9 else _bad[_k][1]])
p["tests"].append([_bad])
_pts = sorted(_r.sample(range(0, 10 ** 9 + 1), 1200))
_ok = [[_pts[2 * i], _pts[2 * i + 1]] for i in range(600)]
_r.shuffle(_ok)
p["tests"].append([_ok])
p["tests"].append([[[i, i + 1] for i in range(1499, -1, -1)]])
p["tests"].append([_ivs(_r, 1500, 0, 100000, 50)])


def b_attend(meetings):
    for a, b in combinations(meetings, 2):
        if a[0] < b[1] and b[0] < a[1]:
            return False
    return True


def g_attend(r):
    return [_ivs(r, r.randint(0, 6), 0, 14, 4)]


def v_attend(tests):
    for t in tests:
        m = t["args"][0]
        assert len(m) <= 5000
        for s, e in m:
            assert 0 <= s < e <= 10 ** 9
    res = [t["expected"] for t in tests]
    assert True in res and False in res


CHECKS["can-attend-all-meetings"] = (b_attend, g_attend, "exact")
VALIDATE["can-attend-all-meetings"] = v_attend

# ------------------------------------------------------------------

p = add(
    id="count-conflicting-meetings", title="Count Conflicting Meetings", diff="Easy", topic=TOPIC,
    fn="countConflicting", params=[("meetings", "int[][]")], ret="int", cmp="exact",
    desc="<p>Each meeting is a half-open time range <code>[start, end)</code>, so a meeting ending at time 10 does not clash with one starting at time 10. Two meetings <em>clash</em> when they share at least one moment.</p><p>A meeting is <em>in conflict</em> if it clashes with at least one other meeting in the list (two identical meetings clash with each other). Return how many meetings are in conflict.</p><pre>meetings = [[1, 5], [2, 3], [6, 8], [8, 9], [10, 12]]  -&gt;  2</pre><p>Only <code>[1, 5]</code> and <code>[2, 3]</code> clash with anything.</p>",
    constraints=["0 &le; meetings.length &le; 5,000", "meetings[i] = [start, end] with 0 &le; start &lt; end &le; 10<sup>9</sup>", "The meetings are in no particular order"],
    hints=["Checking every pair of meetings is a valid start, but there is a faster way after sorting.",
           "Sort by start time. A meeting can clash with an earlier one, with a later one, or with both. How could you detect each of the two cases cheaply?",
           "Keep the largest end time seen so far: if the current start is smaller than it, the meeting clashes with an earlier one. If the next meeting starts before the current one ends, it clashes with a later one."],
    editorial=["After sorting by start time, meeting <code>i</code> clashes with some earlier meeting exactly when its start is smaller than the maximum end time among the earlier meetings. It clashes with some later meeting exactly when the very next meeting in sorted order starts before <code>end[i]</code>, because that next meeting has the smallest start among all later ones.",
               "So one pass with a running maximum end, plus a look at the neighbour, decides each meeting. Counting a meeting once even when it clashes in both directions is natural because you test the two conditions with <code>or</code>. Sorting makes it O(n log n) time with O(n) space."],
    time="O(n log n)", space="O(n)",
    solution='''def countConflicting(meetings):
    ordered = sorted(meetings)
    n = len(ordered)
    count = 0
    max_end = -1
    for i in range(n):
        s, e = ordered[i]
        if s < max_end or (i + 1 < n and ordered[i + 1][0] < e):
            count += 1
        max_end = max(max_end, e)
    return count
''',
    tests=[[[[1, 5], [2, 3], [6, 8], [8, 9], [10, 12]]], [[]], [[[1, 2]]], [[[1, 2], [2, 3], [3, 4]]], [[[1, 2], [1, 2]]],
           [[[1, 10], [2, 3], [4, 5], [6, 7], [11, 12]]], [[[5, 8], [1, 6], [7, 9], [20, 21]]], [[[1, 100], [10, 20], [30, 40], [50, 60], [100, 101]]],
           [[[0, 1000000000], [999999999, 1000000000], [0, 1]]], [[[3, 4], [1, 2], [2, 3]]], [[[1, 4], [4, 6], [3, 5]]]],
)
_r = rnd(4102)
p["tests"].append([_ivs(_r, 1500, 0, 1000000, 40)])
p["tests"].append([_ivs(_r, 1500, 0, 1500, 1)])
_pts = sorted(_r.sample(range(0, 10 ** 9), 1000))
_a = [[_pts[2 * i], _pts[2 * i + 1]] for i in range(500)]
_a += [[_a[7][0], _a[7][1] + 1], [_a[250][0] - 1, _a[250][0] + 1]]
_r.shuffle(_a)
p["tests"].append([_a])
p["tests"].append([[[i, i + 1] for i in range(1500)] + [[0, 10 ** 9]]])


def b_conflict(meetings):
    c = 0
    for i, a in enumerate(meetings):
        if any(j != i and a[0] < b[1] and b[0] < a[1] for j, b in enumerate(meetings)):
            c += 1
    return c


def g_conflict(r):
    return [_ivs(r, r.randint(0, 8), 0, 16, 4)]


def v_conflict(tests):
    for t in tests:
        m = t["args"][0]
        assert len(m) <= 5000
        for s, e in m:
            assert 0 <= s < e <= 10 ** 9


CHECKS["count-conflicting-meetings"] = (b_conflict, g_conflict, "exact")
VALIDATE["count-conflicting-meetings"] = v_conflict

# ------------------------------------------------------------------

p = add(
    id="earliest-open-calendar-slot", title="Earliest Open Calendar Slot", diff="Easy", topic=TOPIC,
    fn="earliestOpenSlot", params=[("meetings", "int[][]"), ("dayLength", "int"), ("duration", "int")], ret="int", cmp="exact",
    desc="<p>A workday runs from time <code>0</code> to time <code>dayLength</code>. The calendar holds a list of busy meetings, each a half-open range <code>[start, end)</code>. Meetings can be in any order and may overlap each other.</p><p>You want to book a new meeting that lasts exactly <code>duration</code> and fits completely inside the day, without sharing any moment with an existing meeting (touching is fine). Return the earliest possible start time, or <code>-1</code> if there is no such slot.</p><pre>meetings = [[0, 5], [4, 8], [10, 12]], dayLength = 20, duration = 2  -&gt;  8\nmeetings = [[0, 9], [9, 19]], dayLength = 20, duration = 2          -&gt;  -1</pre>",
    constraints=["0 &le; meetings.length &le; 5,000", "meetings[i] = [start, end] with 0 &le; start &lt; end &le; dayLength", "1 &le; duration &le; dayLength &le; 10<sup>9</sup>"],
    hints=["A new meeting must fit into a gap of the calendar, possibly the gap before the first meeting or after the last one.",
           "Sort the meetings by start time and keep a cursor: the end of everything handled so far.",
           "Before each meeting, check whether the gap from the cursor to the meeting's start is at least <code>duration</code>. Then move the cursor to <code>max(cursor, end)</code> because meetings may overlap or be nested. Do not forget the final gap up to <code>dayLength</code>."],
    editorial=["Scan the meetings in start order while maintaining <code>cursor</code>, the earliest moment that is free of all meetings seen so far (initially 0). If the next meeting starts at <code>s</code> and <code>s - cursor &ge; duration</code>, the slot starting at the cursor fits and is the earliest one, because everything before the cursor is occupied. Otherwise the meeting occupies time up to its end, so set <code>cursor = max(cursor, end)</code>; the maximum matters because a long meeting can contain shorter ones.",
               "After the last meeting, test the tail gap <code>dayLength - cursor &ge; duration</code>. Return <code>-1</code> if no gap was large enough. Sorting dominates, giving O(n log n) time and O(n) space."],
    time="O(n log n)", space="O(n)",
    solution='''def earliestOpenSlot(meetings, dayLength, duration):
    cursor = 0
    for s, e in sorted(meetings):
        if s - cursor >= duration:
            return cursor
        cursor = max(cursor, e)
    if dayLength - cursor >= duration:
        return cursor
    return -1
''',
    tests=[[[[0, 5], [4, 8], [10, 12]], 20, 2], [[[2, 5], [4, 8], [10, 12]], 20, 2], [[[0, 9], [9, 19]], 20, 2], [[], 10, 10], [[], 10, 9], [[[0, 10]], 10, 1],
           [[[3, 4]], 10, 3], [[[3, 4]], 10, 4], [[[0, 3], [5, 6], [8, 10]], 10, 2], [[[0, 3], [5, 6], [8, 10]], 10, 3],
           [[[0, 1000000000]], 1000000000, 1], [[[1, 5], [2, 3], [3, 4]], 100, 95], [[[1, 5], [2, 3], [3, 4]], 100, 96],
           [[[6, 7], [0, 2], [3, 4]], 8, 1]],
)
_r = rnd(4103)
_m = [[i * 200, i * 200 + 150 + _r.randint(0, 49)] for i in range(1000)]
_r.shuffle(_m)
p["tests"].append([_m, 250000, 50])
_m = [[i * 200, i * 200 + 199] for i in range(1000)]
_r.shuffle(_m)
p["tests"].append([_m, 200000, 2])
p["tests"].append([_ivs(_r, 1200, 0, 1000000, 300), 1000000, 400])


def b_slot(meetings, dayLength, duration):
    for s in range(0, dayLength - duration + 1):
        if all(not (s < e and m < s + duration) for m, e in meetings):
            return s
    return -1


def g_slot(r):
    T = r.randint(1, 22)
    d = r.randint(1, min(T, 5))
    return [_ivs(r, r.randint(0, 5), 0, T, 6), T, d]


def v_slot(tests):
    for t in tests:
        m, T, d = t["args"]
        assert len(m) <= 5000 and 1 <= d <= T <= 10 ** 9
        for s, e in m:
            assert 0 <= s < e <= T
    res = [t["expected"] for t in tests]
    assert -1 in res and any(x > 0 for x in res) and 0 in res


CHECKS["earliest-open-calendar-slot"] = (b_slot, g_slot, "exact")
VALIDATE["earliest-open-calendar-slot"] = v_slot

# ---------------------------------------------------------------- MEDIUM

p = add(
    id="employee-free-time-gaps", title="Employee Free Time", diff="Medium", topic=TOPIC,
    fn="commonFreeTime", params=[("busy", "int[][]")], ret="int[][]", cmp="exact",
    desc="<p>The working schedules of all employees of a team are pooled into one list <code>busy</code>. Each entry <code>[start, end]</code> is a period in which one employee is busy (half-open: the employee is free again at time <code>end</code>). Periods from different employees may overlap, nest or touch.</p><p>Return the periods of <em>common free time</em>: the maximal ranges <code>[a, b]</code> with <code>a &lt; b</code> in which <strong>nobody</strong> is busy. Only report gaps that lie strictly between the earliest start and the latest end of all busy periods (time before everyone has started or after everyone has finished does not count). List the gaps in increasing order. If there is no gap, return an empty array.</p><pre>busy = [[1, 3], [6, 7], [2, 4], [2, 5], [9, 12]]\nresult = [[5, 6], [7, 9]]</pre>",
    constraints=["0 &le; busy.length &le; 5,000", "busy[i] = [start, end] with 0 &le; start &lt; end &le; 10<sup>9</sup>", "The periods are in no particular order"],
    hints=["Time is common-free exactly when it is not covered by any busy period. So you need to find the holes in the union of all periods.",
           "Sort all periods by start time and sweep, remembering the furthest end time reached so far.",
           "When the next period starts strictly after the furthest end, the range between them is a gap. Otherwise the period extends (or is inside) the covered area: update the furthest end with <code>max</code>."],
    editorial=["Merge-style sweep. Sort the busy periods by start. Keep <code>reach</code>, the largest end time among the periods processed so far; initially it is the end of the first period. For each next period <code>[s, e]</code>: if <code>s &gt; reach</code>, nobody is busy during <code>[reach, s]</code>, so record that gap; then set <code>reach = max(reach, e)</code>. If <code>s == reach</code> the periods touch and no gap exists, because a gap needs positive length.",
               "Every recorded gap is maximal: it starts where coverage stops and ends where the next period begins. Gaps come out already sorted. With sorting the algorithm takes O(n log n) time; the output needs O(n) space in the worst case."],
    time="O(n log n)", space="O(n)",
    solution='''def commonFreeTime(busy):
    if not busy:
        return []
    ordered = sorted(busy)
    gaps = []
    reach = ordered[0][1]
    for s, e in ordered[1:]:
        if s > reach:
            gaps.append([reach, s])
        if e > reach:
            reach = e
    return gaps
''',
    tests=[[[[1, 3], [6, 7], [2, 4], [2, 5], [9, 12]]], [[]], [[[1, 5]]], [[[1, 2], [2, 3]]], [[[1, 2], [3, 4]]], [[[1, 10], [2, 3], [4, 5]]],
           [[[5, 6], [1, 2], [3, 4], [7, 8]]], [[[0, 1000000000], [5, 6]]], [[[0, 1], [1000000000 - 1, 1000000000]]],
           [[[1, 3], [3, 5], [5, 7], [8, 9], [9, 10], [12, 14], [13, 15]]], [[[4, 9], [1, 3], [2, 6], [10, 11], [10, 12]]]],
)
_r = rnd(4104)
_a = _ivs(_r, 1200, 0, 40000, 8)
p["tests"].append([_a])
_a = [[i * 3, i * 3 + _r.randint(1, 2)] for i in range(800)]
_r.shuffle(_a)
p["tests"].append([_a])
p["tests"].append([_ivs(_r, 700, 0, 10 ** 9, 5 * 10 ** 6)])
p["tests"].append([[[0, 1000]] * 1000 + [[1001, 1002]]])


def b_free(busy):
    if not busy:
        return []
    lo = min(s for s, _ in busy)
    hi = max(e for _, e in busy)
    covered = [any(s <= t < e for s, e in busy) for t in range(lo, hi)]
    out = []
    t = lo
    while t < hi:
        if not covered[t - lo]:
            u = t
            while u < hi and not covered[u - lo]:
                u += 1
            out.append([t, u])
            t = u
        else:
            t += 1
    return out


def g_free(r):
    return [_ivs(r, r.randint(0, 7), 0, 25, 5)]


def v_free(tests):
    for t in tests:
        busy = t["args"][0]
        assert len(busy) <= 5000
        for s, e in busy:
            assert 0 <= s < e <= 10 ** 9
    res = [t["expected"] for t in tests]
    assert any(len(x) == 0 for x in res) and any(len(x) > 3 for x in res)


CHECKS["employee-free-time-gaps"] = (b_free, g_free, "exact")
VALIDATE["employee-free-time-gaps"] = v_free

# ------------------------------------------------------------------

p = add(
    id="interval-partition-group-labels", title="Interval Partition Group Labels", diff="Medium", topic=TOPIC,
    fn="assignGroups", params=[("intervals", "int[][]")], ret="int[]", cmp="exact",
    desc="<p>Each interval <code>[start, end]</code> is <em>closed</em>: it contains every integer day from <code>start</code> to <code>end</code> inclusive. Two intervals that share even one day <em>overlap</em>, so <code>[1, 3]</code> and <code>[3, 5]</code> overlap.</p><p>Split the intervals into groups so that no two intervals in the same group overlap, using as few groups as possible. To make the answer unique, build the groups with this rule: handle the intervals in order of increasing <code>start</code> (ties broken by smaller input index), and put each interval into the <em>lowest-numbered</em> existing group whose latest interval ended before this interval starts; if no such group exists, open a new group with the next number. Groups are numbered <code>1, 2, 3, ...</code> in the order they are opened.</p><p>Return an array whose <code>i</code>-th element is the group number of <code>intervals[i]</code>.</p><pre>intervals = [[1, 3], [2, 5], [4, 6], [3, 8]]\nresult = [1, 2, 1, 3]</pre><p>The largest label in the result is the minimum number of groups.</p>",
    constraints=["0 &le; intervals.length &le; 5,000", "intervals[i] = [start, end] with 0 &le; start &le; end &le; 10<sup>9</sup>"],
    hints=["Process the intervals from left to right by start time. For the current interval, which groups could it join?",
           "A group is available when the end of its last interval is strictly smaller than the current start. You need the lowest-numbered available group quickly.",
           "Keep a min-heap of busy groups keyed by their last end and a min-heap of free group numbers. Before placing an interval, move every busy group whose end is smaller than the start to the free heap; then take the smallest free number or open a new group."],
    editorial=["This is interval partitioning (colouring an interval graph). Sort indices by <code>(start, index)</code>. Maintain two heaps: <code>busy</code> holds pairs <code>(end, group)</code> for groups whose last interval is still running, <code>free</code> holds numbers of groups that can take a new interval. For the current interval, pop from <code>busy</code> while <code>end &lt; start</code> and push those group numbers to <code>free</code>. Since starts never decrease, a group that became free stays free for all later intervals. Then take <code>heappop(free)</code> if there is one, else open group <code>count + 1</code>; push <code>(end, group)</code> to <code>busy</code>.",
               "The number of groups opened equals the largest number of intervals that cover a common day, which is also a lower bound, so the partition is optimal. Each interval is pushed and popped a constant number of times: O(n log n) time and O(n) space."],
    time="O(n log n)", space="O(n)",
    solution='''import heapq


def assignGroups(intervals):
    n = len(intervals)
    order = sorted(range(n), key=lambda i: (intervals[i][0], i))
    busy = []
    free = []
    groups = 0
    labels = [0] * n
    for i in order:
        s, e = intervals[i]
        while busy and busy[0][0] < s:
            heapq.heappush(free, heapq.heappop(busy)[1])
        if free:
            g = heapq.heappop(free)
        else:
            groups += 1
            g = groups
        labels[i] = g
        heapq.heappush(busy, (e, g))
    return labels
''',
    tests=[[[[1, 3], [2, 5], [4, 6], [3, 8]]], [[]], [[[5, 5]]], [[[1, 2], [3, 4], [5, 6]]], [[[1, 2], [2, 3], [3, 4]]], [[[1, 5], [1, 5], [1, 5]]],
           [[[10, 20], [1, 5], [6, 9], [2, 12], [21, 30]]], [[[0, 1000000000], [0, 0], [1, 999999999], [1000000000, 1000000000]]],
           [[[4, 8], [1, 3], [2, 4], [5, 7], [9, 10], [3, 6]]], [[[1, 10], [2, 9], [3, 8], [4, 7], [5, 6]]], [[[5, 6], [1, 2], [3, 4], [1, 2]]]],
)
_r = rnd(4105)
p["tests"].append([[[a, b - 1] for a, b in _ivs(_r, 1200, 0, 5000, 40)]])
p["tests"].append([[[a, b - 1] for a, b in _ivs(_r, 1000, 0, 100000, 100)]])
p["tests"].append([[[i, 8000 - i] for i in range(800)]])
p["tests"].append([[[a, b - 1] for a, b in _ivs(_r, 600, 0, 10 ** 9, 5 * 10 ** 6)]])


def b_groups(intervals):
    order = sorted(range(len(intervals)), key=lambda i: (intervals[i][0], i))
    last = []
    labels = [0] * len(intervals)
    for i in order:
        s, e = intervals[i]
        for g in range(len(last)):
            if last[g] < s:
                last[g] = e
                labels[i] = g + 1
                break
        else:
            last.append(e)
            labels[i] = len(last)
    return labels


def g_groups(r):
    return [[[a, b - 1] for a, b in _ivs(r, r.randint(0, 8), 0, 14, 5)]]


def v_groups(tests):
    for t in tests:
        iv = t["args"][0]
        lab = t["expected"]
        assert len(iv) <= 5000
        for s, e in iv:
            assert 0 <= s <= e <= 10 ** 9
        by = {}
        for (s, e), g in zip(iv, lab):
            by.setdefault(g, []).append((s, e))
        for g, lst in by.items():
            lst.sort()
            for a, b in zip(lst, lst[1:]):
                assert a[1] < b[0], "overlap inside a group"
        if lab:
            assert set(lab) == set(range(1, max(lab) + 1))
    assert any(len(t["args"][0]) > 0 and max(t["expected"]) >= 3 for t in tests)


CHECKS["interval-partition-group-labels"] = (b_groups, g_groups, "exact")
VALIDATE["interval-partition-group-labels"] = v_groups

# ------------------------------------------------------------------

p = add(
    id="min-rooms-with-cleaning-gap", title="Minimum Rooms With Cleaning Time", diff="Medium", topic=TOPIC, tier="extra",
    fn="minRoomsWithCleaning", params=[("meetings", "int[][]"), ("cleaning", "int")], ret="int", cmp="exact",
    desc="<p>Each meeting is a half-open range <code>[start, end)</code>. After a meeting ends, its room needs <code>cleaning</code> units of time before anybody may use it again, so a room that hosted a meeting ending at time <code>e</code> can host another meeting that starts at time <code>e + cleaning</code> or later. A room is also clean at the start of the day.</p><p>Return the minimum number of rooms needed to hold all the meetings.</p><pre>meetings = [[1, 4], [4, 6], [6, 9]], cleaning = 0  -&gt;  1\nmeetings = [[1, 4], [4, 6], [6, 9]], cleaning = 1  -&gt;  2\nmeetings = [[1, 4], [4, 6], [6, 9]], cleaning = 3  -&gt;  3</pre>",
    constraints=["0 &le; meetings.length &le; 5,000", "meetings[i] = [start, end] with 0 &le; start &lt; end &le; 10<sup>9</sup>", "0 &le; cleaning &le; 10<sup>9</sup>", "The meetings are in no particular order"],
    hints=["Without cleaning time this is the classic minimum-rooms problem. What changes when a room stays blocked a little longer?",
           "A meeting effectively occupies its room during <code>[start, end + cleaning)</code>.",
           "The answer is the largest number of these extended ranges that cover one moment. Sort starts and extended ends separately and sweep, or use a min-heap of room-free times."],
    editorial=["Replace each meeting by the extended range <code>[start, end + cleaning)</code>: during it the room cannot be given to anyone else. Two meetings can share a room exactly when their extended ranges do not overlap, so the question is the maximum number of extended ranges covering a common moment (interval graphs can always be coloured with as many colours as the maximum clique).",
               "Implementation with a min-heap of the times at which rooms become usable: process meetings by start; if the earliest-free room is usable at or before the start, pop it (reuse); push <code>end + cleaning</code> for the current meeting. The heap size at the end is the number of rooms. Equivalent two-pointer version: sort the starts and sort the extended ends; for every start, if it is at least the smallest unused extended end, advance that end pointer (reuse), otherwise count a new room. Time O(n log n), space O(n). Note that <code>end + cleaning</code> can reach 2&middot;10<sup>9</sup>, which overflows a 32-bit signed integer, so use 64-bit arithmetic in such languages."],
    time="O(n log n)", space="O(n)",
    solution='''def minRoomsWithCleaning(meetings, cleaning):
    starts = sorted(m[0] for m in meetings)
    ends = sorted(m[1] + cleaning for m in meetings)
    rooms = 0
    j = 0
    for s in starts:
        if s >= ends[j]:
            j += 1
        else:
            rooms += 1
    return rooms
''',
    tests=[[[[1, 4], [4, 6], [6, 9]], 0], [[[1, 4], [4, 6], [6, 9]], 1], [[[1, 4], [4, 6], [6, 9]], 3], [[], 5], [[[3, 4]], 100],
           [[[0, 30], [5, 10], [15, 20]], 5], [[[0, 30], [5, 10], [15, 20]], 0], [[[1, 2], [4, 5], [7, 8]], 2], [[[1, 2], [4, 5], [7, 8]], 3],
           [[[0, 1], [0, 1], [0, 1]], 0], [[[0, 1000000000], [1000000000 - 1, 1000000000]], 1000000000], [[[2, 3], [5, 6], [1, 7]], 1]],
)
_r = rnd(4106)
p["tests"].append([_ivs(_r, 1500, 0, 100000, 400), 25])
p["tests"].append([_ivs(_r, 1500, 0, 100000, 400), 0])
p["tests"].append([_ivs(_r, 700, 0, 10 ** 9, 10 ** 6), 5 * 10 ** 6])
p["tests"].append([[[i * 10, i * 10 + 9] for i in range(1500)], 1])


def b_cleaning(meetings, cleaning):
    best = 0
    for t in range(0, 60):
        best = max(best, sum(1 for s, e in meetings if s <= t < e + cleaning))
    return best


def g_cleaning(r):
    return [_ivs(r, r.randint(0, 7), 0, 18, 5), r.randint(0, 4)]


def v_cleaning(tests):
    for t in tests:
        m, c = t["args"]
        assert len(m) <= 5000 and 0 <= c <= 10 ** 9
        for s, e in m:
            assert 0 <= s < e <= 10 ** 9
        assert all(isinstance(x, int) for x in [t["expected"]])


CHECKS["min-rooms-with-cleaning-gap"] = (b_cleaning, g_cleaning, "exact")
VALIDATE["min-rooms-with-cleaning-gap"] = v_cleaning

# ------------------------------------------------------------------

p = add(
    id="max-meetings-with-buffer", title="Maximum Meetings With a Buffer", diff="Medium", topic=TOPIC,
    fn="maxMeetingsWithBuffer", params=[("meetings", "int[][]"), ("buffer", "int")], ret="int", cmp="exact",
    desc="<p>You work in a single room. Each requested meeting is a half-open range <code>[start, end)</code>. You may accept any subset of the requests, but between two accepted meetings the room needs a break: if one accepted meeting ends at time <code>e</code> and the next accepted one starts at time <code>s</code>, then <code>s - e &ge; buffer</code>.</p><p>Return the largest number of meetings you can accept.</p><pre>meetings = [[1, 3], [3, 5], [6, 8], [8, 10]], buffer = 0  -&gt;  4\nmeetings = [[1, 3], [3, 5], [6, 8], [8, 10]], buffer = 1  -&gt;  2</pre>",
    constraints=["0 &le; meetings.length &le; 5,000", "meetings[i] = [start, end] with 0 &le; start &lt; end &le; 10<sup>9</sup>", "0 &le; buffer &le; 10<sup>9</sup>", "The requests are in no particular order"],
    hints=["With <code>buffer = 0</code> this is the classic activity-selection problem. Recall which greedy rule solves it.",
           "Accepting the meeting that ends earliest leaves the most room for the rest. The buffer simply moves the point after which the next meeting may start.",
           "Sort by end time. Keep the end of the last accepted meeting; accept a meeting if its start is at least <code>lastEnd + buffer</code>, then update <code>lastEnd</code>."],
    editorial=["Exchange argument: among all meetings that are compatible with what is accepted so far, the one with the earliest end leaves the largest remaining window, and any optimal schedule can be changed to start with it without losing a meeting. The buffer only changes the compatibility test from <code>s &ge; lastEnd</code> to <code>s &ge; lastEnd + buffer</code>; the exchange argument still holds because replacing a meeting by one that ends no later can only make the next gap larger.",
               "Sort by end time (ties do not matter), sweep once and count. The sort gives O(n log n) time and O(n) space. Be careful with 32-bit overflow in other languages: <code>lastEnd + buffer</code> can reach 2&middot;10<sup>9</sup>."],
    time="O(n log n)", space="O(n)",
    solution='''def maxMeetingsWithBuffer(meetings, buffer):
    count = 0
    ready = None
    for s, e in sorted(meetings, key=lambda m: (m[1], m[0])):
        if ready is None or s >= ready:
            count += 1
            ready = e + buffer
    return count
''',
    tests=[[[[1, 3], [3, 5], [6, 8], [8, 10]], 0], [[[1, 3], [3, 5], [6, 8], [8, 10]], 1], [[], 3], [[[5, 6]], 0], [[[1, 2], [1, 2], [1, 2]], 0],
           [[[1, 10], [2, 3], [4, 5], [6, 7]], 0], [[[1, 10], [2, 3], [4, 5], [6, 7]], 1], [[[1, 10], [2, 3], [4, 5], [6, 7]], 2],
           [[[1, 100], [11, 22], [1, 11], [2, 12]], 0], [[[1, 100], [11, 22], [1, 11], [2, 12]], 5],
           [[[0, 1], [1000000000 - 1, 1000000000]], 1000000000], [[[0, 1], [1000000000 - 1, 1000000000]], 1000000000 - 2],
           [[[5, 6], [1, 2], [3, 4]], 1]],
)
_r = rnd(4107)
p["tests"].append([_ivs(_r, 1500, 0, 100000, 60), 7])
p["tests"].append([_ivs(_r, 1500, 0, 5000, 20), 0])
p["tests"].append([_ivs(_r, 800, 0, 10 ** 9, 10 ** 6), 2 * 10 ** 5])


def b_buffer(meetings, buffer):
    n = len(meetings)
    best = 0
    for mask in range(1 << n):
        ch = [meetings[i] for i in range(n) if mask >> i & 1]
        if len(ch) <= best:
            continue
        if all(a[1] + buffer <= b[0] or b[1] + buffer <= a[0] for a, b in combinations(ch, 2)):
            best = len(ch)
    return best


def g_buffer(r):
    return [_ivs(r, r.randint(0, 9), 0, 18, 6), r.randint(0, 3)]


def v_buffer(tests):
    for t in tests:
        m, b = t["args"]
        assert len(m) <= 5000 and 0 <= b <= 10 ** 9
        for s, e in m:
            assert 0 <= s < e <= 10 ** 9


CHECKS["max-meetings-with-buffer"] = (b_buffer, g_buffer, "exact")
VALIDATE["max-meetings-with-buffer"] = v_buffer

# ------------------------------------------------------------------

p = add(
    id="max-free-stretch-shift-k-meetings", title="Longest Free Stretch After Shifting Meetings", diff="Medium", topic=TOPIC, tier="extra",
    fn="maxFreeStretch", params=[("eventTime", "int"), ("k", "int"), ("startTime", "int[]"), ("endTime", "int[]")], ret="int", cmp="exact",
    desc="<p>A day lasts from time <code>0</code> to <code>eventTime</code>. There are <code>n</code> meetings; meeting <code>i</code> occupies the half-open range <code>[startTime[i], endTime[i])</code>. The meetings are given in order, never overlap, and may touch.</p><p>You may reschedule <strong>at most <code>k</code></strong> meetings. A rescheduled meeting keeps its duration and must stay within the day, the meetings must still not overlap, and the <em>relative order</em> of all meetings must not change. Other meetings stay where they are.</p><p>Return the maximum possible length of a continuous stretch of time in which no meeting takes place.</p><pre>eventTime = 10, k = 1, startTime = [0, 2, 9], endTime = [1, 3, 10]  -&gt;  7</pre><p>Move the meeting <code>[2, 3)</code> to <code>[1, 2)</code>; the stretch <code>[2, 9)</code> is then free.</p>",
    constraints=["1 &le; n &le; 5,000 where n = startTime.length = endTime.length", "0 &le; k &le; n", "1 &le; eventTime &le; 10<sup>9</sup>", "0 &le; startTime[i] &lt; endTime[i] &le; startTime[i+1] (for consecutive meetings), and endTime[n-1] &le; eventTime"],
    hints=["Look at the free gaps: before the first meeting, between consecutive meetings, and after the last one. There are n + 1 of them.",
           "Pushing a meeting to one side merges the two gaps next to it. Moving several neighbouring meetings merges even more gaps, while the total free time never changes.",
           "Moving k meetings can merge k + 1 consecutive gaps into one stretch. The answer is the largest sum of k + 1 consecutive gaps; use a sliding window."],
    editorial=["Write <code>gap[0]</code> for the time before meeting 0, <code>gap[i]</code> for the time between meeting <code>i-1</code> and meeting <code>i</code>, and <code>gap[n]</code> for the time after the last meeting. Because the order of meetings is kept, a free stretch in the final schedule is made of consecutive original gaps whose separating meetings were all pushed out of the way. Sliding <code>j</code> consecutive meetings to one side removes them from the middle of the stretch and merges the <code>j + 1</code> gaps around them, with total length equal to the sum of those gaps (meeting durations are preserved, so free time is only redistributed).",
               "With at most <code>k</code> moved meetings you can merge at most <code>k + 1</code> consecutive gaps, and any such window is achievable by pushing the meetings between them to the left end and the right end of the window. The answer is therefore the maximum sum over all windows of <code>min(k + 1, n + 1)</code> consecutive gaps, found in O(n) with a running window sum. Space is O(n) for the gaps (O(1) is possible)."],
    time="O(n)", space="O(n)",
    solution='''def maxFreeStretch(eventTime, k, startTime, endTime):
    gaps = []
    prev = 0
    for s, e in zip(startTime, endTime):
        gaps.append(s - prev)
        prev = e
    gaps.append(eventTime - prev)
    w = min(k + 1, len(gaps))
    cur = sum(gaps[:w])
    best = cur
    for i in range(w, len(gaps)):
        cur += gaps[i] - gaps[i - w]
        if cur > best:
            best = cur
    return best
''',
    tests=[[10, 1, [0, 2, 9], [1, 3, 10]], [5, 1, [1, 3], [2, 5]], [10, 0, [0, 2, 9], [1, 3, 10]], [10, 3, [0, 2, 9], [1, 3, 10]], [10, 2, [0, 2, 9], [1, 3, 10]],
           [1, 1, [0], [1]], [100, 0, [10], [20]], [100, 1, [10], [20]], [20, 2, [2, 5, 8, 15], [4, 6, 12, 18]], [20, 1, [2, 5, 8, 15], [4, 6, 12, 18]],
           [1000000000, 1, [0, 500000000], [500000000, 1000000000]], [12, 2, [1, 2, 3, 4, 5], [2, 3, 4, 5, 6]]],
)
_r = rnd(4108)
for _T, _n, _k, _mg, _ml in [(10 ** 9, 1000, 50, 400000, 400000), (10 ** 9, 1000, 1, 400000, 400000), (10 ** 9, 1000, 999, 1000, 1000)]:
    _s, _e = _sched(_r, _T, _n, _mg, _ml)
    p["tests"].append([_T, _k, _s, _e])
_s, _e = _sched(_r, 100000, 1500, 15, 10)
p["tests"].append([100000, 400, _s, _e])


def b_shift(eventTime, k, startTime, endTime):
    n = len(startTime)
    d = [e - s for s, e in zip(startTime, endTime)]
    suffix = [0] * (n + 1)
    for i in range(n - 1, -1, -1):
        suffix[i] = suffix[i + 1] + d[i]
    best = 0

    def rec(i, prev_end, changed, starts):
        nonlocal best
        if changed > k:
            return
        if i == n:
            pos = 0
            gap = 0
            for j in range(n):
                gap = max(gap, starts[j] - pos)
                pos = starts[j] + d[j]
            gap = max(gap, eventTime - pos)
            best = max(best, gap)
            return
        for p0 in range(prev_end, eventTime - suffix[i] + 1):
            rec(i + 1, p0 + d[i], changed + (p0 != startTime[i]), starts + [p0])

    rec(0, 0, 0, [])
    return best


def g_shift(r):
    T = r.randint(2, 11)
    while True:
        st, en = _sched(r, T, r.randint(1, 4), 3, 3)
        if st:
            break
    return [T, r.randint(0, len(st)), st, en]


def v_shift(tests):
    for t in tests:
        T, k, st, en = t["args"]
        assert 1 <= len(st) == len(en) <= 5000 and 0 <= k <= len(st) and 1 <= T <= 10 ** 9
        _sorted_disjoint(st, en, T)


CHECKS["max-free-stretch-shift-k-meetings"] = (b_shift, g_shift, "exact")
VALIDATE["max-free-stretch-shift-k-meetings"] = v_shift

# ------------------------------------------------------------------

p = add(
    id="max-free-time-move-one-meeting", title="Longest Free Stretch After Moving One Meeting", diff="Medium", topic=TOPIC, tier="extra",
    fn="maxFreeAfterMovingOne", params=[("eventTime", "int"), ("startTime", "int[]"), ("endTime", "int[]")], ret="int", cmp="exact",
    desc="<p>A day lasts from time <code>0</code> to <code>eventTime</code>. Meeting <code>i</code> occupies the half-open range <code>[startTime[i], endTime[i])</code>. The meetings are given in increasing order, never overlap, and may touch.</p><p>You may pick <strong>at most one</strong> meeting and move it to any other position in the day: it keeps its duration, must stay inside <code>[0, eventTime]</code> and must not overlap any other meeting. (It may jump over other meetings, so the order can change.) Return the maximum possible length of a continuous stretch of time without any meeting.</p><pre>eventTime = 10, startTime = [0, 7, 9], endTime = [1, 8, 10]  -&gt;  7</pre><p>Move <code>[0, 1)</code> into the gap between times 8 and 9; the free stretch <code>[0, 7)</code> appears.</p>",
    constraints=["1 &le; n &le; 5,000 where n = startTime.length = endTime.length", "1 &le; eventTime &le; 10<sup>9</sup>", "0 &le; startTime[i] &lt; endTime[i] &le; startTime[i+1] (for consecutive meetings), and endTime[n-1] &le; eventTime"],
    hints=["List the n + 1 free gaps. Moving meeting <code>i</code> merges the two gaps on its sides.",
           "After the merge, the meeting must go somewhere. If it fits into one of the other gaps, the merged stretch keeps its full size plus the meeting's length; if not, push the meeting to one end of the merged region and you still keep both gaps' total.",
           "For meeting <code>i</code> you need the largest gap among all gaps except the two adjacent ones. Prefix and suffix maxima over the gap array give it in O(1)."],
    editorial=["Let <code>gap[0..n]</code> be the free gaps; meeting <code>i</code> sits between <code>gap[i]</code> and <code>gap[i+1]</code> and has length <code>d</code>. If it is removed from its place, a free stretch of <code>gap[i] + d + gap[i+1]</code> appears, but the meeting must be put back somewhere. If some other gap (not <code>i</code> or <code>i+1</code>) has size at least <code>d</code>, put it there: the stretch stays at <code>gap[i] + d + gap[i+1]</code>. Otherwise slide it to the left or right end of that region, leaving <code>gap[i] + gap[i+1]</code>.",
               "Every original gap touches some meeting, so considering every meeting as the one to move also covers the option of not moving anything useful. Compute prefix maxima <code>pre</code> and suffix maxima <code>suf</code> of the gaps; the best other gap for meeting <code>i</code> is <code>max(pre[i], suf[i+2])</code>. Take the best candidate over all <code>i</code>. Time O(n), space O(n)."],
    time="O(n)", space="O(n)",
    solution='''def maxFreeAfterMovingOne(eventTime, startTime, endTime):
    n = len(startTime)
    gaps = []
    prev = 0
    for s, e in zip(startTime, endTime):
        gaps.append(s - prev)
        prev = e
    gaps.append(eventTime - prev)
    pre = [0] * (n + 2)
    for i in range(n + 1):
        pre[i + 1] = max(pre[i], gaps[i])
    suf = [0] * (n + 3)
    for i in range(n, -1, -1):
        suf[i] = max(suf[i + 1], gaps[i])
    best = 0
    for i in range(n):
        d = endTime[i] - startTime[i]
        merged = gaps[i] + gaps[i + 1]
        other = max(pre[i], suf[i + 2])
        best = max(best, merged + d if other >= d else merged)
    return best
''',
    tests=[[10, [0, 7, 9], [1, 8, 10]], [10, [0, 2, 9], [1, 3, 10]], [5, [1, 3], [2, 5]], [1, [0], [1]], [100, [10], [20]], [100, [0], [100]],
           [20, [2, 5, 8, 15], [4, 6, 12, 18]], [14, [2, 6, 10], [4, 8, 12]], [14, [0, 3, 6], [3, 6, 14]], [9, [1, 4, 7], [3, 6, 9]],
           [1000000000, [0, 500000000], [500000000, 1000000000]], [30, [1, 5, 6, 20], [4, 6, 8, 29]]],
)
_r = rnd(4109)
for _T, _n, _mg, _ml in [(10 ** 9, 1000, 400000, 400000), (10 ** 9, 1000, 1000, 100000), (100000, 1500, 15, 10)]:
    _s, _e = _sched(_r, _T, _n, _mg, _ml)
    p["tests"].append([_T, _s, _e])


def b_one(eventTime, startTime, endTime):
    n = len(startTime)

    def longest(iv):
        iv = sorted(iv)
        pos = 0
        g = 0
        for s, e in iv:
            g = max(g, s - pos)
            pos = e
        return max(g, eventTime - pos)

    base = list(zip(startTime, endTime))
    best = longest(base)
    for i in range(n):
        d = endTime[i] - startTime[i]
        others = base[:i] + base[i + 1:]
        for p0 in range(0, eventTime - d + 1):
            if all(not (p0 < e and s < p0 + d) for s, e in others):
                best = max(best, longest(others + [(p0, p0 + d)]))
    return best


def g_one(r):
    T = r.randint(2, 16)
    while True:
        st, en = _sched(r, T, r.randint(1, 5), 4, 4)
        if st:
            break
    return [T, st, en]


def v_one(tests):
    for t in tests:
        T, st, en = t["args"]
        assert 1 <= len(st) == len(en) <= 5000 and 1 <= T <= 10 ** 9
        _sorted_disjoint(st, en, T)


CHECKS["max-free-time-move-one-meeting"] = (b_one, g_one, "exact")
VALIDATE["max-free-time-move-one-meeting"] = v_one

# ---------------------------------------------------------------- HARD

p = add(
    id="max-meetings-k-rooms", title="Maximum Meetings Across K Rooms", diff="Hard", topic=TOPIC, tier="extra",
    fn="maxMeetingsKRooms", params=[("meetings", "int[][]"), ("k", "int")], ret="int", cmp="exact",
    desc="<p>A company has <code>k</code> identical meeting rooms. Each request is a half-open range <code>[start, end)</code>, so a room can host a meeting that starts exactly when the previous one in that room ends. A room hosts one meeting at a time, and a meeting must be held entirely in a single room.</p><p>You may reject requests. Return the largest number of requests that can be held.</p><pre>meetings = [[1, 4], [2, 5], [3, 6], [4, 7]], k = 2  -&gt;  3</pre><p>For example hold <code>[1, 4]</code> and <code>[4, 7]</code> in one room and <code>[2, 5]</code> in the other.</p>",
    constraints=["0 &le; meetings.length &le; 5,000", "1 &le; k &le; 100", "meetings[i] = [start, end] with 0 &le; start &lt; end &le; 10<sup>9</sup>", "The requests are in no particular order"],
    hints=["With <code>k = 1</code> this is activity selection: sort by end time and take every meeting that fits. How can this be extended to several rooms?",
           "Process meetings by increasing end time. A meeting that can be placed should be placed; the question is which room to put it in.",
           "Put it into the room that became free <em>latest</em> but still not after the meeting's start (best fit). That keeps the rooms that are free earlier available for meetings with earlier starts. Keep the free-from times of the k rooms in a sorted list and binary search it."],
    editorial=["Generalised activity selection. Sort meetings by end time (ties by start). Maintain, for each of the k rooms, the time since which it is free (initially 0). For the next meeting <code>[s, e)</code> look for the room with the largest free-time that is still at most <code>s</code>. If one exists, hold the meeting there and set that room's free-time to <code>e</code>; if none exists, every room is busy at <code>s</code> and the meeting is rejected.",
               "Why best fit: among rooms that can take the meeting, using the one that was free the latest wastes the least idle time, and the other rooms (free earlier) stay compatible with a superset of the remaining meetings. An exchange argument shows that this never loses a meeting compared with an optimal schedule, because all later meetings end no earlier than the current one.",
               "Keep the free-times in a sorted list: <code>bisect_right(free, s)</code> gives the number of rooms free by time <code>s</code>; remove the last of them, insert <code>e</code> with <code>insort</code>. With k &le; 100 each list operation is cheap. Total time O(n log n + n k) at worst, space O(k) beyond the sorted copy. As a sanity check, an accepted set is feasible exactly when no moment is covered by more than k accepted meetings."],
    time="O(n log n + n k)", space="O(n)",
    solution='''from bisect import bisect_right, insort


def maxMeetingsKRooms(meetings, k):
    free = [0] * k
    count = 0
    for s, e in sorted(meetings, key=lambda m: (m[1], m[0])):
        i = bisect_right(free, s)
        if i:
            free.pop(i - 1)
            insort(free, e)
            count += 1
    return count
''',
    tests=[[[[1, 4], [2, 5], [3, 6], [4, 7]], 2], [[], 3], [[[1, 2]], 1], [[[1, 5], [1, 5], [1, 5]], 2], [[[1, 5], [1, 5], [1, 5]], 3],
           [[[1, 3], [2, 4], [3, 5], [4, 6], [5, 7]], 1], [[[1, 3], [2, 4], [3, 5], [4, 6], [5, 7]], 2],
           [[[1, 10], [2, 3], [4, 5], [6, 7], [8, 9]], 1], [[[1, 10], [2, 3], [4, 5], [6, 7], [8, 9]], 2],
           [[[0, 1000000000], [0, 500000000], [500000000, 1000000000]], 2], [[[0, 4], [1, 2], [3, 6], [5, 8], [7, 9], [2, 7]], 2],
           [[[6, 9], [1, 4], [2, 8], [3, 5], [4, 7], [5, 10]], 3]],
)
_r = rnd(4110)
p["tests"].append([_ivs(_r, 1500, 0, 100000, 400), 5])
p["tests"].append([_ivs(_r, 1500, 0, 20000, 60), 2])
p["tests"].append([_ivs(_r, 800, 0, 10 ** 9, 10 ** 7), 40])
p["tests"].append([[[i, i + 1000] for i in range(1500)], 100])


def b_kroom(meetings, k):
    n = len(meetings)
    best = 0
    for mask in range(1 << n):
        ch = [meetings[i] for i in range(n) if mask >> i & 1]
        if len(ch) <= best:
            continue
        if all(sum(1 for s, e in ch if s <= t < e) <= k for t in range(0, 40)):
            best = len(ch)
    return best


def g_kroom(r):
    return [_ivs(r, r.randint(0, 9), 0, 16, 6), r.randint(1, 3)]


def v_kroom(tests):
    for t in tests:
        m, k = t["args"]
        assert len(m) <= 5000 and 1 <= k <= 100
        for s, e in m:
            assert 0 <= s < e <= 10 ** 9
    assert any(t["expected"] < len(t["args"][0]) for t in tests)


CHECKS["max-meetings-k-rooms"] = (b_kroom, g_kroom, "exact")
VALIDATE["max-meetings-k-rooms"] = v_kroom

# ------------------------------------------------------------------

p = add(
    id="max-value-k-events", title="Maximum Value From K Events", diff="Hard", topic=TOPIC, tier="extra",
    fn="maxValueKEvents", params=[("events", "int[][]"), ("k", "int")], ret="int", cmp="exact",
    desc="<p>Each event is <code>[startDay, endDay, value]</code>. It takes place on every day from <code>startDay</code> to <code>endDay</code> inclusive, and attending it earns <code>value</code>. You can only be at one event per day, so two attended events must not share any day: if you attend an event ending on day <code>d</code>, the next event must start on day <code>d + 1</code> or later.</p><p>You may attend at most <code>k</code> events. Return the largest total value you can collect.</p><pre>events = [[1, 3, 5], [2, 4, 6], [4, 6, 3], [5, 7, 4]], k = 2  -&gt;  10</pre><p>The best choice is <code>[2, 4, 6]</code> and <code>[5, 7, 4]</code>.</p>",
    constraints=["1 &le; events.length &le; 3,000", "1 &le; k &le; min(events.length, 100)", "events[i] = [startDay, endDay, value] with 1 &le; startDay &le; endDay &le; 10<sup>9</sup> and 1 &le; value &le; 10<sup>5</sup>", "Events are in no particular order"],
    hints=["Without the limit k this would be weighted interval scheduling. The limit adds a second dimension to the state.",
           "Sort events by start day. Let <code>dp[j][i]</code> be the best value using at most <code>j</code> events chosen among events <code>i, i+1, ...</code>. For event <code>i</code> you either skip it or take it and jump to the first event that starts after it ends.",
           "Find that next event with binary search on the sorted start days. Then <code>dp[j][i] = max(dp[j][i+1], value[i] + dp[j-1][next[i]])</code>. Only the previous layer <code>j-1</code> is needed."],
    editorial=["Sort the events by start day and precompute <code>next[i]</code>, the index of the first event whose start day is greater than <code>end[i]</code> (binary search with <code>bisect_right</code> on the start days). Define <code>dp[j][i]</code> as the maximum value obtainable from events with index at least <code>i</code> using at most <code>j</code> of them, with <code>dp[j][n] = 0</code> and <code>dp[0][i] = 0</code>.",
               "Transition: skip event <code>i</code> (<code>dp[j][i+1]</code>) or attend it and continue after it (<code>value[i] + dp[j-1][next[i]]</code>). Take the maximum. Because the transition for layer <code>j</code> reads only layer <code>j-1</code>, two arrays of length n + 1 suffice. The answer is <code>dp[k][0]</code>.",
               "A greedy choice by value or by earliest end fails because of the cap k and the differing values. Time is O(n log n + k&middot;n), space O(n). The largest answer is 3,000 &times; 10<sup>5</sup>, which fits in 32 bits."],
    time="O(n log n + k n)", space="O(n)",
    solution='''from bisect import bisect_right


def maxValueKEvents(events, k):
    ev = sorted(events)
    n = len(ev)
    starts = [e[0] for e in ev]
    nxt = [bisect_right(starts, e[1]) for e in ev]
    prev = [0] * (n + 1)
    for _ in range(k):
        cur = [0] * (n + 1)
        for i in range(n - 1, -1, -1):
            take = ev[i][2] + prev[nxt[i]]
            cur[i] = take if take > cur[i + 1] else cur[i + 1]
        prev = cur
    return prev[0]
''',
    tests=[[[[1, 3, 5], [2, 4, 6], [4, 6, 3], [5, 7, 4]], 2], [[[1, 2, 4], [3, 4, 3], [2, 3, 1]], 2], [[[1, 2, 4], [3, 4, 3], [2, 3, 10]], 3],
           [[[5, 5, 7]], 1], [[[1, 1, 1], [1, 1, 2], [1, 1, 3]], 3], [[[1, 10, 100], [2, 3, 30], [4, 5, 30], [6, 7, 30]], 1],
           [[[1, 10, 100], [2, 3, 30], [4, 5, 30], [6, 7, 30]], 2], [[[1, 10, 100], [2, 3, 30], [4, 5, 30], [6, 7, 30]], 3],
           [[[1, 3, 5], [3, 5, 5], [5, 7, 5]], 3], [[[1, 2, 5], [3, 4, 5], [5, 6, 5]], 2],
           [[[1, 1000000000, 100000], [1, 5, 99999], [6, 1000000000, 99999]], 1], [[[1, 1000000000, 100000], [1, 5, 99999], [6, 1000000000, 99999]], 2]],
)
_r = rnd(4111)


def _evs(r, n, hi, maxlen, vmax=100000):
    out = []
    for _ in range(n):
        s = r.randint(1, hi)
        out.append([s, min(10 ** 9, s + r.randint(0, maxlen)), r.randint(1, vmax)])
    return out


p["tests"].append([_evs(_r, 900, 20000, 40), 100])
p["tests"].append([_evs(_r, 800, 5000000, 5000), 60])
p["tests"].append([_evs(_r, 900, 3000, 8), 5])
p["tests"].append([[[i, i, _r.randint(1, 100000)] for i in range(1, 1201)], 100])


def b_kevents(events, k):
    n = len(events)
    best = 0
    for mask in range(1 << n):
        ch = [events[i] for i in range(n) if mask >> i & 1]
        if len(ch) > k:
            continue
        if all(a[1] < b[0] or b[1] < a[0] for a, b in combinations(ch, 2)):
            best = max(best, sum(c[2] for c in ch))
    return best


def g_kevents(r):
    n = r.randint(1, 9)
    return [[[s, s + r.randint(0, 4), r.randint(1, 20)] for s in (r.randint(1, 14) for _ in range(n))], r.randint(1, n)]


def v_kevents(tests):
    for t in tests:
        ev, k = t["args"]
        assert 1 <= len(ev) <= 3000 and 1 <= k <= min(len(ev), 100)
        for s, e, v in ev:
            assert 1 <= s <= e <= 10 ** 9 and 1 <= v <= 10 ** 5


CHECKS["max-value-k-events"] = (b_kevents, g_kevents, "exact")
VALIDATE["max-value-k-events"] = v_kevents
