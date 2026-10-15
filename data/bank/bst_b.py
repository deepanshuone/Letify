"""Problems: BST order statistics (k-th, closest, ranges, counting, pairs). See data/lib.py for the registry.

Tree encoding used by every problem here: level-order int[], -1 for a missing child,
children of missing nodes are not listed, trailing -1s are dropped, [] is the empty tree.
"""
from bisect import bisect_left, bisect_right
from collections import Counter

from lib import add, rnd, CHECKS, VALIDATE, gen_arr  # noqa: F401

TOPIC = "Binary Search Trees"

_ENC = (
    "<p><strong>Tree encoding.</strong> A binary tree is passed as an integer array in level order. "
    "The first entry is the root. After that, the left and right child of every existing node are written in turn, "
    "level by level, from left to right. A missing child is written as <code>-1</code> (node values are never negative, "
    "so <code>-1</code> cannot be confused with a value). Missing nodes have no children listed, and trailing "
    "<code>-1</code> entries are dropped. The empty tree is <code>[]</code>.</p>"
    "<p>For example, <code>[5,2,7,-1,3,6]</code> is the tree whose root <code>5</code> has left child <code>2</code> and "
    "right child <code>7</code>; node <code>2</code> has no left child and right child <code>3</code>; node <code>7</code> has "
    "left child <code>6</code> and no right child.</p>"
)

# Reference solutions are executed on their own, so each one that needs the tree carries this parser.
# Nodes are numbered in the order they appear in the array, which is also level order.
_PARSE = '''def parse(tree):
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


# ------------------------------------------------------------------ helpers (tests and brute forces only)
def _node(v):
    return [v, None, None]  # value, left, right


def _ser(root):
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


def _bst_insert(root, v, r=None):
    """Insert v; with r given, an equal value goes to a random side (duplicates allowed)."""
    if root is None:
        return _node(v)
    cur = root
    while True:
        if v == cur[0] and r is not None:
            s = r.choice((1, 2))
        else:
            s = 1 if v < cur[0] else 2
        if cur[s] is None:
            cur[s] = _node(v)
            return root
        cur = cur[s]


def _bst_from(vals, r=None):
    root = None
    for v in vals:
        root = _bst_insert(root, v, r)
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


def _rand_arr(r, n, hi):
    """Random BST (insertion order random) with n distinct values from 0..hi, as an array."""
    return _ser(_bst_from(r.sample(range(hi + 1), n)))


def _chain_arr(r, n, hi, rev=False):
    v = sorted(r.sample(range(hi + 1), n))
    return _ser(_bst_from(v[::-1] if rev else v))


def _bal_arr(r, n, hi):
    return _ser(_balanced(sorted(r.sample(range(hi + 1), n))))


def _vals(arr):
    return [x for x in arr if x != -1]


def _chk_tree(arr, nmin, nmax, vmax, distinct=True):
    assert all(isinstance(x, int) and -1 <= x <= vmax for x in arr), "bad entry"
    assert _ser(_parse(arr)) == arr, "tree array is not canonical"
    cnt = len(_vals(arr))
    assert nmin <= cnt <= nmax, ("node count", cnt)
    ino = _inorder(_parse(arr))
    if distinct:
        assert all(ino[i] < ino[i + 1] for i in range(len(ino) - 1)), "not a BST with distinct values"
    else:
        assert all(ino[i] <= ino[i + 1] for i in range(len(ino) - 1)), "not a BST"


# =================================================================== EASY

p = add(
    id="bst-kth-largest-value", title="Kth Largest Value in a BST", diff="Easy", topic=TOPIC,
    fn="kthLargestInBst", params=[("tree", "int[]"), ("k", "int")], ret="int", cmp="exact",
    desc="<p>Given a binary search tree and an integer <code>k</code>, return the <code>k</code>-th <strong>largest</strong> value stored in the tree, counting from 1 (so <code>k = 1</code> is the maximum).</p>"
         "<p>All values are distinct. Try to stop as soon as the answer is known instead of visiting every node.</p>"
         + _ENC +
         "<p><strong>Example 1</strong></p><pre>tree = [5,3,6,2,4,-1,7], k = 2\nOutput: 6\nThe values from largest to smallest are 7, 6, 5, 4, 3, 2.</pre>"
         "<p><strong>Example 2</strong></p><pre>tree = [3,1,4,-1,2], k = 4\nOutput: 1</pre>",
    constraints=["1 &le; k &le; number of nodes &le; 5,000 (so tree.length &le; 9,999)", "0 &le; node value &le; 100,000, all values distinct; the tree is a valid BST"],
    hints=["Collecting all values and sorting them in descending order works. How can the tree give you the values in order without sorting?",
           "An inorder walk (left, node, right) gives ascending order. What do you get if you mirror it?",
           "Walk the tree in <em>reverse</em> inorder (right, node, left) with an explicit stack, count the nodes you pop, and return the value of the k-th one."],
    editorial=["A BST's inorder traversal is ascending, so the mirrored traversal, which visits the right subtree first, then the node, then the left subtree, produces the values in descending order. The k-th node visited is the k-th largest value, and the walk can stop right there.",
               "Implement it iteratively: push the right spine onto a stack, pop a node (the next largest), count it, then continue with that node's left child. The cost is O(h + k) time and O(h) memory, where h is the tree height. Counting from the other end (the (n-k+1)-th smallest) also works but needs the node count first."],
    time="O(h + k)", space="O(h)",
    solution=_PARSE + '''def kthLargestInBst(tree, k):
    val, left, right = parse(tree)
    stack = []
    u = 0
    while stack or u != -1:
        while u != -1:
            stack.append(u)
            u = right[u]
        u = stack.pop()
        k -= 1
        if k == 0:
            return val[u]
        u = left[u]
    return -1
