"""Problems: tree traversals on level-order encoded binary trees (-1 = missing child). See data/lib.py for the registry."""
import sys
from collections import deque

from lib import add, rnd, CHECKS, VALIDATE, gen_arr  # noqa: F401
from lib import P as _P

sys.setrecursionlimit(20000)

TOPIC = "Trees"
MAXN = 1500      # maximum number of nodes in any tree
MAXV = 10000     # maximum node value
MOD = 10 ** 9 + 7

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


def _pre(root):
    """Nodes in preorder (iterative)."""
    out, st = [], ([root] if root else [])
    while st:
        x = st.pop()
        out.append(x)
        if x.r:
            st.append(x.r)
        if x.l:
            st.append(x.l)
    return out


def _post(root):
    """Nodes in postorder (iterative)."""
    out, st = [], ([root] if root else [])
    while st:
        x = st.pop()
        out.append(x)
        if x.l:
            st.append(x.l)
        if x.r:
            st.append(x.r)
    return out[::-1]


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
    for x in _pre(root):
        x.v = r.randint(lo, hi)
    return _encode(root)


def _utree_root(r, n, mode="random", hi=MAXV):
    """A tree whose node values are all distinct."""
    root = _shape(r, n, mode)
    for x, v in zip(_pre(root), r.sample(range(0, hi + 1), n)):
        x.v = v
    return root


def _utree(r, n, mode="random", hi=MAXV):
    return _encode(_utree_root(r, n, mode, hi))


def _gen(nmax=10, vmax=5, modes=MODES):
    def g(r):
        return [_tree(r, r.randint(0, nmax), r.choice(modes), 0, vmax)]
    return g


def _v_trees(tests):
    for t in tests:
        _check_tree(t["args"][0])


def _check_tree(arr):
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

BASE = [
    [], [0], [1, 2, 3], [1, -1, 2, -1, 3], [1, 2, -1, 3, -1, 4], [3, 9, 20, -1, -1, 15, 7],
    [1, 2, 3, 4, 5, 6, 7], [1, 2, 2, 3, 3, -1, -1, 4, 4], [5, 5, 5, 5, 5, 5, 5, 5],
]


def _bigs(seed, hi=MAXV, modes=("left", "random", "complete"), n=MAXN):
    r = rnd(seed)
    return [_tree(r, n, m, 0, hi) for m in modes]


# ================================================================== EASY

# ---------------------------------------------------------------- preorder
add(
    id="binary-tree-preorder-traversal", title="Binary Tree Preorder Traversal", diff="Easy", topic=TOPIC,
    fn="preorderTraversal", params=[("tree", "int[]")], ret="int[]", cmp="exact",
    desc="<p>Return the node values of a binary tree in <em>preorder</em>: first the root, then everything in the left subtree (in preorder), then everything in the right subtree (in preorder). The empty tree gives the empty array.</p>" + ENC +
         "<p>For <code>tree = [1, 2, 3, -1, 4]</code> the answer is <code>[1, 2, 4, 3]</code>. For <code>tree = [1, -1, 2, 3]</code> (root 1, no left child, right child 2 whose left child is 3) the answer is <code>[1, 2, 3]</code>.</p>"
         "<p>Try to do it without recursion, using an explicit stack.</p>",
    constraints=_cons(),
    hints=["Preorder means: visit the node first, then go into the left subtree, then into the right subtree.",
           "Recursion is the direct translation. To avoid it, use a stack that holds the nodes still waiting to be visited.",
           "Push the root. Repeat: pop a node, record its value, then push its <em>right</em> child and afterwards its <em>left</em> child, so that the left child is popped first."],
    editorial=["The recursive definition is three lines: record the node, recurse left, recurse right. An iterative version replaces the call stack with your own. Keep a stack of nodes that still have to be visited. Pop one, record it, and push its right child followed by its left child. Because a stack is last-in first-out, the left child comes out before the right one, and the whole left subtree is finished before the right child is touched.",
               "With the level-order array you do not need node objects: the k-th real node's children sit at slots <code>2k+1</code> and <code>2k+2</code>, so you can precompute for every real node the index of its left and right child and run the stack on indices. Every node is pushed and popped once: O(n) time, and the stack never holds more than the tree height plus one entry per pending right sibling, so O(n) space in the worst case."],
    time="O(n)", space="O(n)",
    solution=LINKS + '''def preorderTraversal(tree):
    vals, left, right = _links(tree)
    out = []
    stack = [0] if vals else []
    while stack:
        k = stack.pop()
        out.append(vals[k])
        if right[k] != -1:
            stack.append(right[k])
        if left[k] != -1:
            stack.append(left[k])
    return out
''',
    tests=[[t] for t in BASE + [[10, 5, -1, 5, -1, 5], [2, 1, 3, 0, -1, -1, 4]] + _bigs(9101)],
)


def _b_preorder(tree):
    out = []

    def go(x):
        if x:
            out.append(x.v)
            go(x.l)
            go(x.r)
    go(_build(tree))
    return out


CHECKS["binary-tree-preorder-traversal"] = (_b_preorder, _gen(), "exact")
VALIDATE["binary-tree-preorder-traversal"] = _v_trees

