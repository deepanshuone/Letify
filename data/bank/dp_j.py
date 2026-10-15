"""Problems: Dynamic Programming on cost grids (falling paths, toll grids, triangles, round trips). See data/lib.py for the registry."""
from itertools import combinations

from lib import add, rnd, CHECKS, VALIDATE, gen_arr  # noqa: F401

TOPIC = "Dynamic Programming"
MOD = 10 ** 9 + 7


def _grid(r, h, w, lo, hi):
    return [[r.randint(lo, hi) for _ in range(w)] for _ in range(h)]


def _is_rect(g):
    return len(g) > 0 and len(g[0]) > 0 and all(len(row) == len(g[0]) for row in g)


def _paths(h, w):
    """Every right/down route from (0,0) to (h-1,w-1) as a list of cells (used by brute forces only)."""
    out = []
    steps = h + w - 2
    for downs in combinations(range(steps), h - 1):
        ds = set(downs)
        r = c = 0
        cells = [(0, 0)]
        for s in range(steps):
            if s in ds:
                r += 1
            else:
                c += 1
            cells.append((r, c))
        out.append(cells)
    return out


# ================================================================ EASY

# ---------------------------------------------------------------- min-falling-path-sum
p = add(
    id="min-falling-path-sum", title="Minimum Falling Path Sum", diff="Easy", topic=TOPIC,
    fn="minFallingPathSum", params=[("matrix", "int[][]")], ret="int", cmp="exact",
    desc="<p>A marble is dropped onto the <code>matrix</code> at any cell of the top row. In every step it falls to the next row, landing either directly below its current cell or in one of the two cells diagonally below it (one column to the left or one column to the right, as long as that column exists).</p><p>The marble collects the value of every cell it touches, including the first and the last one. Return the smallest total it can collect on its way from the top row to the bottom row. Values may be negative.</p>",
    constraints=["1 &le; matrix.length, matrix[0].length &le; 60", "-100 &le; matrix[i][j] &le; 100"],
    hints=["Trying every start column and every sequence of moves is exponential: there are up to three choices in each of the rows. Many routes share their ending, so look for repeated work.",
           "Let <code>best[r][c]</code> be the smallest total of a fall that ends in cell <code>(r, c)</code>. Which cells of row <code>r - 1</code> can the marble have come from?",
           "<code>best[r][c] = matrix[r][c] + min(best[r-1][c-1], best[r-1][c], best[r-1][c+1])</code>, ignoring neighbours outside the matrix. Row 0 is just a copy of the matrix; the answer is the minimum of the last row, and one previous row is all you need to remember."],
    editorial=["Every fall into cell <code>(r, c)</code> comes from one of at most three cells in the row above, and the part of the fall before that cell has to be optimal for the cell it ends in, otherwise swapping in a cheaper prefix would improve the whole fall. So <code>best[r][c] = matrix[r][c] + min</code> over the existing cells among <code>(r-1, c-1)</code>, <code>(r-1, c)</code> and <code>(r-1, c+1)</code>.",
               "The first row has no predecessors, so <code>best[0][c] = matrix[0][c]</code>. The marble may leave from any cell of the last row, so the answer is the minimum over that row. Each row only needs the previous one, giving O(m &middot; n) time and O(n) extra space. Take care that the neighbour window is clamped at the borders; do not wrap around."],
    time="O(m &middot; n)", space="O(n)",
    solution='''def minFallingPathSum(matrix):
    n = len(matrix[0])
    prev = matrix[0][:]
    for row in matrix[1:]:
        cur = []
        for c in range(n):
            lo = c - 1 if c > 0 else 0
            cur.append(row[c] + min(prev[lo:c + 2]))
        prev = cur
    return min(prev)
''',
    tests=[[[[2, 1, 3], [6, 5, 4], [7, 8, 9]]], [[[-19, 57], [-40, -5]]], [[[5]]],
           [[[-7]]], [[[4, -2, 9, 1]]], [[[3], [-4], [8]]], [[[1, 2], [3, 4], [5, 6], [7, 8]]],
           [[[100, 100, 100], [100, 100, 100]]], [[[-100, -100], [-100, -100], [-100, -100]]],
           [[[1, 9, 9, 9, 1], [9, 9, 9, 9, 9], [9, 1, 9, 1, 9], [9, 9, 9, 9, 9]]],
           [[[5, 1, 9], [1, 9, 9], [9, 9, 9], [1, 9, 9]]], [[[0, 0, 0], [0, 0, 0]]]],
)
_r = rnd(11001)
p["tests"].append([_grid(_r, 60, 60, -100, 100)])
p["tests"].append([_grid(_r, 60, 60, 0, 100)])
p["tests"].append([_grid(_r, 60, 3, -100, 100)])
p["tests"].append([_grid(_r, 7, 60, -100, 100)])


def b_mfps(matrix):
    h, w = len(matrix), len(matrix[0])

    def go(r, c):
        if r == h - 1:
            return matrix[r][c]
        return matrix[r][c] + min(go(r + 1, c2) for c2 in (c - 1, c, c + 1) if 0 <= c2 < w)
    return min(go(0, c) for c in range(w))


def v_mfps(tests):
    for t in tests:
        g = t["args"][0]
        assert _is_rect(g) and len(g) <= 60 and len(g[0]) <= 60
        assert all(-100 <= v <= 100 for row in g for v in row)
        assert -100 * len(g) <= t["expected"] <= 100 * len(g)


CHECKS["min-falling-path-sum"] = (b_mfps, lambda r: [_grid(r, r.randint(1, 5), r.randint(1, 5), -9, 9)], "exact")
VALIDATE["min-falling-path-sum"] = v_mfps


# ---------------------------------------------------------------- max-coins-around-walls
p = add(
    id="max-coins-around-walls", title="Richest Walk Around Walls", diff="Easy", topic=TOPIC, tier="extra",
    fn="maxCoinsAroundWalls", params=[("grid", "int[][]")], ret="int", cmp="exact",
    desc="<p>Each cell of the rectangular <code>grid</code> is either a wall, written <code>-1</code>, or a free cell holding that many coins (<code>0</code> or more). A walker starts in the top-left cell and wants to reach the bottom-right cell, moving only one step <strong>right</strong> or one step <strong>down</strong> and never stepping onto a wall. The walker picks up the coins of every cell it stands on, including the first and the last one.</p><p>Return the largest number of coins that can be collected on a valid walk, or <code>-1</code> if the bottom-right cell cannot be reached at all (this includes the case where the start or the destination is a wall).</p>",
    constraints=["1 &le; grid.length, grid[0].length &le; 60", "grid[i][j] = -1 (wall) or 0 &le; grid[i][j] &le; 100 (coins)"],
    hints=["Without walls this is a plain maximum path sum: the best walk into a cell extends the better of two neighbouring walks. What changes when a neighbour is a wall or unreachable?",
           "Let <code>best[r][c]</code> be the most coins on a valid walk ending at <code>(r, c)</code>, with <code>-1</code> meaning that no valid walk ends there. Coins are never negative, so <code>-1</code> can never be mistaken for a real total.",
           "For a free cell, take <code>m = max(best[r-1][c], best[r][c-1])</code> (missing neighbours count as <code>-1</code>). If <code>m</code> is still <code>-1</code> the cell is unreachable, otherwise <code>best[r][c] = m + grid[r][c]</code>. The start cell is seeded with its own coins."],
    editorial=["The structure is the familiar right/down grid DP, with one extra state: unreachable. A cell can be entered from above or from the left; the better of those two walks should be extended. Walls are simply never entered, so their <code>best</code> value is forced to <code>-1</code>, and a free cell whose two predecessors are both <code>-1</code> becomes <code>-1</code> as well.",
               "Because every real total is at least 0, the value <code>-1</code> is a safe marker, and a maximum over predecessors naturally prefers any real walk to a missing one. Using a single array that is updated row by row gives O(m &middot; n) time and O(n) space. The answer is the last cell's value, which is already <code>-1</code> when the destination is a wall or unreachable."],
    time="O(m &middot; n)", space="O(n)",
    solution='''def maxCoinsAroundWalls(grid):
    n = len(grid[0])
    best = [-1] * n
    for r, row in enumerate(grid):
        for c in range(n):
            if row[c] == -1:
                best[c] = -1
                continue
            if r == 0 and c == 0:
                best[c] = row[c]
                continue
            m = best[c]
            if c > 0 and best[c - 1] > m:
                m = best[c - 1]
            best[c] = m + row[c] if m >= 0 else -1
    return best[-1]
''',
    tests=[[[[0, 2, 0], [3, -1, 4], [1, 5, 6]]], [[[1, -1], [-1, 1]]], [[[7]]],
           [[[-1]]], [[[0]]], [[[4, 3, 2, 1]]], [[[4], [-1], [2]]], [[[0, 0], [0, -1]]], [[[-1, 5], [5, 5]]],
           [[[5, 0, 0, 7], [-1, -1, -1, 0], [9, 9, 9, 9]]], [[[1, 2, 3], [-1, -1, 4], [9, 9, 5]]],
           [[[3, -1, 8, 2], [4, 0, -1, 1], [-1, 6, 7, -1], [2, 2, 2, 2]]]],
)
_r = rnd(11002)


