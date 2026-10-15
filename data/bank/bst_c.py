"""Problems: building and counting binary search trees. See data/lib.py for the registry.

Tree encoding used by every problem here: level-order int[], -1 for a missing child,
children of missing nodes are not listed, trailing -1s are dropped, [] is the empty tree.
"""
from itertools import permutations
from math import comb

from lib import add, rnd, CHECKS, VALIDATE, gen_arr  # noqa: F401

TOPIC = "Binary Search Trees"
MOD = 10 ** 9 + 7

_ENC = (
    "<p><strong>Tree encoding.</strong> A binary tree is written as an integer array in level order. "
    "The first entry is the root. After that, the left and right child of every existing node are written in turn, "
    "level by level, from left to right. A missing child is written as <code>-1</code> (real node values are never negative, "
    "so <code>-1</code> cannot be confused with a value). Missing nodes have no children listed, and trailing <code>-1</code> "
    "entries are dropped. The empty tree is <code>[]</code>.</p>"
    "<p>For example, <code>[5,2,7,-1,3,6]</code> is the tree whose root <code>5</code> has left child <code>2</code> and "
    "right child <code>7</code>; node <code>2</code> has no left child and right child <code>3</code>; node <code>7</code> has "
    "left child <code>6</code> and no right child.</p>"
)

# shared helper code shown inside the reference solutions
_SRC_PARSE = '''def parse(tree):
    # nodes are numbered in the order they appear in the array; a child always gets a larger number than its parent
    if not tree:
        return [], [], []
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


'''

_SRC_SER = '''def serialize(root, val, left, right):
    out = []
    queue = [root]
    for u in queue:  # the list grows while we walk it
        if u == -1:
            out.append(-1)
        else:
            out.append(val[u])
            queue.append(left[u])
            queue.append(right[u])
    while out and out[-1] == -1:
        out.pop()
    return out


'''

_SRC_BUILD = '''def build_balanced(a):
    # node i is a[i]; the root of every range lo..hi is the lower middle index
    n = len(a)
    left, right = [-1] * n, [-1] * n
    root = -1
    stack = [(0, n - 1, -1, 0)]
    while stack:
        lo, hi, parent, side = stack.pop()
        if lo > hi:
            continue
        m = (lo + hi) // 2
        if parent == -1:
            root = m
        elif side == 0:
            left[parent] = m
        else:
            right[parent] = m
        stack.append((lo, m - 1, m, 0))
        stack.append((m + 1, hi, m, 1))
    return serialize(root, a, left, right)


'''


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


def _inorder_nodes(root):
    out, st, cur = [], [], root
    while st or cur is not None:
        while cur is not None:
            st.append(cur)
            cur = cur[1]
        cur = st.pop()
        out.append(cur)
        cur = cur[2]
    return out


def _inorder(root):
    return [nd[0] for nd in _inorder_nodes(root)]


def _preorder(root):
    out, st = [], [root] if root is not None else []
    while st:
        nd = st.pop()
        out.append(nd[0])
        if nd[2] is not None:
            st.append(nd[2])
        if nd[1] is not None:
            st.append(nd[1])
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


def _rand_shape(r, n):
    """Random binary tree shape with n nodes (all values 0)."""
    root = _node(0)
    slots = [(root, 1), (root, 2)]
    for _ in range(n - 1):
        j = r.randrange(len(slots))
        slots[j], slots[-1] = slots[-1], slots[j]
        par, side = slots.pop()
        c = _node(0)
        par[side] = c
        slots.append((c, 1))
        slots.append((c, 2))
    return root


def _chain(n, mode):
    root = _node(0)
    cur = root
    for i in range(n - 1):
        s = {"L": 1, "R": 2, "Z": 1 + (i % 2)}[mode]
        c = _node(0)
        cur[s] = c
        cur = c
    return root


def _assign_inorder(root, vals):
    for nd, v in zip(_inorder_nodes(root), vals):
        nd[0] = v
    return root


def _shape_bst(r, n, hi):
    """BST with a random shape (different from the shape of random insertions)."""
    return _assign_inorder(_rand_shape(r, n), sorted(r.sample(range(hi + 1), n)))


def _heights(root):
    h = {}
    for nd in reversed(_nodes(root)):
        h[id(nd)] = 1 + max(h[id(nd[1])] if nd[1] else 0, h[id(nd[2])] if nd[2] else 0)
    return h


def _is_bst(arr):
    ino = _inorder(_parse(arr))
    return all(ino[i] < ino[i + 1] for i in range(len(ino) - 1))


def _chk_tree(arr, nmin, nmax, vmax):
    assert all(isinstance(x, int) and -1 <= x <= vmax for x in arr), "bad entry"
    assert _ser(_parse(arr)) == arr, "tree array is not canonical"
    cnt = sum(1 for x in arr if x != -1)
    assert nmin <= cnt <= nmax, ("node count", cnt)
    assert len(arr) <= 2 * nmax - 1


def _is_balanced_tree(arr):
    root = _parse(arr)
    if root is None:
        return True
    h = _heights(root)
    return all(abs((h[id(nd[1])] if nd[1] else 0) - (h[id(nd[2])] if nd[2] else 0)) <= 1 for nd in _nodes(root))


# =================================================================== EASY

p = add(
    id="sorted-array-to-balanced-bst", title="Sorted Array to Balanced BST", diff="Easy", topic=TOPIC, tier="must",
    fn="sortedArrayToBst", params=[("nums", "int[]")], ret="int[]", cmp="exact",
    desc="<p>The array <code>nums</code> is sorted in strictly increasing order. Build a <em>height-balanced</em> binary search tree that stores exactly these values (in a height-balanced tree the left and right subtrees of every node differ in height by at most one), and return it in level-order encoding.</p>"
         "<p>Many balanced trees exist, so to make the answer unique use this rule: for any range of the array, the root is the <strong>lower middle</strong> element, that is the element at index <code>(lo + hi) / 2</code> rounded down, where <code>lo</code> and <code>hi</code> are the first and last index of the range. The elements to its left form the left subtree and those to its right form the right subtree, built with the same rule.</p>"
         + _ENC +
         "<p><strong>Example 1</strong></p><pre>nums = [1,2,3,4,5]\nOutput: [3,1,4,-1,2,-1,5]\nRoot 3; the left range [1,2] has lower middle 1 (child 2 on its right); the right range [4,5] has lower middle 4 (child 5 on its right).</pre>"
         "<p><strong>Example 2</strong></p><pre>nums = [10,20]\nOutput: [10,-1,20]</pre>",
    constraints=["1 &le; nums.length &le; 5,000", "0 &le; nums[i] &le; 100,000", "nums is strictly increasing"],
    hints=["A binary search tree read in inorder gives a sorted list, so the array is exactly the inorder sequence of the tree you must build.",
           "To keep the tree balanced, the root should split the remaining elements into two parts of (almost) equal size. Which element does that?",
           "Take the middle index of the range as the root, then build the left subtree from the part before it and the right subtree from the part after it. Finally write the tree level by level; recursion depth is only O(log n), or use an explicit stack."],
    editorial=["Choosing the middle element as root puts about half of the values in each subtree, and repeating this rule inside each subtree keeps the sizes of the two sides within one of each other, so heights differ by at most one everywhere. The ordering holds automatically: everything left of the middle is smaller, everything right of it is larger.",
               "Implement it by working on index ranges rather than slicing the array (slicing copies and costs O(n log n)). Every element becomes a node exactly once, so building is O(n). Producing the level-order output is another O(n) pass with a queue. The tree has height about log<sub>2</sub> n, so a recursive version is safe."],
    time="O(n)", space="O(n)",
    solution=_SRC_SER + _SRC_BUILD + '''def sortedArrayToBst(nums):
    return build_balanced(nums)
''',
    tests=[[[5]], [[10, 20]], [[1, 2, 3, 4, 5]], [[0, 1, 2]], [[3, 8, 9, 15]], [[0, 100000]], [[1, 2, 3, 4, 5, 6, 7]],
           [[2, 4, 6, 8, 10, 12]], [[7, 8, 9, 10, 11, 12, 13, 14]]],
)
_r = rnd(8101)
p["tests"].append([sorted(_r.sample(range(100001), 120))])
p["tests"].append([list(range(0, 2047))])
p["tests"].append([sorted(_r.sample(range(100001), 3000))])
p["tests"].append([list(range(50000, 51500))])


