"""Problems: binary trees, level order and views (level-order int[] encoding, -1 for a missing child). See data/lib.py for the registry."""
from collections import deque

from lib import add, rnd, CHECKS, VALIDATE, gen_arr  # noqa: F401

MAXN = 1500      # maximum number of nodes in any tree
MAXV = 10000     # maximum node value
MAXLV = 30       # level cap for problems whose answer is a width measured in complete-tree slots

ENC = (
    "<p><strong>How trees are given.</strong> There is no tree type here. A binary tree is passed as an integer array in "
    "<em>level-order</em> (top to bottom, left to right), the same way LeetCode serialises trees. A missing child is written as "
    "<code>-1</code>, and every real node value is non-negative. The children of a missing node are not listed, and trailing "
    "<code>-1</code> entries are dropped, so a non-empty array never ends with <code>-1</code>. The empty tree is <code>[]</code>.</p>"
    "<p>For example, <code>[1, 2, 3, -1, 4]</code> describes the tree on the left: the root is 1 with children 2 and 3, node 2 has no left "
    "child and has 4 as its right child, and node 3 is a leaf.</p>"
    "<pre>    1\n   / \\\n  2   3\n   \\\n    4</pre>"
)


def _cons(extra=None, minn=0):
    out = [f"{minn} &le; number of nodes &le; {MAXN:,}", f"0 &le; node value &le; {MAXV:,}",
           "The array follows the encoding above exactly (valid level-order, no trailing -1)"]
    return out + (extra or [])


# ------------------------------------------------------------------ helpers (tests, generators and brute forces only)
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


def _levels(root):
    """Nodes grouped by level, each level left to right."""
    out = []
    cur = [root] if root else []
    while cur:
        out.append(cur)
        cur = [c for x in cur for c in (x.l, x.r) if c]
    return out


def _depth_of(arr):
    return len(_levels(_build(arr)))


def _grow(r, n, cap=None, mode="random"):
    """A random tree shape with up to n nodes and at most `cap` levels; returns (root, nodes)."""
    root = _N(0)
    nodes = [root]
    free = []
    if cap is None or cap >= 2:
        free = [(root, 0, 2), (root, 1, 2)]
    flip = 0
    while len(nodes) < n and free:
        if mode == "complete":
            i = 0
        elif mode == "left":
            i = max(0, len(free) - 2)
        elif mode == "right":
            i = len(free) - 1
        elif mode == "zig":
            flip ^= 1
            i = max(0, len(free) - 2 + flip)
        elif mode == "shallow":
            i = r.randrange(min(len(free), 3))
        elif mode == "deep":
            i = len(free) - 1 - r.randrange(min(len(free), 3))
        else:
            i = r.randrange(len(free))
        node, side, lv = free.pop(i)
        c = _N(0)
        if side == 0:
            node.l = c
        else:
            node.r = c
        nodes.append(c)
        if cap is None or lv < cap:
            free.append((c, 0, lv + 1))
            free.append((c, 1, lv + 1))
    return root, nodes


def _tree(r, n, mode="random", cap=None, lo=0, hi=MAXV, distinct=False):
    root, nodes = _grow(r, n, cap, mode)
    if distinct:
        vs = r.sample(range(lo, hi + 1), len(nodes))
        for x, v in zip(nodes, vs):
            x.v = v
    else:
        for x in nodes:
            x.v = r.randint(lo, hi)
    return _encode(root)


def _two_chains(r, h, extra, lo=0, hi=MAXV, distinct=False):
    """A left chain and a right chain of h levels each below the root, plus `extra` random nodes attached below (very wide levels)."""
    root = _N(0)
    nodes = [root]
    a = root
    b = root
    for _ in range(h - 1):
        a.l = _N(0)
        a = a.l
        b.r = _N(0)
        b = b.r
        nodes += [a, b]
    free = [(x, s) for x in nodes for s in (0, 1) if (x.l if s == 0 else x.r) is None]
    lv = {}
    for k, lvl in enumerate(_levels(root)):
        for x in lvl:
            lv[id(x)] = k
    for _ in range(extra):
        cand = [(x, s) for (x, s) in free if lv[id(x)] + 1 < h and (x.l if s == 0 else x.r) is None]
        if not cand:
            break
        x, s = r.choice(cand)
        c = _N(0)
        if s == 0:
            x.l = c
        else:
            x.r = c
        lv[id(c)] = lv[id(x)] + 1
        nodes.append(c)
        free += [(c, 0), (c, 1)]
    if distinct:
        for x, v in zip(nodes, r.sample(range(lo, hi + 1), len(nodes))):
            x.v = v
    else:
        for x in nodes:
            x.v = r.randint(lo, hi)
    return _encode(root)


MODES = ["random", "random", "deep", "shallow", "complete", "left", "right", "zig"]


def _gen(nmax=10, vmax=5, minn=0, cap=None, distinct=False):
    def g(r):
        n = r.randint(minn, nmax)
        return [_tree(r, n, r.choice(MODES), cap, 0, vmax, distinct)]
    return g


def _v_trees(tests, minn=0, cap=None, distinct=False):
    for t in tests:
        arr = t["args"][0]
        assert isinstance(arr, list) and all(isinstance(x, int) for x in arr)
        assert arr == _encode(_build(arr)), ("not a canonical level-order encoding", arr[:12])
        nodes = [x for x in arr if x != -1]
        assert minn <= len(nodes) <= MAXN, "bad number of nodes"
        assert all(0 <= x <= MAXV for x in nodes), "node value out of range"
        assert not arr or arr[0] != -1
        if cap:
            assert _depth_of(arr) <= cap, "too many levels"
        if distinct:
            assert len(set(nodes)) == len(nodes), "values must be distinct"


def _big(seed, cap=None, distinct=False, hi=MAXV, lo=0, shapes=("random", "deep", "left")):
    r = rnd(seed)
    out = []
    for s in shapes:
        if cap is not None and s in ("left", "right", "zig"):
            continue
        out.append(_tree(r, MAXN, s, cap, lo, hi, distinct))
    return out


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
BASE1 = [t for t in BASE if t]                  # at least one node
BASE2 = [t for t in BASE if len(t) >= 2]        # at least two nodes


