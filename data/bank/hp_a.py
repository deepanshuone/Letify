"""Problems: heap, top-k family (k largest / smallest / closest / frequent, kth in streams). See data/lib.py for the registry."""
import heapq  # noqa: F401

from lib import add, rnd, CHECKS, VALIDATE, gen_arr  # noqa: F401

INT_MIN, INT_MAX = -(2 ** 31), 2 ** 31 - 1
T = "Heap"


# ================================================================ EASY

# ---------------------------------------------------------------- k weakest rows
p = add(
    id="k-weakest-rows", title="K Weakest Rows", diff="Easy", topic=T, tier="extra",
    fn="kWeakestRows", params=[("mat", "int[][]"), ("k", "int")], ret="int[]", cmp="exact",
    desc="<p>The grid <code>mat</code> describes the squads of an army. Every row is one squad; a <code>1</code> is a soldier and a <code>0</code> is a civilian, and soldiers and civilians may stand in any order inside a row.</p><p>Squad <code>i</code> is <em>weaker</em> than squad <code>j</code> if it has fewer soldiers, or if both have the same number of soldiers and <code>i &lt; j</code>. Return the indices of the <code>k</code> weakest squads, listed from the weakest to the strongest.</p><pre>mat = [[1,1,0,0,0],\n       [1,1,1,1,0],\n       [1,0,0,0,0],\n       [1,1,0,0,0],\n       [1,1,1,1,1]],  k = 3\n\nsoldiers per row: 2, 4, 1, 2, 5\nweakest first: row 2, row 0, row 3, row 1, row 4\nanswer = [2, 0, 3]</pre>",
    constraints=["1 &le; mat.length, mat[i].length &le; 100", "mat[i][j] is 0 or 1", "1 &le; k &le; mat.length"],
    hints=["Reduce every row to one number first: how many soldiers it holds.",
           "Sorting all rows by (soldiers, index) and taking the first k works. You only need the k weakest, though, so a full sort is more than necessary.",
           "Keep a max-heap of size k keyed by (soldiers, index). When it grows past k, pop the strongest of the kept rows. At the end sort the k survivors."],
    editorial=["Each row has a key <code>(soldier count, row index)</code>. Two rows never have equal keys because the index differs, so the order is total and the answer is unique.",
               "Scan the rows once while keeping a max-heap of at most k keys (in Python, negate the key). After pushing a row, if the heap has more than k entries, remove the largest key, which is the strongest row among those kept. When the scan ends the heap holds exactly the k weakest rows; sort them and print the indices.",
               "Counting soldiers costs O(m n). The heap work is O(m log k), plus O(k log k) for the final sort. Sorting all m rows costs O(m log m) instead, which is also fine for these limits; the heap pays off when k is much smaller than m."],
    time="O(m n + m log k)", space="O(k)",
    solution='''import heapq


def kWeakestRows(mat, k):
    heap = []
    for i, row in enumerate(mat):
        heapq.heappush(heap, (-sum(row), -i))
        if len(heap) > k:
            heapq.heappop(heap)
    heap.sort(reverse=True)
    return [-i for _, i in heap]
''',
    tests=[[[[1, 1, 0, 0, 0], [1, 1, 1, 1, 0], [1, 0, 0, 0, 0], [1, 1, 0, 0, 0], [1, 1, 1, 1, 1]], 3],
           [[[1, 0, 0, 0], [1, 1, 1, 1], [1, 0, 0, 0], [1, 0, 0, 0]], 2],
           [[[0, 1, 0, 1], [1, 1, 0, 0], [0, 0, 0, 0]], 3],
           [[[1]], 1], [[[0]], 1], [[[0], [0], [0], [0]], 2], [[[1, 1], [1, 1], [1, 1]], 3],
           [[[1, 0, 1], [0, 0, 0], [1, 1, 1], [0, 1, 0]], 1], [[[1, 1, 1, 1, 1]], 1],
           [[[0, 1, 1], [1, 0, 0], [1, 1, 0], [0, 0, 1]], 4]],
)
_r = rnd(9101)
p["tests"].append([[[_r.randint(0, 1) for _ in range(100)] for _ in range(100)], 25])
p["tests"].append([[[1 if _r.random() < 0.5 else 0 for _ in range(60)] for _ in range(100)], 100])
p["tests"].append([[[1 if j < _r.randint(0, 3) else 0 for j in range(100)] for _ in range(100)], 1])


def b_weak(mat, k):
    left = list(range(len(mat)))
    out = []
    while len(out) < k:
        best = left[0]
        for i in left:
            if (sum(mat[i]), i) < (sum(mat[best]), best):
                best = i
        out.append(best)
        left.remove(best)
    return out


def g_weak(r):
    m, n = r.randint(1, 7), r.randint(1, 5)
    return [[[r.randint(0, 1) for _ in range(n)] for _ in range(m)], r.randint(1, m)]


def v_weak(tests):
    for t in tests:
        mat, k = t["args"]
        assert 1 <= len(mat) <= 100 and 1 <= k <= len(mat)
        assert all(1 <= len(row) <= 100 and set(row) <= {0, 1} for row in mat)
        assert len(t["expected"]) == k and len(set(t["expected"])) == k


CHECKS["k-weakest-rows"] = (b_weak, g_weak, "exact")
VALIDATE["k-weakest-rows"] = v_weak

# ---------------------------------------------------------------- k strongest values from the median
p = add(
    id="k-strongest-values-from-median", title="K Strongest Values Around the Median", diff="Easy", topic=T, tier="extra",
    fn="strongestValues", params=[("nums", "int[]"), ("k", "int")], ret="int[]", cmp="exact",
    desc="<p>Let <code>m</code> be the <em>median</em> of <code>nums</code>: sort a copy of the array and take the element at position <code>(n - 1) / 2</code> (integer division, positions start at 0), so for an even length it is the lower of the two middle values.</p><p>A value <code>a</code> is <em>stronger</em> than a value <code>b</code> if <code>|a - m| &gt; |b - m|</code>, or if both distances are equal and <code>a &gt; b</code>. Return the <code>k</code> strongest elements of <code>nums</code> (equal values may repeat), strongest first.</p><pre>nums = [6, 7, 11, 7, 6, 8], k = 5\nsorted: 6 6 7 7 8 11  ->  m = 7\ndistances: 11 -> 4, 8 -> 1, 6 -> 1, 6 -> 1, 7 -> 0, 7 -> 0\nanswer = [11, 8, 6, 6, 7]</pre><p>Here 8 beats 6 because both are at distance 1 from the median and 8 is larger.</p>",
    constraints=["1 &le; nums.length &le; 5,000", "-10<sup>9</sup> &le; nums[i] &le; 10<sup>9</sup>", "1 &le; k &le; nums.length"],
    hints=["First find the median exactly as defined, then forget about the original positions: only strength matters.",
           "Strength is the pair (distance from m, value). Compare pairs lexicographically; the answer is the k largest pairs in descending order.",
           "Use a min-heap of size k keyed by strength so the weakest kept element sits at the root; replace the root whenever a stronger element arrives."],
    editorial=["Sort a copy once to read the median. Then every element gets the key <code>(|x - m|, x)</code>; the problem asks for the k elements with the largest keys, in descending key order. Equal values have equal keys, so the output is fully determined.",
               "Keep a min-heap with at most k keys. Push each key and pop the smallest when the size exceeds k. At the end, sort the survivors in descending order. This costs O(n log k) after the O(n log n) sort that finds the median.",
               "A common slip is to take the median as the average of the two middle values or as the upper middle value; this problem defines it as the lower one, so the median is always an element of the array."],
    time="O(n log n)", space="O(k)",
    solution='''import heapq


def strongestValues(nums, k):
    m = sorted(nums)[(len(nums) - 1) // 2]
    heap = []
    for x in nums:
        heapq.heappush(heap, (abs(x - m), x))
        if len(heap) > k:
            heapq.heappop(heap)
    heap.sort(reverse=True)
    return [x for _, x in heap]
''',
    tests=[[[6, 7, 11, 7, 6, 8], 5], [[1, 2, 3, 4, 5], 2], [[1, 1, 3, 5, 5], 2], [[5], 1], [[4, 4], 2],
           [[1, 1000000000, -1000000000, 0], 2], [[-5, -5, -5], 3], [[10, 1], 1], [[3, 1, 2, 2, 3, 3], 4],
           [[9, 8, 7, 6, 5, 4, 3, 2, 1], 9]],
)
_r = rnd(9102)
p["tests"].append([[_r.randint(-10 ** 9, 10 ** 9) for _ in range(5000)], 700])
p["tests"].append([[_r.randint(-20, 20) for _ in range(5000)], 2500])
p["tests"].append([[_r.randint(-10 ** 9, 10 ** 9) for _ in range(3000)], 1])


