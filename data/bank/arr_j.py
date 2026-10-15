"""Problems: arrays & hashing, interview classics (batch J). See data/lib.py for the registry."""
import math
from collections import Counter
from itertools import combinations

from lib import add, rnd, CHECKS, VALIDATE, gen_arr  # noqa: F401

INT_MIN, INT_MAX = -(2 ** 31), 2 ** 31 - 1
TOPIC = "Arrays & Hashing"


# ---------------------------------------------------------------- EASY

p = add(
    id="find-pivot-index", title="Find Pivot Index", diff="Easy", topic=TOPIC,
    fn="pivotIndex", params=[("nums", "int[]")], ret="int", cmp="exact",
    desc="<p>A <em>pivot index</em> of the integer array <code>nums</code> is an index whose left side and right side have the same sum. The left side is every element strictly before the index and the right side is every element strictly after it. An empty side counts as sum <code>0</code>.</p><p>Return the <strong>leftmost</strong> pivot index, or <code>-1</code> if none exists.</p><p>For example, in <code>[1, 7, 3, 6, 5, 6]</code> index <code>3</code> is the pivot: <code>1 + 7 + 3 = 11 = 5 + 6</code>. In <code>[2, 1, -1]</code> index <code>0</code> is the pivot, because its left side is empty (sum 0) and <code>1 + (-1) = 0</code>.</p>",
    constraints=["1 &le; nums.length &le; 10,000", "-1,000 &le; nums[i] &le; 1,000"],
    hints=["For a fixed index <code>i</code> you could add up both sides directly. That costs O(n) per index, so what repeated work can you avoid?",
           "Let <code>total</code> be the sum of the whole array. If you know the sum <code>left</code> of everything before <code>i</code>, the sum after <code>i</code> is <code>total - left - nums[i]</code>.",
           "Scan from left to right keeping a running <code>left</code> sum. At each index compare <code>left</code> with <code>total - left - nums[i]</code>, and return the first index where they match."],
    editorial=["Compute the total sum once. Then walk through the array while maintaining <code>left</code>, the sum of the elements before the current index. The right sum at index <code>i</code> is <code>total - left - nums[i]</code>, so the index is a pivot exactly when <code>left == total - left - nums[i]</code>. Because we scan from the left and stop at the first match, we automatically return the leftmost pivot.",
               "This is the prefix-sum idea in its lightest form: one pass for the total, one pass for the check, and only a couple of variables. Negative numbers and zeros need no special treatment, which is why the answer can be several indices apart even in short arrays (for instance every index of an all-zero array is a pivot, and the leftmost one is 0)."],
    time="O(n)", space="O(1)",
    solution='''def pivotIndex(nums):
    total = sum(nums)
    left = 0
    for i, x in enumerate(nums):
        if left == total - left - x:
            return i
        left += x
    return -1
''',
    tests=[[[1, 7, 3, 6, 5, 6]], [[1, 2, 3]], [[2, 1, -1]], [[5]], [[0, 0, 0]], [[-1, -1, 0, 1, 1, 0]],
           [[1, -1, 0]], [[3, -3, 3, -3]], [[-1000, 1000, 5, -1000, 1000]]],
)
_r = rnd(7101)


def _mk_pivot(r, nl, nr, lo=-1000, hi=1000):
    left = [r.randint(lo, hi) for _ in range(nl)]
    right = [r.randint(lo, hi) for _ in range(nr)]
    diff = sum(left) - sum(right)
    fill = []
    while diff != 0:
        step = max(lo, min(hi, diff))
        fill.append(step)
        diff -= step
    right += fill
    a = left + [r.randint(lo, hi)] + right
    return a


p["tests"].append([[0] * 9999 + [1]])
p["tests"].append([_mk_pivot(_r, 3500, 3800)])
p["tests"].append([[_r.randint(1, 1000) for _ in range(6000)]])


def b_pivot(nums):
    for i in range(len(nums)):
        if sum(nums[:i]) == sum(nums[i + 1:]):
            return i
    return -1


def g_pivot(r):
    if r.random() < 0.4:
        return _mk_pivot(r, r.randint(0, 3), r.randint(0, 3), -3, 3)
    return gen_arr(r, -3, 3, 1, 8)


def v_pivot(tests):
    for t in tests:
        a = t["args"][0]
        assert 1 <= len(a) <= 10000 and all(-1000 <= x <= 1000 for x in a)


CHECKS["find-pivot-index"] = (b_pivot, lambda r: [g_pivot(r)], "exact")
VALIDATE["find-pivot-index"] = v_pivot

