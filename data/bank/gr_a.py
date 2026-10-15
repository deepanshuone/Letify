"""Problems: greedy, scheduling and sorting greedy (deadlines, release times, machines, platforms). See data/lib.py for the registry."""
import heapq
from functools import cmp_to_key
from itertools import permutations, product

from lib import add, rnd, CHECKS, VALIDATE, gen_arr  # noqa: F401

TOPIC = "Greedy"
MOD = 1_000_000_007


# ---------------------------------------------------------------- EASY

p = add(
    id="can-finish-all-tasks-by-deadlines", title="Can Finish All Tasks by Deadlines", diff="Easy", topic=TOPIC,
    fn="canFinishAll", params=[("tasks", "int[][]")], ret="bool", cmp="exact",
    desc="<p>You have a list of tasks, where <code>tasks[i] = [duration, deadline]</code>. You start working at time <code>0</code>, do one task at a time, never pause a task once it has started, and may do the tasks in any order you like. A task that starts at time <code>s</code> finishes at <code>s + duration</code>, and that finish time must be <strong>at most</strong> its <code>deadline</code>.</p><p>Return <code>true</code> if some order lets you finish every task on time, otherwise <code>false</code>.</p><pre>tasks = [[3, 6], [2, 2], [1, 10]]  -&gt;  true\ntasks = [[2, 2], [1, 2]]           -&gt;  false</pre><p>In the first example do the second task (finish at 2), then the first (finish at 5), then the third (finish at 6). In the second example the work takes 3 time units but both deadlines are 2.</p>",
    constraints=["0 &le; tasks.length &le; 2,000", "tasks[i] = [duration, deadline]", "1 &le; duration &le; 100,000", "1 &le; deadline &le; 10<sup>9</sup>"],
    hints=["The total amount of work never changes with the order. What does change is when each individual task finishes.",
           "If a task with a late deadline is done before a task with an early deadline, could swapping the two ever make things worse?",
           "Sort the tasks by deadline (earliest first), keep a running sum of durations, and check that the running sum never exceeds the deadline of the task just added."],
    editorial=["Do the tasks in order of increasing deadline (earliest deadline first) and keep the finish time as a running sum. If the running sum ever exceeds the deadline of the current task, report <code>false</code>; if it never does, report <code>true</code>.",
               "Why this order is enough: suppose some valid order has two neighbouring tasks A then B with <code>deadline(A) &gt; deadline(B)</code>. Swapping them makes B finish earlier and lets A finish exactly when B used to finish, which is not later than B's old finish and therefore not later than <code>deadline(B) &lt; deadline(A)</code>. So repeated swaps turn any valid order into the sorted one. Sorting costs O(n log n) and the scan is O(n)."],
    time="O(n log n)", space="O(n)",
    solution='''def canFinishAll(tasks):
    t = 0
    for duration, deadline in sorted(tasks, key=lambda x: x[1]):
        t += duration
        if t > deadline:
            return False
    return True
''',
    tests=[[[[3, 6], [2, 2], [1, 10]]], [[[2, 2], [1, 2]]], [[]], [[[1, 1]]], [[[2, 1]]], [[[5, 5], [5, 10]]],
           [[[5, 5], [5, 9]]], [[[1, 3], [1, 3], [1, 3]]], [[[1, 3], [1, 3], [1, 3], [1, 3]]],
           [[[100000, 1000000000], [100000, 100000]]], [[[4, 10], [3, 7], [2, 3], [1, 1]]]],
)
_r = rnd(3001)