# ---------------------------------------------------------------- inorder
add(
    id="binary-tree-inorder-traversal", title="Binary Tree Inorder Traversal", diff="Easy", topic=TOPIC, tier="must",
    fn="inorderTraversal", params=[("tree", "int[]")], ret="int[]", cmp="exact",
    desc="<p>Return the node values of a binary tree in <em>inorder</em>: everything in the left subtree (in inorder), then the node itself, then everything in the right subtree (in inorder). The empty tree gives the empty array.</p>" + ENC +
         "<p>For <code>tree = [1, 2, 3, -1, 4]</code> the answer is <code>[2, 4, 1, 3]</code>. For <code>tree = [5, 8, 2, 7, -1, 4, 9]</code> the answer is <code>[7, 8, 5, 4, 2, 9]</code>.</p>"
         "<p>The recursive solution is easy; the goal is to do it iteratively with an explicit stack.</p>",
    constraints=_cons(),
    hints=["A node must be recorded <em>after</em> its whole left subtree, so you cannot record it when you first meet it.",
           "Walk down the left spine from the current node, remembering every node you pass on a stack.",
           "When you cannot go left any more, pop a node, record it, and continue with its right child (again going down its left spine). Stop when both the stack and the current node are empty."],
    editorial=["Inorder visits the left subtree first, so you must first dive as far left as possible, keeping the nodes you pass on a stack: they are waiting for their left subtree to finish. When the current node is missing, pop the top of the stack. That node has its left subtree completed, so record it, then move to its right child and repeat the dive.",
               "Each node is pushed once and popped once, so the running time is O(n); the stack holds at most one root-to-node path, which is O(height) and O(n) for a chain. This push-left-spine, pop, go-right loop is the template behind many other tree iterators (for example the binary search tree iterator), so it is worth knowing by heart."],
    time="O(n)", space="O(h)",
    solution=LINKS + '''def inorderTraversal(tree):
    vals, left, right = _links(tree)
    out = []
    stack = []
    x = 0 if vals else -1
    while stack or x != -1:
        while x != -1:
            stack.append(x)
            x = left[x]
        x = stack.pop()
        out.append(vals[x])
        x = right[x]
    return out
''',
    tests=[[t] for t in BASE + [[10, 5, -1, 5, -1, 5], [5, 8, 2, 7, -1, 4, 9]] + _bigs(9102)],
)


def _b_inorder(tree):
    out = []

    def go(x):
        if x:
            go(x.l)
            out.append(x.v)
            go(x.r)
    go(_build(tree))
    return out


CHECKS["binary-tree-inorder-traversal"] = (_b_inorder, _gen(), "exact")
VALIDATE["binary-tree-inorder-traversal"] = _v_trees

# ---------------------------------------------------------------- leaf sequence


def _with_leaves(r, leaves, mode, unary=0.12, hi=MAXV):
    """A tree whose leaves, read left to right, are exactly `leaves`; the shape is chosen by `mode`."""
    def val():
        return r.randint(0, hi)

    def split(lo, hi_):
        if hi_ - lo == 1:
            return _N(leaves[lo])
        if mode == "left":
            m = hi_ - 1
        elif mode == "right":
            m = lo + 1
        elif mode == "balanced":
            m = (lo + hi_) // 2
        else:
            m = r.randint(lo + 1, hi_ - 1)
        x = _N(val())
        x.l = go(lo, m)
        x.r = go(m, hi_)
        return x

    def go(lo, hi_):
        if r.random() < unary:
            x = _N(val())
            c = split(lo, hi_)
            if r.random() < 0.5:
                x.l = c
            else:
                x.r = c
            return x
        return split(lo, hi_)

    return _encode(go(0, len(leaves)))


def _leafpair(seed, L, ma, mb, vmax=3, change=None):
    r = rnd(seed)
    leaves = [r.randint(0, vmax) for _ in range(L)]
    a = _with_leaves(r, leaves, ma)
    if change == "last":
        leaves = leaves[:-1] + [leaves[-1] + 1]
    elif change == "swap":
        i = next(i for i in range(L - 1) if leaves[i] != leaves[i + 1])
        leaves[i], leaves[i + 1] = leaves[i + 1], leaves[i]
    elif change == "short":
        leaves = leaves[:-1]
    b = _with_leaves(r, leaves, mb)
    return [a, b]


add(
    id="leaf-similar-trees", title="Leaf-Similar Trees", diff="Easy", topic=TOPIC,
    fn="leafSimilar", params=[("a", "int[]"), ("b", "int[]")], ret="bool", cmp="exact",
    desc="<p>The <em>leaf sequence</em> of a binary tree is the list of the values of its leaves (nodes without any child), read from left to right. Two trees can look very different and still have the same leaf sequence.</p>"
         "<p>Given two binary trees <code>a</code> and <code>b</code>, return <code>true</code> if their leaf sequences are equal and <code>false</code> otherwise. The empty tree has an empty leaf sequence.</p>" + ENC +
         "<p>Both arguments use this encoding. For <code>a = [1, 2, 3]</code> and <code>b = [5, 8, -1, 2, 3]</code> both leaf sequences are <code>[2, 3]</code>, so the answer is <code>true</code>. For <code>a = [1, 2, 3]</code> and <code>b = [1, 3, 2]</code> the sequences are <code>[2, 3]</code> and <code>[3, 2]</code>, so the answer is <code>false</code>.</p>",
    constraints=["0 &le; number of nodes in each tree &le; 1,500", f"0 &le; node value &le; {MAXV:,}",
                 "Both arrays follow the encoding above exactly (valid level-order, no trailing -1)"],
    hints=["A leaf is a node with no left child and no right child. Be careful: a node with one child is not a leaf.",
           "Leaves are met in left-to-right order when you traverse the tree in preorder (or inorder), always going left before right.",
           "Collect the leaf sequence of each tree with an iterative preorder (stack: push right, then left) and compare the two lists."],
    editorial=["Any depth-first traversal that always visits the left subtree before the right one meets the leaves in left-to-right order, so collect the leaves of each tree during such a traversal and compare the two lists for equality. A node is a leaf exactly when it has neither child; a node with a single child must not be recorded.",
               "Both traversals are linear. If the trees are huge and the sequences differ early you could stop sooner by advancing the two traversals in lock-step, one leaf at a time, and returning false at the first mismatch; the worst case stays O(n + m), and this version uses only the stack space of the two traversals instead of storing complete leaf lists."],
    time="O(n + m)", space="O(n + m)",
    solution=LINKS + '''def leafSimilar(a, b):
    def leaves(t):
        vals, left, right = _links(t)
        out = []
        stack = [0] if vals else []
        while stack:
            k = stack.pop()
            if left[k] == -1 and right[k] == -1:
                out.append(vals[k])
            if right[k] != -1:
                stack.append(right[k])
            if left[k] != -1:
                stack.append(left[k])
        return out
    return leaves(a) == leaves(b)
''',
    tests=[[[1, 2, 3], [5, 8, -1, 2, 3]], [[1, 2, 3], [1, 3, 2]], [[], []], [[], [4]], [[7], [1, 7]], [[7], [1, 2]],
           [[1, 2, 3, 4, 5, 6, 7], [9, 9, 9, 4, 5, 6, 7]], [[1, 2, 3, 4, 5, 6, 7], [1, 2, 3, 4, 5, 6, 8]],
           [[3, 5, 1, 6, 2, 9, 8, -1, -1, 7, 4], [3, 5, 1, 6, 7, 4, 2, -1, -1, -1, -1, -1, -1, 9, 8]],
           [[5, 5, 5], [5, 5, -1, 5]], [[0], [0]], [[1, 2, -1, 3], [1, -1, 2, -1, 3]],
           _leafpair(9103, 520, "random", "left"), _leafpair(9104, 520, "balanced", "right", change="swap"),
           _leafpair(9105, 480, "left", "random", change="last")],
)