''',
    tests=[[[5, 3, 6, 2, 4, -1, 7], 2], [[3, 1, 4, -1, 2], 4], [[7], 1], [[3, 1, 4, -1, 2], 1], [[0, -1, 1], 1], [[0, -1, 1], 2],
           [[2, 1, 3], 2], [[1, -1, 2, -1, 3, -1, 4], 4], [[4, 3, -1, 2, -1, 1], 2], [[50, 20, 70, 10, 30, 60, 80], 5]],
)
_r = rnd(7001)
_a = _rand_arr(_r, 3000, 100000)
p["tests"] += [[_a, 1], [_a, 1777]]
p["tests"].append([_chain_arr(_r, 1200, 100000), 1100])
p["tests"].append([_chain_arr(_r, 1200, 100000, rev=True), 3])
p["tests"].append([_bal_arr(_r, 2047, 100000), 1024])


def b_kthl(tree, k):
    return sorted(_vals(tree), reverse=True)[k - 1]


def g_kthl(r):
    n = r.randint(1, 10)
    return [_rand_arr(r, n, 40), r.randint(1, n)]


def v_kthl(tests):
    for t in tests:
        arr, k = t["args"]
        _chk_tree(arr, 1, 5000, 100000)
        assert 1 <= k <= len(_vals(arr))


CHECKS["bst-kth-largest-value"] = (b_kthl, g_kthl, "exact")
VALIDATE["bst-kth-largest-value"] = v_kthl

p = add(
    id="bst-closest-value", title="Closest Value in a BST", diff="Easy", topic=TOPIC,
    fn="closestValueInBst", params=[("tree", "int[]"), ("target", "int")], ret="int", cmp="exact",
    desc="<p>Given a binary search tree and an integer <code>target</code>, return the value stored in the tree that is closest to <code>target</code>, that is, the value <code>x</code> with the smallest <code>|x - target|</code>.</p>"
         "<p>If two values are equally close, return the <strong>smaller</strong> one. The target itself does not have to be in the tree.</p>"
         + _ENC +
         "<p><strong>Example 1</strong></p><pre>tree = [10,5,15,2,7,12,20], target = 13\nOutput: 12\n12 is at distance 1, 15 is at distance 2.</pre>"
         "<p><strong>Example 2</strong></p><pre>tree = [8,4,12,2,6,10,14], target = 9\nOutput: 8\n8 and 10 are both at distance 1, so the smaller one wins.</pre>",
    constraints=["1 &le; number of nodes &le; 5,000 (so tree.length &le; 9,999)", "0 &le; node value &le; 100,000, all values distinct; the tree is a valid BST", "-100,000 &le; target &le; 200,000"],
    hints=["Scanning all the nodes and keeping the best one is O(n). The BST ordering lets you do better on a balanced tree.",
           "Search for the target as if you wanted to insert it. Every node on that search path is a candidate for the closest value.",
           "Walk down from the root: update the best candidate (smaller distance, or equal distance and smaller value) at every node, then go left if <code>target &lt; node</code>, otherwise right."],
    editorial=["The closest value is either the largest value not above the target (its floor) or the smallest value not below it (its ceiling). Both of them lie on the search path of the target, because the path passes every node where the answer could still change sides. So walk down once, compare each visited value with the best so far, and move left when the target is smaller than the node and right otherwise.",
               "For ties, compare the pair (distance, value) so that the smaller value wins at equal distance. The walk costs O(h) time and O(1) memory beyond the parsed tree."],
    time="O(h)", space="O(1)",
    solution=_PARSE + '''def closestValueInBst(tree, target):
    val, left, right = parse(tree)
    best = val[0]
    u = 0
    while u != -1:
        x = val[u]
        if (abs(x - target), x) < (abs(best - target), best):
            best = x
        u = left[u] if target < x else right[u]
    return best
''',
    tests=[[[10, 5, 15, 2, 7, 12, 20], 13], [[8, 4, 12, 2, 6, 10, 14], 9], [[5], 5], [[5], 100000], [[5], -100000], [[8, 4, 12, 2, 6, 10, 14], 11],
           [[8, 4, 12, 2, 6, 10, 14], 7], [[8, 4, 12, 2, 6, 10, 14], 0], [[8, 4, 12, 2, 6, 10, 14], 200000], [[1, -1, 3, -1, 5, -1, 7], 4],
           [[7, 5, -1, 3, -1, 1], 6], [[100000, 0], 50000], [[100000, 0], 50001], [[100000, 0], 49999]],
)
_r = rnd(7002)
_a = _rand_arr(_r, 3000, 100000)
p["tests"] += [[_a, 54321], [_a, 200000]]
p["tests"].append([_chain_arr(_r, 1500, 100000), 77777])
p["tests"].append([_bal_arr(_r, 2047, 100000), 31415])


def b_closest(tree, target):
    return min(_vals(tree), key=lambda v: (abs(v - target), v))


def g_closest(r):
    return [_rand_arr(r, r.randint(1, 10), 40), r.randint(-3, 45)]


def v_closest(tests):
    for t in tests:
        arr, target = t["args"]
        _chk_tree(arr, 1, 5000, 100000)
        assert -100000 <= target <= 200000


CHECKS["bst-closest-value"] = (b_closest, g_closest, "exact")
VALIDATE["bst-closest-value"] = v_closest

p = add(
    id="bst-most-frequent-values", title="Most Frequent Values in a BST", diff="Easy", topic=TOPIC,
    fn="modeValuesInBst", params=[("tree", "int[]")], ret="int[]", cmp="exact",
    desc="<p>This binary search tree may contain <strong>duplicate</strong> values. For every node, all values in its left subtree are <em>less than or equal</em> to the node's value and all values in its right subtree are <em>greater than or equal</em> to it.</p>"
         "<p>Return every value that occurs the maximum number of times in the tree, sorted in ascending order. Try to avoid a hash map: the BST order already groups equal values together.</p>"
         + _ENC +
         "<p><strong>Example 1</strong></p><pre>tree = [1,-1,2,2]\nOutput: [2]\n1 occurs once and 2 occurs twice.</pre>"
         "<p><strong>Example 2</strong></p><pre>tree = [4,2,6,2,4,-1,6]\nOutput: [2,4,6]\nThe values in order are 2,2,4,4,6,6: three values tie with two occurrences each.</pre>",
    constraints=["1 &le; number of nodes &le; 5,000 (so tree.length &le; 9,999)", "0 &le; node value &le; 100,000; values may repeat; the tree satisfies the ordering rule above"],
    hints=["A hash map of counts, then picking all values with the largest count, solves it. What does the inorder sequence of a BST look like?",
           "In the inorder sequence equal values sit next to each other, so each value forms one run.",
           "Traverse inorder, track the length of the current run and the best run length so far. A longer run replaces the answer list; an equal-length run is appended to it."],
    editorial=["Because an inorder traversal of such a tree is non-decreasing, all copies of a value appear consecutively. Walk the tree inorder (with an explicit stack to avoid deep recursion) and maintain the current value, the length of its run, the best run length seen so far and the list of values that reached it.",
               "When a run becomes longer than the best length, reset the list to just this value. When it becomes exactly as long, append the value. Since each run grows one step at a time, a value is appended at most once, and the list comes out already sorted. Time is O(n); extra memory is O(h) for the stack, plus the answer."],
    time="O(n)", space="O(h)",
    solution=_PARSE + '''def modeValuesInBst(tree):
    val, left, right = parse(tree)
    best, modes = 0, []
    cur, run = -1, 0
    stack = []
    u = 0
    while stack or u != -1:
        while u != -1:
            stack.append(u)
            u = left[u]
        u = stack.pop()
        x = val[u]
        if x == cur:
            run += 1
        else:
            cur, run = x, 1
        if run > best:
            best, modes = run, [x]
        elif run == best:
            modes.append(x)
        u = right[u]
    return modes
