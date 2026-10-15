"""Problems: building and converting binary trees (level-order encoding, -1 for a missing child). See data/lib.py for the registry."""
import re
from collections import deque

from lib import add, rnd, CHECKS, VALIDATE, gen_arr  # noqa: F401
from lib import P as _P

TOPIC = "Trees"
MAXN = 1500      # maximum number of nodes in any tree
MAXV = 10000     # maximum node value
MOD = 1_000_000_007

ENC = (
    "<p><strong>How trees are given.</strong> There is no tree type here. A binary tree is passed (or returned) as an integer array in "
    "<em>level-order</em> (top to bottom, left to right), the same way LeetCode serialises trees. A missing child is written as "
    "<code>-1</code>, and every real node value is non-negative. The children of a missing node are not listed, and trailing "
    "<code>-1</code> entries are dropped, so a non-empty array never ends with <code>-1</code>. The empty tree is <code>[]</code>.</p>"
    "<p>For example, <code>[1, 2, 3, -1, 4]</code> describes the tree below: the root is 1 with children 2 and 3, node 2 has no left "
    "child and has 4 as its right child, and node 3 is a leaf.</p>"
    "<pre>    1\n   / \\\n  2   3\n   \\\n    4</pre>"
)


def _cons(extra=None, what="number of nodes"):
    out = [f"0 &le; {what} &le; {MAXN:,}", f"0 &le; node value &le; {MAXV:,}",
           "Every tree array follows the encoding above exactly (valid level-order, no trailing -1)"]
    return out + (extra or [])


# ------------------------------------------------------------------ helpers (nodes, traversals, shapes)
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


def _postorder(root):
    out, st = [], ([root] if root else [])
    while st:
        x = st.pop()
        out.append(x)
        if x.l:
            st.append(x.l)
        if x.r:
            st.append(x.r)
    return out[::-1]


def _vals(nodes):
    return [x.v for x in nodes]


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


def _shape_depth(r, n, maxd):
    """Random shape with n nodes and at most maxd levels."""
    if n == 0:
        return None
    root = _N(0)
    free = [(root, 0, 2), (root, 1, 2)] if maxd >= 2 else []
    for _ in range(n - 1):
        i = r.randrange(len(free))
        free[i], free[-1] = free[-1], free[i]
        node, side, d = free.pop()
        c = _N(0)
        if side == 0:
            node.l = c
        else:
            node.r = c
        if d < maxd:
            free.append((c, 0, d + 1))
            free.append((c, 1, d + 1))
    return root


def _full_shape(r, n, mode="random"):
    """A full binary tree (every node has 0 or 2 children) with n (odd) nodes."""
    assert n % 2 == 1
    root = _N(0)
    leaves = deque([root])
    cnt = 1
    while cnt < n:
        if mode == "complete":
            x = leaves.popleft()
        elif mode == "deep":
            x = leaves.pop()
        else:
            i = r.randrange(len(leaves))
            leaves[i], leaves[-1] = leaves[-1], leaves[i]
            x = leaves.pop()
        x.l, x.r = _N(0), _N(0)
        if mode == "deep" and r.random() < 0.5:
            leaves.append(x.l)
            leaves.append(x.r)
        else:
            leaves.append(x.r)
            leaves.append(x.l)
        cnt += 2
    return root


MODES = ["random", "random", "deep", "complete", "left", "right", "zig"]


def _fill(r, root, lo=0, hi=MAXV):
    for x in _preorder(root):
        x.v = r.randint(lo, hi)
    return root


def _fill_distinct(r, root, n):
    for x, v in zip(_preorder(root), r.sample(range(MAXV + 1), n)):
        x.v = v
    return root


def _tree(r, n, mode="random", lo=0, hi=MAXV):
    return _encode(_fill(r, _shape(r, n, mode), lo, hi))


def _dtree_obj(r, n, mode="random"):
    return _fill_distinct(r, _shape(r, n, mode), n)


def _dtree(r, n, mode="random"):
    return _encode(_dtree_obj(r, n, mode))


def _v_enc(arr):
    assert isinstance(arr, list) and all(isinstance(x, int) for x in arr)
    assert arr == _encode(_build(arr)), ("not a canonical level-order encoding", arr[:12])
    nodes = [x for x in arr if x != -1]
    assert len(nodes) <= MAXN, "too many nodes"
    assert all(0 <= x <= MAXV for x in nodes), "node value out of range"


def _depth(arr):
    root = _build(arr)
    best, st = 0, ([(root, 1)] if root else [])
    while st:
        x, d = st.pop()
        best = max(best, d)
        for c in (x.l, x.r):
            if c:
                st.append((c, d + 1))
    return best


def _v_trees(tests):
    for t in tests:
        for arr in t["args"]:
            _v_enc(arr)


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


'''

# Level-order encoding of a tree stored as arrays (node ids index vals/left/right, -1 = none).
ENCODE = '''def _encode(vals, left, right, root):
    if root == -1:
        return []
    out = []
    q = [root]
    for x in q:
        if x == -1:
            out.append(-1)
        else:
            out.append(vals[x])
            q.append(left[x])
            q.append(right[x])
    while out and out[-1] == -1:
        out.pop()
    return out


'''

SMALL = [
    [], [7], [3, 9, 20, -1, -1, 15, 7], [1, 2, -1, 3], [1, -1, 2, -1, 3], [1, 2, 3, 4, 5, 6, 7], [4, 2, 7, 1, 3, 6, 9],
    [5, 3, 8, 1, -1, -1, 9], [10, 20, -1, -1, 30], [8, 4, -1, 2, -1, 1, -1, 6, 3],
]


# ================================================================== EASY

# ---------------------------------------------------------------- mirror
add(
    id="mirror-binary-tree-level-order", title="Mirror a Binary Tree", diff="Easy", topic=TOPIC,
    fn="mirrorTree", params=[("tree", "int[]")], ret="int[]", cmp="exact",
    desc="<p>Mirror a binary tree: swap the left and right child of <em>every</em> node, so that the whole tree is reflected left to right. Return the mirrored tree.</p>" + ENC +
         "<p>The result must use the same encoding. For <code>tree = [4, 2, 7, 1, 3, 6, 9]</code> the answer is <code>[4, 7, 2, 9, 6, 3, 1]</code>. For <code>tree = [1, 2, -1, 3]</code> (a chain going down to the left) the answer is <code>[1, -1, 2, -1, 3]</code> (a chain going down to the right).</p>",
    constraints=_cons(),
    hints=["Look at what mirroring does to one single node, and then think about what it does to the subtrees below it.",
           "Mirroring a tree means: swap the two children, then mirror the left subtree and mirror the right subtree.",
           "Do it with recursion or an explicit stack/queue that visits every node once. Remember to write the answer back in level-order with <code>-1</code> for gaps and without trailing <code>-1</code>s."],
    editorial=["The mirror image of a tree is built from the mirror images of its subtrees: the new left child is the mirror of the old right subtree and the new right child is the mirror of the old left subtree. So a single pass that swaps the two children of every node does the whole job, in any visiting order (preorder, postorder or level by level).",
               "With the array encoding the work is mostly bookkeeping. Read the tree into per-node child links, exchange the two link arrays, and write the tree back in level order, dropping the trailing <code>-1</code> entries. Each node is touched a constant number of times, so the time is linear."],
    time="O(n)", space="O(n)",
    solution=LINKS + ENCODE + '''def mirrorTree(tree):
    vals, left, right = _links(tree)
    if not vals:
        return []
    # swapping the child links of every node mirrors the tree
    return _encode(vals, right, left, 0)
