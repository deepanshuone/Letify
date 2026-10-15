"""Problems: backtracking on grids and words. See data/lib.py for the registry."""
from itertools import product as _product

from lib import add, rnd, CHECKS, VALIDATE, gen_arr  # noqa: F401

TOPIC = "Backtracking"
DIRS4 = ((1, 0), (-1, 0), (0, 1), (0, -1))
DIRS8 = tuple((a, b) for a in (-1, 0, 1) for b in (-1, 0, 1) if a or b)
KNIGHT = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))


def _g(*rows):
    """Letter rows ('cat', 'dog') to a matrix of codes a=1 .. z=26."""
    return [[ord(ch) - 96 for ch in row] for row in rows]


def _ws(*words):
    return [[ord(ch) - 96 for ch in w] for w in words]


def _str(codes):
    return "".join(chr(96 + x) for x in codes)


def _rand_board(r, m, n, k):
    return [[r.randint(1, k) for _ in range(n)] for _ in range(m)]


def _walk(r, board, length):
    """Letters read along a random self-avoiding walk of the board (stops early when stuck)."""
    m, n = len(board), len(board[0])
    cr, cc = r.randrange(m), r.randrange(n)
    seen = {(cr, cc)}
    out = [board[cr][cc]]
    while len(out) < length:
        opts = [(cr + a, cc + b) for a, b in DIRS4 if 0 <= cr + a < m and 0 <= cc + b < n and (cr + a, cc + b) not in seen]
        if not opts:
            break
        cr, cc = r.choice(opts)
        seen.add((cr, cc))
        out.append(board[cr][cc])
    return out


def _legal_board(board, lo=1, hi=26):
    assert board and all(len(row) == len(board[0]) for row in board)
    assert all(lo <= x <= hi for row in board for x in row)


# ================================================================== EASY

# ---------------------------------------------------------------- word in straight lines
p = add(
    id="word-in-straight-lines-count", title="Word in Straight Lines", diff="Easy", topic=TOPIC,
    fn="countStraightWords", params=[("board", "int[][]"), ("word", "string")], ret="int", cmp="exact",
    desc="<p>A grid of letters is given as an integer matrix <code>board</code>: <code>1</code> stands for <code>a</code>, <code>2</code> for <code>b</code>, and so on up to <code>26</code> for <code>z</code>.</p><p>Count how many times the lowercase string <code>word</code> can be read along a straight line of the grid. A reading is fixed by a start cell and one of the <strong>8</strong> directions (left, right, up, down and the four diagonals). The letters of the word must sit on consecutive cells in that direction, and the whole line must stay inside the grid. Two readings are different when their start cell or their direction differs, so a palindrome such as <code>aba</code> is counted once from each of its two ends.</p><p>For example, in the board <code>[[1,2,1],[2,1,2],[1,2,1]]</code> (rows <code>aba</code>, <code>bab</code>, <code>aba</code>) the word <code>aba</code> can be read 8 times: along the top row, the bottom row, the left column and the right column, each in both directions.</p>",
    constraints=["1 &le; board.length, board[i].length &le; 50", "1 &le; board[i][j] &le; 26", "2 &le; word.length &le; 25", "word contains only lowercase letters"],
    hints=["Treat every cell as a possible start and every one of the 8 direction vectors <code>(dr, dc)</code> (all pairs from <code>-1..1</code> except <code>(0, 0)</code>) as a possible direction.",
           "For a fixed start and direction the last letter would sit at <code>(r + dr * (L - 1), c + dc * (L - 1))</code>. If that cell is outside the grid, skip this pair at once; otherwise compare the letters one by one.",
           "Stop comparing at the first mismatch. Add one to the answer when all <code>L</code> letters match. The cost is at most <code>m * n * 8 * L</code> character comparisons, and no cell needs to be marked as used."],
    editorial=["There is no choice to make once the start cell and the direction are fixed: the line of cells is determined, so a direct check is enough. Loop over all cells whose letter equals the first letter of the word, over the 8 directions, discard the pairs whose end cell leaves the grid, and verify the remaining letters one by one, stopping at the first mismatch.",
               "This is the straight-line cousin of the word-path problems that need real backtracking (where the path may turn). Writing the direct check first makes the difference clear: here no cell is ever reused and nothing needs to be undone. The work is at most <code>8 * m * n * L</code> comparisons, and the extra space is constant."],
    time="O(8 &middot; m &middot; n &middot; L)", space="O(1)",
    solution='''def countStraightWords(board, word):
    m, n = len(board), len(board[0])
    codes = [ord(ch) - 96 for ch in word]
    L = len(codes)
    total = 0
    for r in range(m):
        for c in range(n):
            if board[r][c] != codes[0]:
                continue
            for dr in (-1, 0, 1):
                for dc in (-1, 0, 1):
                    if dr == 0 and dc == 0:
                        continue
                    er, ec = r + dr * (L - 1), c + dc * (L - 1)
                    if not (0 <= er < m and 0 <= ec < n):
                        continue
                    k = 1
                    while k < L and board[r + dr * k][c + dc * k] == codes[k]:
                        k += 1
                    if k == L:
                        total += 1
    return total
''',
    tests=[[_g("aba", "bab", "aba"), "aba"],
           [_g("cat"), "tac"],
           [_g("aa", "aa"), "aa"],
           [_g("x"), "xx"],
           [_g("wxyz"), "wxyz"],
           [_g("ab", "ba"), "ab"],
           [_g("abc", "def", "ghi"), "aei"],
           [_g("abc", "def", "ghi"), "ihg"],
           [_g("level", "evnal", "vvlel", "eexel", "lleve"), "level"],
           [_g("aaa", "aaa", "aaa"), "aaa"],
           [_g("hello", "world"), "xyz"]],
)
_r = rnd(1101)
p["tests"].append([_rand_board(_r, 12, 9, 3), "abca"])
_b = _rand_board(_r, 50, 50, 26)
for _ in range(40):   # plant the word along random lines of a big random board
    _w = [_r.randint(1, 26) for _ in range(6)]
    _dr, _dc = _r.choice(DIRS8)
    _sr, _sc = _r.randrange(50), _r.randrange(50)
    if 0 <= _sr + 5 * _dr < 50 and 0 <= _sc + 5 * _dc < 50:
        for _k in range(6):
            _b[_sr + _k * _dr][_sc + _k * _dc] = 3 + _k
p["tests"].append([_b, "cdefgh"])
p["tests"].append([[[1] * 50 for _ in range(50)], "a" * 25])
p["tests"].append([_rand_board(_r, 50, 50, 2), "ababab"])


def b_lines(board, word):
    m, n = len(board), len(board[0])
    s = [_str(row) for row in board]
    lines = list(s)
    lines += ["".join(board_row[c] for board_row in s) for c in range(n)]
    for d in range(-(m - 1), n):
        lines.append("".join(s[i][i + d] for i in range(m) if 0 <= i + d < n))
    for d in range(m + n - 1):
        lines.append("".join(s[i][d - i] for i in range(m) if 0 <= d - i < n))
    tot = 0
    for ln in lines:
        for t in (ln, ln[::-1]):
            for i in range(len(t) - len(word) + 1):
                if t[i:i + len(word)] == word:
                    tot += 1
    return tot


def g_lines(r):
    m, n, k = r.randint(1, 5), r.randint(1, 5), r.randint(1, 3)
    return [_rand_board(r, m, n, k), _str([r.randint(1, k) for _ in range(r.randint(2, 4))])]


def v_lines(tests):
    for t in tests:
        board, word = t["args"]
        _legal_board(board)
        assert len(board) <= 50 and len(board[0]) <= 50 and 2 <= len(word) <= 25 and word.islower() and word.isalpha()
    assert any(t["expected"] == 0 for t in tests) and any(t["expected"] > 20 for t in tests)


CHECKS["word-in-straight-lines-count"] = (b_lines, g_lines, "exact")
VALIDATE["word-in-straight-lines-count"] = v_lines

