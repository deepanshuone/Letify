"""Problems: graphs, minimum spanning trees (Kruskal, Prim, bottleneck, second best, counting). See data/lib.py for the registry."""
import heapq
from itertools import combinations

from lib import add, rnd, CHECKS, VALIDATE, gen_arr  # noqa: F401

MOD = 10 ** 9 + 7
T = "Graphs"


# ---------------------------------------------------------------- shared helpers

def _graph(r, n, m, lo, hi, connected=True, simple=True):
    """Random edge list [a, b, w] on nodes 0..n-1 with about m edges (exactly m if possible)."""
    edges = []
    seen = set()
    if connected and n > 1:
        perm = list(range(n))
        r.shuffle(perm)
        for i in range(1, n):
            a, b = perm[i], perm[r.randrange(i)]
            seen.add((min(a, b), max(a, b)))
            edges.append([a, b, r.randint(lo, hi)])
    maxm = n * (n - 1) // 2 if simple else 10 ** 9
    target = min(m, maxm) if n > 1 else 0
    tries = 0
    while len(edges) < target and tries < 50 * (target + 5):
        tries += 1
        a, b = r.sample(range(n), 2)
        key = (min(a, b), max(a, b))
        if simple and key in seen:
            continue
        seen.add(key)
        edges.append([a, b, r.randint(lo, hi)])
    r.shuffle(edges)
    for e in edges:
        if r.random() < 0.5:
            e[0], e[1] = e[1], e[0]
    return edges


def _components(n, edges):
    parent = list(range(n))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for a, b, *_ in edges:
        parent[find(a)] = find(b)
    return len({find(i) for i in range(n)})


def _check_edges(n, edges, maxn, maxm, wlo, whi, connected=False, simple=False):
    assert 1 <= n <= maxn and len(edges) <= maxm, (n, len(edges))
    seen = set()
    for e in edges:
        assert len(e) == 3
        a, b, w = e
        assert 0 <= a < n and 0 <= b < n and a != b and wlo <= w <= whi
        if simple:
            key = (min(a, b), max(a, b))
            assert key not in seen, "parallel edge"
            seen.add(key)
    if connected:
        assert _components(n, edges) == 1, "graph not connected"


def _big(seed, n, m, lo, hi, connected=True, simple=True):
    return _graph(rnd(seed), n, m, lo, hi, connected, simple)


# ---------------------------------------------------------------- EASY

p = add(
    id="cheapest-city-links", title="Cheapest Way to Link All Cities", diff="Easy", topic=T, tier="must",
    fn="minLinkCost", params=[("n", "int"), ("roads", "int[][]")], ret="int", cmp="exact",
    desc="<p>There are <code>n</code> cities numbered <code>0</code> to <code>n - 1</code>. Each entry <code>roads[i] = [a, b, cost]</code> describes a road that <em>may</em> be built between cities <code>a</code> and <code>b</code> (in both directions) for <code>cost</code>.</p><p>Choose some of the roads so that every city can reach every other city using the chosen roads, and make the total cost as small as possible. Return that minimum total cost, or <code>-1</code> if no choice of roads can connect all the cities.</p><pre>n = 4, roads = [[0,1,1],[1,2,2],[0,2,3],[2,3,4]]   -> 7   (build 0-1, 1-2, 2-3)\nn = 3, roads = [[0,1,5]]                          -> -1  (city 2 is unreachable)</pre>",
    constraints=["1 &le; n &le; 2,000", "0 &le; roads.length &le; 4,000", "roads[i] = [a, b, cost] with 0 &le; a, b &lt; n and a &ne; b", "1 &le; cost &le; 100,000", "Several roads may join the same pair of cities"],
    hints=["Costs are positive, so an optimal choice never contains a cycle: any road that closes a cycle can be dropped. You are looking for a cheapest tree.",
           "Think greedy: always prefer the cheapest road, but only keep it if it joins two groups of cities that are not yet connected.",
           "Sort the roads by cost and process them in that order with a union-find (disjoint set) structure. Keep a road when its endpoints are in different sets, then merge the sets. If you kept exactly n - 1 roads, return the sum, otherwise return -1."],
    editorial=["This is the minimum spanning tree problem, solved by Kruskal's algorithm. Sort the roads by cost. Scan them in order, and keep a road if and only if its two cities currently belong to different connected groups; then merge the groups. A road rejected this way would close a cycle, and the cheapest edge crossing any cut is always safe, which is why the greedy choice is optimal.",
               "A union-find with path compression makes each check almost constant time, so the total cost is dominated by the sort: O(m log m). A spanning tree of n cities has exactly n - 1 roads, so if fewer were kept the cities cannot all be connected and the answer is -1. For n = 1 nothing needs to be built and the answer is 0."],
    time="O(m log m)", space="O(n)",
    solution='''def minLinkCost(n, roads):
    parent = list(range(n))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    total = 0
    used = 0
    for a, b, c in sorted(roads, key=lambda e: e[2]):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb
            total += c
            used += 1
            if used == n - 1:
                break
    return total if used == n - 1 else -1
''',
    tests=[[4, [[0, 1, 1], [1, 2, 2], [0, 2, 3], [2, 3, 4]]], [3, [[0, 1, 5]]], [1, []],
           [2, []], [2, [[0, 1, 9], [1, 0, 4], [0, 1, 7]]],
           [5, [[0, 1, 1], [1, 2, 1], [2, 3, 1], [3, 4, 1], [0, 4, 1]]],
           [4, [[0, 1, 3], [2, 3, 3]]],
           [6, [[0, 1, 10], [1, 2, 10], [2, 3, 10], [3, 4, 10], [4, 5, 10], [0, 5, 1], [0, 3, 2], [1, 4, 2]]],
           [5, [[0, 1, 100000], [1, 2, 100000], [2, 3, 100000], [3, 4, 100000]]]],
)
p["tests"].append([2000, _big(7101, 2000, 4000, 1, 100000)])
p["tests"].append([1500, _big(7102, 1500, 1400, 1, 100000, connected=False, simple=False)])
p["tests"].append([1000, _big(7103, 1000, 2500, 1, 5, simple=False)])


def b_links(n, roads):
    best = -1
    for mask in range(1 << len(roads)):
        chosen = [roads[i] for i in range(len(roads)) if (mask >> i) & 1]
        if _components(n, chosen) == 1:
            c = sum(e[2] for e in chosen)
            if best < 0 or c < best:
                best = c
    return best


def g_links(r):
    n = r.randint(1, 5)
    m = r.randint(0, 7)
    return [n, _graph(r, n, m, 1, r.choice([2, 5, 9]), connected=r.random() < 0.5, simple=r.random() < 0.5)]


def v_links(tests):
    for t in tests:
        n, roads = t["args"]
        _check_edges(n, roads, 2000, 4000, 1, 100000)
    assert any(t["expected"] == -1 for t in tests) and any(t["expected"] > 0 for t in tests)


CHECKS["cheapest-city-links"] = (b_links, g_links, "exact")
VALIDATE["cheapest-city-links"] = v_links

