"""Problems: greedy, two-sided (both neighbours, both ends, balanced distribution). See data/lib.py for the registry."""
import heapq
from collections import deque
from itertools import product

from lib import add, rnd, CHECKS, VALIDATE, gen_arr  # noqa: F401

INT_MIN, INT_MAX = -(2 ** 31), 2 ** 31 - 1


# ---------------------------------------------------------------- EASY

p = add(
    id="max-new-flowers-in-bed", title="Plant the Most Flowers", diff="Easy", topic="Greedy", tier="common",
    fn="maxNewFlowers", params=[("bed", "int[]")], ret="int", cmp="exact",
    desc="<p>A garden bed is a row of plots. <code>bed[i] = 1</code> means plot <code>i</code> already holds a flower and <code>bed[i] = 0</code> means it is empty. No two existing flowers are next to each other.</p><p>You may plant a new flower in an empty plot only if <strong>both</strong> neighbouring plots (the ones that exist) are free of flowers, old or newly planted. Return the maximum number of new flowers you can plant.</p><pre>bed = [1,0,0,0,1]  -> 1\nbed = [0,0,0,0,0]  -> 3\nbed = [0,0,1,0,0]  -> 2</pre><p>In the second example, plant at plots 0, 2 and 4.</p>",
    constraints=["1 &le; bed.length &le; 10,000", "bed[i] is 0 or 1", "The input has no two adjacent 1s"],
    hints=["A new flower blocks both of its neighbours. Which plot should you plant in first so that you block as little useful space as possible?",
           "Scan from the left. The leftmost plot you can still plant in is never a worse choice than any plot to its right.",
           "Walk through the plots; whenever a plot is empty and its left neighbour and right neighbour (if they exist) are empty, plant there, count it and mark the plot as occupied."],
    editorial=["Scan left to right and plant a flower in every plot that is currently allowed. Planting in the leftmost allowed plot is safe by an exchange argument: in any optimal answer, the leftmost planted flower can be moved to the leftmost allowed plot without touching anything further right than the plot it blocks, so the count cannot drop.",
               "Mark the plot as occupied as soon as you plant, so the next plot sees the new flower as its left neighbour. Edge plots only check the one neighbour they have. Equivalently, every run of <code>m</code> empty plots between two existing flowers fits <code>(m - 1) // 2</code> new ones, a run touching one border fits <code>m // 2</code>, and a completely empty bed fits <code>(n + 1) // 2</code>. One pass, O(n)."],
    time="O(n)", space="O(n)",
    solution='''def maxNewFlowers(bed):
    b = list(bed)
    n = len(b)
    count = 0
    for i in range(n):
        if b[i] == 0 and (i == 0 or b[i - 1] == 0) and (i == n - 1 or b[i + 1] == 0):
            b[i] = 1
            count += 1
    return count
''',
    tests=[[[1, 0, 0, 0, 1]], [[0, 0, 0, 0, 0]], [[0, 0, 1, 0, 0]], [[0]], [[1]], [[0, 0]], [[1, 0, 1]], [[0, 1, 0]],
           [[0, 0, 0]], [[1, 0, 0, 1]], [[0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 1, 0, 0]]],
)
_r = rnd(4401)


def _valid_bed(r, n, prob):
    out = []
    for i in range(n):
        out.append(1 if (not out or out[-1] == 0) and r.random() < prob else 0)
    return out


p["tests"].append([[0] * 8000])
p["tests"].append([_valid_bed(_r, 8000, 0.3)])
p["tests"].append([_valid_bed(_r, 7000, 0.12)])
p["tests"].append([[1, 0, 0, 0] * 2000 + [1]])


def b_flowers(bed):
    n = len(bed)
    empties = [i for i in range(n) if bed[i] == 0]
    best = 0
    for mask in range(1 << len(empties)):
        cur = list(bed)
        for t, i in enumerate(empties):
            if (mask >> t) & 1:
                cur[i] = 1
        if all(not (cur[i] and cur[i + 1]) for i in range(n - 1)):
            best = max(best, bin(mask).count("1"))
    return best


def g_flowers(r):
    return [_valid_bed(r, r.randint(1, 12), r.choice([0.0, 0.2, 0.4]))]


def v_flowers(tests):
    for t in tests:
        bed = t["args"][0]
        assert 1 <= len(bed) <= 10000 and all(x in (0, 1) for x in bed)
        assert all(not (bed[i] and bed[i + 1]) for i in range(len(bed) - 1)), "adjacent flowers in input"


CHECKS["max-new-flowers-in-bed"] = (b_flowers, g_flowers, "exact")
VALIDATE["max-new-flowers-in-bed"] = v_flowers


p = add(
    id="farthest-seat-from-everyone", title="Farthest Seat From Everyone", diff="Easy", topic="Greedy", tier="common",
    fn="maxDistToClosest", params=[("seats", "int[]")], ret="int", cmp="exact",
    desc="<p>A row of seats is given by <code>seats</code>: <code>seats[i] = 1</code> means seat <code>i</code> is taken and <code>0</code> means it is free. At least one seat is taken and at least one is free.</p><p>You will choose a free seat. The distance from your seat <code>i</code> to the closest taken seat is the minimum of <code>|i - j|</code> over all taken seats <code>j</code>. Return the largest such distance you can achieve.</p><pre>seats = [1,0,0,0,1,0,1]  -> 2\nseats = [1,0,0,0]        -> 3\nseats = [0,1]            -> 1</pre><p>In the first example sit at seat 2: the taken seats 0 and 4 are both 2 away.</p>",
    constraints=["2 &le; seats.length &le; 10,000", "seats[i] is 0 or 1", "At least one 0 and at least one 1 appear"],
    hints=["Only the free stretches (gaps) between taken seats matter. What are the different kinds of gaps?",
           "A gap between two taken seats is best used in its middle. A gap at the very start or very end of the row has a taken seat on only one side.",
           "For a gap bounded on both sides by taken seats at positions <code>a &lt; b</code>, the best distance is <code>(b - a) // 2</code>. For a gap at the left end the best seat is seat 0, with distance equal to the index of the first taken seat; symmetrically for the right end."],
    editorial=["Scan the row and remember the position of the last taken seat. Three kinds of gaps exist. Before the first taken seat at index <code>f</code>, the best choice is seat 0 and the distance is <code>f</code>. After the last taken seat at index <code>l</code>, the best choice is the final seat with distance <code>n - 1 - l</code>. Between two consecutive taken seats <code>a &lt; b</code>, the best choice is the middle, with distance <code>(b - a) // 2</code>.",
               "The answer is the maximum over all gaps. The reason end gaps are handled differently is that they lack the second neighbour that halves the distance. One pass and O(1) extra memory."],
    time="O(n)", space="O(1)",
    solution='''def maxDistToClosest(seats):
    n = len(seats)
    best = 0
    last = -1
    for i, s in enumerate(seats):
        if s == 1:
            if last == -1:
                best = i
            else:
                best = max(best, (i - last) // 2)
            last = i
    return max(best, n - 1 - last)
''',
    tests=[[[1, 0, 0, 0, 1, 0, 1]], [[1, 0, 0, 0]], [[0, 1]], [[1, 0]], [[0, 0, 1]], [[1, 0, 1]], [[1, 0, 0, 1]],
           [[0, 0, 0, 1, 0, 0, 0, 0, 1, 0]], [[1, 1, 0, 1, 1]], [[0, 1, 0, 0, 0, 0, 0, 1, 0]]],
)
_r = rnd(4402)
p["tests"].append([[1] + [0] * 7998 + [1]])
p["tests"].append([[0] * 5000 + [1]])
p["tests"].append([[1 if _r.random() < 0.02 else 0 for _ in range(7000)][:-2] + [0, 1]])
p["tests"].append([[1 if _r.random() < 0.5 else 0 for _ in range(6000)][:-1] + [0]])


