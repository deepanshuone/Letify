"""Problems: Dynamic Programming on grids and triangles. See data/lib.py for the registry."""
from math import comb

from lib import add, rnd, CHECKS, VALIDATE, gen_arr  # noqa: F401

TOPIC = "Dynamic Programming"
MOD = 10 ** 9 + 7


def _grid(r, h, w, lo, hi):
    return [[r.randint(lo, hi) for _ in range(w)] for _ in range(h)]


def _bin_grid(r, h, w, p_one):
    return [[1 if r.random() < p_one else 0 for _ in range(w)] for _ in range(h)]


def _is_rect(g):
    return len(g) > 0 and all(len(row) == len(g[0]) for row in g) and len(g[0]) > 0


# ================================================================ EASY

# ---------------------------------------------------------------- grid-paths-with-obstacles
add(
    id="grid-paths-with-obstacles", title="Grid Paths with Obstacles", diff="Easy", topic=TOPIC,
    fn="countPathsWithObstacles", params=[("grid", "int[][]")], ret="int", cmp="exact",
    desc="<p>You are given a rectangular <code>grid</code> where <code>0</code> marks a free cell and <code>1</code> marks a blocked cell. A traveller starts in the top-left cell and wants to reach the bottom-right cell, moving only one step <strong>right</strong> or one step <strong>down</strong> at a time and never entering a blocked cell.</p><p>Return the number of different routes. If the start or the destination is blocked, the answer is <code>0</code>. The answer is guaranteed to fit in a 32-bit signed integer.</p>",
    constraints=["1 &le; grid.length, grid[0].length &le; 17", "grid[i][j] is 0 or 1", "The start and destination cells may themselves be blocked"],
    hints=["Think about the last step of any route. Which two neighbouring cells can the traveller come from?",
           "Let <code>ways[r][c]</code> be the number of routes that end in cell <code>(r, c)</code>. A blocked cell has <code>ways = 0</code>; a free cell gets <code>ways[r-1][c] + ways[r][c-1]</code>.",
           "Seed the start cell with 1 (unless it is blocked). Only the previous row is needed, so one array of width n can be updated in place."],
    editorial=["Every route into a free cell arrives from the cell above or the cell on its left, and these two sets of routes are disjoint, so <code>ways[r][c] = ways[r-1][c] + ways[r][c-1]</code>. A blocked cell can never be stood on, so its count is forced to 0, which automatically prevents any route from passing through it.",
               "Row <code>r</code> only reads row <code>r-1</code> and the cell to its own left, so a single array of length <code>n</code> is enough: for each cell, set it to 0 if blocked, otherwise add the value of its left neighbour to the value it already holds from the row above. This runs in O(m &middot; n) time and O(n) space. Because the closed-form binomial count no longer applies once obstacles appear, the DP is the natural tool."],
    time="O(m &middot; n)", space="O(n)",
    solution='''def countPathsWithObstacles(grid):
    n = len(grid[0])
    ways = [0] * n
    ways[0] = 1
    for row in grid:
        for c in range(n):
            if row[c] == 1:
                ways[c] = 0
            elif c > 0:
                ways[c] += ways[c - 1]
    return ways[-1]
''',
    tests=[[[[0, 0, 0], [0, 1, 0], [0, 0, 0]]], [[[0, 1], [0, 0]]], [[[1]]],
           [[[0]]], [[[0, 0, 0, 0, 0]]], [[[0], [0], [0]]], [[[0, 1, 0]]], [[[1, 0], [0, 0]]], [[[0, 0], [0, 1]]],
           [[[0, 0, 0], [1, 1, 1], [0, 0, 0]]], [[[0, 0, 0, 0], [0, 1, 1, 0], [0, 0, 0, 0], [1, 0, 1, 0]]],
           [[[0, 0, 1, 0, 0], [0, 0, 0, 0, 1], [1, 0, 0, 0, 0], [0, 0, 1, 0, 0], [0, 0, 0, 0, 0]]]],
)
_p = [p_ for p_ in __import__("lib").P if p_["id"] == "grid-paths-with-obstacles"][0]
_r = rnd(9101)
_p["tests"].append([[[0] * 17 for _ in range(17)]])
_g = _bin_grid(_r, 17, 17, 0.08); _g[0][0] = _g[16][16] = 0
_p["tests"].append([_g])
_g = _bin_grid(_r, 17, 12, 0.15); _g[0][0] = _g[16][11] = 0
_p["tests"].append([_g])
_g = _bin_grid(_r, 15, 17, 0.25); _g[0][0] = _g[14][16] = 0
_p["tests"].append([_g])
_g = [[0] * 17 for _ in range(17)]; _g[8][8] = 1; _g[3][14] = 1
_p["tests"].append([_g])
_p["tests"].append([[[0] * 17]])


def b_gpo(grid):
    h, w = len(grid), len(grid[0])

    def go(r, c):
        if r >= h or c >= w or grid[r][c] == 1:
            return 0
        if r == h - 1 and c == w - 1:
            return 1
        return go(r + 1, c) + go(r, c + 1)
    return go(0, 0)


def g_gpo(r):
    return [_bin_grid(r, r.randint(1, 5), r.randint(1, 5), r.choice([0.0, 0.15, 0.3]))]


def v_gpo(tests):
    for t in tests:
        g = t["args"][0]
        assert _is_rect(g) and len(g) <= 17 and len(g[0]) <= 17
        assert all(v in (0, 1) for row in g for v in row)
        assert 0 <= t["expected"] <= 2 * 10 ** 9


CHECKS["grid-paths-with-obstacles"] = (b_gpo, g_gpo, "exact")
VALIDATE["grid-paths-with-obstacles"] = v_gpo


