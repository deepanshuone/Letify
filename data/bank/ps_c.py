"""Problems: prefix sums, difference arrays and sweeps (range updates, bookings, coverage counts). See data/lib.py for the registry."""
import heapq
from itertools import combinations, permutations

from lib import add, rnd, CHECKS, VALIDATE, gen_arr  # noqa: F401

TOPIC = "Prefix Sums"
MOD = 1_000_000_007

# ---------------------------------------------------------------- EASY

p = add(
    id="segments-covering-query-points", title="Segments Covering Each Query Point", diff="Easy", topic=TOPIC,
    fn="coverageAtPoints", params=[("segments", "int[][]"), ("points", "int[]")], ret="int[]", cmp="exact",
    desc="<p>Each segment <code>[start, end]</code> covers every integer position from <code>start</code> to <code>end</code> inclusive. For every value <code>x</code> in <code>points</code>, report how many segments cover position <code>x</code>.</p><p>Return the answers in the same order as <code>points</code>.</p><pre>segments = [[1, 4], [3, 6], [4, 4]], points = [4, 0, 5, 7]\nresult = [3, 0, 1, 0]</pre><p>Position 4 lies in all three segments, 0 and 7 lie in none, and 5 lies only in <code>[3, 6]</code>.</p>",
    constraints=["0 &le; segments.length &le; 100,000", "0 &le; points.length &le; 100,000", "0 &le; start &le; end &le; 100,000", "0 &le; points[i] &le; 100,000"],
    hints=["Checking every segment for every point costs O(segments &times; points), which is far too slow at 100,000 each.",
           "The coverage count at position <code>x</code> only changes where a segment starts (+1) or has just ended (-1). Record those changes once, then answer all points from one table.",
           "Keep <code>diff[start] += 1</code> and <code>diff[end + 1] -= 1</code> on an array of size 100,002. A running prefix sum gives <code>cover[x]</code> for every position, and each point is then a lookup."],
    editorial=["This is the difference array applied to counting. Let <code>cover[x]</code> be the number of segments containing <code>x</code>. A segment adds 1 on <code>start..end</code>, which changes the difference <code>cover[x] - cover[x - 1]</code> only at <code>start</code> (+1) and at <code>end + 1</code> (-1).",
               "Fill the difference array in O(segments), prefix-sum it once in O(R) where R = 100,001 is the coordinate range, then answer each point in O(1). Total time O(R + segments + points), space O(R). If coordinates were huge you would compress them or sort the starts and ends and use binary search instead."],
    time="O(R + n + q)", space="O(R)",
    solution='''def coverageAtPoints(segments, points):
    size = 100002
    diff = [0] * (size + 1)
    for start, end in segments:
        diff[start] += 1
        diff[end + 1] -= 1
    cover = [0] * size
    run = 0
    for x in range(size):
        run += diff[x]
        cover[x] = run
    return [cover[x] for x in points]
''',
    tests=[[[[1, 4], [3, 6], [4, 4]], [4, 0, 5, 7]], [[], []], [[], [0, 100000]], [[[0, 0]], [0, 1]], [[[0, 100000]], [0, 50000, 100000]],
           [[[2, 5], [2, 5], [2, 5]], [1, 2, 5, 6]], [[[5, 5], [6, 6], [7, 7]], [5, 6, 7, 8, 4]], [[[1, 3], [2, 4]], []],
           [[[100000, 100000], [0, 100000]], [100000, 99999]], [[[10, 20], [15, 25], [20, 30]], [20, 20, 15, 31]]],
)
_r = rnd(7301)
_u = []
for _ in range(2500):
    _l = _r.randint(0, 100000)
    _u.append([_l, min(100000, _l + _r.randint(0, 60000))])
p["tests"].append([_u, [_r.randint(0, 100000) for _ in range(3000)]])
p["tests"].append([[[0, 100000]] * 2500, [_r.randint(0, 100000) for _ in range(2500)]])
_u = []
for _ in range(1500):
    _l = _r.randint(0, 99)
    _u.append([_l, _r.randint(_l, 99)])
p["tests"].append([_u, list(range(100)) * 20])


def b_cover(segments, points):
    return [sum(1 for s, e in segments if s <= x <= e) for x in points]


def g_cover(r):
    segs = []
    for _ in range(r.randint(0, 6)):
        s = r.randint(0, 9)
        segs.append([s, r.randint(s, 10)])
    return [segs, [r.randint(0, 11) for _ in range(r.randint(0, 6))]]


def v_cover(tests):
    for t in tests:
        segs, pts = t["args"]
        assert len(segs) <= 100000 and len(pts) <= 100000
        assert all(0 <= s <= e <= 100000 for s, e in segs)
        assert all(0 <= x <= 100000 for x in pts)


CHECKS["segments-covering-query-points"] = (b_cover, g_cover, "exact")
VALIDATE["segments-covering-query-points"] = v_cover

p = add(
    id="busiest-day-at-the-lodge", title="Busiest Day at the Lodge", diff="Easy", topic=TOPIC,
    fn="busiestDay", params=[("stays", "int[][]")], ret="int", cmp="exact",
    desc="<p>A mountain lodge keeps a log of guest stays. Each stay is a pair <code>[arrive, depart]</code>: the guest sleeps there on every night from day <code>arrive</code> up to, but <strong>not including</strong>, day <code>depart</code>.</p><p>Return the earliest day on which the largest number of guests is staying at the same time.</p><pre>stays = [[1, 3], [2, 4], [5, 6]]\nresult = 2</pre><p>Here guest 1 stays on days 1-2, guest 2 on days 2-3 and guest 3 on day 5, so day 2 has two guests, the most.</p>",
    constraints=["1 &le; stays.length &le; 100,000", "1 &le; arrive &lt; depart &le; 1,000,000"],
    hints=["Only days on which somebody arrives can be the first day of a new maximum. How can you change the count at those days cheaply?",
           "At <code>arrive</code> the number of guests goes up by one, and at <code>depart</code> it goes down by one (the departure day itself is already free).",
           "Make an array of deltas indexed by day (+1 at arrive, -1 at depart), sweep through the days with a running total, and keep the first day where the total becomes strictly larger than the best so far."],
    editorial=["Turn every stay into two events: +1 on the arrival day and -1 on the departure day. Since the departure day is exclusive, the guest has already left on that day, so applying the -1 at that same day is exactly right.",
               "Sweeping the days in increasing order with a running sum gives the number of guests per day. Updating the answer only when the count is <em>strictly</em> greater than the best so far keeps the earliest day on ties. With days up to 10<sup>6</sup> a plain difference array of that size is fine: O(n + D) time where D is the largest day, O(D) space."],
    time="O(n + D)", space="O(D)",
    solution='''def busiestDay(stays):
    last = max(d for _, d in stays)
    delta = [0] * (last + 2)
    for a, d in stays:
        delta[a] += 1
        delta[d] -= 1
    best = 0
    day = 0
    run = 0
    for x in range(1, last + 1):
        run += delta[x]
        if run > best:
            best = run
            day = x
    return day
''',
    tests=[[[[1, 3], [2, 4], [5, 6]]], [[[1, 2]]], [[[1, 2], [2, 3], [3, 4]]], [[[1, 5], [2, 3], [3, 6], [4, 7]]],
           [[[10, 20], [10, 20], [15, 30]]], [[[1, 1000000]]], [[[5, 8], [1, 4], [2, 6], [7, 9]]],
           [[[3, 4], [1, 4], [2, 4], [4, 5]]], [[[1, 1000000], [999999, 1000000]]]],
)
_r = rnd(7302)
_s = []
for _ in range(2500):
    _a = _r.randint(1, 999999)
    _s.append([_a, _r.randint(_a + 1, min(1000000, _a + 400000))])
