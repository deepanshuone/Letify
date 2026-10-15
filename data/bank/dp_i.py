"""Problems: Dynamic Programming, grid path counting (variants, obstacles, modulo, turns, knight and king moves)."""
from lib import add, rnd, CHECKS, VALIDATE, gen_arr  # noqa: F401

TOPIC = "Dynamic Programming"
MOD = 10 ** 9 + 7


def _bin_grid(r, h, w, p_one):
    return [[1 if r.random() < p_one else 0 for _ in range(w)] for _ in range(h)]


def _is_rect(g):
    return len(g) > 0 and len(g[0]) > 0 and all(len(row) == len(g[0]) for row in g)


def _is_bin(g):
    return all(v in (0, 1) for row in g for v in row)


def _free_ends(g):
    g[0][0] = 0
    g[-1][-1] = 0
    return g


# ================================================================ EASY

# ---------------------------------------------------------------- falling-paths-count-blocked
p = add(
    id="falling-paths-count-blocked", title="Count Falling Paths Around Blocks", diff="Easy", topic=TOPIC,
    fn="countFallingPaths", params=[("grid", "int[][]")], ret="int", cmp="exact",
    desc="<p>A marble is dropped into a rectangular <code>grid</code> in which <code>0</code> marks a free cell and <code>1</code> marks a blocked cell. It may start in <strong>any free cell of the top row</strong>. On every step it falls to the next row, landing in the cell directly below, the cell below and to the left, or the cell below and to the right (never leaving the grid, never entering a blocked cell). It stops when it reaches the bottom row.</p><p>Count the different falls, where two falls differ when they visit different cells. Because the count can be large, return it modulo <code>1,000,000,007</code>.</p><pre>grid = [[0,0,0],\n        [0,1,0],\n        [0,0,0]]   ->  8\ngrid = [[0,1,0],\n        [1,0,1]]   ->  2</pre><p>In the first example the marble has 2 ways to reach each of the two free cells of the middle row next to the block, and these extend to 2 + 4 + 2 ways in the bottom row.</p>",
    constraints=["1 &le; grid.length, grid[0].length &le; 100", "grid[i][j] is 0 or 1", "If the grid has a single row, every free cell counts as one fall of length zero"],
    hints=["Look only at the last cell of a fall. In which cells of the previous row could the marble have been one step earlier?",
           "Let <code>ways[r][c]</code> be the number of falls that end in cell <code>(r, c)</code>. A blocked cell has 0 ways; a free cell adds up the ways of up to three cells in the row above.",
           "Seed the top row with 1 for every free cell, then fill row by row. Only the previous row is needed. Reduce modulo 1,000,000,007 as you go, and sum the bottom row at the end."],
    editorial=["Count falls cell by cell. Every fall that ends in the free cell <code>(r, c)</code> with <code>r &gt; 0</code> came from <code>(r-1, c-1)</code>, <code>(r-1, c)</code> or <code>(r-1, c+1)</code>, and the falls arriving through different predecessors are different. So <code>ways[r][c] = ways[r-1][c-1] + ways[r-1][c] + ways[r-1][c+1]</code> (ignoring neighbours outside the grid), and a blocked cell is forced to 0, which stops any fall from passing through it.",
               "The top row is the base: a free cell starts exactly one fall. The answer is the sum of <code>ways</code> over the bottom row. Because each row depends only on the row above, two arrays of width n suffice. Time O(m &middot; n), extra space O(n). Taking the remainder after every cell keeps numbers small."],
    time="O(m &middot; n)", space="O(n)",
    solution='''def countFallingPaths(grid):
    MOD = 10 ** 9 + 7
    n = len(grid[0])
    cur = [1 - v for v in grid[0]]
    for row in grid[1:]:
        nxt = [0] * n
        for c in range(n):
            if row[c] == 0:
                s = cur[c]
                if c > 0:
                    s += cur[c - 1]
                if c < n - 1:
                    s += cur[c + 1]
                nxt[c] = s % MOD
        cur = nxt
    return sum(cur) % MOD
''',
    tests=[[[[0, 0, 0], [0, 1, 0], [0, 0, 0]]], [[[0, 1, 0], [1, 0, 1]]], [[[0]]], [[[1]]], [[[0, 1, 0, 0]]],
           [[[0], [0], [0]]], [[[0], [1], [0]]], [[[0, 0], [1, 1], [0, 0]]], [[[0, 0, 0], [0, 0, 0]]],
           [[[0, 0, 0, 0, 0], [1, 0, 1, 0, 1], [0, 0, 0, 0, 0], [0, 1, 1, 1, 0]]]],
)
_r = rnd(9201)
p["tests"].append([[[0] * 100 for _ in range(100)]])
p["tests"].append([_bin_grid(_r, 100, 100, 0.12)])
p["tests"].append([_bin_grid(_r, 100, 37, 0.3)])


def b_falling(grid):
    h, w = len(grid), len(grid[0])

    def go(r, c):
        if grid[r][c] == 1:
            return 0
        if r == h - 1:
            return 1
        return sum(go(r + 1, c + d) for d in (-1, 0, 1) if 0 <= c + d < w)
    return sum(go(0, c) for c in range(w)) % MOD


def v_falling(tests):
    for t in tests:
        g = t["args"][0]
        assert _is_rect(g) and len(g) <= 100 and len(g[0]) <= 100 and _is_bin(g)
        assert 0 <= t["expected"] < MOD


CHECKS["falling-paths-count-blocked"] = (b_falling, lambda r: [_bin_grid(r, r.randint(1, 5), r.randint(1, 5), r.choice([0.0, 0.2, 0.4]))], "exact")
VALIDATE["falling-paths-count-blocked"] = v_falling


# ---------------------------------------------------------------- grid-paths-with-diagonal-steps
p = add(
    id="grid-paths-with-diagonal-steps", title="Grid Routes with Diagonal Shortcuts", diff="Easy", topic=TOPIC,
    fn="countRoutesWithDiagonals", params=[("grid", "int[][]")], ret="int", cmp="exact",
    desc="<p>In a rectangular <code>grid</code>, <code>0</code> is a free cell and <code>1</code> is a blocked cell. A courier starts in the top-left cell and must reach the bottom-right cell. In one move the courier may go one cell <strong>right</strong>, one cell <strong>down</strong>, or one cell <strong>diagonally down and to the right</strong>, and may never stand on a blocked cell.</p><p>Return the number of different routes (two routes differ when their lists of visited cells differ), modulo <code>1,000,000,007</code>. If the start or the destination is blocked the answer is <code>0</code>.</p><pre>grid = [[0,0],\n        [0,0]]     ->  3     (right+down, down+right, diagonal)\ngrid = [[0,0,0],\n        [0,1,0],\n        [0,0,0]]   ->  4</pre>",
    constraints=["1 &le; grid.length, grid[0].length &le; 100", "grid[i][j] is 0 or 1", "The start and destination cells may be blocked"],
    hints=["This is the classic right/down counting problem with one extra kind of move. Think about which cells a route can come from when it enters a given cell.",
           "A cell can be entered from above, from the left or from the upper-left diagonal. Let <code>ways[r][c]</code> be the number of routes ending there.",
           "<code>ways[r][c] = ways[r-1][c] + ways[r][c-1] + ways[r-1][c-1]</code> for a free cell, 0 for a blocked one, and <code>ways[0][0] = 1</code> if the start is free. Take every sum modulo 1,000,000,007."],
    editorial=["Every route into a free cell ends with exactly one of three moves, so the routes into it split into three disjoint groups: those arriving from the cell above, from the cell on the left, and from the upper-left diagonal neighbour. Hence <code>ways[r][c] = ways[r-1][c] + ways[r][c-1] + ways[r-1][c-1]</code>, where neighbours outside the grid contribute 0 and a blocked cell is set to 0 so no route can use it.",
               "Fill the table row by row starting from <code>ways[0][0] = 1</code>. Each row needs the previous row, so a rolling pair of arrays gives O(n) memory; time is O(m &middot; n). Without obstacles these numbers are the central Delannoy numbers on a square grid, which is a good way to sanity-check small cases (1, 3, 13, 63, ...)."],
    time="O(m &middot; n)", space="O(n)",
    solution='''def countRoutesWithDiagonals(grid):
    MOD = 10 ** 9 + 7
    n = len(grid[0])
    prev = [0] * n
    for r, row in enumerate(grid):
        cur = [0] * n
        for c in range(n):
            if row[c] == 1:
                continue
            if r == 0 and c == 0:
                cur[c] = 1
                continue
            s = prev[c]
            if c > 0:
                s += cur[c - 1] + prev[c - 1]
            cur[c] = s % MOD
        prev = cur
    return prev[-1]
''',
    tests=[[[[0, 0], [0, 0]]], [[[0, 0, 0], [0, 1, 0], [0, 0, 0]]], [[[0]]], [[[1]]], [[[0, 0, 0, 0]]], [[[0], [0], [0]]],
           [[[0, 1], [1, 0]]], [[[1, 0], [0, 0]]], [[[0, 0], [0, 1]]], [[[0, 0, 0], [0, 0, 0], [0, 0, 0]]],
           [[[0, 1, 0, 0], [0, 0, 1, 0], [1, 0, 0, 0], [0, 0, 0, 0]]]],
)
_r = rnd(9202)
p["tests"].append([[[0] * 100 for _ in range(100)]])
p["tests"].append([_free_ends(_bin_grid(_r, 100, 100, 0.1))])
p["tests"].append([_free_ends(_bin_grid(_r, 63, 100, 0.25))])


