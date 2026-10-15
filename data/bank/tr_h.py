"""Problems: binary trees, structure checks (identical, full, complete, flip equivalent, univalued, BST-ness, heap shape).

Tree encoding used by every problem here: level-order int[], -1 for a missing child,
children of missing nodes are not listed, trailing -1s are dropped, [] is the empty tree.
"""
import heapq
from collections import deque

from lib import add, rnd, CHECKS, VALIDATE, gen_arr  # noqa: F401
from lib import P as _P

MAXN = 1500      # maximum number of nodes in any tree
MAXV = 10000     # maximum node value
TOPIC = "Trees"

ENC = (
    "<p><strong>How trees are given.</strong> There is no tree type here. A binary tree is passed as an integer array in "
    "<em>level-order</em> (top to bottom, left to right), the same way LeetCode serialises trees. A missing child is written as "
    "<code>-1</code>, and every real node value is non-negative. The children of a missing node are not listed, and trailing "
    "<code>-1</code> entries are dropped, so a non-empty array never ends with <code>-1</code>. The empty tree is <code>[]</code>.</p>"
    "<p>For example, <code>[1, 2, 3, -1, 4]</code> describes the tree on the left: the root is 1 with children 2 and 3, node 2 has no left "
    "child and has 4 as its right child, and node 3 is a leaf.</p>"
    "<pre>    1\n   / \\\n  2   3\n   \\\n    4</pre>"
)


def _cons(extra=None, many=False):
    first = (f"0 &le; number of nodes in each tree &le; {MAXN:,}" if many else f"0 &le; number of nodes &le; {MAXN:,}")
    out = [first, f"0 &le; node value &le; {MAXV:,}",
           "Every tree array follows the encoding above exactly (valid level-order, no trailing -1)"]
    return out + (extra or [])


# ------------------------------------------------------------------ helpers (tests and brute forces only)
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


def _bfs(root):
    out, q = [], deque([root] if root else [])
    while q:
        x = q.popleft()
        out.append(x)
        if x.l:
            q.append(x.l)
        if x.r:
            q.append(x.r)
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
    """A valid strict BST shape (strictly increasing inorder) with `mut` random values overwritten."""
    root = _shape(r, n, mode)
    nodes = _inorder(root)
    for x, v in zip(nodes, sorted(r.sample(range(0, vmax + 1), n))):
        x.v = v
    for _ in range(mut if nodes else 0):
        r.choice(nodes).v = r.randint(0, vmax)
    return _encode(root)


def _full_tree(r, internal, lo=0, hi=MAXV, deep=False):
    """A full binary tree (every node has 0 or 2 children) with `internal` internal nodes."""
    root = _N(0)
    leaves = [root]
    for _ in range(internal):
        i = len(leaves) - 1 if deep else r.randrange(len(leaves))
        leaves[i], leaves[-1] = leaves[-1], leaves[i]
        x = leaves.pop()
        x.l, x.r = _N(0), _N(0)
        leaves.append(x.l)
        leaves.append(x.r)
    for x in _preorder(root):
        x.v = r.randint(lo, hi)
    return root


def _cut(root, r, k):
    """Detach k random non-root nodes together with everything below them."""
    for _ in range(k):
        nodes = _preorder(root)
        par = {}
        for x in nodes:
            for c in (x.l, x.r):
                if c:
                    par[id(c)] = x
        cand = [x for x in nodes if x is not root]
        if not cand:
            break
        x = r.choice(cand)
        p = par[id(x)]
        if p.l is x:
            p.l = None
        else:
            p.r = None
    return root


def _cut_leaf(root, r):
    nodes = _preorder(root)
    par = {}
    for x in nodes:
        for c in (x.l, x.r):
            if c:
                par[id(c)] = x
    cand = [x for x in nodes if x is not root and not x.l and not x.r]
    if cand:
        x = r.choice(cand)
        p = par[id(x)]
        if p.l is x:
            p.l = None
        else:
            p.r = None
    return root


def _flip_copy(root, r, p):
    """Copy of the tree where the children of each node are swapped with probability p."""
    if root is None:
        return None
    new = _N(root.v)
    st = [(root, new)]
    while st:
        a, b = st.pop()
        l, rr = a.l, a.r
        if r.random() < p:
            l, rr = rr, l
        if l:
            b.l = _N(l.v)
            st.append((l, b.l))
        if rr:
            b.r = _N(rr.v)
            st.append((rr, b.r))
    return new


def _change_value(arr, r, vmax):
    """Same tree with one value changed to a different value."""
    arr = list(arr)
    idx = [i for i, v in enumerate(arr) if v != -1]
    i = r.choice(idx)
    old = arr[i]
    while arr[i] == old:
        arr[i] = r.randint(0, vmax)
    return arr


def _complete_heap(r, n, vmax, cuts=0, mut=0):
    """Complete tree with n nodes holding a max-heap, then `cuts` subtrees removed and `mut` values overwritten."""
    root = _shape(r, n, "complete")
    nodes = _bfs(root)
    h = [-r.randint(0, vmax) for _ in nodes]
    heapq.heapify(h)
    for x, v in zip(nodes, h):
        x.v = -v
    _cut(root, r, cuts)
    pre = _preorder(root)
    for _ in range(mut if pre else 0):
        r.choice(pre).v = r.randint(0, vmax)
    return _encode(root)


def _mono_tree(r, n, mode, vmax, step):
    """Parent value >= child value everywhere (a heap-ordered tree of any shape)."""
    root = _shape(r, n, mode)
    if root is None:
        return []
    root.v = vmax
    for x in _preorder(root):
        for c in (x.l, x.r):
            if c:
                c.v = max(0, x.v - r.randint(0, step))
    return _encode(root)


def _v_trees(tests, trees=None):
    for t in tests:
        for k, arr in enumerate(t["args"]):
            if trees is not None and k not in trees:
                continue
            assert isinstance(arr, list) and all(isinstance(x, int) for x in arr)
            assert arr == _encode(_build(arr)), ("not a canonical level-order encoding", arr[:12])
            nodes = [x for x in arr if x != -1]
            assert len(nodes) <= MAXN, "too many nodes"
            assert all(0 <= x <= MAXV for x in nodes), "node value out of range"
            assert not arr or arr[0] != -1


def _both_answers(tests):
    outs = {t["expected"] for t in tests}
    assert outs == {True, False}, "tests should contain both true and false answers"


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

BASE = [
    [], [0], [1, 2, 3], [1, -1, 2, -1, 3], [1, 2, -1, 3, -1, 4], [3, 9, 20, -1, -1, 15, 7],
    [1, 2, 3, 4, 5, 6, 7], [1, 2, 2, 3, 3, -1, -1, 4, 4], [5, 5, 5, 5, 5, 5, 5, 5],
]


def _gen(nmax=10, vmax=5, modes=MODES):
    def g(r):
        return [_tree(r, r.randint(0, nmax), r.choice(modes), 0, vmax)]
    return g


# ================================================================== EASY

