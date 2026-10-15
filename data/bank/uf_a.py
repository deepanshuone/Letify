"""Problems: union-find basics (components, redundant edges, valid tree, friend circles). See data/lib.py for the registry."""
from lib import add, rnd, CHECKS, VALIDATE, gen_arr  # noqa: F401


# ------------------------------------------------------------------ helpers shared by the tests

def _pairs(r, n, m, base=0):
    """m distinct unordered pairs on base..base+n-1, random orientation, shuffled."""
    if n < 2:
        return []
    m = min(m, n * (n - 1) // 2)
    if m * 3 > n * (n - 1) // 2:
        allp = [(i, j) for i in range(n) for j in range(i + 1, n)]
        s = set(r.sample(allp, m))
    else:
        s = set()
        while len(s) < m:
            a, b = r.sample(range(n), 2)
            s.add((min(a, b), max(a, b)))
    e = [[a + base, b + base] if r.random() < 0.5 else [b + base, a + base] for a, b in sorted(s)]
    r.shuffle(e)
    return e


def _tree(r, n, chain=False, star=False, base=0):
    """Random labelled tree on n nodes as a shuffled list of oriented edges."""
    lab = list(range(n))
    r.shuffle(lab)
    e = []
    for i in range(1, n):
        p = i - 1 if chain else (0 if star else r.randrange(i))
        a, b = lab[p] + base, lab[i] + base
        e.append([a, b] if r.random() < 0.5 else [b, a])
    r.shuffle(e)
    return e


def _check_edges(edges, n, base=0):
    seen = set()
    for a, b in edges:
        assert base <= a < n + base and base <= b < n + base and a != b, ("bad edge", a, b)
        k = (min(a, b), max(a, b))
        assert k not in seen, ("repeated pair", k)
        seen.add(k)


def _closure(n, edges):
    """Reachability matrix by Floyd-Warshall (independent of union-find); nodes 0..n-1."""
    reach = [[i == j for j in range(n)] for i in range(n)]
    for a, b in edges:
        reach[a][b] = reach[b][a] = True
    for k in range(n):
        for i in range(n):
            if reach[i][k]:
                for j in range(n):
                    if reach[k][j]:
                        reach[i][j] = True
    return reach


# =================================================================== EASY
# ---------------------------------------------------------------- largest friend circle
_t = [
    [5, [[0, 1], [1, 2], [3, 4]]],
    [1, []],
    [4, []],
    [4, [[0, 1], [2, 3]]],
    [6, [[0, 1], [1, 2], [2, 0], [3, 4]]],
    [3, [[0, 1], [1, 2]]],
    [7, [[0, 6], [6, 3], [1, 5]]],
    [2, [[1, 0]]],
    [8, [[0, 1], [2, 3], [4, 5], [6, 7], [1, 2], [5, 6]]],
]
_r = rnd(9101)
_t.append([2000, _pairs(_r, 2000, 700)])
_t.append([2000, _pairs(_r, 2000, 1500)])
_t.append([2000, _tree(_r, 2000, chain=True)])

add(
    id="largest-friend-circle-size", title="Largest Friend Circle", diff="Easy", topic="Union Find",
    fn="largestCircle", params=[("n", "int"), ("friendships", "int[][]")], ret="int", cmp="exact",
    desc="<p>A school has <code>n</code> students labelled <code>0</code> to <code>n - 1</code>. Each entry <code>friendships[i] = [a, b]</code> says that students <code>a</code> and <code>b</code> are friends (friendship works both ways).</p><p>A <em>friend circle</em> is a group of students in which any two can be linked by a chain of friends, and that cannot be enlarged: nobody outside the group is a friend of someone inside it. A student with no friends forms a circle of one.</p><p>Return the number of students in the largest friend circle.</p><pre>n = 5, friendships = [[0,1],[1,2],[3,4]]\n\nresult = 3     (circles: {0,1,2} and {3,4})</pre>",
    constraints=["1 &le; n &le; 2,000", "0 &le; friendships.length &le; 2,500", "0 &le; a, b &lt; n and a &ne; b", "No pair of students appears twice"],
    hints=["Every student belongs to exactly one circle, and two students share a circle exactly when a chain of friendships links them.",
           "Give every student its own group at the start. For each friendship, merge the group of <code>a</code> with the group of <code>b</code>. This is the idea behind union-find.",
           "Keep a size next to each group root and add the two sizes when you merge. Track the largest size seen, starting at 1 because a lone student is a circle of one."],
    editorial=["Use a disjoint-set (union-find) structure with <code>parent[i] = i</code> and <code>size[i] = 1</code>. For every friendship find the two roots; if they differ, attach the smaller tree under the larger one and add the sizes. After each successful merge the new size is a candidate for the answer. The answer starts at 1, which covers the case without any friendship.",
               "With path compression and union by size, each operation is almost constant time, so the whole thing is O(n + m &middot; &alpha;(n)). A BFS or DFS over an adjacency list gives the same answer, but union-find needs no adjacency list and generalises to harder problems where edges arrive one by one."],
    time="O(n + m &middot; &alpha;(n))", space="O(n)",
    solution='''def largestCircle(n, friendships):
    parent = list(range(n))
    size = [1] * n

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    best = 1
    for a, b in friendships:
        ra, rb = find(a), find(b)
        if ra == rb:
            continue
        if size[ra] < size[rb]:
            ra, rb = rb, ra
        parent[rb] = ra
        size[ra] += size[rb]
        best = max(best, size[ra])
    return best
''',
    tests=_t,
)


def b_largest(n, friendships):
    reach = _closure(n, friendships)
    return max(sum(row) for row in reach)


def g_largest(r):
    n = r.randint(1, 9)
    return [n, _pairs(r, n, r.randint(0, n + 1))]


def v_largest(tests):
    for t in tests:
        n, edges = t["args"]
        assert 1 <= n <= 2000 and len(edges) <= 2500
        _check_edges(edges, n)
        assert 1 <= t["expected"] <= n
    assert len({t["expected"] for t in tests}) >= 6


CHECKS["largest-friend-circle-size"] = (b_largest, g_largest, "exact")
VALIDATE["largest-friend-circle-size"] = v_largest

# ---------------------------------------------------------------- same circle queries
_t = [
    [5, [[0, 1], [1, 2], [3, 4]], [[0, 2], [0, 3], [3, 4], [2, 2]]],
    [1, [], [[0, 0]]],
    [3, [], [[0, 1], [1, 2], [2, 0]]],
    [4, [[0, 1], [2, 3]], [[1, 0], [1, 2], [3, 2]]],
    [6, [[0, 1], [1, 2], [2, 3], [3, 4], [4, 5]], [[0, 5], [5, 0], [2, 4]]],
    [6, [[0, 1], [2, 3], [4, 5]], [[0, 3], [4, 5], [1, 0], [2, 5]]],
    [2, [[0, 1]], [[1, 1], [0, 1]]],
    [7, [[6, 0], [0, 3], [1, 5]], [[3, 6], [1, 6], [5, 1], [2, 2], [2, 4]]],
]
_r = rnd(9102)
for _n, _m, _q in [(2000, 900, 2000), (2000, 1900, 2000)]:
    _t.append([_n, _pairs(_r, _n, _m), [[_r.randrange(_n), _r.randrange(_n)] for _ in range(_q)]])
_t.append([1500, _tree(_r, 1500), [[_r.randrange(1500), _r.randrange(1500)] for _ in range(1500)]])

add(
    id="friend-circle-membership-queries", title="Same Friend Circle Queries", diff="Easy", topic="Union Find",
    fn="sameCircle", params=[("n", "int"), ("friendships", "int[][]"), ("queries", "int[][]")], ret="int[]", cmp="exact",
    desc="<p>There are <code>n</code> people labelled <code>0</code> to <code>n - 1</code>. Each entry <code>friendships[i] = [a, b]</code> makes <code>a</code> and <code>b</code> friends. Two people are in the same <em>friend circle</em> if they are friends or can be linked by a chain of friends.</p><p>For every query <code>[x, y]</code> in <code>queries</code>, output <code>1</code> if <code>x</code> and <code>y</code> are in the same circle and <code>0</code> otherwise. A person is always in the same circle as themselves. Return the answers in query order.</p><pre>n = 5, friendships = [[0,1],[1,2],[3,4]]\nqueries = [[0,2],[0,3],[3,4],[2,2]]\n\nresult = [1, 0, 1, 1]</pre>",
    constraints=["1 &le; n &le; 2,000", "0 &le; friendships.length &le; 2,000", "1 &le; queries.length &le; 2,000", "0 &le; a, b, x, y &lt; n and a &ne; b in every friendship", "No pair of people appears twice in friendships"],
    hints=["All queries are about the same fixed set of friendships, so you can process the friendships once and then answer every query cheaply.",
           "Two people are in the same circle exactly when they have the same representative in a disjoint-set structure.",
           "Union the two endpoints of every friendship first. Then for each query compare <code>find(x)</code> with <code>find(y)</code>."],
    editorial=["Build the circles once with union-find: start with every person as their own root and union the endpoints of each friendship. Afterwards <code>find(x) == find(y)</code> tells whether x and y share a circle. Queries with <code>x == y</code> naturally answer 1.",
               "Path compression keeps each find nearly constant, so the total time is O((n + m + q) &middot; &alpha;(n)). Running a fresh BFS for every query would cost O(q &middot; (n + m)), which is the thing union-find saves you from when many queries share one graph."],
    time="O((n + m + q) &middot; &alpha;(n))", space="O(n)",
    solution='''def sameCircle(n, friendships, queries):
    parent = list(range(n))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for a, b in friendships:
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb
    return [1 if find(x) == find(y) else 0 for x, y in queries]
''',
    tests=_t,
)


def b_same(n, friendships, queries):
    reach = _closure(n, friendships)
    return [1 if reach[x][y] else 0 for x, y in queries]


def g_same(r):
    n = r.randint(1, 8)
    q = [[r.randrange(n), r.randrange(n)] for _ in range(r.randint(1, 6))]
    return [n, _pairs(r, n, r.randint(0, n)), q]


def v_same(tests):
    for t in tests:
        n, edges, qs = t["args"]
        assert 1 <= n <= 2000 and len(edges) <= 2000 and 1 <= len(qs) <= 2000
        _check_edges(edges, n)
        assert all(0 <= x < n and 0 <= y < n for x, y in qs)
    assert any(0 in t["expected"] and 1 in t["expected"] for t in tests[8:])


CHECKS["friend-circle-membership-queries"] = (b_same, g_same, "exact")
VALIDATE["friend-circle-membership-queries"] = v_same

# ---------------------------------------------------------------- fewest edits to form a tree
_t = [
    [4, [[0, 1], [1, 2], [2, 3]]],
    [4, []],
    [1, []],
    [3, [[0, 1], [1, 2], [0, 2]]],
    [5, [[0, 1], [1, 2], [2, 0], [3, 4]]],
    [6, [[0, 1], [2, 3], [4, 5]]],
    [2, [[0, 1]]],
    [5, [[0, 1], [0, 2], [0, 3], [0, 4], [1, 2], [3, 4]]],
]
_r = rnd(9103)
_t.append([2000, _pairs(_r, 2000, 2500)])
_t.append([2000, _tree(_r, 2000)])
_t.append([2000, _pairs(_r, 2000, 900)])
_t.append([60, _pairs(_r, 60, 1000)])

add(
    id="fewest-edge-edits-to-form-tree", title="Fewest Edits to Form a Tree", diff="Easy", topic="Union Find", tier="extra",
    fn="fewestEdits", params=[("n", "int"), ("edges", "int[][]")], ret="int", cmp="exact",
    desc="<p>A network has <code>n</code> nodes labelled <code>0</code> to <code>n - 1</code> and the two-way links listed in <code>edges</code>. One <em>edit</em> is either of:</p><ul><li>delete one existing link, or</li><li>add one new link between two nodes that are not linked yet.</li></ul><p>A <em>tree</em> is a network that is connected and has no cycle (it then has exactly <code>n - 1</code> links). Return the smallest number of edits that turns the network into a tree.</p><pre>n = 5, edges = [[0,1],[1,2],[2,0],[3,4]]\n\nresult = 2     (delete [2,0], then add a link between the two pieces)</pre>",
    constraints=["1 &le; n &le; 2,000", "0 &le; edges.length &le; 2,500", "0 &le; a, b &lt; n and a &ne; b", "No pair of nodes appears twice"],
    hints=["Two things can be wrong with the network: pieces that are not connected, and cycles. Count each separately.",
           "With <code>c</code> connected components, you must add at least <code>c - 1</code> links to join them. How many links are surplus inside the components?",
           "A forest with <code>c</code> components has <code>n - c</code> links, so there are <code>m - (n - c)</code> surplus links to delete. Each edit fixes at most one of the two problems, so the answer is <code>(m - n + c) + (c - 1)</code>."],
    editorial=["Count the components <code>c</code> with union-find (start at n and subtract one for every edge that joins two different roots). Edges that join two nodes already connected are the <em>surplus</em> ones; there are <code>m - (n - c)</code> of them, and each must be deleted for the final network to be acyclic. The <code>c</code> components also need <code>c - 1</code> new links to become one piece.",
               "That many edits are enough, and none fewer can work: let the potential be (number of surplus links) + (components - 1). Deleting a surplus link or adding a link between two components lowers it by one; any other edit leaves it unchanged or raises it, and a tree has potential 0. So the answer is <code>m - n + 2c - 1</code>. Time is O(n + m &middot; &alpha;(n))."],
    time="O(n + m &middot; &alpha;(n))", space="O(n)",
    solution='''def fewestEdits(n, edges):
    parent = list(range(n))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    comps = n
    surplus = 0
    for a, b in edges:
        ra, rb = find(a), find(b)
        if ra == rb:
            surplus += 1
        else:
            parent[ra] = rb
            comps -= 1
    return surplus + comps - 1
''',
    tests=_t,
)


def b_edits(n, edges):
    from itertools import combinations
    pairs = [(i, j) for i in range(n) for j in range(i + 1, n)]
    have = {(min(a, b), max(a, b)) for a, b in edges}
    best = None
    for S in combinations(pairs, n - 1):
        reach = _closure(n, list(S))
        if all(reach[0]):
            d = len(have.symmetric_difference(S))
            if best is None or d < best:
                best = d
    return best


def g_edits(r):
    n = r.randint(1, 6)
    return [n, _pairs(r, n, r.randint(0, n + 2))]


def v_edits(tests):
    for t in tests:
        n, edges = t["args"]
        assert 1 <= n <= 2000 and len(edges) <= 2500
        _check_edges(edges, n)
    assert len({t["expected"] for t in tests}) >= 6


CHECKS["fewest-edge-edits-to-form-tree"] = (b_edits, g_edits, "exact")
VALIDATE["fewest-edge-edits-to-form-tree"] = v_edits

# =================================================================== MEDIUM
# ---------------------------------------------------------------- graph valid tree
_t = [
    [5, [[0, 1], [0, 2], [0, 3], [1, 4]]],
    [5, [[0, 1], [1, 2], [2, 3], [1, 3], [1, 4]]],
    [1, []],
    [2, []],
    [2, [[1, 0]]],
    [4, [[0, 1], [2, 3]]],
    [4, [[0, 1], [1, 2], [2, 0]]],
    [3, [[0, 1], [1, 2], [0, 2]]],
    [6, [[0, 1], [1, 2], [2, 0], [3, 4], [4, 5]]],
    [4, [[3, 2], [2, 1], [1, 0]]],
]
_r = rnd(9104)
_t.append([2000, _tree(_r, 2000)])
_t.append([2000, _tree(_r, 2000, chain=True)])
_t.append([2000, _tree(_r, 2000, star=True)])
_t.append([2000, _pairs(_r, 2000, 1999)])  # random graph with n - 1 edges: nearly always has a cycle
_t.append([400, _tree(_r, 200) + _tree(_r, 200, base=200)])  # two separate trees: 398 edges for 400 nodes
_t.append([400, _tree(_r, 399) + [[0, 399]]])  # a tree on 399 nodes with one leaf hung on node 0: valid
_t.append([100, [[0, 1], [1, 2], [2, 0], [2, 3]] + _tree(_r, 95, base=3) + [[98, 99]]])  # a cycle plus a separate pair: n - 1 edges, yet invalid

add(
    id="graph-valid-tree-check", title="Is This Graph a Tree?", diff="Medium", topic="Union Find", tier="must",
    fn="validTree", params=[("n", "int"), ("edges", "int[][]")], ret="bool", cmp="exact",
    desc="<p>You are given <code>n</code> nodes labelled <code>0</code> to <code>n - 1</code> and a list of undirected edges, where <code>edges[i] = [a, b]</code> connects <code>a</code> and <code>b</code>.</p><p>Return <code>true</code> if these edges form a <em>tree</em> on all <code>n</code> nodes: every node can reach every other node, and there is no cycle. Otherwise return <code>false</code>.</p><pre>n = 5, edges = [[0,1],[0,2],[0,3],[1,4]]   result = true\nn = 5, edges = [[0,1],[1,2],[2,3],[1,3],[1,4]]   result = false  (1-2-3 is a cycle)\nn = 4, edges = [[0,1],[2,3]]   result = false  (two separate pieces)</pre>",
    constraints=["1 &le; n &le; 2,000", "0 &le; edges.length &le; 2,500", "0 &le; a, b &lt; n and a &ne; b", "No pair of nodes appears twice"],
    hints=["Count the edges first. How many edges does a tree on <code>n</code> nodes have?",
           "A tree has exactly <code>n - 1</code> edges. With that many edges, the graph is a tree if it is connected, and also if it has no cycle: either property implies the other.",
           "Union the endpoints of each edge. If an edge ever joins two nodes that already have the same root, there is a cycle, so return false. After all edges, a graph with <code>n - 1</code> edges and no cycle is automatically connected."],
    editorial=["Two cheap facts decide everything. A tree on n nodes has exactly <code>n - 1</code> edges, so any other edge count is an immediate <code>false</code>. When the count is right, \"connected\" and \"acyclic\" are equivalent, so checking one is enough.",
               "Run union-find over the edges. If some edge connects two nodes that already share a root, it closes a cycle and the answer is <code>false</code>. If all <code>n - 1</code> unions succeed, every union merged two different components, so n nodes shrink to <code>n - (n - 1) = 1</code> component and the graph is a tree. Time is O(n + m &middot; &alpha;(n)); a DFS that checks connectivity gives the same result."],
    time="O(n + m &middot; &alpha;(n))", space="O(n)",
    solution='''def validTree(n, edges):
    if len(edges) != n - 1:
        return False
    parent = list(range(n))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for a, b in edges:
        ra, rb = find(a), find(b)
        if ra == rb:
            return False
        parent[ra] = rb
    return True
''',
    tests=_t,
)


def b_tree(n, edges):
    # leaf peeling for "no cycle" plus label propagation for "one piece"
    deg = [0] * n
    adj = [[] for _ in range(n)]
    for a, b in edges:
        adj[a].append(b)
        adj[b].append(a)
        deg[a] += 1
        deg[b] += 1
    alive = [True] * n
    todo = [i for i in range(n) if deg[i] <= 1]
    removed = 0
    while todo:
        u = todo.pop()
        if not alive[u]:
            continue
        alive[u] = False
        removed += 1
        for v in adj[u]:
            if alive[v]:
                deg[v] -= 1
                if deg[v] <= 1:
                    todo.append(v)
    acyclic = removed == n
    lab = list(range(n))
    changed = True
    while changed:
        changed = False
        for a, b in edges:
            m = min(lab[a], lab[b])
            if lab[a] != m or lab[b] != m:
                lab[a] = lab[b] = m
                changed = True
    return acyclic and len(set(lab)) == 1


def g_tree(r):
    n = r.randint(1, 8)
    k = r.random()
    if k < 0.4:
        e = _tree(r, n)
    elif k < 0.7:
        e = _pairs(r, n, n - 1)
    else:
        e = _pairs(r, n, r.randint(0, n + 1))
    return [n, e]


def v_tree(tests):
    for t in tests:
        n, edges = t["args"]
        assert 1 <= n <= 2000 and len(edges) <= 2500
        _check_edges(edges, n)
    ex = [t["expected"] for t in tests]
    assert ex.count(True) >= 4 and ex.count(False) >= 4


CHECKS["graph-valid-tree-check"] = (b_tree, g_tree, "exact")
VALIDATE["graph-valid-tree-check"] = v_tree

# ---------------------------------------------------------------- earliest moment everyone is connected
_t = [
    [6, [[101, 0, 1], [104, 3, 4], [107, 2, 3], [211, 1, 5], [224, 2, 4], [301, 0, 3], [312, 1, 2], [322, 4, 5]]],
    [4, [[0, 2, 3], [1, 0, 1], [3, 0, 3], [4, 1, 2], [7, 3, 1]]],
    [2, [[5, 0, 1]]],
    [2, []],
    [3, [[2, 0, 1], [3, 1, 2]]],
    [3, [[9, 1, 2], [4, 0, 1], [6, 0, 2]]],
    [4, [[10, 0, 1], [10, 2, 3], [10, 1, 2]]],
    [5, [[1, 0, 1], [2, 1, 2], [3, 2, 3]]],
    [5, [[8, 3, 4], [1, 0, 1], [6, 1, 2], [3, 2, 3], [9, 0, 4]]],
]
_r = rnd(9105)


def _timed_connected(r, n, extra, tmax=10 ** 6):
    es = _tree(r, n) + _pairs(r, n, extra)
    seen = set()
    out = []
    for a, b in es:
        k = (min(a, b), max(a, b))
        if k not in seen:
            seen.add(k)
            out.append([r.randint(0, tmax), a, b])
    r.shuffle(out)
    return out


_t.append([2000, _timed_connected(_r, 2000, 900)])
_t.append([2000, [[_r.randint(0, 10 ** 6), a, b] for a, b in _pairs(_r, 2000, 2800)]])  # sparse random: some node stays alone
_t.append([1500, [[1500 - i, i, i + 1] for i in range(1499)]])  # chain whose times shrink along the input

add(
    id="earliest-moment-everyone-friends", title="Earliest Moment of Full Friendship", diff="Medium", topic="Union Find",
    fn="earliestFullFriendship", params=[("n", "int"), ("logs", "int[][]")], ret="int", cmp="exact",
    desc="<p>There are <code>n</code> people labelled <code>0</code> to <code>n - 1</code>. Each log entry <code>[t, a, b]</code> records that people <code>a</code> and <code>b</code> became friends at time <code>t</code>. The logs come in no particular order.</p><p>Two people are <em>acquainted</em> at time <code>T</code> if they are friends by time <code>T</code> (their log time is at most <code>T</code>) or if they are linked by a chain of such friendships. Return the earliest time <code>T</code> at which <strong>every</strong> person is acquainted with every other person. If that never happens, return <code>-1</code>.</p><pre>n = 4, logs = [[0,2,3],[1,0,1],[3,0,3],[4,1,2],[7,3,1]]\n\nresult = 3     (after time 3: 2-3, 0-1 and 0-3 link all four people)</pre>",
    constraints=["2 &le; n &le; 2,000", "0 &le; logs.length &le; 3,000", "0 &le; t &le; 1,000,000", "0 &le; a, b &lt; n and a &ne; b", "No pair of people appears in two logs"],
    hints=["Friendships only ever get added over time, so the groups of acquainted people only merge, never split.",
           "Process the logs in increasing order of time and keep merging the groups of <code>a</code> and <code>b</code>.",
           "Count groups with union-find, starting from <code>n</code>. When a merge brings the count down to 1, the time of the current log is the answer. If you finish all logs with more than one group, return -1."],
    editorial=["Sort the logs by time. Maintain a union-find over the people with a counter <code>groups = n</code>. For each log, if the two people have different roots, merge them and decrement the counter. The first log that brings the counter to 1 gives the answer, because the state \"everyone connected\" is reached exactly then and not earlier. Several logs may share a time; the answer is a time value, so ties do not matter.",
               "If the counter is still above 1 after all logs, someone is cut off, so return -1. Sorting costs O(L log L) and the unions cost O(L &middot; &alpha;(n)), so the total is O(L log L + n). The main lesson: when a question asks <em>when</em> something becomes connected, sort the events by time and union them in that order."],
    time="O(L log L + n)", space="O(n)",
    solution='''def earliestFullFriendship(n, logs):
    parent = list(range(n))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    groups = n
    for t, a, b in sorted(logs):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb
            groups -= 1
            if groups == 1:
                return t
    return -1
''',
    tests=_t,
)


def b_earliest(n, logs):
    times = sorted({t for t, _, _ in logs})
    for T in times:
        reach = _closure(n, [(a, b) for t, a, b in logs if t <= T])
        if all(all(row) for row in reach):
            return T
    return -1


def g_earliest(r):
    n = r.randint(2, 6)
    es = _pairs(r, n, r.randint(0, n + 2))
    return [n, [[r.randint(0, 6), a, b] for a, b in es]]


def v_earliest(tests):
    for t in tests:
        n, logs = t["args"]
        assert 2 <= n <= 2000 and len(logs) <= 3000
        _check_edges([[a, b] for _, a, b in logs], n)
        assert all(0 <= x[0] <= 10 ** 6 for x in logs)
    ex = [t["expected"] for t in tests]
    assert -1 in ex and any(v >= 0 for v in ex)


CHECKS["earliest-moment-everyone-friends"] = (b_earliest, g_earliest, "exact")
VALIDATE["earliest-moment-everyone-friends"] = v_earliest

# ---------------------------------------------------------------- weakest road between first and last city
_t = [
    [4, [[1, 2, 9], [2, 3, 6], [2, 4, 5], [1, 4, 7]]],
    [4, [[1, 2, 2], [1, 3, 4], [3, 4, 7]]],
    [2, [[1, 2, 5]]],
    [3, [[1, 2, 4]]],
    [3, [[2, 3, 4]]],
    [5, [[1, 2, 10], [2, 3, 8], [3, 4, 1], [4, 5, 9], [1, 5, 20]]],
    [6, [[1, 2, 5], [2, 6, 7], [3, 4, 1], [4, 5, 1]]],
    [4, [[1, 4, 100], [2, 3, 1], [1, 2, 50]]],
]
_r = rnd(9106)


def _weighted(r, n, es, wmax=10000):
    return [[a, b, r.randint(1, wmax)] for a, b in es]


_t.append([2000, _weighted(_r, 2000, _tree(_r, 2000, base=1))])
_t.append([2000, _weighted(_r, 2000, _pairs(_r, 2000, 2000, base=1))])
_t.append([1600, _weighted(_r, 1600, _tree(_r, 800, base=1) + _tree(_r, 800, base=801))])
_t.append([1500, _weighted(_r, 1500, [[i, i + 1] for i in range(1, 1500)])])

add(
    id="weakest-road-between-first-and-last-city", title="Weakest Road Between Two Cities", diff="Medium", topic="Union Find",
    fn="weakestRoad", params=[("n", "int"), ("roads", "int[][]")], ret="int", cmp="exact",
    desc="<p>There are <code>n</code> cities labelled <code>1</code> to <code>n</code>. Each entry <code>roads[i] = [a, b, w]</code> is a two-way road between cities <code>a</code> and <code>b</code> with quality <code>w</code> (larger means better).</p><p>A <em>route</em> from city 1 to city <code>n</code> is any walk along roads; it may pass through the same city or road more than once. The <em>weakness</em> of a route is the smallest quality of any road on it.</p><p>Return the smallest weakness that any route from city 1 to city <code>n</code> can have (the worst route you could be made to take). If no route exists, return <code>-1</code>.</p><pre>n = 4, roads = [[1,2,9],[2,3,6],[2,4,5],[1,4,7]]\n\nresult = 5     (route 1-2-4 uses the quality-5 road; no route can be weaker)</pre>",
    constraints=["2 &le; n &le; 2,500", "0 &le; roads.length &le; 2,500", "1 &le; a, b &le; n and a &ne; b", "1 &le; w &le; 10,000", "No pair of cities appears twice"],
    hints=["Because a route may wander and reuse roads, a route can detour through any road that is connected to the path.",
           "So which roads can appear on some route from 1 to <code>n</code>? Exactly the roads in the connected component that contains both city 1 and city <code>n</code>.",
           "Union the endpoints of all roads. If cities 1 and <code>n</code> have different roots, answer -1. Otherwise the answer is the minimum <code>w</code> over all roads whose endpoint has the same root as city 1."],
    editorial=["Since walks may revisit cities, any road in the same connected component as city 1 can be included in a route from 1 to n (walk to it, cross it, come back, continue to n) as long as n is also in that component. Hence the answer is simply the smallest road weight inside that component.",
               "Union all roads. If <code>find(1) != find(n)</code>, return -1. Otherwise scan the roads once more and take the minimum weight among those with <code>find(a) == find(1)</code>. Time O((n + m) &middot; &alpha;(n)). A BFS from city 1 works equally well; the point is to recognise that the question is about connectivity, not about shortest paths."],
    time="O((n + m) &middot; &alpha;(n))", space="O(n)",
    solution='''def weakestRoad(n, roads):
    parent = list(range(n + 1))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for a, b, w in roads:
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb
    if find(1) != find(n):
        return -1
    root = find(1)
    return min(w for a, b, w in roads if find(a) == root)
''',
    tests=_t,
)


def b_weakest(n, roads):
    reach = _closure(n, [(a - 1, b - 1) for a, b, _ in roads])
    best = None
    for a, b, w in roads:
        a -= 1
        b -= 1
        if (reach[0][a] and reach[b][n - 1]) or (reach[0][b] and reach[a][n - 1]):
            best = w if best is None else min(best, w)
    return -1 if best is None else best


def g_weakest(r):
    n = r.randint(2, 7)
    es = _pairs(r, n, r.randint(0, n + 1), base=1)
    return [n, [[a, b, r.randint(1, 9)] for a, b in es]]


def v_weakest(tests):
    for t in tests:
        n, roads = t["args"]
        assert 2 <= n <= 2500 and len(roads) <= 2500
        _check_edges([[a, b] for a, b, _ in roads], n, base=1)
        assert all(1 <= w <= 10000 for _, _, w in roads)
    ex = [t["expected"] for t in tests]
    assert -1 in ex and sum(1 for v in ex if v > 0) >= 6


CHECKS["weakest-road-between-first-and-last-city"] = (b_weakest, g_weakest, "exact")
VALIDATE["weakest-road-between-first-and-last-city"] = v_weakest


# ---------------------------------------------------------------- count complete components
def _cliques(r, groups):
    """groups: list of (size, missing_edges). Returns (n, shuffled edge list) with randomly relabelled nodes."""
    n = sum(s for s, _ in groups)
    lab = list(range(n))
    r.shuffle(lab)
    e = []
    off = 0
    for s, miss in groups:
        pr = [(off + i, off + j) for i in range(s) for j in range(i + 1, s)]
        drop = set(r.sample(range(len(pr)), min(miss, len(pr))))
        for k, (a, b) in enumerate(pr):
            if k not in drop:
                e.append([lab[a], lab[b]] if r.random() < 0.5 else [lab[b], lab[a]])
        off += s
    r.shuffle(e)
    return n, e


_t = [
    [6, [[0, 1], [0, 2], [1, 2], [3, 4]]],
    [6, [[0, 1], [0, 2], [1, 2], [3, 4], [3, 5]]],
    [1, []],
    [3, []],
    [2, [[1, 0]]],
    [3, [[0, 1], [1, 2]]],
    [4, [[0, 1], [0, 2], [0, 3], [1, 2], [1, 3], [2, 3]]],
    [5, [[0, 1], [0, 2], [0, 3], [1, 2], [1, 3], [2, 3]]],
    [7, [[0, 1], [1, 2], [2, 0], [3, 4], [4, 5], [5, 3], [3, 6]]],
]
_r = rnd(9107)
_t.append(list(_cliques(_r, [(12, 0)] * 10 + [(10, 1)] * 12 + [(2, 0)] * 100 + [(1, 0)] * 300 + [(5, 0)] * 20 + [(7, 2)] * 5)))
_t.append(list(_cliques(_r, [(40, 0), (30, 0), (30, 1), (3, 0)] + [(4, 0)] * 40 + [(1, 0)] * 100)))
_t.append(list(_cliques(_r, [(1, 0)] * 800)))
_t.append(list(_cliques(_r, [(3, 1)] * 200 + [(3, 0)] * 100)))

add(
    id="count-complete-components", title="Count Complete Components", diff="Medium", topic="Union Find", tier="extra",
    fn="countCompleteComponents", params=[("n", "int"), ("edges", "int[][]")], ret="int", cmp="exact",
    desc="<p>An undirected graph has <code>n</code> nodes labelled <code>0</code> to <code>n - 1</code> and the edges listed in <code>edges</code>. A <em>component</em> is a maximal set of nodes that can reach each other along edges (a node with no edge is a component of its own).</p><p>A component is <em>complete</em> if <strong>every</strong> two different nodes inside it are joined directly by an edge. Return how many components are complete.</p><pre>n = 6, edges = [[0,1],[0,2],[1,2],[3,4]]\n\nresult = 3     ({0,1,2} is complete, {3,4} is complete, {5} is complete)</pre>",
    constraints=["1 &le; n &le; 1,000", "0 &le; edges.length &le; 2,500", "0 &le; a, b &lt; n and a &ne; b", "No pair of nodes appears twice"],
    hints=["A component with <code>k</code> nodes can have at most <code>k(k-1)/2</code> edges, and it is complete exactly when it has that many.",
           "Because edges never leave a component, you only need two numbers per component: its number of nodes and its number of edges.",
           "Union all edges, then count nodes per root and edges per root (use the root of one endpoint). A root is complete when <code>edges == nodes * (nodes - 1) / 2</code>."],
    editorial=["Merge the endpoints of every edge with union-find. Afterwards, group the nodes by root to get each component's node count <code>v</code>, and group the edges by the root of either endpoint to get its edge count <code>e</code>. Since there are no repeated edges, <code>e</code> can reach <code>v(v-1)/2</code> only when every pair of nodes is joined, so a component is complete exactly when <code>e == v(v-1)/2</code>.",
               "Isolated nodes have v = 1 and e = 0, which satisfies the formula, so they count as complete. Time is O(n + m &middot; &alpha;(n)). This pattern, collecting a statistic per union-find root after all unions, is very common in component problems."],
    time="O(n + m &middot; &alpha;(n))", space="O(n)",
    solution='''def countCompleteComponents(n, edges):
    parent = list(range(n))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for a, b in edges:
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb
    nodes = [0] * n
    links = [0] * n
    for i in range(n):
        nodes[find(i)] += 1
    for a, b in edges:
        links[find(a)] += 1
    return sum(1 for i in range(n) if nodes[i] and links[i] == nodes[i] * (nodes[i] - 1) // 2)
''',
    tests=_t,
)


def b_complete(n, edges):
    adj = [set() for _ in range(n)]
    for a, b in edges:
        adj[a].add(b)
        adj[b].add(a)
    seen = [False] * n
    cnt = 0
    for s in range(n):
        if seen[s]:
            continue
        comp = [s]
        seen[s] = True
        for u in comp:
            for v in adj[u]:
                if not seen[v]:
                    seen[v] = True
                    comp.append(v)
        if all(v in adj[u] for u in comp for v in comp if u != v):
            cnt += 1
    return cnt


def g_complete(r):
    parts = []
    left = r.randint(1, 9)
    while left > 0:
        s = r.randint(1, min(left, 4))
        parts.append((s, r.choice([0, 0, 1])))
        left -= s
    n, e = _cliques(r, parts)
    if n >= 2 and r.random() < 0.3:
        extra = _pairs(r, n, 1)
        if extra and extra[0] not in e and extra[0][::-1] not in e:
            e.append(extra[0])
    return [n, e]


def v_complete(tests):
    for t in tests:
        n, edges = t["args"]
        assert 1 <= n <= 1000 and len(edges) <= 2500
        _check_edges(edges, n)
    assert len({t["expected"] for t in tests}) >= 6


CHECKS["count-complete-components"] = (b_complete, g_complete, "exact")
VALIDATE["count-complete-components"] = v_complete

# ---------------------------------------------------------------- peaceful friend circles
_t = [
    [6, [[0, 1], [1, 2], [3, 4]], [[0, 2]]],
    [6, [[0, 1], [1, 2], [3, 4]], [[0, 3], [2, 5]]],
    [1, [], []],
    [3, [], [[0, 1]]],
    [4, [[0, 1], [2, 3]], [[1, 2]]],
    [4, [[0, 1], [2, 3]], [[0, 3], [1, 2]]],
    [5, [[0, 1], [1, 2], [2, 3], [3, 4]], [[0, 4]]],
    [5, [[0, 1], [1, 2], [2, 3], [3, 4]], []],
    [6, [[0, 1], [2, 3], [4, 5]], [[0, 2], [3, 5]]],
]
_r = rnd(9108)


def _forest_with_rivals(r, n, maxsize, cross, inside):
    sizes = []
    left = n
    while left > 0:
        s = min(left, r.randint(1, maxsize))
        sizes.append(s)
        left -= s
    lab = list(range(n))
    r.shuffle(lab)
    fr, comps, off = [], [], 0
    for s in sizes:
        nodes = lab[off:off + s]
        off += s
        comps.append(nodes)
        for i in range(1, s):
            a, b = nodes[i], nodes[r.randrange(i)]
            fr.append([a, b] if r.random() < 0.5 else [b, a])
    friend = {(min(a, b), max(a, b)) for a, b in fr}
    riv = set()
    big = [c for c in comps if len(c) >= 3]
    tries = 0
    while len(riv) < inside and big and tries < 10000:
        tries += 1
        c = r.choice(big)
        a, b = r.sample(c, 2)
        k = (min(a, b), max(a, b))
        if k not in friend:
            riv.add(k)
    while len(riv) < inside + cross and tries < 20000:
        tries += 1
        a, b = r.sample(range(n), 2)
        k = (min(a, b), max(a, b))
        if k not in friend:
            riv.add(k)
    rv = [[a, b] if r.random() < 0.5 else [b, a] for a, b in sorted(riv)]
    r.shuffle(fr)
    r.shuffle(rv)
    return [n, fr, rv]


_t.append(_forest_with_rivals(_r, 2000, 6, 700, 30))
_t.append(_forest_with_rivals(_r, 1500, 40, 20, 120))
_t.append(_forest_with_rivals(_r, 1200, 3, 300, 2))

add(
    id="peaceful-friend-circles-count", title="Peaceful Friend Circles", diff="Medium", topic="Union Find", tier="extra",
    fn="peacefulCircles", params=[("n", "int"), ("friendships", "int[][]"), ("rivalries", "int[][]")], ret="int", cmp="exact",
    desc="<p>There are <code>n</code> people labelled <code>0</code> to <code>n - 1</code>. Each entry <code>friendships[i] = [a, b]</code> makes <code>a</code> and <code>b</code> friends. A <em>friend circle</em> is a maximal group of people connected by chains of friendships (a person without friends is a circle of one).</p><p>Each entry <code>rivalries[j] = [x, y]</code> says that <code>x</code> and <code>y</code> are rivals. A circle is <em>peaceful</em> if no two members of it are rivals. Rivals who sit in different circles do not matter. Return the number of peaceful circles.</p><pre>n = 6, friendships = [[0,1],[1,2],[3,4]], rivalries = [[0,2],[2,5]]\n\nresult = 2     (circle {0,1,2} contains rivals 0 and 2; {3,4} and {5} are peaceful)</pre>",
    constraints=["1 &le; n &le; 2,000", "0 &le; friendships.length &le; 2,000", "0 &le; rivalries.length &le; 1,000", "0 &le; a, b, x, y &lt; n, a &ne; b and x &ne; y", "No pair appears twice within friendships, none twice within rivalries, and no pair is in both lists"],
    hints=["First work out which circle every person is in; the rivalries only matter in comparison with that.",
           "A rivalry <code>[x, y]</code> ruins a circle exactly when x and y belong to the same circle. A rivalry between two different circles ruins nothing.",
           "Union all friendships. Then for each rivalry, if <code>find(x) == find(y)</code>, mark that root as unpeaceful. The answer is the number of distinct roots minus the number of marked roots."],
    editorial=["Build the circles with union-find over the friendships. Then scan the rivalries: for each pair, compare the two roots. If they are equal, the circle with that root contains two rivals, so add the root to a set of spoiled circles. Rivalries across different circles are ignored.",
               "The number of circles equals the number of distinct roots over all n people (equivalently n minus the number of successful unions). The answer is that number minus the size of the spoiled set. Total time is O((n + m + k) &middot; &alpha;(n)) for m friendships and k rivalries."],
    time="O((n + m + k) &middot; &alpha;(n))", space="O(n)",
    solution='''def peacefulCircles(n, friendships, rivalries):
    parent = list(range(n))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    circles = n
    for a, b in friendships:
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb
            circles -= 1
    spoiled = set()
    for x, y in rivalries:
        rx = find(x)
        if rx == find(y):
            spoiled.add(rx)
    return circles - len(spoiled)
''',
    tests=_t,
)


def b_peaceful(n, friendships, rivalries):
    reach = _closure(n, friendships)
    circles = {tuple(row) for row in reach}
    bad = set()
    for x, y in rivalries:
        if reach[x][y]:
            bad.add(tuple(reach[x]))
    return len(circles) - len(bad)


def g_peaceful(r):
    n = r.randint(1, 8)
    fr = _pairs(r, n, r.randint(0, n))
    fs = {(min(a, b), max(a, b)) for a, b in fr}
    rv = [[a, b] for a, b in _pairs(r, n, r.randint(0, 4)) if (min(a, b), max(a, b)) not in fs]
    return [n, fr, rv]


def v_peaceful(tests):
    for t in tests:
        n, fr, rv = t["args"]
        assert 1 <= n <= 2000 and len(fr) <= 2000 and len(rv) <= 1000
        _check_edges(fr, n)
        _check_edges(rv, n)
        fs = {(min(a, b), max(a, b)) for a, b in fr}
        assert all((min(a, b), max(a, b)) not in fs for a, b in rv), "pair in both lists"
    assert len({t["expected"] for t in tests}) >= 6


CHECKS["peaceful-friend-circles-count"] = (b_peaceful, g_peaceful, "exact")
VALIDATE["peaceful-friend-circles-count"] = v_peaceful

# ---------------------------------------------------------------- one-sided follows
_t = [
    [[[0, 1, 0], [0, 0, 0], [0, 0, 0]]],
    [[[0, 0, 0], [0, 0, 0], [0, 0, 0]]],
    [[[1]]],
    [[[0]]],
    [[[0, 0, 1], [0, 0, 0], [0, 1, 0]]],
    [[[0, 1, 0, 0], [0, 0, 0, 0], [0, 0, 0, 1], [0, 0, 0, 0]]],
    [[[0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1], [0, 0, 0, 0]]],
    [[[0, 0, 0, 0], [1, 0, 0, 0], [1, 0, 0, 0], [0, 0, 1, 0]]],
    [[[1, 0, 0, 0, 0], [0, 1, 1, 0, 0], [0, 0, 1, 0, 0], [0, 0, 0, 1, 1], [1, 0, 0, 0, 1]]],
]
_r = rnd(9109)


def _follows(r, n, p, groups=None):
    m = [[0] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            if i == j:
                m[i][j] = r.randint(0, 1)
            elif groups is None or groups[i] == groups[j]:
                m[i][j] = 1 if r.random() < p else 0
    return m


_t.append([_follows(_r, 100, 0.004)])
_t.append([_follows(_r, 100, 0.012)])
_t.append([_follows(_r, 100, 0.2, groups=[i // 10 for i in range(100)])])
_t.append([_follows(_r, 70, 0.0)])

add(
    id="one-sided-follow-circle-count", title="Follow Circles", diff="Medium", topic="Union Find", tier="extra",
    fn="countFollowCircles", params=[("follows", "int[][]")], ret="int", cmp="exact",
    desc="<p>On a social site with <code>n</code> accounts, <code>follows[i][j] = 1</code> means account <code>i</code> follows account <code>j</code>. Following does <em>not</em> have to be returned: <code>follows[i][j]</code> and <code>follows[j][i]</code> can differ. The diagonal entries <code>follows[i][i]</code> carry no information.</p><p>Two accounts are in the same <em>circle</em> if you can get from one to the other by a chain of accounts where each neighbouring pair is linked by a follow in <strong>either</strong> direction. Return the number of circles.</p><pre>follows = [[0,1,0],\n           [0,0,0],\n           [0,0,0]]\n\nresult = 2     (accounts 0 and 1 form a circle; account 2 is alone)</pre>",
    constraints=["1 &le; n &le; 100", "follows is an n x n matrix with entries 0 or 1", "follows[i][j] and follows[j][i] may differ; follows[i][i] may be 0 or 1"],
    hints=["Ignore directions: a follow from i to j connects the two accounts just as much as a follow from j to i.",
           "This is the number-of-provinces problem, except that the matrix does not have to be symmetric. Treat <code>follows[i][j] = 1</code> as an undirected link.",
           "Start with n groups and union i with j whenever <code>follows[i][j] == 1</code> (check every ordered pair, or both <code>[i][j]</code> and <code>[j][i]</code> for each pair). Every successful merge reduces the number of circles by one."],
    editorial=["Start with every account in its own set, <code>circles = n</code>. Scan the whole matrix; for each cell <code>(i, j)</code> with <code>i != j</code> and value 1, find the roots of i and j and merge them if they differ, decreasing the counter. Because every ordered pair is visited, a one-sided follow is enough to link two accounts, and the diagonal is skipped.",
               "The answer is the number of sets left. Time is O(n&sup2; &middot; &alpha;(n)) since the matrix has n&sup2; cells. A common mistake is to only read the upper triangle (<code>j &gt; i</code>), which silently drops follows that appear only below the diagonal."],
    time="O(n&sup2; &middot; &alpha;(n))", space="O(n)",
    solution='''def countFollowCircles(follows):
    n = len(follows)
    parent = list(range(n))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    circles = n
    for i in range(n):
        row = follows[i]
        for j in range(n):
            if i != j and row[j]:
                a, b = find(i), find(j)
                if a != b:
                    parent[a] = b
                    circles -= 1
    return circles
''',
    tests=_t,
)


def b_follow(follows):
    n = len(follows)
    link = [(i, j) for i in range(n) for j in range(n) if i != j and follows[i][j]]
    reach = _closure(n, link)
    return len({tuple(row) for row in reach})


def g_follow(r):
    n = r.randint(1, 7)
    return [_follows(r, n, r.choice([0.1, 0.2, 0.3]))]


def v_follow(tests):
    for t in tests:
        (m,) = t["args"]
        n = len(m)
        assert 1 <= n <= 100 and all(len(row) == n for row in m)
        assert all(v in (0, 1) for row in m for v in row)
    assert len({t["expected"] for t in tests}) >= 6
    assert any(any(m[i][j] != m[j][i] for i in range(len(m)) for j in range(len(m))) for (m,) in (t["args"] for t in tests))


CHECKS["one-sided-follow-circle-count"] = (b_follow, g_follow, "exact")
VALIDATE["one-sided-follow-circle-count"] = v_follow

# =================================================================== HARD
# ---------------------------------------------------------------- redundant connection, directed
def _rooted_plus_edge(r, n, shape, kind):
    """A rooted tree on labels 1..n (edges parent->child) plus one extra directed edge, shuffled.
    kind 'root': the extra edge points at the root (creates a cycle); 'any': it points at any non-root node."""
    lab = list(range(1, n + 1))
    r.shuffle(lab)
    e = []
    for i in range(1, n):
        p = i - 1 if shape == "chain" else (0 if shape == "star" else r.randrange(i))
        e.append([lab[p], lab[i]])
    root = lab[0]
    have = {tuple(x) for x in e}
    while True:
        if kind == "root":
            v = root
        else:
            v = r.choice(lab[1:])
        u = r.choice(lab)
        if u != v and (u, v) not in have:
            break
    e.append([u, v])
    r.shuffle(e)
    return [e]


_t = [
    [[[1, 2], [1, 3], [2, 3]]],
    [[[1, 2], [2, 3], [3, 1]]],
    [[[2, 1], [3, 1], [4, 2], [1, 4]]],
    [[[1, 2], [2, 3], [3, 4], [4, 1], [1, 5]]],
    [[[5, 2], [5, 1], [3, 1], [3, 4], [2, 3]]],
    [[[1, 2], [2, 3], [3, 4], [1, 3]]],
    [[[1, 2], [3, 2], [2, 3]]],
    [[[2, 1], [1, 2], [1, 3]]],
    [[[4, 2], [1, 5], [5, 2], [5, 3], [2, 4]]],
    [[[1, 5], [3, 1], [3, 4], [4, 2], [5, 4]]],
]
_r = rnd(9110)
_t.append(_rooted_plus_edge(_r, 1000, "random", "any"))
_t.append(_rooted_plus_edge(_r, 1000, "chain", "root"))
_t.append(_rooted_plus_edge(_r, 1000, "chain", "any"))
_t.append(_rooted_plus_edge(_r, 1000, "star", "any"))
_t.append(_rooted_plus_edge(_r, 600, "random", "root"))

add(
    id="redundant-connection-directed", title="Redundant Connection in a Rooted Tree", diff="Hard", topic="Union Find",
    fn="findRedundantDirected", params=[("edges", "int[][]")], ret="int[]", cmp="exact",
    desc="<p>A <em>rooted tree</em> on nodes <code>1</code> to <code>n</code> is a directed graph in which exactly one node (the <em>root</em>) has no incoming edge, every other node has exactly one incoming edge (from its parent), and every node can be reached from the root by following edges.</p><p>You are given <code>edges</code>, where <code>edges[i] = [u, v]</code> is a directed edge from <code>u</code> to <code>v</code>. The list is a rooted tree on <code>n</code> nodes to which <strong>one extra directed edge</strong> was added (so it has exactly <code>n</code> edges).</p><p>Return an edge that can be removed so that the remaining <code>n - 1</code> edges form a rooted tree. If several edges work, return the one that appears <strong>last</strong> in the input.</p><pre>edges = [[1,2],[1,3],[2,3]]       result = [2,3]\nedges = [[2,1],[3,1],[4,2],[1,4]] result = [2,1]\nedges = [[1,2],[2,3],[3,1]]       result = [3,1]</pre>",
    constraints=["3 &le; n &le; 1,000, and edges.length = n", "1 &le; u, v &le; n and u &ne; v", "No directed edge appears twice", "The edges are a rooted tree plus exactly one extra edge"],
    hints=["After adding one edge there are only two ways it can break the tree: some node gets two parents, or a cycle appears (sometimes both).",
           "If some node <code>v</code> has two incoming edges, one of those two must go. Call the earlier one <code>first</code> and the later one <code>second</code>. Try ignoring <code>second</code> and run union-find on the rest: if it still makes a cycle, <code>first</code> must be the culprit.",
           "If no node has two parents, the extra edge points at the root and closes a cycle. Run union-find over the edges in order (ignoring direction); the edge that first joins two nodes already connected is the last edge of the cycle in input order, which is the answer."],
    editorial=["Count the parents of each node. Case 1: a node <code>v</code> has two incoming edges <code>first</code> and <code>second</code> (in input order). The answer is one of these two, since removing anything else leaves v with two parents. Rebuild the graph without <code>second</code> and run union-find on the remaining edges (ignoring direction). If a cycle shows up, then <code>second</code> was not the problem and <code>first</code> must be removed; otherwise removing <code>second</code> already gives a valid tree and, as the later edge, it is the answer to return.",
               "Case 2: every node has at most one parent. Then the extra edge points at the root, and the whole graph is one cycle with trees hanging off it. Union-find over the edges in order finds the first edge whose endpoints are already connected; that edge is the last edge of the cycle in input order, and removing any cycle edge gives a valid rooted tree, so the last one is the answer.",
               "Time is O(n &middot; &alpha;(n)) and space O(n). The tricky part is not the data structure but the case analysis: handle the two-parents case first, then fall back to the pure-cycle case."],
    time="O(n &middot; &alpha;(n))", space="O(n)",
    solution='''def findRedundantDirected(edges):
    n = len(edges)
    parent_of = [0] * (n + 1)
    first = second = None
    for u, v in edges:
        if parent_of[v]:
            first = [parent_of[v], v]
            second = [u, v]
        else:
            parent_of[v] = u
    uf = list(range(n + 1))

    def find(x):
        while uf[x] != x:
            uf[x] = uf[uf[x]]
            x = uf[x]
        return x

    for u, v in edges:
        if second is not None and [u, v] == second:
            continue
        ru, rv = find(u), find(v)
        if ru == rv:
            return first if second is not None else [u, v]
        uf[ru] = rv
    return second
''',
    tests=_t,
)


def b_rc2(edges):
    n = len(edges)
    for skip in range(n - 1, -1, -1):
        rest = [e for i, e in enumerate(edges) if i != skip]
        indeg = [0] * (n + 1)
        kids = {}
        for u, v in rest:
            indeg[v] += 1
            kids.setdefault(u, []).append(v)
        roots = [x for x in range(1, n + 1) if indeg[x] == 0]
        if len(roots) != 1 or any(indeg[x] > 1 for x in range(1, n + 1)):
            continue
        seen = {roots[0]}
        todo = [roots[0]]
        while todo:
            for w in kids.get(todo.pop(), []):
                if w not in seen:
                    seen.add(w)
                    todo.append(w)
        if len(seen) == n:
            return edges[skip]
    return None


def g_rc2(r):
    return _rooted_plus_edge(r, r.randint(3, 8), r.choice(["random", "random", "chain", "star"]), r.choice(["any", "any", "root"]))


def v_rc2(tests):
    for t in tests:
        (edges,) = t["args"]
        n = len(edges)
        assert 3 <= n <= 1000
        assert len({tuple(e) for e in edges}) == n, "repeated directed edge"
        assert all(1 <= u <= n and 1 <= v <= n and u != v for u, v in edges)
        assert b_rc2(edges) == t["expected"], "no valid removal / mismatch"
    assert len({tuple(t["expected"]) for t in tests}) >= 10


CHECKS["redundant-connection-directed"] = (b_rc2, g_rc2, "exact")
VALIDATE["redundant-connection-directed"] = v_rc2

# ---------------------------------------------------------------- remove edges, two travelers
def _typed(r, n, m, weights=(1, 1, 1)):
    """m random typed links [type, a, b] on nodes 1..n; the same (type, pair) is never repeated."""
    seen, out = set(), []
    tries = 0
    while len(out) < m and tries < 50 * m + 50:
        tries += 1
        a, b = r.sample(range(1, n + 1), 2)
        t = r.choices([1, 2, 3], weights)[0]
        k = (t, min(a, b), max(a, b))
        if k in seen:
            continue
        seen.add(k)
        out.append([t, a, b] if r.random() < 0.5 else [t, b, a])
    return out


def _feasible_typed(r, n, extra, p3):
    """A spanning tree whose links are shared (type 3) with probability p3, else one link per traveler, plus extras."""
    out, seen = [], set()
    for a, b in _tree(r, n, base=1):
        if r.random() < p3:
            ts = [3]
        else:
            ts = [1, 2]
        for t in ts:
            seen.add((t, min(a, b), max(a, b)))
            out.append([t, a, b])
    for e in _typed(r, n, extra):
        k = (e[0], min(e[1], e[2]), max(e[1], e[2]))
        if k not in seen:
            seen.add(k)
            out.append(e)
    r.shuffle(out)
    return out


_t = [
    [4, [[3, 1, 2], [3, 2, 3], [1, 1, 3], [1, 2, 4], [1, 1, 2], [2, 3, 4]]],
    [4, [[3, 1, 2], [3, 2, 3], [1, 1, 4], [2, 1, 4]]],
    [4, [[3, 2, 3], [1, 1, 2], [2, 3, 4]]],
    [1, []],
    [2, []],
    [2, [[3, 1, 2]]],
    [2, [[1, 1, 2], [2, 1, 2], [3, 1, 2]]],
    [3, [[1, 1, 2], [1, 2, 3], [2, 1, 2], [2, 2, 3]]],
    [3, [[1, 1, 2], [1, 2, 3], [1, 1, 3], [2, 1, 2], [2, 2, 3], [2, 1, 3]]],
    [5, [[3, 1, 2], [3, 2, 3], [3, 3, 4], [3, 4, 5], [3, 1, 5], [1, 1, 3], [2, 2, 5]]],
]
_r = rnd(9111)
_t.append([1000, _feasible_typed(_r, 1000, 700, 0.5)])
_t.append([1000, _feasible_typed(_r, 1000, 1000, 0.9)])
_t.append([1500, _typed(_r, 1500, 2400, (4, 4, 1))])  # sparse typed random graph: usually impossible
_t.append([60, _typed(_r, 60, 1500, (1, 1, 1))])  # dense: almost everything is removable

add(
    id="max-edges-removable-two-travelers", title="Remove the Most Roads for Two Travelers", diff="Hard", topic="Union Find",
    fn="maxRemovable", params=[("n", "int"), ("edges", "int[][]")], ret="int", cmp="exact",
    desc="<p>A park has <code>n</code> junctions labelled <code>1</code> to <code>n</code>, and two visitors, Alice and Bob. Every path joins two junctions in both directions and has a type: <code>edges[i] = [type, a, b]</code>.</p><ul><li>type <code>1</code>: only Alice may walk it,</li><li>type <code>2</code>: only Bob may walk it,</li><li>type <code>3</code>: both may walk it.</li></ul><p>You may close down (delete) some paths, but afterwards <strong>each</strong> visitor must still be able to reach every junction from every other junction using the paths they are allowed to use. Return the maximum number of paths you can delete, or <code>-1</code> if this is impossible even without deleting anything.</p><pre>n = 4, edges = [[3,1,2],[3,2,3],[1,1,3],[1,2,4],[1,1,2],[2,3,4]]\n\nresult = 2     (delete [1,1,3] and [1,1,2])</pre>",
    constraints=["1 &le; n &le; 1,500", "0 &le; edges.length &le; 2,500", "type is 1, 2 or 3; 1 &le; a, b &le; n and a &ne; b", "The same type is never listed twice for the same pair of junctions (different types between one pair are allowed)"],
    hints=["Each visitor needs a spanning tree of the junctions made of paths they may use, so each needs exactly <code>n - 1</code> paths at least. Shared paths (type 3) can serve both at once.",
           "Prefer shared paths. First process all type-3 paths: keep one only if it joins two different groups (of a union-find that is used for both visitors).",
           "Then process type 1 with Alice's own union-find and type 2 with Bob's, keeping a path only when it merges two groups. At the end each visitor must have exactly one group, otherwise the answer is -1. The answer is the total number of paths minus the paths kept."],
    editorial=["A set of paths works for Alice exactly when her allowed paths (types 1 and 3) connect all junctions, and likewise for Bob (types 2 and 3). Minimal such sets are spanning trees, so we want to <em>keep</em> as few paths as possible. A shared path counts for both visitors, so it is never worse than a private path for the same pair: use shared paths first.",
               "Keep two union-find structures, one for Alice and one for Bob. Pass 1: for every type-3 path, try to merge in Alice's structure; if it merged (that means it also merges in Bob's, since the two structures are identical during this pass), merge in Bob's too and count one kept path. Pass 2: type-1 paths go through Alice's structure only, type-2 paths through Bob's, each counted when it merges two groups. Finally both structures must be a single group, else return -1; otherwise the answer is <code>len(edges) - kept</code>.",
               "Why greedy is right: shared paths first give both trees a common backbone, and every other kept path is needed by exactly one visitor. Any valid solution has at least as many kept paths. Time O(m &middot; &alpha;(n))."],
    time="O((n + m) &middot; &alpha;(n))", space="O(n)",
    solution='''def maxRemovable(n, edges):
    def make():
        return list(range(n + 1))

    def find(p, x):
        while p[x] != x:
            p[x] = p[p[x]]
            x = p[x]
        return x

    alice, bob = make(), make()
    ga = gb = n
    kept = 0
    for t, a, b in edges:
        if t != 3:
            continue
        ra, rb = find(alice, a), find(alice, b)
        if ra != rb:
            alice[ra] = rb
            ga -= 1
            xa, xb = find(bob, a), find(bob, b)
            bob[xa] = xb
            gb -= 1
            kept += 1
    for t, a, b in edges:
        if t == 1:
            ra, rb = find(alice, a), find(alice, b)
            if ra != rb:
                alice[ra] = rb
                ga -= 1
                kept += 1
        elif t == 2:
            ra, rb = find(bob, a), find(bob, b)
            if ra != rb:
                bob[ra] = rb
                gb -= 1
                kept += 1
    if ga != 1 or gb != 1:
        return -1
    return len(edges) - kept
''',
    tests=_t,
)


def b_travelers(n, edges):
    m = len(edges)

    def connected(keep, types):
        pairs = [(edges[i][1] - 1, edges[i][2] - 1) for i in range(m) if keep >> i & 1 and edges[i][0] in types]
        return all(all(row) for row in _closure(n, pairs))

    best = None
    for mask in range(1 << m):
        kept = bin(mask).count("1")
        if best is not None and kept >= best:
            continue
        if connected(mask, (1, 3)) and connected(mask, (2, 3)):
            best = kept
    return -1 if best is None else m - best


def g_travelers(r):
    n = r.randint(1, 5)
    m = r.randint(0, 8)
    return [n, _typed(r, n, m) if n >= 2 else []]


def v_travelers(tests):
    for t in tests:
        n, edges = t["args"]
        assert 1 <= n <= 1500 and len(edges) <= 2500
        seen = set()
        for ty, a, b in edges:
            assert ty in (1, 2, 3) and 1 <= a <= n and 1 <= b <= n and a != b
            k = (ty, min(a, b), max(a, b))
            assert k not in seen, "repeated typed pair"
            seen.add(k)
    ex = [t["expected"] for t in tests]
    assert -1 in ex and sum(1 for v in ex if v > 0) >= 5 and 0 in ex


CHECKS["max-edges-removable-two-travelers"] = (b_travelers, g_travelers, "exact")
VALIDATE["max-edges-removable-two-travelers"] = v_travelers
