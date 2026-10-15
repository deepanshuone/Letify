"""Problems: binary trees - depth, height, diameter, balance, counting nodes, leaves and levels.
Trees use the level-order array encoding with -1 for a missing child. See data/lib.py for the registry."""
from collections import deque

from lib import add, rnd, CHECKS, VALIDATE, gen_arr  # noqa: F401
from lib import P as _P

TOPIC = "Trees"
MAXN = 1500      # maximum number of nodes in any tree
MAXV = 10000     # maximum node value

ENC = (
    "<p><strong>How trees are given.</strong> There is no tree type here. A binary tree is passed as an integer array in "
    "<em>level-order</em> (top to bottom, left to right), the same way LeetCode serialises trees. A missing child is written as "
    "<code>-1</code>, and every real node value is non-negative. The children of a missing node are not listed, and trailing "
    "<code>-1</code> entries are dropped, so a non-empty array never ends with <code>-1</code>. The empty tree is <code>[]</code>.</p>"
    "<p>For example, <code>[1, 2, 3, -1, 4]</code> describes the tree on the left: the root is 1 with children 2 and 3, node 2 has no left "
    "child and has 4 as its right child, and node 3 is a leaf.</p>"
    "<pre>    1\n   / \\\n  2   3\n   \\\n    4</pre>"
)


