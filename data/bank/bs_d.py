"""Problems: binary search in two dimensions (sorted matrices). See data/lib.py for the registry."""
from bisect import bisect_left, bisect_right
from collections import deque

from lib import add, rnd, CHECKS, VALIDATE, gen_arr  # noqa: F401

INT_MIN, INT_MAX = -10 ** 9, 10 ** 9  # the largest magnitude the constraints allow
TOPIC = "Binary Search"


def _mono_grid(r, m, n, lo, hi):
    """Random m x n grid whose rows and columns are all non-decreasing (sorting the columns keeps the rows sorted)."""
    g = [[r.randint(lo, hi) for _ in range(n)] for _ in range(m)]
    for row in g:
        row.sort()
    for j in range(n):
        col = sorted(g[i][j] for i in range(m))
        for i in range(m):
            g[i][j] = col[i]
    return g


def _rows_sorted(r, m, n, lo, hi):
    return [sorted(r.randint(lo, hi) for _ in range(n)) for _ in range(m)]


def _flat_grid(r, m, n, lo, hi):
    """Row-major sorted grid: every row is sorted and each row starts at or after the previous row's end."""
    vals = sorted(r.randint(lo, hi) for _ in range(m * n))
    return [vals[i * n:(i + 1) * n] for i in range(m)]


def _is_mono(g):
    m, n = len(g), len(g[0])
    return all(len(row) == n for row in g) and all(
        (j + 1 == n or g[i][j] <= g[i][j + 1]) and (i + 1 == m or g[i][j] <= g[i + 1][j])
        for i in range(m) for j in range(n))


# ---------------------------------------------------------------- EASY

p = add(
    id="row-with-most-ones", title="Row With the Most Ones", diff="Easy", topic=TOPIC, tier="common",
    fn="rowWithMostOnes", params=[("grid", "int[][]")], ret="int", cmp="exact",
    desc="<p>The <code>m x n</code> matrix <code>grid</code> contains only <code>0</code> and <code>1</code>. Inside every row, all the zeros come before all the ones (each row is sorted in non-decreasing order).</p><p>Return the 0-based index of the row that contains the most ones. If several rows tie, return the smallest index. If the matrix contains no <code>1</code> at all, return <code>-1</code>.</p><p>Counting every cell takes O(m * n); try to finish in O(m + n).</p>",
    constraints=["1 &le; m, n &le; 100", "grid[i][j] is 0 or 1", "Each row is in non-decreasing order"],
    hints=["Because each row is sorted, the number of ones in a row is decided by where its first 1 sits. A binary search per row finds it in O(log n).",
           "You do not need the exact count of every row, only to know whether a row beats the best one so far. Suppose the best row so far has its first 1 at column <code>c</code>; a new row beats it only if it has a 1 at column <code>c - 1</code>.",
           "Start at the top-right corner with <code>col = n - 1</code>. For each row, keep moving left while the cell is <code>1</code>; if you moved at all, this row is the new best. The column pointer never moves right, so the whole scan is O(m + n)."],
    editorial=["The simple solutions are to count the ones in each row (O(m * n)) or to binary search the first 1 of each row (O(m log n)). The sortedness of rows allows something better.",
               "Keep a pointer <code>col</code>, initially <code>n - 1</code>, that marks the leftmost column where some row seen so far has a 1 (all columns before it are either unseen or hold zero in the best row). For the next row, slide <code>col</code> left while <code>grid[row][col] == 1</code>. If the pointer moved, this row has strictly more ones than any earlier row, so it becomes the best. If it did not move, the row has at most as many ones as the best row, and since ties keep the earlier row, nothing changes.",
               "The pointer only decreases and the row index only increases, so there are at most m + n steps: O(m + n) time and O(1) extra space. If the pointer never moved, no row contained a one and the answer is -1."],
    time="O(m + n)", space="O(1)",
    solution='''def rowWithMostOnes(grid):
    m, n = len(grid), len(grid[0])
    col = n - 1
    best = -1
    for row in range(m):
        while col >= 0 and grid[row][col] == 1:
            col -= 1
            best = row
    return best
''',
    tests=[[[[0, 0, 1], [0, 1, 1], [0, 0, 0]]], [[[0, 1, 1], [0, 1, 1]]], [[[0]]], [[[1]]], [[[0, 0], [0, 0]]],
           [[[0, 1], [1, 1], [1, 1]]], [[[1, 1, 1]]], [[[0], [0], [1], [1]]],
           [[[0, 0, 0, 1], [0, 0, 1, 1], [0, 1, 1, 1], [1, 1, 1, 1]]], [[[1, 1, 1, 1], [0, 1, 1, 1], [0, 0, 1, 1], [0, 0, 0, 1]]]],
)
_r = rnd(8401)


def _ones_grid(r, m, n, maxones=None):
    mx = n if maxones is None else maxones
    return [[0] * (n - k) + [1] * k for k in (r.randint(0, mx) for _ in range(m))]


p["tests"].append([_ones_grid(_r, 100, 100)])
p["tests"].append([_ones_grid(_r, 100, 100, 3)])
_g = _ones_grid(_r, 100, 100, 40); _g[63] = [0] * 30 + [1] * 70
p["tests"].append([_g])
p["tests"].append([[[0] * 100 for _ in range(100)]])


def b_ones(grid):
    best, idx = 0, -1
    for i, row in enumerate(grid):
        if sum(row) > best:
            best, idx = sum(row), i
    return idx


def g_ones(r):
    return _ones_grid(r, r.randint(1, 6), r.randint(1, 6))


def v_ones(tests):
    for t in tests:
        g = t["args"][0]
        assert 1 <= len(g) <= 100 and 1 <= len(g[0]) <= 100
        for row in g:
            assert len(row) == len(g[0]) and all(v in (0, 1) for v in row) and row == sorted(row)


CHECKS["row-with-most-ones"] = (b_ones, lambda r: [g_ones(r)], "exact")
VALIDATE["row-with-most-ones"] = v_ones

p = add(
    id="smallest-value-common-to-all-rows", title="Smallest Value Common to All Rows", diff="Easy", topic=TOPIC, tier="extra",
    fn="smallestCommon", params=[("grid", "int[][]")], ret="int", cmp="exact",
    desc="<p>Every row of the <code>m x n</code> matrix <code>grid</code> is sorted in strictly increasing order (no row repeats a value). Return the smallest value that appears in <em>every</em> row, or <code>-1</code> if no value is shared by all rows.</p>",
    constraints=["1 &le; m, n &le; 60", "1 &le; grid[i][j] &le; 10,000", "Each row is strictly increasing"],
    hints=["A value is a candidate only if it is in the first row. Check the candidates from the smallest upward and stop at the first one that works.",
           "To test a candidate in another row you do not have to scan that row, since it is sorted.",
           "For each value <code>v</code> of row 0, binary search <code>v</code> in rows 1..m-1. The first <code>v</code> found in all rows is the answer; if some row has no value at or above <code>v</code>, nothing larger can work either and you can return -1."],
    editorial=["The answer, if it exists, is a value of the first row, so go through that row in increasing order; the first value present in every other row is the smallest common value.",
               "Membership of <code>v</code> in a sorted row is a binary search (<code>bisect_left</code>): find the first position with value &ge; <code>v</code> and check that it equals <code>v</code>. If the position runs off the end of a row, that row's maximum is below <code>v</code>, so no later (larger) candidate can be in that row either, and the answer is -1.",
               "Total cost is O(n * m * log n) in the worst case. A counting alternative (a value is common when its count over all rows is m) also works because rows have no repeats, at O(m * n) time with an O(range) count table, but the search version is the one that generalises to rows too large to scan."],
    time="O(m n log n)", space="O(1)",
    solution='''from bisect import bisect_left


def smallestCommon(grid):
    for v in grid[0]:
        found = True
        for row in grid[1:]:
            i = bisect_left(row, v)
            if i == len(row):
                return -1
            if row[i] != v:
                found = False
                break
        if found:
            return v
    return -1
''',
    tests=[[[[1, 2, 3, 4, 5], [2, 4, 5, 8, 10], [3, 5, 7, 9, 11], [1, 3, 5, 7, 9]]], [[[1, 2, 3], [4, 5, 6]]], [[[7]]],
           [[[1, 2, 3, 4]]], [[[5], [5], [5]]], [[[1, 3], [2, 3], [3, 4]]], [[[1, 5, 9], [1, 5, 9], [2, 5, 9]]],
           [[[1, 5, 10000], [1, 6, 10000], [5, 6, 10000]]], [[[1, 2], [1, 3], [1, 4], [1, 5]]], [[[2, 4, 6], [1, 3, 5], [2, 4, 6]]]],
)
_r = rnd(8402)


