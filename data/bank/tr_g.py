"""Problems: trees, tree DP (subtree optimization, independent sets, matching, coverage, coin distribution).

Tree encoding used by every problem here: level-order int[], -1 for a missing child,
children of missing nodes are not listed, trailing -1s are dropped. Real node values are never negative.
"""
from collections import Counter, deque
from itertools import combinations

from lib import add, rnd, CHECKS, VALIDATE, gen_arr  # noqa: F401

TOPIC = "Trees"
MOD = 10 ** 9 + 7

_ENC = (
    "<p><strong>How trees are given.</strong> A binary tree is passed as an integer array in level order (top to bottom, "
    "left to right). The first entry is the root. After that, the left and right child of every existing node are written in turn; "
    "a missing child is written as <code>-1</code> (real node values are never negative). Missing nodes have no children listed, "
    "and trailing <code>-1</code> entries are dropped.</p>"
    "<p>For example, <code>[1,2,3,-1,4]</code> is the tree whose root <code>1</code> has children <code>2</code> and <code>3</code>; "
    "node <code>2</code> has no left child and has <code>4</code> as its right child; node <code>3</code> is a leaf.</p>"
)


# ------------------------------------------------------------------ helpers (tests and brute forces only)
def _node(v=0):
    return [v, None, None]  # value, left, right


def _ser(root):
    out = []
    q = deque([root])
    while q:
        nd = q.popleft()
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
    q = deque([root])
    i = 1
    while q and i < len(arr):
        nd = q.popleft()
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
    """Nodes in level order (the same numbering as the array encoding)."""
    out = [root]
    h = 0
    while h < len(out):
        nd = out[h]
        h += 1
        for s in (1, 2):
            if nd[s] is not None:
                out.append(nd[s])
    return out


def _edges(root):
    """(values, parent index list with -1 for the root, edge list) with nodes numbered in level order."""
    nodes = _nodes(root)
    idx = {id(nd): i for i, nd in enumerate(nodes)}
    par = [-1] * len(nodes)
    ed = []
    for nd in nodes:
        for s in (1, 2):
            if nd[s] is not None:
                par[idx[id(nd[s])]] = idx[id(nd)]
                ed.append((idx[id(nd)], idx[id(nd[s])]))
    return [nd[0] for nd in nodes], par, ed


def _shape(r, n, deep=0.0):
    """Random binary tree with n nodes, all values 0. `deep` biases growth towards the newest nodes."""
    root = _node()
    slots = [(root, 1), (root, 2)]
    for _ in range(n - 1):
        if deep and r.random() < deep:
            j = len(slots) - 1 - r.randint(0, min(1, len(slots) - 1))
        else:
            j = r.randrange(len(slots))
        slots[j], slots[-1] = slots[-1], slots[j]
        par, side = slots.pop()
        c = _node()
        par[side] = c
        slots.append((c, 1))
        slots.append((c, 2))
    return root


def _chain(n, mode, r=None):
    """Path-shaped tree: 'L', 'R', 'Z' (zigzag) or 'X' (random sides)."""
    root = _node()
    cur = root
    for i in range(n - 1):
        s = {"L": 1, "R": 2, "Z": 1 + (i % 2), "X": (r.choice((1, 2)) if r else 1)}[mode]
        c = _node()
        cur[s] = c
        cur = c
    return root


def _perfect(h):
    if h == 0:
        return None
    nd = _node()
    nd[1] = _perfect(h - 1)
    nd[2] = _perfect(h - 1)
    return nd


def _fill(r, root, lo, hi):
    for nd in _nodes(root):
        nd[0] = r.randint(lo, hi)
    return root


def _chk_tree(arr, nmin, nmax, vmax):
    assert all(isinstance(x, int) and -1 <= x <= vmax for x in arr), "bad entry"
    assert arr and arr[-1] != -1, "empty or trailing -1"
    assert _ser(_parse(arr)) == arr, "tree array is not canonical"
    cnt = sum(1 for x in arr if x != -1)
    assert nmin <= cnt <= nmax, ("node count", cnt)


def _small(r, lo=1, hi=9):
    return _shape(r, r.randint(lo, hi), r.choice([0, 0.5]))


_PARSE_SRC = '''def parse(tree):
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

# =================================================================== EASY

p = add(
    id="binary-tree-tilt-total", title="Total Tilt of a Binary Tree", diff="Easy", topic=TOPIC, tier="common",
    fn="treeTilt", params=[("tree", "int[]")], ret="int", cmp="exact",
    desc="<p>The <em>tilt</em> of a node is the absolute difference between the sum of all values in its left subtree and the sum of all values in its right subtree. A missing subtree counts as a sum of <code>0</code>. The node's own value is not part of its tilt.</p>"
         "<p>Return the sum of the tilts of <strong>all</strong> nodes of the tree.</p>"
         + _ENC +
         "<p><strong>Example 1</strong></p><pre>tree = [1,2,3]\nOutput: 1\nThe root has tilt |2 - 3| = 1; both leaves have tilt 0.</pre>"
         "<p><strong>Example 2</strong></p><pre>tree = [4,2,9,3,5,-1,7]\nOutput: 15\nNode 2 has tilt |3 - 5| = 2, node 9 has tilt |0 - 7| = 7, the root has tilt |10 - 16| = 6, the leaves have tilt 0.</pre>",
    constraints=["1 &le; number of nodes &le; 3,000", "0 &le; node value &le; 100", "The array follows the encoding above exactly"],
    hints=["To know a node's tilt you need the total value of each child subtree. Computing each of those from scratch for every node is slow on tall trees.",
           "Compute subtree sums bottom-up: the sum of a subtree is the node's value plus the sums of its two child subtrees. While you do that, the two child sums are exactly the numbers the tilt needs.",
           "In the level-order numbering every child has a larger index than its parent, so looping over nodes from the last index to the first processes children before parents without recursion."],
    editorial=["Define <code>S(u)</code> as the sum of all values in the subtree of <code>u</code>. Then <code>S(u) = val[u] + S(left) + S(right)</code> and the tilt of <code>u</code> is <code>|S(left) - S(right)|</code>. A single bottom-up pass computes both at every node, so each node is touched once.",
               "Recomputing the subtree sums separately for every node costs O(n) per node, O(n<sup>2</sup>) on a chain. The bottom-up pass is O(n) time and O(n) memory (O(h) with recursion). The answer is at most about 4.5 * 10<sup>8</sup> here, so it fits in 32 bits."],
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


def treeTilt(tree):
    val, left, right = parse(tree)
    n = len(val)
    s = val[:]
    total = 0
    for u in range(n - 1, -1, -1):
        a = s[left[u]] if left[u] != -1 else 0
        b = s[right[u]] if right[u] != -1 else 0
        total += abs(a - b)
        s[u] = val[u] + a + b
    return total
''',
    tests=[[[1, 2, 3]], [[4, 2, 9, 3, 5, -1, 7]], [[5]], [[0, 0]], [[7, -1, 3]], [[1, 2, -1, 3, -1, 4]], [[100, 100, 100, 100, 100, 100, 100]],
           [[10, 0, 0, 0, 0, 5, 5]], [[3, 1, 2, 1, 1, 2, 2, 1, 1]]],
)
_r = rnd(7001)
p["tests"].append([_ser(_fill(_r, _shape(_r, 3000), 0, 100))])
p["tests"].append([_ser(_fill(_r, _chain(3000, "Z"), 100, 100))])
p["tests"].append([_ser(_fill(_r, _shape(_r, 3000, 0.8), 0, 100))])