''',
    tests=[],
)


def _tests_mirror():
    r = rnd(8101)
    t = [[e] for e in SMALL]
    t.append([_tree(r, 12, "random", 0, 99)])
    t.append([_tree(r, MAXN, "left")])
    t.append([_tree(r, MAXN, "random")])
    t.append([_tree(r, MAXN, "complete")])
    return t


def _b_mirror(tree):
    def m(x):
        if x is None:
            return None
        x.l, x.r = m(x.r), m(x.l)
        return x
    return _encode(m(_build(tree)))


def _g_tree(nmax=10, vmax=5):
    def g(r):
        return [_tree(r, r.randint(0, nmax), r.choice(MODES), 0, vmax)]
    return g


def _v_mirror(tests):
    _v_trees(tests)
    for t in tests:
        _v_enc(t["expected"])
        a, b = _preorder(_build(t["args"][0])), _preorder(_build(t["expected"]))
        assert sorted(_vals(a)) == sorted(_vals(b))


_P[-1]["tests"] = _tests_mirror()
CHECKS["mirror-binary-tree-level-order"] = (_b_mirror, _g_tree(), "exact")
VALIDATE["mirror-binary-tree-level-order"] = _v_mirror

# ---------------------------------------------------------------- serialize with null markers
add(
    id="serialize-binary-tree-null-markers", title="Serialize a Binary Tree with Null Markers", diff="Easy", topic=TOPIC,
    fn="serializePreorder", params=[("tree", "int[]")], ret="int[]", cmp="exact",
    desc="<p>Convert a binary tree into its <em>preorder serialization with null markers</em>. Visit the tree in preorder (node, then the whole left subtree, then the whole right subtree). Write the value of every real node, and write <code>-1</code> every time you reach a missing child. Missing children are written for <em>every</em> node that lacks them, including the ones at the very end, so the result is a complete description of the tree.</p>" + ENC +
         "<p>The input uses the level-order encoding above; the output is the preorder serialization. For <code>tree = [1, 2, 3, -1, 4]</code> the answer is <code>[1, 2, -1, 4, -1, -1, 3, -1, -1]</code>. The empty tree serializes to <code>[-1]</code>, and the single node <code>[7]</code> to <code>[7, -1, -1]</code>.</p>",
    constraints=_cons(),
    hints=["First list the nodes in preorder. Then think about where the markers must go.",
           "A preorder visit that also visits missing children naturally produces the markers: when the recursion is called on an empty child, output <code>-1</code> and return.",
           "A tree with n nodes has exactly n + 1 missing child slots, so the answer has 2n + 1 entries. Use an explicit stack if you worry about deep trees: pop an item, output it; if it is a node push its right child and then its left child (pushing <code>-1</code> markers for missing ones)."],
    editorial=["Preorder with markers is a recursive definition: <code>ser(empty) = [-1]</code> and <code>ser(node) = [value] + ser(left) + ser(right)</code>. Every node and every empty slot is emitted exactly once, so the output length is 2n + 1 and the time is linear.",
               "Because a tree can be a chain of 1,500 nodes, an iterative version with a stack avoids recursion-depth problems: pop an entry, emit it, and for a real node push the right child first and then the left child, so the left subtree is processed first. This is also the format the next problem in this set (deserialization) reads back."],
    time="O(n)", space="O(n)",
    solution=LINKS + '''def serializePreorder(tree):
    vals, left, right = _links(tree)
    out = []
    stack = [0 if vals else -1]
    while stack:
        k = stack.pop()
        if k == -1:
            out.append(-1)
            continue
        out.append(vals[k])
        stack.append(right[k])
        stack.append(left[k])
    return out
''',
    tests=[],
)


def _tests_serialize():
    r = rnd(8201)
    t = [[e] for e in SMALL]
    t.append([_tree(r, 15, "random", 0, 99)])
    t.append([_tree(r, MAXN, "zig")])
    t.append([_tree(r, MAXN, "random")])
    t.append([_tree(r, MAXN, "deep")])
    return t


def _pre_nulls(root):
    out, st = [], [root]
    while st:
        x = st.pop()
        if x is None:
            out.append(-1)
            continue
        out.append(x.v)
        st.append(x.r)
        st.append(x.l)
    return out


def _b_serialize(tree):
    return _pre_nulls(_build(tree))


def _v_serialize(tests):
    _v_trees(tests)
    for t in tests:
        n = sum(1 for x in t["args"][0] if x != -1)
        assert len(t["expected"]) == 2 * n + 1


_P[-1]["tests"] = _tests_serialize()
CHECKS["serialize-binary-tree-null-markers"] = (_b_serialize, _g_tree(8, 6), "exact")
VALIDATE["serialize-binary-tree-null-markers"] = _v_serialize

# ---------------------------------------------------------------- heap-indexed array
add(
    id="binary-tree-heap-indexed-array", title="Heap-Indexed Array of a Binary Tree", diff="Easy", topic=TOPIC,
    fn="heapIndexed", params=[("tree", "int[]")], ret="int[]", cmp="exact",
    desc="<p>A binary tree can be stored in an array the way a binary heap is: the root sits at index <code>0</code>, and the node at index <code>i</code> keeps its left child at index <code>2i + 1</code> and its right child at index <code>2i + 2</code>. Slots that belong to no node contain <code>-1</code>, and the array ends at the last real node (so its last entry is never <code>-1</code>).</p>"
         "<p>Given a tree in the usual level-order encoding, return its heap-indexed array. The empty tree gives <code>[]</code>.</p>" + ENC +
         "<p>For <code>tree = [1, -1, 2, -1, 3]</code> (a chain that always goes right) the root is at index 0, node 2 at index 2 and node 3 at index 6, so the answer is <code>[1, -1, 2, -1, -1, -1, 3]</code>. For a perfect tree such as <code>[1, 2, 3, 4, 5, 6, 7]</code> the answer is the same array.</p>",
    constraints=_cons(["The tree has at most 12 levels (so the answer has at most 4,095 entries)"]),
    hints=["Every node has a fixed position in the heap layout that depends only on the path from the root to it.",
           "If a node is at index i, its children are at 2i + 1 and 2i + 2. So you only need to know the index of each node's parent.",
           "Walk through the nodes in level order. Parents always come before their children, so you can compute each child's index when you process the parent, then allocate an array of size (largest index + 1) filled with <code>-1</code>."],
    editorial=["Both encodings list the real nodes in level order, so converting between them is a bookkeeping exercise: find the parent of each node, apply <code>2i + 1</code> or <code>2i + 2</code>, and drop the value into an array that was pre-filled with <code>-1</code>.",
               "The children of the k-th real node occupy the slots <code>2k + 1</code> and <code>2k + 2</code> of the compact array, which tells us who the parent of every node is. The largest heap index belongs to a real node, so the array length is exactly that index plus one. The depth limit keeps the output small: a long right chain would otherwise need an exponentially large array, which is the reason heap layouts are only used for balanced-ish trees."],
    time="O(n + output size)", space="O(output size)",
    solution=LINKS + '''def heapIndexed(tree):
    vals, left, right = _links(tree)
    if not vals:
        return []
    idx = [0] * len(vals)
    for k in range(len(vals)):  # parents come before their children in level order
        if left[k] != -1:
            idx[left[k]] = 2 * idx[k] + 1
        if right[k] != -1:
            idx[right[k]] = 2 * idx[k] + 2
    out = [-1] * (max(idx) + 1)
    for k, i in enumerate(idx):
        out[i] = vals[k]
    return out