# ---------------------------------------------------------------- minimum-path-sum-grid
add(
    id="minimum-path-sum-grid", title="Minimum Path Sum in a Grid", diff="Easy", topic=TOPIC,
    fn="minPathSumGrid", params=[("grid", "int[][]")], ret="int", cmp="exact",
    desc="<p>Every cell of the rectangular <code>grid</code> holds a non-negative toll. Starting in the top-left cell you must reach the bottom-right cell, moving only <strong>right</strong> or <strong>down</strong>. You pay the toll of every cell you stand on, including the first and the last one.</p><p>Return the smallest total toll over all possible routes.</p>",
    constraints=["1 &le; grid.length, grid[0].length &le; 100", "0 &le; grid[i][j] &le; 100"],
    hints=["Greedily stepping to the cheaper neighbour can fail, because a cheap cell may lead into an expensive region. Consider the last cell of the route instead.",
           "The cheapest route into cell <code>(r, c)</code> must come from above or from the left. Define <code>best[r][c]</code> as the cheapest toll to reach it.",
           "<code>best[r][c] = grid[r][c] + min(best[r-1][c], best[r][c-1])</code>; the first row and first column only have one possible predecessor."],
    editorial=["Let <code>best[r][c]</code> be the minimum total toll of a route from the top-left cell to <code>(r, c)</code>. The last step of that route came from <code>(r-1, c)</code> or <code>(r, c-1)</code>, and the part before that step must itself be optimal, otherwise swapping in a cheaper prefix would improve the route. That gives <code>best[r][c] = grid[r][c] + min(best[r-1][c], best[r][c-1])</code>.",
               "On the first row there is no cell above and on the first column no cell to the left, so those cells simply extend the single available predecessor. Process cells row by row; a single array holding the current row of <code>best</code> values is sufficient. Time O(m &middot; n), extra space O(n)."],
    time="O(m &middot; n)", space="O(n)",
    solution='''def minPathSumGrid(grid):
    n = len(grid[0])
    best = [0] * n
    for r, row in enumerate(grid):
        for c in range(n):
            if r == 0 and c == 0:
                best[c] = row[c]
            elif r == 0:
                best[c] = best[c - 1] + row[c]
            elif c == 0:
                best[c] += row[c]
            else:
                best[c] = row[c] + min(best[c], best[c - 1])
    return best[-1]
''',
    tests=[[[[1, 3, 1], [1, 5, 1], [4, 2, 1]]], [[[1, 2, 3], [4, 5, 6]]], [[[7]]],
           [[[0]]], [[[5, 1, 4, 9]]], [[[5], [1], [4], [9]]], [[[1, 100, 1], [1, 100, 1], [1, 1, 1]]],
           [[[0, 100, 100], [0, 100, 0], [0, 0, 0]]], [[[100, 100], [100, 100]]],
           [[[1, 2, 5], [3, 2, 1], [9, 9, 1], [1, 1, 1]]], [[[2, 0, 0, 0], [2, 9, 9, 0], [2, 2, 2, 2]]]],
)
_p = [p_ for p_ in __import__("lib").P if p_["id"] == "minimum-path-sum-grid"][0]
_r = rnd(9102)
_p["tests"].append([_grid(_r, 100, 100, 0, 100)])
_p["tests"].append([_grid(_r, 100, 100, 0, 3)])
_p["tests"].append([_grid(_r, 1, 100, 0, 100)])
_p["tests"].append([_grid(_r, 100, 1, 0, 100)])
_p["tests"].append([_grid(_r, 37, 83, 0, 100)])
_p["tests"].append([[[100] * 100 for _ in range(100)]])


def b_mps(grid):
    h, w = len(grid), len(grid[0])
    best = [float("inf")]

    def go(r, c, acc):
        acc += grid[r][c]
        if r == h - 1 and c == w - 1:
            best[0] = min(best[0], acc)
            return
        if r + 1 < h:
            go(r + 1, c, acc)
        if c + 1 < w:
            go(r, c + 1, acc)
    go(0, 0, 0)
    return best[0]


def v_mps(tests):
    for t in tests:
        g = t["args"][0]
        assert _is_rect(g) and len(g) <= 100 and len(g[0]) <= 100
        assert all(0 <= v <= 100 for row in g for v in row)
        assert t["expected"] <= 100 * (len(g) + len(g[0]) - 1)


CHECKS["minimum-path-sum-grid"] = (b_mps, lambda r: [_grid(r, r.randint(1, 5), r.randint(1, 5), 0, 9)], "exact")
VALIDATE["minimum-path-sum-grid"] = v_mps


# ================================================================ MEDIUM

# ---------------------------------------------------------------- triangle-min-path-sum
add(
    id="triangle-min-path-sum", title="Cheapest Descent Through a Triangle", diff="Medium", topic=TOPIC,
    fn="triangleMinPath", params=[("triangle", "int[][]")], ret="int", cmp="exact",
    desc="<p>A number triangle is given as a list of rows: row <code>i</code> has exactly <code>i + 1</code> integers. You start at the single number in the top row and descend one row at a time. From position <code>j</code> in row <code>i</code> you may move to position <code>j</code> or position <code>j + 1</code> in row <code>i + 1</code>.</p><p>Return the smallest possible sum of the numbers visited on a descent from the top row to the bottom row. Numbers may be negative.</p>",
    constraints=["1 &le; triangle.length &le; 100", "triangle[i].length == i + 1", "-1000 &le; triangle[i][j] &le; 1000"],
    hints=["Enumerating all descents takes 2<sup>n-1</sup> paths. Many of them share long stretches, so look for repeated sub-problems.",
           "Try working from the bottom row upwards: what is the cheapest way to finish the descent starting from a given cell?",
           "<code>down[i][j] = triangle[i][j] + min(down[i+1][j], down[i+1][j+1])</code>, starting from the bottom row's own values. The answer is <code>down[0][0]</code>, and one array of size n is enough."],
    editorial=["Define <code>down[i][j]</code> as the minimum sum of a descent that starts at cell <code>(i, j)</code> and ends in the bottom row. For the last row it is the cell value itself. For any other cell, the descent first takes the cell and then continues optimally from one of its two children, so <code>down[i][j] = triangle[i][j] + min(down[i+1][j], down[i+1][j+1])</code>.",
               "Going bottom-up is neat because every row has exactly one more cell than the row above, so no bounds checks are needed, and the answer ends up in a single cell. Reusing one array that starts as a copy of the last row and is shrunk by one element each iteration gives O(n) extra space; total work is O(n<sup>2</sup>) for the n(n+1)/2 cells."],
    time="O(n<sup>2</sup>)", space="O(n)",
    solution='''def triangleMinPath(triangle):
    down = triangle[-1][:]
    for i in range(len(triangle) - 2, -1, -1):
        row = triangle[i]
        for j in range(i + 1):
            down[j] = row[j] + min(down[j], down[j + 1])
    return down[0]
''',
    tests=[[[[2], [3, 4], [6, 5, 7], [4, 1, 8, 3]]], [[[-10]]], [[[1], [2, 3]]],
           [[[0]]], [[[5], [-1, -2]]], [[[1], [1, 1], [1, 1, 1]]], [[[-1], [2, 3], [1, -1, -3]]],
           [[[1000], [1000, 1000], [1000, 1000, 1000]]], [[[-1000], [-1000, -1000], [-1000, -1000, -1000]]],
           [[[3], [1, 9], [9, 9, 1], [9, 9, 9, 9]]], [[[1], [9, 1], [9, 9, 1], [9, 9, 9, 1], [1, 9, 9, 9, 9]]]],
)
_p = [p_ for p_ in __import__("lib").P if p_["id"] == "triangle-min-path-sum"][0]
_r = rnd(9103)


