"""Problems: array manipulation, prefix sums / difference arrays and sweep line. See data/lib.py for the registry."""
import bisect
from itertools import permutations

from lib import add, rnd, CHECKS, VALIDATE, gen_arr  # noqa: F401

INT_MIN, INT_MAX = -(2 ** 31), 2 ** 31 - 1


# ---------------------------------------------------------------- EASY

p = add(
    id="rotate-array-by-k-steps", title="Rotate Array by K Steps", diff="Easy", topic="Arrays & Hashing",
    fn="rotateArray", params=[("nums", "int[]"), ("k", "int")], ret="int[]", cmp="exact",
    desc="<p>Rotate the array <code>nums</code> to the right by <code>k</code> steps and return the rotated array. One step moves the last element to the front and shifts everything else one place to the right.</p><p><code>k</code> can be far larger than the length of the array. Try to do the rotation with O(1) extra space besides the returned array (reversals make this possible).</p><pre>nums = [1, 2, 3, 4, 5, 6, 7], k = 3\nresult = [5, 6, 7, 1, 2, 3, 4]</pre>",
    constraints=["1 &le; nums.length &le; 10,000", "-2<sup>31</sup> &le; nums[i] &le; 2<sup>31</sup> - 1", "0 &le; k &le; 2<sup>31</sup> - 1"],
    hints=["Rotating by <code>n</code> steps gives back the same array. So only <code>k mod n</code> matters.",
           "Look at the target: the last <code>k</code> elements move to the front, in their original order, followed by the first <code>n - k</code> elements.",
           "Reverse the whole array, then reverse the first <code>k</code> elements, then reverse the remaining <code>n - k</code> elements."],
    editorial=["Reduce <code>k</code> to <code>k mod n</code> first, since a full turn changes nothing. After that, the rotated array is the last <code>k</code> elements followed by the first <code>n - k</code> elements.",
               "Slicing builds this directly in O(n) extra space. To avoid the extra space, use three reversals: reversing the whole array puts the last <code>k</code> elements at the front but backwards, and the first <code>n - k</code> elements at the back but backwards. Reversing each of the two blocks again restores their order. Every element is swapped a constant number of times, so the time is O(n).",
               "Simulating one step at a time costs O(n * k), which is far too slow once <code>k</code> reaches the billions."],
    time="O(n)", space="O(1)",
    solution='''def rotateArray(nums, k):
    a = list(nums)
    n = len(a)
    k %= n

    def rev(i, j):
        while i < j:
            a[i], a[j] = a[j], a[i]
            i += 1
            j -= 1

    rev(0, n - 1)
    rev(0, k - 1)
    rev(k, n - 1)
    return a
''',
    tests=[[[1, 2, 3, 4, 5, 6, 7], 3], [[-1, -100, 3, 99], 2], [[1, 2], 1], [[5], 0], [[5], 1000000000],
           [[1, 2, 3], 3], [[1, 2, 3], 4], [[1, 2, 3, 4, 5], 0], [[INT_MIN, 0, INT_MAX, 7], INT_MAX],
           [[4, 4, 4, 1], 2], [[9, 8, 7, 6, 5, 4, 3, 2, 1, 0], 9]],
)
_r = rnd(8301)
p["tests"].append([[_r.randint(INT_MIN, INT_MAX) for _ in range(10000)], 7654321])
p["tests"].append([[_r.randint(-50, 50) for _ in range(9999)], 9999 * 3 + 1])
p["tests"].append([list(range(10000)), 9999])


def b_rotate(nums, k):
    a = list(nums)
    for _ in range(k):
        a.insert(0, a.pop())
    return a


def g_rotate(r):
    return [gen_arr(r, -5, 5, 1, 9), r.randint(0, 25)]


def v_rotate(tests):
    for t in tests:
        nums, k = t["args"]
        assert 1 <= len(nums) <= 10000 and 0 <= k <= INT_MAX
        assert sorted(nums) == sorted(t["expected"])


CHECKS["rotate-array-by-k-steps"] = (b_rotate, g_rotate, "exact")
VALIDATE["rotate-array-by-k-steps"] = v_rotate

p = add(
    id="merge-two-sorted-int-arrays", title="Merge Two Sorted Arrays", diff="Easy", topic="Arrays & Hashing",
    fn="mergeSortedArrays", params=[("a", "int[]"), ("b", "int[]")], ret="int[]", cmp="exact",
    desc="<p>Both <code>a</code> and <code>b</code> are sorted in non-decreasing order. Return a single array that contains every element of both arrays (duplicates included), also sorted in non-decreasing order.</p><p>Do it in O(n + m) time by using the fact that the inputs are already sorted, rather than sorting the combined array from scratch.</p><pre>a = [1, 4, 4, 9], b = [2, 4, 10]\nresult = [1, 2, 4, 4, 4, 9, 10]</pre>",
    constraints=["0 &le; a.length, b.length &le; 10,000", "-2<sup>31</sup> &le; a[i], b[i] &le; 2<sup>31</sup> - 1", "a and b are each sorted in non-decreasing order"],
    hints=["The smallest element overall must be the first element of <code>a</code> or the first element of <code>b</code>.",
           "Keep one pointer in each array and repeatedly take the smaller of the two current elements.",
           "When one array runs out, append everything that remains in the other one. Take from <code>a</code> on ties; either choice gives the same values."],
    editorial=["This is the merge step of merge sort. Maintain indices <code>i</code> and <code>j</code> into the two arrays. While both are in range, compare <code>a[i]</code> and <code>b[j]</code>, append the smaller one to the result, and advance that pointer. When one array is exhausted, copy over the rest of the other.",
               "Each element is appended exactly once, so the running time is O(n + m). The result needs O(n + m) space because it has to be returned. Concatenating and calling a sort also works but costs O(n log n) and ignores the sortedness."],
    time="O(n + m)", space="O(n + m)",
    solution='''def mergeSortedArrays(a, b):
    out = []
    i = j = 0
    while i < len(a) and j < len(b):
        if a[i] <= b[j]:
            out.append(a[i])
            i += 1
        else:
            out.append(b[j])
            j += 1
    out.extend(a[i:])
    out.extend(b[j:])
    return out
''',
    tests=[[[1, 4, 4, 9], [2, 4, 10]], [[], []], [[], [3, 5]], [[-2, -1], []], [[1, 2, 3], [4, 5, 6]],
           [[4, 5, 6], [1, 2, 3]], [[7], [7]], [[1, 1, 1], [1, 1]], [[INT_MIN, 0, INT_MAX], [INT_MIN, INT_MAX]],
           [[-5, -3, 0], [-4, -4, 2]]],
)
_r = rnd(8302)
p["tests"].append([sorted(_r.randint(INT_MIN, INT_MAX) for _ in range(10000)), sorted(_r.randint(INT_MIN, INT_MAX) for _ in range(10000))])
p["tests"].append([sorted(_r.randint(-20, 20) for _ in range(10000)), sorted(_r.randint(-20, 20) for _ in range(7000))])
p["tests"].append([list(range(0, 10000)), list(range(5000, 5005))])


