"""Problems: graphs, topological sorting and DAGs. See data/lib.py for the registry."""
import heapq
from itertools import combinations, permutations

from lib import add, rnd, CHECKS, VALIDATE, gen_arr  # noqa: F401

MOD = 10 ** 9 + 7
T = "Graphs"


# ---------------------------------------------------------------- shared helpers

def _dag(r, n, m, local=None, extra_chain=0.0):
    """Random acyclic edge list (u, v), u before v in a hidden random order. `local` limits how far apart
    (in the hidden order) the endpoints are, which makes long chains likely."""
    perm = list(range(n))
    r.shuffle(perm)
    s = set()
    if n < 2:
        return [], perm
    for i in range(n - 1):
        if r.random() < extra_chain:
            s.add((perm[i], perm[i + 1]))
    tries = 0
    while len(s) < m and tries < 30 * m + 30:
        tries += 1
        i = r.randrange(n - 1)
        j = r.randint(i + 1, min(n - 1, i + local)) if local else r.randint(i + 1, n - 1)
        s.add((perm[i], perm[j]))
    e = sorted(s)
    r.shuffle(e)
    return e, perm


def _is_acyclic(n, edges):
    indeg = [0] * n
    adj = [[] for _ in range(n)]
    for a, b in edges:
        adj[a].append(b)
        indeg[b] += 1
    st = [i for i in range(n) if indeg[i] == 0]
    done = 0
    while st:
        u = st.pop()
        done += 1
        for v in adj[u]:
            indeg[v] -= 1
            if indeg[v] == 0:
                st.append(v)
    return done == n


def _closure(n, edges):
    """reach[i][j] is True when a walk of at least one edge leads from i to j (Floyd-Warshall)."""
    reach = [[False] * n for _ in range(n)]
    for e in edges:
        reach[e[0]][e[1]] = True
    for k in range(n):
        for i in range(n):
            if reach[i][k]:
                for j in range(n):
                    if reach[k][j]:
                        reach[i][j] = True
    return reach


def _rand_pairs(r, n, m, loops=True):
    out = []
    for _ in range(m):
        a, b = r.randrange(n), r.randrange(n)
        if not loops and a == b:
            continue
        out.append([a, b])
    return out


# ================================================================ EASY

# ---------------------------------------------------------------- is it a topological order
p = add(
    id="is-valid-topological-order", title="Is This a Valid Topological Order?", diff="Easy", topic=T,
    fn="isTopologicalOrder", params=[("n", "int"), ("edges", "int[][]"), ("order", "int[]")], ret="bool", cmp="exact",
    desc="<p>A directed graph has <code>n</code> nodes labelled <code>0</code> to <code>n - 1</code>. Each entry <code>edges[i] = [a, b]</code> is a one-way edge from <code>a</code> to <code>b</code>. The graph may contain cycles and self-loops.</p><p>A <em>topological order</em> is a list that contains every node exactly once and in which, for every edge <code>[a, b]</code>, node <code>a</code> appears <strong>before</strong> node <code>b</code>. You are given a candidate list <code>order</code> of exactly <code>n</code> values, each between <code>0</code> and <code>n - 1</code>, but values may repeat. Return <code>true</code> if <code>order</code> is a topological order of the graph and <code>false</code> otherwise.</p><pre>n = 4, edges = [[0,1],[0,2],[1,3],[2,3]], order = [0,2,1,3] -> true\nn = 4, edges = [[0,1],[0,2],[1,3],[2,3]], order = [0,1,3,2] -> false\nn = 3, edges = [[0,1]],                   order = [0,1,1]   -> false</pre>",
    constraints=["1 &le; n &le; 2,000", "0 &le; edges.length &le; 4,000", "0 &le; a, b &lt; n; self-loops and repeated edges are allowed", "order.length = n and 0 &le; order[i] &lt; n"],
    hints=["Two things must hold: every node occurs exactly once, and every edge points forward in the list. Check them one at a time.",
           "To test an edge quickly you need to know where each node sits in <code>order</code>. Build a lookup <code>pos[node]</code> instead of searching the list for every edge.",
           "Fill <code>pos</code> while checking that no node appears twice (this also proves every node appears, because the length is n). Then return <code>false</code> as soon as an edge has <code>pos[a] &ge; pos[b]</code>. A self-loop always fails this test."],
    editorial=["First make sure <code>order</code> is a permutation of the nodes. It has n entries in range, so it is a permutation exactly when no value repeats. While scanning, store the position of each node in <code>pos</code> and fail on a repeat.",
               "Then every edge <code>[a, b]</code> must satisfy <code>pos[a] &lt; pos[b]</code>. If all edges pass, each node's predecessors come before it, which is the definition of a topological order. A graph with a cycle can never pass, because following the cycle would need positions that increase forever; a self-loop fails immediately since <code>pos[a] &lt; pos[a]</code> is false. Total work is O(n + m) time and O(n) space."],
    time="O(n + m)", space="O(n)",
    solution='''def isTopologicalOrder(n, edges, order):
    pos = [-1] * n
    for i, v in enumerate(order):
        if pos[v] != -1:
            return False
        pos[v] = i
    for a, b in edges:
        if pos[a] >= pos[b]:
            return False
    return True
''',
    tests=[[4, [[0, 1], [0, 2], [1, 3], [2, 3]], [0, 2, 1, 3]],
           [4, [[0, 1], [0, 2], [1, 3], [2, 3]], [0, 1, 3, 2]],
           [3, [[0, 1]], [0, 1, 1]],
           [1, [], [0]],
           [1, [[0, 0]], [0]],
           [3, [[0, 1], [1, 2], [2, 0]], [0, 1, 2]],
           [3, [], [2, 0, 1]],
           [5, [[4, 3], [3, 2], [2, 1], [1, 0]], [4, 3, 2, 1, 0]],
           [5, [[4, 3], [3, 2], [2, 1], [1, 0]], [0, 1, 2, 3, 4]],
           [4, [[0, 1], [0, 1], [2, 3]], [2, 0, 3, 1]],
           [2, [[0, 1]], [0, 0]],
           [6, [[0, 5], [5, 1], [1, 4], [4, 2], [2, 3]], [0, 5, 1, 4, 2, 3]]],
)
_r = rnd(9001)
_e, _perm = _dag(_r, 2000, 3000)
p["tests"].append([2000, _e, _perm])
_bad = _perm[:]
_i = _r.randrange(1999)
_bad[_i], _bad[_i + 1] = _bad[_i + 1], _bad[_i]
_u, _v = _perm[_i], _perm[_i + 1]
p["tests"].append([2000, _e + [[_u, _v]], _bad])  # swap breaks the added edge _u -> _v, so this one is false
_dup = _perm[:]
_dup[1500] = _dup[10]
p["tests"].append([2000, _e[:1500], _dup])


def b_validorder(n, edges, order):
    if sorted(order) != list(range(n)):
        return False
    return all(order.index(a) < order.index(b) for a, b in edges)


def g_validorder(r):
    n = r.randint(1, 6)
    if r.random() < 0.7:
        e, perm = _dag(r, n, r.randint(0, 2 * n))
        e = [list(x) for x in e]
        order = perm[:]
        roll = r.random()
        if roll < 0.3 and n > 1:
            i, j = r.sample(range(n), 2)
            order[i], order[j] = order[j], order[i]
        elif roll < 0.4:
            order[r.randrange(n)] = r.randrange(n)
    else:
        e = _rand_pairs(r, n, r.randint(0, 2 * n))
        order = list(range(n))
        r.shuffle(order)
    return [n, e, order]


def v_validorder(tests):
    t_cnt = 0
    for t in tests:
        n, edges, order = t["args"]
        assert 1 <= n <= 2000 and len(edges) <= 4000 and len(order) == n
        assert all(0 <= a < n and 0 <= b < n for a, b in edges)
        assert all(0 <= v < n for v in order)
        t_cnt += t["expected"]
    assert 0 < t_cnt < len(tests), "need both answers"


CHECKS["is-valid-topological-order"] = (b_validorder, g_validorder, "exact")
VALIDATE["is-valid-topological-order"] = v_validorder