def _walls(r, h, w, pw, hi):
    g = [[(-1 if r.random() < pw else r.randint(0, hi)) for _ in range(w)] for _ in range(h)]
    g[0][0] = r.randint(0, hi)
    g[h - 1][w - 1] = r.randint(0, hi)
    return g


p["tests"].append([_walls(_r, 60, 60, 0.15, 100)])
p["tests"].append([_walls(_r, 60, 60, 0.0, 100)])
p["tests"].append([_walls(_r, 60, 45, 0.3, 100)])
p["tests"].append([_walls(_r, 50, 60, 0.45, 100)])
_g = _grid(_r, 60, 60, 0, 100)
for _i in range(60):
    _g[_i][59 - _i] = -1 if _i not in (0, 59) else _g[_i][59 - _i]
_g[0][59] = -1
p["tests"].append([_g])


def b_mcw(grid):
    h, w = len(grid), len(grid[0])

    def go(r, c):
        if r >= h or c >= w or grid[r][c] == -1:
            return None
        if r == h - 1 and c == w - 1:
            return grid[r][c]
        opts = [x for x in (go(r + 1, c), go(r, c + 1)) if x is not None]
        return grid[r][c] + max(opts) if opts else None
    res = go(0, 0)
    return -1 if res is None else res


def g_mcw(r):
    h, w = r.randint(1, 5), r.randint(1, 5)
    return [[(-1 if r.random() < r.choice([0.0, 0.2, 0.4]) else r.randint(0, 9)) for _ in range(w)] for _ in range(h)]


def v_mcw(tests):
    for t in tests:
        g = t["args"][0]
        assert _is_rect(g) and len(g) <= 60 and len(g[0]) <= 60
        assert all(v == -1 or 0 <= v <= 100 for row in g for v in row)
        assert t["expected"] >= -1
    outs = [t["expected"] for t in tests]
    assert -1 in outs and any(o > 0 for o in outs)


CHECKS["max-coins-around-walls"] = (b_mcw, lambda r: [g_mcw(r)], "exact")
VALIDATE["max-coins-around-walls"] = v_mcw


# ================================================================ MEDIUM

# ---------------------------------------------------------------- count-cheapest-grid-routes
p = add(
    id="count-cheapest-grid-routes", title="Count the Cheapest Grid Routes", diff="Medium", topic=TOPIC,
    fn="countCheapestRoutes", params=[("grid", "int[][]")], ret="int", cmp="exact",
    desc="<p>Every cell of the rectangular <code>grid</code> holds a non-negative toll. A route starts in the top-left cell, ends in the bottom-right cell and moves only one step <strong>right</strong> or one step <strong>down</strong> at a time. Its cost is the sum of the tolls of all cells on it, including the first and the last one.</p><p>Several routes may share the smallest possible cost. Return how many different routes have exactly that smallest cost, modulo <code>1,000,000,007</code>. Two routes are different if they visit different sequences of cells.</p>",
    constraints=["1 &le; grid.length, grid[0].length &le; 60", "0 &le; grid[i][j] &le; 9", "The result is taken modulo 1,000,000,007"],
    hints=["Computing only the cheapest cost is the standard minimum path sum. You need to know in how many ways that cost is reached, so store two numbers per cell.",
           "For each cell keep a pair: the cheapest cost <code>cost</code> to reach it and the number <code>ways</code> of reaching it at exactly that cost.",
           "Compare the pairs of the cell above and the cell to the left. The smaller cost wins and its <code>ways</code> is inherited; on a tie, add both <code>ways</code>. Then add the cell's own toll to the cost. Reduce <code>ways</code> modulo 1,000,000,007 as you go."],
    editorial=["A cheapest route to a cell is a cheapest route to one of its two predecessors followed by the cell itself: if the prefix was not optimal for the predecessor, a better prefix would give a cheaper route to the cell. So the cheapest cost satisfies <code>cost[r][c] = grid[r][c] + min(cost[r-1][c], cost[r][c-1])</code>, and the cheapest routes to the cell are exactly the cheapest routes to those predecessors whose cost equals that minimum.",
               "Therefore <code>ways[r][c]</code> is the sum of <code>ways</code> over the predecessors that attain the minimum: one of them when their costs differ, both when they tie. Tolls of 0 are allowed and cause many ties, which is why the count can grow quickly and is reported modulo 1,000,000,007. Note that costs themselves must be compared exactly, only the counts are reduced. Time O(m &middot; n), space O(n) with a rolling row."],
    time="O(m &middot; n)", space="O(n)",
    solution='''def countCheapestRoutes(grid):
    MOD = 10 ** 9 + 7
    INF = float("inf")
    n = len(grid[0])
    cost = [INF] * n
    ways = [0] * n
    for r, row in enumerate(grid):
        for c in range(n):
            if r == 0 and c == 0:
                cost[0] = row[0]
                ways[0] = 1
                continue
            bc, bw = INF, 0
            if r > 0:
                bc, bw = cost[c], ways[c]
            if c > 0:
                if cost[c - 1] < bc:
                    bc, bw = cost[c - 1], ways[c - 1]
                elif cost[c - 1] == bc:
                    bw += ways[c - 1]
            cost[c] = bc + row[c]
            ways[c] = bw % MOD
    return ways[-1] % MOD
''',
    tests=[[[[1, 1, 1], [1, 1, 1], [1, 1, 1]]], [[[0, 9], [9, 0]]], [[[5]]],
           [[[0]]], [[[1, 2, 3, 4]]], [[[1], [2], [3]]], [[[0, 0], [0, 0]]], [[[1, 3, 1], [1, 5, 1], [4, 2, 1]]],
           [[[0, 0, 0], [0, 0, 0], [0, 0, 0]]], [[[2, 1, 9], [1, 9, 1], [9, 1, 2]]],
           [[[9, 9, 9, 9], [9, 0, 0, 9], [9, 0, 0, 9], [9, 9, 9, 9]]], [[[0, 1, 0, 1], [1, 0, 1, 0], [0, 1, 0, 1]]]],
)
_r = rnd(11003)
p["tests"].append([[[0] * 60 for _ in range(60)]])
p["tests"].append([_grid(_r, 60, 60, 0, 1)])
p["tests"].append([_grid(_r, 60, 60, 0, 9)])
p["tests"].append([_grid(_r, 45, 60, 0, 2)])