def _common_grid(r, m, n, hi, planted):
    rows = []
    for _ in range(m):
        pool = [v for v in range(1, hi + 1) if v not in planted]
        row = sorted(r.sample(pool, n - len(planted)) + list(planted))
        rows.append(row)
    return rows


p["tests"].append([_common_grid(_r, 60, 60, 200, [150])])
p["tests"].append([_common_grid(_r, 60, 60, 120, [])])
p["tests"].append([_common_grid(_r, 60, 60, 10000, [3, 9999])])
p["tests"].append([[list(range(1, 61)) for _ in range(60)]])
_g = _common_grid(_r, 60, 60, 300, [200]); _g[41] = [v for v in _g[41] if v != 200] + [10000]; _g[41].sort()
p["tests"].append([_g])


def b_common(grid):
    s = set(grid[0])
    for row in grid[1:]:
        s &= set(row)
    return min(s) if s else -1


def g_common(r):
    m, n = r.randint(1, 5), r.randint(1, 5)
    return [sorted(r.sample(range(1, 9), n)) for _ in range(m)]


def v_common(tests):
    for t in tests:
        g = t["args"][0]
        assert 1 <= len(g) <= 60 and 1 <= len(g[0]) <= 60
        for row in g:
            assert len(row) == len(g[0]) and all(1 <= v <= 10000 for v in row)
            assert all(row[i] < row[i + 1] for i in range(len(row) - 1))


CHECKS["smallest-value-common-to-all-rows"] = (b_common, lambda r: [g_common(r)], "exact")
VALIDATE["smallest-value-common-to-all-rows"] = v_common

p = add(
    id="flattened-grid-insert-position", title="Insert Position in a Flattened Sorted Grid", diff="Easy", topic=TOPIC, tier="extra",
    fn="gridInsertPosition", params=[("grid", "int[][]"), ("target", "int")], ret="int", cmp="exact",
    desc="<p>In the <code>m x n</code> matrix <code>grid</code>, each row is sorted in non-decreasing order, and the first value of every row is greater than or equal to the last value of the row above it. Reading the cells row by row therefore gives one long non-decreasing sequence of <code>m * n</code> values.</p><p>Return the position (0-based, in that row-by-row order) where <code>target</code> would have to be inserted to keep the sequence sorted, placing it before any equal values. Equivalently, return how many cells hold a value strictly smaller than <code>target</code>. The answer lies between <code>0</code> and <code>m * n</code>.</p>",
    constraints=["1 &le; m, n &le; 60", "-10<sup>9</sup> &le; grid[i][j], target &le; 10<sup>9</sup>", "Reading the grid row by row gives a non-decreasing sequence"],
    hints=["Scanning counts the smaller cells in O(m * n). The row-by-row order is sorted, which is exactly what binary search needs.",
           "Treat the grid as one array of length <code>m * n</code>. Position <code>p</code> of that array lives at row <code>p // n</code>, column <code>p % n</code>.",
           "Binary search for the first position <code>p</code> whose value is &ge; <code>target</code>, with search range <code>[0, m * n]</code> (the upper end means 'all values are smaller'). Compare <code>grid[p // n][p % n]</code> with the target."],
    editorial=["Because each row begins at or after the previous row's end, the cells read row by row form a sorted array, and you can binary search it without building it: position <code>p</code> corresponds to <code>grid[p // n][p % n]</code>.",
               "We want the lower bound: the smallest <code>p</code> with value &ge; <code>target</code>, or <code>m * n</code> if there is none. Keep <code>lo = 0</code> and <code>hi = m * n</code>; while <code>lo &lt; hi</code> take <code>mid</code>, and if the cell at <code>mid</code> is smaller than the target move <code>lo = mid + 1</code>, otherwise <code>hi = mid</code>. The result is <code>lo</code>.",
               "The loop runs about log<sub>2</sub>(m * n) times, so the time is O(log(m * n)) with O(1) space. Searching for the first position with value &ge; target (rather than any equal value) is what makes the answer unique when the grid has duplicates."],
    time="O(log(m n))", space="O(1)",
    solution='''def gridInsertPosition(grid, target):
    m, n = len(grid), len(grid[0])
    lo, hi = 0, m * n
    while lo < hi:
        mid = (lo + hi) // 2
        if grid[mid // n][mid % n] < target:
            lo = mid + 1
        else:
            hi = mid
    return lo
''',
    tests=[[[[1, 3, 5], [7, 9, 11]], 6], [[[1, 3, 5], [7, 9, 11]], 7], [[[1, 3, 5], [7, 9, 11]], 0], [[[1, 3, 5], [7, 9, 11]], 12],
           [[[4]], 4], [[[4]], 5], [[[2, 2], [2, 2]], 2], [[[2, 2], [2, 2]], 3], [[[1, 2, 2], [2, 2, 3], [3, 3, 8]], 3],
           [[[-5], [-3], [-3], [0]], -3], [[[-10 ** 9, 0], [0, 10 ** 9]], 0]],
)
_r = rnd(8403)
p["tests"].append([_flat_grid(_r, 60, 60, -10 ** 9, 10 ** 9), 123456789])
_g = _flat_grid(_r, 60, 60, -20, 20)
p["tests"].append([_g, 0])
p["tests"].append([_g, 21])
p["tests"].append([_g, -20])


def b_insert(grid, target):
    return sum(1 for row in grid for v in row if v < target)


def g_insert(r):
    m, n = r.randint(1, 4), r.randint(1, 4)
    return [_flat_grid(r, m, n, -6, 6), r.randint(-8, 8)]


def v_insert(tests):
    for t in tests:
        g, target = t["args"]
        assert 1 <= len(g) <= 60 and 1 <= len(g[0]) <= 60 and abs(target) <= 10 ** 9
        flat = [v for row in g for v in row]
        assert all(len(row) == len(g[0]) for row in g) and flat == sorted(flat)
        assert all(abs(v) <= 10 ** 9 for v in flat)


CHECKS["flattened-grid-insert-position"] = (b_insert, g_insert, "exact")
VALIDATE["flattened-grid-insert-position"] = v_insert