def _gen_deadline_tasks(r, n, slack, tight_break):
    durs = [r.randint(1, 100) for _ in range(n)]
    order = list(range(n))
    r.shuffle(order)
    t = 0
    dl = [0] * n
    for i in order:
        t += durs[i]
        dl[i] = t + r.randint(0, slack)
    tasks = [[durs[i], dl[i]] for i in range(n)]
    if tight_break:
        # make the earliest-deadline-first order fail at the very end
        k = max(range(n), key=lambda i: dl[i])
        tasks[k][1] = max(1, tasks[k][1] - sum(durs) // 2 - 1)
    return tasks


p["tests"].append([_gen_deadline_tasks(_r, 2000, 0, False)])
p["tests"].append([_gen_deadline_tasks(_r, 2000, 5, False)])
p["tests"].append([_gen_deadline_tasks(_r, 2000, 0, True)])


def b_deadlines(tasks):
    if not tasks:
        return True
    for perm in permutations(tasks):
        t = 0
        ok = True
        for d, dl in perm:
            t += d
            if t > dl:
                ok = False
                break
        if ok:
            return True
    return False


def g_deadlines(r):
    return [[[r.randint(1, 4), r.randint(1, 12)] for _ in range(r.randint(0, 6))]]


def v_deadlines(tests):
    outs = set()
    for t in tests:
        tasks = t["args"][0]
        assert 0 <= len(tasks) <= 2000
        assert all(len(x) == 2 and 1 <= x[0] <= 100000 and 1 <= x[1] <= 10 ** 9 for x in tasks)
        outs.add(t["expected"])
    assert outs == {True, False}


CHECKS["can-finish-all-tasks-by-deadlines"] = (b_deadlines, g_deadlines, "exact")
VALIDATE["can-finish-all-tasks-by-deadlines"] = v_deadlines


p = add(
    id="finish-time-with-release-times", title="Finish Time with Release Times", diff="Easy", topic=TOPIC,
    fn="finishTime", params=[("jobs", "int[][]")], ret="int", cmp="exact",
    desc="<p>A single worker has to process <code>jobs</code>, where <code>jobs[i] = [release, duration]</code>. Job <code>i</code> becomes available at time <code>release</code> and cannot start earlier. The worker handles one job at a time, never interrupts a job, and may choose the order. The worker is allowed to wait idle when nothing is available yet.</p><p>Return the earliest possible time at which all jobs are done (<code>0</code> if there are no jobs).</p><pre>jobs = [[0, 3], [10, 2], [4, 1]]  -&gt;  12\njobs = [[5, 2], [5, 3]]           -&gt;  10</pre><p>In the first example the worker does the jobs in release order: [0,3], then [4,5], then [10,12].</p>",
    constraints=["0 &le; jobs.length &le; 2,000", "jobs[i] = [release, duration]", "0 &le; release &le; 10<sup>9</sup>", "1 &le; duration &le; 10,000"],
    hints=["Whatever order you choose, the worker can never finish before the latest release time plus the duration of that job.",
           "Starting a job as soon as possible is always right, so the order is the only decision. What is the natural order if jobs only get unlocked over time?",
           "Sort by release time and simulate: <code>t = max(t, release) + duration</code> for every job."],
    editorial=["Process the jobs in order of release time. Keep the current time <code>t</code>; for each job the worker starts at <code>max(t, release)</code> (waiting if the job is not there yet) and finishes <code>duration</code> later.",
               "Why it is optimal: the finish time of any schedule is at least <code>release_j + (sum of durations of all jobs released at or after release_j)</code> for every <code>j</code>, because all those jobs can only start once <code>release_j</code> has passed. Release order achieves the maximum of these bounds exactly, so no other order can beat it. Cost is O(n log n) for the sort."],
    time="O(n log n)", space="O(n)",
    solution='''def finishTime(jobs):
    t = 0
    for release, duration in sorted(jobs):
        t = max(t, release) + duration
    return t
''',
    tests=[[[[0, 3], [10, 2], [4, 1]]], [[[5, 2], [5, 3]]], [[]], [[[0, 1]]], [[[1000000000, 10000]]],
           [[[0, 5], [0, 5], [0, 5]]], [[[0, 10], [1, 1], [2, 1]]], [[[100, 1], [0, 1], [50, 1]]],
           [[[0, 4], [3, 2], [20, 3], [21, 1]]], [[[7, 3], [7, 3], [20, 1], [8, 1]]]],
)
_r = rnd(3002)
p["tests"].append([[[_r.randint(0, 2_000_000), _r.randint(1, 5000)] for _ in range(2000)]])
p["tests"].append([[[_r.randint(0, 10 ** 9), _r.randint(1, 10000)] for _ in range(2000)]])
p["tests"].append([[[_r.randint(0, 100), _r.randint(5000, 10000)] for _ in range(2000)]])


def b_release(jobs):
    best = None
    for perm in permutations(jobs):
        t = 0
        for rel, d in perm:
            t = max(t, rel) + d
        if best is None or t < best:
            best = t
    return 0 if best is None else best


def g_release(r):
    return [[[r.randint(0, 12), r.randint(1, 5)] for _ in range(r.randint(0, 6))]]


def v_release(tests):
    for t in tests:
        jobs = t["args"][0]
        assert 0 <= len(jobs) <= 2000
        assert all(0 <= a <= 10 ** 9 and 1 <= b <= 10000 for a, b in jobs)


CHECKS["finish-time-with-release-times"] = (b_release, g_release, "exact")
VALIDATE["finish-time-with-release-times"] = v_release


p = add(
    id="latest-start-time-for-deadlines", title="Latest Start Time for All Deadlines", diff="Easy", topic=TOPIC, tier="extra",
    fn="latestStart", params=[("tasks", "int[][]")], ret="int", cmp="exact",
    desc="<p>You must complete every task in <code>tasks</code>, where <code>tasks[i] = [duration, deadline]</code>. You begin working at some integer time <code>S &ge; 0</code>, then work without any break, one task at a time in an order you choose, and no task is interrupted. Every task must finish at or before its deadline.</p><p>Return the <strong>largest</strong> start time <code>S</code> for which this is still possible, or <code>-1</code> if even starting at time <code>0</code> is not enough.</p><pre>tasks = [[3, 10], [2, 6]]  -&gt;  4\ntasks = [[5, 4]]           -&gt;  -1</pre><p>In the first example start at 4: the second task ends at 6 (deadline 6) and the first ends at 9 (deadline 10). Starting at 5 would make the second task end at 7.</p>",
    constraints=["1 &le; tasks.length &le; 2,000", "1 &le; duration &le; 100,000", "1 &le; deadline &le; 10<sup>9</sup>"],
    hints=["First fix the order. For a given order, each task gives an upper bound on <code>S</code>: <code>S + (work up to and including it) &le; deadline</code>.",
           "The best order is the one that makes the tightest of those bounds as loose as possible. Think about which task should come first.",
           "Sort by deadline. The answer is the minimum over all tasks of <code>deadline - (prefix sum of durations)</code>, or <code>-1</code> when that minimum is negative."],
    editorial=["With tasks done back to back in a fixed order, task <code>i</code> ends at <code>S + P_i</code> where <code>P_i</code> is the sum of the durations up to and including it. So the start time is limited by <code>S &le; deadline_i - P_i</code> for every task, and the largest valid <code>S</code> is the minimum of these slacks.",
               "Sorting by deadline (earliest first) maximizes that minimum slack, by the same exchange argument that makes earliest-deadline-first optimal for feasibility: moving a task with a later deadline in front of one with an earlier deadline can only shrink the slack of the earlier one. If the minimum slack is negative no start time works, so the answer is <code>-1</code>. Time O(n log n)."],
    time="O(n log n)", space="O(n)",
    solution='''def latestStart(tasks):
    best = None
    t = 0
    for duration, deadline in sorted(tasks, key=lambda x: x[1]):
        t += duration
        slack = deadline - t
        if best is None or slack < best:
            best = slack
    return best if best >= 0 else -1
''',
    tests=[[[[3, 10], [2, 6]]], [[[5, 4]]], [[[5, 5]]], [[[1, 1000000000]]], [[[2, 2], [1, 2]]],
           [[[4, 10], [3, 7], [2, 3], [1, 1]]], [[[4, 20], [3, 20], [2, 20]]], [[[3, 3], [3, 6], [3, 9]]],
           [[[3, 3], [3, 6], [3, 8]]], [[[100000, 1000000000], [100000, 100000]]]],
)
_r = rnd(3003)
p["tests"].append([_gen_deadline_tasks(_r, 2000, 10, False)])
p["tests"].append([[[_r.randint(1, 100000), _r.randint(10 ** 8, 10 ** 9)] for _ in range(2000)]])
p["tests"].append([_gen_deadline_tasks(_r, 2000, 0, True)])


def b_latest(tasks):
    best = -1
    for perm in permutations(tasks):
        t = 0
        s = None
        for d, dl in perm:
            t += d
            v = dl - t
            s = v if s is None else min(s, v)
        if s >= 0:
            best = max(best, s)
    return best


def g_latest(r):
    return [[[r.randint(1, 4), r.randint(1, 14)] for _ in range(r.randint(1, 6))]]


def v_latest(tests):
    seen_neg = seen_pos = False
    for t in tests:
        tasks = t["args"][0]
        assert 1 <= len(tasks) <= 2000
        assert all(1 <= a <= 100000 and 1 <= b <= 10 ** 9 for a, b in tasks)
        seen_neg |= t["expected"] == -1
        seen_pos |= t["expected"] >= 0
    assert seen_neg and seen_pos


CHECKS["latest-start-time-for-deadlines"] = (b_latest, g_latest, "exact")
VALIDATE["latest-start-time-for-deadlines"] = v_latest


# ---------------------------------------------------------------- MEDIUM

p = add(
    id="platforms-with-cleaning-gap", title="Platforms with a Cleaning Gap", diff="Medium", topic=TOPIC,
    fn="minPlatforms", params=[("arrivals", "int[]"), ("departures", "int[]"), ("gap", "int")], ret="int", cmp="exact",
    desc="<p>A railway station timetable is given by two arrays of the same length: train <code>i</code> arrives at time <code>arrivals[i]</code> and leaves at time <code>departures[i]</code>, with <code>arrivals[i] &le; departures[i]</code>. Times are whole minutes and the trains are listed in no particular order.</p><p>After a train leaves, its platform must be cleaned for <code>gap</code> more minutes. So a train occupies its platform for the whole closed interval <code>[arrival, departure + gap]</code>, and the platform can be given to another train only from time <code>departure + gap + 1</code> on. In particular, with <code>gap = 0</code> a train arriving at the very minute another one leaves still needs a different platform.</p><p>Return the minimum number of platforms that lets every train stop without waiting.</p><pre>arrivals = [900, 940, 950, 1100, 1500, 1800], departures = [910, 1200, 1120, 1130, 1900, 2000], gap = 0  -&gt;  3\n\narrivals = [1, 20], departures = [5, 25], gap = 10  -&gt;  1\narrivals = [1, 20], departures = [5, 25], gap = 15  -&gt;  2</pre><p>In the first example three trains are in the station at time 1100. In the last two, the first train blocks its platform until minute 15 (gap 10) or minute 20 (gap 15), and the second train arrives at minute 20: it fits only in the first case.</p>",
    constraints=["0 &le; arrivals.length = departures.length &le; 3,000", "0 &le; arrivals[i] &le; departures[i] &le; 10<sup>9</sup> - 100,000", "0 &le; gap &le; 100,000"],
    hints=["The answer equals the largest number of trains that need a platform at the same moment, where a train needs it until <code>departure + gap</code>.",
           "That maximum can only increase at an arrival time. Look at the arrivals and the (shifted) release times separately, each in increasing order, instead of at the pairs.",
           "Sort the arrivals and the values <code>departure + gap</code>. Walk through the arrivals with a pointer into the release times: if the next arrival is at or before the earliest unreleased platform, a new platform is needed; otherwise a platform is released."],
    editorial=["Replace every departure by the time its platform becomes available again, <code>departure + gap</code>; the platform is busy on the closed interval <code>[arrival, departure + gap]</code>. Sort the arrival times and these release times independently; the pairing between them does not matter for counting how many platforms are busy at a moment. Use two pointers <code>i</code> (arrivals) and <code>j</code> (releases) and a counter <code>cur</code> of busy platforms. If <code>arrivals[i] &le; release[j]</code>, the next event is an arrival (a tie goes to the arrival because the platform is still busy at that minute): increment <code>cur</code>, record the maximum and advance <code>i</code>. Otherwise a platform became free strictly before the next arrival: decrement <code>cur</code> and advance <code>j</code>.",
               "The maximum value of <code>cur</code> is the number of platforms needed, because intervals on a line can always be coloured with as many colours as the maximum overlap. Sorting dominates: O(n log n) time, O(n) space for the sorted copies."],
    time="O(n log n)", space="O(n)",
    solution='''def minPlatforms(arrivals, departures, gap):
    arr = sorted(arrivals)
    rel = sorted(d + gap for d in departures)
    n = len(arr)
    i = j = cur = best = 0
    while i < n:
        if arr[i] <= rel[j]:
            cur += 1
            best = max(best, cur)
            i += 1
        else:
            cur -= 1
            j += 1
    return best
''',
    tests=[[[900, 940, 950, 1100, 1500, 1800], [910, 1200, 1120, 1130, 1900, 2000], 0], [[1, 20], [5, 25], 10], [[1, 20], [5, 25], 15],
           [[], [], 5], [[7], [7], 0], [[1, 2, 3], [1, 2, 3], 0], [[1, 1, 1, 1], [1, 1, 1, 1], 3],
           [[1, 3, 5], [2, 4, 6], 0], [[1, 3, 5], [2, 4, 6], 1], [[1, 3, 5], [2, 4, 6], 2],
           [[0, 10], [9, 20], 0], [[0, 10], [9, 20], 1], [[0, 10], [10, 20], 0],
           [[5, 1, 9, 3], [6, 4, 12, 8], 2], [[0, 900000000], [899900000, 900000000], 100000]],
)
_r = rnd(3004)


def _gen_trains(r, n, tmax, maxstay):
    a = [r.randint(0, tmax) for _ in range(n)]
    d = [min(10 ** 9 - 100_000, x + r.randint(0, maxstay)) for x in a]
    return a, d


for _n, _tm, _ms, _g in [(3000, 1_000_000, 3000, 250), (3000, 10 ** 9 - 120_000, 10_000_000, 99_999), (3000, 5000, 5, 3)]:
    _a, _d = _gen_trains(_r, _n, _tm, _ms)
    p["tests"].append([_a, _d, _g])


def b_platforms(arrivals, departures, gap):
    best = 0
    for t in arrivals:
        c = sum(1 for a, d in zip(arrivals, departures) if a <= t <= d + gap)
        best = max(best, c)
    return best


def g_platforms(r):
    n = r.randint(0, 7)
    a = [r.randint(0, 12) for _ in range(n)]
    d = [x + r.randint(0, 5) for x in a]
    return [a, d, r.randint(0, 4)]


def v_platforms(tests):
    for t in tests:
        a, d, g = t["args"]
        assert len(a) == len(d) <= 3000
        assert all(0 <= x <= y <= 10 ** 9 - 100_000 for x, y in zip(a, d))
        assert 0 <= g <= 100_000


CHECKS["platforms-with-cleaning-gap"] = (b_platforms, g_platforms, "exact")
VALIDATE["platforms-with-cleaning-gap"] = v_platforms


p = add(
    id="minimize-maximum-lateness", title="Minimize Maximum Lateness", diff="Medium", topic=TOPIC,
    fn="minMaxLateness", params=[("jobs", "int[][]")], ret="int", cmp="exact",
    desc="<p>A single machine must run all <code>jobs</code>, where <code>jobs[i] = [duration, due]</code>. It starts at time <code>0</code>, runs one job at a time without interruption and without idle gaps, in an order of your choice. If job <code>i</code> finishes at time <code>f</code>, its <strong>lateness</strong> is <code>max(0, f - due)</code>.</p><p>Return the smallest possible value of the <em>largest</em> lateness over all jobs (<code>0</code> means every job can be on time, and also the answer for no jobs).</p><pre>jobs = [[3, 6], [2, 4]]  -&gt;  0\njobs = [[4, 3], [2, 3]]  -&gt;  3</pre><p>In the second example, whichever job goes second finishes at time 6 and is 3 late.</p>",
    constraints=["0 &le; jobs.length &le; 2,000", "1 &le; duration &le; 1,000", "0 &le; due &le; 10<sup>9</sup>"],
    hints=["Total work is fixed, so the last job always finishes at the same time. The question is which job should be that last one.",
           "Take two neighbouring jobs A then B. If B is due earlier than A, what happens to the maximum lateness of the pair if you swap them?",
           "Run the jobs in increasing order of due time (earliest due date first), then take the largest <code>max(0, finish - due)</code>."],
    editorial=["Sort the jobs by due time and simulate. This is the earliest-due-date rule and it is optimal for this objective.",
               "Exchange argument: suppose neighbouring jobs A then B have <code>due(A) &gt; due(B)</code>. Let them start at time <code>s</code>. Before the swap the lateness values are <code>s + a - due(A)</code> and <code>s + a + b - due(B)</code>. After swapping they are <code>s + b - due(B)</code> and <code>s + a + b - due(A)</code>. The second new value is smaller than the old <code>s + a + b - due(B)</code> because <code>due(A) &gt; due(B)</code>, and the first new value is smaller than it too. So the maximum of the pair never grows, and repeated swaps reach the sorted order. Time O(n log n)."],
    time="O(n log n)", space="O(n)",
    solution='''def minMaxLateness(jobs):
    t = 0
    worst = 0
    for duration, due in sorted(jobs, key=lambda x: x[1]):
        t += duration
        worst = max(worst, t - due)
    return worst
''',
    tests=[[[[3, 6], [2, 4]]], [[[4, 3], [2, 3]]], [[]], [[[5, 0]]], [[[1, 1000000000]]],
           [[[1, 9], [2, 8], [3, 15], [4, 6], [3, 14], [2, 9]]], [[[2, 2], [2, 2], [2, 2]]],
           [[[10, 1], [1, 2], [1, 3]]], [[[3, 100], [3, 100], [3, 100]]], [[[1, 0], [1, 0], [1, 0], [1, 0]]]],
)
_r = rnd(3005)
p["tests"].append([[[_r.randint(1, 1000), _r.randint(0, 1_000_000)] for _ in range(2000)]])
p["tests"].append([[[_r.randint(1, 1000), _r.randint(0, 2_000_000)] for _ in range(2000)]])
p["tests"].append([[[_r.randint(1, 1000), _r.randint(0, 10 ** 9)] for _ in range(2000)]])


def b_lateness(jobs):
    if not jobs:
        return 0
    best = None
    for perm in permutations(jobs):
        t = 0
        worst = 0
        for d, due in perm:
            t += d
            worst = max(worst, t - due)
        if best is None or worst < best:
            best = worst
    return best


def g_lateness(r):
    return [[[r.randint(1, 5), r.randint(0, 14)] for _ in range(r.randint(0, 6))]]


def v_lateness(tests):
    pos = zero = False
    for t in tests:
        jobs = t["args"][0]
        assert 0 <= len(jobs) <= 2000
        assert all(1 <= a <= 1000 and 0 <= b <= 10 ** 9 for a, b in jobs)
        pos |= t["expected"] > 0
        zero |= t["expected"] == 0
    assert pos and zero


CHECKS["minimize-maximum-lateness"] = (b_lateness, g_lateness, "exact")
VALIDATE["minimize-maximum-lateness"] = v_lateness


p = add(
    id="min-weighted-completion-time", title="Minimum Weighted Completion Time", diff="Medium", topic=TOPIC, tier="extra",
    fn="minWeightedCompletion", params=[("jobs", "int[][]")], ret="int", cmp="exact",
    desc="<p>A single machine runs <code>jobs</code>, where <code>jobs[i] = [duration, weight]</code>, one at a time without pauses, starting at time <code>0</code> and in any order you choose. If job <code>i</code> finishes at time <code>C<sub>i</sub></code>, it costs <code>weight &times; C<sub>i</sub></code>.</p><p>Return the minimum possible total cost, taken modulo <code>1,000,000,007</code> (the minimum is found over the exact values; only the final number is reduced). Return <code>0</code> for no jobs.</p><pre>jobs = [[3, 1], [1, 2]]  -&gt;  6</pre><p>Running the second job first costs <code>2 &times; 1 + 1 &times; 4 = 6</code>; the other order costs <code>1 &times; 3 + 2 &times; 4 = 11</code>.</p>",
    constraints=["0 &le; jobs.length &le; 2,000", "1 &le; duration, weight &le; 100"],
    hints=["Compare just two jobs A and B. Work out the cost of the pair for the order A, B and for B, A, and see what the difference depends on.",
           "The two costs differ by <code>weight(A) &times; duration(B)</code> versus <code>weight(B) &times; duration(A)</code>. Rewrite this as a comparison of two ratios.",
           "Sort by <code>duration / weight</code> ascending (compare with cross-multiplication to avoid fractions), then accumulate time and cost."],
    editorial=["For two neighbouring jobs A, B starting at time <code>s</code>, the other jobs are unaffected by their order. Doing A first adds <code>w<sub>A</sub>(s + d<sub>A</sub>) + w<sub>B</sub>(s + d<sub>A</sub> + d<sub>B</sub>)</code>, while B first adds <code>w<sub>B</sub>(s + d<sub>B</sub>) + w<sub>A</sub>(s + d<sub>A</sub> + d<sub>B</sub>)</code>. A first is better exactly when <code>w<sub>B</sub> d<sub>A</sub> &lt; w<sub>A</sub> d<sub>B</sub></code>, i.e. <code>d<sub>A</sub> / w<sub>A</sub> &lt; d<sub>B</sub> / w<sub>B</sub></code>.",
               "So sort the jobs by <code>duration / weight</code> in increasing order (Smith's rule) and sum <code>weight &times; finish</code>. Jobs with equal ratios can be placed in any order without changing the total. The exact total can reach about 10<sup>11</sup>, which is why the problem asks for it modulo 10<sup>9</sup>+7; Python integers do not overflow so the reduction happens only at the end. Time O(n log n)."],
    time="O(n log n)", space="O(n)",
    solution='''from functools import cmp_to_key


def minWeightedCompletion(jobs):
    MOD = 1_000_000_007
    order = sorted(jobs, key=cmp_to_key(lambda a, b: a[0] * b[1] - b[0] * a[1]))
    t = 0
    total = 0
    for duration, weight in order:
        t += duration
        total += weight * t
    return total % MOD
''',
    tests=[[[[3, 1], [1, 2]]], [[]], [[[5, 7]]], [[[2, 2], [4, 4], [1, 1]]], [[[1, 1], [1, 1], [1, 1]]],
           [[[10, 1], [1, 10]]], [[[1, 100], [100, 1]]], [[[3, 6], [2, 3], [5, 4], [4, 8]]],
           [[[100, 100]] * 10], [[[7, 3], [14, 6], [21, 9], [1, 1]]]],
)
_r = rnd(3006)
p["tests"].append([[[_r.randint(1, 100), _r.randint(1, 100)] for _ in range(2000)]])
p["tests"].append([[[100, _r.randint(1, 100)] for _ in range(2000)]])
p["tests"].append([[[_r.randint(1, 100), 100] for _ in range(2000)]])


def b_weighted(jobs):
    best = None
    for perm in permutations(jobs):
        t = 0
        total = 0
        for d, w in perm:
            t += d
            total += w * t
        if best is None or total < best:
            best = total
    return 0 if best is None else best % MOD


def g_weighted(r):
    return [[[r.randint(1, 6), r.randint(1, 6)] for _ in range(r.randint(0, 6))]]


def v_weighted(tests):
    big = False
    for t in tests:
        jobs = t["args"][0]
        assert 0 <= len(jobs) <= 2000
        assert all(1 <= a <= 100 and 1 <= b <= 100 for a, b in jobs)
        big |= t["expected"] > 10 ** 7
    assert big


CHECKS["min-weighted-completion-time"] = (b_weighted, g_weighted, "exact")
VALIDATE["min-weighted-completion-time"] = v_weighted


p = add(
    id="min-total-completion-time-k-machines", title="Minimum Total Completion Time on K Machines", diff="Medium", topic=TOPIC, tier="extra",
    fn="minTotalCompletion", params=[("durations", "int[]"), ("k", "int")], ret="int", cmp="exact",
    desc="<p>There are <code>k</code> identical machines and <code>durations[i]</code> is the running time of job <code>i</code>. Every job runs on exactly one machine without interruption; a machine runs one job at a time, starting at time <code>0</code> and never idling between its jobs. You decide which machine takes each job and in what order.</p><p>The <strong>completion time</strong> of a job is the time at which it finishes. Return the minimum possible sum of the completion times of all jobs (<code>0</code> if there are no jobs).</p><pre>durations = [3, 1, 2], k = 2  -&gt;  7</pre><p>Run <code>1</code> then <code>3</code> on one machine (finishing at 1 and 4) and <code>2</code> on the other (finishing at 2): 1 + 4 + 2 = 7.</p>",
    constraints=["0 &le; durations.length &le; 2,000", "1 &le; durations[i] &le; 100", "1 &le; k &le; 2,000"],
    hints=["For a single machine the jobs should simply run from shortest to longest. Why?",
           "On one machine the last job's duration is counted once, the second to last twice, and so on: a job with <code>m</code> jobs behind it (including itself) is counted <code>m</code> times. With k machines you have k slots of each multiplicity.",
           "Sort the durations in decreasing order. The k longest jobs get multiplier 1 (they run last on their machines), the next k get multiplier 2, and so on: the job at sorted index <code>i</code> contributes <code>duration * (i // k + 1)</code>."],
    editorial=["The duration of a job is added to the completion time of itself and of every job after it on the same machine. So a job that has <code>m - 1</code> jobs after it on its machine is counted <code>m</code> times in the total. Every machine offers one position with multiplier 1 (its last job), one with multiplier 2, and so on, so the multiset of available multipliers is <code>k</code> copies of 1, <code>k</code> copies of 2, ... Each multiplier is used from 1 upwards, because filling a larger multiplier while a smaller one is free is never better.",
               "To minimize the sum of <code>duration &times; multiplier</code>, pair the largest durations with the smallest multipliers (rearrangement inequality). After sorting durations in decreasing order, index <code>i</code> gets multiplier <code>i // k + 1</code>. Time O(n log n); the largest total is below 2.1&middot;10<sup>8</sup> (k = 1, n = 2000)."],
    time="O(n log n)", space="O(n)",
    solution='''def minTotalCompletion(durations, k):
    total = 0
    for i, d in enumerate(sorted(durations, reverse=True)):
        total += d * (i // k + 1)
    return total
''',
    tests=[[[3, 1, 2], 2], [[], 3], [[5], 1], [[5], 4], [[1, 2, 3, 4], 1], [[1, 2, 3, 4], 2], [[1, 2, 3, 4], 4],
           [[4, 4, 4, 4, 4, 4], 3], [[1, 1, 1, 100, 100, 100, 50], 2], [[7, 3, 9, 1, 5], 3], [[100] * 5, 5]],
)
_r = rnd(3007)
p["tests"].append([[_r.randint(1, 100) for _ in range(2000)], 1])
p["tests"].append([[_r.randint(1, 100) for _ in range(2000)], 7])
p["tests"].append([[_r.randint(1, 100) for _ in range(2000)], 2000])


def b_kmachines(durations, k):
    n = len(durations)
    if n == 0:
        return 0
    best = None
    for assign in product(range(k), repeat=n):
        total = 0
        for m in range(k):
            jobs = [durations[i] for i in range(n) if assign[i] == m]
            lo = None
            for perm in permutations(jobs):
                t = c = 0
                for d in perm:
                    c += d
                    t += c
                if lo is None or t < lo:
                    lo = t
            total += lo or 0
        if best is None or total < best:
            best = total
    return best


def g_kmachines(r):
    return [[r.randint(1, 6) for _ in range(r.randint(0, 5))], r.randint(1, 3)]


def v_kmachines(tests):
    for t in tests:
        dur, k = t["args"]
        assert 0 <= len(dur) <= 2000 and 1 <= k <= 2000
        assert all(1 <= x <= 100 for x in dur)


CHECKS["min-total-completion-time-k-machines"] = (b_kmachines, g_kmachines, "exact")
VALIDATE["min-total-completion-time-k-machines"] = v_kmachines


p = add(
    id="prep-then-cook-min-finish-time", title="Prep Then Cook Minimum Finish Time", diff="Medium", topic=TOPIC, tier="extra",
    fn="minFinishTime", params=[("dishes", "int[][]")], ret="int", cmp="exact",
    desc="<p>A single chef must make every dish in <code>dishes</code>, where <code>dishes[i] = [prep, cook]</code>. The chef prepares the dishes one after another with no breaks, starting at time <code>0</code>, in an order of the chef's choosing. Preparing dish <code>i</code> takes <code>prep</code> time and needs the chef the whole time. As soon as its preparation is done the dish goes into its own oven and takes <code>cook</code> more time; there are enough ovens for all dishes at once, and the chef is free to start preparing the next dish immediately.</p><p>Return the earliest time at which all dishes are finished cooking.</p><pre>dishes = [[2, 5], [3, 1]]  -&gt;  7</pre><p>Prepare the long-cooking dish first: it is in the oven from time 2 and done at 7, while the second dish is prepared during 2..5 and done at 6. The other order ends at 10.</p>",
    constraints=["1 &le; dishes.length &le; 2,000", "1 &le; prep &le; 1,000", "1 &le; cook &le; 1,000,000"],
    hints=["The chef's own work always ends at the same moment, the sum of all prep times. Only the cooking tails differ.",
           "Dish i is done at (time its prep ends) + cook_i. Which dishes should get the earliest prep-end times: the ones with long or short cook times?",
           "Prepare dishes in decreasing order of cook time and track <code>max(prep end + cook)</code> over all dishes."],
    editorial=["The finish time is <code>max over dishes of (prep end of the dish + its cook time)</code>. The prep ends are the prefix sums of the prep times in the chosen order, so the total prep time is paid by the last dish whichever it is, and the real decision is which dishes get the early finish slots.",
               "Exchange argument: if dish A with a smaller cook time is prepared directly before dish B with a larger cook time, swapping them leaves the end of the pair unchanged, makes B finish earlier, and A's new finish <code>(s + prep<sub>B</sub> + prep<sub>A</sub> + cook<sub>A</sub>)</code> is not larger than B's old finish <code>s + prep<sub>A</sub> + prep<sub>B</sub> + cook<sub>B</sub></code>. So sort by cook time descending and scan once. Time O(n log n)."],
    solution='''def minFinishTime(dishes):
    t = 0
    best = 0
    for prep, cook in sorted(dishes, key=lambda x: -x[1]):
        t += prep
        best = max(best, t + cook)
    return best
''',
    time="O(n log n)", space="O(n)",
    tests=[[[[2, 5], [3, 1]]], [[[4, 4]]], [[[1, 1], [1, 1], [1, 1]]], [[[5, 1], [5, 1], [5, 1]]],
           [[[1, 100], [1, 100], [1, 100]]], [[[3, 10], [2, 2], [4, 7], [1, 9]]], [[[1000, 1], [1, 1000000]]],
           [[[2, 3], [2, 3]]], [[[1, 5], [2, 4], [3, 3], [4, 2], [5, 1]]], [[[5, 1], [4, 2], [3, 3], [2, 4], [1, 5]]]],
)
_r = rnd(3008)
p["tests"].append([[[_r.randint(1, 1000), _r.randint(1, 1_000_000)] for _ in range(2000)]])
p["tests"].append([[[_r.randint(1, 1000), _r.randint(1, 1000)] for _ in range(2000)]])
p["tests"].append([[[_r.randint(1, 10), _r.randint(1, 20000)] for _ in range(2000)]])


def b_prepcook(dishes):
    best = None
    for perm in permutations(dishes):
        t = 0
        fin = 0
        for prep, cook in perm:
            t += prep
            fin = max(fin, t + cook)
        if best is None or fin < best:
            best = fin
    return best


def g_prepcook(r):
    return [[[r.randint(1, 5), r.randint(1, 9)] for _ in range(r.randint(1, 6))]]


def v_prepcook(tests):
    for t in tests:
        d = t["args"][0]
        assert 1 <= len(d) <= 2000
        assert all(1 <= a <= 1000 and 1 <= b <= 1_000_000 for a, b in d)


CHECKS["prep-then-cook-min-finish-time"] = (b_prepcook, g_prepcook, "exact")
VALIDATE["prep-then-cook-min-finish-time"] = v_prepcook


p = add(
    id="max-visitors-matched-to-guides", title="Maximum Visitors Matched to Guides", diff="Medium", topic=TOPIC,
    fn="maxMatched", params=[("visitors", "int[]"), ("guides", "int[][]")], ret="int", cmp="exact",
    desc="<p>A museum has several guides. Guide <code>j</code> is on duty during the closed time range <code>guides[j] = [start, end]</code> and can serve at most one visitor. Visitor <code>i</code> arrives at time <code>visitors[i]</code> and can be served only by a guide who is on duty at that moment, that is, <code>start &le; visitors[i] &le; end</code>. A visitor is served by at most one guide.</p><p>Return the largest number of visitors that can be served.</p><pre>visitors = [1, 2, 3], guides = [[1, 2], [2, 3]]  -&gt;  2\nvisitors = [4, 4],    guides = [[1, 5]]          -&gt;  1</pre>",
    constraints=["0 &le; visitors.length &le; 3,000", "0 &le; guides.length &le; 2,000", "0 &le; visitors[i] &le; 10<sup>9</sup>", "guides[j] = [start, end] with 0 &le; start &le; end &le; 10<sup>9</sup>"],
    hints=["This is a maximum matching between visitors and guides, but the structure (points and intervals on a line) makes a greedy possible.",
           "Process visitors from the earliest arrival. Among the guides who could serve this visitor, which one is the least useful for future visitors?",
           "Sort visitors and guides. For each visitor, add every guide that has started into a min-heap keyed by end time, discard guides whose end is before the visitor, and match the visitor with the guide that ends soonest."],
    editorial=["Sweep over the visitors in increasing arrival time and keep a min-heap of the end times of all guides that have already started (<code>start &le; visitor</code>) and have not been used. Remove from the heap the guides whose end is before the current visitor (they can serve nobody from now on). If the heap is not empty, match the visitor with the guide that ends earliest and count one.",
               "Choosing the soonest-ending guide is safe: every later visitor arrives no earlier than this one, so a guide who ends later can serve a superset of the later visitors the soonest-ending guide could. Leaving that more flexible guide for later never loses a match. If the heap is empty, this visitor cannot be served by anyone remaining and is skipped, which is also optimal because skipping costs nothing for the others. Time O((n + m) log(n + m))."],
    time="O(n log n + m log m)", space="O(m)",
    solution='''import heapq


def maxMatched(visitors, guides):
    visitors = sorted(visitors)
    guides = sorted(guides)
    heap = []
    j = 0
    count = 0
    for t in visitors:
        while j < len(guides) and guides[j][0] <= t:
            heapq.heappush(heap, guides[j][1])
            j += 1
        while heap and heap[0] < t:
            heapq.heappop(heap)
        if heap:
            heapq.heappop(heap)
            count += 1
    return count
''',
    tests=[[[1, 2, 3], [[1, 2], [2, 3]]], [[4, 4], [[1, 5]]], [[], []], [[5], []], [[], [[1, 2]]], [[3], [[3, 3]]],
           [[3], [[4, 6]]], [[1, 5, 9], [[0, 10], [0, 10], [0, 10]]], [[1, 2, 3, 4], [[1, 4], [1, 1], [4, 4]]],
           [[2, 2, 2], [[1, 2], [2, 2], [2, 3], [5, 6]]], [[0, 10 ** 9], [[0, 10 ** 9], [10 ** 9, 10 ** 9]]],
           [[1, 3, 5, 7], [[1, 3], [3, 5], [5, 7], [7, 9]]]],
)
_r = rnd(3009)


def _gen_visit(r, nv, ng, tmax, maxlen):
    v = [r.randint(0, tmax) for _ in range(nv)]
    g = []
    for _ in range(ng):
        s = r.randint(0, tmax)
        g.append([s, min(10 ** 9, s + r.randint(0, maxlen))])
    return [v, g]


p["tests"].append(_gen_visit(_r, 3000, 2000, 100_000, 100))
p["tests"].append(_gen_visit(_r, 3000, 2000, 10 ** 9 - 2_000_000, 2_000_000))
p["tests"].append(_gen_visit(_r, 2500, 2000, 3000, 2))


def b_matched(visitors, guides):
    best = 0
    m = len(guides)

    def go(i, used):
        nonlocal best
        if i == len(visitors):
            best = max(best, bin(used).count("1"))
            return
        go(i + 1, used)
        for j in range(m):
            if not (used >> j) & 1 and guides[j][0] <= visitors[i] <= guides[j][1]:
                go(i + 1, used | (1 << j))

    go(0, 0)
    return best


def g_matched(r):
    v = [r.randint(0, 10) for _ in range(r.randint(0, 6))]
    g = []
    for _ in range(r.randint(0, 6)):
        s = r.randint(0, 10)
        g.append([s, s + r.randint(0, 4)])
    return [v, g]


def v_matched(tests):
    for t in tests:
        v, g = t["args"]
        assert len(v) <= 3000 and len(g) <= 2000
        assert all(0 <= x <= 10 ** 9 for x in v)
        assert all(0 <= a <= b <= 10 ** 9 for a, b in g)


CHECKS["max-visitors-matched-to-guides"] = (b_matched, g_matched, "exact")
VALIDATE["max-visitors-matched-to-guides"] = v_matched


# ---------------------------------------------------------------- HARD

p = add(
    id="two-machine-flow-shop-makespan", title="Two-Stage Pipeline Minimum Makespan", diff="Hard", topic=TOPIC, tier="extra",
    fn="minMakespan", params=[("jobs", "int[][]")], ret="int", cmp="exact",
    desc="<p>A workshop has two machines, A and B. Every job <code>jobs[i] = [a, b]</code> must first be processed on machine A for <code>a</code> time units and, once that is finished, on machine B for <code>b</code> time units. Each machine handles one job at a time without interruption. Machine B can start a job only after A has completely finished it, and it may sit idle while waiting. Both machines process the jobs in the <strong>same order</strong>, which you choose (for two machines this is without loss of optimality). Everything starts at time <code>0</code>.</p><p>Return the minimum possible time at which the last job leaves machine B.</p><pre>jobs = [[3, 2], [1, 4]]  -&gt;  7</pre><p>Order [1,4] then [3,2]: A finishes them at 1 and 4; B runs the first during 1..5 and the second during 5..7. The other order gives 9.</p>",
    constraints=["1 &le; jobs.length &le; 2,000", "1 &le; a, b &le; 1,000"],
    hints=["With a fixed order the finish times are easy to simulate: <code>tA += a; tB = max(tB, tA) + b</code>. The whole difficulty is choosing the order.",
           "You want machine B to start working as early as possible and never starve. Which jobs should go first: those that are quick on A, or those that are slow on A?",
           "Johnson's rule. Jobs with <code>a &lt; b</code> go first, sorted by <code>a</code> ascending; the remaining jobs (<code>a &ge; b</code>) go afterwards, sorted by <code>b</code> descending."],
    editorial=["This is the classic two-machine flow shop, solved by Johnson's rule. Split the jobs into group 1 (<code>a &lt; b</code>) and group 2 (<code>a &ge; b</code>). Run group 1 first in increasing order of <code>a</code>, so machine B gets fed as early as possible, then group 2 in decreasing order of <code>b</code>, so the jobs that are short on B and cannot keep it busy are placed last, when machine A is already finished and only B's tail remains.",
               "To get the answer, simulate the chosen order: <code>tA += a; tB = max(tB, tA) + b</code> for each job, and return <code>tB</code>. The correctness proof is an exchange argument on neighbouring jobs: job i should precede job j whenever <code>min(a<sub>i</sub>, b<sub>j</sub>) &le; min(a<sub>j</sub>, b<sub>i</sub>)</code>, and Johnson's order realises exactly that. Sorting dominates: O(n log n)."],
    time="O(n log n)", space="O(n)",
    solution='''def minMakespan(jobs):
    first = sorted((j for j in jobs if j[0] < j[1]), key=lambda j: j[0])
    second = sorted((j for j in jobs if j[0] >= j[1]), key=lambda j: -j[1])
    ta = tb = 0
    for a, b in first + second:
        ta += a
        tb = max(tb, ta) + b
    return tb
''',
    tests=[[[[3, 2], [1, 4]]], [[[5, 5]]], [[[1, 1], [1, 1], [1, 1]]], [[[2, 5], [4, 1], [3, 3]]],
           [[[10, 1], [10, 1], [10, 1]]], [[[1, 10], [1, 10], [1, 10]]], [[[3, 6], [4, 2], [2, 9], [8, 3], [5, 5]]],
           [[[1000, 1000], [1, 1]]], [[[1, 1000], [1000, 1]]], [[[7, 3], [2, 8], [6, 6], [1, 2], [9, 4], [3, 7]]]],
)
_r = rnd(3010)
p["tests"].append([[[_r.randint(1, 1000), _r.randint(1, 1000)] for _ in range(2000)]])
p["tests"].append([[[_r.randint(1, 100), _r.randint(50, 150)] for _ in range(2000)]])
p["tests"].append([[[_r.randint(50, 150), _r.randint(1, 100)] for _ in range(2000)]])


def b_flowshop(jobs):
    best = None
    for perm in permutations(jobs):
        ta = tb = 0
        for a, b in perm:
            ta += a
            tb = max(tb, ta) + b
        if best is None or tb < best:
            best = tb
    return best


def g_flowshop(r):
    return [[[r.randint(1, 8), r.randint(1, 8)] for _ in range(r.randint(1, 7))]]


def v_flowshop(tests):
    for t in tests:
        jobs = t["args"][0]
        assert 1 <= len(jobs) <= 2000
        assert all(1 <= a <= 1000 and 1 <= b <= 1000 for a, b in jobs)


CHECKS["two-machine-flow-shop-makespan"] = (b_flowshop, g_flowshop, "exact")
VALIDATE["two-machine-flow-shop-makespan"] = v_flowshop


p = add(
    id="preemptive-jobs-meet-deadlines", title="Preemptive Jobs Meeting Deadlines", diff="Hard", topic=TOPIC, tier="extra",
    fn="canScheduleAll", params=[("jobs", "int[][]")], ret="bool", cmp="exact",
    desc="<p>One machine must run <code>jobs</code>, where <code>jobs[i] = [release, work, deadline]</code>. Time is divided into unit slots, slot <code>t</code> being the interval from <code>t</code> to <code>t + 1</code>. In each slot the machine runs at most one job, and job <code>i</code> may only occupy slots <code>t</code> with <code>release &le; t &lt; deadline</code>. A job may be paused and resumed any number of times, and it needs exactly <code>work</code> slots in total.</p><p>Return <code>true</code> if every job can get all its slots, otherwise <code>false</code>.</p><pre>jobs = [[0, 2, 4], [1, 1, 2]]  -&gt;  true\njobs = [[0, 3, 4], [1, 2, 3]]  -&gt;  false</pre><p>In the first example the second job takes slot 1 and the first job takes slots 0 and 2. In the second example the second job must use slots 1 and 2, which leaves only slots 0 and 3 for the first job, one short.</p>",
    constraints=["0 &le; jobs.length &le; 1,500", "jobs[i] = [release, work, deadline]", "0 &le; release &lt; deadline &le; 10<sup>7</sup>", "1 &le; work &le; 10<sup>7</sup>"],
    hints=["Simulate time slot by slot (jumping over idle stretches). At every moment you must decide which of the released, unfinished jobs to run.",
           "Always running the job that is most urgent is the natural choice, and a newly released job may deserve to interrupt the current one.",
           "Earliest Deadline First: keep a heap of (deadline, remaining work) for released jobs; run the top one until it finishes or until the next release, whichever comes first, and report <code>false</code> if a job finishes after its deadline."],
    editorial=["Earliest Deadline First (EDF) with preemption is optimal for feasibility on one machine: if any schedule meets all deadlines, EDF does too. The usual exchange argument shows that if at some slot a feasible schedule runs a job with a later deadline while a released job with an earlier deadline is waiting, swapping a slot of the two keeps both feasible.",
               "Simulating slot by slot is too slow for times up to 10<sup>7</sup>, so jump between events. Sort the jobs by release time. Maintain the time <code>t</code> and a min-heap keyed by deadline of released jobs with remaining work. If the heap is empty, jump to the next release. Otherwise take the top job and run it for <code>min(remaining, next_release - t)</code> units; if it completes, check <code>t &le; deadline</code>, otherwise push it back with less remaining work (it stays at the top of the heap, since its deadline is unchanged, unless new jobs arrive). Each job is touched O(1) times per release, so the total cost is O(n log n)."],
    time="O(n log n)", space="O(n)",
    solution='''import heapq


def canScheduleAll(jobs):
    jobs = sorted(jobs)
    n = len(jobs)
    heap = []
    t = 0
    i = 0
    INF = 10 ** 18
    while i < n or heap:
        if not heap and t < jobs[i][0]:
            t = jobs[i][0]
        while i < n and jobs[i][0] <= t:
            heapq.heappush(heap, [jobs[i][2], jobs[i][1]])
            i += 1
        nxt = jobs[i][0] if i < n else INF
        deadline, remaining = heap[0]
        run = min(remaining, nxt - t)
        t += run
        if run == remaining:
            heapq.heappop(heap)
            if t > deadline:
                return False
        else:
            heap[0][1] = remaining - run
    return True
''',
    tests=[[[[0, 2, 4], [1, 1, 2]]], [[[0, 3, 4], [1, 2, 3]]], [[]], [[[0, 1, 1]]], [[[0, 2, 1]]],
           [[[0, 5, 10], [0, 5, 10]]], [[[0, 5, 9], [0, 5, 9]]], [[[0, 4, 10], [2, 2, 4], [3, 1, 5]]],
           [[[0, 4, 10], [2, 2, 4], [3, 2, 5]]], [[[0, 10 ** 7, 10 ** 7]]], [[[5, 3, 20], [1, 4, 6], [8, 2, 10], [9, 3, 15]]]],
)
_r = rnd(3011)


def _gen_preempt(r, n, nblocks, maxblock, slack, extra):
    """Pack random blocks on a timeline, give them to jobs, widen windows by `slack`."""
    owner = [r.randrange(n) for _ in range(nblocks)]
    t = 0
    spans = [[None, 0, None] for _ in range(n)]
    for o in owner:
        ln = r.randint(1, maxblock)
        if spans[o][0] is None:
            spans[o][0] = t
        spans[o][1] += ln
        spans[o][2] = t + ln
        t += ln
    jobs = []
    for s, w, e in spans:
        if s is None:
            continue
        rel = max(0, s - r.randint(0, slack))
        dl = e + r.randint(0, slack)
        jobs.append([rel, w, dl])
    r.shuffle(jobs)
    if extra and jobs:
        j = r.choice(jobs)
        j[1] += extra
        j[2] += extra  # the longer job now needs a slot that is already taken
    return jobs


p["tests"].append([_gen_preempt(_r, 1500, 4500, 20, 0, 0)])
p["tests"].append([_gen_preempt(_r, 1500, 4500, 20, 30, 0)])
p["tests"].append([_gen_preempt(_r, 1500, 4500, 20, 0, 1)])
p["tests"].append([_gen_preempt(_r, 1200, 3600, 2000, 5000, 3)])


def b_preempt(jobs):
    """Demand-bound check: for every window [a, b) the work that must happen inside it fits."""
    rel = {j[0] for j in jobs}
    dls = {j[2] for j in jobs}
    for a in rel:
        for b in dls:
            if b <= a:
                continue
            need = sum(w for r_, w, d in jobs if r_ >= a and d <= b)
            if need > b - a:
                return False
    for r_, w, d in jobs:
        if w > d - r_:
            return False
    return True


def g_preempt(r):
    jobs = []
    for _ in range(r.randint(0, 6)):
        s = r.randint(0, 8)
        jobs.append([s, r.randint(1, 4), s + r.randint(1, 7)])
    return [jobs]


def v_preempt(tests):
    outs = set()
    for t in tests:
        jobs = t["args"][0]
        assert 0 <= len(jobs) <= 1500
        assert all(0 <= r_ < d <= 10 ** 7 and 1 <= w <= 10 ** 7 for r_, w, d in jobs)
        outs.add(t["expected"])
    assert outs == {True, False}


CHECKS["preemptive-jobs-meet-deadlines"] = (b_preempt, g_preempt, "exact")
VALIDATE["preemptive-jobs-meet-deadlines"] = v_preempt