# ---------------------------------------------------------------- maze routes
p = add(
    id="maze-simple-paths-count", title="Maze Routes Without Revisits", diff="Easy", topic=TOPIC,
    fn="countMazeRoutes", params=[("maze", "int[][]")], ret="int", cmp="exact",
    desc="<p>A maze is an integer matrix <code>maze</code> in which <code>0</code> is an open cell and <code>1</code> is a wall. The top-left cell and the bottom-right cell are always open (they are the same cell when the maze has a single cell).</p><p>A <em>route</em> starts at the top-left cell and moves one step at a time to the open cell directly above, below, left or right. A route may <strong>not</strong> visit any cell twice, and it ends the first time it reaches the bottom-right cell. Return the number of different routes. Two routes are different when they visit their cells in a different order.</p><p>For example, an open <code>2 x 2</code> maze has 2 routes (right then down, or down then right), and an open <code>3 x 3</code> maze has 12 routes, because routes may also wander, for example through the cells <code>(0,0), (0,1), (1,1), (1,0), (2,0), (2,1), (2,2)</code>, as long as they never step on a used cell.</p>",
    constraints=["1 &le; maze.length, maze[i].length and maze.length &middot; maze[i].length &le; 25", "maze[i][j] is 0 or 1", "maze[0][0] = 0 and the bottom-right cell is 0"],
    hints=["A route is a sequence of cells, so it can be built one cell at a time. Count how many ways each partial route can be finished.",
           "Keep a <code>visited</code> grid. From the current cell try each of the 4 neighbours that is inside the maze, open and not visited, recurse, and then mark the neighbour as unvisited again so that other routes may use it.",
           "When the recursion arrives at the bottom-right cell it has found one complete route: return 1 and do not continue past that cell. The answer is the sum over all choices."],
    editorial=["This is plain backtracking with undo. <code>go(r, c)</code> returns the number of ways to finish a route that currently stands on <code>(r, c)</code>. At the target it returns 1. Otherwise it marks the cell visited, adds up <code>go</code> over the neighbours that are open and unvisited, and finally unmarks the cell, so that a different route can pass through it later.",
               "The number of routes can be much larger than the number of cells (an open <code>5 x 5</code> maze already has 8,512), and the search enumerates every route, so the running time grows with the answer. The size limit of 30 cells keeps the answer small enough for that. A simple speed-up is to stop a branch when the target is no longer reachable from the current cell, but it is not needed here."],
    time="O(number of routes &middot; path length)", space="O(m &middot; n)",
    solution='''def countMazeRoutes(maze):
    m, n = len(maze), len(maze[0])
    w = n + 2                       # one extra column of walls on each side, and rows above and below
    blocked = [True] * ((m + 2) * w)
    for r in range(m):
        for c in range(n):
            blocked[(r + 1) * w + c + 1] = maze[r][c] == 1
    start, target = w + 1, m * w + n
    steps = (w, -w, 1, -1)

    def go(cell):
        if cell == target:
            return 1
        blocked[cell] = True        # visited cells behave like walls
        total = 0
        for d in steps:
            nxt = cell + d
            if not blocked[nxt]:
                total += go(nxt)
        blocked[cell] = False
        return total

    return go(start)
''',
    tests=[[[[0, 0], [0, 0]]],
           [[[0, 0, 0], [0, 0, 0], [0, 0, 0]]],
           [[[0, 1], [1, 0]]],
           [[[0]]],
           [[[0, 0, 0, 0, 0]]],
           [[[0, 0], [0, 1], [0, 0]]],
           [[[0, 0, 0], [0, 1, 0], [0, 0, 0]]],
           [[[0, 0, 1, 0], [1, 0, 0, 0], [0, 0, 1, 0], [0, 1, 0, 0]]],
           [[[0] * 4 for _ in range(4)]],
           [[[0] * 5 for _ in range(5)]],
           [[[0] * 6 for _ in range(4)]],
           [[[0, 0, 0, 0, 0, 0], [0, 1, 0, 1, 1, 0], [0, 0, 0, 0, 0, 0], [1, 0, 1, 0, 1, 0]]],
           [[[0, 0, 0, 0, 0, 0, 0, 0], [0, 1, 1, 1, 1, 1, 1, 0], [0, 0, 0, 0, 0, 0, 0, 0]]]],
)


def b_maze(maze):
    # dynamic programming over (cell, set of visited cells) instead of recursion
    m, n = len(maze), len(maze[0])
    target = (m - 1) * n + n - 1
    states = {(0, 1): 1}
    total = 0
    while states:
        nxt = {}
        for (cell, mask), ways in states.items():
            if cell == target:
                total += ways
                continue
            r, c = divmod(cell, n)
            for dr, dc in DIRS4:
                nr, nc = r + dr, c + dc
                if 0 <= nr < m and 0 <= nc < n and maze[nr][nc] == 0 and not mask >> (nr * n + nc) & 1:
                    key = (nr * n + nc, mask | 1 << (nr * n + nc))
                    nxt[key] = nxt.get(key, 0) + ways
        states = nxt
    return total


def g_maze(r):
    m, n = r.randint(1, 4), r.randint(1, 4)
    pw = r.choice((0.0, 0.15, 0.3))
    g = [[1 if r.random() < pw else 0 for _ in range(n)] for _ in range(m)]
    g[0][0] = g[m - 1][n - 1] = 0
    return [g]


def v_maze(tests):
    for t in tests:
        g = t["args"][0]
        _legal_board(g, 0, 1)
        assert len(g) * len(g[0]) <= 25 and g[0][0] == 0 and g[-1][-1] == 0
    assert any(t["expected"] == 0 for t in tests) and any(t["expected"] > 1000 for t in tests)


CHECKS["maze-simple-paths-count"] = (b_maze, g_maze, "exact")
VALIDATE["maze-simple-paths-count"] = v_maze


# ================================================================== MEDIUM

# ---------------------------------------------------------------- count word paths
p = add(
    id="word-path-count-in-grid", title="Count the Ways to Spell a Word", diff="Medium", topic=TOPIC,
    fn="countWordPaths", params=[("board", "int[][]"), ("word", "string")], ret="int", cmp="exact",
    desc="<p>A grid of letters is given as an integer matrix <code>board</code> (<code>1</code> is <code>a</code>, <code>2</code> is <code>b</code>, ..., <code>26</code> is <code>z</code>).</p><p>A <em>path</em> that spells <code>word</code> uses one cell per letter, in order. Every cell after the first must be directly above, below, left or right of the previous cell, and a cell may not be used twice in the same path. Return the number of different paths that spell <code>word</code>; paths are different when they use different cells or the same cells in a different order.</p><p>For example, in the board <code>[[1,1],[1,1]]</code> the word <code>aaa</code> can be spelled in 8 ways (4 starting cells, and from each one the path can turn clockwise or counterclockwise), and in <code>[[1,2],[2,1]]</code> the word <code>ab</code> can be spelled in 4 ways.</p>",
    constraints=["1 &le; board.length, board[i].length &le; 5", "1 &le; board[i][j] &le; 26", "1 &le; word.length &le; 9", "word contains only lowercase letters"],
    hints=["Decide a start cell, then every later letter has at most 3 possible next cells. Counting paths is the same search as finding one, except that you keep going after you succeed.",
           "Write <code>go(r, c, k)</code>: the number of ways to spell <code>word[k:]</code> when the path stands on cell <code>(r, c)</code> and that cell already matches <code>word[k]</code>. At <code>k == L - 1</code> return 1; otherwise mark the cell, add up <code>go</code> over the unvisited neighbours that match <code>word[k + 1]</code>, and unmark the cell.",
           "Never recurse into a neighbour whose letter does not match: this prunes almost the whole tree for ordinary words. Sum <code>go</code> over every start cell whose letter is <code>word[0]</code>."],
    editorial=["The classic word search asks whether a path exists and may stop at the first one. Counting asks for all of them, so the search must not stop early: every branch that matches the next letter is explored, and the results are added. A DFS with a <code>visited</code> grid does this, and un-marking the cell on the way back lets other paths reuse it (that is the backtracking part).",
               "A memo table keyed on <code>(cell, k)</code> would be wrong here, because the number of ways to finish depends on <em>which cells have already been used</em>, not only on the current cell and position. Instead the running time is proportional to the number of partial paths that match a prefix of the word, at most <code>m * n * 3<sup>L-1</sup></code>, and the small limits (5 x 5 board, word length at most 9) keep that fast."],
    time="O(m &middot; n &middot; 3<sup>L</sup>)", space="O(m &middot; n)",
    solution='''def countWordPaths(board, word):
    m, n = len(board), len(board[0])
    codes = [ord(ch) - 96 for ch in word]
    L = len(codes)
    seen = [[False] * n for _ in range(m)]

    def go(r, c, k):
        if k == L - 1:
            return 1
        seen[r][c] = True
        total = 0
        want = codes[k + 1]
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nr, nc = r + dr, c + dc
            if 0 <= nr < m and 0 <= nc < n and board[nr][nc] == want and not seen[nr][nc]:
                total += go(nr, nc, k + 1)
        seen[r][c] = False
        return total

    total = 0
    for r in range(m):
        for c in range(n):
            if board[r][c] == codes[0]:
                total += go(r, c, 0)
    return total
''',
    tests=[[_g("aa", "aa"), "aaa"],
           [_g("ab", "ba"), "ab"],
           [_g("abc", "bca", "cab"), "abca"],
           [_g("a"), "a"],
           [_g("a"), "aa"],
           [_g("abc", "def"), "abcfed"],
           [_g("abc", "def"), "abefcb"],
           [_g("aaa", "aaa", "aaa"), "aaaaaaaaa"],
           [_g("aaa", "aaa", "aaa"), "aaaaa"],
           [_g("aab", "aba", "baa"), "aabab"],
           [_g("xyz"), "xyzx"]],
)
_r = rnd(1103)
for _m, _n, _k, _len in ((5, 5, 2, 9), (5, 4, 3, 8), (4, 5, 2, 9), (5, 5, 3, 9)):
    _b = _rand_board(_r, _m, _n, _k)
    p["tests"].append([_b, _str(_walk(_r, _b, _len))])   # a word that is certainly on the board
