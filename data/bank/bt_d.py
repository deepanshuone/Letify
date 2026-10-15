"""Problems: backtracking, constraint satisfaction (N-Queens variants, Sudoku-like grids, magic squares, colorings).
See data/lib.py for the registry."""
import itertools
from itertools import permutations as _perms, product as _product

from lib import add, rnd, CHECKS, VALIDATE, gen_arr  # noqa: F401

TOPIC = "Backtracking"


# ---------------------------------------------------------------- shared helpers (tests, brute forces)
def _queens_ok(cols):
    """True if the queens (row i, column cols[i]) do not attack each other."""
    return all(abs(cols[i] - cols[j]) != j - i for i in range(len(cols)) for j in range(i + 1, len(cols)))


def _rand_graph(r, n, p):
    return [[u, v] for u in range(n) for v in range(u + 1, n) if r.random() < p]


def _check_graph(n, edges):
    seen = set()
    for u, v in edges:
        assert 0 <= u < n and 0 <= v < n and u != v, "bad edge"
        key = (min(u, v), max(u, v))
        assert key not in seen, "duplicate edge"
        seen.add(key)


_MAGIC8 = []


def _magic8():
    """All eight 3 x 3 magic squares of 1..9 as flat tuples, found by trying every permutation."""
    if not _MAGIC8:
        for p in _perms(range(1, 10)):
            if (p[0] + p[1] + p[2] == 15 and p[3] + p[4] + p[5] == 15 and p[6] + p[7] + p[8] == 15
                    and p[0] + p[3] + p[6] == 15 and p[1] + p[4] + p[7] == 15 and p[2] + p[5] + p[8] == 15
                    and p[0] + p[4] + p[8] == 15 and p[2] + p[4] + p[6] == 15):
                _MAGIC8.append(p)
        assert len(_MAGIC8) == 8
    return _MAGIC8


# ================================================================== EASY

# ---------------------------------------------------------------- all queens safe
p = add(
    id="all-queens-safe", title="Are All Queens Safe?", diff="Easy", topic=TOPIC,
    fn="allQueensSafe", params=[("queens", "int[][]")], ret="bool", cmp="exact",
    desc="<p>A queen attacks every square in her row, in her column and on both of her diagonals. You are given the positions of some queens on a very large chessboard as <code>queens</code>, where <code>queens[i] = [row, col]</code>. All positions are different.</p><p>Return <code>true</code> if no two queens attack each other, that is, if no two queens share a row, a column or a diagonal. Queens standing in between do not matter: if two queens lie on a common line, the board is unsafe.</p><pre>queens = [[0,1],[1,3],[2,0],[3,2]]  &rarr;  true\nqueens = [[0,0],[2,1],[1,2]]        &rarr;  false   ((2,1) and (1,2) share a diagonal)</pre>",
    constraints=["0 &le; queens.length &le; 5,000", "0 &le; row, col &le; 100,000", "All positions are distinct"],
    hints=["Two queens clash when they agree on a row, on a column, or on a diagonal. Comparing all pairs works but costs O(m<sup>2</sup>). Can you detect a clash while scanning once?",
           "Along one diagonal the value <code>row - col</code> never changes. Along the other diagonal the value <code>row + col</code> never changes.",
           "Keep four sets: used rows, used columns, used values of <code>row - col</code> and used values of <code>row + col</code>. If a new queen hits any of them, return false."],
    editorial=["Every line a queen attacks along is described by one number: the row index, the column index, <code>row - col</code> for the diagonals that go down-right, and <code>row + col</code> for the diagonals that go down-left. Two queens attack each other exactly when they share one of these four numbers.",
               "Scan the queens once and keep four hash sets. If a queen's row, column, <code>row - col</code> or <code>row + col</code> is already in its set, the board is unsafe; otherwise insert the four values. This is O(m) time and space, and it is the same bookkeeping that makes N-Queens backtracking fast: a diagonal is just a number you can mark as used."],
    time="O(m)", space="O(m)",
    solution='''def allQueensSafe(queens):
    rows, cols, down, up = set(), set(), set(), set()
    for r, c in queens:
        if r in rows or c in cols or (r - c) in down or (r + c) in up:
            return False
        rows.add(r)
        cols.add(c)
        down.add(r - c)
        up.add(r + c)
    return True
''',
    tests=[[[]], [[[0, 0]]], [[[0, 1], [1, 3], [2, 0], [3, 2]]], [[[0, 0], [2, 1], [1, 2]]], [[[3, 2], [7, 2]]], [[[4, 0], [4, 9]]],
           [[[0, 0], [3, 3]]], [[[0, 5], [1, 4]]], [[[0, 0], [1, 2], [2, 4], [3, 1]]],
           [[[100000, 0], [0, 100000]]], [[[5, 5], [6, 7], [8, 6], [9, 9]]]],
)


def _nq_classic(n):  # a valid arrangement for n % 6 not in (2, 3): evens, then odds (1-based)
    return [v - 1 for v in list(range(2, n + 1, 2)) + list(range(1, n + 1, 2))]


_r = rnd(401)
_cols = _nq_classic(2005)
_q = [[i, c] for i, c in enumerate(_cols)]
_r.shuffle(_q)
p["tests"].append([_q])
_q2 = [list(x) for x in _q]
_k = _r.randrange(len(_q2))
_q2[_k][1] = _q2[_k][1] + 1 if _q2[_k][1] + 1 < 2005 else _q2[_k][1] - 1  # move one queen sideways -> clash
p["tests"].append([_q2])
_cols = _nq_classic(997)
_q = [[100 * i, 100 * c] for i, c in enumerate(_cols)]
_r.shuffle(_q)
p["tests"].append([_q])
_q = set()
while len(_q) < 1200:
    _q.add((_r.randint(0, 100000), _r.randint(0, 100000)))
p["tests"].append([[list(x) for x in sorted(_q)]])


def b_safe(queens):
    for i in range(len(queens)):
        for j in range(i + 1, len(queens)):
            (r1, c1), (r2, c2) = queens[i], queens[j]
            if r1 == r2 or c1 == c2 or abs(r1 - r2) == abs(c1 - c2):
                return False
    return True


def g_safe(r):
    n = r.randint(0, 6)
    size = r.randint(max(1, n), 7)
    cells = r.sample([(i, j) for i in range(size) for j in range(size)], n)
    if r.random() < 0.4 and n > 0:  # often a board with no shared row or column
        cols = r.sample(range(size), min(n, size))
        cells = [(i, c) for i, c in enumerate(cols)]
    return [[a, b] for a, b in cells]


def v_safe(tests):
    for t in tests:
        q = t["args"][0]
        assert len(q) <= 5000 and len({tuple(x) for x in q}) == len(q), "positions"
        assert all(0 <= a <= 100000 and 0 <= b <= 100000 for a, b in q)
    assert any(t["expected"] for t in tests) and not all(t["expected"] for t in tests)


CHECKS["all-queens-safe"] = (b_safe, lambda r: [g_safe(r)], "exact")
VALIDATE["all-queens-safe"] = v_safe


