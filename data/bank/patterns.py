"""Problems: binary search, sliding window, two pointers, stack, intervals. See data/lib.py for the registry."""
from itertools import combinations
from fractions import Fraction

from lib import add, rnd, CHECKS, VALIDATE, gen_arr  # noqa: F401

INT_MIN, INT_MAX = -(2 ** 31), 2 ** 31 - 1


# ---------------------------------------------------------------- EASY

p = add(
    id="search-insert-position", title="Search Insert Position", diff="Easy", topic="Binary Search",
    fn="searchInsert", params=[("nums", "int[]"), ("target", "int")], ret="int", cmp="exact",
    desc="<p>You are given a strictly increasing array <code>nums</code> and an integer <code>target</code>. Return the index at which <code>target</code> is found. If it is not present, return the index where it would have to be inserted so that the array stays sorted.</p><p>Your solution must run in O(log n) time.</p>",
    constraints=["0 &le; nums.length &le; 10,000", "-2<sup>31</sup> &le; nums[i], target &le; 2<sup>31</sup> - 1", "nums is sorted in strictly increasing order (no duplicates)"],
    hints=["A linear scan finds the first element that is not smaller than the target, but it is too slow for the intended bound.",
           "The answer is the number of elements strictly smaller than <code>target</code>. Because the array is sorted, those elements form a prefix.",
           "Binary search for the first index whose value is &ge; target. Keep the search range half-open, <code>[lo, hi)</code>, and return <code>lo</code> when it closes."],
    editorial=["The insertion point is the first index <code>i</code> with <code>nums[i] &ge; target</code>, or <code>n</code> when no such index exists. This is a classic lower bound search. The predicate <code>nums[i] &ge; target</code> is false for a prefix and true for the rest, so we can binary search for the boundary.",
               "Keep <code>lo = 0, hi = n</code>. While <code>lo &lt; hi</code>, take <code>mid = (lo + hi) // 2</code>; if <code>nums[mid] &lt; target</code> move <code>lo = mid + 1</code>, otherwise <code>hi = mid</code>. When the loop ends <code>lo</code> is the boundary. Each step halves the range, giving O(log n) time and O(1) space."],
    time="O(log n)", space="O(1)",
    solution='''def searchInsert(nums, target):
    lo, hi = 0, len(nums)
    while lo < hi:
        mid = (lo + hi) // 2
        if nums[mid] < target:
            lo = mid + 1
        else:
            hi = mid
    return lo
''',
    tests=[[[1, 3, 5, 6], 5], [[1, 3, 5, 6], 2], [[1, 3, 5, 6], 7], [[1, 3, 5, 6], 0], [[], 4], [[10], 10], [[10], 3],
           [[10], 11], [[-5, -2, 0, 8], -2], [[-5, -2, 0, 8], -3], [[INT_MIN, 0, INT_MAX], INT_MAX],
           [[INT_MIN, 0, INT_MAX], INT_MIN + 1]],
)
_r = rnd(201)
_a = sorted(_r.sample(range(INT_MIN, INT_MAX), 10000))
p["tests"].append([_a, _a[7777]])
p["tests"].append([_a, _a[7777] + 1 if _a[7777] + 1 not in _a else _a[7777] - 1])
p["tests"].append([_a, INT_MAX])
p["tests"].append([_a, INT_MIN])


def b_sip(nums, target):
    cnt = 0
    for x in nums:
        if x < target:
            cnt += 1
    return cnt


def g_sip(r):
    a = sorted(r.sample(range(-12, 13), r.randint(0, 10)))
    return [a, r.randint(-13, 13)]


def v_sip(tests):
    for t in tests:
        nums, target = t["args"]
        assert len(nums) <= 10000
        assert all(nums[i] < nums[i + 1] for i in range(len(nums) - 1))


CHECKS["search-insert-position"] = (b_sip, g_sip, "exact")
VALIDATE["search-insert-position"] = v_sip

p = add(
    id="move-zeroes", title="Move Zeroes", diff="Easy", topic="Two Pointers",
    fn="moveZeroes", params=[("nums", "int[]")], ret="int[]", cmp="exact",
    desc="<p>Given an integer array <code>nums</code>, move every <code>0</code> to the end while keeping the relative order of the non-zero values unchanged. Return the resulting array.</p><p>Try to do the rearrangement in a single pass with O(1) extra space, by working in place on the array you were given.</p>",
    constraints=["0 &le; nums.length &le; 10,000", "-2<sup>31</sup> &le; nums[i] &le; 2<sup>31</sup> - 1"],
    hints=["Collecting the non-zero values into a new list and padding with zeros works, but uses extra memory.",
           "Use a write pointer that marks where the next non-zero value belongs. Everything before it is already final.",
           "Scan with a read pointer. Whenever <code>nums[read]</code> is non-zero, swap it with <code>nums[write]</code> and advance <code>write</code>."],
    editorial=["Keep two pointers. <code>write</code> is the position where the next non-zero element must be placed; <code>read</code> scans the array. When <code>nums[read] != 0</code>, swap it into <code>nums[write]</code> and advance <code>write</code>. All indices below <code>write</code> hold the non-zero values seen so far, in their original order, and everything between <code>write</code> and <code>read</code> is a zero.",
               "Swapping (rather than copying and then filling with zeros) means each element is touched a constant number of times and zeros drift to the right automatically. Time is O(n), space O(1)."],
    time="O(n)", space="O(1)",
    solution='''def moveZeroes(nums):
    write = 0
    for read in range(len(nums)):
        if nums[read] != 0:
            nums[write], nums[read] = nums[read], nums[write]
            write += 1
    return nums
''',
    tests=[[[0, 1, 0, 3, 12]], [[0]], [[1, 2, 3]], [[0, 0, 0]], [[]], [[5]], [[0, 0, 7]], [[7, 0, 0]],
           [[-1, 0, -2, 0, -3]], [[INT_MIN, 0, INT_MAX, 0]], [[0, 1, 0, 1, 0, 1, 0]]],
)
_r = rnd(202)
p["tests"].append([[_r.choice([0, 0, _r.randint(-99, 99)]) for _ in range(10000)]])
p["tests"].append([[0] * 5000 + [_r.randint(1, 9) for _ in range(5000)]])
p["tests"].append([[_r.randint(INT_MIN, INT_MAX) if _r.random() < 0.3 else 0 for _ in range(10000)]])