# ---------------------------------------------------------------- minimum starting nodes
p = add(
    id="minimum-starting-nodes-to-reach-all", title="Smallest Set of Starting Nodes", diff="Easy", topic=T,
    fn="startingNodes", params=[("n", "int"), ("edges", "int[][]")], ret="int[]", cmp="exact",
    desc="<p>A directed acyclic graph (DAG) has <code>n</code> nodes labelled <code>0</code> to <code>n - 1</code>. Each entry <code>edges[i] = [a, b]</code> is a one-way edge from <code>a</code> to <code>b</code>.</p><p>You want to choose a set of <em>starting nodes</em> so that every node of the graph can be reached by following edges from at least one starting node (a starting node reaches itself). Find the set with the <strong>fewest</strong> nodes. It is unique; return its nodes in increasing order.</p><pre>n = 6, edges = [[0,1],[0,2],[2,5],[3,4],[4,2]] -> [0,3]\nn = 3, edges = []                             -> [0,1,2]\nn = 4, edges = [[0,1],[1,2],[2,3]]            -> [0]</pre>",
    constraints=["1 &le; n &le; 2,000", "0 &le; edges.length &le; 4,000", "0 &le; a, b &lt; n and a &ne; b", "The graph is acyclic and no ordered pair [a, b] appears twice"],
    hints=["Some nodes can never be reached from any other node. What do they have to do with the answer?",
           "A node with an incoming edge is reachable from the node at the other end of that edge. A node with no incoming edge can only be reached by starting at it.",
           "Every node of in-degree 0 must be a starting node. Because the graph is acyclic, following edges backwards from any node must end at an in-degree 0 node, so these nodes are also enough. Return all nodes that never appear as the target <code>b</code> of an edge."],
    editorial=["A node without incoming edges can be reached only by starting there, so all of them must be in the set. That gives a lower bound.",
               "They also suffice. Take any node and walk backwards along an incoming edge as long as there is one. The graph has no cycle, so this walk cannot revisit a node and must stop at a node with no incoming edge, which is a source. Following the same walk forwards shows the source reaches the node we started from.",
               "So the answer is exactly the set of nodes of in-degree 0: mark every edge target, then list the unmarked nodes in increasing order. This takes O(n + m) time. Without the acyclic guarantee the problem would be harder, since a cycle with no entry would need a starting node of its own."],
    time="O(n + m)", space="O(n)",
    solution='''def startingNodes(n, edges):
    has_in = [False] * n
    for a, b in edges:
        has_in[b] = True
    return [i for i in range(n) if not has_in[i]]
''',
    tests=[[6, [[0, 1], [0, 2], [2, 5], [3, 4], [4, 2]]],
           [3, []],
           [4, [[0, 1], [1, 2], [2, 3]]],
           [1, []],
           [2, [[1, 0]]],
           [5, [[0, 4], [1, 4], [2, 4], [3, 4]]],
           [5, [[4, 0], [4, 1], [4, 2], [4, 3]]],
           [6, [[0, 1], [1, 2], [0, 2], [3, 4], [4, 5], [3, 5]]],
           [7, [[5, 3], [3, 1], [1, 6], [6, 0], [0, 2], [2, 4]]]],
)
_r = rnd(9002)
p["tests"].append([2000, _dag(_r, 2000, 2500)[0]])
p["tests"].append([2000, _dag(_r, 2000, 4000, local=50, extra_chain=0.9)[0]])
p["tests"].append([2000, [[i, i + 1] for i in range(1999)]])


def b_starting(n, edges):
    reach = _closure(n, edges)
    return [j for j in range(n) if not any(reach[i][j] for i in range(n))]


def g_starting(r):
    n = r.randint(1, 8)
    e, _ = _dag(r, n, r.randint(0, 2 * n))
    return [n, [list(x) for x in e]]


def v_starting(tests):
    for t in tests:
        n, edges = t["args"]
        assert 1 <= n <= 2000 and len(edges) <= 4000
        assert all(0 <= a < n and 0 <= b < n and a != b for a, b in edges)
        assert len({(a, b) for a, b in edges}) == len(edges)
        assert _is_acyclic(n, edges)


CHECKS["minimum-starting-nodes-to-reach-all"] = (b_starting, g_starting, "exact")
VALIDATE["minimum-starting-nodes-to-reach-all"] = v_starting

# ================================================================ MEDIUM

# ---------------------------------------------------------------- Course Schedule II, smallest order
p = add(
    id="course-order-lexicographically-smallest", title="Course Order, Smallest First", diff="Medium", topic=T, tier="must",
    fn="findOrder", params=[("numCourses", "int"), ("prerequisites", "int[][]")], ret="int[]", cmp="exact",
    desc="<p>There are <code>numCourses</code> courses numbered <code>0</code> to <code>numCourses - 1</code>. Each entry <code>prerequisites[i] = [a, b]</code> means course <code>b</code> must be completed <strong>before</strong> course <code>a</code> can be taken. Pairs may repeat. You take one course at a time.</p><p>Return an order in which all courses can be taken so that every course comes after all of its prerequisites. Often many orders work, so return the <strong>lexicographically smallest</strong> one: comparing two orders, look at the first position where they differ, and the order with the smaller course number there is smaller.</p><p>If the courses cannot all be completed because of a circular dependency, return an empty array.</p><pre>numCourses = 4, prerequisites = [[1,0],[2,0],[3,1],[3,2]] -> [0,1,2,3]\nnumCourses = 3, prerequisites = [[0,1],[1,2]]             -> [2,1,0]\nnumCourses = 3, prerequisites = [[1,0],[2,0]]             -> [0,1,2]\nnumCourses = 2, prerequisites = [[0,1],[1,0]]             -> []</pre>",
    constraints=["1 &le; numCourses &le; 2,000", "0 &le; prerequisites.length &le; 5,000", "0 &le; a, b &lt; numCourses; a pair may name the same course twice (that makes the answer empty)"],
    hints=["Which courses can you take first? Once you take one, which other courses may become available?",
           "Count, for every course, how many of its prerequisites are still missing. A course is available when that count is 0. Taking a course lowers the count of every course that depends on it.",
           "Several courses can be available at once. Always pick the smallest available number: keep the available courses in a min-heap. If you finish with fewer than numCourses courses taken, a cycle blocks the rest, so return an empty array."],
    editorial=["This is Kahn's topological sort. Build for every course the list of courses that depend on it, and the number of unmet prerequisites (<code>indeg</code>). Start with all courses of indegree 0, take one, and decrease the indegree of its dependents; any dependent reaching 0 becomes available.",
               "To get the lexicographically smallest order, make the choice at each step greedily: take the smallest available number. This is correct because any course that is available now will still be available later (availability never disappears), so placing the smallest one first can only be compared with orders that place a larger one first, and swapping the smaller course forward keeps the order valid and makes it smaller. A min-heap supplies the smallest available course in O(log n).",
               "If the loop ends with fewer than <code>numCourses</code> courses taken, the remaining courses all have an unmet prerequisite inside the remaining set, which means they lie on or behind a cycle; return <code>[]</code>. Repeated pairs are counted twice in the indegree and decreased twice, so they cause no trouble. Time is O((n + m) log n), space O(n + m)."],
    time="O((n + m) log n)", space="O(n + m)",
    solution='''import heapq


def findOrder(numCourses, prerequisites):
    adj = [[] for _ in range(numCourses)]
    indeg = [0] * numCourses
    for a, b in prerequisites:
        adj[b].append(a)
        indeg[a] += 1
    heap = [i for i in range(numCourses) if indeg[i] == 0]
    heapq.heapify(heap)
    order = []
    while heap:
        u = heapq.heappop(heap)
        order.append(u)
        for v in adj[u]:
            indeg[v] -= 1
            if indeg[v] == 0:
                heapq.heappush(heap, v)
    return order if len(order) == numCourses else []
''',
    tests=[[4, [[1, 0], [2, 0], [3, 1], [3, 2]]],
           [3, [[0, 1], [1, 2]]],
           [3, [[1, 0], [2, 0]]],
           [2, [[0, 1], [1, 0]]],
           [1, []],
           [1, [[0, 0]]],
           [5, []],
           [4, [[0, 3], [0, 3], [1, 3], [2, 1]]],
           [6, [[5, 4], [4, 3], [3, 2], [2, 1], [1, 0]]],
           [6, [[0, 5], [1, 5], [2, 4], [3, 4], [4, 0]]],
           [5, [[1, 0], [2, 1], [3, 2], [1, 4], [4, 3]]],
           [7, [[6, 5], [5, 4], [4, 6], [1, 0]]]],
)
_r = rnd(9003)
_e, _ = _dag(_r, 2000, 3000)
p["tests"].append([2000, [[v, u] for u, v in _e]])
_e, _ = _dag(_r, 1800, 2600, local=30, extra_chain=0.5)
p["tests"].append([1800, [[v, u] for u, v in _e]])
_e, _perm = _dag(_r, 2000, 2400)
_cyc = [[v, u] for u, v in _e]
_cyc.append([_e[7][0], _e[7][1]])  # closes a two-cycle with edge _e[7]
p["tests"].append([2000, _cyc])


def b_findorder(n, pre):
    for perm in permutations(range(n)):  # permutations come out in lexicographic order
        pos = {v: i for i, v in enumerate(perm)}
        if all(pos[b] < pos[a] for a, b in pre):
            return list(perm)
    return []


def g_findorder(r):
    n = r.randint(1, 6)
    if r.random() < 0.6:
        e, _ = _dag(r, n, r.randint(0, 2 * n))
        return [n, [[v, u] for u, v in e]]
    return [n, _rand_pairs(r, n, r.randint(0, 6))]


