"""Problems: binary search trees and advanced tree problems. See data/lib.py for the registry.

Tree encoding used by every problem here: level-order int[], -1 for a missing child,
children of missing nodes are not listed, trailing -1s are dropped, [] is the empty tree.
"""
from itertools import permutations

from lib import add, rnd, CHECKS, VALIDATE, gen_arr  # noqa: F401

INT_MAX = 2 ** 31 - 1
TOPIC = "Binary Search Trees"
MOD = 10 ** 9 + 7

_ENC = (
    "<p><strong>Tree encoding.</strong> A binary tree is passed as an integer array in level order, "
    "the way LeetCode does it. The first entry is the root. After that, the left and right child of every "
    "existing node are written in turn, level by level, from left to right. A missing child is written as "
    "<code>-1</code> (real node values are never negative, so <code>-1</code> cannot be confused with a value). "
    "Missing nodes have no children listed, and trailing <code>-1</code> entries are dropped. The empty tree is <code>[]</code>.</p>"
    "<p>For example, <code>[5,2,7,-1,3,6]</code> is the tree whose root <code>5</code> has left child <code>2</code> and "
    "right child <code>7</code>; node <code>2</code> has no left child and right child <code>3</code>; node <code>7</code> has "
    "left child <code>6</code> and no right child.</p>"
)


# ------------------------------------------------------------------ helpers (tests and brute forces only)
def _node(v):
    return [v, None, None]  # value, left, right


def _ser(root):
    """Nested nodes -> canonical level-order list (-1 = missing, trailing -1s removed)."""
    out = []
    q = [root]
    h = 0
    while h < len(q):
        nd = q[h]
        h += 1
        if nd is None:
            out.append(-1)
            continue
        out.append(nd[0])
        q.append(nd[1])
        q.append(nd[2])
    while out and out[-1] == -1:
        out.pop()
    return out


def _parse(arr):
    """Level-order list -> nested nodes (None for the empty tree)."""
    if not arr:
        return None
    root = _node(arr[0])
    q = [root]
    h = 0
    i = 1
    while h < len(q) and i < len(arr):
        nd = q[h]
        h += 1
        for side in (1, 2):
            if i >= len(arr):
                break
            v = arr[i]
            i += 1
            if v != -1:
                c = _node(v)
                nd[side] = c
                q.append(c)
    return root


def _nodes(root):
    out = [root] if root is not None else []
    h = 0
    while h < len(out):
        nd = out[h]
        h += 1
        for s in (1, 2):
            if nd[s] is not None:
                out.append(nd[s])
    return out


def _inorder(root):
    out, st, cur = [], [], root
    while st or cur is not None:
        while cur is not None:
            st.append(cur)
            cur = cur[1]
        cur = st.pop()
        out.append(cur[0])
        cur = cur[2]
    return out


def _bst_insert(root, v):
    if root is None:
        return _node(v)
    cur = root
    while True:
        s = 1 if v < cur[0] else 2
        if cur[s] is None:
            cur[s] = _node(v)
            return root
        cur = cur[s]


def _bst_from(vals):
    root = None
    for v in vals:
        root = _bst_insert(root, v)
    return root


def _balanced(sorted_vals):
    def go(lo, hi):
        if lo > hi:
            return None
        m = (lo + hi) // 2
        nd = _node(sorted_vals[m])
        nd[1] = go(lo, m - 1)
        nd[2] = go(m + 1, hi)
        return nd
    return go(0, len(sorted_vals) - 1)


def _rand_bst(r, n, hi):
    return _bst_from(r.sample(range(hi + 1), n))


def _rand_shape(r, n, deep=0.0):
    """Random binary tree shape with n nodes (all values 0). `deep` biases growth towards the newest nodes."""
    root = _node(0)
    slots = [(root, 1), (root, 2)]
    for _ in range(n - 1):
        if deep and r.random() < deep:
            j = len(slots) - 1 - r.randint(0, min(1, len(slots) - 1))
        else:
            j = r.randrange(len(slots))
        slots[j], slots[-1] = slots[-1], slots[j]
        par, side = slots.pop()
        c = _node(0)
        par[side] = c
        slots.append((c, 1))
        slots.append((c, 2))
    return root


def _chain(r, n, mode):
    """Path-shaped tree: mode 'L', 'R' or 'Z' (zigzag) or 'X' (random sides)."""
    root = _node(0)
    cur = root
    for i in range(n - 1):
        s = {"L": 1, "R": 2, "Z": 1 + (i % 2), "X": r.choice((1, 2))}[mode]
        c = _node(0)
        cur[s] = c
        cur = c
    return root


def _fill_random(r, root, lo, hi):
    for nd in _nodes(root):
        nd[0] = r.randint(lo, hi)
    return root


def _edges(root):
    nodes = _nodes(root)
    idx = {id(nd): i for i, nd in enumerate(nodes)}
    ed = []
    for nd in nodes:
        for s in (1, 2):
            if nd[s] is not None:
                ed.append((idx[id(nd)], idx[id(nd[s])]))
    return [nd[0] for nd in nodes], ed


def _is_bst(arr):
    ino = _inorder(_parse(arr))
    return all(ino[i] < ino[i + 1] for i in range(len(ino) - 1))


def _chk_tree(arr, nmin, nmax, vmax):
    assert all(isinstance(x, int) and -1 <= x <= vmax for x in arr), "bad entry"
    assert _ser(_parse(arr)) == arr, "tree array is not canonical"
    cnt = sum(1 for x in arr if x != -1)
    assert nmin <= cnt <= nmax, ("node count", cnt)
    assert len(arr) <= 2 * nmax - 1


# =================================================================== EASY

