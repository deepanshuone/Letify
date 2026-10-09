"""Problems: dynamic programming II (knapsack, bitmask, interval DP). See data/lib.py for the registry."""
from functools import lru_cache
from itertools import permutations, product

from lib import add, rnd, CHECKS, VALIDATE, gen_arr  # noqa: F401

TOPIC = "Dynamic Programming"
MOD = 10 ** 9 + 7


# ---------------------------------------------------------------- EASY

p = add(
    id="zero-one-knapsack-max-value", title="0/1 Knapsack Maximum Value", diff="Easy", topic=TOPIC,
    fn="zeroOneKnapsack", params=[("weights", "int[]"), ("values", "int[]"), ("capacity", "int")], ret="int", cmp="exact",
    desc="<p>A thief finds <code>n</code> distinct items. Item <code>i</code> weighs <code>weights[i]</code> and is worth <code>values[i]</code>. The bag can carry a total weight of at most <code>capacity</code>, and every item can be taken at most once (or left behind).</p><p>Return the largest total value that fits in the bag. Taking nothing is allowed, so the answer is never negative.</p>",
    constraints=["1 &le; weights.length = values.length &le; 200", "1 &le; weights[i] &le; 1,000", "0 &le; values[i] &le; 1,000,000", "0 &le; capacity &le; 5,000"],
    hints=["Greedy by value-per-weight fails here, because items cannot be split. Think about deciding item by item: take it or skip it.",
           "Let best[c] be the best value achievable with total weight at most c using the items seen so far. Adding an item of weight w and value v can turn best[c - w] into best[c - w] + v.",
           "Update the one-dimensional array from the largest capacity down to the smallest, so that each item is used at most once. The answer is best[capacity]."],
    editorial=["Process the items one at a time. After handling some prefix of the items, let <code>best[c]</code> be the maximum value of a selection from that prefix whose total weight is at most <code>c</code>. Handling a new item of weight <code>w</code> and value <code>v</code> gives <code>best[c] = max(best[c], best[c - w] + v)</code> for every <code>c &ge; w</code>: either skip the item, or take it on top of the best selection for the smaller capacity.",
               "The loop over <code>c</code> must run downward. Going downward guarantees that <code>best[c - w]</code> still describes the state <em>before</em> this item, so the item is counted once. Going upward would let the same item be reused, which turns this into the unbounded knapsack. The cost is O(n &middot; capacity) time and O(capacity) space."],
    time="O(n * capacity)", space="O(capacity)",
    solution='''def zeroOneKnapsack(weights, values, capacity):
    best = [0] * (capacity + 1)
    for w, v in zip(weights, values):
        for c in range(capacity, w - 1, -1):
            cand = best[c - w] + v
            if cand > best[c]:
                best[c] = cand
    return best[capacity]
''',
    tests=[[[1, 3, 4, 5], [1, 4, 5, 7], 7], [[2, 3, 4], [3, 4, 5], 5], [[5], [10], 4], [[5], [10], 5], [[1], [0], 0],
           [[3, 3, 3], [4, 4, 4], 0], [[2, 2, 2], [1, 2, 3], 4], [[1, 1, 1, 1], [5, 5, 5, 5], 10], [[4, 5, 1], [1, 2, 3], 4],
           [[6, 5, 4, 3, 2], [0, 0, 0, 0, 0], 9], [[10, 20, 30], [60, 100, 120], 50], [[5, 4, 6, 3], [10, 40, 30, 50], 10]],
)
_r = rnd(7101)
p["tests"].append([[_r.randint(1, 1000) for _ in range(200)], [_r.randint(0, 10 ** 6) for _ in range(200)], 5000])
p["tests"].append([[_r.randint(1, 60) for _ in range(200)], [_r.randint(0, 1000) for _ in range(200)], 5000])
p["tests"].append([[1000] * 200, [10 ** 6] * 200, 5000])
_w = [_r.randint(20, 100) for _ in range(200)]
p["tests"].append([_w, [x * 100 + _r.randint(0, 3) for x in _w], 2500])
p["tests"].append([[1] * 200, [_r.randint(0, 10 ** 6) for _ in range(200)], 117])


def b_knap01(weights, values, capacity):
    n = len(weights)
    best = 0
    for mask in range(1 << n):
        w = sum(weights[i] for i in range(n) if mask >> i & 1)
        if w <= capacity:
            best = max(best, sum(values[i] for i in range(n) if mask >> i & 1))
    return best


def g_knap01(r):
    n = r.randint(1, 9)
    return [[r.randint(1, 8) for _ in range(n)], [r.randint(0, 10) for _ in range(n)], r.randint(0, 22)]


def v_knap(tests):
    for t in tests:
        w, v, c = t["args"]
        assert 1 <= len(w) <= 200 and len(w) == len(v)
        assert all(1 <= x <= 1000 for x in w) and all(0 <= x <= 10 ** 6 for x in v)
        assert 0 <= c <= 5000


CHECKS["zero-one-knapsack-max-value"] = (b_knap01, g_knap01, "exact")
VALIDATE["zero-one-knapsack-max-value"] = v_knap

