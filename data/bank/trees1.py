"""Problems: binary trees (level-order array encoding, -1 for a missing child). See data/lib.py for the registry."""
from collections import deque
from itertools import combinations

from lib import add, rnd, CHECKS, VALIDATE, gen_arr  # noqa: F401
from lib import P as _P

MAXN = 1500      # maximum number of nodes in any tree
MAXV = 10000     # maximum node value

# ------------------------------------------------------------------ shared statement text
ENC = (
    "<p><strong>How trees are given.</strong> There is no tree type here. A binary tree is passed as an integer array in "
    "<em>level-order</em> (top to bottom, left to right), the same way LeetCode serialises trees. A missing child is written as "
    "<code>-1</code>, and every real node value is non-negative. The children of a missing node are not listed, and trailing "
    "<code>-1</code> entries are dropped, so a non-empty array never ends with <code>-1</code>. The empty tree is <code>[]</code>.</p>"
    "<p>For example, <code>[1, 2, 3, -1, 4]</code> describes the tree on the left: the root is 1 with children 2 and 3, node 2 has no left "
    "child and has 4 as its right child, and node 3 is a leaf.</p>"
    "<pre>    1\n   / \\\n  2   3\n   \\\n    4</pre>"
)


def _cons(extra=None):
    out = [f"0 &le; number of nodes &le; {MAXN:,}", f"0 &le; node value &le; {MAXV:,}",
           "The array follows the encoding above exactly (valid level-order, no trailing -1)"]
    return out + (extra or [])


# ------------------------------------------------------------------ helpers (parsing, building, shapes)
class _N:
    __slots__ = ("v", "l", "r")

    def __init__(self, v):
        self.v = v
        self.l = None
        self.r = None


def _build(arr):
    """Queue based parse of the level-order encoding into linked nodes."""
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
    """Canonical level-order encoding of the tree rooted at `root` (trailing -1s removed)."""
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


def _inorder(root):
    out, st, x = [], [], root
    while st or x:
        while x:
            st.append(x)
            x = x.l
        x = st.pop()
        out.append(x)
        x = x.r
    return out


def _shape(r, n, mode="random"):
    """A random tree shape with n nodes (values all 0)."""
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
    root = _shape(r, n, mode)
    for x in _preorder(root):
        x.v = r.randint(lo, hi)
    return _encode(root)


def _bst(r, n, mode="random", mut=0, vmax=MAXV):
    """A valid BST shape (strictly increasing inorder) with `mut` random values overwritten."""
    root = _shape(r, n, mode)
    nodes = _inorder(root)
    for x, v in zip(nodes, sorted(r.sample(range(0, vmax + 1), n))):
        x.v = v
    for _ in range(mut if nodes else 0):
        r.choice(nodes).v = r.randint(0, vmax)
    return _encode(root)


def _mirror(x):
    if x is None:
        return None
    root = _N(x.v)
    st = [(x, root)]
    while st:
        a, b = st.pop()
        if a.l:
            b.r = _N(a.l.v)
            st.append((a.l, b.r))
        if a.r:
            b.l = _N(a.r.v)
            st.append((a.r, b.l))
    return root


def _sym_tree(r, m, mode="random", lo=0, hi=MAXV, mutate=0, rootv=None):
    """Mirror-symmetric tree: a random left part with m nodes and its mirror image on the right."""
    left = _shape(r, m, mode)
    for x in _preorder(left):
        x.v = r.randint(lo, hi)
    root = _N(r.randint(lo, hi) if rootv is None else rootv)
    root.l = left
    root.r = _mirror(left)
    nodes = _preorder(root)
    for _ in range(mutate):
        r.choice(nodes).v = r.randint(lo, hi)
    return _encode(root)


def _gen(nmax=10, vmax=5, modes=MODES):
    def g(r):
        return [_tree(r, r.randint(0, nmax), r.choice(modes), 0, vmax)]
    return g


def _v_trees(tests):
    for t in tests:
        for arr in t["args"]:
            assert isinstance(arr, list) and all(isinstance(x, int) for x in arr)
            assert arr == _encode(_build(arr)), ("not a canonical level-order encoding", arr[:12])
            nodes = [x for x in arr if x != -1]
            assert len(nodes) <= MAXN, "too many nodes"
            assert all(0 <= x <= MAXV for x in nodes), "node value out of range"
            assert not arr or arr[0] != -1


# Parsing used inside the reference solutions. The i-th real node (0-based, level order) owns array
# slots 2i+1 and 2i+2 as its children, because every real node contributes exactly two child slots.
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