def v_findorder(tests):
    nonempty = 0
    for t in tests:
        n, pre = t["args"]
        assert 1 <= n <= 2000 and len(pre) <= 5000
        assert all(0 <= a < n and 0 <= b < n for a, b in pre)
        out = t["expected"]
        acyclic = _is_acyclic(n, [(b, a) for a, b in pre])
        assert (out != []) == acyclic
        if out:
            nonempty += 1
            pos = {v: i for i, v in enumerate(out)}
            assert sorted(out) == list(range(n))
            assert all(pos[b] < pos[a] for a, b in pre)
    assert 0 < nonempty < len(tests)


CHECKS["course-order-lexicographically-smallest"] = (b_findorder, g_findorder, "exact")
VALIDATE["course-order-lexicographically-smallest"] = v_findorder

# ---------------------------------------------------------------- parallel courses
p = add(
    id="parallel-courses-minimum-semesters", title="Parallel Courses", diff="Medium", topic=T,
    fn="minSemesters", params=[("n", "int"), ("relations", "int[][]")], ret="int", cmp="exact",
    desc="<p>A university offers <code>n</code> courses numbered <code>0</code> to <code>n - 1</code>. Each entry <code>relations[i] = [prev, next]</code> means course <code>prev</code> is a prerequisite of course <code>next</code>: you must have <strong>finished</strong> <code>prev</code> in an earlier semester before you can take <code>next</code>.</p><p>In one semester you may take any number of courses, as long as all their prerequisites were completed in earlier semesters. Return the minimum number of semesters needed to finish all courses, or <code>-1</code> if it is impossible because of a circular dependency.</p><pre>n = 3, relations = [[0,2],[1,2]]        -> 2\nn = 4, relations = [[0,1],[1,2],[0,3]]  -> 3\nn = 3, relations = [[0,1],[1,2],[2,0]]  -> -1\nn = 5, relations = []                   -> 1</pre>",
    constraints=["1 &le; n &le; 2,000", "0 &le; relations.length &le; 4,000", "0 &le; prev, next &lt; n; a pair may be repeated, and prev may equal next (then the answer is -1)"],
    hints=["Imagine taking, in every semester, every course you are allowed to take. Is it ever a mistake to delay an available course?",
           "The first semester contains all courses without prerequisites. The second contains the courses whose prerequisites all lie in the first semester, and so on. Process the courses in these layers.",
           "Run Kahn's algorithm level by level: take all current indegree-0 courses as one semester, then collect the courses they free. Count the layers; if fewer than n courses were taken, return -1. The answer equals the length (in courses) of the longest prerequisite chain."],
    editorial=["Taking a course as soon as possible never hurts, since finishing it earlier can only unlock other courses sooner. So the schedule is forced: semester 1 holds every course with no prerequisites, semester 2 holds those whose prerequisites are all in semester 1, and so on.",
               "That is exactly a breadth-first topological sort by layers. Keep the indegree of each course and a list of current zero-indegree courses. For each round, count one semester, remove all courses in the list, and build the next list from the dependents whose indegree reaches 0. If the number of removed courses is less than n, the leftover courses lie on or behind a cycle and the answer is -1.",
               "Equivalently, the number of semesters is the number of courses on the longest path of the dependency graph, which can also be computed with a DP in topological order. Time and space are O(n + m)."],
    time="O(n + m)", space="O(n + m)",
    solution='''def minSemesters(n, relations):
    adj = [[] for _ in range(n)]
    indeg = [0] * n
    for a, b in relations:
        adj[a].append(b)
        indeg[b] += 1
    layer = [i for i in range(n) if indeg[i] == 0]
    taken = 0
    semesters = 0
    while layer:
        semesters += 1
        taken += len(layer)
        nxt = []
        for u in layer:
            for v in adj[u]:
                indeg[v] -= 1
                if indeg[v] == 0:
                    nxt.append(v)
        layer = nxt
    return semesters if taken == n else -1
''',
    tests=[[3, [[0, 2], [1, 2]]],
           [4, [[0, 1], [1, 2], [0, 3]]],
           [3, [[0, 1], [1, 2], [2, 0]]],
           [5, []],
           [1, []],
           [1, [[0, 0]]],
           [6, [[0, 1], [1, 2], [2, 3], [3, 4], [4, 5], [0, 5]]],
           [6, [[0, 1], [0, 2], [0, 3], [1, 4], [2, 4], [3, 4], [4, 5]]],
           [5, [[0, 1], [1, 0], [2, 3], [3, 4]]],
           [7, [[0, 3], [1, 3], [3, 5], [2, 4], [4, 5], [5, 6], [0, 3]]]],
)
_r = rnd(9004)
p["tests"].append([2000, _dag(_r, 2000, 2800)[0]])
p["tests"].append([2000, _dag(_r, 2000, 3500, local=6, extra_chain=0.98)[0]])
p["tests"].append([1800, [[i, i + 1] for i in range(1799)] + [[1799, 900]]])  # cycle at the end
p["tests"].append([2000, [[i, i + 1] for i in range(1999)]])


def b_semesters(n, rel):
    reach = _closure(n, rel)
    if any(reach[i][i] for i in range(n)):
        return -1
    adj = [[] for _ in range(n)]
    for a, b in rel:
        adj[a].append(b)

    def depth(u):
        return 1 + max((depth(v) for v in adj[u]), default=0)

    return max(depth(u) for u in range(n))


def g_semesters(r):
    n = r.randint(1, 7)
    if r.random() < 0.7:
        return [n, [list(x) for x in _dag(r, n, r.randint(0, 2 * n))[0]]]
    return [n, _rand_pairs(r, n, r.randint(0, 2 * n))]


def v_semesters(tests):
    seen = set()
    for t in tests:
        n, rel = t["args"]
        assert 1 <= n <= 2000 and len(rel) <= 4000
        assert all(0 <= a < n and 0 <= b < n for a, b in rel)
        seen.add(t["expected"] == -1)
    assert seen == {True, False}


CHECKS["parallel-courses-minimum-semesters"] = (b_semesters, g_semesters, "exact")
VALIDATE["parallel-courses-minimum-semesters"] = v_semesters

# ---------------------------------------------------------------- heaviest path in a weighted DAG
p = add(
    id="heaviest-path-in-weighted-dag", title="Heaviest Path in a Weighted DAG", diff="Medium", topic=T,
    fn="heaviestPath", params=[("n", "int"), ("edges", "int[][]")], ret="int", cmp="exact",
    desc="<p>A directed acyclic graph has <code>n</code> nodes labelled <code>0</code> to <code>n - 1</code>. Each entry <code>edges[i] = [a, b, w]</code> is a one-way edge from <code>a</code> to <code>b</code> with weight <code>w</code>, which may be negative. Two nodes may be joined by several edges with different weights.</p><p>A <em>path</em> is a sequence of nodes where consecutive nodes are joined by an edge; it may start and end at any nodes, and a single node is a path with no edges. The weight of a path is the sum of the weights of its edges. Return the largest weight of any path. Because a one-node path has weight 0, the answer is never negative.</p><pre>n = 5, edges = [[0,1,3],[1,2,-2],[1,3,4],[2,4,10],[3,4,1]] -> 11   (0 -> 1 -> 2 -> 4)\nn = 3, edges = [[0,1,-5],[1,2,-1]]                          -> 0\nn = 4, edges = [[0,1,2],[2,3,5],[1,3,2]]                    -> 5</pre>",
    constraints=["1 &le; n &le; 2,000", "0 &le; edges.length &le; 3,000", "0 &le; a, b &lt; n and a &ne; b; the graph is acyclic", "-1,000 &le; w &le; 1,000"],
    hints=["The graph has no cycles, so a best path to a node only depends on the nodes that come before it. Try to define the best path <em>ending</em> at each node.",
           "Let <code>best[v]</code> be the largest weight of a path ending at v. It is either 0 (start at v) or <code>best[u] + w</code> for some edge u &rarr; v with weight w.",
           "To use the recurrence, every u must be finished before v. Process nodes in topological order (Kahn's algorithm), pushing <code>best[u] + w</code> into <code>best[v]</code> along each edge. The answer is the maximum of all <code>best</code> values."],
    editorial=["Define <code>best[v]</code> as the maximum weight of a path that ends at v, starting anywhere. A path ending at v either consists of v alone (weight 0) or arrives through a last edge <code>u &rarr; v</code> of weight w, in which case the best choice for the earlier part is <code>best[u]</code>. Hence <code>best[v] = max(0, max over incoming edges of best[u] + w)</code>. The 0 option is what lets a path start fresh whenever the earlier part is negative.",
               "The recurrence needs every predecessor of v to be final before v is computed, which is guaranteed by processing nodes in topological order. Kahn's algorithm gives that order in O(n + m): start from the nodes of indegree 0, and when a node u is popped, relax each outgoing edge with <code>best[v] = max(best[v], best[u] + w)</code> and decrease the indegree of v.",
               "The answer is the maximum over all nodes of <code>best</code>. Parallel edges are handled automatically because each one is relaxed separately. The result fits easily in a 32-bit integer (at most 3,000 edges of weight 1,000, so below 3,000,000). A DFS with memoisation gives the same result but could recurse thousands of levels deep on a long chain."],
    time="O(n + m)", space="O(n + m)",
    solution='''def heaviestPath(n, edges):
    adj = [[] for _ in range(n)]
    indeg = [0] * n
    for a, b, w in edges:
        adj[a].append((b, w))
        indeg[b] += 1
    best = [0] * n
    stack = [i for i in range(n) if indeg[i] == 0]
    while stack:
        u = stack.pop()
        for v, w in adj[u]:
            if best[u] + w > best[v]:
                best[v] = best[u] + w
            indeg[v] -= 1
            if indeg[v] == 0:
                stack.append(v)
    return max(best)
''',
    tests=[[5, [[0, 1, 3], [1, 2, -2], [1, 3, 4], [2, 4, 10], [3, 4, 1]]],
           [3, [[0, 1, -5], [1, 2, -1]]],
           [4, [[0, 1, 2], [2, 3, 5], [1, 3, 2]]],
           [1, []],
           [2, [[1, 0, 7]]],
           [2, [[0, 1, 4], [0, 1, -3], [0, 1, 9]]],
           [5, [[0, 1, -10], [1, 2, 6], [2, 3, -1], [3, 4, 6]]],
           [6, [[5, 4, 1], [4, 3, 1], [3, 2, 1], [2, 1, 1], [1, 0, 1], [5, 0, 4]]],
           [6, [[0, 1, 5], [2, 3, 5], [4, 5, 5]]],
           [4, [[0, 1, -1], [1, 2, -1], [2, 3, -1]]]],
)
_r = rnd(9005)