def _b_leafsim(a, b):
    def leaves(x):
        if x is None:
            return []
        if x.l is None and x.r is None:
            return [x.v]
        return leaves(x.l) + leaves(x.r)
    return leaves(_build(a)) == leaves(_build(b))


def _g_leafsim(r):
    L = r.randint(0, 6)
    leaves = [r.randint(0, 2) for _ in range(L)]
    modes = ["random", "left", "right", "balanced"]
    if L == 0:
        a = []
    else:
        a = _with_leaves(r, leaves, r.choice(modes), 0.3, 3)
    k = r.random()
    if L and k < 0.3:
        leaves = leaves[:]
        leaves[r.randrange(L)] = r.randint(0, 2)
    elif L and k < 0.4:
        leaves = leaves[:-1]
    elif k < 0.5:
        leaves = leaves + [r.randint(0, 2)]
    b = _with_leaves(r, leaves, r.choice(modes), 0.3, 3) if leaves else []
    return [a, b] if r.random() < 0.5 else [b, a]


def _v_leafsim(tests):
    trues = 0
    for t in tests:
        _check_tree(t["args"][0])
        _check_tree(t["args"][1])
        trues += t["expected"] is True
    assert 4 <= trues <= len(tests) - 4, "balance true/false answers"


CHECKS["leaf-similar-trees"] = (_b_leafsim, _g_leafsim, "exact")
VALIDATE["leaf-similar-trees"] = _v_leafsim

# ================================================================== MEDIUM

# ---------------------------------------------------------------- postorder
add(
    id="binary-tree-postorder-traversal", title="Binary Tree Postorder Traversal", diff="Medium", topic=TOPIC,
    fn="postorderTraversal", params=[("tree", "int[]")], ret="int[]", cmp="exact",
    desc="<p>Return the node values of a binary tree in <em>postorder</em>: everything in the left subtree (in postorder), then everything in the right subtree (in postorder), and the node itself last. The empty tree gives the empty array.</p>" + ENC +
         "<p>For <code>tree = [1, 2, 3, -1, 4]</code> the answer is <code>[4, 2, 3, 1]</code>. For <code>tree = [5, 8, 2, 7, -1, 4, 9]</code> the answer is <code>[7, 8, 4, 9, 2, 5]</code>.</p>"
         "<p>The recursive version is trivial. Solve it iteratively, with an explicit stack and without recursion.</p>",
    constraints=_cons(),
    hints=["A node is recorded only after both of its subtrees are finished, which makes the iterative version trickier than for preorder.",
           "Look at the mirror of preorder: visiting node, then <em>right</em> subtree, then <em>left</em> subtree. How does this sequence relate to postorder?",
           "Postorder is exactly the reverse of &ldquo;node, right, left&rdquo;. Run the iterative preorder with the two pushes swapped (push left first, then right) and reverse the result."],
    editorial=["Reverse the postorder sequence (left, right, node) and you get (node, right, left). That is a preorder in which the right child is explored before the left child, which a stack handles easily: pop a node, record it, push its left child, then push its right child (so the right child is popped first). At the end reverse the recorded list.",
               "The cost is O(n) time and O(n) space. A single-stack alternative keeps a pointer to the last visited node and records a node only when its right child is missing or was just visited; it saves the final reversal but is much easier to get wrong, so the reversal trick is the better choice in an interview."],
    time="O(n)", space="O(n)",
    solution=LINKS + '''def postorderTraversal(tree):
    vals, left, right = _links(tree)
    out = []
    stack = [0] if vals else []
    while stack:
        k = stack.pop()
        out.append(vals[k])
        if left[k] != -1:
            stack.append(left[k])
        if right[k] != -1:
            stack.append(right[k])
    out.reverse()
    return out
''',
    tests=[[t] for t in BASE + [[10, 5, -1, 5, -1, 5], [5, 8, 2, 7, -1, 4, 9]] + _bigs(9106)],
)


def _b_postorder(tree):
    out = []

    def go(x):
        if x:
            go(x.l)
            go(x.r)
            out.append(x.v)
    go(_build(tree))
    return out


CHECKS["binary-tree-postorder-traversal"] = (_b_postorder, _gen(), "exact")
VALIDATE["binary-tree-postorder-traversal"] = _v_trees

