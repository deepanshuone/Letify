"""Problems: Dijkstra shortest paths (budgets, products, node fees, grids, state spaces, time-dependent edges)."""
import heapq

from lib import add, rnd, CHECKS, VALIDATE, gen_arr  # noqa: F401

INT_MIN, INT_MAX = -(2 ** 31), 2 ** 31 - 1
TOPIC = "Graphs"


# ------------------------------------------------------------------ shared helpers (tests only)
def _chain_edges(r, n, lo, hi):
    """A random Hamiltonian chain (as undirected edges), so the graph is connected."""
    perm = list(range(n))
    r.shuffle(perm)
    return [[perm[i], perm[i + 1], r.randint(lo, hi)] for i in range(n - 1)]


def _rand_edges(r, n, m, lo, hi):
    return [[r.randrange(n), r.randrange(n), r.randint(lo, hi)] for _ in range(m)]


def _connected_graph(r, n, extra, lo, hi):
    e = _chain_edges(r, n, lo, hi) + _rand_edges(r, n, extra, lo, hi)
    r.shuffle(e)
    return e


def _bf_dist(n, edges, src, directed):
    """Bellman-Ford style relaxation (independent of Dijkstra); None marks unreachable."""
    INF = float("inf")
    d = [INF] * n
    d[src] = 0
    for _ in range(n + 1):
        ch = False
        for a, b, w in edges:
            if d[a] + w < d[b]:
                d[b] = d[a] + w
                ch = True
            if not directed and d[b] + w < d[a]:
                d[a] = d[b] + w
                ch = True
        if not ch:
            break
    return d


# ================================================================ EASY

# ---------------------------------------------------------------- nodes reachable within a travel budget
p = add(
    id="nodes-reachable-within-travel-budget", title="Junctions Within a Travel Budget", diff="Easy", topic=TOPIC,
    fn="countWithinBudget", params=[("n", "int"), ("roads", "int[][]"), ("src", "int"), ("budget", "int")], ret="int", cmp="exact",
    desc="<p>A town has <code>n</code> junctions numbered <code>0</code> to <code>n - 1</code>. Each entry <code>roads[i] = [a, b, w]</code> is a two-way road between junctions <code>a</code> and <code>b</code> that takes <code>w</code> minutes to drive in either direction. Several roads may join the same pair of junctions, and a road may lead from a junction back to itself.</p><p>A courier starts at junction <code>src</code> and may drive for at most <code>budget</code> minutes in total. Return how many junctions the courier can reach, counting the starting junction itself. A junction counts if the <em>fastest</em> route to it takes at most <code>budget</code> minutes.</p><pre>n = 5, src = 0, budget = 5\nroads = [[0,1,4], [1,2,3], [0,3,2], [3,2,1], [3,4,9]]\nfastest times: 0 -> 0, 3 -> 2, 2 -> 3, 1 -> 4, 4 -> 11\n-> 4 junctions (0, 3, 2 and 1)</pre>",
    constraints=["1 &le; n &le; 1,000", "0 &le; roads.length &le; 3,000", "0 &le; a, b &lt; n", "1 &le; w &le; 1,000", "0 &le; src &lt; n", "0 &le; budget &le; 1,000,000"],
    hints=["A junction counts exactly when its fastest travel time from <code>src</code> is at most <code>budget</code>. So the real task is computing fastest travel times.",
           "Roads have different lengths, so breadth-first search (which counts roads, not minutes) is not enough. Expand junctions in order of increasing travel time using a min-heap of <code>(time, junction)</code>.",
           "Run Dijkstra from <code>src</code>. Because times only grow along a route, you can stop as soon as the popped time exceeds <code>budget</code>, or simply never push times above <code>budget</code>. Count each junction the first time it is popped."],
    editorial=["This is Dijkstra's algorithm with an early cut-off. Keep the best known time for every junction and a min-heap of <code>(time, junction)</code> pairs. The first time a junction leaves the heap its time is final, because every road takes a positive number of minutes and so no later route can be shorter.",
               "Since the heap pops times in non-decreasing order, the first popped time that exceeds <code>budget</code> means every remaining junction is out of reach, and we can stop. Each junction that is popped (and not stale) within the budget is counted once. The cost is O((V + E) log E); the cut-off just saves work.",
               "Edge cases: <code>budget = 0</code> gives 1 (only the start, since every road takes at least a minute); self-loops never help; parallel roads are handled by relaxation, which keeps the faster one."],
    time="O((V + E) log E)", space="O(V + E)",
    solution='''import heapq


def countWithinBudget(n, roads, src, budget):
    adj = [[] for _ in range(n)]
    for a, b, w in roads:
        adj[a].append((b, w))
        adj[b].append((a, w))
    best = [float('inf')] * n
    best[src] = 0
    heap = [(0, src)]
    count = 0
    while heap:
        d, u = heapq.heappop(heap)
        if d > best[u]:
            continue
        if d > budget:
            break
        count += 1
        for v, w in adj[u]:
            nd = d + w
            if nd <= budget and nd < best[v]:
                best[v] = nd
                heapq.heappush(heap, (nd, v))
    return count
''',
    tests=[[5, [[0, 1, 4], [1, 2, 3], [0, 3, 2], [3, 2, 1], [3, 4, 9]], 0, 5],
           [1, [], 0, 0], [3, [], 1, 100], [2, [[0, 1, 5]], 0, 4], [2, [[0, 1, 5]], 0, 5],
           [4, [[0, 0, 1], [0, 1, 2], [0, 1, 1], [1, 2, 1], [2, 3, 1]], 0, 3],
           [4, [[0, 1, 1], [1, 2, 1], [2, 3, 1]], 3, 1000000],
           [6, [[0, 1, 2], [2, 3, 2], [3, 4, 2], [4, 5, 2]], 3, 4],
           [5, [[0, 1, 10], [0, 2, 10], [0, 3, 10], [0, 4, 10], [1, 2, 1], [3, 4, 1]], 1, 11]],
)
_r = rnd(6001)
_e = _connected_graph(_r, 1000, 2000, 1, 1000)
p["tests"].append([1000, _e, _r.randrange(1000), 1800])
_e = [[i, i + 1, _r.randint(1, 10)] for i in range(999)] + _rand_edges(_r, 1000, 300, 1, 10)
_r.shuffle(_e)
p["tests"].append([1000, _e, 500, 400])
_e = _rand_edges(_r, 600, 1800, 1, 300)  # half of the junctions have no roads to the first half
_e += [[600 + _r.randrange(400), 600 + _r.randrange(400), _r.randint(1, 300)] for _ in range(1000)]
_r.shuffle(_e)
p["tests"].append([1000, _e, 7, 1000000])


def b_budget(n, roads, src, budget):
    d = _bf_dist(n, roads, src, False)
    return sum(1 for x in d if x <= budget)


def g_budget(r):
    n = r.randint(1, 7)
    return [n, _rand_edges(r, n, r.randint(0, 12), 1, 9), r.randrange(n), r.randint(0, 20)]


def v_budget(tests):
    for t in tests:
        n, roads, src, budget = t["args"]
        assert 1 <= n <= 1000 and len(roads) <= 3000 and 0 <= src < n and 0 <= budget <= 10 ** 6
        for a, b, w in roads:
            assert 0 <= a < n and 0 <= b < n and 1 <= w <= 1000
        assert 1 <= t["expected"] <= n


CHECKS["nodes-reachable-within-travel-budget"] = (b_budget, g_budget, "exact")
VALIDATE["nodes-reachable-within-travel-budget"] = v_budget