'''

# a few hand written trees reused by several problems
BASE = [
    [], [0], [1, 2, 3], [1, -1, 2, -1, 3], [1, 2, -1, 3, -1, 4], [3, 9, 20, -1, -1, 15, 7],
    [1, 2, 3, 4, 5, 6, 7], [1, 2, 2, 3, 3, -1, -1, 4, 4], [5, 5, 5, 5, 5, 5, 5, 5],
]


def _big(seed, hi=MAXV, extra=()):
    r = rnd(seed)
    return [_tree(r, MAXN, "left", 0, hi), _tree(r, MAXN, "right", 0, hi), _tree(r, MAXN, "zig", 0, hi),
            _tree(r, MAXN, "complete", 0, hi), _tree(r, MAXN, "random", 0, hi), _tree(r, MAXN, "deep", 0, hi), *extra]


# ================================================================== EASY

# ---------------------------------------------------------------- maximum depth
add(
    id="binary-tree-maximum-depth", title="Maximum Depth of a Binary Tree", diff="Easy", topic="Trees",
    fn="maxDepth", params=[("tree", "int[]")], ret="int", cmp="exact",
    desc="<p>Given a binary tree, return its <em>depth</em>: the number of nodes on the longest path that starts at the root and ends at a leaf. The empty tree has depth <code>0</code>.</p>" + ENC +
         "<p>For <code>tree = [3, 9, 20, -1, -1, 15, 7]</code> the answer is <code>3</code> (for example 3 &rarr; 20 &rarr; 15).</p>",
    constraints=_cons(),
    hints=["Depth is a property you can compute for every node: how deep does the path to it go?",
           "A child is exactly one level deeper than its parent. Walk the tree from the root and remember the largest level you see.",
           "Recursively: <code>depth(node) = 1 + max(depth(left), depth(right))</code> with <code>depth(missing) = 0</code>. Or process the array level by level and count the levels."],
    editorial=["The recursive definition is the cleanest: an empty tree has depth 0, otherwise the depth is one more than the larger depth of the two subtrees. Every node is visited once, so the running time is linear.",
               "With the array encoding you can avoid recursion completely. The real nodes appear in level order, so the k-th real node's children sit at array slots <code>2k+1</code> and <code>2k+2</code>. Parents always come before their children, so a single left-to-right pass can assign <code>depth[child] = depth[parent] + 1</code> and track the maximum."],
    time="O(n)", space="O(n)",
    solution=LINKS + '''def maxDepth(tree):
    vals, left, right = _links(tree)
    n = len(vals)
    if n == 0:
        return 0
    depth = [1] * n
    best = 1
    for k in range(n):
        for c in (left[k], right[k]):
            if c != -1:
                depth[c] = depth[k] + 1
                best = max(best, depth[c])
    return best
''',
    tests=[[t] for t in BASE + _big(7001)],
)


def _b_depth(tree):
    def d(x):
        return 0 if x is None else 1 + max(d(x.l), d(x.r))
    return d(_build(tree))


CHECKS["binary-tree-maximum-depth"] = (_b_depth, _gen(), "exact")
VALIDATE["binary-tree-maximum-depth"] = _v_trees

# ---------------------------------------------------------------- contains subtree
add(
    id="binary-tree-contains-subtree", title="Subtree of Another Binary Tree", diff="Easy", topic="Trees",
    fn="containsSubtree", params=[("tree", "int[]"), ("sub", "int[]")], ret="bool", cmp="exact",
    desc="<p>Given two binary trees <code>tree</code> and <code>sub</code>, decide whether <code>sub</code> occurs inside <code>tree</code>. It does if some node of <code>tree</code>, taken together with <em>all</em> of its descendants, forms a tree that is identical to <code>sub</code> in both shape and node values.</p>"
         "<p>A node with only some of its descendants does not count, and the empty tree is considered to occur in every tree (including the empty one). Return <code>true</code> or <code>false</code>.</p>" + ENC +
         "<p>Both arguments use this encoding. With <code>tree = [3, 4, 5, 1, 2]</code> and <code>sub = [4, 1, 2]</code> the answer is <code>true</code>. If node 2 of <code>tree</code> had an extra child, as in <code>[3, 4, 5, 1, 2, -1, -1, -1, -1, 0]</code>, the answer would be <code>false</code>.</p>",
    constraints=["0 &le; number of nodes in each tree &le; 1,500", f"0 &le; node value &le; {MAXV:,}",
                 "Both arrays follow the encoding above exactly (valid level-order, no trailing -1)"],
    hints=["Try every node of <code>tree</code> as the possible match for the root of <code>sub</code>, and compare the two trees from there.",
           "That works but can be slow on big inputs (every start may compare many nodes). Can you give each subtree a compact identity that is equal exactly when two subtrees are identical?",
           "Process nodes bottom-up. Give each node an id based on the triple (value, id of left subtree, id of right subtree), using 0 for a missing child and a dictionary to hand out ids. Identical subtrees receive identical ids."],
    editorial=["The direct approach compares <code>sub</code> against the subtree of every node in <code>tree</code>. A comparison stops at the first difference, but in the worst case (long chains of equal values) it can take O(n &middot; m) time overall.",
               "A faster approach is subtree hashing by canonical ids. Process the nodes of both trees from the bottom up and map the key <code>(value, leftId, rightId)</code> to a small integer through one shared dictionary; a missing child has id 0. Two subtrees get the same id exactly when they are identical, since the key captures the value and, inductively, the whole shape beneath. Then <code>sub</code> occurs in <code>tree</code> if and only if the id of the root of <code>sub</code> is among the ids of the nodes of <code>tree</code>. That is O(n + m) expected time."],
    time="O(n + m)", space="O(n + m)",
    solution=LINKS + '''def containsSubtree(tree, sub):
    if not sub:
        return True
    table = {}

    def ids(t):
        vals, left, right = _links(t)
        out = [0] * len(vals)
        for k in range(len(vals) - 1, -1, -1):
            lid = out[left[k]] if left[k] != -1 else 0
            rid = out[right[k]] if right[k] != -1 else 0
            out[k] = table.setdefault((vals[k], lid, rid), len(table) + 1)
        return out

    a = ids(tree)
    b = ids(sub)
    return b[0] in set(a)