# ---------------------------------------------------------------- boundary
add(
    id="binary-tree-boundary-traversal", title="Boundary of a Binary Tree", diff="Medium", topic=TOPIC,
    fn="boundaryTraversal", params=[("tree", "int[]")], ret="int[]", cmp="exact",
    desc="<p>Walk once around the outside of a binary tree, anticlockwise, and report the values of the nodes on the boundary. The boundary is the concatenation of four parts, with no node listed twice:</p>"
         "<ol><li>the root;</li>"
         "<li>the <strong>left boundary</strong>, top to bottom: start at the root's left child (if there is one) and keep stepping to the left child, or to the right child when there is no left child, until you reach a leaf. Every node on this walk <em>except the leaf</em> belongs to the left boundary. If the root has no left child the left boundary is empty;</li>"
         "<li>all <strong>leaves</strong> (nodes with no children), from left to right;</li>"
         "<li>the <strong>right boundary</strong>, bottom to top: defined like the left one but starting at the root's right child and preferring the right child over the left; the final leaf is excluded and the nodes are listed in reverse order (deepest first).</li></ol>"
         "<p>If the root itself is a leaf the answer is just <code>[root]</code>. The empty tree gives the empty array.</p>" + ENC +
         "<p>For <code>tree = [1, -1, 2, 3, 4]</code> the answer is <code>[1, 3, 4, 2]</code>: the root 1, an empty left boundary, the leaves 3 and 4, and the right boundary <code>[2]</code>. For <code>tree = [1, 2, 3, 4, 5, 6, 7]</code> it is <code>[1, 2, 4, 5, 6, 7, 3]</code>.</p>",
    constraints=_cons(),
    hints=["Split the work into three independent parts: the left edge, the leaves, and the right edge. Handle the root and the empty-tree and single-node cases separately.",
           "For the left edge, walk down from the root's left child, preferring left children, and stop at a leaf without recording it. The right edge is the mirror image; collect it top-down and reverse it at the end.",
           "Collect the leaves with any traversal that visits left before right (iterative preorder). Because leaves are excluded from both edges, no value is repeated. Output: root, left edge, leaves, reversed right edge."],
    editorial=["The three parts can be computed independently. The left edge is a single downward walk that prefers left children (falling back to the right child when the left one is missing) and records every non-leaf node it meets. The right edge is the same walk with the roles of left and right swapped; because it has to be reported bottom-up, collect it in a list and reverse it. The leaves are obtained by a depth-first traversal that visits the left child first and records nodes without children.",
               "Pay attention to the corner cases: a root that is a leaf (the answer is just that root), a root with only one child (a root with only a right child has an empty left boundary, and the right child starts the right boundary or is a leaf), and the rule that leaves never appear in an edge, which is what prevents duplicates. Everything is a single pass over the tree: O(n) time, O(n) space for the stack and output."],
    time="O(n)", space="O(n)",
    solution=LINKS + '''def boundaryTraversal(tree):
    vals, left, right = _links(tree)
    if not vals:
        return []

    def leaf(k):
        return left[k] == -1 and right[k] == -1

    if leaf(0):
        return [vals[0]]
    out = [vals[0]]
    k = left[0]
    while k != -1 and not leaf(k):
        out.append(vals[k])
        k = left[k] if left[k] != -1 else right[k]
    stack = [0]
    while stack:
        k = stack.pop()
        if leaf(k):
            out.append(vals[k])
        else:
            if right[k] != -1:
                stack.append(right[k])
            if left[k] != -1:
                stack.append(left[k])
    tail = []
    k = right[0]
    while k != -1 and not leaf(k):
        tail.append(vals[k])
        k = right[k] if right[k] != -1 else left[k]
    out.extend(reversed(tail))
    return out
''',
    tests=[[t] for t in BASE + [[1, -1, 2, 3, 4], [1, 2, -1, 3, -1, 4], [1, -1, 2, -1, 3], [1, 2, 3, -1, 4, 5, -1, -1, -1, 6, 7],
                                 [10, 20, 30, 40, -1, -1, 50, -1, 60, 70, -1, -1, 80]] + _bigs(9107, modes=("zig", "random", "complete"))],
)


def _b_boundary(tree):
    root = _build(tree)
    if root is None:
        return []
    res = [root.v]
    if root.l is None and root.r is None:
        return res

    def leaf(x):
        return x.l is None and x.r is None

    def go(x, lb, rb):
        if x is None:
            return
        if leaf(x) or lb:
            res.append(x.v)
        go(x.l, lb, rb and x.r is None)
        go(x.r, lb and x.l is None, rb)
        if rb and not leaf(x):
            res.append(x.v)
    go(root.l, True, False)
    go(root.r, False, True)
    return res


CHECKS["binary-tree-boundary-traversal"] = (_b_boundary, _gen(11, 5), "exact")
VALIDATE["binary-tree-boundary-traversal"] = _v_trees

# ---------------------------------------------------------------- vertical order
add(
    id="binary-tree-vertical-order", title="Vertical Order Traversal of a Binary Tree", diff="Medium", topic=TOPIC,
    fn="verticalOrder", params=[("tree", "int[]")], ret="int[][]", cmp="exact",
    desc="<p>Give every node a <em>column</em>: the root is in column <code>0</code>, the left child of a node in column <code>c</code> is in column <code>c - 1</code>, and its right child is in column <code>c + 1</code>.</p>"
         "<p>Return the node values grouped by column, with the columns listed from the leftmost to the rightmost. Inside one column the values go from top to bottom (by depth); two nodes of the same column that are at the same depth are listed from left to right. The empty tree gives <code>[]</code>.</p>" + ENC +
         "<p>For <code>tree = [3, 9, 20, -1, -1, 15, 7]</code> the columns are <code>-1: [9]</code>, <code>0: [3, 15]</code>, <code>1: [20]</code>, <code>2: [7]</code>, so the answer is <code>[[9], [3, 15], [20], [7]]</code>.</p>",
    constraints=_cons(),
    hints=["First find a way to compute the column of every node from its parent's column.",
           "If you visit nodes level by level (the array is already in that order!), then within every column the values arrive exactly in the required order: top to bottom, and left to right on the same level.",
           "Walk the real nodes in array order, derive each child's column from the parent's, and append every value to a list stored under its column. At the end read the lists from the smallest column to the largest."],
    editorial=["A breadth-first traversal is the natural fit. It visits nodes level by level and, inside a level, from left to right, which is precisely the tie-breaking the problem asks for. So it is enough to keep a dictionary from column to the list of values seen so far, append each visited node to its column's list, and finally output the lists sorted by column number.",
               "The encoded array is already a level-order listing, so no queue is needed: the k-th real node has its children at slots <code>2k+1</code> and <code>2k+2</code>, and the parent always precedes its children. Only the bucket lists need sorting by key, which costs O(c log c) for c distinct columns (or O(n) if you track the minimum and maximum column and use an array). Total O(n) to O(n log n) time and O(n) space."],
    time="O(n log n)", space="O(n)",
    solution=LINKS + '''def verticalOrder(tree):
    vals, left, right = _links(tree)
    if not vals:
        return []
    col = [0] * len(vals)
    cols = {}
    for k in range(len(vals)):
        cols.setdefault(col[k], []).append(vals[k])
        if left[k] != -1:
            col[left[k]] = col[k] - 1
        if right[k] != -1:
            col[right[k]] = col[k] + 1
    return [cols[c] for c in sorted(cols)]
''',
    tests=[[t] for t in BASE + [[1, 2, 3, 4, 6, 5, 7], [1, -1, 2, 3, -1, 4, -1, 5], [9, 8, -1, -1, 7, 6], [4, 2, 6, 1, 3, 5, 7, 0, -1, -1, -1, -1, -1, -1, 8]] + _bigs(9108, modes=("zig", "random", "complete"))],
)