# ---------------------------------------------------------------- magic blocks in a grid
p = add(
    id="count-magic-blocks", title="Count Magic Blocks in a Grid", diff="Easy", topic=TOPIC,
    fn="countMagicBlocks", params=[("grid", "int[][]")], ret="int", cmp="exact",
    desc="<p>A <em>magic block</em> is a 3 &times; 3 square of neighbouring cells that contains each of the numbers 1 to 9 exactly once, and in which all three rows, all three columns and both diagonals have the same sum.</p><p>Given a rectangular <code>grid</code> of small non-negative integers, return how many 3 &times; 3 blocks of the grid are magic. Blocks may overlap.</p><pre>grid = [[4,3,8,4],\n        [9,5,1,9],\n        [2,7,6,2]]  &rarr;  1</pre><p>The left block is magic (all lines add up to 15). The right block is not: its main diagonal is 3 + 1 + 2.</p>",
    constraints=["1 &le; rows, cols &le; 60", "0 &le; grid[i][j] &le; 15"],
    hints=["There are only (rows - 2) &times; (cols - 2) blocks. Check each one in constant time.",
           "If the nine cells are 1..9, they add up to 45, so every line of a magic block must add up to 15.",
           "The four lines through the centre (middle row, middle column, both diagonals) cover every cell once, except the centre which is counted four times. So 4 &middot; 15 = 45 + 3 &middot; centre, hence the centre must be 5. Use that as a cheap filter, then test the digits and the eight line sums."],
    editorial=["Slide a 3 &times; 3 window over the grid and test it. A block qualifies when its nine values are exactly 1..9 (sorting them and comparing is enough) and the three rows, three columns and two diagonals share one sum. With nine distinct digits from 1..9 the total is 45, which forces that common sum to be 15.",
               "A small observation speeds up the scan: adding the middle row, middle column and both diagonals counts every cell once and the centre four times, so 60 = 45 + 3 &middot; centre and the centre has to be 5. Most windows are rejected by that single comparison. The work is O(rows &middot; cols) with a constant of nine cells per window."],
    time="O(rows * cols)", space="O(1)",
    solution='''def countMagicBlocks(grid):
    rows, cols = len(grid), len(grid[0])
    nine = list(range(1, 10))
    count = 0
    for i in range(rows - 2):
        for j in range(cols - 2):
            if grid[i + 1][j + 1] != 5:
                continue
            a, b, c = grid[i][j:j + 3]
            d, e, f = grid[i + 1][j:j + 3]
            g, h, k = grid[i + 2][j:j + 3]
            if sorted((a, b, c, d, e, f, g, h, k)) != nine:
                continue
            if a + b + c == d + e + f == g + h + k == a + d + g == b + e + h == c + f + k == a + e + k == c + e + g:
                count += 1
    return count
''',
    tests=[[[[4, 3, 8, 4], [9, 5, 1, 9], [2, 7, 6, 2]]], [[[2, 7, 6], [9, 5, 1], [4, 3, 8]]], [[[4, 9, 2], [3, 5, 7], [8, 6, 1]]],
           [[[5]]], [[[4, 9, 2, 3, 5]]],
           [[[1, 2, 3], [4, 5, 6], [7, 8, 9]]],
           [[[0, 0, 0], [0, 5, 0], [0, 0, 0]]], [[[8, 1, 6, 8], [3, 5, 7, 3], [4, 9, 2, 4], [8, 1, 6, 8]]]],
)
# all eight magic squares side by side, then every 3x3 window of that strip is examined
_m8 = [list(m) for m in _magic8()]
_strip = [[m[3 * a + b] for m in _m8 for b in range(3)] for a in range(3)]
p["tests"].append([_strip])
_r = rnd(402)
for _R, _C, _K in [(60, 60, 40), (47, 60, 25), (60, 31, 30)]:
    _g = [[_r.randint(0, 15) for _ in range(_C)] for _ in range(_R)]
    _slots = [(a, b) for a in range(0, _R - 2, 3) for b in range(0, _C - 2, 3)]
    for a, b in _r.sample(_slots, min(_K, len(_slots))):
        m = _r.choice(_m8)
        for x in range(3):
            for y in range(3):
                _g[a + x][b + y] = m[3 * x + y]
    p["tests"].append([_g])


def b_magic(grid):
    squares = set(_magic8())
    R, C = len(grid), len(grid[0])
    return sum(1 for i in range(R - 2) for j in range(C - 2)
               if tuple(grid[i + x][j + y] for x in range(3) for y in range(3)) in squares)


def g_magic(r):
    R, C = r.randint(1, 6), r.randint(1, 6)
    g = [[r.choice([r.randint(0, 15), r.randint(1, 9), r.randint(4, 6)]) for _ in range(C)] for _ in range(R)]
    if R >= 3 and C >= 3 and r.random() < 0.6:
        m = r.choice(_magic8())
        a, b = r.randint(0, R - 3), r.randint(0, C - 3)
        for x in range(3):
            for y in range(3):
                g[a + x][b + y] = m[3 * x + y]
    return g


def v_magic(tests):
    for t in tests:
        g = t["args"][0]
        assert 1 <= len(g) <= 60 and all(len(row) == len(g[0]) for row in g) and 1 <= len(g[0]) <= 60
        assert all(0 <= v <= 15 for row in g for v in row)
    assert sum(1 for t in tests if t["expected"] > 0) >= 4


CHECKS["count-magic-blocks"] = (b_magic, lambda r: [g_magic(r)], "exact")
VALIDATE["count-magic-blocks"] = v_magic


# ================================================================== MEDIUM

# ---------------------------------------------------------------- lexicographically first N-Queens
add(
    id="first-n-queens-placement", title="Lexicographically First N-Queens", diff="Medium", topic=TOPIC,
    fn="firstQueensPlacement", params=[("n", "int")], ret="int[]", cmp="exact",
    desc="<p>Place <code>n</code> queens on an <code>n &times; n</code> board so that no two queens attack each other (no shared row, column or diagonal). A placement is written as an array <code>cols</code> of length <code>n</code>: <code>cols[r]</code> is the 0-based column of the queen in row <code>r</code>.</p><p>Many placements can exist. Return the lexicographically smallest one, comparing <code>cols[0]</code> first, then <code>cols[1]</code>, and so on. If no placement exists, return an empty array.</p><pre>n = 4  &rarr;  [1, 3, 0, 2]\nn = 6  &rarr;  [1, 3, 5, 0, 2, 4]\nn = 3  &rarr;  []</pre>",
    constraints=["1 &le; n &le; 18"],
    hints=["Every row holds exactly one queen, so decide row by row which column to use.",
           "A queen at <code>(r, c)</code> blocks column <code>c</code>, diagonal <code>r - c</code> and anti-diagonal <code>r + c</code>. Remember these three sets (or three bitmasks) while you recurse, and undo them when you backtrack.",
           "Try the columns of each row from left to right and stop the whole search at the first complete placement. The first one found by this order is automatically the lexicographically smallest. If the search finishes without success, return <code>[]</code>."],
    editorial=["Depth-first search over rows. In row <code>r</code> try every column <code>c</code> that is not under attack, place the queen, and recurse into row <code>r + 1</code>; if the recursion fails, remove the queen and try the next column. Attacks are tracked in O(1) with a column set and two diagonal sets, or with three bitmasks where the diagonal masks are shifted by one position at every row.",
               "Because rows are filled in order and the columns of each row are tried in increasing order, the very first complete placement found is the lexicographically smallest one, so the search can stop immediately. For n = 2 and n = 3 the search exhausts all options and returns the empty array. The worst case is exponential, but the pruning makes the first solution appear after only a modest number of steps for the sizes allowed here."],
    time="O(n!) worst case, much less in practice", space="O(n)",
    solution='''def firstQueensPlacement(n):
    full = (1 << n) - 1
    cols = [0] * n

    def go(r, used, down, up):
        if r == n:
            return True
        free = full & ~(used | down | up)
        while free:
            bit = free & -free      # lowest set bit = smallest free column
            free ^= bit
            cols[r] = bit.bit_length() - 1
            if go(r + 1, used | bit, ((down | bit) << 1) & full, (up | bit) >> 1):
                return True
        return False

    return cols if go(0, 0, 0, 0) else []
''',
    tests=[[4], [6], [3], [1], [2], [5], [7], [8], [9], [10], [12], [14], [16], [18]],
)


def b_first_queens(n):
    if n <= 8:
        for perm in _perms(range(n)):  # permutations come in lexicographic order
            if _queens_ok(perm):
                return list(perm)
        return []
    placed = []  # larger boards: plain row-by-row search with pairwise checks

    def go():
        r = len(placed)
        if r == n:
            return True
        for c in range(n):
            if all(c != c2 and abs(c - c2) != r - r2 for r2, c2 in enumerate(placed)):
                placed.append(c)
                if go():
                    return True
                placed.pop()
        return False

    return list(placed) if go() else []


def v_first_queens(tests):
    for t in tests:
        n, e = t["args"][0], t["expected"]
        assert 1 <= n <= 18
        if e:
            assert len(e) == n and sorted(e) == list(range(n)) and _queens_ok(e)
        else:
            assert n in (2, 3)
    assert {t["args"][0] for t in tests} >= {2, 3}


CHECKS["first-n-queens-placement"] = (b_first_queens, lambda r: [r.randint(1, 8)], "exact")
VALIDATE["first-n-queens-placement"] = v_first_queens