def b_ccr(grid):
    h, w = len(grid), len(grid[0])
    costs = [sum(grid[r][c] for r, c in cells) for cells in _paths(h, w)]
    m = min(costs)
    return costs.count(m) % MOD


def v_ccr(tests):
    for t in tests:
        g = t["args"][0]
        assert _is_rect(g) and len(g) <= 60 and len(g[0]) <= 60
        assert all(0 <= v <= 9 for row in g for v in row)
        assert 1 <= t["expected"] < MOD


CHECKS["count-cheapest-grid-routes"] = (b_ccr, lambda r: [_grid(r, r.randint(1, 5), r.randint(1, 5), 0, r.choice([1, 2, 9]))], "exact")
VALIDATE["count-cheapest-grid-routes"] = v_ccr


# ---------------------------------------------------------------- max-nonneg-product-grid-path
p = add(
    id="max-nonneg-product-grid-path", title="Largest Non-Negative Product Route", diff="Medium", topic=TOPIC,
    fn="maxNonNegProductRoute", params=[("grid", "int[][]")], ret="int", cmp="exact",
    desc="<p>The rectangular <code>grid</code> holds small integers, possibly negative or zero. A route starts in the top-left cell, ends in the bottom-right cell and moves only <strong>right</strong> or <strong>down</strong>. The <em>score</em> of a route is the product of all values on it, including the first and the last cell.</p><p>Among all routes whose score is <strong>non-negative</strong> (zero counts), find the largest score and return it modulo <code>1,000,000,007</code>. If every route has a negative score, return <code>-1</code>. Note that the comparison between routes uses the true product, not the remainder.</p>",
    constraints=["1 &le; grid.length, grid[0].length &le; 40", "-9 &le; grid[i][j] &le; 9", "The maximum is compared exactly; only the value that is returned is reduced modulo 1,000,000,007"],
    hints=["A single best product per cell is not enough: a very negative product multiplied by a negative number becomes a very large positive one.",
           "For every cell keep both the largest and the smallest product of a route ending there. These two numbers are enough to know every extreme that can come out of the next multiplication.",
           "For cell value <code>v</code>, collect <code>v * mx</code> and <code>v * mn</code> of the cell above and of the cell to the left; the new maximum and minimum are the max and min of these four candidates. At the end, if the maximum is negative return -1, else return it modulo 1,000,000,007. Python integers will not overflow, so take the modulo only at the very end."],
    editorial=["Multiplying by a positive value preserves order, multiplying by a negative value reverses it, and multiplying by zero collapses everything to zero. Consequently the largest product of a route into a cell can come from the largest <em>or</em> the smallest product of a route into one of its two predecessors, depending on the sign of the cell. Tracking <code>mx</code> and <code>mn</code> for every cell captures both possibilities.",
               "The recurrence is: candidates = the products of the cell value with <code>mx</code> and <code>mn</code> of the upper and left cells; <code>mx</code> is the largest candidate and <code>mn</code> the smallest. The remainder must not be applied while comparing, because remainders do not preserve order; with grids of at most 40 x 40 and values up to 9 the exact products have only a few hundred bits, which big integers handle easily. If the final <code>mx</code> is negative every route is negative and the answer is -1, otherwise it is <code>mx</code> modulo 1,000,000,007. Time O(m &middot; n), space O(n) numbers."],
    time="O(m &middot; n)", space="O(n)",
    solution='''def maxNonNegProductRoute(grid):
    MOD = 10 ** 9 + 7
    n = len(grid[0])
    mx = [0] * n
    mn = [0] * n
    for r, row in enumerate(grid):
        for c in range(n):
            v = row[c]
            if r == 0 and c == 0:
                mx[0] = mn[0] = v
                continue
            cand = []
            if r > 0:
                cand.append(mx[c] * v)
                cand.append(mn[c] * v)
            if c > 0:
                cand.append(mx[c - 1] * v)
                cand.append(mn[c - 1] * v)
            mx[c] = max(cand)
            mn[c] = min(cand)
    return -1 if mx[-1] < 0 else mx[-1] % MOD
''',
    tests=[[[[1, -2, 1], [1, -2, 1], [3, -4, 1]]], [[[-1, -2], [-3, 0]]], [[[-5]]],
           [[[0]]], [[[7]]], [[[-3, 2]]], [[[2], [-1], [-3]]], [[[-1, 0], [0, -1]]], [[[-1, -1], [-1, -1]]],
           [[[1, 4, 4, 0], [-2, 0, 0, 1], [1, -1, 1, 1]]], [[[-1, 2, 3], [4, -5, 6], [7, 8, -9]]],
           [[[9, 9, 9, 9], [9, -9, -9, 9], [9, 9, 9, 9]]], [[[2, -3, 0, 5], [-1, 4, -2, 3], [6, -7, 1, -8]]]],
)
_r = rnd(11004)
p["tests"].append([_grid(_r, 40, 40, -9, 9)])
p["tests"].append([[[(9 if (i + j) % 7 else -9) for j in range(40)] for i in range(40)]])
p["tests"].append([_grid(_r, 40, 40, 5, 9)])
p["tests"].append([_grid(_r, 25, 40, -9, 9)])


def b_mnp(grid):
    h, w = len(grid), len(grid[0])
    best = None
    for cells in _paths(h, w):
        prod = 1
        for r, c in cells:
            prod *= grid[r][c]
        if prod >= 0 and (best is None or prod > best):
            best = prod
    return -1 if best is None else best % MOD


def v_mnp(tests):
    for t in tests:
        g = t["args"][0]
        assert _is_rect(g) and len(g) <= 40 and len(g[0]) <= 40
        assert all(-9 <= v <= 9 for row in g for v in row)
        assert t["expected"] == -1 or 0 <= t["expected"] < MOD
    outs = [t["expected"] for t in tests]
    assert -1 in outs and 0 in outs and any(o > 0 for o in outs)


CHECKS["max-nonneg-product-grid-path"] = (b_mnp, lambda r: [_grid(r, r.randint(1, 4), r.randint(1, 5), -r.choice([2, 4, 9]), r.choice([2, 4, 9]))], "exact")
VALIDATE["max-nonneg-product-grid-path"] = v_mnp