p["tests"].append([_s])
_s = []
for _ in range(2500):
    _a = _r.randint(1, 3000)
    _s.append([_a, _r.randint(_a + 1, 3001)])
p["tests"].append([_s])
p["tests"].append([[[i, i + 1] for i in range(1, 3001)]])


def b_busiest(stays):
    best, day = 0, 0
    for x in range(1, max(d for _, d in stays) + 1):
        c = sum(1 for a, d in stays if a <= x < d)
        if c > best:
            best, day = c, x
    return day


def g_busiest(r):
    s = []
    for _ in range(r.randint(1, 7)):
        a = r.randint(1, 9)
        s.append([a, r.randint(a + 1, 10)])
    return [s]


def v_busiest(tests):
    for t in tests:
        s = t["args"][0]
        assert 1 <= len(s) <= 100000
        assert all(1 <= a < d <= 1000000 for a, d in s)
        assert t["expected"] >= 1


CHECKS["busiest-day-at-the-lodge"] = (b_busiest, g_busiest, "exact")
VALIDATE["busiest-day-at-the-lodge"] = v_busiest

p = add(
    id="plots-watered-by-k-sprinklers", title="Plots Watered by at Least K Sprinklers", diff="Easy", topic=TOPIC,
    fn="countWellWatered", params=[("n", "int"), ("sprinklers", "int[][]"), ("k", "int")], ret="int", cmp="exact",
    desc="<p>A garden has <code>n</code> plots in a row, numbered <code>0</code> to <code>n - 1</code>. Each sprinkler is described by <code>[left, right]</code> and waters every plot from <code>left</code> to <code>right</code> inclusive. A plot may be reached by several sprinklers.</p><p>Return how many plots are watered by <strong>at least</strong> <code>k</code> different sprinklers.</p><pre>n = 6, sprinklers = [[0, 2], [1, 4], [3, 5], [2, 3]], k = 2\nresult = 4</pre><p>The coverage counts per plot are <code>[1, 2, 3, 3, 2, 1]</code>, and four plots have a count of 2 or more.</p>",
    constraints=["1 &le; n &le; 100,000", "0 &le; sprinklers.length &le; 100,000", "0 &le; left &le; right &lt; n", "1 &le; k &le; 100,000"],
    hints=["If you could get the coverage count of every plot, the answer would be a simple count of plots with count &ge; k.",
           "Adding 1 to every plot of every sprinkler is too slow in total. Mark only where each sprinkler starts and where it stops.",
           "Use <code>diff[left] += 1</code> and <code>diff[right + 1] -= 1</code>, sweep with a running sum, and count the plots where the running sum is at least <code>k</code>."],
    editorial=["The coverage of plot <code>i</code> is the number of sprinklers whose range contains <code>i</code>. A difference array computes all coverages at once: +1 where a range starts and -1 just after it ends. The prefix sum of this array is the coverage.",
               "A final pass counts the plots with coverage at least <code>k</code>. Total time O(n + m), space O(n). This +1/-1 sweep is the building block of many 'how many things overlap here' problems."],
    time="O(n + m)", space="O(n)",
    solution='''def countWellWatered(n, sprinklers, k):
    diff = [0] * (n + 1)
    for left, right in sprinklers:
        diff[left] += 1
        diff[right + 1] -= 1
    run = 0
    count = 0
    for i in range(n):
        run += diff[i]
        if run >= k:
            count += 1
    return count
''',
    tests=[[6, [[0, 2], [1, 4], [3, 5], [2, 3]], 2], [1, [], 1], [1, [[0, 0]], 1], [5, [[0, 4]], 2], [5, [[0, 4], [0, 4]], 2],
           [8, [[0, 1], [2, 3], [4, 5], [6, 7]], 1], [8, [[0, 3], [2, 5], [4, 7]], 2], [4, [[1, 2], [1, 2], [1, 2]], 3],
           [7, [[0, 6], [3, 3], [3, 3], [2, 4]], 3]],
)
_r = rnd(7303)
_sp = []
for _ in range(2500):
    _l = _r.randint(0, 99999)
    _sp.append([_l, min(99999, _l + _r.randint(0, 40000))])
p["tests"].append([100000, _sp, 400])
_sp = []
for _ in range(2500):
    _l = _r.randint(0, 1999)
    _sp.append([_l, _r.randint(_l, 1999)])
p["tests"].append([2000, _sp, 1200])
p["tests"].append([100000, [[0, 99999]] * 2000, 2000])


def b_watered(n, sprinklers, k):
    cnt = 0
    for i in range(n):
        if sum(1 for l, r in sprinklers if l <= i <= r) >= k:
            cnt += 1
    return cnt


def g_watered(r):
    n = r.randint(1, 8)
    sp = []
    for _ in range(r.randint(0, 6)):
        l = r.randint(0, n - 1)
        sp.append([l, r.randint(l, n - 1)])
    return [n, sp, r.randint(1, 4)]


def v_watered(tests):
    for t in tests:
        n, sp, k = t["args"]
        assert 1 <= n <= 100000 and len(sp) <= 100000 and 1 <= k <= 100000
        assert all(0 <= l <= r < n for l, r in sp)


CHECKS["plots-watered-by-k-sprinklers"] = (b_watered, g_watered, "exact")
VALIDATE["plots-watered-by-k-sprinklers"] = v_watered

# ---------------------------------------------------------------- MEDIUM

