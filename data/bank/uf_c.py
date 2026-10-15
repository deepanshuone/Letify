"""Problems: Union Find, dynamic connectivity (additions, removals, offline queries). See data/lib.py for the registry."""
from collections import deque
from itertools import combinations  # noqa: F401
from math import gcd

from lib import add, rnd, CHECKS, VALIDATE, gen_arr  # noqa: F401

TOPIC = "Union Find"


# ------------------------------------------------------------------ helpers used only by tests, brute forces and validators
def _comp_count(n, edges):
    """Number of connected components of nodes 0..n-1 (BFS, independent of the union-find solutions)."""
    adj = [[] for _ in range(n)]
    for u, v in edges:
        adj[u].append(v)
        adj[v].append(u)
    seen = [False] * n
    cnt = 0
    for s in range(n):
        if not seen[s]:
            cnt += 1
            seen[s] = True
            dq = deque([s])
            while dq:
                x = dq.popleft()
                for y in adj[x]:
                    if not seen[y]:
                        seen[y] = True
                        dq.append(y)
    return cnt


def _reach(n, edges, a, b):
    adj = [[] for _ in range(n)]
    for u, v in edges:
        adj[u].append(v)
        adj[v].append(u)
    seen = {a}
    dq = deque([a])
    while dq:
        x = dq.popleft()
        for y in adj[x]:
            if y not in seen:
                seen.add(y)
                dq.append(y)
    return b in seen


def _rand_edges(r, n, k):
    out = []
    for _ in range(k):
        u = r.randrange(n)
        v = r.randrange(n)
        while v == u:
            v = r.randrange(n)
        out.append([u, v])
    return out


def _stabilize(g):
    """Remove every brick that is not connected to the top row (so the wall is stable at the start)."""
    R, C = len(g), len(g[0])
    seen = set((0, c) for c in range(C) if g[0][c] == 1)
    st = list(seen)
    while st:
        r, c = st.pop()
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            a, b = r + dr, c + dc
            if 0 <= a < R and 0 <= b < C and g[a][b] == 1 and (a, b) not in seen:
                seen.add((a, b))
                st.append((a, b))
    return [[1 if (i, j) in seen else 0 for j in range(C)] for i in range(R)]


def _tree_edges(r, n):
    """Random spanning tree on 0..n-1 as a list of [u, v]."""
    order = list(range(n))
    r.shuffle(order)
    return [[order[r.randrange(i)], order[i]] for i in range(1, n)]


# =================================================================== EASY
# ---------------------------------------------------------------- components after each edge added
p = add(
    id="components-after-each-edge-added", title="Components After Each Edge Added", diff="Easy", topic=TOPIC,
    fn="countAfterEachEdge", params=[("n", "int"), ("edges", "int[][]")], ret="int[]", cmp="exact",
    desc="<p>A network has <code>n</code> machines numbered <code>0</code> to <code>n - 1</code> and starts with no cables at all. The cables are then installed one by one, in the order given by <code>edges</code>; the entry <code>[u, v]</code> connects machines <code>u</code> and <code>v</code> with a two-way cable.</p><p>A <em>cluster</em> is a maximal group of machines that can reach each other through cables (directly or through other machines). Return an array of length <code>edges.length</code> whose <code>k</code>-th element is the number of clusters right after the <code>k</code>-th cable has been installed.</p><pre>n = 5, edges = [[0,1],[1,2],[0,2],[3,4],[2,3]]\n\nresult = [4,3,3,2,1]</pre><p>The third cable joins machines that are already in the same cluster, so the count stays at 3.</p>",
    constraints=["2 &le; n &le; 100,000", "1 &le; edges.length &le; 100,000", "edges[k] = [u, v] with 0 &le; u, v &lt; n and u &ne; v", "The same pair of machines may be cabled more than once"],
    hints=["Recounting the clusters from scratch after every cable costs O(n + k) each time. Can you update the count instead of recomputing it?",
           "Start with n clusters. A new cable either joins two different clusters (count goes down by one) or lies inside a cluster (count unchanged).",
           "Keep a union-find structure. For each edge find the roots of both ends: if they differ, union them and decrement the counter; always append the counter to the answer."],
    editorial=["Begin with <code>n</code> singleton clusters, which is the count before any cable exists. A union-find (disjoint-set) structure answers the only question that matters: are the two endpoints of the new cable already in the same cluster? If their roots differ the cable merges two clusters, so we union them and subtract one from the counter. If the roots are equal the cable is redundant for connectivity and the counter does not move.",
               "Append the counter after processing each edge. With path compression every <code>find</code> is nearly constant time, so the total is about O((n + k) &middot; &alpha;(n)) for k cables. Note the answers never increase, since adding a cable can only merge clusters."],
    time="O((n + k) &middot; &alpha;(n))", space="O(n)",
    solution='''def countAfterEachEdge(n, edges):
    parent = list(range(n))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    comps = n
    out = []
    for u, v in edges:
        ru, rv = find(u), find(v)
        if ru != rv:
            parent[ru] = rv
            comps -= 1
        out.append(comps)
    return out
''',
    tests=[[5, [[0, 1], [1, 2], [0, 2], [3, 4], [2, 3]]], [2, [[0, 1]]], [2, [[0, 1], [1, 0], [0, 1]]],
           [4, [[0, 1], [2, 3], [1, 2]]], [4, [[3, 2], [2, 1], [1, 0]]], [6, [[0, 5], [1, 4], [2, 3]]],
           [5, [[0, 1], [0, 2], [0, 3], [0, 4]]], [7, [[0, 1], [1, 0], [2, 3], [3, 2], [4, 5], [1, 2], [5, 6]]],
           [3, [[0, 1], [1, 0], [0, 1], [1, 2], [2, 1]]]],
)
_r = rnd(8301)
p["tests"].append([2500, _rand_edges(_r, 2500, 2500)])
_t = _tree_edges(_r, 2000)
_r.shuffle(_t)
p["tests"].append([2000, _t])
p["tests"].append([6000, _rand_edges(_r, 6000, 1500)])


def b_cae(n, edges):
    return [_comp_count(n, edges[:k]) for k in range(1, len(edges) + 1)]


def g_cae(r):
    n = r.randint(2, 8)
    return [n, _rand_edges(r, n, r.randint(1, 10))]


def v_cae(tests):
    for t in tests:
        n, edges = t["args"]
        assert 2 <= n <= 100000 and 1 <= len(edges) <= 100000
        assert all(0 <= u < n and 0 <= v < n and u != v for u, v in edges)
        assert len(t["expected"]) == len(edges)


CHECKS["components-after-each-edge-added"] = (b_cae, g_cae, "exact")
VALIDATE["components-after-each-edge-added"] = v_cae