def b_sorted(nums):
    def go(a):
        if not a:
            return None
        m = (len(a) - 1) // 2
        nd = _node(a[m])
        nd[1] = go(a[:m])
        nd[2] = go(a[m + 1:])
        return nd
    return _ser(go(nums))


def g_sorted(r):
    return [sorted(r.sample(range(40), r.randint(1, 14)))]


def v_sorted(tests):
    for t in tests:
        nums = t["args"][0]
        assert 1 <= len(nums) <= 5000
        assert all(0 <= x <= 100000 for x in nums)
        assert all(nums[i] < nums[i + 1] for i in range(len(nums) - 1))
        out = t["expected"]
        assert _inorder(_parse(out)) == nums
        assert _is_balanced_tree(out)


CHECKS["sorted-array-to-balanced-bst"] = (b_sorted, g_sorted, "exact")
VALIDATE["sorted-array-to-balanced-bst"] = v_sorted

p = add(
    id="balanced-bst-weighted-depth-sum", title="Weighted Depth of a Balanced BST", diff="Easy", topic=TOPIC, tier="extra",
    fn="weightedDepthSum", params=[("nums", "int[]")], ret="int", cmp="exact",
    desc="<p>The array <code>nums</code> holds distinct values in strictly increasing order. A balanced binary search tree is built from them with this rule: for any range of the array, the root is the <strong>lower middle</strong> element (index <code>(lo + hi) / 2</code> rounded down), the elements before it form the left subtree and the elements after it form the right subtree, built with the same rule.</p>"
         "<p>The root has depth <code>0</code>, its children depth <code>1</code>, and so on. Return the sum, over all nodes, of <code>value &times; depth</code>.</p>"
         "<p>You do not need to build the tree explicitly.</p>"
         "<p><strong>Example 1</strong></p><pre>nums = [1,2,3,4,5]\nOutput: 19\nThe tree has root 3 (depth 0), nodes 1 and 4 at depth 1, nodes 2 and 5 at depth 2: 0 + 1 + 4 + 4 + 10 = 19.</pre>"
         "<p><strong>Example 2</strong></p><pre>nums = [7]\nOutput: 0</pre>",
    constraints=["1 &le; nums.length &le; 5,000", "0 &le; nums[i] &le; 10,000", "nums is strictly increasing"],
    hints=["Every element lands at some depth. Find a way to know the depth of each element without creating node objects.",
           "The element chosen as root of a range sits at the depth of that range; its two sub-ranges are one level deeper.",
           "Walk the ranges with an explicit stack of <code>(lo, hi, depth)</code>: pick <code>m = (lo + hi) // 2</code>, add <code>nums[m] * depth</code>, and push <code>(lo, m-1, depth+1)</code> and <code>(m+1, hi, depth+1)</code>."],
    editorial=["The shape of the tree depends only on the array length, and each range corresponds to one node. Process ranges recursively (or with a stack): the middle element of a range is a node at the range's depth, so its contribution is <code>value &times; depth</code>; its two halves are processed at depth + 1.",
               "Each element is the middle of exactly one range, so there are n ranges in total (plus empty ones that end the recursion immediately). Time is O(n). The recursion depth is O(log n), so recursion is fine; an explicit stack uses O(log n) extra memory as well. The largest possible result is below 10<sup>9</sup>, so it fits in 32 bits."],
    time="O(n)", space="O(log n)",
    solution='''def weightedDepthSum(nums):
    total = 0
    stack = [(0, len(nums) - 1, 0)]
    while stack:
        lo, hi, depth = stack.pop()
        if lo > hi:
            continue
        m = (lo + hi) // 2
        total += nums[m] * depth
        stack.append((lo, m - 1, depth + 1))
        stack.append((m + 1, hi, depth + 1))
    return total
''',
    tests=[[[7]], [[1, 2, 3, 4, 5]], [[0, 1]], [[5, 9]], [[0, 10000]], [[1, 2, 3]], [[2, 3, 5, 8, 13, 21]],
           [[10, 20, 30, 40, 50, 60, 70]]],
)
_r = rnd(8102)
p["tests"].append([sorted(_r.sample(range(10001), 50))])
p["tests"].append([sorted(_r.sample(range(10001), 4000))])
p["tests"].append([list(range(5000, 10001))[:5000]])
p["tests"].append([list(range(0, 5000))])
p["tests"].append([sorted(_r.sample(range(10001), 1023))])


def b_wsum(nums):
    root = _balanced(nums)
    total = 0
    q = [(root, 0)]
    for nd, d in q:
        total += nd[0] * d
        for s in (1, 2):
            if nd[s] is not None:
                q.append((nd[s], d + 1))
    return total


def g_wsum(r):
    return [sorted(r.sample(range(60), r.randint(1, 20)))]


def v_wsum(tests):
    for t in tests:
        nums = t["args"][0]
        assert 1 <= len(nums) <= 5000
        assert all(0 <= x <= 10000 for x in nums)
        assert all(nums[i] < nums[i + 1] for i in range(len(nums) - 1))


CHECKS["balanced-bst-weighted-depth-sum"] = (b_wsum, g_wsum, "exact")
VALIDATE["balanced-bst-weighted-depth-sum"] = v_wsum


# =================================================================== MEDIUM

