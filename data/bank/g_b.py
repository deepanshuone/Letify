"""Problems: grid DFS and flood fill (enclaves, island variants, perimeter, regions, shapes). See data/lib.py for the registry."""
from lib import add, rnd, CHECKS, VALIDATE, gen_arr  # noqa: F401

DIRS4 = ((1, 0), (-1, 0), (0, 1), (0, -1))
DIRS8 = DIRS4 + ((1, 1), (1, -1), (-1, 1), (-1, -1))


# ------------------------------------------------------------------ helpers used by tests, brute forces and validators
def _grid(r, R, C, p, vals=(0, 1)):
    """Random grid whose cells are vals[1] with probability p, else vals[0]."""
    return [[vals[1] if r.random() < p else vals[0] for _ in range(C)] for _ in range(R)]


def _comps(g, pred, diag=False):
    """Connected groups of cells where pred(value) holds (plain breadth first search, used by brute forces only)."""
    R, C = len(g), len(g[0])
    ds = DIRS8 if diag else DIRS4
    seen = [[False] * C for _ in range(R)]
    out = []
    for i in range(R):
        for j in range(C):
            if pred(g[i][j]) and not seen[i][j]:
                seen[i][j] = True
                q = [(i, j)]
                k = 0
                while k < len(q):
                    a, b = q[k]
                    k += 1
                    for da, db in ds:
                        x, y = a + da, b + db
                        if 0 <= x < R and 0 <= y < C and pred(g[x][y]) and not seen[x][y]:
                            seen[x][y] = True
                            q.append((x, y))
                out.append(q)
    return out


def _rect(g, rmax, cmax, allowed=None, lo=None, hi=None):
    assert 1 <= len(g) <= rmax, "rows"
    assert all(len(row) == len(g[0]) for row in g), "ragged"
    assert 1 <= len(g[0]) <= cmax, "cols"
    for row in g:
        for v in row:
            if allowed is not None:
                assert v in allowed, ("cell", v)
            if lo is not None:
                assert lo <= v <= hi, ("cell", v)


def _vgrid(rmax, cmax, allowed):
    return lambda tests: [_rect(t["args"][0], rmax, cmax, allowed=allowed) for t in tests]


# =================================================================== EASY
# ---------------------------------------------------------------- island sizes descending
p = add(
    id="island-sizes-descending", title="Island Sizes in Descending Order", diff="Easy", topic="Graphs",
    fn="islandSizes", params=[("grid", "int[][]")], ret="int[]", cmp="exact",
    desc="<p>In a binary <code>grid</code>, a <code>1</code> is land and a <code>0</code> is water. An island is a maximal group of land cells that are connected through the four directions (up, down, left, right).</p><p>Return the sizes (number of cells) of all islands, one number per island, sorted from the largest to the smallest. Return an empty array if there is no land.</p><pre>grid = [[1,1,0,0],\n        [1,0,0,1],\n        [0,0,1,1],\n        [1,0,0,0]]   -> [3,3,1]</pre>",
    constraints=["1 &le; rows, cols &le; 60", "grid[r][c] is 0 or 1", "Diagonal neighbours are <em>not</em> connected"],
    hints=["Count islands with a flood fill first. What extra number does each flood have to report?",
           "While flooding one island, count how many cells you visit. Mark visited cells so that no cell is counted twice.",
           "Collect one size per flood in a list, then sort the list in descending order at the end. Use an explicit stack to avoid deep recursion."],
    editorial=["Scan every cell. When an unvisited land cell is found, start a flood fill (DFS with an explicit stack) from it, mark every reached land cell as visited and count them. When the stack is empty the counter is the size of that island; append it to the answer list.",
               "Every cell is pushed at most once, so the scan costs O(R &middot; C). Sorting the k island sizes costs O(k log k), and k is at most R &middot; C / 2 ."],
    time="O(R &middot; C + k log k)", space="O(R &middot; C)",
    solution='''def islandSizes(grid):
    rows, cols = len(grid), len(grid[0])
    seen = [[False] * cols for _ in range(rows)]
    sizes = []
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == 1 and not seen[r][c]:
                seen[r][c] = True
                stack = [(r, c)]
                size = 0
                while stack:
                    y, x = stack.pop()
                    size += 1
                    for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        ny, nx = y + dy, x + dx
                        if 0 <= ny < rows and 0 <= nx < cols and grid[ny][nx] == 1 and not seen[ny][nx]:
                            seen[ny][nx] = True
                            stack.append((ny, nx))
                sizes.append(size)
    sizes.sort(reverse=True)
    return sizes
''',
    tests=[[[[1, 1, 0, 0], [1, 0, 0, 1], [0, 0, 1, 1], [1, 0, 0, 0]]], [[[0]]], [[[1]]], [[[0, 0], [0, 0]]], [[[1, 1], [1, 1]]],
           [[[1, 0, 1], [0, 1, 0], [1, 0, 1]]], [[[1, 1, 1, 0, 1, 1, 0, 1]]], [[[1], [0], [1], [1], [0], [1], [1], [1]]],
           [[[1, 1, 1], [1, 0, 1], [1, 1, 1]]], [[[1, 0, 0, 1], [0, 0, 0, 0], [0, 0, 0, 0], [1, 0, 0, 1]]]],
)
_r = rnd(8201)
p["tests"].append([_grid(_r, 60, 60, 0.45)])
p["tests"].append([_grid(_r, 60, 60, 0.6)])
p["tests"].append([[[1 if (i % 2 == 0 and j % 2 == 0) else 0 for j in range(60)] for i in range(60)]])
p["tests"].append([_grid(_r, 3, 60, 0.5)])


def b_sizes(grid):
    return sorted((len(c) for c in _comps(grid, lambda v: v == 1)), reverse=True)


CHECKS["island-sizes-descending"] = (b_sizes, lambda r: [_grid(r, r.randint(1, 7), r.randint(1, 7), r.choice([0.3, 0.5, 0.7]))], "exact")
VALIDATE["island-sizes-descending"] = _vgrid(60, 60, (0, 1))