def b_mz(nums):
    return [x for x in nums if x != 0] + [x for x in nums if x == 0]


def v_mz(tests):
    for t in tests:
        assert len(t["args"][0]) <= 10000


CHECKS["move-zeroes"] = (b_mz, lambda r: [gen_arr(r, -3, 3, 0, 12)], "exact")
VALIDATE["move-zeroes"] = v_mz

p = add(
    id="remove-duplicates-from-sorted-array", title="Remove Duplicates from Sorted Array", diff="Easy", topic="Two Pointers",
    fn="removeDuplicates", params=[("nums", "int[]")], ret="int[]", cmp="exact",
    desc="<p>The array <code>nums</code> is sorted in non-decreasing order. Remove the duplicates so that every distinct value appears exactly once, keeping the values in order. Return the resulting array.</p><p>Aim for O(n) time and O(1) extra space by overwriting the array in place.</p>",
    constraints=["0 &le; nums.length &le; 10,000", "-2<sup>31</sup> &le; nums[i] &le; 2<sup>31</sup> - 1", "nums is sorted in non-decreasing order"],
    hints=["Equal values are adjacent because the array is sorted, so a duplicate is just an element equal to its predecessor.",
           "Keep a slow pointer at the end of the deduplicated prefix and a fast pointer that scans ahead.",
           "When <code>nums[fast]</code> differs from <code>nums[slow]</code>, advance <code>slow</code> and copy the value there. The answer is the first <code>slow + 1</code> elements."],
    editorial=["Since equal values are grouped together, each new distinct value is the first element after a run of equal ones. Let <code>slow</code> point at the last value kept. For each <code>fast</code> from 1 onward, if <code>nums[fast] != nums[slow]</code> then it is a new value: increment <code>slow</code> and write <code>nums[fast]</code> into that slot.",
               "At the end the first <code>slow + 1</code> positions hold the distinct values in order. The array is scanned once, so time is O(n); only two indices are used, so space is O(1) beyond the returned slice. Remember to handle the empty array."],
    time="O(n)", space="O(1)",
    solution='''def removeDuplicates(nums):
    if not nums:
        return []
    slow = 0
    for fast in range(1, len(nums)):
        if nums[fast] != nums[slow]:
            slow += 1
            nums[slow] = nums[fast]
    return nums[:slow + 1]
''',
    tests=[[[1, 1, 2]], [[0, 0, 1, 1, 1, 2, 2, 3, 3, 4]], [[]], [[7]], [[2, 2, 2, 2]], [[1, 2, 3]], [[-3, -3, -1, 0, 0, 5]],
           [[INT_MIN, INT_MIN, INT_MAX, INT_MAX]], [[-1, -1, -1, 4, 4, 9, 9, 9, 9]]],
)
_r = rnd(203)
p["tests"].append([sorted(_r.randint(-500, 500) for _ in range(10000))])
p["tests"].append([[3] * 10000])
p["tests"].append([sorted(_r.randint(INT_MIN, INT_MAX) for _ in range(10000))])
p["tests"].append([list(range(-5000, 5000))])


def b_rd(nums):
    return sorted(set(nums))


def g_rd(r):
    return [sorted(gen_arr(r, -4, 4, 0, 12))]


def v_rd(tests):
    for t in tests:
        a = t["args"][0]
        assert len(a) <= 10000
        assert all(a[i] <= a[i + 1] for i in range(len(a) - 1))


CHECKS["remove-duplicates-from-sorted-array"] = (b_rd, g_rd, "exact")
VALIDATE["remove-duplicates-from-sorted-array"] = v_rd


# ---------------------------------------------------------------- MEDIUM

