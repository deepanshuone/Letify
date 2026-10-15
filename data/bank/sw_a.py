"""Problems: sliding window, fixed-size windows. See data/lib.py for the registry."""
from collections import Counter, deque
from bisect import bisect_left, bisect_right

from lib import add, rnd, CHECKS, VALIDATE, gen_arr  # noqa: F401


# ---------------------------------------------------------------- EASY

p = add(
    id="count-windows-average-at-least-threshold", tier="extra", title="Windows With Average At Least a Threshold", diff="Easy", topic="Sliding Window",
    fn="countGoodWindows", params=[("nums", "int[]"), ("k", "int"), ("threshold", "int")], ret="int", cmp="exact",
    desc="<p>Given an integer array <code>nums</code>, a window length <code>k</code> and an integer <code>threshold</code>, count the contiguous blocks of exactly <code>k</code> elements whose <strong>average is at least</strong> <code>threshold</code>.</p><pre>nums = [2, 2, 2, 2, 5, 5, 5, 8], k = 3, threshold = 4\nwindows: [2,2,2] [2,2,2] [2,2,5] [2,5,5] [5,5,5] [5,5,8]\naverages: 2, 2, 3, 4, 5, 6\nresult = 3</pre>",
    constraints=["1 &le; k &le; nums.length &le; 8,000", "-10,000 &le; nums[i] &le; 10,000", "-10,000 &le; threshold &le; 10,000"],
    hints=["Computing every window's sum from scratch costs O(n * k).",
           "Consecutive windows share k - 1 elements, so one sum can be updated into the next in O(1).",
           "Avoid fractions: a window's average is at least <code>threshold</code> exactly when its sum is at least <code>k * threshold</code>."],
    editorial=["Keep the sum of the current window. Moving the window one step right adds the new element and removes the one that left, so each window costs O(1).",
               "Compare the sum against <code>k * threshold</code> instead of dividing, which keeps everything in exact integer arithmetic (no rounding questions with negative numbers). Count the windows that pass. Time O(n), extra space O(1)."],
    time="O(n)", space="O(1)",
    solution='''def countGoodWindows(nums, k, threshold):
    need = k * threshold
    cur = sum(nums[:k])
    count = 1 if cur >= need else 0
    for i in range(k, len(nums)):
        cur += nums[i] - nums[i - k]
        if cur >= need:
            count += 1
    return count
''',
    tests=[[[2, 2, 2, 2, 5, 5, 5, 8], 3, 4], [[11, 13, 17, 23, 29, 31, 7, 5, 2, 3], 3, 5], [[5], 1, 5], [[5], 1, 6], [[-3, -3, -3], 2, -3],
           [[-3, -3, -4], 2, -3], [[1, 2, 3, 4], 4, 3], [[1, 2, 3, 4], 4, 2], [[0, 0, 0, 0], 2, 0], [[10000, -10000, 10000, -10000], 2, 0],
           [[10000, 10000], 2, 10000], [[-10000, -10000], 1, 10000]],
)
_r = rnd(3101)
p["tests"].append([[_r.randint(-10000, 10000) for _ in range(5000)], 1000, 0])
p["tests"].append([[_r.randint(-20, 20) for _ in range(5000)], 3, 1])
p["tests"].append([[_r.randint(0, 100) for _ in range(5000)], 5000, 50])


def b_good_windows(nums, k, threshold):
    return sum(1 for i in range(len(nums) - k + 1) if sum(nums[i:i + k]) / k >= threshold - 1e-9)


def g_good_windows(r):
    a = gen_arr(r, -9, 9, 1, 10)
    return [a, r.randint(1, len(a)), r.randint(-9, 9)]


def v_good_windows(tests):
    for t in tests:
        a, k, th = t["args"]
        assert 1 <= k <= len(a) <= 8000
        assert all(-10000 <= x <= 10000 for x in a) and -10000 <= th <= 10000


CHECKS["count-windows-average-at-least-threshold"] = (b_good_windows, g_good_windows, "exact")
VALIDATE["count-windows-average-at-least-threshold"] = v_good_windows


p = add(
    id="k-radius-window-averages", tier="extra", title="Centered Window Averages", diff="Easy", topic="Sliding Window",
    fn="radiusAverages", params=[("nums", "int[]"), ("k", "int")], ret="int[]", cmp="exact",
    desc="<p>For each index <code>i</code> of <code>nums</code>, consider the window of the <code>2k + 1</code> elements centered on <code>i</code>, that is the elements at indices <code>i-k</code> through <code>i+k</code>.</p><p>If the window fits completely inside the array, the answer for <code>i</code> is the <strong>floor</strong> of the average of its elements (the sum divided by <code>2k + 1</code>, rounded down). If the window sticks out of either end, the answer for <code>i</code> is <code>-1</code>. Return the array of answers.</p><pre>nums = [7, 4, 3, 9, 1, 8, 5, 2, 6], k = 3\nonly i = 3, 4, 5 have a full window\nresult = [-1, -1, -1, 5, 4, 4, -1, -1, -1]</pre>",
    constraints=["1 &le; nums.length &le; 6,000", "0 &le; k &le; 6,000", "0 &le; nums[i] &le; 100,000"],
    hints=["Indices closer than k to either end can never have a full window, so they are always -1.",
           "Summing each window from scratch is O(n * k). Neighbouring windows differ by one element on each side.",
           "Build the first full window, then for each next center add <code>nums[i + k]</code> and subtract <code>nums[i - k - 1]</code>. Use integer floor division by <code>2k + 1</code>."],
    editorial=["Fill the result with -1. If <code>2k + 1 &gt; n</code> nothing fits and the all -1 array is the answer. Otherwise compute the sum of the first full window (centered at index k) and then slide: the window centered at i+1 gains <code>nums[i + 1 + k]</code> and loses <code>nums[i - k]</code>.",
               "Each step is O(1), so the whole scan is O(n). With non-negative numbers, integer division rounds down exactly as required. The sums reach at most about 6,000 * 100,000, which is why the statement caps the values."],
    time="O(n)", space="O(1) extra",
    solution='''def radiusAverages(nums, k):
    n = len(nums)
    res = [-1] * n
    w = 2 * k + 1
    if w > n:
        return res
    cur = sum(nums[:w])
    res[k] = cur // w
    for i in range(k + 1, n - k):
        cur += nums[i + k] - nums[i - k - 1]
        res[i] = cur // w
    return res
''',
    tests=[[[7, 4, 3, 9, 1, 8, 5, 2, 6], 3], [[100000], 0], [[100000], 1], [[1, 2, 3], 0], [[1, 2, 3], 1], [[1, 2, 3], 2], [[0, 0, 0, 0, 0], 2],
           [[5, 6, 7, 8], 1], [[1, 1, 2], 1], [[100000, 100000, 100000, 100000, 100000], 2], [[3, 9], 5], [[2, 7, 1, 8, 2, 8, 1, 8], 2]],
)
_r = rnd(3102)
p["tests"].append([[_r.randint(0, 100000) for _ in range(4000)], 1500])
p["tests"].append([[_r.randint(0, 9) for _ in range(4000)], 0])
p["tests"].append([[_r.randint(0, 1000) for _ in range(4000)], 1999])