p = add(
    id="bst-range-sum", title="Range Sum of a BST", diff="Easy", topic=TOPIC,
    fn="bstRangeSum", params=[("tree", "int[]"), ("low", "int"), ("high", "int")], ret="int", cmp="exact",
    desc="<p>You are given a binary search tree and two integers <code>low</code> and <code>high</code>. Return the sum of the values of all nodes whose value lies in the inclusive range <code>[low, high]</code>.</p>"
         "<p>All values in the tree are distinct. For every node, all values in its left subtree are smaller and all values in its right subtree are larger.</p>"
         + _ENC +
         "<p><strong>Example 1</strong></p><pre>tree = [10,5,15,3,7,-1,18], low = 7, high = 15\nOutput: 32\nThe nodes 7, 10 and 15 are in range.</pre>"
         "<p><strong>Example 2</strong></p><pre>tree = [10,5,15,3,7,13,18,1,-1,6], low = 6, high = 10\nOutput: 23\nThe nodes 6, 7 and 10 are in range.</pre>",
    constraints=["1 &le; number of nodes &le; 5,000 (so tree.length &le; 9,999)", "0 &le; node value &le; 100,000, all values distinct; the tree is a valid BST",
                 "0 &le; low &le; high &le; 100,000"],
    hints=["Visiting every node and adding up the ones in range works. Can the BST order let you skip whole subtrees?",
           "If a node's value is not larger than <code>low</code>, nothing in its left subtree can be in range.",
           "Symmetrically, if a node's value is not smaller than <code>high</code>, skip its right subtree. Use an explicit stack or recursion and prune with these two rules."],
    editorial=["Traverse from the root. At a node with value <code>x</code>: add <code>x</code> if <code>low &le; x &le; high</code>; descend left only if <code>x &gt; low</code> (smaller values might still be in range) and descend right only if <code>x &lt; high</code>. Everything on the skipped side is guaranteed to be out of range because of the BST ordering.",
               "The pruned walk touches only the part of the tree that overlaps the range plus the path leading to it, so it is O(h + k) for k reported nodes; the simple bound is O(n). A plain traversal that ignores the ordering is also O(n) and is accepted, but it does not use the BST property."],
    time="O(n)", space="O(h)",
    solution='''def parse(tree):
    # nodes are numbered in the order they appear in the array
    val, left, right = [tree[0]], [-1], [-1]
    i, u = 1, 0
    while u < len(val) and i < len(tree):
        for kids in (left, right):
            if i < len(tree):
                x = tree[i]
                i += 1
                if x != -1:
                    kids[u] = len(val)
                    val.append(x)
                    left.append(-1)
                    right.append(-1)
        u += 1
    return val, left, right


def bstRangeSum(tree, low, high):
    val, left, right = parse(tree)
    total = 0
    stack = [0]
    while stack:
        u = stack.pop()
        x = val[u]
        if low <= x <= high:
            total += x
        if x > low and left[u] != -1:
            stack.append(left[u])
        if x < high and right[u] != -1:
            stack.append(right[u])
    return total
''',
    tests=[[[10, 5, 15, 3, 7, -1, 18], 7, 15], [[10, 5, 15, 3, 7, 13, 18, 1, -1, 6], 6, 10], [[5], 5, 5], [[5], 0, 4], [[5], 6, 100000],
           [[1, -1, 2, -1, 3, -1, 4], 2, 3], [[4, 3, -1, 2, -1, 1], 1, 4], [[3, 0, 5, -1, 2, 4, 6], 0, 0],
           [[3, 0, 5, -1, 2, 4, 6], 0, 6], [[3, 0, 5, -1, 2, 4, 6], 7, 9], [[100000], 0, 100000]],
)
_r = rnd(2001)
_a = _ser(_rand_bst(_r, 4000, 100000))
p["tests"] += [[_a, 20000, 60000], [_a, 0, 100000], [_a, 99000, 100000], [_a, 50000, 50000]]
_v = sorted(_r.sample(range(100001), 600))
p["tests"] += [[_ser(_bst_from(_v)), _v[100], _v[500]], [_ser(_bst_from(_v[::-1])), 0, _v[300]]]
_v = sorted(_r.sample(range(100001), 4095))
p["tests"].append([_ser(_balanced(_v)), _v[1000], _v[3000]])


def b_range(tree, low, high):
    return sum(x for x in tree if x != -1 and low <= x <= high)


def g_range(r):
    lo = r.randint(0, 32)
    return [_ser(_rand_bst(r, r.randint(1, 10), 30)), lo, r.randint(lo, 34)]


def v_range(tests):
    for t in tests:
        arr, low, high = t["args"]
        _chk_tree(arr, 1, 5000, 100000)
        assert _is_bst(arr)
        assert 0 <= low <= high <= 100000


CHECKS["bst-range-sum"] = (b_range, g_range, "exact")
VALIDATE["bst-range-sum"] = v_range

p = add(
    id="bst-two-sum-iv", title="Two Sum in a BST", diff="Easy", topic=TOPIC,
    fn="twoSumBst", params=[("tree", "int[]"), ("k", "int")], ret="bool", cmp="exact",
    desc="<p>Given a binary search tree and an integer <code>k</code>, return <code>true</code> if there are two <em>different</em> nodes in the tree whose values add up to <code>k</code>, and <code>false</code> otherwise.</p>"
         "<p>All values in the tree are distinct, and a single node cannot be paired with itself.</p>"
         + _ENC +
         "<p><strong>Example 1</strong></p><pre>tree = [5,3,6,2,4,-1,7], k = 9\nOutput: true\n3 + 6 = 9.</pre>"
         "<p><strong>Example 2</strong></p><pre>tree = [5,3,6,2,4,-1,7], k = 28\nOutput: false</pre>",
    constraints=["1 &le; number of nodes &le; 5,000 (so tree.length &le; 9,999)", "0 &le; node value &le; 100,000, all values distinct; the tree is a valid BST",
                 "0 &le; k &le; 200,000"],
    hints=["Try every pair of nodes: O(n&sup2;). Or store values in a hash set and look up <code>k - x</code> for each node.",
           "What does an inorder traversal of a BST give you? Think about how sorted arrays are searched for a pair.",
           "Collect the inorder values (sorted ascending), then use two pointers from both ends: move the left pointer up when the sum is too small and the right pointer down when it is too large."],
    editorial=["An inorder traversal of a BST visits values in increasing order. Put them into an array and run the classic two-pointer scan: with pointers <code>i &lt; j</code>, if <code>a[i] + a[j] == k</code> the answer is true, if the sum is smaller than <code>k</code> advance <code>i</code>, otherwise retreat <code>j</code>. Because <code>i &lt; j</code>, the same node is never used twice.",
               "A hash set also works in O(n) time: walk the tree and, for every value <code>x</code>, check whether <code>k - x</code> was seen earlier. The two-pointer version is the one that makes use of the sorted order, and it can be turned into O(h) memory with two iterators (one ascending, one descending)."],
    time="O(n)", space="O(n)",
    solution='''def parse(tree):
    val, left, right = [tree[0]], [-1], [-1]
    i, u = 1, 0
    while u < len(val) and i < len(tree):
        for kids in (left, right):
            if i < len(tree):
                x = tree[i]
                i += 1
                if x != -1:
                    kids[u] = len(val)
                    val.append(x)
                    left.append(-1)
                    right.append(-1)
        u += 1
    return val, left, right


def twoSumBst(tree, k):
    val, left, right = parse(tree)
    a = []
    stack = []
    u = 0
    while stack or u != -1:
        while u != -1:
            stack.append(u)
            u = left[u]
        u = stack.pop()
        a.append(val[u])
        u = right[u]
    i, j = 0, len(a) - 1
    while i < j:
        s = a[i] + a[j]
        if s == k:
            return True
        if s < k:
            i += 1
        else:
            j -= 1
    return False
''',
    tests=[[[5, 3, 6, 2, 4, -1, 7], 9], [[5, 3, 6, 2, 4, -1, 7], 28], [[5], 10], [[5, 3, 6, 2, 4, -1, 7], 10], [[2, 1, 3], 4],
           [[2, 1, 3], 5], [[0, -1, 1], 1], [[0], 0], [[1, 0, 2], 3], [[3, 1, 5], 6], [[100000, 0], 100000], [[100000, 99999], 200000]],
)
_r = rnd(2002)
_t = _rand_bst(_r, 4000, 100000)
_a = _ser(_t)
_s = sorted(_inorder(_t))
p["tests"] += [[_a, _s[0] + _s[-1]], [_a, _s[-1] + _s[-2] + 1], [_a, 200000], [_a, _s[1500] + _s[2000]], [_a, 2 * _s[777]]]
_v = sorted(_r.sample(range(0, 100001, 7), 600))
p["tests"] += [[_ser(_bst_from(_v)), _v[0] + _v[-1]], [_ser(_bst_from(_v[::-1])), _v[3] + _v[-1] + 1]]


def b_twosum(tree, k):
    vals = [x for x in tree if x != -1]
    return any(vals[i] + vals[j] == k for i in range(len(vals)) for j in range(i + 1, len(vals)))


def g_twosum(r):
    return [_ser(_rand_bst(r, r.randint(1, 9), 20)), r.randint(0, 40)]