p = add(
    id="stock-profit-unlimited-transactions", title="Best Time to Trade Stock II", diff="Easy", topic=TOPIC, tier="must",
    fn="maxProfit", params=[("prices", "int[]")], ret="int", cmp="exact",
    desc="<p><code>prices[i]</code> is the price of a stock on day <code>i</code>. You may buy and sell as often as you like, but you can hold <strong>at most one share</strong> at any time: you must sell before buying again. Selling and buying on the same day is allowed.</p><p>Return the maximum total profit. If no profitable trade exists, return <code>0</code>.</p><p>For example, <code>[7, 1, 5, 3, 6, 4]</code> gives <code>7</code>: buy at 1 and sell at 5 (profit 4), then buy at 3 and sell at 6 (profit 3).</p>",
    constraints=["1 &le; prices.length &le; 10,000", "0 &le; prices[i] &le; 10,000"],
    hints=["Think about each pair of neighbouring days on its own. When is it worth holding the share over that one night?",
           "A long profitable trade is the same as a chain of one-day trades: buying at 1 and selling at 6 equals gaining each day-to-day rise in between.",
           "Add up <code>prices[i] - prices[i-1]</code> over every day where that difference is positive."],
    editorial=["Because there is no limit on the number of trades and no fee, any climb from a low to a high can be split into the sum of its day-to-day increases. Capturing every positive increase and skipping every decrease is therefore the best possible: no strategy can collect more than the sum of all rises, and this one collects exactly that.",
               "So the answer is <code>sum(max(0, prices[i] - prices[i-1]))</code>. A two-state DP (best profit while holding, best profit while not holding) gives the same result and generalises to variants with a cooldown or a transaction fee, where the simple greedy no longer applies."],
    time="O(n)", space="O(1)",
    solution='''def maxProfit(prices):
    profit = 0
    for i in range(1, len(prices)):
        if prices[i] > prices[i - 1]:
            profit += prices[i] - prices[i - 1]
    return profit
''',
    tests=[[[7, 1, 5, 3, 6, 4]], [[1, 2, 3, 4, 5]], [[5, 4, 3, 2, 1]], [[3]], [[2, 2, 2]], [[1, 5]], [[5, 1]],
           [[3, 3, 5, 0, 0, 3, 1, 4]], [[0, 10000, 0, 10000, 0]]],
)
_r = rnd(7102)
p["tests"].append([[0 if i % 2 == 0 else 10000 for i in range(6000)]])
_a = [5000]
for _ in range(6999):
    _a.append(max(0, min(10000, _a[-1] + _r.randint(-300, 300))))
p["tests"].append([_a])
p["tests"].append([[_r.randint(0, 10000) for _ in range(5000)]])


def b_profit(prices):
    # exhaustive search over "hold / not hold" decisions
    best = 0

    def go(day, holding, cash):
        nonlocal best
        if day == len(prices):
            if not holding:
                best = max(best, cash)
            return
        go(day + 1, holding, cash)
        if holding:
            go(day + 1, False, cash + prices[day])
        else:
            go(day + 1, True, cash - prices[day])
    go(0, False, 0)
    return best


def v_profit(tests):
    for t in tests:
        a = t["args"][0]
        assert 1 <= len(a) <= 10000 and all(0 <= x <= 10000 for x in a)


CHECKS["stock-profit-unlimited-transactions"] = (b_profit, lambda r: [gen_arr(r, 0, 9, 1, 10)], "exact")
VALIDATE["stock-profit-unlimited-transactions"] = v_profit

p = add(
    id="min-moves-to-equal-elements", title="Minimum Moves to Equal Array Elements", diff="Easy", topic=TOPIC, tier="extra",
    fn="minMoves", params=[("nums", "int[]")], ret="int", cmp="exact",
    desc="<p>In one move you choose one index and then add <code>1</code> to <strong>every other</strong> element (all elements except the chosen one). Return the minimum number of moves needed to make all elements of <code>nums</code> equal.</p><p>For example, <code>[1, 2, 3]</code> needs <code>3</code> moves: <code>[1,2,3] &rarr; [2,3,3] &rarr; [3,4,3] &rarr; [4,4,4]</code>.</p>",
    constraints=["1 &le; nums.length &le; 10,000", "1 &le; nums[i] &le; 100,000"],
    hints=["Simulating the moves is hopeless for large values. Look for what a single move does to the <em>differences</em> between elements.",
           "Raising all elements except one by 1 changes the differences exactly like lowering that one element by 1 would.",
           "So each move can lower one element by 1 relative to the rest, and everything must come down to the minimum. Count the total amount above the minimum."],
    editorial=["Adding 1 to n-1 elements keeps every pairwise difference between those elements and shifts the chosen element relative to them by -1. For the question of when all elements are equal only the differences matter, so the problem is the same as: in one move you may decrease a single element by 1, and you want all elements equal.",
               "The cheapest common target is the current minimum, because lowering anything below it just costs more. Hence the answer is <code>sum(nums) - n * min(nums)</code>. With the given limits this is at most 10,000 &times; 100,000 = 10<sup>9</sup>, which fits in a 32-bit integer."],
    time="O(n)", space="O(1)",
    solution='''def minMoves(nums):
    return sum(nums) - len(nums) * min(nums)
''',
    tests=[[[1, 2, 3]], [[1, 1, 1]], [[5]], [[1, 100000]], [[3, 3, 4]], [[7, 2, 9, 2, 4]], [[1, 1, 1, 1, 2]],
           [[100000, 100000]], [[2, 1]]],
)
_r = rnd(7103)
p["tests"].append([[100000] * 3000 + [1] * 3000])
p["tests"].append([[_r.randint(1, 100000) for _ in range(7000)]])
p["tests"].append([[_r.randint(1, 5) for _ in range(4000)]])


def b_moves(nums):
    a = list(nums)
    moves = 0
    while len(set(a)) > 1:
        k = a.index(max(a))
        a = [v + 1 if i != k else v for i, v in enumerate(a)]
        moves += 1
    return moves


def v_moves(tests):
    for t in tests:
        a = t["args"][0]
        assert 1 <= len(a) <= 10000 and all(1 <= x <= 100000 for x in a)


CHECKS["min-moves-to-equal-elements"] = (b_moves, lambda r: [gen_arr(r, 1, 4, 1, 5)], "exact")
VALIDATE["min-moves-to-equal-elements"] = v_moves