# ---------------------------------------------------------------- count islands with diagonal links
p = add(
    id="count-islands-with-diagonal-links", title="Count Islands with Diagonal Links", diff="Easy", topic="Graphs",
    fn="countIslands8", params=[("grid", "int[][]")], ret="int", cmp="exact",
    desc="<p>In a binary <code>grid</code>, a <code>1</code> is land and a <code>0</code> is water. Two land cells are <em>linked</em> when they touch in any of the <strong>eight</strong> directions: horizontally, vertically or diagonally. An island is a maximal group of land cells connected through links.</p><p>Return the number of islands.</p><pre>grid = [[1,0,0,1],\n        [0,1,0,0],\n        [0,0,0,1],\n        [1,0,1,0]]   -> 4</pre><p>The cells <code>(0,0)</code> and <code>(1,1)</code> form one island, <code>(2,3)</code> and <code>(3,2)</code> form another, and <code>(0,3)</code> and <code>(3,0)</code> are single-cell islands, so there are 4 islands in total.</p>",
    constraints=["1 &le; rows, cols &le; 60", "grid[r][c] is 0 or 1"],
    hints=["This is the classic island count, only the neighbourhood is larger.",
           "Replace the list of four direction offsets by a list of eight: the four straight ones plus <code>(1,1), (1,-1), (-1,1), (-1,-1)</code>.",
           "Scan the grid; each time you meet an unvisited land cell, add one to the answer and flood-fill everything linked to it with an explicit stack."],
    editorial=["Do the usual flood-fill island count with eight neighbour offsets instead of four. Every time the scan meets an unvisited land cell, a new island has been found: increase the counter and flood all cells linked to it, marking them visited.",
               "Each cell is pushed at most once and looks at 8 neighbours, so the time is O(R &middot; C) and the extra space is O(R &middot; C) for the visited marks and the stack."],
    time="O(R &middot; C)", space="O(R &middot; C)",
    solution='''def countIslands8(grid):
    rows, cols = len(grid), len(grid[0])
    seen = [[False] * cols for _ in range(rows)]
    dirs = [(a, b) for a in (-1, 0, 1) for b in (-1, 0, 1) if (a, b) != (0, 0)]
    count = 0
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == 1 and not seen[r][c]:
                count += 1
                seen[r][c] = True
                stack = [(r, c)]
                while stack:
                    y, x = stack.pop()
                    for dy, dx in dirs:
                        ny, nx = y + dy, x + dx
                        if 0 <= ny < rows and 0 <= nx < cols and grid[ny][nx] == 1 and not seen[ny][nx]:
                            seen[ny][nx] = True
                            stack.append((ny, nx))
    return count
''',
    tests=[[[[1, 0, 0, 1], [0, 1, 0, 0], [0, 0, 0, 1], [1, 0, 1, 0]]], [[[0]]], [[[1]]], [[[1, 0], [0, 1]]], [[[0, 1], [1, 0]]],
           [[[1, 0, 1], [0, 0, 0], [1, 0, 1]]], [[[1, 0, 0], [0, 1, 0], [0, 0, 1]]], [[[1, 1, 1, 1, 1]]],
           [[[1, 0, 1, 0, 1]]], [[[0, 0], [0, 0]]], [[[1, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1], [1, 0, 0, 0]]]],
)
_r = rnd(8202)
p["tests"].append([_grid(_r, 60, 60, 0.3)])
p["tests"].append([_grid(_r, 60, 60, 0.45)])
p["tests"].append([[[1 if (i + j) % 2 == 0 else 0 for j in range(60)] for i in range(60)]])
p["tests"].append([[[1 if (i % 2 == 0 and j % 2 == 0) else 0 for j in range(60)] for i in range(60)]])


def b_islands8(grid):
    return len(_comps(grid, lambda v: v == 1, diag=True))


CHECKS["count-islands-with-diagonal-links"] = (b_islands8, lambda r: [_grid(r, r.randint(1, 7), r.randint(1, 7), r.choice([0.2, 0.35, 0.5]))], "exact")
VALIDATE["count-islands-with-diagonal-links"] = _vgrid(60, 60, (0, 1))

# =================================================================== MEDIUM
# ---------------------------------------------------------------- enclaves
p = add(
    id="enclave-land-cells-count", title="Count Enclave Land Cells", diff="Medium", topic="Graphs",
    fn="countEnclaves", params=[("grid", "int[][]")], ret="int", cmp="exact",
    desc="<p>A <code>grid</code> contains <code>1</code> for land and <code>0</code> for sea. From a land cell you may walk to a neighbouring land cell (up, down, left or right), and you may walk off the grid from any land cell that lies on the first row, last row, first column or last column.</p><p>A land cell is an <em>enclave cell</em> if it is <strong>impossible</strong> to walk off the grid starting from it (walking only over land). Return the number of enclave cells.</p><pre>grid = [[0,0,0,0],\n        [1,0,1,0],\n        [0,1,1,0],\n        [0,0,0,0]]   -> 3</pre><p>The land cell at <code>(1,0)</code> is on the left border so it can leave. The other three cells form a group that never touches the border.</p>",
    constraints=["1 &le; rows, cols &le; 60", "grid[r][c] is 0 or 1"],
    hints=["Asking which cells are trapped is awkward. Ask the opposite: which land cells can reach the border?",
           "All border land cells can leave by definition, and so can every land cell connected to one of them.",
           "Start a flood fill (stack or queue) from every border land cell at the same time. At the end the answer is the total number of land cells minus the number of cells the flood reached."],
    editorial=["Work backwards from the border. Put every land cell on the outer ring of the grid into a stack and mark it as escaped. Then repeatedly pop a cell and push its unvisited land neighbours, marking them as escaped too. A cell is marked exactly when there is a land path from the border to it, which, by symmetry of walking, is the same as having a land path from it to the border.",
               "Every land cell that was never marked cannot leave, so the answer is <code>total land - escaped land</code>. Each cell is pushed at most once: O(R &middot; C) time and space."],
    time="O(R &middot; C)", space="O(R &middot; C)",
    solution='''def countEnclaves(grid):
    rows, cols = len(grid), len(grid[0])
    seen = [[False] * cols for _ in range(rows)]
    stack = []
    for r in range(rows):
        for c in range(cols):
            if (r in (0, rows - 1) or c in (0, cols - 1)) and grid[r][c] == 1:
                seen[r][c] = True
                stack.append((r, c))
    while stack:
        y, x = stack.pop()
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            ny, nx = y + dy, x + dx
            if 0 <= ny < rows and 0 <= nx < cols and grid[ny][nx] == 1 and not seen[ny][nx]:
                seen[ny][nx] = True
                stack.append((ny, nx))
    total = sum(sum(row) for row in grid)
    escaped = sum(sum(1 for v in row if v) for row in seen)
    return total - escaped
''',
    tests=[[[[0, 0, 0, 0], [1, 0, 1, 0], [0, 1, 1, 0], [0, 0, 0, 0]]], [[[0]]], [[[1]]], [[[1, 1], [1, 1]]],
           [[[0, 1, 1, 0], [0, 0, 1, 0], [0, 0, 1, 0], [0, 0, 0, 0]]], [[[0, 0, 0], [0, 1, 0], [0, 0, 0]]],
           [[[1, 1, 1], [1, 1, 1], [1, 1, 1]]], [[[0, 1, 0, 0], [1, 0, 1, 0], [0, 1, 0, 1], [0, 0, 0, 0]]],
           [[[0, 0, 0, 0, 0], [0, 1, 1, 1, 0], [0, 1, 0, 1, 0], [0, 1, 1, 1, 0], [0, 0, 0, 0, 0]]],
           [[[1, 1, 1, 1, 1, 1], [1, 0, 0, 0, 0, 1], [1, 0, 1, 1, 0, 1], [1, 0, 0, 0, 0, 1], [1, 1, 1, 1, 1, 1]]],
           [[[1, 0, 1, 0, 1, 0, 1]]], [[[0, 0, 0, 0], [0, 1, 1, 0], [0, 1, 1, 0], [0, 0, 0, 1]]]],
)
_r = rnd(8203)
p["tests"].append([_grid(_r, 60, 60, 0.55)])
p["tests"].append([_grid(_r, 60, 60, 0.7)])
p["tests"].append([[[1] * 60 for _ in range(60)]])
_a = [[1 if (i % 4 != 3 and 0 < j < 59) else 0 for j in range(60)] for i in range(60)]
p["tests"].append([_a])


def b_enclaves(grid):
    R, C = len(grid), len(grid[0])
    free = {(i, j) for i in range(R) for j in range(C) if grid[i][j] == 1 and (i in (0, R - 1) or j in (0, C - 1))}
    changed = True
    while changed:
        changed = False
        for i in range(R):
            for j in range(C):
                if grid[i][j] == 1 and (i, j) not in free and any((i + a, j + b) in free for a, b in DIRS4):
                    free.add((i, j))
                    changed = True
    return sum(map(sum, grid)) - len(free)


CHECKS["enclave-land-cells-count"] = (b_enclaves, lambda r: [_grid(r, r.randint(1, 7), r.randint(1, 7), r.choice([0.4, 0.6, 0.8]))], "exact")
VALIDATE["enclave-land-cells-count"] = _vgrid(60, 60, (0, 1))

