"""Problems: depth pack (dynamic programming, graphs, backtracking and union find). See data/lib.py for the registry."""
from collections import Counter, deque
from functools import lru_cache
from itertools import combinations  # noqa: F401

from lib import add, rnd, CHECKS, VALIDATE, gen_arr  # noqa: F401


from lib import P as _P  # noqa: E402


def _get(pid):
    return next(x for x in _P if x["id"] == pid)


# ================================================================== EASY

# ---------------------------------------------------------------- find-the-town-judge
add(
    id="find-the-town-judge", title="Find the Town Judge", diff="Easy", topic="Graphs",
    fn="findJudge", params=[("n", "int"), ("trust", "int[][]")], ret="int", cmp="exact",
    desc="<p>A town has <code>n</code> people labelled <code>1</code> to <code>n</code>. Rumour says one of them is the secret judge. If the judge exists, then:</p><ul><li>the judge trusts nobody, and</li><li>everybody else trusts the judge.</li></ul><p>You are given <code>trust</code>, where each entry <code>[a, b]</code> means that person <code>a</code> trusts person <code>b</code>. Anyone not listed as trusting someone trusts nobody.</p><p>Return the label of the judge, or <code>-1</code> if there is no person who satisfies both rules.</p>",
    constraints=["1 &le; n &le; 1,000", "0 &le; trust.length &le; 10,000", "trust[i] = [a, b] with 1 &le; a, b &le; n and a &ne; b", "All pairs in trust are distinct"],
    hints=["The judge is the only person who can satisfy both rules, so at most one answer exists.",
           "Think of each trust pair as a directed edge a &rarr; b. What do the in-degree and out-degree of the judge look like?",
           "Keep one counter per person: subtract one when they trust someone and add one when someone trusts them. The judge ends with exactly <code>n - 1</code>."],
    editorial=["Treat every pair as a directed edge from a to b. The judge has out-degree 0 and in-degree <code>n - 1</code>. Keep a single array <code>score</code>: decrement <code>score[a]</code> and increment <code>score[b]</code> for every pair.",
               "A person who trusts anyone has a score of at most <code>n - 2</code> (they cannot be trusted by everybody else and also trust someone). The judge scores exactly <code>n - 1</code>. So scan the array and return the person with score <code>n - 1</code>, or <code>-1</code> if nobody has it. Because pairs are distinct, no one can be counted twice."],
    time="O(n + t)", space="O(n)",
    solution='''def findJudge(n, trust):
    score = [0] * (n + 1)
    for a, b in trust:
        score[a] -= 1
        score[b] += 1
    for p in range(1, n + 1):
        if score[p] == n - 1:
            return p
    return -1
''',
    tests=[[2, [[1, 2]]], [3, [[1, 3], [2, 3]]], [3, [[1, 3], [2, 3], [3, 1]]], [1, []], [2, []], [2, [[1, 2], [2, 1]]],
           [3, [[1, 2], [2, 3]]], [4, [[1, 3], [1, 4], [2, 3], [2, 4], [4, 3]]], [3, [[1, 2], [3, 2]]],
           [4, [[2, 1], [3, 1]]], [5, [[1, 5], [2, 5], [3, 5], [4, 5], [5, 1]]]],
)
_r = rnd(7001)


def _judge_case(r, n, judge, extra, skip=None):
    pairs = [(p, judge) for p in range(1, n + 1) if p != judge and p != skip]
    st = set(pairs)
    tries = 0
    while len(st) < len(pairs) + extra and tries < extra * 20:
        tries += 1
        a, b = r.randint(1, n), r.randint(1, n)
        if a != b and a != judge and b != judge:
            st.add((a, b))
    out = sorted(st)
    r.shuffle(out)
    return [list(x) for x in out]


_pj = _get("find-the-town-judge")
_pj["tests"].append([1000, _judge_case(_r, 1000, 537, 4000)])
_pj["tests"].append([1000, _judge_case(_r, 1000, 1, 8000)])
_pj["tests"].append([1000, _judge_case(_r, 1000, 1000, 100, skip=250)])
_pj["tests"].append([1000, _judge_case(_r, 1000, 3, 0) + [[3, 4]]])
_pj["tests"].append([1000, [[i, i + 1] for i in range(1, 1000)]])
_pj["tests"].append([300, _judge_case(_r, 300, 150, 2000)])
_pj["tests"].append([6, _judge_case(_r, 6, 4, 8)])


def b_judge(n, trust):
    t = set(map(tuple, trust))
    for j in range(1, n + 1):
        if all((j, x) not in t for x in range(1, n + 1)) and all((i, j) in t for i in range(1, n + 1) if i != j):
            return j
    return -1


def g_judge(r):
    n = r.randint(1, 6)
    allp = [(a, b) for a in range(1, n + 1) for b in range(1, n + 1) if a != b]
    if r.random() < 0.6:
        j = r.randint(1, n)
        st = {(p, j) for p in range(1, n + 1) if p != j}
        if r.random() < 0.3 and st:
            st.discard(r.choice(sorted(st)))
        for a, b in allp:
            if a != j and r.random() < 0.25:
                st.add((a, b))
        if r.random() < 0.15:
            cand = [(j, x) for x in range(1, n + 1) if x != j]
            if cand:
                st.add(r.choice(cand))
    else:
        st = {x for x in allp if r.random() < 0.4}
    out = sorted(st)
    r.shuffle(out)
    return [n, [list(x) for x in out]]


def v_judge(tests):
    for t in tests:
        n, trust = t["args"]
        assert 1 <= n <= 1000 and len(trust) <= 10000
        assert len({tuple(x) for x in trust}) == len(trust), "duplicate pair"
        for a, b in trust:
            assert 1 <= a <= n and 1 <= b <= n and a != b
        assert t["expected"] == -1 or 1 <= t["expected"] <= n
    assert any(t["expected"] == -1 for t in tests) and any(t["expected"] != -1 for t in tests)


CHECKS["find-the-town-judge"] = (b_judge, g_judge, "exact")
VALIDATE["find-the-town-judge"] = v_judge

# ---------------------------------------------------------------- unique-paths
add(
    id="unique-paths", title="Unique Paths", diff="Easy", topic="Dynamic Programming",
    fn="uniquePaths", params=[("m", "int"), ("n", "int")], ret="int", cmp="exact",
    desc="<p>A robot stands in the top-left cell of an <code>m x n</code> grid and wants to reach the bottom-right cell. In one move it can step either one cell down or one cell to the right; it can never leave the grid.</p><p>Return the number of different routes the robot can take. The answer is guaranteed to fit in a 32-bit signed integer.</p>",
    constraints=["1 &le; m, n &le; 100", "The answer is at most 2 &middot; 10<sup>9</sup>"],
    hints=["Look at the last move of any route. From which two cells can the robot arrive at the bottom-right cell?",
           "Let <code>ways[r][c]</code> be the number of routes to cell <code>(r, c)</code>. Then <code>ways[r][c] = ways[r-1][c] + ways[r][c-1]</code>.",
           "The first row and first column each have exactly one route. You only need the previous row to compute the next one, so one array of size n is enough."],
    editorial=["Every route to cell <code>(r, c)</code> ends with a step from above or from the left, and those two groups of routes are disjoint. Hence <code>ways[r][c] = ways[r-1][c] + ways[r][c-1]</code>, with the first row and first column equal to 1.",
               "Because each row only depends on the row above, a single array updated left to right does the job: <code>row[c] += row[c-1]</code>. That is O(m &middot; n) time and O(n) space. A route is also just a choice of which <code>m - 1</code> of the <code>m + n - 2</code> moves go down, giving the closed form C(m + n - 2, m - 1)."],
    time="O(m &middot; n)", space="O(n)",
    solution='''def uniquePaths(m, n):
    row = [1] * n
    for _ in range(1, m):
        for c in range(1, n):
            row[c] += row[c - 1]
    return row[-1]
''',
    tests=[[3, 7], [3, 2], [1, 1], [1, 10], [10, 1], [2, 2], [3, 3], [7, 3], [10, 10], [4, 6], [100, 1], [1, 100], [2, 100],
           [100, 2], [17, 17], [16, 18], [23, 12], [30, 6], [60, 3]],
)


