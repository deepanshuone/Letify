"""Problems: binary search trees (search, floor/ceil, neighbours, delete, operations, validity). See data/lib.py for the registry.

Tree encoding used by every tree problem here: level-order int[], -1 for a missing child,
children of missing nodes are not listed, trailing -1s are dropped, [] is the empty tree.
"""
from lib import add, rnd, CHECKS, VALIDATE, gen_arr  # noqa: F401

TOPIC = "Binary Search Trees"
MAXN = 3000
MAXV = 100000

_ENC = (
    "<p><strong>Tree encoding.</strong> A binary tree is passed as an integer array in level order. "
    "The first entry is the root. After that, the left and right child of every existing node are written in turn, "
    "level by level, from left to right. A missing child is written as <code>-1</code> (node values are never negative, "
    "so <code>-1</code> cannot be confused with a value). Missing nodes have no children listed, and trailing "
    "<code>-1</code> entries are dropped. The empty tree is <code>[]</code>.</p>"
    "<p>For example, <code>[8,3,10,1,6,-1,14]</code> is the tree whose root <code>8</code> has children <code>3</code> and "
    "<code>10</code>; node <code>3</code> has children <code>1</code> and <code>6</code>; node <code>10</code> has no left child "
    "and right child <code>14</code>.</p>"
)

# The sample tree used in most examples: inorder 1 3 4 6 7 8 10 13 14
T0 = [8, 3, 10, 1, 6, -1, 14, -1, -1, 4, 7, 13]


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


def _fill_random(r, root, lo, hi):
    for nd in _nodes(root):
        nd[0] = r.randint(lo, hi)
    return root


def _mutate(r, root, k, hi):
    nodes = _nodes(root)
    for nd in r.sample(nodes, min(k, len(nodes))):
        nd[0] = r.randint(0, hi)
    return root


def _chk_tree(arr, nmin, nmax, vmax):
    assert all(isinstance(x, int) and -1 <= x <= vmax for x in arr), "bad entry"
    assert _ser(_parse(arr)) == arr, "tree array is not canonical"
    cnt = sum(1 for x in arr if x != -1)
    assert nmin <= cnt <= nmax, ("node count", cnt)


def _is_bst(arr):
    ino = _inorder(_parse(arr))
    return all(ino[i] < ino[i + 1] for i in range(len(ino) - 1))


def _chain(vals):
    """BST that is a path: insert the values in the given order."""
    return _bst_from(vals)


_BIG = [_ser(_rand_bst(rnd(900), 2400, MAXV))]  # shared big random BST (read only)


# =================================================================== EASY

p = add(
    id="bst-search-nodes-visited", title="Nodes Visited by a BST Search", diff="Easy", topic=TOPIC,
    fn="searchNodesVisited", params=[("tree", "int[]"), ("target", "int")], ret="int", cmp="exact",
    desc="<p>You are given a binary search tree with distinct values and an integer <code>target</code>. Run the standard BST search: start at the root; at every node, stop if its value equals <code>target</code>, go to the left child if <code>target</code> is smaller, and go to the right child if it is larger. The search also stops when it tries to move to a missing child.</p>"
         "<p>Return the number of <strong>nodes</strong> the search looked at (the node that matches counts, a missing child does not). The empty tree gives <code>0</code>.</p>"
         + _ENC +
         "<p><strong>Example 1</strong></p><pre>tree = [8,3,10,1,6,-1,14,-1,-1,4,7,13], target = 4\nOutput: 4\nThe search looks at 8, 3, 6 and 4.</pre>"
         "<p><strong>Example 2</strong></p><pre>tree = [8,3,10,1,6,-1,14,-1,-1,4,7,13], target = 20\nOutput: 3\nThe search looks at 8, 10 and 14, then 14 has no right child.</pre>"
         "<p><strong>Example 3</strong></p><pre>tree = [], target = 5\nOutput: 0</pre>",
    constraints=[f"0 &le; number of nodes &le; {MAXN:,}", f"0 &le; node value &le; {MAXV:,}, all values distinct; the tree is a valid BST", f"0 &le; target &le; {MAXV:,} (target may or may not be in the tree)"],
    hints=["Each comparison discards one whole side of the tree, so you never need to look at more than one root-to-leaf path.",
           "Keep a pointer to the current node and a counter. Increase the counter every time you step onto a real node.",
           "Loop while the current node exists: count it, stop if it equals the target, otherwise move to the left or right child. Remember the empty tree."],
    editorial=["A BST search follows a single path from the root. Decode the level-order array into explicit left and right child indices, then walk: count the current node, return the count if the value matches, otherwise move left when <code>target &lt; value</code> and right when it is larger. If the child you need is missing the walk ends and the count so far is the answer.",
               "The walk visits at most one node per level, so it costs O(h) after the O(n) decoding step (h is the height of the tree). The extra memory is the decoded child arrays, O(n)."],
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


def searchNodesVisited(tree, target):
    if not tree:
        return 0
    val, left, right = parse(tree)
    u = 0
    steps = 0
    while u != -1:
        steps += 1
        if val[u] == target:
            break
        u = left[u] if target < val[u] else right[u]
    return steps
''',
    tests=[[T0, 4], [T0, 20], [[], 5], [T0, 8], [T0, 1], [T0, 0], [T0, 5], [T0, 13], [T0, 100000], [[7], 7], [[7], 3], [[7], 9],
           [[1, -1, 2, -1, 3, -1, 4], 4], [[1, -1, 2, -1, 3, -1, 4], 0]],
)
_r = rnd(3101)
_vals = sorted(_inorder(_parse(_BIG[0])))
p["tests"] += [[_BIG[0], _r.choice(_vals)], [_BIG[0], _vals[-1] + 1 if _vals[-1] < MAXV else 0], [_BIG[0], _r.randint(0, MAXV)]]
_t = _ser(_chain(list(range(0, 1400))))
p["tests"].append([_t, 1399])
_t = _ser(_chain(list(range(1400, 0, -1))))
p["tests"].append([_t, 0])


def b_visited_fixed(tree, target):
    # interval view: node u is visited iff lo < target < hi where lo/hi are its nearest ancestors' values
    # (a node equal to the target is the last one visited, and its children are not).
    root = _parse(tree)
    if root is None:
        return 0
    count = 0
    stack = [(root, -1, 10 ** 9)]
    while stack:
        nd, lo, hi = stack.pop()
        if not (lo < target < hi):
            continue
        count += 1
        if nd[0] == target:
            continue
        if nd[1] is not None:
            stack.append((nd[1], lo, nd[0]))
        if nd[2] is not None:
            stack.append((nd[2], nd[0], hi))
    return count


def g_visited(r):
    n = r.randint(0, 9)
    t = _ser(_rand_bst(r, n, 20)) if n else []
    return [t, r.randint(0, 20)]


def v_visited(tests):
    for t in tests:
        arr, target = t["args"]
        _chk_tree(arr, 0, MAXN, MAXV)
        assert (not arr) or _is_bst(arr)
        assert 0 <= target <= MAXV
        assert 0 <= t["expected"] <= len(arr)
    ex = [t["expected"] for t in tests]
    assert 0 in ex and max(ex) >= 1000


CHECKS["bst-search-nodes-visited"] = (b_visited_fixed, g_visited, "exact")
VALIDATE["bst-search-nodes-visited"] = v_visited

p = add(
    id="bst-floor-ceil-query", title="Floor and Ceiling in a BST", diff="Easy", topic=TOPIC,
    fn="floorAndCeil", params=[("tree", "int[]"), ("x", "int")], ret="int[]", cmp="exact",
    desc="<p>Given a binary search tree with distinct values and an integer <code>x</code>, find</p>"
         "<ul><li>the <strong>floor</strong> of <code>x</code>: the largest value in the tree that is <code>&le; x</code>, and</li>"
         "<li>the <strong>ceiling</strong> of <code>x</code>: the smallest value in the tree that is <code>&ge; x</code>.</li></ul>"
         "<p>Return them as <code>[floor, ceiling]</code>. If one of them does not exist, write <code>-1</code> in its place. If <code>x</code> is in the tree, both are equal to <code>x</code>.</p>"
         + _ENC +
         "<p><strong>Example 1</strong></p><pre>tree = [8,3,10,1,6,-1,14,-1,-1,4,7,13], x = 5\nOutput: [4,6]</pre>"
         "<p><strong>Example 2</strong></p><pre>tree = [8,3,10,1,6,-1,14,-1,-1,4,7,13], x = 0\nOutput: [-1,1]\nNo value is &le; 0.</pre>"
         "<p><strong>Example 3</strong></p><pre>tree = [8,3,10,1,6,-1,14,-1,-1,4,7,13], x = 20\nOutput: [14,-1]</pre>",
    constraints=[f"0 &le; number of nodes &le; {MAXN:,}", f"0 &le; node value &le; {MAXV:,}, all values distinct; the tree is a valid BST", f"0 &le; x &le; {MAXV:,}"],
    hints=["The inorder sequence of a BST is sorted, so the floor and the ceiling are the neighbours of <code>x</code> in that sorted order. Can you find them without visiting every node?",
           "Walk down from the root as in a normal search. When the current value is smaller than <code>x</code> it is a floor candidate, and anything better can only be in its right subtree.",
           "Keep two variables, <code>floor</code> and <code>ceil</code>, both starting at -1. Value &lt; x: floor = value, go right. Value &gt; x: ceil = value, go left. Value == x: both are x. Stop at a missing child."],
    editorial=["Search for <code>x</code> from the root and remember the best candidates seen on the way. When the current value is smaller than <code>x</code>, it is a valid floor, and every better floor must be larger than it, hence in the right subtree: record it and go right. When the current value is larger, it is a valid ceiling and a better one can only be on the left: record it and go left. An exact match settles both answers at once.",
               "Every step is a plain BST search step, so the walk follows one root-to-leaf path: O(h) after the O(n) decoding of the array. Because values are never negative, -1 is a safe 'does not exist' marker."],
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


def floorAndCeil(tree, x):
    if not tree:
        return [-1, -1]
    val, left, right = parse(tree)
    floor_v = ceil_v = -1
    u = 0
    while u != -1:
        if val[u] == x:
            return [x, x]
        if val[u] < x:
            floor_v = val[u]
            u = right[u]
        else:
            ceil_v = val[u]
            u = left[u]
    return [floor_v, ceil_v]
''',
    tests=[[T0, 5], [T0, 0], [T0, 20], [[], 7], [T0, 8], [T0, 14], [T0, 1], [T0, 2], [T0, 9], [T0, 12], [[5], 5], [[5], 4], [[5], 6],
           [[2, 1, 3], 0], [[2, 1, 3], 100000]],
)
_r = rnd(3102)
_vals = _inorder(_parse(_BIG[0]))
_gaps = [x for x in range(1, MAXV) if x not in set(_vals)]
p["tests"] += [[_BIG[0], _r.choice(_gaps)], [_BIG[0], _vals[0]], [_BIG[0], _r.choice(_gaps)]]