# ---------------------------------------------------------------- nearest hospital
p = add(
    id="nearest-hospital-travel-time", title="Nearest Hospital", diff="Easy", topic=TOPIC,
    fn="nearestHospital", params=[("n", "int"), ("roads", "int[][]"), ("src", "int"), ("hospitals", "int[]")], ret="int", cmp="exact",
    desc="<p>A city has <code>n</code> junctions numbered <code>0</code> to <code>n - 1</code> and <em>one-way</em> streets: <code>roads[i] = [a, b, w]</code> is a street from junction <code>a</code> to junction <code>b</code> that takes <code>w</code> minutes to drive. The array <code>hospitals</code> lists the distinct junctions that have a hospital.</p><p>An ambulance waits at junction <code>src</code>. Return the least number of minutes it needs to reach any hospital junction, or <code>-1</code> if no hospital can be reached. If <code>src</code> itself has a hospital the answer is <code>0</code>.</p><pre>n = 5, src = 0, hospitals = [2, 3, 4]\nroads = [[0,1,2], [1,2,2], [0,3,7], [4,0,1]]\njunction 2 takes 4 minutes, junction 3 takes 7, junction 4 cannot be reached\n-> 4</pre>",
    constraints=["1 &le; n &le; 1,000", "0 &le; roads.length &le; 3,000", "0 &le; a, b &lt; n", "1 &le; w &le; 1,000", "0 &le; src &lt; n", "0 &le; hospitals.length &le; n, all values distinct and in [0, n - 1]"],
    hints=["You need the shortest travel time to the <em>closest</em> of several targets, not to a fixed one.",
           "Dijkstra pops junctions in order of increasing travel time. What does that tell you about the first hospital you pop?",
           "Run Dijkstra from <code>src</code> with a min-heap and mark hospital junctions in a set. Return the popped time the first time a hospital junction comes out of the heap; if the heap runs dry, return -1."],
    editorial=["Run Dijkstra from the ambulance's junction. The heap releases junctions in non-decreasing order of their final travel time, so the first hospital junction that is popped is the closest hospital, and its popped time is the answer. There is no need to compute the remaining distances.",
               "Put the hospitals in a set for O(1) membership tests. If the heap is exhausted without popping a hospital, none is reachable and the answer is -1 (this also covers an empty hospital list). Time O((V + E) log E), space O(V + E).",
               "A common mistake is to run a separate search per hospital, which is much slower. Another is to stop when a hospital is first <em>pushed</em> instead of popped: a pushed time is only a candidate and may still be improved."],
    time="O((V + E) log E)", space="O(V + E)",
    solution='''import heapq


def nearestHospital(n, roads, src, hospitals):
    target = set(hospitals)
    adj = [[] for _ in range(n)]
    for a, b, w in roads:
        adj[a].append((b, w))
    best = [float('inf')] * n
    best[src] = 0
    heap = [(0, src)]
    while heap:
        d, u = heapq.heappop(heap)
        if d > best[u]:
            continue
        if u in target:
            return d
        for v, w in adj[u]:
            nd = d + w
            if nd < best[v]:
                best[v] = nd
                heapq.heappush(heap, (nd, v))
    return -1
''',
    tests=[[5, [[0, 1, 2], [1, 2, 2], [0, 3, 7], [4, 0, 1]], 0, [2, 3, 4]],
           [1, [], 0, [0]], [1, [], 0, []], [3, [[0, 1, 1], [1, 2, 1]], 0, []], [3, [[0, 1, 1], [1, 2, 1]], 2, [0, 1]],
           [4, [[0, 1, 5], [0, 2, 1], [2, 1, 1], [1, 3, 1]], 0, [1, 3]], [4, [[0, 1, 5], [0, 2, 1], [2, 1, 1], [1, 3, 1]], 0, [3]],
           [3, [[0, 0, 1], [0, 1, 4], [0, 1, 2], [1, 2, 3]], 0, [2]],
           [6, [[0, 1, 1], [1, 2, 1], [2, 0, 1], [3, 4, 1], [4, 5, 1]], 0, [3, 4, 5]],
           [5, [[0, 1, 100], [1, 2, 100], [2, 3, 100], [3, 4, 100], [0, 4, 999]], 0, [4]]],
)
_r = rnd(6002)
_n = 1000
_e = _rand_edges(_r, _n, 3000, 1, 1000)
p["tests"].append([_n, _e, 0, _r.sample(range(1, _n), 5)])
_e = [[i, i + 1, _r.randint(1, 1000)] for i in range(_n - 1)] + _rand_edges(_r, _n, 500, 1, 1000)
_r.shuffle(_e)
p["tests"].append([_n, _e, 0, [_n - 1]])
_e = [[i, i + 1, _r.randint(1, 1000)] for i in range(_n - 1)] + _rand_edges(_r, _n, 500, 1, 1000)
_r.shuffle(_e)
p["tests"].append([_n, _e, 600, list(range(0, 500))])  # hospitals only behind the start's reach


def b_nearest(n, roads, src, hospitals):
    d = _bf_dist(n, roads, src, True)
    vals = [d[h] for h in hospitals if d[h] != float("inf")]
    return min(vals) if vals else -1


def g_nearest(r):
    n = r.randint(1, 7)
    return [n, _rand_edges(r, n, r.randint(0, 12), 1, 9), r.randrange(n), r.sample(range(n), r.randint(0, n))]


def v_nearest(tests):
    for t in tests:
        n, roads, src, hosp = t["args"]
        assert 1 <= n <= 1000 and len(roads) <= 3000 and 0 <= src < n
        assert len(set(hosp)) == len(hosp) <= n and all(0 <= h < n for h in hosp)
        for a, b, w in roads:
            assert 0 <= a < n and 0 <= b < n and 1 <= w <= 1000


CHECKS["nearest-hospital-travel-time"] = (b_nearest, g_nearest, "exact")
VALIDATE["nearest-hospital-travel-time"] = v_nearest

# ================================================================ MEDIUM

# ---------------------------------------------------------------- most reliable route (product of loss factors)
p = add(
    id="most-reliable-route-product", title="Most Reliable Route", diff="Medium", topic=TOPIC,
    fn="leastLossFactor", params=[("n", "int"), ("links", "int[][]"), ("src", "int"), ("dst", "int")], ret="int", cmp="exact",
    desc="<p>A network has <code>n</code> servers numbered <code>0</code> to <code>n - 1</code>. Each entry <code>links[i] = [a, b, q]</code> is a two-way link between servers <code>a</code> and <code>b</code> that lets only <em>one packet in every <code>q</code></em> through, so a packet crosses it with probability <code>1/q</code>. A link with <code>q = 1</code> never loses anything. Several links may join the same pair of servers.</p><p>A route is a chain of links from <code>src</code> to <code>dst</code>. Crossing all its links in turn succeeds with probability <code>1 / (q<sub>1</sub> &middot; q<sub>2</sub> &middot; ...)</code>, so we call <code>q<sub>1</sub> &middot; q<sub>2</sub> &middot; ...</code> the <em>loss factor</em> of the route (the empty route from a server to itself has loss factor <code>1</code>). Return the smallest loss factor over all routes from <code>src</code> to <code>dst</code>, which is the most reliable route, or <code>-1</code> if the two servers are not connected.</p><p>The input guarantees that when <code>dst</code> is reachable, the smallest loss factor is at most 2<sup>31</sup> - 1. Loss factors of other, worse routes may be larger.</p><pre>n = 4, src = 0, dst = 3\nlinks = [[0,1,2], [1,3,2], [0,3,5], [0,2,1], [2,3,3]]\n0-1-3: 2*2 = 4,  0-3: 5,  0-2-3: 1*3 = 3\n-> 3</pre>",
    constraints=["1 &le; n &le; 1,000", "0 &le; links.length &le; 3,000", "0 &le; a, b &lt; n", "1 &le; q &le; 2<sup>31</sup> - 1", "0 &le; src, dst &lt; n", "If dst is reachable, the smallest loss factor is at most 2<sup>31</sup> - 1"],
    hints=["Probabilities multiply along a route, so the best route is the one with the smallest product of the <code>q</code> values, not the one with the fewest links.",
           "Dijkstra only needs one property of the route cost: it never decreases when you extend the route. Is that true for a product of numbers that are all at least 1?",
           "Run Dijkstra with 'cost' = product of q instead of sum. Start with product 1 at <code>src</code>, relax with <code>nd = d * q</code>, and skip any product above 2<sup>31</sup> - 1 (it can never be the answer, and it avoids overflow)."],
    editorial=["Dijkstra's algorithm works for any cost that is built from the route with an operation that never makes the cost smaller. Here the cost is a product of factors that are all at least 1, so extending a route never decreases it, and the first time a server is popped from the min-heap its product is final. The only changes from the textbook version are that the start has cost 1 (the empty product) and that relaxation multiplies instead of adding.",
               "The input guarantees the optimal product fits in 32 bits, so any candidate larger than 2<sup>31</sup> - 1 can be dropped. This prevents overflow in fixed-width languages and is safe: a route whose product already exceeds the bound can only grow, so it cannot lead to the optimum. If <code>dst</code> never gets popped, return -1.",
               "A second way to see it is to take logarithms: maximising probability means minimising the sum of <code>log q</code>, an ordinary non-negative shortest path. Working with exact integer products avoids floating-point error. Time O((V + E) log E)."],
    time="O((V + E) log E)", space="O(V + E)",
    solution='''import heapq


def leastLossFactor(n, links, src, dst):
    LIMIT = 2 ** 31 - 1
    adj = [[] for _ in range(n)]
    for a, b, q in links:
        adj[a].append((b, q))
        adj[b].append((a, q))
    best = [None] * n
    best[src] = 1
    heap = [(1, src)]
    while heap:
        d, u = heapq.heappop(heap)
        if d > best[u]:
            continue
        if u == dst:
            return d
        for v, q in adj[u]:
            nd = d * q
            if nd <= LIMIT and (best[v] is None or nd < best[v]):
                best[v] = nd
                heapq.heappush(heap, (nd, v))
    return -1
''',
    tests=[[4, [[0, 1, 2], [1, 3, 2], [0, 3, 5], [0, 2, 1], [2, 3, 3]], 0, 3],
           [1, [], 0, 0], [2, [], 0, 1], [3, [[0, 1, 7], [1, 2, 1]], 2, 0], [2, [[0, 1, 9], [0, 1, 4], [0, 1, 6]], 0, 1],
           [4, [[0, 3, 10], [0, 1, 2], [1, 2, 2], [2, 3, 2]], 0, 3],
           [4, [[0, 3, 8], [0, 1, 2], [1, 2, 2], [2, 3, 2]], 0, 3],
           [5, [[0, 1, 1], [1, 2, 1], [2, 3, 1], [3, 4, 1], [0, 4, 2]], 0, 4],
           [3, [[0, 0, 5], [0, 1, 3], [1, 1, 2], [1, 2, 3]], 0, 2],
           [3, [[0, 1, 1000000], [1, 2, 2147], [0, 2, 2147483647]], 0, 2],
           [6, [[0, 1, 46340], [1, 2, 46340], [2, 3, 1], [0, 4, 2], [4, 5, 2], [5, 3, 2147483647]], 0, 3]],
)
_r = rnd(6003)
_e = _connected_graph(_r, 1000, 1500, 1, 4)
p["tests"].append([1000, _e, _r.randrange(1000), _r.randrange(1000)])
_e = [[i, i + 1, 1] for i in range(0, 999, 2)] + [[i, i + 1, _r.randint(2, 30)] for i in range(1, 999, 2)]
_e += _rand_edges(_r, 1000, 800, 5, 50)
_r.shuffle(_e)
p["tests"].append([1000, _e, 0, 999])
_e = _rand_edges(_r, 500, 1500, 1, 3) + [[500 + _r.randrange(500), 500 + _r.randrange(500), _r.randint(1, 3)] for _ in range(1500)]
_r.shuffle(_e)
p["tests"].append([1000, _e, 3, 900])  # the two halves are not connected


