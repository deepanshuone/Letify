"""Problems: prefix sums on grids (2-D prefix sums, submatrix and block sums, counting by area). See data/lib.py for the registry."""
from lib import add, rnd, CHECKS, VALIDATE, gen_arr  # noqa: F401

T = "Prefix Sums"


# ------------------------------------------------------------------ shared helpers (tests only)
def _mat(r, R, C, lo, hi):
    return [[r.randint(lo, hi) for _ in range(C)] for _ in range(R)]


def _rect_check(m, rmax, cmax, lo, hi):
    assert 1 <= len(m) <= rmax, "rows"
    assert all(len(row) == len(m[0]) for row in m), "ragged"
    assert 1 <= len(m[0]) <= cmax, "cols"
    assert all(lo <= v <= hi for row in m for v in row), "cell range"


def _sum_rect(m, r1, c1, r2, c2):
    return sum(m[i][j] for i in range(r1, r2 + 1) for j in range(c1, c2 + 1))


# ---------------------------------------------------------------- EASY

p = add(
    id="rectangle-sum-queries-2d", title="Rectangle Sum Queries", diff="Easy", topic=T, tier="must",
    fn="rectangleSums", params=[("matrix", "int[][]"), ("queries", "int[][]")], ret="int[]", cmp="exact",
    desc="<p>You are given a rectangular grid of integers <code>matrix</code> and a list of <code>queries</code>. Each query is <code>[r1, c1, r2, c2]</code> and asks for the sum of all cells <code>matrix[i][j]</code> with <code>r1 &le; i &le; r2</code> and <code>c1 &le; j &le; c2</code> (rows and columns are 0-indexed, both ends inclusive).</p><p>Return an array with the answer to every query, in the same order as the queries.</p><pre>matrix = [[3, 0, 1, 4],\n          [5, 6, 3, 2],\n          [1, 2, 0, 1]]\nqueries = [[0, 0, 1, 1], [1, 1, 2, 3], [0, 1, 2, 1]]\nresult = [14, 14, 8]</pre>",
    constraints=["1 &le; rows, columns &le; 60", "-1,000 &le; matrix[i][j] &le; 1,000", "0 &le; queries.length &le; 2,000", "0 &le; r1 &le; r2 &lt; rows and 0 &le; c1 &le; c2 &lt; columns"],
    hints=["Adding up every cell of a rectangle for every query costs O(R * C) per query. Preparing something once could make each query cheap.",
           "In one dimension, <code>prefix[i]</code> = sum of the first <code>i</code> elements lets you answer a range in O(1). Build the same idea for the rectangle from the top-left corner to each cell.",
           "Let <code>P[i][j]</code> be the sum of the rectangle spanning rows <code>0..i-1</code> and columns <code>0..j-1</code>. A query equals <code>P[r2+1][c2+1] - P[r1][c2+1] - P[r2+1][c1] + P[r1][c1]</code> (inclusion-exclusion: the corner was subtracted twice, so add it back once)."],
    editorial=["Build a table <code>P</code> of size (R + 1) x (C + 1) where <code>P[i][j]</code> is the sum of all cells in the top-left i x j rectangle. It fills in O(R * C) with the recurrence <code>P[i][j] = matrix[i-1][j-1] + P[i-1][j] + P[i][j-1] - P[i-1][j-1]</code>; the last term removes the overlap that both neighbours include.",
               "Any rectangle is the big top-left rectangle ending at its bottom-right corner, minus the strip above it, minus the strip to its left, plus the corner rectangle that was subtracted twice. That is four table lookups, so every query is O(1).",
               "Total time is O(R * C + q) and the extra space is O(R * C). The extra row and column of zeros in <code>P</code> avoid special cases for rectangles touching the border."],
    time="O(R*C + q)", space="O(R*C)",
    solution='''def rectangleSums(matrix, queries):
    R, C = len(matrix), len(matrix[0])
    P = [[0] * (C + 1) for _ in range(R + 1)]
    for i in range(R):
        for j in range(C):
            P[i + 1][j + 1] = matrix[i][j] + P[i][j + 1] + P[i + 1][j] - P[i][j]
    out = []
    for r1, c1, r2, c2 in queries:
        out.append(P[r2 + 1][c2 + 1] - P[r1][c2 + 1] - P[r2 + 1][c1] + P[r1][c1])
    return out
''',
    tests=[[[[3, 0, 1, 4], [5, 6, 3, 2], [1, 2, 0, 1]], [[0, 0, 1, 1], [1, 1, 2, 3], [0, 1, 2, 1]]],
           [[[7]], [[0, 0, 0, 0]]],
           [[[1, 2, 3, 4, 5]], [[0, 0, 0, 4], [0, 1, 0, 3], [0, 4, 0, 4]]],
           [[[1], [2], [3], [4]], [[0, 0, 3, 0], [1, 0, 2, 0]]],
           [[[-5, 4], [3, -2]], [[0, 0, 1, 1], [0, 0, 0, 0], [1, 0, 1, 1]]],
           [[[0, 0], [0, 0]], []],
           [[[1000, -1000, 1000], [-1000, 1000, -1000], [1000, -1000, 1000]], [[0, 0, 2, 2], [1, 1, 1, 1], [0, 0, 1, 1]]]],
)
_r = rnd(9101)
_m = _mat(_r, 60, 60, -1000, 1000)
p["tests"].append([_m, [[0, 0, 59, 59]] + [(lambda a, b, c, d: [min(a, b), min(c, d), max(a, b), max(c, d)])(_r.randrange(60), _r.randrange(60), _r.randrange(60), _r.randrange(60)) for _ in range(1500)]])
_m = [[1000] * 60 for _ in range(60)]
p["tests"].append([_m, [[0, 0, 59, 59], [0, 0, 0, 0], [59, 59, 59, 59], [10, 10, 49, 49]]])
_m = _mat(_r, 3, 50, -1000, 1000)
p["tests"].append([_m, [(lambda a, b, c: [min(a, b), c, max(a, b), c + _r.randrange(50 - c)])(_r.randrange(3), _r.randrange(3), _r.randrange(50)) for _ in range(600)]])


def b_rectsum(matrix, queries):
    return [_sum_rect(matrix, *q) for q in queries]


def g_rectsum(r):
    R, C = r.randint(1, 5), r.randint(1, 5)
    qs = []
    for _ in range(r.randint(0, 6)):
        a, b, c, d = r.randrange(R), r.randrange(R), r.randrange(C), r.randrange(C)
        qs.append([min(a, b), min(c, d), max(a, b), max(c, d)])
    return [_mat(r, R, C, -9, 9), qs]


def v_rectsum(tests):
    for t in tests:
        m, qs = t["args"]
        _rect_check(m, 60, 60, -1000, 1000)
        assert len(qs) <= 2000
        for r1, c1, r2, c2 in qs:
            assert 0 <= r1 <= r2 < len(m) and 0 <= c1 <= c2 < len(m[0])


CHECKS["rectangle-sum-queries-2d"] = (b_rectsum, g_rectsum, "exact")
VALIDATE["rectangle-sum-queries-2d"] = v_rectsum