# ---------------------------------------------------------------- identical trees
add(
    id="identical-binary-trees", title="Are the Two Trees Identical?", diff="Easy", topic=TOPIC, tier="must",
    fn="isSameTree", params=[("a", "int[]"), ("b", "int[]")], ret="bool", cmp="exact",
    desc="<p>Two binary trees <code>a</code> and <code>b</code> are <em>identical</em> if they have exactly the same shape and every pair of nodes at the same position holds the same value. Return <code>true</code> if the two given trees are identical and <code>false</code> otherwise. Two empty trees are identical.</p>" + ENC +
         "<p>Both arguments use this encoding. For <code>a = [1, 2, 3]</code> and <code>b = [1, 2, 3]</code> the answer is <code>true</code>. For <code>a = [1, 2]</code> and <code>b = [1, -1, 2]</code> it is <code>false</code>: both trees hold the values 1 and 2, but 2 is the left child in one tree and the right child in the other.</p>",
    constraints=_cons(many=True),
    hints=["Two trees are identical when their roots hold the same value <em>and</em> their left subtrees are identical <em>and</em> their right subtrees are identical.",
           "Walk both trees at the same time. At each step you look at one node from each tree, and a missing node must only ever be matched with a missing node.",
           "Use a stack (or recursion) of node pairs starting with the two roots. Pop a pair: both missing is fine, exactly one missing or different values means the answer is false, otherwise push the pair of left children and the pair of right children."],
    editorial=["Identity is a recursive property. Two empty trees are identical; an empty tree and a non-empty tree are not; and two non-empty trees are identical exactly when their root values are equal and the left subtrees are identical and the right subtrees are identical. Translating this directly gives a function that visits each pair of positions at most once.",
               "The recursion can be turned into a loop with a stack of node pairs, which also avoids deep recursion on chain-shaped trees with 1,500 nodes. The work is proportional to the size of the smaller tree plus one, so it is O(n) time, and the stack holds O(n) pairs in the worst case.",
               "A shortcut specific to this encoding is that the canonical level-order array of a tree determines the tree uniquely, so comparing the two arrays element by element is also correct. The pair-walking version is the one that carries over to trees given as pointer-based nodes."],
    time="O(n)", space="O(n)",
    solution=LINKS + '''def isSameTree(a, b):
    va, la, ra = _links(a)
    vb, lb, rb = _links(b)
    if not va or not vb:
        return not va and not vb
    stack = [(0, 0)]
    while stack:
        x, y = stack.pop()
        if x == -1 and y == -1:
            continue
        if x == -1 or y == -1 or va[x] != vb[y]:
            return False
        stack.append((la[x], lb[y]))
        stack.append((ra[x], rb[y]))
    return True
''',
    tests=[],
)
_ps = _P[-1]
_r = rnd(8101)
_t1 = _tree(_r, MAXN, "random", 0, 3)
_t2 = _tree(_r, 1000, "zig", 0, 0)
_t3 = _tree(_r, 1000, "left", 0, 0)
_t4 = _tree(_r, 1000, "complete", 0, MAXV)
_ps["tests"] = [
    [[1, 2, 3], [1, 2, 3]], [[1, 2], [1, -1, 2]], [[], []], [[], [0]], [[7], []], [[1, 2, 1], [1, 1, 2]],
    [[3, 9, 20, -1, -1, 15, 7], [3, 9, 20, -1, -1, 15, 7]], [[3, 9, 20, -1, -1, 15, 7], [3, 9, 20, -1, -1, 15, 8]],
    [[1, 2, 3, 4], [1, 2, 3, -1, 4]], [[5, 5, 5, 5, 5, 5, 5, 5], [5, 5, 5, 5, 5, 5, 5]],
    [_t1, list(_t1)], [_t1, _change_value(_t1, _r, 3)], [_t2, _t3], [_t4, list(_t4)],
]


def _b_same(a, b):
    def same(x, y):
        if x is None or y is None:
            return x is None and y is None
        return x.v == y.v and same(x.l, y.l) and same(x.r, y.r)

    return same(_build(a), _build(b))


def _g_same(r):
    n = r.randint(0, 9)
    a = _tree(r, n, r.choice(MODES), 0, 2)
    k = r.random()
    if k < 0.4:
        return [a, list(a)]
    if k < 0.7 and a:
        return [a, _change_value(a, r, 2)]
    return [a, _tree(r, r.randint(0, 9), r.choice(MODES), 0, 2)]


CHECKS["identical-binary-trees"] = (_b_same, _g_same, "exact")


def _v_same(tests):
    _v_trees(tests)
    _both_answers(tests)


VALIDATE["identical-binary-trees"] = _v_same

# ---------------------------------------------------------------- univalued
add(
    id="univalued-binary-tree-check", title="Single-Valued Binary Tree", diff="Easy", topic=TOPIC, tier="extra",
    fn="isUnivalued", params=[("tree", "int[]")], ret="bool", cmp="exact",
    desc="<p>A binary tree is <em>univalued</em> if every node in it holds the same value. Return <code>true</code> if the given tree is univalued and <code>false</code> otherwise. The empty tree and a tree with a single node are univalued.</p>" + ENC +
         "<p>For <code>tree = [2, 2, 2, 2, 2]</code> the answer is <code>true</code>. For <code>tree = [2, 2, 2, 2, 5]</code> it is <code>false</code>, because the node 5 differs from the root.</p>",
    constraints=_cons(),
    hints=["What does every node have to be equal to? You do not need to compare nodes with their neighbours in a complicated way.",
           "Remember the value of the root, then visit all the other nodes in any order and compare each with it.",
           "Visit with a stack or queue, or simply scan the real nodes: the first node whose value differs from the root's value makes the answer false. Reaching the end means true."],
    editorial=["If all nodes are equal then in particular all are equal to the root, and the other way round: if every node equals the root value, they are all equal to each other. So the check is one pass over all nodes, comparing each with the root value, and it can stop at the first mismatch.",
               "Any traversal order works. With a recursive formulation, a node is the root of a univalued subtree if its children are missing or univalued with the same value; comparing with the single root value is simpler and needs no bookkeeping. This is the building block of the 'count univalue subtrees' problem, where you must decide it for every subtree."],
    time="O(n)", space="O(n)",
    solution=LINKS + '''def isUnivalued(tree):
    vals, left, right = _links(tree)
    if not vals:
        return True
    stack = [0]
    while stack:
        k = stack.pop()
        if vals[k] != vals[0]:
            return False
        if left[k] != -1:
            stack.append(left[k])
        if right[k] != -1:
            stack.append(right[k])
    return True
''',
    tests=[],
)
_ps = _P[-1]
_r = rnd(8102)
_u = _tree(_r, MAXN, "random", 7, 7)
_u2 = _tree(_r, MAXN, "zig", 9999, 9999)
_u2_bad = list(_u2)
_u2_bad[-1] = 10000
_ps["tests"] = [[t] for t in BASE] + [
    [[2, 2, 2, 2, 2]], [[2, 2, 2, 2, 5]], [[1, 1, 1, -1, 2]], [[0, 0, -1, 0, -1, 0]],
    [_u], [_change_value(_u, _r, 8)], [_u2], [_u2_bad],
]


def _b_uni(tree):
    seen = set()

    def go(x):
        if x:
            seen.add(x.v)
            go(x.l)
            go(x.r)

    go(_build(tree))
    return len(seen) <= 1


def _g_uni(r):
    n = r.randint(0, 9)
    if r.random() < 0.5:
        return [_tree(r, n, r.choice(MODES), 3, 3)] if r.random() < 0.6 else [_tree(r, n, r.choice(MODES), 0, 1)]
    t = _tree(r, n, r.choice(MODES), 3, 3)
    return [_change_value(t, r, 4)] if t else [t]


CHECKS["univalued-binary-tree-check"] = (_b_uni, _g_uni, "exact")