def _tri(r, n, lo, hi):
    return [[r.randint(lo, hi) for _ in range(i + 1)] for i in range(n)]


_p["tests"].append([_tri(_r, 100, -1000, 1000)])
_p["tests"].append([_tri(_r, 100, 0, 1000)])
_p["tests"].append([_tri(_r, 100, -5, 5)])
_p["tests"].append([[[(-1000 if j == 0 else 1000) for j in range(i + 1)] for i in range(100)]])
_p["tests"].append([_tri(_r, 57, -1000, 1000)])


def b_tri(triangle):
    n = len(triangle)

    def go(i, j):
        if i == n - 1:
            return triangle[i][j]
        return triangle[i][j] + min(go(i + 1, j), go(i + 1, j + 1))
    return go(0, 0)


def v_tri(tests):
    for t in tests:
        tri = t["args"][0]
        assert 1 <= len(tri) <= 100
        for i, row in enumerate(tri):
            assert len(row) == i + 1
            assert all(-1000 <= v <= 1000 for v in row)


CHECKS["triangle-min-path-sum"] = (b_tri, lambda r: [_tri(r, r.randint(1, 8), -9, 9)], "exact")
VALIDATE["triangle-min-path-sum"] = v_tri


# ---------------------------------------------------------------- largest-square-of-ones
add(
    id="largest-square-of-ones", title="Largest All-Ones Square", diff="Medium", topic=TOPIC,
    fn="largestSquareOfOnes", params=[("matrix", "int[][]")], ret="int", cmp="exact",
    desc="<p>The <code>matrix</code> contains only <code>0</code>s and <code>1</code>s. Find the largest square block of cells that consists entirely of <code>1</code>s, and return its <strong>area</strong> (side length squared). If the matrix has no <code>1</code> at all, return <code>0</code>.</p>",
    constraints=["1 &le; matrix.length, matrix[0].length &le; 100", "matrix[i][j] is 0 or 1"],
    hints=["Checking every square at every position works but is slow for large grids. Try to reuse information from neighbouring cells.",
           "Let <code>side[r][c]</code> be the side of the largest all-ones square whose <em>bottom-right</em> corner is cell <code>(r, c)</code>.",
           "If the cell is 0 the value is 0; otherwise it is <code>1 + min(side[r-1][c], side[r][c-1], side[r-1][c-1])</code>. The answer is the square of the largest value."],
    editorial=["Fix the bottom-right corner <code>(r, c)</code> of a square. It can have side <code>k</code> only if the cell is 1 and the three squares of side <code>k-1</code> that end just above, just to the left and diagonally up-left of it are all-ones as well. That yields <code>side[r][c] = 1 + min(side[r-1][c], side[r][c-1], side[r-1][c-1])</code> for a 1-cell, and 0 for a 0-cell.",
               "Out-of-range neighbours count as 0, so the first row and column are just copies of the matrix. Track the maximum side seen while filling the table, and return its square. Keeping only the previous row and the old diagonal value reduces memory to O(n); time is O(m &middot; n)."],
    time="O(m &middot; n)", space="O(n)",
    solution='''def largestSquareOfOnes(matrix):
    n = len(matrix[0])
    prev = [0] * (n + 1)
    best = 0
    for row in matrix:
        cur = [0] * (n + 1)
        for c in range(n):
            if row[c] == 1:
                cur[c + 1] = 1 + min(prev[c], prev[c + 1], cur[c])
                if cur[c + 1] > best:
                    best = cur[c + 1]
        prev = cur
    return best * best
''',
    tests=[[[[1, 0, 1, 0, 0], [1, 0, 1, 1, 1], [1, 1, 1, 1, 1], [1, 0, 0, 1, 0]]], [[[0, 1], [1, 0]]], [[[0]]],
           [[[1]]], [[[1, 1, 1, 1]]], [[[1], [1], [1]]], [[[1, 1], [1, 1]]], [[[1, 1, 0], [1, 1, 1], [0, 1, 1]]],
           [[[1, 1, 1], [1, 1, 1], [1, 1, 1]]], [[[0, 0, 0], [0, 0, 0]]], [[[1, 1, 1, 0], [1, 1, 1, 1], [1, 1, 1, 1], [0, 1, 1, 1]]],
           [[[1, 0, 1], [0, 1, 0], [1, 0, 1]]]],
)
_p = [p_ for p_ in __import__("lib").P if p_["id"] == "largest-square-of-ones"][0]
_r = rnd(9104)
_p["tests"].append([[[1] * 100 for _ in range(100)]])
_p["tests"].append([_bin_grid(_r, 100, 100, 0.5)])
_p["tests"].append([_bin_grid(_r, 100, 100, 0.95)])
_p["tests"].append([_bin_grid(_r, 100, 100, 0.995)])
_p["tests"].append([_bin_grid(_r, 60, 100, 0.9)])
_g = [[0] * 100 for _ in range(100)]
for _i in range(30, 71):
    for _j in range(20, 61):
        _g[_i][_j] = 1
_p["tests"].append([_g])
_p["tests"].append([[[1] * 100]])


def b_lsq(matrix):
    h, w = len(matrix), len(matrix[0])
    best = 0
    for r in range(h):
        for c in range(w):
            k = 1
            while r + k <= h and c + k <= w:
                if all(matrix[i][j] == 1 for i in range(r, r + k) for j in range(c, c + k)):
                    best = max(best, k)
                k += 1
    return best * best


def v_lsq(tests):
    for t in tests:
        g = t["args"][0]
        assert _is_rect(g) and len(g) <= 100 and len(g[0]) <= 100
        assert all(v in (0, 1) for row in g for v in row)
        s = int(t["expected"] ** 0.5 + 0.5)
        assert s * s == t["expected"] and s <= min(len(g), len(g[0]))


CHECKS["largest-square-of-ones"] = (b_lsq, lambda r: [_bin_grid(r, r.randint(1, 6), r.randint(1, 6), r.choice([0.5, 0.8]))], "exact")
VALIDATE["largest-square-of-ones"] = v_lsq