def v_twosum(tests):
    for t in tests:
        arr, k = t["args"]
        _chk_tree(arr, 1, 5000, 100000)
        assert _is_bst(arr) and 0 <= k <= 200000
    assert any(t["expected"] for t in tests) and not all(t["expected"] for t in tests)


CHECKS["bst-two-sum-iv"] = (b_twosum, g_twosum, "exact")
VALIDATE["bst-two-sum-iv"] = v_twosum

p = add(
    id="bst-minimum-absolute-difference", title="Minimum Gap Between BST Nodes", diff="Easy", topic=TOPIC,
    fn="minDiffInBst", params=[("tree", "int[]")], ret="int", cmp="exact",
    desc="<p>Given a binary search tree with at least two nodes, return the smallest absolute difference between the values of any two different nodes.</p>"
         + _ENC +
         "<p><strong>Example 1</strong></p><pre>tree = [4,2,6,1,3]\nOutput: 1\nFor instance |2 - 1| = 1.</pre>"
         "<p><strong>Example 2</strong></p><pre>tree = [1,0,48,-1,-1,12,49]\nOutput: 1\n|48 - 49| = 1.</pre>",
    constraints=["2 &le; number of nodes &le; 5,000 (so tree.length &le; 9,999)", "0 &le; node value &le; 100,000, all values distinct; the tree is a valid BST"],
    hints=["Comparing every pair of nodes is O(n&sup2;). Which pairs can actually give the minimum?",
           "If you list the values in sorted order, the closest pair is always two neighbours in that list.",
           "An inorder traversal of a BST produces the sorted order. Keep the previously visited value and update the best gap as you go."],
    editorial=["For sorted numbers <code>a<sub>1</sub> &lt; a<sub>2</sub> &lt; ... &lt; a<sub>n</sub></code>, any pair <code>(a<sub>i</sub>, a<sub>j</sub>)</code> with <code>j &gt; i + 1</code> has a larger gap than the pair <code>(a<sub>i</sub>, a<sub>i+1</sub>)</code> sitting between them. So only neighbours in sorted order matter.",
               "An inorder traversal visits a BST in sorted order, so it is enough to remember the previous value and take the minimum of <code>current - previous</code>. Do the traversal with an explicit stack to avoid deep recursion on skewed trees. Total work is O(n) with O(h) extra memory (the stack)."],
    time="O(n)", space="O(h)",
    solution='''def parse(tree):
    val, left, right = [tree[0]], [-1], [-1]
    i, u = 1, 0
    while u < len(val) and i < len(tree):
        for kids in (left, right):
            if i < len(tree):
                x = tree[i]
                i += 1
                if x != -1:
                    kids[u] = len(val)
                    val.append(x)
                    left.append(-1)
                    right.append(-1)
        u += 1
    return val, left, right


def minDiffInBst(tree):
    val, left, right = parse(tree)
    best = float("inf")
    prev = None
    stack = []
    u = 0
    while stack or u != -1:
        while u != -1:
            stack.append(u)
            u = left[u]
        u = stack.pop()
        if prev is not None:
            best = min(best, val[u] - prev)
        prev = val[u]
        u = right[u]
    return best
''',
    tests=[[[4, 2, 6, 1, 3]], [[1, 0, 48, -1, -1, 12, 49]], [[0, -1, 100000]], [[5, 3]], [[5, -1, 6]], [[10, 5, 15, 2, 7, 12, 20]],
           [[50, 30, 90, 10, 40, 60, 100, -1, 20, -1, 45]], [[1, -1, 3, -1, 6, -1, 10, -1, 15]], [[15, 10, -1, 6, -1, 3, -1, 1]]],
)
_r = rnd(2003)
p["tests"].append([_ser(_rand_bst(_r, 4000, 100000))])
_v = sorted(_r.sample(range(0, 100001, 30), 3000))
_v[1000] = _v[999] + 11
_v.sort()
p["tests"].append([_ser(_bst_from(_r.sample(_v, len(_v))))])
_v = sorted(_r.sample(range(0, 100001, 150), 600))
p["tests"] += [[_ser(_bst_from(_v))], [_ser(_bst_from(_v[::-1]))]]
p["tests"].append([_ser(_balanced(sorted(_r.sample(range(100001), 4095))))])


def b_mindiff(tree):
    vals = [x for x in tree if x != -1]
    return min(abs(vals[i] - vals[j]) for i in range(len(vals)) for j in range(i + 1, len(vals)))


def g_mindiff(r):
    return [_ser(_rand_bst(r, r.randint(2, 10), 60))]


def v_mindiff(tests):
    for t in tests:
        arr = t["args"][0]
        _chk_tree(arr, 2, 5000, 100000)
        assert _is_bst(arr)


CHECKS["bst-minimum-absolute-difference"] = (b_mindiff, g_mindiff, "exact")
VALIDATE["bst-minimum-absolute-difference"] = v_mindiff


# =================================================================== MEDIUM

p = add(
    id="bst-validate", title="Is This Tree a Valid BST?", diff="Medium", topic=TOPIC,
    fn="isValidBst", params=[("tree", "int[]")], ret="bool", cmp="exact",
    desc="<p>Given an arbitrary binary tree, decide whether it is a valid binary search tree. A tree is a valid BST when, for <em>every</em> node, all values in its left subtree are <strong>strictly smaller</strong> than the node's value and all values in its right subtree are <strong>strictly larger</strong>. Both subtrees must themselves be valid BSTs. Duplicate values therefore make a tree invalid.</p>"
         "<p>Note that comparing a node only with its direct children is not enough.</p>"
         + _ENC +
         "<p><strong>Example 1</strong></p><pre>tree = [2,1,3]\nOutput: true</pre>"
         "<p><strong>Example 2</strong></p><pre>tree = [5,1,4,-1,-1,3,6]\nOutput: false\nThe node 4 is in the right subtree of 5 but is smaller than 5.</pre>"
         "<p><strong>Example 3</strong></p><pre>tree = [10,5,15,-1,-1,6,20]\nOutput: false\nThe node 6 is a valid left child of 15, but it sits in the right subtree of 10 and is smaller than 10.</pre>",
    constraints=["1 &le; number of nodes &le; 5,000 (so tree.length &le; 9,999)", "0 &le; node value &le; 2<sup>31</sup> - 1; values may repeat"],
    hints=["Checking <code>left.val &lt; node.val &lt; right.val</code> at every node is not sufficient. Why does Example 3 fool that check?",
           "Every node lives inside an open interval <code>(lo, hi)</code> defined by its ancestors. The root has no limits; going left tightens <code>hi</code>, going right tightens <code>lo</code>.",
           "Walk the tree with a stack holding <code>(node, lo, hi)</code> and return false the moment a value is not strictly inside its interval. Alternatively check that an inorder traversal is strictly increasing."],
    editorial=["Carry the allowed range down the tree. A node with value <code>x</code> in range <code>(lo, hi)</code> is valid only if <code>lo &lt; x &lt; hi</code>; its left child inherits <code>(lo, x)</code> and its right child inherits <code>(x, hi)</code>. Use <code>None</code> for 'no limit' so that the value 2<sup>31</sup> - 1 and 0 are handled without sentinel tricks (sentinels such as INT_MAX break in fixed-width integer languages).",
               "The equivalent view: the inorder sequence of a valid BST is strictly increasing, so an inorder walk that remembers the previous value can reject on the first non-increase. Both approaches visit each node once, O(n) time, and use O(h) memory when written with an explicit stack."],
    time="O(n)", space="O(h)",
    solution='''def parse(tree):
    val, left, right = [tree[0]], [-1], [-1]
    i, u = 1, 0
    while u < len(val) and i < len(tree):
        for kids in (left, right):
            if i < len(tree):
                x = tree[i]
                i += 1
                if x != -1:
                    kids[u] = len(val)
                    val.append(x)
                    left.append(-1)
                    right.append(-1)
        u += 1
    return val, left, right


def isValidBst(tree):
    val, left, right = parse(tree)
    stack = [(0, None, None)]
    while stack:
        u, lo, hi = stack.pop()
        x = val[u]
        if (lo is not None and x <= lo) or (hi is not None and x >= hi):
            return False
        if left[u] != -1:
            stack.append((left[u], lo, x))
        if right[u] != -1:
            stack.append((right[u], x, hi))
    return True
''',
    tests=[[[2, 1, 3]], [[5, 1, 4, -1, -1, 3, 6]], [[10, 5, 15, -1, -1, 6, 20]], [[1]], [[2, 2, 2]], [[1, 1]], [[2, -1, 2]], [[5, 4, 6, -1, -1, 3, 7]],
           [[0]], [[INT_MAX]], [[INT_MAX, 0]], [[0, -1, INT_MAX]], [[INT_MAX, INT_MAX]], [[3, 1, 5, 0, 2, 4, 6]], [[3, 1, 5, 0, 2, 4, 6, -1, -1, -1, 3]],
           [[8, 4, 12, 2, 6, 10, 14, 1, 3, 5, 7, 9, 11, 13, 15]], [[8, 4, 12, 2, 6, 10, 14, 1, 3, 5, 9, 9, 11, 13, 15]]],
)


