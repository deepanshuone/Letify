"""Problems: grid BFS shortest paths (steps between cells, exits, knight, ladders, wall breaks, keys, snake, portals, queen, timed gates). See data/lib.py for the registry."""
from lib import add, rnd, CHECKS, VALIDATE, gen_arr  # noqa: F401

DIRS4 = ((1, 0), (-1, 0), (0, 1), (0, -1))
DIRS8 = ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1))


# ------------------------------------------------------------------ helpers used only to build tests and checks
def _fn(p):
    ns = {}
    exec(p["solution"], ns)
    return ns[p["fn"]]


def _grid(r, R, C, prob, vals=(0, 1), clear=()):
    """Random grid; each cell is vals[1] with probability prob, else vals[0]; cells in `clear` are forced to vals[0]."""
    g = [[vals[1] if r.random() < prob else vals[0] for _ in range(C)] for _ in range(R)]
    for (i, j) in clear:
        g[i][j] = vals[0]
    return g


def _until(p, mk, ok):
    """Draw random test inputs until the reference answer satisfies ok(answer)."""
    f = _fn(p)
    while True:
        a = mk()
        if ok(f(*a)):
            return a


def _bf(nodes, nbrs, src):
    """Bellman-Ford style sweeps with unit edge costs (brute force reference for BFS problems)."""
    dist = {src: 0}
    changed = True
    while changed:
        changed = False
        for u in nodes:
            if u in dist:
                for v in nbrs(u):
                    if v not in dist or dist[v] > dist[u] + 1:
                        dist[v] = dist[u] + 1
                        changed = True
    return dist


def _rect(g, rmax, cmax, allowed=None):
    assert 1 <= len(g) <= rmax, "rows"
    assert all(len(row) == len(g[0]) for row in g), "ragged"
    assert 1 <= len(g[0]) <= cmax, "cols"
    if allowed is not None:
        for row in g:
            for v in row:
                assert v in allowed, ("cell value", v)