def b_diag(grid):
    h, w = len(grid), len(grid[0])

    def go(r, c):
        if r >= h or c >= w or grid[r][c] == 1:
            return 0
        if r == h - 1 and c == w - 1:
            return 1
        return go(r + 1, c) + go(r, c + 1) + go(r + 1, c + 1)
    return go(0, 0) % MOD


def v_diag(tests):
    for t in tests:
        g = t["args"][0]
        assert _is_rect(g) and len(g) <= 100 and len(g[0]) <= 100 and _is_bin(g)
        assert 0 <= t["expected"] < MOD


CHECKS["grid-paths-with-diagonal-steps"] = (b_diag, lambda r: [_bin_grid(r, r.randint(1, 5), r.randint(1, 5), r.choice([0.0, 0.15, 0.3]))], "exact")
VALIDATE["grid-paths-with-diagonal-steps"] = v_diag


# ---------------------------------------------------------------- grid-paths-within-diagonal-band
p = add(
    id="grid-paths-within-diagonal-band", title="Square Grid Paths Near the Diagonal", diff="Easy", topic=TOPIC,
    fn="countBandPaths", params=[("n", "int"), ("w", "int")], ret="int", cmp="exact",
    desc="<p>A traveller walks on an <code>n x n</code> grid from the top-left cell <code>(0, 0)</code> to the bottom-right cell <code>(n-1, n-1)</code>, moving one step <strong>right</strong> or one step <strong>down</strong> at a time. The traveller must stay within <code>w</code> cells of the main diagonal: every visited cell <code>(r, c)</code> must satisfy <code>|r - c| &le; w</code>.</p><p>Return the number of such routes modulo <code>1,000,000,007</code>.</p><pre>n = 3, w = 1  ->  4\nn = 4, w = 1  ->  8\nn = 4, w = 0  ->  0   (no route can stay on the diagonal)\nn = 1, w = 0  ->  1</pre>",
    constraints=["1 &le; n &le; 500", "0 &le; w &le; n"],
    hints=["Without the band restriction the count is a binomial coefficient, but the restriction removes cells in a pattern. A table over cells is natural.",
           "Let <code>ways[r][c]</code> count routes ending in <code>(r, c)</code>. Cells outside the band get 0, which forces every route to avoid them.",
           "Only cells with <code>max(0, r-w) &le; c &le; min(n-1, r+w)</code> matter in row r, so each row needs at most 2w+1 updates. Keep a single array and zero the cell just left of the band when the band slides right."],
    editorial=["Treat the cells outside the band exactly like obstacles: they hold 0 routes. For the other cells <code>ways[r][c] = ways[r-1][c] + ways[r][c-1]</code>, with <code>ways[0][0] = 1</code>. A route is valid precisely when all its cells are inside the band, which the zeros guarantee.",
               "With a single array of width n, row r is computed in place for the columns of the band only. When the band moves one column to the right, the value left over just outside its left edge (<code>c = r - w - 1</code>) must be cleared before it can leak into the next row. That visits O(n &middot; min(n, w)) cells in total, at most O(n<sup>2</sup>), and uses O(n) space. For w &ge; n-1 the band is the whole grid and the answer is the binomial coefficient C(2n-2, n-1) modulo the prime."],
    time="O(n &middot; min(n, w))", space="O(n)",
    solution='''def countBandPaths(n, w):
    MOD = 10 ** 9 + 7
    ways = [0] * n
    for r in range(n):
        lo = max(0, r - w)
        hi = min(n - 1, r + w)
        if lo > 0:
            ways[lo - 1] = 0
        for c in range(lo, hi + 1):
            if r == 0 and c == 0:
                ways[c] = 1
            else:
                v = ways[c]
                if c > 0:
                    v += ways[c - 1]
                ways[c] = v % MOD
    return ways[n - 1]
''',
    tests=[[3, 1], [4, 1], [4, 0], [1, 0], [1, 1], [2, 0], [2, 1], [5, 1], [5, 2], [6, 5], [6, 6], [7, 3]],
)
p["tests"].append([500, 3])
p["tests"].append([500, 500])
p["tests"].append([500, 40])


def b_band(n, w):
    # full 2-D table with an explicit band test, exact integers, remainder only at the end
    t = [[0] * n for _ in range(n)]
    for r in range(n):
        for c in range(n):
            if abs(r - c) > w:
                continue
            if r == 0 and c == 0:
                t[r][c] = 1
            else:
                t[r][c] = (t[r - 1][c] if r else 0) + (t[r][c - 1] if c else 0)
    return t[n - 1][n - 1] % MOD


def v_band(tests):
    for t in tests:
        n, w = t["args"]
        assert 1 <= n <= 500 and 0 <= w <= n
        assert 0 <= t["expected"] < MOD


CHECKS["grid-paths-within-diagonal-band"] = (b_band, lambda r: [r.randint(1, 7), r.randint(0, 7)], "exact")
VALIDATE["grid-paths-within-diagonal-band"] = v_band


# ================================================================ MEDIUM