def b_merge(a, b):
    a, b = list(a), list(b)
    out = []
    while a or b:
        if not b or (a and a[0] <= b[0]):
            out.append(a.pop(0))
        else:
            out.append(b.pop(0))
    return out


def g_merge(r):
    return [sorted(gen_arr(r, -6, 6, 0, 8)), sorted(gen_arr(r, -6, 6, 0, 8))]


def v_merge(tests):
    for t in tests:
        a, b = t["args"]
        assert len(a) <= 10000 and len(b) <= 10000
        assert a == sorted(a) and b == sorted(b)


CHECKS["merge-two-sorted-int-arrays"] = (b_merge, g_merge, "exact")
VALIDATE["merge-two-sorted-int-arrays"] = v_merge

p = add(
    id="range-sum-query-batch", title="Range Sum Queries", diff="Easy", topic="Prefix Sums",
    fn="rangeSums", params=[("nums", "int[]"), ("queries", "int[][]")], ret="int[]", cmp="exact",
    desc="<p>You are given an integer array <code>nums</code> and a list of queries. Each query is a pair <code>[l, r]</code> asking for the sum of <code>nums[l] + nums[l+1] + ... + nums[r]</code> (both ends included, 0-indexed).</p><p>Return an array containing the answer to every query, in the same order as the queries. Many queries can be asked about the same array, so recomputing each sum from scratch is too slow.</p><pre>nums = [3, -1, 4, 1, 5], queries = [[0, 2], [1, 1], [2, 4]]\nresult = [6, -1, 10]</pre>",
    constraints=["1 &le; nums.length &le; 10,000", "-10,000 &le; nums[i] &le; 10,000", "0 &le; queries.length &le; 10,000", "0 &le; l &le; r &lt; nums.length for every query"],
    hints=["Summing each range directly costs O(n) per query, so O(n * q) overall. Can you share work between queries?",
           "Build an array <code>pre</code> where <code>pre[i]</code> is the sum of the first <code>i</code> elements, with <code>pre[0] = 0</code>.",
           "The sum of <code>nums[l..r]</code> equals <code>pre[r + 1] - pre[l]</code>."],
    editorial=["Precompute prefix sums once: <code>pre[0] = 0</code> and <code>pre[i + 1] = pre[i] + nums[i]</code>. The sum of the elements from <code>l</code> to <code>r</code> inclusive is everything up to <code>r</code> minus everything before <code>l</code>, that is <code>pre[r + 1] - pre[l]</code>.",
               "Building the table takes O(n) and each query is answered in O(1), so the total is O(n + q). The leading zero in <code>pre</code> avoids a special case when <code>l = 0</code>. With the given bounds every sum has absolute value at most 10<sup>8</sup>, comfortably inside 32 bits."],
    time="O(n + q)", space="O(n)",
    solution='''def rangeSums(nums, queries):
    pre = [0]
    for x in nums:
        pre.append(pre[-1] + x)
    return [pre[r + 1] - pre[l] for l, r in queries]
''',
    tests=[[[3, -1, 4, 1, 5], [[0, 2], [1, 1], [2, 4]]], [[7], [[0, 0]]], [[7], []], [[1, 2, 3, 4], [[0, 3], [0, 0], [3, 3]]],
           [[-5, -5, -5], [[0, 2], [1, 2]]], [[10000, 10000, 10000], [[0, 2]]], [[-10000, -10000], [[0, 1], [1, 1]]],
           [[0, 0, 0, 0], [[1, 2], [0, 3]]], [[2, -2, 2, -2, 2], [[0, 4], [1, 3], [0, 1]]]],
)
_r = rnd(8303)
_a = [_r.randint(-10000, 10000) for _ in range(10000)]
_q = []
for _ in range(5000):
    _l = _r.randint(0, 9999)
    _q.append([_l, _r.randint(_l, 9999)])
p["tests"].append([_a, _q])
p["tests"].append([[10000] * 10000, [[0, 9999]] * 20 + [[5, 9000]]])
p["tests"].append([[-10000] * 10000, [[0, 9999], [9999, 9999], [0, 0]]])
_a = [_r.randint(-3, 3) for _ in range(9000)]
p["tests"].append([_a, [[i, i] for i in range(0, 9000, 2)]])


def b_rangesums(nums, queries):
    return [sum(nums[l:r + 1]) for l, r in queries]


def g_rangesums(r):
    nums = gen_arr(r, -9, 9, 1, 10)
    q = []
    for _ in range(r.randint(0, 6)):
        l = r.randrange(len(nums))
        q.append([l, r.randint(l, len(nums) - 1)])
    return [nums, q]


def v_rangesums(tests):
    for t in tests:
        nums, queries = t["args"]
        assert 1 <= len(nums) <= 10000 and len(queries) <= 10000
        assert all(-10000 <= x <= 10000 for x in nums)
        assert all(0 <= l <= r < len(nums) for l, r in queries)