p = add(
    id="bst-from-preorder", title="Rebuild a BST from Preorder", diff="Medium", topic=TOPIC, tier="common",
    fn="bstFromPreorder", params=[("preorder", "int[]")], ret="int[]", cmp="exact",
    desc="<p>The array <code>preorder</code> is the preorder traversal (node, then left subtree, then right subtree) of a binary search tree with distinct values. Rebuild the tree and return it in level-order encoding.</p>"
         "<p>For a binary search tree, the preorder sequence determines the tree uniquely. Aim for O(n) time.</p>"
         + _ENC +
         "<p><strong>Example 1</strong></p><pre>preorder = [8,5,1,7,10,12]\nOutput: [8,5,10,1,7,-1,12]\nRoot 8; 5 and 10 are its children; 1 and 7 hang below 5; 12 hangs below 10 on the right.</pre>"
         "<p><strong>Example 2</strong></p><pre>preorder = [1,2,3]\nOutput: [1,-1,2,-1,3]</pre>",
    constraints=["1 &le; preorder.length &le; 5,000", "0 &le; preorder[i] &le; 100,000, all values distinct", "preorder is the preorder traversal of some valid BST"],
    hints=["The first element is the root. Everything after it that is smaller belongs to the left subtree, and what follows belongs to the right subtree. Doing this naively can cost O(n&sup2;).",
           "Instead of searching for the split point, think of inserting the values one by one into a BST in the given order: that reproduces exactly the original tree.",
           "To avoid a full descent for every value, keep a stack of the nodes whose right child is still undecided. For each new value, pop every node smaller than it; the last popped node gets the value as its right child, otherwise the node on top of the stack gets it as its left child. Push the new value."],
    editorial=["Inserting the values in preorder into an empty BST gives the original tree, because each node appears before all of its descendants. That is correct but may take O(n&sup2;) if the tree is a long chain.",
               "The monotonic-stack version is linear. The stack holds the current left spine: values decrease from bottom to top. When a new value <code>v</code> arrives, every stack node smaller than <code>v</code> has finished its left subtree, so pop them; the last popped node is the deepest ancestor for which <code>v</code> belongs in the right subtree, so <code>v</code> becomes its right child. If nothing was popped, <code>v</code> is smaller than the top and becomes its left child. Each value is pushed and popped at most once: O(n). The final level-order output is one more O(n) pass."],
    time="O(n)", space="O(n)",
    solution=_SRC_SER + '''def bstFromPreorder(preorder):
    n = len(preorder)
    left, right = [-1] * n, [-1] * n   # node i is preorder[i]
    stack = [0]
    for i in range(1, n):
        v = preorder[i]
        last = -1
        while stack and preorder[stack[-1]] < v:
            last = stack.pop()
        if last != -1:
            right[last] = i
        else:
            left[stack[-1]] = i
        stack.append(i)
    return serialize(0, preorder, left, right)
''',
    tests=[[[8, 5, 1, 7, 10, 12]], [[1, 2, 3]], [[5]], [[3, 2, 1]], [[2, 1, 3]], [[4, 2, 1, 3, 6, 5, 7]], [[10, 20, 15, 12, 30]],
           [[50, 30, 20, 40, 35, 45, 70, 60, 80]], [[1, 100000]], [[100000, 0]]],
)
_r = rnd(8103)
for _n, _hi in ((1500, 100000), (2000, 9999)):
    p["tests"].append([_preorder(_rand_bst(_r, _n, _hi))])
_t = _shape_bst(_r, 700, 100000)
p["tests"].append([_preorder(_t)])
p["tests"].append([list(range(0, 900))])
p["tests"].append([list(range(900, 0, -1))])
p["tests"].append([_preorder(_assign_inorder(_chain(600, "Z"), sorted(_r.sample(range(100001), 600))))])


def b_pre(pre):
    return _ser(_bst_from(pre))


def g_pre(r):
    return [_preorder(_rand_bst(r, r.randint(1, 10), 25))]


def v_pre(tests):
    for t in tests:
        pre = t["args"][0]
        assert 1 <= len(pre) <= 5000 and len(set(pre)) == len(pre)
        assert all(0 <= x <= 100000 for x in pre)
        root = _parse(t["expected"])
        assert _preorder(root) == pre
        assert _is_bst(t["expected"])


CHECKS["bst-from-preorder"] = (b_pre, g_pre, "exact")
VALIDATE["bst-from-preorder"] = v_pre

p = add(
    id="trim-bst-to-range", title="Trim a BST to a Value Range", diff="Medium", topic=TOPIC, tier="common",
    fn="trimBst", params=[("tree", "int[]"), ("low", "int"), ("high", "int")], ret="int[]", cmp="exact",
    desc="<p>Given a binary search tree and two integers <code>low</code> and <code>high</code>, remove every node whose value is outside the inclusive range <code>[low, high]</code> and return the resulting tree in level-order encoding.</p>"
         "<p>Removal works like this: if a node is too small (<code>value &lt; low</code>) it is replaced by its trimmed <em>right</em> subtree, because everything in its left subtree is even smaller; if it is too large (<code>value &gt; high</code>) it is replaced by its trimmed <em>left</em> subtree. Nodes inside the range stay, keep their ancestor-descendant relationships, and their subtrees are trimmed in the same way. The result may be the empty tree <code>[]</code>.</p>"
         "<p>Do not rebuild or rebalance the tree; only cut away the out-of-range parts.</p>"
         + _ENC +
         "<p><strong>Example 1</strong></p><pre>tree = [3,0,4,-1,2,-1,-1,1], low = 1, high = 3\nOutput: [3,2,-1,1]\nNode 0 is too small and is replaced by its right subtree (2 with child 1); node 4 is too large and disappears.</pre>"
         "<p><strong>Example 2</strong></p><pre>tree = [5,3,8,2,4], low = 6, high = 7\nOutput: []</pre>",
    constraints=["1 &le; number of nodes &le; 5,000 (so tree.length &le; 9,999)", "0 &le; node value &le; 100,000, all values distinct; the tree is a valid BST",
                 "0 &le; low &le; high &le; 100,000"],
    hints=["Look at the root first. If it is outside the range, which of its two subtrees can still contain valid values?",
           "A root that is too small is replaced by the trimmed version of its right subtree; a root that is too large by the trimmed version of its left subtree. Repeat until the root is in range.",
           "Once the root is in range, its left child only needs to be checked against <code>low</code> (everything on the left is already below the root, hence below <code>high</code>), and its right child only against <code>high</code>. Skip down while the child is out of range, then continue with the nodes that remain. Parse the array into child links, trim, and write the tree back level by level."],
    editorial=["A node that is too small has an entirely too-small left subtree, so only its right subtree can contribute; symmetrically for a node that is too large. That gives the classic recursion <code>trim(node)</code>: return <code>trim(node.right)</code> if too small, <code>trim(node.left)</code> if too large, otherwise attach <code>trim(node.left)</code> and <code>trim(node.right)</code> to the node and return it.",
               "Each node is visited once, so the time is O(n) and the recursion uses O(h) stack space. The version in the reference solution is iterative: it finds the new root, then for every kept node skips out-of-range children (moving along the right spine for a too-small left child, along the left spine for a too-large right child). Finally the surviving tree is serialized level by level."],
    time="O(n)", space="O(n)",
    solution=_SRC_PARSE + _SRC_SER + '''def trimBst(tree, low, high):
    val, left, right = parse(tree)
    root = 0
    while root != -1 and not (low <= val[root] <= high):
        root = right[root] if val[root] < low else left[root]
    stack = [root] if root != -1 else []
    while stack:
        u = stack.pop()
        c = left[u]
        while c != -1 and val[c] < low:
            c = right[c]
        left[u] = c
        c = right[u]
        while c != -1 and val[c] > high:
            c = left[c]
        right[u] = c
        if left[u] != -1:
            stack.append(left[u])
        if right[u] != -1:
            stack.append(right[u])
    return serialize(root, val, left, right)
''',
    tests=[[[3, 0, 4, -1, 2, -1, -1, 1], 1, 3], [[5, 3, 8, 2, 4], 6, 7], [[5], 5, 5], [[5], 6, 9], [[5], 0, 4], [[1, 0, 2], 1, 2],
           [[10, 5, 15, 3, 7, 12, 20, 1, 4, 6, 8], 4, 12], [[10, 5, 15, 3, 7, 12, 20], 0, 100000], [[1, -1, 2, -1, 3, -1, 4, -1, 5], 2, 4],
           [[5, 4, -1, 3, -1, 2, -1, 1], 2, 4], [[6, 2, 9, 1, 4, 7, 10, -1, -1, 3, 5], 3, 7]],
)
_r = rnd(8104)
_a = _ser(_rand_bst(_r, 1800, 100000))
p["tests"] += [[_a, 25000, 70000], [_a, 49000, 51000], [_a, 0, 100000], [_a, 99000, 100000]]
_a = _ser(_shape_bst(_r, 1000, 100000))
p["tests"].append([_a, 30000, 60000])


