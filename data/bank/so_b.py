"""Problems: sorting, then a greedy sweep (assign, pair, schedule, minimum cost). See data/lib.py for the registry."""
from itertools import combinations, permutations

from lib import add, rnd, CHECKS, VALIDATE, gen_arr  # noqa: F401

INT_MIN, INT_MAX = -(2 ** 31), 2 ** 31 - 1


# ---------------------------------------------------------------- EASY

p = add(
    id="min-moves-to-seat-students", title="Minimum Moves to Seat Everyone", diff="Easy", topic="Sorting",
    fn="minMovesToSeat", params=[("seats", "int[]"), ("students", "int[]")], ret="int", cmp="exact",
    desc="<p>A long corridor has <code>n</code> seats and <code>n</code> students, all standing on integer positions of a number line. <code>seats[i]</code> is the position of the <code>i</code>-th seat and <code>students[j]</code> is the starting position of the <code>j</code>-th student. Several seats, or several students, may share a position.</p><p>Every student must end up on a different seat. In one move a single student walks one unit to the left or to the right (students may pass through each other and stand on the same spot while moving). Return the minimum total number of moves needed to seat everybody.</p><pre>seats = [3, 1, 5], students = [2, 7, 4]       -> 4\nseats = [4, 1, 5, 9], students = [1, 3, 2, 6] -> 7\nseats = [2, 2, 6, 6], students = [1, 2, 3, 6] -> 4</pre><p>In the first example, seats at 1, 3, 5 are matched with students at 2, 4, 7, which costs 1 + 1 + 2.</p>",
    constraints=["1 &le; n = seats.length = students.length &le; 5,000", "1 &le; seats[i], students[j] &le; 100,000"],
    hints=["Any assignment of students to seats is allowed, and the cost of a pairing is the distance between the two positions. Which pairing minimizes the total distance?",
           "If a student A stands left of a student B but is sent to a seat that is right of B's seat, the two walks cross. What happens to the total if you uncross them?",
           "Sort both arrays and match them index by index: the leftmost student takes the leftmost seat, and so on. The answer is the sum of <code>|seats[i] - students[i]|</code> after sorting."],
    editorial=["Sort the seats and the students. Then the student with the i-th smallest position takes the seat with the i-th smallest position, and the answer is the sum of the absolute differences.",
               "Why: take two students <code>a &le; b</code> and two seats <code>x &le; y</code>. Matching them as <code>(a,y)</code> and <code>(b,x)</code> (crossed) never costs less than matching <code>(a,x)</code> and <code>(b,y)</code>, because on a line the crossed pairing walks the overlapping stretch twice. Repeatedly uncrossing any crossed pair never increases the cost and ends with the sorted matching, so that matching is optimal.",
               "Sorting costs O(n log n), the final sum is O(n)."],
    time="O(n log n)", space="O(n)",
    solution='''def minMovesToSeat(seats, students):
    a = sorted(seats)
    b = sorted(students)
    return sum(abs(x - y) for x, y in zip(a, b))
''',
    tests=[[[3, 1, 5], [2, 7, 4]], [[4, 1, 5, 9], [1, 3, 2, 6]], [[2, 2, 6, 6], [1, 2, 3, 6]], [[5], [5]], [[1], [100000]],
           [[1, 1, 1], [1, 1, 1]], [[1, 2, 3, 4], [4, 3, 2, 1]], [[100000, 1], [1, 100000]], [[10, 20, 30], [1, 1, 1]],
           [[7, 7, 7, 7], [1, 100000, 7, 50]]],
)
_r = rnd(8101)
p["tests"].append([[_r.randint(1, 100000) for _ in range(4000)], [_r.randint(1, 100000) for _ in range(4000)]])
p["tests"].append([[100000] * 2000 + [1] * 2000, [1] * 2000 + [100000] * 2000])
p["tests"].append([list(range(1, 4001)), list(range(4000, 0, -1))])


def b_seat(seats, students):
    return min(sum(abs(x - y) for x, y in zip(seats, perm)) for perm in permutations(students))


def g_seat(r):
    n = r.randint(1, 6)
    return [[r.randint(1, 10) for _ in range(n)], [r.randint(1, 10) for _ in range(n)]]


def v_seat(tests):
    for t in tests:
        s, st = t["args"]
        assert len(s) == len(st) and 1 <= len(s) <= 5000
        assert all(1 <= x <= 100000 for x in s + st)


CHECKS["min-moves-to-seat-students"] = (b_seat, g_seat, "exact")
VALIDATE["min-moves-to-seat-students"] = v_seat


p = add(
    id="max-items-within-budget", title="Most Items Within a Budget", diff="Easy", topic="Sorting",
    fn="maxItems", params=[("prices", "int[]"), ("budget", "int")], ret="int", cmp="exact",
    desc="<p>A clearance shop lists the price of every item in <code>prices</code>. Each item exists only once, so you can buy it at most once. You have <code>budget</code> coins to spend and you do not have to spend all of them.</p><p>Return the largest number of items you can buy.</p><pre>prices = [1, 3, 2, 4, 1], budget = 7        -> 4\nprices = [10, 6, 8, 7, 7, 8], budget = 5    -> 0\nprices = [1, 6, 3, 1, 2, 5], budget = 20    -> 6</pre><p>In the first example the four cheapest items cost 1 + 1 + 2 + 3 = 7.</p>",
    constraints=["0 &le; prices.length &le; 10,000", "1 &le; prices[i] &le; 100,000", "0 &le; budget &le; 2<sup>31</sup> - 1"],
    hints=["You only care about how many items you buy, not which ones. If you buy k items, which k items cost the least in total?",
           "The k cheapest items. So the question becomes: how many of the cheapest items fit into the budget?",
           "Sort the prices ascending and keep buying the next cheapest item while it still fits; stop at the first one that does not."],
    editorial=["Buying the cheapest items first is optimal. If a solution with k items used any item that is not among the k cheapest, swapping it for a cheaper unused one keeps the count and does not increase the cost.",
               "So sort the prices, then walk through them, subtracting each price from the remaining budget while it stays non-negative. The number of items subtracted is the answer. Once an item does not fit, every later one is at least as expensive, so we can stop.",
               "Time is O(n log n) for the sort and O(n) for the scan."],
    time="O(n log n)", space="O(n)",
    solution='''def maxItems(prices, budget):
    count = 0
    for x in sorted(prices):
        if x > budget:
            break
        budget -= x
        count += 1
    return count
''',
    tests=[[[1, 3, 2, 4, 1], 7], [[10, 6, 8, 7, 7, 8], 5], [[1, 6, 3, 1, 2, 5], 20], [[], 100], [[5], 5], [[5], 4], [[3, 3, 3], 0],
           [[100000, 100000], INT_MAX], [[2, 2, 2, 2], 7], [[9, 1, 8, 2, 7, 3], 12]],
)
_r = rnd(8102)
p["tests"].append([[_r.randint(1, 1000) for _ in range(5000)], 1_000_000])
p["tests"].append([[_r.randint(1, 100000) for _ in range(3000)], 40_000_000])
p["tests"].append([[1000] * 4000, 1_999_999])


