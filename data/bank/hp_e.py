"""Problems: heap on graphs and structures (Dijkstra-lite, heap-ordered arrays, ugly numbers, grids with a priority queue)."""
import heapq
from itertools import combinations  # noqa: F401

from lib import add, rnd, CHECKS, VALIDATE, gen_arr  # noqa: F401

INT_MIN, INT_MAX = -(2 ** 31), 2 ** 31 - 1
MOD = 10 ** 9 + 7


# ------------------------------------------------------------------ shared helpers (tests only)
def _pairs(r, n, m):
    """m distinct unordered pairs of different nodes, random orientation and order."""
    m = min(m, n * (n - 1) // 2)
    s = set()
    while len(s) < m:
        u, v = r.sample(range(n), 2)
        s.add((min(u, v), max(u, v)))
    out = [list(x) if r.random() < 0.5 else [x[1], x[0]] for x in sorted(s)]
    r.shuffle(out)
    return out


def _tree_pairs(r, n):
    """Random spanning tree on 0..n-1 (as pairs)."""
    perm = list(range(n))
    r.shuffle(perm)
    return [[perm[r.randrange(v)], perm[v]] for v in range(1, n)]


def _connected_pairs(r, n, m):
    s = {(min(a, b), max(a, b)) for a, b in _tree_pairs(r, n)}
    m = min(max(m, n - 1), n * (n - 1) // 2)
    while len(s) < m:
        u, v = r.sample(range(n), 2)
        s.add((min(u, v), max(u, v)))
    out = [list(x) if r.random() < 0.5 else [x[1], x[0]] for x in sorted(s)]
    r.shuffle(out)
    return out


def _heap_from(r, n, lo, hi):
    a = [r.randint(lo, hi) for _ in range(n)]
    heapq.heapify(a)
    return a


def _is_heap(a):
    return all(a[(i - 1) // 2] <= a[i] for i in range(1, len(a)))


def _simple_pairs_ok(edges, n):
    seen = set()
    for e in edges:
        u, v = e[0], e[1]
        assert 0 <= u < n and 0 <= v < n and u != v
        k = (min(u, v), max(u, v))
        assert k not in seen, "duplicate pair"
        seen.add(k)


# ================================================================ EASY

# ---------------------------------------------------------------- ugly number check
p = add(
    id="ugly-number-check", title="Ugly Number Check", diff="Easy", topic="Heap", tier="extra",
    fn="isUgly", params=[("n", "int")], ret="bool", cmp="exact",
    desc="<p>A positive integer is called <em>ugly</em> when its only prime factors are <code>2</code>, <code>3</code> and <code>5</code>. The number <code>1</code> has no prime factors at all, so it counts as ugly. Zero and negative numbers are never ugly.</p><p>Return <code>true</code> if <code>n</code> is ugly and <code>false</code> otherwise.</p><pre>n = 6   -> true   (2 * 3)\nn = 14  -> false  (2 * 7, and 7 is not allowed)\nn = 1   -> true</pre><p>This is the building block for the next question about listing ugly numbers in order.</p>",
    constraints=["-2<sup>31</sup> &le; n &le; 2<sup>31</sup> - 1"],
    hints=["Handle non-positive numbers first. What should happen for 0 and for negative values?",
           "If n is ugly, you can keep dividing it by 2 while it is divisible, then by 3, then by 5.",
           "After removing every factor 2, 3 and 5, the number is ugly exactly when what is left equals 1."],
    editorial=["Return false for <code>n &le; 0</code>. Otherwise strip all factors of 2, then of 3, then of 5 by repeated division. Whatever remains is the part of n made of other primes: it is 1 when n is ugly and larger than 1 otherwise.",
               "Each division at least halves n, so there are at most about 31 divisions in total. The time is O(log n) and the space is O(1). Do not try to factorize n completely with trial division up to its square root; that is far slower than needed."],
    time="O(log n)", space="O(1)",
    solution='''def isUgly(n):
    if n <= 0:
        return False
    for f in (2, 3, 5):
        while n % f == 0:
            n //= f
    return n == 1
''',
    tests=[[6], [14], [1], [0], [-6], [7], [30], [49], [INT_MIN], [2 ** 30], [3 ** 19], [5 ** 13], [INT_MAX], [2 * 3 * 5 * 7 * 11 * 13]],
)


def b_ugly(n):
    if n <= 0:
        return False
    x = n
    f = 2
    primes = set()
    while f * f <= x:
        while x % f == 0:
            primes.add(f)
            x //= f
        f += 1
    if x > 1:
        primes.add(x)
    return primes <= {2, 3, 5}


def g_ugly(r):
    t = r.random()
    if t < 0.4:
        return [r.randint(-10, 300)]
    return [(2 ** r.randint(0, 5)) * (3 ** r.randint(0, 3)) * (5 ** r.randint(0, 2)) * r.choice([1, 1, 1, 7, 11])]


def v_ugly(tests):
    for t in tests:
        assert INT_MIN <= t["args"][0] <= INT_MAX
    assert any(t["expected"] for t in tests) and any(not t["expected"] for t in tests)


CHECKS["ugly-number-check"] = (b_ugly, g_ugly, "exact")
VALIDATE["ugly-number-check"] = v_ugly

# ---------------------------------------------------------------- min-heap array validity
p = add(
    id="min-heap-array-validity", title="Is This Array a Min-Heap?", diff="Easy", topic="Heap", tier="extra",
    fn="isMinHeap", params=[("arr", "int[]")], ret="bool", cmp="exact",
    desc="<p>A binary min-heap is often stored in an array: the element at index <code>i</code> has its children at indices <code>2i + 1</code> and <code>2i + 2</code> (when they exist), and every element must be <em>less than or equal to</em> each of its children.</p><p>Given an array <code>arr</code>, return <code>true</code> if it is a valid min-heap in this layout and <code>false</code> otherwise.</p><pre>[1, 3, 2, 6, 4, 5]     -> true\n[1, 3, 2, 2, 4]        -> false   (index 3 is a child of index 1: 2 &lt; 3)</pre>",
    constraints=["1 &le; arr.length &le; 8,000", "-2<sup>31</sup> &le; arr[i] &le; 2<sup>31</sup> - 1", "Equal values are allowed"],
    hints=["Every element except the first has exactly one parent. Where is the parent of index i?",
           "The parent of index i (i &ge; 1) is at index <code>(i - 1) // 2</code>.",
           "It is enough to compare every element with its parent: <code>arr[(i-1)//2] &le; arr[i]</code> for all i &ge; 1. Comparing with farther ancestors is implied by transitivity."],
    editorial=["The heap property only talks about parent and child pairs. Because the relation &le; is transitive, checking each parent against its direct children also guarantees that each element is at least as large as all of its ancestors.",
               "Loop over i from 1 to n - 1 and compare <code>arr[i]</code> with <code>arr[(i - 1) // 2]</code>; return false at the first violation. This is O(n) time and O(1) space. No heap operations are needed: this is a check on the array, not a construction."],
    time="O(n)", space="O(1)",
    solution='''def isMinHeap(arr):
    for i in range(1, len(arr)):
        if arr[(i - 1) // 2] > arr[i]:
            return False
    return True
''',
    tests=[[[1, 3, 2, 6, 4, 5]], [[1, 3, 2, 2, 4]], [[7]], [[2, 2, 2, 2]], [[5, 4]], [[1, 2]], [[3, 1, 2]],
           [[1, 5, 2, 6, 7, 3, 4]], [[1, 2, 3, 4, 5, 6, 7, 0]], [[INT_MIN, INT_MAX, INT_MIN, INT_MAX]], [[-1, -2, -3]]],
)
_r = rnd(9501)
_a = sorted(_r.randint(-10 ** 6, 10 ** 6) for _ in range(5000))
p["tests"].append([_a])  # sorted ascending is a valid heap
_a = _heap_from(_r, 5000, -10 ** 6, 10 ** 6)
p["tests"].append([_a])
_a = _heap_from(_r, 5000, -10 ** 6, 10 ** 6)
_a[4999], _a[2499] = _a[2499], _a[4999]
if _is_heap(_a):
    _a[4999] = _a[0] - 1
p["tests"].append([_a])  # one violation near the end (leaf smaller than its parent)
_a = [10 ** 6 - i for i in range(3000)]
p["tests"].append([_a])  # strictly decreasing: a max-heap, not a min-heap


def b_minheap(arr):
    n = len(arr)
    for j in range(1, n):
        i = j
        while i > 0:
            i = (i - 1) // 2
            if arr[i] > arr[j]:
                return False
    return True


def g_minheap(r):
    n = r.randint(1, 10)
    a = _heap_from(r, n, -4, 4)
    t = r.random()
    if t < 0.5 and n >= 2:
        i, j = r.sample(range(n), 2)
        a[i], a[j] = a[j], a[i]
    elif t < 0.7:
        a = [r.randint(-3, 3) for _ in range(n)]
    return [a]


def v_minheap(tests):
    for t in tests:
        a = t["args"][0]
        assert 1 <= len(a) <= 8000
        assert t["expected"] == _is_heap(a)
    assert any(t["expected"] for t in tests) and any(not t["expected"] for t in tests)


CHECKS["min-heap-array-validity"] = (b_minheap, g_minheap, "exact")
VALIDATE["min-heap-array-validity"] = v_minheap

# ================================================================ MEDIUM

# ---------------------------------------------------------------- nth ugly number
p = add(
    id="nth-ugly-number", title="Nth Ugly Number", diff="Medium", topic="Heap",
    fn="nthUglyNumber", params=[("n", "int")], ret="int", cmp="exact",
    desc="<p>An <em>ugly</em> number is a positive integer whose only prime factors are <code>2</code>, <code>3</code> and <code>5</code> (<code>1</code> counts as ugly). Listed in increasing order they start</p><pre>1, 2, 3, 4, 5, 6, 8, 9, 10, 12, 15, 16, 18, 20, 24, ...</pre><p>Return the <code>n</code>-th ugly number (1-indexed).</p><pre>n = 10  -> 12\nn = 1   -> 1</pre>",
    constraints=["1 &le; n &le; 1,690 (the answer then fits in a 32-bit signed integer)"],
    hints=["Testing every integer for ugliness is too slow when answers get large. Build the sequence directly instead.",
           "Every ugly number except 1 is a smaller ugly number multiplied by 2, 3 or 5. So the candidates for the next ugly number are the already-found numbers times 2, times 3 and times 5.",
           "Keep a min-heap (with a set to avoid duplicates), or better, three pointers into the sequence built so far: the next value is the smallest of <code>ugly[a]*2</code>, <code>ugly[b]*3</code>, <code>ugly[c]*5</code>, and every pointer that produced it moves forward."],
    editorial=["Heap approach: start with 1. Repeatedly pop the smallest value x, and push <code>2x</code>, <code>3x</code>, <code>5x</code> unless already seen. The n-th pop is the answer. Each pop adds at most three pushes, so the time is O(n log n).",
               "Pointer approach (a merge of three sorted streams): the sequence is the sorted union of {2u}, {3u} and {5u} over all ugly u. Keep three indices a, b, c into the sequence; the next term is <code>min(seq[a]*2, seq[b]*3, seq[c]*5)</code>. Advance <em>every</em> index whose product equals that minimum, which also removes duplicates such as 6 = 2*3 = 3*2. This is O(n) time and O(n) space and is the same idea as merging k sorted lists with a heap, just with fixed k = 3."],
    time="O(n)", space="O(n)",
    solution='''def nthUglyNumber(n):
    ugly = [1]
    a = b = c = 0
    while len(ugly) < n:
        x2, x3, x5 = ugly[a] * 2, ugly[b] * 3, ugly[c] * 5
        nxt = min(x2, x3, x5)
        ugly.append(nxt)
        if nxt == x2:
            a += 1
        if nxt == x3:
            b += 1
        if nxt == x5:
            c += 1
    return ugly[n - 1]
''',
    tests=[[1], [2], [10], [11], [15], [7], [100], [500], [1000], [1500], [1600], [1689], [1690]],
)


def b_nugly(n):
    def ok(x):
        for f in (2, 3, 5):
            while x % f == 0:
                x //= f
        return x == 1

    x = 0
    cnt = 0
    while cnt < n:
        x += 1
        if ok(x):
            cnt += 1
    return x


def v_nugly(tests):
    for t in tests:
        assert 1 <= t["args"][0] <= 1690
        assert t["expected"] <= INT_MAX


CHECKS["nth-ugly-number"] = (b_nugly, lambda r: [r.randint(1, 80)], "exact")
VALIDATE["nth-ugly-number"] = v_nugly

# ---------------------------------------------------------------- shortest distances from a source
p = add(
    id="shortest-distances-from-source", title="Shortest Distances from a Source", diff="Medium", topic="Heap",
    fn="shortestDistances", params=[("n", "int"), ("roads", "int[][]"), ("src", "int")], ret="int[]", cmp="exact",
    desc="<p>A town has <code>n</code> junctions numbered <code>0</code> to <code>n - 1</code> and a set of <em>one-way</em> roads. Each entry <code>roads[i] = [a, b, w]</code> is a road from junction <code>a</code> to junction <code>b</code> that takes <code>w</code> minutes to drive.</p><p>Return an array <code>dist</code> of length <code>n</code> where <code>dist[v]</code> is the least number of minutes needed to drive from <code>src</code> to <code>v</code>, or <code>-1</code> if <code>v</code> cannot be reached. Note that <code>dist[src] = 0</code>. Several roads may join the same pair of junctions and a road may even lead back to its own start.</p><pre>n = 4, src = 0\nroads = [[0,1,4], [0,2,1], [2,1,2], [1,3,5]]\n-> [0, 3, 1, 8]</pre><p>Junction 1 is reached faster through junction 2 (1 + 2 = 3) than directly (4).</p>",
    constraints=["1 &le; n &le; 2,000", "0 &le; roads.length &le; 5,000", "0 &le; a, b &lt; n", "1 &le; w &le; 1,000", "0 &le; src &lt; n"],
    hints=["Breadth-first search finds fewest roads, not least minutes. You need to expand junctions in order of their travel time.",
           "Keep the best known time to each junction. Always expand the unfinished junction with the smallest known time; use a min-heap of (time, junction) to find it.",
           "When you pop (t, u) and t is larger than the recorded best time of u, skip it (stale entry). Otherwise relax every road u -> v with w: if t + w improves dist[v], record it and push (t + w, v)."],
    editorial=["This is Dijkstra's algorithm. Because all times are positive, the first time a junction is popped from the min-heap its time is final: any other route would have to pass through a junction that is still waiting in the heap with an equal or larger time, and adding a positive road time cannot make it smaller.",
               "Initialise all distances to infinity except <code>dist[src] = 0</code>, push (0, src), and process as described in the hints. Stale heap entries are skipped by comparing the popped time with the stored best. Each road causes at most one push, so the heap holds at most E entries and the total time is O((V + E) log E). Junctions that are never reached keep infinity, which becomes -1 in the output.",
               "Parallel roads and self-loops need no special handling: a self-loop never improves a distance (w &gt; 0), and with parallel roads the cheaper one wins at relaxation time."],
    time="O((V + E) log E)", space="O(V + E)",
    solution='''import heapq


def shortestDistances(n, roads, src):
    adj = [[] for _ in range(n)]
    for a, b, w in roads:
        adj[a].append((b, w))
    INF = float('inf')
    dist = [INF] * n
    dist[src] = 0
    heap = [(0, src)]
    while heap:
        d, u = heapq.heappop(heap)
        if d > dist[u]:
            continue
        for v, w in adj[u]:
            nd = d + w
            if nd < dist[v]:
                dist[v] = nd
                heapq.heappush(heap, (nd, v))
    return [d if d < INF else -1 for d in dist]
''',
    tests=[[4, [[0, 1, 4], [0, 2, 1], [2, 1, 2], [1, 3, 5]], 0], [1, [], 0], [3, [], 1], [2, [[0, 1, 7], [0, 1, 3], [1, 1, 1]], 0],
           [3, [[0, 1, 5], [1, 0, 5]], 2], [4, [[3, 2, 1], [2, 1, 1], [1, 0, 1]], 3], [4, [[3, 2, 1], [2, 1, 1], [1, 0, 1]], 0],
           [5, [[0, 1, 2], [0, 2, 2], [1, 3, 2], [2, 3, 2], [3, 4, 1], [0, 4, 6]], 0],
           [5, [[0, 1, 600], [1, 2, 600], [0, 2, 1000], [2, 3, 1], [3, 4, 1], [4, 0, 1]], 0],
           [6, [[0, 1, 1], [1, 2, 1], [2, 0, 1], [3, 4, 1], [4, 5, 1]], 0]],
)
_r = rnd(9502)
_n = 1000
_e = [[_r.randrange(_n), _r.randrange(_n), _r.randint(1, 1000)] for _ in range(3000)]
p["tests"].append([_n, _e, _r.randrange(_n)])
_n = 2000
_e = [[i, i + 1, _r.randint(1, 1000)] for i in range(_n - 1)]
_e += [[_r.randrange(_n), _r.randrange(_n), _r.randint(1, 1000)] for _ in range(1000)]
_r.shuffle(_e)
p["tests"].append([_n, _e, 0])
_n = 1000
_e = [[_r.randrange(_n // 2), _r.randrange(_n // 2), _r.randint(1, 50)] for _ in range(2500)]
p["tests"].append([_n, _e, 0])  # half of the junctions are unreachable


def b_shortest(n, roads, src):
    INF = float('inf')
    dist = [INF] * n
    dist[src] = 0
    for _ in range(n):
        ch = False
        for a, b, w in roads:
            if dist[a] + w < dist[b]:
                dist[b] = dist[a] + w
                ch = True
        if not ch:
            break
    return [d if d < INF else -1 for d in dist]


def g_shortest(r):
    n = r.randint(1, 7)
    m = r.randint(0, 12)
    return [n, [[r.randrange(n), r.randrange(n), r.randint(1, 9)] for _ in range(m)], r.randrange(n)]


def v_shortest(tests):
    for t in tests:
        n, roads, src = t["args"]
        assert 1 <= n <= 2000 and len(roads) <= 5000 and 0 <= src < n
        for a, b, w in roads:
            assert 0 <= a < n and 0 <= b < n and 1 <= w <= 1000
        assert len(t["expected"]) == n and t["expected"][src] == 0


CHECKS["shortest-distances-from-source"] = (b_shortest, g_shortest, "exact")
VALIDATE["shortest-distances-from-source"] = v_shortest

# ---------------------------------------------------------------- kth smallest in a min-heap array
p = add(
    id="kth-smallest-in-min-heap-array", title="K-th Smallest in a Min-Heap Array", diff="Medium", topic="Heap",
    fn="kthSmallestInHeap", params=[("heap", "int[]"), ("k", "int")], ret="int", cmp="exact",
    desc="<p>The array <code>heap</code> stores a binary min-heap: the children of index <code>i</code> are at <code>2i + 1</code> and <code>2i + 2</code>, and every element is less than or equal to its children. The array is <em>not</em> sorted.</p><p>Return the <code>k</code>-th smallest value in the heap (1-indexed, counting duplicates separately). Do it in about O(k log k) time without sorting the whole array.</p><pre>heap = [1, 3, 2, 6, 4, 5, 7], k = 4\nsorted order: 1, 2, 3, 4, 5, 6, 7  ->  4</pre>",
    constraints=["1 &le; heap.length &le; 8,000", "heap is a valid min-heap in the layout above", "1 &le; k &le; heap.length", "-10<sup>9</sup> &le; heap[i] &le; 10<sup>9</sup>"],
    hints=["Sorting the array costs O(n log n) even when k is tiny. The heap structure already tells you a lot about where small values are.",
           "The smallest value is at index 0. The second smallest must be a child of something already known to be among the smallest.",
           "Run a second min-heap holding candidate indices keyed by their values. Pop the smallest candidate k - 1 times, each time pushing its (up to two) children. The top after that is the k-th smallest."],
    editorial=["A node can only be among the k smallest if all of its ancestors are too, because ancestors are never larger. So the k smallest values form a connected piece of the tree containing the root, and we can grow that piece one node at a time: the next smallest value is always the smallest child of the piece that is not yet included.",
               "Keep an auxiliary min-heap of (value, index). Start with the root. Repeat k - 1 times: pop the smallest, push its children if they exist. After these pops the root of the auxiliary heap is the k-th smallest. The auxiliary heap never holds more than k + 1 entries, so the time is O(k log k) and the space O(k), independent of n.",
               "Ties are harmless: equal values are counted as separate elements, which matches how the pops proceed."],
    time="O(k log k)", space="O(k)",
    solution='''import heapq


def kthSmallestInHeap(heap, k):
    n = len(heap)
    cand = [(heap[0], 0)]
    for _ in range(k - 1):
        v, i = heapq.heappop(cand)
        for c in (2 * i + 1, 2 * i + 2):
            if c < n:
                heapq.heappush(cand, (heap[c], c))
    return cand[0][0]
''',
    tests=[[[1, 3, 2, 6, 4, 5, 7], 4], [[5], 1], [[1, 1, 1, 1], 3], [[2, 9], 2], [[-5, -1, -3, 0, 4, 8, -2], 5],
           [[1, 2, 3, 4, 5, 6, 7, 8, 9, 10], 10], [[4, 4, 5, 4, 6, 5, 5], 4], [[1, 100, 2, 101, 102, 3, 4], 3],
           [[-10 ** 9, 10 ** 9, -10 ** 9, 10 ** 9], 2]],
)
_r = rnd(9503)
_a = _heap_from(_r, 4000, -10 ** 9, 10 ** 9)
p["tests"].append([_a, 2000])
p["tests"].append([_a[:100], 100])
_a = sorted(_r.randint(-1000, 1000) for _ in range(4000))
p["tests"].append([_a, 2001])  # sorted array, heavy ties
_a = _heap_from(_r, 8000, 0, 30)
p["tests"].append([_a, 1])


def b_kheap(heap, k):
    return sorted(heap)[k - 1]


def g_kheap(r):
    n = r.randint(1, 12)
    return [_heap_from(r, n, -6, 6), r.randint(1, n)]


def v_kheap(tests):
    for t in tests:
        h, k = t["args"]
        assert 1 <= len(h) <= 8000 and 1 <= k <= len(h) and _is_heap(h)
        assert all(-10 ** 9 <= x <= 10 ** 9 for x in h)


CHECKS["kth-smallest-in-min-heap-array"] = (b_kheap, g_kheap, "exact")
VALIDATE["kth-smallest-in-min-heap-array"] = v_kheap

# ---------------------------------------------------------------- widest path
p = add(
    id="widest-path-between-two-nodes", title="Widest Path Between Two Nodes", diff="Medium", topic="Heap",
    fn="widestPath", params=[("n", "int"), ("links", "int[][]"), ("src", "int"), ("dst", "int")], ret="int", cmp="exact",
    desc="<p>A network has <code>n</code> servers numbered <code>0</code> to <code>n - 1</code>. Each entry <code>links[i] = [a, b, c]</code> is a two-way cable between servers <code>a</code> and <code>b</code> that can carry at most <code>c</code> units of bandwidth. Several cables may join the same pair.</p><p>The bandwidth of a route is the <em>smallest</em> capacity among the cables it uses. Return the largest bandwidth that any route from <code>src</code> to <code>dst</code> can have, or <code>-1</code> if the two servers are not connected.</p><pre>n = 4, src = 0, dst = 3\nlinks = [[0,1,5], [1,3,3], [0,2,4], [2,3,4]]\n0-1-3 has bandwidth min(5, 3) = 3\n0-2-3 has bandwidth min(4, 4) = 4   -> answer 4</pre>",
    constraints=["2 &le; n &le; 2,000", "0 &le; links.length &le; 5,000", "0 &le; a, b &lt; n and a &ne; b", "1 &le; c &le; 10<sup>9</sup>", "0 &le; src, dst &lt; n and src &ne; dst"],
    hints=["The route with the fewest cables or the one with the largest total capacity is not necessarily the best. What really matters is the weakest cable on the route.",
           "This looks like Dijkstra, but a route's value is the minimum of its edge capacities instead of their sum, and bigger is better.",
           "Keep best[v], the widest bandwidth found so far to v (best[src] = infinity). Use a max-heap: pop the server with the widest bandwidth, and for each cable to v offer min(best[u], c); keep it if it beats best[v]."],
    editorial=["Dijkstra works for any route value that never improves when you extend a route and that is monotone in the prefix. Here extending a route can only keep or lower its bottleneck, and a wider prefix is never worse than a narrower one, so greedily finalising the widest unfinished server is safe.",
               "Run a max-heap version: start with <code>best[src]</code> = infinity. Pop the largest (bandwidth, server). If it is stale, skip it; if it is dst, you can stop. Otherwise, for each cable (u, v, c) compute <code>cand = min(bandwidth, c)</code> and push if it exceeds <code>best[v]</code>. At the end the answer is <code>best[dst]</code>, or -1 if it was never set.",
               "Complexity is O((V + E) log E). Another valid approach sorts the cables by capacity descending and unions endpoints until src and dst join, which gives the capacity of the cable that connected them (this is the maximum spanning tree view)."],
    time="O((V + E) log E)", space="O(V + E)",
    solution='''import heapq


def widestPath(n, links, src, dst):
    adj = [[] for _ in range(n)]
    for a, b, c in links:
        adj[a].append((b, c))
        adj[b].append((a, c))
    best = [0] * n
    best[src] = float('inf')
    heap = [(-best[src], src)]
    while heap:
        negw, u = heapq.heappop(heap)
        w = -negw
        if w < best[u]:
            continue
        if u == dst:
            return w
        for v, c in adj[u]:
            cand = min(w, c)
            if cand > best[v]:
                best[v] = cand
                heapq.heappush(heap, (-cand, v))
    return -1
''',
    tests=[[4, [[0, 1, 5], [1, 3, 3], [0, 2, 4], [2, 3, 4]], 0, 3], [2, [], 0, 1], [2, [[0, 1, 9]], 1, 0], [3, [[0, 1, 4], [0, 1, 8], [1, 2, 6]], 0, 2],
           [4, [[0, 1, 10], [2, 3, 10]], 0, 3], [5, [[0, 1, 1], [1, 2, 1], [2, 3, 1], [3, 4, 1], [0, 4, 1]], 0, 4],
           [5, [[0, 1, 10 ** 9], [1, 2, 10 ** 9], [2, 3, 10 ** 9], [3, 4, 10 ** 9]], 4, 0],
           [6, [[0, 1, 7], [1, 5, 2], [0, 2, 3], [2, 3, 6], [3, 5, 5], [0, 4, 9], [4, 5, 1]], 0, 5],
           [4, [[0, 1, 2], [1, 2, 9], [2, 3, 9], [0, 3, 1]], 0, 3]],
)
_r = rnd(9504)
_n = 1000
_e = [[a, b, _r.randint(1, 10 ** 9)] for a, b in _connected_pairs(_r, _n, 2500)]
p["tests"].append([_n, _e, 3, 777])
_n = 1500
_e = [[i, i + 1, _r.randint(10 ** 8, 10 ** 9)] for i in range(_n - 1)]
_e += [[a, b, _r.randint(1, 10 ** 8)] for a, b in _pairs(_r, _n, 1500) if abs(a - b) > 1]
_r.shuffle(_e)
p["tests"].append([_n, _e, 0, _n - 1])
_n = 800
_e = [[a, b, _r.randint(1, 1000)] for a, b in _pairs(_r, _n // 2, 1500)]
p["tests"].append([_n, _e, 1, _n - 1])  # dst isolated: -1


def b_widest(n, links, src, dst):
    adj = [[] for _ in range(n)]
    for a, b, c in links:
        adj[a].append((b, c))
        adj[b].append((a, c))
    best = [-1]

    def dfs(u, seen, cur):
        if u == dst:
            best[0] = max(best[0], cur)
            return
        for v, c in adj[u]:
            if v not in seen:
                seen.add(v)
                dfs(v, seen, min(cur, c))
                seen.discard(v)

    dfs(src, {src}, float('inf'))
    return best[0]


def g_widest(r):
    n = r.randint(2, 6)
    m = r.randint(0, 9)
    links = []
    for _ in range(m):
        a, b = r.sample(range(n), 2)
        links.append([a, b, r.randint(1, 9)])
    a, b = r.sample(range(n), 2)
    return [n, links, a, b]


def v_widest(tests):
    for t in tests:
        n, links, s, d = t["args"]
        assert 2 <= n <= 2000 and len(links) <= 5000 and s != d and 0 <= s < n and 0 <= d < n
        for a, b, c in links:
            assert a != b and 0 <= a < n and 0 <= b < n and 1 <= c <= 10 ** 9
    assert any(t["expected"] == -1 for t in tests)


CHECKS["widest-path-between-two-nodes"] = (b_widest, g_widest, "exact")
VALIDATE["widest-path-between-two-nodes"] = v_widest

# ---------------------------------------------------------------- half-price coupons
p = add(
    id="cheapest-route-with-half-price-coupons", title="Cheapest Route with Half-Price Coupons", diff="Medium", topic="Heap",
    fn="minCostWithCoupons", params=[("n", "int"), ("roads", "int[][]"), ("k", "int")], ret="int", cmp="exact",
    desc="<p>A country has <code>n</code> cities numbered <code>0</code> to <code>n - 1</code> and two-way toll roads: <code>roads[i] = [a, b, w]</code> is a road between <code>a</code> and <code>b</code> with toll <code>w</code>. You travel from city <code>0</code> to city <code>n - 1</code>.</p><p>You own <code>k</code> half-price coupons. Whenever you drive along a road you may spend <em>one</em> coupon on it, and then you pay only <code>w // 2</code> (rounded down) for that drive. A coupon is used up when spent; you do not have to spend all of them, and you cannot spend two on the same drive.</p><p>Return the least total toll to get from city <code>0</code> to city <code>n - 1</code>, or <code>-1</code> if the city cannot be reached. If <code>n == 1</code> the answer is <code>0</code>.</p><pre>n = 3, roads = [[0,1,10], [1,2,10], [0,2,40]]\nk = 0 -> 20   (0-1-2)\nk = 1 -> 15   (0-1-2 with a coupon on one road: 5 + 10)\nk = 2 -> 10   (0-1-2 with both roads halved)</pre>",
    constraints=["1 &le; n &le; 500", "0 &le; roads.length &le; 3,000", "0 &le; a, b &lt; n and a &ne; b", "1 &le; w &le; 1,000", "0 &le; k &le; 10"],
    hints=["Plain Dijkstra on cities is not enough: two ways of reaching a city can leave you with a different number of coupons, and a more expensive one may be better in the long run.",
           "Make the state (city, coupons used so far). Moving along a road leads either to (v, j) paying w, or to (v, j + 1) paying w // 2.",
           "Run Dijkstra on these (n * (k + 1)) states with a min-heap. The answer is the smallest distance over all states (n - 1, j), j = 0..k."],
    editorial=["Think of k + 1 copies of the map, one per number of coupons spent. Driving along a road without a coupon stays on the same copy and costs w; driving with a coupon moves from copy j to copy j + 1 and costs w // 2. Reaching the destination in any copy is a valid finish, since you may leave coupons unused.",
               "All costs are non-negative, so Dijkstra over the layered graph is correct. There are at most 501 * 11 states and each state looks at every incident road twice, giving O(k (V + E) log (kV)) time.",
               "Because the starting city is distance 0 in layer 0 and a coupon can never raise a cost, <code>dist[v][j]</code> is non-increasing in j after taking the minimum over layers; the final answer is simply <code>min(dist[n-1][j] for j in 0..k)</code>."],
    time="O(k (V + E) log(kV))", space="O(kV + E)",
    solution='''import heapq


def minCostWithCoupons(n, roads, k):
    if n == 1:
        return 0
    adj = [[] for _ in range(n)]
    for a, b, w in roads:
        adj[a].append((b, w))
        adj[b].append((a, w))
    INF = float('inf')
    dist = [[INF] * (k + 1) for _ in range(n)]
    dist[0][0] = 0
    heap = [(0, 0, 0)]
    while heap:
        d, u, j = heapq.heappop(heap)
        if d > dist[u][j]:
            continue
        if u == n - 1:
            return d
        for v, w in adj[u]:
            if d + w < dist[v][j]:
                dist[v][j] = d + w
                heapq.heappush(heap, (d + w, v, j))
            if j < k and d + w // 2 < dist[v][j + 1]:
                dist[v][j + 1] = d + w // 2
                heapq.heappush(heap, (d + w // 2, v, j + 1))
    return -1
''',
    tests=[[3, [[0, 1, 10], [1, 2, 10], [0, 2, 40]], 1], [3, [[0, 1, 10], [1, 2, 10], [0, 2, 40]], 0], [3, [[0, 1, 10], [1, 2, 10], [0, 2, 40]], 2],
           [1, [], 5], [2, [], 3], [2, [[0, 1, 1]], 10], [2, [[0, 1, 7], [0, 1, 9]], 1],
           [4, [[0, 1, 100], [1, 3, 100], [0, 2, 1], [2, 3, 1]], 2], [4, [[0, 1, 100], [1, 3, 100], [0, 2, 50], [2, 3, 49]], 1],
           [5, [[0, 1, 400], [1, 2, 400], [2, 3, 400], [3, 4, 400], [0, 4, 999]], 3],
           [5, [[0, 1, 3], [1, 2, 3], [2, 3, 3], [3, 4, 3]], 4], [4, [[0, 1, 5], [2, 3, 5]], 3]],
)
_r = rnd(9505)
_n = 500
_e = [[a, b, _r.randint(1, 1000)] for a, b in _connected_pairs(_r, _n, 2500)]
p["tests"].append([_n, _e, 10])
_n = 400
_e = [[i, i + 1, _r.randint(500, 1000)] for i in range(_n - 1)]
_e += [[a, b, _r.randint(1, 1000)] for a, b in _pairs(_r, _n, 900) if abs(a - b) > 1]
_r.shuffle(_e)
p["tests"].append([_n, _e, 7])


def b_coupons(n, roads, k):
    if n == 1:
        return 0
    adj = [[] for _ in range(n)]
    for a, b, w in roads:
        adj[a].append((b, w))
        adj[b].append((a, w))
    best = [None]

    def dfs(u, seen, tolls):
        if u == n - 1:
            sav = sorted((w - w // 2 for w in tolls), reverse=True)[:k]
            cost = sum(tolls) - sum(sav)
            if best[0] is None or cost < best[0]:
                best[0] = cost
            return
        for v, w in adj[u]:
            if v not in seen:
                seen.add(v)
                tolls.append(w)
                dfs(v, seen, tolls)
                tolls.pop()
                seen.discard(v)

    dfs(0, {0}, [])
    return -1 if best[0] is None else best[0]


def g_coupons(r):
    n = r.randint(1, 6)
    roads = []
    for _ in range(r.randint(0, 9)):
        if n >= 2:
            a, b = r.sample(range(n), 2)
            roads.append([a, b, r.randint(1, 20)])
    return [n, roads, r.randint(0, 3)]


def v_coupons(tests):
    for t in tests:
        n, roads, k = t["args"]
        assert 1 <= n <= 500 and len(roads) <= 3000 and 0 <= k <= 10
        for a, b, w in roads:
            assert a != b and 0 <= a < n and 0 <= b < n and 1 <= w <= 1000
    assert any(t["expected"] == -1 for t in tests)


CHECKS["cheapest-route-with-half-price-coupons"] = (b_coupons, g_coupons, "exact")
VALIDATE["cheapest-route-with-half-price-coupons"] = v_coupons

# ---------------------------------------------------------------- restricted paths
p = add(
    id="restricted-paths-count", title="Count Paths That Always Get Closer", diff="Medium", topic="Heap", tier="extra",
    fn="countRestrictedPaths", params=[("n", "int"), ("roads", "int[][]")], ret="int", cmp="exact",
    desc="<p>A town has <code>n</code> junctions numbered <code>0</code> to <code>n - 1</code> and two-way roads <code>roads[i] = [a, b, w]</code> of length <code>w</code>. No two roads join the same pair of junctions.</p><p>Let <code>d(x)</code> be the length of the shortest route from junction <code>x</code> to junction <code>n - 1</code> (it is infinite if there is no route). A <em>closing-in path</em> from <code>0</code> to <code>n - 1</code> is a sequence of junctions in which consecutive junctions are joined by a road and <code>d</code> becomes <em>strictly smaller</em> at every step.</p><p>Return the number of closing-in paths modulo <code>1,000,000,007</code>. For <code>n = 1</code> the answer is <code>1</code> (the path consisting only of junction 0).</p><pre>n = 4, roads = [[0,1,1], [1,3,1], [0,2,1], [2,3,1], [1,2,1]]\nd = [2, 1, 1, 0]\npaths: 0-1-3 and 0-2-3  -> 2   (1-2 is not allowed, d does not shrink)</pre>",
    constraints=["1 &le; n &le; 1,500", "0 &le; roads.length &le; 4,000", "0 &le; a, b &lt; n, a &ne; b, and each pair appears at most once", "1 &le; w &le; 1,000"],
    hints=["First you need d(x) for every junction. From which junction should you run the shortest-path search, so that one run gives all of d?",
           "Run Dijkstra from junction n - 1. Because d must strictly decrease along a path, the paths form a DAG, so you can count them with DP instead of enumerating them.",
           "Sort the reachable junctions by d. Set ways[n-1] = 1 and, in increasing d order, ways[u] = sum of ways[v] over roads (u, v) with d[v] &lt; d[u]. The answer is ways[0] (0 if junction 0 cannot reach n - 1)."],
    editorial=["Roads are two-way, so distances to the target equal distances from the target: run Dijkstra from <code>n - 1</code>. Since weights are at least 1, <code>n - 1</code> is the only junction with d = 0.",
               "A step from u to v is allowed exactly when <code>d[v] &lt; d[u]</code>. Along any allowed path d strictly decreases, so no junction repeats and the allowed steps form a directed acyclic graph that is naturally ordered by d. Count the paths from each junction to the target: <code>ways[u] = sum(ways[v])</code> over allowed steps, processing junctions by increasing d so that every <code>ways[v]</code> is final when it is needed.",
               "Dijkstra costs O((V + E) log V) and the DP is O(V log V + E) for the sort and the scan. Junctions with infinite d are skipped; if junction 0 is among them the answer is 0. Counts are reduced modulo 1,000,000,007 because they can be exponentially large."],
    time="O((V + E) log V)", space="O(V + E)",
    solution='''import heapq


def countRestrictedPaths(n, roads):
    MOD = 1000000007
    adj = [[] for _ in range(n)]
    for a, b, w in roads:
        adj[a].append((b, w))
        adj[b].append((a, w))
    INF = float('inf')
    dist = [INF] * n
    dist[n - 1] = 0
    heap = [(0, n - 1)]
    while heap:
        d, u = heapq.heappop(heap)
        if d > dist[u]:
            continue
        for v, w in adj[u]:
            if d + w < dist[v]:
                dist[v] = d + w
                heapq.heappush(heap, (d + w, v))
    order = sorted((d, u) for u, d in enumerate(dist) if d < INF)
    ways = [0] * n
    ways[n - 1] = 1
    for d, u in order:
        if u == n - 1:
            continue
        total = 0
        for v, w in adj[u]:
            if dist[v] < d:
                total += ways[v]
        ways[u] = total % MOD
    return ways[0] % MOD
''',
    tests=[[4, [[0, 1, 1], [1, 3, 1], [0, 2, 1], [2, 3, 1], [1, 2, 1]]], [1, []], [2, []], [2, [[0, 1, 5]]], [3, [[0, 1, 1], [1, 2, 1], [0, 2, 5]]],
           [3, [[0, 1, 1], [1, 2, 1], [0, 2, 2]]], [4, [[0, 1, 1], [1, 2, 1], [2, 3, 1]]], [4, [[0, 1, 1], [2, 3, 1]]],
           [5, [[0, 1, 3], [0, 2, 3], [1, 2, 1], [0, 3, 2], [4, 1, 2], [2, 4, 1], [4, 3, 10]]],
           [6, [[0, 5, 10], [0, 1, 1], [1, 2, 1], [2, 5, 9], [0, 3, 1], [3, 4, 1], [4, 5, 7]]]],
)
_r = rnd(9506)
_n = 1500
_e = [[a, b, _r.randint(1, 1000)] for a, b in _connected_pairs(_r, _n, 4000)]
p["tests"].append([_n, _e])
_side = 38
_e = []
for _i in range(_side):
    for _j in range(_side):
        if _j + 1 < _side:
            _e.append([_i * _side + _j, _i * _side + _j + 1, _r.randint(1, 2)])
        if _i + 1 < _side:
            _e.append([_i * _side + _j, (_i + 1) * _side + _j, _r.randint(1, 2)])
p["tests"].append([_side * _side, _e])  # grid-like graph, huge counts
_n = 1000
_e = [[a, b, _r.randint(1, 5)] for a, b in _pairs(_r, 600, 1500)]
p["tests"].append([_n, _e])


def b_restricted(n, roads):
    INF = float('inf')
    d = [[INF] * n for _ in range(n)]
    for i in range(n):
        d[i][i] = 0
    adj = [[] for _ in range(n)]
    for a, b, w in roads:
        d[a][b] = min(d[a][b], w)
        d[b][a] = min(d[b][a], w)
        adj[a].append(b)
        adj[b].append(a)
    for k in range(n):
        for i in range(n):
            for j in range(n):
                if d[i][k] + d[k][j] < d[i][j]:
                    d[i][j] = d[i][k] + d[k][j]
    dist = [d[x][n - 1] for x in range(n)]

    def go(u):
        if u == n - 1:
            return 1
        return sum(go(v) for v in adj[u] if dist[v] < dist[u])

    if dist[0] == INF:
        return 0
    return go(0) % MOD


def g_restricted(r):
    n = r.randint(1, 7)
    m = r.randint(0, min(10, n * (n - 1) // 2))
    return [n, [[a, b, r.randint(1, 4)] for a, b in _pairs(r, n, m)]]


def v_restricted(tests):
    for t in tests:
        n, roads = t["args"]
        assert 1 <= n <= 1500 and len(roads) <= 4000
        _simple_pairs_ok(roads, n)
        assert all(1 <= w <= 1000 for _, _, w in roads)
    assert any(t["expected"] == 0 for t in tests)


CHECKS["restricted-paths-count"] = (b_restricted, g_restricted, "exact")
VALIDATE["restricted-paths-count"] = v_restricted

# ================================================================ HARD

# ---------------------------------------------------------------- trapping rain water II
p = add(
    id="trapping-rain-water-ii", title="Trapping Rain Water on a Grid", diff="Hard", topic="Heap",
    fn="trapRainWater", params=[("heights", "int[][]")], ret="int", cmp="exact",
    desc="<p>The grid <code>heights</code> gives the height of the ground in every unit cell of a rectangular field. After a long rain, water collects in the low parts. Water can flow from a cell to its four side neighbours (up, down, left, right) whenever the neighbour's water surface is not higher, and everything that reaches the outside of the grid is lost.</p><p>Return the total volume of water that stays trapped, counting one unit of volume for each unit of water depth over each cell.</p><pre>heights = [[5,5,5],\n           [5,1,5],\n           [5,5,5]]\n-> 4   (the middle cell holds water up to height 5)</pre><pre>heights = [[3,3,3,3],\n           [3,1,1,3],\n           [3,3,3,3]]\n-> 4   (two cells, each filled from 1 to 3)</pre>",
    constraints=["1 &le; rows, cols &le; 60", "0 &le; heights[i][j] &le; 10,000", "All rows have the same length"],
    hints=["In one dimension you can use the tallest wall on each side. In two dimensions water can escape through any direction, so the lowest point of the whole boundary matters most.",
           "The water level of a cell is limited by the lowest 'gate' on the best escape path out of the grid. Start from the border cells, which hold no water, and work inwards.",
           "Put all border cells in a min-heap by height. Pop the lowest cell; for each unvisited neighbour, its water level is max(neighbour height, popped level), so it traps max(0, level - height) water. Push the neighbour with that level."],
    editorial=["A cell's final water level is the smallest possible value of 'the highest cell you must cross' over all paths from that cell to the border. Dijkstra-style processing gives this directly: always expand the lowest known boundary of the already-processed region.",
               "Mark all border cells visited and push (height, r, c) into a min-heap. Pop the lowest (level, r, c). For each unvisited neighbour (nr, nc), mark it visited, add <code>max(0, level - heights[nr][nc])</code> to the answer, and push it with level <code>max(level, heights[nr][nc])</code>. The popped level is the lowest wall of the current frontier, so any neighbour lower than it is guaranteed to fill up to exactly that level - water cannot leak because every other part of the frontier is at least as high.",
               "Each cell is pushed and popped once, so the time is O(R C log(R C)) and the space is O(R C). Grids with fewer than three rows or columns have no interior and trap nothing."],
    time="O(R C log(R C))", space="O(R C)",
    solution='''import heapq


def trapRainWater(heights):
    R, C = len(heights), len(heights[0])
    if R < 3 or C < 3:
        return 0
    seen = [[False] * C for _ in range(R)]
    heap = []
    for i in range(R):
        for j in range(C):
            if i in (0, R - 1) or j in (0, C - 1):
                seen[i][j] = True
                heap.append((heights[i][j], i, j))
    heapq.heapify(heap)
    total = 0
    while heap:
        level, i, j = heapq.heappop(heap)
        for ni, nj in ((i + 1, j), (i - 1, j), (i, j + 1), (i, j - 1)):
            if 0 <= ni < R and 0 <= nj < C and not seen[ni][nj]:
                seen[ni][nj] = True
                h = heights[ni][nj]
                if h < level:
                    total += level - h
                    heapq.heappush(heap, (level, ni, nj))
                else:
                    heapq.heappush(heap, (h, ni, nj))
    return total
''',
    tests=[[[[5, 5, 5], [5, 1, 5], [5, 5, 5]]], [[[3, 3, 3, 3], [3, 1, 1, 3], [3, 3, 3, 3]]], [[[7]]], [[[1, 2, 3], [4, 5, 6]]],
           [[[1, 4, 3, 1, 3, 2], [3, 2, 1, 3, 2, 4], [2, 3, 3, 2, 3, 1]]],
           [[[12, 13, 1, 12], [13, 4, 13, 12], [13, 8, 10, 12], [12, 13, 12, 12], [13, 13, 13, 13]]],
           [[[9, 9, 9, 9, 9], [9, 0, 9, 0, 9], [9, 0, 9, 0, 9], [9, 9, 9, 9, 9]]],
           [[[5, 5, 5, 1], [5, 1, 1, 5], [5, 1, 5, 5], [5, 2, 5, 8]]],
           [[[0, 0, 0], [0, 10000, 0], [0, 0, 0]]], [[[10000, 10000, 10000], [10000, 0, 10000], [10000, 10000, 10000]]],
           [[[3, 3, 3, 3, 3], [3, 0, 0, 0, 3], [3, 0, 2, 0, 3], [3, 0, 0, 0, 3], [3, 3, 3, 0, 3]]]],
)
_r = rnd(9507)
p["tests"].append([[[_r.randint(0, 10000) for _ in range(60)] for _ in range(60)]])
p["tests"].append([[[_r.randint(8000, 10000) if (i in (0, 59) or j in (0, 59)) else _r.randint(0, 9000) for j in range(60)] for i in range(60)]])
p["tests"].append([[[(abs(i - 30) + abs(j - 30)) * 150 + _r.randint(0, 20) for j in range(60)] for i in range(60)]])  # a big bowl
p["tests"].append([[[_r.randint(0, 3) for _ in range(60)] for _ in range(40)]])


def b_rain(heights):
    R, C = len(heights), len(heights[0])
    INF = 10 ** 9
    lvl = [[heights[i][j] if (i in (0, R - 1) or j in (0, C - 1)) else INF for j in range(C)] for i in range(R)]
    changed = True
    while changed:
        changed = False
        for i in range(1, R - 1):
            for j in range(1, C - 1):
                m = min(lvl[i - 1][j], lvl[i + 1][j], lvl[i][j - 1], lvl[i][j + 1])
                v = max(heights[i][j], m)
                if v < lvl[i][j]:
                    lvl[i][j] = v
                    changed = True
    return sum(lvl[i][j] - heights[i][j] for i in range(R) for j in range(C))


def g_rain(r):
    R, C = r.randint(1, 6), r.randint(1, 6)
    hi = r.choice([2, 4, 9])
    return [[[r.randint(0, hi) for _ in range(C)] for _ in range(R)]]


def v_rain(tests):
    for t in tests:
        g = t["args"][0]
        assert 1 <= len(g) <= 60 and all(len(row) == len(g[0]) for row in g) and 1 <= len(g[0]) <= 60
        assert all(0 <= v <= 10000 for row in g for v in row)
    assert any(t["expected"] == 0 for t in tests) and any(t["expected"] > 0 for t in tests)


CHECKS["trapping-rain-water-ii"] = (b_rain, g_rain, "exact")
VALIDATE["trapping-rain-water-ii"] = v_rain

# ---------------------------------------------------------------- reachable cells in subdivided corridors
p = add(
    id="reachable-cells-in-corridors", title="Reachable Cells in Subdivided Corridors", diff="Hard", topic="Heap",
    fn="reachableCells", params=[("n", "int"), ("corridors", "int[][]"), ("maxMoves", "int")], ret="int", cmp="exact",
    desc="<p>A maze has <code>n</code> junction rooms numbered <code>0</code> to <code>n - 1</code>. Each entry <code>corridors[i] = [a, b, cnt]</code> is a corridor between rooms <code>a</code> and <code>b</code> that contains <code>cnt</code> extra cells in a row between the two rooms (<code>cnt = 0</code> means the rooms are directly adjacent). A pair of rooms is joined by at most one corridor.</p><p>You start in room <code>0</code>. In one move you step to an adjacent cell (rooms and corridor cells are all cells). You can make at most <code>maxMoves</code> moves. Return the number of different cells (rooms and corridor cells) you can stand on, including room 0 itself.</p><pre>n = 3, corridors = [[0,1,4], [1,2,6], [0,2,1]], maxMoves = 5\nroom distances: 0, 5, 2 -> all 3 rooms are reachable\ncorridor 0-1: 4 cells from the room 0 side           -> 4\ncorridor 1-2: 0 from room 1, 3 from room 2            -> 3\ncorridor 0-2: the single cell                          -> 1\ntotal = 3 + 4 + 3 + 1 = 11</pre>",
    constraints=["1 &le; n &le; 1,500", "0 &le; corridors.length &le; 4,000", "0 &le; a, b &lt; n, a &ne; b, and each pair of rooms has at most one corridor", "0 &le; cnt &le; 10,000", "0 &le; maxMoves &le; 10<sup>9</sup>"],
    hints=["The corridors can hold up to 10,000 cells each, so you cannot create the cells and walk over them. Work with the rooms only.",
           "Find the minimum number of moves to reach each room (a corridor with cnt cells costs cnt + 1 moves between its rooms). That is Dijkstra on the rooms.",
           "For a corridor (a, b, cnt) you can enter from side a with max(0, maxMoves - dist[a]) moves left and from side b with max(0, maxMoves - dist[b]) moves left. The two sides may overlap, so you reach min(cnt, left_a + left_b) of its cells. Add the rooms with dist &le; maxMoves."],
    editorial=["Compute <code>dist[v]</code>, the fewest moves from room 0 to every room, with Dijkstra using corridor lengths <code>cnt + 1</code>. A room is reachable iff <code>dist[v] &le; maxMoves</code>.",
               "A corridor cell is reachable if it can be reached from one of its two end rooms. From room a you have <code>left_a = maxMoves - dist[a]</code> moves after arriving, which covers the first <code>left_a</code> cells of the corridor (if left_a is positive); symmetrically from room b. These two covered ranges start at opposite ends, so together they cover <code>min(cnt, left_a + left_b)</code> distinct cells - never more than the corridor holds. Taking the first-arrival shortest distances is enough because a cell inside a corridor can only be entered through one of its two ends.",
               "The answer is the number of reachable rooms plus the sum of that quantity over all corridors. It is O((V + E) log V) time; the cells are never created, which is why cnt up to 10,000 is fine. The result is at most 1,500 + 4,000 * 10,000 = 40,001,500, safely within 32 bits."],
    time="O((V + E) log V)", space="O(V + E)",
    solution='''import heapq


def reachableCells(n, corridors, maxMoves):
    adj = [[] for _ in range(n)]
    for a, b, cnt in corridors:
        adj[a].append((b, cnt + 1))
        adj[b].append((a, cnt + 1))
    INF = float('inf')
    dist = [INF] * n
    dist[0] = 0
    heap = [(0, 0)]
    while heap:
        d, u = heapq.heappop(heap)
        if d > dist[u]:
            continue
        for v, w in adj[u]:
            if d + w < dist[v]:
                dist[v] = d + w
                heapq.heappush(heap, (d + w, v))
    total = sum(1 for d in dist if d <= maxMoves)
    for a, b, cnt in corridors:
        left_a = max(0, maxMoves - dist[a])
        left_b = max(0, maxMoves - dist[b])
        total += min(cnt, left_a + left_b)
    return total
''',
    tests=[[3, [[0, 1, 4], [1, 2, 6], [0, 2, 1]], 5], [1, [], 0], [1, [], 100], [2, [[0, 1, 0]], 0], [2, [[0, 1, 0]], 1], [2, [[0, 1, 5]], 3],
           [2, [[0, 1, 5]], 6], [3, [[1, 2, 3]], 10], [3, [[0, 1, 10], [1, 2, 10]], 15], [3, [[0, 1, 10], [1, 2, 10], [0, 2, 10]], 8],
           [4, [[0, 1, 2], [1, 2, 2], [2, 3, 2], [3, 0, 2]], 5], [3, [[0, 1, 10000], [1, 2, 10000]], 10 ** 9],
           [5, [[0, 1, 1], [0, 2, 7], [1, 3, 4], [2, 3, 0], [3, 4, 9]], 9]],
)
_r = rnd(9508)
_n = 1000
_e = [[a, b, _r.randint(0, 10000)] for a, b in _connected_pairs(_r, _n, 3000)]
p["tests"].append([_n, _e, 30000])
_n = 1500
_e = [[a, b, _r.randint(0, 300)] for a, b in _connected_pairs(_r, _n, 2000)]
p["tests"].append([_n, _e, 1500])
_n = 600
_e = [[a, b, _r.randint(0, 10000)] for a, b in _pairs(_r, 300, 700)]
p["tests"].append([_n, _e, 10 ** 9])


def b_reach(n, corridors, maxMoves):
    adj = [[] for _ in range(n)]
    total = n
    for a, b, cnt in corridors:
        prev = a
        for _ in range(cnt):
            adj.append([])
            x = len(adj) - 1
            adj[prev].append(x)
            adj[x].append(prev)
            prev = x
        adj[prev].append(b)
        adj[b].append(prev)
    seen = {0: 0}
    frontier = [0]
    while frontier and seen[frontier[0]] < maxMoves:
        nxt = []
        for u in frontier:
            for v in adj[u]:
                if v not in seen:
                    seen[v] = seen[u] + 1
                    nxt.append(v)
        frontier = nxt
    return len(seen)


def g_reach(r):
    n = r.randint(1, 6)
    m = r.randint(0, min(8, n * (n - 1) // 2))
    return [n, [[a, b, r.randint(0, 5)] for a, b in _pairs(r, n, m)], r.randint(0, 14)]


def v_reach(tests):
    for t in tests:
        n, cor, mm = t["args"]
        assert 1 <= n <= 1500 and len(cor) <= 4000 and 0 <= mm <= 10 ** 9
        _simple_pairs_ok(cor, n)
        assert all(0 <= c <= 10000 for _, _, c in cor)


CHECKS["reachable-cells-in-corridors"] = (b_reach, g_reach, "exact")
VALIDATE["reachable-cells-in-corridors"] = v_reach

# ---------------------------------------------------------------- timed gates
p = add(
    id="earliest-arrival-through-timed-gates", title="Earliest Arrival Through Timed Gates", diff="Hard", topic="Heap",
    fn="earliestArrival", params=[("grid", "int[][]")], ret="int", cmp="exact",
    desc="<p>You are at the top-left cell <code>(0, 0)</code> of a grid at time <code>0</code>. Every cell contains a gate: <code>grid[r][c]</code> is the earliest time at which you are allowed to <em>step into</em> that cell (<code>grid[0][0] = 0</code>).</p><p>Each second you must move to one of the four side-adjacent cells; you cannot stay in place. A move that starts at second <code>t</code> puts you in the new cell at second <code>t + 1</code>, and it is allowed only if <code>t + 1 &ge; grid[new row][new col]</code>. You may walk back and forth between cells (for example to wait for a gate to open).</p><p>Return the earliest second at which you can be in the bottom-right cell, or <code>-1</code> if it is impossible. If the grid has one cell, the answer is <code>0</code>.</p><pre>grid = [[0, 1, 3],\n        [3, 2, 2]]\nsecond 1: (0,1)   second 2: (1,1)   second 3: (1,2)  -> 3</pre><pre>grid = [[0, 5],\n        [4, 1]]\nneither neighbour can be entered at second 1  -> -1</pre>",
    constraints=["1 &le; rows, cols &le; 60", "grid[0][0] = 0", "0 &le; grid[r][c] &le; 100,000"],
    hints=["First decide when the answer is impossible. At second 1 you must already be moving. What does that say about the two neighbours of (0, 0)?",
           "If you can make the first move, you can bounce between your current cell and the previous one forever, so waiting is always possible - but only in steps of 2 seconds.",
           "Run Dijkstra on cells with the earliest arrival time. To enter a neighbour with gate g at candidate time t + 1: if g &le; t + 1 use t + 1; otherwise use g when (g - (t + 1)) is even and g + 1 when it is odd."],
    editorial=["If neither the cell to the right nor the cell below the start can be entered at second 1 (both have gate &gt; 1), you can never leave the start cell, so the answer is -1. Otherwise you can always step to such a neighbour and back, so you can kill time two seconds at a time, and every gate eventually opens for good (gates only open, never close again).",
               "Dijkstra on the cells works with a small twist. Arriving at a cell u at time t, a neighbour v with gate g can be entered at time <code>t + 1</code> if <code>g &le; t + 1</code>. Otherwise you have to wait: bouncing changes your arrival time by multiples of 2, so the earliest valid arrival is g when <code>(g - (t + 1))</code> is even and <code>g + 1</code> when it is odd. Arriving earlier is never worse because you can always burn extra time later in steps of 2 (but not 1), which the parity rule already accounts for.",
               "Process cells with a min-heap keyed by arrival time; the first time the bottom-right cell is popped, its time is the answer. Each cell is relaxed at most four times, so the time is O(R C log(R C)). With R = C = 60 this is tiny."],
    time="O(R C log(R C))", space="O(R C)",
    solution='''import heapq


def earliestArrival(grid):
    R, C = len(grid), len(grid[0])
    if R == 1 and C == 1:
        return 0
    can_start = (R > 1 and grid[1][0] <= 1) or (C > 1 and grid[0][1] <= 1)
    if not can_start:
        return -1
    INF = float('inf')
    dist = [[INF] * C for _ in range(R)]
    dist[0][0] = 0
    heap = [(0, 0, 0)]
    while heap:
        t, r, c = heapq.heappop(heap)
        if t > dist[r][c]:
            continue
        if r == R - 1 and c == C - 1:
            return t
        for nr, nc in ((r + 1, c), (r - 1, c), (r, c + 1), (r, c - 1)):
            if 0 <= nr < R and 0 <= nc < C:
                nt = t + 1
                g = grid[nr][nc]
                if g > nt:
                    nt = g if (g - nt) % 2 == 0 else g + 1
                if nt < dist[nr][nc]:
                    dist[nr][nc] = nt
                    heapq.heappush(heap, (nt, nr, nc))
    return -1
''',
    tests=[[[[0, 1, 3], [3, 2, 2]]], [[[0, 5], [4, 1]]], [[[0]]], [[[0, 1, 1, 1]]], [[[0, 2, 1, 1]]], [[[0], [1], [9], [3]]],
           [[[0, 1, 3, 2], [5, 1, 2, 5], [4, 3, 8, 6]]], [[[0, 0], [0, 0]]], [[[0, 1], [1, 100000]]], [[[0, 1, 1], [1, 9, 1], [1, 1, 100000]]],
           [[[0, 2], [2, 2]]], [[[0, 1, 99999], [99999, 99999, 1]]]],
)
_r = rnd(9509)
_g = [[_r.randint(0, 100000) for _ in range(60)] for _ in range(60)]
_g[0][0] = 0
_g[0][1] = 1
p["tests"].append([_g])
_g = [[_r.randint(0, 200) for _ in range(60)] for _ in range(60)]
_g[0][0] = 0
_g[1][0] = 1
p["tests"].append([_g])
_g = [[_r.randint(0, 30) * 3 for _ in range(60)] for _ in range(40)]
_g[0][0] = 0
_g[0][1] = 1
_g[39][59] = 100000
p["tests"].append([_g])
_g = [[1 for _ in range(60)] for _ in range(60)]
_g[0][0] = 0
for _i in range(60):
    for _j in range(60):
        if (_i + _j) % 7 == 3:
            _g[_i][_j] = 5000 + _i * 40 + _j
p["tests"].append([_g])


def b_gates(grid):
    R, C = len(grid), len(grid[0])
    if R * C == 1:
        return 0
    T = max(max(row) for row in grid) + R + C + 6
    cur = {(0, 0)}
    for t in range(1, T + 1):
        nxt = set()
        for (r, c) in cur:
            for nr, nc in ((r + 1, c), (r - 1, c), (r, c + 1), (r, c - 1)):
                if 0 <= nr < R and 0 <= nc < C and grid[nr][nc] <= t:
                    nxt.add((nr, nc))
        cur = nxt
        if (R - 1, C - 1) in cur:
            return t
        if not cur:
            return -1
    return -1


def g_gates(r):
    R, C = r.randint(1, 4), r.randint(1, 4)
    hi = r.choice([2, 5, 9])
    g = [[r.randint(0, hi) for _ in range(C)] for _ in range(R)]
    g[0][0] = 0
    return [g]


def v_gates(tests):
    for t in tests:
        g = t["args"][0]
        assert 1 <= len(g) <= 60 and all(len(row) == len(g[0]) for row in g) and 1 <= len(g[0]) <= 60
        assert g[0][0] == 0 and all(0 <= v <= 100000 for row in g for v in row)
    assert any(t["expected"] == -1 for t in tests) and any(t["expected"] > 0 for t in tests)


CHECKS["earliest-arrival-through-timed-gates"] = (b_gates, g_gates, "exact")
VALIDATE["earliest-arrival-through-timed-gates"] = v_gates
