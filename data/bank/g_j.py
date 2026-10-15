"""Problems: graphs, trees as graphs (diameter, centers, rerooting, distance sums, subtree counts, longest paths). See data/lib.py for the registry."""
from collections import deque

from lib import add, rnd, CHECKS, VALIDATE, gen_arr  # noqa: F401
from lib import P as _P  # noqa: E402


# ------------------------------------------------------------------ helpers shared by the tests (not part of any solution)

def _shape(r, n, mode):
    """Parent index (always smaller than the node index) for nodes 1..n-1 of a tree with the given shape."""
    ps = [0] * n
    for i in range(1, n):
        if mode == "chain":
            p = i - 1
        elif mode == "star":
            p = 0
        elif mode == "deep":
            p = max(0, i - 1 - r.randrange(3))
        elif mode == "broom":
            p = i - 1 if i < n // 2 else max(0, n // 2 - 1)
        elif mode == "cater":
            p = i - 1 if i % 2 == 0 else max(0, i - 2)
        elif mode == "binary":
            p = (i - 1) // 2
        elif mode == "wide":
            p = r.randrange(min(i, 5))
        else:
            p = r.randrange(i)
        ps[i] = p
    return ps


def _edges(r, n, mode="rand"):
    """Random labelled tree on 0..n-1 as a shuffled list of randomly oriented edges."""
    ps = _shape(r, n, mode)
    lab = list(range(n))
    r.shuffle(lab)
    e = []
    for i in range(1, n):
        a, b = lab[ps[i]], lab[i]
        e.append([a, b] if r.random() < 0.5 else [b, a])
    r.shuffle(e)
    return e


def _parents(r, n, mode="rand", root0=False):
    """Random rooted tree as a parent array (-1 for the root). Parents may have larger indices than children."""
    ps = _shape(r, n, mode)
    lab = list(range(n))
    if root0:
        tail = lab[1:]
        r.shuffle(tail)
        lab = [0] + tail
    else:
        r.shuffle(lab)
    par = [-1] * n
    for i in range(1, n):
        par[lab[i]] = lab[ps[i]]
    return par


def _spider(r, lens):
    """A centre with one leg per entry of lens (each leg is a path of that many nodes), randomly relabelled."""
    n = 1 + sum(lens)
    lab = list(range(n))
    r.shuffle(lab)
    e = []
    nxt = 1
    for L in lens:
        prev = 0
        for _ in range(L):
            e.append([lab[prev], lab[nxt]])
            prev = nxt
            nxt += 1
    r.shuffle(e)
    return e


def _adjl(n, edges):
    adj = [[] for _ in range(n)]
    for a, b in edges:
        adj[a].append(b)
        adj[b].append(a)
    return adj


def _dists(n, adj, s):
    """Plain BFS distances from s (used only by brute forces)."""
    d = [-1] * n
    d[s] = 0
    q = deque([s])
    while q:
        u = q.popleft()
        for v in adj[u]:
            if d[v] < 0:
                d[v] = d[u] + 1
                q.append(v)
    return d


def _check_tree(n, edges):
    assert len(edges) == n - 1, "tree needs n-1 edges"
    seen = set()
    for a, b in edges:
        assert 0 <= a < n and 0 <= b < n and a != b, "bad endpoint"
        k = (min(a, b), max(a, b))
        assert k not in seen, "repeated edge"
        seen.add(k)
    assert all(x >= 0 for x in _dists(n, _adjl(n, edges), 0)), "not connected"


def _check_parents(par, root=None):
    n = len(par)
    roots = [i for i in range(n) if par[i] == -1]
    assert len(roots) == 1, "exactly one root"
    if root is not None:
        assert roots[0] == root
    assert all(par[i] == -1 or 0 <= par[i] < n for i in range(n))
    for v in range(n):  # every node reaches the root (no cycles)
        steps = 0
        while par[v] != -1:
            v = par[v]
            steps += 1
            assert steps <= n, "cycle in parent array"


# =================================================================== EASY
# ---------------------------------------------------------------- subtree sizes from a parent array
add(
    id="subtree-sizes-from-parent-array", title="Subtree Sizes from a Parent Array", diff="Easy", topic="Graphs",
    fn="subtreeSizes", params=[("parent", "int[]")], ret="int[]", cmp="exact",
    desc="<p>A rooted tree has <code>n</code> nodes numbered <code>0..n-1</code>. It is described by an array <code>parent</code> where <code>parent[v]</code> is the parent of node <code>v</code>, and the single root has <code>parent[root] = -1</code>. The root can be any node, and a parent may have a larger number than its child.</p><p>The <em>subtree size</em> of a node is the number of nodes in the subtree hanging below it, counting the node itself. Return an array <code>sizes</code> where <code>sizes[v]</code> is the subtree size of node <code>v</code>.</p><pre>parent = [1, -1, 1, 0, 0]\n\nnode 1 is the root with children 0 and 2; node 0 has children 3 and 4\nsizes  = [3, 5, 1, 1, 1]</pre>",
    constraints=["1 &le; n = parent.length &le; 100,000", "parent[v] = -1 for exactly one node (the root); every other entry is a node number in 0..n-1", "The array describes a valid tree (following parents from any node reaches the root)"],
    hints=["Walking up from every node and adding one to each ancestor works but can take O(n<sup>2</sup>) on a long chain.",
           "A node's size is 1 plus the sizes of its children. So children must be finished before their parent.",
           "Build the list of children of each node, get an order in which every parent appears before its children (BFS from the root), then go through that order backwards, adding each node's size to its parent."],
    editorial=["The size of a subtree obeys <code>size[v] = 1 + sum(size[c] for c in children[v])</code>. The values only depend on the children, so we need an order that processes a node after all of its descendants.",
               "Build <code>children</code> from the parent array, run a BFS from the root to get an order where parents come first, then sweep that order in reverse and add <code>size[v]</code> to <code>size[parent[v]]</code>. Because the parent array does not guarantee <code>parent[v] &lt; v</code>, a simple left-to-right sweep over indices would not be correct, which is why the BFS order is needed. A recursive DFS gives the same result but may overflow the call stack on a chain of 100,000 nodes.",
               "Every node is visited a constant number of times: O(n) time and O(n) space."],
    time="O(n)", space="O(n)",
    solution='''def subtreeSizes(parent):
    n = len(parent)
    children = [[] for _ in range(n)]
    root = 0
    for v, p in enumerate(parent):
        if p == -1:
            root = v
        else:
            children[p].append(v)
    order = [root]
    for u in order:  # BFS: parents appear before their children
        order.extend(children[u])
    size = [1] * n
    for u in reversed(order):
        if parent[u] != -1:
            size[parent[u]] += size[u]
    return size
''',
    tests=[[[1, -1, 1, 0, 0]], [[-1]], [[-1, 0]], [[1, -1]], [[-1, 0, 0, 1, 1, 2]], [[3, 0, 1, 4, -1]], [[4, 4, 4, 4, -1]],
           [[2, 0, -1, 2, 3, 3]], [[1, 2, 3, 4, -1]], [[-1, 0, 1, 0, 3, 3, 5]]],
)
_r = rnd(9701)
_P[-1]["tests"].append([_parents(_r, 3000, "rand")])
_P[-1]["tests"].append([_parents(_r, 3500, "chain")])
_P[-1]["tests"].append([_parents(_r, 3000, "star")])
_P[-1]["tests"].append([_parents(_r, 3000, "deep")])


def b_sizes(parent):
    n = len(parent)
    size = [0] * n
    for v in range(n):  # add 1 to the node itself and to every ancestor
        u = v
        while u != -1:
            size[u] += 1
            u = parent[u]
    return size


def g_sizes(r):
    n = r.randint(1, 10)
    return [_parents(r, n, r.choice(["rand", "chain", "star", "deep", "binary", "cater"]))]