''',
    tests=[],
)
_ps = _P[-1]
_r = rnd(7002)


def _sub_of(arr, which):
    root = _build(arr)
    return _encode(which(root))


_t_big = _tree(_r, MAXN, "random", 0, 3)
_t_chain = _tree(_r, MAXN, "left", 0, 0)
_sub_chain = _tree(_r, 700, "left", 0, 0)
_sub_chain_bad = list(_sub_chain)
_sub_chain_bad[-1] = 1
_t_rnd = _tree(_r, MAXN, "random", 0, 1)
_t_comp = _tree(_r, MAXN, "complete", 0, 0)
_big_left = _sub_of(_t_big, lambda x: x.l)
_big_left_bad = list(_big_left)
_big_left_bad[-1] += 1
_ps["tests"] = [
    [[3, 4, 5, 1, 2], [4, 1, 2]],
    [[3, 4, 5, 1, 2, -1, -1, -1, -1, 0], [4, 1, 2]],
    [[], []],
    [[], [1]],
    [[1], []],
    [[1, 2, 3], [1, 2, 3]],
    [[1, 2, 3], [1, 2]],
    [[1, 1], [1]],
    [[1, -1, 1, -1, 1], [1, -1, 1]],
    [[1, 2, 3, 4, 5, 6, 7], [3, 6, 7]],
    [[1, 2, 3, 4, 5, 6, 7], [3, 7, 6]],
    [[0, 0, 0, 0, -1, -1, 0], [0, 0, -1, 0]],
    [_t_big, _big_left],
    [_t_big, _big_left_bad],
    [_t_chain, _sub_chain],
    [_t_chain, _sub_chain_bad],
    [_t_comp, _tree(_r, 255, "complete", 0, 0)],
    [_t_rnd, _sub_of(_t_rnd, lambda x: x.r)],
]


def _b_sub(tree, sub):
    def same(a, b):
        if a is None or b is None:
            return a is None and b is None
        return a.v == b.v and same(a.l, b.l) and same(a.r, b.r)

    t, s = _build(tree), _build(sub)
    if s is None:
        return True
    return any(same(x, s) for x in _preorder(t))


def _g_sub(r):
    mode = r.choice(MODES)
    root = _shape(r, r.randint(0, 10), mode)
    for x in _preorder(root):
        x.v = r.randint(0, 2)
    arr = _encode(root)
    nodes = _preorder(root)
    if nodes and r.random() < 0.6:
        sub = _encode(r.choice(nodes))
        if r.random() < 0.4:
            i = r.choice([j for j, v in enumerate(sub) if v != -1])
            sub[i] = r.randint(0, 2)
    else:
        sub = _tree(r, r.randint(0, 4), r.choice(MODES), 0, 2)
    return [arr, sub]


CHECKS["binary-tree-contains-subtree"] = (_b_sub, _g_sub, "exact")
VALIDATE["binary-tree-contains-subtree"] = _v_trees

# ---------------------------------------------------------------- symmetric
add(
    id="mirror-symmetric-binary-tree", title="Symmetric Binary Tree", diff="Easy", topic="Trees",
    fn="isSymmetric", params=[("tree", "int[]")], ret="bool", cmp="exact",
    desc="<p>A binary tree is <em>symmetric</em> if it is a mirror image of itself around the vertical line through the root: the left subtree of the root, flipped left-to-right, is identical (shape and values) to the right subtree. Return <code>true</code> if the given tree is symmetric and <code>false</code> otherwise. The empty tree is symmetric.</p>" + ENC +
         "<p>For <code>tree = [1, 2, 2, 3, 4, 4, 3]</code> the answer is <code>true</code>. For <code>tree = [1, 2, 2, -1, 3, -1, 3]</code> it is <code>false</code>, because both 2s have their only child on the right side.</p>",
    constraints=_cons(),
    hints=["Comparing the root's left subtree with its right subtree is not a plain equality check. Which child of one side corresponds to which child of the other?",
           "Walk two nodes at once, <code>a</code> in the left half and <code>b</code> in the right half. They must have equal values, and the outer children (<code>a.left</code>, <code>b.right</code>) and inner children (<code>a.right</code>, <code>b.left</code>) must again be mirror pairs.",
           "Keep a stack or queue of pairs, starting with (root.left, root.right). Both missing is fine; exactly one missing or different values means not symmetric."],
    editorial=["Define a helper <code>mirror(a, b)</code>: it is true when both nodes are missing, false when exactly one is missing or the values differ, and otherwise true only if <code>mirror(a.left, b.right)</code> and <code>mirror(a.right, b.left)</code> both hold. The tree is symmetric when <code>mirror(root.left, root.right)</code> holds. Each node is paired with exactly one partner, so the work is linear.",
               "The same check works iteratively with a stack of pairs, which avoids deep recursion on tall, skinny trees. Using the array encoding, the pair of node indices is all you need to push."],
    time="O(n)", space="O(n)",
    solution=LINKS + '''def isSymmetric(tree):
    vals, left, right = _links(tree)
    if not vals:
        return True
    stack = [(left[0], right[0])]
    while stack:
        a, b = stack.pop()
        if a == -1 and b == -1:
            continue
        if a == -1 or b == -1 or vals[a] != vals[b]:
            return False
        stack.append((left[a], right[b]))
        stack.append((right[a], left[b]))
    return True
