"""Problems: heap / priority queue, merging and scheduling. See data/lib.py for the registry."""
import heapq

from lib import add, rnd, CHECKS, VALIDATE, gen_arr  # noqa: F401

INT_MIN, INT_MAX = -(2 ** 31), 2 ** 31 - 1
B = 10 ** 9
MOD = 10 ** 9 + 7


# ================================================================ EASY

# ---------------------------------------------------------------- merge sorted rows distinct
p = add(
    id="merge-sorted-rows-distinct", title="Merge Sorted Rows Without Duplicates", diff="Easy", topic="Heap",
    fn="mergeDistinct", params=[("rows", "int[][]")], ret="int[]", cmp="exact",
    desc="<p>Each row of <code>rows</code> is sorted in non-decreasing order (a row may be empty, and a value may repeat inside a row). Merge all rows into a single array that is sorted in strictly increasing order, so that every value that occurs anywhere in the input appears exactly once.</p><pre>rows = [[1, 4, 4, 9], [2, 4, 8], [], [1, 9]]\nanswer = [1, 2, 4, 8, 9]</pre><p>If every row is empty the answer is the empty array.</p>",
    constraints=["1 &le; rows.length &le; 100", "The total number of values is at most 5,000", "-10<sup>9</sup> &le; value &le; 10<sup>9</sup>", "Every row is sorted in non-decreasing order"],
    hints=["Putting everything in one array and sorting works. The point of this exercise is to use the fact that every row is already sorted.",
           "The smallest value not yet used is always at the front of one of the rows. You only ever need to compare the current front of each row.",
           "Keep a min-heap of <code>(value, row, position)</code> for the front of each non-empty row. Pop the smallest, append it unless it equals the last appended value, then push the next value of the same row."],
    editorial=["This is the classic k-way merge. A min-heap holds at most one entry per row: the first value of that row which has not been consumed yet. Popping the heap yields values in globally sorted order; after each pop the next value of the same row is pushed.",
               "Because the output is sorted, duplicates arrive next to each other, so removing them only needs a comparison with the last value written. Each of the N values is pushed and popped once, and the heap never holds more than k entries, so the time is O(N log k) with O(k) extra space besides the output.",
               "Flattening and calling <code>sorted(set(...))</code> is O(N log N) and fine in practice, but it ignores the sortedness of the input; the heap version is what interviewers expect, and it also works when the rows are streams that cannot be loaded at once."],
    time="O(N log k)", space="O(k)",
    solution='''import heapq


def mergeDistinct(rows):
    h = [(r[0], i, 0) for i, r in enumerate(rows) if r]
    heapq.heapify(h)
    out = []
    while h:
        v, i, j = heapq.heappop(h)
        if not out or out[-1] != v:
            out.append(v)
        if j + 1 < len(rows[i]):
            heapq.heappush(h, (rows[i][j + 1], i, j + 1))
    return out
''',
    tests=[[[[1, 4, 4, 9], [2, 4, 8], [], [1, 9]]], [[[]]], [[[], [], []]], [[[5]]], [[[1, 1, 1], [1, 1]]],
           [[[-3, -1], [-2, 0], [-3, 0]]], [[[1, 2, 3], [], [4, 5]]], [[[B], [-B], [0]]], [[[1, 3, 5], [2, 4, 6]]],
           [[[7, 7, 7, 7]]], [[[2, 2], [2], [2, 2, 2]]]],
)
_r = rnd(9201)


def _sorted_rows(r, k, per, lo, hi):
    return [sorted(r.randint(lo, hi) for _ in range(per)) for _ in range(k)]


p["tests"].append([_sorted_rows(_r, 50, 100, -50, 50)])
p["tests"].append([_sorted_rows(_r, 3, 1600, -B, B)])
_rows = _sorted_rows(_r, 100, 50, -3000, 3000)
_rows[3] = []
_rows[40] = []
p["tests"].append([_rows])


def b_mdist(rows):
    return sorted({v for r in rows for v in r})


def g_mdist(r):
    return [sorted(r.randint(-4, 4) for _ in range(r.randint(0, 5))) for _ in range(r.randint(1, 5))]


def v_mdist(tests):
    for t in tests:
        rows = t["args"][0]
        assert 1 <= len(rows) <= 100
        assert sum(len(x) for x in rows) <= 5000
        for x in rows:
            assert x == sorted(x) and all(-B <= v <= B for v in x)
        e = t["expected"]
        assert all(e[i] < e[i + 1] for i in range(len(e) - 1))


CHECKS["merge-sorted-rows-distinct"] = (b_mdist, lambda r: [g_mdist(r)], "exact")
VALIDATE["merge-sorted-rows-distinct"] = v_mdist

# ---------------------------------------------------------------- seat reservation manager
p = add(
    id="seat-reservation-manager", title="Seat Reservation Manager", diff="Easy", topic="Heap",
    fn="seatManager", params=[("n", "int"), ("ops", "int[][]")], ret="int[]", cmp="exact",
    desc="<p>A theatre has seats numbered <code>1..n</code>, all free at the start. You receive a list of operations <code>ops</code>, applied in order:</p><ul><li><code>[0, 0]</code> &mdash; <strong>reserve</strong>: take the free seat with the smallest number and record that number.</li><li><code>[1, x]</code> &mdash; <strong>release</strong> seat <code>x</code>, which is currently reserved, so that it becomes free again.</li></ul><p>Return the seat numbers recorded by the reserve operations, in the order the operations occur.</p><pre>n = 5\nops = [[0,0],[0,0],[1,2],[0,0],[0,0],[0,0]]\nreserve -> 1, reserve -> 2, release 2,\nreserve -> 2, reserve -> 3, reserve -> 4\nanswer = [1, 2, 2, 3, 4]</pre>",
    constraints=["1 &le; n &le; 100,000", "1 &le; ops.length &le; 10,000 and at least one operation is a reserve", "A reserve is only issued when at least one seat is free", "A release is only issued for a seat that is currently reserved"],
    hints=["Scanning the seats from 1 upwards for the first free one is correct but can cost O(n) per reserve.",
           "Seats that were never reserved form a block <code>next..n</code>; only released seats can be smaller than <code>next</code>. So the answer is either <code>next</code> or a released seat.",
           "Keep an integer <code>next</code> and a min-heap of released seats. Reserve: pop the heap if it is not empty, otherwise use <code>next</code> and increase it. Release: push the seat onto the heap."],
    editorial=["Seats are handed out from the smallest number, so every seat below the counter <code>next</code> has been handed out at some point, and the seats from <code>next</code> on have never been used. The free seats below <code>next</code> are exactly the released ones.",
               "A min-heap of released seats gives the smallest of them in O(log n). If it is empty, <code>next</code> is the smallest free seat. A release is a single heap push. Total time is O(m log m) for m operations and the extra memory is O(m).",
               "You do not need to put all n seats into a heap at the start (that would cost O(n) before the first operation); the counter plus a heap of released seats does the same job lazily."],
    time="O(m log m)", space="O(m)",
    solution='''import heapq


def seatManager(n, ops):
    nxt = 1
    freed = []
    out = []
    for t, x in ops:
        if t == 0:
            if freed:
                out.append(heapq.heappop(freed))
            else:
                out.append(nxt)
                nxt += 1
        else:
            heapq.heappush(freed, x)
    return out
''',
    tests=[[5, [[0, 0], [0, 0], [1, 2], [0, 0], [0, 0], [0, 0]]], [1, [[0, 0], [1, 1], [0, 0]]], [3, [[0, 0], [0, 0], [0, 0]]],
           [3, [[0, 0], [0, 0], [0, 0], [1, 3], [1, 1], [1, 2], [0, 0], [0, 0], [0, 0]]], [4, [[0, 0], [0, 0], [1, 1], [1, 2], [0, 0]]],
           [2, [[0, 0], [1, 1], [0, 0], [1, 1], [0, 0], [0, 0]]], [100000, [[0, 0]]],
           [6, [[0, 0], [0, 0], [0, 0], [0, 0], [1, 4], [1, 2], [0, 0], [1, 1], [0, 0], [0, 0], [0, 0]]]],
)