''',
    tests=[[[1, -1, 2, 2]], [[4, 2, 6, 2, 4, -1, 6]], [[7]], [[3, 3]], [[3, -1, 3]], [[2, 1, 3]], [[5, 5, 5, 5, 5, 5, 5]],
           [[10, 5, 15, 5, 7, 15, 15]], [[0, -1, 0, -1, 0, -1, 1]], [[6, 4, 9, 4, 6, 6, 9, 3, -1, -1, 6]]],
)
_r = rnd(7003)
for _n, _hi in ((2500, 400), (2500, 30), (1500, 100000)):
    _t = _bst_from([_r.randint(0, _hi) for _ in range(_n)], _r)
    p["tests"].append([_ser(_t)])
_t = _bst_from(sorted(_r.randint(0, 50) for _ in range(1200)), _r)
p["tests"].append([_ser(_t)])
_t = _bst_from(sorted((_r.randint(0, 3000) for _ in range(1400)), reverse=True), _r)
p["tests"].append([_ser(_t)])


def b_mode(tree):
    c = Counter(_vals(tree))
    m = max(c.values())
    return sorted(v for v in c if c[v] == m)


def g_mode(r):
    n = r.randint(1, 10)
    return [_ser(_bst_from([r.randint(0, 5) for _ in range(n)], r))]


def v_mode(tests):
    for t in tests:
        _chk_tree(t["args"][0], 1, 5000, 100000, distinct=False)
        assert t["expected"] == sorted(t["expected"])


CHECKS["bst-most-frequent-values"] = (b_mode, g_mode, "exact")
VALIDATE["bst-most-frequent-values"] = v_mode

# =================================================================== MEDIUM

p = add(
    id="bst-merge-two-trees-sorted", title="All Values of Two BSTs in Order", diff="Medium", topic=TOPIC,
    fn="mergeTwoBsts", params=[("tree1", "int[]"), ("tree2", "int[]")], ret="int[]", cmp="exact",
    desc="<p>You are given two binary search trees, <code>tree1</code> and <code>tree2</code>. Return an array containing the values of <strong>both</strong> trees in ascending order. A value that appears in both trees must appear twice in the result.</p>"
         "<p>Inside one tree all values are distinct. Either tree may be empty. Aim for O(n + m) time without sorting the combined values.</p>"
         + _ENC +
         "<p><strong>Example 1</strong></p><pre>tree1 = [4,2,6], tree2 = [5,1,7,-1,2]\nOutput: [1,2,2,4,5,6,7]\ntree1 holds 2, 4, 6 and tree2 holds 1, 2, 5, 7.</pre>"
         "<p><strong>Example 2</strong></p><pre>tree1 = [], tree2 = [3,1]\nOutput: [1,3]</pre>",
    constraints=["0 &le; number of nodes in each tree &le; 3,000", "0 &le; node value &le; 100,000; values are distinct within each tree; both trees are valid BSTs", "The two trees together have at least one node"],
    hints=["Putting both value lists together and sorting gives the answer in O((n + m) log(n + m)). Can you use the fact that each tree is already ordered?",
           "An inorder traversal turns each tree into a sorted list.",
           "Merge the two sorted lists with two pointers, always taking the smaller front element; on a tie take either (they are equal)."],
    editorial=["Each inorder traversal produces an ascending list in O(size) time, so the problem is the classic merge of two sorted lists. Keep one pointer in each list and repeatedly append the smaller front value, then append whatever remains of the other list.",
               "The total cost is O(n + m) time and O(n + m) space for the lists and the result. If memory mattered, you could run both inorder traversals lazily with two stacks (one iterator per tree) and merge on the fly, which needs only O(h1 + h2) extra space beyond the output."],
    time="O(n + m)", space="O(n + m)",
    solution=_PARSE + '''def inorder(tree):
    if not tree:
        return []
    val, left, right = parse(tree)
    out, stack, u = [], [], 0
    while stack or u != -1:
        while u != -1:
            stack.append(u)
            u = left[u]
        u = stack.pop()
        out.append(val[u])
        u = right[u]
    return out


def mergeTwoBsts(tree1, tree2):
    a, b = inorder(tree1), inorder(tree2)
    i = j = 0
    out = []
    while i < len(a) and j < len(b):
        if a[i] <= b[j]:
            out.append(a[i])
            i += 1
        else:
            out.append(b[j])
            j += 1
    out.extend(a[i:])
    out.extend(b[j:])
    return out
''',
    tests=[[[4, 2, 6], [5, 1, 7, -1, 2]], [[], [3, 1]], [[3, 1], []], [[5], [5]], [[2, 1, 3], [20, 10, 30]], [[20, 10, 30], [2, 1, 3]],
           [[1, -1, 2, -1, 3], [3, 2, -1, 1]], [[0], [100000]], [[10, 5, 15, 3, 7, 12, 18], [10, 5, 15, 3, 7, 12, 18]], [[8, 3, 10, 1, 6, -1, 14], [7, 2, 9, 1, 4]]],
)
_r = rnd(7004)
p["tests"].append([_rand_arr(_r, 1300, 5000), _rand_arr(_r, 1300, 5000)])
p["tests"].append([_chain_arr(_r, 900, 100000), _chain_arr(_r, 900, 100000, rev=True)])
p["tests"].append([_bal_arr(_r, 1023, 2000), []])


def b_merge(t1, t2):
    return sorted(_vals(t1) + _vals(t2))


def g_merge(r):
    while True:
        a, b = _rand_arr(r, r.randint(0, 8), 25), _rand_arr(r, r.randint(0, 8), 25)
        if a or b:
            return [a, b]


def v_merge(tests):
    for t in tests:
        for arr in t["args"]:
            _chk_tree(arr, 0, 3000, 100000)
        assert t["args"][0] or t["args"][1]


CHECKS["bst-merge-two-trees-sorted"] = (b_merge, g_merge, "exact")
VALIDATE["bst-merge-two-trees-sorted"] = v_merge

p = add(
    id="bst-greater-sum-tree", title="Replace Values With Sum of Greater-or-Equal Values", diff="Medium", topic=TOPIC,
    fn="greaterSumTree", params=[("tree", "int[]")], ret="int[]", cmp="exact",
    desc="<p>Given a binary search tree, replace the value of every node with the sum of all values in the tree that are <strong>greater than or equal</strong> to that node's original value. The shape of the tree does not change.</p>"
         "<p>Return the new tree in the same level-order encoding. The answer is unique: <code>-1</code> entries stay exactly where they were. The tree may be empty.</p>"
         + _ENC +
         "<p><strong>Example 1</strong></p><pre>tree = [4,2,6,1,3]\nOutput: [10,15,6,16,13]\nThe values are 1, 2, 3, 4, 6. For 4 the sum of values &ge; 4 is 4 + 6 = 10, for 2 it is 2 + 3 + 4 + 6 = 15, and so on.</pre>"
         "<p><strong>Example 2</strong></p><pre>tree = [5]\nOutput: [5]</pre>",
    constraints=["0 &le; number of nodes &le; 3,000 (so tree.length &le; 5,999)", "0 &le; node value &le; 100,000, all values distinct; the tree is a valid BST"],
    hints=["For every node you could sum all larger values: that is O(n&sup2;). Is there a running total that avoids repeating work?",
           "Visit the nodes from the largest value to the smallest. What is the answer for the largest node? And for the next one?",
           "Do a reverse inorder walk (right, node, left) with a running sum: add the node's value to the sum, and store the sum as the node's new value."],
    editorial=["Order the nodes by decreasing value. The new value of a node is the new value of the previous (next larger) node plus the node's own value, and the largest node keeps its own value. This is a suffix sum over the sorted values.",
               "A reverse inorder traversal visits the nodes in exactly that order, so keep one running total while walking right, node, left. Because the tree keeps its shape and the nodes appear in the array in level order, the answer is the original array with each non-<code>-1</code> entry replaced. Time O(n), extra memory O(h)."],
    time="O(n)", space="O(h)",
    solution=_PARSE + '''def greaterSumTree(tree):
    if not tree:
        return []
    val, left, right = parse(tree)
    new = list(val)
    total = 0
    stack = []
    u = 0
    while stack or u != -1:
        while u != -1:
            stack.append(u)
            u = right[u]
        u = stack.pop()
        total += val[u]
        new[u] = total
        u = left[u]
    # nodes are numbered in array order, so write the new values back in that order
    out, k = [], 0
    for x in tree:
        if x == -1:
            out.append(-1)
        else:
            out.append(new[k])
            k += 1
    return out
