"""Problems: heap, two-heap median patterns (running median variants, sliding windows, IPO-like, balance). See data/lib.py."""
from lib import add, rnd, CHECKS, VALIDATE, gen_arr  # noqa: F401

INT_MIN, INT_MAX = -(2 ** 31), 2 ** 31 - 1
B = 10 ** 9
T = "Heap"

# Shared helper pasted into several reference solutions: two heaps (lower half as a max-heap, upper half as a
# min-heap) with lazy removal by id and running sums of both halves.
TWO_HEAPS = '''import heapq


class TwoHeaps:
    """lo = max-heap of the lower half (size = size of hi, or one more), hi = min-heap of the upper half."""

    def __init__(self):
        self.lo, self.hi = [], []          # entries (-value, id) and (value, id)
        self.dead = set()                  # ids removed but still sitting inside a heap
        self.side = {}                     # id -> 0 (in lo) or 1 (in hi)
        self.nlo = self.nhi = 0            # live sizes
        self.slo = self.shi = 0            # live sums

    def _clean(self, h):
        while h and h[0][1] in self.dead:
            self.dead.discard(heapq.heappop(h)[1])

    def add(self, i, x):
        self._clean(self.lo)
        if self.nlo == 0 or x <= -self.lo[0][0]:
            heapq.heappush(self.lo, (-x, i))
            self.side[i] = 0
            self.nlo += 1
            self.slo += x
        else:
            heapq.heappush(self.hi, (x, i))
            self.side[i] = 1
            self.nhi += 1
            self.shi += x
        self._balance()

    def remove(self, i, x):
        if self.side.pop(i) == 0:
            self.nlo -= 1
            self.slo -= x
        else:
            self.nhi -= 1
            self.shi -= x
        self.dead.add(i)
        self._balance()

    def _balance(self):
        while self.nlo > self.nhi + 1:
            self._clean(self.lo)
            nx, i = heapq.heappop(self.lo)
            heapq.heappush(self.hi, (-nx, i))
            self.side[i] = 1
            self.nlo -= 1
            self.nhi += 1
            self.slo += nx
            self.shi -= nx
        while self.nhi > self.nlo:
            self._clean(self.hi)
            x, i = heapq.heappop(self.hi)
            heapq.heappush(self.lo, (-x, i))
            self.side[i] = 0
            self.nhi -= 1
            self.nlo += 1
            self.shi -= x
            self.slo += x

    def median2(self):
        """Twice the median of the live values."""
        self._clean(self.lo)
        if self.nlo > self.nhi:
            return -2 * self.lo[0][0]
        self._clean(self.hi)
        return -self.lo[0][0] + self.hi[0][0]

    def cost(self):
        """Minimum total |x - c| over the live values."""
        self._clean(self.lo)
        med = -self.lo[0][0]
        return self.shi - self.slo + (self.nlo - self.nhi) * med


'''