# ---------------------------------------------------------------- MEDIUM

p = add(
    id="search-row-column-sorted-grid", title="Search a Row- and Column-Sorted Grid", diff="Medium", topic=TOPIC, tier="must",
    fn="searchSortedGrid", params=[("grid", "int[][]"), ("target", "int")], ret="bool", cmp="exact",
    desc="<p>In the <code>m x n</code> matrix <code>grid</code>, every row is sorted in non-decreasing order from left to right, and every column is sorted in non-decreasing order from top to bottom. Unlike a fully flattened sorted grid, the first value of a row may be smaller than the last value of the row above it.</p><p>Return <code>true</code> if <code>target</code> appears somewhere in the grid and <code>false</code> otherwise. Aim for O(m + n) time.</p>",
    constraints=["1 &le; m, n &le; 300", "-10<sup>9</sup> &le; grid[i][j], target &le; 10<sup>9</sup>", "Each row and each column is in non-decreasing order"],
    hints=["Binary searching every row costs O(m log n). Can the column order help you discard a whole row or column with a single comparison?",
           "Look at the top-right cell. It is the largest value in its row and the smallest value in its column. What does comparing it with the target tell you?",
           "Start at the top-right. If the cell equals the target, return true. If it is larger than the target, the whole column below it is even larger, so drop the column (move left). If it is smaller, the whole row to its left is smaller, so drop the row (move down)."],
    editorial=["A corner where one direction increases and the other decreases is the right place to start. At the top-right cell <code>(row, col)</code> the value is the maximum of its row and the minimum of its column.",
               "If it equals the target we are done. If it is greater than the target, every cell below it in the column is at least as large, so the column cannot contain the target and we move left. If it is smaller than the target, every cell to its left in the row is at most as small, so the row cannot contain the target and we move down. Each step discards a full row or column.",
               "The pointer moves left at most n times and down at most m times, giving O(m + n) time and O(1) space. The bottom-left corner works symmetrically. Starting from the top-left or bottom-right does not work, because there both directions increase (or both decrease) and a comparison cannot rule anything out."],
    time="O(m + n)", space="O(1)",
    solution='''def searchSortedGrid(grid, target):
    m, n = len(grid), len(grid[0])
    row, col = 0, n - 1
    while row < m and col >= 0:
        v = grid[row][col]
        if v == target:
            return True
        if v > target:
            col -= 1
        else:
            row += 1
    return False
''',
    tests=[[[[1, 4, 7, 11, 15], [2, 5, 8, 12, 19], [3, 6, 9, 16, 22], [10, 13, 14, 17, 24], [18, 21, 23, 26, 30]], 5],
           [[[1, 4, 7, 11, 15], [2, 5, 8, 12, 19], [3, 6, 9, 16, 22], [10, 13, 14, 17, 24], [18, 21, 23, 26, 30]], 20],
           [[[5]], 5], [[[5]], 6], [[[1, 2, 3, 4, 5]], 4], [[[1], [3], [5]], 2], [[[1, 3], [2, 4]], 0], [[[1, 3], [2, 4]], 5],
           [[[-5, -3], [-4, 0]], -4], [[[2, 2, 2], [2, 2, 2]], 2], [[[2, 2, 2], [2, 2, 2]], 3], [[[INT_MIN, 0], [0, INT_MAX]], INT_MAX]],
)
_r = rnd(8404)
_g = _mono_grid(_r, 60, 60, -10 ** 9, 10 ** 9)
p["tests"].append([_g, _g[37][22]])
p["tests"].append([_g, _g[37][22] + 1])
_g = _mono_grid(_r, 60, 60, -40, 40)
p["tests"].append([_g, 0])
p["tests"].append([_g, 41])
_g = _mono_grid(_r, 1, 60, -100, 100)
p["tests"].append([_g, _g[0][-1]])
_g = _mono_grid(_r, 60, 1, -100, 100)
p["tests"].append([_g, _g[0][0]])


def b_search(grid, target):
    return any(v == target for row in grid for v in row)


def g_search(r):
    return [_mono_grid(r, r.randint(1, 5), r.randint(1, 5), -8, 8), r.randint(-9, 9)]


def v_search(tests):
    for t in tests:
        g, target = t["args"]
        assert 1 <= len(g) <= 300 and 1 <= len(g[0]) <= 300 and _is_mono(g)
        assert abs(target) <= 10 ** 9 and all(abs(v) <= 10 ** 9 for row in g for v in row)
    assert any(t["expected"] for t in tests) and not all(t["expected"] for t in tests)


CHECKS["search-row-column-sorted-grid"] = (b_search, g_search, "exact")
VALIDATE["search-row-column-sorted-grid"] = v_search

p = add(
    id="count-cells-up-to-value-queries", title="Count Cells Up to a Value, Many Queries", diff="Medium", topic=TOPIC, tier="common",
    fn="countCellsAtMost", params=[("grid", "int[][]"), ("queries", "int[]")], ret="int[]", cmp="exact",
    desc="<p>In the <code>m x n</code> matrix <code>grid</code>, every row and every column is sorted in non-decreasing order. Values may repeat.</p><p>For each value <code>q</code> in <code>queries</code> (in order), count how many cells of <code>grid</code> hold a value less than or equal to <code>q</code>. Return the list of counts, one per query. Each query should be answered without looking at every cell.</p>",
    constraints=["1 &le; m, n &le; 60", "1 &le; queries.length &le; 3,000", "-10<sup>9</sup> &le; grid[i][j], queries[i] &le; 10<sup>9</sup>", "Each row and each column is in non-decreasing order"],
    hints=["A single query can be answered by counting in each row separately: in a sorted row, the cells &le; q form a prefix, whose length a binary search finds.",
           "The columns are sorted too, so the length of that prefix can only shrink as you move down the rows. You can walk one pointer instead of searching each row.",
           "Start in the bottom-left corner. If the current cell is greater than <code>q</code>, move up. Otherwise the cells above it in this column are all &le; q: add <code>row + 1</code> and move right. Repeat until you leave the grid; this is O(m + n) per query."],
    editorial=["Fix one query <code>q</code>. The cells with value &le; q form a 'staircase' region anchored at the top-left corner, because both rows and columns are sorted. Counting its cells means finding, for each column, how many cells from the top are &le; q.",
               "Walk the boundary of that region from the bottom-left corner. If <code>grid[row][col] &gt; q</code>, this cell and everything below it in the column are too big, so move up. Otherwise this cell and everything above it in the column are &le; q, so add <code>row + 1</code> to the answer and move right to the next column. The walk moves up at most m times and right at most n times, so a query costs O(m + n).",
               "Total cost is O(Q * (m + n)). Binary searching every row instead gives O(Q * m log n), which is also acceptable but slower for tall grids. This 'count the cells not exceeding a value' routine is exactly the counting step used by the k-th smallest in a sorted matrix binary search."],
    time="O(Q (m + n))", space="O(1)",
    solution='''def countCellsAtMost(grid, queries):
    m, n = len(grid), len(grid[0])
    out = []
    for q in queries:
        row, col, total = m - 1, 0, 0
        while row >= 0 and col < n:
            if grid[row][col] > q:
                row -= 1
            else:
                total += row + 1
                col += 1
        out.append(total)
    return out
''',
    tests=[[[[1, 5, 9], [10, 11, 13], [12, 13, 15]], [0, 1, 11, 12, 13, 15, 16]], [[[7]], [6, 7, 8]], [[[1, 2, 3]], [0, 2, 3]],
           [[[1], [2], [2], [4]], [2, 3, 5]], [[[2, 2], [2, 2]], [1, 2, 3]], [[[-3, 0], [-1, 4]], [-3, -2, -1, 0, 3, 4]],
           [[[1, 3, 5], [2, 4, 6], [3, 5, 7]], [3, 4, 5]], [[[INT_MIN, 0], [0, INT_MAX]], [INT_MIN, -1, 0, INT_MAX]]],
)
_r = rnd(8405)
_g = _mono_grid(_r, 60, 60, -100, 100)
p["tests"].append([_g, [_r.randint(-120, 120) for _ in range(2500)]])
_g = _mono_grid(_r, 60, 60, -10 ** 9, 10 ** 9)
p["tests"].append([_g, [_g[0][0], _g[-1][-1], _g[0][0] - 1] + [_r.randint(-10 ** 9, 10 ** 9) for _ in range(1500)]])
_g = _mono_grid(_r, 30, 60, 0, 5)
p["tests"].append([_g, [_r.randint(-1, 6) for _ in range(1000)]])
p["tests"].append([[[4] * 60 for _ in range(60)], [3, 4, 5]])