p = add(
    id="min-bottleneck-spanning-tree", title="Lightest Heaviest Cable", diff="Easy", topic=T, tier="common",
    fn="minBottleneck", params=[("n", "int"), ("cables", "int[][]")], ret="int", cmp="exact",
    desc="<p>A network has <code>n</code> servers numbered <code>0</code> to <code>n - 1</code>. Each entry <code>cables[i] = [a, b, w]</code> is a possible cable between servers <code>a</code> and <code>b</code> whose rating is <code>w</code>.</p><p>You want to pick a set of cables that connects all the servers, and you want the <strong>highest rating among the picked cables</strong> to be as low as possible (the total does not matter). Return that lowest possible highest rating. Return <code>-1</code> if the servers cannot all be connected, and <code>0</code> if <code>n = 1</code> because no cable is needed.</p><pre>n = 4, cables = [[0,1,5],[1,2,1],[2,3,1],[0,3,4]]   -> 4   (use 1-2, 2-3, 0-3)\nn = 3, cables = [[0,1,2]]                           -> -1</pre>",
    constraints=["1 &le; n &le; 2,000", "0 &le; cables.length &le; 3,000", "cables[i] = [a, b, w] with 0 &le; a, b &lt; n and a &ne; b", "1 &le; w &le; 1,000,000", "Several cables may join the same pair of servers"],
    hints=["Imagine you may only use cables with rating at most R. For which R is the network connected?",
           "The answer is the smallest R for which the cables rated at most R connect everything. That could be found with binary search plus a graph search, but there is a way that needs only one pass.",
           "Process cables from the lowest rating up, merging components with union-find. The rating of the cable that finally reduces the number of components to one is the answer."],
    editorial=["Sort cables by rating and add them one at a time with a union-find structure, exactly like Kruskal's algorithm. The first moment the whole graph becomes a single component, the cable just added has the lowest rating R such that the cables rated at most R connect all servers, so R is the answer. If all cables are processed and there are still several components, the answer is -1.",
               "This works because the minimum spanning tree also minimises its heaviest edge (a minimum bottleneck spanning tree). The statement can also be solved with binary search on R and a BFS on the cables of rating at most R, which costs O((n + m) log m) instead of one sort."],
    time="O(m log m)", space="O(n)",
    solution='''def minBottleneck(n, cables):
    if n == 1:
        return 0
    parent = list(range(n))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    comps = n
    for a, b, w in sorted(cables, key=lambda e: e[2]):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb
            comps -= 1
            if comps == 1:
                return w
    return -1
''',
    tests=[[4, [[0, 1, 5], [1, 2, 1], [2, 3, 1], [0, 3, 4]]], [3, [[0, 1, 2]]], [1, []],
           [2, [[0, 1, 1000000]]], [2, []], [3, [[0, 1, 4], [1, 2, 4], [0, 2, 1]]],
           [4, [[0, 1, 1], [2, 3, 1]]], [5, [[0, 1, 7], [1, 2, 3], [2, 3, 9], [3, 4, 2], [0, 4, 8], [1, 3, 6]]],
           [3, [[0, 1, 1], [0, 1, 2], [1, 2, 6], [1, 2, 3]]]],
)
p["tests"].append([2000, _big(7201, 2000, 3000, 1, 1000000)])
p["tests"].append([2000, _big(7202, 2000, 1990, 1, 1000000, connected=False, simple=False)])
p["tests"].append([1500, _big(7203, 1500, 3000, 1, 30, simple=False)])


def b_bottleneck(n, cables):
    if n == 1:
        return 0
    for t in sorted({e[2] for e in cables}):
        sub = [e for e in cables if e[2] <= t]
        if _components(n, sub) == 1:
            return t
    return -1


def g_bottleneck(r):
    n = r.randint(1, 6)
    return [n, _graph(r, n, r.randint(0, 8), 1, r.choice([3, 8, 20]), connected=r.random() < 0.6, simple=r.random() < 0.5)]


def v_bottleneck(tests):
    for t in tests:
        n, cables = t["args"]
        _check_edges(n, cables, 2000, 3000, 1, 10 ** 6)
    assert any(t["expected"] == -1 for t in tests)


CHECKS["min-bottleneck-spanning-tree"] = (b_bottleneck, g_bottleneck, "exact")
VALIDATE["min-bottleneck-spanning-tree"] = v_bottleneck

p = add(
    id="max-weight-spanning-forest", title="Maximum Weight Spanning Forest", diff="Easy", topic=T, tier="extra",
    fn="maxForestWeight", params=[("n", "int"), ("edges", "int[][]")], ret="int", cmp="exact",
    desc="<p>An undirected graph has <code>n</code> nodes numbered <code>0</code> to <code>n - 1</code> and weighted edges <code>edges[i] = [a, b, w]</code>. Weights can be negative.</p><p>A <em>spanning forest</em> is a set of edges that contains no cycle and still connects every pair of nodes that were connected in the full graph (it has one tree for each connected component). Return the largest possible total weight of a spanning forest.</p><pre>n = 5, edges = [[0,1,4],[1,2,-2],[0,2,3],[3,4,-1]]   -> 6\n(component {0,1,2}: keep 0-1 and 0-2 for 7; component {3,4}: the only edge, -1)</pre>",
    constraints=["1 &le; n &le; 2,000", "0 &le; edges.length &le; 4,000", "edges[i] = [a, b, w] with 0 &le; a, b &lt; n and a &ne; b", "-100,000 &le; w &le; 100,000", "Several edges may join the same pair of nodes"],
    hints=["Minimum spanning trees pick the cheapest edges. What would you change to get the heaviest tree?",
           "Negative edges are not optional: a forest must still connect each component, so a bridge of negative weight has to be kept.",
           "Run Kruskal in descending order of weight (sort by -w) with union-find, keeping every edge that joins two different components. Disconnected graphs need no special handling; you just end up with a forest."],
    editorial=["A maximum spanning forest is a minimum spanning forest of the graph with all weights negated, and negating does not change which edges are acceptable. So run Kruskal's algorithm with the edges sorted from the heaviest to the lightest: keep an edge if its endpoints are in different components, and merge them.",
               "Nothing special is needed for disconnected graphs, because Kruskal stops adding edges only when no remaining edge joins two components; every component ends up with its own tree. Negative weights are also fine: an edge that is needed to connect a component is kept even if it hurts the total, because a forest must span every component. Time is O(m log m)."],
    time="O(m log m)", space="O(n)",
    solution='''def maxForestWeight(n, edges):
    parent = list(range(n))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    total = 0
    for a, b, w in sorted(edges, key=lambda e: -e[2]):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb
            total += w
    return total
''',
    tests=[[5, [[0, 1, 4], [1, 2, -2], [0, 2, 3], [3, 4, -1]]], [1, []], [3, []], [2, [[0, 1, -7]]],
           [2, [[0, 1, -7], [0, 1, -3], [1, 0, -9]]],
           [4, [[0, 1, 5], [1, 2, 5], [2, 3, 5], [3, 0, 5]]],
           [6, [[0, 1, -1], [1, 2, -1], [0, 2, -5], [3, 4, 8], [4, 5, 8], [3, 5, -8]]],
           [4, [[0, 1, 100000], [2, 3, 100000], [1, 2, -100000], [0, 3, 99999]]]],
)
p["tests"].append([2000, _big(7301, 2000, 4000, -100000, 100000)])
p["tests"].append([1500, _big(7302, 1500, 1200, -100000, 100000, connected=False, simple=False)])
p["tests"].append([1000, _big(7303, 1000, 2500, -3, 3, simple=False)])


def b_forest(n, edges):
    comps = _components(n, edges)
    need = n - comps
    best = None
    for combo in combinations(range(len(edges)), need):
        sub = [edges[i] for i in combo]
        if _components(n, sub) == comps:  # need edges and as many merges as possible => acyclic forest
            s = sum(e[2] for e in sub)
            if best is None or s > best:
                best = s
    return best


def g_forest(r):
    n = r.randint(1, 6)
    return [n, _graph(r, n, r.randint(0, 8), -5, 5, connected=r.random() < 0.4, simple=r.random() < 0.5)]


def v_forest(tests):
    for t in tests:
        n, edges = t["args"]
        _check_edges(n, edges, 2000, 4000, -100000, 100000)
    assert any(t["args"][0] > 1 and _components(*t["args"]) > 1 for t in tests)


CHECKS["max-weight-spanning-forest"] = (b_forest, g_forest, "exact")
VALIDATE["max-weight-spanning-forest"] = v_forest

# ---------------------------------------------------------------- MEDIUM