def _v_uni(tests):
    _v_trees(tests)
    _both_answers(tests)


VALIDATE["univalued-binary-tree-check"] = _v_uni

# ---------------------------------------------------------------- full
add(
    id="full-binary-tree-check", title="Full Binary Tree Check", diff="Easy", topic=TOPIC,
    fn="isFull", params=[("tree", "int[]")], ret="bool", cmp="exact",
    desc="<p>A binary tree is <em>full</em> if every node has either <strong>zero</strong> or <strong>two</strong> children. No node may have exactly one child. Return <code>true</code> if the given tree is full and <code>false</code> otherwise. The empty tree is full.</p>" + ENC +
         "<p>For <code>tree = [1, 2, 3, -1, -1, 4, 5]</code> the answer is <code>true</code>: node 1 has children 2 and 3, node 2 is a leaf, and node 3 has children 4 and 5. For <code>tree = [1, 2, 3, 4]</code> it is <code>false</code>, because node 2 has only a left child (4).</p>",
    constraints=_cons(),
    hints=["Look at one node at a time. Which combinations of 'has a left child' and 'has a right child' are allowed?",
           "Only 'none' and 'both' are allowed, so a node is bad exactly when its two child slots disagree: one is missing and the other is a real node.",
           "Visit every node (stack, queue or recursion) and return false at the first node with exactly one child. If none exists, return true."],
    editorial=["The condition is local: it can be checked at every node independently. For each node count its real children; the tree is full exactly when no node has a count of 1. Equivalently, <code>(left is missing) == (right is missing)</code> must hold at every node.",
               "In the level-order encoding you can do this with one scan of the structure: each real node owns two consecutive child slots, and a node is bad when exactly one of its two slots is <code>-1</code>. The work is one visit per node, so O(n) time; no extra structure beyond the traversal stack is needed."],
    time="O(n)", space="O(n)",
    solution=LINKS + '''def isFull(tree):
    vals, left, right = _links(tree)
    for k in range(len(vals)):
        if (left[k] == -1) != (right[k] == -1):
            return False
    return True
''',
    tests=[],
)
_ps = _P[-1]
_r = rnd(8103)


def _full_arr(r, internal, hi=MAXV, deep=False):
    return _encode(_full_tree(r, internal, 0, hi, deep))


_f1 = _full_arr(_r, 749, 5)
_f2 = _full_arr(_r, 700, 5, deep=True)
_f3 = _full_arr(_r, 749, MAXV)
_f1_bad = _encode(_cut_leaf(_build(_f1), _r))
_f2_bad = _encode(_cut_leaf(_build(_f2), _r))
_ps["tests"] = [[t] for t in BASE] + [
    [[1, 2, 3, -1, -1, 4, 5]], [[1, 2, 3, 4]], [[1, 2, 3, -1, -1, 4, 5, -1, -1, 6]], [[1, 2, 3, 4, 5, 6, 7, 8, 9]],
    [_f1], [_f1_bad], [_f2], [_f2_bad], [_f3],
]


def _b_full(tree):
    def go(x):
        if x is None:
            return True
        if (x.l is None) != (x.r is None):
            return False
        return go(x.l) and go(x.r)

    return go(_build(tree))


def _g_full(r):
    if r.random() < 0.5:
        root = _full_tree(r, r.randint(0, 4), 0, 3)
        if r.random() < 0.5:
            _cut_leaf(root, r)
        return [_encode(root)]
    return [_tree(r, r.randint(0, 9), r.choice(MODES), 0, 3)]


CHECKS["full-binary-tree-check"] = (_b_full, _g_full, "exact")


def _v_full(tests):
    _v_trees(tests)
    _both_answers(tests)


VALIDATE["full-binary-tree-check"] = _v_full

# ================================================================== MEDIUM

# ---------------------------------------------------------------- complete
add(
    id="complete-binary-tree-check", title="Is It a Complete Binary Tree?", diff="Medium", topic=TOPIC,
    fn="isComplete", params=[("tree", "int[]")], ret="bool", cmp="exact",
    desc="<p>A binary tree is <em>complete</em> if every level except possibly the last one is completely filled, and all nodes of the last level are as far left as possible. Equivalently, if you write the nodes level by level, left to right, there are no gaps: if the tree has <code>n</code> nodes they occupy exactly the positions <code>1..n</code> of a heap-style numbering (the root is position 1, and the children of position <code>i</code> are <code>2i</code> and <code>2i + 1</code>).</p>"
         "<p>Return <code>true</code> if the given tree is complete and <code>false</code> otherwise. The empty tree is complete.</p>" + ENC +
         "<p>For <code>tree = [1, 2, 3, 4, 5, 6]</code> the answer is <code>true</code>. For <code>tree = [1, 2, 3, 4, 5, -1, 7]</code> it is <code>false</code>: node 3 has a right child but no left child, so there is a gap before node 7.</p>",
    constraints=_cons(),
    hints=["Imagine reading the tree level by level, left to right, and writing down a node or a gap for every child slot. What may never happen after the first gap?",
           "In a complete tree all the real nodes come first and all the gaps after them. The moment you have seen one gap, no real node may follow.",
           "Do a breadth-first walk. Keep a flag 'seen a missing child'. Whenever you meet a missing child set the flag; whenever you meet a real node while the flag is set, return false. (Alternative: number the nodes like a heap and check that the largest number equals the node count.)"],
    editorial=["Do a breadth-first traversal that also enqueues missing children as placeholders. A tree is complete exactly when, in that sequence, once a placeholder has appeared, only placeholders follow. That is the 'no gap before a real node' rule written as a state machine with one boolean.",
               "The level-order input array is already exactly this sequence (each real node contributes its two child slots, and children of missing slots are not listed), so the scan can run directly on the array. In pointer-based form it is a standard BFS with a queue.",
               "A second view uses heap numbering: give the root index 1 and the children of index <code>i</code> the indices <code>2i</code> and <code>2i + 1</code>. The tree is complete if and only if the largest index equals the number of nodes. Both ways take O(n) time."],
    time="O(n)", space="O(n)",
    solution=LINKS + '''def isComplete(tree):
    vals, left, right = _links(tree)
    if not vals:
        return True
    order = [0]
    seen_gap = False
    head = 0
    while head < len(order):
        k = order[head]
        head += 1
        for c in (left[k], right[k]):
            if c == -1:
                seen_gap = True
            else:
                if seen_gap:
                    return False
                order.append(c)
    return True
''',
    tests=[],
)
_ps = _P[-1]
_r = rnd(8104)


def _cmp_tree(r, n, cut=0, vmax=MAXV):
    root = _shape(r, n, "complete")
    for x in _preorder(root or _N(0)):
        x.v = r.randint(0, vmax)
    return _encode(_cut(root, r, cut)) if root else []


_ps["tests"] = [[t] for t in BASE] + [
    [[1, 2, 3, 4, 5, 6]], [[1, 2, 3, 4, 5, -1, 7]], [[1, 2, 3, -1, 5]], [[1, 2]], [[1, -1, 2]],
    [[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16]],
    [_cmp_tree(_r, MAXN, 0, 9)], [_cmp_tree(_r, 1023, 0, 9)],
    [_cmp_tree(_r, MAXN, 1, 9)], [_cmp_tree(_r, MAXN - 1, 0, 9)],
    [_tree(_r, MAXN, "random", 0, 9)], [_tree(_r, MAXN, "left", 0, 9)],
]


