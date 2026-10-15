"""Problems: graphs, traversal on edge lists (components, reachability, degrees, cycle counts). See data/lib.py for the registry."""
from collections import deque

from lib import add, rnd, CHECKS, VALIDATE, gen_arr  # noqa: F401


# ------------------------------------------------------------------ helpers shared by the tests

def _pairs(r, n, m):
    """m distinct unordered pairs on 0..n-1, random orientation, shuffled."""
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
    e = [[a, b] if r.random() < 0.5 else [b, a] for a, b in sorted(s)]
    r.shuffle(e)
    return e


def _tree(r, n, chain=False, star=False):
    """Random labelled tree on n nodes as a shuffled list of oriented edges."""
    lab = list(range(n))
    r.shuffle(lab)
    e = []
    for i in range(1, n):
        p = i - 1 if chain else (0 if star else r.randrange(i))
        a, b = lab[p], lab[i]
        e.append([a, b] if r.random() < 0.5 else [b, a])
    r.shuffle(e)
    return e


def _distinct(edges, n):
    seen = set()
    for a, b in edges:
        assert 0 <= a < n and 0 <= b < n and a != b, "bad endpoint"
        k = (min(a, b), max(a, b))
        assert k not in seen, "repeated edge"
        seen.add(k)


def _adj(r, n, edges):
    """Symmetric adjacency list with every neighbour list in random order."""
    adj = [[] for _ in range(n)]
    for a, b in edges:
        adj[a].append(b)
        adj[b].append(a)
    for l in adj:
        r.shuffle(l)
    return adj


# ================================================================== EASY

# ---------------------------------------------------------------- BFS discovery order
_r = rnd(8401)
_t = [
    [[[1, 2], [0, 3], [0, 3], [1, 2]], 0],
    [[[2, 1, 3], [0, 2], [0, 1], [0]], 3],
    [[[]], 0],
    [[[1], [0], [3], [2], []], 2],
    [[[], [], []], 1],
    [[[1, 2, 3, 4], [0, 2, 3, 4], [0, 1, 3, 4], [0, 1, 2, 4], [0, 1, 2, 3]], 2],
    [[[4, 1], [0, 2], [1, 3], [2, 4], [3, 0]], 2],
    [_adj(_r, 12, _tree(_r, 12)), 5],
]
_n = 2500
_t.append([_adj(_r, _n, _pairs(_r, _n, 3500)), _r.randrange(_n)])
_n = 3000
_t.append([_adj(_r, _n, _tree(_r, _n, chain=True)), _r.randrange(1200, 1800)])
_n = 2500
_t.append([_adj(_r, _n, _tree(_r, _n, star=True)), _r.randrange(_n)])

add(
    id="graph-bfs-discovery-order", title="BFS Discovery Order", diff="Easy", topic="Graphs",
    fn="discoveryOrder", params=[("adj", "int[][]"), ("start", "int")], ret="int[]", cmp="exact",
    desc="<p>An undirected network has <code>n</code> nodes labelled <code>0</code> to <code>n - 1</code>. It is given as an adjacency list: <code>adj[u]</code> lists the neighbours of node <code>u</code> <em>in a fixed order</em>. Every connection is two-way, so <code>v</code> appears in <code>adj[u]</code> exactly when <code>u</code> appears in <code>adj[v]</code>.</p><p>A copier starts at node <code>start</code> and explores the network breadth first: it takes the earliest discovered node that has not been expanded yet, and looks at that node's neighbours in the order they are listed, discovering each neighbour it has not seen before. Return the nodes in the order in which they are discovered, beginning with <code>start</code>. Nodes that cannot be reached from <code>start</code> are not part of the answer.</p>",
    constraints=["1 &le; n = adj.length &le; 3,000", "The total length of all neighbour lists is at most 12,000", "0 &le; start &lt; n", "Connections are symmetric, with no self loops and no repeated neighbour inside one list"],
    hints=["The order depends on which node is expanded next, so you need a first-in, first-out structure.",
           "Put <code>start</code> in a queue and mark it seen. Repeatedly remove the front node, record it, and walk through its neighbours in the listed order.",
           "Mark a neighbour as seen at the moment you add it to the queue, not when you remove it, so no node is queued twice. The order in which nodes leave the queue is the discovery order."],
    editorial=["This is plain breadth-first search with one detail: the neighbour order is given, so the result is completely determined. Keep a queue and a <code>seen</code> array. Pop the front node <code>u</code>, append it to the answer, then scan <code>adj[u]</code> from left to right and push every neighbour that is not yet seen, marking it seen immediately.",
               "Because a node is marked when it is queued, each node enters the queue once, and the queue releases nodes in exactly the order they were discovered. Every node and every neighbour-list entry is touched once, so the work is linear in the size of the input. A recursive depth-first version would give a different order (and risks deep recursion on a 3,000-node path), so use the queue."],
    time="O(n + m)", space="O(n)",
    solution='''from collections import deque


def discoveryOrder(adj, start):
    seen = [False] * len(adj)
    seen[start] = True
    order = []
    q = deque([start])
    while q:
        u = q.popleft()
        order.append(u)
        for v in adj[u]:
            if not seen[v]:
                seen[v] = True
                q.append(v)
    return order
''',
    tests=_t,
)


def b_bfs_order(adj, start):
    # level by level: the next level is built from the current one, left to right
    seen = {start}
    order = [start]
    level = [start]
    while level:
        nxt = []
        for u in level:
            for v in adj[u]:
                if v not in seen:
                    seen.add(v)
                    nxt.append(v)
        order += nxt
        level = nxt
    return order


def g_bfs_order(r):
    n = r.randint(1, 8)
    return [_adj(r, n, _pairs(r, n, r.randint(0, n + 3))), r.randrange(n)]


def v_bfs_order(tests):
    for t in tests:
        adj, s = t["args"]
        n = len(adj)
        assert 1 <= n <= 3000 and 0 <= s < n and sum(map(len, adj)) <= 12000
        for u in range(n):
            assert len(set(adj[u])) == len(adj[u]) and u not in adj[u]
            for v in adj[u]:
                assert 0 <= v < n and u in adj[v]
        assert t["expected"][0] == s and len(set(t["expected"])) == len(t["expected"])


CHECKS["graph-bfs-discovery-order"] = (b_bfs_order, g_bfs_order, "exact")
VALIDATE["graph-bfs-discovery-order"] = v_bfs_order