def _tilt_sum(nd):
    """returns (sum, tilt total) by explicit recursion"""
    if nd is None:
        return 0, 0
    ls, lt = _tilt_sum(nd[1])
    rs, rt = _tilt_sum(nd[2])
    return nd[0] + ls + rs, lt + rt + abs(ls - rs)


def b_tilt(tree):
    return _tilt_sum(_parse(tree))[1]


def g_tilt(r):
    return [_ser(_fill(r, _small(r, 1, 12), 0, 9))]


def v_tilt(tests):
    for t in tests:
        _chk_tree(t["args"][0], 1, 3000, 100)


CHECKS["binary-tree-tilt-total"] = (b_tilt, g_tilt, "exact")
VALIDATE["binary-tree-tilt-total"] = v_tilt

p = add(
    id="binary-tree-subtree-range-sum", title="Sum of Subtree Ranges", diff="Easy", topic=TOPIC, tier="extra",
    fn="sumSubtreeRanges", params=[("tree", "int[]")], ret="int", cmp="exact",
    desc="<p>The <em>range</em> of a subtree is its largest value minus its smallest value. The subtree of a node consists of the node and all of its descendants, so a leaf has range <code>0</code>.</p>"
         "<p>Return the sum of the ranges of the subtrees of <strong>all</strong> nodes of the tree.</p>"
         + _ENC +
         "<p><strong>Example 1</strong></p><pre>tree = [4,8,5,0,1,-1,6]\nOutput: 17\nRanges: root 8 - 0 = 8; node 8: 8 - 0 = 8; node 5: 6 - 5 = 1; the leaves 0, 1 and 6: 0 each.</pre>"
         "<p><strong>Example 2</strong></p><pre>tree = [1,2,3]\nOutput: 2</pre>",
    constraints=["1 &le; number of nodes &le; 3,000", "0 &le; node value &le; 100,000", "The array follows the encoding above exactly"],
    hints=["Recomputing the maximum and minimum of every subtree from scratch is quadratic on a chain. Reuse the answers of the children.",
           "The maximum of a subtree is the largest of the node's value and the maxima of its two child subtrees; the minimum works the same way.",
           "Sweep the level-order array from the last index to 0, keep <code>mx[u]</code> and <code>mn[u]</code>, and add <code>mx[u] - mn[u]</code> to the total at every node."],
    editorial=["For node <code>u</code>, <code>mx[u] = max(val[u], mx[l], mx[r])</code> and <code>mn[u] = min(val[u], mn[l], mn[r])</code>, where missing children are ignored. The range of the subtree of <code>u</code> is <code>mx[u] - mn[u]</code>; adding it up over all nodes gives the answer.",
               "Because each child has a larger level-order index than its parent, one backwards sweep finishes the children before their parent. Time O(n), memory O(n). The total is at most 3,000 * 100,000 = 3 * 10<sup>8</sup>, so it fits in 32 bits."],
    time="O(n)", space="O(n)",
    solution=_PARSE_SRC + '''def sumSubtreeRanges(tree):
    val, left, right = parse(tree)
    n = len(val)
    mx = val[:]
    mn = val[:]
    total = 0
    for u in range(n - 1, -1, -1):
        for c in (left[u], right[u]):
            if c != -1:
                mx[u] = max(mx[u], mx[c])
                mn[u] = min(mn[u], mn[c])
        total += mx[u] - mn[u]
    return total
''',
    tests=[[[4, 8, 5, 0, 1, -1, 6]], [[1, 2, 3]], [[7]], [[5, 5, 5, 5]], [[0, 100000]], [[10, 1, -1, 9, -1, 0]], [[1, 100000, 1, 100000, 1, 100000, 1]],
           [[3, 1, 4, 1, 5, 9, 2, 6]], [[9, 7, 8, 1, 2, 3, 4]]],
)
_r = rnd(7002)
p["tests"].append([_ser(_fill(_r, _shape(_r, 3000), 0, 100000))])
p["tests"].append([_ser(_fill(_r, _chain(3000, "Z"), 0, 100000))])
p["tests"].append([_ser(_fill(_r, _shape(_r, 3000, 0.7), 0, 100000))])


def _range_total(nd):
    """returns (min, max, total of ranges) by explicit recursion"""
    if nd is None:
        return None
    vals = [nd[0]]
    tot = 0
    for ch in (nd[1], nd[2]):
        res = _range_total(ch)
        if res:
            vals += [res[0], res[1]]
            tot += res[2]
    return min(vals), max(vals), tot + max(vals) - min(vals)


def b_range(tree):
    return _range_total(_parse(tree))[2]


def g_range(r):
    return [_ser(_fill(r, _small(r, 1, 12), 0, r.choice([3, 9, 100])))]


def v_range(tests):
    for t in tests:
        _chk_tree(t["args"][0], 1, 3000, 100000)


CHECKS["binary-tree-subtree-range-sum"] = (b_range, g_range, "exact")
VALIDATE["binary-tree-subtree-range-sum"] = v_range