# ---------------------------------------------------------------- N-Queens with blocked squares
p = add(
    id="n-queens-with-blocked-squares", title="N-Queens With Blocked Squares", diff="Medium", topic=TOPIC,
    fn="countQueensBlocked", params=[("n", "int"), ("blocked", "int[][]")], ret="int", cmp="exact",
    desc="<p>Some squares of an <code>n &times; n</code> board are blocked: <code>blocked[i] = [row, col]</code> (0-based). A queen may <strong>not</strong> be placed on a blocked square. Blocked squares do not stop queens from attacking through them.</p><p>Count the ways to place <code>n</code> queens on the board, none of them on a blocked square, so that no two queens share a row, a column or a diagonal.</p><pre>n = 4, blocked = []              &rarr;  2\nn = 4, blocked = [[0,1]]         &rarr;  1\nn = 4, blocked = [[0,1],[0,2]]   &rarr;  0</pre>",
    constraints=["1 &le; n &le; 10", "0 &le; blocked.length &le; n &middot; n", "All blocked squares are distinct and inside the board"],
    hints=["Exactly one queen goes into each row, so search row by row and count the complete placements.",
           "Track which columns and which two kinds of diagonals are already attacked. For row <code>r</code> a column <code>c</code> is usable only if it is not attacked and <code>(r, c)</code> is not blocked.",
           "Store the blocked cells of every row as a bitmask. The set of usable columns in a row is then <code>full &amp; ~(cols | diag1 | diag2 | blockedMask[r])</code>, and you can iterate its set bits."],
    editorial=["This is the classic N-Queens count with one extra restriction. Search row by row. In row <code>r</code> the candidate columns are those that are not in a used column, not on an attacked diagonal and not blocked in this row. For every candidate place the queen, recurse into the next row and add the returned counts.",
               "Bitmasks make the candidate computation a few machine operations: keep a mask of used columns, a mask of attacked columns on the down-left diagonals (shift left by one when moving to the next row) and one for the down-right diagonals (shift right). The blocked cells of each row form one more mask that is OR-ed in. Blocking only removes candidates; it never changes how attacks propagate. For n = 10 the unblocked board has 724 solutions and a few ten thousand search nodes, so the search is instant."],
    time="O(n!) worst case, pruned heavily", space="O(n)",
    solution='''def countQueensBlocked(n, blocked):
    full = (1 << n) - 1
    forbidden = [0] * n
    for r, c in blocked:
        forbidden[r] |= 1 << c

    def go(r, used, down, up):
        if r == n:
            return 1
        free = full & ~(used | down | up | forbidden[r])
        total = 0
        while free:
            bit = free & -free
            free ^= bit
            total += go(r + 1, used | bit, ((down | bit) << 1) & full, (up | bit) >> 1)
        return total

    return go(0, 0, 0, 0)
''',
    tests=[[4, []], [4, [[0, 1]]], [4, [[0, 1], [0, 2]]], [1, []], [1, [[0, 0]]], [2, []], [5, [[2, 2]]], [6, []],
           [8, [[0, 0], [7, 7], [3, 4]]], [10, []], [9, [[r, (3 * r) % 9] for r in range(9)]],
           [10, [[1, 3], [2, 6], [4, 4], [5, 0], [6, 9], [7, 2], [8, 5], [9, 7]]], [7, [[3, c] for c in range(7)]]],
)


def b_blocked(n, blocked):
    bl = {tuple(x) for x in blocked}
    if n <= 7:
        return sum(1 for cols in _perms(range(n)) if all((i, cols[i]) not in bl for i in range(n)) and _queens_ok(cols))
    placed = []

    def go():
        r = len(placed)
        if r == n:
            return 1
        total = 0
        for c in range(n):
            if (r, c) not in bl and all(c != c2 and abs(c - c2) != r - r2 for r2, c2 in enumerate(placed)):
                placed.append(c)
                total += go()
                placed.pop()
        return total

    return go()


def g_blocked(r):
    n = r.randint(1, 7)
    cells = [[i, j] for i in range(n) for j in range(n)]
    k = r.randint(0, min(len(cells), 2 * n))
    return [n, sorted(r.sample(cells, k))]


def v_blocked(tests):
    for t in tests:
        n, bl = t["args"]
        assert 1 <= n <= 10 and len(bl) <= n * n
        assert len({tuple(x) for x in bl}) == len(bl) and all(0 <= a < n and 0 <= b < n for a, b in bl)
    assert any(t["expected"] == 0 for t in tests) and any(t["expected"] > 0 for t in tests)


CHECKS["n-queens-with-blocked-squares"] = (b_blocked, g_blocked, "exact")
VALIDATE["n-queens-with-blocked-squares"] = v_blocked


# ---------------------------------------------------------------- distinct graph colorings
p = add(
    id="count-distinct-graph-colorings", title="Count Distinct Graph Colorings", diff="Medium", topic=TOPIC,
    fn="countColorings", params=[("n", "int"), ("edges", "int[][]"), ("k", "int")], ret="int", cmp="exact",
    desc="<p>An undirected graph has vertices <code>0..n-1</code> and the edge list <code>edges</code>, where each <code>[u, v]</code> joins two different vertices. A <em>coloring</em> gives every vertex a color so that the two ends of every edge get different colors.</p><p>Colors are interchangeable: two colorings are the same if one turns into the other by renaming colors. Equivalently, you are counting the ways to split the vertices into at most <code>k</code> non-empty groups, so that no edge has both ends in the same group (groups are unordered). Return that number.</p><pre>n = 3, edges = [[0,1],[1,2]], k = 3  &rarr;  2    ({0,2}{1} and {0}{1}{2})\nn = 3, edges = [],            k = 2  &rarr;  4    (all together, or one vertex alone, three ways)\nn = 3, edges = [[0,1],[1,2],[0,2]], k = 2  &rarr;  0</pre>",
    constraints=["1 &le; n &le; 10", "1 &le; k &le; 10", "0 &le; edges.length &le; n(n - 1) / 2; no self-loops and no repeated edges"],
    hints=["Give every vertex a color one after another. Counting all k<sup>n</sup> assignments and then dividing by something is messy, so avoid generating renamed copies in the first place.",
           "To skip renamings, allow vertex <code>v</code> to join one of the groups that already exist, or to open <b>one</b> new group (only if fewer than <code>k</code> groups exist). Never choose between several empty colors.",
           "Keep for every group a bitmask of its members and for every vertex a bitmask of its neighbours. Vertex <code>v</code> may join a group when <code>members[g] &amp; adj[v] == 0</code>. At <code>v == n</code> count one."],
    editorial=["The standard trick for counting colorings up to renaming is to fix a canonical numbering: process vertices in order, and let vertex <code>v</code> either join an existing group or start the next new group. Each unordered split is then produced exactly once, because the groups are numbered by the order of their smallest vertex.",
               "Group membership is stored as bitmasks. Joining group <code>g</code> is allowed when none of the group's members is a neighbour of <code>v</code>; opening a new group is allowed while the group count is below <code>k</code>. When all vertices are placed we have one valid split. Without edges the answer is the sum of Stirling numbers of the second kind up to <code>k</code> (at most Bell(10) = 115,975), which bounds the search."],
    time="O(Bell(n) * n)", space="O(n)",
    solution='''def countColorings(n, edges, k):
    adj = [0] * n
    for u, v in edges:
        adj[u] |= 1 << v
        adj[v] |= 1 << u
    groups = []

    def go(v):
        if v == n:
            return 1
        total = 0
        for g in range(len(groups)):
            if groups[g] & adj[v] == 0:
                groups[g] |= 1 << v
                total += go(v + 1)
                groups[g] ^= 1 << v
        if len(groups) < k:
            groups.append(1 << v)
            total += go(v + 1)
            groups.pop()
        return total

    return go(0)
''',
    tests=[[3, [[0, 1], [1, 2]], 3], [3, [], 2], [3, [[0, 1], [1, 2], [0, 2]], 2], [1, [], 1], [1, [], 5], [2, [[0, 1]], 1],
           [4, [[0, 1], [1, 2], [2, 3], [3, 0]], 2], [5, [[i, (i + 1) % 5] for i in range(5)], 3],
           [6, [[i, j] for i in range(3) for j in range(3, 6)], 2], [6, [], 4], [8, [[0, 1], [2, 3], [4, 5], [6, 7]], 3],
           [10, [], 10], [10, [[i, (i + 1) % 10] for i in range(10)], 4], [9, [[0, 1], [1, 2], [3, 4], [5, 6], [7, 8]], 5]],
)
_r = rnd(403)
p["tests"].append([10, _rand_graph(_r, 10, 0.15), 6])
p["tests"].append([10, _rand_graph(_r, 10, 0.3), 5])
p["tests"].append([10, _rand_graph(_r, 10, 0.5), 7])


def b_colorings(n, edges, k):
    if n > 6:  # restricted growth strings with an adjacency matrix
        mat = [[False] * n for _ in range(n)]
        for u, v in edges:
            mat[u][v] = mat[v][u] = True
        lab = []

        def go():
            v = len(lab)
            if v == n:
                return 1
            total = 0
            for x in range(min(k, (max(lab) + 2) if lab else 1)):
                if all(not (mat[v][u] and lab[u] == x) for u in range(v)):
                    lab.append(x)
                    total += go()
                    lab.pop()
            return total

        return go()
    seen = set()
    for col in _product(range(min(k, n)), repeat=n):
        if all(col[u] != col[v] for u, v in edges):
            relabel, canon = {}, []
            for x in col:
                relabel.setdefault(x, len(relabel))
                canon.append(relabel[x])
            seen.add(tuple(canon))
    return len(seen)