def v_sizes(tests):
    for t in tests:
        par = t["args"][0]
        assert 1 <= len(par) <= 100000
        _check_parents(par)
        assert t["expected"][par.index(-1)] == len(par)


CHECKS["subtree-sizes-from-parent-array"] = (b_sizes, g_sizes, "exact")
VALIDATE["subtree-sizes-from-parent-array"] = v_sizes

# ---------------------------------------------------------------- edge list forms a tree
add(
    id="edge-list-forms-a-tree", title="Does This Edge List Form a Tree?", diff="Easy", topic="Graphs",
    fn="isTree", params=[("n", "int"), ("edges", "int[][]")], ret="bool", cmp="exact",
    desc="<p>You are given <code>n</code> nodes numbered <code>0..n-1</code> and a list <code>edges</code> of undirected edges <code>[a, b]</code>. The list is arbitrary: it may contain self-loops (<code>a == b</code>) or the same pair twice.</p><p>Return <code>true</code> if these nodes and edges together form a <em>tree</em>: the graph is connected and contains no cycle (a self-loop or a repeated pair counts as a cycle). Otherwise return <code>false</code>.</p><pre>n = 5, edges = [[0,1],[1,2],[3,2],[4,2]]   -> true\nn = 4, edges = [[0,1],[1,2],[2,0]]         -> false  (cycle, and node 3 is cut off)</pre>",
    constraints=["1 &le; n &le; 3,000", "0 &le; edges.length &le; 3,000", "0 &le; a, b &lt; n for every edge [a, b]"],
    hints=["A tree on n nodes has a very specific number of edges. What is it, and what does a different number tell you immediately?",
           "With exactly n - 1 edges, having no cycle and being connected are equivalent, so you only need to check one of them.",
           "Use union-find: for each edge, if both endpoints already share a root the edge closes a cycle, so return false; otherwise merge them. If you get through all n - 1 edges, return true."],
    editorial=["A tree with n nodes has exactly n - 1 edges. If the list has a different length the answer is false at once: fewer edges cannot connect the nodes, and more edges must create a cycle.",
               "When there are exactly n - 1 edges, a graph is connected exactly when it is acyclic, so checking one property is enough. Union-find does it neatly: process the edges in order, and if an edge joins two nodes that are already in the same set (this includes a self-loop and a repeated pair) a cycle exists. If every edge merges two different sets, the n - 1 merges have joined all n nodes into one set, so the graph is a tree.",
               "A BFS/DFS that checks that all n nodes are reached from node 0 works as well. Either approach runs in near-linear time and O(n) space."],
    time="O(n &middot; &alpha;(n))", space="O(n)",
    solution='''def isTree(n, edges):
    if len(edges) != n - 1:
        return False
    root = list(range(n))

    def find(x):
        while root[x] != x:
            root[x] = root[root[x]]
            x = root[x]
        return x

    for a, b in edges:
        ra, rb = find(a), find(b)
        if ra == rb:
            return False
        root[ra] = rb
    return True
''',
    tests=[[5, [[0, 1], [1, 2], [3, 2], [4, 2]]], [4, [[0, 1], [1, 2], [2, 0]]], [1, []], [1, [[0, 0]]], [2, [[0, 1]]], [2, []],
           [3, [[0, 1], [0, 1]]], [3, [[0, 1], [1, 2], [0, 2]]], [4, [[0, 1], [2, 3]]], [4, [[3, 2], [2, 1], [1, 0]]],
           [2, [[1, 1]]], [6, [[0, 1], [0, 2], [3, 4], [4, 5], [3, 5]]]],
)
_r = rnd(9702)
_P[-1]["tests"].append([3000, _edges(_r, 3000, "rand")])
_e = _edges(_r, 3000, "deep")
_e[_r.randrange(2999)] = [7, 7]
_P[-1]["tests"].append([3000, _e])
_e = _edges(_r, 3000, "wide")
_e[0] = [_e[1][0], _e[1][1]]  # repeated pair: still n-1 edges but not connected
_P[-1]["tests"].append([3000, _e])


def b_forms(n, edges):
    if len(edges) != n - 1:
        return False
    adj = _adjl(n, edges)
    seen = {0}
    stack = [0]
    while stack:
        u = stack.pop()
        for v in adj[u]:
            if v not in seen:
                seen.add(v)
                stack.append(v)
    return len(seen) == n


def g_forms(r):
    n = r.randint(1, 7)
    kind = r.randrange(4)
    e = _edges(r, n)
    if kind == 1 and e:
        e[r.randrange(len(e))] = [r.randrange(n), r.randrange(n)]
    elif kind == 2:
        e = [[r.randrange(n), r.randrange(n)] for _ in range(r.randint(0, n + 1))]
    elif kind == 3:
        e = e + [[r.randrange(n), r.randrange(n)]] if r.random() < 0.5 else e[:-1]
    return [n, e]


def v_forms(tests):
    for t in tests:
        n, edges = t["args"]
        assert 1 <= n <= 3000 and len(edges) <= 3000
        assert all(0 <= a < n and 0 <= b < n for a, b in edges)
    assert {t["expected"] for t in tests} == {True, False}


CHECKS["edge-list-forms-a-tree"] = (b_forms, g_forms, "exact")
VALIDATE["edge-list-forms-a-tree"] = v_forms

# =================================================================== MEDIUM
# ---------------------------------------------------------------- tree diameter
add(
    id="tree-diameter-edge-list", title="Diameter of a Tree", diff="Medium", topic="Graphs", tier="must",
    fn="treeDiameter", params=[("n", "int"), ("edges", "int[][]")], ret="int", cmp="exact",
    desc="<p>An undirected tree has <code>n</code> nodes numbered <code>0..n-1</code>. The list <code>edges</code> holds its <code>n - 1</code> edges, each as a pair <code>[a, b]</code>. The tree is connected and has no cycles.</p><p>The <em>diameter</em> of a tree is the number of edges on the longest path between any two nodes. Return the diameter.</p><pre>n = 6, edges = [[0,1],[1,2],[1,3],[3,4],[4,5]]\n\nlongest path: 2 - 1 - 3 - 4 - 5   (4 edges)   -> 4</pre>",
    constraints=["1 &le; n &le; 100,000", "edges.length = n - 1 and the edges form a tree", "0 &le; a, b &lt; n"],
    hints=["Trying every pair of nodes is far too slow. Is there a way to find just one end of a longest path?",
           "Start from any node and find the node farthest from it. Surprisingly, that node is always an end of some longest path.",
           "Run a BFS from node 0 to get the farthest node <code>u</code>, then run a second BFS from <code>u</code>. The largest distance found in the second search is the diameter."],
    editorial=["Two BFS passes are enough. First BFS from any node, say 0, and take the farthest node <code>u</code>. Then BFS from <code>u</code>; the largest distance in this second pass is the diameter.",
               "Why it works: in a tree the farthest node from any start is an endpoint of some longest path. Intuitively, any longest path must pass near the middle of the tree, and walking away from any node leads you out along one branch of that structure until you reach a path end; a swap argument shows you can always replace the other endpoint by a farther one if the first search had not found a path end.",
               "An alternative is a single DFS (dynamic programming): the longest downward chain from each node is <code>1 + max over children</code>, and the best path through a node combines its two longest child chains. Both versions run in O(n) time and need O(n) space; use an iterative traversal for a chain of 100,000 nodes."],
    time="O(n)", space="O(n)",
    solution='''def treeDiameter(n, edges):
    from collections import deque
    if n == 1:
        return 0
    adj = [[] for _ in range(n)]
    for a, b in edges:
        adj[a].append(b)
        adj[b].append(a)

    def farthest(s):
        dist = [-1] * n
        dist[s] = 0
        q = deque([s])
        last = s
        while q:
            u = q.popleft()
            last = u
            for v in adj[u]:
                if dist[v] < 0:
                    dist[v] = dist[u] + 1
                    q.append(v)
        return last, dist[last]

    u, _ = farthest(0)
    _, d = farthest(u)
    return d
''',
    tests=[[6, [[0, 1], [1, 2], [1, 3], [3, 4], [4, 5]]], [1, []], [2, [[1, 0]]], [3, [[0, 1], [1, 2]]], [4, [[0, 1], [0, 2], [0, 3]]],
           [5, [[2, 0], [2, 1], [2, 3], [2, 4]]], [7, [[0, 1], [0, 2], [1, 3], [1, 4], [2, 5], [2, 6]]],
           [8, [[0, 1], [1, 2], [2, 3], [3, 4], [2, 5], [5, 6], [6, 7]]]],
)
_r = rnd(9703)
_P[-1]["tests"].append([200, _edges(_r, 200, "deep")])
_P[-1]["tests"].append([3000, _edges(_r, 3000, "chain")])
_P[-1]["tests"].append([3000, _edges(_r, 3000, "rand")])
_P[-1]["tests"].append([2800, _edges(_r, 2800, "broom")])


