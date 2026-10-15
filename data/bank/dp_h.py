"""Problems: dynamic programming, 0/1 knapsack variants. See data/lib.py for the registry."""
from itertools import combinations, product

from lib import add, rnd, CHECKS, VALIDATE, gen_arr  # noqa: F401

TOPIC = "Dynamic Programming"
MOD = 10 ** 9 + 7


# ---------------------------------------------------------------- EASY

p = add(
    id="subset-sum-exists", title="Subset Sum Exists", diff="Easy", topic=TOPIC, tier="must",
    fn="subsetSumExists", params=[("nums", "int[]"), ("target", "int")], ret="bool", cmp="exact",
    desc="<p>Given an array <code>nums</code> of positive integers and a non-negative integer <code>target</code>, decide whether some group of elements of <code>nums</code> adds up to exactly <code>target</code>. Every element (every index) may be used at most once. The empty group has sum <code>0</code>, so <code>target = 0</code> is always reachable.</p><p>Return <code>true</code> if such a group exists and <code>false</code> otherwise.</p><pre>nums = [3, 34, 4, 12, 5, 2], target = 9  -> true   (4 + 5)\nnums = [3, 34, 4, 12, 5, 2], target = 30 -> false\nnums = [2, 4, 6, 8],         target = 7  -> false</pre>",
    constraints=["1 &le; nums.length &le; 300", "1 &le; nums[i] &le; 100", "0 &le; target &le; 30,000"],
    hints=["Trying every subset costs 2<sup>n</sup>, far too much. Think about which <em>sums</em> you can reach rather than which subsets you can build.",
           "Keep a boolean table <code>reach[s]</code>: can some subset of the elements seen so far add up to <code>s</code>? At the start only <code>reach[0]</code> is true.",
           "When an element <code>x</code> arrives, every reachable sum <code>s</code> makes <code>s + x</code> reachable too. Loop <code>s</code> from <code>target</code> down to <code>x</code> and set <code>reach[s] |= reach[s - x]</code>; going downward keeps the element from being used twice."],
    editorial=["This is the 0/1 knapsack in its purest form: the only question is which totals can be formed. Let <code>reach[s]</code> say whether some subset of the elements processed so far sums to <code>s</code>. Initially only <code>reach[0]</code> is true (the empty subset). For a new element <code>x</code>, a total <code>s</code> becomes reachable if <code>s - x</code> was reachable before this element, so <code>reach[s] = reach[s] or reach[s - x]</code>.",
               "The loop over <code>s</code> has to go from high to low. Then <code>reach[s - x]</code> is still the value from before the current element and the element is counted at most once; a loop going upward would reuse it. Total cost is O(n &middot; target) time and O(target) space.",
               "A neat speed-up stores the whole table in one big integer used as a bitset: <code>bits |= bits &lt;&lt; x</code> does the entire update at once, and the answer is bit number <code>target</code>. The reference solution does exactly that."],
    time="O(n * target)", space="O(target)",
    solution='''def subsetSumExists(nums, target):
    # bit s of `bits` is 1 when some subset of the elements seen so far sums to s
    bits = 1
    for x in nums:
        bits |= bits << x
    return (bits >> target) & 1 == 1
''',
    tests=[[[3, 34, 4, 12, 5, 2], 9], [[3, 34, 4, 12, 5, 2], 30], [[2, 4, 6, 8], 7], [[7], 7], [[7], 8], [[7], 0],
           [[1, 1, 1], 3], [[1, 1, 1], 4], [[5, 10, 15], 20], [[100, 100, 100], 250], [[100], 30000], [[2, 3], 1]],
)
_r = rnd(8101)
_a = [2 * _r.randint(1, 50) for _ in range(300)]
p["tests"].append([_a, 12345])
_a = [_r.randint(1, 100) for _ in range(300)]
p["tests"].append([_a, sum(_a[::2]) + 3])
p["tests"].append([_a, sum(_a)])
p["tests"].append([_a, sum(_a) + 1])
_a = [7 * _r.randint(1, 14) for _ in range(300)]
p["tests"].append([_a, 7 * 2000 + 3])
p["tests"].append([[100] * 300, 29900])


def b_subsetsum(nums, target):
    n = len(nums)
    for mask in range(1 << n):
        if sum(nums[i] for i in range(n) if mask >> i & 1) == target:
            return True
    return False


def g_subsetsum(r):
    n = r.randint(1, 10)
    return [[r.randint(1, 10) for _ in range(n)], r.randint(0, 45)]


def v_subsetsum(tests):
    for t in tests:
        nums, target = t["args"]
        assert 1 <= len(nums) <= 300 and all(1 <= x <= 100 for x in nums)
        assert 0 <= target <= 30000
    assert any(t["expected"] for t in tests) and not all(t["expected"] for t in tests)


CHECKS["subset-sum-exists"] = (b_subsetsum, g_subsetsum, "exact")
VALIDATE["subset-sum-exists"] = v_subsetsum

p = add(
    id="count-distinct-subset-sums", title="Count Distinct Subset Sums", diff="Easy", topic=TOPIC,
    fn="countDistinctSubsetSums", params=[("nums", "int[]")], ret="int", cmp="exact",
    desc="<p>Given an array <code>nums</code> of non-negative integers, consider the sum of every subset of its elements (a subset is chosen by index, and the empty subset has sum <code>0</code>). Different subsets can have the same sum.</p><p>Return how many <strong>different values</strong> occur as the sum of some subset.</p><pre>[1, 2, 5] -> 8    (sums 0, 1, 2, 3, 5, 6, 7, 8)\n[2, 2, 2] -> 4    (sums 0, 2, 4, 6)\n[0, 0]    -> 1    (only the sum 0)</pre>",
    constraints=["1 &le; nums.length &le; 200", "0 &le; nums[i] &le; 100"],
    hints=["Counting subsets is useless here because many subsets share a sum; you need to count sums.",
           "Maintain the set of sums that are reachable by the elements processed so far. Start with <code>{0}</code>.",
           "When element <code>x</code> comes, the new set is the old set together with <code>{s + x}</code> for every old <code>s</code>. The total never exceeds 20,000, so a boolean array (or a bitset) is enough. The answer is how many entries are true."],
    editorial=["The set of reachable sums only depends on the set from the previous step: after adding element <code>x</code> the reachable sums are the old sums (skip the element) plus the old sums shifted by <code>x</code> (take it). Because every sum lies between 0 and <code>sum(nums)</code> &le; 20,000, a boolean array indexed by sum represents the set, and one update costs O(sum). In total the cost is O(n &middot; sum).",
               "Zeros change nothing (shifting by 0 gives the same set), and duplicates are handled automatically because we track sums, never subsets. With a big-integer bitset the update is the single statement <code>bits |= bits &lt;&lt; x</code>, and the answer is the number of 1-bits."],
    time="O(n * sum)", space="O(sum)",
    solution='''def countDistinctSubsetSums(nums):
    bits = 1  # bit s is 1 when some subset sums to s
    for x in nums:
        bits |= bits << x
    return bin(bits).count("1")
''',
    tests=[[[1, 2, 5]], [[2, 2, 2]], [[0, 0]], [[0]], [[5]], [[1, 1, 1]], [[2, 4, 6]], [[1, 2, 4, 8]], [[3, 3, 3, 3]],
           [[100, 100, 100]], [[1, 100]], [[0, 7, 0, 7]]],
)
_r = rnd(8102)
p["tests"].append([[_r.randint(1, 100) for _ in range(200)]])
p["tests"].append([[100] * 200])
p["tests"].append([[3 * _r.randint(10, 33) for _ in range(200)]])
p["tests"].append([[_r.choice([0, 0, 50, 97, 100]) for _ in range(200)]])
p["tests"].append([[2 ** (i % 7) for i in range(14)] + [100] * 5])


