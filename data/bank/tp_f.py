"""Problems: two pointers, answer-shrinking (container / trapping variants, boats, bounded sums, best pair under a constraint)."""
from lib import add, rnd, CHECKS, VALIDATE, gen_arr  # noqa: F401

TOPIC = "Two Pointers"
INT_MIN, INT_MAX = -(2 ** 31), 2 ** 31 - 1


# ---------------------------------------------------------------- EASY

p = add(
    id="max-pairs-with-sum-k", title="Remove Pairs Adding Up to K", diff="Easy", topic=TOPIC,
    fn="maxKSumPairs", params=[("nums", "int[]"), ("k", "int")], ret="int", cmp="exact", tier="common",
    desc="<p>In one operation you pick two different elements of <code>nums</code> whose values add up to exactly <code>k</code> and remove both from the array.</p><p>Return the maximum number of operations you can perform.</p><pre>nums = [1, 2, 3, 4], k = 5\n(1,4) then (2,3)  -&gt;  result = 2\n\nnums = [3, 1, 3, 4, 3], k = 6\nonly one pair of 3s can be used  -&gt;  result = 1</pre>",
    constraints=["1 &le; nums.length &le; 8,000", "1 &le; nums[i] &le; 10<sup>9</sup>", "1 &le; k &le; 2&middot;10<sup>9</sup>"],
    hints=["Each element can be used at most once, so this is about matching elements with their complements <code>k - x</code>.",
           "Sort the array. The smallest value can only be matched with exactly one value, <code>k - smallest</code>, and that value is the same whichever copy you take.",
           "Use <code>lo</code> and <code>hi</code> on the sorted array: sum equal to <code>k</code> means one operation, move both; sum too small means <code>a[lo]</code> has no partner left, move <code>lo</code>; sum too large means <code>a[hi]</code> has none, move <code>hi</code>."],
    editorial=["Sort the array and place two pointers at the ends. If <code>a[lo] + a[hi] == k</code> we perform an operation and discard both. If the sum is smaller than <code>k</code>, even the largest remaining value is not enough for <code>a[lo]</code>, so <code>a[lo]</code> can never be matched; if it is larger, <code>a[hi]</code> cannot be matched even with the smallest remaining value.",
               "Matching equal pairs greedily is safe because all candidates for a value are interchangeable copies. A hash map of counts gives the same answer in O(n) time but needs O(n) extra space; the sorted two-pointer version needs only the sort."],
    time="O(n log n)", space="O(n)",
    solution='''def maxKSumPairs(nums, k):
    a = sorted(nums)
    lo, hi = 0, len(a) - 1
    ops = 0
    while lo < hi:
        s = a[lo] + a[hi]
        if s == k:
            ops += 1
            lo += 1
            hi -= 1
        elif s < k:
            lo += 1
        else:
            hi -= 1
    return ops
''',
    tests=[[[1, 2, 3, 4], 5], [[3, 1, 3, 4, 3], 6], [[7], 14], [[7, 7], 14], [[7, 7, 7], 14], [[1, 1, 1, 1], 3], [[2, 2, 2, 2], 4],
           [[1, 5, 5, 1, 9, 9, 4, 6], 10], [[10 ** 9, 10 ** 9], 2 * 10 ** 9], [[10 ** 9, 1, 10 ** 9 - 1, 2], 10 ** 9 + 1], [[4, 4, 4, 4, 4, 4, 4], 8],
           [[1, 2, 3], 100]],
)
_r = rnd(7003)
p["tests"].append([[_r.randint(1, 2000) for _ in range(5000)], 2000])
_k = 1000000007
_v = [_r.randint(1, _k - 1) for _ in range(2000)]
_a = _v + [_k - x for x in _v[:1800]]
_r.shuffle(_a)
p["tests"].append([_a, _k])
p["tests"].append([[500] * 3001 + [_r.randint(1, 499) for _ in range(1000)], 1000])


def b_ksum(nums, k):
    n = len(nums)
    memo = {}

    def go(mask):
        if mask in memo:
            return memo[mask]
        i = 0
        while i < n and not (mask >> i) & 1:
            i += 1
        if i == n:
            return 0
        rest = mask & ~(1 << i)
        best = go(rest)
        for j in range(i + 1, n):
            if (rest >> j) & 1 and nums[i] + nums[j] == k:
                best = max(best, 1 + go(rest & ~(1 << j)))
        memo[mask] = best
        return best

    return go((1 << n) - 1)


def v_ksum(tests):
    for t in tests:
        nums, k = t["args"]
        assert 1 <= len(nums) <= 8000
        assert all(1 <= x <= 10 ** 9 for x in nums)
        assert 1 <= k <= 2 * 10 ** 9


CHECKS["max-pairs-with-sum-k"] = (b_ksum, lambda r: [[r.randint(1, 6) for _ in range(r.randint(1, 9))], r.randint(2, 12)], "exact")
VALIDATE["max-pairs-with-sum-k"] = v_ksum


# ---------------------------------------------------------------- MEDIUM