CHECKS["range-sum-query-batch"] = (b_rangesums, g_rangesums, "exact")
VALIDATE["range-sum-query-batch"] = v_rangesums


# ---------------------------------------------------------------- MEDIUM

p = add(
    id="next-permutation-array", title="Next Permutation", diff="Medium", topic="Arrays & Hashing",
    fn="nextPermutation", params=[("nums", "int[]")], ret="int[]", cmp="exact",
    desc="<p>Consider all distinct orderings of the numbers in <code>nums</code>, listed in increasing lexicographic order (compare the first elements, then the second, and so on). Return the ordering that comes right after <code>nums</code> in that list.</p><p>If <code>nums</code> is already the last (largest) ordering, return the first (smallest) one, which is the elements in non-decreasing order. The array may contain duplicates, and a solution needs only O(1) extra space besides the result.</p><pre>[1, 2, 3] -> [1, 3, 2]\n[3, 2, 1] -> [1, 2, 3]\n[1, 1, 5] -> [1, 5, 1]</pre>",
    constraints=["1 &le; nums.length &le; 10,000", "0 &le; nums[i] &le; 100", "Duplicate values are allowed"],
    hints=["Look at the array from the right. The longest non-increasing suffix is already the largest possible arrangement of its elements, so nothing inside it can be made bigger.",
           "Find the rightmost index <code>i</code> with <code>nums[i] &lt; nums[i + 1]</code>. Element <code>i</code> must grow, and everything to its right should then be as small as possible.",
           "Swap <code>nums[i]</code> with the rightmost element greater than it (it lies in the suffix), then reverse the suffix after position <code>i</code> so it becomes ascending. If no such <code>i</code> exists, just reverse the whole array."],
    editorial=["Scan from the right for the first position <code>i</code> where <code>nums[i] &lt; nums[i + 1]</code>. Everything after <code>i</code> is non-increasing, which is the biggest arrangement of those values, so to get the next permutation the prefix up to <code>i</code> must change and <code>nums[i]</code> must be replaced by the smallest larger value available in the suffix.",
               "That value is the rightmost suffix element strictly greater than <code>nums[i]</code> (rightmost because the suffix is non-increasing, so it is the smallest of the larger ones, and picking the rightmost keeps duplicates consistent). Swap the two. The suffix is still non-increasing, so reversing it gives the smallest arrangement of the suffix, which is exactly what the next permutation needs.",
               "If no <code>i</code> exists, the whole array is non-increasing, the last permutation, and reversing it wraps around to the first. Time is O(n) with a constant number of passes."],
    time="O(n)", space="O(1)",
    solution='''def nextPermutation(nums):
    a = list(nums)
    n = len(a)
    i = n - 2
    while i >= 0 and a[i] >= a[i + 1]:
        i -= 1
    if i >= 0:
        j = n - 1
        while a[j] <= a[i]:
            j -= 1
        a[i], a[j] = a[j], a[i]
    lo, hi = i + 1, n - 1
    while lo < hi:
        a[lo], a[hi] = a[hi], a[lo]
        lo += 1
        hi -= 1
    return a
''',
    tests=[[[1, 2, 3]], [[3, 2, 1]], [[1, 1, 5]], [[1]], [[2, 2, 2]], [[1, 3, 2]], [[2, 3, 1]], [[1, 5, 1]],
           [[0, 100, 100, 0]], [[4, 2, 0, 2, 3, 2, 0]], [[1, 2]], [[2, 1]], [[5, 4, 4, 3, 1, 1, 0]]],
)
_r = rnd(8304)
p["tests"].append([sorted((_r.randint(0, 100) for _ in range(10000)), reverse=True)])
p["tests"].append([sorted(_r.randint(0, 100) for _ in range(10000))])
p["tests"].append([[_r.randint(0, 100) for _ in range(10000)]])
_a = list(range(100, 0, -1)) * 99
p["tests"].append([_a[:-3] + [1, 2, 3]])
p["tests"].append([[0, 1] * 5000])


def b_nextperm(nums):
    perms = sorted(set(permutations(nums)))
    idx = perms.index(tuple(nums))
    return list(perms[idx + 1] if idx + 1 < len(perms) else perms[0])


def g_nextperm(r):
    return [gen_arr(r, 0, 3, 1, 7)]


def v_nextperm(tests):
    for t in tests:
        nums = t["args"][0]
        assert 1 <= len(nums) <= 10000 and all(0 <= x <= 100 for x in nums)
        assert sorted(nums) == sorted(t["expected"])


CHECKS["next-permutation-array"] = (b_nextperm, g_nextperm, "exact")
VALIDATE["next-permutation-array"] = v_nextperm