def _perm_tree(seed, n, mode="random", cap=None, hi=MAXV):
    r = rnd(seed)
    return _tree(r, n, mode, cap, 0, hi, True)


# ================================================================== EASY

# ---------------------------------------------------------------- level order groups
add(
    id="binary-tree-level-order-groups", title="Binary Tree Level Order Traversal", diff="Easy", topic="Trees", tier="must",
    fn="levelOrder", params=[("tree", "int[]")], ret="int[][]", cmp="exact",
    desc="<p>Given a binary tree, return its values grouped by level. The result is a list of lists: the first list holds the root, the second list holds the children of the root, and so on. Inside every list the values go from left to right. The empty tree gives <code>[]</code>.</p>" + ENC +
         "<p>For <code>tree = [3, 9, 20, -1, -1, 15, 7]</code> the answer is <code>[[3], [9, 20], [15, 7]]</code>.</p>",
    constraints=_cons(),
    hints=["The array is already in level order. The only job is to find where one level ends and the next one begins.",
           "A node is on the level right below its parent. Walk the nodes in array order and give each child the level of its parent plus one.",
           "Keep a <code>depth</code> value per real node. When you reach a node, append its value to <code>result[depth]</code>, creating a new inner list the first time that depth appears."],
    editorial=["The classic way is a breadth-first search with a queue: process the queue one whole level at a time by taking the current size of the queue, popping that many nodes, and pushing their children for the next round.",
               "With this array encoding no queue is needed. The real nodes appear in level order, so parents always come before their children. A single left-to-right pass can set <code>depth[child] = depth[parent] + 1</code> and append every node to the list of its depth. Every node is handled once, so the time is O(n)."],
    time="O(n)", space="O(n)",
    solution=LINKS + '''def levelOrder(tree):
    vals, left, right = _links(tree)
    n = len(vals)
    depth = [0] * n
    out = []
    for k in range(n):
        d = depth[k]
        if d == len(out):
            out.append([])
        out[d].append(vals[k])
        for c in (left[k], right[k]):
            if c != -1:
                depth[c] = d + 1
    return out
''',
    tests=[[t] for t in BASE + [[1, 2, 3, 4, -1, -1, 5], [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]] + _big(8101, hi=99)],
)


def _b_levels(tree):
    return [[x.v for x in lv] for lv in _levels(_build(tree))]


CHECKS["binary-tree-level-order-groups"] = (_b_levels, _gen(12, 30), "exact")
VALIDATE["binary-tree-level-order-groups"] = _v_trees

# ---------------------------------------------------------------- level averages
add(
    id="tree-level-averages-floored", title="Average of Each Tree Level (Rounded Down)", diff="Easy", topic="Trees",
    fn="levelAverages", params=[("tree", "int[]")], ret="int[]", cmp="exact",
    desc="<p>For every level of a binary tree, compute the average of the values of its nodes, rounded <em>down</em> to an integer. Return these averages from the top level to the bottom level. The empty tree gives <code>[]</code>.</p>" + ENC +
         "<p>For <code>tree = [3, 9, 20, -1, -1, 15, 7]</code> the levels are <code>[3]</code>, <code>[9, 20]</code> and <code>[15, 7]</code>, with exact averages 3, 14.5 and 11, so the answer is <code>[3, 14, 11]</code>.</p>",
    constraints=_cons(),
    hints=["Each level needs two numbers: the sum of its values and the count of its nodes.",
           "Because the array is in level order, a node's level is one more than its parent's level. Keep a <code>depth</code> per node and two parallel lists <code>sums</code> and <code>counts</code> indexed by depth.",
           "At the end the average of level <code>d</code> is <code>sums[d] // counts[d]</code>. All values are non-negative, so integer division rounds down."],
    editorial=["Group the values by level (a breadth-first search, or a single pass over the array that propagates depths from parents to children) while keeping only a running sum and a node count for each level. After the pass, divide each sum by its count with floor division.",
               "No floating point numbers are needed, which also removes any rounding doubt. Time is linear in the number of nodes and the extra space is proportional to the number of levels (plus the depth array)."],
    time="O(n)", space="O(n)",
    solution=LINKS + '''def levelAverages(tree):
    vals, left, right = _links(tree)
    n = len(vals)
    depth = [0] * n
    sums, cnt = [], []
    for k in range(n):
        d = depth[k]
        if d == len(sums):
            sums.append(0)
            cnt.append(0)
        sums[d] += vals[k]
        cnt[d] += 1
        for c in (left[k], right[k]):
            if c != -1:
                depth[c] = d + 1
    return [s // c for s, c in zip(sums, cnt)]
''',
    tests=[[t] for t in BASE + [[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10], [10000, 9999, 1, 5, -1, 6]] + _big(8102)],
)


