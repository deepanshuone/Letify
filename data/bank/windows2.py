"""Problems: more two pointers and sliding window. See data/lib.py for the registry."""
from collections import Counter
from functools import lru_cache
from itertools import combinations

from lib import add, rnd, CHECKS, VALIDATE, gen_arr  # noqa: F401


# ---------------------------------------------------------------- EASY

p = add(
    id="sorted-squares-two-pointers", title="Squares of a Sorted Array", diff="Easy", topic="Two Pointers",
    fn="sortedSquares", params=[("nums", "int[]")], ret="int[]", cmp="exact",
    desc="<p>The array <code>nums</code> is sorted in non-decreasing order and may contain negative numbers. Build and return a new array holding the square of every element, also sorted in non-decreasing order.</p><p>Squaring and then sorting is easy to write. Can you take advantage of the fact that the input is already sorted and finish in O(n) time?</p><pre>nums = [-4, -1, 0, 3, 10]\nresult = [0, 1, 9, 16, 100]</pre>",
    constraints=["1 &le; nums.length &le; 10,000", "-10,000 &le; nums[i] &le; 10,000", "nums is sorted in non-decreasing order"],
    hints=["After squaring, the order is no longer sorted, because large negative numbers become large positive ones.",
           "The largest square is always at one of the two ends of the input: either the most negative or the most positive value.",
           "Keep a pointer at each end, compare absolute values, and fill the result array from the back with the larger square."],
    editorial=["The squares of a sorted array form a valley shape: they shrink while the values are negative and grow again once they are positive. The biggest square therefore sits at the left end or the right end of the input.",
               "Place one pointer at each end and fill the output from the last position down to the first. At each step compare <code>abs(nums[lo])</code> and <code>abs(nums[hi])</code>, write the larger square, and move that pointer inward. Every element is handled once, so the time is O(n) with O(n) for the output. Sorting the squares directly costs O(n log n)."],
    time="O(n)", space="O(n)",
    solution='''def sortedSquares(nums):
    n = len(nums)
    res = [0] * n
    lo, hi = 0, n - 1
    for pos in range(n - 1, -1, -1):
        if abs(nums[lo]) > abs(nums[hi]):
            res[pos] = nums[lo] * nums[lo]
            lo += 1
        else:
            res[pos] = nums[hi] * nums[hi]
            hi -= 1
    return res
''',
    tests=[[[-4, -1, 0, 3, 10]], [[-7, -3, 2, 3, 11]], [[0]], [[-5]], [[3]], [[-2, -2, -2]], [[1, 2, 3]], [[-3, -2, -1]],
           [[-1, 1]], [[-10000, 10000]], [[0, 0, 0]], [[-5, -4, 0, 4, 4, 5]]],
)
_r = rnd(2001)
p["tests"].append([sorted(_r.randint(-10000, 10000) for _ in range(10000))])
p["tests"].append([sorted(_r.randint(-10000, -1) for _ in range(10000))])
p["tests"].append([[-3] * 5000 + [3] * 5000])


def b_squares(nums):
    return sorted(x ** 2 for x in nums)


def v_squares(tests):
    for t in tests:
        a = t["args"][0]
        assert 1 <= len(a) <= 10000
        assert all(-10000 <= x <= 10000 for x in a)
        assert all(a[i] <= a[i + 1] for i in range(len(a) - 1)), "not sorted"


CHECKS["sorted-squares-two-pointers"] = (b_squares, lambda r: [sorted(gen_arr(r, -9, 9, 1, 9))], "exact")
VALIDATE["sorted-squares-two-pointers"] = v_squares


p = add(
    id="max-sum-window-of-size-k", title="Maximum Sum of a Fixed Window", diff="Easy", topic="Sliding Window",
    fn="maxWindowSum", params=[("nums", "int[]"), ("k", "int")], ret="int", cmp="exact",
    desc="<p>Given an integer array <code>nums</code> and a window length <code>k</code>, look at every contiguous block of exactly <code>k</code> elements and return the largest sum found among them.</p><pre>nums = [1, 12, -5, -6, 50, 3], k = 4\nwindows: 2, 51, 42  (sums of [1,12,-5,-6], [12,-5,-6,50], [-5,-6,50,3])\nresult = 51</pre>",
    constraints=["1 &le; k &le; nums.length &le; 10,000", "-10,000 &le; nums[i] &le; 10,000"],
    hints=["Adding up each window from scratch costs O(n * k). Consecutive windows overlap almost completely.",
           "Moving the window one step to the right removes exactly one element on the left and adds one on the right.",
           "Compute the first window's sum once, then update it with <code>sum += nums[i] - nums[i - k]</code> while tracking the maximum."],
    editorial=["Keep a running sum of the current window. Sliding the window by one position changes the sum by adding the new element at the right edge and subtracting the element that just fell off the left edge, which is O(1) per step.",
               "Start with the sum of the first k elements as the best value, then slide through the rest of the array and keep the maximum. Total time is O(n) with O(1) extra space. Be careful to initialise the best value from a real window rather than from 0, since all sums can be negative."],
    time="O(n)", space="O(1)",
    solution='''def maxWindowSum(nums, k):
    cur = sum(nums[:k])
    best = cur
    for i in range(k, len(nums)):
        cur += nums[i] - nums[i - k]
        if cur > best:
            best = cur
    return best
''',
    tests=[[[1, 12, -5, -6, 50, 3], 4], [[5], 1], [[-3, -1, -2], 2], [[-3, -1, -2], 3], [[-3, -1, -2], 1], [[4, 2, 1, 7, 8, 1, 2, 8, 1, 0], 3],
           [[0, 0, 0, 0], 2], [[10000, 10000, 10000], 3], [[-10000, -10000], 1], [[1, -1, 1, -1, 1], 2], [[7, -7, 7, -7, 7], 5]],
)
_r = rnd(2002)
p["tests"].append([[_r.randint(-10000, 10000) for _ in range(10000)], 1234])
p["tests"].append([[_r.randint(-10000, 10000) for _ in range(10000)], 1])
p["tests"].append([[_r.randint(-10000, 10000) for _ in range(10000)], 10000])
p["tests"].append([[_r.randint(-10000, -1) for _ in range(10000)], 5000])