p = add(
    id="largest-square-between-walls", title="Largest Square Tank Between Walls", diff="Medium", topic=TOPIC,
    fn="largestSquareTank", params=[("heights", "int[]")], ret="int", cmp="exact", tier="extra",
    desc="<p>Vertical walls stand along a line: wall <code>i</code> is at position <code>i</code> and has height <code>heights[i]</code>. You want to place a square tank (axis-aligned, standing on the ground) between two walls <code>i &lt; j</code>. It must fit horizontally in the gap, so its side is at most <code>j - i</code>, and it must not rise above the lower of the two walls, so its side is at most <code>min(heights[i], heights[j])</code>.</p><p>Return the largest possible <strong>area</strong> of such a square, over all choices of two walls.</p><pre>heights = [3, 9, 2, 2, 8, 3, 1]\nwalls 1 and 4: gap 3, heights 9 and 8  -&gt;  side 3, area 9\nresult = 9</pre>",
    constraints=["2 &le; heights.length &le; 8,000", "1 &le; heights[i] &le; 10<sup>9</sup>"],
    hints=["Checking every pair of walls is O(n&sup2;). Think of the classic container problem: start with the widest pair and shrink.",
           "The side is <code>min(h[i], h[j], j - i)</code>. Look at the lower wall of the current pair: how large can any pair that keeps this wall but is narrower become?",
           "Keep <code>l = 0</code>, <code>r = n - 1</code>. Record <code>min(h[l], h[r], r - l)</code>, then move the pointer at the lower wall inward. (If the walls are equal either one can move.)"],
    editorial=["Start with the widest pair and compute its side <code>s = min(h[l], h[r], r - l)</code>. Suppose <code>h[l] &le; h[r]</code>. Any other pair that still uses wall <code>l</code> has a partner <code>j &lt; r</code>, so its width is smaller and its side is bounded by <code>min(h[l], width) &le; min(h[l], r - l)</code>. Since <code>h[l] &le; h[r]</code>, that bound equals the side we just recorded. So no pair using wall <code>l</code> with a closer partner can beat the current pair, and wall <code>l</code> can be discarded (<code>l += 1</code>).",
               "The same argument works symmetrically when <code>h[r]</code> is the lower wall. Every step discards one wall, so after <code>n - 1</code> steps all candidates have been covered and the answer is the square of the best side seen. This is O(n) time and O(1) space; the brute force is O(n&sup2;).",
               "The extra <code>r - l</code> term does not break the container argument because the width only shrinks as pointers move inward, exactly as in the classic problem."],
    time="O(n)", space="O(1)",
    solution='''def largestSquareTank(heights):
    l, r = 0, len(heights) - 1
    best = 0
    while l < r:
        side = min(heights[l], heights[r], r - l)
        if side > best:
            best = side
        if heights[l] <= heights[r]:
            l += 1
        else:
            r -= 1
    return best * best
''',
    tests=[[[3, 9, 2, 2, 8, 3, 1]], [[1, 1]], [[5, 5]], [[1, 8, 6, 2, 5, 4, 8, 3, 7]], [[10, 1, 1, 1, 1, 10]], [[2, 2, 2, 2, 2]],
           [[1, 2, 3, 4, 5, 6]], [[6, 5, 4, 3, 2, 1]], [[10 ** 9, 10 ** 9, 10 ** 9]], [[10 ** 9, 1, 1, 1, 10 ** 9]], [[4, 1, 1, 1, 1, 1, 1, 4]],
           [[7, 3, 9, 1, 8, 2, 6, 4, 5]]],
)
_r = rnd(7004)
p["tests"].append([[_r.randint(1, 100000) for _ in range(6000)]])
p["tests"].append([[_r.randint(1, 3000) for _ in range(7000)]])
p["tests"].append([[100000 - i // 2 for i in range(6000)]])
p["tests"].append([[_r.randint(1, 8) for _ in range(7000)]])


def b_square(heights):
    best = 0
    for i in range(len(heights)):
        for j in range(i + 1, len(heights)):
            s = min(heights[i], heights[j], j - i)
            best = max(best, s * s)
    return best


def v_square(tests):
    for t in tests:
        h = t["args"][0]
        assert 2 <= len(h) <= 8000
        assert all(1 <= x <= 10 ** 9 for x in h)


CHECKS["largest-square-between-walls"] = (b_square, lambda r: [[r.randint(1, 9) for _ in range(r.randint(2, 11))]], "exact")
VALIDATE["largest-square-between-walls"] = v_square


p = add(
    id="largest-pool-volume", title="Largest Pool After the Rain", diff="Medium", topic=TOPIC,
    fn="largestPool", params=[("heights", "int[]")], ret="int", cmp="exact", tier="extra",
    desc="<p>A terrain is a row of unit-width columns, <code>heights[i]</code> units tall. After a long rain, the water standing above column <code>i</code> is</p><pre>water[i] = min(max(heights[0..i]), max(heights[i..n-1])) - heights[i]</pre><p>(the usual trapped-water rule: the level is limited by the lower of the tallest column to the left and the tallest to the right, each including column <code>i</code> itself).</p><p>A <strong>pool</strong> is a maximal run of consecutive columns that each hold at least one unit of water. Return the volume of the largest pool (the sum of <code>water[i]</code> over its columns), or <code>0</code> if there is no water at all.</p><pre>heights = [4, 1, 3, 0, 2, 5, 1, 0, 6]\nwater   = [0, 3, 1, 4, 2, 0, 4, 5, 0]\npools: columns 1..4 hold 10, columns 6..7 hold 9\nresult = 10</pre>",
    constraints=["1 &le; heights.length &le; 10,000", "0 &le; heights[i] &le; 10<sup>5</sup>"],
    hints=["First solve the usual question: how much water sits above each column? Prefix and suffix maxima give it in O(n) with extra arrays.",
           "To avoid the two extra arrays, use two pointers with a running left maximum and a running right maximum: always process the side whose current column is lower.",
           "Store (or directly accumulate) the water of every column. Walk through the columns once more: add to the current pool while <code>water[i] &gt; 0</code>, and when a column with zero water appears, close the pool and compare it with the best so far."],
    editorial=["Pools are separated exactly by columns with zero water, i.e. columns at least as tall as the water level around them. So the problem is the standard trapped-water computation followed by a scan for the best run of positive values.",
               "Two pointers compute the water without prefix arrays. Keep <code>lmax</code> and <code>rmax</code>. If <code>heights[l] &lt; heights[r]</code>, the right side already has a wall at least as tall as <code>heights[l]</code>, so the level above column <code>l</code> is decided by <code>lmax</code> alone: update <code>lmax</code>, set <code>water[l] = lmax - heights[l]</code> and advance. Otherwise do the mirror image on the right. The pointers meet at a column that is a global maximum, which holds no water.",
               "The scan over <code>water</code> sums each run of positive entries and keeps the maximum. Total time O(n), space O(n) for the water array (it could be fused into the main loop with a little more care)."],
    time="O(n)", space="O(n)",
    solution='''def largestPool(heights):
    n = len(heights)
    water = [0] * n
    l, r = 0, n - 1
    lmax = rmax = 0
    while l < r:
        if heights[l] < heights[r]:
            if heights[l] > lmax:
                lmax = heights[l]
            water[l] = lmax - heights[l]
            l += 1
        else:
            if heights[r] > rmax:
                rmax = heights[r]
            water[r] = rmax - heights[r]
            r -= 1
    best = cur = 0
    for w in water:
        if w > 0:
            cur += w
            if cur > best:
                best = cur
        else:
            cur = 0
    return best
''',
    tests=[[[4, 1, 3, 0, 2, 5, 1, 0, 6]], [[3, 0, 3, 0, 3]], [[3, 0, 2, 0, 3]], [[5]], [[1, 2, 3, 4]], [[4, 3, 2, 1]], [[2, 0, 2]],
           [[0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1]], [[5, 0, 0, 0, 5, 0, 0, 0, 0, 9]], [[0, 0, 0]], [[6, 1, 4, 1, 6, 2, 0, 2, 8]],
           [[100000, 0, 100000]]],
)
_r = rnd(7005)
p["tests"].append([[_r.randint(0, 1000) for _ in range(6000)]])
p["tests"].append([[100000] + [_r.randint(0, 99999) for _ in range(9998)] + [100000]])
p["tests"].append([[(abs(i - 2500) // 3) * 2 + _r.randint(0, 3) for i in range(5000)]])


def b_pool(heights):
    n = len(heights)
    water = [min(max(heights[:i + 1]), max(heights[i:])) - heights[i] for i in range(n)]
    best = 0
    i = 0
    while i < n:
        if water[i] > 0:
            j = i
            tot = 0
            while j < n and water[j] > 0:
                tot += water[j]
                j += 1
            best = max(best, tot)
            i = j
        else:
            i += 1
    return best


def v_pool(tests):
    for t in tests:
        h = t["args"][0]
        assert 1 <= len(h) <= 10000
        assert all(0 <= x <= 10 ** 5 for x in h)


CHECKS["largest-pool-volume"] = (b_pool, lambda r: [[r.randint(0, 6) for _ in range(r.randint(1, 14))]], "exact")
VALIDATE["largest-pool-volume"] = v_pool


p = add(
    id="min-boat-limit-for-fleet", title="Lowest Weight Limit for a Fixed Fleet", diff="Medium", topic=TOPIC,
    fn="minBoatLimit", params=[("weights", "int[]"), ("boats", "int")], ret="int", cmp="exact", tier="extra",
    desc="<p>A group of people must cross a river. <code>weights[i]</code> is the weight of person <code>i</code>. You have exactly <code>boats</code> boats available (using fewer is fine). Each boat carries at most <strong>two</strong> people and the total weight on a boat must not exceed a common weight limit <code>L</code>; a single person must weigh at most <code>L</code> as well.</p><p>Return the smallest integer <code>L</code> for which everyone can cross using at most <code>boats</code> boats. The input guarantees <code>boats &ge; ceil(n / 2)</code>, so some limit always works.</p><pre>weights = [1, 2, 3, 4, 5], boats = 3\nL = 5: boats (1,4), (2,3), (5)\nresult = 5\n\nweights = [2, 9, 4, 7], boats = 3\nresult = 9</pre>",
    constraints=["1 &le; weights.length &le; 10,000", "1 &le; weights[i] &le; 10<sup>9</sup>", "ceil(weights.length / 2) &le; boats &le; weights.length"],
    hints=["For a fixed limit <code>L</code>, the minimum number of boats is the classic two-pointer greedy. The number of boats needed never increases as <code>L</code> grows. What does that suggest?",
           "That gives binary search on <code>L</code>, but there is an even more direct way. With <code>boats</code> boats and <code>n</code> people, at least <code>p = n - boats</code> boats must carry two people.",
           "Heavy people are best left to travel alone, so the paired people are the <code>2p</code> lightest. Pair the lightest with the heaviest of those <code>2p</code>, the second lightest with the second heaviest, and so on; the limit is the maximum of those pair sums and the heaviest person."],
    editorial=["Every boat carries one or two people, so with <code>boats</code> boats at least <code>p = n - boats</code> boats must be shared (if <code>p &le; 0</code> everyone can travel alone and the answer is the heaviest weight). More shared boats than needed never help, since a shared boat can always be split into two single trips without raising the limit above the heaviest weight, which the limit must cover anyway.",
               "Singles only force <code>L &ge;</code> their own weight, which is already implied by <code>L &ge; max(weights)</code>. So it is best to make the <em>lightest</em> <code>2p</code> people the shared ones: swapping a paired person for a lighter single can only lower the pair sum. Among those <code>2p</code> sorted values, pairing smallest with largest, then the next smallest with the next largest, minimizes the largest pair sum (the standard exchange argument).",
               "Hence <code>L = max(w[n-1], max over i &lt; p of w[i] + w[2p-1-i])</code>. After sorting this is one two-pointer pass. An alternative with the same result is binary searching <code>L</code> and running the boat-counting greedy for each guess, in O(n log n log(sum)). The direct method is O(n log n) for the sort."],
    time="O(n log n)", space="O(n)",
    solution='''def minBoatLimit(weights, boats):
    w = sorted(weights)
    n = len(w)
    p = max(0, n - boats)
    limit = w[-1]
    i, j = 0, 2 * p - 1
    while i < j:
        s = w[i] + w[j]
        if s > limit:
            limit = s
        i += 1
        j -= 1
    return limit
''',
    tests=[[[1, 2, 3, 4, 5], 3], [[2, 9, 4, 7], 3], [[3, 3, 3, 3], 2], [[3, 3, 3, 3], 4], [[8], 1], [[5, 6], 1], [[5, 6], 2],
           [[1, 1, 10, 10], 2], [[1, 2, 3, 4, 5, 6], 3], [[1, 2, 3, 4, 5, 6], 5], [[10 ** 9, 10 ** 9, 10 ** 9, 10 ** 9], 2],
           [[4, 1, 7, 3, 9, 2, 8], 4]],
)
_r = rnd(7006)
p["tests"].append([[_r.randint(1, 100000) for _ in range(5000)], 2600])
p["tests"].append([[_r.randint(1, 10 ** 9) for _ in range(3001)], 1501])
p["tests"].append([[_r.randint(1, 1000) for _ in range(6000)], 4000])


def b_boatlimit(weights, boats):
    n = len(weights)

    def need(L):
        memo = {}

        def go(mask):
            if mask == 0:
                return 0
            if mask in memo:
                return memo[mask]
            i = (mask & -mask).bit_length() - 1
            rest = mask & ~(1 << i)
            best = 1 + go(rest)
            for j in range(n):
                if (rest >> j) & 1 and weights[i] + weights[j] <= L:
                    best = min(best, 1 + go(rest & ~(1 << j)))
            memo[mask] = best
            return best

        return go((1 << n) - 1)

    L = max(weights)
    while need(L) > boats:
        L += 1
    return L


def g_boatlimit(r):
    n = r.randint(1, 8)
    return [[r.randint(1, 10) for _ in range(n)], r.randint((n + 1) // 2, n)]


def v_boatlimit(tests):
    for t in tests:
        w, b = t["args"]
        assert 1 <= len(w) <= 10000
        assert all(1 <= x <= 10 ** 9 for x in w)
        assert (len(w) + 1) // 2 <= b <= len(w)


CHECKS["min-boat-limit-for-fleet"] = (b_boatlimit, g_boatlimit, "exact")
VALIDATE["min-boat-limit-for-fleet"] = v_boatlimit


p = add(
    id="max-triple-sum-not-above-limit", title="Best Triple Sum Within a Limit", diff="Medium", topic=TOPIC,
    fn="bestTripleSum", params=[("nums", "int[]"), ("limit", "int")], ret="int", cmp="exact", tier="extra",
    desc="<p>Given an array <code>nums</code> of positive integers and an integer <code>limit</code>, choose three elements at three different positions so that their sum is as large as possible but <strong>not greater than</strong> <code>limit</code>.</p><p>Return that sum, or <code>-1</code> if every triple sums to more than <code>limit</code> (or there are fewer than three elements).</p><pre>nums = [5, 2, 7, 3, 10, 1], limit = 15\n10 + 3 + 2 = 15\nresult = 15\n\nnums = [4, 6, 9], limit = 18\nresult = -1</pre>",
    constraints=["1 &le; nums.length &le; 400", "1 &le; nums[i] &le; 10<sup>9</sup>", "1 &le; limit &le; 2<sup>31</sup> - 1"],
    hints=["Trying every triple is O(n&sup3;). After fixing one element, the task becomes a pair problem on the rest.",
           "Sort the array. Fix the smallest index <code>i</code>. The remaining question is: best pair among indices after <code>i</code> with sum at most <code>limit - nums[i]</code>.",
           "For the pair, use <code>lo = i + 1</code>, <code>hi = n - 1</code>. If the triple sum fits, record it and move <code>lo</code> up; otherwise move <code>hi</code> down."],
    editorial=["Sort the array, then for each first element <code>a[i]</code> look for the best pair in <code>a[i+1:]</code> with the two-pointer sweep: if <code>a[i] + a[lo] + a[hi] &le; limit</code>, this is a candidate and <code>a[lo]</code> cannot do better with any other partner (all larger partners were already rejected or are not larger), so advance <code>lo</code>; otherwise <code>a[hi]</code> is too large even with the smallest available partner, so retreat <code>hi</code>.",
               "The outer loop has n choices and each sweep is linear, so the time is O(n&sup2;) after the sort. Exiting early when the sum equals <code>limit</code> exactly, or when the three smallest remaining values already exceed it, is only an optimization."],
    time="O(n^2)", space="O(n)",
    solution='''def bestTripleSum(nums, limit):
    a = sorted(nums)
    n = len(a)
    best = -1
    for i in range(n - 2):
        if a[i] + a[i + 1] + a[i + 2] > limit:
            break
        lo, hi = i + 1, n - 1
        while lo < hi:
            s = a[i] + a[lo] + a[hi]
            if s <= limit:
                if s > best:
                    best = s
                    if best == limit:
                        return best
                lo += 1
            else:
                hi -= 1
    return best
''',
    tests=[[[5, 2, 7, 3, 10, 1], 15], [[4, 6, 9], 18], [[4, 6, 9], 19], [[1, 2], 100], [[3], 3], [[1, 1, 1], 3], [[1, 1, 1], 2],
           [[10 ** 9, 10 ** 9, 10 ** 9], INT_MAX], [[10 ** 9, 10 ** 9, 147483647], INT_MAX], [[8, 8, 8, 8], 23],
           [[9, 1, 5, 7, 3, 11, 2], 20], [[1, 2, 3, 4, 5, 6, 7, 8, 9, 10], 1000]],
)
_r = rnd(7008)
p["tests"].append([[_r.randint(1, 10 ** 9) for _ in range(400)], 1500000000])
p["tests"].append([[_r.randint(1, 1000) for _ in range(400)], 1234])
p["tests"].append([[_r.randint(10 ** 8, 10 ** 9) for _ in range(400)], 3 * 10 ** 8 + 12345])


def b_triple(nums, limit):
    best = -1
    n = len(nums)
    for i in range(n):
        for j in range(i + 1, n):
            for k in range(j + 1, n):
                s = nums[i] + nums[j] + nums[k]
                if s <= limit and s > best:
                    best = s
    return best


def v_triple(tests):
    for t in tests:
        nums, limit = t["args"]
        assert 1 <= len(nums) <= 400
        assert all(1 <= x <= 10 ** 9 for x in nums)
        assert 1 <= limit <= INT_MAX


CHECKS["max-triple-sum-not-above-limit"] = (b_triple, lambda r: [[r.randint(1, 9) for _ in range(r.randint(1, 9))], r.randint(1, 30)], "exact")
VALIDATE["max-triple-sum-not-above-limit"] = v_triple


p = add(
    id="shortest-removal-to-make-sorted", title="Shortest Block to Delete for a Sorted Array", diff="Medium", topic=TOPIC,
    fn="shortestRemoval", params=[("nums", "int[]")], ret="int", cmp="exact", tier="common",
    desc="<p>You may delete one <strong>contiguous</strong> block of elements from <code>nums</code> (the block may be empty). After the deletion, the remaining elements, in their original order, must be sorted in non-decreasing order.</p><p>Return the smallest possible length of the deleted block.</p><pre>nums = [2, 4, 9, 3, 1, 5, 6]\ndelete [9, 3, 1] -&gt; [2, 4, 5, 6]\nresult = 3\n\nnums = [5, 4, 3, 2, 1]\nresult = 4      (keep any single element)</pre>",
    constraints=["1 &le; nums.length &le; 10,000", "-10<sup>9</sup> &le; nums[i] &le; 10<sup>9</sup>"],
    hints=["What do the elements you keep look like? They form a prefix and a suffix of the original array, and both must already be sorted.",
           "Find the longest sorted prefix and the longest sorted suffix first. Which blocks are candidates if you keep only one of them?",
           "To keep part of both, use a pointer <code>i</code> in the prefix and <code>j</code> in the suffix. If <code>nums[i] &le; nums[j]</code> you can join them (delete <code>j - i - 1</code> elements) and advance <code>i</code>; otherwise advance <code>j</code>."],
    editorial=["Whatever remains is a prefix <code>nums[0..i]</code> plus a suffix <code>nums[j..n-1]</code>. Each must be non-decreasing by itself, so <code>i</code> is at most the end <code>l</code> of the longest non-decreasing prefix and <code>j</code> is at least the start <code>r</code> of the longest non-decreasing suffix. Also the join must be valid: <code>nums[i] &le; nums[j]</code>.",
               "If the array is already sorted the answer is 0. Otherwise the answers that keep only a prefix or only a suffix cost <code>n - l - 1</code> and <code>r</code>. For the combined case, sweep: with <code>i = 0</code> and <code>j = r</code>, if <code>nums[i] &le; nums[j]</code> record <code>j - i - 1</code> and increase <code>i</code> (a longer prefix is better for this <code>j</code>); otherwise <code>nums[j]</code> is too small for this and every larger prefix end, so increase <code>j</code>. Both pointers only move forward, so the sweep is O(n)."],
    time="O(n)", space="O(1)",
    solution='''def shortestRemoval(nums):
    n = len(nums)
    l = 0
    while l + 1 < n and nums[l] <= nums[l + 1]:
        l += 1
    if l == n - 1:
        return 0
    r = n - 1
    while r > 0 and nums[r - 1] <= nums[r]:
        r -= 1
    best = min(n - l - 1, r)
    i, j = 0, r
    while i <= l and j < n:
        if nums[i] <= nums[j]:
            if j - i - 1 < best:
                best = j - i - 1
            i += 1
        else:
            j += 1
    return best
''',
    tests=[[[2, 4, 9, 3, 1, 5, 6]], [[5, 4, 3, 2, 1]], [[1, 2, 3]], [[7]], [[2, 1]], [[1, 2, 3, 10, 4, 2, 3, 5]], [[3, 3, 3]],
           [[1, 3, 2, 2, 4]], [[9, 1, 2, 3, 4]], [[1, 2, 3, 4, 0]], [[-10 ** 9, 10 ** 9, -10 ** 9, 10 ** 9]], [[4, 5, 1, 2, 3, 6, 7]]],
)
_r = rnd(7009)
_a = sorted(_r.randint(-10 ** 6, 10 ** 6) for _ in range(5000))
_a[2000:2300] = [_r.randint(-10 ** 6, 10 ** 6) for _ in range(300)]
p["tests"].append([_a])
p["tests"].append([[_r.randint(-10 ** 9, 10 ** 9) for _ in range(5000)]])
_a = sorted(_r.randint(0, 10 ** 5) for _ in range(6000))
p["tests"].append([_a[3000:] + _a[:3000]])
p["tests"].append([sorted(_r.randint(0, 50) for _ in range(5000)) + [0]])


def b_removal(nums):
    n = len(nums)
    best = n
    for s in range(n + 1):
        for e in range(s, n + 1):
            rest = nums[:s] + nums[e:]
            if all(rest[x] <= rest[x + 1] for x in range(len(rest) - 1)):
                best = min(best, e - s)
    return best


def v_removal(tests):
    for t in tests:
        nums = t["args"][0]
        assert 1 <= len(nums) <= 10000
        assert all(-10 ** 9 <= x <= 10 ** 9 for x in nums)


CHECKS["shortest-removal-to-make-sorted"] = (b_removal, lambda r: [[r.randint(1, 6) for _ in range(r.randint(1, 10))]], "exact")
VALIDATE["shortest-removal-to-make-sorted"] = v_removal


# ---------------------------------------------------------------- HARD

p = add(
    id="kth-smallest-sum-two-sorted-arrays", title="K-th Smallest Sum From Two Sorted Arrays", diff="Hard", topic=TOPIC,
    fn="kthPairSum", params=[("a", "int[]"), ("b", "int[]"), ("k", "int")], ret="int", cmp="exact", tier="extra",
    desc="<p>Two arrays <code>a</code> and <code>b</code>, both sorted in non-decreasing order, are given. Take one element from each array to form a pair; there are <code>a.length * b.length</code> pairs (pairs at different positions are different even if their values match). Consider all the pair sums <code>a[i] + b[j]</code> in sorted order.</p><p>Return the value of the <code>k</code>-th smallest sum (1-indexed). Note that <code>k</code> can be in the millions, so listing the sums is not an option.</p><pre>a = [1, 7, 11], b = [2, 4, 6], k = 5\nsums sorted: 3, 5, 7, 9, 11, 13, 13, 15, 17\nresult = 11</pre>",
    constraints=["1 &le; a.length, b.length &le; 2,000", "-10<sup>9</sup> &le; a[i], b[j] &le; 10<sup>9</sup>", "a and b are sorted in non-decreasing order", "1 &le; k &le; a.length * b.length"],
    hints=["There can be up to 4 million sums. A heap that pops <code>k</code> times is too slow when <code>k</code> is that big. Think about searching over the <em>value</em> of the answer instead of over the pairs.",
           "For a guess <code>x</code>, can you count how many sums are at most <code>x</code> in O(n + m) using the sorted order? As you move through <code>a</code> upward, the largest usable element of <code>b</code> only moves downward.",
           "Binary search the smallest <code>x</code> whose count is at least <code>k</code>. Counting: pointer <code>j</code> starts at the end of <code>b</code>; for each <code>a[i]</code> in increasing order, decrease <code>j</code> while <code>a[i] + b[j] &gt; x</code>, then add <code>j + 1</code>."],
    editorial=["Let <code>count(x)</code> be the number of pairs with sum at most <code>x</code>. It is non-decreasing in <code>x</code>, and the <code>k</code>-th smallest sum is the smallest <code>x</code> with <code>count(x) &ge; k</code>. So binary search on <code>x</code> between <code>a[0] + b[0]</code> and <code>a[-1] + b[-1]</code>; the range is at most about 4&middot;10<sup>9</sup>, so around 32 iterations.",
               "To compute <code>count(x)</code> with two pointers: process <code>a</code> in increasing order and keep <code>j</code>, the last index of <code>b</code> with <code>a[i] + b[j] &le; x</code>. As <code>a[i]</code> grows, the allowed <code>b[j]</code> shrinks, so <code>j</code> only moves left. Each <code>a[i]</code> contributes <code>j + 1</code> pairs. One count takes O(n + m).",
               "Total time is O((n + m) log(range)). The smallest <code>x</code> with <code>count(x) &ge; k</code> is automatically an actual pair sum, since otherwise <code>x - 1</code> would have the same count."],
    time="O((n + m) log V)", space="O(1)",
    solution='''def kthPairSum(a, b, k):
    lo = a[0] + b[0]
    hi = a[-1] + b[-1]
    while lo < hi:
        mid = (lo + hi) // 2
        cnt = 0
        j = len(b) - 1
        for x in a:
            while j >= 0 and x + b[j] > mid:
                j -= 1
            if j < 0:
                break
            cnt += j + 1
        if cnt >= k:
            hi = mid
        else:
            lo = mid + 1
    return lo
''',
    tests=[[[1, 7, 11], [2, 4, 6], 5], [[1], [1], 1], [[1, 1, 1], [1, 1, 1], 9], [[1, 2], [3], 2], [[1, 2], [3], 1], [[-5, -1, 0], [-3, 2], 4],
           [[0, 0, 0], [5, 5], 6], [[-10 ** 9, 10 ** 9], [-10 ** 9, 10 ** 9], 1], [[-10 ** 9, 10 ** 9], [-10 ** 9, 10 ** 9], 2],
           [[-10 ** 9, 10 ** 9], [-10 ** 9, 10 ** 9], 4], [[1, 3, 5, 7, 9], [2, 4, 6, 8, 10], 13], [[2, 3, 3], [1, 1, 5], 7]],
)
_r = rnd(7010)
_a = sorted(_r.randint(-10 ** 9, 10 ** 9) for _ in range(1800))
_b = sorted(_r.randint(-10 ** 9, 10 ** 9) for _ in range(1500))
p["tests"].append([_a, _b, 1350000])
_a = sorted(_r.randint(0, 40) for _ in range(2000))
_b = sorted(_r.randint(0, 40) for _ in range(2000))
p["tests"].append([_a, _b, 2000000])
_a = sorted(_r.randint(-10 ** 6, 10 ** 6) for _ in range(2000))
_b = sorted(_r.randint(-10 ** 6, 10 ** 6) for _ in range(5))
p["tests"].append([_a, _b, 7777])


def b_kth(a, b, k):
    return sorted(x + y for x in a for y in b)[k - 1]


def g_kth(r):
    a = sorted(r.randint(-8, 8) for _ in range(r.randint(1, 6)))
    b = sorted(r.randint(-8, 8) for _ in range(r.randint(1, 6)))
    return [a, b, r.randint(1, len(a) * len(b))]


def v_kth(tests):
    for t in tests:
        a, b, k = t["args"]
        assert 1 <= len(a) <= 2000 and 1 <= len(b) <= 2000
        assert all(-10 ** 9 <= x <= 10 ** 9 for x in a + b)
        assert a == sorted(a) and b == sorted(b)
        assert 1 <= k <= len(a) * len(b)


CHECKS["kth-smallest-sum-two-sorted-arrays"] = (b_kth, g_kth, "exact")
VALIDATE["kth-smallest-sum-two-sorted-arrays"] = v_kth



# ---------------------------------------------------------------- more problems

p = add(
    id="largest-pair-sum-within-gap", title="Largest Pair Sum With Values Close Together", diff="Easy", topic=TOPIC,
    fn="bestPairWithinGap", params=[("nums", "int[]"), ("d", "int")], ret="int", cmp="exact", tier="common",
    desc="<p>You are given an array <code>nums</code> of positive integers and a non-negative integer <code>d</code>. Choose two different positions <code>i</code> and <code>j</code> such that the two values differ by at most <code>d</code>, that is <code>|nums[i] - nums[j]| &le; d</code>, and the sum <code>nums[i] + nums[j]</code> is as large as possible.</p><p>Return that largest sum, or <code>-1</code> if no two elements differ by at most <code>d</code>.</p><pre>nums = [2, 9, 5, 12, 3], d = 2\nsorted: 2 3 5 9 12\nbest pair is (3, 5)  -&gt;  result = 8\n\nnums = [5, 3, 8], d = 0\nresult = -1</pre>",
    constraints=["1 &le; nums.length &le; 5,000", "1 &le; nums[i] &le; 10<sup>9</sup>", "0 &le; d &le; 10<sup>9</sup>"],
    hints=["Checking all pairs is O(n&sup2;). Sort the array and think about which pairs could ever be optimal.",
           "Take any valid pair <code>x &le; y</code> in the sorted array. If there is an element between them, or just below <code>y</code>, can you swap <code>x</code> for it?",
           "A valid pair can always be replaced by the pair formed by <code>y</code> and its sorted predecessor: that predecessor is at least <code>x</code> and closer to <code>y</code>. So only adjacent pairs matter; scan from the top and return the first adjacent pair whose difference is at most <code>d</code>."],
    editorial=["Sort the array. Suppose <code>(a[p], a[q])</code> with <code>p &lt; q</code> is a valid pair. Then <code>(a[q-1], a[q])</code> is also valid, because <code>a[q-1] &ge; a[p]</code> makes the difference no larger, and its sum is no smaller. Hence an optimal pair can always be chosen from adjacent elements of the sorted array.",
               "Among adjacent pairs, the sum <code>a[j-1] + a[j]</code> grows with <code>j</code>, so the best valid one is the highest index <code>j</code> with <code>a[j] - a[j-1] &le; d</code>. Walk <code>j</code> down from the end and stop at the first success; if the loop finishes, the answer is <code>-1</code>. After the O(n log n) sort the scan is O(n)."],
    time="O(n log n)", space="O(n)",
    solution='''def bestPairWithinGap(nums, d):
    a = sorted(nums)
    for j in range(len(a) - 1, 0, -1):
        if a[j] - a[j - 1] <= d:
            return a[j] + a[j - 1]
    return -1
''',
    tests=[[[2, 9, 5, 12, 3], 2], [[5, 3, 8], 0], [[7], 5], [[4, 4], 0], [[4, 5], 0], [[4, 5], 1], [[1, 10, 20, 30], 5], [[10 ** 9, 1, 10 ** 9], 0],
           [[10 ** 9, 1], 10 ** 9], [[6, 6, 6, 1, 1], 0], [[1, 3, 5, 7, 9, 11], 2], [[100, 90, 80, 70, 71], 1]],
)
_r = rnd(7021)
p["tests"].append([[_r.randint(1, 10 ** 6) for _ in range(4000)], 3])
p["tests"].append([[_r.randint(1, 10 ** 9) for _ in range(3000)], 100])
p["tests"].append([[3 * i + 1 for i in range(4500)], 2])
p["tests"].append([[_r.randint(1, 10 ** 9) for _ in range(3000)], 0])


def b_gapsum(nums, d):
    best = -1
    for i in range(len(nums)):
        for j in range(i + 1, len(nums)):
            if abs(nums[i] - nums[j]) <= d and nums[i] + nums[j] > best:
                best = nums[i] + nums[j]
    return best


def v_gapsum(tests):
    for t in tests:
        nums, d = t["args"]
        assert 1 <= len(nums) <= 5000
        assert all(1 <= x <= 10 ** 9 for x in nums)
        assert 0 <= d <= 10 ** 9


CHECKS["largest-pair-sum-within-gap"] = (b_gapsum, lambda r: [[r.randint(1, 20) for _ in range(r.randint(1, 8))], r.randint(0, 5)], "exact")
VALIDATE["largest-pair-sum-within-gap"] = v_gapsum


p = add(
    id="count-pairs-within-gap", title="Count Pairs Within a Value Gap", diff="Easy", topic=TOPIC,
    fn="countClosePairs", params=[("nums", "int[]"), ("d", "int")], ret="int", cmp="exact", tier="extra",
    desc="<p>Given an integer array <code>nums</code> and a non-negative integer <code>d</code>, count the pairs of positions <code>(i, j)</code> with <code>i &lt; j</code> whose values differ by at most <code>d</code>: <code>|nums[i] - nums[j]| &le; d</code>.</p><p>Pairs at different positions are counted separately even when their values are equal.</p><pre>nums = [1, 5, 3, 9, 4], d = 2\nsorted: 1 3 4 5 9\npairs: (1,3) (3,4) (3,5) (4,5)\nresult = 4\n\nnums = [7, 7, 7, 2], d = 0\nresult = 3</pre>",
    constraints=["1 &le; nums.length &le; 5,000", "-10<sup>9</sup> &le; nums[i] &le; 10<sup>9</sup>", "0 &le; d &le; 2&middot;10<sup>9</sup>"],
    hints=["Only the values matter, not the positions, so you can reorder the array. What does sorting give you?",
           "In a sorted array, the partners of <code>a[j]</code> among earlier elements form a contiguous block ending at <code>j - 1</code>.",
           "Keep a left pointer <code>l</code>. For each <code>j</code> move <code>l</code> forward while <code>a[j] - a[l] &gt; d</code>; all indices <code>l..j-1</code> are partners, so add <code>j - l</code>. The pointer never moves backwards, because <code>a[j]</code> only grows."],
    editorial=["After sorting, <code>a[j] - a[k]</code> is non-increasing in <code>k</code> for a fixed <code>j</code>, so the earlier elements within distance <code>d</code> form a suffix of the prefix <code>a[0..j-1]</code>, starting at the first index <code>l</code> with <code>a[j] - a[l] &le; d</code>. Counting them is just <code>j - l</code>.",
               "When <code>j</code> increases, <code>a[j]</code> does not decrease, so the first acceptable index <code>l</code> cannot move left. Two monotone pointers therefore cover the array in O(n) after the O(n log n) sort. The answer is at most n(n-1)/2, about 12.5 million, which fits in 32 bits."],
    time="O(n log n)", space="O(n)",
    solution='''def countClosePairs(nums, d):
    a = sorted(nums)
    l = 0
    count = 0
    for j in range(len(a)):
        while a[j] - a[l] > d:
            l += 1
        count += j - l
    return count
''',
    tests=[[[1, 5, 3, 9, 4], 2], [[7, 7, 7, 2], 0], [[3], 5], [[1, 2], 0], [[1, 2], 1], [[-5, 5], 9], [[-5, 5], 10], [[0, 0, 0, 0], 0],
           [[-10 ** 9, 10 ** 9], 2 * 10 ** 9], [[-10 ** 9, 10 ** 9, 0], 10 ** 9], [[1, 2, 3, 4, 5, 6], 3], [[10, -10, 20, -20, 0], 15]],
)
_r = rnd(7022)
p["tests"].append([[_r.randint(-10 ** 6, 10 ** 6) for _ in range(4000)], 20000])
p["tests"].append([[_r.randint(-100, 100) for _ in range(5000)], 7])
p["tests"].append([[_r.randint(-10 ** 9, 10 ** 9) for _ in range(2500)], 10 ** 9])


def b_closepairs(nums, d):
    return sum(1 for i in range(len(nums)) for j in range(i + 1, len(nums)) if abs(nums[i] - nums[j]) <= d)


def v_closepairs(tests):
    for t in tests:
        nums, d = t["args"]
        assert 1 <= len(nums) <= 5000
        assert all(-10 ** 9 <= x <= 10 ** 9 for x in nums)
        assert 0 <= d <= 2 * 10 ** 9


CHECKS["count-pairs-within-gap"] = (b_closepairs, lambda r: [gen_arr(r, -8, 8, 1, 9), r.randint(0, 6)], "exact")
VALIDATE["count-pairs-within-gap"] = v_closepairs


p = add(
    id="max-people-ferried-fixed-boats", title="Most People Ferried With Limited Boats", diff="Medium", topic=TOPIC,
    fn="maxFerried", params=[("weights", "int[]"), ("limit", "int"), ("boats", "int")], ret="int", cmp="exact", tier="extra",
    desc="<p>People wait at a river bank; <code>weights[i]</code> is the weight of person <code>i</code>. You have <code>boats</code> boats, each used for a single trip. A boat carries at most <strong>two</strong> people, and the total weight on one boat must not exceed <code>limit</code>.</p><p>Not everyone may fit. Return the largest number of people that can be carried across.</p><pre>weights = [5, 1, 4, 2, 3], limit = 6, boats = 2\nboats: (1,4) and (2,3)  -&gt;  4 people\nresult = 4\n\nweights = [7, 8, 2], limit = 7, boats = 3\nthe person of weight 8 can never ride\nresult = 2</pre>",
    constraints=["1 &le; weights.length &le; 5,000", "1 &le; weights[i] &le; 10<sup>9</sup>", "1 &le; limit &le; 2&middot;10<sup>9</sup>", "1 &le; boats &le; 5,000"],
    hints=["If you decide to carry exactly <code>m</code> people, which <code>m</code> people should they be?",
           "Replacing a carried person with a lighter one who stays behind never hurts, so the carried group can always be the <code>m</code> lightest people. Also, if <code>m</code> people fit in the boats, then <code>m - 1</code> fit too.",
           "Sort and binary search <code>m</code>. For a given <code>m</code>, the lightest <code>m</code> people need at most <code>boats</code> boats if the heaviest of them weighs at most <code>limit</code> and the classic two-pointer pairing (lightest with heaviest if they fit, otherwise heaviest alone) uses at most <code>boats</code> boats."],
    editorial=["Sort the weights. If some set of people can cross, swapping any member for a lighter person outside the set keeps all boat loads within the limit, so the lightest <code>m</code> people are always the best choice for a group of size <code>m</code>. A smaller group of the lightest people is also never harder than a larger one, so feasibility is monotone in <code>m</code>.",
               "Feasibility of <code>m</code>: the heaviest of the group must satisfy <code>w[m-1] &le; limit</code>, and the minimum number of boats for the group, computed by the standard greedy (heaviest person takes the lightest remaining one if they fit, otherwise travels alone), must be at most <code>boats</code>. Binary search the largest feasible <code>m</code>.",
               "Each check is a linear two-pointer pass, so the total time is O(n log n) for the sort plus O(n log n) for the binary search."],
    time="O(n log n)", space="O(n)",
    solution='''def maxFerried(weights, limit, boats):
    w = sorted(weights)
    n = len(w)

    def feasible(m):
        if m == 0:
            return True
        if w[m - 1] > limit:
            return False
        lo, hi = 0, m - 1
        used = 0
        while lo <= hi:
            if w[lo] + w[hi] <= limit:
                lo += 1
            hi -= 1
            used += 1
        return used <= boats

    lo, hi = 0, n
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if feasible(mid):
            lo = mid
        else:
            hi = mid - 1
    return lo
''',
    tests=[[[5, 1, 4, 2, 3], 6, 2], [[7, 8, 2], 7, 3], [[5], 5, 1], [[5], 4, 1], [[3, 3], 6, 1], [[3, 3], 5, 1], [[3, 3, 3], 6, 1],
           [[1, 1, 1, 1, 1], 2, 2], [[1, 1, 1, 1, 1], 2, 3], [[10, 20, 30, 40], 50, 2], [[10 ** 9, 10 ** 9], 2 * 10 ** 9, 1],
           [[9, 1, 8, 2, 7, 3], 10, 3]],
)
_r = rnd(7023)
p["tests"].append([[_r.randint(1, 100000) for _ in range(5000)], 100000, 2000])
p["tests"].append([[_r.randint(1, 10 ** 9) for _ in range(3000)], 1000000000, 900])
p["tests"].append([[_r.randint(1, 1000) for _ in range(5000)], 1200, 5000])


def b_ferried(weights, limit, boats):
    n = len(weights)
    need = [0] * (1 << n)
    for mask in range(1, 1 << n):
        i = (mask & -mask).bit_length() - 1
        rest = mask & ~(1 << i)
        best = 1 + need[rest]
        for j in range(n):
            if (rest >> j) & 1 and weights[i] + weights[j] <= limit:
                best = min(best, 1 + need[rest & ~(1 << j)])
        need[mask] = best
    ans = 0
    for mask in range(1 << n):
        if all(weights[i] <= limit for i in range(n) if (mask >> i) & 1) and need[mask] <= boats:
            ans = max(ans, bin(mask).count("1"))
    return ans


def v_ferried(tests):
    for t in tests:
        w, limit, boats = t["args"]
        assert 1 <= len(w) <= 5000
        assert all(1 <= x <= 10 ** 9 for x in w)
        assert 1 <= limit <= 2 * 10 ** 9
        assert 1 <= boats <= 5000


CHECKS["max-people-ferried-fixed-boats"] = (b_ferried, lambda r: [[r.randint(1, 10) for _ in range(r.randint(1, 8))], r.randint(1, 14), r.randint(1, 5)], "exact")
VALIDATE["max-people-ferried-fixed-boats"] = v_ferried


# ---------------------------------------------------------------- HARD (continued)

p = add(
    id="max-tasks-with-strength-pills", title="Assign Tasks to Workers With Strength Pills", diff="Hard", topic=TOPIC,
    fn="maxTasksWithPills", params=[("tasks", "int[]"), ("workers", "int[]"), ("pills", "int"), ("strength", "int")], ret="int", cmp="exact", tier="extra",
    desc="<p><code>tasks[i]</code> is the strength needed to do task <code>i</code>, and <code>workers[j]</code> is the strength of worker <code>j</code>. Every worker can do at most one task, every task can be done by at most one worker, and a worker can take a task only if the worker's strength is at least the task's requirement.</p><p>You also have <code>pills</code> magic pills. A pill raises the strength of the worker who takes it by exactly <code>strength</code>; each worker may take at most one pill, and each pill is used at most once.</p><p>Return the maximum number of tasks that can be completed.</p><pre>tasks = [5, 4], workers = [2, 5], pills = 1, strength = 3\nworker 2 takes a pill (strength 5) and does task 4; worker 5 does task 5\nresult = 2\n\ntasks = [10, 9, 8], workers = [4, 7, 12], pills = 1, strength = 3\nresult = 2</pre>",
    constraints=["1 &le; tasks.length, workers.length &le; 2,000", "1 &le; tasks[i], workers[j] &le; 10<sup>9</sup>", "0 &le; pills &le; workers.length", "1 &le; strength &le; 10<sup>9</sup>"],
    hints=["Try to answer a simpler question first: can the <code>k</code> tasks be done? And if <code>k</code> tasks can be done, can <code>k - 1</code>?",
           "If exactly <code>k</code> tasks are done, they may as well be the <code>k</code> easiest tasks, performed by the <code>k</code> strongest workers. Binary search on <code>k</code> and design a greedy check for fixed <code>k</code>.",
           "In the check, handle the tasks from hardest to easiest. Keep a deque of workers who could do the current task if given a pill (ascending strength). If the strongest worker can do it unaided, let them (no pill spent); otherwise a pill is needed and the <em>weakest</em> worker in the deque is the right one to receive it."],
    editorial=["Feasibility is monotone: if <code>k</code> tasks can be completed, any <code>k - 1</code> of them can too. For a given <code>k</code>, using the easiest <code>k</code> tasks and the strongest <code>k</code> workers is optimal by a simple exchange argument. So binary search the largest feasible <code>k</code>.",
               "To check a fixed <code>k</code>, sort both lists and process the chosen tasks from hardest to easiest. Maintain a deque of the chosen workers who can do the current task <em>with</em> a pill (workers are added in decreasing strength, so the deque is ascending from front to back). For the current task: if the strongest worker (back) can do it without a pill, assign them, since the hardest remaining task should use the strongest worker if it can. Otherwise a pill must be spent; give it to the weakest worker who can still do the task, which is the front of the deque; that keeps the stronger workers available for the remaining tasks. If the deque is empty, or a pill is needed but none remain, the check fails.",
               "Every worker enters and leaves the deque at most once, so a check is O(n + m), and the total time is O(n log n + m log m + (n + m) log min(n, m))."],
    time="O((n + m) log(n + m))", space="O(n + m)",
    solution='''from collections import deque


def maxTasksWithPills(tasks, workers, pills, strength):
    t = sorted(tasks)
    w = sorted(workers)
    n, m = len(t), len(w)

    def can(k):
        left = pills
        dq = deque()
        ptr = m - 1
        for i in range(k - 1, -1, -1):
            while ptr >= m - k and w[ptr] + strength >= t[i]:
                dq.appendleft(w[ptr])
                ptr -= 1
            if not dq:
                return False
            if dq[-1] >= t[i]:
                dq.pop()
            else:
                if left == 0:
                    return False
                left -= 1
                dq.popleft()
        return True

    lo, hi = 0, min(n, m)
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if can(mid):
            lo = mid
        else:
            hi = mid - 1
    return lo
''',
    tests=[[[5, 4], [2, 5], 1, 3], [[10, 9, 8], [4, 7, 12], 1, 3], [[3, 2, 1], [1, 3, 3], 1, 1], [[5], [5], 0, 1], [[5], [4], 0, 1], [[5], [4], 1, 1],
           [[5, 5], [4, 4], 1, 1], [[5, 5], [4, 4], 2, 1], [[1, 1, 1], [1], 1, 5], [[2, 4, 6, 8], [1, 3, 5, 7], 2, 1],
           [[10 ** 9, 10 ** 9], [1, 10 ** 9], 1, 10 ** 9], [[6, 2, 9, 4, 7], [3, 8, 5, 1, 6], 2, 3]],
)
_r = rnd(7024)
p["tests"].append([[_r.randint(1, 10 ** 6) for _ in range(2000)], [_r.randint(1, 10 ** 6) for _ in range(2000)], 500, 150000])
p["tests"].append([[_r.randint(1, 10 ** 9) for _ in range(1500)], [_r.randint(1, 10 ** 9) for _ in range(1800)], 700, 250000000])
p["tests"].append([[_r.randint(1, 1000) for _ in range(2000)], [_r.randint(1, 1000) for _ in range(1500)], 100, 40])
p["tests"].append([[_r.randint(500, 1000) for _ in range(2000)], [_r.randint(1, 600) for _ in range(2000)], 2000, 450])


def b_tasks(tasks, workers, pills, strength):
    t = sorted(tasks)
    w = list(workers)
    n, m = len(t), len(w)
    memo = {}

    def go(i, mask, left):
        if i == n:
            return 0
        key = (i, mask, left)
        if key in memo:
            return memo[key]
        best = go(i + 1, mask, left)
        for j in range(m):
            if not (mask >> j) & 1:
                if w[j] >= t[i]:
                    best = max(best, 1 + go(i + 1, mask | (1 << j), left))
                elif left > 0 and w[j] + strength >= t[i]:
                    best = max(best, 1 + go(i + 1, mask | (1 << j), left - 1))
        memo[key] = best
        return best

    return go(0, 0, pills)


def g_tasks(r):
    n = r.randint(1, 5)
    m = r.randint(1, 5)
    return [[r.randint(1, 9) for _ in range(n)], [r.randint(1, 9) for _ in range(m)], r.randint(0, m), r.randint(1, 5)]


def v_tasks(tests):
    for t in tests:
        tasks, workers, pills, strength = t["args"]
        assert 1 <= len(tasks) <= 2000 and 1 <= len(workers) <= 2000
        assert all(1 <= x <= 10 ** 9 for x in tasks + workers)
        assert 0 <= pills <= len(workers)
        assert 1 <= strength <= 10 ** 9


CHECKS["max-tasks-with-strength-pills"] = (b_tasks, g_tasks, "exact")
VALIDATE["max-tasks-with-strength-pills"] = v_tasks
