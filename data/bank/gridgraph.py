"""Problems: grid graphs (flood fill, grid BFS/DFS, multi-source BFS, 0-1 BFS). See data/lib.py for the registry."""
from lib import add, rnd, CHECKS, VALIDATE, gen_arr  # noqa: F401
from lib import P as _P  # noqa: E402

INF = 2147483647
DIRS = ((1, 0), (-1, 0), (0, 1), (0, -1))


# ------------------------------------------------------------------ shared helpers (tests only)
def _bin_grid(r, R, C, p):
    return [[1 if r.random() < p else 0 for _ in range(C)] for _ in range(R)]


def _val_grid(r, R, C, vals):
    return [[r.choice(vals) for _ in range(C)] for _ in range(R)]


def _check_rect(g, rmax, cmax, allowed=None, lo=None, hi=None):
    assert 1 <= len(g) <= rmax, "rows"
    assert all(len(row) == len(g[0]) for row in g), "ragged"
    assert 1 <= len(g[0]) <= cmax, "cols"
    for row in g:
        for v in row:
            if allowed is not None:
                assert v in allowed, ("cell value", v)
            if lo is not None:
                assert lo <= v <= hi, ("cell range", v)


def _comp_count(g):
    """Number of 4-connected groups of 1s (independent counting code used by validators)."""
    R, C = len(g), len(g[0])
    seen = set()
    n = 0
    for i in range(R):
        for j in range(C):
            if g[i][j] == 1 and (i, j) not in seen:
                n += 1
                seen.add((i, j))
                todo = [(i, j)]
                while todo:
                    a, b = todo.pop()
                    for da, db in DIRS:
                        x, y = a + da, b + db
                        if 0 <= x < R and 0 <= y < C and g[x][y] == 1 and (x, y) not in seen:
                            seen.add((x, y))
                            todo.append((x, y))
    return n


def _labels(g, same):
    """Group cells into 4-connected groups where same(value) is true. Label propagation (no search)."""
    R, C = len(g), len(g[0])
    lab = {(i, j): i * C + j for i in range(R) for j in range(C) if same(g[i][j])}
    changed = True
    while changed:
        changed = False
        for (i, j) in lab:
            for di, dj in DIRS:
                q = (i + di, j + dj)
                if q in lab and lab[q] < lab[(i, j)]:
                    lab[(i, j)] = lab[q]
                    changed = True
    return lab


def _groups(g, same):
    out = {}
    for cell, lb in _labels(g, same).items():
        out.setdefault(lb, []).append(cell)
    return list(out.values())


# =================================================================== EASY
# ---------------------------------------------------------------- flood fill recolor
add(
    id="flood-fill-recolor", title="Flood Fill Recolor", diff="Easy", topic="Graphs",
    fn="floodFill", params=[("image", "int[][]"), ("sr", "int"), ("sc", "int"), ("color", "int")], ret="int[][]", cmp="exact",
    desc="<p>An <code>image</code> is a grid of integers where each cell holds a color. Starting at the cell <code>(sr, sc)</code>, repaint that cell and every cell reachable from it by steps up, down, left or right that passes <em>only</em> through cells having the same color as the starting cell, using the new color <code>color</code>.</p><p>Return the repainted image. The cells that are not part of this connected same-colored region must be left unchanged.</p><pre>image = [[1,1,0],\n         [1,0,0],\n         [1,1,1]],  sr = 0, sc = 0, color = 7\n\nresult = [[7,7,0],\n          [7,0,0],\n          [7,7,7]]</pre>",
    constraints=["1 &le; image.length, image[0].length &le; 50", "0 &le; image[r][c], color &le; 65,535", "0 &le; sr &lt; image.length and 0 &le; sc &lt; image[0].length"],
    hints=["Only the cells of the starting cell's original color that touch each other (through the four directions) are recolored.",
           "Remember the original color first, then explore from the start with a stack or queue, moving only onto cells that still have that original color.",
           "If the new color already equals the original color, the image does not change at all. Handle that case up front, otherwise recoloring cannot tell visited cells from unvisited ones and the search never ends."],
    editorial=["Read the color <code>old</code> of the start cell. If <code>old == color</code> return a copy of the image straight away. Otherwise run a BFS or DFS from <code>(sr, sc)</code>: paint a cell with the new color at the moment you push it, and only push neighbours whose current color is still <code>old</code>. Painting acts as the visited marker, which is why the early return for the equal-color case is needed.",
               "Each cell is pushed at most once, so the time is O(rows &times; cols). Using an explicit stack avoids deep recursion on a 50 &times; 50 region."],
    time="O(R &middot; C)", space="O(R &middot; C)",
    solution='''def floodFill(image, sr, sc, color):
    res = [row[:] for row in image]
    old = res[sr][sc]
    if old == color:
        return res
    rows, cols = len(res), len(res[0])
    res[sr][sc] = color
    stack = [(sr, sc)]
    while stack:
        y, x = stack.pop()
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            ny, nx = y + dy, x + dx
            if 0 <= ny < rows and 0 <= nx < cols and res[ny][nx] == old:
                res[ny][nx] = color
                stack.append((ny, nx))
    return res
''',
    tests=[[[[1, 1, 0], [1, 0, 0], [1, 1, 1]], 0, 0, 7], [[[0, 0, 0], [0, 0, 0]], 1, 1, 0], [[[5]], 0, 0, 9],
           [[[1, 2, 1], [2, 1, 2], [1, 2, 1]], 1, 1, 3], [[[1, 1, 1, 1]], 0, 2, 0], [[[3], [3], [4], [3]], 3, 0, 8],
           [[[0, 1, 0], [1, 1, 1], [0, 1, 0]], 1, 1, 0], [[[2, 2, 2], [2, 3, 2], [2, 2, 2]], 0, 0, 3],
           [[[2, 2, 2], [2, 3, 2], [2, 2, 2]], 1, 1, 2], [[[0, 0, 1], [0, 1, 1], [1, 1, 0]], 2, 2, 65535]],
)
_r = rnd(7101)
_P[-1]["tests"].append([_val_grid(_r, 50, 50, [0, 0, 0, 1]), 25, 25, 2])
_P[-1]["tests"].append([_val_grid(_r, 50, 50, [4]), 49, 0, 5])
_P[-1]["tests"].append([_val_grid(_r, 50, 50, [4]), 0, 49, 4])
_P[-1]["tests"].append([[[1 if (i % 2 == 0 or (i % 4 == 1 and j == 49) or (i % 4 == 3 and j == 0)) else 0 for j in range(49)] for i in range(49)], 0, 0, 6])
_P[-1]["tests"].append([_val_grid(_r, 40, 50, [0, 1, 2]), 17, 33, 1])


def b_flood(image, sr, sc, color):
    # grow the region by sweeping the whole image until nothing new joins it
    old = image[sr][sc]
    R, C = len(image), len(image[0])
    region = {(sr, sc)}
    grew = True
    while grew:
        grew = False
        for i in range(R):
            for j in range(C):
                if (i, j) not in region and image[i][j] == old:
                    if any((i + a, j + b) in region for a, b in DIRS):
                        region.add((i, j))
                        grew = True
    return [[color if (i, j) in region else image[i][j] for j in range(C)] for i in range(R)]


def g_flood(r):
    R, C = r.randint(1, 5), r.randint(1, 5)
    g = _val_grid(r, R, C, [0, 1, 2][:r.randint(1, 3)])
    return [g, r.randrange(R), r.randrange(C), r.randint(0, 3)]