def b_window(nums, k):
    return max(sum(nums[i:i + k]) for i in range(len(nums) - k + 1))


def g_window(r):
    a = gen_arr(r, -9, 9, 1, 10)
    return [a, r.randint(1, len(a))]


def v_window(tests):
    for t in tests:
        a, k = t["args"]
        assert 1 <= k <= len(a) <= 10000
        assert all(-10000 <= x <= 10000 for x in a)


CHECKS["max-sum-window-of-size-k"] = (b_window, g_window, "exact")
VALIDATE["max-sum-window-of-size-k"] = v_window


p = add(
    id="sorted-arrays-common-elements", title="Common Elements of Two Sorted Arrays", diff="Easy", topic="Two Pointers",
    fn="commonElements", params=[("a", "int[]"), ("b", "int[]")], ret="int[]", cmp="exact",
    desc="<p>Two integer arrays <code>a</code> and <code>b</code> are each sorted in non-decreasing order. Return a sorted array containing every value they share, counting duplicates: a value that appears <code>x</code> times in <code>a</code> and <code>y</code> times in <code>b</code> must appear <code>min(x, y)</code> times in the result.</p><pre>a = [1, 2, 2, 3, 5]\nb = [2, 2, 2, 5, 7]\nresult = [2, 2, 5]</pre>",
    constraints=["0 &le; a.length, b.length &le; 5,000", "-10<sup>9</sup> &le; a[i], b[i] &le; 10<sup>9</sup>", "Both arrays are sorted in non-decreasing order"],
    hints=["Counting values with a hash map works, but it ignores the fact that both arrays are sorted.",
           "Use one pointer per array. Compare the two current values and decide which pointer can safely move.",
           "If the values are equal, record one copy and advance both pointers; otherwise advance the pointer at the smaller value."],
    editorial=["Because both arrays are sorted, a pointer into each array can sweep forward and never needs to go back. At each step compare <code>a[i]</code> and <code>b[j]</code>. The smaller one cannot match anything remaining in the other array (everything there is at least as large), so skip it. When they are equal, output the value and advance both pointers, which automatically pairs up duplicates the right number of times.",
               "The loop does at most <code>len(a) + len(b)</code> steps, so the time is O(n + m) and extra space beyond the output is O(1). A hash-map approach is also O(n + m) but needs extra memory and loses the sorted order for free."],
    time="O(n + m)", space="O(1) extra",
    solution='''def commonElements(a, b):
    i = j = 0
    res = []
    while i < len(a) and j < len(b):
        if a[i] < b[j]:
            i += 1
        elif a[i] > b[j]:
            j += 1
        else:
            res.append(a[i])
            i += 1
            j += 1
    return res
''',
    tests=[[[1, 2, 2, 3, 5], [2, 2, 2, 5, 7]], [[], []], [[1], [2]], [[1, 1, 1], [1, 1]], [[-3, -1, 0, 5], [-3, 0, 5, 9]], [[5], [5]],
           [[], [1, 2]], [[1, 2, 3], []], [[1, 3, 5, 7], [2, 4, 6, 8]], [[-1000000000, 1000000000], [-1000000000, 1000000000]],
           [[0, 0, 0, 0], [0, 0, 0, 0, 0, 0]], [[4, 9, 9, 9, 12], [1, 4, 4, 9, 9, 15]]],
)
_r = rnd(2003)
p["tests"].append([sorted(_r.randint(0, 3000) for _ in range(5000)), sorted(_r.randint(0, 3000) for _ in range(5000))])
_a = sorted(_r.randint(-10 ** 9, 10 ** 9) for _ in range(5000))
p["tests"].append([_a, list(_a)])
p["tests"].append([[2 * i for i in range(5000)], [2 * i + 1 for i in range(5000)]])
p["tests"].append([sorted(_r.randint(-5, 5) for _ in range(5000)), sorted(_r.randint(-5, 5) for _ in range(4000))])


def b_common(a, b):
    rest = list(b)
    out = []
    for x in a:
        if x in rest:
            rest.remove(x)
            out.append(x)
    return sorted(out)


def g_common(r):
    return [sorted(gen_arr(r, -5, 5, 0, 9)), sorted(gen_arr(r, -5, 5, 0, 9))]