# ---------------------------------------------------------------- count-all-ones-squares
add(
    id="count-all-ones-squares", title="Count All-Ones Squares", diff="Medium", topic=TOPIC,
    fn="countAllOnesSquares", params=[("matrix", "int[][]")], ret="int", cmp="exact",
    desc="<p>The <code>matrix</code> contains only <code>0</code>s and <code>1</code>s. Count how many square sub-blocks (of any side length, including <code>1 x 1</code>) are made up entirely of <code>1</code>s. Two blocks are different if they cover different cells, even when one lies inside the other.</p>",
    constraints=["1 &le; matrix.length, matrix[0].length &le; 100", "matrix[i][j] is 0 or 1"],
    hints=["Counting the squares position by position is expensive. Instead, group squares by their bottom-right corner.",
           "Let <code>side[r][c]</code> be the largest all-ones square ending at <code>(r, c)</code>. How many squares end exactly at that corner?",
           "If the biggest square has side <code>k</code>, then squares of sides <code>1, 2, ..., k</code> all end at that corner. So the answer is the sum of all <code>side[r][c]</code>, with <code>side[r][c] = 1 + min(up, left, up-left)</code> for 1-cells."],
    editorial=["A square is determined by its bottom-right corner and its side. For a fixed corner <code>(r, c)</code>, if an all-ones square of side <code>k</code> ends there, so does one of every smaller side, because it is a sub-block. Hence the number of squares ending at the corner equals the largest side <code>k</code> found there.",
               "That largest side follows the usual recurrence <code>side[r][c] = 1 + min(side[r-1][c], side[r][c-1], side[r-1][c-1])</code> for a 1-cell and 0 otherwise. Summing <code>side</code> over the whole matrix gives the total in O(m &middot; n) time; two rows of storage are enough."],
    time="O(m &middot; n)", space="O(n)",
    solution='''def countAllOnesSquares(matrix):
    n = len(matrix[0])
    prev = [0] * (n + 1)
    total = 0
    for row in matrix:
        cur = [0] * (n + 1)
        for c in range(n):
            if row[c] == 1:
                cur[c + 1] = 1 + min(prev[c], prev[c + 1], cur[c])
                total += cur[c + 1]
        prev = cur
    return total
''',
    tests=[[[[0, 1, 1, 1], [1, 1, 1, 1], [0, 1, 1, 1]]], [[[1, 0, 1], [1, 1, 0], [1, 1, 0]]], [[[0]]],
           [[[1]]], [[[1, 1, 1, 1, 1]]], [[[1], [1]]], [[[1, 1], [1, 1]]], [[[0, 0], [0, 0]]],
           [[[1, 1, 1], [1, 1, 1], [1, 1, 1]]], [[[1, 0, 1], [0, 1, 0], [1, 0, 1]]],
           [[[1, 1, 0, 1], [1, 1, 1, 1], [0, 1, 1, 1], [1, 1, 1, 1]]]],
)
_p = [p_ for p_ in __import__("lib").P if p_["id"] == "count-all-ones-squares"][0]
_r = rnd(9105)
_p["tests"].append([[[1] * 100 for _ in range(100)]])
_p["tests"].append([_bin_grid(_r, 100, 100, 0.5)])
_p["tests"].append([_bin_grid(_r, 100, 100, 0.9)])
_p["tests"].append([_bin_grid(_r, 100, 100, 0.98)])
_p["tests"].append([_bin_grid(_r, 100, 40, 0.8)])
_p["tests"].append([_bin_grid(_r, 1, 100, 0.7)])


def b_cas(matrix):
    h, w = len(matrix), len(matrix[0])
    total = 0
    for k in range(1, min(h, w) + 1):
        for r in range(h - k + 1):
            for c in range(w - k + 1):
                if all(matrix[i][j] == 1 for i in range(r, r + k) for j in range(c, c + k)):
                    total += 1
    return total


def v_cas(tests):
    for t in tests:
        g = t["args"][0]
        assert _is_rect(g) and len(g) <= 100 and len(g[0]) <= 100
        assert all(v in (0, 1) for row in g for v in row)
        if all(v == 1 for row in g for v in row):
            h, w = len(g), len(g[0])
            m = min(h, w)
            assert t["expected"] == sum((h - k + 1) * (w - k + 1) for k in range(1, m + 1))


CHECKS["count-all-ones-squares"] = (b_cas, lambda r: [_bin_grid(r, r.randint(1, 6), r.randint(1, 6), r.choice([0.5, 0.8, 0.95]))], "exact")
VALIDATE["count-all-ones-squares"] = v_cas


# ---------------------------------------------------------------- grid-exit-paths-count
add(
    id="grid-exit-paths-count", title="Ways to Leave the Grid", diff="Medium", topic=TOPIC,
    fn="countGridExits", params=[("m", "int"), ("n", "int"), ("maxMove", "int"), ("startRow", "int"), ("startCol", "int")], ret="int", cmp="exact",
    desc="<p>A ball sits in cell <code>(startRow, startCol)</code> of an <code>m x n</code> grid (rows and columns are 0-indexed). In one move it rolls to one of the four orthogonally adjacent cells, and it may roll <em>outside</em> the grid. As soon as the ball leaves the grid it stops for good.</p><p>Count the move sequences of length <strong>at most</strong> <code>maxMove</code> that make the ball leave the grid (a sequence ends at the move that takes the ball outside). Two sequences differ if their lists of directions differ. Because the count can be huge, return it modulo <code>1,000,000,007</code>.</p>",
    constraints=["1 &le; m, n &le; 50", "0 &le; maxMove &le; 50", "0 &le; startRow &lt; m and 0 &le; startCol &lt; n"],
    hints=["A plain recursion branches four ways at every move. Notice that the future of the ball only depends on its cell and the number of moves it still has left.",
           "Simulate time forward: keep <code>ways[r][c]</code>, the number of move sequences that leave the ball at <code>(r, c)</code> after exactly <code>t</code> moves without having exited.",
           "For each step, push every count to the four neighbours. A neighbour inside the grid receives it for the next step; a neighbour outside the grid adds it to a running exit total. Take everything modulo 10<sup>9</sup>+7."],
    editorial=["Let <code>ways_t[r][c]</code> be the number of direction sequences of length <code>t</code> after which the ball is still inside, standing on <code>(r, c)</code>. Start with <code>ways_0 = 1</code> at the start cell. To compute <code>ways_{t+1}</code>, send each count to the four neighbours: if a neighbour lies outside the grid, those sequences have just exited, so add the count to the answer; otherwise add it to that neighbour in the next table.",
               "Because an exited ball never moves again, each exiting sequence is counted exactly once, at the move on which it leaves. Doing this for <code>maxMove</code> rounds costs O(maxMove &middot; m &middot; n) time with two tables of O(m &middot; n) memory. Reduce by 10<sup>9</sup>+7 after every addition."],
    time="O(maxMove &middot; m &middot; n)", space="O(m &middot; n)",
    solution='''def countGridExits(m, n, maxMove, startRow, startCol):
    MOD = 10 ** 9 + 7
    ways = [[0] * n for _ in range(m)]
    ways[startRow][startCol] = 1
    out = 0
    for _ in range(maxMove):
        nxt = [[0] * n for _ in range(m)]
        for r in range(m):
            for c in range(n):
                w = ways[r][c]
                if w == 0:
                    continue
                for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < m and 0 <= nc < n:
                        nxt[nr][nc] = (nxt[nr][nc] + w) % MOD
                    else:
                        out = (out + w) % MOD
        ways = nxt
    return out
''',
    tests=[[2, 2, 2, 0, 0], [1, 3, 3, 0, 1], [1, 1, 0, 0, 0],
           [1, 1, 1, 0, 0], [1, 1, 5, 0, 0], [3, 3, 0, 1, 1], [3, 3, 1, 1, 1], [3, 3, 2, 1, 1], [2, 3, 4, 1, 2],
           [4, 4, 6, 2, 1], [5, 1, 7, 2, 0], [50, 50, 50, 25, 25], [50, 50, 50, 0, 0], [50, 50, 50, 49, 49],
           [1, 50, 50, 0, 25], [50, 1, 50, 10, 0], [20, 30, 50, 5, 17], [7, 9, 40, 3, 4]],
)