# ---------------------------------------------------------------- MEDIUM

p = add(
    id="majority-element-ii", title="Majority Element II", diff="Medium", topic=TOPIC,
    fn="majorityElementII", params=[("nums", "int[]")], ret="int[]", cmp="exact",
    desc="<p>Given an integer array <code>nums</code> of length <code>n</code>, return every value that appears <strong>strictly more than</strong> <code>n / 3</code> times (real division, so for <code>n = 8</code> a value needs at least 3 occurrences).</p><p>Return the values as an array sorted in ascending order. The array is empty if no value qualifies. Aim for O(n) time and O(1) extra space.</p><p>For example, <code>[1, 1, 1, 3, 3, 2, 2, 2]</code> gives <code>[1, 2]</code>.</p>",
    constraints=["1 &le; nums.length &le; 10,000", "-2<sup>31</sup> &le; nums[i] &le; 2<sup>31</sup> - 1"],
    hints=["How many different values can possibly occur more than n/3 times? Each needs more than a third of the slots.",
           "At most two values qualify. Generalise the one-candidate voting trick from the plain majority problem to two candidates with two counters.",
           "Maintain two candidates and counters: a match increments its counter, an empty counter adopts the new value, and otherwise both counters drop by one. Finish with a second pass that counts the two survivors exactly."],
    editorial=["Three distinct values cannot each exceed n/3 occurrences, so the answer has at most two elements. Boyer-Moore voting extends naturally: keep two candidates with counters. For each element, if it equals a candidate bump that counter; else if a counter is zero take the element as the new candidate; else decrement both counters (this cancels three distinct values against each other, and a value that occurs more than n/3 times cannot be fully cancelled).",
               "The voting pass only produces candidates that <em>might</em> qualify, so a second pass must count them and keep those whose count is really above n/3. Sort the (at most two) results before returning. A hash map of counts is the simpler O(n)-space alternative."],
    time="O(n)", space="O(1)",
    solution='''def majorityElementII(nums):
    c1 = c2 = None
    n1 = n2 = 0
    for x in nums:
        if x == c1:
            n1 += 1
        elif x == c2:
            n2 += 1
        elif n1 == 0:
            c1, n1 = x, 1
        elif n2 == 0:
            c2, n2 = x, 1
        else:
            n1 -= 1
            n2 -= 1
    n = len(nums)
    res = []
    for c in (c1, c2):
        if c is not None and 3 * nums.count(c) > n:
            res.append(c)
    return sorted(res)
''',
    tests=[[[3, 2, 3]], [[1]], [[1, 2]], [[1, 1, 1, 3, 3, 2, 2, 2]], [[1, 2, 3]], [[2, 2, 9, 9]],
           [[INT_MIN, INT_MAX, INT_MIN, INT_MAX, 0]], [[4, 4, 4, 4]], [[1, 2, 3, 1, 2, 3]], [[5, 6, 6, 7, 5, 5, 6, 8]]],
)
_r = rnd(7104)


def _mix(r, parts):
    a = []
    for v, c in parts:
        a += [v] * c
    r.shuffle(a)
    return a


p["tests"].append([_mix(_r, [(11, 2000), (-22, 2000), (33, 2000)])])  # nobody above n/3 -> []
p["tests"].append([_mix(_r, [(7, 2400), (8, 2400)] + [(_r.randint(-10 ** 9, 10 ** 9), 1) for _ in range(2200)])])
p["tests"].append([_mix(_r, [(INT_MAX, 2000), (5, 100)] + [(i, 1) for i in range(-2000, 1900 - 100)])])
p["tests"].append([_mix(_r, [(1, 3333), (2, 3333), (3, 3334)])])


def b_major2(nums):
    c = Counter(nums)
    return sorted(v for v, k in c.items() if k * 3 > len(nums))


def g_major2(r):
    n = r.randint(1, 11)
    vals = [r.randint(-2, 2) for _ in range(r.randint(1, 3))]
    return [r.choice(vals) if r.random() < 0.8 else r.randint(-4, 4) for _ in range(n)]


def v_major2(tests):
    for t in tests:
        a = t["args"][0]
        assert 1 <= len(a) <= 10000
        assert t["expected"] == sorted(set(t["expected"]))


CHECKS["majority-element-ii"] = (b_major2, lambda r: [g_major2(r)], "exact")
VALIDATE["majority-element-ii"] = v_major2