# =================================================================== EASY
# ---------------------------------------------------------------- minimum steps between two cells
p = add(
    id="minimum-steps-between-cells", title="Minimum Steps Between Two Cells", diff="Easy", topic="Graphs", tier="must",
    fn="minSteps", params=[("grid", "int[][]"), ("sr", "int"), ("sc", "int"), ("tr", "int"), ("tc", "int")], ret="int", cmp="exact",
    desc="<p>A <code>grid</code> contains <code>0</code> for an open cell and <code>1</code> for a wall. In one step you may move from a cell to the cell directly above, below, left or right of it, as long as that cell is inside the grid and open.</p><p>Return the minimum number of steps needed to get from the open cell <code>(sr, sc)</code> to the open cell <code>(tr, tc)</code>, or <code>-1</code> if the target cannot be reached. If both cells are the same, the answer is <code>0</code>.</p><pre>grid = [[0,0,0],\n        [1,1,0],\n        [0,0,0]],  start = (0,0), target = (2,0)\n\nresult = 6      (right, right, down, down, left, left)</pre>",
    constraints=["1 &le; rows, cols &le; 60", "grid[r][c] is 0 or 1", "The start cell and the target cell are both open (0) and lie inside the grid"],
    hints=["Every step costs the same. Which traversal finds the fewest steps in an unweighted graph?",
           "Use breadth-first search from the start cell: a queue, and a distance for every cell you have reached.",
           "Mark a cell as seen when you put it in the queue, store its distance as the distance of the cell you came from plus one, and stop as soon as the target is taken from the queue. If the queue becomes empty first, return -1."],
    editorial=["Treat every open cell as a node connected to its open neighbours. Because all moves cost one step, breadth-first search reaches cells in increasing order of distance, so the first time the target is reached its distance is the minimum.",
               "Keep a <code>dist</code> table filled with -1. Set the start to 0 and push it. For each cell taken from the queue, look at its four neighbours; every neighbour that is inside the grid, open and still at -1 gets <code>dist + 1</code> and is pushed. Marking on push means each cell enters the queue only once.",
               "The running time is O(rows &times; cols) and so is the memory. A depth-first search would also visit every cell but gives no guarantee about the shortest route, which is why BFS is the right tool here."],
    time="O(R &middot; C)", space="O(R &middot; C)",
    solution='''from collections import deque


def minSteps(grid, sr, sc, tr, tc):
    rows, cols = len(grid), len(grid[0])
    dist = [[-1] * cols for _ in range(rows)]
    dist[sr][sc] = 0
    q = deque([(sr, sc)])
    while q:
        r, c = q.popleft()
        if r == tr and c == tc:
            return dist[r][c]
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] == 0 and dist[nr][nc] == -1:
                dist[nr][nc] = dist[r][c] + 1
                q.append((nr, nc))
    return -1
''',
    tests=[[[[0, 0, 0], [1, 1, 0], [0, 0, 0]], 0, 0, 2, 0], [[[0]], 0, 0, 0, 0], [[[0, 1], [1, 0]], 0, 0, 1, 1],
           [[[0, 0, 0, 0]], 0, 0, 0, 3], [[[0, 0, 0], [0, 0, 0], [0, 0, 0]], 0, 0, 2, 2],
           [[[0, 0, 0], [0, 1, 0], [0, 0, 0]], 1, 0, 1, 2], [[[0, 1, 0, 0], [0, 1, 0, 1], [0, 0, 0, 1], [1, 1, 0, 0]], 0, 0, 0, 2],
           [[[0], [0], [1], [0]], 0, 0, 3, 0], [[[0, 0], [0, 0]], 1, 1, 1, 1], [[[0, 1, 0], [0, 1, 0], [0, 1, 0]], 0, 0, 0, 2]],
)
_r = rnd(8101)
p["tests"].append(_until(p, lambda: [_grid(_r, 60, 60, 0.28, clear=[(0, 0), (59, 59)]), 0, 0, 59, 59], lambda v: v > 0))
_s = [[0] * 59 for _ in range(59)]
for _i in range(1, 59, 2):
    _s[_i] = [1] * 59
    _s[_i][58 if (_i // 2) % 2 == 0 else 0] = 0
p["tests"].append([_s, 0, 0, 58, 58])
p["tests"].append(_until(p, lambda: [_grid(_r, 60, 60, 0.4, clear=[(10, 50), (55, 3)]), 10, 50, 55, 3], lambda v: v > 0))
p["tests"].append(_until(p, lambda: [_grid(_r, 60, 60, 0.5, clear=[(30, 5), (31, 54)]), 30, 5, 31, 54], lambda v: v == -1))


def b_steps(grid, sr, sc, tr, tc):
    R, C = len(grid), len(grid[0])
    nodes = [(i, j) for i in range(R) for j in range(C) if grid[i][j] == 0]
    nb = lambda u: [(u[0] + a, u[1] + b) for a, b in DIRS4 if 0 <= u[0] + a < R and 0 <= u[1] + b < C and grid[u[0] + a][u[1] + b] == 0]
    return _bf(nodes, nb, (sr, sc)).get((tr, tc), -1)


def g_steps(r):
    R, C = r.randint(1, 6), r.randint(1, 6)
    g = _grid(r, R, C, r.choice([0.2, 0.4, 0.55]))
    s = (r.randrange(R), r.randrange(C))
    t = (r.randrange(R), r.randrange(C))
    g[s[0]][s[1]] = 0
    g[t[0]][t[1]] = 0
    return [g, s[0], s[1], t[0], t[1]]


def v_steps(tests):
    for t in tests:
        g, sr, sc, tr, tc = t["args"]
        _rect(g, 60, 60, (0, 1))
        assert 0 <= sr < len(g) and 0 <= tr < len(g) and 0 <= sc < len(g[0]) and 0 <= tc < len(g[0])
        assert g[sr][sc] == 0 and g[tr][tc] == 0


CHECKS["minimum-steps-between-cells"] = (b_steps, g_steps, "exact")
VALIDATE["minimum-steps-between-cells"] = v_steps

# ---------------------------------------------------------------- nearest border exit
p = add(
    id="nearest-border-exit", title="Nearest Border Exit", diff="Easy", topic="Graphs",
    fn="nearestExit", params=[("maze", "int[][]"), ("er", "int"), ("ec", "int")], ret="int", cmp="exact",
    desc="<p>A <code>maze</code> is a grid where <code>0</code> is an open cell and <code>1</code> is a wall. You stand at the open cell <code>(er, ec)</code>, the <em>entrance</em>. In one step you move to an open cell directly above, below, left or right.</p><p>An <em>exit</em> is any open cell on the border of the grid (first or last row, first or last column) <strong>other than the entrance itself</strong>. Return the number of steps to the nearest exit, or <code>-1</code> if no exit can be reached.</p><pre>maze = [[1,1,0,1],\n        [0,0,0,1],\n        [1,1,1,1]],  entrance = (1,0)\n\nresult = 3      ((1,0) -> (1,1) -> (1,2) -> (0,2))</pre>",
    constraints=["1 &le; rows, cols &le; 60", "maze[r][c] is 0 or 1", "The entrance is an open cell inside the grid; it may or may not lie on the border"],
    hints=["Several exits may exist; you want the closest one, in number of steps.",
           "A breadth-first search from the entrance visits cells in order of distance, so the first exit you meet is the closest.",
           "When you take a cell from the queue, check whether it is on the border and is not the entrance. Be careful not to count the entrance itself, even if it sits on the border."],
    editorial=["Run BFS from the entrance. All cells at distance 1 are processed before any cell at distance 2, and so on. So the first cell taken from the queue that is a border cell different from the entrance is a nearest exit, and its distance is the answer.",
               "The only trap is the entrance: it is often on the border, but standing there does not count as leaving. Skip it explicitly (it is the only cell with distance 0). If the queue empties without finding an exit, return -1.",
               "Time and memory are O(rows &times; cols)."],
    time="O(R &middot; C)", space="O(R &middot; C)",
    solution='''from collections import deque


def nearestExit(maze, er, ec):
    rows, cols = len(maze), len(maze[0])
    dist = [[-1] * cols for _ in range(rows)]
    dist[er][ec] = 0
    q = deque([(er, ec)])
    while q:
        r, c = q.popleft()
        if (r, c) != (er, ec) and (r in (0, rows - 1) or c in (0, cols - 1)):
            return dist[r][c]
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols and maze[nr][nc] == 0 and dist[nr][nc] == -1:
                dist[nr][nc] = dist[r][c] + 1
                q.append((nr, nc))
    return -1
''',
    tests=[[[[1, 1, 0, 1], [0, 0, 0, 1], [1, 1, 1, 1]], 1, 0], [[[0]], 0, 0], [[[0, 0]], 0, 0],
           [[[1, 1, 1], [1, 0, 1], [1, 1, 1]], 1, 1], [[[1, 1, 1], [1, 0, 0], [1, 1, 1]], 1, 1],
           [[[0, 1, 1, 1], [0, 0, 0, 1], [1, 1, 0, 1], [1, 1, 1, 1]], 2, 2],
           [[[1, 1, 1, 1, 1], [1, 0, 0, 0, 1], [1, 0, 1, 0, 1], [1, 0, 0, 0, 0], [1, 1, 1, 1, 1]], 1, 1],
           [[[0, 1, 0], [0, 0, 0], [0, 1, 0]], 1, 1], [[[1, 0, 1], [1, 0, 1], [1, 0, 1]], 0, 1],
           [[[1, 1, 1, 1], [1, 0, 0, 1], [1, 1, 0, 1], [1, 1, 1, 1]], 1, 1]],
)
_r = rnd(8102)
p["tests"].append(_until(p, lambda: [_grid(_r, 60, 60, 0.3, clear=[(30, 30)]), 30, 30], lambda v: v > 0))
_m = _grid(_r, 60, 60, 0.3, clear=[(30, 30), (0, 30)])
for _i in range(60):
    for _j in range(60):
        if (_i in (0, 59) or _j in (0, 59)) and (_i, _j) != (0, 30):
            _m[_i][_j] = 1
p["tests"].append([_m, 0, 30])
_m = [[1] * 59 for _ in range(59)]
for _i in range(1, 58, 2):  # a long winding corridor inside a wall frame; the only exit is the far border cell (57, 58)
    for _j in range(1, 58):
        _m[_i][_j] = 0
for _i in range(2, 57, 2):
    _m[_i][57 if (_i // 2) % 2 == 1 else 1] = 0
_m[57][58] = 0
p["tests"].append([_m, 1, 1])
p["tests"].append(_until(p, lambda: [_grid(_r, 60, 60, 0.38, clear=[(17, 41)]), 17, 41], lambda v: v > 30))


def b_exit(maze, er, ec):
    R, C = len(maze), len(maze[0])
    nodes = [(i, j) for i in range(R) for j in range(C) if maze[i][j] == 0]
    nb = lambda u: [(u[0] + a, u[1] + b) for a, b in DIRS4 if 0 <= u[0] + a < R and 0 <= u[1] + b < C and maze[u[0] + a][u[1] + b] == 0]
    d = _bf(nodes, nb, (er, ec))
    ex = [v for (i, j), v in d.items() if (i, j) != (er, ec) and (i in (0, R - 1) or j in (0, C - 1))]
    return min(ex) if ex else -1


def g_exit(r):
    R, C = r.randint(1, 6), r.randint(1, 6)
    g = _grid(r, R, C, r.choice([0.3, 0.5, 0.65]))
    e = (r.randrange(R), r.randrange(C))
    g[e[0]][e[1]] = 0
    return [g, e[0], e[1]]


def v_exit(tests):
    for t in tests:
        g, er, ec = t["args"]
        _rect(g, 60, 60, (0, 1))
        assert 0 <= er < len(g) and 0 <= ec < len(g[0]) and g[er][ec] == 0


CHECKS["nearest-border-exit"] = (b_exit, g_exit, "exact")
VALIDATE["nearest-border-exit"] = v_exit

# ---------------------------------------------------------------- cells within k steps
p = add(
    id="cells-within-k-steps", title="Cells Within K Steps", diff="Easy", topic="Graphs", tier="extra",
    fn="countWithinSteps", params=[("grid", "int[][]"), ("sr", "int"), ("sc", "int"), ("k", "int")], ret="int", cmp="exact",
    desc="<p>In a <code>grid</code> of <code>0</code> (open) and <code>1</code> (wall) cells, you start on the open cell <code>(sr, sc)</code> and may move up, down, left or right onto open cells, one step at a time.</p><p>Count the open cells (the start cell included) that can be reached in <strong>at most</strong> <code>k</code> steps, that is, whose shortest walking distance from the start is <code>&le; k</code>.</p><pre>grid = [[0,0,1],\n        [1,0,0],\n        [0,0,0]],  start = (0,0)\n\nk = 2  ->  3     ((0,0), (0,1), (1,1))\nk = 3  ->  5     ((1,2) and (2,1) join)</pre>",
    constraints=["1 &le; rows, cols &le; 60", "grid[r][c] is 0 or 1", "The start cell is open and inside the grid", "0 &le; k &le; 5,000"],
    hints=["A cell counts only if its shortest distance from the start is at most k, so you need shortest distances.",
           "BFS gives the distance of every reachable cell. Stop expanding once you have processed all cells at distance k.",
           "Process the search level by level: keep a counter of the cells seen so far and run the loop for at most k levels, adding the size of each new level to the count."],
    editorial=["BFS explores the grid in layers: layer 0 is the start, layer 1 holds the cells one step away, and so on. A cell belongs to layer <code>d</code> exactly when its shortest distance is <code>d</code>. We want the total size of layers 0 to k.",
               "Keep a visited table and a list for the current layer. Repeat up to k times: build the next layer from unvisited open neighbours of the current layer, mark them visited, add their number to the answer, and stop early if the layer is empty. Since k can be larger than the grid, the early exit matters; the loop never runs more than rows &times; cols times in practice.",
               "Every cell is added at most once, so the running time is O(rows &times; cols)."],
    time="O(R &middot; C)", space="O(R &middot; C)",
    solution='''def countWithinSteps(grid, sr, sc, k):
    rows, cols = len(grid), len(grid[0])
    seen = [[False] * cols for _ in range(rows)]
    seen[sr][sc] = True
    layer = [(sr, sc)]
    total = 1
    steps = 0
    while layer and steps < k:
        steps += 1
        nxt = []
        for r, c in layer:
            for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nr, nc = r + dr, c + dc
                if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] == 0 and not seen[nr][nc]:
                    seen[nr][nc] = True
                    nxt.append((nr, nc))
        total += len(nxt)
        layer = nxt
    return total
''',
    tests=[[[[0, 0, 1], [1, 0, 0], [0, 0, 0]], 0, 0, 2], [[[0, 0, 1], [1, 0, 0], [0, 0, 0]], 0, 0, 3], [[[0]], 0, 0, 0],
           [[[0]], 0, 0, 100], [[[0, 0, 0, 0, 0]], 0, 2, 1], [[[0, 0, 0, 0, 0]], 0, 2, 2],
           [[[0, 1, 0], [0, 1, 0], [0, 1, 0]], 0, 0, 10], [[[0, 0, 0], [0, 0, 0], [0, 0, 0]], 1, 1, 1],
           [[[0, 0, 0], [0, 0, 0], [0, 0, 0]], 0, 0, 4], [[[0, 0, 0], [0, 0, 0], [0, 0, 0]], 0, 0, 3],
           [[[1, 1, 1], [1, 0, 1], [1, 1, 1]], 1, 1, 5]],
)
_r = rnd(8103)
p["tests"].append([_grid(_r, 60, 60, 0.25, clear=[(5, 5)]), 5, 5, 40])
p["tests"].append([_grid(_r, 60, 60, 0.25, clear=[(30, 30)]), 30, 30, 5000])
p["tests"].append([_s, 0, 0, 1500])
p["tests"].append(_until(p, lambda: [_grid(_r, 60, 60, 0.38, clear=[(59, 0)]), 59, 0, 60], lambda v: v > 100))


def b_within(grid, sr, sc, k):
    R, C = len(grid), len(grid[0])
    nodes = [(i, j) for i in range(R) for j in range(C) if grid[i][j] == 0]
    nb = lambda u: [(u[0] + a, u[1] + b) for a, b in DIRS4 if 0 <= u[0] + a < R and 0 <= u[1] + b < C and grid[u[0] + a][u[1] + b] == 0]
    d = _bf(nodes, nb, (sr, sc))
    return sum(1 for v in d.values() if v <= k)


def g_within(r):
    R, C = r.randint(1, 6), r.randint(1, 6)
    g = _grid(r, R, C, r.choice([0.2, 0.4, 0.55]))
    s = (r.randrange(R), r.randrange(C))
    g[s[0]][s[1]] = 0
    return [g, s[0], s[1], r.randint(0, 8)]


def v_within(tests):
    for t in tests:
        g, sr, sc, k = t["args"]
        _rect(g, 60, 60, (0, 1))
        assert 0 <= sr < len(g) and 0 <= sc < len(g[0]) and g[sr][sc] == 0
        assert 0 <= k <= 5000


CHECKS["cells-within-k-steps"] = (b_within, g_within, "exact")
VALIDATE["cells-within-k-steps"] = v_within

# =================================================================== MEDIUM
# ---------------------------------------------------------------- knight on a bounded board
p = add(
    id="knight-moves-on-bounded-board", title="Knight Moves on a Bounded Board", diff="Medium", topic="Graphs",
    fn="knightMoves", params=[("n", "int"), ("sr", "int"), ("sc", "int"), ("tr", "int"), ("tc", "int")], ret="int", cmp="exact",
    desc="<p>A chess knight stands on the square <code>(sr, sc)</code> of an <code>n x n</code> board (rows and columns are numbered from 0). One knight move changes the position by <code>(&plusmn;1, &plusmn;2)</code> or <code>(&plusmn;2, &plusmn;1)</code>, and the knight may never leave the board. Other pieces are not present.</p><p>Return the minimum number of moves needed to reach <code>(tr, tc)</code>, or <code>-1</code> if the target is unreachable. If the knight already stands on the target, the answer is <code>0</code>.</p><pre>n = 8, start = (0,0), target = (7,7)  ->  6\nn = 3, start = (0,0), target = (1,1)  -> -1     (the centre of a 3x3 board is never reachable)</pre>",
    constraints=["1 &le; n &le; 200", "0 &le; sr, sc, tr, tc &lt; n"],
    hints=["Think of the squares as nodes and legal knight moves as edges. All edges cost one move.",
           "Run BFS from the start square, generating the eight knight moves and discarding those outside the board.",
           "Small boards are the tricky cases: on 1x1, 2x2 and 3x3 boards some squares cannot be reached at all, so the search simply ends without finding the target and the answer is -1."],
    editorial=["The knight graph on an n &times; n board is unweighted, so BFS from the start gives the minimum number of moves to every square. Generate the eight offsets <code>(1,2),(2,1),(-1,2),...</code>, keep those inside the board, and store a distance for every square.",
               "There is no formula to rely on for bounded boards: near corners and edges the knight loses moves, and the tiny boards are not connected (on 3 &times; 3 the centre has no moves in or out; on 2 &times; 2 the knight cannot move at all). BFS handles all of that automatically and returns -1 when the target is never found.",
               "There are n&sup2; squares with eight neighbours each, so the work is O(n&sup2;) time and memory."],
    time="O(n&sup2;)", space="O(n&sup2;)",
    solution='''from collections import deque


def knightMoves(n, sr, sc, tr, tc):
    dist = [[-1] * n for _ in range(n)]
    dist[sr][sc] = 0
    q = deque([(sr, sc)])
    moves = ((1, 2), (2, 1), (-1, 2), (-2, 1), (1, -2), (2, -1), (-1, -2), (-2, -1))
    while q:
        r, c = q.popleft()
        if r == tr and c == tc:
            return dist[r][c]
        for dr, dc in moves:
            nr, nc = r + dr, c + dc
            if 0 <= nr < n and 0 <= nc < n and dist[nr][nc] == -1:
                dist[nr][nc] = dist[r][c] + 1
                q.append((nr, nc))
    return -1
''',
    tests=[[8, 0, 0, 7, 7], [3, 0, 0, 1, 1], [1, 0, 0, 0, 0], [2, 0, 0, 1, 1], [2, 0, 0, 0, 0], [3, 1, 1, 1, 1], [3, 0, 0, 2, 1],
           [3, 0, 0, 2, 2], [4, 0, 0, 3, 3], [5, 2, 2, 2, 3], [8, 3, 3, 4, 4], [6, 0, 5, 5, 0], [200, 0, 0, 199, 199],
           [150, 3, 7, 140, 99], [199, 100, 100, 0, 198]],
)


def b_knight(n, sr, sc, tr, tc):
    sq = [(i, j) for i in range(n) for j in range(n)]
    nb = lambda u: [(u[0] + a, u[1] + b) for a, b in ((1, 2), (2, 1), (-1, 2), (-2, 1), (1, -2), (2, -1), (-1, -2), (-2, -1)) if 0 <= u[0] + a < n and 0 <= u[1] + b < n]
    return _bf(sq, nb, (sr, sc)).get((tr, tc), -1)


def g_knight(r):
    n = r.randint(1, 8)
    return [n, r.randrange(n), r.randrange(n), r.randrange(n), r.randrange(n)]


def v_knight(tests):
    for t in tests:
        n, sr, sc, tr, tc = t["args"]
        assert 1 <= n <= 200
        assert all(0 <= v < n for v in (sr, sc, tr, tc))


CHECKS["knight-moves-on-bounded-board"] = (b_knight, g_knight, "exact")
VALIDATE["knight-moves-on-bounded-board"] = v_knight

# ---------------------------------------------------------------- snakes and ladders
p = add(
    id="snakes-and-ladders-fewest-rolls", title="Snakes and Ladders Fewest Rolls", diff="Medium", topic="Graphs",
    fn="snakesAndLadders", params=[("board", "int[][]")], ret="int", cmp="exact",
    desc="<p>A game board is an <code>n x n</code> grid whose squares are numbered <code>1</code> to <code>n&sup2;</code> in a zigzag: the numbering starts in the <strong>bottom-left</strong> corner (<code>board[n-1][0]</code>), runs left to right along the bottom row, continues one row up from right to left, then left to right again, and so on.</p><p>A square holds either <code>-1</code> or a number <code>d</code> (1 &le; d &le; n&sup2;), meaning a ladder or snake that sends you to square <code>d</code>. You start on square 1. In each turn you choose a die value <code>x</code> from <code>1</code> to <code>6</code> and move to square <code>s + x</code>; a move that would go beyond square <code>n&sup2;</code> is not allowed. If the square you land on holds a number <code>d</code> you <strong>must</strong> go to square <code>d</code> (once; the destination square's own number is not followed). You win when you stand on square <code>n&sup2;</code>.</p><p>Return the minimum number of turns needed to win, or <code>-1</code> if it is impossible.</p><pre>board = [[-1,-1,-1,-1],\n         [-1,-1,-1,-1],\n         [-1,-1,-1,-1],\n         [-1, 5,-1,-1]]   (squares 1..16; bottom row is 1 2 3 4)\n\nresult = 3</pre>",
    constraints=["2 &le; n &le; 50", "board[r][c] is -1 or an integer in [1, n&sup2;]", "Squares 1 and n&sup2; hold -1"],
    hints=["Squares are the nodes. From square s you can go to six squares, and ladders and snakes redirect the landing square.",
           "First convert the 2D board into a flat list indexed by square number; the zigzag rule says that every odd row counted from the bottom is read right to left.",
           "BFS over square numbers: from s try s+1..s+6 (skip those above n&sup2;), apply the jump if the square has one, and push it if unseen. The distance of n&sup2; is the answer."],
    editorial=["Every turn costs one roll, so the minimum number of turns is a shortest-path problem over the squares 1..n&sup2;. The edges out of square <code>s</code> lead to <code>jump(s + x)</code> for <code>x = 1..6</code>, where <code>jump(q)</code> is the number written on square <code>q</code> or <code>q</code> itself when it holds -1. A jump is followed only once because the rule says you do not chain from the destination.",
               "The only fiddly part is the numbering. For square number <code>L</code> let <code>i = L - 1</code>; its row counted from the bottom is <code>i // n</code> and the offset in that row is <code>i % n</code>. On even bottom-rows the column equals the offset, on odd bottom-rows it is <code>n - 1 - offset</code>. Precompute the flat jump table once.",
               "Run a BFS from square 1. Each square enters the queue once and has at most six outgoing edges, so the running time is O(n&sup2;). If square n&sup2; is never discovered (for example when six squares in a row all send you back), return -1."],
    time="O(n&sup2;)", space="O(n&sup2;)",
    solution='''from collections import deque


def snakesAndLadders(board):
    n = len(board)
    total = n * n
    jump = [0] * (total + 1)
    for label in range(1, total + 1):
        i = label - 1
        row_from_bottom, off = divmod(i, n)
        col = off if row_from_bottom % 2 == 0 else n - 1 - off
        v = board[n - 1 - row_from_bottom][col]
        jump[label] = v if v != -1 else label
    dist = [-1] * (total + 1)
    dist[1] = 0
    q = deque([1])
    while q:
        s = q.popleft()
        if s == total:
            return dist[s]
        for x in range(1, 7):
            t = s + x
            if t > total:
                break
            t = jump[t]
            if dist[t] == -1:
                dist[t] = dist[s] + 1
                q.append(t)
    return -1
''',
    tests=[[[[-1, -1, -1, -1], [-1, -1, -1, -1], [-1, -1, -1, -1], [-1, 11, -1, -1]]],
           [[[-1, -1], [-1, -1]]],
           [[[-1, -1, -1], [-1, -1, -1], [-1, -1, -1]]],
           [[[1, -1, -1], [1, 1, 1], [-1, 1, 1]]],
           [[[-1, -1, -1, -1, -1, -1], [-1, -1, -1, -1, -1, -1], [-1, -1, -1, -1, -1, -1], [-1, 35, -1, -1, 13, -1], [-1, -1, -1, -1, -1, -1], [-1, 15, -1, -1, -1, -1]]],
           [[[-1, -1, -1], [-1, 9, -1], [-1, 1, 1]]],
           [[[-1, -1, -1, -1], [-1, -1, -1, -1], [1, 1, 1, 1], [-1, 1, 1, 1]]],
           [[[-1, -1, -1, -1], [-1, -1, -1, -1], [-1, -1, -1, -1], [-1, 16, -1, -1]]],
           [[[-1, 1, -1], [-1, -1, -1], [-1, -1, -1]]]],
)
_r = rnd(8104)


def _sl_board(r, n, extra):
    N = n * n
    flat = [-1] * (N + 1)
    for _ in range(extra):
        s = r.randint(2, N - 1)
        flat[s] = r.randint(1, N)
    b = [[-1] * n for _ in range(n)]
    for L in range(1, N + 1):
        rb, off = divmod(L - 1, n)
        col = off if rb % 2 == 0 else n - 1 - off
        b[n - 1 - rb][col] = flat[L]
    return b


p["tests"].append([_sl_board(_r, 50, 0)])
p["tests"].append([_sl_board(_r, 50, 150)])
p["tests"].append([_sl_board(_r, 45, 400)])
p["tests"].append([_sl_board(_r, 30, 60)])
_b = _sl_board(_r, 40, 100)
for _L in range(2, 8):
    _rb, _off = divmod(_L - 1, 40)
    _b[39 - _rb][_off if _rb % 2 == 0 else 39 - _off] = 1
p["tests"].append([_b])


def b_snakes(board):
    n = len(board)
    N = n * n
    pos = []  # pos[L-1] = (row, col) of square L, built by walking the zigzag
    for k, row in enumerate(range(n - 1, -1, -1)):
        cols = list(range(n)) if k % 2 == 0 else list(range(n - 1, -1, -1))
        pos.extend((row, c) for c in cols)

    def land(L):
        v = board[pos[L - 1][0]][pos[L - 1][1]]
        return L if v == -1 else v

    nb = lambda s: [land(s + x) for x in range(1, 7) if s + x <= N]
    return _bf(range(1, N + 1), nb, 1).get(N, -1)


def g_snakes(r):
    n = r.randint(2, 5)
    return [_sl_board(r, n, r.randint(0, n * 2))]


def v_snakes(tests):
    for t in tests:
        b = t["args"][0]
        n = len(b)
        assert 2 <= n <= 50 and all(len(row) == n for row in b)
        for row in b:
            for v in row:
                assert v == -1 or 1 <= v <= n * n
        assert b[n - 1][0] == -1
        # square n^2 is in the top row: column 0 when n is even, column n-1 when n is odd
        last = b[0][0] if n % 2 == 0 else b[0][n - 1]
        assert last == -1


CHECKS["snakes-and-ladders-fewest-rolls"] = (b_snakes, g_snakes, "exact")
VALIDATE["snakes-and-ladders-fewest-rolls"] = v_snakes

# ---------------------------------------------------------------- portals
p = add(
    id="maze-with-portal-pairs", title="Maze with Portal Pairs", diff="Medium", topic="Graphs",
    fn="minStepsWithPortals", params=[("grid", "int[][]")], ret="int", cmp="exact",
    desc="<p>A <code>grid</code> describes a maze. A cell holds <code>-1</code> for a wall, <code>0</code> for an ordinary open cell, or a positive number <code>p</code> for a <em>portal</em> cell. Every positive label appears on <strong>exactly two</strong> cells, and these two cells are twins.</p><p>You start in the top-left cell and want to reach the bottom-right cell. One step is either (a) a move to an adjacent cell (up, down, left, right) that is not a wall, or (b) if you are standing on a portal cell, a jump to its twin. Both kinds of step cost one. Return the minimum number of steps, or <code>-1</code> if the goal cannot be reached.</p><pre>grid = [[0, 1,-1, 0],\n        [-1,-1,-1,-1],\n        [0, 0, 1, 0]]\n\nresult = 3      ((0,0) -> (0,1) -> jump to (2,2) -> (2,3))</pre><p>Portals can be walked through like open cells; stepping onto a portal does not move you automatically, it only gives you the option of a jump on the next step.</p>",
    constraints=["1 &le; rows, cols &le; 60", "grid[r][c] is -1, 0, or a positive integer up to 1,000", "Every positive label occurs exactly twice", "The top-left and bottom-right cells are both 0"],
    hints=["Add the portal jumps as extra edges to the usual grid graph; all edges still cost one.",
           "Before the search, scan the grid once and record, for every portal cell, the position of its twin.",
           "BFS: from a cell, push the open 4-neighbours and, if the cell is a portal, also its twin. The first time the bottom-right cell is dequeued gives the answer."],
    editorial=["Portals do not change the nature of the problem: each cell has up to four ordinary neighbours plus, for portal cells, one extra neighbour (the twin), and every edge costs one. The graph is still unweighted, so BFS is the right tool.",
               "Preprocess with a dictionary from label to the first cell seen; when the second cell with the same label appears, store both as twins of each other. During BFS, expand each cell to its non-wall neighbours and its twin if it has one, marking cells visited when pushed.",
               "The preprocessing and the search each touch every cell a constant number of times: O(rows &times; cols) time and space. A portal can be a shortcut across the whole maze, so a plain grid distance (Manhattan or even plain BFS) is not enough."],
    time="O(R &middot; C)", space="O(R &middot; C)",
    solution='''from collections import deque


def minStepsWithPortals(grid):
    rows, cols = len(grid), len(grid[0])
    first = {}
    twin = {}
    for r in range(rows):
        for c in range(cols):
            v = grid[r][c]
            if v > 0:
                if v in first:
                    twin[(r, c)] = first[v]
                    twin[first[v]] = (r, c)
                else:
                    first[v] = (r, c)
    dist = [[-1] * cols for _ in range(rows)]
    dist[0][0] = 0
    q = deque([(0, 0)])
    while q:
        r, c = q.popleft()
        if r == rows - 1 and c == cols - 1:
            return dist[r][c]
        nxt = [(r + dr, c + dc) for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1))
               if 0 <= r + dr < rows and 0 <= c + dc < cols and grid[r + dr][c + dc] != -1]
        if (r, c) in twin:
            nxt.append(twin[(r, c)])
        for nr, nc in nxt:
            if dist[nr][nc] == -1:
                dist[nr][nc] = dist[r][c] + 1
                q.append((nr, nc))
    return -1
''',
    tests=[[[[0, 1, -1, 0], [-1, -1, -1, -1], [0, 0, 1, 0]]], [[[0]]], [[[0, -1, 0]]],
           [[[0, 1, -1, 1, 0]]], [[[0, 1, -1, 1, 2, 0, -1, 2, 0]]],
           [[[0, 0, 0], [0, 0, 0], [0, 0, 0]]],
           [[[0, 1, 0], [-1, -1, -1], [0, 1, 0]]],
           [[[0, 1, 1, -1, 0], [-1, -1, -1, -1, -1], [0, -1, -1, -1, 0]]],
           [[[0, 5, -1, 0], [-1, 6, -1, 5], [6, -1, -1, 0]]],
           [[[0, 1], [1, 0]]]],
)
_r = rnd(8105)


def _portal_grid(r, R, C, wall, pairs):
    g = _grid(r, R, C, wall, vals=(0, -1), clear=[(0, 0), (R - 1, C - 1)])
    free = [(i, j) for i in range(R) for j in range(C) if (i, j) not in ((0, 0), (R - 1, C - 1))]
    r.shuffle(free)
    for lab in range(1, pairs + 1):
        if len(free) < 2:
            break
        a, b = free.pop(), free.pop()
        g[a[0]][a[1]] = lab
        g[b[0]][b[1]] = lab
    return g


p["tests"].append([_portal_grid(_r, 60, 60, 0.3, 30)])
p["tests"].append(_until(p, lambda: [_portal_grid(_r, 60, 60, 0.5, 60)], lambda v: v > 0))
p["tests"].append([_portal_grid(_r, 60, 60, 0.45, 0)])
_g = [[0] * 59 for _ in range(59)]
for _i in range(1, 59, 2):
    _g[_i] = [-1] * 59
    _g[_i][58 if (_i // 2) % 2 == 0 else 0] = 0
_g[10][5] = 7
_g[50][3] = 7
_g[56][30] = 9
_g[2][40] = 9
p["tests"].append([_g])


def b_portal(grid):
    R, C = len(grid), len(grid[0])
    cells = [(i, j) for i in range(R) for j in range(C) if grid[i][j] != -1]
    by = {}
    for (i, j) in cells:
        if grid[i][j] > 0:
            by.setdefault(grid[i][j], []).append((i, j))

    def nb(u):
        out = [(u[0] + a, u[1] + b) for a, b in DIRS4 if 0 <= u[0] + a < R and 0 <= u[1] + b < C and grid[u[0] + a][u[1] + b] != -1]
        v = grid[u[0]][u[1]]
        if v > 0:
            out += [w for w in by[v] if w != u]
        return out

    return _bf(cells, nb, (0, 0)).get((R - 1, C - 1), -1)


def g_portal(r):
    R, C = r.randint(1, 6), r.randint(1, 6)
    if R * C < 2:
        return [[[0]]]
    return [_portal_grid(r, R, C, r.choice([0.2, 0.4]), r.randint(0, min(4, (R * C - 2) // 2)))]


def v_portal(tests):
    for t in tests:
        g = t["args"][0]
        _rect(g, 60, 60)
        cnt = {}
        for row in g:
            for v in row:
                assert v == -1 or 0 <= v <= 1000
                if v > 0:
                    cnt[v] = cnt.get(v, 0) + 1
        assert all(c == 2 for c in cnt.values()), "portal labels must occur exactly twice"
        assert g[0][0] == 0 and g[-1][-1] == 0


CHECKS["maze-with-portal-pairs"] = (b_portal, g_portal, "exact")
VALIDATE["maze-with-portal-pairs"] = v_portal

# ---------------------------------------------------------------- queen moves with blockers
p = add(
    id="minimum-queen-moves-with-blockers", title="Minimum Queen Moves with Blockers", diff="Medium", topic="Graphs",
    fn="queenMoves", params=[("grid", "int[][]"), ("sr", "int"), ("sc", "int"), ("tr", "int"), ("tc", "int")], ret="int", cmp="exact",
    desc="<p>A <code>grid</code> is a board where <code>0</code> marks a free square and <code>1</code> a blocked square. A chess queen stands on the free square <code>(sr, sc)</code>. In one move the queen slides any number (at least one) of squares in one of the <strong>8</strong> directions (along a row, a column or a diagonal). Every square it passes over and the square where it stops must be free; it cannot jump over or land on a blocked square.</p><p>Return the minimum number of moves to bring the queen to the free square <code>(tr, tc)</code>, or <code>-1</code> if that is impossible. If the two squares are equal the answer is <code>0</code>.</p><pre>grid = [[0,0,0],\n        [0,1,0],\n        [0,0,0]],  start = (0,0), target = (2,2)\n\nresult = 2     ((0,0) -> (0,2) -> (2,2))</pre>",
    constraints=["1 &le; rows, cols &le; 40", "grid[r][c] is 0 or 1", "The start and the target squares are free (0) and inside the board"],
    hints=["Each queen move is one edge, no matter how far the queen slides. Squares are nodes, so BFS counts moves.",
           "From a square, walk in each of the 8 directions step by step, stopping at the board edge or a blocked square; every free square on the way is a neighbour at distance +1.",
           "To keep the sliding cheap, stop a ray when you meet a square whose distance is already smaller than or equal to the current one: that square will itself cover the rest of the ray. Squares at exactly distance + 1 may be passed through."],
    editorial=["The moves of a sliding piece form an unweighted graph whose edges are 'can reach by one slide', so BFS over squares gives the minimum number of moves. The neighbours of a square are all free squares you meet while walking outward in each direction until a wall or the border.",
               "Naive expansion costs O(max(R,C)) per direction per square, which is still fine for a 40 &times; 40 board (about 40 &middot; 40 &middot; 8 &middot; 40 steps). A standard pruning makes it linear in practice: while sliding from a square with distance <code>d</code>, if you meet a square with distance &le; <code>d</code>, stop, because that square (and the ones beyond it) was or will be expanded with an equal or better distance; if the square is unvisited, label it <code>d + 1</code>; if it already has <code>d + 1</code>, keep walking.",
               "Return the distance when the target is dequeued; if the queue runs out, the answer is -1. Note that on an open board the answer is at most 2, so interesting cases come from walls that cut rays."],
    time="O(R &middot; C &middot; max(R, C))", space="O(R &middot; C)",
    solution='''from collections import deque


def queenMoves(grid, sr, sc, tr, tc):
    rows, cols = len(grid), len(grid[0])
    dist = [[-1] * cols for _ in range(rows)]
    dist[sr][sc] = 0
    q = deque([(sr, sc)])
    dirs = ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1))
    while q:
        r, c = q.popleft()
        d = dist[r][c]
        if r == tr and c == tc:
            return d
        for dr, dc in dirs:
            nr, nc = r + dr, c + dc
            while 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] == 0:
                if dist[nr][nc] == -1:
                    dist[nr][nc] = d + 1
                    q.append((nr, nc))
                elif dist[nr][nc] <= d:
                    break
                nr += dr
                nc += dc
    return -1
''',
    tests=[[[[0, 0, 0], [0, 1, 0], [0, 0, 0]], 0, 0, 2, 2], [[[0]], 0, 0, 0, 0], [[[0, 0, 0], [0, 0, 0], [0, 0, 0]], 0, 0, 1, 2],
           [[[0, 1, 0]], 0, 0, 0, 2], [[[0, 0, 0, 0]], 0, 0, 0, 3], [[[0, 0], [0, 0]], 0, 1, 1, 0],
           [[[0, 1, 1], [1, 1, 1], [1, 1, 0]], 0, 0, 2, 2], [[[0, 0, 1, 0], [1, 0, 1, 1], [0, 0, 0, 0], [0, 1, 1, 0]], 0, 0, 3, 3],
           [[[0, 1, 0, 0, 0], [0, 1, 0, 1, 0], [0, 1, 0, 1, 0], [0, 0, 0, 1, 0], [1, 1, 1, 1, 0]], 0, 0, 4, 4],
           [[[0, 0, 1, 0, 0], [0, 1, 1, 1, 0], [1, 1, 0, 1, 1], [0, 1, 1, 1, 0], [0, 0, 1, 0, 0]], 0, 0, 2, 2]],
)
_r = rnd(8106)
p["tests"].append([_grid(_r, 40, 40, 0.25, clear=[(0, 0), (39, 39)]), 0, 0, 39, 39])
p["tests"].append([_grid(_r, 40, 40, 0.5, clear=[(3, 35), (36, 2)]), 3, 35, 36, 2])
p["tests"].append([_grid(_r, 40, 40, 0.6, clear=[(20, 20), (21, 21)]), 20, 20, 21, 21])
_s2 = [[0] * 39 for _ in range(39)]
for _i in range(1, 39, 2):
    for _j in range(39):
        _s2[_i][_j] = 1
    _s2[_i][38 if (_i // 2) % 2 == 0 else 0] = 0
p["tests"].append([_s2, 0, 0, 38, 38])
p["tests"].append([_grid(_r, 40, 40, 0.0, clear=[(5, 5), (30, 11)]), 5, 5, 30, 11])


def b_queen(grid, sr, sc, tr, tc):
    R, C = len(grid), len(grid[0])
    cells = [(i, j) for i in range(R) for j in range(C) if grid[i][j] == 0]

    def nb(u):
        out = []
        for a, b in DIRS8:
            for k in range(1, max(R, C)):
                x, y = u[0] + a * k, u[1] + b * k
                if not (0 <= x < R and 0 <= y < C) or grid[x][y] == 1:
                    break
                out.append((x, y))
        return out

    return _bf(cells, nb, (sr, sc)).get((tr, tc), -1)


def g_queen(r):
    R, C = r.randint(1, 6), r.randint(1, 6)
    g = _grid(r, R, C, r.choice([0.2, 0.4, 0.6]))
    s = (r.randrange(R), r.randrange(C))
    t = (r.randrange(R), r.randrange(C))
    g[s[0]][s[1]] = 0
    g[t[0]][t[1]] = 0
    return [g, s[0], s[1], t[0], t[1]]


def v_queen(tests):
    for t in tests:
        g, sr, sc, tr, tc = t["args"]
        _rect(g, 40, 40, (0, 1))
        assert 0 <= sr < len(g) and 0 <= tr < len(g) and 0 <= sc < len(g[0]) and 0 <= tc < len(g[0])
        assert g[sr][sc] == 0 and g[tr][tc] == 0


CHECKS["minimum-queen-moves-with-blockers"] = (b_queen, g_queen, "exact")
VALIDATE["minimum-queen-moves-with-blockers"] = v_queen

# ---------------------------------------------------------------- blinking gates
p = add(
    id="crossing-blinking-gates", title="Crossing Blinking Gates", diff="Medium", topic="Graphs",
    fn="minTimeThroughGates", params=[("grid", "int[][]")], ret="int", cmp="exact",
    desc="<p>A <code>grid</code> contains these cells: <code>0</code> is always open, <code>1</code> is a wall, <code>2</code> is a gate that is open only during <strong>even</strong> minutes, and <code>3</code> is a gate that is open only during <strong>odd</strong> minutes.</p><p>At minute 0 you stand on the top-left cell. In every minute you either stay where you are or move to one of the four adjacent cells. The cell you stand on at minute <code>t</code> must be open at minute <code>t</code>. So you cannot enter a gate while it is closed, and you also cannot stay on a gate when it closes.</p><p>Return the earliest minute at which you can stand on the bottom-right cell, or <code>-1</code> if you never can.</p><pre>grid = [[0,3,0],\n        [1,1,2]]\n\nresult = 4      (minute 1: (0,1); minute 2: (0,2); minute 3: wait, the gate below is closed; minute 4: (1,2))</pre>",
    constraints=["1 &le; rows, cols &le; 50", "grid[r][c] is 0, 1, 2 or 3", "The top-left cell is 0"],
    hints=["Time matters, but a gate only cares whether the current minute is even or odd. How many different 'time states' does a cell really have?",
           "Use BFS on states (cell, parity of the current minute). From a state at minute t you can go to the same cell or a neighbour at minute t + 1, if the target cell is open at that minute.",
           "The goal is reached when any state at the bottom-right cell is first discovered; the layer number at that moment is the minute. Reaching a state later with the same parity can never be better, so each (cell, parity) is expanded once."],
    editorial=["The future of a walker depends only on its cell and on whether the minute is even or odd, because the gates repeat every two minutes. That gives at most 2 &times; rows &times; cols states. Each BFS layer is one minute: from every state of layer <code>t - 1</code> try staying and the four moves, and keep a candidate when the target cell is open at minute <code>t</code> (type 0, type 2 at even t, type 3 at odd t) and the pair (cell, <code>t mod 2</code>) is new.",
               "Why is discarding a repeated (cell, parity) correct? If the walker could stand there at minute <code>t</code> and again at <code>t + 2k</code>, every plan that starts at the later time can be started 2k minutes earlier, because the gate pattern is the same. So the earliest visit dominates.",
               "The first layer that contains the bottom-right cell is the answer (minute 0 if the grid is a single cell). If the frontier becomes empty, return -1. The total cost is O(rows &times; cols)."],
    time="O(R &middot; C)", space="O(R &middot; C)",
    solution='''def minTimeThroughGates(grid):
    rows, cols = len(grid), len(grid[0])
    goal = rows * cols - 1
    if goal == 0:
        return 0
    seen = [[False, False] for _ in range(rows * cols)]
    seen[0][0] = True
    frontier = [0]
    t = 0
    while frontier:
        t += 1
        par = t & 1
        nxt = []
        for u in frontier:
            r, c = divmod(u, cols)
            for nr, nc in ((r, c), (r + 1, c), (r - 1, c), (r, c + 1), (r, c - 1)):
                if 0 <= nr < rows and 0 <= nc < cols:
                    v = grid[nr][nc]
                    if v == 0 or (v == 2 and par == 0) or (v == 3 and par == 1):
                        w = nr * cols + nc
                        if not seen[w][par]:
                            seen[w][par] = True
                            if w == goal:
                                return t
                            nxt.append(w)
        frontier = nxt
    return -1
''',
    tests=[[[[0, 3, 0], [1, 1, 2]]], [[[0]]], [[[0, 0]]], [[[0, 2]]], [[[0, 3]]], [[[0, 1], [1, 0]]],
           [[[0, 3, 2, 3, 0]]], [[[0, 2, 0], [3, 1, 3], [0, 2, 0]]],
           [[[0, 3, 1], [1, 2, 1], [1, 3, 0]]], [[[0, 2, 3, 2, 3, 0]]], [[[0, 3], [3, 2]]],
           [[[0, 0, 0], [1, 1, 3], [0, 0, 0]]]],
)
_r = rnd(8107)
def _gate_grid(r, R, C, pw):
    g = [[r.choices([0, 1, 2, 3], weights=[0.7 - pw, pw, 0.15, 0.15])[0] for _ in range(C)] for _ in range(R)]
    g[0][0] = 0
    return g


for _R, _C, _pw, _want in ((50, 50, 0.1, True), (50, 50, 0.2, True), (40, 50, 0.3, False)):
    p["tests"].append(_until(p, lambda: [_gate_grid(_r, _R, _C, _pw)], lambda v: (v > 0) == _want))
_gr = [[0] * 50 for _ in range(50)]
for _i in range(50):
    for _j in range(50):
        if _i == 0 and _j == 0:
            continue
        _gr[_i][_j] = 2 if (_i + _j) % 2 == 0 else 3
p["tests"].append([_gr])


def b_gates(grid):
    R, C = len(grid), len(grid[0])

    def ok(v, t):
        return v == 0 or (v == 2 and t % 2 == 0) or (v == 3 and t % 2 == 1)

    cur = {(0, 0)}
    for t in range(0, 2 * R * C + 4):
        if (R - 1, C - 1) in cur:
            return t
        nxt = set()
        for (i, j) in cur:
            for a, b in ((0, 0),) + DIRS4:
                x, y = i + a, j + b
                if 0 <= x < R and 0 <= y < C and ok(grid[x][y], t + 1):
                    nxt.add((x, y))
        cur = nxt
    return -1


def g_gates(r):
    R, C = r.randint(1, 5), r.randint(1, 5)
    g = [[r.choice([0, 0, 1, 2, 2, 3, 3]) for _ in range(C)] for _ in range(R)]
    g[0][0] = 0
    return [g]


def v_gates(tests):
    for t in tests:
        g = t["args"][0]
        _rect(g, 50, 50, (0, 1, 2, 3))
        assert g[0][0] == 0


CHECKS["crossing-blinking-gates"] = (b_gates, g_gates, "exact")
VALIDATE["crossing-blinking-gates"] = v_gates

# =================================================================== HARD
# ---------------------------------------------------------------- wall breaks
p = add(
    id="shortest-path-with-wall-breaks", title="Shortest Path with Wall Breaks", diff="Hard", topic="Graphs",
    fn="shortestWithBreaks", params=[("grid", "int[][]"), ("k", "int")], ret="int", cmp="exact",
    desc="<p>A <code>grid</code> holds <code>0</code> for an open cell and <code>1</code> for a wall. You start at the top-left cell and want to reach the bottom-right cell, moving one step at a time up, down, left or right. You are allowed to walk <em>through</em> walls, but you may enter at most <code>k</code> wall cells in total over the whole trip (each time you step onto a wall cell counts as one, even if you have stepped onto that same cell before).</p><p>Return the minimum number of steps from the start to the goal, or <code>-1</code> if it cannot be done. When the grid is a single cell the answer is <code>0</code>.</p><pre>grid = [[0,1,1],\n        [1,1,1],\n        [1,1,0]]\n\nk = 3  ->  4      (right, right, down, down crosses 3 walls)\nk = 2  -> -1</pre>",
    constraints=["1 &le; rows, cols &le; 40", "grid[r][c] is 0 or 1", "grid[0][0] = grid[rows-1][cols-1] = 0", "0 &le; k &le; rows &middot; cols"],
    hints=["Plain BFS on cells is not enough: reaching the same cell with different numbers of walls left leads to different futures.",
           "Make the state (row, col, walls already used) and run BFS on those states. The step count is the BFS layer.",
           "If k is at least rows + cols - 3, a monotone path (only right and down) never needs more than that many wall cells, so the answer is simply rows + cols - 2. For smaller k, remember for each cell the largest number of breaks still available when you got there, and only continue if a newcomer has strictly more."],
    editorial=["Add a third coordinate to the node: the number of walls broken so far. Moving to an open cell keeps it, moving onto a wall cell raises it by one, and states with more than k are illegal. All moves cost one step, so BFS over these states returns the minimum.",
               "The state space is rows &times; cols &times; (k + 1), which can be large if k is big, so use two simplifications. First, the shortest conceivable path is the Manhattan route of length rows + cols - 2, and it passes at most rows + cols - 3 wall cells (start and end are open); if k reaches that number the answer is exactly that distance. Second, keep for each cell the best (largest) number of breaks remaining ever seen and only push a new arrival when it improves this value; an earlier arrival with at least as many breaks left dominates a later one.",
               "With k capped at rows + cols - 3 the work is O((rows &times; cols) &middot; (rows + cols)), which is fast enough for a 40 &times; 40 grid."],
    time="O(R &middot; C &middot; min(k, R + C))", space="O(R &middot; C)",
    solution='''def shortestWithBreaks(grid, k):
    rows, cols = len(grid), len(grid[0])
    if rows == 1 and cols == 1:
        return 0
    k = min(k, rows + cols - 3)
    best = [[-1] * cols for _ in range(rows)]
    best[0][0] = k
    frontier = [(0, 0, k)]
    steps = 0
    while frontier:
        steps += 1
        nxt = []
        for r, c, rem in frontier:
            for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nr, nc = r + dr, c + dc
                if 0 <= nr < rows and 0 <= nc < cols:
                    nrem = rem - grid[nr][nc]
                    if nrem > best[nr][nc]:
                        if nr == rows - 1 and nc == cols - 1:
                            return steps
                        best[nr][nc] = nrem
                        nxt.append((nr, nc, nrem))
        frontier = nxt
    return -1
''',
    tests=[[[[0, 1, 1], [1, 1, 1], [1, 1, 0]], 3], [[[0, 1, 1], [1, 1, 1], [1, 1, 0]], 2], [[[0]], 0], [[[0, 0]], 0],
           [[[0, 0, 0], [1, 1, 0], [0, 0, 0], [0, 1, 1], [0, 0, 0]], 1], [[[0, 1, 0], [1, 1, 1], [0, 1, 0]], 0],
           [[[0, 1, 0], [1, 1, 1], [0, 1, 0]], 3], [[[0, 1, 1, 1], [1, 1, 1, 1], [1, 1, 1, 0]], 3],
           [[[0, 1, 1, 1], [1, 1, 1, 1], [1, 1, 1, 0]], 4], [[[0, 1, 0, 0], [0, 1, 0, 1], [0, 0, 0, 1], [1, 1, 1, 0]], 1],
           [[[0, 0, 0, 0, 0], [1, 1, 1, 1, 0], [0, 0, 0, 0, 0], [0, 1, 1, 1, 1], [0, 0, 0, 0, 0]], 0],
           [[[0, 0, 0, 0, 0], [1, 1, 1, 1, 0], [0, 0, 0, 0, 0], [0, 1, 1, 1, 1], [0, 0, 0, 0, 0]], 1],
           [[[0, 1], [1, 0]], 1]],
)
_r = rnd(8108)
p["tests"].append([_grid(_r, 40, 40, 0.35, clear=[(0, 0), (39, 39)]), 3])
p["tests"].append(_until(p, lambda: [_grid(_r, 40, 40, 0.5, clear=[(0, 0), (39, 39)]), 6], lambda v: v > 0))
p["tests"].append([_grid(_r, 40, 40, 0.3, clear=[(0, 0), (39, 39)]), 0])
_w = [[0 if (i + j) % 7 else 1 for j in range(40)] for i in range(40)]
_w[0][0] = 0
_w[39][39] = 0
p["tests"].append([_w, 12])


def b_breaks(grid, k):
    R, C = len(grid), len(grid[0])
    nodes = [(i, j, u) for i in range(R) for j in range(C) for u in range(k + 1)]

    def nb(s):
        i, j, u = s
        out = []
        for a, b in DIRS4:
            x, y = i + a, j + b
            if 0 <= x < R and 0 <= y < C and u + grid[x][y] <= k:
                out.append((x, y, u + grid[x][y]))
        return out

    d = _bf(nodes, nb, (0, 0, 0))
    ends = [d[(R - 1, C - 1, u)] for u in range(k + 1) if (R - 1, C - 1, u) in d]
    return min(ends) if ends else -1


def g_breaks(r):
    R, C = r.randint(1, 5), r.randint(1, 5)
    g = _grid(r, R, C, r.choice([0.3, 0.5, 0.7]), clear=[(0, 0), (R - 1, C - 1)])
    return [g, r.randint(0, 5)]


def v_breaks(tests):
    for t in tests:
        g, k = t["args"]
        _rect(g, 40, 40, (0, 1))
        assert g[0][0] == 0 and g[-1][-1] == 0
        assert 0 <= k <= len(g) * len(g[0])


CHECKS["shortest-path-with-wall-breaks"] = (b_breaks, g_breaks, "exact")
VALIDATE["shortest-path-with-wall-breaks"] = v_breaks

# ---------------------------------------------------------------- collect all keys
p = add(
    id="shortest-walk-collecting-all-keys", title="Shortest Walk Collecting All Keys", diff="Hard", topic="Graphs",
    fn="collectAllKeys", params=[("grid", "int[][]")], ret="int", cmp="exact",
    desc="<p>A <code>grid</code> uses these codes: <code>0</code> empty cell, <code>1</code> wall, <code>2</code> your starting cell, <code>10 + i</code> the key number <code>i</code> (lying on that cell), and <code>20 + i</code> the door number <code>i</code>. If there are <code>m</code> keys, their numbers are exactly <code>0 .. m-1</code> (each key appears once), and each door number appears at most once and is smaller than <code>m</code>.</p><p>In one step you move up, down, left or right. You cannot enter a wall. Stepping onto a key cell picks the key up (keys are never used up). You may enter the cell of door <code>i</code> only if you already hold key <code>i</code>. Return the minimum number of steps after which you hold <strong>all</strong> <code>m</code> keys, or <code>-1</code> if that is impossible.</p><pre>grid = [[ 2,  0, 11],\n        [ 1,  1, 21],\n        [10,  0,  0]]\n\nresult = 6      (right, right: key 1; down through door 1, down, left, left: key 0)</pre>",
    constraints=["1 &le; rows, cols &le; 30", "Exactly one cell is 2; there are m keys, 1 &le; m &le; 6, with codes 10 .. 10+m-1 each appearing exactly once", "Door codes 20 + i appear at most once each, with i &lt; m", "Every other cell is 0 or 1"],
    hints=["The same cell visited with different sets of keys behaves differently. What should the BFS state contain?",
           "State = (row, col, set of keys held), with the key set stored as a bitmask. At most 6 keys means at most 64 masks.",
           "From a state try the four neighbours: skip walls and doors whose key bit is missing; if the neighbour is a key cell, set its bit. The first time the mask has all m bits set, the current layer number is the answer."],
    editorial=["Because a door can only be passed with the right key, being on a cell is not enough information: the keys in hand decide where you can go next. So the node is <code>(r, c, mask)</code> with <code>mask</code> a bitmask of the keys held. There are at most rows &times; cols &times; 2<sup>m</sup> = 30 &times; 30 &times; 64 = 57,600 such nodes.",
               "All moves cost one step, so BFS over these nodes finds the minimum. From <code>(r, c, mask)</code> look at each neighbour: ignore walls; ignore a door <code>i</code> if bit <code>i</code> is not in the mask; if the neighbour holds key <code>i</code>, the new mask is <code>mask | (1 &lt;&lt; i)</code>. Mark states visited when they are pushed. The search stops when the mask equals <code>(1 &lt;&lt; m) - 1</code>.",
               "Keys never disappear, so masks only grow, and each state is expanded once: O(rows &times; cols &times; 2<sup>m</sup>) time and memory. If the queue empties first, some key sits behind a door that can never be opened, and the answer is -1."],
    time="O(R &middot; C &middot; 2^m)", space="O(R &middot; C &middot; 2^m)",
    solution='''def collectAllKeys(grid):
    rows, cols = len(grid), len(grid[0])
    m = 0
    start = (0, 0)
    for r in range(rows):
        for c in range(cols):
            v = grid[r][c]
            if v == 2:
                start = (r, c)
            elif 10 <= v < 20:
                m += 1
    full = (1 << m) - 1
    nm = 1 << m
    seen = bytearray(rows * cols * nm)
    seen[(start[0] * cols + start[1]) * nm] = 1
    frontier = [(start[0], start[1], 0)]
    steps = 0
    while frontier:
        steps += 1
        nxt = []
        for r, c, mask in frontier:
            for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nr, nc = r + dr, c + dc
                if not (0 <= nr < rows and 0 <= nc < cols):
                    continue
                v = grid[nr][nc]
                if v == 1:
                    continue
                if 20 <= v < 30 and not (mask >> (v - 20)) & 1:
                    continue
                new = mask | (1 << (v - 10)) if 10 <= v < 20 else mask
                if new == full:
                    return steps
                idx = (nr * cols + nc) * nm + new
                if not seen[idx]:
                    seen[idx] = 1
                    nxt.append((nr, nc, new))
        frontier = nxt
    return -1
''',
    tests=[[[[2, 0, 11], [1, 1, 21], [10, 0, 0]]], [[[2, 20, 10]]], [[[2, 0, 10]]], [[[2, 10], [11, 0]]], [[[2, 10, 21, 11]]],
           [[[10, 20, 2, 21, 11]]], [[[10, 2, 0, 11]]], [[[2, 1, 10]]],
           [[[2, 0, 0, 10], [1, 1, 20, 1], [11, 0, 0, 0]]],
           [[[2, 10, 20, 11, 21, 12]]], [[[12, 22, 2, 10, 21, 11, 20]]]],
)
_r = rnd(8109)


def _keys_grid(r, R, C, m, wallp, doors):
    g = [[1 if r.random() < wallp else 0 for _ in range(C)] for _ in range(R)]
    cells = [(i, j) for i in range(R) for j in range(C)]
    r.shuffle(cells)
    a = cells.pop()
    g[a[0]][a[1]] = 2
    for i in range(m):
        a = cells.pop()
        g[a[0]][a[1]] = 10 + i
    for i in r.sample(range(m), min(doors, m, len(cells))):
        a = cells.pop()
        g[a[0]][a[1]] = 20 + i
    return g


_f = _fn(p)
for _want, _R, _C, _m, _wp, _dr in ((True, 30, 30, 6, 0.15, 3), (True, 30, 30, 6, 0.25, 4), (False, 30, 30, 6, 0.2, 6), (True, 28, 30, 5, 0.1, 5), (True, 30, 30, 6, 0.3, 2)):
    while True:
        _g = _keys_grid(_r, _R, _C, _m, _wp, _dr)
        _v = _f(_g)
        if (_v > 0) == _want:
            break
    p["tests"].append([_g])


def b_keys(grid):
    R, C = len(grid), len(grid[0])
    m = sum(1 for row in grid for v in row if 10 <= v < 20)
    st = [(i, j) for i in range(R) for j in range(C) if grid[i][j] == 2][0]
    nodes = [(i, j, k) for i in range(R) for j in range(C) if grid[i][j] != 1 for k in range(1 << m)]

    def nb(u):
        i, j, k = u
        out = []
        for a, b in DIRS4:
            x, y = i + a, j + b
            if 0 <= x < R and 0 <= y < C and grid[x][y] != 1:
                v = grid[x][y]
                if 20 <= v < 30 and not (k >> (v - 20)) & 1:
                    continue
                out.append((x, y, k | (1 << (v - 10)) if 10 <= v < 20 else k))
        return out

    d = _bf(nodes, nb, (st[0], st[1], 0))
    ends = [dd for (i, j, k), dd in d.items() if k == (1 << m) - 1]
    return min(ends) if ends else -1


def g_keys(r):
    R, C = r.randint(2, 4), r.randint(2, 4)
    m = r.randint(1, min(3, R * C - 1))
    return [_keys_grid(r, R, C, m, r.choice([0.1, 0.3]), r.randint(0, m))]


def v_keys(tests):
    for t in tests:
        g = t["args"][0]
        _rect(g, 30, 30)
        flat = [v for row in g for v in row]
        assert flat.count(2) == 1
        m = sum(1 for v in flat if 10 <= v < 20)
        assert 1 <= m <= 6
        assert sorted(v for v in flat if 10 <= v < 20) == list(range(10, 10 + m))
        doors = [v for v in flat if v >= 20]
        assert len(doors) == len(set(doors)) and all(20 <= v < 20 + m for v in doors)
        assert all(v in (0, 1, 2) or 10 <= v < 10 + m or 20 <= v < 20 + m for v in flat)


CHECKS["shortest-walk-collecting-all-keys"] = (b_keys, g_keys, "exact")
VALIDATE["shortest-walk-collecting-all-keys"] = v_keys

# ---------------------------------------------------------------- snake with rotations
p = add(
    id="snake-rotation-minimum-moves", title="Snake Rotation Minimum Moves", diff="Hard", topic="Graphs",
    fn="snakeMoves", params=[("grid", "int[][]")], ret="int", cmp="exact",
    desc="<p>On an <code>n x n</code> <code>grid</code> (<code>0</code> empty, <code>1</code> blocked) lives a snake that covers exactly two adjacent cells. At the start it lies horizontally on <code>(0,0)</code> and <code>(0,1)</code>. The goal is to have it lie horizontally on <code>(n-1,n-2)</code> and <code>(n-1,n-1)</code>.</p><p>A move can be one of these (all cells that the snake would newly cover must be empty and inside the grid):</p><ul><li><strong>right</strong>: both cells shift one column to the right;</li><li><strong>down</strong>: both cells shift one row down;</li><li><strong>rotate clockwise</strong>: a horizontal snake on <code>(r,c),(r,c+1)</code> may become vertical on <code>(r,c),(r+1,c)</code> if <code>(r+1,c)</code> and <code>(r+1,c+1)</code> are empty;</li><li><strong>rotate counter-clockwise</strong>: a vertical snake on <code>(r,c),(r+1,c)</code> may become horizontal on <code>(r,c),(r,c+1)</code> if <code>(r,c+1)</code> and <code>(r+1,c+1)</code> are empty.</li></ul><p>The snake never moves left or up. Return the minimum number of moves to reach the goal, or <code>-1</code> if it is impossible.</p><pre>grid = [[0,0,0],\n        [0,0,0],\n        [0,0,0]]\n\nresult = 3      (down, down, right)</pre>",
    constraints=["2 &le; n &le; 50", "grid[r][c] is 0 or 1", "The four cells (0,0), (0,1), (n-1,n-2), (n-1,n-1) are empty"],
    hints=["The snake's position is described by one anchor cell and its orientation (horizontal or vertical). That is your node.",
           "Number the states (r, c, orientation) with the anchor being the top-left cell of the snake. List, for a horizontal and for a vertical snake, which cells must be free for each of its moves.",
           "Run BFS from (0, 0, horizontal) and stop when you reach (n-1, n-2, horizontal). Each state has at most 3 outgoing moves, so there are about 2n&sup2; states and 6n&sup2; edges."],
    editorial=["Model the snake by the cell where its tail sits (the top-left one) and whether it is horizontal or vertical. A horizontal snake on <code>(r,c)</code> covers <code>(r,c)</code> and <code>(r,c+1)</code>, a vertical one covers <code>(r,c)</code> and <code>(r+1,c)</code>. That gives at most 2n&sup2; states, and every move costs one.",
               "From a horizontal state <code>(r,c,0)</code>: move right to <code>(r,c+1,0)</code> if <code>(r,c+2)</code> is free; move down to <code>(r+1,c,0)</code> if both cells below are free, and in that same situation also rotate to <code>(r,c,1)</code>. From a vertical state <code>(r,c,1)</code>: move down to <code>(r+1,c,1)</code> if <code>(r+2,c)</code> is free; move right to <code>(r,c+1,1)</code> if both cells to the right are free, and in that situation also rotate to <code>(r,c,0)</code>.",
               "BFS from the start state finds the shortest sequence. The target is the state <code>(n-1,n-2,0)</code>. Time and memory are O(n&sup2;). Because the snake can only go right, down or rotate, the search is small, but a rotation is the only way to get through a one-cell-wide vertical passage, so ignoring it gives wrong answers."],
    time="O(n&sup2;)", space="O(n&sup2;)",
    solution='''def snakeMoves(grid):
    n = len(grid)
    seen = [[[False, False] for _ in range(n)] for _ in range(n)]
    seen[0][0][0] = True
    frontier = [(0, 0, 0)]
    steps = 0
    while frontier:
        nxt = []
        for r, c, o in frontier:
            if r == n - 1 and c == n - 2 and o == 0:
                return steps
            cand = []
            if o == 0:
                if c + 2 < n and grid[r][c + 2] == 0:
                    cand.append((r, c + 1, 0))
                if r + 1 < n and grid[r + 1][c] == 0 and grid[r + 1][c + 1] == 0:
                    cand.append((r + 1, c, 0))
                    cand.append((r, c, 1))
            else:
                if r + 2 < n and grid[r + 2][c] == 0:
                    cand.append((r + 1, c, 1))
                if c + 1 < n and grid[r][c + 1] == 0 and grid[r + 1][c + 1] == 0:
                    cand.append((r, c + 1, 1))
                    cand.append((r, c, 0))
            for nr, nc, no in cand:
                if not seen[nr][nc][no]:
                    seen[nr][nc][no] = True
                    nxt.append((nr, nc, no))
        frontier = nxt
        steps += 1
    return -1
''',
    tests=[[[[0, 0, 0], [0, 0, 0], [0, 0, 0]]], [[[0, 0], [0, 0]]], [[[0, 0, 0], [0, 1, 0], [0, 0, 0]]],
           [[[0, 0, 1], [0, 0, 0], [0, 0, 0]]],
           [[[0, 0, 0, 0], [0, 0, 0, 1], [0, 1, 0, 0], [0, 0, 0, 0]]],
           [[[0, 0, 0, 0, 0], [0, 0, 0, 0, 1], [1, 1, 1, 0, 0], [0, 0, 1, 0, 0], [0, 1, 0, 0, 0]]],
           [[[0, 0, 0, 0, 1, 1], [0, 0, 0, 1, 1, 0], [0, 0, 1, 1, 0, 0], [0, 1, 0, 0, 0, 0], [0, 0, 0, 1, 1, 0], [0, 0, 0, 0, 0, 0]]],
           [[[0, 0, 0, 1, 1, 1], [0, 0, 0, 0, 1, 1], [1, 0, 1, 1, 0, 1], [0, 0, 0, 1, 1, 0], [0, 0, 0, 0, 1, 1], [0, 0, 0, 0, 0, 0]]],
           [[[0, 0, 0, 1, 1, 0, 0], [0, 0, 0, 1, 1, 1, 1], [0, 0, 0, 0, 0, 0, 0], [0, 1, 0, 0, 0, 1, 1], [0, 1, 0, 1, 0, 0, 1], [0, 0, 0, 0, 0, 0, 0], [1, 0, 1, 0, 0, 0, 0]]],
           [[[0, 0, 0, 0], [1, 1, 1, 0], [0, 0, 0, 0], [0, 0, 0, 0]]],
           [[[0, 0, 0, 0], [0, 1, 1, 1], [0, 0, 0, 0], [1, 1, 0, 0]]],
           [[[0, 0, 1, 0, 0], [0, 0, 1, 0, 0], [0, 0, 0, 0, 0], [0, 1, 1, 1, 0], [0, 0, 0, 0, 0]]]],
)
_r = rnd(8110)


def _shaft_grid(n, loops, runs, drops):
    """Free cells form a staircase corridor: 1-wide horizontal runs and 1-wide vertical shafts joined by 2x2 rooms."""
    g = [[1] * n for _ in range(n)]
    R, c = 0, 0
    for L, M in zip(runs, drops):
        for x in range(c, c + L + 2):
            g[R][x] = 0
        c2 = c + L
        g[R + 1][c2] = g[R + 1][c2 + 1] = 0
        for y in range(R, R + M + 1):
            g[y][c2] = 0
        B = R + M
        g[B][c2 + 1] = g[B - 1][c2 + 1] = 0
        R, c = B - 1, c2
    for x in range(c, n):
        g[R][x] = 0
        g[n - 1][x] = 0
    return g


p["tests"].append([_shaft_grid(50, 6, [6] * 6, [9] * 6)])
p["tests"].append([_shaft_grid(50, 10, [1, 2, 3, 1, 2, 4, 1, 3, 2, 2], [7, 4, 7, 5, 9, 4, 6, 5, 5, 6])])
_f = _fn(p)
while True:
    _g = _grid(_r, 50, 50, 0.09, clear=[(0, 0), (0, 1), (49, 48), (49, 49)])
    if _f(_g) > 97:
        break
p["tests"].append([_g])


def b_snake(grid):
    n = len(grid)
    st = ((0, 0), (0, 1))
    goal = ((n - 1, n - 2), (n - 1, n - 1))

    def free(c):
        return 0 <= c[0] < n and 0 <= c[1] < n and grid[c[0]][c[1]] == 0

    def nb(s):
        (tr, tc), (hr, hc) = s
        old = {(tr, tc), (hr, hc)}
        out = []
        for da, db in ((0, 1), (1, 0)):  # shift right / shift down
            a, b = (tr + da, tc + db), (hr + da, hc + db)
            if all(free(c) for c in (a, b) if c not in old):
                out.append((a, b))
        if tr == hr and free((tr + 1, tc)) and free((hr + 1, hc)):
            out.append(((tr, tc), (tr + 1, tc)))
        if tc == hc and free((tr, tc + 1)) and free((hr, hc + 1)):
            out.append(((tr, tc), (tr, tc + 1)))
        return out

    nodes = [((i, j), (i, j + 1)) for i in range(n) for j in range(n - 1)] + [((i, j), (i + 1, j)) for i in range(n - 1) for j in range(n)]
    nodes = [s for s in nodes if free(s[0]) and free(s[1])]
    return _bf(nodes, nb, st).get(goal, -1)


def g_snake(r):
    n = r.randint(2, 5)
    return [_grid(r, n, n, r.choice([0.1, 0.25, 0.4]), clear=[(0, 0), (0, 1), (n - 1, n - 2), (n - 1, n - 1)])]


def v_snake(tests):
    for t in tests:
        g = t["args"][0]
        _rect(g, 50, 50, (0, 1))
        n = len(g)
        assert n == len(g[0]) and n >= 2
        assert g[0][0] == g[0][1] == g[n - 1][n - 2] == g[n - 1][n - 1] == 0


CHECKS["snake-rotation-minimum-moves"] = (b_snake, g_snake, "exact")
VALIDATE["snake-rotation-minimum-moves"] = v_snake