p = add(
    id="unbounded-knapsack-max-value", title="Unbounded Knapsack Maximum Value", diff="Easy", topic=TOPIC,
    fn="unboundedKnapsack", params=[("weights", "int[]"), ("values", "int[]"), ("capacity", "int")], ret="int", cmp="exact",
    desc="<p>A shop sells <code>n</code> kinds of items in unlimited quantity. One item of kind <code>i</code> weighs <code>weights[i]</code> and is worth <code>values[i]</code>. You may pack any number of copies of each kind (including none) as long as the total weight is at most <code>capacity</code>.</p><p>Return the maximum total value you can pack.</p>",
    constraints=["1 &le; weights.length = values.length &le; 200", "1 &le; weights[i] &le; 1,000", "0 &le; values[i] &le; 100,000", "0 &le; capacity &le; 5,000"],
    hints=["Compared with the 0/1 version, an item can now be used again after you have used it. Which direction of loop allows that?",
           "Let best[c] be the maximum value with total weight at most c. The last item placed has some weight w and value v, so best[c] = best[c - w] + v for some kind.",
           "For every capacity c from 1 to capacity, and every kind, try best[c] = max(best[c], best[c - w] + v). Capacities increase, so best[c - w] may already include the same kind."],
    editorial=["Let <code>best[c]</code> be the largest value achievable with total weight at most <code>c</code>, with <code>best[0] = 0</code>. If an optimal packing for capacity <code>c</code> is non-empty, remove one item of some kind <code>i</code>; what remains is a packing for capacity <code>c - weights[i]</code>. So <code>best[c]</code> is the maximum of <code>best[c - 1]</code> (leave one unit of capacity unused) and <code>best[c - weights[i]] + values[i]</code> over all kinds <code>i</code> that fit.",
               "Iterating capacities upward means <code>best[c - w]</code> may already contain copies of the same kind, which is exactly what unlimited supply allows. This is the one-line difference from the 0/1 knapsack, where the capacity loop runs downward. Time is O(n &middot; capacity) and space is O(capacity)."],
    time="O(n * capacity)", space="O(capacity)",
    solution='''def unboundedKnapsack(weights, values, capacity):
    best = [0] * (capacity + 1)
    for c in range(1, capacity + 1):
        top = best[c - 1]
        for w, v in zip(weights, values):
            if w <= c and best[c - w] + v > top:
                top = best[c - w] + v
        best[c] = top
    return best[capacity]
''',
    tests=[[[1, 3, 4, 5], [1, 4, 5, 7], 7], [[2, 3], [5, 8], 7], [[5], [10], 4], [[5], [10], 23], [[1], [0], 0],
           [[3, 4], [4, 5], 0], [[2, 3, 5], [1, 1, 1], 9], [[4, 6], [7, 11], 12], [[10, 7], [10, 6], 13],
           [[3, 5, 7], [0, 0, 0], 20], [[1, 2], [3, 5], 9], [[6, 4], [13, 8], 14]],
)
p["tests"].append([[_r.randint(1, 1000) for _ in range(200)], [_r.randint(0, 100000) for _ in range(200)], 5000])
p["tests"].append([[_r.randint(1, 60) for _ in range(200)], [_r.randint(0, 1000) for _ in range(200)], 5000])
p["tests"].append([[1000, 999, 998], [100000, 99800, 99700], 5000])
_w = [_r.randint(50, 500) for _ in range(150)]
p["tests"].append([_w, [x * 20 + _r.randint(0, 5) for x in _w], 4999])
p["tests"].append([[1000] * 200, [100000] * 200, 4999])