p = add(
    id="brightest-position-on-street", title="Brightest Position on the Street", diff="Medium", topic=TOPIC,
    fn="brightestPosition", params=[("lamps", "int[][]")], ret="int", cmp="exact",
    desc="<p>A street is modelled as a number line. Each lamp is a pair <code>[position, radius]</code> and lights every <em>integer</em> point from <code>position - radius</code> to <code>position + radius</code> inclusive.</p><p>The brightness of an integer point is the number of lamps that light it. Return the <strong>smallest</strong> integer point whose brightness is the maximum over the whole street.</p><pre>lamps = [[1, 2], [3, 1]]\nresult = 2</pre><p>The first lamp lights -1..3, the second lights 2..4. Points 2 and 3 both have brightness 2, and the smaller one is 2.</p>",
    constraints=["1 &le; lamps.length &le; 100,000", "-100,000,000 &le; position &le; 100,000,000", "0 &le; radius &le; 100,000,000"],
    hints=["The street is far too long to look at point by point, but only a few points can matter. Which points can be where the brightness first reaches its maximum?",
           "Brightness only goes up at the left end of a lamp's interval and only goes down just after its right end.",
           "Create events <code>(position - radius, +1)</code> and <code>(position + radius + 1, -1)</code>, sort them, sweep with a running total, and remember the first coordinate where the total exceeds the best so far. Apply all events of one coordinate before comparing."],
    editorial=["This is a difference array on a huge coordinate range, so we keep it sparse: each lamp contributes +1 at its left end and -1 one past its right end. Sorting the event coordinates and sweeping gives the brightness on each stretch between consecutive events.",
               "The maximum is first reached at some left end, so it is enough to compare the running total after all events of a coordinate have been applied (departures at coordinate <em>x</em> belong to lamps that no longer light <em>x</em>). Updating the answer only on a strict improvement returns the smallest position. Time O(m log m), space O(m)."],
    time="O(m log m)", space="O(m)",
    solution='''def brightestPosition(lamps):
    delta = {}
    for pos, rad in lamps:
        delta[pos - rad] = delta.get(pos - rad, 0) + 1
        delta[pos + rad + 1] = delta.get(pos + rad + 1, 0) - 1
    best = 0
    answer = 0
    run = 0
    for x in sorted(delta):
        run += delta[x]
        if run > best:
            best = run
            answer = x
    return answer
''',
    tests=[[[[1, 2], [3, 1]]], [[[5, 0]]], [[[-5, 3]]], [[[0, 1], [4, 1]]], [[[0, 2], [2, 0], [4, 2]]],
           [[[-100000000, 100000000], [100000000, 100000000]]], [[[10, 5], [10, 5], [0, 1]]], [[[2, 1], [5, 1], [8, 1], [5, 3]]],
           [[[-3, 0], [-3, 0], [-2, 1], [-4, 1]]]],
)
_r = rnd(7304)
p["tests"].append([[[_r.randint(-100000000, 100000000), _r.randint(0, 60000000)] for _ in range(3000)]])
p["tests"].append([[[_r.randint(-500, 500), _r.randint(0, 30)] for _ in range(3000)]])
p["tests"].append([[[i * 3 - 7000, 1] for i in range(3000)]])


def b_bright(lamps):
    lo = min(p_ - r_ for p_, r_ in lamps)
    hi = max(p_ + r_ for p_, r_ in lamps)
    best, ans = 0, lo
    for x in range(lo, hi + 1):
        c = sum(1 for p_, r_ in lamps if p_ - r_ <= x <= p_ + r_)
        if c > best:
            best, ans = c, x
    return ans


def g_bright(r):
    return [[[r.randint(-6, 6), r.randint(0, 4)] for _ in range(r.randint(1, 6))]]


def v_bright(tests):
    for t in tests:
        lamps = t["args"][0]
        assert 1 <= len(lamps) <= 100000
        assert all(-10**8 <= p_ <= 10**8 and 0 <= r_ <= 10**8 for p_, r_ in lamps)


CHECKS["brightest-position-on-street"] = (b_bright, g_bright, "exact")
VALIDATE["brightest-position-on-street"] = v_bright

p = add(
    id="string-range-shifts", title="String Range Shifts", diff="Medium", topic=TOPIC,
    fn="applyShifts", params=[("s", "string"), ("shifts", "int[][]")], ret="string", cmp="exact",
    desc="<p>You are given a lowercase string <code>s</code> and a list of shifts. Each shift is a triple <code>[left, right, direction]</code>. It moves <em>every</em> letter in positions <code>left..right</code> (inclusive) one step through the alphabet: forward if <code>direction = 1</code> (<code>a</code> becomes <code>b</code>, ..., <code>z</code> becomes <code>a</code>), backward if <code>direction = 0</code> (<code>b</code> becomes <code>a</code>, ..., <code>a</code> becomes <code>z</code>).</p><p>Apply all the shifts and return the final string.</p><pre>s = \"xyz\", shifts = [[0, 1, 1], [1, 2, 1], [0, 2, 0]]\nresult = \"xzz\"</pre><p>The string goes <code>xyz</code> &rarr; <code>yzz</code> &rarr; <code>yaa</code> &rarr; <code>xzz</code>.</p>",
    constraints=["1 &le; s.length &le; 100,000", "s consists of lowercase English letters", "0 &le; shifts.length &le; 100,000", "0 &le; left &le; right &lt; s.length", "direction is 0 or 1"],
    hints=["Shifting letter by letter for each operation is O(n) per shift. Think about what the final letter at one position depends on.",
           "Each position ends up shifted by (number of forward shifts covering it) minus (number of backward shifts covering it), taken modulo 26. The order of shifts does not matter.",
           "Use a difference array: +1 for a forward shift and -1 for a backward one at <code>left</code>, the opposite at <code>right + 1</code>. A prefix sum gives the net shift per position; apply it modulo 26."],
    editorial=["Every shift is a +1 or -1 on a range of positions, and shifts commute, so only the net shift of each position matters. Position <code>i</code> gets net <code>cover_forward(i) - cover_backward(i)</code>, applied to its letter modulo 26.",
               "A difference array records the net effect of all shifts in O(1) each; a single prefix sum recovers the net shift of every position. Be careful with negative sums: reduce with a proper modulo (in Python <code>%</code> already returns a non-negative value). Time O(n + m), space O(n)."],
    time="O(n + m)", space="O(n)",
    solution='''def applyShifts(s, shifts):
    n = len(s)
    diff = [0] * (n + 1)
    for left, right, d in shifts:
        step = 1 if d == 1 else -1
        diff[left] += step
        diff[right + 1] -= step
    out = []
    run = 0
    for i in range(n):
        run += diff[i]
        out.append(chr((ord(s[i]) - 97 + run) % 26 + 97))
    return "".join(out)
''',
    tests=[["xyz", [[0, 1, 1], [1, 2, 1], [0, 2, 0]]], ["a", []], ["a", [[0, 0, 0]]], ["z", [[0, 0, 1]]], ["abc", [[0, 2, 1], [0, 2, 1]]],
           ["hello", [[0, 4, 1]] * 26], ["hello", [[1, 3, 0], [2, 2, 1], [0, 0, 0]]], ["zzzz", [[0, 3, 1], [1, 2, 1]]],
           ["abcdefg", [[0, 6, 0], [0, 6, 0], [3, 6, 1]]]],
)
_r = rnd(7305)
_s = "".join(_r.choice("abcdefghijklmnopqrstuvwxyz") for _ in range(3000))
_sh = []
for _ in range(3000):
    _l = _r.randint(0, 2999)
    _sh.append([_l, _r.randint(_l, 2999), _r.randint(0, 1)])
