"""Problems: trees, ancestors / LCA / distances (level-order array encoding, -1 for a missing child). See data/lib.py for the registry."""
from collections import deque

from lib import add, rnd, CHECKS, VALIDATE, gen_arr  # noqa: F401
from lib import P as _P  # noqa: F401

MAXN = 1500      # maximum number of nodes in most problems
MAXV = 10000     # maximum node value

# ------------------------------------------------------------------ shared statement text
ENC = (
    "<p><strong>How trees are given.</strong> There is no tree type here. A binary tree is passed as an integer array in "
    "<em>level-order</em> (top to bottom, left to right). A missing child is written as "
    "<code>-1</code>, and every real node value is non-negative. The children of a missing node are not listed, and trailing "
    "<code>-1</code> entries are dropped, so a non-empty array never ends with <code>-1</code>. The empty tree is <code>[]</code>.</p>"
    "<p>For example, <code>[1, 2, 3, -1, 4]</code> describes the tree on the left: the root is 1 with children 2 and 3, node 2 has no left "
    "child and has 4 as its right child, and node 3 is a leaf.</p>"
    "<pre>    1\n   / \\\n  2   3\n   \\\n    4</pre>"
)

CLASSIC = "<pre>        3\n      /   \\\n     5     1\n    / \\   / \\\n   6   2 0   8\n      / \\\n     7   4</pre>"


def _cons(lo=0, hi=MAXN, extra=None, distinct=True):
    out = [f"{lo} &le; number of nodes &le; {hi:,}", f"0 &le; node value &le; {MAXV:,}"]
    if distinct:
        out.append("All node values are distinct, so a value identifies exactly one node")
    out.append("The array follows the encoding above exactly (valid level-order, no trailing -1)")
    return out + (extra or [])


# ------------------------------------------------------------------ helpers (parsing, building, shapes)
class _N:
    __slots__ = ("v", "l", "r")

    def __init__(self, v):
        self.v = v
        self.l = None
        self.r = None


def _build(arr):
    if not arr:
        return None
    root = _N(arr[0])
    q = deque([root])
    i = 1
    while q and i < len(arr):
        x = q.popleft()
        for side in (0, 1):
            if i < len(arr):
                v = arr[i]
                i += 1
                if v != -1:
                    c = _N(v)
                    if side == 0:
                        x.l = c
                    else:
                        x.r = c
                    q.append(c)
    assert i == len(arr), "encoding has entries below missing nodes"
    return root


def _encode(root):
    if root is None:
        return []
    out = []
    q = deque([root])
    while q:
        x = q.popleft()
        if x is None:
            out.append(-1)
            continue
        out.append(x.v)
        q.append(x.l)
        q.append(x.r)
    while out and out[-1] == -1:
        out.pop()
    return out


def _preorder(root):
    out, st = [], ([root] if root else [])
    while st:
        x = st.pop()
        out.append(x)
        if x.r:
            st.append(x.r)
        if x.l:
            st.append(x.l)
    return out


def _shape(r, n, mode="random"):
    if n == 0:
        return None
    root = _N(0)
    if mode in ("left", "right", "zig"):
        cur = root
        for i in range(n - 1):
            c = _N(0)
            side = 0 if mode == "left" else 1 if mode == "right" else i % 2
            if side == 0:
                cur.l = c
            else:
                cur.r = c
            cur = c
        return root
    free = [(root, 0), (root, 1)]
    head = 0
    for _ in range(n - 1):
        if mode == "complete":
            node, side = free[head]
            head += 1
        else:
            lo = max(0, len(free) - 3) if mode == "deep" else 0
            i = r.randrange(lo, len(free))
            free[i], free[-1] = free[-1], free[i]
            node, side = free.pop()
        c = _N(0)
        if side == 0:
            node.l = c
        else:
            node.r = c
        free.append((c, 0))
        free.append((c, 1))
    return root


MODES = ["random", "random", "deep", "complete", "left", "right", "zig"]


def _tree(r, n, mode="random", lo=0, hi=MAXV):
    """Tree with arbitrary (repeating) values."""
    root = _shape(r, n, mode)
    for x in _preorder(root):
        x.v = r.randint(lo, hi)
    return _encode(root)


def _utree(r, n, mode="random", vmax=MAXV):
    """Tree with pairwise distinct values."""
    root = _shape(r, n, mode)
    for x, v in zip(_preorder(root), r.sample(range(0, vmax + 1), n)):
        x.v = v
    return _encode(root)


def _vals(arr):
    return [x for x in arr if x != -1]


def _v_tree(arr, lo=0, hi=MAXN, distinct=True):
    assert isinstance(arr, list) and all(isinstance(x, int) for x in arr)
    assert arr == _encode(_build(arr)), ("not a canonical level-order encoding", arr[:12])
    nodes = _vals(arr)
    assert lo <= len(nodes) <= hi, ("node count", len(nodes))
    assert all(0 <= x <= MAXV for x in nodes), "node value out of range"
    if distinct:
        assert len(set(nodes)) == len(nodes), "values must be distinct"
    assert not arr or arr[0] != -1


def _paths(root):
    """value -> list of values on the root-to-node path (inclusive). Iterative; for brute forces on small trees."""
    out = {}
    st = [(root, [root.v])] if root else []
    while st:
        x, p = st.pop()
        out[x.v] = p
        if x.l:
            st.append((x.l, p + [x.l.v]))
        if x.r:
            st.append((x.r, p + [x.r.v]))
    return out


def _common(pa, pb):
    c = 0
    while c < len(pa) and c < len(pb) and pa[c] == pb[c]:
        c += 1
    return c  # number of shared path entries


def _small(nmin=1, nmax=10, vmax=40, modes=MODES):
    def g(r):
        return _utree(r, r.randint(nmin, nmax), r.choice(modes), vmax)
    return g


# Parsing used inside the reference solutions. The k-th real node (0-based, level order) owns array
# slots 2k+1 and 2k+2 as its children, because every real node contributes exactly two child slots.
LINKS = '''def _links(t):
    """vals[k], left[k], right[k] for the k-th real node in level order (-1 = no child)."""
    pos, c = [], 0
    for x in t:
        if x == -1:
            pos.append(-1)
        else:
            pos.append(c)
            c += 1
    vals = [x for x in t if x != -1]
    left, right = [-1] * c, [-1] * c
    for k in range(c):
        a = 2 * k + 1
        if a < len(t):
            left[k] = pos[a]
        if a + 1 < len(t):
            right[k] = pos[a + 1]
    return vals, left, right


def _info(t):
    """Adds parent[k] (-1 for the root) and depth[k]. Parents come before children in level order."""
    vals, left, right = _links(t)
    n = len(vals)
    par = [-1] * n
    depth = [0] * n
    for k in range(n):
        for c in (left[k], right[k]):
            if c != -1:
                par[c] = k
                depth[c] = depth[k] + 1
    return vals, left, right, par, depth


'''

CLASSIC_T = [3, 5, 1, 6, 2, 0, 8, -1, -1, 7, 4]
BASE = [
    [0], [1, 2, 3], [1, -1, 2, -1, 3], [1, 2, -1, 3, -1, 4], [1, 2, 3, -1, 4, -1, 5], CLASSIC_T,
    [1, 2, 3, 4, 5, 6, 7], [7, 3, 9, 1, 5, 8, 2, 0, 4, 6],
]