p = add(
    id="find-first-and-last-position", title="Find First and Last Position of Target", diff="Medium", topic="Binary Search",
    fn="searchRange", params=[("nums", "int[]"), ("target", "int")], ret="int[]", cmp="exact",
    desc="<p>Given an array <code>nums</code> sorted in non-decreasing order, find where the value <code>target</code> starts and ends. Return <code>[first, last]</code>, the lowest and highest indices holding <code>target</code>. If <code>target</code> does not occur, return <code>[-1, -1]</code>.</p><p>The solution must run in O(log n) time, so scanning outward from a match is not good enough when there are many duplicates.</p>",
    constraints=["0 &le; nums.length &le; 10,000", "-2<sup>31</sup> &le; nums[i], target &le; 2<sup>31</sup> - 1", "nums is sorted in non-decreasing order"],
    hints=["One binary search can find <em>some</em> index holding the target, but with many duplicates that index tells you little about the edges.",
           "Run two binary searches that each look for a boundary: the first index with value &ge; target and the first index with value &gt; target.",
           "The range is <code>[lower, upper - 1]</code>. If <code>lower == upper</code> (or <code>lower</code> is out of bounds) the target is absent."],
    editorial=["Define <code>lowerBound(x)</code> as the first index whose value is &ge; x, or <code>n</code> if none. The first occurrence of <code>target</code> is <code>lowerBound(target)</code> provided that index is in range and holds the target. The index after the last occurrence is <code>lowerBound(target + 1)</code>, so the last occurrence is that minus one.",
               "Both bounds come from the same binary search routine, so the total cost is two O(log n) searches. Be careful that <code>target + 1</code> can exceed the 32-bit range in fixed-width languages; implementing an <em>upper</em> bound with a strict <code>nums[mid] &le; target</code> test avoids that."],
    time="O(log n)", space="O(1)",
    solution='''def searchRange(nums, target):
    def lower(strict):
        lo, hi = 0, len(nums)
        while lo < hi:
            mid = (lo + hi) // 2
            if nums[mid] < target or (strict and nums[mid] == target):
                lo = mid + 1
            else:
                hi = mid
        return lo

    first = lower(False)
    if first == len(nums) or nums[first] != target:
        return [-1, -1]
    return [first, lower(True) - 1]
''',
    tests=[[[5, 7, 7, 8, 8, 10], 8], [[5, 7, 7, 8, 8, 10], 6], [[], 0], [[1], 1], [[1], 2], [[2, 2, 2, 2], 2],
           [[1, 2, 3, 3, 3, 4], 3], [[1, 2, 3, 4], 1], [[1, 2, 3, 4], 4], [[-4, -4, -1, 0], -4],
           [[INT_MIN, INT_MIN, 0, INT_MAX, INT_MAX], INT_MAX], [[INT_MIN, INT_MIN, 0, INT_MAX, INT_MAX], INT_MIN]],
)
_r = rnd(204)
_a = sorted(_r.randint(-300, 300) for _ in range(10000))
p["tests"].append([_a, _a[4321]])
p["tests"].append([_a, 301])
p["tests"].append([[8] * 10000, 8])
p["tests"].append([[1] * 5000 + [2] * 5000, 2])
p["tests"].append([sorted(_r.randint(INT_MIN, INT_MAX) for _ in range(10000)), 12345])


def b_fl(nums, target):
    idx = [i for i, x in enumerate(nums) if x == target]
    return [idx[0], idx[-1]] if idx else [-1, -1]


def g_fl(r):
    return [sorted(gen_arr(r, -4, 4, 0, 12)), r.randint(-5, 5)]


def v_fl(tests):
    for t in tests:
        nums, _ = t["args"]
        assert len(nums) <= 10000
        assert all(nums[i] <= nums[i + 1] for i in range(len(nums) - 1))


CHECKS["find-first-and-last-position"] = (b_fl, g_fl, "exact")
VALIDATE["find-first-and-last-position"] = v_fl

p = add(
    id="capacity-to-ship-packages", title="Capacity to Ship Packages Within D Days", diff="Medium", topic="Binary Search",
    fn="shipWithinDays", params=[("weights", "int[]"), ("days", "int")], ret="int", cmp="exact",
    desc="<p>A conveyor belt carries packages with the given <code>weights</code>, in the order they arrive. Each day the ship loads packages in that order, without reordering and without exceeding its weight <code>capacity</code>, then sails. A package cannot be split across days.</p><p>Return the smallest ship capacity that lets all packages be shipped within <code>days</code> days.</p>",
    constraints=["1 &le; days &le; weights.length &le; 5,000", "1 &le; weights[i] &le; 500"],
    hints=["Try a fixed capacity: how would you count the number of days it needs? Load greedily and start a new day when the next package no longer fits.",
           "If a capacity works, any larger capacity works too, so feasibility is monotonic in the capacity.",
           "Binary search the capacity between <code>max(weights)</code> (the heaviest single package must fit) and <code>sum(weights)</code> (ship everything in one day), using the greedy count as the test."],
    editorial=["The capacity must be at least the heaviest package and is never worth more than the total weight. For a candidate capacity, simulate greedily: keep adding packages to the current day until the next one would overflow, then begin a new day. Greedy loading uses the fewest possible days for that capacity.",
               "Since a larger capacity never needs more days, the predicate \"fits within <code>days</code>\" flips from false to true exactly once. Binary search the smallest capacity where it is true. There are about log(sum) iterations, each costing O(n), for O(n log(sum)) time and O(1) space."],
    time="O(n log S)", space="O(1)",
    solution='''def shipWithinDays(weights, days):
    def need(cap):
        d, load = 1, 0
        for w in weights:
            if load + w > cap:
                d += 1
                load = 0
            load += w
        return d

    lo, hi = max(weights), sum(weights)
    while lo < hi:
        mid = (lo + hi) // 2
        if need(mid) <= days:
            hi = mid
        else:
            lo = mid + 1
    return lo
''',
    tests=[[[1, 2, 3, 4, 5, 6, 7, 8, 9, 10], 5], [[3, 2, 2, 4, 1, 4], 3], [[1, 2, 3, 1, 1], 4], [[7], 1], [[5, 5, 5, 5], 1],
           [[5, 5, 5, 5], 4], [[1, 1, 1, 1, 1, 1], 2], [[10, 1, 1, 10], 2], [[500, 500, 500], 2],
           [[1, 500, 1, 500, 1], 3], [[2, 3], 1]],
)
_r = rnd(205)
_w = [_r.randint(1, 500) for _ in range(5000)]
p["tests"].append([_w, 1])
p["tests"].append([_w, 5000])
p["tests"].append([_w, 37])
p["tests"].append([_w, 1200])
p["tests"].append([[500] * 5000, 100])
p["tests"].append([[_r.randint(1, 20) for _ in range(5000)], 250])