def b_gec(m, n, maxMove, startRow, startCol):
    from functools import lru_cache

    @lru_cache(maxsize=None)  # memoised recursion over (cell, moves left); modulus only at the very end
    def go(r, c, left):
        if not (0 <= r < m and 0 <= c < n):
            return 1
        if left == 0:
            return 0
        return go(r + 1, c, left - 1) + go(r - 1, c, left - 1) + go(r, c + 1, left - 1) + go(r, c - 1, left - 1)
    return go(startRow, startCol, maxMove) % MOD


def g_gec(r):
    m, n = r.randint(1, 4), r.randint(1, 4)
    return [m, n, r.randint(0, 7), r.randrange(m), r.randrange(n)]


def v_gec(tests):
    for t in tests:
        m, n, mv, sr, sc = t["args"]
        assert 1 <= m <= 50 and 1 <= n <= 50 and 0 <= mv <= 50
        assert 0 <= sr < m and 0 <= sc < n
        assert 0 <= t["expected"] < MOD
        if mv == 0:
            assert t["expected"] == 0
        if m == 1 and n == 1 and mv >= 1:
            assert t["expected"] == 4


CHECKS["grid-exit-paths-count"] = (b_gec, g_gec, "exact")
VALIDATE["grid-exit-paths-count"] = v_gec


# ---------------------------------------------------------------- two-budget-item-picking
add(
    id="two-budget-item-picking", title="Pick Items Under Two Budgets", diff="Medium", topic=TOPIC,
    fn="maxItemsTwoBudgets", params=[("costA", "int[]"), ("costB", "int[]"), ("budgetA", "int"), ("budgetB", "int")], ret="int", cmp="exact",
    desc="<p>A workshop has two separate budgets of materials: <code>budgetA</code> units of material A and <code>budgetB</code> units of material B. There are <code>n</code> items, and item <code>i</code> consumes <code>costA[i]</code> units of A and <code>costB[i]</code> units of B. Each item can be made at most once.</p><p>Return the largest number of different items that can be made without exceeding either budget.</p>",
    constraints=["1 &le; costA.length == costB.length &le; 150", "0 &le; costA[i], costB[i] &le; 100, and costA[i] + costB[i] &ge; 1", "0 &le; budgetA, budgetB &le; 100"],
    hints=["This is a 0/1 knapsack, but with two capacity limits instead of one. The value of every item is simply 1.",
           "Let <code>best[a][b]</code> be the largest number of items you can make using at most <code>a</code> units of A and at most <code>b</code> units of B, considering the items seen so far.",
           "For each item, update the table in <em>decreasing</em> order of both <code>a</code> and <code>b</code>: <code>best[a][b] = max(best[a][b], best[a-costA][b-costB] + 1)</code>. Iterating downwards stops the item being used twice."],
    editorial=["Add the items one at a time. After processing some items, <code>best[a][b]</code> holds the maximum count achievable within budgets <code>(a, b)</code>. When a new item with costs <code>(x, y)</code> arrives, either skip it (value unchanged) or make it, which is possible when <code>a &ge; x</code> and <code>b &ge; y</code> and yields <code>best[a-x][b-y] + 1</code>.",
               "Updating in place requires visiting <code>a</code> from <code>budgetA</code> down to <code>x</code> and, inside it, <code>b</code> from <code>budgetB</code> down to <code>y</code>; this guarantees that the cell we read still reflects the state before the current item, so no item is counted twice. The running time is O(n &middot; budgetA &middot; budgetB) and the memory O(budgetA &middot; budgetB)."],
    time="O(n &middot; A &middot; B)", space="O(A &middot; B)",
    solution='''def maxItemsTwoBudgets(costA, costB, budgetA, budgetB):
    best = [[0] * (budgetB + 1) for _ in range(budgetA + 1)]
    for x, y in zip(costA, costB):
        for a in range(budgetA, x - 1, -1):
            row = best[a]
            src = best[a - x]
            for b in range(budgetB, y - 1, -1):
                v = src[b - y] + 1
                if v > row[b]:
                    row[b] = v
    return best[budgetA][budgetB]
''',
    tests=[[[5, 1, 0, 1, 0], [1, 0, 1, 1, 1], 5, 3], [[0, 1, 0], [1, 0, 1], 1, 1], [[3], [3], 2, 5],
           [[1], [0], 1, 0], [[1], [1], 0, 0], [[0, 0, 0], [1, 2, 3], 0, 3], [[2, 2, 2], [2, 2, 2], 100, 100],
           [[2, 2, 2], [2, 2, 2], 4, 100], [[1, 2, 3, 4], [4, 3, 2, 1], 5, 5], [[5, 4], [1, 1], 4, 2],
           [[10, 1, 1, 1], [1, 10, 1, 1], 3, 3], [[100, 100], [100, 100], 100, 100], [[1, 1, 1, 1], [0, 0, 0, 0], 3, 0]],
)
_p = [p_ for p_ in __import__("lib").P if p_["id"] == "two-budget-item-picking"][0]
_r = rnd(9107)