def b_trim(tree, low, high):
    root = _parse(tree)
    kept = [nd[0] for nd in _nodes(root) if low <= nd[0] <= high]
    return _ser(_bst_from(kept))


def g_trim(r):
    lo = r.randint(0, 28)
    return [_ser(_rand_bst(r, r.randint(1, 10), 30)), lo, r.randint(lo, 31)]


def v_trim(tests):
    for t in tests:
        arr, low, high = t["args"]
        _chk_tree(arr, 1, 5000, 100000)
        assert _is_bst(arr)
        assert 0 <= low <= high <= 100000
        out = t["expected"]
        assert sorted(_inorder(_parse(out))) == [x for x in sorted(arr) if x != -1 and low <= x <= high]


CHECKS["trim-bst-to-range"] = (b_trim, g_trim, "exact")
VALIDATE["trim-bst-to-range"] = v_trim

p = add(
    id="merge-two-bsts-balanced", title="Merge Two BSTs into a Balanced BST", diff="Medium", topic=TOPIC, tier="extra",
    fn="mergeBsts", params=[("a", "int[]"), ("b", "int[]")], ret="int[]", cmp="exact",
    desc="<p>You are given two binary search trees <code>a</code> and <code>b</code>. Build one new balanced binary search tree that contains every value that occurs in at least one of them. A value present in both trees appears <strong>once</strong> in the result.</p>"
         "<p>To make the answer unique, take the combined values in increasing order and build the tree with this rule: for any range of the sorted list, the root is the <strong>lower middle</strong> element (index <code>(lo + hi) / 2</code> rounded down); the elements before it form the left subtree, the elements after it form the right subtree, built the same way. Return the tree in level-order encoding.</p>"
         "<p>Within one tree all values are distinct. One of the two trees may be empty (<code>[]</code>), but not both.</p>"
         + _ENC +
         "<p><strong>Example 1</strong></p><pre>a = [4,2,6], b = [3,1,5]\nOutput: [3,1,5,-1,2,4,6]\nSorted union: 1 2 3 4 5 6; the lower middle is 3, then 1 on the left (with 2 as its right child) and 5 on the right (with 4 and 6 as children).</pre>"
         "<p><strong>Example 2</strong></p><pre>a = [2,1], b = [2,-1,3]\nOutput: [2,1,3]</pre>",
    constraints=["0 &le; nodes in each tree &le; 2,500, and at least one node in total", "0 &le; node value &le; 100,000; both trees are valid BSTs with distinct values inside each tree",
                 "The two trees may share values"],
    hints=["Converting a BST to a sorted list is easy. What does that suggest for combining two of them?",
           "Take the inorder traversal of each tree, merge the two sorted lists like in merge sort, and skip duplicate values.",
           "Build the balanced tree from the merged sorted list by repeatedly picking the lower middle of a range as root. Use index ranges, not list slices, and serialize level by level."],
    editorial=["An inorder traversal of a BST yields its values in increasing order. Two sorted lists can be merged in linear time with two pointers; while merging, a value equal to the last one written is simply skipped, which removes values that occur in both trees.",
               "The merged list is then turned into a balanced BST exactly as for a sorted array: the middle element becomes the root and both halves are built recursively, which keeps the height at about log<sub>2</sub> n. Total time O(n + m) for the traversals, the merge, the construction and the output; extra space O(n + m)."],
    time="O(n + m)", space="O(n + m)",
    solution=_SRC_PARSE + _SRC_SER + _SRC_BUILD + '''def inorder(tree):
    val, left, right = parse(tree)
    out, stack = [], []
    u = 0 if val else -1
    while stack or u != -1:
        while u != -1:
            stack.append(u)
            u = left[u]
        u = stack.pop()
        out.append(val[u])
        u = right[u]
    return out


def mergeBsts(a, b):
    x, y = inorder(a), inorder(b)
    merged = []
    i = j = 0
    while i < len(x) or j < len(y):
        if j == len(y) or (i < len(x) and x[i] <= y[j]):
            v = x[i]
            i += 1
        else:
            v = y[j]
            j += 1
        if not merged or merged[-1] != v:
            merged.append(v)
    return build_balanced(merged)
''',
    tests=[[[4, 2, 6], [3, 1, 5]], [[2, 1], [2, -1, 3]], [[7], []], [[], [7]], [[5], [5]], [[1], [2]], [[3, 1, 5], [3, 1, 5]],
           [[1, -1, 2, -1, 3], [10, 9, -1, 8]], [[50, 20, 70, 10, 30], [60, 40, 80]], [[0], [100000]]],
)
_r = rnd(8105)
_p1 = _r.sample(range(100001), 1000)
_p2 = _r.sample(range(100001), 900)
p["tests"].append([_ser(_bst_from(_p1)), _ser(_bst_from(_p2))])
_s = sorted(_r.sample(range(100001), 1000))
p["tests"].append([_ser(_balanced(_s)), _ser(_balanced(_s[::2]))])
_s = sorted(_r.sample(range(100001), 600))
p["tests"].append([_ser(_bst_from(_s[:300])), _ser(_bst_from(_s[300:][::-1]))])


def b_merge(a, b):
    vals = sorted(set(nd[0] for nd in _nodes(_parse(a))) | set(nd[0] for nd in _nodes(_parse(b))))
    return _ser(_balanced(vals))


def g_merge(r):
    while True:
        a = _ser(_rand_bst(r, r.randint(0, 7), 14)) if r.random() < 0.9 else []
        b = _ser(_rand_bst(r, r.randint(0, 7), 14)) if r.random() < 0.9 else []
        if a or b:
            return [a, b]


def v_merge(tests):
    for t in tests:
        a, b = t["args"]
        for arr in (a, b):
            if arr:
                _chk_tree(arr, 1, 2500, 100000)
                assert _is_bst(arr)
        assert a or b
        out = t["expected"]
        assert _is_bst(out) and _is_balanced_tree(out)


CHECKS["merge-two-bsts-balanced"] = (b_merge, g_merge, "exact")
VALIDATE["merge-two-bsts-balanced"] = v_merge