''',
    tests=[],
)
_ps = _P[-1]
_r = rnd(7003)
_ps["tests"] = [[t] for t in BASE + [
    [1, 2, 2, 3, 4, 4, 3], [1, 2, 2, -1, 3, -1, 3], [1, 2, 2, 3, -1, -1, 3],
    _sym_tree(_r, 749, "left", 0, 5), _sym_tree(_r, 749, "zig", 0, 5),
    _sym_tree(_r, 749, "random", 0, MAXV), _sym_tree(_r, 749, "complete", 0, 1),
    _sym_tree(_r, 700, "deep", 0, 3, mutate=1), _sym_tree(_r, 749, "random", 0, 2, mutate=2),
    _tree(_r, MAXN, "complete", 0, 0),
]]


def _b_sym(tree):
    root = _build(tree)
    return _encode(root) == _encode(_mirror(root))


def _g_sym(r):
    if r.random() < 0.6:
        return [_sym_tree(r, r.randint(0, 5), r.choice(MODES), 0, 2, mutate=r.choice([0, 0, 1, 2]))]
    return [_tree(r, r.randint(0, 9), r.choice(MODES), 0, 2)]


CHECKS["mirror-symmetric-binary-tree"] = (_b_sym, _g_sym, "exact")
def _v_sym(tests):
    _v_trees(tests)
    assert any(t["expected"] for t in tests) and any(not t["expected"] for t in tests)


VALIDATE["mirror-symmetric-binary-tree"] = _v_sym

# ================================================================== MEDIUM

# ---------------------------------------------------------------- balanced
add(
    id="height-balanced-binary-tree-check", title="Height-Balanced Binary Tree", diff="Medium", topic="Trees",
    fn="isBalanced", params=[("tree", "int[]")], ret="bool", cmp="exact",
    desc="<p>The <em>height</em> of a node is the number of nodes on the longest downward path starting at that node (a missing node has height <code>0</code>). A binary tree is <em>height-balanced</em> if, at <strong>every</strong> node, the heights of its left and right subtrees differ by at most <code>1</code>.</p>"
         "<p>Return <code>true</code> if the given tree is height-balanced, <code>false</code> otherwise. The empty tree is balanced.</p>" + ENC +
         "<p>For <code>tree = [3, 9, 20, -1, -1, 15, 7]</code> the answer is <code>true</code>. For <code>tree = [1, 2, 2, 3, 3, -1, -1, 4, 4]</code> it is <code>false</code>: the root's left subtree has height 3 but its right subtree has height 1.</p>",
    constraints=_cons(),
    hints=["Checking only the root is not enough. The rule must hold at every node.",
           "A direct way is to compute the height of both subtrees at every node, but recomputing heights again and again is wasteful on tall trees.",
           "Compute heights bottom-up exactly once. While computing the height of a node, also compare the two child heights, and give up as soon as a difference above 1 shows up."],
    editorial=["The naive solution calls a height function at every node, which repeats work and takes O(n<sup>2</sup>) on a skewed tree.",
               "Instead compute each height once, from the leaves upwards. At a node you already know the heights of both children; if they differ by more than 1 the answer is false, otherwise the node's height is <code>1 + max(left, right)</code>. In the level-order array the children always come after their parent, so a single backwards pass over the real nodes does it with no recursion."],
    time="O(n)", space="O(n)",
    solution=LINKS + '''def isBalanced(tree):
    vals, left, right = _links(tree)
    n = len(vals)
    h = [0] * n
    for k in range(n - 1, -1, -1):
        hl = h[left[k]] if left[k] != -1 else 0
        hr = h[right[k]] if right[k] != -1 else 0
        if abs(hl - hr) > 1:
            return False
        h[k] = 1 + max(hl, hr)
    return True