p["tests"].append([_s, _sh])
p["tests"].append(["a" * 4000, [[0, 3999, 0]] * 3000])
p["tests"].append(["".join(_r.choice("xyz") for _ in range(3000)), [[i, 2999 - i, i % 2] for i in range(1500)]])


def b_shifts(s, shifts):
    a = [ord(c) - 97 for c in s]
    for l, r, d in shifts:
        for i in range(l, r + 1):
            a[i] = (a[i] + (1 if d == 1 else -1)) % 26
    return "".join(chr(x + 97) for x in a)


def g_shifts(r):
    n = r.randint(1, 7)
    s = "".join(r.choice("abxyz") for _ in range(n))
    sh = []
    for _ in range(r.randint(0, 6)):
        l = r.randint(0, n - 1)
        sh.append([l, r.randint(l, n - 1), r.randint(0, 1)])
    return [s, sh]


def v_shifts(tests):
    for t in tests:
        s, sh = t["args"]
        assert 1 <= len(s) <= 100000 and len(sh) <= 100000
        assert s.isalpha() and s.islower() and s.isascii()
        assert all(0 <= l <= r < len(s) and d in (0, 1) for l, r, d in sh)


CHECKS["string-range-shifts"] = (b_shifts, g_shifts, "exact")
VALIDATE["string-range-shifts"] = v_shifts

p = add(
    id="max-sum-by-range-requests", title="Maximum Sum from Range Requests", diff="Medium", topic=TOPIC,
    fn="maxRequestSum", params=[("nums", "int[]"), ("requests", "int[][]")], ret="int", cmp="exact",
    desc="<p>You may rearrange the elements of <code>nums</code> in any order you like. After that, a list of requests is answered: each request <code>[left, right]</code> asks for the sum of the (rearranged) elements at positions <code>left..right</code> inclusive.</p><p>Choose the arrangement that makes the <strong>total of all request answers</strong> as large as possible and return that total modulo <code>1,000,000,007</code>.</p><pre>nums = [1, 2, 3, 4, 5], requests = [[1, 3], [0, 1]]\nresult = 19</pre><p>Position 1 is asked twice, positions 0, 2 and 3 once, position 4 never. Put 5 at position 1, then 4, 3, 2 on the once-asked positions and 1 on position 4: <code>5&times;2 + 4 + 3 + 2 = 19</code>.</p>",
    constraints=["1 &le; nums.length &le; 100,000", "0 &le; nums[i] &le; 100,000", "0 &le; requests.length &le; 100,000", "0 &le; left &le; right &lt; nums.length"],
    hints=["The total equals the sum over positions of (value at position) &times; (number of requests that include the position). What does that say about which value should go where?",
           "By the rearrangement inequality, pair the largest value with the most-requested position, the second largest with the second most-requested one, and so on.",
           "Compute how many requests cover each position with a difference array, sort the coverage counts and the values, multiply them pairwise and add up (take the modulo at the end or along the way)."],
    editorial=["Every request contributes the elements it covers, so position <code>i</code> contributes <code>nums[i] &times; cover(i)</code>, where <code>cover(i)</code> is the number of requests containing <code>i</code>. Only the multiset of coverage counts matters, not where they are.",
               "To maximise a sum of products of two lists, sort both and multiply them in matching order (rearrangement inequality). The coverage counts come from a difference array in O(n + m). Sorting dominates: O(n log n) time, O(n) space. The raw total can reach about 10<sup>15</sup>, hence the modulo."],
    time="O(n log n + m)", space="O(n)",
    solution='''def maxRequestSum(nums, requests):
    n = len(nums)
    diff = [0] * (n + 1)
    for left, right in requests:
        diff[left] += 1
        diff[right + 1] -= 1
    cover = []
    run = 0
    for i in range(n):
        run += diff[i]
        cover.append(run)
    cover.sort()
    vals = sorted(nums)
    total = 0
    for c, v in zip(cover, vals):
        total += c * v
    return total % 1000000007
''',
    tests=[[[1, 2, 3, 4, 5], [[1, 3], [0, 1]]], [[7], []], [[7], [[0, 0]]], [[3, 5, 2], [[0, 2]]], [[0, 0, 0], [[0, 2], [1, 1]]],
           [[5, 1], [[1, 1], [1, 1], [0, 0]]], [[2, 9, 4, 6], [[0, 3], [0, 3], [2, 3]]], [[100000] * 5, [[0, 4]] * 5],
           [[1, 2, 3, 4, 5, 6], [[0, 0], [5, 5], [2, 3], [2, 4]]]],
)
_r = rnd(7306)
p["tests"].append([[_r.randint(0, 100000) for _ in range(3000)], [[a, _r.randint(a, 2999)] for a in (_r.randint(0, 2999) for _ in range(2000))]])
p["tests"].append([[100000] * 3000, [[0, 2999]] * 2000])
p["tests"].append([[_r.randint(0, 100000) for _ in range(3000)], [[a, min(2999, a + _r.randint(0, 30))] for a in (_r.randint(0, 2999) for _ in range(2500))]])


def b_reqsum(nums, requests):
    best = 0
    for perm in permutations(nums):
        t = sum(sum(perm[l:r + 1]) for l, r in requests)
        best = max(best, t)
    return best % 1000000007


def g_reqsum(r):
    n = r.randint(1, 6)
    nums = [r.randint(0, 9) for _ in range(n)]
    rq = []
    for _ in range(r.randint(0, 5)):
        l = r.randint(0, n - 1)
        rq.append([l, r.randint(l, n - 1)])
    return [nums, rq]


def v_reqsum(tests):
    for t in tests:
        nums, rq = t["args"]
        assert 1 <= len(nums) <= 100000 and len(rq) <= 100000
        assert all(0 <= x <= 100000 for x in nums)
        assert all(0 <= l <= r < len(nums) for l, r in rq)


CHECKS["max-sum-by-range-requests"] = (b_reqsum, g_reqsum, "exact")
VALIDATE["max-sum-by-range-requests"] = v_reqsum