def _seat_ops(r, n, m, p_res):
    reserved = []
    nxt = 1
    ops = []
    free = set()
    # simulate with explicit bookkeeping only to keep operations valid
    for _ in range(m):
        if reserved and (len(reserved) >= n or r.random() > p_res):
            k = r.randrange(len(reserved))
            reserved[k], reserved[-1] = reserved[-1], reserved[k]
            x = reserved.pop()
            ops.append([1, x])
            free.add(x)
        else:
            if free:
                s = min(free)
                free.discard(s)
            else:
                s = nxt
                nxt += 1
            reserved.append(s)
            ops.append([0, 0])
    return ops


_r = rnd(9202)
p["tests"].append([100000, _seat_ops(_r, 100000, 3000, 0.6)])
p["tests"].append([3000, [[0, 0]] * 2500 + [[1, x] for x in _r.sample(range(1, 2501), 1500)] + [[0, 0]] * 1500])
p["tests"].append([40, _seat_ops(_r, 40, 3000, 0.5)])


def b_seat(n, ops):
    taken = [False] * (n + 2)
    out = []
    for t, x in ops:
        if t == 0:
            s = 1
            while taken[s]:
                s += 1
            taken[s] = True
            out.append(s)
        else:
            taken[x] = False
    return out


def g_seat(r):
    n = r.randint(1, 6)
    return [n, _seat_ops(r, n, r.randint(1, 12), 0.6)]


def v_seat(tests):
    for t in tests:
        n, ops = t["args"]
        assert 1 <= n <= 100000 and 1 <= len(ops) <= 10000
        taken = set()
        res = 0
        for typ, x in ops:
            if typ == 0:
                assert x == 0 and len(taken) < n
                res += 1
                taken.add(min(set(range(1, len(taken) + 2)) - taken))
            else:
                assert typ == 1 and x in taken
                taken.discard(x)
        assert res >= 1 and len(t["expected"]) == res


CHECKS["seat-reservation-manager"] = (b_seat, g_seat, "exact")
VALIDATE["seat-reservation-manager"] = v_seat

# ---------------------------------------------------------------- checkout lanes total wait
p = add(
    id="checkout-lanes-total-wait", title="Checkout Lanes Total Waiting Time", diff="Easy", topic="Heap", tier="extra",
    fn="totalWait", params=[("lanes", "int"), ("customers", "int[][]")], ret="int", cmp="exact",
    desc="<p>A shop has <code>lanes</code> checkout lanes. Customer <code>i</code> is given as <code>customers[i] = [arrival, service]</code>: they arrive at time <code>arrival</code> and need <code>service</code> time units at a lane. The array is sorted by arrival time and customers are served strictly in this order.</p><p>Each customer goes to the lane that becomes free the earliest (a lane that is already idle counts as free). If that lane is still busy, the customer waits until it is free; service starts at <code>max(arrival, time the lane becomes free)</code>. A customer's <em>waiting time</em> is the start of service minus the arrival. Return the sum of the waiting times of all customers.</p><pre>lanes = 2, customers = [[0,5],[1,3],[2,4],[3,2]]\nc0: lane A, starts 0 (wait 0), lane A busy until 5\nc1: lane B, starts 1 (wait 0), lane B busy until 4\nc2: lane B frees first (4), starts 4 (wait 2), busy until 8\nc3: lane A frees first (5), starts 5 (wait 2)\nanswer = 4</pre>",
    constraints=["1 &le; lanes &le; 1,000", "1 &le; customers.length &le; 5,000", "0 &le; arrival &le; 10<sup>6</sup>, arrivals are in non-decreasing order", "1 &le; service &le; 100"],
    hints=["Simulate the customers one by one in the given order. What do you need to know about the lanes when a customer arrives?",
           "Only the moment each lane becomes free matters, and the customer always takes the lane that becomes free first.",
           "Keep a min-heap with one entry per lane holding its free time (all zeros at the start). For each customer pop the smallest free time <code>f</code>, start at <code>max(arrival, f)</code>, add <code>start - arrival</code> to the answer and push <code>start + service</code>."],
    editorial=["The lane identity never matters, only the set of free times. The customer picks the smallest free time, so a min-heap of the free times is exactly the right structure: pop the earliest, compute the start, push the new free time.",
               "Because a lane that is free earlier than the arrival can serve the customer immediately, the start time is <code>max(arrival, f)</code> and the waiting time is never negative. Each customer costs two heap operations on a heap of size <code>lanes</code>, so the total is O(n log lanes) time and O(lanes) space.",
               "The total can reach about 1.25 &times; 10<sup>9</sup> (5,000 customers of length 100 on one lane, all arriving at time 0), which is why the limits are chosen so that the sum still fits in a 32-bit integer."],
    time="O(n log lanes)", space="O(lanes)",
    solution='''import heapq


def totalWait(lanes, customers):
    free = [0] * lanes
    total = 0
    for arrival, service in customers:
        f = heapq.heappop(free)
        start = max(arrival, f)
        total += start - arrival
        heapq.heappush(free, start + service)
    return total
''',
    tests=[[2, [[0, 5], [1, 3], [2, 4], [3, 2]]], [1, [[0, 3]]], [1, [[0, 3], [0, 3], [0, 3]]], [3, [[0, 3], [0, 3], [0, 3]]],
           [2, [[0, 1], [10, 1], [20, 1]]], [1, [[0, 5], [5, 5], [10, 5]]], [1, [[0, 5], [4, 5], [5, 1]]],
           [1000, [[0, 100], [0, 100]]], [2, [[1, 10], [2, 1], [3, 1], [4, 1], [5, 1], [6, 1]]]],
)
_r = rnd(9203)
p["tests"].append([1, [[0, 100]] * 5000])
_arr = sorted(_r.randint(0, 3000) for _ in range(2500))
p["tests"].append([30, [[a, _r.randint(1, 100)] for a in _arr]])
_arr = sorted(_r.randint(0, 10 ** 6) for _ in range(2500))
p["tests"].append([1000, [[a, _r.randint(1, 100)] for a in _arr]])


def b_wait(lanes, customers):
    free = [0] * lanes
    total = 0
    for a, s in customers:
        best = 0
        for i in range(1, lanes):
            if free[i] < free[best]:
                best = i
        start = max(a, free[best])
        total += start - a
        free[best] = start + s
    return total


def g_wait(r):
    cs = sorted(r.randint(0, 12) for _ in range(r.randint(1, 8)))
    return [r.randint(1, 4), [[a, r.randint(1, 6)] for a in cs]]


def v_wait(tests):
    for t in tests:
        lanes, cs = t["args"]
        assert 1 <= lanes <= 1000 and 1 <= len(cs) <= 5000
        assert all(0 <= a <= 10 ** 6 and 1 <= s <= 100 for a, s in cs)
        assert all(cs[i][0] <= cs[i + 1][0] for i in range(len(cs) - 1))


CHECKS["checkout-lanes-total-wait"] = (b_wait, g_wait, "exact")
VALIDATE["checkout-lanes-total-wait"] = v_wait


# ================================================================ MEDIUM