# ---------------------------------------------------------------- group size queries with merges
p = add(
    id="group-size-queries-with-merges", title="Group Size Queries With Merges", diff="Easy", topic=TOPIC,
    fn="groupQueries", params=[("n", "int"), ("ops", "int[][]")], ret="int[]", cmp="exact",
    desc="<p>There are <code>n</code> people numbered <code>0</code> to <code>n - 1</code>, each starting in a group of their own. You receive a list of operations <code>ops</code>, each of the form <code>[type, a, b]</code>:</p><ul><li><code>type = 1</code>: merge the group containing <code>a</code> with the group containing <code>b</code> (nothing happens if they are already the same group).</li><li><code>type = 2</code>: report the current size of the group containing <code>a</code>. For this type <code>b</code> is always <code>0</code> and must be ignored.</li><li><code>type = 3</code>: report <code>1</code> if <code>a</code> and <code>b</code> are currently in the same group, otherwise <code>0</code>.</li></ul><p>Return the reported values of all type 2 and type 3 operations, in the order the operations appear.</p><pre>n = 6\nops = [[1,0,1],[1,2,3],[3,0,2],[1,1,3],[3,0,2],[2,3,0],[2,5,0]]\n\nresult = [0,1,4,1]</pre><p>After the first two merges the groups are {0,1}, {2,3}, {4}, {5}, so person 0 and 2 are apart. After the third merge {0,1,2,3} is one group of size 4.</p>",
    constraints=["1 &le; n &le; 100,000", "1 &le; ops.length &le; 100,000", "type &isin; {1, 2, 3} and 0 &le; a, b &lt; n", "For type 2, b = 0", "At least one operation has type 2 or 3"],
    hints=["Keeping a group label per person makes a merge cost O(n) in the worst case. What structure merges sets cheaply?",
           "A disjoint-set (union-find) structure supports 'which group is this person in' (find) and 'merge two groups' (union).",
           "Store the size at each root: when two roots are united add the smaller size into the larger root, and a size query is just <code>size[find(a)]</code>. A same-group query compares two roots."],
    editorial=["This is a direct use of union-find with <em>union by size</em>. Every person starts as the root of its own set with size 1. A merge finds both roots, and if they differ, attaches the smaller tree below the larger one and adds the sizes. A size query returns the size stored at the root of <code>a</code>, and a same-group query checks whether the two roots are equal.",
               "Union by size keeps the trees shallow, and path compression flattens them further, so each operation is O(&alpha;(n)), which is effectively constant. The whole sequence runs in about O((n + q) &middot; &alpha;(n)) for q operations. Only the root's size entry is meaningful, so never read the size of a non-root node."],
    time="O((n + q) &middot; &alpha;(n))", space="O(n)",
    solution='''def groupQueries(n, ops):
    parent = list(range(n))
    size = [1] * n

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    out = []
    for t, a, b in ops:
        ra = find(a)
        if t == 1:
            rb = find(b)
            if ra != rb:
                if size[ra] < size[rb]:
                    ra, rb = rb, ra
                parent[rb] = ra
                size[ra] += size[rb]
        elif t == 2:
            out.append(size[ra])
        else:
            out.append(1 if ra == find(b) else 0)
    return out
''',
    tests=[[6, [[1, 0, 1], [1, 2, 3], [3, 0, 2], [1, 1, 3], [3, 0, 2], [2, 3, 0], [2, 5, 0]]], [1, [[2, 0, 0]]],
           [1, [[1, 0, 0], [3, 0, 0], [2, 0, 0]]], [2, [[3, 0, 1], [1, 1, 0], [3, 0, 1], [2, 1, 0]]],
           [5, [[1, 0, 1], [1, 1, 0], [1, 0, 1], [2, 0, 0], [2, 1, 0]]], [5, [[1, 4, 3], [1, 3, 2], [1, 2, 1], [1, 1, 0], [2, 4, 0], [3, 0, 4]]],
           [4, [[2, 0, 0], [2, 1, 0], [2, 2, 0], [2, 3, 0]]], [6, [[1, 0, 1], [1, 2, 3], [1, 4, 5], [1, 1, 2], [2, 0, 0], [3, 3, 4], [1, 3, 5], [2, 4, 0], [3, 0, 5]]]],
)
_r = rnd(8302)
_n = 3000
_ops = []
for _ in range(4000):
    _t = _r.choice([1, 1, 2, 3])
    _a = _r.randrange(_n)
    _b = 0 if _t == 2 else _r.randrange(_n)
    _ops.append([_t, _a, _b])
p["tests"].append([_n, _ops])
_ops = [[1, i, i + 1] for i in range(1999)] + [[2, _r.randrange(2000), 0] for _ in range(300)] + [[3, 0, 1999]]
p["tests"].append([2000, _ops])
_ops = [[1, _r.randrange(1000), _r.randrange(1000)] for _ in range(700)] + [[2, _r.randrange(1000), 0] for _ in range(500)]
p["tests"].append([1000, _ops])


def b_gq(n, ops):
    groups = [{i} for i in range(n)]
    where = list(range(n))
    out = []
    for t, a, b in ops:
        if t == 1:
            ga, gb = where[a], where[b]
            if ga != gb:
                for x in groups[gb]:
                    where[x] = ga
                groups[ga] |= groups[gb]
                groups[gb] = set()
        elif t == 2:
            out.append(len(groups[where[a]]))
        else:
            out.append(1 if where[a] == where[b] else 0)
    return out


def g_gq(r):
    n = r.randint(1, 7)
    ops = []
    for _ in range(r.randint(1, 12)):
        t = r.choice([1, 2, 3])
        ops.append([t, r.randrange(n), 0 if t == 2 else r.randrange(n)])
    ops.append([r.choice([2, 3]), 0, 0])
    return [n, ops]


def v_gq(tests):
    for t in tests:
        n, ops = t["args"]
        assert 1 <= n <= 100000 and 1 <= len(ops) <= 100000
        for typ, a, b in ops:
            assert typ in (1, 2, 3) and 0 <= a < n and 0 <= b < n
            if typ == 2:
                assert b == 0
        assert any(o[0] != 1 for o in ops) and len(t["expected"]) == sum(1 for o in ops if o[0] != 1)


CHECKS["group-size-queries-with-merges"] = (b_gq, g_gq, "exact")
VALIDATE["group-size-queries-with-merges"] = v_gq

# =================================================================== MEDIUM
# ---------------------------------------------------------------- most stones removed
p = add(
    id="most-stones-removed", title="Most Stones Removed", diff="Medium", topic=TOPIC,
    fn="removeStones", params=[("stones", "int[][]")], ret="int", cmp="exact",
    desc="<p>Stones lie on distinct integer points of a plane; the entry <code>[x, y]</code> of <code>stones</code> is a stone in column <code>x</code> and row <code>y</code>. In one move you may remove a stone <code>s</code> if at least one other stone that is <em>still on the plane</em> shares its column (same <code>x</code>) or its row (same <code>y</code>) with <code>s</code>.</p><p>Return the largest number of stones that can be removed by a sequence of such moves.</p><pre>stones = [[0,0],[0,2],[1,1],[2,0],[2,2]]\n\nresult = 3</pre><p>The four corner stones are linked through shared rows and columns, so three of them can go, while the middle stone has nobody in its row or column and must stay.</p>",
    constraints=["1 &le; stones.length &le; 5,000", "0 &le; x, y &le; 10,000", "All stones are at different points"],
    hints=["Try small cases by hand: which stones can never be removed? Think about a stone that is alone in both its row and its column.",
           "Consider the graph where two stones are linked when they share a row or a column. In a connected group, how many stones can you remove?",
           "In every connected group all stones except one can be removed (always remove a leaf of a spanning tree first). So the answer is <code>stones - groups</code>. Count the groups with union-find by joining each stone's row and column."],
    editorial=["Look at each connected group of stones, where two stones are neighbours if they share a row or a column. Inside one group, take a spanning tree and remove stones from the leaves inward: a leaf always still has its tree parent in its row or column, so it is removable. Everything except the last stone (the root) can therefore be removed. A lone stone cannot be removed at all. Hence the maximum is <code>len(stones) - number_of_groups</code>.",
               "To count groups without building the stone graph (which could have O(n&sup2;) edges), treat every distinct row and every distinct column as a node and union <code>x</code> with <code>y</code> for each stone. Stones sharing a row or column end up in the same set. Offset the row ids (for example use <code>~y</code>) so they never collide with column ids. Count the distinct roots among the stones. Time is O(n &middot; &alpha;(n))."],
    time="O(n &middot; &alpha;(n))", space="O(n)",
    solution='''def removeStones(stones):
    parent = {}

    def find(x):
        if x not in parent:
            parent[x] = x
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for x, y in stones:
        a, b = find(x), find(~y)
        if a != b:
            parent[a] = b
    groups = {find(x) for x, y in stones}
    return len(stones) - len(groups)
''',
    tests=[[[[0, 0], [0, 2], [1, 1], [2, 0], [2, 2]]], [[[0, 0], [0, 1], [1, 0], [1, 2], [2, 1], [2, 2]]], [[[0, 0]]], [[[0, 0], [1, 1]]],
           [[[0, 0], [0, 1]]], [[[3, 4], [3, 7], [9, 7], [9, 2], [5, 2], [5, 1]]], [[[0, 0], [1, 1], [2, 2], [3, 3], [4, 4]]],
           [[[0, 0], [0, 1], [0, 2], [0, 3], [5, 5]]], [[[10000, 10000], [0, 10000], [10000, 0], [0, 0]]],
           [[[1, 1], [1, 2], [2, 1], [3, 3], [3, 4], [4, 3], [6, 6]]]],
)
_r = rnd(8303)
_s = set()
while len(_s) < 3000:
    _s.add((_r.randrange(10001), _r.randrange(10001)))
p["tests"].append([[list(q) for q in sorted(_s)]])  # sparse: mostly isolated stones
_s = set()
while len(_s) < 3000:
    _s.add((_r.randrange(1500), _r.randrange(1500)))
_l = [list(q) for q in _s]
_r.shuffle(_l)
p["tests"].append([_l])
_s = set()
while len(_s) < 2000:
    _s.add((_r.randrange(40), _r.randrange(10001)))
_l = [list(q) for q in _s]
_r.shuffle(_l)
p["tests"].append([_l])  # few columns, many rows


def b_stones(stones):
    n = len(stones)
    full = (1 << n) - 1
    memo = {}

    def best(mask):
        if mask in memo:
            return memo[mask]
        res = 0
        for i in range(n):
            if mask >> i & 1:
                for j in range(n):
                    if j != i and mask >> j & 1 and (stones[i][0] == stones[j][0] or stones[i][1] == stones[j][1]):
                        res = max(res, 1 + best(mask & ~(1 << i)))
                        break
        memo[mask] = res
        return res

    return best(full)