def b_up(m, n):
    if m + n > 14:  # too many routes to enumerate one by one: count with a memoised recursion instead
        return _routes_memo(m, n)

    def go(r, c):
        if r == m - 1 and c == n - 1:
            return 1
        total = 0
        if r + 1 < m:
            total += go(r + 1, c)
        if c + 1 < n:
            total += go(r, c + 1)
        return total
    return go(0, 0)


def _routes_memo(m, n):
    @lru_cache(maxsize=None)
    def go(r, c):
        if r == m - 1 or c == n - 1:
            return 1
        return go(r + 1, c) + go(r, c + 1)
    return go(0, 0)


def v_up(tests):
    from math import comb
    for t in tests:
        m, n = t["args"]
        assert 1 <= m <= 100 and 1 <= n <= 100
        assert t["expected"] == comb(m + n - 2, m - 1) <= 2 * 10 ** 9


CHECKS["unique-paths"] = (b_up, lambda r: [r.randint(1, 6), r.randint(1, 6)], "exact")
VALIDATE["unique-paths"] = v_up


# ================================================================== MEDIUM

# ---------------------------------------------------------------- partition-equal-subset-sum
add(
    id="partition-equal-subset-sum", title="Partition Equal Subset Sum", diff="Medium", topic="Dynamic Programming",
    fn="canPartition", params=[("nums", "int[]")], ret="bool", cmp="exact",
    desc="<p>Given an array <code>nums</code> of positive integers, decide whether it can be split into two groups (every element goes into exactly one group) such that both groups have the same sum.</p><p>Return <code>true</code> if such a split exists and <code>false</code> otherwise.</p>",
    constraints=["1 &le; nums.length &le; 200", "1 &le; nums[i] &le; 100"],
    hints=["If the total is odd, the answer is immediately no. Otherwise each group must sum to half of the total.",
           "The question becomes: is there a subset of the numbers that adds up to <code>total / 2</code>? Think of a 0/1 knapsack.",
           "Keep a boolean array <code>reach[s]</code> meaning 'some subset sums to s'. For each number x, update sums from high to low: <code>reach[s] |= reach[s - x]</code>."],
    editorial=["The two groups sum to the total, so each must sum to <code>total / 2</code>; an odd total makes it impossible. Finding one group with sum <code>target = total / 2</code> automatically leaves the rest with the same sum.",
               "This is subset-sum. Let <code>reach[s]</code> be true when some subset of the processed numbers adds to s, starting with only <code>reach[0]</code> true. For each number x iterate s from target down to x (downwards so x is used at most once) and set <code>reach[s] |= reach[s - x]</code>. The answer is <code>reach[target]</code>. The sum is at most 20,000, so this is about 200 &times; 10,000 steps. A big-integer bitmask (<code>bits |= bits &lt;&lt; x</code>) performs the same update in one operation per number."],
    time="O(n &middot; sum)", space="O(sum)",
    solution='''def canPartition(nums):
    total = sum(nums)
    if total % 2:
        return False
    target = total // 2
    reach = [False] * (target + 1)
    reach[0] = True
    for x in nums:
        for s in range(target, x - 1, -1):
            if reach[s - x]:
                reach[s] = True
    return reach[target]
''',
    tests=[[[1, 5, 11, 5]], [[1, 2, 3, 5]], [[1]], [[2, 2]], [[1, 1]], [[1, 2]], [[3, 3, 3, 4, 5]], [[100, 100]],
           [[1, 2, 5]], [[4, 4, 4, 4, 4, 4]], [[2, 2, 3, 5]], [[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 6]]],
)
_r = rnd(7002)
_pp = _get("partition-equal-subset-sum")
_pp["tests"].append([[100] * 200])
_pp["tests"].append([[100] * 199 + [98]])  # even total, but every element is even and half is odd
_pp["tests"].append([[_r.randint(1, 100) for _ in range(200)]])
_pp["tests"].append([[2 * _r.randint(1, 50) for _ in range(199)] + [99]])
_a = [_r.randint(1, 100) for _ in range(199)]
_a.append(1 if sum(_a) % 2 else 2)
_pp["tests"].append([_a])
_a = [97, 89, 83, 79, 73, 71, 67, 61, 59, 53, 47, 43, 41, 37, 31, 29, 23, 19, 17, 13, 11, 7, 5, 3, 2] * 8
_pp["tests"].append([_a[:200]])
_pp["tests"].append([[_r.choice([99, 100, 97]) for _ in range(120)] + [1] * 80])
_pp["tests"].append([[50] * 100 + [1] * 100])


def b_part(nums):
    total = sum(nums)
    if total % 2:
        return False
    half = total // 2
    n = len(nums)
    if n <= 14:
        for mask in range(1 << n):
            if sum(nums[i] for i in range(n) if mask >> i & 1) == half:
                return True
        return False
    sums = {0}
    for x in nums:
        sums |= {s + x for s in sums if s + x <= half}
    return half in sums


def g_part(r):
    return [r.randint(1, r.choice([3, 8, 12])) for _ in range(r.randint(1, 10))]


def v_part(tests):
    for t in tests:
        (nums,) = t["args"]
        assert 1 <= len(nums) <= 200 and all(1 <= x <= 100 for x in nums)
    assert any(t["expected"] for t in tests) and any(not t["expected"] and sum(t["args"][0]) % 2 == 0 for t in tests)


CHECKS["partition-equal-subset-sum"] = (b_part, lambda r: [g_part(r)], "exact")
VALIDATE["partition-equal-subset-sum"] = v_part

