"""Problems: graphs. See data/lib.py for the registry."""
from lib import add, rnd, CHECKS, VALIDATE, gen_arr  # noqa: F401
from itertools import product as _product
from lib import P as _P


# ============================================================ MEDIUM

# ---------------------------------------------------------------- permutations
add(
    id="permutations", title="Permutations", diff="Medium", topic="Backtracking",
    fn="permute", params=[("nums", "int[]")], ret="int[][]", cmp="rowset",
    desc="<p>Given an array <code>nums</code> of distinct integers, return every possible ordering of its elements. Each ordering uses all the numbers exactly once.</p><p>Return the orderings as rows in any sequence you like, but the numbers inside a row must appear in the order of that arrangement (so <code>[1,2]</code> and <code>[2,1]</code> are two different rows).</p>",
    constraints=["1 &le; nums.length &le; 6", "-10 &le; nums[i] &le; 10", "All values are distinct"],
    hints=["With n distinct numbers there are n! orderings, so you will need to build them one at a time.",
           "Fill the positions from left to right. At each position, try every number that has not been used yet.",
           "Keep a <code>used</code> flag per element. Choose a number, mark it, recurse to the next position, then unmark it (backtrack)."],
    editorial=["Build an arrangement position by position. At depth d, loop over all indices; if the number is unused, append it, mark it used and recurse. When the arrangement has n numbers, store a copy. After the recursive call returns, remove the number and clear the flag so the next candidate can take its place.",
               "An alternative is to swap elements in place: at depth d, swap <code>nums[d]</code> with each <code>nums[j]</code> for <code>j &ge; d</code>, recurse, and swap back. That avoids the <code>used</code> array. Either way there are n! results and each costs O(n) to copy, which matches the output size."],
    time="O(n &middot; n!)", space="O(n) extra",
    solution='''def permute(nums):
    n = len(nums)
    res = []
    used = [False] * n
    cur = []

    def go():
        if len(cur) == n:
            res.append(cur[:])
            return
        for i in range(n):
            if used[i]:
                continue
            used[i] = True
            cur.append(nums[i])
            go()
            cur.pop()
            used[i] = False

    go()
    return res
''',
    tests=[[[1, 2, 3]], [[0, 1]], [[7]], [[3, -1, 5]], [[-4, 9, 0, 2]], [[1, 2, 3, 4, 5]], [[6, -2, 0, 10, -10, 3]],
           [[5, 4, 3, 2, 1, 0]]],
)


def b_perm(nums):
    n = len(nums)
    out = []
    for idx in _product(range(n), repeat=n):
        if len(set(idx)) == n:
            out.append([nums[i] for i in idx])
    return out


def _v_perm(tests):
    from math import factorial
    for t in tests:
        nums, res = t["args"][0], t["expected"]
        assert len(res) == factorial(len(nums)) and len({tuple(x) for x in res}) == len(res)
        assert all(sorted(x) == sorted(nums) for x in res)


CHECKS["permutations"] = (b_perm, lambda r: [r.sample(range(-10, 11), r.randint(1, 5))], "rowset")
VALIDATE["permutations"] = _v_perm

# ---------------------------------------------------------------- combination sum
add(
    id="combination-sum", title="Combination Sum", diff="Medium", topic="Backtracking",
    fn="combinationSum", params=[("candidates", "int[]"), ("target", "int")], ret="int[][]", cmp="rowset",
    desc="<p>You are given an array <code>candidates</code> of distinct positive integers and a positive integer <code>target</code>. Return every unique collection of candidates whose sum is exactly <code>target</code>. A candidate may be used any number of times in one collection.</p><p>Two collections are the same if they use each candidate the same number of times, so list every collection only once, with its numbers in non-decreasing order (for example <code>[2,2,3]</code>, never <code>[2,3,2]</code>). The rows can be returned in any order. If nothing works, return an empty array.</p>",
    constraints=["1 &le; candidates.length &le; 8", "2 &le; candidates[i] &le; 40, all values distinct", "1 &le; target &le; 40", "The answer has fewer than 500 combinations"],
    hints=["Think of building a combination one number at a time, with a running total that must reach <code>target</code>.",
           "To avoid listing the same multiset in different orders, only allow choosing candidates at the current index or later.",
           "Sort the candidates. In the recursion, loop from the current index; if a candidate overshoots the remaining amount, every later candidate does too, so stop."],
    editorial=["Sort the candidates, then recurse with the start index and the remaining amount. When the remaining amount hits zero, record the current list. Otherwise try each candidate from the start index onward, recurse with the <em>same</em> index (reuse is allowed), and remove it again afterwards. Because indices never go backwards, every combination is produced exactly once in non-decreasing order.",
               "Sorting lets you break out of the loop as soon as a candidate exceeds what is left, which prunes many branches. The cost is bounded by the number of nodes in the search tree, roughly O(n<sup>target / min</sup>) in the worst case. A dynamic-programming table of combinations per sum also works, but it stores many partial lists, so backtracking is the usual choice."],
    time="O(n<sup>T / m</sup>)", space="O(T / m) extra",
    solution='''def combinationSum(candidates, target):
    cands = sorted(candidates)
    res = []
    cur = []

    def go(start, left):
        if left == 0:
            res.append(cur[:])
            return
        for i in range(start, len(cands)):
            c = cands[i]
            if c > left:
                break
            cur.append(c)
            go(i, left - c)
            cur.pop()

    go(0, target)
    return res
''',
    tests=[[[3, 4, 5], 9], [[2, 4, 5], 9], [[2], 3], [[5, 10], 4], [[4], 12], [[3, 5, 7], 15], [[2, 4, 6, 8], 9],
           [[7, 3, 2], 14], [[2, 3, 5, 7, 11], 26], [[2, 3, 4, 5, 6, 7], 24]],
)