def b_diam(n, edges):
    adj = _adjl(n, edges)
    return max(max(_dists(n, adj, s)) for s in range(n))


def g_diam(r):
    n = r.randint(1, 12)
    return [n, _edges(r, n, r.choice(["rand", "chain", "star", "deep", "broom", "cater", "wide"]))]


def v_diam(tests):
    for t in tests:
        n, edges = t["args"]
        assert 1 <= n <= 100000
        _check_tree(n, edges)


CHECKS["tree-diameter-edge-list"] = (b_diam, g_diam, "exact")
VALIDATE["tree-diameter-edge-list"] = v_diam

# ---------------------------------------------------------------- minimum height roots
add(
    id="minimum-height-tree-roots", title="Roots of Minimum Height Trees", diff="Medium", topic="Graphs",
    fn="minHeightRoots", params=[("n", "int"), ("edges", "int[][]")], ret="int[]", cmp="exact",
    desc="<p>An undirected tree has <code>n</code> nodes numbered <code>0..n-1</code>, given as <code>n - 1</code> edges <code>[a, b]</code>. Any node can be chosen as the root; the <em>height</em> of the resulting rooted tree is the number of edges on the longest downward path from the root.</p><p>Return all nodes that give the <em>smallest possible height</em> when chosen as the root, in ascending order.</p><pre>n = 7, edges = [[0,1],[1,2],[2,3],[3,4],[2,5],[5,6]]\n\nrooted at 2 the height is 2, at any other node it is at least 3   -> [2]</pre>",
    constraints=["1 &le; n &le; 100,000", "edges.length = n - 1 and the edges form a tree", "The answer always has one or two nodes"],
    hints=["Computing the height for every possible root takes O(n<sup>2</sup>). Think about which nodes are hopeless roots.",
           "A leaf is never a better root than its neighbour (unless n is tiny). Remove all leaves, and repeat on what remains.",
           "Peel the tree layer by layer: keep a queue of nodes of degree 1, delete them, decrease the degrees of their neighbours, and continue until at most 2 nodes remain. Those nodes are the answer."],
    editorial=["The best roots are the centers of the tree: the middle node of a longest path, or its two middle nodes if that path has an odd number of edges. So there are at most two answers.",
               "Find them by peeling leaves. Put all nodes of degree 1 in a list. While more than 2 nodes remain, remove the whole current leaf layer, subtract the removed count from the remaining total, decrease the degree of each removed node's neighbour, and collect the neighbours that become leaves as the next layer. When at most two nodes are left, they are the centers.",
               "Each node and edge is processed once, so the time is O(n) and the space is O(n). Handle <code>n &le; 2</code> separately (every node is a center): with n = 2 the two nodes would otherwise be peeled together."],
    time="O(n)", space="O(n)",
    solution='''def minHeightRoots(n, edges):
    if n <= 2:
        return list(range(n))
    adj = [[] for _ in range(n)]
    for a, b in edges:
        adj[a].append(b)
        adj[b].append(a)
    deg = [len(x) for x in adj]
    leaves = [v for v in range(n) if deg[v] == 1]
    remaining = n
    while remaining > 2:
        remaining -= len(leaves)
        nxt = []
        for u in leaves:
            for v in adj[u]:
                deg[v] -= 1
                if deg[v] == 1:
                    nxt.append(v)
        leaves = nxt
    return sorted(leaves)
''',
    tests=[[7, [[0, 1], [1, 2], [2, 3], [3, 4], [2, 5], [5, 6]]], [1, []], [2, [[0, 1]]], [3, [[0, 1], [1, 2]]], [4, [[1, 0], [1, 2], [1, 3]]],
           [6, [[3, 0], [3, 1], [3, 2], [3, 4], [5, 4]]], [4, [[0, 1], [1, 2], [2, 3]]], [5, [[0, 1], [1, 2], [2, 3], [3, 4]]],
           [8, [[0, 1], [1, 2], [2, 3], [3, 4], [4, 5], [3, 6], [6, 7]]]],
)
_r = rnd(9704)
_P[-1]["tests"].append([2000, _edges(_r, 2000, "chain")])
_P[-1]["tests"].append([1999, _edges(_r, 1999, "chain")])
_P[-1]["tests"].append([2000, _edges(_r, 2000, "star")])
_P[-1]["tests"].append([2500, _edges(_r, 2500, "rand")])
_P[-1]["tests"].append([1500, _edges(_r, 1500, "deep")])


def b_mht(n, edges):
    adj = _adjl(n, edges)
    height = [max(_dists(n, adj, s)) for s in range(n)]
    best = min(height)
    return [v for v in range(n) if height[v] == best]


def g_mht(r):
    n = r.randint(1, 12)
    return [n, _edges(r, n, r.choice(["rand", "chain", "star", "deep", "broom", "cater", "wide"]))]


def v_mht(tests):
    for t in tests:
        n, edges = t["args"]
        assert 1 <= n <= 100000
        _check_tree(n, edges)
        assert len(t["expected"]) in (1, 2) and t["expected"] == sorted(t["expected"])
    assert {len(t["expected"]) for t in tests} == {1, 2}


CHECKS["minimum-height-tree-roots"] = (b_mht, g_mht, "exact")
VALIDATE["minimum-height-tree-roots"] = v_mht