def b_rank(grid, queries):
    return [sum(1 for row in grid for v in row if v <= q) for q in queries]


def g_rank(r):
    return [_mono_grid(r, r.randint(1, 5), r.randint(1, 5), -6, 6), [r.randint(-8, 8) for _ in range(r.randint(1, 6))]]


def v_rank(tests):
    for t in tests:
        g, qs = t["args"]
        assert 1 <= len(g) <= 60 and 1 <= len(g[0]) <= 60 and _is_mono(g)
        assert 1 <= len(qs) <= 3000 and all(abs(q) <= 10 ** 9 for q in qs)
        assert all(abs(v) <= 10 ** 9 for row in g for v in row)


CHECKS["count-cells-up-to-value-queries"] = (b_rank, g_rank, "exact")
VALIDATE["count-cells-up-to-value-queries"] = v_rank

p = add(
    id="smallest-square-always-containing-a-one", title="Smallest Square That Always Contains a One", diff="Medium", topic=TOPIC, tier="extra",
    fn="smallestHittingSquare", params=[("grid", "int[][]")], ret="int", cmp="exact",
    desc="<p>The <code>m x n</code> matrix <code>grid</code> contains only <code>0</code> and <code>1</code>. For a side length <code>s</code>, look at every <code>s x s</code> square of consecutive cells that lies completely inside the grid. Call <code>s</code> <em>safe</em> if every one of those squares contains at least one <code>1</code>.</p><p>Return the smallest safe side length <code>s</code> (with <code>1 &le; s &le; min(m, n)</code>), or <code>-1</code> if no side length is safe.</p><pre>grid = [[1, 0, 0, 1],\n        [0, 0, 0, 0],\n        [0, 1, 0, 0],\n        [0, 0, 0, 1]]\ns = 1: the cell at row 0, column 1 is a 0 -> not safe\ns = 2: rows 0-1, columns 1-2 are all 0 -> not safe\ns = 3: all four 3 x 3 squares hold a 1 -> safe\nresult = 3</pre>",
    constraints=["1 &le; m, n &le; 60", "grid[i][j] is 0 or 1"],
    hints=["Checking one fixed side length <code>s</code> means testing every s x s square for 'contains a 1'. How can you count the ones of a square in O(1)?",
           "If every s x s square contains a 1, then every (s+1) x (s+1) square does too, because it contains an s x s square. So 'safe' flips from false to true exactly once as s grows.",
           "Build 2-D prefix sums, write <code>safe(s)</code> as 'every s x s square has sum &ge; 1', and binary search the smallest safe <code>s</code> in <code>[1, min(m, n)]</code>. If <code>min(m, n)</code> itself is not safe, return -1."],
    editorial=["Let <code>safe(s)</code> be 'every s x s square inside the grid contains a 1'. Any (s+1) x (s+1) square contains an s x s square, so if <code>safe(s)</code> holds then <code>safe(s+1)</code> holds as well. The safe lengths therefore form a suffix of <code>1..min(m, n)</code>, and we want the first one.",
               "With a prefix-sum table <code>P</code> the number of ones in the square with top-left corner <code>(i, j)</code> and side <code>s</code> is <code>P[i+s][j+s] - P[i][j+s] - P[i+s][j] + P[i][j]</code>, so one call of <code>safe(s)</code> costs O(m n). First test <code>safe(min(m, n))</code>; if even that fails the answer is -1 (this happens for example when the grid has no 1 at all, or when a non-square grid has an empty largest square). Otherwise binary search the smallest safe s.",
               "The total time is O(m n log min(m, n)) and the space is O(m n) for the prefix table. A linear scan over s would cost an extra factor of min(m, n)."],
    time="O(m n log(min(m,n)))", space="O(m n)",
    solution='''def smallestHittingSquare(grid):
    m, n = len(grid), len(grid[0])
    P = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(m):
        for j in range(n):
            P[i + 1][j + 1] = P[i][j + 1] + P[i + 1][j] - P[i][j] + grid[i][j]

    def safe(s):
        for i in range(m - s + 1):
            for j in range(n - s + 1):
                if P[i + s][j + s] - P[i][j + s] - P[i + s][j] + P[i][j] == 0:
                    return False
        return True

    hi = min(m, n)
    if not safe(hi):
        return -1
    lo = 1
    while lo < hi:
        mid = (lo + hi) // 2
        if safe(mid):
            hi = mid
        else:
            lo = mid + 1
    return lo
''',
    tests=[[[[1, 0, 0, 1], [0, 0, 0, 0], [0, 1, 0, 0], [0, 0, 0, 1]]], [[[1]]], [[[0]]], [[[1, 0, 1, 0, 1]]], [[[1, 0], [0, 0]]],
           [[[0, 0], [0, 0]]], [[[1, 1, 1], [1, 1, 1]]], [[[0, 1, 0, 0], [0, 0, 0, 1], [1, 0, 0, 0], [0, 0, 1, 0]]],
           [[[1, 0, 0], [0, 0, 0], [0, 0, 1]]], [[[0], [1], [0]]], [[[1, 0, 0, 0, 0], [0, 0, 0, 0, 1]]]],
)
_r = rnd(8410)


def _lattice(m, n, d, a, b):
    return [[1 if i % d == a and j % d == b else 0 for j in range(n)] for i in range(m)]


p["tests"].append([_lattice(60, 60, 7, 3, 5)])                      # exactly one 1 in every 7 x 7 square -> 7
_g = _lattice(60, 60, 9, 0, 0)
_g[27][36] = 0                                                      # punch one hole in the lattice
p["tests"].append([_g])
p["tests"].append([[[1 if _r.random() < 0.08 else 0 for _ in range(60)] for _ in range(60)]])
p["tests"].append([[[1 if _r.random() < 0.002 else 0 for _ in range(60)] for _ in range(60)]])
p["tests"].append([[[1 if _r.random() < 0.3 else 0 for _ in range(60)] for _ in range(37)]])


def b_hit(grid):
    m, n = len(grid), len(grid[0])
    for s in range(1, min(m, n) + 1):
        if all(any(grid[i + a][j + b] for a in range(s) for b in range(s))
               for i in range(m - s + 1) for j in range(n - s + 1)):
            return s
    return -1