p = add(
    id="rearrange-array-by-sign", title="Rearrange Array Elements by Sign", diff="Medium", topic=TOPIC,
    fn="rearrangeBySign", params=[("nums", "int[]")], ret="int[]", cmp="exact",
    desc="<p>The array <code>nums</code> has an even length and contains exactly as many positive numbers as negative numbers (there are no zeros). Rearrange it so that:</p><ul><li>positive and negative numbers alternate, starting with a positive number (positives at even indices, negatives at odd indices), and</li><li>the positives keep their original relative order, and so do the negatives.</li></ul><p>Return the rearranged array. For example, <code>[3, 1, -2, -5, 2, -4]</code> becomes <code>[3, -2, 1, -5, 2, -4]</code>.</p>",
    constraints=["2 &le; nums.length &le; 6,000 and nums.length is even", "-100,000 &le; nums[i] &le; 100,000, nums[i] != 0", "Exactly nums.length / 2 elements are positive"],
    hints=["The result is fully determined: slot 0 gets the first positive, slot 1 the first negative, slot 2 the second positive, and so on.",
           "Splitting into two lists and interleaving works in O(n) but with extra lists. Can you write each element straight to its final position?",
           "Keep two write pointers: <code>pos = 0</code> stepping by 2 for positives and <code>neg = 1</code> stepping by 2 for negatives. Scan the input once and place every element at the pointer of its sign."],
    editorial=["Since the counts of positives and negatives are equal and the order inside each group must be preserved, the k-th positive must land at index <code>2k</code> and the k-th negative at index <code>2k + 1</code>. Scanning the input once with two independent write pointers, one for even and one for odd output slots, produces exactly that.",
               "This is a stable partition into an output array. Doing it truly in place while keeping both orders is much harder (it needs rotations and costs O(n<sup>2</sup>) or fancier merge tricks), which is why the problem is normally solved with an output array of size n."],
    time="O(n)", space="O(n)",
    solution='''def rearrangeBySign(nums):
    res = [0] * len(nums)
    pos, neg = 0, 1
    for x in nums:
        if x > 0:
            res[pos] = x
            pos += 2
        else:
            res[neg] = x
            neg += 2
    return res
''',
    tests=[[[3, 1, -2, -5, 2, -4]], [[1, -1]], [[-1, 1]], [[-3, -2, 1, 2]], [[5, 6, -7, -8]], [[-1, -2, -3, 4, 5, 6]],
           [[1, -1, 2, -2, 3, -3]], [[100000, -100000]], [[-5, 4, -3, 2, -1, 7, 8, -9]]],
)
_r = rnd(7105)


def _mk_sign(r, half, lim=100000):
    a = [r.randint(1, lim) for _ in range(half)] + [-r.randint(1, lim) for _ in range(half)]
    r.shuffle(a)
    return a


p["tests"].append([_mk_sign(_r, 3000)])
p["tests"].append([[-(i + 1) for i in range(2000)] + [i + 1 for i in range(2000)]])
p["tests"].append([_mk_sign(_r, 2500, 9)])


def b_sign(nums):
    used = [False] * len(nums)
    out = []
    for i in range(len(nums)):
        want_pos = i % 2 == 0
        for j, x in enumerate(nums):
            if not used[j] and (x > 0) == want_pos:
                used[j] = True
                out.append(x)
                break
    return out


def g_sign(r):
    return _mk_sign(r, r.randint(1, 5), 6)


def v_sign(tests):
    for t in tests:
        a = t["args"][0]
        assert 2 <= len(a) <= 6000 and len(a) % 2 == 0 and all(x != 0 and abs(x) <= 100000 for x in a)
        assert sum(1 for x in a if x > 0) == len(a) // 2


CHECKS["rearrange-array-by-sign"] = (b_sign, lambda r: [g_sign(r)], "exact")
VALIDATE["rearrange-array-by-sign"] = v_sign

p = add(
    id="maximum-product-subarray", title="Maximum Product Subarray", diff="Medium", topic=TOPIC, tier="must",
    fn="maxProduct", params=[("nums", "int[]")], ret="int", cmp="exact",
    desc="<p>Find the non-empty contiguous subarray of <code>nums</code> whose elements have the largest product, and return that product.</p><p>The array may contain negative numbers and zeros. It is guaranteed that the product of <em>every</em> contiguous subarray fits in a 32-bit signed integer.</p><p>Examples: <code>[2, 3, -2, 4]</code> gives <code>6</code> (subarray <code>[2, 3]</code>); <code>[-2, 3, -4]</code> gives <code>24</code> (the whole array).</p>",
    constraints=["1 &le; nums.length &le; 10,000", "-10 &le; nums[i] &le; 10", "The product of any contiguous subarray fits in a signed 32-bit integer"],
    hints=["Maximum Subarray (Kadane) tracks the best sum ending here. Why is tracking only the best <em>product</em> ending here not enough?",
           "A very negative product can become the largest one after multiplying by another negative number. So also track the smallest product of a subarray ending at the current index.",
           "At each element <code>x</code>, the new max is <code>max(x, maxEnd * x, minEnd * x)</code> and the new min is <code>min(x, maxEnd * x, minEnd * x)</code>. Keep the best max seen so far."],
    editorial=["Let <code>mx</code> and <code>mn</code> be the largest and smallest products of subarrays ending at the previous index. A subarray ending at the current element <code>x</code> is either just <code>[x]</code> or an earlier subarray extended by <code>x</code>. Extending the previous maximum by a negative <code>x</code> gives a small value, while extending the previous minimum (a large negative number) by a negative <code>x</code> gives a large value, so both extremes are needed. The new extremes are the max and min over <code>x</code>, <code>mx * x</code> and <code>mn * x</code>.",
               "A zero resets both extremes to zero automatically, because <code>0 * anything = 0</code> and the lone element <code>[x]</code> is always a candidate for the next restart. The answer is the maximum <code>mx</code> seen at any index. One pass, constant memory."],
    time="O(n)", space="O(1)",
    solution='''def maxProduct(nums):
    best = mx = mn = nums[0]
    for x in nums[1:]:
        a, b = mx * x, mn * x
        mx = max(x, a, b)
        mn = min(x, a, b)
        best = max(best, mx)
    return best
''',
    tests=[[[2, 3, -2, 4]], [[-2, 0, -1]], [[-2, 3, -4]], [[-5]], [[0]], [[-1, -1]], [[2, -5, -2, -4, 3]],
           [[0, 0, 0]], [[-2, -3, 0, 5, -1]], [[1, -1, -1, -1]], [[3, -1, 4]]],
)
_r = rnd(7106)