p = add(
    id="unique-minimum-spanning-tree", title="Is the Cheapest Network Unique?", diff="Medium", topic=T, tier="common",
    fn="isMstUnique", params=[("n", "int"), ("edges", "int[][]")], ret="bool", cmp="exact",
    desc="<p>A connected, weighted, undirected graph has <code>n</code> nodes numbered <code>0</code> to <code>n - 1</code>; <code>edges[i] = [a, b, w]</code> is an edge between <code>a</code> and <code>b</code> of weight <code>w</code>. Edges are distinguished by their position in the list, so two parallel edges of equal weight count as different edges.</p><p>A <em>minimum spanning tree</em> (MST) is a set of <code>n - 1</code> edges connecting all nodes with the smallest possible total weight. Return <code>true</code> if the graph has exactly one MST, and <code>false</code> if it has more than one.</p><pre>n = 3, edges = [[0,1,1],[1,2,2],[0,2,3]]   -> true\nn = 3, edges = [[0,1,1],[1,2,2],[0,2,2]]   -> false   (1-2 or 0-2 can be used with 0-1)</pre>",
    constraints=["1 &le; n &le; 2,000", "n - 1 &le; edges.length &le; 4,000", "edges[i] = [a, b, w] with 0 &le; a, b &lt; n and a &ne; b", "1 &le; w &le; 1,000,000", "The graph is connected; parallel edges are allowed"],
    hints=["If all weights are different, the MST is unique. Trouble can only come from edges with equal weights.",
           "Process edges in groups of equal weight. At the start of a group, some edges already have both ends in the same component and are useless. The others are candidates.",
           "For each group, count the candidates (edges joining different components at the start of the group) and then count how many of them Kruskal really adds while merging the group one edge at a time. If a candidate was rejected because an earlier edge of the same group connected its ends, a different tree of the same weight exists."],
    editorial=["Run Kruskal's algorithm, but treat each block of equal-weight edges together. Let the components at the start of a block be fixed. A <em>candidate</em> is an edge of the block whose endpoints lie in different components at that moment. Then go through the candidates, adding those that still join different components and counting them.",
               "If some candidate is rejected because earlier candidates of the same weight already linked its endpoints, then that candidate could replace one of those edges and give another tree of exactly the same weight, so the MST is not unique. If in every block the number of candidates equals the number actually added, no such swap exists and the MST is unique. Equivalently, the MST is unique exactly when no non-tree edge ties with the heaviest edge on its tree path. Cost: O(m log m)."],
    time="O(m log m)", space="O(n)",
    solution='''def isMstUnique(n, edges):
    parent = list(range(n))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    es = sorted(edges, key=lambda e: e[2])
    i = 0
    m = len(es)
    while i < m:
        j = i
        while j < m and es[j][2] == es[i][2]:
            j += 1
        candidates = 0
        for k in range(i, j):
            if find(es[k][0]) != find(es[k][1]):
                candidates += 1
        added = 0
        for k in range(i, j):
            ra, rb = find(es[k][0]), find(es[k][1])
            if ra != rb:
                parent[ra] = rb
                added += 1
        if added != candidates:
            return False
        i = j
    return True
''',
    tests=[[3, [[0, 1, 1], [1, 2, 2], [0, 2, 3]]], [3, [[0, 1, 1], [1, 2, 2], [0, 2, 2]]], [1, []],
           [2, [[0, 1, 4]]], [2, [[0, 1, 4], [1, 0, 4]]], [2, [[0, 1, 4], [1, 0, 5]]],
           [3, [[0, 1, 1], [1, 2, 1], [0, 2, 1]]],
           [4, [[0, 1, 1], [1, 2, 1], [2, 3, 1], [0, 3, 2], [0, 2, 2]]],
           [4, [[0, 1, 1], [1, 2, 3], [2, 3, 3], [0, 3, 3]]],
           [5, [[0, 1, 2], [1, 2, 2], [2, 3, 2], [3, 4, 2], [0, 4, 3], [1, 3, 3]]],
           [4, [[0, 1, 1], [0, 2, 5], [0, 3, 6], [1, 2, 5], [2, 3, 7]]]],
)
_r = rnd(7401)
_w = _r.sample(range(1, 1000001), 4000)
_e = _big(7402, 2000, 4000, 1, 1)
for _i in range(len(_e)):
    _e[_i][2] = _w[_i]
p["tests"].append([2000, _e])                                      # all distinct => true
_tree = _big(7403, 2000, 1999, 1, 1)
p["tests"].append([2000, [[a, b, 2 * (i + 1)] for i, (a, b, _) in enumerate(_tree)]
                   + [[0, 1, 999999]]])       # a single extra edge, heavier than everything => true
_e3 = _big(7404, 1000, 2500, 1, 40)
p["tests"].append([1000, _e3])                                      # lots of ties => false


def b_unique(n, edges):
    if n == 1:
        return True
    trees = []
    for combo in combinations(range(len(edges)), n - 1):
        sub = [edges[i] for i in combo]
        if _components(n, sub) == 1:
            trees.append(sum(e[2] for e in sub))
    return trees.count(min(trees)) == 1