# ---------------------------------------------------------------- reachable without restricted nodes
_r = rnd(8402)
_t = [
    [7, [[0, 1], [1, 2], [3, 1], [4, 0], [0, 5], [5, 6]], [4, 5]],
    [2, [[0, 1]], [1]],
    [4, [[0, 1], [1, 2], [2, 3]], [3]],
    [5, [], [1, 2]],
    [3, [[0, 1], [1, 2], [0, 2]], [1, 2]],
    [6, [[0, 1], [2, 3], [3, 4], [4, 5], [2, 5]], [1]],
    [6, [[0, 1], [1, 2], [2, 3], [3, 4], [4, 5]], [3]],
    [8, [[0, 1], [0, 2], [1, 3], [2, 3], [3, 4], [4, 5], [6, 7]], [3, 7]],
]
_n = 4000
_e = _pairs(_r, _n, 4500)
_t.append([_n, _e, _r.sample(range(1, _n), 700)])
_n = 4000
_e = _tree(_r, _n)
_t.append([_n, _e, _r.sample(range(1, _n), 40)])
_n = 3000
_t.append([_n, _tree(_r, _n, chain=True), [_r.randrange(1, _n)]])

add(
    id="nodes-reachable-without-restricted", title="Reachable Nodes Without Restricted Ones", diff="Easy", topic="Graphs",
    fn="reachableCount", params=[("n", "int"), ("edges", "int[][]"), ("restricted", "int[]")], ret="int", cmp="exact",
    desc="<p>A network has <code>n</code> nodes labelled <code>0</code> to <code>n - 1</code>. Each entry <code>edges[i] = [a, b]</code> is a two-way connection between nodes <code>a</code> and <code>b</code>. Some nodes are <em>restricted</em>: they are listed in the array <code>restricted</code> and may never be entered.</p><p>Starting from node <code>0</code> (which is never restricted), count how many nodes you can reach, counting node <code>0</code> itself, if you may only travel along connections and may never step on a restricted node.</p>",
    constraints=["2 &le; n &le; 5,000", "0 &le; edges.length &le; 6,000", "0 &le; a, b &lt; n, a &ne; b, and no pair of nodes is joined twice", "0 &le; restricted.length &lt; n; the values in restricted are distinct, between 1 and n - 1"],
    hints=["Forget the restricted nodes for a moment: how would you find every node reachable from node 0?",
           "A restricted node simply behaves as if it were not in the graph. A search that never enters it will never get past it either.",
           "Mark all restricted nodes as visited before starting a BFS or DFS from node 0, then count how many nodes the search visits (do not count the restricted ones)."],
    editorial=["Pre-mark every restricted node as already visited. Then run an ordinary iterative DFS or BFS from node 0: whenever it looks at a neighbour that is already marked, it skips it, so restricted nodes are never entered and nothing behind them can be reached through them. The number of nodes the search marks (not counting the restricted pre-marks) is the answer.",
               "Another way to say the same thing is to drop every edge touching a restricted node and count the size of node 0's connected component. Both run in O(n + m) time. Use an explicit stack or queue; a chain of 3,000 nodes would overflow a naive recursive DFS."],
    time="O(n + m)", space="O(n + m)",
    solution='''def reachableCount(n, edges, restricted):
    blocked = [False] * n
    for x in restricted:
        blocked[x] = True
    adj = [[] for _ in range(n)]
    for a, b in edges:
        if not blocked[a] and not blocked[b]:
            adj[a].append(b)
            adj[b].append(a)
    seen = [False] * n
    seen[0] = True
    stack = [0]
    count = 0
    while stack:
        u = stack.pop()
        count += 1
        for v in adj[u]:
            if not seen[v]:
                seen[v] = True
                stack.append(v)
    return count
''',
    tests=_t,
)


def b_reach_restricted(n, edges, restricted):
    reach = {0}
    bad = set(restricted)
    changed = True
    while changed:
        changed = False
        for a, b in edges:
            for x, y in ((a, b), (b, a)):
                if x in reach and y not in bad and y not in reach:
                    reach.add(y)
                    changed = True
    return len(reach)


def g_reach_restricted(r):
    n = r.randint(2, 9)
    k = r.randint(0, n - 1)
    return [n, _pairs(r, n, r.randint(0, n + 3)), r.sample(range(1, n), k)]


def v_reach_restricted(tests):
    for t in tests:
        n, edges, res = t["args"]
        assert 2 <= n <= 5000 and len(edges) <= 6000
        _distinct(edges, n)
        assert len(set(res)) == len(res) < n and all(1 <= x < n for x in res)
        assert 1 <= t["expected"] <= n - len(res)


CHECKS["nodes-reachable-without-restricted"] = (b_reach_restricted, g_reach_restricted, "exact")
VALIDATE["nodes-reachable-without-restricted"] = v_reach_restricted

# ---------------------------------------------------------------- edges to remove to break every cycle
_r = rnd(8403)
_t = [
    [3, [[0, 1], [1, 2], [2, 0]]],
    [4, [[0, 1], [1, 2], [2, 3]]],
    [5, [[0, 1], [1, 2], [2, 0], [2, 3], [3, 4], [4, 2]]],
    [1, []],
    [4, []],
    [4, [[0, 1], [0, 2], [0, 3], [1, 2], [1, 3], [2, 3]]],
    [6, [[0, 1], [1, 2], [2, 0], [3, 4], [4, 5], [5, 3]]],
    [7, [[0, 1], [1, 2], [2, 3], [3, 0], [0, 2], [4, 5]]],
]
_t.append([2000, _pairs(_r, 2000, 3000)])
_t.append([3000, _pairs(_r, 3000, 3500)])
_t.append([80, _pairs(_r, 80, 3160)])  # complete graph minus a few edges
_t.append([2500, _tree(_r, 2500)])

add(
    id="edges-to-break-all-cycles", title="Edges to Remove to Break All Cycles", diff="Easy", topic="Graphs",
    fn="edgesToRemove", params=[("n", "int"), ("edges", "int[][]")], ret="int", cmp="exact",
    desc="<p>An undirected graph has <code>n</code> nodes labelled <code>0</code> to <code>n - 1</code> and the connections listed in <code>edges</code>, where <code>edges[i] = [a, b]</code> joins <code>a</code> and <code>b</code>. The graph may consist of several separate pieces.</p><p>You want to delete some connections so that no cycle remains anywhere in the graph (the result must be a forest: every piece is a tree). Return the smallest number of connections you have to delete. Deleting a connection never deletes a node.</p>",
    constraints=["1 &le; n &le; 3,000", "0 &le; edges.length &le; 6,000", "0 &le; a, b &lt; n, a &ne; b", "No two edges join the same pair of nodes"],
    hints=["A graph with no cycles has a very specific number of edges for a given number of nodes and pieces. What is it?",
           "A forest with <code>n</code> nodes and <code>c</code> connected pieces has exactly <code>n - c</code> edges.",
           "You can keep at most <code>n - c</code> edges, where <code>c</code> is the number of components of the original graph (deleting edges never merges pieces, and a spanning forest keeps every piece connected). So the answer is <code>m - (n - c)</code>."],
    editorial=["Deleting edges can only keep the number of pieces the same or increase it, and a forest on <code>n</code> nodes with <code>c</code> pieces has exactly <code>n - c</code> edges. The best you can do is keep a spanning tree of each component, which uses <code>n - c</code> edges in total, where <code>c</code> is the number of components of the <em>original</em> graph. Everything else has to go, so the answer is <code>m - n + c</code>.",
               "So the whole task reduces to counting connected components with a DFS, BFS or union-find, in O(n + m) time. The value <code>m - n + c</code> is known as the cyclomatic number of the graph: the number of independent cycles. A union-find that counts how many edges join two nodes that were already connected gives the same number."],
    time="O(n + m)", space="O(n + m)",
    solution='''def edgesToRemove(n, edges):
    adj = [[] for _ in range(n)]
    for a, b in edges:
        adj[a].append(b)
        adj[b].append(a)
    seen = [False] * n
    comps = 0
    for s in range(n):
        if seen[s]:
            continue
        comps += 1
        seen[s] = True
        stack = [s]
        while stack:
            u = stack.pop()
            for v in adj[u]:
                if not seen[v]:
                    seen[v] = True
                    stack.append(v)
    return len(edges) - n + comps
''',
    tests=_t,
)