def b_ship(weights, days):
    cap = max(weights)
    while True:
        d, load = 1, 0
        for w in weights:
            if load + w <= cap:
                load += w
            else:
                d += 1
                load = w
        if d <= days:
            return cap
        cap += 1


def g_ship(r):
    n = r.randint(1, 9)
    return [[r.randint(1, 12) for _ in range(n)], r.randint(1, n)]


def v_ship(tests):
    for t in tests:
        w, d = t["args"]
        assert 1 <= d <= len(w) <= 5000
        assert all(1 <= x <= 500 for x in w)


CHECKS["capacity-to-ship-packages"] = (b_ship, g_ship, "exact")
VALIDATE["capacity-to-ship-packages"] = v_ship

p = add(
    id="max-consecutive-ones-iii", title="Max Consecutive Ones III", diff="Medium", topic="Sliding Window",
    fn="longestOnes", params=[("nums", "int[]"), ("k", "int")], ret="int", cmp="exact",
    desc="<p>You are given a binary array <code>nums</code> (every element is <code>0</code> or <code>1</code>) and an integer <code>k</code>. You may flip at most <code>k</code> zeros into ones. Return the length of the longest run of consecutive ones you can obtain.</p>",
    constraints=["1 &le; nums.length &le; 10,000", "nums[i] is 0 or 1", "0 &le; k &le; nums.length"],
    hints=["Instead of thinking about flipping, ask: what is the longest subarray that contains at most <code>k</code> zeros?",
           "A window with too many zeros can be repaired by shrinking it from the left; a valid window can be extended on the right.",
           "Expand <code>right</code> one step at a time, counting zeros. While the count exceeds <code>k</code>, move <code>left</code> forward (decrementing the count if the dropped element was a zero). Track the largest window."],
    editorial=["Flipping at most <code>k</code> zeros inside a stretch is possible exactly when that stretch contains at most <code>k</code> zeros. So the answer is the length of the longest subarray with at most <code>k</code> zeros.",
               "Use a sliding window. Add <code>nums[right]</code>, and if it is a zero increase the zero count. If the count passes <code>k</code>, advance <code>left</code> until the count is back to <code>k</code>. After each step, the window <code>[left, right]</code> is valid, so update the best length. Each index enters and leaves the window at most once: O(n) time, O(1) space."],
    time="O(n)", space="O(1)",
    solution='''def longestOnes(nums, k):
    left = zeros = best = 0
    for right, x in enumerate(nums):
        if x == 0:
            zeros += 1
        while zeros > k:
            if nums[left] == 0:
                zeros -= 1
            left += 1
        best = max(best, right - left + 1)
    return best
''',
    tests=[[[1, 1, 1, 0, 0, 0, 1, 1, 1, 1, 0], 2], [[0, 0, 1, 1, 0, 0, 1, 1, 1, 0, 1, 1, 0, 0, 0, 1, 1, 1, 1], 3], [[0], 0],
           [[0], 1], [[1], 0], [[1, 1, 1], 0], [[0, 0, 0, 0], 2], [[0, 0, 0, 0], 4], [[1, 0, 1, 0, 1, 0, 1], 1],
           [[1, 0, 0, 0, 1], 2], [[0, 1, 0, 1, 1, 0], 0]],
)
_r = rnd(206)
p["tests"].append([[_r.randint(0, 1) for _ in range(10000)], 100])
p["tests"].append([[_r.randint(0, 1) for _ in range(10000)], 0])
p["tests"].append([[0] * 10000, 7777])
p["tests"].append([[1 if _r.random() < 0.9 else 0 for _ in range(10000)], 25])
p["tests"].append([[0, 1] * 5000, 10000])


def b_ones(nums, k):
    n = len(nums)
    best = 0
    for i in range(n):
        z = 0
        for j in range(i, n):
            z += 1 - nums[j]
            if z > k:
                break
            best = max(best, j - i + 1)
    return best


def g_ones(r):
    n = r.randint(1, 14)
    return [[r.randint(0, 1) for _ in range(n)], r.randint(0, n)]


def v_ones(tests):
    for t in tests:
        nums, k = t["args"]
        assert 1 <= len(nums) <= 10000 and 0 <= k <= len(nums)
        assert all(x in (0, 1) for x in nums)


CHECKS["max-consecutive-ones-iii"] = (b_ones, g_ones, "exact")
VALIDATE["max-consecutive-ones-iii"] = v_ones