def _mk_prod(r, n, spikes, zero_p=0.05):
    a = [0 if r.random() < zero_p else r.choice((-1, 1)) for _ in range(n)]
    budget = 28.0
    for _ in range(spikes):
        v = r.randint(2, 10)
        if math.log2(v) > budget:
            continue
        budget -= math.log2(v)
        a[r.randrange(n)] = r.choice((-1, 1)) * v
    return a


p["tests"].append([_mk_prod(_r, 10000, 12, 0.0005)])
p["tests"].append([_mk_prod(_r, 8000, 20, 0.002)])
p["tests"].append([[-1] * 9999 + [1]])
p["tests"].append([[1, -1] * 3000])


def b_prod(nums):
    best = nums[0]
    for i in range(len(nums)):
        prod = 1
        for j in range(i, len(nums)):
            prod *= nums[j]
            best = max(best, prod)
    return best


def v_prod(tests):
    for t in tests:
        a = t["args"][0]
        assert 1 <= len(a) <= 10000 and all(-10 <= x <= 10 for x in a)
        # every subarray product has absolute value at most the product of all non-zero absolute values
        assert sum(math.log2(abs(x)) for x in a if x != 0) <= 30.5, "product might overflow"


CHECKS["maximum-product-subarray"] = (b_prod, lambda r: [gen_arr(r, -3, 3, 1, 9)], "exact")
VALIDATE["maximum-product-subarray"] = v_prod

p = add(
    id="maximum-circular-subarray-sum", title="Maximum Sum Circular Subarray", diff="Medium", topic=TOPIC,
    fn="maxCircularSum", params=[("nums", "int[]")], ret="int", cmp="exact",
    desc="<p>The array <code>nums</code> is arranged in a circle: the last element is followed by the first. A <em>circular subarray</em> is a non-empty run of neighbouring elements on this circle that may wrap around the end, and that uses each element at most once.</p><p>Return the largest possible sum of a circular subarray.</p><p>Examples: <code>[1, -2, 3, -2]</code> gives <code>3</code>; <code>[5, -3, 5]</code> gives <code>10</code> (take <code>5</code> at the end and wrap to the <code>5</code> at the start); <code>[-3, -2, -3]</code> gives <code>-2</code>.</p>",
    constraints=["1 &le; nums.length &le; 10,000", "-10,000 &le; nums[i] &le; 10,000"],
    hints=["Without wrap-around this is Kadane's maximum subarray. What does a wrapping subarray look like on the linear array?",
           "A wrapping subarray is the whole array minus one contiguous middle block. To make the wrapping sum large, remove the block with the <em>smallest</em> sum.",
           "Answer = max(Kadane max, total - Kadane min). Careful: if every element is negative, the min block is the whole array and the second option would be an empty subarray, so return the plain Kadane max in that case."],
    editorial=["Either the best subarray lies inside the array without wrapping (classic Kadane maximum), or it wraps. A wrapping subarray consists of a prefix and a suffix, and what remains is a contiguous block in the middle. Its sum is <code>total - middle</code>, which is largest when the middle block has the minimum possible sum, found by a Kadane-style minimum.",
               "One edge case: if all elements are negative, the minimum block is the entire array and <code>total - min</code> would be 0, corresponding to an empty selection, which is not allowed. In that case the Kadane maximum (the largest single element) is the answer. Checking <code>best &lt; 0</code> covers it, since any array with a non-negative element has a non-negative best."],
    time="O(n)", space="O(1)",
    solution='''def maxCircularSum(nums):
    total = 0
    cur_max = cur_min = 0
    best = nums[0]
    worst = nums[0]
    for x in nums:
        cur_max = max(cur_max + x, x)
        best = max(best, cur_max)
        cur_min = min(cur_min + x, x)
        worst = min(worst, cur_min)
        total += x
    if best < 0:
        return best
    return max(best, total - worst)
''',
    tests=[[[1, -2, 3, -2]], [[5, -3, 5]], [[-3, -2, -3]], [[7]], [[-4]], [[3, 1, 2]], [[0, -1]], [[-5, 1, -5]],
           [[2, -1, 2, -1, 2]], [[8, -10, 9]], [[-2, 4, -5, 4, -5, 9, 4]]],
)
_r = rnd(7107)
p["tests"].append([[_r.randint(-10000, 10000) for _ in range(5000)]])
p["tests"].append([[_r.randint(-10000, -1) for _ in range(3000)]])
p["tests"].append([[_r.randint(-3000, 10000) for _ in range(1500)] + [-10000] * 1500 + [_r.randint(-3000, 10000) for _ in range(1500)]])


def b_circ(nums):
    n = len(nums)
    best = None
    for s in range(n):
        tot = 0
        for k in range(n):
            tot += nums[(s + k) % n]
            if best is None or tot > best:
                best = tot
    return best


def v_circ(tests):
    for t in tests:
        a = t["args"][0]
        assert 1 <= len(a) <= 10000 and all(-10000 <= x <= 10000 for x in a)


CHECKS["maximum-circular-subarray-sum"] = (b_circ, lambda r: [gen_arr(r, -6, 6, 1, 9)], "exact")
VALIDATE["maximum-circular-subarray-sum"] = v_circ

