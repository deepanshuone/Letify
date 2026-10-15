from lib import add, rnd, CHECKS, VALIDATE, gen_arr  # noqa: F401
from itertools import combinations, combinations_with_replacement, permutations

# Problems: advanced graph topics (strong connectivity, cut vertices and bridges, Euler tours,
# 0-1 BFS, state-space BFS and bitmask BFS). See data/lib.py for the registry.

T = "Graphs"


# ------------------------------------------------------------------ shared helpers (tests only)
def _all_pairs(n, directed):
    if directed:
        return [(u, v) for u in range(n) for v in range(n) if u != v]
    return [(u, v) for u in range(n) for v in range(u + 1, n)]


def _rand_edges(r, n, m, directed):
    """m distinct edges on labels 0..n-1 (undirected edges get a random orientation), shuffled."""
    maxm = n * (n - 1) if directed else n * (n - 1) // 2
    m = min(m, maxm)
    if n <= 40:
        chosen = r.sample(_all_pairs(n, directed), m)
    else:
        s = set()
        while len(s) < m:
            u, v = r.randrange(n), r.randrange(n)
            if u == v:
                continue
            if not directed and u > v:
                u, v = v, u
            s.add((u, v))
        chosen = sorted(s)
    out = []
    for u, v in chosen:
        out.append([u, v] if directed or r.random() < 0.5 else [v, u])
    r.shuffle(out)
    return out


def _relabel(r, n, pairs, directed):
    """Apply a random relabelling to a set/list of pairs; undirected pairs get a random orientation."""
    perm = list(range(n))
    r.shuffle(perm)
    out = []
    for u, v in pairs:
        a, b = perm[u], perm[v]
        out.append([a, b] if directed or r.random() < 0.5 else [b, a])
    r.shuffle(out)
    return out


def _tree_pairs(r, n, window):
    """Random tree on 0..n-1: the parent of v is one of the `window` nodes before it (small window = deep tree)."""
    return {(r.randrange(max(0, v - window), v), v) for v in range(1, n)}


def _add_random_pairs(r, n, pairs, k):
    pairs = set(pairs)
    maxm = n * (n - 1) // 2
    target = min(len(pairs) + k, maxm)
    while len(pairs) < target:
        u, v = r.randrange(n), r.randrange(n)
        if u != v:
            pairs.add((min(u, v), max(u, v)))
    return pairs


def _cactus_pairs(r, ncycles, lo=3, hi=6):
    """Chain of cycles glued at single vertices. Returns (n, pairs)."""
    n = 1
    pairs = set()
    for _ in range(ncycles):
        a = r.randrange(max(0, n - 6), n)
        L = r.randint(lo, hi)
        ring = [a] + list(range(n, n + L - 1))
        n += L - 1
        for i in range(L):
            x, y = ring[i], ring[(i + 1) % L]
            pairs.add((min(x, y), max(x, y)))
    return n, pairs


def _planted(r, n, k, chords, forward):
    """n nodes split into k non-empty groups. Every group is a directed cycle (plus `chords` extra edges inside
    groups), and `forward` extra edges go only from a lower-numbered group to a higher one, so the groups are
    exactly the strongly connected components. Nodes are shuffled. Returns the edge list."""
    nodes = list(range(n))
    r.shuffle(nodes)
    groups = [[nodes[g]] for g in range(k)]
    for x in nodes[k:]:
        groups[r.randrange(k)].append(x)
    s = set()
    for g in groups:
        if len(g) > 1:
            for i in range(len(g)):
                s.add((g[i], g[(i + 1) % len(g)]))
    for _ in range(chords):
        g = r.choice(groups)
        if len(g) >= 3:
            u, v = r.sample(g, 2)
            s.add((u, v))
    if k >= 2:
        for _ in range(forward):
            a, b = sorted(r.sample(range(k), 2))
            s.add((r.choice(groups[a]), r.choice(groups[b])))
    out = [list(e) for e in sorted(s)]
    r.shuffle(out)
    return out


def _closure(n, edges):
    """Warshall closure with bitmasks: reach[i] has bit j set when j is reachable from i."""
    reach = [1 << i for i in range(n)]
    for u, v in edges:
        reach[u] |= 1 << v
    for k in range(n):
        bk = reach[k]
        for i in range(n):
            if reach[i] >> k & 1:
                reach[i] |= bk
    return reach


def _is_strong(n, edges):
    full = (1 << n) - 1
    return all(x == full for x in _closure(n, edges))


def _undirected_components(n, edges, removed=None):
    """Number of connected components of the graph without the vertex `removed`."""
    parent = list(range(n))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for u, v in edges:
        if u == removed or v == removed:
            continue
        parent[find(u)] = find(v)
    return len({find(x) for x in range(n) if x != removed})


def _check_graph(t, nmax, mmax, directed, connected=False):
    n, edges = t["args"][0], t["args"][1]
    assert 1 <= n <= nmax and len(edges) <= mmax, "size"
    seen = set()
    for e in edges:
        assert len(e) == 2 and 0 <= e[0] < n and 0 <= e[1] < n and e[0] != e[1], ("bad edge", e)
        k = (e[0], e[1]) if directed else (min(e), max(e))
        assert k not in seen, ("duplicate edge", e)
        seen.add(k)
    if connected:
        assert _undirected_components(n, edges) == 1, "graph must be connected"


def _both_answers(tests):
    vals = {t["expected"] for t in tests}
    assert vals == {True, False}, "need both answers"


# =================================================================== EASY
# ---------------------------------------------------------------- strongly connected?
p = add(
    id="is-digraph-strongly-connected", title="Is the Network Strongly Connected", diff="Easy", topic=T, tier="common",
    fn="isStronglyConnected", params=[("n", "int"), ("edges", "int[][]")], ret="bool", cmp="exact",
    desc="<p>A town has <code>n</code> junctions numbered <code>0</code> to <code>n - 1</code> and a set of one-way streets. Each entry <code>edges[i] = [u, v]</code> is a street that can only be driven from junction <code>u</code> to junction <code>v</code>.</p><p>Return <code>true</code> if for every ordered pair of junctions <code>(a, b)</code> it is possible to drive from <code>a</code> to <code>b</code>, and <code>false</code> otherwise.</p><pre>n = 4, edges = [[0,1],[1,2],[2,3],[3,0],[1,3]]  -> true\nn = 3, edges = [[0,1],[1,2],[0,2]]              -> false  (no street leads back to junction 0)\nn = 1, edges = []                               -> true</pre>",
    constraints=["1 &le; n &le; 5,000", "0 &le; edges.length &le; 10,000", "0 &le; u, v &lt; n and u &ne; v", "No ordered pair [u, v] is listed twice"],
    hints=["Running a search from every junction would work but costs n searches. Can you get away with far fewer?",
           "If junction 0 can reach everybody and everybody can reach junction 0, then any a can reach any b by driving through 0.",
           "Run one search from 0 following the streets as given, and a second search from 0 on the graph with every street reversed. Both searches must visit all n junctions."],
    editorial=["Pick any junction as a hub, say 0. The network is strongly connected exactly when 0 can reach every junction <em>and</em> every junction can reach 0. If both hold, a trip from a to b is a trip from a to 0 followed by a trip from 0 to b. If one fails, some pair is clearly disconnected, so the answer is false.",
               "The first condition is an ordinary DFS or BFS from 0. The second is the same search on the reversed graph (every edge <code>u -> v</code> turned into <code>v -> u</code>), because a path from a to 0 in the original graph is a path from 0 to a in the reversed one.",
               "Two linear searches give O(n + m) time. Searching from every junction would be O(n (n + m)). This hub trick is also the first step of Kosaraju's algorithm for strongly connected components."],
    time="O(n + m)", space="O(n + m)",
    solution='''def isStronglyConnected(n, edges):
    fwd = [[] for _ in range(n)]
    back = [[] for _ in range(n)]
    for u, v in edges:
        fwd[u].append(v)
        back[v].append(u)

    def reaches_all(adj):
        seen = [False] * n
        seen[0] = True
        stack = [0]
        count = 1
        while stack:
            u = stack.pop()
            for v in adj[u]:
                if not seen[v]:
                    seen[v] = True
                    count += 1
                    stack.append(v)
        return count == n

    return reaches_all(fwd) and reaches_all(back)
''',
    tests=[[4, [[0, 1], [1, 2], [2, 3], [3, 0], [1, 3]]],
           [3, [[0, 1], [1, 2], [0, 2]]],
           [1, []],
           [2, [[0, 1]]],
           [2, [[0, 1], [1, 0]]],
           [5, [[0, 1], [1, 2], [2, 0], [2, 3], [3, 4]]],
           [4, [[0, 1], [1, 2], [2, 3], [3, 2], [2, 1], [1, 0]]],
           [4, [[0, 1], [1, 2], [2, 3], [3, 1]]],
           [3, [[1, 0], [2, 1], [0, 2]]],
           [6, [[0, 1], [1, 2], [2, 0], [3, 4], [4, 5], [5, 3], [2, 3]]],
           [5, [[0, 1], [0, 2], [0, 3], [0, 4]]],
           [5, [[0, 1], [1, 0], [0, 2], [2, 0], [0, 3], [3, 0], [0, 4], [4, 0]]]],
)
_r = rnd(12001)
_n = 1800
p["tests"].append([_n, _planted(_r, _n, 1, 1200, 0)])                       # one big cycle plus chords: true
_e = _planted(_r, _n, 2, 1200, 600)                                         # two big cycles, one-way links: false
p["tests"].append([_n, _e])
_e = _planted(_r, _n, 1, 1000, 0)                                           # cycle, but one node loses all incoming edges
_hole = _e[0][1]
_e = [e for e in _e if e[1] != _hole]
p["tests"].append([_n, _e])