BIG_MODES = ["left", "right", "zig", "complete", "random", "deep"]


def _pick(r, arr, k):
    return r.sample(_vals(arr), k)


# ================================================================== EASY

# ---------------------------------------------------------------- cousins
add(
    id="binary-tree-cousin-nodes", title="Are These Two Nodes Cousins?", diff="Easy", topic="Trees",
    fn="areCousins", params=[("tree", "int[]"), ("x", "int"), ("y", "int")], ret="bool", cmp="exact",
    desc="<p>Two nodes of a binary tree are <em>cousins</em> when they are on the same depth (the root has depth <code>0</code>) but have <em>different</em> parents. Siblings (same parent) are not cousins.</p>"
         "<p>Given the tree and two different values <code>x</code> and <code>y</code>, both of which occur in the tree, return <code>true</code> if the nodes holding them are cousins, otherwise <code>false</code>.</p>" + ENC +
         "<p>For <code>tree = [1, 2, 3, -1, 4, -1, 5]</code>, nodes 4 and 5 are cousins (both on depth 2, parents 2 and 3), so <code>x = 4, y = 5</code> gives <code>true</code>. Nodes 2 and 3 are siblings, so <code>x = 2, y = 3</code> gives <code>false</code>.</p>",
    constraints=_cons(2, MAXN, ["<code>x != y</code>, and both values occur in the tree"]),
    hints=["Two facts decide the answer for each of the two nodes: how deep it is and who its parent is.",
           "Because values are distinct, you can store, for every value, a pair <code>(depth, parent value)</code> while walking the tree.",
           "With the array encoding, the k-th real node owns the child slots <code>2k+1</code> and <code>2k+2</code>. One left-to-right pass can therefore record depth and parent of every node; the answer is <code>depth[x] == depth[y] and parent[x] != parent[y]</code>."],
    editorial=["Walk the tree once (level by level, or recursively) and remember for each node its depth and its parent. Then compare: equal depth and different parent means cousins. A breadth-first search can also stop as soon as it finishes the level on which one of the two values is found: if the other is on that same level with a different parent the answer is true, otherwise false.",
               "Every node is visited once, so the time is linear. The array encoding lets you do it without building node objects: real nodes come in level order, and the children of the k-th real node sit at slots <code>2k+1</code> and <code>2k+2</code> of the array."],
    time="O(n)", space="O(n)",
    solution=LINKS + '''def areCousins(tree, x, y):
    vals, left, right, par, depth = _info(tree)
    a = vals.index(x)
    b = vals.index(y)
    return depth[a] == depth[b] and par[a] != par[b]
''',
    tests=[[t, *xy] for t, xy in [
        ([1, 2, 3, -1, 4, -1, 5], (4, 5)), ([1, 2, 3, -1, 4, -1, 5], (2, 3)), ([1, 2, 3, 4], (4, 3)),
        ([1, 2, 3, 4, 5], (4, 5)), ([1, 2, 3, 4, 5, 6, 7], (4, 7)), ([1, 2, 3, 4, 5, 6, 7], (5, 6)),
        ([1, 2], (1, 2)), ([1, 2, 3, 4, 5, 6, 7], (1, 6)), (CLASSIC_T, (6, 0)), (CLASSIC_T, (7, 8)),
        (CLASSIC_T, (7, 4)), ([1, 2, -1, 3, -1, 4], (3, 4)),
    ]],
)
_ps = _P[-1]
_r = rnd(9101)


def _info_small(arr):
    root = _build(arr)
    out = {}
    st = [(root, None, 0)]
    while st:
        x, p, d = st.pop()
        out[x.v] = (p, d)
        for c in (x.l, x.r):
            if c:
                st.append((c, x.v, d + 1))
    return out


def _cousin_pair(r, arr, want):
    inf = _info_small(arr)
    vs = list(inf)
    for _ in range(4000):
        a, b = r.sample(vs, 2)
        ok = inf[a][1] == inf[b][1] and inf[a][0] != inf[b][0]
        if ok == want:
            return [a, b]
    return r.sample(vs, 2)


for _n, _m, _w in [(1500, "complete", True), (1500, "random", True), (1500, "left", False), (1400, "deep", False),
                   (1500, "random", False), (1000, "complete", True)]:
    _a = _utree(_r, _n, _m)
    _ps["tests"].append([_a, *_cousin_pair(_r, _a, _w)])


def _b_cousins(tree, x, y):
    root = _build(tree)
    info = {}

    def go(node, parent, d):
        if node is None:
            return
        info[node.v] = (parent, d)
        go(node.l, node.v, d + 1)
        go(node.r, node.v, d + 1)
    go(root, None, 0)
    return info[x][1] == info[y][1] and info[x][0] != info[y][0]


def _g_cousins(r):
    arr = _utree(r, r.randint(2, 10), r.choice(MODES), 30)
    return [arr, *_cousin_pair(r, arr, r.random() < 0.5)]


def _v_cousins(tests):
    for t in tests:
        arr, x, y = t["args"]
        _v_tree(arr, 2)
        assert x != y and x in arr and y in arr


CHECKS["binary-tree-cousin-nodes"] = (_b_cousins, _g_cousins, "exact")
VALIDATE["binary-tree-cousin-nodes"] = _v_cousins