def _sneaky(root):
    """Break the BST only through a non-parent ancestor: a left leaf in the right subtree of the root gets a value below the root."""
    present = {nd[0] for nd in _nodes(root)}
    for p_ in _nodes(root[2]):
        c = p_[1]
        if c is not None and c[1] is None and c[2] is None:
            v = root[0] - 1
            while v in present:
                v -= 1
            if v >= 0:
                c[0] = v
                return True
    return False


def _break_deepest(root):
    """Set the deepest leaf to a value that fits its parent but not a farther ancestor."""
    best = None
    st = [(root, None, 0, 0)]
    while st:
        nd, par, side, d = st.pop()
        if nd[1] is None and nd[2] is None and par is not None and (best is None or d > best[3]):
            best = (nd, par, side, d)
        for s in (1, 2):
            if nd[s] is not None:
                st.append((nd[s], nd, s, d + 1))
    nd, par, side, _ = best
    nd[0] = 0 if side == 1 else INT_MAX
    return nd


_r = rnd(2004)
_vals = _r.sample(range(1, INT_MAX), 4000)
_t = _bst_from(_vals)
p["tests"].append([_ser(_t)])
_t = _bst_from(_vals)
assert _sneaky(_t)
p["tests"].append([_ser(_t)])
_t = _bst_from(_vals)
_nd = _nodes(_t)
_nd[2500][0] = _nd[10][0]
p["tests"].append([_ser(_t)])
_zig = []
_lo, _hi = 1000, 1600
while _lo <= _hi:
    _zig.append(_lo)
    _lo += 1
    if _lo <= _hi:
        _zig.append(_hi)
        _hi -= 1
p["tests"].append([_ser(_bst_from(_zig))])
_t = _bst_from(_zig)
_break_deepest(_t)
p["tests"].append([_ser(_t)])
p["tests"].append([_ser(_bst_from(list(range(5, 605))))])
_t = _bst_from(list(range(5, 605)))
_nodes(_t)[-1][0] = 4
p["tests"].append([_ser(_t)])
_t = _rand_shape(_r, 3000, 0.3)
p["tests"].append([_ser(_fill_random(_r, _t, 0, INT_MAX))])
p["tests"].append([_ser(_balanced(sorted(_r.sample(range(INT_MAX), 4095))))])


def b_validate(tree):
    root = _parse(tree)

    def go(nd, out):
        if nd is None:
            return
        go(nd[1], out)
        out.append(nd[0])
        go(nd[2], out)
    ino = []
    go(root, ino)
    return all(ino[i] < ino[i + 1] for i in range(len(ino) - 1))


def g_validate(r):
    n = r.randint(1, 9)
    mode = r.random()
    if mode < 0.2:
        return [_ser(_fill_random(r, _rand_shape(r, n), 0, 8))]
    root = _rand_bst(r, n, 14)
    if mode > 0.45:
        r.choice(_nodes(root))[0] = r.randint(0, 14)
    return [_ser(root)]


def v_validate(tests):
    for t in tests:
        _chk_tree(t["args"][0], 1, 5000, INT_MAX)
    res = [t["expected"] for t in tests]
    assert True in res and False in res
    assert res.count(False) >= 8 and res.count(True) >= 6


CHECKS["bst-validate"] = (b_validate, g_validate, "exact")
VALIDATE["bst-validate"] = v_validate

p = add(
    id="bst-kth-smallest", title="Kth Smallest Value in a BST", diff="Medium", topic=TOPIC,
    fn="kthSmallestInBst", params=[("tree", "int[]"), ("k", "int")], ret="int", cmp="exact",
    desc="<p>Given a binary search tree and an integer <code>k</code>, return the <code>k</code>-th smallest value stored in the tree, counting from 1.</p>"
         "<p>All values are distinct. Try to stop the traversal as soon as the answer is known instead of visiting every node.</p>"
         + _ENC +
         "<p><strong>Example 1</strong></p><pre>tree = [3,1,4,-1,2], k = 1\nOutput: 1</pre>"
         "<p><strong>Example 2</strong></p><pre>tree = [5,3,6,2,4,-1,-1,1], k = 3\nOutput: 3\nThe values in increasing order are 1, 2, 3, 4, 5, 6.</pre>",
    constraints=["1 &le; k &le; number of nodes &le; 5,000 (so tree.length &le; 9,999)", "0 &le; node value &le; 100,000, all values distinct; the tree is a valid BST"],
    hints=["Collecting every value and sorting works, but ignores the tree structure. How can the BST hand you values in sorted order for free?",
           "An inorder traversal (left, node, right) visits the values in increasing order.",
           "Run the inorder traversal iteratively with a stack, count visited nodes, and return the value of the k-th visited node without finishing the walk."],
    editorial=["Inorder traversal of a BST yields the values in ascending order, so the answer is simply the k-th node visited. Implement it with an explicit stack: push the left spine, pop a node (that is the next smallest), then continue with its right child. Stop when the pop counter reaches <code>k</code>.",
               "This takes O(h + k) time and O(h) memory. If the tree is modified often and k-th queries are frequent, store the subtree size in each node and descend by comparing k with the left subtree size, which answers a query in O(h)."],
    time="O(h + k)", space="O(h)",
    solution='''def parse(tree):
    val, left, right = [tree[0]], [-1], [-1]
    i, u = 1, 0
    while u < len(val) and i < len(tree):
        for kids in (left, right):
            if i < len(tree):
                x = tree[i]
                i += 1
                if x != -1:
                    kids[u] = len(val)
                    val.append(x)
                    left.append(-1)
                    right.append(-1)
        u += 1
    return val, left, right


def kthSmallestInBst(tree, k):
    val, left, right = parse(tree)
    stack = []
    u = 0
    while stack or u != -1:
        while u != -1:
            stack.append(u)
            u = left[u]
        u = stack.pop()
        k -= 1
        if k == 0:
            return val[u]
        u = right[u]
    return -1
''',
    tests=[[[3, 1, 4, -1, 2], 1], [[5, 3, 6, 2, 4, -1, -1, 1], 3], [[7], 1], [[3, 1, 4, -1, 2], 4], [[3, 1, 4, -1, 2], 2], [[0, -1, 1], 2],
           [[2, 1, 3], 3], [[1, -1, 2, -1, 3, -1, 4], 4], [[4, 3, -1, 2, -1, 1], 1], [[50, 20, 70, 10, 30, 60, 80], 5]],
)
_r = rnd(2005)
_t = _rand_bst(_r, 4000, 100000)
_a = _ser(_t)
p["tests"] += [[_a, 1], [_a, 4000], [_a, 2000], [_a, 3123]]
_v = sorted(_r.sample(range(100001), 600))
p["tests"] += [[_ser(_bst_from(_v)), 599], [_ser(_bst_from(_v[::-1])), 600], [_ser(_bst_from(_v[::-1])), 1]]
_v = sorted(_r.sample(range(100001), 4095))
p["tests"].append([_ser(_balanced(_v)), 2048])