p = add(
    id="increment-submatrices-grid", title="Increment Submatrices", diff="Medium", topic=TOPIC,
    fn="applyRectangles", params=[("n", "int"), ("queries", "int[][]")], ret="int[][]", cmp="exact",
    desc="<p>Start with an <code>n &times; n</code> grid of zeros. Each query is <code>[r1, c1, r2, c2]</code>: add 1 to every cell <code>(r, c)</code> with <code>r1 &le; r &le; r2</code> and <code>c1 &le; c &le; c2</code>.</p><p>Apply all queries and return the final grid as an array of rows.</p><pre>n = 3, queries = [[0, 0, 1, 1], [1, 1, 2, 2]]\nresult = [[1, 1, 0],\n          [1, 2, 1],\n          [0, 1, 1]]</pre>",
    constraints=["1 &le; n &le; 500", "0 &le; queries.length &le; 100,000", "0 &le; r1 &le; r2 &lt; n and 0 &le; c1 &le; c2 &lt; n"],
    hints=["Adding 1 to every cell of every rectangle can cost up to 250,000 operations per query. You need O(1) per query.",
           "In one dimension you mark the start and the cell after the end. In two dimensions a rectangle has four corners to mark.",
           "Do <code>d[r1][c1] += 1</code>, <code>d[r1][c2+1] -= 1</code>, <code>d[r2+1][c1] -= 1</code>, <code>d[r2+1][c2+1] += 1</code> on an (n+1)&times;(n+1) grid, then take the 2-D prefix sum: <code>g[r][c] = d[r][c] + g[r-1][c] + g[r][c-1] - g[r-1][c-1]</code>."],
    editorial=["The 2-D difference array is the mirror image of the 2-D prefix sum. Marking +1 at the top-left corner, -1 just right of the top-right corner and just below the bottom-left corner, and +1 at the cell diagonally past the bottom-right corner makes the 2-D prefix sum equal 1 exactly inside the rectangle and 0 outside it.",
               "Because the effects are linear, all queries accumulate in the same difference grid. One pass of 2-D prefix sums over the (n+1)&times;(n+1) grid recovers every cell. Time O(n<sup>2</sup> + q), space O(n<sup>2</sup>). The counts never exceed 100,000."],
    time="O(n^2 + q)", space="O(n^2)",
    solution='''def applyRectangles(n, queries):
    d = [[0] * (n + 2) for _ in range(n + 2)]
    for r1, c1, r2, c2 in queries:
        d[r1][c1] += 1
        d[r1][c2 + 1] -= 1
        d[r2 + 1][c1] -= 1
        d[r2 + 1][c2 + 1] += 1
    g = [[0] * (n + 1) for _ in range(n + 1)]
    out = []
    for r in range(n):
        row = []
        for c in range(n):
            above = g[r - 1][c] if r > 0 else 0
            left = g[r][c - 1] if c > 0 else 0
            diag = g[r - 1][c - 1] if r > 0 and c > 0 else 0
            g[r][c] = d[r][c] + above + left - diag
            row.append(g[r][c])
        out.append(row)
    return out
''',
    tests=[[3, [[0, 0, 1, 1], [1, 1, 2, 2]]], [1, []], [1, [[0, 0, 0, 0]]], [2, [[0, 0, 1, 1], [0, 0, 1, 1]]], [3, []],
           [4, [[0, 0, 3, 3], [1, 1, 2, 2], [2, 2, 2, 2]]], [3, [[0, 2, 2, 2], [2, 0, 2, 2]]], [5, [[1, 0, 1, 4], [0, 3, 4, 3], [0, 0, 0, 0]]],
           [2, [[1, 1, 1, 1]]]],
)
_r = rnd(7307)
_q = []
for _ in range(2500):
    _a, _b = sorted((_r.randint(0, 59), _r.randint(0, 59)))
    _c, _d = sorted((_r.randint(0, 59), _r.randint(0, 59)))
    _q.append([_a, _c, _b, _d])
p["tests"].append([60, _q])
p["tests"].append([60, [[0, 0, 59, 59]] * 2000])
_q = []
for _ in range(500):
    _a = _r.randint(0, 24)
    _c = _r.randint(0, 24)
    _q.append([_a, _c, _r.randint(_a, 24), _r.randint(_c, 24)])
p["tests"].append([25, _q])


def b_rect(n, queries):
    g = [[0] * n for _ in range(n)]
    for r1, c1, r2, c2 in queries:
        for r in range(r1, r2 + 1):
            for c in range(c1, c2 + 1):
                g[r][c] += 1
    return g


def g_rect(r):
    n = r.randint(1, 6)
    qs = []
    for _ in range(r.randint(0, 5)):
        a = r.randint(0, n - 1)
        c = r.randint(0, n - 1)
        qs.append([a, c, r.randint(a, n - 1), r.randint(c, n - 1)])
    return [n, qs]


def v_rect(tests):
    for t in tests:
        n, qs = t["args"]
        assert 1 <= n <= 500 and len(qs) <= 100000
        assert all(0 <= a <= c < n and 0 <= b <= d < n for a, b, c, d in qs)
        assert len(t["expected"]) == n and all(len(row) == n for row in t["expected"])


CHECKS["increment-submatrices-grid"] = (b_rect, g_rect, "exact")
VALIDATE["increment-submatrices-grid"] = v_rect

p = add(
    id="painting-mixed-segments-sums", title="Mixed Paint Segment Sums", diff="Medium", topic=TOPIC,
    fn="mixedSegments", params=[("paints", "int[][]")], ret="int[][]", cmp="exact",
    desc="<p>A long strip is painted with several coats. Each coat is a triple <code>[start, end, color]</code> and covers the half-open stretch <code>[start, end)</code>. Every coat has a different positive color value. Where coats overlap, the colors <em>mix</em>, and the mixed value is the <strong>sum</strong> of the colors of all coats covering that stretch.</p><p>Collect every distinct start and end coordinate and sort them. Each pair of consecutive coordinates <code>a &lt; b</code> forms a piece <code>[a, b)</code>. Return the list <code>[a, b, mixedValue]</code> of all pieces that are covered by at least one coat, in increasing order. Pieces nobody paints are left out.</p><pre>paints = [[1, 6, 2], [4, 9, 5]]\nresult = [[1, 4, 2], [4, 6, 7], [6, 9, 5]]</pre><p>With <code>[[1, 3, 2], [5, 8, 4]]</code> the answer is <code>[[1, 3, 2], [5, 8, 4]]</code>: the piece <code>[3, 5)</code> is unpainted and is skipped.</p>",
    constraints=["1 &le; paints.length &le; 2,000", "1 &le; start &lt; end &le; 100,000,000", "1 &le; color &le; 100,000, and all colors are distinct"],
    hints=["Only coordinates that are a start or an end of some coat can change the mixed value. There are at most 2 &times; paints.length of them.",
           "When you walk from left to right, a coat starting adds its color to the running mix and a coat ending removes it.",
           "Store <code>delta[start] += color</code>, <code>delta[end] -= color</code> and a similar +1/-1 coat counter in a dictionary, sort the coordinates, sweep, and output a piece for each pair of neighbouring coordinates while the coat counter is positive."],
    editorial=["This is a difference array over a huge coordinate range, kept sparse. At each coordinate we add the colors of coats that begin there and subtract the colors of coats that end there; the running sum is the mixed value on the piece that follows.",
               "Since every color is at least 1, a sum above zero would already mean 'covered', but we also keep a coat counter so the logic does not depend on that. Sorting the at most 2n coordinates and sweeping them gives O(n log n) time and O(n) space. The largest possible mix is 2,000 distinct colors &le; 100,000 each, below 2&times;10<sup>8</sup>."],
    time="O(n log n)", space="O(n)",
    solution='''def mixedSegments(paints):
    total = {}
    cnt = {}
    for start, end, color in paints:
        total[start] = total.get(start, 0) + color
        total[end] = total.get(end, 0) - color
        cnt[start] = cnt.get(start, 0) + 1
        cnt[end] = cnt.get(end, 0) - 1
    xs = sorted(total)
    out = []
    mix = 0
    cover = 0
    for i in range(len(xs) - 1):
        mix += total[xs[i]]
        cover += cnt[xs[i]]
        if cover > 0:
            out.append([xs[i], xs[i + 1], mix])
    return out
''',
    tests=[[[[1, 6, 2], [4, 9, 5]]], [[[1, 3, 2], [5, 8, 4]]], [[[1, 4, 5], [4, 7, 7], [1, 7, 9]]], [[[1, 2, 1]]],
           [[[1, 10, 3], [2, 3, 4], [3, 4, 5]]], [[[5, 10, 1], [1, 5, 2], [10, 12, 3]]], [[[1, 100000000, 100000], [50, 60, 99999]]],
           [[[3, 8, 1], [3, 8, 2], [3, 8, 3]]], [[[1, 4, 1], [2, 6, 2], [3, 8, 4], [7, 9, 8]]]],
)
_r = rnd(7308)
_cols = _r.sample(range(1, 100001), 600)
p["tests"].append([[[_a, _r.randint(_a + 1, _a + 300000), _cols[i]] for i, _a in enumerate(_r.randint(1, 5000000) for _ in range(600))]])
_cols = _r.sample(range(1, 100001), 1000)
p["tests"].append([[[_a, _r.randint(_a + 1, 400), _cols[i]] for i, _a in enumerate(_r.randint(1, 399) for _ in range(1000))]])
_cols = _r.sample(range(1, 100001), 1000)
p["tests"].append([[[i * 7 + 1, i * 7 + 20, _cols[i]] for i in range(1000)]])