def b_items(prices, budget):
    best = 0
    for mask in range(1 << len(prices)):
        tot = cnt = 0
        for i, x in enumerate(prices):
            if (mask >> i) & 1:
                tot += x
                cnt += 1
        if tot <= budget:
            best = max(best, cnt)
    return best


def g_items(r):
    return [[r.randint(1, 12) for _ in range(r.randint(0, 9))], r.randint(0, 40)]


def v_items(tests):
    for t in tests:
        prices, budget = t["args"]
        assert len(prices) <= 10000 and all(1 <= x <= 100000 for x in prices)
        assert 0 <= budget <= INT_MAX


CHECKS["max-items-within-budget"] = (b_items, g_items, "exact")
VALIDATE["max-items-within-budget"] = v_items


p = add(
    id="maximize-sum-after-k-negations", title="Largest Sum After K Sign Flips", diff="Easy", topic="Sorting", tier="extra",
    fn="largestSumAfterFlips", params=[("nums", "int[]"), ("k", "int")], ret="int", cmp="exact",
    desc="<p>You are given an integer array <code>nums</code> and an integer <code>k</code>. You must perform exactly <code>k</code> operations. In one operation you pick any index <code>i</code> and replace <code>nums[i]</code> by <code>-nums[i]</code>. The same index may be picked in several operations.</p><p>Return the largest possible sum of the array after exactly <code>k</code> operations.</p><pre>nums = [3, -1, 0, 2], k = 3          -> 6\nnums = [2, -3, -1, 5, -4], k = 2     -> 13\nnums = [1, 2], k = 3                 -> 1</pre><p>In the first example flip -1 once; the two remaining operations flip the same element (for example 0) twice, so they change nothing.</p>",
    constraints=["1 &le; nums.length &le; 10,000", "-10,000 &le; nums[i] &le; 10,000", "0 &le; k &le; 10,000"],
    hints=["A flip helps only when it turns a negative number positive. Which negative numbers gain the most?",
           "The most negative ones: flipping <code>-9</code> gains 18, flipping <code>-1</code> gains 2. Sort the array and flip from the smallest value upward.",
           "After all negatives are flipped (or k runs out), leftover flips come in pairs that cancel. Only if an odd number remains you must lose by flipping once: do it on the element with the smallest absolute value, costing twice that value."],
    editorial=["Sort the array ascending. Walk from the left: while the current value is negative and flips remain, flip it. Negative numbers farthest from zero come first, so each flip gains as much as possible.",
               "If flips remain afterwards, all values are now non-negative. Flipping any element twice returns it to its value, so only the parity of the remaining flips matters. If it is even, nothing changes. If it is odd, exactly one flip has to be wasted, and the cheapest one is on the element with the smallest absolute value <code>m</code> (this includes a zero, which costs nothing): subtract <code>2 * m</code> from the sum.",
               "Note that the smallest absolute value must be taken after the flips, because a flipped element can become the smallest. Time is O(n log n) for the sort."],
    time="O(n log n)", space="O(n)",
    solution='''def largestSumAfterFlips(nums, k):
    a = sorted(nums)
    for i in range(len(a)):
        if k > 0 and a[i] < 0:
            a[i] = -a[i]
            k -= 1
    total = sum(a)
    if k % 2 == 1:
        total -= 2 * min(a)
    return total
''',
    tests=[[[3, -1, 0, 2], 3], [[2, -3, -1, 5, -4], 2], [[1, 2], 3], [[5], 0], [[5], 1], [[-5], 1], [[-5], 2], [[0], 7],
           [[-2, -2, -2], 2], [[-2, -2, -2], 4], [[4, 2, 3], 1], [[-1, 1], 1]],
)
_r = rnd(8103)
p["tests"].append([[_r.randint(-10000, 10000) for _ in range(5000)], 2500])
p["tests"].append([[_r.randint(-10000, 10000) for _ in range(4000)], 10000])
p["tests"].append([[_r.randint(0, 10000) for _ in range(4000)], 9999])


def b_negate(nums, k):
    states = {tuple(nums)}
    for _ in range(k):
        nxt = set()
        for s in states:
            for i in range(len(s)):
                t = list(s)
                t[i] = -t[i]
                nxt.add(tuple(t))
        states = nxt
    return max(sum(s) for s in states)


def g_negate(r):
    return [[r.randint(-6, 6) for _ in range(r.randint(1, 4))], r.randint(0, 6)]


def v_negate(tests):
    for t in tests:
        nums, k = t["args"]
        assert 1 <= len(nums) <= 10000 and all(-10000 <= x <= 10000 for x in nums)
        assert 0 <= k <= 10000


CHECKS["maximize-sum-after-k-negations"] = (b_negate, g_negate, "exact")
VALIDATE["maximize-sum-after-k-negations"] = v_negate


# ---------------------------------------------------------------- MEDIUM