def _weighted(r, n, m, local=None, extra_chain=0.0, lo=-1000, hi=1000):
    e, _ = _dag(r, n, m, local, extra_chain)
    return [[a, b, r.randint(lo, hi)] for a, b in e]


p["tests"].append([2000, _weighted(_r, 2000, 2800, local=40, extra_chain=0.9, lo=-300, hi=1000)])
p["tests"].append([1500, _weighted(_r, 1500, 2500)])
p["tests"].append([1500, [[i, i + 1, 1000] for i in range(1499)]])
p["tests"].append([1200, _weighted(_r, 1200, 1200, lo=-1000, hi=-1)])


def b_heaviest(n, edges):
    adj = [[] for _ in range(n)]
    for a, b, w in edges:
        adj[a].append((b, w))
    best = 0

    def go(u, total):
        nonlocal best
        best = max(best, total)
        for v, w in adj[u]:
            go(v, total + w)

    for s in range(n):
        go(s, 0)
    return best


def g_heaviest(r):
    n = r.randint(1, 7)
    e, _ = _dag(r, n, r.randint(0, 2 * n))
    out = [[a, b, r.randint(-6, 6)] for a, b in e]
    if out and r.random() < 0.3:
        a, b, _w = r.choice(out)
        out.append([a, b, r.randint(-6, 6)])
    return [n, out]


def v_heaviest(tests):
    for t in tests:
        n, edges = t["args"]
        assert 1 <= n <= 2000 and len(edges) <= 3000
        assert all(0 <= a < n and 0 <= b < n and a != b and -1000 <= w <= 1000 for a, b, w in edges)
        assert _is_acyclic(n, [(e[0], e[1]) for e in edges])
        assert t["expected"] >= 0


CHECKS["heaviest-path-in-weighted-dag"] = (b_heaviest, g_heaviest, "exact")
VALIDATE["heaviest-path-in-weighted-dag"] = v_heaviest

# ---------------------------------------------------------------- eventual safe nodes
p = add(
    id="eventual-safe-nodes", title="Eventually Safe Nodes", diff="Medium", topic=T,
    fn="eventualSafeNodes", params=[("graph", "int[][]")], ret="int[]", cmp="exact",
    desc="<p>A directed graph has <code>n = graph.length</code> nodes labelled <code>0</code> to <code>n - 1</code>. The list <code>graph[i]</code> contains the nodes that node <code>i</code> points to (the targets of the outgoing edges of <code>i</code>). A node with no outgoing edges is a <em>terminal</em> node.</p><p>A token starts on some node and keeps moving along outgoing edges, choosing any edge it likes at each step, until it reaches a terminal node (it stops there). A node is <em>safe</em> if <strong>every</strong> possible way of moving the token from that node is guaranteed to end in a terminal node after finitely many steps. In particular a terminal node is safe, and a node from which the token could circle forever is not safe.</p><p>Return all safe nodes in increasing order.</p><pre>graph = [[1,2],[2,3],[5],[0],[5],[],[]] -> [2,4,5,6]\ngraph = [[1,2,3,4],[1,2],[3,4],[0,4],[]] -> [4]\ngraph = [[],[0],[1]]                    -> [0,1,2]</pre>",
    constraints=["1 &le; n &le; 3,000", "The total number of edges is at most 8,000", "graph[i] contains distinct values in [0, n - 1]; it may contain i itself (a self-loop)"],
    hints=["A node is unsafe exactly when the token can wander into a cycle from it. What does that say about the nodes that <em>are</em> safe, in terms of the nodes they point to?",
           "A node is safe if all of its targets are safe (a terminal node has no targets, so it is vacuously safe). This is a 'peeling' process that starts from the terminal nodes.",
           "Reverse every edge and run Kahn's algorithm: use the out-degree of each node as its counter, start with the terminal nodes, and whenever a node is confirmed safe decrease the counter of every node that points to it. A node whose counter reaches 0 is safe. Finally sort the safe nodes."],
    editorial=["Call a node safe if all of its paths end. A terminal node is safe. A non-terminal node is safe exactly when each of its targets is safe: if one target is unsafe the token can go there and loop forever, and if all are safe every route ends. So safety can be discovered by repeatedly peeling off nodes whose targets are all known to be safe.",
               "Implement the peeling with a reversed graph. For each edge <code>i &rarr; j</code> record <code>i</code> in <code>rev[j]</code>, and let <code>remaining[i]</code> be the out-degree of i. Put all terminal nodes (remaining 0) in a queue. When a node j is popped it is safe: for each i in <code>rev[j]</code> decrease <code>remaining[i]</code>, and when it hits 0 every target of i is safe, so i is safe too and joins the queue.",
               "Nodes on a cycle, or with a path into a cycle, never reach 0, so they are never reported. The result is sorted before returning. A DFS with three colours (unvisited, in progress, done) is an alternative, but the reversed Kahn approach avoids deep recursion. Time and space are O(n + m) apart from the final sort."],
    time="O(n + m)", space="O(n + m)",
    solution='''def eventualSafeNodes(graph):
    n = len(graph)
    rev = [[] for _ in range(n)]
    remaining = [len(graph[i]) for i in range(n)]
    for i in range(n):
        for j in graph[i]:
            rev[j].append(i)
    stack = [i for i in range(n) if remaining[i] == 0]
    safe = []
    while stack:
        j = stack.pop()
        safe.append(j)
        for i in rev[j]:
            remaining[i] -= 1
            if remaining[i] == 0:
                stack.append(i)
    return sorted(safe)
''',
    tests=[[[[1, 2], [2, 3], [5], [0], [5], [], []]],
           [[[1, 2, 3, 4], [1, 2], [3, 4], [0, 4], []]],
           [[[], [0], [1]]],
           [[[]]],
           [[[0]]],
           [[[1], [0]]],
           [[[1], [2], [3], []]],
           [[[1], [2], [3], [1], []]],
           [[[1, 2], [3], [3], [4], [2]]],
           [[[], [], [0, 1], [2, 3], [3]]],
           [[[2], [2, 4], [3], [], [4]]]],
)
_r = rnd(9006)


def _graph_with_cycles(r, n, m, back):
    """Mostly forward edges (so many nodes are safe) plus `back` random back edges that create cycles."""
    e, perm = _dag(r, n, m, local=60)
    g = [[] for _ in range(n)]
    for a, b in e:
        g[a].append(b)
    for _ in range(back):
        i, j = sorted(r.sample(range(n), 2))
        g[perm[j]].append(perm[i])
    return [sorted(set(x)) for x in g]


p["tests"].append([_graph_with_cycles(_r, 3000, 6000, 3)])
p["tests"].append([_graph_with_cycles(_r, 3000, 5000, 0)])
p["tests"].append([_graph_with_cycles(_r, 2500, 4000, 40)])
p["tests"].append([[[i + 1] for i in range(2999)] + [[1500]]])


def b_safe(graph):
    n = len(graph)
    reach = _closure(n, [(i, j) for i in range(n) for j in graph[i]])
    return [i for i in range(n) if not any(reach[i][j] and reach[j][j] for j in range(n)) and not reach[i][i]]


def g_safe(r):
    n = r.randint(1, 7)
    return [[sorted(r.sample(range(n), r.randint(0, min(n, 2)))) if r.random() < 0.8 else [] for _ in range(n)]]