def b_mixed(paints):
    pts = sorted({x for s, e, c in paints for x in (s, e)})
    out = []
    for a, b in zip(pts, pts[1:]):
        cs = [c for s, e, c in paints if s <= a and b <= e]
        if cs:
            out.append([a, b, sum(cs)])
    return out


def g_mixed(r):
    k = r.randint(1, 5)
    cols = r.sample(range(1, 30), k)
    ps = []
    for c in cols:
        s = r.randint(1, 9)
        ps.append([s, r.randint(s + 1, 10), c])
    return [ps]


def v_mixed(tests):
    for t in tests:
        ps = t["args"][0]
        assert 1 <= len(ps) <= 2000
        assert all(1 <= s < e <= 10**8 and 1 <= c <= 100000 for s, e, c in ps)
        assert len({c for _, _, c in ps}) == len(ps), "colors must be distinct"
        out = t["expected"]
        assert all(a < b and m > 0 for a, b, m in out)


CHECKS["painting-mixed-segments-sums"] = (b_mixed, g_mixed, "exact")
VALIDATE["painting-mixed-segments-sums"] = v_mixed

p = add(
    id="min-queries-to-zero-array", title="Fewest Queries to Zero the Array", diff="Medium", topic=TOPIC, tier="extra",
    fn="minQueriesToZero", params=[("nums", "int[]"), ("queries", "int[][]")], ret="int", cmp="exact",
    desc="<p>You have an array <code>nums</code> of non-negative integers and a list of queries. Query <code>[left, right, cap]</code>, when used, lets you lower <em>each</em> element at positions <code>left..right</code> by any amount from <code>0</code> to <code>cap</code>, chosen independently for every element.</p><p>Queries are used in the given order. Return the smallest <code>k</code> such that after the first <code>k</code> queries the array can be turned into all zeros (exactly zero, never negative). Return <code>0</code> if <code>nums</code> is already all zeros, and <code>-1</code> if even all queries are not enough.</p><pre>nums = [2, 0, 2], queries = [[0, 2, 1], [0, 2, 1], [1, 1, 3]]\nresult = 2</pre><p>After one query every position can lose at most 1, but position 0 holds 2. After two queries every position can lose up to 2, which is enough.</p>",
    constraints=["1 &le; nums.length &le; 100,000", "0 &le; nums[i] &le; 100,000", "0 &le; queries.length &le; 100,000", "0 &le; left &le; right &lt; nums.length, 1 &le; cap &le; 100,000"],
    hints=["Positions are independent: position <code>i</code> can reach zero after the first <code>k</code> queries exactly when the sum of the caps of the queries (among the first k) that cover it is at least <code>nums[i]</code>.",
           "If it works for <code>k</code> queries it also works for <code>k + 1</code>, so the answer can be found by binary search on <code>k</code>.",
           "To test one value of <code>k</code>, build a difference array with <code>+cap</code> at <code>left</code> and <code>-cap</code> at <code>right + 1</code> for the first k queries, prefix-sum it, and check <code>total[i] &ge; nums[i]</code> for every i."],
    editorial=["Each query offers a 'budget' of at most <code>cap</code> to every position in its range, and a position needs the budget to add up to at least its value (any smaller amount can be used by choosing fewer decrements). So feasibility for a fixed prefix of queries is a pure coverage-sum check, done in O(n + k) with a difference array.",
               "Adding more queries never hurts, so feasibility is monotone in <code>k</code>, which allows binary search over <code>0..q</code>. If even <code>k = q</code> fails, return -1. Total time O((n + q) log q), space O(n)."],
    time="O((n + q) log q)", space="O(n)",
    solution='''def minQueriesToZero(nums, queries):
    n = len(nums)

    def ok(k):
        diff = [0] * (n + 1)
        for left, right, cap in queries[:k]:
            diff[left] += cap
            diff[right + 1] -= cap
        run = 0
        for i in range(n):
            run += diff[i]
            if run < nums[i]:
                return False
        return True

    if not ok(len(queries)):
        return -1
    lo, hi = 0, len(queries)
    while lo < hi:
        mid = (lo + hi) // 2
        if ok(mid):
            hi = mid
        else:
            lo = mid + 1
    return lo
''',
    tests=[[[2, 0, 2], [[0, 2, 1], [0, 2, 1], [1, 1, 3]]], [[0, 0], []], [[1], []], [[5], [[0, 0, 5]]], [[5], [[0, 0, 2], [0, 0, 2]]],
           [[4, 3, 2, 1, 4], [[1, 3, 2], [0, 2, 1], [0, 4, 1], [3, 4, 3]]], [[3, 3], [[0, 0, 3], [1, 1, 1], [1, 1, 1], [1, 1, 5]]],
           [[1, 2, 3], [[0, 2, 1], [1, 2, 1], [2, 2, 1]]], [[7, 6, 8], [[0, 2, 4], [0, 1, 4]]], [[0], [[0, 0, 4]]]],
)
_r = rnd(7309)
_nums = [_r.randint(0, 3000) for _ in range(3000)]
_qs = []
for _ in range(2000):
    _l = _r.randint(0, 2999)
    _qs.append([_l, min(2999, _l + _r.randint(0, 400)), _r.randint(1, 300)])