p = add(
    id="bag-of-tokens-max-score", title="Bag of Tokens", diff="Medium", topic="Sorting", tier="extra",
    fn="bagOfTokens", params=[("tokens", "int[]"), ("power", "int")], ret="int", cmp="exact",
    desc="<p>You start with <code>power</code> units of power and a score of <code>0</code>. There is a bag of tokens, where <code>tokens[i]</code> is the value of the <code>i</code>-th token. Each token can be played at most once, in any order, in one of two ways:</p><ul><li><strong>Face up:</strong> if your power is at least <code>tokens[i]</code>, you may spend <code>tokens[i]</code> power to gain <code>1</code> score.</li><li><strong>Face down:</strong> if your score is at least <code>1</code>, you may spend <code>1</code> score to gain <code>tokens[i]</code> power.</li></ul><p>You do not have to play every token. Return the largest score you can have at any moment.</p><pre>tokens = [100], power = 50              -> 0\ntokens = [100, 200], power = 150        -> 1\ntokens = [100, 200, 300, 400], power = 200 -> 2</pre><p>In the last example: play 100 face up (power 100, score 1), play 400 face down (power 500, score 0), then play 200 and 300 face up (power 0, score 2).</p>",
    constraints=["0 &le; tokens.length &le; 5,000", "0 &le; tokens[i], power &le; 10,000"],
    hints=["Face up converts power into score, face down converts score back into power. Which tokens do you want to spend power on, and which do you want to sell for power?",
           "Spend power on the cheapest tokens, and when you need power, sell the most valuable remaining token. Sort the tokens.",
           "Use two pointers on the sorted array. If the smallest token is affordable, play it face up; otherwise, if you have score, play the largest token face down; otherwise stop. Track the best score seen along the way."],
    editorial=["Each point of score costs a token's value in power, so you want the cheapest tokens face up. A token played face down returns its value in power, so you want the most valuable tokens face down. Sorting puts both ends where they are needed.",
               "Keep pointers <code>lo</code> and <code>hi</code> on the sorted array. While <code>lo &le; hi</code>: if <code>power &ge; tokens[lo]</code>, play it face up (power decreases, score increases) and update the best score; else if the score is positive, play <code>tokens[hi]</code> face down and move <code>hi</code> left; else stop. Selling a token only makes sense when you cannot afford the cheapest one, which is why the best score is recorded after every face-up move and not only at the end.",
               "Each token is touched once after the sort, so the time is O(n log n)."],
    time="O(n log n)", space="O(n)",
    solution='''def bagOfTokens(tokens, power):
    t = sorted(tokens)
    lo, hi = 0, len(t) - 1
    score = best = 0
    while lo <= hi:
        if power >= t[lo]:
            power -= t[lo]
            lo += 1
            score += 1
            if score > best:
                best = score
        elif score > 0:
            power += t[hi]
            hi -= 1
            score -= 1
        else:
            break
    return best
''',
    tests=[[[100], 50], [[100, 200], 150], [[100, 200, 300, 400], 200], [[], 10], [[0], 0], [[5], 5], [[5, 5, 5], 4], [[1, 1, 1, 1], 0],
           [[10, 100, 1000], 10], [[1, 2, 3, 4, 5, 6, 7, 8], 10], [[50, 50, 60], 100], [[10000, 9999, 10000], 10000]],
)
_r = rnd(8104)
p["tests"].append([[_r.randint(0, 10000) for _ in range(5000)], 5000])
p["tests"].append([[_r.randint(1, 100) for _ in range(5000)], 100])
p["tests"].append([[_r.randint(0, 10000) for _ in range(3000)], 0])


def b_tokens(tokens, power):
    n = len(tokens)
    seen = set()
    best = 0
    stack = [(0, 0)]  # (face-up mask, face-down mask)
    seen.add((0, 0))
    while stack:
        up, down = stack.pop()
        pw = power
        sc = 0
        for i in range(n):
            if (up >> i) & 1:
                pw -= tokens[i]
                sc += 1
            if (down >> i) & 1:
                pw += tokens[i]
                sc -= 1
        best = max(best, sc)
        for i in range(n):
            if ((up | down) >> i) & 1:
                continue
            if pw >= tokens[i]:
                s = (up | (1 << i), down)
                if s not in seen:
                    seen.add(s)
                    stack.append(s)
            if sc >= 1:
                s = (up, down | (1 << i))
                if s not in seen:
                    seen.add(s)
                    stack.append(s)
    return best


def g_tokens(r):
    return [[r.randint(0, 9) for _ in range(r.randint(0, 6))], r.randint(0, 12)]


def v_tokens(tests):
    for t in tests:
        tokens, power = t["args"]
        assert len(tokens) <= 5000 and all(0 <= x <= 10000 for x in tokens)
        assert 0 <= power <= 10000


CHECKS["bag-of-tokens-max-score"] = (b_tokens, g_tokens, "exact")
VALIDATE["bag-of-tokens-max-score"] = v_tokens


p = add(
    id="max-profit-assigning-work", title="Most Profit From Assigned Jobs", diff="Medium", topic="Sorting",
    fn="maxProfitAssignment", params=[("difficulty", "int[]"), ("profit", "int[]"), ("worker", "int[]")], ret="int", cmp="exact",
    desc="<p>A job board lists <code>n</code> jobs. Job <code>i</code> has difficulty <code>difficulty[i]</code> and pays <code>profit[i]</code>. There are <code>m</code> workers; worker <code>j</code> has ability <code>worker[j]</code> and can do any job whose difficulty is at most that ability.</p><p>Each worker takes at most one job, but a job is not used up: any number of workers can take the same job. Return the largest total pay all workers can earn together. A worker who cannot do any job earns nothing.</p><pre>difficulty = [2, 4, 6, 8, 10]\nprofit     = [10, 20, 30, 40, 50]\nworker     = [4, 5, 6, 7]                  -> 100\n\ndifficulty = [85, 47, 57], profit = [24, 66, 99], worker = [40, 25, 25] -> 0</pre><p>In the first example the workers earn 20, 20, 30 and 30.</p>",
    constraints=["1 &le; difficulty.length = profit.length &le; 3,000", "0 &le; worker.length &le; 3,000", "1 &le; difficulty[i], worker[j] &le; 100,000", "0 &le; profit[i] &le; 100,000"],
    hints=["Workers do not compete: each worker independently takes the best-paying job they are able to do. What is the answer for a single worker?",
           "For one worker with ability <code>a</code>, you want the maximum profit among jobs with difficulty at most <code>a</code>. Doing that scan for every worker is O(n * m); sorting can share the work.",
           "Sort jobs by difficulty and keep a running maximum of profit. Sort the workers by ability and sweep both lists with one pointer into the jobs: for each worker advance the pointer over all jobs they can do, updating the running best, then add that best."],
    editorial=["Because a job can be taken by any number of workers, the workers are independent and each one should simply take the best job within their ability. The total is the sum of those best values.",
               "To avoid checking every job for every worker, sort the jobs by difficulty and the workers by ability. Maintain <code>best</code>, the maximum profit among the jobs whose difficulty is at most the current worker's ability. As abilities increase, the set of doable jobs only grows, so a single pointer moving forward through the sorted jobs is enough. Add <code>best</code> to the answer for each worker.",
               "Time O(n log n + m log m), space O(n)."],
    time="O((n + m) log(n + m))", space="O(n)",
    solution='''def maxProfitAssignment(difficulty, profit, worker):
    jobs = sorted(zip(difficulty, profit))
    total = 0
    best = 0
    i = 0
    for ability in sorted(worker):
        while i < len(jobs) and jobs[i][0] <= ability:
            if jobs[i][1] > best:
                best = jobs[i][1]
            i += 1
        total += best
    return total
''',
    tests=[[[2, 4, 6, 8, 10], [10, 20, 30, 40, 50], [4, 5, 6, 7]], [[85, 47, 57], [24, 66, 99], [40, 25, 25]], [[5], [7], []],
           [[5], [7], [5]], [[5], [7], [4]], [[3, 3, 3], [1, 9, 5], [3, 3]], [[1, 2, 3], [100, 0, 0], [1, 2, 3]],
           [[10, 1], [0, 0], [10, 10]], [[4, 2, 6], [5, 9, 1], [1, 2, 3, 4, 5, 6, 7]], [[100000], [100000], [100000] * 5]],
)
_r = rnd(8105)
p["tests"].append([[_r.randint(1, 100000) for _ in range(3000)], [_r.randint(0, 100000) for _ in range(3000)], [_r.randint(1, 100000) for _ in range(3000)]])
p["tests"].append([[_r.randint(1, 1000) for _ in range(3000)], [_r.randint(0, 100000) for _ in range(3000)], [_r.randint(1, 1000) for _ in range(3000)]])
p["tests"].append([list(range(1, 3001)), list(range(3000, 0, -1)), [_r.randint(1, 3000) for _ in range(3000)]])