def v_safe(tests):
    for t in tests:
        g = t["args"][0]
        n = len(g)
        assert 1 <= n <= 3000 and sum(len(x) for x in g) <= 8000
        assert all(len(set(x)) == len(x) and all(0 <= v < n for v in x) for x in g)
    assert any(len(t["expected"]) < len(t["args"][0]) for t in tests)


CHECKS["eventual-safe-nodes"] = (b_safe, g_safe, "exact")
VALIDATE["eventual-safe-nodes"] = v_safe

# ---------------------------------------------------------------- unique sequence reconstruction
p = add(
    id="unique-sequence-reconstruction", title="Unique Sequence Reconstruction", diff="Medium", topic=T,
    fn="uniqueSupersequence", params=[("nums", "int[]"), ("sequences", "int[][]")], ret="bool", cmp="exact",
    desc="<p>The array <code>nums</code> is a permutation of the integers <code>1</code> to <code>n</code>. You are also given a list of smaller sequences <code>sequences</code>; each one lists distinct values from <code>1..n</code>.</p><p>Consider all arrangements (permutations) of <code>1..n</code> in which <strong>every</strong> sequence appears as a subsequence, that is, its values occur in that relative order (not necessarily next to each other). Return <code>true</code> if <code>nums</code> is such an arrangement and it is the <strong>only</strong> one; otherwise return <code>false</code>. If no arrangement exists at all, the answer is <code>false</code>.</p><pre>nums = [1,2,3], sequences = [[1,2],[2,3]]  -> true\nnums = [1,2,3], sequences = [[1,2],[1,3]]  -> false   ([1,3,2] also works)\nnums = [1,2,3], sequences = [[1,2]]        -> false   (3 can go anywhere)\nnums = [1,2],   sequences = [[1,2],[2,1]]  -> false   (contradiction)\nnums = [3,1,2], sequences = [[3,1,2]]      -> true</pre>",
    constraints=["1 &le; n = nums.length &le; 2,000", "nums is a permutation of 1..n", "0 &le; sequences.length &le; 3,000; each sequence has between 1 and n values, distinct inside the sequence, in [1, n]", "The total length of all sequences is at most 8,000"],
    hints=["Every sequence only says 'x comes before y' for neighbouring values. Turn each neighbouring pair into a directed edge.",
           "An arrangement that respects all sequences is a topological order of that graph. So the question is whether the graph has exactly one topological order, and whether it is nums.",
           "Run Kahn's algorithm and look at the queue. If at any moment two or more nodes have indegree 0, they could be placed in either order, so the answer is <code>false</code>. Otherwise compare each removed node with the next value of <code>nums</code>, and finally check that all n nodes were removed (a cycle leaves some behind)."],
    editorial=["A sequence is a subsequence of an arrangement exactly when each neighbouring pair of the sequence appears in the right order (order is transitive), so only the pairs <code>(s[i], s[i+1])</code> matter. Build a directed graph on 1..n from those pairs; the valid arrangements are precisely the topological orders of this graph.",
               "A DAG has a unique topological order exactly when, at every step of Kahn's algorithm, there is only one node with indegree 0: if two were available, swapping them would give a second order, and if one is always available there is never a choice. So run Kahn's algorithm, return <code>false</code> as soon as the set of ready nodes has size other than 1, or when the node removed differs from <code>nums[i]</code>.",
               "At the end the number of removed nodes must be n. If a cycle exists (contradicting sequences) the ready set becomes empty before n nodes are removed, which also gives <code>false</code>. Values missing from every sequence start with indegree 0 and would be ready at the same time as another node (unless n = 1), correctly producing <code>false</code>. Repeated pairs must be counted once, so use a set per node or deduplicate. Time and space are O(n + total length)."],
    time="O(n + L)", space="O(n + L)",
    solution='''def uniqueSupersequence(nums, sequences):
    n = len(nums)
    adj = [set() for _ in range(n + 1)]
    indeg = [0] * (n + 1)
    for s in sequences:
        for a, b in zip(s, s[1:]):
            if b not in adj[a]:
                adj[a].add(b)
                indeg[b] += 1
    ready = [v for v in range(1, n + 1) if indeg[v] == 0]
    i = 0
    while ready:
        if len(ready) > 1:
            return False
        u = ready[0]
        if nums[i] != u:
            return False
        i += 1
        ready = []
        for v in adj[u]:
            indeg[v] -= 1
            if indeg[v] == 0:
                ready.append(v)
    return i == n
''',
    tests=[[[1, 2, 3], [[1, 2], [2, 3]]],
           [[1, 2, 3], [[1, 2], [1, 3]]],
           [[1, 2, 3], [[1, 2]]],
           [[1, 2], [[1, 2], [2, 1]]],
           [[3, 1, 2], [[3, 1, 2]]],
           [[1], []],
           [[1], [[1]]],
           [[1, 2], []],
           [[2, 1], [[2, 1]]],
           [[1, 2], [[2, 1]]],
           [[4, 1, 3, 2], [[4, 1], [1, 3], [3, 2], [4, 3]]],
           [[4, 1, 3, 2], [[4, 3, 2], [1, 3], [4, 1]]],
           [[1, 2, 3, 4, 5], [[1, 2, 3], [3, 4], [4, 5], [1, 5]]],
           [[1, 2, 3, 4, 5], [[1, 2, 3], [3, 5], [5, 4]]]],
)
_r = rnd(9007)
_nums = list(range(1, 2001)); _r.shuffle(_nums)
_seqs = [_nums[i:i + 2] for i in range(1999)]
_r.shuffle(_seqs)
p["tests"].append([_nums, _seqs])  # true
p["tests"].append([_nums, _seqs[:1000] + _seqs[1001:]])  # one adjacent pair missing -> false
_long = [_nums[:1000], _nums[1000:]]
p["tests"].append([_nums, _long + [_nums[999:1001]]])  # true via long sequences
_seqs2 = [s[:] for s in _seqs]
_seqs2[10] = _seqs2[10][::-1]
p["tests"].append([_nums, _seqs2])  # a reversed pair makes a cycle -> false


def b_uniqueseq(nums, sequences):
    n = len(nums)

    def is_subseq(s, perm):
        it = iter(perm)
        return all(x in it for x in s)

    good = [p_ for p_ in permutations(range(1, n + 1)) if all(is_subseq(s, p_) for s in sequences)]
    return len(good) == 1 and list(good[0]) == nums


def g_uniqueseq(r):
    n = r.randint(1, 6)
    nums = list(range(1, n + 1))
    r.shuffle(nums)
    seqs = []
    base = nums if r.random() < 0.8 else r.sample(nums, n)
    if r.random() < 0.6:
        seqs = [base[i:i + 2] for i in range(n - 1)]
        r.shuffle(seqs)
        if seqs and r.random() < 0.3:
            seqs.pop(r.randrange(len(seqs)))
    else:
        for _ in range(r.randint(0, 4)):
            k = r.randint(1, n)
            idx = sorted(r.sample(range(n), k))
            seqs.append([base[i] for i in idx])
    return [nums, seqs]


def v_uniqueseq(tests):
    seen = set()
    for t in tests:
        nums, seqs = t["args"]
        n = len(nums)
        assert 1 <= n <= 2000 and sorted(nums) == list(range(1, n + 1))
        assert len(seqs) <= 3000 and sum(len(s) for s in seqs) <= 8000
        for s in seqs:
            assert 1 <= len(s) <= n and len(set(s)) == len(s) and all(1 <= v <= n for v in s)
        seen.add(t["expected"])
    assert seen == {True, False}


CHECKS["unique-sequence-reconstruction"] = (b_uniqueseq, g_uniqueseq, "exact")
VALIDATE["unique-sequence-reconstruction"] = v_uniqueseq