p = add(
    id="non-overlapping-intervals", title="Non-overlapping Intervals", diff="Medium", topic="Intervals",
    fn="eraseOverlapIntervals", params=[("intervals", "int[][]")], ret="int", cmp="exact",
    desc="<p>Each interval is a pair <code>[start, end]</code> with <code>start &lt; end</code>. Two intervals overlap when they share more than a single point, so intervals that merely touch, such as <code>[1, 2]</code> and <code>[2, 3]</code>, do <em>not</em> overlap.</p><p>Return the minimum number of intervals you have to remove so that the remaining intervals are pairwise non-overlapping.</p>",
    constraints=["0 &le; intervals.length &le; 5,000", "intervals[i].length == 2", "-10<sup>9</sup> &le; start &lt; end &le; 10<sup>9</sup>"],
    hints=["Removing the fewest intervals is the same as keeping the largest possible set of mutually compatible intervals.",
           "When choosing which interval to keep first, the one that finishes earliest leaves the most room for the rest.",
           "Sort by end value. Sweep through, keeping an interval whenever its start is at least the end of the last kept interval; otherwise count it as removed."],
    editorial=["This is the classic activity-selection problem. Maximise the number of intervals kept; the answer is <code>n - kept</code>.",
               "Greedy rule: sort by end and always keep the interval that ends first among those compatible with what you already kept. An exchange argument shows this is optimal: any optimal solution can swap its first interval for the earliest-ending one without creating a conflict. Sorting costs O(n log n) and the sweep is O(n); extra space is for the sorted copy."],
    time="O(n log n)", space="O(n)",
    solution='''def eraseOverlapIntervals(intervals):
    kept = 0
    last_end = None
    for s, e in sorted(intervals, key=lambda x: x[1]):
        if last_end is None or s >= last_end:
            kept += 1
            last_end = e
    return len(intervals) - kept
''',
    tests=[[[[1, 2], [2, 3], [3, 4], [1, 3]]], [[[1, 2], [1, 2], [1, 2]]], [[[1, 2], [2, 3]]], [[]], [[[0, 5]]],
           [[[1, 10], [2, 3], [4, 5], [6, 7]]], [[[1, 100], [11, 22], [1, 11], [2, 12]]], [[[-5, -1], [-3, 0], [0, 4]]],
           [[[-1000000000, 1000000000], [-1000000000, 0], [0, 1000000000]]], [[[1, 3], [2, 4], [3, 5], [4, 6], [5, 7]]],
           [[[5, 6], [1, 2], [3, 4]]]],
)
_r = rnd(207)


def _ivs(r, n, lo, hi, maxlen):
    out = []
    for _ in range(n):
        s = r.randint(lo, hi - 1)
        out.append([s, min(hi, s + r.randint(1, maxlen))])
    return out


p["tests"].append([_ivs(_r, 5000, -1000000000, 1000000000, 2000000)])
p["tests"].append([_ivs(_r, 5000, 0, 20000, 30)])
p["tests"].append([_ivs(_r, 5000, 0, 1000, 500)])
p["tests"].append([[[i, i + 1] for i in range(5000)]])
p["tests"].append([[[0, 1000000000]] * 2500 + [[i, i + 1] for i in range(2500)]])


def b_nov(intervals):
    n = len(intervals)
    best = 0
    for mask in range(1 << n):
        chosen = [intervals[i] for i in range(n) if mask >> i & 1]
        if len(chosen) <= best:
            continue
        ok = True
        for a, b in combinations(chosen, 2):
            if max(a[0], b[0]) < min(a[1], b[1]):
                ok = False
                break
        if ok:
            best = len(chosen)
    return n - best


def g_nov(r):
    return [_ivs(r, r.randint(0, 9), 0, 12, 6)]


def v_nov(tests):
    for t in tests:
        iv = t["args"][0]
        assert len(iv) <= 5000
        assert all(len(x) == 2 and -10 ** 9 <= x[0] < x[1] <= 10 ** 9 for x in iv)


CHECKS["non-overlapping-intervals"] = (b_nov, g_nov, "exact")
VALIDATE["non-overlapping-intervals"] = v_nov

p = add(
    id="minimum-number-of-arrows", title="Minimum Number of Arrows to Burst Balloons", diff="Medium", topic="Intervals",
    fn="findMinArrowShots", params=[("points", "int[][]")], ret="int", cmp="exact",
    desc="<p>Balloons are pinned to a wall. Balloon <code>i</code> covers the horizontal range <code>[points[i][0], points[i][1]]</code> (both ends included). An arrow shot straight up from position <code>x</code> bursts every balloon whose range contains <code>x</code>, and the arrow keeps going.</p><p>Return the minimum number of arrows needed to burst all balloons.</p>",
    constraints=["0 &le; points.length &le; 5,000", "points[i].length == 2", "-2<sup>31</sup> &le; points[i][0] &le; points[i][1] &le; 2<sup>31</sup> - 1"],
    hints=["Balloons whose ranges share a common point can be burst by a single arrow.",
           "Sort the balloons by their right end. Shooting at the right end of the first balloon is never worse than shooting anywhere else inside it.",
           "Shoot at the current right end; every following balloon whose left end is &le; that position is already burst. The first balloon whose left end is larger needs a new arrow, placed at its own right end."],
    editorial=["Sort balloons by right end. Place the first arrow at the right end of the first balloon: any arrow that bursts that balloon can be slid right to its end without losing any other balloon that is later in the sorted order, so this position is at least as good as any other.",
               "Walk through the sorted list. A balloon with <code>start &le; arrowPos</code> is already burst. Otherwise fire a new arrow at its right end and continue. Since both ends are inclusive, a balloon that starts exactly at the arrow position is hit. Comparisons only (no sums) keep the logic safe at the 32-bit limits. O(n log n) for sorting, O(1) beyond that."],
    time="O(n log n)", space="O(n)",
    solution='''def findMinArrowShots(points):
    arrows = 0
    pos = None
    for s, e in sorted(points, key=lambda x: x[1]):
        if pos is None or s > pos:
            arrows += 1
            pos = e
    return arrows
''',
    tests=[[[[10, 16], [2, 8], [1, 6], [7, 12]]], [[[1, 2], [3, 4], [5, 6], [7, 8]]], [[[1, 2], [2, 3], [3, 4], [4, 5]]], [[]],
           [[[5, 5]]], [[[1, 5], [1, 5], [1, 5]]], [[[INT_MIN, INT_MAX], [0, 0]]], [[[INT_MIN, INT_MIN], [INT_MAX, INT_MAX]]],
           [[[-6, -3], [-4, 1], [0, 2], [2, 9]]], [[[1, 100], [2, 3], [50, 60], [99, 100]]], [[[3, 9], [7, 12], [3, 8], [6, 8], [9, 12], [2, 9], [0, 9], [3, 9], [0, 6], [2, 8]]]],
)
_r = rnd(208)