p = add(
    id="tree-ancestor-free-selection-sum", title="Ancestor-Free Selection", diff="Easy", topic=TOPIC, tier="extra",
    fn="bestAncestorFreeSum", params=[("tree", "int[]")], ret="int", cmp="exact",
    desc="<p>Every node of a binary tree holds a number of points. You may pick any set of nodes, as long as <strong>no picked node is an ancestor of another picked node</strong> (a node is an ancestor of every node below it in its subtree; a parent and its child are the simplest example). Picking nothing is allowed.</p>"
         "<p>Return the maximum total number of points of an ancestor-free selection.</p>"
         + _ENC +
         "<p><strong>Example 1</strong></p><pre>tree = [10,3,4,5,6]\nOutput: 15\nPick 5, 6 (below node 3) and 4. Picking the root gives only 10.</pre>"
         "<p><strong>Example 2</strong></p><pre>tree = [20,3,4,5,6]\nOutput: 20\nThe root alone beats 5 + 6 + 4 = 15.</pre>",
    constraints=["1 &le; number of nodes &le; 5,000", "0 &le; node value &le; 100,000", "The array follows the encoding above exactly"],
    hints=["Look at one node. Either it is picked, and then nothing in its subtree may be picked, or it is not picked and its two child subtrees are independent problems.",
           "Let <code>best[u]</code> be the answer for the subtree of <code>u</code>. If <code>u</code> is picked the total is <code>val[u]</code>, otherwise it is <code>best[left] + best[right]</code>.",
           "So <code>best[u] = max(val[u], best[left] + best[right])</code> with <code>best</code> of a missing child equal to 0. Fill it from the last level-order index down to the root."],
    editorial=["Picking a node blocks its whole subtree, but leaves the sibling subtrees untouched, so the subtrees decide independently. For a node <code>u</code> the choice is binary: take <code>u</code> alone (<code>val[u]</code>) or skip it and combine the best selections of its children. Hence <code>best[u] = max(val[u], best[l] + best[r])</code> and the answer is <code>best[root]</code>.",
               "For a leaf both children are missing, so <code>best</code> is simply its value. One backwards sweep over the level-order array gives O(n) time and O(n) memory. Greedy rules like 'always take the largest value' or 'always take the leaves' fail, which is why the comparison at each node is needed."],
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


def bestAncestorFreeSum(tree):
    val, left, right = parse(tree)
    n = len(val)
    best = [0] * n
    for u in range(n - 1, -1, -1):
        below = 0
        for c in (left[u], right[u]):
            if c != -1:
                below += best[c]
        best[u] = max(val[u], below)
    return best[0]
''',
    tests=[[[10, 3, 4, 5, 6]], [[20, 3, 4, 5, 6]], [[0]], [[8]], [[5, 5]], [[1, 2, 3]], [[7, 1, -1, 1, -1, 1]], [[100, 1, 1, 1, 1, 1, 1, 1, 1]],
           [[9, 4, 4, 4, 4, 4, 4]], [[0, 0, 0, 0]]],
)
_r = rnd(7003)
p["tests"].append([_ser(_fill(_r, _shape(_r, 3000), 0, 100000))])
p["tests"].append([_ser(_fill(_r, _shape(_r, 3000, 0.7), 0, 100000))])
p["tests"].append([_ser(_fill(_r, _chain(2500, "X", _r), 0, 100000))])


def b_anti(tree):
    vals, par, ed = _edges(_parse(tree))
    n = len(vals)
    anc = [set() for _ in range(n)]
    for v in range(n):
        u = par[v]
        while u != -1:
            anc[v].add(u)
            u = par[u]
    best = 0
    for mask in range(1 << n):
        chosen = [i for i in range(n) if (mask >> i) & 1]
        if any(b in anc[a] for a in chosen for b in chosen):
            continue
        best = max(best, sum(vals[i] for i in chosen))
    return best


def g_anti(r):
    return [_ser(_fill(r, _small(r, 1, 11), 0, 9))]


def v_anti(tests):
    for t in tests:
        _chk_tree(t["args"][0], 1, 5000, 100000)


CHECKS["tree-ancestor-free-selection-sum"] = (b_anti, g_anti, "exact")
VALIDATE["tree-ancestor-free-selection-sum"] = v_anti

# =================================================================== MEDIUM

p = add(
    id="distribute-coins-in-binary-tree", title="Distribute Coins in a Binary Tree", diff="Medium", topic=TOPIC, tier="common",
    fn="minCoinMoves", params=[("tree", "int[]")], ret="int", cmp="exact",
    desc="<p>Each node of a binary tree holds some coins, and the total number of coins in the tree equals the number of nodes. In one move you take one coin from a node and give it to an adjacent node (its parent or one of its children).</p>"
         "<p>Return the minimum number of moves after which every node holds exactly one coin.</p>"
         + _ENC +
         "<p>Here the numbers in the array are the coin counts of the nodes.</p>"
         "<p><strong>Example 1</strong></p><pre>tree = [3,0,0]\nOutput: 2\nMove one coin to each child.</pre>"
         "<p><strong>Example 2</strong></p><pre>tree = [0,3,0]\nOutput: 3\nThe left child sends two coins to the root (2 moves) and the root passes one of them on to the right child (1 move).</pre>",
    constraints=["1 &le; number of nodes &le; 3,000", "0 &le; node value &le; number of nodes", "The sum of all node values equals the number of nodes", "The array follows the encoding above exactly"],
    hints=["Consider one edge between a node and its child. Only the coins that must cross this edge matter, and you can ignore what happens inside the two sides.",
           "Look at the subtree below the edge. It owns <code>coins</code> coins and has <code>size</code> nodes, so it needs <code>size - coins</code> coins from outside (or has <code>coins - size</code> to send out). That many coins must cross the edge, in whichever direction.",
           "Every crossing costs exactly one move, and crossings on different edges never help each other, so the answer is the sum over all non-root nodes of <code>|coins(subtree) - size(subtree)|</code>. Compute it bottom-up with one running 'excess' per node."],
    editorial=["Define the excess of a node <code>u</code> as <code>excess(u) = coins in subtree(u) - nodes in subtree(u)</code>. If it is positive, that many coins have to leave the subtree through the edge to the parent; if it is negative, that many must come in. Either way the edge between <code>u</code> and its parent is used exactly <code>|excess(u)|</code> times, and no sequence of moves can use it fewer times.",
               "The bound is achievable by moving coins greedily from the leaves upwards, so the answer is the sum of <code>|excess(u)|</code> over all non-root nodes. The excess recurrence is <code>excess(u) = val[u] - 1 + excess(left) + excess(right)</code>. A backwards sweep over the level-order array gives O(n) time and O(n) memory. Since the root's own excess is always 0 (coins equal nodes), summing over all nodes gives the same total."],
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


def minCoinMoves(tree):
    val, left, right = parse(tree)
    n = len(val)
    excess = [v - 1 for v in val]
    moves = 0
    for u in range(n - 1, -1, -1):
        for c in (left[u], right[u]):
            if c != -1:
                excess[u] += excess[c]
        moves += abs(excess[u])
    return moves
''',
    tests=[[[3, 0, 0]], [[0, 3, 0]], [[1]], [[2, 0]], [[0, 2]], [[0, 0, 3]], [[1, 0, 2]], [[1, 1, 1, 1, 1, 1, 1]], [[0, 0, 0, 0, 0, 0, 0, 8]],
           [[5, 0, 0, 0, 0]], [[0, 0, 0, 0, 0, 4, 3]]],
)


def _coins(r, root, mode):
    nodes = _nodes(root)
    n = len(nodes)
    for nd in nodes:
        nd[0] = 0
    if mode == "random":
        for _ in range(n):
            r.choice(nodes)[0] += 1
    elif mode == "one":
        r.choice(nodes)[0] = n
    elif mode == "last":
        nodes[-1][0] = n
    elif mode == "root":
        nodes[0][0] = n
    return root