def _bf_prod(n, links, src):
    d = [None] * n
    d[src] = 1
    for _ in range(n + 1):
        ch = False
        for a, b, q in links:
            for x, y in ((a, b), (b, a)):
                if d[x] is not None and (d[y] is None or d[x] * q < d[y]):
                    d[y] = d[x] * q
                    ch = True
        if not ch:
            break
    return d


def b_prod(n, links, src, dst):
    d = _bf_prod(n, links, src)[dst]
    return -1 if d is None else d


def g_prod(r):
    n = r.randint(1, 7)
    return [n, [[r.randrange(n), r.randrange(n), r.randint(1, 5)] for _ in range(r.randint(0, 12))], r.randrange(n), r.randrange(n)]


def v_prod(tests):
    for t in tests:
        n, links, src, dst = t["args"]
        assert 1 <= n <= 1000 and len(links) <= 3000 and 0 <= src < n and 0 <= dst < n
        for a, b, q in links:
            assert 0 <= a < n and 0 <= b < n and 1 <= q <= INT_MAX
        true = _bf_prod(n, links, src)[dst] if n <= 20 else None
        if true is None and n > 20:
            # exact (unpruned) Dijkstra to confirm the guarantee on the big tests
            adj = [[] for _ in range(n)]
            for a, b, q in links:
                adj[a].append((b, q))
                adj[b].append((a, q))
            best = {src: 1}
            h = [(1, src)]
            true = None
            while h:
                d, u = heapq.heappop(h)
                if d > best[u]:
                    continue
                if u == dst:
                    true = d
                    break
                for v, q in adj[u]:
                    if v not in best or d * q < best[v]:
                        best[v] = d * q
                        heapq.heappush(h, (d * q, v))
        if true is not None:
            assert true <= INT_MAX, "guarantee violated"
            assert t["expected"] == true
        else:
            assert t["expected"] == -1


CHECKS["most-reliable-route-product"] = (b_prod, g_prod, "exact")
VALIDATE["most-reliable-route-product"] = v_prod

# ---------------------------------------------------------------- cheapest route with city fees
p = add(
    id="cheapest-route-with-city-fees", title="Cheapest Route with City Fees", diff="Medium", topic=TOPIC,
    fn="cheapestRoute", params=[("n", "int"), ("roads", "int[][]"), ("fees", "int[]"), ("src", "int"), ("dst", "int")], ret="int", cmp="exact",
    desc="<p>A country has <code>n</code> cities numbered <code>0</code> to <code>n - 1</code>. Each entry <code>roads[i] = [a, b, toll]</code> is a two-way road between cities <code>a</code> and <code>b</code> with the given toll. In addition, every city <code>v</code> charges an entry fee <code>fees[v]</code> to every traveller who is in it, <em>including the city you start in and the city you end in</em>. If a route visits a city twice, the fee is paid twice.</p><p>Return the smallest total cost (all tolls plus all city fees along the route) of travelling from <code>src</code> to <code>dst</code>, or <code>-1</code> if there is no route. If <code>src == dst</code> the cost is just <code>fees[src]</code>.</p><pre>n = 4, src = 0, dst = 3, fees = [1, 10, 2, 1]\nroads = [[0,1,1], [1,3,1], [0,2,3], [2,3,3]]\nvia city 1: 1 + 1 + 10 + 1 + 1 = 14\nvia city 2: 1 + 3 + 2 + 3 + 1 = 10\n-> 10</pre>",
    constraints=["1 &le; n &le; 1,000", "0 &le; roads.length &le; 3,000", "0 &le; a, b &lt; n", "1 &le; toll &le; 1,000", "fees.length == n, 0 &le; fees[v] &le; 1,000", "0 &le; src, dst &lt; n"],
    hints=["The cost lives on cities as well as on roads. Think about which of the two is easier to turn into the other.",
           "Charge each city's fee when you <em>enter</em> it: moving along a road to city <code>v</code> costs <code>toll + fees[v]</code>. The start city's fee is paid up front.",
           "Now every step has a positive cost, so run ordinary Dijkstra from <code>src</code> with initial distance <code>fees[src]</code> and edge weight <code>toll + fees[v]</code>."],
    editorial=["Node weights can be folded into edge weights. Every route enters each city after the first through exactly one road, so assign the fee of the destination city to that road: the weight of travelling <code>u -> v</code> becomes <code>toll + fees[v]</code>, and the fee of the start city is added once as the initial distance. The total of such weights along a route equals tolls plus fees of every visited city.",
               "All new weights are at least 1 (tolls are positive), so Dijkstra applies directly. Because the fee is paid for every visit, a route that revisits a city is never better, which is consistent with a shortest path being simple.",
               "Remember to make the roads two-way, to initialise <code>dist[src] = fees[src]</code> (not 0), and to treat -1 for an unreachable destination. Time O((V + E) log E)."],
    time="O((V + E) log E)", space="O(V + E)",
    solution='''import heapq


def cheapestRoute(n, roads, fees, src, dst):
    adj = [[] for _ in range(n)]
    for a, b, toll in roads:
        adj[a].append((b, toll + fees[b]))
        adj[b].append((a, toll + fees[a]))
    INF = float('inf')
    dist = [INF] * n
    dist[src] = fees[src]
    heap = [(fees[src], src)]
    while heap:
        d, u = heapq.heappop(heap)
        if d > dist[u]:
            continue
        if u == dst:
            return d
        for v, w in adj[u]:
            nd = d + w
            if nd < dist[v]:
                dist[v] = nd
                heapq.heappush(heap, (nd, v))
    return -1
''',
    tests=[[4, [[0, 1, 1], [1, 3, 1], [0, 2, 3], [2, 3, 3]], [1, 10, 2, 1], 0, 3],
           [1, [], [5], 0, 0], [2, [], [1, 1], 0, 1], [2, [[0, 1, 4]], [0, 0], 0, 1], [2, [[0, 1, 4]], [7, 9], 1, 0],
           [3, [[0, 1, 1], [1, 2, 1], [0, 2, 10]], [0, 100, 0], 0, 2], [3, [[0, 1, 1], [1, 2, 1], [0, 2, 10]], [0, 8, 0], 0, 2],
           [3, [[0, 1, 1], [1, 2, 1], [0, 2, 10]], [0, 9, 0], 0, 2],
           [4, [[0, 0, 1], [0, 1, 5], [0, 1, 2], [1, 1, 3], [1, 2, 4]], [3, 0, 2, 1], 0, 2],
           [5, [[0, 1, 1], [1, 2, 1], [2, 3, 1]], [0, 0, 0, 0, 0], 0, 4]],
)
_r = rnd(6004)
_e = _connected_graph(_r, 1000, 2000, 1, 1000)
p["tests"].append([1000, _e, [_r.randint(0, 1000) for _ in range(1000)], _r.randrange(1000), _r.randrange(1000)])
_e = [[i, i + 1, _r.randint(1, 20)] for i in range(999)] + _rand_edges(_r, 1000, 600, 1, 1000)
_r.shuffle(_e)
p["tests"].append([1000, _e, [_r.randint(0, 5) if i % 7 else 1000 for i in range(1000)], 0, 999])
_e = _rand_edges(_r, 1000, 900, 1, 1000)
p["tests"].append([1000, _e, [_r.randint(0, 1000) for _ in range(1000)], 5, 997])


def b_fees(n, roads, fees, src, dst):
    best = [None]

    def dfs(u, cost, seen):
        if u == dst:
            if best[0] is None or cost < best[0]:
                best[0] = cost
            return
        for a, b, toll in roads:
            for x, y in ((a, b), (b, a)):
                if x == u and y not in seen:
                    seen.add(y)
                    dfs(y, cost + toll + fees[y], seen)
                    seen.discard(y)

    dfs(src, fees[src], {src})
    return -1 if best[0] is None else best[0]


def g_fees(r):
    n = r.randint(1, 6)
    return [n, _rand_edges(r, n, r.randint(0, 9), 1, 9), [r.randint(0, 9) for _ in range(n)], r.randrange(n), r.randrange(n)]


def v_fees(tests):
    for t in tests:
        n, roads, fees, src, dst = t["args"]
        assert 1 <= n <= 1000 and len(roads) <= 3000 and len(fees) == n and 0 <= src < n and 0 <= dst < n
        assert all(0 <= f <= 1000 for f in fees)
        for a, b, w in roads:
            assert 0 <= a < n and 0 <= b < n and 1 <= w <= 1000


CHECKS["cheapest-route-with-city-fees"] = (b_fees, g_fees, "exact")
VALIDATE["cheapest-route-with-city-fees"] = v_fees