def _items(r, n, lo, hi):
    a, b = [], []
    while len(a) < n:
        x, y = r.randint(lo, hi), r.randint(lo, hi)
        if x + y >= 1:
            a.append(x)
            b.append(y)
    return a, b


for _n, _lo, _hi, _A, _B in ((150, 0, 20, 100, 100), (150, 0, 100, 100, 100), (120, 1, 8, 100, 60),
                             (150, 0, 3, 100, 100), (100, 5, 30, 77, 100), (60, 0, 10, 100, 0)):
    _a, _b = _items(_r, _n, _lo, _hi)
    _p["tests"].append([_a, _b, _A, _B])


def b_mitb(costA, costB, budgetA, budgetB):
    n = len(costA)
    best = 0
    for mask in range(1 << n):
        sa = sb = cnt = 0
        for i in range(n):
            if mask >> i & 1:
                sa += costA[i]
                sb += costB[i]
                cnt += 1
        if sa <= budgetA and sb <= budgetB:
            best = max(best, cnt)
    return best


def g_mitb(r):
    n = r.randint(1, 9)
    a, b = _items(r, n, 0, 6)
    return [a, b, r.randint(0, 12), r.randint(0, 12)]


def v_mitb(tests):
    for t in tests:
        a, b, A, B = t["args"]
        assert 1 <= len(a) == len(b) <= 150
        assert all(0 <= v <= 100 for v in a + b)
        assert all(x + y >= 1 for x, y in zip(a, b))
        assert 0 <= A <= 100 and 0 <= B <= 100
        assert 0 <= t["expected"] <= len(a)


CHECKS["two-budget-item-picking"] = (b_mitb, g_mitb, "exact")
VALIDATE["two-budget-item-picking"] = v_mitb


# ---------------------------------------------------------------- grid-paths-sum-divisible-by-k
add(
    id="grid-paths-sum-divisible-by-k", title="Grid Paths with Sum Divisible by K", diff="Medium", topic=TOPIC,
    fn="countPathsDivisibleByK", params=[("grid", "int[][]"), ("k", "int")], ret="int", cmp="exact",
    desc="<p>You walk from the top-left cell to the bottom-right cell of <code>grid</code>, stepping only <strong>right</strong> or <strong>down</strong>. The sum of all cell values on a route (including both end cells) is the route's score.</p><p>Count the routes whose score is divisible by <code>k</code>. Since the count may be enormous, return it modulo <code>1,000,000,007</code>.</p>",
    constraints=["1 &le; grid.length, grid[0].length &le; 50", "0 &le; grid[i][j] &le; 100", "1 &le; k &le; 50"],
    hints=["Only the remainder of the running sum modulo <code>k</code> matters, never the sum itself.",
           "Extend the usual path-counting DP with a third dimension: <code>ways[r][c][x]</code> is the number of routes to <code>(r, c)</code> whose sum leaves remainder <code>x</code>.",
           "A route reaching <code>(r, c)</code> with remainder <code>x</code> comes from above or from the left with remainder <code>(x - grid[r][c]) mod k</code>. The answer is <code>ways[m-1][n-1][0]</code>."],
    editorial=["Two routes that arrive at the same cell with the same remainder modulo <code>k</code> are indistinguishable for the rest of the journey, so we can merge them into one counter. The state is therefore (cell, remainder), giving at most 50 &middot; 50 &middot; 50 states.",
               "Transition: after stepping onto a cell of value <code>v</code>, a route that had remainder <code>x</code> in its predecessor now has remainder <code>(x + v) mod k</code>. Add the counters of the upper and left predecessors under that shift, taking the result modulo 10<sup>9</sup>+7. Seed the top-left cell with remainder <code>grid[0][0] mod k</code> equal to 1. Only the previous row and the current row of remainder tables are needed, so memory is O(n &middot; k) and time is O(m &middot; n &middot; k)."],
    time="O(m &middot; n &middot; k)", space="O(n &middot; k)",
    solution='''def countPathsDivisibleByK(grid, k):
    MOD = 10 ** 9 + 7
    n = len(grid[0])
    dp = [[0] * k for _ in range(n)]
    for i, row in enumerate(grid):
        for j in range(n):
            v = row[j] % k
            new = [0] * k
            if i == 0 and j == 0:
                new[v] = 1
            else:
                if i > 0:
                    for rem, cnt in enumerate(dp[j]):
                        if cnt:
                            idx = (rem + v) % k
                            new[idx] = (new[idx] + cnt) % MOD
                if j > 0:
                    for rem, cnt in enumerate(dp[j - 1]):
                        if cnt:
                            idx = (rem + v) % k
                            new[idx] = (new[idx] + cnt) % MOD
            dp[j] = new
    return dp[n - 1][0]
''',
    tests=[[[[5, 2, 4], [3, 0, 5], [0, 7, 2]], 3], [[[0, 0]], 5], [[[7, 3, 4, 9], [2, 3, 6, 2], [2, 3, 7, 0]], 1],
           [[[0]], 1], [[[4]], 4], [[[3]], 2], [[[1, 2, 3]], 6], [[[1], [2], [3]], 5], [[[1, 1], [1, 1]], 3],
           [[[2, 2], [2, 2]], 2], [[[5, 5, 5], [5, 5, 5], [5, 5, 5]], 5], [[[1, 2, 3], [4, 5, 6], [7, 8, 9]], 7],
           [[[100, 100], [100, 100]], 50]],
)
_p = [p_ for p_ in __import__("lib").P if p_["id"] == "grid-paths-sum-divisible-by-k"][0]
_r = rnd(9108)
_p["tests"].append([_grid(_r, 50, 50, 0, 100), 1])
_p["tests"].append([_grid(_r, 50, 50, 0, 100), 50])
_p["tests"].append([_grid(_r, 50, 50, 0, 100), 7])
_p["tests"].append([_grid(_r, 50, 50, 0, 3), 2])
_p["tests"].append([[[0] * 50 for _ in range(50)], 50])
_p["tests"].append([_grid(_r, 31, 44, 0, 100), 37])
_p["tests"].append([_grid(_r, 50, 50, 0, 100), 49])