# ---------------------------------------------------------------- most exposed island perimeter
p = add(
    id="most-exposed-island-perimeter", title="Island with the Longest Perimeter", diff="Medium", topic="Graphs",
    fn="maxIslandPerimeter", params=[("grid", "int[][]")], ret="int", cmp="exact",
    desc="<p>In a binary <code>grid</code>, a <code>1</code> is a unit square of land and a <code>0</code> is water. An island is a maximal group of land squares connected through the four directions.</p><p>The <em>perimeter</em> of an island is the number of square sides that belong to its land squares and face water or the outside of the grid. Water enclosed inside an island (a lake) counts too, because its sides are also sides facing water. Return the largest perimeter among all islands, or <code>0</code> if the grid has no land.</p><pre>grid = [[1,1,1,0,0],\n        [1,0,1,0,1],\n        [1,1,1,0,0],\n        [0,0,0,0,1]]   -> 16</pre><p>The ring of eight cells has an outer boundary of 12 sides and a lake boundary of 4 sides, so its perimeter is 16. The two single cells have perimeter 4 each.</p>",
    constraints=["1 &le; rows, cols &le; 60", "grid[r][c] is 0 or 1"],
    hints=["First split the grid into islands. Then compute a perimeter per island and keep the maximum.",
           "For one land cell, the number of sides facing water or the outside is the number of its four neighbours that are water or off-grid.",
           "While flooding an island, add up that per-cell count over all visited cells. Compare the total with the best seen so far once the island is finished."],
    editorial=["Run a flood fill from each unvisited land cell. For every cell taken from the stack, look at its four neighbours: if a neighbour is outside the grid or is water, that side is part of the perimeter and adds one to the island total; if the neighbour is land and unvisited, push it.",
               "When the stack is empty the island total is its perimeter, so update the maximum. A lake inside the island needs no special handling, because its sides are land squares facing water and are counted automatically. Total work is O(R &middot; C)."],
    time="O(R &middot; C)", space="O(R &middot; C)",
    solution='''def maxIslandPerimeter(grid):
    rows, cols = len(grid), len(grid[0])
    seen = [[False] * cols for _ in range(rows)]
    best = 0
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == 1 and not seen[r][c]:
                seen[r][c] = True
                stack = [(r, c)]
                perimeter = 0
                while stack:
                    y, x = stack.pop()
                    for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        ny, nx = y + dy, x + dx
                        if not (0 <= ny < rows and 0 <= nx < cols) or grid[ny][nx] == 0:
                            perimeter += 1
                        elif not seen[ny][nx]:
                            seen[ny][nx] = True
                            stack.append((ny, nx))
                best = max(best, perimeter)
    return best
''',
    tests=[[[[1, 1, 1, 0, 0], [1, 0, 1, 0, 1], [1, 1, 1, 0, 0], [0, 0, 0, 0, 1]]], [[[0]]], [[[1]]], [[[1, 1], [1, 1]]],
           [[[1, 0, 1]]], [[[1, 1, 1, 1, 1]]], [[[1, 0, 1], [0, 0, 0], [1, 0, 1]]], [[[0, 0], [0, 0]]],
           [[[1, 0, 0, 0], [1, 0, 1, 1], [1, 0, 1, 0], [0, 0, 0, 0]]], [[[0, 1, 0], [1, 1, 1], [0, 1, 0]]],
           [[[1, 0, 1, 0, 1], [1, 1, 1, 1, 1], [1, 0, 1, 0, 1]]]],
)
_r = rnd(8204)
p["tests"].append([_grid(_r, 60, 60, 0.5)])
p["tests"].append([_grid(_r, 60, 60, 0.65)])
p["tests"].append([[[(i + j) % 2 for j in range(60)] for i in range(60)]])
p["tests"].append([[[1 if (i % 2 == 0 or j % 2 == 0) else 0 for j in range(60)] for i in range(60)]])


def b_maxperim(grid):
    R, C = len(grid), len(grid[0])
    best = 0
    for cells in _comps(grid, lambda v: v == 1):
        s = 0
        for i, j in cells:
            for a, b in DIRS4:
                x, y = i + a, j + b
                if not (0 <= x < R and 0 <= y < C) or grid[x][y] == 0:
                    s += 1
        best = max(best, s)
    return best


CHECKS["most-exposed-island-perimeter"] = (b_maxperim, lambda r: [_grid(r, r.randint(1, 7), r.randint(1, 7), r.choice([0.4, 0.6, 0.8]))], "exact")
VALIDATE["most-exposed-island-perimeter"] = _vgrid(60, 60, (0, 1))

# ---------------------------------------------------------------- regions cut by diagonal lines
p = add(
    id="regions-cut-by-diagonal-lines", title="Regions Cut by Diagonal Lines", diff="Medium", topic="Graphs", tier="extra",
    fn="countRegions", params=[("cells", "int[][]")], ret="int", cmp="exact",
    desc="<p>A rectangle is divided into unit squares. Each square either is empty or has one diagonal line drawn through it, from corner to corner. The array <code>cells</code> describes the squares row by row:</p><ul><li><code>0</code> &mdash; empty square, no line;</li><li><code>1</code> &mdash; a line from the bottom-left corner to the top-right corner (like <code>/</code>);</li><li><code>2</code> &mdash; a line from the top-left corner to the bottom-right corner (like <code>\\</code>).</li></ul><p>The lines cut the rectangle into regions. Return the number of regions.</p><pre>cells = [[0,1],\n         [1,0]]   -> 2\ncells = [[1,2],\n         [2,1]]   -> 5</pre><p>In the first example the two <code>/</code> lines join at the middle point and form one straight line from the top-right corner to the bottom-left corner of the 2 &times; 2 rectangle, which cuts it into 2 regions. In the second example the four lines form a diamond: 1 region inside the diamond and 4 corner triangles outside, 5 regions in total.</p>",
    constraints=["1 &le; rows, cols &le; 40", "cells[r][c] is 0, 1 or 2", "A line never leaves its own square"],
    hints=["A diagonal line is hard to represent on a grid of squares. Can you make the picture finer so that a line becomes a set of blocked cells?",
           "Blow every square up to a 3 &times; 3 block of small cells. An empty square becomes 9 free cells; a <code>/</code> square blocks the anti-diagonal of its block; a <code>\\</code> square blocks the main diagonal.",
           "Now count the connected groups of free small cells with a flood fill. Each group is one region."],
    editorial=["Upscale the picture by a factor of three. For a square at (r, c) the small block covers rows 3r..3r+2 and columns 3c..3c+2. A <code>/</code> blocks the small cells (0,2), (1,1), (2,0) of the block and a <code>\\</code> blocks (0,0), (1,1), (2,2). The lines of neighbouring squares meet exactly at the shared corners, so they remain connected in the finer grid, while the free triangles on both sides of a line stay separated (the diagonal cells are blocked and there is no way to step across a diagonal with four-directional moves).",
               "The number of regions of the original picture equals the number of 4-connected groups of free cells in the (3R) &times; (3C) grid. Count them with a flood fill and an explicit stack. The grid has at most 120 &times; 120 small cells, so the time is O(R &middot; C) with a constant of 9. Another well-known solution uses union-find with four triangles per square."],
    time="O(R &middot; C)", space="O(R &middot; C)",
    solution='''def countRegions(cells):
    R, C = len(cells), len(cells[0])
    H, W = 3 * R, 3 * C
    blocked = [[False] * W for _ in range(H)]
    for r in range(R):
        for c in range(C):
            if cells[r][c] == 1:
                for k in range(3):
                    blocked[3 * r + k][3 * c + 2 - k] = True
            elif cells[r][c] == 2:
                for k in range(3):
                    blocked[3 * r + k][3 * c + k] = True
    regions = 0
    for i in range(H):
        for j in range(W):
            if not blocked[i][j]:
                regions += 1
                blocked[i][j] = True
                stack = [(i, j)]
                while stack:
                    y, x = stack.pop()
                    for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        ny, nx = y + dy, x + dx
                        if 0 <= ny < H and 0 <= nx < W and not blocked[ny][nx]:
                            blocked[ny][nx] = True
                            stack.append((ny, nx))
    return regions
''',
    tests=[[[[0, 1], [1, 0]]], [[[1, 2], [2, 1]]], [[[0]]], [[[1]]], [[[2]]], [[[0, 0], [0, 0]]], [[[1, 2]]], [[[2, 1]]],
           [[[2, 2], [2, 2]]], [[[1, 1, 1]]], [[[0, 2, 0], [2, 0, 2], [0, 2, 0]]], [[[1, 2, 1], [2, 1, 2], [1, 2, 1]]],
           [[[2, 0, 0], [0, 2, 0], [0, 0, 2]]]],
)
_r = rnd(8205)
p["tests"].append([_grid(_r, 40, 40, 0.5, vals=(0, 1))])
p["tests"].append([[[_r.choice([0, 1, 2]) for _ in range(40)] for _ in range(40)]])
p["tests"].append([[[_r.choice([1, 2]) for _ in range(40)] for _ in range(40)]])
p["tests"].append([[[1 if (i + j) % 2 == 0 else 2 for j in range(40)] for i in range(40)]])