''',
    tests=[],
)
_ps = _P[-1]
_r = rnd(7004)


def _fib_tree(h):
    if h == 0:
        return None
    x = _N(0)
    x.l = _fib_tree(h - 1)
    x.r = _fib_tree(h - 2) if h >= 2 else None
    return x


def _fib_arr(h, spoil=False, seed=0):
    root = _fib_tree(h)
    nodes = _preorder(root)
    rr = rnd(seed)
    for x in nodes:
        x.v = rr.randint(0, MAXV)
    if spoil:
        cur = root
        while cur.l:
            cur = cur.l
        cur.l = _N(7)
    return _encode(root)


_ps["tests"] = [[t] for t in BASE + [
    [1, 2, 2, 3, 3, -1, -1, 4, 4], [1, 2, -1, 3], [1, 2, 3, 4, -1, -1, -1, 5], [1, 2, 3, 4, 5, -1, -1, 6],
    _fib_arr(14, False, 1), _fib_arr(14, True, 2),
    _tree(_r, MAXN, "complete", 0, MAXV), _tree(_r, MAXN, "left", 0, MAXV), _tree(_r, MAXN, "random", 0, MAXV),
    _tree(_r, 1023, "complete", 0, 3) + [0],
]]


def _b_bal(tree):
    def h(x):
        return 0 if x is None else 1 + max(h(x.l), h(x.r))

    return all(abs(h(x.l) - h(x.r)) <= 1 for x in _preorder(_build(tree)))


def _g_bal(r):
    return [_tree(r, r.randint(0, 12), r.choice(["random", "complete", "deep", "random"]), 0, 4)]


CHECKS["height-balanced-binary-tree-check"] = (_b_bal, _g_bal, "exact")


def _v_bal(tests):
    _v_trees(tests)
    assert any(t["expected"] for t in tests) and any(not t["expected"] for t in tests)


VALIDATE["height-balanced-binary-tree-check"] = _v_bal

# ---------------------------------------------------------------- diameter
add(
    id="binary-tree-diameter-in-edges", title="Diameter of a Binary Tree", diff="Medium", topic="Trees",
    fn="treeDiameter", params=[("tree", "int[]")], ret="int", cmp="exact",
    desc="<p>The <em>diameter</em> of a binary tree is the number of <strong>edges</strong> on the longest path between any two nodes. The path may or may not pass through the root, and it is allowed to turn at a node (go up, then down). A tree with zero or one node has diameter <code>0</code>.</p>" + ENC +
         "<p>For <code>tree = [1, 2, 3, 4, 5]</code> the answer is <code>3</code>, for example the path 4 &rarr; 2 &rarr; 1 &rarr; 3.</p>",
    constraints=_cons(),
    hints=["Look at the highest node of the longest path. Where can that path turn around?",
           "If a path peaks at node <code>x</code>, it goes down into the left subtree and down into the right subtree. Its length is the (deepest chain in left) + (deepest chain in right).",
           "Compute subtree heights bottom-up. At every node, the best path peaking there is <code>heightLeft + heightRight</code> (heights counted in nodes). Keep the maximum of that over all nodes."],
    editorial=["Every path has exactly one highest node, the place where it turns (or an endpoint). If the path peaks at <code>x</code>, the best choice is to go as deep as possible on each side, so the longest path peaking at <code>x</code> has <code>height(left) + height(right)</code> edges, where height counts nodes and a missing child has height 0.",
               "So one bottom-up pass is enough: compute the height of every node from its children's heights and update a global best with <code>hl + hr</code>. The answer is that best value. The array encoding lets you do the pass backwards over the real nodes without any recursion."],
    time="O(n)", space="O(n)",
    solution=LINKS + '''def treeDiameter(tree):
    vals, left, right = _links(tree)
    n = len(vals)
    h = [0] * n
    best = 0
    for k in range(n - 1, -1, -1):
        hl = h[left[k]] if left[k] != -1 else 0
        hr = h[right[k]] if right[k] != -1 else 0
        best = max(best, hl + hr)
        h[k] = 1 + max(hl, hr)
    return best
''',
    tests=[[t] for t in BASE + _big(7005) + [[1, 2, 3, 4, 5], [1, 2, -1, 3, 4, 5, -1, 6, -1, -1, 7]]],
)


def _b_diam(tree):
    nodes = _preorder(_build(tree))
    idx = {id(x): i for i, x in enumerate(nodes)}
    adj = [[] for _ in nodes]
    for x in nodes:
        for c in (x.l, x.r):
            if c:
                adj[idx[id(x)]].append(idx[id(c)])
                adj[idx[id(c)]].append(idx[id(x)])
    best = 0
    for s in range(len(nodes)):
        dist = {s: 0}
        q = deque([s])
        while q:
            u = q.popleft()
            for w in adj[u]:
                if w not in dist:
                    dist[w] = dist[u] + 1
                    q.append(w)
        best = max(best, max(dist.values()))
    return best


CHECKS["binary-tree-diameter-in-edges"] = (_b_diam, _gen(11), "exact")
VALIDATE["binary-tree-diameter-in-edges"] = _v_trees

# ---------------------------------------------------------------- zigzag
add(
    id="binary-tree-zigzag-levels", title="Zigzag Level Order Traversal", diff="Medium", topic="Trees",
    fn="zigzagLevels", params=[("tree", "int[]")], ret="int[][]", cmp="exact",
    desc="<p>Return the node values of a binary tree grouped by level, from the root level down. The first level (the root) is listed left to right, the next level right to left, the next left to right again, and so on, alternating at each level.</p>"
         "<p>The result is an array of rows, one row per level. The empty tree gives an empty list <code>[]</code>.</p>" + ENC +
         "<p>For <code>tree = [3, 9, 20, -1, -1, 15, 7]</code> the answer is <code>[[3], [20, 9], [15, 7]]</code>.</p>",
    constraints=_cons(),
    hints=["First solve the plain level-order traversal: how do you know which nodes are on the same level?",
           "A queue processed level by level gives each row in left-to-right order. Alternatively, record every node's depth and append to a row per depth.",
           "Once a row is collected left to right, reverse every row whose index (starting at 0) is odd."],
    editorial=["Collect the nodes level by level in normal left-to-right order. A breadth-first search with a queue does this naturally: process exactly as many nodes as were in the queue at the start of the level to form one row. Then reverse the rows at odd depths.",
               "Reversing costs the same as building the row, so the total work stays linear. The level-order array already lists nodes in this order; a node's depth is its parent's depth plus one, which lets you fill the rows in a single pass without a queue."],
    time="O(n)", space="O(n)",
    solution=LINKS + '''def zigzagLevels(tree):
    vals, left, right = _links(tree)
    n = len(vals)
    if n == 0:
        return []
    depth = [0] * n
    rows = []
    for k in range(n):
        d = depth[k]
        if d == len(rows):
            rows.append([])
        rows[d].append(vals[k])
        for c in (left[k], right[k]):
            if c != -1:
                depth[c] = d + 1
    for d in range(1, len(rows), 2):
        rows[d].reverse()
    return rows