p = add(
    id="sort-three-colors-in-place", title="Sort Colors (Dutch Flag)", diff="Medium", topic="Arrays & Hashing",
    fn="sortColors", params=[("nums", "int[]")], ret="int[]", cmp="exact",
    desc="<p>Every element of <code>nums</code> is <code>0</code>, <code>1</code> or <code>2</code> (think of red, white and blue pieces of cloth). Rearrange the array so that all the <code>0</code>s come first, then all the <code>1</code>s, then all the <code>2</code>s, and return the rearranged array.</p><p>Use a library sort only as a last resort: the point of this exercise is a single pass over the array with O(1) extra space, without counting the values first.</p><pre>nums = [2, 0, 2, 1, 1, 0]\nresult = [0, 0, 1, 1, 2, 2]</pre>",
    constraints=["1 &le; nums.length &le; 10,000", "nums[i] is 0, 1 or 2"],
    hints=["Counting how many of each value there are and rewriting the array works in two passes. Can you do it in one?",
           "Maintain three regions: a block of 0s at the front, a block of 2s at the back, and an unexamined middle. A 1 can simply stay where it is.",
           "Use pointers <code>lo</code>, <code>i</code>, <code>hi</code>. If <code>nums[i]</code> is 0, swap it to <code>lo</code> and advance both; if it is 2, swap it to <code>hi</code> and move only <code>hi</code> down (the swapped-in value is still unknown); if it is 1, just advance <code>i</code>."],
    editorial=["This is the Dutch national flag partition. Keep the invariant that <code>nums[0:lo]</code> are all 0, <code>nums[lo:i]</code> are all 1, <code>nums[hi+1:]</code> are all 2, and <code>nums[i:hi+1]</code> are not yet classified.",
               "Look at <code>nums[i]</code>. A 0 is swapped with <code>nums[lo]</code> (which is a 1 or is the same cell) and both <code>lo</code> and <code>i</code> move forward. A 2 is swapped with <code>nums[hi]</code> and <code>hi</code> moves back, but <code>i</code> stays put because the element that arrived from the right has not been inspected yet. A 1 is already in the correct region, so <code>i</code> advances. The loop ends when <code>i</code> passes <code>hi</code>.",
               "Every step shrinks the unclassified region by one cell, so the time is O(n) in a single pass with O(1) extra space."],
    time="O(n)", space="O(1)",
    solution='''def sortColors(nums):
    a = list(nums)
    lo, i, hi = 0, 0, len(a) - 1
    while i <= hi:
        if a[i] == 0:
            a[lo], a[i] = a[i], a[lo]
            lo += 1
            i += 1
        elif a[i] == 2:
            a[hi], a[i] = a[i], a[hi]
            hi -= 1
        else:
            i += 1
    return a
''',
    tests=[[[2, 0, 2, 1, 1, 0]], [[2, 0, 1]], [[0]], [[1]], [[2]], [[2, 2, 2]], [[0, 0, 1, 1, 2, 2]], [[2, 2, 1, 1, 0, 0]],
           [[1, 2, 0]], [[1, 1, 1, 0]], [[2, 1]], [[1, 0, 1, 0, 2, 2, 0, 1]]],
)
_r = rnd(8305)
p["tests"].append([[_r.choice((0, 1, 2)) for _ in range(10000)]])
p["tests"].append([[2] * 5000 + [0] * 5000])
p["tests"].append([[1, 2] * 5000])
p["tests"].append([[_r.choice((0, 2)) for _ in range(9999)]])


def b_colors(nums):
    return [0] * nums.count(0) + [1] * nums.count(1) + [2] * nums.count(2)


def g_colors(r):
    return [[r.randint(0, 2) for _ in range(r.randint(1, 12))]]


def v_colors(tests):
    for t in tests:
        nums = t["args"][0]
        assert 1 <= len(nums) <= 10000 and all(x in (0, 1, 2) for x in nums)


CHECKS["sort-three-colors-in-place"] = (b_colors, g_colors, "exact")
VALIDATE["sort-three-colors-in-place"] = v_colors

p = add(
    id="flight-bookings-seat-totals", title="Flight Bookings Seat Totals", diff="Medium", topic="Prefix Sums",
    fn="flightBookings", params=[("n", "int"), ("bookings", "int[][]")], ret="int[]", cmp="exact",
    desc="<p>An airline operates <code>n</code> flights numbered <code>1</code> to <code>n</code>. Each booking is a triple <code>[first, last, seats]</code>, meaning <code>seats</code> seats were reserved on <em>every</em> flight from number <code>first</code> to number <code>last</code> inclusive.</p><p>Return an array of length <code>n</code> whose element at index <code>i</code> is the total number of seats reserved on flight <code>i + 1</code>.</p><pre>n = 5, bookings = [[1, 2, 10], [2, 3, 20], [2, 5, 25]]\nresult = [10, 55, 45, 25, 25]</pre>",
    constraints=["1 &le; n &le; 10,000", "0 &le; bookings.length &le; 10,000", "1 &le; first &le; last &le; n", "1 &le; seats &le; 10,000"],
    hints=["Adding <code>seats</code> to every flight of a booking costs O(n) per booking. With 10,000 bookings that is too slow in the worst case.",
           "Record only the changes: at flight <code>first</code> the running total goes up by <code>seats</code>, and just after <code>last</code> it goes back down by <code>seats</code>.",
           "Store <code>diff[first] += seats</code> and <code>diff[last + 1] -= seats</code> (size n + 2), then take the running sum of <code>diff</code> to recover every flight's total."],
    editorial=["This is the difference array technique. Instead of updating a whole range, mark where the contribution of a booking starts and where it stops: add <code>seats</code> at index <code>first</code> and subtract <code>seats</code> at index <code>last + 1</code>.",
               "A single left-to-right running sum over the difference array then gives, at each flight, the sum of all bookings that are currently active. Processing the bookings costs O(1) each and the final sweep costs O(n), for O(n + m) time overall and O(n) space.",
               "The totals never exceed 10,000 bookings times 10,000 seats, that is 10<sup>8</sup>, so 32-bit integers suffice."],
    time="O(n + m)", space="O(n)",
    solution='''def flightBookings(n, bookings):
    diff = [0] * (n + 2)
    for first, last, seats in bookings:
        diff[first] += seats
        diff[last + 1] -= seats
    out = []
    run = 0
    for i in range(1, n + 1):
        run += diff[i]
        out.append(run)
    return out
''',
    tests=[[5, [[1, 2, 10], [2, 3, 20], [2, 5, 25]]], [2, [[1, 2, 10], [2, 2, 15]]], [1, []], [1, [[1, 1, 5]]], [3, []],
           [4, [[1, 4, 1], [1, 4, 1], [1, 4, 1]]], [6, [[3, 3, 7], [1, 1, 2], [6, 6, 9]]], [5, [[5, 5, 10000], [1, 5, 10000]]],
           [7, [[2, 6, 3], [3, 5, 4], [4, 4, 5]]]],
)
_r = rnd(8306)
_bk = []
for _ in range(10000):
    _f = _r.randint(1, 10000)
    _bk.append([_f, _r.randint(_f, 10000), _r.randint(1, 10000)])
p["tests"].append([10000, _bk])
p["tests"].append([10000, [[1, 10000, 10000]] * 10000])
_bk = []
for _ in range(6000):
    _f = _r.randint(1, 500)
    _bk.append([_f, _r.randint(_f, 500), _r.randint(1, 50)])