def b_break_cycles(n, edges):
    # union-find: an edge whose ends are already connected closes a cycle and must go
    p = list(range(n))

    def find(x):
        while p[x] != x:
            p[x] = p[p[x]]
            x = p[x]
        return x

    out = 0
    for a, b in edges:
        ra, rb = find(a), find(b)
        if ra == rb:
            out += 1
        else:
            p[ra] = rb
    return out


def g_break_cycles(r):
    n = r.randint(1, 9)
    return [n, _pairs(r, n, r.randint(0, n + 5))]


def v_break_cycles(tests):
    for t in tests:
        n, edges = t["args"]
        assert 1 <= n <= 3000 and len(edges) <= 6000
        _distinct(edges, n)


CHECKS["edges-to-break-all-cycles"] = (b_break_cycles, g_break_cycles, "exact")
VALIDATE["edges-to-break-all-cycles"] = v_break_cycles


# ================================================================== MEDIUM

# ---------------------------------------------------------------- count connected components
_r = rnd(8404)
_t = [
    [5, [[0, 1], [1, 2], [3, 4]]],
    [5, [[0, 1], [1, 2], [2, 3], [3, 4]]],
    [4, []],
    [1, []],
    [2, [[1, 0]]],
    [6, [[0, 1], [1, 2], [2, 0], [3, 4]]],
    [7, [[0, 6], [6, 3], [1, 5], [5, 2], [2, 1]]],
    [10, [[0, 1], [2, 3], [4, 5], [6, 7], [8, 9], [1, 2], [5, 6]]],
]
_t.append([5000, _pairs(_r, 5000, 2600)])      # many components
_t.append([5000, _pairs(_r, 5000, 5000)])      # a giant component plus leftovers
_t.append([4000, _tree(_r, 4000, chain=True)])
_t.append([3000, []])

add(
    id="count-connected-components-edge-list", title="Count Connected Components", diff="Medium", tier="must", topic="Graphs",
    fn="countComponents", params=[("n", "int"), ("edges", "int[][]")], ret="int", cmp="exact",
    desc="<p>There are <code>n</code> nodes labelled <code>0</code> to <code>n - 1</code>. Each entry <code>edges[i] = [a, b]</code> is a two-way connection between nodes <code>a</code> and <code>b</code>.</p><p>Two nodes belong to the same <em>component</em> if you can get from one to the other by following connections. Return the number of components. A node with no connections is a component of its own.</p>",
    constraints=["1 &le; n &le; 5,000", "0 &le; edges.length &le; 5,000", "0 &le; a, b &lt; n, a &ne; b", "No two edges join the same pair of nodes"],
    hints=["Every node belongs to exactly one component. If you could find the whole component of one node, you could cross all of its members off.",
           "Build an adjacency list. Scan the nodes from 0 to n - 1; when you meet a node that has not been visited, you have found a new component.",
           "Start a DFS or BFS from that node and mark everything it reaches as visited, then add one to the counter. The counter at the end is the answer."],
    editorial=["Convert the edge list to an adjacency list (add each edge in both directions). Loop over all nodes; each time you meet an unvisited node, increase the component count and flood the whole component from it with an iterative DFS or BFS, marking every reached node. Nodes already marked are skipped later in the loop, so each component is counted exactly once.",
               "Union-find solves it just as well: start with <code>n</code> components and subtract one every time an edge joins two different roots. Either way the cost is O(n + m) (union-find with path compression is nearly linear). This count is the basic building block for many harder questions: the size of each component, the number of redundant edges, or how many links are missing to connect everything."],
    time="O(n + m)", space="O(n + m)",
    solution='''def countComponents(n, edges):
    adj = [[] for _ in range(n)]
    for a, b in edges:
        adj[a].append(b)
        adj[b].append(a)
    seen = [False] * n
    comps = 0
    for s in range(n):
        if seen[s]:
            continue
        comps += 1
        seen[s] = True
        stack = [s]
        while stack:
            u = stack.pop()
            for v in adj[u]:
                if not seen[v]:
                    seen[v] = True
                    stack.append(v)
    return comps
''',
    tests=_t,
)


def b_components(n, edges):
    # label propagation: every node keeps the smallest label it has heard of
    lab = list(range(n))
    changed = True
    while changed:
        changed = False
        for a, b in edges:
            m = min(lab[a], lab[b])
            if lab[a] != m or lab[b] != m:
                lab[a] = lab[b] = m
                changed = True
    return len(set(lab))


def g_components(r):
    n = r.randint(1, 9)
    return [n, _pairs(r, n, r.randint(0, n + 2))]


def v_components(tests):
    for t in tests:
        n, edges = t["args"]
        assert 1 <= n <= 5000 and len(edges) <= 5000
        _distinct(edges, n)
        assert 1 <= t["expected"] <= n


CHECKS["count-connected-components-edge-list"] = (b_components, g_components, "exact")
VALIDATE["count-connected-components-edge-list"] = v_components

# ---------------------------------------------------------------- maximal network rank
_r = rnd(8405)
_t = [
    [4, [[0, 1], [0, 3], [1, 2], [1, 3]]],
    [5, [[0, 1], [0, 3], [1, 2], [1, 3], [2, 3], [2, 4]]],
    [8, [[0, 1], [1, 2], [2, 3], [2, 4], [5, 6], [5, 7]]],
    [2, []],
    [2, [[0, 1]]],
    [3, [[0, 1], [1, 2], [0, 2]]],
    [5, [[0, 1], [0, 2], [0, 3], [0, 4]]],
    [6, [[0, 1], [2, 3], [4, 5]]],
    [7, [[0, 1], [0, 2], [0, 3], [4, 5], [4, 6], [1, 5]]],
]
_t.append([100, _pairs(_r, 100, 2500)])
_t.append([100, _pairs(_r, 100, 4950)])
_t.append([100, _pairs(_r, 100, 120)])