def b_kth(tree, k):
    return sorted(x for x in tree if x != -1)[k - 1]


def g_kth(r):
    n = r.randint(1, 10)
    return [_ser(_rand_bst(r, n, 40)), r.randint(1, n)]


def v_kth(tests):
    for t in tests:
        arr, k = t["args"]
        _chk_tree(arr, 1, 5000, 100000)
        assert _is_bst(arr)
        assert 1 <= k <= sum(1 for x in arr if x != -1)


CHECKS["bst-kth-smallest"] = (b_kth, g_kth, "exact")
VALIDATE["bst-kth-smallest"] = v_kth

p = add(
    id="bst-insert-level-order", title="Insert Into a BST", diff="Medium", topic=TOPIC,
    fn="insertIntoBst", params=[("tree", "int[]"), ("value", "int")], ret="int[]", cmp="exact",
    desc="<p>You are given a binary search tree (possibly empty) and a <code>value</code> that is not yet in the tree. Insert the value as a <strong>new leaf</strong> using the standard BST insertion walk: starting at the root, go left if the value is smaller than the current node, right otherwise, until you reach a missing child and attach the new node there. Existing nodes are never moved.</p>"
         "<p>Return the resulting tree in the same level-order encoding (with trailing <code>-1</code> entries removed), which makes the answer unique.</p>"
         + _ENC +
         "<p><strong>Example 1</strong></p><pre>tree = [4,2,7,1,3], value = 5\nOutput: [4,2,7,1,3,5]\n5 goes to the left of 7.</pre>"
         "<p><strong>Example 2</strong></p><pre>tree = [4,2,7,1,3], value = 0\nOutput: [4,2,7,1,3,-1,-1,0]\n0 becomes the left child of 1; the two missing children of 3 and the missing right child of 7 sit before it in level order.</pre>"
         "<p><strong>Example 3</strong></p><pre>tree = [], value = 9\nOutput: [9]</pre>",
    constraints=["0 &le; number of nodes &le; 5,000", "0 &le; node value &le; 100,000, all values distinct; the tree is a valid BST", "0 &le; value &le; 100,000 and value is not in the tree"],
    hints=["First find where the new node attaches: compare with the current node and move left or right until the child slot is empty.",
           "After attaching, you must write the tree back as a level-order array. A breadth-first traversal that records <code>-1</code> for every missing child does that.",
           "Do not forget to drop the trailing <code>-1</code> entries at the end, and handle the empty tree separately (the answer is <code>[value]</code>)."],
    editorial=["Decode the array into explicit left/right child links, then walk down from the root: go left when <code>value &lt; node</code>, otherwise right, and stop at the first empty slot to attach the new node.",
               "Encode again with a queue: pop a node, emit its value, push its two children (missing ones push a marker and later emit <code>-1</code>); markers produce no further entries. Finally remove trailing <code>-1</code>s. Decoding, the descent and encoding are each linear, so the total is O(n) time and O(n) space."],
    time="O(n)", space="O(n)",
    solution='''def parse(tree):
    val, left, right = [tree[0]], [-1], [-1]
    i, u = 1, 0
    while u < len(val) and i < len(tree):
        for kids in (left, right):
            if i < len(tree):
                x = tree[i]
                i += 1
                if x != -1:
                    kids[u] = len(val)
                    val.append(x)
                    left.append(-1)
                    right.append(-1)
        u += 1
    return val, left, right


def insertIntoBst(tree, value):
    if not tree:
        return [value]
    val, left, right = parse(tree)
    new = len(val)
    u = 0
    while True:
        kids = left if value < val[u] else right
        if kids[u] == -1:
            kids[u] = new
            break
        u = kids[u]
    val.append(value)
    left.append(-1)
    right.append(-1)
    out = []
    queue = [0]
    head = 0
    while head < len(queue):
        u = queue[head]
        head += 1
        if u == -1:
            out.append(-1)
            continue
        out.append(val[u])
        queue.append(left[u])
        queue.append(right[u])
    while out and out[-1] == -1:
        out.pop()
    return out
''',
    tests=[[[4, 2, 7, 1, 3], 5], [[4, 2, 7, 1, 3], 0], [[], 9], [[5], 3], [[5], 8], [[0], 1], [[1], 0], [[4, 2, 7, 1, 3], 6], [[4, 2, 7, 1, 3], 100000],
           [[4, 2, 7, 1, 3], 8], [[1, -1, 2, -1, 3], 4], [[3, 2, -1, 1], 0], [[3, 1, 5, 0, 2, 4, 6], 7]],
)
_r = rnd(2006)
_t = _rand_bst(_r, 4000, 100000)
_s = set(_inorder(_t))
_free = [x for x in range(100001) if x not in _s]
p["tests"] += [[_ser(_t), _r.choice(_free)] for _ in range(3)]
_v = sorted(_r.sample(range(0, 100000), 600))
p["tests"] += [[_ser(_bst_from(_v)), 100000], [_ser(_bst_from(_v[::-1])), 100000], [_ser(_bst_from(_v[::-1])), _v[300] + 1 if _v[300] + 1 not in _v else 100000]]
_zig = []
_lo, _hi = 1000, 1500
while _lo <= _hi:
    _zig.append(_lo)
    _lo += 1
    if _lo <= _hi:
        _zig.append(_hi)
        _hi -= 1
p["tests"].append([_ser(_bst_from(_zig)), 0])
p["tests"].append([_ser(_balanced(sorted(_r.sample(range(0, 100000, 2), 2047)))), 99999])


def b_insert(tree, value):
    # a BST rebuilt by inserting its values in level order has the same shape
    root = None
    for x in tree + [value]:
        if x != -1:
            root = _bst_insert(root, x)
    return _ser(root) if root is not None else []


def g_insert(r):
    n = r.randint(0, 9)
    vals = r.sample(range(0, 30), n + 1)
    return [_ser(_bst_from(vals[:n])) if n else [], vals[n]]


def v_insert(tests):
    for t in tests:
        arr, value = t["args"]
        _chk_tree(arr, 0, 5000, 100000)
        assert _is_bst(arr) if arr else True
        assert 0 <= value <= 100000 and value not in arr
        _chk_tree(t["expected"], 1, 5001, 100000)


CHECKS["bst-insert-level-order"] = (b_insert, g_insert, "exact")
VALIDATE["bst-insert-level-order"] = v_insert