# ---------------------------------------------------------------- company broadcast time
add(
    id="company-broadcast-completion-time", title="Company Broadcast Completion Time", diff="Medium", topic="Graphs",
    fn="broadcastTime", params=[("manager", "int[]"), ("informTime", "int[]")], ret="int", cmp="exact",
    desc="<p>A company has <code>n</code> employees numbered <code>0..n-1</code>. The array <code>manager</code> gives each employee's direct manager, and the head of the company has <code>manager[head] = -1</code>. The company hierarchy is a tree rooted at the head.</p><p>The head learns some news at time 0. An employee who learns it needs <code>informTime[e]</code> minutes to tell <em>all</em> of their direct subordinates at once (they all hear it exactly <code>informTime[e]</code> minutes later). Employees without subordinates have <code>informTime = 0</code>. Return the number of minutes until every employee knows the news.</p><pre>manager    = [-1, 0, 0, 1, 1, 2]\ninformTime = [ 3, 2, 4, 0, 0, 0]\n\nemployees 1 and 2 hear at 3, employees 3 and 4 at 3+2 = 5, employee 5 at 3+4 = 7   -> 7</pre>",
    constraints=["1 &le; n = manager.length = informTime.length &le; 100,000", "Exactly one employee has manager -1; every other manager[e] is a valid employee number and the hierarchy is a tree", "0 &le; informTime[e] &le; 1,000 (informTime[e] is 0 when e has no subordinates)"],
    hints=["When does an employee hear the news? Think of the chain of managers above them.",
           "An employee hears it at the sum of <code>informTime</code> of all their managers on the way up to the head. The answer is the largest such sum over all employees.",
           "Build the list of subordinates of each manager and traverse from the head, passing down the time at which each employee hears the news (parent's time plus the parent's <code>informTime</code>). Use a stack or queue instead of recursion."],
    editorial=["Model the hierarchy as a rooted tree. If employee <code>e</code> hears at time <code>t[e]</code>, then each direct subordinate <code>s</code> hears at <code>t[e] + informTime[e]</code>, because the manager tells everybody in one go. So <code>t[head] = 0</code> and the answer is the maximum of <code>t</code> over all employees (which is always attained at a leaf).",
               "Build <code>subordinates</code> lists from the manager array, then traverse top-down with a stack, storing the arrival time of each employee. This is O(n) time and space. A recursive DFS gives the same result but the hierarchy can be 100,000 levels deep (a chain), so prefer an iterative traversal.",
               "Notice that the time spent by a manager does not depend on how many subordinates there are, only on the manager. This is why the answer is simply the heaviest root-to-leaf path when each node is weighted by its <code>informTime</code>."],
    time="O(n)", space="O(n)",
    solution='''def broadcastTime(manager, informTime):
    n = len(manager)
    subs = [[] for _ in range(n)]
    head = 0
    for e, m in enumerate(manager):
        if m == -1:
            head = e
        else:
            subs[m].append(e)
    best = 0
    stack = [(head, 0)]
    while stack:
        e, t = stack.pop()
        if t > best:
            best = t
        for s in subs[e]:
            stack.append((s, t + informTime[e]))
    return best
''',
    tests=[[[-1, 0, 0, 1, 1, 2], [3, 2, 4, 0, 0, 0]], [[-1], [0]], [[-1, 0], [5, 0]], [[1, -1], [0, 7]], [[-1, 0, 0, 0], [4, 0, 0, 0]],
           [[-1, 0, 1, 2, 3], [1, 2, 3, 4, 0]], [[2, 2, -1, 2, 3], [0, 0, 6, 3, 0]], [[-1, 0, 0, 1, 1], [0, 0, 0, 0, 0]],
           [[-1, 0, 0, 1, 2], [5, 1, 9, 0, 0]]],
)
_r = rnd(9705)


def _mk_broadcast(r, n, mode, hi=1000):
    par = _parents(r, n, mode)
    has_sub = [False] * n
    for p in par:
        if p != -1:
            has_sub[p] = True
    return [par, [r.randint(0, hi) if has_sub[v] else 0 for v in range(n)]]


_P[-1]["tests"].append(_mk_broadcast(_r, 3000, "rand"))
_P[-1]["tests"].append(_mk_broadcast(_r, 3000, "chain", 20))
_P[-1]["tests"].append(_mk_broadcast(_r, 3000, "deep", 1000))
_P[-1]["tests"].append(_mk_broadcast(_r, 3000, "star", 1000))


def b_broadcast(manager, informTime):
    best = 0
    for e in range(len(manager)):
        t = 0
        u = e
        while manager[u] != -1:  # every manager above e adds the time they need to tell their team
            u = manager[u]
            t += informTime[u]
        best = max(best, t)
    return best


def g_broadcast(r):
    n = r.randint(1, 10)
    par = _parents(r, n, r.choice(["rand", "chain", "star", "deep", "binary"]))
    has_sub = [False] * n
    for p in par:
        if p != -1:
            has_sub[p] = True
    return [par, [r.randint(0, 6) if has_sub[v] else 0 for v in range(n)]]


def v_broadcast(tests):
    for t in tests:
        manager, inform = t["args"]
        assert 1 <= len(manager) <= 100000 and len(manager) == len(inform)
        _check_parents(manager)
        assert all(0 <= x <= 1000 for x in inform)
        has_sub = set(manager)
        assert all(inform[v] == 0 for v in range(len(manager)) if v not in has_sub)


CHECKS["company-broadcast-completion-time"] = (b_broadcast, g_broadcast, "exact")
VALIDATE["company-broadcast-completion-time"] = v_broadcast

# ---------------------------------------------------------------- subtree nodes with the same label
add(
    id="subtree-nodes-sharing-node-label", title="Subtree Nodes Sharing the Node's Label", diff="Medium", topic="Graphs",
    fn="sameLabelCounts", params=[("n", "int"), ("edges", "int[][]"), ("labels", "string")], ret="int[]", cmp="exact",
    desc="<p>An undirected tree has <code>n</code> nodes numbered <code>0..n-1</code> and is rooted at node <code>0</code>. Its <code>n - 1</code> edges are given as pairs <code>[a, b]</code>. Each node carries a lowercase letter: <code>labels[v]</code> is the label of node <code>v</code>.</p><p>For every node <code>v</code>, count the nodes in the subtree of <code>v</code> (including <code>v</code> itself) whose label equals <code>labels[v]</code>. Return the counts as an array indexed by node.</p><pre>n = 5, edges = [[0,1],[0,2],[1,3],[1,4]], labels = \"abaab\"\n\nnode 0 ('a'): subtree is everything, 'a' occurs 3 times\nnode 1 ('b'): subtree {1,3,4} = b,a,b -> 2\nresult = [3, 2, 1, 1, 1]</pre>",
    constraints=["1 &le; n &le; 50,000", "edges.length = n - 1 and the edges form a tree", "labels.length = n and every character is a lowercase letter a-z"],
    hints=["For each node, collecting its subtree and counting letters costs O(n) per node, O(n<sup>2</sup>) in total on a chain.",
           "If each node knew how many times each of the 26 letters occurs in its subtree, the answer for a node would be one lookup.",
           "Root the tree at 0, get a BFS order, and sweep it backwards: add a node's own letter to its count array, record the answer, then add its 26 counts into its parent's array."],
    editorial=["Keep for every node an array of 26 counters: how many nodes of each letter lie in its subtree. A node's array is its own letter plus the arrays of all its children, so it can be computed bottom-up. The answer for node <code>v</code> is the entry for <code>labels[v]</code> in its array.",
               "To process children before parents without recursion, find a BFS order from the root (recording each node's parent) and walk it in reverse. When we reach <code>v</code>, all its descendants were already merged into <code>cnt[v]</code>; add <code>v</code>'s own letter, read the answer, then add <code>cnt[v]</code> into <code>cnt[parent[v]]</code>.",
               "Each node merges 26 numbers into its parent once, so the time is O(26 &middot; n) and the space is O(26 &middot; n). Another route is an Euler tour: each subtree becomes a contiguous range, and the question becomes counting a letter in a range, answered with 26 prefix-count arrays or per-letter sorted position lists and binary search."],
    time="O(26 &middot; n)", space="O(26 &middot; n)",
    solution='''def sameLabelCounts(n, edges, labels):
    adj = [[] for _ in range(n)]
    for a, b in edges:
        adj[a].append(b)
        adj[b].append(a)
    parent = [-1] * n
    order = [0]
    seen = [False] * n
    seen[0] = True
    for u in order:
        for v in adj[u]:
            if not seen[v]:
                seen[v] = True
                parent[v] = u
                order.append(v)
    cnt = [[0] * 26 for _ in range(n)]
    res = [0] * n
    for u in reversed(order):
        c = ord(labels[u]) - 97
        cnt[u][c] += 1
        res[u] = cnt[u][c]
        p = parent[u]
        if p >= 0:
            cp, cu = cnt[p], cnt[u]
            for i in range(26):
                cp[i] += cu[i]
    return res
''',
    tests=[[5, [[0, 1], [0, 2], [1, 3], [1, 4]], "abaab"], [1, [], "z"], [2, [[1, 0]], "aa"], [2, [[0, 1]], "ab"],
           [4, [[0, 1], [1, 2], [2, 3]], "aaaa"], [4, [[3, 0], [3, 1], [3, 2]], "abca"], [6, [[0, 1], [0, 2], [1, 3], [1, 4], [2, 5]], "abacbe"],
           [7, [[0, 1], [1, 2], [2, 3], [3, 4], [4, 5], [5, 6]], "abababa"], [5, [[2, 0], [2, 1], [4, 2], [3, 4]], "cbabc"]],
)
_r = rnd(9706)
for _n, _mode, _alpha in ((2500, "rand", "abc"), (2500, "chain", "ab"), (2000, "deep", "abcdefghijklmnopqrstuvwxyz")):
    _P[-1]["tests"].append([_n, _edges(_r, _n, _mode), "".join(_r.choice(_alpha) for _ in range(_n))])