def _b_vertical(tree):
    items = []
    rank = []

    def go(x, c, d):
        if x:
            go(x.l, c - 1, d + 1)
            rank.append(0)
            items.append((c, d, len(rank), x.v))   # len(rank) = inorder position: left-to-right inside a level
            go(x.r, c + 1, d + 1)
    go(_build(tree), 0, 0)
    items.sort()
    out = {}
    for c, d, _, v in items:
        out.setdefault(c, []).append(v)
    return [out[c] for c in sorted(out)]


CHECKS["binary-tree-vertical-order"] = (_b_vertical, _gen(11, 9), "exact")
VALIDATE["binary-tree-vertical-order"] = _v_trees

# ---------------------------------------------------------------- diagonal sums
add(
    id="binary-tree-diagonal-sums", title="Diagonal Sums of a Binary Tree", diff="Medium", topic=TOPIC,
    fn="diagonalSums", params=[("tree", "int[]")], ret="int[]", cmp="exact",
    desc="<p>Cut a binary tree into <em>diagonals</em> that run from the upper left to the lower right. The root is on diagonal <code>0</code>; the right child of a node is on the same diagonal as the node, and the left child of a node is on the next diagonal (one more than the node's diagonal).</p>"
         "<p>Return the array whose entry <code>d</code> is the sum of the values of all nodes on diagonal <code>d</code>, for <code>d = 0, 1, 2, ...</code> up to the last non-empty diagonal. The empty tree gives <code>[]</code>.</p>" + ENC +
         "<p>For <code>tree = [8, 3, 10, 1, 6, -1, 14, -1, -1, 4, 7, 13]</code> diagonal 0 holds 8, 10, 14; diagonal 1 holds 3, 6, 7, 13; diagonal 2 holds 1, 4. The answer is <code>[32, 29, 5]</code>.</p>",
    constraints=_cons(["Every sum fits comfortably in a 32-bit integer"]),
    hints=["Every node gets a diagonal number that depends only on its parent's number and on whether it is a left or a right child.",
           "The right child keeps the diagonal of its parent; the left child adds one. Parents come before their children in level order.",
           "Walk the real nodes in array order, pass the diagonal number down to the children, and add each value into <code>sums[diagonal]</code> (extend the list when a new diagonal appears)."],
    editorial=["Assign each node a diagonal number: <code>diag(root) = 0</code>, <code>diag(right) = diag(parent)</code>, <code>diag(left) = diag(parent) + 1</code>. Then the answer is just the sum of the values grouped by that number. Any traversal that visits a parent before its children can compute the numbers; the level-order array does that for free, so one left-to-right pass with an array of diagonals is enough.",
               "Equivalently, you can imagine following the right chain from the root, then from every node on it going to its left child and following that node's right chain, and so on: each chain is one diagonal. Because every diagonal is reached from the previous one, the diagonal numbers are consecutive and the answer has no gaps. Time and space are O(n)."],
    time="O(n)", space="O(n)",
    solution=LINKS + '''def diagonalSums(tree):
    vals, left, right = _links(tree)
    n = len(vals)
    diag = [0] * n
    sums = []
    for k in range(n):
        d = diag[k]
        while len(sums) <= d:
            sums.append(0)
        sums[d] += vals[k]
        if right[k] != -1:
            diag[right[k]] = d
        if left[k] != -1:
            diag[left[k]] = d + 1
    return sums
''',
    tests=[[t] for t in BASE + [[8, 3, 10, 1, 6, -1, 14, -1, -1, 4, 7, 13], [1, 2, -1, 3, -1, 4], [1, -1, 2, -1, 3, -1, 4]] + _bigs(9109, modes=("zig", "random", "left"))],
)


def _b_diag(tree):
    acc = {}

    def go(x, d):
        if x:
            acc[d] = acc.get(d, 0) + x.v
            go(x.l, d + 1)
            go(x.r, d)
    go(_build(tree), 0)
    return [acc[d] for d in range(len(acc))]


CHECKS["binary-tree-diagonal-sums"] = (_b_diag, _gen(11, 9), "exact")
VALIDATE["binary-tree-diagonal-sums"] = _v_trees

# ---------------------------------------------------------------- inorder successors


def _succ_tests():
    r = rnd(9110)
    out = []
    for t in [[1], [4, 2, 6, 1, 3, 5, 7], [5, 8, 2, 7, -1, 4, 9], [1, 2, -1, 3, -1, 4], [1, -1, 2, -1, 3]]:
        vs = [x for x in t if x != -1]
        out.append([t, vs[:] if len(vs) <= 8 else r.sample(vs, 8)])
    for mode, n, qn in (("left", 12, 12), ("right", 10, 6), ("random", 40, 40), ("complete", 31, 25)):
        t = _utree(r, n, mode, 99)
        vs = [x for x in t if x != -1]
        out.append([t, [r.choice(vs) for _ in range(qn)]])
    for mode in ("random", "left", "complete"):
        t = _utree(r, MAXN, mode)
        vs = [x for x in t if x != -1]
        out.append([t, [r.choice(vs) for _ in range(MAXN)]])
    return out