# ---------------------------------------------------------------- prerequisite queries
p = add(
    id="course-prerequisite-queries", title="Is It a Prerequisite? (Queries)", diff="Medium", topic=T, tier="extra",
    fn="checkPrerequisites", params=[("n", "int"), ("prerequisites", "int[][]"), ("queries", "int[][]")], ret="int[]", cmp="exact",
    desc="<p>There are <code>n</code> courses numbered <code>0</code> to <code>n - 1</code>. Each entry <code>prerequisites[i] = [a, b]</code> means course <code>a</code> must be taken directly before course <code>b</code> (<code>a</code> is a <em>direct</em> prerequisite of <code>b</code>). The dependencies contain no cycle.</p><p>Prerequisites are transitive: if <code>a</code> is a prerequisite of <code>b</code> and <code>b</code> is a prerequisite of <code>c</code>, then <code>a</code> is also a prerequisite of <code>c</code>. A course is never a prerequisite of itself.</p><p>For each query <code>queries[j] = [u, v]</code>, decide whether course <code>u</code> is a (direct or indirect) prerequisite of course <code>v</code>. Return an array where entry <code>j</code> is <code>1</code> if the answer to query <code>j</code> is yes and <code>0</code> otherwise.</p><pre>n = 3, prerequisites = [[0,1],[1,2]], queries = [[0,2],[2,0],[1,1],[0,1]] -> [1,0,0,1]\nn = 4, prerequisites = [[0,2],[1,2]],  queries = [[0,1],[1,2]]             -> [0,1]</pre>",
    constraints=["1 &le; n &le; 1,000", "0 &le; prerequisites.length &le; 4,000", "1 &le; queries.length &le; 3,000", "0 &le; a, b, u, v &lt; n; a &ne; b; the prerequisite graph is acyclic; pairs may repeat; u may equal v in a query"],
    hints=["Answering one query is a reachability question: is there a path from u to v? Doing a fresh search for each of up to 3,000 queries is slow, so share work between queries.",
           "For every course, compute the full set of courses that are its prerequisites. The set of a course is the union of (direct prerequisite + that prerequisite's own set) over its direct prerequisites.",
           "Process courses in topological order and store each set as a bitmask held in a Python integer: <code>mask[v] |= mask[u] | (1 &lt;&lt; u)</code> for every edge u &rarr; v. Each query is then a single bit test <code>(mask[v] &gt;&gt; u) &amp; 1</code>."],
    editorial=["Because the graph is acyclic, the prerequisites of a course v are exactly its direct prerequisites u together with all prerequisites of those u. If we handle the courses in topological order, <code>pre[u]</code> is complete before we use it to build <code>pre[v]</code>.",
               "Representing <code>pre[v]</code> as a bitmask of n bits, the update for an edge u &rarr; v is <code>pre[v] |= pre[u] | (1 &lt;&lt; u)</code>, which costs O(n / 64) machine words (Python's big integers do this in C). With m edges the total is about O(m * n / 64), and each query is O(1) afterwards. Course u is a prerequisite of v when bit u of <code>pre[v]</code> is set; a course never sets its own bit because the graph has no cycles, so <code>u = v</code> correctly gives 0.",
               "Alternatives are Floyd-Warshall transitive closure, O(n<sup>3</sup>), which is too slow for n = 1,000 in plain Python, or one DFS per query, O(q * (n + m)). The bitset DP is the practical choice."],
    time="O(m * n / 64 + q)", space="O(n<sup>2</sup> / 64 + m)",
    solution='''def checkPrerequisites(n, prerequisites, queries):
    adj = [[] for _ in range(n)]
    indeg = [0] * n
    for a, b in prerequisites:
        adj[a].append(b)
        indeg[b] += 1
    pre = [0] * n
    stack = [i for i in range(n) if indeg[i] == 0]
    while stack:
        u = stack.pop()
        bits = pre[u] | (1 << u)
        for v in adj[u]:
            pre[v] |= bits
            indeg[v] -= 1
            if indeg[v] == 0:
                stack.append(v)
    return [(pre[v] >> u) & 1 for u, v in queries]
''',
    tests=[[3, [[0, 1], [1, 2]], [[0, 2], [2, 0], [1, 1], [0, 1]]],
           [4, [[0, 2], [1, 2]], [[0, 1], [1, 2]]],
           [1, [], [[0, 0]]],
           [2, [], [[0, 1], [1, 0]]],
           [2, [[1, 0]], [[1, 0], [0, 1]]],
           [5, [[0, 1], [1, 2], [2, 3], [3, 4]], [[0, 4], [4, 0], [1, 3], [3, 1], [2, 2]]],
           [5, [[0, 1], [0, 1], [2, 1]], [[0, 1], [2, 1], [0, 2], [1, 0]]],
           [6, [[0, 2], [1, 2], [2, 3], [2, 4], [4, 5]], [[0, 5], [1, 5], [3, 5], [0, 3], [1, 0], [4, 3]]],
           [6, [[5, 4], [4, 3], [3, 2], [5, 0]], [[5, 2], [5, 0], [0, 5], [4, 0], [3, 4]]]],
)
_r = rnd(9008)
for _n, _m, _kw in ((1000, 2000, {}), (800, 3000, {"local": 25, "extra_chain": 0.9})):
    _e, _ = _dag(_r, _n, _m, **_kw)
    _q = [[_r.randrange(_n), _r.randrange(_n)] for _ in range(2000)]
    p["tests"].append([_n, [list(x) for x in _e], _q])
_e, _perm = _dag(_r, 1000, 1500, local=40, extra_chain=1.0)
_q = []
for _ in range(1800):
    _i, _j = _r.sample(range(1000), 2)
    _q.append([_perm[_i], _perm[_j]])
p["tests"].append([1000, [list(x) for x in _e], _q])


def b_prereq(n, pre, queries):
    reach = _closure(n, pre)
    return [1 if reach[u][v] else 0 for u, v in queries]


def g_prereq(r):
    n = r.randint(1, 7)
    e, _ = _dag(r, n, r.randint(0, 2 * n))
    e = [list(x) for x in e]
    if e and r.random() < 0.3:
        e.append(list(r.choice(e)))
    return [n, e, [[r.randrange(n), r.randrange(n)] for _ in range(r.randint(1, 8))]]


def v_prereq(tests):
    for t in tests:
        n, pre, q = t["args"]
        assert 1 <= n <= 1000 and len(pre) <= 4000 and 1 <= len(q) <= 3000
        assert all(0 <= a < n and 0 <= b < n and a != b for a, b in pre)
        assert all(0 <= a < n and 0 <= b < n for a, b in q)
        assert _is_acyclic(n, pre)
        assert len(t["expected"]) == len(q)


CHECKS["course-prerequisite-queries"] = (b_prereq, g_prereq, "exact")
VALIDATE["course-prerequisite-queries"] = v_prereq

# ================================================================ HARD

# ---------------------------------------------------------------- largest color value
p = add(
    id="largest-color-value-in-digraph", title="Largest Color Value in a Directed Graph", diff="Hard", topic=T,
    fn="largestColorValue", params=[("colors", "int[]"), ("edges", "int[][]")], ret="int", cmp="exact",
    desc="<p>A directed graph has <code>n = colors.length</code> nodes labelled <code>0</code> to <code>n - 1</code>. Node <code>i</code> has the color <code>colors[i]</code>, an integer from <code>0</code> to <code>25</code>. Each entry <code>edges[i] = [a, b]</code> is a one-way edge from <code>a</code> to <code>b</code>.</p><p>A <em>path</em> is a sequence of nodes where each consecutive pair is joined by an edge (a single node is a path). The <em>color value</em> of a path is the number of times the most frequent color occurs among the nodes of the path (nodes are counted with multiplicity along the path, and since the graph is acyclic no node repeats).</p><p>Return the largest color value over all paths in the graph. If the graph contains a cycle, return <code>-1</code> instead.</p><pre>colors = [0,2,1,0,0], edges = [[0,1],[0,2],[2,3],[3,4]] -> 3   (path 0 -> 2 -> 3 -> 4 has colors 0,1,0,0)\ncolors = [0],         edges = [[0,0]]                    -> -1\ncolors = [5,5,5],     edges = []                         -> 1</pre>",
    constraints=["1 &le; n &le; 2,000", "0 &le; edges.length &le; 3,000", "0 &le; colors[i] &le; 25", "0 &le; a, b &lt; n; repeated edges and self-loops are allowed (a self-loop is a cycle)"],
    hints=["First deal with cycles: if the graph has one, the answer is -1. For an acyclic graph the paths form a nice order, so think about dynamic programming over that order.",
           "For each node v and each color c, let <code>dp[v][c]</code> be the largest number of nodes of color c on a path <em>ending</em> at v. There are only 26 colors, so this table is small.",
           "In topological order, push each node's row to its successors: <code>dp[v][c] = max(dp[v][c], dp[u][c])</code> for every edge u &rarr; v, and when a node is processed add one to <code>dp[u][colors[u]]</code> first. The answer is the largest entry that ever appears. If Kahn's algorithm removes fewer than n nodes, return -1."],
    editorial=["The count of a color along a path is additive, but the most frequent color is not, so we cannot keep a single number per node. Instead keep, for every node, the best count of <em>every</em> color on paths ending there. With 26 colors this is a 26-entry row per node.",
               "Process the nodes in topological order (Kahn's algorithm). When node u is taken, all its predecessors have already pushed their rows into <code>dp[u]</code>, so <code>dp[u][c]</code> is the best count of color c among paths that end just before u. Add 1 to <code>dp[u][colors[u]]</code> to include u itself, update the global answer with the maximum of the row, and for each outgoing edge u &rarr; v merge the row into v by taking the entry-wise maximum.",
               "The number of removed nodes tells us about cycles: if it is less than n, some nodes never reached indegree 0, so a cycle exists and the answer is -1 (this also covers self-loops). Total time is O(26 * (n + m)) and memory O(26 * n). Searching with DFS and memoisation also works but recurses deeply on long chains."],
    time="O(26 * (n + m))", space="O(26 * n + m)",
    solution='''def largestColorValue(colors, edges):
    n = len(colors)
    adj = [[] for _ in range(n)]
    indeg = [0] * n
    for a, b in edges:
        adj[a].append(b)
        indeg[b] += 1
    dp = [[0] * 26 for _ in range(n)]
    stack = [i for i in range(n) if indeg[i] == 0]
    taken = 0
    best = 0
    while stack:
        u = stack.pop()
        taken += 1
        row = dp[u]
        row[colors[u]] += 1
        m = max(row)
        if m > best:
            best = m
        for v in adj[u]:
            target = dp[v]
            for c in range(26):
                if row[c] > target[c]:
                    target[c] = row[c]
            indeg[v] -= 1
            if indeg[v] == 0:
                stack.append(v)
    return best if taken == n else -1
''',
    tests=[[[0, 2, 1, 0, 0], [[0, 1], [0, 2], [2, 3], [3, 4]]],
           [[0], [[0, 0]]],
           [[5, 5, 5], []],
           [[7], []],
           [[0, 1], [[0, 1], [1, 0]]],
           [[0, 0, 0, 0], [[0, 1], [1, 2], [2, 3]]],
           [[0, 1, 0, 1, 0, 1], [[0, 1], [1, 2], [2, 3], [3, 4], [4, 5]]],
           [[3, 3, 4, 4, 4], [[0, 2], [1, 2], [2, 3], [2, 4]]],
           [[25, 0, 25, 0, 25], [[4, 3], [3, 2], [2, 1], [1, 0], [4, 2], [4, 2]]],
           [[1, 1, 2, 2, 2, 1], [[0, 1], [1, 2], [2, 3], [3, 4], [4, 2], [4, 5]]],
           [[0, 1, 2, 0, 1, 2, 0], [[0, 3], [1, 3], [2, 3], [3, 6], [4, 6], [5, 6]]]],
)
_r = rnd(9009)