# ---------------------------------------------------------------- smallest-first task order
p = add(
    id="smallest-first-task-order", title="Smallest-First Task Order With Prerequisites", diff="Medium", topic="Heap",
    fn="taskOrder", params=[("n", "int"), ("prereqs", "int[][]")], ret="int[]", cmp="exact",
    desc="<p>A build system has tasks numbered <code>0..n-1</code>. Each entry <code>[a, b]</code> of <code>prereqs</code> means that task <code>a</code> must be run <strong>before</strong> task <code>b</code>. Tasks run one at a time. Whenever the system has to choose, it runs the <strong>smallest-numbered</strong> task whose prerequisites have all been run already.</p><p>Return the sequence of task numbers in the order they are run. If the prerequisites contain a cycle, so that not every task can ever be run, return <code>[-1]</code>.</p><pre>n = 5, prereqs = [[3,1],[4,1],[1,0]]\nready at first: 2, 3, 4 -> run 2\nready: 3, 4 -> run 3; then 4; now 1 is ready -> run 1; then 0\nanswer = [2, 3, 4, 1, 0]</pre><p>Task 0 is the smallest number, but it cannot go first because it needs task 1.</p>",
    constraints=["1 &le; n &le; 3,000", "0 &le; prereqs.length &le; 5,000, 0 &le; a, b &lt; n, a != b", "The same pair may appear more than once", "The prerequisites may contain a cycle"],
    hints=["A task can run only when all its prerequisites are done. Count, for every task, how many prerequisites are still unfinished.",
           "Tasks with a count of zero are ready. Running a task lowers the count of every task that depends on it, which may make new tasks ready.",
           "Keep the ready tasks in a min-heap. Pop the smallest, append it to the order, decrease the counts of its dependants and push those that reach zero. If fewer than n tasks were produced, there is a cycle."],
    editorial=["This is Kahn's topological sort with one twist: the queue of ready tasks is a min-heap instead of a FIFO queue. The heap makes the task number the tie-breaker among all tasks that are ready at the same moment, which is exactly the rule in the statement and yields the lexicographically smallest topological order.",
               "Choosing the smallest ready task is always safe: any valid order can be changed to start with the smallest ready task without violating a dependency, so the greedy choice never loses lexicographic minimality.",
               "If a cycle exists, the tasks on it (and everything behind them) never reach a count of zero, so fewer than n tasks come out of the heap and we return [-1]. The cost is O((n + e) log n) time and O(n + e) space for e prerequisite pairs. Duplicate pairs are harmless because the count and the adjacency list are both incremented once per pair."],
    time="O((n + e) log n)", space="O(n + e)",
    solution='''import heapq


def taskOrder(n, prereqs):
    adj = [[] for _ in range(n)]
    indeg = [0] * n
    for a, b in prereqs:
        adj[a].append(b)
        indeg[b] += 1
    h = [i for i in range(n) if indeg[i] == 0]
    heapq.heapify(h)
    out = []
    while h:
        u = heapq.heappop(h)
        out.append(u)
        for v in adj[u]:
            indeg[v] -= 1
            if indeg[v] == 0:
                heapq.heappush(h, v)
    return out if len(out) == n else [-1]
''',
    tests=[[5, [[3, 1], [4, 1], [1, 0]]], [1, []], [3, []], [3, [[2, 1], [1, 0]]], [2, [[0, 1], [1, 0]]], [4, [[0, 1], [0, 1], [0, 1], [2, 3]]],
           [4, [[1, 2], [2, 3], [3, 1]]], [6, [[5, 0], [5, 2], [4, 1], [4, 0], [2, 3], [3, 1]]], [3, [[0, 1], [1, 2], [2, 0]]],
           [5, [[4, 3], [3, 2], [2, 1], [1, 0]]]],
)


def _dag_pairs(r, n, e):
    perm = list(range(n))
    r.shuffle(perm)
    out = []
    for _ in range(e):
        i, j = sorted(r.sample(range(n), 2))
        out.append([perm[i], perm[j]])
    return out


_r = rnd(9204)
p["tests"].append([3000, _dag_pairs(_r, 3000, 2500)])
p["tests"].append([3000, _dag_pairs(_r, 3000, 600)])
_e = _dag_pairs(_r, 3000, 2500)
_e.append(_e[7][::-1])
p["tests"].append([3000, _e])


def b_torder(n, prereqs):
    from itertools import permutations
    for perm in permutations(range(n)):
        pos = {v: i for i, v in enumerate(perm)}
        if all(pos[a] < pos[b] for a, b in prereqs):
            return list(perm)
    return [-1]


def g_torder(r):
    n = r.randint(1, 6)
    if n == 1:
        return [1, []]
    e = []
    for _ in range(r.randint(0, 7)):
        a, b = r.sample(range(n), 2)
        e.append([a, b])
    return [n, e]


def v_torder(tests):
    for t in tests:
        n, e = t["args"]
        assert 1 <= n <= 3000 and len(e) <= 5000
        assert all(0 <= a < n and 0 <= b < n and a != b for a, b in e)
        o = t["expected"]
        if o != [-1]:
            assert sorted(o) == list(range(n))


CHECKS["smallest-first-task-order"] = (b_torder, g_torder, "exact")
VALIDATE["smallest-first-task-order"] = v_torder

# ---------------------------------------------------------------- most booked meeting room
p = add(
    id="most-booked-meeting-room", title="Most Booked Meeting Room", diff="Medium", topic="Heap",
    fn="mostBooked", params=[("n", "int"), ("meetings", "int[][]")], ret="int", cmp="exact",
    desc="<p>An office has rooms numbered <code>0..n-1</code>. Each meeting is given as <code>[start, end]</code> and occupies a room for the half-open period <code>[start, end)</code>. All <code>start</code> values are different. The meetings are handled in increasing order of <code>start</code>, using these rules:</p><ul><li>If some rooms are free at the meeting's start, it takes the free room with the smallest number.</li><li>If every room is busy, the meeting <strong>waits</strong> for the room that becomes free first (ties: smaller room number). It then starts at that moment and keeps its original length, so its end is shifted by the same delay.</li><li>A room whose meeting ends at time <code>t</code> is free at time <code>t</code>.</li></ul><p>Return the number of the room that hosts the most meetings; if several rooms tie, return the smallest number.</p><pre>n = 2, meetings = [[0,10],[1,5],[2,7],[3,4]]\n[0,10] -> room 0 (until 10); [1,5] -> room 1 (until 5)\n[2,7]: both busy, room 1 frees at 5 -> runs 5..10 in room 1\n[3,4]: both busy, rooms 0 and 1 free at 10 -> runs 10..11 in room 0\nroom 0 hosted 2 meetings, room 1 hosted 2 -> tie -> answer = 0</pre>",
    constraints=["1 &le; n &le; 100", "1 &le; meetings.length &le; 5,000", "0 &le; start &lt; end &le; 500,000", "All start values are distinct (the meetings are not necessarily sorted)"],
    hints=["Sort the meetings by start and process them one at a time; delayed meetings only influence the later ones through the room they occupy.",
           "You need two things at each meeting: the free room with the smallest number, and, if there is none, the room that finishes first.",
           "Use a min-heap of free room numbers and a min-heap of busy rooms ordered by <code>(end time, room)</code>. Move rooms whose end is at most the start into the free heap. If the free heap is empty, pop the busy heap instead: the meeting starts at that end time, and its new end is <code>that end + (end - start)</code>."],
    editorial=["Process meetings by increasing original start; this is the order in which the rules give priority. A meeting that is delayed keeps its length, so we only need to store the (possibly shifted) end time of every busy room.",
               "Free rooms are kept in a min-heap of numbers so that the smallest is chosen. Busy rooms live in a heap keyed by <code>(end time, room number)</code>: when everyone is busy, its top is exactly the room that frees first with the smallest number among ties. When rooms are free, first release every busy room with end &le; start.",
               "Counting the meetings per room and returning the first index of the maximum handles the tie rule. The time is O(m log m + m log n) and the end times can exceed 32 bits in other languages, because delays accumulate, so use 64-bit integers there."],
    time="O(m log m)", space="O(n + m)",
    solution='''import heapq


def mostBooked(n, meetings):
    free = list(range(n))
    busy = []
    cnt = [0] * n
    for s, e in sorted(meetings):
        while busy and busy[0][0] <= s:
            heapq.heappush(free, heapq.heappop(busy)[1])
        if free:
            r = heapq.heappop(free)
            st = s
        else:
            st, r = heapq.heappop(busy)
        heapq.heappush(busy, (st + e - s, r))
        cnt[r] += 1
    return cnt.index(max(cnt))
''',
    tests=[[2, [[0, 10], [1, 5], [2, 7], [3, 4]]], [1, [[5, 6]]], [3, [[1, 20], [2, 10], [3, 5], [4, 9], [6, 8]]], [2, [[0, 1], [10, 11], [20, 21]]],
           [3, [[3, 4], [1, 2], [2, 3]]], [2, [[1, 5], [2, 6], [3, 7], [4, 8]]], [4, [[0, 100], [1, 100], [2, 100], [3, 100], [4, 5]]],
           [2, [[0, 10], [1, 2], [2, 3], [3, 4], [4, 5]]], [5, [[10, 11], [11, 12]]]],
)
_r = rnd(9205)
_st = _r.sample(range(0, 200000), 3000)
p["tests"].append([3, [[s, s + _r.randint(1, 200)] for s in _st]])
_st = _r.sample(range(0, 400000), 2500)
p["tests"].append([100, [[s, s + _r.randint(1, 100000)] for s in _st]])
_st = _r.sample(range(0, 5000), 1500)
p["tests"].append([17, [[s, s + _r.randint(1, 500000 - s) % 400 + 1] for s in _st]])