def g_stones(r):
    cells = [(x, y) for x in range(4) for y in range(4)]
    k = r.randint(1, 8)
    return [[list(c) for c in r.sample(cells, k)]]


def v_stones(tests):
    for t in tests:
        st = t["args"][0]
        assert 1 <= len(st) <= 5000
        assert len({tuple(s) for s in st}) == len(st)
        assert all(len(s) == 2 and 0 <= s[0] <= 10000 and 0 <= s[1] <= 10000 for s in st)
        assert 0 <= t["expected"] < len(st)


CHECKS["most-stones-removed"] = (b_stones, g_stones, "exact")
VALIDATE["most-stones-removed"] = v_stones

# ---------------------------------------------------------------- earliest moment everyone connected
p = add(
    id="earliest-moment-everyone-connected", title="Earliest Moment Everyone Is Connected", diff="Medium", topic=TOPIC,
    fn="earliestFullConnection", params=[("n", "int"), ("logs", "int[][]")], ret="int", cmp="exact",
    desc="<p>In a club of <code>n</code> members numbered <code>0</code> to <code>n - 1</code>, nobody knows anybody at the start. The log <code>logs</code> lists friendship events in arbitrary order: an entry <code>[t, a, b]</code> means that at time <code>t</code> members <code>a</code> and <code>b</code> became friends (friendship is mutual and stays forever).</p><p>Two members are <em>acquainted</em> at time <code>T</code> if they are friends directly or through a chain of friends, using only events with <code>t &le; T</code>. Return the smallest time <code>T</code> at which every pair of members is acquainted, or <code>-1</code> if that never happens.</p><pre>n = 4\nlogs = [[20,0,1],[5,2,3],[30,1,2],[12,0,3]]\n\nresult = 20</pre><p>The events at times 5 and 12 build the group {0,2,3}; member 1 only joins at time 20, when everybody becomes connected.</p>",
    constraints=["2 &le; n &le; 5,000", "1 &le; logs.length &le; 20,000", "logs[k] = [t, a, b] with 0 &le; t &le; 10<sup>9</sup>, 0 &le; a, b &lt; n and a &ne; b", "Several events may share the same time; the same pair may appear several times"],
    hints=["Everyone is acquainted exactly when the friendship graph is connected. Which events matter for reaching that state first?",
           "Process the events in increasing order of time. Adding events can only merge groups, never split them.",
           "Sort by time and union the two members of each event. Keep a counter of groups starting at n; the moment it becomes 1, the current event's time is the answer. If it never reaches 1, return -1."],
    editorial=["The friendship graph only gains edges as time passes, so we can replay history in order. Sort the log by time and keep a union-find over the members together with a counter of groups, initially <code>n</code>. For each event, if the two members are in different sets, union them and decrease the counter. The first moment the counter drops to 1 everyone is connected, and the time of that event is the answer.",
               "If several events share a timestamp it does not matter in which order they are processed: the counter first hits 1 while processing some event of time <code>T</code>, and every earlier timestamp was not enough. If all events are consumed without reaching 1, return -1. Sorting dominates the cost: O(m log m + m &middot; &alpha;(n)) for m events."],
    time="O(m log m + m &middot; &alpha;(n))", space="O(n)",
    solution='''def earliestFullConnection(n, logs):
    parent = list(range(n))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    groups = n
    for t, a, b in sorted(logs):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb
            groups -= 1
            if groups == 1:
                return t
    return -1
''',
    tests=[[4, [[20, 0, 1], [5, 2, 3], [30, 1, 2], [12, 0, 3]]], [2, [[7, 0, 1]]], [2, [[0, 1, 0]]], [3, [[1, 0, 1], [2, 1, 0]]],
           [3, [[4, 0, 1], [4, 1, 2]]], [5, [[10, 0, 1], [10, 1, 2], [10, 2, 3], [11, 3, 4]]], [4, [[3, 0, 1], [2, 2, 3]]],
           [6, [[9, 0, 1], [8, 2, 3], [7, 4, 5], [6, 1, 2], [5, 3, 4], [1000000000, 0, 5]]],
           [5, [[1, 0, 1], [2, 0, 2], [3, 0, 3], [4, 0, 4], [5, 1, 2]]], [4, [[100, 0, 1], [90, 1, 2], [80, 2, 0], [70, 0, 2]]]],
)
_r = rnd(8304)
_n = 1500
_tr = _tree_edges(_r, _n)
_lg = [[_r.randint(0, 10 ** 6), u, v] for u, v in _tr] + [[_r.randint(0, 10 ** 6)] + e for e in _rand_edges(_r, _n, 1300)]
_r.shuffle(_lg)
p["tests"].append([_n, _lg])
_lg = [[_r.randint(0, 10 ** 9)] + e for e in _rand_edges(_r, 1000, 900)]
p["tests"].append([1000, _lg])  # sparse: never connected
_n = 1200
_lg = [[_r.randint(0, 3000), u, v] for u, v in _tree_edges(_r, _n)]
p["tests"].append([_n, _lg])  # many equal timestamps


def b_emc(n, logs):
    for T in sorted({t for t, a, b in logs}):
        if _comp_count(n, [[a, b] for t, a, b in logs if t <= T]) == 1:
            return T
    return -1


def g_emc(r):
    n = r.randint(2, 6)
    logs = []
    for _ in range(r.randint(1, 9)):
        a, b = r.sample(range(n), 2)
        logs.append([r.randint(0, 8), a, b])
    return [n, logs]


def v_emc(tests):
    for t in tests:
        n, logs = t["args"]
        assert 2 <= n <= 5000 and 1 <= len(logs) <= 20000
        assert all(0 <= x <= 10 ** 9 and 0 <= a < n and 0 <= b < n and a != b for x, a, b in logs)


CHECKS["earliest-moment-everyone-connected"] = (b_emc, g_emc, "exact")
VALIDATE["earliest-moment-everyone-connected"] = v_emc

# ---------------------------------------------------------------- largest island size after each addition
p = add(
    id="largest-island-after-each-addition", title="Largest Island After Each Addition", diff="Medium", topic=TOPIC,
    fn="largestIslandAfterEach", params=[("m", "int"), ("n", "int"), ("positions", "int[][]")], ret="int[]", cmp="exact",
    desc="<p>An <code>m x n</code> map starts as all water. The entry <code>positions[k] = [r, c]</code> turns the cell in row <code>r</code>, column <code>c</code> into land; if that cell is already land nothing changes.</p><p>An <em>island</em> is a maximal set of land cells connected through shared sides (up, down, left, right). Return an array whose <code>k</code>-th element is the number of cells of the <strong>largest island</strong> right after the <code>k</code>-th operation.</p><pre>m = 3, n = 3\npositions = [[0,0],[0,1],[2,2],[1,1],[2,1],[0,0]]\n\nresult = [1,2,2,3,5,5]</pre><p>Adding (2,1) at step 5 joins the island {(0,0),(0,1),(1,1)} with the lone cell (2,2), giving 3 + 1 + 1 = 5 cells.</p>",
    constraints=["1 &le; m, n &le; 60", "1 &le; positions.length &le; 5,000", "positions[k] = [r, c] with 0 &le; r &lt; m and 0 &le; c &lt; n", "The same cell may appear more than once"],
    hints=["After one operation only a few islands can change. Is the largest size ever going to decrease?",
           "A new land cell can merge at most four neighbouring islands, and merging only makes islands bigger.",
           "Use union-find with a size per root. When a cell is added, union it with every land neighbour, then update a running maximum with the size of the resulting set. Repeated cells just repeat the current maximum."],
    editorial=["Islands only grow and merge, so a union-find with sizes is a natural fit. Index each cell as <code>r * n + c</code>. For a new land cell, start with a set of size 1, then union it with each of its four neighbours that is already land, adding sizes at the root. After the unions, the island containing the new cell is the only island whose size changed, so the global maximum is <code>max(previous_max, size[find(cell)])</code>.",
               "A cell that is already land must be skipped, otherwise its size would be double counted; in that case just repeat the previous maximum. Because the maximum never decreases we do not need to scan all islands. Total time is O(mn + k &middot; &alpha;(mn)) for k operations."],
    time="O(mn + k &middot; &alpha;(mn))", space="O(mn)",
    solution='''def largestIslandAfterEach(m, n, positions):
    parent = list(range(m * n))
    size = [1] * (m * n)
    land = [False] * (m * n)

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    best = 0
    out = []
    for r, c in positions:
        idx = r * n + c
        if not land[idx]:
            land[idx] = True
            for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nr, nc = r + dr, c + dc
                if 0 <= nr < m and 0 <= nc < n and land[nr * n + nc]:
                    a, b = find(idx), find(nr * n + nc)
                    if a != b:
                        if size[a] < size[b]:
                            a, b = b, a
                        parent[b] = a
                        size[a] += size[b]
            best = max(best, size[find(idx)])
        out.append(best)
    return out
''',
    tests=[[3, 3, [[0, 0], [0, 1], [2, 2], [1, 1], [2, 1], [0, 0]]], [1, 1, [[0, 0]]], [1, 1, [[0, 0], [0, 0]]],
           [2, 2, [[0, 0], [1, 1], [0, 1], [1, 0]]], [1, 5, [[0, 0], [0, 2], [0, 4], [0, 1], [0, 3]]],
           [4, 1, [[3, 0], [1, 0], [2, 0], [0, 0]]], [3, 3, [[0, 0], [0, 2], [2, 0], [2, 2], [1, 1], [0, 1], [1, 0], [1, 2], [2, 1]]],
           [3, 4, [[0, 0], [1, 1], [2, 2], [1, 2], [0, 1], [2, 3], [0, 3], [1, 3]]], [2, 3, [[1, 2], [1, 2], [0, 0], [0, 0], [0, 1]]]],
)
_r = rnd(8305)
p["tests"].append([60, 60, [[_r.randrange(60), _r.randrange(60)] for _ in range(3000)]])
_cells = [[i, j] for i in range(60) for j in range(60)]
_r.shuffle(_cells)
p["tests"].append([60, 60, _cells[:2600]])
_cells = [[i, j] for i in range(40) for j in range(40) if (i + j) % 2 == 0]
_r.shuffle(_cells)
_cells += [[i, j] for i in range(40) for j in range(40) if (i + j) % 2 == 1]
p["tests"].append([40, 40, _cells])  # checkerboard first, then everything merges