p["tests"].append([500, _bk])
p["tests"].append([9999, [[i, i, i % 9000 + 1] for i in range(1, 9999)]])


def b_flights(n, bookings):
    res = [0] * n
    for first, last, seats in bookings:
        for f in range(first, last + 1):
            res[f - 1] += seats
    return res


def g_flights(r):
    n = r.randint(1, 9)
    bk = []
    for _ in range(r.randint(0, 6)):
        f = r.randint(1, n)
        bk.append([f, r.randint(f, n), r.randint(1, 9)])
    return [n, bk]


def v_flights(tests):
    for t in tests:
        n, bk = t["args"]
        assert 1 <= n <= 10000 and len(bk) <= 10000
        assert all(1 <= f <= l <= n and 1 <= s <= 10000 for f, l, s in bk)


CHECKS["flight-bookings-seat-totals"] = (b_flights, g_flights, "exact")
VALIDATE["flight-bookings-seat-totals"] = v_flights

p = add(
    id="car-pooling-capacity-check", title="Car Pooling Capacity Check", diff="Medium", topic="Prefix Sums",
    fn="canCarpool", params=[("trips", "int[][]"), ("capacity", "int")], ret="bool", cmp="exact",
    desc="<p>A minibus drives along a straight road in one direction and never turns back. It holds at most <code>capacity</code> passengers at any moment. Each trip is a triple <code>[passengers, from, to]</code>: a group of that many people gets on at position <code>from</code> and gets off at position <code>to</code>.</p><p>When a group leaves at position <code>x</code> and another group boards at the same position <code>x</code>, the leaving group is already gone before the new one boards. Return <code>true</code> if the bus can serve every trip without ever exceeding its capacity, otherwise <code>false</code>.</p><pre>trips = [[2, 1, 5], [3, 3, 7]], capacity = 4  -> false  (positions 3 to 5 carry 5 people)\ntrips = [[2, 1, 5], [3, 5, 7]], capacity = 3  -> true</pre>",
    constraints=["1 &le; trips.length &le; 10,000", "1 &le; passengers &le; 100", "0 &le; from &lt; to &le; 100,000", "1 &le; capacity &le; 1,000,000"],
    hints=["The load on the bus only changes at the positions where somebody boards or leaves, so checking just those positions is enough.",
           "Turn every trip into two events: <code>+passengers</code> at <code>from</code> and <code>-passengers</code> at <code>to</code>. Order the events by position.",
           "At equal positions process the drop-offs before the boardings (sorting <code>(position, delta)</code> pairs does exactly this). Keep a running load and fail the moment it exceeds the capacity. Alternatively, use a difference array over positions 0..100,000."],
    editorial=["Model the bus load as a function of position. A trip raises the load by <code>passengers</code> on the half-open stretch <code>[from, to)</code>, so the load is the sum of all active trips. The question becomes whether the maximum of that function exceeds the capacity.",
               "Create the events <code>(from, +passengers)</code> and <code>(to, -passengers)</code>, sort them (negative deltas sort before positive ones at the same position, which implements the rule that leaving passengers are off before new ones board), and sweep while keeping a running total. If the total ever exceeds <code>capacity</code>, the answer is false.",
               "Since positions are bounded by 100,000, a difference array over the positions gives the same result without sorting: add at <code>from</code>, subtract at <code>to</code>, then prefix-sum and compare each value with the capacity. Sorting costs O(m log m); the array approach costs O(m + P) where P is the largest position."],
    time="O(m log m)", space="O(m)",
    solution='''def canCarpool(trips, capacity):
    events = []
    for people, start, end in trips:
        events.append((start, people))
        events.append((end, -people))
    events.sort()
    load = 0
    for _, delta in events:
        load += delta
        if load > capacity:
            return False
    return True
''',
    tests=[[[[2, 1, 5], [3, 3, 7]], 4], [[[2, 1, 5], [3, 3, 7]], 5], [[[2, 1, 5], [3, 5, 7]], 3], [[[5, 0, 1]], 4], [[[5, 0, 1]], 5],
           [[[1, 0, 100000]], 1], [[[3, 2, 4], [3, 4, 6], [3, 6, 8]], 3], [[[3, 2, 4], [3, 3, 6], [3, 6, 8]], 5],
           [[[2, 1, 10], [2, 2, 9], [2, 3, 8], [2, 4, 7]], 7], [[[2, 1, 10], [2, 2, 9], [2, 3, 8], [2, 4, 7]], 8],
           [[[10, 5, 6], [1, 0, 100000]], 10]],
)
_r = rnd(8307)
# staircase trips that never overlap more than the capacity: feasible
_t = []
for _i in range(5000):
    _t.append([_r.randint(1, 100), _i * 20, _i * 20 + _r.randint(1, 20)])
p["tests"].append([_t, 100])
# many short overlapping trips: exactly at capacity, then over by one
_t = [[1, 0, 100000]] * 10000
p["tests"].append([_t, 10000])
p["tests"].append([_t, 9999])
_t = []
for _ in range(10000):
    _s = _r.randint(0, 99990)
    _t.append([_r.randint(1, 100), _s, _s + _r.randint(1, 10)])
_load = [0] * 100002
for _p, _s, _e in _t:
    for _x in range(_s, _e):
        _load[_x] += _p
_peak = max(_load)
p["tests"].append([_t, _peak])
p["tests"].append([_t, _peak - 1])
p["tests"].append([[[100, 0, 50000], [100, 50000, 100000]] * 5000, 100])


def b_carpool(trips, capacity):
    for _, s, _ in trips:
        load = sum(pp for pp, a, b in trips if a <= s < b)
        if load > capacity:
            return False
    return True


def g_carpool(r):
    trips = []
    for _ in range(r.randint(1, 6)):
        a = r.randint(0, 8)
        trips.append([r.randint(1, 5), a, r.randint(a + 1, 10)])
    return [trips, r.randint(1, 9)]