def b_assign(difficulty, profit, worker):
    total = 0
    for a in worker:
        total += max([pr for d, pr in zip(difficulty, profit) if d <= a] + [0])
    return total


def g_assign(r):
    n = r.randint(1, 6)
    return [[r.randint(1, 10) for _ in range(n)], [r.randint(0, 10) for _ in range(n)], [r.randint(1, 10) for _ in range(r.randint(0, 6))]]


def v_assign(tests):
    for t in tests:
        d, pr, w = t["args"]
        assert len(d) == len(pr) and 1 <= len(d) <= 3000 and len(w) <= 3000
        assert all(1 <= x <= 100000 for x in d + w) and all(0 <= x <= 100000 for x in pr)
        assert t["expected"] <= 3000 * 100000


CHECKS["max-profit-assigning-work"] = (b_assign, g_assign, "exact")
VALIDATE["max-profit-assigning-work"] = v_assign


p = add(
    id="max-events-attended", title="Maximum Events You Can Attend", diff="Medium", topic="Sorting",
    fn="maxEvents", params=[("events", "int[][]")], ret="int", cmp="exact",
    desc="<p>Each event is a pair <code>[start, end]</code>: it takes place on every day from <code>start</code> to <code>end</code> inclusive, and you can attend it by showing up on any <strong>one</strong> of those days. You can attend at most one event per day.</p><p>Return the maximum number of different events you can attend.</p><pre>[[1,2],[2,3],[3,4]]         -> 3\n[[1,2],[2,3],[3,4],[1,2]]   -> 4\n[[1,1],[1,1],[1,1]]         -> 1</pre><p>In the second example the two events [1,2] take days 1 and 2, then [2,3] takes day 3 and [3,4] takes day 4.</p>",
    constraints=["0 &le; events.length &le; 3,000", "events[i] = [start, end] with 1 &le; start &le; end &le; 100,000"],
    hints=["Think of days as slots and events as jobs that fit into a range of slots. When you are standing on a day, which of the available events should you attend?",
           "Among the events that have already started and have not yet ended, the one that ends soonest is the most urgent: any other event can wait longer.",
           "Sort the events by start day. Sweep the days; push the end day of every event starting today into a min-heap, drop expired ends, and attend the event with the smallest end. Jump ahead when the heap is empty."],
    editorial=["Greedy by earliest deadline. On each day <code>d</code>, consider all events that have started (<code>start &le; d</code>) and are not over (<code>end &ge; d</code>). Attending the one with the earliest end is never worse: if an optimal plan attends a different event today, swap them. The other event still has at least as many days left, and the urgent one is saved from expiring.",
               "Implementation: sort events by start. Keep a min-heap of end days. For the current day, push the ends of all events with that start; pop and discard ends smaller than today; if the heap is non-empty pop the smallest end, count one attended event, and move to the next day. If the heap is empty, jump straight to the start of the next unprocessed event so empty stretches of days cost nothing.",
               "Every event enters and leaves the heap once, so the time is O(n log n)."],
    time="O(n log n)", space="O(n)",
    solution='''import heapq


def maxEvents(events):
    ev = sorted(events)
    heap = []
    i = 0
    n = len(ev)
    day = 0
    count = 0
    while i < n or heap:
        if not heap:
            day = max(day, ev[i][0])
        while i < n and ev[i][0] <= day:
            heapq.heappush(heap, ev[i][1])
            i += 1
        while heap and heap[0] < day:
            heapq.heappop(heap)
        if heap:
            heapq.heappop(heap)
            count += 1
            day += 1
    return count
''',
    tests=[[[[1, 2], [2, 3], [3, 4]]], [[[1, 2], [2, 3], [3, 4], [1, 2]]], [[[1, 1], [1, 1], [1, 1]]], [[]], [[[5, 5]]],
           [[[1, 100000], [1, 100000], [1, 100000]]], [[[1, 5], [1, 5], [1, 5], [2, 2], [3, 3]]],
           [[[1, 3], [1, 3], [1, 3], [3, 4]]], [[[10, 12], [1, 2], [11, 11], [10, 10]]], [[[2, 3], [2, 3], [2, 3], [2, 3]]],
           [[[1, 4], [4, 4], [2, 2], [3, 4], [1, 1]]]],
)
_r = rnd(8106)
_ev = []
for _ in range(3000):
    _s = _r.randint(1, 100000)
    _ev.append([_s, min(100000, _s + _r.randint(0, 50))])
p["tests"].append([_ev])
_ev = []
for _ in range(3000):
    _s = _r.randint(1, 1500)
    _ev.append([_s, _r.randint(_s, 1500)])
p["tests"].append([_ev])
_ev = [[1, _r.randint(2000, 100000)] for _ in range(2500)]
p["tests"].append([_ev])