def _b_complete(tree):
    root = _build(tree)
    if root is None:
        return True
    n = 0
    top = 0
    st = [(root, 1)]
    while st:
        x, i = st.pop()
        n += 1
        top = max(top, i)
        if x.l:
            st.append((x.l, 2 * i))
        if x.r:
            st.append((x.r, 2 * i + 1))
    return top == n


def _g_complete(r):
    k = r.random()
    if k < 0.45:
        n = r.randint(1, 10)
        root = _shape(r, n, "complete")
        if r.random() < 0.5:
            root = _cut(root, r, r.randint(1, 2))
        return [_encode(root)]
    if k < 0.6:
        return [_encode(_shape(r, r.randint(0, 9), "complete"))]
    return [_tree(r, r.randint(0, 9), r.choice(MODES), 0, 3)]


CHECKS["complete-binary-tree-check"] = (_b_complete, _g_complete, "exact")


def _v_complete(tests):
    _v_trees(tests)
    _both_answers(tests)


VALIDATE["complete-binary-tree-check"] = _v_complete

# ---------------------------------------------------------------- flip equivalent
add(
    id="flip-equivalent-binary-trees", title="Flip-Equivalent Binary Trees", diff="Medium", topic=TOPIC,
    fn="flipEquivalent", params=[("a", "int[]"), ("b", "int[]")], ret="bool", cmp="exact",
    desc="<p>A <em>flip</em> at a node swaps its left and right children (together with their whole subtrees); a missing child can be swapped with a real one too. Two binary trees <code>a</code> and <code>b</code> are <em>flip equivalent</em> if <code>a</code> can be turned into a tree identical to <code>b</code> by performing some number of flips, each at any node, possibly none.</p>"
         "<p>Return <code>true</code> if the two given trees are flip equivalent and <code>false</code> otherwise. Two empty trees are flip equivalent. Values may repeat, so you cannot match nodes by value alone.</p>" + ENC +
         "<p>Both arguments use this encoding. For <code>a = [1, 2, 3, 4]</code> and <code>b = [1, 3, 2, -1, -1, -1, 4]</code> the answer is <code>true</code>: flip the root of <code>a</code>, then flip node 2 so that its child 4 moves to the right. For <code>a = [1, 2, 3]</code> and <code>b = [1, 2, 4]</code> it is <code>false</code>, because no sequence of flips can change a value.</p>",
    constraints=_cons(many=True),
    hints=["Compare the two roots first. If their values differ, no flips can help. If they match, what are the only two ways their children can be paired up?",
           "Either the left subtree matches the left subtree and right matches right, or the left matches the right and right matches the left. Flips below can be chosen independently in each pair.",
           "With repeated values a naive 'try both pairings' recursion can take exponential time. Give every subtree a canonical id: the key (value, smaller child id, larger child id) looked up in a shared dictionary. Two subtrees are flip equivalent exactly when their ids are equal."],
    editorial=["Flipping a node only reorders its two children, so the set of trees reachable from a tree is determined by treating each node's children as an <em>unordered</em> pair. Two trees are flip equivalent exactly when, recursively, the root values are equal and the two child subtrees of one root can be matched with the two child subtrees of the other root in either order.",
               "The direct recursion <code>f(x, y) = (f(xl, yl) and f(xr, yr)) or (f(xl, yr) and f(xr, yl))</code> is fine when values are distinct, because then at most one pairing can have matching roots. With repeated values (for example two long chains of zeros, one leaning left and the other zig-zagging) both pairings may be tried at every level and the running time explodes.",
               "The robust solution assigns each subtree a canonical id bottom-up. The id of a node is looked up in one dictionary shared by both trees under the key <code>(value, min(leftId, rightId), max(leftId, rightId))</code>, with id 0 for a missing child. By induction two subtrees get the same id exactly when they are flip equivalent. The answer is whether the two root ids are equal. Every node is processed once: O(n + m) expected time."],
    time="O(n + m)", space="O(n + m)",
    solution=LINKS + '''def flipEquivalent(a, b):
    table = {}

    def root_id(t):
        vals, left, right = _links(t)
        out = [0] * len(vals)
        for k in range(len(vals) - 1, -1, -1):
            x = out[left[k]] if left[k] != -1 else 0
            y = out[right[k]] if right[k] != -1 else 0
            if x > y:
                x, y = y, x
            out[k] = table.setdefault((vals[k], x, y), len(table) + 1)
        return out[0] if out else 0

    return root_id(a) == root_id(b)
''',
    tests=[],
)
_ps = _P[-1]
_r = rnd(8105)
_fa = _tree(_r, MAXN, "random", 0, 2)
_fb = _encode(_flip_copy(_build(_fa), _r, 0.5))
_fc = _tree(_r, 1200, "random", 0, 1)
_fd = _encode(_flip_copy(_build(_fc), _r, 0.5))
_zl = _tree(_r, 1400, "left", 0, 0)
_zz = _tree(_r, 1400, "zig", 0, 0)
_zr = _tree(_r, 1400, "right", 0, 0)
_ps["tests"] = [
    [[1, 2, 3, 4], [1, 3, 2, -1, -1, -1, 4]], [[1, 2, 3], [1, 2, 4]], [[], []], [[], [1]], [[2], [2]],
    [[1, 2, 3], [1, 3, 2]], [[1, 2], [1, -1, 2]], [[1, 2, -1, 3], [1, -1, 2, -1, 3]],
    [[1, 2, 3, -1, 4], [1, 3, 2, 4]], [[0, 0, 0, 0], [0, 0, 0, -1, -1, 0]],
    [[5, 5, 5, 5, 5, 5, 5, 5], [5, 5, 5, 5, 5, 5, 5, 5]],
    [_fa, _fb], [_fa, _change_value(_fb, _r, 2)], [_fc, _fd],
    [_zl, _zz], [_zr, _zz], [_zl, _encode(_cut_leaf(_build(_zr), _r))],
]


def _b_flip(a, b):
    def f(x, y):
        if x is None or y is None:
            return x is None and y is None
        if x.v != y.v:
            return False
        return (f(x.l, y.l) and f(x.r, y.r)) or (f(x.l, y.r) and f(x.r, y.l))

    return f(_build(a), _build(b))


def _g_flip(r):
    a = _tree(r, r.randint(0, 9), r.choice(MODES), 0, 2)
    k = r.random()
    if k < 0.5:
        return [a, _encode(_flip_copy(_build(a), r, 0.5))]
    if k < 0.7 and a:
        return [a, _change_value(_encode(_flip_copy(_build(a), r, 0.5)), r, 2)]
    return [a, _tree(r, r.randint(0, 9), r.choice(MODES), 0, 2)]


CHECKS["flip-equivalent-binary-trees"] = (_b_flip, _g_flip, "exact")


def _v_flip(tests):
    _v_trees(tests)
    _both_answers(tests)


VALIDATE["flip-equivalent-binary-trees"] = _v_flip