def _cons(extra=None, lo=0):
    out = [f"{lo} &le; number of nodes &le; {MAXN:,}", f"0 &le; node value &le; {MAXV:,}",
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


def _levelorder(root):
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


def _tree_distinct(r, n, mode="random"):
    root = _shape(r, n, mode)
    vals = r.sample(range(0, MAXV + 1), n)
    for x, v in zip(_preorder(root), vals):
        x.v = v
    return _encode(root)


def _perfect(h, r, lo=0, hi=MAXV):
    """Perfect tree with h levels (2^h - 1 nodes)."""
    if h == 0:
        return None
    x = _N(r.randint(lo, hi))
    x.l = _perfect(h - 1, r, lo, hi)
    x.r = _perfect(h - 1, r, lo, hi)
    return x


def _attach_random(r, root, extra, lo=0, hi=MAXV):
    """Hang `extra` new random nodes on free child slots of an existing tree."""
    free = []
    for x in _preorder(root):
        if x.l is None:
            free.append((x, 0))
        if x.r is None:
            free.append((x, 1))
    for _ in range(extra):
        i = r.randrange(len(free))
        free[i], free[-1] = free[-1], free[i]
        node, side = free.pop()
        c = _N(r.randint(lo, hi))
        if side == 0:
            node.l = c
        else:
            node.r = c
        free.append((c, 0))
        free.append((c, 1))
    return root


def _gen(nmax=10, vmax=5, modes=MODES):
    def g(r):
        return [_tree(r, r.randint(0, nmax), r.choice(modes), 0, vmax)]
    return g


def _v_trees(tests):
    for t in tests:
        arr = t["args"][0]
        assert isinstance(arr, list) and all(isinstance(x, int) for x in arr)
        assert arr == _encode(_build(arr)), ("not a canonical level-order encoding", arr[:12])
        nodes = [x for x in arr if x != -1]
        assert len(nodes) <= MAXN, "too many nodes"
        assert all(0 <= x <= MAXV for x in nodes), "node value out of range"
        assert not arr or arr[0] != -1


def _v_varied(tests):
    """Trees are valid and the answers are not all the same."""
    _v_trees(tests)
    assert len({repr(t["expected"]) for t in tests}) >= 4, "answers not varied enough"


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

BASE = [
    [], [0], [1, 2, 3], [1, -1, 2, -1, 3], [1, 2, -1, 3, -1, 4], [3, 9, 20, -1, -1, 15, 7],
    [1, 2, 3, 4, 5, 6, 7], [1, 2, 2, 3, 3, -1, -1, 4, 4], [5, 5, 5, 5, 5, 5, 5, 5],
]


def _big(seed, hi=MAXV):
    """Four large trees of different shapes."""
    r = rnd(seed)
    return [_tree(r, MAXN, "left", 0, hi), _tree(r, MAXN, "zig", 0, hi),
            _tree(r, MAXN, "complete", 0, hi), _tree(r, MAXN, "random", 0, hi)]


# ================================================================== EASY

# ---------------------------------------------------------------- minimum depth
add(
    id="binary-tree-minimum-depth", title="Minimum Depth of a Binary Tree", diff="Easy", topic=TOPIC,
    fn="minDepth", params=[("tree", "int[]")], ret="int", cmp="exact",
    desc="<p>A <em>leaf</em> is a node with no children. Given a binary tree, return the number of nodes on the <strong>shortest</strong> path that starts at the root and ends at a leaf. The empty tree has minimum depth <code>0</code>.</p>"
         "<p>Be careful: a node that has only one child is <em>not</em> a leaf, so the path must keep going through that child.</p>" + ENC +
         "<p>For <code>tree = [3, 9, 20, -1, -1, 15, 7]</code> the answer is <code>2</code> (the path 3 &rarr; 9). For <code>tree = [2, -1, 3, -1, 4, -1, 5]</code>, a chain going right, the answer is <code>4</code>.</p>",
    constraints=_cons(),
    hints=["This looks like the maximum depth problem with <code>min</code> instead of <code>max</code>. Test it on a tree where the root has a single child.",
           "Only a node with <em>no</em> children ends a path. A missing child must not be treated as a path of length 0.",
           "Visit nodes level by level: the first leaf you meet is on the shallowest level, so its level number is the answer. Or recurse: if one child is missing, use the other child's result, otherwise take the smaller of the two."],
    editorial=["The tempting formula <code>1 + min(depth(left), depth(right))</code> is wrong when exactly one child is missing, because the missing side would count as depth 0 and make a non-leaf look like the end of a path. A path must end at a real leaf.",
               "The simplest correct idea is a breadth-first scan. Nodes in level order are grouped by depth, so the first node without children that you encounter is on the shallowest possible level. In the array encoding the parent of every node comes earlier than the node, so one forward pass that sets <code>depth[child] = depth[parent] + 1</code> and returns at the first leaf works without recursion.",
               "The recursive version handles the three cases explicitly: no children gives 1, one child gives 1 plus that child's result, two children gives 1 plus the smaller result. Both versions visit every node at most once."],
    time="O(n)", space="O(n)",
    solution=LINKS + '''def minDepth(tree):
    vals, left, right = _links(tree)
    n = len(vals)
    if n == 0:
        return 0
    depth = [1] * n
    for k in range(n):
        if left[k] == -1 and right[k] == -1:
            return depth[k]
        for c in (left[k], right[k]):
            if c != -1:
                depth[c] = depth[k] + 1
    return depth[0]
''',
    tests=[],
)
_r = rnd(8101)
_P[-1]["tests"] = [[t] for t in BASE + [
    [2, -1, 3, -1, 4, -1, 5], [1, 2], [1, 2, 3, 4], [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15],
] + _big(8101)] + [[_tree(_r, MAXN, "right", 0, MAXV)]]


def _b_mindepth(tree):
    def d(x):
        if x is None:
            return 0
        if x.l is None and x.r is None:
            return 1
        if x.l is None:
            return 1 + d(x.r)
        if x.r is None:
            return 1 + d(x.l)
        return 1 + min(d(x.l), d(x.r))
    return d(_build(tree))


CHECKS["binary-tree-minimum-depth"] = (_b_mindepth, _gen(), "exact")
VALIDATE["binary-tree-minimum-depth"] = _v_varied

# ---------------------------------------------------------------- leaves / single child / two children
add(
    id="binary-tree-leaf-and-child-counts", title="Leaves, One-Child and Two-Child Nodes", diff="Easy", topic=TOPIC,
    fn="countNodeKinds", params=[("tree", "int[]")], ret="int[]", cmp="exact",
    desc="<p>Every node of a binary tree falls into exactly one of three kinds: a <em>leaf</em> (no children), a node with <em>exactly one</em> child, or a node with <em>two</em> children.</p>"
         "<p>Return an array of three integers <code>[leaves, oneChild, twoChildren]</code> with the number of nodes of each kind. For the empty tree return <code>[0, 0, 0]</code>.</p>" + ENC +
         "<p>For <code>tree = [1, 2, 3, 4, 5, -1, 6]</code> the answer is <code>[3, 1, 2]</code>: the leaves are 4, 5 and 6, node 3 has one child, and nodes 1 and 2 have two.</p>",
    constraints=_cons(),
    hints=["Each node has two child slots in the tree. You only need to know how many of them are filled for each node.",
           "In the array, every real node is followed (later on) by exactly two slots that belong to it, and a slot holds either a value or <code>-1</code>. Count how many real values sit in each node's two slots.",
           "Alternatively, count the real nodes <code>n</code> and the number of real nodes that are children, then reason about totals: the number of filled child slots equals <code>n - 1</code> for a non-empty tree, so <code>oneChild + 2 * twoChildren = n - 1</code>."],
    editorial=["For each node look at its two child slots. Zero filled slots means leaf, one filled slot means a single-child node, two means a full node. In the level-order array the k-th real node owns slots <code>2k+1</code> and <code>2k+2</code>, so one pass over the real nodes is enough and no tree has to be built.",
               "There is a neat consequence worth remembering: in any non-empty binary tree, <code>leaves = twoChildren + 1</code>. Each full node adds one extra branch, and every branch ends in a leaf. This identity makes a handy sanity check for your counts.",
               "The work is linear in the length of the array and uses constant extra memory apart from the parsing helper."],
    time="O(n)", space="O(n)",
    solution=LINKS + '''def countNodeKinds(tree):
    vals, left, right = _links(tree)
    res = [0, 0, 0]
    for k in range(len(vals)):
        kids = (left[k] != -1) + (right[k] != -1)
        res[2 if kids == 2 else 1 if kids == 1 else 0] += 1
    return res
''',
    tests=[],
)
_r = rnd(8102)
_P[-1]["tests"] = [[t] for t in BASE + [
    [1, 2, 3, 4, 5, -1, 6], [7, 7], [1, -1, 2], [4, 2, 6, 1, 3, 5, 7, 0],
] + _big(8102)]


def _b_kinds(tree):
    res = [0, 0, 0]
    for x in _preorder(_build(tree)):
        kids = (x.l is not None) + (x.r is not None)
        res[[0, 1, 2][kids]] += 1
    return res


def _v_kinds(tests):
    _v_trees(tests)
    for t in tests:
        a, b, c = t["expected"]
        if a + b + c:
            assert a == c + 1
    assert len({repr(t["expected"]) for t in tests}) >= 5


CHECKS["binary-tree-leaf-and-child-counts"] = (_b_kinds, _gen(), "exact")
VALIDATE["binary-tree-leaf-and-child-counts"] = _v_kinds

# ---------------------------------------------------------------- sum of node depths
add(
    id="binary-tree-sum-of-node-depths", title="Sum of All Node Depths", diff="Easy", topic=TOPIC,
    fn="sumNodeDepths", params=[("tree", "int[]")], ret="int", cmp="exact",
    desc="<p>The <em>depth</em> of a node is the number of edges on the path from the root to that node, so the root has depth <code>0</code>, its children have depth <code>1</code>, and so on.</p>"
         "<p>Return the sum of the depths of all nodes in the tree. The empty tree gives <code>0</code>.</p>" + ENC +
         "<p>For <code>tree = [3, 9, 20, -1, -1, 15, 7]</code> the depths are 0, 1, 1, 2, 2, so the answer is <code>6</code>.</p>",
    constraints=_cons(),
    hints=["Compute the depth of each node and add them up. The depth of a node is one more than the depth of its parent.",
           "You do not need recursion or a separate traversal order: process the nodes so that every parent is handled before its children.",
           "In the level-order array the parent always appears before its children. One left-to-right pass can set <code>depth[child] = depth[parent] + 1</code> while adding to the sum."],
    editorial=["A parent is always processed before its children in level order, so the depth of every node can be derived in O(1) from its parent's depth. Keep the running sum while assigning depths.",
               "A recursive version passes the current depth down: <code>f(node, d) = d + f(left, d + 1) + f(right, d + 1)</code>. Both are linear. The answer can reach about 1.1 million on a path of 1,500 nodes, comfortably inside 32-bit integers."],
    time="O(n)", space="O(n)",
    solution=LINKS + '''def sumNodeDepths(tree):
    vals, left, right = _links(tree)
    n = len(vals)
    depth = [0] * n
    total = 0
    for k in range(n):
        total += depth[k]
        for c in (left[k], right[k]):
            if c != -1:
                depth[c] = depth[k] + 1
    return total
''',
    tests=[],
)
_P[-1]["tests"] = [[t] for t in BASE + [[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15], [9, 8, -1, 7, -1, 6]] + _big(8103)]


def _b_depthsum(tree):
    st, total = [(_build(tree), 0)], 0
    while st:
        x, d = st.pop()
        if x is None:
            continue
        total += d
        st.append((x.l, d + 1))
        st.append((x.r, d + 1))
    return total


CHECKS["binary-tree-sum-of-node-depths"] = (_b_depthsum, _gen(), "exact")
VALIDATE["binary-tree-sum-of-node-depths"] = _v_varied

# ================================================================== MEDIUM

# ---------------------------------------------------------------- sum of heights
add(
    id="binary-tree-sum-of-node-heights", title="Sum of All Node Heights", diff="Medium", topic=TOPIC,
    fn="sumNodeHeights", params=[("tree", "int[]")], ret="int", cmp="exact",
    desc="<p>The <em>height</em> of a node is the number of edges on the longest downward path from that node to a leaf in its own subtree. A leaf has height <code>0</code>.</p>"
         "<p>Return the sum of the heights of <strong>all</strong> nodes of the tree. The empty tree gives <code>0</code>.</p>" + ENC +
         "<p>For <code>tree = [3, 9, 20, -1, -1, 15, 7]</code> the heights are 2 (root), 0, 1, 0, 0, so the answer is <code>3</code>. For the chain <code>[1, 2, -1, 3]</code> the heights are 2, 1, 0 and the answer is <code>3</code>.</p>",
    constraints=_cons(),
    hints=["Computing the height of each node separately from scratch would be O(n<sup>2</sup>) on a long chain. Look for a way to reuse results.",
           "The height of a node depends only on the heights of its two children.",
           "Process nodes from the last one back to the first (children come after their parent in level order): <code>h[k] = 1 + max(h[left], h[right])</code> with a missing child counting as <code>-1</code>, then sum all <code>h</code>."],
    editorial=["The height of a node is <code>0</code> for a leaf and <code>1 + max(height(left), height(right))</code> otherwise. If you treat a missing child as height <code>-1</code> the two cases merge into one formula.",
               "Heights must be computed bottom-up so each node's value is known when its parent needs it. In the level-order array all children come after their parent, so a single backward pass over the real nodes does it. Adding every height as you go gives the answer in O(n) total, instead of O(n<sup>2</sup>) for the approach that recomputes a height for every node.",
               "The largest possible answer (a path of 1,500 nodes) is about 1.1 million, which fits easily."],
    time="O(n)", space="O(n)",
    solution=LINKS + '''def sumNodeHeights(tree):
    vals, left, right = _links(tree)
    n = len(vals)
    h = [0] * n
    total = 0
    for k in range(n - 1, -1, -1):
        hl = h[left[k]] if left[k] != -1 else -1
        hr = h[right[k]] if right[k] != -1 else -1
        h[k] = 1 + max(hl, hr)
        total += h[k]
    return total
''',
    tests=[], tier="extra",
)
_P[-1]["tests"] = [[t] for t in BASE + [[1, 2, -1, 3], [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]] + _big(8104)]


def _b_heightsum(tree):
    def height(x):
        return -1 if x is None else 1 + max(height(x.l), height(x.r))
    return sum(height(x) for x in _preorder(_build(tree)))


CHECKS["binary-tree-sum-of-node-heights"] = (_b_heightsum, _gen(), "exact")
VALIDATE["binary-tree-sum-of-node-heights"] = _v_varied

# ---------------------------------------------------------------- count unbalanced nodes
add(
    id="binary-tree-unbalanced-node-count", title="Count the Unbalanced Nodes", diff="Medium", topic=TOPIC,
    fn="countUnbalanced", params=[("tree", "int[]")], ret="int", cmp="exact",
    desc="<p>Let the <em>height</em> of a subtree be the number of nodes on its longest downward path (an empty subtree has height <code>0</code>). Call a node <em>unbalanced</em> if the heights of its left and right subtrees differ by <strong>more than 1</strong>.</p>"
         "<p>Return how many nodes of the tree are unbalanced. A tree is height-balanced exactly when this number is <code>0</code>.</p>" + ENC +
         "<p>For <code>tree = [1, 2, 2, 3, 3, -1, -1, 4, 4]</code> the answer is <code>1</code> (only the root: its left subtree has height 3, its right one has height 1). For the chain <code>[1, 2, -1, 3, -1, 4]</code> the answer is <code>2</code>.</p>",
    constraints=_cons(),
    hints=["Unlike the yes/no balance check, you may not stop at the first bad node: every node has to be examined.",
           "Each node needs only the heights of its two subtrees. Computing a height from scratch at every node is too slow on tall trees.",
           "Go through the nodes from last to first in level order, store the height of each node, and count the nodes where the two child heights differ by more than 1."],
    editorial=["The height of every subtree is needed by its parent, so compute heights bottom-up in one pass. At each node compare the two child heights (missing child = 0); if they differ by more than 1 increase the counter. The node height is then <code>1 + max(left, right)</code>.",
               "Because the level-order array lists parents before children, walking the real nodes backwards guarantees that both child heights are ready when a node is reached. The whole solution is O(n)."],
    time="O(n)", space="O(n)",
    solution=LINKS + '''def countUnbalanced(tree):
    vals, left, right = _links(tree)
    n = len(vals)
    h = [0] * n
    bad = 0
    for k in range(n - 1, -1, -1):
        hl = h[left[k]] if left[k] != -1 else 0
        hr = h[right[k]] if right[k] != -1 else 0
        if abs(hl - hr) > 1:
            bad += 1
        h[k] = 1 + max(hl, hr)
    return bad
''',
    tests=[],
)
_r = rnd(8105)
_P[-1]["tests"] = [[t] for t in BASE + [
    [1, 2, -1, 3, -1, 4], [1, 2, 3, 4, -1, -1, -1, 5], [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15],
] + _big(8105) + [_tree(_r, 1023, "complete", 0, 5)]]


def _b_unbal(tree):
    def h(x):
        return 0 if x is None else 1 + max(h(x.l), h(x.r))
    return sum(1 for x in _preorder(_build(tree)) if abs(h(x.l) - h(x.r)) > 1)


def _g_unbal(r):
    return [_tree(r, r.randint(0, 14), r.choice(["random", "complete", "deep", "random", "left", "zig"]), 0, 4)]


CHECKS["binary-tree-unbalanced-node-count"] = (_b_unbal, _g_unbal, "exact")
VALIDATE["binary-tree-unbalanced-node-count"] = _v_varied

# ---------------------------------------------------------------- largest balanced subtree
add(
    id="binary-tree-largest-balanced-subtree", title="Largest Height-Balanced Subtree", diff="Medium", topic=TOPIC,
    fn="largestBalancedSubtree", params=[("tree", "int[]")], ret="int", cmp="exact",
    desc="<p>A subtree consists of a node together with <strong>all</strong> of its descendants. It is <em>height-balanced</em> if at every node inside it the heights of the left and right sub-subtrees differ by at most <code>1</code> (an empty side has height <code>0</code>; height counts nodes on the longest downward path).</p>"
         "<p>Return the number of nodes in the largest height-balanced subtree of the tree. The empty tree gives <code>0</code>; a single node is always balanced.</p>" + ENC +
         "<p>For <code>tree = [1, 2, 2, 3, 3, -1, -1, 4, 4]</code> the whole tree is not balanced, but the subtree rooted at the left child (the nodes 2, 3, 3, 4, 4) is, so the answer is <code>5</code>.</p>",
    constraints=_cons(),
    hints=["Checking every node as a candidate root and testing balance from scratch is easy but quadratic on skewed trees.",
           "A subtree is balanced only if both child subtrees are balanced <em>and</em> their heights differ by at most 1. So a node can decide using what its children already know.",
           "From last node to first, store for each node: its height, its size, and whether it is balanced. The answer is the largest size among balanced nodes."],
    editorial=["Define for each node three facts about its subtree: <code>height</code>, <code>size</code> and <code>balanced</code>. A node is balanced when both children are balanced (a missing child counts as balanced with height 0) and their heights differ by at most 1. Its size is <code>1 + size(left) + size(right)</code> and its height is <code>1 + max(...)</code>.",
               "All three facts depend only on the children, so one backward pass through the level-order array computes them. Track the maximum size over balanced nodes. Time and space are linear, versus O(n<sup>2</sup>) for retesting each subtree independently."],
    time="O(n)", space="O(n)",
    solution=LINKS + '''def largestBalancedSubtree(tree):
    vals, left, right = _links(tree)
    n = len(vals)
    h = [0] * n
    size = [1] * n
    ok = [True] * n
    best = 0
    for k in range(n - 1, -1, -1):
        hl = hr = sl = sr = 0
        okl = okr = True
        if left[k] != -1:
            c = left[k]
            hl, sl, okl = h[c], size[c], ok[c]
        if right[k] != -1:
            c = right[k]
            hr, sr, okr = h[c], size[c], ok[c]
        h[k] = 1 + max(hl, hr)
        size[k] = 1 + sl + sr
        ok[k] = okl and okr and abs(hl - hr) <= 1
        if ok[k] and size[k] > best:
            best = size[k]
    return best
''',
    tests=[], tier="extra",
)
_r = rnd(8106)
_P[-1]["tests"] = [[t] for t in BASE + [
    [1, 2, -1, 3, -1, 4], [1, 2, 3, 4, -1, -1, -1, 5], [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15],
] + _big(8106)]


def _b_lbs(tree):
    def h(x):
        return 0 if x is None else 1 + max(h(x.l), h(x.r))

    def bal(x):
        return all(abs(h(y.l) - h(y.r)) <= 1 for y in _preorder(x))

    best = 0
    for x in _preorder(_build(tree)):
        if bal(x):
            best = max(best, len(_preorder(x)))
    return best


CHECKS["binary-tree-largest-balanced-subtree"] = (_b_lbs, _g_unbal, "exact")
VALIDATE["binary-tree-largest-balanced-subtree"] = _v_varied

# ---------------------------------------------------------------- perfect subtrees
add(
    id="binary-tree-perfect-subtree-count", title="Count the Perfect Subtrees", diff="Medium", topic=TOPIC,
    fn="countPerfectSubtrees", params=[("tree", "int[]")], ret="int", cmp="exact",
    desc="<p>A binary tree is <em>perfect</em> if every node that is not a leaf has exactly two children and all leaves are at the same depth. A single node is a perfect tree.</p>"
         "<p>For every node of the given tree consider the subtree made of that node and all its descendants. Return how many of these subtrees are perfect. The empty tree gives <code>0</code>.</p>" + ENC +
         "<p>For <code>tree = [1, 2, 3, 4, 5]</code> the answer is <code>4</code>: the leaves 4, 5, 3 and the subtree rooted at 2 are perfect; the whole tree is not. For <code>[1, 2, 3, 4, 5, 6, 7]</code> every one of the 7 subtrees is perfect.</p>",
    constraints=_cons(),
    hints=["Every leaf is a perfect subtree by itself. Think about which extra condition lets a larger node qualify.",
           "A node's subtree is perfect exactly when it has two children whose subtrees are both perfect <em>and</em> of the same height.",
           "Walk the real nodes from last to first, storing a perfect flag and a height for each; count the flags that are true."],
    editorial=["A perfect tree of height h is two perfect trees of height h-1 joined by a root, and a single node is the base case. So node <code>x</code> roots a perfect subtree iff it is a leaf, or it has two children, both children root perfect subtrees, and those subtrees have equal height.",
               "Compute heights and flags bottom-up in the level-order array (children come after their parent, so go backwards). A node with exactly one child is never perfect. The counter of true flags is the answer. This is O(n) time and space."],
    time="O(n)", space="O(n)",
    solution=LINKS + '''def countPerfectSubtrees(tree):
    vals, left, right = _links(tree)
    n = len(vals)
    h = [1] * n
    perfect = [False] * n
    count = 0
    for k in range(n - 1, -1, -1):
        a, b = left[k], right[k]
        if a == -1 and b == -1:
            perfect[k] = True
        else:
            if a != -1 and b != -1:
                perfect[k] = perfect[a] and perfect[b] and h[a] == h[b]
            h[k] = 1 + max(h[a] if a != -1 else 0, h[b] if b != -1 else 0)
        count += perfect[k]
    return count
''',
    tests=[], tier="extra",
)
_r = rnd(8107)
_perfect_big = _encode(_perfect(10, _r))                      # 1023 nodes, all subtrees perfect
_pp = _perfect(10, _r)
_attach_random(_r, _pp, 25)                                   # perfect tree with a few extra nodes hung on
_P[-1]["tests"] = [[t] for t in BASE + [
    [1, 2, 3, 4, 5], [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15], [1, 2, 3, 4, 5, 6, 7, 8],
    [1, 2, 3, 4, -1, 6, 7],
] + [_perfect_big, _encode(_pp), _tree(_r, MAXN, "complete", 0, MAXV), _tree(_r, MAXN, "random", 0, MAXV)]]


def _b_perfect(tree):
    def perfect(x):
        # explicit definition: internal nodes have 0 or 2 children and all leaves share one depth
        depths = set()
        st = [(x, 0)]
        while st:
            y, d = st.pop()
            if (y.l is None) != (y.r is None):
                return False
            if y.l is None:
                depths.add(d)
            else:
                st.append((y.l, d + 1))
                st.append((y.r, d + 1))
        return len(depths) == 1

    return sum(1 for x in _preorder(_build(tree)) if perfect(x))


def _g_perfect(r):
    if r.random() < 0.5:
        root = _perfect(r.randint(1, 3), r, 0, 3)
        _attach_random(r, root, r.choice([0, 0, 1, 2]), 0, 3)
        return [_encode(root)]
    return [_tree(r, r.randint(0, 12), r.choice(MODES), 0, 3)]


CHECKS["binary-tree-perfect-subtree-count"] = (_b_perfect, _g_perfect, "exact")
VALIDATE["binary-tree-perfect-subtree-count"] = _v_varied

# ---------------------------------------------------------------- average of subtree
add(
    id="binary-tree-nodes-equal-subtree-average", title="Nodes Equal to Their Subtree Average", diff="Medium", topic=TOPIC,
    fn="countAverageNodes", params=[("tree", "int[]")], ret="int", cmp="exact",
    desc="<p>For a node <code>x</code>, look at the values of <code>x</code> and all its descendants. The <em>subtree average</em> of <code>x</code> is the sum of those values divided by how many there are, <strong>rounded down</strong> to an integer.</p>"
         "<p>Return how many nodes have a value equal to their own subtree average. The empty tree gives <code>0</code>.</p>" + ENC +
         "<p>For <code>tree = [3, 1, 2]</code> the average at the root is <code>6 / 3 = 2</code>, which differs from 3, while both leaves equal their own value, so the answer is <code>2</code>. For <code>[2, 1, 3]</code> the root's average is 2, so all three nodes count and the answer is <code>3</code>.</p>",
    constraints=_cons(),
    hints=["For one node you need two numbers from its subtree: the sum of values and the number of nodes.",
           "Both numbers of a node are the node's own contribution plus the numbers of its two children, so they can be accumulated bottom-up.",
           "Go through the real nodes from last to first, keeping <code>sum[k]</code> and <code>cnt[k]</code>. Count the nodes with <code>sum[k] // cnt[k] == value[k]</code> (all values are non-negative, so <code>//</code> rounds down)."],
    editorial=["Re-summing the subtree of every node is O(n<sup>2</sup>) on a path. Instead keep two totals per node: the sum of values in its subtree and the number of nodes. A node's totals are its own value and 1 plus the totals of its children.",
               "In the level-order array children follow their parent, so a backward pass over the real nodes always finds the children's totals ready. After computing a node's totals, compare <code>sum // cnt</code> with the node's value. Total sums are at most 1,500 &times; 10,000 = 15 million, well within 32 bits."],
    time="O(n)", space="O(n)",
    solution=LINKS + '''def countAverageNodes(tree):
    vals, left, right = _links(tree)
    n = len(vals)
    s = vals[:]
    c = [1] * n
    count = 0
    for k in range(n - 1, -1, -1):
        for ch in (left[k], right[k]):
            if ch != -1:
                s[k] += s[ch]
                c[k] += c[ch]
        if s[k] // c[k] == vals[k]:
            count += 1
    return count
''',
    tests=[],
)
_r = rnd(8108)
_P[-1]["tests"] = [[t] for t in BASE + [
    [3, 1, 2], [2, 1, 3], [4, 2, 6, 1, 3, 5, 7], [10, 0, 0, 0, 0, 0, 0],
] + [_tree(_r, MAXN, "left", 0, 20), _tree(_r, MAXN, "zig", 0, MAXV), _tree(_r, MAXN, "complete", 0, 3),
     _tree(_r, MAXN, "random", 0, MAXV)]]


def _b_avg(tree):
    def vals(x):
        return [] if x is None else [x.v] + vals(x.l) + vals(x.r)

    return sum(1 for x in _preorder(_build(tree)) if sum(vals(x)) // len(vals(x)) == x.v)


CHECKS["binary-tree-nodes-equal-subtree-average"] = (_b_avg, _gen(10, 4), "exact")
VALIDATE["binary-tree-nodes-equal-subtree-average"] = _v_varied

# ---------------------------------------------------------------- farthest distance from every node
add(
    id="binary-tree-farthest-node-distances", title="Farthest Node From Every Node", diff="Medium", topic=TOPIC,
    fn="farthestDistances", params=[("tree", "int[]")], ret="int[]", cmp="exact",
    desc="<p>Treat the binary tree as an undirected graph: you may walk from a node to its parent as well as to its children, and each step along an edge costs 1.</p>"
         "<p>For every node, find the largest distance (in edges) from that node to any node of the tree. Return these values as an array in <strong>level-order</strong> of the real nodes, that is, in the same order in which the real (non-<code>-1</code>) entries appear in the input. The empty tree gives <code>[]</code>.</p>" + ENC +
         "<p>For <code>tree = [1, 2, 3, 4, 5]</code> the nodes in order are 1, 2, 3, 4, 5 and the answer is <code>[2, 2, 3, 3, 3]</code>: for example node 1 reaches node 4 in 2 steps, while node 4 needs 3 steps to reach node 3.</p>",
    constraints=_cons(),
    hints=["Running a breadth-first search from every node works, but it costs O(n<sup>2</sup>) in total, which is needless for a tree.",
           "Think about the diameter. For any node, one of the two end points of a longest path in the tree is always a farthest node from it.",
           "Find the two diameter end points <code>a</code> and <code>b</code> with BFS (BFS from any node to the farthest node <code>a</code>, then BFS from <code>a</code> to the farthest node <code>b</code>). The answer for a node is <code>max(dist(node, a), dist(node, b))</code>, so one more BFS from <code>b</code> finishes the job."],
    editorial=["A classic fact about trees: a farthest node from <em>any</em> node can be chosen among the two ends <code>a</code>, <code>b</code> of a diameter. So after finding a diameter, each node's eccentricity is the maximum of its distance to <code>a</code> and its distance to <code>b</code>.",
               "To find the diameter ends: BFS from any node (say the root) and take the farthest node as <code>a</code>; BFS from <code>a</code> and take the farthest node <code>b</code>. A third BFS from <code>b</code> gives the second set of distances. Three BFS passes over the n-1 edges give O(n) total time.",
               "The undirected adjacency list is built from the level-order array: the k-th real node has its children at slots <code>2k+1</code> and <code>2k+2</code>. Special cases: the empty tree gives an empty array, and a single node gives <code>[0]</code>."],
    time="O(n)", space="O(n)",
    solution=LINKS + '''def farthestDistances(tree):
    vals, left, right = _links(tree)
    n = len(vals)
    if n == 0:
        return []
    adj = [[] for _ in range(n)]
    for k in range(n):
        for c in (left[k], right[k]):
            if c != -1:
                adj[k].append(c)
                adj[c].append(k)

    def bfs(src):
        dist = [-1] * n
        dist[src] = 0
        order = [src]
        for x in order:
            for y in adj[x]:
                if dist[y] == -1:
                    dist[y] = dist[x] + 1
                    order.append(y)
        return dist

    d0 = bfs(0)
    a = d0.index(max(d0))
    da = bfs(a)
    b = da.index(max(da))
    db = bfs(b)
    return [max(da[i], db[i]) for i in range(n)]
''',
    tests=[], tier="extra",
)
_r = rnd(8109)
_P[-1]["tests"] = [[t] for t in BASE + [
    [1, 2, 3, 4, 5], [1, 2, -1, 3, -1, 4], [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15],
] + _big(8109)]


def _b_far(tree):
    root = _build(tree)
    nodes = _levelorder(root)
    idx = {id(x): i for i, x in enumerate(nodes)}
    adj = [[] for _ in nodes]
    for x in nodes:
        for c in (x.l, x.r):
            if c is not None:
                adj[idx[id(x)]].append(idx[id(c)])
                adj[idx[id(c)]].append(idx[id(x)])
    res = []
    for s in range(len(nodes)):
        dist = {s: 0}
        q = deque([s])
        while q:
            u = q.popleft()
            for v in adj[u]:
                if v not in dist:
                    dist[v] = dist[u] + 1
                    q.append(v)
        res.append(max(dist.values()))
    return res


def _v_far(tests):
    _v_trees(tests)
    assert len({len(t["expected"]) for t in tests}) >= 5


CHECKS["binary-tree-farthest-node-distances"] = (_b_far, _g_unbal, "exact")
VALIDATE["binary-tree-farthest-node-distances"] = _v_far

# ================================================================== HARD

# ---------------------------------------------------------------- count diameter paths
add(
    id="binary-tree-diameter-path-count", title="How Many Longest Paths?", diff="Hard", topic=TOPIC,
    fn="countDiameterPaths", params=[("tree", "int[]")], ret="int", cmp="exact",
    desc="<p>The <em>diameter</em> of a binary tree is the largest number of edges on a path between two nodes (a path may go up and then down). Count how many <strong>unordered pairs of distinct nodes</strong> are joined by a path with exactly that many edges. The pair <code>(u, v)</code> is the same pair as <code>(v, u)</code>.</p>"
         "<p>The empty tree and a tree with a single node have no pair of distinct nodes, so the answer is <code>0</code>.</p>" + ENC +
         "<p>For <code>tree = [1, 2, 3, 4, 5]</code> the diameter is 3 and exactly two pairs achieve it: nodes (4, 3) and (5, 3). For the perfect tree <code>[1, 2, 3, 4, 5, 6, 7]</code> the diameter is 4 and the pairs are (4,6), (4,7), (5,6), (5,7), so the answer is <code>4</code>.</p>",
    constraints=_cons(),
    hints=["First settle the diameter itself. Then think about which nodes can be the two ends of a longest path.",
           "Group the paths by their highest node (the node where the path turns). At a node you can combine the deepest descendants hanging off different child branches, or the node itself as one end.",
           "For every node keep two values: <code>dep</code> = distance to its deepest descendant, and <code>cnt</code> = how many descendants are at exactly that distance. At a node, the branches are: the node itself <code>(0, 1)</code>, and each child <code>(dep+1, cnt)</code>. Combine two different branches to get lengths <code>d1 + d2</code> with <code>c1 * c2</code> pairs."],
    editorial=["Every path has a unique highest node. For a node <code>x</code> the possible \"ends\" below it fall into at most three branches: the node itself (distance 0, one node), the left child side (distance <code>dep(left)+1</code>, <code>cnt(left)</code> nodes at that distance) and the right child side. A longest path peaking at <code>x</code> uses two different branches, each at its deepest level, so its length is <code>d1 + d2</code> and there are <code>c1 * c2</code> of them. Only pairs of branches are possible, so there are at most three pairs to try.",
               "Keep the global best length and the number of pairs reaching it. For each node compute the best length over its branch pairs; if it beats the global best, replace both numbers; if it ties, add the pair count. Only the deepest nodes of a branch matter: a path that ends higher up in a branch could be extended downwards, so it can never reach the global maximum.",
               "Then update the node's own <code>(dep, cnt)</code>: a leaf is <code>(0, 1)</code>; otherwise <code>dep</code> is the largest <code>dep(child)+1</code> and <code>cnt</code> sums the counts of the children reaching it. The whole computation is one bottom-up pass, O(n). The count is at most about 560,000 for 1,500 nodes."],
    time="O(n)", space="O(n)",
    solution=LINKS + '''def countDiameterPaths(tree):
    vals, left, right = _links(tree)
    n = len(vals)
    dep = [0] * n
    cnt = [1] * n
    best, ways = 0, 0
    for k in range(n - 1, -1, -1):
        branches = [(0, 1)]
        for c in (left[k], right[k]):
            if c != -1:
                branches.append((dep[c] + 1, cnt[c]))
        # longest paths that turn at k: pairs of different branches
        for i in range(len(branches)):
            for j in range(i + 1, len(branches)):
                length = branches[i][0] + branches[j][0]
                if length > best:
                    best, ways = length, branches[i][1] * branches[j][1]
                elif length == best and length > 0:
                    ways += branches[i][1] * branches[j][1]
        d = max(b[0] for b in branches)
        dep[k] = d
        cnt[k] = sum(b[1] for b in branches if b[0] == d)
    return ways
''',
    tests=[], tier="extra",
)
_r = rnd(8110)
_P[-1]["tests"] = [[t] for t in BASE + [
    [1, 2, 3, 4, 5], [1, 2, -1, 3, -1, 4], [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15],
    [1, 2, 3, 4, 5, -1, -1, 6, 7, 8, 9],
] + [_tree(_r, MAXN, "left", 0, MAXV), _perfect_big, _tree(_r, MAXN, "complete", 0, MAXV),
     _tree(_r, MAXN, "random", 0, MAXV)]]


def _b_dpaths(tree):
    nodes = _levelorder(_build(tree))
    n = len(nodes)
    if n < 2:
        return 0
    idx = {id(x): i for i, x in enumerate(nodes)}
    adj = [[] for _ in nodes]
    for x in nodes:
        for c in (x.l, x.r):
            if c is not None:
                adj[idx[id(x)]].append(idx[id(c)])
                adj[idx[id(c)]].append(idx[id(x)])
    best, pairs = 0, 0
    for s in range(n):
        dist = {s: 0}
        q = deque([s])
        while q:
            u = q.popleft()
            for v in adj[u]:
                if v not in dist:
                    dist[v] = dist[u] + 1
                    q.append(v)
        for t in range(s + 1, n):
            if dist[t] > best:
                best, pairs = dist[t], 1
            elif dist[t] == best:
                pairs += 1
    return pairs


def _v_dpaths(tests):
    _v_trees(tests)
    assert len({t["expected"] for t in tests}) >= 5
    assert any(t["expected"] > 10000 for t in tests), "want a large answer in the tests"


CHECKS["binary-tree-diameter-path-count"] = (_b_dpaths, _g_unbal, "exact")
VALIDATE["binary-tree-diameter-path-count"] = _v_dpaths

# ---------------------------------------------------------------- height after removing a subtree
add(
    id="binary-tree-height-after-subtree-removals", title="Tree Height After Removing a Subtree", diff="Hard", topic=TOPIC,
    fn="heightsAfterRemoval", params=[("tree", "int[]"), ("queries", "int[]")], ret="int[]", cmp="exact",
    desc="<p>The values in the tree <code>tree</code> are all <strong>distinct</strong>. The <em>height</em> of a tree is the number of edges on the longest path from the root down to a leaf (a tree with only a root has height <code>0</code>).</p>"
         "<p>Each entry of <code>queries</code> is the value of some node other than the root. For every query, imagine removing that node together with its whole subtree from the original tree, and report the height of what is left. The queries are <strong>independent</strong>: the tree is restored before the next one.</p>"
         "<p>Return an array with one height per query, in the same order.</p>" + ENC +
         "<p>For <code>tree = [1, 2, 3, 4, 5, -1, 6, 7]</code> (height 3, through 1 &rarr; 2 &rarr; 4 &rarr; 7) and <code>queries = [4, 2, 6, 3]</code> the answer is <code>[2, 2, 3, 3]</code>: removing 4 or 2 cuts the longest path and the next longest has 2 edges, while removing 6 or 3 does not touch it.</p>",
    constraints=["2 &le; number of nodes &le; 1,500", f"0 &le; node value &le; {MAXV:,}, and all node values are distinct",
                 "The array follows the encoding above exactly (valid level-order, no trailing -1)",
                 "1 &le; queries.length &le; 1,500", "Every query is the value of a node of the tree and is not the root's value; queries may repeat"],
    hints=["Recomputing the height after every removal costs O(n) per query, which is too slow if both the tree and the number of queries are large. Prepare something once and answer each query in O(1).",
           "Removing a subtree can only lower the height if its node was on the deepest path. Look at nodes on the same level as the removed node: some other node on that level may still lead just as deep.",
           "For each depth <code>d</code>, store the best and second best value of <code>depth + height</code> over all nodes at depth <code>d</code>. Removing node <code>x</code> at depth <code>d</code> leaves <code>max(d - 1, best of its level excluding x)</code>."],
    editorial=["Every root-to-leaf path passes through exactly one node on each level it reaches. If <code>x</code> is removed, the deepest remaining node is either reached through another node <code>y</code> at the same depth as <code>x</code> (it then has length <code>depth(y) + height(y)</code>) or it is at most the parent of <code>x</code>, at depth <code>depth(x) - 1</code>. Longer paths avoiding <code>x</code> must also pass through some node at <code>x</code>'s depth, unless they are shorter than that depth.",
               "So compute, for every node, its depth and its height (edges down to the deepest leaf) with two passes over the level-order array (forward for depth, backward for height). For each depth keep the two largest values of <code>depth + height</code> together with the node that owns the largest. A query for node <code>x</code> at depth <code>d</code> uses the best value of level <code>d</code> unless that is <code>x</code> itself, in which case it uses the second best (or nothing). The result is <code>max(d - 1, that value)</code>.",
               "Preparation is O(n) and every query is O(1). This is the key idea behind many \"answer each removal query\" tree problems: summarise each level by its top two candidates."],
    time="O(n + q)", space="O(n)",
    solution=LINKS + '''def heightsAfterRemoval(tree, queries):
    vals, left, right = _links(tree)
    n = len(vals)
    depth = [0] * n
    for k in range(n):
        for c in (left[k], right[k]):
            if c != -1:
                depth[c] = depth[k] + 1
    height = [0] * n
    for k in range(n - 1, -1, -1):
        for c in (left[k], right[k]):
            if c != -1:
                height[k] = max(height[k], height[c] + 1)
    top1 = {}   # depth -> (value, node)
    top2 = {}   # depth -> value
    for k in range(n):
        d = depth[k]
        v = depth[k] + height[k]
        if d not in top1 or v > top1[d][0]:
            if d in top1:
                top2[d] = top1[d][0]
            top1[d] = (v, k)
        elif v > top2.get(d, -1):
            top2[d] = v
    node_of = {vals[k]: k for k in range(n)}
    out = []
    for q in queries:
        k = node_of[q]
        d = depth[k]
        rest = top2.get(d, -1) if top1[d][1] == k else top1[d][0]
        out.append(max(d - 1, rest))
    return out
''',
    tests=[], tier="extra",
)
_r = rnd(8111)


def _q_for(r, arr, m):
    vals = [x for x in arr if x != -1]
    pool = vals[1:]
    return [r.choice(pool) for _ in range(m)]


_h_tests = [[[1, 2, 3, 4, 5, -1, 6, 7], [4, 2, 6, 3]], [[1, 2], [2]], [[5, 4, 3], [4, 3, 4]],
            [[1, -1, 2, -1, 3, -1, 4], [4, 3, 2]], [[8, 3, 10, 1, 6, -1, 14, -1, -1, 4, 7, 13], [3, 6, 14, 13, 1]],
            [[0, 1, 2, 3, 4, 5, 6], [1, 2, 3, 4, 5, 6]]]
for _n, _mode, _m in [(40, "random", 40), (60, "deep", 30), (80, "complete", 50)]:
    _a = _tree_distinct(_r, _n, _mode)
    _h_tests.append([_a, _q_for(_r, _a, _m)])
for _mode in ("left", "zig", "complete", "random"):
    _a = _tree_distinct(_r, MAXN, _mode)
    _h_tests.append([_a, _q_for(_r, _a, 400)])
_P[-1]["tests"] = _h_tests


def _b_hrem(tree, queries):
    root = _build(tree)

    def h(x, banned):
        if x is None or x.v == banned:
            return -1
        return 1 + max(h(x.l, banned), h(x.r, banned))

    return [h(root, q) for q in queries]


def _g_hrem(r):
    n = r.randint(2, 12)
    a = _tree_distinct(r, n, r.choice(MODES))
    return [a, _q_for(r, a, r.randint(1, 8))]


def _v_hrem(tests):
    for t in tests:
        arr, qs = t["args"]
        assert arr == _encode(_build(arr))
        vals = [x for x in arr if x != -1]
        assert 2 <= len(vals) <= MAXN and len(set(vals)) == len(vals), "values must be distinct"
        assert all(0 <= x <= MAXV for x in vals)
        assert 1 <= len(qs) <= 1500 and all(q in vals and q != vals[0] for q in qs)
    assert len({repr(t["expected"]) for t in tests}) >= 6


CHECKS["binary-tree-height-after-subtree-removals"] = (_b_hrem, _g_hrem, "exact")
VALIDATE["binary-tree-height-after-subtree-removals"] = _v_hrem