p["tests"].append([[[1] * 5 for _ in range(5)], "a" * 9])
p["tests"].append([[[1] * 5 for _ in range(5)], "a" * 7 + "b"])


def b_wcount(board, word):
    m, n = len(board), len(board[0])
    codes = [ord(ch) - 96 for ch in word]
    cur = {(r * n + c, 1 << (r * n + c)): 1 for r in range(m) for c in range(n) if board[r][c] == codes[0]}
    for ch in codes[1:]:
        nxt = {}
        for (cell, mask), ways in cur.items():
            r, c = divmod(cell, n)
            for dr, dc in DIRS4:
                nr, nc = r + dr, c + dc
                if 0 <= nr < m and 0 <= nc < n and board[nr][nc] == ch and not mask >> (nr * n + nc) & 1:
                    key = (nr * n + nc, mask | 1 << (nr * n + nc))
                    nxt[key] = nxt.get(key, 0) + ways
        cur = nxt
    return sum(cur.values())


def g_wcount(r):
    m, n, k = r.randint(1, 4), r.randint(1, 4), r.randint(1, 3)
    return [_rand_board(r, m, n, k), _str([r.randint(1, k) for _ in range(r.randint(1, 6))])]


def v_wcount(tests):
    for t in tests:
        board, word = t["args"]
        _legal_board(board)
        assert len(board) <= 5 and len(board[0]) <= 5 and 1 <= len(word) <= 9 and word.islower() and word.isalpha()
    assert any(t["expected"] == 0 for t in tests) and any(t["expected"] > 1000 for t in tests)


CHECKS["word-path-count-in-grid"] = (b_wcount, g_wcount, "exact")
VALIDATE["word-path-count-in-grid"] = v_wcount

# ---------------------------------------------------------------- domino tilings with holes
p = add(
    id="domino-tilings-with-holes", title="Domino Tilings with Holes", diff="Medium", topic=TOPIC,
    fn="countDominoTilings", params=[("grid", "int[][]")], ret="int", cmp="exact",
    desc="<p>A board is given as an integer matrix <code>grid</code>, where <code>0</code> is a free cell and <code>1</code> is a hole. A domino covers exactly two free cells that share a side (it may lie horizontally or vertically).</p><p>Count the ways to place dominoes so that every free cell is covered by exactly one domino and no domino touches a hole. Two ways are different when the sets of dominoes differ. A board with no free cell at all has exactly one way (place nothing).</p><p>For example, a free <code>2 x 3</code> board has 3 tilings, and a free <code>2 x 2</code> board has 2.</p>",
    constraints=["1 &le; grid.length, grid[i].length and grid.length &middot; grid[i].length &le; 36", "grid[i][j] is 0 or 1"],
    hints=["Look at the first free cell in row-major order (top row first, left to right). Whatever tiling you build, some domino must cover that cell.",
           "That domino can only go to the right or down: the cell above and the cell to the left are either holes or already covered (they come earlier in the order). So there are at most 2 choices per step.",
           "Keep an occupancy bitmask of all cells that are covered or are holes. Find the lowest empty bit, try the two placements that are possible, recurse, and add the counts. When no empty cell is left, return 1."],
    editorial=["Always completing the <em>first</em> uncovered cell removes all symmetry: each tiling is produced exactly once, because the domino over the first free cell is forced to extend to the right or downward. A bitmask <code>filled</code> in row-major order holds holes and covered cells; <code>low = ~filled &amp; (filled + 1)</code> isolates the first empty cell. A horizontal domino needs the next bit empty and the cell to stay in the same row, a vertical one needs the bit one row below to be empty and inside the board.",
               "The number of search nodes is about the number of partial tilings that are still extendable. A full 6 x 6 board has 6,728 tilings, which is fast. A broken-profile dynamic programme (storing the occupancy of the next <code>n</code> cells) would count much larger boards in polynomial time per row, but the 36-cell limit lets plain backtracking pass."],
    time="O(number of partial tilings)", space="O(m &middot; n) recursion",
    solution='''def countDominoTilings(grid):
    m, n = len(grid), len(grid[0])
    total_cells = m * n
    full = (1 << total_cells) - 1
    holes = 0
    for r in range(m):
        for c in range(n):
            if grid[r][c] == 1:
                holes |= 1 << (r * n + c)

    def go(filled):
        if filled == full:
            return 1
        low = ~filled & (filled + 1)        # lowest empty cell
        pos = low.bit_length() - 1
        r, c = divmod(pos, n)
        ways = 0
        if c + 1 < n and not filled >> (pos + 1) & 1:
            ways += go(filled | low | (low << 1))
        if r + 1 < m and not filled >> (pos + n) & 1:
            ways += go(filled | low | (low << n))
        return ways

    return go(holes)
''',
    tests=[[[[0, 0, 0], [0, 0, 0]]],
           [[[0, 0], [0, 0]]],
           [[[0, 0, 0, 0], [0, 1, 1, 0], [0, 0, 0, 0]]],
           [[[0]]],
           [[[1]]],
           [[[0, 0]]],
           [[[0], [0], [0]]],
           [[[0, 0, 0], [0, 0, 0], [0, 0, 0]]],
           [[[0] * 4 for _ in range(4)]],
           [[[0] * 3 for _ in range(4)]],
           [[[0, 0, 0, 0, 0, 0]] + [[0] * 6 for _ in range(4)] + [[0, 0, 0, 0, 0, 0]]],
           [[[1, 0, 0, 0, 0, 0]] + [[0] * 6 for _ in range(4)] + [[0, 0, 0, 0, 0, 1]]],
           [[[0] * 9 for _ in range(4)]],
           [[[0] * 12 for _ in range(3)]],
           [[[0] * 18 for _ in range(2)]]],
)
_r = rnd(1104)


def _holey_board(r, m, n, dominoes):
    """A board that is certainly tileable: lay random dominoes, everything else becomes a hole."""
    g = [[1] * n for _ in range(m)]
    placed = 0
    while placed < dominoes:
        a, b = r.randrange(m), r.randrange(n)
        dr, dc = r.choice(((0, 1), (1, 0)))
        if a + dr < m and b + dc < n and g[a][b] == 1 and g[a + dr][b + dc] == 1:
            g[a][b] = g[a + dr][b + dc] = 0
            placed += 1
    return g


p["tests"].append([_holey_board(_r, 6, 6, 17)])
p["tests"].append([_holey_board(_r, 4, 9, 15)])
p["tests"].append([[[0, 0, 1, 0, 0, 0, 0], [0, 0, 0, 0, 1, 0, 0], [0, 1, 0, 0, 0, 0, 0], [0, 0, 0, 1, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0]]])


def b_domino(grid):
    # broken-profile DP: process cells in row-major order, remember which of the next n cells are already covered
    m, n = len(grid), len(grid[0])
    dp = {0: 1}
    for r in range(m):
        for c in range(n):
            nd = {}
            for prof, ways in dp.items():
                covered = prof & 1
                rest = prof >> 1
                if grid[r][c] == 1:
                    if covered:
                        continue
                    nd[rest] = nd.get(rest, 0) + ways
                    continue
                if covered:
                    nd[rest] = nd.get(rest, 0) + ways
                    continue
                # horizontal: needs the right neighbour free and not covered
                if c + 1 < n and grid[r][c + 1] == 0 and not rest & 1:
                    k = rest | 1
                    nd[k] = nd.get(k, 0) + ways
                # vertical: covers the cell n below (bit n-1 of rest)
                if r + 1 < m and grid[r + 1][c] == 0:
                    k = rest | (1 << (n - 1))
                    nd[k] = nd.get(k, 0) + ways
            dp = nd
    return dp.get(0, 0)


def g_domino(r):
    m, n = r.randint(1, 4), r.randint(1, 5)
    pw = r.choice((0.0, 0.1, 0.25))
    return [[[1 if r.random() < pw else 0 for _ in range(n)] for _ in range(m)]]


def v_domino(tests):
    for t in tests:
        g = t["args"][0]
        _legal_board(g, 0, 1)
        assert len(g) * len(g[0]) <= 36
    assert any(t["expected"] == 0 for t in tests) and any(t["expected"] > 4000 for t in tests)


CHECKS["domino-tilings-with-holes"] = (b_domino, g_domino, "exact")
VALIDATE["domino-tilings-with-holes"] = v_domino