def v_common(tests):
    for t in tests:
        a, b = t["args"]
        assert len(a) <= 5000 and len(b) <= 5000
        assert all(-10 ** 9 <= x <= 10 ** 9 for x in a + b)
        assert a == sorted(a) and b == sorted(b), "not sorted"


CHECKS["sorted-arrays-common-elements"] = (b_common, g_common, "exact")
VALIDATE["sorted-arrays-common-elements"] = v_common


# ---------------------------------------------------------------- MEDIUM

p = add(
    id="boats-to-carry-people", title="Boats to Carry People", diff="Medium", topic="Two Pointers",
    fn="minBoats", params=[("weights", "int[]"), ("limit", "int")], ret="int", cmp="exact",
    desc="<p>A group of people needs to cross a river. <code>weights[i]</code> is the weight of person <code>i</code>. Every boat can carry at most two people at once, and the combined weight on a boat must not exceed <code>limit</code>.</p><p>Every person weighs at most <code>limit</code>, so everyone can always travel, even alone. Return the smallest number of boats needed to carry everybody.</p><pre>weights = [3, 2, 2, 1], limit = 3\nboats: [1, 2], [2], [3]\nresult = 3</pre>",
    constraints=["1 &le; weights.length &le; 10,000", "1 &le; weights[i] &le; limit &le; 30,000"],
    hints=["Each boat holds at most two people, so the answer is at least half the number of people. What decides how many pairs you can form?",
           "Think about the heaviest remaining person. Who is the best partner for them, if any partner is possible at all?",
           "Sort the weights. If the heaviest person can share a boat with the lightest remaining person, do it; otherwise the heaviest travels alone. Use two pointers."],
    editorial=["Sort the weights. Consider the heaviest unassigned person. If even the lightest unassigned person cannot ride with them, nobody can, so they take a boat alone. Otherwise pairing them with the lightest person is never worse than pairing them with anyone else: the lightest is the most flexible partner, and using it here does not hurt anyone else's chances.",
               "Implement this with a left pointer at the lightest and a right pointer at the heaviest. Each iteration uses one boat, always moves the right pointer in, and moves the left pointer in as well when the pair fits. The sort dominates, so the time is O(n log n) with O(n) space for the sorted copy."],
    time="O(n log n)", space="O(n)",
    solution='''def minBoats(weights, limit):
    w = sorted(weights)
    lo, hi = 0, len(w) - 1
    boats = 0
    while lo <= hi:
        if w[lo] + w[hi] <= limit:
            lo += 1
        hi -= 1
        boats += 1
    return boats
''',
    tests=[[[1, 2], 3], [[3, 2, 2, 1], 3], [[3, 5, 3, 4], 5], [[5], 5], [[1, 1, 1, 1], 2], [[2, 2, 2], 4], [[1, 2, 3, 4, 5], 6],
           [[30000, 30000], 30000], [[1, 30000], 30000], [[1, 30000], 30001 - 1], [[4, 4, 4, 4, 4, 4], 8], [[2, 3, 3, 5, 6, 7, 8], 10]],
)
_r = rnd(2004)
p["tests"].append([[_r.randint(1, 30000) for _ in range(10000)], 30000])
p["tests"].append([[_r.randint(1, 15000) for _ in range(10000)], 30000])
p["tests"].append([[_r.randint(10000, 20000) for _ in range(9999)], 20000])
p["tests"].append([[_r.randint(1, 100) for _ in range(10000)], 150])


def b_boats(weights, limit):
    n = len(weights)

    @lru_cache(maxsize=None)
    def go(mask):
        if mask == 0:
            return 0
        i = (mask & -mask).bit_length() - 1
        rest = mask & ~(1 << i)
        best = 1 + go(rest)
        for j in range(n):
            if rest >> j & 1 and weights[i] + weights[j] <= limit:
                best = min(best, 1 + go(rest & ~(1 << j)))
        return best

    return go((1 << n) - 1)


def g_boats(r):
    limit = r.randint(1, 12)
    return [[r.randint(1, limit) for _ in range(r.randint(1, 8))], limit]


def v_boats(tests):
    for t in tests:
        w, limit = t["args"]
        assert 1 <= len(w) <= 10000
        assert 1 <= limit <= 30000
        assert all(1 <= x <= limit for x in w)


CHECKS["boats-to-carry-people"] = (b_boats, g_boats, "exact")
VALIDATE["boats-to-carry-people"] = v_boats