# ---------------------------------------------------------------- count univalue subtrees
add(
    id="count-univalue-subtrees", title="Count Single-Valued Subtrees", diff="Medium", topic=TOPIC,
    fn="countUnivalueSubtrees", params=[("tree", "int[]")], ret="int", cmp="exact",
    desc="<p>Every node of a binary tree is the root of a <em>subtree</em> that consists of that node and all of its descendants. A subtree is <em>single-valued</em> if all of its nodes hold the same value. Return how many subtrees of the given tree are single-valued. Every leaf counts, and the empty tree has none.</p>" + ENC +
         "<p>For <code>tree = [1, 1, 1, 1, 2]</code> the answer is <code>3</code>: the two leaves holding 1 and the leaf holding 2. The left child of the root has children 1 and 2, and the root's subtree has two different values, so neither counts. For <code>tree = [4, 4, 4, 4, 4, -1, 4]</code> every one of the 6 subtrees is single-valued, so the answer is <code>6</code>.</p>",
    constraints=_cons(),
    hints=["A leaf is always single-valued. What do you need to know about the children of a node to decide about the node itself?",
           "A node's subtree is single-valued exactly when each of its existing children roots a single-valued subtree and has the same value as the node.",
           "Process nodes bottom-up (the reverse of level order works). Store one boolean per node, combine it from the children, and add one to a counter whenever the boolean is true."],
    editorial=["Decide the question for every node, children first. For a node with value <code>v</code> the subtree is single-valued if and only if every existing child is the root of a single-valued subtree <em>and</em> its value equals <code>v</code>. Missing children impose no condition. The count is the number of nodes for which this holds.",
               "Because children come after their parent in level order, walking the nodes from the last one to the first guarantees both children are decided before their parent, with no recursion needed (important for chain-shaped trees with 1,500 nodes). Each node is looked at once, so the algorithm is O(n) time and O(n) space.",
               "A common mistake is to check only <code>child.value == node.value</code> without requiring the child's whole subtree to be single-valued: in <code>[1, 1, 1, 1, 2]</code> the left child equals the root's value but its subtree contains a 2."],
    time="O(n)", space="O(n)",
    solution=LINKS + '''def countUnivalueSubtrees(tree):
    vals, left, right = _links(tree)
    n = len(vals)
    ok = [True] * n
    count = 0
    for k in range(n - 1, -1, -1):
        for c in (left[k], right[k]):
            if c != -1 and not (ok[c] and vals[c] == vals[k]):
                ok[k] = False
        if ok[k]:
            count += 1
    return count
''',
    tests=[],
)
_ps = _P[-1]
_r = rnd(8106)
_ps["tests"] = [[t] for t in BASE] + [
    [[1, 1, 1, 1, 2]], [[4, 4, 4, 4, 4, -1, 4]], [[1, 1, 2]], [[0, 0, 0, 1]],
    [_tree(_r, MAXN, "random", 0, 1)], [_tree(_r, MAXN, "complete", 0, 0)], [_tree(_r, MAXN, "left", 0, 1)],
    [_tree(_r, MAXN, "deep", 0, 2)], [_tree(_r, MAXN, "zig", 3, 3)],
]


def _b_univ(tree):
    def vals(x, acc):
        if x:
            acc.append(x.v)
            vals(x.l, acc)
            vals(x.r, acc)

    cnt = 0
    for x in _preorder(_build(tree)):
        acc = []
        vals(x, acc)
        cnt += len(set(acc)) == 1
    return cnt


CHECKS["count-univalue-subtrees"] = (_b_univ, _gen(10, 1), "exact")
VALIDATE["count-univalue-subtrees"] = _v_trees

# ---------------------------------------------------------------- duplicate subtrees
add(
    id="count-repeated-subtree-shapes", title="Count Repeated Subtrees", diff="Medium", topic=TOPIC,
    fn="countRepeatedSubtrees", params=[("tree", "int[]")], ret="int", cmp="exact",
    desc="<p>Two subtrees (a node together with all its descendants) are <em>the same</em> if they are identical in shape and in every node value. Count how many <strong>distinct</strong> subtrees occur at <strong>two or more</strong> different nodes of the given tree. Each distinct repeated subtree is counted once, however many copies exist. Leaves are subtrees too.</p>" + ENC +
         "<p>For <code>tree = [1, 2, 2, 3, -1, 3]</code> the answer is <code>2</code>: the subtree 'a lone 3' appears twice, and the subtree 'a 2 with a single left child 3' appears twice. The root is unique.</p>",
    constraints=_cons(),
    hints=["Comparing every pair of subtrees node by node is far too slow. Can a subtree be described by something short that is equal for equal subtrees?",
           "Describe a subtree by its root value together with descriptions of its left and right subtrees (and mark missing children). Two subtrees are equal exactly when their descriptions are equal.",
           "Replace the long text description by a small integer id: look up the triple (value, left id, right id) in a dictionary shared by all nodes, creating a new id when it is new. Count how many nodes get each id and count the ids that occur at least twice."],
    editorial=["Serialising every subtree as a string works but may cost O(n<sup>2</sup>) characters on chain-shaped trees. The fix is to avoid repeating the work for the children: if each child subtree already has a small integer id, the identity of a node is just the triple <code>(value, leftId, rightId)</code> with id 0 for a missing child.",
               "Process the nodes bottom-up and keep a dictionary from triples to ids. Two subtrees get the same id exactly when they are identical, by induction on the height. Count the occurrences of every id (a <code>Counter</code>) and return the number of ids occurring at least twice. Counting ids instead of nodes is what makes each repeated shape count once.",
               "Every node does one dictionary lookup, so the time is O(n) expected, and the dictionary holds at most n entries."],
    time="O(n)", space="O(n)",
    solution=LINKS + '''def countRepeatedSubtrees(tree):
    vals, left, right = _links(tree)
    n = len(vals)
    table = {}
    ids = [0] * n
    seen = {}
    for k in range(n - 1, -1, -1):
        lid = ids[left[k]] if left[k] != -1 else 0
        rid = ids[right[k]] if right[k] != -1 else 0
        ids[k] = table.setdefault((vals[k], lid, rid), len(table) + 1)
        seen[ids[k]] = seen.get(ids[k], 0) + 1
    return sum(1 for c in seen.values() if c >= 2)
''',
    tests=[],
)
_ps = _P[-1]
_r = rnd(8107)
_ps["tests"] = [[t] for t in BASE] + [
    [[1, 2, 2, 3, -1, 3]], [[1, 1]], [[1, 1, 1]], [[1, 2, 3, 4, 2, 4, 4, -1, -1, 4]],
    [_tree(_r, MAXN, "random", 0, 2)], [_tree(_r, MAXN, "complete", 0, 0)], [_tree(_r, MAXN, "left", 0, 1)],
    [_tree(_r, MAXN, "zig", 0, 0)], [_tree(_r, MAXN, "deep", 0, 1)],
]


def _b_rep(tree):
    from collections import Counter

    def ser(x):
        if x is None:
            return "#"
        return "(" + str(x.v) + ser(x.l) + "," + ser(x.r) + ")"

    c = Counter(ser(x) for x in _preorder(_build(tree)))
    return sum(1 for v in c.values() if v >= 2)


CHECKS["count-repeated-subtree-shapes"] = (_b_rep, _gen(11, 2), "exact")
VALIDATE["count-repeated-subtree-shapes"] = _v_trees