# ---------------------------------------------------------------- ancestors of a value
add(
    id="ancestors-of-tree-value", title="Ancestors of a Node", diff="Easy", topic="Trees",
    fn="ancestorsOf", params=[("tree", "int[]"), ("target", "int")], ret="int[]", cmp="exact",
    desc="<p>An <em>ancestor</em> of a node is any node on the path from the root down to its parent. Given a binary tree and a value <code>target</code> that occurs in it, return the values of all ancestors of the node holding <code>target</code>, ordered from the <strong>closest one (its parent) up to the root</strong>.</p>"
         "<p>The root has no ancestors, so for the root the answer is the empty array <code>[]</code>.</p>" + ENC +
         "<p>For the tree below (<code>[3, 5, 1, 6, 2, 0, 8, -1, -1, 7, 4]</code>) and <code>target = 7</code> the answer is <code>[2, 5, 3]</code>.</p>" + CLASSIC,
    constraints=_cons(1, MAXN, ["<code>target</code> occurs in the tree"]),
    hints=["The ancestors of a node are exactly the nodes you pass on the way from the root to it. How can you remember that way?",
           "Store, for every node, who its parent is. Then starting from the target you can follow parents until you reach the root.",
           "Level order puts every parent before its children. For the k-th real node, its children are at array slots <code>2k+1</code> and <code>2k+2</code>, so a single pass fills a <code>parent</code> array. Walk up from the target and collect the values."],
    editorial=["Record the parent of every node once, then climb. The climb from the target to the root visits at most depth(target) nodes, which is exactly the answer. The parent array can be filled in one linear pass over the level-order array because each real node accounts for exactly two child slots.",
               "A recursive search that returns <code>true</code> when the target is found in its subtree and appends the current node on the way back out produces the same list. It is just as fast but uses recursion depth up to n on skewed trees."],
    time="O(n)", space="O(n)",
    solution=LINKS + '''def ancestorsOf(tree, target):
    vals, left, right, par, depth = _info(tree)
    k = vals.index(target)
    out = []
    k = par[k]
    while k != -1:
        out.append(vals[k])
        k = par[k]
    return out
''',
    tests=[[t, v] for t, v in [
        (CLASSIC_T, 7), (CLASSIC_T, 3), (CLASSIC_T, 8), ([0], 0), ([1, 2, 3], 3), ([1, -1, 2, -1, 3], 3),
        ([1, 2, -1, 3, -1, 4], 4), ([1, 2, 3, 4, 5, 6, 7], 6), ([7, 3, 9, 1, 5, 8, 2, 0, 4, 6], 6), ([5, 1], 1),
    ]],
)
_ps = _P[-1]
_r = rnd(9102)
for _n, _m in [(1500, "left"), (1500, "zig"), (1500, "random"), (1200, "complete")]:
    _a = _utree(_r, _n, _m)
    _ps["tests"].append([_a, _r.choice(_vals(_a)[len(_vals(_a)) // 2:])])


def _b_anc(tree, target):
    p = _paths(_build(tree))[target]
    return p[:-1][::-1]


CHECKS["ancestors-of-tree-value"] = (_b_anc, lambda r: (lambda a: [a, r.choice(_vals(a))])(_small()(r)), "exact")


def _v_anc(tests):
    for t in tests:
        _v_tree(t["args"][0], 1)
        assert t["args"][1] in t["args"][0]


VALIDATE["ancestors-of-tree-value"] = _v_anc

# ---------------------------------------------------------------- subtree sums by value
add(
    id="subtree-sum-by-value-queries", title="Subtree Sum Queries", diff="Easy", topic="Trees",
    fn="subtreeSums", params=[("tree", "int[]"), ("queries", "int[]")], ret="int[]", cmp="exact",
    desc="<p>The <em>subtree sum</em> of a node is the sum of the values of that node and of all its descendants.</p>"
         "<p>Given a binary tree and an array <code>queries</code> of node values (each of which occurs in the tree), return an array <code>ans</code> where <code>ans[i]</code> is the subtree sum of the node whose value is <code>queries[i]</code>.</p>" + ENC +
         "<p>For the tree below (<code>[3, 5, 1, 6, 2, 0, 8, -1, -1, 7, 4]</code>) and <code>queries = [5, 3, 6]</code> the answer is <code>[24, 36, 6]</code>: node 5 owns 5 + 6 + 2 + 7 + 4 = 24, the root owns everything.</p>" + CLASSIC,
    constraints=_cons(1, MAXN, ["1 &le; queries.length &le; 1,500", "Every query value occurs in the tree; the same value may be queried more than once"]),
    hints=["Answering each query with its own traversal works, but can you compute all subtree sums together?",
           "A node's subtree sum is its own value plus the subtree sums of its two children.",
           "In level order, children always come after their parents. Walk the real nodes from last to first and add each node's total to its parent's total. Store totals in a dictionary from value to sum and answer the queries from it."],
    editorial=["Compute the subtree sum of every node once, bottom-up: <code>sum(node) = value + sum(left) + sum(right)</code>. Processing the nodes in reverse level order guarantees that both children are finished before their parent, so no recursion is needed. Then each query is a dictionary lookup (values are distinct, so a value names one node).",
               "Total time is O(n + q). The sums are at most 1,500 &times; 10,000, which fits comfortably in a 32-bit integer."],
    time="O(n + q)", space="O(n)",
    solution=LINKS + '''def subtreeSums(tree, queries):
    vals, left, right = _links(tree)
    n = len(vals)
    total = vals[:]
    for k in range(n - 1, -1, -1):
        if left[k] != -1:
            total[k] += total[left[k]]
        if right[k] != -1:
            total[k] += total[right[k]]
    where = {v: k for k, v in enumerate(vals)}
    return [total[where[q]] for q in queries]
''',
    tests=[[t, q] for t, q in [
        (CLASSIC_T, [5, 3, 6]), ([0], [0]), ([1, 2, 3], [1, 2, 3]), ([1, -1, 2, -1, 3], [1, 2, 3, 2]),
        ([4, 1, -1, 7, 9], [4, 7, 9, 1]), ([10000, 9999, 9998], [10000, 9999]), ([1, 2, 3, 4, 5, 6, 7], [2, 3, 7, 1]),
        ([7, 3, 9, 1, 5, 8, 2, 0, 4, 6], [3, 5, 8, 9, 7]),
    ]],
)
_ps = _P[-1]
_r = rnd(9103)
for _n, _m in [(1500, "random"), (1500, "left"), (1500, "complete"), (1500, "zig")]:
    _a = _utree(_r, _n, _m)
    _ps["tests"].append([_a, [_r.choice(_vals(_a)) for _ in range(1500)]])
_ps["tests"].append([[0], [0] * 1500])


def _b_subsum(tree, queries):
    root = _build(tree)

    def s(x):
        return 0 if x is None else x.v + s(x.l) + s(x.r)
    nodes = {x.v: x for x in _preorder(root)}
    return [s(nodes[q]) for q in queries]


def _g_subsum(r):
    a = _small()(r)
    return [a, [r.choice(_vals(a)) for _ in range(r.randint(1, 6))]]


def _v_subsum(tests):
    for t in tests:
        _v_tree(t["args"][0], 1)
        qs = t["args"][1]
        assert 1 <= len(qs) <= 1500 and all(q in t["args"][0] for q in qs)


CHECKS["subtree-sum-by-value-queries"] = (_b_subsum, _g_subsum, "exact")
VALIDATE["subtree-sum-by-value-queries"] = _v_subsum

# ================================================================== MEDIUM

# ---------------------------------------------------------------- LCA
add(
    id="lowest-common-ancestor-binary-tree", title="Lowest Common Ancestor of a Binary Tree", diff="Medium", topic="Trees", tier="must",
    fn="lowestCommonAncestor", params=[("tree", "int[]"), ("p", "int"), ("q", "int")], ret="int", cmp="exact",
    desc="<p>The <em>lowest common ancestor</em> (LCA) of two nodes <code>p</code> and <code>q</code> in a binary tree is the deepest node that has both of them in its subtree. A node counts as part of its own subtree, so if <code>p</code> is an ancestor of <code>q</code> then the LCA is <code>p</code> itself.</p>"
         "<p>Given the tree and the values <code>p</code> and <code>q</code> (both occur in the tree; they may be equal), return the <em>value</em> of their lowest common ancestor.</p>" + ENC +
         "<p>For the tree below (<code>[3, 5, 1, 6, 2, 0, 8, -1, -1, 7, 4]</code>): <code>p = 5, q = 1</code> gives <code>3</code>, and <code>p = 5, q = 4</code> gives <code>5</code>.</p>" + CLASSIC,
    constraints=_cons(1, MAXN, ["<code>p</code> and <code>q</code> occur in the tree (possibly <code>p == q</code>)"]),
    hints=["Think of the path from the root to each of the two nodes. Where do the two paths split?",
           "If you know the depth and the parent of every node, you can move the deeper node up until both are on the same depth.",
           "After equalising depths, move both nodes up one parent at a time until they are the same node. That node is the LCA. With level order, parents come before children, so depth and parent arrays take a single pass to fill."],
    editorial=["Compute parent and depth of every node. To find the LCA of <code>a</code> and <code>b</code>, lift the deeper node until the depths are equal, then lift both together until they meet. This is O(n) to prepare and O(depth) per query.",
               "The classic recursive solution does the same without extra arrays: <code>lca(node)</code> returns the node if it is <code>p</code> or <code>q</code>; otherwise it asks both subtrees, and if both return something, the current node is the split point. If only one side returns something, pass that result up. Either way each node is looked at once."],
    time="O(n)", space="O(n)",
    solution=LINKS + '''def lowestCommonAncestor(tree, p, q):
    vals, left, right, par, depth = _info(tree)
    a = vals.index(p)
    b = vals.index(q)
    while depth[a] > depth[b]:
        a = par[a]
    while depth[b] > depth[a]:
        b = par[b]
    while a != b:
        a = par[a]
        b = par[b]
    return vals[a]
''',
    tests=[[t, p, q] for t, p, q in [
        (CLASSIC_T, 5, 1), (CLASSIC_T, 5, 4), (CLASSIC_T, 7, 4), (CLASSIC_T, 6, 8), (CLASSIC_T, 3, 3), ([0], 0, 0),
        ([1, 2], 2, 1), ([1, -1, 2, -1, 3], 3, 2), ([1, 2, 3, 4, 5, 6, 7], 4, 5), ([1, 2, 3, 4, 5, 6, 7], 4, 7),
        ([7, 3, 9, 1, 5, 8, 2, 0, 4, 6], 6, 8),
    ]],
)
_ps = _P[-1]
_r = rnd(9104)
for _n, _m in [(1500, "left"), (1500, "zig"), (1500, "random"), (1500, "deep")]:
    _a = _utree(_r, _n, _m)
    _vv = _vals(_a)
    _ps["tests"].append([_a, _vv[-1], _vv[-2] if _m != "left" else _vv[len(_vv) // 2]])


def _b_lca(tree, p, q):
    ps = _paths(_build(tree))
    a, b = ps[p], ps[q]
    return a[_common(a, b) - 1]


CHECKS["lowest-common-ancestor-binary-tree"] = (
    _b_lca, lambda r: (lambda a: [a, r.choice(_vals(a)), r.choice(_vals(a))])(_small()(r)), "exact")


def _v_lca(tests):
    for t in tests:
        _v_tree(t["args"][0], 1)
        assert t["args"][1] in t["args"][0] and t["args"][2] in t["args"][0]


VALIDATE["lowest-common-ancestor-binary-tree"] = _v_lca

# ---------------------------------------------------------------- nodes at distance K
add(
    id="nodes-at-distance-k-from-target", title="Nodes at Distance K from a Target", diff="Medium", topic="Trees", tier="must",
    fn="distanceK", params=[("tree", "int[]"), ("target", "int"), ("k", "int")], ret="int[]", cmp="flat",
    desc="<p>The distance between two nodes of a tree is the number of edges on the path connecting them; the path may go <em>up</em> towards the root and then <em>down</em> again.</p>"
         "<p>Given a binary tree, the value <code>target</code> of one of its nodes and an integer <code>k</code>, return the values of all nodes whose distance from the target node is exactly <code>k</code>. The values may be returned in any order; if there is no such node, return an empty array.</p>" + ENC +
         "<p>For the tree below (<code>[3, 5, 1, 6, 2, 0, 8, -1, -1, 7, 4]</code>) with <code>target = 5</code>: <code>k = 2</code> gives <code>[1, 4, 7]</code> (any order) and <code>k = 3</code> gives <code>[0, 8]</code>.</p>" + CLASSIC,
    constraints=_cons(1, MAXN, ["<code>target</code> occurs in the tree", "0 &le; k &le; 2,000"]),
    hints=["Going down from the target is easy. The hard part is nodes reached by first going up to an ancestor.",
           "A tree is a graph in which every edge can be walked in both directions. If every node knew its parent, you could treat the tree as an undirected graph.",
           "Record each node's parent, then run a breadth-first search from the target over the three neighbours (left, right, parent), tracking a visited set. The nodes found at BFS level exactly <code>k</code> are the answer."],
    editorial=["Add the missing 'up' edges: one pass over the array gives the parent of every node. Now every node has up to three neighbours and a breadth-first search from the target visits nodes in increasing order of distance. Stop after level <code>k</code> and report the nodes of that level. A visited set (or remembering the node we came from) prevents going back.",
               "Time and space are O(n). An alternative is a recursive method that returns the distance from the current node to the target and, on the way back, collects nodes at the remaining distance in the sibling subtree; it needs no parent pointers but is easier to get wrong."],
    time="O(n)", space="O(n)",
    solution=LINKS + '''def distanceK(tree, target, k):
    vals, left, right, par, depth = _info(tree)
    n = len(vals)
    start = vals.index(target)
    dist = [-1] * n
    dist[start] = 0
    frontier = [start]
    d = 0
    while frontier and d < k:
        nxt = []
        for x in frontier:
            for y in (left[x], right[x], par[x]):
                if y != -1 and dist[y] == -1:
                    dist[y] = d + 1
                    nxt.append(y)
        frontier = nxt
        d += 1
    if d < k:
        return []
    return sorted(vals[x] for x in frontier)
''',
    tests=[[t, v, k] for t, v, k in [
        (CLASSIC_T, 5, 2), (CLASSIC_T, 5, 3), (CLASSIC_T, 5, 0), (CLASSIC_T, 5, 1), (CLASSIC_T, 5, 9), (CLASSIC_T, 7, 4),
        ([0], 0, 0), ([0], 0, 1), ([1, 2, 3, 4, 5, 6, 7], 2, 3), ([1, 2, 3, 4, 5, 6, 7], 1, 2),
        ([1, -1, 2, -1, 3, -1, 4], 3, 2),
    ]],
)
_ps = _P[-1]
_r = rnd(9105)
for _n, _m, _k in [(1500, "complete", 7), (1500, "random", 6), (1500, "zig", 300), (1500, "deep", 40)]:
    _a = _utree(_r, _n, _m)
    _ps["tests"].append([_a, _r.choice(_vals(_a)), _k])


def _b_distk(tree, target, k):
    ps = _paths(_build(tree))
    pt = ps[target]
    out = []
    for v, pv in ps.items():
        c = _common(pt, pv)
        if (len(pt) - c) + (len(pv) - c) == k:
            out.append(v)
    return out


def _g_distk(r):
    a = _small()(r)
    return [a, r.choice(_vals(a)), r.randint(0, 6)]


def _v_distk(tests):
    for t in tests:
        _v_tree(t["args"][0], 1)
        assert t["args"][1] in t["args"][0] and 0 <= t["args"][2] <= 2000


CHECKS["nodes-at-distance-k-from-target"] = (_b_distk, _g_distk, "flat")
VALIDATE["nodes-at-distance-k-from-target"] = _v_distk

# ---------------------------------------------------------------- distance between two nodes
add(
    id="distance-between-two-tree-values", title="Distance Between Two Nodes", diff="Medium", topic="Trees",
    fn="nodeDistance", params=[("tree", "int[]"), ("a", "int"), ("b", "int")], ret="int", cmp="exact",
    desc="<p>The distance between two nodes of a binary tree is the number of edges on the unique path that connects them (the path may climb up to a common ancestor and then descend).</p>"
         "<p>Given the tree and two values <code>a</code> and <code>b</code> that occur in it (they may be equal), return the distance between the nodes holding them. The distance of a node to itself is <code>0</code>.</p>" + ENC +
         "<p>For the tree below (<code>[3, 5, 1, 6, 2, 0, 8, -1, -1, 7, 4]</code>): <code>a = 7, b = 8</code> gives <code>5</code> (7 &rarr; 2 &rarr; 5 &rarr; 3 &rarr; 1 &rarr; 8), and <code>a = 5, b = 4</code> gives <code>2</code>.</p>" + CLASSIC,
    constraints=_cons(1, MAXN, ["<code>a</code> and <code>b</code> occur in the tree"]),
    hints=["Any path between two nodes goes up to some node and then down. Which node is that turning point?",
           "The turning point is the lowest common ancestor of the two nodes.",
           "If <code>l</code> is the LCA, then <code>dist(a, b) = depth(a) + depth(b) - 2 * depth(l)</code>. Find the LCA by lifting the deeper node and then both nodes, counting the steps as you go."],
    editorial=["Let <code>l</code> be the lowest common ancestor. The path from <code>a</code> to <code>b</code> is the path from <code>a</code> up to <code>l</code> followed by the path from <code>l</code> down to <code>b</code>, so its length is <code>depth(a) - depth(l) + depth(b) - depth(l)</code>.",
               "You do not need the LCA explicitly: lift the deeper node until the depths are equal (count each step), then lift both nodes together until they are the same node (count two steps each time). One pass fills the depth and parent arrays, so the whole solution is O(n)."],
    time="O(n)", space="O(n)",
    solution=LINKS + '''def nodeDistance(tree, a, b):
    vals, left, right, par, depth = _info(tree)
    x = vals.index(a)
    y = vals.index(b)
    steps = 0
    while depth[x] > depth[y]:
        x = par[x]
        steps += 1
    while depth[y] > depth[x]:
        y = par[y]
        steps += 1
    while x != y:
        x = par[x]
        y = par[y]
        steps += 2
    return steps
''',
    tests=[[t, a, b] for t, a, b in [
        (CLASSIC_T, 7, 8), (CLASSIC_T, 5, 4), (CLASSIC_T, 6, 6), (CLASSIC_T, 3, 7), (CLASSIC_T, 0, 8), ([0], 0, 0),
        ([1, 2], 1, 2), ([1, -1, 2, -1, 3, -1, 4], 1, 4), ([1, 2, 3, 4, 5, 6, 7], 4, 7), ([1, 2, 3, 4, 5, 6, 7], 4, 5),
    ]],
)
_ps = _P[-1]
_r = rnd(9106)
for _n, _m in [(1500, "left"), (1500, "zig"), (1500, "random"), (1500, "complete")]:
    _a = _utree(_r, _n, _m)
    _vv = _vals(_a)
    _ps["tests"].append([_a, _vv[-1], _vv[1] if _m != "left" else _vv[len(_vv) // 3]])


def _b_dist(tree, a, b):
    ps = _paths(_build(tree))
    pa, pb = ps[a], ps[b]
    c = _common(pa, pb)
    return len(pa) + len(pb) - 2 * c


CHECKS["distance-between-two-tree-values"] = (
    _b_dist, lambda r: (lambda a: [a, r.choice(_vals(a)), r.choice(_vals(a))])(_small()(r)), "exact")
VALIDATE["distance-between-two-tree-values"] = _v_lca

# ---------------------------------------------------------------- LCA of deepest leaves
add(
    id="lca-of-deepest-leaves", title="Smallest Subtree Holding All Deepest Nodes", diff="Medium", topic="Trees",
    fn="deepestLeavesLCA", params=[("tree", "int[]")], ret="int", cmp="exact",
    desc="<p>The <em>deepest nodes</em> of a non-empty binary tree are the nodes whose depth (root = <code>0</code>) is the largest in the tree; there can be several of them.</p>"
         "<p>Among all nodes whose subtree contains <em>every</em> deepest node, find the one with the smallest subtree (equivalently, the deepest such node), and return its value. This is the lowest common ancestor of all the deepest nodes. If there is a single deepest node, it is its own answer.</p>" + ENC +
         "<p>For the tree below (<code>[3, 5, 1, 6, 2, 0, 8, -1, -1, 7, 4]</code>) the deepest nodes are 7 and 4, and the answer is <code>2</code>. For <code>[1, 2, 3, 4]</code> the only deepest node is 4, so the answer is <code>4</code>. For <code>[1, 2, 3]</code> the answer is <code>1</code>.</p>" + CLASSIC,
    constraints=_cons(1, MAXN),
    hints=["First work out what 'deepest' means for this tree: compute the depth of every node.",
           "For each node, ask: how deep is the deepest node in its left subtree, and in its right subtree?",
           "Process the nodes bottom-up and keep for every node the pair (deepest depth below it, best answer below it). If both children reach the same deepest depth, the current node is the split point; otherwise take the answer of the deeper side. A leaf answers with itself."],
    editorial=["Define for every node two things: <code>md</code>, the largest depth inside its subtree, and <code>res</code>, the lowest node whose subtree contains all the nodes of maximal depth inside this subtree. A leaf has <code>md = depth</code> and <code>res = itself</code>. For an inner node compare the <code>md</code> of its children: if they are equal, the deepest nodes are spread over both sides and the node itself is the answer; if one side is deeper, all deepest nodes live there, so copy that child's <code>res</code> and <code>md</code>. A missing child counts as depth -1.",
               "Evaluating nodes from the last to the first in level order handles children before parents without recursion. The answer is <code>res</code> of the root. Time and space are O(n)."],
    time="O(n)", space="O(n)",
    solution=LINKS + '''def deepestLeavesLCA(tree):
    vals, left, right, par, depth = _info(tree)
    n = len(vals)
    md = [0] * n
    res = [0] * n
    for k in range(n - 1, -1, -1):
        l, r = left[k], right[k]
        a = md[l] if l != -1 else -1
        b = md[r] if r != -1 else -1
        if l == -1 and r == -1:
            md[k] = depth[k]
            res[k] = k
        elif a == b:
            md[k] = a
            res[k] = k
        elif a > b:
            md[k] = a
            res[k] = res[l]
        else:
            md[k] = b
            res[k] = res[r]
    return vals[res[0]]
''',
    tests=[[t] for t in [
        CLASSIC_T, [1, 2, 3, 4], [1, 2, 3], [0], [1, 2], [1, 2, 3, 4, 5, 6, 7], [1, 2, 3, 4, 5, 6], [1, -1, 2, -1, 3],
        [7, 3, 9, 1, 5, 8, 2, 0, 4, 6], [1, 2, 3, -1, 4, -1, 5, -1, -1, 6, 7],
    ]],
)
_ps = _P[-1]
_r = rnd(9107)
for _n, _m in [(1500, "left"), (1500, "complete"), (1500, "random"), (1500, "deep"), (1024, "complete")]:
    _ps["tests"].append([_utree(_r, _n, _m)])


def _b_deep(tree):
    root = _build(tree)
    ps = _paths(root)
    md = max(len(p) for p in ps.values())
    deepest = [p for p in ps.values() if len(p) == md]
    best = None
    for v, p in ps.items():
        if all(len(d) >= len(p) and d[:len(p)] == p for d in deepest):
            if best is None or len(p) > len(ps[best]):
                best = v
    return best


def _v_deep(tests):
    for t in tests:
        _v_tree(t["args"][0], 1)


CHECKS["lca-of-deepest-leaves"] = (_b_deep, lambda r: [_small()(r)], "exact")
VALIDATE["lca-of-deepest-leaves"] = _v_deep

# ---------------------------------------------------------------- time to spread
add(
    id="time-to-spread-from-node", title="Minutes Until Everything Is Infected", diff="Medium", topic="Trees",
    fn="spreadTime", params=[("tree", "int[]"), ("start", "int")], ret="int", cmp="exact",
    desc="<p>At minute <code>0</code> the node of a binary tree holding the value <code>start</code> catches an infection. In every following minute, each infected node infects all of its neighbours: its left child, its right child and its parent (when they exist).</p>"
         "<p>Return the number of minutes after which the whole tree is infected. A tree with a single node needs <code>0</code> minutes.</p>" + ENC +
         "<p>For the tree below (<code>[3, 5, 1, 6, 2, 0, 8, -1, -1, 7, 4]</code>) and <code>start = 2</code> the infection reaches 5, 7 and 4 after one minute, then 6 and 3, then 1, and finally 0 and 8, so the answer is <code>4</code>. With <code>start = 3</code> the answer is <code>3</code>.</p>" + CLASSIC,
    constraints=_cons(1, MAXN, ["<code>start</code> occurs in the tree"]),
    hints=["Each minute the infection moves exactly one edge. What is the answer in terms of distances?",
           "The tree is infected completely when the farthest node from <code>start</code> is infected. That farthest distance is the answer.",
           "Give every node a parent link (children are already known) and run a breadth-first search from <code>start</code>, counting levels; or compute the distance to every node by walking the array in level order after rooting the tree at <code>start</code>."],
    editorial=["After <code>t</code> minutes exactly the nodes within distance <code>t</code> of the start are infected, so the answer is the largest distance from <code>start</code> to any node (its eccentricity).",
               "Build the undirected neighbour lists (left, right, parent) in one pass and run a breadth-first search from the start; the number of BFS levels beyond the first is the answer. Each node and edge is processed once, so the solution is O(n)."],
    time="O(n)", space="O(n)",
    solution=LINKS + '''def spreadTime(tree, start):
    vals, left, right, par, depth = _info(tree)
    n = len(vals)
    s = vals.index(start)
    seen = [False] * n
    seen[s] = True
    frontier = [s]
    minutes = -1
    while frontier:
        minutes += 1
        nxt = []
        for x in frontier:
            for y in (left[x], right[x], par[x]):
                if y != -1 and not seen[y]:
                    seen[y] = True
                    nxt.append(y)
        frontier = nxt
    return minutes
''',
    tests=[[t, s] for t, s in [
        (CLASSIC_T, 2), (CLASSIC_T, 3), (CLASSIC_T, 7), ([0], 0), ([1, 2], 2), ([1, 2], 1), ([1, 2, 3, 4, 5, 6, 7], 1),
        ([1, 2, 3, 4, 5, 6, 7], 4), ([1, -1, 2, -1, 3, -1, 4], 4), ([1, -1, 2, -1, 3, -1, 4], 2),
    ]],
)
_ps = _P[-1]
_r = rnd(9108)
for _n, _m in [(1500, "left"), (1500, "zig"), (1500, "random"), (1500, "complete"), (1500, "deep")]:
    _a = _utree(_r, _n, _m)
    _ps["tests"].append([_a, _r.choice(_vals(_a))])


def _b_spread(tree, start):
    root = _build(tree)
    adj = {}
    st = [root]
    while st:
        x = st.pop()
        adj.setdefault(x.v, set())
        for c in (x.l, x.r):
            if c:
                adj.setdefault(c.v, set())
                adj[x.v].add(c.v)
                adj[c.v].add(x.v)
                st.append(c)
    infected = {start}
    t = 0
    while len(infected) < len(adj):
        infected |= {y for x in infected for y in adj[x]}
        t += 1
    return t


CHECKS["time-to-spread-from-node"] = (_b_spread, lambda r: (lambda a: [a, r.choice(_vals(a))])(_small()(r)), "exact")


def _v_spread(tests):
    for t in tests:
        _v_tree(t["args"][0], 1)
        assert t["args"][1] in t["args"][0]


VALIDATE["time-to-spread-from-node"] = _v_spread

# ---------------------------------------------------------------- good leaf pairs
add(
    id="leaf-pairs-within-distance", title="Pairs of Leaves Within a Distance", diff="Medium", topic="Trees", tier="extra",
    fn="countLeafPairs", params=[("tree", "int[]"), ("distance", "int")], ret="int", cmp="exact",
    desc="<p>A <em>leaf</em> is a node without children. Two different leaves form a <em>close pair</em> if the number of edges on the path between them is at most <code>distance</code>. Pairs are unordered: the pair (u, v) is the same as (v, u).</p>"
         "<p>Given a binary tree and <code>distance</code>, return the number of close pairs of leaves. A tree with fewer than two leaves has none. Node values play no role here and may repeat.</p>" + ENC +
         "<p>For the tree below (<code>[3, 5, 1, 6, 2, 0, 8, -1, -1, 7, 4]</code>) the leaves are 6, 0, 8, 7 and 4. With <code>distance = 3</code> the close pairs are (7, 4), (6, 7), (6, 4) and (0, 8), so the answer is <code>4</code>.</p>" + CLASSIC,
    constraints=_cons(0, MAXN, ["1 &le; distance &le; 10"], distinct=False),
    hints=["Checking every pair of leaves with a path computation is quadratic in the number of leaves, and each path may be long. Use that the distance limit is tiny.",
           "Every pair of leaves has a unique meeting node: their lowest common ancestor. For each node you only need to know how many leaves lie at each distance 1..distance below it.",
           "Return from each node an array <code>cnt[d]</code> = number of leaves at distance <code>d</code> below it (shift the children's arrays by one). At a node with two children, add <code>cntL[a] * cntR[b]</code> over all <code>a + b &le; distance</code> to the answer, then merge the two arrays."],
    editorial=["Group the pairs by their lowest common ancestor. For a node <code>x</code>, let <code>L[a]</code> be the number of leaves at distance <code>a</code> from <code>x</code> inside its left subtree and <code>R[b]</code> the same for the right subtree. The pairs of leaves that meet exactly at <code>x</code> are one from each side, and their distance is <code>a + b</code>, so <code>x</code> contributes the sum of <code>L[a] * R[b]</code> over all <code>a + b &le; distance</code>.",
               "Distances greater than <code>distance</code> never matter, so each node keeps an array of just <code>distance + 1</code> counters. A leaf has <code>cnt[0] = 1</code>; an inner node's array is the element-wise sum of its children's arrays shifted by one. Processing nodes from last to first in level order handles children before parents. The cost is O(n &middot; distance<sup>2</sup>)."],
    time="O(n * distance^2)", space="O(n * distance)",
    solution=LINKS + '''def countLeafPairs(tree, distance):
    vals, left, right = _links(tree)
    n = len(vals)
    D = distance
    cnt = [None] * n
    pairs = 0
    for k in range(n - 1, -1, -1):
        l, r = left[k], right[k]
        if l == -1 and r == -1:
            c = [0] * (D + 1)
            c[0] = 1
            cnt[k] = c
            continue
        A = [0] * (D + 1)
        B = [0] * (D + 1)
        if l != -1:
            A[1:] = cnt[l][:D]
            cnt[l] = None
        if r != -1:
            B[1:] = cnt[r][:D]
            cnt[r] = None
        if l != -1 and r != -1:
            for a in range(1, D + 1):
                if A[a]:
                    for b in range(1, D - a + 1):
                        pairs += A[a] * B[b]
        cnt[k] = [A[i] + B[i] for i in range(D + 1)]
    return pairs
''',
    tests=[[t, d] for t, d in [
        (CLASSIC_T, 3), (CLASSIC_T, 2), (CLASSIC_T, 10), (CLASSIC_T, 1), ([], 5), ([0], 4), ([1, 2], 3), ([1, 2, 3], 2),
        ([1, 2, 3, 4, 5, 6, 7], 3), ([1, 2, 3, 4, 5, 6, 7], 4), ([1, 1, 1, -1, 1, 1, -1, 1], 6),
    ]],
)
_ps = _P[-1]
_r = rnd(9109)
for _n, _m, _d in [(1500, "complete", 4), (1500, "random", 10), (1500, "random", 3), (1500, "deep", 10), (1500, "zig", 10)]:
    _ps["tests"].append([_tree(_r, _n, _m, 0, MAXV), _d])


def _b_leafpairs(tree, distance):
    root = _build(tree)
    ps = {}
    st = [(root, ())] if root else []
    leaves = []
    while st:
        x, p = st.pop()
        p = p + (id(x),)
        if x.l is None and x.r is None:
            leaves.append(p)
        for c in (x.l, x.r):
            if c:
                st.append((c, p))
    cnt = 0
    for i in range(len(leaves)):
        for j in range(i + 1, len(leaves)):
            c = _common(leaves[i], leaves[j])
            if len(leaves[i]) + len(leaves[j]) - 2 * c <= distance:
                cnt += 1
    return cnt


def _v_leafpairs(tests):
    for t in tests:
        _v_tree(t["args"][0], 0, MAXN, distinct=False)
        assert 1 <= t["args"][1] <= 10


CHECKS["leaf-pairs-within-distance"] = (
    _b_leafpairs, lambda r: [_tree(r, r.randint(0, 14), r.choice(MODES), 0, 3), r.randint(1, 8)], "exact")
VALIDATE["leaf-pairs-within-distance"] = _v_leafpairs

# ================================================================== HARD

# ---------------------------------------------------------------- sum of distances
add(
    id="sum-of-distances-in-binary-tree", title="Sum of Distances to All Other Nodes", diff="Hard", topic="Trees", tier="extra",
    fn="sumOfDistances", params=[("tree", "int[]")], ret="int[]", cmp="exact",
    desc="<p>For every node of a binary tree compute the sum of the distances (number of edges on the connecting path) from that node to every other node of the tree.</p>"
         "<p>Return an array with one entry per real node, <strong>in the order in which the nodes appear in the level-order input</strong> (skip the <code>-1</code> markers): <code>ans[k]</code> belongs to the k-th real node. Node values play no role and may repeat. The empty tree gives <code>[]</code>.</p>" + ENC +
         "<p>For <code>tree = [1, 2, 3]</code> the answer is <code>[2, 3, 3]</code>: from the root both nodes are at distance 1; from node 2 the root is at distance 1 and node 3 at distance 2. For <code>tree = [5, 5, -1, 5]</code> (a chain of three nodes) the answer is <code>[3, 2, 3]</code>.</p>",
    constraints=_cons(0, MAXN, distinct=False),
    hints=["Running a search from every node costs O(n) each, which is O(n<sup>2</sup>) overall. With n = 1,500 that is borderline, and the idea matters more: reuse work between neighbouring nodes.",
           "Compute the answer for the root with one traversal, and compute subtree sizes at the same time. Then think about how the answer changes when you move from a node to one of its children.",
           "Moving from a parent <code>p</code> to its child <code>c</code> brings the <code>size[c]</code> nodes of c's subtree one step closer and pushes the other <code>n - size[c]</code> nodes one step farther: <code>ans[c] = ans[p] - size[c] + (n - size[c])</code>. The root's answer is the sum of all depths."],
    editorial=["This is the classic re-rooting technique. First compute <code>size[k]</code>, the number of nodes in the subtree of k, bottom-up, and the answer of the root, which is simply the sum of all depths.",
               "Now go top-down. Take a node <code>p</code> with known answer and its child <code>c</code>. Compared with standing at <code>p</code>, standing at <code>c</code> shortens the distance by 1 to each of the <code>size[c]</code> nodes inside c's subtree and lengthens it by 1 to each of the other <code>n - size[c]</code> nodes. Hence <code>ans[c] = ans[p] - size[c] + (n - size[c])</code>. Because the level-order array lists parents before children, both passes are plain loops over the nodes: O(n) time and space.",
               "The largest possible value is about n<sup>2</sup>/2 &asymp; 1.1 million for a chain of 1,500 nodes, comfortably inside 32 bits."],
    time="O(n)", space="O(n)",
    solution=LINKS + '''def sumOfDistances(tree):
    vals, left, right, par, depth = _info(tree)
    n = len(vals)
    if n == 0:
        return []
    size = [1] * n
    for k in range(n - 1, 0, -1):
        size[par[k]] += size[k]
    ans = [0] * n
    ans[0] = sum(depth)
    for k in range(1, n):
        ans[k] = ans[par[k]] - size[k] + (n - size[k])
    return ans
''',
    tests=[[t] for t in [
        [], [0], [1, 2], [1, 2, 3], [5, 5, -1, 5], [1, 2, 3, 4, 5, 6, 7], CLASSIC_T, [1, -1, 2, -1, 3, -1, 4], [1, 2, 3, -1, 4, -1, 5],
    ]],
)
_ps = _P[-1]
_r = rnd(9110)
for _n, _m in [(1500, "left"), (1500, "random"), (1500, "complete"), (1499, "zig")]:
    _ps["tests"].append([_tree(_r, _n, _m, 0, MAXV)])


def _b_sumdist(tree):
    root = _build(tree)
    if root is None:
        return []
    order, adj = [], {}
    q = deque([root])
    while q:
        x = q.popleft()
        order.append(x)
        adj[id(x)] = adj.get(id(x), [])
        for c in (x.l, x.r):
            if c:
                adj.setdefault(id(c), []).append(id(x))
                adj[id(x)].append(id(c))
                q.append(c)
    out = []
    for x in order:
        dist = {id(x): 0}
        bq = deque([id(x)])
        while bq:
            u = bq.popleft()
            for w in adj[u]:
                if w not in dist:
                    dist[w] = dist[u] + 1
                    bq.append(w)
        out.append(sum(dist.values()))
    return out


def _v_sumdist(tests):
    for t in tests:
        _v_tree(t["args"][0], 0, MAXN, distinct=False)


CHECKS["sum-of-distances-in-binary-tree"] = (
    _b_sumdist, lambda r: [_tree(r, r.randint(0, 12), r.choice(MODES), 0, 3)], "exact")
VALIDATE["sum-of-distances-in-binary-tree"] = _v_sumdist

# ---------------------------------------------------------------- mixed ancestor queries
MAXQN = 2000
MAXQ = 1500
add(
    id="tree-ancestor-lca-distance-queries", title="Ancestor, LCA and Distance Queries", diff="Hard", topic="Trees", tier="extra",
    fn="answerQueries", params=[("tree", "int[]"), ("ops", "int[][]")], ret="int[]", cmp="exact",
    desc="<p>You are given a binary tree with distinct node values and a list of queries. Each query is a triple <code>[type, a, b]</code>; the answer to query <code>i</code> goes to position <code>i</code> of the result.</p>"
         "<ul><li><code>[1, v, k]</code>: the value of the <code>k</code>-th ancestor of the node with value <code>v</code> (<code>k = 1</code> is its parent, <code>k = 2</code> its grandparent, ...). If the node has fewer than <code>k</code> ancestors the answer is <code>-1</code>. For <code>k = 0</code> the answer is <code>v</code> itself.</li>"
         "<li><code>[2, a, b]</code>: the value of the lowest common ancestor of the nodes holding <code>a</code> and <code>b</code> (a node is its own ancestor here).</li>"
         "<li><code>[3, a, b]</code>: the distance, in edges, between the nodes holding <code>a</code> and <code>b</code>.</li></ul>" + ENC +
         "<p>For the tree below (<code>[3, 5, 1, 6, 2, 0, 8, -1, -1, 7, 4]</code>) and <code>ops = [[1, 7, 2], [2, 6, 4], [3, 7, 8], [1, 3, 1]]</code> the answer is <code>[5, 5, 5, -1]</code>: the grandparent of 7 is 5, LCA(6, 4) = 5, dist(7, 8) = 5, and the root has no parent.</p>" + CLASSIC,
    constraints=_cons(1, MAXQN, ["1 &le; ops.length &le; 1,500", "Every <code>v</code>, <code>a</code>, <code>b</code> in a query occurs in the tree", "Each query has exactly three integers; <code>type</code> is 1, 2 or 3; for type 1, 0 &le; k &le; 2,000"]),
    hints=["Answering each query by climbing parent by parent costs O(depth). On a chain of 2,000 nodes with 1,500 queries that is millions of steps, so look for a way to jump.",
           "Each node has one parent, so the 2<sup>j</sup>-th ancestor of a node is the 2<sup>j-1</sup>-th ancestor of its 2<sup>j-1</sup>-th ancestor. Precompute <code>up[j][node]</code> for all j up to log<sub>2</sub>(n).",
           "k-th ancestor: if k exceeds the depth the answer is -1; otherwise jump by every power of two present in the binary form of k. LCA: lift the deeper node by the depth difference, then from the highest j to the lowest jump both nodes whenever <code>up[j]</code> differs. Distance: <code>depth[a] + depth[b] - 2 * depth[lca]</code>."],
    editorial=["Use <em>binary lifting</em>. Compute parent and depth of every node (one pass over the level-order array, since parents come first), then fill <code>up[0] = parent</code> and <code>up[j][x] = up[j-1][ up[j-1][x] ]</code>, with -1 meaning 'above the root'. There are about log<sub>2</sub> n tables, built in O(n log n).",
               "A k-th ancestor query first checks <code>k &gt; depth[v]</code> (answer -1) and then jumps once for every set bit of k. For the LCA, lift the deeper node to the depth of the other one; if they coincide that node is the answer; otherwise for j from high to low jump both nodes while <code>up[j][a] != up[j][b]</code>, and the common parent <code>up[0][a]</code> is the LCA. The distance follows from depths and the LCA. Each query costs O(log n), so the whole solution is O((n + q) log n).",
               "For this size a plain climb also passes in many cases, but it degrades to O(n &middot; q) on deep trees; the lifting tables are the technique worth knowing, and they work unchanged for trees with millions of nodes."],
    time="O((n + q) log n)", space="O(n log n)",
    solution=LINKS + '''def answerQueries(tree, ops):
    vals, left, right, par, depth = _info(tree)
    n = len(vals)
    where = {v: k for k, v in enumerate(vals)}
    LOG = max(1, max(depth).bit_length())
    up = [par]
    for j in range(1, LOG):
        prev = up[-1]
        up.append([prev[x] if prev[x] == -1 else prev[prev[x]] for x in range(n)])

    def lift(x, k):
        j = 0
        while k and x != -1:
            if k & 1:
                x = up[j][x]
            k >>= 1
            j += 1
        return x

    def lca(a, b):
        if depth[a] < depth[b]:
            a, b = b, a
        a = lift(a, depth[a] - depth[b])
        if a == b:
            return a
        for j in range(LOG - 1, -1, -1):
            if up[j][a] != up[j][b]:
                a = up[j][a]
                b = up[j][b]
        return par[a]

    out = []
    for t, a, b in ops:
        if t == 1:
            x = where[a]
            if b > depth[x]:
                out.append(-1)
            else:
                out.append(vals[lift(x, b)])
        else:
            x, y = where[a], where[b]
            l = lca(x, y)
            out.append(vals[l] if t == 2 else depth[x] + depth[y] - 2 * depth[l])
    return out
''',
    tests=[],
)
_ps = _P[-1]
_r = rnd(9111)


def _ops(r, arr, q, kmax=None):
    vv = _vals(arr)
    out = []
    for _ in range(q):
        t = r.randint(1, 3)
        if t == 1:
            out.append([1, r.choice(vv), r.randint(0, kmax if kmax is not None else 12)])
        else:
            out.append([t, r.choice(vv), r.choice(vv)])
    return out


for _t, _o in [
    (CLASSIC_T, [[1, 7, 2], [2, 6, 4], [3, 7, 8], [1, 3, 1]]),
    ([0], [[1, 0, 0], [1, 0, 1], [2, 0, 0], [3, 0, 0]]),
    ([1, 2], [[1, 2, 1], [1, 2, 2], [2, 1, 2], [3, 1, 2], [3, 2, 2]]),
    ([1, -1, 2, -1, 3, -1, 4], [[1, 4, 3], [1, 4, 4], [2, 4, 2], [3, 1, 4], [1, 3, 0]]),
    ([1, 2, 3, 4, 5, 6, 7], [[2, 4, 5], [2, 4, 7], [3, 4, 7], [3, 4, 5], [1, 5, 2], [1, 5, 3], [2, 1, 6]]),
]:
    _ps["tests"].append([_t, _o])
for _n, _m, _q, _kmax in [(30, "random", 40, 8), (60, "deep", 80, 20)]:
    _a = _utree(_r, _n, _m)
    _ps["tests"].append([_a, _ops(_r, _a, _q, _kmax)])
for _n, _m, _q, _kmax in [(2000, "left", 1500, 2000), (2000, "zig", 1500, 2000), (2000, "random", 1500, 15)]:
    _a = _utree(_r, _n, _m)
    _ps["tests"].append([_a, _ops(_r, _a, _q, _kmax)])


def _b_ops(tree, ops):
    ps = _paths(_build(tree))
    out = []
    for t, a, b in ops:
        if t == 1:
            p = ps[a]
            out.append(p[len(p) - 1 - b] if b < len(p) else -1)
        else:
            pa, pb = ps[a], ps[b]
            c = _common(pa, pb)
            out.append(pa[c - 1] if t == 2 else len(pa) + len(pb) - 2 * c)
    return out


def _v_ops(tests):
    for t in tests:
        arr, ops = t["args"]
        _v_tree(arr, 1, MAXQN)
        assert 1 <= len(ops) <= MAXQ
        s = set(arr)
        for o in ops:
            assert len(o) == 3 and o[0] in (1, 2, 3)
            assert o[1] in s
            if o[0] == 1:
                assert 0 <= o[2] <= 2000
            else:
                assert o[2] in s


CHECKS["tree-ancestor-lca-distance-queries"] = (
    _b_ops, lambda r: (lambda a: [a, _ops(r, a, r.randint(1, 8))])(_small(1, 12)(r)), "exact")
VALIDATE["tree-ancestor-lca-distance-queries"] = _v_ops