# ---------------------------------------------------------------- grid-paths-with-exactly-k-turns
p = add(
    id="grid-paths-with-exactly-k-turns", title="Grid Routes with Exactly K Turns", diff="Medium", topic=TOPIC,
    fn="countRoutesWithTurns", params=[("grid", "int[][]"), ("k", "int")], ret="int", cmp="exact",
    desc="<p>A vehicle drives from the top-left cell to the bottom-right cell of a rectangular <code>grid</code> (<code>0</code> = free, <code>1</code> = blocked), moving one cell <strong>right</strong> or one cell <strong>down</strong> per step and never entering a blocked cell. A <em>turn</em> happens when two consecutive moves go in different directions (right followed by down, or down followed by right). The first move is never a turn.</p><p>Return the number of routes that contain <strong>exactly</strong> <code>k</code> turns, modulo <code>1,000,000,007</code>. If the start or the destination is blocked the answer is <code>0</code>. In a 1&times;1 grid the only route makes no moves and has 0 turns.</p><pre>grid = 3 rows x 4 columns, all free\nk = 0 -> 0     (a straight line cannot reach the opposite corner)\nk = 1 -> 2     (RRRDD and DDRRR)\nk = 2 -> 3\nk = 3 -> 4\nk = 4 -> 1</pre>",
    constraints=["1 &le; grid.length, grid[0].length &le; 40", "0 &le; k &le; 40", "grid[i][j] is 0 or 1"],
    hints=["A plain cell count is not enough: to know whether the next move is a turn you must remember the direction of the previous move.",
           "Keep two tables per cell, <code>R[r][c][t]</code> and <code>D[r][c][t]</code>: routes ending in <code>(r, c)</code> whose last move was right (or down) and that used t turns so far.",
           "Entering <code>(r, c)</code> by a right move: <code>R[r][c][t] = R[r][c-1][t] + D[r][c-1][t-1]</code> (continuing straight keeps t, switching direction adds one). Down moves are symmetric. Seed the two first moves out of the start with t = 0."],
    editorial=["Add the information the rule depends on to the state: the direction of the last move and the number of turns so far. For a free cell, routes whose last move was right come either from a cell on the left that was also entered by a right move (no new turn) or from one that was entered by a down move (a new turn). So <code>R[r][c][t] = R[r][c-1][t] + D[r][c-1][t-1]</code>, and symmetrically <code>D[r][c][t] = D[r-1][c][t] + R[r-1][c][t-1]</code>. Blocked cells hold zeros.",
               "The start cell has no previous move, so the first move is seeded directly: moving right into <code>(0, 1)</code> gives <code>R = 1</code> at t = 0, and moving down into <code>(1, 0)</code> gives <code>D = 1</code> at t = 0. The answer is <code>R + D</code> at the destination for t = k, plus the special case of a 1&times;1 grid. States: O(m &middot; n &middot; k); each is computed in O(1)."],
    time="O(m &middot; n &middot; k)", space="O(m &middot; n &middot; k)",
    solution='''def countRoutesWithTurns(grid, k):
    MOD = 10 ** 9 + 7
    m, n = len(grid), len(grid[0])
    if grid[0][0] == 1 or grid[m - 1][n - 1] == 1:
        return 0
    if m == 1 and n == 1:
        return 1 if k == 0 else 0
    zero = [0] * (k + 1)
    R = [[zero] * n for _ in range(m)]
    D = [[zero] * n for _ in range(m)]
    for r in range(m):
        for c in range(n):
            if grid[r][c] == 1:
                continue
            nr = zero[:]
            nd = zero[:]
            if c > 0:
                if r == 0 and c == 1:
                    nr[0] = 1
                else:
                    pr, pd = R[r][c - 1], D[r][c - 1]
                    for t in range(k + 1):
                        nr[t] = (pr[t] + (pd[t - 1] if t else 0)) % MOD
            if r > 0:
                if r == 1 and c == 0:
                    nd[0] = 1
                else:
                    pr, pd = R[r - 1][c], D[r - 1][c]
                    for t in range(k + 1):
                        nd[t] = (pd[t] + (pr[t - 1] if t else 0)) % MOD
            R[r][c] = nr
            D[r][c] = nd
    return (R[m - 1][n - 1][k] + D[m - 1][n - 1][k]) % MOD
''',
    tests=[[[[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]], 0], [[[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]], 1],
           [[[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]], 2], [[[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]], 4],
           [[[0]], 0], [[[0]], 3], [[[1]], 0], [[[0, 0, 0, 0]], 0], [[[0], [0], [0]], 1],
           [[[0, 0, 0], [0, 1, 0], [0, 0, 0]], 1], [[[0, 0, 0], [0, 1, 0], [0, 0, 0]], 2],
           [[[0, 0], [0, 0]], 1], [[[0, 1, 0], [0, 0, 0], [1, 0, 0]], 3], [[[0, 0], [0, 0]], 5]],
)
_r = rnd(9203)
p["tests"].append([[[0] * 40 for _ in range(40)], 20])
p["tests"].append([_free_ends(_bin_grid(_r, 40, 40, 0.08)), 17])
p["tests"].append([[[0] * 40 for _ in range(40)], 40])


def b_turns(grid, k):
    h, w = len(grid), len(grid[0])
    cnt = [0]

    def go(r, c, last, turns):
        if r >= h or c >= w or grid[r][c] == 1 or turns > k:
            return
        if r == h - 1 and c == w - 1:
            if turns == k:
                cnt[0] += 1
            return
        for d, (dr, dc) in enumerate(((0, 1), (1, 0))):
            go(r + dr, c + dc, d, turns + (1 if last is not None and last != d else 0))
    go(0, 0, None, 0)
    return cnt[0] % MOD


def v_turns(tests):
    for t in tests:
        g, k = t["args"]
        assert _is_rect(g) and len(g) <= 40 and len(g[0]) <= 40 and _is_bin(g)
        assert 0 <= k <= 40 and 0 <= t["expected"] < MOD


CHECKS["grid-paths-with-exactly-k-turns"] = (b_turns, lambda r: [_bin_grid(r, r.randint(1, 5), r.randint(1, 5), r.choice([0.0, 0.15, 0.3])), r.randint(0, 6)], "exact")
VALIDATE["grid-paths-with-exactly-k-turns"] = v_turns


# ---------------------------------------------------------------- grid-paths-through-at-most-one-wall
p = add(
    id="grid-paths-through-at-most-one-wall", title="Grid Routes Through at Most One Wall", diff="Medium", topic=TOPIC,
    fn="countRoutesOneWall", params=[("grid", "int[][]")], ret="int", cmp="exact",
    desc="<p>A hiker walks from the top-left cell to the bottom-right cell of a rectangular <code>grid</code>, moving one step <strong>right</strong> or one step <strong>down</strong> at a time. A cell with value <code>1</code> contains a wall and a cell with value <code>0</code> is open. The hiker has a pickaxe that lets them pass through <strong>at most one</strong> wall cell during the whole walk (the start and destination cells count too if they are walls).</p><p>Return the number of different routes that use at most one wall cell, modulo <code>1,000,000,007</code>.</p><pre>grid = [[0,1],\n        [1,0]]   ->  2   (each of the two routes crosses exactly one wall)\ngrid = [[0,1,0],\n        [1,1,0],\n        [0,0,0]] ->  2</pre>",
    constraints=["1 &le; grid.length, grid[0].length &le; 100", "grid[i][j] is 0 or 1"],
    hints=["Counting routes that avoid all walls is the easy part. The new twist is a resource (one pickaxe use) that a route may or may not have spent.",
           "Store two numbers per cell: routes that arrive having used the pickaxe 0 times and routes that arrive having used it exactly once.",
           "Entering an open cell keeps both counts. Entering a wall cell moves every unused-pickaxe route into the used column, and routes that already spent it are dropped. The answer is the sum of both counts at the destination."],
    editorial=["Let <code>a[r][c]</code> be the number of routes into <code>(r, c)</code> using no wall so far and <code>b[r][c]</code> those using exactly one. First gather what comes from the cell above and the cell to the left: <code>a' = a[r-1][c] + a[r][c-1]</code>, <code>b' = b[r-1][c] + b[r][c-1]</code> (for the start cell, <code>a' = 1</code>, <code>b' = 0</code>).",
               "If the cell is open the new values are <code>a = a'</code>, <code>b = b'</code>. If it is a wall, every route that has not used the pickaxe now uses it: <code>a = 0</code>, <code>b = a'</code>, and routes in <code>b'</code> would need a second wall so they vanish. The answer is <code>a + b</code> at the bottom-right cell. A single array of pairs per row gives O(n) memory and O(m &middot; n) time. The same layering trick (an extra dimension for a small budget) works for any 'at most j walls' variant at O(m &middot; n &middot; j)."],
    time="O(m &middot; n)", space="O(n)",
    solution='''def countRoutesOneWall(grid):
    MOD = 10 ** 9 + 7
    m, n = len(grid), len(grid[0])
    cur = [[0, 0] for _ in range(n)]
    for r in range(m):
        for c in range(n):
            if r == 0 and c == 0:
                a, b = 1, 0
            else:
                a = b = 0
                if r > 0:
                    a += cur[c][0]
                    b += cur[c][1]
                if c > 0:
                    a += cur[c - 1][0]
                    b += cur[c - 1][1]
            if grid[r][c] == 1:
                a, b = 0, a
            cur[c] = [a % MOD, b % MOD]
    return (cur[n - 1][0] + cur[n - 1][1]) % MOD
''',
    tests=[[[[0, 1], [1, 0]]], [[[0, 1, 0], [1, 1, 0], [0, 0, 0]]], [[[0]]], [[[1]]], [[[1, 1]]], [[[0, 1, 0, 1, 0]]],
           [[[1], [0], [1]]], [[[0, 0], [0, 0]]], [[[1, 1], [1, 1]]], [[[1, 0], [0, 0]]],
           [[[0, 1, 1], [1, 1, 0], [0, 0, 0]]], [[[0, 0, 1, 0], [1, 0, 1, 0], [1, 1, 0, 0], [0, 0, 0, 0]]]],
)
_r = rnd(9204)
p["tests"].append([[[0] * 100 for _ in range(100)]])
p["tests"].append([_bin_grid(_r, 100, 100, 0.05)])
p["tests"].append([_bin_grid(_r, 100, 100, 0.3)])
p["tests"].append([_bin_grid(_r, 60, 100, 0.12)])