def b_labels(n, edges, labels):
    adj = _adjl(n, edges)
    parent = [-2] * n
    parent[0] = -1
    stack = [0]
    while stack:
        u = stack.pop()
        for v in adj[u]:
            if parent[v] == -2:
                parent[v] = u
                stack.append(v)
    res = []
    for v in range(n):
        c = 0
        for u in range(n):  # u is in the subtree of v when v is on the way from u up to the root
            w = u
            while w != -1 and w != v:
                w = parent[w]
            if w == v and labels[u] == labels[v]:
                c += 1
        res.append(c)
    return res


def g_labels(r):
    n = r.randint(1, 11)
    alpha = "abcdefghijklmnopqrstuvwxyz"[:r.randint(1, 4)]
    return [n, _edges(r, n, r.choice(["rand", "chain", "star", "deep", "binary"])), "".join(r.choice(alpha) for _ in range(n))]


def v_labels(tests):
    for t in tests:
        n, edges, labels = t["args"]
        assert 1 <= n <= 50000 and len(labels) == n
        _check_tree(n, edges)
        assert all("a" <= ch <= "z" for ch in labels)
        assert all(1 <= x <= n for x in t["expected"])


CHECKS["subtree-nodes-sharing-node-label"] = (b_labels, g_labels, "exact")
VALIDATE["subtree-nodes-sharing-node-label"] = v_labels

# ---------------------------------------------------------------- nodes lying on some longest path
add(
    id="nodes-on-some-longest-path", title="Nodes on Some Longest Path", diff="Medium", topic="Graphs", tier="extra",
    fn="countDiameterNodes", params=[("n", "int"), ("edges", "int[][]")], ret="int", cmp="exact",
    desc="<p>An undirected tree has <code>n</code> nodes numbered <code>0..n-1</code> and <code>n - 1</code> edges <code>[a, b]</code>. A <em>longest path</em> is a path between two nodes with the maximum possible number of edges (the diameter). A tree may have many different longest paths.</p><p>Return how many nodes lie on <em>at least one</em> longest path.</p><pre>n = 7, edges = [[0,1],[1,2],[2,3],[3,4],[2,5],[1,6]]\n\nthe diameter is 4 and the longest paths are 0-1-2-3-4 and 6-1-2-3-4\nnodes on them: 0, 1, 2, 3, 4, 6   -> 6   (node 5 is on none)</pre>",
    constraints=["1 &le; n &le; 100,000", "edges.length = n - 1 and the edges form a tree", "A single node is a path of length 0 and lies on it, so n = 1 gives 1"],
    hints=["First find the diameter D. Then the question is which nodes can be an inner point or end of a path of exactly D edges.",
           "For a node v, look at the longest chains that start at v and leave it through different neighbours. A path of length D passes through v exactly when the two longest such chains add up to D.",
           "Compute <code>down[v]</code> (height of v's subtree) and <code>up[v]</code> (longest chain starting at v and going first to its parent) with a downward pass and an upward pass; for each node take the top two branch lengths (chains through different neighbours, plus 0), and count the nodes where they sum to the maximum over all nodes."],
    editorial=["For any node v, every branch from v goes out through one neighbour. Let the branch lengths be the longest chain starting at v and leaving through each neighbour. The best path <em>passing through</em> v has length equal to the sum of the two longest branch lengths (a missing branch counts as 0, which makes v an end of the path). The diameter D is the maximum of this value over all v, and v lies on a longest path exactly when its value equals D.",
               "Compute the branches with rerooting. Root the tree at 0. <code>down[v]</code> is the longest chain going down from v (0 for a leaf). For a child c of p, the branch of p through c has length <code>down[c] + 1</code>. The branch of v going up is <code>up[v] = 1 + max(up[p], best branch of p through a child other than v)</code>, where <code>up</code> of the root is treated as 0. To get 'best other child' in O(1), keep the two largest child branches of each node.",
               "Then for each node collect its branch values (child branches and, for non-roots, the up branch), take the two largest (pad with 0), and sum them. Take the maximum as D and count nodes that reach it. Everything is O(n) with two passes over a BFS order."],
    time="O(n)", space="O(n)",
    solution='''def countDiameterNodes(n, edges):
    if n == 1:
        return 1
    adj = [[] for _ in range(n)]
    for a, b in edges:
        adj[a].append(b)
        adj[b].append(a)
    parent = [-1] * n
    order = [0]
    seen = [False] * n
    seen[0] = True
    for u in order:
        for v in adj[u]:
            if not seen[v]:
                seen[v] = True
                parent[v] = u
                order.append(v)
    down = [0] * n
    top1 = [0] * n  # two largest child branches (down[c] + 1) of each node
    top2 = [0] * n
    for u in reversed(order):
        p = parent[u]
        if p >= 0:
            b = down[u] + 1
            if b > top1[p]:
                top2[p] = top1[p]
                top1[p] = b
            elif b > top2[p]:
                top2[p] = b
            down[p] = top1[p]
    up = [0] * n
    for u in order:
        p = parent[u]
        if p < 0:
            continue
        other = top2[p] if down[u] + 1 == top1[p] else top1[p]
        up[u] = 1 + max(up[p], other)
    through = [0] * n
    for v in range(n):
        a, b = top1[v], top2[v]
        if v != 0:
            x = up[v]
            if x > a:
                a, b = x, a
            elif x > b:
                b = x
        through[v] = a + b
    best = max(through)
    return sum(1 for x in through if x == best)
''',
    tests=[[7, [[0, 1], [1, 2], [2, 3], [3, 4], [2, 5], [1, 6]]], [1, []], [2, [[0, 1]]], [3, [[0, 1], [1, 2]]], [4, [[0, 1], [0, 2], [0, 3]]],
           [5, [[0, 1], [1, 2], [2, 3], [3, 4]]], [7, [[0, 1], [1, 2], [2, 3], [3, 4], [2, 5], [5, 6]]],
           [9, [[0, 1], [1, 2], [0, 3], [3, 4], [0, 5], [5, 6], [6, 7], [7, 8]]], [6, [[0, 1], [0, 2], [0, 3], [3, 4], [3, 5]]]],
)
_r = rnd(9707)
_P[-1]["tests"].append([2401, _spider(_r, [800, 800, 800])])
_P[-1]["tests"].append([2501, _spider(_r, [1200, 1200, 100])])
_P[-1]["tests"].append([3000, _edges(_r, 3000, "rand")])
_P[-1]["tests"].append([2000, _edges(_r, 2000, "cater")])


def b_ondiam(n, edges):
    adj = _adjl(n, edges)
    d = [_dists(n, adj, s) for s in range(n)]
    D = max(max(row) for row in d)
    on = set()
    for a in range(n):
        for b in range(n):
            if d[a][b] == D:
                on.update(v for v in range(n) if d[a][v] + d[v][b] == D)
    return len(on)


def g_ondiam(r):
    n = r.randint(1, 12)
    if r.random() < 0.3 and n >= 4:
        k = r.randint(2, 4)
        lens = [r.randint(1, 3) for _ in range(k)]
        return [1 + sum(lens), _spider(r, lens)]
    return [n, _edges(r, n, r.choice(["rand", "chain", "star", "deep", "broom", "cater", "wide"]))]