def g_colorings(r):
    n = r.randint(1, 6)
    return [n, _rand_graph(r, n, r.choice([0.0, 0.2, 0.4, 0.7])), r.randint(1, 6)]


def v_colorings(tests):
    for t in tests:
        n, edges, k = t["args"]
        assert 1 <= n <= 10 and 1 <= k <= 10
        _check_graph(n, edges)
    assert any(t["expected"] == 0 for t in tests) and any(t["expected"] > 100 for t in tests)


CHECKS["count-distinct-graph-colorings"] = (b_colorings, g_colorings, "exact")
VALIDATE["count-distinct-graph-colorings"] = v_colorings


# ---------------------------------------------------------------- 6 x 6 mini sudoku completions
def _mini_random_solution(r):
    g = [[0] * 6 for _ in range(6)]

    def ok(i, j, d):
        if any(g[i][c] == d for c in range(6)) or any(g[x][j] == d for x in range(6)):
            return False
        bi, bj = i // 2 * 2, j // 3 * 3
        return all(g[bi + x][bj + y] != d for x in range(2) for y in range(3))

    def go(pos):
        if pos == 36:
            return True
        i, j = divmod(pos, 6)
        ds = list(range(1, 7))
        r.shuffle(ds)
        for d in ds:
            if ok(i, j, d):
                g[i][j] = d
                if go(pos + 1):
                    return True
                g[i][j] = 0
        return False

    assert go(0)
    return g


def _mini_conflict_free(g):
    groups = [[(i, j) for j in range(6)] for i in range(6)] + [[(i, j) for i in range(6)] for j in range(6)]
    groups += [[(bi + x, bj + y) for x in range(2) for y in range(3)] for bi in (0, 2, 4) for bj in (0, 3)]
    for grp in groups:
        vals = [g[i][j] for i, j in grp if g[i][j]]
        if len(vals) != len(set(vals)):
            return False
    return True


p = add(
    id="count-mini-sudoku-completions", title="Count Mini Sudoku Completions", diff="Medium", topic=TOPIC,
    fn="countMiniSudoku", params=[("grid", "int[][]")], ret="int", cmp="exact",
    desc="<p>A mini Sudoku is a 6 &times; 6 grid in which every row, every column and every one of the six 2 &times; 3 boxes (2 rows high, 3 columns wide: rows 0-1, 2-3 or 4-5 combined with columns 0-2 or 3-5) must contain each of the digits 1 to 6 exactly once.</p><p>You get a partly filled <code>grid</code>: <code>0</code> marks an empty cell, <code>1..6</code> a given digit. The given digits never repeat inside a row, column or box. Return the number of different ways to fill all empty cells so that the whole grid becomes a valid mini Sudoku (<code>0</code> if there is none).</p><p>To keep the search small, it is guaranteed that the answer is at most <code>10000</code>. A valid grid that is already full has exactly one completion (itself).</p>",
    constraints=["grid is exactly 6 &times; 6", "0 &le; grid[i][j] &le; 6, where 0 means empty", "The given digits contain no repeated digit in any row, column or box", "The answer is at most 10,000"],
    hints=["Fill the empty cells one by one. A digit is allowed in a cell if it does not yet occur in that row, that column or that box.",
           "Keep a bitmask of used digits for each of the 6 rows, 6 columns and 6 boxes. The candidates of a cell are the digits missing from all three masks. The box of cell <code>(r, c)</code> is <code>(r // 2) * 2 + c // 3</code>.",
           "To prune harder, always continue with the empty cell that has the fewest candidates. If some cell has no candidate at all, stop that branch immediately."],
    editorial=["This is plain constraint-satisfaction backtracking. Preload the masks with the given digits, then recursively pick an empty cell, try each digit that is free in its row, column and box, recurse, and undo the placement. Every leaf of the recursion is one valid completion, so the answer is the number of leaves.",
               "Choosing the most constrained empty cell first (the one with the fewest candidates) keeps the tree small: forced cells are filled at once and dead ends are detected early. A completely empty 6 &times; 6 grid has over 28 million completions, which is why the statement bounds the answer; with at most 10,000 completions the search finishes in a blink. The same machinery solves the full 9 &times; 9 Sudoku."],
    time="O(answer * cells) roughly, heavily pruned", space="O(cells)",
    solution='''def countMiniSudoku(grid):
    rows, cols, boxes = [0] * 6, [0] * 6, [0] * 6
    empty = []
    for r in range(6):
        for c in range(6):
            v = grid[r][c]
            if v:
                bit = 1 << v
                rows[r] |= bit
                cols[c] |= bit
                boxes[(r // 2) * 2 + c // 3] |= bit
            else:
                empty.append((r, c))
    FULL = 0b1111110

    def go(k):
        if k == len(empty):
            return 1
        best, best_mask, best_n = k, 0, 7
        for i in range(k, len(empty)):
            r, c = empty[i]
            m = FULL & ~(rows[r] | cols[c] | boxes[(r // 2) * 2 + c // 3])
            n = bin(m).count("1")
            if n < best_n:
                best, best_mask, best_n = i, m, n
                if n == 0:
                    return 0
        empty[k], empty[best] = empty[best], empty[k]
        r, c = empty[k]
        b = (r // 2) * 2 + c // 3
        total = 0
        m = best_mask
        while m:
            bit = m & -m
            m ^= bit
            rows[r] |= bit
            cols[c] |= bit
            boxes[b] |= bit
            total += go(k + 1)
            rows[r] ^= bit
            cols[c] ^= bit
            boxes[b] ^= bit
        empty[k], empty[best] = empty[best], empty[k]
        return total

    return go(0)
''',
    tests=[],
)
_r = rnd(404)
_sol = _mini_random_solution(_r)
_row_swapped = [list(row) for row in _sol]
p["tests"].append([[list(row) for row in _sol]])
_g = [list(row) for row in _sol]
_g[2][4] = 0
p["tests"].append([_g])
for _dens in (0.35, 0.5, 0.6, 0.7, 0.8):
    _s = _mini_random_solution(_r)
    p["tests"].append([[[0 if _r.random() < _dens else v for v in row] for row in _s]])
# sparse clue sets (some unsolvable, some with many completions)
for _clues in (6, 8, 10, 14):
    for _try in range(200):
        _g = [[0] * 6 for _ in range(6)]
        for i, j in _r.sample([(a, b) for a in range(6) for b in range(6)], _clues):
            _g[i][j] = _r.randint(1, 6)
        if _mini_conflict_free(_g):
            p["tests"].append([_g])
            break
p["tests"].append([[[1, 2, 3, 4, 5, 6], [4, 5, 6, 1, 2, 3], [0] * 6, [0] * 6, [0] * 6, [0] * 6]])
p["tests"].append([[[1, 2, 3, 4, 5, 6], [4, 5, 6, 0, 0, 0], [0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0]]])