add(
    id="maximal-network-rank", title="Maximal Network Rank", diff="Medium", topic="Graphs",
    fn="maxNetworkRank", params=[("n", "int"), ("roads", "int[][]")], ret="int", cmp="exact",
    desc="<p>A country has <code>n</code> cities labelled <code>0</code> to <code>n - 1</code>. Each entry <code>roads[i] = [a, b]</code> is a two-way road between cities <code>a</code> and <code>b</code>.</p><p>The <em>network rank</em> of two different cities is the number of roads that touch at least one of them. A road that joins the two cities directly is counted only once. Return the largest network rank over all pairs of different cities.</p>",
    constraints=["2 &le; n &le; 100", "0 &le; roads.length &le; n(n - 1) / 2", "0 &le; a, b &lt; n, a &ne; b", "No two roads join the same pair of cities"],
    hints=["Start with a single city: how many roads touch it?",
           "For a pair of cities, adding their two degrees counts a direct road between them twice.",
           "The rank of a pair is <code>deg[i] + deg[j]</code>, minus one if <code>i</code> and <code>j</code> are joined by a road. With n at most 100 you can test every pair, using a set of edges for the direct-road check."],
    editorial=["Compute the degree of every city and store the roads in a set of normalised pairs. For two different cities <code>i</code> and <code>j</code>, the roads touching either one number <code>deg[i] + deg[j]</code>, except that a road directly between them was counted once for each end, so subtract one in that case. Trying all pairs takes O(n<sup>2</sup>) and n is only 100.",
               "A faster idea sorts the cities by degree: only the cities with the largest and second largest degrees can matter, and ties need a little care because some pairs of top cities may be directly connected. That gets to O(n + m), but the quadratic scan is simpler and fully sufficient under these limits."],
    time="O(n<sup>2</sup> + m)", space="O(n + m)",
    solution='''def maxNetworkRank(n, roads):
    deg = [0] * n
    link = set()
    for a, b in roads:
        deg[a] += 1
        deg[b] += 1
        link.add((min(a, b), max(a, b)))
    best = 0
    for i in range(n):
        for j in range(i + 1, n):
            rank = deg[i] + deg[j] - (1 if (i, j) in link else 0)
            if rank > best:
                best = rank
    return best
''',
    tests=_t,
)


def b_netrank(n, roads):
    best = 0
    for i in range(n):
        for j in range(i + 1, n):
            c = sum(1 for a, b in roads if a in (i, j) or b in (i, j))
            best = max(best, c)
    return best