add(
    id="binary-tree-inorder-successors", title="Inorder Successors in a Binary Tree", diff="Medium", topic=TOPIC,
    fn="inorderSuccessors", params=[("tree", "int[]"), ("queries", "int[]")], ret="int[]", cmp="exact",
    desc="<p>In the inorder sequence of a binary tree (left subtree, node, right subtree) the <em>successor</em> of a node is the node that comes right after it. Note that the tree is an ordinary binary tree, <strong>not</strong> a search tree, so values are not sorted.</p>"
         "<p>All node values of <code>tree</code> are distinct. For every value <code>q</code> in <code>queries</code> (each of them is the value of some node in the tree) report the value of the inorder successor of that node, or <code>-1</code> if the node is the last one in inorder. Return the answers in the order of the queries; the same value may be queried several times.</p>" + ENC +
         "<p>For <code>tree = [5, 8, 2, 7, -1, 4, 9]</code> the inorder sequence is <code>7, 8, 5, 4, 2, 9</code>. For <code>queries = [8, 9, 4]</code> the answer is <code>[5, -1, 2]</code>.</p>",
    constraints=["1 &le; number of nodes &le; 1,500", f"0 &le; node value &le; {MAXV:,}, and all node values are distinct",
                 "1 &le; queries.length &le; 1,500", "Every query value occurs in the tree",
                 "The tree array follows the encoding above exactly (valid level-order, no trailing -1)"],
    hints=["In a search tree you could use ordering to find a successor. Here you cannot: the structure of the tree is all you have.",
           "The successor of a node is simply the next element of the inorder sequence, so one traversal gives the answer for every node at once.",
           "Compute the inorder sequence once (iteratively), store <code>next[value]</code> for consecutive pairs (and -1 for the last one), then answer each query by a lookup."],
    editorial=["For a single query you could reason locally: if the node has a right subtree the successor is the leftmost node of that subtree; otherwise it is the nearest ancestor of which the node lies in the left subtree. That needs parent pointers or a root-to-node path. With many queries it is simpler and faster to produce the whole inorder sequence once.",
               "Run the iterative inorder traversal, remember the previous value, and fill a dictionary <code>succ[prev] = current</code> for every consecutive pair. The last value gets <code>-1</code>. Because values are distinct the dictionary is unambiguous, and every query becomes a constant-time lookup. Total O(n + q) time and O(n) space."],
    time="O(n + q)", space="O(n)",
    solution=LINKS + '''def inorderSuccessors(tree, queries):
    vals, left, right = _links(tree)
    order = []
    stack = []
    x = 0 if vals else -1
    while stack or x != -1:
        while x != -1:
            stack.append(x)
            x = left[x]
        x = stack.pop()
        order.append(vals[x])
        x = right[x]
    succ = {}
    for i, v in enumerate(order):
        succ[v] = order[i + 1] if i + 1 < len(order) else -1
    return [succ[q] for q in queries]
''',
    tests=_succ_tests(),
)


def _b_succ(tree, queries):
    root = _build(tree)
    seq = []

    def go(x):
        if x:
            go(x.l)
            seq.append(x.v)
            go(x.r)
    go(root)
    return [seq[seq.index(q) + 1] if seq.index(q) + 1 < len(seq) else -1 for q in queries]


def _g_succ(r):
    n = r.randint(1, 9)
    t = _utree(r, n, r.choice(MODES), 20)
    vs = [x for x in t if x != -1]
    return [t, [r.choice(vs) for _ in range(r.randint(1, 6))]]


def _v_succ(tests):
    for t in tests:
        tree, queries = t["args"]
        _check_tree(tree)
        vs = [x for x in tree if x != -1]
        assert 1 <= len(vs) and len(set(vs)) == len(vs), "values must be distinct"
        assert 1 <= len(queries) <= 1500 and all(q in set(vs) for q in queries)


CHECKS["binary-tree-inorder-successors"] = (_b_succ, _g_succ, "exact")
VALIDATE["binary-tree-inorder-successors"] = _v_succ

# ---------------------------------------------------------------- valid preorder serialization


def _pre_nulls(root):
    """Preorder with an explicit -1 for every missing child."""
    out, st = [], [root]
    while st:
        x = st.pop()
        if x is None:
            out.append(-1)
        else:
            out.append(x.v)
            st.append(x.r)
            st.append(x.l)
    return out


def _ser_tests():
    out = [[[-1]], [[]], [[7]], [[1, -1]], [[1, -1, -1]], [[1, 2, -1, -1, 3, -1, -1]], [[5, 1, -1, -1, 7, -1]],
           [[-1, 5, -1, -1]], [[9, 3, 4, -1, -1, 1, -1, -1, 2, -1, 6, -1, -1]], [[1, -1, 2, -1, 3, -1, -1]],
           [[1, 2, -1, -1, -1]], [[0, 0, 0, -1, -1, -1]], [[3, -1, -1, -1]]]
    r = rnd(9111)
    for n, mode in ((MAXN, "random"), (MAXN, "left"), (MAXN, "zig"), (800, "complete")):
        s = _pre_nulls(_utree_root(r, n, mode))
        out.append([s])
        if n == MAXN and mode == "random":
            out.append([s[:-1]])
        elif mode == "zig":
            out.append([s + [-1]])
        elif mode == "left":
            i = max(j for j, x in enumerate(s) if x == -1 and j < len(s) - 1)
            t = s[:]
            t[i] = 17
            out.append([t])
    return out