def b_distinct(nums):
    n = len(nums)
    seen = set()
    for mask in range(1 << n):
        seen.add(sum(nums[i] for i in range(n) if mask >> i & 1))
    return len(seen)


def g_distinct(r):
    return [[r.randint(0, 9) for _ in range(r.randint(1, 11))]]


def v_distinct(tests):
    for t in tests:
        nums = t["args"][0]
        assert 1 <= len(nums) <= 200 and all(0 <= x <= 100 for x in nums)


CHECKS["count-distinct-subset-sums"] = (b_distinct, g_distinct, "exact")
VALIDATE["count-distinct-subset-sums"] = v_distinct


# -------------------------------------------------------------- MEDIUM

p = add(
    id="fewest-items-summing-to-target", title="Fewest Items Summing to Target", diff="Medium", topic=TOPIC,
    fn="fewestItemsForTarget", params=[("nums", "int[]"), ("target", "int")], ret="int", cmp="exact",
    desc="<p>You are given an array <code>nums</code> of positive integers and an integer <code>target</code>. Choose some of the elements, each index at most once, so that their sum is exactly <code>target</code>, and use as <strong>few</strong> elements as possible.</p><p>Return that minimum number of elements, or <code>-1</code> if no choice adds up to <code>target</code>. For <code>target = 0</code> the answer is <code>0</code>.</p><pre>nums = [2, 3, 5, 7], target = 10 -> 2    (3 + 7)\nnums = [4, 6, 1],    target = 5  -> 2    (4 + 1)\nnums = [4, 6],       target = 7  -> -1\nnums = [5, 5, 5],    target = 15 -> 3</pre><p>Unlike the unbounded coin change problem, an element cannot be used twice, even if you would like to.</p>",
    constraints=["1 &le; nums.length &le; 100", "1 &le; nums[i] &le; 100", "0 &le; target &le; 5,000"],
    hints=["This looks like Coin Change, but each element is single-use. What changes in the DP?",
           "Let <code>best[s]</code> be the fewest elements, among those processed so far, that sum to <code>s</code> (infinity if impossible). <code>best[0] = 0</code>.",
           "For each element <code>x</code>, loop <code>s</code> from <code>target</code> down to <code>x</code> and set <code>best[s] = min(best[s], best[s - x] + 1)</code>. The downward direction is what prevents reusing <code>x</code>. The answer is <code>best[target]</code>, or -1 if it is still infinity."],
    editorial=["Use a 0/1 knapsack in which every element has weight <code>x</code> and cost 1, and the knapsack has to be filled <em>exactly</em>. Define <code>best[s]</code> as the minimum number of already processed elements whose sum is <code>s</code>, with <code>best[0] = 0</code> and infinity elsewhere. An element <code>x</code> improves <code>best[s]</code> to <code>best[s - x] + 1</code> when that is smaller.",
               "Iterating <code>s</code> downward makes sure <code>best[s - x]</code> comes from before the current element. Iterating upward would let the same element be taken repeatedly, which is the unbounded Coin Change recurrence and would give wrong answers whenever a value repeats in the optimal solution (for example <code>[5]</code> with target 10 must give -1, not 2). Time O(n &middot; target), space O(target)."],
    time="O(n * target)", space="O(target)",
    solution='''def fewestItemsForTarget(nums, target):
    INF = float("inf")
    best = [INF] * (target + 1)
    best[0] = 0
    for x in nums:
        for s in range(target, x - 1, -1):
            if best[s - x] + 1 < best[s]:
                best[s] = best[s - x] + 1
    return -1 if best[target] == INF else best[target]
''',
    tests=[[[2, 3, 5, 7], 10], [[4, 6, 1], 5], [[4, 6], 7], [[5, 5, 5], 15], [[5], 10], [[5], 0], [[9], 9], [[1, 1, 1, 1], 3],
           [[1, 2, 3, 4, 5], 15], [[1, 2, 3, 4, 5], 16], [[6, 7, 8], 14], [[100] * 3, 200]],
)
_r = rnd(8103)
p["tests"].append([[1] * 100, 100])
p["tests"].append([[1] * 100, 101])
_a = [_r.randint(1, 100) for _ in range(100)]
p["tests"].append([_a, sum(_a[::3])])
_a = [_r.randint(1, 100) for _ in range(100)]
p["tests"].append([_a, 4999])
p["tests"].append([[2 * _r.randint(1, 50) for _ in range(100)], 4001])


def b_fewest(nums, target):
    n = len(nums)
    best = None
    for k in range(n + 1):
        for comb in combinations(range(n), k):
            if sum(nums[i] for i in comb) == target:
                return k
    return -1


def g_fewest(r):
    return [[r.randint(1, 9) for _ in range(r.randint(1, 10))], r.randint(0, 45)]


def v_fewest(tests):
    for t in tests:
        nums, target = t["args"]
        assert 1 <= len(nums) <= 100 and all(1 <= x <= 100 for x in nums)
        assert 0 <= target <= 5000
    assert any(t["expected"] == -1 for t in tests) and any(t["expected"] > 1 for t in tests)


CHECKS["fewest-items-summing-to-target"] = (b_fewest, g_fewest, "exact")
VALIDATE["fewest-items-summing-to-target"] = v_fewest