def b_gpd(grid, k):
    h, w = len(grid), len(grid[0])
    total = [0]

    def go(r, c, acc):
        acc += grid[r][c]
        if r == h - 1 and c == w - 1:
            if acc % k == 0:
                total[0] += 1
            return
        if r + 1 < h:
            go(r + 1, c, acc)
        if c + 1 < w:
            go(r, c + 1, acc)
    go(0, 0, 0)
    return total[0] % MOD


def g_gpd(r):
    return [_grid(r, r.randint(1, 5), r.randint(1, 5), 0, 12), r.randint(1, 7)]


def v_gpd(tests):
    for t in tests:
        g, k = t["args"]
        assert _is_rect(g) and len(g) <= 50 and len(g[0]) <= 50
        assert all(0 <= v <= 100 for row in g for v in row)
        assert 1 <= k <= 50
        assert 0 <= t["expected"] < MOD
        if k == 1:
            assert t["expected"] == comb(len(g) + len(g[0]) - 2, len(g) - 1) % MOD


CHECKS["grid-paths-sum-divisible-by-k"] = (b_gpd, g_gpd, "exact")
VALIDATE["grid-paths-sum-divisible-by-k"] = v_gpd


# ================================================================ HARD

# ---------------------------------------------------------------- dungeon-minimum-starting-health
add(
    id="dungeon-minimum-starting-health", title="Dungeon Minimum Starting Health", diff="Hard", topic=TOPIC,
    fn="minStartingHealth", params=[("dungeon", "int[][]")], ret="int", cmp="exact",
    desc="<p>A knight must cross a rectangular dungeon from the top-left room to the bottom-right room, moving only <strong>right</strong> or <strong>down</strong>. Entering a room changes his health by that room's value: a negative number is damage, a positive number is a healing potion, and <code>0</code> changes nothing. The first and the last room also apply their value.</p><p>The knight dies the moment his health becomes <code>0</code> or less, even in the final room. Return the smallest positive starting health that lets him complete the crossing along some route.</p>",
    constraints=["1 &le; dungeon.length, dungeon[0].length &le; 100", "-1000 &le; dungeon[i][j] &le; 1000", "The knight's health must stay at least 1 after entering every room"],
    hints=["Running a forward DP over 'minimum health needed so far' is tricky because two quantities matter: the current health and the lowest point reached. Try going backwards.",
           "Let <code>need[r][c]</code> be the minimum health required <em>on entering</em> room <code>(r, c)</code> to survive the rest of the trip to the end.",
           "At the end room <code>need = max(1, 1 - value)</code>. Elsewhere, <code>need[r][c] = max(1, min(need[r+1][c], need[r][c+1]) - value[r][c])</code>. The answer is <code>need[0][0]</code>."],
    editorial=["A forward DP does not work, because a route with a large sum so far but a deep dip earlier is not comparable to one with a smaller sum and no dip. Reversing the direction fixes this: define <code>need[r][c]</code> as the least health with which the knight can <em>enter</em> room <code>(r, c)</code> and still finish alive. It depends only on the future, which is exactly what the knight must survive.",
               "In the last room the health after entering must be at least 1, so <code>need = max(1, 1 - value)</code>. In another room the health after entering is <code>h + value</code>, and it must be at least the smaller requirement of the two next rooms, so <code>h &ge; min(need[r+1][c], need[r][c+1]) - value</code>; clamp this to at least 1 because health must always be positive. Fill the table from the bottom-right corner back to the top-left in O(m &middot; n) time and O(n) space."],
    time="O(m &middot; n)", space="O(n)",
    solution='''def minStartingHealth(dungeon):
    m, n = len(dungeon), len(dungeon[0])
    INF = float("inf")
    need = [INF] * (n + 1)
    need[n - 1] = 1
    for r in range(m - 1, -1, -1):
        for c in range(n - 1, -1, -1):
            nxt = min(need[c], need[c + 1])
            need[c] = max(1, nxt - dungeon[r][c])
    return need[0]
''',
    tests=[[[[-2, -3, 3], [-5, -10, 1], [10, 30, -5]]], [[[0]]], [[[-5]]],
           [[[5]]], [[[100]]], [[[-3, 5]]], [[[1, -3, 3], [0, -2, 0], [-3, -3, -3]]], [[[0, 0], [0, 0]]],
           [[[-1], [-1], [-1], [-1]]], [[[2], [-5], [10]]], [[[0, -3, -4], [1, 10, -20]]],
           [[[1, 1, 1, -1000], [-1000, 1000, 1000, 1000]]], [[[-1000, -1000], [-1000, -1000]]],
           [[[0, 5, -3, -20], [-1, -6, 2, 3], [8, -4, -4, -4]]]],
)
_p = [p_ for p_ in __import__("lib").P if p_["id"] == "dungeon-minimum-starting-health"][0]
_r = rnd(9109)
_p["tests"].append([_grid(_r, 100, 100, -1000, 1000)])
_p["tests"].append([_grid(_r, 100, 100, -10, 10)])
_p["tests"].append([_grid(_r, 100, 100, -1000, -1)])
_p["tests"].append([_grid(_r, 100, 100, 0, 1000)])
_p["tests"].append([_grid(_r, 100, 1, -1000, 1000)])
_p["tests"].append([_grid(_r, 1, 100, -1000, 1000)])
_p["tests"].append([_grid(_r, 47, 91, -300, 250)])
_g = _grid(_r, 100, 100, -5, 5)
for _i in range(100):  # a cheap detour: damage along the border, healing in the middle
    _g[0][_i] = -1000
    _g[_i][0] = -1000
_p["tests"].append([_g])


def b_msh(dungeon):
    m, n = len(dungeon), len(dungeon[0])

    def survives(h):
        def go(r, c, hp):
            hp += dungeon[r][c]
            if hp <= 0:
                return False
            if r == m - 1 and c == n - 1:
                return True
            return (r + 1 < m and go(r + 1, c, hp)) or (c + 1 < n and go(r, c + 1, hp))
        return go(0, 0, h)
    h = 1
    while not survives(h):
        h += 1
    return h


def g_msh(r):
    return [_grid(r, r.randint(1, 5), r.randint(1, 5), -9, 9)]


def v_msh(tests):
    for t in tests:
        g = t["args"][0]
        assert _is_rect(g) and len(g) <= 100 and len(g[0]) <= 100
        assert all(-1000 <= v <= 1000 for row in g for v in row)
        assert t["expected"] >= 1
        if all(v >= 0 for row in g for v in row):
            assert t["expected"] == 1


CHECKS["dungeon-minimum-starting-health"] = (b_msh, g_msh, "exact")
VALIDATE["dungeon-minimum-starting-health"] = v_msh