def b_events(events):
    # maximum bipartite matching of events to days (Kuhn)
    days = sorted({d for s, e in events for d in range(s, e + 1)})
    match = {}

    def try_event(i, seen):
        s, e = events[i]
        for d in range(s, e + 1):
            if d in seen:
                continue
            seen.add(d)
            if d not in match or try_event(match[d], seen):
                match[d] = i
                return True
        return False

    return sum(1 for i in range(len(events)) if try_event(i, set()))


def g_events(r):
    out = []
    for _ in range(r.randint(0, 7)):
        s = r.randint(1, 6)
        out.append([s, r.randint(s, 7)])
    return [out]


def v_events(tests):
    for t in tests:
        ev = t["args"][0]
        assert len(ev) <= 3000
        assert all(1 <= s <= e <= 100000 for s, e in ev)


CHECKS["max-events-attended"] = (b_events, g_events, "exact")
VALIDATE["max-events-attended"] = v_events


p = add(
    id="min-absolute-sum-difference", title="Minimum Absolute Sum Difference", diff="Medium", topic="Sorting", tier="extra",
    fn="minAbsSumDiff", params=[("nums1", "int[]"), ("nums2", "int[]")], ret="int", cmp="exact",
    desc="<p>The <em>absolute sum difference</em> of two arrays of equal length is the sum of <code>|nums1[i] - nums2[i]|</code> over all indices.</p><p>You may replace <strong>at most one</strong> element of <code>nums1</code> by any other element that already appears in <code>nums1</code> (you copy the value; <code>nums2</code> never changes). Return the smallest absolute sum difference you can reach.</p><pre>nums1 = [1, 7, 5], nums2 = [2, 3, 5]          -> 3\nnums1 = [2, 4, 6, 8, 10], nums2 = same        -> 0\nnums1 = [1, 10, 4, 4, 2, 7], nums2 = [9, 3, 5, 1, 7, 4] -> 20</pre><p>In the first example replace <code>7</code> with <code>1</code>: the differences become 1, 2, 0.</p>",
    constraints=["1 &le; n = nums1.length = nums2.length &le; 5,000", "1 &le; nums1[i], nums2[i] &le; 100,000"],
    hints=["First compute the current total. Replacing nums1[i] only changes the term at index i, so you want the replacement with the largest saving for a single index.",
           "For index i with target <code>nums2[i]</code>, the best replacement is the value of nums1 that is closest to <code>nums2[i]</code>. Trying every value for every index is O(n<sup>2</sup>).",
           "Keep a sorted copy of nums1. For each i binary search for <code>nums2[i]</code> and look at the two neighbours around the insertion point; the saving is <code>|nums1[i]-nums2[i]| - closest</code>. Subtract the largest saving from the total."],
    editorial=["Let <code>total</code> be the sum of all differences. If you replace <code>nums1[i]</code> with some value <code>v</code> from nums1, the total changes by <code>|v - nums2[i]| - |nums1[i] - nums2[i]|</code>, so the choices at different indices are independent and you only need the single best saving over all indices.",
               "For a fixed index the best <code>v</code> is the element of nums1 nearest to <code>nums2[i]</code>. Sort a copy of nums1 once, and for each i find with binary search the first element not smaller than <code>nums2[i]</code>; the nearest value is either that element or the one just before it. The saving at i is the old difference minus the new smallest difference (zero if no improvement).",
               "Answer: <code>total - max_saving</code>. Sorting is O(n log n) and the n binary searches are O(n log n) as well. The largest possible total here is 5,000 * 100,000, which fits in a 32-bit integer."],
    time="O(n log n)", space="O(n)",
    solution='''from bisect import bisect_left


def minAbsSumDiff(nums1, nums2):
    s = sorted(nums1)
    total = 0
    best = 0
    for a, b in zip(nums1, nums2):
        d = abs(a - b)
        total += d
        j = bisect_left(s, b)
        near = d
        if j < len(s):
            near = min(near, abs(s[j] - b))
        if j > 0:
            near = min(near, abs(s[j - 1] - b))
        if d - near > best:
            best = d - near
    return total - best
''',
    tests=[[[1, 7, 5], [2, 3, 5]], [[2, 4, 6, 8, 10], [2, 4, 6, 8, 10]], [[1, 10, 4, 4, 2, 7], [9, 3, 5, 1, 7, 4]], [[5], [100000]],
           [[1], [1]], [[1, 1, 1], [100000, 100000, 100000]], [[1, 100000], [100000, 1]], [[3, 3], [1, 5]],
           [[10, 20, 30], [30, 20, 10]], [[1, 2, 3, 4], [4, 3, 2, 1]], [[100000, 1, 100000, 1], [1, 100000, 1, 100000]]],
)
_r = rnd(8107)
p["tests"].append([[_r.randint(1, 100000) for _ in range(4000)], [_r.randint(1, 100000) for _ in range(4000)]])
p["tests"].append([[_r.randint(1, 100000) for _ in range(3000)], [_r.randint(1, 100000) for _ in range(3000)]])
p["tests"].append([[_r.randint(1, 50) for _ in range(3000)], [_r.randint(99950, 100000) for _ in range(3000)]])


def b_absdiff(nums1, nums2):
    n = len(nums1)
    base = sum(abs(a - b) for a, b in zip(nums1, nums2))
    best = base
    for i in range(n):
        for v in nums1:
            cur = base - abs(nums1[i] - nums2[i]) + abs(v - nums2[i])
            best = min(best, cur)
    return best


def g_absdiff(r):
    n = r.randint(1, 7)
    return [[r.randint(1, 15) for _ in range(n)], [r.randint(1, 15) for _ in range(n)]]


def v_absdiff(tests):
    for t in tests:
        a, b = t["args"]
        assert len(a) == len(b) and 1 <= len(a) <= 5000
        assert all(1 <= x <= 100000 for x in a + b)


CHECKS["min-absolute-sum-difference"] = (b_absdiff, g_absdiff, "exact")
VALIDATE["min-absolute-sum-difference"] = v_absdiff