# ---------------------------------------------------------------- count BST subtrees
add(
    id="count-bst-subtrees", title="Count Subtrees That Are Valid BSTs", diff="Medium", topic=TOPIC, tier="extra",
    fn="countBstSubtrees", params=[("tree", "int[]")], ret="int", cmp="exact",
    desc="<p>A binary tree is a <em>binary search tree</em> (BST) if for every node all values in its left subtree are strictly smaller than the node's value and all values in its right subtree are strictly larger. The empty tree and a single node are BSTs.</p>"
         "<p>Every node of a given binary tree roots a <em>subtree</em> made of that node and all its descendants. Return the number of subtrees that are valid BSTs. Every leaf counts, and the whole tree counts if it is a BST.</p>" + ENC +
         "<p>For <code>tree = [10, 5, 15, 1, 8, -1, 7]</code> the answer is <code>4</code>: the leaves 1, 8 and 7, and the subtree rooted at 5 (children 1 and 8). The subtree rooted at 15 is not a BST since its right child 7 is smaller than 15, and the root is not a BST because it contains that subtree.</p>",
    constraints=_cons(),
    hints=["Testing each node separately by running a full BST validation on its subtree works, but may be quadratic on tall trees.",
           "For a node to root a BST both child subtrees must be BSTs, the largest value on the left must be smaller than the node, and the smallest value on the right must be larger. What two numbers do you need from each child subtree?",
           "Compute, bottom-up and once per node, whether the subtree is a BST together with its minimum and maximum value. Add one to the answer whenever the flag is true."],
    editorial=["The classic validation passes down lower and upper bounds, but here the question is asked for <em>every</em> subtree, so a bottom-up formulation is better. For each node keep three facts about its subtree: is it a BST, its minimum value and its maximum value.",
               "A node with value <code>v</code> roots a BST exactly when its left child (if any) roots a BST with maximum &lt; <code>v</code> and its right child (if any) roots a BST with minimum &gt; <code>v</code>. In that case the subtree minimum is the left child's minimum (or <code>v</code> if there is no left child) and the maximum is the right child's maximum (or <code>v</code>). If the node does not root a BST, mark it so; its ancestors then fail too, because a BST can only contain BST subtrees.",
               "Nodes are processed from the last in level order to the first so children are ready before parents. Each node is touched once: O(n) time and space. Strictness matters: equal values on either side make the subtree invalid."],
    time="O(n)", space="O(n)",
    solution=LINKS + '''def countBstSubtrees(tree):
    vals, left, right = _links(tree)
    n = len(vals)
    ok = [True] * n
    lo = list(vals)
    hi = list(vals)
    count = 0
    for k in range(n - 1, -1, -1):
        v = vals[k]
        a, b = left[k], right[k]
        if a != -1:
            if ok[a] and hi[a] < v:
                lo[k] = lo[a]
            else:
                ok[k] = False
        if b != -1:
            if ok[b] and lo[b] > v:
                hi[k] = hi[b]
            else:
                ok[k] = False
        if ok[k]:
            count += 1
    return count
''',
    tests=[],
)
_ps = _P[-1]
_r = rnd(8108)
_ps["tests"] = [[t] for t in BASE] + [
    [[10, 5, 15, 1, 8, -1, 7]], [[2, 1, 3]], [[2, 2, 3]], [[5, 1, 4, -1, -1, 3, 6]],
    [_bst(_r, MAXN, "random", 0)], [_bst(_r, MAXN, "random", 6)], [_bst(_r, MAXN, "left", 2)],
    [_bst(_r, MAXN, "zig", 0)], [_bst(_r, MAXN, "deep", 25)], [_tree(_r, MAXN, "complete", 0, 5)],
]


def _b_cbst(tree):
    def inorder_vals(x, acc):
        if x:
            inorder_vals(x.l, acc)
            acc.append(x.v)
            inorder_vals(x.r, acc)

    cnt = 0
    for x in _preorder(_build(tree)):
        acc = []
        inorder_vals(x, acc)
        cnt += all(acc[i] < acc[i + 1] for i in range(len(acc) - 1))
    return cnt


def _g_cbst(r):
    if r.random() < 0.7:
        return [_bst(r, r.randint(0, 10), r.choice(MODES), r.choice([0, 1, 1, 2]), 12)]
    return [_tree(r, r.randint(0, 9), r.choice(MODES), 0, 4)]


CHECKS["count-bst-subtrees"] = (_b_cbst, _g_cbst, "exact")
VALIDATE["count-bst-subtrees"] = _v_trees

# ---------------------------------------------------------------- downward path equals list
add(
    id="tree-contains-downward-value-path", title="Downward Path Spelling a Sequence", diff="Medium", topic=TOPIC, tier="extra",
    fn="hasDownwardPath", params=[("path", "int[]"), ("tree", "int[]")], ret="bool", cmp="exact",
    desc="<p>You are given a sequence <code>path</code> of values and a binary tree <code>tree</code>. Decide whether the tree contains a <em>downward path</em> whose node values, read from top to bottom, are exactly <code>path</code>. A downward path starts at any node, moves from a node to one of its children at every step, and may stop at any node (it does not have to end at a leaf).</p>"
         "<p>Return <code>true</code> if such a path exists and <code>false</code> otherwise. The empty tree contains no path.</p>" + ENC +
         "<p>The tree uses this encoding; <code>path</code> is an ordinary array of values. For <code>tree = [5, 2, 4, 1, 6, 3]</code> (root 5 with children 2 and 4; node 2 has children 1 and 6; node 4 has left child 3): <code>path = [2, 6]</code> gives <code>true</code>, <code>path = [5, 4, 3]</code> gives <code>true</code>, and <code>path = [2, 4]</code> gives <code>false</code> because 4 is not a child of 2.</p>",
    constraints=["1 &le; path.length &le; 800", f"0 &le; path[i] &le; {MAXV:,}", f"0 &le; number of nodes in tree &le; {MAXN:,}", f"0 &le; node value &le; {MAXV:,}",
                 "The tree array follows the encoding above exactly (valid level-order, no trailing -1)"],
    hints=["Try every node as the start of the path and walk down comparing with the sequence. That is correct; the question is how slow it gets when values repeat a lot.",
           "A downward path is a substring of some root-to-node path. So you can search for <code>path</code> as a pattern while walking down from the root, carrying the length of the longest suffix matched so far.",
           "Precompute the KMP failure table of <code>path</code>. During a depth-first walk keep the match length for each node (it is derived from its parent's match length), and answer true as soon as some node reaches a match length equal to <code>path.length</code>."],
    editorial=["The brute force starts a fresh comparison at every node and recurses into both children while the values keep matching. It is correct, but with many equal values (a long chain of zeros against a long list of zeros) it can compare close to <code>n &middot; m</code> pairs, which is acceptable at these limits but is the starting point for something better.",
               "Every downward path is a contiguous piece of a root-to-node path, so the task is string matching along the tree. Compute the KMP failure function of <code>path</code>. Walk the tree from the root; for each node derive its match length from its parent's match length by the usual KMP step (follow failure links while the next expected value differs, then extend by one when it matches). Different children of a node both start from the parent's state, which is why the state is stored per node (or passed down in the DFS stack) instead of in one global variable.",
               "If any node reaches match length <code>m = path.length</code>, the path exists. Each node does a number of failure hops bounded by its current match length, so the total is O(n + m) for typical inputs and never worse than O(n &middot; m); memory is O(n + m)."],
    time="O(n + m)", space="O(n + m)",
    solution=LINKS + '''def hasDownwardPath(path, tree):
    m = len(path)
    fail = [0] * m
    k = 0
    for i in range(1, m):
        while k and path[i] != path[k]:
            k = fail[k - 1]
        if path[i] == path[k]:
            k += 1
        fail[i] = k
    vals, left, right = _links(tree)
    if not vals:
        return False
    stack = [(0, 0)]
    while stack:
        x, s = stack.pop()
        v = vals[x]
        while s and path[s] != v:
            s = fail[s - 1]
        if path[s] == v:
            s += 1
        if s == m:
            return True
        for c in (left[x], right[x]):
            if c != -1:
                stack.append((c, s))
    return False
''',
    tests=[],
)
_ps = _P[-1]
_r = rnd(8109)