''',
    tests=[[[4, 2, 6, 1, 3]], [[5]], [[]], [[0]], [[2, 1, 3]], [[1, -1, 2, -1, 3, -1, 4]], [[4, 3, -1, 2, -1, 1]],
           [[10, 5, 15, 3, 7, 12, 18]], [[0, -1, 100000]], [[7, 3, 9, 1, 5, 8]]],
)
_r = rnd(7005)
p["tests"].append([_rand_arr(_r, 2500, 100000)])
p["tests"].append([_chain_arr(_r, 1200, 100000)])
p["tests"].append([_bal_arr(_r, 1023, 100000)])


def b_gst(tree):
    vals = _vals(tree)
    return [-1 if x == -1 else sum(y for y in vals if y >= x) for x in tree]


def g_gst(r):
    return [_rand_arr(r, r.randint(0, 10), 30)]


def v_gst(tests):
    for t in tests:
        _chk_tree(t["args"][0], 0, 3000, 100000)
        assert len(t["expected"]) == len(t["args"][0])


CHECKS["bst-greater-sum-tree"] = (b_gst, g_gst, "exact")
VALIDATE["bst-greater-sum-tree"] = v_gst

p = add(
    id="bst-iterator-ops", title="BST Iterator", diff="Medium", topic=TOPIC, tier="must",
    fn="bstIteratorOps", params=[("tree", "int[]"), ("ops", "int[]")], ret="int[]", cmp="exact",
    desc="<p>Design an iterator over a binary search tree that walks the values in <strong>ascending</strong> order. It supports two operations:</p>"
         "<ul><li><code>next()</code> (code <code>0</code>) returns the next smallest value that has not been returned yet.</li>"
         "<li><code>hasNext()</code> (code <code>1</code>) tells whether any value is left: <code>1</code> if yes, <code>0</code> if not.</li></ul>"
         "<p>You receive the tree and a list <code>ops</code> of operation codes. Perform them in order and return one number per operation: the returned value for <code>next</code>, and <code>1</code> or <code>0</code> for <code>hasNext</code>. A <code>next</code> call is only made when a value is left.</p>"
         "<p>The intended solution uses only O(h) extra memory (h is the tree height) and O(1) amortized time per call, so it must not copy the whole tree into an array first.</p>"
         + _ENC +
         "<p><strong>Example</strong></p><pre>tree = [7,3,15,-1,-1,9,20], ops = [1,0,0,0,1,0,0,1,1]\nOutput: [1,3,7,9,1,15,20,0,0]\nThe values in order are 3, 7, 9, 15, 20.</pre>",
    constraints=["1 &le; number of nodes &le; 5,000 (so tree.length &le; 9,999)", "0 &le; node value &le; 100,000, all values distinct; the tree is a valid BST", "1 &le; ops.length &le; 10,000; every op is 0 or 1, and op 0 is never issued when no value is left"],
    hints=["Flattening the tree into a sorted array and keeping an index is easy, but costs O(n) memory. What is the smallest part of the tree you have to remember?",
           "Keep a stack holding the path to the next value: the current leftmost node and its ancestors that are still waiting.",
           "On <code>next</code>, pop the top node (that is the answer), then push the left spine of its right child. <code>hasNext</code> is simply 'is the stack non-empty'."],
    editorial=["Simulate an inorder traversal that is paused after every value. The stack always contains the nodes whose own value and right subtree are still unvisited, topmost first. Initially push the left spine from the root, so the top is the minimum.",
               "<code>next</code> pops the top node, which is the smallest unreturned value, and then pushes the left spine of that node's right child so that the new top is the following value. Each node is pushed and popped once, which gives O(1) amortized time per call, while the stack never holds more than h nodes. <code>hasNext</code> checks whether the stack is empty."],
    time="O(1) amortized per op", space="O(h)",
    solution=_PARSE + '''def bstIteratorOps(tree, ops):
    val, left, right = parse(tree)
    stack = []
    u = 0
    while u != -1:
        stack.append(u)
        u = left[u]
    out = []
    for op in ops:
        if op == 0:
            u = stack.pop()
            out.append(val[u])
            v = right[u]
            while v != -1:
                stack.append(v)
                v = left[v]
        else:
            out.append(1 if stack else 0)
    return out