def g_unique(r):
    n = r.randint(1, 6)
    return [n, _graph(r, n, r.randint(n - 1, min(9, n * (n - 1) // 2) + 1), 1, r.choice([2, 3, 6, 30]), simple=r.random() < 0.7)]


def v_unique(tests):
    for t in tests:
        n, edges = t["args"]
        _check_edges(n, edges, 2000, 4000, 1, 1000000, connected=True)
        assert len(edges) >= n - 1
    outs = [t["expected"] for t in tests]
    assert True in outs and False in outs


CHECKS["unique-minimum-spanning-tree"] = (b_unique, g_unique, "exact")
VALIDATE["unique-minimum-spanning-tree"] = v_unique

p = add(
    id="prim-visit-order", title="Prim's Growth Order", diff="Medium", topic=T, tier="common",
    fn="primOrder", params=[("n", "int"), ("edges", "int[][]")], ret="int[]", cmp="exact",
    desc="<p>A connected, weighted, undirected graph has <code>n</code> nodes numbered <code>0</code> to <code>n - 1</code> and edges <code>edges[i] = [a, b, w]</code>. A tree is grown as in Prim's algorithm: it starts with node <code>0</code> only. In every step, look at all edges with exactly one endpoint in the tree and take one with the smallest weight; if several edges have that weight, prefer the one whose <strong>outside endpoint has the smaller label</strong>. The outside endpoint joins the tree.</p><p>Return the nodes in the order in which they join the tree (the first element is <code>0</code>).</p><pre>n = 5, edges = [[0,1,4],[0,2,1],[2,1,2],[1,3,5],[2,3,5],[3,4,1]]   -> [0, 2, 1, 3, 4]</pre><p>Here node 2 joins first (weight 1), then node 1 (weight 2 via node 2), then node 3 (weight 5 from either side), then node 4.</p>",
    constraints=["1 &le; n &le; 2,000", "n - 1 &le; edges.length &le; 4,000", "edges[i] = [a, b, w] with 0 &le; a, b &lt; n and a &ne; b", "1 &le; w &le; 1,000", "The graph is connected; parallel edges are allowed"],
    hints=["Simulate the process: keep a set of nodes in the tree and repeatedly choose the best edge leaving it. A direct simulation is O(n &middot; m); can you speed up the choice?",
           "Keep a min-heap of candidate edges leaving the tree, ordered by (weight, outside node). Whenever a node joins the tree, push all its edges to nodes that are still outside.",
           "When you pop an entry whose node is already in the tree, skip it (a lazy deletion). The first valid entry popped is exactly the edge Prim would take, and the tie rule is built into the tuple order."],
    editorial=["Prim's algorithm grows one tree. Instead of scanning all edges in each step, store the edges leaving the tree in a binary heap. The heap orders entries by the tuple <code>(weight, node)</code>, where <code>node</code> is the outside endpoint, which implements both the weight rule and the tie-break at the same time.",
               "After adding a node, push every edge from it to a node not yet in the tree. When popping, ignore entries whose node has meanwhile joined the tree through a cheaper edge. Each edge is pushed at most twice and each push or pop costs O(log m), so the total is O(m log m). The answer is the order in which nodes are accepted."],
    time="O(m log m)", space="O(n + m)",
    solution='''import heapq


def primOrder(n, edges):
    adj = [[] for _ in range(n)]
    for a, b, w in edges:
        adj[a].append((w, b))
        adj[b].append((w, a))
    seen = [False] * n
    seen[0] = True
    order = [0]
    heap = list(adj[0])
    heapq.heapify(heap)
    while heap and len(order) < n:
        w, v = heapq.heappop(heap)
        if seen[v]:
            continue
        seen[v] = True
        order.append(v)
        for item in adj[v]:
            if not seen[item[1]]:
                heapq.heappush(heap, item)
    return order
''',
    tests=[[5, [[0, 1, 4], [0, 2, 1], [2, 1, 2], [1, 3, 5], [2, 3, 5], [3, 4, 1]]], [1, []], [2, [[1, 0, 9]]],
           [3, [[0, 1, 2], [0, 2, 2], [1, 2, 1]]],
           [4, [[0, 3, 1], [0, 2, 1], [0, 1, 1], [1, 2, 1]]],
           [4, [[0, 1, 5], [1, 2, 1], [2, 3, 1], [0, 3, 6]]],
           [5, [[0, 4, 3], [0, 3, 3], [4, 3, 1], [3, 2, 7], [4, 1, 7], [2, 1, 7]]],
           [5, [[0, 1, 1], [0, 1, 2], [1, 2, 1], [2, 3, 1], [3, 4, 1], [4, 0, 1]]]],
)
p["tests"].append([2000, _big(7501, 2000, 4000, 1, 1000)])
p["tests"].append([2000, _big(7502, 2000, 4000, 1, 4, simple=False)])
p["tests"].append([1500, _big(7503, 1500, 1499, 1, 1)])


def b_prim(n, edges):
    inside = {0}
    order = [0]
    while len(order) < n:
        best = None
        for a, b, w in edges:
            if (a in inside) != (b in inside):
                u = b if a in inside else a
                if best is None or (w, u) < best:
                    best = (w, u)
        inside.add(best[1])
        order.append(best[1])
    return order


def g_prim(r):
    n = r.randint(1, 7)
    return [n, _graph(r, n, r.randint(n - 1, 11), 1, r.choice([1, 2, 4, 9]), simple=r.random() < 0.6)]


def v_prim(tests):
    for t in tests:
        n, edges = t["args"]
        _check_edges(n, edges, 2000, 4000, 1, 1000, connected=True)
        assert sorted(t["expected"]) == list(range(n)) and t["expected"][0] == 0


CHECKS["prim-visit-order"] = (b_prim, g_prim, "exact")
VALIDATE["prim-visit-order"] = v_prim

p = add(
    id="minimax-path-queries", title="Lowest Peak Between Two Cities", diff="Medium", topic=T, tier="common",
    fn="lowestPeak", params=[("n", "int"), ("roads", "int[][]"), ("queries", "int[][]")], ret="int[]", cmp="exact",
    desc="<p>There are <code>n</code> cities numbered <code>0</code> to <code>n - 1</code>. Each road <code>roads[i] = [a, b, h]</code> joins cities <code>a</code> and <code>b</code> in both directions, and <code>h</code> is the height of the highest pass on that road.</p><p>For a trip from city <code>u</code> to city <code>v</code>, the <em>peak</em> of a route is the largest pass height among the roads it uses. For every query <code>queries[j] = [u, v]</code>, return the smallest peak over all possible routes from <code>u</code> to <code>v</code>. The answer is <code>0</code> when <code>u = v</code> (an empty route) and <code>-1</code> when <code>v</code> cannot be reached from <code>u</code>.</p><pre>n = 4, roads = [[0,1,5],[1,2,3],[0,2,7],[2,3,9]], queries = [[0,2],[0,3],[1,1]]   -> [5, 9, 0]</pre><p>From 0 to 2 the direct road has height 7, but going 0-1-2 only needs height 5.</p>",
    constraints=["1 &le; n &le; 1,500", "0 &le; roads.length &le; 4,000", "1 &le; queries.length &le; 1,500", "0 &le; a, b, u, v &lt; n, a &ne; b for roads", "1 &le; h &le; 1,000,000", "Roads can be parallel; the graph may be disconnected"],
    hints=["Answering each query with its own search is too slow for many queries. Think about which roads can possibly matter for a route with small peak.",
           "Add roads in increasing order of height with union-find. At the moment u and v first end up in the same component, the road just added is the smallest possible peak.",
           "To answer all queries without extra structure, merge components small-to-large and keep in each component the set of query ids touching it. When two components merge, any query id that appears on both sides is answered with the current road height."],
    editorial=["Roads are added by increasing height (Kruskal order). u and v become connected exactly when the road that finishes a route with minimum peak is added, so the answer to a query is the height of the road whose merge first puts u and v into the same component. Equivalently, it is the largest edge on the path between u and v in a minimum spanning tree.",
               "To find that moment for all queries at once, give every component a set of query ids (a query id is placed in the sets of both its endpoints). When two components merge, iterate over the smaller set: if the id is already in the larger set, both endpoints are now together and the query is answered with the current height; otherwise move it into the larger set. Small-to-large merging moves each id O(log q) times, so the total is O((m + q) log m). Queries never answered get -1; queries with u = v get 0."],
    time="O(m log m + q log q)", space="O(n + m + q)",
    solution='''def lowestPeak(n, roads, queries):
    q = len(queries)
    ans = [-1] * q
    parent = list(range(n))
    pending = [set() for _ in range(n)]
    for j, (u, v) in enumerate(queries):
        if u == v:
            ans[j] = 0
        else:
            pending[u].add(j)
            pending[v].add(j)

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for a, b, h in sorted(roads, key=lambda e: e[2]):
        ra, rb = find(a), find(b)
        if ra == rb:
            continue
        if len(pending[ra]) < len(pending[rb]):
            ra, rb = rb, ra
        for j in pending[rb]:
            if j in pending[ra]:
                ans[j] = h
                pending[ra].discard(j)
            else:
                pending[ra].add(j)
        pending[rb] = set()
        parent[rb] = ra
    return ans
''',
    tests=[[4, [[0, 1, 5], [1, 2, 3], [0, 2, 7], [2, 3, 9]], [[0, 2], [0, 3], [1, 1]]],
           [1, [], [[0, 0]]], [2, [], [[0, 1], [1, 0], [1, 1]]],
           [3, [[0, 1, 4], [0, 1, 2]], [[0, 1], [1, 2], [2, 2]]],
           [5, [[0, 1, 1], [1, 2, 2], [2, 3, 3], [3, 4, 4], [0, 4, 10]], [[0, 4], [4, 0], [1, 3], [2, 2]]],
           [6, [[0, 1, 5], [1, 2, 5], [3, 4, 1], [4, 5, 8], [2, 3, 20]], [[0, 5], [0, 2], [3, 5], [1, 4], [5, 0]]],
           [4, [[0, 1, 7], [1, 2, 7], [2, 3, 7], [3, 0, 7]], [[0, 2], [1, 3], [0, 1]]],
           [3, [[0, 1, 1000000], [1, 2, 1]], [[0, 2], [2, 0], [1, 2]]]],
)


def _mm_test(seed, n, m, q, hi, connected):
    r = rnd(seed)
    return [n, _graph(r, n, m, 1, hi, connected=connected), [[r.randrange(n), r.randrange(n)] for _ in range(q)]]


p["tests"].append(_mm_test(7601, 1500, 4000, 1500, 1000000, True))
p["tests"].append(_mm_test(7602, 1000, 800, 600, 1000000, False))
p["tests"].append(_mm_test(7603, 1000, 1999, 800, 50, True))


def b_minimax(n, roads, queries):
    out = []
    for u, v in queries:
        if u == v:
            out.append(0)
            continue
        res = -1
        for t in sorted({e[2] for e in roads}):
            seen = {u}
            stack = [u]
            while stack:
                x = stack.pop()
                for a, b, h in roads:
                    if h <= t:
                        if a == x and b not in seen:
                            seen.add(b)
                            stack.append(b)
                        elif b == x and a not in seen:
                            seen.add(a)
                            stack.append(a)
            if v in seen:
                res = t
                break
        out.append(res)
    return out


def g_minimax(r):
    n = r.randint(1, 6)
    roads = _graph(r, n, r.randint(0, 8), 1, r.choice([3, 9, 20]), connected=r.random() < 0.4, simple=r.random() < 0.5)
    return [n, roads, [[r.randrange(n), r.randrange(n)] for _ in range(r.randint(1, 6))]]


def v_minimax(tests):
    for t in tests:
        n, roads, qs = t["args"]
        _check_edges(n, roads, 1500, 4000, 1, 1000000)
        assert 1 <= len(qs) <= 1500 and all(len(x) == 2 and 0 <= x[0] < n and 0 <= x[1] < n for x in qs)
        assert len(t["expected"]) == len(qs)
    assert any(-1 in t["expected"] for t in tests)


CHECKS["minimax-path-queries"] = (b_minimax, g_minimax, "exact")
VALIDATE["minimax-path-queries"] = v_minimax

p = add(
    id="max-spacing-k-clusters", title="Widest Gap Between K Clusters", diff="Medium", topic=T, tier="common",
    fn="maxSpacing", params=[("points", "int[][]"), ("k", "int")], ret="int", cmp="exact",
    desc="<p>You are given <code>n</code> points on a grid, <code>points[i] = [x, y]</code>. The distance between two points is the Manhattan distance <code>|x1 - x2| + |y1 - y2|</code>.</p><p>Split the points into exactly <code>k</code> non-empty clusters. The <em>spacing</em> of a split is the smallest distance between two points that belong to <strong>different</strong> clusters. Return the largest spacing that any split into <code>k</code> clusters can achieve.</p><pre>points = [[0,0],[1,0],[10,0],[11,0],[30,0]], k = 3   -> 9\n(clusters {0,1}, {10,11}, {30}: the closest cross-cluster pair is 1 and 10)</pre>",
    constraints=["2 &le; k &le; n &le; 700", "points[i] = [x, y] with 0 &le; x, y &le; 1,000,000", "Points may coincide"],
    hints=["With k = n every point is alone and the spacing is the smallest pairwise distance. With fewer clusters, which pairs of points must be placed together?",
           "Two points at distance d can be separated only if all other pairs that are closer than d are already inside clusters. Think of merging the closest pair first, again and again, like Kruskal.",
           "Kruskal's algorithm stops being useful once exactly k groups remain: the next edge that would join two groups is the spacing. Equivalently, compute the MST and take its (k-1)-th largest edge weight."],
    editorial=["Merging the closest pairs greedily (Kruskal, stopping at k components) produces the k-clustering with maximum spacing. Right after the last merge the groups are k, and the cheapest edge between two different groups is the next edge Kruskal would accept, which is the spacing.",
               "Instead of sorting all n(n-1)/2 distances, build the MST with Prim's algorithm in O(n&sup2;) time: it has n - 1 edges, and removing its k - 1 heaviest edges leaves exactly k clusters. The spacing is then the (k-1)-th largest MST edge. Any other split into k clusters must cut at least one MST edge of weight no larger than that value, which proves optimality."],
    time="O(n&sup2;)", space="O(n)",
    solution='''def maxSpacing(points, k):
    n = len(points)
    INF = float('inf')
    dist = [INF] * n
    used = [False] * n
    dist[0] = 0
    weights = []
    for step in range(n):
        u = -1
        best = INF
        for i in range(n):
            if not used[i] and dist[i] < best:
                best = dist[i]
                u = i
        used[u] = True
        if step > 0:
            weights.append(best)
        ux, uy = points[u]
        for i in range(n):
            if not used[i]:
                d = abs(points[i][0] - ux) + abs(points[i][1] - uy)
                if d < dist[i]:
                    dist[i] = d
    weights.sort(reverse=True)
    return weights[k - 2]
''',
    tests=[[[[0, 0], [1, 0], [10, 0], [11, 0], [30, 0]], 3], [[[0, 0], [5, 5]], 2], [[[3, 3], [3, 3], [3, 3]], 2],
           [[[0, 0], [1, 0], [10, 0], [11, 0], [30, 0]], 2], [[[0, 0], [1, 0], [10, 0], [11, 0], [30, 0]], 5],
           [[[0, 0], [0, 10], [10, 0], [10, 10]], 2], [[[0, 0], [0, 10], [10, 0], [10, 10]], 4],
           [[[0, 0], [0, 1], [0, 2], [0, 3], [100, 100], [100, 101]], 3],
           [[[1000000, 1000000], [0, 0], [500000, 500000]], 2]],
)
_r = rnd(7701)
p["tests"].append([[[_r.randint(0, 1000000), _r.randint(0, 1000000)] for _ in range(700)], 10])
p["tests"].append([[[_r.randint(0, 1000000), _r.randint(0, 1000000)] for _ in range(700)], 700])
_cl = []
for _c in range(5):
    _cx, _cy = _r.randint(0, 900000), _r.randint(0, 900000)
    _cl += [[_cx + _r.randint(0, 1000), _cy + _r.randint(0, 1000)] for _ in range(140)]
_r.shuffle(_cl)
p["tests"].append([_cl, 5])
p["tests"].append([[[_r.randint(0, 30), _r.randint(0, 30)] for _ in range(600)], 20])


def b_spacing(points, k):
    n = len(points)
    best = -1

    def d(i, j):
        return abs(points[i][0] - points[j][0]) + abs(points[i][1] - points[j][1])

    def rec(i, labels, used):
        nonlocal best
        if i == n:
            if used == k:
                s = min(d(a, b) for a in range(n) for b in range(a + 1, n) if labels[a] != labels[b])
                best = max(best, s)
            return
        for c in range(min(used + 1, k)):
            rec(i + 1, labels + [c], max(used, c + 1))

    rec(0, [], 0)
    return best


def g_spacing(r):
    n = r.randint(2, 6)
    pts = [[r.randint(0, 8), r.randint(0, 8)] for _ in range(n)]
    return [pts, r.randint(2, n)]


def v_spacing(tests):
    for t in tests:
        pts, k = t["args"]
        assert 2 <= k <= len(pts) <= 700
        assert all(len(q) == 2 and 0 <= q[0] <= 1000000 and 0 <= q[1] <= 1000000 for q in pts)


CHECKS["max-spacing-k-clusters"] = (b_spacing, g_spacing, "exact")
VALIDATE["max-spacing-k-clusters"] = v_spacing

p = add(
    id="connect-points-min-axis-cost", title="Link Towers by the Shorter Axis", diff="Medium", topic=T, tier="extra",
    fn="minAxisLinkCost", params=[("points", "int[][]")], ret="int", cmp="exact",
    desc="<p>There are <code>n</code> towers at positions <code>points[i] = [x, y]</code>. Building a cable between towers <code>i</code> and <code>j</code> costs <code>min(|xi - xj|, |yi - yj|)</code>: only the <em>smaller</em> of the two coordinate differences counts.</p><p>Return the minimum total cost of cables needed so that every tower is connected to every other tower, directly or through other towers.</p><pre>points = [[0,0],[3,1],[7,2]]   -> 2\n(0-1 costs min(3,1) = 1, 1-2 costs min(4,1) = 1, 0-2 costs min(7,2) = 2)</pre>",
    constraints=["1 &le; n &le; 4,000", "points[i] = [x, y] with 0 &le; x, y &le; 100,000", "Points may coincide"],
    hints=["Taking every pair gives about n&sup2;/2 candidate cables, which is too many for n = 4,000 in the worst case. You need a much smaller candidate set that still contains an MST.",
           "Sort the towers by x. For a cable between towers that are not neighbours in this order, there is a tower in between with both x-differences smaller. What does that say about the cost of the cables that go through it?",
           "Only neighbours in the x-sorted order and neighbours in the y-sorted order need to be considered: that is at most 2(n - 1) cables. Run Kruskal on them."],
    editorial=["Consider a cable between towers i and j with cost c = min(dx, dy), and suppose c = dx (the case c = dy is symmetric with the y-order). If another tower k lies between i and j in the x-order, then both |xi - xk| and |xk - xj| are at most dx, so the cables i-k and k-j each cost at most c. The cable i-j is then a heaviest edge of the cycle i-k-j, and by the cycle property it is not needed in some minimum spanning tree.",
               "Therefore an MST exists that uses only cables between towers that are neighbours in the x-sorted order or neighbours in the y-sorted order. That is at most 2(n - 1) cables. Sort them by cost and run Kruskal with union-find: O(n log n) in total, in contrast to O(n&sup2; log n) for the complete graph."],
    time="O(n log n)", space="O(n)",
    solution='''def minAxisLinkCost(points):
    n = len(points)
    if n == 1:
        return 0
    edges = []
    for axis in (0, 1):
        order = sorted(range(n), key=lambda i: points[i][axis])
        for a, b in zip(order, order[1:]):
            dx = abs(points[a][0] - points[b][0])
            dy = abs(points[a][1] - points[b][1])
            edges.append((min(dx, dy), a, b))
    edges.sort()
    parent = list(range(n))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    total = 0
    for c, a, b in edges:
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb
            total += c
    return total
''',
    tests=[[[[0, 0], [3, 1], [7, 2]]], [[[5, 5]]], [[[1, 1], [1, 1]]], [[[0, 0], [100000, 100000]]],
           [[[0, 0], [10, 0], [20, 0], [30, 0]]], [[[0, 0], [0, 10], [10, 0], [10, 10]]],
           [[[0, 5], [5, 0], [10, 5], [5, 10], [5, 5]]],
           [[[1, 100], [2, 1], [3, 99], [4, 2], [5, 98]]],
           [[[0, 0], [1, 100000], [100000, 1], [100000, 100000], [50000, 50000]]]],
)
_r = rnd(7801)
p["tests"].append([[[_r.randint(0, 100000), _r.randint(0, 100000)] for _ in range(3000)]])
p["tests"].append([[[_r.randint(0, 100000), _r.randint(0, 300)] for _ in range(2500)]])
p["tests"].append([[[_r.randint(0, 60), _r.randint(0, 60)] for _ in range(2000)]])


def b_axis(points):
    n = len(points)
    total = 0
    # Prim over the complete graph (independent of the Kruskal + candidate reduction)
    dist = {i: min(abs(points[0][0] - points[i][0]), abs(points[0][1] - points[i][1])) for i in range(1, n)}
    while dist:
        u = min(dist, key=lambda i: dist[i])
        total += dist.pop(u)
        for i in dist:
            dist[i] = min(dist[i], min(abs(points[u][0] - points[i][0]), abs(points[u][1] - points[i][1])))
    return total


def g_axis(r):
    n = r.randint(1, 8)
    hi = r.choice([3, 8, 20])
    return [[[r.randint(0, hi), r.randint(0, hi)] for _ in range(n)]]


def v_axis(tests):
    for t in tests:
        pts = t["args"][0]
        assert 1 <= len(pts) <= 4000
        assert all(len(q) == 2 and 0 <= q[0] <= 100000 and 0 <= q[1] <= 100000 for q in pts)


CHECKS["connect-points-min-axis-cost"] = (b_axis, g_axis, "exact")
VALIDATE["connect-points-min-axis-cost"] = v_axis

# ---------------------------------------------------------------- HARD

p = add(
    id="second-best-spanning-tree", title="Second Cheapest Spanning Tree", diff="Hard", topic=T, tier="extra",
    fn="secondBestWeight", params=[("n", "int"), ("edges", "int[][]")], ret="int", cmp="exact",
    desc="<p>A connected, weighted, undirected graph has <code>n</code> nodes numbered <code>0</code> to <code>n - 1</code>; <code>edges[i] = [a, b, w]</code> is an edge between <code>a</code> and <code>b</code> of weight <code>w</code>. A <em>spanning tree</em> is a set of <code>n - 1</code> edges (identified by their positions in the list) that connects all nodes.</p><p>List the total weights of <strong>all</strong> spanning trees in non-decreasing order, one entry per tree, so equal weights may appear several times. Return the second entry of this list. If the graph has only one spanning tree, return <code>-1</code>.</p><pre>n = 4, edges = [[0,1,1],[1,2,2],[2,3,3],[0,3,4]]   -> 7\n(trees: 6 [edges 0,1,2], 7 [0,1,3], 8 [0,2,3], 9 [1,2,3])</pre><p>If two different trees both have the minimum weight, the answer equals the minimum weight.</p>",
    constraints=["1 &le; n &le; 500", "n - 1 &le; edges.length &le; 2,000", "edges[i] = [a, b, w] with 0 &le; a, b &lt; n and a &ne; b", "1 &le; w &le; 100,000", "The graph is connected; parallel edges are allowed"],
    hints=["Start with a minimum spanning tree T of weight W. How could a different spanning tree look if it is as close to T as possible?",
           "A second-best tree can always be obtained from T by a single swap: add one non-tree edge e = (a, b) and remove the heaviest tree edge on the path from a to b.",
           "So the answer is the minimum of W + w(e) - maxOnPath(a, b) over all non-tree edges e. To get maxOnPath for all pairs quickly, record the weight whenever Kruskal merges two components: every pair (x in A, y in B) gets that weight as its maximum on the tree path."],
    editorial=["Build an MST T with Kruskal's algorithm and let W be its weight. Every other spanning tree differs from T, and a classical exchange argument shows that the cheapest tree different from T can be reached by a single swap: insert a non-tree edge e = (a, b), which closes a cycle through the tree path from a to b, and delete the heaviest edge on that path. The resulting weight is W + w(e) - maxOnPath(a, b).",
               "If several MSTs exist, some swap has difference 0 and the formula returns W, matching the definition. If there are no non-tree edges, T is the only spanning tree and the answer is -1. To get maxOnPath(a, b), note that when Kruskal merges components A and B with an edge of weight c, the tree path between any x in A and y in B has the merge edge as its heaviest one (all other edges were added earlier and are not heavier). Filling a matrix this way costs O(n&sup2;) in total, since every pair is assigned exactly once. Overall: O(m log m + n&sup2;)."],
    time="O(m log m + n&sup2;)", space="O(n&sup2;)",
    solution='''def secondBestWeight(n, edges):
    order = sorted(range(len(edges)), key=lambda i: edges[i][2])
    parent = list(range(n))
    members = [[i] for i in range(n)]
    mx = [[0] * n for _ in range(n)]

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    total = 0
    in_tree = [False] * len(edges)
    for i in order:
        a, b, w = edges[i]
        ra, rb = find(a), find(b)
        if ra == rb:
            continue
        in_tree[i] = True
        total += w
        for x in members[ra]:
            row = mx[x]
            for y in members[rb]:
                row[y] = w
                mx[y][x] = w
        if len(members[ra]) < len(members[rb]):
            ra, rb = rb, ra
        members[ra].extend(members[rb])
        members[rb] = []
        parent[rb] = ra
    best = None
    for i, (a, b, w) in enumerate(edges):
        if not in_tree[i]:
            cand = total + w - mx[a][b]
            if best is None or cand < best:
                best = cand
    return -1 if best is None else best
''',
    tests=[[4, [[0, 1, 1], [1, 2, 2], [2, 3, 3], [0, 3, 4]]], [1, []], [2, [[0, 1, 5]]], [2, [[0, 1, 5], [0, 1, 5]]],
           [2, [[0, 1, 5], [1, 0, 9]]],
           [3, [[0, 1, 1], [1, 2, 1], [0, 2, 1]]],
           [3, [[0, 1, 1], [1, 2, 2], [0, 2, 10]]],
           [4, [[0, 1, 1], [1, 2, 1], [2, 3, 1], [0, 3, 1], [0, 2, 1], [1, 3, 1]]],
           [5, [[0, 1, 1], [1, 2, 2], [2, 3, 3], [3, 4, 4], [0, 4, 100], [1, 3, 5]]],
           [4, [[0, 1, 3], [1, 2, 3], [2, 3, 3]]],
           [6, [[0, 1, 2], [1, 2, 2], [2, 0, 3], [3, 4, 5], [4, 5, 5], [5, 3, 6], [2, 3, 1]]]],
)
p["tests"].append([500, _big(7901, 500, 2000, 1, 100000)])
p["tests"].append([500, _big(7902, 500, 2000, 1, 6, simple=False)])
p["tests"].append([500, _big(7903, 500, 499, 1, 100000)])
p["tests"].append([450, _big(7904, 450, 520, 1, 100000)])


def b_second(n, edges):
    ws = []
    for combo in combinations(range(len(edges)), n - 1):
        sub = [edges[i] for i in combo]
        if _components(n, sub) == 1:
            ws.append(sum(e[2] for e in sub))
    ws.sort()
    return ws[1] if len(ws) > 1 else -1


def g_second(r):
    n = r.randint(1, 6)
    return [n, _graph(r, n, r.randint(n - 1, min(9, n * (n - 1) // 2) + 1), 1, r.choice([1, 3, 6, 20]), simple=r.random() < 0.6)]


def v_second(tests):
    for t in tests:
        n, edges = t["args"]
        _check_edges(n, edges, 500, 2000, 1, 100000, connected=True)
        assert len(edges) >= n - 1
    outs = [t["expected"] for t in tests]
    assert -1 in outs and any(o > 0 for o in outs)


CHECKS["second-best-spanning-tree"] = (b_second, g_second, "exact")
VALIDATE["second-best-spanning-tree"] = v_second

p = add(
    id="mst-weight-without-each-edge", title="Rebuilding the Network Without Each Edge", diff="Hard", topic=T, tier="extra",
    fn="mstWithoutEdge", params=[("n", "int"), ("edges", "int[][]")], ret="int[]", cmp="exact",
    desc="<p>A connected, weighted, undirected graph has <code>n</code> nodes numbered <code>0</code> to <code>n - 1</code> and edges <code>edges[i] = [a, b, w]</code>.</p><p>For every index <code>i</code>, imagine that edge <code>i</code> is deleted from the graph (all other edges stay). Let <code>res[i]</code> be the total weight of a minimum spanning tree of the remaining graph, or <code>-1</code> if the remaining graph is not connected. Return the array <code>res</code>.</p><pre>n = 3, edges = [[0,1,1],[1,2,2],[0,2,3]]   -> [5, 4, 3]</pre><p>Without edge 0 the tree is 1-2 and 0-2 (weight 5); without edge 1 it is 0-1 and 0-2 (weight 4); without edge 2 it is 0-1 and 1-2 (weight 3).</p>",
    constraints=["1 &le; n &le; 1,000", "n - 1 &le; edges.length &le; 3,000", "edges[i] = [a, b, w] with 0 &le; a, b &lt; n and a &ne; b", "1 &le; w &le; 100,000", "The graph is connected; parallel edges are allowed"],
    hints=["Recomputing the MST after deleting each edge costs O(m) times O(m log m), which is too slow. Which deletions do not change anything?",
           "Fix one MST T of weight W. If edge i is not in T, then T is still available after the deletion, so res[i] = W. Only the n - 1 tree edges need work.",
           "If tree edge i is deleted, T splits into two parts and the best repair is the cheapest non-tree edge that crosses between them, giving W - w(i) + that edge. For all tree edges at once: sort non-tree edges by weight; for each one, walk its tree path and give every not-yet-covered tree edge on it that weight. A union-find that jumps over covered edges makes this near-linear."],
    editorial=["Compute an MST T (weight W) with Kruskal. Deleting a non-tree edge leaves T intact, and T is still a minimum spanning tree of the smaller graph, so the answer is W. Deleting a tree edge e splits T into two sides. The new MST can be obtained from T - e by adding the cheapest remaining edge that connects the two sides (the cut property), so the answer is W - w(e) + c(e) where c(e) is the cheapest non-tree edge whose tree path contains e, and -1 if there is none (e is a bridge).",
               "Compute c(e) for all tree edges at once: root T, record parent, depth and the parent-edge index. Process the non-tree edges in increasing weight. For a non-tree edge (a, b), climb from the deeper endpoint using a union-find that links each already-covered node to its parent: every tree edge met on the way is covered for the first time, so this non-tree edge is its cheapest cover; assign it and link the node upward. Every tree edge is assigned once, so the total is O(m log m) for sorting plus almost linear for the covering."],
    time="O(m log m)", space="O(n + m)",
    solution='''def mstWithoutEdge(n, edges):
    m = len(edges)
    order = sorted(range(m), key=lambda i: edges[i][2])
    parent = list(range(n))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    in_tree = [False] * m
    adj = [[] for _ in range(n)]
    total = 0
    for i in order:
        a, b, w = edges[i]
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb
            in_tree[i] = True
            total += w
            adj[a].append((b, i))
            adj[b].append((a, i))
    par = [-1] * n
    pe = [-1] * n
    depth = [0] * n
    seen = [False] * n
    seen[0] = True
    stack = [0]
    while stack:
        u = stack.pop()
        for v, i in adj[u]:
            if not seen[v]:
                seen[v] = True
                par[v] = u
                pe[v] = i
                depth[v] = depth[u] + 1
                stack.append(v)
    up = list(range(n))

    def top(x):
        while up[x] != x:
            up[x] = up[up[x]]
            x = up[x]
        return x

    cover = [None] * m
    for i in order:
        if in_tree[i]:
            continue
        a, b, w = edges[i]
        a, b = top(a), top(b)
        while a != b:
            if depth[a] < depth[b]:
                a, b = b, a
            cover[pe[a]] = w
            up[a] = par[a]
            a = top(a)
    res = []
    for i in range(m):
        if not in_tree[i]:
            res.append(total)
        elif cover[i] is None:
            res.append(-1)
        else:
            res.append(total - edges[i][2] + cover[i])
    return res
''',
    tests=[[3, [[0, 1, 1], [1, 2, 2], [0, 2, 3]]], [1, []], [2, [[0, 1, 4]]], [2, [[0, 1, 4], [1, 0, 6]]],
           [4, [[0, 1, 1], [1, 2, 1], [2, 3, 1]]],
           [4, [[0, 1, 1], [1, 2, 1], [2, 3, 1], [3, 0, 1]]],
           [5, [[0, 1, 2], [1, 2, 3], [2, 3, 4], [3, 4, 5], [0, 4, 10], [1, 3, 7]]],
           [6, [[0, 1, 1], [1, 2, 1], [2, 0, 5], [2, 3, 9], [3, 4, 1], [4, 5, 1], [5, 3, 2]]],
           [5, [[0, 1, 3], [0, 2, 3], [0, 3, 3], [0, 4, 3], [1, 2, 3], [3, 4, 3]]]],
)
p["tests"].append([1000, _big(8001, 1000, 3000, 1, 100000)])
p["tests"].append([1000, _big(8002, 1000, 1200, 1, 100000)])
p["tests"].append([800, _big(8003, 800, 3000, 1, 4, simple=False)])


def b_without(n, edges):
    res = []
    for i in range(len(edges)):
        rest = sorted((e for j, e in enumerate(edges) if j != i), key=lambda e: e[2])
        parent = list(range(n))

        def find(x):
            while parent[x] != x:
                x = parent[x]
            return x

        tot = 0
        used = 0
        for a, b, w in rest:
            ra, rb = find(a), find(b)
            if ra != rb:
                parent[ra] = rb
                tot += w
                used += 1
        res.append(tot if used == n - 1 else -1)
    return res


def g_without(r):
    n = r.randint(1, 6)
    return [n, _graph(r, n, r.randint(n - 1, 9), 1, r.choice([2, 4, 9]), simple=r.random() < 0.6)]


def v_without(tests):
    for t in tests:
        n, edges = t["args"]
        _check_edges(n, edges, 1000, 3000, 1, 100000, connected=True)
        assert len(edges) >= n - 1 and len(t["expected"]) == len(edges)
    assert any(-1 in t["expected"] for t in tests)


CHECKS["mst-weight-without-each-edge"] = (b_without, g_without, "exact")
VALIDATE["mst-weight-without-each-edge"] = v_without

p = add(
    id="count-minimum-spanning-trees", title="Count the Cheapest Networks", diff="Hard", topic=T, tier="extra",
    fn="countMsts", params=[("n", "int"), ("edges", "int[][]")], ret="int", cmp="exact",
    desc="<p>A connected, weighted, undirected graph has <code>n</code> nodes numbered <code>0</code> to <code>n - 1</code>; <code>edges[i] = [a, b, w]</code> is an edge between <code>a</code> and <code>b</code> of weight <code>w</code>. Edges are distinguished by their position in the list, so parallel edges are different edges.</p><p>Count how many different minimum spanning trees the graph has, i.e. how many sets of <code>n - 1</code> edges connect all nodes with the smallest possible total weight. Return the count modulo <code>1,000,000,007</code>.</p><pre>n = 3, edges = [[0,1,1],[1,2,1],[0,2,1]]   -> 3   (any two of the three edges)\nn = 3, edges = [[0,1,1],[1,2,2],[0,2,2]]   -> 2</pre>",
    constraints=["1 &le; n &le; 60", "n - 1 &le; edges.length &le; 300", "edges[i] = [a, b, w] with 0 &le; a, b &lt; n and a &ne; b", "1 &le; w &le; 1,000", "The graph is connected; parallel edges are allowed"],
    hints=["All MSTs use the same number of edges of each weight, and the components formed after each weight class are the same in every MST. So the choices for different weights are independent and their counts multiply.",
           "Process weights in increasing order. For one weight, contract the current components into single nodes; the edges of this weight that join different components form a small multigraph. You must count the ways to choose edges that connect each of its parts without cycles.",
           "Counting spanning trees of a multigraph is done by Kirchhoff's matrix tree theorem: build the Laplacian (degree on the diagonal, minus the number of parallel edges off the diagonal), delete one row and column, and take the determinant modulo 1,000,000,007 with Gaussian elimination. Do this for each connected part of the contracted graph and multiply."],
    editorial=["Group the edges by weight and handle the groups in increasing order, keeping a union-find of the components built so far. For a group, only the edges whose endpoints lie in different components matter. Treat each current component as one node: the chosen edges of this weight must form a spanning forest of that contracted multigraph, one tree for each of its connected parts, and any such forest keeps the total weight minimal. Different groups are independent, so the final count is the product over groups and over connected parts of the number of spanning trees.",
               "The number of spanning trees of a connected multigraph on k nodes equals any cofactor of its Laplacian matrix (Kirchhoff). Delete the last row and column and compute the determinant of the (k - 1) x (k - 1) matrix modulo the prime 1,000,000,007 using Gaussian elimination and modular inverses (a 1 x 1 or empty matrix gives 1 or the single entry). After counting a group, union all its edges in the union-find. With n &le; 60, the elimination costs at most about 60&sup3; operations."],
    time="O(n&sup3; + m log m)", space="O(n&sup2;)",
    solution='''def countMsts(n, edges):
    MOD = 10 ** 9 + 7
    parent = list(range(n))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def det(mat):
        k = len(mat)
        res = 1
        for c in range(k):
            piv = -1
            for r in range(c, k):
                if mat[r][c] % MOD:
                    piv = r
                    break
            if piv < 0:
                return 0
            if piv != c:
                mat[piv], mat[c] = mat[c], mat[piv]
                res = -res
            res = res * mat[c][c] % MOD
            inv = pow(mat[c][c], MOD - 2, MOD)
            for r in range(c + 1, k):
                f = mat[r][c] * inv % MOD
                if f:
                    for j in range(c, k):
                        mat[r][j] = (mat[r][j] - f * mat[c][j]) % MOD
        return res % MOD

    es = sorted(edges, key=lambda e: e[2])
    ans = 1
    i = 0
    m = len(es)
    while i < m:
        j = i
        while j < m and es[j][2] == es[i][2]:
            j += 1
        group = []
        for k in range(i, j):
            ra, rb = find(es[k][0]), find(es[k][1])
            if ra != rb:
                group.append((ra, rb))
        # connected parts of the contracted multigraph
        local = {}
        for ra, rb in group:
            local.setdefault(ra, ra)
            local.setdefault(rb, rb)

        def lfind(x):
            while local[x] != x:
                local[x] = local[local[x]]
                x = local[x]
            return x

        for ra, rb in group:
            local[lfind(ra)] = lfind(rb)
        parts = {}
        for node in local:
            parts.setdefault(lfind(node), []).append(node)
        for nodes in parts.values():
            idx = {v: t for t, v in enumerate(nodes)}
            s = len(nodes)
            lap = [[0] * s for _ in range(s)]
            for ra, rb in group:
                if ra in idx and rb in idx:
                    x, y = idx[ra], idx[rb]
                    lap[x][x] += 1
                    lap[y][y] += 1
                    lap[x][y] -= 1
                    lap[y][x] -= 1
            minor = [[v % MOD for v in row[:-1]] for row in lap[:-1]]
            ans = ans * det(minor) % MOD
        for ra, rb in group:
            a, b = find(ra), find(rb)
            if a != b:
                parent[a] = b
        i = j
    return ans % MOD
''',
    tests=[[3, [[0, 1, 1], [1, 2, 1], [0, 2, 1]]], [3, [[0, 1, 1], [1, 2, 2], [0, 2, 2]]], [1, []],
           [2, [[0, 1, 4]]], [2, [[0, 1, 4], [1, 0, 4], [0, 1, 4]]], [2, [[0, 1, 4], [1, 0, 5]]],
           [4, [[a, b, 1] for a in range(4) for b in range(a + 1, 4)]],
           [6, [[a, b, 1] for a in range(6) for b in range(a + 1, 6)]],
           [5, [[0, 1, 1], [1, 2, 1], [2, 3, 1], [3, 4, 1], [4, 0, 1]]],
           [6, [[0, 1, 1], [1, 2, 1], [2, 0, 1], [3, 4, 1], [4, 5, 1], [5, 3, 1], [0, 3, 2], [1, 4, 2], [2, 5, 2]]],
           [5, [[0, 1, 1], [1, 2, 2], [2, 3, 3], [3, 4, 4], [0, 4, 9]]]],
)
p["tests"].append([60, _big(8101, 60, 300, 1, 3)])
p["tests"].append([60, _big(8102, 60, 300, 1, 1)])
p["tests"].append([40, _big(8103, 40, 300, 1, 2)])
p["tests"].append([60, _big(8104, 60, 150, 1, 1000)])


def b_count(n, edges):
    if n == 1:
        return 1
    best = None
    cnt = 0
    for combo in combinations(range(len(edges)), n - 1):
        sub = [edges[i] for i in combo]
        if _components(n, sub) == 1:
            s = sum(e[2] for e in sub)
            if best is None or s < best:
                best, cnt = s, 1
            elif s == best:
                cnt += 1
    return cnt % MOD


def g_count(r):
    n = r.randint(1, 6)
    return [n, _graph(r, n, r.randint(n - 1, 9), 1, r.choice([1, 2, 3]), simple=r.random() < 0.6)]


def v_count(tests):
    for t in tests:
        n, edges = t["args"]
        _check_edges(n, edges, 60, 300, 1, 1000, connected=True)
        assert len(edges) >= n - 1
    assert any(t["expected"] > 1 for t in tests) and any(t["expected"] == 1 for t in tests)


CHECKS["count-minimum-spanning-trees"] = (b_count, g_count, "exact")
VALIDATE["count-minimum-spanning-trees"] = v_count