_r = rnd(7004)
p["tests"].append([_ser(_coins(_r, _shape(_r, 3000), "random"))])
p["tests"].append([_ser(_coins(_r, _chain(3000, "Z"), "last"))])
p["tests"].append([_ser(_coins(_r, _chain(3000, "L"), "root"))])
p["tests"].append([_ser(_coins(_r, _shape(_r, 3000, 0.6), "one"))])


def b_coins(tree):
    root = _parse(tree)
    vals, par, ed = _edges(root)
    n = len(vals)
    adj = [[] for _ in range(n)]
    for a, b in ed:
        adj[a].append(b)
        adj[b].append(a)
    start = tuple(vals)
    goal = tuple([1] * n)
    dist = {start: 0}
    q = deque([start])
    while q:
        s = q.popleft()
        if s == goal:
            return dist[s]
        for u in range(n):
            if s[u] > 0:
                for w in adj[u]:
                    t = list(s)
                    t[u] -= 1
                    t[w] += 1
                    t = tuple(t)
                    if t not in dist:
                        dist[t] = dist[s] + 1
                        q.append(t)
    raise AssertionError("unreachable")


def g_coins(r):
    root = _shape(r, r.randint(1, 6), r.choice([0, 0.5]))
    return [_ser(_coins(r, root, r.choice(["random", "one", "last", "root"])))]


def v_coins(tests):
    for t in tests:
        arr = t["args"][0]
        _chk_tree(arr, 1, 3000, 3000)
        cnt = sum(1 for x in arr if x != -1)
        # coin counts are the values; -1 only marks missing children, so count real nodes by parsing
        nodes = _nodes(_parse(arr))
        assert sum(nd[0] for nd in nodes) == len(nodes), "coins must equal nodes"
        assert cnt == len(nodes)


CHECKS["distribute-coins-in-binary-tree"] = (b_coins, g_coins, "exact")
VALIDATE["distribute-coins-in-binary-tree"] = v_coins

p = add(
    id="most-frequent-subtree-sums", title="Most Frequent Subtree Sums", diff="Medium", topic=TOPIC, tier="common",
    fn="frequentSubtreeSums", params=[("tree", "int[]")], ret="int[]", cmp="exact",
    desc="<p>The <em>subtree sum</em> of a node is the sum of the values of the node and all of its descendants. Every node of the tree has one subtree sum, and different nodes may share the same one.</p>"
         "<p>Return every subtree sum that occurs the largest number of times among all nodes. If several sums tie for the highest frequency, return all of them. The returned array must be sorted in <strong>ascending</strong> order.</p>"
         + _ENC +
         "<p><strong>Example 1</strong></p><pre>tree = [5,2,3]\nOutput: [2,3,10]\nThe subtree sums are 2, 3 and 10, each occurring once.</pre>"
         "<p><strong>Example 2</strong></p><pre>tree = [2,1,1]\nOutput: [1]\nThe sums are 1, 1 and 4; the sum 1 occurs twice.</pre>",
    constraints=["1 &le; number of nodes &le; 3,000", "0 &le; node value &le; 1,000", "The array follows the encoding above exactly", "Return the sums in ascending order"],
    hints=["First work out how to get the subtree sum of every node in one pass instead of re-summing each subtree separately.",
           "The sum of a subtree is the node's value plus the sums of its two child subtrees, so a bottom-up sweep produces every subtree sum exactly once.",
           "Count how often each sum appears in a hash map while sweeping, then take the maximum count and collect all sums that reach it. Sort them before returning."],
    editorial=["Compute <code>S(u) = val[u] + S(left) + S(right)</code> for all nodes in one backwards sweep over the level-order array (children have larger indices than parents). Each computed value is added to a frequency counter.",
               "After the sweep, find the highest frequency and return all sums with that frequency in ascending order. Time is O(n + d log d), where d is the number of distinct sums, and memory is O(n). Because values are non-negative, several nodes can share a sum (for example a node with a single child of value 0 and its child), which is why ties and the sorted output matter."],
    time="O(n log n)", space="O(n)",
    solution=_PARSE_SRC + '''def frequentSubtreeSums(tree):
    val, left, right = parse(tree)
    n = len(val)
    s = val[:]
    freq = {}
    for u in range(n - 1, -1, -1):
        for c in (left[u], right[u]):
            if c != -1:
                s[u] += s[c]
        freq[s[u]] = freq.get(s[u], 0) + 1
    top = max(freq.values())
    return sorted(k for k, v in freq.items() if v == top)
''',
    tests=[[[5, 2, 3]], [[2, 1, 1]], [[0]], [[7]], [[0, 0, 0]], [[3, 0, -1, 3]], [[1, 2, 3, 4, 5, 6, 7]], [[4, 2, 2, 2, 2, 2, 2]],
           [[6, 1, 5, 1, -1, 2, 3]], [[1, 0, 0, 1, 1, 1, 1]]],
)
_r = rnd(7005)
p["tests"].append([_ser(_fill(_r, _shape(_r, 3000), 0, 1000))])
p["tests"].append([_ser(_fill(_r, _shape(_r, 3000, 0.5), 0, 2))])
p["tests"].append([_ser(_fill(_r, _chain(3000, "Z"), 0, 0))])


def _sub_sums(nd, out):
    if nd is None:
        return 0
    s = nd[0] + _sub_sums(nd[1], out) + _sub_sums(nd[2], out)
    out.append(s)
    return s


def b_freq(tree):
    out = []
    _sub_sums(_parse(tree), out)
    c = Counter(out)
    top = max(c.values())
    return sorted(k for k in c if c[k] == top)


def g_freq(r):
    return [_ser(_fill(r, _small(r, 1, 12), 0, r.choice([1, 2, 4])))]


def v_freq(tests):
    for t in tests:
        _chk_tree(t["args"][0], 1, 3000, 1000)
        assert t["expected"] == sorted(set(t["expected"]))


CHECKS["most-frequent-subtree-sums"] = (b_freq, g_freq, "exact")
VALIDATE["most-frequent-subtree-sums"] = v_freq