def g_netrank(r):
    n = r.randint(2, 8)
    return [n, _pairs(r, n, r.randint(0, n * (n - 1) // 2))]


def v_netrank(tests):
    for t in tests:
        n, roads = t["args"]
        assert 2 <= n <= 100 and len(roads) <= n * (n - 1) // 2
        _distinct(roads, n)


CHECKS["maximal-network-rank"] = (b_netrank, g_netrank, "exact")
VALIDATE["maximal-network-rank"] = v_netrank

# ---------------------------------------------------------------- reorder routes towards city zero
_r = rnd(8406)
_t = [
    [6, [[0, 1], [1, 3], [2, 3], [4, 0], [4, 5]]],
    [5, [[1, 0], [1, 2], [3, 2], [3, 4]]],
    [3, [[1, 0], [2, 0]]],
    [2, [[0, 1]]],
    [2, [[1, 0]]],
    [4, [[0, 1], [0, 2], [0, 3]]],
    [5, [[0, 1], [1, 2], [2, 3], [3, 4]]],
    [7, [[1, 0], [2, 1], [3, 2], [4, 3], [5, 4], [6, 5]]],
    [8, [[0, 1], [2, 0], [1, 3], [4, 1], [2, 5], [6, 2], [7, 6]]],
]
_t.append([4000, _tree(_r, 4000)])
_e = _tree(_r, 3000, chain=True)
_t.append([3000, _e])
_t.append([2500, _tree(_r, 2500, star=True)])

add(
    id="reorder-routes-to-city-zero", title="Reorder Routes to Reach City Zero", diff="Medium", topic="Graphs",
    fn="minReorder", params=[("n", "int"), ("roads", "int[][]")], ret="int", cmp="exact",
    desc="<p>A country has <code>n</code> cities labelled <code>0</code> to <code>n - 1</code> and exactly <code>n - 1</code> one-way roads. Each entry <code>roads[i] = [a, b]</code> is a road that can only be driven from city <code>a</code> to city <code>b</code>. If you ignore the directions, the roads connect all the cities and there is exactly one route between any two cities.</p><p>City <code>0</code> is the capital. You may reverse the direction of some roads so that, in the end, a traveller starting in any city can reach the capital. Return the minimum number of roads you must reverse.</p>",
    constraints=["2 &le; n &le; 5,000", "roads.length = n - 1", "0 &le; a, b &lt; n, a &ne; b", "Ignoring directions the roads form a tree (every city is connected to every other city)"],
    hints=["Because the roads form a tree, every city has exactly one route towards the capital. Which direction must each road on that route have?",
           "Look at a road from the capital's side: it must point <em>towards</em> the parent (closer to city 0). If it points away from city 0, it has to be reversed.",
           "Do a BFS or DFS from city 0 on the undirected tree. Store each road at both ends, with a cost of 1 when you traverse it in its original direction (that means it points away from city 0) and 0 otherwise. Sum the costs of the tree edges you use."],
    editorial=["Turn the roads into an undirected adjacency list, remembering the original direction: the entry <code>a &rarr; b</code> stored at <code>a</code> carries cost 1 and the mirror entry stored at <code>b</code> carries cost 0. Now walk the tree outward from city 0. When you step from <code>u</code> to a new city <code>v</code> along an entry of cost 1, the road was built from <code>u</code> to <code>v</code>, i.e. away from the capital, so it must be reversed. Entries of cost 0 already point towards the capital.",
               "Each road lies on the unique path of exactly one of its endpoints to the capital, and its required direction is fixed, so the reversals are forced and the sum of the costs is both necessary and enough. The traversal visits every city and road once, so it runs in O(n). An iterative traversal avoids recursion limits on a long chain."],
    time="O(n)", space="O(n)",
    solution='''def minReorder(n, roads):
    adj = [[] for _ in range(n)]
    for a, b in roads:
        adj[a].append((b, 1))
        adj[b].append((a, 0))
    seen = [False] * n
    seen[0] = True
    stack = [0]
    flips = 0
    while stack:
        u = stack.pop()
        for v, cost in adj[u]:
            if not seen[v]:
                seen[v] = True
                flips += cost
                stack.append(v)
    return flips
''',
    tests=_t,
)


def b_reorder(n, roads):
    # try every subset of roads to reverse
    best = n
    for mask in range(1 << len(roads)):
        rev = [[b, a] if mask >> i & 1 else [a, b] for i, (a, b) in enumerate(roads)]
        # everyone reaches 0  <=>  walking backwards from 0 along the roads touches every city
        got = {0}
        changed = True
        while changed:
            changed = False
            for a, b in rev:
                if b in got and a not in got:
                    got.add(a)
                    changed = True
        if len(got) == n:
            best = min(best, bin(mask).count("1"))
    return best


def g_reorder(r):
    n = r.randint(2, 9)
    return [n, _tree(r, n)]


def v_reorder(tests):
    for t in tests:
        n, roads = t["args"]
        assert 2 <= n <= 5000 and len(roads) == n - 1
        _distinct(roads, n)
        p = list(range(n))

        def find(x):
            while p[x] != x:
                p[x] = p[p[x]]
                x = p[x]
            return x

        for a, b in roads:
            ra, rb = find(a), find(b)
            assert ra != rb, "not a tree"
            p[ra] = rb


CHECKS["reorder-routes-to-city-zero"] = (b_reorder, g_reorder, "exact")
VALIDATE["reorder-routes-to-city-zero"] = v_reorder

# ---------------------------------------------------------------- unreachable node pairs
_r = rnd(8407)
_t = [
    [3, [[0, 1], [0, 2], [1, 2]]],
    [7, [[0, 2], [0, 5], [2, 4], [1, 6], [5, 4]]],
    [4, []],
    [1, []],
    [2, []],
    [2, [[0, 1]]],
    [5, [[0, 1], [2, 3]]],
    [6, [[0, 1], [1, 2], [3, 4]]],
    [9, [[0, 1], [1, 2], [3, 4], [4, 5], [5, 3], [6, 7]]],
]
_t.append([3000, []])
_t.append([3000, _pairs(_r, 3000, 1500)])
_t.append([3000, _pairs(_r, 3000, 3600)])

add(
    id="count-unreachable-node-pairs", title="Count Unreachable Node Pairs", diff="Medium", topic="Graphs",
    fn="countUnreachablePairs", params=[("n", "int"), ("edges", "int[][]")], ret="int", cmp="exact",
    desc="<p>An undirected graph has <code>n</code> nodes labelled <code>0</code> to <code>n - 1</code>. Each entry <code>edges[i] = [a, b]</code> is a two-way connection between <code>a</code> and <code>b</code>.</p><p>Count the pairs of different nodes <code>(u, v)</code> with <code>u &lt; v</code> for which there is <em>no</em> way to travel from <code>u</code> to <code>v</code>. Each pair is counted once.</p>",
    constraints=["1 &le; n &le; 3,000", "0 &le; edges.length &le; 5,000", "0 &le; a, b &lt; n, a &ne; b", "No two edges join the same pair of nodes"],
    hints=["Count the opposite thing first: which pairs <em>can</em> reach each other?",
           "Two nodes can reach each other exactly when they lie in the same component, so you only need the size of every component.",
           "A component of size <code>s</code> has <code>s * (n - s)</code> ordered pairs leading to nodes outside it. Sum that over all components and halve it, or add up <code>size * (nodes not yet processed)</code> component by component."],
    editorial=["Find the size of every connected component with a DFS, BFS or union-find. Nodes in different components are never connected, and nodes in the same component always are, so the unreachable pairs are exactly the pairs of nodes that sit in different components.",
               "Sweep through the components keeping the number of nodes <code>left</code> that have not yet been assigned to a processed component. For a component of size <code>s</code>, subtract it from <code>left</code> and add <code>s * left</code> to the answer: that counts each cross-component pair exactly once. With n at most 3,000 the answer is below 4.5 million, so it fits comfortably in 32 bits. Time O(n + m)."],
    time="O(n + m)", space="O(n + m)",
    solution='''def countUnreachablePairs(n, edges):
    adj = [[] for _ in range(n)]
    for a, b in edges:
        adj[a].append(b)
        adj[b].append(a)
    seen = [False] * n
    left = n
    total = 0
    for s in range(n):
        if seen[s]:
            continue
        seen[s] = True
        stack = [s]
        size = 0
        while stack:
            u = stack.pop()
            size += 1
            for v in adj[u]:
                if not seen[v]:
                    seen[v] = True
                    stack.append(v)
        left -= size
        total += size * left
    return total
''',
    tests=_t,
)


def b_unreach(n, edges):
    reach = [[i == j for j in range(n)] for i in range(n)]
    for a, b in edges:
        reach[a][b] = reach[b][a] = True
    for k in range(n):
        for i in range(n):
            if reach[i][k]:
                for j in range(n):
                    if reach[k][j]:
                        reach[i][j] = True
    return sum(1 for i in range(n) for j in range(i + 1, n) if not reach[i][j])


def g_unreach(r):
    n = r.randint(1, 9)
    return [n, _pairs(r, n, r.randint(0, n + 1))]


def v_unreach(tests):
    for t in tests:
        n, edges = t["args"]
        assert 1 <= n <= 3000 and len(edges) <= 5000
        _distinct(edges, n)
        assert 0 <= t["expected"] <= n * (n - 1) // 2


CHECKS["count-unreachable-node-pairs"] = (b_unreach, g_unreach, "exact")
VALIDATE["count-unreachable-node-pairs"] = v_unreach

# ---------------------------------------------------------------- operations to connect the network
_r = rnd(8408)
_t = [
    [4, [[0, 1], [0, 2], [1, 2]]],
    [6, [[0, 1], [0, 2], [0, 3], [1, 2], [1, 3]]],
    [6, [[0, 1], [0, 2], [0, 3], [1, 2]]],
    [1, []],
    [2, []],
    [2, [[0, 1]]],
    [3, [[0, 1], [1, 2]]],
    [5, [[0, 1], [1, 2], [2, 0], [3, 4]]],
    [7, [[0, 1], [1, 2], [2, 0], [0, 3], [3, 1], [4, 5]]],
    [4, [[0, 1], [1, 2], [2, 3], [3, 0], [0, 2], [1, 3]]],
]
_t.append([2500, _pairs(_r, 2500, 2000)])       # too few cables
_t.append([2500, _pairs(_r, 2500, 2900)])       # enough cables, many components
_t.append([1500, _pairs(_r, 1500, 3500)])       # already connected
_t.append([2000, _pairs(_r, 2000, 1999)])

add(
    id="min-operations-connect-network", title="Make the Network Connected", diff="Medium", topic="Graphs",
    fn="makeConnected", params=[("n", "int"), ("cables", "int[][]")], ret="int", cmp="exact",
    desc="<p>A data centre has <code>n</code> computers labelled <code>0</code> to <code>n - 1</code>. Each entry <code>cables[i] = [a, b]</code> is a cable between computers <code>a</code> and <code>b</code>; information flows both ways, so computers that are linked directly or through other computers can talk to each other.</p><p>In one operation you may unplug any cable and use it to join any two computers that are not currently joined by a cable. Return the minimum number of operations needed to make <em>every</em> computer able to reach every other one, or <code>-1</code> if that is impossible.</p>",
    constraints=["1 &le; n &le; 3,000", "0 &le; cables.length &le; 5,000", "0 &le; a, b &lt; n, a &ne; b", "No two cables join the same pair of computers"],
    hints=["Connecting <code>n</code> computers needs at least <code>n - 1</code> cables. What if you own fewer?",
           "If there are at least <code>n - 1</code> cables, a cable is either needed to keep its component connected or it is a spare. Unplugging a spare disconnects nothing.",
           "Let <code>c</code> be the number of components. Joining <code>c</code> components takes <code>c - 1</code> new cables, and (when <code>cables.length &ge; n - 1</code>) there are always enough spares to do it. So the answer is <code>c - 1</code>."],
    editorial=["First rule out the impossible case: a connected network on <code>n</code> computers needs at least <code>n - 1</code> cables, so if <code>cables.length &lt; n - 1</code> the answer is <code>-1</code>.",
               "Otherwise count the connected components <code>c</code> with a DFS or union-find. Each of the <code>c - 1</code> missing joins needs one cable. A component with <code>k</code> computers and <code>e</code> cables has <code>e - (k - 1)</code> spare cables; summing over components gives <code>cables.length - n + c</code> spares, which is at least <code>c - 1</code> exactly when <code>cables.length &ge; n - 1</code>. A spare can be unplugged without splitting anything and used to join two components, so <code>c - 1</code> operations are enough and also necessary (each operation lowers the component count by at most one). Time O(n + m)."],
    time="O(n + m)", space="O(n + m)",
    solution='''def makeConnected(n, cables):
    if len(cables) < n - 1:
        return -1
    adj = [[] for _ in range(n)]
    for a, b in cables:
        adj[a].append(b)
        adj[b].append(a)
    seen = [False] * n
    comps = 0
    for s in range(n):
        if seen[s]:
            continue
        comps += 1
        seen[s] = True
        stack = [s]
        while stack:
            u = stack.pop()
            for v in adj[u]:
                if not seen[v]:
                    seen[v] = True
                    stack.append(v)
    return comps - 1
''',
    tests=_t,
)


def b_make_connected(n, cables):
    # count spare cables (those closing a cycle) and the components with a union-find
    p = list(range(n))

    def find(x):
        while p[x] != x:
            p[x] = p[p[x]]
            x = p[x]
        return x

    spare = 0
    comps = n
    for a, b in cables:
        ra, rb = find(a), find(b)
        if ra == rb:
            spare += 1
        else:
            p[ra] = rb
            comps -= 1
    return -1 if spare < comps - 1 else comps - 1


def g_make_connected(r):
    n = r.randint(1, 9)
    return [n, _pairs(r, n, r.randint(0, n + 3))]


def v_make_connected(tests):
    for t in tests:
        n, cables = t["args"]
        assert 1 <= n <= 3000 and len(cables) <= 5000
        _distinct(cables, n)


CHECKS["min-operations-connect-network"] = (b_make_connected, g_make_connected, "exact")
VALIDATE["min-operations-connect-network"] = v_make_connected

# ---------------------------------------------------------------- components that are simple cycles
_r = rnd(8409)


def _cycle_world(r, n, cyc_sizes, extra_paths, noise):
    """Disjoint cycles of the given sizes, some paths, and a few noisy pieces, nodes relabelled randomly."""
    lab = list(range(n))
    r.shuffle(lab)
    pos = 0
    e = []
    for s in cyc_sizes:
        nodes = lab[pos:pos + s]
        pos += s
        e += [[nodes[i], nodes[(i + 1) % s]] for i in range(s)]
    for s in extra_paths:
        nodes = lab[pos:pos + s]
        pos += s
        e += [[nodes[i], nodes[i + 1]] for i in range(s - 1)]
    for s in noise:  # a cycle with one chord, which is not a plain cycle
        nodes = lab[pos:pos + s]
        pos += s
        e += [[nodes[i], nodes[(i + 1) % s]] for i in range(s)]
        e.append([nodes[0], nodes[2]])
    assert pos <= n
    r.shuffle(e)
    return e


_t = [
    [6, [[0, 1], [0, 2], [1, 2], [3, 4], [3, 5]]],
    [6, [[0, 1], [0, 2], [1 , 2], [3, 4], [3, 5], [4, 5]]],
    [3, [[0, 1], [1, 2], [2, 0]]],
    [1, []],
    [2, [[0, 1]]],
    [4, [[0, 1], [1, 2], [2, 3], [3, 0]]],
    [4, [[0, 1], [1, 2], [2, 3], [3, 0], [0, 2]]],
    [7, [[0, 1], [1, 2], [2, 0], [3, 4], [4, 5], [5, 6]]],
    [10, [[0, 1], [1, 2], [2, 3], [3, 0], [4, 5], [5, 6], [6, 4], [7, 8], [8, 9]]],
]
_t.append([3000, _cycle_world(_r, 3000, [3] * 300 + [4] * 100 + [5] * 100 + [10] * 50, [2] * 100 + [7] * 40, [6] * 35)])
_t.append([3000, _cycle_world(_r, 3000, [3000], [], [])])
_t.append([3000, _cycle_world(_r, 3000, [3] * 900, [], [])])
_t.append([2400, _cycle_world(_r, 2400, [20] * 60 + [100] * 3, [50] * 10, [30] * 10)])

add(
    id="count-cycle-components", title="Count Components That Are Cycles", diff="Medium", tier="extra", topic="Graphs",
    fn="countCycleComponents", params=[("n", "int"), ("edges", "int[][]")], ret="int", cmp="exact",
    desc="<p>An undirected graph has <code>n</code> nodes labelled <code>0</code> to <code>n - 1</code> and the connections listed in <code>edges</code>, where <code>edges[i] = [a, b]</code> joins <code>a</code> and <code>b</code>.</p><p>A connected component is called a <em>ring</em> if its nodes can be arranged in a closed loop <code>v<sub>1</sub>, v<sub>2</sub>, &hellip;, v<sub>k</sub></code> (with <code>k &ge; 3</code>) in which consecutive nodes are joined, <code>v<sub>k</sub></code> is joined to <code>v<sub>1</sub></code>, and there are <em>no other</em> connections inside the component. Return the number of components of the graph that are rings.</p>",
    constraints=["1 &le; n &le; 3,000", "0 &le; edges.length &le; 4,000", "0 &le; a, b &lt; n, a &ne; b", "No two edges join the same pair of nodes"],
    hints=["Look at the degrees of the nodes in a ring. What do they all have in common?",
           "In a ring every node touches exactly two connections. Conversely, a connected piece in which every node has degree exactly 2 can only be one loop.",
           "Find the components with a DFS or BFS, and for each component check that every node has degree 2. Count the components that pass."],
    editorial=["Compute the degree of every node and find the connected components. A ring has all degrees equal to 2. The reverse also holds: if a connected component has every degree equal to 2, then it has as many edges as nodes and walking along the edges can never branch, so it must be one single loop. Since no two edges join the same pair of nodes, such a loop has at least 3 nodes.",
               "Any extra chord gives some node degree 3, a path has end nodes of degree 1, and an isolated node has degree 0, so each of those components fails the test. Count the components in which every node has degree exactly 2. One traversal does all of this in O(n + m)."],
    time="O(n + m)", space="O(n + m)",
    solution='''def countCycleComponents(n, edges):
    adj = [[] for _ in range(n)]
    for a, b in edges:
        adj[a].append(b)
        adj[b].append(a)
    seen = [False] * n
    rings = 0
    for s in range(n):
        if seen[s]:
            continue
        seen[s] = True
        stack = [s]
        ok = True
        while stack:
            u = stack.pop()
            if len(adj[u]) != 2:
                ok = False
            for v in adj[u]:
                if not seen[v]:
                    seen[v] = True
                    stack.append(v)
        if ok:
            rings += 1
    return rings
''',
    tests=_t,
)


def b_rings(n, edges):
    nb = {i: set() for i in range(n)}
    for a, b in edges:
        nb[a].add(b)
        nb[b].add(a)
    done = set()
    out = 0
    for s in range(n):
        if s in done:
            continue
        comp = {s}
        todo = [s]
        while todo:
            u = todo.pop()
            for v in nb[u]:
                if v not in comp:
                    comp.add(v)
                    todo.append(v)
        done |= comp
        if len(comp) < 3 or any(len(nb[u]) != 2 for u in comp):
            continue
        # walk around the loop and check that it comes back after visiting every node
        prev, cur, steps = -1, s, 0
        while True:
            nxt = [v for v in nb[cur] if v != prev]
            prev, cur = cur, nxt[0] if prev != -1 else min(nb[cur])
            steps += 1
            if cur == s:
                break
        if steps == len(comp):
            out += 1
    return out


def g_rings(r):
    n = r.randint(1, 10)
    return [n, _pairs(r, n, r.randint(0, n + 2))]


def v_rings(tests):
    for t in tests:
        n, edges = t["args"]
        assert 1 <= n <= 3000 and len(edges) <= 4000
        _distinct(edges, n)


CHECKS["count-cycle-components"] = (b_rings, g_rings, "exact")
VALIDATE["count-cycle-components"] = v_rings

# ================================================================== HARD

# ---------------------------------------------------------------- minimize malware spread
_r = rnd(8410)
_t = [
    [3, [[0, 1], [1, 2]], [0, 1]],
    [3, [[0, 1]], [0, 2]],
    [4, [[0, 1], [1, 2], [2, 3]], [3, 0]],
    [1, [], [0]],
    [4, [], [3, 1]],
    [5, [[0, 1], [2, 3], [3, 4]], [0, 2, 4]],
    [6, [[0, 1], [1, 2], [3, 4], [4, 5]], [0, 1, 3]],
    [6, [[0, 1], [1, 2], [2, 0], [3, 4]], [2, 4, 5]],
    [7, [[0, 1], [1, 2], [3, 4], [4, 5], [5, 6]], [0, 2, 3, 6]],
]
for _n, _m, _k in [(3000, 2400, 60), (3000, 1500, 400), (2500, 2500, 25)]:
    _e = _pairs(_r, _n, _m)
    _t.append([_n, _e, _r.sample(range(_n), _k)])

add(
    id="minimize-malware-spread", title="Minimize Malware Spread", diff="Hard", topic="Graphs",
    fn="minMalwareSpread", params=[("n", "int"), ("edges", "int[][]"), ("initial", "int[]")], ret="int", cmp="exact",
    desc="<p>A network has <code>n</code> nodes labelled <code>0</code> to <code>n - 1</code>. Each entry <code>edges[i] = [a, b]</code> is a two-way connection between <code>a</code> and <code>b</code>. Some nodes, listed in <code>initial</code>, are infected by malware at the start. The malware keeps spreading: whenever a node is infected, every node it is directly connected to becomes infected too, until nothing changes. So a component of the network ends up entirely infected as soon as it contains at least one infected node.</p><p>You may pick <strong>exactly one</strong> node from <code>initial</code> and cure it before the spread starts (the node stays in the network and may be re-infected by a neighbour). Choose the node so that the final number of infected nodes is as small as possible, and return it. If several nodes give the same smallest final count, return the one with the smallest label.</p>",
    constraints=["1 &le; n &le; 3,000", "0 &le; edges.length &le; 5,000", "0 &le; a, b &lt; n, a &ne; b, and no two edges join the same pair of nodes", "1 &le; initial.length &le; n; the values in initial are distinct and lie in 0..n - 1"],
    hints=["Infection fills whole components. Which components do you actually have a chance of saving?",
           "Curing a node saves its component only if that node is the <em>only</em> initially infected node in it. Otherwise the others will still infect the whole component.",
           "Compute component sizes and the number of initially infected nodes per component. The saving of a candidate is the component size if it is alone there and 0 otherwise. Pick the largest saving, breaking ties by the smaller label (if every saving is 0, that is the smallest label in <code>initial</code>)."],
    editorial=["Because infection floods an entire component, the final infected count is the total size of all components that contain at least one infected node. Curing node <code>u</code> removes <code>u</code>'s component from that total only if <code>u</code> is the single infected node of its component; if another infected node lives in the same component, the component is infected anyway and nothing is saved.",
               "So compute the component of every node (DFS, BFS or union-find), the size of each component, and how many nodes of <code>initial</code> fall into each. For each <code>u</code> in <code>initial</code>, its saving is <code>size</code> of its component when the count there is 1, else 0. Take the node with the largest saving, scanning the labels in increasing order and updating only on a strictly larger saving, so ties go to the smallest label (and if all savings are 0, the smallest label in <code>initial</code> is returned). The whole thing takes O(n + m) plus the sort of <code>initial</code>."],
    time="O((n + m) + k log k)", space="O(n + m)",
    solution='''def minMalwareSpread(n, edges, initial):
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
    size = [0] * n
    for v in range(n):
        size[find(v)] += 1
    infected = [0] * n
    for u in initial:
        infected[find(u)] += 1
    best, best_save = -1, -1
    for u in sorted(initial):
        root = find(u)
        save = size[root] if infected[root] == 1 else 0
        if save > best_save:
            best, best_save = u, save
    return best
''',
    tests=_t,
)


def b_malware(n, edges, initial):
    adj = [[] for _ in range(n)]
    for a, b in edges:
        adj[a].append(b)
        adj[b].append(a)

    def spread(sources):
        got = set(sources)
        todo = list(sources)
        while todo:
            u = todo.pop()
            for v in adj[u]:
                if v not in got:
                    got.add(v)
                    todo.append(v)
        return len(got)

    best = None
    for u in sorted(initial):
        c = spread([x for x in initial if x != u])
        if best is None or c < best[0]:
            best = (c, u)
    return best[1]


def g_malware(r):
    n = r.randint(1, 9)
    return [n, _pairs(r, n, r.randint(0, n + 1)), r.sample(range(n), r.randint(1, n))]


def v_malware(tests):
    for t in tests:
        n, edges, init = t["args"]
        assert 1 <= n <= 3000 and len(edges) <= 5000
        _distinct(edges, n)
        assert 1 <= len(init) <= n and len(set(init)) == len(init) and all(0 <= x < n for x in init)
        assert t["expected"] in init


CHECKS["minimize-malware-spread"] = (b_malware, g_malware, "exact")
VALIDATE["minimize-malware-spread"] = v_malware

# ---------------------------------------------------------------- number of good paths in a tree
_r = rnd(8411)


def _vals(r, n, hi):
    return [r.randint(0, hi) for _ in range(n)]


_t = [
    [[1, 3, 2, 1, 3], [[0, 1], [0, 2], [2, 3], [2, 4]]],
    [[1, 1, 2, 2, 3], [[0, 1], [1, 2], [2, 3], [2, 4]]],
    [[1], []],
    [[2, 2], [[0, 1]]],
    [[1, 2], [[0, 1]]],
    [[5, 5, 5, 5], [[0, 1], [1, 2], [2, 3]]],
    [[3, 1, 3, 1, 3], [[0, 1], [1, 2], [2, 3], [3, 4]]],
    [[1, 2, 1, 2, 1, 2], [[0, 1], [1, 2], [2, 3], [3, 4], [4, 5]]],
    [[0, 4, 0, 4, 0, 4, 0], [[1, 0], [1, 2], [1, 3], [3, 4], [3, 5], [5, 6]]],
]
_t.append([_vals(_r, 2500, 3), _tree(_r, 2500)])
_t.append([_vals(_r, 2500, 60), _tree(_r, 2500, chain=True)])
_t.append([[7] * 2000, _tree(_r, 2000, star=True)])
_t.append([_vals(_r, 1500, 100000), _tree(_r, 1500)])

add(
    id="number-of-good-paths-in-tree", title="Number of Good Paths in a Tree", diff="Hard", topic="Graphs",
    fn="goodPaths", params=[("vals", "int[]"), ("edges", "int[][]")], ret="int", cmp="exact",
    desc="<p>A tree has <code>n</code> nodes labelled <code>0</code> to <code>n - 1</code>. Node <code>i</code> carries the value <code>vals[i]</code>, and <code>edges</code> lists its <code>n - 1</code> two-way connections, so any two nodes are joined by exactly one simple path.</p><p>A path is <em>good</em> if its two end nodes have the same value and every node on the path (ends included) has a value that is at most that value. A path made of a single node is good. The paths <code>u &rarr; v</code> and <code>v &rarr; u</code> count as one path. Return the number of good paths.</p>",
    constraints=["1 &le; n = vals.length &le; 5,000", "0 &le; vals[i] &le; 100,000", "edges.length = n - 1 and the edges form a tree", "0 &le; a, b &lt; n for every edge [a, b]"],
    hints=["Checking every pair of equal-valued nodes by walking the path is too slow for a star with thousands of equal nodes. Think about how a path becomes allowed as you raise a threshold.",
           "Process the edges in increasing order of the larger value of their two ends. After processing all edges up to threshold <code>v</code>, each component contains only nodes of value at most <code>v</code>.",
           "Use union-find where every root also remembers the largest value in its component and how many nodes carry it. When two components with the same largest value are merged, add <code>countA * countB</code> new good paths. Start the answer at <code>n</code> for the single-node paths."],
    editorial=["A path is good exactly when its maximum value is attained at both ends. Sort all edges by <code>max(vals[a], vals[b])</code> and add them one at a time to a union-find structure. When an edge of weight <code>w</code> is added, both of its end components consist only of nodes with value at most <code>w</code>, so any path through the new edge between two nodes of value <code>w</code> has maximum <code>w</code> and is good.",
               "For every component keep the maximum value and the number of nodes holding it. Merging components whose maximums differ simply keeps the larger maximum and its count, since the smaller-valued maxima can no longer be the end of a good path through the merged component. If the maximums are equal, every node with that value in one component pairs with every such node in the other, giving <code>cnt<sub>a</sub> &middot; cnt<sub>b</sub></code> new good paths, and the counts add. Starting from <code>n</code> single-node paths, the total is the answer. The cost is O(n log n) for the sort plus nearly linear union-find work, and the answer is at most n(n + 1)/2, which fits in 32 bits for n at most 5,000."],
    time="O(n log n)", space="O(n)",
    solution='''def goodPaths(vals, edges):
    n = len(vals)
    parent = list(range(n))
    cnt = [1] * n          # how many nodes in the component hold its maximum value
    top = vals[:]          # maximum value of the component

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    total = n
    for a, b in sorted(edges, key=lambda e: max(vals[e[0]], vals[e[1]])):
        ra, rb = find(a), find(b)
        if top[ra] > top[rb]:
            parent[rb] = ra
        elif top[ra] < top[rb]:
            parent[ra] = rb
        else:
            total += cnt[ra] * cnt[rb]
            parent[rb] = ra
            cnt[ra] += cnt[rb]
    return total
''',
    tests=_t,
)


def b_good_paths(vals, edges):
    n = len(vals)
    adj = [[] for _ in range(n)]
    for a, b in edges:
        adj[a].append(b)
        adj[b].append(a)
    total = 0
    for i in range(n):
        par = [-2] * n
        par[i] = -1
        todo = [i]
        for u in todo:
            for v in adj[u]:
                if par[v] == -2:
                    par[v] = u
                    todo.append(v)
        for j in range(i, n):
            if vals[j] != vals[i]:
                continue
            x, ok = j, True
            while x != -1:
                if vals[x] > vals[i]:
                    ok = False
                    break
                x = par[x]
            if ok:
                total += 1
    return total


def g_good_paths(r):
    n = r.randint(1, 10)
    return [_vals(r, n, r.choice([1, 2, 4])), _tree(r, n)]


def v_good_paths(tests):
    for t in tests:
        vals, edges = t["args"]
        n = len(vals)
        assert 1 <= n <= 5000 and len(edges) == n - 1 and all(0 <= v <= 100000 for v in vals)
        _distinct(edges, n)
        p = list(range(n))

        def find(x):
            while p[x] != x:
                p[x] = p[p[x]]
                x = p[x]
            return x

        for a, b in edges:
            ra, rb = find(a), find(b)
            assert ra != rb, "not a tree"
            p[ra] = rb
        assert n <= t["expected"] <= n * (n + 1) // 2


CHECKS["number-of-good-paths-in-tree"] = (b_good_paths, g_good_paths, "exact")
VALIDATE["number-of-good-paths-in-tree"] = v_good_paths
