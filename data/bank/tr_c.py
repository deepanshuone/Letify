"""Problems: binary tree path problems (root-to-leaf sums, downward paths, any-to-any paths, consecutive / univalue / zigzag paths).
Trees are level-order int[] arrays. Two encodings are used and each statement says which one:
  * "plain":  missing child = -1, values are non-negative (same as the other tree modules);
  * "signed": missing child = 1000, values lie in [-500, 500] (so negative values are possible).
See data/lib.py for the registry."""
from collections import deque

from lib import add, rnd, CHECKS, VALIDATE, gen_arr  # noqa: F401

MAXN = 1500      # maximum number of nodes in any tree
MAXV = 10000     # maximum node value (plain encoding)
NS = 1000        # "missing child" marker of the signed encoding
SLO, SHI = -500, 500   # value range of the signed encoding

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

ENC_S = (
    "<p><strong>How trees are given.</strong> There is no tree type here. A binary tree is passed as an integer array in "
    "<em>level-order</em> (top to bottom, left to right). Node values can be negative in this problem, so a missing child is written as "
    "<code>1000</code> (real node values always lie between -500 and 500, so the marker can never be confused with a value). "
    "The children of a missing node are not listed, and trailing <code>1000</code> entries are dropped, so a non-empty array never ends with "
    "<code>1000</code>. The empty tree is <code>[]</code>.</p>"
    "<p>For example, <code>[1, 2, 3, 1000, 4]</code> describes the tree on the left: the root is 1 with children 2 and 3, node 2 has no left "
    "child and has 4 as its right child, and node 3 is a leaf.</p>"
    "<pre>    1\n   / \\\n  2   3\n   \\\n    4</pre>"
)


def _cons(extra=None, lo_nodes=0):
    out = [f"{lo_nodes} &le; number of nodes &le; {MAXN:,}", f"0 &le; node value &le; {MAXV:,}",
           "The array follows the encoding above exactly (valid level-order, no trailing -1)"]
    return out + (extra or [])


def _cons_s(extra=None, lo_nodes=0):
    out = [f"{lo_nodes} &le; number of nodes &le; {MAXN:,}", f"-500 &le; node value &le; 500",
           "The array follows the encoding above exactly (valid level-order, missing child written as 1000, no trailing 1000)"]
    return out + (extra or [])


# ------------------------------------------------------------------ helpers (parsing, building, shapes)
class _N:
    __slots__ = ("v", "l", "r")

    def __init__(self, v):
        self.v = v
        self.l = None
        self.r = None


def _build(arr, nul=-1):
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
                if v != nul:
                    c = _N(v)
                    if side == 0:
                        x.l = c
                    else:
                        x.r = c
                    q.append(c)
    assert i == len(arr), "encoding has entries below missing nodes"
    return root


def _encode(root, nul=-1):
    if root is None:
        return []
    out = []
    q = deque([root])
    while q:
        x = q.popleft()
        if x is None:
            out.append(nul)
            continue
        out.append(x.v)
        q.append(x.l)
        q.append(x.r)
    while out and out[-1] == nul:
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


def _tree(r, n, mode="random", lo=0, hi=MAXV, nul=-1):
    root = _shape(r, n, mode)
    for x in _preorder(root):
        x.v = r.randint(lo, hi)
    return _encode(root, nul)


def _walk_tree(r, n, mode, p_up, p_down, lo, hi, nul=-1):
    """Tree whose child value is parent+1 (prob p_up), parent-1 (prob p_down) or random in [lo, hi]."""
    root = _shape(r, n, mode)
    if root is None:
        return []
    root.v = r.randint(lo, hi)
    st = [root]
    while st:
        x = st.pop()
        for c in (x.l, x.r):
            if c is None:
                continue
            u = r.random()
            if u < p_up and x.v + 1 <= hi:
                c.v = x.v + 1
            elif u < p_up + p_down and x.v - 1 >= lo:
                c.v = x.v - 1
            else:
                c.v = r.randint(lo, hi)
            st.append(c)
    return _encode(root, nul)


def _small(nmax, lo, hi, nul, nmin=0, modes=MODES):
    def g(r):
        return [_tree(r, r.randint(nmin, nmax), r.choice(modes), lo, hi, nul)]
    return g


def _v_trees(lo, hi, nul, nmin=0, extra=None):
    def v(tests):
        for t in tests:
            arr = t["args"][0]
            assert isinstance(arr, list) and all(isinstance(x, int) for x in arr)
            assert arr == _encode(_build(arr, nul), nul), ("not a canonical level-order encoding", arr[:12])
            nodes = [x for x in arr if x != nul]
            assert nmin <= len(nodes) <= MAXN, "node count out of range"
            assert all(lo <= x <= hi for x in nodes), "node value out of range"
            if extra:
                extra(t)
    return v


def _leaf_sums(arr, nul):
    """Root-to-leaf sums in left-to-right order (used when creating tests)."""
    root = _build(arr, nul)
    out, st = [], ([(root, root.v)] if root else [])
    while st:
        x, s = st.pop()
        if x.l is None and x.r is None:
            out.append(s)
        if x.r:
            st.append((x.r, s + x.r.v))
        if x.l:
            st.append((x.l, s + x.l.v))
    return out[::-1] if False else out


def _all_paths(arr, nul):
    """Every simple path (ordered pair u, v) of the tree as a list of nodes. Small trees only."""
    root = _build(arr, nul)
    nodes = _preorder(root)
    par = {id(root): None}
    dep = {id(root): 0}
    for x in nodes:
        for c in (x.l, x.r):
            if c:
                par[id(c)] = x
                dep[id(c)] = dep[id(x)] + 1
    out = []
    for u in nodes:
        for v in nodes:
            a, b = u, v
            first, second = [], []
            while a is not b:
                if dep[id(a)] >= dep[id(b)]:
                    first.append(a)
                    a = par[id(a)]
                else:
                    second.append(b)
                    b = par[id(b)]
            out.append(first + [a] + second[::-1])
    return out


# Parsing used inside the reference solutions. The k-th real node (0-based, level order) owns array
# slots 2k+1 and 2k+2 as its children, because every real node contributes exactly two child slots.
LINKS_BODY = '''def _links(t):
    """vals[k], left[k], right[k] for the k-th real node in level order (-1 = no child)."""
    pos, c = [], 0
    for x in t:
        if x == NUL:
            pos.append(-1)
        else:
            pos.append(c)
            c += 1
    vals = [x for x in t if x != NUL]
    left, right = [-1] * c, [-1] * c
    for k in range(c):
        a = 2 * k + 1
        if a < len(t):
            left[k] = pos[a]
        if a + 1 < len(t):
            right[k] = pos[a + 1]
    return vals, left, right


'''


def LINKS(nul):
    return f"NUL = {nul}\n\n" + LINKS_BODY


N = NS  # short name for hand written signed trees

# ================================================================== EASY