def v_ondiam(tests):
    for t in tests:
        n, edges = t["args"]
        assert 1 <= n <= 100000
        _check_tree(n, edges)
        assert 1 <= t["expected"] <= n


CHECKS["nodes-on-some-longest-path"] = (b_ondiam, g_ondiam, "exact")
VALIDATE["nodes-on-some-longest-path"] = v_ondiam

# ---------------------------------------------------------------- pairs at distance exactly k
add(
    id="node-pairs-at-distance-exactly-k", title="Node Pairs at Distance Exactly K", diff="Medium", topic="Graphs", tier="extra",
    fn="countPairsAtDistance", params=[("n", "int"), ("edges", "int[][]"), ("k", "int")], ret="int", cmp="exact",
    desc="<p>An undirected tree has <code>n</code> nodes numbered <code>0..n-1</code> and <code>n - 1</code> edges <code>[a, b]</code>. The distance between two nodes is the number of edges on the unique path connecting them.</p><p>Return the number of unordered pairs of distinct nodes <code>{u, v}</code> whose distance is exactly <code>k</code>.</p><pre>n = 6, edges = [[0,1],[0,2],[1,3],[1,4],[2,5]], k = 2\n\npairs: {0,3} {0,4} {0,5} {3,4} {1,2}   -> 5</pre>",
    constraints=["1 &le; n &le; 50,000", "1 &le; k &le; 100", "edges.length = n - 1 and the edges form a tree"],
    hints=["A BFS from every node counts everything but costs O(n<sup>2</sup>) overall. Use the fact that k is small.",
           "Root the tree. For every node v let <code>cnt[v][d]</code> be the number of nodes at depth d below v (d from 0 to k). A pair at distance k has a top node (their lowest common ancestor) at which the two halves meet.",
           "Merge the children of v one by one into <code>cnt[v]</code>. Before adding a child c, every node already collected at depth i can pair with every node at depth k - 1 - i below c; add <code>cur[i] * cnt[c][k-1-i]</code>, then fold c's counts in, shifted by one."],
    editorial=["Every pair of nodes has a unique lowest common ancestor in the rooted tree, so count each pair at its LCA. Keep, for each node, an array <code>cnt[d]</code> for <code>d = 0..k</code>: the number of nodes in its subtree at depth exactly d below it (so <code>cnt[0] = 1</code>).",
               "Process nodes bottom-up. For a node v start with <code>cur = [1, 0, ..., 0]</code> (just v). For each child c in turn, count the pairs that have v as LCA and one node inside c's subtree and the other either v itself or inside an earlier child's subtree: for each i, <code>cur[i] * cnt[c][k - 1 - i]</code>, because a node at depth j below c is at depth j + 1 below v and we need <code>i + j + 1 = k</code>. Then add c into cur: <code>cur[j+1] += cnt[c][j]</code>. Merging children one at a time ensures that nodes from the same child are never paired through v.",
               "Each merge costs O(k), and there are n - 1 merges, so the total time is O(n &middot; k). The answer is at most n(n-1)/2 &le; 1.25 &middot; 10<sup>9</sup>, which fits in 32 bits. Use an iterative bottom-up order to avoid deep recursion."],
    time="O(n &middot; k)", space="O(n &middot; k)",
    solution='''def countPairsAtDistance(n, edges, k):
    adj = [[] for _ in range(n)]
    for a, b in edges:
        adj[a].append(b)
        adj[b].append(a)
    parent = [-1] * n
    order = [0]
    seen = [False] * n
    seen[0] = True
    for u in order:
        for v in adj[u]:
            if not seen[v]:
                seen[v] = True
                parent[v] = u
                order.append(v)
    cnt = [None] * n
    total = 0
    for v in reversed(order):
        cur = [0] * (k + 1)
        cur[0] = 1
        for c in adj[v]:
            if c == parent[v]:
                continue
            ch = cnt[c]
            cnt[c] = None
            for i in range(k):
                total += cur[i] * ch[k - 1 - i]
            for j in range(k):
                cur[j + 1] += ch[j]
        cnt[v] = cur
    return total
''',
    tests=[[6, [[0, 1], [0, 2], [1, 3], [1, 4], [2, 5]], 2], [1, [], 1], [2, [[0, 1]], 1], [2, [[0, 1]], 2], [5, [[0, 1], [1, 2], [2, 3], [3, 4]], 4],
           [5, [[0, 1], [1, 2], [2, 3], [3, 4]], 3], [5, [[2, 0], [2, 1], [2, 3], [2, 4]], 2], [5, [[2, 0], [2, 1], [2, 3], [2, 4]], 1],
           [7, [[0, 1], [0, 2], [1, 3], [1, 4], [2, 5], [2, 6]], 3], [7, [[0, 1], [0, 2], [1, 3], [1, 4], [2, 5], [2, 6]], 4]],
)
_r = rnd(9708)
_P[-1]["tests"].append([3000, _edges(_r, 3000, "rand"), 6])
_P[-1]["tests"].append([3000, _edges(_r, 3000, "deep"), 50])
_P[-1]["tests"].append([2500, _edges(_r, 2500, "star"), 2])
_P[-1]["tests"].append([2500, _edges(_r, 2500, "chain"), 100])


def b_pairs_k(n, edges, k):
    adj = _adjl(n, edges)
    total = 0
    for s in range(n):
        total += sum(1 for x in _dists(n, adj, s) if x == k)
    return total // 2


def g_pairs_k(r):
    n = r.randint(1, 12)
    return [n, _edges(r, n, r.choice(["rand", "chain", "star", "deep", "broom", "cater", "wide", "binary"])), r.randint(1, 6)]


def v_pairs_k(tests):
    for t in tests:
        n, edges, k = t["args"]
        assert 1 <= n <= 50000 and 1 <= k <= 100
        _check_tree(n, edges)
    assert any(t["expected"] == 0 for t in tests) and any(t["expected"] > 100 for t in tests)


CHECKS["node-pairs-at-distance-exactly-k"] = (b_pairs_k, g_pairs_k, "exact")
VALIDATE["node-pairs-at-distance-exactly-k"] = v_pairs_k