def g_hit(r):
    m, n = r.randint(1, 7), r.randint(1, 7)
    pr = r.choice([0.05, 0.15, 0.3, 0.6])
    return [[[1 if r.random() < pr else 0 for _ in range(n)] for _ in range(m)]]


def v_hit(tests):
    for t in tests:
        g = t["args"][0]
        assert 1 <= len(g) <= 60 and 1 <= len(g[0]) <= 60
        assert all(len(row) == len(g[0]) and all(v in (0, 1) for v in row) for row in g)
    res = [t["expected"] for t in tests]
    assert -1 in res and any(x > 1 for x in res) and 1 in res


CHECKS["smallest-square-always-containing-a-one"] = (b_hit, g_hit, "exact")
VALIDATE["smallest-square-always-containing-a-one"] = v_hit


p = add(
    id="closest-value-in-sorted-grid", title="Closest Value in a Sorted Grid", diff="Medium", topic=TOPIC, tier="extra",
    fn="closestInGrid", params=[("grid", "int[][]"), ("target", "int")], ret="int", cmp="exact",
    desc="<p>In the <code>m x n</code> matrix <code>grid</code>, every row and every column is sorted in non-decreasing order. Return the value stored in the grid that is closest to <code>target</code> (smallest absolute difference). If two different values are equally close, return the smaller one.</p><p>Try to look at only O(m + n) cells.</p>",
    constraints=["1 &le; m, n &le; 300", "-10<sup>9</sup> &le; grid[i][j], target &le; 10<sup>9</sup>", "Each row and each column is in non-decreasing order"],
    hints=["The closest value is either the largest value &le; target (the floor) or the smallest value &ge; target (the ceiling). Binary searching each row for both gives O(m log n).",
           "To use the column order as well, run the usual row-and-column search for the target from the top-right corner, but do not stop when you do not find it.",
           "Walk from the top-right: if the cell is greater than the target move left, otherwise move down. Compare <i>every</i> visited cell with the target and remember the best (ties go to the smaller value). The floor and the ceiling are always among the visited cells."],
    editorial=["Whatever the target is, the answer is its floor (largest grid value &le; target) or its ceiling (smallest grid value &gt; target), whichever is nearer, preferring the smaller on a tie. So the task is to find the floor and the ceiling in a row- and column-sorted grid.",
               "Run the top-right staircase walk: move left when the cell exceeds the target, move down when it does not. Claim: the walk visits a cell holding the floor and a cell holding the ceiling. For the floor, suppose its cell is <code>(i, j)</code> but the walk left row <code>i</code> by moving down from some column <code>j' &gt; j</code>; then <code>grid[i][j'] &ge; grid[i][j]</code> and is still &le; target, so it also holds the floor value. A symmetric argument works for the ceiling, using the left move out of column <code>j</code>.",
               "So it is enough to compare every visited cell with the target and keep the best one. The walk makes at most m + n steps: O(m + n) time, O(1) space. Remember the tie rule: when two candidates are equally distant, the smaller value wins."],
    time="O(m + n)", space="O(1)",
    solution='''def closestInGrid(grid, target):
    m, n = len(grid), len(grid[0])
    row, col = 0, n - 1
    best = grid[0][n - 1]
    while row < m and col >= 0:
        v = grid[row][col]
        if abs(v - target) < abs(best - target) or (abs(v - target) == abs(best - target) and v < best):
            best = v
        if v == target:
            return v
        if v > target:
            col -= 1
        else:
            row += 1
    return best
''',
    tests=[[[[1, 4, 7], [3, 6, 9], [5, 8, 11]], 5], [[[1, 4, 7], [3, 6, 9], [5, 8, 11]], 10], [[[1, 4, 7], [3, 6, 9], [5, 8, 11]], 100],
           [[[1, 4, 7], [3, 6, 9], [5, 8, 11]], -100], [[[7]], 3], [[[1, 3, 5, 7, 9]], 6], [[[2], [4], [8]], 6], [[[2], [4], [8]], 7],
           [[[5, 5], [5, 5]], 9], [[[-8, -2], [-5, 4]], -3], [[[INT_MIN, 0], [0, INT_MAX]], 1], [[[INT_MIN, 0], [0, INT_MAX]], -1]],
)
_r = rnd(8407)
_g = _mono_grid(_r, 60, 60, -10 ** 9, 10 ** 9)
p["tests"].append([_g, 12345678])
p["tests"].append([_g, -987654321])
_g = _mono_grid(_r, 60, 60, -300, 300)
p["tests"].append([_g, 77])
p["tests"].append([_g, 301])
p["tests"].append([_mono_grid(_r, 60, 60, 0, 1000000), 500001])


def b_closest(grid, target):
    return min((abs(v - target), v) for row in grid for v in row)[1]


def g_closest(r):
    return [_mono_grid(r, r.randint(1, 5), r.randint(1, 5), -9, 9), r.randint(-12, 12)]


def v_closest(tests):
    for t in tests:
        g, target = t["args"]
        assert 1 <= len(g) <= 300 and 1 <= len(g[0]) <= 300 and _is_mono(g) and abs(target) <= 10 ** 9
        assert all(abs(v) <= 10 ** 9 for row in g for v in row)


CHECKS["closest-value-in-sorted-grid"] = (b_closest, g_closest, "exact")
VALIDATE["closest-value-in-sorted-grid"] = v_closest