p["tests"].append([_nums, _qs])
_qs = []
for _ in range(2000):
    _l = _r.randint(0, 2999)
    _qs.append([_l, _r.randint(_l, 2999), _r.randint(1, 20)])
p["tests"].append([[_r.randint(0, 60) for _ in range(3000)], _qs])
p["tests"].append([[100000] * 3000, [[0, 2999, 1]] * 2000])


def b_minq(nums, queries):
    n = len(nums)
    for k in range(len(queries) + 1):
        cap = [0] * n
        for l, r, c in queries[:k]:
            for i in range(l, r + 1):
                cap[i] += c
        if all(cap[i] >= nums[i] for i in range(n)):
            return k
    return -1


def g_minq(r):
    n = r.randint(1, 6)
    nums = [r.randint(0, 6) for _ in range(n)]
    qs = []
    for _ in range(r.randint(0, 6)):
        l = r.randint(0, n - 1)
        qs.append([l, r.randint(l, n - 1), r.randint(1, 4)])
    return [nums, qs]


def v_minq(tests):
    for t in tests:
        nums, qs = t["args"]
        assert 1 <= len(nums) <= 100000 and len(qs) <= 100000
        assert all(0 <= x <= 100000 for x in nums)
        assert all(0 <= l <= r < len(nums) and 1 <= c <= 100000 for l, r, c in qs)


CHECKS["min-queries-to-zero-array"] = (b_minq, g_minq, "exact")
VALIDATE["min-queries-to-zero-array"] = v_minq

# ---------------------------------------------------------------- HARD

p = add(
    id="arithmetic-progression-range-updates", title="Arithmetic Progression Range Updates", diff="Hard", topic=TOPIC,
    fn="applyProgressions", params=[("n", "int"), ("ops", "int[][]")], ret="int[]", cmp="exact",
    desc="<p>Start with an array of <code>n</code> zeros. Each operation is <code>[left, right, a, d]</code>: add the arithmetic progression <code>a, a + d, a + 2d, ...</code> to positions <code>left, left + 1, ..., right</code>. That is, position <code>i</code> in the range receives <code>a + d &times; (i - left)</code>. The values <code>a</code> and <code>d</code> may be negative.</p><p>Apply all operations and return the final array, each element reduced modulo <code>1,000,000,007</code> to a value between <code>0</code> and <code>1,000,000,006</code>.</p><pre>n = 5, ops = [[1, 3, 10, 5], [0, 4, 1, 1]]\nresult = [1, 12, 18, 24, 5]</pre><p>The first operation adds 10, 15, 20 to positions 1-3; the second adds 1, 2, 3, 4, 5 to positions 0-4.</p>",
    constraints=["1 &le; n &le; 100,000", "0 &le; ops.length &le; 100,000", "0 &le; left &le; right &lt; n", "-1,000,000 &le; a, d &le; 1,000,000"],
    hints=["A plain difference array handles 'add the same number to a range'. Here the added amount changes linearly. What happens if you take the difference array <em>of the difference</em>?",
           "The added sequence <code>g</code> (zero outside the range) has first differences: <code>a</code> at <code>left</code>, then <code>d</code> at each of <code>left+1..right</code>, then <code>-(a + d&times;(right-left))</code> at <code>right+1</code>.",
           "Keep two difference arrays: <code>H</code> for the single spikes (<code>H[left] += a</code>, <code>H[right+1] -= a + d*(right-left)</code>) and <code>E</code> for the constant-d stretch (<code>E[left+1] += d</code>, <code>E[right+1] -= d</code>). The step array is <code>H</code> plus the prefix sum of <code>E</code>, and the result is the prefix sum of the step array."],
    editorial=["Applying difference arrays twice handles linear updates. Let <code>g</code> be what one operation adds (a linear ramp inside the range, zero outside). Its first difference <code>h[i] = g[i] - g[i-1]</code> equals <code>a</code> at <code>left</code>, <code>d</code> on <code>left+1..right</code> and a closing drop of <code>-(a + d&times;(right-left))</code> at <code>right+1</code>.",
               "The constant-<code>d</code> stretch is itself a range-add, which is a +<code>d</code>/-<code>d</code> pair in a second difference array. (When <code>left = right</code> the pair lands on the same cell and cancels, which is correct.) After all operations: prefix-sum the second array, add the spike array to get <code>h</code>, and prefix-sum once more to get the answer. All arithmetic is done modulo 1,000,000,007. Time O(n + m), space O(n).",
               "In general, adding a polynomial of degree k over a range needs k + 1 layers of difference arrays and k + 1 prefix-sum passes."],
    time="O(n + m)", space="O(n)",
    solution='''def applyProgressions(n, ops):
    MOD = 1000000007
    spike = [0] * (n + 2)
    slope = [0] * (n + 2)
    for left, right, a, d in ops:
        spike[left] += a
        spike[right + 1] -= a + d * (right - left)
        slope[left + 1] += d
        slope[right + 1] -= d
    out = []
    s = 0
    h = 0
    cur = 0
    for i in range(n):
        s = (s + slope[i]) % MOD
        h = (spike[i] + s) % MOD
        cur = (cur + h) % MOD
        out.append(cur)
    return out
''',
    tests=[[5, [[1, 3, 10, 5], [0, 4, 1, 1]]], [1, []], [1, [[0, 0, 7, 100]]], [4, [[0, 3, 1, 1]]], [4, [[0, 3, 0, 0]]],
           [5, [[0, 4, 4, -1]]], [5, [[2, 2, -3, 5], [2, 2, 3, -5]]], [6, [[0, 5, 1000000, 1000000], [1, 4, -1000000, -1000000]]],
           [3, [[0, 2, 1, 1]] * 4], [8, [[0, 7, 1, 0], [3, 7, 0, 2], [1, 2, -5, 3]]]],
)
_r = rnd(7310)
_ops = []
for _ in range(1000):
    _l = _r.randint(0, 2999)
    _ops.append([_l, _r.randint(_l, 2999), _r.randint(-1000000, 1000000), _r.randint(-1000000, 1000000)])
p["tests"].append([3000, _ops])
p["tests"].append([3000, [[0, 2999, 1000000, 1000000]] * 1200])
_ops = []
for _ in range(700):
    _l = _r.randint(0, 299)
    _ops.append([_l, _r.randint(_l, 299), _r.randint(-50, 50), _r.randint(-50, 50)])
p["tests"].append([300, _ops])