''',
    tests=[[t] for t in BASE + _big(7006, 99) + [[1, 2, 3, 4, -1, -1, 5], [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]]],
)


def _b_zig(tree):
    rows = {}

    def go(x, d):
        if x is None:
            return
        rows.setdefault(d, []).append(x.v)
        go(x.l, d + 1)
        go(x.r, d + 1)

    go(_build(tree), 0)
    return [rows[d][::-1] if d % 2 else rows[d] for d in range(len(rows))]


CHECKS["binary-tree-zigzag-levels"] = (_b_zig, _gen(12, 30), "exact")
VALIDATE["binary-tree-zigzag-levels"] = _v_trees

# ---------------------------------------------------------------- right side view
add(
    id="binary-tree-right-side-values", title="Binary Tree Right Side View", diff="Medium", topic="Trees",
    fn="rightSideView", params=[("tree", "int[]")], ret="int[]", cmp="exact",
    desc="<p>Imagine standing to the right of a binary tree and looking at it. At each level you can see only the rightmost node of that level (nodes further left are hidden behind it). Return the values of the visible nodes, from the top level to the bottom level.</p>"
         "<p>The empty tree gives <code>[]</code>.</p>" + ENC +
         "<p>For <code>tree = [1, 2, 3, -1, 5, -1, 4]</code> the answer is <code>[1, 3, 4]</code>. Level 2 holds the nodes 5 and 4, and 4 is the rightmost of them, while 5 is hidden behind it.</p>",
    constraints=_cons(),
    hints=["One value per level is visible. Which node of a level is it?",
           "In a level-order traversal, the last node of each level is the rightmost one. Alternatively, a depth-first search that visits the right child first sees the visible node of each level first.",
           "Track depth. With a right-first DFS, record a node's value only when its depth has not been recorded yet. With level order, overwrite the answer for that depth every time you reach a node on it."],
    editorial=["Because the level-order array lists nodes top to bottom and left to right, the last node you see at a given depth is exactly the rightmost node of that level. Keep an answer slot per depth and overwrite it as you go; or take the last element of each level in a BFS.",
               "A depth-first alternative visits the right child before the left child and records the first node reached at each new depth. Both run in linear time."],
    time="O(n)", space="O(n)",
    solution=LINKS + '''def rightSideView(tree):
    vals, left, right = _links(tree)
    n = len(vals)
    if n == 0:
        return []
    depth = [0] * n
    view = []
    for k in range(n):
        d = depth[k]
        if d == len(view):
            view.append(vals[k])
        else:
            view[d] = vals[k]
        for c in (left[k], right[k]):
            if c != -1:
                depth[c] = d + 1
    return view
''',
    tests=[[t] for t in BASE + _big(7007, 99) + [[1, 2, 3, -1, 5, -1, 4], [1, 2, 3, 4], [1, 2, -1, 3, -1, 4, -1, 5]]],
)


def _b_right(tree):
    seen = {}

    def go(x, d):
        if x is None:
            return
        if d not in seen:
            seen[d] = x.v
        go(x.r, d + 1)
        go(x.l, d + 1)

    go(_build(tree), 0)
    return [seen[d] for d in range(len(seen))]


CHECKS["binary-tree-right-side-values"] = (_b_right, _gen(12, 30), "exact")
VALIDATE["binary-tree-right-side-values"] = _v_trees

# ---------------------------------------------------------------- good nodes
add(
    id="binary-tree-good-nodes-count", title="Count Good Nodes in a Binary Tree", diff="Medium", topic="Trees",
    fn="countGoodNodes", params=[("tree", "int[]")], ret="int", cmp="exact",
    desc="<p>In a binary tree, call a node <em>good</em> if no node on the path from the root to it (excluding the node itself) has a larger value than it. In other words, its value is greater than or equal to every ancestor's value. The root is always good.</p>"
         "<p>Return the number of good nodes. The empty tree has <code>0</code>.</p>" + ENC +
         "<p>For <code>tree = [3, 1, 4, 3, -1, 1, 5]</code> the answer is <code>4</code>: the nodes 3 (root), 4, the 3 below the 1, and 5 are good. The 1s are not, since each has an ancestor larger than 1.</p>",
    constraints=_cons(),
    hints=["Whether a node is good depends only on the path above it.",
           "You do not need the whole path, only the maximum value on it. What can you pass from a parent to its children?",
           "Carry <code>maxSoFar</code> down the tree. A node is good if <code>value &ge; maxSoFar</code>, and its children receive <code>max(maxSoFar, value)</code>."],
    editorial=["A node is good exactly when its value is at least the maximum of its ancestors' values, so each node only needs the running maximum of the path above it. Starting with the root (always good, running maximum equal to its value), push the running maximum down: a child is good if its value is at least the parent's running maximum, and it passes <code>max(parentMax, childValue)</code> on to its own children.",
               "Each node is visited once, so the time is linear. Since a parent precedes its children in the level-order array, a single left-to-right pass over the real nodes works without recursion."],
    time="O(n)", space="O(n)",
    solution=LINKS + '''def countGoodNodes(tree):
    vals, left, right = _links(tree)
    n = len(vals)
    if n == 0:
        return 0
    top = [0] * n            # largest value on the path from the root to node k, inclusive
    top[0] = vals[0]
    good = 1
    for k in range(n):
        for c in (left[k], right[k]):
            if c != -1:
                if vals[c] >= top[k]:
                    good += 1
                top[c] = max(top[k], vals[c])
    return good