add(
    id="valid-preorder-null-serialization", title="Valid Preorder Serialization", diff="Medium", topic=TOPIC,
    fn="isValidPreorder", params=[("seq", "int[]")], ret="bool", cmp="exact",
    desc="<p>A binary tree can be written down by a preorder walk that also records the empty spots: write the node's value, then the serialization of its left child, then the serialization of its right child, and write <code>-1</code> in place of every missing child. So a single node <code>7</code> is <code>[7, -1, -1]</code>, and the empty tree is <code>[-1]</code>. Real node values are non-negative.</p>"
         "<p>Given an integer array <code>seq</code>, decide whether it is the serialization of <em>some</em> binary tree. It must describe one complete tree: nothing may be missing at the end and nothing may be left over. The empty array is not a valid serialization.</p>"
         "<p>For example <code>[5, 1, -1, -1, 7, -1, -1]</code> is valid (root 5 with children 1 and 7), <code>[5, 1, -1, -1, 7, -1]</code> is not (the right child of 7 is missing), and <code>[-1, 5, -1, -1]</code> is not (the first <code>-1</code> already completes the tree).</p>"
         "<p>Do not rebuild the tree; a single pass with O(1) extra memory is enough.</p>",
    constraints=["0 &le; seq.length &le; 6,000", f"-1 &le; seq[i] &le; {MAXV:,}", "-1 stands for a missing child, every other value is a real node"],
    hints=["Think about how many entries the rest of the array still has to supply while you read it from left to right.",
           "Keep a counter of &ldquo;open slots&rdquo;. At the beginning exactly one slot is open: the root. Reading an element fills one slot.",
           "A real node fills one slot and opens two new ones (its children); a <code>-1</code> only fills a slot. If you ever need a slot while none is open, the answer is false; at the end exactly zero slots must remain."],
    editorial=["Count the open slots. Initially there is one: the place for the root. Every element of the array must go into an open slot, otherwise the sequence has extra data (return false as soon as you meet an element while the count is zero). A value other than <code>-1</code> is a real node: it uses up one slot and creates two new ones, one for each child, so the net change is +1. A <code>-1</code> only consumes a slot, net change -1.",
               "After the last element, the serialization is complete exactly when no slot is left open. A short array leaves slots open, a long one runs out of slots early. This is a single left-to-right scan, O(n) time and O(1) space; the preorder structure guarantees that the order in which slots are filled does not matter for the count. The empty array fails because the root slot stays open."],
    time="O(n)", space="O(1)",
    solution='''def isValidPreorder(seq):
    slots = 1
    for x in seq:
        if slots == 0:
            return False
        slots -= 1
        if x != -1:
            slots += 2
    return slots == 0
''',
    tests=_ser_tests(),
)


def _b_ser(seq):
    pos = [0]

    def parse():
        if pos[0] >= len(seq):
            return False
        x = seq[pos[0]]
        pos[0] += 1
        if x == -1:
            return True
        return parse() and parse()
    return parse() and pos[0] == len(seq)


def _g_ser(r):
    k = r.random()
    if k < 0.4:
        n = r.randint(0, 5)
        s = _pre_nulls(_utree_root(r, n, r.choice(MODES), 6))
        m = r.random()
        if m < 0.25 and s:
            s = s[:-1]
        elif m < 0.4:
            s = s + [r.choice([-1, 3])]
        elif m < 0.6 and s:
            s[r.randrange(len(s))] = r.choice([-1, 2])
        return [s]
    return [[r.choice([-1, -1, 4]) for _ in range(r.randint(0, 9))]]


def _v_ser(tests):
    for t in tests:
        s = t["args"][0]
        assert 0 <= len(s) <= 6000 and all(-1 <= x <= MAXV for x in s)
    answers = [t["expected"] for t in tests]
    assert 5 <= sum(answers) <= len(answers) - 5


CHECKS["valid-preorder-null-serialization"] = (_b_ser, _g_ser, "exact")
VALIDATE["valid-preorder-null-serialization"] = _v_ser

# ================================================================== HARD

# ---------------------------------------------------------------- vertical order with value tie-break
add(
    id="binary-tree-vertical-order-sorted", title="Vertical Order with Sorted Ties", diff="Hard", topic=TOPIC, tier="extra",
    fn="verticalOrderSorted", params=[("tree", "int[]")], ret="int[][]", cmp="exact",
    desc="<p>Place every node of a binary tree at a coordinate <code>(row, column)</code>: the root is at <code>(0, 0)</code>; the left child of a node at <code>(row, col)</code> is at <code>(row + 1, col - 1)</code> and its right child is at <code>(row + 1, col + 1)</code>.</p>"
         "<p>Report the values column by column, from the smallest column number to the largest. Inside a column list the nodes by increasing row; if several nodes of the same column are in the <em>same row</em>, list them by increasing value (equal values simply appear next to each other). The empty tree gives <code>[]</code>.</p>" + ENC +
         "<p>For <code>tree = [1, 2, 3, 4, 6, 5, 7]</code> the nodes 5 and 6 share the position row 2, column 0 and are ordered by value, so the answer is <code>[[4], [2], [1, 5, 6], [3], [7]]</code>. (With &ldquo;left to right&rdquo; tie-breaking, the middle column would be <code>[1, 6, 5]</code>.)</p>",
    constraints=_cons(["Values may repeat"]),
    hints=["Give each node a triple of (column, row, value) and think about which ordering of the triples gives exactly the requested output.",
           "Sorting the triples lexicographically by column, then row, then value already puts everything in the right order. A plain BFS is no longer enough because of the value tie-break.",
           "Traverse the tree computing row and column for each node, collect the triples, sort them, and cut the sorted list into groups of equal column."],
    editorial=["The required order is exactly the lexicographic order on <code>(column, row, value)</code>. So compute the row and the column of every node (parents are always listed before children in the level-order array, which makes this one pass), put the triples into a list, sort it, and then split the sorted list into groups that share a column value.",
               "Sorting costs O(n log n). Compared with the version where ties are resolved from left to right, the difference is that two nodes can only compete when they have the same row <em>and</em> the same column, and then the smaller value must go first, so the left-to-right order of a plain level-order walk cannot be relied on. An alternative that avoids the global sort is to keep a bucket per column and sort each bucket, but the single sort is simplest."],
    time="O(n log n)", space="O(n)",
    solution=LINKS + '''def verticalOrderSorted(tree):
    vals, left, right = _links(tree)
    n = len(vals)
    if n == 0:
        return []
    col = [0] * n
    row = [0] * n
    items = []
    for k in range(n):
        items.append((col[k], row[k], vals[k]))
        if left[k] != -1:
            col[left[k]] = col[k] - 1
            row[left[k]] = row[k] + 1
        if right[k] != -1:
            col[right[k]] = col[k] + 1
            row[right[k]] = row[k] + 1
    items.sort()
    out = []
    prev = None
    for c, _, v in items:
        if c != prev:
            out.append([])
            prev = c
        out[-1].append(v)
    return out
''',
    tests=[[t] for t in BASE + [[1, 2, 3, 4, 6, 5, 7], [0, 1, 1, 2, 3, 3, 2, 5, 4, 4, 5]] + _bigs(9112, hi=6, modes=("random", "complete", "zig"))],
)