def b_strong(n, edges):
    return _is_strong(n, edges)


def g_strong(r):
    n = r.randint(1, 7)
    if r.random() < 0.5:
        order = list(range(n))
        r.shuffle(order)
        es = {(order[i], order[(i + 1) % n]) for i in range(n) if n > 1}
        for _ in range(r.randint(0, n)):
            if n > 1:
                u, v = r.sample(range(n), 2)
                es.add((u, v))
        if es and r.random() < 0.5:
            es.discard(r.choice(sorted(es)))
        edges = [list(e) for e in sorted(es)]
        r.shuffle(edges)
    else:
        edges = _rand_edges(r, n, int(r.choice([0.1, 0.2, 0.35, 0.5]) * n * (n - 1)), True)
    return [n, edges]


def v_strong(tests):
    for t in tests:
        _check_graph(t, 5000, 10000, True)
    _both_answers(tests)


CHECKS["is-digraph-strongly-connected"] = (b_strong, g_strong, "exact")
VALIDATE["is-digraph-strongly-connected"] = v_strong

# ---------------------------------------------------------------- Euler circuit exists
p = add(
    id="eulerian-circuit-exists", title="Closed Tour Over Every Road", diff="Easy", topic=T, tier="common",
    fn="hasClosedTour", params=[("n", "int"), ("edges", "int[][]")], ret="bool", cmp="exact",
    desc="<p>A town has <code>n</code> junctions numbered <code>0</code> to <code>n - 1</code> and two-way roads, where <code>edges[i] = [u, v]</code> joins junctions <code>u</code> and <code>v</code>.</p><p>An inspector wants a <em>closed tour</em>: start at some junction, drive along <strong>every road exactly once</strong>, and end at the junction where the tour began. Return <code>true</code> if such a tour exists, otherwise <code>false</code>.</p><p>Junctions with no roads are simply ignored. If there are no roads at all, the (empty) tour exists and the answer is <code>true</code>.</p><pre>n = 5, edges = [[0,1],[1,2],[2,0],[2,3],[3,4],[4,2]]  -> true   (two triangles sharing junction 2)\nn = 3, edges = [[0,1],[1,2]]                          -> false  (junctions 0 and 2 have one road each)\nn = 6, edges = [[0,1],[1,2],[2,0],[3,4],[4,5],[5,3]]  -> false  (two separate triangles)</pre>",
    constraints=["1 &le; n &le; 5,000", "0 &le; edges.length &le; 10,000", "0 &le; u, v &lt; n and u &ne; v", "No road is listed twice (in either direction)"],
    hints=["Think about a single junction in the middle of the tour. Every time the tour arrives there along one road, it must leave along a different one.",
           "So every junction must have an even number of roads. Is that already enough? Look at two separate triangles.",
           "The roads must also all lie in one connected piece. Check that all junctions with degree greater than 0 are connected (ignoring isolated junctions) and that every degree is even. Union-find or one DFS does the connectivity check."],
    editorial=["This is Euler's theorem for circuits: a graph has a closed walk that uses every edge exactly once if and only if (1) every vertex has even degree and (2) all vertices with at least one edge lie in the same connected component.",
               "Necessity: inside the tour each visit to a vertex uses one road to enter and another to leave, so the roads at a vertex are used in pairs; the start vertex pairs its first departure with the final arrival. The tour is also a single walk, so it cannot jump between components.",
               "Sufficiency follows from Hierholzer's algorithm: with all degrees even, you can never get stuck anywhere except at the start, so you can keep splicing closed loops together until every road is used.",
               "Implementation: count degrees, check parity, union the endpoints of every road, then verify that all junctions with degree &gt; 0 share one root. Time is O((n + m) &alpha;(n)), essentially linear."],
    time="O(n + m)", space="O(n)",
    solution='''def hasClosedTour(n, edges):
    if not edges:
        return True
    deg = [0] * n
    parent = list(range(n))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for u, v in edges:
        deg[u] += 1
        deg[v] += 1
        ru, rv = find(u), find(v)
        if ru != rv:
            parent[ru] = rv
    if any(d % 2 for d in deg):
        return False
    root = find(edges[0][0])
    return all(find(v) == root for v in range(n) if deg[v] > 0)
''',
    tests=[[5, [[0, 1], [1, 2], [2, 0], [2, 3], [3, 4], [4, 2]]],
           [3, [[0, 1], [1, 2]]],
           [6, [[0, 1], [1, 2], [2, 0], [3, 4], [4, 5], [5, 3]]],
           [1, []],
           [4, []],
           [3, [[0, 1], [1, 2], [2, 0]]],
           [2, [[0, 1]]],
           [4, [[0, 1], [1, 2], [2, 3], [3, 0]]],
           [5, [[0, 1], [1, 2], [2, 3], [3, 0], [0, 2]]],
           [6, [[4, 5], [5, 1], [1, 4]]],
           [5, [[0, 1], [0, 2], [0, 3], [0, 4]]],
           [6, [[0, 1], [1, 2], [2, 0], [0, 3], [3, 4], [4, 0], [0, 5], [5, 1], [1, 3], [3, 5]]]],
)


def _xor_cycle(es, nodes):
    for i in range(len(nodes)):
        a, b = nodes[i], nodes[(i + 1) % len(nodes)]
        k = (min(a, b), max(a, b))
        if k in es:
            es.remove(k)
        else:
            es.add(k)


def _edge_bearing_connected(n, es):
    ends = {x for e in es for x in e}
    if not ends:
        return True
    parent = {x: x for x in ends}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for a, b in es:
        parent[find(a)] = find(b)
    return len({find(x) for x in ends}) == 1


def _big_even_graph(r, n, pool_size, ncycles):
    """Connected graph with all degrees even: a Hamiltonian cycle on a node pool, then random short cycles XOR-ed in."""
    while True:
        pool = r.sample(range(n), pool_size)
        es = set()
        _xor_cycle(es, pool[:])
        for _ in range(ncycles):
            _xor_cycle(es, r.sample(pool, r.randint(3, 12)))
        if _edge_bearing_connected(n, es):
            return pool, es


_r = rnd(12002)
_n = 3000
_pool, _es = _big_even_graph(_r, _n, 1200, 160)
p["tests"].append([_n, _relabel(_r, _n, sorted(_es), False)])                      # true (isolated junctions ignored)
_free = [x for x in range(_n) if x not in set(_pool)]
_es2 = set(_es)
_xor_cycle(_es2, _free[:3])                                                         # extra separate triangle: false
p["tests"].append([_n, _relabel(_r, _n, sorted(_es2), False)])
_es3 = set(_es)
while True:                                                                         # one extra road: two odd junctions
    _a, _b = _r.sample(_pool, 2)
    if (min(_a, _b), max(_a, _b)) not in _es3:
        _es3.add((min(_a, _b), max(_a, _b)))
        break
p["tests"].append([_n, _relabel(_r, _n, sorted(_es3), False)])
_pool, _es = _big_even_graph(_r, 2000, 2000, 120)
p["tests"].append([2000, _relabel(_r, 2000, sorted(_es), False)])                  # every junction used: true


def b_euler(n, edges):
    m = len(edges)
    if m == 0:
        return True
    adj = [[] for _ in range(n)]
    for i, (u, v) in enumerate(edges):
        adj[u].append((v, i))
        adj[v].append((u, i))
    used = [False] * m
    start = edges[0][0]

    def go(cur, cnt):
        if cnt == m:
            return cur == start
        for v, i in adj[cur]:
            if not used[i]:
                used[i] = True
                ok = go(v, cnt + 1)
                used[i] = False
                if ok:
                    return True
        return False

    return go(start, 0)


def g_euler(r):
    while True:
        n = r.randint(1, 6)
        es = set()
        if n >= 3:
            for _ in range(r.randint(0, 3)):
                _xor_cycle(es, r.sample(range(n), r.randint(3, n)))
        if n >= 2 and r.random() < 0.3:
            u, v = r.sample(range(n), 2)
            k = (min(u, v), max(u, v))
            if k in es:
                es.remove(k)
            else:
                es.add(k)
        if len(es) <= 8:
            return [n, _relabel(r, n, sorted(es), False)]


def v_euler(tests):
    for t in tests:
        _check_graph(t, 5000, 10000, False)
    _both_answers(tests)


CHECKS["eulerian-circuit-exists"] = (b_euler, g_euler, "exact")
VALIDATE["eulerian-circuit-exists"] = v_euler

