"""Problems: intervals, sweep line (crowd counts, bookings, event sorting, skyline, union area). See data/lib.py for the registry."""
from itertools import combinations

from lib import add, rnd, CHECKS, VALIDATE, gen_arr  # noqa: F401

TOPIC = "Intervals"
MOD = 10 ** 9 + 7


def _ivs(r, n, lo, hi, maxlen):
    """n random half-open intervals [s, e) with lo <= s < e <= hi."""
    out = []
    for _ in range(n):
        s = r.randint(lo, hi - 1)
        out.append([s, min(hi, s + r.randint(1, maxlen))])
    return out


def _maxov(iv):
    """Largest number of half-open intervals sharing one moment."""
    ev = sorted([(s, 1) for s, e in iv] + [(e, -1) for s, e in iv])
    run = best = 0
    for _, d in ev:
        run += d
        best = max(best, run)
    return best


def _check_ivs(iv, nmax, lo, hi):
    assert len(iv) <= nmax
    for s, e in iv:
        assert lo <= s < e <= hi, (s, e)


# ---------------------------------------------------------------- EASY

p = add(
    id="first-moment-k-active", title="First Moment With K Active Sessions", diff="Easy", topic=TOPIC,
    fn="firstMomentWithK", params=[("sessions", "int[][]"), ("k", "int")], ret="int", cmp="exact",
    desc="<p>A server logs user sessions. Each session is a half-open time range <code>[start, end)</code>: it is active at every integer time <code>t</code> with <code>start &le; t &lt; end</code>, so a session that ends at time 5 and one that starts at time 5 are never active together.</p><p>Return the <strong>earliest</strong> integer time at which at least <code>k</code> sessions are active at once, or <code>-1</code> if that never happens. The sessions come in no particular order.</p><pre>sessions = [[1, 4], [2, 6], [3, 5]], k = 2  -&gt;  2\nsessions = [[1, 4], [2, 6], [3, 5]], k = 3  -&gt;  3\nsessions = [[0, 5], [5, 9]],         k = 2  -&gt; -1</pre>",
    constraints=["1 &le; sessions.length &le; 100,000", "sessions[i] = [start, end] with 0 &le; start &lt; end &le; 10<sup>9</sup>", "1 &le; k &le; 100,000"],
    hints=["Checking every time from 0 to the maximum end is far too slow when times go up to 10<sup>9</sup>. The number of active sessions only changes at a start or an end.",
           "Turn every session into two events: +1 at <code>start</code> and -1 at <code>end</code>. Sort the events by time and keep a running count.",
           "At equal times process the -1 events before the +1 events (a session ending at <code>t</code> is not active at <code>t</code>). Return the time of the first +1 event after which the count reaches <code>k</code>."],
    editorial=["The count of active sessions is a step function that only changes at event times. Create <code>(start, +1)</code> and <code>(end, -1)</code> for each session and sort them; tuples <code>(time, delta)</code> sort a -1 before a +1 at the same time, which is exactly the half-open rule.",
               "Sweep the sorted events with a running total. The count can only increase on a +1 event, so the first time the total reaches <code>k</code> it happens at the time of that event, and nothing earlier can be a valid answer. If the sweep ends without reaching <code>k</code>, return -1. Sorting dominates: O(n log n) time, O(n) space."],
    time="O(n log n)", space="O(n)",
    solution='''def firstMomentWithK(sessions, k):
    events = []
    for s, e in sessions:
        events.append((s, 1))
        events.append((e, -1))
    events.sort()
    active = 0
    for t, d in events:
        active += d
        if active >= k:
            return t
    return -1
''',
    tests=[[[[1, 4], [2, 6], [3, 5]], 2], [[[1, 4], [2, 6], [3, 5]], 3], [[[0, 5], [5, 9]], 2], [[[1, 4], [2, 6], [3, 5]], 4],
           [[[0, 1]], 1], [[[5, 9], [0, 5]], 1], [[[2, 3], [2, 3], [2, 3]], 3], [[[1, 10], [3, 4], [3, 4]], 3],
           [[[0, 10 ** 9]], 1], [[[0, 10 ** 9], [10 ** 9 - 1, 10 ** 9]], 2], [[[4, 6], [1, 2], [1, 2], [6, 8]], 2],
           [[[7, 9], [1, 3], [2, 8], [5, 6]], 3]],
)
_r = rnd(9301)
_a = _ivs(_r, 2000, 0, 10 ** 6, 4000)
p["tests"].append([_a, _maxov(_a) // 2 + 1])
p["tests"].append([_a, _maxov(_a) + 1])
_a = _ivs(_r, 1800, 0, 10 ** 9, 3 * 10 ** 6)
p["tests"].append([_a, _maxov(_a)])


def b_firstk(sessions, k):
    for t in range(0, max(e for _, e in sessions) + 1):
        if sum(1 for s, e in sessions if s <= t < e) >= k:
            return t
    return -1


def g_firstk(r):
    return [_ivs(r, r.randint(1, 8), 0, 14, 6), r.randint(1, 5)]


def v_firstk(tests):
    for t in tests:
        sessions, k = t["args"]
        _check_ivs(sessions, 100000, 0, 10 ** 9)
        assert len(sessions) >= 1 and 1 <= k <= 100000
        if t["expected"] != -1:
            assert t["expected"] >= 0


CHECKS["first-moment-k-active"] = (b_firstk, g_firstk, "exact")
VALIDATE["first-moment-k-active"] = v_firstk

p = add(
    id="min-starting-stock-for-event-log", title="Minimum Starting Stock for an Event Log", diff="Easy", topic=TOPIC, tier="extra",
    fn="minStartingStock", params=[("events", "int[][]")], ret="int", cmp="exact",
    desc="<p>A warehouse log lists stock changes as <code>[time, change]</code>: a positive <code>change</code> is a delivery, a negative one is a pickup. The entries are in no particular order.</p><p>All changes that carry the <strong>same time</strong> happen together, so only their total counts at that moment. The stock level must never drop below zero after any moment has been applied.</p><p>Return the smallest non-negative initial stock for which this holds.</p><pre>events = [[5, -3], [1, 2], [5, 2], [3, -4]]  -&gt;  3</pre><p>Sorted by time the totals are +2 at time 1, -4 at time 3 and -1 at time 5. Starting with 3, the stock goes 5, 1, 0 and never gets negative; starting with 2 it would reach -1.</p>",
    constraints=["0 &le; events.length &le; 100,000", "events[i] = [time, change] with 0 &le; time &le; 10<sup>9</sup>", "-10,000 &le; change &le; 10,000", "Several events may share the same time"],
    hints=["The order of the entries in the input does not matter, but the order of the times does. What should you do first with the list?",
           "After sorting by time and adding up the changes of equal times, you get a running balance. The initial stock only shifts that whole balance up.",
           "If the lowest running balance (starting from 0) is <code>m</code> and it is negative, you need exactly <code>-m</code> units at the start; if it never goes below 0 the answer is 0."],
    editorial=["Let <code>b</code> be the running total of changes after each distinct time, starting from zero. With an initial stock <code>s</code> the actual stock is <code>s + b</code>, which must stay non-negative everywhere. That is the case exactly when <code>s &ge; -min(b)</code>, so the answer is <code>max(0, -min(b))</code>.",
               "Grouping equal times matters: a pickup and a delivery at the same moment cancel, and only the net effect is checked. Sort the events by time (or collect the totals in a map and sort its keys), sweep once, and track the minimum balance. O(n log n) time, O(n) space."],
    time="O(n log n)", space="O(n)",
    solution='''def minStartingStock(events):
    totals = {}
    for t, c in events:
        totals[t] = totals.get(t, 0) + c
    balance = 0
    lowest = 0
    for t in sorted(totals):
        balance += totals[t]
        if balance < lowest:
            lowest = balance
    return -lowest
''',
    tests=[[[[5, -3], [1, 2], [5, 2], [3, -4]]], [[]], [[[1, 5]]], [[[1, -5]]], [[[2, -3], [2, 3]]], [[[2, -3], [1, 1], [2, 1]]],
           [[[1, -1], [2, -1], [3, -1]]], [[[1, 10000], [2, -10000], [3, -10000]]], [[[10 ** 9, -7], [0, 3], [10 ** 9, 4]]],
           [[[4, 6], [4, -2], [9, -5], [9, -2], [12, -1]]], [[[3, -2], [3, -2], [3, 4]]]],
)
_r = rnd(9302)
p["tests"].append([[[_r.randint(0, 10 ** 6), _r.randint(-50, 50)] for _ in range(3000)]])
p["tests"].append([[[_r.randint(0, 300), _r.randint(-60, 40)] for _ in range(3000)]])
p["tests"].append([[[i, -10000] for i in range(2999, -1, -1)]])


def b_stock(events):
    for s in range(0, 400):
        times = sorted({t for t, _ in events})
        ok = True
        cur = s
        for t in times:
            cur += sum(c for tt, c in events if tt == t)
            if cur < 0:
                ok = False
                break
        if ok:
            return s
    return -1


def g_stock(r):
    return [[[r.randint(0, 8), r.randint(-6, 6)] for _ in range(r.randint(0, 9))]]


def v_stock(tests):
    for t in tests:
        ev = t["args"][0]
        assert len(ev) <= 100000
        assert all(0 <= a <= 10 ** 9 and -10000 <= c <= 10000 for a, c in ev)
        assert t["expected"] >= 0


CHECKS["min-starting-stock-for-event-log"] = (b_stock, g_stock, "exact")
VALIDATE["min-starting-stock-for-event-log"] = v_stock

# ---------------------------------------------------------------- MEDIUM

p = add(
    id="count-overlapping-interval-pairs", title="Count Overlapping Pairs of Sessions", diff="Medium", topic=TOPIC,
    fn="countOverlappingPairs", params=[("intervals", "int[][]")], ret="int", cmp="exact",
    desc="<p>Each interval <code>[start, end)</code> is half-open: it covers every moment <code>t</code> with <code>start &le; t &lt; end</code>. Two intervals <strong>overlap</strong> when some moment is covered by both; intervals that merely touch (one ends exactly where the other starts) do not overlap.</p><p>Count the unordered pairs of different intervals (different positions in the list) that overlap. Identical intervals count as separate ones.</p><pre>intervals = [[1, 4], [2, 6], [5, 8]]  -&gt;  2</pre><p>The first two overlap and the last two overlap, but the first and the last do not.</p>",
    constraints=["0 &le; intervals.length &le; 50,000", "intervals[i] = [start, end] with 0 &le; start &lt; end &le; 10<sup>9</sup>", "The answer is at most 50,000 &middot; 49,999 / 2 &lt; 2<sup>31</sup>"],
    hints=["Testing all pairs is O(n<sup>2</sup>), too slow for 50,000 intervals. Count the pairs differently: group them by the interval that starts <em>later</em>.",
           "Sort the intervals by start. For the i-th interval in that order, an earlier one overlaps it exactly when it has not ended by the time the i-th starts.",
           "Among the i earlier intervals, those that ended are the intervals with <code>end &le; start_i</code>. Count them with a binary search in the sorted list of all ends, and add <code>i - ended</code>."],
    editorial=["Two intervals overlap exactly when the one that starts later (ties: either) starts before the other one ends. So walk through the intervals in order of start; the pairs formed with earlier-starting intervals are the earlier intervals that are still active at this start.",
               "Every interval with <code>end &le; start_i</code> began strictly before <code>start_i</code>, so it is among the first <code>i</code> intervals in sorted order. Therefore the number of active earlier intervals is <code>i - (number of ends &le; start_i)</code>, and the number of ends is found by binary search in the sorted array of ends. Summing over i gives the answer in O(n log n) time and O(n) space.",
               "Equivalently you can sweep events and add the current number of active intervals every time a new one starts."],
    time="O(n log n)", space="O(n)",
    solution='''from bisect import bisect_right


def countOverlappingPairs(intervals):
    starts = sorted(s for s, e in intervals)
    ends = sorted(e for s, e in intervals)
    total = 0
    for i, s in enumerate(starts):
        total += i - bisect_right(ends, s)
    return total
''',
    tests=[[[[1, 4], [2, 6], [5, 8]]], [[]], [[[3, 4]]], [[[1, 2], [2, 3]]], [[[1, 5], [1, 5], [1, 5]]], [[[0, 10], [1, 2], [3, 4], [5, 6]]],
           [[[5, 6], [1, 2], [3, 4], [2, 3]]], [[[1, 3], [1, 3]]], [[[0, 10 ** 9], [10 ** 9 - 1, 10 ** 9], [0, 1]]],
           [[[4, 9], [1, 3], [2, 6], [10, 11], [10, 12], [8, 10]]]],
)
_r = rnd(9303)
p["tests"].append([_ivs(_r, 1800, 0, 10 ** 6, 900)])
p["tests"].append([_ivs(_r, 1800, 0, 10 ** 9, 10 ** 8)])
p["tests"].append([[[i, 10 ** 9 - i] for i in range(1500)]])
p["tests"].append([[[2 * i, 2 * i + 1] for i in range(600)]])


def b_pairs(intervals):
    return sum(1 for a, b in combinations(intervals, 2) if max(a[0], b[0]) < min(a[1], b[1]))


def g_pairs(r):
    return [_ivs(r, r.randint(0, 9), 0, 14, 7)]


def v_pairs(tests):
    for t in tests:
        _check_ivs(t["args"][0], 50000, 0, 10 ** 9)


CHECKS["count-overlapping-interval-pairs"] = (b_pairs, g_pairs, "exact")
VALIDATE["count-overlapping-interval-pairs"] = v_pairs

p = add(
    id="time-at-each-crowd-level", title="Time Spent at Each Crowd Level", diff="Medium", topic=TOPIC,
    fn="timeAtEachLevel", params=[("intervals", "int[][]"), ("T", "int")], ret="int[]", cmp="exact",
    desc="<p>A museum is open from time <code>0</code> to time <code>T</code>. Each visitor group stays for a half-open range <code>[start, end)</code> with <code>0 &le; start &lt; end &le; T</code>. The groups are in no particular order.</p><p>Return an array <code>res</code> of length <code>n + 1</code> (where <code>n</code> is the number of groups) such that <code>res[c]</code> is the total length of time, inside <code>[0, T)</code>, during which <strong>exactly</strong> <code>c</code> groups are in the museum. The entries always add up to <code>T</code>.</p><pre>intervals = [[1, 3], [2, 4]], T = 5  -&gt;  [2, 2, 1]</pre><p>Nobody is inside during [0, 1) and [4, 5) (2 units), exactly one group during [1, 2) and [3, 4) (2 units), and two groups during [2, 3) (1 unit).</p>",
    constraints=["0 &le; intervals.length &le; 100,000", "1 &le; T &le; 10<sup>9</sup>", "intervals[i] = [start, end] with 0 &le; start &lt; end &le; T"],
    hints=["T can be 10<sup>9</sup>, so you cannot loop over every time unit. How many different times can the crowd size change at?",
           "Between two consecutive event times (starts and ends of the groups) the crowd size is constant. Sort the distinct event times.",
           "Keep the current crowd size <code>c</code> and the previous event time. At each new event time <code>t</code> add <code>t - prev</code> to <code>res[c]</code>, then apply the change (+1 for starts, -1 for ends) of all events at <code>t</code>. Finally add <code>T - prev</code> to <code>res[0]</code>."],
    editorial=["Collect the net change of the crowd size for every distinct event time in a map. Process the times in increasing order, remembering the previous time and the crowd size that held since then. The stretch <code>[prev, t)</code> had exactly <code>c</code> groups, so add its length to <code>res[c]</code>; then update <code>c</code> with the net change at <code>t</code>.",
               "Before the first event and after the last one the museum is empty, so the stretch from 0 to the first event time and the stretch from the last event time to <code>T</code> both go to <code>res[0]</code> (the code handles the first one with <code>prev = 0</code> and <code>c = 0</code>). Using net changes per time removes any worry about the order of starts and ends at the same time. O(n log n) time because of the sort, O(n) space."],
    time="O(n log n)", space="O(n)",
    solution='''def timeAtEachLevel(intervals, T):
    delta = {}
    for s, e in intervals:
        delta[s] = delta.get(s, 0) + 1
        delta[e] = delta.get(e, 0) - 1
    res = [0] * (len(intervals) + 1)
    crowd = 0
    prev = 0
    for t in sorted(delta):
        res[crowd] += t - prev
        crowd += delta[t]
        prev = t
    res[crowd] += T - prev
    return res
''',
    tests=[[[[1, 3], [2, 4]], 5], [[], 5], [[[0, 5]], 5], [[[0, 5], [0, 5]], 5], [[[0, 2], [2, 5]], 5], [[[3, 4]], 10],
           [[[1, 9], [2, 8], [3, 7], [4, 6]], 10], [[[0, 1], [0, 1], [1, 2], [1, 2], [1, 2]], 3], [[[0, 10 ** 9]], 10 ** 9],
           [[[5, 10 ** 9], [0, 7], [6, 6 + 1]], 10 ** 9], [[[4, 9], [1, 3], [2, 6], [10, 11], [10, 12], [8, 10]], 12], [[], 1]],
)
_r = rnd(9304)
p["tests"].append([_ivs(_r, 1500, 0, 10 ** 6, 8000), 10 ** 6])
p["tests"].append([_ivs(_r, 1500, 0, 10 ** 9, 5 * 10 ** 6), 10 ** 9])


def b_levels(intervals, T):
    res = [0] * (len(intervals) + 1)
    for t in range(T):
        res[sum(1 for s, e in intervals if s <= t < e)] += 1
    return res


def g_levels(r):
    T = r.randint(1, 14)
    return [_ivs(r, r.randint(0, 7), 0, T, 6) if T > 0 else [], T]


def v_levels(tests):
    for t in tests:
        iv, T = t["args"]
        _check_ivs(iv, 100000, 0, T)
        assert 1 <= T <= 10 ** 9
        assert len(t["expected"]) == len(iv) + 1 and sum(t["expected"]) == T


CHECKS["time-at-each-crowd-level"] = (b_levels, g_levels, "exact")
VALIDATE["time-at-each-crowd-level"] = v_levels

p = add(
    id="double-booking-calendar", title="Calendar With At Most Two Overlapping Events", diff="Medium", topic=TOPIC,
    fn="bookUpToTwoOverlapping", params=[("requests", "int[][]")], ret="int[]", cmp="exact",
    desc="<p>A shared calendar receives booking requests one after another. A request <code>[start, end)</code> is a half-open range. The calendar tolerates a double booking, but never a triple one: a request is <strong>accepted</strong> if, after adding it to the accepted events, no moment is covered by three or more accepted events; otherwise it is <strong>rejected</strong> and the calendar stays unchanged.</p><p>Process the requests in the given order and return an array with <code>1</code> for every accepted request and <code>0</code> for every rejected one.</p><pre>requests = [[10, 20], [50, 60], [10, 40], [5, 15], [5, 10], [25, 55]]\nresult   = [1, 1, 1, 0, 1, 1]</pre><p>[5, 15) is rejected because [10, 15) is already covered by [10, 20) and [10, 40). [5, 10) is fine since it only touches that double-booked region.</p>",
    constraints=["0 &le; requests.length &le; 1,000", "requests[i] = [start, end] with 0 &le; start &lt; end &le; 10<sup>9</sup>"],
    hints=["Checking a request against the accepted events one pair at a time is not enough: three events can overlap even if no single pair looks dangerous. What kind of region is dangerous?",
           "A new request is bad exactly when it overlaps a region that is <em>already</em> covered twice. Keep a list of such double-covered ranges.",
           "Keep two lists: accepted events and double-covered ranges. A request is rejected if it overlaps any double range. Otherwise accept it and add its intersection with every accepted event to the double ranges (use <code>max(starts)</code> and <code>min(ends)</code> and keep the intersection only if it is non-empty)."],
    editorial=["Maintain <code>events</code> (all accepted ranges) and <code>doubles</code> (every range covered by at least two accepted events). A request <code>[s, e)</code> would create a triple booking if and only if it shares a moment with some range of <code>doubles</code>: any such moment is already covered twice, and the request adds a third cover.",
               "If it passes that test, accept it. Its overlaps with existing events become new double-covered ranges, so append <code>[max(s, a), min(e, b)]</code> for every accepted event <code>[a, b)</code> when that range is not empty. Because the request does not touch any old double range, no moment can be covered more than twice, and the invariant holds. Each request costs O(n), so the total is O(n<sup>2</sup>) time and O(n) space, fine for 1,000 requests.",
               "A sweep alternative: for each request, add it tentatively to the events, sort the events and check the running count; that is O(n<sup>2</sup> log n) overall."],
    time="O(n^2)", space="O(n)",
    solution='''def bookUpToTwoOverlapping(requests):
    events = []
    doubles = []
    result = []
    for s, e in requests:
        if any(s < b and a < e for a, b in doubles):
            result.append(0)
            continue
        for a, b in events:
            lo = max(s, a)
            hi = min(e, b)
            if lo < hi:
                doubles.append((lo, hi))
        events.append((s, e))
        result.append(1)
    return result
''',
    tests=[[[[10, 20], [50, 60], [10, 40], [5, 15], [5, 10], [25, 55]]], [[]], [[[1, 2]]], [[[1, 2], [1, 2], [1, 2]]],
           [[[1, 5], [1, 5], [5, 9], [5, 9], [1, 9]]], [[[1, 10], [3, 5], [4, 6], [2, 3], [5, 6]]],
           [[[0, 10 ** 9], [0, 10 ** 9], [10 ** 9 - 1, 10 ** 9]]], [[[1, 4], [2, 6], [3, 8], [6, 7], [4, 5]]],
           [[[3, 7], [1, 4], [6, 9], [2, 8], [0, 1], [8, 10], [4, 6]]], [[[1, 3], [2, 4], [3, 5], [4, 6], [5, 7], [1, 7]]]],
)
_r = rnd(9305)
p["tests"].append([_ivs(_r, 1000, 0, 5000, 150)])
p["tests"].append([_ivs(_r, 1000, 0, 10 ** 9, 4 * 10 ** 7)])
p["tests"].append([_ivs(_r, 1000, 0, 100000, 400)])


def b_cal(requests):
    accepted = []
    out = []
    for s, e in requests:
        trial = accepted + [(s, e)]
        ev = sorted([(a, 1) for a, b in trial] + [(b, -1) for a, b in trial])
        run = peak = 0
        for _, d in ev:
            run += d
            peak = max(peak, run)
        if peak <= 2:
            accepted = trial
            out.append(1)
        else:
            out.append(0)
    return out


def g_cal(r):
    return [_ivs(r, r.randint(0, 9), 0, 14, 8)]


def v_cal(tests):
    for t in tests:
        _check_ivs(t["args"][0], 1000, 0, 10 ** 9)
    big = [t for t in tests if len(t["args"][0]) >= 1000]
    for t in big:
        assert 0 in t["expected"] and 1 in t["expected"]


CHECKS["double-booking-calendar"] = (b_cal, g_cal, "exact")
VALIDATE["double-booking-calendar"] = v_cal

p = add(
    id="first-overflow-booking", title="First Booking That Overflows the Capacity", diff="Medium", topic=TOPIC, tier="extra",
    fn="firstOverflowBooking", params=[("bookings", "int[][]"), ("capacity", "int")], ret="int", cmp="exact",
    desc="<p>A hall has <code>capacity</code> seats. Each booking is <code>[start, end, seats]</code>: it reserves <code>seats</code> seats for the half-open time range <code>[start, end)</code>. Bookings are made one after another and the hall never rejects them.</p><p>Return the 0-based index of the <strong>first booking</strong> after which there is some moment at which the total reserved seats exceed <code>capacity</code>. If this never happens, return <code>-1</code>.</p><pre>bookings = [[1, 5, 3], [3, 8, 2], [4, 6, 2]], capacity = 6  -&gt;  2\nbookings = [[1, 5, 3], [5, 9, 3]],            capacity = 3  -&gt; -1</pre><p>In the first example, at time 4 the first three bookings together reserve 3 + 2 + 2 = 7 seats; the first two alone reserve at most 5.</p>",
    constraints=["0 &le; bookings.length &le; 20,000", "bookings[i] = [start, end, seats] with 0 &le; start &lt; end &le; 10<sup>9</sup> and 1 &le; seats &le; 10,000", "1 &le; capacity &le; 10<sup>9</sup>"],
    hints=["Re-checking the hall after every single booking costs O(n) or O(n log n) each time. Is there something monotonic you can search over?",
           "If the first <code>k</code> bookings already overflow the hall, then so do the first <code>k + 1</code> bookings (more reservations never help). So the answer is the smallest <code>k</code> where the prefix overflows.",
           "Binary search on the prefix length. To test a prefix, sweep its events: +seats at start, -seats at end, sorted by time with the negative changes first at equal times, and see if the running total ever exceeds <code>capacity</code>."],
    editorial=["Define <code>overflow(k)</code> as: do the first k bookings together exceed the capacity at some moment? Adding bookings can only increase the load at every moment, so <code>overflow</code> is monotone: false, false, ..., true, true. The answer is the (0-based) index of the first booking for which it becomes true.",
               "Evaluating <code>overflow(k)</code> is a plain sweep: build the events <code>(start, +seats)</code> and <code>(end, -seats)</code>, sort them (a pair with a negative change sorts before a positive one at the same time, so a booking that ends at <code>t</code> frees its seats before a booking starting at <code>t</code> takes seats), and track the running total. With binary search over k the total cost is O(n log<sup>2</sup> n) time and O(n) space.",
               "Check the full list first: if even all bookings fit, the answer is -1."],
    time="O(n log^2 n)", space="O(n)",
    solution='''def firstOverflowBooking(bookings, capacity):
    def overflow(k):
        events = []
        for s, e, c in bookings[:k]:
            events.append((s, c))
            events.append((e, -c))
        events.sort()
        load = 0
        for _, d in events:
            load += d
            if load > capacity:
                return True
        return False

    n = len(bookings)
    if not overflow(n):
        return -1
    lo, hi = 1, n
    while lo < hi:
        mid = (lo + hi) // 2
        if overflow(mid):
            hi = mid
        else:
            lo = mid + 1
    return lo - 1
''',
    tests=[[[[1, 5, 3], [3, 8, 2], [4, 6, 2]], 6], [[[1, 5, 3], [5, 9, 3]], 3], [[], 1], [[[1, 2, 5]], 4], [[[1, 2, 5]], 5],
           [[[1, 4, 2], [2, 6, 2], [3, 5, 2], [4, 7, 2]], 5], [[[1, 4, 2], [2, 6, 2], [3, 5, 2], [4, 7, 2]], 4],
           [[[0, 10 ** 9, 10000], [0, 10 ** 9, 10000], [5, 6, 1]], 20000], [[[5, 9, 4], [1, 5, 4], [9, 12, 4], [3, 7, 1]], 4],
           [[[2, 3, 1], [2, 3, 1], [2, 3, 1], [2, 3, 1]], 3]],
)
_r = rnd(9306)
_b = [[s, e, _r.randint(1, 50)] for s, e in _ivs(_r, 1500, 0, 10 ** 6, 3000)]
p["tests"].append([_b, 6 * 10 ** 4])
p["tests"].append([_b, 10 ** 9])
_b = [[s, e, _r.randint(1, 10000)] for s, e in _ivs(_r, 1500, 0, 10 ** 9, 10 ** 6)]
p["tests"].append([_b, 15000])


def b_over(bookings, capacity):
    for k in range(1, len(bookings) + 1):
        part = bookings[:k]
        for s, _, _ in part:
            if sum(c for a, b, c in part if a <= s < b) > capacity:
                return k - 1
    return -1


def g_over(r):
    return [[[s, e, r.randint(1, 4)] for s, e in _ivs(r, r.randint(0, 8), 0, 12, 6)], r.randint(1, 8)]


def v_over(tests):
    for t in tests:
        b, cap = t["args"]
        assert len(b) <= 20000 and 1 <= cap <= 10 ** 9
        assert all(0 <= s < e <= 10 ** 9 and 1 <= c <= 10000 for s, e, c in b)
    assert any(t["expected"] == -1 for t in tests) and any(t["expected"] > 0 for t in tests)


CHECKS["first-overflow-booking"] = (b_over, g_over, "exact")
VALIDATE["first-overflow-booking"] = v_over

p = add(
    id="silhouette-area-of-buildings", title="Area Under a Skyline Silhouette", diff="Medium", topic=TOPIC, tier="extra",
    fn="silhouetteArea", params=[("buildings", "int[][]")], ret="int", cmp="exact",
    desc="<p>Rectangular buildings stand on a flat line. Building <code>[left, right, height]</code> occupies the horizontal range from <code>left</code> to <code>right</code> (width <code>right - left</code>) and is <code>height</code> tall. Buildings may overlap, nest or touch.</p><p>Seen from far away, the buildings form one silhouette: above every position <code>x</code> its height is the tallest building covering <code>x</code> (0 where there is none). Return the <strong>area</strong> under this silhouette, modulo <code>1,000,000,007</code>.</p><pre>buildings = [[2, 9, 10], [3, 7, 15], [5, 12, 12], [15, 20, 10], [19, 24, 8]]  -&gt;  212</pre><p>Heights: 10 on [2, 3), 15 on [3, 7), 12 on [7, 12), 0 on [12, 15), 10 on [15, 20) and 8 on [20, 24), so the area is 10 + 60 + 60 + 0 + 50 + 32 = 212.</p>",
    constraints=["0 &le; buildings.length &le; 50,000", "buildings[i] = [left, right, height] with 0 &le; left &lt; right &le; 10<sup>9</sup>", "1 &le; height &le; 10<sup>9</sup>", "The true area can exceed 32 bits, hence the modulo"],
    hints=["Adding up the areas of the rectangles double-counts overlaps. Between two neighbouring building edges the silhouette is flat, though. How many such flat pieces are there?",
           "Sort all distinct x-coordinates (every left and right edge). Between two consecutive coordinates the height is the maximum height of the buildings covering that strip.",
           "Sweep left to right with a max-heap of <code>(height, right)</code>. Push buildings whose left edge has been reached, pop the top while its right edge is already behind you, and multiply the top height by the strip width."],
    editorial=["Let <code>x<sub>0</sub> &lt; x<sub>1</sub> &lt; ...</code> be the sorted distinct edge coordinates. Inside the strip <code>[x<sub>i</sub>, x<sub>i+1</sub>)</code> no building starts or ends, so each building either covers the whole strip or none of it, and the silhouette height is constant there.",
               "Sweep the strips from left to right. A max-heap keyed by height stores <code>(height, right)</code> of the buildings that have started. At strip i, push every building with <code>left &le; x<sub>i</sub></code> and pop the top while its <code>right &le; x<sub>i</sub></code> (lazy deletion: a stale entry that is not on top cannot influence the maximum). The top height times the strip width is the contribution of the strip; empty heap means height 0.",
               "Each building enters and leaves the heap once: O(n log n) time, O(n) space. Python integers do not overflow, so take the modulo at the end (in fixed-width languages reduce after each strip)."],
    time="O(n log n)", space="O(n)",
    solution='''import heapq


def silhouetteArea(buildings):
    MOD = 1000000007
    bs = sorted(buildings)
    xs = sorted({x for l, r, h in bs for x in (l, r)})
    heap = []
    i = 0
    total = 0
    for j in range(len(xs) - 1):
        x = xs[j]
        while i < len(bs) and bs[i][0] <= x:
            heapq.heappush(heap, (-bs[i][2], bs[i][1]))
            i += 1
        while heap and heap[0][1] <= x:
            heapq.heappop(heap)
        if heap:
            total += -heap[0][0] * (xs[j + 1] - x)
    return total % MOD
''',
    tests=[[[[2, 9, 10], [3, 7, 15], [5, 12, 12], [15, 20, 10], [19, 24, 8]]], [[]], [[[0, 4, 3]]], [[[0, 2, 3], [2, 5, 3]]],
           [[[0, 5, 4], [2, 3, 4]]], [[[1, 3, 2], [1, 3, 5], [1, 3, 1]]], [[[0, 2, 3], [4, 6, 3]]],
           [[[0, 10 ** 9, 10 ** 9]]], [[[0, 10 ** 9, 10 ** 9], [1, 10 ** 9 - 1, 5]]], [[[1, 3, 5], [3, 6, 2]]], [[[1, 6, 2], [3, 4, 9], [3, 8, 4]]]],
)
_r = rnd(9307)
p["tests"].append([[[l, r, _r.randint(1, 10 ** 4)] for l, r in _ivs(_r, 2000, 0, 10 ** 6, 20000)]])
p["tests"].append([[[l, r, _r.randint(1, 10 ** 9)] for l, r in _ivs(_r, 2000, 0, 10 ** 9, 10 ** 8)]])


def b_sil(buildings):
    if not buildings:
        return 0
    lo = min(b[0] for b in buildings)
    hi = max(b[1] for b in buildings)
    return sum(max([h for l, r, h in buildings if l <= x < r], default=0) for x in range(lo, hi)) % MOD


def g_sil(r):
    return [[[l, rr, r.randint(1, 6)] for l, rr in _ivs(r, r.randint(0, 7), 0, 14, 8)]]


def v_sil(tests):
    for t in tests:
        b = t["args"][0]
        assert len(b) <= 50000
        assert all(0 <= l < r <= 10 ** 9 and 1 <= h <= 10 ** 9 for l, r, h in b)
        assert 0 <= t["expected"] < MOD


CHECKS["silhouette-area-of-buildings"] = (b_sil, g_sil, "exact")
VALIDATE["silhouette-area-of-buildings"] = v_sil

p = add(
    id="longest-stretch-k-coverage", title="Longest Stretch Covered at Least K Times", diff="Medium", topic=TOPIC, tier="extra",
    fn="longestStretchCovered", params=[("intervals", "int[][]"), ("k", "int")], ret="int", cmp="exact",
    desc="<p>Each interval <code>[start, end)</code> is half-open and covers every moment <code>t</code> with <code>start &le; t &lt; end</code>.</p><p>Find the longest continuous stretch of time in which <strong>every</strong> moment is covered by at least <code>k</code> intervals, and return its length. Return <code>0</code> if no moment is covered <code>k</code> times.</p><pre>intervals = [[1, 4], [2, 6], [3, 5]], k = 2  -&gt;  3\nintervals = [[0, 3], [3, 6]],         k = 1  -&gt;  6</pre><p>In the first example the coverage is 1, 2, 3, 2, 1 on the unit pieces from time 1 to time 6, so the stretch [2, 5) is covered at least twice. In the second example the two intervals touch and together cover [0, 6) without a hole.</p>",
    constraints=["0 &le; intervals.length &le; 100,000", "intervals[i] = [start, end] with 0 &le; start &lt; end &le; 10<sup>9</sup>", "1 &le; k &le; 100,000"],
    hints=["The coverage count only changes at starts and ends. Between two consecutive event times it is constant.",
           "Sort the distinct event times and compute the coverage of each piece between neighbouring times with a running sum of +1/-1 changes.",
           "Walk through the pieces: if the coverage is at least <code>k</code>, add the piece length to the current run, otherwise reset the run to 0. Pieces are adjacent in time, so consecutive good pieces form one stretch. Track the best run."],
    editorial=["Store the net change of the coverage for every distinct event time and sort the times. The coverage of the piece between times <code>t<sub>i</sub></code> and <code>t<sub>i+1</sub></code> is the sum of all changes at times up to and including <code>t<sub>i</sub></code>.",
               "The pieces tile the range from the first to the last event without gaps, so a run of consecutive pieces with coverage &ge; k is one continuous stretch; two good pieces separated by a bad one are not. A single pass keeps the length of the current run and the best one. O(n log n) time for sorting, O(n) space."],
    time="O(n log n)", space="O(n)",
    solution='''def longestStretchCovered(intervals, k):
    delta = {}
    for s, e in intervals:
        delta[s] = delta.get(s, 0) + 1
        delta[e] = delta.get(e, 0) - 1
    times = sorted(delta)
    cover = 0
    run = 0
    best = 0
    for i in range(len(times) - 1):
        cover += delta[times[i]]
        if cover >= k:
            run += times[i + 1] - times[i]
            if run > best:
                best = run
        else:
            run = 0
    return best
''',
    tests=[[[[1, 4], [2, 6], [3, 5]], 2], [[[0, 3], [3, 6]], 1], [[[1, 4], [2, 6], [3, 5]], 1], [[[1, 4], [2, 6], [3, 5]], 3],
           [[[1, 4], [2, 6], [3, 5]], 4], [[], 1], [[[0, 10 ** 9]], 1], [[[0, 10 ** 9], [0, 10 ** 9]], 2],
           [[[1, 3], [5, 9], [2, 6], [8, 12]], 1], [[[1, 3], [5, 9], [2, 6], [8, 12]], 2], [[[1, 4], [4, 8], [2, 7], [6, 10], [9, 11]], 2],
           [[[0, 2], [1, 3], [3, 5], [4, 6]], 2]],
)
_r = rnd(9308)
_a = _ivs(_r, 2000, 0, 10 ** 6, 3000)
p["tests"].append([_a, max(1, _maxov(_a) // 2)])
_a = _ivs(_r, 2000, 0, 10 ** 9, 3 * 10 ** 6)
p["tests"].append([_a, 2])
p["tests"].append([[[i, i + 2] for i in range(1500)], 2])


def b_stretch(intervals, k):
    if not intervals:
        return 0
    lo = min(s for s, _ in intervals)
    hi = max(e for _, e in intervals)
    best = run = 0
    for t in range(lo, hi):
        if sum(1 for s, e in intervals if s <= t < e) >= k:
            run += 1
            best = max(best, run)
        else:
            run = 0
    return best


def g_stretch(r):
    return [_ivs(r, r.randint(0, 8), 0, 16, 8), r.randint(1, 3)]


def v_stretch(tests):
    for t in tests:
        iv, k = t["args"]
        _check_ivs(iv, 100000, 0, 10 ** 9)
        assert 1 <= k <= 100000
    assert any(t["expected"] == 0 for t in tests) and any(t["expected"] > 0 for t in tests)


CHECKS["longest-stretch-k-coverage"] = (b_stretch, g_stretch, "exact")
VALIDATE["longest-stretch-k-coverage"] = v_stretch

# ---------------------------------------------------------------- HARD

p = add(
    id="skyline-outline-of-buildings", title="Skyline Outline of Buildings", diff="Hard", topic=TOPIC, tier="must",
    fn="getSkyline", params=[("buildings", "int[][]")], ret="int[][]", cmp="exact",
    desc="<p>Rectangular buildings stand on a flat line. Building <code>[left, right, height]</code> occupies the range from <code>left</code> to <code>right</code> (right edge exclusive) and has the given <code>height</code>. Buildings may overlap, nest or touch, and they come in no particular order.</p><p>The <strong>skyline</strong> is the outline of the union of all buildings. Describe it as a list of <em>key points</em> <code>[x, h]</code> sorted by <code>x</code>: <code>x</code> is a position at which the outline height changes, and <code>h</code> is the new height from <code>x</code> onward (up to the next key point). The last key point always has height <code>0</code>. Two consecutive key points never have the same height, and there is at most one key point per <code>x</code>.</p><pre>buildings = [[2, 9, 10], [3, 7, 15], [5, 12, 12], [15, 20, 10], [19, 24, 8]]\nresult    = [[2, 10], [3, 15], [7, 12], [12, 0], [15, 10], [20, 8], [24, 0]]</pre><p>With no buildings the skyline is empty: return <code>[]</code>.</p>",
    constraints=["0 &le; buildings.length &le; 10,000", "buildings[i] = [left, right, height] with 0 &le; left &lt; right &le; 2<sup>31</sup> - 1", "1 &le; height &le; 2<sup>31</sup> - 1"],
    hints=["The outline height can only change at a left or right edge of some building. At such an x you need the tallest building that covers it.",
           "Sweep the sorted distinct edge coordinates. Keep the buildings that have started in a max-heap keyed by height, so the current outline height is the top of the heap.",
           "Remove finished buildings lazily: while the top of the heap has <code>right &le; x</code>, pop it. Compare the resulting height (0 for an empty heap) with the previous outline height and output <code>[x, height]</code> only when it differs."],
    editorial=["Between two neighbouring edge coordinates the outline is flat, so it is enough to evaluate the height at each distinct edge coordinate <code>x</code>, in increasing order. The height at <code>x</code> is the maximum height among buildings with <code>left &le; x &lt; right</code>.",
               "Sort the buildings by left edge and keep a max-heap of <code>(-height, right)</code>. For each x: push all buildings with <code>left &le; x</code>, then pop from the top while <code>right &le; x</code>. Entries that are expired but buried below the top cannot affect the maximum, and they are removed as soon as they surface, so this lazy deletion is correct. The top gives the current height (0 if the heap is empty).",
               "Output <code>[x, height]</code> when the height differs from the previous one. That automatically merges adjacent buildings of equal height, keeps a single key point where one building ends and a taller or shorter one starts at the same x, and ends with a height-0 point. Sorting and heap operations make it O(n log n) time with O(n) space."],
    time="O(n log n)", space="O(n)",
    solution='''import heapq


def getSkyline(buildings):
    bs = sorted(buildings)
    xs = sorted({x for l, r, h in bs for x in (l, r)})
    heap = []
    i = 0
    result = []
    prev = 0
    for x in xs:
        while i < len(bs) and bs[i][0] <= x:
            heapq.heappush(heap, (-bs[i][2], bs[i][1]))
            i += 1
        while heap and heap[0][1] <= x:
            heapq.heappop(heap)
        cur = -heap[0][0] if heap else 0
        if cur != prev:
            result.append([x, cur])
            prev = cur
    return result
''',
    tests=[[[[2, 9, 10], [3, 7, 15], [5, 12, 12], [15, 20, 10], [19, 24, 8]]], [[]], [[[0, 2, 3]]], [[[0, 2, 3], [2, 5, 3]]],
           [[[1, 2, 1], [1, 2, 2], [1, 2, 3]]], [[[0, 5, 4], [2, 3, 4]]], [[[1, 3, 5], [3, 6, 2]]], [[[1, 3, 2], [3, 6, 5]]],
           [[[0, 2, 3], [4, 6, 3]]], [[[0, 2 ** 31 - 1, 2 ** 31 - 1]]], [[[0, 4, 1], [1, 5, 2], [2, 6, 3], [3, 7, 4]]],
           [[[0, 10, 5], [2, 4, 8], [6, 8, 8], [3, 7, 6]]]],
)
_r = rnd(9309)
p["tests"].append([[[l, r, _r.randint(1, 10 ** 4)] for l, r in _ivs(_r, 1200, 0, 10 ** 6, 3000)]])
p["tests"].append([[[l, r, _r.randint(1, 2 ** 31 - 1)] for l, r in _ivs(_r, 1200, 0, 2 ** 31 - 1, 10 ** 8)]])
p["tests"].append([[[i * 3, i * 3 + 5, 1 + (i % 7)] for i in range(1000)]])


def b_sky(buildings):
    if not buildings:
        return []
    lo = min(b[0] for b in buildings)
    hi = max(b[1] for b in buildings)
    out = []
    prev = 0
    for x in range(lo, hi + 1):
        cur = max([h for l, r, h in buildings if l <= x < r], default=0)
        if cur != prev:
            out.append([x, cur])
            prev = cur
    return out


def g_sky(r):
    return [[[l, rr, r.randint(1, 6)] for l, rr in _ivs(r, r.randint(0, 8), 0, 14, 8)]]


def v_sky(tests):
    for t in tests:
        b = t["args"][0]
        assert len(b) <= 10000
        assert all(0 <= l < r <= 2 ** 31 - 1 and 1 <= h <= 2 ** 31 - 1 for l, r, h in b)
        out = t["expected"]
        assert (not b) == (not out)
        if out:
            assert out[-1][1] == 0
        for a, c in zip(out, out[1:]):
            assert a[0] < c[0] and a[1] != c[1]


CHECKS["skyline-outline-of-buildings"] = (b_sky, g_sky, "exact")
VALIDATE["skyline-outline-of-buildings"] = v_sky

p = add(
    id="area-of-union-of-rectangles", title="Area Covered by Overlapping Rectangles", diff="Hard", topic=TOPIC,
    fn="unionArea", params=[("rects", "int[][]")], ret="int", cmp="exact",
    desc="<p>Each rectangle <code>[x1, y1, x2, y2]</code> is axis-aligned, with its bottom-left corner at <code>(x1, y1)</code> and its top-right corner at <code>(x2, y2)</code>, where <code>x1 &lt; x2</code> and <code>y1 &lt; y2</code>. Rectangles may overlap, nest or touch.</p><p>Return the total area of the plane covered by <strong>at least one</strong> rectangle (each point counted once), modulo <code>1,000,000,007</code>.</p><pre>rects = [[0, 0, 2, 2], [1, 1, 3, 3]]  -&gt;  7\nrects = [[0, 1, 3, 2], [1, 0, 2, 3]]  -&gt;  5</pre><p>The first example is two 2x2 squares sharing a 1x1 corner: 4 + 4 - 1 = 7. The second is a plus shape made of a 3x1 and a 1x3 rectangle.</p>",
    constraints=["0 &le; rects.length &le; 1,000", "rects[i] = [x1, y1, x2, y2] with 0 &le; x1 &lt; x2 &le; 10<sup>9</sup> and 0 &le; y1 &lt; y2 &le; 10<sup>9</sup>", "The true area can reach 10<sup>18</sup>, hence the modulo"],
    hints=["Inclusion-exclusion over rectangles explodes. Instead, slice the plane into vertical strips between consecutive x-coordinates of rectangle edges.",
           "In a strip, every rectangle either spans the whole strip or does not touch it. So the area of the strip is its width times the total length of the union of the y-ranges of the active rectangles.",
           "Sweep over x. At <code>x1</code> add the y-range, at <code>x2</code> remove it. Maintain the covered y-length with a segment tree over the compressed y-coordinates: each node stores a cover count and the covered length of its range, and counts are never pushed down."],
    editorial=["Sweep a vertical line from left to right. Between two consecutive event x-coordinates, the set of active rectangles is fixed, so the covered area of that strip equals <code>(x<sub>next</sub> - x) &times; coveredLength</code>, where <code>coveredLength</code> is the length of the union of the active y-intervals.",
               "Compress all y-coordinates; the elementary pieces between neighbouring y-values are the leaves of a segment tree. Each node keeps <code>cnt</code>, the number of active rectangles that cover the node's whole range (and are registered exactly at that node), and <code>cov</code>, the covered length inside the node: if <code>cnt &gt; 0</code> it is the full length of the node's range, otherwise the sum of the children's <code>cov</code> (0 for a leaf). Adding a rectangle increments <code>cnt</code> on O(log n) canonical nodes and removing it decrements the same nodes, so no lazy propagation is needed.",
               "Process the 2n events sorted by x, add <code>cov[root] &times; (x - previousX)</code> to the area before each event batch, then update the tree. O(n log n) time and O(n) space. Take the result modulo 10<sup>9</sup>+7 at the end (exact Python integers cannot overflow)."],
    time="O(n log n)", space="O(n)",
    solution='''def unionArea(rects):
    MOD = 1000000007
    if not rects:
        return 0
    ys = sorted({y for x1, y1, x2, y2 in rects for y in (y1, y2)})
    index = {y: i for i, y in enumerate(ys)}
    m = len(ys) - 1
    cnt = [0] * (4 * m)
    cov = [0] * (4 * m)

    def update(node, lo, hi, a, b, v):
        if b <= lo or hi <= a:
            return
        if a <= lo and hi <= b:
            cnt[node] += v
        else:
            mid = (lo + hi) // 2
            update(2 * node, lo, mid, a, b, v)
            update(2 * node + 1, mid, hi, a, b, v)
        if cnt[node] > 0:
            cov[node] = ys[hi] - ys[lo]
        elif hi - lo == 1:
            cov[node] = 0
        else:
            cov[node] = cov[2 * node] + cov[2 * node + 1]

    events = []
    for x1, y1, x2, y2 in rects:
        events.append((x1, 1, index[y1], index[y2]))
        events.append((x2, -1, index[y1], index[y2]))
    events.sort()
    area = 0
    prev = events[0][0]
    for x, v, a, b in events:
        area += cov[1] * (x - prev)
        prev = x
        update(1, 0, m, a, b, v)
    return area % MOD
''',
    tests=[[[[0, 0, 2, 2], [1, 1, 3, 3]]], [[[0, 1, 3, 2], [1, 0, 2, 3]]], [[]], [[[0, 0, 5, 3]]], [[[0, 0, 2, 2], [2, 0, 4, 2]]],
           [[[0, 0, 4, 4], [1, 1, 2, 2], [0, 0, 4, 4]]], [[[0, 0, 1, 1], [5, 5, 6, 7]]], [[[0, 0, 10 ** 9, 10 ** 9]]],
           [[[0, 0, 10 ** 9, 10 ** 9], [1, 1, 10 ** 9 - 1, 10 ** 9 - 1], [10 ** 9 - 5, 0, 10 ** 9, 3]]],
           [[[0, 0, 3, 1], [0, 1, 3, 2], [0, 2, 3, 3], [1, 0, 2, 3]]], [[[1, 1, 4, 3], [2, 2, 6, 5], [3, 0, 5, 4], [0, 3, 2, 6]]]],
)
_r = rnd(9310)


def _rects(r, n, hi, maxw):
    out = []
    for _ in range(n):
        x = r.randint(0, hi - 1)
        y = r.randint(0, hi - 1)
        out.append([x, y, min(hi, x + r.randint(1, maxw)), min(hi, y + r.randint(1, maxw))])
    return out


p["tests"].append([_rects(_r, 1000, 10 ** 9, 3 * 10 ** 8)])
p["tests"].append([_rects(_r, 1000, 3000, 200)])
p["tests"].append([[[i, i, i + 600, i + 700] for i in range(1000)]])


def b_union(rects):
    cells = set()
    for x1, y1, x2, y2 in rects:
        for x in range(x1, x2):
            for y in range(y1, y2):
                cells.add((x, y))
    return len(cells) % MOD


def g_union(r):
    return [_rects(r, r.randint(0, 6), 10, 6)]


def v_union(tests):
    for t in tests:
        rs = t["args"][0]
        assert len(rs) <= 1000
        assert all(0 <= x1 < x2 <= 10 ** 9 and 0 <= y1 < y2 <= 10 ** 9 for x1, y1, x2, y2 in rs)
        assert 0 <= t["expected"] < MOD


CHECKS["area-of-union-of-rectangles"] = (b_union, g_union, "exact")
VALIDATE["area-of-union-of-rectangles"] = v_union

p = add(
    id="min-removals-to-cap-overlap", title="Fewest Removals to Cap the Overlap", diff="Hard", topic=TOPIC, tier="extra",
    fn="minRemovalsToCap", params=[("intervals", "int[][]"), ("k", "int")], ret="int", cmp="exact",
    desc="<p>Each interval <code>[start, end)</code> is half-open and covers every moment <code>t</code> with <code>start &le; t &lt; end</code>. You want to delete some intervals so that <strong>no moment is covered by more than <code>k</code></strong> of the remaining intervals.</p><p>Return the minimum number of intervals you must delete. (With <code>k = 1</code> this is the classic problem of making the intervals non-overlapping.)</p><pre>intervals = [[1, 3], [2, 4], [3, 5]], k = 1  -&gt;  1\nintervals = [[1, 10], [2, 9], [3, 8], [4, 7]], k = 2  -&gt;  2</pre><p>In the first example removing [2, 4) leaves two touching intervals. In the second example all four intervals share the moment 4, so two of them must go.</p>",
    constraints=["0 &le; intervals.length &le; 100,000", "intervals[i] = [start, end] with 0 &le; start &lt; end &le; 10<sup>9</sup>", "1 &le; k &le; 100,000"],
    hints=["Think of the intervals in order of start time. At the moment a new interval starts, how many kept intervals are still running?",
           "If after adding the new interval more than <code>k</code> kept intervals are running, one of them has to go. Deleting the one that ends <em>latest</em> frees the most future time.",
           "Keep a min-heap of end times to forget finished intervals and a max-heap (with lazy deletion) to find the running interval with the latest end. Count each eviction."],
    editorial=["Sort the intervals by start and sweep. Maintain the set of kept intervals that are still running. When an interval starts, first drop the kept intervals that ended (<code>end &le; start</code>), then add the new one. If the running count now exceeds k, evict the running interval with the largest end (this may be the new interval itself) and count one removal. After the eviction exactly k are running, so one eviction per step suffices.",
               "The greedy choice is optimal by an exchange argument: all running intervals are alive right now, so any of them is equally harmful at this moment; the one that ends latest can only cause more overlap later, so removing it never hurts compared to removing another. This is the same idea as the optimal greedy for k = 1 that keeps intervals with the earliest ends.",
               "Implementation: a min-heap on end times expires finished intervals, and a max-heap on end times finds the eviction candidate; an <code>inactive</code> flag per interval makes deletions lazy in both heaps. Each interval is pushed and popped O(1) times: O(n log n) time, O(n) space."],
    time="O(n log n)", space="O(n)",
    solution='''import heapq


def minRemovalsToCap(intervals, k):
    order = sorted(range(len(intervals)), key=lambda i: intervals[i][0])
    inactive = [False] * len(intervals)
    by_end = []   # min-heap (end, id): expires finished intervals
    by_late = []  # max-heap (-end, id): finds the eviction candidate
    running = 0
    removed = 0
    for i in order:
        s, e = intervals[i]
        while by_end and by_end[0][0] <= s:
            _, j = heapq.heappop(by_end)
            if not inactive[j]:
                inactive[j] = True
                running -= 1
        heapq.heappush(by_end, (e, i))
        heapq.heappush(by_late, (-e, i))
        running += 1
        if running > k:
            while inactive[by_late[0][1]]:
                heapq.heappop(by_late)
            _, j = heapq.heappop(by_late)
            inactive[j] = True
            running -= 1
            removed += 1
    return removed
''',
    tests=[[[[1, 3], [2, 4], [3, 5]], 1], [[[1, 10], [2, 9], [3, 8], [4, 7]], 2], [[], 1], [[[1, 2], [2, 3]], 1], [[[1, 5], [1, 5], [1, 5]], 1],
           [[[1, 5], [1, 5], [1, 5]], 2], [[[1, 5], [1, 5], [1, 5]], 3], [[[1, 100], [2, 3], [4, 5], [6, 7]], 1],
           [[[1, 4], [2, 6], [3, 5], [4, 7], [5, 9], [6, 8]], 2], [[[0, 10 ** 9], [0, 10 ** 9], [0, 1]], 1],
           [[[1, 3], [1, 3], [2, 4], [2, 4], [3, 6], [3, 6]], 2], [[[5, 8], [1, 6], [3, 4], [2, 9], [7, 10], [4, 7]], 2]],
)
_r = rnd(9311)
p["tests"].append([_ivs(_r, 2000, 0, 10 ** 6, 5000), 3])
p["tests"].append([_ivs(_r, 2000, 0, 10 ** 9, 5 * 10 ** 6), 1])
p["tests"].append([_ivs(_r, 2000, 0, 20000, 300), 10])


def b_cap(intervals, k):
    n = len(intervals)
    best = n
    for mask in range(1 << n):
        kept = [intervals[i] for i in range(n) if mask >> i & 1]
        if n - len(kept) >= best:
            continue
        if all(sum(1 for a, b in kept if a <= s < b) <= k for s, _ in kept):
            best = n - len(kept)
    return best


def g_cap(r):
    return [_ivs(r, r.randint(0, 9), 0, 12, 6), r.randint(1, 3)]


def v_cap(tests):
    for t in tests:
        iv, k = t["args"]
        _check_ivs(iv, 100000, 0, 10 ** 9)
        assert 1 <= k <= 100000
        assert 0 <= t["expected"] <= len(iv)
    assert any(t["expected"] > 0 for t in tests) and any(t["expected"] == 0 for t in tests)


CHECKS["min-removals-to-cap-overlap"] = (b_cap, g_cap, "exact")
VALIDATE["min-removals-to-cap-overlap"] = v_cap