def b_seat(seats):
    taken = [j for j, s in enumerate(seats) if s]
    return max(min(abs(i - j) for j in taken) for i, s in enumerate(seats) if not s)


def g_seat(r):
    n = r.randint(2, 12)
    a = [1 if r.random() < r.choice([0.15, 0.4]) else 0 for _ in range(n)]
    i, j = r.sample(range(n), 2)
    a[i], a[j] = 1, 0
    return [a]


def v_seat(tests):
    for t in tests:
        s = t["args"][0]
        assert 2 <= len(s) <= 10000 and set(s) == {0, 1}


CHECKS["farthest-seat-from-everyone"] = (b_seat, g_seat, "exact")
VALIDATE["farthest-seat-from-everyone"] = v_seat


# ---------------------------------------------------------------- MEDIUM

p = add(
    id="min-moves-to-level-piles", title="Level the Piles on a Line", diff="Medium", topic="Greedy", tier="common",
    fn="levelPiles", params=[("piles", "int[]")], ret="int", cmp="exact",
    desc="<p>Stones are arranged in a row of piles; <code>piles[i]</code> is the number of stones in pile <code>i</code>. In one move you take a single stone from a non-empty pile and drop it on an <strong>adjacent</strong> pile (left or right neighbour).</p><p>Return the minimum number of moves that makes all piles contain the same number of stones, or <code>-1</code> if that is impossible.</p><pre>piles = [1,0,5]  -> 4\npiles = [2,2,2]  -> 0\npiles = [1,2]    -> -1</pre><p>In the first example the target is 2 stones per pile. Moving a stone from pile 2 to pile 1, then 1 to 0, then 2 to 1 twice (four moves) gives 2, 2, 2.</p>",
    constraints=["1 &le; piles.length &le; 5,000", "0 &le; piles[i]", "sum(piles) &le; 100,000"],
    hints=["Equal piles are only possible if the total is divisible by the number of piles. What would each pile hold then?",
           "Look at the boundary between pile <code>i</code> and pile <code>i + 1</code>. The left part has a surplus or a deficit compared to its target.",
           "That surplus (or deficit) must cross the boundary one stone at a time, and every crossing costs one move. Sum the absolute prefix surplus over all boundaries."],
    editorial=["Let <code>avg = sum / n</code>; if the sum is not divisible by <code>n</code> the answer is -1. For each boundary between pile <code>i</code> and <code>i + 1</code>, compute <code>s_i = (piles[0] + ... + piles[i]) - (i + 1) * avg</code>, the net number of stones the left part has to give away (positive) or receive (negative). Exactly <code>|s_i|</code> stones must cross that boundary, and each crossing is one move, so the answer is at least <code>sum |s_i|</code>.",
               "That lower bound is achievable: whenever a boundary needs to push stones to the right, push from a pile that has stones; a feasible order always exists (always move a stone from a pile that can currently give it), so no stone has to wait for another. One pass and O(1) memory. The result stays below about 2.5 &times; 10<sup>8</sup> under the stated limits."],
    time="O(n)", space="O(1)",
    solution='''def levelPiles(piles):
    n = len(piles)
    total = sum(piles)
    if total % n:
        return -1
    avg = total // n
    prefix = 0
    moves = 0
    for i in range(n - 1):
        prefix += piles[i] - avg
        moves += abs(prefix)
    return moves
''',
    tests=[[[1, 0, 5]], [[2, 2, 2]], [[1, 2]], [[0]], [[7]], [[3, 0]], [[0, 0, 6]], [[4, 0, 0, 0]], [[1, 1, 1, 5]],
           [[5, 0, 0, 1, 0, 0, 6]], [[0, 9, 0]]],
)
_r = rnd(4403)


def _shuffled_level(r, n, avg, steps):
    a = [avg] * n
    for _ in range(steps):
        i = r.randrange(n)
        j = r.randrange(n)
        if a[i] > 0:
            a[i] -= 1
            a[j] += 1
    return a


p["tests"].append([[100000] + [0] * 4999])
p["tests"].append([[0] * 2499 + [50000] + [0] * 2 + [50000] + [0] * 2497])
p["tests"].append([_shuffled_level(_r, 5000, 20, 60000)])
p["tests"].append([_shuffled_level(_r, 3000, 1, 9000)])