def b_lia(m, n, positions):
    grid = [[0] * n for _ in range(m)]
    out = []
    for r, c in positions:
        grid[r][c] = 1
        seen = set()
        best = 0
        for i in range(m):
            for j in range(n):
                if grid[i][j] and (i, j) not in seen:
                    seen.add((i, j))
                    st = [(i, j)]
                    cnt = 0
                    while st:
                        x, y = st.pop()
                        cnt += 1
                        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                            a, b = x + dx, y + dy
                            if 0 <= a < m and 0 <= b < n and grid[a][b] and (a, b) not in seen:
                                seen.add((a, b))
                                st.append((a, b))
                    best = max(best, cnt)
        out.append(best)
    return out


def g_lia(r):
    m, n = r.randint(1, 4), r.randint(1, 4)
    return [m, n, [[r.randrange(m), r.randrange(n)] for _ in range(r.randint(1, 10))]]


def v_lia(tests):
    for t in tests:
        m, n, pos = t["args"]
        assert 1 <= m <= 60 and 1 <= n <= 60 and 1 <= len(pos) <= 5000
        assert all(0 <= r < m and 0 <= c < n for r, c in pos)
        assert t["expected"] == sorted(t["expected"])


CHECKS["largest-island-after-each-addition"] = (b_lia, g_lia, "exact")
VALIDATE["largest-island-after-each-addition"] = v_lia

# ---------------------------------------------------------------- components after each edge removal
p = add(
    id="components-after-each-edge-removal", title="Components After Each Edge Removal", diff="Medium", topic=TOPIC,
    fn="componentsAfterRemovals", params=[("n", "int"), ("edges", "int[][]"), ("removals", "int[]")], ret="int[]", cmp="exact",
    desc="<p>An undirected graph has nodes <code>0</code> to <code>n - 1</code> and the edge list <code>edges</code> (edge number <code>i</code> is <code>edges[i] = [u, v]</code>). Then edges are deleted one at a time: <code>removals[k]</code> is the <em>index</em> of the edge deleted in the <code>k</code>-th step. Every index appears at most once, and edges that are never listed stay forever.</p><p>Return an array whose <code>k</code>-th element is the number of connected components of the graph right after the <code>k</code>-th deletion.</p><pre>n = 5\nedges = [[0,1],[1,2],[2,3],[3,4],[0,2]]\nremovals = [4,1,2]\n\nresult = [1,2,3]</pre><p>Deleting edge 4 (0-2) leaves the path 0-1-2-3-4 (one component). Deleting edge 1 (1-2) splits it into {0,1} and {2,3,4}. Deleting edge 2 (2-3) leaves {0,1}, {2}, {3,4}.</p>",
    constraints=["2 &le; n &le; 100,000", "1 &le; edges.length &le; 100,000", "edges[i] = [u, v] with 0 &le; u, v &lt; n and u &ne; v; parallel edges are allowed", "1 &le; removals.length &le; edges.length", "removals contains distinct valid edge indices"],
    hints=["Union-find supports merging sets, but it cannot undo a merge. Deleting edges looks like the wrong direction for it.",
           "Run time backwards. Going backwards, deleting an edge becomes adding that edge.",
           "Start from the graph that contains only the edges never deleted and count its components. Then walk through <code>removals</code> from the last to the first: record the current count as the answer of that step, and afterwards add that edge back (union; decrement the count if it merges two sets)."],
    editorial=["Deleting edges from a union-find structure is not supported, but adding them is. So reverse the process. Build a union-find from all edges that are <em>never</em> removed; its component count is the state after the very last deletion.",
               "Now iterate over <code>removals</code> from the end towards the start. At position <code>k</code> the current structure is exactly the graph right after deletion <code>k</code>, so store the current component count as <code>result[k]</code>. Then put the edge <code>removals[k]</code> back by uniting its endpoints (subtracting one from the count if they were in different sets); this gives the graph right after deletion <code>k - 1</code>. Total time is O((n + m) &middot; &alpha;(n)) with m edges. This offline 'reverse time' trick is the standard way to handle deletions with union-find."],
    time="O((n + m) &middot; &alpha;(n))", space="O(n)",
    solution='''def componentsAfterRemovals(n, edges, removals):
    parent = list(range(n))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(u, v):
        ru, rv = find(u), find(v)
        if ru == rv:
            return False
        parent[ru] = rv
        return True

    gone = set(removals)
    comps = n
    for i, (u, v) in enumerate(edges):
        if i not in gone and union(u, v):
            comps -= 1
    out = [0] * len(removals)
    for k in range(len(removals) - 1, -1, -1):
        out[k] = comps
        u, v = edges[removals[k]]
        if union(u, v):
            comps -= 1
    return out
''',
    tests=[[5, [[0, 1], [1, 2], [2, 3], [3, 4], [0, 2]], [4, 1, 2]], [2, [[0, 1]], [0]], [2, [[0, 1], [0, 1]], [0]], [2, [[0, 1], [0, 1]], [1, 0]],
           [4, [[0, 1], [1, 2], [2, 3]], [1]], [4, [[0, 1], [1, 2], [2, 3]], [0, 1, 2]], [4, [[0, 1], [1, 2], [2, 3]], [2, 0, 1]],
           [4, [[0, 1], [1, 2], [2, 3], [3, 0]], [0, 2]], [6, [[0, 1], [2, 3], [4, 5], [1, 2], [3, 4]], [3, 4]],
           [5, [[0, 1], [0, 2], [0, 3], [0, 4]], [3, 2, 1, 0]], [3, [[0, 1], [1, 2], [0, 2], [2, 0]], [2, 0, 3]]],
)
_r = rnd(8306)
_n = 2000
_e = _tree_edges(_r, _n) + _rand_edges(_r, _n, 400)
_r.shuffle(_e)
_rm = list(range(len(_e)))
_r.shuffle(_rm)
p["tests"].append([_n, _e, _rm[:2000]])
_n = 1800
_e = _rand_edges(_r, _n, 2000)
_rm = list(range(len(_e)))
_r.shuffle(_rm)
p["tests"].append([_n, _e, _rm])
p["tests"].append([3000, [[i, i + 1] for i in range(2999)], _r.sample(range(2999), 1500)])


def b_car(n, edges, removals):
    cur = {i: tuple(e) for i, e in enumerate(edges)}
    out = []
    for k in removals:
        del cur[k]
        out.append(_comp_count(n, list(cur.values())))
    return out


def g_car(r):
    n = r.randint(2, 6)
    e = _rand_edges(r, n, r.randint(1, 8))
    rm = r.sample(range(len(e)), r.randint(1, len(e)))
    return [n, e, rm]