p = add(
    id="increasing-triplet-subsequence", title="Increasing Triplet Subsequence", diff="Medium", topic=TOPIC,
    fn="hasIncreasingTriplet", params=[("nums", "int[]")], ret="bool", cmp="exact",
    desc="<p>Return <code>true</code> if there are three indices <code>i &lt; j &lt; k</code> such that <code>nums[i] &lt; nums[j] &lt; nums[k]</code> (strictly increasing values), otherwise return <code>false</code>. The indices do not have to be adjacent.</p><p>Examples: <code>[2, 1, 5, 0, 4, 6]</code> is <code>true</code> (for instance 1, 4, 6); <code>[5, 4, 3, 2, 1]</code> is <code>false</code>. Aim for O(n) time and O(1) extra space.</p>",
    constraints=["1 &le; nums.length &le; 10,000", "-2<sup>31</sup> &le; nums[i] &le; 2<sup>31</sup> - 1"],
    hints=["Trying all triples is O(n<sup>3</sup>). Think about what you need to remember while scanning left to right.",
           "Keep the smallest value seen so far (<code>a</code>) and the smallest value that already has a smaller value before it (<code>b</code>), i.e. the best end of an increasing pair.",
           "For each x: if <code>x &le; a</code> set <code>a = x</code>; else if <code>x &le; b</code> set <code>b = x</code>; otherwise x is larger than a pair end, so return <code>true</code>."],
    editorial=["We maintain the smallest possible last value of an increasing subsequence of length 1 (<code>a</code>) and of length 2 (<code>b</code>). A new value that does not exceed <code>a</code> lowers <code>a</code>; one that exceeds <code>a</code> but not <code>b</code> lowers <code>b</code>; one that exceeds <code>b</code> completes a triple. This is the length-3 special case of the patience-sorting tails array used for the longest increasing subsequence.",
               "A subtle point: when <code>a</code> is lowered after <code>b</code> was set, the old pair behind <code>b</code> is still valid, because a smaller <code>a</code> appearing <em>later</em> does not erase the earlier pair that justified <code>b</code>. Only the existence of some earlier smaller element is needed, not its identity."],
    time="O(n)", space="O(1)",
    solution='''def hasIncreasingTriplet(nums):
    a = b = 1 << 62
    for x in nums:
        if x <= a:
            a = x
        elif x <= b:
            b = x
        else:
            return True
    return False
''',
    tests=[[[1, 2, 3, 4, 5]], [[5, 4, 3, 2, 1]], [[2, 1, 5, 0, 4, 6]], [[1]], [[1, 2]], [[1, 1, 1]],
           [[20, 100, 10, 12, 5, 13]], [[1, 5, 0, 4, 1, 3]], [[INT_MIN, 0, INT_MAX]], [[2, 4, -2, -3]]],
)
_r = rnd(7108)
p["tests"].append([list(range(5000, 0, -1))])
p["tests"].append([[10 ** 6 if i % 2 else i % 7 for i in range(5000)]])
_a = [_r.randint(-10 ** 9, 10 ** 9) for _ in range(3000)]
p["tests"].append([sorted(_a, reverse=True)[:2999] + [INT_MAX]])
p["tests"].append([[3000 - i if i < 3000 else i for i in range(3001)] + [20000]])


def b_triplet(nums):
    n = len(nums)
    return any(nums[i] < nums[j] < nums[k] for i, j, k in combinations(range(n), 3))


def v_triplet(tests):
    for t in tests:
        a = t["args"][0]
        assert 1 <= len(a) <= 10000


CHECKS["increasing-triplet-subsequence"] = (b_triplet, lambda r: [gen_arr(r, -4, 4, 1, 9)], "exact")
VALIDATE["increasing-triplet-subsequence"] = v_triplet