def v_flood(tests):
    for t in tests:
        image, sr, sc, color = t["args"]
        _check_rect(image, 50, 50, lo=0, hi=65535)
        assert 0 <= sr < len(image) and 0 <= sc < len(image[0]) and 0 <= color <= 65535


CHECKS["flood-fill-recolor"] = (b_flood, g_flood, "exact")
VALIDATE["flood-fill-recolor"] = v_flood

# ---------------------------------------------------------------- island perimeter
add(
    id="island-perimeter-length", title="Island Perimeter Length", diff="Easy", topic="Graphs",
    fn="islandPerimeter", params=[("grid", "int[][]")], ret="int", cmp="exact",
    desc="<p>In a <code>grid</code>, a <code>1</code> is a unit square of land and a <code>0</code> is water. Every land square has four sides. A side is part of the <em>perimeter</em> if the square next to it (above, below, left or right) is water, or if that side lies on the outer edge of the grid.</p><p>Return the total number of perimeter sides over all land squares. Water enclosed by land (a lake) also contributes its boundary sides, and the grid may hold any number of separate islands.</p><pre>grid = [[0,1,0,0],\n        [1,1,1,0],\n        [0,1,0,0]]   -> 12</pre>",
    constraints=["1 &le; rows, cols &le; 100", "grid[r][c] is 0 or 1"],
    hints=["You do not need to find islands at all. Think about each land square on its own.",
           "A single land square contributes 4 sides. Two land squares that touch hide one side of each.",
           "Count 4 per land square, then subtract 2 for every pair of land squares that are adjacent. Check only the cell above and the cell to the left so each pair is counted once."],
    editorial=["Look at each land square independently: it has four sides, and each side is on the perimeter unless the neighbour across it is land. Equivalently, the answer is <code>4 * land - 2 * shared</code>, where <code>shared</code> is the number of adjacent land pairs (each pair removes one side from both squares).",
               "Scan the grid once. For every land cell add one to <code>land</code> and add one to <code>shared</code> for the land cell directly above it and for the one directly to its left. This is O(rows &times; cols) time and O(1) extra space, and it works for any number of islands and lakes because only local neighbours matter."],
    time="O(R &middot; C)", space="O(1)",
    solution='''def islandPerimeter(grid):
    land = 0
    shared = 0
    for r in range(len(grid)):
        for c in range(len(grid[0])):
            if grid[r][c] == 1:
                land += 1
                if r > 0 and grid[r - 1][c] == 1:
                    shared += 1
                if c > 0 and grid[r][c - 1] == 1:
                    shared += 1
    return 4 * land - 2 * shared
''',
    tests=[[[[0, 1, 0, 0], [1, 1, 1, 0], [0, 1, 0, 0]]], [[[1]]], [[[0]]], [[[1, 0]]], [[[1, 1], [1, 1]]],
           [[[1, 1, 1], [1, 0, 1], [1, 1, 1]]], [[[1, 0, 1], [0, 0, 0], [1, 0, 1]]], [[[1, 1, 1, 1, 1]]],
           [[[1], [0], [1], [1]]], [[[0, 0, 0], [0, 0, 0]]]],
)
_r = rnd(7102)
_P[-1]["tests"].append([_bin_grid(_r, 100, 100, 0.5)])
_P[-1]["tests"].append([[[1] * 100 for _ in range(100)]])
_P[-1]["tests"].append([[[(i + j) % 2 for j in range(100)] for i in range(100)]])
_P[-1]["tests"].append([_bin_grid(_r, 100, 100, 0.85)])
_P[-1]["tests"].append([_bin_grid(_r, 1, 100, 0.6)])


def b_perim(grid):
    R, C = len(grid), len(grid[0])
    total = 0
    for i in range(R):
        for j in range(C):
            if grid[i][j]:
                for a, b in DIRS:
                    x, y = i + a, j + b
                    if not (0 <= x < R and 0 <= y < C) or grid[x][y] == 0:
                        total += 1
    return total


CHECKS["island-perimeter-length"] = (b_perim, lambda r: [_bin_grid(r, r.randint(1, 6), r.randint(1, 6), r.choice([0.3, 0.6, 0.9]))], "exact")
VALIDATE["island-perimeter-length"] = lambda tests: [_check_rect(t["args"][0], 100, 100, allowed=(0, 1)) for t in tests]


# =================================================================== MEDIUM
# ---------------------------------------------------------------- surrounded regions
add(
    id="surrounded-regions-capture", title="Surrounded Regions Capture", diff="Medium", topic="Graphs",
    fn="captureRegions", params=[("board", "int[][]")], ret="int[][]", cmp="exact",
    desc="<p>A <code>board</code> holds <code>1</code> for a wall tile and <code>0</code> for an open tile. Open tiles that touch each other (up, down, left or right) form a <em>region</em>. A region is <em>surrounded</em> when none of its tiles lies on the outer border of the board (first or last row, first or last column).</p><p>Turn every tile of every surrounded region into a wall (<code>1</code>) and return the resulting board. Open regions that reach the border stay exactly as they are.</p><pre>board = [[1,1,1,1],\n         [1,0,0,1],\n         [1,1,0,1],\n         [1,0,1,0]]\n\nresult = [[1,1,1,1],\n          [1,1,1,1],\n          [1,1,1,1],\n          [1,0,1,0]]</pre>",
    constraints=["1 &le; rows, cols &le; 100", "board[r][c] is 0 or 1"],
    hints=["Deciding for every region whether it touches the border is possible, but the reverse question is easier: which open tiles are safe?",
           "An open tile is safe exactly when it can be reached from an open tile on the border by walking only on open tiles.",
           "Start a search from every open border tile at once and mark everything reached as safe. Afterwards, every open tile that is not marked safe is surrounded and becomes a wall."],
    editorial=["Instead of testing each region, flood from the outside in. Push every open border tile on a stack and mark it safe. Pop a tile and push its unmarked open neighbours, marking them safe as well. When the stack is empty, the safe tiles are precisely the open tiles that belong to regions touching the border.",
               "Build the answer in one more pass: a tile stays <code>0</code> only if it is safe, every other tile becomes <code>1</code>. Each tile is visited a constant number of times, so the algorithm runs in O(rows &times; cols) time and space. An explicit stack keeps the search safe for a 100 &times; 100 board."],
    time="O(R &middot; C)", space="O(R &middot; C)",
    solution='''def captureRegions(board):
    rows, cols = len(board), len(board[0])
    safe = [[False] * cols for _ in range(rows)]
    stack = []
    for r in range(rows):
        for c in range(cols):
            if (r in (0, rows - 1) or c in (0, cols - 1)) and board[r][c] == 0:
                safe[r][c] = True
                stack.append((r, c))
    while stack:
        y, x = stack.pop()
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            ny, nx = y + dy, x + dx
            if 0 <= ny < rows and 0 <= nx < cols and board[ny][nx] == 0 and not safe[ny][nx]:
                safe[ny][nx] = True
                stack.append((ny, nx))
    return [[0 if safe[r][c] else 1 for c in range(cols)] for r in range(rows)]
''',
    tests=[[[[1, 1, 1, 1], [1, 0, 0, 1], [1, 1, 0, 1], [1, 0, 1, 0]]], [[[0]]], [[[1]]], [[[0, 0, 0], [0, 0, 0], [0, 0, 0]]],
           [[[1, 1, 1], [1, 0, 1], [1, 1, 1]]], [[[1, 1, 1, 1, 1], [1, 0, 0, 0, 1], [1, 0, 1, 0, 1], [1, 0, 0, 0, 1], [1, 1, 1, 1, 1]]],
           [[[1, 1, 1, 1, 1], [1, 0, 0, 0, 1], [1, 0, 1, 0, 1], [1, 0, 0, 0, 0], [1, 1, 1, 1, 1]]],
           [[[1, 0, 1], [0, 1, 0], [1, 0, 1]]], [[[0, 1, 1], [1, 0, 1], [1, 1, 0]]], [[[1, 1], [1, 1]]]],
)
_r = rnd(7103)
_P[-1]["tests"].append([_bin_grid(_r, 100, 100, 0.45)])
_P[-1]["tests"].append([_bin_grid(_r, 100, 100, 0.6)])
_P[-1]["tests"].append([[[1] * 100] + [[1] + [0] * 98 + [1] for _ in range(98)] + [[1] * 100]])  # one huge enclosed room
_P[-1]["tests"].append([[[0 if (min(i, j, 99 - i, 99 - j) % 2 == 1) else 1 for j in range(100)] for i in range(100)]])  # nested rings
_P[-1]["tests"].append([[[0 if (i == 0 or (i % 2 == 1) or (i % 4 == 2 and j == 98) or (i % 4 == 0 and j == 1)) else 1 for j in range(100)] for i in range(100)]])