def _down_path(r, root, length):
    """Values along a random downward path of at most `length` nodes starting at a random node."""
    x = r.choice(_preorder(root))
    out = [x.v]
    while len(out) < length:
        kids = [c for c in (x.l, x.r) if c]
        if not kids:
            break
        x = r.choice(kids)
        out.append(x.v)
    return out


_tt = _tree(_r, MAXN, "random", 0, 1)
_tz = _tree(_r, MAXN, "deep", 0, 1)
_tc = _tree(_r, MAXN, "left", 0, 0)
_tc_broken = _build(_tc)
_nodes = _preorder(_tc_broken)
_nodes[1000].v = 1
_tc_broken = _encode(_tc_broken)
_ps["tests"] = [
    [[2, 6], [5, 2, 4, 1, 6, 3]], [[5, 4, 3], [5, 2, 4, 1, 6, 3]], [[2, 4], [5, 2, 4, 1, 6, 3]], [[5, 2], [5, 2, 4, 1, 6, 3]],
    [[1], []], [[1], [1]], [[1], [2]], [[1, 1], [1]], [[0, 0, 1], [0, 0, 0, 0, 1]],
    [[1, 2], [2, 1]], [[3, 3, 3], [3, 3, -1, 3, 3]],
    [[0] * 700, _tc], [[0] * 700, _tc_broken], [[0] * 400 + [1], _tc_broken],
    [_down_path(_r, _build(_tt), 25), _tt], [_down_path(_r, _build(_tz), 300), _tz], [[5] + _down_path(_r, _build(_tt), 20), _tt],
]


def _b_dpath(path, tree):
    root = _build(tree)
    if root is None:
        return False

    def go(x, i):
        if x is None or x.v != path[i]:
            return False
        if i == len(path) - 1:
            return True
        return go(x.l, i + 1) or go(x.r, i + 1)

    return any(go(x, 0) for x in _preorder(root))


def _g_dpath(r):
    t = _tree(r, r.randint(0, 10), r.choice(MODES), 0, 2)
    if t and r.random() < 0.6:
        p = _down_path(r, _build(t), r.randint(1, 5))
        if r.random() < 0.4:
            p[r.randrange(len(p))] = r.randint(0, 2)
        return [p, t]
    return [[r.randint(0, 2) for _ in range(r.randint(1, 4))], t]


CHECKS["tree-contains-downward-value-path"] = (_b_dpath, _g_dpath, "exact")


def _v_dpath(tests):
    _v_trees(tests, trees={1})
    for t in tests:
        p = t["args"][0]
        assert 1 <= len(p) <= 800 and all(0 <= x <= MAXV for x in p)
    _both_answers(tests)


VALIDATE["tree-contains-downward-value-path"] = _v_dpath

# ================================================================== HARD

# ---------------------------------------------------------------- largest max-heap subtree
add(
    id="largest-heap-shaped-subtree", title="Largest Max-Heap Subtree", diff="Hard", topic=TOPIC, tier="extra",
    fn="largestHeapSubtree", params=[("tree", "int[]")], ret="int", cmp="exact",
    desc="<p>A binary tree is a <em>max-heap tree</em> if it is <strong>complete</strong> (every level except possibly the last is full, and the last level is filled from the left without gaps) and every node's value is greater than or equal to the values of its children.</p>"
         "<p>Every node roots a <em>subtree</em> made of that node and all its descendants. Return the number of nodes in the largest subtree of the given tree that is a max-heap tree. A single node always is one, so for a non-empty tree the answer is at least 1; for the empty tree it is 0.</p>" + ENC +
         "<p>For <code>tree = [5, 8, 3, 4, 7]</code> the answer is <code>3</code>: the whole tree fails because 5 is smaller than its child 8, but the subtree rooted at 8 has children 4 and 7, is complete, and 8 &ge; 4, 7. For <code>tree = [6, 4, 5, 3, -1, 2, 1]</code> the answer is also <code>3</code>: the whole tree is not complete (node 4 has a missing right child but the level continues with 2 and 1), but the subtree rooted at 5 is a valid heap of size 3, and the subtree rooted at 4 only has 2 nodes.</p>",
    constraints=_cons(),
    hints=["Testing every node's subtree from scratch is correct but can cost O(n<sup>2</sup>) on tall trees. What small summary of a subtree would let its parent decide quickly whether it is a heap tree?",
           "A complete tree is described by its height and by two flags: 'complete' and 'perfect' (all levels full). The parent can be complete in exactly two ways: left complete and right perfect and the left is one level taller, or left perfect and right complete and both have equal heights.",
           "Bottom-up, store for each node: size, height, is-complete-heap, is-perfect-heap. A missing child is perfect and complete with height 0 and size 0. Add the heap-order test (node value &ge; the values of its existing children) and take the maximum size over nodes whose subtree is a complete heap."],
    editorial=["The two properties combine well bottom-up. For a node whose children subtrees are already summarised, the subtree is <em>complete</em> exactly in one of two situations. Either the left subtree is complete, the right subtree is perfect and the left height is one more than the right height (the last level is only partly filled, within the left part), or the left subtree is perfect, the right subtree is complete and both heights are equal (the last level is partly filled, reaching into the right part). A missing child counts as a perfect tree of height 0.",
               "The subtree is <em>perfect</em> when both children are perfect with equal heights. For heap order we only need to compare the node with its children's values: if the child subtrees are valid heap trees then their roots are their maxima, and so the node dominates everything below it as soon as it dominates its two children. It is important that a subtree is only accepted if the child subtrees are themselves valid heap trees, not merely complete.",
               "Keep a summary per node (size, height, complete-heap flag, perfect-heap flag), processing the nodes from last to first in level order so children come first, and record the largest size among nodes flagged as complete heaps. Each node costs O(1), giving O(n) time and space."],
    time="O(n)", space="O(n)",
    solution=LINKS + '''def largestHeapSubtree(tree):
    vals, left, right = _links(tree)
    n = len(vals)
    size = [1] * n
    height = [1] * n
    comp = [False] * n
    perf = [False] * n
    best = 0
    for k in range(n - 1, -1, -1):
        a, b = left[k], right[k]
        lc, lp, lh, ls = (comp[a], perf[a], height[a], size[a]) if a != -1 else (True, True, 0, 0)
        rc, rp, rh, rs = (comp[b], perf[b], height[b], size[b]) if b != -1 else (True, True, 0, 0)
        size[k] = 1 + ls + rs
        height[k] = 1 + max(lh, rh)
        order = (a == -1 or vals[a] <= vals[k]) and (b == -1 or vals[b] <= vals[k])
        if order:
            perf[k] = lp and rp and lh == rh
            comp[k] = (lc and rp and lh == rh + 1) or (lp and rc and lh == rh)
        if comp[k]:
            best = max(best, size[k])
    return best
''',
    tests=[],
)
_ps = _P[-1]
_r = rnd(8110)
_ps["tests"] = [[t] for t in BASE] + [
    [[5, 8, 3, 4, 7]], [[6, 4, 5, 3, -1, 2, 1]], [[9, 9, 9, 9, 9, 9, 9]], [[3, 1, 2, 5]],
    [_complete_heap(_r, MAXN, MAXV)], [_complete_heap(_r, MAXN, 50, cuts=3)], [_complete_heap(_r, MAXN, 20, cuts=1, mut=40)],
    [_mono_tree(_r, MAXN, "random", MAXV, 3)], [_mono_tree(_r, MAXN, "left", MAXV, 3)],
    [_tree(_r, MAXN, "complete", 0, 0)], [_tree(_r, MAXN, "random", 0, 9)],
]