def v_carpool(tests):
    seen = set()
    for t in tests:
        trips, cap = t["args"]
        assert 1 <= len(trips) <= 10000 and 1 <= cap <= 1000000
        assert all(1 <= p_ <= 100 and 0 <= a < b <= 100000 for p_, a, b in trips)
        seen.add(t["expected"])
    assert seen == {True, False}, "need both outcomes"


CHECKS["car-pooling-capacity-check"] = (b_carpool, g_carpool, "exact")
VALIDATE["car-pooling-capacity-check"] = v_carpool

p = add(
    id="interval-lists-intersection", title="Intersection of Two Interval Lists", diff="Medium", topic="Intervals",
    fn="intervalIntersection", params=[("firstList", "int[][]"), ("secondList", "int[][]")], ret="int[][]", cmp="exact",
    desc="<p>You are given two lists of closed intervals <code>[start, end]</code>. Inside each list the intervals are sorted by start and pairwise disjoint (no two of them share a point). The two lists may overlap each other freely.</p><p>Return the intersection of the two lists as a list of closed intervals, sorted by start. Two intervals that touch at a single point intersect in that point, for example <code>[1, 3]</code> and <code>[3, 5]</code> intersect in <code>[3, 3]</code>.</p><pre>firstList  = [[0, 2], [5, 10], [13, 23], [24, 25]]\nsecondList = [[1, 5], [8, 12], [15, 24], [25, 26]]\nresult = [[1, 2], [5, 5], [8, 10], [15, 23], [24, 24], [25, 25]]</pre>",
    constraints=["0 &le; firstList.length, secondList.length &le; 5,000", "0 &le; start &le; end &le; 10<sup>9</sup>", "Within each list, start<sub>i+1</sub> &gt; end<sub>i</sub> (sorted and disjoint)"],
    hints=["Take the first interval from each list. If they overlap, the overlap is <code>[max(starts), min(ends)]</code>; otherwise there is nothing to report for this pair.",
           "After handling a pair, one of the two intervals can never intersect anything later. Which one?",
           "Advance the pointer of the list whose current interval ends first (on ties, advancing either is fine). Because each list is sorted and disjoint, this visits every possible intersection in order."],
    editorial=["Use two pointers <code>i</code> and <code>j</code>. For the current pair compute <code>lo = max(a.start, b.start)</code> and <code>hi = min(a.end, b.end)</code>. If <code>lo &le; hi</code> the pair intersects in <code>[lo, hi]</code>, so append it (note that <code>lo == hi</code> is a valid single-point intersection).",
               "Then discard the interval that finishes first: its right end is smaller, so every later interval in the other list starts beyond it and cannot overlap it, and the later intervals of its own list are disjoint from it. When the ends are equal both intervals are finished, and advancing one of them is enough because the other will then fail the overlap test and be advanced next.",
               "Each step advances a pointer, so the total time is O(n + m) and the output is already sorted, since intersections are produced in increasing order of position. Comparing every pair would also be correct but costs O(n * m)."],
    time="O(n + m)", space="O(1)",
    solution='''def intervalIntersection(firstList, secondList):
    out = []
    i = j = 0
    while i < len(firstList) and j < len(secondList):
        lo = max(firstList[i][0], secondList[j][0])
        hi = min(firstList[i][1], secondList[j][1])
        if lo <= hi:
            out.append([lo, hi])
        if firstList[i][1] < secondList[j][1]:
            i += 1
        else:
            j += 1
    return out
''',
    tests=[[[[0, 2], [5, 10], [13, 23], [24, 25]], [[1, 5], [8, 12], [15, 24], [25, 26]]], [[[1, 3], [5, 9]], []], [[], [[4, 8], [10, 12]]],
           [[], []], [[[1, 3]], [[3, 5]]], [[[1, 3]], [[4, 5]]], [[[1, 7]], [[3, 4], [5, 6]]], [[[3, 4], [5, 6]], [[1, 7]]],
           [[[2, 2]], [[2, 2]]], [[[0, 1000000000]], [[0, 0], [5, 5], [1000000000, 1000000000]]],
           [[[1, 2], [3, 4], [5, 6]], [[2, 3], [4, 5], [6, 7]]], [[[1, 5], [10, 14]], [[2, 3], [4, 11], [12, 12]]]],
)
_r = rnd(8308)


def _disjoint_list(r, count, hi_bound):
    pts = sorted(r.sample(range(hi_bound), 2 * count))
    out = []
    for i in range(count):
        s, e = pts[2 * i], pts[2 * i + 1]
        if r.random() < 0.15:
            e = s
        out.append([s, e])
    return out


p["tests"].append([_disjoint_list(_r, 5000, 10 ** 9 + 1), _disjoint_list(_r, 5000, 10 ** 9 + 1)])
p["tests"].append([_disjoint_list(_r, 4000, 20000), _disjoint_list(_r, 5000, 20000)])
p["tests"].append([[[i * 2, i * 2] for i in range(5000)], [[i * 2, i * 2 + 1] for i in range(5000)]])
p["tests"].append([[[i * 3, i * 3 + 2] for i in range(5000)], [[i * 3 + 1, i * 3 + 3] for i in range(4000)]])
p["tests"].append([[[0, 10 ** 9]], [[i * 100000, i * 100000 + 50000] for i in range(5000)]])


def b_intersection(a, b):
    res = []
    for s1, e1 in a:
        for s2, e2 in b:
            lo, hi = max(s1, s2), min(e1, e2)
            if lo <= hi:
                res.append([lo, hi])
    res.sort()
    return res


def g_intersection(r):
    return [_disjoint_list(r, r.randint(0, 5), 30), _disjoint_list(r, r.randint(0, 5), 30)]


def v_intersection(tests):
    for t in tests:
        for lst in t["args"]:
            assert len(lst) <= 5000
            for s, e in lst:
                assert 0 <= s <= e <= 10 ** 9
            for x, y in zip(lst, lst[1:]):
                assert y[0] > x[1], "not sorted/disjoint"