p = add(
    id="max-sum-k-by-k-block", title="Heaviest K by K Block", diff="Easy", topic=T, tier="common",
    fn="maxBlockSum", params=[("matrix", "int[][]"), ("k", "int")], ret="int", cmp="exact",
    desc="<p>A <strong>block</strong> is a square of <code>k</code> x <code>k</code> consecutive cells of the grid <code>matrix</code>. Return the largest possible sum of the cells of a block.</p><pre>matrix = [[1, 2, 3],\n          [4, 5, 6],\n          [7, 8, 9]], k = 2\nblocks: 12, 16, 24, 28\nresult = 28</pre>",
    constraints=["1 &le; rows, columns &le; 60", "-1,000 &le; matrix[i][j] &le; 1,000", "1 &le; k &le; min(rows, columns)"],
    hints=["There are at most (R - k + 1) * (C - k + 1) blocks. Summing each from scratch costs k<sup>2</sup> per block, which gets slow for large k.",
           "Neighbouring blocks overlap almost completely. A table of rectangle sums from the top-left corner lets you get any block sum in constant time.",
           "With <code>P[i][j]</code> = sum of the top-left i x j rectangle, the block with top-left cell (i, j) has sum <code>P[i+k][j+k] - P[i][j+k] - P[i+k][j] + P[i][j]</code>. Take the maximum over all positions."],
    editorial=["Build the 2-D prefix table <code>P</code> of size (R + 1) x (C + 1) once, using <code>P[i][j] = matrix[i-1][j-1] + P[i-1][j] + P[i][j-1] - P[i-1][j-1]</code>.",
               "Then slide the block over every top-left position (i, j) with <code>0 &le; i &le; R-k</code> and <code>0 &le; j &le; C-k</code>, evaluate its sum with four lookups, and keep the maximum. Time O(R * C), space O(R * C).",
               "Negative cells are fine: the maximum is taken over all blocks, so no special handling is needed. The largest possible magnitude is 3,600 * 1,000, comfortably inside 32 bits."],
    time="O(R*C)", space="O(R*C)",
    solution='''def maxBlockSum(matrix, k):
    R, C = len(matrix), len(matrix[0])
    P = [[0] * (C + 1) for _ in range(R + 1)]
    for i in range(R):
        for j in range(C):
            P[i + 1][j + 1] = matrix[i][j] + P[i][j + 1] + P[i + 1][j] - P[i][j]
    best = None
    for i in range(R - k + 1):
        for j in range(C - k + 1):
            s = P[i + k][j + k] - P[i][j + k] - P[i + k][j] + P[i][j]
            if best is None or s > best:
                best = s
    return best
''',
    tests=[[[[1, 2, 3], [4, 5, 6], [7, 8, 9]], 2], [[[5]], 1], [[[-3]], 1], [[[1, -2, 3, -4]], 1], [[[1, -2, 3, -4], [5, -6, 7, -8]], 2],
           [[[-1, -2], [-3, -4]], 1], [[[-1, -2], [-3, -4]], 2], [[[1, 2], [3, 4], [5, 6]], 2], [[[0, 0, 0], [0, 0, 0]], 2],
           [[[9, -9, 9], [-9, 9, -9], [9, -9, 9]], 3]],
)
_r = rnd(9102)
p["tests"].append([_mat(_r, 60, 60, -1000, 1000), 1])
p["tests"].append([_mat(_r, 60, 60, -1000, 1000), 17])
p["tests"].append([_mat(_r, 60, 60, -1000, 1000), 60])
p["tests"].append([_mat(_r, 40, 60, -1000, -1), 25])


def b_maxblock(matrix, k):
    R, C = len(matrix), len(matrix[0])
    return max(_sum_rect(matrix, i, j, i + k - 1, j + k - 1) for i in range(R - k + 1) for j in range(C - k + 1))


def g_maxblock(r):
    R, C = r.randint(1, 6), r.randint(1, 6)
    return [_mat(r, R, C, -9, 9), r.randint(1, min(R, C))]


def v_maxblock(tests):
    for t in tests:
        m, k = t["args"]
        _rect_check(m, 60, 60, -1000, 1000)
        assert 1 <= k <= min(len(m), len(m[0]))


CHECKS["max-sum-k-by-k-block"] = (b_maxblock, g_maxblock, "exact")
VALIDATE["max-sum-k-by-k-block"] = v_maxblock

p = add(
    id="equal-sum-grid-cuts", title="Equal-Sum Grid Cuts", diff="Easy", topic=T, tier="extra",
    fn="countEqualCuts", params=[("matrix", "int[][]")], ret="int", cmp="exact",
    desc="<p>You may cut the grid <code>matrix</code> along one straight line that runs between two neighbouring rows or between two neighbouring columns. A cut splits the grid into two non-empty parts. A cut is <strong>fair</strong> if the two parts have exactly the same sum.</p><p>Return the number of fair cuts. A horizontal cut and a vertical cut are different cuts, and different positions are different cuts.</p><pre>matrix = [[1, 2],\n          [2, 1]]\nhorizontal cut: 3 | 3  (fair)\nvertical cut:   3 | 3  (fair)\nresult = 2</pre>",
    constraints=["1 &le; rows, columns &le; 60", "-1,000 &le; matrix[i][j] &le; 1,000", "A grid with a single row has no horizontal cut; a grid with a single column has no vertical cut"],
    hints=["If the top part has sum <code>s</code>, what must the sum of the bottom part be for the cut to be fair?",
           "A cut is fair exactly when the part on one side is half of the total sum. Compute the total first.",
           "Compute the sum of every row and every column. A horizontal cut after row <code>i</code> is fair if the prefix sum of row sums equals <code>total - prefix</code>; do the same with column sums for vertical cuts."],
    editorial=["Let <code>total</code> be the sum of all cells. A cut leaves a top part (or left part) with sum <code>s</code> and a remaining part with sum <code>total - s</code>, so the cut is fair if and only if <code>2 * s == total</code>.",
               "For horizontal cuts, walk through the rows keeping the running sum of row sums; every position between row <code>i</code> and row <code>i + 1</code> (for <code>i</code> from 0 to R-2) is tested. Vertical cuts work the same on column sums. This is a one-dimensional prefix sum on the margins of the grid.",
               "With negative values or zeros, several cuts of the same direction may all be fair, which is why the answer is a count. Time O(R * C), space O(R + C)."],
    time="O(R*C)", space="O(R+C)",
    solution='''def countEqualCuts(matrix):
    R, C = len(matrix), len(matrix[0])
    rows = [sum(row) for row in matrix]
    cols = [sum(matrix[i][j] for i in range(R)) for j in range(C)]
    total = sum(rows)
    count = 0
    run = 0
    for i in range(R - 1):
        run += rows[i]
        if 2 * run == total:
            count += 1
    run = 0
    for j in range(C - 1):
        run += cols[j]
        if 2 * run == total:
            count += 1
    return count
''',
    tests=[[[[1, 2], [2, 1]]], [[[5]]], [[[1, 0, 1]]], [[[1], [0], [1]]], [[[0, 0], [0, 0]]], [[[1, 2], [3, 4]]],
           [[[3, -1, 1], [2, 0, -2], [1, 1, 0]]], [[[0, 0, 0, 0]]], [[[2, -2], [-2, 2], [5, 5]]]],
)
_r = rnd(9103)
p["tests"].append([[[0] * 60 for _ in range(60)]])
p["tests"].append([[[1] * 60 for _ in range(60)]])
_m = _mat(_r, 60, 60, -3, 3)
p["tests"].append([_m])
_m = [[_r.choice([-1, 0, 1]) for _ in range(60)] for _ in range(60)]
p["tests"].append([_m])


def b_cuts(matrix):
    R, C = len(matrix), len(matrix[0])
    tot = _sum_rect(matrix, 0, 0, R - 1, C - 1)
    cnt = 0
    for i in range(1, R):
        if _sum_rect(matrix, 0, 0, i - 1, C - 1) == tot - _sum_rect(matrix, 0, 0, i - 1, C - 1):
            cnt += 1
    for j in range(1, C):
        if _sum_rect(matrix, 0, 0, R - 1, j - 1) == tot - _sum_rect(matrix, 0, 0, R - 1, j - 1):
            cnt += 1
    return cnt