def b_capture(board):
    R, C = len(board), len(board[0])
    out = [row[:] for row in board]
    for i in range(R):
        for j in range(C):
            if board[i][j] == 0:
                # walk the region of (i, j) on its own; does it ever touch the border?
                seen = {(i, j)}
                todo = [(i, j)]
                touches = False
                while todo:
                    a, b = todo.pop()
                    if a in (0, R - 1) or b in (0, C - 1):
                        touches = True
                        break
                    for da, db in DIRS:
                        q = (a + da, b + db)
                        if board[q[0]][q[1]] == 0 and q not in seen:
                            seen.add(q)
                            todo.append(q)
                if not touches:
                    out[i][j] = 1
    return out


CHECKS["surrounded-regions-capture"] = (b_capture, lambda r: [_bin_grid(r, r.randint(1, 7), r.randint(1, 7), r.choice([0.4, 0.6, 0.75]))], "exact")
VALIDATE["surrounded-regions-capture"] = lambda tests: [_check_rect(t["args"][0], 100, 100, allowed=(0, 1)) for t in tests]

# ---------------------------------------------------------------- pacific atlantic
add(
    id="pacific-atlantic-water-flow", title="Pacific Atlantic Water Flow", diff="Medium", topic="Graphs",
    fn="pacificAtlantic", params=[("heights", "int[][]")], ret="int[][]", cmp="rowset",
    desc="<p>A rectangular island is described by <code>heights[r][c]</code>, the height of each cell. The Pacific Ocean touches the island along its <strong>top row and left column</strong>; the Atlantic Ocean touches it along its <strong>bottom row and right column</strong>.</p><p>Rain falling on a cell flows to any of the four adjacent cells whose height is <em>less than or equal to</em> the current cell, and from there onwards in the same way. A cell on the Pacific edge can flow into the Pacific, and a cell on the Atlantic edge can flow into the Atlantic.</p><p>Return the coordinates <code>[r, c]</code> of every cell from which water can reach <em>both</em> oceans. The rows of the result may be in any order.</p><pre>heights = [[1,2,3],\n           [8,9,4],\n           [7,6,5]]\n\nresult = [[0,2],[1,0],[1,1],[1,2],[2,0],[2,1],[2,2]]</pre>",
    constraints=["1 &le; rows, cols &le; 100", "0 &le; heights[r][c] &le; 100,000", "The result always contains at least one cell"],
    hints=["Simulating the flow from every single cell works but repeats a lot of work.",
           "Reverse the question: start at the ocean and walk <em>uphill</em>. Which cells can reach the Pacific? Which can reach the Atlantic?",
           "Run one search from all Pacific-edge cells moving to neighbours that are at least as high, and another from all Atlantic-edge cells. The answer is the intersection of the two visited sets."],
    editorial=["Flowing downhill from each cell is expensive, but the relation is symmetric when reversed: if water can go from <code>a</code> to a neighbour <code>b</code> (<code>h[b] &le; h[a]</code>), then walking from <code>b</code> to <code>a</code> goes uphill or level. So the set of cells that can reach the Pacific is exactly the set reachable from the Pacific edge when you only step to neighbours that are not lower.",
               "Do one BFS/DFS seeded with the top row and left column, and another seeded with the bottom row and right column. Collect the cells visited in both, sorted for neatness. Each search touches each cell once, giving O(rows &times; cols) time and space."],
    time="O(R &middot; C)", space="O(R &middot; C)",
    solution='''def pacificAtlantic(heights):
    rows, cols = len(heights), len(heights[0])

    def reach(starts):
        seen = set(starts)
        stack = list(starts)
        while stack:
            y, x = stack.pop()
            for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                ny, nx = y + dy, x + dx
                if 0 <= ny < rows and 0 <= nx < cols and (ny, nx) not in seen and heights[ny][nx] >= heights[y][x]:
                    seen.add((ny, nx))
                    stack.append((ny, nx))
        return seen

    pacific = [(0, c) for c in range(cols)] + [(r, 0) for r in range(1, rows)]
    atlantic = [(rows - 1, c) for c in range(cols)] + [(r, cols - 1) for r in range(rows - 1)]
    both = reach(pacific) & reach(atlantic)
    return [[r, c] for r, c in sorted(both)]
''',
    tests=[[[[1, 2, 3], [8, 9, 4], [7, 6, 5]]], [[[1, 2, 2, 3, 5], [3, 2, 3, 4, 4], [2, 4, 5, 3, 1], [6, 7, 1, 4, 5], [5, 1, 1, 2, 4]]],
           [[[7]]], [[[1, 2, 3, 4]]], [[[4], [3], [2], [1]]], [[[2, 2], [2, 2]]],
           [[[5, 4, 3], [4, 3, 2], [3, 2, 1]]], [[[1, 1, 1], [1, 9, 1], [1, 1, 1]]],
           [[[3, 3, 3], [3, 1, 3], [3, 3, 3]]], [[[10, 10, 10], [1, 1, 1], [10, 10, 10]]]],
)
_r = rnd(7104)
_P[-1]["tests"].append([_val_grid(_r, 100, 100, list(range(0, 100001, 997)))])
_P[-1]["tests"].append([[[7] * 60 for _ in range(60)]])
_P[-1]["tests"].append([[[100000 - (i + j) * 10 for j in range(100)] for i in range(100)]])
_P[-1]["tests"].append([[[(i * j) % 13 + _r.randint(0, 2) for j in range(80)] for i in range(80)]])
_P[-1]["tests"].append([[[abs(i - 50) + abs(j - 50) for j in range(100)] for i in range(100)]])  # a bowl


def b_pacific(h):
    R, C = len(h), len(h[0])

    def can(i, j, ocean):
        seen = {(i, j)}
        todo = [(i, j)]
        while todo:
            a, b = todo.pop()
            if ocean == "P" and (a == 0 or b == 0):
                return True
            if ocean == "A" and (a == R - 1 or b == C - 1):
                return True
            for da, db in DIRS:
                x, y = a + da, b + db
                if 0 <= x < R and 0 <= y < C and (x, y) not in seen and h[x][y] <= h[a][b]:
                    seen.add((x, y))
                    todo.append((x, y))
        return False

    return [[i, j] for i in range(R) for j in range(C) if can(i, j, "P") and can(i, j, "A")]