def _balloons(r, n, lo, hi, maxlen):
    out = []
    for _ in range(n):
        s = r.randint(lo, hi)
        out.append([s, min(hi, s + r.randint(0, maxlen))])
    return out


p["tests"].append([_balloons(_r, 5000, INT_MIN, INT_MAX, 100000000)])
p["tests"].append([_balloons(_r, 5000, 0, 10000, 20)])
p["tests"].append([_balloons(_r, 5000, -50000, 50000, 5000)])
p["tests"].append([[[i, i] for i in range(5000)]])
p["tests"].append([[[i, i + 1] for i in range(5000)]])


def b_arr(points):
    if not points:
        return 0
    cand = sorted({v for pt in points for v in pt})
    for k in range(1, len(points) + 1):
        for xs in combinations(cand, k):
            if all(any(a <= x <= b for x in xs) for a, b in points):
                return k


def g_arr(r):
    return [_balloons(r, r.randint(0, 7), 0, 10, 5)]


def v_arr(tests):
    for t in tests:
        pts = t["args"][0]
        assert len(pts) <= 5000
        assert all(len(x) == 2 and INT_MIN <= x[0] <= x[1] <= INT_MAX for x in pts)


CHECKS["minimum-number-of-arrows"] = (b_arr, g_arr, "exact")
VALIDATE["minimum-number-of-arrows"] = v_arr

p = add(
    id="car-fleet", title="Car Fleet", diff="Medium", topic="Stack",
    fn="carFleet", params=[("target", "int"), ("position", "int[]"), ("speed", "int[]")], ret="int", cmp="exact",
    desc="<p>Several cars drive along a one-lane road towards a destination at mile <code>target</code>. Car <code>i</code> starts at mile <code>position[i]</code> and moves at a constant <code>speed[i]</code> miles per hour. All starting positions are distinct and lie before the destination.</p><p>A car can never pass the car in front of it. If it catches up, it slows down and from then on travels at the speed of that car, bumper to bumper; together they form a <em>fleet</em>. A single car is also a fleet, and a car that catches up exactly at the destination still joins the fleet that arrives there.</p><p>Return the number of fleets that arrive at the destination.</p>",
    constraints=["1 &le; position.length == speed.length &le; 1,000", "1 &le; target &le; 10<sup>6</sup>", "0 &le; position[i] &lt; target, and all positions are distinct", "1 &le; speed[i] &le; 10<sup>6</sup>"],
    hints=["Process the cars from the one closest to the destination backwards. A car's fate depends only on the cars in front of it.",
           "For each car compute the time it would need if the road were empty: <code>(target - position) / speed</code>. A car with a time not larger than the fleet ahead of it will merge into that fleet.",
           "Go in descending order of position and keep the arrival time of the fleet in front (a stack, or just its top). A car whose time is strictly larger starts a new fleet. Compare fractions by cross-multiplying to avoid rounding."],
    editorial=["Sort cars by starting position, nearest to the destination first. The first car is always the head of a fleet. For each next car, compute its free-road arrival time <code>t = (target - p) / s</code>. If <code>t</code> is not larger than the arrival time of the fleet immediately ahead, it catches up (or ties exactly at the finish) and joins it; its effective time becomes the fleet's time. If <code>t</code> is strictly larger, it will never catch that fleet and becomes the head of a new one.",
               "Only the time of the closest fleet ahead matters, which is the top of a monotonic stack of fleet times (strictly increasing from the front car backwards). To stay exact, compare <code>(target - p1) / s1 &gt; (target - p2) / s2</code> as <code>(target - p1) * s2 &gt; (target - p2) * s1</code>; the products are at most 10<sup>12</sup>, which needs 64-bit arithmetic in some languages. Sorting dominates: O(n log n) time, O(n) space."],
    time="O(n log n)", space="O(n)",
    solution='''def carFleet(target, position, speed):
    cars = sorted(zip(position, speed), reverse=True)
    fleets = 0
    lead_dist = lead_speed = None
    for p, s in cars:
        d = target - p
        # strictly later than the fleet ahead: d / s > lead_dist / lead_speed
        if lead_dist is None or d * lead_speed > lead_dist * s:
            fleets += 1
            lead_dist, lead_speed = d, s
    return fleets
''',
    tests=[[12, [10, 8, 0, 5, 3], [2, 4, 1, 1, 3]], [10, [3], [3]], [100, [0, 2, 4], [4, 2, 1]], [10, [6, 8], [3, 2]],
           [10, [0, 4, 2], [2, 1, 3]], [10, [0, 5], [10, 5]], [1, [0], [1]], [20, [0, 5, 10, 15], [1, 1, 1, 1]],
           [20, [15, 10, 5, 0], [1, 2, 3, 4]], [1000000, [0, 999999], [1000000, 1]], [100, [90, 80, 70, 60], [1, 2, 4, 8]]],
)
_r = rnd(209)
for _n, _tg, _mx in ((1000, 1000000, 1000000), (1000, 1000000, 10), (1000, 5000, 100), (800, 1000000, 1000000)):
    _pos = _r.sample(range(0, _tg), _n)
    p["tests"].append([_tg, _pos, [_r.randint(1, _mx) for _ in _pos]])
