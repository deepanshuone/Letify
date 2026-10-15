"""Problems: graphs - bipartite checks, odd cycles, cycle detection and colouring. See data/lib.py for the registry."""
from collections import deque

from lib import add, rnd, CHECKS, VALIDATE, gen_arr  # noqa: F401
from lib import P as _P  # noqa: E402

T = "Graphs"


# ------------------------------------------------------------------ shared helpers (tests only)
def _pairs(r, n, m):
    """m distinct unordered pairs a != b, returned as [a, b] lists in random orientation."""
    m = min(m, n * (n - 1) // 2)
    seen, out = set(), []
    while len(out) < m:
        a, b = r.randrange(n), r.randrange(n)
        if a == b:
            continue
        k = (min(a, b), max(a, b))
        if k in seen:
            continue
        seen.add(k)
        out.append([a, b] if r.random() < 0.5 else [b, a])
    return out


def _bip_pairs(r, n, m, side=None):
    """m distinct pairs that go between the two sides of a random side assignment (so the graph is bipartite)."""
    if side is None:
        side = [r.randrange(2) for _ in range(n)]
    left = [v for v in range(n) if side[v] == 0]
    right = [v for v in range(n) if side[v] == 1]
    m = min(m, len(left) * len(right))
    seen, out = set(), []
    while len(out) < m:
        a, b = r.choice(left), r.choice(right)
        if (a, b) in seen:
            continue
        seen.add((a, b))
        out.append([a, b] if r.random() < 0.5 else [b, a])
    return out, side


def _dpairs(r, n, m, loops=True):
    """m distinct ordered pairs [a, b] (directed edges); self-loops allowed when loops is true."""
    cap = n * n if loops else n * (n - 1)
    m = min(m, cap)
    seen, out = set(), []
    while len(out) < m:
        a, b = r.randrange(n), r.randrange(n)
        if a == b and not loops:
            continue
        if (a, b) in seen:
            continue
        seen.add((a, b))
        out.append([a, b])
    return out


def _check_distinct_undirected(n, edges):
    seen = set()
    for a, b in edges:
        assert 0 <= a < n and 0 <= b < n and a != b, ("bad edge", a, b)
        k = (min(a, b), max(a, b))
        assert k not in seen, ("duplicate edge", k)
        seen.add(k)


def _check_distinct_directed(n, edges):
    seen = set()
    for a, b in edges:
        assert 0 <= a < n and 0 <= b < n, ("bad edge", a, b)
        assert (a, b) not in seen, ("duplicate edge", a, b)
        seen.add((a, b))


def _two_colourable(n, edges):
    """Independent bipartite test used by validators and brute force: try every colouring (small n only)."""
    for mask in range(1 << n):
        if all(((mask >> a) & 1) != ((mask >> b) & 1) for a, b in edges):
            return True
    return False


def _is_bip(n, edges):
    """Bipartite test for any size, by depth parity in a spanning search (used only by validators)."""
    adj = [[] for _ in range(n)]
    for a, b in edges:
        adj[a].append(b)
        adj[b].append(a)
    col = [-1] * n
    for s in range(n):
        if col[s] != -1:
            continue
        col[s] = 0
        stack = [s]
        while stack:
            u = stack.pop()
            for v in adj[u]:
                if col[v] == -1:
                    col[v] = col[u] ^ 1
                    stack.append(v)
                elif col[v] == col[u]:
                    return False
    return True


def _cycle_lengths(n, edges):
    """Lengths of all simple cycles of a small undirected simple graph, by exhaustive search."""
    adj = [set() for _ in range(n)]
    for a, b in edges:
        adj[a].add(b)
        adj[b].add(a)
    out = []

    def go(start, u, seen, d):
        for v in adj[u]:
            if v == start and d >= 2:
                out.append(d + 1)
            elif v > start and v not in seen:
                seen.add(v)
                go(start, v, seen, d + 1)
                seen.discard(v)

    for s in range(n):
        go(s, s, {s}, 0)
    return out


def _acyclic_dfs(n, edges):
    adj = [[] for _ in range(n)]
    for a, b in edges:
        adj[a].append(b)
    state = [0] * n

    def dfs(u):
        state[u] = 1
        for v in adj[u]:
            if state[v] == 1:
                return False
            if state[v] == 0 and not dfs(v):
                return False
        state[u] = 2
        return True

    return all(state[v] != 0 or dfs(v) for v in range(n))


def _far_even(r, n, edges):
    """A pair of nodes joined by a path of even length, as far apart as possible (BFS from a random start)."""
    adj = [[] for _ in range(n)]
    for a, b in edges:
        adj[a].append(b)
        adj[b].append(a)
    best = None
    for s in r.sample(range(n), min(n, 150)):
        dist = {s: 0}
        q = deque([s])
        while q:
            u = q.popleft()
            for v in adj[u]:
                if v not in dist:
                    dist[v] = dist[u] + 1
                    q.append(v)
        for v, d in dist.items():
            if d >= 2 and d % 2 == 0 and (best is None or d > best[0]):
                best = (d, s, v)
    return best


def _mixed_components(r, n, p_bip, sizes=(1, 1, 2, 3, 4, 5, 8, 13, 25), extra=0.4):
    """Random graph made of many separate pieces; each piece is a bipartite graph with probability p_bip,
    otherwise it contains an odd cycle. Edges are distinct and shuffled."""
    nodes = list(range(n))
    r.shuffle(nodes)
    edges, seen, i = [], set(), 0
    while i < n:
        size = min(n - i, r.choice(sizes))
        grp = nodes[i:i + size]
        i += size
        if size == 1:
            continue
        col = {grp[0]: 0}
        for idx in range(1, size):
            par = grp[r.randrange(idx)]
            v = grp[idx]
            col[v] = 1 - col[par]
            edges.append([par, v])
            seen.add((min(par, v), max(par, v)))
        bip = r.random() < p_bip
        todo, tries = int(size * extra), 0
        while todo > 0 and tries < 60:
            tries += 1
            a, b = r.sample(grp, 2)
            k = (min(a, b), max(a, b))
            if k in seen or (bip and col[a] == col[b]):
                continue
            seen.add(k)
            edges.append([a, b])
            todo -= 1
        if not bip:
            same = [(a, b) for a in grp for b in grp if a < b and col[a] == col[b] and (a, b) not in seen]
            if same:
                a, b = r.choice(same)
                seen.add((a, b))
                edges.append([a, b])
    r.shuffle(edges)
    return edges


def _paths_and_rings(r, n, ring_parity=None, ring_p=0.4, max_len=40):
    """Edges of a graph in which every node has at most two neighbours: disjoint paths and rings.
    ring_parity (0 even, 1 odd) forces the length parity of every ring."""
    nodes = list(range(n))
    r.shuffle(nodes)
    edges, i = [], 0
    while i < n:
        size = min(n - i, r.randint(1, max_len))
        grp = nodes[i:i + size]
        i += size
        if size >= 3 and r.random() < ring_p:
            if ring_parity is not None and size % 2 != ring_parity:
                if size > 3:
                    i -= 1
                    size -= 1
                    grp = grp[:size]
                else:
                    edges += [[grp[j], grp[j + 1]] for j in range(size - 1)]
                    continue
            edges += [[grp[j], grp[(j + 1) % size]] for j in range(size)]
        else:
            edges += [[grp[j], grp[j + 1]] for j in range(size - 1)]
    r.shuffle(edges)
    return [[a, b] if r.random() < 0.5 else [b, a] for a, b in edges]


# =================================================================== EASY
# ---------------------------------------------------------------- count bipartite components
add(
    id="count-bipartite-components", title="Count Bipartite Components", diff="Easy", topic=T,
    fn="countBipartiteComponents", params=[("n", "int"), ("edges", "int[][]")], ret="int", cmp="exact",
    desc="<p>An undirected graph has <code>n</code> nodes labelled <code>0</code> to <code>n - 1</code> and the connections listed in <code>edges</code>, where <code>edges[i] = [a, b]</code> joins <code>a</code> and <code>b</code>. The graph may fall apart into several connected components; a node without any edge is a component of its own.</p><p>A component is <em>bipartite</em> if its nodes can be painted with two colours so that every edge inside it joins two differently coloured nodes. Return how many components of the graph are bipartite.</p><pre>n = 7, edges = [[0,1],[1,2],[2,0],[3,4],[4,5]]  ->  2\n(the triangle 0-1-2 is not bipartite; the path 3-4-5 and the lone node 6 are)\n\nn = 4, edges = [[0,1],[1,2],[2,3],[3,0]]        ->  1</pre>",
    constraints=["1 &le; n &le; 3,000", "0 &le; edges.length &le; 4,000", "0 &le; a, b &lt; n and a &ne; b", "No two edges join the same pair of nodes"],
    hints=["Treat every connected component separately. A single node with no edges is always fine.",
           "Within one component, paint the first node with colour 0 and force each neighbour to get the opposite colour. When does this fail?",
           "Run a BFS or DFS from every unpainted node. If you see an edge between two nodes with the same colour, that component is not bipartite. Keep exploring the rest of that component anyway, so that you do not start a second search inside it, and count the components where no clash happened."],
    editorial=["A component is bipartite exactly when it contains no cycle of odd length, and two-colouring finds such a cycle if it exists. Once the colour of one node is fixed, every other node of the component has a forced colour, because each edge demands opposite colours at its ends. So a single traversal decides the whole component.",
               "Build the adjacency lists and keep a colour array initialised to -1. For each node that is still unpainted, start a BFS: paint it 0, and for every popped node look at all neighbours. An unpainted neighbour gets the opposite colour and joins the queue; a painted neighbour with the same colour as the current node marks the component as not bipartite. Do not stop at the first clash, finish the traversal so that every node of the component ends up painted, and add one to the answer only when no clash was seen.",
               "Every node and edge is handled a constant number of times, so the running time is O(n + m) with O(n + m) memory for the adjacency lists."],
    time="O(n + m)", space="O(n + m)",
    solution='''from collections import deque


def countBipartiteComponents(n, edges):
    adj = [[] for _ in range(n)]
    for a, b in edges:
        adj[a].append(b)
        adj[b].append(a)
    color = [-1] * n
    count = 0
    for s in range(n):
        if color[s] != -1:
            continue
        color[s] = 0
        ok = True
        queue = deque([s])
        while queue:
            u = queue.popleft()
            for v in adj[u]:
                if color[v] == -1:
                    color[v] = 1 - color[u]
                    queue.append(v)
                elif color[v] == color[u]:
                    ok = False
        if ok:
            count += 1
    return count
''',
    tests=[[7, [[0, 1], [1, 2], [2, 0], [3, 4], [4, 5]]],
           [4, [[0, 1], [1, 2], [2, 3], [3, 0]]],
           [1, []],
           [5, []],
           [3, [[0, 1], [1, 2], [2, 0]]],
           [6, [[0, 1], [2, 3], [3, 4], [4, 2], [5, 4]]],
           [8, [[0, 1], [1, 2], [2, 3], [3, 4], [4, 0], [5, 6], [6, 7], [7, 5]]],
           [2, [[1, 0]]],
           [9, [[0, 1], [0, 2], [0, 3], [4, 5], [5, 6], [6, 7], [7, 4], [4, 6]]]],
)
_p = _P[-1]
_r = rnd(9101)
_p["tests"].append([2500, _mixed_components(_r, 2500, 0.7)])
_p["tests"].append([2200, _mixed_components(_r, 2200, 0.0, sizes=(40, 100, 300))])
_p["tests"].append([2000, _mixed_components(_r, 2000, 1.0, sizes=(2, 3, 6, 50, 400))])
_p["tests"].append([1500, [[i, i + 1] for i in range(1499)]])


def b_cbc(n, edges):
    comp = list(range(n))
    changed = True
    while changed:
        changed = False
        for a, b in edges:
            m = min(comp[a], comp[b])
            if comp[a] != m or comp[b] != m:
                comp[a] = comp[b] = m
                changed = True
    total = 0
    for c in set(comp):
        nodes = [v for v in range(n) if comp[v] == c]
        idx = {v: i for i, v in enumerate(nodes)}
        sub = [[idx[a], idx[b]] for a, b in edges if comp[a] == c]
        if _two_colourable(len(nodes), sub):
            total += 1
    return total


def g_cbc(r):
    n = r.randint(1, 9)
    return [n, _pairs(r, n, r.randint(0, n + 2))]


def v_cbc(tests):
    for t in tests:
        n, edges = t["args"]
        assert 1 <= n <= 3000 and len(edges) <= 4000
        _check_distinct_undirected(n, edges)
    big = [t for t in tests if t["args"][0] >= 1500]
    assert len(big) >= 3 and sum(1 for t in big if t["expected"] >= 1) >= 3 and any(t["expected"] == 0 for t in tests)


CHECKS["count-bipartite-components"] = (b_cbc, g_cbc, "exact")
VALIDATE["count-bipartite-components"] = v_cbc

# ---------------------------------------------------------------- can a node return to itself
add(
    id="can-node-return-to-itself", title="Can a Node Return to Itself?", diff="Easy", topic=T,
    fn="canReturn", params=[("n", "int"), ("edges", "int[][]"), ("s", "int")], ret="bool", cmp="exact",
    desc="<p>A directed graph has <code>n</code> nodes labelled <code>0</code> to <code>n - 1</code>. Each entry <code>edges[i] = [a, b]</code> is a one-way edge from <code>a</code> to <code>b</code>. A self-loop <code>[a, a]</code> is allowed.</p><p>Starting at node <code>s</code>, you must follow <strong>at least one</strong> edge, always in its direction. Return <code>true</code> if you can arrive back at <code>s</code>, which means that <code>s</code> lies on a directed cycle. Return <code>false</code> otherwise.</p><pre>n = 4, edges = [[0,1],[1,2],[2,0],[2,3]], s = 1  ->  true   (1 -> 2 -> 0 -> 1)\nn = 4, edges = [[0,1],[1,2],[2,0],[2,3]], s = 3  ->  false  (node 3 has no outgoing edge)\nn = 2, edges = [[0,0]],                  s = 0  ->  true   (the self-loop)\nn = 2, edges = [[0,1]],                  s = 0  ->  false</pre>",
    constraints=["1 &le; n &le; 3,000", "0 &le; edges.length &le; 4,000", "0 &le; a, b, s &lt; n", "No directed edge appears twice; self-loops are allowed"],
    hints=["You are not asking whether a path from <code>s</code> to <code>t</code> exists for some other <code>t</code>; the target is <code>s</code> itself, and the walk has to use at least one edge.",
           "Start the search from the nodes that <code>s</code> points to, not from <code>s</code> with 'already visited'.",
           "Mark all out-neighbours of <code>s</code> as visited and push them. Run a DFS or BFS along directed edges. As soon as <code>s</code> itself is reached, answer <code>true</code>; if the search ends first, answer <code>false</code>."],
    editorial=["The node <code>s</code> is on a directed cycle exactly when there is a walk of one or more edges from <code>s</code> back to <code>s</code>. A search that begins at <code>s</code> and marks <code>s</code> visited immediately would never notice such a walk, so the trick is to seed the search with the out-neighbours of <code>s</code> only.",
               "Mark every out-neighbour of <code>s</code> as visited and put it on a stack. Pop a node; if it is <code>s</code>, a walk of at least one edge has come back and the answer is <code>true</code>. Otherwise visit its unvisited out-neighbours. A self-loop is handled automatically, because <code>s</code> is then among its own out-neighbours. If the stack empties, <code>s</code> cannot be reached again and the answer is <code>false</code>.",
               "Each node is pushed at most once and each edge is looked at once, so the time is O(n + m). Running a full cycle-detection for the whole graph would answer more than is asked; the question is about one node."],
    time="O(n + m)", space="O(n + m)",
    solution='''def canReturn(n, edges, s):
    adj = [[] for _ in range(n)]
    for a, b in edges:
        adj[a].append(b)
    seen = [False] * n
    stack = []
    for v in adj[s]:
        if not seen[v]:
            seen[v] = True
            stack.append(v)
    while stack:
        u = stack.pop()
        if u == s:
            return True
        for v in adj[u]:
            if not seen[v]:
                seen[v] = True
                stack.append(v)
    return False
''',
    tests=[[4, [[0, 1], [1, 2], [2, 0], [2, 3]], 1],
           [4, [[0, 1], [1, 2], [2, 0], [2, 3]], 3],
           [2, [[0, 0]], 0],
           [2, [[0, 1]], 0],
           [1, [], 0],
           [3, [[0, 1], [1, 1]], 0],
           [3, [[0, 1], [1, 1]], 1],
           [5, [[0, 1], [1, 2], [2, 3], [3, 4], [4, 2]], 0],
           [5, [[0, 1], [1, 2], [2, 3], [3, 4], [4, 2]], 3],
           [4, [[1, 0], [0, 1], [2, 3]], 2]],
)
_p = _P[-1]
_r = rnd(9102)
# a long one-way chain with the closing edge missing / present
_p["tests"].append([2000, [[i, i + 1] for i in range(1999)], 0])
_p["tests"].append([2000, [[i, i + 1] for i in range(1999)] + [[1999, 5]], 5])
_p["tests"].append([2000, [[i, i + 1] for i in range(1999)] + [[1999, 5]], 2])
_cyc = _r.sample(range(3000), 150)
_ed = {(a, b) for a, b in _dpairs(_r, 3000, 3000)} | {(_cyc[i], _cyc[(i + 1) % 150]) for i in range(150)}
_p["tests"].append([3000, [list(x) for x in sorted(_ed)], _cyc[7]])


def b_ret(n, edges, s):
    cur = {s}
    for _ in range(n):
        cur = {b for a, b in edges if a in cur}
        if s in cur:
            return True
    return False


def g_ret(r):
    n = r.randint(1, 7)
    return [n, _dpairs(r, n, r.randint(0, n + 3), loops=r.random() < 0.3), r.randrange(n)]


def v_ret(tests):
    for t in tests:
        n, edges, s = t["args"]
        assert 1 <= n <= 3000 and len(edges) <= 4000 and 0 <= s < n
        _check_distinct_directed(n, edges)
    exp = [t["expected"] for t in tests]
    assert True in exp and False in exp


CHECKS["can-node-return-to-itself"] = (b_ret, g_ret, "exact")
VALIDATE["can-node-return-to-itself"] = v_ret

# ---------------------------------------------------------------- colours for paths and rings
add(
    id="colours-for-paths-and-rings", title="Colours for Paths and Rings", diff="Easy", topic=T, tier="extra",
    fn="minColours", params=[("n", "int"), ("edges", "int[][]")], ret="int", cmp="exact",
    desc="<p>A network has <code>n</code> nodes labelled <code>0</code> to <code>n - 1</code> and undirected links <code>edges[i] = [a, b]</code>. Every node has <strong>at most two</strong> links, so each connected piece of the network is either a simple path or a ring (a cycle).</p><p>You want to give each node a colour so that two nodes joined by a link never share a colour. Return the smallest number of colours that is enough. A network without links needs one colour.</p><pre>n = 5, edges = [[0,1],[1,2],[2,3]]   ->  2   (a path of 4 nodes and a lone node)\nn = 3, edges = [[0,1],[1,2],[2,0]]   ->  3   (a ring of 3 nodes)\nn = 4, edges = [[0,1],[1,2],[2,3],[3,0]]  ->  2   (a ring of 4 nodes)\nn = 4, edges = []                    ->  1</pre>",
    constraints=["1 &le; n &le; 3,000", "0 &le; edges.length &le; 3,000", "0 &le; a, b &lt; n and a &ne; b; no pair of nodes is linked twice", "Every node appears in at most two links"],
    hints=["Only three answers are possible. When is one colour enough?",
           "Two colours work exactly when you can alternate them along every piece. A path can always alternate. What about a ring?",
           "A ring alternates perfectly only if its length is even. So the answer is 1 without links, 3 if some ring has an odd number of nodes, and 2 otherwise. A connected piece with at most two links per node is a ring exactly when it has as many links as nodes."],
    editorial=["With no links one colour is enough. With links you need at least two. Because every node has at most two neighbours, no node can see three mutually different colours around it that would force a fourth, and three colours always suffice: colour the nodes of each piece one after another along the path or ring, giving each node a colour different from its previous neighbour and, for the last node of a ring, different from both neighbours.",
               "So the question is only whether two colours are enough. A path can always be coloured alternately. A ring can be coloured alternately only when it has an even number of nodes; an odd ring forces two neighbours to match. So the answer is 3 exactly when some ring has odd length, and 2 otherwise (when there is at least one link).",
               "To find the rings, group nodes into connected pieces with union-find or a search and count nodes and links in each piece. Since the degree is at most two, a piece is a ring precisely when its link count equals its node count. Check whether that count is odd. The running time is O(n + m)."],
    time="O(n + m)", space="O(n)",
    solution='''def minColours(n, edges):
    if not edges:
        return 1
    parent = list(range(n))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for a, b in edges:
        parent[find(a)] = find(b)
    nodes = {}
    for v in range(n):
        root = find(v)
        nodes[root] = nodes.get(root, 0) + 1
    links = {}
    for a, b in edges:
        root = find(a)
        links[root] = links.get(root, 0) + 1
    for root, k in links.items():
        if k == nodes[root] and k % 2 == 1:
            return 3
    return 2
''',
    tests=[[5, [[0, 1], [1, 2], [2, 3]]],
           [3, [[0, 1], [1, 2], [2, 0]]],
           [4, [[0, 1], [1, 2], [2, 3], [3, 0]]],
           [4, []],
           [1, []],
           [2, [[0, 1]]],
           [7, [[0, 1], [1, 2], [2, 3], [3, 0], [4, 5], [5, 6], [6, 4]]],
           [8, [[0, 1], [1, 2], [2, 3], [3, 4], [4, 0], [5, 6], [6, 7]]],
           [10, [[0, 1], [1, 2], [2, 3], [3, 4], [4, 5], [5, 0], [6, 7], [7, 8], [8, 9], [9, 6]]]],
)
_p = _P[-1]
_r = rnd(9103)
_p["tests"].append([2400, _paths_and_rings(_r, 2400, ring_parity=0)])
_p["tests"].append([2400, _paths_and_rings(_r, 2400, ring_parity=None, ring_p=0.5, max_len=9)])
_p["tests"].append([1999, [[i, (i + 1) % 1999] for i in range(1999)]])
_p["tests"].append([1500, [[i, i + 1] for i in range(1499)]])


def b_col2(n, edges):
    adj = [[] for _ in range(n)]
    for a, b in edges:
        adj[a].append(b)
        adj[b].append(a)

    def ok(k):
        col = [-1] * n

        def go(v):
            if v == n:
                return True
            for c in range(k):
                if all(col[u] != c for u in adj[v] if u < v):
                    col[v] = c
                    if go(v + 1):
                        return True
            col[v] = -1
            return False

        return go(0)

    k = 1
    while not ok(k):
        k += 1
    return k


def g_col2(r):
    n = r.randint(1, 9)
    return [n, _paths_and_rings(r, n, ring_p=0.6, max_len=7)]


def v_col2(tests):
    for t in tests:
        n, edges = t["args"]
        assert 1 <= n <= 3000 and len(edges) <= 3000
        _check_distinct_undirected(n, edges)
        deg = [0] * n
        for a, b in edges:
            deg[a] += 1
            deg[b] += 1
        assert max(deg) <= 2
    assert {t["expected"] for t in tests} == {1, 2, 3}


CHECKS["colours-for-paths-and-rings"] = (b_col2, g_col2, "exact")
VALIDATE["colours-for-paths-and-rings"] = v_col2

# =================================================================== MEDIUM
# ---------------------------------------------------------------- first edge that breaks bipartiteness
add(
    id="first-edge-that-breaks-bipartiteness", title="First Edge That Breaks Two-Colouring", diff="Medium", topic=T,
    fn="firstBreakingEdge", params=[("n", "int"), ("edges", "int[][]")], ret="int", cmp="exact",
    desc="<p>A network of <code>n</code> nodes labelled <code>0</code> to <code>n - 1</code> starts without any links. The links <code>edges[0], edges[1], ...</code> are then added one at a time in this order, where <code>edges[i] = [a, b]</code> joins <code>a</code> and <code>b</code>. The same pair may be added more than once.</p><p>The network is <em>bipartite</em> while its nodes can be coloured with two colours so that every link joins different colours. Return the smallest index <code>i</code> such that the network made of <code>edges[0..i]</code> is no longer bipartite, or <code>-1</code> if it stays bipartite after all links were added.</p><pre>n = 5, edges = [[0,1],[1,2],[3,4],[2,3],[4,0],[0,2]]  ->  4\n(after index 4 the links 0-1-2-3-4-0 form a cycle of 5 nodes)\n\nn = 3, edges = [[0,1],[1,2]]                           ->  -1</pre>",
    constraints=["2 &le; n &le; 3,000", "0 &le; edges.length &le; 4,000", "0 &le; a, b &lt; n and a &ne; b", "The same pair of nodes may appear several times"],
    hints=["Checking every prefix from scratch with a fresh BFS is too slow when there are thousands of links. What information do you need to keep between steps?",
           "A new link [a, b] breaks bipartiteness exactly when a and b are already connected and are forced to have the <em>same</em> colour.",
           "Use union-find where every node also stores its colour parity relative to its parent. When joining two different groups, set the parity so that a and b end up different. When a and b are in the same group and have the same parity, this link is the answer."],
    editorial=["Adding a link between two nodes that lie in different pieces never creates a problem: you can flip all colours of one piece if needed. Only a link inside one piece can hurt. Inside a piece the colours are fully determined up to a global flip, so the link [a, b] is fine if the colours of a and b already differ, and creates an odd cycle if they are equal.",
               "Keep a union-find forest in which every node stores <code>par[x]</code>, the colour difference (0 or 1) between <code>x</code> and its parent. The function <code>find(x)</code> returns the root and the difference between <code>x</code> and the root, compressing the path while it adds up the differences by XOR. For a link [a, b], let (ra, pa) = find(a) and (rb, pb) = find(b). If ra equals rb and pa equals pb, return the index. If ra differs from rb, attach one root below the other with difference <code>pa ^ pb ^ 1</code>, so that a and b get different colours. Repeating a pair that was already added is harmless.",
               "Every link costs one or two find operations, which are almost constant with path compression and union by size. The total time is about O(m alpha(n)). Without union-find you could binary search on the prefix length and run a BFS check each time, for O(m (n + m) log m) which is much slower."],
    time="O(m alpha(n))", space="O(n)",
    solution='''def firstBreakingEdge(n, edges):
    parent = list(range(n))
    par = [0] * n      # colour difference between a node and its parent
    size = [1] * n

    def find(x):
        path = []
        while parent[x] != x:
            path.append(x)
            x = parent[x]
        root = x
        acc = 0
        for node in reversed(path):
            acc ^= par[node]
            par[node] = acc
            parent[node] = root
        return root

    for i, (a, b) in enumerate(edges):
        ra, rb = find(a), find(b)
        pa, pb = par[a], par[b]    # a and b are now attached to their roots (or are roots with difference 0)
        if ra == rb:
            if pa == pb:
                return i
        else:
            if size[ra] > size[rb]:
                ra, rb = rb, ra
            parent[ra] = rb
            par[ra] = pa ^ pb ^ 1
            size[rb] += size[ra]
    return -1
''',
    tests=[[5, [[0, 1], [1, 2], [3, 4], [2, 3], [4, 0], [0, 2]]],
           [3, [[0, 1], [1, 2]]],
           [3, [[0, 1], [1, 2], [2, 0]]],
           [2, []],
           [2, [[0, 1], [1, 0], [0, 1]]],
           [4, [[0, 1], [2, 3], [1, 2], [3, 0]]],
           [6, [[0, 1], [2, 3], [4, 5], [1, 2], [3, 4], [5, 0]]],
           [6, [[0, 1], [2, 3], [4, 5], [1, 2], [3, 4], [5, 0], [0, 3]]],
           [7, [[0, 1], [1, 2], [2, 3], [3, 4], [4, 5], [5, 6], [6, 0]]],
           [5, [[0, 1], [0, 2], [0, 3], [0, 4], [1, 2]]]],
)
_p = _P[-1]
_r = rnd(9104)


def _break_case(r, n, m, at):
    """m links consistent with a hidden two-colouring, except one same-colour link inserted at index `at`
    that joins two nodes already connected by an even path."""
    side = [r.randrange(2) for _ in range(n)]
    left = [v for v in range(n) if side[v] == 0]
    right = [v for v in range(n) if side[v] == 1]
    ed = []
    for _ in range(at):
        a, b = r.choice(left), r.choice(right)
        ed.append([a, b] if r.random() < 0.5 else [b, a])
    d, s, t = _far_even(r, n, ed)
    ed.append([s, t])
    while len(ed) < m:
        a, b = r.randrange(n), r.randrange(n)
        if a != b:
            ed.append([a, b])
    return ed, at


# sparse so that the connecting even path is long
_e, _at = _break_case(_r, 3000, 3000, 1500)
_p["tests"].append([3000, _e])
_e, _at = _break_case(_r, 1600, 2800, 2400)
_p["tests"].append([1600, _e])
_e = _bip_pairs(_r, 2500, 2400)[0]
_p["tests"].append([2500, _e])  # stays bipartite
_p["tests"].append([2000, [[i, (i + 1) % 2000] for i in range(2000)]])  # even ring, stays bipartite
_p["tests"].append([1999, [[i, (i + 1) % 1999] for i in range(1999)]])  # odd ring closes at the last link


def b_first(n, edges):
    for i in range(len(edges)):
        if not _two_colourable(n, edges[:i + 1]):
            return i
    return -1


def g_first(r):
    n = r.randint(2, 8)
    m = r.randint(0, 9)
    ed = []
    if r.random() < 0.5:
        side = [r.randrange(2) for _ in range(n)]
        for _ in range(m):
            a, b = r.randrange(n), r.randrange(n)
            if a != b and (side[a] != side[b] or r.random() < 0.15):
                ed.append([a, b])
    else:
        for _ in range(m):
            a, b = r.randrange(n), r.randrange(n)
            if a != b:
                ed.append([a, b])
    return [n, ed]


def v_first(tests):
    for t in tests:
        n, edges = t["args"]
        assert 2 <= n <= 3000 and len(edges) <= 4000
        for a, b in edges:
            assert 0 <= a < n and 0 <= b < n and a != b
    assert tests[-1]["expected"] == 1998 and tests[-2]["expected"] == -1
    assert tests[-5]["expected"] == 1500 and tests[-4]["expected"] == 2400


CHECKS["first-edge-that-breaks-bipartiteness"] = (b_first, g_first, "exact")
VALIDATE["first-edge-that-breaks-bipartiteness"] = v_first

# ---------------------------------------------------------------- knights and knaves
add(
    id="knights-and-knaves-max-knights", title="Knights and Knaves: Most Knights", diff="Medium", topic=T,
    fn="maxKnights", params=[("n", "int"), ("statements", "int[][]")], ret="int", cmp="exact",
    desc="<p>On an island live <code>n</code> people labelled <code>0</code> to <code>n - 1</code>. Each person is either a <em>knight</em>, who always tells the truth, or a <em>knave</em>, who always lies. Some people made statements about others. Each entry <code>statements[i] = [a, b, t]</code> means: person <code>a</code> said about person <code>b</code> that <strong>b is a knight</strong> (when <code>t = 1</code>) or that <strong>b is a knave</strong> (when <code>t = 0</code>).</p><p>Among all assignments of knight/knave to the people that agree with every statement, return the largest possible number of knights. If no assignment agrees with all statements, return <code>-1</code>. A person who made no statement and was not talked about can be a knight.</p><pre>n = 3, statements = [[0,1,1],[1,2,0],[2,0,0]]  ->  2\n(0 and 1 knights, 2 a knave: 0 truthfully calls 1 a knight, 1 truthfully calls 2 a knave,\n 2 falsely calls 0 a knave)\n\nn = 2, statements = [[0,1,1],[1,0,0]]          ->  -1</pre>",
    constraints=["1 &le; n &le; 3,000", "0 &le; statements.length &le; 3,500", "0 &le; a, b &lt; n and a &ne; b; t is 0 or 1", "Several statements may be about the same pair"],
    hints=["Write 'knight' as 1 and 'knave' as 0 and look at one statement. If a is a knight the statement is true, if a is a knave it is false. What does that say about the relation between the values of a and b?",
           "The statement [a, b, t] holds exactly when value(a) XOR value(b) equals 1 - t, no matter who a is. So every statement says 'same type' or 'different type'.",
           "Build a graph whose edges are 'same' / 'different' and two-colour each connected component by BFS. A conflict means the answer is -1. Otherwise a component has two possible assignments (the two colour classes swap roles), so pick the larger class as knights, and add up over all components."],
    editorial=["Let k(x) be 1 for a knight and 0 for a knave. If a is a knight, the statement is true, so k(b) = t. If a is a knave, the statement is false, so k(b) = 1 - t. Both cases are covered by the single equation <code>k(b) = k(a) XOR (1 - t)</code>. A statement therefore only says whether a and b are of the same type (t = 1) or of different types (t = 0).",
               "Treat each statement as an edge labelled with that parity, and process every connected component with BFS: fix the first node at 0, give each neighbour <code>value ^ label</code>, and if an already assigned neighbour disagrees return -1. Once a component is consistent, its assignment is determined up to swapping the two classes, and nothing connects different components, so each component can be flipped independently. The best choice makes the larger class knights.",
               "The answer is the sum, over components, of the size of the larger class; an isolated person forms a component of size 1 and contributes 1. The work is O(n + m). Trying all 2<sup>n</sup> assignments is hopeless for n = 3,000, which is why the parity relation is the heart of the problem."],
    time="O(n + m)", space="O(n + m)",
    solution='''from collections import deque


def maxKnights(n, statements):
    adj = [[] for _ in range(n)]
    for a, b, t in statements:
        w = 1 - t
        adj[a].append((b, w))
        adj[b].append((a, w))
    val = [-1] * n
    total = 0
    for s in range(n):
        if val[s] != -1:
            continue
        val[s] = 0
        count = [1, 0]
        queue = deque([s])
        while queue:
            u = queue.popleft()
            for v, w in adj[u]:
                want = val[u] ^ w
                if val[v] == -1:
                    val[v] = want
                    count[want] += 1
                    queue.append(v)
                elif val[v] != want:
                    return -1
        total += max(count)
    return total
''',
    tests=[[3, [[0, 1, 1], [1, 2, 0], [2, 0, 0]]],
           [2, [[0, 1, 1], [1, 0, 0]]],
           [1, []],
           [4, []],
           [2, [[0, 1, 0]]],
           [2, [[0, 1, 1]]],
           [3, [[0, 1, 0], [1, 2, 0], [0, 2, 0]]],
           [3, [[0, 1, 0], [1, 2, 0], [0, 2, 1]]],
           [5, [[0, 1, 0], [0, 2, 0], [0, 3, 0], [4, 0, 1]]],
           [6, [[0, 1, 1], [1, 0, 1], [2, 3, 0], [3, 2, 0], [4, 5, 0], [5, 4, 1]]]],
)
_p = _P[-1]
_r = rnd(9105)


def _knight_case(r, n, m, spoil=False, pk=0.5):
    truth = [1 if r.random() < pk else 0 for _ in range(n)]
    st = []
    for a, b in _pairs(r, n, m):
        t = truth[b] if truth[a] == 1 else 1 - truth[b]
        st.append([a, b, t])
    if spoil:
        i = r.randrange(len(st))
        st[i][2] ^= 1
        # a flipped statement can only be harmless if it is not on a cycle, so add a parallel opposite one
        st.append([st[i][1], st[i][0], 1 - st[i][2]])
    return st


_p["tests"].append([3000, _knight_case(_r, 3000, 3400)])
_p["tests"].append([3000, _knight_case(_r, 3000, 1200, pk=0.3)])
_p["tests"].append([1500, _knight_case(_r, 1500, 3400, spoil=True)])


def b_knk(n, statements):
    best = -1
    for mask in range(1 << n):
        if all(((mask >> b) & 1) == (t if (mask >> a) & 1 else 1 - t) for a, b, t in statements):
            best = max(best, bin(mask).count("1"))
    return best


def g_knk(r):
    n = r.randint(1, 8)
    if n == 1:
        return [1, []]
    if r.random() < 0.5:
        st = _knight_case(r, n, r.randint(0, n + 2), pk=r.random())
        if st and r.random() < 0.3:
            st[r.randrange(len(st))][2] ^= 1
        return [n, st]
    st = []
    for _ in range(r.randint(0, 8)):
        a, b = r.randrange(n), r.randrange(n)
        if a != b:
            st.append([a, b, r.randint(0, 1)])
    return [n, st]


def v_knk(tests):
    for t in tests:
        n, st = t["args"]
        assert 1 <= n <= 3000 and len(st) <= 3500
        for a, b, x in st:
            assert 0 <= a < n and 0 <= b < n and a != b and x in (0, 1)
    assert any(t["expected"] == -1 for t in tests)
    assert tests[-3]["expected"] > 1000 and tests[-2]["expected"] > 1500


CHECKS["knights-and-knaves-max-knights"] = (b_knk, g_knk, "exact")
VALIDATE["knights-and-knaves-max-knights"] = v_knk

# ---------------------------------------------------------------- nodes that finish within k moves
add(
    id="nodes-safe-within-k-moves", title="Nodes That Always Finish Within K Moves", diff="Medium", topic=T, tier="extra",
    fn="safeWithinKMoves", params=[("graph", "int[][]"), ("k", "int")], ret="int[]", cmp="exact",
    desc="<p>A directed graph has <code>n = graph.length</code> nodes labelled <code>0</code> to <code>n - 1</code>. The list <code>graph[i]</code> holds the nodes that node <code>i</code> points to. A node without outgoing edges is <em>terminal</em>.</p><p>A token is placed on a node and then moved along outgoing edges, one edge per move, choosing any edge it likes, until it stands on a terminal node, where it must stop. A node is <em>k-safe</em> if, <strong>whatever</strong> choices are made, the token is guaranteed to stop after <strong>at most</strong> <code>k</code> moves. A terminal node needs 0 moves, so it is k-safe for every <code>k &ge; 0</code>; a node from which the token can wander forever is never k-safe.</p><p>Return all k-safe nodes in increasing order.</p><pre>graph = [[1,2],[2],[3],[]], k = 2  ->  [1,2,3]\n(longest walks: from 0 it is 3 moves, from 1 it is 2, from 2 it is 1, node 3 is terminal)\n\ngraph = [[1],[0],[]], k = 5        ->  [2]</pre>",
    constraints=["1 &le; n &le; 3,000", "The total number of edges is at most 6,000", "graph[i] holds distinct values in [0, n - 1]; it may contain i itself", "0 &le; k &le; 3,000"],
    hints=["For every node you want the number of moves in the <em>worst</em> case. What is that for a terminal node, and how does it follow from the targets of a non-terminal node?",
           "The worst-case number of moves of a node is 1 plus the largest worst case among its targets. It is infinite if the node can reach a cycle.",
           "Reverse the edges and run Kahn's algorithm from the terminal nodes (out-degree counters). When you finish a node j, update each predecessor i with <code>depth[i] = max(depth[i], depth[j] + 1)</code>. Nodes that never get their counter to zero can loop forever. Report the finished nodes with depth at most k."],
    editorial=["Let depth(v) be the largest number of moves the token can make from v before stopping. For a terminal node it is 0, and otherwise it is <code>1 + max(depth(w))</code> over all targets w, provided every target has a finite depth. If some target can reach a cycle, the token can circle forever and the node is never safe. The answer is the set of nodes with a finite depth that is at most k.",
               "Compute depths with a reversed Kahn's algorithm. Keep <code>remaining[i]</code>, the number of targets of i whose depth is not final yet, starting at the out-degree. Push the terminal nodes. When a node j is popped its depth is final; for every predecessor i set <code>depth[i] = max(depth[i], depth[j] + 1)</code> and decrease <code>remaining[i]</code>; at zero, i's depth is final and it joins the stack. Nodes on a cycle, or with a path into a cycle, keep a positive counter forever and are never reported.",
               "Finally collect the nodes with counter zero and depth at most k, in increasing order. The cost is O(n + m) plus the final sort (which you can avoid by scanning the nodes in order). This is the 'safe states' idea from cycle detection with an extra bound on the longest path."],
    time="O(n + m)", space="O(n + m)",
    solution='''def safeWithinKMoves(graph, k):
    n = len(graph)
    rev = [[] for _ in range(n)]
    remaining = [len(graph[i]) for i in range(n)]
    for i in range(n):
        for j in graph[i]:
            rev[j].append(i)
    depth = [0] * n
    stack = [i for i in range(n) if remaining[i] == 0]
    while stack:
        j = stack.pop()
        for i in rev[j]:
            if depth[j] + 1 > depth[i]:
                depth[i] = depth[j] + 1
            remaining[i] -= 1
            if remaining[i] == 0:
                stack.append(i)
    return [i for i in range(n) if remaining[i] == 0 and depth[i] <= k]
''',
    tests=[[[[1, 2], [2], [3], []], 2],
           [[[1], [0], []], 5],
           [[[]], 0],
           [[[0]], 10],
           [[[1, 2], [2], [3], []], 3],
           [[[1, 2], [2], [3], []], 0],
           [[[1, 2, 3, 4], [1, 2], [3, 4], [0, 4], []], 1],
           [[[1, 2], [2, 3], [5], [0], [5], [], []], 1],
           [[[1, 2], [2, 3], [5], [0], [5], [], []], 4],
           [[[], [0], [1], [2], [3, 0]], 2],
           [[[1], [2], [3], [4], [5], [6], []], 3]],
)
_p = _P[-1]
_r = rnd(9106)


def _dag_with_cycles(r, n, span, back):
    g = [set() for _ in range(n)]
    for i in range(n - 1):
        for _ in range(r.randint(0, 1)):
            g[i].add(min(n - 1, i + r.randint(1, span)))
        if r.random() < 0.9:
            g[i].add(i + 1)
    for _ in range(back):
        a = r.randrange(5, n)
        b = r.randrange(0, a)
        g[a].add(b)
    return [sorted(s) for s in g]


_g = _dag_with_cycles(_r, 3000, 40, 0)
_p["tests"].append([_g, 1500])
_p["tests"].append([_g, 2999])
_g = _dag_with_cycles(_r, 3000, 12, 6)
_p["tests"].append([_g, 400])


def b_swk(graph, k):
    n = len(graph)
    out = []
    for v in range(n):
        cur = {v}
        for _ in range(k + 1):
            cur = {w for u in cur for w in graph[u]}
        if not cur:
            out.append(v)
    return out


def g_swk(r):
    n = r.randint(1, 8)
    g = []
    for i in range(n):
        if r.random() < 0.5:
            c = [j for j in range(i + 1, n) if r.random() < 0.35]
            if r.random() < 0.15:
                c.append(r.randrange(n))
        else:
            c = [j for j in range(n) if r.random() < 0.18]
        g.append(sorted(set(c)))
    return [g, r.randint(0, 5)]


def v_swk(tests):
    for t in tests:
        g, k = t["args"]
        n = len(g)
        assert 1 <= n <= 3000 and sum(len(x) for x in g) <= 6000 and 0 <= k <= 3000
        for x in g:
            assert len(set(x)) == len(x) and all(0 <= y < n for y in x)
        assert t["expected"] == sorted(t["expected"])
    assert any(0 < len(t["expected"]) < len(t["args"][0]) for t in tests[-3:])


CHECKS["nodes-safe-within-k-moves"] = (b_swk, g_swk, "exact")
VALIDATE["nodes-safe-within-k-moves"] = v_swk

# ---------------------------------------------------------------- shortest cycle in an undirected graph
add(
    id="shortest-cycle-undirected-graph", title="Shortest Cycle in an Undirected Graph", diff="Medium", topic=T,
    fn="shortestCycle", params=[("n", "int"), ("edges", "int[][]")], ret="int", cmp="exact",
    desc="<p>An undirected graph has <code>n</code> nodes labelled <code>0</code> to <code>n - 1</code> and the connections <code>edges[i] = [a, b]</code>. It can be disconnected. A <em>cycle</em> is a closed route that starts and ends at the same node, uses at least three connections and never visits a node twice (except for returning to the start).</p><p>Return the number of connections on the shortest cycle of the graph, or <code>-1</code> if the graph has no cycle.</p><pre>n = 6, edges = [[0,1],[1,2],[2,3],[3,4],[4,5],[5,0],[0,3]]  ->  4\n(the cycle 0-1-2-3-0 has 4 connections, the cycle 0-3-4-5-0 too, the big ring has 6)\n\nn = 4, edges = [[0,1],[1,2],[2,3]]                         ->  -1</pre>",
    constraints=["1 &le; n &le; 300", "0 &le; edges.length &le; 900", "0 &le; a, b &lt; n and a &ne; b", "No two edges join the same pair of nodes"],
    hints=["A shortest path search finds distances. Which search tells you the distance in an unweighted graph, and what would a cycle look like inside its result?",
           "Start a BFS from a node s. If you meet an already-seen node v from node u, and v is not the parent of u, then the two BFS branches plus the edge u-v enclose a closed walk containing a cycle.",
           "Run the BFS from every node and keep the minimum of <code>dist[u] + dist[v] + 1</code> over all non-tree edges (u, v) met. For a start node that lies on a shortest cycle the value is exactly the cycle length, and for any other start it is never smaller than the true answer."],
    editorial=["Consider a BFS from a node s. Every edge (u, v) that is not a tree edge links two nodes whose tree paths to s, together with the edge itself, form a closed walk of length <code>dist[u] + dist[v] + 1</code>. That closed walk contains a cycle (the tree paths separate at their lowest common ancestor and the part below it, plus the edge, is a cycle), so the value is at least the length of the shortest cycle of the graph.",
               "Equality is reached when s is a node of a shortest cycle C. The BFS distances to the nodes of C are their distances along C, since a shortcut would give a shorter cycle, so the edge of C opposite to s is a non-tree edge whose value is the length of C. Taking the minimum over all start nodes s therefore gives exactly the shortest cycle.",
               "Implementation: for each s run a BFS storing <code>dist</code> and <code>parent</code>; whenever a neighbour v of the popped node u is already seen and <code>v != parent[u]</code> update the best value with <code>dist[u] + dist[v] + 1</code>. Because the graph has no repeated edges, comparing with the parent is enough to skip the tree edge. Total time O(n (n + m)), which is fine for n &le; 300. Return -1 when no cycle was found."],
    time="O(n (n + m))", space="O(n + m)",
    solution='''from collections import deque


def shortestCycle(n, edges):
    adj = [[] for _ in range(n)]
    for a, b in edges:
        adj[a].append(b)
        adj[b].append(a)
    best = float("inf")
    for s in range(n):
        dist = [-1] * n
        parent = [-1] * n
        dist[s] = 0
        queue = deque([s])
        while queue:
            u = queue.popleft()
            if 2 * dist[u] >= best:
                break
            for v in adj[u]:
                if dist[v] == -1:
                    dist[v] = dist[u] + 1
                    parent[v] = u
                    queue.append(v)
                elif v != parent[u]:
                    best = min(best, dist[u] + dist[v] + 1)
    return -1 if best == float("inf") else best
''',
    tests=[[6, [[0, 1], [1, 2], [2, 3], [3, 4], [4, 5], [5, 0], [0, 3]]],
           [4, [[0, 1], [1, 2], [2, 3]]],
           [1, []],
           [3, [[0, 1], [1, 2], [2, 0]]],
           [7, [[0, 1], [1, 2], [2, 3], [3, 4], [4, 5], [5, 6], [6, 0]]],
           [8, [[0, 1], [1, 2], [2, 3], [3, 0], [4, 5], [5, 6], [6, 7], [7, 4], [0, 4]]],
           [6, [[0, 1], [0, 2], [0, 3], [3, 4], [3, 5]]],
           [10, [[0, 1], [1, 2], [2, 3], [3, 4], [4, 0], [5, 6], [6, 7], [7, 5], [8, 9]]],
           [5, [[0, 1], [0, 2], [0, 3], [0, 4], [1, 2], [2, 3], [3, 4], [4, 1]]]],
)
_p = _P[-1]
_r = rnd(9107)
_p["tests"].append([300, [[i, (i + 1) % 300] for i in range(300)]])
_p["tests"].append([300, _pairs(_r, 300, 900)])
_p["tests"].append([300, [[i, i + 1] for i in range(299)] + [[0, 299]] + [[10, 120]]])
# a sparse tree plus a few far-apart extra edges: all cycles are long
_tree = [[i, _r.randrange(max(0, i - 3), i)] for i in range(1, 300)]
_ext = set()
while len(_ext) < 3:
    a, b = _r.randrange(300), _r.randrange(300)
    if abs(a - b) > 40 and [a, b] not in _tree and [b, a] not in _tree:
        _ext.add((min(a, b), max(a, b)))
_p["tests"].append([300, _tree + [list(x) for x in _ext]])


def b_sc(n, edges):
    c = _cycle_lengths(n, edges)
    return min(c) if c else -1


def g_sc(r):
    n = r.randint(1, 8)
    return [n, _pairs(r, n, r.randint(0, n + 3))]


def v_sc(tests):
    for t in tests:
        n, edges = t["args"]
        assert 1 <= n <= 300 and len(edges) <= 900
        _check_distinct_undirected(n, edges)
    exp = [t["expected"] for t in tests]
    assert -1 in exp and max(exp) >= 100


CHECKS["shortest-cycle-undirected-graph"] = (b_sc, g_sc, "exact")
VALIDATE["shortest-cycle-undirected-graph"] = v_sc

# ---------------------------------------------------------------- most balanced two-team split
add(
    id="most-balanced-two-team-split", title="Most Balanced Two-Team Split", diff="Medium", topic=T, tier="extra",
    fn="minTeamGap", params=[("n", "int"), ("dislikes", "int[][]")], ret="int", cmp="exact",
    desc="<p>A class of <code>n</code> students labelled <code>0</code> to <code>n - 1</code> must be split into two teams. Every student joins exactly one team, and a team may be empty. The list <code>dislikes</code> contains pairs <code>[a, b]</code> meaning that students <code>a</code> and <code>b</code> cannot be on the same team.</p><p>Among all valid splits, find the smallest possible difference between the sizes of the two teams, that is the minimum of <code>|size(team 1) - size(team 2)|</code>. If no valid split exists, return <code>-1</code>.</p><pre>n = 5, dislikes = [[0,1],[1,2],[3,4]]  ->  1\n(for example the teams {0,2,3} and {1,4})\n\nn = 3, dislikes = [[0,1],[1,2],[2,0]]  ->  -1\nn = 4, dislikes = [[0,1],[0,2],[0,3]]  ->  2</pre>",
    constraints=["1 &le; n &le; 3,000", "0 &le; dislikes.length &le; 4,000", "0 &le; a, b &lt; n and a &ne; b", "No pair appears twice"],
    hints=["First decide whether any valid split exists at all. Which graph property is that?",
           "Inside a connected group of students who (indirectly) dislike each other, the split is forced up to swapping the teams. So each group contributes either (x to team 1, y to team 2) or (y to team 1, x to team 2).",
           "Compute x and y for every group by two-colouring. Then it is a subset-sum problem: which sizes of team 1 can you reach by choosing, for each group, x or y? A bitset (an integer whose bit s says 'team 1 can have size s') makes this fast: <code>S = (S &lt;&lt; x) | (S &lt;&lt; y)</code>."],
    editorial=["If the dislike graph has an odd cycle, no valid split exists and the answer is -1. Otherwise every connected component is bipartite, and its two-colouring is unique up to swapping the colours. So a component with colour classes of sizes x and y adds either x students to team 1 and y to team 2, or the other way round. Isolated students are components with sizes (1, 0).",
               "The question becomes: choose for each component whether x or y goes to team 1, so that team 1 gets s students in total and the gap <code>|n - 2s|</code> is as small as possible. Keep the set of reachable values of s as a bitset stored in a Python integer: start with <code>S = 1</code> (size 0) and for every component do <code>S = (S &lt;&lt; x) | (S &lt;&lt; y)</code>. At the end, scan s from 0 to n and take the best <code>|n - 2s|</code> over the set bits.",
               "Colouring costs O(n + m). The bitset has at most n + 1 bits, so each of at most n components costs O(n / 64) word operations. In total this is O(n + m + n<sup>2</sup>/64), tiny for n = 3,000."],
    time="O(n + m + n^2 / w)", space="O(n + m)",
    solution='''from collections import deque


def minTeamGap(n, dislikes):
    adj = [[] for _ in range(n)]
    for a, b in dislikes:
        adj[a].append(b)
        adj[b].append(a)
    color = [-1] * n
    reach = 1
    for s in range(n):
        if color[s] != -1:
            continue
        color[s] = 0
        count = [1, 0]
        queue = deque([s])
        while queue:
            u = queue.popleft()
            for v in adj[u]:
                if color[v] == -1:
                    color[v] = 1 - color[u]
                    count[color[v]] += 1
                    queue.append(v)
                elif color[v] == color[u]:
                    return -1
        reach = (reach << count[0]) | (reach << count[1])
    best = n
    for size in range(n + 1):
        if (reach >> size) & 1:
            best = min(best, abs(n - 2 * size))
    return best
''',
    tests=[[5, [[0, 1], [1, 2], [3, 4]]],
           [3, [[0, 1], [1, 2], [2, 0]]],
           [4, [[0, 1], [0, 2], [0, 3]]],
           [1, []],
           [2, []],
           [5, []],
           [6, [[0, 1], [2, 3], [4, 5]]],
           [7, [[0, 1], [0, 2], [0, 3], [4, 5], [5, 6]]],
           [8, [[0, 1], [0, 2], [0, 3], [0, 4], [0, 5], [0, 6], [0, 7]]],
           [6, [[0, 1], [1, 2], [2, 3], [3, 4], [4, 5], [5, 0]]]],
)
_p = _P[-1]
_r = rnd(9108)
_p["tests"].append([3000, _mixed_components(_r, 3000, 1.0)])
_p["tests"].append([2999, _mixed_components(_r, 2999, 1.0, sizes=(1, 3, 40, 300, 700), extra=0.5)])
_p["tests"].append([3000, _mixed_components(_r, 3000, 0.97, sizes=(1, 2, 3, 4, 5, 8))])
_p["tests"].append([1203, [[0, i] for i in range(1, 801)] + [[801, i] for i in range(802, 1102)] + [[1102, i] for i in range(1103, 1203)]])


def b_mtg(n, dislikes):
    best = -1
    for mask in range(1 << n):
        if all(((mask >> a) & 1) != ((mask >> b) & 1) for a, b in dislikes):
            gap = abs(n - 2 * bin(mask).count("1"))
            if best == -1 or gap < best:
                best = gap
    return best


def g_mtg(r):
    n = r.randint(1, 10)
    if r.random() < 0.6:
        return [n, _bip_pairs(r, n, r.randint(0, n))[0]]
    return [n, _pairs(r, n, r.randint(0, n + 1))]


def v_mtg(tests):
    for t in tests:
        n, d = t["args"]
        assert 1 <= n <= 3000 and len(d) <= 4000
        _check_distinct_undirected(n, d)
        assert (t["expected"] == -1) == (not _is_bip(n, d))
    assert -1 in [t["expected"] for t in tests]
    assert tests[-4]["expected"] >= 0 and tests[-3]["expected"] >= 0 and tests[-1]["expected"] == 401


CHECKS["most-balanced-two-team-split"] = (b_mtg, g_mtg, "exact")
VALIDATE["most-balanced-two-team-split"] = v_mtg

# ---------------------------------------------------------------- edges whose removal makes a DAG
add(
    id="edges-whose-removal-gives-dag", title="Edges That Fix All Cycles", diff="Medium", topic=T, tier="extra",
    fn="countFixingEdges", params=[("n", "int"), ("edges", "int[][]")], ret="int", cmp="exact",
    desc="<p>A directed graph has <code>n</code> nodes labelled <code>0</code> to <code>n - 1</code>. Each entry <code>edges[i] = [a, b]</code> is a one-way edge from <code>a</code> to <code>b</code>; self-loops <code>[a, a]</code> are allowed.</p><p>Count the edges with the following property: after deleting <strong>only that edge</strong>, the graph has no directed cycle at all. If the graph is already free of cycles, deleting any edge keeps it so, and then every edge counts.</p><pre>n = 4, edges = [[0,1],[1,2],[2,0],[2,3]]       ->  3  (any of the three edges of the cycle 0-1-2)\nn = 3, edges = [[0,1],[1,0],[1,2],[2,1]]       ->  0  (two separate cycles, one deletion cannot fix both)\nn = 3, edges = [[0,1],[1,2]]                   ->  2  (already acyclic)</pre>",
    constraints=["1 &le; n &le; 300", "0 &le; edges.length &le; 800", "0 &le; a, b &lt; n", "No directed edge appears twice; self-loops are allowed"],
    hints=["Suppose the graph has a directed cycle. If you delete an edge that is not on that cycle, is the cycle still there?",
           "So only the edges of one fixed cycle can possibly fix the graph. How many such candidates are there at most?",
           "Find any one cycle (peel nodes with Kahn's algorithm; every node that is left over has a leftover predecessor, so walking backwards finds a cycle). For each of its at most n edges, test whether the graph without that edge is acyclic with another Kahn pass. If the graph was acyclic from the start, answer with the number of edges."],
    editorial=["If the graph has no cycle, every deletion leaves it acyclic, so the answer is the number of edges. Otherwise take any directed cycle C. An edge outside C does not break C, so it cannot be a fixing edge. Therefore only the edges of C are candidates, and there are at most n of them.",
               "To find a cycle, run Kahn's algorithm (repeatedly remove nodes with in-degree 0). The nodes that cannot be removed all keep an incoming edge from another leftover node. Pick a leftover node and repeatedly step to one of its leftover predecessors; the first node that repeats closes a cycle, and the edges walked between the two visits are the cycle. Self-loops are cycles of length 1 and are found the same way.",
               "For each candidate edge, run Kahn's algorithm again while skipping that edge; if all n nodes can be removed, count it. This costs O(n (n + m)) in the worst case, which is fine for n &le; 300 and m &le; 800. For huge graphs there are smarter linear-time methods, but they are much harder to get right."],
    time="O(n (n + m))", space="O(n + m)",
    solution='''def countFixingEdges(n, edges):
    m = len(edges)
    out = [[] for _ in range(n)]
    for i, (a, b) in enumerate(edges):
        out[a].append((b, i))

    def kahn(skip):
        indeg = [0] * n
        for i, (a, b) in enumerate(edges):
            if i != skip:
                indeg[b] += 1
        stack = [v for v in range(n) if indeg[v] == 0]
        removed = [False] * n
        done = 0
        while stack:
            u = stack.pop()
            removed[u] = True
            done += 1
            for v, i in out[u]:
                if i != skip:
                    indeg[v] -= 1
                    if indeg[v] == 0:
                        stack.append(v)
        return done == n, removed

    acyclic, removed = kahn(-1)
    if acyclic:
        return m
    pred = {}
    for i, (a, b) in enumerate(edges):
        if not removed[a] and not removed[b] and b not in pred:
            pred[b] = (a, i)
    cur = next(v for v in range(n) if not removed[v])
    pos = {}
    walk = []
    while cur not in pos:
        pos[cur] = len(walk)
        a, i = pred[cur]
        walk.append(i)
        cur = a
    cycle_edges = walk[pos[cur]:]
    return sum(1 for i in cycle_edges if kahn(i)[0])
''',
    tests=[[4, [[0, 1], [1, 2], [2, 0], [2, 3]]],
           [3, [[0, 1], [1, 0], [1, 2], [2, 1]]],
           [3, [[0, 1], [1, 2]]],
           [1, []],
           [1, [[0, 0]]],
           [2, [[0, 0], [1, 1]]],
           [3, [[0, 1], [1, 2], [2, 0], [0, 2]]],
           [4, [[0, 1], [1, 2], [2, 3], [3, 0], [1, 3]]],
           [5, [[0, 1], [1, 2], [2, 0], [2, 3], [3, 4], [4, 2]]],
           [5, [[0, 1], [1, 2], [2, 3], [3, 4], [4, 0], [1, 0]]]],
)
_p = _P[-1]
_r = rnd(9109)
# one long ring with forward chords
_ring = [[i, (i + 1) % 300] for i in range(300)]
_ch = {(a, b) for a, b in _ring}
while len(_ch) < 560:
    a = _r.randrange(0, 290)
    b = a + _r.randint(2, 9)
    _ch.add((a, b))
_p["tests"].append([300, [list(x) for x in sorted(_ch)]])
# long DAG: boundary case where every edge counts
_dag = {(a, min(299, a + _r.randint(1, 6))) for a in range(299)} | {(a, min(299, a + _r.randint(1, 30))) for a in range(299)}
_p["tests"].append([300, [list(x) for x in sorted(_dag)]])
# two disjoint big rings: nothing fixes both
_p["tests"].append([300, [[i, (i + 1) % 150] for i in range(150)] + [[150 + i, 150 + (i + 1) % 150] for i in range(150)]])
_p["tests"].append([300, _dpairs(_r, 300, 800)])


def b_fix(n, edges):
    return sum(1 for i in range(len(edges)) if _acyclic_dfs(n, edges[:i] + edges[i + 1:]))


def g_fix(r):
    n = r.randint(1, 6)
    if r.random() < 0.5:
        e = _dpairs(r, n, r.randint(0, n + 3), loops=r.random() < 0.3)
    else:
        e = [[a, b] for a, b in _dpairs(r, n, r.randint(0, n + 2), loops=False) if a < b]
        e += [x for x in _dpairs(r, n, 2, loops=False) if x not in e and r.random() < 0.6]
    return [n, e]


def v_fix(tests):
    for t in tests:
        n, e = t["args"]
        assert 1 <= n <= 300 and len(e) <= 800
        _check_distinct_directed(n, e)
    exp = [t["expected"] for t in tests]
    assert 0 in exp and any(x > 0 for x in exp)
    assert tests[-3]["expected"] == len(tests[-3]["args"][1])
    assert tests[-2]["expected"] == 0


CHECKS["edges-whose-removal-gives-dag"] = (b_fix, g_fix, "exact")
VALIDATE["edges-whose-removal-gives-dag"] = v_fix

# =================================================================== HARD
# ---------------------------------------------------------------- shortest odd cycle
add(
    id="shortest-odd-cycle-length", title="Shortest Odd Cycle", diff="Hard", topic=T, tier="extra",
    fn="shortestOddCycle", params=[("n", "int"), ("edges", "int[][]")], ret="int", cmp="exact",
    desc="<p>An undirected graph has <code>n</code> nodes labelled <code>0</code> to <code>n - 1</code> and the connections <code>edges[i] = [a, b]</code>. It may be disconnected. A <em>cycle</em> visits at least three different nodes, never repeats a node and returns to its start; its length is the number of connections it uses.</p><p>Return the length of the shortest cycle that has an <strong>odd</strong> length. Return <code>-1</code> if the graph has no odd cycle, which means that it is bipartite.</p><pre>n = 7, edges = [[0,1],[1,2],[2,3],[3,4],[4,5],[5,6],[6,0],[0,3]]  ->  5\n(the ring of 7 is odd, but the chord 0-3 gives the cycles 0-1-2-3 (length 4) and 0-3-4-5-6 (length 5))\n\nn = 5, edges = [[0,1],[1,2],[2,3],[3,4],[4,0]]              ->  5\nn = 4, edges = [[0,1],[1,2],[2,3],[3,0]]                    ->  -1</pre>",
    constraints=["1 &le; n &le; 300", "0 &le; edges.length &le; 900", "0 &le; a, b &lt; n and a &ne; b", "No two edges join the same pair of nodes"],
    hints=["A graph has an odd cycle exactly when it is not bipartite, so the answer is -1 exactly when two-colouring succeeds. The hard part is finding the <em>shortest</em> odd cycle.",
           "Run a BFS from a start node s. If an edge joins two nodes of the <em>same</em> BFS level d, the two tree paths plus this edge form a closed walk of odd length 2d + 1.",
           "Do this BFS from every possible start node and take the minimum of 2d + 1 over all edges inside a level. It never underestimates, because the odd closed walk contains an odd cycle, and when s is on a shortest odd cycle of length 2k + 1 the edge opposite to s joins two nodes of level k."],
    editorial=["From a start node s, run a BFS and look at the levels (distances). An edge whose two endpoints are on the same level d closes a walk of length d + d + 1 = 2d + 1: down one tree path, across the edge and up the other. Every odd closed walk contains an odd simple cycle that is no longer than the walk, so this value is never smaller than the length of the shortest odd cycle of the graph.",
               "Now let C be a shortest odd cycle, with length 2k + 1, and start the BFS at a node s of C. Distances inside the graph from s to the nodes of C equal the distances along C: if some node of C were closer, the shortcut would split C into two parts, one of which would be an odd cycle shorter than C. Hence the two nodes of C opposite to s are both at level k and are joined by an edge of C, which yields the value 2k + 1.",
               "So the answer is the minimum, over all start nodes s and all edges (u, v) with level(u) = level(v), of 2 * level(u) + 1, or -1 if there is no such edge for any s. Edges between consecutive levels or inside different components never matter. The cost is n BFS runs of O(n + m) each, so O(n (n + m)) overall. Equivalent view: BFS in the 'doubled' graph with states (node, parity) looking for the shortest odd closed walk through each node."],
    time="O(n (n + m))", space="O(n + m)",
    solution='''from collections import deque


def shortestOddCycle(n, edges):
    adj = [[] for _ in range(n)]
    for a, b in edges:
        adj[a].append(b)
        adj[b].append(a)
    best = float("inf")
    for s in range(n):
        dist = [-1] * n
        dist[s] = 0
        queue = deque([s])
        while queue:
            u = queue.popleft()
            if 2 * dist[u] + 1 >= best:
                break
            for v in adj[u]:
                if dist[v] == -1:
                    dist[v] = dist[u] + 1
                    queue.append(v)
                elif dist[v] == dist[u]:
                    best = min(best, 2 * dist[u] + 1)
    return -1 if best == float("inf") else best
''',
    tests=[[6, [[0, 1], [1, 2], [2, 3], [3, 0], [3, 4], [4, 5], [5, 2]]],
           [5, [[0, 1], [1, 2], [2, 3], [3, 4], [4, 0]]],
           [4, [[0, 1], [1, 2], [2, 3], [3, 0]]],
           [1, []],
           [3, [[0, 1], [1, 2], [2, 0]]],
           [8, [[0, 1], [1, 2], [2, 3], [3, 0], [4, 5], [5, 6], [6, 7], [7, 4], [0, 4]]],
           [7, [[0, 1], [1, 2], [2, 3], [3, 4], [4, 5], [5, 6], [6, 0]]],
           [7, [[0, 1], [1, 2], [2, 3], [3, 4], [4, 5], [5, 6], [6, 0], [0, 3]]],
           [9, [[0, 1], [1, 2], [2, 3], [3, 4], [4, 5], [5, 6], [6, 7], [7, 8], [8, 0], [2, 6]]],
           [6, [[0, 1], [1, 2], [2, 3], [3, 4], [4, 5], [5, 0], [0, 3], [1, 4]]]],
)
_p = _P[-1]
_r = rnd(9110)
# even ring of 300 plus one chord between nodes at even distance: the only odd cycles use the chord
_p["tests"].append([300, [[i, (i + 1) % 300] for i in range(300)] + [[0, 150]]])
_p["tests"].append([300, [[i, (i + 1) % 300] for i in range(300)] + [[0, 100]]])
_p["tests"].append([299, [[i, (i + 1) % 299] for i in range(299)]])
for _m in (600, 700):
    _e, _side = _bip_pairs(_r, 300, _m)
    _res = _far_even(_r, 300, _e)
    _e.append([_res[1], _res[2]])
    _p["tests"].append([300, _e])
_p["tests"].append([300, _bip_pairs(_r, 300, 700)[0]])
# sparse tree with a few extra edges (some odd, far apart)
_tree = [[i, _r.randrange(max(0, i - 4), i)] for i in range(1, 300)]
_p["tests"].append([300, _tree + [[3, 250], [10, 200]]])


def b_soc(n, edges):
    c = [x for x in _cycle_lengths(n, edges) if x % 2 == 1]
    return min(c) if c else -1


def g_soc(r):
    n = r.randint(1, 8)
    if r.random() < 0.4:
        e, side = _bip_pairs(r, n, r.randint(0, n + 2))
        extra = [x for x in _pairs(r, n, 1) if x not in e and [x[1], x[0]] not in e]
        return [n, e + extra]
    return [n, _pairs(r, n, r.randint(0, n + 3))]


def v_soc(tests):
    for t in tests:
        n, edges = t["args"]
        assert 1 <= n <= 300 and len(edges) <= 900
        _check_distinct_undirected(n, edges)
        assert (t["expected"] == -1) == _is_bip(n, edges)
    exp = [t["expected"] for t in tests]
    assert -1 in exp and 3 in exp and max(exp) >= 100


CHECKS["shortest-odd-cycle-length"] = (b_soc, g_soc, "exact")
VALIDATE["shortest-odd-cycle-length"] = v_soc

# ---------------------------------------------------------------- largest peaceful group
add(
    id="largest-peaceful-group", title="Largest Peaceful Group", diff="Hard", topic=T, tier="extra",
    fn="largestPeacefulGroup", params=[("n", "int"), ("dislikes", "int[][]")], ret="int", cmp="exact",
    desc="<p>There are <code>n</code> people labelled <code>0</code> to <code>n - 1</code>. The list <code>dislikes</code> contains pairs <code>[a, b]</code>: people <code>a</code> and <code>b</code> dislike each other. The people can be split into two teams so that nobody dislikes anybody in their own team (the dislike graph is <em>bipartite</em>); this is guaranteed.</p><p>You want to invite as many people as possible to a party, but you must not invite two people who dislike each other. Return the maximum number of people you can invite.</p><pre>n = 4, dislikes = [[0,1],[1,2],[2,3]]  ->  2   (e.g. 0 and 2, or 1 and 3, or 0 and 3)\nn = 4, dislikes = [[0,1],[0,2],[0,3]]  ->  3   (everybody except person 0)\nn = 5, dislikes = []                   ->  5</pre>",
    constraints=["1 &le; n &le; 1,500", "0 &le; dislikes.length &le; 4,000", "0 &le; a, b &lt; n and a &ne; b; no pair appears twice", "The dislike graph is bipartite"],
    hints=["Without the bipartite guarantee this is a very hard problem. So the guarantee must help: what structure can you use once you know the two teams?",
           "Look at the people as two sides, left and right, with the dislikes as edges between them. A matching is a set of dislike pairs that share nobody. Each matched pair can contribute at most one invited person.",
           "By Konig's theorem the largest set with no dislike pair equals <code>n</code> minus the size of a maximum matching. Compute the maximum matching with augmenting paths (Hopcroft-Karp, or simple Kuhn's algorithm), and return <code>n - matching</code>."],
    editorial=["Inviting people so that no two dislike each other means choosing an <em>independent set</em> of the dislike graph, and you want a maximum one. In general graphs that is NP-hard, but in a bipartite graph there is a beautiful duality. Konig's theorem says the size of a maximum matching equals the size of a minimum vertex cover, and the complement of a vertex cover is an independent set. So the largest independent set has <code>n - M</code> people, where M is the size of a maximum matching.",
               "First two-colour the graph with a BFS to obtain the left side (colour 0) and the right side (colour 1). Then find a maximum matching between them. Hopcroft-Karp does it in rounds: a BFS from all free left nodes builds layers along alternating edges, and a DFS then finds a maximal set of shortest vertex-disjoint augmenting paths along those layers; each round raises the matching size, and O(sqrt(n)) rounds suffice. For these limits the simpler Kuhn's algorithm (one DFS per left node) would also pass, but it can be slower on adversarial inputs. Use an iterative DFS to avoid deep recursion on long paths.",
               "Answer <code>n - M</code>. Nodes without any dislike are never matched and are always invited, which the formula takes care of automatically. Hopcroft-Karp runs in O(m sqrt(n)) time. Checking the claim on a path of 4 people: the maximum matching has 2 edges, so the answer is 4 - 2 = 2."],
    time="O(m sqrt(n))", space="O(n + m)",
    solution='''from collections import deque


def largestPeacefulGroup(n, dislikes):
    adj = [[] for _ in range(n)]
    for a, b in dislikes:
        adj[a].append(b)
        adj[b].append(a)
    color = [-1] * n
    for s in range(n):
        if color[s] != -1:
            continue
        color[s] = 0
        queue = deque([s])
        while queue:
            u = queue.popleft()
            for v in adj[u]:
                if color[v] == -1:
                    color[v] = 1 - color[u]
                    queue.append(v)
    left = [v for v in range(n) if color[v] == 0]
    match_left = [-1] * n
    match_right = [-1] * n
    matching = 0
    while True:
        # BFS layers from all free left nodes along alternating paths
        layer = {}
        queue = deque()
        for u in left:
            if match_left[u] == -1:
                layer[u] = 0
                queue.append(u)
        found = False
        while queue:
            u = queue.popleft()
            for v in adj[u]:
                w = match_right[v]
                if w == -1:
                    found = True
                elif w not in layer:
                    layer[w] = layer[u] + 1
                    queue.append(w)
        if not found:
            break
        ptr = [0] * n
        for s in left:
            if match_left[s] != -1:
                continue
            stack = [s]
            chosen = []
            while stack:
                u = stack[-1]
                if ptr[u] < len(adj[u]):
                    v = adj[u][ptr[u]]
                    ptr[u] += 1
                    w = match_right[v]
                    if w == -1:
                        chosen.append(v)
                        for x, y in zip(stack, chosen):
                            match_left[x] = y
                            match_right[y] = x
                        matching += 1
                        break
                    if layer.get(w) == layer[u] + 1:
                        chosen.append(v)
                        stack.append(w)
                else:
                    stack.pop()
                    if chosen:
                        chosen.pop()
    return n - matching
''',
    tests=[[4, [[0, 1], [1, 2], [2, 3]]],
           [4, [[0, 1], [0, 2], [0, 3]]],
           [5, []],
           [1, []],
           [2, [[1, 0]]],
           [6, [[0, 1], [1, 2], [2, 3], [3, 4], [4, 5], [5, 0]]],
           [7, [[0, 1], [0, 2], [0, 3], [4, 3], [4, 5], [6, 5]]],
           [8, [[0, 4], [0, 5], [1, 4], [2, 4], [2, 6], [3, 6], [3, 7]]],
           [9, [[0, 1], [1, 2], [2, 3], [3, 4], [5, 6], [6, 7]]]],
)
_p = _P[-1]
_r = rnd(9111)
_p["tests"].append([1500, _mixed_components(_r, 1500, 1.0, sizes=(1, 3, 6, 40, 200, 600), extra=0.9)])
_p["tests"].append([1500, _bip_pairs(_r, 1500, 3800)[0]])
_p["tests"].append([1500, [[i, i + 1] for i in range(1499)]])
_e, _side = _bip_pairs(_r, 1200, 3000, side=[0] * 300 + [1] * 900)
_p["tests"].append([1200, _e])


def b_lpg(n, dislikes):
    best = 0
    for mask in range(1 << n):
        if all(not ((mask >> a) & 1 and (mask >> b) & 1) for a, b in dislikes):
            best = max(best, bin(mask).count("1"))
    return best


def g_lpg(r):
    n = r.randint(1, 12)
    return [n, _bip_pairs(r, n, r.randint(0, n + 4))[0]]


def v_lpg(tests):
    for t in tests:
        n, d = t["args"]
        assert 1 <= n <= 1500 and len(d) <= 4000
        _check_distinct_undirected(n, d)
        assert _is_bip(n, d), "not bipartite"
        assert (n + 1) // 2 <= t["expected"] <= n
    assert tests[-2]["expected"] == 750 and tests[-1]["expected"] >= 900


CHECKS["largest-peaceful-group"] = (b_lpg, g_lpg, "exact")
VALIDATE["largest-peaceful-group"] = v_lpg