p = add(
    id="smallest-range-after-k-changes", title="Smallest Range After K Changes", diff="Medium", topic="Sorting",
    fn="smallestRange", params=[("nums", "int[]"), ("k", "int")], ret="int", cmp="exact",
    desc="<p>You are given an integer array <code>nums</code> and an integer <code>k</code>. In one move you choose any element and overwrite it with <strong>any integer you like</strong>. You may make at most <code>k</code> moves.</p><p>The <em>range</em> of an array is its largest value minus its smallest value. Return the smallest range you can obtain.</p><pre>nums = [5, 3, 2, 4], k = 2             -> 1\nnums = [1, 5, 0, 10, 14], k = 3        -> 1\nnums = [6, 6, 0, 1, 1, 4, 4, 0], k = 2 -> 4</pre><p>In the first example keep 3 and 4 and overwrite 5 and 2 with 3 and 4: the array becomes [3, 3, 4, 4] with range 1.</p>",
    constraints=["1 &le; nums.length &le; 10,000", "-10<sup>9</sup> &le; nums[i] &le; 10<sup>9</sup>", "0 &le; k &le; nums.length"],
    hints=["Elements you overwrite can be given any value, so they never hurt the range if you pick a value inside it. Only the elements you <em>keep</em> determine the range.",
           "You keep at least <code>n - k</code> elements (and at least one). To make their range small, which elements should you keep: ones that are close together in value.",
           "Sort the array. The kept elements can be taken as a window of consecutive values in sorted order, of size <code>n - k</code>. Slide that window and take the smallest <code>last - first</code>. If <code>k &ge; n - 1</code> the answer is 0."],
    editorial=["Overwritten elements can be set to a value equal to one of the kept elements, so they do not widen the range. The problem becomes: choose which <code>m = n - k</code> elements to keep (all <code>k</code> moves should be used when they help) so that their max minus min is smallest. If <code>m &le; 1</code>, one kept element (or none) gives range 0.",
               "After sorting, any set of m kept elements has range at least that of the m consecutive sorted elements starting at its minimum, because replacing the kept set by the m consecutive elements from its smallest member never increases the maximum. So we only look at windows of m consecutive sorted values and return the minimum <code>a[i + m - 1] - a[i]</code>.",
               "Sorting is O(n log n) and the window sweep is O(n). The largest answer is 2*10<sup>9</sup>, which still fits in a signed 32-bit integer."],
    time="O(n log n)", space="O(n)",
    solution='''def smallestRange(nums, k):
    n = len(nums)
    m = n - k
    if m <= 1:
        return 0
    a = sorted(nums)
    return min(a[i + m - 1] - a[i] for i in range(n - m + 1))
''',
    tests=[[[5, 3, 2, 4], 2], [[1, 5, 0, 10, 14], 3], [[6, 6, 0, 1, 1, 4, 4, 0], 2], [[7], 0], [[7], 1], [[1, 10], 0], [[1, 10], 1],
           [[4, 4, 4], 0], [[-1000000000, 1000000000], 0], [[-1000000000, 0, 1000000000], 1], [[9, 1, 5, 3, 7], 0],
           [[9, 1, 5, 3, 7], 2], [[1, 2, 3, 4, 100, 200], 2]],
)
_r = rnd(8108)
p["tests"].append([[_r.randint(-10 ** 9, 10 ** 9) for _ in range(4000)], 100])
p["tests"].append([[_r.randint(-1000, 1000) for _ in range(5000)], 2500])
p["tests"].append([[_r.randint(-10 ** 9, 10 ** 9) for _ in range(3000)], 0])


def b_range(nums, k):
    n = len(nums)
    m = max(1, n - k)
    return min(max(c) - min(c) for c in combinations(nums, m))


def g_range(r):
    n = r.randint(1, 8)
    return [[r.randint(-9, 9) for _ in range(n)], r.randint(0, n)]


def v_range(tests):
    for t in tests:
        nums, k = t["args"]
        assert 1 <= len(nums) <= 10000 and all(-10 ** 9 <= x <= 10 ** 9 for x in nums)
        assert 0 <= k <= len(nums)


CHECKS["smallest-range-after-k-changes"] = (b_range, g_range, "exact")
VALIDATE["smallest-range-after-k-changes"] = v_range


p = add(
    id="job-sequencing-max-profit", title="Job Sequencing With Deadlines", diff="Medium", topic="Sorting",
    fn="maxJobProfit", params=[("deadlines", "int[]"), ("profits", "int[]")], ret="int", cmp="exact",
    desc="<p>A single machine works through jobs one at a time. Every job takes exactly one unit of time, and the machine starts at time 0, so the jobs it runs occupy the time slots 1, 2, 3, &hellip; Job <code>i</code> earns <code>profits[i]</code> but only if it finishes by its deadline: it must be placed in a slot that is at most <code>deadlines[i]</code>. A job can be skipped, and each job can run at most once.</p><p>Return the largest total profit that can be earned.</p><pre>deadlines = [2, 1, 2, 1, 3], profits = [100, 19, 27, 25, 15] -> 142\ndeadlines = [4, 1, 1, 1], profits = [20, 10, 40, 30]          -> 60\ndeadlines = [1, 1, 1], profits = [5, 6, 7]                    -> 7</pre><p>In the first example run the job worth 27 in slot 1, the job worth 100 in slot 2 and the job worth 15 in slot 3.</p>",
    constraints=["0 &le; n = deadlines.length = profits.length &le; 5,000", "1 &le; deadlines[i] &le; 1,000,000,000", "0 &le; profits[i] &le; 100,000"],
    hints=["Whatever set of jobs you pick, a feasible schedule exists if and only if the jobs can be placed in distinct slots up to their deadlines. Which jobs are the most worth fighting for a slot?",
           "Consider jobs from the highest profit to the lowest. Take a job if it can still get a slot; put it in the latest free slot not after its deadline, so earlier slots stay free for tighter jobs.",
           "Finding the latest free slot quickly: deadlines can be capped at <code>n</code> (you never run more than n jobs). Use a union-find over slots where each used slot points to the slot before it, or sort by deadline and use a min-heap of chosen profits."],
    editorial=["Sort the jobs by profit, largest first. Process them in that order and try to give each one the <em>latest</em> free slot that is not after its deadline. If there is one, the job is scheduled; otherwise it is dropped. Choosing the latest slot is safe because it leaves all earlier slots free for jobs with shorter deadlines. Accepting a job whenever it fits is safe because the sets of schedulable jobs form a matroid, so the greedy by weight gives an optimal set.",
               "Because at most n jobs can run, cap every deadline at n. To find the latest free slot at or before <code>d</code> quickly, keep a union-find array <code>parent[s]</code> where a used slot links to <code>s - 1</code>; slot 0 means no free slot. After placing a job, link its slot to the slot before it.",
               "An alternative with the same result: sort the jobs by deadline, push each profit into a min-heap, and whenever the heap holds more jobs than the current deadline allows, pop the smallest profit. Both run in O(n log n)."],
    time="O(n log n)", space="O(n)",
    solution='''def maxJobProfit(deadlines, profits):
    n = len(deadlines)
    parent = list(range(n + 1))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    total = 0
    order = sorted(range(n), key=lambda i: -profits[i])
    for i in order:
        slot = find(min(deadlines[i], n))
        if slot > 0:
            total += profits[i]
            parent[slot] = slot - 1
    return total
''',
    tests=[[[2, 1, 2, 1, 3], [100, 19, 27, 25, 15]], [[4, 1, 1, 1], [20, 10, 40, 30]], [[1, 1, 1], [5, 6, 7]], [[], []], [[1], [9]],
           [[1000000000], [100000]], [[3, 3, 3], [1, 2, 3]], [[1, 2, 3], [5, 5, 5]], [[2, 2, 2, 2], [4, 0, 9, 9]],
           [[1000000000, 1, 1000000000, 1], [5, 50, 6, 40]], [[5, 5, 5, 5, 5], [1, 2, 3, 4, 5]]],
)
_r = rnd(8109)
p["tests"].append([[_r.randint(1, 3000) for _ in range(3500)], [_r.randint(0, 100000) for _ in range(3500)]])
p["tests"].append([[_r.randint(1, 1000) for _ in range(3500)], [_r.randint(0, 100000) for _ in range(3500)]])
p["tests"].append([[_r.randint(1, 10 ** 9) for _ in range(2500)], [_r.randint(0, 100000) for _ in range(2500)]])