p = add(
    id="best-value-at-most-k-items", title="Best Value With at Most K Items", diff="Medium", topic=TOPIC,
    fn="bestValueAtMostKItems", params=[("weights", "int[]"), ("values", "int[]"), ("k", "int"), ("capacity", "int")], ret="int", cmp="exact",
    desc="<p>A hiker may pack at most <code>k</code> of <code>n</code> distinct items, and the total weight must not exceed <code>capacity</code>. Item <code>i</code> weighs <code>weights[i]</code> and is worth <code>values[i]</code>; each item can be taken at most once.</p><p>Return the largest total value the hiker can pack. Taking nothing is allowed, so the answer is never negative.</p><pre>weights = [3, 4, 2, 5], values = [40, 50, 30, 70], k = 2, capacity = 8 -> 110   (items 0 and 3)\nweights = [3, 4, 2, 5], values = [40, 50, 30, 70], k = 3, capacity = 9 -> 120   (items 0, 1, 2)\nweights = [3, 4, 2, 5], values = [40, 50, 30, 70], k = 1, capacity = 9 -> 70</pre>",
    constraints=["1 &le; weights.length = values.length &le; 50", "1 &le; weights[i] &le; 100", "0 &le; values[i] &le; 1,000,000", "1 &le; k &le; 25", "0 &le; capacity &le; 400"],
    hints=["A plain knapsack table has one dimension (weight). The extra limit on the number of items asks for a second dimension.",
           "Let <code>best[j][c]</code> be the largest value using at most <code>j</code> items of total weight at most <code>c</code>, over the items processed so far.",
           "For each item (weight <code>w</code>, value <code>v</code>), update <code>best[j][c] = max(best[j][c], best[j-1][c-w] + v)</code> with <code>j</code> going from <code>k</code> down to 1 (and <code>c</code> downward as well, or by using the old row), so every item is used once. Answer: <code>best[k][capacity]</code>."],
    editorial=["Add a second axis to the knapsack: the number of items used. Define <code>best[j][c]</code> as the maximum value obtainable from the items seen so far using <em>at most</em> <code>j</code> of them with total weight at most <code>c</code>. Starting with all zeros already encodes the empty choice, and because both limits are &quot;at most&quot;, the table is monotone in <code>j</code> and <code>c</code>.",
               "Processing an item with weight <code>w</code> and value <code>v</code> creates the candidate <code>best[j-1][c-w] + v</code> for every <code>j &ge; 1</code> and <code>c &ge; w</code>. The candidate reads a row with one fewer item that must still describe the state <em>before</em> this item, so the rows are visited from <code>j = k</code> downward (and within a row <code>c</code> is read from the previous row, never from itself). The cost is O(n &middot; k &middot; capacity) time and O(k &middot; capacity) space. The same pattern handles any problem with two independent limits, such as a weight limit and an item-count limit."],
    time="O(n * k * capacity)", space="O(k * capacity)",
    solution='''def bestValueAtMostKItems(weights, values, k, capacity):
    best = [[0] * (capacity + 1) for _ in range(k + 1)]
    for w, v in zip(weights, values):
        if w > capacity:
            continue
        for j in range(k, 0, -1):
            prev = best[j - 1]
            row = best[j]
            # row[c] = max(row[c], prev[c - w] + v) for every c >= w
            row[w:] = [x if x >= y + v else y + v for x, y in zip(row[w:], prev)]
    return best[k][capacity]
''',
    tests=[[[3, 4, 2, 5], [40, 50, 30, 70], 2, 8], [[3, 4, 2, 5], [40, 50, 30, 70], 3, 9], [[3, 4, 2, 5], [40, 50, 30, 70], 1, 9],
           [[5], [10], 1, 4], [[5], [10], 1, 5], [[1, 1, 1], [5, 6, 7], 2, 0], [[1, 1, 1], [5, 6, 7], 2, 3],
           [[1, 1, 1], [5, 6, 7], 25, 3], [[2, 2, 2, 2], [0, 0, 0, 0], 2, 8], [[10, 1, 1, 1], [100, 3, 3, 3], 2, 11],
           [[10, 1, 1, 1], [100, 3, 3, 3], 3, 11], [[6, 5, 4, 3, 2], [9, 8, 7, 6, 5], 2, 9]],
)
_r = rnd(8104)
p["tests"].append([[_r.randint(1, 100) for _ in range(50)], [_r.randint(0, 10 ** 6) for _ in range(50)], 25, 400])
p["tests"].append([[_r.randint(1, 20) for _ in range(50)], [_r.randint(0, 1000) for _ in range(50)], 25, 400])
p["tests"].append([[_r.randint(1, 20) for _ in range(50)], [_r.randint(0, 1000) for _ in range(50)], 7, 400])
p["tests"].append([[17] * 50, [10 ** 6] * 50, 25, 400])
p["tests"].append([[1] * 50, [_r.randint(0, 10 ** 6) for _ in range(50)], 12, 20])


def b_bestk(weights, values, k, capacity):
    n = len(weights)
    best = 0
    for mask in range(1 << n):
        cnt = bin(mask).count("1")
        if cnt > k:
            continue
        if sum(weights[i] for i in range(n) if mask >> i & 1) <= capacity:
            best = max(best, sum(values[i] for i in range(n) if mask >> i & 1))
    return best


def g_bestk(r):
    n = r.randint(1, 9)
    return [[r.randint(1, 8) for _ in range(n)], [r.randint(0, 10) for _ in range(n)], r.randint(1, 5), r.randint(0, 25)]


def v_bestk(tests):
    for t in tests:
        w, v, k, c = t["args"]
        assert 1 <= len(w) <= 50 and len(w) == len(v)
        assert all(1 <= x <= 100 for x in w) and all(0 <= x <= 10 ** 6 for x in v)
        assert 1 <= k <= 25 and 0 <= c <= 400


CHECKS["best-value-at-most-k-items"] = (b_bestk, g_bestk, "exact")
VALIDATE["best-value-at-most-k-items"] = v_bestk

p = add(
    id="bounded-knapsack-with-copies", title="Bounded Knapsack with Limited Copies", diff="Medium", topic=TOPIC, tier="extra",
    fn="boundedKnapsack", params=[("weights", "int[]"), ("values", "int[]"), ("counts", "int[]"), ("capacity", "int")], ret="int", cmp="exact",
    desc="<p>A warehouse stocks <code>n</code> kinds of goods. Every unit of kind <code>i</code> weighs <code>weights[i]</code> and is worth <code>values[i]</code>, and exactly <code>counts[i]</code> units of that kind are available. A truck can load any number of units of each kind, up to what is available, as long as the total weight stays within <code>capacity</code>.</p><p>Return the maximum total value that can be loaded.</p><pre>weights = [2, 3], values = [3, 5], counts = [3, 2], capacity = 10 -> 16   (two units of kind 1 and two of kind 0)\nweights = [4],    values = [7], counts = [2], capacity = 9       -> 14\nweights = [4],    values = [7], counts = [5], capacity = 7       -> 7</pre>",
    constraints=["1 &le; weights.length = values.length = counts.length &le; 50", "1 &le; weights[i] &le; 60", "0 &le; values[i] &le; 100,000", "1 &le; counts[i] &le; 100", "0 &le; capacity &le; 2,000"],
    hints=["Treating each unit as a separate 0/1 item works but creates up to 5,000 items. Can you represent &quot;up to c copies&quot; with far fewer 0/1 items?",
           "Any number from 0 to c can be written as a sum of the pieces 1, 2, 4, ... plus one remainder piece. Splitting c = 13 into 1, 2, 4, 6 gives every count from 0 to 13.",
           "Replace kind i by the bundles: a bundle of size m has weight <code>m * w</code> and value <code>m * v</code>. Run an ordinary 0/1 knapsack on all bundles."],
    editorial=["The straightforward idea is to expand every kind into <code>counts[i]</code> identical 0/1 items, which can be slow when counts are large. Binary splitting keeps the expansion logarithmic: write <code>c = 1 + 2 + 4 + ... + 2<sup>t-1</sup> + r</code> where <code>r</code> is the leftover so that the total is exactly <code>c</code>. Any number of copies between 0 and <code>c</code> is a sum of a subset of these bundle sizes, and no subset can exceed <code>c</code>.",
               "Each bundle becomes one 0/1 item with weight <code>size * w</code> and value <code>size * v</code>. The standard downward 0/1 knapsack then finds the best load. There are at most about <code>n &middot; log(counts)</code> bundles, so the time is O(n &middot; log(c) &middot; capacity). (A monotonic-queue technique can reach O(n &middot; capacity), but binary splitting is simpler and fast enough.)"],
    time="O(n * log(c) * capacity)", space="O(capacity)",
    solution='''def boundedKnapsack(weights, values, counts, capacity):
    best = [0] * (capacity + 1)
    for w, v, c in zip(weights, values, counts):
        size = 1
        while c > 0:
            take = min(size, c)
            c -= take
            size *= 2
            bw, bv = w * take, v * take
            if bw > capacity:
                continue
            best = best[:bw] + [max(a, b + bv) for a, b in zip(best[bw:], best)]
    return best[capacity]
''',
    tests=[[[2, 3], [3, 5], [3, 2], 10], [[4], [7], [2], 9], [[4], [7], [5], 7], [[5], [9], [3], 4], [[1], [0], [1], 0],
           [[1], [5], [100], 100], [[1], [5], [100], 2000], [[3, 5], [4, 7], [1, 1], 7], [[3, 5], [4, 7], [1, 1], 8],
           [[2, 2, 2], [1, 2, 3], [1, 1, 1], 4], [[10, 20, 30], [60, 100, 120], [1, 1, 1], 50], [[10, 20, 30], [60, 100, 120], [3, 3, 3], 50]],
)
_r = rnd(8105)
p["tests"].append([[_r.randint(1, 60) for _ in range(50)], [_r.randint(0, 100000) for _ in range(50)], [_r.randint(1, 100) for _ in range(50)], 2000])
p["tests"].append([[_r.randint(1, 8) for _ in range(50)], [_r.randint(0, 1000) for _ in range(50)], [100] * 50, 2000])
p["tests"].append([[60] * 50, [100000] * 50, [100] * 50, 2000])
_w = [_r.randint(20, 60) for _ in range(50)]
p["tests"].append([_w, [x * 1000 + _r.randint(0, 9) for x in _w], [_r.randint(1, 100) for _ in range(50)], 1999])
p["tests"].append([[1] * 50, [_r.randint(0, 100000) for _ in range(50)], [100] * 50, 777])