# =================================================================== HARD
# ---------------------------------------------------------------- sum of distances to every node (rerooting)
add(
    id="tree-distance-sums-rerooting", title="Sum of Distances from Every Node", diff="Hard", topic="Graphs",
    fn="distanceSums", params=[("n", "int"), ("edges", "int[][]")], ret="int[]", cmp="exact",
    desc="<p>An undirected tree has <code>n</code> nodes numbered <code>0..n-1</code> and <code>n - 1</code> edges <code>[a, b]</code>. The distance between two nodes is the number of edges on the path between them.</p><p>Return an array <code>answer</code> of length <code>n</code> where <code>answer[v]</code> is the sum of the distances from node <code>v</code> to all the other nodes.</p><pre>n = 5, edges = [[0,1],[1,2],[1,3],[3,4]]\n\nanswer[0] = 1+2+2+3 = 8      answer[1] = 1+1+1+2 = 5\nanswer = [8, 5, 8, 6, 9]</pre>",
    constraints=["1 &le; n &le; 30,000", "edges.length = n - 1 and the edges form a tree", "Running a BFS from every node (O(n<sup>2</sup>)) is too slow; an O(n) method exists"],
    hints=["Computing the answer for one fixed root is easy: add up the depths of all nodes. The hard part is doing it for every root.",
           "Compare the answer of a node p with the answer of its child c. Moving the root from p to c brings the nodes in c's subtree one step closer and sends all other nodes one step farther.",
           "Root at 0, compute <code>size[v]</code> and <code>answer[0]</code>, then for each child c of p use <code>answer[c] = answer[p] - size[c] + (n - size[c])</code>, processing nodes in BFS order."],
    editorial=["This is the classic rerooting technique: compute the answer for one root, then derive the answer for each neighbour in O(1).",
               "Root the tree at 0 and get a BFS order with parents. Compute <code>size[v]</code> (subtree sizes) by sweeping the order backwards, and compute <code>answer[0]</code> as the sum of all depths. Now take a node p and its child c. If the root moves from p to c, then every node inside c's subtree (there are <code>size[c]</code> of them) gets one edge closer, and every other node (<code>n - size[c]</code> of them) gets one edge farther. So <code>answer[c] = answer[p] - size[c] + (n - size[c])</code>. Sweep the BFS order forwards and fill every answer.",
               "Total time O(n) and space O(n). The largest possible value is the sum on a path, n(n-1)/2, which is under 4.5 &middot; 10<sup>8</sup> for the allowed n, so it fits in 32 bits."],
    time="O(n)", space="O(n)",
    solution='''def distanceSums(n, edges):
    adj = [[] for _ in range(n)]
    for a, b in edges:
        adj[a].append(b)
        adj[b].append(a)
    parent = [-1] * n
    depth = [0] * n
    order = [0]
    seen = [False] * n
    seen[0] = True
    for u in order:
        for v in adj[u]:
            if not seen[v]:
                seen[v] = True
                parent[v] = u
                depth[v] = depth[u] + 1
                order.append(v)
    size = [1] * n
    for u in reversed(order):
        if parent[u] >= 0:
            size[parent[u]] += size[u]
    ans = [0] * n
    ans[0] = sum(depth)
    for u in order:
        p = parent[u]
        if p >= 0:
            ans[u] = ans[p] + n - 2 * size[u]
    return ans
''',
    tests=[[5, [[0, 1], [1, 2], [1, 3], [3, 4]]], [1, []], [2, [[1, 0]]], [3, [[0, 1], [1, 2]]], [4, [[0, 1], [0, 2], [0, 3]]], [4, [[3, 2], [2, 1], [1, 0]]],
           [6, [[0, 1], [0, 2], [2, 3], [2, 4], [2, 5]]], [7, [[0, 1], [0, 2], [1, 3], [1, 4], [2, 5], [2, 6]]]],
)
_r = rnd(9709)
_P[-1]["tests"].append([1800, _edges(_r, 1800, "chain")])
_P[-1]["tests"].append([1800, _edges(_r, 1800, "rand")])
_P[-1]["tests"].append([1500, _edges(_r, 1500, "star")])
_P[-1]["tests"].append([1500, _edges(_r, 1500, "broom")])


def b_distsum(n, edges):
    adj = _adjl(n, edges)
    return [sum(_dists(n, adj, s)) for s in range(n)]


def g_distsum(r):
    n = r.randint(1, 12)
    return [n, _edges(r, n, r.choice(["rand", "chain", "star", "deep", "broom", "cater", "wide", "binary"]))]


def v_distsum(tests):
    for t in tests:
        n, edges = t["args"]
        assert 1 <= n <= 30000
        _check_tree(n, edges)
        assert len(t["expected"]) == n and max(t["expected"]) <= n * (n - 1) // 2


CHECKS["tree-distance-sums-rerooting"] = (b_distsum, g_distsum, "exact")
VALIDATE["tree-distance-sums-rerooting"] = v_distsum

# ---------------------------------------------------------------- joining two trees
add(
    id="minimum-diameter-after-joining-two-trees", title="Minimum Diameter After Joining Two Trees", diff="Hard", topic="Graphs", tier="extra",
    fn="minDiameterAfterJoin", params=[("edges1", "int[][]"), ("edges2", "int[][]")], ret="int", cmp="exact",
    desc="<p>You have two separate undirected trees. The first has <code>edges1.length + 1</code> nodes numbered from <code>0</code>, the second has <code>edges2.length + 1</code> nodes, also numbered from <code>0</code>. Each list contains the edges <code>[a, b]</code> of its tree (an empty list means a tree with a single node).</p><p>You must add <em>exactly one</em> new edge that connects one node of the first tree with one node of the second tree, producing one big tree. You may choose the two endpoints freely. The diameter of a tree is the number of edges on its longest path. Return the smallest diameter the combined tree can have.</p><pre>edges1 = [[0,1],[0,2],[0,3]]        (a star, diameter 2)\nedges2 = [[0,1],[1,2],[2,3]]        (a path of 4 nodes, diameter 3)\n\njoin the star's center to a middle node of the path   -> 4</pre>",
    constraints=["0 &le; edges1.length, edges2.length &le; 100,000", "Both lists describe trees (connected, no cycles) on nodes numbered 0..edges.length", "The two trees use separate node numbering; nodes of the two trees never need to be compared"],
    hints=["Whatever you do, the new diameter is at least as large as the diameter of each tree on its own.",
           "A new longest path may cross the new edge: it goes from one tree to the other. It is shortest when the edge joins the two trees at their centers, because a center minimizes the farthest distance inside its tree.",
           "Let d1 and d2 be the two diameters. The farthest distance from a center of a tree with diameter d is <code>ceil(d / 2)</code>. The answer is <code>max(d1, d2, ceil(d1/2) + ceil(d2/2) + 1)</code>; find d1 and d2 with the two-BFS method."],
    editorial=["Let d1 and d2 be the diameters of the two trees. After joining, the old longest paths still exist, so the result is at least <code>max(d1, d2)</code>. In addition there are paths that cross the new edge <code>(a, b)</code>: the longest one has length <code>ecc1(a) + 1 + ecc2(b)</code>, where <code>ecc</code> is the farthest distance from a node to any node of its own tree.",
               "To minimize it choose <code>a</code> and <code>b</code> with the smallest eccentricity in their trees, namely the centers. The smallest eccentricity (the radius) of a tree with diameter d is <code>ceil(d / 2)</code>. So the best crossing path has length <code>ceil(d1/2) + ceil(d2/2) + 1</code>, and the final diameter is the maximum of this and the two original diameters.",
               "Computing d1 and d2 takes two BFS runs per tree, so O(n1 + n2) time and space overall. A single-node tree has diameter 0 and radius 0, which the formula handles without special cases."],
    time="O(n1 + n2)", space="O(n1 + n2)",
    solution='''def minDiameterAfterJoin(edges1, edges2):
    from collections import deque

    def diameter(edges):
        n = len(edges) + 1
        if n == 1:
            return 0
        adj = [[] for _ in range(n)]
        for a, b in edges:
            adj[a].append(b)
            adj[b].append(a)

        def far(s):
            dist = [-1] * n
            dist[s] = 0
            q = deque([s])
            last = s
            while q:
                u = q.popleft()
                last = u
                for v in adj[u]:
                    if dist[v] < 0:
                        dist[v] = dist[u] + 1
                        q.append(v)
            return last, dist[last]

        u, _ = far(0)
        return far(u)[1]

    d1, d2 = diameter(edges1), diameter(edges2)
    return max(d1, d2, (d1 + 1) // 2 + (d2 + 1) // 2 + 1)
''',
    tests=[[[[0, 1], [0, 2], [0, 3]], [[0, 1], [1, 2], [2, 3]]], [[], []], [[], [[0, 1]]], [[[0, 1]], [[0, 1]]], [[[0, 1], [1, 2]], []],
           [[[0, 1], [1, 2], [2, 3], [3, 4]], [[0, 1], [1, 2], [2, 3], [3, 4]]], [[[0, 1], [1, 2], [2, 3], [3, 4], [4, 5], [5, 6]], [[0, 1]]],
           [[[0, 1], [0, 2], [0, 3], [0, 4]], [[0, 1], [0, 2], [0, 3]]], [[[0, 1], [1, 2], [2, 3]], [[0, 1], [0, 2], [1, 3], [1, 4]]]],
)
_r = rnd(9710)
_P[-1]["tests"].append([_edges(_r, 1500, "chain"), _edges(_r, 1500, "rand")])
_P[-1]["tests"].append([_edges(_r, 1500, "deep"), _edges(_r, 1400, "broom")])
_P[-1]["tests"].append([_edges(_r, 1200, "star"), _edges(_r, 1800, "chain")])