# ---------------------------------------------------------------- number-of-provinces
add(
    id="number-of-provinces", title="Number of Provinces", diff="Medium", topic="Union Find",
    fn="findCircleNum", params=[("isConnected", "int[][]")], ret="int", cmp="exact",
    desc="<p>There are <code>n</code> cities. Some pairs of cities are directly linked by a road; two cities can also reach each other indirectly through a chain of roads. A <em>province</em> is a maximal group of cities that can all reach one another.</p><p>You are given an <code>n x n</code> matrix <code>isConnected</code> where <code>isConnected[i][j] = 1</code> means city <code>i</code> and city <code>j</code> are directly linked and <code>0</code> means they are not. Every city is linked to itself.</p><p>Return the number of provinces.</p>",
    constraints=["1 &le; n &le; 200", "isConnected[i][j] is 0 or 1", "isConnected[i][i] = 1", "isConnected[i][j] = isConnected[j][i]"],
    hints=["Cities form an undirected graph. A province is exactly one connected component.",
           "Start a DFS or BFS from any city you have not visited, marking every city you can reach. Each start counts as a new province.",
           "Alternatively use union-find: begin with n separate sets, merge the sets of i and j whenever they are linked, and subtract one from the count each time a merge actually joins two different sets."],
    editorial=["Count connected components of the graph described by the matrix. With union-find, start with <code>n</code> components. For each pair <code>i &lt; j</code> with <code>isConnected[i][j] = 1</code>, find the roots of i and j; if they differ, union them and decrease the component count by one. The final count is the answer.",
               "Use path compression (and optionally union by size) so each find is near constant time. The matrix has n&sup2; entries, so reading it dominates: O(n&sup2; &middot; &alpha;(n)). A DFS or BFS over the matrix rows gives the same bound."],
    time="O(n&sup2; &middot; &alpha;(n))", space="O(n)",
    solution='''def findCircleNum(isConnected):
    n = len(isConnected)
    parent = list(range(n))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    comps = n
    for i in range(n):
        row = isConnected[i]
        for j in range(i + 1, n):
            if row[j]:
                a, b = find(i), find(j)
                if a != b:
                    parent[a] = b
                    comps -= 1
    return comps
''',
    tests=[[[[1, 1, 0], [1, 1, 0], [0, 0, 1]]], [[[1, 0, 0], [0, 1, 0], [0, 0, 1]]], [[[1]]], [[[1, 1], [1, 1]]],
           [[[1, 0], [0, 1]]], [[[1, 1, 1], [1, 1, 1], [1, 1, 1]]], [[[1, 1, 0, 0], [1, 1, 1, 0], [0, 1, 1, 0], [0, 0, 0, 1]]],
           [[[1, 0, 0, 1], [0, 1, 1, 0], [0, 1, 1, 0], [1, 0, 0, 1]]], [[[1, 0, 1, 0, 0], [0, 1, 0, 1, 0], [1, 0, 1, 0, 0], [0, 1, 0, 1, 0], [0, 0, 0, 0, 1]]],
           [[[1, 1, 0, 0, 0], [1, 1, 1, 0, 0], [0, 1, 1, 1, 0], [0, 0, 1, 1, 1], [0, 0, 0, 1, 1]]]],
)