p = add(
    id="subarrays-with-product-below-k", title="Subarrays With Product Below K", diff="Medium", topic="Sliding Window",
    fn="countProductBelow", params=[("nums", "int[]"), ("k", "int")], ret="int", cmp="exact",
    desc="<p>You are given an array <code>nums</code> of positive integers and an integer <code>k</code>. Count the contiguous, non-empty subarrays whose elements multiply to a value strictly less than <code>k</code>.</p><p>Subarrays at different positions are counted separately even if their contents are identical.</p><pre>nums = [10, 5, 2, 6], k = 100\nresult = 8\n[10] [5] [2] [6] [10,5] [5,2] [2,6] [5,2,6]</pre>",
    constraints=["1 &le; nums.length &le; 10,000", "1 &le; nums[i] &le; 1,000", "0 &le; k &le; 10<sup>6</sup>"],
    hints=["Checking every subarray is O(n&sup2;). Notice that every number is at least 1, so extending a subarray never decreases its product.",
           "That monotonic behaviour means that if a window is too big, every longer window with the same start is too big as well.",
           "Use a window <code>[left, right]</code> with a running product. After adding <code>nums[right]</code>, shrink from the left while the product is at least k, then add <code>right - left + 1</code> to the answer."],
    editorial=["Fix the right end <code>right</code>. Because all values are positive integers, the product of <code>nums[left..right]</code> only grows as <code>left</code> moves to the left. So the valid starting points form one contiguous range ending at <code>right</code>, and the number of valid subarrays ending at <code>right</code> is exactly the window length.",
               "Maintain the product incrementally: multiply by the new element, then divide by <code>nums[left]</code> while the product is too large (stop shrinking when <code>left</code> passes <code>right</code>, which handles <code>k &le; 1</code> where nothing qualifies). Each index enters and leaves the window once, giving O(n) time and O(1) space."],
    time="O(n)", space="O(1)",
    solution='''def countProductBelow(nums, k):
    if k <= 1:
        return 0
    prod = 1
    left = 0
    count = 0
    for right, x in enumerate(nums):
        prod *= x
        while prod >= k:
            prod //= nums[left]
            left += 1
        count += right - left + 1
    return count
''',
    tests=[[[10, 5, 2, 6], 100], [[1, 2, 3], 0], [[1, 1, 1], 2], [[1], 1], [[1], 2], [[5, 5, 5], 5], [[1000, 1000, 1000, 1000, 1000], 1000000],
           [[1, 2, 3], 1000000], [[7], 8], [[7], 7], [[2, 2, 2, 2], 5], [[3, 1, 4, 1, 5, 9, 2, 6], 50]],
)
_r = rnd(2005)
p["tests"].append([[1] * 10000, 2])
p["tests"].append([[_r.randint(1, 5) for _ in range(10000)], 1000000])
p["tests"].append([[_r.randint(1, 1000) for _ in range(10000)], 1000000])
p["tests"].append([[_r.randint(1, 3) for _ in range(10000)], 40])


def b_prod(nums, k):
    cnt = 0
    for i in range(len(nums)):
        prod = 1
        for j in range(i, len(nums)):
            prod *= nums[j]
            if prod < k:
                cnt += 1
    return cnt


def g_prod(r):
    return [[r.randint(1, 6) for _ in range(r.randint(1, 9))], r.randint(0, 80)]


def v_prod(tests):
    for t in tests:
        a, k = t["args"]
        assert 1 <= len(a) <= 10000
        assert all(1 <= x <= 1000 for x in a)
        assert 0 <= k <= 10 ** 6


CHECKS["subarrays-with-product-below-k"] = (b_prod, g_prod, "exact")
VALIDATE["subarrays-with-product-below-k"] = v_prod


p = add(
    id="longest-ones-after-one-deletion", title="Longest Run of Ones After Deleting One", diff="Medium", topic="Sliding Window",
    fn="longestOnesAfterDeletion", params=[("nums", "int[]")], ret="int", cmp="exact",
    desc="<p>The array <code>nums</code> contains only <code>0</code> and <code>1</code>. You must delete exactly one element (it may be a <code>0</code> or a <code>1</code>). After the deletion the remaining elements close up with no gap.</p><p>Return the length of the longest block of consecutive <code>1</code>s you can end up with. If the array has no <code>1</code> after the deletion, the answer is 0.</p><pre>nums = [1, 1, 0, 1]\ndelete the 0 -> [1, 1, 1]\nresult = 3</pre>",
    constraints=["1 &le; nums.length &le; 10,000", "nums[i] is 0 or 1"],
    hints=["Deleting a 0 joins the run of ones on its left with the run on its right. Deleting a 1 only shortens a run.",
           "Think of it as finding the longest window that contains at most one 0. The deleted element is that 0.",
           "Slide a window, shrinking from the left whenever it holds two zeros. The answer is the largest window length minus 1, because one element must always be deleted, which also covers an array of all ones."],
    editorial=["A window with at most one zero becomes a run of ones once that zero is deleted, and its length drops by one. If the window has no zero at all, we still have to delete one element, which again costs one. So the answer is <code>max window length - 1</code> over all windows containing at most one zero.",
               "Maintain the window <code>[left, right]</code> and a count of zeros inside it. When the count exceeds one, move <code>left</code> forward until it is back to one. A single pass gives O(n) time and O(1) space. Edge cases fall out naturally: an array of all zeros has windows of length 1, giving 0, and a single element gives 0."],
    time="O(n)", space="O(1)",
    solution='''def longestOnesAfterDeletion(nums):
    left = 0
    zeros = 0
    best = 0
    for right, x in enumerate(nums):
        if x == 0:
            zeros += 1
        while zeros > 1:
            if nums[left] == 0:
                zeros -= 1
            left += 1
        best = max(best, right - left + 1)
    return best - 1
''',
    tests=[[[1, 1, 0, 1]], [[0, 1, 1, 1, 0, 1, 1, 0, 1]], [[1, 1, 1]], [[0]], [[1]], [[0, 0, 0]], [[1, 0]], [[0, 1]], [[1, 0, 1]], [[1, 1, 0, 0, 1, 1, 1]],
           [[0, 0, 1, 1, 0, 1, 0, 0]], [[1, 0, 1, 0, 1, 0, 1]]],
)
_r = rnd(2006)
p["tests"].append([[1] * 10000])
p["tests"].append([[1 if _r.random() < 0.9 else 0 for _ in range(10000)]])
p["tests"].append([[i % 2 for i in range(10000)]])
p["tests"].append([[0] * 10000])
p["tests"].append([[1 if _r.random() < 0.5 else 0 for _ in range(10000)]])