# ---------------------------------------------------------------- min-path-sum-with-waivers
p = add(
    id="min-path-sum-with-waivers", title="Cheapest Route with Toll Waivers", diff="Medium", topic=TOPIC, tier="extra",
    fn="minPathSumWithWaivers", params=[("grid", "int[][]"), ("k", "int")], ret="int", cmp="exact",
    desc="<p>Each cell of the rectangular <code>grid</code> has a non-negative toll. You travel from the top-left cell to the bottom-right cell, moving only <strong>right</strong> or <strong>down</strong>, and normally pay the toll of every cell you stand on, including the first and the last one.</p><p>You also own <code>k</code> waiver tickets. A ticket can be used on any cell of your route to pay nothing for that cell; at most one ticket per cell, and you do not have to use them all. Return the smallest total toll that you can be charged.</p>",
    constraints=["1 &le; grid.length, grid[0].length &le; 50", "0 &le; grid[i][j] &le; 100", "0 &le; k &le; 10"],
    hints=["Without tickets this is the plain minimum path sum. A ticket is a limited resource, so the best choice at a cell depends on how many tickets are still left.",
           "Add a dimension: <code>f[j][r][c]</code> is the cheapest cost of reaching <code>(r, c)</code> having used exactly <code>j</code> tickets so far.",
           "Entering cell <code>(r, c)</code> from a neighbour, either pay <code>grid[r][c]</code> and keep <code>j</code>, or waive it and come from the neighbour's state <code>j - 1</code>. Take the minimum over both options and both neighbours; the answer is the minimum over all <code>j</code> at the last cell."],
    editorial=["A route together with a choice of cells to waive is all that matters, and the waived cells will obviously be the most expensive ones on the route. That observation gives a quick brute force, but for a DP it is easier to decide cell by cell. Let <code>f[j][r][c]</code> be the cheapest total for a route that ends at <code>(r, c)</code> and has used exactly <code>j</code> waivers on its cells so far.",
               "To enter <code>(r, c)</code> with <code>j</code> waivers used, there are two options: pay for the cell and arrive with the same <code>j</code> from the upper or left neighbour, or waive it and arrive with <code>j - 1</code> from either neighbour at no extra cost. Using fewer than <code>k</code> tickets is allowed, so the result is the minimum of <code>f[j][m-1][n-1]</code> over <code>j</code> from 0 to <code>k</code>. This takes O(k &middot; m &middot; n) time and O(k &middot; n) space with a rolling row, which is tiny for k &le; 10."],
    time="O(k &middot; m &middot; n)", space="O(k &middot; n)",
    solution='''def minPathSumWithWaivers(grid, k):
    INF = float("inf")
    n = len(grid[0])
    prev = None
    for r, row in enumerate(grid):
        cur = [[INF] * n for _ in range(k + 1)]
        for c in range(n):
            v = row[c]
            for j in range(k + 1):
                if r == 0 and c == 0:
                    if j == 0:
                        cur[0][0] = v
                    elif j == 1:
                        cur[1][0] = 0
                    continue
                pay = INF
                if r > 0:
                    pay = prev[j][c]
                if c > 0 and cur[j][c - 1] < pay:
                    pay = cur[j][c - 1]
                best = pay + v
                if j > 0:
                    free = INF
                    if r > 0:
                        free = prev[j - 1][c]
                    if c > 0 and cur[j - 1][c - 1] < free:
                        free = cur[j - 1][c - 1]
                    if free < best:
                        best = free
                cur[j][c] = best
        prev = cur
    return min(prev[j][n - 1] for j in range(k + 1))
''',
    tests=[[[[1, 3, 1], [1, 5, 1], [4, 2, 1]], 1], [[[1, 3, 1], [1, 5, 1], [4, 2, 1]], 0], [[[7]], 1],
           [[[7]], 0], [[[5, 5, 5]], 2], [[[5], [5], [5]], 10], [[[9, 9], [9, 9]], 1], [[[100, 100], [100, 100]], 3],
           [[[0, 0], [0, 0]], 5], [[[2, 100, 2], [2, 100, 2], [2, 2, 2]], 2], [[[1, 50, 1, 50], [50, 1, 50, 1], [1, 50, 1, 50]], 3],
           [[[10, 1, 1, 1], [10, 90, 90, 1], [10, 90, 90, 1], [1, 1, 1, 1]], 1]],
)
_r = rnd(11005)
p["tests"].append([_grid(_r, 50, 50, 0, 100), 10])
p["tests"].append([_grid(_r, 50, 50, 0, 100), 4])
p["tests"].append([_grid(_r, 50, 50, 90, 100), 7])
p["tests"].append([_grid(_r, 30, 50, 0, 100), 0])


def b_mpw(grid, k):
    h, w = len(grid), len(grid[0])
    best = None
    for cells in _paths(h, w):
        vals = sorted((grid[r][c] for r, c in cells), reverse=True)
        total = sum(vals[k:])
        if best is None or total < best:
            best = total
    return best


def g_mpw(r):
    return [_grid(r, r.randint(1, 4), r.randint(1, 5), 0, r.choice([3, 9])), r.randint(0, 4)]


def v_mpw(tests):
    for t in tests:
        g, k = t["args"]
        assert _is_rect(g) and len(g) <= 50 and len(g[0]) <= 50
        assert all(0 <= v <= 100 for row in g for v in row)
        assert 0 <= k <= 10
        assert 0 <= t["expected"] <= 100 * (len(g) + len(g[0]) - 1)


CHECKS["min-path-sum-with-waivers"] = (b_mpw, g_mpw, "exact")
VALIDATE["min-path-sum-with-waivers"] = v_mpw


# ---------------------------------------------------------------- max-points-with-column-penalty
p = add(
    id="max-points-with-column-penalty", title="Spotlight Show with Move Penalty", diff="Medium", topic=TOPIC,
    fn="maxPointsWithPenalty", params=[("points", "int[][]")], ret="int", cmp="exact",
    desc="<p>A stage is a grid with one row per scene and one column per spotlight position. <code>points[r][c]</code> is the score earned when scene <code>r</code> is lit from position <code>c</code>.</p><p>You must choose exactly one position for every scene. Moving the spotlight between two consecutive scenes from position <code>a</code> to position <code>b</code> costs <code>|a - b|</code> points. The total is the sum of the chosen scores minus the sum of all moving costs. Return the largest total you can obtain.</p>",
    constraints=["1 &le; points.length, points[0].length &le; 60", "0 &le; points[r][c] &le; 100,000"],
    hints=["Choosing the best cell in every row greedily ignores the penalty. Let the decision for a row depend on where the previous row ended.",
           "Let <code>f[r][c]</code> be the best total of scenes <code>0..r</code> if scene <code>r</code> uses position <code>c</code>. Then <code>f[r][c] = points[r][c] + max over b of (f[r-1][b] - |b - c|)</code>. Evaluating that maximum for every <code>c</code> directly costs O(n<sup>2</sup>) per row.",
           "Split the absolute value. For positions <code>b &le; c</code> you need <code>max(f[r-1][b] + b) - c</code>, and for <code>b &ge; c</code> you need <code>max(f[r-1][b] - b) + c</code>. Both are running maxima: one left-to-right sweep and one right-to-left sweep per row, i.e. <code>left[c] = max(prev[c], left[c-1] - 1)</code> and the mirrored <code>right[c]</code>."],
    editorial=["The recurrence <code>f[r][c] = points[r][c] + max over b of (f[r-1][b] - |b - c|)</code> is correct but takes O(m &middot; n<sup>2</sup>) time. The maximum can be computed for all <code>c</code> at once because the penalty is linear in the distance: the best previous value seen from the left, discounted by one for every column travelled, is <code>left[c] = max(prev[c], left[c-1] - 1)</code>, and symmetrically <code>right[c] = max(prev[c], right[c+1] - 1)</code>.",
               "Then <code>f[r][c] = points[r][c] + max(left[c], right[c])</code>. Staying in the same column corresponds to the term <code>prev[c]</code> that both sweeps include. The answer is the maximum of the last row. The total time is O(m &middot; n) and the space O(n). The result is at most 60 &middot; 100,000, well within 32-bit range."],
    time="O(m &middot; n)", space="O(n)",
    solution='''def maxPointsWithPenalty(points):
    n = len(points[0])
    prev = points[0][:]
    for row in points[1:]:
        left = prev[:]
        for c in range(1, n):
            if left[c - 1] - 1 > left[c]:
                left[c] = left[c - 1] - 1
        right = prev[:]
        for c in range(n - 2, -1, -1):
            if right[c + 1] - 1 > right[c]:
                right[c] = right[c + 1] - 1
        prev = [row[c] + max(left[c], right[c]) for c in range(n)]
    return max(prev)
''',
    tests=[[[[1, 2, 3], [1, 5, 1], [3, 1, 1]]], [[[1, 5], [2, 3], [4, 2]]], [[[7, 3, 9]]],
           [[[4]]], [[[0]]], [[[1], [2], [3]]], [[[0, 0, 0], [0, 0, 0]]], [[[100000, 0, 0, 0, 0], [0, 0, 0, 0, 100000]]],
           [[[5, 0, 0, 0, 5], [0, 0, 9, 0, 0], [5, 0, 0, 0, 5]]], [[[1, 1, 1, 1], [1, 1, 1, 1], [1, 1, 1, 1]]],
           [[[10, 0], [0, 10], [10, 0], [0, 10]]], [[[3, 9, 2, 8, 1], [1, 2, 3, 4, 5], [9, 1, 9, 1, 9]]]],
)
_r = rnd(11006)
p["tests"].append([_grid(_r, 60, 60, 0, 100000)])
p["tests"].append([_grid(_r, 60, 60, 0, 5)])
p["tests"].append([_grid(_r, 60, 60, 99990, 100000)])
p["tests"].append([[[(100000 if (i + j) % 2 == 0 else 0) for j in range(60)] for i in range(40)]])