def b_booked(n, meetings):
    free = [0] * n
    cnt = [0] * n
    for s, e in sorted(meetings):
        ready = [r for r in range(n) if free[r] <= s]
        if ready:
            r = min(ready)
            st = s
        else:
            st = min(free)
            r = min(x for x in range(n) if free[x] == st)
        free[r] = st + e - s
        cnt[r] += 1
    best = max(cnt)
    return [i for i in range(n) if cnt[i] == best][0]


def g_booked(r):
    st = r.sample(range(0, 20), r.randint(1, 8))
    return [r.randint(1, 4), [[s, s + r.randint(1, 8)] for s in st]]


def v_booked(tests):
    for t in tests:
        n, ms = t["args"]
        assert 1 <= n <= 100 and 1 <= len(ms) <= 5000
        assert all(0 <= s < e <= 500000 for s, e in ms)
        assert len({s for s, _ in ms}) == len(ms)
        assert 0 <= t["expected"] < n


CHECKS["most-booked-meeting-room"] = (b_booked, g_booked, "exact")
VALIDATE["most-booked-meeting-room"] = v_booked

# ---------------------------------------------------------------- orders in the backlog
p = add(
    id="order-book-backlog-total", title="Order Book Backlog Total", diff="Medium", topic="Heap",
    fn="backlogTotal", params=[("orders", "int[][]")], ret="int", cmp="exact",
    desc="<p>A trading system keeps a <em>backlog</em> of unmatched orders. Each incoming order is <code>[price, amount, type]</code> where <code>type = 0</code> is a <strong>buy</strong> and <code>type = 1</code> is a <strong>sell</strong>. Orders arrive in the given sequence and are processed one by one:</p><ul><li>A buy order matches against the sell orders in the backlog whose price is <strong>at most</strong> its price, always taking the cheapest sell order first.</li><li>A sell order matches against the buy orders in the backlog whose price is <strong>at least</strong> its price, always taking the most expensive buy order first.</li><li>A match trades <code>min(amounts)</code> units and removes them from both orders; keep matching while units remain and a matching order exists.</li><li>Whatever is left of the incoming order is added to the backlog.</li></ul><p>After all orders have been processed, return the total number of units still in the backlog, modulo <code>1,000,000,007</code>.</p><pre>orders = [[10,5,0],[15,2,1],[25,1,1],[30,4,0]]\nbuy 5 @10 -> backlog\nsell 2 @15: needs a buy &ge; 15, none -> backlog\nsell 1 @25 -> backlog\nbuy 4 @30: sells &le; 30 are @15 (2) and @25 (1): trades 2 then 1, 1 unit left -> backlog\nbacklog: buy 5 @10, buy 1 @30 -> total 6</pre>",
    constraints=["1 &le; orders.length &le; 5,000", "1 &le; price, amount &le; 10<sup>9</sup>", "type is 0 (buy) or 1 (sell)"],
    hints=["The backlog never contains a buy and a sell that could trade with each other, so the two sides can be stored separately.",
           "For a new buy you repeatedly need the cheapest sell; for a new sell you repeatedly need the most expensive buy. That is a min-heap and a max-heap.",
           "Keep a min-heap of sells <code>(price, amount)</code> and a max-heap of buys (store the negated price). Match while possible, pushing back the unfinished part of the order at the top if it is only partly used, then add what remains of the incoming order. At the end sum the amounts in both heaps modulo 1,000,000,007."],
    editorial=["After every step the backlog is stable: its best buy price is strictly below its best sell price. A new buy can only trade with the cheapest sells, a new sell only with the highest buys, so each side needs a priority queue ordered by the price that matters first.",
               "Each loop iteration either removes an order completely from a heap or finishes the incoming order, so the number of heap operations is bounded by a constant times the number of orders: every order is pushed at most once (plus at most one re-push after a partial match). The time is O(n log n).",
               "The total amount can reach 5 &times; 10<sup>12</sup>, hence the modulo; in a fixed-width language accumulate the sum in a 64-bit type or reduce while adding."],
    time="O(n log n)", space="O(n)",
    solution='''import heapq


def backlogTotal(orders):
    MOD = 10 ** 9 + 7
    buys = []
    sells = []
    for price, amount, typ in orders:
        if typ == 0:
            while amount and sells and sells[0][0] <= price:
                sp, sa = heapq.heappop(sells)
                if sa > amount:
                    heapq.heappush(sells, (sp, sa - amount))
                    amount = 0
                else:
                    amount -= sa
            if amount:
                heapq.heappush(buys, (-price, amount))
        else:
            while amount and buys and -buys[0][0] >= price:
                bp, ba = heapq.heappop(buys)
                if ba > amount:
                    heapq.heappush(buys, (bp, ba - amount))
                    amount = 0
                else:
                    amount -= ba
            if amount:
                heapq.heappush(sells, (price, amount))
    return (sum(a for _, a in buys) + sum(a for _, a in sells)) % MOD
''',
    tests=[[[[10, 5, 0], [15, 2, 1], [25, 1, 1], [30, 4, 0]]], [[[7, 1000000000, 1], [15, 3, 0], [5, 999999999, 0]]], [[[5, 3, 0]]],
           [[[5, 3, 0], [5, 3, 1]]], [[[5, 3, 0], [6, 3, 1]]], [[[10, 4, 1], [10, 4, 1], [10, 5, 0]]], [[[1, 1, 0], [2, 1, 0], [3, 1, 0], [1, 2, 1]]],
           [[[B, B, 0], [B, B, 1], [B, B, 1], [1, B, 0]]], [[[3, 2, 1], [4, 2, 1], [5, 2, 1], [9, 5, 0], [1, 10, 1]]], [[[8, 5, 0], [9, 5, 0], [7, 8, 1], [7, 3, 1]]]],
)
_r = rnd(9206)
p["tests"].append([[[_r.randint(1, 1000), _r.randint(1, B), _r.randint(0, 1)] for _ in range(2500)]])
p["tests"].append([[[_r.randint(1, 50), _r.randint(1, 20), _r.randint(0, 1)] for _ in range(4000)]])
p["tests"].append([[[_r.randint(1, 100) + (0 if i % 2 else 500), _r.randint(1, B), i % 2] for i in range(1500)]])