# ---------------------------------------------------------------- longest path of distinct letters
p = add(
    id="longest-distinct-letter-path", title="Longest Path of Distinct Letters", diff="Medium", topic=TOPIC,
    fn="longestDistinctLetterPath", params=[("board", "int[][]")], ret="int", cmp="exact",
    desc="<p>A grid of letters is given as an integer matrix <code>board</code> (<code>1</code> is <code>a</code>, <code>2</code> is <code>b</code>, ..., <code>26</code> is <code>z</code>).</p><p>A path starts at any cell and moves one step at a time to the cell directly above, below, left or right. The path is <em>valid</em> when no two cells on it carry the same letter (so it can never use a cell twice either). Return the number of cells of the longest valid path. A single cell is a valid path, so the answer is at least 1.</p><p>For example, <code>[[1,2,3],[6,5,4]]</code> has 6 different letters and the snake <code>a, b, c, d, e, f</code> visits all of them, so the answer is 6. In <code>[[1,2,1],[2,1,2]]</code> only the letters <code>a</code> and <code>b</code> exist, so no path can be longer than 2.</p>",
    constraints=["1 &le; board.length, board[i].length and board.length &middot; board[i].length &le; 20", "1 &le; board[i][j] &le; 26"],
    hints=["A path with pairwise different letters never reuses a cell, so a bitmask of the letters used so far replaces the visited grid.",
           "From a start cell, try each neighbour whose letter is not in the mask, add the letter to the mask, recurse, and remember the longest length seen. The mask is passed by value, so there is nothing to undo.",
           "Two prunings: the answer cannot exceed the number of distinct letters in the whole grid, so stop everything once that length is reached; and the future of a search depends only on <code>(cell, mask)</code>, so remember the pairs already expanded and skip them."],
    editorial=["Start a DFS from every cell with the mask containing only that cell's letter. At each cell try the four neighbours, skip those whose letter is already in the mask, and recurse with the extended mask. The depth of the recursion is at most 20, the number of cells, and the best depth reached over the whole search is the answer.",
               "Because the position and the set of letters used completely determine what can still be reached, a set of visited <code>(cell, mask)</code> pairs avoids exploring the same situation twice (different routes can reach the same cell with the same letters when letters repeat in the grid). The upper bound <code>number of distinct letters</code> gives an early exit in the common case where a long snake exists. In the worst case the search still looks at every self-avoiding path with distinct letters, which is why the board is limited to 20 cells."],
    time="O(number of distinct (cell, letter set) states)", space="O(states)",
    solution='''def longestDistinctLetterPath(board):
    m, n = len(board), len(board[0])
    distinct = len({x for row in board for x in row})
    nbrs = [[[(r + dr, c + dc) for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1))
              if 0 <= r + dr < m and 0 <= c + dc < n] for c in range(n)] for r in range(m)]
    best = 0
    seen = set()

    def go(r, c, mask, length):
        nonlocal best
        if length > best:
            best = length
        if best == distinct:
            return
        for nr, nc in nbrs[r][c]:
            bit = 1 << board[nr][nc]
            if not mask & bit:
                key = (nr, nc, mask | bit)
                if key not in seen:
                    seen.add(key)
                    go(nr, nc, mask | bit, length + 1)
                    if best == distinct:
                        return

    for r in range(m):
        for c in range(n):
            go(r, c, 1 << board[r][c], 1)
            if best == distinct:
                return best
    return best
''',
    tests=[[[[1, 2, 3], [6, 5, 4]]],
           [[[1, 2, 1], [2, 1, 2]]],
           [[[1, 2, 3], [3, 2, 1], [1, 3, 2]]],
           [[[5]]],
           [[[7, 7, 7], [7, 7, 7]]],
           [[[1, 2, 3, 4, 5, 6, 7, 8]]],
           [[[1, 2, 1, 3, 1, 4]]],
           [[[1, 1, 1, 1], [1, 2, 3, 1], [1, 4, 5, 1], [1, 1, 1, 1]]],
           [[[1, 2, 3, 4, 5], [10, 9, 8, 7, 6], [11, 12, 13, 14, 15], [20, 19, 18, 17, 16]]],
           [[[1, 2, 3, 4, 5], [2, 3, 4, 5, 1], [3, 4, 5, 1, 2], [4, 5, 1, 2, 3]]],
           [[[1, 2, 3, 4, 5], [6, 7, 8, 9, 10], [11, 12, 13, 14, 15], [16, 17, 18, 19, 3]]],
           [[[1, 2, 2, 1], [3, 4, 4, 3], [5, 6, 6, 5], [1, 2, 2, 1], [3, 4, 4, 3]]]],
)
_r = rnd(1105)
for _m, _n, _k in ((4, 5, 12), (4, 5, 26), (5, 4, 9), (3, 6, 15)):
    p["tests"].append([_rand_board(_r, _m, _n, _k)])


def b_distinct(board):
    m, n = len(board), len(board[0])
    layer = {(r * n + c, 1 << board[r][c]) for r in range(m) for c in range(n)}
    length = 0
    while layer:
        length += 1
        nxt = set()
        for cell, mask in layer:
            r, c = divmod(cell, n)
            for dr, dc in DIRS4:
                nr, nc = r + dr, c + dc
                if 0 <= nr < m and 0 <= nc < n and not mask >> board[nr][nc] & 1:
                    nxt.add((nr * n + nc, mask | 1 << board[nr][nc]))
        layer = nxt
    return length


def g_distinct(r):
    m, n, k = r.randint(1, 4), r.randint(1, 4), r.randint(1, 9)
    return [_rand_board(r, m, n, k)]


def v_distinct(tests):
    for t in tests:
        g = t["args"][0]
        _legal_board(g)
        assert len(g) * len(g[0]) <= 20 and t["expected"] >= 1
    assert any(t["expected"] >= 10 for t in tests)


CHECKS["longest-distinct-letter-path"] = (b_distinct, g_distinct, "exact")
VALIDATE["longest-distinct-letter-path"] = v_distinct