def b_mpp(points):
    h, w = len(points), len(points[0])

    def go(r, c):
        if r == h - 1:
            return points[r][c]
        return points[r][c] + max(go(r + 1, c2) - abs(c - c2) for c2 in range(w))
    return max(go(0, c) for c in range(w))


def v_mpp(tests):
    for t in tests:
        g = t["args"][0]
        assert _is_rect(g) and len(g) <= 60 and len(g[0]) <= 60
        assert all(0 <= v <= 100000 for row in g for v in row)
        assert 0 <= t["expected"] <= 100000 * len(g)


CHECKS["max-points-with-column-penalty"] = (b_mpp, lambda r: [_grid(r, r.randint(1, 4), r.randint(1, 5), 0, r.choice([3, 9]))], "exact")
VALIDATE["max-points-with-column-penalty"] = v_mpp


# ---------------------------------------------------------------- triangle-alternating-parity-max-path
p = add(
    id="triangle-alternating-parity-max-path", title="Triangle Descent with Alternating Parity", diff="Medium", topic=TOPIC, tier="extra",
    fn="maxAlternatingParityDescent", params=[("triangle", "int[][]")], ret="int", cmp="exact",
    desc="<p>A number triangle is given as a list of rows: row <code>i</code> has exactly <code>i + 1</code> positive integers. A descent starts at the single number in the top row and moves down one row at a time. From position <code>j</code> in row <code>i</code> it may go to position <code>j</code> or position <code>j + 1</code> in row <code>i + 1</code>.</p><p>A descent is <strong>valid</strong> only if any two consecutive numbers on it have different parity (one is even and the other is odd). Return the largest sum of a valid descent from the top row to the bottom row, or <code>-1</code> if no valid descent exists.</p>",
    constraints=["1 &le; triangle.length &le; 100", "triangle[i].length == i + 1", "1 &le; triangle[i][j] &le; 1000"],
    hints=["Without the parity rule this is the classic triangle maximum path. Which part of the state do you need to add to enforce the rule, and is that already part of the state?",
           "The parity of the current number is determined by the cell itself, so the cell position alone is enough. Define <code>down[i][j]</code> as the best valid sum from cell <code>(i, j)</code> to the bottom, or <code>-1</code> if there is none.",
           "Work from the bottom row up: the last row has <code>down = value</code>. For a cell, look only at the two children whose value has the opposite parity and whose <code>down</code> is not <code>-1</code>; take the larger one and add the cell's value. If no child qualifies, <code>down</code> is <code>-1</code>."],
    editorial=["The validity of a step depends only on the two numbers it connects, and both are known once the cell positions are known. So no extra dimension is needed: the sub-problem 'best valid descent from cell <code>(i, j)</code> to the bottom' is self-contained, because the rule for later steps depends only on the parity of cell <code>(i, j)</code>, which is fixed.",
               "Bottom-up: in the last row every cell is its own descent. For other cells <code>down[i][j] = value + max(down[child])</code>, where only children with the opposite parity and a valid descent are allowed. Since all numbers are positive, a real sum is never negative and <code>-1</code> is a safe marker for 'impossible'. If the top cell gets <code>-1</code> there is no valid descent at all (for example when all numbers have the same parity and the triangle has more than one row). Time O(n<sup>2</sup>), space O(n)."],
    time="O(n<sup>2</sup>)", space="O(n)",
    solution='''def maxAlternatingParityDescent(triangle):
    down = triangle[-1][:]
    for i in range(len(triangle) - 2, -1, -1):
        child = triangle[i + 1]
        new = []
        for j in range(i + 1):
            v = triangle[i][j]
            best = -1
            for k in (j, j + 1):
                if (child[k] - v) % 2 == 1 and down[k] > best:
                    best = down[k]
            new.append(v + best if best >= 0 else -1)
        down = new
    return down[0]
''',
    tests=[[[[3], [4, 7], [5, 2, 8], [6, 9, 10, 1]]], [[[1], [3, 5]]], [[[8]]],
           [[[1]]], [[[2], [3, 4]]], [[[1], [2, 4]]], [[[2], [4, 6], [8, 10, 12]]], [[[1], [2, 2], [1, 1, 1]]],
           [[[5], [6, 6], [5, 7, 5], [6, 6, 8, 6]]], [[[1000], [999, 998], [1000, 1, 2]]],
           [[[7], [2, 3], [5, 4, 9], [2, 1, 6, 7]]], [[[1], [1, 2], [3, 3, 4], [1, 5, 6, 7], [2, 2, 9, 9, 1]]]],
)
_r = rnd(11007)
p["tests"].append([[[_r.randint(1, 1000) for _ in range(i + 1)] for i in range(100)]])
p["tests"].append([[[_r.choice([1, 3, 5, 999]) for _ in range(i + 1)] for i in range(100)]])
p["tests"].append([[[_r.randint(1, 1000) for _ in range(i + 1)] for i in range(77)]])


def _zigzag_tri(r, n):
    path = [0]
    for _ in range(n - 1):
        path.append(path[-1] + r.randint(0, 1))
    tri = []
    for i in range(n):
        row = [r.choice([1, 3, 5, 997, 999]) for _ in range(i + 1)]
        if i % 2 == 1:
            row[path[i]] = r.choice([2, 4, 1000])
        tri.append(row)
    return tri


p["tests"].append([_zigzag_tri(_r, 100)])


def b_tapm(triangle):
    n = len(triangle)

    def go(i, j):
        if i == n - 1:
            return triangle[i][j]
        best = -1
        for k in (j, j + 1):
            if (triangle[i + 1][k] - triangle[i][j]) % 2 == 1:
                x = go(i + 1, k)
                if x > best:
                    best = x
        return triangle[i][j] + best if best >= 0 else -1
    return go(0, 0)


def g_tapm(r):
    n = r.randint(1, 7)
    mode = r.choice([0, 1, 2])
    if mode == 0:
        return [[r.randint(1, 9) for _ in range(i + 1)] for i in range(n)]
    if mode == 1:
        return [[r.choice([1, 3, 5, 7]) if r.random() < 0.8 else r.choice([2, 4]) for _ in range(i + 1)] for i in range(n)]
    return _zigzag_tri(r, n)


def v_tapm(tests):
    for t in tests:
        tri = t["args"][0]
        assert 1 <= len(tri) <= 100
        for i, row in enumerate(tri):
            assert len(row) == i + 1 and all(1 <= v <= 1000 for v in row)
        assert t["expected"] == -1 or 1 <= t["expected"] <= 1000 * len(tri)
    outs = [t["expected"] for t in tests]
    assert -1 in outs and any(o > 0 for o in outs)


CHECKS["triangle-alternating-parity-max-path"] = (b_tapm, lambda r: [g_tapm(r)], "exact")
VALIDATE["triangle-alternating-parity-max-path"] = v_tapm