CHECKS["interval-lists-intersection"] = (b_intersection, g_intersection, "exact")
VALIDATE["interval-lists-intersection"] = v_intersection


# ---------------------------------------------------------------- HARD

p = add(
    id="max-overlap-after-each-booking", title="Max Overlap After Each Booking", diff="Hard", topic="Intervals",
    fn="maxOverlapAfterEach", params=[("bookings", "int[][]")], ret="int[]", cmp="exact",
    desc="<p>A hall receives booking requests one at a time. Each request is a half-open time range <code>[start, end)</code>: it occupies every moment <code>t</code> with <code>start &le; t &lt; end</code>, so two bookings that merely meet (one ends exactly when the other starts) do not overlap.</p><p>Process the requests in the given order. After each request has been added, report the largest number of bookings that cover one common moment (considering all requests accepted so far; every request is accepted). Return these maxima as an array with one entry per request.</p><pre>bookings = [[10, 20], [50, 60], [10, 40], [5, 15], [5, 10], [25, 55]]\nresult = [1, 1, 2, 3, 3, 3]</pre>",
    constraints=["1 &le; bookings.length &le; 2,000", "0 &le; start &lt; end &le; 10<sup>9</sup>"],
    hints=["After each request the answer can only stay the same or grow, and it can grow by at most one. Only the moments inside the new range can have changed.",
           "Coordinates go up to 10<sup>9</sup>, but only the 2n distinct endpoints matter. Compress them so that each gap between two consecutive endpoints is one cell holding a count.",
           "Each booking is a range add of +1 on cells and you need the maximum cell after every insertion. A segment tree with lazy range add and a max query solves it in O(log n) per booking; the answer is the maximum stored in the root."],
    editorial=["Between two consecutive distinct endpoints the number of active bookings is constant, so compress the up to 2n endpoints to ranks and work on the n' = (number of distinct endpoints - 1) elementary cells. A booking <code>[s, e)</code> covers the cells with ranks <code>rank(s) .. rank(e) - 1</code>.",
               "The task is now: repeat a range add of +1 on cells, and after each add report the global maximum. A segment tree with range add and a stored maximum per node does exactly that. Use the non-propagating lazy form: each node keeps <code>add</code> (a pending increment applying to its whole range) and <code>mx = add + max(mx of children)</code>. An update that fully covers a node just bumps both values; otherwise recurse and recompute. The answer after a booking is the root's <code>mx</code>.",
               "That gives O(n log n) overall. A simpler approach keeps a sorted map of boundary changes and sweeps through all of it for every booking, which is O(n<sup>2</sup>) and is acceptable for n = 2,000 in compiled languages but slower in scripting languages; the tree is the version that scales."],
    time="O(n log n)", space="O(n)",
    solution='''def maxOverlapAfterEach(bookings):
    xs = sorted({x for b in bookings for x in b})
    rank = {x: i for i, x in enumerate(xs)}
    m = len(xs) - 1  # elementary cells between consecutive endpoints
    mx = [0] * (4 * m)
    add_ = [0] * (4 * m)

    def update(node, l, r, a, b):
        if a <= l and r <= b:
            mx[node] += 1
            add_[node] += 1
            return
        mid = (l + r) // 2
        if a <= mid:
            update(2 * node, l, mid, a, b)
        if b > mid:
            update(2 * node + 1, mid + 1, r, a, b)
        mx[node] = add_[node] + max(mx[2 * node], mx[2 * node + 1])

    out = []
    for s, e in bookings:
        update(1, 0, m - 1, rank[s], rank[e] - 1)
        out.append(mx[1])
    return out
''',
    tests=[[[[10, 20], [50, 60], [10, 40], [5, 15], [5, 10], [25, 55]]], [[[1, 2]]], [[[1, 2], [2, 3]]], [[[1, 5], [1, 5], [1, 5]]],
           [[[0, 1000000000], [0, 1], [999999999, 1000000000]]], [[[1, 3], [2, 4], [3, 5], [4, 6]]], [[[5, 10], [1, 4], [4, 5], [10, 11]]],
           [[[1, 10], [2, 9], [3, 8], [4, 7], [5, 6]]], [[[5, 6], [4, 7], [3, 8], [2, 9], [1, 10]]], [[[1, 4], [6, 9], [2, 7], [3, 8]]]],
)
_r = rnd(8309)
_bk = []
for _ in range(2000):
    _s = _r.randint(0, 10 ** 9 - 1)
    _bk.append([_s, _r.randint(_s + 1, min(10 ** 9, _s + 10 ** 8))])
p["tests"].append([_bk])
_bk = []
for _ in range(2000):
    _s = _r.randint(0, 1000)
    _bk.append([_s, _r.randint(_s + 1, 1001)])
p["tests"].append([_bk])
p["tests"].append([[[i, i + 1] for i in range(2000)]])
p["tests"].append([[[i, 2000 - i] for i in range(1000)] + [[i, 2001] for i in range(1000)]])
p["tests"].append([[[0, 10 ** 9]] * 2000])


def b_maxoverlap(bookings):
    res = []
    for i in range(len(bookings)):
        best = 0
        for s, _ in bookings[:i + 1]:
            best = max(best, sum(1 for a, b in bookings[:i + 1] if a <= s < b))
        res.append(best)
    return res


def g_maxoverlap(r):
    bk = []
    for _ in range(r.randint(1, 8)):
        s = r.randint(0, 12)
        bk.append([s, r.randint(s + 1, 14)])
    return [bk]


def v_maxoverlap(tests):
    for t in tests:
        bk = t["args"][0]
        assert 1 <= len(bk) <= 2000
        assert all(0 <= s < e <= 10 ** 9 for s, e in bk)


CHECKS["max-overlap-after-each-booking"] = (b_maxoverlap, g_maxoverlap, "exact")
VALIDATE["max-overlap-after-each-booking"] = v_maxoverlap