p = add(
    id="bst-recover-swapped-values", title="Recover a BST With Two Swapped Nodes", diff="Medium", topic=TOPIC,
    fn="recoverSwappedValues", params=[("tree", "int[]")], ret="int[]", cmp="exact",
    desc="<p>A binary search tree with distinct values had the values of exactly two of its nodes exchanged by mistake (the tree shape did not change). The tree you are given is therefore no longer a valid BST.</p>"
         "<p>Return the two values that were exchanged, as an array <code>[a, b]</code> with <code>a &lt; b</code>.</p>"
         + _ENC +
         "<p><strong>Example 1</strong></p><pre>tree = [1,3,-1,-1,2]\nOutput: [1,3]\nThe original tree was [3,1,-1,-1,2]; the values 1 and 3 were swapped.</pre>"
         "<p><strong>Example 2</strong></p><pre>tree = [3,1,4,-1,-1,2]\nOutput: [2,3]\nThe original tree was [2,1,4,-1,-1,3].</pre>",
    constraints=["2 &le; number of nodes &le; 5,000 (so tree.length &le; 9,999)", "0 &le; node value &le; 1,000,000; before the swap all values were distinct and the tree was a valid BST",
                 "Exactly two nodes had their values swapped"],
    hints=["Write down the inorder sequence of a valid BST: it is sorted. What does the sequence look like after two values are swapped?",
           "Scanning the inorder sequence you will see one or two places where a value is larger than its successor (a 'descent').",
           "The larger element of the first descent and the smaller element of the last descent are the two swapped values. With a single descent (swapped neighbours) both come from that one pair."],
    editorial=["Swapping two values in a sorted sequence creates either one descent (when the two were neighbours) or two descents. In the first descent <code>a[i] &gt; a[i+1]</code> the earlier element <code>a[i]</code> is out of place (too big), and in the last descent <code>a[j] &gt; a[j+1]</code> the later element <code>a[j+1]</code> is out of place (too small). Those two elements are the swapped pair.",
               "Do an iterative inorder traversal that remembers the previously visited node; whenever <code>prev &gt; current</code> record <code>first = prev</code> (only the first time) and <code>second = current</code> (every time). Return the two recorded values in ascending order. One pass, O(n) time, O(h) memory. Sorting the inorder list and comparing with the original also works but costs O(n log n)."],
    time="O(n)", space="O(h)",
    solution='''def parse(tree):
    val, left, right = [tree[0]], [-1], [-1]
    i, u = 1, 0
    while u < len(val) and i < len(tree):
        for kids in (left, right):
            if i < len(tree):
                x = tree[i]
                i += 1
                if x != -1:
                    kids[u] = len(val)
                    val.append(x)
                    left.append(-1)
                    right.append(-1)
        u += 1
    return val, left, right


def recoverSwappedValues(tree):
    val, left, right = parse(tree)
    first = second = None
    prev = None
    stack = []
    u = 0
    while stack or u != -1:
        while u != -1:
            stack.append(u)
            u = left[u]
        u = stack.pop()
        if prev is not None and prev > val[u]:
            if first is None:
                first = prev
            second = val[u]
        prev = val[u]
        u = right[u]
    return sorted([first, second])
''',
    tests=[[[1, 3, -1, -1, 2]], [[3, 1, 4, -1, -1, 2]]],
)


def _swapped(r, n, hi, mode):
    root = _rand_bst(r, n, hi) if mode != "chain" else _bst_from(sorted(r.sample(range(hi + 1), n)))
    nodes = _nodes(root)
    byval = sorted(nodes, key=lambda nd: nd[0])
    if mode == "adjacent":
        i = r.randrange(n - 1)
        a, b = byval[i], byval[i + 1]
    elif mode == "root":
        a, b = root, r.choice([nd for nd in nodes if nd is not root])
    elif mode == "extremes":
        a, b = byval[0], byval[-1]
    else:
        a, b = r.sample(nodes, 2)
    a[0], b[0] = b[0], a[0]
    return _ser(root)


_r = rnd(2007)
p["tests"] += [[_swapped(_r, 2, 10, "any")], [_swapped(_r, 3, 10, "adjacent")], [_swapped(_r, 7, 50, "root")], [_swapped(_r, 7, 50, "extremes")],
               [_swapped(_r, 10, 100, "adjacent")], [_swapped(_r, 15, 1000, "any")], [_swapped(_r, 40, 1000000, "any")],
               [_swapped(_r, 4000, 1000000, "any")], [_swapped(_r, 4000, 1000000, "adjacent")], [_swapped(_r, 4000, 1000000, "extremes")],
               [_swapped(_r, 4000, 1000000, "root")], [_swapped(_r, 600, 1000000, "chain")], [_swapped(_r, 600, 1000000, "adjacent")]]


def b_recover(tree):
    ino = []

    def go(nd):
        if nd is None:
            return
        go(nd[1])
        ino.append(nd[0])
        go(nd[2])
    go(_parse(tree))
    srt = sorted(ino)
    return sorted(ino[i] for i in range(len(ino)) if ino[i] != srt[i])


def g_recover(r):
    n = r.randint(2, 10)
    return [_swapped(r, n, 30, r.choice(["any", "adjacent", "root", "extremes", "chain"]))]


def v_recover(tests):
    for t in tests:
        arr = t["args"][0]
        _chk_tree(arr, 2, 5000, 1000000)
        ino = _inorder(_parse(arr))
        assert len(set(ino)) == len(ino)
        srt = sorted(ino)
        diff = [ino[i] for i in range(len(ino)) if ino[i] != srt[i]]
        assert len(diff) == 2 and t["expected"] == sorted(diff)


CHECKS["bst-recover-swapped-values"] = (b_recover, g_recover, "exact")
VALIDATE["bst-recover-swapped-values"] = v_recover