def _diam_brute(n, edges):
    adj = _adjl(n, edges)
    return max(max(_dists(n, adj, s)) for s in range(n))


def b_join(edges1, edges2):
    n1, n2 = len(edges1) + 1, len(edges2) + 1
    best = None
    for a in range(n1):
        for b in range(n2):
            e = [list(x) for x in edges1] + [[x + n1, y + n1] for x, y in edges2] + [[a, b + n1]]
            d = _diam_brute(n1 + n2, e)
            if best is None or d < best:
                best = d
    return best


def g_join(r):
    n1, n2 = r.randint(1, 8), r.randint(1, 8)
    modes = ["rand", "chain", "star", "deep", "broom", "cater"]
    return [_edges(r, n1, r.choice(modes)), _edges(r, n2, r.choice(modes))]


def v_join(tests):
    for t in tests:
        for edges in t["args"]:
            assert len(edges) <= 100000
            _check_tree(len(edges) + 1, edges)
    # the answer is determined by the diameters only: make sure all three regimes occur
    assert len({t["expected"] for t in tests}) >= 6


CHECKS["minimum-diameter-after-joining-two-trees"] = (b_join, g_join, "exact")
VALIDATE["minimum-diameter-after-joining-two-trees"] = v_join

# ---------------------------------------------------------------- longest path with different adjacent letters
add(
    id="longest-path-different-adjacent-letters", title="Longest Path with Different Adjacent Letters", diff="Hard", topic="Graphs",
    fn="longestAlternatingPath", params=[("parent", "int[]"), ("s", "string")], ret="int", cmp="exact",
    desc="<p>A tree has <code>n</code> nodes numbered <code>0..n-1</code> and is rooted at node <code>0</code>. The array <code>parent</code> gives the parent of each node, with <code>parent[0] = -1</code>. Node <code>v</code> carries the letter <code>s[v]</code>.</p><p>Look at paths in the tree, in any direction (a path may go up and then down). A path is <em>valid</em> if no two <em>neighbouring</em> nodes on it carry the same letter. Return the largest number of nodes of a valid path. A single node is a valid path.</p><pre>parent = [-1, 0, 0, 1, 1, 1], s = \"abacbe\"\n\n3 - 1 - 5 uses letters c, b, e   (valid, 3 nodes)\n3 - 1 - 4 is invalid (b, b);  3 - 1 - 0 - 2 is invalid (a, a)   -> 3</pre>",
    constraints=["1 &le; n = parent.length = s.length &le; 100,000", "parent[0] = -1, and every other entry is a node number in 0..n-1 such that the whole array forms a tree rooted at 0 (a parent can have a larger number than its child)", "s consists of lowercase letters a-z"],
    hints=["Without the letter rule this is the tree diameter in nodes. Think about how the diameter DP changes when a chain cannot continue into a neighbour with the same letter.",
           "For each node v compute the longest valid chain going <em>down</em> from v. A child c may extend the chain of v only when <code>s[c] != s[v]</code>.",
           "At each node keep the two longest chains among its children with a different letter. The best path through v has <code>top1 + top2 + 1</code> nodes; the chain passed up to the parent is <code>top1 + 1</code>. Process nodes in reverse BFS order to avoid recursion."],
    editorial=["This is the tree diameter DP with a filter. Let <code>chain[v]</code> be the maximum number of nodes of a valid path that starts at v and only goes down. Then <code>chain[v] = 1 + max(chain[c])</code> over children c with <code>s[c] != s[v]</code> (just 1 if there is no such child).",
               "A valid path that has v as its highest node uses at most two child branches. Both branches must start at children with a letter different from <code>s[v]</code>; they may have equal letters with each other, because the two children are not neighbours on the path. So the best path with top node v has <code>1 + best1 + best2</code> nodes, where best1 and best2 are the two largest <code>chain[c]</code> among allowed children (missing branches count as 0). The answer is the maximum of this over all nodes.",
               "Build children lists, order nodes by BFS from the root, and process the order backwards so that children are done before parents. Each node updates its parent's two best values in O(1). The total time is O(n), space O(n)."],
    time="O(n)", space="O(n)",
    solution='''def longestAlternatingPath(parent, s):
    n = len(parent)
    children = [[] for _ in range(n)]
    for v in range(1, n):
        children[parent[v]].append(v)
    order = [0]
    for u in order:
        order.extend(children[u])
    b1 = [0] * n
    b2 = [0] * n
    best = 1
    for u in reversed(order):
        best = max(best, b1[u] + b2[u] + 1)
        p = parent[u]
        if p >= 0 and s[p] != s[u]:
            c = b1[u] + 1
            if c > b1[p]:
                b2[p] = b1[p]
                b1[p] = c
            elif c > b2[p]:
                b2[p] = c
    return best
''',
    tests=[[[-1, 0, 0, 1, 1, 1], "abacbe"], [[-1], "a"], [[-1, 0], "aa"], [[-1, 0], "ab"], [[-1, 0, 1, 2, 3], "ababa"], [[-1, 0, 1, 2, 3], "aaaaa"],
           [[-1, 0, 0, 0], "abbb"], [[-1, 0, 0, 0], "abcc"], [[-1, 0, 0, 1, 1, 2, 2], "abbcdcc"], [[-1, 0, 1, 1, 0, 4], "aabbbc"],
           [[-1, 0, 1, 0, 3, 2], "abaaba"]],
)
_r = rnd(9711)
_P[-1]["tests"].append([_parents(_r, 5000, "rand", True), "".join(_r.choice("abc") for _ in range(5000))])
_P[-1]["tests"].append([_parents(_r, 5000, "deep", True), "".join(_r.choice("ab") for _ in range(5000))])
_P[-1]["tests"].append([_parents(_r, 6000, "chain", True), "ab" * 3000])
_P[-1]["tests"].append([_parents(_r, 5000, "binary", True), "".join(_r.choice("abcdefghijklmnopqrstuvwxyz") for _ in range(5000))])


def b_alt(parent, s):
    n = len(parent)
    depth = [0] * n
    for v in range(n):
        d, u = 0, v
        while parent[u] != -1:
            u = parent[u]
            d += 1
        depth[v] = d
    best = 1
    for a in range(n):
        for b in range(a, n):
            up_a, up_b = [a], [b]  # climb to the lowest common ancestor, collecting the nodes
            x, y = a, b
            while depth[x] > depth[y]:
                x = parent[x]
                up_a.append(x)
            while depth[y] > depth[x]:
                y = parent[y]
                up_b.append(y)
            while x != y:
                x, y = parent[x], parent[y]
                up_a.append(x)
                up_b.append(y)
            path = up_a + up_b[:-1][::-1]
            if all(s[path[i]] != s[path[i + 1]] for i in range(len(path) - 1)):
                best = max(best, len(path))
    return best


def g_alt(r):
    n = r.randint(1, 10)
    alpha = "abcdefghijklmnopqrstuvwxyz"[:r.randint(1, 3)]
    return [_parents(r, n, r.choice(["rand", "chain", "star", "deep", "binary", "cater"]), True), "".join(r.choice(alpha) for _ in range(n))]


def v_alt(tests):
    for t in tests:
        parent, s = t["args"]
        assert 1 <= len(parent) <= 100000 and len(s) == len(parent)
        _check_parents(parent, root=0)
        assert all("a" <= ch <= "z" for ch in s)
        assert 1 <= t["expected"] <= len(parent)


CHECKS["longest-path-different-adjacent-letters"] = (b_alt, g_alt, "exact")
VALIDATE["longest-path-different-adjacent-letters"] = v_alt