p = add(
    id="count-subarrays-with-sum-in-range", title="Count Subarrays With Sum in Range", diff="Hard", topic="Prefix Sums",
    fn="countRangeSum", params=[("nums", "int[]"), ("lower", "int"), ("upper", "int")], ret="int", cmp="exact",
    desc="<p>Given an integer array <code>nums</code> and two bounds <code>lower</code> and <code>upper</code>, count the contiguous non-empty subarrays whose sum <code>S</code> satisfies <code>lower &le; S &le; upper</code>. Subarrays at different positions are counted separately even if they have equal contents.</p><p>The array can contain negative numbers, so a sliding window does not work.</p><pre>nums = [2, -3, 1, 4], lower = 0, upper = 3\nresult = 5   ([2], [1], [2,-3,1], [-3,1,4], [2,-3,1,4])</pre>",
    constraints=["1 &le; nums.length &le; 10,000", "-10<sup>6</sup> &le; nums[i] &le; 10<sup>6</sup>", "-2<sup>31</sup> &le; lower &le; upper &le; 2<sup>31</sup> - 1"],
    hints=["Checking every pair <code>(i, j)</code> with a running sum is O(n<sup>2</sup>). With n = 10,000 that is 50 million sums, which is borderline; look for something better.",
           "With prefix sums <code>P</code> (where <code>P[0] = 0</code>), the sum of <code>nums[i..j-1]</code> is <code>P[j] - P[i]</code>. For each <code>j</code> you need to count earlier <code>i</code> with <code>P[j] - upper &le; P[i] &le; P[j] - lower</code>.",
           "Sweep <code>j</code> from left to right while keeping all earlier prefix sums in a structure that can count values in a range: a Fenwick tree over the compressed prefix values, or a merge sort that counts cross-half pairs."],
    editorial=["Let <code>P[0] = 0</code> and <code>P[k] = nums[0] + ... + nums[k-1]</code>. A subarray covering <code>nums[i..j-1]</code> has sum <code>P[j] - P[i]</code> with <code>i &lt; j</code>. So the task is to count pairs of indices <code>i &lt; j</code> with <code>lower &le; P[j] - P[i] &le; upper</code>, equivalently <code>P[i]</code> in the interval <code>[P[j] - upper, P[j] - lower]</code>.",
               "Process <code>j</code> in order, with all <code>P[i]</code> for <code>i &lt; j</code> already inserted into a data structure that supports 'insert a value' and 'how many stored values lie in [x, y]'. Prefix sums can reach 10<sup>10</sup> in absolute value, so compress them into ranks first (sort the distinct values) and use a Fenwick tree over the ranks; the interval bounds are mapped to ranks with binary search (<code>bisect_left</code> for the lower end, <code>bisect_right</code> for the upper end).",
               "Total time is O(n log n). An equally good alternative is to run merge sort on the prefix array: while merging two sorted halves, two moving pointers count, for each element of the right half, how many left-half values fall inside the allowed interval. Brute force over all pairs is O(n<sup>2</sup>)."],
    time="O(n log n)", space="O(n)",
    solution='''import bisect


def countRangeSum(nums, lower, upper):
    pre = [0]
    for x in nums:
        pre.append(pre[-1] + x)
    vals = sorted(set(pre))
    size = len(vals)
    tree = [0] * (size + 1)

    def add(pos):
        pos += 1
        while pos <= size:
            tree[pos] += 1
            pos += pos & -pos

    def query(cnt):  # number of inserted values among the first cnt ranks
        total = 0
        while cnt > 0:
            total += tree[cnt]
            cnt -= cnt & -cnt
        return total

    add(bisect.bisect_left(vals, 0))
    ans = 0
    for j in range(1, len(pre)):
        lo = bisect.bisect_left(vals, pre[j] - upper)
        hi = bisect.bisect_right(vals, pre[j] - lower)
        ans += query(hi) - query(lo)
        add(bisect.bisect_left(vals, pre[j]))
    return ans
''',
    tests=[[[2, -3, 1, 4], 0, 3], [[-2, 5, -1], -2, 2], [[0], 0, 0], [[5], 1, 4], [[5], 5, 5], [[1, 2, 3], 3, 3],
           [[-1, -1, -1], -2, -1], [[0, 0, 0, 0], 0, 0], [[1, -1, 1, -1], 0, 0], [[10, 20, 30], -100, 100],
           [[1000000, 1000000, -1000000], INT_MIN, INT_MAX], [[7, -7, 7], 1, 1000000], [[3, 1, 4, 1, 5, 9, 2, 6], 8, 12]],
)
_r = rnd(8310)
p["tests"].append([[_r.randint(-1000000, 1000000) for _ in range(10000)], -500000, 500000])
p["tests"].append([[_r.randint(-1000, 1000) for _ in range(10000)], -2000, 3000])
p["tests"].append([[_r.randint(-5, 5) for _ in range(10000)], 0, 0])
p["tests"].append([[_r.randint(0, 9) for _ in range(9000)], 100, 200])
p["tests"].append([[0] * 10000, 0, 0])
p["tests"].append([[1000000] * 10000, 5000000, 9000000])
p["tests"].append([[_r.randint(-1000000, 1000000) for _ in range(10000)], INT_MIN, INT_MAX])


def b_rangesum(nums, lower, upper):
    cnt = 0
    for i in range(len(nums)):
        s = 0
        for j in range(i, len(nums)):
            s += nums[j]
            if lower <= s <= upper:
                cnt += 1
    return cnt


def g_rangesum(r):
    lo = r.randint(-8, 8)
    return [gen_arr(r, -5, 5, 1, 12), lo, lo + r.randint(0, 8)]


def v_rangesum(tests):
    for t in tests:
        nums, lo, hi = t["args"]
        assert 1 <= len(nums) <= 10000 and all(-10 ** 6 <= x <= 10 ** 6 for x in nums)
        assert INT_MIN <= lo <= hi <= INT_MAX


CHECKS["count-subarrays-with-sum-in-range"] = (b_rangesum, g_rangesum, "exact")
VALIDATE["count-subarrays-with-sum-in-range"] = v_rangesum