def b_unbounded(weights, values, capacity):
    n = len(weights)

    @lru_cache(maxsize=None)
    def go(i, cap):
        if i == n:
            return 0
        return max(k * values[i] + go(i + 1, cap - k * weights[i]) for k in range(cap // weights[i] + 1))

    return go(0, capacity)


def g_unbounded(r):
    n = r.randint(1, 5)
    return [[r.randint(1, 8) for _ in range(n)], [r.randint(0, 10) for _ in range(n)], r.randint(0, 30)]


def v_unbounded(tests):
    for t in tests:
        w, v, c = t["args"]
        assert 1 <= len(w) <= 200 and len(w) == len(v)
        assert all(1 <= x <= 1000 for x in w) and all(0 <= x <= 100000 for x in v)
        assert 0 <= c <= 5000


CHECKS["unbounded-knapsack-max-value"] = (b_unbounded, g_unbounded, "exact")
VALIDATE["unbounded-knapsack-max-value"] = v_unbounded


# -------------------------------------------------------------- MEDIUM

p = add(
    id="target-sum-assign-signs-count", title="Target Sum by Assigning Signs", diff="Medium", topic=TOPIC,
    fn="countSignAssignments", params=[("nums", "int[]"), ("target", "int")], ret="int", cmp="exact",
    desc="<p>You are given an array <code>nums</code> of non-negative integers and an integer <code>target</code>. Put either a <code>+</code> or a <code>-</code> sign in front of every element of <code>nums</code> and add them all up.</p><p>Return the number of different sign assignments whose total equals <code>target</code>. Two assignments are different if some index gets a different sign, so an element equal to <code>0</code> doubles the count: both of its signs give the same sum but count as separate assignments.</p>",
    constraints=["1 &le; nums.length &le; 30", "0 &le; nums[i] &le; 1,000", "-30,000 &le; target &le; 30,000", "The answer fits in a 32-bit signed integer"],
    hints=["There are 2<sup>n</sup> sign assignments, which is far too many for n = 30. Look for structure in what a valid assignment looks like.",
           "Let P be the sum of the elements that get a plus sign and N the sum of those with a minus sign. Then P - N = target, while P + N = sum(nums).",
           "So P = (sum + target) / 2. The task becomes: count the subsets of nums with sum exactly P. Check parity and range first, then use a counting knapsack with a downward loop."],
    editorial=["Call the sum of the plus-signed elements <code>P</code> and the sum of the minus-signed elements <code>N</code>. Then <code>P - N = target</code> and <code>P + N = total</code>, so <code>P = (total + target) / 2</code>. If <code>|target| &gt; total</code> or <code>total + target</code> is odd, no assignment exists and the answer is 0.",
               "Otherwise every assignment corresponds to exactly one subset (the plus-signed indices) with sum <code>P</code>. Count them with <code>ways[s]</code> = number of subsets with sum <code>s</code>: start with <code>ways[0] = 1</code> and, for each element <code>x</code>, update <code>ways[s] += ways[s - x]</code> from high <code>s</code> to low. A zero element makes each count double, which matches the statement. Time O(n &middot; P), space O(P)."],
    time="O(n * sum)", space="O(sum)",
    solution='''def countSignAssignments(nums, target):
    total = sum(nums)
    if abs(target) > total or (total + target) % 2:
        return 0
    need = (total + target) // 2
    ways = [0] * (need + 1)
    ways[0] = 1
    for x in nums:
        for s in range(need, x - 1, -1):
            ways[s] += ways[s - x]
    return ways[need]
''',
    tests=[[[1, 1, 1, 1, 1], 3], [[1], 1], [[1], -1], [[1], 2], [[0], 0], [[0], 1], [[0, 0, 0, 0, 0, 0, 0, 0, 1], 1],
           [[1, 2, 3, 4], 0], [[5, 5], 0], [[2, 4, 6], 3], [[7, 9, 3, 8, 0, 2, 4, 8, 3, 9], 0], [[100, 200, 300], -600],
           [[3, 3, 3, 3], 6]],
)
_r = rnd(7102)
p["tests"].append([[0] * 30, 0])
p["tests"].append([[1] * 30, 0])
p["tests"].append([[1] * 29 + [2], 0])
_a = [_r.randint(0, 1000) for _ in range(30)]
p["tests"].append([_a, sum(_a) - 2 * sum(_a[::3])])
_a = [_r.randint(0, 40) for _ in range(30)]
p["tests"].append([_a, sum(_a) - 2 * sum(_a[1::2])])
p["tests"].append([[1000] * 30, 30000])
p["tests"].append([[1000] * 30, -28000])
p["tests"].append([[_r.randint(1, 1000) for _ in range(30)], 30001 - 1])


def b_target(nums, target):
    cnt = 0
    for signs in product((1, -1), repeat=len(nums)):
        if sum(s * x for s, x in zip(signs, nums)) == target:
            cnt += 1
    return cnt


def g_target(r):
    n = r.randint(1, 10)
    nums = [r.randint(0, 6) for _ in range(n)]
    return [nums, r.randint(-sum(nums) - 1, sum(nums) + 1)]


def v_target(tests):
    for t in tests:
        nums, target = t["args"]
        assert 1 <= len(nums) <= 30 and all(0 <= x <= 1000 for x in nums)
        assert -30000 <= target <= 30000
        assert t["expected"] <= 2 ** 31 - 1


CHECKS["target-sum-assign-signs-count"] = (b_target, g_target, "exact")
VALIDATE["target-sum-assign-signs-count"] = v_target

p = add(
    id="last-stone-weight-ii-min-remaining", title="Smash Stones, Minimum Remainder", diff="Medium", topic=TOPIC,
    fn="minRemainingStone", params=[("stones", "int[]")], ret="int", cmp="exact",
    desc="<p>You have a pile of stones, where <code>stones[i]</code> is the weight of the <code>i</code>-th stone. Repeatedly choose <em>any</em> two stones with weights <code>x &le; y</code> and smash them together:</p><ul><li>if <code>x == y</code>, both stones are destroyed;</li><li>otherwise the lighter one is destroyed and the heavier one is left with weight <code>y - x</code>.</li></ul><p>You may stop only when at most one stone remains. You choose the pair at every step, trying to make the final result as small as possible. Return the smallest possible weight of the last stone, or <code>0</code> if no stone is left.</p>",
    constraints=["1 &le; stones.length &le; 100", "1 &le; stones[i] &le; 100"],
    hints=["Try small cases by hand. Notice that every stone ends up contributing either positively or negatively to the final weight.",
           "The final weight always equals |sum of some group of stones - sum of the remaining group|, and any split of the stones into two groups can be realised by a suitable smashing order.",
           "So you want to split the stones into two groups with sums as close as possible. Find which sums up to total/2 are reachable by a subset (a 0/1 knapsack feasibility table) and take the largest reachable one."],
    editorial=["Unroll all the smashes: each stone is added to or subtracted from the final weight, so the last stone weighs <code>|S1 - S2|</code> for some partition of the stones into two groups with sums <code>S1</code> and <code>S2</code>. Conversely every partition can be realised, by repeatedly smashing a stone from the heavier group against a stone from the lighter one, so the answer is the minimum of <code>|S1 - S2|</code> over all partitions.",
               "With <code>S1 + S2 = total</code> this is <code>total - 2 * a</code> where <code>a &le; total / 2</code> is the largest subset sum that does not exceed half of the total. Subset sums are computed with a boolean table (or a Python big-integer bitset: <code>bits |= bits &lt;&lt; s</code> for each stone). The cost is O(n &middot; total)."],
    time="O(n * sum)", space="O(sum)",
    solution='''def minRemainingStone(stones):
    total = sum(stones)
    bits = 1
    for s in stones:
        bits |= bits << s
    for a in range(total // 2, -1, -1):
        if (bits >> a) & 1:
            return total - 2 * a
    return total
''',
    tests=[[[2, 7, 4, 1, 8, 1]], [[31, 26, 33, 21, 40]], [[1]], [[5, 5]], [[3, 9]], [[1, 1, 1]], [[1, 2, 3, 4, 5]],
           [[100, 1, 1]], [[10, 10, 10, 10, 7]], [[7, 3, 3, 3, 3, 3, 3]], [[4, 4, 4, 4, 4, 4, 4]], [[9, 8, 7, 1]]],
)
_r = rnd(7103)
p["tests"].append([[_r.randint(1, 100) for _ in range(100)]])
p["tests"].append([[100] * 99 + [99]])
p["tests"].append([[_r.randint(90, 100) for _ in range(100)]])
p["tests"].append([[2 * _r.randint(1, 50) for _ in range(100)]])
p["tests"].append([[1] * 100])
p["tests"].append([[100, 99, 98, 97, 96] * 20])
p["tests"].append([[_r.choice([1, 100]) for _ in range(100)]])


@lru_cache(maxsize=None)
def _smash(state):
    if len(state) <= 1:
        return state[0] if state else 0
    best = None
    for i in range(len(state)):
        for j in range(i + 1, len(state)):
            rest = list(state[:i] + state[i + 1:j] + state[j + 1:])
            d = abs(state[i] - state[j])
            if d:
                rest.append(d)
            res = _smash(tuple(sorted(rest)))
            if best is None or res < best:
                best = res
    return best


def b_stones2(stones):
    return _smash(tuple(sorted(stones)))


def g_stones2(r):
    return [[r.randint(1, 12) for _ in range(r.randint(1, 7))]]


def v_stones2(tests):
    for t in tests:
        s = t["args"][0]
        assert 1 <= len(s) <= 100 and all(1 <= x <= 100 for x in s)


CHECKS["last-stone-weight-ii-min-remaining"] = (b_stones2, lambda r: g_stones2(r), "exact")
VALIDATE["last-stone-weight-ii-min-remaining"] = v_stones2

p = add(
    id="combination-sum-iv-ordered-count", title="Count Ordered Sums to Target", diff="Medium", topic=TOPIC,
    fn="countOrderedSums", params=[("nums", "int[]"), ("target", "int")], ret="int", cmp="exact",
    desc="<p>You are given an array <code>nums</code> of distinct positive integers and a positive integer <code>target</code>. Count the sequences of numbers, each chosen from <code>nums</code> with repetition allowed, whose sum equals <code>target</code>. The order matters: <code>[1, 2]</code> and <code>[2, 1]</code> are different sequences.</p><p>The count can be huge, so return it modulo <code>1,000,000,007</code>.</p>",
    constraints=["1 &le; nums.length &le; 100", "1 &le; nums[i] &le; 1,000, all values distinct", "1 &le; target &le; 5,000"],
    hints=["Think about the last number of a valid sequence. What is the sum of everything before it?",
           "If the last number is x, the earlier part is any ordered sequence that sums to target - x. So ways[t] is the sum of ways[t - x] over all x in nums with x &le; t.",
           "Set ways[0] = 1 (the empty sequence) and fill t = 1..target in increasing order, taking everything modulo 1,000,000,007."],
    editorial=["Let <code>ways[t]</code> be the number of ordered sequences summing to <code>t</code>. Group the sequences by their last element <code>x</code>: removing it leaves an ordered sequence summing to <code>t - x</code>, and every such sequence extended by <code>x</code> is valid. Hence <code>ways[t] = sum of ways[t - x]</code> over all <code>x &le; t</code> in <code>nums</code>, with <code>ways[0] = 1</code>.",
               "The loop order is what makes the count ordered: the target is the outer loop and the numbers are the inner loop, so every position of a sequence can use every number. Swapping the loops (numbers outside) would count combinations instead, ignoring order. Time O(n &middot; target), space O(target)."],
    time="O(n * target)", space="O(target)",
    solution='''def countOrderedSums(nums, target):
    MOD = 1_000_000_007
    ways = [0] * (target + 1)
    ways[0] = 1
    for t in range(1, target + 1):
        total = 0
        for x in nums:
            if x <= t:
                total += ways[t - x]
        ways[t] = total % MOD
    return ways[target]
''',
    tests=[[[1, 2, 3], 4], [[9], 3], [[1], 1], [[1], 7], [[2], 7], [[2], 8], [[1, 2], 10], [[3, 5], 11], [[4, 2, 1], 6],
           [[7, 2, 9, 4], 1], [[2, 3, 6, 7], 7], [[5, 1, 8], 13]],
)
_r = rnd(7104)
p["tests"].append([[1], 5000])
p["tests"].append([[1, 2], 5000])
p["tests"].append([[1, 2, 3], 5000])
p["tests"].append([list(range(1, 100)), 5000])
p["tests"].append([_r.sample(range(1, 1001), 100), 5000])
p["tests"].append([_r.sample(range(1, 1001), 100), 1000])
p["tests"].append([[1000, 999, 997], 5000])
p["tests"].append([[500, 1000, 250], 4750])
p["tests"].append([[7, 13, 29, 101, 333], 4096])


def b_ordered(nums, target):
    count = 0
    stack = [0]
    while stack:
        s = stack.pop()
        if s == target:
            count += 1
            continue
        for x in nums:
            if s + x <= target:
                stack.append(s + x)
    return count % MOD


def g_ordered(r):
    return [r.sample(range(1, 9), r.randint(1, 4)), r.randint(1, 14)]


def v_ordered(tests):
    for t in tests:
        nums, target = t["args"]
        assert 1 <= len(nums) <= 100 and len(set(nums)) == len(nums)
        assert all(1 <= x <= 1000 for x in nums)
        assert 1 <= target <= 5000


CHECKS["combination-sum-iv-ordered-count"] = (b_ordered, g_ordered, "exact")
VALIDATE["combination-sum-iv-ordered-count"] = v_ordered

p = add(
    id="minimum-score-triangulation-polygon", title="Minimum Score Triangulation", diff="Medium", topic=TOPIC,
    fn="minScoreTriangulation", params=[("values", "int[]")], ret="int", cmp="exact",
    desc="<p>A convex polygon has <code>n</code> vertices, listed in order around the polygon. Vertex <code>i</code> carries the number <code>values[i]</code>.</p><p>You split the polygon into <code>n - 2</code> triangles by drawing non-crossing diagonals between vertices. The score of one triangle is the <em>product</em> of the three numbers on its corners, and the score of a triangulation is the sum over its triangles. Return the smallest score over all possible triangulations.</p>",
    constraints=["3 &le; values.length &le; 100", "1 &le; values[i] &le; 100"],
    hints=["Look at the edge between the first vertex and the last vertex. In every triangulation it belongs to exactly one triangle.",
           "That triangle uses some third vertex k strictly between them. It cuts the polygon into two smaller polygons: vertices i..k and vertices k..j.",
           "Define dp[i][j] as the best score for the polygon formed by vertices i..j (with the edge i-j closing it). Then dp[i][j] = min over k of dp[i][k] + dp[k][j] + values[i] * values[k] * values[j]. Fill by increasing j - i."],
    editorial=["Interval DP. For vertices <code>i &lt; j</code>, let <code>dp[i][j]</code> be the minimum score to triangulate the sub-polygon formed by the vertices <code>i, i+1, ..., j</code>; it is 0 when <code>j - i &lt; 2</code> because no triangle fits. The chord <code>(i, j)</code> is an edge of this sub-polygon, so it belongs to exactly one triangle <code>(i, k, j)</code> with <code>i &lt; k &lt; j</code>. That triangle scores <code>values[i] * values[k] * values[j]</code> and leaves the sub-polygons <code>i..k</code> and <code>k..j</code> to be triangulated independently.",
               "Hence <code>dp[i][j] = min over k of dp[i][k] + dp[k][j] + values[i] * values[k] * values[j]</code>. Process the intervals by increasing length; the answer is <code>dp[0][n-1]</code>. There are O(n<sup>2</sup>) states and O(n) choices each, so O(n<sup>3</sup>) time and O(n<sup>2</sup>) space."],
    time="O(n^3)", space="O(n^2)",
    solution='''def minScoreTriangulation(values):
    n = len(values)
    dp = [[0] * n for _ in range(n)]
    for length in range(2, n):
        for i in range(n - length):
            j = i + length
            best = None
            for k in range(i + 1, j):
                cost = dp[i][k] + dp[k][j] + values[i] * values[k] * values[j]
                if best is None or cost < best:
                    best = cost
            dp[i][j] = best
    return dp[0][n - 1]
''',
    tests=[[[1, 2, 3]], [[3, 7, 4, 5]], [[1, 3, 1, 4, 1, 5]], [[100, 100, 100]], [[2, 2, 2, 2]], [[5, 1, 5, 1]],
           [[10, 1, 10, 1, 10]], [[1, 1, 1, 1, 1, 1, 1]], [[9, 8, 7, 6, 5, 4]], [[4, 9, 2, 8, 3, 7, 1]],
           [[100, 1, 100, 1, 100, 1]], [[2, 100, 2]]],
)
_r = rnd(7105)
p["tests"].append([[_r.randint(1, 100) for _ in range(100)]])
p["tests"].append([[100] * 100])
p["tests"].append([[1] * 100])
p["tests"].append([[100 if i % 2 else 1 for i in range(100)]])
p["tests"].append([list(range(1, 101))])
p["tests"].append([[_r.randint(1, 10) for _ in range(60)]])
p["tests"].append([[_r.randint(1, 100) for _ in range(23)]])


@lru_cache(maxsize=None)
def _ear(poly):
    m = len(poly)
    if m == 3:
        return poly[0] * poly[1] * poly[2]
    best = None
    for i in range(m):
        cost = poly[i - 1] * poly[i] * poly[(i + 1) % m]
        res = cost + _ear(poly[:i] + poly[i + 1:])
        if best is None or res < best:
            best = res
    return best


def b_triang(values):
    return _ear(tuple(values))


def g_triang(r):
    return [[r.randint(1, 12) for _ in range(r.randint(3, 8))]]


def v_triang(tests):
    for t in tests:
        v = t["args"][0]
        assert 3 <= len(v) <= 100 and all(1 <= x <= 100 for x in v)


CHECKS["minimum-score-triangulation-polygon"] = (b_triang, g_triang, "exact")
VALIDATE["minimum-score-triangulation-polygon"] = v_triang

p = add(
    id="can-i-win-bitmask-game", title="Pick Numbers to Reach the Total", diff="Medium", topic=TOPIC,
    fn="canFirstPlayerWin", params=[("maxChoosable", "int"), ("desiredTotal", "int")], ret="bool", cmp="exact",
    desc="<p>Two players take turns choosing a number from the pool <code>1, 2, ..., maxChoosable</code>. A number, once chosen by either player, is removed from the pool and cannot be chosen again. The running total of all chosen numbers is tracked, and the player whose choice makes the total reach <code>desiredTotal</code> or more wins immediately.</p><p>If the pool is exhausted and nobody has reached the target, nobody wins. The first player moves first and both players play perfectly. Return <code>true</code> if the first player can force a win, and <code>false</code> otherwise.</p>",
    constraints=["1 &le; maxChoosable &le; 15", "0 &le; desiredTotal &le; 150"],
    hints=["Handle the trivial cases first: what if desiredTotal is already 0, or if even the sum of the whole pool cannot reach it?",
           "The state of the game is fully described by which numbers are already used, because the running total is just their sum. A bitmask of 15 bits is a compact description.",
           "A state is winning for the player to move if some available number either reaches the target or leaves the opponent in a losing state. Memoise the result per bitmask."],
    editorial=["If <code>desiredTotal</code> is 0 (or less) the first player wins on the first move. If the numbers <code>1..maxChoosable</code> add up to less than <code>desiredTotal</code>, nobody can win, so the answer is <code>false</code>.",
               "Otherwise, represent the used numbers as a bitmask. The total so far is the sum of the used numbers, so the mask alone is the complete game state. A state is winning for the player to move if there is an unused number <code>x</code> such that either the total plus <code>x</code> reaches the target or the state after taking <code>x</code> is losing for the opponent. With memoisation there are at most 2<sup>maxChoosable</sup> states and each does up to maxChoosable work: O(2<sup>m</sup> &middot; m)."],
    time="O(2^m * m)", space="O(2^m)",
    solution='''def canFirstPlayerWin(maxChoosable, desiredTotal):
    if desiredTotal <= 0:
        return True
    if maxChoosable * (maxChoosable + 1) // 2 < desiredTotal:
        return False
    memo = {}

    def win(used, remaining):
        if used in memo:
            return memo[used]
        result = False
        for i in range(maxChoosable):
            bit = 1 << i
            if used & bit:
                continue
            if i + 1 >= remaining or not win(used | bit, remaining - (i + 1)):
                result = True
                break
        memo[used] = result
        return result

    return win(0, desiredTotal)
''',
    tests=[[10, 11], [10, 0], [10, 1], [1, 1], [1, 2], [1, 0], [2, 3], [3, 6], [4, 6], [5, 15], [5, 16], [6, 12],
           [8, 30], [15, 60], [15, 100], [15, 119], [15, 120], [15, 121], [15, 150], [14, 77], [13, 90], [15, 75],
           [12, 55], [15, 111], [15, 95], [15, 42]],
)


def b_canwin(maxChoosable, desiredTotal):
    # outcome for the player to move: 1 = wins, 0 = nobody wins, -1 = loses
    @lru_cache(maxsize=None)
    def go(remaining_nums, need):
        if not remaining_nums:
            return 0
        best = -1
        for x in remaining_nums:
            if x >= need:
                return 1
            best = max(best, -go(remaining_nums - {x}, need - x))
        return best

    if desiredTotal <= 0:
        return True
    return go(frozenset(range(1, maxChoosable + 1)), desiredTotal) == 1


def g_canwin(r):
    m = r.randint(1, 8)
    return [m, r.randint(0, m * (m + 1) // 2 + 3)]


def v_canwin(tests):
    for t in tests:
        m, d = t["args"]
        assert 1 <= m <= 15 and 0 <= d <= 150
    assert any(t["expected"] for t in tests) and any(not t["expected"] for t in tests)


CHECKS["can-i-win-bitmask-game"] = (b_canwin, g_canwin, "exact")
VALIDATE["can-i-win-bitmask-game"] = v_canwin

p = add(
    id="predict-the-winner-pile-ends", title="Predict the Winner from Pile Ends", diff="Medium", topic=TOPIC,
    fn="canFirstPlayerWinPiles", params=[("nums", "int[]")], ret="bool", cmp="exact",
    desc="<p>Two players play a game on a row of piles, where pile <code>i</code> contains <code>nums[i]</code> points. They alternate turns, the first player going first. On a turn, the player must take the pile at either the left end or the right end of the remaining row, and adds its points to their own score.</p><p>The game ends when no piles remain, and the player with the higher score wins. If the scores are equal, the first player wins. Assuming both players play to maximise their own advantage, return <code>true</code> if the first player wins.</p>",
    constraints=["1 &le; nums.length &le; 500", "0 &le; nums[i] &le; 10,000,000"],
    hints=["Instead of tracking two scores, track only the score difference (current player minus opponent). The player to move wants to maximise it.",
           "Let diff(l, r) be the best difference the player to move can achieve on piles l..r. Taking the left pile gives nums[l] minus whatever the opponent then achieves on l+1..r.",
           "diff(l, r) = max(nums[l] - diff(l+1, r), nums[r] - diff(l, r-1)). The first player wins exactly when diff(0, n-1) &ge; 0."],
    editorial=["Both players have the same goal in a zero-sum game, so describe each position by a single number: <code>diff(l, r)</code>, the largest possible (my score minus opponent's score) from the piles <code>l..r</code> when it is my turn. If I take <code>nums[l]</code>, the opponent is then the player to move on <code>l+1..r</code> and gains <code>diff(l+1, r)</code> over me, so I end up with <code>nums[l] - diff(l+1, r)</code>; similarly for the right end.",
               "Therefore <code>diff(l, r) = max(nums[l] - diff(l+1, r), nums[r] - diff(l, r-1))</code> with <code>diff(i, i) = nums[i]</code>. The first player wins iff <code>diff(0, n-1) &ge; 0</code> (ties go to the first player). Filling the table by increasing interval length takes O(n<sup>2</sup>) time; keeping one row gives O(n) space."],
    time="O(n^2)", space="O(n)",
    solution='''def canFirstPlayerWinPiles(nums):
    n = len(nums)
    dp = nums[:]          # dp[j] = diff(i, j) for the current i
    for i in range(n - 2, -1, -1):
        for j in range(i + 1, n):
            dp[j] = max(nums[i] - dp[j], nums[j] - dp[j - 1])
    return dp[n - 1] >= 0
''',
    tests=[[[1, 5, 2]], [[1, 5, 233, 7]], [[7]], [[0]], [[3, 3]], [[1, 2]], [[2, 1, 2]], [[1, 1, 1]], [[1, 2, 3]],
           [[5, 3, 4, 5]], [[0, 0, 0, 0]], [[1, 100, 1]], [[9, 1, 1, 9, 1]], [[4, 2, 7, 1, 8, 2]]],
)
_r = rnd(7106)
p["tests"].append([[_r.randint(0, 10 ** 7) for _ in range(500)]])
p["tests"].append([[_r.randint(0, 10 ** 7) for _ in range(499)]])
p["tests"].append([[10 ** 7] * 500])
p["tests"].append([[i + 1 for i in range(500)]])
p["tests"].append([[500 - i for i in range(499)]])
p["tests"].append([[(10 ** 7 if i % 2 else 1) for i in range(500)]])
p["tests"].append([[_r.randint(0, 3) for _ in range(300)]])


def b_piles(nums):
    n = len(nums)

    def margin(l, r, turn):
        if l > r:
            return 0
        if turn == 0:
            return max(nums[l] + margin(l + 1, r, 1), nums[r] + margin(l, r - 1, 1))
        return min(-nums[l] + margin(l + 1, r, 0), -nums[r] + margin(l, r - 1, 0))

    return margin(0, n - 1, 0) >= 0


def g_piles(r):
    return [[r.randint(0, 9) for _ in range(r.randint(1, 12))]]


def v_piles(tests):
    for t in tests:
        a = t["args"][0]
        assert 1 <= len(a) <= 500 and all(0 <= x <= 10 ** 7 for x in a)
    assert any(t["expected"] for t in tests) and any(not t["expected"] for t in tests)


CHECKS["predict-the-winner-pile-ends"] = (b_piles, g_piles, "exact")
VALIDATE["predict-the-winner-pile-ends"] = v_piles


# ---------------------------------------------------------------- HARD

p = add(
    id="minimum-cost-to-merge-stones-k-piles", title="Merge Stones into One Pile", diff="Hard", topic=TOPIC,
    fn="mergeStonesMinCost", params=[("stones", "int[]"), ("k", "int")], ret="int", cmp="exact",
    desc="<p>There are <code>n</code> piles of stones in a row, and <code>stones[i]</code> is the number of stones in pile <code>i</code>. In one move you pick exactly <code>k</code> <em>consecutive</em> piles and merge them into a single pile. The cost of the move is the total number of stones in those <code>k</code> piles, and the new pile holds that many stones.</p><p>Return the minimum total cost of merging all the piles into one single pile, or <code>-1</code> if it is impossible.</p>",
    constraints=["1 &le; stones.length &le; 100", "1 &le; stones[i] &le; 100", "2 &le; k &le; 30"],
    hints=["Each merge reduces the pile count by k - 1. When can n piles ever become exactly 1 pile?",
           "Use interval DP. Let dp[i][j] be the minimum cost to merge piles i..j into as few piles as possible. Think about where the first merged group ends.",
           "Split [i, j] as [i, m] merged into one pile plus [m+1, j] reduced to (len - 1) mod (k - 1) piles; m advances in steps of k - 1. If the length of [i, j] minus 1 is divisible by k - 1, add the sum of the interval for the final merge."],
    editorial=["Each move removes <code>k - 1</code> piles, so one pile can be reached only if <code>(n - 1) % (k - 1) == 0</code>; otherwise the answer is -1.",
               "Let <code>dp[i][j]</code> be the minimum cost to merge the piles <code>i..j</code> until no more merges are possible, which leaves <code>(len - 1) % (k - 1) + 1</code> piles. Intervals shorter than <code>k</code> cost 0. For longer intervals, the leftmost remaining pile covers some prefix <code>[i, m]</code> that was merged into a single pile, so <code>m - i</code> is a multiple of <code>k - 1</code>, and the rest <code>[m+1, j]</code> is reduced independently: <code>dp[i][j] = min over m of dp[i][m] + dp[m+1][j]</code>. If the interval can collapse completely, i.e. <code>(len - 1) % (k - 1) == 0</code>, the last merge combines <code>k</code> piles holding the whole interval's stones, adding <code>prefix[j+1] - prefix[i]</code>.",
               "There are O(n<sup>2</sup>) intervals and about n / (k - 1) split points each, so the total time is O(n<sup>3</sup> / k) and space is O(n<sup>2</sup>)."],
    time="O(n^3 / k)", space="O(n^2)",
    solution='''def mergeStonesMinCost(stones, k):
    n = len(stones)
    if (n - 1) % (k - 1):
        return -1
    pre = [0]
    for s in stones:
        pre.append(pre[-1] + s)
    dp = [[0] * n for _ in range(n)]
    for length in range(k, n + 1):
        for i in range(n - length + 1):
            j = i + length - 1
            best = min(dp[i][m] + dp[m + 1][j] for m in range(i, j, k - 1))
            if (length - 1) % (k - 1) == 0:
                best += pre[j + 1] - pre[i]
            dp[i][j] = best
    return dp[0][n - 1]
''',
    tests=[[[3, 2, 4, 1], 2], [[3, 2, 4, 1], 3], [[3, 5, 1, 2, 6], 3], [[5], 2], [[5], 7], [[4, 6], 2], [[4, 6], 3],
           [[1, 1, 1, 1, 1, 1, 1], 2], [[9, 1, 1, 9], 2], [[1, 2, 3, 4, 5, 6, 7], 3], [[2, 2, 2, 2, 2], 5],
           [[100, 1, 100, 1, 100], 3], [[5, 4, 3, 2, 1, 6, 7, 8, 9], 4], [[1, 2, 3, 4, 5, 6], 3]],
)
_r = rnd(7107)
p["tests"].append([[_r.randint(1, 100) for _ in range(100)], 2])
p["tests"].append([[_r.randint(1, 100) for _ in range(88)], 30])
p["tests"].append([[_r.randint(1, 100) for _ in range(100)], 4])
p["tests"].append([[_r.randint(1, 100) for _ in range(97)], 3])
p["tests"].append([[_r.randint(1, 100) for _ in range(100)], 3])
p["tests"].append([[100] * 100, 2])
p["tests"].append([[_r.randint(1, 100) for _ in range(91)], 10])
p["tests"].append([[_r.randint(1, 100) for _ in range(60)], 30])
p["tests"].append([[_r.randint(1, 9) for _ in range(85)], 6])


def b_merge(stones, k):
    INF = float("inf")

    @lru_cache(maxsize=None)
    def go(state):
        if len(state) == 1:
            return 0
        best = INF
        for i in range(len(state) - k + 1):
            s = sum(state[i:i + k])
            best = min(best, s + go(state[:i] + (s,) + state[i + k:]))
        return best

    res = go(tuple(stones))
    return -1 if res == INF else res


def g_merge(r):
    return [[r.randint(1, 12) for _ in range(r.randint(1, 9))], r.randint(2, 4)]


def v_merge(tests):
    for t in tests:
        s, k = t["args"]
        assert 1 <= len(s) <= 100 and all(1 <= x <= 100 for x in s) and 2 <= k <= 30
    assert any(t["expected"] == -1 for t in tests) and any(t["expected"] > 0 for t in tests)


CHECKS["minimum-cost-to-merge-stones-k-piles"] = (b_merge, g_merge, "exact")
VALIDATE["minimum-cost-to-merge-stones-k-piles"] = v_merge

p = add(
    id="shortest-walk-visiting-all-nodes", title="Shortest Walk Visiting Every Node", diff="Hard", topic=TOPIC,
    fn="shortestWalkAllNodes", params=[("graph", "int[][]")], ret="int", cmp="exact",
    desc="<p>An undirected, connected graph has <code>n</code> nodes labelled <code>0</code> to <code>n - 1</code>. It is given as an adjacency list: <code>graph[i]</code> lists every node that shares an edge with node <code>i</code>.</p><p>A walk may start at any node, may finish anywhere, and may revisit nodes and reuse edges as often as needed. Return the minimum number of edges in a walk that visits every node at least once.</p>",
    constraints=["1 &le; graph.length &le; 12", "0 &le; graph[i].length &lt; graph.length", "graph[i] has no repeated values and never contains i", "j is in graph[i] if and only if i is in graph[j]", "The graph is connected"],
    hints=["Because nodes may be revisited, a plain search over simple paths is not enough. Which pieces of information must a search state remember?",
           "A state is (set of visited nodes, current node). With n &le; 12 there are at most 2<sup>12</sup> &middot; 12 states, which is small.",
           "All edges cost 1, so run a breadth-first search on these states, starting from every node at once with only that node marked visited. The first time a state's mask is full, its distance is the answer."],
    editorial=["Model the walk as a path in a state graph. A state is a pair <code>(mask, u)</code>: <code>mask</code> is the set of nodes visited so far and <code>u</code> the current node. Moving along an edge <code>u - v</code> goes to <code>(mask | (1 &lt;&lt; v), v)</code> and costs one edge. A state can be revisited with the same mask, which is why we keep a visited table over states rather than over nodes.",
               "Since every transition costs 1, breadth-first search finds shortest distances. Start with all <code>(1 &lt;&lt; i, i)</code> at distance 0 (the walk may begin anywhere) and stop at the first state whose mask has all <code>n</code> bits set. For a single node the answer is 0. There are <code>n &middot; 2<sup>n</sup></code> states and each expands over at most <code>n</code> neighbours, so the time is O(n<sup>2</sup> &middot; 2<sup>n</sup>)."],
    time="O(n^2 * 2^n)", space="O(n * 2^n)",
    solution='''from collections import deque


def shortestWalkAllNodes(graph):
    n = len(graph)
    full = (1 << n) - 1
    if n == 1:
        return 0
    seen = [[False] * n for _ in range(1 << n)]
    dq = deque()
    for i in range(n):
        seen[1 << i][i] = True
        dq.append((1 << i, i, 0))
    while dq:
        mask, u, d = dq.popleft()
        for v in graph[u]:
            nm = mask | (1 << v)
            if nm == full:
                return d + 1
            if not seen[nm][v]:
                seen[nm][v] = True
                dq.append((nm, v, d + 1))
    return -1
''',
    tests=[[[[1, 2, 3], [0], [0], [0]]], [[[1], [0, 2, 4], [1, 3, 4], [2], [1, 2]]], [[[]]], [[[1], [0]]],
           [[[1, 2], [0, 2], [0, 1]]], [[[1], [0, 2], [1, 3], [2]]], [[[1, 2, 3], [0, 2, 3], [0, 1, 3], [0, 1, 2]]],
           [[[1, 3], [0, 2], [1, 3], [0, 2]]], [[[1, 2, 3, 4], [0], [0], [0], [0]]], [[[1], [0, 2, 3], [1], [1, 4], [3]]],
           [[[1], [0, 2], [1, 3, 4], [2], [2, 5], [4]]], [[[1, 5], [0, 2], [1, 3], [2, 4], [3, 5], [4, 0]]]],
)


def _path_graph(n):
    return [[j for j in (i - 1, i + 1) if 0 <= j < n] for i in range(n)]


def _from_edges(n, edges):
    adj = [set() for _ in range(n)]
    for a, b in edges:
        adj[a].add(b)
        adj[b].add(a)
    return [sorted(s) for s in adj]


def _rand_connected(r, n, extra):
    edges = []
    order = list(range(n))
    r.shuffle(order)
    for idx in range(1, n):
        edges.append((order[idx], order[r.randrange(idx)]))
    for _ in range(extra):
        a, b = r.randrange(n), r.randrange(n)
        if a != b:
            edges.append((a, b))
    return _from_edges(n, edges)


_r = rnd(7108)
p["tests"].append([_path_graph(12)])
p["tests"].append([[list(range(1, 12))] + [[0] for _ in range(11)]])
p["tests"].append([[[j for j in range(12) if j != i] for i in range(12)]])
p["tests"].append([_from_edges(12, [(i, (i + 1) % 12) for i in range(12)])])
p["tests"].append([_from_edges(12, [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (0, 6), (6, 7), (7, 8), (8, 9), (9, 10), (10, 11)])])
p["tests"].append([_from_edges(12, [(0, 1), (0, 2), (0, 3), (1, 4), (1, 5), (2, 6), (2, 7), (3, 8), (3, 9), (4, 10), (5, 11)])])
for _extra in (0, 3, 6, 12):
    p["tests"].append([_rand_connected(_r, 12, _extra)])
p["tests"].append([_rand_connected(_r, 11, 5)])
p["tests"].append([_rand_connected(_r, 10, 0)])


def _bfs_dist(graph, s):
    dist = [-1] * len(graph)
    dist[s] = 0
    q = [s]
    for u in q:
        for v in graph[u]:
            if dist[v] < 0:
                dist[v] = dist[u] + 1
                q.append(v)
    return dist


def b_walk(graph):
    n = len(graph)
    dist = [_bfs_dist(graph, s) for s in range(n)]
    best = None
    for perm in permutations(range(n)):
        total = sum(dist[perm[i]][perm[i + 1]] for i in range(n - 1))
        if best is None or total < best:
            best = total
    return best


def g_walk(r):
    n = r.randint(1, 6)
    return [_rand_connected(r, n, r.randint(0, 5))]


def v_walk(tests):
    for t in tests:
        g = t["args"][0]
        n = len(g)
        assert 1 <= n <= 12
        for i, nb in enumerate(g):
            assert len(set(nb)) == len(nb) and i not in nb and len(nb) < n
            for j in nb:
                assert 0 <= j < n and i in g[j]
        assert all(d >= 0 for d in _bfs_dist(g, 0)), "graph not connected"


CHECKS["shortest-walk-visiting-all-nodes"] = (b_walk, g_walk, "exact")
VALIDATE["shortest-walk-visiting-all-nodes"] = v_walk
