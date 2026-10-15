"""Problems: Bellman-Ford, Floyd-Warshall and negative edges (graphs as edge lists)."""
import heapq
from fractions import Fraction

from lib import add, rnd, CHECKS, VALIDATE, gen_arr  # noqa: F401

NOPATH = 1000000000


# ------------------------------------------------------------------ shared helpers
def _upairs(r, n, m, connected=False):
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


def _dpairs(r, n, m, loops=False):
    """m distinct ordered pairs (u, v); u != v unless loops=True."""
    cap = n * n if loops else n * (n - 1)
    m = min(m, cap)
    s = set()
    while len(s) < m:
        u = r.randrange(n)
        v = r.randrange(n)
        if u == v and not loops:
            continue
        s.add((u, v))
    out = [list(x) for x in sorted(s)]
    r.shuffle(out)
    return out


def _pot_edges(r, n, m, pmax, cmax, loops=False):
    """Directed edges with possibly negative weights but no negative cycle at all:
    w(u, v) = c + p[v] - p[u] with c >= 0, so every cycle has weight sum(c) >= 0."""
    p = [r.randint(-pmax, pmax) for _ in range(n)]
    return [[u, v, r.randint(0, cmax) + p[v] - p[u]] for u, v in _dpairs(r, n, m, loops)]