# ---------------------------------------------------------------- min-row-sweep-descent
p = add(
    id="min-row-sweep-descent", title="Row-Sweeping Descent", diff="Medium", topic=TOPIC,
    fn="minRowSweepDescent", params=[("matrix", "int[][]")], ret="int", cmp="exact",
    desc="<p>A cleaner enters the <code>matrix</code> through any cell of the top row and processes the rows one after another. In every row it arrives at some column <code>a</code> (in the top row it may choose <code>a</code> freely), then walks horizontally along that row to some column <code>b</code> (possibly <code>b = a</code>), visiting every cell between <code>a</code> and <code>b</code> inclusive, and pays the value of each of these cells exactly once. Then it steps down into the cell <code>(next row, b)</code>. In the last row it stops after its horizontal walk.</p><p>Return the smallest total that can be paid. Values may be negative.</p>",
    constraints=["1 &le; matrix.length, matrix[0].length &le; 60", "-100 &le; matrix[i][j] &le; 100"],
    hints=["Treat one row at a time. What does the next row need to know about everything that happened above it?",
           "Only the column where the cleaner leaves the row. Let <code>f[r][b]</code> be the cheapest total after finishing the walk in row <code>r</code> and standing in column <code>b</code>. Then <code>f[r][b] = min over a of f[r-1][a] + (sum of row r from column a to column b)</code>, with <code>f[-1][a] = 0</code>.",
           "Use prefix sums <code>P</code> of the row. For <code>a &le; b</code> the cost is <code>f[r-1][a] - P[a] + P[b+1]</code>, so keep a running minimum of <code>f[r-1][a] - P[a]</code> from the left. For <code>a &ge; b</code> it is <code>f[r-1][a] + P[a+1] - P[b]</code>, handled by a running minimum from the right. Take the smaller of the two for each <code>b</code>."],
    editorial=["The row is the stage and the exit column is the state, so <code>f[r][b]</code> is the cheapest way to finish row <code>r</code> in column <code>b</code>. The transition enumerates the entry column <code>a</code>: you pay the contiguous segment between <code>a</code> and <code>b</code>, and the previous row must have ended in column <code>a</code> (the step down keeps the column). Done naively this is O(n<sup>2</sup>) per row.",
               "With prefix sums <code>P[x] = row[0] + ... + row[x-1]</code>, the segment sum is <code>P[b+1] - P[a]</code> when <code>a &le; b</code> and <code>P[a+1] - P[b]</code> when <code>a &ge; b</code>. Each is a sum of a term depending only on <code>a</code> and a term depending only on <code>b</code>, so the minimum over <code>a</code> is a prefix minimum (from the left) or a suffix minimum (from the right). That reduces each row to O(n). The answer is the minimum of the last row's <code>f</code>. Total O(m &middot; n) time and O(n) space."],
    time="O(m &middot; n)", space="O(n)",
    solution='''def minRowSweepDescent(matrix):
    n = len(matrix[0])
    f = [0] * n
    for row in matrix:
        P = [0] * (n + 1)
        for i in range(n):
            P[i + 1] = P[i] + row[i]
        new = [0] * n
        run = float("inf")
        for b in range(n):
            run = min(run, f[b] - P[b])
            new[b] = run + P[b + 1]
        run = float("inf")
        for b in range(n - 1, -1, -1):
            run = min(run, f[b] + P[b + 1])
            new[b] = min(new[b], run - P[b])
        f = new
    return min(f)
''',
    tests=[[[[1, -2, 3], [4, 5, -6], [-7, 8, 9]]], [[[5, -5], [-5, 5]]], [[[4]]],
           [[[-4]]], [[[3, -1, -2, 4]]], [[[3], [-1], [-2]]], [[[1, 2, 3], [4, 5, 6]]], [[[-1, -1, -1], [-1, -1, -1]]],
           [[[100, 100], [100, 100]]], [[[-100, 50, -100], [50, -100, 50], [-100, 50, -100]]],
           [[[2, -3, 4, -5, 6], [-1, 8, -2, 7, -3], [5, -4, 3, -6, 2]]], [[[0, 0], [0, 0], [0, 0]]]],
)
_r = rnd(11008)
p["tests"].append([_grid(_r, 60, 60, -100, 100)])
p["tests"].append([_grid(_r, 60, 60, -100, 30)])
p["tests"].append([_grid(_r, 60, 60, -30, 100)])
p["tests"].append([_grid(_r, 8, 60, -100, 100)])


def b_mrs(matrix):
    h, w = len(matrix), len(matrix[0])

    def go(r, a):
        if r == h:
            return 0
        best = None
        for b in range(w):
            lo, hi = min(a, b), max(a, b)
            cost = sum(matrix[r][lo:hi + 1]) + go(r + 1, b)
            if best is None or cost < best:
                best = cost
        return best
    return min(go(0, a) for a in range(w))


def v_mrs(tests):
    for t in tests:
        g = t["args"][0]
        assert _is_rect(g) and len(g) <= 60 and len(g[0]) <= 60
        assert all(-100 <= v <= 100 for row in g for v in row)
        assert abs(t["expected"]) <= 100 * len(g) * len(g[0])


CHECKS["min-row-sweep-descent"] = (b_mrs, lambda r: [_grid(r, r.randint(1, 3), r.randint(1, 4), -9, 9)], "exact")
VALIDATE["min-row-sweep-descent"] = v_mrs


# ================================================================ HARD

# ---------------------------------------------------------------- min-falling-path-no-repeat-column
p = add(
    id="min-falling-path-no-repeat-column", title="Falling Path with No Repeated Column", diff="Hard", topic=TOPIC, tier="extra",
    fn="minFallingPathNoRepeat", params=[("matrix", "int[][]")], ret="int", cmp="exact",
    desc="<p>Choose exactly one cell from every row of the <code>matrix</code>, so that the cells chosen in two <strong>consecutive</strong> rows never lie in the same column. (The columns of rows that are further apart may coincide.)</p><p>Return the smallest possible sum of the chosen values. The input always admits a valid choice: if the matrix has more than one row, it has more than one column.</p>",
    constraints=["1 &le; matrix.length, matrix[0].length &le; 60", "If matrix.length &gt; 1 then matrix[0].length &ge; 2", "-100 &le; matrix[i][j] &le; 100"],
    hints=["Let <code>f[r][c]</code> be the best sum for rows <code>0..r</code> if row <code>r</code> uses column <code>c</code>. Which values of the previous row are allowed?",
           "<code>f[r][c] = matrix[r][c] + min over b &ne; c of f[r-1][b]</code>. Computing the inner minimum from scratch for every <code>c</code> gives O(m &middot; n<sup>2</sup>), which you can improve.",
           "For a whole row <code>f[r-1]</code> only two numbers matter: its smallest value (at column <code>i1</code>) and the smallest value among the other columns. Column <code>c &ne; i1</code> uses the smallest value, column <code>i1</code> uses the second smallest."],
    editorial=["The recurrence <code>f[r][c] = matrix[r][c] + min over b &ne; c of f[r-1][b]</code> follows from the fact that only the column of the previous row matters for the rule. To avoid scanning all other columns for each <code>c</code>, notice that the minimum of 'all except one' is the global minimum unless the excluded column is exactly the one holding the global minimum, in which case it is the second smallest value of the row.",
               "So per row we find the smallest value (with its column) and the second smallest value in one pass, then fill the next row in O(n). The total is O(m &middot; n) time and O(n) space. Care is needed for ties: if the smallest value occurs twice, the second smallest equals the smallest, which the 'smallest of the others' scan handles naturally. A single-row matrix is simply the minimum of that row."],
    time="O(m &middot; n)", space="O(n)",
    solution='''def minFallingPathNoRepeat(matrix):
    prev = matrix[0][:]
    for row in matrix[1:]:
        n = len(prev)
        i1 = min(range(n), key=lambda x: prev[x])
        m1 = prev[i1]
        m2 = min(prev[x] for x in range(n) if x != i1)
        prev = [row[c] + (m2 if c == i1 else m1) for c in range(n)]
    return min(prev)
''',
    tests=[[[[1, 2, 3], [4, 5, 6], [7, 8, 9]]], [[[7]]], [[[1, 2], [3, 4]]],
           [[[-5]]], [[[3, -1, 4]]], [[[1, 1], [1, 1], [1, 1]]], [[[1, 9], [1, 9], [1, 9], [1, 9]]],
           [[[-100, 100], [-100, 100]]], [[[0, 0, 0], [0, 0, 0]]], [[[5, 1, 5], [5, 1, 5], [5, 1, 5]]],
           [[[2, 2, 1], [1, 2, 2], [2, 1, 2], [2, 2, 1]]], [[[-3, 8, 2, 9], [-3, 1, 7, 4], [6, -3, 5, 0]]]],
)
_r = rnd(11009)
p["tests"].append([_grid(_r, 60, 60, -100, 100)])
p["tests"].append([_grid(_r, 60, 60, -2, 2)])
p["tests"].append([[[-100 if c == 0 else r_ % 7 for c in range(60)] for r_ in range(60)]])
p["tests"].append([_grid(_r, 60, 2, -100, 100)])