def b_jobseq(deadlines, profits):
    n = len(deadlines)
    best = 0
    for mask in range(1 << n):
        ds = sorted(deadlines[i] for i in range(n) if (mask >> i) & 1)
        if all(d >= t + 1 for t, d in enumerate(ds)):
            best = max(best, sum(profits[i] for i in range(n) if (mask >> i) & 1))
    return best


def g_jobseq(r):
    n = r.randint(0, 9)
    return [[r.randint(1, 5) for _ in range(n)], [r.randint(0, 20) for _ in range(n)]]


def v_jobseq(tests):
    for t in tests:
        d, pr = t["args"]
        assert len(d) == len(pr) <= 5000
        assert all(1 <= x <= 10 ** 9 for x in d) and all(0 <= x <= 100000 for x in pr)
        assert t["expected"] <= 5000 * 100000


CHECKS["job-sequencing-max-profit"] = (b_jobseq, g_jobseq, "exact")
VALIDATE["job-sequencing-max-profit"] = v_jobseq


# ---------------------------------------------------------------- HARD

p = add(
    id="maximize-capital-k-projects", title="Maximize Capital With K Projects", diff="Hard", topic="Sorting",
    fn="finalCapital", params=[("k", "int"), ("w", "int"), ("profits", "int[]"), ("capital", "int[]")], ret="int", cmp="exact",
    desc="<p>A startup has <code>w</code> units of capital and may complete at most <code>k</code> projects, one after another. Project <code>i</code> can be started only if the current capital is at least <code>capital[i]</code> (the amount is a requirement, it is <strong>not</strong> spent), and when it is finished the capital grows by <code>profits[i]</code>. Each project can be done once.</p><p>Return the largest capital you can hold after finishing at most <code>k</code> projects.</p><pre>k = 2, w = 0, profits = [1, 2, 3], capital = [0, 1, 1] -> 4\nk = 3, w = 0, profits = [1, 2, 3], capital = [0, 1, 2] -> 6\nk = 1, w = 5, profits = [4, 9], capital = [6, 5]        -> 14</pre><p>In the first example start with project 0 (capital becomes 1), then take project 2 with profit 3 (capital 4).</p>",
    constraints=["0 &le; k &le; 10,000", "0 &le; w &le; 100,000", "1 &le; n = profits.length = capital.length &le; 5,000", "0 &le; profits[i] &le; 10,000", "0 &le; capital[i] &le; 100,000,000"],
    hints=["Profits are never negative, so more capital never hurts. At each step, among the projects you can currently afford, which one should you do?",
           "The one with the largest profit: it raises your capital the most and also unlocks the most new projects. The difficulty is knowing which projects are affordable as capital grows.",
           "Sort projects by required capital. Keep a max-heap of profits of the affordable projects: before each of the k rounds move every project with <code>capital &le; w</code> into the heap, then pop the largest profit and add it to <code>w</code>. Stop early if the heap is empty."],
    editorial=["Because profits are non-negative and the requirement is not consumed, capital is monotone: doing a project can only make more projects available. In each of the k rounds the best move is to complete the affordable project with the largest profit. An exchange argument shows it: any plan that picks a smaller affordable profit now can swap it for the larger one, ending with at least the same capital and a superset of unlocked projects.",
               "To find that project quickly, sort the projects by required capital. Keep a pointer into the sorted list and a max-heap of profits. In each round, move all projects with <code>capital &le; w</code> from the sorted list into the heap, then pop the largest profit and add it to <code>w</code>. If the heap is empty, no project is affordable and we stop.",
               "Sorting is O(n log n), and every project enters and leaves the heap at most once, so the total is O((n + k) log n)."],
    time="O((n + k) log n)", space="O(n)",
    solution='''import heapq


def finalCapital(k, w, profits, capital):
    projects = sorted(zip(capital, profits))
    heap = []
    i = 0
    n = len(projects)
    for _ in range(k):
        while i < n and projects[i][0] <= w:
            heapq.heappush(heap, -projects[i][1])
            i += 1
        if not heap:
            break
        w -= heapq.heappop(heap)
    return w
''',
    tests=[[2, 0, [1, 2, 3], [0, 1, 1]], [3, 0, [1, 2, 3], [0, 1, 2]], [1, 5, [4, 9], [6, 5]], [0, 10, [5], [0]], [1, 0, [5], [1]],
           [5, 0, [1, 2, 3], [0, 1, 2]], [2, 100, [0, 0, 0], [0, 0, 0]], [3, 1, [10, 0, 50, 5], [1, 1, 12, 5]],
           [2, 1, [1, 100], [1, 3]], [4, 2, [3, 3, 3, 3], [2, 5, 8, 11]], [3, 100000, [10000, 10000], [100000000, 0]]],
)
_r = rnd(8110)
p["tests"].append([3000, 0, [_r.randint(0, 10000) for _ in range(5000)], [0] + [_r.randint(0, 3000) for _ in range(4999)]])
_cap = sorted(_r.randint(0, 10 ** 8) for _ in range(4000))
p["tests"].append([4000, 1000, [_r.randint(0, 10000) for _ in range(4000)], _cap])
p["tests"].append([10000, 5, [_r.randint(0, 10) for _ in range(4000)], [i * 5 for i in range(4000)]])