def b_ones_del(nums):
    best = 0
    for i in range(len(nums)):
        rest = nums[:i] + nums[i + 1:]
        run = 0
        for x in rest:
            run = run + 1 if x == 1 else 0
            best = max(best, run)
    return best


def v_ones_del(tests):
    for t in tests:
        a = t["args"][0]
        assert 1 <= len(a) <= 10000
        assert all(x in (0, 1) for x in a)


CHECKS["longest-ones-after-one-deletion"] = (b_ones_del, lambda r: [gen_arr(r, 0, 1, 1, 12)], "exact")
VALIDATE["longest-ones-after-one-deletion"] = v_ones_del


p = add(
    id="min-removals-from-ends-to-reach-sum", title="Minimum Removals From the Ends to Reach a Sum", diff="Medium", topic="Sliding Window",
    fn="minRemovals", params=[("nums", "int[]"), ("x", "int")], ret="int", cmp="exact",
    desc="<p>In one move you may delete either the first or the last element of <code>nums</code>, and you subtract the deleted value from <code>x</code>. Return the smallest number of moves that makes <code>x</code> exactly <code>0</code>, or <code>-1</code> if that cannot be done.</p><p>The array changes after every move, so later moves operate on what remains.</p><pre>nums = [1, 1, 4, 2, 3], x = 5\nremove 3 (right), then 2 (right): 5 - 3 - 2 = 0\nresult = 2</pre>",
    constraints=["1 &le; nums.length &le; 10,000", "1 &le; nums[i] &le; 10,000", "1 &le; x &le; 10<sup>9</sup>"],
    hints=["Whatever you remove is some prefix plus some suffix of the array. What is left over?",
           "The remaining middle part is a contiguous subarray whose sum equals <code>sum(nums) - x</code>. Fewest removals means longest middle.",
           "All values are positive, so a variable-size sliding window can find the longest subarray with a given sum. Return <code>n - longest</code>, or -1 if no such subarray exists."],
    editorial=["Removing elements from both ends leaves a contiguous block in the middle. If the removed values sum to <code>x</code>, the block sums to <code>target = total - x</code>. Minimising the moves is the same as maximising the block length.",
               "If <code>target &lt; 0</code> the answer is -1. If <code>target == 0</code> everything must be removed, so the answer is n. Otherwise, because all numbers are positive, a window sum grows when extended right and shrinks when the left edge moves, so a two-pointer sweep finds the longest subarray summing to <code>target</code> in O(n). The result is <code>n - longest</code>, or -1 if none was found."],
    time="O(n)", space="O(1)",
    solution='''def minRemovals(nums, x):
    n = len(nums)
    target = sum(nums) - x
    if target < 0:
        return -1
    if target == 0:
        return n
    best = -1
    left = 0
    cur = 0
    for right in range(n):
        cur += nums[right]
        while cur > target:
            cur -= nums[left]
            left += 1
        if cur == target:
            best = max(best, right - left + 1)
    return -1 if best < 0 else n - best
''',
    tests=[[[1, 1, 4, 2, 3], 5], [[5, 6, 7, 8, 9], 4], [[3, 2, 20, 1, 1, 3], 10], [[1], 1], [[1], 2], [[1, 1], 2], [[2, 3, 1], 6], [[2, 3, 1], 7],
           [[10, 1, 1, 10], 12], [[8828, 9581, 49, 9818, 9974, 9869, 9391, 1], 134365], [[5, 5, 5, 5], 10], [[4, 1, 1, 1, 4], 3]],
)
_r = rnd(2007)
_a = [_r.randint(1, 10) for _ in range(10000)]
p["tests"].append([_a, sum(_a) // 2])
_a = [_r.randint(1, 10000) for _ in range(10000)]
p["tests"].append([_a, sum(_a[:3000]) + sum(_a[-2000:])])
p["tests"].append([[1] * 10000, 10000])
p["tests"].append([[1] * 10000, 10001])
_a = [_r.randint(1, 10000) for _ in range(10000)]
p["tests"].append([_a, 987654321])


def b_removals(nums, x):
    n = len(nums)
    best = -1
    for l in range(n + 1):
        s = sum(nums[:l])
        for r in range(n - l + 1):
            tot = s + (sum(nums[n - r:]) if r else 0)
            if tot == x and (best < 0 or l + r < best):
                best = l + r
    return best


def g_removals(r):
    a = [r.randint(1, 6) for _ in range(r.randint(1, 9))]
    return [a, r.randint(1, sum(a) + 3)]


def v_removals(tests):
    for t in tests:
        a, x = t["args"]
        assert 1 <= len(a) <= 10000
        assert all(1 <= v <= 10000 for v in a)
        assert 1 <= x <= 10 ** 9


CHECKS["min-removals-from-ends-to-reach-sum"] = (b_removals, g_removals, "exact")
VALIDATE["min-removals-from-ends-to-reach-sum"] = v_removals


p = add(
    id="four-sum-unique-quadruplets", title="4Sum", diff="Medium", topic="Two Pointers",
    fn="fourSum", params=[("nums", "int[]"), ("target", "int")], ret="int[][]", cmp="rowset",
    desc="<p>Given an integer array <code>nums</code> and an integer <code>target</code>, return every distinct quadruplet of values <code>[a, b, c, d]</code> that can be chosen from four different positions of <code>nums</code> and satisfies <code>a + b + c + d = target</code>.</p><p>Two quadruplets are the same if they contain the same values, regardless of positions. Write each quadruplet in <strong>non-decreasing</strong> order; the order of the quadruplets in the result does not matter. Return an empty list when there is none.</p><pre>nums = [1, 0, -1, 0, -2, 2], target = 0\nresult = [[-2,-1,1,2], [-2,0,0,2], [-1,0,0,1]]</pre>",
    constraints=["1 &le; nums.length &le; 150", "-10<sup>6</sup> &le; nums[i] &le; 10<sup>6</sup>", "-4 &times; 10<sup>6</sup> &le; target &le; 4 &times; 10<sup>6</sup>"],
    hints=["Four nested loops are O(n&#8308;). Can you reduce the problem step by step, as in 3Sum and Two Sum?",
           "Sort the array. Fix the first two values with two loops, then find the other two with two pointers moving inward.",
           "Skip repeated values at each of the four levels (first, second, and inside the pointer loop after a match) so each quadruplet is reported once."],
    editorial=["Sort the array. Loop over the first value <code>i</code>, then over the second value <code>j &gt; i</code>, and finish with <code>lo = j + 1</code> and <code>hi = n - 1</code>. If the four-value sum is below the target, move <code>lo</code> right; if above, move <code>hi</code> left; if equal, record it and move both pointers past their duplicates.",
               "To avoid duplicate quadruplets, skip a value at the <code>i</code> level when it equals the previous <code>i</code> value, likewise at the <code>j</code> level (only when <code>j &gt; i + 1</code>), and skip equal neighbours after each match. Time is O(n&sup3;) after the O(n log n) sort, and extra space is O(1) besides the output."],
    time="O(n&sup3;)", space="O(1) extra",
    solution='''def fourSum(nums, target):
    a = sorted(nums)
    n = len(a)
    res = []
    for i in range(n - 3):
        if i > 0 and a[i] == a[i - 1]:
            continue
        for j in range(i + 1, n - 2):
            if j > i + 1 and a[j] == a[j - 1]:
                continue
            lo, hi = j + 1, n - 1
            while lo < hi:
                s = a[i] + a[j] + a[lo] + a[hi]
                if s < target:
                    lo += 1
                elif s > target:
                    hi -= 1
                else:
                    res.append([a[i], a[j], a[lo], a[hi]])
                    lo += 1
                    hi -= 1
                    while lo < hi and a[lo] == a[lo - 1]:
                        lo += 1
                    while lo < hi and a[hi] == a[hi + 1]:
                        hi -= 1
    return res
''',
    tests=[[[1, 0, -1, 0, -2, 2], 0], [[2, 2, 2, 2, 2], 8], [[0, 0, 0, 0], 0], [[1, 2, 3], 6], [[5], 5], [[1, 1, 1, 1], 5],
           [[-3, -1, 0, 2, 4, 5], 2], [[1000000, 1000000, 1000000, 1000000], 4000000], [[-1000000, -1000000, -1000000, -1000000, 7], -4000000],
           [[0, 0, 0, 0, 0, 0], 0], [[-2, -1, -1, 1, 1, 2, 2], 0], [[4, -4, 3, -3, 2, -2, 1, -1], 0]],
)
_r = rnd(2008)
p["tests"].append([[_r.randint(-12, 12) for _ in range(150)], 0])
p["tests"].append([[_r.randint(-1000000, 1000000) for _ in range(150)], 0])
p["tests"].append([[_r.randint(-30, 30) for _ in range(150)], 17])
p["tests"].append([[0] * 150, 0])
p["tests"].append([[_r.randint(-5, 5) for _ in range(150)], -3])


def b_foursum(nums, target):
    found = set()
    for c in combinations(range(len(nums)), 4):
        if sum(nums[i] for i in c) == target:
            found.add(tuple(sorted(nums[i] for i in c)))
    return [list(t) for t in sorted(found)]


def g_foursum(r):
    return [gen_arr(r, -4, 4, 1, 9), r.randint(-8, 8)]


def v_foursum(tests):
    for t in tests:
        a, target = t["args"]
        assert 1 <= len(a) <= 150
        assert all(-10 ** 6 <= x <= 10 ** 6 for x in a)
        assert -4 * 10 ** 6 <= target <= 4 * 10 ** 6
        rows = t["expected"]
        assert all(len(row) == 4 and row == sorted(row) for row in rows), "rows must be sorted"
        assert len({tuple(row) for row in rows}) == len(rows), "duplicate rows"
        assert sum(len(row) for row in rows) <= 20000, "expected output too big"


CHECKS["four-sum-unique-quadruplets"] = (b_foursum, g_foursum, "rowset")
VALIDATE["four-sum-unique-quadruplets"] = v_foursum


# ---------------------------------------------------------------- HARD

p = add(
    id="shortest-window-containing-subsequence", title="Shortest Window Containing a Subsequence", diff="Hard", topic="Sliding Window",
    fn="shortestWindowLength", params=[("nums", "int[]"), ("pattern", "int[]")], ret="int", cmp="exact",
    desc="<p>You are given two integer arrays, <code>nums</code> and <code>pattern</code>. Find the shortest <em>contiguous</em> subarray of <code>nums</code> in which <code>pattern</code> appears as a subsequence, that is, you can pick the pattern's values in order from the subarray, skipping any elements in between.</p><p>Return the length of that shortest subarray, or <code>-1</code> if no subarray works. Only the length is asked for, so ties between different windows do not matter.</p><pre>nums = [1, 3, 2, 4, 3, 2, 5, 4], pattern = [3, 2, 4]\nsubarray [3, 2, 4] (positions 1 to 3) works\nresult = 3</pre>",
    constraints=["1 &le; nums.length &le; 10,000", "1 &le; pattern.length &le; 100", "-1,000 &le; nums[i], pattern[i] &le; 1,000"],
    hints=["Checking every subarray against the pattern is far too slow. Start from a smarter question: for a fixed ending position, which start gives the shortest window?",
           "Scan forward matching the pattern greedily until it is fully matched. That gives a valid end. Now walk backward from that end, matching the pattern in reverse, to find the latest possible start.",
           "After recording the window, restart the forward scan from just after that start (not from the end). Repeat until the forward scan can no longer complete the pattern, and keep the smallest length seen."],
    editorial=["Scan forward with a pointer into the pattern, advancing it whenever the current element matches. When the whole pattern is matched at index <code>end</code>, the window <code>[?, end]</code> is valid for some start, but the start found by the forward scan is not necessarily the tightest. Walk backward from <code>end</code>, matching the pattern from its last element to its first; the position where the backward walk finishes is the latest start for which a valid window ends at <code>end</code>. Record <code>end - start + 1</code>.",
               "Next, continue the search from <code>start + 1</code>: any better window must start after the current start (a window starting at <code>start</code> or earlier cannot beat it for the same end region). Repeat until the forward scan runs out of array. This works in roughly O(n * m) time in the worst case (n = array length, m = pattern length) with O(1) extra space. A dynamic programming formulation that stores, for every pattern prefix, the latest start of a match is equivalent and gives the same O(n * m) bound."],
    time="O(n * m)", space="O(1)",
    solution='''def shortestWindowLength(nums, pattern):
    n, m = len(nums), len(pattern)
    best = -1
    i = 0
    while i < n:
        j = 0
        k = i
        while k < n and j < m:
            if nums[k] == pattern[j]:
                j += 1
            k += 1
        if j < m:
            break
        end = k - 1
        j = m - 1
        k = end
        while j >= 0:
            if nums[k] == pattern[j]:
                j -= 1
            k -= 1
        start = k + 1
        length = end - start + 1
        if best < 0 or length < best:
            best = length
        i = start + 1
    return best
''',
    tests=[[[1, 3, 2, 4, 3, 2, 5, 4], [3, 2, 4]], [[1, 2, 3, 4, 5], [2, 4]], [[1, 2, 3, 4, 5], [5, 1]], [[7], [7]], [[7], [8]], [[1, 1, 1, 1], [1, 1]],
           [[1, 2, 1, 2, 1, 2], [1, 2, 1]], [[5, 1, 5, 2, 5, 3, 5], [1, 2, 3]], [[2, 2, 2], [2, 2, 2, 2]], [[1, 2, 3], [1, 2, 3]],
           [[3, 1, 2, 1, 3, 2, 1], [1, 3, 1]], [[0, 0, 0], [0]], [[-1, 5, -1, 5, -1], [-1, -1]], [[4, 9, 4, 9, 9, 4], [9, 4]]],
)
_r = rnd(2009)
p["tests"].append([[_r.randint(1, 5) for _ in range(10000)], [_r.randint(1, 5) for _ in range(50)]])
p["tests"].append([[_r.randint(1, 2) for _ in range(10000)], [_r.randint(1, 2) for _ in range(100)]])
p["tests"].append([[(i % 7) - 3 for i in range(10000)], [(i % 7) - 3 for i in range(3, 80)]])
p["tests"].append([[1] * 10000, [1] * 100])
p["tests"].append([[_r.randint(-1000, 1000) for _ in range(10000)], [_r.randint(-1000, 1000) for _ in range(3)]])
p["tests"].append([[_r.randint(1, 4) for _ in range(10000)], [1000] + [1] * 5])
_a = [_r.randint(1, 3) for _ in range(10000)]
p["tests"].append([_a, [_a[i] for i in sorted(_r.sample(range(4000, 4800), 100))]])


def b_window_subseq(nums, pattern):
    def has(sub):
        it = iter(sub)
        return all(any(x == y for y in it) for x in pattern)

    best = -1
    for i in range(len(nums)):
        for j in range(i, len(nums)):
            if has(nums[i:j + 1]):
                if best < 0 or j - i + 1 < best:
                    best = j - i + 1
                break
    return best


def g_window_subseq(r):
    nums = [r.randint(1, 3) for _ in range(r.randint(1, 12))]
    return [nums, [r.randint(1, 3) for _ in range(r.randint(1, 4))]]


def v_window_subseq(tests):
    for t in tests:
        a, pat = t["args"]
        assert 1 <= len(a) <= 10000
        assert 1 <= len(pat) <= 100
        assert all(-1000 <= x <= 1000 for x in a + pat)


CHECKS["shortest-window-containing-subsequence"] = (b_window_subseq, g_window_subseq, "exact")
VALIDATE["shortest-window-containing-subsequence"] = v_window_subseq


p = add(
    id="min-k-bit-flips-to-all-ones", title="Minimum K-Window Flips to All Ones", diff="Hard", topic="Sliding Window",
    fn="minKWindowFlips", params=[("nums", "int[]"), ("k", "int")], ret="int", cmp="exact",
    desc="<p>The array <code>nums</code> contains only <code>0</code> and <code>1</code>. One operation picks any block of exactly <code>k</code> consecutive elements and flips every bit in it (<code>0</code> becomes <code>1</code> and <code>1</code> becomes <code>0</code>).</p><p>Return the minimum number of operations needed to make every element equal to <code>1</code>, or <code>-1</code> if it is impossible.</p><pre>nums = [0, 0, 0, 1, 0, 1, 1, 0], k = 3\nflip [0..2] -> 1 1 1 1 0 1 1 0\nflip [4..6] -> 1 1 1 1 1 0 0 0\nflip [5..7] -> 1 1 1 1 1 1 1 1\nresult = 3</pre>",
    constraints=["1 &le; k &le; nums.length &le; 10,000", "nums[i] is 0 or 1"],
    hints=["Flipping the same block twice cancels out, and the order of flips does not matter. So each starting position is either used once or not at all.",
           "Look at the leftmost 0. Only a block starting exactly at that position can fix it without touching anything further left, so that flip is forced.",
           "Sweep left to right with a greedy rule. To know the current state of a bit quickly, track how many active flips cover it (only the parity matters) and schedule the end of each flip with a difference array or a queue."],
    editorial=["Because flips commute and cancel in pairs, the final state depends only on which start positions are used. Process positions from left to right. When you reach index <code>i</code>, its current value is its original value XOR the parity of the flips that cover it. If it is 0, the only block that can repair it without disturbing earlier, already fixed positions starts at <code>i</code>, so flipping there is forced. If <code>i + k &gt; n</code> such a block does not fit, and the answer is -1.",
               "Track the number of covering flips as a running parity: toggle it when you start a flip at <code>i</code>, and toggle it back at index <code>i + k</code> using a difference array of size n + 1. Every index is visited once, so the time is O(n) and the space is O(n). Because every flip is forced, the count is minimal."],
    time="O(n)", space="O(n)",
    solution='''def minKWindowFlips(nums, k):
    n = len(nums)
    end = [0] * (n + 1)
    parity = 0
    flips = 0
    for i in range(n):
        parity ^= end[i]
        if nums[i] ^ parity == 0:
            if i + k > n:
                return -1
            flips += 1
            parity ^= 1
            end[i + k] ^= 1
    return flips
''',
    tests=[[[0, 1, 0], 1], [[1, 1, 0], 2], [[0, 0, 0, 1, 0, 1, 1, 0], 3], [[1], 1], [[0], 1], [[1, 1, 1], 3], [[0, 0, 0], 3], [[0, 1, 0], 3],
           [[1, 0, 1, 0, 1], 2], [[0, 0, 0, 0, 0, 0], 2], [[1, 0, 0, 1, 1, 0, 1], 4], [[0, 1, 1, 0], 2]],
)
_r = rnd(2010)
p["tests"].append([[_r.randint(0, 1) for _ in range(10000)], 7])
p["tests"].append([[_r.randint(0, 1) for _ in range(10000)], 1])
p["tests"].append([[_r.randint(0, 1) for _ in range(10000)], 10000])
p["tests"].append([[0] * 10000, 2])
p["tests"].append([[0] * 9999, 3])
_n, _k = 10000, 37
_a = [1] * _n
for _ in range(1500):
    _s = _r.randint(0, _n - _k)
    for _i in range(_s, _s + _k):
        _a[_i] ^= 1
p["tests"].append([_a, _k])


def b_kflips(nums, k):
    n = len(nums)
    m = n - k + 1
    best = -1
    for mask in range(1 << m):
        a = list(nums)
        for s in range(m):
            if mask >> s & 1:
                for i in range(s, s + k):
                    a[i] ^= 1
        if all(a):
            c = bin(mask).count("1")
            if best < 0 or c < best:
                best = c
    return best


def g_kflips(r):
    n = r.randint(1, 10)
    return [[r.randint(0, 1) for _ in range(n)], r.randint(1, n)]


def v_kflips(tests):
    for t in tests:
        a, k = t["args"]
        assert 1 <= k <= len(a) <= 10000
        assert all(x in (0, 1) for x in a)


CHECKS["min-k-bit-flips-to-all-ones"] = (b_kflips, g_kflips, "exact")
VALIDATE["min-k-bit-flips-to-all-ones"] = v_kflips