def b_wall(grid):
    h, w = len(grid), len(grid[0])
    cnt = [0]

    def go(r, c, walls):
        walls += grid[r][c]
        if walls > 1:
            return
        if r == h - 1 and c == w - 1:
            cnt[0] += 1
            return
        if r + 1 < h:
            go(r + 1, c, walls)
        if c + 1 < w:
            go(r, c + 1, walls)
    go(0, 0, 0)
    return cnt[0] % MOD


def v_wall(tests):
    for t in tests:
        g = t["args"][0]
        assert _is_rect(g) and len(g) <= 100 and len(g[0]) <= 100 and _is_bin(g)
        assert 0 <= t["expected"] < MOD


CHECKS["grid-paths-through-at-most-one-wall"] = (b_wall, lambda r: [_bin_grid(r, r.randint(1, 5), r.randint(1, 5), r.choice([0.0, 0.3, 0.5]))], "exact")
VALIDATE["grid-paths-through-at-most-one-wall"] = v_wall


# ---------------------------------------------------------------- king-walks-on-blocked-board
p = add(
    id="king-walks-on-blocked-board", title="Chess King Walks of Fixed Length", diff="Medium", topic=TOPIC,
    fn="countKingWalks", params=[("board", "int[][]"), ("k", "int")], ret="int", cmp="exact",
    desc="<p>A chess king stands on the top-left cell of a rectangular <code>board</code>. Cells with <code>1</code> are blocked, cells with <code>0</code> are free. In one move the king goes to any of the up to 8 neighbouring cells (horizontally, vertically or diagonally adjacent) that lie on the board and are free. The king <strong>may revisit cells</strong>.</p><p>Return the number of different move sequences of <strong>exactly</strong> <code>k</code> moves that end on the bottom-right cell, modulo <code>1,000,000,007</code>. Two sequences differ if the lists of visited cells differ. If the start or the destination is blocked the answer is <code>0</code>.</p><pre>board = 2x2 all free   k = 1 -> 1,  k = 2 -> 2,  k = 3 -> 7\nboard = [[0,1],[1,0]], k = 2 -> 0</pre><p>With <code>k = 0</code> the king does not move, so the answer is <code>1</code> only when the board has a single free cell, and <code>0</code> otherwise.</p>",
    constraints=["1 &le; board.length, board[0].length &le; 15", "0 &le; k &le; 60", "board[i][j] is 0 or 1"],
    hints=["Walks may revisit cells, so there is no 'visited' set. What matters about a partial walk is only where it currently stands and how many moves are left.",
           "Let <code>f[t][r][c]</code> be the number of walks of exactly t moves that start at the top-left and end at <code>(r, c)</code>.",
           "<code>f[t][r][c]</code> is the sum of <code>f[t-1]</code> over the free neighbours of <code>(r, c)</code> (up to 8 of them), with <code>f[0]</code> equal to 1 at the start and 0 elsewhere. Only the previous layer is needed."],
    editorial=["A walk of t moves ending at a free cell has a last move from one of its neighbouring free cells, after a walk of t-1 moves. That gives the recurrence <code>f[t][r][c] = sum of f[t-1][r'][c']</code> over the 8 neighbours (r', c') that are inside the board and free, and f is 0 on blocked cells. Layer 0 has a single 1 on the start cell. After k layers the answer is <code>f[k]</code> at the bottom-right cell.",
               "Since layer t only reads layer t-1, two m &times; n arrays are enough. The work is k &middot; m &middot; n &middot; 8 additions, tiny for this input size. Reduce modulo 1,000,000,007 after each layer. The recurrence is exactly 'multiply by the adjacency matrix of the king graph k times', which is why a much larger k would call for matrix exponentiation."],
    time="O(k &middot; m &middot; n)", space="O(m &middot; n)",
    solution='''def countKingWalks(board, k):
    MOD = 10 ** 9 + 7
    m, n = len(board), len(board[0])
    if board[0][0] == 1 or board[m - 1][n - 1] == 1:
        return 0
    cur = [[0] * n for _ in range(m)]
    cur[0][0] = 1
    for _ in range(k):
        nxt = [[0] * n for _ in range(m)]
        for r in range(m):
            for c in range(n):
                if board[r][c] == 1:
                    continue
                s = 0
                for dr in (-1, 0, 1):
                    a = r + dr
                    if 0 <= a < m:
                        row = cur[a]
                        for dc in (-1, 0, 1):
                            b = c + dc
                            if (dr or dc) and 0 <= b < n:
                                s += row[b]
                nxt[r][c] = s % MOD
        cur = nxt
    return cur[m - 1][n - 1]
''',
    tests=[[[[0, 0], [0, 0]], 1], [[[0, 0], [0, 0]], 2], [[[0, 0], [0, 0]], 3], [[[0, 1], [1, 0]], 2], [[[0, 1], [1, 0]], 1],
           [[[0]], 0], [[[0]], 4], [[[0, 0, 0]], 2], [[[0, 0, 0]], 0], [[[0], [0], [0]], 3], [[[1, 0], [0, 0]], 2],
           [[[0, 0, 0], [0, 1, 0], [0, 0, 0]], 4], [[[0, 0, 0], [1, 1, 1], [0, 0, 0]], 7], [[[0, 0], [0, 0]], 0]],
)
_r = rnd(9205)
p["tests"].append([[[0] * 15 for _ in range(15)], 60])
p["tests"].append([_free_ends(_bin_grid(_r, 15, 15, 0.2)), 55])
p["tests"].append([_free_ends(_bin_grid(_r, 12, 15, 0.1)), 28])


def b_king(board, k):
    m, n = len(board), len(board[0])
    cells = [(r, c) for r in range(m) for c in range(n)]
    idx = {x: i for i, x in enumerate(cells)}
    s = len(cells)
    A = [[0] * s for _ in range(s)]
    for (r, c) in cells:
        if board[r][c] == 1:
            continue
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                a, b = r + dr, c + dc
                if (dr or dc) and 0 <= a < m and 0 <= b < n and board[a][b] == 0:
                    A[idx[(r, c)]][idx[(a, b)]] = 1
    vec = [0] * s
    if board[0][0] == 0:
        vec[0] = 1
    for _ in range(k):
        vec = [sum(vec[i] * A[i][j] for i in range(s)) for j in range(s)]
    return vec[s - 1] % MOD if board[m - 1][n - 1] == 0 else 0


def v_king(tests):
    for t in tests:
        g, k = t["args"]
        assert _is_rect(g) and len(g) <= 15 and len(g[0]) <= 15 and _is_bin(g)
        assert 0 <= k <= 60 and 0 <= t["expected"] < MOD