def g_cuts(r):
    R, C = r.randint(1, 5), r.randint(1, 5)
    return [_mat(r, R, C, -1, 2)]


def v_cuts(tests):
    for t in tests:
        _rect_check(t["args"][0], 60, 60, -1000, 1000)


CHECKS["equal-sum-grid-cuts"] = (b_cuts, g_cuts, "exact")
VALIDATE["equal-sum-grid-cuts"] = v_cuts

# ---------------------------------------------------------------- MEDIUM

p = add(
    id="neighborhood-block-sums", title="Neighborhood Block Sums", diff="Medium", topic=T, tier="common",
    fn="blockSums", params=[("matrix", "int[][]"), ("k", "int")], ret="int[][]", cmp="exact",
    desc="<p>Given a grid <code>matrix</code> and a radius <code>k</code>, build a grid <code>answer</code> of the same shape where <code>answer[i][j]</code> is the sum of all cells <code>matrix[r][c]</code> with <code>|r - i| &le; k</code> and <code>|c - j| &le; k</code>. Cells that fall outside the grid are simply ignored, so near the border the neighbourhood is smaller.</p><pre>matrix = [[1, 2, 3],\n          [4, 5, 6],\n          [7, 8, 9]], k = 1\nanswer = [[12, 21, 16],\n          [27, 45, 33],\n          [24, 39, 28]]</pre>",
    constraints=["1 &le; rows, columns &le; 60", "0 &le; k &le; 100", "-100 &le; matrix[i][j] &le; 100"],
    hints=["Summing the (2k + 1) x (2k + 1) square around every cell costs up to R * C * k<sup>2</sup>, which is too slow for large k.",
           "Each answer cell is the sum of a rectangle. A 2-D prefix table gives any rectangle sum in O(1).",
           "Clamp the rectangle to the grid: rows <code>max(0, i-k)..min(R-1, i+k)</code> and columns <code>max(0, j-k)..min(C-1, j+k)</code>, then evaluate it with the four-term prefix formula."],
    editorial=["Build the prefix table <code>P</code> of size (R + 1) x (C + 1) where <code>P[i][j]</code> is the sum of the top-left i x j block. For each cell (i, j) the neighbourhood is the rectangle with corners <code>(r1, c1) = (max(0, i-k), max(0, j-k))</code> and <code>(r2, c2) = (min(R-1, i+k), min(C-1, j+k))</code>.",
               "Its sum is <code>P[r2+1][c2+1] - P[r1][c2+1] - P[r2+1][c1] + P[r1][c1]</code>. The clamping handles the border automatically and k larger than the grid just means the whole grid.",
               "Time O(R * C), independent of k, and O(R * C) space for the table and the output."],
    time="O(R*C)", space="O(R*C)",
    solution='''def blockSums(matrix, k):
    R, C = len(matrix), len(matrix[0])
    P = [[0] * (C + 1) for _ in range(R + 1)]
    for i in range(R):
        for j in range(C):
            P[i + 1][j + 1] = matrix[i][j] + P[i][j + 1] + P[i + 1][j] - P[i][j]
    out = []
    for i in range(R):
        r1, r2 = max(0, i - k), min(R - 1, i + k)
        row = []
        for j in range(C):
            c1, c2 = max(0, j - k), min(C - 1, j + k)
            row.append(P[r2 + 1][c2 + 1] - P[r1][c2 + 1] - P[r2 + 1][c1] + P[r1][c1])
        out.append(row)
    return out
''',
    tests=[[[[1, 2, 3], [4, 5, 6], [7, 8, 9]], 1], [[[1, 2, 3], [4, 5, 6], [7, 8, 9]], 0], [[[1, 2, 3], [4, 5, 6], [7, 8, 9]], 2],
           [[[4]], 3], [[[1, -1, 1, -1, 1]], 1], [[[1], [-2], [3], [-4]], 2], [[[-5, 5], [5, -5]], 1],
           [[[100, -100, 100], [-100, 100, -100]], 100], [[[1, 2], [3, 4], [5, 6], [7, 8]], 1]],
)
_r = rnd(9104)
p["tests"].append([_mat(_r, 60, 60, -100, 100), 5])
p["tests"].append([_mat(_r, 60, 60, -100, 100), 100])
p["tests"].append([_mat(_r, 45, 60, -100, 100), 0])


def b_blocksum(matrix, k):
    R, C = len(matrix), len(matrix[0])
    return [[_sum_rect(matrix, max(0, i - k), max(0, j - k), min(R - 1, i + k), min(C - 1, j + k)) for j in range(C)] for i in range(R)]


def g_blocksum(r):
    R, C = r.randint(1, 6), r.randint(1, 6)
    return [_mat(r, R, C, -9, 9), r.randint(0, 5)]


def v_blocksum(tests):
    for t in tests:
        m, k = t["args"]
        _rect_check(m, 60, 60, -100, 100)
        assert 0 <= k <= 100


CHECKS["neighborhood-block-sums"] = (b_blocksum, g_blocksum, "exact")
VALIDATE["neighborhood-block-sums"] = v_blocksum

p = add(
    id="count-fixed-area-rectangles-under-limit", title="Count Fixed-Area Rectangles Under a Limit", diff="Medium", topic=T, tier="extra",
    fn="countRectanglesByArea", params=[("matrix", "int[][]"), ("area", "int"), ("limit", "int")], ret="int", cmp="exact",
    desc="<p>Count the rectangular blocks of the grid <code>matrix</code> that contain exactly <code>area</code> cells and whose cell sum is at most <code>limit</code>.</p><p>A block is a set of consecutive rows and consecutive columns. A block of height <code>h</code> and width <code>w</code> has area <code>h * w</code>; shapes <code>h x w</code> and <code>w x h</code> are different shapes (if <code>h != w</code>), and blocks at different positions are counted separately.</p><pre>matrix = [[1, 2, 3],\n          [4, 5, 6]], area = 2, limit = 5\n1 x 2 blocks with sum &le; 5: [1, 2] = 3, [2, 3] = 5\n2 x 1 blocks with sum &le; 5: [1, 4] = 5\nresult = 3</pre>",
    constraints=["1 &le; rows, columns &le; 60", "-50 &le; matrix[i][j] &le; 50", "1 &le; area &le; 3,600", "-1,000,000 &le; limit &le; 1,000,000"],
    hints=["Only shapes <code>h x w</code> with <code>h * w = area</code> matter. How many such shapes can there be?",
           "The number of divisors of <code>area</code> is small (at most a few dozen), and each shape must also fit inside the grid.",
           "For every valid shape, slide it over all positions and read each block sum from a 2-D prefix table in O(1). Count the positions with sum &le; limit."],
    editorial=["List the shapes: every divisor <code>h</code> of <code>area</code> with <code>h &le; R</code> and <code>area / h &le; C</code> gives one shape <code>(h, area / h)</code>. Since the heights differ, no shape is counted twice (a square shape appears once).",
               "Build the usual 2-D prefix table <code>P</code>. For a shape (h, w) every top-left corner (i, j) with <code>i + h &le; R</code> and <code>j + w &le; C</code> gives a block sum <code>P[i+h][j+w] - P[i][j+w] - P[i+h][j] + P[i][j]</code>. Count those that do not exceed <code>limit</code>.",
               "A grid has at most 3,600 positions and an integer up to 3,600 has at most 60 divisors, but only divisors that fit in the grid matter, so the work is O(R * C * d) with a small d. Without the prefix table each block would cost <code>area</code> extra steps."],
    time="O(R*C*d)", space="O(R*C)",
    solution='''def countRectanglesByArea(matrix, area, limit):
    R, C = len(matrix), len(matrix[0])
    P = [[0] * (C + 1) for _ in range(R + 1)]
    for i in range(R):
        for j in range(C):
            P[i + 1][j + 1] = matrix[i][j] + P[i][j + 1] + P[i + 1][j] - P[i][j]
    count = 0
    for h in range(1, R + 1):
        if area % h:
            continue
        w = area // h
        if w > C:
            continue
        for i in range(R - h + 1):
            for j in range(C - w + 1):
                if P[i + h][j + w] - P[i][j + w] - P[i + h][j] + P[i][j] <= limit:
                    count += 1
    return count
''',
    tests=[[[[1, 2, 3], [4, 5, 6]], 2, 5], [[[1, 2, 3], [4, 5, 6]], 1, 3], [[[1, 2, 3], [4, 5, 6]], 6, 21], [[[1, 2, 3], [4, 5, 6]], 6, 20],
           [[[1, 2, 3], [4, 5, 6]], 7, 100], [[[0, 0], [0, 0]], 4, 0], [[[0, 0], [0, 0]], 1, -1], [[[-5, 5, -5, 5]], 2, 0],
           [[[3, -3], [-3, 3], [3, -3]], 2, 0], [[[1, 1, 1, 1], [1, 1, 1, 1], [1, 1, 1, 1], [1, 1, 1, 1]], 4, 4]],
)
_r = rnd(9105)
p["tests"].append([_mat(_r, 60, 60, -50, 50), 12, 0])
p["tests"].append([_mat(_r, 60, 60, -50, 50), 3600, 100000])
p["tests"].append([_mat(_r, 60, 60, -50, 50), 60, 25])
p["tests"].append([[[0] * 60 for _ in range(60)], 24, 0])