p = add(
    id="kth-smallest-in-ragged-sorted-rows", title="Kth Smallest in Ragged Sorted Rows", diff="Medium", topic=TOPIC, tier="extra",
    fn="kthInRows", params=[("rows", "int[][]"), ("k", "int")], ret="int", cmp="exact",
    desc="<p><code>rows</code> is a list of integer lists that may have different lengths (each has at least one element). Every individual list is sorted in non-decreasing order, but nothing is promised between different lists. Values may repeat.</p><p>Imagine all values from all lists poured into one sorted sequence (duplicates count separately). Return the <code>k</code>-th smallest value, where <code>k = 1</code> is the smallest.</p>",
    constraints=["1 &le; rows.length &le; 200", "1 &le; rows[i].length &le; 200 and the total number of values is at most 6,000", "-10<sup>9</sup> &le; rows[i][j] &le; 10<sup>9</sup>", "1 &le; k &le; total number of values", "Each rows[i] is in non-decreasing order"],
    hints=["Sorting everything works in O(N log N) for N values, but the sorted rows are not being used.",
           "Think about the reverse question: for a number <code>x</code>, how many values are &le; x? In a sorted row that is one binary search.",
           "The k-th smallest is the smallest <code>x</code> in <code>[min of row starts, max of row ends]</code> whose count of values &le; x is at least k. Binary search on <code>x</code>, and count with <code>bisect_right</code> in every row."],
    editorial=["Let <code>count(x)</code> be the number of values &le; x over all lists; it is non-decreasing in x. The k-th smallest value is the smallest x with <code>count(x) &ge; k</code>: at that x the count first reaches k, which can only happen at a value that actually occurs, and duplicates are handled because they all raise the count together.",
               "Computing <code>count(x)</code> takes one <code>bisect_right</code> per list, O(R log L) for R lists of length up to L. The value range is about 2 * 10<sup>9</sup>, so the outer binary search needs about 31 iterations: O(R log L log V) in total, with O(1) extra space.",
               "A k-way merge with a heap also works, at O(k log R). The value-space search is preferable when k is large, and it is the same idea as the 'median of a row-sorted matrix' problem."],
    time="O(R log L log V)", space="O(1)",
    solution='''from bisect import bisect_right


def kthInRows(rows, k):
    lo = min(r[0] for r in rows)
    hi = max(r[-1] for r in rows)
    while lo < hi:
        mid = (lo + hi) // 2
        cnt = 0
        for r in rows:
            cnt += bisect_right(r, mid)
        if cnt >= k:
            hi = mid
        else:
            lo = mid + 1
    return lo
''',
    tests=[[[[1, 5, 9], [2, 6], [3, 4, 7, 8]], 1], [[[1, 5, 9], [2, 6], [3, 4, 7, 8]], 5], [[[1, 5, 9], [2, 6], [3, 4, 7, 8]], 9],
           [[[7]], 1], [[[2, 2, 2], [2, 2]], 4], [[[1, 1, 2], [1, 2, 2]], 3], [[[1, 1, 2], [1, 2, 2]], 4], [[[-5, 0, 5]], 2],
           [[[10], [1], [5], [3]], 3], [[[INT_MIN, 0], [INT_MAX], [-1, 1]], 3], [[[1, 2, 3, 4, 5, 6, 7, 8], [100]], 9]],
)
_r = rnd(8408)
_rows = [sorted(_r.randint(-10 ** 9, 10 ** 9) for _ in range(_r.randint(1, 60))) for _ in range(100)]
_tot = sum(len(x) for x in _rows)
p["tests"].append([_rows, _tot // 2])
p["tests"].append([_rows, _tot])
p["tests"].append([_rows, 1])
_rows = [sorted(_r.randint(0, 20) for _ in range(_r.randint(1, 50))) for _ in range(120)]
p["tests"].append([_rows, sum(len(x) for x in _rows) // 3])
_rows = [[_r.randint(0, 5)] * _r.randint(1, 40) for _ in range(150)]
p["tests"].append([_rows, sum(len(x) for x in _rows) // 2 + 1])


def b_kth_rows(rows, k):
    return sorted(v for r in rows for v in r)[k - 1]


def g_kth_rows(r):
    rows = [sorted(r.randint(-5, 5) for _ in range(r.randint(1, 5))) for _ in range(r.randint(1, 4))]
    return [rows, r.randint(1, sum(len(x) for x in rows))]


def v_kth_rows(tests):
    for t in tests:
        rows, k = t["args"]
        tot = sum(len(x) for x in rows)
        assert 1 <= len(rows) <= 200 and 1 <= tot <= 6000 and 1 <= k <= tot
        for x in rows:
            assert 1 <= len(x) <= 200 and x == sorted(x) and all(abs(v) <= 10 ** 9 for v in x)


CHECKS["kth-smallest-in-ragged-sorted-rows"] = (b_kth_rows, g_kth_rows, "exact")
VALIDATE["kth-smallest-in-ragged-sorted-rows"] = v_kth_rows

p = add(
    id="path-with-maximum-minimum-value", title="Path With the Largest Smallest Cell", diff="Medium", topic=TOPIC, tier="extra",
    fn="maxMinPath", params=[("grid", "int[][]")], ret="int", cmp="exact",
    desc="<p>You stand on the top-left cell of the <code>m x n</code> matrix <code>grid</code> and want to reach the bottom-right cell, moving one step up, down, left or right at a time. The <em>score</em> of a path is the smallest value among all cells it visits, including the first and the last cell.</p><p>Return the largest score any path from the top-left to the bottom-right cell can achieve.</p><pre>grid = [[5, 4, 5],\n        [1, 2, 6],\n        [7, 4, 6]]\npath 5 -> 4 -> 5 -> 6 -> 6 has score 4\nno path avoids both the 4 and the 1/2 cells, so result = 4</pre>",
    constraints=["1 &le; m, n &le; 60", "0 &le; grid[i][j] &le; 10<sup>9</sup>"],
    hints=["Instead of searching for the best path directly, ask a yes/no question: for a given threshold <code>t</code>, can you reach the goal using only cells with value &ge; t?",
           "If a path exists using only cells &ge; t, the same path works for every smaller threshold, so the answer to the yes/no question is monotone in <code>t</code>. The best score is one of the values that appear in the grid.",
           "Sort the distinct values (or binary search over <code>[0, 10^9]</code>) and for each probe <code>t</code> run a BFS/DFS from the top-left cell over cells &ge; t. Find the largest <code>t</code> whose search reaches the bottom-right cell."],
    editorial=["Define <code>reach(t)</code> as 'the bottom-right cell is reachable from the top-left one using only cells with value &ge; t' (it is false right away if either end cell is below t). If a path works for t it works for every t' &lt; t, so <code>reach</code> is true for small thresholds and false for large ones. The answer is the largest t with <code>reach(t) = true</code>; it always equals some cell value, namely the smallest cell on an optimal path.",
               "Binary search over the sorted distinct cell values: each probe is one flood fill (BFS) in O(m n), and there are O(log(m n)) probes. The largest feasible value is the answer; the smaller of the two end cells always works, so a feasible value exists.",
               "Total time is O(m n log(m n)) (the sort plus the probes) and the space is O(m n). A priority queue that always expands the largest unvisited frontier cell (a Dijkstra variant) reaches the same result, and so does a union-find that adds cells from the largest value downwards until the two end cells join."],
    time="O(m n log(m n))", space="O(m n)",
    solution='''from collections import deque


def maxMinPath(grid):
    m, n = len(grid), len(grid[0])

    def reach(t):
        if grid[0][0] < t or grid[m - 1][n - 1] < t:
            return False
        seen = [[False] * n for _ in range(m)]
        seen[0][0] = True
        q = deque([(0, 0)])
        while q:
            i, j = q.popleft()
            if i == m - 1 and j == n - 1:
                return True
            for x, y in ((i + 1, j), (i - 1, j), (i, j + 1), (i, j - 1)):
                if 0 <= x < m and 0 <= y < n and not seen[x][y] and grid[x][y] >= t:
                    seen[x][y] = True
                    q.append((x, y))
        return False

    vals = sorted({v for row in grid for v in row})
    lo, hi = 0, len(vals) - 1
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if reach(vals[mid]):
            lo = mid
        else:
            hi = mid - 1
    return vals[lo]
''',
    tests=[[[[5, 4, 5], [1, 2, 6], [7, 4, 6]]], [[[3]]], [[[2, 2, 1, 2, 2, 2], [1, 2, 2, 2, 1, 2]]], [[[1, 2, 3]]], [[[4], [9], [2]]],
           [[[0, 9], [9, 0]]], [[[8, 8], [8, 8]]], [[[3, 4, 6, 3, 4], [0, 2, 1, 1, 7], [8, 8, 3, 2, 7], [3, 2, 4, 9, 8], [4, 1, 2, 0, 0], [4, 6, 5, 4, 3]]],
           [[[9, 1, 9], [9, 1, 9], [9, 9, 9]]], [[[7, 0, 7], [0, 0, 0], [7, 0, 7]]]],
)
_r = rnd(8411)
p["tests"].append([[[_r.randint(0, 10 ** 9) for _ in range(60)] for _ in range(60)]])
p["tests"].append([[[_r.randint(0, 20) for _ in range(60)] for _ in range(60)]])
_g = [[_r.randint(0, 50) for _ in range(60)] for _ in range(60)]
for _i in range(60):                                               # a winding corridor of high values with 1-cell gaps
    for _j in range(60):
        if _i % 2 == 0 or (_i % 4 == 1 and _j == 59) or (_i % 4 == 3 and _j == 0):
            _g[_i][_j] = _r.randint(900, 1000)
_g[0][0] = 1000
_g[40][33] = 777
p["tests"].append([_g])


def b_maxmin(grid):
    import heapq
    m, n = len(grid), len(grid[0])
    best = [[-1] * n for _ in range(m)]
    h = [(-grid[0][0], 0, 0)]
    while h:
        v, i, j = heapq.heappop(h)
        v = -v
        if best[i][j] >= 0:
            continue
        best[i][j] = v
        for x, y in ((i + 1, j), (i - 1, j), (i, j + 1), (i, j - 1)):
            if 0 <= x < m and 0 <= y < n and best[x][y] < 0:
                heapq.heappush(h, (-min(v, grid[x][y]), x, y))
    return best[m - 1][n - 1]


def g_maxmin(r):
    m, n = r.randint(1, 6), r.randint(1, 6)
    hi = r.choice([3, 9, 30])
    return [[[r.randint(0, hi) for _ in range(n)] for _ in range(m)]]


def v_maxmin(tests):
    for t in tests:
        g = t["args"][0]
        assert 1 <= len(g) <= 60 and 1 <= len(g[0]) <= 60
        assert all(len(row) == len(g[0]) and all(0 <= v <= 10 ** 9 for v in row) for row in g)


CHECKS["path-with-maximum-minimum-value"] = (b_maxmin, g_maxmin, "exact")
VALIDATE["path-with-maximum-minimum-value"] = v_maxmin

# ---------------------------------------------------------------- HARD

p = add(
    id="kth-smallest-sum-one-per-row", title="Kth Smallest Sum Picking One Value Per Row", diff="Hard", topic=TOPIC, tier="extra",
    fn="kthRowPickSum", params=[("mat", "int[][]"), ("k", "int")], ret="int", cmp="exact",
    desc="<p>The <code>m x n</code> matrix <code>mat</code> has rows sorted in non-decreasing order. A <em>pick</em> chooses exactly one cell from every row (one column index per row), and its sum is the total of the chosen values. Two picks that use different column indices in some row are different picks, even if their sums are equal, so there are <code>n<sup>m</sup></code> picks in total.</p><p>Sort the sums of all picks in non-decreasing order and return the <code>k</code>-th one (1-based).</p><pre>mat = [[1, 3, 11],\n       [2, 4, 6]], k = 5\nall nine sums: 3, 5, 7, 5, 7, 9, 13, 15, 17\nsorted:        3, 5, 5, 7, 7, 9, 13, 15, 17\nresult = 7</pre>",
    constraints=["1 &le; m, n &le; 40", "1 &le; mat[i][j] &le; 5,000", "Every row is sorted in non-decreasing order", "1 &le; k &le; min(200, n<sup>m</sup>)"],
    hints=["There can be 40<sup>40</sup> picks, so you cannot list them. But k is small. Which sums can possibly matter?",
           "Ask the counting question instead: how many picks have sum &le; S? It grows with S, so you can binary search the smallest S whose count reaches k. You never need the exact count above k.",
           "Count with a depth-first search over rows, choosing columns left to right and stopping a row as soon as the sum can no longer be completed within S (use the sum of every later row's first element as the cheapest completion). Quit the whole search once the count reaches k; the pruning keeps every visited node on a path to a valid pick, so at most about m * k nodes are visited."],
    editorial=["The k-th smallest sum is the smallest S such that at least k picks have sum &le; S. The number of picks with sum &le; S does not decrease when S grows, so we can binary search S between the smallest possible sum (every row's first value added up) and the largest one (every row's last value added up).",
               "To test S we count picks with sum &le; S, but only up to k. Precompute <code>rest[i]</code>, the sum of the first elements of rows <code>i..m-1</code>, the cheapest way to finish from row i. In the DFS at row i with budget b, try columns in order; since rows are sorted, stop at the first value v with <code>v + rest[i+1] &gt; b</code>. Every node we enter can be completed into at least one valid pick, so the number of visited nodes is at most m times the number of counted picks, and we abort the search as soon as k picks are found. One probe therefore costs O(m * k) steps.",
               "With about log(m * 5000) &le; 18 probes the total time is O(m k log(m * maxValue)) and the extra space is O(m) for the recursion. An alternative is to merge the rows one at a time, keeping only the k smallest partial sums with a heap, which costs O(m k log k)."],
    time="O(m k log(m V))", space="O(m)",
    solution='''import sys


def kthRowPickSum(mat, k):
    m = len(mat)
    sys.setrecursionlimit(10000)
    rest = [0] * (m + 1)
    for i in range(m - 1, -1, -1):
        rest[i] = rest[i + 1] + mat[i][0]

    def count(S):
        cnt = 0

        def dfs(i, budget):
            nonlocal cnt
            if i == m:
                cnt += 1
                return
            for v in mat[i]:
                if v + rest[i + 1] > budget:
                    break
                dfs(i + 1, budget - v)
                if cnt >= k:
                    return

        dfs(0, S)
        return cnt

    lo, hi = rest[0], sum(row[-1] for row in mat)
    while lo < hi:
        mid = (lo + hi) // 2
        if count(mid) >= k:
            hi = mid
        else:
            lo = mid + 1
    return lo
''',
    tests=[[[[1, 3, 11], [2, 4, 6]], 5], [[[1, 3, 11], [2, 4, 6]], 9], [[[1, 10, 10], [1, 4, 5], [2, 3, 6]], 7], [[[1, 1, 10], [2, 2, 2]], 1],
           [[[5]], 1], [[[1, 2, 3, 4]], 3], [[[2], [3], [4]], 1], [[[1, 1], [1, 1], [1, 1]], 8], [[[1, 2], [1, 2], [1, 2]], 4],
           [[[1, 5000], [1, 5000], [1, 5000], [1, 5000]], 16]],
)
_r = rnd(8412)
p["tests"].append([_rows_sorted(_r, 40, 40, 1, 5000), 200])
p["tests"].append([_rows_sorted(_r, 40, 40, 1, 5000), 1])
p["tests"].append([_rows_sorted(_r, 40, 40, 1, 3), 137])
p["tests"].append([[[1] * 40 for _ in range(40)], 200])
p["tests"].append([_rows_sorted(_r, 25, 2, 1, 5000), 200])


def b_pick(mat, k):
    from itertools import product
    return sorted(sum(c) for c in product(*mat))[k - 1]


def g_pick(r):
    m, n = r.randint(1, 4), r.randint(1, 4)
    mat = _rows_sorted(r, m, n, 1, r.choice([3, 8, 30]))
    return [mat, r.randint(1, min(200, n ** m))]


def v_pick(tests):
    for t in tests:
        mat, k = t["args"]
        m, n = len(mat), len(mat[0])
        assert 1 <= m <= 40 and 1 <= n <= 40
        assert all(len(row) == n and row == sorted(row) and all(1 <= v <= 5000 for v in row) for row in mat)
        assert 1 <= k <= min(200, n ** m)


CHECKS["kth-smallest-sum-one-per-row"] = (b_pick, g_pick, "exact")
VALIDATE["kth-smallest-sum-one-per-row"] = v_pick

p = add(
    id="smallest-box-around-black-pixels", title="Smallest Box Around Black Pixels", diff="Hard", topic=TOPIC, tier="extra",
    fn="minBoxArea", params=[("image", "int[][]"), ("x", "int"), ("y", "int")], ret="int", cmp="exact",
    desc="<p><code>image</code> is an <code>m x n</code> binary picture: <code>1</code> is a black pixel and <code>0</code> is a white pixel. All the black pixels are connected to each other through horizontal and vertical neighbours, so they form a single blob (there is exactly one blob and it is not empty).</p><p>You are given the position <code>(x, y)</code> (row <code>x</code>, column <code>y</code>, both 0-based) of one black pixel. Return the area (number of cells) of the smallest axis-aligned rectangle that contains all the black pixels. A solution that inspects far fewer than <code>m * n</code> cells exists.</p>",
    constraints=["1 &le; m, n &le; 60", "image[i][j] is 0 or 1", "The black pixels form exactly one connected blob (4-directional) and image[x][y] = 1"],
    hints=["Scanning the whole picture to find the extreme black rows and columns is O(m * n). Because the blob is connected, a lot more can be said about which rows and columns contain black pixels.",
           "Every row and column that contains a black pixel forms one unbroken range, and the given pixel <code>(x, y)</code> lies inside it. So going away from <code>x</code>, rows are either 'has black' and then 'all white' with no coming back.",
           "Binary search each of the four borders: the first column in <code>[0, y]</code> containing a black pixel, the last in <code>[y, n-1]</code>, and likewise for rows with <code>[0, x]</code> and <code>[x, m-1]</code>. Each probe scans one row or column. Multiply the resulting height and width."],
    editorial=["Let a column be 'occupied' if it holds at least one black pixel. The blob is connected, so the occupied columns are contiguous: if columns a &lt; c are occupied, any column between them is crossed by the path that links the two blobs parts, hence occupied too. The same holds for rows. The known pixel <code>(x, y)</code> is inside both contiguous ranges.",
               "Therefore the columns in <code>[0, y]</code> read 'white ... white, occupied ... occupied', a monotone pattern, and the left border is the first occupied column, found by binary search. The right border is the last occupied column in <code>[y, n-1]</code> (pattern 'occupied ... occupied, white ... white'); the top and bottom borders are found in the same way with rows.",
               "Each of the four searches does O(log) probes, and a probe checks one row (O(n)) or one column (O(m)), so the cost is O(m log n + n log m). The final area is <code>(bottom - top + 1) * (right - left + 1)</code>. Without the connectivity guarantee the pattern would not be monotone and binary search would fail."],
    time="O(m log n + n log m)", space="O(1)",
    solution='''def minBoxArea(image, x, y):
    m, n = len(image), len(image[0])

    def col_has(c):
        for i in range(m):
            if image[i][c]:
                return True
        return False

    def row_has(r):
        return 1 in image[r]

    lo, hi = 0, y
    while lo < hi:
        mid = (lo + hi) // 2
        if col_has(mid):
            hi = mid
        else:
            lo = mid + 1
    left = lo
    lo, hi = y, n - 1
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if col_has(mid):
            lo = mid
        else:
            hi = mid - 1
    right = lo
    lo, hi = 0, x
    while lo < hi:
        mid = (lo + hi) // 2
        if row_has(mid):
            hi = mid
        else:
            lo = mid + 1
    top = lo
    lo, hi = x, m - 1
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if row_has(mid):
            lo = mid
        else:
            hi = mid - 1
    bottom = lo
    return (bottom - top + 1) * (right - left + 1)
''',
    tests=[[[[0, 0, 1, 0], [0, 1, 1, 0], [0, 1, 0, 0]], 0, 2], [[[1]], 0, 0], [[[0, 1, 0]], 0, 1], [[[0], [1], [1], [0]], 2, 0],
           [[[1, 1], [1, 1]], 1, 0], [[[0, 0, 0, 0], [0, 1, 1, 0], [0, 1, 1, 0], [0, 0, 0, 0]], 1, 1],
           [[[1, 1, 1], [1, 0, 1], [1, 1, 1]], 2, 1], [[[1, 0, 0, 0], [1, 1, 1, 1], [0, 0, 0, 1], [0, 0, 0, 0]], 1, 3],
           [[[0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 1], [0, 0, 0, 0, 0]], 2, 4]],
)
_r = rnd(8410)


def _blob(r, m, n, steps, walk):
    sx, sy = r.randrange(m), r.randrange(n)
    cells = [(sx, sy)]
    seen = {(sx, sy)}
    cur = (sx, sy)
    for _ in range(steps):
        base = cur if walk else r.choice(cells)
        dx, dy = r.choice([(1, 0), (-1, 0), (0, 1), (0, -1)])
        nx, ny = base[0] + dx, base[1] + dy
        if 0 <= nx < m and 0 <= ny < n:
            cur = (nx, ny)
            if cur not in seen:
                seen.add(cur)
                cells.append(cur)
    img = [[0] * n for _ in range(m)]
    for a, b in cells:
        img[a][b] = 1
    return img, r.choice(cells)


for _args in [(60, 60, 1500, True), (60, 60, 600, False), (60, 60, 4000, True), (45, 60, 300, True), (60, 60, 40, True)]:
    _img, _c = _blob(_r, *_args)
    p["tests"].append([_img, _c[0], _c[1]])
# a long thin snake across the whole picture, and a solid frame with an empty inside
_img = [[0] * 60 for _ in range(60)]
for _j in range(60):
    _img[0][_j] = 1
for _i in range(60):
    _img[_i][59] = 1
p["tests"].append([_img, 30, 59])
_img = [[0] * 60 for _ in range(60)]
for _k in range(3, 57):
    _img[3][_k] = _img[56][_k] = _img[_k][3] = _img[_k][56] = 1
p["tests"].append([_img, 3, 30])


def b_box(image, x, y):
    pts = [(i, j) for i, row in enumerate(image) for j, v in enumerate(row) if v]
    return (max(a for a, _ in pts) - min(a for a, _ in pts) + 1) * (max(b for _, b in pts) - min(b for _, b in pts) + 1)


def g_box(r):
    m, n = r.randint(1, 7), r.randint(1, 7)
    img, c = _blob(r, m, n, r.randint(0, 25), r.random() < 0.5)
    return [img, c[0], c[1]]


def v_box(tests):
    for t in tests:
        img, x, y = t["args"]
        m, n = len(img), len(img[0])
        assert 1 <= m <= 60 and 1 <= n <= 60 and all(len(row) == n and all(v in (0, 1) for v in row) for row in img)
        assert 0 <= x < m and 0 <= y < n and img[x][y] == 1
        total = sum(map(sum, img))
        seen = {(x, y)}
        dq = deque([(x, y)])
        while dq:
            a, b = dq.popleft()
            for da, db in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                na, nb = a + da, b + db
                if 0 <= na < m and 0 <= nb < n and img[na][nb] and (na, nb) not in seen:
                    seen.add((na, nb))
                    dq.append((na, nb))
        assert len(seen) == total, "black pixels are not connected"


CHECKS["smallest-box-around-black-pixels"] = (b_box, g_box, "exact")
VALIDATE["smallest-box-around-black-pixels"] = v_box