# =================================================================== MEDIUM
# ---------------------------------------------------------------- count SCCs
p = add(
    id="count-strongly-connected-components", title="Count Strongly Connected Components", diff="Medium", topic=T, tier="common",
    fn="countComponents", params=[("n", "int"), ("edges", "int[][]")], ret="int", cmp="exact",
    desc="<p>A directed graph has <code>n</code> nodes numbered <code>0</code> to <code>n - 1</code>. Each entry <code>edges[i] = [u, v]</code> is an edge from <code>u</code> to <code>v</code>.</p><p>Two nodes <code>a</code> and <code>b</code> belong to the same <em>strongly connected component</em> if <code>a</code> can reach <code>b</code> and <code>b</code> can reach <code>a</code> by following edges (every node is in the same component as itself). Return the number of strongly connected components.</p><pre>n = 5, edges = [[0,1],[1,2],[2,0],[1,3],[3,4]]  -> 3   ({0,1,2}, {3}, {4})\nn = 4, edges = []                               -> 4\nn = 3, edges = [[0,1],[1,2],[2,0]]              -> 1</pre>",
    constraints=["1 &le; n &le; 5,000", "0 &le; edges.length &le; 10,000", "0 &le; u, v &lt; n and u &ne; v", "No ordered pair [u, v] is listed twice"],
    hints=["Start with small cases: in a directed acyclic graph every node is its own component. What does a cycle do?",
           "A DFS finishes a node only after everything reachable from it has been explored. The node that finishes last in the whole DFS lies in a component that no other component can reach.",
           "Use Kosaraju (DFS to record finishing order, then DFS on the reversed graph in decreasing finishing order, counting the number of DFS starts) or Tarjan (keep a stack, an index and a low-link per node, and close a component when low == index). Write the DFS with an explicit stack, since a path can be 5,000 nodes long."],
    editorial=["Tarjan's algorithm does one DFS. Every node gets a discovery index and a low-link value, the smallest discovery index reachable from its DFS subtree using at most one edge that goes back to a node still on the component stack. Nodes are pushed on a stack when discovered. When a node finishes with <code>low == index</code>, it is the root of a component: pop the stack down to that node and count one component.",
               "Kosaraju's algorithm gets the same count with two passes: first a DFS on the original graph to compute finishing order, then a DFS on the reversed graph that starts from nodes in decreasing finishing order. Every start of the second pass discovers exactly one new component, because the reversed edges cannot leave a component whose finishing time is the largest among those not yet taken.",
               "Both run in O(n + m). An explicit stack instead of recursion keeps the long-path inputs safe."],
    time="O(n + m)", space="O(n + m)",
    solution='''def countComponents(n, edges):
    adj = [[] for _ in range(n)]
    for u, v in edges:
        adj[u].append(v)
    index = [-1] * n
    low = [0] * n
    on_stack = [False] * n
    stack = []
    counter = 0
    comps = 0
    for root in range(n):
        if index[root] != -1:
            continue
        index[root] = low[root] = counter
        counter += 1
        stack.append(root)
        on_stack[root] = True
        work = [(root, 0)]
        while work:
            u, i = work.pop()
            if i < len(adj[u]):
                work.append((u, i + 1))
                v = adj[u][i]
                if index[v] == -1:
                    index[v] = low[v] = counter
                    counter += 1
                    stack.append(v)
                    on_stack[v] = True
                    work.append((v, 0))
                elif on_stack[v] and index[v] < low[u]:
                    low[u] = index[v]
            else:
                if low[u] == index[u]:
                    comps += 1
                    while True:
                        w = stack.pop()
                        on_stack[w] = False
                        if w == u:
                            break
                if work:
                    parent = work[-1][0]
                    if low[u] < low[parent]:
                        low[parent] = low[u]
    return comps
''',
    tests=[[5, [[0, 1], [1, 2], [2, 0], [1, 3], [3, 4]]],
           [4, []],
           [3, [[0, 1], [1, 2], [2, 0]]],
           [1, []],
           [4, [[0, 1], [1, 2], [2, 3]]],
           [6, [[0, 1], [1, 0], [2, 3], [3, 2], [4, 5], [5, 4], [1, 2], [3, 4]]],
           [7, [[0, 1], [1, 2], [2, 0], [2, 3], [3, 4], [4, 5], [5, 3], [5, 6]]],
           [5, [[0, 1], [0, 2], [0, 3], [0, 4], [1, 0], [2, 0], [3, 0], [4, 0]]],
           [6, [[5, 4], [4, 3], [3, 2], [2, 1], [1, 0], [0, 5]]],
           [8, [[0, 1], [1, 2], [2, 3], [3, 0], [4, 5], [5, 6], [6, 7], [7, 4], [0, 4], [3, 6], [1, 5]]]],
)
_r = rnd(12003)
_n = 1800
_e = _planted(_r, _n, 650, 80, 500)
p["tests"].append([_n, _e])
p["tests"].append([1800, _rand_edges(_r, 1800, 2000, True)])
_perm = list(range(1800))
_r.shuffle(_perm)
p["tests"].append([1800, [[_perm[i], _perm[i + 1]] for i in range(1799)]])         # one long path: 1800 components
p["tests"].append([1800, [[_perm[i], _perm[(i + 1) % 1800]] for i in range(1800)]])  # one long cycle: 1 component


def b_scc(n, edges):
    reach = _closure(n, edges)
    count = 0
    for i in range(n):
        if not any((reach[i] >> j & 1) and (reach[j] >> i & 1) for j in range(i)):
            count += 1
    return count


def g_scc(r):
    n = r.randint(1, 8)
    if r.random() < 0.4:
        k = r.randint(1, n)
        return [n, _planted(r, n, k, r.randint(0, 2), r.randint(0, 2 * k))]
    return [n, _rand_edges(r, n, int(r.choice([0.05, 0.1, 0.2, 0.3]) * n * (n - 1)), True)]


def v_scc(tests):
    for t in tests:
        _check_graph(t, 5000, 10000, True)


CHECKS["count-strongly-connected-components"] = (b_scc, g_scc, "exact")
VALIDATE["count-strongly-connected-components"] = v_scc

# ---------------------------------------------------------------- cut vertices
p = add(
    id="cut-vertices-of-a-network", title="Cut Vertices of a Network", diff="Medium", topic=T, tier="common",
    fn="cutVertices", params=[("n", "int"), ("edges", "int[][]")], ret="int[]", cmp="exact",
    desc="<p>A network has <code>n</code> servers numbered <code>0</code> to <code>n - 1</code> and bidirectional cables, where <code>edges[i] = [u, v]</code> connects servers <code>u</code> and <code>v</code>. The network is not necessarily connected.</p><p>A server is a <em>single point of failure</em> (a cut vertex) if switching it off, together with all its cables, increases the number of connected groups of the remaining servers. Return all such servers in increasing order.</p><pre>n = 6, edges = [[0,1],[1,2],[2,0],[1,3],[3,4],[3,5]]  -> [1,3]\nn = 4, edges = [[0,1],[1,2],[2,3],[3,0]]              -> []    (a ring has no weak point)\nn = 5, edges = [[0,1],[1,2]]                          -> [1]   (servers 3 and 4 are isolated)</pre>",
    constraints=["1 &le; n &le; 5,000", "0 &le; edges.length &le; 10,000", "0 &le; u, v &lt; n and u &ne; v", "No cable is listed twice (in either direction)"],
    hints=["The brute force removes every server and recounts the groups, which is O(n (n + m)). Look for a single pass.",
           "Run a DFS and give every node a discovery time. For a node v, find the smallest discovery time that v's DFS subtree can reach with a single non-tree edge (its low-link).",
           "A non-root node u is a cut vertex when some DFS child v has <code>low[v] &ge; disc[u]</code>: the subtree of v cannot get around u. The DFS root is a cut vertex exactly when it has two or more DFS children. Use an explicit stack because the DFS can be 5,000 levels deep."],
    editorial=["Do a DFS over every component and record <code>disc[u]</code> (when u is first reached) and <code>low[u]</code> (the smallest discovery time reachable from u's subtree using tree edges downward and at most one back edge). Back edges connect a node to an ancestor, and the edge back to the direct parent is not counted.",
               "Take a non-root node u and a DFS child v. All of v's subtree can reach something strictly above u exactly when <code>low[v] &lt; disc[u]</code>. If instead <code>low[v] &ge; disc[u]</code>, deleting u cuts v's subtree off from the rest of the component, so u is a cut vertex. Any one such child is enough.",
               "The root has nothing above it, so it is a cut vertex precisely when it has at least two DFS children (those children's subtrees are unconnected once the root is removed).",
               "The whole thing is one DFS, O(n + m). Isolated servers and leaves are never cut vertices."],
    time="O(n + m)", space="O(n + m)",
    solution='''def cutVertices(n, edges):
    adj = [[] for _ in range(n)]
    for u, v in edges:
        adj[u].append(v)
        adj[v].append(u)
    disc = [-1] * n
    low = [0] * n
    is_cut = [False] * n
    timer = 0
    for root in range(n):
        if disc[root] != -1:
            continue
        disc[root] = low[root] = timer
        timer += 1
        root_children = 0
        work = [(root, -1, 0)]
        while work:
            u, parent, i = work.pop()
            if i < len(adj[u]):
                work.append((u, parent, i + 1))
                v = adj[u][i]
                if v == parent:
                    continue
                if disc[v] == -1:
                    disc[v] = low[v] = timer
                    timer += 1
                    if u == root:
                        root_children += 1
                    work.append((v, u, 0))
                elif disc[v] < low[u]:
                    low[u] = disc[v]
            elif work:
                p = work[-1][0]
                if low[u] < low[p]:
                    low[p] = low[u]
                if p != root and low[u] >= disc[p]:
                    is_cut[p] = True
        if root_children >= 2:
            is_cut[root] = True
    return [v for v in range(n) if is_cut[v]]
''',
    tests=[[6, [[0, 1], [1, 2], [2, 0], [1, 3], [3, 4], [3, 5]]],
           [4, [[0, 1], [1, 2], [2, 3], [3, 0]]],
           [5, [[0, 1], [1, 2]]],
           [1, []],
           [2, [[0, 1]]],
           [5, [[0, 1], [0, 2], [0, 3], [0, 4]]],
           [7, [[0, 1], [1, 2], [2, 0], [2, 3], [3, 4], [4, 5], [5, 3], [5, 6]]],
           [6, [[0, 1], [1, 2], [2, 3], [3, 4], [4, 5]]],
           [8, [[0, 1], [1, 2], [2, 0], [3, 4], [4, 5], [5, 3], [6, 7]]],
           [6, [[0, 1], [0, 2], [1, 2], [1, 3], [2, 3], [3, 4], [3, 5], [4, 5]]],
           [5, [[0, 1], [0, 2], [0, 3], [0, 4], [1, 2], [2, 3], [3, 4], [4, 1]]]],
)
_r = rnd(12004)
p["tests"].append([2300, _relabel(_r, 2300, _add_random_pairs(_r, 2300, _tree_pairs(_r, 2300, 4), 30), False)])   # deep tree plus a few cycles
_nc, _pc = _cactus_pairs(_r, 600)
p["tests"].append([_nc, _relabel(_r, _nc, _pc, False)])                                                              # chain of cycles
p["tests"].append([2300, _relabel(_r, 2300, _add_random_pairs(_r, 2300, _tree_pairs(_r, 2300, 2300), 300), False)])  # random tree plus chords