def b_radius(nums, k):
    n = len(nums)
    return [sum(nums[i - k:i + k + 1]) // (2 * k + 1) if i - k >= 0 and i + k < n else -1 for i in range(n)]


def g_radius(r):
    return [gen_arr(r, 0, 20, 1, 12), r.randint(0, 7)]


def v_radius(tests):
    for t in tests:
        a, k = t["args"]
        assert 1 <= len(a) <= 6000 and 0 <= k <= 6000
        assert all(0 <= x <= 100000 for x in a)


CHECKS["k-radius-window-averages"] = (b_radius, g_radius, "exact")
VALIDATE["k-radius-window-averages"] = v_radius


p = add(
    id="distinct-count-per-window", title="Distinct Values in Every Window", diff="Easy", topic="Sliding Window",
    fn="distinctPerWindow", params=[("nums", "int[]"), ("k", "int")], ret="int[]", cmp="exact",
    desc="<p>Slide a window of length <code>k</code> across <code>nums</code> from left to right. For every position, count how many <strong>different values</strong> are inside the window. Return these counts as an array of length <code>nums.length - k + 1</code>.</p><pre>nums = [1, 2, 1, 3, 4, 2, 3], k = 4\nwindows: [1,2,1,3] [2,1,3,4] [1,3,4,2] [3,4,2,3]\nresult = [3, 4, 4, 3]</pre>",
    constraints=["1 &le; k &le; nums.length &le; 6,000", "-10<sup>9</sup> &le; nums[i] &le; 10<sup>9</sup>"],
    hints=["Building a set for every window costs O(n * k).",
           "Maintain a frequency map for the current window. A value is 'inside' as long as its frequency is above zero.",
           "When sliding, increase the frequency of the new element (a new distinct value if it was 0 before) and decrease that of the leaving element (one fewer distinct value if it drops to 0)."],
    editorial=["Keep a hash map from value to its count in the window and a variable <code>distinct</code> for the number of keys with a positive count. Adding an element whose count goes from 0 to 1 increases <code>distinct</code>; removing an element whose count goes from 1 to 0 decreases it.",
               "Record <code>distinct</code> after the first k elements and after every slide. Each step does O(1) expected work, so the total is O(n) time with O(k) extra space for the map."],
    time="O(n)", space="O(k)",
    solution='''def distinctPerWindow(nums, k):
    cnt = {}
    distinct = 0
    res = []
    for i, x in enumerate(nums):
        c = cnt.get(x, 0)
        if c == 0:
            distinct += 1
        cnt[x] = c + 1
        if i >= k:
            y = nums[i - k]
            cnt[y] -= 1
            if cnt[y] == 0:
                distinct -= 1
        if i >= k - 1:
            res.append(distinct)
    return res
''',
    tests=[[[1, 2, 1, 3, 4, 2, 3], 4], [[5], 1], [[7, 7, 7, 7], 2], [[1, 2, 3, 4], 4], [[1, 2, 3, 4], 1], [[1, 1, 2, 2, 1, 1], 3],
           [[-1000000000, 1000000000, -1000000000], 2], [[1, 2, 3, 1, 2, 3, 1, 2, 3], 3], [[4, 4, 4, 5], 4], [[0, 1, 0, 1, 0, 1], 5],
           [[9, 8, 7, 6, 5], 2]],
)
_r = rnd(3103)
p["tests"].append([[_r.randint(-5, 5) for _ in range(4000)], 7])
p["tests"].append([[_r.randint(-10**9, 10**9) for _ in range(4000)], 2000])
p["tests"].append([[_r.randint(0, 300) for _ in range(4000)], 4000])


def b_distinct(nums, k):
    return [len(set(nums[i:i + k])) for i in range(len(nums) - k + 1)]


def g_distinct(r):
    a = gen_arr(r, -3, 3, 1, 12)
    return [a, r.randint(1, len(a))]


def v_distinct(tests):
    for t in tests:
        a, k = t["args"]
        assert 1 <= k <= len(a) <= 6000
        assert all(-10**9 <= x <= 10**9 for x in a)


CHECKS["distinct-count-per-window"] = (b_distinct, g_distinct, "exact")
VALIDATE["distinct-count-per-window"] = v_distinct


# ---------------------------------------------------------------- MEDIUM

p = add(
    id="max-sum-window-all-distinct", title="Best Window With All Distinct Values", diff="Medium", topic="Sliding Window",
    fn="maxDistinctWindowSum", params=[("nums", "int[]"), ("k", "int")], ret="int", cmp="exact",
    desc="<p>Look at every contiguous block of exactly <code>k</code> elements of <code>nums</code> in which <strong>all values are different</strong>. Return the largest sum among those blocks, or <code>0</code> if no block qualifies.</p><pre>nums = [4, 2, 4, 5, 6, 2], k = 3\nblocks: [4,2,4] x   [2,4,5] 11   [4,5,6] 15   [5,6,2] 13\nresult = 15</pre>",
    constraints=["1 &le; k &le; nums.length &le; 8,000", "1 &le; nums[i] &le; 100,000"],
    hints=["A window is valid only if it contains no repeated value. How can you know that without rebuilding a set each time?",
           "Keep a frequency map and the number of distinct keys. The window has all distinct values exactly when the distinct count equals k.",
           "Maintain the window sum alongside the map. After each slide, if <code>distinct == k</code>, the current sum is a candidate for the answer."],
    editorial=["Maintain three things for the current window: the sum, a frequency map and the number of distinct values. Sliding adds one element and removes one, each in O(1).",
               "Because the window has exactly k elements, it holds k distinct values if and only if it contains no duplicate. After every slide (including the first window) check <code>distinct == k</code> and update the best sum. The answer starts at 0, which also covers the no-valid-window case. Time O(n), space O(k)."],
    time="O(n)", space="O(k)",
    solution='''def maxDistinctWindowSum(nums, k):
    cnt = {}
    distinct = 0
    cur = 0
    best = 0
    for i, x in enumerate(nums):
        c = cnt.get(x, 0)
        if c == 0:
            distinct += 1
        cnt[x] = c + 1
        cur += x
        if i >= k:
            y = nums[i - k]
            cnt[y] -= 1
            if cnt[y] == 0:
                distinct -= 1
            cur -= y
        if i >= k - 1 and distinct == k and cur > best:
            best = cur
    return best
''',
    tests=[[[4, 2, 4, 5, 6, 2], 3], [[1, 5, 4, 2, 9, 9, 9], 3], [[4, 4, 4], 3], [[7], 1], [[3, 3], 1], [[1, 2, 3, 4, 5], 5], [[1, 2, 3, 1, 5], 5],
           [[100000, 99999, 100000], 2], [[5, 1, 5, 1, 5, 1], 2], [[2, 2, 3, 4, 4, 5, 6, 7], 4], [[9, 1, 1, 9, 1, 1, 9], 2],
           [[10, 20, 10, 20, 10], 3]],
)
_r = rnd(3104)
p["tests"].append([[_r.randint(1, 100000) for _ in range(6000)], 500])
p["tests"].append([[_r.randint(1, 60) for _ in range(6000)], 40])
p["tests"].append([[_r.randint(1, 5000) for _ in range(6000)], 100])


def b_distinct_sum(nums, k):
    best = 0
    for i in range(len(nums) - k + 1):
        w = nums[i:i + k]
        if len(set(w)) == k:
            best = max(best, sum(w))
    return best


def g_distinct_sum(r):
    a = gen_arr(r, 1, 7, 1, 12)
    return [a, r.randint(1, len(a))]


def v_distinct_sum(tests):
    for t in tests:
        a, k = t["args"]
        assert 1 <= k <= len(a) <= 8000
        assert all(1 <= x <= 100000 for x in a)
    assert any(t["expected"] == 0 for t in tests) and any(t["expected"] > 0 for t in tests)


CHECKS["max-sum-window-all-distinct"] = (b_distinct_sum, g_distinct_sum, "exact")
VALIDATE["max-sum-window-all-distinct"] = v_distinct_sum


p = add(
    id="max-card-points-from-ends", title="Maximum Points From Both Ends", diff="Medium", topic="Sliding Window",
    fn="maxCardPoints", params=[("cards", "int[]"), ("k", "int")], ret="int", cmp="exact",
    desc="<p>Cards lie in a row and card <code>i</code> is worth <code>cards[i]</code> points. In each of exactly <code>k</code> turns you take one card, either the leftmost or the rightmost one that is still in the row. Return the maximum total number of points you can collect.</p><pre>cards = [1, 2, 3, 4, 5, 6, 1], k = 3\ntake the three rightmost cards: 5 + 6 + 1 = 12\nresult = 12</pre>",
    constraints=["1 &le; k &le; cards.length &le; 8,000", "1 &le; cards[i] &le; 10,000"],
    hints=["Trying every sequence of left/right choices is exponential. What does the set of cards you finally hold look like?",
           "Whatever you choose, you end up with some prefix of length <code>i</code> and a suffix of length <code>k - i</code>. The cards you leave behind form one contiguous block.",
           "The untouched middle block has fixed length <code>n - k</code>. Minimize its sum with a fixed-size window and subtract it from the total."],
    editorial=["Taking k cards from the two ends always leaves a contiguous block of <code>n - k</code> cards in the middle, and every contiguous block of that length is reachable. So maximizing the points taken is the same as minimizing the sum of the block that stays.",
               "Slide a window of length <code>n - k</code> across the array with a running sum, track the smallest sum, and return <code>total - smallest</code>. When <code>k == n</code> the window is empty with sum 0 and the answer is the total. Time O(n), space O(1)."],
    time="O(n)", space="O(1)",
    solution='''def maxCardPoints(cards, k):
    n = len(cards)
    w = n - k
    total = sum(cards)
    cur = sum(cards[:w])
    best = cur
    for i in range(w, n):
        cur += cards[i] - cards[i - w]
        if cur < best:
            best = cur
    return total - best
''',
    tests=[[[1, 2, 3, 4, 5, 6, 1], 3], [[2, 2, 2], 2], [[9, 7, 7, 9, 7, 7, 9], 7], [[5], 1], [[1, 100, 1], 1], [[1, 100, 1], 2],
           [[100, 1, 1, 100], 2], [[1, 1000, 1, 1, 1], 4], [[3, 1, 4, 1, 5, 9, 2, 6], 4], [[10000, 10000], 1], [[1, 2, 3, 4], 4],
           [[4, 3, 2, 1], 1]],
)
_r = rnd(3105)
p["tests"].append([[_r.randint(1, 10000) for _ in range(8000)], 3000])
p["tests"].append([[_r.randint(1, 10000) for _ in range(8000)], 7990])
p["tests"].append([[_r.randint(1, 50) for _ in range(8000)], 1])


def b_cards(cards, k):
    return max(sum(cards[:i]) + (sum(cards[len(cards) - (k - i):]) if k - i else 0) for i in range(k + 1))


def g_cards(r):
    a = gen_arr(r, 1, 9, 1, 10)
    return [a, r.randint(1, len(a))]


def v_cards(tests):
    for t in tests:
        a, k = t["args"]
        assert 1 <= k <= len(a) <= 8000
        assert all(1 <= x <= 10000 for x in a)


CHECKS["max-card-points-from-ends"] = (b_cards, g_cards, "exact")
VALIDATE["max-card-points-from-ends"] = v_cards


p = add(
    id="min-swaps-to-group-ones", title="Minimum Swaps to Group All Ones", diff="Medium", topic="Sliding Window",
    fn="minSwapsGroupOnes", params=[("bits", "int[]")], ret="int", cmp="exact",
    desc="<p>The array <code>bits</code> contains only <code>0</code> and <code>1</code>. In one swap you may exchange the values at any two positions (they need not be neighbours). Return the minimum number of swaps needed so that all the 1s end up in one contiguous block. If there are no 1s, the answer is 0.</p><pre>bits = [1, 0, 1, 0, 1, 0, 0, 1]\nfour 1s, so look at windows of length 4: none contains more than two 1s, e.g. [1,0,1,0]\nresult = 4 - 2 = 2</pre>",
    constraints=["1 &le; bits.length &le; 8,000", "bits[i] is 0 or 1"],
    hints=["In the final arrangement the 1s occupy a block whose length equals the total number of 1s, call it <code>m</code>.",
           "Pick the block position first. Each 0 currently inside that block needs one swap with a 1 from outside it.",
           "So the cost of a block is <code>m</code> minus the number of 1s already inside it. Find the window of length <code>m</code> with the most 1s."],
    editorial=["Let <code>m</code> be the number of ones. Wherever the final block of length m goes, the zeros currently inside it must be exchanged with ones currently outside, and each swap fixes exactly one zero (there are always as many outside ones as inside zeros). The cost is therefore the count of zeros in the block.",
               "Minimizing zeros in a length-m window is the same as maximizing ones in it. A fixed-size sliding window with a running count of ones does this in O(n) time and O(1) space. The answer is <code>m - maxOnes</code>, and 0 when m is 0."],
    time="O(n)", space="O(1)",
    solution='''def minSwapsGroupOnes(bits):
    m = sum(bits)
    if m == 0:
        return 0
    cur = sum(bits[:m])
    best = cur
    for i in range(m, len(bits)):
        cur += bits[i] - bits[i - m]
        if cur > best:
            best = cur
    return m - best
''',
    tests=[[[1, 0, 1, 0, 1, 0, 0, 1]], [[1, 0, 1, 0, 1]], [[0, 0, 0]], [[1]], [[0]], [[1, 1, 1]], [[1, 0, 0, 0, 1]], [[1, 0, 0, 1, 0, 0, 1, 0, 0, 1]],
           [[0, 1, 1, 0, 1, 1, 0]], [[1, 0]], [[1, 0, 1]], [[0, 0, 1, 1, 0, 0, 1, 1, 0, 0]]],
)
_r = rnd(3106)
p["tests"].append([[_r.randint(0, 1) for _ in range(8000)]])
p["tests"].append([[1 if _r.random() < 0.05 else 0 for _ in range(8000)]])
p["tests"].append([[1] * 100 + [0] * 7000 + [1] * 100 + [0] * 800])


def b_swaps(bits):
    # try every target block; count zeros inside it
    m = sum(bits)
    if m == 0:
        return 0
    return min(bits[s:s + m].count(0) for s in range(len(bits) - m + 1))


def v_swaps(tests):
    for t in tests:
        a = t["args"][0]
        assert 1 <= len(a) <= 8000 and set(a) <= {0, 1}


CHECKS["min-swaps-to-group-ones"] = (b_swaps, lambda r: [[r.randint(0, 1) for _ in range(r.randint(1, 12))]], "exact")
VALIDATE["min-swaps-to-group-ones"] = v_swaps


p = add(
    id="max-sum-two-fixed-windows", tier="extra", title="Two Non-Overlapping Windows", diff="Medium", topic="Sliding Window",
    fn="maxTwoWindows", params=[("nums", "int[]"), ("a", "int"), ("b", "int")], ret="int", cmp="exact",
    desc="<p>Choose two contiguous blocks of <code>nums</code>: one of length exactly <code>a</code> and one of length exactly <code>b</code>. They must not share any index, but they may appear in either order and may touch each other. Return the maximum possible total of the two block sums.</p><pre>nums = [0, 6, 5, 2, 2, 5, 1, 9, 4], a = 1, b = 2\nlength-1 block [9] and length-2 block [6,5]: 9 + 11\nresult = 20</pre>",
    constraints=["1 &le; a, b", "a + b &le; nums.length &le; 8,000", "0 &le; nums[i] &le; 1,000"],
    hints=["First compute the sum of every window of length a and of length b with prefix sums.",
           "Fix the position where the second window ends. The first window can be any block that ends before the second one starts.",
           "While sweeping, keep the best sum of an <code>a</code>-window seen so far that ends at or before the start of the current <code>b</code>-window. Run the sweep twice, once with a first and once with b first."],
    editorial=["Let <code>P</code> be the prefix sums. Consider the case where the a-window comes before the b-window. Sweep the end <code>i</code> of the b-window; its start is <code>i - b</code>. All a-windows ending at or before <code>i - b</code> are allowed, so maintain their maximum sum as <code>i</code> grows and add the b-window sum <code>P[i] - P[i-b]</code>.",
               "Repeat with the roles swapped (b first, then a) and return the larger value. Each sweep is O(n) after the prefix sums, so the total is O(n) time and O(n) space for the prefix array."],
    time="O(n)", space="O(n)",
    solution='''def maxTwoWindows(nums, a, b):
    n = len(nums)
    P = [0] * (n + 1)
    for i, x in enumerate(nums):
        P[i + 1] = P[i] + x

    def sweep(first, second):
        best = 0
        best_first = 0
        for i in range(first + second, n + 1):
            best_first = max(best_first, P[i - second] - P[i - second - first])
            best = max(best, best_first + P[i] - P[i - second])
        return best

    return max(sweep(a, b), sweep(b, a))
''',
    tests=[[[0, 6, 5, 2, 2, 5, 1, 9, 4], 1, 2], [[3, 8, 1, 3, 2, 1, 8, 9, 0], 3, 2], [[2, 1, 5, 6, 0, 9, 5, 0, 3, 8], 4, 3], [[5, 5], 1, 1],
           [[1, 2, 3], 1, 2], [[0, 0, 0, 0], 2, 2], [[9, 0, 0, 9], 1, 1], [[1000, 1, 1, 1000], 2, 1], [[7, 7, 7, 7, 7], 2, 3], [[4, 1, 4, 1, 4, 1], 1, 1],
           [[1, 100, 1, 1, 100, 1], 2, 2]],
)
_r = rnd(3107)
p["tests"].append([[_r.randint(0, 1000) for _ in range(6000)], 1500, 2500])
p["tests"].append([[_r.randint(0, 1000) for _ in range(6000)], 1, 1])
p["tests"].append([[_r.randint(0, 1000) for _ in range(6000)], 3000, 3000])


def b_two_windows(nums, a, b):
    n = len(nums)
    best = 0
    for i in range(n - a + 1):
        sa = sum(nums[i:i + a])
        for j in range(n - b + 1):
            if j + b <= i or i + a <= j:
                best = max(best, sa + sum(nums[j:j + b]))
    return best


def g_two_windows(r):
    arr = gen_arr(r, 0, 9, 2, 11)
    a = r.randint(1, len(arr) - 1)
    b = r.randint(1, len(arr) - a)
    return [arr, a, b]


def v_two_windows(tests):
    for t in tests:
        nums, a, b = t["args"]
        assert a >= 1 and b >= 1 and a + b <= len(nums) <= 8000
        assert all(0 <= x <= 1000 for x in nums)


CHECKS["max-sum-two-fixed-windows"] = (b_two_windows, g_two_windows, "exact")
VALIDATE["max-sum-two-fixed-windows"] = v_two_windows


p = add(
    id="max-satisfied-customers-calm-streak", tier="extra", title="Satisfied Customers With a Calm Streak", diff="Medium", topic="Sliding Window",
    fn="maxSatisfied", params=[("customers", "int[]"), ("grumpy", "int[]"), ("minutes", "int")], ret="int", cmp="exact",
    desc="<p>A shop is open for <code>n</code> minutes. During minute <code>i</code>, <code>customers[i]</code> people visit. The owner is in a bad mood during minute <code>i</code> when <code>grumpy[i] = 1</code>, and calm when <code>grumpy[i] = 0</code>. Visitors are satisfied only in minutes when the owner is calm.</p><p>The owner knows a trick that makes them calm for <strong>exactly <code>minutes</code> consecutive minutes</strong>, usable once. Choose where to use it and return the maximum number of satisfied customers over the whole day.</p><pre>customers = [1, 0, 1, 2, 1, 1, 7, 5]\ngrumpy    = [0, 1, 0, 1, 0, 1, 0, 1]\nminutes = 3\ncalm anyway: 1 + 1 + 1 + 7 = 10\nthe trick on minutes 5..7 wins the grumpy customers 1 + 5 = 6 more\nresult = 16</pre>",
    constraints=["1 &le; minutes &le; customers.length = grumpy.length &le; 8,000", "0 &le; customers[i] &le; 1,000", "grumpy[i] is 0 or 1"],
    hints=["Customers in calm minutes are satisfied no matter what you do, so count them once up front.",
           "The trick can only help in grumpy minutes. How many extra customers does it win if it covers a given block of minutes?",
           "The extra for a block is the sum of <code>customers[i] * grumpy[i]</code> over it. Find the maximum such sum over all windows of length <code>minutes</code>."],
    editorial=["Split the total into a fixed part, <code>sum(customers[i] for calm i)</code>, and a gain that depends on the chosen block. The trick turns every grumpy minute in the block calm, so the gain of a block is the sum of <code>customers[i]</code> over its grumpy minutes.",
               "Define <code>lost[i] = customers[i] * grumpy[i]</code> and slide a window of length <code>minutes</code> to find the largest window sum. The result is the fixed part plus that maximum. Time O(n), extra space O(1) if you compute <code>lost[i]</code> on the fly."],
    time="O(n)", space="O(1)",
    solution='''def maxSatisfied(customers, grumpy, minutes):
    n = len(customers)
    base = sum(c for c, g in zip(customers, grumpy) if g == 0)
    cur = sum(customers[i] * grumpy[i] for i in range(minutes))
    gain = cur
    for i in range(minutes, n):
        cur += customers[i] * grumpy[i] - customers[i - minutes] * grumpy[i - minutes]
        if cur > gain:
            gain = cur
    return base + gain
''',
    tests=[[[1, 0, 1, 2, 1, 1, 7, 5], [0, 1, 0, 1, 0, 1, 0, 1], 3], [[1], [0], 1], [[1], [1], 1], [[4, 10, 10], [1, 1, 0], 2], [[3, 3, 3], [0, 0, 0], 2],
           [[3, 3, 3], [1, 1, 1], 3], [[5, 0, 0, 5], [1, 1, 1, 1], 1], [[2, 6, 6, 9], [0, 0, 1, 1], 1], [[1000, 1000], [1, 1], 1],
           [[0, 0, 0], [1, 1, 1], 2], [[7, 1, 8, 2, 9], [1, 0, 1, 0, 1], 2]],
)
_r = rnd(3108)
for _n, _m in ((4000, 700), (4000, 1), (4000, 4000)):
    p["tests"].append([[_r.randint(0, 1000) for _ in range(_n)], [_r.randint(0, 1) for _ in range(_n)], _m])


def b_satisfied(customers, grumpy, minutes):
    n = len(customers)
    best = 0
    for s in range(n - minutes + 1):
        tot = 0
        for i in range(n):
            if grumpy[i] == 0 or s <= i < s + minutes:
                tot += customers[i]
        best = max(best, tot)
    return best


def g_satisfied(r):
    n = r.randint(1, 10)
    return [[r.randint(0, 9) for _ in range(n)], [r.randint(0, 1) for _ in range(n)], r.randint(1, n)]


def v_satisfied(tests):
    for t in tests:
        c, g, m = t["args"]
        assert 1 <= m <= len(c) == len(g) <= 8000
        assert all(0 <= x <= 1000 for x in c) and set(g) <= {0, 1}


CHECKS["max-satisfied-customers-calm-streak"] = (b_satisfied, g_satisfied, "exact")
VALIDATE["max-satisfied-customers-calm-streak"] = v_satisfied


p = add(
    id="count-windows-with-small-spread", title="Windows With Small Spread", diff="Medium", topic="Sliding Window",
    fn="countSteadyWindows", params=[("nums", "int[]"), ("k", "int"), ("d", "int")], ret="int", cmp="exact",
    desc="<p>The <em>spread</em> of a block is its largest value minus its smallest value. Given <code>nums</code>, a window length <code>k</code> and a limit <code>d</code>, count the contiguous blocks of exactly <code>k</code> elements whose spread is <strong>at most</strong> <code>d</code>.</p><pre>nums = [4, 6, 5, 9, 8, 8, 1], k = 3, d = 2\nwindows: [4,6,5] spread 2   [6,5,9] 4   [5,9,8] 4   [9,8,8] 1   [8,8,1] 7\nresult = 2</pre>",
    constraints=["1 &le; k &le; nums.length &le; 8,000", "0 &le; d &le; 2 * 10<sup>9</sup>", "-10<sup>9</sup> &le; nums[i] &le; 10<sup>9</sup>"],
    hints=["Taking max and min of each window directly costs O(n * k).",
           "You need the maximum and the minimum of a sliding window. A monotonic deque gives either in amortized O(1).",
           "Keep one deque of indices with decreasing values (front = max) and one with increasing values (front = min). Drop front indices that fall out of the window; compare <code>nums[maxFront] - nums[minFront]</code> with d."],
    editorial=["Maintain two deques of indices. In the max-deque the values are strictly decreasing from front to back, so the front is the window maximum; before pushing index <code>i</code> pop all back entries with value less than or equal to <code>nums[i]</code>. The min-deque is the mirror image. Pop from the front whenever its index is at most <code>i - k</code>.",
               "Once <code>i &ge; k - 1</code>, the window is complete: check whether <code>nums[maxdq[0]] - nums[mindq[0]] &le; d</code> and count it. Every index enters and leaves each deque at most once, so the time is O(n), with O(k) space."],
    time="O(n)", space="O(k)",
    solution='''def countSteadyWindows(nums, k, d):
    from collections import deque
    mx = deque()
    mn = deque()
    count = 0
    for i, x in enumerate(nums):
        while mx and nums[mx[-1]] <= x:
            mx.pop()
        mx.append(i)
        while mn and nums[mn[-1]] >= x:
            mn.pop()
        mn.append(i)
        if mx[0] <= i - k:
            mx.popleft()
        if mn[0] <= i - k:
            mn.popleft()
        if i >= k - 1 and nums[mx[0]] - nums[mn[0]] <= d:
            count += 1
    return count
''',
    tests=[[[4, 6, 5, 9, 8, 8, 1], 3, 2], [[5], 1, 0], [[5, 5, 5], 2, 0], [[1, 2, 3, 4], 4, 2], [[1, 2, 3, 4], 4, 3], [[1, 2, 3, 4], 1, 0],
           [[-1000000000, 1000000000, -1000000000], 2, 1000000000], [[-1000000000, 1000000000, -1000000000], 2, 1999999999],
           [[3, 1, 4, 1, 5, 9, 2, 6, 5, 3], 3, 4], [[-1000000000, 1000000000, 0], 3, 2000000000], [[9, 8, 7, 6, 5], 2, 1], [[2, 2, 9, 2, 2], 3, 0], [[7, 1, 7, 1, 7, 1], 5, 6]],
)
_r = rnd(3109)
p["tests"].append([[_r.randint(0, 1000) for _ in range(6000)], 30, 600])
p["tests"].append([[_r.randint(-10**9, 10**9) for _ in range(6000)], 2000, 10**9 + 1])
_a = [0]
for _ in range(5999):
    _a.append(_a[-1] + _r.randint(-3, 3))
p["tests"].append([_a, 500, 30])


def b_steady(nums, k, d):
    return sum(1 for i in range(len(nums) - k + 1) if max(nums[i:i + k]) - min(nums[i:i + k]) <= d)


def g_steady(r):
    a = gen_arr(r, -9, 9, 1, 12)
    return [a, r.randint(1, len(a)), r.randint(0, 12)]


def v_steady(tests):
    for t in tests:
        a, k, d = t["args"]
        assert 1 <= k <= len(a) <= 8000
        assert all(-10**9 <= x <= 10**9 for x in a) and 0 <= d <= 2 * 10**9


CHECKS["count-windows-with-small-spread"] = (b_steady, g_steady, "exact")
VALIDATE["count-windows-with-small-spread"] = v_steady


# ---------------------------------------------------------------- HARD

p = add(
    id="sliding-window-lower-median", tier="extra", title="Lower Median of Every Window", diff="Hard", topic="Sliding Window",
    fn="windowLowerMedians", params=[("nums", "int[]"), ("k", "int")], ret="int[]", cmp="exact",
    desc="<p>For each window of <code>k</code> consecutive elements of <code>nums</code>, report its <strong>lower median</strong>: sort the window and take the element at (0-based) position <code>(k - 1) / 2</code>, rounded down. For odd <code>k</code> this is the usual median; for even <code>k</code> it is the smaller of the two middle values.</p><p>Return the medians of all windows from left to right.</p><pre>nums = [1, 3, -1, -3, 5, 3, 6, 7], k = 4\nsorted windows: [-3,-1,1,3] [-3,-1,3,5] [-3,-1,3,5] [-3,3,5,6] [3,5,6,7]\nelement at position 1 of each: -1, -1, -1, 3, 5\nresult = [-1, -1, -1, 3, 5]</pre>",
    constraints=["1 &le; k &le; nums.length &le; 8,000", "-10<sup>9</sup> &le; nums[i] &le; 10<sup>9</sup>"],
    hints=["Sorting every window costs O(n * k log k). Neighbouring windows differ by only one removed and one added element.",
           "You need the r-th smallest element of a changing multiset, with r = (k - 1) / 2 + 1. Which structure supports insert, delete and rank queries?",
           "Compress the values to ranks and use a Fenwick tree of counts. Add the new value, remove the old one, then find the r-th smallest by descending the tree."],
    editorial=["Compress the distinct values of <code>nums</code> to ranks 1..m. A Fenwick tree (binary indexed tree) stores how many window elements have each rank. Inserting or deleting an element is one point update, O(log m).",
               "To find the element of rank <code>r = (k - 1) // 2 + 1</code>, descend the tree from the highest power of two: at each step jump forward if the stored prefix count is still smaller than what remains to be found. This yields the smallest position whose prefix count reaches r in O(log m).",
               "Total time is O(n log n) and space O(n). Two heaps with lazy deletion, or a sorted list with binary search, also work; the Fenwick approach has clean worst-case guarantees and handles duplicates naturally."],
    time="O(n log n)", space="O(n)",
    solution='''def windowLowerMedians(nums, k):
    vals = sorted(set(nums))
    rank = {v: i + 1 for i, v in enumerate(vals)}
    m = len(vals)
    tree = [0] * (m + 1)
    top = 1
    while top * 2 <= m:
        top *= 2

    def update(i, delta):
        while i <= m:
            tree[i] += delta
            i += i & -i

    def kth(t):
        pos = 0
        step = top
        while step:
            nxt = pos + step
            if nxt <= m and tree[nxt] < t:
                pos = nxt
                t -= tree[nxt]
            step >>= 1
        return pos + 1

    target = (k - 1) // 2 + 1
    res = []
    for i, x in enumerate(nums):
        update(rank[x], 1)
        if i >= k:
            update(rank[nums[i - k]], -1)
        if i >= k - 1:
            res.append(vals[kth(target) - 1])
    return res
''',
    tests=[[[1, 3, -1, -3, 5, 3, 6, 7], 4], [[1, 3, -1, -3, 5, 3, 6, 7], 3], [[5], 1], [[2, 1], 2], [[2, 1], 1], [[7, 7, 7, 7], 3], [[1, 2, 3, 4, 5], 5],
           [[5, 4, 3, 2, 1], 4], [[-1000000000, 1000000000, 0, 1000000000, -1000000000], 3], [[1, 1, 2, 2, 3, 3], 4], [[9, 1, 9, 1, 9, 1], 2],
           [[4, 2, 12, 11, -5], 2]],
)
_r = rnd(3110)
p["tests"].append([[_r.randint(-10**9, 10**9) for _ in range(5000)], 1001])
p["tests"].append([[_r.randint(-20, 20) for _ in range(5000)], 800])
p["tests"].append([[_r.randint(-1000, 1000) for _ in range(5000)], 5000])


def b_medians(nums, k):
    return [sorted(nums[i:i + k])[(k - 1) // 2] for i in range(len(nums) - k + 1)]


def g_medians(r):
    a = gen_arr(r, -6, 6, 1, 12)
    return [a, r.randint(1, len(a))]


def v_medians(tests):
    for t in tests:
        a, k = t["args"]
        assert 1 <= k <= len(a) <= 8000
        assert all(-10**9 <= x <= 10**9 for x in a)


CHECKS["sliding-window-lower-median"] = (b_medians, g_medians, "exact")
VALIDATE["sliding-window-lower-median"] = v_medians


p = add(
    id="count-close-pairs-index-and-value", tier="extra", title="Close Pairs Within an Index Gap", diff="Hard", topic="Sliding Window",
    fn="countClosePairs", params=[("nums", "int[]"), ("t", "int"), ("d", "int")], ret="int", cmp="exact",
    desc="<p>Count the pairs of indices <code>i &lt; j</code> that are close in <strong>both</strong> senses: the positions are at most <code>t</code> apart (<code>j - i &le; t</code>) and the values are at most <code>d</code> apart (<code>|nums[i] - nums[j]| &le; d</code>).</p><pre>nums = [1, 5, 3, 4, 2], t = 2, d = 1\nclose pairs (index gap &le; 2, value gap &le; 1): (1,3) 5,4   (2,3) 3,4   (2,4) 3,2\nresult = 3</pre>",
    constraints=["1 &le; nums.length &le; 6,000", "1 &le; t &le; 6,000", "0 &le; d &le; 10<sup>9</sup>", "-10<sup>9</sup> &le; nums[i] &le; 10<sup>9</sup>"],
    hints=["Checking every pair with j - i &le; t is O(n * t), which is too slow when t is large.",
           "When you reach index j, the only partners that matter are the previous t elements, a window that slides with j. You need to count how many of them have a value in [nums[j] - d, nums[j] + d].",
           "Keep the window's values in a counting structure over compressed ranks (a Fenwick tree). Count with two binary searches for the range ends, then add nums[j] and remove nums[j - t]."],
    editorial=["Process j from left to right while maintaining a multiset holding exactly the values at indices <code>max(0, j - t) .. j - 1</code>. The number of pairs ending at j is the number of values in that multiset within <code>[nums[j] - d, nums[j] + d]</code>; summing over j counts every valid pair once.",
               "Compress the values of nums to sorted order and use a Fenwick tree of counts. For the query, find the range of ranks with <code>bisect_left</code> (first value &ge; nums[j] - d) and <code>bisect_right</code> (first value &gt; nums[j] + d) and take a prefix-count difference. After the query, insert nums[j]; when index <code>j - t</code> leaves the window, remove it.",
               "Each step costs O(log n), so the total is O(n log n) time and O(n) space. The answer is at most n * t pairs, at most 36 million here, so it fits comfortably in 32 bits."],
    time="O(n log n)", space="O(n)",
    solution='''def countClosePairs(nums, t, d):
    from bisect import bisect_left, bisect_right
    vals = sorted(set(nums))
    m = len(vals)
    tree = [0] * (m + 1)

    def update(i, delta):
        i += 1
        while i <= m:
            tree[i] += delta
            i += i & -i

    def prefix(i):
        total = 0
        while i > 0:
            total += tree[i]
            i -= i & -i
        return total

    pos = {v: i for i, v in enumerate(vals)}
    total = 0
    for j, x in enumerate(nums):
        lo = bisect_left(vals, x - d)
        hi = bisect_right(vals, x + d)
        total += prefix(hi) - prefix(lo)
        update(pos[x], 1)
        if j >= t:
            update(pos[nums[j - t]], -1)
    return total
''',
    tests=[[[1, 5, 3, 4, 2], 2, 1], [[7], 1, 0], [[3, 3, 3, 3], 1, 0], [[3, 3, 3, 3], 3, 0], [[3, 3, 3, 3], 100, 0], [[1, 2, 3, 4, 5], 4, 0],
           [[1, 2, 3, 4, 5], 4, 4], [[1, 10, 1, 10, 1], 2, 0], [[1, 10, 1, 10, 1], 1, 9], [[-1000000000, 1000000000], 1, 1000000000],
           [[-1000000000, 1000000000], 1, 999999999], [[0, 5, 1, 6, 2, 7], 3, 2], [[10, 8, 6, 4, 2], 2, 2]],
)
_r = rnd(3111)
p["tests"].append([[_r.randint(-10**9, 10**9) for _ in range(5000)], 700, 10**8])
p["tests"].append([[_r.randint(0, 50) for _ in range(5000)], 4999, 0])
p["tests"].append([[_r.randint(-1000, 1000) for _ in range(5000)], 1, 300])


def b_close_pairs(nums, t, d):
    n = len(nums)
    return sum(1 for i in range(n) for j in range(i + 1, min(n, i + t + 1)) if abs(nums[i] - nums[j]) <= d)


def g_close_pairs(r):
    a = gen_arr(r, -9, 9, 1, 12)
    return [a, r.randint(1, 13), r.randint(0, 8)]


def v_close_pairs(tests):
    for t in tests:
        a, tt, d = t["args"]
        assert 1 <= len(a) <= 6000 and 1 <= tt <= 6000 and 0 <= d <= 10**9
        assert all(-10**9 <= x <= 10**9 for x in a)
        assert t["expected"] <= 2**31 - 1


CHECKS["count-close-pairs-index-and-value"] = (b_close_pairs, g_close_pairs, "exact")
VALIDATE["count-close-pairs-index-and-value"] = v_close_pairs