def doubled_median(sorted_vals):
    m = len(sorted_vals)
    return 2 * sorted_vals[m // 2] if m % 2 else sorted_vals[m // 2 - 1] + sorted_vals[m // 2]


def gather_cost(vals):
    """Brute force: try every element as the meeting point."""
    return min(sum(abs(x - c) for x in vals) for c in vals)


# ================================================================ EASY

# ---------------------------------------------------------------- validate two-heap median split
p = add(
    id="validate-two-heap-median-split", tier="extra", title="Validate a Two-Heap Median Split", diff="Easy", topic=T,
    fn="medianOfHalves", params=[("lower", "int[]"), ("upper", "int[]")], ret="int[]", cmp="exact",
    desc="<p>A data structure keeps a growing set of numbers split into two halves: the <code>lower</code> half (the smaller numbers) and the <code>upper</code> half (the larger ones). Each half is given as an array in arbitrary order.</p><p>The split is <strong>valid</strong> when all three conditions hold:</p><ul><li><code>lower</code> is not empty;</li><li><code>lower</code> has the same number of elements as <code>upper</code>, or exactly one more;</li><li>every value of <code>lower</code> is less than or equal to every value of <code>upper</code> (equal values on both sides are fine).</li></ul><p>If the split is valid, return a one-element array holding <strong>twice the median</strong> of all the numbers (the median of an even count is the average of the two middle values, so doubling keeps everything an integer). If the split is not valid, return an empty array.</p><pre>lower = [3, 1, 2], upper = [5, 4, 9]   -> [7]   (middle values 3 and 4)\nlower = [4, 1, 3], upper = [7, 5]      -> [8]   (median 4, doubled)\nlower = [2, 9],    upper = [5]         -> []    (9 is larger than 5)</pre>",
    constraints=["0 &le; lower.length, upper.length &le; 4,000", "-10<sup>9</sup> &le; lower[i], upper[i] &le; 10<sup>9</sup>", "The arrays are not sorted and may contain duplicates"],
    hints=["Check the sizes first: <code>lower</code> must be non-empty and its size may exceed the size of <code>upper</code> by 0 or 1 only.",
           "You do not need to compare every pair. The order condition holds exactly when the largest value of <code>lower</code> is at most the smallest value of <code>upper</code>.",
           "If valid: with an odd total the median is <code>max(lower)</code> (answer twice that); with an even total it is the mean of <code>max(lower)</code> and <code>min(upper)</code> (answer their sum)."],
    editorial=["This is exactly the invariant a two-heap median structure maintains, written as a checker. The roots of the two heaps are <code>max(lower)</code> and <code>min(upper)</code>, so the whole ordering requirement collapses to one comparison between those two values, and the median can be read from them.",
               "Sizes: if <code>lower</code> is larger by one, the total is odd and the median is the extra middle element, <code>max(lower)</code>. If the sizes are equal, the total is even and the two middle values are <code>max(lower)</code> and <code>min(upper)</code>; their sum is twice the median.",
               "One pass over each array finds the maximum and the minimum, so the time is O(n) with O(1) extra space. Sorting everything would also work but costs O(n log n) and does not check the split."],
    time="O(n)", space="O(1)",
    solution='''def medianOfHalves(lower, upper):
    a, b = len(lower), len(upper)
    if a == 0 or a - b not in (0, 1):
        return []
    top = max(lower)
    if b and min(upper) < top:
        return []
    if a > b:
        return [2 * top]
    return [top + min(upper)]
''',
    tests=[[[3, 1, 2], [5, 4, 9]], [[4, 1, 3], [7, 5]], [[2, 9], [5]], [[], []], [[7], []], [[], [7]], [[5, 5], [5, 5]],
           [[1, 2, 3], [3]], [[-4, -9], [-4, 0]], [[B], [B]], [[-B, -B, -B], [-B, -B]], [[1, 2, 3], []], [[1], [2, 3]]],
)
_r = rnd(9101)
_pool = sorted(_r.randint(-B, B) for _ in range(6000))
_lo, _hi = _pool[:3000], _pool[3000:]
_r.shuffle(_lo); _r.shuffle(_hi)
p["tests"].append([_lo, _hi])
_lo2 = _lo[:]; _hi2 = _hi[:]
_hi2[_r.randrange(3000)] = _pool[10] - 1  # one value of the upper half drops below max(lower)
p["tests"].append([_lo2, _hi2])
_pool = sorted(_r.randint(-5, 5) for _ in range(5001))
_lo, _hi = _pool[:2501], _pool[2501:]
_r.shuffle(_lo); _r.shuffle(_hi)
p["tests"].append([_lo, _hi])


def b_halves(lower, upper):
    if not lower or len(lower) - len(upper) not in (0, 1):
        return []
    if not all(a <= b for a in lower for b in upper):
        return []
    s = sorted(lower + upper)
    return [doubled_median(s)]


def g_halves(r):
    pool = sorted(r.randint(-4, 4) for _ in range(r.randint(0, 9)))
    k = (len(pool) + 1) // 2
    lo, hi = pool[:k], pool[k:]
    c = r.random()
    if c < 0.25 and pool:
        lo, hi = pool[:r.randint(0, len(pool))], pool[r.randint(0, len(pool)):]
    elif c < 0.5 and lo and hi:
        lo[r.randrange(len(lo))] += r.randint(0, 4)
    r.shuffle(lo)
    r.shuffle(hi)
    return [lo, hi]


def v_halves(tests):
    for t in tests:
        lo, hi = t["args"]
        assert len(lo) <= 4000 and len(hi) <= 4000
        assert all(-B <= x <= B for x in lo + hi)


CHECKS["validate-two-heap-median-split"] = (b_halves, g_halves, "exact")
VALIDATE["validate-two-heap-median-split"] = v_halves

# ---------------------------------------------------------------- count rising medians
p = add(
    id="count-rising-medians", tier="extra", title="Count Rising Medians", diff="Easy", topic=T,
    fn="countRisingMedians", params=[("nums", "int[]")], ret="int", cmp="exact",
    desc="<p>Numbers arrive one at a time in the order of <code>nums</code>. After each arrival, the <strong>median</strong> of everything received so far is defined: the middle value of the sorted numbers for an odd count, or the average of the two middle values for an even count.</p><p>Count how many arrivals made the median <strong>strictly larger</strong> than it was right after the previous arrival. The first arrival has no predecessor and never counts.</p><pre>nums = [5, 2, 8, 1, 9, 9]\nmedians after each arrival: 5, 3.5, 5, 3.5, 5, 6.5\nrises: 3.5 -> 5, 3.5 -> 5, 5 -> 6.5   so the answer is 3</pre>",
    constraints=["1 &le; nums.length &le; 5,000", "-10<sup>9</sup> &le; nums[i] &le; 10<sup>9</sup>"],
    hints=["Sorting every prefix is too slow for large inputs; you only need the middle of the sorted prefix.",
           "To avoid fractions, compare <em>twice</em> the median: the middle value doubled for an odd count, the sum of the two middle values for an even count.",
           "Keep the lower half in a max-heap and the upper half in a min-heap with sizes differing by at most one, then read the median from the two roots after each insertion."],
    editorial=["Maintain two heaps: <code>lo</code>, a max-heap with the smaller half (it gets the extra element when the count is odd), and <code>hi</code>, a min-heap with the larger half. A new number goes into <code>lo</code> if it is at most the root of <code>lo</code>, otherwise into <code>hi</code>; then one root is moved across if the sizes drift apart by more than allowed.",
               "After each insertion the doubled median is <code>2 * lo.root</code> for an odd count and <code>lo.root + hi.root</code> for an even count. Comparing doubled medians with the previous one counts the rises with exact integer arithmetic.",
               "Each insertion costs O(log n), so the total is O(n log n) time and O(n) space. Doubled values reach at most 2 * 10<sup>9</sup>, which still fits a signed 32-bit integer."],
    time="O(n log n)", space="O(n)",
    solution='''import heapq


def countRisingMedians(nums):
    lo, hi = [], []  # lo: max-heap (negated) of the lower half, hi: min-heap of the upper half
    prev = None
    rises = 0
    for x in nums:
        if not lo or x <= -lo[0]:
            heapq.heappush(lo, -x)
        else:
            heapq.heappush(hi, x)
        if len(lo) > len(hi) + 1:
            heapq.heappush(hi, -heapq.heappop(lo))
        elif len(hi) > len(lo):
            heapq.heappush(lo, -heapq.heappop(hi))
        cur = -2 * lo[0] if len(lo) > len(hi) else -lo[0] + hi[0]
        if prev is not None and cur > prev:
            rises += 1
        prev = cur
    return rises
''',
    tests=[[[5, 2, 8, 1, 9, 9]], [[7]], [[1, 2]], [[2, 1]], [[3, 3, 3, 3]], [[1, 2, 3, 4, 5, 6]], [[6, 5, 4, 3, 2, 1]],
           [[-1, -2, -3, -4]], [[B, -B, B, -B]], [[-B, B]], [[0, 0, 5, -5, 0]], [[10, 1, 10, 1, 10, 1]]],
)
_r = rnd(9102)
p["tests"].append([[_r.randint(-B, B) for _ in range(5000)]])
p["tests"].append([[_r.randint(-20, 20) for _ in range(5000)]])
p["tests"].append([[(i * 7919) % 10007 - 5000 for i in range(5000)]])


def b_rising(nums):
    prev = None
    c = 0
    for i in range(len(nums)):
        s = sorted(nums[:i + 1])
        m = len(s)
        # compare as fractions: median = s[m//2] (odd) or (s[m//2-1]+s[m//2])/2
        cur = (s[m // 2], 1) if m % 2 else (s[m // 2 - 1] + s[m // 2], 2)
        if prev is not None and cur[0] * prev[1] > prev[0] * cur[1]:
            c += 1
        prev = cur
    return c


def v_rising(tests):
    for t in tests:
        nums = t["args"][0]
        assert 1 <= len(nums) <= 5000 and all(-B <= x <= B for x in nums)


CHECKS["count-rising-medians"] = (b_rising, lambda r: [[r.randint(-6, 6) for _ in range(r.randint(1, 14))]], "exact")
VALIDATE["count-rising-medians"] = v_rising

# ================================================================ MEDIUM

# ---------------------------------------------------------------- prefix gathering cost
p = add(
    id="prefix-gathering-costs", tier="common", title="Gathering Cost of Every Prefix", diff="Medium", topic=T,
    fn="prefixGatherCosts", params=[("positions", "int[]")], ret="int[]", cmp="exact",
    desc="<p>Houses are built one after another along a straight road; <code>positions[i]</code> is the coordinate of the i-th house. After each new house is built, the residents want to choose one meeting point (any integer coordinate) that minimises the <strong>total walking distance</strong> of all houses built so far, where a house at <code>x</code> walks <code>|x - meeting point|</code>.</p><p>Return an array whose i-th entry is that minimum total distance once the first <code>i + 1</code> houses exist.</p><pre>positions = [4, 1, 7, 2]\n[4]          -> 0\n[4, 1]       -> 3   (meet anywhere from 1 to 4)\n[4, 1, 7]    -> 6   (meet at 4: 0 + 3 + 3)\n[4, 1, 7, 2] -> 8   (meet at 2: 2 + 1 + 5 + 0)\nanswer = [0, 3, 6, 8]</pre>",
    constraints=["1 &le; positions.length &le; 3,500", "-10<sup>5</sup> &le; positions[i] &le; 10<sup>5</sup>", "Every answer fits in a 32-bit signed integer"],
    hints=["The best meeting point for a set of numbers is always a median of the set. The hard part is keeping the median while numbers keep arriving.",
           "Split the houses into a lower half and an upper half (two heaps). Everything in the lower half is walking right to the median, everything in the upper half is walking left.",
           "Keep the sum of each half. With median <code>m</code>: cost = (sum of upper half - |upper| * m) + (|lower| * m - sum of lower half)."],
    editorial=["For a multiset of points, <code>sum |x - c|</code> is minimised at a median. Moving the meeting point one step to the right helps the points on its right and hurts the points on its left, so the optimum sits where both sides are balanced, the median. For an even count any point between the two middle values is optimal, so the lower median gives the same cost.",
               "Hold the smaller half in a max-heap <code>lo</code> and the larger half in a min-heap <code>hi</code>, sizes equal or <code>lo</code> one larger, and also track <code>sum(lo)</code> and <code>sum(hi)</code>. The median is the root of <code>lo</code>. Everything in <code>hi</code> is at least the median and everything in <code>lo</code> is at most the median, so no absolute values are needed: cost = <code>sum(hi) - sum(lo) + (|lo| - |hi|) * median</code>.",
               "Each insertion costs O(log n) and the cost is read in O(1), for O(n log n) total. A sorted list with binary insertion is O(n<sup>2</sup>) in the worst case because of the shifting."],
    time="O(n log n)", space="O(n)",
    solution='''import heapq


def prefixGatherCosts(positions):
    lo, hi = [], []  # lo: max-heap (negated) of the lower half, hi: min-heap of the upper half
    slo = shi = 0
    out = []
    for x in positions:
        if not lo or x <= -lo[0]:
            heapq.heappush(lo, -x)
            slo += x
        else:
            heapq.heappush(hi, x)
            shi += x
        if len(lo) > len(hi) + 1:
            y = -heapq.heappop(lo)
            heapq.heappush(hi, y)
            slo -= y
            shi += y
        elif len(hi) > len(lo):
            y = heapq.heappop(hi)
            heapq.heappush(lo, -y)
            shi -= y
            slo += y
        med = -lo[0]
        out.append(shi - slo + (len(lo) - len(hi)) * med)
    return out
''',
    tests=[[[4, 1, 7, 2]], [[5]], [[3, 3, 3]], [[1, 100000]], [[-100000, 100000, -100000, 100000]], [[1, 2, 3, 4, 5, 6]],
           [[6, 5, 4, 3, 2, 1]], [[-5, -1, -3]], [[0, 0, 0, 7]], [[10, -10, 20, -20, 30, -30, 0]]],
)
_r = rnd(9103)
p["tests"].append([[_r.randint(-10 ** 5, 10 ** 5) for _ in range(3500)]])
p["tests"].append([[(-10 ** 5 if i % 2 else 10 ** 5) for i in range(2500)]])
p["tests"].append([[_r.randint(-30, 30) for _ in range(3000)]])


def b_prefix_cost(positions):
    return [gather_cost(positions[:i + 1]) for i in range(len(positions))]


def v_prefix_cost(tests):
    for t in tests:
        a = t["args"][0]
        assert 1 <= len(a) <= 3500 and all(-10 ** 5 <= x <= 10 ** 5 for x in a)


CHECKS["prefix-gathering-costs"] = (b_prefix_cost, lambda r: [[r.randint(-8, 8) for _ in range(r.randint(1, 10))]], "exact")
VALIDATE["prefix-gathering-costs"] = v_prefix_cost

# ---------------------------------------------------------------- fewest projects to reach a target (IPO-like)
p = add(
    id="fewest-projects-to-reach-target", tier="common", title="Fewest Projects to Reach a Target", diff="Medium", topic=T,
    fn="fewestProjects", params=[("target", "int"), ("capital", "int"), ("costs", "int[]"), ("profits", "int[]")], ret="int", cmp="exact",
    desc="<p>You start with <code>capital</code> coins and want to own at least <code>target</code> coins. There are <code>n</code> projects. Project <code>i</code> can be started only if you currently own at least <code>costs[i]</code> coins; starting it does not use up the coins, and when it finishes you immediately gain <code>profits[i]</code> coins. Each project can be done at most once, one at a time.</p><p>Return the <strong>fewest projects</strong> needed to reach <code>target</code> coins, or <code>-1</code> if it is impossible. If you already own enough coins, the answer is 0.</p><pre>target = 10, capital = 2\ncosts   = [2, 5, 3, 9]\nprofits = [3, 4, 2, 8]\nstart project 0 (cost 2)  -> 5 coins\nstart project 1 (cost 5)  -> 9 coins\nstart project 3 (cost 9)  -> 17 coins\nanswer = 3   (no two projects can reach 10)</pre>",
    constraints=["0 &le; target, capital &le; 10<sup>9</sup>", "1 &le; n = costs.length = profits.length &le; 3,000", "0 &le; costs[i] &le; 10<sup>9</sup>", "1 &le; profits[i] &le; 10<sup>6</sup>"],
    hints=["Try small cases by hand: after doing exactly <code>j</code> projects, what is the largest amount of capital you could have?",
           "Greedy: at every step, among the projects you can afford right now, take the one with the largest profit. Taking a smaller profit never leaves you with more capital or more choices.",
           "Sort the projects by cost. Move every project that has become affordable into a max-heap keyed by profit, pop the best one, and repeat until the capital reaches the target or the heap runs dry."],
    editorial=["Because every profit is positive, owning more coins never hurts, and a project that is affordable stays affordable. Take any plan with j projects; swapping one of its projects for an affordable project of larger profit cannot reduce the capital at any later moment. So the greedy plan (always the most profitable affordable project) maximises the capital after exactly j projects, for every j at once. The answer is therefore the first j at which greedy reaches the target.",
               "Implementation: sort projects by cost; a pointer feeds every project with <code>cost &le; capital</code> into a max-heap of profits. Pop the largest profit, add it to the capital, count one project, and feed newly affordable projects. If the heap is empty while the target has not been reached, nothing more can be started and the answer is -1.",
               "Sorting costs O(n log n) and each project enters and leaves the heap once, so the total time is O(n log n) and the space is O(n). This is the same engine as the classic &ldquo;maximise capital with k projects&rdquo; problem, but asking for the smallest count instead of the best final capital."],
    time="O(n log n)", space="O(n)",
    solution='''import heapq


def fewestProjects(target, capital, costs, profits):
    order = sorted(range(len(costs)), key=costs.__getitem__)
    heap = []  # negated profits of affordable projects
    j = 0
    count = 0
    while capital < target:
        while j < len(order) and costs[order[j]] <= capital:
            heapq.heappush(heap, -profits[order[j]])
            j += 1
        if not heap:
            return -1
        capital -= heapq.heappop(heap)
        count += 1
    return count
''',
    tests=[[10, 2, [2, 5, 3, 9], [3, 4, 2, 8]], [5, 5, [1], [1]], [0, 0, [0], [1]], [6, 1, [2], [9]], [20, 1, [1, 1, 1], [3, 3, 3]],
           [8, 0, [0, 1, 3, 100], [1, 2, 5, 50]], [7, 3, [3, 3, 3], [2, 2, 2]], [100, 10, [10, 20, 40, 80], [10, 20, 40, 80]],
           [1000000000, 0, [0, 500000000], [1000000, 1000000]], [30, 1, [1, 2, 4, 8, 16], [1, 2, 4, 8, 16]], [15, 4, [4, 4, 100], [5, 5, 20]]],
)
_r = rnd(9104)
_n = 3000
_costs = [_r.randint(0, 1500) for _ in range(_n)]
_profits = [_r.randint(1, 40) for _ in range(_n)]
p["tests"].append([50000, 10, _costs, _profits])
_costs = sorted(_r.randint(0, 120000) for _ in range(_n))
_profits = [_r.randint(1, 60) + (c // 400) for c in _costs]
p["tests"].append([120000, 5, _costs, _profits])
_costs = [i for i in range(_n)]  # chain: project i needs i coins and pays 1
p["tests"].append([_n + 100, 0, _costs, [1] * _n])


def b_fewest(target, capital, costs, profits):
    n = len(costs)
    best = -1
    reach = [False] * (1 << n)
    reach[0] = True
    for mask in range(1 << n):
        if not reach[mask]:
            continue
        cap = capital + sum(profits[i] for i in range(n) if mask >> i & 1)
        if cap >= target:
            c = bin(mask).count("1")
            if best == -1 or c < best:
                best = c
        for i in range(n):
            if not mask >> i & 1 and cap >= costs[i]:
                reach[mask | 1 << i] = True
    return best


def g_fewest(r):
    n = r.randint(1, 8)
    costs = [r.randint(0, 12) for _ in range(n)]
    profits = [r.randint(1, 6) for _ in range(n)]
    return [r.randint(0, 30), r.randint(0, 6), costs, profits]


def v_fewest(tests):
    for t in tests:
        tg, cap, costs, profits = t["args"]
        assert 0 <= tg <= B and 0 <= cap <= B and 1 <= len(costs) == len(profits) <= 3000
        assert all(0 <= c <= B for c in costs) and all(1 <= x <= 10 ** 6 for x in profits)


CHECKS["fewest-projects-to-reach-target"] = (b_fewest, g_fewest, "exact")
VALIDATE["fewest-projects-to-reach-target"] = v_fewest

# ---------------------------------------------------------------- median of recent events
p = add(
    id="median-of-recent-events", tier="common", title="Median of Recent Events", diff="Medium", topic=T,
    fn="recentMedians", params=[("events", "int[][]"), ("span", "int")], ret="int[]", cmp="exact",
    desc="<p>A sensor reports readings over time. <code>events[i] = [time, value]</code>, and the times are given in non-decreasing order (several readings can share one time). After each event arrives at time <code>t</code>, look at the <strong>recent window</strong>: all events so far whose time is greater than <code>t - span</code> (so times in <code>(t - span, t]</code>, the new event included).</p><p>For every event, report <strong>twice the median</strong> of the values in its recent window. The median of an even count is the average of the two middle values, so doubling keeps everything an integer.</p><pre>events = [[1,5], [2,1], [4,9], [5,3], [9,7]], span = 3\nt=1: window {5}        -> 10\nt=2: window {5, 1}     -> 1 + 5 = 6\nt=4: times 2..4 {1, 9} -> 10\nt=5: times 3..5 {9, 3} -> 12\nt=9: times 7..9 {7}    -> 14\nanswer = [10, 6, 10, 12, 14]</pre>",
    constraints=["1 &le; events.length &le; 2,000", "0 &le; time &le; 10<sup>9</sup>, times are non-decreasing", "-10<sup>9</sup> &le; value &le; 10<sup>9</sup>", "1 &le; span &le; 10<sup>9</sup>"],
    hints=["Events leave the window in the same order in which they arrived, because times never decrease. A pointer to the oldest live event is enough to know what to expire.",
           "Two heaps (lower half and upper half) give the median of a growing set. Removing a specific element from the middle of a heap is the problem.",
           "Use lazy deletion: remember that an event expired, but only physically pop it when it reaches the top of its heap. Track the number of live elements per heap separately to decide when to rebalance."],
    editorial=["Combine two ideas. First, the two-heap median: a max-heap <code>lo</code> with the smaller half and a min-heap <code>hi</code> with the larger half, <code>lo</code> holding the extra element for odd counts. Second, lazy deletion: heaps cannot delete arbitrary elements cheaply, so when an event expires we mark its id as dead, decrease the live count of the heap it belongs to, and only discard the stale entry when it floats to the top.",
               "For each new event, first expire every old event with <code>time &le; t - span</code> (a queue pointer walks over them), then insert the new value on the correct side, then rebalance using the <em>live</em> counts. Before reading a root or comparing against it, clean dead entries off the top of that heap. Which heap an element lives in is recorded when it is inserted or moved.",
               "Every event is pushed, moved and popped a constant number of times at O(log n) each, so the time is O(n log n); space is O(n). A sorted list rebuilt per event would be O(n<sup>2</sup> log n) in the worst case."],
    time="O(n log n)", space="O(n)",
    solution=TWO_HEAPS + '''def recentMedians(events, span):
    t = TwoHeaps()
    out = []
    old = 0
    for i, (time, value) in enumerate(events):
        while events[old][0] <= time - span:
            t.remove(old, events[old][1])
            old += 1
        t.add(i, value)
        out.append(t.median2())
    return out
''',
    tests=[[[[1, 5], [2, 1], [4, 9], [5, 3], [9, 7]], 3], [[[0, 4]], 1], [[[5, 1], [5, 2], [5, 3]], 1], [[[1, 3], [2, 3], [3, 3]], 10],
           [[[1, 1], [2, 2], [3, 3], [4, 4]], 2], [[[0, 5], [10, 6], [20, 7]], 5], [[[1, -B], [1, B], [2, B]], 2],
           [[[1, 9], [2, 8], [3, 7], [4, 6], [5, 5], [6, 4]], 3], [[[0, 1], [1, 2], [2, 3], [3, 4], [4, 5]], B],
           [[[B - 1, 5], [B, 2]], 1], [[[1, 10], [3, 1], [3, 1], [4, 10], [8, 5], [8, 5]], 4]],
)
_r = rnd(9105)
_t = 0
_ev = []
for _ in range(2000):
    _t += _r.choice([0, 0, 1, 1, 2, 3])
    _ev.append([_t, _r.randint(-10 ** 6, 10 ** 6)])
p["tests"].append([_ev, 40])
_ev = [[i // 3, _r.randint(-1000, 1000)] for i in range(2000)]
p["tests"].append([_ev, 700])
_ev = [[i, _r.randint(-B, B)] for i in range(1500)]
p["tests"].append([_ev, 3000])


def b_recent(events, span):
    out = []
    for i, (t, _) in enumerate(events):
        vals = sorted(v for (tt, v) in events[:i + 1] if tt > t - span)
        out.append(doubled_median(vals))
    return out


def g_recent(r):
    n = r.randint(1, 12)
    t = r.randint(0, 3)
    ev = []
    for _ in range(n):
        t += r.choice([0, 0, 1, 2, 3])
        ev.append([t, r.randint(-6, 6)])
    return [ev, r.randint(1, 6)]


def v_recent(tests):
    for t in tests:
        ev, span = t["args"]
        assert 1 <= len(ev) <= 2000 and 1 <= span <= B
        assert all(0 <= a <= B and -B <= v <= B for a, v in ev)
        assert all(ev[i][0] <= ev[i + 1][0] for i in range(len(ev) - 1))


CHECKS["median-of-recent-events"] = (b_recent, g_recent, "exact")
VALIDATE["median-of-recent-events"] = v_recent

# ---------------------------------------------------------------- median with deletions
p = add(
    id="median-with-deletions", tier="common", title="Median with Insertions and Deletions", diff="Medium", topic=T,
    fn="medianAfterEachOperation", params=[("ops", "int[][]")], ret="int[]", cmp="exact",
    desc="<p>A collection of integers (duplicates allowed) starts empty and is changed by a list of operations. <code>ops[i] = [type, x]</code>:</p><ul><li><code>type = 1</code>: insert the value <code>x</code>;</li><li><code>type = 2</code>: delete <strong>one</strong> occurrence of the value <code>x</code> (it is guaranteed to be present).</li></ul><p>The collection is never empty after any operation. After each operation, report <strong>twice the median</strong> of the collection (the middle value for an odd size, the sum of the two middle values for an even size).</p><pre>ops = [[1,5], [1,2], [1,8], [2,2], [1,1]]\n{5}       -> 10\n{2,5}     -> 7\n{2,5,8}   -> 10\ndelete 2: {5,8}   -> 13\ninsert 1: {1,5,8} -> 10\nanswer = [10, 7, 10, 13, 10]</pre>",
    constraints=["1 &le; ops.length &le; 2,500", "type is 1 or 2; -10<sup>9</sup> &le; x &le; 10<sup>9</sup>", "A deletion always names a value that is currently present", "The collection is non-empty after every operation"],
    hints=["Two heaps handle insertions nicely. What makes a deletion hard is that the value may be buried deep inside one of the heaps.",
           "You can tell which heap holds <code>x</code>: if <code>x</code> is at most the root of the lower half (after cleaning), it is in the lower heap, otherwise in the upper heap.",
           "Do not search for it. Record a pending deletion for that heap (a counter per value), shrink that heap's live size, rebalance, and discard stale entries only when they reach the top."],
    editorial=["Keep a max-heap <code>lo</code> for the smaller half and a min-heap <code>hi</code> for the larger half, with <em>live</em> sizes tracked separately from the physical heap sizes. Every value in <code>lo</code> is at most every value in <code>hi</code>, so a value <code>x</code> that is at most the live root of <code>lo</code> must live in <code>lo</code>; otherwise it lives in <code>hi</code>. (If <code>x</code> equals the root it is safe to take it from <code>lo</code>.)",
               "A deletion records <code>x</code> in a per-heap &ldquo;pending removal&rdquo; counter and reduces that heap's live size. Whenever a root is needed, entries at the top whose value has a pending removal are popped and the counter is decremented. After the size change, the usual rebalance (move a root across until <code>lo</code> has the same number of live elements as <code>hi</code> or one more) restores the invariant.",
               "Keeping the pending counters separate for the two heaps matters: equal values can sit in both heaps, and a removal must only consume entries from the heap it was assigned to. Each operation is O(log n) amortised, giving O(n log n) time and O(n) space."],
    time="O(n log n)", space="O(n)",
    solution='''import heapq
from collections import Counter


def medianAfterEachOperation(ops):
    lo, hi = [], []              # lo: max-heap (negated values), hi: min-heap
    dlo, dhi = Counter(), Counter()  # pending (lazy) deletions per heap
    nlo = nhi = 0                # live sizes

    def clean_lo():
        while lo and dlo[-lo[0]] > 0:
            dlo[-lo[0]] -= 1
            heapq.heappop(lo)

    def clean_hi():
        while hi and dhi[hi[0]] > 0:
            dhi[hi[0]] -= 1
            heapq.heappop(hi)

    out = []
    for typ, x in ops:
        clean_lo()
        if typ == 1:
            if nlo == 0 or x <= -lo[0]:
                heapq.heappush(lo, -x)
                nlo += 1
            else:
                heapq.heappush(hi, x)
                nhi += 1
        else:
            if x <= -lo[0]:
                dlo[x] += 1
                nlo -= 1
            else:
                dhi[x] += 1
                nhi -= 1
        while nlo > nhi + 1:
            clean_lo()
            heapq.heappush(hi, -heapq.heappop(lo))
            nlo -= 1
            nhi += 1
        while nhi > nlo:
            clean_hi()
            heapq.heappush(lo, -heapq.heappop(hi))
            nhi -= 1
            nlo += 1
        clean_lo()
        if nlo > nhi:
            out.append(-2 * lo[0])
        else:
            clean_hi()
            out.append(-lo[0] + hi[0])
    return out
''',
    tests=[[[[1, 5], [1, 2], [1, 8], [2, 2], [1, 1]]], [[[1, 7]]], [[[1, 3], [1, 3], [2, 3]]], [[[1, 1], [1, 2], [2, 1]]],
           [[[1, 4], [1, 4], [1, 4], [2, 4], [2, 4]]], [[[1, -B], [1, B], [2, -B]]], [[[1, 1], [1, 2], [1, 3], [1, 4], [2, 1], [2, 2], [2, 3]]],
           [[[1, 5], [1, 5], [1, 1], [1, 9], [2, 5], [2, 9], [2, 1]]], [[[1, 2], [1, 10], [2, 10], [1, 10], [1, 0], [2, 2], [2, 0]]],
           [[[1, 3], [1, 1], [1, 2], [2, 3], [1, 3], [2, 1], [1, 7], [2, 2]]]],
)
_r = rnd(9106)


def _make_ops(r, n, lo_v, hi_v, p_del):
    cur = []
    ops = []
    for _ in range(n):
        if len(cur) >= 2 and r.random() < p_del:
            x = cur.pop(r.randrange(len(cur)))
            ops.append([2, x])
        else:
            x = r.randint(lo_v, hi_v)
            cur.append(x)
            ops.append([1, x])
    return ops


p["tests"].append([_make_ops(_r, 2500, -10 ** 6, 10 ** 6, 0.4)])
p["tests"].append([_make_ops(_r, 2500, -5, 5, 0.45)])
p["tests"].append([_make_ops(_r, 1500, -B, B, 0.3)])


def b_ops_median(ops):
    cur = []
    out = []
    for typ, x in ops:
        if typ == 1:
            cur.append(x)
        else:
            cur.remove(x)
        out.append(doubled_median(sorted(cur)))
    return out


def v_ops_median(tests):
    for t in tests:
        ops = t["args"][0]
        assert 1 <= len(ops) <= 2500
        cur = []
        for typ, x in ops:
            assert typ in (1, 2) and -B <= x <= B
            if typ == 1:
                cur.append(x)
            else:
                cur.remove(x)  # raises if absent
            assert cur, "collection became empty"


CHECKS["median-with-deletions"] = (b_ops_median, lambda r: [_make_ops(r, r.randint(1, 14), -4, 4, 0.4)], "exact")
VALIDATE["median-with-deletions"] = v_ops_median

# ---------------------------------------------------------------- running percentile
p = add(
    id="running-percentile", tier="common", title="Running Percentile of a Stream", diff="Medium", topic=T,
    fn="runningPercentile", params=[("nums", "int[]"), ("p", "int")], ret="int[]", cmp="exact",
    desc="<p>Numbers arrive one at a time in the order of <code>nums</code>. After each arrival, report the <strong>p-th percentile</strong> of everything received so far, using the nearest-rank rule: if <code>m</code> numbers have arrived, take the sorted numbers and report the one at 1-based rank <code>ceil(p * m / 100)</code>.</p><p>With <code>p = 50</code> this is the lower median; with <code>p = 100</code> it is the maximum so far.</p><pre>nums = [7, 3, 9, 1, 5, 8], p = 75\nm=1: rank 1 of [7]               -> 7\nm=2: rank 2 of [3,7]             -> 7\nm=3: rank 3 of [3,7,9]           -> 9\nm=4: rank 3 of [1,3,7,9]         -> 7\nm=5: rank 4 of [1,3,5,7,9]       -> 7\nm=6: rank 5 of [1,3,5,7,8,9]     -> 8\nanswer = [7, 7, 9, 7, 7, 8]</pre>",
    constraints=["1 &le; nums.length &le; 3,000", "-10<sup>9</sup> &le; nums[i] &le; 10<sup>9</sup>", "1 &le; p &le; 100"],
    hints=["The answer is the element of rank <code>r</code> in the sorted prefix, where <code>r = ceil(p * m / 100)</code> changes by at most one when a number arrives.",
           "Generalise the median trick: keep the <code>r</code> smallest numbers in a max-heap and all the others in a min-heap. The percentile is the root of the max-heap.",
           "On each arrival, push the number into the correct heap, then move roots across until the max-heap has exactly <code>r</code> elements for the new <code>m</code>."],
    editorial=["The median structure is the special case where the lower heap holds the first half. Here the lower max-heap <code>lo</code> must hold exactly the <code>r = ceil(p * m / 100)</code> smallest numbers, and then its root is precisely the rank-<code>r</code> element. The upper min-heap <code>hi</code> holds the rest.",
               "When a number <code>x</code> arrives (so <code>m</code> grows by one), put it into <code>lo</code> if it is at most the root of <code>lo</code>, otherwise into <code>hi</code>; this keeps the order between the heaps. Then compute the new <code>r</code>. Because <code>r</code> grows by at most one per arrival, but the insertion may have gone to the wrong side by one, a loop that moves roots from <code>lo</code> to <code>hi</code> while <code>lo</code> is too big, and from <code>hi</code> to <code>lo</code> while it is too small, runs at most a couple of iterations.",
               "Integer arithmetic for the rank: <code>(p * m + 99) // 100</code> is <code>ceil(p * m / 100)</code>. Since <code>p &ge; 1</code> the rank is at least 1, so <code>lo</code> is never empty. Overall O(n log n) time and O(n) space."],
    time="O(n log n)", space="O(n)",
    solution='''import heapq


def runningPercentile(nums, p):
    lo, hi = [], []  # lo: max-heap (negated) with the r smallest, hi: min-heap with the rest
    out = []
    for m, x in enumerate(nums, 1):
        if lo and x > -lo[0]:
            heapq.heappush(hi, x)
        else:
            heapq.heappush(lo, -x)
        r = (p * m + 99) // 100
        while len(lo) > r:
            heapq.heappush(hi, -heapq.heappop(lo))
        while len(lo) < r:
            heapq.heappush(lo, -heapq.heappop(hi))
        out.append(-lo[0])
    return out
''',
    tests=[[[7, 3, 9, 1, 5, 8], 75], [[5], 1], [[5], 100], [[4, 2, 6, 1], 50], [[4, 2, 6, 1], 100], [[4, 2, 6, 1], 1],
           [[3, 3, 3, 3, 3], 90], [[-5, 10, -3, 8, 0, 7, -9], 25], [[1, 2, 3, 4, 5, 6, 7, 8, 9, 10], 90],
           [[10, 9, 8, 7, 6, 5, 4, 3, 2, 1], 33], [[B, -B, 0, B, -B], 60]],
)
_r = rnd(9107)
p["tests"].append([[_r.randint(-B, B) for _ in range(3000)], 95])
p["tests"].append([[_r.randint(-100, 100) for _ in range(3000)], 50])
p["tests"].append([[_r.randint(-10 ** 6, 10 ** 6) for _ in range(3000)], 7])


def b_percentile(nums, p):
    out = []
    for m in range(1, len(nums) + 1):
        s = sorted(nums[:m])
        rank = -(-p * m // 100)
        out.append(s[rank - 1])
    return out


def v_percentile(tests):
    for t in tests:
        nums, p_ = t["args"]
        assert 1 <= len(nums) <= 3000 and 1 <= p_ <= 100 and all(-B <= x <= B for x in nums)


CHECKS["running-percentile"] = (b_percentile, lambda r: [[r.randint(-8, 8) for _ in range(r.randint(1, 14))], r.randint(1, 100)], "exact")
VALIDATE["running-percentile"] = v_percentile

# ---------------------------------------------------------------- two meeting points split
p = add(
    id="two-meeting-points-best-split", tier="extra", title="Two Meeting Points: Best Split", diff="Medium", topic=T,
    fn="bestSplitCost", params=[("positions", "int[]")], ret="int", cmp="exact",
    desc="<p>Houses stand along a road in the order given by <code>positions</code> (coordinates, not necessarily sorted). The road crew cuts the list into two non-empty groups: a <strong>prefix</strong> (the first <code>k</code> houses) and the remaining <strong>suffix</strong>, with <code>1 &le; k &lt; n</code>. Each group picks its own meeting point (any integer coordinate), and every house walks <code>|x - meeting point|</code> to the point of its group.</p><p>Return the smallest possible total walking distance over all choices of <code>k</code> and both meeting points.</p><pre>positions = [1, 2, 9, 10, 3]\nk=2: [1,2] costs 1, [9,10,3] costs 7 (meet at 9)  -> 8\nk=4: [1,2,9,10] costs 8, [3] costs 0               -> 8\nk=1: 0 + 14 = 14,   k=3: 8 + 7 = 15\nanswer = 8</pre>",
    constraints=["2 &le; positions.length &le; 5,000", "-10<sup>5</sup> &le; positions[i] &le; 10<sup>5</sup>"],
    hints=["For a fixed split the two groups are independent, and each group's best meeting point is a median. So you need the gathering cost of every prefix and of every suffix.",
           "Prefix costs: insert houses one by one into a two-heap median structure that also keeps the sum of each half. Suffix costs: do the same on the reversed array.",
           "Then answer = the minimum over <code>k</code> of <code>prefixCost[k] + suffixCost[k]</code>."],
    editorial=["Fix the cut position. The total distance is the cost of the prefix plus the cost of the suffix, and each part is minimised independently by meeting at its median. So the problem reduces to computing <code>cost(positions[0..k))</code> for all k and <code>cost(positions[k..n))</code> for all k, then taking the best sum.",
               "Prefix costs come from the standard two-heap routine: a max-heap for the lower half, a min-heap for the upper half, and sums of both halves; the cost after each insertion is <code>sum(hi) - sum(lo) + (|lo| - |hi|) * median</code>. Running the same routine on the reversed array yields the suffix costs.",
               "Two passes of O(n log n) plus an O(n) scan give O(n log n) time and O(n) space. Trying every split with a fresh sort would be O(n<sup>2</sup> log n). The two parts never share a meeting point, so no interaction needs to be modelled."],
    time="O(n log n)", space="O(n)",
    solution='''import heapq


def _prefix_costs(a):
    lo, hi = [], []
    slo = shi = 0
    out = []
    for x in a:
        if not lo or x <= -lo[0]:
            heapq.heappush(lo, -x)
            slo += x
        else:
            heapq.heappush(hi, x)
            shi += x
        if len(lo) > len(hi) + 1:
            y = -heapq.heappop(lo)
            heapq.heappush(hi, y)
            slo -= y
            shi += y
        elif len(hi) > len(lo):
            y = heapq.heappop(hi)
            heapq.heappush(lo, -y)
            shi -= y
            slo += y
        out.append(shi - slo + (len(lo) - len(hi)) * -lo[0])
    return out


def bestSplitCost(positions):
    n = len(positions)
    pre = _prefix_costs(positions)             # pre[i] = cost of positions[0..i]
    suf = _prefix_costs(positions[::-1])       # suf[j] = cost of the last j + 1 houses
    best = None
    for k in range(1, n):                      # prefix = first k houses, suffix = last n - k houses
        total = pre[k - 1] + suf[n - k - 1]
        if best is None or total < best:
            best = total
    return best
''',
    tests=[[[1, 2, 9, 10, 3]], [[5, 5]], [[1, 100000]], [[1, 2, 9, 10]], [[10, 9, 2, 1]], [[1, 10, 2, 9]], [[3, 3, 3, 3]],
           [[-100000, 100000, -100000, 100000, 0]], [[1, 2, 3, 4, 5, 6, 7]], [[7, 1, 7, 1, 7, 1]], [[0, 50, 100, 150, 200, 250, 300]]],
)
_r = rnd(9108)
p["tests"].append([[_r.randint(-10 ** 5, 10 ** 5) for _ in range(5000)]])
p["tests"].append([[(-10 ** 5 + _r.randint(0, 1000)) if i < 2500 else (10 ** 5 - _r.randint(0, 1000)) for i in range(5000)]])
p["tests"].append([[_r.randint(-20, 20) for _ in range(5000)]])


def b_split(positions):
    n = len(positions)
    return min(gather_cost(positions[:k]) + gather_cost(positions[k:]) for k in range(1, n))


def v_split(tests):
    for t in tests:
        a = t["args"][0]
        assert 2 <= len(a) <= 5000 and all(-10 ** 5 <= x <= 10 ** 5 for x in a)


CHECKS["two-meeting-points-best-split"] = (b_split, lambda r: [[r.randint(-8, 8) for _ in range(r.randint(2, 11))]], "exact")
VALIDATE["two-meeting-points-best-split"] = v_split

# ================================================================ HARD

# ---------------------------------------------------------------- weighted running median
p = add(
    id="weighted-running-median", tier="extra", title="Weighted Running Median", diff="Hard", topic=T,
    fn="weightedRunningMedian", params=[("items", "int[][]")], ret="int[]", cmp="exact",
    desc="<p>Items arrive one at a time; <code>items[i] = [value, weight]</code>. The <strong>weighted median</strong> of a set of items is the smallest value <code>v</code> such that the total weight of the items with value at most <code>v</code> is at least <strong>half</strong> of the total weight (that is, <code>2 * (weight of items with value &le; v) &ge; total weight</code>).</p><p>After each arrival, report the weighted median of all items received so far. (With all weights equal to 1 this is the lower median.)</p><pre>items = [[5,2], [1,1], [9,6], [4,1], [3,8]]\n{5:2}                           total 2  -> 5\n{1:1, 5:2}                      total 3  -> 5   (weight up to 1 is 1: 2 < 3)\n{1:1, 5:2, 9:6}                 total 9  -> 9   (weight up to 5 is 3: 6 < 9)\n{1:1, 4:1, 5:2, 9:6}            total 10 -> 9\n{1:1, 3:8, 4:1, 5:2, 9:6}       total 18 -> 3   (weight up to 3 is 9: 18 >= 18)\nanswer = [5, 5, 9, 9, 3]</pre>",
    constraints=["1 &le; items.length &le; 2,500", "-10<sup>9</sup> &le; value &le; 10<sup>9</sup>", "1 &le; weight &le; 1,000"],
    hints=["Think of an item of weight w as w copies of its value. The weighted median is then the lower median of that big multiset, but you cannot afford to insert w copies.",
           "Keep two heaps again, but balance them by <em>total weight</em> instead of by count: the lower max-heap must carry at least half of the total weight.",
           "The root of the lower heap is the answer exactly when 2 * (lower weight) &ge; total and 2 * (lower weight - weight of its root) &lt; total. Move whole items between the heaps until both hold."],
    editorial=["Let <code>lo</code> be a max-heap of items with the smaller values and <code>hi</code> a min-heap with the larger ones, every item of <code>lo</code> having value at most every item of <code>hi</code>, and let <code>Wlo</code>, <code>Whi</code> be their total weights. The root of <code>lo</code> is the weighted median when two conditions hold: <code>2 * Wlo &ge; total</code> (enough weight at or below the root) and <code>2 * (Wlo - w_root) &lt; total</code> (not enough weight strictly below the root's rank, so no smaller value qualifies). Items with a value equal to the root's value may sit in either heap, which does not matter: the answer is the value.",
               "Insert the new item into <code>lo</code> if its value is at most the root of <code>lo</code> (or <code>lo</code> is empty), otherwise into <code>hi</code>, and update the weights. Restore the invariants with two loops: while the root of <code>lo</code> can be spared (<code>2 * (Wlo - w_root) &ge; total</code>), move it to <code>hi</code>; while <code>2 * Wlo &lt; total</code>, move the root of <code>hi</code> into <code>lo</code>.",
               "An insertion of weight w changes the balance by less than w, so at most about w items (each of weight at least 1) cross between the heaps, and each crossing costs O(log n). With random or modest weights that is a handful of moves per item, so the running time is close to O(n log n); the worst case is O(n * W * log n) for maximum weight W (here at most 1,000). Space is O(n). Expanding weights into copies would cost O(sum of weights) heap operations for every item instead."],
    time="O(n W log n) worst case, near O(n log n) typically", space="O(n)",
    solution='''import heapq


def weightedRunningMedian(items):
    lo, hi = [], []  # lo: max-heap (-value, weight); hi: min-heap (value, weight)
    wlo = whi = 0
    out = []
    for v, w in items:
        if not lo or v <= -lo[0][0]:
            heapq.heappush(lo, (-v, w))
            wlo += w
        else:
            heapq.heappush(hi, (v, w))
            whi += w
        total = wlo + whi
        while 2 * (wlo - lo[0][1]) >= total:
            nv, ww = heapq.heappop(lo)
            heapq.heappush(hi, (-nv, ww))
            wlo -= ww
            whi += ww
        while 2 * wlo < total:
            vv, ww = heapq.heappop(hi)
            heapq.heappush(lo, (-vv, ww))
            whi -= ww
            wlo += ww
        out.append(-lo[0][0])
    return out
''',
    tests=[[[[5, 2], [1, 1], [9, 6], [4, 1], [3, 8]]], [[[7, 3]]], [[[1, 1], [2, 1]]], [[[2, 1], [1, 1]]], [[[4, 5], [4, 5], [4, 1]]],
           [[[1, 1], [2, 1], [3, 1], [4, 1], [5, 1], [6, 1]]], [[[1, 1000], [2, 1], [3, 1], [-5, 1000]]], [[[B, 1], [-B, 1], [0, 2]]],
           [[[10, 1], [20, 1], [30, 1], [40, 100], [5, 300], [25, 5]]], [[[3, 2], [3, 3], [1, 4], [5, 4], [3, 1]]]],
)
_r = rnd(9109)
p["tests"].append([[[_r.randint(-10 ** 6, 10 ** 6), _r.randint(1, 1000)] for _ in range(2500)]])
p["tests"].append([[[_r.randint(-50, 50), _r.randint(1, 5)] for _ in range(2500)]])
p["tests"].append([[[i if i % 2 else -i, 1 + (i * 37) % 1000] for i in range(2500)]])


def b_wmedian(items):
    out = []
    for m in range(1, len(items) + 1):
        cur = sorted(items[:m])
        total = sum(w for _, w in cur)
        acc = 0
        for v, w in cur:
            acc += w
            if 2 * acc >= total:
                out.append(v)
                break
    return out


def v_wmedian(tests):
    for t in tests:
        it = t["args"][0]
        assert 1 <= len(it) <= 2500
        assert all(-B <= v <= B and 1 <= w <= 1000 for v, w in it)


CHECKS["weighted-running-median"] = (b_wmedian, lambda r: [[[r.randint(-5, 5), r.randint(1, 6)] for _ in range(r.randint(1, 12))]], "exact")
VALIDATE["weighted-running-median"] = v_wmedian

# ---------------------------------------------------------------- sliding window equalize cost
p = add(
    id="sliding-window-equalize-costs", tier="extra", title="Equalizing Cost of Every Window", diff="Hard", topic=T,
    fn="windowEqualizeCosts", params=[("nums", "int[]"), ("k", "int")], ret="int[]", cmp="exact",
    desc="<p>For a group of numbers, the <strong>equalizing cost</strong> is the smallest total number of unit steps needed to make all of them equal, where one step raises or lowers a single number by 1. Equivalently it is the minimum over integers <code>c</code> of the sum of <code>|x - c|</code>.</p><p>For every window of <code>k</code> consecutive elements of <code>nums</code>, from left to right, return the equalizing cost of that window.</p><pre>nums = [1, 4, 2, 9, 3], k = 3\n[1,4,2] -> make all 2: 1 + 2 + 0 = 3\n[4,2,9] -> make all 4: 0 + 2 + 5 = 7\n[2,9,3] -> make all 3: 1 + 6 + 0 = 7\nanswer = [3, 7, 7]</pre>",
    constraints=["1 &le; k &le; nums.length &le; 5,000", "-10<sup>5</sup> &le; nums[i] &le; 10<sup>5</sup>", "Every answer fits in a 32-bit signed integer"],
    hints=["The best target value for a window is its median. The cost is the distance of every element to that median.",
           "Slide the window while keeping a lower half and an upper half in two heaps together with the sum of each half. Then the cost needs no loop over the window.",
           "Elements leave the window from the left, in the middle of the heaps: use lazy deletion (mark the element dead, adjust live sizes and sums, and clean a heap's top only when you need its root)."],
    editorial=["For a window, <code>sum |x - c|</code> is minimised at a median. Split the window into the smaller half <code>lo</code> (a max-heap, the extra element when k is odd) and the larger half <code>hi</code> (a min-heap). With median <code>m</code> equal to the root of <code>lo</code>, the cost is <code>sum(hi) - sum(lo) + (|lo| - |hi|) * m</code>, which only needs the two sums and the sizes.",
               "Sliding by one means inserting the new element and removing the one that left. Insertion is the usual two-heap step. Removal targets an arbitrary element, so mark its id as dead, update the live size and live sum of the half it belongs to, and rebalance with the live sizes. Dead entries are physically popped only when they reach the top of a heap, which keeps each element's total cost at O(log k) amortised.",
               "Entries carry their index so that equal values are not confused, and the half each index lives in is tracked as elements move between heaps. Total time is O(n log n) and space O(n). Recomputing each window with a sort would be O(n k log k)."],
    time="O(n log n)", space="O(n)",
    solution=TWO_HEAPS + '''def windowEqualizeCosts(nums, k):
    t = TwoHeaps()
    out = []
    for i, x in enumerate(nums):
        if i >= k:
            t.remove(i - k, nums[i - k])
        t.add(i, x)
        if i >= k - 1:
            out.append(t.cost())
    return out
''',
    tests=[[[1, 4, 2, 9, 3], 3], [[5], 1], [[5, 5, 5, 5], 2], [[1, 100000, -100000, 5], 2], [[1, 2, 3, 4, 5, 6], 6], [[6, 1, 5, 2, 4, 3], 1],
           [[3, 1, 4, 1, 5, 9, 2, 6, 5, 3, 5], 4], [[-100000, 100000, -100000, 100000, -100000, 100000], 3], [[2, 2, 7, 7, 2, 2], 4],
           [[9, 8, 7, 6, 5, 4, 3, 2, 1], 5]],
)
_r = rnd(9110)
_a = [_r.randint(-10 ** 5, 10 ** 5) for _ in range(3000)]
p["tests"].append([_a, 1500])
p["tests"].append([[_r.randint(-10 ** 5, 10 ** 5) for _ in range(3000)], 7])
p["tests"].append([[_r.randint(-30, 30) for _ in range(5000)], 1000])


def b_win_cost(nums, k):
    return [gather_cost(nums[i:i + k]) for i in range(len(nums) - k + 1)]


def g_win_cost(r):
    n = r.randint(1, 12)
    return [[r.randint(-9, 9) for _ in range(n)], r.randint(1, n)]


def v_win_cost(tests):
    for t in tests:
        a, k = t["args"]
        assert 1 <= k <= len(a) <= 5000 and all(-10 ** 5 <= x <= 10 ** 5 for x in a)


CHECKS["sliding-window-equalize-costs"] = (b_win_cost, g_win_cost, "exact")
VALIDATE["sliding-window-equalize-costs"] = v_win_cost

# ---------------------------------------------------------------- longest window equalizable within a budget
p = add(
    id="longest-window-equalizable-within-budget", tier="extra", title="Longest Window Equalizable Within a Budget", diff="Hard", topic=T,
    fn="longestEqualizable", params=[("nums", "int[]"), ("budget", "int")], ret="int", cmp="exact",
    desc="<p>The <strong>equalizing cost</strong> of a group of numbers is the smallest total number of unit steps (raise or lower one number by 1) needed to make all of them equal; equivalently, the minimum over integers <code>c</code> of the sum of <code>|x - c|</code>.</p><p>Return the length of the longest contiguous subarray of <code>nums</code> whose equalizing cost is at most <code>budget</code>.</p><pre>nums = [1, 4, 2, 9, 3], budget = 8\n[4,2,9,3] -> make all 3: 1 + 1 + 6 + 0 = 8   (fits)\nthe whole array costs 10 (make all 3)          (too much)\nanswer = 4</pre>",
    constraints=["1 &le; nums.length &le; 5,000", "-10<sup>5</sup> &le; nums[i] &le; 10<sup>5</sup>", "0 &le; budget &le; 10<sup>9</sup>"],
    hints=["A single element always costs 0, so the answer is at least 1. Adding an element to a subarray never makes its cost smaller. What does that suggest?",
           "Because of that monotonicity, two pointers work: grow the right end, and while the window is too expensive, advance the left end.",
           "You need the equalizing cost of the current window quickly after each add and remove: keep the window in two heaps (lower and upper half) with the sum of each half, and delete the leaving element lazily."],
    editorial=["Cost is monotone under inclusion: if window A is contained in window B, then <code>cost(A) &le; cost(B)</code>, because the best common target for B also works for A and B only has extra non-negative terms. So if a window is affordable, all its sub-windows are, which is exactly the condition for the standard two-pointer technique: for each right end, the smallest valid left end never moves left.",
               "Maintain the window in a two-heap median structure with half sums: lower half in a max-heap, upper half in a min-heap, cost <code>sum(hi) - sum(lo) + (|lo| - |hi|) * median</code>. When the right end advances, insert the new element; while the cost exceeds the budget, remove <code>nums[left]</code> (lazy deletion by index) and advance <code>left</code>. Track the largest window length seen.",
               "Each element is inserted once and removed at most once, each in O(log n) amortised, so the whole scan is O(n log n) time with O(n) space. A binary search on the length combined with the sliding cost computation would also work but adds a log factor and is not needed."],
    time="O(n log n)", space="O(n)",
    solution=TWO_HEAPS + '''def longestEqualizable(nums, budget):
    t = TwoHeaps()
    left = 0
    best = 0
    for right, x in enumerate(nums):
        t.add(right, x)
        while t.cost() > budget:
            t.remove(left, nums[left])
            left += 1
        best = max(best, right - left + 1)
    return best
''',
    tests=[[[1, 4, 2, 9, 3], 8], [[7], 0], [[1, 4, 2, 9, 3], 0], [[5, 5, 5, 5], 0], [[1, 100000, -100000, 5], 100000],
           [[1, 2, 3, 4, 5, 6], 9], [[1, 2, 3, 4, 5, 6], 1000000000], [[10, 1, 10, 1, 10, 1], 18], [[3, 1, 4, 1, 5, 9, 2, 6, 5, 3, 5], 12],
           [[-100000, 100000, -100000, 100000], 199999], [[2, 2, 7, 7, 2, 2], 10]],
)
_r = rnd(9111)
p["tests"].append([[_r.randint(-10 ** 5, 10 ** 5) for _ in range(5000)], 3 * 10 ** 6])
p["tests"].append([[_r.randint(-10 ** 5, 10 ** 5) for _ in range(5000)], 40 * 10 ** 6])
p["tests"].append([[(i * 13) % 200 - 100 for i in range(5000)], 100000])


def b_longest_eq(nums, budget):
    best = 0
    n = len(nums)
    for i in range(n):
        for j in range(i, n):
            if gather_cost(nums[i:j + 1]) <= budget:
                best = max(best, j - i + 1)
    return best


def v_longest_eq(tests):
    for t in tests:
        a, b = t["args"]
        assert 1 <= len(a) <= 5000 and all(-10 ** 5 <= x <= 10 ** 5 for x in a) and 0 <= b <= B


CHECKS["longest-window-equalizable-within-budget"] = (b_longest_eq, lambda r: [[r.randint(-8, 8) for _ in range(r.randint(1, 10))], r.randint(0, 30)], "exact")
VALIDATE["longest-window-equalizable-within-budget"] = v_longest_eq