CHECKS["king-walks-on-blocked-board"] = (b_king, lambda r: [_bin_grid(r, r.randint(1, 4), r.randint(1, 4), r.choice([0.0, 0.2, 0.4])), r.randint(0, 7)], "exact")
VALIDATE["king-walks-on-blocked-board"] = v_king


# ---------------------------------------------------------------- knight-walks-fixed-length
p = add(
    id="knight-walks-fixed-length", title="Knight Walks of Fixed Length", diff="Medium", topic=TOPIC,
    fn="countKnightWalks", params=[("n", "int"), ("k", "int"), ("sr", "int"), ("sc", "int"), ("tr", "int"), ("tc", "int")], ret="int", cmp="exact",
    desc="<p>A chess knight stands on cell <code>(sr, sc)</code> of an empty <code>n x n</code> board (rows and columns are numbered from 0). One move changes the position by <code>(&plusmn;1, &plusmn;2)</code> or <code>(&plusmn;2, &plusmn;1)</code> and must stay on the board. The knight may visit the same cell any number of times.</p><p>Return the number of different sequences of <strong>exactly</strong> <code>k</code> moves that finish on cell <code>(tr, tc)</code>, modulo <code>1,000,000,007</code>. Two sequences differ when their lists of visited cells differ.</p><pre>n = 3, k = 2, from (0,0) to (0,0)  ->  2\nn = 3, k = 2, from (0,0) to (2,2)  ->  0\nn = 3, k = 1, from (0,0) to (1,2)  ->  1</pre>",
    constraints=["1 &le; n &le; 20", "0 &le; k &le; 50", "0 &le; sr, sc, tr, tc &lt; n"],
    hints=["Do not try to enumerate the walks: there are up to 8<sup>k</sup> of them. How many different (cell, moves left) situations are there instead?",
           "Let <code>f[t][r][c]</code> be the number of t-move walks from the start that end at <code>(r, c)</code>.",
           "Push each cell's count to the up to 8 cells a knight reaches from it to build layer t+1 from layer t, starting from a single 1 on the start cell. Read the answer from layer k at the target."],
    editorial=["A walk of t+1 moves is a walk of t moves followed by one more knight move. So if <code>f[t]</code> holds the number of t-move walks ending at each cell, then <code>f[t+1][b]</code> is the sum of <code>f[t][a]</code> over all cells a from which a knight move reaches b. Equivalently, push the count of every cell to its up to 8 knight neighbours. Layer 0 contains a single 1 on the start cell.",
               "After k layers, the answer is <code>f[k][tr][tc]</code>. Each layer costs 8 &middot; n<sup>2</sup> operations, so the total is O(k &middot; n<sup>2</sup>) time and O(n<sup>2</sup>) space. Counts are reduced modulo 1,000,000,007 per layer. A parity fact gives quick sanity checks: every knight move flips the colour of the square, so if k is odd the target must have the opposite colour to the start, otherwise the answer is 0."],
    time="O(k &middot; n<sup>2</sup>)", space="O(n<sup>2</sup>)",
    solution='''def countKnightWalks(n, k, sr, sc, tr, tc):
    MOD = 10 ** 9 + 7
    moves = [(1, 2), (2, 1), (-1, 2), (-2, 1), (1, -2), (2, -1), (-1, -2), (-2, -1)]
    cur = [[0] * n for _ in range(n)]
    cur[sr][sc] = 1
    for _ in range(k):
        nxt = [[0] * n for _ in range(n)]
        for r in range(n):
            for c in range(n):
                v = cur[r][c]
                if v:
                    for dr, dc in moves:
                        a, b = r + dr, c + dc
                        if 0 <= a < n and 0 <= b < n:
                            nxt[a][b] += v
        cur = [[x % MOD for x in row] for row in nxt]
    return cur[tr][tc]
''',
    tests=[[3, 2, 0, 0, 0, 0], [3, 2, 0, 0, 2, 2], [3, 1, 0, 0, 1, 2], [1, 0, 0, 0, 0, 0], [1, 3, 0, 0, 0, 0], [2, 1, 0, 0, 1, 1],
           [3, 4, 1, 1, 1, 1], [3, 0, 2, 2, 2, 2], [3, 0, 0, 0, 1, 1], [4, 3, 0, 0, 3, 2], [4, 4, 0, 0, 3, 3],
           [5, 5, 2, 2, 0, 1], [8, 6, 0, 0, 7, 7]],
)
p["tests"].append([20, 50, 0, 0, 19, 19])
p["tests"].append([20, 49, 3, 7, 12, 10])
p["tests"].append([20, 50, 9, 9, 10, 10])


def b_knight(n, k, sr, sc, tr, tc):
    # pull-style layers with exact integers; remainder only at the end
    moves = ((1, 2), (2, 1), (-1, 2), (-2, 1), (1, -2), (2, -1), (-1, -2), (-2, -1))
    f = {(r, c): 0 for r in range(n) for c in range(n)}
    f[(sr, sc)] = 1
    for _ in range(k):
        f = {(r, c): sum(f.get((r + dr, c + dc), 0) for dr, dc in moves) for (r, c) in f}
    return f[(tr, tc)] % MOD


def g_knight(r):
    n = r.randint(1, 5)
    return [n, r.randint(0, 7), r.randrange(n), r.randrange(n), r.randrange(n), r.randrange(n)]


def v_knight(tests):
    for t in tests:
        n, k, sr, sc, tr, tc = t["args"]
        assert 1 <= n <= 20 and 0 <= k <= 50
        assert all(0 <= x < n for x in (sr, sc, tr, tc))
        assert 0 <= t["expected"] < MOD


CHECKS["knight-walks-fixed-length"] = (b_knight, g_knight, "exact")
VALIDATE["knight-walks-fixed-length"] = v_knight