def b_floorceil(tree, x):
    ino = _inorder(_parse(tree))
    lo = [v for v in ino if v <= x]
    hi = [v for v in ino if v >= x]
    return [max(lo) if lo else -1, min(hi) if hi else -1]


def g_floorceil(r):
    n = r.randint(0, 9)
    t = _ser(_rand_bst(r, n, 20)) if n else []
    return [t, r.randint(0, 20)]


def v_floorceil(tests):
    for t in tests:
        arr, x = t["args"]
        _chk_tree(arr, 0, MAXN, MAXV)
        assert (not arr) or _is_bst(arr)
        assert 0 <= x <= MAXV
    ex = [t["expected"] for t in tests]
    assert [-1, -1] in ex and any(e[0] == -1 and e[1] != -1 for e in ex) and any(e[1] == -1 and e[0] != -1 for e in ex)
    assert any(e[0] == e[1] != -1 for e in ex) and any(-1 != e[0] < e[1] for e in ex)


CHECKS["bst-floor-ceil-query"] = (b_floorceil, g_floorceil, "exact")
VALIDATE["bst-floor-ceil-query"] = v_floorceil


# =================================================================== MEDIUM

p = add(
    id="bst-lowest-common-ancestor", title="Lowest Common Ancestor in a BST", diff="Medium", topic=TOPIC, tier="must",
    fn="lowestCommonAncestor", params=[("tree", "int[]"), ("p", "int"), ("q", "int")], ret="int", cmp="exact",
    desc="<p>Given a binary search tree with distinct values and two values <code>p</code> and <code>q</code> that both occur in the tree, return the value of their <strong>lowest common ancestor</strong>: the deepest node that has both <code>p</code> and <code>q</code> in its subtree. A node counts as part of its own subtree, so if <code>p</code> is an ancestor of <code>q</code> the answer is <code>p</code>. It is allowed that <code>p == q</code>.</p>"
         + _ENC +
         "<p><strong>Example 1</strong></p><pre>tree = [8,3,10,1,6,-1,14,-1,-1,4,7,13], p = 4, q = 7\nOutput: 6</pre>"
         "<p><strong>Example 2</strong></p><pre>tree = [8,3,10,1,6,-1,14,-1,-1,4,7,13], p = 1, q = 13\nOutput: 8</pre>"
         "<p><strong>Example 3</strong></p><pre>tree = [8,3,10,1,6,-1,14,-1,-1,4,7,13], p = 3, q = 4\nOutput: 3\n3 is an ancestor of 4.</pre>",
    constraints=[f"1 &le; number of nodes &le; {MAXN:,}", f"0 &le; node value &le; {MAXV:,}, all values distinct; the tree is a valid BST", "p and q are values that occur in the tree (they may be equal)"],
    hints=["For a general binary tree you would have to search both subtrees. What extra information does the BST order give you at every node?",
           "Look at the current node <code>v</code>. If both <code>p</code> and <code>q</code> are smaller than <code>v</code>, they are both in the left subtree. What if both are larger?",
           "Start at the root. Move left while both targets are smaller, move right while both are larger. The first node where they split (or where it equals one of them) is the answer."],
    editorial=["Standing at a node <code>v</code>, the BST order tells you where each target is: smaller values are in the left subtree, larger ones in the right subtree. If both targets are smaller than <code>v</code> the lowest common ancestor is inside the left subtree, so move there. If both are larger, move right. Otherwise one target is on each side (or <code>v</code> is itself one of them), so <code>v</code> has both in its subtree while none of its children does: that is the lowest common ancestor.",
               "The walk goes down one path and never backtracks, so it takes O(h) time after decoding the array in O(n). No recursion is needed, which also avoids stack overflows on path-shaped trees."],
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


def lowestCommonAncestor(tree, p, q):
    val, left, right = parse(tree)
    u = 0
    while True:
        if p < val[u] and q < val[u]:
            u = left[u]
        elif p > val[u] and q > val[u]:
            u = right[u]
        else:
            return val[u]
''',
    tests=[[T0, 4, 7], [T0, 1, 13], [T0, 3, 4], [T0, 13, 13], [T0, 8, 14], [T0, 1, 7], [T0, 10, 13], [T0, 14, 10], [T0, 7, 1], [[5], 5, 5],
           [[5, 3], 3, 5], [[1, -1, 2, -1, 3, -1, 4], 3, 4]],
)
_r = rnd(3103)
_vals = _inorder(_parse(_BIG[0]))
p["tests"] += [[_BIG[0], _r.choice(_vals), _r.choice(_vals)] for _ in range(2)]
_v = list(range(1, 1500))
p["tests"].append([_ser(_chain(_v)), 1499, 1200])
_v2 = _r.sample(range(MAXV + 1), 1500)
_t = _bst_from(_v2)
p["tests"].append([_ser(_t), min(_v2), max(_v2)])


def b_lca(tree, p_, q_):
    root = _parse(tree)

    def path(target):
        # generic root-to-node path by DFS, without using the BST order
        stack = [(root, [root])]
        while stack:
            nd, pt = stack.pop()
            if nd[0] == target:
                return pt
            for s in (1, 2):
                if nd[s] is not None:
                    stack.append((nd[s], pt + [nd[s]]))

    a, b = path(p_), path(q_)
    k = 0
    while k < len(a) and k < len(b) and a[k] is b[k]:
        k += 1
    return a[k - 1][0]


def g_lca(r):
    n = r.randint(1, 10)
    vals = r.sample(range(0, 30), n)
    return [_ser(_bst_from(vals)), r.choice(vals), r.choice(vals)]


def v_lca(tests):
    for t in tests:
        arr, a, b = t["args"]
        _chk_tree(arr, 1, MAXN, MAXV)
        assert _is_bst(arr)
        ino = _inorder(_parse(arr))
        assert a in ino and b in ino
        assert t["expected"] in ino
    ex = [(t["args"][1], t["args"][2], t["expected"]) for t in tests]
    assert any(a == b == e for a, b, e in ex) and any(e in (a, b) and a != b for a, b, e in ex) and any(e not in (a, b) for a, b, e in ex)


CHECKS["bst-lowest-common-ancestor"] = (b_lca, g_lca, "exact")
VALIDATE["bst-lowest-common-ancestor"] = v_lca

_DELETE_RULE = ("<p><strong>Deletion rule.</strong> To delete a node: if it is a leaf, remove it; if it has exactly one child, replace the node by that child (the child's whole subtree moves up); "
                "if it has two children, copy into it the <em>smallest value of its right subtree</em> (its inorder successor) and then delete that smallest node from the right subtree, which by construction has at most one child. "
                "If the key is not in the tree nothing changes.</p>")

_DELETE_SOL = '''def parse(tree):
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


def dump(val, left, right, root):
    out = []
    queue = [root]
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
'''

p = add(
    id="bst-delete-node", title="Delete a Key from a BST", diff="Medium", topic=TOPIC, tier="must",
    fn="deleteFromBst", params=[("tree", "int[]"), ("key", "int")], ret="int[]", cmp="exact",
    desc="<p>Given a binary search tree with distinct values and an integer <code>key</code>, delete the node holding <code>key</code> (if there is one) and return the resulting tree in the same level-order encoding.</p>"
         + _DELETE_RULE +
         "<p>Following this rule exactly makes the resulting tree unique.</p>"
         + _ENC +
         "<p><strong>Example 1</strong></p><pre>tree = [8,3,10,1,6,-1,14,-1,-1,4,7,13], key = 3\nOutput: [8,4,10,1,6,-1,14,-1,-1,-1,7,13]\nNode 3 has two children. Its right subtree is rooted at 6 and its smallest value is 4, so 3 becomes 4 and the old node 4 (a leaf) is removed.</pre>"
         "<p><strong>Example 2</strong></p><pre>tree = [8,3,10,1,6,-1,14,-1,-1,4,7,13], key = 10\nOutput: [8,3,14,1,6,13,-1,-1,-1,4,7]\nNode 10 has only a right child, so 14 (with its subtree) takes its place.</pre>"
         "<p><strong>Example 3</strong></p><pre>tree = [8,3,10,1,6,-1,14,-1,-1,4,7,13], key = 99\nOutput: [8,3,10,1,6,-1,14,-1,-1,4,7,13]\nThe key is not present.</pre>",
    constraints=[f"0 &le; number of nodes &le; {MAXN:,}", f"0 &le; node value &le; {MAXV:,}, all values distinct; the tree is a valid BST", f"0 &le; key &le; {MAXV:,}"],
    hints=["Treat the three cases separately: no child, one child, two children. The first two only need a pointer change at the parent.",
           "When the node has two children you cannot simply drop it. Which value in the tree can take its place and still keep everything in the left subtree smaller and everything in the right subtree larger?",
           "Walk down while remembering the parent to find the key. For two children, walk left from the right child to the smallest node, copy its value up, and let its right child take its place. Finish with a breadth-first dump that writes -1 for missing children and removes trailing -1s."],
    editorial=["Find the node with a normal BST search, remembering its parent so a link can be redirected. A leaf is detached by clearing the parent's link (or by emptying the tree when it is the root). A node with one child is bypassed: the parent links straight to that child. A node with two children is the interesting case: the smallest node of its right subtree is larger than everything on the left and not larger than anything on the right, so its value can be copied into the node. That smallest node has no left child, so detaching it falls back to the one-child case.",
               "Finally serialise: a queue-based breadth-first walk writes each node's value and queues both children, with a placeholder for a missing child that prints as -1 and has no children of its own; trailing -1 entries are trimmed. Searching and fixing links is O(h); decoding and encoding the array make the total O(n) time and space."],
    time="O(n)", space="O(n)",
    solution=_DELETE_SOL + '''

def deleteFromBst(tree, key):
    if not tree:
        return []
    val, left, right = parse(tree)
    root = 0
    par = -1
    kids = None
    u = root
    while u != -1 and val[u] != key:
        par = u
        kids = left if key < val[u] else right
        u = kids[u]
    if u == -1:
        return list(tree)
    if left[u] == -1 or right[u] == -1:
        child = left[u] if left[u] != -1 else right[u]
        if par == -1:
            root = child
        else:
            kids[par] = child
    else:
        sp = u
        s = right[u]
        while left[s] != -1:
            sp = s
            s = left[s]
        val[u] = val[s]
        if sp == u:
            right[u] = right[s]
        else:
            left[sp] = right[s]
    return dump(val, left, right, root)
''',
    tests=[[T0, 3], [T0, 10], [T0, 99], [T0, 8], [T0, 1], [T0, 13], [T0, 6], [T0, 14], [[], 5], [[5], 5], [[5], 4], [[5, 3], 5], [[5, -1, 8], 5], [[5, 3, 8], 5],
           [[1, -1, 2, -1, 3, -1, 4], 1], [[1, -1, 2, -1, 3, -1, 4], 2], [[4, 2, 9, -1, -1, 6, 10, 5, 7], 4]],
)
_r = rnd(3104)
_vals = _inorder(_parse(_BIG[0]))
_t = _parse(_BIG[0])
p["tests"] += [[_BIG[0], _t[0]], [_BIG[0], _r.choice(_vals)]]
_t = _ser(_balanced(sorted(_r.sample(range(0, MAXV, 3), 2047))))
p["tests"].append([_t, _parse(_t)[0]])
_zig = []
_lo, _hi = 1000, 1700
while _lo <= _hi:
    _zig.append(_lo)
    _lo += 1
    if _lo <= _hi:
        _zig.append(_hi)
        _hi -= 1
p["tests"].append([_ser(_bst_from(_zig)), 1001])


def _nested_delete(nd, k):
    if nd is None:
        return None
    if k < nd[0]:
        nd[1] = _nested_delete(nd[1], k)
    elif k > nd[0]:
        nd[2] = _nested_delete(nd[2], k)
    else:
        if nd[1] is None:
            return nd[2]
        if nd[2] is None:
            return nd[1]
        m = nd[2]
        while m[1] is not None:
            m = m[1]
        nd[0] = m[0]
        nd[2] = _nested_delete(nd[2], m[0])
    return nd


def b_delete(tree, key):
    return _ser(_nested_delete(_parse(tree), key))


def g_delete(r):
    n = r.randint(0, 10)
    vals = r.sample(range(0, 25), n)
    key = r.choice(vals) if n and r.random() < 0.8 else r.randint(0, 24)
    return [_ser(_bst_from(vals)) if n else [], key]


def v_delete(tests):
    for t in tests:
        arr, key = t["args"]
        _chk_tree(arr, 0, MAXN, MAXV)
        assert (not arr) or _is_bst(arr)
        assert 0 <= key <= MAXV
        out = t["expected"]
        ino_in = _inorder(_parse(arr))
        ino_out = _inorder(_parse(out))
        assert ino_out == [v for v in ino_in if v != key]
    ex = [(t["args"], t["expected"]) for t in tests]
    assert any(a[1] not in _inorder(_parse(a[0])) for a, e in ex)
    assert any(e == [] for a, e in ex)


CHECKS["bst-delete-node"] = (b_delete, g_delete, "exact")
VALIDATE["bst-delete-node"] = v_delete

p = add(
    id="bst-apply-operations", title="Replay Inserts and Deletes on a BST", diff="Medium", topic=TOPIC,
    fn="applyOperations", params=[("tree", "int[]"), ("ops", "int[][]")], ret="int[]", cmp="exact",
    desc="<p>You start with a binary search tree with distinct values and apply a list of operations in order. Each operation is a pair <code>[type, value]</code>:</p>"
         "<ul><li><code>[1, v]</code>: <strong>insert</strong> <code>v</code> as a new leaf, found by the usual walk (go left if smaller, right if larger, attach at the first missing child). If <code>v</code> is already in the tree, do nothing.</li>"
         "<li><code>[2, v]</code>: <strong>delete</strong> <code>v</code>. If <code>v</code> is not in the tree, do nothing.</li></ul>"
         + _DELETE_RULE +
         "<p>Return the final tree in the level-order encoding. The rules make the shape of the tree unique.</p>"
         + _ENC +
         "<p><strong>Example 1</strong></p><pre>tree = [4,2,7,1,3], ops = [[1,5],[2,2],[2,4],[1,9]]\nOutput: [5,3,7,1,-1,-1,9]\nAfter inserting 5: 5 is the left child of 7. Deleting 2 (two children) copies its successor 3 up and removes the old 3. Deleting the root 4 copies the smallest value of its right subtree, 5, to the root and removes that leaf. Finally 9 becomes the right child of 7.</pre>"
         "<p><strong>Example 2</strong></p><pre>tree = [], ops = [[1,3],[1,1],[2,3],[2,8]]\nOutput: [1]\nAfter deleting the root 3 (one child) the node 1 becomes the root; deleting 8 does nothing.</pre>"
         "<p><strong>Example 3</strong></p><pre>tree = [2,1,3], ops = [[1,2],[2,1],[2,3],[2,2]]\nOutput: []</pre>",
    constraints=[f"0 &le; number of nodes in the initial tree &le; {MAXN:,}", f"0 &le; node value &le; {MAXV:,}, all values distinct; the tree is a valid BST", f"0 &le; ops.length &le; 3,000; each operation is [1, v] or [2, v] with 0 &le; v &le; {MAXV:,}", "The number of nodes never exceeds 6,000 during the process"],
    hints=["Each operation is one of the two classic BST routines. Write them once on a node-link representation instead of on the raw array.",
           "Decode the array into arrays <code>val</code>, <code>left</code>, <code>right</code> (index = position in level order). New nodes are appended, deleted nodes just become unreachable. Keep a variable for the root, because deleting the root can change it.",
           "For delete: find the node and its parent; with at most one child redirect the parent's link; with two children copy the minimum of the right subtree into the node and splice that minimum out. Encode the final tree with a breadth-first walk and trim trailing -1s."],
    editorial=["Keep the tree as three parallel arrays (value, left index, right index) with -1 for 'none' and a separate <code>root</code> variable. Insert walks down and attaches a new index at the first missing child (or becomes the root of an empty tree); a duplicate is detected when the walk meets an equal value. Delete finds the node while tracking the parent link, handles the zero/one-child cases by redirecting that link (or the root), and for two children copies the successor value and splices the successor node out of the right subtree.",
               "Every operation costs O(h). A path-shaped tree gives h up to n, so the worst case is O(n) per operation, which is fine for these limits. The final breadth-first dump is linear in the number of nodes."],
    time="O(n + m * h)", space="O(n + m)",
    solution=_DELETE_SOL + '''

def applyOperations(tree, ops):
    if tree:
        val, left, right = parse(tree)
        root = 0
    else:
        val, left, right = [], [], []
        root = -1
    for t, v in ops:
        if t == 1:
            if root == -1:
                val.append(v)
                left.append(-1)
                right.append(-1)
                root = len(val) - 1
                continue
            u = root
            while val[u] != v:
                kids = left if v < val[u] else right
                if kids[u] == -1:
                    val.append(v)
                    left.append(-1)
                    right.append(-1)
                    kids[u] = len(val) - 1
                    break
                u = kids[u]
        else:
            par = -1
            kids = None
            u = root
            while u != -1 and val[u] != v:
                par = u
                kids = left if v < val[u] else right
                u = kids[u]
            if u == -1:
                continue
            if left[u] == -1 or right[u] == -1:
                child = left[u] if left[u] != -1 else right[u]
                if par == -1:
                    root = child
                else:
                    kids[par] = child
            else:
                sp = u
                s = right[u]
                while left[s] != -1:
                    sp = s
                    s = left[s]
                val[u] = val[s]
                if sp == u:
                    right[u] = right[s]
                else:
                    left[sp] = right[s]
    if root == -1:
        return []
    return dump(val, left, right, root)
''',
    tests=[[[4, 2, 7, 1, 3], [[1, 5], [2, 2], [2, 4], [1, 9]]], [[], [[1, 3], [1, 1], [2, 3], [2, 8]]], [[2, 1, 3], [[1, 2], [2, 1], [2, 3], [2, 2]]],
           [[], []], [[7], []], [[7], [[2, 7]]], [[7], [[2, 7], [1, 7]]], [[4, 2, 7, 1, 3], [[2, 4], [2, 7], [2, 2], [2, 1], [2, 3]]],
           [T0, [[2, 8], [2, 10], [1, 9], [1, 11], [2, 3], [1, 0]]], [T0, [[1, 5], [1, 2], [1, 12], [2, 99], [1, 8]]],
           [[1, -1, 2, -1, 3], [[1, 0], [2, 2], [1, 5], [2, 1], [2, 0]]]],
)


def _gen_ops(r, present, count, hi, p_ins, p_noop=0.1):
    """Random mix of inserts and deletes; `present` is the set of values currently in the tree (updated)."""
    ops = []
    for _ in range(count):
        ins = r.random() < p_ins
        if ins:
            if present and r.random() < p_noop:
                v = r.choice(sorted(present)) if len(present) < 50 else next(iter(present))
            else:
                v = r.randint(0, hi)
                while v in present:
                    v = r.randint(0, hi)
            ops.append([1, v])
            present.add(v)
        else:
            if present and r.random() >= p_noop:
                v = r.choice(sorted(present)) if len(present) < 50 else next(iter(present))
            else:
                v = r.randint(0, hi)
            ops.append([2, v])
            present.discard(v)
    return ops


_r = rnd(3105)
_t = _rand_bst(_r, 900, MAXV)
_pres = set(_inorder(_t))
_ops = []
for _ in range(1200):  # random walks over existing values (deterministic choice via sorted list is slow, so sample lazily)
    if _r.random() < 0.5:
        _v = _r.randint(0, MAXV)
        _ops.append([1, _v])
        _pres.add(_v)
    else:
        if _r.random() < 0.85:
            _v = _r.choice(list(_pres))
        else:
            _v = _r.randint(0, MAXV)
        _ops.append([2, _v])
        _pres.discard(_v)
p["tests"].append([_ser(_t), _ops])
_t = _rand_bst(_r, 1100, MAXV)
_pres = set(_inorder(_t))
_ops = []
for _ in range(1100):  # deletes first, then refill
    _v = _r.choice(list(_pres)) if _pres else 0
    _ops.append([2, _v])
    _pres.discard(_v)
p["tests"].append([_ser(_t), _ops])
_v = _r.sample(range(MAXV + 1), 500)
_vs = sorted(_v)
_ops = [[2, x] for x in _vs[::2]] + [[1, x + 1] for x in _vs[1::3] if x + 1 not in set(_v)]
p["tests"].append([_ser(_bst_from(_vs)), _ops])  # sorted insertion = a path; ops walk it


def _nested_insert(nd, v):
    if nd is None:
        return _node(v)
    if v < nd[0]:
        nd[1] = _nested_insert(nd[1], v)
    elif v > nd[0]:
        nd[2] = _nested_insert(nd[2], v)
    return nd


def b_apply(tree, ops):
    root = _parse(tree)
    for t, v in ops:
        root = _nested_insert(root, v) if t == 1 else _nested_delete(root, v)
    return _ser(root) if root is not None else []


def g_apply(r):
    n = r.randint(0, 8)
    vals = r.sample(range(0, 20), n)
    present = set(vals)
    ops = _gen_ops(r, present, r.randint(0, 10), 19, 0.5, 0.2)
    return [_ser(_bst_from(vals)) if n else [], ops]


def v_apply(tests):
    for t in tests:
        arr, ops = t["args"]
        _chk_tree(arr, 0, MAXN, MAXV)
        assert (not arr) or _is_bst(arr)
        assert len(ops) <= 3000
        assert all(len(o) == 2 and o[0] in (1, 2) and 0 <= o[1] <= MAXV for o in ops)
        out = t["expected"]
        _chk_tree(out, 0, 6000, MAXV)
        assert (not out) or _is_bst(out)
        cur = set(_inorder(_parse(arr)))
        peak = len(cur)
        for k, v in ops:
            if k == 1:
                cur.add(v)
            else:
                cur.discard(v)
            peak = max(peak, len(cur))
        assert peak <= 6000
        assert sorted(cur) == _inorder(_parse(out))


CHECKS["bst-apply-operations"] = (b_apply, g_apply, "exact")
VALIDATE["bst-apply-operations"] = v_apply

p = add(
    id="bst-neighbors-of-queries", title="Strict Neighbours of Query Values", diff="Medium", topic=TOPIC,
    fn="strictNeighbors", params=[("tree", "int[]"), ("queries", "int[]")], ret="int[][]", cmp="exact",
    desc="<p>Given a binary search tree with distinct values and an array <code>queries</code>, answer every query <code>q</code> with the pair <code>[pred, succ]</code>:</p>"
         "<ul><li><code>pred</code> is the largest value in the tree that is <strong>strictly smaller</strong> than <code>q</code>,</li>"
         "<li><code>succ</code> is the smallest value in the tree that is <strong>strictly larger</strong> than <code>q</code>.</li></ul>"
         "<p>Use <code>-1</code> when no such value exists. A query may or may not be a value of the tree; if it is, this gives the inorder predecessor and inorder successor of that node. Return the pairs in query order.</p>"
         + _ENC +
         "<p><strong>Example 1</strong></p><pre>tree = [8,3,10,1,6,-1,14,-1,-1,4,7,13], queries = [5,8,0,14]\nOutput: [[4,6],[7,10],[-1,1],[13,-1]]</pre>"
         "<p><strong>Example 2</strong></p><pre>tree = [2,1,3], queries = [1,2,3]\nOutput: [[-1,2],[1,3],[2,-1]]</pre>"
         "<p><strong>Example 3</strong></p><pre>tree = [], queries = [4]\nOutput: [[-1,-1]]</pre>",
    constraints=[f"0 &le; number of nodes &le; {MAXN:,}", f"0 &le; node value &le; {MAXV:,}, all values distinct; the tree is a valid BST", f"1 &le; queries.length &le; 3,000; 0 &le; queries[i] &le; {MAXV:,}"],
    hints=["Walking the tree once per query works, but the tree can be a long path. Is there a representation of the tree where each query is a single quick lookup?",
           "The inorder traversal of a BST is a sorted array of its values. Neighbours of a query in the tree are neighbours in that array.",
           "Collect the inorder values (iteratively, with a stack). For each query use binary search: the first index with value &ge; q gives the predecessor just before it, and the first index with value &gt; q gives the successor."],
    editorial=["Do an inorder traversal to turn the BST into a sorted list <code>a</code>. For a query <code>q</code>, <code>bisect_left(a, q)</code> returns the first index whose value is <code>&ge; q</code>, so the element before it is the strict predecessor. <code>bisect_right(a, q)</code> returns the first index whose value is <code>&gt; q</code>, which is the strict successor. Missing neighbours become -1.",
               "Building the list costs O(n) and each query costs O(log n), so the total is O(n + k log n) for k queries. Walking down the tree per query would cost O(h) each, which degrades to O(n) per query on a path-shaped tree; the sorted list avoids that. The traversal uses an explicit stack, so deep trees are fine."],
    time="O(n + k log n)", space="O(n)",
    solution='''from bisect import bisect_left, bisect_right


def parse(tree):
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


def strictNeighbors(tree, queries):
    a = []
    if tree:
        val, left, right = parse(tree)
        stack = []
        u = 0
        while stack or u != -1:
            while u != -1:
                stack.append(u)
                u = left[u]
            u = stack.pop()
            a.append(val[u])
            u = right[u]
    out = []
    n = len(a)
    for q in queries:
        i = bisect_left(a, q)
        j = bisect_right(a, q)
        out.append([a[i - 1] if i > 0 else -1, a[j] if j < n else -1])
    return out
''',
    tests=[[T0, [5, 8, 0, 14]], [[2, 1, 3], [1, 2, 3]], [[], [4]], [T0, [100000]], [T0, [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]], [[9], [9, 8, 10]],
           [[1, -1, 2, -1, 3, -1, 4], [0, 1, 2, 3, 4, 5]], [[0], [0]], [[100000], [100000, 0]]],
)
_r = rnd(3106)
_vals = _inorder(_parse(_BIG[0]))
p["tests"] += [[_BIG[0], [_r.randint(0, MAXV) for _ in range(1500)]], [_BIG[0], [_r.choice(_vals) for _ in range(1500)]]]
_t = _ser(_chain(list(range(0, 3 * 1200, 3))))
p["tests"].append([_t, [_r.randint(-0, 3600) for _ in range(1000)]])


def b_neighbors(tree, queries):
    vals = _inorder(_parse(tree))
    out = []
    for q in queries:
        lo = [v for v in vals if v < q]
        hi = [v for v in vals if v > q]
        out.append([max(lo) if lo else -1, min(hi) if hi else -1])
    return out


def g_neighbors(r):
    n = r.randint(0, 9)
    t = _ser(_rand_bst(r, n, 20)) if n else []
    return [t, [r.randint(0, 20) for _ in range(r.randint(1, 6))]]


def v_neighbors(tests):
    for t in tests:
        arr, qs = t["args"]
        _chk_tree(arr, 0, MAXN, MAXV)
        assert (not arr) or _is_bst(arr)
        assert 1 <= len(qs) <= 3000 and all(0 <= q <= MAXV for q in qs)
        assert len(t["expected"]) == len(qs)


CHECKS["bst-neighbors-of-queries"] = (b_neighbors, g_neighbors, "exact")
VALIDATE["bst-neighbors-of-queries"] = v_neighbors

p = add(
    id="bst-valid-preorder-sequence", title="Could This Be a BST's Preorder?", diff="Medium", topic=TOPIC,
    fn="isBstPreorder", params=[("preorder", "int[]")], ret="bool", cmp="exact",
    desc="<p>You are given an array of <strong>distinct</strong> integers. Decide whether it can be the <strong>preorder traversal</strong> (root, then left subtree, then right subtree) of some binary search tree, where every value in a node's left subtree is smaller than the node and every value in its right subtree is larger.</p>"
         "<p>Only the array is given, not the tree: you must decide whether any BST has exactly this preorder.</p>"
         "<p><strong>Example 1</strong></p><pre>preorder = [5,2,1,3,7,6,8]\nOutput: true\nThis is the preorder of [5,2,7,1,3,6,8].</pre>"
         "<p><strong>Example 2</strong></p><pre>preorder = [5,2,6,1,3]\nOutput: false\nAfter 6 (larger than the root 5) we are in the right subtree of 5, so the later 1 cannot appear.</pre>"
         "<p><strong>Example 3</strong></p><pre>preorder = [4]\nOutput: true</pre>",
    constraints=["1 &le; preorder.length &le; 5,000", "0 &le; preorder[i] &le; 10<sup>9</sup>, all values distinct"],
    hints=["The first value is the root. In a BST preorder, the values smaller than the root come first (left subtree), then the larger ones (right subtree). Checking this recursively is correct but may be slow on skewed input.",
           "Once you have moved to the right of some value <code>x</code> (you read something larger than <code>x</code> after it), every later value must stay larger than <code>x</code>. So you only need the largest such <code>x</code> seen so far as a lower bound.",
           "Keep a stack of values whose right subtree is still open and a variable <code>low</code>. For each value: if it is below <code>low</code> return false; while the stack top is smaller than the value, pop it and set <code>low</code> to it; then push the value."],
    editorial=["Simulate the construction with a stack that holds the current left spine. When the next value is smaller than the stack top it goes into the left subtree of the top, so just push it. When it is larger, it belongs to the right subtree of the last stack element that is smaller than it: pop all those elements, and remember the last popped one as <code>low</code>. From then on, nothing in the sequence may ever be below <code>low</code>, because that would need to be placed inside a subtree that is already closed.",
               "Every value is pushed and popped at most once, so the algorithm runs in O(n) time with O(n) stack space in the worst case. An alternative is the recursive split 'smaller part, then larger part' which costs O(n log n) on balanced input and O(n^2) on a chain."],
    time="O(n)", space="O(n)",
    solution='''def isBstPreorder(preorder):
    low = -1
    stack = []
    for x in preorder:
        if x < low:
            return False
        while stack and stack[-1] < x:
            low = stack.pop()
        stack.append(x)
    return True
''',
    tests=[[[5, 2, 1, 3, 7, 6, 8]], [[5, 2, 6, 1, 3]], [[4]], [[1, 2]], [[2, 1]], [[1, 3, 2]], [[3, 1, 2]], [[2, 3, 1]], [[3, 4, 1, 2]], [[10, 5, 1, 7, 40, 50]],
           [[10, 5, 1, 7, 40, 8]], [[0, 1000000000]], [[1000000000, 0]]],
)
_r = rnd(3107)
_t = _rand_bst(_r, 3000, 10 ** 9)
_pre = _preorder(_t)
p["tests"].append([_pre])  # valid, random shape
_bad = _pre[:]
_bad[100], _bad[2500] = _bad[2500], _bad[100]
p["tests"].append([_bad])  # swapped far apart, invalid
p["tests"].append([list(range(1, 3000)) + [0]])  # ascending chain then a small value
p["tests"].append([list(range(3000, 0, -1))])  # descending chain, valid
_pre2 = _preorder(_rand_bst(_r, 1000, 10 ** 9))
p["tests"].append([_pre2 + [_pre2[0] // 2 + 1 if _pre2[0] // 2 + 1 not in _pre2 else 3]])


def _pre_ok(a):
    if len(a) <= 1:
        return True
    root = a[0]
    k = 1
    while k < len(a) and a[k] < root:
        k += 1
    if any(x < root for x in a[k:]):
        return False
    return _pre_ok(a[1:k]) and _pre_ok(a[k:])


def b_preorder(a):
    return _pre_ok(a)


def g_preorder(r):
    n = r.randint(1, 8)
    if r.random() < 0.5:
        return [_preorder(_rand_bst(r, n, 15))]
    return [r.sample(range(0, 16), n)]


def v_preorder(tests):
    for t in tests:
        a = t["args"][0]
        assert 1 <= len(a) <= 5000 and len(set(a)) == len(a) and all(0 <= x <= 10 ** 9 for x in a)
        if len(a) <= 200:
            assert _pre_ok(a) == t["expected"]
    res = [t["expected"] for t in tests]
    assert res.count(True) >= 5 and res.count(False) >= 5


CHECKS["bst-valid-preorder-sequence"] = (b_preorder, g_preorder, "exact")
VALIDATE["bst-valid-preorder-sequence"] = v_preorder

p = add(
    id="bst-count-misplaced-nodes", title="Count Nodes Breaking an Ancestor's Order", diff="Medium", topic=TOPIC, tier="extra",
    fn="countMisplacedNodes", params=[("tree", "int[]")], ret="int", cmp="exact",
    desc="<p>The tree below was meant to be a binary search tree but may contain mistakes. Call a node <strong>misplaced</strong> if it breaks the order demanded by at least one of its <em>ancestors</em>: it lies in the left subtree of an ancestor but its value is <strong>not smaller</strong> than that ancestor, or it lies in the right subtree of an ancestor but its value is <strong>not larger</strong> than that ancestor. Equal values therefore count as a violation.</p>"
         "<p>Return the number of misplaced nodes. A tree is a valid BST exactly when the answer is <code>0</code>. Every ancestor counts, even an ancestor that is itself misplaced.</p>"
         + _ENC +
         "<p><strong>Example 1</strong></p><pre>tree = [10,5,15,-1,-1,6,20]\nOutput: 1\nThe node 6 is the left child of 15, but it also lies in the right subtree of 10 and 6 &lt; 10.</pre>"
         "<p><strong>Example 2</strong></p><pre>tree = [3,4,2,5]\nOutput: 3\nThe node 4 is in the left subtree of 3 but is larger; 2 is in the right subtree of 3 but is smaller; and 5 sits in the left subtree of 3 as well, below 4, and is larger than 3.</pre>"
         "<p><strong>Example 3</strong></p><pre>tree = [2,1,3]\nOutput: 0</pre>",
    constraints=[f"1 &le; number of nodes &le; {MAXN:,}", f"0 &le; node value &le; {MAXV:,}; values may repeat"],
    hints=["Comparing a node with its parent is not enough, as Example 1 shows. A node must respect every ancestor.",
           "While going down, every ancestor that you pass on the left side gives an upper bound, every ancestor passed on the right gives a lower bound. Only the tightest bounds matter.",
           "Do a stack walk carrying <code>(node, lo, hi)</code>. A node is misplaced if it is not strictly between <code>lo</code> and <code>hi</code>. Children inherit <code>(lo, min(hi, value))</code> and <code>(max(lo, value), hi)</code> from their parent, whether or not the parent was misplaced."],
    editorial=["Each ancestor restricts its descendants: everything on its left must be smaller and everything on its right larger. Accumulating these restrictions along the path gives for each node an open interval <code>(lo, hi)</code>, where <code>lo</code> is the largest ancestor value from which we went right and <code>hi</code> the smallest ancestor value from which we went left. A node violates some ancestor exactly when its value is not strictly inside that interval.",
               "Note that the bounds must keep being tightened by the node's own value even if the node is misplaced, because the definition counts every ancestor. One depth-first walk with an explicit stack does the job in O(n) time, O(n) space, and does not recurse so deep trees are fine."],
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


def countMisplacedNodes(tree):
    val, left, right = parse(tree)
    bad = 0
    stack = [(0, -1, 1 << 40)]
    while stack:
        u, lo, hi = stack.pop()
        x = val[u]
        if not (lo < x < hi):
            bad += 1
        if left[u] != -1:
            stack.append((left[u], lo, min(hi, x)))
        if right[u] != -1:
            stack.append((right[u], max(lo, x), hi))
    return bad
''',
    tests=[[[10, 5, 15, -1, -1, 6, 20]], [[3, 4, 2, 5]], [[2, 1, 3]], [[7]], [[7, 7]], [[7, 7, 7]], [[5, 6]], [[5, -1, 4]], [[5, 1, 8, 0, 9, 3, 6]],
           [[5, 1, 8, 0, 2, 3, 6, -1, -1, -1, -1, 4, 7, 9, 10]]],
)
_r = rnd(3108)
_b = _rand_bst(_r, 2000, MAXV)
p["tests"].append([_ser(_mutate(_r, _b, 150, MAXV))])
p["tests"].append([_ser(_fill_random(_r, _rand_shape(_r, 2000), 0, MAXV))])
p["tests"].append([_ser(_fill_random(_r, _rand_shape(_r, 1500), 0, 5))])
p["tests"].append([_ser(_balanced(sorted(_r.sample(range(MAXV + 1), 2047))))])