def b_piles(piles):
    n, total = len(piles), sum(piles)
    if total % n:
        return -1
    goal = tuple([total // n] * n)
    start = tuple(piles)
    seen = {start}
    dq = deque([(start, 0)])
    while dq:
        s, d = dq.popleft()
        if s == goal:
            return d
        for i in range(n):
            if s[i] > 0:
                for j in (i - 1, i + 1):
                    if 0 <= j < n:
                        t = list(s)
                        t[i] -= 1
                        t[j] += 1
                        t = tuple(t)
                        if t not in seen:
                            seen.add(t)
                            dq.append((t, d + 1))
    return -1


def g_piles(r):
    n = r.randint(1, 4)
    if r.random() < 0.7:
        avg = r.randint(0, 2)
        a = [0] * n
        for _ in range(avg * n):
            a[r.randrange(n)] += 1
        return [a]
    return [[r.randint(0, 3) for _ in range(n)]]


def v_piles(tests):
    for t in tests:
        a = t["args"][0]
        assert 1 <= len(a) <= 5000 and all(x >= 0 for x in a) and sum(a) <= 100000


CHECKS["min-moves-to-level-piles"] = (b_piles, g_piles, "exact")
VALIDATE["min-moves-to-level-piles"] = v_piles


p = add(
    id="zigzag-by-lowering-elements", title="Zigzag by Lowering", diff="Medium", topic="Greedy", tier="common",
    fn="movesToZigzag", params=[("nums", "int[]")], ret="int", cmp="exact",
    desc="<p>In one move you may choose any element of <code>nums</code> and decrease it by 1. Elements may become negative.</p><p>The array is a <em>valley zigzag</em> if one of the two holds (indices start at 0):</p><ul><li>every element at an <strong>even</strong> index is strictly smaller than each of its adjacent elements, or</li><li>every element at an <strong>odd</strong> index is strictly smaller than each of its adjacent elements.</li></ul><p>Return the minimum number of moves needed to turn <code>nums</code> into a valley zigzag.</p><pre>nums = [1,2,3]      -> 2\nnums = [9,6,1,6,2]  -> 4</pre>",
    constraints=["1 &le; nums.length &le; 10,000", "1 &le; nums[i] &le; 1,000"],
    hints=["There are only two shapes to aim for: even indices are the valleys, or odd indices are the valleys. Solve each shape separately and take the cheaper.",
           "Lowering an element that is meant to be a peak can never help anybody. Only valleys need to be lowered.",
           "For a valley at index <code>i</code>, look at both neighbours. It must end up at most <code>min(left, right) - 1</code>, so its cost is <code>max(0, nums[i] - min(left, right) + 1)</code>; a missing neighbour is ignored. Neighbours are peaks and stay unchanged."],
    editorial=["Fix which parity holds the valleys. Peaks are never changed (decreasing a peak only makes its neighbours' job harder), so every valley is independent: it must be strictly less than the original values of its one or two neighbours, which costs <code>max(0, nums[i] - min(neighbours) + 1)</code> moves. Sum this over all valleys of that parity.",
               "Repeat for the other parity and return the smaller total. The greedy part is that each valley goes exactly one below its smaller neighbour, no further. Time O(n), space O(1)."],
    time="O(n)", space="O(1)",
    solution='''def movesToZigzag(nums):
    n = len(nums)
    INF = 10 ** 9
    best = None
    for start in (0, 1):
        cost = 0
        for i in range(start, n, 2):
            left = nums[i - 1] if i > 0 else INF
            right = nums[i + 1] if i + 1 < n else INF
            m = min(left, right)
            if nums[i] >= m:
                cost += nums[i] - m + 1
        best = cost if best is None else min(best, cost)
    return best
''',
    tests=[[[1, 2, 3]], [[9, 6, 1, 6, 2]], [[5]], [[2, 2]], [[1, 1, 1, 1]], [[3, 2, 1]], [[1, 5, 1, 5, 1]], [[7, 7, 7]],
           [[10, 1, 10, 1, 10, 1]], [[1000, 1000, 1000, 1000, 1000]], [[1, 2, 3, 4, 5, 6, 7]]],
)
_r = rnd(4404)
p["tests"].append([[_r.randint(1, 1000) for _ in range(7000)]])
p["tests"].append([[1000] * 8000])
p["tests"].append([[1 + (i % 1000) for i in range(8000)]])
p["tests"].append([[(1000 if i % 2 else _r.randint(1, 5)) for i in range(6000)]])


def b_zigzag(nums):
    # dp over the final values: valleys must end strictly below both neighbours, any element may be lowered
    n = len(nums)
    lo = min(nums) - 1
    best = None
    for par in (0, 1):
        dp = {v: nums[0] - v for v in range(lo, nums[0] + 1)}
        for i in range(1, n):
            nd = {}
            for v in range(lo, nums[i] + 1):
                cost = None
                for pv, pc in dp.items():
                    valley_prev = (i - 1) % 2 == par
                    ok = (pv < v) if valley_prev else (v < pv)
                    if ok and (cost is None or pc < cost):
                        cost = pc
                if cost is not None:
                    nd[v] = cost + nums[i] - v
            dp = nd
        if dp:
            c = min(dp.values())
            if best is None or c < best:
                best = c
    return best


def g_zigzag(r):
    return [[r.randint(1, 4) for _ in range(r.randint(1, 5))]]


def v_zigzag(tests):
    for t in tests:
        a = t["args"][0]
        assert 1 <= len(a) <= 10000 and all(1 <= x <= 1000 for x in a)


CHECKS["zigzag-by-lowering-elements"] = (b_zigzag, g_zigzag, "exact")
VALIDATE["zigzag-by-lowering-elements"] = v_zigzag


p = add(
    id="cinema-rows-group-seating", title="Seating Groups of Four", diff="Medium", topic="Greedy", tier="extra",
    fn="maxSeatedGroups", params=[("rows", "int"), ("reserved", "int[][]")], ret="int", cmp="exact",
    desc="<p>A theatre has <code>rows</code> rows, numbered from 1, and every row has 10 seats numbered 1 to 10. The entry <code>reserved[i] = [row, seat]</code> is a seat that is already taken.</p><p>A group of four people must sit together on four consecutive seats of one row. Because of the aisles, the only blocks of seats a group may use are <strong>2-5</strong>, <strong>4-7</strong> and <strong>6-9</strong>. Two groups cannot share a seat, and no group may use a reserved seat.</p><p>Return the maximum number of groups that can be seated in the whole theatre.</p><pre>rows = 4, reserved = [[1,2],[1,8],[2,6],[3,1],[3,10]]  -> 6\nrows = 2, reserved = []                                -> 4</pre><p>In the first example row 1 fits one group (seats 4-7), row 2 fits one (seats 2-5), row 3 fits two (2-5 and 6-9) and row 4 is empty and fits two.</p>",
    constraints=["1 &le; rows &le; 10<sup>9</sup>", "0 &le; reserved.length &le; 10,000", "1 &le; reserved[i][0] &le; rows and 1 &le; reserved[i][1] &le; 10", "All reserved seats are distinct"],
    hints=["Rows are independent. How many groups can one row hold at most, given the three allowed blocks?",
           "Blocks 2-5 and 6-9 do not overlap, so a row fits two groups exactly when both of them are free. Block 4-7 overlaps both.",
           "Per row: two groups if blocks 2-5 and 6-9 are both free, otherwise one group if any of the three blocks is free, otherwise zero. Rows without reservations contribute 2 each and must not be looped over one by one."],
    editorial=["Only rows that appear in <code>reserved</code> need work. Collect the reserved seats of each such row. The left block 2-5 is free when no reserved seat lies in 2..5, the right block 6-9 when none lies in 6..9, and the middle block 4-7 when none lies in 4..7.",
               "If left and right are both free the row takes two groups. Otherwise the row takes one group if the middle, the left or the right block is free (they all overlap pairwise), else none. Add <code>2 * (rows - number of rows with reservations)</code> for the untouched rows. Time O(m) for m reservations, independent of the number of rows. The maximum answer 2 &times; 10<sup>9</sup> still fits into 32 bits."],
    time="O(m)", space="O(m)",
    solution='''def maxSeatedGroups(rows, reserved):
    taken = {}
    for r, s in reserved:
        taken.setdefault(r, set()).add(s)
    total = 2 * (rows - len(taken))
    for seats in taken.values():
        left = not any(2 <= s <= 5 for s in seats)
        right = not any(6 <= s <= 9 for s in seats)
        mid = not any(4 <= s <= 7 for s in seats)
        if left and right:
            total += 2
        elif left or right or mid:
            total += 1
    return total
''',
    tests=[[4, [[1, 2], [1, 8], [2, 6], [3, 1], [3, 10]]], [2, []], [1, [[1, 5]]], [1, [[1, 1], [1, 10]]],
           [1, [[1, 2], [1, 9]]], [1, [[1, 3], [1, 8]]], [3, [[2, 4], [2, 7]]], [2, [[1, i] for i in range(1, 11)]],
           [5, [[1, 5], [2, 6], [3, 5], [3, 6], [5, 10]]], [1000000000, []], [1000000000, [[1, 1], [1000000000, 10]]]],
)
_r = rnd(4405)
for _rows, _m in ((2000, 8000), (10 ** 9, 3000), (30, 250)):
    _res = set()
    while len(_res) < min(_m, _rows * 10 // 2):
        _res.add((_r.randint(1, _rows), _r.randint(1, 10)))
    p["tests"].append([_rows, [list(x) for x in sorted(_res)]])


def b_cinema(rows, reserved):
    total = 0
    taken = set(map(tuple, reserved))
    blocks = [(2, 5), (4, 7), (6, 9)]
    for row in range(1, rows + 1):
        best = 0
        for mask in range(8):
            chosen = [blocks[t] for t in range(3) if (mask >> t) & 1]
            seats = []
            for a, b in chosen:
                seats += list(range(a, b + 1))
            if len(seats) == len(set(seats)) and all((row, s) not in taken for s in seats):
                best = max(best, len(chosen))
        total += best
    return total


def g_cinema(r):
    rows = r.randint(1, 4)
    cells = [(a, b) for a in range(1, rows + 1) for b in range(1, 11)]
    res = r.sample(cells, r.randint(0, min(len(cells), 8)))
    return [rows, [list(x) for x in res]]


def v_cinema(tests):
    for t in tests:
        rows, res = t["args"]
        assert 1 <= rows <= 10 ** 9 and len(res) <= 10000
        assert len({tuple(x) for x in res}) == len(res)
        assert all(1 <= a <= rows and 1 <= b <= 10 for a, b in res)


CHECKS["cinema-rows-group-seating"] = (b_cinema, g_cinema, "exact")
VALIDATE["cinema-rows-group-seating"] = v_cinema


p = add(
    id="candy-with-equal-rating-ties", title="Candy With Equal Ties", diff="Medium", topic="Greedy", tier="extra",
    fn="candyWithTies", params=[("ratings", "int[]")], ret="int", cmp="exact",
    desc="<p>Children stand in a line and child <code>i</code> has rating <code>ratings[i]</code>. Every child gets at least one candy. For two <strong>adjacent</strong> children:</p><ul><li>if one has a strictly higher rating, that child must receive strictly more candies;</li><li>if the ratings are equal, both must receive <strong>exactly the same</strong> number of candies.</li></ul><p>Return the minimum total number of candies.</p><pre>ratings = [1,2,2]    -> 5\nratings = [1,3,3,2]  -> 6\nratings = [4,4,4]    -> 3</pre><p>In the first example the two children rated 2 must get the same amount, and they are above the child rated 1, so the candies are 1, 2, 2.</p>",
    constraints=["1 &le; ratings.length &le; 10,000", "0 &le; ratings[i] &le; 20,000"],
    hints=["Children with equal ratings next to each other must behave identically. Treat a maximal run of equal ratings as a single unit.",
           "After merging runs, neighbouring units always have different ratings, so you are back to a classic two-direction candy problem on the units.",
           "Compute the minimum candy per unit with a left-to-right and a right-to-left pass (take the maximum of both), then multiply each unit's candy by the number of children in the run and add everything up."],
    editorial=["Compress consecutive equal ratings into runs, keeping the length of each run. All children of a run get the same number of candies, and the only constraints that remain are between neighbouring runs, whose ratings differ.",
               "On the runs, do the usual two sweeps: left to right give <code>c[i] = c[i-1] + 1</code> when the run rating exceeds the previous one (else 1), then right to left raise <code>c[i]</code> to <code>c[i+1] + 1</code> when the run rating exceeds the next one and it is not already larger. Each run's value is the smallest allowed, so the total <code>sum(c[i] * length[i])</code> is minimal. O(n) time and space."],
    time="O(n)", space="O(n)",
    solution='''def candyWithTies(ratings):
    vals = []
    cnt = []
    for x in ratings:
        if vals and vals[-1] == x:
            cnt[-1] += 1
        else:
            vals.append(x)
            cnt.append(1)
    m = len(vals)
    c = [1] * m
    for i in range(1, m):
        if vals[i] > vals[i - 1]:
            c[i] = c[i - 1] + 1
    for i in range(m - 2, -1, -1):
        if vals[i] > vals[i + 1] and c[i] <= c[i + 1]:
            c[i] = c[i + 1] + 1
    return sum(ci * k for ci, k in zip(c, cnt))
''',
    tests=[[[1, 2, 2]], [[1, 3, 3, 2]], [[4, 4, 4]], [[7]], [[1, 0, 2]], [[2, 2, 1, 1, 2, 2]], [[1, 2, 3, 3, 3, 2, 1]],
           [[5, 4, 3, 2, 1]], [[0, 20000, 20000, 0]], [[3, 1, 1, 1, 3]], [[1, 1, 2, 3, 3, 4, 4, 4, 0]]],
)
_r = rnd(4406)
p["tests"].append([[_r.randint(0, 5) for _ in range(7000)]])
p["tests"].append([[x for v in range(0, 2000, 1) for x in [v] * _r.randint(1, 3)][:6000]])
_a = []
while len(_a) < 6000:
    _a += [_r.randint(0, 20000)] * _r.randint(1, 4)
p["tests"].append([_a[:6000]])


def b_candy_ties(ratings):
    n = len(ratings)
    c = [1] * n
    changed = True
    while changed:
        changed = False
        for i in range(n):
            for j in (i - 1, i + 1):
                if 0 <= j < n:
                    if ratings[i] > ratings[j] and c[i] <= c[j]:
                        c[i] = c[j] + 1
                        changed = True
                    elif ratings[i] == ratings[j] and c[i] < c[j]:
                        c[i] = c[j]
                        changed = True
    return sum(c)


def g_candy_ties(r):
    return [[r.randint(0, r.choice([1, 2, 3])) for _ in range(r.randint(1, 9))]]


def v_candy_ties(tests):
    for t in tests:
        a = t["args"][0]
        assert 1 <= len(a) <= 10000 and all(0 <= x <= 20000 for x in a)


CHECKS["candy-with-equal-rating-ties"] = (b_candy_ties, g_candy_ties, "exact")
VALIDATE["candy-with-equal-rating-ties"] = v_candy_ties


p = add(
    id="seat-of-kth-arrival", title="Seat of the K-th Student", diff="Medium", topic="Greedy", tier="common",
    fn="seatOfArrival", params=[("n", "int"), ("k", "int")], ret="int", cmp="exact",
    desc="<p>A long bench has <code>n</code> seats numbered <code>0</code> to <code>n - 1</code>. Students arrive one at a time and nobody ever leaves.</p><p>The first student sits at seat <code>0</code>. Every later student picks the free seat whose distance to the <strong>closest seated student</strong> is as large as possible; if several seats give the same largest distance, the one with the smallest number is taken.</p><p>Return the seat taken by the <code>k</code>-th student (counting from 1).</p><pre>n = 10: the seats are taken in the order 0, 9, 4, 2, 6, 1, 3, 5, 7, 8\nn = 10, k = 4  -> 2\nn = 10, k = 10 -> 8</pre>",
    constraints=["1 &le; n &le; 10<sup>9</sup>", "1 &le; k &le; min(n, 50,000)"],
    hints=["Simulating over all n seats per student is far too slow. Think about the free stretches between seated students instead.",
           "Each stretch between two seated students has one best seat (its middle, the smaller one on ties) and a known distance. The stretch behind the last seated student also needs a rule.",
           "Keep the best seat of every stretch in a heap ordered by (largest distance, smallest seat). Pop the best, then split its stretch into two new stretches. The end of the bench (seat n-1) starts as a one-sided stretch with distance n-1."],
    editorial=["After the first student sits at seat 0, the free seats form stretches. A stretch strictly between seated students at <code>l &lt; r</code> offers its best seat at <code>(l + r) // 2</code> with distance <code>(r - l) // 2</code>. The only one-sided stretch is the tail after the last seated student; its best seat is <code>n - 1</code> at distance <code>n - 1 - l</code>, because there is no second neighbour. (No head stretch exists since seat 0 is taken first.)",
               "The global choice at each step is the best candidate over all stretches, which is the minimum of the tuples <code>(-distance, seat)</code> in a heap. Taking a seat splits its stretch into two interior stretches whose candidates are pushed. Only <code>k</code> pops are needed, so the work is O(k log k) no matter how large n is."],
    time="O(k log k)", space="O(k)",
    solution='''import heapq

def seatOfArrival(n, k):
    if k == 1:
        return 0
    heap = [(-(n - 1), n - 1, 0, -1)]  # (-distance, seat, left, right); right == -1 marks the tail
    seat = 0

    def push(l, r):
        if r - l >= 2:
            s = (l + r) // 2
            heapq.heappush(heap, (-(s - l), s, l, r))

    for _ in range(k - 1):
        d, seat, l, r = heapq.heappop(heap)
        if r == -1:
            push(l, seat)
        else:
            push(l, seat)
            push(seat, r)
    return seat
''',
    tests=[[10, 4], [10, 10], [10, 1], [10, 2], [10, 3], [1, 1], [2, 2], [3, 3], [5, 4], [7, 7], [100, 37]],
)
p["tests"].append([10 ** 9, 50000])
p["tests"].append([50000, 50000])
p["tests"].append([10 ** 9, 49999])
p["tests"].append([123456789, 31337])


def b_kth(n, k):
    seated = [0]
    last = 0
    for _ in range(k - 1):
        best = (-1, 0)
        for s in range(n):
            if s in seated:
                continue
            d = min(abs(s - t) for t in seated)
            if d > best[0]:
                best = (d, s)
        last = best[1]
        seated.append(last)
    return last if k > 1 else 0


def g_kth(r):
    n = r.randint(1, 14)
    return [n, r.randint(1, n)]


def v_kth(tests):
    for t in tests:
        n, k = t["args"]
        assert 1 <= n <= 10 ** 9 and 1 <= k <= min(n, 50000)


CHECKS["seat-of-kth-arrival"] = (b_kth, g_kth, "exact")
VALIDATE["seat-of-kth-arrival"] = v_kth


p = add(
    id="min-merges-to-palindrome-array", title="Merge Into a Palindrome", diff="Medium", topic="Greedy", tier="common",
    fn="minMergesForPalindrome", params=[("nums", "int[]")], ret="int", cmp="exact",
    desc="<p>You are given an array of positive integers. One operation takes two <strong>adjacent</strong> elements and replaces them by a single element equal to their sum, so the array becomes one element shorter.</p><p>Return the minimum number of operations after which the array is a palindrome (it reads the same from left to right and from right to left). A single element is a palindrome.</p><pre>nums = [1,4,5,1]  -> 1\nnums = [1,2,3,4]  -> 3\nnums = [2,3,3,2]  -> 0</pre><p>In the first example merge 4 and 5 to get <code>[1,9,1]</code>.</p>",
    constraints=["1 &le; nums.length &le; 10,000", "1 &le; nums[i] &le; 10,000"],
    hints=["Compare the two ends. What can you say when they are equal?",
           "If the left end is smaller than the right end, the left end can never match unless it grows. The only way to grow it is to merge it with its right neighbour. Doing that now never hurts.",
           "Use two pointers with the current end sums <code>a</code> and <code>b</code>. If <code>a == b</code> move both pointers inward; if <code>a &lt; b</code> absorb the next element on the left (one operation); otherwise absorb the next element on the right."],
    editorial=["The final array corresponds to cutting the original into contiguous blocks whose sums read as a palindrome, and the number of operations is <code>n</code> minus the number of blocks. Build the blocks from both ends at once. If the left block sum equals the right block sum, close both blocks and continue inside. If the left sum is smaller, no block ending earlier on the right can match it, so the left block must absorb its right neighbour, costing one operation; symmetrically on the right.",
               "This forced choice is why the greedy is optimal: a smaller side has no alternative. When the pointers meet, whatever is left forms the middle block. One pass, O(n) time, O(1) space."],
    time="O(n)", space="O(1)",
    solution='''def minMergesForPalindrome(nums):
    i, j = 0, len(nums) - 1
    a, b = nums[i], nums[j]
    ops = 0
    while i < j:
        if a == b:
            i += 1
            j -= 1
            if i < j:
                a, b = nums[i], nums[j]
        elif a < b:
            i += 1
            a += nums[i]
            ops += 1
        else:
            j -= 1
            b += nums[j]
            ops += 1
    return ops
''',
    tests=[[[1, 4, 5, 1]], [[1, 2, 3, 4]], [[2, 3, 3, 2]], [[5]], [[1, 2]], [[3, 3]], [[4, 3, 2, 1, 2, 3, 1]],
           [[1, 1, 1, 1, 1]], [[10, 1, 1, 8]], [[1, 2, 3, 6]], [[7, 1, 2, 3, 1, 1, 7]]],
)
_r = rnd(4407)


def _split_palindrome(r, n_target, vmax):
    # random palindrome of block sums, each block then cut into pieces of positive values
    out = []
    half = []
    while len(out) < n_target:
        v = r.randint(2, vmax)
        half.append(v)
        out += _cut(r, v)
    blocks = half + half[::-1]
    res = []
    for v in blocks:
        res += _cut(r, v)
    return res


def _cut(r, v):
    parts = []
    while v > 0:
        x = r.randint(1, min(v, 3))
        parts.append(x)
        v -= x
    return parts


_a = _split_palindrome(_r, 2400, 6)
p["tests"].append([_a[:6000]])
p["tests"].append([[_r.randint(1, 10) for _ in range(5000)]])
p["tests"].append([[1] * 4000 + [2] + [1] * 4000])
p["tests"].append([list(range(1, 101)) * 40])


def b_merge_pal(nums):
    n = len(nums)
    best = None
    for mask in range(1 << (n - 1)):
        sums = []
        cur = nums[0]
        for i in range(1, n):
            if (mask >> (i - 1)) & 1:
                sums.append(cur)
                cur = nums[i]
            else:
                cur += nums[i]
        sums.append(cur)
        if sums == sums[::-1]:
            ops = n - len(sums)
            if best is None or ops < best:
                best = ops
    return best


def g_merge_pal(r):
    return [[r.randint(1, r.choice([2, 3, 5])) for _ in range(r.randint(1, 9))]]


def v_merge_pal(tests):
    for t in tests:
        a = t["args"][0]
        assert 1 <= len(a) <= 10000 and all(1 <= x <= 10000 for x in a)


CHECKS["min-merges-to-palindrome-array"] = (b_merge_pal, g_merge_pal, "exact")
VALIDATE["min-merges-to-palindrome-array"] = v_merge_pal


# ---------------------------------------------------------------- HARD

p = add(
    id="circular-candy-distribution", title="Candy in a Circle", diff="Hard", topic="Greedy", tier="extra",
    fn="candyCircle", params=[("ratings", "int[]")], ret="int", cmp="exact",
    desc="<p>Children sit around a round table, so child <code>0</code> is a neighbour of child <code>n - 1</code>. Child <code>i</code> has rating <code>ratings[i]</code>. Every child gets at least one candy, and a child with a strictly higher rating than a neighbour (on either side) must get strictly more candies than that neighbour. Equal ratings impose nothing.</p><p>Return the minimum total number of candies. With one child the answer is 1; with two children each is the other's only neighbour.</p><pre>ratings = [3,1,2]    -> 6\nratings = [2,2,2]    -> 3\nratings = [1,5,2,4]  -> 6</pre><p>In the first example the child rated 3 is above both the child rated 2 (wrapping around) and the child rated 1, so the candies are 3, 1, 2 in that order.</p>",
    constraints=["1 &le; ratings.length &le; 10,000", "0 &le; ratings[i] &le; 20,000"],
    hints=["On a line you can use a left pass and a right pass. On a circle there is no natural start, so the passes would need to run around forever. Is there a child whose candy count you can fix in advance?",
           "A child with the globally smallest rating is never strictly above a neighbour, so one candy is enough for them.",
           "Rotate the array so that a minimum-rating child is first. Run the left-to-right pass, then the right-to-left pass; in the second pass the last child's right neighbour is the first child (who keeps 1 candy). Sum the results."],
    editorial=["The constraints form a directed graph: an edge from every child to each strictly lower neighbour. The minimum candies of a child is 1 plus the maximum candies among the lower neighbours (the longest descending chain). On a line the two sweeps compute that; on a circle the chains could wrap, but a globally minimal child has no lower neighbour, so every descending chain ends there at the latest.",
               "Rotate the circle to start at a minimum-rating child (candy 1 there, and it is not changed by any pass). Left-to-right: raise a child above its left neighbour if its rating is higher. Right-to-left: raise a child above its right neighbour (for the last child that neighbour is the first child). Each child ends with the longest chain length, which is the minimum. O(n) time."],
    time="O(n)", space="O(n)",
    solution='''def candyCircle(ratings):
    n = len(ratings)
    m = ratings.index(min(ratings))
    b = ratings[m:] + ratings[:m]
    c = [1] * n
    for i in range(1, n):
        if b[i] > b[i - 1]:
            c[i] = c[i - 1] + 1
    for i in range(n - 1, -1, -1):
        nxt = (i + 1) % n
        if b[i] > b[nxt] and c[i] <= c[nxt]:
            c[i] = c[nxt] + 1
    return sum(c)
''',
    tests=[[[3, 1, 2]], [[2, 2, 2]], [[1, 5, 2, 4]], [[9]], [[1, 2]], [[4, 4]], [[1, 2, 3, 4, 5]], [[5, 4, 3, 2, 1]],
           [[4, 1, 1, 4]], [[0, 20000, 0, 20000, 0, 20000]], [[3, 4, 5, 1, 2, 3, 3, 0]], [[2, 1, 2, 1, 2]]],
)
_r = rnd(4408)
p["tests"].append([[_r.randint(0, 20000) for _ in range(6000)]])
p["tests"].append([list(range(3000, 6000)) + list(range(0, 3000))])
p["tests"].append([[(i * 7) % 4 for i in range(7000)]])
p["tests"].append([list(range(5000, 0, -1)) + list(range(1, 5000))])


def b_candy_circle(ratings):
    n = len(ratings)
    c = [1] * n
    changed = True
    while changed:
        changed = False
        for i in range(n):
            for j in ((i - 1) % n, (i + 1) % n):
                if ratings[i] > ratings[j] and c[i] <= c[j]:
                    c[i] = c[j] + 1
                    changed = True
    return sum(c)


def g_candy_circle(r):
    return [[r.randint(0, r.choice([2, 4, 8])) for _ in range(r.randint(1, 10))]]


def v_candy_circle(tests):
    for t in tests:
        a = t["args"][0]
        assert 1 <= len(a) <= 10000 and all(0 <= x <= 20000 for x in a)


CHECKS["circular-candy-distribution"] = (b_candy_circle, g_candy_circle, "exact")
VALIDATE["circular-candy-distribution"] = v_candy_circle


p = add(
    id="min-rounds-to-balance-machines", title="Balance the Machines", diff="Hard", topic="Greedy", tier="extra",
    fn="minRoundsToBalance", params=[("machines", "int[]")], ret="int", cmp="exact",
    desc="<p>There are <code>n</code> machines in a row; machine <code>i</code> holds <code>machines[i]</code> items. The work proceeds in rounds. In each round you may choose any number of machines, and every chosen machine passes <strong>one</strong> of the items it held at the <em>start</em> of the round to one adjacent machine (left or right, your choice per machine). All passes of a round happen at the same time, so an item that has just arrived cannot be passed on in the same round.</p><p>Return the minimum number of rounds after which all machines hold the same number of items, or <code>-1</code> if that cannot be done.</p><pre>machines = [1,0,5]  -> 3\nmachines = [0,3,0]  -> 2\nmachines = [0,2,0]  -> -1</pre>",
    constraints=["1 &le; machines.length &le; 5,000", "0 &le; machines[i] &le; 100,000"],
    hints=["Equal loads need a total divisible by <code>n</code>. Then every machine has a known target.",
           "Fix a machine <code>i</code>. Items have to cross it from the left part to the right part or the other way round. Count how many the left side and the right side are off from their targets.",
           "A machine passes at most one item per round. If both sides lack items, machine <code>i</code> must send out <code>|L| + |R|</code> items in total, one per round. Otherwise the larger of the two imbalances is the bottleneck. The answer is the maximum over all machines."],
    editorial=["Let <code>avg = total / n</code> (answer -1 if not divisible). For machine <code>i</code> let <code>L</code> be (items on its left) minus (<code>i * avg</code>), and <code>R</code> be (items on its right) minus (<code>(n - 1 - i) * avg</code>). A negative value means that side is short of items and needs them to flow in.",
               "If both <code>L &lt; 0</code> and <code>R &lt; 0</code>, machine <code>i</code> alone has to supply both sides and, as it can emit only one item per round, needs at least <code>-L - R</code> rounds. In every other case the flow across each boundary needs at least <code>|L|</code> and <code>|R|</code> rounds, since one item crosses a boundary per round. Each of these is a lower bound and the largest bound over all machines is attainable, so the answer is <code>max(...)</code> over <code>i</code>. One pass with running sums, O(n)."],
    time="O(n)", space="O(1)",
    solution='''def minRoundsToBalance(machines):
    n = len(machines)
    total = sum(machines)
    if total % n:
        return -1
    avg = total // n
    left = 0
    ans = 0
    for i, x in enumerate(machines):
        right = total - left - x
        l = left - i * avg
        r = right - (n - 1 - i) * avg
        if l < 0 and r < 0:
            need = -l - r
        else:
            need = max(abs(l), abs(r))
        ans = max(ans, need)
        left += x
    return ans
''',
    tests=[[[1, 0, 5]], [[0, 3, 0]], [[0, 2, 0]], [[0]], [[5]], [[2, 2, 2]], [[4, 0]], [[0, 0, 6]], [[6, 0, 0]],
           [[1, 1, 1, 9]], [[0, 0, 11, 5]], [[3, 0, 0, 0, 3]]],
)
_r = rnd(4409)
p["tests"].append([[100000] + [0] * 4999])
p["tests"].append([_shuffled_level(_r, 5000, 20, 80000)])
p["tests"].append([[0] * 2000 + [30000] * 1 + [0] * 1000 + [70000] + [0] * 1998])
p["tests"].append([_shuffled_level(_r, 4000, 3, 30000)])


def b_machines(machines):
    n, total = len(machines), sum(machines)
    if total % n:
        return -1
    goal = tuple([total // n] * n)
    start = tuple(machines)
    seen = {start}
    frontier = [start]
    rounds = 0
    while frontier:
        if goal in seen:
            return rounds
        nxt = []
        for s in frontier:
            opts = []
            for i in range(n):
                o = [0]
                if s[i] > 0:
                    if i > 0:
                        o.append(-1)
                    if i < n - 1:
                        o.append(1)
                opts.append(o)
            for choice in product(*opts):
                t = list(s)
                for i, d in enumerate(choice):
                    if d:
                        t[i] -= 1
                        t[i + d] += 1
                t = tuple(t)
                if t not in seen:
                    seen.add(t)
                    nxt.append(t)
        frontier = nxt
        rounds += 1
    return -1


def g_machines(r):
    n = r.randint(1, 4)
    if r.random() < 0.75:
        avg = r.randint(0, 2)
        a = [0] * n
        for _ in range(avg * n):
            a[r.randrange(n)] += 1
        return [a]
    return [[r.randint(0, 3) for _ in range(n)]]


def v_machines(tests):
    for t in tests:
        a = t["args"][0]
        assert 1 <= len(a) <= 5000 and all(0 <= x <= 100000 for x in a)


CHECKS["min-rounds-to-balance-machines"] = (b_machines, g_machines, "exact")
VALIDATE["min-rounds-to-balance-machines"] = v_machines


p = add(
    id="max-building-height-with-limits", title="Tallest Building Under Limits", diff="Hard", topic="Greedy", tier="extra",
    fn="maxBuildingHeight", params=[("n", "int"), ("limits", "int[][]")], ret="int", cmp="exact",
    desc="<p>A street has <code>n</code> buildings in a row, numbered <code>1</code> to <code>n</code>. Each height is a non-negative integer. Building 1 must have height 0, and the heights of two neighbouring buildings differ by <strong>at most 1</strong>.</p><p>In addition, <code>limits[i] = [id, cap]</code> says that building <code>id</code> may be at most <code>cap</code> tall. The ids are distinct and listed in arbitrary order, and no limit mentions building 1.</p><p>Return the largest height that any building can have.</p><pre>n = 5, limits = [[2,1],[4,1]]  -> 2\nn = 6, limits = []             -> 5\nn = 10, limits = [[5,3],[2,5],[7,4],[10,3]] -> 5</pre>",
    constraints=["2 &le; n &le; 10<sup>9</sup>", "0 &le; limits.length &le; min(n - 1, 2,000)", "2 &le; id &le; n, ids are distinct", "0 &le; cap &le; 10<sup>9</sup>"],
    hints=["A limit on one building indirectly limits its neighbours too, because heights can change by at most 1 per step. Limits can be tightened before you search for a peak.",
           "Sort the limits by position, include building 1 with limit 0, and tighten with a left-to-right pass (cap[i] &le; cap[i-1] + distance) and then a right-to-left pass.",
           "After tightening, between two consecutive limited buildings at distance <code>d</code> with caps <code>h1</code> and <code>h2</code> the best peak is <code>(h1 + h2 + d) // 2</code>. After the last limited building the height can keep rising by 1 per building until building <code>n</code>."],
    editorial=["Sort the restrictions by position and add the fixed building 1 with limit 0. A limit effectively propagates: if building <code>a</code> has cap <code>c</code>, building <code>b</code> can be at most <code>c + |b - a|</code>. A forward sweep applies this from left neighbours, a backward sweep from right neighbours; after both, every cap equals the true maximum height of that building and consecutive caps differ by at most the distance between them.",
               "Between two consecutive limited buildings at positions <code>x1 &lt; x2</code> with tightened caps <code>h1</code>, <code>h2</code>, the tallest possible building is the tent that climbs from both sides: height <code>(h1 + h2 + (x2 - x1)) // 2</code>. Beyond the last limit the height climbs by 1 per building: <code>h + n - x</code>. The answer is the maximum of all these values. Sorting dominates: O(m log m), independent of n."],
    time="O(m log m)", space="O(m)",
    solution='''def maxBuildingHeight(n, limits):
    pts = sorted([[1, 0]] + [list(x) for x in limits])
    m = len(pts)
    for i in range(1, m):
        pts[i][1] = min(pts[i][1], pts[i - 1][1] + pts[i][0] - pts[i - 1][0])
    for i in range(m - 2, -1, -1):
        pts[i][1] = min(pts[i][1], pts[i + 1][1] + pts[i + 1][0] - pts[i][0])
    best = 0
    for i in range(m - 1):
        x1, h1 = pts[i]
        x2, h2 = pts[i + 1]
        best = max(best, (h1 + h2 + x2 - x1) // 2)
    best = max(best, pts[-1][1] + n - pts[-1][0])
    return best
''',
    tests=[[5, [[2, 1], [4, 1]]], [6, []], [10, [[5, 3], [2, 5], [7, 4], [10, 3]]], [2, []], [2, [[2, 0]]],
           [10, [[10, 0]]], [10, [[3, 0], [8, 0]]], [9, [[5, 100]]], [20, [[6, 2], [11, 7], [20, 1]]],
           [10 ** 9, []], [10 ** 9, [[10 ** 9, 0]]], [10 ** 9, [[500000000, 10 ** 9]]]],
)
_r = rnd(4410)
for _n, _m, _cmax in ((10 ** 9, 1500, 10 ** 9), (20000, 2000, 300), (10 ** 9, 1000, 5000000)):
    _ids = sorted(_r.sample(range(2, _n + 1), _m)) if _n < 10 ** 6 else sorted({_r.randint(2, _n) for _ in range(_m)})
    _lim = [[i, _r.randint(0, _cmax)] for i in _ids]
    _r.shuffle(_lim)
    p["tests"].append([_n, _lim])


def b_buildings(n, limits):
    cap = [None] * (n + 1)
    for i, c in limits:
        cap[i] = c
    best = 0

    def go(i, h, peak):
        nonlocal best
        if i == n:
            best = max(best, peak)
            return
        for nh in (h - 1, h, h + 1):
            if nh >= 0 and (cap[i + 1] is None or nh <= cap[i + 1]):
                go(i + 1, nh, max(peak, nh))

    go(1, 0, 0)
    return best


def g_buildings(r):
    n = r.randint(2, 9)
    ids = r.sample(range(2, n + 1), r.randint(0, n - 1))
    return [n, [[i, r.randint(0, 6)] for i in ids]]


def v_buildings(tests):
    for t in tests:
        n, lim = t["args"]
        assert 2 <= n <= 10 ** 9 and len(lim) <= min(n - 1, 2000)
        assert len({i for i, _ in lim}) == len(lim)
        assert all(2 <= i <= n and 0 <= c <= 10 ** 9 for i, c in lim)


CHECKS["max-building-height-with-limits"] = (b_buildings, g_buildings, "exact")
VALIDATE["max-building-height-with-limits"] = v_buildings
