"""Problems: heap, greedy with heaps (reorganize, refuel, hire, minimize, exchange). See data/lib.py for the registry."""
from itertools import combinations
from fractions import Fraction

from lib import add, rnd, CHECKS, VALIDATE, gen_arr  # noqa: F401

INT_MIN, INT_MAX = -(2 ** 31), 2 ** 31 - 1
MOD = 10 ** 9 + 7


# ================================================================ EASY

# ---------------------------------------------------------------- halving piles
p = add(
    id="min-stones-after-halving-piles", title="Minimum Stones After Halving Piles", diff="Easy", topic="Heap", tier="extra",
    fn="minStonesAfterHalving", params=[("piles", "int[]"), ("k", "int")], ret="int", cmp="exact",
    desc="<p>There are several piles of stones; <code>piles[i]</code> is the number of stones in pile <code>i</code>. In one operation you choose a pile with <code>p</code> stones and throw away <code>floor(p / 2)</code> of them, so <code>ceil(p / 2)</code> stones stay in that pile. The same pile may be chosen again in later operations.</p><p>Perform <strong>exactly</strong> <code>k</code> operations (an operation on a pile with a single stone changes nothing) and return the smallest possible total number of stones left.</p><pre>piles = [5, 4, 9], k = 2\n9 -> 5 gives [5, 4, 5]\n5 -> 3 gives [3, 4, 5]   total = 12</pre>",
    constraints=["1 &le; piles.length &le; 5,000", "1 &le; piles[i] &le; 10,000", "1 &le; k &le; 100,000"],
    hints=["An operation removes more stones from a big pile than from a small one. Which pile should the very first operation use?",
           "Always halve the pile that is currently the largest: the number of stones it removes, floor(p / 2), never decreases with p.",
           "You need to repeatedly find and update the maximum. A max-heap does that in O(log n); Python's heapq is a min-heap, so store negated sizes."],
    editorial=["The gain of one operation on a pile of size <code>p</code> is <code>floor(p / 2)</code>, which grows with <code>p</code>. Halving a pile also never makes another pile's gain bigger. So at every step the best move is to halve the current largest pile; an exchange argument shows that any plan that halves a smaller pile first can swap it for the larger one without losing stones.",
               "Keep all piles in a max-heap. Repeat <code>k</code> times: look at the top, stop early if it is 1 (nothing can shrink any more), otherwise replace it by <code>(top + 1) // 2</code>. The answer is the sum of what is left in the heap.",
               "Each operation costs O(log n), so the total is O((n + k) log n). Because a pile reaches 1 after about 14 halvings for piles up to 10,000, the loop stops after at most about 14 n steps."],
    time="O((n + k) log n)", space="O(n)",
    solution='''import heapq


def minStonesAfterHalving(piles, k):
    h = [-x for x in piles]
    heapq.heapify(h)
    for _ in range(k):
        top = -h[0]
        if top == 1:
            break
        heapq.heapreplace(h, -((top + 1) // 2))
    return -sum(h)
''',
    tests=[[[5, 4, 9], 2], [[4, 3, 6, 7], 3], [[1], 5], [[1, 1, 1], 100000], [[10000], 1], [[10000], 100000],
           [[2, 2, 2], 1], [[7, 7, 7], 3], [[3, 1, 8, 2], 4], [[9, 9], 2]],
)
_r = rnd(8401)
p["tests"].append([[_r.randint(1, 10000) for _ in range(5000)], 5000])
p["tests"].append([[_r.randint(1, 10000) for _ in range(3000)], 100000])
p["tests"].append([[_r.randint(9000, 10000) for _ in range(4000)], 20000])