def _colored(r, n, m, ncol, **kw):
    e, _ = _dag(r, n, m, **kw)
    return [r.randrange(ncol) for _ in range(n)], [list(x) for x in e]


_c, _e = _colored(_r, 2000, 3000, 3, local=30, extra_chain=0.9)
p["tests"].append([_c, _e])
_c, _e = _colored(_r, 1500, 3000, 26)
p["tests"].append([_c, _e])
_c, _e = _colored(_r, 1500, 2500, 2, local=10, extra_chain=1.0)
_e.append([_e[5][1], _e[5][0]])  # a cycle hidden in a big graph
p["tests"].append([_c, _e])
p["tests"].append([[_r.choice([0, 0, 0, 1]) for _ in range(1500)], [[i, i + 1] for i in range(1499)]])


def b_color(colors, edges):
    n = len(colors)
    reach = _closure(n, edges)
    if any(reach[i][i] for i in range(n)):
        return -1
    adj = [[] for _ in range(n)]
    for a, b in edges:
        adj[a].append(b)
    best = 0

    def go(u, cnt):
        nonlocal best
        cnt[colors[u]] += 1
        best = max(best, max(cnt))
        for v in adj[u]:
            go(v, cnt)
        cnt[colors[u]] -= 1

    for s in range(n):
        go(s, [0] * 26)
    return best


def g_color(r):
    n = r.randint(1, 7)
    if r.random() < 0.75:
        e = [list(x) for x in _dag(r, n, r.randint(0, 2 * n))[0]]
        if e and r.random() < 0.3:
            e.append(list(r.choice(e)))
    else:
        e = _rand_pairs(r, n, r.randint(0, 2 * n))
    return [[r.choice([0, 1, 2, 25]) for _ in range(n)], e]


def v_color(tests):
    seen = set()
    for t in tests:
        colors, edges = t["args"]
        n = len(colors)
        assert 1 <= n <= 2000 and len(edges) <= 3000
        assert all(0 <= c <= 25 for c in colors)
        assert all(0 <= a < n and 0 <= b < n for a, b in edges)
        assert (t["expected"] == -1) == (not _is_acyclic(n, edges))
        seen.add(t["expected"] == -1)
    assert seen == {True, False}


CHECKS["largest-color-value-in-digraph"] = (b_color, g_color, "exact")
VALIDATE["largest-color-value-in-digraph"] = v_color

# ---------------------------------------------------------------- count topological orders
p = add(
    id="count-topological-orders", title="Count the Topological Orders", diff="Hard", topic=T, tier="extra",
    fn="countTopologicalOrders", params=[("n", "int"), ("edges", "int[][]")], ret="int", cmp="exact",
    desc="<p>A directed graph has <code>n</code> nodes labelled <code>0</code> to <code>n - 1</code>. Each entry <code>edges[i] = [a, b]</code> is an edge from <code>a</code> to <code>b</code>. A <em>topological order</em> is an arrangement of all <code>n</code> nodes in a line such that, for every edge <code>[a, b]</code>, node <code>a</code> comes before node <code>b</code>.</p><p>Count how many different topological orders the graph has, and return the count modulo <code>1,000,000,007</code>. If the graph has a cycle (or a self-loop) there is no topological order and the answer is <code>0</code>.</p><pre>n = 3, edges = []                    -> 6\nn = 3, edges = [[0,1],[0,2]]         -> 2\nn = 4, edges = [[0,1],[1,2],[2,3]]   -> 1\nn = 2, edges = [[0,1],[1,0]]         -> 0</pre>",
    constraints=["1 &le; n &le; 15", "0 &le; edges.length &le; 60", "0 &le; a, b &lt; n; repeated edges, cycles and self-loops are allowed"],
    hints=["Listing all permutations is hopeless for n = 15, since 15! is more than a trillion. Many different permutations share the same <em>set</em> of nodes placed so far.",
           "Let <code>dp[mask]</code> be the number of ways to arrange the nodes in <code>mask</code> as the first positions of a valid order. Which nodes can be placed next, given the set mask?",
           "A node v outside the mask may be placed next if all of its predecessors are already in the mask: with <code>pred[v]</code> as a bitmask this is <code>pred[v] &amp; ~mask == 0</code>. Then <code>dp[mask | (1 &lt;&lt; v)] += dp[mask]</code>. The answer is <code>dp[(1 &lt;&lt; n) - 1]</code>."],
    editorial=["The only thing that matters about the nodes already placed is <em>which</em> they are, not in what order, because the next node must simply have all its predecessors among them. That gives a DP over subsets: <code>dp[mask]</code> is the number of valid orders of the nodes in <code>mask</code> that can start a complete order.",
               "Store for each node a bitmask <code>pred[v]</code> of its in-neighbours (repeated edges just set the same bit). Start with <code>dp[0] = 1</code>. For each mask in increasing numeric order (a mask is always smaller than the masks that add a bit to it), try each node v not in mask whose predecessors are all inside mask, and add <code>dp[mask]</code> to <code>dp[mask | 1 &lt;&lt; v]</code>, modulo 1,000,000,007.",
               "The answer is <code>dp</code> of the full set. A self-loop makes a node its own predecessor, so it can never be placed and the full mask stays at 0; a longer cycle likewise blocks the DP, which gives the required 0 without a separate cycle check. The running time is O(2<sup>n</sup> * n) and memory O(2<sup>n</sup>). The count itself can reach 15!, so the modulo is needed."],
    time="O(2^n * n)", space="O(2^n)",
    solution='''def countTopologicalOrders(n, edges):
    MOD = 1000000007
    pred = [0] * n
    for a, b in edges:
        pred[b] |= 1 << a
    full = (1 << n) - 1
    dp = [0] * (1 << n)
    dp[0] = 1
    for mask in range(1 << n):
        d = dp[mask]
        if not d:
            continue
        rest = full & ~mask
        while rest:
            low = rest & -rest
            v = low.bit_length() - 1
            if pred[v] & ~mask == 0:
                dp[mask | low] = (dp[mask | low] + d) % MOD
            rest ^= low
    return dp[full]
''',
    tests=[[3, []],
           [3, [[0, 1], [0, 2]]],
           [4, [[0, 1], [1, 2], [2, 3]]],
           [2, [[0, 1], [1, 0]]],
           [1, []],
           [1, [[0, 0]]],
           [4, [[0, 1], [0, 1], [2, 3]]],
           [5, [[0, 4], [1, 4], [2, 4], [3, 4]]],
           [6, [[0, 1], [1, 2], [3, 4], [4, 5]]],
           [8, [[0, 2], [1, 2], [2, 3], [2, 4], [3, 5], [4, 5], [5, 6], [5, 7]]],
           [10, [[i, i + 1] for i in range(0, 9, 2)]],
           [12, [[0, 1], [1, 2], [2, 0], [5, 6]]],
           [15, []],
           [15, [[i, i + 1] for i in range(14)]],
           [15, [[0, i] for i in range(1, 15)]],
           [15, [[i, i + 2] for i in range(13)]]],
)
_r = rnd(9010)
_e, _ = _dag(_r, 15, 22)
p["tests"].append([15, [list(x) for x in _e]])
_e, _ = _dag(_r, 15, 12)
p["tests"].append([15, [list(x) for x in _e]])