def b_regions(cells):
    # union-find over four triangles (0 top, 1 right, 2 bottom, 3 left) of each square
    R, C = len(cells), len(cells[0])
    par = list(range(4 * R * C))

    def find(x):
        while par[x] != x:
            par[x] = par[par[x]]
            x = par[x]
        return x

    def union(a, b):
        par[find(a)] = find(b)

    def t(i, j, k):
        return 4 * (i * C + j) + k

    for i in range(R):
        for j in range(C):
            v = cells[i][j]
            if v == 0:
                union(t(i, j, 0), t(i, j, 1)); union(t(i, j, 1), t(i, j, 2)); union(t(i, j, 2), t(i, j, 3))
            elif v == 1:
                union(t(i, j, 0), t(i, j, 3)); union(t(i, j, 1), t(i, j, 2))
            else:
                union(t(i, j, 0), t(i, j, 1)); union(t(i, j, 2), t(i, j, 3))
            if i + 1 < R:
                union(t(i, j, 2), t(i + 1, j, 0))
            if j + 1 < C:
                union(t(i, j, 1), t(i, j + 1, 3))
    return len({find(x) for x in range(4 * R * C)})


def _gen_regions(r):
    R, C = r.randint(1, 6), r.randint(1, 6)
    return [[r.choice([0, 1, 2]) for _ in range(C)] for _ in range(R)]


CHECKS["regions-cut-by-diagonal-lines"] = (b_regions, lambda r: [_gen_regions(r)], "exact")
VALIDATE["regions-cut-by-diagonal-lines"] = _vgrid(40, 40, (0, 1, 2))

# ---------------------------------------------------------------- path with maximum gold
p = add(
    id="max-gold-single-walk", title="Maximum Gold in a Single Walk", diff="Medium", topic="Graphs", tier="common",
    fn="maxGold", params=[("grid", "int[][]")], ret="int", cmp="exact",
    desc="<p>A <code>grid</code> describes a gold mine: <code>grid[r][c]</code> is the amount of gold in that cell, and <code>0</code> means the cell is empty rock.</p><p>You choose any cell that holds gold as the start, and then walk. Each step goes to a neighbouring cell (up, down, left or right) that holds gold. You collect the gold of every cell you step on, but you may <strong>not step on the same cell twice</strong>, and you may stop at any moment. Return the largest total amount of gold you can collect, or <code>0</code> if the mine has no gold.</p><pre>grid = [[0,3,0],\n        [4,9,5],\n        [0,2,0]]   -> 18\ngrid = [[2,2],\n        [2,2]]     -> 8</pre><p>In the first example the best walk is 4, 9, 5. In the second example the walk can go around all four cells.</p>",
    constraints=["1 &le; rows, cols &le; 15", "0 &le; grid[r][c] &le; 100", "At most 18 cells contain gold"],
    hints=["The walk may turn in any direction, so a greedy choice of the largest neighbour does not work.",
           "Try every starting cell and explore every possible walk from it. With at most 18 gold cells the number of walks is small enough.",
           "Use backtracking: take the gold of the current cell (set it to 0 to mark it as used), recurse into the four neighbours that still hold gold, then restore the cell before returning."],
    editorial=["This is a depth-first search with backtracking. From each gold cell, collect its gold and temporarily set the cell to zero, so that it cannot be entered again on the current walk. Then try each of the four neighbours that still have gold and keep the best total returned by them. Finally restore the original value so that other walks can use the cell.",
               "The answer is the best value over all starting cells. In the worst case a walk visits all 18 gold cells, but because gold cells are capped, the number of simple walks in a grid is small enough to enumerate (a full 4 &times; 4 block has only a few thousand simple walks). The time is exponential in the number of gold cells, O(k &middot; 3<sup>k</sup>), and the space is O(k) for the recursion."],
    time="O(k &middot; 3^k), k = gold cells", space="O(k)",
    solution='''def maxGold(grid):
    rows, cols = len(grid), len(grid[0])

    def walk(y, x):
        gold = grid[y][x]
        grid[y][x] = 0
        best = 0
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            ny, nx = y + dy, x + dx
            if 0 <= ny < rows and 0 <= nx < cols and grid[ny][nx] > 0:
                best = max(best, walk(ny, nx))
        grid[y][x] = gold
        return gold + best

    answer = 0
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] > 0:
                answer = max(answer, walk(r, c))
    return answer
''',
    tests=[[[[0, 3, 0], [4, 9, 5], [0, 2, 0]]], [[[2, 2], [2, 2]]], [[[0]]], [[[7]]], [[[0, 0], [0, 0]]], [[[1, 0, 5]]],
           [[[1, 2, 3, 4]]], [[[5, 0, 5], [0, 0, 0], [5, 0, 5]]], [[[10, 1, 1], [1, 0, 1], [1, 1, 10]]],
           [[[1, 1, 1], [1, 1, 1], [1, 1, 1]]], [[[3, 0, 6], [2, 0, 4], [1, 9, 7], [0, 2, 0]]],
           [[[100, 1, 100], [1, 50, 1], [100, 1, 100]]]],
)
p["tests"].append([[[(r * 7 + c * 3) % 20 + 1 if (r * 4 + c) % 5 != 0 else 0 for c in range(5)] for r in range(4)]])
p["tests"].append([[[(r * 11 + c * 5) % 90 + 10 for c in range(6)] for r in range(3)]])
p["tests"].append([[[(r * 13 + c * 7) % 90 + 10 if r < 4 and c < 4 else 0 for c in range(15)] for r in range(15)]])


def b_gold(grid):
    R, C = len(grid), len(grid[0])
    cells = [(i, j) for i in range(R) for j in range(C) if grid[i][j] > 0]
    best = 0

    def extend(path):
        nonlocal best
        best = max(best, sum(grid[i][j] for i, j in path))
        i, j = path[-1]
        for a, b in DIRS4:
            nxt = (i + a, j + b)
            if nxt in cells and nxt not in path:
                extend(path + [nxt])

    for c in cells:
        extend([c])
    return best


def g_gold(r):
    R, C = r.randint(1, 4), r.randint(1, 4)
    return [[r.choice([0, 0, 1, 2, 5, 9]) for _ in range(C)] for _ in range(R)]


def v_gold(tests):
    for t in tests:
        g = t["args"][0]
        _rect(g, 15, 15, lo=0, hi=100)
        assert sum(1 for row in g for v in row if v) <= 18, "too many gold cells"