''',
    tests=[[[7, 3, 15, -1, -1, 9, 20], [1, 0, 0, 0, 1, 0, 0, 1, 1]], [[5], [0, 1]], [[5], [1, 1, 0, 1]], [[2, 1, 3], [0, 0, 0, 1]],
           [[1, -1, 2, -1, 3, -1, 4], [0, 0, 1, 0, 0, 1]], [[4, 3, -1, 2, -1, 1], [1, 0, 0, 1, 0, 0, 1]], [[8, 4, 12, 2, 6, 10, 14], [1, 1, 1]]],
)


def _iter_ops(r, n, q, p_next):
    ops, rem = [], n
    for _ in range(q):
        if rem > 0 and r.random() < p_next:
            ops.append(0)
            rem -= 1
        else:
            ops.append(1)
    return ops


_r = rnd(7006)
_a = _rand_arr(_r, 2500, 100000)
p["tests"].append([_a, [0] * 2500 + [1]])
p["tests"].append([_a, _iter_ops(_r, 2500, 4000, 0.7)])
p["tests"].append([_chain_arr(_r, 900, 100000), _iter_ops(_r, 900, 1800, 0.5)])
p["tests"].append([_chain_arr(_r, 900, 100000, rev=True), _iter_ops(_r, 900, 1500, 0.8)])
p["tests"].append([_bal_arr(_r, 1023, 100000), [1] + [0, 1] * 1023])


def b_iter(tree, ops):
    s = sorted(_vals(tree))
    i = 0
    out = []
    for op in ops:
        if op == 0:
            out.append(s[i])
            i += 1
        else:
            out.append(1 if i < len(s) else 0)
    return out


def g_iter(r):
    n = r.randint(1, 8)
    return [_rand_arr(r, n, 25), _iter_ops(r, n, r.randint(1, 14), 0.6)]


def v_iter(tests):
    for t in tests:
        arr, ops = t["args"]
        _chk_tree(arr, 1, 5000, 100000)
        assert 1 <= len(ops) <= 10000 and all(o in (0, 1) for o in ops)
        rem = len(_vals(arr))
        for o in ops:
            if o == 0:
                assert rem > 0, "next() with nothing left"
                rem -= 1


CHECKS["bst-iterator-ops"] = (b_iter, g_iter, "exact")
VALIDATE["bst-iterator-ops"] = v_iter

p = add(
    id="bst-two-trees-pair-count", title="Pairs Across Two BSTs With Given Sum", diff="Medium", topic=TOPIC,
    fn="countPairsAcrossBsts", params=[("tree1", "int[]"), ("tree2", "int[]"), ("target", "int")], ret="int", cmp="exact",
    desc="<p>You are given two binary search trees and an integer <code>target</code>. Count the pairs <code>(a, b)</code> such that <code>a</code> is a value from the first tree, <code>b</code> is a value from the second tree and <code>a + b = target</code>.</p>"
         "<p>Values are distinct inside each tree, but the same number may occur in both trees. Either tree may be empty.</p>"
         + _ENC +
         "<p><strong>Example 1</strong></p><pre>tree1 = [4,2,6], tree2 = [5,1,7,-1,2], target = 9\nOutput: 2\ntree1 holds 2, 4, 6 and tree2 holds 1, 2, 5, 7. The pairs are 2 + 7 and 4 + 5.</pre>"
         "<p><strong>Example 2</strong></p><pre>tree1 = [4,2,6], tree2 = [5,1,7,-1,2], target = 100\nOutput: 0</pre>",
    constraints=["0 &le; number of nodes in each tree &le; 3,000", "0 &le; node value &le; 100,000; values are distinct within each tree; both trees are valid BSTs", "0 &le; target &le; 200,000"],
    hints=["Testing all pairs is O(n &middot; m). A hash set of one tree's values plus a lookup for each value of the other brings it to O(n + m).",
           "Inorder gives each tree as an ascending list. How do you find pairs summing to a target using one ascending list and one descending list?",
           "Put one pointer at the smallest value of tree1 and one at the largest value of tree2. If the sum is too small advance the first pointer, if too large move the second back, and on equality count it and move both."],
    editorial=["Turn both trees into ascending lists with inorder traversals. Then run the two-pointer technique with the first pointer scanning list A from the smallest value and the second scanning list B from the largest. If <code>A[i] + B[j]</code> is smaller than the target, no pair with <code>A[i]</code> and anything at or below <code>B[j]</code> can work, so <code>i</code> moves up; if it is larger, <code>B[j]</code> is too big for every remaining value of A, so <code>j</code> moves down.",
               "Because values are distinct inside each list, a matching pair is used exactly once: count it and move both pointers. The scan is O(n + m). With two lazy iterators (one ascending over tree1, one descending over tree2) the same idea needs only O(h1 + h2) memory. A hash set over one tree is an equally valid O(n + m) alternative."],
    time="O(n + m)", space="O(n + m)",
    solution=_PARSE + '''def inorder(tree):
    if not tree:
        return []
    val, left, right = parse(tree)
    out, stack, u = [], [], 0
    while stack or u != -1:
        while u != -1:
            stack.append(u)
            u = left[u]
        u = stack.pop()
        out.append(val[u])
        u = right[u]
    return out


def countPairsAcrossBsts(tree1, tree2, target):
    a, b = inorder(tree1), inorder(tree2)
    i, j = 0, len(b) - 1
    count = 0
    while i < len(a) and j >= 0:
        s = a[i] + b[j]
        if s == target:
            count += 1
            i += 1
            j -= 1
        elif s < target:
            i += 1
        else:
            j -= 1
    return count
''',
    tests=[[[4, 2, 6], [5, 1, 7, -1, 2], 9], [[4, 2, 6], [5, 1, 7, -1, 2], 100], [[], [3, 1], 4], [[3, 1], [], 4], [[5], [5], 10], [[5], [5], 9],
           [[2, 1, 3], [20, 10, 30], 23], [[0, -1, 100000], [100000, 0], 100000], [[0, -1, 100000], [100000, 0], 200000],
           [[8, 3, 10, 1, 6, -1, 14], [7, 2, 9, 1, 4], 11], [[1, -1, 2, -1, 3, -1, 4], [4, 3, -1, 2, -1, 1], 5]],
)
_r = rnd(7007)
_A = _r.sample(range(0, 60001), 1500)
_B = [50000 - x for x in _r.sample(_A, 700)] + _r.sample(range(0, 60001), 600)
_B = sorted(set(v for v in _B if 0 <= v <= 100000))
_r.shuffle(_B)
p["tests"].append([_ser(_bst_from(_A)), _ser(_bst_from(_B)), 50000])
_A = sorted(_r.sample(range(0, 100001), 1000))
_B = sorted(_r.sample(range(0, 100001), 1000))
p["tests"].append([_ser(_balanced(_A)), _ser(_balanced(_B)), _A[300] + _B[400]])
_A = sorted(_r.sample(range(0, 50001), 1000))
p["tests"].append([_ser(_bst_from(_A)), _ser(_bst_from(_A[::-1])), 50000])


def b_pairs(t1, t2, target):
    return sum(1 for a in _vals(t1) for b in _vals(t2) if a + b == target)


def g_pairs(r):
    return [_rand_arr(r, r.randint(0, 8), 20), _rand_arr(r, r.randint(0, 8), 20), r.randint(0, 40)]


def v_pairs(tests):
    for t in tests:
        a, b, target = t["args"]
        _chk_tree(a, 0, 3000, 100000)
        _chk_tree(b, 0, 3000, 100000)
        assert 0 <= target <= 200000
    assert any(t["expected"] > 100 for t in tests), "need a case with many pairs"


CHECKS["bst-two-trees-pair-count"] = (b_pairs, g_pairs, "exact")
VALIDATE["bst-two-trees-pair-count"] = v_pairs

p = add(
    id="bst-k-closest-values", title="K Closest Values in a BST", diff="Medium", topic=TOPIC,
    fn="kClosestInBst", params=[("tree", "int[]"), ("target", "int"), ("k", "int")], ret="int[]", cmp="exact",
    desc="<p>Given a binary search tree, an integer <code>target</code> and an integer <code>k</code>, find the <code>k</code> values in the tree that are closest to <code>target</code>, where the distance of a value <code>x</code> is <code>|x - target|</code>. If two values are equally close, the <strong>smaller</strong> value counts as closer.</p>"
         "<p>Return the chosen values sorted in ascending order. The target does not have to be in the tree.</p>"
         + _ENC +
         "<p><strong>Example 1</strong></p><pre>tree = [8,4,12,2,6,10,14], target = 9, k = 3\nOutput: [6,8,10]\n8 and 10 are at distance 1; 6 and 12 are both at distance 3 and 6 is smaller.</pre>"
         "<p><strong>Example 2</strong></p><pre>tree = [8,4,12,2,6,10,14], target = 100, k = 2\nOutput: [12,14]</pre>",
    constraints=["1 &le; k &le; number of nodes &le; 5,000 (so tree.length &le; 9,999)", "0 &le; node value &le; 100,000, all values distinct; the tree is a valid BST", "-100,000 &le; target &le; 200,000"],
    hints=["Sorting all values by (distance, value) and taking the first k works in O(n log n). What does the answer look like inside the sorted order of the values?",
           "The k closest values always form one contiguous block of the inorder (ascending) sequence, and that block contains or touches the position where the target would be inserted.",
           "Build the ascending list, locate the target's position, and expand a window outwards k times, each time taking the left or the right neighbour whichever is closer (the left one on a tie)."],
    editorial=["Let the ascending inorder list be <code>v</code>. Closeness is unimodal around the target, so the k closest values are a contiguous window of <code>v</code>. Find the first index whose value is not below the target by binary search, set <code>lo</code> just before it and <code>hi</code> at it, then take k values: compare the candidates <code>v[lo]</code> and <code>v[hi]</code> by the pair (distance, value) and move the pointer of the winner outwards.",
               "Since all values are distinct and the left candidate is smaller than the right one, the tie-break always favours the left neighbour, which makes the answer unique. The window ends up as <code>v[lo+1:hi]</code>, already sorted. Building the list costs O(n); the expansion costs O(k). With two stack-based iterators (predecessors and successors of the target) this drops to O(h + k)."],
    time="O(n)", space="O(n)",
    solution=_PARSE + '''from bisect import bisect_left