p = add(
    id="unique-bst-count", title="Count Unique BST Shapes", diff="Medium", topic=TOPIC, tier="must",
    fn="countUniqueBsts", params=[("n", "int")], ret="int", cmp="exact",
    desc="<p>Count how many structurally different binary search trees can store exactly the values <code>1, 2, ..., n</code>, each value once. Two trees are different if their shapes differ (a node has a left child in one tree and not in the other, and so on).</p>"
         "<p>Return the count modulo <code>1,000,000,007</code>.</p>"
         "<p><strong>Example 1</strong></p><pre>n = 3\nOutput: 5\nThe root can be 1, 2 or 3. With root 2 there is exactly one tree; with root 1 or root 3 there are two trees each (2 + 1 + 2 = 5).</pre>"
         "<p><strong>Example 2</strong></p><pre>n = 1\nOutput: 1</pre>",
    constraints=["1 &le; n &le; 1,000"],
    hints=["Try n = 1, 2, 3, 4 by hand and look at the counts. Fix the root and see what is left to build.",
           "If the root is the value <code>i</code>, the values smaller than <code>i</code> form the left subtree and the larger ones form the right subtree. The two subtrees are chosen independently.",
           "Let <code>f(k)</code> be the answer for k values (<code>f(0) = 1</code> for the empty tree). Then <code>f(k) = sum over i of f(i) * f(k-1-i)</code>. Fill the table bottom-up modulo 1,000,000,007."],
    editorial=["Let <code>f(k)</code> be the number of BSTs on k consecutive values. Only the number of values matters, not the values themselves. If the root is the (i+1)-th smallest value, the left subtree uses i values and the right subtree uses k-1-i values, and any left shape can be combined with any right shape, so <code>f(k) = &sum;<sub>i=0..k-1</sub> f(i) &middot; f(k-1-i)</code> with <code>f(0) = 1</code>.",
               "These are the Catalan numbers 1, 1, 2, 5, 14, 42, ... A bottom-up loop takes O(n&sup2;) time and O(n) space. Products of two reduced values reach about 10<sup>18</sup>, so use a 64-bit type and reduce modulo 1,000,000,007 after each addition of a product (or after the whole sum if the sum is kept in a wide type). The closed form <code>C(2n, n) / (n + 1)</code> with a modular inverse gives O(n) as well."],
    time="O(n^2)", space="O(n)",
    solution='''def countUniqueBsts(n):
    M = 1000000007
    f = [0] * (n + 1)
    f[0] = 1
    for k in range(1, n + 1):
        s = 0
        for i in range(k):
            s += f[i] * f[k - 1 - i]
        f[k] = s % M
    return f[n]
''',
    tests=[[1], [2], [3], [4], [5], [6], [8], [10], [19], [20], [35], [100], [500], [1000]],
)


def b_ubst(n):
    if n > 7:  # too many permutations: closed form
        return comb(2 * n, n) // (n + 1) % MOD
    shapes = set()
    for perm in permutations(range(n)):
        shapes.add(tuple(_ser(_bst_from(perm))))
    return len(shapes) % MOD


def v_ubst(tests):
    known = {1: 1, 2: 2, 3: 5, 4: 14, 5: 42, 10: 16796, 19: 1767263190 % MOD}
    for t in tests:
        n = t["args"][0]
        assert 1 <= n <= 1000
        if n in known:
            assert t["expected"] == known[n]


CHECKS["unique-bst-count"] = (b_ubst, lambda r: [r.randint(1, 7)], "exact")
VALIDATE["unique-bst-count"] = v_ubst

p = add(
    id="count-balanced-subtrees", title="Count Height-Balanced Subtrees", diff="Medium", topic=TOPIC, tier="extra",
    fn="countBalancedSubtrees", params=[("tree", "int[]")], ret="int", cmp="exact",
    desc="<p>A binary tree is <em>height-balanced</em> if, for <strong>every</strong> node in it, the heights of the node's left and right subtrees differ by at most one. The height of an empty subtree is <code>0</code> and the height of a leaf is <code>1</code>.</p>"
         "<p>For a given binary search tree, count the nodes whose subtree (the node together with all its descendants) is height-balanced. Every leaf counts, and the whole tree counts if it is height-balanced.</p>"
         + _ENC +
         "<p><strong>Example 1</strong></p><pre>tree = [4,2,6,1,3,5,7]\nOutput: 7\nEvery subtree of this perfect tree is balanced.</pre>"
         "<p><strong>Example 2</strong></p><pre>tree = [1,-1,2,-1,3]\nOutput: 2\nThe tree is a chain 1 &rarr; 2 &rarr; 3. The subtrees rooted at 3 and at 2 are balanced; the whole tree is not (heights 0 and 2 at the root).</pre>",
    constraints=["1 &le; number of nodes &le; 5,000 (so tree.length &le; 9,999)", "0 &le; node value &le; 100,000, all values distinct; the tree is a valid BST"],
    hints=["First solve the single question: is one given subtree balanced? It needs the heights of both child subtrees and the balance of both children.",
           "Doing that separately for every node repeats work (up to O(n&sup2;)). Can each node reuse what its children already know?",
           "Compute bottom-up for every node the pair (height, balanced?). A node is balanced iff both children are balanced and their heights differ by at most 1. Count the balanced ones. In the level-order array every child comes after its parent, so processing node numbers in reverse order is a valid bottom-up order without recursion."],
    editorial=["Define for each node <code>h(u) = 1 + max(h(left), h(right))</code> and <code>ok(u) = ok(left) and ok(right) and |h(left) - h(right)| &le; 1</code>, with <code>h = 0</code> and <code>ok = true</code> for a missing child. The answer is the number of nodes with <code>ok(u)</code> true.",
               "Every node is evaluated once, so the time is O(n). The reference solution numbers the nodes in the order of the level-order array; a child always has a larger number than its parent, so a single backwards loop processes children before parents, with no recursion and no risk of stack overflow on a long chain."],
    time="O(n)", space="O(n)",
    solution=_SRC_PARSE + '''def countBalancedSubtrees(tree):
    val, left, right = parse(tree)
    n = len(val)
    height = [0] * n
    ok = [True] * n
    count = 0
    for u in range(n - 1, -1, -1):
        l, r = left[u], right[u]
        hl = height[l] if l != -1 else 0
        hr = height[r] if r != -1 else 0
        good = (ok[l] if l != -1 else True) and (ok[r] if r != -1 else True) and abs(hl - hr) <= 1
        height[u] = 1 + max(hl, hr)
        ok[u] = good
        if good:
            count += 1
    return count
''',
    tests=[[[4, 2, 6, 1, 3, 5, 7]], [[1, -1, 2, -1, 3]], [[5]], [[5, 3, 8, 2, -1, -1, -1, 1]], [[2, 1]], [[2, 1, 3]],
           [[4, 2, 6, 1, 3, 5]], [[3, 2, -1, 1]], [[8, 4, 12, 2, 6, 10, 14, 1, -1, 5, 7]], [[10, 5, 20, 3, 8, 15, 30, 1, -1, 7, -1, 12, -1, -1, 40, 0]]],
)
_r = rnd(8106)
p["tests"].append([_ser(_rand_bst(_r, 2000, 100000))])
p["tests"].append([_ser(_balanced(sorted(_r.sample(range(100001), 1500))))])
p["tests"].append([_ser(_assign_inorder(_chain(700, "Z"), sorted(_r.sample(range(100001), 700))))])
p["tests"].append([_ser(_shape_bst(_r, 2000, 100000))])


def b_cbal(tree):
    root = _parse(tree)

    def height(nd):
        return 0 if nd is None else 1 + max(height(nd[1]), height(nd[2]))

    def balanced(nd):
        if nd is None:
            return True
        return abs(height(nd[1]) - height(nd[2])) <= 1 and balanced(nd[1]) and balanced(nd[2])

    return sum(1 for nd in _nodes(root) if balanced(nd))


def g_cbal(r):
    if r.random() < 0.5:
        return [_ser(_rand_bst(r, r.randint(1, 12), 30))]
    return [_ser(_shape_bst(r, r.randint(1, 12), 30))]


def v_cbal(tests):
    for t in tests:
        arr = t["args"][0]
        _chk_tree(arr, 1, 5000, 100000)
        assert _is_bst(arr)
        assert 1 <= t["expected"] <= len([x for x in arr if x != -1])