''',
    tests=[],
)


def _tests_heap():
    r = rnd(8301)
    t = [[e] for e in SMALL]
    t.append([[1, 2, 3, 4, 5, 6, 7]])
    z = _tree(r, 12, "zig")
    t.append([z])
    t.append([_encode(_fill(r, _shape_depth(r, 300, 12)))])
    t.append([_encode(_fill(r, _shape_depth(r, MAXN, 12)))])
    t.append([_encode(_fill(r, _shape_depth(r, MAXN, 11)))])
    return t


def _b_heap(tree):
    res = {}

    def rec(x, i):
        if x is None:
            return
        res[i] = x.v
        rec(x.l, 2 * i + 1)
        rec(x.r, 2 * i + 2)
    rec(_build(tree), 0)
    if not res:
        return []
    return [res.get(i, -1) for i in range(max(res) + 1)]


def _g_heap(r):
    return [_encode(_fill(r, _shape_depth(r, r.randint(0, 10), 5), 0, 9))]


def _v_heap(tests):
    _v_trees(tests)
    for t in tests:
        assert _depth(t["args"][0]) <= 12
        e = t["expected"]
        assert len(e) <= 4095 and (not e or e[-1] != -1)


_P[-1]["tests"] = _tests_heap()
CHECKS["binary-tree-heap-indexed-array"] = (_b_heap, _g_heap, "exact")
VALIDATE["binary-tree-heap-indexed-array"] = _v_heap

# ================================================================== MEDIUM

# ---------------------------------------------------------------- preorder + inorder
CON_TRAV = ["0 &le; n &le; 1,500", f"0 &le; value &le; {MAXV:,}", "All values are distinct"]


def _trav_cons(a, b):
    return CON_TRAV + [f"<code>{b}</code> is a permutation of <code>{a}</code>, and both traversals come from the same binary tree"]


add(
    id="construct-tree-from-preorder-inorder", title="Build a Binary Tree from Preorder and Inorder", diff="Medium", topic=TOPIC, tier="must",
    fn="buildTree", params=[("preorder", "int[]"), ("inorder", "int[]")], ret="int[]", cmp="exact",
    desc="<p>You are given the <em>preorder</em> traversal (node, left subtree, right subtree) and the <em>inorder</em> traversal (left subtree, node, right subtree) of a binary tree whose node values are all distinct. Rebuild the tree and return it in level-order encoding.</p>" + ENC +
         "<p>For <code>preorder = [3, 9, 20, 15, 7]</code> and <code>inorder = [9, 3, 15, 20, 7]</code> the answer is <code>[3, 9, 20, -1, -1, 15, 7]</code>. For <code>preorder = [1, 2, 3]</code> and <code>inorder = [3, 2, 1]</code> the tree is a chain going down to the left, and the answer is <code>[1, 2, -1, 3]</code>.</p>"
         "<p>With distinct values the two traversals determine the tree uniquely. Both arrays are empty for the empty tree, whose answer is <code>[]</code>.</p>",
    constraints=_trav_cons("preorder", "inorder"),
    hints=["Which element of the preorder array is the root of the whole tree?",
           "Find the root in the inorder array. Everything to its left is the left subtree and everything to its right is the right subtree; this also tells you how many nodes each subtree has.",
           "The preorder array is the root, then the left subtree's preorder (as many entries as the left subtree has nodes), then the right subtree's preorder. Recurse on the two pairs of slices, and use a dictionary from value to inorder index so each root is located in O(1)."],
    editorial=["The first preorder entry is the root. In the inorder array the root splits the nodes into the left subtree (before it) and the right subtree (after it); if the left part has k nodes, then the next k preorder entries after the root are the left subtree's preorder and the remaining ones are the right subtree's. Recursing on those two pairs of ranges rebuilds the tree.",
               "Searching for the root linearly would cost O(n) per node (O(n<sup>2</sup>) overall on a chain), so precompute a map from value to inorder position. Then every node costs O(1) and the total is O(n). Working with index ranges instead of slicing avoids copying arrays, and an explicit stack of ranges avoids deep recursion; the reference solution does exactly that and finally writes the tree out level by level."],
    time="O(n)", space="O(n)",
    solution=ENCODE + '''def buildTree(preorder, inorder):
    n = len(preorder)
    if n == 0:
        return []
    pos = {v: i for i, v in enumerate(inorder)}
    left = [-1] * n
    right = [-1] * n
    # node id = index in preorder; a task is (preorder start, inorder start, size)
    stack = [(0, 0, n)]
    while stack:
        p, s, size = stack.pop()
        k = pos[preorder[p]] - s  # nodes in the left subtree
        if k > 0:
            left[p] = p + 1
            stack.append((p + 1, s, k))
        if size - 1 - k > 0:
            right[p] = p + 1 + k
            stack.append((p + 1 + k, s + k + 1, size - 1 - k))
    return _encode(preorder, left, right, 0)