# ---------------------------------------------------------------- two-robots-cherry-collection
add(
    id="two-robots-cherry-collection", title="Two Robots Cherry Collection", diff="Hard", topic=TOPIC,
    fn="twoRobotsCherries", params=[("grid", "int[][]")], ret="int", cmp="exact",
    desc="<p>An orchard is a grid with <code>rows</code> rows and <code>cols</code> columns; <code>grid[r][c]</code> is the number of cherries lying in that cell. Two robots work together. Robot 1 starts in the top-left cell <code>(0, 0)</code> and robot 2 starts in the top-right cell <code>(0, cols - 1)</code>.</p><p>The robots move in lockstep, one row down per step. From column <code>c</code>, each robot independently moves to column <code>c - 1</code>, <code>c</code> or <code>c + 1</code> in the next row, never leaving the grid. Each robot picks up all the cherries in every cell it stands on, including its starting cell. If both robots are in the same cell, the cherries there are only collected once. Both robots stop in the last row.</p><p>Return the maximum total number of cherries the robots can collect.</p>",
    constraints=["1 &le; rows &le; 60, 1 &le; cols &le; 40", "0 &le; grid[r][c] &le; 100", "When cols == 1 both robots start in the same cell"],
    hints=["Two robots in the same row means the situation at any moment is described by the row and the two columns. Moving them one after another instead of together would need far more state.",
           "Define <code>f[r][a][b]</code> as the most cherries both robots can still collect from row <code>r</code> down, when robot 1 is in column <code>a</code> and robot 2 in column <code>b</code>.",
           "<code>f[r][a][b] = cells(r, a, b) + max f[r+1][a'][b']</code> over the 9 combinations <code>a' in {a-1,a,a+1}</code>, <code>b' in {b-1,b,b+1}</code>, where <code>cells</code> adds the cherries of both columns but counts a shared cell once."],
    editorial=["Because both robots descend exactly one row per step, the pair (column of robot 1, column of robot 2) fully describes the future once the row is known. There are at most cols<sup>2</sup> such pairs per row, and each has 9 successors, so a DP over rows is cheap even though the number of joint routes is astronomical.",
               "Work from the last row upwards: <code>f[last][a][b] = cells(last, a, b)</code>, and for earlier rows add the best successor value. The value of a cell pair is <code>grid[r][a] + grid[r][b]</code> if <code>a != b</code>, else just <code>grid[r][a]</code>; this is what handles the 'collected only once' rule. The answer is <code>f[0][0][cols-1]</code>. Only two layers of the table are needed at any time, so memory is O(cols<sup>2</sup>) and time O(rows &middot; cols<sup>2</sup> &middot; 9)."],
    time="O(rows &middot; cols<sup>2</sup>)", space="O(cols<sup>2</sup>)",
    solution='''def twoRobotsCherries(grid):
    rows, cols = len(grid), len(grid[0])
    NEG = float("-inf")
    last = grid[-1]
    f = [[(last[a] + (last[b] if a != b else 0)) for b in range(cols)] for a in range(cols)]
    for r in range(rows - 2, -1, -1):
        row = grid[r]
        g = [[NEG] * cols for _ in range(cols)]
        for a in range(cols):
            alo, ahi = max(0, a - 1), min(cols - 1, a + 1)
            for b in range(cols):
                blo, bhi = max(0, b - 1), min(cols - 1, b + 1)
                best = NEG
                for na in range(alo, ahi + 1):
                    fa = f[na]
                    for nb in range(blo, bhi + 1):
                        if fa[nb] > best:
                            best = fa[nb]
                g[a][b] = best + row[a] + (row[b] if a != b else 0)
        f = g
    return f[0][cols - 1]
''',
    tests=[[[[3, 1, 1], [2, 5, 1], [1, 5, 5], [2, 1, 1]]], [[[1, 0, 0, 0, 0, 0, 1], [2, 0, 0, 0, 0, 3, 0], [2, 0, 9, 0, 0, 0, 0], [0, 3, 0, 5, 4, 0, 0], [1, 0, 2, 3, 0, 0, 6]]], [[[5]]],
           [[[4], [7], [9]]], [[[1, 2]]], [[[3, 8]]], [[[1, 2], [3, 4]]], [[[0, 0, 0], [0, 0, 0]]],
           [[[100, 100], [100, 100], [100, 100]]], [[[1, 1, 1, 1], [1, 1, 1, 1], [1, 1, 1, 1], [1, 1, 1, 1]]],
           [[[1, 0, 0, 0, 1], [0, 9, 9, 9, 0], [1, 0, 0, 0, 1]]], [[[0, 5, 5, 0], [9, 0, 0, 9], [0, 0, 0, 0]]],
           [[[2, 3, 4]]]],
)
_p = [p_ for p_ in __import__("lib").P if p_["id"] == "two-robots-cherry-collection"][0]
_r = rnd(9110)
_p["tests"].append([_grid(_r, 60, 40, 0, 100)])
_p["tests"].append([_grid(_r, 60, 40, 0, 3)])
_p["tests"].append([_grid(_r, 60, 1, 0, 100)])
_p["tests"].append([_grid(_r, 1, 40, 0, 100)])
_p["tests"].append([_grid(_r, 45, 25, 0, 100)])
_p["tests"].append([[[100] * 40 for _ in range(60)]])
_p["tests"].append([_grid(_r, 30, 2, 0, 100)])


def b_trc(grid):
    rows, cols = len(grid), len(grid[0])

    def go(r, a, b):
        got = grid[r][a] + (grid[r][b] if a != b else 0)
        if r == rows - 1:
            return got
        best = 0
        for da in (-1, 0, 1):
            for db in (-1, 0, 1):
                na, nb = a + da, b + db
                if 0 <= na < cols and 0 <= nb < cols:
                    best = max(best, go(r + 1, na, nb))
        return got + best
    return go(0, 0, cols - 1)


def g_trc(r):
    return [_grid(r, r.randint(1, 5), r.randint(1, 4), 0, 9)]


def v_trc(tests):
    for t in tests:
        g = t["args"][0]
        assert _is_rect(g) and len(g) <= 60 and len(g[0]) <= 40
        assert all(0 <= v <= 100 for row in g for v in row)
        assert 0 <= t["expected"] <= 2 * 100 * len(g)
        if len(g[0]) == 1:
            assert t["expected"] == sum(row[0] for row in g)


CHECKS["two-robots-cherry-collection"] = (b_trc, g_trc, "exact")
VALIDATE["two-robots-cherry-collection"] = v_trc