CHECKS["max-gold-single-walk"] = (b_gold, lambda r: [g_gold(r)], "exact")
VALIDATE["max-gold-single-walk"] = v_gold

# ---------------------------------------------------------------- cycle in grid of equal values
p = add(
    id="cycle-of-equal-values-in-grid", title="Cycle of Equal Values in a Grid", diff="Medium", topic="Graphs",
    fn="hasValueCycle", params=[("grid", "int[][]")], ret="bool", cmp="exact",
    desc="<p>Every cell of the <code>grid</code> holds a small integer, think of it as a letter. A <em>cycle</em> is a walk of length at least 4 that starts and ends at the same cell, moves up, down, left or right at each step, visits only cells with the <strong>same value</strong> as the start, and never enters a cell twice except for returning to the start at the very end. In particular, a walk may not immediately step back to the cell it just came from.</p><p>Return <code>true</code> if the grid contains at least one cycle, otherwise <code>false</code>.</p><pre>grid = [[1,1,1],\n        [1,2,1],\n        [1,1,1]]   -> true   (the ring of eight 1s)\ngrid = [[1,1,2],\n        [2,1,2]]   -> false</pre>",
    constraints=["1 &le; rows, cols &le; 60", "1 &le; grid[r][c] &le; 26"],
    hints=["Think of the cells as vertices of a graph, with an edge between two adjacent cells holding equal values. The question is whether this graph contains a cycle.",
           "In a DFS on an undirected graph, meeting an already visited vertex that is not the vertex you just came from means a cycle exists. Pass the parent cell down the recursion (or store it on the stack).",
           "Run the DFS from every unvisited cell, restricted to cells of the same value as the start, with an explicit stack of (cell, parent) pairs. Any visited neighbour that is not the parent proves a cycle."],
    editorial=["Build the graph implicitly: two adjacent cells are connected when their values are equal. A connected, undirected graph is a tree exactly when it has no cycle, and a DFS finds a cycle as soon as it meets a visited vertex other than its parent. Because the grid is bipartite, any such cycle automatically has even length of at least 4, so the 'at least 4' rule in the statement needs no extra check.",
               "Scan all cells; from each unvisited cell, run an iterative DFS that stores (cell, parent) on the stack. Mark a cell visited when it is pushed. When looking at a neighbour with the same value, skip the parent; if the neighbour is already visited, return true. If all searches finish, return false. This costs O(R &middot; C) time and space. A union-find sweep that unites each cell with its equal up and left neighbours, and reports a cycle when they are already united, is an alternative."],
    time="O(R &middot; C)", space="O(R &middot; C)",
    solution='''def hasValueCycle(grid):
    rows, cols = len(grid), len(grid[0])
    seen = [[False] * cols for _ in range(rows)]
    for r in range(rows):
        for c in range(cols):
            if seen[r][c]:
                continue
            seen[r][c] = True
            stack = [(r, c, -1, -1)]
            while stack:
                y, x, py, px = stack.pop()
                for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    ny, nx = y + dy, x + dx
                    if not (0 <= ny < rows and 0 <= nx < cols) or grid[ny][nx] != grid[y][x]:
                        continue
                    if (ny, nx) == (py, px):
                        continue
                    if seen[ny][nx]:
                        return True
                    seen[ny][nx] = True
                    stack.append((ny, nx, y, x))
    return False
''',
    tests=[[[[1, 1, 1], [1, 2, 1], [1, 1, 1]]], [[[1, 1, 2], [2, 1, 2]]], [[[1]]], [[[1, 1], [1, 1]]], [[[1, 2], [2, 1]]],
           [[[1, 1, 1, 1]]], [[[1, 2, 1], [2, 1, 2], [1, 2, 1]]], [[[3, 3, 3], [3, 4, 3], [3, 3, 4]]],
           [[[1, 1, 1], [1, 2, 2], [1, 1, 1]]], [[[1, 1, 1, 1], [1, 2, 2, 1], [1, 2, 2, 2], [1, 1, 1, 1]]],
           [[[1, 2, 3], [4, 5, 6], [7, 8, 9]]], [[[5, 5, 5], [5, 6, 5], [5, 6, 6], [5, 5, 5]]]],
)
_r = rnd(8206)
p["tests"].append([_grid(_r, 60, 60, 0.5, vals=(1, 2))])
# all neighbours differ in value: no cycle anywhere
_a = [[3 + ((i // 2) * 7 + j * 3 + (i % 2)) % 20 for j in range(60)] for i in range(60)]
p["tests"].append([_a])
# a comb of 1s (a tree: no cycle) in a checkerboard of 2s and 3s
_b = [[(2 + (i + j) % 2) for j in range(60)] for i in range(60)]
for j in range(60):
    _b[0][j] = 1
for j in range(0, 60, 2):
    for i in range(0, 59):
        _b[i][j] = 1
p["tests"].append([_b])
_c = [row[:] for row in _b]
_c[10][1] = 1
_c[10][3] = 1
_c[9][1] = 1
_c[9][3] = 1
p["tests"].append([_c])
p["tests"].append([[[_r.randint(1, 3) for _ in range(60)] for _ in range(60)]])


def b_cycle(grid):
    # a connected graph has a cycle exactly when it has at least as many edges as vertices
    R, C = len(grid), len(grid[0])
    seen = set()
    for i in range(R):
        for j in range(C):
            if (i, j) in seen:
                continue
            v = grid[i][j]
            comp = [(i, j)]
            seen.add((i, j))
            k = 0
            while k < len(comp):
                a, b = comp[k]
                k += 1
                for da, db in DIRS4:
                    x, y = a + da, b + db
                    if 0 <= x < R and 0 <= y < C and grid[x][y] == v and (x, y) not in seen:
                        seen.add((x, y))
                        comp.append((x, y))
            members = set(comp)
            edges = sum(1 for a, b in comp for da, db in ((1, 0), (0, 1)) if (a + da, b + db) in members)
            if edges >= len(comp):
                return True
    return False


def g_cycle(r):
    R, C = r.randint(1, 5), r.randint(1, 5)
    k = r.randint(1, 4)
    return [[r.randint(1, k) for _ in range(C)] for _ in range(R)]


def v_cycle(tests):
    for t in tests:
        _rect(t["args"][0], 60, 60, lo=1, hi=26)
    flags = [t["expected"] for t in tests]
    assert True in flags and False in flags, "both answers should occur"


CHECKS["cycle-of-equal-values-in-grid"] = (b_cycle, lambda r: [g_cycle(r)], "exact")
VALIDATE["cycle-of-equal-values-in-grid"] = v_cycle

# ---------------------------------------------------------------- farmland rectangles
p = add(
    id="farmland-rectangles-listing", title="List the Farmland Rectangles", diff="Medium", topic="Graphs", tier="extra",
    fn="findFarmland", params=[("land", "int[][]")], ret="int[][]", cmp="rowset",
    desc="<p>A <code>land</code> map uses <code>1</code> for a farmland cell and <code>0</code> for forest. Every maximal group of farmland cells connected through the four directions is guaranteed to fill an axis-aligned rectangle completely, and no two different groups touch each other horizontally or vertically (they may touch diagonally).</p><p>For every group return its bounding box as <code>[r1, c1, r2, c2]</code>, where <code>(r1, c1)</code> is the top-left cell and <code>(r2, c2)</code> the bottom-right cell. Return the boxes sorted by <code>r1</code>, then by <code>c1</code>. If there is no farmland return an empty array.</p><pre>land = [[1,1,0,0],\n        [1,1,0,1],\n        [0,0,0,1],\n        [1,0,0,0]]\n\nresult = [[0,0,1,1],[1,3,2,3],[3,0,3,0]]</pre>",
    constraints=["1 &le; rows, cols &le; 60", "land[r][c] is 0 or 1", "Every group of farmland cells is a filled rectangle; groups are never horizontally or vertically adjacent"],
    hints=["You are promised that each group is a full rectangle, so you do not need a general flood fill: the top-left corner and the bottom-right corner describe the whole group.",
           "A cell is the top-left corner of its rectangle exactly when it is farmland and the cell above and the cell to the left are not farmland.",
           "Scan the grid in row-major order (this also gives the required sorting). At a top-left corner, walk right while cells are farmland to find <code>c2</code>, and walk down to find <code>r2</code>."],
    editorial=["Because every group is a filled rectangle, we can find a group by its top-left corner: a farmland cell whose upper neighbour and left neighbour are both missing or forest. No other cell of a rectangle has this property. Scanning rows from top to bottom and columns from left to right meets the corners in exactly the order the answer requires.",
               "At each corner, extend downwards along the same column while cells are farmland to get <code>r2</code>, and extend to the right along the same row to get <code>c2</code>. The extensions cost at most the perimeter of each rectangle, so the total time is O(R &middot; C). A flood fill that tracks the minimum and maximum row and column of each group is a more general alternative that does not depend on the rectangle guarantee."],
    time="O(R &middot; C)", space="O(1) extra",
    solution='''def findFarmland(land):
    rows, cols = len(land), len(land[0])
    result = []
    for r in range(rows):
        for c in range(cols):
            if land[r][c] != 1:
                continue
            if r > 0 and land[r - 1][c] == 1:
                continue
            if c > 0 and land[r][c - 1] == 1:
                continue
            r2, c2 = r, c
            while r2 + 1 < rows and land[r2 + 1][c] == 1:
                r2 += 1
            while c2 + 1 < cols and land[r][c2 + 1] == 1:
                c2 += 1
            result.append([r, c, r2, c2])
    return result
''',
    tests=[[[[1, 1, 0, 0], [1, 1, 0, 1], [0, 0, 0, 1], [1, 0, 0, 0]]], [[[0]]], [[[1]]], [[[1, 1], [1, 1]]], [[[0, 0], [0, 0]]],
           [[[1, 0, 1, 0, 1]]], [[[1], [0], [1], [1]]], [[[1, 0, 0], [0, 1, 0], [0, 0, 1]]],
           [[[1, 1, 0, 1], [1, 1, 0, 1], [0, 0, 0, 0], [1, 1, 1, 0]]], [[[0, 1, 1, 1], [0, 1, 1, 1], [0, 0, 0, 0], [1, 0, 1, 1]]]],
)


def _gen_farm(r, R, C, tries):
    g = [[0] * C for _ in range(R)]
    for _ in range(tries):
        h, w = r.randint(1, max(1, R // 3)), r.randint(1, max(1, C // 3))
        r1, c1 = r.randint(0, R - h), r.randint(0, C - w)
        r2, c2 = r1 + h - 1, c1 + w - 1
        ok = True
        for i in range(r1 - 1, r2 + 2):
            for j in range(c1 - 1, c2 + 2):
                inside = r1 <= i <= r2 and c1 <= j <= c2
                corner = (i in (r1 - 1, r2 + 1)) and (j in (c1 - 1, c2 + 1))
                if corner:
                    continue
                if 0 <= i < R and 0 <= j < C and g[i][j] == 1:
                    ok = False
        if ok:
            for i in range(r1, r2 + 1):
                for j in range(c1, c2 + 1):
                    g[i][j] = 1
    return g


_r = rnd(8207)
p["tests"].append([_gen_farm(_r, 60, 60, 400)])
p["tests"].append([_gen_farm(_r, 60, 60, 60)])
p["tests"].append([[[1] * 60 for _ in range(60)]])
p["tests"].append([[[1 if (i % 2 == 0 and j % 2 == 0) else 0 for j in range(60)] for i in range(60)]])
p["tests"].append([_gen_farm(_r, 8, 50, 100)])


def b_farm(land):
    out = []
    for cells in _comps(land, lambda v: v == 1):
        out.append([min(a for a, b in cells), min(b for a, b in cells), max(a for a, b in cells), max(b for a, b in cells)])
    return sorted(out)


def g_farm(r):
    R, C = r.randint(1, 8), r.randint(1, 8)
    return [_gen_farm(r, R, C, r.randint(0, 12))]


def v_farm(tests):
    for t in tests:
        g = t["args"][0]
        _rect(g, 60, 60, allowed=(0, 1))
        for cells in _comps(g, lambda v: v == 1):
            r1, c1 = min(a for a, b in cells), min(b for a, b in cells)
            r2, c2 = max(a for a, b in cells), max(b for a, b in cells)
            assert len(cells) == (r2 - r1 + 1) * (c2 - c1 + 1), "group is not a filled rectangle"
        assert t["expected"] == sorted(t["expected"])


CHECKS["farmland-rectangles-listing"] = (b_farm, g_farm, "rowset")
VALIDATE["farmland-rectangles-listing"] = v_farm

# =================================================================== HARD
# ---------------------------------------------------------------- largest island after one flip
p = add(
    id="largest-island-after-one-flip", title="Largest Island After One Flip", diff="Hard", topic="Graphs", tier="common",
    fn="largestIsland", params=[("grid", "int[][]")], ret="int", cmp="exact",
    desc="<p>In a binary <code>grid</code> a <code>1</code> is land and a <code>0</code> is water. An island is a maximal group of land cells connected through the four directions.</p><p>You may change <strong>at most one</strong> water cell into land. Return the size of the largest island you can have afterwards. If the grid contains no water, nothing can be changed and the answer is the size of the whole grid.</p><pre>grid = [[1,1,0],\n        [0,0,1],\n        [0,1,1]]   -> 6</pre><p>Turning the centre cell <code>(1,1)</code> into land joins the island of size 2 (top-left) with the island of size 3 (bottom-right): 2 + 3 + 1 = 6.</p>",
    constraints=["1 &le; rows, cols &le; 60", "grid[r][c] is 0 or 1"],
    hints=["Trying every water cell and recounting the islands from scratch costs O((R &middot; C)<sup>2</sup>). Can the island sizes be computed once?",
           "Label each island with an id and store its size. A water cell that is flipped joins the islands of its four neighbours.",
           "For each water cell, collect the <em>distinct</em> island ids around it (a set of up to four ids; two neighbours can belong to the same island), and add 1 plus the sizes of those islands. Also consider the case of no flip, which matters when there is no water."],
    editorial=["First flood-fill every island and give it an id; keep <code>size[id]</code> and a <code>label</code> grid. Then look at each water cell: flipping it creates an island made of the new cell and every neighbouring island. Because two neighbours may belong to the same island, take the set of their ids before summing the sizes, otherwise one island would be counted twice.",
               "The answer is the maximum over all water cells of <code>1 + sum of sizes of distinct neighbouring islands</code>, and also the largest existing island (relevant when there is no water cell, in which case the whole grid is one island). Everything is O(R &middot; C) time and space."],
    time="O(R &middot; C)", space="O(R &middot; C)",
    solution='''def largestIsland(grid):
    rows, cols = len(grid), len(grid[0])
    label = [[0] * cols for _ in range(rows)]
    size = [0]
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == 1 and label[r][c] == 0:
                ident = len(size)
                label[r][c] = ident
                stack = [(r, c)]
                count = 0
                while stack:
                    y, x = stack.pop()
                    count += 1
                    for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        ny, nx = y + dy, x + dx
                        if 0 <= ny < rows and 0 <= nx < cols and grid[ny][nx] == 1 and label[ny][nx] == 0:
                            label[ny][nx] = ident
                            stack.append((ny, nx))
                size.append(count)
    best = max(size)
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == 0:
                ids = set()
                for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    ny, nx = r + dy, c + dx
                    if 0 <= ny < rows and 0 <= nx < cols and grid[ny][nx] == 1:
                        ids.add(label[ny][nx])
                best = max(best, 1 + sum(size[i] for i in ids))
    return best
''',
    tests=[[[[1, 1, 0], [0, 0, 1], [0, 1, 1]]], [[[0]]], [[[1]]], [[[1, 1], [1, 1]]], [[[1, 0]]], [[[1, 0, 1]]],
           [[[0, 0], [0, 0]]], [[[1, 0], [0, 1]]], [[[1, 0, 1], [0, 1, 0], [1, 0, 1]]], [[[1, 1, 1], [1, 0, 1], [1, 1, 1]]],
           [[[1, 1, 0, 1, 1], [1, 1, 0, 1, 1], [0, 0, 0, 0, 0], [1, 0, 0, 0, 1]]], [[[0, 1, 0], [1, 0, 1], [0, 1, 0]]]],
)
_r = rnd(8208)
p["tests"].append([_grid(_r, 60, 60, 0.55)])
p["tests"].append([_grid(_r, 60, 60, 0.4)])
p["tests"].append([[[1] * 60 for _ in range(60)]])
p["tests"].append([[[0 if (i % 3 == 1 and j % 5 == 2) else 1 for j in range(60)] for i in range(60)]])


def b_flip(grid):
    R, C = len(grid), len(grid[0])

    def biggest(g):
        return max([len(c) for c in _comps(g, lambda v: v == 1)] or [0])

    best = biggest(grid)
    for i in range(R):
        for j in range(C):
            if grid[i][j] == 0:
                g2 = [row[:] for row in grid]
                g2[i][j] = 1
                best = max(best, biggest(g2))
    return best


CHECKS["largest-island-after-one-flip"] = (b_flip, lambda r: [_grid(r, r.randint(1, 6), r.randint(1, 6), r.choice([0.3, 0.55, 0.8]))], "exact")
VALIDATE["largest-island-after-one-flip"] = _vgrid(60, 60, (0, 1))

# ---------------------------------------------------------------- distinct islands up to rotation and reflection
p = add(
    id="distinct-islands-rotate-reflect", title="Distinct Islands Up to Rotation and Reflection", diff="Hard", topic="Graphs", tier="extra",
    fn="countShapeClasses", params=[("grid", "int[][]")], ret="int", cmp="exact",
    desc="<p>In a binary <code>grid</code> an island is a maximal group of <code>1</code> cells connected through the four directions. Two islands are considered the <em>same shape</em> if one can be turned into the other by any combination of sliding (translation), rotating by 90, 180 or 270 degrees, and mirroring (left-right or up-down flip).</p><p>Return the number of different shapes among the islands of the grid.</p><pre>grid = [[1,1,0,0,0],\n        [1,0,0,1,1],\n        [0,0,0,0,1],\n        [1,0,0,0,0],\n        [1,1,0,1,0]]   -> 2</pre><p>Three islands are L-shaped trominoes in different orientations and one is a single cell. If rotations were not allowed the answer would be 4.</p>",
    constraints=["1 &le; rows, cols &le; 50", "grid[r][c] is 0 or 1", "The answer is 0 when there is no land"],
    hints=["Finding islands is routine. The interesting part is a description of an island that is the same for all of its orientations.",
           "There are 8 orientations of a shape (4 rotations, each with or without mirroring). For every orientation, translate the cells so that the smallest row and smallest column become 0 and sort them.",
           "Take the lexicographically smallest of these 8 sorted tuples as the canonical form of the island, and count the distinct canonical forms in a set."],
    editorial=["Flood-fill every island and gather its cell coordinates. Apply the 8 symmetries of the square to the coordinates: <code>(r,c), (r,-c), (-r,c), (-r,-c), (c,r), (c,-r), (-c,r), (-c,-r)</code>. After each transformation, subtract the minimum row and the minimum column from all cells so that sliding no longer matters, then sort the cells into a tuple.",
               "Two islands have the same shape exactly when the sets of their 8 tuples coincide, therefore the smallest tuple is a canonical representative. The answer is the number of distinct canonical tuples. With n land cells the work is O(n log n) per island times a constant of 8, so O(R &middot; C log(R &middot; C)) overall."],
    time="O(R &middot; C log(R &middot; C))", space="O(R &middot; C)",
    solution='''def countShapeClasses(grid):
    rows, cols = len(grid), len(grid[0])
    seen = [[False] * cols for _ in range(rows)]
    forms = set()
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == 1 and not seen[r][c]:
                seen[r][c] = True
                stack = [(r, c)]
                cells = []
                while stack:
                    y, x = stack.pop()
                    cells.append((y, x))
                    for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        ny, nx = y + dy, x + dx
                        if 0 <= ny < rows and 0 <= nx < cols and grid[ny][nx] == 1 and not seen[ny][nx]:
                            seen[ny][nx] = True
                            stack.append((ny, nx))
                best = None
                for f in (lambda a, b: (a, b), lambda a, b: (a, -b), lambda a, b: (-a, b), lambda a, b: (-a, -b),
                          lambda a, b: (b, a), lambda a, b: (b, -a), lambda a, b: (-b, a), lambda a, b: (-b, -a)):
                    moved = [f(a, b) for a, b in cells]
                    mr = min(a for a, b in moved)
                    mc = min(b for a, b in moved)
                    form = tuple(sorted((a - mr, b - mc) for a, b in moved))
                    if best is None or form < best:
                        best = form
                forms.add(best)
    return len(forms)
''',
    tests=[[[[1, 1, 0, 0, 0], [1, 0, 0, 1, 1], [0, 0, 0, 0, 1], [1, 0, 0, 0, 0], [1, 1, 0, 1, 0]]], [[[0]]], [[[1]]],
           [[[1, 0, 1]]], [[[1, 1, 0, 1], [0, 0, 0, 1]]], [[[1, 1, 0, 1, 1], [1, 0, 0, 0, 1]]],
           [[[1, 1, 0, 0], [0, 1, 1, 0], [0, 0, 0, 0], [0, 1, 1, 0], [1, 1, 0, 0]]],
           [[[1, 1, 1, 0, 1, 0], [0, 1, 0, 0, 1, 1], [0, 0, 0, 0, 1, 0]]],
           [[[1, 0, 1, 0, 1, 0, 1]]], [[[1, 1, 1], [1, 0, 1], [1, 1, 1]]], [[[1, 1, 0, 0, 1, 0], [0, 1, 0, 0, 1, 1], [0, 0, 0, 0, 0, 0]]],
           [[[0, 1, 1, 0, 0], [1, 1, 0, 0, 1], [0, 0, 0, 0, 1], [1, 0, 0, 1, 1]]]],
)
_r = rnd(8209)
p["tests"].append([_grid(_r, 50, 50, 0.4)])
p["tests"].append([_grid(_r, 50, 50, 0.3)])
p["tests"].append([[[1 if (i % 2 == 0 and j % 2 == 0) else 0 for j in range(50)] for i in range(50)]])
p["tests"].append([_grid(_r, 50, 50, 0.52)])


def b_classes(grid):
    def norm(cells):
        mr = min(a for a, b in cells)
        mc = min(b for a, b in cells)
        return frozenset((a - mr, b - mc) for a, b in cells)

    def orientations(cells):
        out = []
        cur = list(cells)
        for _ in range(2):
            for _ in range(4):
                cur = [(b, -a) for a, b in cur]  # turn by 90 degrees
                out.append(norm(cur))
            cur = [(a, -b) for a, b in cur]  # mirror
        return out

    reps = []
    for comp in _comps(grid, lambda v: v == 1):
        s = norm(comp)
        if not any(s in rep_o for rep_o in reps):
            reps.append(set(orientations(comp)))
    return len(reps)


CHECKS["distinct-islands-rotate-reflect"] = (b_classes, lambda r: [_grid(r, r.randint(1, 8), r.randint(1, 8), r.choice([0.35, 0.5, 0.65]))], "exact")
VALIDATE["distinct-islands-rotate-reflect"] = _vgrid(50, 50, (0, 1))

# ---------------------------------------------------------------- days to disconnect
p = add(
    id="cells-to-remove-to-split-land", title="Cells to Remove to Split the Land", diff="Hard", topic="Graphs", tier="extra",
    fn="minRemovals", params=[("grid", "int[][]")], ret="int", cmp="exact",
    desc="<p>In a binary <code>grid</code> a <code>1</code> is land and a <code>0</code> is water. An island is a maximal group of land cells connected through the four directions. The grid is called <em>split</em> when it does not contain exactly one island (it has none, or two or more).</p><p>In one operation you turn a single land cell into water. Return the minimum number of operations needed to make the grid split. If it is already split, the answer is <code>0</code>.</p><pre>grid = [[1,1,1],\n        [0,1,0],\n        [1,1,1]]   -> 1\ngrid = [[1,1],\n        [1,1]]     -> 2\ngrid = [[1,0,1]]   -> 0</pre><p>In the first example removing the middle cell separates the top row from the bottom row.</p>",
    constraints=["1 &le; rows, cols &le; 50", "grid[r][c] is 0 or 1"],
    hints=["The answer is always 0, 1 or 2. Try to see why 2 is enough whenever the land is one island.",
           "Answer 0: the grid already has no island or at least two. Answer 1: removing one particular cell splits the land, which means that cell is a cut vertex (articulation point) of the land graph, or the island is a single cell. Otherwise the answer is 2.",
           "Why 2 always works: take the top-most, then left-most land cell. It has at most two land neighbours (right and below). Removing both isolates it, or empties the grid. To check for answer 1, test every land cell by removing it and counting islands (small grids), or find articulation points with one DFS (low-link values)."],
    editorial=["Count the islands first. If there is not exactly one, return 0. Otherwise, if the island has a single cell, removing it leaves no land, so the answer is 1.",
               "The answer is at most 2: the top-most, left-most land cell can have land neighbours only to the right and below, so removing at most those two cells isolates it from the rest (or empties the island). Therefore we only have to decide whether one removal is enough. One removal splits the island exactly when the removed cell is an articulation point of the graph whose vertices are the land cells. Compute articulation points with an iterative DFS using discovery times and low-link values: a non-root vertex v is an articulation point if it has a child u with <code>low[u] &ge; disc[v]</code>, and the root is one if it has at least two DFS children.",
               "That is O(R &middot; C) time. A simpler approach removes every land cell in turn and recounts the islands, which costs O((R &middot; C)<sup>2</sup>) and is also fine for small grids."],
    time="O(R &middot; C)", space="O(R &middot; C)",
    solution='''def minRemovals(grid):
    rows, cols = len(grid), len(grid[0])
    cells = [(r, c) for r in range(rows) for c in range(cols) if grid[r][c] == 1]
    if not cells:
        return 0
    dirs = ((1, 0), (-1, 0), (0, 1), (0, -1))
    # connectivity from the first cell
    start = cells[0]
    seen = {start}
    stack = [start]
    while stack:
        y, x = stack.pop()
        for dy, dx in dirs:
            ny, nx = y + dy, x + dx
            if 0 <= ny < rows and 0 <= nx < cols and grid[ny][nx] == 1 and (ny, nx) not in seen:
                seen.add((ny, nx))
                stack.append((ny, nx))
    if len(seen) != len(cells):
        return 0
    if len(cells) == 1:
        return 1
    # articulation points with an iterative DFS
    disc = {}
    low = {}
    timer = 0
    disc[start] = low[start] = timer
    timer += 1
    root_children = 0
    work = [(start, None, iter(dirs))]
    while work:
        v, parent, it = work[-1]
        advanced = False
        for dy, dx in it:
            u = (v[0] + dy, v[1] + dx)
            if not (0 <= u[0] < rows and 0 <= u[1] < cols) or grid[u[0]][u[1]] != 1:
                continue
            if u not in disc:
                disc[u] = low[u] = timer
                timer += 1
                if v == start:
                    root_children += 1
                work.append((u, v, iter(dirs)))
                advanced = True
                break
            elif u != parent:
                low[v] = min(low[v], disc[u])
        if advanced:
            continue
        work.pop()
        if parent is not None:
            low[parent] = min(low[parent], low[v])
            if parent != start and low[v] >= disc[parent]:
                return 1
    if root_children >= 2:
        return 1
    return 2
''',
    tests=[[[[1, 1, 1], [0, 1, 0], [1, 1, 1]]], [[[1, 1], [1, 1]]], [[[1, 0, 1]]], [[[0]]], [[[1]]], [[[1, 1]]],
           [[[1, 1, 1, 1]]], [[[1, 1, 1], [1, 0, 1], [1, 1, 1]]], [[[0, 0], [0, 0]]],
           [[[1, 1, 0], [1, 1, 1], [0, 1, 1]]], [[[1, 1, 1], [1, 1, 1], [1, 1, 1]]],
           [[[0, 1, 0], [1, 1, 1], [0, 1, 0]]], [[[1, 1, 1, 1], [1, 0, 0, 1], [1, 1, 1, 1]]],
           [[[1, 1, 0, 0], [1, 1, 0, 0], [0, 1, 1, 1], [0, 0, 1, 1]]]],
)
_two = [[1 if ((i < 20 and j < 20) or (i >= 25 and j >= 25) or (i == 20 and j == 19) or (20 < i < 25 and j == 19) or (i == 24 and 19 <= j <= 25)) else 0 for j in range(50)] for i in range(50)]
p["tests"].append([[[1] * 50 for _ in range(50)]])
p["tests"].append([_two])
p["tests"].append([[[1 if i % 2 == 0 or (i % 4 == 1 and j == 49) or (i % 4 == 3 and j == 0) else 0 for j in range(50)] for i in range(50)]])
p["tests"].append([[[1 if (i % 3 != 2 or (i % 6 == 2 and j == 49) or (i % 6 == 5 and j == 0)) else 0 for j in range(50)] for i in range(50)]])
p["tests"].append([[[1 if (i < 2 or j < 1) or (i, j) in {(5, 5), (6, 5)} else 0 for j in range(50)] for i in range(50)]])
_r = rnd(8210)
p["tests"].append([_grid(_r, 50, 50, 0.8)])


def b_remove(grid):
    R, C = len(grid), len(grid[0])
    land = [(i, j) for i in range(R) for j in range(C) if grid[i][j] == 1]

    def split(removed):
        g2 = [row[:] for row in grid]
        for i, j in removed:
            g2[i][j] = 0
        return len(_comps(g2, lambda v: v == 1)) != 1

    from itertools import combinations
    for k in range(len(land) + 1):
        for rem in combinations(land, k):
            if split(rem):
                return k
    return len(land)


def v_remove(tests):
    for t in tests:
        _rect(t["args"][0], 50, 50, allowed=(0, 1))
        assert t["expected"] in (0, 1, 2)
    assert {t["expected"] for t in tests} == {0, 1, 2}, "all three answers should occur"


CHECKS["cells-to-remove-to-split-land"] = (b_remove, lambda r: [_grid(r, r.randint(1, 4), r.randint(1, 4), r.choice([0.6, 0.8, 0.95]))], "exact")
VALIDATE["cells-to-remove-to-split-land"] = v_remove