CHECKS["count-balanced-subtrees"] = (b_cbal, g_cbal, "exact")
VALIDATE["count-balanced-subtrees"] = v_cbal

p = add(
    id="min-swaps-tree-to-bst", title="Minimum Swaps to Turn a Tree into a BST", diff="Medium", topic=TOPIC, tier="extra",
    fn="minSwapsToBst", params=[("tree", "int[]")], ret="int", cmp="exact",
    desc="<p>You are given a binary tree whose node values are distinct but not necessarily ordered. In one operation you may pick any two nodes and swap their values; the shape of the tree never changes.</p>"
         "<p>Return the minimum number of operations needed to make the tree a valid binary search tree (for every node, all values in its left subtree are smaller and all values in its right subtree are larger).</p>"
         + _ENC +
         "<p><strong>Example 1</strong></p><pre>tree = [3,2,1]\nOutput: 2\nThe inorder sequence is 2,3,1 and must become 1,2,3. Swap the values 2 and 1, then 3 and 2 &ndash; two swaps are needed.</pre>"
         "<p><strong>Example 2</strong></p><pre>tree = [4,2,6,1,3,5,7]\nOutput: 0</pre>",
    constraints=["1 &le; number of nodes &le; 5,000 (so tree.length &le; 9,999)", "0 &le; node value &le; 100,000, all values distinct"],
    hints=["For a fixed tree shape, which value must end up in which node? Think about what order an inorder traversal must produce.",
           "The tree is a BST exactly when its inorder sequence is sorted increasing, and the shape fixes the inorder positions. So the target arrangement is unique: the sorted values placed in inorder positions.",
           "The task becomes: the minimum number of swaps to sort the inorder array of distinct numbers. Map every element to its rank, view the array as a permutation, and count cycles: the answer is <code>n - (number of cycles)</code>."],
    editorial=["Because the shape is fixed and a BST's inorder traversal is strictly increasing, the final tree is completely determined: the k-th smallest value goes to the k-th node in inorder. Swapping values of two nodes is swapping two entries of the inorder array, so we need the minimum number of swaps that sorts that array.",
               "Replace each value by its rank (position in sorted order). The array is then a permutation, which decomposes into cycles; a cycle of length L needs exactly L-1 swaps and no swap can do better than merging one cycle fix per swap. Hence the answer is <code>n - cycles</code>. Time is O(n log n) for the sort, space O(n)."],
    time="O(n log n)", space="O(n)",
    solution=_SRC_PARSE + '''def minSwapsToBst(tree):
    val, left, right = parse(tree)
    n = len(val)
    order = []
    stack = []
    u = 0
    while stack or u != -1:
        while u != -1:
            stack.append(u)
            u = left[u]
        u = stack.pop()
        order.append(val[u])
        u = right[u]
    rank = {v: i for i, v in enumerate(sorted(order))}
    target = [rank[v] for v in order]   # where the element at position i has to go
    seen = [False] * n
    cycles = 0
    for i in range(n):
        if not seen[i]:
            cycles += 1
            j = i
            while not seen[j]:
                seen[j] = True
                j = target[j]
    return n - cycles
''',
    tests=[[[3, 2, 1]], [[4, 2, 6, 1, 3, 5, 7]], [[5]], [[1, 2, 3]], [[2, 1, 3]], [[1, -1, 3, -1, 2]], [[3, 1, 2]],
           [[5, 4, 3, 2, 1]], [[10, 20, 30, 40, 50, 60, 70]], [[7, 3, 6, 5, 1, 2, 4]], [[9, 0, 8, 1, 7, 2, 6]]],
)
_r = rnd(8107)


def _shuffled_shape(r, n, hi):
    t = _rand_shape(r, n)
    vals = r.sample(range(hi + 1), n)
    for nd, v in zip(_nodes(t), vals):
        nd[0] = v
    return t


p["tests"].append([_ser(_shuffled_shape(_r, 2500, 100000))])
p["tests"].append([_ser(_shuffled_shape(_r, 1200, 100000))])
_t = _shape_bst(_r, 2000, 100000)
_ns = _inorder_nodes(_t)
for _ in range(30):  # near-BST: a few random swaps
    _a, _b = _r.sample(range(len(_ns)), 2)
    _ns[_a][0], _ns[_b][0] = _ns[_b][0], _ns[_a][0]
p["tests"].append([_ser(_t)])
p["tests"].append([_ser(_shape_bst(_r, 3000, 100000))])


def b_swaps(tree):
    root = _parse(tree)
    nodes = _nodes(root)
    idx = {id(nd): i for i, nd in enumerate(nodes)}
    pos = [idx[id(nd)] for nd in _inorder_nodes(root)]  # node indices in inorder
    start = tuple(nd[0] for nd in nodes)

    def done(state):
        seq = [state[i] for i in pos]
        return all(seq[i] < seq[i + 1] for i in range(len(seq) - 1))

    seen = {start}
    frontier = [start]
    steps = 0
    while frontier:
        if any(done(s) for s in frontier):
            return steps
        nxt = []
        for s in frontier:
            for i in range(len(s)):
                for j in range(i + 1, len(s)):
                    t = list(s)
                    t[i], t[j] = t[j], t[i]
                    t = tuple(t)
                    if t not in seen:
                        seen.add(t)
                        nxt.append(t)
        frontier = nxt
        steps += 1


def g_swaps(r):
    return [_ser(_shuffled_shape(r, r.randint(1, 6), 20))]


def v_swaps(tests):
    for t in tests:
        arr = t["args"][0]
        _chk_tree(arr, 1, 5000, 100000)
        vals = [x for x in arr if x != -1]
        assert len(set(vals)) == len(vals)
        assert 0 <= t["expected"] < len(vals)


CHECKS["min-swaps-tree-to-bst"] = (b_swaps, g_swaps, "exact")
VALIDATE["min-swaps-tree-to-bst"] = v_swaps


# =================================================================== HARD