def b_backlog(orders):
    buys = []
    sells = []
    for price, amount, typ in orders:
        if typ == 0:
            while amount:
                c = [s for s in sells if s[0] <= price]
                if not c:
                    break
                s = min(c, key=lambda x: x[0])
                q = min(amount, s[1])
                amount -= q
                s[1] -= q
                if s[1] == 0:
                    sells.remove(s)
            if amount:
                buys.append([price, amount])
        else:
            while amount:
                c = [b for b in buys if b[0] >= price]
                if not c:
                    break
                b = max(c, key=lambda x: x[0])
                q = min(amount, b[1])
                amount -= q
                b[1] -= q
                if b[1] == 0:
                    buys.remove(b)
            if amount:
                sells.append([price, amount])
    return (sum(x[1] for x in buys) + sum(x[1] for x in sells)) % MOD


def g_backlog(r):
    return [[[r.randint(1, 8), r.randint(1, 6), r.randint(0, 1)] for _ in range(r.randint(1, 10))]]


def v_backlog(tests):
    for t in tests:
        o = t["args"][0]
        assert 1 <= len(o) <= 5000
        assert all(1 <= a <= B and 1 <= b <= B and c in (0, 1) for a, b, c in o)


CHECKS["order-book-backlog-total"] = (b_backlog, g_backlog, "exact")
VALIDATE["order-book-backlog-total"] = v_backlog

# ---------------------------------------------------------------- maximum cpu load
p = add(
    id="maximum-cpu-load", title="Maximum CPU Load", diff="Medium", topic="Heap", tier="extra",
    fn="maxLoad", params=[("jobs", "int[][]")], ret="int", cmp="exact",
    desc="<p>Each job is given as <code>[start, end, load]</code>. While it runs, from time <code>start</code> up to but not including time <code>end</code>, it puts <code>load</code> units of work on a single CPU. A job that ends at time <code>t</code> no longer counts at time <code>t</code>.</p><p>Return the maximum total load that the CPU has at any single moment.</p><pre>jobs = [[1,4,3],[2,5,4],[4,7,2],[6,9,5]]\ntime 2..3: jobs 0 and 1 run -> 3 + 4 = 7\ntime 4:    jobs 1 and 2 run (job 0 ended) -> 4 + 2 = 6\ntime 6:    jobs 2 and 3 run (job 1 ended) -> 2 + 5 = 7\nanswer = 7</pre>",
    constraints=["1 &le; jobs.length &le; 5,000", "0 &le; start &lt; end &le; 10<sup>9</sup>", "1 &le; load &le; 100,000", "The jobs are in arbitrary order"],
    hints=["The load can only change at job start times, and the maximum is reached right after some job starts. So it is enough to know the total load just after each start.",
           "Process the jobs sorted by start. Which jobs are still running when the next job starts?",
           "Keep a min-heap of <code>(end, load)</code> of running jobs and the current total. Before adding a job, pop every job with <code>end &le; start</code> and subtract its load; then push the job, add its load and update the maximum."],
    editorial=["Sort by start time. Maintain the running total of all jobs that are active at the current start. A min-heap keyed by end time gives the job that finishes first; if its end is at most the new start it is already over and its load must be removed (a job ending exactly at the start does not overlap).",
               "After inserting the new job the total equals the exact load at time <code>start</code>, because every job that started earlier and has not ended is in the heap. Since the load only increases at start times, the maximum over these values is the answer.",
               "Sorting costs O(n log n) and each job enters and leaves the heap once, giving O(n log n) overall. A sweep over sorted start/end events works as well, but must process the ends before the starts at equal times."],
    time="O(n log n)", space="O(n)",
    solution='''import heapq


def maxLoad(jobs):
    h = []
    cur = 0
    best = 0
    for s, e, w in sorted(jobs):
        while h and h[0][0] <= s:
            cur -= heapq.heappop(h)[1]
        heapq.heappush(h, (e, w))
        cur += w
        best = max(best, cur)
    return best
''',
    tests=[[[[1, 4, 3], [2, 5, 4], [4, 7, 2], [6, 9, 5]]], [[[1, 2, 5]]], [[[1, 4, 3], [4, 8, 6]]], [[[1, 4, 3], [1, 4, 3], [1, 4, 3]]],
           [[[6, 9, 5], [1, 10, 1], [2, 3, 7], [3, 4, 7]]], [[[0, B, 100000], [5, 6, 1], [5, 7, 2]]], [[[1, 3, 2], [2, 4, 2], [3, 5, 2], [4, 6, 2]]],
           [[[10, 20, 4], [1, 30, 1], [15, 16, 9], [16, 17, 9]]], [[[0, 1, 1], [1, 2, 1], [2, 3, 1]]]],
)
_r = rnd(9207)
_j = []
for _ in range(1500):
    s = _r.randint(0, 10 ** 6)
    _j.append([s, s + _r.randint(1, 100000), _r.randint(1, 100000)])
p["tests"].append([_j])
_j = []
for _ in range(2500):
    s = _r.randint(0, 3000)
    _j.append([s, s + _r.randint(1, 60), _r.randint(1, 100000)])
p["tests"].append([_j])
p["tests"].append([[[i, 10 ** 9 - i, 100000] for i in range(800)]])


def b_load(jobs):
    best = 0
    for s, _, _ in jobs:
        best = max(best, sum(w for a, b, w in jobs if a <= s < b))
    return best


def g_load(r):
    out = []
    for _ in range(r.randint(1, 8)):
        s = r.randint(0, 12)
        out.append([s, s + r.randint(1, 7), r.randint(1, 9)])
    return [out]


def v_load(tests):
    for t in tests:
        js = t["args"][0]
        assert 1 <= len(js) <= 5000
        assert all(0 <= s < e <= B and 1 <= w <= 100000 for s, e, w in js)


CHECKS["maximum-cpu-load"] = (b_load, lambda r: g_load(r), "exact")
VALIDATE["maximum-cpu-load"] = v_load