def b_fixedarea(matrix, area, limit):
    R, C = len(matrix), len(matrix[0])
    cnt = 0
    for r1 in range(R):
        for r2 in range(r1, R):
            for c1 in range(C):
                for c2 in range(c1, C):
                    if (r2 - r1 + 1) * (c2 - c1 + 1) == area and _sum_rect(matrix, r1, c1, r2, c2) <= limit:
                        cnt += 1
    return cnt


def g_fixedarea(r):
    R, C = r.randint(1, 5), r.randint(1, 5)
    return [_mat(r, R, C, -4, 4), r.choice([1, 2, 3, 4, 6, 8, 9, 12, 25, 30]), r.randint(-6, 8)]


def v_fixedarea(tests):
    for t in tests:
        m, area, limit = t["args"]
        _rect_check(m, 60, 60, -50, 50)
        assert 1 <= area <= 3600 and -10 ** 6 <= limit <= 10 ** 6


CHECKS["count-fixed-area-rectangles-under-limit"] = (b_fixedarea, g_fixedarea, "exact")
VALIDATE["count-fixed-area-rectangles-under-limit"] = v_fixedarea

p = add(
    id="largest-square-sum-within-limit", title="Largest Square Within a Sum Limit", diff="Medium", topic=T, tier="common",
    fn="maxSquareSide", params=[("matrix", "int[][]"), ("limit", "int")], ret="int", cmp="exact",
    desc="<p>The grid <code>matrix</code> holds non-negative integers. Find the largest side length <code>s</code> such that some <code>s x s</code> square of consecutive cells has a cell sum that is at most <code>limit</code>. Return <code>0</code> if even a single cell is above the limit.</p><pre>matrix = [[2, 2, 2],\n          [2, 1, 0],\n          [2, 0, 0]], limit = 1\nbottom-right 2 x 2 square: 1 + 0 + 0 + 0 = 1\nresult = 2</pre>",
    constraints=["1 &le; rows, columns &le; 60", "0 &le; matrix[i][j] &le; 1,000", "0 &le; limit &le; 10,000,000"],
    hints=["Try every side length and every position. What do you need so that testing one square is O(1)?",
           "Because all values are non-negative, if some square of side <code>s</code> fits under the limit then a square of side <code>s - 1</code> inside it does too.",
           "That monotonic property allows binary search on the side. Check a given side by scanning all positions with a 2-D prefix table in O(R * C)."],
    editorial=["Let <code>ok(s)</code> be true if some <code>s x s</code> square has sum at most <code>limit</code>. Every square of side <code>s - 1</code> contained in a good square of side <code>s</code> has a smaller or equal sum (cells are non-negative), so <code>ok</code> is monotonic: true for small sides, then false from some point on. <code>ok(0)</code> is trivially true.",
               "Binary search the largest <code>s</code> between 0 and <code>min(R, C)</code>. Each evaluation of <code>ok(s)</code> scans all (R - s + 1)(C - s + 1) positions and reads each square sum from the prefix table in O(1). The total is O(R * C * log(min(R, C))).",
               "A simpler alternative walks the squares while growing the answer by at most one per cell, giving O(R * C) overall, but the binary-search version is easier to prove correct. Note that with negative cells the monotonic property would fail, which is why they are excluded."],
    time="O(R*C*log(min(R,C)))", space="O(R*C)",
    solution='''def maxSquareSide(matrix, limit):
    R, C = len(matrix), len(matrix[0])
    P = [[0] * (C + 1) for _ in range(R + 1)]
    for i in range(R):
        for j in range(C):
            P[i + 1][j + 1] = matrix[i][j] + P[i][j + 1] + P[i + 1][j] - P[i][j]

    def ok(s):
        for i in range(R - s + 1):
            for j in range(C - s + 1):
                if P[i + s][j + s] - P[i][j + s] - P[i + s][j] + P[i][j] <= limit:
                    return True
        return False

    lo, hi = 0, min(R, C)
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if ok(mid):
            lo = mid
        else:
            hi = mid - 1
    return lo
''',
    tests=[[[[2, 2, 2], [2, 1, 0], [2, 0, 0]], 1], [[[2, 2, 2], [2, 1, 0], [2, 0, 0]], 0], [[[2, 2, 2], [2, 1, 0], [2, 0, 0]], 11],
           [[[2, 2, 2], [2, 1, 0], [2, 0, 0]], 10], [[[5]], 4], [[[5]], 5], [[[0, 0, 0, 0]], 0], [[[1, 1, 3, 2, 4, 3, 2]] * 3, 4],
           [[[7, 7], [7, 7], [7, 7]], 27], [[[7, 7], [7, 7], [7, 7]], 28], [[[1000, 0], [0, 1000]], 999]],
)
_r = rnd(9106)
_m = _mat(_r, 60, 60, 0, 1000)
p["tests"].append([_m, _sum_rect(_m, 0, 0, 29, 29)])
_m = _mat(_r, 60, 60, 0, 1000)
p["tests"].append([_m, 1500000])
p["tests"].append([[[1000] * 60 for _ in range(60)], 10000000])
p["tests"].append([_mat(_r, 60, 60, 500, 1000), 400])


def b_maxsq(matrix, limit):
    R, C = len(matrix), len(matrix[0])
    best = 0
    for s in range(1, min(R, C) + 1):
        for i in range(R - s + 1):
            for j in range(C - s + 1):
                if _sum_rect(matrix, i, j, i + s - 1, j + s - 1) <= limit:
                    best = max(best, s)
    return best


def g_maxsq(r):
    R, C = r.randint(1, 6), r.randint(1, 6)
    return [_mat(r, R, C, 0, 5), r.randint(0, 40)]


def v_maxsq(tests):
    for t in tests:
        m, limit = t["args"]
        _rect_check(m, 60, 60, 0, 1000)
        assert 0 <= limit <= 10 ** 7