def b_capital(k, w, profits, capital):
    best = w

    def go(w, done, left):
        nonlocal best
        best = max(best, w)
        if left == 0:
            return
        for i in range(len(profits)):
            if not (done >> i) & 1 and capital[i] <= w:
                go(w + profits[i], done | (1 << i), left - 1)

    go(w, 0, k)
    return best


def g_capital(r):
    n = r.randint(1, 6)
    return [r.randint(0, 4), r.randint(0, 5), [r.randint(0, 6) for _ in range(n)], [r.randint(0, 12) for _ in range(n)]]


def v_capital(tests):
    for t in tests:
        k, w, pr, cap = t["args"]
        assert len(pr) == len(cap) and 1 <= len(pr) <= 5000
        assert 0 <= k <= 10000 and 0 <= w <= 100000
        assert all(0 <= x <= 10000 for x in pr) and all(0 <= x <= 10 ** 8 for x in cap)


CHECKS["maximize-capital-k-projects"] = (b_capital, g_capital, "exact")
VALIDATE["maximize-capital-k-projects"] = v_capital


p = add(
    id="min-max-score-marble-bags", title="Marble Bags: Best Minus Worst Split", diff="Hard", topic="Sorting", tier="extra",
    fn="marbleScoreGap", params=[("weights", "int[]"), ("k", "int")], ret="int", cmp="exact",
    desc="<p>The marbles <code>weights[0..n-1]</code> lie in a row. You must split the row into exactly <code>k</code> non-empty bags, each bag being a block of <strong>consecutive</strong> marbles. The cost of a bag that spans indices <code>i..j</code> is <code>weights[i] + weights[j]</code> (for a bag with a single marble that is twice its weight). The score of a split is the sum of the costs of its bags.</p><p>Over all valid splits, find the maximum score and the minimum score, and return <strong>maximum minus minimum</strong>.</p><pre>weights = [1, 3, 5, 1], k = 2   -> 4\nweights = [1, 3], k = 2         -> 0\nweights = [4, 2, 9], k = 1      -> 0</pre><p>In the first example the splits [1][3,5,1], [1,3][5,1], [1,3,5][1] score 6, 10 and 8, so the answer is 10 - 6.</p>",
    constraints=["1 &le; k &le; n = weights.length &le; 10,000", "1 &le; weights[i] &le; 10,000"],
    hints=["Write the score of a split in terms of its cut points. Every split always includes the first and the last marble in its cost; what else is counted?",
           "Each cut between positions <code>i</code> and <code>i+1</code> adds <code>weights[i] + weights[i+1]</code> to the score, on top of the fixed <code>weights[0] + weights[n-1]</code>. The k - 1 cuts are independent of each other.",
           "Compute the n - 1 values <code>weights[i] + weights[i+1]</code> and sort them. The maximum score takes the k - 1 largest of them, the minimum score takes the k - 1 smallest; the fixed part cancels in the difference."],
    editorial=["Consider a split with cuts after positions <code>c_1 &lt; c_2 &lt; &hellip; &lt; c_{k-1}</code>. The bags are [0..c_1], [c_1+1..c_2], &hellip;. The first bag contributes <code>weights[0] + weights[c_1]</code>, the next one <code>weights[c_1+1] + weights[c_2]</code>, and so on. Grouping the terms, the score equals <code>weights[0] + weights[n-1] + &sum; (weights[c] + weights[c+1])</code> over the cuts.",
               "So the score is a constant plus the sum of the pair values <code>pair[c] = weights[c] + weights[c+1]</code> of the chosen cuts, and any set of k - 1 distinct cut positions among the n - 1 gaps is a valid split. Hence the maximum score uses the k - 1 largest pair values and the minimum uses the k - 1 smallest. The constant cancels when subtracting.",
               "Sort the pair values and subtract the sum of the k - 1 smallest from the sum of the k - 1 largest. When k = 1 or k = n the two sets coincide and the answer is 0. Time O(n log n)."],
    time="O(n log n)", space="O(n)",
    solution='''def marbleScoreGap(weights, k):
    pairs = sorted(weights[i] + weights[i + 1] for i in range(len(weights) - 1))
    if k == 1:
        return 0
    return sum(pairs[len(pairs) - (k - 1):]) - sum(pairs[:k - 1])
''',
    tests=[[[1, 3, 5, 1], 2], [[1, 3], 2], [[4, 2, 9], 1], [[7], 1], [[5, 5, 5, 5], 2], [[5, 5, 5, 5], 4], [[1, 10000, 1, 10000, 1], 3],
           [[1, 2, 3, 4, 5, 6], 3], [[6, 5, 4, 3, 2, 1], 6], [[9, 1, 9, 1, 9, 1, 9], 2], [[10000] * 10, 5]],
)
_r = rnd(8111)
p["tests"].append([[_r.randint(1, 10000) for _ in range(6000)], 3000])
p["tests"].append([[_r.randint(1, 10000) for _ in range(6000)], 5999])
p["tests"].append([[_r.randint(1, 10000) for _ in range(5000)], 2])


def b_marbles(weights, k):
    n = len(weights)
    scores = []
    for cuts in combinations(range(n - 1), k - 1):
        starts = [0] + [c + 1 for c in cuts]
        ends = list(cuts) + [n - 1]
        scores.append(sum(weights[a] + weights[b] for a, b in zip(starts, ends)))
    return max(scores) - min(scores)


def g_marbles(r):
    n = r.randint(1, 9)
    return [[r.randint(1, 12) for _ in range(n)], r.randint(1, n)]


def v_marbles(tests):
    for t in tests:
        w, k = t["args"]
        assert 1 <= k <= len(w) <= 10000 and all(1 <= x <= 10000 for x in w)


CHECKS["min-max-score-marble-bags"] = (b_marbles, g_marbles, "exact")
VALIDATE["min-max-score-marble-bags"] = v_marbles