''',
    tests=[],
)


def _tests_pre_in():
    r = rnd(8401)
    encs = [_dtree(r, 7, "random"), _dtree(r, 8, "deep"), _dtree(r, 11, "random")]
    encs = [e for e in SMALL if len(set(x for x in e if x != -1)) == len([x for x in e if x != -1])] + encs
    big = [_dtree(r, MAXN, "left"), _dtree(r, MAXN, "random"), _dtree(r, MAXN, "zig")]
    out = []
    for e in encs + big:
        root = _build(e)
        out.append([_vals(_preorder(root)), _vals(_inorder(root))])
    return out


def _b_pre_in(pre, ino):
    def rec(pre, ino):
        if not pre:
            return None
        x = _N(pre[0])
        k = ino.index(pre[0])
        x.l = rec(pre[1:1 + k], ino[:k])
        x.r = rec(pre[1 + k:], ino[k + 1:])
        return x
    return _encode(rec(pre, ino))


def _g_pre_in(r):
    root = _dtree_obj(r, r.randint(0, 9), r.choice(MODES))
    return [_vals(_preorder(root)), _vals(_inorder(root))]


def _v_pre_in(tests):
    for t in tests:
        pre, ino = t["args"]
        _v_enc(t["expected"])
        assert len(pre) == len(ino) <= MAXN and len(set(pre)) == len(pre) and sorted(pre) == sorted(ino)
        assert all(0 <= v <= MAXV for v in pre)
        root = _build(t["expected"])
        assert _vals(_preorder(root)) == pre and _vals(_inorder(root)) == ino


_P[-1]["tests"] = _tests_pre_in()
CHECKS["construct-tree-from-preorder-inorder"] = (_b_pre_in, _g_pre_in, "exact")
VALIDATE["construct-tree-from-preorder-inorder"] = _v_pre_in

# ---------------------------------------------------------------- inorder + postorder
add(
    id="construct-tree-from-inorder-postorder", title="Build a Binary Tree from Inorder and Postorder", diff="Medium", topic=TOPIC,
    fn="buildTree", params=[("inorder", "int[]"), ("postorder", "int[]")], ret="int[]", cmp="exact",
    desc="<p>You are given the <em>inorder</em> traversal (left subtree, node, right subtree) and the <em>postorder</em> traversal (left subtree, right subtree, node) of a binary tree whose node values are all distinct. Rebuild the tree and return it in level-order encoding.</p>" + ENC +
         "<p>For <code>inorder = [9, 3, 15, 20, 7]</code> and <code>postorder = [9, 15, 7, 20, 3]</code> the answer is <code>[3, 9, 20, -1, -1, 15, 7]</code>. For <code>inorder = [1, 2]</code> and <code>postorder = [2, 1]</code> the answer is <code>[1, -1, 2]</code>.</p>"
         "<p>With distinct values the two traversals determine the tree uniquely. Both arrays are empty for the empty tree, whose answer is <code>[]</code>.</p>",
    constraints=_trav_cons("inorder", "postorder"),
    hints=["Where in the postorder array does the root of the whole tree sit?",
           "Find that root in the inorder array. The part before it is the left subtree, the part after it is the right subtree. The sizes of the two parts tell you how to cut the postorder array.",
           "Postorder is: left subtree, right subtree, root. So with a left size of k, the first k entries are the left subtree and the next ones (up to the last) are the right subtree. Recurse, using a value-to-inorder-index map to find each root in O(1)."],
    editorial=["The last postorder entry is the root. Locate it in the inorder array: it separates the left subtree (k nodes) from the right subtree. In the postorder array the first k entries are then the left subtree and the following ones, up to but excluding the final root entry, are the right subtree. Recursing on the two matching pairs of ranges rebuilds everything.",
               "As with the preorder version, a precomputed map from value to inorder position makes each root lookup O(1), for O(n) in total. The mirror-image relationship is worth noticing: reading the postorder array from the back gives root, right subtree, left subtree, which is the preorder of the mirrored tree. The reference solution uses ranges and an explicit stack to avoid recursion-depth limits on chain-shaped trees."],
    time="O(n)", space="O(n)",
    solution=ENCODE + '''def buildTree(inorder, postorder):
    n = len(postorder)
    if n == 0:
        return []
    pos = {v: i for i, v in enumerate(inorder)}
    left = [-1] * n
    right = [-1] * n
    # node id = index in postorder; a task is (postorder start, inorder start, size)
    stack = [(0, 0, n)]
    while stack:
        q, s, size = stack.pop()
        root = q + size - 1
        k = pos[postorder[root]] - s  # nodes in the left subtree
        if k > 0:
            left[root] = q + k - 1
            stack.append((q, s, k))
        if size - 1 - k > 0:
            right[root] = root - 1
            stack.append((q + k, s + k + 1, size - 1 - k))
    return _encode(postorder, left, right, n - 1)
''',
    tests=[],
)


def _tests_in_post():
    r = rnd(8501)
    encs = [_dtree(r, 7, "random"), _dtree(r, 9, "deep"), _dtree(r, 10, "random")]
    encs = [e for e in SMALL if len(set(x for x in e if x != -1)) == len([x for x in e if x != -1])] + encs
    big = [_dtree(r, MAXN, "right"), _dtree(r, MAXN, "random"), _dtree(r, MAXN, "complete")]
    out = []
    for e in encs + big:
        root = _build(e)
        out.append([_vals(_inorder(root)), _vals(_postorder(root))])
    return out


def _b_in_post(ino, post):
    def rec(ino, post):
        if not post:
            return None
        x = _N(post[-1])
        k = ino.index(post[-1])
        x.l = rec(ino[:k], post[:k])
        x.r = rec(ino[k + 1:], post[k:-1])
        return x
    return _encode(rec(ino, post))


def _g_in_post(r):
    root = _dtree_obj(r, r.randint(0, 9), r.choice(MODES))
    return [_vals(_inorder(root)), _vals(_postorder(root))]


def _v_in_post(tests):
    for t in tests:
        ino, post = t["args"]
        _v_enc(t["expected"])
        assert len(post) == len(ino) <= MAXN and len(set(post)) == len(post) and sorted(post) == sorted(ino)
        assert all(0 <= v <= MAXV for v in post)
        root = _build(t["expected"])
        assert _vals(_postorder(root)) == post and _vals(_inorder(root)) == ino


_P[-1]["tests"] = _tests_in_post()
CHECKS["construct-tree-from-inorder-postorder"] = (_b_in_post, _g_in_post, "exact")
VALIDATE["construct-tree-from-inorder-postorder"] = _v_in_post

# ---------------------------------------------------------------- flatten to right chain
add(
    id="flatten-binary-tree-right-chain", title="Flatten a Binary Tree into a Right Chain", diff="Medium", topic=TOPIC,
    fn="flattenTree", params=[("tree", "int[]")], ret="int[]", cmp="exact",
    desc="<p>Rearrange a binary tree into a <em>right chain</em>: a tree in which no node has a left child and every node's right child is the next node in the <em>preorder</em> traversal of the original tree. The root stays the root and no value changes; only the child links change.</p>" + ENC +
         "<p>Return the flattened tree in the same level-order encoding. For <code>tree = [1, 2, 5, 3, 4, -1, 6]</code> the preorder is 1, 2, 3, 4, 5, 6, so the answer is <code>[1, -1, 2, -1, 3, -1, 4, -1, 5, -1, 6]</code>. The empty tree stays <code>[]</code>.</p>",
    constraints=_cons(),
    hints=["Write down the preorder of the tree first. The flattened tree is a chain through exactly these nodes in this order.",
           "What does the level-order encoding of a right chain with values v1, v2, ..., vn look like? Each node contributes its value and then a <code>-1</code> for its missing left child.",
           "Do a preorder traversal with an explicit stack (push the right child, then the left child, so the left one is popped first) and output <code>value, -1</code> for each node. Remove the final trailing <code>-1</code>."],
    editorial=["The flattened tree is determined entirely by the preorder of the original: the chain visits the nodes in preorder, so the problem reduces to computing the preorder traversal and then writing a chain in level-order encoding. A chain with values v<sub>1</sub>,&nbsp;...,&nbsp;v<sub>n</sub> is the array <code>v1, -1, v2, -1, ..., vn</code> because every node has a missing left child but its right child is listed next.",
               "To flatten the tree in place, as it is usually asked in interviews, you would instead splice each left subtree between a node and its right subtree: for a node, find the last node of its left subtree (the rightmost one), attach the node's old right subtree there, move the left subtree to the right and clear the left link. Both approaches run in linear time; the preorder one needs O(n) memory for the stack, the splicing one (Morris style) only O(1)."],
    time="O(n)", space="O(n)",
    solution=LINKS + '''def flattenTree(tree):
    vals, left, right = _links(tree)
    if not vals:
        return []
    out = []
    stack = [0]
    while stack:
        k = stack.pop()
        out.append(vals[k])
        out.append(-1)
        if right[k] != -1:
            stack.append(right[k])
        if left[k] != -1:
            stack.append(left[k])
    out.pop()
    return out