CHECKS["largest-square-sum-within-limit"] = (b_maxsq, g_maxsq, "exact")
VALIDATE["largest-square-sum-within-limit"] = v_maxsq

p = add(
    id="largest-bordered-square", title="Largest Square with a Solid Border", diff="Medium", topic=T, tier="common",
    fn="largestBorderSquare", params=[("grid", "int[][]")], ret="int", cmp="exact",
    desc="<p>The grid <code>grid</code> contains only <code>0</code> and <code>1</code>. Find the largest square sub-grid whose <strong>border</strong> consists only of <code>1</code>s; the cells strictly inside the border may be anything. Return the side length of that square, or <code>0</code> if the grid has no <code>1</code> at all.</p><p>A single cell containing <code>1</code> is a square of side 1.</p><pre>grid = [[1, 1, 1, 1],\n        [1, 0, 0, 1],\n        [1, 0, 0, 1],\n        [1, 1, 1, 1]]\nresult = 4</pre>",
    constraints=["1 &le; rows, columns &le; 60", "grid[i][j] is 0 or 1"],
    hints=["A square with top-left corner (i, j) and side <code>s</code> is valid if its four sides are all ones. Checking the sides cell by cell costs O(s).",
           "A side is a segment of a row or of a column. A 1-D prefix sum along each row and each column tells you in O(1) whether a segment is all ones (its sum equals its length).",
           "For every cell that holds a 1, try side lengths from the largest possible down to the current best plus one, and stop at the first side whose top, bottom, left and right segments are all ones."],
    editorial=["Precompute <code>rowP[i][j]</code> = number of ones in row <code>i</code> among the first <code>j</code> cells and <code>colP[j][i]</code> = number of ones in column <code>j</code> among the first <code>i</code> cells. A segment of length <code>s</code> is all ones exactly when its prefix difference equals <code>s</code>.",
               "For a top-left corner (i, j) and side <code>s</code>, check the top row segment <code>(i, j..j+s-1)</code>, the bottom row segment <code>(i+s-1, j..j+s-1)</code>, the left column segment <code>(i..i+s-1, j)</code> and the right column segment <code>(i..i+s-1, j+s-1)</code>.",
               "Trying sides from large to small and stopping at the first success, and only looking at sides larger than the best answer so far, keeps the search tight. The worst case is O(R * C * min(R, C)) with O(1) per check, about 216,000 checks for a 60 x 60 grid."],
    time="O(R*C*min(R,C))", space="O(R*C)",
    solution='''def largestBorderSquare(grid):
    R, C = len(grid), len(grid[0])
    rowP = [[0] * (C + 1) for _ in range(R)]
    colP = [[0] * (R + 1) for _ in range(C)]
    for i in range(R):
        for j in range(C):
            rowP[i][j + 1] = rowP[i][j] + grid[i][j]
            colP[j][i + 1] = colP[j][i] + grid[i][j]
    best = 0
    for i in range(R):
        for j in range(C):
            if grid[i][j] == 0:
                continue
            for s in range(min(R - i, C - j), best, -1):
                if (rowP[i][j + s] - rowP[i][j] == s
                        and rowP[i + s - 1][j + s] - rowP[i + s - 1][j] == s
                        and colP[j][i + s] - colP[j][i] == s
                        and colP[j + s - 1][i + s] - colP[j + s - 1][i] == s):
                    best = s
                    break
    return best
''',
    tests=[[[[1, 1, 1, 1], [1, 0, 0, 1], [1, 0, 0, 1], [1, 1, 1, 1]]], [[[1, 1], [1, 0]]], [[[0]]], [[[1]]], [[[0, 0], [0, 0]]],
           [[[1, 1, 1], [1, 0, 1], [1, 1, 1]]], [[[1, 1, 1], [1, 0, 1], [1, 1, 0]]], [[[1, 1, 0, 1, 1, 1], [1, 1, 0, 1, 0, 1], [0, 0, 0, 1, 1, 1]]],
           [[[1, 1, 1, 1, 1]]], [[[1], [1], [0], [1]]], [[[1, 0, 1], [0, 1, 0], [1, 0, 1]]]],
)
_r = rnd(9107)
p["tests"].append([[[1] * 60 for _ in range(60)]])
_g = [[1] * 60 for _ in range(60)]
for _i in range(1, 59):
    for _j in range(1, 59):
        _g[_i][_j] = 0
p["tests"].append([_g])
p["tests"].append([[[1 if _r.random() < 0.9 else 0 for _ in range(60)] for _ in range(60)]])
p["tests"].append([[[1 if _r.random() < 0.55 else 0 for _ in range(60)] for _ in range(60)]])


def b_border(grid):
    R, C = len(grid), len(grid[0])
    best = 0
    for i in range(R):
        for j in range(C):
            for s in range(1, min(R - i, C - j) + 1):
                ok = True
                for t in range(s):
                    if not (grid[i][j + t] and grid[i + s - 1][j + t] and grid[i + t][j] and grid[i + t][j + s - 1]):
                        ok = False
                        break
                if ok:
                    best = max(best, s)
    return best


def g_border(r):
    R, C = r.randint(1, 7), r.randint(1, 7)
    pr = r.choice([0.5, 0.75, 0.9])
    return [[[1 if r.random() < pr else 0 for _ in range(C)] for _ in range(R)]]


def v_border(tests):
    for t in tests:
        _rect_check(t["args"][0], 60, 60, 0, 1)


CHECKS["largest-bordered-square"] = (b_border, g_border, "exact")
VALIDATE["largest-bordered-square"] = v_border

p = add(
    id="points-in-query-rectangles", title="Points in Query Rectangles", diff="Medium", topic=T, tier="extra",
    fn="countPoints", params=[("n", "int"), ("points", "int[][]"), ("queries", "int[][]")], ret="int[]", cmp="exact",
    desc="<p>A map is an <code>n x n</code> grid of cells with coordinates <code>(x, y)</code>, where <code>0 &le; x, y &lt; n</code>. The array <code>points</code> lists markers as <code>[x, y]</code> pairs; several markers may lie on the same cell and each one counts.</p><p>Each query is <code>[x1, y1, x2, y2]</code> and asks how many markers lie in the rectangle <code>x1 &le; x &le; x2</code>, <code>y1 &le; y &le; y2</code> (borders included). Return the answers in query order.</p><pre>n = 4\npoints = [[0, 0], [1, 1], [1, 1], [3, 2]]\nqueries = [[0, 0, 1, 1], [1, 1, 3, 3], [2, 0, 3, 1]]\nresult = [3, 3, 0]</pre>",
    constraints=["1 &le; n &le; 300", "0 &le; points.length &le; 3,000, with 0 &le; x, y &lt; n", "0 &le; queries.length &le; 2,000", "0 &le; x1 &le; x2 &lt; n and 0 &le; y1 &le; y2 &lt; n"],
    hints=["Checking every marker for every query costs O(points * queries) in total. The map is small, so think about the grid itself.",
           "Turn the markers into a grid of counts: <code>cnt[x][y]</code> is the number of markers on that cell. Now each query asks for a rectangle sum over this grid.",
           "Build a 2-D prefix table over <code>cnt</code> and answer every query with the four-term formula in O(1)."],
    editorial=["Create an (n + 1) x (n + 1) table <code>P</code> where <code>P[x+1][y+1]</code> starts as the number of markers on cell (x, y). Then convert it into a 2-D prefix table by adding the table above and to the left and subtracting the overlap, so that <code>P[a][b]</code> counts the markers with <code>x &lt; a</code> and <code>y &lt; b</code>.",
               "A query is answered by inclusion-exclusion: <code>P[x2+1][y2+1] - P[x1][y2+1] - P[x2+1][y1] + P[x1][y1]</code>. Multiple markers on one cell are handled naturally because the counts are added, not set.",
               "Time O(n<sup>2</sup> + p + q), space O(n<sup>2</sup>). This trade of memory for speed works because the coordinates are small; with huge coordinates one would sort and compress them first."],
    time="O(n^2 + p + q)", space="O(n^2)",
    solution='''def countPoints(n, points, queries):
    P = [[0] * (n + 1) for _ in range(n + 1)]
    for x, y in points:
        P[x + 1][y + 1] += 1
    for a in range(1, n + 1):
        for b in range(1, n + 1):
            P[a][b] += P[a - 1][b] + P[a][b - 1] - P[a - 1][b - 1]
    out = []
    for x1, y1, x2, y2 in queries:
        out.append(P[x2 + 1][y2 + 1] - P[x1][y2 + 1] - P[x2 + 1][y1] + P[x1][y1])
    return out
''',
    tests=[[4, [[0, 0], [1, 1], [1, 1], [3, 2]], [[0, 0, 1, 1], [1, 1, 3, 3], [2, 0, 3, 1]]],
           [1, [[0, 0], [0, 0]], [[0, 0, 0, 0]]], [1, [], [[0, 0, 0, 0]]], [3, [[2, 2]], [[0, 0, 1, 1], [2, 2, 2, 2], [0, 0, 2, 2]]],
           [5, [[0, 4], [4, 0], [2, 2]], [[0, 0, 4, 4], [0, 4, 0, 4], [4, 0, 4, 0], [1, 1, 3, 3]]],
           [3, [[0, 0], [1, 0], [2, 0]], [[0, 0, 2, 0], [1, 0, 1, 0], [0, 1, 2, 2]]], [2, [[0, 1], [1, 0]], []]],
)
_r = rnd(9108)