CHECKS["pacific-atlantic-water-flow"] = (b_pacific, lambda r: [_val_grid(r, r.randint(1, 6), r.randint(1, 6), list(range(r.randint(1, 8))))], "rowset")


def v_pacific(tests):
    for t in tests:
        _check_rect(t["args"][0], 100, 100, lo=0, hi=100000)
        assert len(t["expected"]) >= 1


VALIDATE["pacific-atlantic-water-flow"] = v_pacific

# ---------------------------------------------------------------- walls and gates
add(
    id="walls-and-gates-distance", title="Walls and Gates Distance", diff="Medium", topic="Graphs",
    fn="wallsAndGates", params=[("rooms", "int[][]")], ret="int[][]", cmp="exact",
    desc="<p>A building floor plan is a grid <code>rooms</code> where <code>-1</code> is a wall, <code>0</code> is a gate and <code>2147483647</code> (called <code>INF</code>) is an empty room. You may move between rooms that are adjacent up, down, left or right, and you cannot enter a wall.</p><p>Replace every empty room with the length of the shortest path (number of steps) to its <em>nearest</em> gate. A room that cannot reach any gate keeps the value <code>INF</code>. Return the updated grid; walls and gates keep their values.</p><pre>rooms = [[INF, -1,  0, INF],\n         [INF, INF, INF, -1],\n         [INF, -1, INF, -1],\n         [ 0,  -1, INF, INF]]\n\nresult = [[3, -1, 0, 1],\n          [2,  2, 1, -1],\n          [1, -1, 2, -1],\n          [0, -1, 3,  4]]</pre>",
    constraints=["1 &le; rows, cols &le; 100", "rooms[r][c] is -1, 0 or 2147483647", "INF = 2147483647 marks an empty room"],
    hints=["Running a BFS from every empty room to find its nearest gate is too slow for large grids. Reverse who starts the search.",
           "BFS visits cells in order of increasing distance from its start. What if the search started at all gates at the same time?",
           "Put every gate into the queue with distance 0 and run one BFS. When you step from a cell to an unvisited empty room, its distance is the current cell's distance plus 1. Rooms never reached stay INF."],
    editorial=["This is a multi-source BFS. Seed the queue with all gates. The first time the search reaches an empty room, it arrives along a shortest path from the <em>closest</em> gate, because BFS expands in layers of equal distance from the whole set of sources. Write the layer number into the room at that moment; a room still equal to INF has not been visited, so no separate visited array is needed.",
               "Every cell is enqueued at most once, so the running time is O(rows &times; cols). Rooms that are separated from all gates by walls are never reached and correctly keep INF."],
    time="O(R &middot; C)", space="O(R &middot; C)",
    solution='''from collections import deque


def wallsAndGates(rooms):
    INF = 2147483647
    res = [row[:] for row in rooms]
    rows, cols = len(res), len(res[0])
    q = deque((r, c) for r in range(rows) for c in range(cols) if res[r][c] == 0)
    while q:
        y, x = q.popleft()
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            ny, nx = y + dy, x + dx
            if 0 <= ny < rows and 0 <= nx < cols and res[ny][nx] == INF:
                res[ny][nx] = res[y][x] + 1
                q.append((ny, nx))
    return res
''',
    tests=[[[[INF, -1, 0, INF], [INF, INF, INF, -1], [INF, -1, INF, -1], [0, -1, INF, INF]]], [[[0]]], [[[INF]]], [[[-1]]],
           [[[0, INF, INF, INF, 0]]], [[[INF, -1, INF], [-1, 0, -1], [INF, -1, INF]]], [[[0, 0], [0, 0]]],
           [[[INF, INF, INF], [INF, 0, INF], [INF, INF, INF]]], [[[0, -1, INF], [-1, -1, INF], [INF, INF, 0]]],
           [[[INF, INF], [-1, -1], [INF, 0]]]],
)
_r = rnd(7105)


def _wg(r, R, C, pw, pg):
    return [[(-1 if x < pw else (0 if x < pw + pg else INF)) for x in (r.random() for _ in range(C))] for _ in range(R)]


_P[-1]["tests"].append([_wg(_r, 100, 100, 0.25, 0.01)])
_P[-1]["tests"].append([_wg(_r, 100, 100, 0.0, 0.001)])
_P[-1]["tests"].append([_wg(_r, 100, 100, 0.4, 0.02)])
_P[-1]["tests"].append([[[-1] * 100 for _ in range(50)]])
_P[-1]["tests"].append([[[0 if (i == 0 and j == 0) else (INF if (i % 2 == 0 or (i % 4 == 1 and j == 99) or (i % 4 == 3 and j == 0)) else -1) for j in range(100)] for i in range(99)]])  # long winding corridor with a gate at one end
_P[-1]["tests"].append([[[INF] * 100 for _ in range(100)]])


def b_gates(rooms):
    R, C = len(rooms), len(rooms[0])
    d = [row[:] for row in rooms]
    changed = True
    while changed:  # relaxation sweeps until stable
        changed = False
        for i in range(R):
            for j in range(C):
                if rooms[i][j] != INF:
                    continue
                for a, b in DIRS:
                    x, y = i + a, j + b
                    if 0 <= x < R and 0 <= y < C and d[x][y] not in (-1, INF) and d[x][y] + 1 < d[i][j]:
                        d[i][j] = d[x][y] + 1
                        changed = True
    return d


CHECKS["walls-and-gates-distance"] = (b_gates, lambda r: [_wg(r, r.randint(1, 7), r.randint(1, 7), r.choice([0.2, 0.4]), r.choice([0.1, 0.25]))], "exact")
VALIDATE["walls-and-gates-distance"] = lambda tests: [_check_rect(t["args"][0], 100, 100, allowed=(-1, 0, INF)) for t in tests]