def v_car(tests):
    for t in tests:
        n, e, rm = t["args"]
        assert 2 <= n <= 100000 and 1 <= len(e) <= 100000
        assert all(0 <= u < n and 0 <= v < n and u != v for u, v in e)
        assert 1 <= len(rm) <= len(e) and len(set(rm)) == len(rm) and all(0 <= i < len(e) for i in rm)
        assert t["expected"] == sorted(t["expected"])


CHECKS["components-after-each-edge-removal"] = (b_car, g_car, "exact")
VALIDATE["components-after-each-edge-removal"] = v_car

# ---------------------------------------------------------------- edge limited path queries
p = add(
    id="edge-limited-path-queries", title="Edge Limited Path Queries", diff="Medium", topic=TOPIC, tier="extra",
    fn="edgeLimitedConnectivity", params=[("n", "int"), ("edges", "int[][]"), ("queries", "int[][]")], ret="int[]", cmp="exact",
    desc="<p>A road network has cities <code>0</code> to <code>n - 1</code> and bidirectional roads <code>edges[i] = [u, v, w]</code> of length <code>w</code> (several roads may join the same two cities). Each query <code>[p, q, limit]</code> asks: is there a route from <code>p</code> to <code>q</code> in which <strong>every</strong> road has length <em>strictly less</em> than <code>limit</code>?</p><p>Return an array with one entry per query: <code>1</code> if such a route exists, otherwise <code>0</code>. A query with <code>p = q</code> is always answered <code>1</code>.</p><pre>n = 5\nedges = [[0,1,2],[1,2,4],[2,3,6],[0,3,10],[3,4,1]]\nqueries = [[0,2,5],[0,3,6],[0,3,7],[4,4,1],[3,4,1],[3,4,2]]\n\nresult = [1,0,1,1,0,1]</pre>",
    constraints=["2 &le; n &le; 20,000", "1 &le; edges.length, queries.length &le; 20,000", "edges[i] = [u, v, w] with 0 &le; u, v &lt; n, u &ne; v and 1 &le; w &le; 10<sup>6</sup>", "queries[j] = [p, q, limit] with 0 &le; p, q &lt; n and 1 &le; limit &le; 10<sup>6</sup> + 1"],
    hints=["Running a BFS that ignores long roads for each query is O(queries &middot; (n + edges)). Look for a way to share work between queries.",
           "Different queries differ only in how many roads are allowed. If you handle queries in order of increasing limit, the allowed road set only grows.",
           "Sort the roads by length and the queries by limit. For each query in that order, union all roads with length &lt; limit not yet added, then check <code>find(p) == find(q)</code>. Store the answer at the original query index."],
    editorial=["The set of usable roads for a query is 'all roads shorter than limit'. If the queries are sorted by limit, these sets are nested: each query uses all the roads of the previous one plus a few more. That is exactly the situation where union-find shines, because it only supports merging.",
               "Sort the roads by weight, sort the query indices by limit, and keep a pointer into the road list. For each query (in increasing limit) advance the pointer while the next road has <code>w &lt; limit</code>, uniting its endpoints. The query is then answered by comparing the roots of <code>p</code> and <code>q</code>; write the answer into the slot of the original query. Total time is O(E log E + Q log Q + (E + Q) &middot; &alpha;(n)). Answering queries offline in a clever order is the whole trick."],
    time="O(E log E + Q log Q)", space="O(n + Q)",
    solution='''def edgeLimitedConnectivity(n, edges, queries):
    parent = list(range(n))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    roads = sorted(edges, key=lambda e: e[2])
    order = sorted(range(len(queries)), key=lambda i: queries[i][2])
    ans = [0] * len(queries)
    ptr = 0
    for qi in order:
        p, q, limit = queries[qi]
        while ptr < len(roads) and roads[ptr][2] < limit:
            ra, rb = find(roads[ptr][0]), find(roads[ptr][1])
            if ra != rb:
                parent[ra] = rb
            ptr += 1
        ans[qi] = 1 if find(p) == find(q) else 0
    return ans
''',
    tests=[[5, [[0, 1, 2], [1, 2, 4], [2, 3, 6], [0, 3, 10], [3, 4, 1]], [[0, 2, 5], [0, 3, 6], [0, 3, 7], [4, 4, 1], [3, 4, 1], [3, 4, 2]]],
           [2, [[0, 1, 5]], [[0, 1, 5], [0, 1, 6], [1, 0, 6], [0, 0, 1]]], [3, [[0, 1, 1], [1, 2, 1]], [[0, 2, 1], [0, 2, 2]]],
           [4, [[0, 1, 3], [0, 1, 1], [2, 3, 2]], [[0, 1, 2], [0, 1, 1], [2, 3, 3], [1, 2, 1000001]]],
           [4, [[0, 1, 4], [1, 2, 4], [2, 3, 4]], [[0, 3, 4], [0, 3, 5], [3, 0, 5]]], [5, [[0, 1, 9], [1, 2, 8], [2, 3, 7], [3, 4, 6]], [[0, 4, 10], [0, 4, 9], [1, 4, 9], [2, 4, 7], [3, 4, 7]]],
           [6, [[0, 1, 1], [2, 3, 1], [4, 5, 1], [1, 2, 5], [3, 4, 5]], [[0, 5, 5], [0, 5, 6], [0, 3, 6], [2, 5, 2]]],
           [3, [[0, 2, 1000000]], [[0, 2, 1000000], [0, 2, 1000001], [1, 1, 1]]]],
)
_r = rnd(8307)
_n = 700


def _wedges(r, n, k, wmax):
    return [e + [r.randint(1, wmax)] for e in _rand_edges(r, n, k)]


p["tests"].append([_n, _wedges(_r, _n, 1800, 10 ** 6), [[_r.randrange(_n), _r.randrange(_n), _r.randint(300000, 10 ** 6 + 1)] for _ in range(1200)]])
_n = 800
_tr = [e + [i + 1] for i, e in enumerate(_tree_edges(_r, _n))]
p["tests"].append([_n, _tr, [[_r.randrange(_n), _r.randrange(_n), _r.randint(1, _n + 1)] for _ in range(500)]])
_n = 3000
_qs = []
for _ in range(600):
    _a = _r.randrange(_n - 40)
    _qs.append([_a, _a + _r.randint(1, 40), _r.randint(200, 501)])
p["tests"].append([_n, [[i, i + 1, _r.randint(1, 500)] for i in range(_n - 1)], _qs])


def b_elp(n, edges, queries):
    out = []
    for a, b, lim in queries:
        out.append(1 if a == b or _reach(n, [[u, v] for u, v, w in edges if w < lim], a, b) else 0)
    return out


def g_elp(r):
    n = r.randint(2, 7)
    e = [[*r.sample(range(n), 2), r.randint(1, 6)] for _ in range(r.randint(1, 9))]
    q = [[r.randrange(n), r.randrange(n), r.randint(1, 8)] for _ in range(r.randint(1, 8))]
    return [n, e, q]


def v_elp(tests):
    for t in tests:
        n, e, q = t["args"]
        assert 2 <= n <= 20000 and 1 <= len(e) <= 20000 and 1 <= len(q) <= 20000
        assert all(0 <= u < n and 0 <= v < n and u != v and 1 <= w <= 10 ** 6 for u, v, w in e)
        assert all(0 <= a < n and 0 <= b < n and 1 <= lim <= 10 ** 6 + 1 for a, b, lim in q)
        assert len(t["expected"]) == len(q)


CHECKS["edge-limited-path-queries"] = (b_elp, g_elp, "exact")
VALIDATE["edge-limited-path-queries"] = v_elp