# ---------------------------------------------------------------- second shortest route length
p = add(
    id="second-shortest-route-length", title="Second Shortest Route", diff="Medium", topic=TOPIC, tier="extra",
    fn="secondShortestRoute", params=[("n", "int"), ("roads", "int[][]")], ret="int", cmp="exact",
    desc="<p>A region has <code>n</code> towns numbered <code>0</code> to <code>n - 1</code> and <em>one-way</em> roads <code>roads[i] = [a, b, w]</code> of length <code>w</code>. A <em>route</em> from town <code>0</code> to town <code>n - 1</code> is any walk along the roads: towns and roads may be used more than once.</p><p>Let <code>L</code> be the length of the shortest route. Return the length of the shortest route whose length is <em>strictly greater</em> than <code>L</code> (routes of length exactly <code>L</code> do not count, however many there are). Return <code>-1</code> if there is no route at all or no route longer than <code>L</code>.</p><pre>n = 4\nroads = [[0,1,1], [1,3,1], [0,2,2], [2,3,2], [1,2,1]]\nshortest: 0-1-3 = 2;  next lengths: 0-1-2-3 = 4, 0-2-3 = 4\n-> 4</pre>",
    constraints=["1 &le; n &le; 1,000", "0 &le; roads.length &le; 3,000", "0 &le; a, b &lt; n", "1 &le; w &le; 100", "If n == 1, the only town is both start and end (a route of length 0 always exists)"],
    hints=["A plain shortest path only gives you the best length. What extra information per town would let you also know the second best?",
           "Keep two values for every town: the shortest and the second shortest <em>distinct</em> route length that reaches it. A route may revisit towns, so the second best can go around a cycle.",
           "Run Dijkstra on (length, town) entries. When you relax an edge with new length <code>nd</code>, update the first value if <code>nd</code> beats it (the old first value becomes a candidate for the second), otherwise update the second if <code>nd</code> is strictly between the two. Push an entry whenever either value changes."],
    editorial=["Think of each town as two states: 'reached with the best length' and 'reached with the second best distinct length'. A route to town <code>v</code> that is second best must arrive over a last road <code>u -> v</code> whose own route to <code>u</code> was either best or second best, otherwise swapping in a better prefix would give something shorter and still distinct. So it suffices to keep two lengths per town.",
               "Use a Dijkstra loop over <code>(length, town)</code>. Pop the smallest entry and skip it when it is longer than the town's second best (it is stale). For every road, compute <code>nd = length + w</code>; if <code>nd &lt; first[v]</code>, swap it into <code>first[v]</code> and carry the old first value on as <code>nd</code>; then if <code>first[v] &lt; nd &lt; second[v]</code> set <code>second[v] = nd</code>. Push the entry for each value that changed. Because lengths are positive, entries pop in non-decreasing order and each town is finalised at most twice.",
               "The answer is <code>second[n - 1]</code>, or -1 if it stays infinite. Each of the 2V states is expanded once, so the time is O((V + E) log E). For <code>n == 1</code> the first value is 0 and the second is the shortest cycle through town 0, if any."],
    time="O((V + E) log E)", space="O(V + E)",
    solution='''import heapq


def secondShortestRoute(n, roads):
    adj = [[] for _ in range(n)]
    for a, b, w in roads:
        adj[a].append((b, w))
    INF = float('inf')
    first = [INF] * n
    second = [INF] * n
    first[0] = 0
    heap = [(0, 0)]
    while heap:
        d, u = heapq.heappop(heap)
        if d > second[u]:
            continue
        for v, w in adj[u]:
            nd = d + w
            if nd < first[v]:
                first[v], nd = nd, first[v]
                heapq.heappush(heap, (first[v], v))
            if first[v] < nd < second[v]:
                second[v] = nd
                heapq.heappush(heap, (nd, v))
    return -1 if second[n - 1] == INF else second[n - 1]
''',
    tests=[[4, [[0, 1, 1], [1, 3, 1], [0, 2, 2], [2, 3, 2], [1, 2, 1]]],
           [1, []], [1, [[0, 0, 4]]], [1, [[0, 0, 4], [0, 0, 3]]], [2, []], [2, [[0, 1, 5]]], [2, [[0, 1, 5], [0, 1, 5]]],
           [2, [[0, 1, 5], [0, 1, 9]]], [2, [[0, 1, 3], [1, 0, 2]]], [3, [[0, 1, 1], [1, 2, 1], [0, 2, 2]]],
           [3, [[0, 1, 1], [1, 2, 1], [2, 1, 1]]], [4, [[0, 1, 1], [1, 2, 1], [2, 3, 1], [0, 3, 3], [3, 0, 1]]]],
)
_r = rnd(6005)
_n = 1000
_e = _rand_edges(_r, _n, 2800, 1, 100)
p["tests"].append([_n, _e])
_e = [[i, i + 1, _r.randint(1, 100)] for i in range(_n - 1)] + [[i, i + 2, 1000 // 10] for i in range(0, _n - 2, 40)]
_r.shuffle(_e)
p["tests"].append([_n, _e])
_e = [[i, i + 1, _r.randint(1, 100)] for i in range(_n - 1)]  # a single path, no cycles: no second route
_r.shuffle(_e)
p["tests"].append([_n, _e])
_e = [[i, i + 1, 1] for i in range(_n - 1)] + [[i, i + 1, 1] for i in range(0, _n - 1, 3)] + [[_n - 1, 0, 100]]
p["tests"].append([_n, _e])


def b_second(n, roads):
    # all walks up to a length bound: reach[L] = set of towns reachable with total length exactly L
    B = 36 * n + 40
    reach = [set() for _ in range(B + 1)]
    reach[0].add(0)
    for L in range(B + 1):
        for u in reach[L]:
            for a, b, w in roads:
                if a == u and L + w <= B:
                    reach[L + w].add(b)
    lens = [L for L in range(B + 1) if (n - 1) in reach[L]]
    return lens[1] if len(lens) >= 2 else -1


def g_second(r):
    n = r.randint(1, 6)
    return [n, [[r.randrange(n), r.randrange(n), r.randint(1, 5)] for _ in range(r.randint(0, 10))]]


def v_second(tests):
    for t in tests:
        n, roads = t["args"]
        assert 1 <= n <= 1000 and len(roads) <= 3000
        for a, b, w in roads:
            assert 0 <= a < n and 0 <= b < n and 1 <= w <= 100
    exp = [t["expected"] for t in tests]
    assert -1 in exp and any(e > 0 for e in exp)


CHECKS["second-shortest-route-length"] = (b_second, g_second, "exact")
VALIDATE["second-shortest-route-length"] = v_second

# ---------------------------------------------------------------- cheapest walk through a weighted grid
p = add(
    id="cheapest-walk-through-weighted-grid", title="Cheapest Walk Through a Cost Grid", diff="Medium", topic=TOPIC,
    fn="cheapestWalk", params=[("grid", "int[][]")], ret="int", cmp="exact",
    desc="<p>Every cell of the <code>m x n</code> matrix <code>grid</code> has a positive cost <code>grid[r][c]</code> that you pay each time you step <em>onto</em> the cell. You start on the top-left cell (paying its cost) and want to stand on the bottom-right cell.</p><p>From a cell you may move to any of the four side-adjacent cells (up, down, left or right), not only right and down. Return the minimum total cost of a walk from the top-left to the bottom-right cell, counting the cost of every cell on the walk including both ends.</p><pre>grid = [[1, 1, 1, 1],\n        [9, 9, 9, 1],\n        [1, 1, 1, 1],\n        [1, 9, 9, 9],\n        [1, 1, 1, 1]]\nbest walk snakes right, down, left, down, right: cost 14\n(the best walk that only goes right and down costs 16)</pre>",
    constraints=["1 &le; m, n &le; 60", "1 &le; grid[r][c] &le; 100"],
    hints=["The classic dynamic programme for 'minimum path sum' only allows moves to the right and down. Why does that break down when you may also go up and left?",
           "The grid is a graph: cells are vertices, and stepping onto a cell costs that cell's value. All costs are positive, so shortest-path algorithms apply.",
           "Run Dijkstra from the top-left cell with initial distance <code>grid[0][0]</code>. Relax each neighbour with <code>d + grid[nr][nc]</code>. Return the distance of the bottom-right cell when it is popped."],
    editorial=["With four-direction movement a cheap cell can lie 'behind' you, so the cost of a cell no longer depends only on its top and left neighbours and the simple DP table cannot be filled in one sweep. Treat the grid as a graph with up to 3,600 vertices: the weight of entering a cell is that cell's cost.",
               "Dijkstra's algorithm handles it: keep <code>dist[r][c]</code> initialised to infinity except <code>dist[0][0] = grid[0][0]</code>, pop the smallest <code>(d, r, c)</code> from a min-heap, skip stale entries, and relax the four neighbours. The first time the bottom-right cell is popped its distance is optimal because all costs are positive.",
               "Time is O(mn log(mn)) and space O(mn). For a 1 x 1 grid the answer is just the single cell's cost."],
    time="O(mn log(mn))", space="O(mn)",
    solution='''import heapq


def cheapestWalk(grid):
    m, n = len(grid), len(grid[0])
    INF = float('inf')
    dist = [[INF] * n for _ in range(m)]
    dist[0][0] = grid[0][0]
    heap = [(grid[0][0], 0, 0)]
    while heap:
        d, r, c = heapq.heappop(heap)
        if d > dist[r][c]:
            continue
        if r == m - 1 and c == n - 1:
            return d
        for nr, nc in ((r + 1, c), (r - 1, c), (r, c + 1), (r, c - 1)):
            if 0 <= nr < m and 0 <= nc < n:
                nd = d + grid[nr][nc]
                if nd < dist[nr][nc]:
                    dist[nr][nc] = nd
                    heapq.heappush(heap, (nd, nr, nc))
''',
    tests=[[[[1, 1, 1, 1], [9, 9, 9, 1], [1, 1, 1, 1], [1, 9, 9, 9], [1, 1, 1, 1]]],
           [[[7]]], [[[1, 2, 3]]], [[[4], [5], [6]]], [[[1, 3, 1], [1, 5, 1], [4, 2, 1]]], [[[100, 1], [1, 100]]],
           [[[1, 100, 1], [1, 100, 1], [1, 1, 1]]], [[[1, 100, 1, 1, 1], [1, 100, 1, 100, 1], [1, 1, 1, 100, 1]]],
           [[[5, 5, 5], [5, 5, 5], [5, 5, 5]]], [[[1, 100, 100], [1, 1, 100], [100, 1, 1]]],
           [[[1, 9, 1, 1, 1, 1], [1, 9, 1, 9, 9, 1], [1, 9, 1, 1, 9, 1], [1, 9, 9, 1, 9, 1], [1, 1, 1, 1, 9, 1]]]],
)
_r = rnd(6006)
p["tests"].append([[[_r.randint(1, 100) for _ in range(60)] for _ in range(60)]])
# a winding cheap corridor through expensive cells: rows alternate between a corridor row and a wall row with one gap
_g = [[100] * 60 for _ in range(59)]
for _i in range(0, 59, 2):
    _g[_i] = [_r.randint(1, 3) for _ in range(60)]
for _i in range(1, 59, 2):
    _g[_i][59 if (_i // 2) % 2 == 0 else 0] = _r.randint(1, 3)
_g.append([_r.randint(1, 3) for _ in range(60)])
p["tests"].append([_g])
p["tests"].append([[[_r.choice([1, 1, 1, 60, 100]) for _ in range(40)] for _ in range(60)]])


def b_walk(grid):
    m, n = len(grid), len(grid[0])
    INF = float("inf")
    d = [[INF] * n for _ in range(m)]
    d[0][0] = grid[0][0]
    ch = True
    while ch:
        ch = False
        for r in range(m):
            for c in range(n):
                for nr, nc in ((r + 1, c), (r - 1, c), (r, c + 1), (r, c - 1)):
                    if 0 <= nr < m and 0 <= nc < n and d[nr][nc] + grid[r][c] < d[r][c]:
                        d[r][c] = d[nr][nc] + grid[r][c]
                        ch = True
    return d[m - 1][n - 1]


def g_walk(r):
    m, n = r.randint(1, 5), r.randint(1, 5)
    return [[[r.randint(1, 9) for _ in range(n)] for _ in range(m)]]


def v_walk(tests):
    for t in tests:
        g = t["args"][0]
        assert 1 <= len(g) <= 60 and all(len(row) == len(g[0]) and 1 <= len(row) <= 60 for row in g)
        assert all(1 <= x <= 100 for row in g for x in row)


CHECKS["cheapest-walk-through-weighted-grid"] = (b_walk, g_walk, "exact")
VALIDATE["cheapest-walk-through-weighted-grid"] = v_walk

# ---------------------------------------------------------------- min cost number transformation
p = add(
    id="min-cost-number-transformation", title="Cheapest Number Transformation", diff="Medium", topic=TOPIC, tier="extra",
    fn="minCostTransform", params=[("start", "int"), ("target", "int"), ("limit", "int"), ("costs", "int[]")], ret="int", cmp="exact",
    desc="<p>You hold the number <code>start</code> and want to turn it into <code>target</code>. Three operations are available, with prices given by <code>costs = [add, dbl, half]</code>:</p><ul><li><code>x -> x + 1</code> costs <code>add</code>;</li><li><code>x -> 2 * x</code> costs <code>dbl</code>;</li><li><code>x -> x / 2</code>, allowed only when <code>x</code> is even, costs <code>half</code>.</li></ul><p>The number must always stay between <code>0</code> and <code>limit</code> inclusive, so an operation that would leave that range is not allowed. Return the minimum total price of a sequence of operations that turns <code>start</code> into <code>target</code>, or <code>-1</code> if it is impossible. If <code>start == target</code> the price is <code>0</code>.</p><pre>start = 3, target = 10, limit = 40, costs = [4, 3, 1]\n3 -> 4 -> 5 -> 10 costs 4 + 4 + 3 = 11\ndoubling first is dearer: 3 -> 6 -> 7 -> 8 -> 9 -> 10 costs 3 + 4*4 = 19\n-> 11</pre>",
    constraints=["0 &le; start, target &le; limit &le; 20,000", "costs.length == 3 and 1 &le; costs[i] &le; 1,000"],
    hints=["Think of every number from 0 to <code>limit</code> as a vertex, and every allowed operation as a directed edge with its price as weight.",
           "The graph is implicit: you never need to build it, only generate the (at most three) neighbours of a number when you pop it.",
           "Run Dijkstra from <code>start</code>. Neighbours of <code>x</code> are <code>x + 1</code> (if at most limit), <code>2x</code> (if at most limit) and <code>x / 2</code> (if x is even). Return the distance of <code>target</code> when it is popped, or -1 if the heap empties first."],
    editorial=["Because operations have different prices, breadth-first search (which minimises the <em>number</em> of operations) is wrong; for example a long run of cheap additions may beat one expensive doubling. The state is only the current number, so the state graph has <code>limit + 1</code> vertices and at most three outgoing edges each: this is shortest path with positive weights, the textbook use case for Dijkstra.",
               "Maintain <code>dist[x]</code> for all numbers in range, a min-heap of <code>(price, x)</code>, and expand a number by generating its neighbours. The first pop of <code>target</code> gives the minimum price. The limit also bounds how far a detour can go (for example doubling past the target and then halving back), so no extra argument is needed to stop the search.",
               "Time O(limit log limit), space O(limit). Note that doubling 0 or halving 0 just returns to 0 and never improves anything, so no special case is required. If <code>target</code> is smaller than <code>start</code> it can only be reached by halving steps, so the answer may be -1."],
    time="O(L log L) with L = limit", space="O(L)",
    solution='''import heapq


def minCostTransform(start, target, limit, costs):
    add_c, dbl_c, half_c = costs
    INF = float('inf')
    dist = [INF] * (limit + 1)
    dist[start] = 0
    heap = [(0, start)]
    while heap:
        d, x = heapq.heappop(heap)
        if d > dist[x]:
            continue
        if x == target:
            return d
        moves = []
        if x + 1 <= limit:
            moves.append((x + 1, add_c))
        if 2 * x <= limit:
            moves.append((2 * x, dbl_c))
        if x % 2 == 0:
            moves.append((x // 2, half_c))
        for y, c in moves:
            if d + c < dist[y]:
                dist[y] = d + c
                heapq.heappush(heap, (d + c, y))
    return -1
''',
    tests=[[3, 10, 40, [4, 3, 1]], [5, 5, 5, [1, 1, 1]], [0, 0, 0, [7, 7, 7]], [0, 1, 1, [3, 9, 9]], [1, 0, 1, [3, 9, 9]],
           [2, 1, 10, [1, 1, 1]], [3, 1, 10, [1, 1, 1]], [1, 16, 16, [100, 1, 1]], [1, 16, 16, [1, 100, 1]],
           [7, 20, 20, [2, 5, 1]], [7, 20, 21, [2, 5, 1]], [9, 3, 40, [10, 2, 3]], [12, 3, 12, [1, 1, 1]], [12, 3, 40, [1, 1, 1]]],
)
_r = rnd(6007)
p["tests"].append([1, 19999, 20000, [_r.randint(1, 1000) for _ in range(3)]])
p["tests"].append([17, 19000, 20000, [997, 3, 2]])
p["tests"].append([19001, 7, 20000, [5, 1, 1]])


def b_trans(start, target, limit, costs):
    INF = float("inf")
    d = [INF] * (limit + 1)
    d[start] = 0
    ch = True
    while ch:
        ch = False
        for x in range(limit + 1):
            if d[x] == INF:
                continue
            for y, c in ((x + 1, costs[0]), (2 * x, costs[1]), (x // 2 if x % 2 == 0 else -1, costs[2])):
                if 0 <= y <= limit and d[x] + c < d[y]:
                    d[y] = d[x] + c
                    ch = True
    return -1 if d[target] == INF else d[target]


def g_trans(r):
    limit = r.randint(0, 25)
    return [r.randint(0, limit), r.randint(0, limit), limit, [r.randint(1, 9) for _ in range(3)]]


def v_trans(tests):
    for t in tests:
        s, g, lim, costs = t["args"]
        assert 0 <= s <= lim and 0 <= g <= lim <= 20000 and len(costs) == 3 and all(1 <= c <= 1000 for c in costs)
    assert any(t["expected"] == -1 for t in tests)


CHECKS["min-cost-number-transformation"] = (b_trans, g_trans, "exact")
VALIDATE["min-cost-number-transformation"] = v_trans

# ---------------------------------------------------------------- lexicographically smallest shortest path
p = add(
    id="lexicographically-smallest-shortest-path", title="Lexicographically Smallest Shortest Path", diff="Medium", topic=TOPIC, tier="extra",
    fn="smallestShortestPath", params=[("n", "int"), ("roads", "int[][]")], ret="int[]", cmp="exact",
    desc="<p>A map has <code>n</code> towns numbered <code>0</code> to <code>n - 1</code> and two-way roads <code>roads[i] = [a, b, w]</code> of length <code>w</code>. Several roads may join the same pair of towns, and a road may lead from a town back to itself.</p><p>Among all routes from town <code>0</code> to town <code>n - 1</code> of minimum total length, return the one that is smallest when the routes are compared as sequences of town numbers, element by element from the start (like dictionary order on lists of numbers). Return the route as the array of towns it visits, starting with <code>0</code> and ending with <code>n - 1</code>. If the two towns are not connected, return <code>[-1]</code>. For <code>n == 1</code> the answer is <code>[0]</code>.</p><pre>n = 5\nroads = [[0,1,2], [0,2,2], [1,4,3], [2,4,3], [0,3,1], [3,4,4]]\nroutes of length 5: 0-1-4, 0-2-4, 0-3-4;  the smallest is [0, 1, 4]\n-> [0, 1, 4]</pre>",
    constraints=["1 &le; n &le; 1,000", "0 &le; roads.length &le; 3,000", "0 &le; a, b &lt; n", "1 &le; w &le; 100"],
    hints=["First find the shortest length. Only routes of exactly that length are candidates for the 'smallest sequence'.",
           "Compute the distance <code>D[v]</code> from every town to the destination <code>n - 1</code> (Dijkstra from the destination, roads are two-way). A road <code>u - v</code> lies on some shortest route from <code>u</code> exactly when <code>w + D[v] == D[u]</code>.",
           "Walk from town 0: at town <code>u</code> choose the smallest-numbered neighbour <code>v</code> with <code>w + D[v] == D[u]</code>, append it, and continue until you reach <code>n - 1</code>. Picking the smallest next town greedily is correct because all candidate routes share the same prefix so far."],
    editorial=["Run Dijkstra backwards from the destination to obtain <code>D[v]</code>, the shortest distance from each town to <code>n - 1</code>. If <code>D[0]</code> is infinite there is no route. Otherwise, a road <code>u - v</code> of length <code>w</code> can be the next step of some shortest route from <code>u</code> precisely when <code>w + D[v] = D[u]</code>; call these 'tight' roads.",
               "Every shortest route from 0 uses only tight roads, and every walk of tight roads from 0 ends in a shortest route. Because lengths are positive, <code>D</code> strictly decreases along a tight road, so the walk never revisits a town. For the dictionary-smallest route, build the answer greedily: at the current town, among tight roads take the one leading to the smallest town number (equal numbers via parallel roads are the same town). All routes still in the running share the prefix chosen so far, so the next element decides the comparison.",
               "Time O((V + E) log E) for the Dijkstra and O(V + E) for the walk. Starting the search from the destination (instead of from 0) is what makes the greedy walk possible: it tells us at every town which neighbours still lead to a shortest route."],
    time="O((V + E) log E)", space="O(V + E)",
    solution='''import heapq


def smallestShortestPath(n, roads):
    adj = [[] for _ in range(n)]
    for a, b, w in roads:
        adj[a].append((b, w))
        adj[b].append((a, w))
    INF = float('inf')
    D = [INF] * n
    D[n - 1] = 0
    heap = [(0, n - 1)]
    while heap:
        d, u = heapq.heappop(heap)
        if d > D[u]:
            continue
        for v, w in adj[u]:
            if d + w < D[v]:
                D[v] = d + w
                heapq.heappush(heap, (D[v], v))
    if D[0] == INF:
        return [-1]
    path = [0]
    u = 0
    while u != n - 1:
        nxt = min(v for v, w in adj[u] if w + D[v] == D[u])
        path.append(nxt)
        u = nxt
    return path
''',
    tests=[[5, [[0, 1, 2], [0, 2, 2], [1, 4, 3], [2, 4, 3], [0, 3, 1], [3, 4, 4]]],
           [1, []], [1, [[0, 0, 3]]], [2, []], [2, [[0, 1, 4]]], [2, [[0, 1, 4], [0, 1, 2]]], [3, [[0, 1, 1], [1, 2, 1], [0, 2, 2]]],
           [3, [[0, 2, 3], [0, 1, 1], [1, 2, 1]]], [4, [[0, 2, 1], [0, 1, 1], [2, 3, 1], [1, 3, 1]]],
           [4, [[0, 1, 1], [1, 0, 1], [1, 1, 5], [1, 3, 1], [0, 2, 1], [2, 3, 1]]],
           [6, [[0, 5, 10], [0, 1, 1], [1, 2, 1], [2, 3, 1], [3, 4, 1], [4, 5, 1], [0, 3, 3], [3, 5, 2]]],
           [4, [[0, 1, 1], [2, 3, 1]]]],
)
_r = rnd(6008)
# a 40 x 25 unit grid: an enormous number of equally short routes
_R, _C = 25, 40
_e = []
for _i in range(_R):
    for _j in range(_C):
        if _j + 1 < _C:
            _e.append([_i * _C + _j, _i * _C + _j + 1, 1])
        if _i + 1 < _R:
            _e.append([_i * _C + _j, (_i + 1) * _C + _j, 1])
_r.shuffle(_e)
p["tests"].append([_R * _C, _e])
_e = _connected_graph(_r, 1000, 2000, 1, 5)
p["tests"].append([1000, _e])
_e = _rand_edges(_r, 1000, 1200, 1, 100)
p["tests"].append([1000, _e])


def b_lex(n, roads):
    best = [None, None]

    def dfs(u, dist, path, seen):
        if u == n - 1:
            key = (dist, list(path))
            if best[0] is None or key < (best[0], best[1]):
                best[0], best[1] = key
            return
        for a, b, w in roads:
            for x, y in ((a, b), (b, a)):
                if x == u and y not in seen:
                    seen.add(y)
                    path.append(y)
                    dfs(y, dist + w, path, seen)
                    path.pop()
                    seen.discard(y)

    dfs(0, 0, [0], {0})
    return [-1] if best[0] is None else best[1]


def g_lex(r):
    n = r.randint(1, 7)
    return [n, [[r.randrange(n), r.randrange(n), r.randint(1, 3)] for _ in range(r.randint(0, 12))]]


def v_lex(tests):
    for t in tests:
        n, roads = t["args"]
        assert 1 <= n <= 1000 and len(roads) <= 3000
        for a, b, w in roads:
            assert 0 <= a < n and 0 <= b < n and 1 <= w <= 100
        e = t["expected"]
        assert e == [-1] or (e[0] == 0 and e[-1] == n - 1)


CHECKS["lexicographically-smallest-shortest-path"] = (b_lex, g_lex, "exact")
VALIDATE["lexicographically-smallest-shortest-path"] = v_lex

# ================================================================ HARD

# ---------------------------------------------------------------- minimum weight subgraph for two sources
p = add(
    id="min-weight-subgraph-for-two-sources", title="Cheapest Network Serving Two Sources", diff="Hard", topic=TOPIC,
    fn="minNetworkCost", params=[("n", "int"), ("edges", "int[][]"), ("s1", "int"), ("s2", "int"), ("t", "int")], ret="int", cmp="exact",
    desc="<p>A directed graph has <code>n</code> nodes numbered <code>0</code> to <code>n - 1</code> and edges <code>edges[i] = [from, to, cost]</code>. Several edges may join the same pair of nodes. Two source nodes <code>s1</code> and <code>s2</code> and a target node <code>t</code> are given; all three are different.</p><p>You must buy a set of edges so that <code>t</code> can be reached from <code>s1</code> <em>and</em> from <code>s2</code> using only the bought edges. An edge used by both routes is bought (and paid for) only once. Return the minimum total cost of such a set, or <code>-1</code> if <code>t</code> cannot be reached from both sources even with every edge.</p><pre>n = 6, s1 = 0, s2 = 1, t = 5\nedges = [[0,2,2], [0,5,6], [1,0,3], [1,4,5], [2,1,1], [2,3,3], [2,3,4], [3,4,2], [4,5,1]]\nbuy 0-&gt;5 (6) so that s1 = 0 reaches t, and 1-&gt;0 (3) so that s2 = 1 reaches 0 and then follows the same edge\n(6 + 3 = 9; buying 0-&gt;5 and 1-&gt;4-&gt;5 separately would cost 12) -> 9</pre>",
    constraints=["3 &le; n &le; 1,000", "0 &le; edges.length &le; 3,000", "0 &le; from, to &lt; n", "1 &le; cost &le; 1,000", "s1, s2 and t are three distinct nodes in [0, n - 1]"],
    hints=["The cheapest set of edges is always a tree-like shape: the two routes may run separately for a while and then share a common tail to <code>t</code>.",
           "Suppose the routes first meet at node <code>v</code> and share everything from <code>v</code> to <code>t</code>. The cost is then <code>dist(s1, v) + dist(s2, v) + dist(v, t)</code>, and any such choice is achievable.",
           "Compute three shortest-path arrays: from <code>s1</code> and from <code>s2</code> on the original graph, and to <code>t</code> by running Dijkstra from <code>t</code> on the <em>reversed</em> graph. The answer is the minimum over all nodes <code>v</code> of the sum of the three values (skip nodes where any value is infinite)."],
    editorial=["Take the optimal set of bought edges and follow the route of <code>s1</code> and the route of <code>s2</code> to <code>t</code>. Once the two routes meet at some node <code>v</code> they can be assumed to coincide from there on (if they are different afterwards, we could reroute one along the other without increasing the cost, since both stay inside the bought set). Before meeting, each route should be a shortest path from its source to <code>v</code>, and after meeting the common tail should be a shortest path from <code>v</code> to <code>t</code>. Paying for the shared tail only once is exactly why the sum is minimised at a meeting node.",
               "So the answer is <code>min over v of d1[v] + d2[v] + dt[v]</code> where <code>d1</code>, <code>d2</code> are shortest distances from the two sources and <code>dt[v]</code> is the shortest distance from <code>v</code> to <code>t</code>. The last one comes from one Dijkstra run from <code>t</code> over the graph with all edges reversed. Three Dijkstra runs: O((V + E) log E) in total.",
               "Overcounting is not an issue: if the separately chosen shortest paths happen to share edges before the meeting point, then the formula only overestimates that choice, and another meeting node (an earlier one) gives a value at least as small. The minimum over all <code>v</code> is therefore exact. Nodes unreachable in any of the three directions are skipped; if no node qualifies, return -1."],
    time="O((V + E) log E)", space="O(V + E)",
    solution='''import heapq


def minNetworkCost(n, edges, s1, s2, t):
    fwd = [[] for _ in range(n)]
    rev = [[] for _ in range(n)]
    for a, b, c in edges:
        fwd[a].append((b, c))
        rev[b].append((a, c))
    INF = float('inf')

    def dijkstra(adj, src):
        dist = [INF] * n
        dist[src] = 0
        heap = [(0, src)]
        while heap:
            d, u = heapq.heappop(heap)
            if d > dist[u]:
                continue
            for v, w in adj[u]:
                if d + w < dist[v]:
                    dist[v] = d + w
                    heapq.heappush(heap, (d + w, v))
        return dist

    d1 = dijkstra(fwd, s1)
    d2 = dijkstra(fwd, s2)
    dt = dijkstra(rev, t)
    best = min(d1[v] + d2[v] + dt[v] for v in range(n))
    return -1 if best == INF else best
''',
    tests=[[6, [[0, 2, 2], [0, 5, 6], [1, 0, 3], [1, 4, 5], [2, 1, 1], [2, 3, 3], [2, 3, 4], [3, 4, 2], [4, 5, 1]], 0, 1, 5],
           [3, [], 0, 1, 2], [3, [[0, 2, 4], [1, 2, 5]], 0, 1, 2], [3, [[0, 2, 4]], 0, 1, 2], [3, [[0, 1, 1], [1, 2, 1]], 0, 1, 2],
           [3, [[0, 1, 1], [1, 2, 7], [1, 2, 3], [0, 2, 20]], 0, 1, 2],
           [4, [[0, 3, 10], [1, 3, 10], [0, 2, 1], [1, 2, 1], [2, 3, 1]], 0, 1, 3],
           [4, [[0, 3, 10], [1, 3, 10], [0, 2, 5], [1, 2, 5], [2, 3, 1]], 0, 1, 3],
           [5, [[0, 2, 1], [1, 3, 1], [2, 4, 1], [3, 4, 1], [2, 3, 1]], 0, 1, 4],
           [5, [[2, 0, 1], [2, 1, 1], [0, 4, 3], [1, 4, 3], [2, 4, 5]], 0, 1, 4],
           [5, [[0, 0, 1], [0, 1, 2], [1, 1, 1], [1, 4, 1], [4, 3, 1], [3, 2, 1]], 0, 1, 2]],
)
_r = rnd(6009)
_n = 1000
p["tests"].append([_n, _rand_edges(_r, _n, 3000, 1, 1000), 0, 1, 999])
_e = [[i, i + 1, _r.randint(1, 50)] for i in range(_n - 1)] + _rand_edges(_r, _n, 1200, 1, 1000)
_r.shuffle(_e)
p["tests"].append([_n, _e, 10, 20, 900])  # t is at the end of a long chain
_e = _rand_edges(_r, _n, 2400, 1, 1000)
_e = [x for x in _e if x[1] != 5]  # nothing leads into node 5, which is the target
p["tests"].append([_n, _e, 100, 200, 5])


def b_sub(n, edges, s1, s2, t):
    m = len(edges)
    best = None
    for mask in range(1 << m):
        cost = 0
        adj = [[] for _ in range(n)]
        for i in range(m):
            if mask >> i & 1:
                a, b, c = edges[i]
                adj[a].append(b)
                cost += c
        if best is not None and cost >= best:
            continue
        ok = True
        for s in (s1, s2):
            seen = {s}
            st = [s]
            while st:
                u = st.pop()
                for v in adj[u]:
                    if v not in seen:
                        seen.add(v)
                        st.append(v)
            if t not in seen:
                ok = False
                break
        if ok:
            best = cost
    return -1 if best is None else best


def g_sub(r):
    n = r.randint(3, 6)
    a, b, c = r.sample(range(n), 3)
    return [n, [[r.randrange(n), r.randrange(n), r.randint(1, 9)] for _ in range(r.randint(0, 9))], a, b, c]


def v_sub(tests):
    for t in tests:
        n, edges, s1, s2, tt = t["args"]
        assert 3 <= n <= 1000 and len(edges) <= 3000 and len({s1, s2, tt}) == 3
        assert all(0 <= x < n for x in (s1, s2, tt))
        for a, b, c in edges:
            assert 0 <= a < n and 0 <= b < n and 1 <= c <= 1000
    assert any(t["expected"] == -1 for t in tests) and any(t["expected"] > 0 for t in tests)


CHECKS["min-weight-subgraph-for-two-sources"] = (b_sub, g_sub, "exact")
VALIDATE["min-weight-subgraph-for-two-sources"] = v_sub

# ---------------------------------------------------------------- traffic lights
p = add(
    id="earliest-arrival-with-traffic-lights", title="Earliest Arrival with Traffic Lights", diff="Hard", topic=TOPIC, tier="extra",
    fn="earliestArrival", params=[("n", "int"), ("roads", "int[][]"), ("lights", "int[][]"), ("src", "int"), ("dst", "int")], ret="int", cmp="exact",
    desc="<p>A town has <code>n</code> junctions numbered <code>0</code> to <code>n - 1</code> and two-way roads <code>roads[i] = [a, b, w]</code> that take <code>w</code> minutes to drive. Every junction <code>v</code> has a traffic light described by <code>lights[v] = [period, green]</code>: the light is green during minute <code>t</code> exactly when <code>t % period &lt; green</code> (so it is green at time 0, stays green for <code>green</code> minutes, then red for the remaining <code>period - green</code> minutes, and repeats).</p><p>You may leave a junction only while its light is green (departing at the first instant of a green minute is fine); you may wait at a junction for as long as you like. The light of the junction you arrive at does not delay your arrival there. You are at junction <code>src</code> at time 0. Return the earliest time at which you can be at junction <code>dst</code>, or <code>-1</code> if you cannot get there. If <code>src == dst</code> the answer is <code>0</code>.</p><pre>n = 3, src = 0, dst = 2\nroads = [[0,1,2], [1,2,2], [0,2,9]]\nlights = [[4,4], [5,2], [3,1]]\nleave 0 at t=0, arrive at 1 at t=2; light 1 is green only for t%5 in {0,1}, so wait until t=5 and drive: arrive at t=7\nthe direct road arrives at t=9  ->  7</pre>",
    constraints=["1 &le; n &le; 1,000", "0 &le; roads.length &le; 3,000", "0 &le; a, b &lt; n", "1 &le; w &le; 100", "lights.length == n, and for every light 1 &le; green &le; period &le; 20", "0 &le; src, dst &lt; n"],
    hints=["Time matters now: the cost of leaving a junction depends on <em>when</em> you get there. Is arriving earlier ever worse than arriving later?",
           "It is not: since you may wait, anyone who arrives earlier can imitate a later arrival. So the earliest arrival time at each junction is all you need to remember, and Dijkstra on arrival times is valid.",
           "When you pop <code>(t, u)</code>, compute your departure time: <code>t</code> if <code>t % period &lt; green</code>, otherwise the next multiple of <code>period</code>, that is <code>t + (period - t % period)</code>. Then each road gives arrival time <code>departure + w</code> at its other end."],
    editorial=["Travel times are no longer fixed weights, but the problem keeps the 'FIFO' property: leaving a junction later can never lead to arriving earlier, because the departure time is a non-decreasing function of the arrival time (wait until the next green minute). For such time-dependent graphs Dijkstra's algorithm still works if the key is the earliest arrival time and an edge's 'weight' is computed from the current time.",
               "Keep <code>best[v]</code>, the earliest known time you can be at <code>v</code>. Pop the smallest <code>(t, u)</code>; if it is stale, skip it. The earliest departure from <code>u</code> is <code>t</code> when <code>t % period &lt; green</code>, otherwise <code>t - t % period + period</code> (the next start of a green phase). For each road <code>u - v</code> of length <code>w</code> the candidate arrival at <code>v</code> is <code>departure + w</code>. Return <code>t</code> when <code>dst</code> is popped. The light at the destination never matters, and neither does the light at <code>src</code> at time 0 (it is always green then).",
               "Because every arrival is strictly later than the previous time on the route, the usual Dijkstra argument applies and each junction is finalised once. Time O((V + E) log E). The waiting time at a junction is at most <code>period - green</code> &le; 19 minutes, so all times stay small."],
    time="O((V + E) log E)", space="O(V + E)",
    solution='''import heapq


def earliestArrival(n, roads, lights, src, dst):
    adj = [[] for _ in range(n)]
    for a, b, w in roads:
        adj[a].append((b, w))
        adj[b].append((a, w))
    INF = float('inf')
    best = [INF] * n
    best[src] = 0
    heap = [(0, src)]
    while heap:
        t, u = heapq.heappop(heap)
        if t > best[u]:
            continue
        if u == dst:
            return t
        period, green = lights[u]
        r = t % period
        depart = t if r < green else t + (period - r)
        for v, w in adj[u]:
            nt = depart + w
            if nt < best[v]:
                best[v] = nt
                heapq.heappush(heap, (nt, v))
    return -1
''',
    tests=[[3, [[0, 1, 2], [1, 2, 2], [0, 2, 9]], [[4, 4], [5, 2], [3, 1]], 0, 2],
           [1, [], [[3, 1]], 0, 0], [2, [], [[3, 1], [3, 1]], 0, 1], [2, [[0, 1, 5]], [[1, 1], [1, 1]], 0, 1],
           [2, [[0, 1, 5]], [[20, 1], [20, 1]], 0, 1], [3, [[0, 1, 1], [1, 2, 1]], [[2, 1], [2, 1], [2, 1]], 0, 2],
           [3, [[0, 1, 1], [1, 2, 1]], [[3, 1], [3, 1], [3, 1]], 0, 2], [3, [[0, 1, 2], [1, 2, 2]], [[3, 1], [3, 1], [3, 1]], 0, 2],
           [4, [[0, 1, 1], [1, 3, 1], [0, 2, 4], [2, 3, 1]], [[5, 1], [5, 1], [5, 5], [5, 5]], 0, 3],
           [4, [[0, 1, 1], [1, 3, 1], [0, 2, 3], [2, 3, 1]], [[6, 1], [6, 1], [6, 6], [6, 6]], 0, 3],
           [3, [[0, 0, 1], [0, 1, 3], [0, 1, 2]], [[3, 1], [2, 1], [2, 1]], 0, 1],
           [4, [[0, 1, 1], [2, 3, 1]], [[1, 1]] * 4, 0, 3]],
)
_r = rnd(6010)
_n = 1000
_e = _connected_graph(_r, _n, 1500, 1, 100)
p["tests"].append([_n, _e, [[(pp := _r.randint(1, 20)), _r.randint(1, pp)] for _ in range(_n)], 0, _n - 1])
_e = [[i, i + 1, _r.randint(1, 30)] for i in range(_n - 1)] + _rand_edges(_r, _n, 300, 1, 100)
_r.shuffle(_e)
p["tests"].append([_n, _e, [[20, 1]] * _n, 0, _n - 1])
_e = _rand_edges(_r, _n, 1800, 1, 100)
p["tests"].append([_n, _e, [[(pp := _r.randint(5, 20)), _r.randint(1, 3)] for _ in range(_n)], 2, 997])


def b_lights(n, roads, lights, src, dst):
    T = n * (4 + 6) + 5
    H = T + 5
    arrived = [[False] * (H + 1) for _ in range(n)]
    arrived[src][0] = True
    for t in range(H + 1):
        if arrived[dst][t]:
            return t
        for v in range(n):
            if not arrived[v][t]:
                continue
            if t + 1 <= H:
                arrived[v][t + 1] = True
            if t % lights[v][0] < lights[v][1]:
                for a, b, w in roads:
                    for x, y in ((a, b), (b, a)):
                        if x == v and t + w <= H:
                            arrived[y][t + w] = True
    return -1


def g_lights(r):
    n = r.randint(1, 6)
    lights = []
    for _ in range(n):
        pp = r.randint(1, 5)
        lights.append([pp, r.randint(1, pp)])
    return [n, [[r.randrange(n), r.randrange(n), r.randint(1, 4)] for _ in range(r.randint(0, 9))], lights, r.randrange(n), r.randrange(n)]


def v_lights(tests):
    for t in tests:
        n, roads, lights, src, dst = t["args"]
        assert 1 <= n <= 1000 and len(roads) <= 3000 and len(lights) == n and 0 <= src < n and 0 <= dst < n
        assert all(1 <= g <= p_ <= 20 for p_, g in lights)
        for a, b, w in roads:
            assert 0 <= a < n and 0 <= b < n and 1 <= w <= 100
    assert any(t["expected"] == -1 for t in tests)


CHECKS["earliest-arrival-with-traffic-lights"] = (b_lights, g_lights, "exact")
VALIDATE["earliest-arrival-with-traffic-lights"] = v_lights

# ---------------------------------------------------------------- cheapest trip with a fuel tank
p = add(
    id="cheapest-trip-with-fuel-tank", title="Cheapest Trip with a Fuel Tank", diff="Hard", topic=TOPIC, tier="extra",
    fn="cheapestFuelTrip", params=[("n", "int"), ("roads", "int[][]"), ("prices", "int[]"), ("cap", "int")], ret="int", cmp="exact",
    desc="<p>A country has <code>n</code> cities numbered <code>0</code> to <code>n - 1</code> and two-way roads <code>roads[i] = [a, b, len]</code>: driving along the road uses exactly <code>len</code> units of fuel. Fuel is sold in every city <code>v</code> at <code>prices[v]</code> per unit, and you may buy any whole number of units there as long as the tank (capacity <code>cap</code> units) does not overflow. You may pass through a city without buying anything, and you may visit a city more than once.</p><p>You start in city <code>0</code> with an <em>empty</em> tank and want to reach city <code>n - 1</code>. Return the minimum total amount of money you must spend on fuel, or <code>-1</code> if the trip is impossible. If <code>n == 1</code> the answer is <code>0</code>. Fuel left in the tank at the end is wasted.</p><pre>n = 4, cap = 4, prices = [3, 1, 2, 9]\nroads = [[0,1,2], [1,2,3], [2,3,1], [0,3,6]]\nbuy 2 units in city 0 (cost 6), drive to city 1; buy 4 units there (cost 4),\ndrive to city 2 (3 units); buy nothing more: 1 unit is left, drive to city 3\n-> 10</pre>",
    constraints=["1 &le; n &le; 100", "0 &le; roads.length &le; 400", "0 &le; a, b &lt; n", "1 &le; len &le; 100", "1 &le; prices[v] &le; 100 and prices.length == n", "1 &le; cap &le; 100"],
    hints=["Knowing only the current city is not enough: the best decision depends on how much fuel you have. What should a 'state' contain?",
           "Use states <code>(city, fuel)</code> with <code>0 &le; fuel &le; cap</code>. There are at most 100 x 101 of them, and moving between them has a cost: buying one unit of fuel costs <code>prices[city]</code>, driving costs nothing in money.",
           "Run Dijkstra over these states. From <code>(v, f)</code> you can go to <code>(v, f + 1)</code> for <code>prices[v]</code> (if <code>f &lt; cap</code>), or along each road <code>(v, u, len)</code> with <code>f &ge; len</code> to <code>(u, f - len)</code> for free. The answer is the cheapest popped state with city <code>n - 1</code>."],
    editorial=["Add the fuel level to the vertex: the state graph has up to <code>n * (cap + 1)</code> = 10,100 vertices. Edges are of two kinds: 'buy one unit' from <code>(v, f)</code> to <code>(v, f + 1)</code> with weight <code>prices[v]</code>, and 'drive' from <code>(v, f)</code> to <code>(u, f - len)</code> with weight 0 when enough fuel is available. All weights are non-negative, so Dijkstra gives the minimum money spent.",
               "Buying one unit at a time loses no generality: any purchase of <code>k</code> units is <code>k</code> consecutive single-unit purchases, and the tank bound is checked at every step. Since you never gain by carrying leftover fuel except to use it later, Dijkstra will naturally prefer to fill up cheaply in cheap cities and just enough in expensive ones.",
               "The first time a state <code>(n - 1, f)</code> is popped, its cost is the answer (any fuel level is fine at the end). If the heap empties first, there is no way to arrive, for example because some required road is longer than <code>cap</code>. Time O(n * cap * (deg + 1) * log), which is about 10<sup>5</sup> heap operations here."],
    time="O(n * cap * (deg + 1) * log(n * cap))", space="O(n * cap)",
    solution='''import heapq


def cheapestFuelTrip(n, roads, prices, cap):
    adj = [[] for _ in range(n)]
    for a, b, ln in roads:
        adj[a].append((b, ln))
        adj[b].append((a, ln))
    INF = float('inf')
    dist = [[INF] * (cap + 1) for _ in range(n)]
    dist[0][0] = 0
    heap = [(0, 0, 0)]
    while heap:
        d, v, f = heapq.heappop(heap)
        if d > dist[v][f]:
            continue
        if v == n - 1:
            return d
        if f < cap and d + prices[v] < dist[v][f + 1]:
            dist[v][f + 1] = d + prices[v]
            heapq.heappush(heap, (d + prices[v], v, f + 1))
        for u, ln in adj[v]:
            if f >= ln and d < dist[u][f - ln]:
                dist[u][f - ln] = d
                heapq.heappush(heap, (d, u, f - ln))
    return -1
''',
    tests=[[4, [[0, 1, 2], [1, 2, 3], [2, 3, 1], [0, 3, 6]], [3, 1, 2, 9], 4],
           [1, [], [5], 1], [2, [], [1, 1], 5], [2, [[0, 1, 3]], [2, 7], 3], [2, [[0, 1, 4]], [2, 7], 3],
           [3, [[0, 1, 2], [1, 2, 2]], [5, 1, 1], 2], [3, [[0, 1, 2], [1, 2, 2]], [5, 1, 1], 4], [3, [[0, 1, 2], [1, 2, 2]], [1, 5, 5], 3],
           [4, [[0, 1, 1], [1, 2, 1], [2, 3, 1], [0, 3, 5]], [4, 3, 2, 1], 2],
           [4, [[0, 1, 1], [1, 2, 1], [2, 3, 1], [0, 3, 3]], [2, 9, 9, 9], 3],
           [4, [[0, 1, 3], [1, 0, 3], [1, 1, 1], [2, 3, 1]], [1, 1, 1, 1], 5],
           [5, [[0, 1, 3], [1, 4, 3], [0, 2, 2], [2, 3, 2], [3, 4, 2]], [4, 10, 1, 5, 9], 3]],
)
_r = rnd(6011)
_n = 100
_e = [[i, i + 1, _r.randint(1, 40)] for i in range(_n - 1)] + [[_r.randrange(_n), _r.randrange(_n), _r.randint(1, 100)] for _ in range(300)]
_r.shuffle(_e)
p["tests"].append([_n, _e, [_r.randint(1, 100) for _ in range(_n)], 100])
_e = [[i, i + 1, _r.randint(30, 50)] for i in range(_n - 1)] + [[_r.randrange(_n), _r.randrange(_n), _r.randint(20, 90)] for _ in range(300)]
_r.shuffle(_e)
p["tests"].append([_n, _e, [_r.randint(1, 100) for _ in range(_n)], 60])
_e = [[_r.randrange(_n), _r.randrange(_n), _r.randint(1, 100)] for _ in range(400)]
p["tests"].append([_n, _e, [_r.randint(1, 100) for _ in range(_n)], 100])


def b_fuel(n, roads, prices, cap):
    INF = float("inf")
    d = [[INF] * (cap + 1) for _ in range(n)]
    d[0][0] = 0
    ch = True
    while ch:
        ch = False
        for v in range(n):
            for f in range(cap + 1):
                if d[v][f] == INF:
                    continue
                if f < cap and d[v][f] + prices[v] < d[v][f + 1]:
                    d[v][f + 1] = d[v][f] + prices[v]
                    ch = True
                for a, b, ln in roads:
                    for x, y in ((a, b), (b, a)):
                        if x == v and f >= ln and d[v][f] < d[y][f - ln]:
                            d[y][f - ln] = d[v][f]
                            ch = True
    best = min(d[n - 1])
    return -1 if best == INF else best


def g_fuel(r):
    n = r.randint(1, 5)
    cap = r.randint(1, 6)
    return [n, [[r.randrange(n), r.randrange(n), r.randint(1, cap + 1)] for _ in range(r.randint(0, 8))], [r.randint(1, 6) for _ in range(n)], cap]


def v_fuel(tests):
    for t in tests:
        n, roads, prices, cap = t["args"]
        assert 1 <= n <= 100 and len(roads) <= 400 and len(prices) == n and 1 <= cap <= 100
        assert all(1 <= x <= 100 for x in prices)
        for a, b, ln in roads:
            assert 0 <= a < n and 0 <= b < n and 1 <= ln <= 100
    assert any(t["expected"] == -1 for t in tests)


CHECKS["cheapest-trip-with-fuel-tank"] = (b_fuel, g_fuel, "exact")
VALIDATE["cheapest-trip-with-fuel-tank"] = v_fuel