# ---------------------------------------------------------------- distinct island shapes
add(
    id="distinct-island-shapes-count", title="Distinct Island Shapes", diff="Medium", topic="Graphs",
    fn="countDistinctShapes", params=[("grid", "int[][]")], ret="int", cmp="exact",
    desc="<p>In a binary <code>grid</code>, an island is a group of <code>1</code> cells connected through the four directions. Two islands have the <em>same shape</em> if one can be moved onto the other purely by sliding it (translation). Rotating or mirroring an island produces a <em>different</em> shape.</p><p>Return the number of distinct island shapes in the grid.</p><pre>grid = [[1,1,0,0,0],\n        [1,0,0,0,1],\n        [0,0,0,1,1],\n        [1,1,0,0,0],\n        [1,0,0,0,0]]   -> 2</pre><p>The islands at the top-left and bottom-left are the same L shape. The one in the right-middle is an L shape that is rotated, so it is different.</p>",
    constraints=["1 &le; rows, cols &le; 50", "grid[r][c] is 0 or 1", "The answer is 0 when the grid has no land"],
    hints=["First find all islands; then the real question is how to decide whether two islands are the same under sliding.",
           "If you describe each island by the positions of its cells relative to one fixed reference cell of that island, then sliding the island does not change the description.",
           "Scanning in row-major order, the first cell you reach in an island is always its top-most, left-most cell. Collect the offsets <code>(r - r0, c - c0)</code> of all its cells, sort them, and put them in a set."],
    editorial=["Scan the grid row by row. When you meet an unvisited land cell <code>(r0, c0)</code>, it is the first cell of a new island in scan order, so it plays the role of the island's anchor. Flood the island (stack or queue) and record every cell as the offset <code>(r - r0, c - c0)</code>.",
               "Sort the offsets into a tuple. Two islands that differ only by translation have exactly the same offset tuple, while a rotated or mirrored island has a different one. The answer is the size of the set of tuples. The work is proportional to the number of cells plus sorting each island, which is O(R &middot; C log(R &middot; C)) in the worst case and O(R &middot; C) space."],
    time="O(R &middot; C log(R &middot; C))", space="O(R &middot; C)",
    solution='''def countDistinctShapes(grid):
    rows, cols = len(grid), len(grid[0])
    seen = [[False] * cols for _ in range(rows)]
    shapes = set()
    for r0 in range(rows):
        for c0 in range(cols):
            if grid[r0][c0] == 1 and not seen[r0][c0]:
                seen[r0][c0] = True
                stack = [(r0, c0)]
                cells = []
                while stack:
                    y, x = stack.pop()
                    cells.append((y - r0, x - c0))
                    for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        ny, nx = y + dy, x + dx
                        if 0 <= ny < rows and 0 <= nx < cols and grid[ny][nx] == 1 and not seen[ny][nx]:
                            seen[ny][nx] = True
                            stack.append((ny, nx))
                shapes.add(tuple(sorted(cells)))
    return len(shapes)
''',
    tests=[[[[1, 1, 0, 0, 0], [1, 0, 0, 0, 1], [0, 0, 0, 1, 1], [1, 1, 0, 0, 0], [1, 0, 0, 0, 0]]], [[[0]]], [[[1]]],
           [[[1, 0, 1], [0, 0, 0], [1, 0, 1]]], [[[1, 1, 0, 1, 1]]], [[[1, 1, 0, 1], [0, 0, 0, 1]]],
           [[[1, 1, 0, 0, 1], [0, 1, 0, 0, 1], [0, 0, 0, 0, 0], [1, 0, 1, 1, 0], [1, 0, 0, 1, 0]]],
           [[[1, 0, 0, 1], [1, 1, 0, 1], [0, 0, 0, 1], [1, 1, 1, 0]]], [[[1, 1, 1], [1, 0, 1], [1, 1, 1]]],
           [[[1, 1, 0, 1, 0], [0, 1, 0, 1, 1]]]],
)
_r = rnd(7106)
_P[-1]["tests"].append([_bin_grid(_r, 50, 50, 0.4)])
_P[-1]["tests"].append([_bin_grid(_r, 50, 50, 0.3)])
_P[-1]["tests"].append([[[1 if (i % 3 != 2 and j % 4 != 3 and not (i % 3 == 1 and j % 4 == 1)) else 0 for j in range(50)] for i in range(50)]])  # many copies of one shape
_P[-1]["tests"].append([[[1 if (i % 2 == 0 and j % 2 == 0) else 0 for j in range(50)] for i in range(50)]])  # 625 single cells
_P[-1]["tests"].append([[[1] * 50 for _ in range(50)]])
_P[-1]["tests"].append([_bin_grid(_r, 50, 50, 0.52)])


def b_shapes(grid):
    shapes = set()
    for cells in _groups(grid, lambda v: v == 1):
        mr = min(a for a, b in cells)
        mc = min(b for a, b in cells)
        shapes.add(frozenset((a - mr, b - mc) for a, b in cells))
    return len(shapes)


CHECKS["distinct-island-shapes-count"] = (b_shapes, lambda r: [_bin_grid(r, r.randint(1, 7), r.randint(1, 7), r.choice([0.3, 0.45, 0.6]))], "exact")
VALIDATE["distinct-island-shapes-count"] = lambda tests: [_check_rect(t["args"][0], 50, 50, allowed=(0, 1)) for t in tests]

# ---------------------------------------------------------------- count sub-islands
add(
    id="count-sub-islands-contained", title="Count Contained Sub-Islands", diff="Medium", topic="Graphs",
    fn="countSubIslands", params=[("grid1", "int[][]"), ("grid2", "int[][]")], ret="int", cmp="exact",
    desc="<p>You are given two binary grids <code>grid1</code> and <code>grid2</code> of the same size. A <code>1</code> is land and a <code>0</code> is water; an island is a set of land cells connected through the four directions.</p><p>An island of <code>grid2</code> is <em>contained</em> if <strong>every</strong> one of its cells is also land in <code>grid1</code>. The island in <code>grid1</code> may be larger, but it must not be missing any cell of the <code>grid2</code> island. Return how many islands of <code>grid2</code> are contained.</p><pre>grid1 = [[1,1,1,0],\n         [0,1,1,0],\n         [0,0,0,0],\n         [1,0,1,1]]\ngrid2 = [[1,1,0,0],\n         [0,1,0,0],\n         [0,0,0,0],\n         [1,1,0,1]]   -> 2</pre><p>The top-left island of <code>grid2</code> is covered by <code>grid1</code>. The bottom-left one is not (its cell at row 3, column 1 is water in <code>grid1</code>). The single cell at the bottom right is covered.</p>",
    constraints=["1 &le; rows, cols &le; 100", "grid1 and grid2 have the same dimensions", "Every cell is 0 or 1"],
    hints=["Only the islands of grid2 are counted. Grid1 is just a lookup table.",
           "An island of grid2 fails as soon as one of its cells sits on water in grid1. But you must still finish exploring it, so that its remaining cells are not mistaken for a new island later.",
           "Flood each grid2 island completely with a stack, keeping a flag that turns false if any visited cell has <code>grid1 == 0</code>. Count the islands whose flag stayed true."],
    editorial=["Scan grid2. For each unvisited land cell, flood the whole island with an explicit stack and mark cells as visited. While doing so keep a boolean <code>ok</code> that becomes false when any cell has <code>grid1[r][c] == 0</code>. After the flood finishes, add one to the answer if <code>ok</code> is still true.",
               "It is important not to stop the flood early when <code>ok</code> turns false: the remaining cells of that island would otherwise be found later and counted as another island. Each cell is processed once, giving O(rows &times; cols) time and space."],
    time="O(R &middot; C)", space="O(R &middot; C)",
    solution='''def countSubIslands(grid1, grid2):
    rows, cols = len(grid2), len(grid2[0])
    seen = [[False] * cols for _ in range(rows)]
    count = 0
    for r in range(rows):
        for c in range(cols):
            if grid2[r][c] == 1 and not seen[r][c]:
                seen[r][c] = True
                stack = [(r, c)]
                ok = True
                while stack:
                    y, x = stack.pop()
                    if grid1[y][x] == 0:
                        ok = False
                    for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        ny, nx = y + dy, x + dx
                        if 0 <= ny < rows and 0 <= nx < cols and grid2[ny][nx] == 1 and not seen[ny][nx]:
                            seen[ny][nx] = True
                            stack.append((ny, nx))
                if ok:
                    count += 1
    return count
''',
    tests=[[[[1, 1, 1, 0], [0, 1, 1, 0], [0, 0, 0, 0], [1, 0, 1, 1]], [[1, 1, 0, 0], [0, 1, 0, 0], [0, 0, 0, 0], [1, 1, 0, 1]]],
           [[[1]], [[1]]], [[[1]], [[0]]], [[[0]], [[1]]], [[[0, 0]], [[0, 0]]], [[[1, 1, 1]], [[1, 0, 1]]],
           [[[1, 1, 1], [1, 1, 1], [1, 1, 1]], [[1, 0, 1], [0, 0, 0], [1, 0, 1]]],
           [[[1, 0, 1], [0, 0, 0], [1, 0, 1]], [[1, 1, 1], [1, 1, 1], [1, 1, 1]]],
           [[[1, 1, 0, 1, 1], [1, 0, 0, 0, 1]], [[1, 1, 0, 1, 0], [1, 0, 0, 0, 1]]],
           [[[1, 1, 1, 1], [1, 0, 0, 1], [1, 1, 1, 1]], [[1, 1, 1, 1], [1, 0, 0, 1], [1, 1, 0, 1]]]],
)
_r = rnd(7107)
_g2 = _bin_grid(_r, 100, 100, 0.45)
_g1 = [[1 if (v == 1 and _r.random() < 0.97) or (v == 0 and _r.random() < 0.3) else 0 for v in row] for row in _g2]
_P[-1]["tests"].append([_g1, _g2])
_g2 = _bin_grid(_r, 100, 100, 0.3)
_P[-1]["tests"].append([[[1 if (v == 1 or _r.random() < 0.2) else 0 for v in row] for row in _g2], _g2])  # grid1 is a superset: every island counts
_g2 = _bin_grid(_r, 100, 100, 0.55)
_P[-1]["tests"].append([_bin_grid(_r, 100, 100, 0.5), _g2])
_P[-1]["tests"].append([[[1] * 100 for _ in range(100)], _bin_grid(_r, 100, 100, 0.5)])
_P[-1]["tests"].append([[[0] * 100 for _ in range(100)], _bin_grid(_r, 100, 100, 0.5)])
_P[-1]["tests"].append([[[1] * 100 for _ in range(100)], [[1] * 100 for _ in range(100)]])