def _rq(n, cnt):
    out = []
    for _ in range(cnt):
        a, b, c, d = _r.randrange(n), _r.randrange(n), _r.randrange(n), _r.randrange(n)
        out.append([min(a, b), min(c, d), max(a, b), max(c, d)])
    return out


p["tests"].append([300, [[_r.randrange(300), _r.randrange(300)] for _ in range(3000)], [[0, 0, 299, 299]] + _rq(300, 1500)])
p["tests"].append([300, [[7, 7]] * 3000, [[7, 7, 7, 7], [0, 0, 6, 6], [8, 8, 299, 299], [0, 0, 299, 299]]])
p["tests"].append([40, [[_r.randrange(40), _r.randrange(40)] for _ in range(2000)], _rq(40, 1000)])


def b_points(n, points, queries):
    return [sum(1 for x, y in points if x1 <= x <= x2 and y1 <= y <= y2) for x1, y1, x2, y2 in queries]


def g_points(r):
    n = r.randint(1, 6)
    pts = [[r.randrange(n), r.randrange(n)] for _ in range(r.randint(0, 10))]
    qs = []
    for _ in range(r.randint(0, 6)):
        a, b, c, d = r.randrange(n), r.randrange(n), r.randrange(n), r.randrange(n)
        qs.append([min(a, b), min(c, d), max(a, b), max(c, d)])
    return [n, pts, qs]


def v_points(tests):
    for t in tests:
        n, pts, qs = t["args"]
        assert 1 <= n <= 300 and len(pts) <= 3000 and len(qs) <= 2000
        assert all(len(q) == 2 and 0 <= q[0] < n and 0 <= q[1] < n for q in pts)
        assert all(0 <= a <= c < n and 0 <= b <= d < n for a, b, c, d in qs)


CHECKS["points-in-query-rectangles"] = (b_points, g_points, "exact")
VALIDATE["points-in-query-rectangles"] = v_points

# ---------------------------------------------------------------- HARD

p = add(
    id="smallest-rectangle-with-sum-at-least", title="Smallest Rectangle Reaching a Sum", diff="Hard", topic=T, tier="extra",
    fn="minRectangleArea", params=[("matrix", "int[][]"), ("target", "int")], ret="int", cmp="exact",
    desc="<p>The grid <code>matrix</code> holds non-negative integers. Among all rectangular blocks (consecutive rows and consecutive columns) whose cell sum is at least <code>target</code>, find the one with the smallest number of cells and return that number. If no block reaches <code>target</code> (not even the whole grid), return <code>0</code>.</p><pre>matrix = [[1, 2, 3],\n          [4, 5, 6],\n          [7, 8, 9]], target = 25\nbest block: the bottom-right 2 x 2 (5 + 6 + 8 + 9 = 28), area 4\nresult = 4</pre>",
    constraints=["1 &le; rows, columns &le; 60", "0 &le; matrix[i][j] &le; 100", "1 &le; target &le; 100,000,000"],
    hints=["Trying every block is O(R<sup>2</sup>C<sup>2</sup>) blocks. Fix the top and bottom rows to reduce the problem to one dimension.",
           "For a fixed pair of rows, add the rows into one array of column sums. A block is now a contiguous segment of that array, and the width should be as small as possible while the segment sum is at least <code>target</code>.",
           "All numbers are non-negative, so extending a segment never decreases its sum. That allows a two-pointer window over the column sums. Update the column sums incrementally while the bottom row moves down."],
    editorial=["Fix the top row <code>t</code> and move the bottom row <code>b</code> downwards, maintaining <code>col[c]</code> = the sum of column <code>c</code> over rows <code>t..b</code>. Every block with these row bounds is a contiguous range of columns, with the sum of <code>col</code> over that range.",
               "Because the values are non-negative, the shortest range ending at column <code>right</code> with sum at least <code>target</code> can be found with a sliding window: add <code>col[right]</code>, and while the window sum is at least <code>target</code>, record the area <code>(b - t + 1) * (right - left + 1)</code> and drop the left column. Each column enters and leaves the window once.",
               "This gives O(R<sup>2</sup> * C) time and O(C) space. With negative numbers the window would not be monotonic and a different technique (prefix sums with ordered lookups) would be required."],
    time="O(R^2*C)", space="O(C)",
    solution='''def minRectangleArea(matrix, target):
    R, C = len(matrix), len(matrix[0])
    best = 0
    for top in range(R):
        col = [0] * C
        for bottom in range(top, R):
            row = matrix[bottom]
            for c in range(C):
                col[c] += row[c]
            h = bottom - top + 1
            left = 0
            s = 0
            for right in range(C):
                s += col[right]
                while s >= target and left <= right:
                    area = h * (right - left + 1)
                    if best == 0 or area < best:
                        best = area
                    s -= col[left]
                    left += 1
    return best
''',
    tests=[[[[1, 2, 3], [4, 5, 6], [7, 8, 9]], 25], [[[1, 2, 3], [4, 5, 6], [7, 8, 9]], 9], [[[1, 2, 3], [4, 5, 6], [7, 8, 9]], 45],
           [[[1, 2, 3], [4, 5, 6], [7, 8, 9]], 46], [[[1, 2, 3], [4, 5, 6], [7, 8, 9]], 11], [[[0, 0], [0, 0]], 1], [[[5]], 5], [[[5]], 6],
           [[[3, 0, 0, 3]], 6], [[[3], [0], [0], [3]], 6], [[[0, 9, 0], [0, 0, 0], [9, 0, 9]], 18], [[[1, 1, 1], [1, 1, 1]], 4]],
)
_r = rnd(9109)
p["tests"].append([_mat(_r, 60, 60, 0, 100), 150000])
p["tests"].append([_mat(_r, 60, 60, 0, 100), 300])
p["tests"].append([[[1] * 60 for _ in range(60)], 3000])
p["tests"].append([[[0] * 59 + [100] for _ in range(60)], 5000])