def b_cutv(n, edges):
    base = _undirected_components(n, edges)
    return [v for v in range(n) if _undirected_components(n, edges, removed=v) > base]


def g_cutv(r):
    n = r.randint(1, 9)
    if r.random() < 0.5 and n >= 2:
        pairs = _add_random_pairs(r, n, _tree_pairs(r, n, r.randint(1, n)), r.randint(0, 3))
        if r.random() < 0.4 and pairs:
            pairs = set(sorted(pairs)[:-1])
        return [n, _relabel(r, n, sorted(pairs), False)]
    return [n, _rand_edges(r, n, int(r.choice([0.1, 0.2, 0.35]) * n * (n - 1) / 2), False)]


def v_cutv(tests):
    for t in tests:
        _check_graph(t, 5000, 10000, False)
        assert t["expected"] == sorted(set(t["expected"]))
    assert any(t["expected"] for t in tests) and any(not t["expected"] for t in tests)


CHECKS["cut-vertices-of-a-network"] = (b_cutv, g_cutv, "exact")
VALIDATE["cut-vertices-of-a-network"] = v_cutv

# ---------------------------------------------------------------- open the lock
p = add(
    id="open-the-combination-lock", title="Open the Combination Lock", diff="Medium", topic=T, tier="common",
    fn="openLock", params=[("deadends", "int[]"), ("target", "int")], ret="int", cmp="exact",
    desc="<p>A lock has four wheels, each showing a digit from 0 to 9. A combination is written as an integer from <code>0</code> to <code>9999</code> whose four digits are the wheels, with leading zeros understood: <code>7</code> means wheels 0-0-0-7 and <code>120</code> means 0-1-2-0. The lock starts at combination <code>0</code> (0-0-0-0).</p><p>One move turns a single wheel one step up or one step down, and wheels wrap around: one step up from 9 gives 0 and one step down from 0 gives 9.</p><p>The combinations in <code>deadends</code> jam the lock. As soon as the wheels show one of them, the lock is stuck, so a dead-end combination can never be passed through. Return the minimum number of moves needed to reach <code>target</code>, or <code>-1</code> if it is impossible. (If the starting combination <code>0</code> itself is a dead end, or the target is, the answer is <code>-1</code>.)</p><pre>deadends = [2],             target = 3        -> 5   (0000, 0010, 0011, 0012, 0013, 0003)\ndeadends = [],              target = 5555     -> 20\ndeadends = [1,9,10,90,100,900,1000,9000], target = 5 -> -1  (all 8 neighbours of 0000 are jammed)</pre>",
    constraints=["0 &le; deadends.length &le; 9,999", "0 &le; deadends[i], target &le; 9,999", "All values in deadends are distinct", "target may equal 0 (answer 0 if 0 is not a dead end)"],
    hints=["Treat every combination as a node of a graph with 10,000 nodes. Which nodes are adjacent to a given one?",
           "Every combination has exactly 8 neighbours (4 wheels times 2 directions). All moves cost the same, so you want the fewest edges from node 0 to the target.",
           "Breadth-first search from 0, never entering a dead end, stopping when the target is reached. Handle the special cases where 0 or the target is a dead end first. A visited array of size 10,000 keeps the search linear."],
    editorial=["The set of combinations forms an unweighted graph where each node has 8 neighbours. A breadth-first search from <code>0</code> explores combinations in order of distance, so the first time the target is dequeued or discovered, that distance is the minimum number of moves.",
               "Treat dead ends exactly like visited cells: put them in a set (or mark them in a boolean array) before starting, and never push them. If 0 is a dead end nothing can start, and if the target is a dead end it can never be entered, so both return -1 immediately. A target of 0 needs zero moves.",
               "To extract the digits of a combination use <code>(x // 10**k) % 10</code>; to turn a wheel replace that digit by <code>(d + 1) % 10</code> or <code>(d + 9) % 10</code>. The graph has at most 10,000 nodes and 80,000 edges, so the search is instantaneous. A bidirectional search would cut the explored area further but is not needed here."],
    time="O(10^4 &middot; 8)", space="O(10^4)",
    solution='''from collections import deque


def openLock(deadends, target):
    dead = [False] * 10000
    for d in deadends:
        dead[d] = True
    if dead[0] or dead[target]:
        return -1
    if target == 0:
        return 0
    dist = [-1] * 10000
    dist[0] = 0
    queue = deque([0])
    while queue:
        cur = queue.popleft()
        for p in (1, 10, 100, 1000):
            digit = cur // p % 10
            base = cur - digit * p
            for nd in ((digit + 1) % 10, (digit + 9) % 10):
                nxt = base + nd * p
                if dist[nxt] == -1 and not dead[nxt]:
                    dist[nxt] = dist[cur] + 1
                    if nxt == target:
                        return dist[nxt]
                    queue.append(nxt)
    return -1
''',
    tests=[[[2], 3],
           [[], 5555],
           [[1, 9, 10, 90, 100, 900, 1000, 9000], 5],
           [[], 0],
           [[0], 5],
           [[1234], 1234],
           [[3], 3],
           [[], 9],
           [[1, 9], 99],
           [[1, 10, 100, 1000, 9, 90, 900], 9000],
           [[5, 15, 25, 35, 45, 55, 65, 75, 85, 95, 105, 205, 305], 6000]],
)
_r = rnd(12005)
_ring = [x for x in (1, 9, 10, 90, 100, 900, 1000, 9000)]
_dense = [v for v in range(1, 10000) if v != 8888 and _r.random() < 0.62]
p["tests"].append([_dense, 8888])                                                    # random maze of jammed combinations
_wall = [v for v in range(10000) if (v // 1000) % 10 == 5 and v % 10 != 3]            # a wall of jammed combinations with a single gap
p["tests"].append([_wall, 9999])
_walk = [v for v in range(10000) if (v // 100) % 10 == 5 and (v % 100) != 37]
p["tests"].append([_walk, 4444])


def b_lock(deadends, target):
    dead = {tuple(int(c) for c in "%04d" % d) for d in deadends}
    start = (0, 0, 0, 0)
    goal = tuple(int(c) for c in "%04d" % target)
    if start in dead or goal in dead:
        return -1
    seen = {start}
    level = {start}
    steps = 0
    while level:
        if goal in level:
            return steps
        nxt = set()
        for s in level:
            for w in range(4):
                for delta in (1, 9):
                    t = list(s)
                    t[w] = (t[w] + delta) % 10
                    t = tuple(t)
                    if t not in seen and t not in dead:
                        seen.add(t)
                        nxt.add(t)
        level = nxt
        steps += 1
    return -1


def g_lock(r):
    target = r.randrange(10000) if r.random() < 0.7 else r.randrange(100)
    mode = r.random()
    if mode < 0.35:
        dens = r.choice([0.0, 0.2, 0.4, 0.55, 0.7])
        dead = [v for v in range(10000) if r.random() < dens and v != target]
    elif mode < 0.7:
        dead = r.sample(range(10000), r.randint(0, 40))
    else:
        # jam most neighbours of 0 or of the target
        centre = r.choice([0, target])
        nb = []
        for p10 in (1, 10, 100, 1000):
            d = centre // p10 % 10
            for nd in ((d + 1) % 10, (d + 9) % 10):
                nb.append(centre - d * p10 + nd * p10)
        dead = [v for v in nb if r.random() < 0.8 and v != target and v != 0]
        dead += [v for v in r.sample(range(10000), r.randint(0, 3000)) if v != 0 and v != target]
        dead = sorted(set(dead))
    if r.random() < 0.04:
        dead = sorted(set(dead) | {0})
    r.shuffle(dead)
    return [dead, target]


def v_lock(tests):
    for t in tests:
        d, target = t["args"]
        assert len(d) <= 9999 and len(set(d)) == len(d)
        assert all(0 <= x <= 9999 for x in d) and 0 <= target <= 9999
    vals = [t["expected"] for t in tests]
    assert any(v == -1 for v in vals) and max(vals) >= 15 and any(0 < v <= 5 for v in vals)


CHECKS["open-the-combination-lock"] = (b_lock, g_lock, "exact")
VALIDATE["open-the-combination-lock"] = v_lock

# ---------------------------------------------------------------- sliding puzzle 2x3
p = add(
    id="sliding-puzzle-two-by-three", title="Two-by-Three Sliding Puzzle", diff="Medium", topic=T, tier="common",
    fn="slidingPuzzle", params=[("board", "int[][]")], ret="int", cmp="exact",
    desc="<p>A sliding puzzle is played on a board with 2 rows and 3 columns. Five tiles are numbered <code>1</code> to <code>5</code> and one square is empty, written as <code>0</code>.</p><p>A move slides a tile that is orthogonally next to the empty square into the empty square (equivalently, the empty square swaps with a neighbour). The puzzle is solved when the board reads exactly <code>[[1,2,3],[4,5,0]]</code>.</p><p>Given the starting <code>board</code>, return the minimum number of moves needed to solve the puzzle, or <code>-1</code> if it cannot be solved.</p><pre>board = [[1,2,3],[4,0,5]]  -> 1\nboard = [[1,2,3],[5,4,0]]  -> -1\nboard = [[4,1,2],[5,0,3]]  -> 5</pre>",
    constraints=["board has 2 rows and 3 columns", "board contains each of 0, 1, 2, 3, 4, 5 exactly once"],
    hints=["Describe the whole board by a single value, for example the six digits written in row order. How many different boards exist?",
           "There are only 6! = 720 boards. Each board is a node, and each legal move is an edge to another board. Moves all cost 1.",
           "Run a BFS from the starting board over strings like <code>'412503'</code>; the empty square swaps with the squares next to it. Return the depth when you meet <code>'123450'</code>, or -1 if the search runs out of new boards."],
    editorial=["This is shortest path in an implicit graph. A state is the arrangement of the six values, for instance the string read row by row. From a state, the empty square at index <code>z</code> can swap with its neighbours, and the neighbours of each of the six indices can be hard-coded: <code>[1,3], [0,2,4], [1,5], [0,4], [1,3,5], [2,4]</code>.",
               "BFS from the starting board visits states in order of their number of moves, so the first time the goal string appears the depth is the answer. If the queue empties, the goal is unreachable and the answer is -1. Exactly half of the 720 arrangements are solvable (a parity argument on tile inversions), so about half the inputs end in -1; BFS discovers this by exhausting the 360 reachable boards.",
               "The state space is tiny, so the search takes microseconds. The same approach scales to other sizes only while the number of states stays manageable (a 3 x 3 board already has 181,440 reachable states)."],
    time="O(6!)", space="O(6!)",
    solution='''def slidingPuzzle(board):
    start = ''.join(str(x) for row in board for x in row)
    goal = '123450'
    if start == goal:
        return 0
    nbr = [(1, 3), (0, 2, 4), (1, 5), (0, 4), (1, 3, 5), (2, 4)]
    seen = {start}
    frontier = [start]
    steps = 0
    while frontier:
        steps += 1
        nxt = []
        for s in frontier:
            z = s.index('0')
            for j in nbr[z]:
                t = list(s)
                t[z], t[j] = t[j], t[z]
                t = ''.join(t)
                if t not in seen:
                    if t == goal:
                        return steps
                    seen.add(t)
                    nxt.append(t)
        frontier = nxt
    return -1
''',
    tests=[[[[1, 2, 3], [4, 0, 5]]],
           [[[1, 2, 3], [5, 4, 0]]],
           [[[4, 1, 2], [5, 0, 3]]],
           [[[1, 2, 3], [4, 5, 0]]],
           [[[1, 2, 3], [0, 4, 5]]],
           [[[0, 1, 2], [4, 5, 3]]],
           [[[3, 2, 1], [0, 5, 4]]],
           [[[1, 2, 0], [4, 5, 3]]],
           [[[2, 1, 3], [4, 5, 0]]],
           [[[4, 5, 0], [1, 2, 3]]],
           [[[4, 5, 0], [3, 2, 1]]],
           [[[2, 3, 5], [1, 0, 4]]]],
)

_SP = {}


def _sp_table():
    """Distance to the solved board for every arrangement, by repeated relaxation over all 720 permutations."""
    if not _SP:
        states = list(permutations(range(6)))
        INF = 99
        dist = {s: INF for s in states}
        dist[(1, 2, 3, 4, 5, 0)] = 0
        changed = True
        while changed:
            changed = False
            for s in states:
                z = s.index(0)
                r0, c0 = divmod(z, 3)
                for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    r1, c1 = r0 + dr, c0 + dc
                    if 0 <= r1 < 2 and 0 <= c1 < 3:
                        t = list(s)
                        j = r1 * 3 + c1
                        t[z], t[j] = t[j], t[z]
                        t = tuple(t)
                        if dist[t] + 1 < dist[s]:
                            dist[s] = dist[t] + 1
                            changed = True
        _SP.update({s: (d if d < INF else -1) for s, d in dist.items()})
    return _SP


def b_slide(board):
    return _sp_table()[tuple(x for row in board for x in row)]


def g_slide(r):
    a = list(range(6))
    r.shuffle(a)
    return [[a[:3], a[3:]]]


def v_slide(tests):
    for t in tests:
        b = t["args"][0]
        assert len(b) == 2 and all(len(row) == 3 for row in b)
        assert sorted(x for row in b for x in row) == list(range(6))
    vals = [t["expected"] for t in tests]
    assert -1 in vals and max(vals) >= 18 and 0 in vals


CHECKS["sliding-puzzle-two-by-three"] = (b_slide, g_slide, "exact")
VALIDATE["sliding-puzzle-two-by-three"] = v_slide

# ---------------------------------------------------------------- 0-1 BFS on arrow grid
_ARROW = {1: (0, 1), 2: (0, -1), 3: (1, 0), 4: (-1, 0)}

p = add(
    id="min-arrow-changes-to-reach-corner", title="Fewest Arrow Changes to Reach the Corner", diff="Medium", topic=T, tier="common",
    fn="minArrowChanges", params=[("grid", "int[][]")], ret="int", cmp="exact",
    desc="<p>Every cell of the <code>grid</code> holds an arrow: <code>1</code> points right, <code>2</code> points left, <code>3</code> points down and <code>4</code> points up. A traveller starts in the top-left cell and, in each step, moves to the neighbouring cell in the direction of the arrow in the cell they stand on. The walk is meant to end in the bottom-right cell.</p><p>You may change the arrow in any cell to any of the four directions; changing one cell costs <code>1</code> (a cell is changed at most once). Arrows are allowed to point out of the grid as long as the traveller never actually follows such an arrow.</p><p>Return the minimum number of cells you must change so that the traveller starting in the top-left cell reaches the bottom-right cell.</p><pre>grid = [[1,1,3],\n        [2,4,2],\n        [1,1,1]]  -> 1   (redirect the arrow in the middle of the right column)\ngrid = [[2,2],\n        [2,2]]    -> 2\ngrid = [[4]]       -> 0</pre>",
    constraints=["1 &le; rows, cols &le; 60", "1 &le; grid[r][c] &le; 4"],
    hints=["Think of cells as nodes of a graph: from each cell you can step to its up to four neighbours. What does a step cost?",
           "A step in the direction of the cell's own arrow is free, any other step costs 1 (you change the arrow). So you want the cheapest path where every edge costs 0 or 1.",
           "Use Dijkstra, or the faster 0-1 BFS: keep a deque, push a neighbour reached by a cost-0 edge at the front and one reached by a cost-1 edge at the back. The distance of the bottom-right cell is the answer."],
    editorial=["Model the grid as a weighted graph: from cell (r, c) there is an edge to each in-grid neighbour, with weight 0 if the arrow in (r, c) points to that neighbour and weight 1 otherwise. A path of total weight W corresponds to a plan that changes exactly W arrows along that path. Conversely, any plan for which the traveller arrives walks along a path that never repeats a cell (a repeat would make the traveller loop forever), so its number of changes is at least the weight of that path. Hence the answer is the shortest path from the top-left to the bottom-right cell.",
               "With only weights 0 and 1, Dijkstra's heap is unnecessary. In 0-1 BFS you use a double-ended queue: when relaxing an edge of weight 0, push the neighbour on the <em>front</em>, otherwise on the <em>back</em>. The deque then always holds nodes in nondecreasing distance order (it contains at most two distinct distance values), exactly like BFS does for unit weights.",
               "Each cell is relaxed a bounded number of times, so the time is O(rows &times; cols). When processing a popped cell, read its current best distance from the table, because a cell may be pushed twice."],
    time="O(R &middot; C)", space="O(R &middot; C)",
    solution='''from collections import deque


def minArrowChanges(grid):
    R, C = len(grid), len(grid[0])
    INF = float('inf')
    dist = [[INF] * C for _ in range(R)]
    dist[0][0] = 0
    moves = ((1, 0, 1), (2, 0, -1), (3, 1, 0), (4, -1, 0))
    dq = deque([(0, 0)])
    while dq:
        r, c = dq.popleft()
        d = dist[r][c]
        for k, dr, dc in moves:
            nr, nc = r + dr, c + dc
            if 0 <= nr < R and 0 <= nc < C:
                w = 0 if grid[r][c] == k else 1
                if d + w < dist[nr][nc]:
                    dist[nr][nc] = d + w
                    if w == 0:
                        dq.appendleft((nr, nc))
                    else:
                        dq.append((nr, nc))
    return dist[R - 1][C - 1]
''',
    tests=[[[[1, 1, 3], [2, 4, 2], [1, 1, 1]]],
           [[[2, 2], [2, 2]]],
           [[[4]]],
           [[[1, 1, 1], [1, 1, 1]]],
           [[[2, 2, 2, 2]]],
           [[[1, 1, 1, 1]]],
           [[[3], [3], [3]]],
           [[[4], [4], [4]]],
           [[[1, 1, 3], [3, 3, 3], [3, 3, 3]]],
           [[[1, 2, 1, 2], [2, 1, 2, 1], [1, 2, 1, 2]]],
           [[[3, 4, 3, 4], [3, 4, 3, 4], [3, 4, 3, 4], [1, 1, 1, 1]]]],
)
_r = rnd(12006)


def _snake_grid(r, R, C, flips, noise=True):
    """Grid with a zig-zag path of correct arrows from the top-left to the bottom-right cell; `flips` of the path
    arrows are then redirected. Cells outside the path get random arrows."""
    g = [[r.randint(1, 4) for _ in range(C)] for _ in range(R)]
    path = []
    for i in range(R):
        cols = range(C) if i % 2 == 0 else range(C - 1, -1, -1)
        for j in cols:
            path.append((i, j))
    for a in range(len(path) - 1):
        (i, j), (x, y) = path[a], path[a + 1]
        g[i][j] = {(0, 1): 1, (0, -1): 2, (1, 0): 3, (-1, 0): 4}[(x - i, y - j)]
    for _ in range(flips):
        i, j = r.choice(path[:-1])
        g[i][j] = r.randint(1, 4)
    return g


p["tests"].append([[[r_ for r_ in (_r.randint(1, 4) for _ in range(60))] for _ in range(60)]])
p["tests"].append([_snake_grid(_r, 60, 60, 0)])
p["tests"].append([_snake_grid(_r, 59, 60, 25)])
p["tests"].append([[[2 if _r.random() < 0.6 else 4 for _ in range(60)] for _ in range(50)]])


def b_arrows(grid):
    R, C = len(grid), len(grid[0])
    best = [10 ** 9]
    seen = [[False] * C for _ in range(R)]

    def dfs(r, c, cost):
        if cost >= best[0]:
            return
        if r == R - 1 and c == C - 1:
            best[0] = cost
            return
        seen[r][c] = True
        for k, (dr, dc) in _ARROW.items():
            nr, nc = r + dr, c + dc
            if 0 <= nr < R and 0 <= nc < C and not seen[nr][nc]:
                dfs(nr, nc, cost + (grid[r][c] != k))
        seen[r][c] = False

    dfs(0, 0, 0)
    return best[0]


def g_arrows(r):
    R, C = r.randint(1, 4), r.randint(1, 4)
    return [[[r.randint(1, 4) for _ in range(C)] for _ in range(R)]]


def v_arrows(tests):
    for t in tests:
        g = t["args"][0]
        assert 1 <= len(g) <= 60 and all(len(row) == len(g[0]) for row in g) and 1 <= len(g[0]) <= 60
        assert all(1 <= x <= 4 for row in g for x in row)
    vals = [t["expected"] for t in tests]
    assert 0 in vals and max(vals) >= 5


CHECKS["min-arrow-changes-to-reach-corner"] = (b_arrows, g_arrows, "exact")
VALIDATE["min-arrow-changes-to-reach-corner"] = v_arrows

# ---------------------------------------------------------------- lamps (bitmask BFS)
p = add(
    id="min-presses-to-turn-off-all-lamps", title="Switch Off All the Lamps", diff="Medium", topic=T, tier="extra",
    fn="minPresses", params=[("lamps", "int[][]")], ret="int", cmp="exact",
    desc="<p>A control panel is a grid of lamps; <code>lamps[r][c]</code> is <code>1</code> if that lamp is on and <code>0</code> if it is off. Every lamp is also a button. Pressing the button at <code>(r, c)</code> toggles that lamp and each of its orthogonal neighbours (up, down, left, right, when they exist): lamps that were on go off and lamps that were off go on.</p><p>Return the minimum number of button presses needed to turn every lamp off, or <code>-1</code> if it is impossible.</p><pre>lamps = [[0,0],[0,1]]     -> 3\nlamps = [[1,0,1]]         -> 2   (press the two outer lamps)\nlamps = [[1,0,0],[1,0,0]] -> -1</pre>",
    constraints=["1 &le; rows, cols and rows &times; cols &le; 12", "lamps[r][c] is 0 or 1"],
    hints=["What matters about the panel at any moment? Is there a compact way to describe the entire state?",
           "The state is one of at most 2<sup>12</sup> = 4,096 on/off patterns, so it fits in a 12-bit integer. A press is an XOR with a fixed mask. Pressing the same button twice cancels out.",
           "BFS over states: start from the initial pattern, apply every button mask with XOR, and stop when the pattern becomes 0. If the queue runs dry, return -1. Return 0 right away when everything is already off."],
    editorial=["Encode the panel as a bitmask, bit <code>r * cols + c</code> being the lamp at (r, c). Each button has a fixed mask (its own bit plus the bits of its neighbours), and pressing it replaces the state <code>s</code> by <code>s ^ mask</code>. This turns the puzzle into an unweighted shortest-path problem on at most 4,096 states, with one edge per button from each state.",
               "A breadth-first search from the starting pattern finds the fewest presses to reach the all-zero pattern. Keep a set (or array) of visited patterns so that every state is expanded once. The cost is states &times; buttons, at most 4,096 &times; 12.",
               "Because pressing the same button twice cancels, order does not matter and every button is used at most once in an optimal solution, so enumerating all 2<sup>buttons</sup> subsets also works for these sizes. BFS is the version that generalises when presses interact in more complicated ways."],
    time="O(2^(R&middot;C) &middot; R &middot; C)", space="O(2^(R&middot;C))",
    solution='''def minPresses(lamps):
    R, C = len(lamps), len(lamps[0])
    start = 0
    for i in range(R):
        for j in range(C):
            if lamps[i][j]:
                start |= 1 << (i * C + j)
    if start == 0:
        return 0
    masks = []
    for i in range(R):
        for j in range(C):
            m = 1 << (i * C + j)
            for di, dj in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                a, b = i + di, j + dj
                if 0 <= a < R and 0 <= b < C:
                    m |= 1 << (a * C + b)
            masks.append(m)
    seen = {start}
    frontier = [start]
    steps = 0
    while frontier:
        steps += 1
        nxt = []
        for s in frontier:
            for m in masks:
                t = s ^ m
                if t == 0:
                    return steps
                if t not in seen:
                    seen.add(t)
                    nxt.append(t)
        frontier = nxt
    return -1
''',
    tests=[[[[0, 0], [0, 1]]],
           [[[1, 0, 1]]],
           [[[1, 0, 0], [1, 0, 0]]],
           [[[0]]],
           [[[1]]],
           [[[1, 1]]],
           [[[1, 1, 1], [1, 1, 1], [1, 1, 1]]],
           [[[0, 1, 0], [1, 1, 1], [0, 1, 0]]],
           [[[1, 0, 0], [0, 0, 0], [0, 0, 1]]],
           [[[1, 1, 0, 1], [0, 1, 1, 0], [1, 0, 0, 1]]],
           [[[1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 1]]],
           [[[1, 0], [0, 1], [1, 0], [0, 1], [1, 0], [0, 1]]],
           [[[1, 1, 1, 1], [1, 0, 0, 1], [1, 1, 1, 1]]]],
)


def b_lamps(lamps):
    R, C = len(lamps), len(lamps[0])
    cells = [(i, j) for i in range(R) for j in range(C)]
    best = -1
    for sub in range(1 << len(cells)):
        g = [row[:] for row in lamps]
        for b, (i, j) in enumerate(cells):
            if sub >> b & 1:
                for di, dj in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)):
                    a, c = i + di, j + dj
                    if 0 <= a < R and 0 <= c < C:
                        g[a][c] ^= 1
        if not any(any(row) for row in g):
            k = bin(sub).count("1")
            if best == -1 or k < best:
                best = k
    return best


def g_lamps(r):
    R = r.randint(1, 3)
    C = r.randint(1, 12 // R if R else 1)
    C = min(C, 4)
    return [[[1 if r.random() < r.choice([0.2, 0.5]) else 0 for _ in range(C)] for _ in range(R)]]


def v_lamps(tests):
    for t in tests:
        g = t["args"][0]
        assert 1 <= len(g) and all(len(row) == len(g[0]) for row in g) and 1 <= len(g) * len(g[0]) <= 12
        assert all(x in (0, 1) for row in g for x in row)
    vals = [t["expected"] for t in tests]
    assert -1 in vals and 0 in vals and max(vals) >= 4


CHECKS["min-presses-to-turn-off-all-lamps"] = (b_lamps, g_lamps, "exact")
VALIDATE["min-presses-to-turn-off-all-lamps"] = v_lamps

# =================================================================== HARD
# ---------------------------------------------------------------- reconstruct itinerary
p = add(
    id="reconstruct-flight-itinerary", title="Reconstruct the Flight Itinerary", diff="Hard", topic=T, tier="must",
    fn="findItinerary", params=[("tickets", "int[][]")], ret="int[]", cmp="exact",
    desc="<p>Airports are numbered with non-negative integers. Each ticket <code>tickets[i] = [from, to]</code> is a one-way flight from airport <code>from</code> to airport <code>to</code>. The same ticket can appear several times, and each copy is a separate flight.</p><p>A traveller starts at airport <code>0</code> and wants to use <strong>every ticket exactly once</strong>, taking each flight from where the previous one landed. At least one such itinerary is guaranteed to exist.</p><p>Return the itinerary as the list of visited airports (the airport 0 at the start, then the destination of each flight). If several itineraries exist, return the lexicographically smallest one, comparing airport numbers as integers from left to right.</p><pre>tickets = [[0,1],[1,2],[2,0],[0,3]]        -> [0,1,2,0,3]\ntickets = [[0,2],[2,0],[0,1]]              -> [0,2,0,1]   (going to 1 first would strand the traveller)\ntickets = [[0,1],[1,0],[0,1],[1,2]]        -> [0,1,0,1,2]</pre>",
    constraints=["1 &le; tickets.length &le; 5,000", "0 &le; from, to &le; 999", "At least one itinerary starting at 0 that uses every ticket once exists"],
    hints=["Using each ticket exactly once is an Euler path problem in a directed multigraph. A greedy 'always take the smallest next airport' idea gets stuck sometimes - see the second example.",
           "Backtracking (try the smallest destination, undo if the itinerary cannot be completed) is correct but can be exponential. Think about what the stuck airport looks like: it is where the whole itinerary must end.",
           "Hierholzer's algorithm: run a DFS that always takes the smallest unused outgoing ticket, and append an airport to the answer only when it has no unused tickets left (post-order). Reverse the collected list at the end."],
    editorial=["The tickets are edges of a directed multigraph and an itinerary is an Euler path starting at 0. Hierholzer's algorithm builds one in linear time: from the current airport, follow unused tickets (here in increasing order of destination) until you get stuck, and when an airport has nothing left to leave through, move it to the output and step back. The finished output is the itinerary in reverse.",
               "Why does this yield the lexicographically smallest itinerary? When the DFS at some airport takes the smallest ticket, either the rest of the itinerary can be completed through it, in which case it is the right choice, or it leads into the airport where the whole route must finish, which is a dead end. The dead end is emitted first in the reversed order, i.e. it ends up last, and the traveller returns to finish the other tickets, exactly as the second example shows ([0,2,0,1] instead of the stuck [0,1]).",
               "Store the destinations of each airport sorted in descending order so that <code>pop()</code> gives the smallest one in O(1). Sorting costs O(E log E) and the DFS (written with an explicit stack to avoid deep recursion) is O(E), so the total is O(E log E)."],
    time="O(E log E)", space="O(E)",
    solution='''def findItinerary(tickets):
    graph = {}
    for a, b in tickets:
        graph.setdefault(a, []).append(b)
    for a in graph:
        graph[a].sort(reverse=True)
    route = []
    stack = [0]
    while stack:
        u = stack[-1]
        out = graph.get(u)
        if out:
            stack.append(out.pop())
        else:
            route.append(stack.pop())
    route.reverse()
    return route
''',
    tests=[[[[0, 1], [1, 2], [2, 0], [0, 3]]],
           [[[0, 2], [2, 0], [0, 1]]],
           [[[0, 1], [1, 0], [0, 1], [1, 2]]],
           [[[0, 5]]],
           [[[0, 0]]],
           [[[0, 0], [0, 0], [0, 1]]],
           [[[0, 3], [3, 4], [4, 0], [0, 1], [1, 5], [5, 1], [1, 0]]],
           [[[0, 1], [0, 2], [2, 3], [3, 0], [1, 2], [2, 1]]],
           [[[0, 4], [4, 5], [5, 0], [0, 2], [2, 4], [4, 6], [6, 0]]],
           [[[3, 0], [0, 3], [3, 2], [2, 3], [0, 1], [1, 0]]],
           [[[0, 1], [1, 2], [2, 3], [3, 1], [1, 4], [4, 5], [5, 1]]]],
)


def _walk_tickets(r, n, steps, window=None):
    cur = 0
    out = []
    for _ in range(steps):
        nxt = r.randrange(n)
        out.append([cur, nxt])
        cur = nxt
    r.shuffle(out)
    return out


_r = rnd(12007)
p["tests"].append([_walk_tickets(_r, 30, 2200)])                       # few airports, many repeated tickets
p["tests"].append([_walk_tickets(_r, 900, 2200)])                      # many airports, mostly distinct tickets
p["tests"].append([_walk_tickets(_r, 3, 2400)])                        # three airports, heavy multi-edges
_t = []
for _i in range(1, 800):                                               # long loops hanging off airport 0 + one dead-end spur
    _t += [[0, _i], [_i, 0]]
_t += [[0, 801], [801, 802]]
_r.shuffle(_t)
p["tests"].append([_t])


def b_itin(tickets):
    t = sorted(tuple(x) for x in tickets)
    used = [False] * len(t)
    path = [0]

    def dfs(cur):
        if len(path) == len(t) + 1:
            return True
        prev = None
        for i, (a, b) in enumerate(t):
            if used[i] or a != cur or b == prev:
                continue
            prev = b
            used[i] = True
            path.append(b)
            if dfs(b):
                return True
            path.pop()
            used[i] = False
        return False

    dfs(0)
    return path


def g_itin(r):
    n = r.randint(1, 4)
    return [_walk_tickets(r, n, r.randint(1, 8))]


def v_itin(tests):
    for t in tests:
        tk, route = t["args"][0], t["expected"]
        assert 1 <= len(tk) <= 5000
        assert all(0 <= a <= 999 and 0 <= b <= 999 for a, b in tk)
        assert route[0] == 0 and len(route) == len(tk) + 1
        assert sorted(zip(route, route[1:])) == sorted(tuple(x) for x in tk), "itinerary must use every ticket once"


CHECKS["reconstruct-flight-itinerary"] = (b_itin, g_itin, "exact")
VALIDATE["reconstruct-flight-itinerary"] = v_itin

# ---------------------------------------------------------------- make network bridgeless
p = add(
    id="min-edges-to-make-network-bridgeless", title="Make the Network Bridge-Free", diff="Hard", topic=T, tier="extra",
    fn="minNewCables", params=[("n", "int"), ("edges", "int[][]")], ret="int", cmp="exact",
    desc="<p>A connected network has <code>n</code> servers numbered <code>0</code> to <code>n - 1</code> and bidirectional cables, where <code>edges[i] = [u, v]</code> joins servers <code>u</code> and <code>v</code>. A cable is a <em>bridge</em> if cutting it would split the network into two disconnected parts.</p><p>You may install new cables between any two distinct servers; a new cable may run parallel to an existing one. Return the minimum number of new cables so that the network has <strong>no bridge</strong>, i.e. it stays connected after any single cable is cut.</p><pre>n = 4, edges = [[0,1],[1,2],[2,3]]              -> 1   (a path; join its two ends)\nn = 5, edges = [[0,1],[0,2],[0,3],[0,4]]        -> 2   (a star with 4 leaves)\nn = 4, edges = [[0,1],[1,2],[2,0],[2,3]]        -> 1   (triangle with a pendant server)</pre>",
    constraints=["1 &le; n &le; 5,000", "n - 1 &le; edges.length &le; 10,000", "0 &le; u, v &lt; n and u &ne; v", "No cable is listed twice; the network is connected"],
    hints=["Cables on a cycle are never bridges. Start by finding all bridges (DFS with discovery times and low-links). What do the pieces between bridges look like?",
           "Contract every group of servers that stay connected without the bridges (a 2-edge-connected component) into one node. The bridges then form a tree. Which nodes of that tree are the weakest?",
           "A leaf of the bridge tree has exactly one bridge, and a new cable has only two ends, so each new cable can protect at most two leaves. The answer is ceil(leaves / 2), or 0 when there are no bridges at all."],
    editorial=["Find all bridges with a DFS using discovery times and low-links: a tree edge from parent <code>p</code> to child <code>c</code> is a bridge when <code>low[c] &gt; disc[p]</code>. Then merge the servers joined by non-bridge cables (union-find, or a component labelling). Every group is a 2-edge-connected component, and contracting each group to one node turns the network into a tree whose edges are the bridges (the <em>bridge tree</em>).",
               "Let L be the number of leaves of this tree (components with exactly one bridge). If the tree is a single node there is no bridge and the answer is 0. Otherwise, every leaf needs a new cable with an end inside it, because its only bridge must end up on a cycle, and a cable has just two ends, so at least ceil(L / 2) cables are needed.",
               "That many are also enough: pair up the leaves (taking them in depth-first order and pairing the i-th with the (i + L/2)-th for even L, adding one more to any leaf when L is odd) and join each pair. Every bridge then lies on a cycle created by one of the new cables. For a tree with two nodes (L = 2) a single parallel cable does the job, which is why parallel cables are allowed.",
               "The whole algorithm is linear: one DFS, one union-find pass and one degree count over the bridges. The DFS is written with an explicit stack so that long chains of servers do not overflow the recursion limit."],
    time="O(n + m)", space="O(n + m)",
    solution='''def minNewCables(n, edges):
    m = len(edges)
    adj = [[] for _ in range(n)]
    for i, (u, v) in enumerate(edges):
        adj[u].append((v, i))
        adj[v].append((u, i))
    disc = [-1] * n
    low = [0] * n
    is_bridge = [False] * m
    disc[0] = low[0] = 0
    timer = 1
    work = [(0, -1, 0)]
    while work:
        u, pe, i = work.pop()
        if i < len(adj[u]):
            work.append((u, pe, i + 1))
            v, e = adj[u][i]
            if e == pe:
                continue
            if disc[v] == -1:
                disc[v] = low[v] = timer
                timer += 1
                work.append((v, e, 0))
            elif disc[v] < low[u]:
                low[u] = disc[v]
        elif work:
            parent = work[-1][0]
            if low[u] < low[parent]:
                low[parent] = low[u]
            if low[u] > disc[parent]:
                is_bridge[pe] = True
    root = list(range(n))

    def find(x):
        while root[x] != x:
            root[x] = root[root[x]]
            x = root[x]
        return x

    for i, (u, v) in enumerate(edges):
        if not is_bridge[i]:
            root[find(u)] = find(v)
    deg = {}
    for i, (u, v) in enumerate(edges):
        if is_bridge[i]:
            a, b = find(u), find(v)
            deg[a] = deg.get(a, 0) + 1
            deg[b] = deg.get(b, 0) + 1
    leaves = sum(1 for d in deg.values() if d == 1)
    return (leaves + 1) // 2
''',
    tests=[[4, [[0, 1], [1, 2], [2, 3]]],
           [5, [[0, 1], [0, 2], [0, 3], [0, 4]]],
           [4, [[0, 1], [1, 2], [2, 0], [2, 3]]],
           [1, []],
           [2, [[0, 1]]],
           [3, [[0, 1], [1, 2], [2, 0]]],
           [3, [[0, 1], [1, 2]]],
           [6, [[0, 1], [1, 2], [2, 0], [3, 4], [4, 5], [5, 3], [2, 3]]],
           [7, [[0, 1], [1, 2], [2, 0], [2, 3], [3, 4], [4, 5], [5, 3], [4, 6]]],
           [6, [[0, 1], [1, 2], [2, 3], [3, 4], [4, 5], [1, 4]]],
           [7, [[0, 1], [0, 2], [1, 3], [1, 4], [2, 5], [2, 6]]],
           [7, [[0, 1], [1, 2], [2, 0], [3, 4], [4, 5], [5, 3], [0, 6], [6, 3]]]],
)
_r = rnd(12008)
p["tests"].append([2200, _relabel(_r, 2200, _add_random_pairs(_r, 2200, _tree_pairs(_r, 2200, 2200), 40), False)])   # random tree with a few cycles
_nc, _pc = _cactus_pairs(_r, 600, 3, 5)
_pc = set(_pc)
_big = _nc
for _i in range(100):                                                                                                # cycles chain plus pendant paths
    _a = _r.randrange(_big)
    _pc.add((_a, _big))
    _big += 1
p["tests"].append([_big, _relabel(_r, _big, _pc, False)])
p["tests"].append([2200, _relabel(_r, 2200, _tree_pairs(_r, 2200, 6), False)])                                       # deep tree: all edges are bridges
p["tests"].append([2200, _relabel(_r, 2200, {(0, i) for i in range(1, 2200)}, False)])                               # star: 2199 leaves -> 1100


def b_bridgeless(n, edges):
    def ok(es):
        for skip in range(len(es)):
            parent = list(range(n))

            def find(x):
                while parent[x] != x:
                    parent[x] = parent[parent[x]]
                    x = parent[x]
                return x

            for j, (u, v) in enumerate(es):
                if j != skip:
                    parent[find(u)] = find(v)
            if len({find(x) for x in range(n)}) > 1:
                return False
        return True

    pairs = _all_pairs(n, False)
    for k in range(0, n + 1):
        for add_ in combinations_with_replacement(pairs, k):
            if ok([tuple(e) for e in edges] + list(add_)):
                return k


def g_bridgeless(r):
    n = r.randint(1, 6)
    pairs = _tree_pairs(r, n, r.randint(1, max(1, n)))
    pairs = _add_random_pairs(r, n, pairs, r.choice([0, 0, 1, 2, 3]))
    return [n, _relabel(r, n, sorted(pairs), False)]


def v_bridgeless(tests):
    for t in tests:
        _check_graph(t, 5000, 10000, False, connected=True)
    vals = [t["expected"] for t in tests]
    assert 0 in vals and max(vals) >= 3


CHECKS["min-edges-to-make-network-bridgeless"] = (b_bridgeless, g_bridgeless, "exact")
VALIDATE["min-edges-to-make-network-bridgeless"] = v_bridgeless

# ---------------------------------------------------------------- strongly connect with fewest new edges
p = add(
    id="min-edges-to-strongly-connect", title="Make the One-Way Network Strongly Connected", diff="Hard", topic=T, tier="extra",
    fn="minNewStreets", params=[("n", "int"), ("edges", "int[][]")], ret="int", cmp="exact",
    desc="<p>A town has <code>n</code> junctions numbered <code>0</code> to <code>n - 1</code> and one-way streets, where <code>edges[i] = [u, v]</code> can only be driven from junction <code>u</code> to junction <code>v</code>. The council may build additional one-way streets between any two different junctions.</p><p>Return the minimum number of new streets needed so that it becomes possible to drive from every junction to every other junction.</p><pre>n = 3, edges = [[0,1],[1,2]]            -> 1   (build 2 -> 0)\nn = 4, edges = [[0,1],[0,2],[0,3]]      -> 3   (every leaf needs a way out)\nn = 3, edges = [[0,1],[1,2],[2,0]]      -> 0</pre>",
    constraints=["1 &le; n &le; 5,000", "0 &le; edges.length &le; 10,000", "0 &le; u, v &lt; n and u &ne; v", "No ordered pair [u, v] is listed twice"],
    hints=["Junctions that can already reach each other can be treated as one unit. Find these units (strongly connected components); the units form a directed acyclic graph.",
           "In that DAG, a unit with no incoming street is a source, and a unit with no outgoing street is a sink. Each source needs a new street entering it and each sink needs a new street leaving it.",
           "One new street can serve one sink (as its start) and one source (as its end), so at least max(sources, sinks) new streets are needed, and that many suffice. If there is only one unit the answer is 0. An isolated junction is both a source and a sink."],
    editorial=["Compute the strongly connected components with Tarjan or Kosaraju and look at the condensation, the DAG in which every component is one node. If it has a single node, the network is already strongly connected and the answer is 0.",
               "Otherwise let S be the number of source components (no street enters them) and K the number of sink components (no street leaves them); an isolated junction counts for both. Every source needs some new street ending inside it and every sink needs some new street starting inside it. A new street supplies one start and one end, so at least max(S, K) streets are necessary.",
               "They are also sufficient: link the sinks to the sources in a chain-like fashion (every sink to a distinct source, which closes loops through the DAG), and attach any leftover sources or sinks to the structure with one street each. After that every component lies on a cycle through the whole structure. The answer is therefore max(S, K).",
               "The running time is that of the SCC algorithm, O(n + m). Degrees in the condensation can be counted while scanning the original streets: a street between two different components gives its target component an incoming street and its source component an outgoing street."],
    time="O(n + m)", space="O(n + m)",
    solution='''def minNewStreets(n, edges):
    adj = [[] for _ in range(n)]
    for u, v in edges:
        adj[u].append(v)
    index = [-1] * n
    low = [0] * n
    on_stack = [False] * n
    comp = [-1] * n
    stack = []
    counter = 0
    comps = 0
    for root in range(n):
        if index[root] != -1:
            continue
        index[root] = low[root] = counter
        counter += 1
        stack.append(root)
        on_stack[root] = True
        work = [(root, 0)]
        while work:
            u, i = work.pop()
            if i < len(adj[u]):
                work.append((u, i + 1))
                v = adj[u][i]
                if index[v] == -1:
                    index[v] = low[v] = counter
                    counter += 1
                    stack.append(v)
                    on_stack[v] = True
                    work.append((v, 0))
                elif on_stack[v] and index[v] < low[u]:
                    low[u] = index[v]
            else:
                if low[u] == index[u]:
                    while True:
                        w = stack.pop()
                        on_stack[w] = False
                        comp[w] = comps
                        if w == u:
                            break
                    comps += 1
                if work:
                    parent = work[-1][0]
                    if low[u] < low[parent]:
                        low[parent] = low[u]
    if comps == 1:
        return 0
    has_in = [False] * comps
    has_out = [False] * comps
    for u, v in edges:
        if comp[u] != comp[v]:
            has_out[comp[u]] = True
            has_in[comp[v]] = True
    sources = sum(1 for c in range(comps) if not has_in[c])
    sinks = sum(1 for c in range(comps) if not has_out[c])
    return max(sources, sinks)
''',
    tests=[[3, [[0, 1], [1, 2]]],
           [4, [[0, 1], [0, 2], [0, 3]]],
           [3, [[0, 1], [1, 2], [2, 0]]],
           [1, []],
           [2, []],
           [5, []],
           [2, [[0, 1]]],
           [4, [[0, 1], [1, 0], [2, 3], [3, 2]]],
           [6, [[0, 1], [1, 2], [2, 0], [3, 4], [4, 5], [5, 3], [0, 3]]],
           [5, [[0, 2], [1, 2], [2, 3], [2, 4]]],
           [7, [[0, 1], [1, 0], [2, 3], [3, 2], [4, 5], [5, 4], [0, 6], [2, 6], [4, 6]]],
           [8, [[0, 1], [1, 2], [2, 0], [3, 1], [3, 4], [4, 5], [5, 3], [6, 4], [7, 6], [6, 7], [5, 2]]],
           [6, [[0, 5], [1, 5], [2, 5], [5, 3], [5, 4], [3, 4], [4, 3]]]],
)
_r = rnd(12009)
_n = 1800
p["tests"].append([_n, _planted(_r, _n, 500, 80, 600)])                                      # many components, random DAG between them
p["tests"].append([_n, _planted(_r, _n, 800, 0, 900)])
p["tests"].append([_n, _rand_edges(_r, _n, 1700, True)])                                       # sparse random digraph
p["tests"].append([1800, _planted(_r, 1800, 300, 150, 80)])                                    # few forward edges: many sources and sinks


def b_strongnew(n, edges):
    cand = [(u, v) for u in range(n) for v in range(n) if u != v and [u, v] not in edges]
    for k in range(0, len(cand) + 1):
        for add_ in combinations(cand, k):
            if _is_strong(n, [tuple(e) for e in edges] + list(add_)):
                return k


def g_strongnew(r):
    n = r.randint(1, 5)
    if r.random() < 0.5:
        k = r.randint(1, n)
        return [n, _planted(r, n, k, r.randint(0, 1), r.randint(0, 2 * k))]
    return [n, _rand_edges(r, n, int(r.choice([0.1, 0.2, 0.3, 0.45]) * n * (n - 1)), True)]


def v_strongnew(tests):
    for t in tests:
        _check_graph(t, 5000, 10000, True)
    vals = [t["expected"] for t in tests]
    assert 0 in vals and max(vals) >= 5


CHECKS["min-edges-to-strongly-connect"] = (b_strongnew, g_strongnew, "exact")
VALIDATE["min-edges-to-strongly-connect"] = v_strongnew