def _b_vsorted(tree):
    acc = {}

    def go(x, c, d):
        if x:
            acc.setdefault(c, []).append((d, x.v))
            go(x.l, c - 1, d + 1)
            go(x.r, c + 1, d + 1)
    go(_build(tree), 0, 0)
    return [[v for _, v in sorted(acc[c])] for c in sorted(acc)]


CHECKS["binary-tree-vertical-order-sorted"] = (_b_vsorted, _gen(12, 3), "exact")
VALIDATE["binary-tree-vertical-order-sorted"] = _v_trees

# ---------------------------------------------------------------- trees with the same preorder and postorder


def _pp_args(root):
    return [[x.v for x in _pre(root)], [x.v for x in _post(root)]]


def _pp_tests():
    r = rnd(9113)
    out = [[[], []], [[4], [4]], [[1, 2, 3], [3, 2, 1]], [[1, 2, 3], [2, 3, 1]], [[1, 2, 3, 4], [3, 4, 2, 1]],
           [[1, 2, 4, 5, 3], [4, 5, 2, 3, 1]], [[1, 2], [2, 1]], [[7, 3, 9, 1, 5], [9, 3, 5, 1, 7]]]
    for n, mode in ((9, "random"), (15, "complete"), (40, "random"), (120, "deep")):
        out.append(_pp_args(_utree_root(r, n, mode)))
    for n, mode in ((MAXN, "left"), (MAXN, "zig"), (MAXN, "random")):
        out.append(_pp_args(_utree_root(r, n, mode)))
    return out


add(
    id="trees-with-same-preorder-postorder", title="Count Trees with Given Preorder and Postorder", diff="Hard", topic=TOPIC, tier="extra",
    fn="countTrees", params=[("preorder", "int[]"), ("postorder", "int[]")], ret="int", cmp="exact",
    desc="<p>A binary tree with pairwise distinct node values is described by two traversals: its <em>preorder</em> (node, left subtree, right subtree) and its <em>postorder</em> (left subtree, right subtree, node). The two arrays are guaranteed to be the preorder and the postorder of at least one binary tree.</p>"
         "<p>Different trees can share both traversals. A node that has exactly one child may hold that child on its left or on its right, and the two traversals do not tell which. Count how many different binary trees (a left child and a right child are different things) have exactly this preorder and this postorder. Return the count modulo <code>1,000,000,007</code>. Two empty arrays describe the empty tree, which counts as one tree.</p>"
         "<p>For <code>preorder = [1, 2, 3]</code> and <code>postorder = [3, 2, 1]</code> the tree is a chain 1 &rarr; 2 &rarr; 3 and each of the two links can go left or right: the answer is <code>4</code>. For <code>postorder = [2, 3, 1]</code> the root has two children and the answer is <code>1</code>.</p>",
    constraints=["0 &le; preorder.length = postorder.length &le; 1,500", f"0 &le; value &le; {MAXV:,}, all values distinct",
                 "The arrays are the preorder and postorder of at least one binary tree"],
    hints=["Consider one node and look at the traversals restricted to its subtree: where do its children show up in each array?",
           "The first child of a node is the element right after it in the preorder; the last child is the element right before it in the postorder. If they are the same element, the node has a single child, which could be on either side.",
           "If they differ, the node has two children and the split of the traversals is forced. So the answer is 2<sup>k</sup>, where k is the number of nodes with exactly one child. Detect them with a position table of the postorder."],
    editorial=["Look at a node <code>u</code> with a non-empty subtree. In the preorder, the element after <code>u</code> is the root of its first child subtree, call it <code>a</code> (the left child if it exists, otherwise the right one). In the postorder, the element just before <code>u</code> is the root of the <em>last</em> child subtree, <code>b</code> (the right child if it exists, otherwise the left one). If <code>u</code> has two children then <code>a</code> is the left root and <code>b</code> the right root, and they differ. If <code>u</code> has one child both equal that child.",
               "When <code>a != b</code> the structure below <code>u</code> is completely determined: the left subtree is the prefix of the preorder starting at <code>a</code> and the prefix of the postorder ending at <code>a</code>, which fixes its size. When <code>a == b</code> the single child can be attached on either side, giving a factor 2, and the rest of the structure is determined recursively. For a leaf the element after it in the preorder cannot be the element before it in the postorder (that node would have to be both a descendant of the leaf and not), so there is no false match.",
               "Therefore the answer is 2<sup>k</sup> modulo 1,000,000,007 where k is the number of indices <code>i</code> with <code>pos[preorder[i+1]] = pos[preorder[i]] - 1</code>, <code>pos</code> being the index of a value in the postorder. One pass with a dictionary: O(n) time and space."],
    time="O(n)", space="O(n)",
    solution='''def countTrees(preorder, postorder):
    MOD = 1_000_000_007
    pos = {v: i for i, v in enumerate(postorder)}
    single = 0
    for i in range(len(preorder) - 1):
        if pos[preorder[i + 1]] == pos[preorder[i]] - 1:
            single += 1
    return pow(2, single, MOD)
''',
    tests=_pp_tests(),
)


def _b_pp(pre, post):
    def ways(a, b):
        if not a:
            return 1
        if a[0] != b[-1] or len(a) != len(b):
            return 0
        n = len(a)
        total = 0
        for k in range(n):   # size of the left subtree
            if set(a[1:1 + k]) == set(b[:k]) and set(a[1 + k:]) == set(b[k:n - 1]):
                total += ways(a[1:1 + k], b[:k]) * ways(a[1 + k:], b[k:n - 1])
        return total % MOD
    return ways(pre, post)


def _g_pp(r):
    n = r.randint(0, 9)
    root = _utree_root(r, n, r.choice(["random", "random", "deep", "left", "zig", "complete"]), 15)
    return _pp_args(root)


def _v_pp(tests):
    for t in tests:
        pre, post = t["args"]
        assert len(pre) == len(post) <= 1500 and len(set(pre)) == len(pre)
        assert sorted(pre) == sorted(post) and all(0 <= v <= MAXV for v in pre)
        assert not pre or pre[0] == post[-1]
    assert len({t["expected"] for t in tests}) >= 8


CHECKS["trees-with-same-preorder-postorder"] = (_b_pp, _g_pp, "exact")
VALIDATE["trees-with-same-preorder-postorder"] = _v_pp