p = add(
    id="tree-maximum-edge-matching", title="Maximum Matching in a Binary Tree", diff="Medium", topic=TOPIC, tier="extra",
    fn="maxTreeMatching", params=[("tree", "int[]")], ret="int", cmp="exact",
    desc="<p>A <em>matching</em> is a set of edges of the tree such that no two chosen edges share a node. Return the maximum possible number of edges in a matching.</p>"
         "<p>Only the shape of the tree matters, so every node in the input has value <code>0</code>.</p>"
         + _ENC +
         "<p><strong>Example 1</strong></p><pre>tree = [0,0,-1,0,-1,0]\nOutput: 2\nThe tree is a path of 4 nodes a-b-c-d. Take edges a-b and c-d.</pre>"
         "<p><strong>Example 2</strong></p><pre>tree = [0,0,0,0,0,0,0]\nOutput: 2\nA perfect tree with 7 nodes: match one leaf with its parent on each side and leave the root free. Every edge uses an inner node, and only the three inner nodes exist, but pairing the root with a child would use two inner nodes in one edge, so 3 edges are impossible.</pre>",
    constraints=["1 &le; number of nodes &le; 3,000", "Every node value is 0", "The array follows the encoding above exactly"],
    hints=["Look at a single node <code>u</code>. Either <code>u</code> is matched to one of its children, or it is not matched inside its own subtree.",
           "Keep two numbers per node: <code>f[u]</code>, the best matching inside the subtree of <code>u</code>, and <code>g[u]</code>, the best one in which <code>u</code> itself stays unmatched. Then <code>g[u]</code> is the sum of <code>f</code> over the children.",
           "To match <code>u</code> with child <code>c</code>, take <code>g[u] - f[c] + g[c] + 1</code> (child <code>c</code> must be unmatched below, plus one for the new edge). <code>f[u]</code> is the maximum of <code>g[u]</code> and these options."],
    editorial=["Let <code>f[u]</code> be the largest matching in the subtree of <code>u</code> and <code>g[u]</code> the largest one in which <code>u</code> is not used. Then <code>g[u] = sum of f[c]</code> over the children. If <code>u</code> is matched with child <code>c</code>, then <code>c</code> may not be matched to its own children, so that option is worth <code>g[u] - f[c] + g[c] + 1</code>. Take <code>f[u]</code> as the best of <code>g[u]</code> and all such options; the answer is <code>f[root]</code>.",
               "A backwards sweep over the level-order array evaluates it in O(n) time and O(n) memory. A greedy variant also works: process nodes bottom-up and match a node with a child whenever both are still free (leaves first), but the two-state DP is easier to justify, and it is the template for the vertex cover, independent set and dominating set DPs on trees."],
    time="O(n)", space="O(n)",
    solution=_PARSE_SRC + '''def maxTreeMatching(tree):
    val, left, right = parse(tree)
    n = len(val)
    f = [0] * n
    g = [0] * n
    for u in range(n - 1, -1, -1):
        kids = [c for c in (left[u], right[u]) if c != -1]
        base = sum(f[c] for c in kids)
        g[u] = base
        best = base
        for c in kids:
            best = max(best, base - f[c] + g[c] + 1)
        f[u] = best
    return f[0]
''',
    tests=[[[0, 0, -1, 0, -1, 0]], [[0, 0, 0, 0, 0, 0, 0]], [[0]], [[0, 0]], [[0, 0, 0]], [[0, -1, 0, -1, 0, -1, 0, -1, 0]], [[0, 0, 0, 0, -1, 0]],
           [[0, 0, 0, 0, 0, -1, 0, 0, 0]], [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]],
)
_r = rnd(7006)
p["tests"].append([_ser(_shape(_r, 3000))])
p["tests"].append([_ser(_shape(_r, 3000, 0.7))])
p["tests"].append([_ser(_chain(3000, "X", _r))])


def b_match(tree):
    vals, par, ed = _edges(_parse(tree))
    best = 0
    m = len(ed)
    for mask in range(1 << m):
        used = set()
        ok = True
        for i in range(m):
            if (mask >> i) & 1:
                a, b = ed[i]
                if a in used or b in used:
                    ok = False
                    break
                used.add(a)
                used.add(b)
        if ok:
            best = max(best, bin(mask).count("1"))
    return best


def g_match(r):
    return [_ser(_small(r, 1, 11))]


def v_match(tests):
    for t in tests:
        _chk_tree(t["args"][0], 1, 3000, 0)


CHECKS["tree-maximum-edge-matching"] = (b_match, g_match, "exact")
VALIDATE["tree-maximum-edge-matching"] = v_match

p = add(
    id="tree-count-independent-sets", title="Count Independent Sets in a Tree", diff="Medium", topic=TOPIC, tier="extra",
    fn="countIndependentSets", params=[("tree", "int[]")], ret="int", cmp="exact",
    desc="<p>An <em>independent set</em> of a tree is a set of nodes in which no two nodes are directly connected by an edge (no node is chosen together with its parent). The empty set counts as an independent set.</p>"
         "<p>Return the number of independent sets of the tree, modulo <code>1,000,000,007</code>.</p>"
         "<p>Only the shape of the tree matters, so every node in the input has value <code>0</code>.</p>"
         + _ENC +
         "<p><strong>Example 1</strong></p><pre>tree = [0,0,0]\nOutput: 5\nThe sets are {}, {root}, {left}, {right} and {left, right}.</pre>"
         "<p><strong>Example 2</strong></p><pre>tree = [0,0,-1,0,-1,0]\nOutput: 8\nA path of 4 nodes has 8 independent sets.</pre>",
    constraints=["1 &le; number of nodes &le; 3,000", "Every node value is 0", "The array follows the encoding above exactly"],
    hints=["Brute force over subsets is exponential. Think about one node and decide whether it is in the set or not.",
           "Per node keep two counts for its subtree: <code>inc[u]</code> (sets that contain <code>u</code>) and <code>exc[u]</code> (sets that do not). The subtrees of the two children are independent, so counts multiply.",
           "If <code>u</code> is chosen, each child must be left out: <code>inc[u] = product of exc[c]</code>. If not, each child is free: <code>exc[u] = product of (inc[c] + exc[c])</code>. A missing child contributes a factor of 1. Reduce modulo 10<sup>9</sup>+7."],
    editorial=["Count by cases on the node. Sets containing <code>u</code> may not contain any child of <code>u</code>, but may do anything below the children's children, which is exactly what <code>exc[c]</code> counts for each child. Sets not containing <code>u</code> combine any independent set of the left subtree with any independent set of the right subtree, giving the product of <code>inc[c] + exc[c]</code>.",
               "For a leaf <code>inc = exc = 1</code>. The answer is <code>inc[root] + exc[root]</code> modulo 10<sup>9</sup>+7. One bottom-up pass gives O(n) time and O(n) memory. For a path of n nodes this reproduces the Fibonacci numbers, a good sanity check."],
    time="O(n)", space="O(n)",
    solution=_PARSE_SRC + '''def countIndependentSets(tree):
    MOD = 10 ** 9 + 7
    val, left, right = parse(tree)
    n = len(val)
    inc = [1] * n
    exc = [1] * n
    for u in range(n - 1, -1, -1):
        a = b = 1
        for c in (left[u], right[u]):
            if c != -1:
                a = a * exc[c] % MOD
                b = b * (inc[c] + exc[c]) % MOD
        inc[u] = a
        exc[u] = b
    return (inc[0] + exc[0]) % MOD
''',
    tests=[[[0, 0, 0]], [[0, 0, -1, 0, -1, 0]], [[0]], [[0, 0]], [[0, 0, 0, 0, 0, 0, 0]], [[0, -1, 0, -1, 0]], [[0, 0, 0, 0, 0, -1, 0, 0, 0]],
           [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]],
)
_r = rnd(7007)
p["tests"].append([_ser(_shape(_r, 3000))])
p["tests"].append([_ser(_chain(3000, "Z"))])
p["tests"].append([_ser(_perfect(11))])
p["tests"].append([_ser(_shape(_r, 3000, 0.5))])