# ---------------------------------------------------------------- paths-around-forbidden-rectangle
p = add(
    id="paths-around-forbidden-rectangle", title="Grid Routes Around a Forbidden Rectangle", diff="Medium", topic=TOPIC,
    fn="countRoutesAvoidingRectangle", params=[("m", "int"), ("n", "int"), ("r1", "int"), ("c1", "int"), ("r2", "int"), ("c2", "int")], ret="int", cmp="exact",
    desc="<p>A courier travels across an <code>m x n</code> grid from the top-left cell <code>(0, 0)</code> to the bottom-right cell <code>(m-1, n-1)</code>, moving one step <strong>right</strong> or one step <strong>down</strong> at a time. All cells <code>(r, c)</code> with <code>r1 &le; r &le; r2</code> and <code>c1 &le; c &le; c2</code> form a flooded rectangle that must not be entered. The rectangle never contains the start or the destination cell.</p><p>Return the number of routes that avoid the rectangle, modulo <code>1,000,000,007</code>. The grid is far too large to fill cell by cell.</p><pre>m = 3, n = 3, rectangle rows 1..1, columns 1..1  ->  2\nm = 3, n = 3, rectangle rows 1..1, columns 0..2  ->  0\nm = 2, n = 5, rectangle rows 0..0, columns 2..3  ->  2</pre>",
    constraints=["2 &le; m &middot; n and 1 &le; m, n &le; 50,000", "0 &le; r1 &le; r2 &lt; m and 0 &le; c1 &le; c2 &lt; n", "The rectangle contains neither (0, 0) nor (m-1, n-1)"],
    hints=["Counting all routes is one binomial coefficient: C(m+n-2, m-1). Maybe it is easier to count the routes that do touch the rectangle and subtract.",
           "Every route that touches the rectangle has a unique first cell inside it, and that cell is either on the top edge (entered from above) or on the left edge (entered from the left).",
           "For each entry cell multiply (routes from the start to the cell just before it) by (routes from the entry cell to the destination). Both factors are binomials, so the total is O(m + n) terms. Precompute factorials and inverse factorials modulo the prime."],
    editorial=["Routes avoiding the rectangle = all routes minus routes that touch it. A route that touches the rectangle enters it for the first time at exactly one cell. That cell is either in the top row of the rectangle (<code>r = r1</code>, columns c1..c2) and was entered from the cell above, or in its left column (<code>c = c1</code>, rows r1..r2) and was entered from the cell to its left. The cell (r1, c1) is allowed to be entered from both sides, and these two situations are different routes, so nothing is double counted.",
               "Nothing before the entry touches the rectangle: the cell above a top-edge entry lies in row r1-1 and the cell to the left of a left-edge entry lies in column c1-1, so any route to it is automatically clear. Hence the number of bad routes through the top edge is the sum over c of <code>W(0,0 -> r1-1,c) &middot; W(r1,c -> m-1,n-1)</code> (only if r1 &gt; 0), and similarly for the left edge, where <code>W(a,b -> x,y) = C((x-a)+(y-b), x-a)</code>. With factorial tables modulo the prime the whole answer takes O(m + n) time."],
    time="O(m + n)", space="O(m + n)",
    solution='''def countRoutesAvoidingRectangle(m, n, r1, c1, r2, c2):
    MOD = 10 ** 9 + 7
    size = m + n
    fact = [1] * (size + 1)
    for i in range(1, size + 1):
        fact[i] = fact[i - 1] * i % MOD
    inv = [1] * (size + 1)
    inv[size] = pow(fact[size], MOD - 2, MOD)
    for i in range(size, 0, -1):
        inv[i - 1] = inv[i] * i % MOD

    def ways(dr, dc):
        if dr < 0 or dc < 0:
            return 0
        return fact[dr + dc] * inv[dr] % MOD * inv[dc] % MOD

    total = ways(m - 1, n - 1)
    bad = 0
    if r1 > 0:
        for c in range(c1, c2 + 1):
            bad += ways(r1 - 1, c) * ways(m - 1 - r1, n - 1 - c)
    if c1 > 0:
        for r in range(r1, r2 + 1):
            bad += ways(r, c1 - 1) * ways(m - 1 - r, n - 1 - c1)
    return (total - bad) % MOD
''',
    tests=[[3, 3, 1, 1, 1, 1], [3, 3, 1, 0, 1, 2], [2, 5, 0, 2, 0, 3], [2, 2, 0, 1, 0, 1], [2, 2, 1, 0, 1, 0],
           [1, 5, 0, 2, 0, 2], [5, 1, 3, 0, 3, 0], [4, 4, 1, 1, 2, 2], [4, 4, 0, 1, 2, 3], [4, 4, 1, 0, 3, 2],
           [5, 6, 2, 0, 2, 2], [6, 5, 0, 2, 4, 3], [3, 4, 1, 1, 2, 2]],
)
p["tests"].append([50000, 50000, 20000, 15000, 49000, 30000])
p["tests"].append([50000, 50000, 1, 1, 49998, 49998])
p["tests"].append([50000, 3, 25000, 1, 40000, 1])
p["tests"].append([30001, 49999, 0, 100, 30000, 49997])


def b_rect(m, n, r1, c1, r2, c2):
    dp = [[0] * n for _ in range(m)]
    for r in range(m):
        for c in range(n):
            if r1 <= r <= r2 and c1 <= c <= c2:
                continue
            if r == 0 and c == 0:
                dp[r][c] = 1
            else:
                dp[r][c] = (dp[r - 1][c] if r else 0) + (dp[r][c - 1] if c else 0)
    return dp[m - 1][n - 1] % MOD


def g_rect(r):
    while True:
        m, n = r.randint(1, 7), r.randint(1, 7)
        r1, r2 = sorted((r.randrange(m), r.randrange(m)))
        c1, c2 = sorted((r.randrange(n), r.randrange(n)))
        if m * n < 2:
            continue
        if r1 <= 0 <= r2 and c1 <= 0 <= c2:
            continue
        if r1 <= m - 1 <= r2 and c1 <= n - 1 <= c2:
            continue
        return [m, n, r1, c1, r2, c2]


def v_rect(tests):
    for t in tests:
        m, n, r1, c1, r2, c2 = t["args"]
        assert 1 <= m <= 50000 and 1 <= n <= 50000 and m * n >= 2
        assert 0 <= r1 <= r2 < m and 0 <= c1 <= c2 < n
        assert not (r1 == 0 and c1 == 0), "rectangle contains the start"
        assert not (r2 == m - 1 and c2 == n - 1), "rectangle contains the destination"
        assert 0 <= t["expected"] < MOD


CHECKS["paths-around-forbidden-rectangle"] = (b_rect, g_rect, "exact")
VALIDATE["paths-around-forbidden-rectangle"] = v_rect


# ================================================================ HARD

# ---------------------------------------------------------------- grid-paths-huge-grid-few-obstacles
p = add(
    id="grid-paths-huge-grid-few-obstacles", title="Routes Through a Huge Grid with Few Obstacles", diff="Hard", topic=TOPIC, tier="extra",
    fn="countRoutesFewObstacles", params=[("m", "int"), ("n", "int"), ("obstacles", "int[][]")], ret="int", cmp="exact",
    desc="<p>An <code>m x n</code> grid has a few blocked cells, given as a list <code>obstacles</code> of distinct pairs <code>[row, col]</code> (0-indexed, in any order). A traveller goes from the top-left cell to the bottom-right cell, moving only one step <strong>right</strong> or one step <strong>down</strong> at a time and never entering a blocked cell.</p><p>Return the number of routes modulo <code>1,000,000,007</code>. The grid has up to 2.5 &middot; 10<sup>9</sup> cells, so it cannot be filled; only the obstacles may be processed one by one. If the start or the destination is blocked the answer is <code>0</code>.</p><pre>m = 3, n = 3, obstacles = [[1,1]]          ->  2\nm = 3, n = 3, obstacles = [[0,1],[1,0]]    ->  0\nm = 2, n = 2, obstacles = []               ->  2</pre>",
    constraints=["1 &le; m, n &le; 50,000", "0 &le; obstacles.length &le; 500", "obstacles[i] = [row, col] with 0 &le; row &lt; m and 0 &le; col &lt; n; all pairs are distinct"],
    hints=["Without obstacles the answer is a single binomial coefficient. The difficulty is subtracting the routes that touch an obstacle without double counting.",
           "Sort the obstacles by row, then column. For obstacle i, count the routes from the start that reach it <em>without touching any earlier obstacle</em>: all routes to it, minus those that first hit an earlier obstacle j.",
           "<code>bad[i] = W(start, i) - sum over j before i with col(j) &le; col(i) of bad[j] &middot; W(j, i)</code>. Treat the destination as one more obstacle placed last; <code>bad</code> of it is the answer. Use factorial tables for W."],
    editorial=["Let <code>W(a, b)</code> be the number of unrestricted right/down routes from cell a to cell b, a binomial coefficient (0 if b is not weakly below and to the right of a). Sort the obstacles by (row, column) and append the destination as a final pseudo-obstacle. Define <code>f[i]</code> as the number of routes from the start to obstacle i that touch no other obstacle before reaching it.",
               "Every route from the start to i either touches no earlier obstacle, or has a unique <em>first</em> obstacle j on it. Counting by first obstacle gives <code>W(start, i) = f[i] + sum over j &lt; i of f[j] &middot; W(j, i)</code>, so <code>f[i] = W(start, i) - sum f[j] &middot; W(j, i)</code>. The sort guarantees that every obstacle that can lie on a route to i comes earlier. The value for the destination is the answer.",
               "Factorials up to m + n modulo the prime cost O(m + n), and the double loop costs O(k<sup>2</sup>) for k obstacles. Memory is O(m + n + k)."],
    time="O(m + n + k<sup>2</sup>)", space="O(m + n + k)",
    solution='''def countRoutesFewObstacles(m, n, obstacles):
    MOD = 10 ** 9 + 7
    size = m + n
    fact = [1] * (size + 1)
    for i in range(1, size + 1):
        fact[i] = fact[i - 1] * i % MOD
    inv = [1] * (size + 1)
    inv[size] = pow(fact[size], MOD - 2, MOD)
    for i in range(size, 0, -1):
        inv[i - 1] = inv[i] * i % MOD

    def ways(dr, dc):
        if dr < 0 or dc < 0:
            return 0
        return fact[dr + dc] * inv[dr] % MOD * inv[dc] % MOD

    pts = sorted(tuple(o) for o in obstacles)
    if (0, 0) in pts or (m - 1, n - 1) in pts:
        return 0
    pts.append((m - 1, n - 1))
    f = []
    for i, (r, c) in enumerate(pts):
        v = ways(r, c)
        for j in range(i):
            rj, cj = pts[j]
            if cj <= c:
                v -= f[j] * ways(r - rj, c - cj)
        f.append(v % MOD)
    return f[-1]
''',
    tests=[[3, 3, [[1, 1]]], [3, 3, [[0, 1], [1, 0]]], [2, 2, []], [1, 1, []], [1, 1, [[0, 0]]], [1, 6, [[0, 3]]],
           [4, 4, [[1, 1], [2, 2]]], [4, 4, [[3, 3]]], [4, 5, [[2, 3], [1, 1], [3, 0], [0, 4]]], [5, 5, [[1, 0], [1, 1], [1, 2], [1, 3]]],
           [50000, 50000, []], [6, 6, [[2, 2], [2, 3], [3, 2], [3, 3], [4, 4]]]],
)
_r = rnd(9206)