p = add(
    id="tree-house-robber-iii-money", title="Robbing a Tree of Houses", diff="Medium", topic=TOPIC,
    fn="robTree", params=[("tree", "int[]")], ret="int", cmp="exact",
    desc="<p>The houses of a village form a binary tree: each node is a house and its value is the amount of money inside. A thief may rob any set of houses, but two houses connected by an edge (a parent and one of its children) must not both be robbed, otherwise an alarm goes off.</p>"
         "<p>Return the maximum total amount of money the thief can take.</p>"
         + _ENC +
         "<p><strong>Example 1</strong></p><pre>tree = [3,2,3,-1,3,-1,1]\nOutput: 7\nRob the root (3) and the two grandchildren 3 and 1.</pre>"
         "<p><strong>Example 2</strong></p><pre>tree = [3,4,5,1,3,-1,1]\nOutput: 9\nRob the children 4 and 5.</pre>",
    constraints=["1 &le; number of nodes &le; 5,000 (so tree.length &le; 9,999)", "0 &le; node value &le; 100,000"],
    hints=["A greedy rule such as 'always take the richest level' fails. Think about what decision you make at each node: rob it or not.",
           "For every node compute two numbers: the best total in its subtree if the node <em>is</em> robbed, and if it is <em>not</em> robbed.",
           "Robbed: node value plus the 'not robbed' totals of both children. Not robbed: for each child take the better of its two totals. Process children before parents (for example in reverse level order)."],
    editorial=["Let <code>take[u]</code> be the best sum in the subtree of <code>u</code> when <code>u</code> is robbed and <code>skip[u]</code> the best when it is not. Then <code>take[u] = val[u] + skip[l] + skip[r]</code> and <code>skip[u] = max(take[l], skip[l]) + max(take[r], skip[r])</code>, treating a missing child as 0. The answer is <code>max(take[root], skip[root])</code>.",
               "Because the encoding numbers nodes in level order, every child has a larger index than its parent, so looping over the nodes from the last to the first processes children first with no recursion, which keeps skewed trees safe. Time and memory are both O(n). Plain recursion without memoization re-solves grandchildren repeatedly and is exponential."],
    time="O(n)", space="O(n)",
    solution='''def parse(tree):
    val, left, right = [tree[0]], [-1], [-1]
    i, u = 1, 0
    while u < len(val) and i < len(tree):
        for kids in (left, right):
            if i < len(tree):
                x = tree[i]
                i += 1
                if x != -1:
                    kids[u] = len(val)
                    val.append(x)
                    left.append(-1)
                    right.append(-1)
        u += 1
    return val, left, right


def robTree(tree):
    val, left, right = parse(tree)
    n = len(val)
    take = [0] * n
    skip = [0] * n
    for u in range(n - 1, -1, -1):
        t = val[u]
        s = 0
        for c in (left[u], right[u]):
            if c != -1:
                t += skip[c]
                s += max(take[c], skip[c])
        take[u] = t
        skip[u] = s
    return max(take[0], skip[0])
''',
    tests=[[[3, 2, 3, -1, 3, -1, 1]], [[3, 4, 5, 1, 3, -1, 1]], [[0]], [[7]], [[1, 2]], [[2, 1, 3]], [[1, 100, 1]], [[5, 1, -1, 1, -1, 5]],
           [[1, 9, -1, 1, -1, 9]], [[0, 0, 0, 0, 0]], [[10, 1, 1, 10, 10, 10, 10]]],
)
_r = rnd(2008)
p["tests"].append([_ser(_fill_random(_r, _rand_shape(_r, 4000), 0, 100000))])
p["tests"].append([_ser(_fill_random(_r, _rand_shape(_r, 4000, 0.7), 0, 100000))])
p["tests"].append([_ser(_fill_random(_r, _chain(_r, 600, "L"), 0, 100000))])
p["tests"].append([_ser(_fill_random(_r, _chain(_r, 600, "Z"), 0, 100000))])
p["tests"].append([_ser(_fill_random(_r, _chain(_r, 600, "X"), 99000, 100000))])
p["tests"].append([_ser(_fill_random(_r, _rand_shape(_r, 3000), 100000, 100000))])
_t = _balanced(list(range(4095)))
p["tests"].append([_ser(_fill_random(_r, _t, 0, 100000))])


def b_rob(tree):
    vals, ed = _edges(_parse(tree))
    n = len(vals)
    best = 0
    for mask in range(1 << n):
        if any((mask >> a) & 1 and (mask >> b) & 1 for a, b in ed):
            continue
        best = max(best, sum(vals[i] for i in range(n) if (mask >> i) & 1))
    return best


def g_rob(r):
    return [_ser(_fill_random(r, _rand_shape(r, r.randint(1, 12), r.choice([0, 0.5])), 0, 9))]


def v_rob(tests):
    for t in tests:
        _chk_tree(t["args"][0], 1, 5000, 100000)


CHECKS["tree-house-robber-iii-money"] = (b_rob, g_rob, "exact")
VALIDATE["tree-house-robber-iii-money"] = v_rob


# =================================================================== HARD

p = add(
    id="tree-surveillance-cameras", title="Cameras on a Binary Tree", diff="Hard", topic=TOPIC,
    fn="minCameraCover", params=[("tree", "int[]")], ret="int", cmp="exact",
    desc="<p>Cameras are to be installed on the nodes of a binary tree. A camera at a node watches that node, its parent and its children. Return the minimum number of cameras needed so that <strong>every</strong> node of the tree is watched.</p>"
         "<p>Every node in the input has value <code>0</code>, so only the shape of the tree matters.</p>"
         + _ENC +
         "<p><strong>Example 1</strong></p><pre>tree = [0,0,-1,0,0]\nOutput: 1\nA camera on the left child of the root watches the root and both of its own children.</pre>"
         "<p><strong>Example 2</strong></p><pre>tree = [0,0,-1,0,-1,0,-1,-1,0]\nOutput: 2</pre>"
         "<p><strong>Example 3</strong></p><pre>tree = [0]\nOutput: 1</pre>",
    constraints=["1 &le; number of nodes &le; 5,000 (so tree.length &le; 9,999)", "Every node value is 0 (missing children are -1)"],
    hints=["Trying all subsets of nodes is exponential. Try deciding, for each subtree, how its root can end up: with a camera, watched by a child, or still unwatched.",
           "Consider the deepest leaf. A camera on the leaf itself is never better than a camera on its parent. Which nodes does the parent's camera cover that the leaf's camera does not?",
           "Process nodes bottom-up with three states (0 = not watched, 1 = watched without a camera, 2 = has a camera). A node must get a camera if any child is state 0; otherwise it is state 1 if some child has a camera, else state 0. If the root ends in state 0, it needs one more camera."],
    editorial=["Greedy from the bottom: a leaf has no one below it, so it is not watched yet (state 0). Putting the camera on the leaf's parent is at least as good as putting it on the leaf, because it watches the leaf, itself, the grandparent and the sibling. So whenever a node has a child in state 0, install a camera there (state 2). A node with no state-0 child but at least one camera child is watched (state 1). A node with only state-1 children is not watched (state 0) and leaves the decision to its parent. Finally, if the root is in state 0, add a camera at the root.",
               "To avoid recursion on deep trees the solution walks the nodes in reverse level order, which visits every child before its parent. Time is O(n), memory O(n). The same result comes from a DP with the three states per node (camera here, watched by a child, watched by the parent); the greedy is the compressed form of that DP."],
    time="O(n)", space="O(n)",
    solution='''def parse(tree):
    val, left, right = [tree[0]], [-1], [-1]
    i, u = 1, 0
    while u < len(val) and i < len(tree):
        for kids in (left, right):
            if i < len(tree):
                x = tree[i]
                i += 1
                if x != -1:
                    kids[u] = len(val)
                    val.append(x)
                    left.append(-1)
                    right.append(-1)
        u += 1
    return val, left, right


def minCameraCover(tree):
    val, left, right = parse(tree)
    n = len(val)
    # 0 = not watched, 1 = watched, no camera, 2 = camera
    state = [0] * n
    cameras = 0
    for u in range(n - 1, -1, -1):
        kids = [state[c] for c in (left[u], right[u]) if c != -1]
        if 0 in kids:
            state[u] = 2
            cameras += 1
        elif 2 in kids:
            state[u] = 1
    if state[0] == 0:
        cameras += 1
    return cameras
''',
    tests=[[[0, 0, -1, 0, 0]], [[0, 0, -1, 0, -1, 0, -1, -1, 0]], [[0]], [[0, 0]], [[0, 0, 0]], [[0, 0, 0, 0, 0, 0, 0]], [[0, 0, -1, 0, -1, 0]],
           [[0, 0, -1, 0, -1, 0, -1, 0, -1, 0]], [[0, 0, 0, 0, -1, 0, 0, -1, -1, -1, 0]], [[0, -1, 0, -1, 0, -1, 0, -1, 0, -1, 0, -1, 0]]],
)
_r = rnd(2009)
p["tests"].append([_ser(_rand_shape(_r, 4000))])
p["tests"].append([_ser(_rand_shape(_r, 4000, 0.8))])
p["tests"].append([_ser(_rand_shape(_r, 3000, 0.4))])
p["tests"].append([_ser(_chain(_r, 600, "L"))])
p["tests"].append([_ser(_chain(_r, 601, "Z"))])
p["tests"].append([_ser(_chain(_r, 598, "X"))])
p["tests"].append([_ser(_fill_random(_r, _balanced(list(range(4095))), 0, 0))])
p["tests"].append([_ser(_fill_random(_r, _balanced(list(range(2000))), 0, 0))])


