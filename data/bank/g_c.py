"""Problems: graphs, multi-source BFS and level BFS (nearest source, spreading, fire, territories). See data/lib.py for the registry."""
from lib import add, rnd, CHECKS, VALIDATE, gen_arr  # noqa: F401

DIRS = ((1, 0), (-1, 0), (0, 1), (0, -1))


# ------------------------------------------------------------------ helpers (tests only)
def _ref(p):
    ns = {}
    exec(p["solution"], ns)
    return ns[p["fn"]]


def _g(r, R, C, w):
    """Random grid; w is a list of (value, weight)."""
    vals = [v for v, _ in w]
    ws = [x for _, x in w]
    return [r.choices(vals, ws, k=C) for _ in range(R)]


def _scatter(r, g, items):
    """Write the given values on distinct random cells of g."""
    R, C = len(g), len(g[0])
    cells = r.sample([(i, j) for i in range(R) for j in range(C)], len(items))
    for (i, j), v in zip(cells, items):
        g[i][j] = v
    return g


def _check_grid(g, rmax, cmax, allowed, rmin=1, cmin=1):
    assert rmin <= len(g) <= rmax, "rows"
    assert all(len(row) == len(g[0]) for row in g), "ragged"
    assert cmin <= len(g[0]) <= cmax, "cols"
    for row in g:
        for v in row:
            assert v in allowed, ("cell value", v)


def _count(g, v):
    return sum(row.count(v) for row in g)