p["tests"].append([1000000, list(range(1000)), [1] * 1000])
p["tests"].append([1000000, list(range(999000, 1000000)), list(range(1, 1001))])


def b_cf(target, position, speed):
    n = len(position)
    times = [Fraction(target - position[i], speed[i]) for i in range(n)]
    cnt = 0
    for i in range(n):
        if all(times[j] < times[i] for j in range(n) if position[j] > position[i]):
            cnt += 1
    return cnt


def g_cf(r):
    target = r.randint(1, 15)
    n = r.randint(1, min(target, 8))
    pos = r.sample(range(0, target), n)
    return [target, pos, [r.randint(1, 5) for _ in range(n)]]


def v_cf(tests):
    for t in tests:
        target, pos, spd = t["args"]
        assert 1 <= len(pos) == len(spd) <= 1000
        assert 1 <= target <= 10 ** 6
        assert len(set(pos)) == len(pos) and all(0 <= x < target for x in pos)
        assert all(1 <= s <= 10 ** 6 for s in spd)


CHECKS["car-fleet"] = (b_cf, g_cf, "exact")
VALIDATE["car-fleet"] = v_cf


# ---------------------------------------------------------------- HARD

p = add(
    id="split-array-largest-sum", title="Split Array Largest Sum", diff="Hard", topic="Binary Search",
    fn="splitArray", params=[("nums", "int[]"), ("k", "int")], ret="int", cmp="exact",
    desc="<p>Split the non-negative integer array <code>nums</code> into exactly <code>k</code> non-empty contiguous pieces. The <em>cost</em> of a split is the largest piece sum. Return the smallest cost that any split can achieve.</p>",
    constraints=["1 &le; k &le; nums.length &le; 1,000", "0 &le; nums[i] &le; 10<sup>6</sup>"],
    hints=["A dynamic programming over (prefix, pieces) works but is cubic in the straightforward form. Think about whether the answer itself can be searched for.",
           "Fix a limit <code>L</code> and ask: can the array be cut into at most <code>k</code> pieces, each with sum &le; <code>L</code>? A greedy sweep that extends each piece as far as possible answers this.",
           "The answer is the smallest feasible <code>L</code>. Feasibility is monotonic, so binary search <code>L</code> between <code>max(nums)</code> and <code>sum(nums)</code>. Note that using fewer pieces can always be turned into exactly <code>k</code> by splitting pieces further, which never raises the maximum."],
    editorial=["Let <code>feasible(L)</code> be true when the array can be divided into at most <code>k</code> contiguous pieces with every sum &le; <code>L</code>. The greedy check scans left to right, closing a piece when adding the next element would exceed <code>L</code>; it uses the minimum possible number of pieces for that limit.",
               "If a limit works, a bigger one works too, so binary search on the answer between <code>max(nums)</code> (every element must fit in some piece) and <code>sum(nums)</code> (one piece). Having fewer than <code>k</code> pieces is fine: because <code>k &le; n</code>, any piece with more than one element can be cut further without increasing the maximum, until exactly <code>k</code> pieces exist. Complexity is O(n log(sum)) time and O(1) space; a DP would cost O(k n<sup>2</sup>). Total sums stay below 10<sup>9</sup>, inside 32-bit range."],
    time="O(n log S)", space="O(1)",
    solution='''def splitArray(nums, k):
    def pieces(limit):
        count, cur = 1, 0
        for x in nums:
            if cur + x > limit:
                count += 1
                cur = 0
            cur += x
        return count

    lo, hi = max(nums), sum(nums)
    while lo < hi:
        mid = (lo + hi) // 2
        if pieces(mid) <= k:
            hi = mid
        else:
            lo = mid + 1
    return lo
''',
    tests=[[[7, 2, 5, 10, 8], 2], [[1, 2, 3, 4, 5], 2], [[1, 4, 4], 3], [[5], 1], [[0, 0, 0], 2], [[10, 5, 13, 4, 8, 4, 5, 11, 14, 9, 16, 10, 20, 8], 8],
           [[1, 1, 1, 1, 1, 1], 6], [[1, 1, 1, 1, 1, 1], 1], [[100, 1, 1, 1, 100], 3], [[0, 5, 0, 5, 0], 2],
           [[1000000, 1000000, 1000000], 2]],
)
_r = rnd(210)
_a = [_r.randint(0, 1000000) for _ in range(1000)]
p["tests"].append([_a, 1])
p["tests"].append([_a, 1000])
p["tests"].append([_a, 2])
p["tests"].append([_a, 17])
p["tests"].append([_a, 333])
p["tests"].append([[1000000] * 1000, 7])
p["tests"].append([[_r.randint(0, 5) for _ in range(1000)], 40])


def b_split(nums, k):
    n = len(nums)
    pre = [0]
    for x in nums:
        pre.append(pre[-1] + x)
    INF = float("inf")
    dp = [[INF] * (n + 1) for _ in range(k + 1)]
    dp[0][0] = 0
    for j in range(1, k + 1):
        for i in range(j, n + 1):
            for m in range(j - 1, i):
                v = max(dp[j - 1][m], pre[i] - pre[m])
                if v < dp[j][i]:
                    dp[j][i] = v
    return dp[k][n]