p = add(
    id="shortest-unsorted-subarray-length", title="Shortest Unsorted Continuous Subarray", diff="Medium", topic=TOPIC,
    fn="unsortedLength", params=[("nums", "int[]")], ret="int", cmp="exact",
    desc="<p>Find the shortest contiguous subarray of <code>nums</code> such that sorting just that subarray in non-decreasing order makes the <strong>whole</strong> array sorted in non-decreasing order. Return its length, or <code>0</code> if the array is already sorted.</p><p>Examples: <code>[2, 6, 4, 8, 10, 9, 15]</code> gives <code>5</code> (sort <code>[6, 4, 8, 10, 9]</code>); <code>[1, 3, 2, 2, 2]</code> gives <code>4</code>; <code>[1, 2, 3, 4]</code> gives <code>0</code>.</p>",
    constraints=["1 &le; nums.length &le; 10,000", "-100,000 &le; nums[i] &le; 100,000", "Duplicate values are allowed"],
    hints=["Sorting a copy and comparing it with the original shows the first and last mismatch, which gives an O(n log n) answer. Can you find these two positions in O(n)?",
           "The right end of the window is the last index whose value is smaller than the maximum of everything before it. The left end is the first index whose value is larger than the minimum of everything after it.",
           "Scan left to right keeping the running maximum and mark <code>end = i</code> whenever <code>nums[i]</code> is below it. Scan right to left keeping the running minimum and mark <code>start = i</code> whenever <code>nums[i]</code> is above it."],
    editorial=["An element is out of place on the right side if something larger precedes it, so the rightmost such element marks where the window must end: scanning left to right with the running maximum, the last index with <code>nums[i] &lt; max</code> is the end. Symmetrically, an element is out of place on the left side if something smaller follows it, and the leftmost such index (found by scanning right to left with the running minimum) is the start.",
               "If no index is ever below the running maximum the array is sorted and the answer is 0. Otherwise the answer is <code>end - start + 1</code>. Equal values are never counted as out of order because the comparisons are strict, which is why <code>[1, 3, 2, 2, 2]</code> needs the window <code>[3, 2, 2, 2]</code> but <code>[1, 2, 2, 3]</code> needs nothing."],
    time="O(n)", space="O(1)",
    solution='''def unsortedLength(nums):
    n = len(nums)
    end = -1
    mx = nums[0]
    for i in range(1, n):
        if nums[i] < mx:
            end = i
        else:
            mx = nums[i]
    if end == -1:
        return 0
    start = 0
    mn = nums[-1]
    for i in range(n - 2, -1, -1):
        if nums[i] > mn:
            start = i
        else:
            mn = nums[i]
    return end - start + 1
''',
    tests=[[[2, 6, 4, 8, 10, 9, 15]], [[1, 2, 3, 4]], [[1]], [[2, 1]], [[1, 3, 2, 2, 2]], [[1, 2, 2, 3]],
           [[5, 4, 3, 2, 1]], [[1, 3, 5, 4, 2]], [[2, 2, 2, 2]], [[1, 2, 4, 3, 5, 7, 6, 8]], [[3, 1, 2, 4, 5]]],
)
_r = rnd(7109)
_a = sorted(_r.randint(-100000, 100000) for _ in range(5000))
_b = list(_a)
_b[100], _b[4900] = _b[4900], _b[100]
p["tests"].append([_b])
p["tests"].append([_a])
_c = sorted(_r.randint(-50, 50) for _ in range(5000))
for _ in range(30):
    i, j = sorted(_r.sample(range(1500, 3500), 2))
    _c[i], _c[j] = _c[j], _c[i]
p["tests"].append([_c])
p["tests"].append([[_r.randint(-100000, 100000) for _ in range(4000)]])


def b_unsorted(nums):
    n = len(nums)
    target = sorted(nums)
    if nums == target:
        return 0
    for L in range(1, n + 1):
        for i in range(n - L + 1):
            if nums[:i] + sorted(nums[i:i + L]) + nums[i + L:] == target:
                return L


def v_unsorted(tests):
    for t in tests:
        a = t["args"][0]
        assert 1 <= len(a) <= 10000 and all(-100000 <= x <= 100000 for x in a)


CHECKS["shortest-unsorted-subarray-length"] = (b_unsorted, lambda r: [gen_arr(r, -4, 4, 1, 9)], "exact")
VALIDATE["shortest-unsorted-subarray-length"] = v_unsorted


# ---------------------------------------------------------------- HARD

p = add(
    id="count-smaller-numbers-after-self", title="Count of Smaller Numbers After Self", diff="Hard", topic=TOPIC, tier="extra",
    fn="countSmaller", params=[("nums", "int[]")], ret="int[]", cmp="exact",
    desc="<p>For every index <code>i</code> of <code>nums</code>, count how many elements to its <strong>right</strong> are strictly smaller than <code>nums[i]</code>. Return the array <code>counts</code> where <code>counts[i]</code> is that number.</p><p>For example, <code>[5, 2, 6, 1]</code> gives <code>[2, 1, 1, 0]</code>: to the right of 5 there are 2 and 1; to the right of 2 there is 1; to the right of 6 there is 1; nothing is to the right of the last element.</p>",
    constraints=["1 &le; nums.length &le; 5,000", "-10<sup>9</sup> &le; nums[i] &le; 10<sup>9</sup>"],
    hints=["Comparing every pair is O(n<sup>2</sup>). For a bigger input you need to answer 'how many earlier-inserted values are smaller than x?' quickly.",
           "Process the array from right to left and insert each value into a structure that supports 'count of stored values below x' and 'insert x', both in O(log n).",
           "Compress the values to ranks 1..m (the values can be huge but there are only n of them) and use a Fenwick tree (binary indexed tree) of counts over those ranks. Query the prefix of ranks below the current rank, then add the current rank."],
    editorial=["Walk from the last element to the first. When we reach index <code>i</code> the structure contains exactly the elements to its right, so <code>counts[i]</code> is the number of stored values strictly smaller than <code>nums[i]</code>. A Fenwick tree indexed by compressed rank answers this prefix count in O(log n) and supports the insertion in O(log n).",
               "Coordinate compression (sorting the distinct values and mapping each to its rank) keeps the tree size at most n regardless of how large the values are. Equal values get the same rank, and querying the prefix below the current rank excludes them, which matches the strict 'smaller' in the statement. An alternative with the same O(n log n) bound is a merge sort that counts, during each merge, how many right-half elements jump ahead of every left-half element."],
    time="O(n log n)", space="O(n)",
    solution='''def countSmaller(nums):
    vals = sorted(set(nums))
    rank = {v: i + 1 for i, v in enumerate(vals)}
    m = len(vals)
    tree = [0] * (m + 1)
    res = [0] * len(nums)
    for i in range(len(nums) - 1, -1, -1):
        r = rank[nums[i]]
        k = r - 1
        s = 0
        while k > 0:
            s += tree[k]
            k -= k & -k
        res[i] = s
        k = r
        while k <= m:
            tree[k] += 1
            k += k & -k
    return res
''',
    tests=[[[5, 2, 6, 1]], [[-1]], [[-1, -1]], [[1, 2, 3]], [[3, 2, 1]], [[2, 0, 1]], [[5 * 10 ** 8, -10 ** 9, 10 ** 9, 0]],
           [[4, 4, 4, 1, 1]], [[26, 78, 27, 100, 33, 67, 90, 23, 66, 5, 38, 7, 35, 23, 52, 22, 83, 51, 98, 69]]],
)
_r = rnd(7110)
p["tests"].append([[_r.randint(-10 ** 9, 10 ** 9) for _ in range(3500)]])
p["tests"].append([list(range(3000, 0, -1))])
p["tests"].append([[_r.randint(-5, 5) for _ in range(3500)]])