def b_minrect(matrix, target):
    R, C = len(matrix), len(matrix[0])
    best = 0
    for r1 in range(R):
        for r2 in range(r1, R):
            for c1 in range(C):
                for c2 in range(c1, C):
                    if _sum_rect(matrix, r1, c1, r2, c2) >= target:
                        a = (r2 - r1 + 1) * (c2 - c1 + 1)
                        if best == 0 or a < best:
                            best = a
    return best


def g_minrect(r):
    R, C = r.randint(1, 5), r.randint(1, 5)
    return [_mat(r, R, C, 0, r.choice([1, 3, 9])), r.randint(1, 30)]


def v_minrect(tests):
    for t in tests:
        m, target = t["args"]
        _rect_check(m, 60, 60, 0, 100)
        assert 1 <= target <= 10 ** 8


CHECKS["smallest-rectangle-with-sum-at-least"] = (b_minrect, g_minrect, "exact")
VALIDATE["smallest-rectangle-with-sum-at-least"] = v_minrect

p = add(
    id="stamp-the-grid", title="Stamp the Empty Cells", diff="Hard", topic=T, tier="common",
    fn="canStamp", params=[("grid", "int[][]"), ("h", "int"), ("w", "int")], ret="bool", cmp="exact",
    desc="<p>The grid <code>grid</code> has empty cells (<code>0</code>) and blocked cells (<code>1</code>). You own an unlimited supply of rectangular stamps of height <code>h</code> and width <code>w</code> (they cannot be rotated). A stamp may be pressed anywhere as long as it lies completely inside the grid and covers <strong>no blocked cell</strong>. Stamps may overlap each other.</p><p>Return <code>true</code> if you can press stamps so that every empty cell is covered by at least one stamp, and <code>false</code> otherwise. Blocked cells are never covered, so a grid with no empty cell needs no stamp.</p><pre>grid = [[1, 0, 0],\n        [0, 0, 0]], h = 2, w = 2\nThe cell (1, 0) can only be covered by a stamp at columns 0..1,\nbut that stamp would contain the blocked cell (0, 0).\nresult = false</pre>",
    constraints=["1 &le; rows, columns &le; 60", "1 &le; h, w &le; 60", "grid[i][j] is 0 or 1"],
    hints=["Pressing a stamp on every legal position only helps: it never covers a blocked cell, and overlapping is allowed. So you only need to know the set of legal positions.",
           "A position is legal if the h x w rectangle there contains no blocked cell. A 2-D prefix sum of the blocked cells tests that in O(1).",
           "Then you must find out whether every empty cell lies in at least one legal rectangle. Marking each rectangle cell by cell is too slow; use a 2-D difference array (add at the top-left corner, cancel at the other three corners) and take 2-D prefix sums to get coverage counts."],
    editorial=["Using all legal stamp positions is always at least as good as any subset, so the answer is true exactly when the union of all legal stamps contains every empty cell. A position (i, j) is legal when the number of blocked cells inside its h x w rectangle is zero, which a 2-D prefix sum over the blocked cells answers in O(1).",
               "To compute the union, use a 2-D difference array <code>D</code>: for a legal rectangle with top-left (i, j) do <code>D[i][j] += 1</code>, <code>D[i][j+w] -= 1</code>, <code>D[i+h][j] -= 1</code>, <code>D[i+h][j+w] += 1</code>. Taking the 2-D prefix sum of <code>D</code> gives the number of legal stamps covering each cell.",
               "Finally check that every empty cell has coverage at least one (a blocked cell can never have coverage since any rectangle containing it is illegal). Time O(R * C), space O(R * C). The key insight is combining two grid prefix-sum tools: one to validate a rectangle, one to paint many rectangles at once."],
    time="O(R*C)", space="O(R*C)",
    solution='''def canStamp(grid, h, w):
    R, C = len(grid), len(grid[0])
    P = [[0] * (C + 1) for _ in range(R + 1)]
    for i in range(R):
        for j in range(C):
            P[i + 1][j + 1] = grid[i][j] + P[i][j + 1] + P[i + 1][j] - P[i][j]
    D = [[0] * (C + 2) for _ in range(R + 2)]
    for i in range(R - h + 1):
        for j in range(C - w + 1):
            if P[i + h][j + w] - P[i][j + w] - P[i + h][j] + P[i][j] == 0:
                D[i][j] += 1
                D[i][j + w] -= 1
                D[i + h][j] -= 1
                D[i + h][j + w] += 1
    cover = [[0] * (C + 1) for _ in range(R + 1)]
    for i in range(R):
        for j in range(C):
            cover[i][j] = D[i][j] + (cover[i - 1][j] if i else 0) + (cover[i][j - 1] if j else 0) - (cover[i - 1][j - 1] if i and j else 0)
            if grid[i][j] == 0 and cover[i][j] == 0:
                return False
    return True
''',
    tests=[[[[1, 0, 0], [0, 0, 0]], 2, 2], [[[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]], 2, 2], [[[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]], 2, 3],
           [[[1, 1], [1, 1]], 5, 5], [[[1, 1], [1, 1]], 1, 1], [[[0]], 1, 1], [[[0]], 2, 1], [[[0, 1, 0]], 1, 2], [[[0, 1, 0]], 1, 1],
           [[[1, 0, 0, 0], [1, 0, 0, 0], [1, 0, 0, 0], [1, 0, 0, 0]], 2, 2], [[[1, 0, 0, 0], [1, 0, 0, 0], [1, 0, 1, 0], [1, 0, 0, 0]], 2, 2],
           [[[0, 0, 0], [0, 1, 0], [0, 0, 0]], 1, 3], [[[0, 0, 0], [0, 1, 0], [0, 0, 0]], 2, 2]],
)
_r = rnd(9110)


def _stampable(R, C, h, w, placements):
    g = [[1] * C for _ in range(R)]
    for _ in range(placements):
        i, j = _r.randrange(R - h + 1), _r.randrange(C - w + 1)
        for a in range(i, i + h):
            for b in range(j, j + w):
                g[a][b] = 0
    return g


p["tests"].append([_stampable(60, 60, 4, 5, 250), 4, 5])
_g = _stampable(60, 60, 4, 5, 250)
_g[30][30] = 1 - _g[30][30] if _g[30][30] == 0 else 0  # flips a blocked cell to empty or breaks nothing
p["tests"].append([_g, 4, 5])
p["tests"].append([[[0] * 60 for _ in range(60)], 60, 60])
p["tests"].append([[[0] * 60 for _ in range(60)], 7, 7])
p["tests"].append([[[1 if _r.random() < 0.04 else 0 for _ in range(60)] for _ in range(60)], 2, 2])
p["tests"].append([_stampable(55, 60, 3, 3, 700), 3, 3])


def b_stamp(grid, h, w):
    R, C = len(grid), len(grid[0])
    cov = [[False] * C for _ in range(R)]
    for i in range(R - h + 1):
        for j in range(C - w + 1):
            if all(grid[a][b] == 0 for a in range(i, i + h) for b in range(j, j + w)):
                for a in range(i, i + h):
                    for b in range(j, j + w):
                        cov[a][b] = True
    return all(cov[i][j] for i in range(R) for j in range(C) if grid[i][j] == 0)