# ---------------------------------------------------------------- parallel tasks with workers
p = add(
    id="dependent-tasks-with-workers", title="Dependent Tasks With Limited Workers", diff="Medium", topic="Heap",
    fn="finishTime", params=[("workers", "int"), ("durations", "int[]"), ("deps", "int[][]")], ret="int", cmp="exact",
    desc="<p>There are <code>n = durations.length</code> tasks numbered <code>0..n-1</code>; task <code>i</code> takes <code>durations[i]</code> time units. Each entry <code>[a, b]</code> of <code>deps</code> means task <code>a</code> must be <strong>finished</strong> before task <code>b</code> can start. The dependencies contain no cycle.</p><p>You have <code>workers</code> identical workers and every worker handles one task at a time without interruption. The schedule is generated by this rule: whenever a worker is idle and some tasks are <em>ready</em> (all their prerequisites are finished and they have not started), the ready task with the <strong>smallest number</strong> is started immediately. A task whose prerequisite finishes at time <code>t</code> is ready at time <code>t</code>, and a worker that finishes at time <code>t</code> is idle at time <code>t</code>. At time 0 all tasks without prerequisites are ready.</p><p>Return the time at which the last task finishes.</p><pre>workers = 2, durations = [3, 2, 4, 1]\ndeps = [[0, 3], [1, 3]]\nt=0: tasks 0, 1, 2 are ready -> start 0 and 1\nt=2: task 1 done -> start task 2 (ends 6)\nt=3: task 0 done -> task 3 is ready (0 and 1 done) -> starts, ends 4\nanswer = 6</pre>",
    constraints=["1 &le; workers &le; 100", "1 &le; n &le; 3,000, 1 &le; durations[i] &le; 1,000", "0 &le; deps.length &le; 2,500, all pairs are distinct and the dependency graph is acyclic"],
    hints=["Think of the schedule as an event simulation: time only changes when some running task finishes.",
           "You need the smallest-numbered ready task, and the running task that finishes first. Both are priority-queue questions. To know when a task is ready, count its unfinished prerequisites.",
           "Keep <code>indegree</code> counts, a min-heap <code>ready</code> of task numbers, and a min-heap <code>running</code> of <code>(finish, task)</code>. Start tasks while a worker and a ready task exist. Then jump to the earliest finish time, finish every task with exactly that time (decreasing the indegree of its successors, pushing new ready ones) and repeat."],
    editorial=["This is a topological sort driven by a clock. Whenever a task finishes, each task that depends on it loses one pending prerequisite; when that count reaches zero it enters the <code>ready</code> heap, ordered by task number as the rule demands.",
               "At every decision time we fill the idle workers from the ready heap, then advance the clock to the smallest finish time in the <code>running</code> heap. All tasks finishing at that exact moment must be completed <em>before</em> new tasks are started, because their successors may be ready and may have a smaller number than tasks that were already waiting.",
               "Every task enters each heap once, every dependency is relaxed once, so the running time is O((n + e) log n). The answer is the clock value when the last running task finishes."],
    time="O((n + e) log n)", space="O(n + e)",
    solution='''import heapq


def finishTime(workers, durations, deps):
    n = len(durations)
    adj = [[] for _ in range(n)]
    indeg = [0] * n
    for a, b in deps:
        adj[a].append(b)
        indeg[b] += 1
    ready = [i for i in range(n) if indeg[i] == 0]
    heapq.heapify(ready)
    running = []
    free = workers
    t = 0
    while ready or running:
        while ready and free:
            i = heapq.heappop(ready)
            heapq.heappush(running, (t + durations[i], i))
            free -= 1
        t = running[0][0]
        while running and running[0][0] == t:
            _, i = heapq.heappop(running)
            free += 1
            for v in adj[i]:
                indeg[v] -= 1
                if indeg[v] == 0:
                    heapq.heappush(ready, v)
    return t
''',
    tests=[[2, [3, 2, 4, 1], [[0, 3], [1, 3]]], [1, [5], []], [3, [2, 2, 2], []], [1, [2, 3, 4], []], [2, [1, 1, 1, 1], [[0, 1], [1, 2], [2, 3]]],
           [2, [5, 1, 1, 1], [[0, 3], [1, 2]]], [1, [1, 1, 1, 1], [[3, 2], [2, 1], [1, 0]]], [3, [4, 4, 1, 1, 1], [[0, 4], [1, 4], [2, 3]]],
           [2, [2, 2, 2, 2, 2, 2], [[0, 5], [1, 5], [2, 4], [3, 4]]], [100, [7, 3, 9], [[0, 1], [1, 2]]]],
)