def kClosestInBst(tree, target, k):
    val, left, right = parse(tree)
    v, stack, u = [], [], 0
    while stack or u != -1:
        while u != -1:
            stack.append(u)
            u = left[u]
        u = stack.pop()
        v.append(val[u])
        u = right[u]
    hi = bisect_left(v, target)
    lo = hi - 1
    for _ in range(k):
        if lo < 0:
            hi += 1
        elif hi >= len(v):
            lo -= 1
        elif (target - v[lo], v[lo]) <= (v[hi] - target, v[hi]):
            lo -= 1
        else:
            hi += 1
    return v[lo + 1:hi]
''',
    tests=[[[8, 4, 12, 2, 6, 10, 14], 9, 3], [[8, 4, 12, 2, 6, 10, 14], 100, 2], [[8, 4, 12, 2, 6, 10, 14], -5, 3], [[5], 5, 1], [[5], 90000, 1],
           [[8, 4, 12, 2, 6, 10, 14], 8, 7], [[8, 4, 12, 2, 6, 10, 14], 8, 4], [[8, 4, 12, 2, 6, 10, 14], 9, 1], [[8, 4, 12, 2, 6, 10, 14], 11, 2],
           [[1, -1, 3, -1, 5, -1, 7], 4, 2], [[7, 5, -1, 3, -1, 1], 2, 3], [[100000, 0], 50000, 1]],
)
_r = rnd(7008)
_a = _rand_arr(_r, 3000, 100000)
p["tests"] += [[_a, 40000, 1000], [_a, -50000, 5]]
p["tests"].append([_chain_arr(_r, 1500, 100000), 66666, 800])
p["tests"].append([_bal_arr(_r, 2047, 100000), 99999, 2047])


def b_kclose(tree, target, k):
    return sorted(sorted(_vals(tree), key=lambda v: (abs(v - target), v))[:k])


def g_kclose(r):
    n = r.randint(1, 10)
    return [_rand_arr(r, n, 30), r.randint(-4, 34), r.randint(1, n)]


def v_kclose(tests):
    for t in tests:
        arr, target, k = t["args"]
        _chk_tree(arr, 1, 5000, 100000)
        assert 1 <= k <= len(_vals(arr)) and -100000 <= target <= 200000


CHECKS["bst-k-closest-values"] = (b_kclose, g_kclose, "exact")
VALIDATE["bst-k-closest-values"] = v_kclose

p = add(
    id="bst-range-count-queries", title="Count Values in Ranges of a BST", diff="Medium", topic=TOPIC,
    fn="bstRangeCounts", params=[("tree", "int[]"), ("queries", "int[][]")], ret="int[]", cmp="exact",
    desc="<p>You are given a binary search tree and a list of queries. Each query is a pair <code>[lo, hi]</code>. For every query, count how many values <code>x</code> in the tree satisfy <code>lo &le; x &le; hi</code>, and return the counts in the order of the queries.</p>"
         "<p>There can be many queries, so a full traversal per query is too slow; answer each one in roughly O(h) time.</p>"
         + _ENC +
         "<p><strong>Example</strong></p><pre>tree = [8,4,12,2,6,10,14], queries = [[3,9],[0,100],[15,20],[8,8]]\nOutput: [3,7,0,1]\nThe values are 2, 4, 6, 8, 10, 12, 14. Between 3 and 9 there are 4, 6 and 8.</pre>",
    constraints=["1 &le; number of nodes &le; 5,000 (so tree.length &le; 9,999)", "0 &le; node value &le; 100,000, all values distinct; the tree is a valid BST", "1 &le; queries.length &le; 3,000; 0 &le; lo &le; hi &le; 100,000"],
    hints=["Walking the whole tree for every query costs O(n) each. The answer to a range query can be built from two simpler questions.",
           "Define rank(x) = how many values are strictly smaller than x. Then the answer is rank(hi + 1) - rank(lo).",
           "Store the subtree size at every node. To compute rank(x), descend from the root: when you go right at a node, add 1 + size of its left subtree; when you go left, add nothing."],
    editorial=["Compute the size of every subtree once. Nodes are numbered in level order, so processing them from the last to the first guarantees that both children are done before their parent. Then <code>rank(x)</code>, the count of values strictly below <code>x</code>, is found by a single root-to-leaf walk: at a node with value <code>v</code>, if <code>v &lt; x</code> then the node and its entire left subtree are smaller than <code>x</code>, so add <code>1 + size[left]</code> and go right; otherwise go left.",
               "A range <code>[lo, hi]</code> contains <code>rank(hi + 1) - rank(lo)</code> values (values are integers). Each query costs O(h), so the total is O(n + q &middot; h). Flattening the tree into a sorted array and using two binary searches is an equivalent alternative with O(n) memory."],
    time="O(n + q*h)", space="O(n)",
    solution=_PARSE + '''def bstRangeCounts(tree, queries):
    val, left, right = parse(tree)
    n = len(val)
    size = [1] * n
    for u in range(n - 1, -1, -1):
        for c in (left[u], right[u]):
            if c != -1:
                size[u] += size[c]

    def rank(x):  # number of values strictly smaller than x
        total, u = 0, 0
        while u != -1:
            if val[u] < x:
                total += 1 + (size[left[u]] if left[u] != -1 else 0)
                u = right[u]
            else:
                u = left[u]
        return total

    return [rank(hi + 1) - rank(lo) for lo, hi in queries]