def b_comb(cands, target):
    out = []
    ranges = [range(target // c + 1) for c in cands]
    for counts in _product(*ranges):
        if sum(c * k for c, k in zip(cands, counts)) == target:
            row = []
            for c, k in sorted(zip(cands, counts)):
                row += [c] * k
            out.append(row)
    return out


def _v_comb(tests):
    for t in tests:
        cands, target = t["args"]
        res = t["expected"]
        assert len(res) < 500, ("too many combos", len(res))
        assert len({tuple(x) for x in res}) == len(res)
        for row in res:
            assert row == sorted(row) and sum(row) == target and set(row) <= set(cands)
        assert sum(len(x) for x in res) < 4000


CHECKS["combination-sum"] = (b_comb, lambda r: [r.sample(range(2, 12), r.randint(1, 4)), r.randint(1, 24)], "rowset")
VALIDATE["combination-sum"] = _v_comb

# ---------------------------------------------------------------- rotate image
add(
    id="rotate-image", title="Rotate Image", diff="Medium", topic="Matrix",
    fn="rotate", params=[("matrix", "int[][]")], ret="int[][]", cmp="exact",
    desc="<p>You are given a square <code>n &times; n</code> matrix of integers. Return a <strong>new</strong> matrix that is the original turned 90 degrees clockwise.</p><p>In the result, the first row is the first column of the input read from bottom to top, the second row is the second column read from bottom to top, and so on. The input itself is left unchanged.</p>",
    constraints=["1 &le; n &le; 50", "-10,000 &le; matrix[i][j] &le; 10,000"],
    hints=["Look at where a single cell lands: the top-left corner of the input becomes the top-right corner of the output.",
           "Work out the target position of <code>matrix[i][j]</code> in terms of <code>i</code>, <code>j</code> and <code>n</code>.",
           "The cell at row <code>i</code>, column <code>j</code> moves to row <code>j</code>, column <code>n - 1 - i</code>. Fill a fresh matrix with that rule."],
    editorial=["After a clockwise quarter turn, the old row <code>i</code> becomes the new column <code>n - 1 - i</code>, and the old column <code>j</code> becomes the new row <code>j</code>. So <code>result[j][n - 1 - i] = matrix[i][j]</code>. Allocate an n &times; n result and copy every cell once.",
               "Doing it in place is a classic follow-up: transpose the matrix (swap <code>[i][j]</code> with <code>[j][i]</code>) and then reverse every row, or rotate four cells at a time layer by layer. Since this version asks for a new matrix, the O(n&sup2;) extra space is the simplest, least error-prone choice."],
    time="O(n&sup2;)", space="O(n&sup2;)",
    solution='''def rotate(matrix):
    n = len(matrix)
    res = [[0] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            res[j][n - 1 - i] = matrix[i][j]
    return res
''',
    tests=[[[[1, 2, 3], [4, 5, 6], [7, 8, 9]]], [[[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12], [13, 14, 15, 16]]], [[[42]]],
           [[[1, 2], [3, 4]]], [[[0, -1], [-2, 0]]], [[[7, 7, 7], [7, 7, 7], [7, 7, 7]]], [[[1, 0, 0, 0, 0], [0, 2, 0, 0, 0], [0, 0, 3, 0, 0], [0, 0, 0, 4, 0], [0, 0, 0, 0, 5]]]],
)
_r = rnd(101)
_P[-1]["tests"].append([[[_r.randint(-10000, 10000) for _ in range(50)] for _ in range(50)]])
_P[-1]["tests"].append([[[_r.randint(0, 99) for _ in range(40)] for _ in range(40)]])


def b_rot(m):
    n = len(m)
    # rotate by reading each output row from the input column, bottom to top
    return [[m[n - 1 - k][j] for k in range(n)] for j in range(n)]


def _gen_sq(r):
    n = r.randint(1, 6)
    return [[[r.randint(-9, 9) for _ in range(n)] for _ in range(n)]]


CHECKS["rotate-image"] = (b_rot, _gen_sq, "exact")

# ---------------------------------------------------------------- max area of island
add(
    id="max-area-of-island", title="Max Area of Island", diff="Medium", topic="Graphs",
    fn="maxAreaOfIsland", params=[("grid", "int[][]")], ret="int", cmp="exact",
    desc="<p>A <code>grid</code> contains <code>1</code> for land and <code>0</code> for water. An island is a set of land cells that are linked through neighbours directly above, below, left or right of each other (diagonals do not link cells).</p><p>The area of an island is the number of land cells in it. Return the largest area among all islands, or <code>0</code> when the grid has no land.</p>",
    constraints=["1 &le; rows, cols &le; 100", "grid[r][c] is 0 or 1"],
    hints=["Each land cell is a node; its land neighbours in the four directions are connected to it.",
           "When you reach an unvisited land cell, explore its whole island while counting how many cells you touch.",
           "Use an explicit stack or queue (BFS/DFS) and mark cells as visited when you push them, so a 100 &times; 100 island does not overflow the call stack."],
    editorial=["Scan the grid. At every land cell that has not been seen, start a flood fill with a stack, marking cells visited as they are pushed, and count the cells popped. The count is that island's area; keep the maximum over all islands (start at 0 for a grid without land).",
               "Every cell enters the stack at most once, so the running time is O(rows &times; cols). A recursive DFS is shorter to write but can reach depth 10,000 on a snake-shaped island; a disjoint-set union that tracks component sizes is another valid approach."],
    time="O(R &middot; C)", space="O(R &middot; C)",
    solution='''def maxAreaOfIsland(grid):
    rows, cols = len(grid), len(grid[0])
    seen = [[False] * cols for _ in range(rows)]
    best = 0
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == 1 and not seen[r][c]:
                seen[r][c] = True
                stack = [(r, c)]
                area = 0
                while stack:
                    y, x = stack.pop()
                    area += 1
                    for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        ny, nx = y + dy, x + dx
                        if 0 <= ny < rows and 0 <= nx < cols and grid[ny][nx] == 1 and not seen[ny][nx]:
                            seen[ny][nx] = True
                            stack.append((ny, nx))
                best = max(best, area)
    return best
''',
    tests=[[[[1, 1, 0, 0], [1, 0, 0, 1], [0, 0, 1, 1], [0, 0, 1, 1]]], [[[1, 0, 1], [0, 1, 0], [1, 0, 1]]], [[[0, 0, 0], [0, 0, 0]]],
           [[[1]]], [[[0]]], [[[1, 1, 1, 1, 1]]], [[[1], [1], [0], [1]]],
           [[[1, 1, 1], [1, 0, 1], [1, 1, 1]]], [[[1, 0, 1, 1, 1], [1, 0, 1, 0, 1], [1, 1, 1, 0, 1], [0, 0, 0, 0, 1]]]],
)
_r = rnd(102)
_P[-1]["tests"].append([[[1 if _r.random() < 0.58 else 0 for _ in range(100)] for _ in range(100)]])
_P[-1]["tests"].append([[[1 if _r.random() < 0.4 else 0 for _ in range(50)] for _ in range(50)]])
_P[-1]["tests"].append([[[1 if (i % 2 == 0 or (i % 4 == 1 and j == 99) or (i % 4 == 3 and j == 0)) else 0 for j in range(100)] for i in range(100)]])


def b_area(grid):
    # label propagation: every land cell repeatedly takes the smallest label among itself and its neighbours
    rows, cols = len(grid), len(grid[0])
    lab = {(r, c): r * cols + c for r in range(rows) for c in range(cols) if grid[r][c]}
    changed = True
    while changed:
        changed = False
        for (r, c) in lab:
            for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                q = (r + dr, c + dc)
                if q in lab and lab[q] < lab[(r, c)]:
                    lab[(r, c)] = lab[q]
                    changed = True
    sizes = {}
    for v in lab.values():
        sizes[v] = sizes.get(v, 0) + 1
    return max(sizes.values(), default=0)


CHECKS["max-area-of-island"] = (b_area, lambda r: (lambda R, C: [[[1 if r.random() < 0.55 else 0 for _ in range(C)] for _ in range(R)]])(r.randint(1, 5), r.randint(1, 5)), "exact")

# ---------------------------------------------------------------- rotting oranges
add(
    id="rotting-oranges", title="Rotting Oranges", diff="Medium", topic="Graphs",
    fn="orangesRotting", params=[("grid", "int[][]")], ret="int", cmp="exact",
    desc="<p>Each cell of a <code>grid</code> is <code>0</code> (empty), <code>1</code> (a fresh orange) or <code>2</code> (a rotten orange). Every minute, each fresh orange that touches a rotten orange directly above, below, left or right becomes rotten. All oranges that qualify turn at the same moment.</p><p>Return the number of minutes that pass until no fresh orange is left. If some fresh orange can never rot, return <code>-1</code>. If there is no fresh orange at the start, the answer is <code>0</code>.</p>",
    constraints=["1 &le; rows, cols &le; 100", "grid[r][c] is 0, 1 or 2"],
    hints=["Rot spreads outwards at the same speed from every rotten orange, like ripples. Time equals distance.",
           "Start from all rotten oranges at once rather than one at a time.",
           "Run a BFS with all rotten cells in the queue at minute 0, process it level by level (one level per minute), and count the fresh oranges you convert. If any fresh orange remains, the answer is -1."],
    editorial=["Put every rotten cell in a queue and count the fresh oranges. Process the queue one level at a time: for each cell in the current level, rot its fresh neighbours, decrease the fresh counter and add them to the next level. The number of levels that actually rotted something is the elapsed time. If the counter is not zero at the end, some fresh orange was cut off by empty cells and the answer is -1.",
               "This is a multi-source BFS: the time for a cell to rot is its shortest distance to the nearest rotten orange. Simulating each minute by rescanning the whole grid also works, but it can take O(R &middot; C) per minute and up to O((R &middot; C)&sup2;) overall, whereas BFS touches every cell only once."],
    time="O(R &middot; C)", space="O(R &middot; C)",
    solution='''from collections import deque


def orangesRotting(grid):
    rows, cols = len(grid), len(grid[0])
    g = [row[:] for row in grid]
    q = deque()
    fresh = 0
    for r in range(rows):
        for c in range(cols):
            if g[r][c] == 2:
                q.append((r, c))
            elif g[r][c] == 1:
                fresh += 1
    minutes = 0
    while q and fresh:
        for _ in range(len(q)):
            y, x = q.popleft()
            for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                ny, nx = y + dy, x + dx
                if 0 <= ny < rows and 0 <= nx < cols and g[ny][nx] == 1:
                    g[ny][nx] = 2
                    fresh -= 1
                    q.append((ny, nx))
        minutes += 1
    return -1 if fresh else minutes
''',
    tests=[[[[2, 1, 1], [0, 1, 1], [1, 1, 1]]], [[[2, 1, 1], [0, 1, 1], [1, 0, 1]]], [[[0, 2]]], [[[1, 2, 1], [1, 0, 1], [1, 1, 1]]],
           [[[0]]], [[[1]]], [[[2]]], [[[2, 2], [2, 2]]], [[[1, 1, 1], [1, 1, 1]]], [[[2, 1, 0, 1], [0, 0, 0, 1], [1, 1, 1, 1]]],
           [[[2, 1, 1, 1, 1, 2]]]],
)
_r = rnd(103)
_g = [[1 if _r.random() < 0.9 else 0 for _ in range(60)] for _ in range(60)]
for _ in range(3):
    _g[_r.randrange(60)][_r.randrange(60)] = 2
_P[-1]["tests"].append([_g])
# a long serpentine corridor of fresh oranges with a rotten orange at its start (about 5,000 minutes)
_g = [[1 if (i % 2 == 0 or (i % 4 == 1 and j == 99) or (i % 4 == 3 and j == 0)) else 0 for j in range(100)] for i in range(100)]
_g[0][0] = 2
_P[-1]["tests"].append([_g])
# the same corridor, but one cell is cut so the far end can never rot
_g2 = [row[:] for row in _g]
_g2[40][99] = 0
_P[-1]["tests"].append([_g2])


def b_rot_sim(grid):
    g = [row[:] for row in grid]
    rows, cols = len(g), len(g[0])
    t = 0
    while any(1 in row for row in g):
        nxt = [row[:] for row in g]
        moved = False
        for r in range(rows):
            for c in range(cols):
                if g[r][c] == 1:
                    for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        rr, cc = r + dr, c + dc
                        if 0 <= rr < rows and 0 <= cc < cols and g[rr][cc] == 2:
                            nxt[r][c] = 2
                            moved = True
                            break
        if not moved:
            return -1
        g = nxt
        t += 1
    return t


CHECKS["rotting-oranges"] = (b_rot_sim, lambda r: (lambda R, C: [[[r.choice([0, 1, 1, 1, 2]) for _ in range(C)] for _ in range(R)]])(r.randint(1, 5), r.randint(1, 5)), "exact")

# ---------------------------------------------------------------- course schedule
add(
    id="course-schedule", title="Course Schedule", diff="Medium", topic="Graphs",
    fn="canFinish", params=[("numCourses", "int"), ("prerequisites", "int[][]")], ret="bool", cmp="exact",
    desc="<p>A school offers <code>numCourses</code> courses numbered <code>0</code> to <code>numCourses - 1</code>. Each entry <code>prerequisites[i] = [a, b]</code> says that course <code>b</code> must be completed before you can take course <code>a</code>. The same pair may appear more than once, and a pair may even name the same course twice.</p><p>Return <code>true</code> if it is possible to complete every course, and <code>false</code> otherwise.</p>",
    constraints=["1 &le; numCourses &le; 1,000", "0 &le; prerequisites.length &le; 2,500", "0 &le; a, b &lt; numCourses", "Duplicate pairs and pairs with a = b are allowed"],
    hints=["Draw an edge from <code>b</code> to <code>a</code> for every pair. When can the courses not all be finished?",
           "Exactly when the graph has a cycle, because every course on a cycle waits for another course on it. A pair <code>[a, a]</code> is a cycle of length one.",
           "Repeatedly take a course with no unmet prerequisites (in-degree 0), remove it, and lower the in-degree of its dependants. If you remove every course, there is no cycle."],
    editorial=["Count, for every course, the number of prerequisite edges pointing at it (duplicates count each time, which is fine because they are removed each time too). Put all courses with count 0 in a queue. Pop a course, mark it finished and decrement the count of each course that depends on it, queueing those that reach 0. The answer is <code>true</code> exactly when all courses were popped (Kahn's algorithm).",
               "A DFS that colours nodes white/grey/black and reports a cycle when it meets a grey node is equivalent. Prefer the queue-based version here, since a chain of 1,000 courses would give a recursion depth of 1,000 for DFS. Both run in O(V + E)."],
    time="O(V + E)", space="O(V + E)",
    solution='''from collections import deque


def canFinish(numCourses, prerequisites):
    adj = [[] for _ in range(numCourses)]
    indeg = [0] * numCourses
    for a, b in prerequisites:
        adj[b].append(a)
        indeg[a] += 1
    q = deque(i for i in range(numCourses) if indeg[i] == 0)
    done = 0
    while q:
        u = q.popleft()
        done += 1
        for v in adj[u]:
            indeg[v] -= 1
            if indeg[v] == 0:
                q.append(v)
    return done == numCourses
''',
    tests=[[4, [[1, 0], [2, 1], [3, 2]]], [3, [[0, 1], [1, 2], [2, 0]]], [2, [[0, 1], [0, 1], [1, 0]]],
           [1, []], [1, [[0, 0]]], [5, []], [2, [[1, 0], [1, 0], [1, 0]]], [4, [[1, 0], [2, 0], [3, 1], [3, 2]]],
           [6, [[1, 0], [2, 1], [3, 2], [4, 3], [5, 4], [2, 5]]], [3, [[0, 0], [1, 2]]]],
)
_r = rnd(104)
_n = 1000
_perm = list(range(_n)); _r.shuffle(_perm)
# the hidden order _perm[0], _perm[1], ...: every requirement points from an earlier to a later course
_edges = [[_perm[i + 1], _perm[i]] for i in range(_n - 1)]
while len(_edges) < 2500:
    i = _r.randrange(_n - 1)
    j = min(_n - 1, i + _r.randint(1, 40))
    _edges.append([_perm[j], _perm[i]])
_r.shuffle(_edges)
_P[-1]["tests"].append([_n, _edges])
_P[-1]["tests"].append([_n, _edges[:-1] + [[_perm[0], _perm[_n - 1]]]])  # the last course is required by the first: a long cycle
_P[-1]["tests"].append([_n, [[i + 1, i] for i in range(_n - 1)]])
_P[-1]["tests"].append([_n, [[i + 1, i] for i in range(_n - 1)] + [[0, _n - 1]]])


def b_cs(n, pre):
    reach = [[False] * n for _ in range(n)]
    for a, b in pre:
        reach[b][a] = True
    for k in range(n):
        for i in range(n):
            if reach[i][k]:
                for j in range(n):
                    if reach[k][j]:
                        reach[i][j] = True
    return not any(reach[i][i] for i in range(n))


CHECKS["course-schedule"] = (b_cs, lambda r: (lambda n: [n, [[r.randrange(n), r.randrange(n)] for _ in range(r.randint(0, 9))]])(r.randint(1, 6)), "exact")

# ---------------------------------------------------------------- network delay time
add(
    id="network-delay-time", title="Network Delay Time", diff="Medium", topic="Graphs",
    fn="networkDelayTime", params=[("times", "int[][]"), ("n", "int"), ("k", "int")], ret="int", cmp="exact",
    desc="<p>A network has <code>n</code> nodes numbered <code>1</code> to <code>n</code>. Each entry <code>times[i] = [u, v, w]</code> is a one-way link: a message sent from node <code>u</code> reaches node <code>v</code> after exactly <code>w</code> time units. There may be several links between the same two nodes.</p><p>At time 0 a message is sent from node <code>k</code>, and every node forwards it along all of its outgoing links the moment it first receives it. Return the time at which the last node receives the message, or <code>-1</code> if some node never gets it.</p>",
    constraints=["1 &le; k &le; n &le; 200", "0 &le; times.length &le; 1,500", "1 &le; u, v &le; n", "1 &le; w &le; 100"],
    hints=["A node gets the message at the earliest time over all routes, so you need the shortest travel time from k to each node.",
           "The answer is the largest of those shortest times, or -1 if some node cannot be reached at all.",
           "Weights are positive, so Dijkstra's algorithm with a min-heap gives all shortest times in O((V + E) log V)."],
    editorial=["Build an adjacency list. Keep a distance array initialised to infinity with <code>dist[k] = 0</code> and a min-heap of <code>(distance, node)</code>. Pop the closest node; if the popped distance is stale (bigger than the recorded one), skip it. Otherwise relax each outgoing edge and push improved distances. When the heap is empty, the answer is the maximum distance, or -1 if any node is still at infinity.",
               "Bellman-Ford (relax all edges up to n - 1 times) is simpler and also correct for positive weights, but it costs O(V &middot; E), which is 300,000 steps in the worst case here. Dijkstra is the intended solution because it scales to much larger graphs."],
    time="O((V + E) log V)", space="O(V + E)",
    solution='''import heapq


def networkDelayTime(times, n, k):
    adj = [[] for _ in range(n + 1)]
    for u, v, w in times:
        adj[u].append((v, w))
    INF = float('inf')
    dist = [INF] * (n + 1)
    dist[k] = 0
    heap = [(0, k)]
    while heap:
        d, u = heapq.heappop(heap)
        if d > dist[u]:
            continue
        for v, w in adj[u]:
            nd = d + w
            if nd < dist[v]:
                dist[v] = nd
                heapq.heappush(heap, (nd, v))
    worst = max(dist[1:])
    return -1 if worst == INF else worst
''',
    tests=[[[[1, 2, 4], [1, 3, 1], [3, 2, 2], [2, 4, 5]], 4, 1], [[[1, 2, 3], [3, 1, 1]], 3, 1], [[], 1, 1],
           [[[2, 1, 7]], 2, 1], [[[1, 2, 5], [1, 2, 3], [1, 2, 9]], 2, 1], [[[1, 1, 4], [1, 2, 6], [2, 2, 1]], 2, 1],
           [[[1, 2, 10], [1, 3, 1], [3, 2, 1], [2, 4, 1], [3, 4, 20]], 4, 3], [[[1, 2, 100], [2, 3, 100], [3, 4, 100], [4, 5, 100]], 5, 1],
           [[[1, 2, 100], [2, 3, 100], [3, 4, 100], [4, 5, 100]], 5, 2]],
)
_r = rnd(105)
_E = [[i, i + 1, _r.randint(40, 100)] for i in range(1, 200)]
_E += [[_r.randint(1, 200), _r.randint(1, 200), _r.randint(1, 100)] for _ in range(1300)]
_r.shuffle(_E)
_P[-1]["tests"].append([_E, 200, 1])
_E = [[i, i + 1, _r.randint(40, 100)] for i in range(1, 200) if i != 120]
_E += [[_r.randint(1, 200), _r.randint(1, 200), _r.randint(1, 100)] for _ in range(1300)]
_E = [e for e in _E if not (e[0] <= 120 < e[1])]  # nothing crosses from 1..120 to 121..200
_r.shuffle(_E)
_P[-1]["tests"].append([_E, 200, 1])
_E = [[_r.randint(1, 100), _r.randint(1, 100), _r.randint(1, 100)] for _ in range(700)] + [[i, i + 1, 100] for i in range(1, 100)]
_r.shuffle(_E)
_P[-1]["tests"].append([_E, 100, 37])


def b_ndt(times, n, k):
    INF = 10 ** 9
    dist = [INF] * (n + 1)
    dist[k] = 0
    for _ in range(n):
        changed = False
        for u, v, w in times:
            if dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
                changed = True
        if not changed:
            break
    worst = max(dist[1:])
    return -1 if worst >= INF else worst


def _g_ndt(r):
    n = r.randint(1, 6)
    return [[[r.randint(1, n), r.randint(1, n), r.randint(1, 9)] for _ in range(r.randint(0, 10))], n, r.randint(1, n)]


CHECKS["network-delay-time"] = (b_ndt, _g_ndt, "exact")

# ============================================================ HARD

# ---------------------------------------------------------------- partition to k equal sum subsets
add(
    id="partition-to-k-equal-sum-subsets", title="Partition to K Equal Sum Subsets", diff="Hard", topic="Backtracking",
    fn="canPartitionKSubsets", params=[("nums", "int[]"), ("k", "int")], ret="bool", cmp="exact",
    desc="<p>Given an array <code>nums</code> of positive integers and an integer <code>k</code>, decide whether the numbers can be divided into exactly <code>k</code> non-empty groups so that every group has the same sum. Each element must go into exactly one group.</p><p>Return <code>true</code> if such a division exists and <code>false</code> otherwise.</p>",
    constraints=["1 &le; k &le; nums.length &le; 16", "1 &le; nums[i] &le; 10,000"],
    hints=["If the total is not divisible by <code>k</code>, or some number is larger than <code>total / k</code>, the answer is immediately false. Otherwise every group must sum to <code>target = total / k</code>.",
           "Fill the groups one after another: pick unused numbers until the current group reaches <code>target</code>, then start the next group.",
           "With at most 16 numbers, the set of used numbers fits in a bitmask. The current group's partial sum is determined by the mask (it is <code>sum(mask) mod target</code>), so you can remember masks from which no solution exists and never explore them again."],
    editorial=["Let <code>target = total / k</code>. Search over bitmasks of used numbers: from a mask, add any unused number that keeps the current group at most <code>target</code>; when the group sum reaches <code>target</code> it resets to zero. If the mask with all bits set is reached, the answer is true. Because the partial group sum depends only on the mask, a mask that failed once can be stored in a set and skipped, so there are at most 2<sup>n</sup> states, each tried with n choices: O(n &middot; 2<sup>n</sup>).",
               "Plain backtracking that places each number into one of k buckets can take k<sup>n</sup> steps on unlucky inputs, which is why the memo matters. Sorting the numbers ascending allows an early break as soon as a number does not fit, and skipping a number equal to an unused predecessor avoids retrying identical choices. An equivalent bottom-up DP stores, for each mask, the partial sum of the current group, or -1 if the mask cannot be reached."],
    time="O(n &middot; 2<sup>n</sup>)", space="O(2<sup>n</sup>)",
    solution='''def canPartitionKSubsets(nums, k):
    total = sum(nums)
    if total % k:
        return False
    target = total // k
    a = sorted(nums)
    if a[-1] > target:
        return False
    n = len(a)
    full = (1 << n) - 1
    dead = set()

    def go(mask, cur):
        if mask == full:
            return True
        if mask in dead:
            return False
        for i in range(n):
            if mask >> i & 1:
                continue
            if cur + a[i] > target:
                break
            if i and a[i] == a[i - 1] and not (mask >> (i - 1) & 1):
                continue
            nxt = cur + a[i]
            if go(mask | (1 << i), 0 if nxt == target else nxt):
                return True
        dead.add(mask)
        return False

    return go(0, 0)
''',
    tests=[[[3, 1, 4, 2, 2, 5, 3], 4], [[6, 6, 3, 3, 2], 2], [[5], 1], [[4, 3, 2, 3, 5, 2, 1], 4], [[1, 2, 3, 4], 3], [[2, 2, 2, 2], 2], [[3, 3, 3, 3], 3], [[1, 1, 1, 1, 1, 1], 6],
           [[6, 6, 6, 3, 3], 3], [[10, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], 2], [[7, 7, 7, 7, 7, 7], 6], [[1, 2, 3, 4, 5, 6], 3],
           [[13, 27, 52, 21, 9, 59, 28, 47, 32, 11, 49, 54, 46, 15, 57, 25], 5],
           [[43, 48, 28, 51, 8, 14, 44, 27, 40, 50, 58, 48, 30, 52, 49, 58], 4],
           [[19, 35, 29, 38, 49, 45, 30, 14, 23, 31, 15, 55, 53, 29, 50, 55], 5],
           [[57, 27, 43, 19, 27, 53, 54, 38, 44, 30, 22, 59, 47, 34, 33, 21], 4],
           [[10] * 16, 8], [[10000] * 16, 16], [[9999, 1, 5000, 5000, 4000, 6000, 3000, 7000, 2000, 8000, 1000, 9000, 500, 9500, 250, 9750], 8]],
)


def b_part(nums, k):
    n = len(nums)
    for assign in _product(range(k), repeat=n):
        sums = [0] * k
        cnt = [0] * k
        for x, g in zip(nums, assign):
            sums[g] += x
            cnt[g] += 1
        if all(c > 0 for c in cnt) and len(set(sums)) == 1:
            return True
    return False


def _g_part(r):
    n = r.randint(1, 7)
    k = r.randint(1, min(n, 4))
    nums = [r.randint(1, 6) for _ in range(n)]
    return [nums, k]


CHECKS["partition-to-k-equal-sum-subsets"] = (b_part, _g_part, "exact")


def _v_part(tests):
    ans = [t["expected"] for t in tests]
    assert True in ans and False in ans
    assert all(1 <= t["args"][1] <= len(t["args"][0]) <= 16 for t in tests)
    assert any(len(t["args"][0]) == 16 and t["args"][1] >= 5 for t in tests)


VALIDATE["partition-to-k-equal-sum-subsets"] = _v_part

# ---------------------------------------------------------------- longest increasing path
add(
    id="longest-increasing-path-in-a-matrix", title="Longest Increasing Path in a Matrix", diff="Hard", topic="Graphs",
    fn="longestIncreasingPath", params=[("matrix", "int[][]")], ret="int", cmp="exact",
    desc="<p>You are given an integer <code>matrix</code>. Starting from any cell, you may repeatedly step to a cell directly above, below, left or right, as long as the value in the new cell is <strong>strictly larger</strong> than the value in the current cell. You cannot leave the matrix.</p><p>Return the largest number of cells on any such path (a path of a single cell has length 1).</p>",
    constraints=["1 &le; rows, cols &le; 100", "-10<sup>9</sup> &le; matrix[r][c] &le; 10<sup>9</sup>"],
    hints=["Treat each cell as a node, with an arrow from a cell to every neighbour that holds a larger value. Because values strictly grow, this graph has no cycles.",
           "Define <code>best(cell)</code> as the longest path that starts there. It equals 1 plus the maximum of <code>best(neighbour)</code> over larger neighbours.",
           "Compute it in order of decreasing value, so every larger neighbour is already done. Equivalently, process cells by increasing value and let each cell extend the best path ending at a smaller neighbour."],
    editorial=["Sort all cells by value. Walk through them from smallest to largest; for each cell, <code>len[cell] = 1 + max(len[nb])</code> over neighbours with a strictly smaller value (those were processed earlier, and equal values never count). The answer is the maximum of <code>len</code>. Sorting makes the order explicit, so there is no recursion at all, which matters for a 100 &times; 100 snake-shaped matrix where a recursive DFS would go 10,000 levels deep.",
               "A memoised DFS from every cell gives the same result and is shorter to write when recursion depth is not a concern. A third way is a topological sort: peel off cells with no smaller neighbour layer by layer, and the number of layers is the answer. Each approach does O(R &middot; C) work per cell-visit; sorting adds the log factor."],
    time="O(R &middot; C log(R &middot; C))", space="O(R &middot; C)",
    solution='''def longestIncreasingPath(matrix):
    rows, cols = len(matrix), len(matrix[0])
    order = sorted((matrix[r][c], r, c) for r in range(rows) for c in range(cols))
    length = [[1] * cols for _ in range(rows)]
    best = 1
    for v, r, c in order:
        m = 0
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols and matrix[nr][nc] < v and length[nr][nc] > m:
                m = length[nr][nc]
        length[r][c] = m + 1
        if length[r][c] > best:
            best = length[r][c]
    return best
''',
    tests=[[[[3, 4, 5], [2, 9, 6], [1, 8, 7]]], [[[4, 4], [4, 4]]], [[[1, 2, 3, 4]]], [[[7]]], [[[5], [4], [3], [2]]],
           [[[9, 9, 4], [6, 7, 8], [2, 1, 1]]], [[[1, 2, 5], [8, 3, 4], [9, 6, 7]]], [[[-5, -4], [-6, 0]]],
           [[[-1000000000, 1000000000], [0, 5]]]],
)
_r = rnd(106)
_snake = [[0] * 60 for _ in range(60)]
for _i in range(60):
    for _j in range(60):
        _snake[_i][_j] = _i * 60 + (_j if _i % 2 == 0 else 59 - _j) + 1
_P[-1]["tests"].append([_snake])
_P[-1]["tests"].append([[[_r.randint(-10 ** 9, 10 ** 9) for _ in range(30)] for _ in range(30)]])
_P[-1]["tests"].append([[[_r.randint(0, 9) for _ in range(100)] for _ in range(100)]])
_P[-1]["tests"].append([[[i + j for j in range(70)] for i in range(70)]])
# a serpentine path of increasing values (a path of 1,300 cells) inside a 50 x 50 field of lower noise
_m = [[_r.randint(-100, 0) for _ in range(50)] for _ in range(50)]
_cells = []
for _i in range(0, 50, 2):
    _cells += [(_i, _j) for _j in range(50)]
    _cells.append((_i + 1, 49 if (_i // 2) % 2 == 0 else 0))
for _k, (_i, _j) in enumerate(_cells):
    _m[_i][_j] = _k + 1
_P[-1]["tests"].append([_m])


def b_lip(m):
    rows, cols = len(m), len(m[0])

    def walk(r, c):
        best = 1
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols and m[nr][nc] > m[r][c]:
                best = max(best, 1 + walk(nr, nc))
        return best

    return max(walk(r, c) for r in range(rows) for c in range(cols))


CHECKS["longest-increasing-path-in-a-matrix"] = (b_lip, lambda r: (lambda R, C: [[[r.randint(0, 6) for _ in range(C)] for _ in range(R)]])(r.randint(1, 4), r.randint(1, 4)), "exact")


def _v_lip(tests):
    t = next(t for t in tests if len(t["args"][0]) == 60 and t["args"][0][1][0] == 120)
    assert t["expected"] == 3600


VALIDATE["longest-increasing-path-in-a-matrix"] = _v_lip