def b_indep(tree):
    vals, par, ed = _edges(_parse(tree))
    n = len(vals)
    cnt = 0
    for mask in range(1 << n):
        if all(not ((mask >> a) & 1 and (mask >> b) & 1) for a, b in ed):
            cnt += 1
    return cnt % MOD


def g_indep(r):
    return [_ser(_small(r, 1, 12))]


def v_indep(tests):
    for t in tests:
        _chk_tree(t["args"][0], 1, 3000, 0)


CHECKS["tree-count-independent-sets"] = (b_indep, g_indep, "exact")
VALIDATE["tree-count-independent-sets"] = v_indep

p = add(
    id="split-tree-maximum-product", title="Split a Tree for Maximum Product", diff="Medium", topic=TOPIC, tier="common",
    fn="maxSplitProduct", params=[("tree", "int[]")], ret="int", cmp="exact",
    desc="<p>You may delete exactly one edge of the binary tree, which splits it into two connected pieces. Compute the sum of node values in each piece and multiply the two sums.</p>"
         "<p>Return the largest product you can obtain over all choices of the deleted edge, taken modulo <code>1,000,000,007</code>. The maximum must be chosen by the true (unreduced) product; only the final answer is reduced.</p>"
         + _ENC +
         "<p><strong>Example 1</strong></p><pre>tree = [1,2,3,4,5,6]\nOutput: 110\nCutting the edge above node 2 gives sums 11 (nodes 2, 4, 5) and 10, so the product is 110.</pre>"
         "<p><strong>Example 2</strong></p><pre>tree = [5,5,5]\nOutput: 50\nCut off any leaf: sums 5 and 10.</pre>",
    constraints=["2 &le; number of nodes &le; 3,000", "0 &le; node value &le; 10,000", "The array follows the encoding above exactly"],
    hints=["Deleting the edge between a node and its parent separates exactly the subtree of that node from the rest.",
           "If the whole tree sums to <code>T</code> and the subtree of <code>u</code> sums to <code>s</code>, the product for that cut is <code>s * (T - s)</code>. There is one candidate for every non-root node.",
           "Compute all subtree sums bottom-up, then take the maximum of <code>s * (T - s)</code> over non-root nodes <strong>before</strong> reducing modulo 10<sup>9</sup>+7. Reducing early can break the comparison."],
    editorial=["Each edge connects a non-root node to its parent, and removing it isolates that node's subtree. With subtree sums <code>s[u]</code> and total <code>T = s[root]</code>, the two pieces have sums <code>s[u]</code> and <code>T - s[u]</code>. One backwards pass over the level-order array computes <code>s[u]</code>; a second pass (or the same one) maximises <code>s[u] * (T - s[u])</code>.",
               "The product can reach about 2 * 10<sup>14</sup>, which does not fit into 32 bits but fits easily into 64-bit or Python integers; compare the exact values and apply the modulus only at the end. The ideal cut is the one whose subtree sum is closest to <code>T / 2</code>. Time O(n), memory O(n)."],
    time="O(n)", space="O(n)",
    solution=_PARSE_SRC + '''def maxSplitProduct(tree):
    val, left, right = parse(tree)
    n = len(val)
    s = val[:]
    for u in range(n - 1, -1, -1):
        for c in (left[u], right[u]):
            if c != -1:
                s[u] += s[c]
    total = s[0]
    best = 0
    for u in range(1, n):
        best = max(best, s[u] * (total - s[u]))
    return best % (10 ** 9 + 7)
''',
    tests=[[[1, 2, 3, 4, 5, 6]], [[5, 5, 5]], [[1, 1]], [[0, 0]], [[7, 0]], [[10000, 10000, 10000, 10000]], [[1, -1, 2, -1, 3, -1, 4]], [[3, 1, 1, 1, 1, 1, 1]],
           [[2, 9, 1, 1, 1, 9, 9]]],
)
_r = rnd(7008)
p["tests"].append([_ser(_fill(_r, _shape(_r, 3000), 9000, 10000))])
p["tests"].append([_ser(_fill(_r, _chain(3000, "X", _r), 0, 10000))])
p["tests"].append([_ser(_fill(_r, _shape(_r, 3000, 0.6), 0, 10000))])


def b_split(tree):
    vals, par, ed = _edges(_parse(tree))
    n = len(vals)
    best = 0
    for cut in range(len(ed)):
        adj = [[] for _ in range(n)]
        for i, (a, b) in enumerate(ed):
            if i != cut:
                adj[a].append(b)
                adj[b].append(a)
        seen = {0}
        st = [0]
        while st:
            x = st.pop()
            for y in adj[x]:
                if y not in seen:
                    seen.add(y)
                    st.append(y)
        s1 = sum(vals[i] for i in seen)
        s2 = sum(vals) - s1
        best = max(best, s1 * s2)
    return best % MOD


def g_split(r):
    return [_ser(_fill(r, _small(r, 2, 12), 0, r.choice([3, 20, 10000])))]


def v_split(tests):
    for t in tests:
        _chk_tree(t["args"][0], 2, 3000, 10000)


CHECKS["split-tree-maximum-product"] = (b_split, g_split, "exact")
VALIDATE["split-tree-maximum-product"] = v_split