def b_strong(nums, k):
    m = sorted(nums)[(len(nums) - 1) // 2]

    def stronger(a, b):
        return abs(a - m) > abs(b - m) or (abs(a - m) == abs(b - m) and a > b)

    left = list(nums)
    out = []
    for _ in range(k):
        best = left[0]
        for x in left:
            if stronger(x, best):
                best = x
        out.append(best)
        left.remove(best)
    return out


def g_strong(r):
    n = r.randint(1, 9)
    return [[r.randint(-6, 6) for _ in range(n)], r.randint(1, n)]


def v_strong(tests):
    for t in tests:
        nums, k = t["args"]
        assert 1 <= len(nums) <= 5000 and 1 <= k <= len(nums)
        assert all(-10 ** 9 <= x <= 10 ** 9 for x in nums)
        assert len(t["expected"]) == k


CHECKS["k-strongest-values-from-median"] = (b_strong, g_strong, "exact")
VALIDATE["k-strongest-values-from-median"] = v_strong

# ---------------------------------------------------------------- running top-k sum
p = add(
    id="running-top-k-sum", title="Running Sum of the K Best Scores", diff="Easy", topic=T,
    fn="runningTopKSum", params=[("scores", "int[]"), ("k", "int")], ret="int[]", cmp="exact",
    desc="<p>Contest scores arrive one at a time and are stored in the array <code>scores</code>. After each arrival, the organisers publish the total of the <code>k</code> highest scores received so far; while fewer than <code>k</code> scores have arrived, the total of all of them is published instead.</p><p>Return the array whose <code>i</code>-th element is the published total after the first <code>i + 1</code> scores. Scores can be negative.</p><pre>scores = [5, 1, 4, 2, 8], k = 2\nafter 5 : 5\nafter 1 : 5 + 1 = 6\nafter 4 : 5 + 4 = 9\nafter 2 : 5 + 4 = 9\nafter 8 : 8 + 5 = 13\nanswer = [5, 6, 9, 9, 13]</pre>",
    constraints=["1 &le; scores.length &le; 5,000", "-100,000 &le; scores[i] &le; 100,000", "1 &le; k &le; scores.length"],
    hints=["Recomputing the best k from scratch after every score works but is slow. What changes when one new score arrives?",
           "You only ever need the current top k scores and their sum. A newcomer either enters that group or it does not.",
           "Keep a min-heap holding the current top k and a running sum. Push the new score and add it to the sum; if the heap now holds more than k scores, pop the smallest and subtract it."],
    editorial=["The set of the k largest scores changes by at most one element per arrival: the new score joins it (and the previous k-th largest drops out) or the new score is not good enough and the group is unchanged. A min-heap of size k represents the group, with its smallest member at the root, which is exactly the one that is evicted.",
               "Maintain <code>total</code> as the sum of the heap. For each score, push it and add it to the total; if the heap size exceeds k, pop the minimum and subtract it from the total. Record the total. While the heap has fewer than k members, nothing is ever popped, so the total is the sum of everything seen, as the statement requires (negative scores included).",
               "Each score costs one push and at most one pop, so the whole run is O(n log k) time with O(k) memory."],
    time="O(n log k)", space="O(k)",
    solution='''import heapq


def runningTopKSum(scores, k):
    heap = []
    total = 0
    out = []
    for x in scores:
        heapq.heappush(heap, x)
        total += x
        if len(heap) > k:
            total -= heapq.heappop(heap)
        out.append(total)
    return out
''',
    tests=[[[5, 1, 4, 2, 8], 2], [[3, 3, 3], 1], [[-4, -2, -9, -1], 2], [[7], 1], [[1, 2, 3, 4, 5], 5],
           [[5, 4, 3, 2, 1], 3], [[100000, -100000, 100000, -100000], 2], [[0, 0, 0, 0], 2],
           [[-1, 5, -3, 5, -3, 5], 4], [[2, 9], 1]],
)
_r = rnd(9103)
p["tests"].append([[_r.randint(-100000, 100000) for _ in range(2500)], 37])
p["tests"].append([[_r.randint(-100000, 100000) for _ in range(2200)], 1200])
p["tests"].append([[i * 20 - 40000 for i in range(2000)], 1000])


def b_runtop(scores, k):
    return [sum(sorted(scores[:i + 1], reverse=True)[:k]) for i in range(len(scores))]


def g_runtop(r):
    n = r.randint(1, 9)
    return [[r.randint(-8, 8) for _ in range(n)], r.randint(1, n)]


def v_runtop(tests):
    for t in tests:
        s, k = t["args"]
        assert 1 <= len(s) <= 5000 and 1 <= k <= len(s)
        assert all(-100000 <= x <= 100000 for x in s)
        assert len(t["expected"]) == len(s)


CHECKS["running-top-k-sum"] = (b_runtop, g_runtop, "exact")
VALIDATE["running-top-k-sum"] = v_runtop

# ================================================================ MEDIUM

# ---------------------------------------------------------------- leaderboard
p = add(
    id="top-k-leaderboard-ops", title="Leaderboard Top-K Totals", diff="Medium", topic=T,
    fn="leaderboardQueries", params=[("ops", "int[][]")], ret="int[]", cmp="exact",
    desc="<p>A game keeps a leaderboard of players identified by integers. It starts empty, and <code>ops</code> lists the operations in order. Each operation is a triple <code>[type, a, b]</code>:</p><ul><li><code>[1, id, points]</code>: add <code>points</code> to the score of player <code>id</code>. A player who is not on the board yet enters it with that score.</li><li><code>[2, id, 0]</code>: remove player <code>id</code> from the board. If the player is not on the board nothing happens. The player may enter again later and then starts from zero.</li><li><code>[3, k, 0]</code>: query. Report the sum of the <code>k</code> highest scores currently on the board; if fewer than <code>k</code> players are on the board, report the sum of all their scores (an empty board gives 0).</li></ul><p>Return the answers to all queries, in order.</p><pre>ops = [[1,0,50], [1,1,30], [1,0,10], [3,2,0], [2,0,0], [3,2,0]]\nboard after 3 ops: player 0 -> 60, player 1 -> 30\nquery k=2 -> 90\nremove player 0\nquery k=2 -> 30   (only one player left)\nanswer = [90, 30]</pre>",
    constraints=["1 &le; ops.length &le; 2,000, and at least one operation is a query", "0 &le; id &le; 999", "1 &le; points &le; 10,000", "1 &le; k &le; 1,000"],
    hints=["Store the scores in a hash map from player id to score; updates and removals are then trivial. The interesting part is a query.",
           "A query asks for the k largest values among the current scores. You do not need to sort all of them.",
           "For each query scan the scores with a min-heap of size k (or call a library <code>nlargest</code>) and sum the heap. That is O(P log k) per query for P players."],
    editorial=["Updates and removals are O(1) with a dictionary. For queries, the k largest values among P current scores can be selected with a min-heap of size k: push every score and pop the smallest whenever the heap exceeds k. The sum of the heap is the answer. This is O(P log k), which is much cheaper than sorting when k is small, and it works unchanged when k exceeds the number of players.",
               "With at most 2,000 operations and 1,000 players the direct approach is comfortably fast. If queries were far more frequent than updates you could keep the scores in a balanced structure (an order-statistic tree or a Fenwick tree over score ranks) to answer queries in O(log) or O(k), but for interviews the heap-per-query solution is the expected one.",
               "Pitfalls: removal must delete the player entirely (a later addition starts from zero, not from the old score), and a query with k larger than the board size must just add everything."],
    time="O(q P log k)", space="O(P)",
    solution='''import heapq


def leaderboardQueries(ops):
    score = {}
    out = []
    for t, a, b in ops:
        if t == 1:
            score[a] = score.get(a, 0) + b
        elif t == 2:
            score.pop(a, None)
        else:
            out.append(sum(heapq.nlargest(a, score.values())))
    return out
''',
    tests=[[[[1, 0, 50], [1, 1, 30], [1, 0, 10], [3, 2, 0], [2, 0, 0], [3, 2, 0]]],
           [[[3, 5, 0]]], [[[1, 7, 10], [3, 1, 0], [3, 3, 0]]],
           [[[1, 1, 5], [1, 2, 6], [1, 3, 7], [3, 1, 0], [3, 2, 0], [3, 3, 0], [3, 4, 0]]],
           [[[1, 1, 5], [2, 1, 0], [1, 1, 3], [3, 1, 0]]], [[[2, 9, 0], [1, 9, 4], [3, 1, 0]]],
           [[[1, 0, 1], [1, 1, 1], [1, 2, 1], [3, 2, 0], [1, 1, 5], [3, 2, 0], [2, 1, 0], [3, 2, 0]]],
           [[[1, 999, 10000], [1, 0, 10000], [3, 1000, 0], [2, 999, 0], [2, 0, 0], [3, 1, 0]]],
           [[[1, 4, 9], [1, 4, 9], [2, 4, 0], [2, 4, 0], [3, 1, 0]]]],
)


def _lb_ops(r, nops, players, maxadd, kmax, pq=0.25, prm=0.12):
    ops = []
    for _ in range(nops - 1):
        x = r.random()
        if x < pq:
            ops.append([3, r.randint(1, kmax), 0])
        elif x < pq + prm:
            ops.append([2, r.randrange(players), 0])
        else:
            ops.append([1, r.randrange(players), r.randint(1, maxadd)])
    ops.append([3, r.randint(1, kmax), 0])
    return ops


_r = rnd(9104)
p["tests"].append([_lb_ops(_r, 2000, 1000, 10000, 1000, pq=0.3)])
p["tests"].append([_lb_ops(_r, 2000, 300, 10000, 20, pq=0.3, prm=0.05)])
p["tests"].append([_lb_ops(_r, 1500, 40, 100, 1000, pq=0.4, prm=0.2)])


def b_lb(ops):
    board = {}
    out = []
    for t, a, b in ops:
        if t == 1:
            board[a] = board.get(a, 0) + b
        elif t == 2:
            if a in board:
                del board[a]
        else:
            vals = sorted(board.values(), reverse=True)
            out.append(sum(vals[:a]))
    return out


def g_lb(r):
    return [_lb_ops(r, r.randint(1, 14), r.randint(1, 4), 9, 5)]


def v_lb(tests):
    for t in tests:
        ops = t["args"][0]
        assert 1 <= len(ops) <= 2000 and any(o[0] == 3 for o in ops)
        for ty, a, b in ops:
            assert ty in (1, 2, 3)
            if ty == 1:
                assert 0 <= a <= 999 and 1 <= b <= 10000
            elif ty == 2:
                assert 0 <= a <= 999 and b == 0
            else:
                assert 1 <= a <= 1000 and b == 0
        assert len(t["expected"]) == sum(1 for o in ops if o[0] == 3)


CHECKS["top-k-leaderboard-ops"] = (b_lb, g_lb, "exact")
VALIDATE["top-k-leaderboard-ops"] = v_lb

# ---------------------------------------------------------------- stock price with corrections
p = add(
    id="stock-price-corrections", title="Stock Price With Corrections", diff="Medium", topic=T,
    fn="stockQueries", params=[("ops", "int[][]")], ret="int[]", cmp="exact",
    desc="<p>A ticker receives price records out of order and sometimes corrects an earlier record. <code>ops</code> is a list of triples <code>[type, a, b]</code>:</p><ul><li><code>[1, t, price]</code>: record that the price at timestamp <code>t</code> is <code>price</code>. If timestamp <code>t</code> was recorded before, this <strong>replaces</strong> the old price (a correction).</li><li><code>[2, 0, 0]</code>: report the price at the <strong>latest</strong> timestamp recorded so far.</li><li><code>[3, 0, 0]</code>: report the <strong>maximum</strong> of the current prices over all timestamps.</li><li><code>[4, 0, 0]</code>: report the <strong>minimum</strong> of the current prices over all timestamps.</li></ul><p>The first operation is always a record. Return the answers to all queries (types 2, 3 and 4) in order.</p><pre>ops = [[1,1,10], [1,2,5], [3,0,0], [4,0,0], [1,1,3], [3,0,0], [4,0,0], [2,0,0], [1,4,2], [2,0,0], [4,0,0]]\nprices: t1=10, t2=5  -> max 10, min 5\ncorrect t1 to 3      -> max 5, min 3, latest (t2) 5\nrecord t4=2          -> latest 2, min 2\nanswer = [10, 5, 5, 3, 5, 2, 2]</pre>",
    constraints=["1 &le; ops.length &le; 5,000; ops[0] is a record", "1 &le; t, price &le; 10<sup>9</sup>", "Every query is preceded by at least one record"],
    hints=["A hash map from timestamp to its current price handles records, corrections and the latest-timestamp query. The max and min queries are the hard ones.",
           "A heap can give the max or min quickly, but a correction changes a price that is already inside the heap, and you cannot easily delete from the middle of one.",
           "Do not delete. On every record push <code>(price, t)</code> into a max-heap and a min-heap. When a query looks at the top, discard it while its price differs from the current price of that timestamp (it is stale), then read the top."],
    editorial=["Keep <code>price[t]</code> (the current value) and the largest timestamp seen. The latest price is just <code>price[latest]</code>.",
               "For max and min use two heaps with <em>lazy deletion</em>. Every record pushes an entry <code>(price, t)</code> into both heaps. A correction does not remove the old entry; instead, when a query inspects the top of a heap, it checks whether the entry still matches <code>price[t]</code>. If not, the entry is stale and is popped; this repeats until the top is current. The top is then the true extreme. If a stale entry happens to equal the current price again (the value was corrected back), it is simply valid, which is harmless.",
               "Each entry is pushed once and popped at most once, so all operations cost O(log n) amortised and the total is O(n log n). The lazy-deletion pattern is the standard answer whenever a heap must support updates or deletions of arbitrary elements."],
    time="O(n log n)", space="O(n)",
    solution='''import heapq


def stockQueries(ops):
    price = {}
    hi, lo = [], []
    latest = 0
    out = []
    for t, a, b in ops:
        if t == 1:
            price[a] = b
            if a > latest:
                latest = a
            heapq.heappush(hi, (-b, a))
            heapq.heappush(lo, (b, a))
        elif t == 2:
            out.append(price[latest])
        elif t == 3:
            while price[hi[0][1]] != -hi[0][0]:
                heapq.heappop(hi)
            out.append(-hi[0][0])
        else:
            while price[lo[0][1]] != lo[0][0]:
                heapq.heappop(lo)
            out.append(lo[0][0])
    return out
''',
    tests=[[[[1, 1, 10], [1, 2, 5], [3, 0, 0], [4, 0, 0], [1, 1, 3], [3, 0, 0], [4, 0, 0], [2, 0, 0], [1, 4, 2], [2, 0, 0], [4, 0, 0]]],
           [[[1, 5, 7], [2, 0, 0], [3, 0, 0], [4, 0, 0]]],
           [[[1, 3, 4], [1, 1, 9], [2, 0, 0], [1, 3, 1], [2, 0, 0], [3, 0, 0], [4, 0, 0]]],
           [[[1, 1, 5], [1, 1, 6], [1, 1, 5], [3, 0, 0], [4, 0, 0]]],
           [[[1, 10, 100], [1, 20, 200], [1, 30, 300], [1, 30, 50], [3, 0, 0], [2, 0, 0], [4, 0, 0], [1, 30, 400], [3, 0, 0]]],
           [[[1, 1000000000, 1000000000], [1, 1, 1], [3, 0, 0], [4, 0, 0], [2, 0, 0], [1, 1000000000, 1], [3, 0, 0], [2, 0, 0]]],
           [[[1, 2, 8], [1, 2, 9], [1, 2, 7], [1, 3, 7], [4, 0, 0], [1, 3, 20], [4, 0, 0], [3, 0, 0]]],
           [[[1, 4, 3], [1, 3, 8], [2, 0, 0], [1, 4, 8], [4, 0, 0], [1, 3, 2], [3, 0, 0], [2, 0, 0]]]],
)


def _st_ops(r, nops, tmax, pmax, pq=0.4):
    ops = [[1, r.randint(1, tmax), r.randint(1, pmax)]]
    for _ in range(nops - 1):
        if r.random() < pq:
            ops.append([r.choice((2, 3, 4)), 0, 0])
        else:
            ops.append([1, r.randint(1, tmax), r.randint(1, pmax)])
    return ops


_r = rnd(9105)
p["tests"].append([_st_ops(_r, 3000, 900, 100000)])
p["tests"].append([_st_ops(_r, 3000, 40, 100000, pq=0.5)])
_big = [[1, i, 1000 + i] for i in range(1, 801)] + [[1, i, 5 + (i % 7)] for i in range(1, 801)] + [[3, 0, 0], [4, 0, 0], [2, 0, 0]] * 300
p["tests"].append([_big])


def b_stock(ops):
    cur = {}
    out = []
    for t, a, b in ops:
        if t == 1:
            cur[a] = b
        elif t == 2:
            out.append(cur[max(cur)])
        elif t == 3:
            out.append(max(cur.values()))
        else:
            out.append(min(cur.values()))
    return out


def g_stock(r):
    return [_st_ops(r, r.randint(1, 16), r.randint(1, 5), 9)]


def v_stock(tests):
    for t in tests:
        ops = t["args"][0]
        assert 1 <= len(ops) <= 5000 and ops[0][0] == 1
        for ty, a, b in ops:
            assert ty in (1, 2, 3, 4)
            if ty == 1:
                assert 1 <= a <= 10 ** 9 and 1 <= b <= 10 ** 9
            else:
                assert a == 0 and b == 0
        assert len(t["expected"]) == sum(1 for o in ops if o[0] != 1)


CHECKS["stock-price-corrections"] = (b_stock, g_stock, "exact")
VALIDATE["stock-price-corrections"] = v_stock

# ---------------------------------------------------------------- k-th nearest point per query
p = add(
    id="kth-nearest-point-per-query", title="K-th Nearest Point for Each Query", diff="Medium", topic=T, tier="extra",
    fn="kthNearest", params=[("points", "int[][]"), ("queries", "int[][]")], ret="int[]", cmp="exact",
    desc="<p><code>points[i] = [x, y]</code> are the positions of shops on a plane. Each query is a triple <code>[qx, qy, k]</code>: standing at <code>(qx, qy)</code>, find the shop that is the <code>k</code>-th nearest by straight-line distance, and report its <strong>index</strong> in <code>points</code>.</p><p>Shops at the same distance are ordered by their index (the smaller index is nearer). So the order of shops for a query is by (squared distance, index), and the answer is the k-th shop in this order. Return one index per query.</p><pre>points  = [[0,0], [2,0], [0,3], [-1,0]]\nqueries = [[0,0,1], [0,0,2], [0,0,4], [2,1,3]]\n\nfrom (0,0): squared distances 0, 4, 9, 1  -> order: 0, 3, 1, 2\nfrom (2,1): squared distances 5, 1, 8, 10 -> order: 1, 0, 2, 3\nanswer = [0, 3, 2, 2]</pre>",
    constraints=["1 &le; points.length &le; 600", "1 &le; queries.length &le; 200", "-1,000 &le; x, y, qx, qy &le; 1,000", "1 &le; k &le; points.length"],
    hints=["Compare squared distances so that everything stays an integer. For a single query, sorting the shops by (distance, index) and reading position k-1 already works.",
           "You only need the k-th element, not the whole order. Think about which k shops you must remember while scanning.",
           "Scan the shops while keeping a max-heap of the k nearest so far, keyed by (squared distance, index). The root is the farthest of those k, so after the scan the root is exactly the k-th nearest."],
    editorial=["For one query, define the key <code>(dx*dx + dy*dy, index)</code>; keys are distinct, so the k-th smallest key identifies a single shop.",
               "Scan the shops and maintain a max-heap (store negated keys in Python) containing the k smallest keys seen. While it has fewer than k keys, push. Afterwards, if the new key is smaller than the root, replace the root. When the scan ends, the root is the largest of the k smallest keys, i.e. the k-th smallest, and its second component is the answer.",
               "Each query costs O(n log k), so the whole solution is O(q n log k) time and O(k) extra space. This is the same idea as K Closest Points, but the answer is the boundary element of the kept set rather than the set itself."],
    time="O(q n log k)", space="O(k)",
    solution='''import heapq


def kthNearest(points, queries):
    out = []
    for qx, qy, k in queries:
        heap = []
        for i, (x, y) in enumerate(points):
            key = (-((x - qx) ** 2 + (y - qy) ** 2), -i)
            if len(heap) < k:
                heapq.heappush(heap, key)
            elif key > heap[0]:
                heapq.heapreplace(heap, key)
        out.append(-heap[0][1])
    return out
''',
    tests=[[[[0, 0], [2, 0], [0, 3], [-1, 0]], [[0, 0, 1], [0, 0, 2], [0, 0, 4], [2, 1, 3]]],
           [[[5, 5]], [[0, 0, 1], [5, 5, 1]]],
           [[[1, 1], [1, 1], [1, 1]], [[0, 0, 1], [0, 0, 2], [0, 0, 3]]],
           [[[0, 0], [10, 0], [0, 10], [-10, 0], [0, -10]], [[0, 0, 3], [10, 10, 2], [-10, -10, 5]]],
           [[[1000, 1000], [-1000, -1000], [1000, -1000], [-1000, 1000]], [[0, 0, 1], [0, 0, 4], [1000, 1000, 2]]],
           [[[3, 4], [4, 3], [-3, -4], [-4, -3], [0, 5], [5, 0]], [[0, 0, 1], [0, 0, 6], [0, 0, 3], [1, 1, 2]]],
           [[[2, 2], [2, 2]], [[2, 2, 2], [3, 3, 1]]],
           [[[0, 0], [1, 0], [2, 0], [3, 0], [4, 0]], [[4, 0, 1], [4, 0, 5], [2, 0, 2], [2, 0, 3]]]],
)
_r = rnd(9106)
p["tests"].append([[[_r.randint(-1000, 1000), _r.randint(-1000, 1000)] for _ in range(600)],
                   [[_r.randint(-1000, 1000), _r.randint(-1000, 1000), _r.randint(1, 600)] for _ in range(200)]])
p["tests"].append([[[_r.randint(-8, 8), _r.randint(-8, 8)] for _ in range(600)],
                   [[_r.randint(-8, 8), _r.randint(-8, 8), _r.randint(1, 30)] for _ in range(200)]])
p["tests"].append([[[_r.randint(-1000, 1000), _r.randint(-1000, 1000)] for _ in range(500)],
                   [[_r.randint(-1000, 1000), _r.randint(-1000, 1000), _r.choice([1, 2, 500, 499])] for _ in range(150)]])


def b_kth(points, queries):
    out = []
    for qx, qy, k in queries:
        order = sorted(range(len(points)), key=lambda i: ((points[i][0] - qx) ** 2 + (points[i][1] - qy) ** 2, i))
        out.append(order[k - 1])
    return out


def g_kth(r):
    n = r.randint(1, 8)
    pts = [[r.randint(-4, 4), r.randint(-4, 4)] for _ in range(n)]
    qs = [[r.randint(-4, 4), r.randint(-4, 4), r.randint(1, n)] for _ in range(r.randint(1, 4))]
    return [pts, qs]


def v_kth(tests):
    for t in tests:
        pts, qs = t["args"]
        assert 1 <= len(pts) <= 600 and 1 <= len(qs) <= 200
        assert all(len(q) == 2 and -1000 <= q[0] <= 1000 and -1000 <= q[1] <= 1000 for q in pts)
        assert all(len(q) == 3 and -1000 <= q[0] <= 1000 and -1000 <= q[1] <= 1000 and 1 <= q[2] <= len(pts) for q in qs)
        assert len(t["expected"]) == len(qs)


CHECKS["kth-nearest-point-per-query"] = (b_kth, g_kth, "exact")
VALIDATE["kth-nearest-point-per-query"] = v_kth

# ---------------------------------------------------------------- k largest subarray sums
p = add(
    id="k-largest-subarray-sums", title="K Largest Subarray Sums", diff="Medium", topic=T, tier="extra",
    fn="kLargestSubarraySums", params=[("nums", "int[]"), ("k", "int")], ret="int[]", cmp="exact",
    desc="<p>Consider the sums of all non-empty contiguous subarrays of <code>nums</code>. Two different subarrays (different start or end index) are counted separately even when their sums are equal.</p><p>Return the <code>k</code> largest of these sums in non-increasing order. All numbers in <code>nums</code> are positive.</p><pre>nums = [3, 1, 2], k = 4\nsubarray sums: 6 (3,1,2), 4 (3,1), 3 (1,2), 3 (3), 2 (2), 1 (1)\nanswer = [6, 4, 3, 3]</pre>",
    constraints=["1 &le; nums.length &le; 3,000", "1 &le; nums[i] &le; 10,000", "1 &le; k &le; min(n(n+1)/2, 3,000)"],
    hints=["There are about n<sup>2</sup>/2 subarrays, far too many to sort when n is 3,000 and k is small. Which subarray has the largest sum?",
           "Because every number is positive, shrinking a subarray from either end strictly lowers its sum. So the second largest sum is one of the two subarrays obtained from the full array by dropping an end.",
           "Run a best-first search: keep a max-heap of candidate subarrays keyed by sum, starting from the whole array. Pop the best, record it, and push its two shrunk neighbours <code>[l+1, r]</code> and <code>[l, r-1]</code> (use a visited set so a subarray is never pushed twice)."],
    editorial=["Subarrays form a lattice: shrinking by one element at either end gives smaller sums. Every subarray other than the full array can be reached by shrinking some subarray with a larger sum, so the next largest sum is always the sum of an unvisited neighbour of an already-popped subarray.",
               "Compute prefix sums so any subarray sum costs O(1). Start the heap with the full array. Repeat k times: pop the largest-sum subarray <code>(l, r)</code>, append its sum to the answer, and push <code>(l+1, r)</code> and <code>(l, r-1)</code> when valid and not yet seen. The seen set matters because <code>(l+1, r-1)</code> can be reached from two parents.",
               "Each pop pushes at most two entries, so the heap never exceeds 2k elements and the running time is O(n + k log k) with O(k) memory beyond the prefix sums. This 'pop and expand neighbours' pattern is the same one used for K Smallest Pair Sums."],
    time="O(n + k log k)", space="O(n + k)",
    solution='''import heapq


def kLargestSubarraySums(nums, k):
    n = len(nums)
    pre = [0]
    for x in nums:
        pre.append(pre[-1] + x)
    heap = [(-pre[n], 0, n - 1)]
    seen = {n - 1}
    out = []
    while len(out) < k:
        s, l, r = heapq.heappop(heap)
        out.append(-s)
        if l < r:
            for l2, r2 in ((l + 1, r), (l, r - 1)):
                code = l2 * n + r2
                if code not in seen:
                    seen.add(code)
                    heapq.heappush(heap, (-(pre[r2 + 1] - pre[l2]), l2, r2))
    return out
''',
    tests=[[[3, 1, 2], 4], [[5], 1], [[1, 1, 1], 6], [[2, 7], 2], [[4, 1, 4, 1], 5], [[1, 2, 3, 4, 5], 15],
           [[10, 1, 1, 10], 3], [[1, 1, 1, 1, 1, 1], 10], [[9, 8, 7, 6], 1], [[10000, 10000], 3],
           [[1, 100, 1], 4]],
)
_r = rnd(9107)
p["tests"].append([[_r.randint(1, 10000) for _ in range(3000)], 3000])
p["tests"].append([[_r.randint(1, 5) for _ in range(3000)], 1500])
p["tests"].append([[_r.randint(1, 10000) for _ in range(2500)], 1])
p["tests"].append([[_r.randint(1, 10000) for _ in range(76)], 2926])


def b_ksub(nums, k):
    n = len(nums)
    sums = [sum(nums[i:j + 1]) for i in range(n) for j in range(i, n)]
    sums.sort(reverse=True)
    return sums[:k]


def g_ksub(r):
    n = r.randint(1, 7)
    return [[r.randint(1, 6) for _ in range(n)], r.randint(1, n * (n + 1) // 2)]


def v_ksub(tests):
    for t in tests:
        nums, k = t["args"]
        n = len(nums)
        assert 1 <= n <= 3000 and all(1 <= x <= 10000 for x in nums)
        assert 1 <= k <= min(n * (n + 1) // 2, 3000)
        assert len(t["expected"]) == k


CHECKS["k-largest-subarray-sums"] = (b_ksub, g_ksub, "exact")
VALIDATE["k-largest-subarray-sums"] = v_ksub

# ---------------------------------------------------------------- top-k students by feedback
p = add(
    id="top-k-students-by-feedback-score", title="Top K Students by Feedback Score", diff="Medium", topic=T, tier="extra",
    fn="topStudents", params=[("positive", "int[]"), ("negative", "int[]"), ("reports", "int[][]"), ("k", "int")], ret="int[]", cmp="exact",
    desc="<p>Teachers write feedback reports about students. Words are encoded as integers: <code>positive</code> lists the ids of positive words and <code>negative</code> the ids of negative words (no id is in both lists; any other word id is neutral).</p><p>Each row of <code>reports</code> is <code>[studentId, w1, w2, ...]</code>: one report about student <code>studentId</code> that contains the words <code>w1, w2, ...</code> (a row may contain only the student id). A student can be the subject of many reports. Every occurrence of a positive word adds <strong>3</strong> points, every occurrence of a negative word subtracts <strong>1</strong> point, neutral words add nothing.</p><p>Return the ids of the <code>k</code> students with the highest total score, ordered by score from high to low, and by smaller id first when scores are equal. Only students who appear in at least one report take part.</p><pre>positive = [1, 2], negative = [3]\nreports = [[10,1,3], [20,2,2], [10,3,3,4], [30,4]], k = 2\nstudent 10: +3 -1 -1 +0 = 1,  student 20: +6,  student 30: 0\nanswer = [20, 10]</pre>",
    constraints=["1 &le; reports.length &le; 500; every row has between 1 and 40 numbers", "0 &le; student id, word id &le; 10<sup>6</sup>", "0 &le; positive.length, negative.length &le; 200", "1 &le; k &le; number of distinct students in reports"],
    hints=["First compute one total score per student: a dictionary from student id to score, updated word by word for every report.",
           "Ranking is by (score descending, id ascending). Turn it into a key where 'worse' simply means 'smaller'.",
           "Push <code>(score, -id)</code> into a min-heap of size k and pop whenever it grows past k; at the end sort the survivors from best to worst."],
    editorial=["Put the positive and negative word ids into sets for O(1) lookup. Walk through every report and add <code>+3</code>, <code>-1</code> or <code>0</code> per word to the student's total.",
               "To select the k best students use a min-heap of size k whose entries are <code>(score, -id)</code>. A smaller tuple means a worse student: a lower score, or the same score with a larger id. After each push, evict the smallest when the heap has more than k entries. When all students have been seen, sort the heap in descending order and read off the ids.",
               "Scoring costs O(total words); selection costs O(S log k) for S distinct students. A plain sort of all students by <code>(-score, id)</code> is O(S log S) and equally correct; the heap version is the one to know when S is huge and k is small."],
    time="O(W + S log k)", space="O(S)",
    solution='''import heapq


def topStudents(positive, negative, reports, k):
    pos, neg = set(positive), set(negative)
    score = {}
    for row in reports:
        sid = row[0]
        sc = score.get(sid, 0)
        for w in row[1:]:
            if w in pos:
                sc += 3
            elif w in neg:
                sc -= 1
        score[sid] = sc
    heap = []
    for sid, sc in score.items():
        heapq.heappush(heap, (sc, -sid))
        if len(heap) > k:
            heapq.heappop(heap)
    heap.sort(reverse=True)
    return [-s for _, s in heap]
''',
    tests=[[[1, 2], [3], [[10, 1, 3], [20, 2, 2], [10, 3, 3, 4], [30, 4]], 2],
           [[1], [2], [[5, 1], [6, 2], [7, 9]], 3],
           [[1], [], [[3, 1], [3, 1], [2, 1, 1], [1, 1, 1, 1]], 3],
           [[], [], [[4], [2], [9, 1, 2, 3]], 2],
           [[7], [8], [[100, 8, 8, 8]], 1],
           [[1, 2, 3], [4, 5], [[1, 1, 4], [2, 2, 5], [1, 2, 3], [2, 1, 4, 5]], 2],
           [[10], [20], [[0, 20], [1000000, 10], [0, 10, 10], [1000000, 20, 20, 20]], 2],
           [[5], [6], [[1, 5], [2, 5], [3, 5], [4, 6, 6], [5, 6]], 5]],
)
_r = rnd(9108)
_pos = _r.sample(range(1, 300), 150)
_neg = _r.sample([x for x in range(1, 300) if x not in set(_pos)], 120)
p["tests"].append([_pos, _neg, [[_r.randint(0, 60)] + [_r.randint(1, 300) for _ in range(_r.randint(0, 20))] for _ in range(400)], 15])
p["tests"].append([_pos, _neg, [[_r.randint(0, 12)] + [_r.randint(1, 300) for _ in range(_r.randint(0, 6))] for _ in range(300)], 13])
_ids = _r.sample(range(0, 10 ** 6), 450)
p["tests"].append([_pos[:100], _neg[:100], [[_ids[i]] + [_r.randint(1, 300) for _ in range(_r.randint(0, 25))] for i in range(450)], 100])


def b_stud(positive, negative, reports, k):
    score = {}
    for row in reports:
        score.setdefault(row[0], 0)
        for w in row[1:]:
            if w in positive:
                score[row[0]] += 3
            if w in negative:
                score[row[0]] -= 1
    ranked = sorted(score, key=lambda s: (-score[s], s))
    return ranked[:k]


def g_stud(r):
    pool = list(range(1, 9))
    r.shuffle(pool)
    pos, neg = pool[:r.randint(0, 3)], pool[3:3 + r.randint(0, 3)]
    reports = [[r.randint(0, 4)] + [r.randint(1, 8) for _ in range(r.randint(0, 4))] for _ in range(r.randint(1, 8))]
    ds = len({row[0] for row in reports})
    return [pos, neg, reports, r.randint(1, ds)]


def v_stud(tests):
    for t in tests:
        pos, neg, reports, k = t["args"]
        assert 1 <= len(reports) <= 500 and all(1 <= len(row) <= 40 for row in reports)
        assert all(0 <= x <= 10 ** 6 for row in reports for x in row)
        assert len(pos) <= 200 and len(neg) <= 200 and not (set(pos) & set(neg))
        assert 1 <= k <= len({row[0] for row in reports})
        assert len(t["expected"]) == k


CHECKS["top-k-students-by-feedback-score"] = (b_stud, g_stud, "exact")
VALIDATE["top-k-students-by-feedback-score"] = v_stud

# ---------------------------------------------------------------- best k items with group cap
p = add(
    id="best-k-items-with-group-cap", title="Best K Items With a Cap Per Group", diff="Medium", topic=T, tier="extra",
    fn="bestItems", params=[("items", "int[][]"), ("c", "int"), ("k", "int")], ret="int", cmp="exact",
    desc="<p>A store has items <code>items[i] = [group, value]</code>. You may take at most <code>k</code> items in total and at most <code>c</code> items from any single group. Taking an item adds its <code>value</code> (which can be negative) to your total, and taking nothing is allowed.</p><p>Return the largest total you can obtain.</p><pre>items = [[1,9], [1,8], [1,7], [2,6], [2,-4], [3,5]], c = 2, k = 3\ngroup 1 offers 9, 8 (cap 2)   group 2 offers 6   group 3 offers 5\nbest three: 9 + 8 + 6 = 23\nanswer = 23</pre>",
    constraints=["1 &le; items.length &le; 4,000", "0 &le; group &le; 100", "-10,000 &le; value &le; 10,000", "1 &le; c, k &le; items.length"],
    hints=["Negative items never help, so they can be ignored from the start. Inside one group, which items are even worth considering?",
           "Only the c largest values of each group can ever be used. After keeping those, the groups no longer matter and the limit is just 'at most k items'.",
           "Per group, keep a min-heap of size c (push, then pop the smallest when it exceeds c). Collect all heap contents into one pool and sum its k largest values (another bounded heap, or <code>nlargest</code>)."],
    editorial=["Discard non-positive values. For a fixed group, any chosen item that is not among the group's c best could be swapped for an unchosen better item of the same group without breaking the group cap, so only the top c values of each group are candidates.",
               "Build those candidates with one size-c min-heap per group. Then the problem is plain: choose at most k candidates with maximum sum, which means taking the k largest candidates (all of them if fewer than k remain; all are positive, so more is never worse).",
               "Time is O(n log c) for the per-group heaps plus O(m log k) for the final selection among m candidates, with O(n) memory."],
    time="O(n log c + n log k)", space="O(n)",
    solution='''import heapq


def bestItems(items, c, k):
    groups = {}
    for g, v in items:
        if v <= 0:
            continue
        h = groups.setdefault(g, [])
        if len(h) < c:
            heapq.heappush(h, v)
        else:
            heapq.heappushpop(h, v)
    pool = [v for h in groups.values() for v in h]
    return sum(heapq.nlargest(k, pool))
''',
    tests=[[[[1, 9], [1, 8], [1, 7], [2, 6], [2, -4], [3, 5]], 2, 3],
           [[[1, 5], [1, 5], [1, 5]], 1, 3],
           [[[0, -3], [1, -2]], 2, 2],
           [[[4, 10]], 1, 1],
           [[[1, 4], [2, 3], [3, 2], [4, 1]], 1, 2],
           [[[1, 4], [2, 3], [3, 2], [4, 1]], 4, 4],
           [[[5, 7], [5, 6], [5, 5], [5, 4], [6, 1]], 3, 4],
           [[[100, 10000], [100, 10000], [0, 10000], [0, -10000]], 2, 4],
           [[[1, 0], [1, 0], [2, 0]], 1, 3],
           [[[1, 3], [2, 3], [1, 4], [2, 4], [3, 1]], 1, 5]],
)
_r = rnd(9109)
p["tests"].append([[[_r.randint(0, 100), _r.randint(-10000, 10000)] for _ in range(4000)], 7, 300])
p["tests"].append([[[_r.randint(0, 3), _r.randint(-3000, 10000)] for _ in range(3500)], 400, 1200])
p["tests"].append([[[_r.randint(0, 100), _r.randint(1, 9999)] for _ in range(3000)], 1, 3000])


def b_items(items, c, k):
    best = 0
    groups = sorted({g for g, _ in items})
    cands = []
    for g in groups:
        vals = sorted((v for gg, v in items if gg == g and v > 0), reverse=True)
        cands.extend(vals[:c])
    cands.sort(reverse=True)
    best = sum(cands[:k])
    return best


def g_items(r):
    n = r.randint(1, 9)
    return [[[r.randint(0, 3), r.randint(-5, 9)] for _ in range(n)], r.randint(1, n), r.randint(1, n)]


def v_items(tests):
    for t in tests:
        items, c, k = t["args"]
        assert 1 <= len(items) <= 4000 and 1 <= c <= len(items) and 1 <= k <= len(items)
        assert all(0 <= g <= 100 and -10000 <= v <= 10000 for g, v in items)
        assert t["expected"] >= 0


CHECKS["best-k-items-with-group-cap"] = (b_items, g_items, "exact")
VALIDATE["best-k-items-with-group-cap"] = v_items

# ================================================================ HARD

# ---------------------------------------------------------------- k-th largest subsequence sum
p = add(
    id="kth-largest-subsequence-sum", title="K-th Largest Subsequence Sum", diff="Hard", topic=T, tier="extra",
    fn="kthLargestSubsequenceSum", params=[("nums", "int[]"), ("k", "int")], ret="int", cmp="exact",
    desc="<p>A <em>subsequence</em> of <code>nums</code> is obtained by choosing any subset of the positions (the empty choice is allowed and has sum 0). Different position sets count as different subsequences even if their sums are equal, so an array of length <code>n</code> has exactly <code>2<sup>n</sup></code> subsequences.</p><p>List all subsequence sums in non-increasing order and return the <code>k</code>-th one (counting from 1). Elements may be negative.</p><pre>nums = [2, 4, -2], k = 5\nsums: 6 (2,4), 4 (4), 4 (2,4,-2), 2 (2), 2 (4,-2), 0 (empty), 0 (2,-2), -2 (-2)\n5th largest = 2</pre><p>Enumerating all <code>2<sup>n</sup></code> subsequences is impossible for large <code>n</code>; <code>k</code> is small.</p>",
    constraints=["1 &le; nums.length &le; 5,000", "-100,000 &le; nums[i] &le; 100,000", "1 &le; k &le; min(2<sup>n</sup>, 2,000)"],
    hints=["Which subsequence has the largest sum? Take every positive number. Call that sum M.",
           "Any other subsequence differs from this best one by either leaving out a positive number or including a negative one, and in both cases the sum drops by the absolute value of that element. So the sum is M minus the sum of some subset of absolute values.",
           "The k-th largest subsequence sum is M minus the k-th <em>smallest</em> subset sum of the absolute values (empty subset = 0). Generate subset sums in increasing order with a min-heap over sorted absolute values: from (sum, i) you can extend with element i+1, or swap element i for element i+1."],
    editorial=["Let M be the sum of the positive numbers and let <code>a</code> be the sorted list of absolute values. Every subsequence corresponds to exactly one subset of <code>a</code> (the positives it omits plus the negatives it includes), and its sum is M minus that subset's sum. So the k-th largest subsequence sum equals <code>M - (k-th smallest subset sum of a)</code>.",
               "Subset sums in increasing order come from a heap. The smallest is 0 (empty subset). Seed the heap with <code>(a[0], 0)</code>, meaning 'the subset whose largest index is 0'. Popping <code>(s, i)</code> yields the next smallest sum; push <code>(s + a[i+1], i+1)</code> (add the next element) and <code>(s - a[i] + a[i+1], i+1)</code> (replace the last element by the next one). Because <code>a</code> is sorted, both children are no smaller than their parent, and every non-empty subset is generated exactly once, through its unique parent obtained by removing or shifting its largest-index element.",
               "Pop k-1 times; the last popped sum (or 0 when k = 1) is the k-th smallest. The total time is O(n log n + k log k) and the heap holds O(k) entries. The trick of reducing 'k-th largest of an exponential family' to a heap walk over a sorted structure is the key idea."],
    time="O(n log n + k log k)", space="O(n + k)",
    solution='''import heapq


def kthLargestSubsequenceSum(nums, k):
    best = sum(x for x in nums if x > 0)
    a = sorted(abs(x) for x in nums)
    n = len(a)
    heap = [(a[0], 0)]
    cur = 0
    for _ in range(k - 1):
        s, i = heapq.heappop(heap)
        cur = s
        if i + 1 < n:
            heapq.heappush(heap, (s + a[i + 1], i + 1))
            heapq.heappush(heap, (s - a[i] + a[i + 1], i + 1))
    return best - cur
''',
    tests=[[[2, 4, -2], 5], [[1], 1], [[1], 2], [[-5], 2], [[-1, -2, -3], 1], [[-1, -2, -3], 8],
           [[5, 5, 5], 4], [[0, 0, 0], 8], [[3, -3], 3], [[100000, -100000, 100000], 6],
           [[1, 2, 3, 4], 10], [[-7, 7, -7, 7, 0], 20]],
)
_r = rnd(9110)
p["tests"].append([[_r.randint(-100000, 100000) for _ in range(5000)], 2000])
p["tests"].append([[_r.randint(-5, 5) for _ in range(4000)], 1999])
p["tests"].append([[_r.randint(-100000, 100000) for _ in range(11)], 2000])
p["tests"].append([[-_r.randint(1, 100000) for _ in range(4000)], 2000])


def b_kssum(nums, k):
    n = len(nums)
    sums = []
    for mask in range(1 << n):
        sums.append(sum(nums[i] for i in range(n) if mask >> i & 1))
    sums.sort(reverse=True)
    return sums[k - 1]


def g_kssum(r):
    n = r.randint(1, 8)
    return [[r.randint(-6, 6) for _ in range(n)], r.randint(1, 1 << n)]


def v_kssum(tests):
    for t in tests:
        nums, k = t["args"]
        n = len(nums)
        assert 1 <= n <= 5000 and all(-100000 <= x <= 100000 for x in nums)
        assert 1 <= k <= min(2 ** n, 2000)


CHECKS["kth-largest-subsequence-sum"] = (b_kssum, g_kssum, "exact")
VALIDATE["kth-largest-subsequence-sum"] = v_kssum

# ---------------------------------------------------------------- k-th largest in every window
p = add(
    id="kth-largest-in-every-window", title="K-th Largest in Every Window", diff="Hard", topic=T, tier="extra",
    fn="kthLargestInWindows", params=[("nums", "int[]"), ("w", "int"), ("k", "int")], ret="int[]", cmp="exact",
    desc="<p>A window of size <code>w</code> slides from the left end of <code>nums</code> to the right end, one position at a time. For each window position, report the <code>k</code>-th largest value inside the window, counting duplicates: in the window <code>[4, 4, 1]</code> the 1st largest is 4, the 2nd largest is 4 and the 3rd largest is 1.</p><p>Return an array with one answer per window position, from left to right (it has <code>n - w + 1</code> elements).</p><pre>nums = [1, 3, -1, -3, 5, 3, 6, 7], w = 3, k = 2\n[1, 3, -1] -> 1      [3, -1, -3] -> -1     [-1, -3, 5] -> -1\n[-3, 5, 3] -> 3      [5, 3, 6] -> 5        [3, 6, 7] -> 6\nanswer = [1, -1, -1, 3, 5, 6]</pre>",
    constraints=["1 &le; nums.length &le; 5,000", "-10<sup>6</sup> &le; nums[i] &le; 10<sup>6</sup>", "1 &le; k &le; w &le; nums.length"],
    hints=["Sorting every window costs O(n w log w). A window changes by exactly one element leaving and one entering. Could you keep the window organised between steps?",
           "Split the window into two groups: the k largest values, and everything else. The k-th largest value is then the smallest value of the first group.",
           "Use a min-heap for the top-k group and a max-heap for the rest. Heaps cannot delete arbitrary elements, so delete lazily: remember which indices are still in the window and in which group, and discard stale heap entries when they reach the top."],
    editorial=["Keep two groups: <code>top</code> (the k largest elements of the window, a min-heap whose root is the k-th largest) and <code>rest</code> (all others, a max-heap). Every element of top is at least every element of rest. The answer for a window is the root of top.",
               "Adding an element: if top has fewer than k elements, put it in top. Otherwise compare it with the root of top; if it is larger, it replaces the root, which moves to rest; if not, it goes to rest. Removing an element that leaves the window: if it was in top, remove it from top and promote the largest element of rest to take its place; if it was in rest just forget it.",
               "Heaps cannot remove from the middle, so removal is lazy. Give each array index a state (0 gone, 1 in top, 2 in rest) and a version number that increases whenever the index is pushed to a heap. A heap entry is valid only if its state and version match the index's current ones. Before reading or popping a heap root, pop entries that are not valid. Each index is pushed O(1) times, so the total time is O(n log n) with O(n) memory. A sorted list with binary search and insertion also works for small windows, but the two-heap approach scales to large ones."],
    time="O(n log n)", space="O(n)",
    solution='''import heapq


def kthLargestInWindows(nums, w, k):
    n = len(nums)
    top, rest = [], []          # min-heap of (value, idx, ver); max-heap of (-value, idx, ver)
    state = [0] * n             # 0 outside, 1 in top, 2 in rest
    ver = [0] * n
    cnt = 0                     # number of live elements in top

    def push_top(i):
        ver[i] += 1
        state[i] = 1
        heapq.heappush(top, (nums[i], i, ver[i]))

    def push_rest(i):
        ver[i] += 1
        state[i] = 2
        heapq.heappush(rest, (-nums[i], i, ver[i]))

    def clean_top():
        while top and (state[top[0][1]] != 1 or ver[top[0][1]] != top[0][2]):
            heapq.heappop(top)

    def clean_rest():
        while rest and (state[rest[0][1]] != 2 or ver[rest[0][1]] != rest[0][2]):
            heapq.heappop(rest)

    out = []
    for i in range(n):
        if i >= w:
            j = i - w
            if state[j] == 1:
                state[j] = 0
                cnt -= 1
                clean_rest()
                if rest:
                    m = heapq.heappop(rest)[1]
                    push_top(m)
                    cnt += 1
            else:
                state[j] = 0
        if cnt < k:
            push_top(i)
            cnt += 1
        else:
            clean_top()
            if nums[i] > top[0][0]:
                m = heapq.heappop(top)[1]
                push_rest(m)
                push_top(i)
            else:
                push_rest(i)
        if i >= w - 1:
            clean_top()
            out.append(top[0][0])
    return out
''',
    tests=[[[1, 3, -1, -3, 5, 3, 6, 7], 3, 2], [[5], 1, 1], [[2, 2, 2, 2], 2, 2], [[4, 4, 1], 3, 3], [[9, 8, 7, 6], 4, 1],
           [[9, 8, 7, 6], 4, 4], [[1, 2, 3, 4, 5, 6], 3, 1], [[6, 5, 4, 3, 2, 1], 3, 3],
           [[-1000000, 1000000, -1000000, 1000000, 0], 2, 2], [[3, 1, 4, 1, 5, 9, 2, 6, 5, 3, 5], 4, 2],
           [[1, 1, 2, 2, 3, 3], 5, 3]],
)
_r = rnd(9111)
p["tests"].append([[_r.randint(-10 ** 6, 10 ** 6) for _ in range(3500)], 1200, 500])
p["tests"].append([[_r.randint(-10 ** 6, 10 ** 6) for _ in range(3000)], 30, 5])
p["tests"].append([[_r.randint(-5, 5) for _ in range(3000)], 1500, 700])
p["tests"].append([list(range(2000)) + list(range(2000, 0, -1)), 700, 100])


def b_kwin(nums, w, k):
    return [sorted(nums[i:i + w], reverse=True)[k - 1] for i in range(len(nums) - w + 1)]


def g_kwin(r):
    n = r.randint(1, 12)
    w = r.randint(1, n)
    return [[r.randint(-5, 5) for _ in range(n)], w, r.randint(1, w)]


def v_kwin(tests):
    for t in tests:
        nums, w, k = t["args"]
        assert 1 <= len(nums) <= 5000 and all(-10 ** 6 <= x <= 10 ** 6 for x in nums)
        assert 1 <= k <= w <= len(nums)
        assert len(t["expected"]) == len(nums) - w + 1


CHECKS["kth-largest-in-every-window"] = (b_kwin, g_kwin, "exact")
VALIDATE["kth-largest-in-every-window"] = v_kwin