def _snake(R, C, closed=True):
    """Walls (1) with one winding corridor of open cells (0) through rows 1..R-2 and cols 1..C-2.
    Returns (grid, first_cell, last_cell). Needs R odd."""
    g = [[1] * C for _ in range(R)]
    cells = []
    for i in range(1, R - 1, 2):
        cols = list(range(1, C - 1))
        if (i // 2) % 2 == 1:
            cols.reverse()
        for j in cols:
            g[i][j] = 0
            cells.append((i, j))
        if i + 2 < R - 1:
            j = cols[-1]
            g[i + 1][j] = 0
            cells.append((i + 1, j))
    return g, cells[0], cells[-1]


def _simple_edges(r, n, m):
    pairs = set()
    m = min(m, n * (n - 1) // 2)
    while len(pairs) < m:
        a, b = r.randrange(n), r.randrange(n)
        if a != b:
            pairs.add((min(a, b), max(a, b)))
    return [list(x) if r.random() < 0.5 else [x[1], x[0]] for x in sorted(pairs)]


def _check_graph(n, edges, nmax, emax):
    assert 1 <= n <= nmax and len(edges) <= emax
    seen = set()
    for a, b in edges:
        assert 0 <= a < n and 0 <= b < n and a != b, "bad edge"
        k = (min(a, b), max(a, b))
        assert k not in seen, "duplicate edge"
        seen.add(k)


# =================================================================== EASY
# ---------------------------------------------------------------- BFS level sizes
p = add(
    id="graph-bfs-level-sizes", title="BFS Level Sizes", diff="Easy", topic="Graphs", tier="common",
    fn="bfsLevelSizes", params=[("n", "int"), ("edges", "int[][]"), ("src", "int")], ret="int[]", cmp="exact",
    desc="<p>An undirected graph has <code>n</code> nodes numbered <code>0</code> to <code>n - 1</code>. Each entry <code>edges[i] = [a, b]</code> is a connection between nodes <code>a</code> and <code>b</code>.</p><p>The <em>distance</em> of a node from <code>src</code> is the fewest connections you must follow to get there. Return an array <code>sizes</code> where <code>sizes[d]</code> is the number of nodes whose distance from <code>src</code> is exactly <code>d</code>. The array ends at the largest distance that occurs; nodes that cannot be reached from <code>src</code> are not counted anywhere.</p><pre>n = 7, src = 0\nedges = [[0,1], [0,2], [1,3], [2,3], [3,4], [5,6]]\n-> [1, 2, 1, 1]</pre><p>Node 0 is at distance 0, nodes 1 and 2 at distance 1, node 3 at distance 2 and node 4 at distance 3. Nodes 5 and 6 are in a different component.</p>",
    constraints=["1 &le; n &le; 3,000", "0 &le; edges.length &le; 3,000", "0 &le; a, b &lt; n, a &ne; b, and no pair of nodes is listed twice", "0 &le; src &lt; n"],
    hints=["The distance of a node is exactly the round in which a breadth-first search first reaches it.",
           "Run BFS from <code>src</code> but process the queue one <em>round</em> at a time: everything currently in the queue belongs to the same distance.",
           "Keep a list for the current level. Record its length, then build the next level from the unvisited neighbours of the current one. Stop when the next level is empty."],
    editorial=["Build adjacency lists, mark <code>src</code> as visited and put it in the first level. Repeat: append the size of the current level to the answer, then collect every not-yet-visited neighbour of the level's nodes (marking them visited as you add them) into the next level. The loop ends when a level comes out empty.",
               "A node is added the first time any node of the previous level touches it, and by the layered nature of BFS that is exactly its shortest distance. Every node and edge is looked at a constant number of times, so the time is O(n + m)."],
    time="O(n + m)", space="O(n + m)",
    solution='''def bfsLevelSizes(n, edges, src):
    adj = [[] for _ in range(n)]
    for a, b in edges:
        adj[a].append(b)
        adj[b].append(a)
    seen = [False] * n
    seen[src] = True
    level = [src]
    sizes = []
    while level:
        sizes.append(len(level))
        nxt = []
        for u in level:
            for v in adj[u]:
                if not seen[v]:
                    seen[v] = True
                    nxt.append(v)
        level = nxt
    return sizes
''',
    tests=[[7, [[0, 1], [0, 2], [1, 3], [2, 3], [3, 4], [5, 6]], 0], [1, [], 0], [2, [], 1], [2, [[0, 1]], 1],
           [5, [[0, 1], [0, 2], [0, 3], [0, 4]], 3], [4, [[0, 1], [1, 2], [2, 3]], 2],
           [4, [[0, 1], [0, 2], [0, 3], [1, 2], [1, 3], [2, 3]], 1], [6, [[0, 1], [1, 2], [2, 3], [3, 4], [4, 5], [5, 0]], 0],
           [8, [[0, 1], [1, 2], [3, 4], [4, 5], [5, 6], [3, 6], [6, 7]], 5], [3, [[0, 1]], 2],
           [9, [[0, 1], [0, 2], [1, 3], [1, 4], [2, 5], [2, 6], [3, 7], [4, 7], [6, 8]], 7]],
)
_r = rnd(9301)
_n = 3000
_perm = list(range(_n)); _r.shuffle(_perm)
p["tests"].append([_n, [[_perm[i], _perm[i + 1]] for i in range(_n - 1)], _perm[0]])  # one long path: 3000 levels of one node


def _layered(r, sizes, extra):
    levels, idx = [], 0
    for s in sizes:
        levels.append(list(range(idx, idx + s)))
        idx += s
    perm = list(range(idx))
    r.shuffle(perm)
    es = set()
    for k in range(1, len(levels)):
        for v in levels[k]:
            es.add((levels[k - 1][r.randrange(len(levels[k - 1]))], v))
    for _ in range(extra):
        k = r.randrange(len(levels))
        k2 = min(len(levels) - 1, k + r.randint(0, 1))  # same level or the next one: never shortens a distance
        a, b = r.choice(levels[k]), r.choice(levels[k2])
        if a != b and (a, b) not in es and (b, a) not in es:
            es.add((a, b))
    return idx, [[perm[a], perm[b]] for a, b in sorted(es)], perm[0]


_nn, _ee, _ss = _layered(_r, list(range(1, 65)), 600)  # levels of growing size 1, 2, ..., 64
p["tests"].append([_nn, _ee, _ss])
_n = 3000
p["tests"].append([_n, _simple_edges(_r, _n, 2400), 5])  # sparse random graph with many small components


def b_levels(n, edges, src):
    INF = 10 ** 9
    d = [INF] * n
    d[src] = 0
    changed = True
    while changed:
        changed = False
        for a, b in edges:
            if d[a] + 1 < d[b]:
                d[b] = d[a] + 1
                changed = True
            if d[b] + 1 < d[a]:
                d[a] = d[b] + 1
                changed = True
    mx = max(x for x in d if x < INF)
    return [sum(1 for x in d if x == k) for k in range(mx + 1)]


def g_levels(r):
    n = r.randint(1, 9)
    return [n, _simple_edges(r, n, r.randint(0, n + 3)), r.randrange(n)]


def v_levels(tests):
    for t in tests:
        n, edges, src = t["args"]
        _check_graph(n, edges, 3000, 3000)
        assert 0 <= src < n
        assert sum(t["expected"]) <= n and t["expected"][0] == 1 and all(x > 0 for x in t["expected"])


CHECKS["graph-bfs-level-sizes"] = (b_levels, g_levels, "exact")
VALIDATE["graph-bfs-level-sizes"] = v_levels

# ---------------------------------------------------------------- infected after t minutes
p = add(
    id="cells-infected-after-t-minutes", title="Cells Infected After T Minutes", diff="Easy", topic="Graphs", tier="common",
    fn="infectedCells", params=[("grid", "int[][]"), ("t", "int")], ret="int", cmp="exact",
    desc="<p>A <code>grid</code> describes a field: <code>0</code> is an open cell, <code>1</code> is a wall and <code>2</code> is a cell that is infected at minute 0 (there is at least one).</p><p>Every minute, each open cell that shares a side (up, down, left or right) with an infected cell becomes infected; all cells that qualify in a minute change at the same moment, and walls never change. Return the number of infected cells (the initial ones included) after exactly <code>t</code> minutes.</p><pre>grid = [[2,0,0],\n        [1,1,0],\n        [0,0,0]]\n\nt = 3  -> 4      (cells (0,0), (0,1), (0,2), (1,2))\nt = 4  -> 5</pre>",
    constraints=["1 &le; rows, cols &le; 60", "0 &le; t &le; 10,000", "grid[r][c] is 0, 1 or 2, and at least one cell is 2"],
    hints=["Infection moves one step per minute in all directions at once, so the minute a cell gets infected equals its distance from the nearest infected cell.",
           "Start one BFS with all initially infected cells in the queue and process it one level (one minute) at a time.",
           "Stop after <code>t</code> levels, or earlier if a level is empty. Count the initial cells plus every cell added in each processed level."],
    editorial=["This is a multi-source BFS with a depth limit. Put all cells with value 2 into the first frontier and mark them visited. For minute 1, 2, ..., t, build the next frontier from the unvisited open neighbours of the current one, add its size to the counter and make it the current frontier. If a frontier is ever empty, nothing else can be infected and the loop stops, which also makes a huge <code>t</code> cheap.",
               "Each cell enters a frontier at most once, so the running time is O(rows &times; cols) however large <code>t</code> is. Simulating minute by minute with a full scan of the grid would cost O(rows &times; cols) per minute."],
    time="O(R &middot; C)", space="O(R &middot; C)",
    solution='''def infectedCells(grid, t):
    rows, cols = len(grid), len(grid[0])
    seen = [[False] * cols for _ in range(rows)]
    frontier = []
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == 2:
                seen[r][c] = True
                frontier.append((r, c))
    count = len(frontier)
    minute = 0
    while frontier and minute < t:
        nxt = []
        for y, x in frontier:
            for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                ny, nx = y + dy, x + dx
                if 0 <= ny < rows and 0 <= nx < cols and not seen[ny][nx] and grid[ny][nx] == 0:
                    seen[ny][nx] = True
                    nxt.append((ny, nx))
        count += len(nxt)
        frontier = nxt
        minute += 1
    return count
''',
    tests=[[[[2, 0, 0], [1, 1, 0], [0, 0, 0]], 3], [[[2, 0, 0], [1, 1, 0], [0, 0, 0]], 4], [[[2, 0, 0], [1, 1, 0], [0, 0, 0]], 0],
           [[[2]], 5], [[[2, 1, 0]], 100], [[[0, 0, 2, 0, 0]], 1], [[[0, 0, 2, 0, 0]], 2], [[[2], [0], [0], [2]], 1],
           [[[2, 2], [2, 2]], 3], [[[0, 1, 0], [1, 2, 1], [0, 1, 0]], 7], [[[2, 0, 1, 0, 0], [0, 0, 1, 0, 2], [0, 0, 1, 0, 0]], 2],
           [[[1, 1, 1], [1, 2, 1], [1, 1, 1]], 4]],
)
_r = rnd(9302)
p["tests"].append([_scatter(_r, _g(_r, 60, 60, [(0, 7), (1, 3)]), [2, 2, 2]), 25])
_gg, _a, _b = _snake(59, 60)
_gg[_a[0]][_a[1]] = 2
p["tests"].append([_gg, 700])  # winding corridor of about 1,700 cells, only partly infected
p["tests"].append([_gg, 10000])  # the same corridor, infected completely
p["tests"].append([_scatter(_r, _g(_r, 60, 60, [(0, 1)]), [2]), 40])


def b_infect(grid, t):
    g = [row[:] for row in grid]
    R, C = len(g), len(g[0])
    for _ in range(min(t, R * C)):
        nxt = [row[:] for row in g]
        for i in range(R):
            for j in range(C):
                if g[i][j] == 0 and any(0 <= i + a < R and 0 <= j + b < C and g[i + a][j + b] == 2 for a, b in DIRS):
                    nxt[i][j] = 2
        g = nxt
    return sum(row.count(2) for row in g)


def g_infect(r):
    R, C = r.randint(1, 5), r.randint(1, 5)
    g = _g(r, R, C, [(0, 3), (1, 1)])
    _scatter(r, g, [2] * r.randint(1, min(2, R * C)))
    return [g, r.randint(0, 8)]


def v_infect(tests):
    for t in tests:
        g, tt = t["args"]
        _check_grid(g, 60, 60, (0, 1, 2))
        assert 0 <= tt <= 10000 and _count(g, 2) >= 1


CHECKS["cells-infected-after-t-minutes"] = (b_infect, g_infect, "exact")
VALIDATE["cells-infected-after-t-minutes"] = v_infect

# ---------------------------------------------------------------- nearest shelter per node
p = add(
    id="nearest-shelter-distance-per-node", title="Nearest Shelter for Every Town", diff="Easy", topic="Graphs", tier="common",
    fn="nearestShelter", params=[("n", "int"), ("edges", "int[][]"), ("shelters", "int[]")], ret="int[]", cmp="exact",
    desc="<p>A region has <code>n</code> towns numbered <code>0</code> to <code>n - 1</code>, joined by two-way roads: <code>edges[i] = [a, b]</code> is a road between towns <code>a</code> and <code>b</code>. The towns listed in <code>shelters</code> have a storm shelter.</p><p>Return an array <code>ans</code> of length <code>n</code> where <code>ans[v]</code> is the smallest number of roads you must drive to get from town <code>v</code> to <em>any</em> town with a shelter (<code>0</code> for a shelter town itself), or <code>-1</code> if no shelter can be reached from <code>v</code>.</p><pre>n = 6, edges = [[0,1], [1,2], [2,3], [4,5]], shelters = [0, 3]\n-> [0, 1, 1, 0, -1, -1]</pre>",
    constraints=["1 &le; n &le; 3,000", "0 &le; edges.length &le; 3,000; no road joins a town to itself and no pair is listed twice", "0 &le; shelters.length &le; n; the shelter towns are distinct"],
    hints=["Running a separate BFS from every town would be O(n &middot; (n + m)). Think about which towns the searches should start from instead.",
           "Reverse the question: BFS from the shelters, and the level in which a town is reached is its distance to the closest shelter.",
           "Put all shelters into the queue at distance 0 at once. Towns that are never reached keep the value -1."],
    editorial=["Roads are two-way, so the distance from a town to its nearest shelter equals the shortest distance from the set of shelters to the town. Initialise <code>ans</code> with -1, set it to 0 for every shelter and enqueue them all. Then run an ordinary BFS: when you pop a town, give every neighbour whose answer is still -1 the value <code>ans[town] + 1</code> and enqueue it.",
               "Because the queue always holds towns in nondecreasing distance, the first assignment to a town is its smallest possible distance, so the value -1 doubles as the visited flag. Time O(n + m), and towns in components without a shelter are simply never touched."],
    time="O(n + m)", space="O(n + m)",
    solution='''from collections import deque


def nearestShelter(n, edges, shelters):
    adj = [[] for _ in range(n)]
    for a, b in edges:
        adj[a].append(b)
        adj[b].append(a)
    ans = [-1] * n
    q = deque()
    for s in shelters:
        ans[s] = 0
        q.append(s)
    while q:
        u = q.popleft()
        for v in adj[u]:
            if ans[v] == -1:
                ans[v] = ans[u] + 1
                q.append(v)
    return ans
''',
    tests=[[6, [[0, 1], [1, 2], [2, 3], [4, 5]], [0, 3]], [1, [], [0]], [1, [], []], [3, [[0, 1], [1, 2]], []],
           [4, [[0, 1], [1, 2], [2, 3]], [0, 1, 2, 3]], [5, [[0, 1], [1, 2], [2, 3], [3, 4]], [2]],
           [6, [[0, 1], [0, 2], [0, 3], [0, 4], [0, 5]], [5]], [7, [[0, 1], [1, 2], [2, 0], [3, 4], [5, 6]], [1, 6]],
           [8, [[0, 1], [1, 2], [2, 3], [3, 4], [4, 5], [5, 6], [6, 7], [7, 0]], [0, 4]], [2, [], [1]]],
)
_r = rnd(9303)
_n = 3000
_perm = list(range(_n)); _r.shuffle(_perm)
p["tests"].append([_n, [[_perm[i], _perm[i + 1]] for i in range(_n - 1)], [_perm[0], _perm[1500]]])
p["tests"].append([_n, _simple_edges(_r, _n, 3000), sorted(_r.sample(range(_n), 12))])
p["tests"].append([_n, _simple_edges(_r, _n, 1800), [7]])


def b_shelter(n, edges, shelters):
    adj = [[] for _ in range(n)]
    for a, b in edges:
        adj[a].append(b)
        adj[b].append(a)
    sh = set(shelters)
    out = []
    for v in range(n):
        dist = {v: 0}
        todo = [v]
        res = -1
        while todo and res == -1:
            nxt = []
            for u in todo:
                if u in sh:
                    res = dist[u]
                    break
                for w in adj[u]:
                    if w not in dist:
                        dist[w] = dist[u] + 1
                        nxt.append(w)
            todo = nxt
        out.append(res)
    return out


def g_shelter(r):
    n = r.randint(1, 9)
    return [n, _simple_edges(r, n, r.randint(0, n + 2)), sorted(r.sample(range(n), r.randint(0, min(3, n))))]


def v_shelter(tests):
    for t in tests:
        n, edges, sh = t["args"]
        _check_graph(n, edges, 3000, 3000)
        assert len(set(sh)) == len(sh) and all(0 <= s < n for s in sh)


CHECKS["nearest-shelter-distance-per-node"] = (b_shelter, g_shelter, "exact")
VALIDATE["nearest-shelter-distance-per-node"] = v_shelter

# =================================================================== MEDIUM
# ---------------------------------------------------------------- distance to nearest zero
p = add(
    id="distance-to-nearest-zero-cell", title="Distance to the Nearest Zero", diff="Medium", topic="Graphs", tier="must",
    fn="nearestZeroDistance", params=[("mat", "int[][]")], ret="int[][]", cmp="exact",
    desc="<p>A matrix <code>mat</code> contains only <code>0</code>s and <code>1</code>s, and at least one <code>0</code>. For every cell, find the distance to the closest cell holding <code>0</code>, where moving to a cell that shares a side (up, down, left or right) counts as one step. Cells are not blocked in any way.</p><p>Return a matrix of the same shape with these distances.</p><pre>mat = [[0,0,0],\n       [0,1,0],\n       [1,1,1]]\n\nresult = [[0,0,0],\n          [0,1,0],\n          [1,2,1]]</pre>",
    constraints=["1 &le; rows, cols &le; 60", "mat[r][c] is 0 or 1", "At least one cell is 0"],
    hints=["A brute force that scans the whole matrix for the nearest zero from every cell is O((rows &times; cols)<sup>2</sup>). Try to share work between cells.",
           "Searching <em>from</em> the zeros is better than searching <em>to</em> them. What if all zeros were the starting points of a single BFS?",
           "Seed the queue with every zero at distance 0. When you take a cell from the queue, each unvisited neighbour gets the cell's distance plus one. The first time a cell is reached is its smallest distance."],
    editorial=["Start a BFS whose queue initially contains every cell with value 0 (distance 0); all other cells are marked as not yet reached. Pop a cell, and for each neighbour that has not been reached yet set its distance to the popped distance plus one and push it. BFS expands in rings of increasing distance around the whole set of zeros, so a cell is first reached along a shortest path to its nearest zero.",
               "Every cell is queued once, giving O(rows &times; cols). A two-pass dynamic programming sweep also works: one pass from the top-left taking the minimum of the upper and left neighbours plus one, then one pass from the bottom-right using the lower and right neighbours."],
    time="O(R &middot; C)", space="O(R &middot; C)",
    solution='''from collections import deque


def nearestZeroDistance(mat):
    rows, cols = len(mat), len(mat[0])
    dist = [[-1] * cols for _ in range(rows)]
    q = deque()
    for r in range(rows):
        for c in range(cols):
            if mat[r][c] == 0:
                dist[r][c] = 0
                q.append((r, c))
    while q:
        y, x = q.popleft()
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            ny, nx = y + dy, x + dx
            if 0 <= ny < rows and 0 <= nx < cols and dist[ny][nx] == -1:
                dist[ny][nx] = dist[y][x] + 1
                q.append((ny, nx))
    return dist
''',
    tests=[[[[0, 0, 0], [0, 1, 0], [1, 1, 1]]], [[[0]]], [[[0, 1, 1, 1, 1]]], [[[1], [1], [1], [0]]], [[[0, 0], [0, 0]]],
           [[[1, 1, 1], [1, 0, 1], [1, 1, 1]]], [[[0, 1, 0], [1, 1, 1], [0, 1, 0]]], [[[1, 1, 1, 1], [1, 1, 1, 1], [1, 1, 1, 0]]],
           [[[1, 0, 1, 1, 1, 0, 1], [1, 1, 1, 1, 1, 1, 1]]], [[[1, 1, 1], [1, 1, 1], [1, 1, 1], [1, 1, 1], [0, 1, 1]]]],
)
_r = rnd(9304)
_m = [[1] * 60 for _ in range(60)]; _m[0][0] = 0
p["tests"].append([_m])
p["tests"].append([_scatter(_r, [[1] * 60 for _ in range(60)], [0] * 40)])
_m = [[1] * 59 for _ in range(60)]; _m[30][29] = 0; _m[59][58] = 0
p["tests"].append([_m])


def b_zero(mat):
    R, C = len(mat), len(mat[0])
    zs = [(i, j) for i in range(R) for j in range(C) if mat[i][j] == 0]
    return [[min(abs(i - a) + abs(j - b) for a, b in zs) for j in range(C)] for i in range(R)]


def g_zero(r):
    R, C = r.randint(1, 6), r.randint(1, 6)
    g = _g(r, R, C, [(0, 1), (1, 3)])
    _scatter(r, g, [0])
    return [g]


def v_zero(tests):
    for t in tests:
        _check_grid(t["args"][0], 60, 60, (0, 1))
        assert _count(t["args"][0], 0) >= 1


CHECKS["distance-to-nearest-zero-cell"] = (b_zero, g_zero, "exact")
VALIDATE["distance-to-nearest-zero-cell"] = v_zero

# ---------------------------------------------------------------- farthest water from land
p = add(
    id="farthest-water-cell-from-land", title="Farthest Water Cell From Land", diff="Medium", topic="Graphs", tier="common",
    fn="maxDistanceFromLand", params=[("grid", "int[][]")], ret="int", cmp="exact",
    desc="<p>A map <code>grid</code> has <code>0</code> for water and <code>1</code> for land. The <em>distance</em> between two cells at <code>(r1, c1)</code> and <code>(r2, c2)</code> is <code>|r1 - r2| + |c1 - c2|</code>, which is the number of up/down/left/right steps between them.</p><p>Find the water cell whose distance to the closest land cell is as large as possible, and return that distance. If the map has no water or no land at all, return <code>-1</code>.</p><pre>grid = [[1,0,1],\n        [0,0,0],\n        [1,0,1]]  -> 2\n\ngrid = [[1,0,0],\n        [0,0,0],\n        [0,0,0]]  -> 4</pre><p>In the first map the middle cell is two steps from every corner; in the second the opposite corner is four steps from the only land cell.</p>",
    constraints=["1 &le; rows, cols &le; 60", "grid[r][c] is 0 or 1"],
    hints=["First deal with the degenerate maps (all water or all land). Then think about what 'closest land' means for all water cells simultaneously.",
           "Compute, for every water cell, its distance to the nearest land cell with one BFS that starts from all land cells together.",
           "BFS visits cells in nondecreasing distance, so the distance of the last cell taken from the queue is the maximum. No separate max tracking is needed."],
    editorial=["If there is no land or no water, return -1. Otherwise push all land cells into a queue with distance 0 and run a BFS over the whole grid (no obstacles exist, so every cell is reachable). Each water cell gets the distance of the first wave that reaches it, which is its distance to the nearest land.",
               "The answer is the largest distance assigned. Since cells leave the queue in order of increasing distance, the final popped cell has the maximum. This runs in O(rows &times; cols); the naive approach of comparing every water cell with every land cell is quadratic in the number of cells."],
    time="O(R &middot; C)", space="O(R &middot; C)",
    solution='''from collections import deque


def maxDistanceFromLand(grid):
    rows, cols = len(grid), len(grid[0])
    dist = [[-1] * cols for _ in range(rows)]
    q = deque()
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == 1:
                dist[r][c] = 0
                q.append((r, c))
    if not q or len(q) == rows * cols:
        return -1
    last = 0
    while q:
        y, x = q.popleft()
        last = dist[y][x]
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            ny, nx = y + dy, x + dx
            if 0 <= ny < rows and 0 <= nx < cols and dist[ny][nx] == -1:
                dist[ny][nx] = last + 1
                q.append((ny, nx))
    return last
''',
    tests=[[[[1, 0, 1], [0, 0, 0], [1, 0, 1]]], [[[1, 0, 0], [0, 0, 0], [0, 0, 0]]], [[[1]]], [[[0]]], [[[0, 0], [0, 0]]],
           [[[1, 1], [1, 1]]], [[[0, 1, 0]]], [[[1], [0], [0], [0], [0]]], [[[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 1]]],
           [[[1, 0, 0, 0, 1], [0, 0, 0, 0, 0], [0, 0, 1, 0, 0]]], [[[0, 1, 0], [1, 0, 1], [0, 1, 0]]]],
)
_r = rnd(9305)
p["tests"].append([_scatter(_r, [[0] * 60 for _ in range(60)], [1] * 4)])
p["tests"].append([_scatter(_r, [[0] * 60 for _ in range(60)], [1])])
p["tests"].append([_g(_r, 60, 60, [(0, 20), (1, 1)])])


def b_land(grid):
    R, C = len(grid), len(grid[0])
    land = [(i, j) for i in range(R) for j in range(C) if grid[i][j] == 1]
    water = [(i, j) for i in range(R) for j in range(C) if grid[i][j] == 0]
    if not land or not water:
        return -1
    return max(min(abs(i - a) + abs(j - b) for a, b in land) for i, j in water)


def g_land(r):
    R, C = r.randint(1, 6), r.randint(1, 6)
    return [_g(r, R, C, [(0, 3), (1, 1)])]


def v_land(tests):
    for t in tests:
        _check_grid(t["args"][0], 60, 60, (0, 1))


CHECKS["farthest-water-cell-from-land"] = (b_land, g_land, "exact")
VALIDATE["farthest-water-cell-from-land"] = v_land

# ---------------------------------------------------------------- territory split
p = add(
    id="territory-split-by-nearest-base", title="Territory Split by Nearest Base", diff="Medium", topic="Graphs", tier="extra",
    fn="splitTerritory", params=[("grid", "int[][]")], ret="int[]", cmp="exact",
    desc="<p>Two rival clans have built bases on a <code>grid</code>: <code>0</code> is open ground, <code>1</code> is a wall, <code>2</code> is a base of clan A and <code>3</code> is a base of clan B. Each clan has at least one base. Walking moves one step up, down, left or right and never enters a wall.</p><p>The <em>walking distance</em> from a clan to a cell is the smallest number of steps from any of its bases to that cell (bases and open ground are both walkable). Every non-wall cell belongs to the clan that is strictly closer, or to nobody in case of a tie or when neither clan can reach it.</p><p>Return <code>[a, b, tie, none]</code>: the number of non-wall cells strictly closer to A, strictly closer to B, equally far from both, and unreachable for both.</p><pre>grid = [[2,0,0,0,0,3],\n        [1,1,0,1,1,1],\n        [0,0,0,0,0,0]]\n-> [10, 3, 0, 0]</pre><p>The bottom row hangs off the opening in the middle: it is 4 steps from A's base but 5 from B's, so it all goes to A.</p>",
    constraints=["1 &le; rows, cols &le; 60", "grid[r][c] is 0, 1, 2 or 3", "At least one cell is 2 and at least one cell is 3"],
    hints=["For one single cell you would need its distance to the nearest A base and to the nearest B base, then compare. How can you get these two distance tables for the whole grid cheaply?",
           "Distance to the <em>nearest</em> base of a clan is a multi-source BFS: start from all bases of that clan together. Do it once for A and once for B.",
           "With the two distance grids <code>dA</code> and <code>dB</code> (use infinity for unreachable), classify each non-wall cell: <code>dA &lt; dB</code> goes to A, <code>dB &lt; dA</code> to B, equal finite values are ties, and both infinite means unreachable."],
    editorial=["Run a multi-source BFS from all cells equal to 2 to obtain <code>dA</code>, and another from all cells equal to 3 to obtain <code>dB</code>. Walls are never entered, so their distance stays infinite and they must be skipped when counting. For every other cell compare <code>dA</code> and <code>dB</code>: the smaller one wins, equal finite values count as a tie, and two infinities mean that no base can reach the cell.",
               "Each BFS touches every cell at most once, so the total time is O(rows &times; cols). It is also possible to run a single BFS with both clans in the queue and a label per cell (A, B or tie), but handling a cell that is reached by both clans in the same round makes the code more delicate than two plain searches."],
    time="O(R &middot; C)", space="O(R &middot; C)",
    solution='''from collections import deque


def splitTerritory(grid):
    rows, cols = len(grid), len(grid[0])
    INF = float("inf")

    def bfs(kind):
        dist = [[INF] * cols for _ in range(rows)]
        q = deque()
        for r in range(rows):
            for c in range(cols):
                if grid[r][c] == kind:
                    dist[r][c] = 0
                    q.append((r, c))
        while q:
            y, x = q.popleft()
            for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                ny, nx = y + dy, x + dx
                if 0 <= ny < rows and 0 <= nx < cols and grid[ny][nx] != 1 and dist[ny][nx] == INF:
                    dist[ny][nx] = dist[y][x] + 1
                    q.append((ny, nx))
        return dist

    da, db = bfs(2), bfs(3)
    a = b = tie = none = 0
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == 1:
                continue
            if da[r][c] == INF and db[r][c] == INF:
                none += 1
            elif da[r][c] < db[r][c]:
                a += 1
            elif db[r][c] < da[r][c]:
                b += 1
            else:
                tie += 1
    return [a, b, tie, none]
''',
    tests=[[[[2, 0, 0, 0, 0, 3], [1, 1, 0, 1, 1, 1], [0, 0, 0, 0, 0, 0]]], [[[2, 3]]], [[[2, 0, 3]]], [[[2, 0, 0, 3]]],
           [[[2, 1, 3]]], [[[2, 0, 0, 0, 0, 0, 3]]], [[[3, 0, 0, 0, 0, 2], [0, 0, 0, 0, 0, 0]]],
           [[[2, 0, 0], [0, 1, 0], [0, 0, 3]]], [[[2, 0, 1, 0, 3], [0, 0, 1, 0, 0], [1, 1, 1, 0, 0]]],
           [[[2, 2, 0, 3, 3], [0, 0, 0, 0, 0], [3, 0, 0, 0, 2]]], [[[0, 0, 0], [0, 2, 0], [0, 0, 0], [0, 3, 0]]]],
)
_r = rnd(9306)
p["tests"].append([_scatter(_r, _g(_r, 60, 60, [(0, 7), (1, 2)]), [2, 2, 2, 3, 3, 3])])
p["tests"].append([_scatter(_r, _g(_r, 60, 60, [(0, 1)]), [2] * 5 + [3] * 5)])
p["tests"].append([_scatter(_r, _g(_r, 60, 59, [(0, 3), (1, 2)]), [2, 3])])


def b_terr(grid):
    R, C = len(grid), len(grid[0])
    INF = 10 ** 9

    def dists(src):
        d = {src: 0}
        todo = [src]
        while todo:
            nxt = []
            for (i, j) in todo:
                for a, b in DIRS:
                    q = (i + a, j + b)
                    if 0 <= q[0] < R and 0 <= q[1] < C and grid[q[0]][q[1]] != 1 and q not in d:
                        d[q] = d[(i, j)] + 1
                        nxt.append(q)
            todo = nxt
        return d

    A = [dists((i, j)) for i in range(R) for j in range(C) if grid[i][j] == 2]
    B = [dists((i, j)) for i in range(R) for j in range(C) if grid[i][j] == 3]
    res = [0, 0, 0, 0]
    for i in range(R):
        for j in range(C):
            if grid[i][j] == 1:
                continue
            xa = min((d.get((i, j), INF) for d in A), default=INF)
            xb = min((d.get((i, j), INF) for d in B), default=INF)
            if xa == INF and xb == INF:
                res[3] += 1
            elif xa < xb:
                res[0] += 1
            elif xb < xa:
                res[1] += 1
            else:
                res[2] += 1
    return res


def g_terr(r):
    R, C = r.randint(1, 5), r.randint(2, 6)
    g = _g(r, R, C, [(0, 4), (1, 2)])
    k = 2 if R * C >= 4 else 1
    _scatter(r, g, [2] * r.randint(1, k) + [3] * r.randint(1, k))
    return [g]


def v_terr(tests):
    for t in tests:
        g = t["args"][0]
        _check_grid(g, 60, 60, (0, 1, 2, 3))
        assert _count(g, 2) >= 1 and _count(g, 3) >= 1
        assert sum(t["expected"]) == sum(len(row) for row in g) - _count(g, 1)


CHECKS["territory-split-by-nearest-base"] = (b_terr, g_terr, "exact")
VALIDATE["territory-split-by-nearest-base"] = v_terr

# ---------------------------------------------------------------- escape the spreading fire
p = add(
    id="escape-the-spreading-fire-maze", title="Escape the Spreading Fire", diff="Medium", topic="Graphs", tier="common",
    fn="escapeMinutes", params=[("grid", "int[][]")], ret="int", cmp="exact",
    desc="<p>You are trapped in a maze given as a <code>grid</code>: <code>0</code> is open floor, <code>1</code> is a wall, <code>2</code> is a cell on fire and <code>3</code> is you (exactly one such cell). Fire may start in several places, or in none.</p><p>Time passes in minutes. In each minute you first move to a side-adjacent open cell that is not on fire (walls and burning cells cannot be entered; you may also stand still), and <em>then</em> the fire spreads to every non-wall cell that shares a side with a burning cell. If the fire reaches the cell you are standing on, you are lost. Open cells that are not burning are the only places where you can stand.</p><p>You get out by stepping off the grid from a border cell, which takes one minute like any other move. Return the fewest minutes needed to get out, or <code>-1</code> if it cannot be done.</p><pre>grid = [[1,1,1,1,1,1,1],\n        [0,0,0,3,0,0,1],\n        [1,1,1,0,1,1,1],\n        [1,1,1,2,1,1,1]]\n-> 4</pre><p>The fire climbs towards you and reaches your starting cell in minute 3. You run left: three moves reach the border cell (1,0) and a fourth takes you outside. Going right leads into a dead end.</p>",
    constraints=["1 &le; rows, cols &le; 60", "grid[r][c] is 0, 1, 2 or 3, and exactly one cell is 3", "Your starting cell is never on fire at minute 0"],
    hints=["The fire spreads at a known speed: it reaches every cell at a fixed minute, independent of what you do. How could you compute that for all cells at once?",
           "Run a multi-source BFS from all burning cells to get <code>fire[cell]</code>, the minute in which each cell starts burning (infinity if never).",
           "Now BFS from your position. You may enter a cell at minute <code>d</code> only if <code>d &lt; fire[cell]</code> (if the fire arrives in the same minute you move in, it catches you). The first time you reach a border cell at minute <code>d</code>, the answer is <code>d + 1</code>."],
    editorial=["Because the fire's progress does not depend on you, compute it first with a BFS that starts from all fire cells at minute 0 and spreads through every cell that is not a wall. This gives the burn minute of each cell.",
               "Then run a second BFS from your cell. Arriving at a neighbour at minute <code>d</code> is allowed only when <code>d &lt; fire[neighbour]</code>: the fire spreads after you move, so it must not reach that cell in the same minute. Waiting is never useful, since the fire only gets closer, so a plain shortest-path search is enough. The first border cell reached at minute <code>d</code> lets you step outside at minute <code>d + 1</code>; if your start is on the border the answer is 1. If the search ends with no border cell reached, return -1. Both searches are O(rows &times; cols)."],
    time="O(R &middot; C)", space="O(R &middot; C)",
    solution='''from collections import deque


def escapeMinutes(grid):
    rows, cols = len(grid), len(grid[0])
    INF = 10 ** 9
    fire = [[INF] * cols for _ in range(rows)]
    q = deque()
    start = None
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == 2:
                fire[r][c] = 0
                q.append((r, c))
            elif grid[r][c] == 3:
                start = (r, c)
    while q:
        y, x = q.popleft()
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            ny, nx = y + dy, x + dx
            if 0 <= ny < rows and 0 <= nx < cols and grid[ny][nx] != 1 and fire[ny][nx] == INF:
                fire[ny][nx] = fire[y][x] + 1
                q.append((ny, nx))

    def on_border(y, x):
        return y in (0, rows - 1) or x in (0, cols - 1)

    if on_border(*start):
        return 1
    dist = {start: 0}
    q = deque([start])
    while q:
        y, x = q.popleft()
        d = dist[(y, x)] + 1
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            ny, nx = y + dy, x + dx
            if 0 <= ny < rows and 0 <= nx < cols and grid[ny][nx] != 1 and (ny, nx) not in dist and d < fire[ny][nx]:
                if on_border(ny, nx):
                    return d + 1
                dist[(ny, nx)] = d
                q.append((ny, nx))
    return -1
''',
    tests=[[[[1, 1, 1, 1, 1, 1, 1], [0, 0, 0, 3, 0, 0, 1], [1, 1, 1, 0, 1, 1, 1], [1, 1, 1, 2, 1, 1, 1]]],
           [[[3]]], [[[1, 1, 1], [1, 3, 1], [1, 1, 1]]], [[[2, 0, 3, 0, 0]]], [[[0, 0, 3, 0, 2]]],
           [[[0, 3, 0, 2]]], [[[1, 0, 1], [0, 3, 0], [1, 2, 1]]], [[[1, 0, 1], [1, 3, 1], [1, 0, 1]]],
           [[[1, 1, 1, 1, 1], [1, 3, 0, 0, 1], [1, 0, 1, 0, 1], [1, 0, 1, 0, 1], [1, 2, 1, 0, 1], [1, 1, 1, 0, 1]]],
           [[[1, 1, 0, 1, 1], [1, 0, 0, 0, 1], [1, 0, 3, 0, 1], [1, 0, 0, 0, 1], [1, 1, 1, 1, 1]]],
           [[[1, 1, 0, 1, 1], [1, 2, 0, 0, 1], [1, 0, 3, 0, 1], [1, 0, 0, 0, 1], [1, 1, 1, 1, 1]]]],
)
_r = rnd(9307)
_gg, _a, _b = _snake(59, 60)
_gg[_a[0]][_a[1]] = 2
_gg[_a[0]][_a[1] + 1] = 3
_gg[_b[0] + 1][_b[1]] = 0  # exit on the bottom border at the far end of the corridor
p["tests"].append([_gg])  # fire right behind you in a 1,700-cell corridor: still safe, answer is the corridor length + 1
_g2 = [row[:] for row in _gg]
_g2[_b[0] + 1][_b[1]] = 2  # fire waiting at the exit end: you and the fire meet in the corridor
p["tests"].append([_g2])
_ref_esc = _ref(p)
for _k in range(200):
    _g3 = _scatter(_r, _g(_r, 60, 60, [(0, 7), (1, 3)]), [3] + [2] * 6)
    if _g3[0][0] != 3 and _ref_esc(_g3) > 3 and not any(3 in row for row in (_g3[0], _g3[-1])) and all(row[0] != 3 and row[-1] != 3 for row in _g3):
        break
p["tests"].append([_g3])
for _k in range(200):
    _g4 = _scatter(_r, _g(_r, 40, 40, [(0, 5), (1, 4)]), [3] + [2] * 3)
    if _ref_esc(_g4) == -1 and all(row[0] != 3 and row[-1] != 3 for row in _g4) and 3 not in _g4[0] and 3 not in _g4[-1]:
        break
p["tests"].append([_g4])


def b_escape(grid):
    R, C = len(grid), len(grid[0])
    F = {(i, j) for i in range(R) for j in range(C) if grid[i][j] == 2}
    P = {(i, j) for i in range(R) for j in range(C) if grid[i][j] == 3}
    for t in range(1, R * C + 5):
        if any(i in (0, R - 1) or j in (0, C - 1) for i, j in P):
            return t
        P2 = set()
        for i, j in P:
            for a, b in DIRS:
                q = (i + a, j + b)
                if 0 <= q[0] < R and 0 <= q[1] < C and grid[q[0]][q[1]] != 1 and q not in F:
                    P2.add(q)
        F2 = set(F)
        for i, j in F:
            for a, b in DIRS:
                q = (i + a, j + b)
                if 0 <= q[0] < R and 0 <= q[1] < C and grid[q[0]][q[1]] != 1:
                    F2.add(q)
        F = F2
        P = P2 - F
        if not P:
            return -1
    return -1


def g_escape(r):
    R, C = r.randint(1, 6), r.randint(1, 6)
    g = _g(r, R, C, [(0, 5), (1, 2)])
    _scatter(r, g, [3] + [2] * r.randint(0, min(2, R * C - 1)))
    return [g]


def v_escape(tests):
    for t in tests:
        g = t["args"][0]
        _check_grid(g, 60, 60, (0, 1, 2, 3))
        assert _count(g, 3) == 1


CHECKS["escape-the-spreading-fire-maze"] = (b_escape, g_escape, "exact")
VALIDATE["escape-the-spreading-fire-maze"] = v_escape

# ---------------------------------------------------------------- safest path away from thieves
p = add(
    id="safest-path-away-from-thieves", title="Safest Path Away From Thieves", diff="Medium", topic="Graphs", tier="common",
    fn="maxSafeness", params=[("grid", "int[][]")], ret="int", cmp="exact",
    desc="<p>A square <code>grid</code> of size <code>n &times; n</code> contains <code>1</code> where a thief stands and <code>0</code> elsewhere; there is at least one thief. The <em>safeness</em> of a cell is its Manhattan distance <code>|r1 - r2| + |c1 - c2|</code> to the closest thief.</p><p>You walk from the top-left cell <code>(0, 0)</code> to the bottom-right cell <code>(n - 1, n - 1)</code>, each step moving to a side-adjacent cell (you may step on any cell, including a thief's). The safeness of a walk is the <em>smallest</em> cell safeness along it, start and end included. Return the largest safeness any walk can have.</p><pre>grid = [[0,0,1],\n        [0,0,0],\n        [0,0,0]]\n-> 2\n\ngrid = [[1,0,0],\n        [0,0,0],\n        [0,0,1]]\n-> 0</pre><p>In the first grid, going down the left column and along the bottom row keeps you at distance 2 or more from the thief. In the second, a thief stands on the start cell.</p>",
    constraints=["1 &le; n &le; 60", "grid[r][c] is 0 or 1", "At least one cell is 1"],
    hints=["Split the task in two: first learn how safe each cell is, then find the best route given those numbers.",
           "The safeness of every cell comes from one multi-source BFS that starts at all thieves. After that the problem is a 'maximise the minimum along the path' search.",
           "Either binary search on the answer <code>s</code> (can you walk from start to end using only cells with safeness &ge; <code>s</code>?), or run a Dijkstra-like search with a max-heap where a walk to a cell is worth the minimum safeness seen so far."],
    editorial=["Run a BFS from all thieves to fill <code>safe[r][c]</code>. This is the Manhattan distance to the nearest thief because nothing blocks movement.",
               "To maximise the minimum along a path, use a best-first search: keep a max-heap of cells keyed by the best safeness with which they can be reached, starting with <code>(0, 0)</code> at <code>safe[0][0]</code>. When a cell is popped, each neighbour can be reached with <code>min(current, safe[neighbour])</code>; push it if that beats the best value known for the neighbour. The value at which the bottom-right corner is first popped is the answer. This costs O(n<sup>2</sup> log n).",
               "An equivalent approach is binary search on <code>s</code> with a flood fill restricted to cells of safeness at least <code>s</code>, which is O(n<sup>2</sup> log n) as well."],
    time="O(n&sup2; log n)", space="O(n&sup2;)",
    solution='''import heapq
from collections import deque


def maxSafeness(grid):
    n = len(grid)
    safe = [[-1] * n for _ in range(n)]
    q = deque()
    for r in range(n):
        for c in range(n):
            if grid[r][c] == 1:
                safe[r][c] = 0
                q.append((r, c))
    while q:
        y, x = q.popleft()
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            ny, nx = y + dy, x + dx
            if 0 <= ny < n and 0 <= nx < n and safe[ny][nx] == -1:
                safe[ny][nx] = safe[y][x] + 1
                q.append((ny, nx))
    best = [[-1] * n for _ in range(n)]
    best[0][0] = safe[0][0]
    heap = [(-safe[0][0], 0, 0)]
    while heap:
        neg, y, x = heapq.heappop(heap)
        s = -neg
        if s < best[y][x]:
            continue
        if y == n - 1 and x == n - 1:
            return s
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            ny, nx = y + dy, x + dx
            if 0 <= ny < n and 0 <= nx < n:
                ns = min(s, safe[ny][nx])
                if ns > best[ny][nx]:
                    best[ny][nx] = ns
                    heapq.heappush(heap, (-ns, ny, nx))
    return 0
''',
    tests=[[[[0, 0, 1], [0, 0, 0], [0, 0, 0]]], [[[1, 0, 0], [0, 0, 0], [0, 0, 1]]], [[[1]]], [[[1, 0], [0, 0]]],
           [[[0, 0], [0, 1]]], [[[0, 1], [0, 0]]], [[[0, 0, 0], [0, 1, 0], [0, 0, 0]]],
           [[[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 1]]], [[[0, 0, 0, 0, 0], [1, 1, 1, 1, 0], [0, 0, 0, 0, 0], [0, 1, 1, 1, 1], [0, 0, 0, 0, 0]]],
           [[[0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 1, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0]]],
           [[[0, 0, 0, 0, 1], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [1, 0, 0, 0, 0]]]],
)
_r = rnd(9308)
p["tests"].append([_scatter(_r, [[0] * 60 for _ in range(60)], [1] * 8)])
p["tests"].append([_scatter(_r, [[0] * 60 for _ in range(60)], [1])])
_m = [[0] * 60 for _ in range(60)]
for _i in range(1, 59, 2):  # thief walls with a single gap, forcing a zig-zag
    for _j in range(60):
        _m[_i][_j] = 1 if _j != (59 if (_i // 2) % 2 == 0 else 0) else 0
p["tests"].append([_m])


def b_safe(grid):
    n = len(grid)
    th = [(i, j) for i in range(n) for j in range(n) if grid[i][j] == 1]
    d = [[min(abs(i - a) + abs(j - b) for a, b in th) for j in range(n)] for i in range(n)]
    for s in range(max(max(row) for row in d), -1, -1):
        if d[0][0] < s or d[n - 1][n - 1] < s:
            continue
        seen = {(0, 0)}
        todo = [(0, 0)]
        while todo:
            i, j = todo.pop()
            for a, b in DIRS:
                q = (i + a, j + b)
                if 0 <= q[0] < n and 0 <= q[1] < n and q not in seen and d[q[0]][q[1]] >= s:
                    seen.add(q)
                    todo.append(q)
        if (n - 1, n - 1) in seen:
            return s
    return 0


def g_safe(r):
    n = r.randint(1, 6)
    g = _g(r, n, n, [(0, 6), (1, 1)])
    _scatter(r, g, [1])
    return [g]


def v_safe(tests):
    for t in tests:
        g = t["args"][0]
        _check_grid(g, 60, 60, (0, 1))
        assert len(g) == len(g[0]) and _count(g, 1) >= 1


CHECKS["safest-path-away-from-thieves"] = (b_safe, g_safe, "exact")
VALIDATE["safest-path-away-from-thieves"] = v_safe

# =================================================================== HARD
# ---------------------------------------------------------------- minimum total walk to all buildings
p = add(
    id="min-total-walk-to-all-buildings", title="Minimum Total Walk to All Buildings", diff="Hard", topic="Graphs", tier="common",
    fn="shortestTotalDistance", params=[("grid", "int[][]")], ret="int", cmp="exact",
    desc="<p>A <code>grid</code> shows a town: <code>0</code> is an empty plot, <code>1</code> is a building and <code>2</code> is an obstacle. There is at least one building.</p><p>You want to put a new bakery on an empty plot so that the sum of the walking distances from the bakery to <em>every</em> building is as small as possible. You walk one step at a time up, down, left or right through empty plots only (never through buildings or obstacles); the last step of a walk goes onto the building itself. The distance to a building is the number of steps of the shortest such walk.</p><p>Return the smallest possible sum, or <code>-1</code> if no empty plot can reach all the buildings.</p><pre>grid = [[1,0,2,0,1],\n        [0,0,0,0,0],\n        [0,0,1,0,0]]\n-> 7</pre><p>The plot at row 1, column 2 is at distance 3, 3 and 1 from the three buildings.</p>",
    constraints=["1 &le; rows, cols &le; 40", "grid[r][c] is 0, 1 or 2", "1 &le; number of buildings &le; 50"],
    hints=["Try every empty plot and measure its distance to every building. How slow is that, and is there a way to share work?",
           "Running one BFS per <em>building</em> (not per plot) gives the distance from that building to all empty plots. A plot's total is the sum over the BFS runs.",
           "While running these BFS passes, also count for every plot how many buildings reached it. Only plots reached by all buildings are valid, and the answer is the smallest total among them."],
    editorial=["The walking distance from a plot to a building equals the distance from the building to the plot, so BFS from each building through empty plots fills in one distance for every plot it can reach. Keep two tables: <code>total[plot]</code>, the sum of the distances found so far, and <code>reach[plot]</code>, the number of buildings whose BFS visited it.",
               "After all <code>B</code> buildings are processed, the candidates are the empty plots with <code>reach == B</code>. Return the minimum of their totals, or -1 if there is none. The cost is O(B &middot; rows &middot; cols), which is far better than a BFS from every plot when buildings are few. Buildings are not expanded during a BFS, because the search only continues through empty plots."],
    time="O(B &middot; R &middot; C)", space="O(R &middot; C)",
    solution='''def shortestTotalDistance(grid):
    rows, cols = len(grid), len(grid[0])
    W = cols + 2
    cell = [2] * ((rows + 2) * W)  # a border of obstacles avoids bounds checks
    for r in range(rows):
        for c in range(cols):
            cell[(r + 1) * W + c + 1] = grid[r][c]
    total = [0] * len(cell)
    reach = [0] * len(cell)
    buildings = [i for i, v in enumerate(cell) if v == 1]
    steps = (1, -1, W, -W)
    for b in buildings:
        seen = bytearray(len(cell))
        level = [b]
        d = 0
        while level:
            d += 1
            nxt = []
            for u in level:
                for s in steps:
                    v = u + s
                    if cell[v] == 0 and not seen[v]:
                        seen[v] = 1
                        total[v] += d
                        reach[v] += 1
                        nxt.append(v)
            level = nxt
    best = -1
    for i, v in enumerate(cell):
        if v == 0 and reach[i] == len(buildings) and (best == -1 or total[i] < best):
            best = total[i]
    return best
''',
    tests=[[[[1, 0, 2, 0, 1], [0, 0, 0, 0, 0], [0, 0, 1, 0, 0]]], [[[1]]], [[[1, 0]]], [[[1, 2, 0]]], [[[1, 1]]],
           [[[0, 1, 0]]], [[[1, 0, 1]]], [[[1, 0, 0, 0, 1], [0, 2, 2, 2, 0], [0, 0, 0, 0, 0]]],
           [[[1, 2, 1], [2, 0, 2], [1, 2, 1]]], [[[1, 0, 1], [0, 1, 0], [1, 0, 1]]],
           [[[0, 0, 0], [0, 1, 0], [0, 0, 0]]], [[[1, 0, 0, 2, 0, 1], [0, 0, 0, 2, 0, 0], [0, 0, 0, 2, 0, 0], [0, 0, 0, 0, 0, 0]]]],
)
_r = rnd(9309)
p["tests"].append([_scatter(_r, _g(_r, 40, 40, [(0, 24), (2, 1)]), [1] * 45)])
p["tests"].append([_scatter(_r, _g(_r, 40, 40, [(0, 1)]), [1] * 50)])
p["tests"].append([_scatter(_r, _g(_r, 40, 38, [(0, 9), (2, 1)]), [1] * 30)])
p["tests"].append([_scatter(_r, _g(_r, 40, 38, [(0, 3), (2, 1)]), [1] * 50)])  # many obstacles: some buildings are probably sealed off


def b_build(grid):
    R, C = len(grid), len(grid[0])
    nb = sum(row.count(1) for row in grid)
    best = -1
    for i in range(R):
        for j in range(C):
            if grid[i][j] != 0:
                continue
            dist = {(i, j): 0}
            found = {}
            todo = [(i, j)]
            while todo:
                nxt = []
                for (y, x) in todo:
                    for a, b in DIRS:
                        q = (y + a, x + b)
                        if not (0 <= q[0] < R and 0 <= q[1] < C):
                            continue
                        v = grid[q[0]][q[1]]
                        if v == 1 and q not in found:
                            found[q] = dist[(y, x)] + 1
                        elif v == 0 and q not in dist:
                            dist[q] = dist[(y, x)] + 1
                            nxt.append(q)
                todo = nxt
            if len(found) == nb:
                tot = sum(found.values())
                if best == -1 or tot < best:
                    best = tot
    return best


def g_build(r):
    R, C = r.randint(1, 5), r.randint(1, 5)
    g = _g(r, R, C, [(0, 4), (1, 1), (2, 1)])
    _scatter(r, g, [1])
    return [g]


def v_build(tests):
    for t in tests:
        g = t["args"][0]
        _check_grid(g, 40, 40, (0, 1, 2))
        assert 1 <= _count(g, 1) <= 50


CHECKS["min-total-walk-to-all-buildings"] = (b_build, g_build, "exact")
VALIDATE["min-total-walk-to-all-buildings"] = v_build

# ---------------------------------------------------------------- latest departure before fire arrives
p = add(
    id="latest-departure-before-fire-arrives", title="Latest Departure Before the Fire Arrives", diff="Hard", topic="Graphs", tier="extra",
    fn="maxWaitMinutes", params=[("grid", "int[][]")], ret="int", cmp="exact",
    desc="<p>A <code>grid</code> shows a field: <code>0</code> is grass, <code>1</code> is a burning cell and <code>2</code> is a wall. You stand at the top-left cell and want to reach the safe house in the bottom-right cell; both of these cells are grass.</p><p>You may wait at the start for <code>w</code> whole minutes, and then walk without stopping, one step per minute, to a side-adjacent non-wall cell. In every minute the fire spreads <em>after</em> you have moved (or waited): each grass cell that shares a side with a burning cell starts to burn. You may enter a cell only if it is not burning at that moment, and you must not be standing on a cell when the fire spreads onto it, with a single exception: reaching the safe house in the same minute as the fire is fine.</p><p>Return the largest <code>w</code> that still lets you reach the safe house. Return <code>-1</code> if you cannot even if you leave immediately (<code>w = 0</code>), and <code>1000000000</code> if you can reach it however long you wait.</p><pre>grid = [[0,0,0,0,0],\n        [0,2,0,0,0],\n        [0,1,2,0,0]]\n-> 2</pre><p>The only fire is at (2,1). It is boxed in by walls and can only escape through (2,0), so it reaches (1,0) after 2 minutes and the start after 3. Waiting 3 minutes would burn you at the start, but waiting 2 is fine: you stay one step ahead of the fire all along the top row and reach the house first.</p>",
    constraints=["2 &le; rows, cols &le; 50", "grid[r][c] is 0, 1 or 2", "grid[0][0] = grid[rows-1][cols-1] = 0"],
    hints=["Waiting longer can only make things worse, because the fire only spreads further. What does that say about the set of waiting times that work?",
           "Compute <code>fire[cell]</code>, the minute in which each cell starts burning, with a BFS from all burning cells. Then, for a fixed waiting time <code>w</code>, check by BFS whether you can reach the end.",
           "Binary search on <code>w</code>. For a given <code>w</code> you may step into a cell at time <code>w + d</code> only if <code>w + d &lt; fire[cell]</code>, except the safe house where <code>w + d &le; fire[house]</code>. Also require <code>w &lt; fire[start]</code>. Detect the 'wait forever' case with a waiting time larger than any possible burn time."],
    editorial=["The fire's schedule is fixed, so a multi-source BFS gives the minute <code>fire[cell]</code> at which each cell catches fire (infinity if never). Whether waiting <code>w</code> minutes works is monotone: if it works for <code>w</code>, it works for every smaller value, since you arrive everywhere earlier.",
               "To test one value of <code>w</code>, check <code>w &lt; fire[start]</code> and run a BFS from the start where the cell reached after <code>d</code> steps is entered only if <code>w + d &lt; fire[cell]</code>; the safe house is special and may be entered when <code>w + d &le; fire[house]</code>. Binary search the largest feasible <code>w</code> in <code>[0, rows * cols]</code>. If <code>w = 0</code> fails, return -1. If a waiting time above every finite burn time (at most <code>rows * cols</code>) still works, the fire never matters for you and the answer is 1,000,000,000.",
               "Total time is O(rows &times; cols &times; log(rows &times; cols)). An alternative is to compare the fire's arrival time at the house with your arrival time and examine the last steps of the route, but that is easy to get wrong; the binary search is robust."],
    time="O(R &middot; C &middot; log(R &middot; C))", space="O(R &middot; C)",
    solution='''from collections import deque


def maxWaitMinutes(grid):
    rows, cols = len(grid), len(grid[0])
    INF = 10 ** 18
    fire = [[INF] * cols for _ in range(rows)]
    q = deque()
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == 1:
                fire[r][c] = 0
                q.append((r, c))
    while q:
        y, x = q.popleft()
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            ny, nx = y + dy, x + dx
            if 0 <= ny < rows and 0 <= nx < cols and grid[ny][nx] == 0 and fire[ny][nx] == INF:
                fire[ny][nx] = fire[y][x] + 1
                q.append((ny, nx))

    def ok(w):
        if fire[0][0] <= w:
            return False
        dist = [[-1] * cols for _ in range(rows)]
        dist[0][0] = 0
        q = deque([(0, 0)])
        while q:
            y, x = q.popleft()
            nd = dist[y][x] + 1
            for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                ny, nx = y + dy, x + dx
                if 0 <= ny < rows and 0 <= nx < cols and grid[ny][nx] == 0 and dist[ny][nx] == -1:
                    if ny == rows - 1 and nx == cols - 1:
                        if w + nd <= fire[ny][nx]:
                            return True
                    elif w + nd < fire[ny][nx]:
                        dist[ny][nx] = nd
                        q.append((ny, nx))
        return False

    if not ok(0):
        return -1
    hi = rows * cols + 2
    if ok(hi):
        return 1000000000
    lo = 0
    while hi - lo > 1:
        mid = (lo + hi) // 2
        if ok(mid):
            lo = mid
        else:
            hi = mid
    return lo
''',
    tests=[[[[0, 0, 0, 0, 0], [0, 2, 0, 0, 0], [0, 1, 2, 0, 0]]],
           [[[0, 0], [0, 0]]], [[[0, 1], [0, 0]]], [[[0, 2], [2, 0]]], [[[0, 0], [1, 0]]],
           [[[0, 0, 0], [0, 0, 0], [1, 0, 0]]], [[[0, 0, 0, 0], [0, 2, 2, 0], [0, 0, 0, 0]]],
           [[[0, 0, 0, 0, 0, 0], [2, 2, 2, 2, 2, 0], [0, 0, 0, 0, 0, 0], [0, 2, 2, 2, 2, 2], [0, 0, 1, 0, 0, 0]]],
           [[[0, 2, 0, 0], [0, 2, 0, 2], [0, 0, 0, 0], [2, 2, 2, 1], [0, 0, 0, 0]]],
           [[[0, 0, 0, 0, 0, 0], [0, 2, 2, 2, 2, 0], [0, 0, 0, 0, 0, 0], [2, 2, 2, 2, 1, 0], [0, 0, 0, 0, 0, 0]]]],
)


def _fire_rooms(R, C, qc, lf, fire_connects=True):
    """Person corridor: top row then right column. A fire corridor leaves the top row at column qc and goes down lf cells."""
    g = [[2] * C for _ in range(R)]
    for j in range(C):
        g[0][j] = 0
    for i in range(R):
        g[i][C - 1] = 0
    for i in range(1, lf + 1):
        g[i][qc] = 0
    g[lf][qc] = 1
    if not fire_connects:
        g[1][qc] = 2
    return g


p["tests"].append([_fire_rooms(50, 50, 30, 40)])  # fire corridor of length 40 joins the top row at column 30
p["tests"].append([_fire_rooms(50, 50, 10, 47)])
p["tests"].append([_fire_rooms(50, 50, 25, 20)])  # the fire gets to the corridor too soon
p["tests"].append([_fire_rooms(50, 50, 44, 47, fire_connects=False)])  # the fire is sealed in: wait as long as you like
_r = rnd(9310)
_ref_fire = _ref(p)
_found = []
for _k in range(4000):
    _R, _C = _r.randint(6, 9), _r.randint(6, 9)
    _g5 = _g(_r, _R, _C, [(0, 7), (2, 2)])
    _g5[0][0] = 0
    _g5[_R - 1][_C - 1] = 0
    _fi = [(i, j) for i in range(_R) for j in range(_C) if _g5[i][j] == 0 and (i, j) not in ((0, 0), (_R - 1, _C - 1))]
    for _c in _r.sample(_fi, 2):
        _g5[_c[0]][_c[1]] = 1
    _v = _ref_fire(_g5)
    if 2 <= _v < 10 ** 6:
        _found.append(_g5)
        if len(_found) == 3:
            break
for _x in _found:
    p["tests"].append([_x])


def b_fire(grid):
    R, C = len(grid), len(grid[0])
    LIM = R * C + 2

    def works(w):
        F = {(i, j) for i in range(R) for j in range(C) if grid[i][j] == 1}

        def spread(F):
            F2 = set(F)
            for i, j in F:
                for a, b in DIRS:
                    q = (i + a, j + b)
                    if 0 <= q[0] < R and 0 <= q[1] < C and grid[q[0]][q[1]] == 0:
                        F2.add(q)
            return F2

        for _ in range(w):
            F = spread(F)
        if (0, 0) in F:
            return False
        P = {(0, 0)}
        for _ in range(R * C + 3):
            P2 = set()
            for i, j in P:
                for a, b in DIRS:
                    q = (i + a, j + b)
                    if 0 <= q[0] < R and 0 <= q[1] < C and grid[q[0]][q[1]] == 0 and q not in F:
                        P2.add(q)
            if (R - 1, C - 1) in P2:
                return True
            F = spread(F)
            P = P2 - F
            if not P:
                return False
        return False

    good = [w for w in range(LIM + 1) if works(w)]
    if not good:
        return -1
    return 1000000000 if max(good) == LIM else max(good)


def g_fire(r):
    R, C = r.randint(2, 5), r.randint(2, 5)
    g = _g(r, R, C, [(0, 5), (2, 2)])
    g[0][0] = 0
    g[R - 1][C - 1] = 0
    cand = [(i, j) for i in range(R) for j in range(C) if (i, j) not in ((0, 0), (R - 1, C - 1)) and g[i][j] == 0]
    for _ in range(r.randint(0, 2)):
        if cand:
            i, j = cand.pop(r.randrange(len(cand)))
            g[i][j] = 1
    return [g]


def v_fire(tests):
    for t in tests:
        g = t["args"][0]
        _check_grid(g, 50, 50, (0, 1, 2), rmin=2, cmin=2)
        assert g[0][0] == 0 and g[-1][-1] == 0
        assert t["expected"] == -1 or t["expected"] >= 0


CHECKS["latest-departure-before-fire-arrives"] = (b_fire, g_fire, "exact")
VALIDATE["latest-departure-before-fire-arrives"] = v_fire

# ---------------------------------------------------------------- fewest bus routes
p = add(
    id="fewest-bus-routes-to-destination", title="Fewest Bus Routes to a Stop", diff="Hard", topic="Graphs", tier="common",
    fn="minBusRoutes", params=[("routes", "int[][]"), ("source", "int"), ("target", "int")], ret="int", cmp="exact",
    desc="<p>A city has several bus lines. The array <code>routes</code> lists them: <code>routes[i]</code> holds the (distinct) stop numbers of line <code>i</code>, and every bus of line <code>i</code> drives around those stops in a loop forever, so you can get on or off at any of its stops at any time. A stop may belong to several lines.</p><p>You start at stop <code>source</code> and are not on a bus yet. Moving only by bus, find the smallest number of <em>bus rides</em> (boardings) needed to arrive at stop <code>target</code>. Staying on a line and riding through many stops counts as one ride; changing to another line counts as another. Return <code>0</code> if <code>source == target</code>, and <code>-1</code> if the target cannot be reached.</p><pre>routes = [[1,2,7], [3,6,7]], source = 1, target = 6\n-> 2</pre><p>Take line 0 from stop 1 to stop 7, then line 1 from stop 7 to stop 6.</p>",
    constraints=["1 &le; routes.length &le; 500", "1 &le; routes[i].length &le; 100, the stops inside one line are distinct, and the total number of stops over all lines is at most 6,300", "0 &le; routes[i][j], source, target &le; 1,000,000", "source and target need not appear in any line"],
    hints=["Think of what the BFS nodes should be. Modelling every stop as a node with an edge to every other stop on the same line has far too many edges.",
           "The quantity you minimise is the number of <em>lines</em> used, so make each line a unit of the search: build a map from every stop to the lines that serve it.",
           "BFS over stops, but process a line only once: when you pop stops of the current level, take every line serving them that has not been used yet, and all its stops form the next level. Count the levels."],
    editorial=["Build <code>lines_at[stop]</code>, the list of lines serving that stop. Run a level-by-level BFS where level k holds the stops reachable with exactly k rides. For the stops of the current level, take every line serving them that was not used before, mark it as used and look at all its stops: if one of them is the target, the answer is the current ride count; otherwise unseen stops form the next level.",
               "Marking a line as used the first time it is met is the key to efficiency: each line's stop list is scanned only once, so the total work is O(total number of stops). Using the first level where the target appears is correct because BFS finds the fewest rides. A source equal to the target needs no ride, and a source or target that no line serves makes the answer -1."],
    time="O(S) where S is the total number of stops over all lines", space="O(S)",
    solution='''def minBusRoutes(routes, source, target):
    if source == target:
        return 0
    lines_at = {}
    for i, route in enumerate(routes):
        for s in route:
            lines_at.setdefault(s, []).append(i)
    if source not in lines_at or target not in lines_at:
        return -1
    used = [False] * len(routes)
    seen = {source}
    level = [source]
    rides = 0
    while level:
        rides += 1
        nxt = []
        for s in level:
            for i in lines_at[s]:
                if used[i]:
                    continue
                used[i] = True
                for t in routes[i]:
                    if t == target:
                        return rides
                    if t not in seen:
                        seen.add(t)
                        nxt.append(t)
        level = nxt
    return -1
''',
    tests=[[[[1, 2, 7], [3, 6, 7]], 1, 6], [[[1, 2, 3]], 2, 2], [[[1, 2, 3]], 1, 3], [[[1, 2, 3]], 1, 9], [[[1, 2, 3]], 9, 1],
           [[[1, 2], [3, 4]], 1, 4], [[[0, 5, 10], [10, 15], [15, 20, 0]], 0, 20], [[[0, 5, 10], [10, 15], [15, 20, 0]], 5, 20],
           [[[7, 12], [4, 5, 15], [6], [15, 19], [9, 12, 13]], 15, 12], [[[1, 2, 7, 8], [3, 6, 7, 9], [9, 10], [2, 10, 11], [11, 6]], 1, 6],
           [[[1000000, 0], [0, 500000]], 1000000, 500000], [[[5]], 5, 5], [[[5]], 5, 6]],
)
_r = rnd(9311)
# a chain of 250 lines of 21 stops each; consecutive lines share exactly one stop (answer 250)
_chain = []
for _i in range(250):
    _l = list(range(_i * 20, _i * 20 + 21))
    _r.shuffle(_l)
    _chain.append(_l)
_r.shuffle(_chain)
p["tests"].append([_chain, 0, 5000])
p["tests"].append([_chain, 4999, 3])
# 500 random lines of 12 stops over 1,500 stops
p["tests"].append([[_r.sample(range(0, 1500), 12) for _ in range(500)], 3, 1499])
# 500 lines over 6,000 stops: sparse, so many stops are served by a single line and the answer is large or -1
p["tests"].append([[_r.sample(range(0, 6000), 12) for _ in range(500)], 17, 5000])


def b_bus(routes, source, target):
    INF = 10 ** 9
    dist = {source: 0}
    changed = True
    while changed:
        changed = False
        for route in routes:
            m = min(dist.get(s, INF) for s in route)
            if m < INF:
                for s in route:
                    if dist.get(s, INF) > m + 1:
                        dist[s] = m + 1
                        changed = True
    return dist.get(target, -1)


def g_bus(r):
    U = r.randint(2, 9)
    routes = [r.sample(range(U), r.randint(1, min(U, 4))) for _ in range(r.randint(1, 6))]
    return [routes, r.randrange(U + 1), r.randrange(U + 1)]


def v_bus(tests):
    for t in tests:
        routes, s, g = t["args"]
        assert 1 <= len(routes) <= 500
        assert sum(len(x) for x in routes) <= 6300
        for x in routes:
            assert 1 <= len(x) <= 100 and len(set(x)) == len(x)
            assert all(0 <= v <= 1000000 for v in x)
        assert 0 <= s <= 1000000 and 0 <= g <= 1000000


CHECKS["fewest-bus-routes-to-destination"] = (b_bus, g_bus, "exact")
VALIDATE["fewest-bus-routes-to-destination"] = v_bus