def b_bounded(weights, values, counts, capacity):
    n = len(weights)
    memo = {}

    def go(i, cap):
        if i == n:
            return 0
        key = (i, cap)
        if key not in memo:
            memo[key] = max(k * values[i] + go(i + 1, cap - k * weights[i])
                            for k in range(min(counts[i], cap // weights[i]) + 1))
        return memo[key]

    return go(0, capacity)


def g_bounded(r):
    n = r.randint(1, 5)
    return [[r.randint(1, 7) for _ in range(n)], [r.randint(0, 10) for _ in range(n)], [r.randint(1, 5) for _ in range(n)], r.randint(0, 40)]


def v_bounded(tests):
    for t in tests:
        w, v, c, cap = t["args"]
        assert 1 <= len(w) <= 50 and len(w) == len(v) == len(c)
        assert all(1 <= x <= 60 for x in w) and all(0 <= x <= 100000 for x in v) and all(1 <= x <= 100 for x in c)
        assert 0 <= cap <= 2000


CHECKS["bounded-knapsack-with-copies"] = (b_bounded, g_bounded, "exact")
VALIDATE["bounded-knapsack-with-copies"] = v_bounded

p = add(
    id="grouped-knapsack-one-per-group", title="Grouped Knapsack: One Item per Group", diff="Medium", topic=TOPIC,
    fn="groupedKnapsack", params=[("items", "int[][]"), ("capacity", "int")], ret="int", cmp="exact",
    desc="<p>A shop sells items in product families. Each element of <code>items</code> is a triple <code>[group, weight, value]</code>: the item belongs to family <code>group</code>, weighs <code>weight</code> and is worth <code>value</code>. Items of the same family are alternatives of each other, so you may pick <strong>at most one item from each family</strong> (and none from a family is fine). Items of one family can appear anywhere in the array, not necessarily next to each other.</p><p>The total weight of the chosen items must not exceed <code>capacity</code>. Return the maximum total value.</p><pre>items = [[0,2,3], [0,3,4], [1,4,6], [1,2,2]], capacity = 5 -> 6   (item [1,4,6] alone)\nitems = [[0,2,3], [0,3,4], [1,4,6], [1,2,2]], capacity = 6 -> 9   ([0,2,3] and [1,4,6])\nitems = [[7,1,5], [7,1,9]],                   capacity = 5 -> 9   (only one of the two may be used)</pre>",
    constraints=["1 &le; items.length &le; 150", "items[i] = [group, weight, value] with 0 &le; group &le; 100, 1 &le; weight &le; 100, 0 &le; value &le; 100,000", "0 &le; capacity &le; 1,000"],
    hints=["The usual item-by-item loop would allow two items of the same family. What should be the unit of the outer loop instead?",
           "Process one family at a time. Let <code>dp[c]</code> be the best value using the families handled so far with total weight at most <code>c</code>.",
           "For a family, build a new table from the old one: <code>new[c] = max(old[c], old[c - w] + v)</code> over every item <code>(w, v)</code> of the family. Always read from <code>old</code>, so two items of the same family are never combined."],
    editorial=["Group the triples by their family id. The knapsack state after finishing some families is the usual array <code>dp[c]</code> (best value with weight at most <code>c</code>). For the next family we have three kinds of choices: take nothing from it, or take exactly one of its items. Hence <code>new[c] = max(dp[c], max over items (w, v) of dp[c - w] + v)</code>, and every candidate reads the table <em>from before</em> the family, which makes it impossible to combine two items of the same family.",
               "Computing the new table into a separate array (or iterating capacity downward and looping over the family's items in the innermost loop) both work. Each item is looked at once for each capacity, giving O(n &middot; capacity) time and O(capacity) space. This &quot;group knapsack&quot; pattern shows up whenever choices are mutually exclusive, for example choosing one size per product."],
    time="O(n * capacity)", space="O(capacity)",
    solution='''def groupedKnapsack(items, capacity):
    groups = {}
    for g, w, v in items:
        groups.setdefault(g, []).append((w, v))
    dp = [0] * (capacity + 1)
    for members in groups.values():
        new = dp[:]  # taking nothing from this family
        for w, v in members:
            for c in range(w, capacity + 1):
                cand = dp[c - w] + v  # dp is the table from before this family
                if cand > new[c]:
                    new[c] = cand
        dp = new
    return dp[capacity]
''',
    tests=[[[[0, 2, 3], [0, 3, 4], [1, 4, 6], [1, 2, 2]], 5], [[[0, 2, 3], [0, 3, 4], [1, 4, 6], [1, 2, 2]], 6], [[[7, 1, 5], [7, 1, 9]], 5],
           [[[0, 5, 10]], 4], [[[0, 5, 10]], 5], [[[3, 1, 0]], 0], [[[0, 1, 1], [1, 1, 1], [2, 1, 1]], 2],
           [[[0, 1, 1], [1, 1, 1], [0, 1, 1], [1, 1, 1]], 4], [[[5, 3, 8], [2, 3, 9], [5, 2, 7], [2, 4, 12], [9, 1, 1]], 6],
           [[[1, 10, 100], [2, 10, 100]], 15], [[[4, 2, 5], [4, 2, 6], [4, 2, 7]], 100], [[[0, 100, 100000]], 1000]],
)
_r = rnd(8106)
p["tests"].append([[[_r.randint(0, 100), _r.randint(1, 100), _r.randint(0, 100000)] for _ in range(150)], 1000])
p["tests"].append([[[_r.randint(0, 10), _r.randint(1, 100), _r.randint(0, 100000)] for _ in range(150)], 1000])
p["tests"].append([[[i % 5, _r.randint(1, 30), _r.randint(0, 1000)] for i in range(150)], 90])
p["tests"].append([[[0, _r.randint(1, 100), _r.randint(0, 100000)] for _ in range(150)], 1000])
p["tests"].append([[[i, 7, _r.randint(0, 100000)] for i in range(101)] + [[_r.randint(0, 100), 7, 5] for _ in range(49)], 700])


def b_grouped(items, capacity):
    groups = {}
    for g, w, v in items:
        groups.setdefault(g, []).append((w, v))
    options = [[None] + members for members in groups.values()]
    best = 0
    for pick in product(*options):
        wt = sum(x[0] for x in pick if x)
        if wt <= capacity:
            best = max(best, sum(x[1] for x in pick if x))
    return best


def g_grouped(r):
    n = r.randint(1, 8)
    return [[[r.randint(0, 3), r.randint(1, 6), r.randint(0, 10)] for _ in range(n)], r.randint(0, 20)]


def v_grouped(tests):
    for t in tests:
        items, cap = t["args"]
        assert 1 <= len(items) <= 150 and 0 <= cap <= 1000
        for g, w, v in items:
            assert 0 <= g <= 100 and 1 <= w <= 100 and 0 <= v <= 100000


CHECKS["grouped-knapsack-one-per-group"] = (b_grouped, g_grouped, "exact")
VALIDATE["grouped-knapsack-one-per-group"] = v_grouped

p = add(
    id="smallest-subset-sum-divisible-by-m", title="Smallest Subset With Sum Divisible by M", diff="Medium", topic=TOPIC, tier="extra",
    fn="smallestSubsetDivisibleByM", params=[("nums", "int[]"), ("m", "int")], ret="int", cmp="exact",
    desc="<p>Given an array <code>nums</code> of positive integers and an integer <code>m</code>, look for a <strong>non-empty</strong> subset of the elements (chosen by index) whose sum is divisible by <code>m</code>.</p><p>Return the smallest possible size of such a subset, or <code>-1</code> if there is none.</p><pre>nums = [3, 1, 4, 1, 5], m = 5 -> 1    (the element 5)\nnums = [3, 5, 6],       m = 7 -> 3    (3 + 5 + 6 = 14)\nnums = [2, 4],          m = 8 -> -1   (sums are 2, 4 and 6)</pre>",
    constraints=["1 &le; nums.length &le; 500", "1 &le; nums[i] &le; 1,000,000", "1 &le; m &le; 500"],
    hints=["Only the remainder of the running sum modulo <code>m</code> matters. How many different remainders are there?",
           "Let <code>dp[r]</code> be the fewest elements of a non-empty subset (among the elements seen so far) whose sum has remainder <code>r</code>. Update it element by element, always reading the table from before the element.",
           "For element <code>x</code>: first copy the table, then <code>new[x % m] = min(new[x % m], 1)</code>, and for every <code>r</code> with <code>dp[r]</code> finite, <code>new[(r + x) % m] = min(new[(r + x) % m], dp[r] + 1)</code>. The answer is <code>dp[0]</code>."],
    editorial=["Two subsets with the same remainder are interchangeable for the future, so the knapsack can be taken modulo <code>m</code>: the &quot;weight&quot; of an element is <code>x mod m</code> and the &quot;capacity&quot; wraps around. Define <code>dp[r]</code> as the minimum size of a non-empty subset of the processed elements with sum &equiv; <code>r</code> (mod <code>m</code>), infinity if none exists.",
               "For each element <code>x</code> we create a new table: copy the old one (do not take <code>x</code>), try the subset <code>{x}</code> on its own, and extend every existing subset by <code>x</code>, which moves the remainder from <code>r</code> to <code>(r + x) mod m</code> and adds one to the size. The answer is <code>dp[0]</code>; it counts only non-empty subsets because the empty subset is never inserted. Time O(n &middot; m), space O(m).",
               "A side note: if <code>n &ge; m</code> a valid subset always exists (a pigeonhole argument on prefix sums), but the answer can still be larger than 1, so the DP is needed to find the smallest."],
    time="O(n * m)", space="O(m)",
    solution='''def smallestSubsetDivisibleByM(nums, m):
    INF = float("inf")
    dp = [INF] * m  # dp[r]: fewest elements in a non-empty subset with sum % m == r
    for x in nums:
        new = dp[:]
        xr = x % m
        if new[xr] > 1:
            new[xr] = 1
        for r in range(m):
            if dp[r] != INF:
                t = (r + xr) % m
                if dp[r] + 1 < new[t]:
                    new[t] = dp[r] + 1
        dp = new
    return -1 if dp[0] == INF else dp[0]
''',
    tests=[[[3, 1, 4, 1, 5], 5], [[3, 5, 6], 7], [[2, 4], 8], [[7], 7], [[7], 3], [[1], 1], [[5, 5, 5], 1], [[2, 2, 2], 6],
           [[4, 4, 4, 4], 6], [[1000000, 999999], 2], [[3, 3, 3, 3, 3], 15], [[1, 2, 4, 8], 16]],
)
_r = rnd(8107)
p["tests"].append([[2 * _r.randint(1, 500000) for _ in range(500)], 499])
p["tests"].append([[_r.randint(1, 10 ** 6) for _ in range(500)], 500])
p["tests"].append([[_r.randint(1, 10 ** 6) for _ in range(300)], 499])
p["tests"].append([[17 * _r.randint(1, 58000) + 1 for _ in range(500)], 17 * 29])
p["tests"].append([[499 * _r.randint(1, 2000) + 1 for _ in range(500)], 499])
p["tests"].append([[499 * _r.randint(1, 2000) + 1 for _ in range(498)], 499])
p["tests"].append([[6 * _r.randint(1, 100000) + 3 for _ in range(500)], 500])


def b_divm(nums, m):
    n = len(nums)
    for k in range(1, n + 1):
        for comb in combinations(range(n), k):
            if sum(nums[i] for i in comb) % m == 0:
                return k
    return -1


def g_divm(r):
    m = r.randint(1, 12)
    n = r.randint(1, 9)
    return [[r.randint(1, 30) * r.choice([1, 1, 2, 3]) for _ in range(n)], m]


def v_divm(tests):
    for t in tests:
        nums, m = t["args"]
        assert 1 <= len(nums) <= 500 and all(1 <= x <= 10 ** 6 for x in nums) and 1 <= m <= 500
    assert any(t["expected"] == -1 for t in tests) and any(t["expected"] >= 3 for t in tests)


CHECKS["smallest-subset-sum-divisible-by-m"] = (b_divm, g_divm, "exact")
VALIDATE["smallest-subset-sum-divisible-by-m"] = v_divm

p = add(
    id="count-k-item-subsets-with-sum", title="Count K-Element Subsets With Given Sum", diff="Medium", topic=TOPIC,
    fn="countKItemSubsets", params=[("nums", "int[]"), ("k", "int"), ("target", "int")], ret="int", cmp="exact",
    desc="<p>Given an array <code>nums</code> of non-negative integers, count the subsets that contain <strong>exactly <code>k</code> elements</strong> and whose elements add up to exactly <code>target</code>. A subset is chosen by index, so equal values at different positions give different subsets.</p><p>The count can be large; return it modulo <code>1,000,000,007</code>.</p><pre>nums = [1, 2, 3, 4, 5], k = 2, target = 6 -> 2    ({1,5} and {2,4})\nnums = [2, 2, 2, 2],    k = 2, target = 4 -> 6    (any two of the four 2s)\nnums = [0, 0, 3],       k = 2, target = 3 -> 2    ({0,3} using either zero)</pre>",
    constraints=["1 &le; nums.length &le; 50", "0 &le; nums[i] &le; 40", "1 &le; k &le; 25", "0 &le; target &le; 500"],
    hints=["Counting subsets with a given sum is a standard DP. Now there is a second condition: the number of chosen elements.",
           "Let <code>ways[j][s]</code> be the number of subsets with exactly <code>j</code> elements and sum <code>s</code>, among the elements seen so far. <code>ways[0][0] = 1</code>.",
           "For each element <code>x</code>, update <code>ways[j][s] += ways[j-1][s-x]</code> with <code>j</code> going from <code>k</code> down to 1 so that the element is used once. Reduce modulo 1,000,000,007. The answer is <code>ways[k][target]</code>."],
    editorial=["Extend the counting knapsack by one more axis. <code>ways[j][s]</code> counts the subsets of the processed elements that have exactly <code>j</code> elements and sum exactly <code>s</code>. The empty subset gives <code>ways[0][0] = 1</code>. When an element <code>x</code> is added, every subset counted in <code>ways[j-1][s-x]</code> can be extended by <code>x</code> to a subset counted in <code>ways[j][s]</code>, so <code>ways[j][s]</code> grows by that amount.",
               "To use each element once, the rows are updated from <code>j = k</code> down to <code>1</code>, so the row <code>j - 1</code> being read still reflects the situation before the current element. Elements equal to 0 are handled correctly: they extend a subset without changing the sum, and each zero is a different index. The count is taken modulo 1,000,000,007. Time O(n &middot; k &middot; target), space O(k &middot; target)."],
    time="O(n * k * target)", space="O(k * target)",
    solution='''def countKItemSubsets(nums, k, target):
    MOD = 10 ** 9 + 7
    ways = [[0] * (target + 1) for _ in range(k + 1)]
    ways[0][0] = 1
    for x in nums:
        if x > target:
            continue
        for j in range(k, 0, -1):
            prev = ways[j - 1]
            row = ways[j]
            for s in range(x, target + 1):
                if prev[s - x]:
                    row[s] = (row[s] + prev[s - x]) % MOD
    return ways[k][target]
''',
    tests=[[[1, 2, 3, 4, 5], 2, 6], [[2, 2, 2, 2], 2, 4], [[0, 0, 3], 2, 3], [[5], 1, 5], [[5], 1, 4], [[5], 2, 5], [[0], 1, 0],
           [[0, 0, 0, 0], 3, 0], [[1, 1, 1, 1, 1, 1], 3, 3], [[1, 2, 3, 4, 5], 5, 15], [[1, 2, 3, 4, 5], 3, 100], [[40, 40, 40], 2, 80]],
)
_r = rnd(8108)
p["tests"].append([[_r.randint(0, 40) for _ in range(50)], 25, 500])
p["tests"].append([[20] * 50, 25, 500])
p["tests"].append([[_r.randint(0, 40) for _ in range(50)], 10, 200])
p["tests"].append([[0] * 50, 25, 0])
p["tests"].append([[_r.randint(0, 3) for _ in range(50)], 25, 38])
p["tests"].append([[_r.randint(10, 30) for _ in range(50)], 20, 400])


def b_countk(nums, k, target):
    return sum(1 for comb in combinations(range(len(nums)), k) if sum(nums[i] for i in comb) == target) % MOD


def g_countk(r):
    n = r.randint(1, 10)
    return [[r.randint(0, 6) for _ in range(n)], r.randint(1, 6), r.randint(0, 25)]


def v_countk(tests):
    for t in tests:
        nums, k, target = t["args"]
        assert 1 <= len(nums) <= 50 and all(0 <= x <= 40 for x in nums)
        assert 1 <= k <= 25 and 0 <= target <= 500
        assert 0 <= t["expected"] < MOD
    assert any(t["expected"] > 10 ** 9 for t in tests) or any(t["expected"] > 10 ** 6 for t in tests)


CHECKS["count-k-item-subsets-with-sum"] = (b_countk, g_countk, "exact")
VALIDATE["count-k-item-subsets-with-sum"] = v_countk


# ---------------------------------------------------------------- HARD

p = add(
    id="removable-elements-for-equal-partition", title="Removable Elements for an Equal Partition", diff="Hard", topic=TOPIC, tier="extra",
    fn="countRemovableElements", params=[("nums", "int[]")], ret="int", cmp="exact",
    desc="<p>You are given an array <code>nums</code> of positive integers. For each index <code>i</code>, imagine deleting the element <code>nums[i]</code> (only that one) and looking at the remaining <code>n - 1</code> elements. Index <code>i</code> is <strong>removable</strong> if those remaining elements can be split into two groups with exactly the same sum, where every remaining element goes into exactly one of the two groups.</p><p>Return the number of removable indices. Equal values at different indices are counted separately.</p><pre>[2, 2, 2]    -> 3   (any removal leaves [2, 2])\n[1, 1, 2]    -> 1   (only removing the 2 leaves [1, 1]; removing a 1 leaves [1, 2])\n[1, 2, 3]    -> 0   (no remaining pair has equal parts)\n[1, 1, 2, 4] -> 1   (removing 4 leaves [1, 1, 2] = 2 + 2)</pre>",
    constraints=["2 &le; nums.length &le; 200", "1 &le; nums[i] &le; 50"],
    hints=["For one fixed index the question is exactly Partition Equal Subset Sum. Doing that from scratch for every index is correct, just slow. Can you share work between indices?",
           "Removing element <code>i</code> only matters if the sum of the rest is even; then you need a subset of the other elements with sum equal to half of it. So you need &quot;is sum s reachable using all elements except i&quot;.",
           "Divide and conquer on the index range: to answer for all i in [l, r), first add the elements of one half to the reachable-sum set, then recurse into the other half, and the other way round. Each element is added O(log n) times in total."],
    editorial=["For a fixed index <code>i</code> the remaining sum is <code>S - nums[i]</code>. If that is odd the index is not removable. Otherwise we need a subset of the other elements with sum exactly <code>(S - nums[i]) / 2</code>: the standard subset-sum DP. Running it separately for each index costs O(n<sup>2</sup> &middot; S).",
               "The shared work can be recovered with a &quot;delete one element&quot; divide and conquer. Define <code>solve(l, r, reach)</code>, where <code>reach</code> is the set of sums achievable using all elements <em>outside</em> the range <code>[l, r)</code>. If <code>r - l == 1</code>, the set is exactly the set of sums available without element <code>l</code>, and we test the target there. Otherwise split the range at <code>mid</code>: for the left half, add the elements of <code>[mid, r)</code> to <code>reach</code> and recurse; for the right half, add the elements of <code>[l, mid)</code> and recurse. Every element is inserted into a sum-set once per recursion level, so the total number of insertions is O(n log n) and the time is O(n log n &middot; S) (or O(n log n &middot; S / 64) with bitsets).",
               "Only sums up to S / 2 are ever needed, which halves the table. With the limits here (S &le; 10,000) the divide-and-conquer version needs roughly 200 &middot; 8 &middot; 5,000 = 8 million basic steps."],
    time="O(n log n * S)", space="O(S log n)",
    solution='''def countRemovableElements(nums):
    n = len(nums)
    total = sum(nums)
    limit = total // 2
    mask = (1 << (limit + 1)) - 1
    answer = 0

    def solve(lo, hi, bits):
        # bits: sums reachable using only elements outside [lo, hi)
        nonlocal answer
        if hi - lo == 1:
            rest = total - nums[lo]
            if rest % 2 == 0 and (bits >> (rest // 2)) & 1:
                answer += 1
            return
        mid = (lo + hi) // 2
        left = bits
        for x in nums[mid:hi]:
            left |= left << x
        solve(lo, mid, left & mask)
        right = bits
        for x in nums[lo:mid]:
            right |= right << x
        solve(mid, hi, right & mask)

    solve(0, n, 1)
    return answer
''',
    tests=[[[2, 2, 2]], [[1, 1, 2]], [[1, 2, 3]], [[1, 1, 2, 4]], [[1, 1]], [[5, 5]], [[1, 2]], [[3, 3, 3, 3]], [[1, 1, 1, 1, 1]],
           [[1, 2, 3, 4, 5, 6]], [[50, 50, 50]], [[1, 1, 1, 7]]],
)
_r = rnd(8109)
p["tests"].append([[_r.randint(1, 50) for _ in range(200)]])
p["tests"].append([[50] * 200])
p["tests"].append([[2 * _r.randint(1, 25) for _ in range(200)]])
p["tests"].append([[_r.randint(1, 50) for _ in range(199)] + [1]])
p["tests"].append([[50] * 199 + [49]])
_a = [_r.randint(40, 50) for _ in range(120)] + [_r.randint(1, 5) for _ in range(80)]
_r.shuffle(_a)
p["tests"].append([_a])


def b_removable(nums):
    cnt = 0
    for i in range(len(nums)):
        rest = nums[:i] + nums[i + 1:]
        s = sum(rest)
        if s % 2:
            continue
        sums = {0}
        for x in rest:
            sums |= {t + x for t in sums}
        if s // 2 in sums:
            cnt += 1
    return cnt


def g_removable(r):
    return [[r.randint(1, 9) for _ in range(r.randint(2, 10))]]


def v_removable(tests):
    for t in tests:
        nums = t["args"][0]
        assert 2 <= len(nums) <= 200 and all(1 <= x <= 50 for x in nums)
        assert sum(nums) <= 10000
    assert any(t["expected"] == 0 for t in tests) and any(t["expected"] > 5 for t in tests)


CHECKS["removable-elements-for-equal-partition"] = (b_removable, g_removable, "exact")
VALIDATE["removable-elements-for-equal-partition"] = v_removable

p = add(
    id="lexicographically-smallest-subset-for-target", title="Lexicographically Smallest Subset for a Target", diff="Hard", topic=TOPIC, tier="extra",
    fn="smallestIndexSubset", params=[("nums", "int[]"), ("target", "int")], ret="int[]", cmp="exact",
    desc="<p>Given an array <code>nums</code> of positive integers and a positive integer <code>target</code>, consider every set of indices whose elements add up to exactly <code>target</code>. Write each such set as a list of indices in increasing order, and compare two lists lexicographically (compare the first indices, then the second ones, and so on).</p><p>Return the <strong>lexicographically smallest</strong> index list, or an empty array if no subset adds up to <code>target</code>.</p><pre>nums = [4, 1, 3, 2, 5], target = 6 -> [0, 3]      (4 + 2; others are [1,4] and [1,2,3])\nnums = [9, 1, 2, 4],    target = 7 -> [1, 2, 3]   (1 + 2 + 4)\nnums = [5, 5],          target = 7 -> []</pre>",
    constraints=["1 &le; nums.length &le; 200", "1 &le; nums[i] &le; 100", "1 &le; target &le; 5,000"],
    hints=["Existence is the plain subset sum DP, but you must reconstruct a specific subset. Think about building the answer left to right.",
           "To decide whether index <code>j</code> can be the next chosen index, you need to know whether the remaining sum can be formed from the elements <em>after</em> <code>j</code>. That suggests a DP over suffixes: <code>can[i][s]</code> = some subset of <code>nums[i:]</code> sums to <code>s</code>.",
           "Walk forward with the remaining sum <code>rem</code>. From the current position pick the smallest index <code>j</code> with <code>nums[j] &le; rem</code> and <code>can[j+1][rem - nums[j]]</code>, subtract, and continue from <code>j + 1</code> until <code>rem = 0</code>."],
    editorial=["First compute the suffix table <code>can[i][s]</code>: whether the elements <code>nums[i], nums[i+1], ...</code> contain a subset with sum <code>s</code>. It is filled from the back: <code>can[n][0]</code> is true, and <code>can[i][s] = can[i+1][s] or can[i+1][s - nums[i]]</code>. If <code>can[0][target]</code> is false, return the empty array.",
               "Otherwise construct the answer greedily. A lexicographically smallest list has the smallest possible first index, then the smallest possible second index, and so on. Standing at position <code>pos</code> with remaining sum <code>rem &gt; 0</code>, the candidate next index <code>j &ge; pos</code> is feasible exactly when <code>nums[j] &le; rem</code> and the rest <code>rem - nums[j]</code> can be formed from <code>nums[j+1:]</code>, which is one table lookup. Pick the smallest feasible <code>j</code>. Since all values are positive, a list can never be a proper prefix of another valid list, so this greedy order is the lexicographic order.",
               "The table takes O(n &middot; target) time and memory, and the reconstruction is O(n) lookups per chosen index, O(n<sup>2</sup>) in the worst case. The reference solution keeps each suffix row as a Python big integer bitset."],
    time="O(n * target)", space="O(n * target)",
    solution='''def smallestIndexSubset(nums, target):
    n = len(nums)
    # suf[i]: bit s is 1 when some subset of nums[i:] sums to s
    suf = [0] * (n + 1)
    suf[n] = 1
    for i in range(n - 1, -1, -1):
        suf[i] = suf[i + 1] | (suf[i + 1] << nums[i])
    if not (suf[0] >> target) & 1:
        return []
    result = []
    pos, rem = 0, target
    while rem > 0:
        for j in range(pos, n):
            if nums[j] <= rem and (suf[j + 1] >> (rem - nums[j])) & 1:
                result.append(j)
                rem -= nums[j]
                pos = j + 1
                break
    return result
''',
    tests=[[[4, 1, 3, 2, 5], 6], [[9, 1, 2, 4], 7], [[5, 5], 7], [[5], 5], [[5], 6], [[1, 1, 1], 2], [[3, 3, 3], 9],
           [[3, 3, 3], 10], [[6, 1, 2, 3, 4], 7], [[10, 20, 30], 50], [[2, 4, 6, 8], 15], [[7, 2, 2, 2, 1], 5]],
)
_r = rnd(8110)
p["tests"].append([[_r.randint(1, 100) for _ in range(200)], 5000])
p["tests"].append([[_r.randint(1, 100) for _ in range(200)], 4321])
p["tests"].append([[100] * 50 + [_r.randint(1, 99) for _ in range(150)], 77])
p["tests"].append([[2 * _r.randint(1, 50) for _ in range(200)], 4999])
p["tests"].append([[100] * 200, 4900])
p["tests"].append([[_r.randint(60, 100) for _ in range(200)] + [], 999])


def b_lexi(nums, target):
    n = len(nums)
    best = None
    for k in range(1, n + 1):
        for comb in combinations(range(n), k):
            if sum(nums[i] for i in comb) == target:
                if best is None or list(comb) < best:
                    best = list(comb)
    return best if best is not None else []


def g_lexi(r):
    n = r.randint(1, 10)
    return [[r.randint(1, 9) for _ in range(n)], r.randint(1, 40)]


def v_lexi(tests):
    for t in tests:
        nums, target = t["args"]
        assert 1 <= len(nums) <= 200 and all(1 <= x <= 100 for x in nums)
        assert 1 <= target <= 5000
        res = t["expected"]
        assert res == sorted(set(res))
        if res:
            assert sum(nums[i] for i in res) == target
    assert any(t["expected"] == [] for t in tests) and any(len(t["expected"]) >= 3 for t in tests)


CHECKS["lexicographically-smallest-subset-for-target"] = (b_lexi, g_lexi, "exact")
VALIDATE["lexicographically-smallest-subset-for-target"] = v_lexi

p = add(
    id="fill-two-bags-max-value", title="Fill Two Bags for Maximum Value", diff="Hard", topic=TOPIC, tier="extra",
    fn="fillTwoBags", params=[("weights", "int[]"), ("values", "int[]"), ("cap1", "int"), ("cap2", "int")], ret="int", cmp="exact",
    desc="<p>You have two bags. Bag 1 can hold total weight at most <code>cap1</code> and bag 2 at most <code>cap2</code>. There are <code>n</code> items, item <code>i</code> weighs <code>weights[i]</code> and is worth <code>values[i]</code>. Every item can be put into bag 1, into bag 2, or left out, but it cannot be split or copied.</p><p>Return the maximum total value that can be stored in the two bags together.</p><pre>weights = [4, 3, 5, 2], values = [8, 5, 9, 3], cap1 = 7, cap2 = 5 -> 22   (bag 1: weights 4 and 3, bag 2: weight 5)\nweights = [6, 6],       values = [10, 10],     cap1 = 5, cap2 = 6 -> 10\nweights = [2, 2, 2],    values = [1, 1, 1],    cap1 = 2, cap2 = 4 -> 3</pre>",
    constraints=["1 &le; weights.length = values.length &le; 50", "1 &le; weights[i] &le; 50", "0 &le; values[i] &le; 100,000", "0 &le; cap1, cap2 &le; 80"],
    hints=["Filling the bags one after the other (best subset for bag 1, then best of what is left) can fail. The two bags have to be planned together.",
           "Use a table with two capacity axes: <code>best[a][b]</code> = the maximum value using the items seen so far, when bag 1 may hold weight at most <code>a</code> and bag 2 at most <code>b</code>.",
           "A new item (weight <code>w</code>, value <code>v</code>) has three options: skip, go to bag 1 (<code>best[a-w][b] + v</code>), or go to bag 2 (<code>best[a][b-w] + v</code>). Read from the table as it was before the item, then answer <code>best[cap1][cap2]</code>."],
    editorial=["This is a 0/1 knapsack with two separate capacities. Greedy ideas such as &quot;fill the larger bag optimally first&quot; fail because the best subset for one bag may use items that the other bag needed. Instead keep one state per pair of capacities: <code>best[a][b]</code> is the maximum value obtainable from the processed items if bag 1 is allowed weight <code>a</code> and bag 2 weight <code>b</code>.",
               "For an item <code>(w, v)</code> the new table is <code>max(old[a][b], old[a-w][b] + v, old[a][b-w] + v)</code>, where the second option needs <code>a &ge; w</code> and the third needs <code>b &ge; w</code>. Computing the new table from the old one (or sweeping both indices downward in place) prevents any item from being used twice or in both bags. The cost is O(n &middot; cap1 &middot; cap2) time and O(cap1 &middot; cap2) space.",
               "The same state design generalises to any fixed number of bags, but the table grows by one dimension per bag."],
    time="O(n * cap1 * cap2)", space="O(cap1 * cap2)",
    solution='''def fillTwoBags(weights, values, cap1, cap2):
    best = [[0] * (cap2 + 1) for _ in range(cap1 + 1)]
    for w, v in zip(weights, values):
        new = []
        for a in range(cap1 + 1):
            cur = best[a][:]
            if a >= w:  # the item goes to bag 1
                cur = [x if x >= y + v else y + v for x, y in zip(cur, best[a - w])]
            if w <= cap2:  # the item goes to bag 2
                cur[w:] = [x if x >= y + v else y + v for x, y in zip(cur[w:], best[a])]
            new.append(cur)
        best = new
    return best[cap1][cap2]
''',
    tests=[[[4, 3, 5, 2], [8, 5, 9, 3], 7, 5], [[6, 6], [10, 10], 5, 6], [[2, 2, 2], [1, 1, 1], 2, 4], [[5], [7], 0, 0],
           [[5], [7], 5, 0], [[5], [7], 0, 5], [[5], [7], 4, 4], [[1, 1, 1, 1], [1, 2, 3, 4], 2, 2], [[3, 3], [5, 6], 3, 3],
           [[3, 3], [5, 6], 6, 0], [[10, 9, 8], [0, 0, 0], 10, 10], [[50, 50, 50], [100000, 100000, 100000], 80, 80]],
)
_r = rnd(8111)
p["tests"].append([[_r.randint(1, 50) for _ in range(50)], [_r.randint(0, 100000) for _ in range(50)], 80, 80])
p["tests"].append([[_r.randint(1, 12) for _ in range(50)], [_r.randint(0, 1000) for _ in range(50)], 80, 80])
p["tests"].append([[_r.randint(1, 12) for _ in range(50)], [_r.randint(0, 1000) for _ in range(50)], 80, 37])
_w = [_r.randint(5, 30) for _ in range(50)]
p["tests"].append([_w, [x * 100 + _r.randint(0, 3) for x in _w], 79, 80])
p["tests"].append([[1] * 50, [_r.randint(0, 100000) for _ in range(50)], 50, 3])


def b_twobags(weights, values, cap1, cap2):
    n = len(weights)
    best = 0
    for assign in product((0, 1, 2), repeat=n):
        w1 = sum(weights[i] for i in range(n) if assign[i] == 1)
        w2 = sum(weights[i] for i in range(n) if assign[i] == 2)
        if w1 <= cap1 and w2 <= cap2:
            best = max(best, sum(values[i] for i in range(n) if assign[i]))
    return best


def g_twobags(r):
    n = r.randint(1, 8)
    return [[r.randint(1, 7) for _ in range(n)], [r.randint(0, 10) for _ in range(n)], r.randint(0, 14), r.randint(0, 14)]


def v_twobags(tests):
    for t in tests:
        w, v, c1, c2 = t["args"]
        assert 1 <= len(w) <= 50 and len(w) == len(v)
        assert all(1 <= x <= 50 for x in w) and all(0 <= x <= 100000 for x in v)
        assert 0 <= c1 <= 80 and 0 <= c2 <= 80


CHECKS["fill-two-bags-max-value"] = (b_twobags, g_twobags, "exact")
VALIDATE["fill-two-bags-max-value"] = v_twobags