def b_mfpn(matrix):
    h, w = len(matrix), len(matrix[0])

    def go(r, banned):
        if r == h:
            return 0
        return min(matrix[r][c] + go(r + 1, c) for c in range(w) if c != banned)
    return go(0, -1)


def g_mfpn(r):
    h = r.randint(1, 5)
    w = r.randint(2 if h > 1 else 1, 5)
    return _grid(r, h, w, -r.choice([3, 9]), r.choice([3, 9]))


def v_mfpn(tests):
    for t in tests:
        g = t["args"][0]
        assert _is_rect(g) and len(g) <= 60 and len(g[0]) <= 60
        assert len(g) == 1 or len(g[0]) >= 2
        assert all(-100 <= v <= 100 for row in g for v in row)
        assert abs(t["expected"]) <= 100 * len(g)


CHECKS["min-falling-path-no-repeat-column"] = (b_mfpn, lambda r: [g_mfpn(r)], "exact")
VALIDATE["min-falling-path-no-repeat-column"] = v_mfpn


# ---------------------------------------------------------------- max-sum-path-limited-turns
p = add(
    id="max-sum-path-limited-turns", title="Richest Route with Limited Turns", diff="Hard", topic=TOPIC, tier="extra",
    fn="maxSumLimitedTurns", params=[("grid", "int[][]"), ("t", "int")], ret="int", cmp="exact",
    desc="<p>A courier starts in the top-left cell of the <code>grid</code> and must reach the bottom-right cell, moving only one step <strong>right</strong> or one step <strong>down</strong> at a time. The value of every visited cell, including the first and the last, is added to the courier's score; values may be negative.</p><p>A <em>turn</em> happens whenever two consecutive steps have different directions (right followed by down, or down followed by right). The first step never counts as a turn. Return the largest score among all routes that contain <strong>at most</strong> <code>t</code> turns.</p>",
    constraints=["1 &le; grid.length, grid[0].length &le; 50", "-100 &le; grid[i][j] &le; 100", "1 &le; t &le; 20 (so a route with at most t turns always exists)"],
    hints=["A route is a sequence of moves. The score so far and the position are not enough to decide the next move: you also need to know whether another turn is still affordable.",
           "Use the state <code>(r, c, d, k)</code>: you are at cell <code>(r, c)</code>, the last step had direction <code>d</code> (right or down) and you have made <code>k</code> turns so far. Store the best score for each state.",
           "Arrive by a right move from <code>(r, c-1)</code>: from direction right keeping <code>k</code>, or from direction down with <code>k - 1</code> (that step is a turn). Arrive by a down move symmetrically. The start cell is seeded with both directions and <code>k = 0</code>. The answer is the maximum over all directions and all <code>k &le; t</code> at the last cell."],
    editorial=["The classic right/down DP forgets how a cell was reached, but the turn rule needs exactly that, so we remember the last direction, and since the number of turns is bounded we remember how many were used. Let <code>f[d][k][r][c]</code> be the maximum score of a route ending at <code>(r, c)</code> whose last step had direction <code>d</code> and that made exactly <code>k</code> turns.",
               "Transitions: <code>f[right][k][r][c] = grid[r][c] + max(f[right][k][r][c-1], f[down][k-1][r][c-1])</code> and <code>f[down][k][r][c] = grid[r][c] + max(f[down][k][r-1][c], f[right][k-1][r-1][c])</code>. The start is a special case: it has not moved yet, so it is given both directions with zero turns, which makes the first step free of turns whatever it is. Because a route has at most <code>m + n - 3</code> turns, larger <code>t</code> can be capped. The state space is 2 &middot; (t + 1) &middot; m &middot; n and each state needs two lookups, so the time is O(t &middot; m &middot; n); keeping only the previous row gives O(t &middot; n) memory."],
    time="O(t &middot; m &middot; n)", space="O(t &middot; n)",
    solution='''def maxSumLimitedTurns(grid, t):
    m, n = len(grid), len(grid[0])
    t = min(t, m + n)
    NEG = float("-inf")
    # prev[d][k][c]: d = 0 last step right, d = 1 last step down
    prev = None
    for r in range(m):
        cur = [[[NEG] * n for _ in range(t + 1)] for _ in range(2)]
        for c in range(n):
            v = grid[r][c]
            if r == 0 and c == 0:
                cur[0][0][0] = v
                cur[1][0][0] = v
                continue
            for k in range(t + 1):
                if c > 0:
                    a = cur[0][k][c - 1]
                    if k > 0 and cur[1][k - 1][c - 1] > a:
                        a = cur[1][k - 1][c - 1]
                    cur[0][k][c] = a + v
                if r > 0:
                    b = prev[1][k][c]
                    if k > 0 and prev[0][k - 1][c] > b:
                        b = prev[0][k - 1][c]
                    if b + v > cur[1][k][c]:
                        cur[1][k][c] = b + v
        prev = cur
    return int(max(prev[d][k][n - 1] for d in range(2) for k in range(t + 1)))
''',
    tests=[[[[1, 2, 3], [4, 5, 6], [7, 8, 9]], 1], [[[1, 2, 3], [4, 5, 6], [7, 8, 9]], 2], [[[5]], 1],
           [[[-3, 4, -1, 6]], 1], [[[1], [-2], [3]], 5], [[[0, 0], [0, 0]], 1], [[[1, -9, 9], [-9, -9, -9], [9, -9, 1]], 1],
           [[[1, -9, 9], [-9, 5, -9], [9, -9, 1]], 2], [[[1, -9, 9], [-9, 5, -9], [9, -9, 1]], 4],
           [[[1, 1, 1, 1], [1, 9, 1, 1], [1, 1, 9, 1], [1, 1, 1, 1]], 1], [[[1, 1, 1, 1], [1, 9, 1, 1], [1, 1, 9, 1], [1, 1, 1, 1]], 3],
           [[[1, 1, 1, 1], [1, 9, 1, 1], [1, 1, 9, 1], [1, 1, 1, 1]], 20], [[[-5, -5], [-5, -5]], 1]],
)
_r = rnd(11010)
p["tests"].append([_grid(_r, 50, 50, -100, 100), 20])
p["tests"].append([_grid(_r, 50, 50, -100, 100), 3])
p["tests"].append([_grid(_r, 50, 50, 0, 100), 8])
p["tests"].append([_grid(_r, 50, 30, -100, 60), 12])


def b_mslt(grid, t):
    h, w = len(grid), len(grid[0])
    best = None
    for cells in _paths(h, w):
        moves = [(cells[i + 1][0] - cells[i][0]) for i in range(len(cells) - 1)]
        turns = sum(1 for i in range(1, len(moves)) if moves[i] != moves[i - 1])
        if turns <= t:
            s = sum(grid[r][c] for r, c in cells)
            if best is None or s > best:
                best = s
    return best