def _dag(r, n, e):
    perm = list(range(n))
    r.shuffle(perm)
    seen = set()
    out = []
    tries = 0
    while len(out) < e and tries < 20 * e + 20:
        tries += 1
        i, j = r.sample(range(n), 2)
        if i > j:
            i, j = j, i
        if j - i > max(3, n // 8) and r.random() < 0.7:
            continue
        if (i, j) in seen:
            continue
        seen.add((i, j))
        out.append([perm[i], perm[j]])
    return out


_r = rnd(9208)
_n = 3000
p["tests"].append([8, [_r.randint(1, 1000) for _ in range(_n)], _dag(_r, _n, 2500)])
p["tests"].append([100, [_r.randint(1, 1000) for _ in range(_n)], _dag(_r, _n, 1200)])
p["tests"].append([1, [_r.randint(1, 1000) for _ in range(2000)], _dag(_r, 2000, 2400)])


def b_finish(workers, durations, deps):
    n = len(durations)
    pre = [set() for _ in range(n)]
    for a, b in deps:
        pre[b].add(a)
    done = set()
    started = set()
    endt = {}
    t = 0
    while len(done) < n:
        for i, e in list(endt.items()):
            if e == t and i not in done:
                done.add(i)
        busy = sum(1 for i, e in endt.items() if i not in done)
        for i in range(n):
            if busy >= workers:
                break
            if i not in started and pre[i] <= done:
                started.add(i)
                endt[i] = t + durations[i]
                busy += 1
        if len(done) == n:
            break
        t += 1
    return t


def g_finish(r):
    n = r.randint(1, 7)
    return [r.randint(1, 3), [r.randint(1, 4) for _ in range(n)], _dag(r, n, r.randint(0, min(6, n * (n - 1) // 2)))]


def v_finish(tests):
    for t in tests:
        w, d, deps = t["args"]
        n = len(d)
        assert 1 <= w <= 100 and 1 <= n <= 3000 and len(deps) <= 2500
        assert all(1 <= x <= 1000 for x in d)
        assert len({tuple(x) for x in deps}) == len(deps)
        indeg = [0] * n
        adj = [[] for _ in range(n)]
        for a, b in deps:
            assert 0 <= a < n and 0 <= b < n and a != b
            adj[a].append(b)
            indeg[b] += 1
        st = [i for i in range(n) if indeg[i] == 0]
        seen = 0
        while st:
            u = st.pop()
            seen += 1
            for v in adj[u]:
                indeg[v] -= 1
                if indeg[v] == 0:
                    st.append(v)
        assert seen == n, "cycle"


CHECKS["dependent-tasks-with-workers"] = (b_finish, g_finish, "exact")
VALIDATE["dependent-tasks-with-workers"] = v_finish


# ================================================================ HARD

# ---------------------------------------------------------------- smallest interval containing each query
p = add(
    id="smallest-interval-for-each-query", title="Smallest Interval for Each Query", diff="Hard", topic="Heap",
    fn="minInterval", params=[("intervals", "int[][]"), ("queries", "int[]")], ret="int[]", cmp="exact",
    desc="<p>You are given closed intervals <code>intervals[i] = [left, right]</code> and a list of integer <code>queries</code>. The <em>size</em> of an interval is <code>right - left + 1</code>.</p><p>For every query <code>q</code>, find the smallest size among the intervals that contain <code>q</code> (that is, <code>left &le; q &le; right</code>). If no interval contains <code>q</code>, the answer for that query is <code>-1</code>. Return the answers in the order of the queries.</p><pre>intervals = [[1,4],[2,4],[3,6],[4,4]], queries = [2,3,4,5,9]\nq=2: [1,4] (4), [2,4] (3) -> 3\nq=3: [1,4], [2,4], [3,6] -> sizes 4, 3, 4 -> 3\nq=4: [4,4] has size 1 -> 1\nq=5: only [3,6] (4) -> 4\nq=9: none -> -1\nanswer = [3, 3, 1, 4, -1]</pre>",
    constraints=["1 &le; intervals.length, queries.length &le; 2,500", "1 &le; left &le; right &le; 10<sup>9</sup>", "1 &le; queries[j] &le; 10<sup>9</sup>"],
    hints=["Checking every interval for every query is O(nq). The queries are independent, so you may answer them in any order you like.",
           "Answer the queries in increasing order. Then an interval becomes relevant once <code>left &le; q</code>, and it is useless forever after <code>right &lt; q</code>.",
           "Sort intervals by left and queries ascending (remember their original positions). Push intervals with <code>left &le; q</code> into a min-heap of <code>(size, right)</code>. Pop from the top while <code>right &lt; q</code>; the top, if any, is the answer."],
    editorial=["Offline processing turns a 2-D condition into a sweep. When queries are sorted ascending, the set of intervals with <code>left &le; q</code> only grows, so each interval is inserted exactly once with a single pointer into the sorted interval list.",
               "Among the inserted intervals we want the smallest size whose right end is at least q. Intervals with right &lt; q can be discarded permanently, since later queries are larger. We discard lazily: a min-heap ordered by size exposes the best candidate, and while its right end is smaller than q we pop it. Whatever is left on top contains q (it started at or before q and ends at or after q) and has the minimum size.",
               "Sorting costs O((n + q) log) and each interval is pushed and popped at most once, so the total is O((n + q) log n) time and O(n + q) space."],
    time="O((n + q) log n)", space="O(n + q)",
    solution='''import heapq


def minInterval(intervals, queries):
    iv = sorted(intervals)
    order = sorted(range(len(queries)), key=lambda i: queries[i])
    res = [-1] * len(queries)
    h = []
    p = 0
    for qi in order:
        q = queries[qi]
        while p < len(iv) and iv[p][0] <= q:
            heapq.heappush(h, (iv[p][1] - iv[p][0] + 1, iv[p][1]))
            p += 1
        while h and h[0][1] < q:
            heapq.heappop(h)
        if h:
            res[qi] = h[0][0]
    return res
''',
    tests=[[[[1, 4], [2, 4], [3, 6], [4, 4]], [2, 3, 4, 5, 9]], [[[5, 5]], [5]], [[[5, 5]], [4, 6]], [[[1, 10]], [1, 10, 11]],
           [[[2, 3], [2, 5], [1, 8], [20, 25]], [2, 19, 5, 22, 8]], [[[1, B]], [B, 1, 500000000]], [[[3, 9], [3, 9], [4, 6]], [3, 4, 9, 6, 7]],
           [[[1, 2], [3, 4], [5, 6]], [6, 4, 2, 3, 1, 5]], [[[1, 100], [10, 20], [12, 13], [30, 31]], [12, 15, 31, 50, 20, 21]]],
)
_r = rnd(9209)
_iv = []
for _ in range(1500):
    l = _r.randint(1, 10 ** 6)
    _iv.append([l, l + _r.randint(0, 300000)])
p["tests"].append([_iv, [_r.randint(1, 1300000) for _ in range(1500)]])
_iv = []
for _ in range(1200):
    l = _r.randint(1, B - 10 ** 6)
    _iv.append([l, l + _r.randint(0, 10 ** 6)])
p["tests"].append([_iv, [_r.choice(_iv)[0] + _r.randint(0, 10 ** 6) for _ in range(1200)]])
_iv = [[i + 1, 5000 - i] for i in range(2500)]
p["tests"].append([_iv, [_r.randint(1, 5100) for _ in range(2500)]])


def b_minint(intervals, queries):
    out = []
    for q in queries:
        best = -1
        for l, r in intervals:
            if l <= q <= r and (best == -1 or r - l + 1 < best):
                best = r - l + 1
        out.append(best)
    return out


def g_minint(r):
    iv = []
    for _ in range(r.randint(1, 6)):
        l = r.randint(1, 12)
        iv.append([l, l + r.randint(0, 6)])
    return [iv, [r.randint(1, 20) for _ in range(r.randint(1, 8))]]


def v_minint(tests):
    for t in tests:
        iv, qs = t["args"]
        assert 1 <= len(iv) <= 2500 and 1 <= len(qs) <= 2500
        assert all(1 <= l <= r <= B for l, r in iv) and all(1 <= q <= B for q in qs)
        assert len(t["expected"]) == len(qs)


CHECKS["smallest-interval-for-each-query"] = (b_minint, g_minint, "exact")
VALIDATE["smallest-interval-for-each-query"] = v_minint

# ---------------------------------------------------------------- k-ary rope merging
p = add(
    id="merge-ropes-up-to-k-at-a-time", title="Merge Ropes Up To K At A Time", diff="Hard", topic="Heap", tier="extra",
    fn="mergeCostK", params=[("ropes", "int[]"), ("k", "int")], ret="int", cmp="exact",
    desc="<p>You have ropes with lengths <code>ropes</code>. In one operation you pick <strong>between 2 and k</strong> ropes (any number in that range) and tie them into a single rope whose length is the sum of the chosen lengths; the operation costs exactly that sum.</p><p>Repeat until only one rope remains and return the minimum possible total cost. A single rope needs no operation, so the cost is 0.</p><pre>ropes = [4, 3, 2, 6], k = 3\ntie 2 + 3 = 5 (cost 5)   -> [4, 5, 6]\ntie 4 + 5 + 6 = 15 (cost 15) -> [15]\ntotal = 20\n(tying 2, 3 and 4 first costs 9, then 9 + 6 costs 15: total 24)</pre><p>With <code>k = 2</code> this is the classic problem, answer 29 for the same ropes.</p>",
    constraints=["1 &le; ropes.length &le; 5,000", "1 &le; ropes[i] &le; 1,000", "2 &le; k &le; 100"],
    hints=["For k = 2 the greedy rule is to always tie the two shortest ropes. Think about what the final tying tree looks like and how many ropes each node of the tree may have.",
           "A rope that is tied late is paid for few times, so the shortest ropes should be at the bottom of the tree and each node should have as many children (up to k) as possible. The only problem is that the last operation might not be able to take exactly k ropes.",
           "Make the number of ropes <code>n</code> satisfy <code>(n - 1) % (k - 1) == 0</code> by adding zero-length ropes (a zero rope means \"this operation ties fewer than k ropes\"). Then always tie the k shortest ropes with a min-heap."],
    editorial=["Every rope is paid for once for each operation it takes part in, directly or through the ropes it was merged into: its length times its depth in the merge tree. We want the tree that minimises the sum of length times depth; this is Huffman coding with a k-ary tree.",
               "In a k-ary tree where every internal node has exactly k children, the number of leaves n satisfies <code>(n - 1) % (k - 1) == 0</code>. If it does not, we add <code>(k - 1) - (n - 1) % (k - 1)</code> dummy ropes of length 0. They cost nothing, but they let one operation (the deepest one) tie fewer than k real ropes. Then repeat: pop the k smallest, push their sum, and add the sum to the cost.",
               "Each operation removes k - 1 ropes, so there are about n / (k - 1) operations, each with k pops and one push: O(n log n) time in total, O(n) space. If k &ge; n a single operation ties everything, which the padding reproduces automatically."],
    time="O(n log n)", space="O(n)",
    solution='''import heapq


def mergeCostK(ropes, k):
    h = list(ropes)
    n = len(h)
    if n == 1:
        return 0
    r = (n - 1) % (k - 1)
    if r:
        h += [0] * (k - 1 - r)
    heapq.heapify(h)
    total = 0
    while len(h) > 1:
        s = 0
        for _ in range(k):
            s += heapq.heappop(h)
        total += s
        heapq.heappush(h, s)
    return total
''',
    tests=[[[4, 3, 2, 6], 3], [[4, 3, 2, 6], 2], [[7], 5], [[3, 5], 4], [[1, 1, 1, 1, 1], 3], [[1, 2, 3, 4, 5, 6, 7], 3], [[10, 1, 1, 1, 1], 4],
           [[5, 5, 5, 5, 5, 5], 5], [[1000, 1, 1000, 1, 1000], 2], [[2, 2, 2, 2], 4], [[1, 2, 3, 4, 5, 6, 7, 8, 9, 10], 100]],
)
_r = rnd(9210)
p["tests"].append([[_r.randint(1, 1000) for _ in range(5000)], 2])
p["tests"].append([[_r.randint(1, 1000) for _ in range(4999)], 7])
p["tests"].append([[_r.randint(1, 1000) for _ in range(4500)], 100])


def b_kary(ropes, k):
    seen = {}

    def go(t):
        if len(t) == 1:
            return 0
        if t in seen:
            return seen[t]
        best = None
        n = len(t)
        for mask in range(1, 1 << n):
            c = bin(mask).count("1")
            if c < 2 or c > k:
                continue
            s = sum(t[i] for i in range(n) if mask >> i & 1)
            rest = [t[i] for i in range(n) if not mask >> i & 1]
            v = s + go(tuple(sorted(rest + [s])))
            if best is None or v < best:
                best = v
        seen[t] = best
        return best

    return go(tuple(sorted(ropes)))


def v_kary(tests):
    for t in tests:
        a, k = t["args"]
        assert 1 <= len(a) <= 5000 and all(1 <= x <= 1000 for x in a) and 2 <= k <= 100


CHECKS["merge-ropes-up-to-k-at-a-time"] = (b_kary, lambda r: [[r.randint(1, 9) for _ in range(r.randint(1, 6))], r.randint(2, 5)], "exact")
VALIDATE["merge-ropes-up-to-k-at-a-time"] = v_kary

# ---------------------------------------------------------------- shortest remaining time first
p = add(
    id="shortest-remaining-time-completion", title="Shortest Remaining Time First", diff="Hard", topic="Heap", tier="extra",
    fn="completionTimes", params=[("jobs", "int[][]")], ret="int[]", cmp="exact",
    desc="<p>A single CPU uses <strong>preemptive shortest-remaining-time-first</strong> scheduling. Job <code>i</code> is given as <code>jobs[i] = [arrival, burst]</code>: it becomes available at time <code>arrival</code> and needs <code>burst</code> units of CPU time in total.</p><p>At every moment the CPU runs the available unfinished job with the smallest <em>remaining</em> time (ties: smaller index). When a job arrives whose remaining time is smaller than that of the running job, or equal with a smaller index, it takes over immediately, and the interrupted job keeps its remaining time. If no job is available the CPU idles until the next arrival. Return the time at which each job finishes, indexed like <code>jobs</code>.</p><pre>jobs = [[0, 7], [2, 4], [4, 1], [5, 4]]\n0..2 job 0 runs (5 left); at 2 job 1 (4) is shorter -> runs 2..4 (2 left)\nat 4 job 2 (1) is shorter -> runs 4..5, done at 5\nat 5: job 1 (2 left), job 3 (4), job 0 (5) -> job 1 runs 5..7, done at 7\njob 3 runs 7..11, job 0 runs 11..16\nanswer = [16, 7, 5, 11]</pre>",
    constraints=["1 &le; jobs.length &le; 5,000", "0 &le; arrival &le; 10<sup>6</sup>", "1 &le; burst &le; 1,000"],
    hints=["Simulating every time unit is far too slow for large arrival times, and the CPU may even idle for a long time. Only a few instants matter: arrivals and completions.",
           "Between two consecutive arrival times the set of available jobs is fixed, so the CPU simply keeps working on the best job until it finishes or the next arrival occurs, whichever is first.",
           "Sort the jobs by arrival. Keep a clock and a min-heap of <code>(remaining, index)</code>. Push all arrived jobs, pop the best, and run it for <code>min(remaining, next_arrival - clock)</code>. If it is not finished push it back with the reduced remaining time; otherwise record the finish time. If the heap is empty, jump the clock to the next arrival."],
    editorial=["The schedule can only change at an arrival (a newcomer may preempt) or at a completion. Between those events the CPU works on the job with the smallest remaining time, so we can jump from event to event instead of stepping through unit times.",
               "Maintain a clock <code>t</code>, the next unseen arrival, and a min-heap keyed by <code>(remaining, index)</code>. After inserting every job with arrival &le; t, pop the best job. If it can finish before the next arrival (<code>t + remaining &le; next_arrival</code>) record <code>t + remaining</code> as its completion time. Otherwise run it until the next arrival and push the leftover back; the loop then inserts the new arrival and the heap decides whether it preempts.",
               "Each arrival causes at most one preemption, so the number of loop iterations is at most 2n and the cost is O(n log n). The tie-break by index is encoded by the second tuple component. If no job is available, jump forward to the next arrival rather than stepping the clock."],
    time="O(n log n)", space="O(n)",
    solution='''import heapq


def completionTimes(jobs):
    n = len(jobs)
    order = sorted(range(n), key=lambda i: (jobs[i][0], i))
    h = []
    done = [0] * n
    t = 0
    p = 0
    finished = 0
    while finished < n:
        if not h and t < jobs[order[p]][0]:
            t = jobs[order[p]][0]
        while p < n and jobs[order[p]][0] <= t:
            i = order[p]
            heapq.heappush(h, (jobs[i][1], i))
            p += 1
        rem, i = heapq.heappop(h)
        nxt = jobs[order[p]][0] if p < n else None
        if nxt is None or t + rem <= nxt:
            t += rem
            done[i] = t
            finished += 1
        else:
            heapq.heappush(h, (rem - (nxt - t), i))
            t = nxt
    return done
''',
    tests=[[[[0, 7], [2, 4], [4, 1], [5, 4]]], [[[3, 5]]], [[[0, 3], [0, 3], [0, 3]]], [[[0, 5], [1, 5]]], [[[0, 5], [1, 4]]], [[[0, 1], [10, 1], [20, 2]]],
           [[[0, 8], [1, 4], [2, 2], [3, 1]]], [[[5, 2], [0, 10], [5, 2]]], [[[1000000, 1000], [0, 1000]]], [[[0, 4], [2, 2], [2, 2], [3, 1]]],
           [[[0, 6], [1, 6], [2, 6], [3, 5], [4, 4]]]],
)
_r = rnd(9211)
p["tests"].append([[[_r.randint(0, 10 ** 6), _r.randint(1, 1000)] for _ in range(1500)]])
p["tests"].append([[[_r.randint(0, 3000), _r.randint(1, 1000)] for _ in range(1500)]])
p["tests"].append([[[_r.randint(0, 20000), _r.randint(1, 10)] for _ in range(2500)]])


def b_srtf(jobs):
    n = len(jobs)
    rem = [b for _, b in jobs]
    done = [0] * n
    t = 0
    left = n
    while left:
        av = [i for i in range(n) if jobs[i][0] <= t and rem[i] > 0]
        if av:
            i = min(av, key=lambda x: (rem[x], x))
            rem[i] -= 1
            if rem[i] == 0:
                done[i] = t + 1
                left -= 1
        t += 1
    return done


def g_srtf(r):
    return [[[r.randint(0, 12), r.randint(1, 6)] for _ in range(r.randint(1, 7))]]


def v_srtf(tests):
    for t in tests:
        js = t["args"][0]
        assert 1 <= len(js) <= 5000
        assert all(0 <= a <= 10 ** 6 and 1 <= b <= 1000 for a, b in js)
        assert all(t["expected"][i] >= js[i][0] + js[i][1] for i in range(len(js)))


CHECKS["shortest-remaining-time-completion"] = (b_srtf, g_srtf, "exact")
VALIDATE["shortest-remaining-time-completion"] = v_srtf