def _sym(r, n, p):
    m = [[1 if i == j else 0 for j in range(n)] for i in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            if r.random() < p:
                m[i][j] = m[j][i] = 1
    return m


_r = rnd(7003)
_pv = _get("number-of-provinces")
_pv["tests"].append([_sym(_r, 200, 0.003)])
_pv["tests"].append([_sym(_r, 200, 0.008)])
_pv["tests"].append([_sym(_r, 200, 0.02)])
_pv["tests"].append([_sym(_r, 200, 0.0)])
_pv["tests"].append([[[1] * 200 for _ in range(200)]])
_ch = [[1 if abs(i - j) <= 1 else 0 for j in range(200)] for i in range(200)]
_pv["tests"].append([_ch])
_gm = [[1 if (i // 20 == j // 20) else 0 for j in range(200)] for i in range(200)]
_pv["tests"].append([_gm])
_pv["tests"].append([_sym(_r, 60, 0.03)])


def b_prov(m):
    n = len(m)
    reach = [[bool(m[i][j]) or i == j for j in range(n)] for i in range(n)]
    for k in range(n):
        for i in range(n):
            if reach[i][k]:
                for j in range(n):
                    if reach[k][j]:
                        reach[i][j] = True
    return len({tuple(row) for row in reach})


def v_prov(tests):
    for t in tests:
        (m,) = t["args"]
        n = len(m)
        assert 1 <= n <= 200 and all(len(row) == n for row in m)
        for i in range(n):
            assert m[i][i] == 1
            for j in range(n):
                assert m[i][j] in (0, 1) and m[i][j] == m[j][i]
    assert len({t["expected"] for t in tests}) >= 5


CHECKS["number-of-provinces"] = (b_prov, lambda r: [_sym(r, r.randint(1, 8), r.choice([0.1, 0.2, 0.35]))], "exact")
VALIDATE["number-of-provinces"] = v_prov

# ---------------------------------------------------------------- redundant-connection
add(
    id="redundant-connection", title="Redundant Connection", diff="Medium", topic="Union Find",
    fn="findRedundantConnection", params=[("edges", "int[][]")], ret="int[]", cmp="exact",
    desc="<p>A connected, cycle-free graph (a tree) on nodes <code>1..n</code> had one extra edge added between two nodes that were not already directly connected. You are given the resulting list <code>edges</code> of <code>n</code> undirected edges; <code>edges[i] = [a, b]</code> joins nodes <code>a</code> and <code>b</code>.</p><p>Removing a suitable edge turns the graph back into a tree. If several edges could be removed, return the one that appears <strong>last</strong> in <code>edges</code>. Return it exactly as written in the input (same order of its two numbers).</p>",
    constraints=["3 &le; n = edges.length &le; 1,000", "edges[i] = [a, b] with 1 &le; a, b &le; n and a &ne; b", "No two edges join the same pair of nodes", "The graph is connected"],
    hints=["Adding one edge to a tree creates exactly one cycle. The answer lies on that cycle.",
           "Process the edges in order, keeping track of which nodes are already connected. When would an edge be redundant?",
           "Use union-find: for each edge, if both endpoints already share a root, this edge closes the cycle and is the answer; otherwise union them."],
    editorial=["Insert the edges one by one into a union-find structure. For an edge <code>[a, b]</code>, find the roots of a and b. If the roots differ, the edge connects two separate pieces, so union them. If the roots are equal, a and b were already connected by earlier edges, so this edge completes the unique cycle.",
               "That edge is also the last cycle edge in the input: every other edge of the single cycle came earlier (it was needed to connect a and b), and edges after it are not on the cycle. So the first edge found to be redundant while scanning in order is the required answer. With path compression this runs in nearly linear time."],
    time="O(n &middot; &alpha;(n))", space="O(n)",
    solution='''def findRedundantConnection(edges):
    parent = list(range(len(edges) + 1))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for a, b in edges:
        ra, rb = find(a), find(b)
        if ra == rb:
            return [a, b]
        parent[ra] = rb
    return []
''',
    tests=[[[[1, 2], [1, 3], [2, 3]]], [[[1, 2], [2, 3], [3, 4], [1, 4], [1, 5]]], [[[1, 2], [2, 3], [1, 3]]],
           [[[2, 1], [3, 1], [3, 2]]], [[[1, 2], [3, 4], [2, 3], [4, 1]]], [[[3, 4], [1, 2], [2, 4], [5, 1], [1, 4]]],
           [[[1, 4], [3, 4], [1, 3], [1, 2], [4, 5]]], [[[9, 8], [1, 2], [3, 4], [2, 3], [4, 5], [5, 6], [6, 7], [7, 8], [1, 9]]],
           [[[1, 2], [2, 3], [3, 4], [4, 5], [5, 1]]], [[[2, 3], [1, 2], [4, 5], [3, 4], [5, 6], [6, 7], [7, 8], [2, 4]]]],
)


def _tree_plus_edge(r, n, shape="random"):
    labels = list(range(1, n + 1))
    r.shuffle(labels)
    if shape == "path":
        tree = [(i, i + 1) for i in range(n - 1)]
    elif shape == "star":
        tree = [(0, i) for i in range(1, n)]
    else:
        tree = [(r.randrange(i), i) for i in range(1, n)]
    adj = {(min(a, b), max(a, b)) for a, b in tree}
    while True:
        a, b = r.randrange(n), r.randrange(n)
        if a != b and (min(a, b), max(a, b)) not in adj:
            break
    es = [(labels[a], labels[b]) for a, b in tree] + [(labels[a], labels[b])]
    r.shuffle(es)
    return [[a, b] if r.random() < 0.5 else [b, a] for a, b in es]


_r = rnd(7004)
_pr = _get("redundant-connection")
for _n, _shape in ((1000, "random"), (1000, "path"), (1000, "star"), (999, "random"), (500, "path"), (250, "random")):
    _pr["tests"].append([_tree_plus_edge(_r, _n, _shape)])
_pr["tests"].append([[[i, i + 1] for i in range(1, 1000)] + [[1, 1000]]])
_pr["tests"].append([[[1, 1000]] + [[i, i + 1] for i in range(1, 1000)]])


def b_redundant(edges):
    n = len(edges)

    def is_tree(es):
        adj = {i: [] for i in range(1, n + 1)}
        for a, b in es:
            adj[a].append(b)
            adj[b].append(a)
        seen = {1}
        stack = [1]
        while stack:
            u = stack.pop()
            for v in adj[u]:
                if v not in seen:
                    seen.add(v)
                    stack.append(v)
        return len(seen) == n and len(es) == n - 1

    for i in range(n - 1, -1, -1):
        if is_tree(edges[:i] + edges[i + 1:]):
            return edges[i]
    return []


def v_redundant(tests):
    for t in tests:
        (edges,) = t["args"]
        n = len(edges)
        assert 3 <= n <= 1000
        assert len({frozenset(e) for e in edges}) == n, "repeated pair"
        for a, b in edges:
            assert 1 <= a <= n and 1 <= b <= n and a != b
        assert t["expected"] in edges


CHECKS["redundant-connection"] = (b_redundant, lambda r: [_tree_plus_edge(r, r.randint(3, 9), r.choice(["random", "path", "star"]))], "exact")
VALIDATE["redundant-connection"] = v_redundant

# ---------------------------------------------------------------- combination-sum-ii
add(
    id="combination-sum-ii", title="Combination Sum II", diff="Medium", topic="Backtracking",
    fn="combinationSum2", params=[("candidates", "int[]"), ("target", "int")], ret="int[][]", cmp="rowset",
    desc="<p>Given an array <code>candidates</code> of positive integers (values may repeat) and a positive integer <code>target</code>, find every distinct combination of candidates whose sum is exactly <code>target</code>.</p><p>Each element of the array may be used <strong>at most once</strong>, but if a value appears several times in the array it may be picked up to that many times. Two combinations are the same if they contain the same values with the same multiplicities, regardless of which copies were chosen.</p><p>Return the combinations as rows with their numbers written in <strong>non-decreasing order</strong>. The rows can be listed in any order, and no combination may be listed twice. If no combination works, return an empty list.</p>",
    constraints=["1 &le; candidates.length &le; 30", "1 &le; candidates[i] &le; 50", "1 &le; target &le; 40"],
    hints=["Sort the array so equal values sit next to each other and each row comes out in non-decreasing order.",
           "Do a depth-first search where each step picks the next element to include, moving forward through the sorted array so no element is reused. Stop when the remaining sum is negative.",
           "To avoid duplicate rows, at any one level of the recursion skip a value if it is equal to the previous value you already tried at that same level."],
    editorial=["Sort the candidates. Recurse with a start index and the remaining target. In the loop over <code>i</code> from start, break as soon as <code>candidates[i]</code> exceeds the remaining target (all later values are at least as large). Otherwise take it, recurse with start <code>i + 1</code> (each element is used once), and undo.",
               "Duplicates are removed with one rule: inside a single loop, if <code>i &gt; start</code> and <code>candidates[i] == candidates[i - 1]</code>, skip it. The first copy of a value covers every combination that begins with that value at this position, while a later copy at the same level would repeat them. Copies of the same value are still allowed deeper in the recursion because there the index equals the start of the new loop."],
    time="O(2<sup>n</sup>) worst case", space="O(n) recursion",
    solution='''def combinationSum2(candidates, target):
    cs = sorted(candidates)
    res = []
    cur = []

    def go(start, remain):
        if remain == 0:
            res.append(cur[:])
            return
        for i in range(start, len(cs)):
            if cs[i] > remain:
                break
            if i > start and cs[i] == cs[i - 1]:
                continue
            cur.append(cs[i])
            go(i + 1, remain - cs[i])
            cur.pop()

    go(0, target)
    return res
''',
    tests=[[[10, 1, 2, 7, 6, 1, 5], 8], [[2, 5, 2, 1, 2], 5], [[1], 1], [[1], 2], [[2, 3], 1], [[1, 1, 1, 1], 2],
           [[3, 1, 3, 5, 4, 1], 8], [[4, 4, 4, 4], 8], [[1, 2, 3, 4, 5], 9], [[5, 5, 5], 10], [[6, 7, 9], 5], [[2, 2, 2, 2, 2], 6]],
)
_r = rnd(7005)
_pc = _get("combination-sum-ii")
_pc["tests"].append([list(range(1, 31)), 40])
_pc["tests"].append([[_r.randint(1, 10) for _ in range(30)], 30])
_pc["tests"].append([[1] * 15 + [2] * 10 + [3] * 5, 20])
_pc["tests"].append([[_r.randint(1, 50) for _ in range(30)], 40])
_pc["tests"].append([[50] * 30, 40])
_pc["tests"].append([[_r.randint(5, 25) for _ in range(30)], 40])
_pc["tests"].append([[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 20, 20, 19, 19, 18, 18, 17, 17, 16, 16], 33])


def b_comb2(candidates, target):
    n = len(candidates)
    found = set()
    if n <= 12:
        for mask in range(1, 1 << n):
            sel = sorted(candidates[i] for i in range(n) if mask >> i & 1)
            if sum(sel) == target:
                found.add(tuple(sel))
    else:
        cnt = sorted(Counter(candidates).items())

        def rec(i, remain, picked):
            if remain == 0:
                found.add(tuple(picked))
                return
            if i == len(cnt) or remain < 0:
                return
            v, c = cnt[i]
            for k in range(c + 1):
                if k * v > remain:
                    break
                rec(i + 1, remain - k * v, picked + [v] * k)

        rec(0, target, [])
    return [list(x) for x in sorted(found)]


def g_comb2(r):
    return [[r.randint(1, 8) for _ in range(r.randint(1, 10))], r.randint(1, 20)]


def v_comb2(tests):
    for t in tests:
        cands, target = t["args"]
        assert 1 <= len(cands) <= 30 and all(1 <= x <= 50 for x in cands) and 1 <= target <= 40
        rows = t["expected"]
        assert len(rows) <= 20000
        assert len({tuple(x) for x in rows}) == len(rows), "duplicate rows"
        for row in rows:
            assert row == sorted(row) and sum(row) == target
            assert not (Counter(row) - Counter(cands))
    assert any(not t["expected"] for t in tests) and any(len(t["expected"]) >= 100 for t in tests)


CHECKS["combination-sum-ii"] = (b_comb2, g_comb2, "rowset")
VALIDATE["combination-sum-ii"] = v_comb2

# ---------------------------------------------------------------- shortest-path-in-binary-matrix
add(
    id="shortest-path-in-binary-matrix", title="Shortest Path in a Binary Matrix", diff="Medium", topic="Graphs",
    fn="shortestPathBinaryMatrix", params=[("grid", "int[][]")], ret="int", cmp="exact",
    desc="<p>You are given an <code>n x n</code> grid of <code>0</code>s (open cells) and <code>1</code>s (blocked cells). A <em>clear path</em> goes from the top-left cell to the bottom-right cell, visits only open cells, and moves between cells that touch either along a side or at a corner, so each step may go in any of the <strong>8</strong> directions.</p><p>The <em>length</em> of a path is the number of cells it visits, including the first and the last. Return the length of the shortest clear path, or <code>-1</code> if there is none.</p>",
    constraints=["1 &le; n &le; 100", "grid[i][j] is 0 or 1", "The start or the end cell may itself be blocked, in which case the answer is -1"],
    hints=["Every step costs the same, so which classic algorithm finds shortest paths in an unweighted graph?",
           "Use breadth-first search from the top-left cell, expanding to all 8 neighbours that are in range and open. Don't forget to check that the start cell is open.",
           "Mark a cell as visited when you push it on the queue, and keep the distance with it (or process the queue level by level). The first time you pop the bottom-right cell, its distance is the answer."],
    editorial=["The grid is an unweighted graph where each open cell is connected to up to eight open neighbours, so BFS gives the shortest path. If the start or end cell is blocked, return -1 right away. Put the start in a queue with distance 1 and mark it visited. Pop a cell; if it is the bottom-right cell, return its distance; otherwise push each unvisited open neighbour with distance + 1, marking it visited when pushed.",
               "Marking on push (not on pop) guarantees each cell enters the queue once, and BFS order guarantees the first arrival at any cell is along a shortest route. Total work is O(n&sup2;) with 8 neighbour checks per cell. If the queue empties without reaching the target, no clear path exists."],
    time="O(n&sup2;)", space="O(n&sup2;)",
    solution='''from collections import deque


def shortestPathBinaryMatrix(grid):
    n = len(grid)
    if grid[0][0] or grid[n - 1][n - 1]:
        return -1
    dist = [[0] * n for _ in range(n)]
    dist[0][0] = 1
    q = deque([(0, 0)])
    while q:
        r, c = q.popleft()
        if r == n - 1 and c == n - 1:
            return dist[r][c]
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                nr, nc = r + dr, c + dc
                if 0 <= nr < n and 0 <= nc < n and not grid[nr][nc] and not dist[nr][nc]:
                    dist[nr][nc] = dist[r][c] + 1
                    q.append((nr, nc))
    return -1
''',
    tests=[[[[0, 1], [1, 0]]], [[[0, 0, 0], [1, 1, 0], [1, 1, 0]]], [[[1, 0, 0], [1, 1, 0], [1, 1, 0]]], [[[0]]], [[[1]]],
           [[[0, 0], [0, 1]]], [[[0, 1], [1, 1]]], [[[0, 0, 0], [0, 0, 0], [0, 0, 0]]],
           [[[0, 1, 0, 0], [0, 1, 0, 1], [0, 1, 0, 0], [0, 0, 0, 0]]], [[[0, 0, 1], [1, 1, 1], [0, 0, 0]]],
           [[[0, 0, 0, 0, 0], [1, 1, 1, 1, 0], [0, 0, 0, 0, 0], [0, 1, 1, 1, 1], [0, 0, 0, 0, 0]]]],
)
_r = rnd(7006)
_pb = _get("shortest-path-in-binary-matrix")


def _rand_grid(r, n, dens):
    g = [[1 if r.random() < dens else 0 for _ in range(n)] for _ in range(n)]
    g[0][0] = 0
    g[n - 1][n - 1] = 0
    return g


_pb["tests"].append([[[0] * 100 for _ in range(100)]])
_pb["tests"].append([_rand_grid(_r, 100, 0.2)])
_pb["tests"].append([_rand_grid(_r, 100, 0.35)])
_pb["tests"].append([_rand_grid(_r, 100, 0.5)])
_pb["tests"].append([_rand_grid(_r, 60, 0.3)])
_serp = [[0] * 99 for _ in range(99)]
for _i in range(1, 99, 2):
    _serp[_i] = [1] * 99
    _serp[_i][98 if (_i // 2) % 2 == 0 else 0] = 0
_pb["tests"].append([_serp])
_cut = [[0] * 100 for _ in range(100)]
for _i in range(100):
    _cut[_i][99 - _i] = 1
_cut[0][99] = 1
_pb["tests"].append([_cut])
_pb["tests"].append([[[0 if (i == 0 or j == 99) else (1 if _r.random() < 0.3 else 0) for j in range(100)] for i in range(100)]])


def b_sp(grid):
    n = len(grid)
    if grid[0][0] or grid[n - 1][n - 1]:
        return -1
    INF = 10 ** 9
    d = [[INF] * n for _ in range(n)]
    d[0][0] = 1
    changed = True
    while changed:
        changed = False
        for i in range(n):
            for j in range(n):
                if grid[i][j]:
                    continue
                for di in (-1, 0, 1):
                    for dj in (-1, 0, 1):
                        a, b = i + di, j + dj
                        if (di or dj) and 0 <= a < n and 0 <= b < n and not grid[a][b] and d[a][b] + 1 < d[i][j]:
                            d[i][j] = d[a][b] + 1
                            changed = True
    return d[n - 1][n - 1] if d[n - 1][n - 1] < INF else -1


def g_sp(r):
    n = r.randint(1, 7)
    return [[1 if r.random() < r.choice([0.2, 0.4, 0.55]) else 0 for _ in range(n)] for _ in range(n)]


def v_sp(tests):
    for t in tests:
        (g,) = t["args"]
        n = len(g)
        assert 1 <= n <= 100 and all(len(row) == n and all(v in (0, 1) for v in row) for row in g)
    assert any(t["expected"] == -1 for t in tests) and any(t["expected"] > 50 for t in tests)


CHECKS["shortest-path-in-binary-matrix"] = (b_sp, lambda r: [g_sp(r)], "exact")
VALIDATE["shortest-path-in-binary-matrix"] = v_sp

# ---------------------------------------------------------------- best-time-to-buy-and-sell-stock-with-cooldown
add(
    id="best-time-to-buy-and-sell-stock-with-cooldown", title="Best Time to Buy and Sell Stock with Cooldown",
    diff="Medium", topic="Dynamic Programming",
    fn="maxProfit", params=[("prices", "int[]")], ret="int", cmp="exact",
    desc="<p><code>prices[i]</code> is the price of a stock on day <code>i</code>. You may complete as many buy/sell transactions as you like, subject to these rules:</p><ul><li>you can hold at most one share at a time, so you must sell before buying again;</li><li>after you sell, you cannot buy on the very next day (one day of <em>cooldown</em>);</li><li>a share bought on day <code>i</code> can be sold on any later day.</li></ul><p>Return the maximum total profit you can make. If no profitable trade exists, the answer is <code>0</code>.</p>",
    constraints=["1 &le; prices.length &le; 5,000", "0 &le; prices[i] &le; 1,000"],
    hints=["At the end of any day you are in one of a few situations: holding a share, not holding and free to buy, or just sold and in cooldown.",
           "Track the best profit for each of the three states and update them day by day: hold = max(hold, free - price), sold = hold_prev + price, free = max(free, sold_prev).",
           "Be careful to use the previous day's values on the right-hand side, so compute new values in a temporary step. The answer is the larger of the 'free' and 'sold' states on the last day."],
    editorial=["Define three values at the end of day i: <code>hold</code> is the best profit while owning a share, <code>sold</code> is the best profit if you sold today (so tomorrow is a cooldown), and <code>free</code> is the best profit while owning nothing and being allowed to buy tomorrow.",
               "Transitions for price p: <code>hold' = max(hold, free - p)</code> (keep, or buy today from the free state); <code>sold' = hold + p</code> (sell today); <code>free' = max(free, sold)</code> (rest, or finish yesterday's cooldown). Start with <code>hold = -infinity</code>, <code>sold = 0</code>, <code>free = 0</code>. After the last day the answer is <code>max(sold, free)</code>; ending while still holding a share can never be better. Only O(1) values are kept, so the space is constant."],
    time="O(n)", space="O(1)",
    solution='''def maxProfit(prices):
    hold = -10 ** 9
    sold = 0
    free = 0
    for p in prices:
        new_hold = max(hold, free - p)
        new_sold = hold + p
        new_free = max(free, sold)
        hold, sold, free = new_hold, new_sold, new_free
    return max(sold, free)
''',
    tests=[[[1, 2, 3, 0, 2]], [[1]], [[1, 2]], [[2, 1]], [[1, 2, 4]], [[6, 1, 3, 2, 4, 7]], [[1, 4, 2, 7]], [[5, 5, 5, 5]],
           [[3, 2, 1, 0]], [[0, 10, 0, 10, 0, 10]], [[2, 1, 4, 5, 2, 9, 7]], [[1, 2, 3, 4, 5]], [[1000, 0, 1000]]],
)
_r = rnd(7007)
_pk = _get("best-time-to-buy-and-sell-stock-with-cooldown")
_pk["tests"].append([[_r.randint(0, 1000) for _ in range(5000)]])
_pk["tests"].append([[i % 1001 for i in range(5000)]])
_pk["tests"].append([[1000 - (i % 1001) for i in range(5000)]])
_pk["tests"].append([[(i % 2) * 1000 for i in range(5000)]])
_pk["tests"].append([[500 + _r.randint(-3, 3) for _ in range(3000)]])
_pk["tests"].append([[_r.randint(0, 5) for _ in range(4000)]])
_pk["tests"].append([[(i * 7) % 13 * 70 for i in range(5000)]])


def b_cool(prices):
    n = len(prices)
    if n <= 10:
        best = 0

        def rec(day, holding, cool, buy_price, profit):
            nonlocal best
            if day == n:
                best = max(best, profit)
                return
            rec(day + 1, holding, False, buy_price, profit)  # do nothing (cooldown ends)
            if holding:
                rec(day + 1, False, True, 0, profit + prices[day] - buy_price)  # sell
            elif not cool:
                rec(day + 1, True, False, prices[day], profit)  # buy

        rec(0, False, False, 0, 0)
        return best

    @lru_cache(maxsize=None)
    def f(i):
        if i >= n:
            return 0
        res = f(i + 1)
        for b in range(i, n):
            for s in range(b + 1, n):
                if prices[s] > prices[b]:
                    res = max(res, prices[s] - prices[b] + f(s + 2))
        return res

    return f(0)


def v_cool(tests):
    for t in tests:
        (p,) = t["args"]
        assert 1 <= len(p) <= 5000 and all(0 <= x <= 1000 for x in p)
        assert t["expected"] >= 0


CHECKS["best-time-to-buy-and-sell-stock-with-cooldown"] = (b_cool, lambda r: [[r.randint(0, 9) for _ in range(r.randint(1, 9))]], "exact")
VALIDATE["best-time-to-buy-and-sell-stock-with-cooldown"] = v_cool


# ================================================================== HARD

# ---------------------------------------------------------------- number-of-islands-ii
add(
    id="number-of-islands-ii", title="Number of Islands II", diff="Hard", topic="Union Find",
    fn="numIslands2", params=[("m", "int"), ("n", "int"), ("positions", "int[][]")], ret="int[]", cmp="exact",
    desc="<p>An <code>m x n</code> map starts as all water. You are given a list <code>positions</code>; the <code>k</code>-th entry <code>[r, c]</code> turns the water cell in row <code>r</code>, column <code>c</code> into land (if that cell is already land, nothing changes).</p><p>An <em>island</em> is a maximal group of land cells that are connected through shared sides (up, down, left, right; diagonals do not count).</p><p>Return an array whose <code>k</code>-th element is the number of islands right after the <code>k</code>-th operation has been applied.</p>",
    constraints=["1 &le; m, n &le; 100", "1 &le; positions.length &le; 10,000", "positions[k] = [r, c] with 0 &le; r &lt; m and 0 &le; c &lt; n", "The same cell may appear more than once"],
    hints=["Re-running a full flood fill after every operation is far too slow for big inputs. How can you update the count incrementally?",
           "When a cell becomes land it forms a new island (count + 1), but it may then join up to four neighbouring islands.",
           "Use union-find over cell indices <code>r * n + c</code>. After marking the new cell, union it with each land neighbour; every union that merges two different sets lowers the count by one. Skip cells that are already land."],
    editorial=["Keep a union-find over the <code>m * n</code> cells plus a boolean <code>land</code> array and a running island count. For each position: if the cell is already land, just record the current count. Otherwise mark it as land, add one to the count (it is a new island on its own), then look at the four neighbours. For each neighbour that is land, find the two roots; if they differ, union them and subtract one from the count.",
               "Each operation does at most four unions, and with path compression and union by size every find is almost constant time, so the total cost is about O(k &middot; &alpha;(m &middot; n)) for k operations, plus O(m &middot; n) to set up. Repeated positions must be ignored: counting them again as new islands would be wrong."],
    time="O((mn + k) &middot; &alpha;(mn))", space="O(mn)",
    solution='''def numIslands2(m, n, positions):
    parent = list(range(m * n))
    size = [1] * (m * n)
    land = [False] * (m * n)

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    count = 0
    out = []
    for r, c in positions:
        idx = r * n + c
        if not land[idx]:
            land[idx] = True
            count += 1
            for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nr, nc = r + dr, c + dc
                if 0 <= nr < m and 0 <= nc < n and land[nr * n + nc]:
                    a, b = find(idx), find(nr * n + nc)
                    if a != b:
                        if size[a] < size[b]:
                            a, b = b, a
                        parent[b] = a
                        size[a] += size[b]
                        count -= 1
        out.append(count)
    return out
''',
    tests=[[3, 3, [[0, 0], [0, 1], [1, 2], [2, 1]]], [1, 1, [[0, 0]]], [1, 1, [[0, 0], [0, 0]]], [2, 2, [[0, 0], [1, 1], [0, 1], [1, 0]]],
           [3, 3, [[0, 0], [0, 2], [2, 0], [2, 2], [1, 1], [0, 1], [1, 0], [1, 2], [2, 1]]], [1, 5, [[0, 0], [0, 2], [0, 4], [0, 1], [0, 3]]],
           [3, 3, [[1, 1], [1, 1], [0, 1], [0, 1], [2, 1]]], [4, 1, [[3, 0], [1, 0], [2, 0], [0, 0]]],
           [3, 4, [[0, 0], [1, 1], [2, 2], [1, 2], [0, 1], [2, 3], [0, 3], [1, 3]]], [2, 3, [[0, 0], [1, 2], [0, 2], [1, 0], [1, 1], [0, 1]]]],
)
_r = rnd(7008)
_pi = _get("number-of-islands-ii")
_pi["tests"].append([100, 100, [[_r.randrange(100), _r.randrange(100)] for _ in range(5000)]])
_pi["tests"].append([100, 100, [[_r.randrange(100), _r.randrange(100)] for _ in range(300)]])
_cells = [[i, j] for i in range(70) for j in range(70)]
_r.shuffle(_cells)
_pi["tests"].append([70, 70, _cells])
_cells = [[i, j] for i in range(0, 100, 2) for j in range(100)] + [[i, 99 if (i // 2) % 2 == 0 else 0] for i in range(1, 100, 2)]
_pi["tests"].append([100, 100, _cells])
_cells = [[i, j] for i in range(100) for j in range(100) if (i + j) % 2 == 0]
_r.shuffle(_cells)
_pi["tests"].append([100, 100, _cells[:5000]])
_pi["tests"].append([1, 100, [[0, j] for j in range(0, 100, 2)] + [[0, j] for j in range(1, 100, 2)]])
_pi["tests"].append([100, 1, [[i, 0] for i in range(99, -1, -1)]])
_pi["tests"].append([30, 40, [[_r.randrange(30), _r.randrange(40)] for _ in range(1500)]])


def b_isl2(m, n, positions):
    grid = [[0] * n for _ in range(m)]
    out = []
    for r, c in positions:
        grid[r][c] = 1
        seen = set()
        cnt = 0
        for i in range(m):
            for j in range(n):
                if grid[i][j] and (i, j) not in seen:
                    cnt += 1
                    q = deque([(i, j)])
                    seen.add((i, j))
                    while q:
                        a, b = q.popleft()
                        for da, db in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                            x, y = a + da, b + db
                            if 0 <= x < m and 0 <= y < n and grid[x][y] and (x, y) not in seen:
                                seen.add((x, y))
                                q.append((x, y))
        out.append(cnt)
    return out


def g_isl2(r):
    m, n = r.randint(1, 5), r.randint(1, 5)
    return [m, n, [[r.randrange(m), r.randrange(n)] for _ in range(r.randint(1, 14))]]


def v_isl2(tests):
    for t in tests:
        m, n, pos = t["args"]
        assert 1 <= m <= 100 and 1 <= n <= 100 and 1 <= len(pos) <= 10000
        assert all(0 <= r < m and 0 <= c < n for r, c in pos)
        assert len(t["expected"]) == len(pos)
    assert any(len({tuple(p) for p in t["args"][2]}) < len(t["args"][2]) for t in tests), "need repeated cells"
    assert any(max(t["expected"]) > 100 for t in tests)


CHECKS["number-of-islands-ii"] = (b_isl2, g_isl2, "exact")
VALIDATE["number-of-islands-ii"] = v_isl2

# ---------------------------------------------------------------- palindrome-partitioning-ii
add(
    id="palindrome-partitioning-ii", title="Palindrome Partitioning II", diff="Hard", topic="Dynamic Programming",
    fn="minCut", params=[("s", "string")], ret="int", cmp="exact",
    desc="<p>Cut the string <code>s</code> into consecutive pieces so that every piece reads the same forwards and backwards (a palindrome). Each place where you split the string counts as one cut.</p><p>Return the minimum number of cuts needed. A string that is already a palindrome needs <code>0</code> cuts.</p>",
    constraints=["1 &le; s.length &le; 2,000", "s consists of lowercase English letters only"],
    hints=["Every single character is a palindrome, so some answer always exists (at most <code>n - 1</code> cuts).",
           "Let <code>cuts[i]</code> be the minimum cuts for the first <code>i</code> characters. The last piece <code>s[j..i-1]</code> must be a palindrome, giving <code>cuts[i] = min(cuts[j] + 1)</code> over such j. How can you test palindromes fast?",
           "Instead of testing every substring, expand around each of the 2n-1 centres. Whenever <code>s[l..r]</code> is a palindrome, update <code>cuts[r + 1] = min(cuts[r + 1], cuts[l] + 1)</code>."],
    editorial=["Define <code>cuts[i]</code> as the minimum cuts for the prefix of length i, with <code>cuts[0] = -1</code> so that a prefix that is itself one palindrome costs <code>-1 + 1 = 0</code>. Initialise <code>cuts[i] = i - 1</code>, the cost of cutting between all characters.",
               "Every palindrome has a centre, either a character or a gap between two. Process centres from left to right; for each, grow the window outwards while the two end characters match. For every palindrome <code>s[l..r]</code> found, relax <code>cuts[r + 1]</code> with <code>cuts[l] + 1</code>. Because every palindrome ending before position l has its centre to the left of the current one, <code>cuts[l]</code> is already final when it is used. Total work is O(n&sup2;) with only O(n) memory, versus O(n&sup2;) memory for a full palindrome table."],
    time="O(n&sup2;)", space="O(n)",
    solution='''def minCut(s):
    n = len(s)
    cuts = [i - 1 for i in range(n + 1)]
    for c in range(n):
        for l, r in ((c, c), (c, c + 1)):
            while l >= 0 and r < n and s[l] == s[r]:
                if cuts[l] + 1 < cuts[r + 1]:
                    cuts[r + 1] = cuts[l] + 1
                l -= 1
                r += 1
    return cuts[n]
''',
    tests=[["aab"], ["a"], ["ab"], ["aa"], ["abcba"], ["abcd"], ["aaaa"], ["abababab"], ["noonabbad"], ["racecar"], ["abbab"],
           ["cdd"], ["ababbbabbababa"], ["leet"], ["aabaa"], ["banana"], ["zzzyzzzx"]],
)
_r = rnd(7009)
_pq = _get("palindrome-partitioning-ii")
_pq["tests"].append(["a" * 2000])
_pq["tests"].append(["ab" * 1000])
_pq["tests"].append(["".join(_r.choice("ab") for _ in range(2000))])
_pq["tests"].append(["".join(_r.choice("abc") for _ in range(2000))])
_pq["tests"].append(["abcdefghij" * 200])
_pq["tests"].append(["a" * 1000 + "b" + "a" * 999])
_pq["tests"].append(["".join(_r.choice("abcdefghijklmnopqrstuvwxyz") for _ in range(2000))])
_h = "".join(_r.choice("ab") for _ in range(499))
_pq["tests"].append([_h + _h[::-1] + "c" + _h + _h[::-1]])
_pq["tests"].append(["abc" * 5 + "cba" * 5 + "ab" * 50])


def b_pp2(s):
    n = len(s)
    if n <= 12:
        best = n
        for mask in range(1 << (n - 1)):
            start = 0
            ok = True
            cuts = 0
            for i in range(n):
                if i == n - 1 or mask >> i & 1:
                    piece = s[start:i + 1]
                    if piece != piece[::-1]:
                        ok = False
                        break
                    start = i + 1
                    if i != n - 1:
                        cuts += 1
            if ok:
                best = min(best, cuts)
        return best

    @lru_cache(maxsize=None)
    def f(i):  # min cuts for suffix s[i:]
        if s[i:] == s[i:][::-1]:
            return 0
        return min(1 + f(j) for j in range(i + 1, n) if s[i:j] == s[i:j][::-1])

    return f(0)


def v_pp2(tests):
    for t in tests:
        (s,) = t["args"]
        assert 1 <= len(s) <= 2000 and all("a" <= ch <= "z" for ch in s)
        assert 0 <= t["expected"] < len(s)


CHECKS["palindrome-partitioning-ii"] = (b_pp2, lambda r: ["".join(r.choice(r.choice(["ab", "abc", "aab"])) for _ in range(r.randint(1, 10)))], "exact")
VALIDATE["palindrome-partitioning-ii"] = v_pp2

# ---------------------------------------------------------------- critical-connections-in-a-network
add(
    id="critical-connections-in-a-network", title="Critical Connections in a Network", diff="Hard", topic="Graphs",
    fn="criticalConnections", params=[("n", "int"), ("connections", "int[][]")], ret="int[][]", cmp="rowset",
    desc="<p>A network has <code>n</code> servers numbered <code>0</code> to <code>n - 1</code>, joined by undirected cables. <code>connections[i] = [a, b]</code> is a cable between servers <code>a</code> and <code>b</code>. Every server can reach every other server, directly or through other servers.</p><p>A cable is <em>critical</em> if removing it (and only it) leaves at least one pair of servers unable to reach each other.</p><p>Return all critical cables. Write each one as <code>[a, b]</code> with <code>a &lt; b</code>. The rows may be listed in any order. If none is critical, return an empty list.</p>",
    constraints=["2 &le; n &le; 1,000", "n - 1 &le; connections.length &le; 5,000", "connections[i] = [a, b] with 0 &le; a, b &lt; n and a &ne; b", "No pair of servers is joined by more than one cable", "The network is connected"],
    hints=["A critical cable is a bridge. Trying to delete every edge and re-check connectivity costs O(E &middot; (V + E)), which is too slow for large inputs.",
           "Run a DFS and record for each node the time at which it was first visited. Then ask: from the subtree below an edge, can any node reach back to an ancestor above that edge?",
           "Keep <code>low[v]</code>, the smallest discovery time reachable from v's subtree using at most one back edge. A tree edge (u, v) is a bridge exactly when <code>low[v] &gt; disc[u]</code>."],
    editorial=["Run a depth-first search that assigns each node a discovery time <code>disc</code> and computes <code>low[v]</code> = the smallest discovery time reachable from v's DFS subtree through tree edges followed by at most one non-tree (back) edge. When processing the child v of u over tree edge (u, v), after finishing v set <code>low[u] = min(low[u], low[v])</code>. For any other already-visited neighbour w (not the parent edge), set <code>low[u] = min(low[u], disc[w])</code>.",
               "The edge (u, v) is a bridge exactly when <code>low[v] &gt; disc[u]</code>: nothing in v's subtree can climb back to u or above, so the cable is the only link. This is Tarjan's bridge-finding algorithm, linear in nodes plus edges. Since depth can reach 1,000, an explicit stack (iterative DFS) avoids recursion limits. Normalise each bridge to <code>[min, max]</code> before returning."],
    time="O(V + E)", space="O(V + E)",
    solution='''def criticalConnections(n, connections):
    adj = [[] for _ in range(n)]
    for i, (a, b) in enumerate(connections):
        adj[a].append((b, i))
        adj[b].append((a, i))
    disc = [-1] * n
    low = [0] * n
    out = []
    timer = 0
    disc[0] = low[0] = 0
    timer = 1
    stack = [(0, -1, 0)]  # node, edge id used to arrive, next neighbour index
    while stack:
        u, pe, k = stack.pop()
        if k < len(adj[u]):
            stack.append((u, pe, k + 1))
            v, eid = adj[u][k]
            if eid == pe:
                continue
            if disc[v] == -1:
                disc[v] = low[v] = timer
                timer += 1
                stack.append((v, eid, 0))
            else:
                low[u] = min(low[u], disc[v])
        elif stack:
            p = stack[-1][0]
            low[p] = min(low[p], low[u])
            if low[u] > disc[p]:
                out.append([min(p, u), max(p, u)])
    return out
''',
    tests=[[4, [[0, 1], [1, 2], [2, 0], [1, 3]]], [2, [[0, 1]]], [3, [[0, 1], [1, 2], [2, 0]]], [3, [[0, 1], [1, 2]]],
           [4, [[0, 1], [1, 2], [2, 3], [3, 0]]], [5, [[1, 0], [2, 0], [3, 2], [4, 2], [4, 3], [3, 0], [4, 0]]],
           [6, [[0, 1], [1, 2], [2, 0], [2, 3], [3, 4], [4, 5], [5, 3]]], [5, [[4, 3], [3, 2], [2, 1], [1, 0]]],
           [6, [[0, 1], [0, 2], [0, 3], [0, 4], [0, 5]]], [7, [[0, 1], [1, 2], [2, 0], [3, 4], [4, 5], [5, 3], [2, 3], [5, 6]]],
           [4, [[0, 1], [0, 2], [0, 3], [1, 2], [1, 3], [2, 3]]]],
)


def _conn_graph(r, n, extra):
    order = list(range(n))
    r.shuffle(order)
    es = set()
    for i in range(1, n):
        p = order[r.randrange(i)]
        es.add((min(p, order[i]), max(p, order[i])))
    tries = 0
    target = len(es) + extra
    while len(es) < target and tries < extra * 30 + 100:
        tries += 1
        a, b = r.randrange(n), r.randrange(n)
        if a != b:
            es.add((min(a, b), max(a, b)))
    out = sorted(es)
    r.shuffle(out)
    return [[a, b] if r.random() < 0.5 else [b, a] for a, b in out]


_r = rnd(7010)
_pc2 = _get("critical-connections-in-a-network")
_pc2["tests"].append([1000, [[i, i + 1] for i in range(999)]])
_pc2["tests"].append([1000, [[i, (i + 1) % 1000] for i in range(1000)]])
_pc2["tests"].append([1000, _conn_graph(_r, 1000, 0)])
_pc2["tests"].append([1000, _conn_graph(_r, 1000, 30)])
_pc2["tests"].append([1000, _conn_graph(_r, 1000, 400)])
_pc2["tests"].append([1000, _conn_graph(_r, 1000, 4000)])
_pc2["tests"].append([500, _conn_graph(_r, 500, 120)])
# chain of triangles joined by bridges
_cn = []
for _b in range(0, 990, 3):
    _cn += [[_b, _b + 1], [_b + 1, _b + 2], [_b + 2, _b]]
    if _b + 3 < 990:
        _cn.append([_b + 2, _b + 3])
_pc2["tests"].append([990, _cn])
_pc2["tests"].append([1000, [[0, i] for i in range(1, 1000)]])
_pc2["tests"].append([60, _conn_graph(_r, 60, 10)])


def b_crit(n, connections):
    def connected(skip):
        adj = [[] for _ in range(n)]
        for i, (a, b) in enumerate(connections):
            if i != skip:
                adj[a].append(b)
                adj[b].append(a)
        seen = {0}
        q = deque([0])
        while q:
            u = q.popleft()
            for v in adj[u]:
                if v not in seen:
                    seen.add(v)
                    q.append(v)
        return len(seen) == n

    return [[min(a, b), max(a, b)] for i, (a, b) in enumerate(connections) if not connected(i)]


def g_crit(r):
    n = r.randint(2, 9)
    return [n, _conn_graph(r, n, r.randint(0, 6))]


def v_crit(tests):
    for t in tests:
        n, es = t["args"]
        assert 2 <= n <= 1000 and n - 1 <= len(es) <= 5000
        assert len({frozenset(e) for e in es}) == len(es), "repeated pair"
        adj = [[] for _ in range(n)]
        for a, b in es:
            assert 0 <= a < n and 0 <= b < n and a != b
            adj[a].append(b)
            adj[b].append(a)
        seen = {0}
        st = [0]
        while st:
            u = st.pop()
            for v in adj[u]:
                if v not in seen:
                    seen.add(v)
                    st.append(v)
        assert len(seen) == n, "network not connected"
        rows = t["expected"]
        assert all(a < b for a, b in rows) and len({tuple(x) for x in rows}) == len(rows)
    assert any(not t["expected"] for t in tests) and any(len(t["expected"]) > 100 for t in tests)


CHECKS["critical-connections-in-a-network"] = (b_crit, g_crit, "rowset")
VALIDATE["critical-connections-in-a-network"] = v_crit