def g_stamp(r):
    R, C = r.randint(1, 6), r.randint(1, 6)
    pr = r.choice([0.1, 0.25, 0.4])
    if r.random() < 0.5:
        h, w = r.randint(1, min(R, 3)), r.randint(1, min(C, 3))
        g = [[1] * C for _ in range(R)]
        for _ in range(r.randint(1, 6)):
            i, j = r.randrange(R - h + 1), r.randrange(C - w + 1)
            for a in range(i, i + h):
                for b in range(j, j + w):
                    g[a][b] = 0
        if r.random() < 0.3:
            g[r.randrange(R)][r.randrange(C)] ^= 1
        return [g, h, w]
    return [[[1 if r.random() < pr else 0 for _ in range(C)] for _ in range(R)], r.randint(1, 3), r.randint(1, 3)]


def v_stamp(tests):
    for t in tests:
        g, h, w = t["args"]
        _rect_check(g, 60, 60, 0, 1)
        assert 1 <= h <= 60 and 1 <= w <= 60
    res = [t["expected"] for t in tests]
    assert True in res and False in res, "need both outcomes"


CHECKS["stamp-the-grid"] = (b_stamp, g_stamp, "exact")
VALIDATE["stamp-the-grid"] = v_stamp

p = add(
    id="two-disjoint-square-blocks", title="Two Disjoint Heaviest Blocks", diff="Hard", topic=T, tier="extra",
    fn="maxTwoBlocks", params=[("matrix", "int[][]"), ("k", "int")], ret="int", cmp="exact",
    desc="<p>Choose two <code>k x k</code> blocks of the grid <code>matrix</code> that do not share any cell, so that the total sum of the cells of both blocks is as large as possible. Return that total. Blocks may touch along an edge.</p><p>The input guarantees that two disjoint blocks fit in the grid.</p><pre>matrix = [[ 1,  2,  3,  4],\n          [ 5,  6,  7,  8],\n          [ 9, 10, 11, 12],\n          [13, 14, 15, 16]], k = 2\nbottom-right block 11 + 12 + 15 + 16 = 54\nbottom-left block   9 + 10 + 13 + 14 = 46\nresult = 100</pre>",
    constraints=["1 &le; rows, columns &le; 60", "-100 &le; matrix[i][j] &le; 100", "1 &le; k, and two disjoint k x k blocks fit: rows &ge; 2k or columns &ge; 2k (and both dimensions are &ge; k)"],
    hints=["There can be about 3,500 blocks, so trying all pairs means millions of pairs. First make each block sum available in O(1).",
           "Two axis-aligned k x k squares that do not overlap are always separated: one lies entirely above the other (top rows differ by at least k), or entirely to the left (left columns differ by at least k).",
           "Compute all block sums, then the best block starting in each row and in each column. For a horizontal separation, combine for each row <code>i</code> the best block starting at row <code>i</code> with the best block starting at any row up to <code>i - k</code> (a running maximum). Do the same for columns and take the larger result."],
    editorial=["Let <code>S[i][j]</code> be the sum of the block whose top-left cell is (i, j), found from the 2-D prefix table in O(1). Two blocks overlap exactly when their top rows differ by less than <code>k</code> <em>and</em> their left columns differ by less than <code>k</code>. So a disjoint pair must have row distance at least <code>k</code> or column distance at least <code>k</code>.",
               "Handle the two cases independently. Let <code>rowBest[i] = max_j S[i][j]</code> and <code>pre[i]</code> = the maximum of <code>rowBest[0..i]</code>. If the second block starts in row <code>i</code> and the first in a row at most <code>i - k</code>, the best total is <code>pre[i - k] + rowBest[i]</code>; maximise over <code>i</code> from <code>k</code> to <code>R - k</code>. Repeat with <code>colBest</code> for the vertical case. Cases that do not fit are simply skipped, and the guarantee ensures at least one case produces a value.",
               "Time O(R * C) for the sums plus O(R * C) for the maxima; space O(R * C). Comparing every pair would be O((R * C)<sup>2</sup>). Negative numbers are why the answer is not simply the two largest blocks: those might overlap, and a good block may even have a negative sum."],
    time="O(R*C)", space="O(R*C)",
    solution='''def maxTwoBlocks(matrix, k):
    R, C = len(matrix), len(matrix[0])
    P = [[0] * (C + 1) for _ in range(R + 1)]
    for i in range(R):
        for j in range(C):
            P[i + 1][j + 1] = matrix[i][j] + P[i][j + 1] + P[i + 1][j] - P[i][j]
    nr, nc = R - k + 1, C - k + 1
    S = [[P[i + k][j + k] - P[i][j + k] - P[i + k][j] + P[i][j] for j in range(nc)] for i in range(nr)]
    NEG = float("-inf")
    best = NEG
    rowBest = [max(S[i]) for i in range(nr)]
    pre = []
    for v in rowBest:
        pre.append(v if not pre else max(pre[-1], v))
    for i in range(k, nr):
        best = max(best, pre[i - k] + rowBest[i])
    colBest = [max(S[i][j] for i in range(nr)) for j in range(nc)]
    pre = []
    for v in colBest:
        pre.append(v if not pre else max(pre[-1], v))
    for j in range(k, nc):
        best = max(best, pre[j - k] + colBest[j])
    return best
''',
    tests=[[[[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12], [13, 14, 15, 16]], 2], [[[5], [6]], 1], [[[5, 6]], 1], [[[-5, -6]], 1],
           [[[-1, -2, -3, -4], [-5, -6, -7, -8]], 1], [[[9, 9, 9, 9], [9, 9, 9, 9]], 2], [[[100, -100, 100], [-100, 100, -100], [100, -100, 100]], 1],
           [[[0, 0, 0, 0, 0], [0, 0, 0, 0, 0]], 2], [[[1, 1, 1], [2, 2, 2], [3, 3, 3], [4, 4, 4], [5, 5, 5], [6, 6, 6]], 3], [[[-3, 8, -3], [8, -3, 8], [-3, 8, -3], [8, -3, 8]], 2],
           [[[5, -50, 5], [5, -50, 5], [5, -50, 5]], 1]],
)
_r = rnd(9111)
p["tests"].append([_mat(_r, 60, 60, -100, 100), 1])
p["tests"].append([_mat(_r, 60, 60, -100, 100), 20])
p["tests"].append([_mat(_r, 60, 60, -100, 100), 30])
p["tests"].append([_mat(_r, 10, 60, -100, 100), 5])
p["tests"].append([_mat(_r, 60, 7, -100, 0), 3])


def b_twoblocks(matrix, k):
    R, C = len(matrix), len(matrix[0])
    pos = [(i, j, _sum_rect(matrix, i, j, i + k - 1, j + k - 1)) for i in range(R - k + 1) for j in range(C - k + 1)]
    best = None
    for a in range(len(pos)):
        for b in range(a + 1, len(pos)):
            i1, j1, s1 = pos[a]
            i2, j2, s2 = pos[b]
            if abs(i1 - i2) >= k or abs(j1 - j2) >= k:
                if best is None or s1 + s2 > best:
                    best = s1 + s2
    return best


def g_twoblocks(r):
    k = r.randint(1, 3)
    while True:
        R, C = r.randint(k, 7), r.randint(k, 7)
        if R >= 2 * k or C >= 2 * k:
            break
    return [_mat(r, R, C, -9, 9), k]


def v_twoblocks(tests):
    for t in tests:
        m, k = t["args"]
        _rect_check(m, 60, 60, -100, 100)
        R, C = len(m), len(m[0])
        assert k >= 1 and R >= k and C >= k and (R >= 2 * k or C >= 2 * k), "two blocks must fit"


CHECKS["two-disjoint-square-blocks"] = (b_twoblocks, g_twoblocks, "exact")
VALIDATE["two-disjoint-square-blocks"] = v_twoblocks