p = add(
    id="even-tree-max-edge-removals", title="Even Tree", diff="Medium", topic=TOPIC, tier="extra",
    fn="maxEvenCuts", params=[("tree", "int[]")], ret="int", cmp="exact",
    desc="<p>You may delete edges of a binary tree, which splits it into several connected pieces. A set of deletions is <em>good</em> if every resulting piece contains an <strong>even</strong> number of nodes.</p>"
         "<p>Return the maximum number of edges that can be deleted by a good set of deletions. The number of nodes in the tree is always even, so deleting nothing is a good set.</p>"
         "<p>Only the shape of the tree matters, so every node in the input has value <code>0</code>.</p>"
         + _ENC +
         "<p><strong>Example 1</strong></p><pre>tree = [0,0,0,0]\nOutput: 1\nThe root has children a and b, and a has a left child c. Deleting the edge between the root and a leaves the pieces {a, c} and {root, b}, both of size 2.</pre>"
         "<p><strong>Example 2</strong></p><pre>tree = [0,0,-1,0,-1,0,-1,0,-1,0]\nOutput: 2\nA path of 6 nodes. Cutting after the 2nd and the 4th node leaves three pieces of size 2.</pre>",
    constraints=["2 &le; number of nodes &le; 3,000, and the number of nodes is even", "Every node value is 0", "The array follows the encoding above exactly"],
    hints=["Deleting the edge between a node and its parent cuts off exactly the subtree of that node. When is it allowed to cut there?",
           "If the subtree of <code>u</code> has an even number of nodes, cutting above it creates an even piece, and the rest of the tree loses an even number of nodes, so it stays even in total. If the subtree is odd, cutting there can never be part of a good set.",
           "Compute subtree sizes bottom-up and count the non-root nodes whose subtree size is even. Remember that the cuts do not interfere: every such edge can be deleted at the same time."],
    editorial=["Count the nodes of every subtree: <code>size[u] = 1 + size[l] + size[r]</code>. Deleting the edge above <code>u</code> separates a piece of size <code>size[u]</code> from the rest, so it is only possible when <code>size[u]</code> is even in a good set. Conversely, delete the edges above all non-root nodes with even subtree size at once: every resulting piece is the subtree of such a node minus the subtrees of the even descendants cut below it, which is an even number minus even numbers, hence even. The root's piece is the total (even) minus even numbers, again even.",
               "So the answer is the number of non-root nodes with an even subtree size. One backwards sweep over the level-order array gives O(n) time and O(n) memory."],
    time="O(n)", space="O(n)",
    solution=_PARSE_SRC + '''def maxEvenCuts(tree):
    val, left, right = parse(tree)
    n = len(val)
    size = [1] * n
    cuts = 0
    for u in range(n - 1, -1, -1):
        for c in (left[u], right[u]):
            if c != -1:
                size[u] += size[c]
        if u > 0 and size[u] % 2 == 0:
            cuts += 1
    return cuts
''',
    tests=[[[0, 0]], [[0, 0, 0, 0]], [[0, 0, 0, -1, 0, 0, 0]], [[0, 0, 0, 0, 0, 0]], [[0, 0, -1, 0, -1, 0]], [[0, 0, 0, 0, 0, 0, 0, 0]],
           [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]],
)
_r = rnd(7009)
p["tests"].append([_ser(_shape(_r, 3000))])
p["tests"].append([_ser(_chain(3000, "X", _r))])
p["tests"].append([_ser(_shape(_r, 3000, 0.6))])
p["tests"].append([_ser(_shape(_r, 2998, 0.2))])


def b_even(tree):
    vals, par, ed = _edges(_parse(tree))
    n = len(vals)
    best = 0
    for mask in range(1 << len(ed)):
        parent = list(range(n))

        def find(x):
            while parent[x] != x:
                parent[x] = parent[parent[x]]
                x = parent[x]
            return x
        for i, (a, b) in enumerate(ed):
            if not (mask >> i) & 1:
                parent[find(a)] = find(b)
        comp = Counter(find(i) for i in range(n))
        if all(v % 2 == 0 for v in comp.values()):
            best = max(best, bin(mask).count("1"))
    return best


def g_even(r):
    return [_ser(_shape(r, 2 * r.randint(1, 5), r.choice([0, 0.5])))]


def v_even(tests):
    for t in tests:
        arr = t["args"][0]
        _chk_tree(arr, 2, 3000, 0)
        assert len(_nodes(_parse(arr))) % 2 == 0


CHECKS["even-tree-max-edge-removals"] = (b_even, g_even, "exact")
VALIDATE["even-tree-max-edge-removals"] = v_even

# =================================================================== HARD

p = add(
    id="tree-cheapest-guard-coverage", title="Cheapest Guard Coverage", diff="Hard", topic=TOPIC, tier="extra",
    fn="minGuardCost", params=[("tree", "int[]")], ret="int", cmp="exact",
    desc="<p>A guard may be posted at any node of a binary tree; posting a guard at a node costs the node's value. A guard watches its own node, its parent and its children.</p>"
         "<p>Return the minimum total cost of a set of guards such that <strong>every</strong> node of the tree is watched by at least one guard. Costs can be <code>0</code>.</p>"
         + _ENC +
         "<p><strong>Example 1</strong></p><pre>tree = [4,1,1]\nOutput: 2\nGuards at both children (cost 1 + 1) watch everything; the root alone costs 4.</pre>"
         "<p><strong>Example 2</strong></p><pre>tree = [3,1,-1,1]\nOutput: 1\nThe tree is a path with costs 3, 1, 1. A guard on the middle node watches all three.</pre>",
    constraints=["1 &le; number of nodes &le; 3,000", "0 &le; node value (cost) &le; 1,000", "The array follows the encoding above exactly"],
    hints=["With all costs equal to 1 a greedy bottom-up rule works, but with different costs it can fail. Think of a DP with a few states per node.",
           "For each node keep three costs for its subtree: <code>A</code> = node has a guard; <code>B</code> = no guard on it, but a child's guard watches it; <code>C</code> = no guard on it and not watched by a child (the parent must cover it, but every node below is already watched).",
           "<code>A[u] = cost[u] + sum(min(A, B, C) of children)</code>; <code>C[u] = sum(B of children)</code>; <code>B[u]</code> = sum of <code>min(A, B)</code> over children, where at least one child must use state A (add the smallest extra price of switching one child to A; impossible for a leaf). Answer: <code>min(A, B)</code> at the root."],
    editorial=["Every node ends up in one of three situations: it has a guard (A), it has none but one of its children has (B), or it has none and no child has, so only its parent can watch it (C). Which states are allowed for a child depends on its parent. If the parent has a guard (A), the child is watched anyway, so it may be in any state. If the parent has no guard but is watched by a child (B), each child may be A or B, because a child in state C would need this very parent to carry a guard. If the parent is in state C, none of its children may have a guard, so every child must be in state B.",
               "This gives <code>A[u] = cost + sum(min(A,B,C)[c])</code>, <code>C[u] = sum(B[c])</code> and <code>B[u] = sum(min(A,B)[c]) + min over c of (A[c] - min(A,B)[c])</code>, the last term forcing one child into state A at the smallest extra cost, with B infinite for a leaf. At the root C is not allowed (nobody above), so the answer is <code>min(A, B)</code>. A backwards pass over level order runs in O(n) time with O(n) memory. Greedy rules such as 'guard the parents of leaves' break when those parents are expensive."],
    time="O(n)", space="O(n)",
    solution=_PARSE_SRC + '''def minGuardCost(tree):
    INF = 10 ** 15
    val, left, right = parse(tree)
    n = len(val)
    A = [0] * n
    B = [INF] * n
    C = [0] * n
    for u in range(n - 1, -1, -1):
        kids = [c for c in (left[u], right[u]) if c != -1]
        A[u] = val[u] + sum(min(A[c], B[c], C[c]) for c in kids)
        C[u] = sum(B[c] for c in kids)
        if kids:
            base = sum(min(A[c], B[c]) for c in kids)
            extra = min(A[c] - min(A[c], B[c]) for c in kids)
            B[u] = base + extra
    return min(A[0], B[0])
''',
    tests=[[[4, 1, 1]], [[3, 1, -1, 1]], [[5]], [[0]], [[2, 7]], [[1, 5, 5, 1, 1, 1, 1]], [[9, 1, 9, 9, 1, 9, 9]], [[1, 1, 1, 1, 1, 1, 1]],
           [[10, 10, 10, 1, 1, 1, 1]], [[0, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5]]],
)
_r = rnd(7010)
p["tests"].append([_ser(_fill(_r, _shape(_r, 3000), 0, 1000))])
p["tests"].append([_ser(_fill(_r, _shape(_r, 3000, 0.6), 1, 1000))])
p["tests"].append([_ser(_fill(_r, _chain(3000, "X", _r), 0, 1000))])