def _b_heap(tree):
    def vals_of(x, acc):
        # heap-numbered list of (index, value) pairs for the subtree
        st = [(x, 1)]
        while st:
            y, i = st.pop()
            acc[i] = y.v
            if y.l:
                st.append((y.l, 2 * i))
            if y.r:
                st.append((y.r, 2 * i + 1))

    best = 0
    for x in _preorder(_build(tree)):
        acc = {}
        vals_of(x, acc)
        n = len(acc)
        if max(acc) != n:
            continue
        if all(acc[i] <= acc[i // 2] for i in acc if i > 1):
            best = max(best, n)
    return best


def _g_heap(r):
    k = r.random()
    if k < 0.45:
        return [_complete_heap(r, r.randint(0, 12), 6, cuts=r.choice([0, 1, 1, 2]), mut=r.choice([0, 0, 1, 2]))]
    if k < 0.7:
        return [_mono_tree(r, r.randint(0, 10), r.choice(MODES), 6, 2)]
    return [_tree(r, r.randint(0, 9), r.choice(MODES), 0, 3)]


CHECKS["largest-heap-shaped-subtree"] = (_b_heap, _g_heap, "exact")
VALIDATE["largest-heap-shaped-subtree"] = _v_trees

# ---------------------------------------------------------------- minimum value edits to make a BST
add(
    id="min-value-edits-to-make-bst", title="Fewest Value Changes to Make a BST", diff="Hard", topic=TOPIC, tier="extra",
    fn="minEditsToBst", params=[("tree", "int[]")], ret="int", cmp="exact",
    desc="<p>You may change the value stored in any node of a binary tree to <em>any integer</em> (negative values and values above 10,000 are allowed), but you may not change the shape of the tree. A tree is a valid <em>binary search tree</em> when for every node all values in its left subtree are strictly smaller than the node's value and all values in its right subtree are strictly larger.</p>"
         "<p>Return the minimum number of nodes whose value has to be changed so that the tree becomes a valid BST. If it already is one, the answer is 0.</p>" + ENC +
         "<p>For <code>tree = [3, 1, 2]</code> (root 3, left child 1, right child 2) the answer is <code>1</code>: change the 2 to 4. For <code>tree = [2, 2, 2]</code> the answer is <code>2</code>, because a BST has distinct values and at most one of the 2s can stay. For <code>tree = [4, 2, 6, 1, 3, 5, 7]</code> the answer is <code>0</code>.</p>",
    constraints=_cons(),
    hints=["A tree is a strict BST exactly when its inorder sequence is strictly increasing, so only the inorder sequence matters, not the shape. The problem becomes: change the fewest entries of an array so that it is strictly increasing.",
           "Choose a set of entries to keep. Between two kept entries at positions <code>i &lt; j</code> there must be room for <code>j - i - 1</code> distinct integers, which means <code>a[j] - a[i] &ge; j - i</code>. Entries before the first and after the last kept one have unlimited room because any integer is allowed.",
           "The condition <code>a[j] - j &ge; a[i] - i</code> says that the numbers <code>b[i] = a[i] - i</code> of the kept entries form a non-decreasing subsequence. Maximise its length (longest non-decreasing subsequence with binary search, O(n log n)); the answer is <code>n</code> minus that length."],
    editorial=["Reduce to an array. A binary tree is a strict BST if and only if its inorder traversal is strictly increasing, and the shape does not change, so the nodes keep their positions in the inorder order. Let <code>a[0..n-1]</code> be the inorder values. We want the largest set of positions that can keep their values; all others are changed (and changing a node is allowed to produce any integer, so changed nodes are never the bottleneck).",
               "Kept positions <code>i &lt; j</code> that are neighbours in the kept set need <code>j - i - 1</code> distinct integers strictly between <code>a[i]</code> and <code>a[j]</code> for the changed nodes between them, which is possible exactly when <code>a[j] - a[i] &ge; j - i</code>, i.e. <code>a[j] - j &ge; a[i] - i</code>. Before the first kept and after the last kept position there is no limit. Checking neighbouring kept pairs is enough, since the condition is transitive.",
               "So the kept positions form a non-decreasing subsequence of <code>b[i] = a[i] - i</code>. The longest non-decreasing subsequence is computed in O(n log n) with the patience-sorting array and <code>bisect_right</code>, and the answer is <code>n</code> minus its length. Producing the inorder sequence takes an iterative traversal in O(n). Note that equal inorder values give strictly decreasing <code>b</code>, so at most one of them can be kept."],
    time="O(n log n)", space="O(n)",
    solution=LINKS + '''from bisect import bisect_right


def minEditsToBst(tree):
    vals, left, right = _links(tree)
    if not vals:
        return 0
    order = []
    stack = []
    x = 0
    while stack or x != -1:
        while x != -1:
            stack.append(x)
            x = left[x]
        x = stack.pop()
        order.append(vals[x])
        x = right[x]
    tails = []
    for i, v in enumerate(order):
        b = v - i
        j = bisect_right(tails, b)
        if j == len(tails):
            tails.append(b)
        else:
            tails[j] = b
    return len(order) - len(tails)
''',
    tests=[],
)
_ps = _P[-1]
_r = rnd(8111)
_ps["tests"] = [[t] for t in BASE] + [
    [[3, 1, 2]], [[2, 2, 2]], [[4, 2, 6, 1, 3, 5, 7]], [[1, 1, 2]], [[2, 1, 1]], [[1, 2, 3, 4, 5]],
    [_bst(_r, MAXN, "random", 0)], [_bst(_r, MAXN, "random", 30)], [_bst(_r, MAXN, "left", 400)],
    [_tree(_r, MAXN, "random", 0, MAXV)], [_tree(_r, MAXN, "complete", 0, 0)], [_tree(_r, MAXN, "zig", 0, 1500)],
]


def _b_edits(tree):
    root = _build(tree)
    a = [x.v for x in _inorder(root)]
    n = len(a)
    best = n
    for mask in range(1 << n):
        cur = None
        ok = True
        for i in range(n):
            if mask >> i & 1:  # kept
                if cur is not None and a[i] <= cur:
                    ok = False
                    break
                cur = a[i]
            elif cur is not None:  # changed: take the smallest value that still works
                cur += 1
        if ok:
            best = min(best, n - bin(mask).count("1"))
    return best


def _g_edits(r):
    if r.random() < 0.6:
        return [_bst(r, r.randint(0, 9), r.choice(MODES), r.choice([0, 1, 2, 3]), 12)]
    return [_tree(r, r.randint(0, 9), r.choice(MODES), 0, 5)]


CHECKS["min-value-edits-to-make-bst"] = (_b_edits, _g_edits, "exact")
VALIDATE["min-value-edits-to-make-bst"] = _v_trees