def _obst(r, m, n, k):
    s = set()
    while len(s) < k:
        c = (r.randrange(m), r.randrange(n))
        if c not in ((0, 0), (m - 1, n - 1)):
            s.add(c)
    return [list(c) for c in r.sample(sorted(s), len(s))]


p["tests"].append([50000, 50000, _obst(_r, 50000, 50000, 500)])
# obstacles hugging the main diagonal of a big square: many of them lie on common routes
_diag = set()
while len(_diag) < 500:
    t = _r.randrange(1, 49999)
    _diag.add((t, min(49999, max(0, t + _r.randint(-300, 300)))))
_diag.discard((49999, 49999))
p["tests"].append([50000, 50000, [list(c) for c in _r.sample(sorted(_diag), len(_diag))]])
p["tests"].append([50000, 4, _obst(_r, 50000, 4, 300)])
p["tests"].append([37777, 49999, _obst(_r, 37777, 49999, 150)])


def b_few_obst(m, n, obstacles):
    blocked = {tuple(o) for o in obstacles}
    dp = [[0] * n for _ in range(m)]
    for r in range(m):
        for c in range(n):
            if (r, c) in blocked:
                continue
            if r == 0 and c == 0:
                dp[r][c] = 1
            else:
                dp[r][c] = (dp[r - 1][c] if r else 0) + (dp[r][c - 1] if c else 0)
    return dp[m - 1][n - 1] % MOD


def g_few_obst(r):
    m, n = r.randint(1, 8), r.randint(1, 8)
    cells = [(a, b) for a in range(m) for b in range(n)]
    k = r.randint(0, min(len(cells), 10))
    pick = r.sample(cells, k)
    return [m, n, [list(c) for c in pick]]


def v_few_obst(tests):
    for t in tests:
        m, n, ob = t["args"]
        assert 1 <= m <= 50000 and 1 <= n <= 50000 and len(ob) <= 500
        assert len({tuple(o) for o in ob}) == len(ob), "duplicate obstacle"
        assert all(len(o) == 2 and 0 <= o[0] < m and 0 <= o[1] < n for o in ob)
        assert 0 <= t["expected"] < MOD


CHECKS["grid-paths-huge-grid-few-obstacles"] = (b_few_obst, g_few_obst, "exact")
VALIDATE["grid-paths-huge-grid-few-obstacles"] = v_few_obst