def b_misplaced(tree):
    root = _parse(tree)
    parent = {}
    for nd in _nodes(root):
        for s in (1, 2):
            if nd[s] is not None:
                parent[id(nd[s])] = (nd, s)
    cnt = 0
    for nd in _nodes(root):
        cur = nd
        wrong = False
        while id(cur) in parent:
            anc, s = parent[id(cur)]
            if (s == 1 and nd[0] >= anc[0]) or (s == 2 and nd[0] <= anc[0]):
                wrong = True
                break
            cur = anc
        cnt += wrong
    return cnt


def g_misplaced(r):
    n = r.randint(1, 9)
    mode = r.random()
    if mode < 0.3:
        return [_ser(_fill_random(r, _rand_shape(r, n), 0, 6))]
    root = _rand_bst(r, n, 14)
    if mode > 0.4:
        _mutate(r, root, r.randint(1, 3), 14)
    return [_ser(root)]


def v_misplaced(tests):
    for t in tests:
        _chk_tree(t["args"][0], 1, MAXN, MAXV)
        assert 0 <= t["expected"] <= len(t["args"][0])
    res = [t["expected"] for t in tests]
    assert 0 in res and sum(1 for x in res if x >= 5) >= 2


CHECKS["bst-count-misplaced-nodes"] = (b_misplaced, g_misplaced, "exact")
VALIDATE["bst-count-misplaced-nodes"] = v_misplaced