def b_halve(piles, k):
    seen = {}

    def go(t, k):
        if k == 0:
            return sum(t)
        key = (t, k)
        if key in seen:
            return seen[key]
        best = min(go(tuple(sorted(t[:i] + ((t[i] + 1) // 2,) + t[i + 1:])), k - 1) for i in range(len(t)))
        seen[key] = best
        return best

    return go(tuple(sorted(piles)), k)


def v_halve(tests):
    for t in tests:
        piles, k = t["args"]
        assert 1 <= len(piles) <= 5000 and all(1 <= x <= 10000 for x in piles)
        assert 1 <= k <= 100000


CHECKS["min-stones-after-halving-piles"] = (b_halve, lambda r: [[r.randint(1, 12) for _ in range(r.randint(1, 4))], r.randint(1, 5)], "exact")
VALIDATE["min-stones-after-halving-piles"] = v_halve

# ---------------------------------------------------------------- max moves removing from two piles
p = add(
    id="max-moves-taking-from-two-piles", title="Maximum Moves Taking From Two Piles", diff="Easy", topic="Heap", tier="extra",
    fn="maxPairMoves", params=[("piles", "int[]")], ret="int", cmp="exact",
    desc="<p>You are given piles of stones, <code>piles[i]</code> being the size of pile <code>i</code>. In one move you pick <strong>two different</strong> piles that are both non-empty and remove exactly one stone from each.</p><p>Return the maximum number of moves you can make.</p><pre>piles = [2, 3, 1]  result = 3\nmove on piles 1 and 0 -> [1, 2, 1]\nmove on piles 1 and 0 -> [0, 1, 1]\nmove on piles 1 and 2 -> [0, 0, 0]\n\npiles = [5, 1, 1]  result = 2   (the big pile needs partners)</pre>",
    constraints=["1 &le; piles.length &le; 500", "0 &le; piles[i] &le; 100"],
    hints=["Every move uses two stones, so the answer is at most half the total. But a huge pile can run out of partners.",
           "Which two piles should be paired in the next move? Stones in the largest pile are the hardest to use up later, so use them early.",
           "Greedy: take the two largest non-empty piles, remove one from each, and put them back into a max-heap. Count the moves until fewer than two non-empty piles remain."],
    editorial=["Always pair the two currently largest piles. The pile that is the largest is the one most at risk of being left with stones and no partners, and decreasing the two largest keeps the sizes as balanced as possible, which is what allows the most moves.",
               "Implementation: put the non-zero piles in a max-heap. While the heap has at least two items, pop the two largest, count a move, and push each back if it still has stones. The total number of moves is at most half of the total number of stones, which is at most 25,000 under the constraints, so the loop is fast.",
               "There is also a closed form. With total <code>S</code> and largest pile <code>M</code>, the answer is <code>min(S // 2, S - M)</code>: either the stones pair up perfectly, or the largest pile is the bottleneck and every other stone is used as its partner."],
    time="O(S log n)", space="O(n)",
    solution='''import heapq


def maxPairMoves(piles):
    h = [-x for x in piles if x > 0]
    heapq.heapify(h)
    moves = 0
    while len(h) >= 2:
        a = heapq.heappop(h)
        b = heapq.heappop(h)
        moves += 1
        if a + 1 < 0:
            heapq.heappush(h, a + 1)
        if b + 1 < 0:
            heapq.heappush(h, b + 1)
    return moves
''',
    tests=[[[2, 3, 1]], [[5, 1, 1]], [[0]], [[7]], [[1, 1]], [[0, 0, 4]], [[3, 3, 3]], [[10, 1, 1, 1, 1]], [[100, 100]],
           [[4, 4, 1, 0]]],
)
_r = rnd(8402)
p["tests"].append([[_r.randint(0, 100) for _ in range(500)]])
p["tests"].append([[100] + [_r.randint(0, 1) for _ in range(499)]])
p["tests"].append([[100] * 500])


def b_twopiles(piles):
    seen = {}

    def go(t):
        if t in seen:
            return seen[t]
        best = 0
        for i in range(len(t)):
            for j in range(i + 1, len(t)):
                if t[i] > 0 and t[j] > 0:
                    u = list(t)
                    u[i] -= 1
                    u[j] -= 1
                    best = max(best, 1 + go(tuple(sorted(u))))
        seen[t] = best
        return best

    return go(tuple(sorted(piles)))


def v_twopiles(tests):
    for t in tests:
        piles = t["args"][0]
        assert 1 <= len(piles) <= 500 and all(0 <= x <= 100 for x in piles)


CHECKS["max-moves-taking-from-two-piles"] = (b_twopiles, lambda r: [[r.randint(0, 5) for _ in range(r.randint(1, 4))]], "exact")
VALIDATE["max-moves-taking-from-two-piles"] = v_twopiles

# ================================================================ MEDIUM

# ---------------------------------------------------------------- max score of k indices
p = add(
    id="max-score-sum-times-min-of-k-indices", title="Maximum Sum Times Minimum of K Indices", diff="Medium", topic="Heap",
    fn="maxScore", params=[("nums1", "int[]"), ("nums2", "int[]"), ("k", "int")], ret="int", cmp="exact",
    desc="<p>The arrays <code>nums1</code> and <code>nums2</code> have the same length <code>n</code>. Choose exactly <code>k</code> distinct indices. The score of a choice is</p><p><code>(sum of nums1[i] over the chosen i) * (minimum of nums2[i] over the chosen i)</code>.</p><p>Return the maximum possible score.</p><pre>nums1 = [1, 3, 3, 2], nums2 = [2, 1, 3, 4], k = 3\nchoose indices 0, 2, 3: sum = 1 + 3 + 2 = 6, min = min(2, 3, 4) = 2, score = 12</pre>",
    constraints=["1 &le; n &le; 1,500", "1 &le; k &le; n", "0 &le; nums1[i], nums2[i] &le; 1,000"],
    hints=["The minimum of nums2 is awkward. What if you fixed which index supplies the minimum?",
           "Process indices in decreasing order of nums2. When index <code>i</code> is the current one, every index seen so far has nums2 at least as large, so <code>nums2[i]</code> is a valid minimum.",
           "Among the indices seen so far you want the k with the largest nums1. Keep a min-heap of size k and a running sum, dropping the smallest nums1 whenever the heap grows beyond k."],
    editorial=["Sort the indices by <code>nums2</code> from large to small. Suppose the chosen group has its minimum at the index <code>i</code> that comes last in this order. Then the group is <code>i</code> together with other indices that came earlier, and the score is <code>nums2[i]</code> times the sum of the group's nums1 values. To maximise it we want the k largest nums1 values among the first positions of the order up to and including <code>i</code> (it is fine if <code>i</code> itself is not among them, since then the true minimum is even larger and the real score is only higher).",
               "Sweep through the sorted order keeping a min-heap of the nums1 values of the current best k and their sum. Push the new value, and if the heap has more than k items pop the smallest and subtract it. Once the heap holds k items, the candidate score is <code>sum * nums2[i]</code>. The answer is the largest candidate.",
               "Sorting costs O(n log n) and each heap operation O(log k), so the total time is O(n log n) with O(n + k) memory. The largest possible score is below 1,500 * 1,000 * 1,000 = 1.5e9, which fits in a 32-bit integer."],
    time="O(n log n)", space="O(n)",
    solution='''import heapq


def maxScore(nums1, nums2, k):
    order = sorted(range(len(nums1)), key=lambda i: -nums2[i])
    h = []
    s = 0
    best = 0
    for i in order:
        heapq.heappush(h, nums1[i])
        s += nums1[i]
        if len(h) > k:
            s -= heapq.heappop(h)
        if len(h) == k:
            best = max(best, s * nums2[i])
    return best
''',
    tests=[[[1, 3, 3, 2], [2, 1, 3, 4], 3], [[4, 2, 3, 1, 1], [7, 5, 10, 9, 6], 1], [[5], [4], 1], [[0, 0, 0], [5, 5, 5], 2],
           [[3, 3, 3], [0, 0, 0], 3], [[1, 2, 3], [3, 2, 1], 3], [[10, 1, 1], [1, 9, 9], 2], [[7, 7, 7, 7], [1, 2, 3, 4], 2],
           [[1000, 1000], [1000, 1000], 2]],
)
_r = rnd(8403)
p["tests"].append([[_r.randint(0, 1000) for _ in range(1500)], [_r.randint(0, 1000) for _ in range(1500)], 700])
p["tests"].append([[_r.randint(0, 1000) for _ in range(1500)], [_r.randint(0, 1000) for _ in range(1500)], 1])
p["tests"].append([[_r.randint(900, 1000) for _ in range(1500)], [_r.randint(1, 1000) for _ in range(1500)], 1500])
p["tests"].append([[_r.randint(0, 1000) for _ in range(1500)], [_r.randint(0, 1000) for _ in range(1500)], 40])


def b_score(nums1, nums2, k):
    best = 0
    for c in combinations(range(len(nums1)), k):
        best = max(best, sum(nums1[i] for i in c) * min(nums2[i] for i in c))
    return best


def g_score(r):
    n = r.randint(1, 7)
    return [[r.randint(0, 9) for _ in range(n)], [r.randint(0, 9) for _ in range(n)], r.randint(1, n)]


def v_score(tests):
    for t in tests:
        a, b, k = t["args"]
        assert len(a) == len(b) and 1 <= len(a) <= 1500 and 1 <= k <= len(a)
        assert all(0 <= x <= 1000 for x in a + b)


CHECKS["max-score-sum-times-min-of-k-indices"] = (b_score, g_score, "exact")
VALIDATE["max-score-sum-times-min-of-k-indices"] = v_score

# ---------------------------------------------------------------- total cost to hire k workers
p = add(
    id="total-cost-to-hire-k-workers", title="Total Cost to Hire K Workers", diff="Medium", topic="Heap",
    fn="totalHireCost", params=[("costs", "int[]"), ("k", "int"), ("candidates", "int")], ret="int", cmp="exact",
    desc="<p>The array <code>costs</code> lists the hiring cost of the workers standing in a queue, <code>costs[i]</code> being the cost of the worker at position <code>i</code>. You must run exactly <code>k</code> hiring rounds. In each round:</p><ul><li>look only at the first <code>candidates</code> workers and the last <code>candidates</code> workers of the workers still waiting (if fewer than <code>2 * candidates</code> are waiting, all of them are visible; nobody is counted twice);</li><li>hire the visible worker with the lowest cost; if several have that cost, take the one with the smallest original index.</li></ul><p>A hired worker leaves the queue and the others keep their order. Return the total cost of the <code>k</code> hired workers.</p><pre>costs = [17, 12, 10, 2, 7, 2, 11, 20, 8], k = 3, candidates = 4\nround 1: visible 17 12 10 2 | 2 11 20 8 -> hire index 3 (cost 2)\nround 2: visible 17 12 10 7 | 2 11 20 8 -> hire index 5 (cost 2)\nround 3: visible 17 12 10 7 | 7 11 20 8 -> hire index 4 (cost 7)\ntotal = 11</pre>",
    constraints=["1 &le; costs.length &le; 5,000", "1 &le; costs[i] &le; 100,000", "1 &le; k &le; costs.length", "1 &le; candidates &le; costs.length"],
    hints=["A direct simulation scans the visible workers in every round. That is O(k * candidates). Can you find the cheapest visible worker faster?",
           "The visible workers form two groups: the front group and the back group. Keep each group in its own min-heap of (cost, index).",
           "After hiring from a group, slide the window: take the next waiting worker from that side (the front pointer moves right, the back pointer moves left) as long as the two pointers have not crossed."],
    editorial=["Maintain two pointers <code>l</code> and <code>r</code> that delimit the workers not yet shown to any heap. First push the first <code>candidates</code> workers into a left min-heap and the last <code>candidates</code> workers into a right min-heap, never pushing a worker that was already pushed (stop when <code>l &gt; r</code>).",
               "In each round compare the tops of the two heaps as (cost, index) pairs. Because every index in the left heap is smaller than every index in the right heap, comparing the pairs directly gives the right tie-break. Pop the better one, add its cost, and refill the heap it came from with the next unseen worker on that side if one is left.",
               "Every worker enters a heap at most once and each round performs O(1) heap operations, so the total time is O((candidates + k) log candidates) and the memory is O(candidates)."],
    time="O((c + k) log c)", space="O(c)",
    solution='''import heapq


def totalHireCost(costs, k, candidates):
    n = len(costs)
    left, right = [], []
    l, r = 0, n - 1
    for _ in range(candidates):
        if l <= r:
            heapq.heappush(left, (costs[l], l))
            l += 1
    for _ in range(candidates):
        if l <= r:
            heapq.heappush(right, (costs[r], r))
            r -= 1
    total = 0
    for _ in range(k):
        if left and (not right or left[0] <= right[0]):
            c, _i = heapq.heappop(left)
            total += c
            if l <= r:
                heapq.heappush(left, (costs[l], l))
                l += 1
        else:
            c, _i = heapq.heappop(right)
            total += c
            if l <= r:
                heapq.heappush(right, (costs[r], r))
                r -= 1
    return total
''',
    tests=[[[17, 12, 10, 2, 7, 2, 11, 20, 8], 3, 4], [[1, 2, 4, 1], 3, 3], [[5], 1, 1], [[3, 3, 3, 3], 4, 1], [[9, 8, 7, 1, 2], 3, 1],
           [[1, 100, 100, 100, 1], 2, 1], [[4, 2, 6, 1], 2, 4], [[10, 1, 10, 10, 10, 10, 1, 10], 4, 2], [[5, 4, 3, 2, 1], 5, 2]],
)
_r = rnd(8404)
p["tests"].append([[_r.randint(1, 100000) for _ in range(5000)], 2500, 100])
p["tests"].append([[_r.randint(1, 100000) for _ in range(5000)], 5000, 1])
p["tests"].append([[_r.randint(1, 20) for _ in range(5000)], 3000, 300])
p["tests"].append([[_r.randint(1, 100000) for _ in range(5000)], 1000, 5000])


def b_hire(costs, k, candidates):
    rem = [(c, i) for i, c in enumerate(costs)]
    total = 0
    for _ in range(k):
        vis = rem[:candidates] + rem[max(candidates, len(rem) - candidates):]
        best = min(vis)
        total += best[0]
        rem.remove(best)
    return total


def g_hire(r):
    n = r.randint(1, 9)
    return [[r.randint(1, 6) for _ in range(n)], r.randint(1, n), r.randint(1, n)]


def v_hire(tests):
    for t in tests:
        costs, k, c = t["args"]
        assert 1 <= len(costs) <= 5000 and all(1 <= x <= 100000 for x in costs)
        assert 1 <= k <= len(costs) and 1 <= c <= len(costs)


CHECKS["total-cost-to-hire-k-workers"] = (b_hire, g_hire, "exact")
VALIDATE["total-cost-to-hire-k-workers"] = v_hire

# ---------------------------------------------------------------- assign tasks to servers
p = add(
    id="assign-tasks-to-servers", title="Assign Tasks to Servers", diff="Medium", topic="Heap", tier="extra",
    fn="assignTasks", params=[("servers", "int[]"), ("tasks", "int[]")], ret="int[]", cmp="exact",
    desc="<p>A cluster has servers numbered <code>0..n-1</code>; <code>servers[i]</code> is the weight of server <code>i</code>. There are <code>m</code> tasks. Task <code>j</code> arrives at second <code>j</code> and needs <code>tasks[j]</code> seconds to run. Arriving tasks wait in a queue in the order of their index.</p><p>At every second, while the queue is not empty and at least one server is free, the task at the front of the queue is given to the free server with the <strong>smallest weight</strong>, ties broken by the <strong>smallest index</strong>. A server that starts a task at second <code>s</code> is busy until second <code>s + tasks[j]</code>, and at that very second it is free again and can accept a task.</p><p>Return an array <code>ans</code> of length <code>m</code> where <code>ans[j]</code> is the index of the server that runs task <code>j</code>.</p><pre>servers = [3, 3, 2], tasks = [1, 2, 3, 2, 1, 2]\nresult  = [2, 2, 0, 2, 1, 2]\nsecond 0: task 0 -> server 2 (weight 2), busy until 1\nsecond 1: task 1 -> server 2 again, busy until 3\nsecond 2: task 2 -> server 0 (weights tie, smaller index), busy until 5\nsecond 3: task 3 -> server 2, busy until 5\nsecond 4: task 4 -> server 1, busy until 5\nsecond 5: task 5 -> server 2</pre>",
    constraints=["1 &le; servers.length &le; 3,000", "1 &le; tasks.length &le; 3,000", "1 &le; servers[i], tasks[j] &le; 100,000"],
    hints=["Simulating every second is too slow when tasks last 100,000 seconds. Which moments actually matter?",
           "Only moments when a task is assigned matter. Keep a min-heap of free servers ordered by (weight, index) and a min-heap of busy servers ordered by finishing time.",
           "For task j, set the current time to max(time, j). Move every busy server that finished by then back to the free heap. If no server is free, jump the time to the earliest finishing time and release again."],
    editorial=["Use two heaps. The free heap holds <code>(weight, index)</code>, the busy heap holds <code>(finish time, weight, index)</code>. Keep a variable <code>t</code> for the time at which the current task gets assigned; because the queue is first-in-first-out, assignment times never go backwards.",
               "For task <code>j</code>: first <code>t = max(t, j)</code>, since the task cannot start before it arrives. Release from the busy heap all servers with finish time <code>&le; t</code>. If the free heap is still empty, the task has to wait: set <code>t</code> to the smallest finish time and release again (this may free several servers at once, and the tie-break among them is exactly the heap order). Then pop the best free server, record it, and push it to the busy heap with finish time <code>t + tasks[j]</code>.",
               "Each task causes a constant number of heap operations, so the time is O((n + m) log n) and the memory O(n)."],
    time="O((n + m) log n)", space="O(n)",
    solution='''import heapq


def assignTasks(servers, tasks):
    free = [(w, i) for i, w in enumerate(servers)]
    heapq.heapify(free)
    busy = []
    ans = []
    t = 0
    for j, d in enumerate(tasks):
        t = max(t, j)
        while busy and busy[0][0] <= t:
            _e, w, i = heapq.heappop(busy)
            heapq.heappush(free, (w, i))
        if not free:
            t = busy[0][0]
            while busy and busy[0][0] <= t:
                _e, w, i = heapq.heappop(busy)
                heapq.heappush(free, (w, i))
        w, i = heapq.heappop(free)
        ans.append(i)
        heapq.heappush(busy, (t + d, w, i))
    return ans
''',
    tests=[[[3, 3, 2], [1, 2, 3, 2, 1, 2]], [[5, 1, 4, 3, 2], [2, 1, 2, 4, 5, 2, 1]], [[1], [5]], [[1], [3, 3, 3]], [[2, 2], [1, 1, 1, 1]],
           [[10, 20, 30], [100, 100, 100, 1, 1, 1]], [[4, 4, 4], [5, 5, 5, 5, 5, 5, 5]], [[1, 2], [2, 1, 1, 1, 1]], [[7, 3, 5], [1]]],
)
_r = rnd(8405)
p["tests"].append([[_r.randint(1, 100000) for _ in range(3000)], [_r.randint(1, 100000) for _ in range(3000)]])
p["tests"].append([[_r.randint(1, 10) for _ in range(300)], [_r.randint(1, 100) for _ in range(3000)]])
p["tests"].append([[_r.randint(1, 100000) for _ in range(3000)], [_r.randint(1, 5) for _ in range(3000)]])


def b_assign(servers, tasks):
    n, m = len(servers), len(tasks)
    finish = [0] * n
    queue = []
    ans = [None] * m
    t = 0
    done = 0
    while done < m:
        if t < m:
            queue.append(t)
        while queue:
            cand = [(servers[i], i) for i in range(n) if finish[i] <= t]
            if not cand:
                break
            _w, i = min(cand)
            j = queue.pop(0)
            ans[j] = i
            finish[i] = t + tasks[j]
            done += 1
        t += 1
    return ans


def g_assign(r):
    return [[r.randint(1, 5) for _ in range(r.randint(1, 4))], [r.randint(1, 6) for _ in range(r.randint(1, 8))]]


def v_assign(tests):
    for t in tests:
        s, ts = t["args"]
        assert 1 <= len(s) <= 3000 and 1 <= len(ts) <= 3000
        assert all(1 <= x <= 100000 for x in s + ts)
        assert len(t["expected"]) == len(ts) and all(0 <= x < len(s) for x in t["expected"])


CHECKS["assign-tasks-to-servers"] = (b_assign, g_assign, "exact")
VALIDATE["assign-tasks-to-servers"] = v_assign

# ---------------------------------------------------------------- max product after k increments
p = add(
    id="max-product-after-k-increments", title="Maximum Product After K Increments", diff="Medium", topic="Heap",
    fn="maxProductAfterIncrements", params=[("nums", "int[]"), ("k", "int")], ret="int", cmp="exact",
    desc="<p>You are given an array of non-negative integers <code>nums</code> and an integer <code>k</code>. In one operation you choose any index and add <code>1</code> to that element. You may do <strong>at most</strong> <code>k</code> operations.</p><p>Return the maximum possible product of all elements after the operations, <strong>modulo</strong> <code>1,000,000,007</code>. (Compare the true products when deciding what is maximal; only the returned value is reduced.)</p><pre>nums = [6, 3, 3, 2], k = 2\n2 -> 3 gives [6, 3, 3, 3]\n3 -> 4 gives [6, 4, 3, 3]   product = 216\n\nnums = [0, 4], k = 5\n0 climbs to 4, then one more increment: [5, 4]   product = 20</pre>",
    constraints=["1 &le; nums.length &le; 5,000", "0 &le; nums[i] &le; 1,000,000", "0 &le; k &le; 50,000"],
    hints=["Adding 1 to x multiplies the product by (x + 1) / x. For which x is that factor the biggest?",
           "The factor (x + 1) / x is largest for the smallest x (a zero is even better: it lifts the whole product off zero). So always increment the current minimum.",
           "Use a min-heap: k times pop the smallest value and push it back plus one. At the end multiply everything modulo 1,000,000,007."],
    editorial=["For a fixed element <code>x</code>, incrementing it multiplies the product by <code>(x + 1) / x</code>, which is larger for smaller <code>x</code>. Equivalent view: for a fixed sum, a product is largest when the factors are as equal as possible. Incrementing the minimum repeatedly makes the array as even as possible, and an exchange argument proves optimality: moving an increment from a larger element to a smaller one never reduces the product.",
               "Heapify the array, then do <code>k</code> times <code>heapreplace(h, h[0] + 1)</code>, which is one O(log n) operation. Finally multiply all values modulo 1,000,000,007. Using all <code>k</code> operations is never worse because all values are non-negative.",
               "Time O(n + k log n), memory O(n). Never compare products modulo the prime; the heap only ever compares the individual values, so no huge numbers are needed."],
    time="O(n + k log n)", space="O(n)",
    solution='''import heapq

MOD = 10 ** 9 + 7


def maxProductAfterIncrements(nums, k):
    h = list(nums)
    heapq.heapify(h)
    for _ in range(k):
        heapq.heapreplace(h, h[0] + 1)
    result = 1
    for x in h:
        result = result * x % MOD
    return result
''',
    tests=[[[6, 3, 3, 2], 2], [[0, 4], 5], [[7], 0], [[0, 0, 0], 0], [[0, 0, 0], 3], [[1, 1, 1, 1], 4], [[5], 10], [[1000000, 1000000], 50000],
           [[2, 9], 3], [[0, 1000000, 0], 50000]],
)
_r = rnd(8406)
p["tests"].append([[_r.randint(0, 1000000) for _ in range(5000)], 50000])
p["tests"].append([[_r.randint(0, 20) for _ in range(5000)], 50000])
p["tests"].append([[_r.randint(0, 3) for _ in range(3000)], 40000])


def b_prod(nums, k):
    best = [0]

    def go(t, left, i):
        if i == len(t):
            pr = 1
            for x in t:
                pr *= x
            best[0] = max(best[0], pr)
            return
        for add_ in range(left + 1):
            t[i] += add_
            go(t, left - add_, i + 1)
            t[i] -= add_

    go(list(nums), k, 0)
    return best[0] % MOD


def g_prod(r):
    return [[r.randint(0, 6) for _ in range(r.randint(1, 4))], r.randint(0, 7)]


def v_prod(tests):
    for t in tests:
        nums, k = t["args"]
        assert 1 <= len(nums) <= 5000 and all(0 <= x <= 1000000 for x in nums)
        assert 0 <= k <= 50000


CHECKS["max-product-after-k-increments"] = (b_prod, g_prod, "exact")
VALIDATE["max-product-after-k-increments"] = v_prod

# ---------------------------------------------------------------- eaten apples
p = add(
    id="maximum-eaten-apples", title="Maximum Number of Eaten Apples", diff="Medium", topic="Heap", tier="extra",
    fn="eatenApples", params=[("apples", "int[]"), ("days", "int[]")], ret="int", cmp="exact",
    desc="<p>An apple tree bears fruit for <code>n</code> days. On day <code>i</code> (counting from 0) it grows <code>apples[i]</code> new apples, and these apples rot after <code>days[i]</code> days, which means they can be eaten on days <code>i, i+1, ..., i + days[i] - 1</code> and not later. A day with <code>apples[i] = 0</code> grows nothing.</p><p>You eat <strong>at most one</strong> apple per day, and you may keep eating after day <code>n - 1</code> as long as unrotten apples remain. Return the maximum number of apples you can eat.</p><pre>apples = [1, 2, 3, 5, 2], days = [3, 2, 1, 4, 2]\nresult = 7\nbatches: {1 apple, days 0-2}, {2 apples, days 1-2}, {3 apples, day 2 only}, {5 apples, days 3-6}, {2 apples, days 4-5}\nday 0: batch 0   day 1: batch 1   day 2: batch 1 (batch 2 would rot next day, but one apple per day only)\nday 3: batch 3   day 4: batch 4   day 5: batch 4   day 6: batch 3   -> 7 apples</pre>",
    constraints=["1 &le; n &le; 3,000", "0 &le; apples[i] &le; 20,000", "0 &le; days[i] &le; 20,000", "days[i] &ge; 1 whenever apples[i] &gt; 0"],
    hints=["Each day you have to decide which batch to eat from. Think of each batch as having a deadline.",
           "Eating the apples that rot soonest first never hurts: apples that expire later can still be eaten on the following days.",
           "Keep a min-heap of batches keyed by their last edible day. Each day add today's batch, drop batches that already rotted, and eat one apple from the batch on top."],
    editorial=["This is a scheduling problem with unit tasks and deadlines: every apple is a task that must be done by the last edible day of its batch, and each day offers one slot. Earliest-deadline-first is optimal: if an optimal plan eats a later-expiring apple on a day when an earlier-expiring one was available, swapping them keeps every apple edible and the count unchanged.",
               "Simulate day by day. Maintain a min-heap of <code>[last edible day (exclusive), remaining count]</code>. On day <code>i</code>, push today's batch if it has apples, pop batches whose expiry is at most <code>i</code>, then decrement the count of the top batch and add one to the answer; remove the batch from the heap when its count reaches 0. Continue past day <code>n - 1</code> until the heap is empty.",
               "The loop runs at most <code>n + max(days)</code> iterations (at most 23,000 here), each with O(log n) heap work. Memory is O(n)."],
    time="O((n + D) log n)", space="O(n)",
    solution='''import heapq


def eatenApples(apples, days):
    n = len(apples)
    h = []
    eaten = 0
    i = 0
    while i < n or h:
        if i < n and apples[i] > 0:
            heapq.heappush(h, [i + days[i], apples[i]])
        while h and h[0][0] <= i:
            heapq.heappop(h)
        if h:
            h[0][1] -= 1
            eaten += 1
            if h[0][1] == 0:
                heapq.heappop(h)
        i += 1
    return eaten
''',
    tests=[[[1, 2, 3, 5, 2], [3, 2, 1, 4, 2]], [[3, 0, 0, 0, 0, 2], [3, 0, 0, 0, 0, 2]], [[0], [0]], [[5], [1]], [[1], [5]], [[5], [5]],
           [[2, 2, 2], [1, 1, 1]], [[1, 1, 1, 1], [4, 3, 2, 1]], [[0, 0, 4], [0, 0, 2]], [[10, 0, 0, 1], [3, 0, 0, 5]]],
)
_r = rnd(8407)
p["tests"].append([[_r.randint(0, 20000) for _ in range(3000)], [_r.randint(1, 20000) for _ in range(3000)]])
p["tests"].append([[_r.randint(0, 3) for _ in range(3000)], [_r.randint(1, 8) for _ in range(3000)]])
p["tests"].append([[20000] * 3000, [20000] * 3000])
p["tests"].append([[(_r.randint(1, 6) if _r.random() < 0.3 else 0) for _ in range(3000)], [_r.randint(1, 30) for _ in range(3000)]])


def b_apples(apples, days):
    n = len(apples)
    seen = {}

    def go(d, batches):
        # batches: sorted tuple of (last_edible_day, count)
        if d >= n and not batches:
            return 0
        key = (d, batches)
        if key in seen:
            return seen[key]
        cur = list(batches)
        if d < n and apples[d] > 0:
            cur.append((d + days[d] - 1, apples[d]))
        cur = [(e, c) for e, c in cur if e >= d]
        best = go(d + 1, tuple(sorted(cur)))
        for idx in range(len(cur)):
            nxt = list(cur)
            e, c = nxt[idx]
            if c == 1:
                nxt.pop(idx)
            else:
                nxt[idx] = (e, c - 1)
            best = max(best, 1 + go(d + 1, tuple(sorted(nxt))))
        seen[key] = best
        return best

    return go(0, ())


def g_apples(r):
    n = r.randint(1, 5)
    a = [r.randint(0, 3) for _ in range(n)]
    dd = [r.randint(1, 4) for _ in range(n)]
    return [a, [dd[i] if a[i] > 0 else r.choice([0, dd[i]]) for i in range(n)]]


def v_apples(tests):
    for t in tests:
        a, d = t["args"]
        assert len(a) == len(d) and 1 <= len(a) <= 3000
        assert all(0 <= x <= 20000 for x in a + d)
        assert all(d[i] >= 1 for i in range(len(a)) if a[i] > 0)


CHECKS["maximum-eaten-apples"] = (b_apples, g_apples, "exact")
VALIDATE["maximum-eaten-apples"] = v_apples

# ---------------------------------------------------------------- longest string without three in a row
p = add(
    id="longest-string-no-triple-repeat", title="Longest String Without Three in a Row", diff="Medium", topic="Heap",
    fn="longestNoTriple", params=[("counts", "int[]")], ret="int", cmp="exact",
    desc="<p>You own a supply of letters: <code>counts[i]</code> copies of the <code>i</code>-th letter of an alphabet with <code>counts.length</code> letters. Build a string using at most <code>counts[i]</code> copies of letter <code>i</code> such that <strong>no letter appears three times in a row</strong>.</p><p>Return the maximum possible length of such a string.</p><pre>counts = [1, 1, 7]  result = 8   (e.g. c c a c c b c c)\ncounts = [2, 2, 1]  result = 5   (e.g. a a b b c)\ncounts = [5]        result = 2   (a a)</pre>",
    constraints=["1 &le; counts.length &le; 26", "0 &le; counts[i] &le; 3,000"],
    hints=["A letter that is very frequent is the limiting factor: it needs separators between every pair of its triples.",
           "Build left to right. Which letter should come next? The one with the most copies remaining, since it is the hardest to place later.",
           "Use a max-heap of remaining counts. Take the top letter unless it has already been written twice in a row; then take the second one instead (if there is none, you are done)."],
    editorial=["Construct the string greedily, one character at a time. At each step choose the letter with the largest remaining count that is allowed, meaning that it is not the letter which has just been used twice in a row. Using the most plentiful letter first keeps the stock as balanced as possible, so that no letter is left over without separators.",
               "With a max-heap of <code>(-remaining, letter)</code>: pop the top; if it equals the last letter and the current run is already 2, pop the next one instead and push the first one back. If the heap is empty at that point nothing more can be added and the process ends. After using a letter, push it back if copies remain.",
               "The string is at most 78,000 characters long and each step does O(log 26) heap work, so the cost is O(L log k) for k letters and output length L, with O(k) memory."],
    time="O(L log k)", space="O(k)",
    solution='''import heapq


def longestNoTriple(counts):
    h = [(-c, i) for i, c in enumerate(counts) if c > 0]
    heapq.heapify(h)
    length = 0
    last = -1
    run = 0
    while h:
        c, i = heapq.heappop(h)
        if i == last and run == 2:
            if not h:
                break
            c2, i2 = heapq.heappop(h)
            heapq.heappush(h, (c, i))
            c, i = c2, i2
        length += 1
        if i == last:
            run += 1
        else:
            last, run = i, 1
        if c + 1 < 0:
            heapq.heappush(h, (c + 1, i))
    return length
''',
    tests=[[[1, 1, 7]], [[2, 2, 1]], [[5]], [[0]], [[0, 0, 0]], [[1]], [[3, 3]], [[10, 1]], [[4, 4, 4, 4]], [[0, 9, 0, 1]], [[3000]],
           [[3000, 3000, 3000]]],
)
_r = rnd(8408)
p["tests"].append([[_r.randint(0, 3000) for _ in range(26)]])
p["tests"].append([[3000] + [_r.randint(0, 5) for _ in range(25)]])


def b_triple(counts):
    seen = {}

    def go(t, last, run):
        key = (t, last, run)
        if key in seen:
            return seen[key]
        best = 0
        for i in range(len(t)):
            if t[i] == 0:
                continue
            if i == last and run == 2:
                continue
            u = list(t)
            u[i] -= 1
            best = max(best, 1 + go(tuple(u), i, run + 1 if i == last else 1))
        seen[key] = best
        return best

    return go(tuple(counts), -1, 0)


def v_triple(tests):
    for t in tests:
        c = t["args"][0]
        assert 1 <= len(c) <= 26 and all(0 <= x <= 3000 for x in c)


CHECKS["longest-string-no-triple-repeat"] = (b_triple, lambda r: [[r.randint(0, 5) for _ in range(r.randint(1, 4))]], "exact")
VALIDATE["longest-string-no-triple-repeat"] = v_triple

# ================================================================ HARD

# ---------------------------------------------------------------- minimum cost to hire k workers
p = add(
    id="min-cost-to-hire-k-workers-by-quality", title="Minimum Cost to Hire K Workers", diff="Hard", topic="Heap",
    fn="minCostToHire", params=[("quality", "int[]"), ("wage", "int[]"), ("k", "int")], ret="int", cmp="exact",
    desc="<p>Worker <code>i</code> has a work quality <code>quality[i]</code> and demands a minimum wage <code>wage[i]</code>. You must hire exactly <code>k</code> workers and pay them under two rules:</p><ul><li>every hired worker is paid at least their minimum wage;</li><li>the pay of the hired workers is proportional to their quality: if worker <code>a</code> has twice the quality of worker <code>b</code>, then <code>a</code> is paid twice as much as <code>b</code>.</li></ul><p>Pay may be a fraction of a currency unit. Return the smallest possible total pay <strong>rounded up to the next integer</strong>.</p><pre>quality = [10, 20, 5], wage = [70, 50, 30], k = 2\nhire workers 0 and 2: pay per quality unit must be at least max(7, 6) = 7\npay = 70 and 35, total 105\n\nquality = [3, 1, 10, 10, 1], wage = [4, 8, 2, 2, 7], k = 3\nbest group: workers 0, 2, 3 at rate 4/3 per quality unit, total 30.666..., rounded up to 31</pre>",
    constraints=["1 &le; n &le; 3,000, where n = quality.length = wage.length", "1 &le; k &le; n", "1 &le; quality[i] &le; 100", "1 &le; wage[i] &le; 1,000"],
    hints=["Once you fix the group, everyone is paid the same rate per unit of quality. Which worker decides that rate?",
           "The rate must be at least wage[i] / quality[i] for every hired worker, so the group's rate is the largest of these ratios; the total pay is rate times the sum of the group's qualities.",
           "Sort workers by ratio. Sweep: the current worker supplies the rate, and among the workers seen so far (all with smaller or equal ratio) you want the k smallest qualities. Keep a max-heap of qualities of size k and its sum."],
    editorial=["For a chosen group, every worker is paid <code>rate * quality</code> with a common <code>rate</code>, and the rate must satisfy <code>rate &ge; wage[i] / quality[i]</code> for every member, so the cheapest legal rate is the maximum ratio in the group. The total pay is therefore <code>max_ratio * sum of qualities</code>.",
               "Sort the workers by <code>wage / quality</code> (compare with cross-multiplication to stay in integers). Process them in this order; when worker <code>w</code> is processed, it can be the maximum-ratio member of any group made of itself and earlier workers. For a fixed maximum ratio we want the smallest possible sum of qualities, i.e. the k smallest qualities among the workers seen so far. Keep those in a max-heap with a running sum: push the new quality, and if the heap holds more than k, pop the largest. Whenever the heap holds exactly k workers, the candidate cost is <code>ratio(w) * sum</code>, computed as <code>ceil(wage[w] * sum / quality[w])</code>. If the current worker itself was popped, the cost is still a valid payment for the remaining group (its rate is at least as large as needed), so it never goes below the true optimum.",
               "Rounding up commutes with taking the minimum, so we may round each candidate. Sorting costs O(n log n) and the heap O(n log k). All intermediate products fit in Python integers and the final answer is below 3,000 * 100 * 1,000 = 3e8."],
    time="O(n log n)", space="O(n)",
    solution='''import heapq
from functools import cmp_to_key


def minCostToHire(quality, wage, k):
    n = len(quality)
    order = sorted(range(n), key=cmp_to_key(lambda a, b: wage[a] * quality[b] - wage[b] * quality[a]))
    h = []
    total_q = 0
    best = None
    for i in order:
        heapq.heappush(h, -quality[i])
        total_q += quality[i]
        if len(h) > k:
            total_q += heapq.heappop(h)
        if len(h) == k:
            cost = (wage[i] * total_q + quality[i] - 1) // quality[i]
            if best is None or cost < best:
                best = cost
    return best
''',
    tests=[[[10, 20, 5], [70, 50, 30], 2], [[3, 1, 10, 10, 1], [4, 8, 2, 2, 7], 3], [[5], [9], 1], [[1, 1, 1], [5, 5, 5], 3],
           [[1, 1, 1], [5, 5, 5], 1], [[2, 3], [10, 10], 2], [[100, 1], [1, 1000], 2], [[7, 7, 7, 7], [1, 2, 3, 4], 2],
           [[4, 1, 2], [8, 5, 3], 2], [[3, 6, 9], [1, 1, 1], 3]],
)
_r = rnd(8409)
p["tests"].append([[_r.randint(1, 100) for _ in range(3000)], [_r.randint(1, 1000) for _ in range(3000)], 1500])
p["tests"].append([[_r.randint(1, 100) for _ in range(3000)], [_r.randint(1, 1000) for _ in range(3000)], 20])
p["tests"].append([[_r.randint(1, 100) for _ in range(3000)], [_r.randint(1, 1000) for _ in range(3000)], 3000])


def b_hire_ratio(quality, wage, k):
    best = None
    for c in combinations(range(len(quality)), k):
        rate = max(Fraction(wage[i], quality[i]) for i in c)
        total = rate * sum(quality[i] for i in c)
        cost = -((-total.numerator) // total.denominator)
        if best is None or cost < best:
            best = cost
    return best


def g_hire_ratio(r):
    n = r.randint(1, 7)
    return [[r.randint(1, 9) for _ in range(n)], [r.randint(1, 30) for _ in range(n)], r.randint(1, n)]


def v_hire_ratio(tests):
    for t in tests:
        q, w, k = t["args"]
        assert len(q) == len(w) and 1 <= len(q) <= 3000 and 1 <= k <= len(q)
        assert all(1 <= x <= 100 for x in q) and all(1 <= x <= 1000 for x in w)


CHECKS["min-cost-to-hire-k-workers-by-quality"] = (b_hire_ratio, g_hire_ratio, "exact")
VALIDATE["min-cost-to-hire-k-workers-by-quality"] = v_hire_ratio

# ---------------------------------------------------------------- minimize deviation
p = add(
    id="minimize-deviation-by-halving-and-doubling", title="Minimize Deviation by Halving and Doubling", diff="Hard", topic="Heap", tier="extra",
    fn="minimumDeviation", params=[("nums", "int[]")], ret="int", cmp="exact",
    desc="<p>You are given an array <code>nums</code> of positive integers. You may apply any number of operations, each on any element:</p><ul><li>if the element is <strong>even</strong>, divide it by 2;</li><li>if the element is <strong>odd</strong>, multiply it by 2.</li></ul><p>The <em>deviation</em> of the array is the difference between its largest and its smallest element. Return the minimum deviation that can be reached.</p><pre>nums = [1, 2, 3, 4]  result = 1\ndouble 1 -> [2, 2, 3, 4], halve 4 -> [2, 2, 3, 2]   max 3, min 2\n\nnums = [4, 1, 5, 20, 3]  result = 3</pre>",
    constraints=["1 &le; nums.length &le; 5,000", "1 &le; nums[i] &le; 1,000,000"],
    hints=["Each element can only take values from a short chain. Write down which values an odd element and an even element can reach.",
           "An odd x can become x or 2x. An even x can become any of x, x/2, x/4, ... down to its odd part. So you can first double every odd element and then only ever need to <em>decrease</em> elements.",
           "After doubling the odds, everything can only be halved (while even). Repeatedly halve the maximum with a max-heap, tracking the current minimum and the best max - min seen; stop when the maximum is odd."],
    editorial=["Normalise: double every odd number. Now every element is even-or-odd-but-already-maximal, and the set of values an element can take is its current value divided by 2 repeatedly, down to its odd part. The doubled value is the largest in each chain, so the starting state has every element at its maximum.",
               "From there the only useful move is to lower the current maximum, because lowering anything else cannot reduce the max. Keep a max-heap and the minimum <code>mn</code> of the current values. Compute <code>max - mn</code> as a candidate, then if the maximum is even, halve it, update <code>mn</code> and repeat; if the maximum is odd it cannot be reduced and no later state can be better, so stop.",
               "Every element is halved at most about 21 times, so there are at most about 100,000 heap steps: O(n log n log M) time (M is the largest value), O(n) memory. The result is the minimum candidate seen."],
    time="O(n log M log n)", space="O(n)",
    solution='''import heapq


def minimumDeviation(nums):
    h = []
    mn = None
    for x in nums:
        if x % 2:
            x *= 2
        h.append(-x)
        if mn is None or x < mn:
            mn = x
    heapq.heapify(h)
    best = -h[0] - mn
    while True:
        x = -h[0]
        if x % 2:
            break
        x //= 2
        heapq.heapreplace(h, -x)
        if x < mn:
            mn = x
        best = min(best, -h[0] - mn)
    return best
''',
    tests=[[[1, 2, 3, 4]], [[4, 1, 5, 20, 3]], [[2, 10, 8]], [[7]], [[1, 1, 1]], [[3, 5]], [[1000000, 1]], [[999999, 999999]], [[16, 8, 4, 2]],
           [[9, 12, 5]]],
)
_r = rnd(8410)
p["tests"].append([[_r.randint(1, 1000000) for _ in range(5000)]])
p["tests"].append([[2 ** _r.randint(0, 17) * _r.choice([1, 3, 5, 7]) for _ in range(5000)]])
p["tests"].append([[_r.randint(1, 100) for _ in range(5000)]])


def b_dev(nums):
    start = tuple(nums)
    seen = {start}
    stack = [start]
    best = max(start) - min(start)
    while stack:
        t = stack.pop()
        best = min(best, max(t) - min(t))
        for i, x in enumerate(t):
            y = x // 2 if x % 2 == 0 else x * 2
            u = t[:i] + (y,) + t[i + 1:]
            if u not in seen:
                seen.add(u)
                stack.append(u)
    return best


def v_dev(tests):
    for t in tests:
        nums = t["args"][0]
        assert 1 <= len(nums) <= 5000 and all(1 <= x <= 1000000 for x in nums)


CHECKS["minimize-deviation-by-halving-and-doubling"] = (b_dev, lambda r: [[r.randint(1, 24) for _ in range(r.randint(1, 4))]], "exact")
VALIDATE["minimize-deviation-by-halving-and-doubling"] = v_dev

# ---------------------------------------------------------------- construct target array
p = add(
    id="build-target-from-ones-by-sums", title="Build Target From Ones by Sums", diff="Hard", topic="Heap", tier="extra",
    fn="canBuildTarget", params=[("target", "int[]")], ret="bool", cmp="exact",
    desc="<p>Start with an array of the same length as <code>target</code> in which every element is <code>1</code>. Then repeat the following step as often as you like: let <code>x</code> be the sum of all elements currently in the array, choose any index <code>i</code> and set <code>arr[i] = x</code>.</p><p>Return <code>true</code> if the array can become exactly <code>target</code>, element by element, and <code>false</code> otherwise.</p><pre>target = [9, 3, 5]  result = true\n[1, 1, 1] -> [1, 3, 1] -> [1, 3, 5] -> [9, 3, 5]\n\ntarget = [1, 1, 1, 2]  result = false\ntarget = [8, 5]        result = true\ntarget = [1]           result = true (nothing to do)</pre>",
    constraints=["1 &le; target.length &le; 5,000", "1 &le; target[i] &le; 1,000,000,000"],
    hints=["Run the process backwards. Which element of the final array must have been written last?",
           "The last written element is the largest one, and it equals the total of the array at that moment. Undo it: the previous value was max - (sum of the other elements).",
           "Use a max-heap and the running total. Replace the max by max mod (sum of the others) instead of subtracting one step at a time, and reject when the others sum to 0, the result would be 0, or the others already exceed the max."],
    editorial=["Going forward the choices are huge, but backwards the move is forced. In the last step the written element became the sum of the whole array, so it is strictly larger than every other element (for length at least 2), i.e. it is the maximum. Undo it: the old value of that cell is <code>max - rest</code> where <code>rest</code> is the sum of the other elements. If this is not at least 1 the target is impossible.",
               "Subtracting <code>rest</code> one time at a time can take up to 1e9 steps, as in <code>[1, 1000000000]</code>. The same cell will be the maximum again and again until it drops below <code>rest</code>, so jump directly: the new value is <code>max % rest</code>. If that is 0, the cell would have to be 0 (impossible), except when <code>rest = 1</code>, where the cell can be reduced by 1s all the way down to 1, so the answer is true. Stop with true when the maximum is 1.",
               "Each jump is a Euclid-style step, which at least halves the maximum, so there are O(log M) jumps per element and O(n + log M) heap operations in total. Time O(n + k log n) with k the number of jumps, memory O(n). A single-element array is true only for <code>[1]</code>: the rest is 0, which the loop rejects."],
    time="O(n + k log n)", space="O(n)",
    solution='''import heapq


def canBuildTarget(target):
    total = sum(target)
    h = [-x for x in target]
    heapq.heapify(h)
    while -h[0] > 1:
        m = -heapq.heappop(h)
        rest = total - m
        if rest == 1:
            return True
        if rest == 0 or rest >= m:
            return False
        new = m % rest
        if new == 0:
            return False
        total = rest + new
        heapq.heappush(h, -new)
    return True
''',
    tests=[[[9, 3, 5]], [[1, 1, 1, 2]], [[8, 5]], [[1]], [[2]], [[1, 1]], [[1, 2]], [[2, 2]], [[1, 1000000000]], [[5, 1, 1]],
           [[3, 7, 17]], [[1, 1, 1, 1, 1, 1000]], [[12, 5, 3]], [[999999999, 1000000000]]],
)
_r = rnd(8411)


def _fwd(n, steps, cap=10 ** 9):
    a = [1] * n
    for _ in range(steps):
        s = sum(a)
        if s > cap:
            break
        a[_r.randrange(n)] = s
    return a


_big = [1] * 5000
_cur = list(_big)
for _ in range(25):
    s = sum(_cur)
    if s > 10 ** 9:
        break
    _cur[_r.randrange(5000)] = s
p["tests"].append([_cur])
_bad = list(_cur)
_bad[_bad.index(max(_bad))] += 1
p["tests"].append([_bad])
_f = [1, 1]
while _f[-1] + _f[-2] <= 10 ** 9:
    _f.append(_f[-1] + _f[-2])
p["tests"].append([[_f[-1], _f[-2]]])
p["tests"].append([[_f[-2], _f[-1]]])
p["tests"].append([[1] * 5000])


def b_target(target):
    n = len(target)
    start = tuple([1] * n)
    goal = tuple(target)
    seen = {start}
    stack = [start]
    while stack:
        t = stack.pop()
        if t == goal:
            return True
        s = sum(t)
        for i in range(n):
            if s <= goal[i]:
                u = t[:i] + (s,) + t[i + 1:]
                if all(u[j] <= goal[j] for j in range(n)) and u not in seen:
                    seen.add(u)
                    stack.append(u)
    return False


def g_target(r):
    n = r.randint(1, 4)
    if r.random() < 0.55:
        a = [1] * n
        for _ in range(r.randint(0, 6)):
            s = sum(a)
            if s > 40:
                break
            a[r.randrange(n)] = s
        if r.random() < 0.3:
            a[r.randrange(n)] += r.randint(-1, 2)
            a = [max(1, x) for x in a]
        return [a]
    return [[r.randint(1, 20) for _ in range(n)]]


def v_target(tests):
    for t in tests:
        a = t["args"][0]
        assert 1 <= len(a) <= 5000 and all(1 <= x <= 10 ** 9 for x in a)
    assert any(t["expected"] for t in tests) and any(not t["expected"] for t in tests)


CHECKS["build-target-from-ones-by-sums"] = (b_target, g_target, "exact")
VALIDATE["build-target-from-ones-by-sums"] = v_target