# ---------------------------------------------------------------- disjoint-path-pairs-in-grid
p = add(
    id="disjoint-path-pairs-in-grid", title="Pairs of Non-Touching Grid Routes", diff="Hard", topic=TOPIC, tier="extra",
    fn="countDisjointRoutePairs", params=[("grid", "int[][]")], ret="int", cmp="exact",
    desc="<p>In a rectangular <code>grid</code> (<code>0</code> = free, <code>1</code> = blocked) a <em>route</em> goes from the top-left cell to the bottom-right cell using steps <strong>right</strong> and <strong>down</strong> through free cells only. Two routes are <em>non-touching</em> if they share no cell other than the start and the destination.</p><p>Count the <strong>unordered pairs</strong> of non-touching routes, modulo <code>1,000,000,007</code>. The start and destination cells are always free, and the grid has at least 2 rows and 2 columns, so two non-touching routes are always different routes.</p><pre>grid = 2x2 all free              ->  1   (one goes right-down, the other down-right)\ngrid = 2x3 all free              ->  1\ngrid = 3x3 all free              ->  3</pre>",
    constraints=["2 &le; grid.length, grid[0].length &le; 40", "grid[i][j] is 0 or 1", "grid[0][0] = 0 and the bottom-right cell is 0"],
    hints=["Enumerating pairs of routes is hopeless, but two routes can be advanced <em>together</em>: after t steps both are on the anti-diagonal r + c = t.",
           "Two right/down routes that never share a cell cannot cross, so one of them stays strictly above the other on every diagonal. Fix that labelling: it turns unordered pairs into ordered pairs (upper, lower).",
           "State: the diagonal t and the rows <code>(a, b)</code> of the two walkers with a &lt; b. Each walker either goes right or down, giving 4 transitions, and both new cells must be free and keep a' &lt; b'. Count the states that reach the two cells next to the destination."],
    editorial=["Move both routes simultaneously, one step per round. After t steps each route stands on the diagonal r + c = t, so a state is the diagonal together with the two rows (a, b); the columns follow as t - a and t - b. If the routes never share an interior cell they can never swap sides, because a step changes a row by at most one and equal rows on the same diagonal mean the same cell. So for exactly one labelling the 'upper' route (smaller row) stays strictly above the 'lower' one on every interior diagonal; counting only this labelling counts every unordered pair once.",
               "At diagonal 1 the upper route must be at (0, 1) and the lower one at (1, 0). A transition adds 0 or 1 to each row, requires both target cells to lie inside the grid and be free, and requires a' &lt; b'. The routes may finally meet at the destination only: on the last interior diagonal the upper walker must be at (m-2, n-1) and the lower at (m-1, n-2). The answer is the number of ways to reach exactly that state.",
               "There are m + n diagonals and at most min(m, n)<sup>2</sup> states on each, with 4 transitions per state, so the cost is O((m + n) &middot; min(m, n)<sup>2</sup>) time and O(min(m, n)<sup>2</sup>) memory with rolling layers. This is the same non-intersecting-paths idea that the Lindstr&ouml;m&ndash;Gessel&ndash;Viennot lemma generalises."],
    time="O((m + n) &middot; min(m, n)<sup>2</sup>)", space="O(min(m, n)<sup>2</sup>)",
    solution='''def countDisjointRoutePairs(grid):
    MOD = 10 ** 9 + 7
    m, n = len(grid), len(grid[0])
    D = m + n - 2
    if D - 1 < 1:
        return 0
    free = lambda r, c: 0 <= r < m and 0 <= c < n and grid[r][c] == 0
    cur = {}
    if free(0, 1) and free(1, 0):
        cur[(0, 1)] = 1
    for t in range(1, D - 1):
        nxt = {}
        for (a, b), v in cur.items():
            for da in (0, 1):
                a2 = a + da
                if not free(a2, t + 1 - a2):
                    continue
                for db in (0, 1):
                    b2 = b + db
                    if a2 < b2 and free(b2, t + 1 - b2):
                        key = (a2, b2)
                        nxt[key] = (nxt.get(key, 0) + v) % MOD
        cur = nxt
    return cur.get((m - 2, m - 1), 0) % MOD
''',
    tests=[[[[0, 0], [0, 0]]], [[[0, 0, 0], [0, 0, 0]]], [[[0, 0, 0], [0, 0, 0], [0, 0, 0]]], [[[0, 1], [0, 0]]],
           [[[0, 0, 0], [0, 1, 0], [0, 0, 0]]], [[[0, 0], [0, 0], [0, 0]]],
           [[[0, 0], [0, 0], [0, 0], [0, 0]]], [[[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]],
           [[[0, 0, 0, 0], [0, 1, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]], [[[0, 0, 1, 0], [0, 0, 0, 0], [0, 1, 0, 0], [0, 0, 0, 0]]],
           [[[0, 1, 0], [0, 0, 0], [0, 1, 0]]], [[[0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0]]]],
)
_r = rnd(9207)
p["tests"].append([[[0] * 40 for _ in range(40)]])
p["tests"].append([_free_ends(_bin_grid(_r, 40, 40, 0.04))])
p["tests"].append([_free_ends(_bin_grid(_r, 40, 40, 0.1))])
p["tests"].append([[[0] * 40 for _ in range(2)]])
p["tests"].append([[[0] * 3 for _ in range(40)]])


def b_disjoint(grid):
    m, n = len(grid), len(grid[0])
    routes = []

    def go(r, c, cells):
        if r >= m or c >= n or grid[r][c] == 1:
            return
        cells = cells + [(r, c)]
        if r == m - 1 and c == n - 1:
            routes.append(frozenset(cells[1:-1]))
            return
        go(r + 1, c, cells)
        go(r, c + 1, cells)
    go(0, 0, [])
    cnt = 0
    for i in range(len(routes)):
        for j in range(i + 1, len(routes)):
            if not (routes[i] & routes[j]):
                cnt += 1
    return cnt % MOD


def v_disjoint(tests):
    for t in tests:
        g = t["args"][0]
        assert _is_rect(g) and 2 <= len(g) <= 40 and 2 <= len(g[0]) <= 40 and _is_bin(g)
        assert g[0][0] == 0 and g[-1][-1] == 0
        assert 0 <= t["expected"] < MOD


CHECKS["disjoint-path-pairs-in-grid"] = (b_disjoint, lambda r: [_free_ends(_bin_grid(r, r.randint(2, 5), r.randint(2, 5), r.choice([0.0, 0.1, 0.25])))], "exact")
VALIDATE["disjoint-path-pairs-in-grid"] = v_disjoint


# ---------------------------------------------------------------- knight-walks-enormous-length
p = add(
    id="knight-walks-enormous-length", title="Knight Walks of Enormous Length", diff="Hard", topic=TOPIC, tier="extra",
    fn="countLongKnightWalks", params=[("m", "int"), ("n", "int"), ("k", "int")], ret="int", cmp="exact",
    desc="<p>A chess knight may start on <strong>any</strong> cell of an empty <code>m x n</code> board. One move changes the position by <code>(&plusmn;1, &plusmn;2)</code> or <code>(&plusmn;2, &plusmn;1)</code> and must stay on the board. The knight may visit cells repeatedly.</p><p>Count the walks of exactly <code>k</code> moves, where a walk is the list of visited cells (including the starting cell), and return the count modulo <code>1,000,000,007</code>. A walk of 0 moves is just a starting cell.</p><pre>m = 3, n = 4, k = 1  ->  28\nm = 3, n = 3, k = 2  ->  32   (the centre cell has no moves)\nm = 4, n = 4, k = 3  ->  464\nm = 2, n = 4, k = 5  ->  8     (every cell has exactly one move)</pre>",
    constraints=["1 &le; m, n and m &middot; n &le; 16", "0 &le; k &le; 10<sup>9</sup>"],
    hints=["Layer-by-layer DP over the moves costs O(k &middot; cells), which is far too slow for k up to a billion. Look at the structure of one layer step.",
           "One DP step is the same linear map every time: <code>new = A &middot; old</code>, where A is the adjacency matrix of the knight graph (at most 16 &times; 16).",
           "Raise A to the k-th power by repeated squaring, apply it to the all-ones vector (one walk of length 0 from every cell), and add up the entries. Keep every product modulo 1,000,000,007."],
    editorial=["Number the cells 0..s-1 (s = m &middot; n &le; 16) and let A[i][j] = 1 when a knight can jump from cell i to cell j. If <code>v[t][i]</code> is the number of walks of t moves that start anywhere and end at cell i, then <code>v[t+1] = A<sup>T</sup> v[t]</code>; since A is symmetric the transpose does not matter. Starting from <code>v[0] = (1, ..., 1)</code>, the answer is the sum of the entries of <code>A<sup>k</sup> v[0]</code>.",
               "Compute the power with binary exponentiation: keep P = A<sup>2<sup>i</sup></sup> by repeated squaring, and whenever bit i of k is set replace the vector v by P v. Powers of the same matrix commute, so the order does not matter, and only squarings cost s<sup>3</sup>. In total that is about 30 matrix squarings of size at most 16, i.e. roughly 30 &middot; 4096 multiplications, plus 30 cheap matrix-vector products. Everything is taken modulo 1,000,000,007 so that numbers stay small.",
               "Edge cases: k = 0 gives exactly m &middot; n walks, and boards on which the knight can never move (such as 1 &times; n or 2 &times; 2) give 0 for every k &ge; 1."],
    time="O(s<sup>3</sup> log k)", space="O(s<sup>2</sup>)",
    solution='''def countLongKnightWalks(m, n, k):
    MOD = 10 ** 9 + 7
    s = m * n
    A = [[0] * s for _ in range(s)]
    for r in range(m):
        for c in range(n):
            for dr, dc in ((1, 2), (2, 1), (-1, 2), (-2, 1), (1, -2), (2, -1), (-1, -2), (-2, -1)):
                a, b = r + dr, c + dc
                if 0 <= a < m and 0 <= b < n:
                    A[r * n + c][a * n + b] = 1
    v = [1] * s
    P = A
    while k:
        if k & 1:
            v = [sum(x * y for x, y in zip(row, v)) % MOD for row in P]
        k >>= 1
        if k:
            cols = list(zip(*P))
            P = [[sum(x * y for x, y in zip(row, col)) % MOD for col in cols] for row in P]
    return sum(v) % MOD
''',
    tests=[[3, 4, 1], [3, 3, 2], [4, 4, 3], [2, 4, 5], [1, 1, 0], [1, 16, 3], [2, 2, 1], [3, 3, 0], [4, 4, 0], [3, 4, 0],
           [3, 3, 1], [3, 4, 2], [4, 4, 10], [2, 8, 7]],
)
p["tests"].append([4, 4, 10 ** 9])
p["tests"].append([3, 5, 999999937])
p["tests"].append([4, 3, 987654321])
p["tests"].append([2, 8, 123456789])


def b_longknight(m, n, k):
    cells = [(r, c) for r in range(m) for c in range(n)]
    cnt = {x: 1 for x in cells}
    for _ in range(k):
        new = {}
        for (r, c) in cells:
            tot = 0
            for dr, dc in ((1, 2), (2, 1), (-1, 2), (-2, 1), (1, -2), (2, -1), (-1, -2), (-2, -1)):
                tot += cnt.get((r + dr, c + dc), 0)
            new[(r, c)] = tot
        cnt = new
    return sum(cnt.values()) % MOD


def g_longknight(r):
    while True:
        m, n = r.randint(1, 5), r.randint(1, 5)
        if m * n <= 16:
            return [m, n, r.randint(0, 25)]


def v_longknight(tests):
    for t in tests:
        m, n, k = t["args"]
        assert m >= 1 and n >= 1 and m * n <= 16 and 0 <= k <= 10 ** 9
        assert 0 <= t["expected"] < MOD


CHECKS["knight-walks-enormous-length"] = (b_longknight, g_longknight, "exact")
VALIDATE["knight-walks-enormous-length"] = v_longknight