def b_counttopo(n, edges):
    if n <= 7:
        c = 0
        for perm in permutations(range(n)):
            pos = {v: i for i, v in enumerate(perm)}
            if all(pos[a] < pos[b] for a, b in edges):
                c += 1
        return c % MOD
    # larger n: choose the LAST node of the order (a node with no successor left), recursively
    succ = [0] * n
    for a, b in edges:
        succ[a] |= 1 << b
    memo = {}

    def f(mask):  # number of orders of the nodes in mask
        if mask == 0:
            return 1
        if mask in memo:
            return memo[mask]
        total = 0
        for v in range(n):
            if (mask >> v) & 1 and succ[v] & mask == 0:
                total += f(mask ^ (1 << v))
        memo[mask] = total % MOD
        return memo[mask]

    return f((1 << n) - 1)


def g_counttopo(r):
    n = r.randint(1, 7)
    if r.random() < 0.7:
        return [n, [list(x) for x in _dag(r, n, r.randint(0, 2 * n))[0]]]
    return [n, _rand_pairs(r, n, r.randint(0, n + 2))]


def v_counttopo(tests):
    zero = 0
    for t in tests:
        n, edges = t["args"]
        assert 1 <= n <= 15 and len(edges) <= 60
        assert all(0 <= a < n and 0 <= b < n for a, b in edges)
        assert (t["expected"] == 0) == (not _is_acyclic(n, edges))
        zero += t["expected"] == 0
    assert 0 < zero < len(tests)


CHECKS["count-topological-orders"] = (b_counttopo, g_counttopo, "exact")
VALIDATE["count-topological-orders"] = v_counttopo

# ---------------------------------------------------------------- parallel courses with a per-semester limit
p = add(
    id="parallel-courses-with-semester-limit", title="Parallel Courses With a Limit", diff="Hard", topic=T, tier="extra",
    fn="minSemestersWithLimit", params=[("n", "int"), ("relations", "int[][]"), ("k", "int")], ret="int", cmp="exact",
    desc="<p>A university has <code>n</code> courses numbered <code>0</code> to <code>n - 1</code>. Each entry <code>relations[i] = [prev, next]</code> means course <code>prev</code> must be finished in an earlier semester than course <code>next</code>. The dependencies contain no cycle.</p><p>In every semester you may take <strong>at most <code>k</code></strong> courses, and only courses whose prerequisites were all completed in earlier semesters. Return the minimum number of semesters needed to finish all courses.</p><pre>n = 4, relations = [[1,0],[2,0],[3,0]], k = 2 -> 3\nn = 5, relations = [[1,0],[2,0]],       k = 2 -> 3\nn = 6, relations = [[0,1],[1,2]],       k = 3 -> 3\nn = 4, relations = [],                  k = 3 -> 2</pre><p>In the first example, courses 1, 2 and 3 are all prerequisites of course 0: two of them go in semester 1, the last one in semester 2, and course 0 in semester 3.</p>",
    constraints=["1 &le; n &le; 12", "0 &le; relations.length &le; 40", "0 &le; prev, next &lt; n and prev &ne; next; the graph is acyclic; pairs may repeat", "1 &le; k &le; n"],
    hints=["Without the limit k the answer is the length of the longest prerequisite chain. With the limit, a greedy 'take the first k available courses' can go wrong, because some courses unlock much more than others.",
           "The state of the plan after each semester is just the <em>set</em> of finished courses. With n &le; 12 there are only 4,096 such sets, so use dynamic programming over subsets.",
           "<code>dp[mask]</code> = fewest semesters to finish exactly the courses in mask. From mask compute <code>avail</code>, the courses outside mask whose prerequisites all lie in mask. If <code>avail</code> has at most k courses take them all; otherwise try every submask of avail with exactly k courses. Transition to <code>mask | chosen</code> with cost +1."],
    editorial=["After each semester, all that matters is which courses are finished. So define <code>dp[mask]</code> as the minimum number of semesters needed to have finished exactly the courses of mask (infinite if impossible). Store <code>pre[v]</code>, the bitmask of the direct prerequisites of v. Course v can be taken from state mask when it is not in mask and <code>pre[v] &amp; ~mask == 0</code>; let <code>avail</code> be the set of such courses.",
               "From mask we choose a subset of avail of size at most k to take this semester. Finishing more courses never hurts (a larger finished set allows everything a smaller set allows), so it is enough to consider taking all of avail when it has at most k courses and exactly k courses otherwise. Iterate masks in increasing order, enumerate submasks of avail with <code>sub = (sub - 1) &amp; avail</code> and use a precomputed popcount table to keep those of size k.",
               "The answer is <code>dp[(1 &lt;&lt; n) - 1]</code>. Enumerating every submask of the available set over all masks costs at most 3<sup>n</sup> steps (each course is in the mask, in the available set or in neither), which is about 531,000 for n = 12. Greedy strategies such as 'take the courses with the longest remaining chain first' are tempting but fail on some inputs, which is why the exhaustive DP is used here."],
    time="O(3^n)", space="O(2^n)",
    solution='''def minSemestersWithLimit(n, relations, k):
    pre = [0] * n
    for a, b in relations:
        pre[b] |= 1 << a
    full = (1 << n) - 1
    pc = [0] * (1 << n)
    for i in range(1, 1 << n):
        pc[i] = pc[i >> 1] + (i & 1)
    INF = 10 ** 9
    dp = [INF] * (1 << n)
    dp[0] = 0
    for mask in range(1 << n):
        d = dp[mask]
        if d == INF:
            continue
        avail = 0
        for v in range(n):
            if not (mask >> v) & 1 and pre[v] & ~mask == 0:
                avail |= 1 << v
        if pc[avail] <= k:
            nm = mask | avail
            if d + 1 < dp[nm]:
                dp[nm] = d + 1
        else:
            sub = avail
            while sub:
                if pc[sub] == k:
                    nm = mask | sub
                    if d + 1 < dp[nm]:
                        dp[nm] = d + 1
                sub = (sub - 1) & avail
    return dp[full]
''',
    tests=[[4, [[1, 0], [2, 0], [3, 0]], 2],
           [5, [[1, 0], [2, 0]], 2],
           [6, [[0, 1], [1, 2]], 3],
           [4, [], 3],
           [1, [], 1],
           [5, [], 1],
           [5, [[0, 1], [1, 2], [2, 3], [3, 4]], 5],
           [6, [[0, 1], [0, 2], [0, 3], [4, 5]], 2],
           [7, [[0, 3], [1, 3], [2, 3], [3, 4], [3, 5], [3, 6]], 2],
           [8, [[0, 4], [1, 4], [2, 5], [3, 5], [4, 6], [5, 7]], 3],
           [9, [[0, 1], [0, 2], [0, 3], [1, 4], [2, 4], [3, 4], [4, 5], [4, 6], [4, 7], [4, 8]], 3],
           [12, [], 5],
           [12, [[i, i + 1] for i in range(11)], 3],
           [12, [[i, 11] for i in range(11)], 4]],
)
_r = rnd(9011)
for _m, _k in ((14, 3), (20, 4), (8, 2), (30, 5)):
    _e, _ = _dag(_r, 12, _m)
    p["tests"].append([12, [list(x) for x in _e], _k])
_e, _ = _dag(_r, 12, 18)
p["tests"].append([12, [list(x) for x in _e], 1])
p["tests"].append([12, [[0, 1], [0, 2], [0, 3], [1, 4], [2, 5], [3, 6], [3, 7], [4, 8], [5, 8], [6, 9], [7, 9], [8, 10], [9, 11]], 2])


def b_limited(n, rel, k):
    pre = [0] * n
    for a, b in rel:
        pre[b] |= 1 << a
    memo = {}

    def f(done):  # fewest further semesters
        if done == (1 << n) - 1:
            return 0
        if done in memo:
            return memo[done]
        avail = [v for v in range(n) if not (done >> v) & 1 and pre[v] & ~done == 0]
        best = 10 ** 9
        for size in range(1, min(k, len(avail)) + 1):
            for comb in combinations(avail, size):
                nd = done
                for v in comb:
                    nd |= 1 << v
                best = min(best, 1 + f(nd))
        memo[done] = best
        return best

    return f(0)


def g_limited(r):
    n = r.randint(1, 7)
    e, _ = _dag(r, n, r.randint(0, 2 * n))
    e = [list(x) for x in e]
    if e and r.random() < 0.3:
        e.append(list(r.choice(e)))
    return [n, e, r.randint(1, n)]


def v_limited(tests):
    for t in tests:
        n, rel, k = t["args"]
        assert 1 <= n <= 12 and len(rel) <= 40 and 1 <= k <= n
        assert all(0 <= a < n and 0 <= b < n and a != b for a, b in rel)
        assert _is_acyclic(n, rel)
        assert t["expected"] >= -(-n // k)


CHECKS["parallel-courses-with-semester-limit"] = (b_limited, g_limited, "exact")
VALIDATE["parallel-courses-with-semester-limit"] = v_limited