def b_cam(tree):
    vals, ed = _edges(_parse(tree))
    n = len(vals)
    full = (1 << n) - 1
    best = n
    for mask in range(1 << n):
        cnt = bin(mask).count("1")
        if cnt >= best:
            continue
        cov = mask
        for a, b in ed:
            if (mask >> a) & 1:
                cov |= 1 << b
            if (mask >> b) & 1:
                cov |= 1 << a
        if cov == full:
            best = cnt
    return best


def g_cam(r):
    return [_ser(_rand_shape(r, r.randint(1, 14), r.choice([0, 0.5, 0.9])))]


def v_cam(tests):
    for t in tests:
        arr = t["args"][0]
        _chk_tree(arr, 1, 5000, 0)
        assert t["expected"] >= 1


CHECKS["tree-surveillance-cameras"] = (b_cam, g_cam, "exact")
VALIDATE["tree-surveillance-cameras"] = v_cam

p = add(
    id="bst-same-shape-reorderings", title="Reorderings That Build the Same BST", diff="Hard", topic=TOPIC,
    fn="countSameBstReorders", params=[("nums", "int[]")], ret="int", cmp="exact",
    desc="<p>The array <code>nums</code> is a permutation of <code>1..n</code>. Inserting its elements one by one, from left to right, into an initially empty binary search tree (each new value goes to the left if it is smaller than the current node and to the right otherwise, ending as a new leaf) produces a tree of some shape.</p>"
         "<p>Count how many <strong>other</strong> permutations of <code>1..n</code> produce exactly the same tree when inserted in the same way. Since the count can be huge, return it modulo <code>1,000,000,007</code>.</p>"
         "<p><strong>Example 1</strong></p><pre>nums = [2,1,3]\nOutput: 1\nThe permutation [2,3,1] builds the same tree (root 2, children 1 and 3).</pre>"
         "<p><strong>Example 2</strong></p><pre>nums = [3,4,5,1,2]\nOutput: 5\nThe tree has root 3, a right chain 4 then 5, and a left subtree 1 then 2. Five other orders build it, e.g. [3,1,2,4,5] and [3,4,1,5,2].</pre>"
         "<p><strong>Example 3</strong></p><pre>nums = [1,2,3]\nOutput: 0\nOnly the order 1, 2, 3 builds this chain.</pre>",
    constraints=["1 &le; nums.length &le; 1,000", "nums is a permutation of 1..nums.length"],
    hints=["Count the orders (including the original) that build the tree, then subtract one. For tiny n you could try all n! permutations, but you need a formula.",
           "The first element must be the root. After it, the elements of the left subtree and the elements of the right subtree can be interleaved in any way, as long as each side keeps its own internal order requirement.",
           "If the left subtree has <code>a</code> nodes and the right one <code>b</code>, the number of interleavings is <code>C(a + b, a)</code>, and the answer for a node is <code>C(a + b, a) * ways(left) * ways(right)</code>. Compute subtree sizes and multiply the binomials of all nodes."],
    editorial=["Let <code>ways(T)</code> be the number of insertion orders that build tree <code>T</code>. The root must come first. The nodes of the left subtree must appear in an order that builds the left subtree, and likewise for the right one, while elements from the two sides are independent of each other, so any interleaving works: <code>ways(T) = C(|L| + |R|, |L|) * ways(L) * ways(R)</code>. The answer is <code>ways(T) - 1</code> modulo 10<sup>9</sup> + 7.",
               "Build the tree by inserting into explicit child arrays (O(n h) worst case, fine for n &le; 1000). Node indexes follow insertion order, so a child always has a larger index than its parent and a reverse loop gives subtree sizes without recursion. Precompute factorials and inverse factorials modulo the prime to evaluate every binomial in O(1), then multiply over all nodes."],
    time="O(n * h)", space="O(n)",
    solution='''def countSameBstReorders(nums):
    MOD = 10 ** 9 + 7
    n = len(nums)
    left = [-1] * n
    right = [-1] * n
    for i in range(1, n):
        x = nums[i]
        u = 0
        while True:
            kids = left if x < nums[u] else right
            if kids[u] == -1:
                kids[u] = i
                break
            u = kids[u]
    size = [1] * n
    for u in range(n - 1, -1, -1):
        if left[u] != -1:
            size[u] += size[left[u]]
        if right[u] != -1:
            size[u] += size[right[u]]
    fact = [1] * (n + 1)
    for i in range(1, n + 1):
        fact[i] = fact[i - 1] * i % MOD
    inv = [pow(f, MOD - 2, MOD) for f in fact]
    ways = 1
    for u in range(n):
        a = size[left[u]] if left[u] != -1 else 0
        b = size[u] - 1 - a
        ways = ways * fact[a + b] % MOD * inv[a] % MOD * inv[b] % MOD
    return (ways - 1) % MOD
''',
    tests=[[[2, 1, 3]], [[3, 4, 5, 1, 2]], [[1, 2, 3]], [[1]], [[1, 2]], [[2, 1]], [[3, 2, 1]], [[2, 3, 1]], [[4, 2, 6, 1, 3, 5, 7]], [[3, 1, 2, 5, 4]],
           [[5, 3, 7, 2, 4, 6, 8, 1]]],
)
_r = rnd(2010)


def _bfs_order_perfect(n):
    """Insertion order (level order) of the perfect/balanced BST over 1..n."""
    out = []
    q = [(1, n)]
    for lo, hi in q:
        if lo > hi:
            continue
        m = (lo + hi) // 2
        out.append(m)
        q.append((lo, m - 1))
        q.append((m + 1, hi))
    return out


for _n in (1000, 700, 300):
    _a = list(range(1, _n + 1))
    _r.shuffle(_a)
    p["tests"].append([_a])
p["tests"] += [[_bfs_order_perfect(1000)], [_bfs_order_perfect(511)], [list(range(1, 1001))], [list(range(1000, 0, -1))]]
_a = []
_lo, _hi = 1, 1000
while _lo <= _hi:
    _a.append(_lo)
    _lo += 1
    if _lo <= _hi:
        _a.append(_hi)
        _hi -= 1
p["tests"].append([_a])
_a = list(range(1, 501)) + list(range(1000, 500, -1))
p["tests"].append([_a])


def b_reorder(nums):
    def shape(seq):
        root = None
        for x in seq:
            root = _bst_insert(root, x)
        return _ser(root)
    target = shape(nums)
    cnt = sum(1 for perm in permutations(sorted(nums)) if shape(perm) == target)
    return (cnt - 1) % MOD


def g_reorder(r):
    a = list(range(1, r.randint(1, 7) + 1))
    r.shuffle(a)
    return [a]


def v_reorder(tests):
    for t in tests:
        nums = t["args"][0]
        assert 1 <= len(nums) <= 1000 and sorted(nums) == list(range(1, len(nums) + 1))
        assert 0 <= t["expected"] < MOD


CHECKS["bst-same-shape-reorderings"] = (b_reorder, g_reorder, "exact")
VALIDATE["bst-same-shape-reorderings"] = v_reorder