# ---------------------------------------------------------------- required cells path count
p = add(
    id="required-cells-path-count", title="Routes Through Required Cells", diff="Medium", topic=TOPIC,
    fn="countRoutesThroughRequired", params=[("grid", "int[][]")], ret="int", cmp="exact",
    desc="<p>A grid is an integer matrix. The values mean: <code>1</code> the start cell, <code>2</code> the end cell, <code>3</code> a <em>required</em> cell, <code>0</code> an ordinary free cell, and <code>-1</code> a blocked cell that can never be entered. There is exactly one start and exactly one end cell, and there may be any number of required cells.</p><p>A route begins on the start cell and moves one step at a time up, down, left or right. It may not enter a blocked cell and may not visit any cell twice. The route finishes the first time it reaches the end cell. Return the number of routes that visit <strong>every</strong> required cell before finishing. Ordinary free cells may be visited or skipped, and two routes are different when they visit their cells in a different order.</p><p>For example, in <code>[[1,3,2],[0,0,0]]</code> the answer is 3: the direct walk along the top row, and two walks that dip into the bottom row and climb back to the top row through the required cell; in <code>[[1,0,2]]</code> there is one route and no cell is required, so it counts.</p>",
    constraints=["1 &le; grid.length, grid[i].length and grid.length &middot; grid[i].length &le; 25", "grid[i][j] is one of -1, 0, 1, 2, 3", "Exactly one cell is 1 and exactly one cell is 2"],
    hints=["Count the required cells first. A finished route is only valid if none is left over when it reaches the end.",
           "Run a DFS from the start with a <code>visited</code> grid and a counter <code>left</code> of required cells still unvisited. Entering a required cell decreases the counter.",
           "At the end cell return 1 if <code>left == 0</code> and 0 otherwise, and never walk on from the end cell. Elsewhere mark the cell, add up the results for all open unvisited neighbours, and unmark the cell on the way back."],
    editorial=["Compared with counting all routes between two cells, the only new ingredient is the counter of required cells that have not been seen yet. It is passed down the recursion (so it needs no undo), and it is checked only at the end cell: a route that arrives there with required cells left is simply not counted. The route cannot continue past the end cell, because the end cell may not be visited twice.",
               "The search enumerates the routes, so its cost grows with the number of routes between the two cells in a grid of at most 25 cells (at most about 9,000 on a 25-cell board). Pruning is possible, for example abandoning a branch as soon as a required cell can no longer be reached, but it is not required."],
    time="O(number of routes &middot; path length)", space="O(m &middot; n)",
    solution='''def countRoutesThroughRequired(grid):
    m, n = len(grid), len(grid[0])
    w = n + 2                              # border of blocked cells so that no bounds checks are needed
    blocked = [True] * ((m + 2) * w)
    required = [False] * ((m + 2) * w)
    need = 0
    for r in range(m):
        for c in range(n):
            v = grid[r][c]
            i = (r + 1) * w + c + 1
            blocked[i] = v == -1
            if v == 1:
                start = i
            elif v == 2:
                end = i
            elif v == 3:
                required[i] = True
                need += 1
    steps = (w, -w, 1, -1)

    def go(cell, left):
        if cell == end:
            return 1 if left == 0 else 0
        blocked[cell] = True
        total = 0
        for d in steps:
            nxt = cell + d
            if not blocked[nxt]:
                total += go(nxt, left - 1 if required[nxt] else left)
        blocked[cell] = False
        return total

    return go(start, need)
''',
    tests=[[[[1, 3, 2], [0, 0, 0]]],
           [[[1, 0, 2]]],
           [[[1, 0, 0], [0, 3, 0], [0, 0, 2]]],
           [[[1, 2]]],
           [[[1, -1, 2], [0, -1, 3]]],
           [[[1, 3, 2]]],
           [[[2, 3, 1]]],
           [[[1, 0, 2], [3, 0, 0]]],
           [[[1, -1, 2], [0, 3, 0]]],
           [[[1, 0, 0, 0], [0, 3, 0, 0], [0, 0, 3, 0], [0, 0, 0, 2]]],
           [[[1, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 2]]],
           [[[0, 0, 0, 0, 0], [0, 1, 0, 0, 0], [0, 0, 3, 0, 0], [0, 0, 0, 2, 0], [0, 0, 0, 0, 0]]],
           [[[3, 0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 1, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 2]]],
           [[[1, 0, 0, 0, 0, 0], [0, 0, -1, 0, 0, 0], [0, 0, 0, 3, 0, 0], [0, 0, 0, 0, 0, 2]]],
           [[[3, 0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [1, 0, 0, 0, 2]]]],
)


def b_required(grid):
    m, n = len(grid), len(grid[0])
    req = 0
    for r in range(m):
        for c in range(n):
            if grid[r][c] == 1:
                st = r * n + c
            elif grid[r][c] == 2:
                en = r * n + c
            elif grid[r][c] == 3:
                req |= 1 << (r * n + c)
    states = {(st, 1 << st): 1}
    total = 0
    while states:
        nxt = {}
        for (cell, mask), ways in states.items():
            if cell == en:
                if mask & req == req:
                    total += ways
                continue
            r, c = divmod(cell, n)
            for dr, dc in DIRS4:
                nr, nc = r + dr, c + dc
                if 0 <= nr < m and 0 <= nc < n and grid[nr][nc] != -1 and not mask >> (nr * n + nc) & 1:
                    key = (nr * n + nc, mask | 1 << (nr * n + nc))
                    nxt[key] = nxt.get(key, 0) + ways
        states = nxt
    return total


def g_required(r):
    m, n = r.randint(1, 4), r.randint(1, 4)
    if m * n < 2:
        n = 2
    cells = [(a, b) for a in range(m) for b in range(n)]
    r.shuffle(cells)
    g = [[0] * n for _ in range(m)]
    g[cells[0][0]][cells[0][1]] = 1
    g[cells[1][0]][cells[1][1]] = 2
    for a, b in cells[2:]:
        g[a][b] = r.choice((0, 0, 0, 3, -1))
    return [g]


def v_required(tests):
    for t in tests:
        g = t["args"][0]
        _legal_board(g, -1, 3)
        flat = [x for row in g for x in row]
        assert len(flat) <= 25 and flat.count(1) == 1 and flat.count(2) == 1
    assert any(t["expected"] == 0 for t in tests) and any(t["expected"] > 1000 for t in tests)


CHECKS["required-cells-path-count"] = (b_required, g_required, "exact")
VALIDATE["required-cells-path-count"] = v_required

# ---------------------------------------------------------------- word path on a wrap-around grid
p = add(
    id="wraparound-word-path", title="Word Path on a Wrap-Around Grid", diff="Medium", topic=TOPIC, tier="extra",
    fn="wrapWordPathExists", params=[("board", "int[][]"), ("word", "string")], ret="bool", cmp="exact",
    desc="<p>A grid of letters is given as an integer matrix <code>board</code> (<code>1</code> is <code>a</code>, ..., <code>26</code> is <code>z</code>). The grid <strong>wraps around</strong>: stepping off the right edge brings you to the left edge of the same row, stepping off the left edge brings you to the right edge, and the same holds between the top row and the bottom row.</p><p>Decide whether the lowercase string <code>word</code> can be spelled by a path that starts at any cell and moves one step at a time to the cell above, below, left or right (with wrapping). A cell may be used at most once in a path.</p><p>For example, on the single-row board <code>[[1,2,3]]</code> (the letters <code>abc</code>) the word <code>cab</code> can be spelled: after <code>c</code> the path steps right, wraps to <code>a</code>, and then reaches <code>b</code>. On the board with rows <code>abc</code> and <code>def</code> the word <code>cfd</code> can also be spelled, by going down from <code>c</code> to <code>f</code> and then right from <code>f</code>, wrapping to <code>d</code>.</p>",
    constraints=["1 &le; board.length, board[i].length &le; 5", "1 &le; board[i][j] &le; 26", "1 &le; word.length &le; 25", "word contains only lowercase letters"],
    hints=["Start a search from every cell that holds the first letter, and extend letter by letter. The only change compared with an ordinary grid is how neighbours are computed.",
           "Use modular arithmetic for the four neighbours: <code>((r - 1) % m, c)</code>, <code>((r + 1) % m, c)</code>, <code>(r, (c - 1) % n)</code>, <code>(r, (c + 1) % n)</code>. In a grid with 1 or 2 rows (or columns) some of these coincide with each other or with the cell itself, and the visited mark already forbids the cell itself, so it is enough to remove duplicates.",
           "Mark the current cell as used before looking at the neighbours and unmark it afterwards. Cheap pruning: fail at once when the word has more copies of a letter than the board, or when it is longer than <code>m * n</code>; and begin from the end of the word that has the rarer letter on the board."],
    editorial=["The search is the usual word-search backtracking: <code>go(r, c, k)</code> checks that the cell holds the k-th letter, finishes on the last letter, and otherwise tries the unused neighbours with letter <code>k + 1</code>. The wrap-around only changes the neighbour function, which now uses the remainder operator so every cell has four neighbours (fewer distinct ones when a dimension is 1 or 2).",
               "Wrapping does not change the worst case, which is exponential in the word length, but the board has at most 25 cells and the letter-count check and the longer-than-the-board check remove the hopeless words. Reading the word backwards (when its last letter is rarer on the board) reduces the number of starting cells and is a valid trick because a path can be walked in either direction."],
    time="O(m &middot; n &middot; 3<sup>L</sup>)", space="O(L) recursion",
    solution='''def wrapWordPathExists(board, word):
    m, n = len(board), len(board[0])
    codes = [ord(ch) - 96 for ch in word]
    L = len(codes)
    if L > m * n:
        return False
    have, need = {}, {}
    for row in board:
        for x in row:
            have[x] = have.get(x, 0) + 1
    for x in codes:
        need[x] = need.get(x, 0) + 1
    for x, v in need.items():
        if have.get(x, 0) < v:
            return False
    if have[codes[0]] > have[codes[-1]]:
        codes.reverse()
    nbrs = [[sorted({((r - 1) % m, c), ((r + 1) % m, c), (r, (c - 1) % n), (r, (c + 1) % n)} - {(r, c)})
             for c in range(n)] for r in range(m)]
    seen = [[False] * n for _ in range(m)]

    def go(r, c, k):
        if board[r][c] != codes[k]:
            return False
        if k == L - 1:
            return True
        seen[r][c] = True
        found = False
        for nr, nc in nbrs[r][c]:
            if not seen[nr][nc] and go(nr, nc, k + 1):
                found = True
                break
        seen[r][c] = False
        return found

    return any(go(r, c, 0) for r in range(m) for c in range(n) if board[r][c] == codes[0])
''',
    tests=[[_g("abc"), "cab"],
           [_g("abc", "def"), "cfd"],
           [_g("abc", "def"), "afc"],
           [_g("q"), "q"],
           [_g("q"), "qq"],
           [_g("abcde"), "edcba"],
           [_g("abcde"), "aeb"],
           [_g("abcde"), "deabc"],
           [_g("ab", "cd"), "adcb"],
           [_g("ab", "cd"), "abcd"],
           [_g("abc", "bca", "cab"), "aaa"],
           [_g("aaa", "aab", "aaa"), "aaaaaaabaa"]],
)
_r = rnd(1107)


def _torus_walk(r, board, length):
    m, n = len(board), len(board[0])
    cr, cc = r.randrange(m), r.randrange(n)
    seen = {(cr, cc)}
    out = [board[cr][cc]]
    while len(out) < length:
        opts = sorted({((cr - 1) % m, cc), ((cr + 1) % m, cc), (cr, (cc - 1) % n), (cr, (cc + 1) % n)} - seen)
        if not opts:
            break
        cr, cc = r.choice(opts)
        seen.add((cr, cc))
        out.append(board[cr][cc])
    return out


for _k, _len, _tweak in ((2, 25, False), (2, 25, True), (2, 22, True), (3, 20, False), (3, 24, True), (4, 18, True)):
    _b = _rand_board(_r, 5, 5, _k)
    _w = _torus_walk(_r, _b, _len)
    if _tweak:
        _w[_r.randrange(len(_w))] = _r.randint(1, _k)
    p["tests"].append([_b, _str(_w)])


def b_wrap(board, word):
    m, n = len(board), len(board[0])
    codes = [ord(c) - 96 for c in word]
    cur = {(r * n + c, 1 << (r * n + c)) for r in range(m) for c in range(n) if board[r][c] == codes[0]}
    for ch in codes[1:]:
        nxt = set()
        for cell, mask in cur:
            r, c = divmod(cell, n)
            for dr, dc in DIRS4:
                nr, nc = (r + dr) % m, (c + dc) % n
                if board[nr][nc] == ch and not mask >> (nr * n + nc) & 1:
                    nxt.add((nr * n + nc, mask | 1 << (nr * n + nc)))
        cur = nxt
        if not cur:
            return False
    return bool(cur)


def g_wrap(r):
    m, n, k = r.randint(1, 4), r.randint(1, 4), r.randint(1, 3)
    b = _rand_board(r, m, n, k)
    if r.random() < 0.6:
        w = _torus_walk(r, b, r.randint(1, 8))
        if r.random() < 0.4:
            w[r.randrange(len(w))] = r.randint(1, k)
    else:
        w = [r.randint(1, k) for _ in range(r.randint(1, 8))]
    return [b, _str(w)]


def v_wrap(tests):
    for t in tests:
        board, word = t["args"]
        _legal_board(board)
        assert len(board) <= 5 and len(board[0]) <= 5 and 1 <= len(word) <= 25 and word.islower() and word.isalpha()
    assert any(t["expected"] for t in tests) and any(not t["expected"] for t in tests)


CHECKS["wraparound-word-path"] = (b_wrap, g_wrap, "exact")
VALIDATE["wraparound-word-path"] = v_wrap

# ---------------------------------------------------------------- lexicographically first knight tour
p = add(
    id="knight-tour-first-board", title="First Knight's Tour", diff="Medium", topic=TOPIC, tier="extra",
    fn="firstKnightTour", params=[("m", "int"), ("n", "int"), ("startRow", "int"), ("startCol", "int")], ret="int[][]", cmp="exact",
    desc="<p>A knight stands on cell <code>(startRow, startCol)</code> of an <code>m x n</code> board (0-indexed). A knight move changes the position by <code>(+-2, +-1)</code> or <code>(+-1, +-2)</code> and must stay on the board. A <em>tour</em> is a sequence of moves that visits every cell exactly once, starting on the given cell.</p><p>Write each visited cell as the pair <code>(row, col)</code> and compare two tours by their sequences of cells, from the first cell on: at the first position where they differ, the tour with the smaller pair (smaller row first, then smaller column) is the smaller tour. Return the board of the <strong>smallest</strong> tour, where <code>result[r][c]</code> is the step at which cell <code>(r, c)</code> is visited (<code>1</code> for the starting cell, up to <code>m * n</code>). If no tour exists, return an empty array <code>[]</code>.</p><p>For example, for <code>m = 3, n = 4</code> and start <code>(0, 0)</code> the answer is <code>[[1,4,7,10],[8,11,2,5],[3,6,9,12]]</code>: from the corner the knight can go to <code>(1,2)</code> or <code>(2,1)</code>, and <code>(1,2)</code> is smaller.</p>",
    constraints=["1 &le; m, n and m &middot; n &le; 25", "0 &le; startRow &lt; m and 0 &le; startCol &lt; n"],
    hints=["Build the tour one cell at a time, as a DFS over knight moves that never revisits a cell, and undo a move when the rest of the tour cannot be completed.",
           "Trying the next cells in increasing <code>(row, col)</code> order guarantees that the first complete tour you find is the smallest one in the required comparison. Return as soon as the tour is complete; do not look at other tours.",
           "Without pruning the search can be slow on 5 x 5. Keep for every cell the number of unvisited cells a knight could still reach from it. After you move, a neighbour of the new cell whose count dropped to 0 can only be the final cell of the tour: if more than one cell remains, abandon the branch."],
    editorial=["The comparison in the statement is exactly the order in which a depth-first search tries its candidates when the eight knight offsets are listed so that the destination cells come out in increasing <code>(row, col)</code> order. That order is <code>(-2,-1), (-2,+1), (-1,-2), (-1,+2), (+1,-2), (+1,+2), (+2,-1), (+2,+1)</code>. The first time the DFS manages to place all <code>m * n</code> cells, the tour found is the smallest one, because every smaller prefix was tried and failed first.",
               "Plain backtracking explores a huge number of dead ends on boards like 5 x 5. A sound pruning rule keeps the answer unchanged: store the number of unvisited neighbours for each cell. When the knight moves, those counts drop for the neighbours of the new cell. An unvisited cell with no unvisited neighbour left can still be entered right now but can never be left, so it must be the very last cell. If more than one cell remains, no tour exists below this branch. With this rule every board of at most 25 cells is solved well within the time limit. Warnsdorff's heuristic (always go to the neighbour with fewest exits) is faster, but it does not produce the smallest tour, so it cannot be used here."],
    time="exponential in the worst case; fast with pruning", space="O(m &middot; n)",
    solution='''def firstKnightTour(m, n, startRow, startCol):
    offsets = [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)]
    total = m * n
    nbrs = []
    for r in range(m):
        for c in range(n):
            nbrs.append([(r + dr) * n + (c + dc) for dr, dc in offsets
                         if 0 <= r + dr < m and 0 <= c + dc < n])
    free = [len(x) for x in nbrs]           # unvisited neighbours of every cell
    seen = [False] * total
    order = []

    def go(cell, left):
        order.append(cell)
        seen[cell] = True
        if left == 0:
            return True
        for v in nbrs[cell]:
            free[v] -= 1
        found = False
        viable = True
        if left > 1:
            for v in nbrs[cell]:
                if not seen[v] and free[v] == 0:
                    viable = False
                    break
        if viable:
            for v in nbrs[cell]:
                if not seen[v] and go(v, left - 1):
                    found = True
                    break
        for v in nbrs[cell]:
            free[v] += 1
        if not found:
            seen[cell] = False
            order.pop()
        return found

    if not go(startRow * n + startCol, total - 1):
        return []
    board = [[0] * n for _ in range(m)]
    for step, cell in enumerate(order):
        board[cell // n][cell % n] = step + 1
    return board
''',
    tests=[[3, 4, 0, 0],
           [3, 3, 0, 0],
           [1, 1, 0, 0],
           [3, 4, 2, 0],
           [3, 4, 1, 1],
           [1, 5, 0, 2],
           [2, 2, 1, 1],
           [4, 4, 0, 0],
           [3, 5, 1, 2],
           [4, 5, 0, 0],
           [4, 5, 3, 4],
           [3, 8, 0, 0],
           [5, 5, 0, 0],
           [5, 5, 2, 2],
           [5, 5, 0, 1]],
)


def b_knight_first(m, n, sr, sc):
    # memoised depth-first search over (cell, visited set), same candidate order
    total = m * n
    offs = sorted(KNIGHT)
    dead = set()
    path = []

    def go(r, c, mask):
        path.append((r, c))
        mask |= 1 << (r * n + c)
        if len(path) == total:
            return True
        key = (r * n + c, mask)
        if key not in dead:
            for dr, dc in offs:
                nr, nc = r + dr, c + dc
                if 0 <= nr < m and 0 <= nc < n and not mask >> (nr * n + nc) & 1 and go(nr, nc, mask):
                    return True
            dead.add(key)
        path.pop()
        return False

    if not go(sr, sc, 0):
        return []
    board = [[0] * n for _ in range(m)]
    for i, (r, c) in enumerate(path):
        board[r][c] = i + 1
    return board


def g_knight_first(r):
    m, n = r.choice(((3, 4), (4, 3), (3, 3), (4, 4), (3, 5), (5, 3), (1, 4), (2, 5), (4, 5), (5, 4), (3, 6), (1, 1), (2, 2)))
    return [m, n, r.randrange(m), r.randrange(n)]


def v_knight_first(tests):
    for t in tests:
        m, n, sr, sc = t["args"]
        assert 1 <= m and 1 <= n and m * n <= 25 and 0 <= sr < m and 0 <= sc < n
        b = t["expected"]
        if b:
            pos = {b[r][c]: (r, c) for r in range(m) for c in range(n)}
            assert sorted(pos) == list(range(1, m * n + 1)) and pos[1] == (sr, sc)
            for k in range(1, m * n):
                assert sorted((abs(pos[k][0] - pos[k + 1][0]), abs(pos[k][1] - pos[k + 1][1]))) == [1, 2]
    assert any(t["expected"] == [] for t in tests) and any(t["expected"] for t in tests)


CHECKS["knight-tour-first-board"] = (b_knight_first, g_knight_first, "exact")
VALIDATE["knight-tour-first-board"] = v_knight_first


# ================================================================== HARD

# ---------------------------------------------------------------- find all words in a grid
p = add(
    id="grid-words-found-indices", title="Find All Dictionary Words in a Grid", diff="Hard", topic=TOPIC, tier="must",
    fn="wordsFoundInGrid", params=[("board", "int[][]"), ("words", "int[][]")], ret="int[]", cmp="exact",
    desc="<p>A grid of letters is given as an integer matrix <code>board</code>, and a dictionary as a list <code>words</code> in which every word is itself an array of letter codes. In both, <code>1</code> stands for <code>a</code>, <code>2</code> for <code>b</code>, and so on up to <code>26</code> for <code>z</code>.</p><p>A word is <em>found</em> if its letters can be read along a path that starts at any cell and moves one step at a time to the cell directly above, below, left or right, without using any cell twice in the same path. Return the indices (0-based) of all found words, in increasing order. The words in the dictionary are all different, and each word is checked independently of the others.</p><p>For example, for the board with rows <code>cat</code>, <code>oer</code>, <code>dgs</code> and the words <code>cat</code>, <code>tag</code>, <code>cod</code>, <code>reg</code>, <code>coat</code> the answer is <code>[0, 2, 3]</code>.</p>",
    constraints=["1 &le; board.length, board[i].length &le; 10", "1 &le; words.length &le; 100 and all words are different", "1 &le; words[i].length &le; 10", "1 &le; board[i][j], words[i][k] &le; 26"],
    hints=["Searching the grid once for every word works for a few words, but repeats a lot of work: words that start with the same letters walk the same paths.",
           "Store all words in a trie (a tree keyed by letter codes). Start a DFS from every cell and descend the trie in step with the path, so one walk serves every word with the same prefix. A branch stops as soon as the next letter has no child in the trie.",
           "Mark the end of each word in the trie with its index. When the DFS reaches such a node, record the index and clear the marker so that the word is reported once. Optionally delete trie nodes that have become empty, which makes the search faster as words are found."],
    editorial=["Build a trie of the dictionary; each word-ending node remembers the index of its word. For each cell run <code>dfs(r, c, node)</code>: look up the cell's letter among the children of <code>node</code>, stop if it is missing, report the word index if the child ends a word, then mark the cell visited and recurse into the four neighbours with the child as the new trie node. Unmark the cell when returning (backtracking).",
               "This beats running a single-word search for each word, because all words with a common prefix share the walk along that prefix, and a path that cannot be a prefix of any word is cut at once. Pruning the trie (removing a child once its subtree holds no unreported words) shrinks the search as more words are found. The cost is bounded by the number of self-avoiding paths that follow a trie path, at most <code>m * n * 3<sup>L-1</sup></code>, but realistic inputs are far smaller."],
    time="O(m &middot; n &middot; 3<sup>L</sup>) worst case", space="O(total letters in words)",
    solution='''def wordsFoundInGrid(board, words):
    m, n = len(board), len(board[0])
    root = {}
    for idx, w in enumerate(words):
        node = root
        for ch in w:
            node = node.setdefault(ch, {})
        node[0] = idx                       # key 0 can never be a letter: it marks the end of a word
    found = []

    def dfs(r, c, parent):
        ch = board[r][c]
        node = parent.get(ch)
        if node is None:
            return
        if 0 in node:
            found.append(node.pop(0))
        board[r][c] = 0                     # visited
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nr, nc = r + dr, c + dc
            if 0 <= nr < m and 0 <= nc < n and board[nr][nc] != 0:
                dfs(nr, nc, node)
        board[r][c] = ch
        if not node:                        # nothing left to find below this node
            del parent[ch]

    for r in range(m):
        for c in range(n):
            dfs(r, c, root)
    found.sort()
    return found
''',
    tests=[[_g("cat", "oer", "dgs"), _ws("cat", "tag", "cod", "reg", "coat")],
           [_g("a"), _ws("a", "b", "aa")],
           [_g("ab", "cd"), _ws("abdc", "acdb", "abcd", "adbc")],
           [_g("abc"), _ws("abc", "cba", "ac", "b", "bca")],
           [_g("aaa", "aaa", "aaa"), _ws("a", "aa", "aaaaaaaaa", "aaaaaaaaaa", "ab")],
           [_g("oaan", "etae", "ihkr", "iflv"), _ws("oath", "pea", "eat", "rain", "oate", "eatk", "kate")],
           [_g("abcd", "efgh", "ijkl", "mnop"), _ws("afkp", "abcdhgfe", "aeim", "ponm", "afk", "fgh", "agf", "dhlp")],
           [_g("xyz", "zyx"), _ws("xyzzyx", "xyx", "zyz", "xzy")],
           [_g("ab", "cd"), _ws("ad", "bc", "da")],
           [_g("ab", "ba"), _ws("ab", "ba", "aa", "bb", "aba", "bab", "abab", "baba", "abba")]],
)
_r = rnd(1109)


def _words_case(r, m, n, k, planted, noise, lo=3, hi=10):
    board = _rand_board(r, m, n, k)
    words = set()
    while len(words) < planted:
        w = _walk(r, board, r.randint(lo, hi))
        if len(w) >= lo:
            words.add(tuple(w))
    while len(words) < planted + noise:
        words.add(tuple(r.randint(1, k) for _ in range(r.randint(lo, hi - 2))))
    words = [list(w) for w in words]
    r.shuffle(words)
    return [board, words]


p["tests"].append(_words_case(_r, 6, 6, 3, 14, 10))
p["tests"].append(_words_case(_r, 8, 8, 4, 30, 30))
p["tests"].append(_words_case(_r, 10, 10, 5, 40, 40))
p["tests"].append(_words_case(_r, 10, 8, 26, 12, 20, 2, 6))
p["tests"].append([[[1] * 6 for _ in range(6)], [[1] * k for k in range(1, 11)]])


def b_words(board, words):
    m, n = len(board), len(board[0])
    out = []
    for idx, w in enumerate(words):
        cur = {(r * n + c, 1 << (r * n + c)) for r in range(m) for c in range(n) if board[r][c] == w[0]}
        for ch in w[1:]:
            nxt = set()
            for cell, mask in cur:
                r, c = divmod(cell, n)
                for dr, dc in DIRS4:
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < m and 0 <= nc < n and board[nr][nc] == ch and not mask >> (nr * n + nc) & 1:
                        nxt.add((nr * n + nc, mask | 1 << (nr * n + nc)))
            cur = nxt
            if not cur:
                break
        if cur:
            out.append(idx)
    return out


def g_words(r):
    m, n, k = r.randint(1, 4), r.randint(1, 4), r.randint(1, 3)
    board = _rand_board(r, m, n, k)
    words = set()
    for _ in range(r.randint(1, 7)):
        if r.random() < 0.5:
            words.add(tuple(_walk(r, board, r.randint(1, 6))))
        else:
            words.add(tuple(r.randint(1, k) for _ in range(r.randint(1, 6))))
    return [board, [list(w) for w in words]]


def v_words(tests):
    for t in tests:
        board, words = t["args"]
        _legal_board(board)
        assert len(board) <= 10 and len(board[0]) <= 10
        assert 1 <= len(words) <= 100 and len({tuple(w) for w in words}) == len(words)
        assert all(1 <= len(w) <= 10 and all(1 <= x <= 26 for x in w) for w in words)
    assert any(t["expected"] == [] for t in tests) and any(len(t["expected"]) >= 20 for t in tests)


CHECKS["grid-words-found-indices"] = (b_words, g_words, "exact")
VALIDATE["grid-words-found-indices"] = v_words

# ---------------------------------------------------------------- word squares
p = add(
    id="word-squares-count", title="Count the Word Squares", diff="Hard", topic=TOPIC, tier="extra",
    fn="countWordSquares", params=[("words", "int[][]")], ret="int", cmp="exact",
    desc="<p>You are given a list <code>words</code> of different words, all of the same length <code>L</code>. Every word is an array of letter codes (<code>1</code> is <code>a</code>, ..., <code>26</code> is <code>z</code>).</p><p>A <em>word square</em> is a sequence of <code>L</code> words <code>w<sub>0</sub>, w<sub>1</sub>, ..., w<sub>L-1</sub></code> taken from the list (the same word may be used several times) such that, written as the rows of an <code>L x L</code> grid, row <code>k</code> and column <code>k</code> read the same word for every <code>k</code>. In other words <code>w<sub>i</sub>[j] = w<sub>j</sub>[i]</code> for all <code>i, j</code>.</p><p>Return the number of word squares. Different sequences count as different squares, even if they hold the same words in another order. It is guaranteed that the answer fits in a 32-bit signed integer.</p><p>For example, for the words <code>ab, ba, aa</code> there are 5 squares: <code>(ab, ba)</code>, <code>(ba, ab)</code>, <code>(ba, aa)</code>, <code>(aa, ab)</code> and <code>(aa, aa)</code>.</p>",
    constraints=["1 &le; words.length &le; 1,000", "1 &le; L &le; 5, all words have the same length L and are pairwise different", "1 &le; words[i][k] &le; 26", "The answer is at most 2<sup>31</sup> - 1 and the tests keep it small enough to enumerate"],
    hints=["Fill the square one row at a time. How much freedom does row <code>k</code> have once rows <code>0..k-1</code> are fixed?",
           "Column <code>k</code> must equal row <code>k</code>. The first <code>k</code> letters of row <code>k</code> are therefore already known: they are the letters at position <code>k</code> of the earlier rows. Row <code>k</code> must be a word that starts with that prefix.",
           "Precompute a map from every prefix (as a tuple of codes, including the empty prefix) to the list of words that begin with it. The DFS asks the map for the candidates of the next row, recurses, and adds up the results."],
    editorial=["After choosing rows <code>0..k-1</code> the prefix of row <code>k</code> is forced: its <code>j</code>-th letter must equal letter <code>k</code> of row <code>j</code>. So the choice of row <code>k</code> is limited to the words with that prefix. A dictionary from prefix tuples to word lists (or a trie that stores a list at every node) gives these candidates instantly, and the DFS never builds a row that already contradicts the earlier ones.",
               "The count is the number of leaves of this search tree, and the work is proportional to the number of partial squares that can still be extended by looking at one row. Without the prefix map, scanning the whole list for each row would multiply the cost by the number of words. Memory is O(number of words &middot; L) for the map."],
    time="O(number of partial squares)", space="O(words &middot; L)",
    solution='''def countWordSquares(words):
    L = len(words[0])
    by_prefix = {}
    for w in words:
        for k in range(L):
            by_prefix.setdefault(tuple(w[:k]), []).append(w)
    rows = []

    def go():
        k = len(rows)
        if k == L:
            return 1
        prefix = tuple(rows[i][k] for i in range(k))
        total = 0
        for w in by_prefix.get(prefix, ()):
            rows.append(w)
            total += go()
            rows.pop()
        return total

    return go()
''',
    tests=[[_ws("ab", "ba", "aa")],
           [_ws("area", "lead", "wall", "lady", "ball")],
           [_ws("a", "b", "c")],
           [_ws("abc")],
           [_ws("aaa")],
           [_ws("aa")],
           [_ws("ab", "ba")],
           [_ws("abc", "bca", "cab")],
           [_ws("abcd", "bcda", "cdab", "dabc", "aaaa")],
           [_ws("aab", "aba", "baa", "bbb", "aaa", "abb")]],
)
_r = rnd(1110)


def _symmetric_words(r, L, k, copies):
    out = set()
    for _ in range(copies):
        g = [[0] * L for _ in range(L)]
        for i in range(L):
            for j in range(i, L):
                g[i][j] = g[j][i] = r.randint(1, k)
        out.update(tuple(row) for row in g)
    return out


def _squares_case(r, L, k, size, planted=0):
    allw = set(_symmetric_words(r, L, k, planted))
    while len(allw) < size:
        allw.add(tuple(r.randint(1, k) for _ in range(L)))
    allw = [list(w) for w in allw]
    r.shuffle(allw)
    return [allw[:size] if planted == 0 else allw]


p["tests"].append(_squares_case(_r, 4, 4, 60))
p["tests"].append(_squares_case(_r, 5, 3, 40))
p["tests"].append(_squares_case(_r, 3, 6, 100))
p["tests"].append(_squares_case(_r, 4, 26, 1000, planted=40))
p["tests"].append(_squares_case(_r, 3, 26, 800, planted=60))


def b_squares(words):
    L = len(words[0])
    cnt = 0
    for rows in _product(words, repeat=L):
        if all(rows[i][j] == rows[j][i] for i in range(L) for j in range(i + 1, L)):
            cnt += 1
    return cnt


def g_squares(r):
    L = r.randint(1, 4)
    k = r.randint(1, 3)
    allw = list(_product(range(1, k + 1), repeat=L))
    cnt = r.randint(1, min(len(allw), 6 if L < 4 else 4))
    return [[list(w) for w in r.sample(allw, cnt)]]


def v_squares(tests):
    for t in tests:
        words = t["args"][0]
        L = len(words[0])
        assert 1 <= len(words) <= 1000 and 1 <= L <= 5 and len({tuple(w) for w in words}) == len(words)
        assert all(len(w) == L and all(1 <= x <= 26 for x in w) for w in words)
        assert t["expected"] <= 2 ** 31 - 1
    assert any(t["expected"] == 0 for t in tests) and any(t["expected"] > 500 for t in tests)


CHECKS["word-squares-count"] = (b_squares, g_squares, "exact")
VALIDATE["word-squares-count"] = v_squares

# ---------------------------------------------------------------- knight tour count
p = add(
    id="knight-tour-count", title="Count the Knight's Tours", diff="Hard", topic=TOPIC, tier="extra",
    fn="countKnightTours", params=[("m", "int"), ("n", "int"), ("startRow", "int"), ("startCol", "int")], ret="int", cmp="exact",
    desc="<p>A knight stands on cell <code>(startRow, startCol)</code> of an <code>m x n</code> board (0-indexed). A knight move changes the position by <code>(+-2, +-1)</code> or <code>(+-1, +-2)</code> and must stay on the board. A <em>tour</em> is a sequence of moves that starts on the given cell and visits every cell of the board exactly once; it does not have to return to the start.</p><p>Return the number of different tours. Two tours are different when they visit the cells in a different order.</p><p>For example, on a <code>3 x 4</code> board the knight has 2 tours from the cell <code>(2, 0)</code>, on a <code>5 x 5</code> board it has 304 tours from the corner <code>(0, 0)</code>, and on a <code>3 x 3</code> board it has none (the middle cell can never be visited).</p>",
    constraints=["1 &le; m, n and m &middot; n &le; 25", "0 &le; startRow &lt; m and 0 &le; startCol &lt; n"],
    hints=["Count with backtracking: from the current cell try each of up to 8 knight moves to an unvisited cell, recurse, and add up the number of completed tours. A tour is complete when all <code>m * n</code> cells are used.",
           "Keep the visited cells as a bitmask and precompute, for every cell, the list of cells a knight can jump to (and the same list as a bitmask).",
           "Prune with dead ends: after a move, if an unvisited neighbour of the new cell has no unvisited neighbour of its own, it can only be the last cell of the tour, so if more than one cell is still unvisited, return 0 immediately."],
    editorial=["A depth-first search with a visited bitmask enumerates every sequence of knight moves that never repeats a cell and counts those of full length. The branching factor of a knight is at most 8, but only about 2 to 3 moves are available on average, and there are strong constraints: corner cells have only two neighbours, so the tour must pass through them in a very specific way.",
               "The dead-end rule makes the search practical for boards up to 25 cells: after stepping to a cell, look at the unvisited cells it attacks; one of them having no unvisited neighbour means it can be entered only from here and never left, so it must be the final cell. If there are still two or more cells to visit the whole branch is dead. The same test would also detect two such cells. With the rule, the worst start on a 5 x 5 board needs about 10<sup>5</sup> calls. Bit tricks keep the inner loop short: <code>not (nbmask[v] &amp; ~mask)</code> means that <code>v</code> has no unvisited neighbour."],
    time="exponential, practical for m &middot; n &le; 25", space="O(m &middot; n)",
    solution='''def countKnightTours(m, n, startRow, startCol):
    offsets = [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)]
    nbrs = []
    for r in range(m):
        for c in range(n):
            nbrs.append([(r + dr) * n + (c + dc) for dr, dc in offsets
                         if 0 <= r + dr < m and 0 <= c + dc < n])
    nbmask = [sum(1 << v for v in lst) for lst in nbrs]

    def go(cell, mask, left):
        if left == 0:
            return 1
        if left > 1:
            for v in nbrs[cell]:
                if not mask >> v & 1 and not nbmask[v] & ~mask:
                    return 0               # v could only be the last cell, but more cells remain
        total = 0
        for v in nbrs[cell]:
            if not mask >> v & 1:
                total += go(v, mask | 1 << v, left - 1)
        return total

    start = startRow * n + startCol
    return go(start, 1 << start, m * n - 1)
''',
    tests=[[3, 4, 2, 0],
           [3, 3, 0, 0],
           [5, 5, 0, 0],
           [1, 1, 0, 0],
           [1, 3, 0, 0],
           [2, 2, 0, 1],
           [3, 4, 1, 1],
           [3, 4, 0, 0],
           [4, 4, 0, 0],
           [4, 5, 0, 0],
           [4, 5, 2, 3],
           [3, 7, 1, 3],
           [3, 8, 0, 0],
           [5, 5, 2, 2],
           [5, 5, 0, 1],
           [4, 6, 0, 5]],
)


def b_knight_count(m, n, sr, sc):
    total = m * n
    seen = [[False] * n for _ in range(m)]

    def go(r, c, k):
        if k == total:
            return 1
        seen[r][c] = True
        cnt = 0
        for dr, dc in KNIGHT:
            nr, nc = r + dr, c + dc
            if 0 <= nr < m and 0 <= nc < n and not seen[nr][nc]:
                cnt += go(nr, nc, k + 1)
        seen[r][c] = False
        return cnt

    return go(sr, sc, 1)


def g_knight_count(r):
    m, n = r.choice(((3, 4), (4, 3), (3, 3), (4, 4), (3, 5), (5, 3), (1, 4), (2, 5), (3, 6), (6, 3), (4, 5), (5, 4), (1, 1), (2, 2), (3, 4), (4, 3)))
    return [m, n, r.randrange(m), r.randrange(n)]


def v_knight_count(tests):
    for t in tests:
        m, n, sr, sc = t["args"]
        assert 1 <= m and 1 <= n and m * n <= 25 and 0 <= sr < m and 0 <= sc < n
    assert any(t["expected"] == 0 for t in tests) and any(t["expected"] >= 300 for t in tests)
    assert any(0 < t["expected"] < 10 for t in tests)


CHECKS["knight-tour-count"] = (b_knight_count, g_knight_count, "exact")
VALIDATE["knight-tour-count"] = v_knight_count