# =================================================================== HARD

p = add(
    id="bst-largest-valid-subtree", title="Largest BST Hidden in a Tree", diff="Hard", topic=TOPIC,
    fn="largestBstSubtree", params=[("tree", "int[]")], ret="int", cmp="exact",
    desc="<p>You are given an arbitrary binary tree (it may not be a BST). A <em>subtree</em> is a node together with all of its descendants. A subtree is a <strong>valid BST</strong> when for every node inside it all values in the left part are strictly smaller and all values in the right part strictly larger than that node (so duplicates make it invalid). A single node is always a valid BST.</p>"
         "<p>Return the largest number of nodes in a subtree that is a valid BST. The empty tree gives <code>0</code>.</p>"
         + _ENC +
         "<p><strong>Example 1</strong></p><pre>tree = [10,5,15,1,8,-1,7]\nOutput: 3\nThe whole tree is not a BST (7 is in the right subtree of 15 but smaller). The subtree rooted at 5 with children 1 and 8 is a BST of 3 nodes.</pre>"
         "<p><strong>Example 2</strong></p><pre>tree = [2,1,3]\nOutput: 3</pre>"
         "<p><strong>Example 3</strong></p><pre>tree = [4,4,4]\nOutput: 1\nEqual values break the strict order, so only single nodes qualify.</pre>",
    constraints=[f"0 &le; number of nodes &le; {MAXN:,}", f"0 &le; node value &le; {MAXV:,}; values may repeat"],
    hints=["Testing every node separately by running a full BST validation on its subtree works, but it is O(n * h) or worse. Can each subtree reuse what its children already know?",
           "A node roots a valid BST exactly when its left subtree is a valid BST whose maximum is below the node, and its right subtree is a valid BST whose minimum is above the node.",
           "Process nodes bottom-up (in reverse level order). For each node store whether its subtree is a valid BST and, if so, its size, minimum and maximum. Keep the largest size of any valid one."],
    editorial=["Work bottom-up, so that every node can use the summary of its two children. For a valid BST subtree we store three numbers: its size, its smallest value and its largest value. A node with left summary <code>L</code> and right summary <code>R</code> forms a valid BST when each present child is itself valid, <code>L.max &lt; value</code> and <code>R.min &gt; value</code>. Its size is <code>L.size + R.size + 1</code>, its minimum is <code>L.min</code> (or its own value if there is no left child) and its maximum is <code>R.max</code> (or its own value). Otherwise the node is marked invalid, and so are all its ancestors, since a subtree containing an invalid part cannot be a BST.",
               "Decoding the array yields nodes in level order, where children always come after their parent; iterating the indices in reverse is therefore a valid bottom-up order and needs no recursion. Time O(n), space O(n)."],
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


def largestBstSubtree(tree):
    if not tree:
        return 0
    val, left, right = parse(tree)
    n = len(val)
    ok = [False] * n
    size = [0] * n
    lo = [0] * n
    hi = [0] * n
    best = 0
    for u in range(n - 1, -1, -1):
        l, r = left[u], right[u]
        if (l == -1 or (ok[l] and hi[l] < val[u])) and (r == -1 or (ok[r] and lo[r] > val[u])):
            ok[u] = True
            size[u] = 1 + (size[l] if l != -1 else 0) + (size[r] if r != -1 else 0)
            lo[u] = lo[l] if l != -1 else val[u]
            hi[u] = hi[r] if r != -1 else val[u]
            if size[u] > best:
                best = size[u]
    return best
''',
    tests=[[[10, 5, 15, 1, 8, -1, 7]], [[2, 1, 3]], [[4, 4, 4]], [[]], [[9]], [[5, 6]], [[5, 4]], [[5, 4, -1, 3]], [[5, 1, 8, 0, 9, 3, 6]],
           [[10, 5, 15, 1, 8, 12, 20, -1, -1, 6, 9, 11, 13]], [[3, 2, 4, 1, 5]]],
)
_r = rnd(3109)
p["tests"].append([_ser(_mutate(_r, _rand_bst(_r, 2200, MAXV), 25, MAXV))])
p["tests"].append([_ser(_mutate(_r, _rand_bst(_r, 2200, MAXV), 200, MAXV))])
p["tests"].append([_ser(_fill_random(_r, _rand_shape(_r, 2000), 0, MAXV))])
_v = _r.sample(range(MAXV + 1), 1500)
_c = _bst_from(sorted(_v))
_nd = _nodes(_c)
_nd[1400][0] = 0
p["tests"].append([_ser(_c)])  # a long chain with one bad value near the bottom


def b_largest(tree):
    root = _parse(tree)
    best = 0
    for nd in _nodes(root):
        sub = []
        stack = [nd]
        while stack:
            x = stack.pop()
            sub.append(x)
            for s in (1, 2):
                if x[s] is not None:
                    stack.append(x[s])
        ino = _inorder(nd)
        if all(ino[i] < ino[i + 1] for i in range(len(ino) - 1)):
            best = max(best, len(sub))
    return best


def g_largest(r):
    n = r.randint(0, 9)
    if n == 0:
        return [[]]
    mode = r.random()
    if mode < 0.3:
        return [_ser(_fill_random(r, _rand_shape(r, n), 0, 6))]
    root = _rand_bst(r, n, 14)
    if mode > 0.4:
        _mutate(r, root, r.randint(1, 2), 14)
    return [_ser(root)]


def v_largest(tests):
    for t in tests:
        arr = t["args"][0]
        _chk_tree(arr, 0, MAXN, MAXV)
        n = sum(1 for x in arr if x != -1)
        assert 0 <= t["expected"] <= n
    res = [(sum(1 for x in t["args"][0] if x != -1), t["expected"]) for t in tests]
    assert any(e < n for n, e in res) and any(e == n and n > 1 for n, e in res)


CHECKS["bst-largest-valid-subtree"] = (b_largest, g_largest, "exact")
VALIDATE["bst-largest-valid-subtree"] = v_largest

p = add(
    id="odd-even-jump-good-starts", title="Odd and Even Jumps to the End", diff="Hard", topic=TOPIC, tier="extra",
    fn="countGoodStarts", params=[("a", "int[]")], ret="int", cmp="exact",
    desc="<p>You stand on some index of the array <code>a</code> and make a series of jumps, always to the <strong>right</strong>. The jumps are numbered 1, 2, 3, ... and alternate between two kinds. From index <code>i</code>:</p>"
         "<ul><li>on an <strong>odd-numbered</strong> jump you go to the index <code>j &gt; i</code> with the <strong>smallest</strong> value <code>a[j] &ge; a[i]</code>;</li>"
         "<li>on an <strong>even-numbered</strong> jump you go to the index <code>j &gt; i</code> with the <strong>largest</strong> value <code>a[j] &le; a[i]</code>.</li></ul>"
         "<p>If several indices have that best value, take the smallest index among them. If no index qualifies, you are stuck. A starting index is <em>good</em> if some series of jumps (there is only one, since every jump is forced) reaches the last index. The last index itself is always good.</p>"
         "<p>Return the number of good starting indices.</p>"
         "<p><strong>Example 1</strong></p><pre>a = [10,13,12,14,15]\nOutput: 2\nFrom index 3 (value 14) the first jump goes to 15 at the end. From index 0: jump 1 goes to 12, jump 2 needs a value &le; 12 to the right of it and finds none, so it is stuck. Indices 1 and 2 get stuck the same way. Good starts: indices 3 and 4.</pre>"
         "<p><strong>Example 2</strong></p><pre>a = [2,3,1,1,4]\nOutput: 3\nGood starts: indices 1, 3 and 4. For example from index 3 (value 1): jump 1 goes to 4, the last index. From index 0 (value 2): jump 1 goes to 3 (index 1), jump 2 goes to the largest value &le; 3 on the right, which is 1 at index 2 (the first of two ones), jump 3 goes to the smallest value &ge; 1, which is 1 at index 3, jump 4 needs a value &le; 1 to the right of index 3 and finds none, so it is stuck.</pre>"
         "<p><strong>Example 3</strong></p><pre>a = [5]\nOutput: 1</pre>",
    constraints=["1 &le; a.length &le; 5,000", "0 &le; a[i] &le; 100,000"],
    hints=["Simulating every start for as long as it takes is O(n) jumps per start, O(n<sup>2</sup>) overall. Notice that a jump from index <code>i</code> only depends on <code>i</code> and the kind of jump, not on how you got there.",
           "Let <code>up[i]</code> mean 'standing on i and the next jump is odd, can I reach the end?' and <code>down[i]</code> the same for an even next jump. Then <code>up[i] = down[j]</code> where j is the odd-jump target, and <code>down[i] = up[j']</code> for the even-jump target j'.",
           "Compute the answers from right to left. Keep the already seen indices to the right of i in a sorted structure of pairs (value, index); the odd target is the first pair not smaller than (a[i], -1) and the even target is found by taking the last pair with value &le; a[i] and then moving to the smallest index of that value. Count the indices with <code>up[i]</code> true."],
    editorial=["Every jump is forced, so a start is good or bad independent of how the walk got there. Define <code>up[i]</code> (the next jump from i is odd) and <code>down[i]</code> (the next jump is even) as 'the last index is reachable'. The last index has both set. For i from right to left, find the odd target j (the successor of a[i] among the values to the right, ties to the smallest index) and the even target j' (the floor of a[i], ties again to the smallest index), then <code>up[i] = down[j]</code> and <code>down[i] = up[j']</code>, treating a missing target as false. The answer is the number of true <code>up[i]</code>: every start begins with jump number 1, an odd jump.",
               "The only data structure needed is an ordered set of (value, index) pairs that supports insert, successor and floor, exactly what a balanced BST offers. In Python a sorted list with <code>bisect</code> and <code>insort</code> plays that role: inserting is a fast memmove and the queries are binary searches. Total O(n log n) comparisons (O(n<sup>2</sup>) tiny memmove work in the worst case, fine for n = 5,000). A monotonic-stack solution over the values sorted by (value, index) also exists."],
    time="O(n log n)", space="O(n)",
    solution='''from bisect import bisect_left, bisect_right, insort


def countGoodStarts(a):
    n = len(a)
    up = [False] * n
    down = [False] * n
    up[n - 1] = down[n - 1] = True
    seen = [(a[n - 1], n - 1)]
    for i in range(n - 2, -1, -1):
        v = a[i]
        k = bisect_left(seen, (v, -1))
        if k < len(seen):
            up[i] = down[seen[k][1]]
        k = bisect_right(seen, (v, n + 1)) - 1
        if k >= 0:
            k = bisect_left(seen, (seen[k][0], -1))
            down[i] = up[seen[k][1]]
        insort(seen, (v, i))
    return sum(up)
''',
    tests=[[[10, 13, 12, 14, 15]], [[2, 3, 1, 1, 4]], [[5]], [[1, 2]], [[2, 1]], [[3, 3, 3]], [[0, 100000]], [[5, 1, 3, 4, 2]], [[1, 1, 1, 1, 1, 1]],
           [[5, 4, 3, 2, 1]], [[1, 2, 3, 4, 5]], [[3, 1, 4, 1, 5, 9, 2, 6, 5, 3, 5]]],
)
_r = rnd(3110)
p["tests"].append([[_r.randint(0, MAXV) for _ in range(4000)]])
p["tests"].append([[_r.randint(0, 30) for _ in range(4000)]])
p["tests"].append([[_r.randint(0, 3) if k % 7 else _r.randint(0, MAXV) for k in range(3500)]])
p["tests"].append([list(range(2500, 0, -1)) + list(range(2500))])


def b_jumps(a):
    n = len(a)
    good = 0
    for s in range(n):
        i, odd = s, True
        while i != n - 1:
            best = -1
            for j in range(i + 1, n):
                if odd:
                    if a[j] >= a[i] and (best == -1 or a[j] < a[best]):
                        best = j
                else:
                    if a[j] <= a[i] and (best == -1 or a[j] > a[best]):
                        best = j
            if best == -1:
                break
            i, odd = best, not odd
        good += i == n - 1
    return good


def g_jumps(r):
    return [[r.randint(0, r.choice((3, 8, 20))) for _ in range(r.randint(1, 12))]]


def v_jumps(tests):
    for t in tests:
        a = t["args"][0]
        assert 1 <= len(a) <= 5000 and all(0 <= x <= MAXV for x in a)
        assert 1 <= t["expected"] <= len(a)
        if len(a) <= 200:
            assert b_jumps(a) == t["expected"]
    res = [t["expected"] for t in tests]
    assert max(res) >= 100 and min(res) == 1


CHECKS["odd-even-jump-good-starts"] = (b_jumps, g_jumps, "exact")
VALIDATE["odd-even-jump-good-starts"] = v_jumps

p = add(
    id="bst-insertion-depths-sequence", title="Depth of Every Insertion into a BST", diff="Hard", topic=TOPIC, tier="extra",
    fn="insertionDepths", params=[("values", "int[]")], ret="int[]", cmp="exact",
    desc="<p>Start with an empty binary search tree and insert the distinct integers of <code>values</code> one after another, in the given order. Every insertion uses the standard rule: begin at the root, go left when the new value is smaller than the current node and right when it is larger, and attach the new node at the first missing child. The first value becomes the root.</p>"
         "<p>Return an array <code>d</code> where <code>d[i]</code> is the <strong>depth</strong> of <code>values[i]</code> at the moment it is inserted (the root has depth <code>0</code>, its children depth <code>1</code>, and so on). Nodes never move afterwards, so this is also its final depth.</p>"
         "<p>Doing the insertions one by one can take O(n<sup>2</sup>) time when the sequence is sorted; try to do better.</p>"
         "<p><strong>Example 1</strong></p><pre>values = [5,2,8,1,3]\nOutput: [0,1,1,2,2]</pre>"
         "<p><strong>Example 2</strong></p><pre>values = [1,2,3,4]\nOutput: [0,1,2,3]\nThe tree is a path.</pre>"
         "<p><strong>Example 3</strong></p><pre>values = [4,6,5,7,3]\nOutput: [0,1,2,2,1]</pre>",
    constraints=["1 &le; values.length &le; 5,000", "0 &le; values[i] &le; 100,000, all values distinct"],
    hints=["The depth of a new node is one more than the depth of its parent. Which existing node will become the parent of the new value?",
           "When a value is inserted, its parent is either the predecessor or the successor of the value among the values <em>already inserted</em>: whichever of the two was inserted later (is deeper).",
           "Finding the predecessor and successor among earlier values is easy if you go backwards: put all values in a doubly linked list sorted by value, then remove them from the last insertion to the first. At the moment you remove <code>values[i]</code>, its two list neighbours are exactly its neighbours among values[0..i-1]. Then compute depths forwards: <code>d[i] = 1 + max(d[pred], d[succ])</code>."],
    editorial=["Claim: when <code>x</code> is inserted, its parent is its predecessor or its successor among the values already in the tree, namely the one inserted later. Both are on the search path of <code>x</code>, and between them in value order there is nothing else yet. Hence <code>depth(x) = 1 + max(depth(pred), depth(succ))</code> (a missing neighbour counts as depth -1, which makes the first element depth 0).",
               "To get pred and succ among earlier elements for all i at once, sort the indices by value and link them in a doubly linked list. Process i from n-1 down to 0: the neighbours of i in the list right now are the closest earlier-inserted values around <code>values[i]</code> (all later ones have been removed already); record them and unlink i in O(1). Then fill the depths forwards in insertion order. Total O(n log n) for the sort and O(n) for the rest, with no tree needed."],
    time="O(n log n)", space="O(n)",
    solution='''def insertionDepths(values):
    n = len(values)
    order = sorted(range(n), key=lambda i: values[i])
    prv = [-1] * n
    nxt = [-1] * n
    for k in range(n):
        i = order[k]
        if k > 0:
            prv[i] = order[k - 1]
        if k + 1 < n:
            nxt[i] = order[k + 1]
    pa = [-1] * n
    su = [-1] * n
    for i in range(n - 1, -1, -1):
        p, q = prv[i], nxt[i]
        pa[i], su[i] = p, q
        if p != -1:
            nxt[p] = q
        if q != -1:
            prv[q] = p
    depth = [0] * n
    for i in range(1, n):
        d = -1
        if pa[i] != -1:
            d = depth[pa[i]]
        if su[i] != -1 and depth[su[i]] > d:
            d = depth[su[i]]
        depth[i] = d + 1
    return depth
''',
    tests=[[[5, 2, 8, 1, 3]], [[1, 2, 3, 4]], [[4, 6, 5, 7, 3]], [[9]], [[1, 0]], [[0, 100000]], [[4, 2, 6, 1, 3, 5, 7]], [[1, 7, 2, 6, 3, 5, 4]], [[4, 3, 2, 1]],
           [[3, 1, 2]]],
)
_r = rnd(3111)
p["tests"].append([_r.sample(range(MAXV + 1), 4000)])
p["tests"].append([list(range(0, 3500))])
_z = []
_lo, _hi = 0, 3999
while _lo <= _hi:
    _z.append(_lo)
    _lo += 1
    if _lo <= _hi:
        _z.append(_hi)
        _hi -= 1
p["tests"].append([_z])


def b_depths(values):
    root = None
    out = []
    for v in values:
        if root is None:
            root = _node(v)
            out.append(0)
            continue
        cur, d = root, 0
        while True:
            s = 1 if v < cur[0] else 2
            d += 1
            if cur[s] is None:
                cur[s] = _node(v)
                break
            cur = cur[s]
        out.append(d)
    return out


def g_depths(r):
    return [r.sample(range(0, 40), r.randint(1, 12))]


def v_depths(tests):
    for t in tests:
        a = t["args"][0]
        assert 1 <= len(a) <= 5000 and len(set(a)) == len(a) and all(0 <= x <= MAXV for x in a)
        d = t["expected"]
        assert len(d) == len(a) and d[0] == 0 and all(0 <= x < len(a) for x in d)
        if len(a) <= 300:
            assert d == b_depths(a)
    assert max(max(t["expected"]) for t in tests) >= 3000


CHECKS["bst-insertion-depths-sequence"] = (b_depths, g_depths, "exact")
VALIDATE["bst-insertion-depths-sequence"] = v_depths