''',
    tests=[[[8, 4, 12, 2, 6, 10, 14], [[3, 9], [0, 100], [15, 20], [8, 8]]], [[5], [[5, 5]]], [[5], [[0, 4], [6, 100000], [0, 100000]]],
           [[1, -1, 2, -1, 3, -1, 4], [[1, 1], [2, 3], [0, 0], [4, 100000], [3, 3]]], [[4, 3, -1, 2, -1, 1], [[0, 4], [1, 2], [2, 3], [5, 9]]],
           [[50, 20, 70, 10, 30, 60, 80], [[10, 80], [11, 79], [31, 59], [20, 70], [61, 69]]], [[0, -1, 100000], [[0, 100000], [1, 99999], [0, 0], [100000, 100000]]]],
)
_r = rnd(7009)


def _qs(r, q, hi, vals=None):
    out = []
    for _ in range(q):
        if vals and r.random() < 0.5:
            a, b = r.choice(vals), r.choice(vals)
        else:
            a, b = r.randint(0, hi), r.randint(0, hi)
        out.append([min(a, b), max(a, b)])
    return out


_v = _r.sample(range(100001), 3000)
p["tests"].append([_ser(_bst_from(_v)), _qs(_r, 1200, 100000, _v)])
_v = sorted(_r.sample(range(100001), 1500))
p["tests"].append([_ser(_balanced(_v)), _qs(_r, 800, 100000, _v) + [[0, 100000]]])
_v = _v[::3]
p["tests"].append([_ser(_bst_from(_v)), _qs(_r, 500, 100000, _v)])


def b_rangecnt(tree, queries):
    vals = _vals(tree)
    return [sum(1 for x in vals if lo <= x <= hi) for lo, hi in queries]


def g_rangecnt(r):
    qs = []
    for _ in range(r.randint(1, 6)):
        a, b = r.randint(0, 32), r.randint(0, 32)
        qs.append([min(a, b), max(a, b)])
    return [_rand_arr(r, r.randint(1, 10), 30), qs]


def v_rangecnt(tests):
    for t in tests:
        arr, qs = t["args"]
        _chk_tree(arr, 1, 5000, 100000)
        assert 1 <= len(qs) <= 3000 and all(0 <= lo <= hi <= 100000 for lo, hi in qs)


CHECKS["bst-range-count-queries"] = (b_rangecnt, g_rangecnt, "exact")
VALIDATE["bst-range-count-queries"] = v_rangecnt

# =================================================================== HARD

p = add(
    id="bst-order-statistic-ops", title="Dynamic Order Statistics on a BST", diff="Hard", topic=TOPIC, tier="extra",
    fn="orderStatisticOps", params=[("tree", "int[]"), ("ops", "int[][]")], ret="int[]", cmp="exact",
    desc="<p>You start with a set of distinct integers stored in a binary search tree (possibly empty), and then receive a list of operations <code>[type, x]</code> to apply in order:</p>"
         "<ul><li><code>[0, x]</code>: insert the value <code>x</code> into the set. It is not in the set yet.</li>"
         "<li><code>[1, x]</code>: delete the value <code>x</code> from the set. It is in the set.</li>"
         "<li><code>[2, x]</code>: query the <code>x</code>-th smallest value currently in the set (counting from 1). The set has at least <code>x</code> values.</li>"
         "<li><code>[3, x]</code>: query how many values currently in the set are strictly smaller than <code>x</code>.</li></ul>"
         "<p>Return the answers to the queries (types 2 and 3) in the order they were asked. Updates produce no output.</p>"
         "<p>The tree only describes the starting set; you may use any structure you like afterwards. A solution that walks the whole set for every query is too slow: aim for about O(log n) per operation.</p>"
         + _ENC +
         "<p><strong>Example</strong></p><pre>tree = [5,2,8], ops = [[2,2],[0,6],[3,7],[1,2],[2,2],[3,100]]\nOutput: [5,3,6,3]\nStart {2,5,8}: 2nd smallest is 5. Insert 6 gives {2,5,6,8}: values below 7 are 2, 5, 6 (3 of them). Delete 2 gives {5,6,8}: 2nd smallest is 6. Values below 100: 3.</pre>",
    constraints=["0 &le; initial number of nodes &le; 3,000; the tree is a valid BST with distinct values", "1 &le; ops.length &le; 6,000; at least one op is a query",
                 "0 &le; every value and every <code>x</code> in types 0, 1, 3 &le; 1,000,000", "Inserts never duplicate a value; deletes always remove an existing value; <code>x</code> in type 2 is within the current set size"],
    hints=["Keeping a sorted list and using binary search handles the queries, but each insert and delete shifts O(n) items. Can you make updates and order queries both logarithmic?",
           "Order statistics need counts. Think about a structure that stores, for ranges of values, how many members are present. All values appearing in the input are known in advance.",
           "Sort and deduplicate every value from the tree and from the inserts, and use a Fenwick tree (binary indexed tree) over that coordinate list with 1 for present and 0 for absent. rank = prefix sum; k-th smallest = binary descent on the Fenwick tree."],
    editorial=["The classic answer is a balanced BST augmented with subtree sizes, which gives O(log n) insert, delete, rank and k-th. An easier route when all values can be read in advance is offline coordinate compression: collect the initial values and every inserted value, sort them, and map each to an index. Then a Fenwick tree over these indices stores 1 for a present value and 0 otherwise.",
               "Insert and delete are point updates; <code>rank(x)</code> is a prefix sum over the indices of values smaller than <code>x</code> (use binary search to find the boundary index); the <code>x</code>-th smallest value is found by the Fenwick descent: starting from the highest power of two, step forward while the accumulated count stays below <code>x</code>. The next position is the answer's index. Total time O((n + q) log (n + q)), memory O(n + q)."],
    time="O((n + q) log (n + q))", space="O(n + q)",
    solution=_PARSE + '''from bisect import bisect_left


def orderStatisticOps(tree, ops):
    init = []
    if tree:
        init = parse(tree)[0]
    keys = sorted(set(init) | {x for t, x in ops if t == 0})
    m = len(keys)
    index = {v: i + 1 for i, v in enumerate(keys)}
    bit = [0] * (m + 1)

    def update(i, d):
        while i <= m:
            bit[i] += d
            i += i & -i

    def prefix(i):
        s = 0
        while i > 0:
            s += bit[i]
            i -= i & -i
        return s

    top = 1
    while top * 2 <= m:
        top *= 2
    for v in init:
        update(index[v], 1)
    out = []
    for t, x in ops:
        if t == 0:
            update(index[x], 1)
        elif t == 1:
            update(index[x], -1)
        elif t == 2:
            pos, step, need = 0, top, x
            while step:
                nxt = pos + step
                if nxt <= m and bit[nxt] < need:
                    pos = nxt
                    need -= bit[nxt]
                step >>= 1
            out.append(keys[pos])  # pos is 0-based index of the answer
        else:
            out.append(prefix(bisect_left(keys, x)))
    return out