''',
    tests=[],
)


def _tests_flatten():
    r = rnd(8601)
    t = [[e] for e in SMALL]
    t.append([[1, 2, 5, 3, 4, -1, 6]])
    t.append([_tree(r, 14, "random", 0, 99)])
    t.append([_tree(r, MAXN, "random")])
    t.append([_tree(r, MAXN, "complete")])
    t.append([_tree(r, MAXN, "zig")])
    return t


def _b_flatten(tree):
    root = _build(tree)

    def flat(x):  # flattens the subtree in place and returns its last node
        if x.l is None and x.r is None:
            return x
        lt = flat(x.l) if x.l else None
        rt = flat(x.r) if x.r else None
        if lt:
            lt.r = x.r
            x.r = x.l
            x.l = None
        return rt if rt else lt
    if root:
        flat(root)
    return _encode(root)


def _v_flatten(tests):
    _v_trees(tests)
    for t in tests:
        _v_enc(t["expected"])
        n = sum(1 for x in t["args"][0] if x != -1)
        assert len(t["expected"]) == max(0, 2 * n - 1)


_P[-1]["tests"] = _tests_flatten()
CHECKS["flatten-binary-tree-right-chain"] = (_b_flatten, _g_tree(), "exact")
VALIDATE["flatten-binary-tree-right-chain"] = _v_flatten

# ---------------------------------------------------------------- deserialize
add(
    id="deserialize-binary-tree-null-markers", title="Deserialize a Binary Tree from Null-Marked Preorder", diff="Medium", topic=TOPIC, tier="must",
    fn="deserializePreorder", params=[("data", "int[]")], ret="int[]", cmp="exact",
    desc="<p>A binary tree was serialized in preorder: the value of every real node is written when the node is visited, followed by the serialization of its left subtree and then of its right subtree, and a missing child is written as <code>-1</code>. Missing children are written for every node that lacks them, so the array describes the tree completely.</p>"
         "<p>Given such an array <code>data</code>, rebuild the tree and return it in the standard level-order encoding.</p>" + ENC +
         "<p>For <code>data = [1, 2, -1, 4, -1, -1, 3, -1, -1]</code> the answer is <code>[1, 2, 3, -1, 4]</code>. For <code>data = [-1]</code> (the empty tree) the answer is <code>[]</code>, and for <code>data = [5, -1, 6, -1, -1]</code> it is <code>[5, -1, 6]</code>.</p>",
    constraints=["1 &le; data.length &le; 3,001 (a tree with at most 1,500 nodes has 2n + 1 entries)", f"Every real value is between 0 and {MAXV:,}; missing children are -1",
                 "data is a valid serialization: it contains exactly one more <code>-1</code> than it contains real values, and it ends exactly when the tree is complete"],
    hints=["The first entry is the root (or <code>-1</code> for the empty tree). What must come right after it?",
           "After the root comes the complete serialization of its left subtree, and when that is finished, the complete serialization of its right subtree. A subtree is finished when a missing marker closes it.",
           "Keep a stack of nodes whose children are not yet complete. Each next entry becomes the next free child of the node on top of the stack: first the left slot, then the right slot (after which the parent leaves the stack). A real value is also pushed as a new open node."],
    editorial=["Read the array from left to right and think of every entry as the next child slot to fill. The recursive formulation is: <code>read()</code> takes the next entry; if it is <code>-1</code> return empty, otherwise create a node whose left child is <code>read()</code> and whose right child is <code>read()</code>. Because the format is self-delimiting, no extra information is needed to find where a subtree ends.",
               "The same thing without recursion keeps a stack of open nodes together with a flag saying whether the left child has been filled. Every entry goes into the left slot, or the right slot of the node on top of the stack, and a node is popped as soon as its right slot is filled; a real value is pushed as a new open node. Each entry is processed once, so the time is linear. Finally the tree is written out level by level as in the other problems."],
    time="O(n)", space="O(n)",
    solution=ENCODE + '''def deserializePreorder(data):
    vals, left, right = [], [], []
    stack = []  # [node id, next slot to fill: 0 = left, 1 = right]
    root = -1
    for x in data:
        child = -1
        if x != -1:
            child = len(vals)
            vals.append(x)
            left.append(-1)
            right.append(-1)
        if stack:
            top = stack[-1]
            if top[1] == 0:
                left[top[0]] = child
                top[1] = 1
            else:
                right[top[0]] = child
                stack.pop()
        else:
            root = child
        if child != -1:
            stack.append([child, 0])
    return _encode(vals, left, right, root)
''',
    tests=[],
)


def _tests_deser():
    r = rnd(8701)
    encs = list(SMALL) + [_tree(r, 13, "random", 0, 99), _tree(r, 9, "deep", 0, 9)]
    encs += [_tree(r, MAXN, "left"), _tree(r, MAXN, "random"), _tree(r, MAXN, "complete")]
    return [[_pre_nulls(_build(e))] for e in encs]


def _b_deser(data):
    it = iter(data)

    def rec():
        x = next(it)
        if x == -1:
            return None
        n = _N(x)
        n.l = rec()
        n.r = rec()
        return n
    root = rec()
    assert next(it, None) is None
    return _encode(root)


def _g_deser(r):
    return [_pre_nulls(_build(_tree(r, r.randint(0, 9), r.choice(MODES), 0, 6)))]


def _v_deser(tests):
    for t in tests:
        d = t["args"][0]
        _v_enc(t["expected"])
        assert 1 <= len(d) <= 2 * MAXN + 1
        b = 1  # open child slots
        for i, x in enumerate(d):
            assert b > 0, "data continues after the tree is complete"
            b += (1 if x != -1 else -1)
            assert x == -1 or 0 <= x <= MAXV
        assert b == 0, "data ends early"
        assert _pre_nulls(_build(t["expected"])) == d


_P[-1]["tests"] = _tests_deser()
CHECKS["deserialize-binary-tree-null-markers"] = (_b_deser, _g_deser, "exact")
VALIDATE["deserialize-binary-tree-null-markers"] = _v_deser

# ---------------------------------------------------------------- parent-child descriptions
add(
    id="tree-from-parent-child-descriptions", title="Build a Tree from Parent-Child Descriptions", diff="Medium", topic=TOPIC,
    fn="buildFromDescriptions", params=[("descriptions", "int[][]")], ret="int[]", cmp="exact",
    desc="<p>A binary tree with distinct node values is described by a list of edges, in arbitrary order. Each edge is a triple <code>[parent, child, isLeft]</code>: the node <code>child</code> hangs below the node <code>parent</code>, as its left child if <code>isLeft = 1</code> and as its right child if <code>isLeft = 0</code>. The list contains every parent-child relation of the tree exactly once and nothing else, and the edges form a single valid binary tree (it has at least two nodes). The root is not named: it is the one node that is never a child.</p>"
         "<p>Return the tree in level-order encoding.</p>" + ENC +
         "<p>For <code>descriptions = [[20, 15, 1], [20, 17, 0], [50, 20, 1], [50, 80, 0], [80, 19, 1]]</code> the root is 50 with children 20 (left) and 80 (right); node 20 has children 15 and 17, and node 80 has the single left child 19. The answer is <code>[50, 20, 80, 15, 17, 19]</code>.</p>",
    constraints=["1 &le; descriptions.length &le; 1,499", f"0 &le; parent, child &le; {MAXV:,}; the node values are distinct", "isLeft is 0 or 1", "The edges describe exactly one valid binary tree (no node has two left or two right children, no cycles, one root)"],
    hints=["Which node is the root? Think about which values appear as a parent but never as a child.",
           "Store for every parent its left child and its right child in dictionaries. Then you can move downward from any node in O(1).",
           "After finding the root, run a level-order traversal using the dictionaries (a missing entry means <code>-1</code>), and trim the trailing <code>-1</code>s."],
    editorial=["First pass over the edges: record the left or right child of each parent in two dictionaries, and collect the set of all parents and the set of all children. The root is the single value that is in the parents but not in the children. All other nodes have exactly one parent, so nothing else can be a candidate.",
               "Then run a breadth-first traversal from the root. For a node x the entries to append for its children are <code>left.get(x, -1)</code> and <code>right.get(x, -1)</code>, and <code>-1</code> entries do not get expanded. The tail of <code>-1</code> values is trimmed at the end. Everything is linear in the number of edges, and the input order of the edges is irrelevant."],
    time="O(n)", space="O(n)",
    solution='''def buildFromDescriptions(descriptions):
    left, right = {}, {}
    parents, kids = set(), set()
    for p, c, is_left in descriptions:
        parents.add(p)
        kids.add(c)
        if is_left:
            left[p] = c
        else:
            right[p] = c
    root = next(iter(parents - kids))
    out = []
    queue = [root]
    for x in queue:
        if x == -1:
            out.append(-1)
        else:
            out.append(x)
            queue.append(left.get(x, -1))
            queue.append(right.get(x, -1))
    while out and out[-1] == -1:
        out.pop()
    return out