def g_mslt(r):
    return [_grid(r, r.randint(1, 5), r.randint(1, 5), -9, 9), r.randint(1, 4)]


def v_mslt(tests):
    for t in tests:
        g, tt = t["args"]
        assert _is_rect(g) and len(g) <= 50 and len(g[0]) <= 50
        assert all(-100 <= v <= 100 for row in g for v in row)
        assert 1 <= tt <= 20
        assert abs(t["expected"]) <= 100 * (len(g) + len(g[0]) - 1)


CHECKS["max-sum-path-limited-turns"] = (b_mslt, g_mslt, "exact")
VALIDATE["max-sum-path-limited-turns"] = v_mslt


# ---------------------------------------------------------------- gem-orchard-round-trip
p = add(
    id="gem-orchard-round-trip", title="Gem Orchard Round Trip", diff="Hard", topic=TOPIC,
    fn="maxGemsRoundTrip", params=[("grid", "int[][]")], ret="int", cmp="exact",
    desc="<p>The square <code>grid</code> describes an orchard. A cell holding <code>-1</code> is a thorn bush that cannot be entered; any other cell holds that many gems (<code>0</code> or more).</p><p>A collector starts in the top-left cell, walks to the bottom-right cell moving only <strong>right</strong> or <strong>down</strong> through cells that are not thorn bushes, and then walks back to the top-left cell moving only <strong>left</strong> or <strong>up</strong> through cells that are not thorn bushes. Whenever the collector stands on a cell it takes all gems there, and the cell is empty from then on (so gems of a cell are only counted once, even if both walks cross it).</p><p>Return the largest number of gems that can be collected on such a round trip. If there is no way to reach the bottom-right cell, return <code>0</code>.</p>",
    constraints=["1 &le; grid.length == grid[0].length &le; 35", "grid[i][j] = -1 (thorn bush) or 0 &le; grid[i][j] &le; 20 (gems)"],
    hints=["The way back, read in reverse, is another right/down walk. So the task is to pick two right/down walks from corner to corner that together collect the most, counting a shared cell once.",
           "Greedily taking the best first walk and then the best second walk is wrong, because the first walk can steal gems that the second walk needs. Move the two walkers <em>simultaneously</em>, one step each.",
           "After <code>t</code> steps walker 1 is at <code>(r1, t - r1)</code> and walker 2 at <code>(r2, t - r2)</code>, so the state is just <code>(t, r1, r2)</code>. They stand on the same cell exactly when <code>r1 == r2</code>, and then the gems are counted once. Each walker came from above or from the left, giving four predecessor states."],
    editorial=["Reverse the way back: the trip becomes two walks from the top-left to the bottom-right cell, both moving right or down, and the collected gems are the gems of the union of their cells. Optimising the two walks one after the other fails, because the first walk may take gems that make a worse first walk plus a better second walk the true optimum.",
               "Advance both walkers together. After exactly <code>t</code> steps each walker has <code>r + c = t</code>, so the pair of positions is described by <code>(r1, r2)</code> alone. Let <code>dp[t][r1][r2]</code> be the most gems collected when the walkers are at those cells; two walkers on the same cell at the same time add its gems once, and since both walk monotonically they can never share a cell at different times. Transitions take the best of the four previous states <code>(r1 or r1-1, r2 or r2-1)</code> and add the gems of the cells (thorn bushes make the state invalid). The answer is <code>dp[2n-2][n-1][n-1]</code>, or 0 if that state is unreachable. There are O(n) layers of O(n<sup>2</sup>) states, so the time is O(n<sup>3</sup>) and the space O(n<sup>2</sup>)."],
    time="O(n<sup>3</sup>)", space="O(n<sup>2</sup>)",
    solution='''def maxGemsRoundTrip(grid):
    n = len(grid)
    NEG = -10 ** 9
    if grid[0][0] == -1:
        return 0
    dp = [[NEG] * n for _ in range(n)]
    dp[0][0] = grid[0][0]
    for t in range(1, 2 * n - 1):
        new = [[NEG] * n for _ in range(n)]
        lo, hi = max(0, t - n + 1), min(n - 1, t)
        for r1 in range(lo, hi + 1):
            c1 = t - r1
            if grid[r1][c1] == -1:
                continue
            for r2 in range(r1, hi + 1):
                c2 = t - r2
                if grid[r2][c2] == -1:
                    continue
                best = dp[r1][r2]
                if r1 > 0 and dp[r1 - 1][r2] > best:
                    best = dp[r1 - 1][r2]
                if r2 > 0 and dp[r1][r2 - 1] > best:
                    best = dp[r1][r2 - 1]
                if r1 > 0 and r2 > 0 and dp[r1 - 1][r2 - 1] > best:
                    best = dp[r1 - 1][r2 - 1]
                if best < 0:
                    continue
                gain = grid[r1][c1] + (grid[r2][c2] if r1 != r2 else 0)
                new[r1][r2] = new[r2][r1] = best + gain
        dp = new
    return max(0, dp[n - 1][n - 1])
''',
    tests=[[[[0, 1, 1], [1, 0, 1], [0, 1, 1]]], [[[1, 1, -1], [1, -1, 1], [-1, 1, 1]]], [[[5]]],
           [[[-1]]], [[[0]]], [[[0, 5], [5, 0]]], [[[0, -1], [-1, 0]]], [[[3, 2], [4, 1]]], [[[1, -1], [1, 1]]],
           [[[0, 20, 0, 0], [0, 0, 0, 20], [20, 0, 0, 0], [0, 0, 20, 0]]], [[[1, 1, 1, 1], [1, -1, -1, 1], [1, 1, 1, 1], [-1, 1, -1, 1]]],
           [[[2, 0, 0, 3], [0, -1, 7, 0], [0, 7, -1, 0], [3, 0, 0, 2]]], [[[0, 1, 0, -1], [1, -1, 1, 1], [0, 1, 0, 0], [-1, 1, 1, 1]]]],
)
_r = rnd(11011)


def _orchard(r, n, pw, hi):
    g = [[(-1 if r.random() < pw else r.randint(0, hi)) for _ in range(n)] for _ in range(n)]
    g[0][0] = r.randint(0, hi)
    g[n - 1][n - 1] = r.randint(0, hi)
    return g


p["tests"].append([_orchard(_r, 35, 0.0, 20)])
p["tests"].append([_orchard(_r, 35, 0.12, 20)])
p["tests"].append([_orchard(_r, 35, 0.3, 20)])
p["tests"].append([_orchard(_r, 30, 0.2, 1)])
p["tests"].append([[[20] * 35 for _ in range(35)]])


def b_mgrt(grid):
    n = len(grid)
    paths = [cells for cells in _paths(n, n) if all(grid[r][c] != -1 for r, c in cells)]
    best = 0
    for a in paths:
        for b in paths:
            best = max(best, sum(grid[r][c] for r, c in set(a) | set(b)))
    return best


def g_mgrt(r):
    n = r.randint(1, 4)
    return _orchard(r, n, r.choice([0.0, 0.15, 0.3]), r.choice([1, 9]))


def v_mgrt(tests):
    for t in tests:
        g = t["args"][0]
        assert _is_rect(g) and len(g) == len(g[0]) and len(g) <= 35
        assert all(v == -1 or 0 <= v <= 20 for row in g for v in row)
        assert 0 <= t["expected"] <= 20 * (4 * len(g))
    outs = [t["expected"] for t in tests]
    assert 0 in outs and any(o > 0 for o in outs)


CHECKS["gem-orchard-round-trip"] = (b_mgrt, lambda r: [g_mgrt(r)], "exact")
VALIDATE["gem-orchard-round-trip"] = v_mgrt