''',
    tests=[[[5, 2, 8], [[2, 2], [0, 6], [3, 7], [1, 2], [2, 2], [3, 100]]], [[], [[0, 5], [2, 1], [3, 5], [3, 6]]], [[7], [[3, 7], [3, 8], [2, 1], [1, 7], [0, 3], [2, 1]]],
           [[2, 1, 3], [[1, 1], [1, 2], [1, 3], [0, 1000000], [2, 1], [3, 1000000]]], [[0, -1, 1000000], [[2, 1], [2, 2], [3, 0], [3, 1], [3, 1000000]]],
           [[4, 2, 6, 1, 3, 5, 7], [[3, 4], [1, 4], [3, 4], [2, 4], [0, 4], [2, 4], [0, 0], [2, 1], [3, 8]]]],
)


def _os_ops(r, init, q, hi):
    live = list(init)
    inset = set(init)
    ops = []
    for _ in range(q - 1):
        c = r.random()
        if c < 0.25:
            x = r.randint(0, hi)
            while x in inset:
                x = r.randint(0, hi)
            inset.add(x)
            live.append(x)
            ops.append([0, x])
        elif c < 0.45 and live:
            i = r.randrange(len(live))
            live[i], live[-1] = live[-1], live[i]
            x = live.pop()
            inset.discard(x)
            ops.append([1, x])
        elif c < 0.75 and live:
            ops.append([2, r.randint(1, len(live))])
        else:
            ops.append([3, r.randint(0, hi)])
    ops.append([3, r.randint(0, hi)])
    return ops


_r = rnd(7010)
_v = _r.sample(range(1000001), 2000)
p["tests"].append([_ser(_bst_from(_v)), _os_ops(_r, _v, 4000, 1000000)])
_v = _r.sample(range(1000001), 400)
p["tests"].append([_ser(_bst_from(_v)), _os_ops(_r, _v, 1500, 1000000)])
_v = _r.sample(range(1000001), 1500)
p["tests"].append([_ser(_balanced(sorted(_v))), _os_ops(_r, _v, 2000, 3000000 // 3)])
p["tests"].append([[], _os_ops(_r, [], 60, 200)])


def b_osops(tree, ops):
    s = set(_vals(tree))
    out = []
    for t, x in ops:
        if t == 0:
            s.add(x)
        elif t == 1:
            s.remove(x)
        elif t == 2:
            out.append(sorted(s)[x - 1])
        else:
            out.append(sum(1 for v in s if v < x))
    return out


def g_osops(r):
    init = r.sample(range(0, 41), r.randint(0, 8))
    return [_ser(_bst_from(init)), _os_ops(r, init, r.randint(1, 16), 40)]


def v_osops(tests):
    for t in tests:
        arr, ops = t["args"]
        _chk_tree(arr, 0, 3000, 1000000)
        assert 1 <= len(ops) <= 6000
        s = set(_vals(arr))
        queries = 0
        for ty, x in ops:
            assert 0 <= ty <= 3
            if ty == 0:
                assert 0 <= x <= 1000000 and x not in s
                s.add(x)
            elif ty == 1:
                assert x in s
                s.remove(x)
            elif ty == 2:
                assert 1 <= x <= len(s)
                queries += 1
            else:
                assert 0 <= x <= 1000000
                queries += 1
        assert queries >= 1
        assert len(t["expected"]) == queries


CHECKS["bst-order-statistic-ops"] = (b_osops, g_osops, "exact")
VALIDATE["bst-order-statistic-ops"] = v_osops

p = add(
    id="bst-subtree-median-sum", title="Sum of Subtree Medians in a BST", diff="Hard", topic=TOPIC, tier="extra",
    fn="subtreeMedianSum", params=[("tree", "int[]")], ret="int", cmp="exact",
    desc="<p>Every node of a binary search tree is the root of a subtree. The <strong>median</strong> of a subtree with <code>s</code> values is its <code>((s + 1) / 2)</code>-th smallest value, where the division rounds down (so for an even size the smaller of the two middle values is used).</p>"
         "<p>Return the sum of the medians of the subtrees rooted at <em>all</em> nodes of the tree. Every node counts once, including leaves, whose median is their own value.</p>"
         "<p>Sorting the values of every subtree separately is O(n&sup2; log n) on a path-shaped tree. Aim for O(n).</p>"
         + _ENC +
         "<p><strong>Example 1</strong></p><pre>tree = [4,2,6,1,3,5,7]\nOutput: 28\nLeaves 1, 3, 5, 7 give 16. Node 2 has {1,2,3} so 2, node 6 has {5,6,7} so 6, and the root has seven values with median 4. Total 16 + 2 + 6 + 4 = 28.</pre>"
         "<p><strong>Example 2</strong></p><pre>tree = [1,-1,2,-1,3]\nOutput: 7\nSubtree of 1 is {1,2,3} with median 2, subtree of 2 is {2,3} with median 2 (smaller middle value), subtree of 3 is {3}. Total 2 + 2 + 3 = 7.</pre>",
    constraints=["1 &le; number of nodes &le; 5,000 (so tree.length &le; 9,999)", "0 &le; node value &le; 100,000, all values distinct; the tree is a valid BST", "The sum always fits in a 32-bit integer"],
    hints=["For a small tree you can collect the values of each subtree, sort them and pick the median. What property of a BST makes the sorting unnecessary?",
           "Look at the inorder (ascending) sequence of the whole tree. Which part of it belongs to a given subtree?",
           "Every subtree occupies a contiguous block of the global inorder sequence, starting at (rank of the node) - (size of its left subtree) and of length equal to its size. Read the median straight from that block."],
    editorial=["In a BST the values of any subtree are consecutive in the inorder order of the whole tree. If a node has inorder position <code>pos</code> (0-based) and its left subtree has <code>L</code> nodes, then its subtree starts at <code>pos - L</code> and spans <code>s</code> positions. The median is therefore the element at index <code>pos - L + (s - 1) // 2</code> of the inorder array.",
               "So the algorithm computes the inorder array and each node's position once, computes the subtree sizes (children are processed before parents by iterating over the level-order numbering backwards), and adds one array lookup per node. The total is O(n) time and O(n) memory, with no sorting and no recursion."],
    time="O(n)", space="O(n)",
    solution=_PARSE + '''def subtreeMedianSum(tree):
    val, left, right = parse(tree)
    n = len(val)
    size = [1] * n
    for u in range(n - 1, -1, -1):
        for c in (left[u], right[u]):
            if c != -1:
                size[u] += size[c]
    order = []          # inorder sequence of node ids
    stack, u = [], 0
    while stack or u != -1:
        while u != -1:
            stack.append(u)
            u = left[u]
        u = stack.pop()
        order.append(u)
        u = right[u]
    seq = [val[u] for u in order]
    total = 0
    for pos, u in enumerate(order):
        lsize = size[left[u]] if left[u] != -1 else 0
        start = pos - lsize
        total += seq[start + (size[u] - 1) // 2]
    return total
''',
    tests=[[[4, 2, 6, 1, 3, 5, 7]], [[1, -1, 2, -1, 3]], [[9]], [[2, 1]], [[1, -1, 2]], [[3, 1, 4, -1, 2]], [[5, 3, 8, 2, 4, 7, 9, 1]],
           [[10, 4, -1, 2, 8, 1, 3, 6, 9]], [[0, -1, 100000]], [[3, 2, 4, 1]]],
)
_r = rnd(7011)
p["tests"].append([_rand_arr(_r, 4000, 100000)])
p["tests"].append([_chain_arr(_r, 2500, 100000)])
p["tests"].append([_chain_arr(_r, 2500, 100000, rev=True)])
p["tests"].append([_bal_arr(_r, 2047, 100000)])


def _brute_med(arr):
    root = _parse(arr)
    total = 0

    def collect(nd):
        if nd is None:
            return []
        return collect(nd[1]) + [nd[0]] + collect(nd[2])

    def walk(nd):
        nonlocal total
        if nd is None:
            return
        vs = sorted(collect(nd))
        total += vs[(len(vs) + 1) // 2 - 1]
        walk(nd[1])
        walk(nd[2])

    walk(root)
    return total


def g_submed(r):
    return [_rand_arr(r, r.randint(1, 12), 30)]


def v_submed(tests):
    for t in tests:
        _chk_tree(t["args"][0], 1, 5000, 100000)


CHECKS["bst-subtree-median-sum"] = (_brute_med, g_submed, "exact")
VALIDATE["bst-subtree-median-sum"] = v_submed