def g_split(r):
    n = r.randint(1, 9)
    return [[r.randint(0, 15) for _ in range(n)], r.randint(1, n)]


def v_split(tests):
    for t in tests:
        nums, k = t["args"]
        assert 1 <= k <= len(nums) <= 1000
        assert all(0 <= x <= 10 ** 6 for x in nums)


CHECKS["split-array-largest-sum"] = (b_split, g_split, "exact")
VALIDATE["split-array-largest-sum"] = v_split

p = add(
    id="shortest-subarray-with-sum-at-least-k", title="Shortest Subarray with Sum at Least K", diff="Hard", topic="Sliding Window",
    fn="shortestSubarray", params=[("nums", "int[]"), ("k", "int")], ret="int", cmp="exact",
    desc="<p>Given an integer array <code>nums</code> that may contain negative numbers, and a positive integer <code>k</code>, return the length of the shortest non-empty contiguous subarray whose sum is at least <code>k</code>. If no such subarray exists, return <code>-1</code>.</p>",
    constraints=["1 &le; nums.length &le; 5,000", "-10<sup>4</sup> &le; nums[i] &le; 10<sup>4</sup>", "1 &le; k &le; 10<sup>9</sup>"],
    hints=["The classic shrinking window fails here because negative values mean that adding an element can lower the sum. Use prefix sums instead: you want the closest pair <code>i &lt; j</code> with <code>pre[j] - pre[i] &ge; k</code>.",
           "For a fixed <code>j</code>, a larger and closer <code>i</code> is always better. If <code>pre[i1] &ge; pre[i2]</code> with <code>i1 &gt; i2</code>, then index <code>i2</code> is useless.",
           "Maintain a deque of indices with increasing prefix sums. At each <code>j</code>, pop from the front while <code>pre[j] - pre[front] &ge; k</code> (recording lengths), then pop from the back while <code>pre[back] &ge; pre[j]</code>, then push <code>j</code>."],
    editorial=["Let <code>pre[0] = 0</code> and <code>pre[j] = nums[0] + ... + nums[j-1]</code>. We want the minimum <code>j - i</code> with <code>i &lt; j</code> and <code>pre[j] - pre[i] &ge; k</code>.",
               "Keep a deque of candidate start indices whose prefix sums are strictly increasing. When we reach <code>j</code>: (1) while the front index satisfies the condition, record <code>j - front</code> and pop it, since any later <code>j</code> would only give a longer length for that start; (2) while the back index has a prefix sum that is not smaller than <code>pre[j]</code>, pop it, since <code>j</code> is a later and lower start that dominates it; (3) push <code>j</code>. Each index is pushed and popped once, so the algorithm runs in O(n) time and O(n) space."],
    time="O(n)", space="O(n)",
    solution='''def shortestSubarray(nums, k):
    from collections import deque
    n = len(nums)
    pre = [0] * (n + 1)
    for i, x in enumerate(nums):
        pre[i + 1] = pre[i] + x
    best = n + 1
    dq = deque()
    for j in range(n + 1):
        while dq and pre[j] - pre[dq[0]] >= k:
            best = min(best, j - dq.popleft())
        while dq and pre[dq[-1]] >= pre[j]:
            dq.pop()
        dq.append(j)
    return best if best <= n else -1
''',
    tests=[[[1], 1], [[1, 2], 4], [[2, -1, 2], 3], [[84, -37, 32, 40, 95], 167], [[-1, -2, -3], 1], [[5], 6], [[1, 1, 1, 1], 3],
           [[10, -5, 10, -5, 10], 15], [[-5, 20, -5, 20], 30], [[0, 0, 0, 7], 7], [[3, -2, -2, 5, -10, 8], 6],
           [[10000] * 10, 100000]],
)
_r = rnd(211)
p["tests"].append([[_r.randint(-10000, 10000) for _ in range(5000)], 1000000])
p["tests"].append([[_r.randint(-10000, 10000) for _ in range(5000)], 50])
p["tests"].append([[_r.randint(-10000, 10000) for _ in range(5000)], 1000000000])
p["tests"].append([[_r.randint(-100, 10000) for _ in range(5000)], 30000000])
p["tests"].append([[_r.randint(-10000, 100) for _ in range(5000)], 10000])
p["tests"].append([[10000, -10000] * 2500, 10000])
p["tests"].append([[-1] * 2500 + [10000] * 2500, 20000])


def b_ssk(nums, k):
    n = len(nums)
    best = -1
    for i in range(n):
        s = 0
        for j in range(i, n):
            s += nums[j]
            if s >= k:
                if best == -1 or j - i + 1 < best:
                    best = j - i + 1
                break
    return best


def g_ssk(r):
    n = r.randint(1, 12)
    return [[r.randint(-6, 8) for _ in range(n)], r.randint(1, 20)]


def v_ssk(tests):
    for t in tests:
        nums, k = t["args"]
        assert 1 <= len(nums) <= 5000 and 1 <= k <= 10 ** 9
        assert all(-10 ** 4 <= x <= 10 ** 4 for x in nums)


CHECKS["shortest-subarray-with-sum-at-least-k"] = (b_ssk, g_ssk, "exact")
VALIDATE["shortest-subarray-with-sum-at-least-k"] = v_ssk