def b_guard(tree):
    vals, par, ed = _edges(_parse(tree))
    n = len(vals)
    nb = [{i} for i in range(n)]
    for a, b in ed:
        nb[a].add(b)
        nb[b].add(a)
    best = None
    for mask in range(1 << n):
        if all(any((mask >> j) & 1 for j in nb[i]) for i in range(n)):
            c = sum(vals[i] for i in range(n) if (mask >> i) & 1)
            if best is None or c < best:
                best = c
    return best


def g_guard(r):
    return [_ser(_fill(r, _small(r, 1, 11), 0, r.choice([1, 3, 9])))]


def v_guard(tests):
    for t in tests:
        _chk_tree(t["args"][0], 1, 3000, 1000)


CHECKS["tree-cheapest-guard-coverage"] = (b_guard, g_guard, "exact")
VALIDATE["tree-cheapest-guard-coverage"] = v_guard

p = add(
    id="rooted-connected-subset-max-sum", title="Best Connected Cluster Containing the Root", diff="Hard", topic=TOPIC, tier="extra",
    fn="bestRootedCluster", params=[("tree", "int[]"), ("k", "int")], ret="int", cmp="exact",
    desc="<p>Choose exactly <code>k</code> nodes of the binary tree such that the chosen nodes form a connected group <strong>containing the root</strong>: the root is chosen, and every chosen node other than the root has its parent chosen too.</p>"
         "<p>Return the maximum possible sum of the values of the chosen nodes. It is guaranteed that <code>k</code> does not exceed the number of nodes, so such a choice always exists.</p>"
         + _ENC +
         "<p><strong>Example 1</strong></p><pre>tree = [1,5,2,3,-1,10,1], k = 3\nOutput: 13\nChoose the root 1, its right child 2 and that node's left child 10.</pre>"
         "<p><strong>Example 2</strong></p><pre>tree = [1,5,2,3,-1,10,1], k = 1\nOutput: 1\nOnly the root can be chosen.</pre>",
    constraints=["1 &le; number of nodes &le; 3,000", "1 &le; k &le; min(number of nodes, 60)", "0 &le; node value &le; 1,000", "The array follows the encoding above exactly"],
    hints=["A greedy 'always extend with the largest reachable value' can fail: a small value may unlock a large one behind it. Define the problem per subtree.",
           "Let <code>dp[u][j]</code> be the best sum of a connected group of exactly <code>j</code> nodes inside the subtree of <code>u</code> that contains <code>u</code>. Start with <code>dp[u][1] = val[u]</code>.",
           "Merge the children one by one like a knapsack: giving <code>t</code> of the remaining slots to a child adds <code>dp[child][t]</code> (or take nothing from that child). Cap every list at length <code>k</code> so that the total work is O(n * k)."],
    editorial=["This is a tree knapsack. For node <code>u</code> start with the list <code>[-, val[u]]</code>, meaning one node taken. For each child <code>c</code>, form a new list in which <code>new[j + t] = max(cur[j] + dp[c][t])</code> for <code>t &ge; 1</code>, while <code>t = 0</code> keeps <code>cur[j]</code> (the child contributes nothing). Entries beyond <code>k</code> are never needed and are cut.",
               "Because the list for a subtree has at most <code>min(size, k) + 1</code> entries, the merge costs <code>min(size_a, k) * min(size_b, k)</code>, and the standard argument gives O(n * k) in total. The answer is <code>dp[root][k]</code>. Memory is O(n * k) in the worst case; freeing a child's list after merging keeps it small in practice. Since all values are non-negative, every count from 1 to min(size, k) is reachable, so no 'impossible' states need handling apart from j = 0."],
    time="O(n * k)", space="O(n * k)",
    solution=_PARSE_SRC + '''def bestRootedCluster(tree, k):
    val, left, right = parse(tree)
    n = len(val)
    dp = [None] * n
    for u in range(n - 1, -1, -1):
        cur = [-1, val[u]]
        for c in (left[u], right[u]):
            if c == -1:
                continue
            d = dp[c]
            dp[c] = None
            lc, ld = len(cur) - 1, len(d) - 1
            m = min(lc + ld, k)
            new = cur[:min(lc, k) + 1] + [-1] * (m - min(lc, k))
            for j in range(1, lc + 1):
                base = cur[j]
                for t in range(1, min(ld, k - j) + 1):
                    cand = base + d[t]
                    if cand > new[j + t]:
                        new[j + t] = cand
            cur = new
        dp[u] = cur
    return dp[0][k]
''',
    tests=[[[1, 5, 2, 3, -1, 10, 1], 3], [[1, 5, 2, 3, -1, 10, 1], 1], [[1, 5, 2, 3, -1, 10, 1], 6], [[4], 1], [[0, 9], 1], [[0, 9], 2], [[1, 0, 0, 0, 0, 100, 100], 3],
           [[1, 0, 0, 50, -1, -1, 0, 60], 4], [[2, 1, 1, 1, 1, 1, 1], 4]],
)
_r = rnd(7011)
_t = _ser(_fill(_r, _shape(_r, 3000), 0, 1000))
p["tests"].append([_t, 60])
_t = _ser(_fill(_r, _chain(3000, "Z"), 0, 1000))
p["tests"].append([_t, 60])
_t = _ser(_fill(_r, _shape(_r, 3000, 0.7), 0, 1000))
p["tests"].append([_t, 37])


def b_cluster(tree, k):
    vals, par, ed = _edges(_parse(tree))
    n = len(vals)
    best = -1
    for comb in combinations(range(n), k):
        s = set(comb)
        if 0 in s and all(i == 0 or par[i] in s for i in comb):
            best = max(best, sum(vals[i] for i in comb))
    return best


def g_cluster(r):
    root = _fill(r, _small(r, 1, 10), 0, r.choice([3, 9, 50]))
    n = len(_nodes(root))
    return [_ser(root), r.randint(1, n)]


def v_cluster(tests):
    for t in tests:
        arr, k = t["args"]
        _chk_tree(arr, 1, 3000, 1000)
        n = len(_nodes(_parse(arr)))
        assert 1 <= k <= min(n, 60)


CHECKS["rooted-connected-subset-max-sum"] = (b_cluster, g_cluster, "exact")
VALIDATE["rooted-connected-subset-max-sum"] = v_cluster