# ---------------------------------------------------------------- divisor threshold connectivity
p = add(
    id="divisor-threshold-connectivity", title="Divisor Threshold Connectivity", diff="Medium", topic=TOPIC, tier="extra",
    fn="divisorConnectivity", params=[("n", "int"), ("threshold", "int"), ("queries", "int[][]")], ret="int[]", cmp="exact",
    desc="<p>Cities are labelled <code>1</code> to <code>n</code>. Two different cities <code>a</code> and <code>b</code> are joined by a road exactly when they have a common divisor strictly greater than <code>threshold</code>, i.e. <code>gcd(a, b) &gt; threshold</code>.</p><p>For each query <code>[a, b]</code> decide whether one can travel from city <code>a</code> to city <code>b</code> along these roads, possibly through other cities. Return an array with <code>1</code> for reachable and <code>0</code> for not reachable, one entry per query.</p><pre>n = 6, threshold = 2\nqueries = [[4,5],[3,6],[2,4]]\n\nresult = [0,1,0]</pre><p>With threshold 2, the only road is 3-6 (gcd 3). With threshold 0 every pair of cities would have a road, since every gcd is at least 1.</p>",
    constraints=["2 &le; n &le; 12,000", "0 &le; threshold &le; n", "1 &le; queries.length &le; 5,000", "queries[j] = [a, b] with 1 &le; a, b &le; n and a &ne; b"],
    hints=["Building the road list by testing every pair with gcd costs O(n&sup2; log n) which is too slow for n = 20,000. Find a way to generate only the useful roads.",
           "Two cities share a divisor <code>z &gt; threshold</code> exactly when both are multiples of such a <code>z</code>. So all multiples of one <code>z</code> belong to the same group.",
           "For every <code>z</code> from <code>threshold + 1</code> to <code>n</code>, union <code>z</code> with <code>2z, 3z, ...</code> using union-find. Then each query is <code>find(a) == find(b)</code>. This is a sieve-like loop with about n log n unions."],
    editorial=["Instead of testing all pairs, flip the question around: for a fixed <code>z &gt; threshold</code>, every pair of multiples of <code>z</code> has gcd at least <code>z</code> and so is connected. It is enough to connect <code>z</code> with each of its multiples <code>2z, 3z, ...</code>, because all multiples are then in one set through <code>z</code>. Doing this for every <code>z</code> from <code>threshold + 1</code> to <code>n</code> adds all roads' worth of connectivity.",
               "A pair with <code>gcd(a, b) = g &gt; threshold</code> is covered by <code>z = g</code>, since both are multiples of <code>g</code>; conversely every union we perform corresponds to a real road. The loops perform about <code>n &middot; (1/1 + 1/2 + ...) = O(n log n)</code> unions in the worst case (threshold 0), each nearly constant time. Queries are then answered by comparing roots."],
    time="O(n log n &middot; &alpha;(n) + Q)", space="O(n)",
    solution='''def divisorConnectivity(n, threshold, queries):
    parent = list(range(n + 1))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for z in range(threshold + 1, n + 1):
        rz = find(z)
        for m in range(2 * z, n + 1, z):
            rm = find(m)
            if rm != rz:
                parent[rm] = rz
    return [1 if find(a) == find(b) else 0 for a, b in queries]
''',
    tests=[[6, 2, [[4, 5], [3, 6], [2, 4]]], [6, 0, [[1, 6], [2, 5], [3, 4]]], [2, 0, [[1, 2], [2, 1]]], [2, 1, [[1, 2]]],
           [10, 1, [[2, 4], [3, 9], [2, 3], [5, 10], [6, 9], [4, 10]]], [12, 3, [[4, 8], [6, 12], [4, 12], [5, 10], [3, 6], [7, 12]]],
           [30, 5, [[6, 12], [7, 14], [10, 15], [6, 7], [11, 22], [13, 26], [12, 18], [25, 30]]], [9, 9, [[1, 9], [3, 9]]],
           [20, 4, [[5, 10], [6, 12], [5, 15], [10, 20], [7, 14], [8, 16], [9, 18], [6, 18], [8, 12]]]],
)
_r = rnd(8308)
for _n, _th, _q in [(12000, 0, 800), (12000, 3, 1500), (12000, 200, 1500), (12000, 5000, 1500), (10000, 15, 1500)]:
    _qs = [list(_r.sample(range(1, _n + 1), 2)) for _ in range(_q // 2)]
    while len(_qs) < _q:  # pairs that tend to be linked (multiples of a common z) mixed with random pairs
        _z = _r.randint(_th + 1, max(_th + 1, _n // 2))
        _a, _b = _r.sample(range(1, _n // _z + 1), 2) if _n // _z >= 2 else (1, 2)
        if _a * _z != _b * _z and _a * _z <= _n and _b * _z <= _n:
            _qs.append([_a * _z, _b * _z])
    _r.shuffle(_qs)
    p["tests"].append([_n, _th, _qs])


def b_dtc(n, threshold, queries):
    adj = {i: [] for i in range(1, n + 1)}
    for a in range(1, n + 1):
        for b in range(a + 1, n + 1):
            if gcd(a, b) > threshold:
                adj[a].append(b)
                adj[b].append(a)
    out = []
    for a, b in queries:
        seen = {a}
        st = [a]
        while st:
            x = st.pop()
            for y in adj[x]:
                if y not in seen:
                    seen.add(y)
                    st.append(y)
        out.append(1 if b in seen else 0)
    return out


def g_dtc(r):
    n = r.randint(2, 30)
    return [n, r.randint(0, n), [r.sample(range(1, n + 1), 2) for _ in range(r.randint(1, 6))]]


def v_dtc(tests):
    for t in tests:
        n, th, q = t["args"]
        assert 2 <= n <= 12000 and 0 <= th <= n and 1 <= len(q) <= 5000
        assert all(1 <= a <= n and 1 <= b <= n and a != b for a, b in q)
        assert len(t["expected"]) == len(q)


CHECKS["divisor-threshold-connectivity"] = (b_dtc, g_dtc, "exact")
VALIDATE["divisor-threshold-connectivity"] = v_dtc

# =================================================================== HARD
# ---------------------------------------------------------------- last day to cross the grid
p = add(
    id="last-day-to-cross-flooding-grid", title="Last Day to Cross a Flooding Grid", diff="Hard", topic=TOPIC,
    fn="lastDayToCross", params=[("row", "int"), ("col", "int"), ("cells", "int[][]")], ret="int", cmp="exact",
    desc="<p>A field is a grid with <code>row</code> rows and <code>col</code> columns, numbered from 1. On day 0 every cell is land. The array <code>cells</code> lists <strong>all</strong> <code>row * col</code> cells in the order they flood: <code>cells[d - 1] = [r, c]</code> is the cell that turns into water on day <code>d</code>, and flooded cells stay water.</p><p>On a given day you can walk from the top row to the bottom row if there is a path of land cells that starts at some cell of row 1, ends at some cell of row <code>row</code>, and moves only up, down, left or right between land cells (you may start on any land cell in the top row and finish on any land cell in the bottom row).</p><p>Return the last day on which such a walk is still possible.</p><pre>row = 2, col = 2\ncells = [[1,1],[2,1],[1,2],[2,2]]\n\nresult = 2</pre><p>After day 2 the cells (1,1) and (2,1) are water, but column 2 is still land, giving a path from the top to the bottom. On day 3 the cell (1,2) floods too and the top row has no land left.</p>",
    constraints=["1 &le; row, col &le; 60", "cells is a permutation of all row * col cells, each given as [r, c] with 1 &le; r &le; row and 1 &le; c &le; col", "Day 0 (all land) always allows a walk"],
    hints=["The walkable property never comes back once it is lost, so you could binary search the day and test each with a BFS. That works, but try to avoid the extra log factor.",
           "Think backwards in time: reversing the flooding turns water cells back into land, and land only joins up.",
           "Process the cells from the last to the first, turning each back into land and uniting it with its land neighbours in a union-find. Add two virtual nodes, one for the top row and one for the bottom row. The first moment (going backwards) when they are connected, the day is the answer."],
    editorial=["Going forward, land is destroyed, which union-find cannot handle. Going backward, land appears cell by cell and components only merge, a perfect fit. Add two virtual nodes TOP and BOTTOM: every land cell in row 1 is united with TOP and every land cell in row <code>row</code> is united with BOTTOM. Then 'a walk exists' means <code>find(TOP) == find(BOTTOM)</code>.",
               "Iterate <code>i</code> from <code>row * col - 1</code> down to 0. At that moment, the land is exactly the cells <code>cells[i], cells[i + 1], ...</code>, which is the field on day <code>i</code>. Make <code>cells[i]</code> land, unite it with its four land neighbours (and with TOP / BOTTOM if it lies on an edge row) and test connectivity. The first <code>i</code> where the two virtual nodes are connected is the last walkable day, so return it. This takes O(row &middot; col &middot; &alpha;) time. A binary search on the day with a BFS check is also accepted in practice but runs in O(row &middot; col &middot; log(row &middot; col))."],
    time="O(rc &middot; &alpha;(rc))", space="O(rc)",
    solution='''def lastDayToCross(row, col, cells):
    total = row * col
    top, bottom = total, total + 1
    parent = list(range(total + 2))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb

    land = [False] * total
    for i in range(total - 1, -1, -1):
        r, c = cells[i][0] - 1, cells[i][1] - 1
        idx = r * col + c
        land[idx] = True
        if r == 0:
            union(idx, top)
        if r == row - 1:
            union(idx, bottom)
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nr, nc = r + dr, c + dc
            if 0 <= nr < row and 0 <= nc < col and land[nr * col + nc]:
                union(idx, nr * col + nc)
        if find(top) == find(bottom):
            return i
    return 0
''',
    tests=[[2, 2, [[1, 1], [2, 1], [1, 2], [2, 2]]], [1, 1, [[1, 1]]], [1, 3, [[1, 2], [1, 1], [1, 3]]], [3, 1, [[2, 1], [1, 1], [3, 1]]],
           [3, 3, [[1, 2], [2, 1], [3, 3], [2, 2], [1, 1], [1, 3], [3, 1], [2, 3], [3, 2]]],
           [2, 3, [[1, 1], [1, 2], [1, 3], [2, 1], [2, 2], [2, 3]]], [2, 3, [[2, 2], [1, 2], [1, 1], [2, 1], [1, 3], [2, 3]]],
           [3, 2, [[1, 1], [2, 1], [3, 1], [1, 2], [2, 2], [3, 2]]], [4, 4, [[2, 2], [2, 3], [3, 2], [3, 3], [1, 1], [4, 4], [1, 4], [4, 1], [1, 2], [1, 3], [2, 1], [2, 4], [3, 1], [3, 4], [4, 2], [4, 3]]]],
)
_r = rnd(8309)


def _perm(R, C):
    c = [[i, j] for i in range(1, R + 1) for j in range(1, C + 1)]
    _r.shuffle(c)
    return c


p["tests"].append([60, 60, _perm(60, 60)])
p["tests"].append([45, 50, _perm(45, 50)])
p["tests"].append([50, 40, [[i, j] for j in range(1, 41) for i in range(1, 51)]])  # column by column
p["tests"].append([30, 30, [[i, j] for i in range(30, 0, -1) for j in range(1, 31)]])  # bottom row first


def b_ldc(row, col, cells):
    best = 0
    for d in range(row * col + 1):
        water = {tuple(c) for c in cells[:d]}
        seen = set()
        st = [(1, c) for c in range(1, col + 1) if (1, c) not in water]
        seen.update(st)
        ok = False
        while st:
            r, c = st.pop()
            if r == row:
                ok = True
                break
            for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                a, b = r + dr, c + dc
                if 1 <= a <= row and 1 <= b <= col and (a, b) not in water and (a, b) not in seen:
                    seen.add((a, b))
                    st.append((a, b))
        if ok:
            best = d
    return best


def g_ldc(r):
    R, C = r.randint(1, 5), r.randint(1, 5)
    c = [[i, j] for i in range(1, R + 1) for j in range(1, C + 1)]
    r.shuffle(c)
    return [R, C, c]


def v_ldc(tests):
    for t in tests:
        R, C, cells = t["args"]
        assert 1 <= R <= 60 and 1 <= C <= 60 and len(cells) == R * C
        assert {tuple(c) for c in cells} == {(i, j) for i in range(1, R + 1) for j in range(1, C + 1)}
        assert 0 <= t["expected"] < R * C


CHECKS["last-day-to-cross-flooding-grid"] = (b_ldc, g_ldc, "exact")
VALIDATE["last-day-to-cross-flooding-grid"] = v_ldc

# ---------------------------------------------------------------- bricks falling when hit
p = add(
    id="bricks-falling-when-hit", title="Bricks Falling When Hit", diff="Hard", topic=TOPIC, tier="extra",
    fn="hitBricks", params=[("grid", "int[][]"), ("hits", "int[][]")], ret="int[]", cmp="exact",
    desc="<p>A wall is a binary grid: <code>1</code> is a brick and <code>0</code> is empty. A brick is <strong>stable</strong> if it is in the top row (row 0), or if it shares a side (up, down, left, right) with a stable brick. Any brick that is not stable falls immediately and disappears. At the start every brick of the grid is stable.</p><p>You are given a list <code>hits</code> of distinct cells. Apply them in order: hit <code>[r, c]</code> removes the brick at that cell (if the cell is empty or its brick has already fallen, nothing happens), and afterwards every brick that is no longer stable falls. Return an array where the <code>k</code>-th element is the number of bricks that fall because of the <code>k</code>-th hit, <em>not</em> counting the hit brick itself.</p><pre>grid = [[1,0,0,0],\n        [1,1,1,0]]\nhits = [[1,0]]\n\nresult = [2]</pre><p>Removing the brick at (1,0) leaves (1,1) and (1,2) hanging with no stable neighbour, so both fall.</p>",
    constraints=["1 &le; grid.length, grid[0].length &le; 60", "grid[r][c] is 0 or 1, and every brick is stable in the initial grid", "1 &le; hits.length &le; 3,000", "hits are distinct cells inside the grid"],
    hints=["Simulating each hit with a fresh search from the top row costs O(rc) per hit and can be too slow. Think about how to avoid searching again after every hit.",
           "Go in reverse: if you first remove all hit bricks and then put them back from the last hit to the first, bricks only become connected, never disconnected.",
           "Build a union-find on the wall after all hits, with a virtual 'roof' node connected to the top row, keeping component sizes. Re-adding hit brick k connects it to its neighbours; the number of bricks that fall for that hit is the growth of the roof component minus one (the brick itself), but never below zero."],
    editorial=["Falling bricks are hard to model forward, but the reverse view is clean. First delete every brick listed in <code>hits</code> from the grid (remember which hit cells actually held a brick). Build a union-find over the remaining bricks plus a virtual ROOF node united with all bricks in row 0, and track set sizes. The size of the ROOF set counts exactly the stable bricks after all hits.",
               "Now undo the hits from last to first. For hit <code>k</code> whose cell originally held a brick: record <code>before = size(ROOF set)</code>, place the brick back, union it with the ROOF if it is in row 0, and union it with each existing neighbour. Let <code>after = size(ROOF set)</code>. Everything that joined the roof set apart from the brick itself had been falling due to this very hit, so the answer for hit <code>k</code> is <code>max(0, after - before - 1)</code>. The max handles a restored brick that is still not attached to the roof. Hits on empty cells answer 0. Total time is O(rc + h) &middot; &alpha; for h hits."],
    time="O((rc + h) &middot; &alpha;(rc))", space="O(rc)",
    solution='''def hitBricks(grid, hits):
    R, C = len(grid), len(grid[0])
    roof = R * C
    parent = list(range(R * C + 1))
    size = [1] * (R * C + 1)

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            if size[ra] < size[rb]:
                ra, rb = rb, ra
            parent[rb] = ra
            size[ra] += size[rb]

    g = [row[:] for row in grid]
    for r, c in hits:
        g[r][c] -= 1          # 1 -> 0 (brick removed), 0 -> -1 (was already empty)
    for r in range(R):
        for c in range(C):
            if g[r][c] == 1:
                if r == 0:
                    union(r * C + c, roof)
                if r > 0 and g[r - 1][c] == 1:
                    union(r * C + c, (r - 1) * C + c)
                if c > 0 and g[r][c - 1] == 1:
                    union(r * C + c, r * C + c - 1)
    out = [0] * len(hits)
    for k in range(len(hits) - 1, -1, -1):
        r, c = hits[k]
        if grid[r][c] == 0:
            continue
        before = size[find(roof)]
        g[r][c] = 1
        if r == 0:
            union(r * C + c, roof)
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nr, nc = r + dr, c + dc
            if 0 <= nr < R and 0 <= nc < C and g[nr][nc] == 1:
                union(r * C + c, nr * C + nc)
        after = size[find(roof)]
        out[k] = max(0, after - before - 1)
    return out
''',
    tests=[[[[1, 0, 0, 0], [1, 1, 1, 0]], [[1, 0]]], [[[1, 0, 0, 0], [1, 1, 0, 0]], [[1, 1], [1, 0]]], [[[1]], [[0, 0]]], [[[0]], [[0, 0]]],
           [[[1, 1, 1]], [[0, 1]]], [[[1], [1], [1], [1]], [[1, 0], [3, 0], [2, 0]]], [[[1, 1], [1, 1]], [[1, 0], [1, 1], [0, 0]]],
           [[[1, 1, 1], [0, 1, 0], [0, 1, 0]], [[1, 1], [0, 1]]], [[[1, 0, 1], [1, 1, 1], [1, 0, 1]], [[1, 1], [1, 0], [1, 2], [2, 0]]],
           [[[0, 1, 0], [1, 1, 1], [0, 1, 0]], [[0, 1], [1, 1], [2, 1], [1, 0]]], [[[1, 1, 0, 0], [0, 1, 0, 0], [0, 1, 1, 1], [0, 0, 0, 1]], [[1, 1], [2, 1], [2, 2]]]],
)
_r = rnd(8310)
_g = _stabilize([[1 if _r.random() < 0.72 else 0 for _ in range(60)] for _ in range(60)])
_cells = [[i, j] for i in range(60) for j in range(60)]
_h = _r.sample(_cells, 1500)
p["tests"].append([_g, _h])
_g = [[1] * 50 for _ in range(50)]
_cells = [[i, j] for i in range(50) for j in range(50)]
p["tests"].append([_g, [[0, 0]] + _r.sample(_cells[1:], 900)])
_g = [[1] * 40 if i % 2 == 0 else ([1 if j in (0, 39) else 0 for j in range(40)]) for i in range(40)]  # snake-like wall
p["tests"].append([_g, [[i, 0 if (i // 2) % 2 == 1 else 39] for i in range(1, 40, 2)] + [[0, j] for j in range(0, 40, 3)]])
_g = _stabilize([[1 if _r.random() < 0.7 else 0 for _ in range(30)] for _ in range(50)])
_h = _r.sample([[i, j] for i in range(50) for j in range(30)], 700)
p["tests"].append([_g, _h])


def b_hit(grid, hits):
    R, C = len(grid), len(grid[0])
    g = [row[:] for row in grid]

    def stable_set():
        seen = set()
        st = [(0, c) for c in range(C) if g[0][c] == 1]
        seen.update(st)
        while st:
            r, c = st.pop()
            for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                a, b = r + dr, c + dc
                if 0 <= a < R and 0 <= b < C and g[a][b] == 1 and (a, b) not in seen:
                    seen.add((a, b))
                    st.append((a, b))
        return seen

    out = []
    for r, c in hits:
        g[r][c] = 0
        keep = stable_set()
        fell = 0
        for i in range(R):
            for j in range(C):
                if g[i][j] == 1 and (i, j) not in keep:
                    g[i][j] = 0
                    fell += 1
        out.append(fell)
    return out


def g_hit(r):
    R, C = r.randint(1, 5), r.randint(1, 5)
    g = _stabilize([[1 if r.random() < 0.7 else 0 for _ in range(C)] for _ in range(R)])
    cells = [[i, j] for i in range(R) for j in range(C)]
    return [g, r.sample(cells, r.randint(1, min(len(cells), 8)))]


def v_hit(tests):
    for t in tests:
        g, h = t["args"]
        R, C = len(g), len(g[0])
        assert 1 <= R <= 60 and 1 <= C <= 60 and all(len(row) == C for row in g)
        assert all(v in (0, 1) for row in g for v in row)
        assert g == _stabilize(g), "initial wall must be stable"
        assert 1 <= len(h) <= 3000 and len({tuple(x) for x in h}) == len(h)
        assert all(0 <= r < R and 0 <= c < C for r, c in h)
        assert len(t["expected"]) == len(h)


CHECKS["bricks-falling-when-hit"] = (b_hit, g_hit, "exact")
VALIDATE["bricks-falling-when-hit"] = v_hit

# ---------------------------------------------------------------- restricted friend requests
p = add(
    id="restricted-friend-requests", title="Restricted Friend Requests", diff="Hard", topic=TOPIC, tier="extra",
    fn="processRequests", params=[("n", "int"), ("restrictions", "int[][]"), ("requests", "int[][]")], ret="int[]", cmp="exact",
    desc="<p>A social network has <code>n</code> users numbered <code>0</code> to <code>n - 1</code>, with no friendships at the start. A pair <code>[x, y]</code> in <code>restrictions</code> means that <code>x</code> and <code>y</code> must <strong>never</strong> be connected, neither directly nor through a chain of friends.</p><p>The friend requests <code>requests[k] = [u, v]</code> are handled one by one in order. A request is <em>approved</em> if, after making <code>u</code> and <code>v</code> friends, no restricted pair would be connected; otherwise it is <em>rejected</em> and nothing changes. An approved request makes the friendship permanent. A request between users who are already connected (directly or indirectly) is always approved.</p><p>Return an array with <code>1</code> for each approved request and <code>0</code> for each rejected one.</p><pre>n = 4\nrestrictions = [[0,3]]\nrequests = [[0,1],[1,2],[2,3],[3,1]]\n\nresult = [1,1,0,0]</pre><p>After the first two requests {0,1,2} are connected. Linking 2 and 3 would connect 0 with 3, so it is rejected, and so is 3-1 for the same reason.</p>",
    constraints=["2 &le; n &le; 1,000", "1 &le; restrictions.length &le; 200", "1 &le; requests.length &le; 400", "All pairs have two different users in the range [0, n - 1]"],
    hints=["After a request you may need to know whether any restricted pair has become connected. Checking the whole graph with a BFS each time is wasteful.",
           "Only the merge of the two components of <code>u</code> and <code>v</code> can create a violation. You can test the hypothetical merge without performing it.",
           "Keep a union-find. For a request with different roots <code>ru, rv</code>, look at every restriction <code>(x, y)</code>: if <code>{find(x), find(y)} == {ru, rv}</code> the merge would connect a forbidden pair, so reject. Otherwise union and approve."],
    editorial=["A restriction can only be violated at the moment two components are merged, and the only way to violate <code>(x, y)</code> by merging components A and B is that x is in one of them and y in the other. So for a request with <code>ru = find(u) != rv = find(v)</code> we scan the restrictions and reject if some pair has its two roots equal to <code>{ru, rv}</code> (in either order). If no restriction blocks it, we union the sets and answer 1.",
               "If the roots are already equal the request changes nothing and is approved. The scan costs O(R) per request, so the total is O(Q &middot; R &middot; &alpha;(n)), about 160,000 find operations at the stated limits. For much larger inputs you could store, per component, the set of components it is forbidden from joining and merge these sets small-to-large; the plain scan is the standard solution at these sizes."],
    time="O(Q &middot; R &middot; &alpha;(n))", space="O(n)",
    solution='''def processRequests(n, restrictions, requests):
    parent = list(range(n))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    out = []
    for u, v in requests:
        ru, rv = find(u), find(v)
        if ru == rv:
            out.append(1)
            continue
        ok = True
        for x, y in restrictions:
            fx, fy = find(x), find(y)
            if (fx == ru and fy == rv) or (fx == rv and fy == ru):
                ok = False
                break
        if ok:
            parent[ru] = rv
        out.append(1 if ok else 0)
    return out
''',
    tests=[[4, [[0, 3]], [[0, 1], [1, 2], [2, 3], [3, 1]]], [2, [[0, 1]], [[0, 1], [1, 0]]], [3, [[0, 1]], [[0, 2], [2, 1], [1, 2], [0, 2]]],
           [3, [[0, 1]], [[1, 2], [0, 2], [0, 2]]], [5, [[0, 4], [1, 3]], [[0, 1], [3, 4], [1, 2], [2, 4], [2, 3], [0, 3]]],
           [5, [[0, 1], [0, 1]], [[2, 3], [3, 4], [4, 0], [1, 2], [4, 1]]], [4, [[0, 1], [2, 3]], [[0, 2], [1, 3], [0, 3], [1, 2], [0, 1], [2, 3]]],
           [6, [[0, 5]], [[0, 1], [1, 2], [3, 4], [4, 5], [2, 3], [2, 5], [1, 4]]], [3, [[1, 2]], [[0, 1], [0, 2], [1, 0], [2, 0]]],
           [7, [[0, 6], [2, 4], [1, 5]], [[0, 1], [2, 3], [4, 5], [3, 4], [1, 2], [5, 6], [3, 5], [0, 6]]]],
)
_r = rnd(8311)
for _n, _R, _Q in [(1000, 200, 400), (30, 200, 400), (60, 200, 400), (150, 200, 400), (90, 100, 300)]:
    p["tests"].append([_n, _rand_edges(_r, _n, _R), _rand_edges(_r, _n, _Q)])


def b_prq(n, restrictions, requests):
    friends = []
    out = []

    def comp_of(edges):
        lab = list(range(n))
        changed = True
        while changed:
            changed = False
            for u, v in edges:
                m = min(lab[u], lab[v])
                if lab[u] != m or lab[v] != m:
                    lab[u] = lab[v] = m
                    changed = True
        return lab

    for u, v in requests:
        lab = comp_of(friends + [[u, v]])
        if all(lab[x] != lab[y] for x, y in restrictions):
            friends.append([u, v])
            out.append(1)
        else:
            out.append(0)
    return out


def g_prq(r):
    n = r.randint(2, 7)
    return [n, [r.sample(range(n), 2) for _ in range(r.randint(1, 4))], [r.sample(range(n), 2) for _ in range(r.randint(1, 9))]]


def v_prq(tests):
    for t in tests:
        n, rs, rq = t["args"]
        assert 2 <= n <= 1000 and 1 <= len(rs) <= 200 and 1 <= len(rq) <= 400
        assert all(0 <= a < n and 0 <= b < n and a != b for a, b in rs + rq)
        assert len(t["expected"]) == len(rq)


CHECKS["restricted-friend-requests"] = (b_prq, g_prq, "exact")
VALIDATE["restricted-friend-requests"] = v_prq