p = add(
    id="count-bsts-with-height-limit", title="Count BSTs with a Height Limit", diff="Hard", topic=TOPIC, tier="extra",
    fn="countBstsWithHeight", params=[("n", "int"), ("h", "int")], ret="int", cmp="exact",
    desc="<p>Count the structurally different binary search trees that store exactly the values <code>1, 2, ..., n</code> and have height <strong>at most</strong> <code>h</code>. The height of a tree is the number of nodes on the longest path from the root down to a leaf; the empty tree has height <code>0</code> and a single node has height <code>1</code>.</p>"
         "<p>Two trees are different if their shapes differ. Return the count modulo <code>1,000,000,007</code>.</p>"
         "<p><strong>Example 1</strong></p><pre>n = 3, h = 2\nOutput: 1\nOnly the tree with root 2 and children 1 and 3 has height 2; the other four shapes are chains or zigzags of height 3.</pre>"
         "<p><strong>Example 2</strong></p><pre>n = 3, h = 3\nOutput: 5\nThe height limit does not restrict anything, so all five shapes count.</pre>",
    constraints=["1 &le; n &le; 80", "1 &le; h &le; 80"],
    hints=["Without the height limit the answer is the Catalan number. Which extra piece of information does each subtree now need?",
           "If the whole tree has height at most h, its left and right subtrees both have height at most h-1, and the sizes of the subtrees add up to n-1.",
           "Let <code>f[d][k]</code> be the number of shapes with k nodes and height at most d. Then <code>f[0][0] = 1</code>, <code>f[0][k] = 0</code> for k &gt; 0 and <code>f[d][k] = sum over i of f[d-1][i] * f[d-1][k-1-i]</code>. Only the previous row is needed."],
    editorial=["Add the height as a second dimension to the Catalan recurrence. Let <code>f[d][k]</code> count shapes with k nodes and height at most d. A tree with root and subtrees of sizes i and k-1-i has height at most d precisely when both subtrees have height at most d-1, and the two choices are independent: <code>f[d][k] = &sum;<sub>i</sub> f[d-1][i] &middot; f[d-1][k-1-i]</code>. The base row is <code>f[0] = [1, 0, 0, ...]</code> (only the empty tree has height 0).",
               "Counting &ldquo;at most d&rdquo; instead of &ldquo;exactly d&rdquo; avoids subtracting tree counts of the neighbouring heights. The answer is <code>f[h][n]</code>. Values of h above n behave like h = n, since no tree on n nodes is taller than n. Time is O(h &middot; n&sup2;) and space O(n) with two rolling rows."],
    time="O(h * n^2)", space="O(n)",
    solution='''def countBstsWithHeight(n, h):
    M = 1000000007
    h = min(h, n)
    prev = [1] + [0] * n          # height at most 0: only the empty tree
    for _ in range(h):
        cur = [1] + [0] * n
        for k in range(1, n + 1):
            s = 0
            for i in range(k):
                if prev[i]:
                    s += prev[i] * prev[k - 1 - i]
            cur[k] = s % M
        prev = cur
    return prev[n]
''',
    tests=[[1, 1], [1, 5], [2, 1], [2, 2], [3, 2], [3, 3], [4, 2], [4, 3], [5, 3], [7, 4], [10, 5], [20, 20], [30, 6], [50, 10], [80, 80], [80, 12]],
)

_HEIGHT_CACHE = {}


def _all_heights(n):
    if n not in _HEIGHT_CACHE:
        if n == 0:
            _HEIGHT_CACHE[n] = [0]
        else:
            _HEIGHT_CACHE[n] = [1 + max(a, b) for i in range(n) for a in _all_heights(i) for b in _all_heights(n - 1 - i)]
    return _HEIGHT_CACHE[n]


def b_hlimit(n, h):
    if n > 9:  # exact-height counts, subtracted/added up (different formulation from the reference)
        from functools import lru_cache

        @lru_cache(None)
        def ex(k, d):  # shapes with k nodes and height exactly d
            if k == 0:
                return 1 if d == 0 else 0
            if d == 0:
                return 0
            tot = 0
            for i in range(k):
                for a in range(d):
                    tot += ex(i, d - 1) * ex(k - 1 - i, a) + (ex(i, a) * ex(k - 1 - i, d - 1) if a < d - 1 else 0)
            return tot
        return sum(ex(n, d) for d in range(0, min(h, n) + 1)) % MOD
    return sum(1 for x in _all_heights(n) if x <= h) % MOD


def g_hlimit(r):
    return [r.randint(1, 9), r.randint(1, 10)]


def v_hlimit(tests):
    for t in tests:
        n, h = t["args"]
        assert 1 <= n <= 80 and 1 <= h <= 80
        if h < n.bit_length():
            assert t["expected"] == 0  # fewer than 2^h - 1 >= n slots


CHECKS["count-bsts-with-height-limit"] = (b_hlimit, g_hlimit, "exact")
VALIDATE["count-bsts-with-height-limit"] = v_hlimit

p = add(
    id="count-height-balanced-bsts", title="Count Height-Balanced BST Shapes", diff="Hard", topic=TOPIC, tier="extra",
    fn="countAvlShapes", params=[("n", "int")], ret="int", cmp="exact",
    desc="<p>A binary tree is <em>height-balanced</em> if, for every node, the heights of its left and right subtrees differ by at most one (the height of the empty tree is <code>0</code>). Count the structurally different height-balanced binary search trees that store exactly the values <code>1, 2, ..., n</code>.</p>"
         "<p>Two trees are different if their shapes differ. Return the count modulo <code>1,000,000,007</code>.</p>"
         "<p><strong>Example 1</strong></p><pre>n = 4\nOutput: 4\nThe root has subtrees of 2 and 1 nodes, or 1 and 2 nodes; the 2-node subtree can lean left or right: 2 &times; 2 = 4 shapes.</pre>"
         "<p><strong>Example 2</strong></p><pre>n = 3\nOutput: 1</pre>",
    constraints=["1 &le; n &le; 300"],
    hints=["A balanced tree with n nodes has height only about log n. That limits how many different heights you ever have to consider.",
           "For a root whose subtrees have heights a and b, balance requires |a - b| &le; 1, and the whole tree has height 1 + max(a, b). So you need counts of balanced trees by (number of nodes, exact height).",
           "Let <code>g[k][d]</code> be the number of balanced shapes with k nodes and height exactly d. For the root with i nodes on the left and k-1-i on the right: combine <code>g[i][d-1] * g[j][d-1]</code>, <code>g[i][d-1] * g[j][d-2]</code> and <code>g[i][d-2] * g[j][d-1]</code>. Only heights up to about 1.44 log<sub>2</sub> n occur."],
    editorial=["State: <code>g[k][d]</code> = number of height-balanced shapes with k nodes and height exactly d, with <code>g[0][0] = 1</code>. For a tree of height d the subtree heights are (d-1, d-1), (d-1, d-2) or (d-2, d-1); all other pairs are either unbalanced or give a different total height. With a left subtree of i nodes and a right subtree of j = k-1-i nodes, add the products of the matching counts for these three cases.",
               "The smallest balanced tree of height d has <code>N(d) = 1 + N(d-1) + N(d-2)</code> nodes (Fibonacci-like, N(1) = 1, N(2) = 2) and the largest has 2<sup>d</sup>-1 nodes, so d never exceeds roughly 1.44 log<sub>2</sub>(n+2) and each k only has a couple of feasible heights. The cost is O(n&sup2; log n) time and O(n log n) space. The answer is the sum of <code>g[n][d]</code> over all d. The sequence starts 1, 2, 1, 4, 6, 4, 17, 32, ..."],
    time="O(n^2 log n)", space="O(n log n)",
    solution='''def countAvlShapes(n):
    M = 1000000007
    mn = [0, 1]                      # mn[d] = fewest nodes in a balanced tree of height d
    while mn[-1] <= n:
        mn.append(1 + mn[-1] + mn[-2])
    H = len(mn) - 2                  # largest height that fits
    g = [[0] * (H + 1) for _ in range(n + 1)]
    g[0][0] = 1
    for k in range(1, n + 1):
        for d in range(1, H + 1):
            if k < mn[d] or k > (1 << d) - 1:
                continue
            s = 0
            for i in range(k):
                j = k - 1 - i
                a = g[i][d - 1]
                b = g[j][d - 1]
                s += a * b
                if d >= 2:
                    s += a * g[j][d - 2] + g[i][d - 2] * b
            g[k][d] = s % M
    return sum(g[n]) % M
''',
    tests=[[1], [2], [3], [4], [5], [6], [7], [8], [10], [15], [31], [64], [127], [200], [300]],
)