def b_sub(g1, g2):
    return sum(1 for cells in _groups(g2, lambda v: v == 1) if all(g1[a][b] == 1 for a, b in cells))


def g_sub(r):
    R, C = r.randint(1, 6), r.randint(1, 6)
    g2 = _bin_grid(r, R, C, r.choice([0.4, 0.6]))
    g1 = [[1 if (v and r.random() < 0.8) or (not v and r.random() < 0.3) else 0 for v in row] for row in g2]
    return [g1, g2]


def v_sub(tests):
    for t in tests:
        g1, g2 = t["args"]
        _check_rect(g1, 100, 100, allowed=(0, 1))
        _check_rect(g2, 100, 100, allowed=(0, 1))
        assert len(g1) == len(g2) and len(g1[0]) == len(g2[0]), "dimension mismatch"


CHECKS["count-sub-islands-contained"] = (b_sub, g_sub, "exact")
VALIDATE["count-sub-islands-contained"] = v_sub


# ---------------------------------------------------------------- shortest bridge
def _grow(r, R, C, start, size, blocked):
    cells = [start]
    inside = {start}
    tries = 0
    while len(cells) < size and tries < 60 * size:
        tries += 1
        a, b = r.choice(cells)
        da, db = r.choice(DIRS)
        q = (a + da, b + db)
        if 0 <= q[0] < R and 0 <= q[1] < C and q not in inside and q not in blocked:
            inside.add(q)
            cells.append(q)
    return inside


def _two_islands(r, R, C, sa, sb):
    """A grid with exactly two islands of about sa and sb cells (4-connected components)."""
    while True:
        a = _grow(r, R, C, (r.randrange(R), r.randrange(C)), sa, set())
        halo = set(a)
        for (i, j) in a:
            for di, dj in DIRS:
                halo.add((i + di, j + dj))
        free = [(i, j) for i in range(R) for j in range(C) if (i, j) not in halo]
        if not free:
            continue
        b = _grow(r, R, C, r.choice(free), sb, halo)
        g = [[1 if (i, j) in a or (i, j) in b else 0 for j in range(C)] for i in range(R)]
        if _comp_count(g) == 2:
            return g


add(
    id="shortest-bridge-between-islands", title="Shortest Bridge Between Islands", diff="Medium", topic="Graphs",
    fn="shortestBridge", params=[("grid", "int[][]")], ret="int", cmp="exact",
    desc="<p>A square <code>grid</code> of <code>0</code> (water) and <code>1</code> (land) contains <strong>exactly two</strong> islands. An island is a set of land cells connected through the four directions, and the two islands do not touch each other along an edge.</p><p>You may change water cells into land. Return the smallest number of water cells you must change so that the two islands become one single island.</p><pre>grid = [[1,1,0,0,0],\n        [1,0,0,0,0],\n        [0,0,0,1,0],\n        [0,0,0,1,1]]   -> 3</pre>",
    constraints=["2 &le; rows &times; cols and 1 &le; rows, cols &le; 100", "grid[r][c] is 0 or 1", "The grid contains exactly two islands"],
    hints=["The answer is the length of the shortest chain of water cells linking one island to the other.",
           "Find one island completely (with a flood fill). Then you want the shortest distance from any of its cells to the other island.",
           "Run a layered BFS that starts from all cells of the first island at once, crossing only water. The number of full layers completed before the search touches the second island is the number of cells to flip."],
    editorial=["Scan until you meet the first land cell and flood fill its island, marking the cells with a different value. These cells form the BFS start frontier at distance 0.",
               "Expand the frontier one layer at a time. Each layer adds the unvisited water neighbours of the current frontier. As soon as a neighbour is a land cell that is not yet marked, it belongs to the second island and the search has found the bridge; the number of water layers crossed so far is the answer. BFS visits each cell once, so the cost is O(rows &times; cols) time and space."],
    time="O(R &middot; C)", space="O(R &middot; C)",
    solution='''def shortestBridge(grid):
    rows, cols = len(grid), len(grid[0])
    seen = [[False] * cols for _ in range(rows)]
    start = None
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == 1:
                start = (r, c)
                break
        if start:
            break
    seen[start[0]][start[1]] = True
    stack = [start]
    frontier = []
    while stack:
        y, x = stack.pop()
        frontier.append((y, x))
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            ny, nx = y + dy, x + dx
            if 0 <= ny < rows and 0 <= nx < cols and grid[ny][nx] == 1 and not seen[ny][nx]:
                seen[ny][nx] = True
                stack.append((ny, nx))
    flips = 0
    while frontier:
        nxt = []
        for y, x in frontier:
            for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                ny, nx = y + dy, x + dx
                if 0 <= ny < rows and 0 <= nx < cols and not seen[ny][nx]:
                    if grid[ny][nx] == 1:
                        return flips
                    seen[ny][nx] = True
                    nxt.append((ny, nx))
        frontier = nxt
        flips += 1
    return -1
''',
    tests=[[[[1, 1, 0, 0, 0], [1, 0, 0, 0, 0], [0, 0, 0, 1, 0], [0, 0, 0, 1, 1]]], [[[1, 0, 1]]], [[[1, 0], [0, 1]]],
           [[[1, 0, 0, 1]]], [[[0, 1, 0], [0, 0, 0], [0, 1, 0]]], [[[1, 1, 1, 1, 1], [1, 0, 0, 0, 1], [1, 0, 1, 0, 1], [1, 0, 0, 0, 1], [1, 1, 1, 1, 1]]],
           [[[1, 1, 0, 1], [0, 0, 0, 0], [0, 0, 0, 0]]], [[[1], [0], [0], [0], [1]]],
           [[[0, 0, 0, 0], [0, 1, 1, 0], [0, 0, 0, 0], [0, 0, 0, 1]]], [[[1, 0, 0], [0, 0, 0], [0, 0, 1]]]],
)
_r = rnd(7108)
_P[-1]["tests"].append([_two_islands(_r, 100, 100, 900, 500)])
_P[-1]["tests"].append([_two_islands(_r, 100, 100, 3000, 20)])
_P[-1]["tests"].append([_two_islands(_r, 60, 100, 150, 150)])
_P[-1]["tests"].append([_two_islands(_r, 100, 30, 100, 100)])
_P[-1]["tests"].append([[[1 if (i, j) in ((0, 0), (99, 99)) else 0 for j in range(100)] for i in range(100)]])
_P[-1]["tests"].append([[[1 if (i == 0 or j == 0) else 0 for j in range(100)] for i in range(100)][:-1] + [[0] * 99 + [1]]])  # an L-shaped island and a far corner cell