def _b_avg(tree):
    return [sum(x.v for x in lv) // len(lv) for lv in _levels(_build(tree))]


CHECKS["tree-level-averages-floored"] = (_b_avg, _gen(12, 30), "exact")
VALIDATE["tree-level-averages-floored"] = _v_trees

# ---------------------------------------------------------------- bottom-left value
add(
    id="deepest-row-leftmost-value", title="Leftmost Value in the Deepest Row", diff="Easy", topic="Trees", tier="extra",
    fn="bottomLeftValue", params=[("tree", "int[]")], ret="int", cmp="exact",
    desc="<p>Given a non-empty binary tree, look at its deepest level (the level furthest from the root). Return the value of the leftmost node on that level.</p>" + ENC +
         "<p>For <code>tree = [2, 1, 3, 4, -1, 5, 6, -1, -1, 7]</code> the deepest level contains only the node 7, so the answer is <code>7</code>. For <code>tree = [2, 1, 3]</code> the deepest level is <code>[1, 3]</code> and the answer is <code>1</code>.</p>",
    constraints=_cons(minn=1),
    hints=["Only the last level matters. How would you know which level is the last one?",
           "In a level-order array the levels appear one after the other, so the last real node belongs to the last level. But the leftmost node of that level is not necessarily near the end of the array.",
           "Track the depth of each node. Whenever you see a depth for the first time, remember that node's value as the leftmost of that depth. The remembered value of the largest depth is the answer."],
    editorial=["Do a breadth-first pass, left to right. The first node you meet on a new level is the leftmost node of that level. Overwrite your stored candidate every time a new level starts; after the last node has been processed the candidate belongs to the deepest level.",
               "A depth-first search works too (visit the left child first and record a value only when a strictly deeper level is reached), but the level-order array makes a single linear scan the simplest."],
    time="O(n)", space="O(n)",
    solution=LINKS + '''def bottomLeftValue(tree):
    vals, left, right = _links(tree)
    n = len(vals)
    depth = [0] * n
    answer = vals[0]
    seen = 0
    for k in range(n):
        d = depth[k]
        if d == seen:
            answer = vals[k]
            seen += 1
        for c in (left[k], right[k]):
            if c != -1:
                depth[c] = d + 1
    return answer
''',
    tests=[[t] for t in BASE1 + [[2, 1, 3, 4, -1, 5, 6, -1, -1, 7], [2, 1, 3], [1, 2, 3, 4, 5, 6, 7, 8, 9], [1, 2, 3, -1, 4, -1, 5, -1, -1, 6]] + _big(8103)],
)


def _b_bottom_left(tree):
    best = [-1, None]

    def go(x, d, first_left):
        if x is None:
            return
        if d > best[0]:
            best[0], best[1] = d, x.v
        go(x.l, d + 1, 0)
        go(x.r, d + 1, 0)

    go(_build(tree), 0, 0)
    return best[1]


CHECKS["deepest-row-leftmost-value"] = (_b_bottom_left, _gen(12, 30, minn=1), "exact")
VALIDATE["deepest-row-leftmost-value"] = lambda tests: _v_trees(tests, minn=1)

# ================================================================== MEDIUM

# ---------------------------------------------------------------- kth largest level sum
_pk = add(
    id="kth-largest-level-sum", title="K-th Largest Level Sum", diff="Medium", topic="Trees", tier="extra",
    fn="kthLargestLevelSum", params=[("tree", "int[]"), ("k", "int")], ret="int", cmp="exact",
    desc="<p>The <em>level sum</em> of a binary tree level is the sum of the values of all nodes on that level. Given a tree and an integer <code>k</code>, return the <code>k</code>-th largest level sum. Equal sums on different levels count separately (for sums 10, 10 and 4 the 2nd largest is 10 and the 3rd largest is 4). If the tree has fewer than <code>k</code> levels, return <code>-1</code>.</p>" + ENC +
         "<p>For <code>tree = [5, 8, 9, 2, 1, 3, 7, 4, 6]</code> the level sums are 5, 17, 13 and 10. With <code>k = 2</code> the answer is <code>13</code>, and with <code>k = 5</code> the answer is <code>-1</code>.</p>",
    constraints=_cons(["1 &le; k &le; 1,500"]),
    hints=["First reduce the tree to a list with one number per level.",
           "Compute each level's sum in one pass: a node's level is one more than its parent's level, and parents come before children in the array.",
           "Once you have the list of level sums, sort it in descending order and take position <code>k - 1</code>, or return <code>-1</code> when the list is shorter than <code>k</code>."],
    editorial=["Accumulate a sum per level while scanning the nodes in level order, then pick the k-th largest of those sums. Sorting the (at most n) sums costs O(L log L) with L the number of levels, so the total is O(n + L log L), and a heap of size k would give O(n + L log k).",
               "Remember that levels with equal sums are separate entries. Do not de-duplicate the sums, and check the length before indexing."],
    time="O(n + L log L)", space="O(n)",
    solution=LINKS + '''def kthLargestLevelSum(tree, k):
    vals, left, right = _links(tree)
    n = len(vals)
    depth = [0] * n
    sums = []
    for i in range(n):
        d = depth[i]
        if d == len(sums):
            sums.append(0)
        sums[d] += vals[i]
        for c in (left[i], right[i]):
            if c != -1:
                depth[c] = d + 1
    if len(sums) < k:
        return -1
    sums.sort(reverse=True)
    return sums[k - 1]
''',
    tests=[[[5, 8, 9, 2, 1, 3, 7, 4, 6], 2], [[5, 8, 9, 2, 1, 3, 7, 4, 6], 5], [[5, 8, 9, 2, 1, 3, 7, 4, 6], 1], [[], 1], [[7], 1], [[7], 2],
           [[1, 2, 3], 2], [[4, 4, -1, 4, -1, 4], 3], [[2, 5, 5, 1, 1, 1, 1], 2], [[2, 5, 5, 1, 1, 1, 1], 3], [[1, -1, 2, -1, 3, -1, 4], 4],
           [[10, 0, 0, 10, 10], 2], [[10, 0, 0, 10, 10], 3]],
)
_r = rnd(8104)
for _k, _mode in ((1, "random"), (7, "complete"), (11, "deep"), (1500, "left")):
    _pk["tests"].append([_tree(_r, MAXN, _mode, None, 0, MAXV), _k])


def _b_kth(tree, k):
    sums = sorted((sum(x.v for x in lv) for lv in _levels(_build(tree))), reverse=True)
    return sums[k - 1] if k <= len(sums) else -1


def _g_kth(r):
    return [_tree(r, r.randint(0, 12), r.choice(MODES), None, 0, 6), r.randint(1, 6)]


def _v_kth(tests):
    _v_trees(tests)
    for t in tests:
        assert 1 <= t["args"][1] <= MAXN


CHECKS["kth-largest-level-sum"] = (_b_kth, _g_kth, "exact")
VALIDATE["kth-largest-level-sum"] = _v_kth

# ---------------------------------------------------------------- min swaps to sort each level
_ps = add(
    id="min-swaps-to-sort-each-level", title="Minimum Swaps to Sort Every Level", diff="Medium", topic="Trees", tier="extra",
    fn="minSwapsPerLevel", params=[("tree", "int[]")], ret="int", cmp="exact",
    desc="<p>In one operation you may pick two nodes that are on the <em>same level</em> of the tree and swap their values (the shape of the tree never changes). Return the minimum total number of operations needed so that on every level the values, read from left to right, are in strictly increasing order.</p>"
         "<p>All node values of the tree are distinct, so the order inside a level is well defined. The empty tree needs <code>0</code> operations.</p>" + ENC +
         "<p>For <code>tree = [1, 4, 3, 7, 6, 8, 5, -1, -1, -1, -1, 9, -1, 10]</code> the levels are <code>[1]</code>, <code>[4, 3]</code>, <code>[7, 6, 8, 5]</code> and <code>[9, 10]</code>. They need 0, 1, 2 and 0 swaps, so the answer is <code>3</code>.</p>",
    constraints=_cons(["All node values are distinct"]),
    hints=["Swaps never move a value to another level, so every level can be solved on its own and the answers added.",
           "For one level, compare the current order with the sorted order. Every value has a target position; follow value &rarr; target position &rarr; the value that sits there &rarr; and so on.",
           "These chains form cycles. A cycle of length <code>c</code> can be fixed with exactly <code>c - 1</code> swaps, and no fewer. So the cost of a level is its length minus its number of cycles."],
    editorial=["Different levels are independent: a swap on one level never helps another. For a single level with values <code>a[0..m-1]</code>, sort the indices by value to get the target position of each element. This defines a permutation, which splits into disjoint cycles. A cycle of length 1 is already in place; a cycle of length <code>c &gt; 1</code> needs <code>c - 1</code> swaps (each swap can put at most one extra element in its final place, and the last swap fixes two). Hence the minimum number of swaps for the level is <code>m - (number of cycles)</code>.",
               "Computing the levels takes O(n), and sorting each level costs O(m log m), so the whole solution is O(n log n). Distinct values are what make the target positions unique."],
    time="O(n log n)", space="O(n)",
    solution=LINKS + '''def minSwapsPerLevel(tree):
    vals, left, right = _links(tree)
    n = len(vals)
    depth = [0] * n
    levels = []
    for k in range(n):
        d = depth[k]
        if d == len(levels):
            levels.append([])
        levels[d].append(vals[k])
        for c in (left[k], right[k]):
            if c != -1:
                depth[c] = d + 1
    total = 0
    for lv in levels:
        m = len(lv)
        order = sorted(range(m), key=lambda i: lv[i])
        seen = [False] * m
        for i in range(m):
            if not seen[i]:
                j = i
                length = 0
                while not seen[j]:
                    seen[j] = True
                    j = order[j]
                    length += 1
                total += length - 1
    return total
''',
    tests=[[t] for t in [[], [0], [1, 3, 2], [2, 1, 3], [1, 4, 3, 7, 6, 8, 5, -1, -1, -1, -1, 9, -1, 10],
                         [9, 8, 7, 6, 5, 4, 3, 2, 1], [1, 2, 3, 4, 5, 6, 7], [7, 6, 5, 4, 3, 2, 1],
                         [10, 5, 8, 4, 3, 6, 9, 7, 0, 2, 1]]
           + [_perm_tree(8105, MAXN, "complete"), _perm_tree(8106, MAXN, "random"), _perm_tree(8107, MAXN, "shallow")]],
)


def _b_swaps(tree):
    total = 0
    for lv in _levels(_build(tree)):
        a = [x.v for x in lv]
        for i in range(len(a)):             # selection sort: one swap per misplaced position
            j = a.index(min(a[i:]), i)
            if j != i:
                a[i], a[j] = a[j], a[i]
                total += 1
    return total


CHECKS["min-swaps-to-sort-each-level"] = (_b_swaps, _gen(14, 60, distinct=True), "exact")
VALIDATE["min-swaps-to-sort-each-level"] = lambda tests: _v_trees(tests, distinct=True)

# ---------------------------------------------------------------- top view
_VIEW_TEXT = (
    "<p>Give every node a <em>column</em>: the root is in column <code>0</code>, the left child of a node in column <code>c</code> is in column <code>c - 1</code> and its right child is in column <code>c + 1</code>. "
    "Imagine every column as a vertical line.</p>"
)
add(
    id="binary-tree-top-view", title="Top View of a Binary Tree", diff="Medium", topic="Trees", tier="common",
    fn="topView", params=[("tree", "int[]")], ret="int[]", cmp="exact",
    desc="<p>Looking at a binary tree from above, each vertical line shows only the highest node on it; nodes lower on the same line are hidden underneath. Return the values of the visible nodes ordered from the leftmost column to the rightmost column.</p>" + _VIEW_TEXT +
         "<p>In each column, the visible node is the one closest to the root (smallest level). If two nodes of one column are on the same level, the left one is visible (it comes first in level order). The empty tree gives <code>[]</code>.</p>" + ENC +
         "<p>For <code>tree = [1, 2, 3, 4, 5, 6, 7]</code> the columns are -2: {4}, -1: {2}, 0: {1, 5, 6}, 1: {3}, 2: {7}. Column 0 shows the root 1, so the answer is <code>[4, 2, 1, 3, 7]</code>.</p>",
    constraints=_cons(),
    hints=["Compute the column of every node first. Which tree traversal gives you nodes closest to the root first?",
           "In level order, a node is met before every node that lies deeper, and nodes on one level are met left to right. So the first node met in a column is exactly the visible one.",
           "Store <code>col[child] = col[parent] &plusmn; 1</code> while scanning the array. Keep a dictionary column &rarr; value and only write the value if the column is new. Finally output the dictionary values sorted by column."],
    editorial=["Do a level-order traversal and carry each node's column along with it. A column's visible node is the first node met in that column: level order visits nodes level by level, left to right, so the first one has the smallest level and, among equals, is the leftmost. Record it once and ignore later nodes of the same column.",
               "A depth-first search is also possible, but then you must compare levels explicitly (and break ties by left-to-right position), so the level-order scan is simpler. Sorting the columns at the end costs O(c log c), where c is the number of columns; since columns are consecutive integers, the minimum and the maximum column are enough to avoid sorting."],
    time="O(n)", space="O(n)",
    solution=LINKS + '''def topView(tree):
    vals, left, right = _links(tree)
    n = len(vals)
    if n == 0:
        return []
    col = [0] * n
    first = {}
    for k in range(n):
        if col[k] not in first:
            first[col[k]] = vals[k]
        if left[k] != -1:
            col[left[k]] = col[k] - 1
        if right[k] != -1:
            col[right[k]] = col[k] + 1
    return [first[c] for c in range(min(first), max(first) + 1)]
''',
    tests=[[t] for t in BASE + [[1, 2, 3, 4, -1, -1, 5, -1, -1, 6, 7], [1, 2, 3, -1, 4, 5, -1, -1, 6]]
           + _big(8108, hi=1000, shapes=("random", "complete", "zig"))],
)


def _walk_cols(root):
    """(column, level, heap_index, value) of every node, found by recursion (heap index: root 1, children 2i and 2i+1)."""
    out = []

    def go(x, c, d, h):
        if x is None:
            return
        out.append((c, d, h, x.v))
        go(x.l, c - 1, d + 1, 2 * h)
        go(x.r, c + 1, d + 1, 2 * h + 1)

    go(root, 0, 0, 1)
    return out


def _b_top(tree):
    best = {}
    for c, d, h, v in _walk_cols(_build(tree)):
        if c not in best or (d, h) < best[c][0]:
            best[c] = ((d, h), v)
    return [best[c][1] for c in sorted(best)]


CHECKS["binary-tree-top-view"] = (_b_top, _gen(14, 30), "exact")
VALIDATE["binary-tree-top-view"] = _v_trees

# ---------------------------------------------------------------- bottom view
add(
    id="binary-tree-bottom-view", title="Bottom View of a Binary Tree", diff="Medium", topic="Trees", tier="extra",
    fn="bottomView", params=[("tree", "int[]")], ret="int[]", cmp="exact",
    desc="<p>Looking at a binary tree from below, each vertical line shows only the lowest node on it. Return the values of the visible nodes ordered from the leftmost column to the rightmost column.</p>" + _VIEW_TEXT +
         "<p>In each column, the visible node is the one furthest from the root (largest level). If two nodes of one column are on the same, deepest, level, the right one is visible (it comes last in level order). The empty tree gives <code>[]</code>.</p>" + ENC +
         "<p>For <code>tree = [1, 2, 3, 4, 5, 6, 7]</code> column 0 contains the nodes 1, 5 and 6; the nodes 5 and 6 are both on the deepest level of that column, and 6 is the right one. The answer is <code>[4, 2, 6, 3, 7]</code>.</p>",
    constraints=_cons(),
    hints=["Again you need the column of every node. What decides which node of a column is visible now?",
           "The visible node is the last node of its column in level order: deeper levels come later, and on one level nodes come left to right.",
           "While scanning the array in order, keep a dictionary column &rarr; value and <em>overwrite</em> it every time you see the column. Output the values sorted by column."],
    editorial=["Mirror image of the top view logic. Scan the nodes in level order while propagating columns from parents to children (left child: column - 1, right child: column + 1). Because level order visits shallow nodes before deep ones and left nodes before right ones on a level, the last node written for a column is the deepest and, among the deepest, the rightmost, which is exactly the node that is visible from below.",
               "So the only change relative to the top view is that every node overwrites the stored value instead of being ignored. The time is O(n) plus the output ordering over the (consecutive) columns."],
    time="O(n)", space="O(n)",
    solution=LINKS + '''def bottomView(tree):
    vals, left, right = _links(tree)
    n = len(vals)
    if n == 0:
        return []
    col = [0] * n
    last = {}
    for k in range(n):
        last[col[k]] = vals[k]
        if left[k] != -1:
            col[left[k]] = col[k] - 1
        if right[k] != -1:
            col[right[k]] = col[k] + 1
    return [last[c] for c in range(min(last), max(last) + 1)]
''',
    tests=[[t] for t in BASE + [[1, 2, 3, 4, -1, -1, 5, -1, -1, 6, 7], [20, 8, 22, 5, 3, 4, 25, -1, -1, 10, 14]]
           + _big(8109, hi=1000, shapes=("random", "shallow", "right"))],
)


def _b_bottom(tree):
    best = {}
    for c, d, h, v in _walk_cols(_build(tree)):
        if c not in best or (d, h) > best[c][0]:
            best[c] = ((d, h), v)
    return [best[c][1] for c in sorted(best)]


CHECKS["binary-tree-bottom-view"] = (_b_bottom, _gen(14, 30), "exact")
VALIDATE["binary-tree-bottom-view"] = _v_trees

# ---------------------------------------------------------------- widest level
add(
    id="widest-tree-level", title="Widest Level of a Binary Tree", diff="Medium", topic="Trees", tier="common",
    fn="widestLevel", params=[("tree", "int[]")], ret="int", cmp="exact",
    desc="<p>Imagine the tree drawn on a complete binary tree frame: the root has slot <code>1</code>, and a node in slot <code>p</code> has its left child in slot <code>2p</code> and its right child in slot <code>2p + 1</code>. The <em>width</em> of a level is <code>(slot of its rightmost node) - (slot of its leftmost node) + 1</code>, so missing nodes between the two ends count too. Return the largest width over all levels. The empty tree has width <code>0</code>.</p>" + ENC +
         "<p>For <code>tree = [1, 3, 2, 5, 3, -1, 9]</code> the last level has nodes in slots 4, 5 and 7, so its width is 7 - 4 + 1 = <code>4</code>.</p>",
    constraints=_cons([f"The tree has at most {MAXLV} levels, so every width fits in a 32-bit integer"]),
    hints=["Only the leftmost and the rightmost node of every level matter for the width of that level.",
           "Give every node a slot number: <code>2p</code> for a left child and <code>2p + 1</code> for a right child. Slots on the same level are comparable, so the width is the largest minus the smallest slot plus one.",
           "Process nodes in level order and keep the minimum and maximum slot per level. In Python integers are unbounded; in other languages subtract the first slot of the level to keep numbers small."],
    editorial=["Slot numbering turns the picture of the complete binary tree into arithmetic. On any level the slots of different nodes are different, and the order of slots equals the left-to-right order, so the first node met on a level has the smallest slot and the last one the largest. The width of the level is their difference plus one.",
               "Scan the nodes in level order, store the slot of every node, and keep for each level its first and last slot. The answer is the maximum of <code>last - first + 1</code>. Slots grow like 2<sup>depth</sup>, which is why the number of levels is limited here; in a language with fixed-width integers subtract the first slot of the level before doubling (re-basing each level) to stay safe on deep trees."],
    time="O(n)", space="O(n)",
    solution=LINKS + '''def widestLevel(tree):
    vals, left, right = _links(tree)
    n = len(vals)
    if n == 0:
        return 0
    pos = [0] * n
    depth = [0] * n
    pos[0] = 1
    lo, hi = [], []
    for k in range(n):
        d = depth[k]
        if d == len(lo):
            lo.append(pos[k])
            hi.append(pos[k])
        else:
            hi[d] = pos[k]
        if left[k] != -1:
            pos[left[k]] = 2 * pos[k]
            depth[left[k]] = d + 1
        if right[k] != -1:
            pos[right[k]] = 2 * pos[k] + 1
            depth[right[k]] = d + 1
    return max(h - l + 1 for l, h in zip(lo, hi))
''',
    tests=[[t] for t in BASE + [[1, 3, 2, 5, 3, -1, 9], [1, 3, 2, 5, -1, -1, 9, 6, -1, 7], [1, 3, -1, 5, 3], [1, 3, 2, 5],
                               [1, 1, 1, 1, -1, -1, 1, 1, -1, -1, -1, -1, 1]]
           + _big(8110, cap=MAXLV, shapes=("complete", "deep"))
           + [_two_chains(rnd(8111), 29, 1200), _two_chains(rnd(8112), 30, 100)]],
)


def _b_widest(tree):
    best = {}
    for c, d, h, v in _walk_cols(_build(tree)):
        lo, hi = best.get(d, (h, h))
        best[d] = (min(lo, h), max(hi, h))
    return max((hi - lo + 1 for lo, hi in best.values()), default=0)


CHECKS["widest-tree-level"] = (_b_widest, _gen(14, 30), "exact")
VALIDATE["widest-tree-level"] = lambda tests: _v_trees(tests, cap=MAXLV)

# ---------------------------------------------------------------- cousin sums
add(
    id="replace-with-cousin-sums", title="Replace Every Value with the Sum of Its Cousins", diff="Medium", topic="Trees", tier="extra",
    fn="replaceWithCousinSums", params=[("tree", "int[]")], ret="int[]", cmp="exact",
    desc="<p>Two nodes are <em>cousins</em> if they are on the same level but have different parents. Build a new tree with the same shape in which the value of every node is replaced by the sum of the <em>original</em> values of all its cousins (0 if it has none). The root has no cousins, and neither do its children, so they become 0.</p>"
         "<p>Return the new tree in the same level-order encoding, with <code>-1</code> kept at exactly the same positions as in the input.</p>" + ENC +
         "<p>For <code>tree = [5, 4, 9, 1, 10, -1, 7]</code> the third level is <code>[1, 10, 7]</code>, where 1 and 10 share the parent 4. Node 1 has the single cousin 7, node 10 also has the cousin 7, and node 7 has the cousins 1 and 10. The answer is <code>[0, 0, 0, 7, 7, -1, 11]</code>.</p>",
    constraints=_cons(),
    hints=["For a node, cousins = (all nodes on its level) minus (the node and its siblings).",
           "So you need two kinds of sums: the total of each level, and for every parent the total of its children.",
           "New value of a node = <code>levelSum[depth] - childrenSum[parent]</code>. The root has no parent and simply becomes 0."],
    editorial=["Counting cousins directly would be quadratic on wide levels. Instead use subtraction: the cousins of a node are all nodes of its level except the ones that share its parent (the node itself and its sibling, if any). With the level total <code>S[d]</code> and the sum <code>C[p]</code> of the values of the children of parent <code>p</code>, the new value is <code>S[d] - C[p]</code>.",
               "Compute <code>S</code> and <code>C</code> in one pass over the array (parents precede children), then write the new values in a second pass. The input values are the original ones in both passes, so no cousin sum can contaminate another. Time O(n)."],
    time="O(n)", space="O(n)",
    solution=LINKS + '''def replaceWithCousinSums(tree):
    vals, left, right = _links(tree)
    n = len(vals)
    depth = [0] * n
    parent = [0] * n
    level_sum = []
    kids = [0] * n
    for k in range(n):
        d = depth[k]
        if d == len(level_sum):
            level_sum.append(0)
        level_sum[d] += vals[k]
        for c in (left[k], right[k]):
            if c != -1:
                depth[c] = d + 1
                parent[c] = k
                kids[k] += vals[c]
    new = [0] + [level_sum[depth[k]] - kids[parent[k]] for k in range(1, n)] if n else []
    out = []
    k = 0
    for x in tree:
        if x == -1:
            out.append(-1)
        else:
            out.append(new[k])
            k += 1
    return out
''',
    tests=[[t] for t in BASE + [[5, 4, 9, 1, 10, -1, 7], [1, 2, 3, 4, -1, 5, 6, 7, 8, 9, 10]] + _big(8113, hi=MAXV, shapes=("random", "complete", "deep"))],
)


def _b_cousin(tree):
    root = _build(tree)
    rows = {}

    def go(x, d, par):
        if x is None:
            return
        rows.setdefault(d, []).append((x, par))
        go(x.l, d + 1, x)
        go(x.r, d + 1, x)

    go(root, 0, None)
    new = {}
    for d, lst in rows.items():
        for x, par in lst:
            new[id(x)] = sum(y.v for y, q in lst if q is not par)
    out = []
    q = deque([root] if root else [])
    nodes_in_order = []
    while q:
        x = q.popleft()
        nodes_in_order.append(x)
        for c in (x.l, x.r):
            if c:
                q.append(c)
    it = iter(nodes_in_order)
    for v in tree:
        out.append(-1 if v == -1 else new[id(next(it))])
    return out


CHECKS["replace-with-cousin-sums"] = (_b_cousin, _gen(14, 30), "exact")
VALIDATE["replace-with-cousin-sums"] = _v_trees

# ================================================================== HARD

# ---------------------------------------------------------------- widest level with child swaps
_pf = add(
    id="widest-level-after-child-swaps", title="Widest Level After Swapping Children", diff="Hard", topic="Trees", tier="extra",
    fn="widestAfterSwaps", params=[("tree", "int[]")], ret="int", cmp="exact",
    desc="<p>Place a binary tree on a complete binary tree frame: the root has slot <code>1</code>, and a node in slot <code>p</code> has its left child in slot <code>2p</code> and its right child in slot <code>2p + 1</code>. The <em>width of a level</em> is <code>(slot of its rightmost node) - (slot of its leftmost node) + 1</code> (missing nodes between the ends count), and the <em>width of the tree</em> is the largest width of any level. The empty tree has width <code>0</code>.</p>"
         "<p>Before measuring, you may pick any set of nodes and, for each picked node, swap its left and right child (a missing child is swapped too, so a lone left child can become a lone right child). A swap moves the complete subtrees. Return the largest tree width that can be reached.</p>" + ENC +
         "<p>For <code>tree = [1, 2, 3, 4, -1, 5, -1, 6, -1, 7]</code> (two chains hanging below the root) the last level holds the nodes 6 and 7 in slots 8 and 12, so the width is 5. Swapping the children of node 3 and of node 5 moves 7 to slot 15, giving width 8, and no arrangement does better, so the answer is <code>8</code>. For <code>tree = [1, 2, -1, 3]</code>, a single path, every level has one node and the answer is <code>1</code>.</p>",
    constraints=_cons([f"The tree has at most {MAXLV} levels, so every width fits in a 32-bit integer"]),
    hints=["A wide level needs two far apart nodes on one level. Where do the paths from the root to two such nodes separate?",
           "Let the two nodes separate at a node <code>a</code> that has children in both directions. Below <code>a</code> the two paths share no node, so you can choose the swaps on them independently: swapping at <code>a</code> puts one node to the left side, and swaps further down can push that node to the far left of its half and the other to the far right of its half.",
           "If both nodes are <code>k</code> levels below <code>a</code>, the width is exactly <code>2<sup>k</sup></code> (from the leftmost to the rightmost slot below <code>a</code> on that level), independent of everything above <code>a</code>. The deepest common level below <code>a</code> is limited by the shorter of its two child subtrees."],
    editorial=["Take any level and two of its nodes <code>u</code> and <code>v</code>, and let <code>a</code> be their lowest common ancestor, <code>k</code> levels above them. The slots of <code>u</code> and <code>v</code> agree on all bits that come from the path root &rarr; <code>a</code>; after that, <code>u</code> goes into one child subtree of <code>a</code> and <code>v</code> into the other, and then each follows a path made of choices that belong to nodes only on its own side. Using the swap at <code>a</code> we put <code>u</code> on the left, and swaps along the path of <code>u</code> make every step go left (any node on the path has at most one child on that path, and a swap decides whether it is the left or the right one), so <code>u</code> gets the smallest possible slot <code>A &middot; 2<sup>k</sup></code>. In the same way <code>v</code> gets the largest slot <code>A &middot; 2<sup>k</sup> + 2<sup>k</sup> - 1</code>. The width of the level is therefore exactly <code>2<sup>k</sup></code>, whatever the shape above <code>a</code>.",
               "So we want a node <code>a</code> with two children and the largest <code>k</code> such that both child subtrees reach <code>k - 1</code> edges below the children. With <code>h(x)</code> the height of the subtree of x in edges, the best value for <code>a</code> is <code>k = 1 + min(h(left), h(right))</code>. The answer is <code>2<sup>1 + M</sup></code> with <code>M</code> the maximum of <code>min(h(left), h(right))</code> over all nodes that have two children. If no node has two children the tree is a single path and every level has one node, so the answer is 1 (and 0 for the empty tree). Heights come from one backwards pass over the level-order array, so the time is O(n)."],
    time="O(n)", space="O(n)",
    solution=LINKS + '''def widestAfterSwaps(tree):
    vals, left, right = _links(tree)
    n = len(vals)
    if n == 0:
        return 0
    height = [0] * n
    for k in range(n - 1, -1, -1):
        for c in (left[k], right[k]):
            if c != -1:
                height[k] = max(height[k], height[c] + 1)
    best = -1
    for k in range(n):
        if left[k] != -1 and right[k] != -1:
            best = max(best, min(height[left[k]], height[right[k]]))
    return 1 << (best + 1)
''',
    tests=[[t] for t in BASE + [[1, 2, 3, 4, -1, 5, -1, 6, -1, 7], [1, 2, -1, 3], [1, 2, 3, 4], [1, -1, 2, -1, 3, -1, 4],
                               [1, 2, 3, 4, 5, -1, -1, 6, -1, -1, 7]]
           + _big(8114, cap=MAXLV, shapes=("random", "deep", "shallow"))
           + [_two_chains(rnd(8118), 30, 40)]],
)


def _b_swaps_width(tree):
    root = _build(tree)
    if root is None:
        return 0
    nodes = [x for lv in _levels(root) for x in lv]
    best = 0
    for mask in range(1 << len(nodes)):
        for i, x in enumerate(nodes):
            if mask >> i & 1:
                x.l, x.r = x.r, x.l
        slots = {}

        def go(x, d, p):
            if x is None:
                return
            lo, hi = slots.get(d, (p, p))
            slots[d] = (min(lo, p), max(hi, p))
            go(x.l, d + 1, 2 * p)
            go(x.r, d + 1, 2 * p + 1)

        go(root, 0, 1)
        best = max(best, max(hi - lo + 1 for lo, hi in slots.values()))
        for i, x in enumerate(nodes):
            if mask >> i & 1:
                x.l, x.r = x.r, x.l
    return best


CHECKS["widest-level-after-child-swaps"] = (_b_swaps_width, _gen(10, 30), "exact")
VALIDATE["widest-level-after-child-swaps"] = lambda tests: _v_trees(tests, cap=MAXLV)

# ---------------------------------------------------------------- width after cutting one subtree
_pc = add(
    id="tree-width-after-subtree-cut", title="Narrowest Tree After Cutting One Subtree", diff="Hard", topic="Trees", tier="extra",
    fn="minWidthAfterCut", params=[("tree", "int[]")], ret="int", cmp="exact",
    desc="<p>Place a binary tree on a complete binary tree frame: the root has slot <code>1</code>, and a node in slot <code>p</code> has its left child in slot <code>2p</code> and its right child in slot <code>2p + 1</code>. The <em>width of a level</em> is <code>(slot of its rightmost node) - (slot of its leftmost node) + 1</code> (missing nodes between the ends count), and the <em>width of the tree</em> is the largest width of any level.</p>"
         "<p>You must choose exactly one node other than the root and cut it off together with its whole subtree. The remaining nodes keep their slots. Return the smallest tree width that can be reached by a single cut.</p>" + ENC +
         "<p>For <code>tree = [1, 2, 3, 4, 5, 6, 7]</code> the width is 4 (the last level, slots 4 to 7). Cutting node 4 leaves the slots 5, 6, 7 on the last level (width 3). Cutting node 2 removes 2, 4 and 5 and leaves the nodes 1, 3, 6, 7, whose levels have widths 1, 1 and 2, so the answer is <code>2</code>. For <code>tree = [1, 2, 3, 4, -1, -1, 5]</code> the last level has slots 4 and 7 (width 4); cutting node 2 together with its child 4 leaves the single path 1, 3, 5, so the answer is <code>1</code>.</p>",
    constraints=_cons(["2 &le; number of nodes", f"The tree has at most {MAXLV} levels, so every width fits in a 32-bit integer"]),
    hints=["Try every node as the one to cut, and think about how the widths of the levels change. Which levels are not affected at all?",
           "Levels above the cut node keep their width. On every level below, the cut removes one contiguous block of nodes (the descendants of the cut node), and the width changes only if that block touches the left end or the right end of the level.",
           "The descendants of a node on the next level form a block of consecutive positions that you can get from prefix counts of children. Walk down level by level while updating the block; the number of levels is at most 30, so O(n &middot; levels) work is fine. Use prefix and suffix maxima of the original level widths for the levels above the cut and below the point where the block becomes empty."],
    editorial=["Cutting a node removes, on each level below it, a contiguous block of nodes of that level (all the descendants of the cut node on that level, which stay together because levels are ordered left to right). If the block is strictly inside the level (there are nodes remaining on both sides), the leftmost and rightmost slots are unchanged, hence the width is unchanged. If the block contains the left end, the new width is measured from the first remaining node; symmetric for the right end; if the block is the whole level, the level disappears.",
               "Index the nodes of each level 0..m-1 and store for each level the number of children produced by the first <code>i</code> nodes, <code>childrenBefore[i]</code>. Then the descendants of the block <code>[a, b]</code> on the next level are exactly the block <code>[childrenBefore[a], childrenBefore[b+1] - 1]</code>. For a cut node, start with its own one-element block on its level and walk down while the block is non-empty, recording the new width of each level. Levels above the cut are covered by a prefix maximum of the original widths, and once the block becomes empty the remaining deeper levels keep their original widths (a suffix maximum). The answer is the minimum over all cut nodes. Each node walks down at most as many levels as the tree has (at most 30), so the total time is O(n &middot; L)."],
    time="O(n * L)", space="O(n)",
    solution=LINKS + '''def minWidthAfterCut(tree):
    vals, left, right = _links(tree)
    n = len(vals)
    depth = [0] * n
    pos = [0] * n
    idx = [0] * n
    pos[0] = 1
    levels = []
    for k in range(n):
        d = depth[k]
        if d == len(levels):
            levels.append([])
        idx[k] = len(levels[d])
        levels[d].append(k)
        if left[k] != -1:
            depth[left[k]] = d + 1
            pos[left[k]] = 2 * pos[k]
        if right[k] != -1:
            depth[right[k]] = d + 1
            pos[right[k]] = 2 * pos[k] + 1
    H = len(levels)
    W = [pos[lv[-1]] - pos[lv[0]] + 1 for lv in levels]
    prefix = [0] * (H + 1)          # prefix[d] = widest of levels 0..d-1
    for d in range(H):
        prefix[d + 1] = max(prefix[d], W[d])
    suffix = [0] * (H + 1)          # suffix[d] = widest of levels d..H-1
    for d in range(H - 1, -1, -1):
        suffix[d] = max(suffix[d + 1], W[d])
    before = []                     # before[d][i] = children of the first i nodes of level d
    for d in range(H):
        acc = [0]
        for k in levels[d]:
            acc.append(acc[-1] + (left[k] != -1) + (right[k] != -1))
        before.append(acc)
    best = None
    for v in range(1, n):
        d = depth[v]
        a = b = idx[v]
        cur = prefix[d]
        lvl = d
        while lvl < H:
            if a > b:
                cur = max(cur, suffix[lvl])
                break
            lv = levels[lvl]
            m = len(lv)
            if a > 0 and b < m - 1:
                w = W[lvl]
            elif a > 0:
                w = pos[lv[a - 1]] - pos[lv[0]] + 1
            elif b < m - 1:
                w = pos[lv[-1]] - pos[lv[b + 1]] + 1
            else:
                w = 0
            cur = max(cur, w)
            a, b = before[lvl][a], before[lvl][b + 1] - 1
            lvl += 1
        if best is None or cur < best:
            best = cur
    return best
''',
    tests=[[t] for t in [[1, 2, 3, 4, 5, 6, 7], [1, 2, 3, 4, -1, -1, 5], [1, 2], [1, -1, 2], [1, 2, 3], [1, 2, 3, 4, 5],
                         [1, 2, 3, -1, 4, 5, -1, -1, 6, 7], [1, 2, 3, 4, -1, -1, 5, 6, -1, -1, 7, 8, -1, -1, 9],
                         [3, 9, 20, -1, -1, 15, 7], [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]]]
           + [[_two_chains(rnd(8115), 25, 900)], [_tree(rnd(8116), MAXN, "random", MAXLV)], [_tree(rnd(8117), MAXN, "complete", MAXLV)]],
)


def _b_cut(tree):
    def width(root, banned):
        slots = {}

        def go(x, d, p):
            if x is None or x is banned:
                return
            lo, hi = slots.get(d, (p, p))
            slots[d] = (min(lo, p), max(hi, p))
            go(x.l, d + 1, 2 * p)
            go(x.r, d + 1, 2 * p + 1)

        go(root, 0, 1)
        return max(hi - lo + 1 for lo, hi in slots.values())

    root = _build(tree)
    cands = [x for lv in _levels(root)[1:] for x in lv]
    return min(width(root, x) for x in cands)


CHECKS["tree-width-after-subtree-cut"] = (_b_cut, _gen(14, 30, minn=2, cap=MAXLV), "exact")
VALIDATE["tree-width-after-subtree-cut"] = lambda tests: _v_trees(tests, minn=2, cap=MAXLV)