def b_avl(n):
    if n > 10:  # memoised recursion over (nodes, height) instead of enumerating shapes
        from functools import lru_cache

        @lru_cache(None)
        def cnt(k, d):  # balanced shapes with k nodes and height exactly d
            if k == 0:
                return 1 if d == 0 else 0
            if d <= 0:
                return 0
            return sum(cnt(i, a) * cnt(k - 1 - i, b)
                       for i in range(k) for a in (d - 1, d - 2) for b in (d - 1, d - 2)
                       if max(a, b) == d - 1 and abs(a - b) <= 1 and a >= 0 and b >= 0)
        return sum(cnt(n, d) for d in range(0, n + 1)) % MOD
    memo = {}

    def shapes(k):
        # list of (height, balanced) for every binary tree shape with k nodes
        if k in memo:
            return memo[k]
        if k == 0:
            res = [(0, True)]
        else:
            res = []
            for i in range(k):
                for ha, ba in shapes(i):
                    for hb, bb in shapes(k - 1 - i):
                        res.append((1 + max(ha, hb), ba and bb and abs(ha - hb) <= 1))
        memo[k] = res
        return res

    return sum(1 for _, ok in shapes(n) if ok) % MOD


def v_avl(tests):
    known = {1: 1, 2: 2, 3: 1, 4: 4, 5: 6, 6: 4, 7: 17, 8: 32, 9: 44, 10: 60}
    for t in tests:
        n = t["args"][0]
        assert 1 <= n <= 300
        if n in known:
            assert t["expected"] == known[n]


CHECKS["count-height-balanced-bsts"] = (b_avl, lambda r: [r.randint(1, 10)], "exact")
VALIDATE["count-height-balanced-bsts"] = v_avl

p = add(
    id="optimal-bst-search-cost", title="Optimal Binary Search Tree Cost", diff="Hard", topic=TOPIC, tier="extra",
    fn="optimalBstCost", params=[("freq", "int[]")], ret="int", cmp="exact",
    desc="<p>A dictionary stores the keys <code>1, 2, ..., n</code> in a binary search tree. Key <code>i + 1</code> will be looked up <code>freq[i]</code> times. Looking up a key costs its depth in the tree, where the root has depth <code>1</code>, its children depth <code>2</code>, and so on.</p>"
         "<p>Among all binary search trees that store these n keys, find the smallest possible total cost, that is the minimum of the sum of <code>freq[i] &times; depth(key i + 1)</code> over all keys.</p>"
         "<p><strong>Example 1</strong></p><pre>freq = [34,8,50]\nOutput: 142\nKey 3 as root (cost 50), key 1 as its left child (cost 34 &times; 2) and key 2 below it as the right child (8 &times; 3): 50 + 68 + 24 = 142.</pre>"
         "<p><strong>Example 2</strong></p><pre>freq = [3,3,3]\nOutput: 15\nThe middle key as root: 3 + 6 + 6.</pre>",
    constraints=["1 &le; freq.length &le; 400", "1 &le; freq[i] &le; 1,000"],
    hints=["Choosing the root splits the keys into a left part and a right part, each of which becomes a subtree. What happens to the depth of every key in those parts?",
           "Every key in a subtree is one level deeper than it would be as the root of that subtree, which adds exactly the total frequency of the subtree to its cost. Define the cost of a key interval <code>[i, j)</code> and try all roots <code>r</code> in it.",
           "<code>cost[i][j] = min over r of (cost[i][r] + cost[r+1][j]) + sum(freq[i..j-1])</code>. Prefix sums give interval sums in O(1). Trying all roots is O(n&sup3;); to get O(n&sup2;) note that the best root of <code>[i, j)</code> lies between the best root of <code>[i, j-1)</code> and the best root of <code>[i+1, j)</code> (Knuth's optimization)."],
    editorial=["For the key interval <code>[i, j)</code> let <code>cost[i][j]</code> be the minimum total cost of a BST on exactly these keys. If key r is the root, the cost is its own frequency plus the cost of both subtrees, and every key of both subtrees moves one level deeper, which adds their frequencies once more. In total <code>cost[i][j] = min<sub>r</sub>(cost[i][r] + cost[r+1][j]) + W(i, j)</code> where <code>W</code> is the sum of frequencies in the interval (a prefix-sum difference). The empty interval costs 0.",
               "Filling the table by increasing interval length gives O(n&sup3;), fine up to a few hundred keys in a compiled language. The cost function satisfies the quadrangle inequality, so the optimal root is monotone: <code>opt[i][j-1] &le; opt[i][j] &le; opt[i+1][j]</code>. Restricting the search for r to that window makes the work along each diagonal telescope, giving O(n&sup2;) time overall with O(n&sup2;) memory."],
    time="O(n^2)", space="O(n^2)",
    solution='''def optimalBstCost(freq):
    n = len(freq)
    pre = [0] * (n + 1)
    for i, f in enumerate(freq):
        pre[i + 1] = pre[i] + f
    cost = [[0] * (n + 1) for _ in range(n + 2)]   # cost[i][j]: keys i..j-1
    opt = [[0] * (n + 1) for _ in range(n + 2)]
    for i in range(n):
        cost[i][i + 1] = freq[i]
        opt[i][i + 1] = i
    for length in range(2, n + 1):
        for i in range(n - length + 1):
            j = i + length
            best, best_r = None, -1
            for r in range(opt[i][j - 1], opt[i + 1][j] + 1):
                c = cost[i][r] + cost[r + 1][j]
                if best is None or c < best:
                    best, best_r = c, r
            cost[i][j] = best + pre[j] - pre[i]
            opt[i][j] = best_r
    return cost[0][n]
''',
    tests=[[[34, 8, 50]], [[3, 3, 3]], [[10]], [[1, 1]], [[5, 1]], [[1, 5]], [[1, 1, 1, 1, 1, 1, 1]], [[1000, 1, 1, 1, 1000]],
           [[4, 2, 6, 3]], [[1, 2, 3, 4, 5, 6, 7, 8]], [[8, 7, 6, 5, 4, 3, 2, 1]]],
)
_r = rnd(8108)
p["tests"].append([[_r.randint(1, 1000) for _ in range(120)]])
p["tests"].append([[_r.randint(1, 1000) for _ in range(400)]])
p["tests"].append([[1 + (i * 37) % 1000 for i in range(400)]])
p["tests"].append([[1000] * 400])


def b_opt(freq):
    n = len(freq)
    if n > 8:  # plain cubic interval DP
        c = [[0] * (n + 1) for _ in range(n + 1)]
        for ln in range(1, n + 1):
            for i in range(n - ln + 1):
                j = i + ln
                c[i][j] = min(c[i][r] + c[r + 1][j] for r in range(i, j)) + sum(freq[i:j])
        return c[0][n]

    def go(lo, hi, depth):
        if lo >= hi:
            return 0
        return min(freq[r] * depth + go(lo, r, depth + 1) + go(r + 1, hi, depth + 1) for r in range(lo, hi))

    return go(0, n, 1)


def g_opt(r):
    return [[r.randint(1, 12) for _ in range(r.randint(1, 8))]]


def v_opt(tests):
    for t in tests:
        f = t["args"][0]
        assert 1 <= len(f) <= 400 and all(1 <= x <= 1000 for x in f)
        assert sum(f) <= t["expected"] <= sum(f) * len(f)


CHECKS["optimal-bst-search-cost"] = (b_opt, g_opt, "exact")
VALIDATE["optimal-bst-search-cost"] = v_opt