''',
    tests=[[t] for t in BASE + _big(7008, 50) + [[3, 1, 4, 3, -1, 1, 5], [3, 3, -1, 4, 2], [9, 8, 7, 6, 5, 4, 3, 2, 1]]],
)


def _b_good(tree):
    count = 0

    def go(x, path):
        nonlocal count
        if x is None:
            return
        if all(p <= x.v for p in path):
            count += 1
        path.append(x.v)
        go(x.l, path)
        go(x.r, path)
        path.pop()

    go(_build(tree), [])
    return count


CHECKS["binary-tree-good-nodes-count"] = (_b_good, _gen(12, 6), "exact")
VALIDATE["binary-tree-good-nodes-count"] = _v_trees

# ================================================================== HARD

# ---------------------------------------------------------------- cameras
add(
    id="binary-tree-minimum-cameras", title="Binary Tree Cameras", diff="Hard", topic="Trees",
    fn="minCameras", params=[("tree", "int[]")], ret="int", cmp="exact",
    desc="<p>You may place surveillance cameras on the nodes of a binary tree. A camera on a node watches that node itself, its parent and its children (but nothing further away). Return the minimum number of cameras needed so that <strong>every</strong> node of the tree is watched. The empty tree needs <code>0</code> cameras.</p>" + ENC +
         "<p>Node values are irrelevant to the answer; only the shape matters. For <code>tree = [0, 0, -1, 0, 0]</code> the answer is <code>1</code> (a camera on the middle node covers all four nodes). For the chain <code>[0, 0, -1, 0, -1, 0]</code> of four nodes the answer is <code>2</code>.</p>",
    constraints=_cons(["Node values do not matter; only the shape of the tree does"]),
    hints=["Think about the leaves. Is it ever better to put a camera on a leaf than on its parent?",
           "Decide bottom-up. For each node keep one of three states: not watched yet, has a camera, or watched by a neighbouring camera.",
           "Greedy rule: if any child is not watched, this node needs a camera. Otherwise, if any child has a camera, this node is watched. Otherwise this node is not watched (its parent will have to cover it). At the end, an unwatched root needs one more camera."],
    editorial=["A camera on a leaf watches at most the leaf and its parent, while a camera on the leaf's parent watches those two plus the parent's other child and its own parent. So pushing cameras up, to the parents of leaves, is never worse. Applying this idea at every level gives a bottom-up greedy algorithm.",
               "Give every node a state: 0 = not watched, 1 = holds a camera, 2 = watched by a camera on a child. Missing children count as state 2 (they need no cover). For a node: if some child is in state 0, the node must hold a camera (state 1, count it); else if some child is in state 1, the node is state 2; else the node is state 0 and waits for its parent. After the pass, if the root is still in state 0, add one camera for it.",
               "The pass visits each node once. Because the array lists parents before children, running over the real nodes from last to first processes every child before its parent, with no recursion."],
    time="O(n)", space="O(n)",
    solution=LINKS + '''def minCameras(tree):
    vals, left, right = _links(tree)
    n = len(vals)
    if n == 0:
        return 0
    # 0 = not watched, 1 = holds a camera, 2 = watched by a child's camera
    state = [0] * n
    cameras = 0
    for k in range(n - 1, -1, -1):
        kids = [state[c] for c in (left[k], right[k]) if c != -1]
        if 0 in kids:
            state[k] = 1
            cameras += 1
        elif 1 in kids:
            state[k] = 2
        else:
            state[k] = 0
    return cameras + (1 if state[0] == 0 else 0)