def b_smaller(nums):
    return [sum(1 for y in nums[i + 1:] if y < nums[i]) for i in range(len(nums))]


def v_smaller(tests):
    for t in tests:
        a = t["args"][0]
        assert 1 <= len(a) <= 5000 and all(abs(x) <= 10 ** 9 for x in a)
        assert len(t["expected"]) == len(a)


CHECKS["count-smaller-numbers-after-self"] = (b_smaller, lambda r: [gen_arr(r, -5, 5, 1, 10)], "exact")
VALIDATE["count-smaller-numbers-after-self"] = v_smaller

p = add(
    id="reverse-pairs-double-count", title="Count Reverse Pairs", diff="Hard", topic=TOPIC, tier="extra",
    fn="reversePairs", params=[("nums", "int[]")], ret="int", cmp="exact",
    desc="<p>A <em>reverse pair</em> is a pair of indices <code>(i, j)</code> with <code>i &lt; j</code> and <code>nums[i] &gt; 2 * nums[j]</code>. Return the number of reverse pairs in <code>nums</code>.</p><p>Do the comparison with exact arithmetic (in languages with 32-bit integers, <code>2 * nums[j]</code> can overflow, so widen to 64 bits first).</p><p>For example, <code>[1, 3, 2, 3, 1]</code> gives <code>2</code>, from the pairs of values <code>(3, 1)</code> at indices (1, 4) and <code>(3, 1)</code> at indices (3, 4). The array <code>[2, 4, 3, 5, 1]</code> gives <code>3</code>.</p>",
    constraints=["1 &le; nums.length &le; 5,000", "-2<sup>31</sup> &le; nums[i] &le; 2<sup>31</sup> - 1"],
    hints=["Checking all pairs is O(n<sup>2</sup>), about 12 million checks at the largest size, which is the baseline to beat. Think about divide and conquer on the array.",
           "Split into a left and right half and count the pairs that cross the middle, plus the pairs fully inside each half (recursion). Sorting each half first makes the crossing count easy.",
           "With both halves sorted, walk through the left half in ascending order and move a pointer <code>j</code> forward in the right half while <code>2 * right[j] &lt; left[i]</code>; the pointer never moves back, and <code>j</code> is the number of valid partners for <code>left[i]</code>."],
    editorial=["This is the merge-sort inversion count with a twist: the counting condition (<code>nums[i] &gt; 2 * nums[j]</code>) is not the same as the sort order. So we count first and merge afterwards. For each half we get its sorted version and its internal pair count by recursion. To count the crossing pairs, iterate over the sorted left half; as <code>left[i]</code> grows, the set of right elements with <code>2 * right[j] &lt; left[i]</code> only grows, so a single moving pointer over the sorted right half gives all counts in linear time. Then merge the two halves and return.",
               "Each level of the recursion does linear work and there are log n levels, so the total is O(n log n). A Fenwick tree over the compressed values of all <code>nums[i]</code> and <code>2 * nums[i]</code> achieves the same bound. Negative numbers need no special handling since the whole argument only uses the ordering of the numbers."],
    time="O(n log n)", space="O(n)",
    solution='''def reversePairs(nums):
    def solve(a):
        if len(a) <= 1:
            return a, 0
        mid = len(a) // 2
        left, cl = solve(a[:mid])
        right, cr = solve(a[mid:])
        cnt = cl + cr
        j = 0
        for x in left:
            while j < len(right) and 2 * right[j] < x:
                j += 1
            cnt += j
        return sorted(left + right), cnt
    return solve(nums)[1]
''',
    tests=[[[1, 3, 2, 3, 1]], [[2, 4, 3, 5, 1]], [[1]], [[0, 0]], [[5, -3]], [[-5, -3]], [[-5, -2]],
           [[INT_MAX, INT_MIN, INT_MAX, INT_MIN]], [[INT_MIN, INT_MAX, 1, 0]], [[3, 3, 3]], [[10, 4, 1, 0, -1, -4, -10]]],
)
_r = rnd(7111)
p["tests"].append([[_r.randint(INT_MIN, INT_MAX) for _ in range(4000)]])
p["tests"].append([list(range(5000, 0, -1))])
p["tests"].append([[_r.randint(-30000, 30000) for _ in range(4500)]])


def b_rev(nums):
    n = len(nums)
    return sum(1 for i in range(n) for j in range(i + 1, n) if nums[i] > 2 * nums[j])


def v_rev(tests):
    for t in tests:
        a = t["args"][0]
        assert 1 <= len(a) <= 5000 and all(INT_MIN <= x <= INT_MAX for x in a)


CHECKS["reverse-pairs-double-count"] = (b_rev, lambda r: [gen_arr(r, -8, 8, 1, 10)], "exact")
VALIDATE["reverse-pairs-double-count"] = v_rev