def b_ap(n, ops):
    a = [0] * n
    for l, r, s, d in ops:
        for i in range(l, r + 1):
            a[i] += s + d * (i - l)
    return [x % 1000000007 for x in a]


def g_ap(r):
    n = r.randint(1, 8)
    ops = []
    for _ in range(r.randint(0, 5)):
        l = r.randint(0, n - 1)
        ops.append([l, r.randint(l, n - 1), r.randint(-6, 6), r.randint(-4, 4)])
    return [n, ops]


def v_ap(tests):
    for t in tests:
        n, ops = t["args"]
        assert 1 <= n <= 100000 and len(ops) <= 100000
        assert all(0 <= l <= r < n and -10**6 <= a <= 10**6 and -10**6 <= d <= 10**6 for l, r, a, d in ops)
        assert all(0 <= x < 1000000007 for x in t["expected"])


CHECKS["arithmetic-progression-range-updates"] = (b_ap, g_ap, "exact")
VALIDATE["arithmetic-progression-range-updates"] = v_ap

p = add(
    id="max-removable-range-queries", title="Maximum Removable Range Queries", diff="Hard", topic=TOPIC, tier="extra",
    fn="maxRemovable", params=[("nums", "int[]"), ("queries", "int[][]")], ret="int", cmp="exact",
    desc="<p>You are given an array <code>nums</code> of non-negative integers and a list of queries. Query <code>[left, right]</code>, when kept, may lower <em>each</em> element at positions <code>left..right</code> by <strong>at most 1</strong>, chosen independently for every element.</p><p>You may delete some queries. Return the maximum number of queries you can delete such that the remaining ones can still turn <code>nums</code> into all zeros (exactly zero). If even keeping <em>all</em> queries cannot do it, return <code>-1</code>.</p><pre>nums = [2, 0, 2], queries = [[0, 2], [0, 2], [0, 0], [2, 2]]\nresult = 2</pre><p>Positions 0 and 2 each need two covering queries; the first two queries cover both, so the last two can be deleted.</p>",
    constraints=["1 &le; nums.length &le; 100,000", "0 &le; nums[i] &le; 100,000", "1 &le; queries.length &le; 100,000", "0 &le; left &le; right &lt; nums.length"],
    hints=["Position <code>i</code> can become zero exactly when at least <code>nums[i]</code> of the kept queries cover it. So you want a smallest set of queries such that every position is covered enough times.",
           "Sweep positions from left to right. When position <code>i</code> does not have enough active queries yet, you must pick more queries among those that start at or before <code>i</code> and have not ended before it.",
           "Among the candidates, picking the one with the <em>farthest right end</em> is never worse (greedy). Use a max-heap of right ends for queries that have started, and a difference array to track how many chosen queries are active. If you run out of candidates (or the best one ends before <code>i</code>), the answer is -1."],
    editorial=["Minimising kept queries is the same as maximising deletions. For one position the choice among covering queries only matters for the positions to its right, and a query with a farther right end covers a superset of the future positions of any query with a nearer end (all candidates already cover the current position). That makes the greedy 'pick the longest-reaching candidate' optimal by an exchange argument.",
               "Implementation: sort queries by left end. Walk <code>i</code> from 0 to n - 1; push the right ends of queries with <code>left = i</code> onto a max-heap; maintain <code>active</code> = number of chosen queries covering <code>i</code> using a difference array (chosen query with end <code>r</code> adds +1 now and -1 at <code>r + 1</code>). While <code>active &lt; nums[i]</code>, pop the largest right end; if the heap is empty or that end is less than <code>i</code> return -1; otherwise choose it. At the end the answer is <code>len(queries) - chosen</code>.",
               "Each query enters and leaves the heap once: O((n + q) log q) time, O(n + q) space."],
    time="O((n + q) log q)", space="O(n + q)",
    solution='''import heapq


def maxRemovable(nums, queries):
    n = len(nums)
    starts = [[] for _ in range(n)]
    for left, right in queries:
        starts[left].append(right)
    heap = []
    expire = [0] * (n + 1)
    active = 0
    chosen = 0
    for i in range(n):
        active -= expire[i]
        for r in starts[i]:
            heapq.heappush(heap, -r)
        while active < nums[i]:
            if not heap or -heap[0] < i:
                return -1
            r = -heapq.heappop(heap)
            chosen += 1
            active += 1
            expire[r + 1] += 1
    return len(queries) - chosen
''',
    tests=[[[2, 0, 2], [[0, 2], [0, 2], [0, 0], [2, 2]]], [[0], [[0, 0]]], [[1], [[0, 0]]], [[2], [[0, 0]]], [[0, 0, 0], [[0, 2], [1, 1]]],
           [[1, 1, 1], [[0, 0], [1, 1], [2, 2], [0, 2]]], [[3, 3, 3], [[0, 2], [0, 2], [0, 2], [0, 2]]], [[1, 0, 1], [[0, 1], [1, 2]]],
           [[1, 2, 1], [[0, 1], [1, 2], [0, 2], [1, 1]]], [[2, 2, 0, 3], [[0, 3], [0, 1], [2, 3], [1, 3], [3, 3]]]],
)
_r = rnd(7311)
_nums = [_r.randint(0, 6) for _ in range(3000)]
_qs = []
for _ in range(3500):
    _l = _r.randint(0, 2999)
    _qs.append([_l, min(2999, _l + _r.randint(0, 120))])
p["tests"].append([_nums, _qs])
_nums = [_r.randint(0, 3) for _ in range(4000)]
_qs = []
for _ in range(3000):
    _l = _r.randint(0, 3999)
    _qs.append([_l, _r.randint(_l, 3999)])
p["tests"].append([_nums, _qs])
p["tests"].append([[1] * 4000, [[i, i] for i in range(4000)] + [[0, 3999]] * 100])


def b_removable(nums, queries):
    q = len(queries)
    n = len(nums)
    for keep in range(0, q + 1):
        for comb in combinations(range(q), keep):
            cov = [0] * n
            for j in comb:
                l, r = queries[j]
                for i in range(l, r + 1):
                    cov[i] += 1
            if all(cov[i] >= nums[i] for i in range(n)):
                return q - keep
    return -1


def g_removable(r):
    n = r.randint(1, 6)
    nums = [r.randint(0, 3) for _ in range(n)]
    qs = []
    for _ in range(r.randint(1, 8)):
        l = r.randint(0, n - 1)
        qs.append([l, r.randint(l, n - 1)])
    return [nums, qs]


def v_removable(tests):
    for t in tests:
        nums, qs = t["args"]
        assert 1 <= len(nums) <= 100000 and 1 <= len(qs) <= 100000
        assert all(0 <= x <= 100000 for x in nums)
        assert all(0 <= l <= r < len(nums) for l, r in qs)
        assert -1 <= t["expected"] <= len(qs)


CHECKS["max-removable-range-queries"] = (b_removable, g_removable, "exact")
VALIDATE["max-removable-range-queries"] = v_removable
