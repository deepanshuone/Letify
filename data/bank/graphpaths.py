"""Problems: graphs given as edge lists (traversal, shortest paths, spanning trees, orderings)."""
import heapq
from itertools import combinations, permutations, product

from lib import add, rnd, CHECKS, VALIDATE, gen_arr  # noqa: F401

MOD = 10 ** 9 + 7


# ------------------------------------------------------------------ shared helpers
def _pairs(r, n, m, connected=False):
    """m distinct undirected pairs on 0..n-1 (random labels, random orientation, random order).
    With connected=True the pairs contain a random spanning tree."""
    perm = list(range(n))
    r.shuffle(perm)
    s = set()
    if connected:
        for v in range(1, n):
            s.add((r.randrange(v), v))
    m = min(m, n * (n - 1) // 2)
    while len(s) < m:
        u, v = r.sample(range(n), 2)
        s.add((min(u, v), max(u, v)))
    out = []
    for u, v in sorted(s):
        a, b = perm[u], perm[v]
        out.append([a, b] if r.random() < 0.5 else [b, a])
    r.shuffle(out)
    return out


def _dpairs(r, n, m):
    """m distinct directed pairs (u, v), u != v."""
    m = min(m, n * (n - 1))
    s = set()
    while len(s) < m:
        u, v = r.sample(range(n), 2)
        s.add((u, v))
    out = [list(x) for x in sorted(s)]
    r.shuffle(out)
    return out


def _unordered_distinct(edges):
    seen = set()
    for e in edges:
        u, v = e[0], e[1]
        k = (min(u, v), max(u, v))
        assert k not in seen, "duplicate edge"
        seen.add(k)


# ====================================================================== EASY
# ---------------------------------------------------------------- star graph center
_tests = [
    [[[1, 2], [2, 3]]],
    [[[1, 2], [5, 1], [1, 3], [1, 4]]],
    [[[4, 2], [1, 2], [2, 3]]],
    [[[3, 1], [2, 1]]],
    [[[1, 3], [2, 3]]],
    [[[2, 1], [3, 1]]],
    [[[7, 4], [4, 1], [3, 4], [4, 6], [5, 4], [2, 4]]],
    [[[2, 5], [5, 1], [3, 5], [4, 5], [5, 6]]],
]
_r = rnd(7101)
for _n, _c in ((5001, 3000), (5001, 1), (5001, 5001), (2000, 777), (3, 2)):
    _leaves = [x for x in range(1, _n + 1) if x != _c]
    _e = [[_c, x] if _r.random() < 0.5 else [x, _c] for x in _leaves]
    _r.shuffle(_e)
    _tests.append([_e])

add(
    id="star-graph-center", title="Star Graph Center", diff="Easy", topic="Graphs",
    fn="findCenter", params=[("edges", "int[][]")], ret="int", cmp="exact",
    desc="<p>A <em>star graph</em> has one center node that is joined directly to every other node, and has no other connections. The graph has <code>n</code> nodes labelled <code>1</code> to <code>n</code> and therefore exactly <code>n - 1</code> edges.</p><p>You are given the edges as pairs <code>edges[i] = [a, b]</code>, in no particular order and with either endpoint first. The edges are guaranteed to describe a star graph. Return the label of its center.</p>",
    constraints=["3 &le; n &le; 5,001, so 2 &le; edges.length &le; 5,000", "edges[i].length == 2 and 1 &le; edges[i][j] &le; n", "The edges form a valid star graph"],
    hints=["In a star every edge touches the center. What does that say about any two different edges?",
           "Two different edges share exactly one node, and that shared node must be the center.",
           "You only need the first two edges: whichever endpoint of edge 0 also appears in edge 1 is the answer. No counting is required."],
    editorial=["Counting how often each label occurs works: the center occurs in every edge, so it is the one label with count <code>n - 1</code>. That takes O(n) time and O(n) space.",
               "A constant-time observation does better. Because n &ge; 3 there are at least two edges, and both contain the center. Each of those edges has two endpoints; the center is the only label they have in common. So compare the endpoints of <code>edges[0]</code> with the endpoints of <code>edges[1]</code> and return the shared one. The other labels are leaves and each appears in just one edge, so they can never be shared."],
    time="O(1)", space="O(1)",
    solution='''def findCenter(edges):
    a, b = edges[0]
    c, d = edges[1]
    return a if a == c or a == d else b
''',
    tests=_tests,
)


def b_star(edges):
    cnt = {}
    for u, v in edges:
        cnt[u] = cnt.get(u, 0) + 1
        cnt[v] = cnt.get(v, 0) + 1
    for node, c in cnt.items():
        if c == len(edges):
            return node


def g_star(r):
    n = r.randint(3, 8)
    c = r.randint(1, n)
    perm = list(range(1, n + 1))
    r.shuffle(perm)
    edges = [[c, x] if r.random() < 0.5 else [x, c] for x in perm if x != c]
    return [edges]


def v_star(tests):
    for t in tests:
        edges = t["args"][0]
        n = len(edges) + 1
        assert 3 <= n <= 5001
        cnt = {}
        for u, v in edges:
            assert 1 <= u <= n and 1 <= v <= n and u != v
            cnt[u] = cnt.get(u, 0) + 1
            cnt[v] = cnt.get(v, 0) + 1
        assert len(cnt) == n
        assert cnt[t["expected"]] == n - 1
        assert sorted(cnt.values()).count(1) == n - 1


CHECKS["star-graph-center"] = (b_star, g_star, "exact")
VALIDATE["star-graph-center"] = v_star

# ---------------------------------------------------------------- path exists
_tests = [
    [3, [[0, 1], [1, 2], [2, 0]], 0, 2],
    [6, [[0, 1], [0, 2], [3, 5], [5, 4], [4, 3]], 0, 5],
    [1, [], 0, 0],
    [2, [], 0, 1],
    [2, [[1, 0]], 0, 1],
    [5, [[0, 1], [1, 2], [2, 3], [3, 4]], 4, 0],
    [4, [[0, 1], [2, 3]], 1, 1],
    [7, [[0, 1], [1, 2], [3, 4], [4, 5], [5, 6], [6, 3]], 2, 4],
    [8, [[0, 1], [2, 1], [2, 3], [4, 3], [4, 5], [6, 5], [7, 6]], 0, 7],
]
_r = rnd(7102)
_tests.append([2000, [[i, i + 1] for i in range(1999)], 0, 1999])  # a single long path
_tests.append([2000, [[i, i + 1] for i in range(1999) if i != 1000], 0, 1999])  # path broken in the middle
_e = _pairs(_r, 1000, 3000, connected=True)
_tests.append([2000, _e + [[a + 1000, b + 1000] for a, b in _pairs(_r, 1000, 2000, connected=True)], 17, 954])
_tests.append([2000, _e + [[a + 1000, b + 1000] for a, b in _pairs(_r, 1000, 2000, connected=True)], 17, 1954])
_tests.append([2000, _pairs(_r, 2000, 900), 5, 1500])

add(
    id="path-exists-in-undirected-graph", title="Path Exists in an Undirected Graph", diff="Easy", topic="Graphs",
    fn="validPath", params=[("n", "int"), ("edges", "int[][]"), ("source", "int"), ("destination", "int")], ret="bool", cmp="exact",
    desc="<p>A network has <code>n</code> nodes labelled <code>0</code> to <code>n - 1</code>. Each entry <code>edges[i] = [a, b]</code> is a two-way connection between nodes <code>a</code> and <code>b</code>. No pair of nodes is joined by more than one edge and no node is joined to itself.</p><p>Return <code>true</code> if you can travel from node <code>source</code> to node <code>destination</code> by following connections, and <code>false</code> otherwise. A node can always reach itself.</p>",
    constraints=["1 &le; n &le; 2,000", "0 &le; edges.length &le; 5,000", "0 &le; a, b, source, destination &lt; n, and a &ne; b", "No two edges join the same pair of nodes"],
    hints=["Think of the connections as a graph. The question is whether two nodes lie in the same connected piece.",
           "Starting from <code>source</code>, repeatedly visit neighbours you have not seen yet (BFS or DFS) and note everything you reach.",
           "Build an adjacency list first, keep a <code>visited</code> array, and stop early when you pop <code>destination</code>. Use an explicit queue or stack so a 2,000-node chain cannot overflow the recursion limit."],
    editorial=["Turn the edge list into an adjacency list, adding each edge in both directions. Run a breadth-first search from <code>source</code>, marking nodes as visited when they are first put on the queue. If <code>destination</code> is ever reached the answer is <code>true</code>; if the queue empties first, it is <code>false</code>. When source and destination are the same node the search succeeds immediately.",
               "A union-find structure is an equally good alternative: union the endpoints of every edge, then compare the representatives of the two nodes. It never builds an adjacency list and is handy if the question has to be answered for many pairs. Both approaches take O(n + m) time."],
    time="O(n + m)", space="O(n + m)",
    solution='''from collections import deque


def validPath(n, edges, source, destination):
    adj = [[] for _ in range(n)]
    for a, b in edges:
        adj[a].append(b)
        adj[b].append(a)
    seen = [False] * n
    seen[source] = True
    q = deque([source])
    while q:
        u = q.popleft()
        if u == destination:
            return True
        for v in adj[u]:
            if not seen[v]:
                seen[v] = True
                q.append(v)
    return False
''',
    tests=_tests,
)


def b_path(n, edges, source, destination):
    reach = [[i == j for j in range(n)] for i in range(n)]
    for a, b in edges:
        reach[a][b] = reach[b][a] = True
    for k in range(n):
        for i in range(n):
            if reach[i][k]:
                for j in range(n):
                    if reach[k][j]:
                        reach[i][j] = True
    return reach[source][destination]


def g_path(r):
    n = r.randint(1, 8)
    m = r.randint(0, n)
    return [n, _pairs(r, n, m) if n >= 2 else [], r.randrange(n), r.randrange(n)]


def v_path(tests):
    for t in tests:
        n, edges, s, d = t["args"]
        assert 1 <= n <= 2000 and len(edges) <= 5000 and 0 <= s < n and 0 <= d < n
        for a, b in edges:
            assert 0 <= a < n and 0 <= b < n and a != b
        _unordered_distinct(edges)


CHECKS["path-exists-in-undirected-graph"] = (b_path, g_path, "exact")
VALIDATE["path-exists-in-undirected-graph"] = v_path

# ====================================================================== MEDIUM
# ---------------------------------------------------------------- count paths in a DAG
_tests = [
    [4, [[0, 1], [0, 2], [1, 3], [2, 3]]],
    [5, [[0, 1], [1, 2], [2, 3], [3, 4], [0, 2], [1, 3], [2, 4]]],
    [3, [[0, 1]]],
    [2, []],
    [2, [[0, 1]]],
    [2, [[1, 0]]],
    [4, [[2, 0], [3, 2], [1, 3]]],
    [6, [[0, 1], [0, 2], [1, 3], [2, 3], [3, 5], [4, 5], [0, 4], [1, 4]]],
    [5, [[4, 0], [4, 1], [0, 1], [1, 2], [2, 3]]],
]
_r = rnd(7103)


def _layered(r, layers, width):
    """Complete bipartite connections between consecutive layers; node 0 is the source, node n-1 the sink."""
    n = 2 + layers * width
    mid = list(range(1, n - 1))
    r.shuffle(mid)
    L = [mid[i * width:(i + 1) * width] for i in range(layers)]
    e = [[0, x] for x in L[0]] + [[x, n - 1] for x in L[-1]]
    for i in range(layers - 1):
        e += [[a, b] for a in L[i] for b in L[i + 1]]
    r.shuffle(e)
    return n, e


def _dag(r, n, m, skip_source=False):
    """Random DAG on 0..n-1 where 0 and n-1 are free to sit anywhere in the hidden order."""
    order = list(range(n))
    r.shuffle(order)
    s = set()
    m = min(m, n * (n - 1) // 2)
    while len(s) < m:
        i, j = r.sample(range(n), 2)
        s.add((min(i, j), max(i, j)))
    e = [[order[i], order[j]] for i, j in sorted(s)]
    r.shuffle(e)
    return e


_n, _e = _layered(_r, 300, 3)
_tests.append([_n, _e])
_n, _e = _layered(_r, 60, 8)
_tests.append([_n, _e])
_n, _e = _layered(_r, 1, 4)
_tests.append([_n, _e])
_tests.append([1000, _dag(_r, 1000, 5000)])
_tests.append([1000, [[i, i + 1] for i in range(999)] + [[i, i + 2] for i in range(998)]])  # Fibonacci style counts
_tests.append([800, _dag(_r, 800, 2500)])

add(
    id="count-paths-in-a-dag", title="Count Paths in a DAG", diff="Medium", topic="Graphs",
    fn="countDagPaths", params=[("n", "int"), ("edges", "int[][]")], ret="int", cmp="exact",
    desc="<p>A directed graph has <code>n</code> nodes labelled <code>0</code> to <code>n - 1</code>. Each entry <code>edges[i] = [a, b]</code> is a one-way edge from <code>a</code> to <code>b</code>. The graph is guaranteed to contain <em>no cycles</em>.</p><p>Count the distinct paths that start at node <code>0</code> and end at node <code>n - 1</code>. Two paths are different if they use a different sequence of edges. The count can be astronomically large, so return it modulo <code>1,000,000,007</code>.</p><p>Note that node <code>0</code> may have incoming edges, and node <code>n - 1</code> may have outgoing edges; only the paths that run from <code>0</code> to <code>n - 1</code> are counted. If <code>n - 1</code> cannot be reached the answer is <code>0</code>.</p>",
    constraints=["2 &le; n &le; 1,000", "0 &le; edges.length &le; 5,000", "0 &le; a, b &lt; n and a &ne; b", "The graph is acyclic and no ordered pair (a, b) appears twice"],
    hints=["Count the paths ending at each node instead of enumerating them: how many ways are there to arrive at node v?",
           "ways[v] is the sum of ways[u] over every edge u &rarr; v, and ways[0] = 1. This only works if every u is finished before v is computed.",
           "Process the nodes in topological order (Kahn's algorithm with in-degrees). Push ways forward along each edge, taking the sum modulo 1,000,000,007, and read ways[n - 1] at the end."],
    editorial=["Enumerating the paths is hopeless because their number can grow exponentially. Instead let <code>ways[v]</code> be the number of paths from node 0 to v. Node 0 has one (empty) path to itself, and any other node is reached through one of its in-neighbours, so <code>ways[v] = sum of ways[u]</code> over edges <code>u &rarr; v</code>.",
               "Because the graph is acyclic we can order the nodes so that every edge points forward. Kahn's algorithm provides that order: keep in-degrees, start from the nodes of in-degree 0, and whenever a node is taken, add its <code>ways</code> into each successor and decrement that successor's in-degree. A node is taken only when all its predecessors were processed, so its <code>ways</code> value is final at that moment. Nodes that cannot be reached from 0 simply keep a count of 0 and pass zeros along. Total work is O(n + m). A memoised DFS from node 0 gives the same result, but may recurse 1,000 levels deep."],
    time="O(n + m)", space="O(n + m)",
    solution='''def countDagPaths(n, edges):
    MOD = 1000000007
    adj = [[] for _ in range(n)]
    indeg = [0] * n
    for a, b in edges:
        adj[a].append(b)
        indeg[b] += 1
    ways = [0] * n
    ways[0] = 1
    stack = [i for i in range(n) if indeg[i] == 0]
    while stack:
        u = stack.pop()
        for v in adj[u]:
            ways[v] = (ways[v] + ways[u]) % MOD
            indeg[v] -= 1
            if indeg[v] == 0:
                stack.append(v)
    return ways[n - 1]
''',
    tests=_tests,
)


def b_dagpaths(n, edges):
    adj = [[] for _ in range(n)]
    for a, b in edges:
        adj[a].append(b)

    def go(u):
        if u == n - 1:
            return 1
        return sum(go(v) for v in adj[u])

    return go(0) % MOD


def g_dagpaths(r):
    n = r.randint(2, 8)
    return [n, _dag(r, n, r.randint(0, n * 2))]


def v_dagpaths(tests):
    for t in tests:
        n, edges = t["args"]
        assert 2 <= n <= 1000 and len(edges) <= 5000
        indeg = [0] * n
        adj = [[] for _ in range(n)]
        seen = set()
        for a, b in edges:
            assert 0 <= a < n and 0 <= b < n and a != b and (a, b) not in seen
            seen.add((a, b))
            adj[a].append(b)
            indeg[b] += 1
        stack = [i for i in range(n) if indeg[i] == 0]
        done = 0
        while stack:
            u = stack.pop()
            done += 1
            for v in adj[u]:
                indeg[v] -= 1
                if indeg[v] == 0:
                    stack.append(v)
        assert done == n, "graph has a cycle"


CHECKS["count-paths-in-a-dag"] = (b_dagpaths, g_dagpaths, "exact")
VALIDATE["count-paths-in-a-dag"] = v_dagpaths

# ---------------------------------------------------------------- bipartite check (edge list)
_tests = [
    [4, [[0, 1], [1, 2], [2, 3], [3, 0]]],
    [3, [[0, 1], [1, 2], [2, 0]]],
    [1, []],
    [1, [[0, 0]]],
    [5, []],
    [2, [[0, 1]]],
    [6, [[0, 1], [2, 3], [3, 4], [4, 2]]],
    [6, [[0, 3], [0, 4], [1, 3], [1, 5], [2, 4], [2, 5]]],
    [5, [[0, 1], [1, 2], [2, 3], [3, 4], [4, 0]]],
    [7, [[0, 1], [1, 2], [3, 4], [4, 5], [5, 6], [6, 3], [2, 2]]],
]
_r = rnd(7104)
_tests.append([2000, [[i, i + 1] for i in range(1999)] + [[0, 1999]]])  # even cycle of length 2000
_tests.append([2000, [[i, i + 1] for i in range(1999)] + [[0, 1998]]])  # odd cycle of length 1999


def _bip_graph(r, n, m):
    side = [r.randint(0, 1) for _ in range(n)]
    perm = list(range(n))
    s = set()
    for v in range(1, n):  # connect with a bipartite tree
        cands = [u for u in range(v) if side[u] != side[v]]
        if cands:
            s.add((r.choice(cands), v))
    tries = 0
    while len(s) < m and tries < 20 * m:
        tries += 1
        u, v = r.sample(range(n), 2)
        if side[u] != side[v]:
            s.add((min(u, v), max(u, v)))
    out = [[a, b] if r.random() < 0.5 else [b, a] for a, b in sorted(s)]
    r.shuffle(out)
    return out, side


_e, _side = _bip_graph(_r, 2000, 4800)
_tests.append([2000, _e])
_same = [(u, v) for u in range(2000) for v in range(u + 1, 2000) if _side[u] == _side[v]]
_u, _v = _same[1234]
_tests.append([2000, _e + [[_u, _v]]])
_tests.append([1500, _pairs(_r, 1500, 1400)])
_tests.append([1000, _pairs(_r, 1000, 5000)])

add(
    id="is-graph-bipartite-edge-list", title="Is the Graph Bipartite?", diff="Medium", topic="Graphs",
    fn="isBipartite", params=[("n", "int"), ("edges", "int[][]")], ret="bool", cmp="exact",
    desc="<p>An undirected graph has <code>n</code> nodes labelled <code>0</code> to <code>n - 1</code>, and the edge list <code>edges</code> where <code>edges[i] = [a, b]</code> joins nodes <code>a</code> and <code>b</code>. The graph may be disconnected. An edge may join a node to itself, but no pair of nodes appears twice.</p><p>The graph is <em>bipartite</em> if its nodes can be split into two groups so that every edge has one endpoint in each group. Return <code>true</code> if the graph is bipartite and <code>false</code> otherwise.</p>",
    constraints=["1 &le; n &le; 2,000", "0 &le; edges.length &le; 5,000", "0 &le; a, b &lt; n", "No two edges join the same unordered pair of nodes; self-loops are allowed"],
    hints=["Try to colour every node with one of two colours so that neighbours always differ. Once one node's colour is chosen, what does that force for its neighbours?",
           "Colouring spreads along edges. If you ever find an edge whose two endpoints must share a colour, the graph cannot be split. Remember the graph can have several components.",
           "Run BFS from every uncoloured node. Give a newly discovered neighbour the opposite colour of its parent; if you meet an already coloured neighbour with the same colour as the current node (a self-loop does this too), return <code>false</code>."],
    editorial=["A graph is bipartite exactly when it has no cycle of odd length, and two-colouring finds such a cycle if there is one. Build the adjacency list. For each node that has no colour yet, start a BFS: colour it 0, and for every popped node look at each neighbour. An uncoloured neighbour gets the opposite colour and joins the queue; a coloured neighbour with the same colour as the popped node proves an odd cycle (or a self-loop, where the neighbour is the node itself), so the answer is <code>false</code>.",
               "Starting a fresh search from each still-uncoloured node handles disconnected graphs, including isolated nodes, which are trivially fine. The work is O(n + m). DFS with a colour array or a union-find that links each node to the opposite copy of its neighbour give the same answer; the iterative BFS avoids deep recursion on a path of 2,000 nodes."],
    time="O(n + m)", space="O(n + m)",
    solution='''from collections import deque


def isBipartite(n, edges):
    adj = [[] for _ in range(n)]
    for a, b in edges:
        adj[a].append(b)
        adj[b].append(a)
    color = [-1] * n
    for s in range(n):
        if color[s] != -1:
            continue
        color[s] = 0
        q = deque([s])
        while q:
            u = q.popleft()
            for v in adj[u]:
                if color[v] == -1:
                    color[v] = 1 - color[u]
                    q.append(v)
                elif color[v] == color[u]:
                    return False
    return True
''',
    tests=_tests,
)


def b_bip(n, edges):
    for mask in range(1 << n):
        if all(((mask >> a) & 1) != ((mask >> b) & 1) for a, b in edges):
            return True
    return False


def g_bip(r):
    n = r.randint(1, 9)
    if r.random() < 0.5 or n < 2:
        e = _pairs(r, n, r.randint(0, n + 2)) if n >= 2 else []
    else:
        e, _ = _bip_graph(r, n, r.randint(1, n + 2))
        if r.random() < 0.5:
            e = e + _pairs(r, n, 1)
            e = [list(x) for x in {(min(a, b), max(a, b)) for a, b in e}]
    if r.random() < 0.1:
        s = r.randrange(n)
        e = e + [[s, s]]
    return [n, e]


def v_bip(tests):
    for t in tests:
        n, edges = t["args"]
        assert 1 <= n <= 2000 and len(edges) <= 5000
        for a, b in edges:
            assert 0 <= a < n and 0 <= b < n
        _unordered_distinct(edges)


CHECKS["is-graph-bipartite-edge-list"] = (b_bip, g_bip, "exact")
VALIDATE["is-graph-bipartite-edge-list"] = v_bip

# ---------------------------------------------------------------- cheapest flights within k stops
_tests = [
    [4, [[0, 1, 100], [1, 2, 100], [2, 0, 100], [1, 3, 600], [2, 3, 200]], 0, 3, 1],
    [3, [[0, 1, 100], [1, 2, 100], [0, 2, 500]], 0, 2, 1],
    [3, [[0, 1, 100], [1, 2, 100], [0, 2, 500]], 0, 2, 0],
    [2, [], 0, 1, 1],
    [2, [[1, 0, 5]], 0, 1, 1],
    [5, [[0, 1, 1], [1, 2, 1], [2, 3, 1], [3, 4, 1], [0, 4, 10]], 0, 4, 2],
    [5, [[0, 1, 1], [1, 2, 1], [2, 3, 1], [3, 4, 1], [0, 4, 10]], 0, 4, 3],
    [4, [[0, 1, 5], [1, 0, 5], [1, 2, 5], [2, 1, 5], [2, 3, 5], [0, 3, 40]], 3, 0, 3],
    [4, [[0, 1, 1], [0, 2, 5], [1, 2, 1], [2, 3, 1], [1, 3, 6]], 0, 3, 1],
    [6, [[0, 1, 2], [1, 2, 2], [2, 3, 2], [3, 4, 2], [4, 5, 2], [0, 2, 3], [2, 4, 3], [3, 5, 9]], 0, 5, 2],
]
_r = rnd(7105)
_tests.append([100, [[i, i + 1, 1] for i in range(99)] + [[0, 99, 5000]], 0, 99, 0])
_tests.append([100, [[i, i + 1, 1] for i in range(99)] + [[0, 99, 5000]], 0, 99, 97])
_tests.append([100, [[i, i + 1, 1] for i in range(99)] + [[0, 99, 5000]], 0, 99, 98])
_tests.append([100, [[u, v, _r.randint(1, 10000)] for u, v in _dpairs(_r, 100, 3000)], 0, 99, 3])
_tests.append([100, [[u, v, _r.randint(1, 10000)] for u, v in _dpairs(_r, 100, 3000)], 5, 77, 99])
_tests.append([100, [[u, v, _r.randint(1, 50)] for u, v in _dpairs(_r, 100, 400) if v != 42], 3, 42, 99])
_tests.append([60, [[u, v, _r.randint(1, 100)] for u, v in _dpairs(_r, 60, 1500)], 10, 11, 1])

add(
    id="cheapest-flights-within-k-stops", title="Cheapest Flights Within K Stops", diff="Medium", topic="Graphs",
    fn="findCheapestPrice", params=[("n", "int"), ("flights", "int[][]"), ("src", "int"), ("dst", "int"), ("k", "int")], ret="int", cmp="exact",
    desc="<p>There are <code>n</code> cities labelled <code>0</code> to <code>n - 1</code>. Each entry <code>flights[i] = [from, to, price]</code> is a one-way flight that costs <code>price</code>.</p><p>Find the lowest total price of a trip from city <code>src</code> to city <code>dst</code> that makes <em>at most</em> <code>k</code> stops, where a stop is an intermediate city between two flights (so a trip with <code>k</code> stops uses at most <code>k + 1</code> flights). Cities may be visited more than once, although with positive prices that never helps. Return <code>-1</code> if no such trip exists.</p>",
    constraints=["2 &le; n &le; 100", "0 &le; flights.length &le; 3,000", "0 &le; from, to, src, dst &lt; n, from &ne; to and src &ne; dst", "1 &le; price &le; 10,000", "0 &le; k &lt; n", "Each ordered pair (from, to) appears at most once"],
    hints=["The cheapest route overall may use too many flights, so ordinary Dijkstra on price alone can pick a path that breaks the limit.",
           "Track the number of flights used as part of the state: let <code>best[j][v]</code> be the cheapest price to reach v with at most j flights.",
           "Bellman-Ford with exactly <code>k + 1</code> rounds does this. In each round, relax every flight using the distances from the <em>previous</em> round (work on a copy) so a round adds at most one flight."],
    editorial=["Add a second dimension to the shortest path problem: the number of flights used. Bellman-Ford does exactly that. Keep an array <code>dist</code> with <code>dist[src] = 0</code> and everything else infinite. Repeat <code>k + 1</code> times: copy <code>dist</code> to <code>nxt</code>, and for each flight <code>(u, v, w)</code> set <code>nxt[v] = min(nxt[v], dist[u] + w)</code>. After round j, <code>dist[v]</code> is the cheapest price using at most j flights. The copy is essential; relaxing in place could chain several flights within one round and ignore the stop limit.",
               "The answer is <code>dist[dst]</code> after the last round, or -1 if it is still infinite. The cost is O(k &middot; E). A BFS or Dijkstra over states (city, flights used) is an alternative with the same asymptotic flavour, as long as the state includes the flight count: pruning by city alone is wrong because a pricier arrival with fewer flights can still lead to the best total."],
    time="O(k &middot; E)", space="O(n)",
    solution='''def findCheapestPrice(n, flights, src, dst, k):
    INF = float('inf')
    dist = [INF] * n
    dist[src] = 0
    for _ in range(k + 1):
        nxt = dist[:]
        for u, v, w in flights:
            if dist[u] + w < nxt[v]:
                nxt[v] = dist[u] + w
        dist = nxt
    return -1 if dist[dst] == INF else dist[dst]
''',
    tests=_tests,
)


def b_flights(n, flights, src, dst, k):
    adj = [[] for _ in range(n)]
    for u, v, w in flights:
        adj[u].append((v, w))
    best = [None]

    def go(u, left, cost):
        if u == dst:
            if best[0] is None or cost < best[0]:
                best[0] = cost
        if left == 0:
            return
        for v, w in adj[u]:
            go(v, left - 1, cost + w)

    go(src, k + 1, 0)
    return -1 if best[0] is None else best[0]


def g_flights(r):
    n = r.randint(2, 6)
    src, dst = r.sample(range(n), 2)
    fl = [[u, v, r.randint(1, 9)] for u, v in _dpairs(r, n, r.randint(0, n * 2))]
    return [n, fl, src, dst, r.randint(0, n - 1)]


def v_flights(tests):
    for t in tests:
        n, fl, src, dst, k = t["args"]
        assert 2 <= n <= 100 and len(fl) <= 3000 and src != dst and 0 <= src < n and 0 <= dst < n and 0 <= k < n
        seen = set()
        for u, v, w in fl:
            assert 0 <= u < n and 0 <= v < n and u != v and 1 <= w <= 10000
            assert (u, v) not in seen
            seen.add((u, v))


CHECKS["cheapest-flights-within-k-stops"] = (b_flights, g_flights, "exact")
VALIDATE["cheapest-flights-within-k-stops"] = v_flights

# ---------------------------------------------------------------- path with minimum effort
_tests = [
    [[[1, 2, 2], [3, 8, 2], [5, 3, 5]]],
    [[[1, 2, 3], [3, 8, 4], [5, 3, 5]]],
    [[[1, 2, 1, 1, 1], [1, 2, 1, 2, 1], [1, 2, 1, 2, 1], [1, 2, 1, 2, 1], [1, 1, 1, 2, 1]]],
    [[[7]]],
    [[[1, 100]]],
    [[[5], [1], [9]]],
    [[[10, 1], [1, 10]]],
    [[[1, 1000000], [1, 1]]],
    [[[1, 10, 6, 7, 9, 10, 4, 9]]],
    [[[4, 3, 4, 10, 5, 5, 9, 2], [10, 8, 2, 10, 9, 7, 5, 6], [5, 8, 10, 10, 10, 7, 4, 2], [5, 1, 3, 1, 1, 3, 1, 9], [6, 4, 10, 6, 10, 9, 4, 6]]],
]
_r = rnd(7106)
_tests.append([[[_r.randint(1, 1000000) for _ in range(100)] for _ in range(100)]])
_tests.append([[[_r.randint(1, 20) for _ in range(100)] for _ in range(100)]])
_tests.append([[[1 + 3 * (i + j) + _r.randint(0, 2) for j in range(100)] for i in range(100)]])  # a smooth slope
_g = [[1000000 if (i % 2 == 1 and not ((i // 2) % 2 == 0 and j == 99) and not ((i // 2) % 2 == 1 and j == 0)) else 1 + (j % 2)
       for j in range(100)] for i in range(100)]  # serpentine corridor
_tests.append([_g])
_tests.append([[[_r.randint(1, 1000000)] for _ in range(100)]])
_tests.append([[[_r.randint(1, 1000000) for _ in range(100)]]])
_tests.append([[[(i * 37 + j * 91) % 1000003 + 1 for j in range(60)] for i in range(80)]])

add(
    id="path-with-minimum-effort", title="Path With Minimum Effort", diff="Medium", topic="Graphs",
    fn="minimumEffortPath", params=[("heights", "int[][]")], ret="int", cmp="exact",
    desc="<p>A hiker studies a rectangular map where <code>heights[r][c]</code> is the altitude of cell <code>(r, c)</code>. The hiker starts at the top-left cell <code>(0, 0)</code> and wants to reach the bottom-right cell, moving one step at a time up, down, left or right.</p><p>The <em>effort</em> of a route is the largest absolute difference in altitude between two consecutive cells on it, not the total. Return the smallest effort among all routes from the top-left cell to the bottom-right cell. If both cells are the same cell, the effort is <code>0</code>.</p>",
    constraints=["1 &le; rows, cols &le; 100", "1 &le; heights[r][c] &le; 1,000,000", "All rows have the same length"],
    hints=["Walking cheaply is not the goal. What counts for a route is its single worst step, so you want to minimise a maximum, not a sum.",
           "Either guess an effort limit <code>x</code> and check whether the goal is reachable using only steps of difference at most <code>x</code> (the limit is monotone, so binary search works), or tweak Dijkstra's algorithm.",
           "In Dijkstra, let the cost of reaching a cell be the minimum possible effort of any route to it. Moving to a neighbour gives <code>max(cost_here, |height difference|)</code>; keep the usual min-heap and relax when that value improves."],
    editorial=["This is a shortest path problem with a different way of combining edge weights: the cost of a route is the maximum of its edge weights (a <em>bottleneck</em> path). Dijkstra's algorithm still works because extending a route can never lower its cost. Store the best known effort per cell, start with 0 at the top-left, and always pop the cell with the smallest effort. For each neighbour compute <code>max(effort, |h[a] - h[b]|)</code> and push it if it beats the neighbour's best. The first time the bottom-right cell is popped, its effort is optimal. The cost is O(R &middot; C &middot; log(R &middot; C)).",
               "Alternatives: binary search on the effort limit with a BFS feasibility test costs O(R &middot; C &middot; log(max height)); or sort all adjacent-cell edges by difference and add them with union-find until the two corners become connected. They all return the same value."],
    time="O(RC log(RC))", space="O(RC)",
    solution='''import heapq


def minimumEffortPath(heights):
    R, C = len(heights), len(heights[0])
    INF = float('inf')
    best = [[INF] * C for _ in range(R)]
    best[0][0] = 0
    heap = [(0, 0, 0)]
    while heap:
        d, r, c = heapq.heappop(heap)
        if d > best[r][c]:
            continue
        if r == R - 1 and c == C - 1:
            return d
        for nr, nc in ((r + 1, c), (r - 1, c), (r, c + 1), (r, c - 1)):
            if 0 <= nr < R and 0 <= nc < C:
                nd = max(d, abs(heights[nr][nc] - heights[r][c]))
                if nd < best[nr][nc]:
                    best[nr][nc] = nd
                    heapq.heappush(heap, (nd, nr, nc))
    return 0
''',
    tests=_tests,
)


def b_effort(h):
    R, C = len(h), len(h[0])
    best = [None]
    seen = [[False] * C for _ in range(R)]

    def go(r, c, worst):
        if best[0] is not None and worst >= best[0]:
            return
        if r == R - 1 and c == C - 1:
            best[0] = worst
            return
        seen[r][c] = True
        for nr, nc in ((r + 1, c), (r - 1, c), (r, c + 1), (r, c - 1)):
            if 0 <= nr < R and 0 <= nc < C and not seen[nr][nc]:
                go(nr, nc, max(worst, abs(h[nr][nc] - h[r][c])))
        seen[r][c] = False

    go(0, 0, 0)
    return best[0]


def g_effort(r):
    R, C = r.randint(1, 3), r.randint(1, 4)
    hi = r.choice([3, 9, 30])
    return [[[r.randint(1, hi) for _ in range(C)] for _ in range(R)]]


def v_effort(tests):
    for t in tests:
        h = t["args"][0]
        assert 1 <= len(h) <= 100 and 1 <= len(h[0]) <= 100
        assert all(len(row) == len(h[0]) for row in h)
        assert all(1 <= x <= 1000000 for row in h for x in row)


CHECKS["path-with-minimum-effort"] = (b_effort, g_effort, "exact")
VALIDATE["path-with-minimum-effort"] = v_effort

# ---------------------------------------------------------------- min cost to connect all points
_tests = [
    [[[0, 0], [2, 2], [3, 10], [5, 2], [7, 0]]],
    [[[3, 12], [-2, 5], [-4, 1]]],
    [[[0, 0]]],
    [[[0, 0], [0, 0]]],
    [[[1, 1], [-1, -1]]],
    [[[0, 0], [1, 1], [1, 0], [-1, 1]]],
    [[[5, 5], [5, 5], [5, 5]]],
    [[[-1000000, -1000000], [1000000, 1000000]]],
    [[[-1000000, 1000000], [1000000, -1000000], [0, 0]]],
    [[[0, 0], [10, 0], [20, 0], [30, 0], [1, 7], [29, 7]]],
]
_r = rnd(7107)
_tests.append([[[_r.randint(-1000000, 1000000), _r.randint(-1000000, 1000000)] for _ in range(500)]])
_tests.append([[[_r.randint(-50, 50), _r.randint(-50, 50)] for _ in range(500)]])  # many near-ties and duplicates
_tests.append([[[(i % 25) * 3, (i // 25) * 3] for i in range(500)]])  # a lattice
_tests.append([[[i * 2000 - 500000, 0] for i in range(500)]])  # a line
_tests.append([[[(1000000 if i % 2 else -1000000), (1000000 if (i // 2) % 2 else -1000000)] for i in range(500)]])  # four far corners
_tests.append([[[_r.choice([-1, 1]) * (1000000 - _r.randint(0, 3)), _r.choice([-1, 1]) * (1000000 - _r.randint(0, 3))] for _ in range(300)]])
_tests.append([[[7, 7]] * 400])

add(
    id="min-cost-to-connect-all-points", title="Min Cost to Connect All Points", diff="Medium", topic="Graphs",
    fn="minCostConnectPoints", params=[("points", "int[][]")], ret="int", cmp="exact",
    desc="<p>You are given <code>points</code>, where <code>points[i] = [x, y]</code> is a location on a plane. Laying a cable between two points costs the Manhattan distance <code>|x1 - x2| + |y1 - y2|</code>.</p><p>Connect all the points using cables so that there is exactly one route between every pair of points (no cycles, no isolated groups). Return the minimum total cost. Several points may sit at the same location, and joining those costs <code>0</code>.</p>",
    constraints=["1 &le; points.length &le; 500", "-1,000,000 &le; x, y &le; 1,000,000", "Points are not necessarily distinct"],
    hints=["Every pair of points is a possible edge, so you are looking for a minimum spanning tree of a complete graph with n(n-1)/2 edges.",
           "Kruskal's algorithm sorts all pairs and joins components with union-find. For a complete graph there is a better way: Prim's algorithm that grows one tree.",
           "Keep <code>d[v]</code>, the cheapest cable from v to the tree so far. Repeatedly add the outside point with the smallest <code>d</code>, then update <code>d</code> for the remaining points using distances to the point you just added. That needs no edge list and no heap: O(n&sup2;)."],
    editorial=["Minimum spanning tree on a complete graph. Prim's algorithm starts with an arbitrary point (index 0) in the tree. For every other point it remembers the cheapest cable that attaches it to the tree. Each round it scans for the outside point with the smallest such cost, adds it, adds that cost to the answer, and then lowers the stored costs of the remaining points if the newly added point is closer to them. After n rounds the tree spans everything. The loops are O(n&sup2;) with only two arrays of memory, which beats Kruskal's O(n&sup2; log n) on 250,000 candidate edges.",
               "Kruskal works too: build all pair edges, sort by cost and union the endpoints, stopping after n - 1 successful unions. The answer fits easily in 32 bits here, since the tree has at most 499 cables and no cable costs more than 4,000,000."],
    time="O(n&sup2;)", space="O(n)",
    solution='''def minCostConnectPoints(points):
    n = len(points)
    INF = float('inf')
    d = [INF] * n
    d[0] = 0
    used = [False] * n
    total = 0
    for _ in range(n):
        u = -1
        for i in range(n):
            if not used[i] and (u == -1 or d[i] < d[u]):
                u = i
        used[u] = True
        total += d[u]
        ux, uy = points[u]
        for v in range(n):
            if not used[v]:
                w = abs(ux - points[v][0]) + abs(uy - points[v][1])
                if w < d[v]:
                    d[v] = w
    return total
''',
    tests=_tests,
)


def b_mst_points(points):
    n = len(points)
    if n == 1:
        return 0

    def dist(a, b):
        return abs(points[a][0] - points[b][0]) + abs(points[a][1] - points[b][1])

    if n == 2:
        return dist(0, 1)
    best = None
    for seq in product(range(n), repeat=n - 2):  # every labelled tree via its Pruefer sequence
        deg = [1] * n
        for x in seq:
            deg[x] += 1
        cost = 0
        for x in seq:
            leaf = min(i for i in range(n) if deg[i] == 1)
            cost += dist(leaf, x)
            deg[leaf] -= 1
            deg[x] -= 1
        last = [i for i in range(n) if deg[i] == 1]
        cost += dist(last[0], last[1])
        if best is None or cost < best:
            best = cost
    return best


def g_mst_points(r):
    n = r.randint(1, 6)
    hi = r.choice([2, 6, 20])
    return [[[r.randint(-hi, hi), r.randint(-hi, hi)] for _ in range(n)]]


def v_mst_points(tests):
    for t in tests:
        pts = t["args"][0]
        assert 1 <= len(pts) <= 500
        assert all(len(p_) == 2 and abs(p_[0]) <= 1000000 and abs(p_[1]) <= 1000000 for p_ in pts)


CHECKS["min-cost-to-connect-all-points"] = (b_mst_points, g_mst_points, "exact")
VALIDATE["min-cost-to-connect-all-points"] = v_mst_points

# ---------------------------------------------------------------- number of ways to arrive at destination
_tests = [
    [7, [[0, 6, 7], [0, 1, 2], [1, 2, 3], [1, 3, 3], [6, 3, 3], [3, 5, 1], [6, 5, 1], [2, 5, 1], [0, 4, 5], [4, 6, 2]]],
    [2, [[1, 0, 10]]],
    [1, []],
    [3, [[0, 1, 1], [1, 2, 1], [0, 2, 2]]],
    [3, [[0, 1, 1], [1, 2, 1], [0, 2, 3]]],
    [4, [[0, 1, 1], [0, 2, 1], [1, 3, 1], [2, 3, 1]]],
    [5, [[0, 1, 2], [1, 2, 2], [2, 4, 2], [0, 3, 3], [3, 4, 3], [1, 3, 1]]],
    [4, [[0, 3, 1000000000], [0, 2, 500000000], [2, 3, 500000000], [0, 1, 500000000], [1, 3, 500000000], [1, 2, 1000000000]]],
]
_r = rnd(7108)


def _diamonds(k):
    """k diamonds in a row: 3k + 1 nodes, 2**k shortest paths from 0 to n-1 (all edges weight 1)."""
    n = 3 * k + 1
    e = []
    for i in range(k):
        a, b, c, d = 3 * i, 3 * i + 1, 3 * i + 2, 3 * i + 3
        e += [[a, b, 1], [a, c, 1], [b, d, 1], [c, d, 1]]
    return n, e


def _conn_weighted(r, n, m, lo, hi):
    return [[u, v, r.randint(lo, hi)] for u, v in _pairs(r, n, m, connected=True)]


def _relabel_ends(r, n, edges):
    """Swap labels so that the first node of the structure is 0 and the last is n-1 (already so) but shuffle the middle."""
    mid = list(range(1, n - 1))
    shuffled = mid[:]
    r.shuffle(shuffled)
    mp = {0: 0, n - 1: n - 1}
    mp.update(dict(zip(mid, shuffled)))
    out = [[mp[u], mp[v], w] for u, v, w in edges]
    r.shuffle(out)
    return out


_n, _e = _diamonds(99)
_tests.append([_n, _relabel_ends(_r, _n, _e)])
_n, _e = _diamonds(33)
_tests.append([_n, _relabel_ends(_r, _n, _e)])
_tests.append([300, _conn_weighted(_r, 300, 2000, 1, 3)])
_tests.append([300, _conn_weighted(_r, 300, 700, 1, 1)])
_tests.append([250, _conn_weighted(_r, 250, 1500, 1, 1000000000)])
_tests.append([200, _conn_weighted(_r, 200, 600, 5, 6)])
_tests.append([300, [[i, i + 1, 1] for i in range(299)]])

add(
    id="number-of-ways-to-arrive-at-destination", title="Number of Ways to Arrive at Destination", diff="Medium", topic="Graphs",
    fn="countPaths", params=[("n", "int"), ("roads", "int[][]")], ret="int", cmp="exact",
    desc="<p>A city has <code>n</code> intersections labelled <code>0</code> to <code>n - 1</code>. Each entry <code>roads[i] = [a, b, t]</code> is a two-way road between intersections <code>a</code> and <code>b</code> that takes <code>t</code> minutes to drive. Any intersection can be reached from any other, and at most one road joins a given pair.</p><p>Count the routes that take the <em>minimum possible total time</em> to get from intersection <code>0</code> to intersection <code>n - 1</code>. Return the count modulo <code>1,000,000,007</code>. If <code>n == 1</code>, the answer is <code>1</code>.</p>",
    constraints=["1 &le; n &le; 300", "n - 1 &le; roads.length &le; 2,000", "0 &le; a, b &lt; n, a &ne; b, and no pair of intersections has two roads", "1 &le; t &le; 1,000,000,000", "The road network is connected"],
    hints=["First work out the shortest time to every intersection. Then ask: how many different shortest routes end at each one?",
           "A route to v is shortest when it arrives from some u with <code>dist[u] + t(u, v) == dist[v]</code>, and its first part must itself be a shortest route to u.",
           "Extend Dijkstra with a <code>ways</code> array. On a strictly better distance, copy <code>ways[u]</code> into <code>ways[v]</code>; on an equal distance, add <code>ways[u]</code> to <code>ways[v]</code> (modulo 1,000,000,007). Positive weights mean <code>ways[u]</code> is final when u is popped."],
    editorial=["Run Dijkstra from intersection 0 while also counting routes. Set <code>dist[0] = 0</code> and <code>ways[0] = 1</code>. When a popped node u relaxes an edge to v with candidate distance <code>nd = dist[u] + t</code>: if <code>nd &lt; dist[v]</code> we have found a strictly shorter way in, so set <code>dist[v] = nd</code>, set <code>ways[v] = ways[u]</code> and push v; if <code>nd == dist[v]</code> we have found another equally short way in, so add <code>ways[u]</code> to <code>ways[v]</code>.",
               "This is correct because every time is at least 1: all predecessors of u on a shortest route are strictly closer to the source and have been popped before u, so <code>ways[u]</code> is already complete when it is used. Skip stale heap entries (popped distance larger than <code>dist[u]</code>) so nothing is counted twice. The answer is <code>ways[n - 1]</code> modulo 1,000,000,007; the number of shortest routes can be as large as 2<sup>100</sup> or more, which is why the modulus is needed. Distances reach about 3 &middot; 10<sup>11</sup>, which Python handles natively and a 32-bit int would not, so use 64-bit integers if you port this."],
    time="O((V + E) log V)", space="O(V + E)",
    solution='''import heapq


def countPaths(n, roads):
    MOD = 1000000007
    adj = [[] for _ in range(n)]
    for a, b, t in roads:
        adj[a].append((b, t))
        adj[b].append((a, t))
    INF = float('inf')
    dist = [INF] * n
    ways = [0] * n
    dist[0] = 0
    ways[0] = 1
    heap = [(0, 0)]
    while heap:
        d, u = heapq.heappop(heap)
        if d > dist[u]:
            continue
        for v, t in adj[u]:
            nd = d + t
            if nd < dist[v]:
                dist[v] = nd
                ways[v] = ways[u]
                heapq.heappush(heap, (nd, v))
            elif nd == dist[v]:
                ways[v] = (ways[v] + ways[u]) % MOD
    return ways[n - 1] % MOD
''',
    tests=_tests,
)


def b_ways(n, roads):
    adj = [[] for _ in range(n)]
    for a, b, t in roads:
        adj[a].append((b, t))
        adj[b].append((a, t))
    lens = []
    seen = [False] * n

    def go(u, total):
        if u == n - 1:
            lens.append(total)
            return
        seen[u] = True
        for v, t in adj[u]:
            if not seen[v]:
                go(v, total + t)
        seen[u] = False

    go(0, 0)
    m = min(lens)
    return lens.count(m) % MOD


def g_ways(r):
    n = r.randint(1, 7)
    if n == 1:
        return [1, []]
    return [n, _conn_weighted(r, n, r.randint(n - 1, n + 4), 1, r.choice([1, 2, 4]))]


def v_ways(tests):
    for t in tests:
        n, roads = t["args"]
        assert 1 <= n <= 300 and n - 1 <= len(roads) <= 2000
        parent = list(range(n))

        def find(x):
            while parent[x] != x:
                parent[x] = parent[parent[x]]
                x = parent[x]
            return x

        for a, b, w in roads:
            assert 0 <= a < n and 0 <= b < n and a != b and 1 <= w <= 1000000000
            parent[find(a)] = find(b)
        _unordered_distinct(roads)
        assert len({find(i) for i in range(n)}) == 1, "graph not connected"


CHECKS["number-of-ways-to-arrive-at-destination"] = (b_ways, g_ways, "exact")
VALIDATE["number-of-ways-to-arrive-at-destination"] = v_ways

# ====================================================================== HARD
# ---------------------------------------------------------------- alien dictionary (integer letters)
_tests = [
    [4, [[3, 2], [2, 1, 0], [1, 1], [1, 0, 0]]],
    [3, [[0], [1], [2]]],
    [3, [[2], [1], [0]]],
    [3, [[0], [1], [0]]],
    [2, [[1, 0], [1]]],
    [1, [[0], [0, 0]]],
    [1, [[0]]],
    [5, [[4]]],
    [5, [[1, 2], [1, 3], [4, 3], [4, 0]]],
    [4, [[2, 0], [2, 0], [2, 0, 1], [3]]],
    [4, [[0, 1], [1, 0], [0, 0]]],
    [6, [[5], [3, 3], [3, 2], [1, 4], [1, 4, 0]]],
    [3, [[1, 2, 0], [1, 2], [0]]],
]
_r = rnd(7109)


def _alien_valid(r, m, count, maxlen, hidden=None):
    order = hidden if hidden is not None else r.sample(range(m), m)
    rank = {c: i for i, c in enumerate(order)}
    words = [[r.randrange(m) for _ in range(r.randint(1, maxlen))] for _ in range(count)]
    words.sort(key=lambda w: [rank[c] for c in w])
    return words


_tests.append([100, _alien_valid(_r, 100, 500, 20)])
_tests.append([100, _alien_valid(_r, 100, 500, 3)])
_tests.append([26, _alien_valid(_r, 26, 500, 6)])
_hid = _r.sample(range(100), 100)
_tests.append([100, [[c] for c in _hid]])  # a single letter per word forces the whole order
_tests.append([100, [[c] for c in _hid] + [[_hid[0]]]])  # ... and then the first letter appears again: a cycle
_w = _alien_valid(_r, 60, 500, 8)
_w[250], _w[251] = _w[251][:], _w[250][:]
_tests.append([60, _w])
_tests.append([200, _alien_valid(_r, 200, 300, 2)])
_tests.append([100, [[7] * 20, [7] * 19]])

add(
    id="alien-dictionary-integer-order", title="Alien Dictionary Order", diff="Hard", topic="Graphs",
    fn="alienOrder", params=[("m", "int"), ("words", "int[][]")], ret="int[]", cmp="exact",
    desc="<p>An alien language uses an alphabet of <code>m</code> letters, written here as the integers <code>0</code> to <code>m - 1</code>. The alien order of the letters is unknown. A dictionary of words (each word is an array of letters) is known to be listed in <em>lexicographic order under that unknown alphabet order</em>: comparing two words, look at the first position where they differ, and the word with the letter that comes earlier in the alien alphabet is the smaller one. If one word is a prefix of the other, the shorter word is smaller. Equal words may appear next to each other.</p><p>Return an ordering of all <code>m</code> letters (every letter from <code>0</code> to <code>m - 1</code> exactly once) that is consistent with the dictionary. Letters the dictionary says nothing about must still appear. Because many orderings may be consistent, return the <em>lexicographically smallest</em> one when the orderings are compared as integer arrays. If the dictionary is contradictory, return an empty array.</p>",
    constraints=["1 &le; m &le; 200", "1 &le; words.length &le; 500", "1 &le; words[i].length &le; 20", "0 &le; words[i][j] &lt; m"],
    hints=["Only neighbouring words need comparing, and each such pair tells you at most one fact: the first differing letters give 'a comes before b'.",
           "Those facts are edges of a directed graph on the letters, and an ordering that respects all of them is a topological order. Watch for the prefix trap: a longer word directly before its own prefix is impossible no matter what the alphabet is.",
           "To get the smallest valid order, run Kahn's algorithm with a min-heap of the letters whose in-degree is zero instead of a plain queue. If fewer than m letters come out, there is a cycle: return an empty array."],
    editorial=["Compare each adjacent pair of words. Scan to the first differing position; if there is one, add an edge <code>a &rarr; b</code> from the letter in the earlier word to the letter in the later one (once per distinct pair; duplicates would double-count the in-degree). If there is none, the words are equal up to the shorter length: that is fine when the first is the shorter or the same length, but when the first word is longer, it would have to sort after its own prefix, so the dictionary is invalid and the answer is empty.",
               "Now any valid alphabet is a topological order of the graph over all m letters, including those with no edges at all. A plain topological sort could return any of them; the lexicographically smallest is produced by always taking the smallest available letter. Use a min-heap holding every letter whose in-degree has dropped to 0: pop the smallest, append it, and release its out-edges. Picking the smallest ready letter at each step is optimal because each choice only delays larger letters, never blocks smaller ones. If the output has fewer than m letters a cycle exists (for example 0, 1, 0 as three words) and the answer is []. Cost: O(L + m log m + E) where L is the total number of letters in the comparisons."],
    time="O(L + m log m)", space="O(m + E)",
    solution='''import heapq


def alienOrder(m, words):
    adj = [set() for _ in range(m)]
    indeg = [0] * m
    for a, b in zip(words, words[1:]):
        k = 0
        lim = min(len(a), len(b))
        while k < lim and a[k] == b[k]:
            k += 1
        if k == lim:
            if len(a) > len(b):
                return []
            continue
        if b[k] not in adj[a[k]]:
            adj[a[k]].add(b[k])
            indeg[b[k]] += 1
    heap = [c for c in range(m) if indeg[c] == 0]
    heapq.heapify(heap)
    order = []
    while heap:
        c = heapq.heappop(heap)
        order.append(c)
        for d in adj[c]:
            indeg[d] -= 1
            if indeg[d] == 0:
                heapq.heappush(heap, d)
    return order if len(order) == m else []
''',
    tests=_tests,
)


def b_alien(m, words):
    for perm in permutations(range(m)):  # permutations come out in increasing lexicographic order
        rank = {c: i for i, c in enumerate(perm)}
        keys = [[rank[c] for c in w] for w in words]
        if all(keys[i] <= keys[i + 1] for i in range(len(keys) - 1)):
            return list(perm)
    return []


def g_alien(r):
    m = r.randint(1, 6)
    cnt = r.randint(1, 6)
    ml = r.randint(1, 4)
    if r.random() < 0.6:
        words = _alien_valid(r, m, cnt, ml)
    else:
        words = [[r.randrange(m) for _ in range(r.randint(1, ml))] for _ in range(cnt)]
    return [m, words]


def v_alien(tests):
    for t in tests:
        m, words = t["args"]
        assert 1 <= m <= 200 and 1 <= len(words) <= 500
        for w in words:
            assert 1 <= len(w) <= 20 and all(0 <= c < m for c in w)
        out = t["expected"]
        assert out == [] or sorted(out) == list(range(m))


CHECKS["alien-dictionary-integer-order"] = (b_alien, g_alien, "exact")
VALIDATE["alien-dictionary-integer-order"] = v_alien

# ---------------------------------------------------------------- critical / pseudo-critical MST edges
_tests = [
    [5, [[0, 1, 1], [1, 2, 1], [2, 3, 2], [0, 3, 2], [0, 4, 3], [3, 4, 3], [1, 4, 6]]],
    [4, [[0, 1, 1], [1, 2, 1], [2, 3, 1], [0, 3, 1]]],
    [3, [[0, 1, 5], [1, 2, 5], [0, 2, 5]]],
    [2, [[0, 1, 9]]],
    [4, [[0, 1, 2], [1, 2, 3], [2, 3, 4]]],
    [4, [[0, 1, 1], [1, 2, 1], [0, 2, 1], [2, 3, 7]]],
    [4, [[0, 1, 1], [1, 2, 1], [2, 3, 1], [3, 0, 1], [0, 2, 10]]],
    [5, [[0, 1, 1], [1, 2, 1], [0, 2, 1], [2, 3, 2], [3, 4, 2], [2, 4, 2]]],
    [6, [[0, 1, 3], [1, 2, 4], [2, 3, 5], [3, 4, 6], [4, 5, 7], [5, 0, 8], [0, 3, 9], [1, 4, 2]]],
    [4, [[3, 2, 4], [2, 1, 4], [1, 0, 4], [3, 0, 4], [1, 3, 4], [0, 2, 4]]],
]
_r = rnd(7110)


def _mst_graph(r, n, m, lo, hi):
    return [[u, v, r.randint(lo, hi)] for u, v in _pairs(r, n, m, connected=True)]


_tests.append([100, _mst_graph(_r, 100, 200, 1, 4)])
_tests.append([100, _mst_graph(_r, 100, 200, 1, 1000)])
_tests.append([100, _mst_graph(_r, 100, 99, 1, 10)])
_tests.append([20, [[u, v, 7] for u in range(20) for v in range(u + 1, 20)]])
_tests.append([100, _mst_graph(_r, 100, 150, 1, 2)])
_tests.append([60, _mst_graph(_r, 60, 200, 1, 3)])
_tests.append([100, [[i, i + 1, 5] for i in range(99)] + [[i, i + 2, 5] for i in range(0, 98, 2)] + [[0, 99, 1000]]])

add(
    id="mst-critical-and-pseudo-critical-edges", title="Critical and Pseudo-Critical Edges of an MST", diff="Hard", topic="Graphs",
    fn="classifyMstEdges", params=[("n", "int"), ("edges", "int[][]")], ret="int[]", cmp="exact",
    desc="<p>A connected, weighted, undirected graph has <code>n</code> nodes labelled <code>0</code> to <code>n - 1</code>. Each entry <code>edges[i] = [a, b, w]</code> joins nodes <code>a</code> and <code>b</code> with weight <code>w</code>. A <em>minimum spanning tree</em> (MST) is a set of <code>n - 1</code> edges that connects all nodes and has the smallest possible total weight. Several different MSTs may exist when weights tie.</p><p>Classify every edge by its role across <em>all</em> minimum spanning trees:</p><ul><li><code>2</code> &mdash; <em>critical</em>: it belongs to every MST (removing it makes the cheapest spanning tree heavier, or impossible).</li><li><code>1</code> &mdash; <em>pseudo-critical</em>: it belongs to at least one MST but not to all of them.</li><li><code>0</code> &mdash; it belongs to no MST at all.</li></ul><p>Return an array <code>res</code> of length <code>edges.length</code> where <code>res[i]</code> is the class of <code>edges[i]</code>.</p>",
    constraints=["2 &le; n &le; 100", "n - 1 &le; edges.length &le; min(200, n(n-1)/2)", "0 &le; a, b &lt; n, a &ne; b, and each pair of nodes is joined by at most one edge", "1 &le; w &le; 1,000", "The graph is connected"],
    hints=["Start by finding the weight W of an MST (Kruskal's algorithm). All MSTs share that weight, so you can test each edge by comparing against W.",
           "An edge is critical if the best spanning tree that is forbidden from using it is heavier than W (or cannot exist at all).",
           "If an edge is not critical, force it in: start the union-find with that edge already joined, run Kruskal on the rest, and compare. If the total is still W, some MST contains it (pseudo-critical); otherwise it is in none."],
    editorial=["Compute <code>W</code>, the weight of an MST, with Kruskal's algorithm: sort the edges by weight and join components with union-find. Then examine each edge i separately, using the same routine with two options. <em>Excluding</em> edge i: skip it during Kruskal. If the tree is heavier than W or fails to connect all nodes, every MST must use edge i, so it is critical (2).",
               "Otherwise some MST avoids edge i. <em>Forcing</em> edge i: union its endpoints first, add its weight, then run Kruskal over the other edges. If the total equals W, then there is an MST that contains edge i and one that does not, so it is pseudo-critical (1). If the forced tree is heavier than W, edge i is in no MST (0). Each test is one Kruskal pass over the sorted edges, so the whole algorithm is O(E &middot; E &middot; &alpha;(n)), about 80,000 steps for 200 edges.",
               "It is worth seeing why forcing is sound: Kruskal on the remaining edges, after the forced edge is merged, returns the cheapest spanning tree that contains that edge, by the same exchange argument that proves ordinary Kruskal optimal. And a graph where all weights tie shows the three classes clearly: every non-bridge edge is pseudo-critical, every bridge is critical."],
    time="O(E&sup2; &alpha;(n))", space="O(n + E)",
    solution='''def classifyMstEdges(n, edges):
    E = len(edges)
    order = sorted(range(E), key=lambda i: edges[i][2])
    INF = float('inf')

    def kruskal(skip, force):
        parent = list(range(n))

        def find(x):
            while parent[x] != x:
                parent[x] = parent[parent[x]]
                x = parent[x]
            return x

        total = 0
        used = 0
        if force >= 0:
            a, b, w = edges[force]
            parent[find(a)] = find(b)
            total += w
            used += 1
        for i in order:
            if i == skip or i == force:
                continue
            a, b, w = edges[i]
            ra, rb = find(a), find(b)
            if ra != rb:
                parent[ra] = rb
                total += w
                used += 1
        return total if used == n - 1 else INF

    best = kruskal(-1, -1)
    res = []
    for i in range(E):
        if kruskal(i, -1) > best:
            res.append(2)
        elif kruskal(-1, i) == best:
            res.append(1)
        else:
            res.append(0)
    return res
''',
    tests=_tests,
)


def b_mst_edges(n, edges):
    E = len(edges)
    trees = []
    for combo in combinations(range(E), n - 1):
        parent = list(range(n))

        def find(x):
            while parent[x] != x:
                x = parent[x]
            return x

        ok = True
        for i in combo:
            ra, rb = find(edges[i][0]), find(edges[i][1])
            if ra == rb:
                ok = False
                break
            parent[ra] = rb
        if ok:
            trees.append((sum(edges[i][2] for i in combo), set(combo)))
    best = min(t[0] for t in trees)
    mins = [t[1] for t in trees if t[0] == best]
    res = []
    for i in range(E):
        c = sum(1 for s in mins if i in s)
        res.append(2 if c == len(mins) else (1 if c > 0 else 0))
    return res


def g_mst_edges(r):
    n = r.randint(2, 6)
    m = r.randint(n - 1, min(9, n * (n - 1) // 2))
    return [n, _mst_graph(r, n, m, 1, r.choice([1, 2, 3, 6]))]


def v_mst_edges(tests):
    for t in tests:
        n, edges = t["args"]
        assert 2 <= n <= 100 and n - 1 <= len(edges) <= min(200, n * (n - 1) // 2)
        parent = list(range(n))

        def find(x):
            while parent[x] != x:
                parent[x] = parent[parent[x]]
                x = parent[x]
            return x

        for a, b, w in edges:
            assert 0 <= a < n and 0 <= b < n and a != b and 1 <= w <= 1000
            parent[find(a)] = find(b)
        _unordered_distinct(edges)
        assert len({find(i) for i in range(n)}) == 1, "graph not connected"
        res = t["expected"]
        assert len(res) == len(edges) and all(x in (0, 1, 2) for x in res)
        assert res.count(2) + res.count(1) >= n - 1


CHECKS["mst-critical-and-pseudo-critical-edges"] = (b_mst_edges, g_mst_edges, "exact")
VALIDATE["mst-critical-and-pseudo-critical-edges"] = v_mst_edges