# ---------------------------------------------------------------- root-to-leaf sum exists
_r = rnd(8301)
_t_big = [
    _tree(_r, MAXN, "random", SLO, SHI, NS),
    _tree(_r, MAXN, "left", -3, 3, NS),
    _tree(_r, MAXN, "deep", SLO, SHI, NS),
]
_hand = [
    [[5, 4, 8, 11, N, 13, 4, 7, 2, N, N, N, 1], 22],
    [[1, 2], 1],
    [[1, 2, 3], 4],
    [[], 0],
    [[7], 7],
    [[-3], 3],
    [[1, 2, 3], 5],
    [[0, 1, 1], 1],
    [[-2, N, -3], -5],
    [[10, 5, -3, 3, 2, N, 11, 3, -2, N, 1], 18],
    [[1, -2, -3, 1, 3, -2, N, -1], -1],
    [[1, 2, N, 3, N, 4], 10],
]
_hand[3][1] = 0
_big_tests = []
_ls = _leaf_sums(_t_big[0], NS)
_big_tests.append([_t_big[0], _ls[len(_ls) // 2]])
_ls = _leaf_sums(_t_big[1], NS)
_big_tests.append([_t_big[1], _ls[0] + 1])
_ls = _leaf_sums(_t_big[2], NS)
_big_tests.append([_t_big[2], _ls[-1]])

add(
    id="tree-root-to-leaf-sum-exists", title="Root-to-Leaf Path With a Given Sum", diff="Easy", topic="Trees",
    fn="hasPathSum", params=[("tree", "int[]"), ("target", "int")], ret="bool", cmp="exact",
    desc="<p>A <em>root-to-leaf path</em> starts at the root and follows child links down to a <em>leaf</em>, a node that has no children. Given a binary tree and an integer <code>target</code>, decide whether some root-to-leaf path has node values that add up to exactly <code>target</code>. Return <code>true</code> or <code>false</code>.</p>"
         "<p>The path must end at a leaf: a node that merely has a missing child on one side is not a leaf. The empty tree has no paths, so the answer is <code>false</code> for it.</p>" + ENC_S +
         "<p>For <code>tree = [5, 4, 8, 11, 1000, 13, 4, 7, 2, 1000, 1000, 1000, 1]</code> and <code>target = 22</code> the answer is <code>true</code> (the path 5 &rarr; 4 &rarr; 11 &rarr; 2). For <code>tree = [1, 2]</code> and <code>target = 1</code> the answer is <code>false</code>: the only leaf is 2, and the path to it sums to 3.</p>",
    constraints=_cons_s(["-100,000 &le; target &le; 100,000"]),
    hints=["Every root-to-leaf path is determined by its last node. Can you know the sum of the path ending at a node when you reach it?",
           "The sum of the path to a child is the sum of the path to its parent plus the child's value. Carry that running sum downward.",
           "Walk the tree top to bottom. At a node with no children, compare its running sum with <code>target</code>. Remember that a node with exactly one child is not a leaf, and that the empty tree gives <code>false</code>."],
    editorial=["Define the running sum of a node as the sum of all values on the path from the root to that node. The root's running sum is its own value, and a child's running sum is its parent's running sum plus its own value. A root-to-leaf path with sum <code>target</code> exists exactly when some leaf has running sum <code>target</code>.",
               "In the level-order array a parent always comes before its children, so one forward pass over the real nodes computes every running sum with no recursion. Check the sums of the nodes without children. A recursive version that subtracts the node value from <code>target</code> on the way down and tests for <code>0</code> at a leaf is equivalent. The two traps are treating a node with a single child as a leaf and forgetting that values can be negative, so you cannot stop early when the running sum passes the target.",
               "Each node is visited once: O(n) time, and the array of running sums takes O(n) space."],
    time="O(n)", space="O(n)",
    solution=LINKS(NS) + '''def hasPathSum(tree, target):
    vals, left, right = _links(tree)
    n = len(vals)
    if n == 0:
        return False
    run = [0] * n
    run[0] = vals[0]
    for k in range(n):
        a, b = left[k], right[k]
        if a == -1 and b == -1:
            if run[k] == target:
                return True
            continue
        if a != -1:
            run[a] = run[k] + vals[a]
        if b != -1:
            run[b] = run[k] + vals[b]
    return False
''',
    tests=_hand + _big_tests,
)


def _b_pathsum(tree, target):
    root = _build(tree, NS)

    def go(x, rest):
        if x is None:
            return False
        if x.l is None and x.r is None:
            return rest == x.v
        return go(x.l, rest - x.v) or go(x.r, rest - x.v)
    return go(root, target)


def _g_pathsum(r):
    n = r.randint(0, 10)
    t = _tree(r, n, r.choice(MODES), -4, 4, NS)
    if t and r.random() < 0.6:
        target = r.choice(_leaf_sums(t, NS))
    else:
        target = r.randint(-8, 8)
    return [t, target]


CHECKS["tree-root-to-leaf-sum-exists"] = (_b_pathsum, _g_pathsum, "exact")
VALIDATE["tree-root-to-leaf-sum-exists"] = _v_trees(SLO, SHI, NS)

# ---------------------------------------------------------------- binary numbers on root-to-leaf paths
_r = rnd(8302)
_hand = [[1, 0, 1, 0, 1, 0, 1], [1], [0], [], [1, 1], [1, -1, 0, -1, 1], [1, 0, 0, 1, 1, 0, 1, 1],
         [0, 1, 1, 1, 0, 0, 1], [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]]
_big = [_tree(_r, MAXN, "left", 0, 1), _tree(_r, MAXN, "random", 0, 1), _tree(_r, MAXN, "complete", 0, 1)]
_bigx = _tree(_r, MAXN, "zig", 1, 1)
add(
    id="tree-root-to-leaf-binary-numbers-sum", title="Sum of Root-to-Leaf Binary Numbers", diff="Easy", topic="Trees",
    fn="sumBinaryPaths", params=[("tree", "int[]")], ret="int", cmp="exact",
    desc="<p>Every node of a binary tree holds a single bit, <code>0</code> or <code>1</code>. Each root-to-leaf path therefore spells a binary number: read the bits from the root down to the leaf, with the root as the most significant bit. For example the path 1 &rarr; 0 &rarr; 1 is the number <code>101</code> in binary, which is 5.</p>"
         "<p>Return the sum of the numbers spelled by <strong>all</strong> root-to-leaf paths (a leaf is a node with no children), taken modulo <code>1,000,000,007</code>. The empty tree has no paths and gives <code>0</code>.</p>" + ENC +
         "<p>For <code>tree = [1, 0, 1, 0, 1, 0, 1]</code> the four paths spell 100, 101, 110 and 111, that is 4 + 5 + 6 + 7, so the answer is <code>22</code>.</p>",
    constraints=_cons(lo_nodes=0)[:1] + ["Every node value is 0 or 1", "The array follows the encoding above exactly (valid level-order, no trailing -1)", "Return the sum modulo 1,000,000,007"],
    hints=["Think about how the number for the path to a node relates to the number for the path to its parent.",
           "Appending a bit <code>b</code> to a binary number <code>x</code> gives <code>2 * x + b</code>.",
           "Carry the number downward with <code>child = 2 * parent + bit</code>, keeping it modulo 1,000,000,007 because a path can have 1,500 bits. Add the value of every leaf to the answer."],
    editorial=["Let <code>num[v]</code> be the binary number spelled by the path from the root to node <code>v</code>. Appending one more bit shifts the number left by one position and adds the bit, so <code>num[child] = 2 * num[parent] + bit(child)</code> and <code>num[root] = bit(root)</code>. The answer is the sum of <code>num</code> over all leaves.",
               "A path may be 1,500 nodes long, which is far beyond 64 bits, so every update is done modulo 1,000,000,007. This is safe because the recurrence only uses additions and multiplications. In the level-order array parents come before children, so one forward pass over the real nodes is enough.",
               "O(n) time, O(n) space for the numbers (the values can also be passed down a stack/recursion instead)."],
    time="O(n)", space="O(n)",
    solution=LINKS(-1) + '''def sumBinaryPaths(tree):
    MOD = 1000000007
    vals, left, right = _links(tree)
    n = len(vals)
    if n == 0:
        return 0
    num = [0] * n
    num[0] = vals[0]
    total = 0
    for k in range(n):
        a, b = left[k], right[k]
        if a == -1 and b == -1:
            total = (total + num[k]) % MOD
            continue
        for c in (a, b):
            if c != -1:
                num[c] = (2 * num[k] + vals[c]) % MOD
    return total
''',
    tests=[[t] for t in _hand + _big + [_bigx]],
)


def _b_binsum(tree):
    root = _build(tree)
    out = []

    def go(x, cur):
        if x is None:
            return
        cur = cur * 2 + x.v
        if x.l is None and x.r is None:
            out.append(cur)
        go(x.l, cur)
        go(x.r, cur)
    go(root, 0)
    return sum(out) % 1000000007


CHECKS["tree-root-to-leaf-binary-numbers-sum"] = (_b_binsum, _small(11, 0, 1, -1), "exact")
VALIDATE["tree-root-to-leaf-binary-numbers-sum"] = _v_trees(0, 1, -1)

# ================================================================== MEDIUM

# ---------------------------------------------------------------- all root-to-leaf paths with a given sum
_r = rnd(8303)
_hand = [
    [[5, 4, 8, 11, N, 13, 4, 7, 2, N, N, 5, 1], 22],
    [[1, 2, 3], 5],
    [[1, 2], 0],
    [[], 0],
    [[0], 0],
    [[0, 0, 0, 0, 0, 0, 0], 0],
    [[-2, N, -3], -5],
    [[1, -2, -3, 1, 3, -2, N, -1], -1],
    [[1, -2, -3, 1, 3, -2, N, -1], 2],
    [[3, 1, 2, 2, N, N, 1], 6],
    [[2, 2, 2, 2, 2, 2, 2], 6],
]
_tb = [_tree(_r, MAXN, "random", SLO, SHI, NS), _tree(_r, MAXN, "complete", SLO, SHI, NS), _tree(_r, MAXN, "deep", -2, 2, NS)]
_big_tests = []
_ls = _leaf_sums(_tb[0], NS)
_big_tests.append([_tb[0], _ls[len(_ls) // 3]])
_ls = _leaf_sums(_tb[1], NS)
_big_tests.append([_tb[1], _ls[len(_ls) // 2]])
_ls = _leaf_sums(_tb[2], NS)
_multi = [v for v in set(_ls) if _ls.count(v) >= 2]
_big_tests.append([_tb[2], min(_multi, key=_ls.count) if _multi else _ls[0]])
_tbl = _tree(_r, 1500, "zig", -2, 2, NS)
_ls = _leaf_sums(_tbl, NS)
_big_tests.append([_tbl, _ls[0]])

add(
    id="tree-root-to-leaf-paths-with-sum", title="List All Root-to-Leaf Paths With a Given Sum", diff="Medium", topic="Trees",
    fn="pathsWithSum", params=[("tree", "int[]"), ("target", "int")], ret="int[][]", cmp="exact",
    desc="<p>Given a binary tree and an integer <code>target</code>, return <strong>every</strong> root-to-leaf path whose node values add up to <code>target</code>. A path is reported as the list of its node values from the root down to the leaf, and a leaf is a node without children.</p>"
         "<p>Report the paths in <em>left-to-right</em> order of their leaves (the order a pre-order walk that visits the left child first would find them). If no path matches, return an empty list. Different paths may have identical value lists; each path is reported once.</p>" + ENC_S +
         "<p>For <code>tree = [5, 4, 8, 11, 1000, 13, 4, 7, 2, 1000, 1000, 5, 1]</code> and <code>target = 22</code> the answer is <code>[[5, 4, 11, 2], [5, 8, 4, 5]]</code>.</p>",
    constraints=_cons_s(["-100,000 &le; target &le; 100,000", "The total number of values in the returned paths is at most 6,000"]),
    hints=["A path is only valid if it ends at a leaf, so decide at the leaves. What do you need to know when you arrive at one?",
           "Track the running sum from the root to every node. A leaf whose running sum equals <code>target</code> ends a matching path.",
           "Do not copy whole paths while descending. Remember each node's parent, and rebuild the list by walking up from a matching leaf, then reverse it. Visit leaves in pre-order (push the right child before the left child on a stack) so the output order comes out right."],
    editorial=["The running sum of a node (sum of values from the root to it) is computed from its parent's in O(1). A root-to-leaf path matches exactly when its leaf has running sum <code>target</code>, so the problem splits into two parts: find the matching leaves in left-to-right order, and turn each into its value list.",
               "Visiting nodes with an explicit stack in pre-order (push right, then left) meets the leaves in left-to-right order. For every matching leaf, climb the parent links to the root and reverse. Only matching leaves pay for building a path, so the total work is O(n + total output length) instead of O(n &middot; depth) when paths are copied at every node.",
               "Because values may be negative, you can never prune a branch just because its running sum already exceeds the target."],
    time="O(n + output)", space="O(n)",
    solution=LINKS(NS) + '''def pathsWithSum(tree, target):
    vals, left, right = _links(tree)
    n = len(vals)
    if n == 0:
        return []
    parent = [-1] * n
    run = [0] * n
    run[0] = vals[0]
    for k in range(n):
        for c in (left[k], right[k]):
            if c != -1:
                parent[c] = k
                run[c] = run[k] + vals[c]
    out = []
    stack = [0]
    while stack:
        k = stack.pop()
        a, b = left[k], right[k]
        if a == -1 and b == -1:
            if run[k] == target:
                path = []
                x = k
                while x != -1:
                    path.append(vals[x])
                    x = parent[x]
                path.reverse()
                out.append(path)
        else:
            if b != -1:
                stack.append(b)
            if a != -1:
                stack.append(a)
    return out
''',
    tests=_hand + _big_tests,
)


def _b_paths(tree, target):
    root = _build(tree, NS)
    out = []

    def go(x, path):
        if x is None:
            return
        path = path + [x.v]
        if x.l is None and x.r is None:
            if sum(path) == target:
                out.append(path)
            return
        go(x.l, path)
        go(x.r, path)
    go(root, [])
    return out


def _v_paths_extra(t):
    assert -100000 <= t["args"][1] <= 100000
    assert sum(len(p) for p in t["expected"]) <= 6000, "output too large"


CHECKS["tree-root-to-leaf-paths-with-sum"] = (_b_paths, _g_pathsum, "exact")
VALIDATE["tree-root-to-leaf-paths-with-sum"] = _v_trees(SLO, SHI, NS, extra=_v_paths_extra)

# ---------------------------------------------------------------- downward paths with a given sum (count)
_r = rnd(8304)
_hand = [
    [[10, 5, -3, 3, 2, N, 11, 3, -2, N, 1], 8],
    [[1], 1],
    [[], 0],
    [[0, 0, 0], 0],
    [[1, 2, 3], 3],
    [[1, -1, N, 1, N, -1], 0],
    [[5, 4, 8, 11, N, 13, 4, 7, 2, N, N, 5, 1], 22],
    [[1, 1, 1, 1, 1, 1, 1], 2],
    [[-2, -3, 4, 5, N, N, -4], -5],
    [[1, N, 2, N, 3, N, 4, N, 5], 5],
]
_tb = [_tree(_r, MAXN, "left", 0, 0, NS), _tree(_r, MAXN, "random", -3, 3, NS), _tree(_r, MAXN, "zig", -4, 4, NS),
       _tree(_r, MAXN, "complete", SLO, SHI, NS)]
_hand += [[_tb[0], 0], [_tb[1], 2], [_tb[2], -3], [_tb[3], 100]]
add(
    id="tree-downward-paths-with-sum-count", title="Count Downward Paths With a Given Sum", diff="Medium", topic="Trees", tier="must",
    fn="countDownwardPaths", params=[("tree", "int[]"), ("target", "int")], ret="int", cmp="exact",
    desc="<p>Count the paths of a binary tree whose node values add up to <code>target</code>, where a path is allowed to start at <strong>any</strong> node and end at <strong>any</strong> node below it. It always moves from a parent to one of its children, never upward. A path consists of at least one node, and it does not need to start at the root or end at a leaf.</p>"
         "<p>Two paths are different if their sets of nodes differ, even when the values are identical. Node values can be negative or zero, so several different start nodes can combine with the same end node.</p>" + ENC_S +
         "<p>For <code>tree = [10, 5, -3, 3, 2, 1000, 11, 3, -2, 1000, 1]</code> and <code>target = 8</code> the answer is <code>3</code>: the paths 5 &rarr; 3, 5 &rarr; 2 &rarr; 1 and -3 &rarr; 11.</p>",
    constraints=_cons_s(["-1,000,000 &le; target &le; 1,000,000", "The answer fits in a 32-bit integer (it is at most 1,500 &middot; 1,501 / 2)"]),
    hints=["Fix the <em>end</em> node of a path instead of the start. Which start nodes make the path sum equal <code>target</code>?",
           "If <code>S(v)</code> is the sum from the root to <code>v</code>, a downward path from an ancestor <code>u</code> (its child side) to <code>v</code> has sum <code>S(v) - S(parent(u))</code>. So you need ancestors whose prefix sum is exactly <code>S(v) - target</code>.",
           "Keep a hash map counting the prefix sums on the current root-to-node path (start with {0: 1}). On entering a node, add <code>count[S - target]</code> to the answer, then record <code>S</code>; on leaving the node, remove it again."],
    editorial=["Checking every start node costs O(n &middot; depth), which is up to O(n<sup>2</sup>) on a chain. The standard trick from subarray sums carries over to trees: let <code>S(v)</code> be the sum of values from the root to <code>v</code>. A downward path that ends at <code>v</code> and starts at a proper descendant of an ancestor <code>a</code> has sum <code>S(v) - S(a)</code>. It equals <code>target</code> exactly when <code>S(a) = S(v) - target</code>, where <code>a</code> may also be the virtual prefix 0 before the root.",
               "So run a DFS that maintains a map from prefix sum to the number of ancestors (on the current path) with that prefix sum, initialised with {0: 1}. When you enter <code>v</code> compute <code>S(v)</code>, add <code>map[S(v) - target]</code> to the answer, then increment <code>map[S(v)]</code>. When you leave <code>v</code>, decrement it again so the map only ever describes the current root-to-node path. Use an explicit stack with enter and exit markers because the tree can be 1,500 deep.",
               "Every node is entered and left once: O(n) time and O(depth) extra space for the map."],
    time="O(n)", space="O(n)",
    solution=LINKS(NS) + '''def countDownwardPaths(tree, target):
    vals, left, right = _links(tree)
    n = len(vals)
    if n == 0:
        return 0
    cnt = {0: 1}
    ans = 0
    stack = [(0, 0, 0)]  # (node, prefix sum of its parent, phase: 0 = enter, 1 = exit)
    while stack:
        k, sp, phase = stack.pop()
        if phase == 1:
            cnt[sp] -= 1  # here sp holds the node's own prefix sum
            continue
        s = sp + vals[k]
        ans += cnt.get(s - target, 0)
        cnt[s] = cnt.get(s, 0) + 1
        stack.append((k, s, 1))
        if right[k] != -1:
            stack.append((right[k], s, 0))
        if left[k] != -1:
            stack.append((left[k], s, 0))
    return ans
''',
    tests=_hand,
)


def _b_down(tree, target):
    root = _build(tree, NS)
    nodes = _preorder(root)
    total = 0

    def go(x, s):
        nonlocal total
        if x is None:
            return
        s += x.v
        if s == target:
            total += 1
        go(x.l, s)
        go(x.r, s)
    for x in nodes:
        go(x, 0)
    return total


def _g_down(r):
    n = r.randint(0, 11)
    return [_tree(r, n, r.choice(MODES), -3, 3, NS), r.randint(-5, 5)]


CHECKS["tree-downward-paths-with-sum-count"] = (_b_down, _g_down, "exact")
VALIDATE["tree-downward-paths-with-sum-count"] = _v_trees(SLO, SHI, NS, extra=lambda t: None)

# ---------------------------------------------------------------- longest univalue path
_r = rnd(8305)
_hand = [[5, 4, 5, 1, 1, -1, 5], [1, 4, 5, 4, 4, -1, 5], [], [7], [2, 2], [3, 3, 3, 3, 3, 3, 3], [1, 2, 3, 4, 5, 6, 7],
         [1, 1, 1, -1, 1, 1, -1, -1, -1, 1, -1, -1, 1], [0, 1, 0, 1, 0, 1, 0, 1], [1, 1, 2, 1, 1, 2, 2, 1]]
_big = [_tree(_r, MAXN, "random", 0, 1), _tree(_r, MAXN, "complete", 5, 5), _tree(_r, MAXN, "deep", 0, 2),
        _tree(_r, MAXN, "zig", 0, 1)]
add(
    id="tree-longest-univalue-path", title="Longest Path of Equal Values", diff="Medium", topic="Trees",
    fn="longestUnivaluePath", params=[("tree", "int[]")], ret="int", cmp="exact",
    desc="<p>Find the longest path in a binary tree in which <strong>every node has the same value</strong>. The path may start and end at any nodes, may pass through the root or not, and can turn at a node (go up to a common ancestor and then down again). Return its length measured in <strong>edges</strong>, so a path of a single node has length <code>0</code>. The empty tree also gives <code>0</code>.</p>" + ENC +
         "<p>For <code>tree = [5, 4, 5, 1, 1, -1, 5]</code> the answer is <code>2</code>: the three 5s at the root, its right child and that child's right child form a path with two edges.</p>",
    constraints=_cons(),
    hints=["Look at the highest node of the best path (the place where it turns). It extends down on at most two sides.",
           "For each node compute <code>chain[v]</code>: the longest downward run of equal values that starts at <code>v</code>. A child only extends the chain if it has the same value as <code>v</code>.",
           "The best path that turns at <code>v</code> has length <code>(left run) + (right run)</code>, where a run is <code>chain[child] + 1</code> if the child equals <code>v</code> and 0 otherwise. Take the maximum over all nodes, and set <code>chain[v]</code> to the larger of the two runs."],
    editorial=["Every path has a highest node. If the path is all one value <code>x</code> and peaks at node <code>v</code> with value <code>x</code>, then it goes down into the left child (only if that child also holds <code>x</code>) and down into the right child (same condition), as far as the equal values continue.",
               "Let <code>chain[v]</code> be the number of edges of the longest downward path from <code>v</code> in which all values equal <code>v</code>'s value. For the left child <code>a</code>, the run on the left side is <code>chain[a] + 1</code> when <code>val[a] == val[v]</code> and <code>0</code> otherwise; the right side is analogous. Then <code>chain[v] = max(leftRun, rightRun)</code> and the longest path peaking at <code>v</code> has <code>leftRun + rightRun</code> edges. The answer is the maximum of that over all nodes.",
               "In the level-order array, children come after their parents, so processing the real nodes from the last to the first computes all <code>chain</code> values bottom-up without recursion. O(n) time and O(n) space."],
    time="O(n)", space="O(n)",
    solution=LINKS(-1) + '''def longestUnivaluePath(tree):
    vals, left, right = _links(tree)
    n = len(vals)
    chain = [0] * n
    best = 0
    for k in range(n - 1, -1, -1):
        a, b = left[k], right[k]
        la = chain[a] + 1 if a != -1 and vals[a] == vals[k] else 0
        lb = chain[b] + 1 if b != -1 and vals[b] == vals[k] else 0
        chain[k] = max(la, lb)
        best = max(best, la + lb)
    return best
''',
    tests=[[t] for t in _hand + _big],
)


def _b_univ(tree):
    best = 0
    for p in _all_paths(tree, -1) if tree else []:
        if len({x.v for x in p}) == 1:
            best = max(best, len(p) - 1)
    return best


CHECKS["tree-longest-univalue-path"] = (_b_univ, _small(10, 0, 2, -1), "exact")
VALIDATE["tree-longest-univalue-path"] = _v_trees(0, MAXV, -1)

# ---------------------------------------------------------------- consecutive downward path
_r = rnd(8306)
_hand = [[1, -1, 3, 2, 4, -1, -1, -1, 5], [2, -1, 3, -1, 4, -1, 5], [], [9], [1, 2, 3], [1, 2, 2, 3, 3, 3, 3, 4, 4],
         [3, 2, 4, 1, 3, 5, 6], [5, 6, 7, 8, 9, 10, 11], [1, 2, 3, 0, 5, 6, 7, 4, 4],
         [4, 5, 6, 5, 7, 7, 8, 6, 5, 8, 9]]
_big = [_walk_tree(_r, MAXN, "left", 0.995, 0, 0, 5000), _walk_tree(_r, MAXN, "random", 0.7, 0, 0, MAXV),
        _walk_tree(_r, MAXN, "deep", 0.9, 0, 0, MAXV), _walk_tree(_r, MAXN, "complete", 0.8, 0, 0, MAXV)]
add(
    id="tree-longest-consecutive-downward-path", title="Longest Parent-to-Child Consecutive Path", diff="Medium", topic="Trees",
    fn="longestConsecutiveDown", params=[("tree", "int[]")], ret="int", cmp="exact",
    desc="<p>A <em>consecutive downward path</em> starts at some node and repeatedly moves to a child, such that every step increases the value by exactly <code>1</code>. For instance 3 &rarr; 4 &rarr; 5 is such a path, but 3 &rarr; 5 and 4 &rarr; 3 are not. It may start anywhere, never moves upward, and a single node already counts as a path.</p>"
         "<p>Return the number of <strong>nodes</strong> on the longest such path (<code>0</code> for the empty tree).</p>" + ENC +
         "<p>For <code>tree = [1, -1, 3, 2, 4, -1, -1, -1, 5]</code> the answer is <code>3</code>, from the path 3 &rarr; 4 &rarr; 5. The path 3 &rarr; 2 does not count because the value goes down.</p>",
    constraints=_cons(),
    hints=["A consecutive path is always extended one node at a time. What do you need to know about the parent to decide whether the child continues its path?",
           "Let <code>len[v]</code> be the length of the longest consecutive path that <em>ends</em> at <code>v</code>. It depends only on the parent of <code>v</code>.",
           "If the parent's value is <code>val[v] - 1</code>, then <code>len[v] = len[parent] + 1</code>; otherwise <code>len[v] = 1</code> (the path restarts at <code>v</code>). Walk the tree from the root and track the maximum."],
    editorial=["Because a downward path has a unique ancestor chain, the longest consecutive path ending at a node <code>v</code> is either just <code>v</code> or the longest one ending at its parent, extended by <code>v</code> when <code>val[v] = val[parent] + 1</code>. That gives the one-line recurrence <code>len[v] = len[parent] + 1</code> if the values are consecutive and <code>len[v] = 1</code> otherwise, with <code>len[root] = 1</code>.",
               "The answer is the maximum of <code>len</code> over all nodes. In the level-order array a parent is always handled before its children, so a single pass over the real nodes, pushing <code>len</code> from each node to its children, is enough and avoids recursion on deep trees.",
               "O(n) time and O(n) space."],
    time="O(n)", space="O(n)",
    solution=LINKS(-1) + '''def longestConsecutiveDown(tree):
    vals, left, right = _links(tree)
    n = len(vals)
    if n == 0:
        return 0
    ln = [1] * n
    best = 1
    for k in range(n):
        for c in (left[k], right[k]):
            if c != -1 and vals[c] == vals[k] + 1:
                ln[c] = ln[k] + 1
                if ln[c] > best:
                    best = ln[c]
    return best
''',
    tests=[[t] for t in _hand + _big],
)


def _b_consdown(tree):
    root = _build(tree)
    best = 0

    def go(x, ln):
        nonlocal best
        if x is None:
            return
        best = max(best, ln)
        for c in (x.l, x.r):
            if c is not None:
                go(c, ln + 1 if c.v == x.v + 1 else 1)
    if root:
        go(root, 1)
    return best


def _g_consdown(r):
    return [_walk_tree(r, r.randint(0, 11), r.choice(MODES), 0.6, 0.1, 0, 5)]


CHECKS["tree-longest-consecutive-downward-path"] = (_b_consdown, _g_consdown, "exact")
VALIDATE["tree-longest-consecutive-downward-path"] = _v_trees(0, MAXV, -1)

# ---------------------------------------------------------------- longest zigzag path
_r = rnd(8307)
_hand = [[1, 2, 3, -1, 4, -1, -1, 5], [], [1], [1, 2], [1, -1, 2], [1, 2, 3, 4, 5, 6, 7], [1, 2, -1, 3, -1, 4, -1, 5],
         [1, 2, 3, -1, 4, 5, -1, -1, -1, -1, 6, 7, -1, -1, 8]]
_big = [_tree(_r, MAXN, "zig", 0, 9), _tree(_r, MAXN, "random", 0, 9), _tree(_r, MAXN, "deep", 0, 9),
        _tree(_r, MAXN, "left", 0, 9)]
add(
    id="tree-longest-zigzag-path", title="Longest Zigzag Path in a Binary Tree", diff="Medium", topic="Trees", tier="extra",
    fn="longestZigzag", params=[("tree", "int[]")], ret="int", cmp="exact",
    desc="<p>A <em>zigzag path</em> is built like this: pick any starting node and an initial direction, <em>left</em> or <em>right</em>. Move to the child in that direction if it exists, then switch direction (left becomes right and right becomes left) and repeat. The walk stops when the child in the required direction is missing. A single node is a zigzag path of length <code>0</code>.</p>"
         "<p>Return the length, in <strong>edges</strong>, of the longest zigzag path of the tree. The node values do not matter for this problem; only the shape counts. The empty tree gives <code>0</code>.</p>" + ENC +
         "<p>For <code>tree = [1, 2, 3, -1, 4, -1, -1, 5]</code> the answer is <code>3</code>: start at the root, go left to 2, right to 4 and left to 5.</p>",
    constraints=_cons(),
    hints=["From a node, a zigzag walk has only two possibilities for its first move: left or right. After that, the whole walk is forced.",
           "Define two numbers per node: the longest zigzag that starts at this node and goes <em>left</em> first, and the one that goes <em>right</em> first. Express each with the child's values.",
           "<code>L[v] = 1 + R[left child]</code> if the left child exists (else 0), and <code>R[v] = 1 + L[right child]</code> if the right child exists (else 0). The answer is the largest <code>L</code> or <code>R</code> over all nodes."],
    editorial=["After the first move the path is forced: it always has to continue in the opposite direction. So a zigzag walk starting at <code>v</code> and first going left consists of the edge to the left child <code>a</code>, followed by a zigzag walk that starts at <code>a</code> and goes <em>right</em> first. That yields the recurrences <code>L[v] = 1 + R[a]</code> and <code>R[v] = 1 + L[b]</code> for the right child <code>b</code>, with the value 0 when the child is missing.",
               "Any zigzag path starts somewhere, so the answer is the maximum of all <code>L[v]</code> and <code>R[v]</code>. Computing the values from the last real node to the first one makes sure the children are ready (a child always sits after its parent in level order). Trying every start with a fresh simulation would also work but is O(n &middot; depth) in the worst case.",
               "O(n) time, O(n) space."],
    time="O(n)", space="O(n)",
    solution=LINKS(-1) + '''def longestZigzag(tree):
    vals, left, right = _links(tree)
    n = len(vals)
    L = [0] * n
    R = [0] * n
    best = 0
    for k in range(n - 1, -1, -1):
        a, b = left[k], right[k]
        if a != -1:
            L[k] = 1 + R[a]
        if b != -1:
            R[k] = 1 + L[b]
        best = max(best, L[k], R[k])
    return best
''',
    tests=[[t] for t in _hand + _big],
)


def _b_zig(tree):
    root = _build(tree)
    best = 0
    for start in _preorder(root):
        for d in (0, 1):
            x, ln, dd = start, 0, d
            while True:
                nxt = x.l if dd == 0 else x.r
                if nxt is None:
                    break
                x, ln, dd = nxt, ln + 1, 1 - dd
            best = max(best, ln)
    return best


CHECKS["tree-longest-zigzag-path"] = (_b_zig, _small(12, 0, 9, -1), "exact")
VALIDATE["tree-longest-zigzag-path"] = _v_trees(0, MAXV, -1)

# ---------------------------------------------------------------- equalize root-to-leaf sums
_r = rnd(8308)
_hand = [[1, 2, 3], [1, 5, 2, 2, 3, 3, 1], [5], [], [1, 2], [1, 2, 3, 4, 5, 6, 7], [0, 0, 0, 0, 0, 0, 0],
         [4, 2, 1, 3, -1, 5, 6, 7, -1, -1, 8], [2, 1, -1, 1, -1, 1, -1, 1]]
_big = [_tree(_r, MAXN, "random", 0, 100), _tree(_r, MAXN, "complete", 0, 100), _tree(_r, MAXN, "deep", 0, 100)]
add(
    id="tree-equalize-root-to-leaf-sums", title="Equalize All Root-to-Leaf Sums", diff="Medium", topic="Trees", tier="extra",
    fn="minIncrements", params=[("tree", "int[]")], ret="int", cmp="exact",
    desc="<p>In one operation you may choose any node of a binary tree and increase its value by <code>1</code>. Values are never decreased. Find the minimum number of operations needed so that <strong>all root-to-leaf paths have the same sum</strong> (a leaf is a node with no children; the sum of a path is the sum of the values of its nodes).</p>"
         "<p>A tree with at most one leaf already satisfies the condition, so the answer is <code>0</code> for it, including the empty tree.</p>" + ENC +
         "<p>For <code>tree = [1, 2, 3]</code> the two path sums are 3 and 4, so one operation (raise the left leaf, node 2, by 1) is enough and the answer is <code>1</code>. For <code>tree = [1, 5, 2, 2, 3, 3, 1]</code> the answer is <code>6</code>.</p>",
    constraints=_cons()[:1] + ["0 &le; node value &le; 100", "The array follows the encoding above exactly (valid level-order, no trailing -1)"],
    hints=["Raising a node raises every path that goes through it. Where is it cheapest to fix a difference between two sibling subtrees?",
           "At a node whose two child subtrees have different best path sums, the weaker side has to catch up. Increasing the <em>child on the weaker side</em> lifts all its paths at once.",
           "Compute <code>f[v]</code>, the largest sum of a downward path starting at <code>v</code>. Each node with two children contributes <code>|f[left] - f[right]|</code> to the answer; nodes with one child or none contribute nothing. Sum these up."],
    editorial=["Only the relative sums inside each subtree matter at a node: raising a node shifts all leaf sums below it by the same amount, so it cannot reduce a difference between the two sides of any node underneath it. Differences can only be closed by raising nodes inside the weaker child's subtree.",
               "Process bottom-up. Suppose every subtree below <code>v</code> is already balanced (all its downward paths have equal sum), with common sum <code>f[child]</code>. If <code>v</code> has two children with <code>f[left] != f[right]</code>, the cheapest fix is to add the difference to the weaker child itself, which raises all of its paths with a single increment amount of <code>|f[left] - f[right]|</code>. No cheaper repair exists because the paths through the weaker side must gain at least that much while the operations inside the other subtree cannot help. After this, both sides have equal sums and <code>f[v] = val[v] + max(f[left], f[right])</code>.",
               "So the answer is the sum of <code>|f[left] - f[right]|</code> over the nodes with two children. A node with one child needs nothing. A single backwards pass over the level-order array gives O(n) time and O(n) space. The statement keeps values at most 100 so that the result fits in 32 bits."],
    time="O(n)", space="O(n)",
    solution=LINKS(-1) + '''def minIncrements(tree):
    vals, left, right = _links(tree)
    n = len(vals)
    f = [0] * n
    cost = 0
    for k in range(n - 1, -1, -1):
        a, b = left[k], right[k]
        if a != -1 and b != -1:
            cost += abs(f[a] - f[b])
            f[k] = vals[k] + max(f[a], f[b])
        elif a != -1:
            f[k] = vals[k] + f[a]
        elif b != -1:
            f[k] = vals[k] + f[b]
        else:
            f[k] = vals[k]
    return cost
''',
    tests=[[t] for t in _hand + _big],
)


def _b_equal(tree):
    root = _build(tree)
    if root is None:
        return 0
    mx = [0]

    def top(x, s):
        s += x.v
        if x.l is None and x.r is None:
            mx[0] = max(mx[0], s)
        for c in (x.l, x.r):
            if c:
                top(c, s)
    top(root, 0)
    INF = 10 ** 9
    memo = {}

    def g(x, rem):
        """Minimum total increments inside x's subtree so that every downward path from x to a leaf sums to rem."""
        key = (id(x), rem)
        if key in memo:
            return memo[key]
        best = INF
        if rem >= x.v:
            if x.l is None and x.r is None:
                best = rem - x.v
            else:
                for a in range(0, rem - x.v + 1):
                    tot = a
                    for c in (x.l, x.r):
                        if c:
                            tot += g(c, rem - x.v - a)
                    best = min(best, tot)
        memo[key] = best
        return best
    return min(g(root, T) for T in range(mx[0], mx[0] + 3))


CHECKS["tree-equalize-root-to-leaf-sums"] = (_b_equal, _small(7, 0, 3, -1), "exact")
VALIDATE["tree-equalize-root-to-leaf-sums"] = _v_trees(0, 100, -1)

# ================================================================== HARD

# ---------------------------------------------------------------- maximum path sum
_r = rnd(8309)
_hand = [
    [-10, 9, 20, N, N, 15, 7],
    [1, 2, 3],
    [-3],
    [-1, -2, -3],
    [2, -1],
    [5, 4, 8, 11, N, 13, 4, 7, 2, N, N, N, 1],
    [-2, 1],
    [1, -2, 3],
    [0, 0, 0],
    [10, -50, -50, 20, N, N, 20],
    [-5, -4, -4, N, 3, 3],
]
_big = [_tree(_r, MAXN, "random", SLO, SHI, NS), _tree(_r, MAXN, "left", SLO, SHI, NS),
        _tree(_r, MAXN, "complete", -500, 100, NS), _tree(_r, MAXN, "deep", -500, 200, NS)]
add(
    id="tree-maximum-path-sum", title="Maximum Path Sum in a Binary Tree", diff="Hard", topic="Trees", tier="must",
    fn="maxPathSum", params=[("tree", "int[]")], ret="int", cmp="exact",
    desc="<p>A <em>path</em> in a binary tree is a sequence of nodes in which every two neighbours in the sequence are connected by an edge (parent and child), and no node appears twice. A path may start and end at <strong>any</strong> nodes, does not have to pass through the root, and can go up to a common ancestor and then down again. It must contain at least one node.</p>"
         "<p>The sum of a path is the sum of its node values, which can be negative. Return the largest path sum over all paths.</p>" + ENC_S +
         "<p>For <code>tree = [-10, 9, 20, 1000, 1000, 15, 7]</code> the answer is <code>42</code>, from the path 15 &rarr; 20 &rarr; 7. For <code>tree = [-3]</code> the answer is <code>-3</code>, because a path needs at least one node.</p>",
    constraints=_cons_s(lo_nodes=1),
    hints=["Look at the highest node of the best path (where it turns). A path that peaks at <code>v</code> is made of <code>v</code> plus a downward chain on the left plus a downward chain on the right.",
           "For each node define <code>down[v]</code>: the best sum of a downward chain that starts at <code>v</code>. A child's chain is only worth taking if it is positive; otherwise skip it.",
           "<code>down[v] = val[v] + max(0, down[left], down[right])</code>, and the best path peaking at <code>v</code> is <code>val[v] + max(0, down[left]) + max(0, down[right])</code>. The answer is the maximum of the latter over all nodes (it can be negative, so start from -infinity)."],
    editorial=["Every path has exactly one highest node, so classify the paths by this peak. For a path peaking at <code>v</code>, the part below <code>v</code> on each side is a downward chain starting at a child, or nothing at all. Both sides are independent, so the best choice on each side is the best downward chain from the child, or 0 (take nothing) if every chain is negative.",
               "Let <code>down[v]</code> be the best sum of a downward chain that starts at <code>v</code> and contains at least <code>v</code>. Then <code>down[v] = val[v] + max(0, down[left], down[right])</code> because the chain either stops at <code>v</code> or continues into exactly one child. The best path with peak <code>v</code> is <code>val[v] + max(0, down[left]) + max(0, down[right])</code>, and the answer is the maximum of this over all nodes.",
               "Pitfalls: initialising the answer with 0 is wrong when every value is negative (the path must have a node), and returning the two-sided sum from a node to its parent would let a path fork. A backwards pass over the level-order array processes children before parents, giving O(n) time and O(n) space."],
    time="O(n)", space="O(n)",
    solution=LINKS(NS) + '''def maxPathSum(tree):
    vals, left, right = _links(tree)
    n = len(vals)
    down = [0] * n
    best = -10 ** 9
    for k in range(n - 1, -1, -1):
        ga = max(0, down[left[k]]) if left[k] != -1 else 0
        gb = max(0, down[right[k]]) if right[k] != -1 else 0
        down[k] = vals[k] + max(ga, gb)
        best = max(best, vals[k] + ga + gb)
    return best
''',
    tests=[[t] for t in _hand + _big],
)


def _b_maxpath(tree):
    return max(sum(x.v for x in p) for p in _all_paths(tree, NS))


def _g_maxpath(r):
    return [_tree(r, r.randint(1, 10), r.choice(MODES), -5, 5, NS)]


CHECKS["tree-maximum-path-sum"] = (_b_maxpath, _g_maxpath, "exact")
VALIDATE["tree-maximum-path-sum"] = _v_trees(SLO, SHI, NS, nmin=1)

# ---------------------------------------------------------------- maximum path sum with at most k nodes
_r = rnd(8310)
_T0 = [-10, 9, 20, N, N, 15, 7]
_hand = [
    [_T0, 2], [_T0, 3], [_T0, 1],
    [[-3], 5],
    [[1, 2, 3], 3],
    [[1, 2, 3], 2],
    [[-1, -2, -3], 2],
    [[5, 4, 8, 11, N, 13, 4, 7, 2, N, N, N, 1], 4],
    [[5, 4, 8, 11, N, 13, 4, 7, 2, N, N, N, 1], 60],
    [[1, N, 2, N, 3, N, 4, N, 5, N, 6], 4],
    [[3, -1, -1, 5, 5, -2, -2, 1, 1], 3],
]
_tb = [_tree(_r, MAXN, "random", SLO, SHI, NS), _tree(_r, MAXN, "complete", -300, 400, NS), _tree(_r, MAXN, "zig", -400, 450, NS)]
_hand += [[_tb[0], 7], [_tb[1], 60], [_tb[2], 25]]
add(
    id="tree-max-path-sum-at-most-k-nodes", title="Maximum Path Sum With at Most K Nodes", diff="Hard", topic="Trees", tier="extra",
    fn="maxPathSumAtMostK", params=[("tree", "int[]"), ("k", "int")], ret="int", cmp="exact",
    desc="<p>A <em>path</em> in a binary tree is a sequence of nodes in which every two neighbours in the sequence are parent and child, and no node is used twice. A path may start and end at any nodes and may turn at a node (go up to a common ancestor and then down again). It must contain at least one node.</p>"
         "<p>Return the largest sum of node values over all paths that contain <strong>at most <code>k</code> nodes</strong>. Values can be negative, and the tree is guaranteed to have at least one node.</p>" + ENC_S +
         "<p>For <code>tree = [-10, 9, 20, 1000, 1000, 15, 7]</code>: with <code>k = 1</code> the answer is <code>20</code>, with <code>k = 2</code> it is <code>35</code> (15 &rarr; 20) and with <code>k = 3</code> it is <code>42</code> (15 &rarr; 20 &rarr; 7).</p>",
    constraints=_cons_s(["1 &le; k &le; 60"], lo_nodes=1),
    hints=["If k were unlimited this is the classic maximum path sum. The limit on the number of nodes means a single number per node is no longer enough.",
           "For each node <code>v</code> and each length <code>j</code> up to <code>k</code>, store the best sum of a downward chain starting at <code>v</code> with at most <code>j</code> nodes (or 0 for taking nothing). A chain is <code>v</code> plus a chain of at most <code>j - 1</code> nodes from one child.",
           "A path peaking at <code>v</code> uses <code>a</code> nodes on the left and <code>k - 1 - a</code> on the right. Because the stored values never decrease with the allowed length, trying every <code>a</code> from 0 to <code>k - 1</code> with the total fixed at <code>k - 1</code> covers all splits with at most <code>k - 1</code> nodes below <code>v</code>. That is O(k) per node."],
    editorial=["Classify paths by their highest node <code>v</code>, as in the unrestricted problem. A path peaking at <code>v</code> consists of <code>v</code>, a downward chain of <code>a</code> nodes below the left child and a downward chain of <code>b</code> nodes below the right child, with <code>a + b + 1 &le; k</code>. Now the best chain depends on its allowed length, so we keep a table.",
               "Let <code>c[v][j]</code> be the best sum of a downward chain that starts at <code>v</code> and has at most <code>j</code> nodes, or 0 if taking nothing is better (so <code>c[v][0] = 0</code>, and a missing child is the all-zero row). Then <code>c[v][j] = max(0, val[v] + max(c[left][j-1], c[right][j-1]))</code>. Rows are non-decreasing in <code>j</code>.",
               "The best path peaking at <code>v</code> with at most <code>k</code> nodes is <code>val[v] + max over a in [0, k-1] of (c[left][a] + c[right][k-1-a])</code>. Because the rows never decrease, giving the two sides a total budget of exactly <code>k - 1</code> already includes every split that uses fewer nodes. The answer is the maximum over all nodes (initialise it to a very small number, since every value may be negative).",
               "Each node costs O(k) for the combination and O(k) for building its row, so the time is O(n &middot; k). Rows of finished children can be discarded to keep memory at the size of the active frontier."],
    time="O(n * k)", space="O(n * k)",
    solution=LINKS(NS) + '''def maxPathSumAtMostK(tree, k):
    vals, left, right = _links(tree)
    n = len(vals)
    zero = [0] * (k + 1)
    rows = [None] * n
    best = -10 ** 9
    for v in range(n - 1, -1, -1):
        A = rows[left[v]] if left[v] != -1 else zero
        B = rows[right[v]] if right[v] != -1 else zero
        m = -10 ** 9
        for a in range(k):
            t = A[a] + B[k - 1 - a]
            if t > m:
                m = t
        if vals[v] + m > best:
            best = vals[v] + m
        row = [0] * (k + 1)
        x = vals[v]
        for j in range(1, k + 1):
            t = x + (A[j - 1] if A[j - 1] > B[j - 1] else B[j - 1])
            row[j] = t if t > 0 else 0
        rows[v] = row
        if left[v] != -1:
            rows[left[v]] = None
        if right[v] != -1:
            rows[right[v]] = None
    return best
''',
    tests=_hand,
)


def _b_maxk(tree, k):
    return max(sum(x.v for x in p) for p in _all_paths(tree, NS) if len(p) <= k)


def _g_maxk(r):
    return [_tree(r, r.randint(1, 10), r.choice(MODES), -5, 5, NS), r.randint(1, 8)]


def _v_maxk_extra(t):
    assert 1 <= t["args"][1] <= 60


CHECKS["tree-max-path-sum-at-most-k-nodes"] = (_b_maxk, _g_maxk, "exact")
VALIDATE["tree-max-path-sum-at-most-k-nodes"] = _v_trees(SLO, SHI, NS, nmin=1, extra=_v_maxk_extra)

# ---------------------------------------------------------------- longest consecutive path in either direction
_r = rnd(8311)
_hand = [[2, 1, 3], [1, 2, 3], [], [5], [1, 2, 2, 3, 3, 3, 1], [3, 2, 4, 1, 3, 5, 5], [4, 3, 5, 2, 4, 6, 6, 1, 3, 5, 7],
         [1, 3, 2, 4, 2, 1, 3], [6, 5, 7, 6, 4, 8, 9, 7, 5, 3, 9, 10], [2, 2, 2, 1, 3, 1, 3]]
_big = [_walk_tree(_r, MAXN, "random", 0.45, 0.45, 0, 4000), _walk_tree(_r, MAXN, "left", 0.5, 0.5, 100, 4000),
        _walk_tree(_r, MAXN, "complete", 0.5, 0.45, 800, 3000), _walk_tree(_r, MAXN, "deep", 0.48, 0.48, 100, 5000)]
add(
    id="tree-longest-consecutive-any-direction", title="Longest Consecutive Path in Either Direction", diff="Hard", topic="Trees", tier="extra",
    fn="longestConsecutiveEither", params=[("tree", "int[]")], ret="int", cmp="exact",
    desc="<p>Consider a path in a binary tree: a sequence of nodes in which every two neighbours are parent and child, and no node is repeated. The path may start and end anywhere and may turn at a node (go up to a common ancestor, then down). Call it <em>consecutive</em> if, read from one end to the other, the values change by exactly <code>+1</code> at every step, or by exactly <code>-1</code> at every step. The two directions must not be mixed: 1, 2, 1 is not consecutive. A single node is a consecutive path.</p>"
         "<p>Return the number of <strong>nodes</strong> on the longest consecutive path (<code>0</code> for the empty tree).</p>" + ENC +
         "<p>For <code>tree = [2, 1, 3]</code> the answer is <code>3</code>: the path 1 &rarr; 2 &rarr; 3 goes up from the left child through the root to the right child. For <code>tree = [1, 2, 3]</code> the answer is <code>2</code>, since 2 &rarr; 1 &rarr; 3 mixes a decrease with an increase.</p>",
    constraints=_cons(),
    hints=["Look at the node where the path turns. The part of the path on each side of it is a downward chain.",
           "For each node keep two numbers: the longest downward chain that increases by 1 at each step (<code>inc</code>) and the longest that decreases by 1 at each step (<code>dec</code>), counted in nodes.",
           "A path through <code>v</code> that increases in one direction is a <code>dec</code> chain going down on one side joined to an <code>inc</code> chain going down on the other. Its length is <code>inc[v] + dec[v] - 1</code>. The two chains use different children automatically, because the child values are <code>val[v] + 1</code> and <code>val[v] - 1</code>."],
    editorial=["Every path has a highest node <code>v</code> (the turning point), and both parts of the path below it are downward chains. Suppose the whole path increases when read from left to right. The part ending at <code>v</code> read downward goes <code>v, v-1, v-2, ...</code>, a decreasing chain, and the part that continues from <code>v</code> goes <code>v, v+1, v+2, ...</code>, an increasing chain. The mirror image (path decreasing left to right) swaps the roles, so one formula covers both.",
               "Compute for every node <code>inc[v]</code> = the number of nodes of the longest downward chain starting at <code>v</code> with each step +1, and <code>dec[v]</code> likewise with each step -1. Both are at least 1. For a child <code>c</code>: if <code>val[c] = val[v] + 1</code> then <code>inc[v] = max(inc[v], inc[c] + 1)</code>, and if <code>val[c] = val[v] - 1</code> then <code>dec[v] = max(dec[v], dec[c] + 1)</code>. A child cannot satisfy both, so the two chains at <code>v</code> never share a child.",
               "The longest consecutive path that turns at <code>v</code> has <code>inc[v] + dec[v] - 1</code> nodes (<code>v</code> is counted once). Take the maximum over all nodes. A backwards pass over the level-order array processes the children first: O(n) time and O(n) space."],
    time="O(n)", space="O(n)",
    solution=LINKS(-1) + '''def longestConsecutiveEither(tree):
    vals, left, right = _links(tree)
    n = len(vals)
    inc = [1] * n
    dec = [1] * n
    best = 0
    for k in range(n - 1, -1, -1):
        for c in (left[k], right[k]):
            if c == -1:
                continue
            if vals[c] == vals[k] + 1 and inc[c] + 1 > inc[k]:
                inc[k] = inc[c] + 1
            elif vals[c] == vals[k] - 1 and dec[c] + 1 > dec[k]:
                dec[k] = dec[c] + 1
        best = max(best, inc[k] + dec[k] - 1)
    return best
''',
    tests=[[t] for t in _hand + _big],
)


def _b_consany(tree):
    if not tree:
        return 0
    best = 0
    for p in _all_paths(tree, -1):
        v = [x.v for x in p]
        d = {b - a for a, b in zip(v, v[1:])}
        if d <= {1} or d <= {-1}:
            best = max(best, len(p))
    return best


def _g_consany(r):
    return [_walk_tree(r, r.randint(0, 11), r.choice(MODES), 0.4, 0.4, 0, 5)]


CHECKS["tree-longest-consecutive-any-direction"] = (_b_consany, _g_consany, "exact")
VALIDATE["tree-longest-consecutive-any-direction"] = _v_trees(0, MAXV, -1)