''',
    tests=[],
)


def _edges_of(root, r):
    edges, st = [], [root]
    while st:
        x = st.pop()
        if x.l:
            edges.append([x.v, x.l.v, 1])
            st.append(x.l)
        if x.r:
            edges.append([x.v, x.r.v, 0])
            st.append(x.r)
    r.shuffle(edges)
    return edges


def _tests_desc():
    r = rnd(8801)
    out = [[[[20, 15, 1], [20, 17, 0], [50, 20, 1], [50, 80, 0], [80, 19, 1]]],
           [[[1, 2, 1]]], [[[1, 2, 0]]], [[[5, 3, 1], [3, 9, 0]]], [[[0, 10000, 0], [10000, 7, 1]]]]
    for n, mode in [(7, "random"), (12, "deep"), (15, "complete")]:
        out.append([_edges_of(_dtree_obj(r, n, mode), r)])
    for mode in ("left", "random", "zig"):
        out.append([_edges_of(_dtree_obj(r, MAXN, mode), r)])
    return out


def _b_desc(descriptions):
    nodes = {}
    for p, c, is_left in descriptions:
        for v in (p, c):
            nodes.setdefault(v, _N(v))
        if is_left:
            nodes[p].l = nodes[c]
        else:
            nodes[p].r = nodes[c]
    has_parent = {id(x.l) for x in nodes.values() if x.l} | {id(x.r) for x in nodes.values() if x.r}
    roots = [x for x in nodes.values() if id(x) not in has_parent]
    assert len(roots) == 1
    return _encode(roots[0])


def _g_desc(r):
    root = _dtree_obj(r, r.randint(2, 9), r.choice(MODES))
    return [_edges_of(root, r)]


def _v_desc(tests):
    for t in tests:
        d = t["args"][0]
        assert 1 <= len(d) <= MAXN - 1
        _v_enc(t["expected"])
        assert all(len(e) == 3 and e[2] in (0, 1) and 0 <= e[0] <= MAXV and 0 <= e[1] <= MAXV for e in d)
        assert len({e[1] for e in d}) == len(d), "a node has two parents"
        assert len({(e[0], e[2]) for e in d}) == len(d), "two left or two right children"
        nodes = {e[0] for e in d} | {e[1] for e in d}
        assert len(nodes) == len(d) + 1
        assert sum(1 for x in t["expected"] if x != -1) == len(nodes), "edges do not form one tree"


_P[-1]["tests"] = _tests_desc()
CHECKS["tree-from-parent-child-descriptions"] = (_b_desc, _g_desc, "exact")
VALIDATE["tree-from-parent-child-descriptions"] = _v_desc

# ---------------------------------------------------------------- full binary tree from preorder + postorder
add(
    id="full-binary-tree-from-preorder-postorder", title="Rebuild a Full Binary Tree from Preorder and Postorder", diff="Medium", topic=TOPIC,
    fn="buildFullTree", params=[("preorder", "int[]"), ("postorder", "int[]")], ret="int[]", cmp="exact",
    desc="<p>A binary tree is <em>full</em> if every node has either zero or two children. You are given the preorder traversal (node, left, right) and the postorder traversal (left, right, node) of a full binary tree with distinct node values. Rebuild the tree and return it in level-order encoding.</p>" + ENC +
         "<p>For <code>preorder = [1, 2, 4, 5, 3, 6, 7]</code> and <code>postorder = [4, 5, 2, 6, 7, 3, 1]</code> the answer is <code>[1, 2, 3, 4, 5, 6, 7]</code>. For <code>preorder = [8]</code> and <code>postorder = [8]</code> the answer is <code>[8]</code>.</p>"
         "<p>For general trees preorder and postorder do not determine the tree (a lone child may be left or right), but for full trees they do, so the answer is unique. The empty tree has empty arrays and the answer <code>[]</code>.</p>",
    constraints=["0 &le; n &le; 1,499 and n is odd or zero", f"0 &le; value &le; {MAXV:,}", "All values are distinct",
                 "<code>postorder</code> is a permutation of <code>preorder</code>, and both come from the same full binary tree"],
    hints=["The first preorder entry is the root and the last postorder entry is the root. What is the second preorder entry, if the tree has more than one node?",
           "In a full tree the root has two children, so <code>preorder[1]</code> is the root of the left subtree. Find it in the postorder array: that subtree ends exactly there.",
           "If the left subtree's root is at postorder index j (and the current range starts at index q), the left subtree has <code>j - q + 1</code> nodes. Split both arrays by that size and recurse on the two parts, using a value-to-postorder-index map."],
    editorial=["Preorder starts with the root followed by the left subtree and then the right subtree. Postorder lists the left subtree, then the right subtree, then the root. If the tree is full and has more than one node, the root has two children, and <code>preorder[1]</code> is the root of the left subtree. In the postorder array the root of a subtree is its last entry, so the left subtree occupies everything from the start of the range up to the position of <code>preorder[1]</code>. That gives its size, hence also the boundary between the subtrees in both arrays.",
               "Fullness is what makes the split unique. If a node could have a single child, <code>preorder[1]</code> could be the root of a left or of a right subtree and the position in the postorder array would not tell which. Using a dictionary from value to postorder index, every split costs O(1), and the whole reconstruction is O(n). The reference solution processes ranges with an explicit stack to be safe on deep trees."],
    time="O(n)", space="O(n)",
    solution=ENCODE + '''def buildFullTree(preorder, postorder):
    n = len(preorder)
    if n == 0:
        return []
    pos = {v: i for i, v in enumerate(postorder)}
    left = [-1] * n
    right = [-1] * n
    # node id = index in preorder; a task is (preorder start, postorder start, size)
    stack = [(0, 0, n)]
    while stack:
        p, q, size = stack.pop()
        if size == 1:
            continue
        k = pos[preorder[p + 1]] - q + 1  # size of the left subtree
        left[p] = p + 1
        right[p] = p + 1 + k
        stack.append((p + 1, q, k))
        stack.append((p + 1 + k, q + k, size - 1 - k))
    return _encode(preorder, left, right, 0)