def _dag_edges(r, n, m, wlo, whi):
    """Chain i -> i+1 plus random forward edges (u < v). Always acyclic, every node reachable from 0."""
    s = {(i, i + 1) for i in range(n - 1)}
    m = max(m, n - 1)
    m = min(m, n * (n - 1) // 2)
    while len(s) < m:
        u, v = sorted(r.sample(range(n), 2))
        s.add((u, v))
    return [[u, v, r.randint(wlo, whi)] for u, v in sorted(s)]


def _dag_dist(n, edges, a, b):
    """Shortest a -> b distance in a forward-only edge list (edges have u < v)."""
    INF = 10 ** 15
    d = [INF] * n
    d[a] = 0
    for u, v, w in sorted(edges):
        if d[u] < INF and d[u] + w < d[v]:
            d[v] = d[u] + w
    return d[b]


def _close(edges, n, a, b, slack):
    """Add edge b -> a so that the cycle a ~> b -> a has weight -slack (slack = 1: negative, 0: zero cycle)."""
    sp = _dag_dist(n, edges, a, b)
    assert sp < 10 ** 15
    return edges + [[b, a, -sp - slack]]


def _shuffled(r, edges):
    e = [list(x) for x in edges]
    r.shuffle(e)
    return e


def _simple_cycles(n, adj):
    """All simple directed cycles (self-loops included) as (set of nodes, weight sum, length). adj[u] = [(v, w)]."""
    out = []

    def dfs(s, u, seen, total, length):
        for v, w in adj[u]:
            if v == s:
                out.append((set(seen), total + w, length + 1))
            elif v > s and v not in seen:
                seen.add(v)
                dfs(s, v, seen, total + w, length + 1)
                seen.discard(v)

    for s in range(n):
        dfs(s, s, {s}, 0, 0)
    return out


def _adj(n, edges, undirected=False):
    adj = [[] for _ in range(n)]
    for u, v, w in edges:
        adj[u].append((v, w))
        if undirected:
            adj[v].append((u, w))
    return adj


def _reach(n, adj, s):
    seen = {s}
    st = [s]
    while st:
        u = st.pop()
        for v, _ in adj[u]:
            if v not in seen:
                seen.add(v)
                st.append(v)
    return seen


def _bf_dist(n, edges, s):
    """Plain repeated relaxation until nothing changes (graph without negative cycles)."""
    d = [None] * n
    d[s] = 0
    changed = True
    while changed:
        changed = False
        for u, v, w in edges:
            if d[u] is not None and (d[v] is None or d[u] + w < d[v]):
                d[v] = d[u] + w
                changed = True
    return d


def _connected_check(n, edges):
    adj = _adj(n, edges, True)
    return len(_reach(n, adj, 0)) == n


# ====================================================================== EASY
# ---------------------------------------------------------------- sum of all pairs distances
_tests = [
    [3, [[0, 1, 4], [1, 2, 3], [0, 2, 10]]],
    [4, [[0, 1, 1], [2, 3, 1]]],
    [1, []],
    [2, [[1, 0, 7]]],
    [2, []],
    [4, [[0, 1, 1], [1, 2, 1], [2, 3, 1], [3, 0, 1]]],
    [5, [[0, 1, 1], [0, 2, 1], [0, 3, 1], [0, 4, 1]]],
    [4, [[0, 1, 1000], [1, 2, 1000], [2, 3, 1000], [0, 3, 999], [0, 2, 1]]],
    [6, [[0, 1, 2], [1, 2, 2], [3, 4, 2], [4, 5, 2], [2, 3, 1]]],
    [5, [[0, 1, 5], [1, 2, 5], [3, 4, 5], [0, 2, 1]]],
]
_r = rnd(8101)
_tests.append([80, [[i, i + 1, 1000] for i in range(79)]])
_tests.append([80, [[u, v, _r.randint(1, 1000)] for u, v in _upairs(_r, 80, 600, True)]])
_tests.append([75, [[u, v, _r.randint(1, 1000)] for u, v in _upairs(_r, 75, 74, True)]])
_tests.append([80, [[u, v, _r.randint(1, 1000)] for u, v in _upairs(_r, 80, 900)]])
_tests.append([60, [[u, v, _r.randint(1, 20)] for u, v in _upairs(_r, 60, 200, True)]])

add(
    id="sum-of-all-pairs-shortest-distances", title="Sum of All Pairs Shortest Distances", diff="Easy", topic="Graphs",
    fn="sumOfPairDistances", params=[("n", "int"), ("roads", "int[][]")], ret="int", cmp="exact",
    desc="<p>A region has <code>n</code> towns labelled <code>0</code> to <code>n - 1</code>. Each entry <code>roads[i] = [a, b, w]</code> is a two-way road between towns <code>a</code> and <code>b</code> of length <code>w</code>.</p><p>For every unordered pair of different towns <code>{i, j}</code>, take the length of the shortest route between them. Return the sum of these values over all <code>n(n - 1) / 2</code> pairs. If even one pair of towns cannot reach each other, return <code>-1</code>.</p><p>Example: with <code>n = 3</code> and roads <code>[[0,1,4],[1,2,3],[0,2,10]]</code> the shortest distances are <code>d(0,1) = 4</code>, <code>d(1,2) = 3</code> and <code>d(0,2) = 4 + 3 = 7</code> (going through town 1 beats the direct road of 10), so the answer is <code>14</code>.</p>",
    constraints=["1 &le; n &le; 80", "0 &le; roads.length &le; n(n - 1) / 2", "roads[i] = [a, b, w] with 0 &le; a, b &lt; n, a &ne; b and 1 &le; w &le; 1,000", "No two roads join the same pair of towns"],
    hints=["You need the distance between <em>every</em> pair of towns, not from a single source. With n up to 80, an O(n<sup>3</sup>) method is fine.",
           "Let <code>d[i][j]</code> be the best known distance from i to j. Start with direct roads (0 on the diagonal, infinity elsewhere), then ask for each town k: is going through k better?",
           "Floyd-Warshall: for k in 0..n-1, for all i, j, set <code>d[i][j] = min(d[i][j], d[i][k] + d[k][j])</code>. The outer loop must be over the intermediate town k. Afterwards add up <code>d[i][j]</code> for i &lt; j, or return -1 on the first infinity."],
    editorial=["Floyd-Warshall solves the all-pairs problem by dynamic programming over the set of allowed intermediate towns. After processing towns <code>0..k</code>, <code>d[i][j]</code> is the shortest distance from i to j using only those towns as stops in between. Allowing town k means a shortest route either avoids k (the old value) or passes through it once, splitting into i to k and k to j that only use earlier stops.",
               "The three loops give O(n<sup>3</sup>) time and O(n<sup>2</sup>) space, which is about half a million steps for n = 80. Running Dijkstra from every town costs O(n &middot; (E log n)) and is better on sparse graphs, but Floyd-Warshall is shorter to write and works unchanged when weights are negative. Sum the upper triangle only, because the graph is undirected and <code>d[i][j] = d[j][i]</code>. If any entry stays infinite the graph is disconnected and the answer is -1."],
    time="O(n<sup>3</sup>)", space="O(n<sup>2</sup>)",
    solution='''def sumOfPairDistances(n, roads):
    INF = 10 ** 15
    d = [[INF] * n for _ in range(n)]
    for i in range(n):
        d[i][i] = 0
    for a, b, w in roads:
        if w < d[a][b]:
            d[a][b] = d[b][a] = w
    for k in range(n):
        dk = d[k]
        for i in range(n):
            dik = d[i][k]
            if dik < INF:
                d[i] = [x if x <= dik + y else dik + y for x, y in zip(d[i], dk)]
    total = 0
    for i in range(n):
        for j in range(i + 1, n):
            if d[i][j] >= INF:
                return -1
            total += d[i][j]
    return total
''',
    tests=_tests,
)


def b_allpairs(n, roads):
    edges = [[a, b, w] for a, b, w in roads] + [[b, a, w] for a, b, w in roads]
    total = 0
    for s in range(n):
        d = _bf_dist(n, edges, s)
        for j in range(s + 1, n):
            if d[j] is None:
                return -1
            total += d[j]
    return total


def g_allpairs(r):
    n = r.randint(1, 7)
    m = r.randint(0, n * (n - 1) // 2) if n >= 2 else 0
    ps = _upairs(r, n, m, connected=r.random() < 0.6) if n >= 2 else []
    return [n, [[u, v, r.randint(1, 9)] for u, v in ps]]


def v_allpairs(tests):
    for t in tests:
        n, roads = t["args"]
        assert 1 <= n <= 80 and len(roads) <= n * (n - 1) // 2
        seen = set()
        for a, b, w in roads:
            assert 0 <= a < n and 0 <= b < n and a != b and 1 <= w <= 1000
            k = (min(a, b), max(a, b))
            assert k not in seen
            seen.add(k)


CHECKS["sum-of-all-pairs-shortest-distances"] = (b_allpairs, g_allpairs, "exact")
VALIDATE["sum-of-all-pairs-shortest-distances"] = v_allpairs

# ---------------------------------------------------------------- radius and diameter
_tests = [
    [4, [[0, 1, 2], [1, 2, 3], [2, 3, 4]]],
    [3, [[0, 1, 1], [1, 2, 1], [0, 2, 1]]],
    [1, []],
    [3, [[0, 1, 5]]],
    [2, [[0, 1, 9]]],
    [5, [[0, 1, 1], [0, 2, 1], [0, 3, 1], [0, 4, 1]]],
    [6, [[0, 1, 4], [1, 2, 4], [2, 3, 4], [3, 4, 4], [4, 5, 4], [5, 0, 4]]],
    [5, [[0, 1, 10], [1, 2, 1], [2, 3, 1], [3, 4, 10], [0, 4, 3]]],
    [4, [[0, 1, 1], [2, 3, 1]]],
    [7, [[0, 1, 3], [1, 2, 3], [2, 3, 3], [3, 4, 3], [4, 5, 3], [5, 6, 3], [0, 6, 20]]],
]
_r = rnd(8102)
_tests.append([80, [[i, i + 1, 1000] for i in range(79)]])
_tests.append([80, [[u, v, _r.randint(1, 1000)] for u, v in _upairs(_r, 80, 500, True)]])
_tests.append([70, [[u, v, _r.randint(1, 50)] for u, v in _upairs(_r, 70, 69, True)]])
_tests.append([80, [[u, v, _r.randint(1, 1000)] for u, v in _upairs(_r, 80, 79)]])

add(
    id="weighted-graph-radius-and-diameter", title="Weighted Graph Radius and Diameter", diff="Easy", topic="Graphs",
    fn="radiusAndDiameter", params=[("n", "int"), ("roads", "int[][]")], ret="int[]", cmp="exact", tier="extra",
    desc="<p>There are <code>n</code> junctions labelled <code>0</code> to <code>n - 1</code>. Each <code>roads[i] = [a, b, w]</code> is a two-way road of length <code>w</code>.</p><p>The <em>eccentricity</em> of a junction is the length of the shortest route to the junction that is farthest from it (measured by shortest route length). The <em>radius</em> of the network is the smallest eccentricity over all junctions, and the <em>diameter</em> is the largest one.</p><p>Return <code>[radius, diameter]</code>. If some junction cannot reach another, the eccentricities are undefined and you must return <code>[-1, -1]</code>. A network with a single junction has radius and diameter <code>0</code>.</p><p>Example: <code>n = 4</code>, roads <code>[[0,1,2],[1,2,3],[2,3,4]]</code> (a path). Eccentricities are 9, 7, 5, 9 (for example junction 2 is 5 away from junction 0, 3 from junction 1 and 4 from junction 3), so the answer is <code>[5, 9]</code>.</p>",
    constraints=["1 &le; n &le; 80", "0 &le; roads.length &le; n(n - 1) / 2", "roads[i] = [a, b, w] with 0 &le; a, b &lt; n, a &ne; b and 1 &le; w &le; 1,000", "No two roads join the same pair of junctions"],
    hints=["Eccentricity needs the shortest distance from a junction to all others. You need it for every junction.",
           "Compute all-pairs shortest distances with Floyd-Warshall (n is only 80). Then the eccentricity of i is the maximum of row i.",
           "If any entry of the matrix is still infinite, return [-1, -1]. Otherwise radius = min over rows of the row maximum, and diameter = max over rows of the row maximum (equivalently the largest entry in the whole matrix)."],
    editorial=["Build the shortest-distance matrix with Floyd-Warshall in O(n<sup>3</sup>). Row i of that matrix lists the distances from junction i, so its largest value is the eccentricity of i. The radius is the smallest of these row maxima and the diameter is the largest.",
               "Disconnected networks are detected for free: some matrix entry is never improved from infinity. Note that the diameter is the length of the longest shortest route, not the longest simple path. Repeated Dijkstra also works in O(n &middot; E log n); on a tree each eccentricity can even be found with two BFS passes, but the general weighted case needs one of the all-pairs approaches."],
    time="O(n<sup>3</sup>)", space="O(n<sup>2</sup>)",
    solution='''def radiusAndDiameter(n, roads):
    INF = 10 ** 15
    d = [[INF] * n for _ in range(n)]
    for i in range(n):
        d[i][i] = 0
    for a, b, w in roads:
        if w < d[a][b]:
            d[a][b] = d[b][a] = w
    for k in range(n):
        dk = d[k]
        for i in range(n):
            dik = d[i][k]
            if dik < INF:
                d[i] = [x if x <= dik + y else dik + y for x, y in zip(d[i], dk)]
    ecc = [max(row) for row in d]
    if max(ecc) >= INF:
        return [-1, -1]
    return [min(ecc), max(ecc)]
''',
    tests=_tests,
)


def b_radius(n, roads):
    edges = [[a, b, w] for a, b, w in roads] + [[b, a, w] for a, b, w in roads]
    ecc = []
    for s in range(n):
        d = _bf_dist(n, edges, s)
        if any(x is None for x in d):
            return [-1, -1]
        ecc.append(max(d))
    return [min(ecc), max(ecc)]


def g_radius(r):
    n = r.randint(1, 7)
    m = r.randint(0, n * (n - 1) // 2) if n >= 2 else 0
    ps = _upairs(r, n, m, connected=r.random() < 0.7) if n >= 2 else []
    return [n, [[u, v, r.randint(1, 9)] for u, v in ps]]


CHECKS["weighted-graph-radius-and-diameter"] = (b_radius, g_radius, "exact")
VALIDATE["weighted-graph-radius-and-diameter"] = v_allpairs

# ====================================================================== MEDIUM
# ---------------------------------------------------------------- distances with negative edges
_tests = [
    [5, [[0, 1, 4], [0, 2, 5], [1, 2, -3], [2, 3, 2], [3, 1, 2]], 0],
    [3, [[0, 1, 5], [1, 2, -4]], 0],
    [1, [], 0],
    [3, [[0, 1, 2]], 2],
    [4, [[0, 1, 1], [1, 2, -1], [2, 3, -1]], 1],
    [4, [[0, 1, 10], [0, 2, 3], [2, 1, -8], [1, 3, 1]], 0],
    [5, [[0, 1, 1], [1, 2, 1], [2, 3, 1], [3, 4, 1], [0, 4, 100], [4, 2, -1]], 0],
    [4, [[3, 2, -5], [2, 1, -5], [1, 0, -5]], 3],
    [6, [[0, 1, 2], [1, 2, -2], [2, 0, 0], [2, 3, -7], [3, 4, 4]], 0],
]
_r = rnd(8103)
_n = 300
_chain = [[i, i + 1, _r.randint(-3, 5)] for i in range(_n - 1)][::-1]
_tests.append([_n, _chain, 0])
_e = _pot_edges(_r, 300, 2000, 250, 300)
_tests.append([300, _e, 0])
_e = _pot_edges(_r, 300, 700, 250, 300)
_tests.append([300, _e, 17])
_tests.append([300, [[i, i + 1, -1000] for i in range(299)][::-1] + [[i, i + 2, 1000] for i in range(0, 298, 2)], 0])
_tests.append([200, [[u, v, _r.randint(0, 100)] for u, v in _dpairs(_r, 200, 1500)], 5])

add(
    id="distances-with-negative-edge-weights", title="Shortest Distances With Negative Edge Weights", diff="Medium", topic="Graphs",
    fn="shortestDistances", params=[("n", "int"), ("edges", "int[][]"), ("src", "int")], ret="int[]", cmp="exact",
    desc="<p>A delivery network has <code>n</code> depots labelled <code>0</code> to <code>n - 1</code>. Each <code>edges[i] = [from, to, cost]</code> is a one-way route. A cost can be <em>negative</em>: the courier receives a rebate for that leg.</p><p>It is guaranteed that no cycle in the network has a negative total cost, so cheapest routes are well defined. Return an array <code>dist</code> of length <code>n</code> where <code>dist[v]</code> is the lowest total cost of a route from <code>src</code> to depot <code>v</code>, or <code>1000000000</code> if <code>v</code> cannot be reached from <code>src</code>. Of course <code>dist[src] = 0</code>.</p><p>Example: <code>n = 5</code>, <code>edges = [[0,1,4],[0,2,5],[1,2,-3],[2,3,2],[3,1,2]]</code>, <code>src = 0</code>. Going 0 &rarr; 1 &rarr; 2 costs 4 - 3 = 1, cheaper than the direct 5. The answer is <code>[0, 4, 1, 3, 1000000000]</code>; depot 4 has no incoming route.</p>",
    constraints=["1 &le; n &le; 300", "0 &le; edges.length &le; 2,000", "edges[i] = [from, to, cost] with 0 &le; from, to &lt; n, from &ne; to and -1,000 &le; cost &le; 1,000", "Each ordered pair (from, to) appears at most once", "The graph has no cycle of negative total cost; zero-cost cycles may exist", "0 &le; src &lt; n"],
    hints=["Dijkstra's greedy choice (the closest unfinished node is final) fails once an edge can lower a cost that was already settled.",
           "A cheapest route never needs to repeat a depot, so it has at most n - 1 edges. Relax every edge repeatedly: <code>dist[v] = min(dist[v], dist[u] + cost)</code>.",
           "Bellman-Ford: do up to n - 1 passes over all edges, skipping edges whose source is still unreachable, and stop early when a whole pass changes nothing. After pass j, every route with at most j edges is accounted for."],
    editorial=["Bellman-Ford keeps the best known cost for each depot and relaxes all edges again and again. Induction on the number of edges shows that after pass j, <code>dist[v]</code> is at most the cost of the cheapest route to v that uses j edges or fewer. Because there is no negative cycle, a cheapest route can be chosen without repeated depots, so n - 1 edges and therefore n - 1 passes always suffice.",
               "Each pass costs O(E), so the total is O(n &middot; E) in the worst case, and the early exit makes typical inputs much faster. Only relax from depots that are already reachable; adding a cost to a 'not reachable' marker would corrupt the result. Dijkstra is faster (O(E log n)) but only correct for non-negative costs. Adding a constant to every edge to remove negatives does not work either, since routes with more edges would be penalised more."],
    time="O(n &middot; E)", space="O(n)",
    solution='''def shortestDistances(n, edges, src):
    NOPATH = 1000000000
    INF = float('inf')
    dist = [INF] * n
    dist[src] = 0
    for _ in range(n - 1):
        changed = False
        for u, v, w in edges:
            if dist[u] != INF and dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
                changed = True
        if not changed:
            break
    return [NOPATH if d == INF else d for d in dist]
''',
    tests=_tests,
)


def b_negdist(n, edges, src):
    INF = 10 ** 15
    d = [[INF] * n for _ in range(n)]
    for i in range(n):
        d[i][i] = 0
    for u, v, w in edges:
        d[u][v] = min(d[u][v], w)
    for k in range(n):
        for i in range(n):
            for j in range(n):
                if d[i][k] + d[k][j] < d[i][j]:
                    d[i][j] = d[i][k] + d[k][j]
    return [NOPATH if d[src][v] >= INF // 2 else d[src][v] for v in range(n)]


def g_negdist(r):
    n = r.randint(1, 7)
    m = r.randint(0, n * 2) if n >= 2 else 0
    e = _pot_edges(r, n, m, 5, 6) if n >= 2 else []
    return [n, e, r.randrange(n)]


def v_negdist(tests):
    for t in tests:
        n, edges, src = t["args"]
        assert 1 <= n <= 300 and len(edges) <= 2000 and 0 <= src < n
        seen = set()
        for u, v, w in edges:
            assert 0 <= u < n and 0 <= v < n and u != v and -1000 <= w <= 1000
            assert (u, v) not in seen
            seen.add((u, v))
        # no negative cycle: n rounds of relaxation from a virtual source must converge
        dist = [0] * n
        for rnd_ in range(n + 1):
            ch = False
            for u, v, w in edges:
                if dist[u] + w < dist[v]:
                    dist[v] = dist[u] + w
                    ch = True
            if not ch:
                break
        else:
            raise AssertionError("negative cycle in a test")


CHECKS["distances-with-negative-edge-weights"] = (b_negdist, g_negdist, "exact")
VALIDATE["distances-with-negative-edge-weights"] = v_negdist

# ---------------------------------------------------------------- negative cycle reachable from source
_tests = [
    [3, [[0, 1, 1], [1, 2, -2], [2, 1, 1]], 0],
    [3, [[0, 1, 1], [1, 2, -2], [2, 1, 2]], 0],
    [4, [[0, 1, 5], [2, 3, -4], [3, 2, 1]], 0],
    [1, [], 0],
    [2, [[0, 1, -5]], 0],
    [2, [[0, 1, -5], [1, 0, 4]], 1],
    [2, [[0, 1, -5], [1, 0, 5]], 0],
    [4, [[0, 1, 1], [1, 2, 1], [2, 3, 1], [3, 1, -3]], 0],
    [4, [[0, 1, 1], [1, 2, 1], [2, 3, 1], [3, 1, -3]], 3],
    [4, [[1, 0, 1], [1, 2, 1], [2, 3, 1], [3, 1, -3]], 0],
    [3, [[0, 0, -1]], 0],
    [3, [[0, 1, 4], [0, 0, 0], [1, 2, 3]], 0],
]
_r = rnd(8104)
_n = 300
_base = [[i, i + 1, 1] for i in range(_n - 1)]
_tests.append([_n, _shuffled(_r, _base + [[_n - 1, 0, -(_n - 1) - 1]]), 0])
_tests.append([_n, _shuffled(_r, _base + [[_n - 1, 0, -(_n - 1)]]), 0])
_tests.append([_n, _shuffled(_r, _base + [[_n - 1, 0, -(_n - 1) - 1]]), _n - 1])
_e = _dag_edges(_r, 250, 1200, -20, 30)
_e1 = _close(_e, 250, 100, 110, 1)
_tests.append([250, _shuffled(_r, _e1), 0])
_tests.append([250, _shuffled(_r, _e1), 120])
_e2 = _close(_e, 250, 100, 110, 0)
_tests.append([250, _shuffled(_r, _e2), 0])
_tests.append([300, _pot_edges(_r, 300, 1800, 250, 300, loops=True), 3])

add(
    id="negative-cycle-reachable-from-source", title="Negative Cycle Reachable From Source", diff="Medium", topic="Graphs",
    fn="hasNegativeCycle", params=[("n", "int"), ("edges", "int[][]"), ("src", "int")], ret="bool", cmp="exact",
    desc="<p>A directed network has <code>n</code> nodes labelled <code>0</code> to <code>n - 1</code>. Each <code>edges[i] = [from, to, w]</code> is a one-way edge of weight <code>w</code>, which may be negative.</p><p>Return <code>true</code> if the network contains a cycle whose total weight is <em>strictly negative</em> and that can be reached from node <code>src</code> (that is, some node of the cycle is reachable from <code>src</code>, which means all of them are). Otherwise return <code>false</code>. A cycle of total weight exactly 0 does not count, and a negative cycle that <code>src</code> can never reach does not count either. A self-loop <code>[v, v, w]</code> is a cycle of one edge.</p><p>Example: <code>n = 3</code>, <code>edges = [[0,1,1],[1,2,-2],[2,1,1]]</code>, <code>src = 0</code>. The cycle 1 &rarr; 2 &rarr; 1 has weight -2 + 1 = -1 and is reachable, so the answer is <code>true</code>. If the last edge had weight 2 the cycle would total 0 and the answer would be <code>false</code>.</p>",
    constraints=["1 &le; n &le; 300", "0 &le; edges.length &le; 2,000", "edges[i] = [from, to, w] with 0 &le; from, to &lt; n and -1,000 &le; w &le; 1,000", "Each ordered pair (from, to) appears at most once; from may equal to", "0 &le; src &lt; n"],
    hints=["If shortest distances from src were well defined, they would stop changing after enough rounds of relaxing all edges. What happens when a negative cycle is reachable?",
           "Relax all edges n - 1 times, only from nodes that already have a finite distance. A shortest simple route has at most n - 1 edges, so without a reachable negative cycle everything is final by then.",
           "Do one more pass. If any edge can still be relaxed (<code>dist[u] + w &lt; dist[v]</code> with <code>dist[u]</code> finite), a negative cycle is reachable from src; return true. Nodes with no route from src must be ignored, otherwise unreachable negative cycles cause false alarms."],
    editorial=["This is the standard Bellman-Ford negative cycle test. Start with <code>dist[src] = 0</code> and infinity elsewhere and relax every edge n - 1 times, skipping edges that start at an unreached node. If no negative cycle is reachable, then each shortest route is a simple path of at most n - 1 edges, so all distances are final after those passes and an n-th pass changes nothing. If a reachable negative cycle exists, its total weight is below zero, so the sum of the relaxation inequalities around it cannot all hold: at least one edge of the cycle is still relaxable in the n-th pass.",
               "The condition 'reachable from src' is what the infinity guard implements: unreached nodes keep infinite distance and never relax anything, so a negative cycle in a different component is invisible, as the problem requires. Zero-weight cycles never allow a strict improvement and are not reported. Time is O(n &middot; E), space O(n). Floyd-Warshall with a check for <code>d[i][i] &lt; 0</code> also finds negative cycles but in O(n<sup>3</sup>) and it would need an extra reachability test."],
    time="O(n &middot; E)", space="O(n)",
    solution='''def hasNegativeCycle(n, edges, src):
    INF = float('inf')
    dist = [INF] * n
    dist[src] = 0
    for _ in range(n - 1):
        changed = False
        for u, v, w in edges:
            if dist[u] != INF and dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
                changed = True
        if not changed:
            return False
    for u, v, w in edges:
        if dist[u] != INF and dist[u] + w < dist[v]:
            return True
    return False
''',
    tests=_tests,
)


def b_negcycle(n, edges, src):
    adj = _adj(n, edges)
    reach = _reach(n, adj, src)
    for nodes, total, _ in _simple_cycles(n, adj):
        if total < 0 and next(iter(nodes)) in reach:
            return True
    return False


def g_negcycle(r):
    n = r.randint(1, 7)
    m = r.randint(0, n * 2)
    if r.random() < 0.4:
        e = _pot_edges(r, n, m, 5, 6, loops=True)
        if e and r.random() < 0.5:
            e[r.randrange(len(e))][2] -= r.randint(0, 3)
    else:
        e = [[u, v, r.randint(-3, 5)] for u, v in _dpairs(r, n, m, loops=True)]
    return [n, e, r.randrange(n)]


def v_negcycle(tests):
    got = [t["expected"] for t in tests]
    assert True in got and False in got
    for t in tests:
        n, edges, src = t["args"]
        assert 1 <= n <= 300 and len(edges) <= 2000 and 0 <= src < n
        seen = set()
        for u, v, w in edges:
            assert 0 <= u < n and 0 <= v < n and -1000 <= w <= 1000
            assert (u, v) not in seen
            seen.add((u, v))


CHECKS["negative-cycle-reachable-from-source"] = (b_negcycle, g_negcycle, "exact")
VALIDATE["negative-cycle-reachable-from-source"] = v_negcycle

# ---------------------------------------------------------------- currency arbitrage
_tests = [
    [3, [[0, 1, 2, 1], [1, 2, 3, 1], [2, 0, 1, 7]]],
    [3, [[0, 1, 2, 1], [1, 2, 3, 1], [2, 0, 1, 5]]],
    [2, [[0, 1, 3, 2], [1, 0, 2, 3]]],
    [2, [[0, 1, 3, 2], [1, 0, 3, 4]]],
    [2, []],
    [4, [[0, 1, 1000, 1], [1, 2, 1000, 1], [2, 3, 1000, 1], [0, 3, 1000, 1], [0, 2, 1000, 1], [1, 3, 1000, 1]]],
    [5, [[0, 1, 1, 2], [1, 0, 1, 2], [2, 3, 2, 1], [3, 4, 3, 1], [4, 2, 1, 5]]],
    [3, [[0, 1, 1000, 999], [1, 2, 999, 998], [2, 0, 998, 1000]]],
    [3, [[0, 1, 1000, 999], [1, 2, 999, 998], [2, 0, 998, 999]]],
    [2, [[0, 1, 2, 1], [1, 0, 2, 1]]],
    [4, [[0, 1, 5, 4], [1, 2, 5, 4], [2, 3, 5, 4], [3, 0, 1, 2]]],
    [4, [[0, 1, 5, 4], [1, 2, 5, 4], [2, 3, 5, 4], [3, 0, 1, 3]]],
]
_r = rnd(8105)


def _consistent_rates(r, n, m, bump=False):
    """Rates P[u] / P[v] : every cycle multiplies to exactly 1."""
    P = r.sample(range(1, 1001), n)
    e = [[u, v, P[u], P[v]] for u, v in _dpairs(r, n, m)]
    if bump:
        cand = [x for x in e if x[2] < 1000]
        x = r.choice(cand)
        x[2] += 1
    return e


def _telescope_cycle(n, bump):
    P = list(range(1000, 1000 - n, -1))
    e = [[i, (i + 1) % n, P[i], P[(i + 1) % n]] for i in range(n)]
    if bump:
        e[7][2] -= 1
    return e


_tests.append([50, _consistent_rates(_r, 50, 600)])
_tests.append([50, _consistent_rates(_r, 50, 600, bump=True)])
_tests.append([50, _telescope_cycle(50, False)])
_tests.append([50, _telescope_cycle(50, True)])
_tests.append([50, [[u, v, _r.randint(1, 1000), _r.randint(1, 1000)] for u, v in _dpairs(_r, 50, 500)]])
_tests.append([50, [[u, v, a, b] for u, v in _dpairs(_r, 50, 600) for a, b in [sorted((_r.randint(1, 1000), _r.randint(1, 1000)))]]])
_tests.append([50, [[i, i + 1, 999, 1000] for i in range(49)] + [[49, 0, 1000, 600]]])

add(
    id="currency-arbitrage-exists", title="Currency Arbitrage Exists", diff="Medium", topic="Graphs",
    fn="hasArbitrage", params=[("n", "int"), ("rates", "int[][]")], ret="bool", cmp="exact",
    desc="<p>An exchange desk deals in <code>n</code> currencies numbered <code>0</code> to <code>n - 1</code>. Each <code>rates[i] = [from, to, num, den]</code> says that one unit of currency <code>from</code> can be converted into exactly <code>num / den</code> units of currency <code>to</code>. Only the listed directions are available, a conversion can be used any number of times, and amounts may be fractional.</p><p>An <em>arbitrage</em> is a closed loop of conversions that starts and ends in the same currency and leaves you with <em>strictly more</em> of it than you started with. Return <code>true</code> if an arbitrage exists and <code>false</code> otherwise. A loop that returns exactly what you started with is not an arbitrage.</p><p>Example: <code>n = 3</code>, <code>rates = [[0,1,2,1],[1,2,3,1],[2,0,1,5]]</code>. One unit of 0 becomes 2 units of 1, then 6 units of 2, then 6/5 units of 0, which is more than 1, so the answer is <code>true</code>. With the last rate 1/7 the loop returns 6/7, so the answer is <code>false</code>.</p>",
    constraints=["2 &le; n &le; 50", "0 &le; rates.length &le; 600", "rates[i] = [from, to, num, den] with 0 &le; from, to &lt; n, from &ne; to and 1 &le; num, den &le; 1,000", "Each ordered pair (from, to) appears at most once"],
    hints=["A loop gains money exactly when the product of its rates is greater than 1. Products are awkward; how can multiplication become addition?",
           "Taking logarithms turns 'product &gt; 1' into 'sum of log-rates &gt; 0', that is, a positive cycle. Negating gives a negative cycle, which Bellman-Ford can detect. Floating point can misjudge loops whose product is exactly 1, though.",
           "Stay exact: keep for each currency the best product so far as a fraction (numerator, denominator), start every currency at 1/1, and relax with <code>best[u] * rate &gt; best[v]</code> using integer cross-multiplication. In each round read the values of the previous round. If an improvement is still possible in round n, there is a profitable loop."],
    editorial=["Model currencies as nodes and conversions as directed edges. A closed loop is profitable when the product of its rates exceeds 1. Instead of minimising a sum of weights, Bellman-Ford can <em>maximise a product</em>: start every currency with value 1 (as if a free virtual source led to each currency), and repeatedly relax <code>value[v] = max(value[v], value[u] * rate)</code>, computing each round from the values of the previous round. After round j, <code>value[v]</code> is the best product over chains of at most j conversions. Without a profitable loop the values settle after n - 1 rounds, because an optimal chain never repeats a currency (cutting out a loop of product at most 1 cannot hurt). If round n still improves something, a chain of n conversions beats every shorter chain, and since it repeats a currency it contains a profitable loop.",
               "Floating-point logarithms are the textbook shortcut, but a loop whose product is exactly 1 (for example 2/1 followed by 1/2, or long telescoping chains) may come out as 1.0000000000000002 and be wrongly reported. With integer rates you can avoid the problem completely by storing each value as an unreduced pair <code>(a, b)</code> and comparing <code>a1 * b2 &gt; a2 * b1</code>; Python integers do not overflow, and because every round uses only the previous round's values, numbers have at most about 10 bits per conversion in the chain, so they stay small. With at most 50 currencies and 600 rates the work is about 50 &middot; 600 big-integer multiplications. Time O(n &middot; E) operations, space O(n)."],
    time="O(n &middot; E)", space="O(n)",
    solution='''def hasArbitrage(n, rates):
    num = [1] * n
    den = [1] * n
    for _ in range(n):
        nn = num[:]
        dd = den[:]
        changed = False
        for u, v, a, b in rates:
            x = num[u] * a
            y = den[u] * b
            if x * dd[v] > nn[v] * y:
                nn[v], dd[v] = x, y
                changed = True
        if not changed:
            return False
        num, den = nn, dd
    return True
''',
    tests=_tests,
)


def b_arbitrage(n, rates):
    adj = [[] for _ in range(n)]
    for u, v, a, b in rates:
        adj[u].append((v, Fraction(a, b)))
    for s in range(n):
        # simple cycles whose smallest node is s
        stack = [(s, {s}, Fraction(1))]
        while stack:
            u, seen, prod = stack.pop()
            for v, f in adj[u]:
                if v == s:
                    if prod * f > 1:
                        return True
                elif v > s and v not in seen:
                    stack.append((v, seen | {v}, prod * f))
    return False


def g_arbitrage(r):
    n = r.randint(2, 6)
    m = r.randint(0, n * 2)
    mode = r.random()
    if mode < 0.35:
        P = r.sample(range(1, 12), n)
        e = [[u, v, P[u], P[v]] for u, v in _dpairs(r, n, m)]
        if e and r.random() < 0.5:
            r.choice(e)[2] += 1
    else:
        e = [[u, v, r.randint(1, 6), r.randint(1, 6)] for u, v in _dpairs(r, n, m)]
    return [n, e]


def v_arbitrage(tests):
    got = [t["expected"] for t in tests]
    assert True in got and False in got
    for t in tests:
        n, rates = t["args"]
        assert 2 <= n <= 50 and len(rates) <= 600
        seen = set()
        for u, v, a, b in rates:
            assert 0 <= u < n and 0 <= v < n and u != v and 1 <= a <= 1000 and 1 <= b <= 1000
            assert (u, v) not in seen
            seen.add((u, v))
        # independent exact check with Fractions (max-product Bellman-Ford)
        val = [Fraction(1)] * n
        for _ in range(n):
            nxt = val[:]
            ch = False
            for u, v, a, b in rates:
                x = val[u] * Fraction(a, b)
                if x > nxt[v]:
                    nxt[v] = x
                    ch = True
            val = nxt
            if not ch:
                break
        assert ch == t["expected"], "arbitrage mismatch"


CHECKS["currency-arbitrage-exists"] = (b_arbitrage, g_arbitrage, "exact")
VALIDATE["currency-arbitrage-exists"] = v_arbitrage

# ---------------------------------------------------------------- city with fewest neighbors within threshold
_tests = [
    [4, [[0, 1, 3], [1, 2, 1], [1, 3, 4], [2, 3, 1]], 4],
    [5, [[0, 1, 2], [0, 4, 8], [1, 2, 3], [1, 4, 2], [2, 3, 1], [3, 4, 1]], 2],
    [3, [[0, 1, 5], [1, 2, 5]], 1],
    [1, [], 10],
    [2, [[0, 1, 4]], 4],
    [2, [[0, 1, 4]], 3],
    [4, [[0, 1, 1], [1, 2, 1], [2, 3, 1], [3, 0, 1]], 2],
    [4, [[0, 1, 1], [0, 2, 1], [0, 3, 1]], 1],
    [6, [[0, 1, 1], [1, 2, 1], [3, 4, 1], [4, 5, 1], [2, 3, 100]], 3],
    [5, [[0, 1, 10], [1, 2, 10], [2, 3, 10], [3, 4, 10], [0, 4, 25]], 20],
]
_r = rnd(8106)
_tests.append([80, [[i, i + 1, 3] for i in range(79)], 30])
_tests.append([80, [[u, v, _r.randint(1, 10000)] for u, v in _upairs(_r, 80, 1200, True)], 6000])
_tests.append([80, [[u, v, _r.randint(1, 10000)] for u, v in _upairs(_r, 80, 300, True)], 12000])
_tests.append([80, [[u, v, _r.randint(1, 100)] for u, v in _upairs(_r, 80, 1400)], 150])
_tests.append([60, [[u, v, _r.randint(1, 20)] for u, v in _upairs(_r, 60, 150, True)], 1])

add(
    id="city-with-fewest-reachable-neighbors", title="City With Fewest Reachable Neighbors", diff="Medium", topic="Graphs",
    fn="findCity", params=[("n", "int"), ("roads", "int[][]"), ("threshold", "int")], ret="int", cmp="exact",
    desc="<p>There are <code>n</code> cities labelled <code>0</code> to <code>n - 1</code>. Each <code>roads[i] = [a, b, w]</code> is a two-way road of length <code>w</code>.</p><p>A city <code>y</code> is a <em>neighbor</em> of city <code>x</code> if <code>y &ne; x</code> and the shortest route from x to y has total length at most <code>threshold</code> (routes may pass through other cities). Return the city that has the <em>fewest</em> neighbors. If several cities tie, return the one with the <em>largest</em> label.</p><p>Example: <code>n = 4</code>, roads <code>[[0,1,3],[1,2,1],[1,3,4],[2,3,1]]</code>, <code>threshold = 4</code>. The shortest distances are 0-1: 3, 0-2: 4, 0-3: 5, 1-2: 1, 1-3: 2, 2-3: 1. Neighbor counts are 2, 3, 3, 2 for cities 0, 1, 2, 3, so cities 0 and 3 tie and the answer is <code>3</code>.</p>",
    constraints=["1 &le; n &le; 80 (for n = 1 the answer is 0)", "0 &le; roads.length &le; n(n - 1) / 2", "roads[i] = [a, b, w] with 0 &le; a, b &lt; n, a &ne; b and 1 &le; w &le; 10,000", "1 &le; threshold &le; 100,000", "No two roads join the same pair of cities"],
    hints=["To count neighbors you must know the shortest distance from every city to every other city.",
           "With n at most 80, run Floyd-Warshall (all pairs in O(n<sup>3</sup>)) or Dijkstra from each city. A direct road can be longer than a detour, so do not use road lengths directly.",
           "For each city count the other cities with distance &le; threshold. Keep the city with the smallest count, and on equal counts prefer the larger label (iterate in increasing order and use &le; when comparing)."],
    editorial=["Compute the full distance matrix with Floyd-Warshall: initialise the diagonal to 0 and direct roads to their length, then for each intermediate city k relax every pair with <code>d[i][k] + d[k][j]</code>. This costs O(n<sup>3</sup>), about half a million operations for n = 80.",
               "Then scan each row and count entries (other than the diagonal) with distance at most the threshold. Walk the cities in increasing order and replace the best candidate whenever the current count is smaller than or equal to the best count; this implements the 'largest label wins ties' rule in one pass. Running Dijkstra from every city is an alternative with O(n &middot; E log n) time and wins on sparse graphs, while Floyd-Warshall is simpler to code. Unreachable pairs have infinite distance and are naturally excluded."],
    time="O(n<sup>3</sup>)", space="O(n<sup>2</sup>)",
    solution='''def findCity(n, roads, threshold):
    INF = 10 ** 15
    d = [[INF] * n for _ in range(n)]
    for i in range(n):
        d[i][i] = 0
    for a, b, w in roads:
        if w < d[a][b]:
            d[a][b] = d[b][a] = w
    for k in range(n):
        dk = d[k]
        for i in range(n):
            dik = d[i][k]
            if dik < INF:
                d[i] = [x if x <= dik + y else dik + y for x, y in zip(d[i], dk)]
    best_city, best_count = -1, n + 1
    for i in range(n):
        cnt = sum(1 for j in range(n) if j != i and d[i][j] <= threshold)
        if cnt <= best_count:
            best_city, best_count = i, cnt
    return best_city
''',
    tests=_tests,
)


def b_city(n, roads, threshold):
    adj = _adj(n, roads, True)
    counts = []
    for s in range(n):
        dist = {s: 0}
        h = [(0, s)]
        while h:
            d, u = heapq.heappop(h)
            if d > dist[u]:
                continue
            for v, w in adj[u]:
                if d + w < dist.get(v, 10 ** 18):
                    dist[v] = d + w
                    heapq.heappush(h, (d + w, v))
        counts.append(sum(1 for v, d in dist.items() if v != s and d <= threshold))
    m = min(counts)
    return max(i for i in range(n) if counts[i] == m)


def g_city(r):
    n = r.randint(1, 7)
    m = r.randint(0, n * (n - 1) // 2) if n >= 2 else 0
    ps = _upairs(r, n, m, connected=r.random() < 0.5) if n >= 2 else []
    return [n, [[u, v, r.randint(1, 8)] for u, v in ps], r.randint(1, 14)]


def v_city(tests):
    for t in tests:
        n, roads, th = t["args"]
        assert 1 <= n <= 80 and len(roads) <= n * (n - 1) // 2 and 1 <= th <= 100000
        seen = set()
        for a, b, w in roads:
            assert 0 <= a < n and 0 <= b < n and a != b and 1 <= w <= 10000
            k = (min(a, b), max(a, b))
            assert k not in seen
            seen.add(k)


CHECKS["city-with-fewest-reachable-neighbors"] = (b_city, g_city, "exact")
VALIDATE["city-with-fewest-reachable-neighbors"] = v_city

# ---------------------------------------------------------------- cheapest walk with exactly k roads
_tests = [
    [3, [[0, 1, 4], [1, 2, -2], [2, 0, 3], [0, 2, 5]], 0, 2, 2],
    [3, [[0, 1, 4], [1, 2, -2], [2, 0, 3], [0, 2, 5]], 0, 2, 1],
    [3, [[0, 1, 4], [1, 2, -2], [2, 0, 3], [0, 2, 5]], 0, 2, 3],
    [3, [[0, 1, 4], [1, 2, -2], [2, 0, 3], [0, 2, 5]], 0, 2, 4],
    [2, [[0, 1, 1]], 0, 0, 0],
    [2, [[0, 1, 1]], 0, 1, 0],
    [2, [[0, 1, 1]], 0, 0, 2],
    [2, [[0, 1, -5], [1, 0, 2]], 0, 0, 6],
    [2, [[0, 1, -5], [1, 0, 2]], 0, 1, 7],
    [4, [[0, 1, 1], [1, 2, 1], [2, 3, 1], [0, 3, 10]], 0, 3, 3],
    [4, [[0, 1, 1], [1, 2, 1], [2, 3, 1], [0, 3, 10]], 0, 3, 1],
    [4, [[0, 1, 1], [1, 2, 1], [2, 3, 1], [0, 3, 10]], 0, 3, 2],
]
_r = rnd(8107)
_tests.append([100, [[i, (i + 1) % 100, 1] for i in range(100)], 0, 37, 237])
_tests.append([100, [[i, (i + 1) % 100, _r.randint(-5, 20)] for i in range(100)] + [[u, v, _r.randint(-50, 100)] for u, v in _dpairs(_r, 100, 600) if v != (u + 1) % 100], 0, 99, 300])
_tests.append([100, [[u, v, _r.randint(-100, 100)] for u, v in _dpairs(_r, 100, 900)], 7, 61, 250])
_tests.append([60, [[u, v, _r.randint(-3, 3)] for u, v in _dpairs(_r, 60, 400)], 1, 1, 299])

add(
    id="cheapest-walk-with-exactly-k-roads", title="Cheapest Walk With Exactly K Roads", diff="Medium", topic="Graphs",
    fn="cheapestExactWalk", params=[("n", "int"), ("roads", "int[][]"), ("src", "int"), ("dst", "int"), ("k", "int")], ret="int", cmp="exact", tier="extra",
    desc="<p>A one-way road network has <code>n</code> towns labelled <code>0</code> to <code>n - 1</code>. Each <code>roads[i] = [from, to, toll]</code> is a one-way road. A toll may be <em>negative</em> (a bonus paid to the driver).</p><p>A travel plan must start at town <code>src</code>, end at town <code>dst</code> and use <em>exactly</em> <code>k</code> roads. Towns and roads may be used again and again, so cycles are allowed. Return the smallest possible sum of tolls over all such plans, or <code>1000000000</code> if no plan with exactly k roads exists. With <code>k = 0</code> the only plan is to stay put, which works only when <code>src == dst</code> and costs 0.</p><p>Because the number of roads is fixed, a cycle with negative total toll cannot be repeated forever, so the answer is always well defined.</p><p>Example: <code>roads = [[0,1,4],[1,2,-2],[2,0,3],[0,2,5]]</code>, <code>src = 0</code>, <code>dst = 2</code>. With <code>k = 1</code> the answer is 5, with <code>k = 2</code> it is 2 (0 &rarr; 1 &rarr; 2), and with <code>k = 3</code> it is 13 (0 &rarr; 2 &rarr; 0 &rarr; 2).</p>",
    constraints=["1 &le; n &le; 100", "0 &le; roads.length &le; 1,000", "roads[i] = [from, to, toll] with 0 &le; from, to &lt; n, from &ne; to and -100 &le; toll &le; 100", "0 &le; src, dst &lt; n", "0 &le; k &le; 300", "Each ordered pair (from, to) appears at most once"],
    hints=["A plain shortest path would ignore the 'exactly k roads' rule, and with negative tolls you cannot just forbid revisiting towns.",
           "Let <code>f[j][v]</code> be the cheapest toll total of a plan that starts at src, uses exactly j roads and ends at v. How is <code>f[j]</code> computed from <code>f[j-1]</code>?",
           "Start with <code>f[0][src] = 0</code>. For each j from 1 to k, build a fresh array: for every road (u, v, t) with <code>f[j-1][u]</code> finite, update <code>f[j][v] = min(f[j][v], f[j-1][u] + t)</code>. Return <code>f[k][dst]</code> or the 'impossible' value."],
    editorial=["This is Bellman-Ford without the early exit and without the 'at most' relaxation: the rounds themselves are the answer. Layer j of the table stores the best cost for walks of exactly j roads. Every layer is built only from the previous one, so a road is counted once per round, and the final layer k holds the cheapest cost of walks with exactly k roads ending in each town.",
               "Negative cycles are harmless here because a walk cannot loop more than k times; the minimum over a finite set of walks exists. That is the difference from the unrestricted shortest path problem, where a negative cycle would make the answer unbounded. Only the previous layer is needed, so space is O(n) and time is O(k &middot; E). If k were huge (10<sup>9</sup>), the same recurrence would be done by repeated squaring of the distance matrix in the (min, +) semiring."],
    time="O(k &middot; E)", space="O(n)",
    solution='''def cheapestExactWalk(n, roads, src, dst, k):
    NOPATH = 1000000000
    INF = float('inf')
    cur = [INF] * n
    cur[src] = 0
    for _ in range(k):
        nxt = [INF] * n
        for u, v, t in roads:
            if cur[u] != INF and cur[u] + t < nxt[v]:
                nxt[v] = cur[u] + t
        cur = nxt
    return NOPATH if cur[dst] == INF else cur[dst]
''',
    tests=_tests,
)


def b_exactwalk(n, roads, src, dst, k):
    adj = _adj(n, roads)
    best = [None]

    def go(u, left, cost):
        if left == 0:
            if u == dst and (best[0] is None or cost < best[0]):
                best[0] = cost
            return
        for v, t in adj[u]:
            go(v, left - 1, cost + t)

    go(src, k, 0)
    return NOPATH if best[0] is None else best[0]


def g_exactwalk(r):
    n = r.randint(1, 5)
    m = r.randint(0, n * 2) if n >= 2 else 0
    e = [[u, v, r.randint(-6, 8)] for u, v in _dpairs(r, n, m)] if n >= 2 else []
    return [n, e, r.randrange(n), r.randrange(n), r.randint(0, 7)]


def v_exactwalk(tests):
    for t in tests:
        n, roads, src, dst, k = t["args"]
        assert 1 <= n <= 100 and len(roads) <= 1000 and 0 <= src < n and 0 <= dst < n and 0 <= k <= 300
        seen = set()
        for u, v, w in roads:
            assert 0 <= u < n and 0 <= v < n and u != v and -100 <= w <= 100
            assert (u, v) not in seen
            seen.add((u, v))


CHECKS["cheapest-walk-with-exactly-k-roads"] = (b_exactwalk, g_exactwalk, "exact")
VALIDATE["cheapest-walk-with-exactly-k-roads"] = v_exactwalk

# ---------------------------------------------------------------- sum of distances after each new road
_tests = [
    [4, [[0, 1, 5], [1, 2, 5], [2, 3, 5]], [[0, 3, 4], [1, 3, 1]]],
    [2, [[0, 1, 10]], [[0, 1, 4], [0, 1, 6], [1, 0, 1]]],
    [3, [[0, 1, 1], [1, 2, 1]], []],
    [3, [[0, 1, 1], [1, 2, 1]], [[0, 2, 5]]],
    [3, [[0, 1, 9], [1, 2, 9]], [[0, 2, 1]]],
    [1, [], []],
    [5, [[0, 1, 100], [1, 2, 100], [2, 3, 100], [3, 4, 100]], [[0, 4, 50], [1, 3, 10], [0, 2, 1]]],
    [4, [[0, 1, 3], [0, 2, 3], [0, 3, 3]], [[1, 2, 1], [2, 3, 1], [1, 3, 1]]],
    [4, [[0, 1, 2], [0, 1, 1], [1, 2, 7], [2, 3, 7]], [[0, 3, 3], [0, 3, 2]]],
]
_r = rnd(8108)


def _road_case(r, n, m_extra, q, wmax, qmax):
    init = [[u, v, r.randint(1, wmax)] for u, v in _upairs(r, n, n - 1 + m_extra, True)]
    qs = []
    for _ in range(q):
        u, v = r.sample(range(n), 2)
        qs.append([u, v, r.randint(1, qmax)])
    return [n, init, qs]


_tests.append(_road_case(_r, 60, 60, 100, 1000, 400))
_tests.append(_road_case(_r, 60, 0, 100, 1000, 1000))
_tests.append(_road_case(_r, 50, 40, 80, 1000, 600))
_tests.append([60, [[i, i + 1, 1000] for i in range(59)], [[0, 59, 1000 - 17 * 10]] + [[i, i + 5, 5] for i in range(0, 50, 5)]])
_tests.append(_road_case(_r, 40, 100, 100, 20, 30))

add(
    id="sum-of-distances-after-each-new-road", title="Sum of Distances After Each New Road", diff="Medium", topic="Graphs",
    fn="distanceSumsAfterRoads", params=[("n", "int"), ("roads", "int[][]"), ("newRoads", "int[][]")], ret="int[]", cmp="exact", tier="extra",
    desc="<p>A country has <code>n</code> towns labelled <code>0</code> to <code>n - 1</code> and an existing set of two-way roads <code>roads[i] = [a, b, w]</code> of length <code>w</code>. The existing roads connect all towns (every town can reach every other). Two towns may be joined by several roads.</p><p>Then <code>newRoads[j] = [a, b, w]</code> are built one after another. After <em>each</em> new road is added (keeping all earlier roads and all earlier new roads), compute the sum, over all <code>n(n - 1) / 2</code> unordered pairs of different towns, of the shortest route length between them. Return these sums as an array of length <code>newRoads.length</code>, one entry per construction.</p><p>Example: <code>n = 4</code>, <code>roads = [[0,1,5],[1,2,5],[2,3,5]]</code> and <code>newRoads = [[0,3,4],[1,3,1]]</code>. After the first new road the pair distances are 5, 5, 5, 9, 9, 4, which sum to 37. After the second, distances are 5, 1, 4, 5, 9, 5 which sum to 29. The answer is <code>[37, 29]</code>.</p>",
    constraints=["1 &le; n &le; 60", "n - 1 &le; roads.length &le; 500 and the existing roads connect all towns (for n = 1, roads is empty)", "0 &le; newRoads.length &le; 100", "Every road has 0 &le; a, b &lt; n, a &ne; b and 1 &le; w &le; 1,000", "Parallel roads between the same towns are allowed"],
    hints=["Recomputing all shortest paths after every new road would cost O(n<sup>3</sup>) each time, up to 100 times over. Is the old distance table still useful?",
           "Keep the all-pairs matrix <code>d</code>. A shortest route in the new graph either ignores the new road (old value) or uses it exactly once, as a to b or b to a.",
           "For a new road (a, b, w): for every pair (i, j) set <code>d[i][j] = min(d[i][j], d[i][a] + w + d[b][j], d[i][b] + w + d[a][j])</code>, reading the <em>old</em> values of rows a and b (copy them first). That is O(n<sup>2</sup>) per road; then add up the matrix again."],
    editorial=["Run Floyd-Warshall once on the initial graph in O(n<sup>3</sup>). After that, adding an edge can be handled by one extra 'relaxation through the new edge' step, a degenerate version of Floyd-Warshall's inner loop. A new shortest route in the enlarged graph uses the new road at most once (weights are positive, so a route that used it twice would contain a useless cycle). If it uses the road from a to b, its cost is <code>d[i][a] + w + d[b][j]</code> with old distances on both sides, and the opposite direction gives the second formula.",
               "Both formulas must read distances from before this update, because after the update <code>d[i][a]</code> itself may have decreased and mixing old and new values could count the new road twice. Copy the rows of a and b before touching the matrix. The total cost is O(n<sup>3</sup> + q &middot; n<sup>2</sup>), with q at most 100 and n at most 60 this is under a million steps for the update phase, versus roughly twenty million if you re-ran Floyd-Warshall for every query. The sum itself is O(n<sup>2</sup>) per query as well."],
    time="O(n<sup>3</sup> + q &middot; n<sup>2</sup>)", space="O(n<sup>2</sup>)",
    solution='''def distanceSumsAfterRoads(n, roads, newRoads):
    INF = 10 ** 15
    d = [[INF] * n for _ in range(n)]
    for i in range(n):
        d[i][i] = 0
    for a, b, w in roads:
        if w < d[a][b]:
            d[a][b] = d[b][a] = w
    for k in range(n):
        dk = d[k]
        for i in range(n):
            dik = d[i][k]
            if dik < INF:
                d[i] = [x if x <= dik + y else dik + y for x, y in zip(d[i], dk)]
    out = []
    for a, b, w in newRoads:
        if w < d[a][b]:
            da = d[a][:]
            db = d[b][:]
            for i in range(n):
                x = da[i] + w
                y = db[i] + w
                row = [c if c <= x + e else x + e for c, e in zip(d[i], db)]
                d[i] = [c if c <= y + f else y + f for c, f in zip(row, da)]
        out.append(sum(sum(row) for row in d) // 2)
    return out
''',
    tests=_tests,
)


def b_newroads(n, roads, newRoads):
    out = []
    cur = [list(x) for x in roads]
    for nr in newRoads:
        cur.append(list(nr))
        und = [[a, b, w] for a, b, w in cur] + [[b, a, w] for a, b, w in cur]
        total = 0
        for s in range(n):
            d = _bf_dist(n, und, s)
            total += sum(d[s + 1:]) if n > 1 else 0
        out.append(total)
    return out


def g_newroads(r):
    n = r.randint(1, 6)
    if n == 1:
        return [1, [], []]
    init = [[u, v, r.randint(1, 9)] for u, v in _upairs(r, n, n - 1 + r.randint(0, 3), True)]
    if r.random() < 0.3:
        u, v, w = r.choice(init)
        init.append([u, v, r.randint(1, 9)])
    qs = []
    for _ in range(r.randint(1, 5)):
        u, v = r.sample(range(n), 2)
        qs.append([u, v, r.randint(1, 9)])
    return [n, init, qs]


def v_newroads(tests):
    for t in tests:
        n, roads, nr = t["args"]
        assert 1 <= n <= 60 and n - 1 <= len(roads) <= 500 and len(nr) <= 100
        assert _connected_check(n, roads)
        for a, b, w in roads + nr:
            assert 0 <= a < n and 0 <= b < n and a != b and 1 <= w <= 1000
        assert len(t["expected"]) == len(nr)


CHECKS["sum-of-distances-after-each-new-road"] = (b_newroads, g_newroads, "exact")
VALIDATE["sum-of-distances-after-each-new-road"] = v_newroads

# ====================================================================== HARD
# ---------------------------------------------------------------- nodes with unbounded distance
_tests = [
    [5, [[0, 1, 2], [1, 2, -3], [2, 1, 1], [2, 3, 4], [4, 0, 1]], 0],
    [4, [[0, 1, 2], [2, 3, -5], [3, 2, 1]], 0],
    [2, [[0, 1, 1], [1, 0, -2]], 0],
    [1, [], 0],
    [1, [[0, 0, -1]], 0],
    [1, [[0, 0, 0]], 0],
    [3, [[0, 1, 1], [1, 2, 1]], 0],
    [3, [[0, 1, 1], [1, 2, 1], [2, 1, -2]], 1],
    [3, [[0, 1, 1], [1, 2, 1], [2, 1, -2]], 2],
    [5, [[0, 1, 1], [1, 2, -1], [2, 1, 0], [1, 3, 5], [3, 4, 5]], 0],
    [6, [[0, 1, 1], [1, 2, -4], [2, 3, 2], [3, 1, 1], [3, 4, 1], [5, 4, 1]], 0],
    [6, [[0, 1, 1], [1, 2, -4], [2, 3, 2], [3, 1, 1], [3, 4, 1], [5, 4, 1]], 5],
    [4, [[0, 1, -1], [1, 2, -1], [2, 3, -1]], 0],
    [5, [[0, 1, 3], [1, 0, -4], [0, 2, 1], [3, 4, 1], [4, 3, -9]], 2],
]
_r = rnd(8109)


def _unb_case(r, n, m, cycles, src, wlo=-20, whi=30):
    e = _dag_edges(r, n, m, wlo, whi)
    base = [list(x) for x in e]
    for a, b, slack in cycles:
        e = e + [[b, a, -_dag_dist(n, base, a, b) - slack]]
    return [n, _shuffled(r, e), src]


_tests.append(_unb_case(_r, 200, 900, [(100, 112, 1)], 0))
_tests.append(_unb_case(_r, 200, 900, [(100, 112, 1)], 150))
_tests.append(_unb_case(_r, 200, 900, [(100, 112, 1), (20, 27, 1), (150, 158, 1)], 21))
_tests.append(_unb_case(_r, 200, 900, [(100, 112, 0), (30, 36, 2)], 0))
_tests.append(_unb_case(_r, 200, 1200, [(10, 14, 1), (50, 55, 0)], 60))
_tests.append([200, _shuffled(_r, [[i, i + 1, -1] for i in range(199)]), 0])
_tests.append([150, _pot_edges(_r, 150, 1000, 200, 300, loops=True), 4])

add(
    id="nodes-with-unbounded-negative-distance", title="Nodes With Unbounded Negative Distance", diff="Hard", topic="Graphs",
    fn="unboundedNodes", params=[("n", "int"), ("edges", "int[][]"), ("src", "int")], ret="int[]", cmp="exact", tier="extra",
    desc="<p>A directed graph has <code>n</code> nodes labelled <code>0</code> to <code>n - 1</code>; each <code>edges[i] = [from, to, w]</code> is a one-way edge with weight <code>w</code>, possibly negative. A walk may repeat nodes and edges.</p><p>Walk costs are summed edge weights. Starting from <code>src</code>, a node <code>v</code> is called <em>unbounded</em> if walks from <code>src</code> to <code>v</code> can be made as cheap as you like, which happens exactly when some walk from <code>src</code> to <code>v</code> passes through a cycle of negative total weight. Return the labels of all unbounded nodes in increasing order (an empty array if there are none). Nodes that cannot be reached from <code>src</code> are not unbounded, and src itself counts as unbounded if some walk from src back to src passes through a negative cycle.</p><p>Example: <code>n = 5</code>, <code>edges = [[0,1,2],[1,2,-3],[2,1,1],[2,3,4],[4,0,1]]</code>, <code>src = 0</code>. The cycle 1 &rarr; 2 &rarr; 1 has weight -2, so nodes 1 and 2 get cheaper with every lap, and node 3 hangs off node 2. Node 0 is fine (cost 0) and node 4 is unreachable. The answer is <code>[1, 2, 3]</code>.</p>",
    constraints=["1 &le; n &le; 200", "0 &le; edges.length &le; 1,500", "edges[i] = [from, to, w] with 0 &le; from, to &lt; n and -1,000 &le; w &le; 1,000", "Each ordered pair (from, to) appears at most once; from may equal to", "0 &le; src &lt; n"],
    hints=["Plain Bellman-Ford only tells you <em>whether</em> some negative cycle is reachable. You need to know which nodes are affected by it.",
           "After n - 1 rounds of relaxation from src, every node whose distance is still final is correct. If an edge (u, v, w) can still be relaxed, then v can be reached through a negative cycle.",
           "Collect every node v that can still be relaxed after n - 1 rounds (with u reachable), then run a BFS/DFS from all of them along the edges. Every node reached is unbounded, because after reaching the cycle you can loop forever and then continue to it. Sort the result."],
    editorial=["Run n - 1 rounds of Bellman-Ford from src, ignoring edges that start at nodes not yet reached. Nodes that are not influenced by any reachable negative cycle have their true distance by now. Do one more pass and mark each node v for which some edge (u, v, w) with reached u still improves <code>dist[v]</code>. Every such v is unbounded, since a simple route would already be final, so the improvement must come from a walk that uses a negative cycle. Moreover each reachable negative cycle contains at least one such node: if all edges of the cycle satisfied <code>dist[u] + w &ge; dist[v]</code>, adding these inequalities around the cycle would force its weight to be non-negative.",
               "Unboundedness then spreads along edges: if v is unbounded and v &rarr; x is an edge, x is unbounded as well. A single multi-source BFS from the marked nodes reaches exactly the unbounded nodes (every node of a negative cycle is reached from the marked one on it). The algorithm costs O(n &middot; E) for Bellman-Ford plus O(n + E) for the search. A common mistake is marking only the nodes relaxed in the extra pass, which misses downstream nodes such as node 3 in the example."],
    time="O(n &middot; E)", space="O(n + E)",
    solution='''def unboundedNodes(n, edges, src):
    INF = float('inf')
    dist = [INF] * n
    dist[src] = 0
    for _ in range(n - 1):
        changed = False
        for u, v, w in edges:
            if dist[u] != INF and dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
                changed = True
        if not changed:
            return []
    adj = [[] for _ in range(n)]
    for u, v, w in edges:
        adj[u].append(v)
    bad = [False] * n
    stack = []
    for u, v, w in edges:
        if dist[u] != INF and dist[u] + w < dist[v] and not bad[v]:
            bad[v] = True
            stack.append(v)
    while stack:
        u = stack.pop()
        for v in adj[u]:
            if not bad[v]:
                bad[v] = True
                stack.append(v)
    return [v for v in range(n) if bad[v]]
''',
    tests=_tests,
)


def b_unbounded(n, edges, src):
    adj = _adj(n, edges)
    reach = [_reach(n, adj, s) for s in range(n)]
    neg = [c for c in _simple_cycles(n, adj) if c[1] < 0]
    out = []
    for v in range(n):
        for nodes, _, _ in neg:
            c = next(iter(nodes))
            if c in reach[src] and v in reach[c]:
                out.append(v)
                break
    return out


def g_unbounded(r):
    n = r.randint(1, 7)
    m = r.randint(0, n * 2)
    if r.random() < 0.4:
        e = _pot_edges(r, n, m, 5, 6, loops=True)
        if e and r.random() < 0.7:
            e[r.randrange(len(e))][2] -= r.randint(1, 4)
    else:
        e = [[u, v, r.randint(-4, 3)] for u, v in _dpairs(r, n, m, loops=True)]
    return [n, e, r.randrange(n)]


def v_unbounded(tests):
    some = False
    for t in tests:
        n, edges, src = t["args"]
        assert 1 <= n <= 200 and len(edges) <= 1500 and 0 <= src < n
        seen = set()
        for u, v, w in edges:
            assert 0 <= u < n and 0 <= v < n and -1000 <= w <= 1000
            assert (u, v) not in seen
            seen.add((u, v))
        assert t["expected"] == sorted(set(t["expected"]))
        some = some or bool(t["expected"])
    assert some
    assert any(not t["expected"] for t in tests)


CHECKS["nodes-with-unbounded-negative-distance"] = (b_unbounded, g_unbounded, "exact")
VALIDATE["nodes-with-unbounded-negative-distance"] = v_unbounded

# ---------------------------------------------------------------- lightest cycle
_tests = [
    [5, [[0, 1, 1], [1, 2, 2], [2, 3, 3], [3, 0, 4], [0, 2, 10]]],
    [4, [[0, 1, 1], [1, 2, 1], [2, 3, 1]]],
    [3, [[0, 1, 1], [1, 2, 1], [0, 2, 1]]],
    [1, []],
    [2, [[0, 1, 5]]],
    [4, [[0, 1, 1], [1, 2, 1], [0, 2, 1], [2, 3, 1]]],
    [6, [[0, 1, 1], [1, 2, 1], [2, 3, 1], [3, 4, 1], [4, 5, 1], [5, 0, 1]]],
    [6, [[0, 1, 1], [1, 2, 1], [2, 3, 1], [3, 4, 1], [4, 5, 1], [5, 0, 1], [0, 3, 5]]],
    [6, [[0, 1, 1], [1, 2, 1], [2, 3, 1], [3, 4, 1], [4, 5, 1], [5, 0, 1], [0, 3, 1]]],
    [7, [[0, 1, 5], [1, 2, 5], [0, 2, 5], [3, 4, 1], [4, 5, 1], [5, 6, 1], [6, 3, 1]]],
    [5, [[0, 1, 1000], [1, 2, 1000], [2, 3, 1000], [3, 4, 1000], [4, 0, 1000]]],
    [4, [[0, 1, 1], [0, 2, 2], [0, 3, 3], [1, 2, 4], [1, 3, 5], [2, 3, 6]]],
]
_r = rnd(8110)
_tests.append([80, [[i, i + 1, 1000] for i in range(79)]])
_tests.append([80, [[i, i + 1, 100] for i in range(79)] + [[0, 79, 777]]])
_tests.append([80, [[u, v, _r.randint(1, 1000)] for u, v in _upairs(_r, 80, 85, True)]])
_tests.append([80, [[u, v, _r.randint(1, 1000)] for u, v in _upairs(_r, 80, 400)]])
_tests.append([80, [[u, v, _r.randint(1, 1000)] for u, v in _upairs(_r, 80, 1500, True)]])
_tests.append([50, [[u, v, _r.randint(500, 1000)] for u, v in _upairs(_r, 50, 1000, True)]])

add(
    id="lightest-cycle-in-weighted-graph", title="Lightest Cycle in a Weighted Graph", diff="Hard", topic="Graphs",
    fn="lightestCycle", params=[("n", "int"), ("edges", "int[][]")], ret="int", cmp="exact", tier="extra",
    desc="<p>An undirected graph has <code>n</code> nodes labelled <code>0</code> to <code>n - 1</code>. Each <code>edges[i] = [a, b, w]</code> is an edge of positive weight <code>w</code>.</p><p>A <em>simple cycle</em> visits at least three different nodes, returns to its start and never repeats a node or an edge. Return the smallest total weight of any simple cycle in the graph, or <code>-1</code> if the graph has no cycle at all.</p><p>Example: <code>n = 5</code>, <code>edges = [[0,1,1],[1,2,2],[2,3,3],[3,0,4],[0,2,10]]</code>. The square 0-1-2-3 weighs 1 + 2 + 3 + 4 = 10, the triangle 0-1-2 weighs 1 + 2 + 10 = 13 and the triangle 0-2-3 weighs 10 + 3 + 4 = 17, so the answer is <code>10</code>. A graph that is a tree (for instance only the edges <code>[[0,1,1],[1,2,1]]</code>) has answer <code>-1</code>.</p>",
    constraints=["1 &le; n &le; 80", "0 &le; edges.length &le; n(n - 1) / 2", "edges[i] = [a, b, w] with 0 &le; a, b &lt; n, a &ne; b and 1 &le; w &le; 1,000", "No two edges join the same pair of nodes"],
    hints=["A cycle through an edge (u, v) is that edge plus a different route from u back to v. For one edge, how would you find the cheapest such route?",
           "Brute force: for every edge, remove it and run Dijkstra between its endpoints, cost O(E &middot; E log n). Floyd-Warshall can do better by thinking of the <em>highest-numbered node</em> k of a cycle.",
           "During Floyd-Warshall, before allowing k as an intermediate node, <code>d[i][j]</code> is the shortest i-j route using only nodes below k. For all i &ne; j below k with edges to k, the cycle i ~ j - k - i has weight <code>d[i][j] + w(j,k) + w(k,i)</code>. Take the minimum over all k, i, j, then update d with k."],
    editorial=["Order the nodes by label and look at the largest-labelled node k on a lightest cycle. Its two cycle neighbours i and j have smaller labels, and the rest of the cycle is a simple route from i to j that only uses nodes below k. So the cycle weight is at least <code>d_k[i][j] + w(i,k) + w(k,j)</code> where <code>d_k</code> is the shortest-distance table that Floyd-Warshall holds just before it processes k (intermediates restricted to nodes below k). Conversely every such candidate corresponds to a real simple cycle: the shortest i-j route avoids k, is simple, and together with the two edges to k it closes into a cycle with at least three nodes. Therefore the answer is the minimum candidate over all k and all unordered pairs i, j of neighbours of k with labels below k.",
               "Evaluate the candidates for k first, then relax all pairs through k as usual. The candidate loops cost O(n<sup>3</sup>/6) in total and the relaxations O(n<sup>3</sup>), with O(n<sup>2</sup>) space. Do not simply use the full shortest-path matrix: <code>d[i][i]</code> is 0, and going i &rarr; j &rarr; i along the same edge is not a cycle. That is why distinct nodes and the 'strictly below k' restriction (which keeps the i-j route from using k or the same edges) are essential. An alternative is O(n &middot; E log n) by removing each edge in turn and running Dijkstra between its endpoints."],
    time="O(n<sup>3</sup>)", space="O(n<sup>2</sup>)",
    solution='''def lightestCycle(n, edges):
    INF = 10 ** 15
    w = [[INF] * n for _ in range(n)]
    d = [[INF] * n for _ in range(n)]
    for i in range(n):
        d[i][i] = 0
    for a, b, c in edges:
        w[a][b] = w[b][a] = c
        d[a][b] = d[b][a] = c
    best = INF
    for k in range(n):
        wk = w[k]
        nbrs = [i for i in range(k) if wk[i] < INF]
        for x in range(len(nbrs)):
            i = nbrs[x]
            di = d[i]
            for y in range(x):
                j = nbrs[y]
                s = di[j] + wk[i] + wk[j]
                if s < best:
                    best = s
        dk = d[k]
        for i in range(n):
            dik = d[i][k]
            if dik < INF:
                d[i] = [p if p <= dik + q else dik + q for p, q in zip(d[i], dk)]
    return -1 if best >= INF else best
''',
    tests=_tests,
)


def b_lightcycle(n, edges):
    adj = _adj(n, edges, True)
    best = [None]

    def dfs(s, u, seen, total, length):
        for v, w in adj[u]:
            if v == s and length >= 2:
                t = total + w
                if best[0] is None or t < best[0]:
                    best[0] = t
            elif v > s and v not in seen:
                seen.add(v)
                dfs(s, v, seen, total + w, length + 1)
                seen.discard(v)

    for s in range(n):
        dfs(s, s, {s}, 0, 0)
    return -1 if best[0] is None else best[0]


def g_lightcycle(r):
    n = r.randint(1, 7)
    m = r.randint(0, n * (n - 1) // 2) if n >= 2 else 0
    ps = _upairs(r, n, m) if n >= 2 else []
    return [n, [[u, v, r.randint(1, 9)] for u, v in ps]]


def v_lightcycle(tests):
    for t in tests:
        n, edges = t["args"]
        assert 1 <= n <= 80 and len(edges) <= n * (n - 1) // 2
        seen = set()
        for a, b, w in edges:
            assert 0 <= a < n and 0 <= b < n and a != b and 1 <= w <= 1000
            k = (min(a, b), max(a, b))
            assert k not in seen
            seen.add(k)
    assert any(t["expected"] == -1 for t in tests)


CHECKS["lightest-cycle-in-weighted-graph"] = (b_lightcycle, g_lightcycle, "exact")
VALIDATE["lightest-cycle-in-weighted-graph"] = v_lightcycle

# ---------------------------------------------------------------- minimum mean cycle
_tests = [
    [3, [[0, 1, 2], [1, 2, -1], [2, 0, 5]]],
    [4, [[0, 1, 3], [1, 0, -4], [2, 3, 1]]],
    [3, [[0, 1, 1], [1, 2, 1]]],
    [1, []],
    [1, [[0, 0, 7]]],
    [2, [[0, 0, 5], [0, 1, 1], [1, 1, 3]]],
    [3, [[0, 1, 4], [1, 0, 4], [1, 2, 1], [2, 1, 4]]],
    [4, [[0, 1, 1], [1, 2, 1], [2, 3, 1], [3, 0, 1], [0, 2, 0], [2, 0, 3]]],
    [5, [[0, 1, -3], [1, 0, 3], [2, 3, 2], [3, 4, 2], [4, 2, 2]]],
    [3, [[0, 1, 1000], [1, 2, 1000], [2, 0, 1000]]],
    [3, [[0, 1, -1000], [1, 2, -1000], [2, 0, -999]]],
    [4, [[0, 1, 5], [1, 2, -5], [2, 0, 0], [2, 3, -7], [3, 3, -6]]],
    [5, [[0, 1, 2], [1, 0, 2], [2, 3, 1], [3, 2, 3], [4, 4, 2]]],
]
_r = rnd(8111)
_tests.append([100, [[i, (i + 1) % 100, _r.randint(-1000, 1000)] for i in range(100)]])
_tests.append([100, [[u, v, _r.randint(-1000, 1000)] for u, v in _dpairs(_r, 100, 1000, loops=True)]])
_tests.append([100, [[u, v, _r.randint(1, 1000)] for u, v in _dpairs(_r, 100, 800)]])
_tests.append([100, _shuffled(_r, _dag_edges(_r, 100, 900, -1000, 1000))])
_tests.append([100, _shuffled(_r, _close(_dag_edges(_r, 100, 700, 0, 300), 100, 10, 90, -400))])

add(
    id="minimum-mean-cycle", title="Minimum Mean Weight Cycle", diff="Hard", topic="Graphs",
    fn="minimumMeanCycle", params=[("n", "int"), ("edges", "int[][]")], ret="int[]", cmp="exact", tier="extra",
    desc="<p>A directed graph has <code>n</code> nodes labelled <code>0</code> to <code>n - 1</code>; each <code>edges[i] = [from, to, w]</code> is a one-way edge of weight <code>w</code> (negative values allowed). A <em>cycle</em> is a closed walk <code>v0 &rarr; v1 &rarr; &hellip; &rarr; v0</code>; a self-loop is a cycle of one edge. The <em>mean</em> of a cycle is its total weight divided by its number of edges.</p><p>Find the cycle with the smallest mean (nodes of the walk may repeat, but repeating nodes never gives a smaller mean than the best simple cycle). Return that minimum mean as the reduced fraction <code>[p, q]</code> with <code>q &gt; 0</code> and <code>gcd(|p|, q) = 1</code>; the value 0 is written <code>[0, 1]</code>. If the graph has no cycle, return the empty array <code>[]</code>.</p><p>Example: <code>n = 3</code>, <code>edges = [[0,1,2],[1,2,-1],[2,0,5]]</code>. The only cycle has weight 6 and 3 edges, mean 2, answer <code>[2, 1]</code>. For <code>n = 4</code>, <code>edges = [[0,1,3],[1,0,-4],[2,3,1]]</code> the cycle 0 &rarr; 1 &rarr; 0 has mean -1/2, so the answer is <code>[-1, 2]</code>. A graph with only <code>[[0,1,1],[1,2,1]]</code> has no cycle: <code>[]</code>.</p>",
    constraints=["1 &le; n &le; 100", "0 &le; edges.length &le; 1,000", "edges[i] = [from, to, w] with 0 &le; from, to &lt; n and -1,000 &le; w &le; 1,000", "Each ordered pair (from, to) appears at most once; from may equal to"],
    hints=["Compare cycles by mean, not by total weight. Guessing the mean and checking with a negative-cycle test (subtract the guess from every weight) works with binary search on rationals but is awkward to make exact.",
           "Karp's algorithm: let <code>D[k][v]</code> be the cheapest walk with exactly k edges that ends at v and may start anywhere (so <code>D[0][v] = 0</code>). Any walk of n edges contains a cycle.",
           "The minimum mean is the minimum over nodes v with finite <code>D[n][v]</code> of the maximum over k in 0..n-1 of <code>(D[n][v] - D[k][v]) / (n - k)</code>. Compare fractions by cross-multiplication, then reduce by the gcd. If every <code>D[n][v]</code> is infinite, there is no cycle."],
    editorial=["Karp's theorem gives the minimum cycle mean in O(n &middot; E) time with the same table you would use for Bellman-Ford with exact edge counts. Fill <code>D[0][v] = 0</code> for all v (every node may start a walk) and <code>D[k][v] = min over edges (u,v,w) of D[k-1][u] + w</code>. The value <code>D[n][v]</code> is finite only if a walk with n edges ends at v, and any such walk repeats a node and therefore contains a cycle; if no <code>D[n][v]</code> is finite the graph is acyclic.",
               "Karp's formula: <code>mu = min over v of max over k of (D[n][v] - D[k][v]) / (n - k)</code>, taken over nodes v with finite <code>D[n][v]</code> (then all <code>D[k][v]</code>, k &le; n, are finite as well, since a walk of n edges has suffixes of every shorter length). Intuitively, for a node v on the best cycle, the best n-edge walk to v reaches the cycle early and then circles around it, so the maximum over k exposes the cycle's mean. Keep the fractions as integer pairs and compare with cross-multiplication to stay exact; all weights are integers so the result is a rational with denominator at most n. Complexity: O(n &middot; E) time to fill the table, O(n<sup>2</sup>) for the final scan and space."],
    time="O(n &middot; E)", space="O(n<sup>2</sup>)",
    solution='''from math import gcd


def minimumMeanCycle(n, edges):
    INF = 1 << 60
    D = [[INF] * n for _ in range(n + 1)]
    D[0] = [0] * n
    for k in range(1, n + 1):
        prev = D[k - 1]
        cur = D[k]
        for u, v, w in edges:
            if prev[u] < INF and prev[u] + w < cur[v]:
                cur[v] = prev[u] + w
    best = None
    for v in range(n):
        if D[n][v] >= INF:
            continue
        worst = None
        for k in range(n):
            p = D[n][v] - D[k][v]
            q = n - k
            if worst is None or p * worst[1] > worst[0] * q:
                worst = (p, q)
        if best is None or worst[0] * best[1] < best[0] * worst[1]:
            best = worst
    if best is None:
        return []
    g = gcd(abs(best[0]), best[1])
    return [best[0] // g, best[1] // g]
''',
    tests=_tests,
)


def b_meancycle(n, edges):
    adj = _adj(n, edges)
    best = None
    for _, total, length in _simple_cycles(n, adj):
        f = Fraction(total, length)
        if best is None or f < best:
            best = f
    if best is None:
        return []
    return [best.numerator, best.denominator]


def g_meancycle(r):
    n = r.randint(1, 6)
    m = r.randint(0, n * 2)
    e = [[u, v, r.randint(-6, 8)] for u, v in _dpairs(r, n, m, loops=r.random() < 0.5)]
    return [n, e]


def v_meancycle(tests):
    for t in tests:
        n, edges = t["args"]
        assert 1 <= n <= 100 and len(edges) <= 1000
        seen = set()
        for u, v, w in edges:
            assert 0 <= u < n and 0 <= v < n and -1000 <= w <= 1000
            assert (u, v) not in seen
            seen.add((u, v))
        e = t["expected"]
        assert e == [] or (len(e) == 2 and e[1] > 0 and Fraction(e[0], e[1]).denominator == e[1])
    assert any(t["expected"] == [] for t in tests)
    assert any(t["expected"] and t["expected"][0] < 0 for t in tests)


CHECKS["minimum-mean-cycle"] = (b_meancycle, g_meancycle, "exact")
VALIDATE["minimum-mean-cycle"] = v_meancycle