def b_bridge(grid):
    isl = _groups(grid, lambda v: v == 1)
    assert len(isl) == 2
    a, b = isl
    return min(abs(p[0] - q[0]) + abs(p[1] - q[1]) for p in a for q in b) - 1


def _g_bridge_args(r):
    R, C = r.randint(2, 8), r.randint(2, 8)
    while R * C < 4:
        R, C = r.randint(2, 8), r.randint(2, 8)
    return [_two_islands(r, R, C, r.randint(1, max(1, R * C // 5)), r.randint(1, max(1, R * C // 5)))]


def v_bridge(tests):
    for t in tests:
        g = t["args"][0]
        _check_rect(g, 100, 100, allowed=(0, 1))
        assert _comp_count(g) == 2, "must have exactly two islands"
        assert t["expected"] >= 1


CHECKS["shortest-bridge-between-islands"] = (b_bridge, _g_bridge_args, "exact")
VALIDATE["shortest-bridge-between-islands"] = v_bridge


# =================================================================== HARD
# ---------------------------------------------------------------- minimum obstacle removal
def _obst(r, R, C, p):
    g = _bin_grid(r, R, C, p)
    g[0][0] = 0
    g[R - 1][C - 1] = 0
    return g


add(
    id="minimum-obstacle-removal-grid", title="Minimum Obstacle Removal in a Grid", diff="Hard", topic="Graphs",
    fn="minRemovals", params=[("grid", "int[][]")], ret="int", cmp="exact",
    desc="<p>In a <code>grid</code>, a <code>0</code> is an empty cell and a <code>1</code> is an obstacle. You stand at the top-left cell and want to reach the bottom-right cell by moving up, down, left or right. You may walk through empty cells freely, and you may also break through an obstacle, which removes it and costs 1.</p><p>Return the minimum number of obstacles you have to remove to reach the bottom-right cell. Both the start and the target cell are empty.</p><pre>grid = [[0,1,1],\n        [1,1,0],\n        [1,1,0]]   -> 2</pre>",
    constraints=["1 &le; rows, cols &le; 100", "grid[r][c] is 0 or 1", "grid[0][0] = grid[rows-1][cols-1] = 0"],
    hints=["The shortest route in steps is not what matters: stepping on an empty cell is free and breaking an obstacle costs 1.",
           "This is a shortest-path problem where entering a cell costs either 0 or 1. Dijkstra works. Can you do better using the fact that costs are only 0 and 1?",
           "Use a deque: when moving to a cell of cost 0 push the cell at the <em>front</em> of the deque, for cost 1 push it at the <em>back</em> (0-1 BFS). Update a distance array only when you find a strictly smaller value."],
    editorial=["Model each cell as a node and the cost of entering it as its value (0 or 1). The task is the cheapest path from the top-left to the bottom-right node. Plain BFS fails because edges have different weights, and Dijkstra is correct but pays a logarithmic factor for the heap.",
               "With weights restricted to 0 and 1, a deque replaces the heap: pop a cell from the front, and for each neighbour try <code>dist[cur] + grid[nb]</code>; if that improves the stored distance, store it and push the neighbour on the front when the cost is 0, otherwise on the back. The deque always stays ordered by distance, so each cell settles after a constant number of improvements. Total time is O(rows &times; cols)."],
    time="O(R &middot; C)", space="O(R &middot; C)",
    solution='''from collections import deque


def minRemovals(grid):
    rows, cols = len(grid), len(grid[0])
    BIG = 10 ** 9
    dist = [[BIG] * cols for _ in range(rows)]
    dist[0][0] = 0
    dq = deque([(0, 0)])
    while dq:
        y, x = dq.popleft()
        d = dist[y][x]
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            ny, nx = y + dy, x + dx
            if 0 <= ny < rows and 0 <= nx < cols:
                nd = d + grid[ny][nx]
                if nd < dist[ny][nx]:
                    dist[ny][nx] = nd
                    if grid[ny][nx] == 0:
                        dq.appendleft((ny, nx))
                    else:
                        dq.append((ny, nx))
    return dist[rows - 1][cols - 1]
''',
    tests=[[[[0, 1, 1], [1, 1, 0], [1, 1, 0]]], [[[0]]], [[[0, 0, 0], [0, 0, 0]]], [[[0, 1, 0]]], [[[0], [1], [0]]],
           [[[0, 1, 1, 1], [1, 1, 1, 1], [1, 1, 1, 0]]], [[[0, 1, 0, 0, 0], [0, 1, 0, 1, 0], [0, 0, 0, 1, 0]]],
           [[[0, 1, 0], [0, 1, 0], [0, 1, 0]]], [[[0, 1, 1], [1, 1, 1], [1, 1, 0]]],
           [[[0, 1, 0, 1, 0], [0, 1, 0, 1, 0], [0, 1, 0, 1, 0], [0, 0, 0, 0, 0]]]],
)
_r = rnd(7109)
_P[-1]["tests"].append([_obst(_r, 100, 100, 0.35)])
_P[-1]["tests"].append([_obst(_r, 100, 100, 0.5)])
_P[-1]["tests"].append([_obst(_r, 100, 100, 0.65)])
_P[-1]["tests"].append([[[0 if (i, j) in ((0, 0), (99, 99)) else 1 for j in range(100)] for i in range(100)]])
_P[-1]["tests"].append([[[1 if (i % 2 == 1 and j != (99 if i % 4 == 1 else 0)) else 0 for j in range(100)] for i in range(99)]])  # winding free corridor
_P[-1]["tests"].append([[[1 if i % 2 == 1 else 0 for j in range(100)] for i in range(99)]])  # solid walls on every other row
_P[-1]["tests"].append([[[1 if (j % 3 == 1 and i != (j * 7) % 100) else 0 for j in range(100)] for i in range(100)]])


def b_obst(grid):
    # Bellman-Ford style relaxation sweeps until nothing improves
    R, C = len(grid), len(grid[0])
    d = {(i, j): 10 ** 9 for i in range(R) for j in range(C)}
    d[(0, 0)] = 0
    changed = True
    while changed:
        changed = False
        for i in range(R):
            for j in range(C):
                for a, b in DIRS:
                    q = (i + a, j + b)
                    if q in d and d[q] + grid[i][j] < d[(i, j)]:
                        d[(i, j)] = d[q] + grid[i][j]
                        changed = True
    return d[(R - 1, C - 1)]


CHECKS["minimum-obstacle-removal-grid"] = (b_obst, lambda r: [_obst(r, r.randint(1, 6), r.randint(1, 6), r.choice([0.3, 0.5, 0.7]))], "exact")


def v_obst(tests):
    for t in tests:
        g = t["args"][0]
        _check_rect(g, 100, 100, allowed=(0, 1))
        assert g[0][0] == 0 and g[-1][-1] == 0


VALIDATE["minimum-obstacle-removal-grid"] = v_obst

# ---------------------------------------------------------------- swim in rising water
add(
    id="swim-in-rising-water-grid", title="Swim in Rising Water", diff="Hard", topic="Graphs",
    fn="swimInWater", params=[("elevation", "int[][]")], ret="int", cmp="exact",
    desc="<p>An <code>n x n</code> grid <code>elevation</code> holds the height of the ground at every cell; the heights are the distinct integers <code>0, 1, ..., n*n - 1</code>, each used once. At time <code>t</code> the water level everywhere is exactly <code>t</code>.</p><p>You start at the top-left cell and want to reach the bottom-right cell. In zero time you can move to an adjacent cell (up, down, left or right) when <em>both</em> the cell you stand on and the cell you move to have height at most <code>t</code>. You may wait for the water to rise as long as you like. Return the smallest <code>t</code> at which the bottom-right cell can be reached.</p><pre>elevation = [[0, 2],\n             [1, 3]]   -> 3</pre><p>At <code>t = 3</code> every cell is flooded enough to walk along the top row and down; before that the target (height 3) is still above the water.</p>",
    constraints=["1 &le; n &le; 100", "elevation is n x n and contains each of 0 .. n*n - 1 exactly once"],
    hints=["Walking a path is possible at time t iff the highest cell on the path is at most t. So you want a path whose highest cell is as low as possible.",
           "One approach: guess a time t and test with BFS whether the target is reachable using only cells of height at most t. Reachability only gets easier as t grows.",
           "Another: run a Dijkstra-like search with a min-heap keyed by the largest height seen on the way so far. The key of the target when it is first popped is the answer."],
    editorial=["The time to complete a path equals the maximum height of any cell on it, including start and end. The answer is the minimum, over all paths, of that maximum (a minimax path).",
               "A min-heap search handles it directly: start with <code>(elevation[0][0], 0, 0)</code>, pop the smallest key, and push each unvisited neighbour with key <code>max(key, height)</code>. Because keys come out of the heap in non-decreasing order, the first time the bottom-right cell is popped its key is the optimum. This costs O(n<sup>2</sup> log n).",
               "Alternatives: binary search on <code>t</code> with a BFS feasibility check (O(n<sup>2</sup> log n)), or add cells in increasing height order into a disjoint-set union and stop when the start and end become connected."],
    time="O(n^2 log n)", space="O(n^2)",
    solution='''import heapq


def swimInWater(elevation):
    n = len(elevation)
    seen = [[False] * n for _ in range(n)]
    heap = [(elevation[0][0], 0, 0)]
    seen[0][0] = True
    while heap:
        t, y, x = heapq.heappop(heap)
        if y == n - 1 and x == n - 1:
            return t
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            ny, nx = y + dy, x + dx
            if 0 <= ny < n and 0 <= nx < n and not seen[ny][nx]:
                seen[ny][nx] = True
                heapq.heappush(heap, (max(t, elevation[ny][nx]), ny, nx))
    return -1
''',
    tests=[[[[0, 2], [1, 3]]], [[[0]]], [[[0, 1, 2, 3, 4], [24, 23, 22, 21, 5], [12, 13, 14, 15, 16], [11, 17, 18, 19, 20], [10, 9, 8, 7, 6]]],
           [[[3, 2], [0, 1]]], [[[0, 1], [2, 3]]], [[[0, 3, 4], [1, 8, 5], [2, 7, 6]]],
           [[[8, 7, 6], [1, 0, 5], [2, 3, 4]]], [[[0, 8, 7], [1, 2, 6], [3, 4, 5]]],
           [[[4, 3, 2, 1], [5, 12, 13, 0], [6, 11, 14, 15], [7, 8, 9, 10]]], [[[0, 5, 6, 7], [1, 2, 3, 8], [15, 14, 4, 9], [13, 12, 11, 10]]]],
)
_r = rnd(7110)


def _perm(r, n):
    v = list(range(n * n))
    r.shuffle(v)
    return [v[i * n:(i + 1) * n] for i in range(n)]


def _spiral(n):
    g = [[0] * n for _ in range(n)]
    top, bot, left, right, k = 0, n - 1, 0, n - 1, 0
    while top <= bot and left <= right:
        for j in range(left, right + 1):
            g[top][j] = k; k += 1
        top += 1
        for i in range(top, bot + 1):
            g[i][right] = k; k += 1
        right -= 1
        if top <= bot:
            for j in range(right, left - 1, -1):
                g[bot][j] = k; k += 1
            bot -= 1
        if left <= right:
            for i in range(bot, top - 1, -1):
                g[i][left] = k; k += 1
            left += 1
    return g


def _stair(r, n):
    """A staircase path from corner to corner gets the lowest heights, in order; the rest is shuffled above."""
    path = []
    i = j = 0
    path.append((0, 0))
    while (i, j) != (n - 1, n - 1):
        if i == n - 1:
            j += 1
        elif j == n - 1:
            i += 1
        elif r.random() < 0.5:
            i += 1
        else:
            j += 1
        path.append((i, j))
    g = [[0] * n for _ in range(n)]
    on = set(path)
    rest = list(range(len(path), n * n))
    r.shuffle(rest)
    k = 0
    for i in range(n):
        for j in range(n):
            if (i, j) not in on:
                g[i][j] = rest[k]
                k += 1
    for idx, (i, j) in enumerate(path):
        g[i][j] = idx
    return g


_P[-1]["tests"].append([_perm(_r, 100)])
_P[-1]["tests"].append([_perm(_r, 50)])
_P[-1]["tests"].append([[[i * 70 + j for j in range(70)] for i in range(70)]])
_P[-1]["tests"].append([_spiral(100)])
_P[-1]["tests"].append([_stair(_r, 100)])
_P[-1]["tests"].append([_stair(_r, 37)])
_P[-1]["tests"].append([[[(i * 60 + j) if i % 2 == 0 else (i * 60 + 59 - j) for j in range(60)] for i in range(60)]])  # snake order


def b_swim(g):
    n = len(g)
    t = max(g[0][0], g[n - 1][n - 1])
    while True:
        seen = {(0, 0)}
        todo = [(0, 0)]
        while todo:
            a, b = todo.pop()
            for da, db in DIRS:
                x, y = a + da, b + db
                if 0 <= x < n and 0 <= y < n and (x, y) not in seen and g[x][y] <= t:
                    seen.add((x, y))
                    todo.append((x, y))
        if (n - 1, n - 1) in seen:
            return t
        t += 1


def v_swim(tests):
    for t in tests:
        g = t["args"][0]
        n = len(g)
        assert 1 <= n <= 100 and all(len(row) == n for row in g)
        assert sorted(v for row in g for v in row) == list(range(n * n)), "not a permutation"


CHECKS["swim-in-rising-water-grid"] = (b_swim, lambda r: [_perm(r, r.randint(1, 5))], "exact")
VALIDATE["swim-in-rising-water-grid"] = v_swim