''',
    tests=[],
)


def _full_obj(r, n, mode):
    return _fill_distinct(r, _full_shape(r, n, mode), n)


def _tests_full():
    r = rnd(8901)
    out = [[[], []], [[8], [8]], [[1, 2, 4, 5, 3, 6, 7], [4, 5, 2, 6, 7, 3, 1]]]
    for n, mode in [(3, "random"), (5, "deep"), (9, "random"), (11, "complete"), (13, "deep")]:
        root = _full_obj(r, n, mode)
        out.append([_vals(_preorder(root)), _vals(_postorder(root))])
    for n, mode in [(1499, "deep"), (1499, "random"), (1499, "complete")]:
        root = _full_obj(r, n, mode)
        out.append([_vals(_preorder(root)), _vals(_postorder(root))])
    return out


def _b_full(pre, post):
    def rec(pre, post):
        if not pre:
            return None
        x = _N(pre[0])
        if len(pre) == 1:
            return x
        m = len(pre) - 1
        for k in range(1, m):
            if set(pre[1:1 + k]) == set(post[:k]):
                x.l = rec(pre[1:1 + k], post[:k])
                x.r = rec(pre[1 + k:], post[k:m])
                return x
        raise AssertionError("not a full tree")
    return _encode(rec(pre, post))


def _g_full(r):
    n = 2 * r.randint(0, 5) + 1 if r.random() < 0.95 else 0
    if n == 0:
        return [[], []]
    root = _full_obj(r, n, r.choice(["random", "deep", "complete"]))
    return [_vals(_preorder(root)), _vals(_postorder(root))]


def _v_full(tests):
    for t in tests:
        pre, post = t["args"]
        _v_enc(t["expected"])
        assert len(pre) == len(post) <= MAXN - 1 and len(set(pre)) == len(pre) and sorted(pre) == sorted(post)
        assert len(pre) % 2 == 1 or not pre
        root = _build(t["expected"])
        assert _vals(_preorder(root)) == pre and _vals(_postorder(root)) == post
        for x in _preorder(root):
            assert (x.l is None) == (x.r is None), "tree is not full"


_P[-1]["tests"] = _tests_full()
CHECKS["full-binary-tree-from-preorder-postorder"] = (_b_full, _g_full, "exact")
VALIDATE["full-binary-tree-from-preorder-postorder"] = _v_full

# ================================================================== HARD

# ---------------------------------------------------------------- general tree from preorder + postorder
add(
    id="general-tree-from-preorder-postorder", title="Rebuild a General Tree from Preorder and Postorder", diff="Medium", topic=TOPIC, tier="extra",
    fn="parentsFromTraversals", params=[("preorder", "int[]"), ("postorder", "int[]")], ret="int[]", cmp="exact",
    desc="<p>A rooted tree whose children are ordered but where every node may have <em>any number</em> of children (not just two) has distinct node values. You are given its <em>preorder</em> (a node, then each of its child subtrees from first to last) and its <em>postorder</em> (each child subtree from first to last, then the node) traversal. Unlike for binary trees, where a lone child can be left or right, these two traversals determine such a tree uniquely.</p>"
         "<p>Return the parent of every node as an array <code>parents</code> of the same length: <code>parents[i]</code> is the value of the parent of <code>preorder[i]</code>, and <code>-1</code> for the root.</p>"
         "<p>For <code>preorder = [1, 2, 3, 4]</code> and <code>postorder = [3, 2, 4, 1]</code> the tree is: 1 has the children 2 and 4, and 2 has the child 3. The answer is <code>[-1, 1, 2, 1]</code>. For <code>preorder = [1, 2, 3]</code> and <code>postorder = [2, 3, 1]</code> the root has two children, so the answer is <code>[-1, 1, 1]</code>; with <code>postorder = [3, 2, 1]</code> it is a chain and the answer is <code>[-1, 1, 2]</code>.</p>",
    constraints=["1 &le; n &le; 1,500", f"0 &le; value &le; {MAXV:,}", "All values are distinct",
                 "<code>postorder</code> is a permutation of <code>preorder</code>, and both come from the same ordered rooted tree"],
    hints=["Node x is an ancestor of node y exactly when x comes before y in preorder and after y in postorder.",
           "Walk through the preorder array and keep the path of ancestors that are still &quot;open&quot; on a stack. Which nodes on the stack are not ancestors of the new node?",
           "A node t on top of the stack is finished (not an ancestor of the next node x) when t appears <em>before</em> x in postorder. Pop such nodes; the node left on top is the parent of x. Then push x."],
    editorial=["In a tree, x is a proper ancestor of y exactly when x is visited before y in preorder (we enter x first) and after y in postorder (we leave x last). The parent of y is the deepest ancestor, i.e. the ancestor that is entered latest.",
               "Process the nodes in preorder and keep the stack of the current root-to-node path. For the next node x, a stack node t is no longer an ancestor if t was already left before x was left, that is, if its postorder index is smaller than that of x. Such nodes are popped from the top; the first node that survives is the parent of x (the stack is ordered from the root down, and ancestry is nested). Every node is pushed and popped at most once, so the algorithm is linear with a value-to-postorder-index map.",
               "For binary trees the same traversals are ambiguous only because a lone child could be a left or a right child; here the tree has no such left/right distinction, so the parent array is the whole answer."],
    time="O(n)", space="O(n)",
    solution='''def parentsFromTraversals(preorder, postorder):
    pos = {v: i for i, v in enumerate(postorder)}
    parents = [-1]
    stack = [preorder[0]]
    for x in preorder[1:]:
        while pos[stack[-1]] < pos[x]:  # already left before x: not an ancestor
            stack.pop()
        parents.append(stack[-1])
        stack.append(x)
    return parents