def b_mini(grid):
    perms = list(_perms(range(1, 7)))
    cands = [[q for q in perms if all(g == 0 or g == x for g, x in zip(grid[r], q))] for r in range(6)]
    colset = [set() for _ in range(6)]
    boxset = [set() for _ in range(6)]

    def go(r):
        if r == 6:
            return 1
        total = 0
        for q in cands[r]:
            if all(q[c] not in colset[c] and q[c] not in boxset[(r // 2) * 2 + c // 3] for c in range(6)):
                for c in range(6):
                    colset[c].add(q[c])
                    boxset[(r // 2) * 2 + c // 3].add(q[c])
                total += go(r + 1)
                for c in range(6):
                    colset[c].discard(q[c])
                    boxset[(r // 2) * 2 + c // 3].discard(q[c])
        return total

    return go(0)


def g_mini(r):
    if r.random() < 0.6:
        s = _mini_random_solution(r)
        dens = r.choice([0.3, 0.4, 0.5, 0.6])
        return [[0 if r.random() < dens else v for v in row] for row in s]
    while True:
        g = [[0] * 6 for _ in range(6)]
        for i, j in r.sample([(a, b) for a in range(6) for b in range(6)], r.randint(10, 16)):
            g[i][j] = r.randint(1, 6)
        if _mini_conflict_free(g):
            return [g]


CHECKS["count-mini-sudoku-completions"] = (b_mini, lambda r: (lambda x: x if isinstance(x[0][0], list) else [x])(g_mini(r)), "exact")


def v_mini(tests):
    for t in tests:
        g = t["args"][0]
        assert len(g) == 6 and all(len(row) == 6 and all(0 <= v <= 6 for v in row) for row in g)
        assert _mini_conflict_free(g), "conflicting givens"
        assert 0 <= t["expected"] <= 10000
    assert any(t["expected"] > 500 for t in tests) and any(t["expected"] == 0 for t in tests)
    assert any(t["expected"] == 1 for t in tests)


VALIDATE["count-mini-sudoku-completions"] = v_mini


# ---------------------------------------------------------------- distinct-digit grid with line sums
p = add(
    id="digit-grid-with-line-sums", title="Digit Grid From Row and Column Sums", diff="Medium", topic=TOPIC,
    fn="countSumGrids", params=[("rows", "int"), ("cols", "int"), ("rowSums", "int[]"), ("colSums", "int[]")], ret="int", cmp="exact",
    desc="<p>Fill a grid with <code>rows</code> rows and <code>cols</code> columns using digits from 1 to 9, where <strong>no digit may be used more than once</strong> in the whole grid. Row <code>i</code> must add up to <code>rowSums[i]</code> and column <code>j</code> must add up to <code>colSums[j]</code>.</p><p>Return the number of different grids that satisfy all sums (two grids differ if some cell holds different digits).</p><pre>rows = 2, cols = 2, rowSums = [3, 7], colSums = [4, 6]  &rarr;  1   ([[1,2],[3,4]])\nrows = 3, cols = 3, all six sums 15                      &rarr;  72  (magic squares are 8 of these)</pre>",
    constraints=["1 &le; rows, cols and rows &middot; cols &le; 9", "rowSums.length = rows, colSums.length = cols", "0 &le; rowSums[i], colSums[j] &le; 45"],
    hints=["At most 9 cells are filled and each uses a distinct digit, so a search cell by cell is affordable. Write it first, then prune.",
           "Keep the remaining sum of each row and each column. A digit is allowed in a cell only if it is unused and not larger than both the remaining row sum and the remaining column sum.",
           "The last cell of a row has no freedom: the digit must equal the remaining row sum. The same holds for the last cell of a column. Use these forced values to cut branches, and also skip a digit that would leave a remaining sum of 0 while cells are still left in that line."],
    editorial=["Go through the cells in row-major order and keep a bitmask of used digits plus the remaining sum of every row and column. For a cell, try each unused digit that does not exceed its row's and column's remaining sums. After the placement subtract the digit from both sums and recurse.",
               "Two kinds of pruning shrink the tree enormously. In the last column of a row the digit is forced to be exactly the remaining row sum; in the last row it is forced to be the remaining column sum. And a digit that would bring a remaining sum to 0 while more cells of that line are still empty can never work because every digit is at least 1. For a 3 &times; 3 grid only the top-left 2 &times; 2 block is really free (at most 9 &middot; 8 &middot; 7 &middot; 6 choices), the other cells are decided by the sums."],
    time="O(9 * 8 * 7 * 6) for 3 x 3 after pruning", space="O(rows * cols)",
    solution='''def countSumGrids(rows, cols, rowSums, colSums):
    rs = list(rowSums)
    cs = list(colSums)

    def go(pos, used):
        if pos == rows * cols:
            return 1
        r, c = divmod(pos, cols)
        last_col = c == cols - 1
        last_row = r == rows - 1
        total = 0
        for d in range(1, 10):
            if (used >> d) & 1 or d > rs[r] or d > cs[c]:
                continue
            if last_col and d != rs[r]:
                continue
            if last_row and d != cs[c]:
                continue
            if not last_col and rs[r] - d <= 0:
                continue
            if not last_row and cs[c] - d <= 0:
                continue
            rs[r] -= d
            cs[c] -= d
            total += go(pos + 1, used | (1 << d))
            rs[r] += d
            cs[c] += d
        return total

    return go(0, 0)
''',
    tests=[[2, 2, [3, 7], [4, 6]], [3, 3, [15, 15, 15], [15, 15, 15]], [1, 1, [5], [5]], [1, 1, [10], [10]], [1, 3, [6], [1, 2, 3]],
           [1, 3, [6], [1, 2, 4]], [3, 1, [6, 9, 12], [27]], [2, 2, [10, 10], [10, 10]], [2, 3, [15, 15], [9, 10, 11]],
           [3, 3, [6, 15, 24], [12, 15, 18]], [3, 3, [20, 15, 10], [12, 15, 18]], [3, 3, [45, 0, 0], [15, 15, 15]],
           [2, 4, [14, 22], [4, 9, 12, 11]], [4, 2, [14, 12, 9, 7], [26, 16]], [3, 3, [10, 12, 23], [14, 15, 16]],
           [1, 9, [45], [1, 2, 3, 4, 5, 6, 7, 8, 9]], [9, 1, [1, 2, 3, 4, 5, 6, 7, 8, 9], [45]], [3, 2, [3, 7, 11], [11, 10]]],
)


def b_sumgrid(rows, cols, rowSums, colSums):
    count = 0

    def pick(r, left, grid):
        nonlocal count
        if r == rows:
            if all(sum(grid[i][j] for i in range(rows)) == colSums[j] for j in range(cols)):
                count += 1
            return
        for row in _perms(sorted(left), cols):
            if sum(row) == rowSums[r]:
                pick(r + 1, left - set(row), grid + [row])

    pick(0, set(range(1, 10)), [])
    return count


def g_sumgrid(r):
    rows, cols = r.choice([(1, 1), (1, 2), (1, 4), (2, 1), (4, 1), (2, 2), (2, 2), (2, 3), (3, 2), (2, 4), (3, 3), (3, 3), (1, 5)])
    if r.random() < 0.75:
        digits = r.sample(range(1, 10), rows * cols)
        grid = [digits[i * cols:(i + 1) * cols] for i in range(rows)]
        return [rows, cols, [sum(row) for row in grid], [sum(grid[i][j] for i in range(rows)) for j in range(cols)]]
    return [rows, cols, [r.randint(1, 24) for _ in range(rows)], [r.randint(1, 24) for _ in range(cols)]]


def v_sumgrid(tests):
    for t in tests:
        rows, cols, rs, cs = t["args"]
        assert 1 <= rows and 1 <= cols and rows * cols <= 9 and len(rs) == rows and len(cs) == cols
        assert all(0 <= x <= 45 for x in rs + cs)
    assert any(t["expected"] == 0 for t in tests) and any(t["expected"] >= 8 for t in tests)


CHECKS["digit-grid-with-line-sums"] = (b_sumgrid, g_sumgrid, "exact")
VALIDATE["digit-grid-with-line-sums"] = v_sumgrid


# ---------------------------------------------------------------- queens that also dodge knights
p = add(
    id="queens-avoiding-knight-moves", title="Queens That Dodge Knights", diff="Medium", topic=TOPIC,
    fn="countAmazonPlacements", params=[("n", "int")], ret="int", cmp="exact", tier="extra",
    desc="<p>Place <code>n</code> pieces on an <code>n &times; n</code> board. Each piece threatens everything a queen threatens (its row, its column, both diagonals) <strong>and</strong> everything a knight threatens (squares that are 1 row and 2 columns, or 2 rows and 1 column, away). No piece may threaten another.</p><p>Return the number of different placements of the <code>n</code> pieces. Pieces on a threatened line do not shield each other, and all pieces look the same.</p><pre>n = 1   &rarr;  1\nn = 4   &rarr;  0\nn = 10  &rarr;  4</pre>",
    constraints=["1 &le; n &le; 12"],
    hints=["Two pieces may not share a row, so a valid placement has exactly one piece per row (n pieces, n rows). Search row by row.",
           "As in N-Queens, mark columns and both diagonals as taken. The extra knight rule only links pieces in rows that are one or two apart.",
           "When choosing a column in row <code>r</code>, also forbid <code>a &plusmn; 2</code> where <code>a</code> is the column used in row <code>r - 1</code>, and <code>b &plusmn; 1</code> where <code>b</code> is the column used in row <code>r - 2</code>. With bitmasks this is two shifts per neighbour row."],
    editorial=["Start from the N-Queens backtracking: one piece per row, columns tried from a free-mask, diagonals tracked with shifted masks. The knight rule adds a local restriction, because a knight move changes the row by 1 or 2. A piece in row <code>r - 1</code> at column <code>a</code> forbids columns <code>a - 2</code> and <code>a + 2</code> in row <code>r</code>, and a piece in row <code>r - 2</code> at column <code>b</code> forbids <code>b - 1</code> and <code>b + 1</code>. Only the last two placed columns matter, so pass them down the recursion.",
               "The extra restriction prunes the tree strongly, which is why small boards have zero solutions and even n = 12 stays cheap. Counting is exhaustive: the number of leaves reached at depth n is the answer (4 for n = 10)."],
    time="O(n!) worst case, pruned heavily", space="O(n)",
    solution='''def countAmazonPlacements(n):
    full = (1 << n) - 1

    def go(r, used, down, up, last, before_last):
        if r == n:
            return 1
        knight = ((last << 2) | (last >> 2) | (before_last << 1) | (before_last >> 1)) & full
        free = full & ~(used | down | up | knight)
        total = 0
        while free:
            bit = free & -free
            free ^= bit
            total += go(r + 1, used | bit, ((down | bit) << 1) & full, (up | bit) >> 1, bit, last)
        return total

    return go(0, 0, 0, 0, 0, 0)
''',
    tests=[[n] for n in range(1, 13)],
)


def b_amazons(n):
    placed = []

    def clash(r1, c1, r2, c2):
        dr, dc = abs(r1 - r2), abs(c1 - c2)
        return dr == 0 or dc == 0 or dr == dc or (dr, dc) in ((1, 2), (2, 1))

    def go():
        r = len(placed)
        if r == n:
            return 1
        total = 0
        for c in range(n):
            if not any(clash(r, c, r2, c2) for r2, c2 in enumerate(placed)):
                placed.append(c)
                total += go()
                placed.pop()
        return total

    return go()


def v_amazons(tests):
    for t in tests:
        assert 1 <= t["args"][0] <= 12
    assert any(t["expected"] > 0 and t["args"][0] > 1 for t in tests) and any(t["expected"] == 0 for t in tests)


CHECKS["queens-avoiding-knight-moves"] = (b_amazons, lambda r: [r.randint(1, 10)], "exact")
VALIDATE["queens-avoiding-knight-moves"] = v_amazons


# ================================================================== HARD

# ---------------------------------------------------------------- minimum colors of a graph
p = add(
    id="minimum-graph-colors", title="Minimum Colors for a Graph", diff="Hard", topic=TOPIC, tier="extra",
    fn="minGraphColors", params=[("n", "int"), ("edges", "int[][]")], ret="int", cmp="exact",
    desc="<p>An undirected graph has vertices <code>0..n-1</code> and the edge list <code>edges</code>, where every <code>[u, v]</code> joins two different vertices. Give each vertex a color so that the two ends of every edge have different colors.</p><p>Return the smallest number of colors that makes this possible (the <em>chromatic number</em> of the graph).</p><pre>n = 3, edges = [[0,1],[1,2],[0,2]]            &rarr;  3   (a triangle)\nn = 4, edges = [[0,1],[1,2],[2,3],[3,0]]      &rarr;  2   (a 4-cycle)\nn = 5, edges = [[0,1],[1,2],[2,3],[3,4],[4,0]] &rarr;  3   (an odd cycle)</pre>",
    constraints=["1 &le; n &le; 15", "0 &le; edges.length &le; n(n - 1) / 2", "No self-loops and no repeated edges; the graph may be disconnected"],
    hints=["Turn the question into a yes/no one: <em>can the graph be colored with k colors?</em> Ask it for k = 1, 2, 3, ... The first k that works is the answer, and k = n always works.",
           "To test a fixed k, color vertices one by one with backtracking: a vertex may take any color not used by an already colored neighbour. Avoid repeating mirror-image work: a vertex may open a new color only if it is the next unused one (colors are interchangeable).",
           "The order of the vertices decides the speed. Always continue with the uncolored vertex that currently sees the most different colors among its neighbours (ties: the larger degree). Such vertices fail early, which prunes the tree a lot (this is the DSATUR heuristic)."],
    editorial=["The chromatic number is found by testing k = 1, 2, 3, ... until a proper coloring with k colors exists. With no edges the answer is 1, otherwise at least 2. The test for a fixed k is a backtracking search: choose a vertex, try every allowed color, recurse, undo.",
               "Two ideas make it fast enough for n &le; 15. First, symmetry: colors are interchangeable, so a vertex may use an already used color or exactly one new color (the smallest unused one); this removes a factor of up to k! from the search. Second, dynamic vertex ordering: choose the uncolored vertex whose neighbours already use the most distinct colors (its <em>saturation</em>), breaking ties by degree. Such vertices have few options, so contradictions appear after a few levels. The worst case is still exponential, as the problem is NP-hard."],
    time="O(n * k^n) worst case, far less with pruning", space="O(n)",
    solution='''def minGraphColors(n, edges):
    if not edges:
        return 1
    adj = [0] * n
    for u, v in edges:
        adj[u] |= 1 << v
        adj[v] |= 1 << u
    deg = [bin(a).count("1") for a in adj]
    color = [-1] * n

    def feasible(k):
        for v in range(n):
            color[v] = -1

        def go(done, used):
            if done == n:
                return True
            best, best_key, best_seen = -1, (-1, -1), 0
            for v in range(n):
                if color[v] < 0:
                    seen = 0
                    a = adj[v]
                    while a:
                        low = a & -a
                        a ^= low
                        c = color[low.bit_length() - 1]
                        if c >= 0:
                            seen |= 1 << c
                    key = (bin(seen).count("1"), deg[v])
                    if key > best_key:
                        best, best_key, best_seen = v, key, seen
            options = ((1 << min(used + 1, k)) - 1) & ~best_seen
            while options:
                low = options & -options
                options ^= low
                c = low.bit_length() - 1
                color[best] = c
                if go(done + 1, max(used, c + 1)):
                    return True
            color[best] = -1
            return False

        return go(0, 0)

    k = 2
    while not feasible(k):
        k += 1
    return k
''',
    tests=[],
)
_petersen = [[i, (i + 1) % 5] for i in range(5)] + [[i, i + 5] for i in range(5)] + [[5 + i, 5 + (i + 2) % 5] for i in range(5)]
_grotzsch = [[i, (i + 1) % 5] for i in range(5)] + [[5 + i, (i + 1) % 5] for i in range(5)] + [[5 + i, (i - 1) % 5] for i in range(5)] + [[10, 5 + i] for i in range(5)]
_wheel = [[i, (i + 1) % 5] for i in range(5)] + [[5, i] for i in range(5)]
p["tests"] += [
    [3, [[0, 1], [1, 2], [0, 2]]], [4, [[0, 1], [1, 2], [2, 3], [3, 0]]], [5, [[0, 1], [1, 2], [2, 3], [3, 4], [4, 0]]],
    [1, []], [6, []], [2, [[1, 0]]], [5, [[i, j] for i in range(5) for j in range(i + 1, 5)]],
    [6, [[i, (i + 1) % 6] for i in range(6)]], [10, _petersen], [11, _grotzsch], [6, _wheel],
    [9, [[i, j] for i in range(9) for j in range(i + 1, 9) if i % 3 != j % 3]],
    [15, [[i, i + 1] for i in range(14)]],
    [12, [[i, j] for i in range(12) for j in range(i + 1, 12) if (i // 4) != (j // 4)]],
]
_r = rnd(405)
for _n, _pr in [(15, 0.3), (15, 0.5), (15, 0.7), (14, 0.6), (15, 0.85), (13, 0.45)]:
    p["tests"].append([_n, _rand_graph(_r, _n, _pr)])


def b_chromatic(n, edges):
    nb = [[] for _ in range(n)]
    for u, v in edges:
        nb[u].append(v)
        nb[v].append(u)
    for k in range(1, n + 1):
        col = [-1] * n

        def go(v):
            if v == n:
                return True
            for c in range(k):
                if all(col[u] != c for u in nb[v]):
                    col[v] = c
                    if go(v + 1):
                        return True
                    col[v] = -1
            return False

        if go(0):
            return k


def g_chromatic(r):
    n = r.randint(1, 8)
    return [n, _rand_graph(r, n, r.choice([0.0, 0.2, 0.4, 0.6, 0.85]))]


def v_chromatic(tests):
    for t in tests:
        n, edges = t["args"]
        assert 1 <= n <= 15
        _check_graph(n, edges)
    assert {1, 2, 3, 4, 5} <= {t["expected"] for t in tests}


CHECKS["minimum-graph-colors"] = (b_chromatic, g_chromatic, "exact")
VALIDATE["minimum-graph-colors"] = v_chromatic


# ---------------------------------------------------------------- sudoku solver
_SUDOKU_TESTS = [
    "530070000600195000098000060800060003400803001700020006060000280000419005000080079",
    "609200748450630090010000005394005007175309000006004000980470506067593000043000209",
    "379264518865391742241758369953476821186923475724815936592147683637582194418639250",
    "000000010400000000020000000000050407008000300001090000300400200050100000000806000",
    "091800003023050010500000000080003201070082936000001087800260105009305600010700090",
    "004000050003000048050063000000002004005010090192007060407030005900006400500784200",
    "000080040000204900160700008080090500020000000000006009907010002052000084816040000",
    "000090040780060030120500006000010800000000109008000073030046500900000000200005397",
    "200000190300090020000205307000000030008006000000001800065010080007003006009600005",
    "050031702060700080000460000084900050000000003002007000000000500100090030000014908",
    "000000000000003085001020000000507000004000100090000000500000073002010000000040009",
    "379264518865391742241758369953476821186923475724815936592147683637582194418639257",
]
_SUD_BASE = [[int(ch) for ch in "379264518865391742241758369953476821186923475724815936592147683637582194418639257"[9 * i:9 * i + 9]] for i in range(9)]


def _sud_grid(s):
    return [[int(s[9 * i + j]) for j in range(9)] for i in range(9)]


def _sud_count(g, limit=2):
    """Number of solutions of a 9 x 9 board, stopping at `limit` (used to check that puzzles are unique)."""
    rows, cols, boxes, empty = [0] * 9, [0] * 9, [0] * 9, []
    for r in range(9):
        for c in range(9):
            v = g[r][c]
            if v:
                bit = 1 << v
                if (rows[r] | cols[c] | boxes[r // 3 * 3 + c // 3]) & bit:
                    return 0
                rows[r] |= bit
                cols[c] |= bit
                boxes[r // 3 * 3 + c // 3] |= bit
            else:
                empty.append((r, c))
    found = [0]

    def go(k):
        if found[0] >= limit:
            return
        if k == len(empty):
            found[0] += 1
            return
        best, best_mask, best_n = k, 0, 10
        for i in range(k, len(empty)):
            r, c = empty[i]
            m = 0x3FE & ~(rows[r] | cols[c] | boxes[r // 3 * 3 + c // 3])
            n = bin(m).count("1")
            if n < best_n:
                best, best_mask, best_n = i, m, n
                if n <= 1:
                    break
        if best_n == 0:
            return
        empty[k], empty[best] = empty[best], empty[k]
        r, c = empty[k]
        b = r // 3 * 3 + c // 3
        m = best_mask
        while m:
            bit = m & -m
            m ^= bit
            rows[r] |= bit
            cols[c] |= bit
            boxes[b] |= bit
            go(k + 1)
            rows[r] ^= bit
            cols[c] ^= bit
            boxes[b] ^= bit
        empty[k], empty[best] = empty[best], empty[k]

    go(0)
    return found[0]


assert _sud_count(_SUD_BASE) == 1

p = add(
    id="sudoku-solver", title="Sudoku Solver", diff="Hard", topic=TOPIC, tier="must",
    fn="solveSudoku", params=[("board", "int[][]")], ret="int[][]", cmp="exact",
    desc="<p>Solve a Sudoku puzzle. The <code>board</code> is a 9 &times; 9 matrix where <code>0</code> marks an empty cell and <code>1..9</code> are given digits. Fill every empty cell so that each row, each column and each of the nine 3 &times; 3 boxes contains the digits 1 to 9 exactly once. The boxes start at rows and columns 0, 3 and 6.</p><p>Return the completed 9 &times; 9 board. Every input puzzle is valid and has <strong>exactly one</strong> solution.</p><pre>board row 0: [5,3,0, 0,7,0, 0,0,0]   &rarr;   solved row 0: [5,3,4, 6,7,8, 9,1,2]</pre>",
    constraints=["board is 9 &times; 9", "0 &le; board[i][j] &le; 9, where 0 means empty", "The puzzle has exactly one solution"],
    hints=["Find an empty cell, try the digits 1 to 9 that do not clash with its row, column or box, and recurse. If a cell has no valid digit, undo the last placement and try its next digit.",
           "Keep a bitmask of used digits for each row, column and box so that the candidates of a cell are found with a few bit operations, and update the masks when you place or remove a digit.",
           "The speed depends on which cell you fill next. Instead of scanning left to right, always take the empty cell with the fewest candidates. Forced cells (one candidate) get filled immediately and contradictions (zero candidates) are found right away; even the hardest puzzles then need only a small search."],
    editorial=["Sudoku is a constraint-satisfaction problem, and backtracking is the natural solver. Maintain three arrays of 9 bitmasks (rows, columns, boxes) holding the digits already used. The candidates of a cell <code>(r, c)</code> are the digits missing from <code>rows[r] | cols[c] | boxes[(r // 3) * 3 + c // 3]</code>. Place a candidate, update the masks, recurse, and on failure remove it and try the next one.",
               "A plain left-to-right order can need millions of steps on adversarial puzzles. The standard fix is the <em>minimum remaining values</em> rule: at each step scan the remaining empty cells, pick the one with the fewest candidates and branch only on those. Singles are forced, empty candidate sets cut the branch at once. Each node costs O(empty cells) for the scan, but the tree stays tiny, and the whole solve takes a few milliseconds. Because the puzzle has a unique solution, the first complete board found is the answer."],
    time="O(9^m) worst case (m = empty cells), tiny in practice", space="O(m)",
    solution='''def solveSudoku(board):
    g = [row[:] for row in board]
    rows, cols, boxes = [0] * 9, [0] * 9, [0] * 9
    empty = []
    for r in range(9):
        for c in range(9):
            v = g[r][c]
            if v:
                bit = 1 << v
                rows[r] |= bit
                cols[c] |= bit
                boxes[(r // 3) * 3 + c // 3] |= bit
            else:
                empty.append((r, c))
    FULL = 0x3FE

    def go(k):
        if k == len(empty):
            return True
        best, best_mask, best_n = k, 0, 10
        for i in range(k, len(empty)):
            r, c = empty[i]
            m = FULL & ~(rows[r] | cols[c] | boxes[(r // 3) * 3 + c // 3])
            n = bin(m).count("1")
            if n < best_n:
                best, best_mask, best_n = i, m, n
                if n <= 1:
                    break
        if best_n == 0:
            return False
        empty[k], empty[best] = empty[best], empty[k]
        r, c = empty[k]
        b = (r // 3) * 3 + c // 3
        m = best_mask
        while m:
            bit = m & -m
            m ^= bit
            rows[r] |= bit
            cols[c] |= bit
            boxes[b] |= bit
            g[r][c] = bit.bit_length() - 1
            if go(k + 1):
                return True
            rows[r] ^= bit
            cols[c] ^= bit
            boxes[b] ^= bit
        g[r][c] = 0
        empty[k], empty[best] = empty[best], empty[k]
        return False

    go(0)
    return g
''',
    tests=[[_sud_grid(s)] for s in _SUDOKU_TESTS],
)


def b_sudoku(board):
    g = [row[:] for row in board]

    def ok(r, c, d):
        for i in range(9):
            if g[r][i] == d or g[i][c] == d:
                return False
        br, bc = r // 3 * 3, c // 3 * 3
        return all(g[br + i][bc + j] != d for i in range(3) for j in range(3))

    def go(pos):
        while pos < 81 and g[pos // 9][pos % 9]:
            pos += 1
        if pos == 81:
            return True
        r, c = divmod(pos, 9)
        for d in range(1, 10):
            if ok(r, c, d):
                g[r][c] = d
                if go(pos + 1):
                    return True
                g[r][c] = 0
        return False

    go(0)
    return g


def g_sudoku(r):
    digits = list(range(1, 10))
    r.shuffle(digits)
    bands = [b * 3 + x for b in r.sample(range(3), 3) for x in r.sample(range(3), 3)]
    stacks = [b * 3 + x for b in r.sample(range(3), 3) for x in r.sample(range(3), 3)]
    full = [[digits[_SUD_BASE[bands[i]][stacks[j]] - 1] for j in range(9)] for i in range(9)]
    if r.random() < 0.5:
        full = [list(row) for row in zip(*full)]
    while True:
        g = [row[:] for row in full]
        for cell in r.sample(range(81), r.randint(3, 13)):
            g[cell // 9][cell % 9] = 0
        if _sud_count(g) == 1:
            return [g]


def v_sudoku(tests):
    for t in tests:
        b, sol = t["args"][0], t["expected"]
        assert len(b) == 9 and all(len(row) == 9 and all(0 <= v <= 9 for v in row) for row in b)
        assert _sud_count(b) == 1, "puzzle must have exactly one solution"
        assert all(sol[i][j] == b[i][j] or b[i][j] == 0 for i in range(9) for j in range(9))
        groups = [sol[i] for i in range(9)] + [[sol[i][j] for i in range(9)] for j in range(9)]
        groups += [[sol[bi + x][bj + y] for x in range(3) for y in range(3)] for bi in (0, 3, 6) for bj in (0, 3, 6)]
        assert all(sorted(grp) == list(range(1, 10)) for grp in groups)


CHECKS["sudoku-solver"] = (b_sudoku, g_sudoku, "exact")
VALIDATE["sudoku-solver"] = v_sudoku


# ---------------------------------------------------------------- cryptarithm solution count
p = add(
    id="cryptarithm-solution-count", title="Count Cryptarithm Solutions", diff="Hard", topic=TOPIC,
    fn="countCryptarithms", params=[("a", "string"), ("b", "string"), ("c", "string")], ret="int", cmp="exact",
    desc="<p>A <em>cryptarithm</em> is an addition <code>a + b = c</code> in which every letter stands for a decimal digit. Different letters must stand for different digits and the same letter always stands for the same digit. A word with more than one letter cannot start with the digit 0 (a one-letter word may be 0).</p><p>Given three words <code>a</code>, <code>b</code> and <code>c</code> of upper-case letters, return the number of ways to assign digits to the letters so that the number written by <code>a</code> plus the number written by <code>b</code> equals the number written by <code>c</code>.</p><pre>a = \"SEND\", b = \"MORE\", c = \"MONEY\"  &rarr;  1   (9567 + 1085 = 10652)\na = \"A\", b = \"A\", c = \"B\"           &rarr;  4   (A = 1..4, B = 2A)\na = \"AB\", b = \"AB\", c = \"AB\"        &rarr;  0</pre>",
    constraints=["1 &le; a.length, b.length &le; 8 and 1 &le; c.length &le; 9", "All words consist of the letters A-Z", "At most 10 different letters occur in the three words together"],
    hints=["With at most 10 letters there are at most 10! = 3,628,800 assignments. That is too slow to check each one in full, so use the structure of addition.",
           "Process the columns from the least significant digit. In one column, once the digits of the two addends and the incoming carry are known, the digit of the result is forced: <code>(da + db + carry) % 10</code>, and the new carry is <code>(da + db + carry) // 10</code>.",
           "Walk the columns right to left. In each column assign only letters not yet seen, let the sum letter be determined (or checked) by the formula, reject clashes with digits already in use, and respect the no-leading-zero rule. After the last column the carry must be 0."],
    editorial=["Do not enumerate permutations of all letters. Add the numbers the way you do on paper, column by column from the right, and let the search branch only on letters that appear for the first time. In a column with addend letters <code>x</code>, <code>y</code> and sum letter <code>z</code>, choose digits for the unseen addend letters (trying the unused digits), and then <code>z</code> has to be <code>(dx + dy + carry) % 10</code>: it is either already assigned (check equality) or free (check that the digit is unused). Continue with carry <code>(dx + dy + carry) // 10</code> into the next column. Columns beyond the end of a word count as digit 0. Once every column is processed the carry must be 0, which also makes the result exactly <code>a + b = c</code>.",
               "A letter fixed in an early column prunes everything later, so the number of search nodes stays small even with 10 letters. Leading letters of words longer than one character are simply never given the digit 0. Different letters get different digits, so the count of assignments is the count of distinct solutions."],
    time="O(10^k) worst case for k letters, strongly pruned", space="O(k)",
    solution='''def countCryptarithms(a, b, c):
    A, B, C = a[::-1], b[::-1], c[::-1]
    width = max(len(A), len(B), len(C))
    lead = {w[0] for w in (a, b, c) if len(w) > 1}
    val = {}
    used = [False] * 10

    def try_letter(ch, step):
        if ch is None:
            return step(0)
        if ch in val:
            return step(val[ch])
        total = 0
        for d in range(10):
            if used[d] or (d == 0 and ch in lead):
                continue
            val[ch] = d
            used[d] = True
            total += step(d)
            del val[ch]
            used[d] = False
        return total

    def column(col, carry):
        if col == width:
            return 1 if carry == 0 else 0
        la = A[col] if col < len(A) else None
        lb = B[col] if col < len(B) else None
        lc = C[col] if col < len(C) else None

        def with_a(da):
            def with_b(db):
                s = da + db + carry
                need = s % 10
                if lc is None:
                    return column(col + 1, s // 10) if need == 0 else 0
                if lc in val:
                    return column(col + 1, s // 10) if val[lc] == need else 0
                if used[need] or (need == 0 and lc in lead):
                    return 0
                val[lc] = need
                used[need] = True
                res = column(col + 1, s // 10)
                del val[lc]
                used[need] = False
                return res
            return try_letter(lb, with_b)

        return try_letter(la, with_a)

    return column(0, 0)
''',
    tests=[["SEND", "MORE", "MONEY"], ["A", "A", "B"], ["AB", "AB", "AB"], ["TWO", "TWO", "FOUR"], ["A", "A", "A"], ["A", "B", "C"],
           ["CROSS", "ROADS", "DANGER"], ["BASE", "BALL", "GAMES"], ["AB", "CD", "EFG"], ["ABC", "ABC", "ABC"], ["NO", "NO", "YES"],
           ["ZZZ", "Z", "ZZZZ"], ["ABCDEFGH", "IJ", "ABCDEFGH"], ["LEFT", "RIGHT", "CLEAR"]],
)
_r = rnd(406)
for _la, _lb in [(5, 4), (6, 6), (8, 6), (7, 7), (8, 8), (4, 4)]:
    for _try in range(1000):
        _m = _r.sample(range(10), 10)  # letter i stands for digit _m[i]
        _inv = {d: chr(65 + i) for i, d in enumerate(_m)}
        _x = _r.randint(10 ** (_la - 1), 10 ** _la - 1)
        _y = _r.randint(10 ** (_lb - 1), 10 ** _lb - 1)
        _z = _x + _y
        _ws = ["".join(_inv[int(ch)] for ch in str(v)) for v in (_x, _y, _z)]
        if len(_ws[2]) <= 9 and len(set("".join(_ws))) <= 10:
            p["tests"].append(_ws)
            break


def _crypt_val(word, mp):
    v = 0
    for ch in word:
        v = v * 10 + mp[ch]
    return v


def b_crypt(a, b, c):
    letters = sorted(set(a + b + c))
    lead = {w[0] for w in (a, b, c) if len(w) > 1}
    if len(letters) > 10:
        return 0
    if len(letters) <= 5:
        count = 0
        for digits in _perms(range(10), len(letters)):
            mp = dict(zip(letters, digits))
            if any(mp[ch] == 0 for ch in lead):
                continue
            if _crypt_val(a, mp) + _crypt_val(b, mp) == _crypt_val(c, mp):
                count += 1
        return count
    # more letters: assign in order of lowest column, check the low digits modulo 10^j as soon as they are known
    order = []
    low_col = {}
    for w in (a, b, c):
        for i, ch in enumerate(reversed(w)):
            low_col[ch] = min(low_col.get(ch, 99), i)
    order = sorted(letters, key=lambda ch: (low_col[ch], ch))
    width = max(len(a), len(b), len(c))
    ready = []  # after assigning order[:t], the largest j such that every letter in columns < j is assigned
    for t in range(len(order) + 1):
        known = set(order[:t])
        j = 0
        while j < width and all(w[-1 - j] in known for w in (a, b, c) if j < len(w)):
            j += 1
        ready.append(j)
    mp = {}
    used = set()

    def low(word, j):
        return sum(mp[ch] * 10 ** i for i, ch in enumerate(reversed(word[-j:] if j else ""))) if j else 0

    def go(t):
        if t == len(order):
            return 1 if _crypt_val(a, mp) + _crypt_val(b, mp) == _crypt_val(c, mp) else 0
        total = 0
        for d in range(10):
            if d in used or (d == 0 and order[t] in lead):
                continue
            mp[order[t]] = d
            used.add(d)
            j = ready[t + 1]
            if j == 0 or (low(a, min(j, len(a))) + low(b, min(j, len(b))) - low(c, min(j, len(c)))) % 10 ** j == 0:
                total += go(t + 1)
            del mp[order[t]]
            used.discard(d)
        return total

    return go(0)


def g_crypt(r):
    if r.random() < 0.6:
        pool = [chr(65 + i) for i in range(r.randint(2, 5))]
        digs = r.sample(range(10), len(pool))
        mp = dict(zip(pool, digs))
        inv = {d: ch for ch, d in mp.items()}
        for _ in range(60):
            x = r.randint(0, 10 ** r.randint(1, 3) - 1)
            y = r.randint(0, 10 ** r.randint(1, 3) - 1)
            z = x + y
            if all(int(ch) in inv for v in (x, y, z) for ch in str(v)):
                return ["".join(inv[int(ch)] for ch in str(v)) for v in (x, y, z)]
    pool = "ABCDE"[:r.randint(2, 5)]
    return ["".join(r.choice(pool) for _ in range(r.randint(1, 3))) for _ in range(3)]


def v_crypt(tests):
    for t in tests:
        a, b, c = t["args"]
        assert 1 <= len(a) <= 8 and 1 <= len(b) <= 8 and 1 <= len(c) <= 9
        assert all("A" <= ch <= "Z" for ch in a + b + c) and len(set(a + b + c)) <= 10
    assert any(t["expected"] == 0 for t in tests) and any(t["expected"] > 1 for t in tests)


CHECKS["cryptarithm-solution-count"] = (b_crypt, g_crypt, "exact")
VALIDATE["cryptarithm-solution-count"] = v_crypt