''',
    tests=[[t] for t in BASE + _big(7009, 0) + [[0, 0, -1, 0, 0], [0, 0, -1, 0, -1, 0], [0, 0, 0, 0, -1, -1, 0, 0]]],
)


def _b_cam(tree):
    nodes = _preorder(_build(tree))
    n = len(nodes)
    if n == 0:
        return 0
    idx = {id(x): i for i, x in enumerate(nodes)}
    cover = [{i} for i in range(n)]
    for x in nodes:
        for c in (x.l, x.r):
            if c:
                cover[idx[id(x)]].add(idx[id(c)])
                cover[idx[id(c)]].add(idx[id(x)])
    for size in range(n + 1):
        for combo in combinations(range(n), size):
            seen = set()
            for i in combo:
                seen |= cover[i]
            if len(seen) == n:
                return size


CHECKS["binary-tree-minimum-cameras"] = (_b_cam, _gen(11, 0), "exact")
VALIDATE["binary-tree-minimum-cameras"] = _v_trees

# ---------------------------------------------------------------- max sum BST subtree
add(
    id="binary-tree-max-bst-subtree-sum", title="Maximum Sum BST in a Binary Tree", diff="Hard", topic="Trees",
    fn="maxBstSubtreeSum", params=[("tree", "int[]")], ret="int", cmp="exact",
    desc="<p>A <em>BST subtree</em> is a node together with all of its descendants such that, at every node inside it, all values in the left part are <strong>strictly smaller</strong> and all values in the right part are <strong>strictly larger</strong> than that node's value. A single node is always a BST subtree.</p>"
         "<p>Return the largest possible sum of the values in a BST subtree of the given tree. The empty tree gives <code>0</code>.</p>" + ENC +
         "<p>For <code>tree = [5, 3, 8, 2, 4, 7, 9]</code> the whole tree is a BST, so the answer is <code>38</code>. For <code>tree = [5, 3, 8, 2, 6, 7, 9]</code> the root is not valid because 6 lies in the left part of 5 but is larger than 5; the best BST subtree is the one rooted at 8 (8 + 7 + 9 = 24).</p>",
    constraints=_cons(["Duplicate values are allowed in the tree; a subtree containing equal values on a node's left or right side is not a BST subtree"]),
    hints=["For a node to root a BST subtree, it is not enough that its children are in order. Every value in its left part must be below it and every value in its right part above it.",
           "Work bottom-up. What would you like to know about each child's subtree to decide whether the node can join it into a larger BST?",
           "For every subtree keep: is it a BST, its minimum, its maximum and the sum of its values. A node roots a BST if both child subtrees are BSTs, <code>max(left) &lt; value</code> and <code>min(right) &gt; value</code>. Then its sum is <code>left + value + right</code>."],
    editorial=["Checking each node independently (validate the whole subtree, then sum it) takes O(n<sup>2</sup>) on skewed trees. Post-order information removes the repeated work.",
               "For every node, compute from its children whether its subtree is a BST, together with the minimum value, the maximum value and the sum of the subtree. A missing child is trivially fine. The node roots a BST exactly when every present child subtree is a BST, the left maximum is smaller than the node's value and the right minimum is larger than the node's value. In that case the subtree's minimum comes from the left side (or the node itself), the maximum from the right side (or the node itself), and the sum is the two child sums plus the node's value. Track the largest sum over all BST subtrees.",
               "Parents come before children in the level-order array, so a backwards pass over the real nodes visits children first and needs no recursion. Because values are non-negative, the answer is at least the largest single node, and it is 0 only for the empty tree."],
    time="O(n)", space="O(n)",
    solution=LINKS + '''def maxBstSubtreeSum(tree):
    vals, left, right = _links(tree)
    n = len(vals)
    ok = [False] * n
    lo = [0] * n
    hi = [0] * n
    total = [0] * n
    best = 0
    for k in range(n - 1, -1, -1):
        v = vals[k]
        good = True
        mn = mx = v
        s = v
        l, r = left[k], right[k]
        if l != -1:
            if ok[l] and hi[l] < v:
                mn = lo[l]
                s += total[l]
            else:
                good = False
        if r != -1:
            if ok[r] and lo[r] > v:
                mx = hi[r]
                s += total[r]
            else:
                good = False
        ok[k], lo[k], hi[k], total[k] = good, mn, mx, s
        if good and s > best:
            best = s
    return best
''',
    tests=[],
)
_ps = _P[-1]
_r = rnd(7010)
_ps["tests"] = [[t] for t in BASE + [
    [5, 3, 8, 2, 4, 7, 9], [5, 3, 8, 2, 6, 7, 9], [1, 4, 3, 2, 4, 2, 5, -1, -1, -1, -1, -1, -1, 4, 6],
    [4, 3, -1, 1, 2], [10, 5, 15, -1, -1, 6, 20],
    _bst(_r, MAXN, "random", 0), _bst(_r, MAXN, "left", 0), _bst(_r, MAXN, "right", 0), _bst(_r, MAXN, "complete", 0),
    _bst(_r, MAXN, "random", 1), _bst(_r, MAXN, "deep", 3), _bst(_r, MAXN, "complete", 10),
    _bst(_r, MAXN, "zig", 2), _tree(_r, MAXN, "random", 0, MAXV),
]]


def _b_bst(tree):
    best = 0
    for x in _preorder(_build(tree)):
        seq = [y.v for y in _inorder(x)]
        if all(a < b for a, b in zip(seq, seq[1:])):
            best = max(best, sum(seq))
    return best


def _g_bst(r):
    n = r.randint(0, 11)
    if r.random() < 0.8:
        return [_bst(r, n, r.choice(MODES), r.choice([0, 0, 1, 2, 3]), 30)]
    return [_tree(r, n, r.choice(MODES), 0, 6)]


CHECKS["binary-tree-max-bst-subtree-sum"] = (_b_bst, _g_bst, "exact")
VALIDATE["binary-tree-max-bst-subtree-sum"] = _v_trees