''',
    tests=[],
)


def _general(r, n, mode):
    """Random ordered tree: parent[i] < i for every node i >= 1. Returns (preorder, postorder) with distinct values."""
    par = [-1] * n
    for i in range(1, n):
        if mode == "chain":
            par[i] = i - 1
        elif mode == "star":
            par[i] = 0
        elif mode == "deep":
            par[i] = r.randint(max(0, i - 3), i - 1)
        else:
            par[i] = r.randint(0, i - 1)
    kids = [[] for _ in range(n)]
    for i in range(1, n):
        kids[par[i]].append(i)
    vals = r.sample(range(MAXV + 1), n)
    pre, post, st = [], [], [(0, 0)]
    while st:
        v, j = st.pop()
        if j == 0:
            pre.append(vals[v])
        if j < len(kids[v]):
            st.append((v, j + 1))
            st.append((kids[v][j], 0))
        else:
            post.append(vals[v])
    return [pre, post]


def _tests_general():
    r = rnd(9001)
    out = [[[1], [1]], [[1, 2, 3, 4], [3, 2, 4, 1]], [[1, 2, 3], [2, 3, 1]], [[1, 2, 3], [3, 2, 1]],
           [[5, 4, 9, 7, 8, 2], [9, 7, 4, 8, 2, 5]]]
    for n, mode in [(9, "random"), (12, "deep"), (20, "random"), (15, "star")]:
        out.append(_general(r, n, mode))
    for n, mode in [(MAXN, "chain"), (MAXN, "random"), (MAXN, "deep")]:
        out.append(_general(r, n, mode))
    return out


def _b_general(pre, post):
    res = []
    for x in range(len(pre)):
        anc = [y for y in range(len(pre)) if y < x and post.index(pre[y]) > post.index(pre[x])]
        res.append(pre[max(anc)] if anc else -1)
    return res


def _g_general(r):
    return _general(r, r.randint(1, 9), r.choice(["random", "random", "chain", "star", "deep"]))


def _v_general(tests):
    for t in tests:
        pre, post = t["args"]
        assert 1 <= len(pre) == len(post) <= MAXN and len(set(pre)) == len(pre) and sorted(pre) == sorted(post)
        assert all(0 <= v <= MAXV for v in pre)
        e = t["expected"]
        assert e.count(-1) == 1 and e[0] == -1 and len(e) == len(pre)
        pos = {v: i for i, v in enumerate(pre)}
        assert all(pos[e[i]] < i for i in range(1, len(e))), "parent must come earlier in preorder"


_P[-1]["tests"] = _tests_general()
CHECKS["general-tree-from-preorder-postorder"] = (_b_general, _g_general, "exact")
VALIDATE["general-tree-from-preorder-postorder"] = _v_general

# ================================================================== HARD

# ---------------------------------------------------------------- dashed preorder string
add(
    id="tree-from-dashed-preorder-string", title="Recover a Tree from a Dashed Preorder String", diff="Hard", topic=TOPIC, tier="common",
    fn="recoverTree", params=[("s", "string")], ret="int[]", cmp="exact",
    desc="<p>A binary tree was written as a single string by a preorder traversal. Every node is written as <em>D</em> dashes followed by its value, where <em>D</em> is the depth of the node (the root has depth 0, its children depth 1, and so on). The nodes are written in preorder, one after another with nothing between them.</p>"
         "<p>If a node has exactly one child, that child is its <em>left</em> child. Recover the tree and return it in level-order encoding.</p>" + ENC +
         "<p>For <code>s = \"1-2--3--4-5--6--7\"</code> the nodes are 1 (depth 0), 2 (1), 3 (2), 4 (2), 5 (1), 6 (2), 7 (2): the root 1 has children 2 and 5, and each of them has two leaf children. The answer is <code>[1, 2, 5, 3, 4, 6, 7]</code>. For <code>s = \"1-401--349---90--88\"</code> the answer is <code>[1, 401, -1, 349, 88, 90]</code>.</p>",
    constraints=["1 &le; number of nodes &le; 1,500 and 1 &le; s.length &le; 30,000", f"Every value is an integer between 0 and {MAXV:,} written without leading zeros",
                 "s is a valid description: the depths start at 0 for the root only, and each node's depth is at most one more than that of the node before it"],
    hints=["Parse the string into pairs (depth, value) first. Where is the parent of a node in the sequence?",
           "In preorder, the parent of a node at depth d is the most recent earlier node with depth d - 1. A stack that holds the current root-to-node path can tell you which one that is.",
           "Keep the path as a stack. For each new item with depth d, cut the stack down to d entries (leaving the parent on top), attach the node as the parent's left child if that is still free and as its right child otherwise, then push it."],
    editorial=["First tokenize the string: count the dashes to get the depth, then read the digits as the value. The sequence of (depth, value) pairs is the preorder of the tree annotated with depths, so for every item the parent is the nearest preceding item that is one level shallower.",
               "A stack that holds the path from the root to the most recently created node gives that parent immediately. For an item at depth d, pop until only d nodes remain; the top is the parent. Because a single child is always the left one, and children are written left before right, the new node becomes the left child if the parent's left slot is empty and the right child otherwise. Push the new node and continue. Every node is pushed and popped once, so the time is linear in the length of the string, and the final step writes the tree in level order."],
    time="O(|s|)", space="O(n)",
    solution=ENCODE + '''def recoverTree(s):
    vals, left, right = [], [], []
    path = []
    i, n = 0, len(s)
    while i < n:
        depth = 0
        while s[i] == '-':
            depth += 1
            i += 1
        v = 0
        while i < n and s[i] != '-':
            v = v * 10 + ord(s[i]) - 48
            i += 1
        k = len(vals)
        vals.append(v)
        left.append(-1)
        right.append(-1)
        del path[depth:]
        if path:
            p = path[-1]
            if left[p] == -1:
                left[p] = k
            else:
                right[p] = k
        path.append(k)
    return _encode(vals, left, right, 0)
''',
    tests=[],
)


def _dash_obj(r, n, mode, lo=0, hi=MAXV):
    root = _fill(r, _shape(r, n, mode), lo, hi)
    for x in _preorder(root):
        if x.l is None and x.r is not None:
            x.l, x.r = x.r, None
    return root


def _dash(root):
    parts, st = [], [(root, 0)]
    while st:
        x, d = st.pop()
        parts.append("-" * d + str(x.v))
        if x.r:
            st.append((x.r, d + 1))
        if x.l:
            st.append((x.l, d + 1))
    return "".join(parts)


def _tests_dash():
    r = rnd(9101)
    out = [["1-2--3--4-5--6--7"], ["1-401--349---90--88"], ["0"], ["10000"], ["5-6--7---8----9"], ["3-0-0"]]
    for n, mode, hi in [(10, "random", 99), (14, "deep", 9999), (20, "left", 50), (16, "complete", 9)]:
        out.append([_dash(_dash_obj(r, n, mode, 0, hi))])
    for n, mode in [(160, "left"), (800, "random"), (1500, "complete")]:
        out.append([_dash(_dash_obj(r, n, mode))])
    return out


def _b_dash(s):
    items = [(len(m.group(1)), int(m.group(2))) for m in re.finditer(r"(-*)(\d+)", s)]

    def build(i, d):
        x = _N(items[i][1])
        i += 1
        if i < len(items) and items[i][0] == d + 1:
            x.l, i = build(i, d + 1)
        if i < len(items) and items[i][0] == d + 1:
            x.r, i = build(i, d + 1)
        return x, i
    root, end = build(0, 0)
    assert end == len(items)
    return _encode(root)


def _g_dash(r):
    return [_dash(_dash_obj(r, r.randint(1, 10), r.choice(MODES), 0, r.choice([9, 100, 10000])))]


def _v_dash(tests):
    for t in tests:
        s = t["args"][0]
        assert 1 <= len(s) <= 30000 and re.fullmatch(r"(-*(0|[1-9][0-9]*))+", s), "bad characters"
        items = [(len(m.group(1)), int(m.group(2))) for m in re.finditer(r"(-*)(\d+)", s)]
        assert len(items) <= MAXN and items[0][0] == 0 and all(d >= 1 for d, _ in items[1:])
        assert all(0 <= v <= MAXV for _, v in items)
        for k in range(1, len(items)):
            assert items[k][0] <= items[k - 1][0] + 1
        _v_enc(t["expected"])
        assert sum(1 for x in t["expected"] if x != -1) == len(items)
        assert _dash(_build(t["expected"])) == s


_P[-1]["tests"] = _tests_dash()
CHECKS["tree-from-dashed-preorder-string"] = (_b_dash, _g_dash, "exact")
VALIDATE["tree-from-dashed-preorder-string"] = _v_dash
