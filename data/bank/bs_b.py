"""Problems: binary search on rotated and modified sorted arrays. See data/lib.py for the registry."""
from lib import add, rnd, CHECKS, VALIDATE, gen_arr  # noqa: F401

INT_MIN, INT_MAX = -(2 ** 31), 2 ** 31 - 1


def _right(a, k):
    """Move the last element to the front, k times (k may be any non-negative number)."""
    n = len(a)
    k %= n
    return a[n - k:] + a[:n - k] if k else a[:]


def _left(a, k):
    """Move the first element to the back, k times."""
    n = len(a)
    k %= n
    return a[k:] + a[:k]


def _distinct(r, n, lo, hi):
    return r.sample(range(lo, hi + 1), n)


def _dups(r, n, lo, hi):
    return sorted(r.randint(lo, hi) for _ in range(n))


def _is_rotation(nums):
    """True when nums is a rotation of a non-decreasing array (at most one circular descent)."""
    n = len(nums)
    return sum(1 for i in range(n) if nums[i] > nums[(i + 1) % n]) <= 1


# ---------------------------------------------------------------- EASY

p = add(
    id="count-rotations-in-sorted-array", title="Count Rotations of a Sorted Array", diff="Easy", topic="Binary Search",
    fn="countRotations", params=[("nums", "int[]")], ret="int", cmp="exact", tier="common",
    desc="<p>Start with an array of distinct integers sorted in ascending order. Repeat this step <code>k</code> times: remove the <strong>last</strong> element and insert it at the front. The result is the array <code>nums</code>.</p><p>Given <code>nums</code>, return the number of steps <code>k</code> with <code>0 &le; k &lt; nums.length</code> (doing <code>nums.length</code> steps would give the original array back, so that case is never needed). For example, starting from <code>[1, 2, 3, 4, 5]</code> two steps give <code>[4, 5, 1, 2, 3]</code>, so for that input the answer is <code>2</code>. A sorted array has answer <code>0</code>.</p><p>Do it in O(log n) time.</p>",
    constraints=["1 &le; nums.length &le; 10,000", "All values are distinct", "-2<sup>31</sup> &le; nums[i] &le; 2<sup>31</sup> - 1", "nums is a sorted array after some number of the described steps"],
    hints=["Look at where the smallest element of the original sorted array ended up. What does its position say about the number of steps?",
           "Each step pushes the smallest element one place to the right, so after k steps it sits at index k. The answer is simply the index of the minimum.",
           "Binary search for the minimum: compare <code>nums[mid]</code> with <code>nums[hi]</code>. If it is larger, the minimum is strictly to the right of <code>mid</code>; otherwise it is at <code>mid</code> or to its left."],
    editorial=["The smallest element starts at index 0. Every step moves each element one place to the right (the last one wraps to the front), so after <code>k</code> steps the smallest element is at index <code>k</code>. Therefore the number of steps equals the index of the minimum, and for a sorted array that index is 0.",
               "To find that index in O(log n), keep a window <code>[lo, hi]</code> that always contains the minimum. Let <code>mid</code> be the middle. If <code>nums[mid] &gt; nums[hi]</code> then the drop from large to small values happens somewhere to the right of <code>mid</code>, so set <code>lo = mid + 1</code>. Otherwise <code>mid</code> and everything up to <code>hi</code> are in increasing order, so the minimum is at <code>mid</code> or before it: set <code>hi = mid</code>. When <code>lo == hi</code> that index is the answer. Distinct values guarantee the comparison is never a tie. Time O(log n), space O(1)."],
    time="O(log n)", space="O(1)",
    solution='''def countRotations(nums):
    lo, hi = 0, len(nums) - 1
    while lo < hi:
        mid = (lo + hi) // 2
        if nums[mid] > nums[hi]:
            lo = mid + 1
        else:
            hi = mid
    return lo
''',
    tests=[[[4, 5, 1, 2, 3]], [[1, 2, 3, 4, 5]], [[5, 1, 2, 3, 4]], [[2, 3, 4, 5, 1]], [[7]], [[2, 1]], [[1, 2]],
           [[3, 4, 5, 6, 7, 1, 2]], [[INT_MAX, INT_MIN, 0]], [[0, INT_MAX, INT_MIN]], [[-5, -4, -3, -9, -8, -7, -6]]],
)
_r = rnd(8201)
_s = sorted(_distinct(_r, 4000, -10 ** 4, 10 ** 4))
p["tests"].append([_right(_s, 2999)])
p["tests"].append([_right(_s, 1)])
p["tests"].append([_right(_s, 3999)])
p["tests"].append([_s])


def b_cnt(nums):
    return nums.index(min(nums))


def g_cnt(r):
    n = r.randint(1, 9)
    a = sorted(_distinct(r, n, -15, 15))
    return [_right(a, r.randint(0, n - 1))]


def v_cnt(tests):
    for t in tests:
        nums = t["args"][0]
        assert 1 <= len(nums) <= 10000
        assert len(set(nums)) == len(nums), "values must be distinct"
        assert all(INT_MIN <= x <= INT_MAX for x in nums)
        assert _is_rotation(nums)
        assert 0 <= t["expected"] < len(nums)


CHECKS["count-rotations-in-sorted-array"] = (b_cnt, g_cnt, "exact")
VALIDATE["count-rotations-in-sorted-array"] = v_cnt

p = add(
    id="kth-smallest-in-rotated-array", title="K-th Smallest in a Rotated Array", diff="Easy", topic="Binary Search",
    fn="kthSmallestRotated", params=[("nums", "int[]"), ("k", "int")], ret="int", cmp="exact", tier="extra",
    desc="<p>A sorted array of distinct integers was cut at some position into a front part and a back part, and the two parts were swapped. For instance <code>[0, 1, 2, 4, 5, 6, 7]</code> may become <code>[4, 5, 6, 7, 0, 1, 2]</code>. Cutting at the very end (or the very start) leaves the array unchanged.</p><p>Given such an array <code>nums</code> and an integer <code>k</code>, return the <code>k</code>-th smallest value, counting from 1. You may not sort the array: use O(log n) time. For <code>nums = [4, 5, 6, 7, 0, 1, 2]</code> and <code>k = 3</code> the answer is <code>2</code>.</p>",
    constraints=["1 &le; nums.length &le; 10,000", "1 &le; k &le; nums.length", "All values are distinct", "-2<sup>31</sup> &le; nums[i] &le; 2<sup>31</sup> - 1"],
    hints=["Sorting works but costs O(n log n). The array is already almost sorted, so what information is missing?",
           "If you knew the index where the sorted order starts (the index of the minimum), the k-th smallest would be exactly k - 1 places after it.",
           "Find the index <code>s</code> of the minimum with a binary search, then answer <code>nums[(s + k - 1) % n]</code>; the modulo handles the wrap-around."],
    editorial=["Reading the array circularly starting at the minimum gives the sorted order. So once the index <code>s</code> of the minimum is known, the k-th smallest is at <code>(s + k - 1) mod n</code>.",
               "Find <code>s</code> with the usual binary search on a window <code>[lo, hi]</code>: if <code>nums[mid] &gt; nums[hi]</code> the minimum lies right of <code>mid</code> (<code>lo = mid + 1</code>), otherwise at <code>mid</code> or left (<code>hi = mid</code>). This costs O(log n); the lookup afterwards is O(1). Space O(1)."],
    time="O(log n)", space="O(1)",
    solution='''def kthSmallestRotated(nums, k):
    n = len(nums)
    lo, hi = 0, n - 1
    while lo < hi:
        mid = (lo + hi) // 2
        if nums[mid] > nums[hi]:
            lo = mid + 1
        else:
            hi = mid
    return nums[(lo + k - 1) % n]
''',
    tests=[[[4, 5, 6, 7, 0, 1, 2], 3], [[4, 5, 6, 7, 0, 1, 2], 1], [[4, 5, 6, 7, 0, 1, 2], 7], [[4, 5, 6, 7, 0, 1, 2], 4],
           [[1, 2, 3, 4], 2], [[9], 1], [[2, 1], 1], [[2, 1], 2], [[3, 1, 2], 3], [[INT_MAX, INT_MIN, 0], 2],
           [[10, 20, 30, 40, 5], 5]],
)
_r = rnd(8202)
_s = sorted(_distinct(_r, 4000, -10 ** 4, 10 ** 4))
p["tests"].append([_left(_s, 2500), 3750])
p["tests"].append([_left(_s, 3999), 4000])
p["tests"].append([_left(_s, 1), 1])


def b_kth(nums, k):
    return sorted(nums)[k - 1]


def g_kth(r):
    n = r.randint(1, 9)
    a = sorted(_distinct(r, n, -15, 15))
    return [_left(a, r.randint(0, n - 1)), r.randint(1, n)]


def v_kth(tests):
    for t in tests:
        nums, k = t["args"]
        assert 1 <= len(nums) <= 10000 and 1 <= k <= len(nums)
        assert len(set(nums)) == len(nums)
        assert all(INT_MIN <= x <= INT_MAX for x in nums)
        assert _is_rotation(nums)


CHECKS["kth-smallest-in-rotated-array"] = (b_kth, g_kth, "exact")
VALIDATE["kth-smallest-in-rotated-array"] = v_kth

p = add(
    id="missing-term-arithmetic-progression", title="Missing Term of an Arithmetic Progression", diff="Easy", topic="Binary Search",
    fn="missingTerm", params=[("nums", "int[]")], ret="int", cmp="exact", tier="extra",
    desc="<p>An arithmetic progression is a sequence in which every term is the previous term plus a fixed non-zero step <code>d</code> (the step may be negative, so the sequence may be descending). One term of a progression was deleted, but it was <strong>not</strong> the first and <strong>not</strong> the last term. The remaining terms are given, in their original order, as <code>nums</code>.</p><p>Return the deleted term. For <code>nums = [5, 7, 11, 13]</code> the progression was <code>5, 7, 9, 11, 13</code>, so the answer is <code>9</code>. Aim for O(log n) time.</p>",
    constraints=["2 &le; nums.length &le; 10,000", "The original progression has nums.length + 1 terms, a non-zero integer step, and every term fits in a signed 32-bit integer", "The deleted term is neither the first nor the last"],
    hints=["First work out the step. You know the first and last term and how many terms the full progression had.",
           "With first term <code>a</code> and step <code>d</code>, the term at index <code>i</code> should be <code>a + i * d</code>. Where does the array stop following this rule?",
           "Before the gap every index matches <code>a + i * d</code>; from the gap on, none does. Binary search the first index that mismatches; the answer is <code>a + i * d</code> for that index."],
    editorial=["The full progression has <code>n + 1</code> terms, so the step is <code>d = (last - first) / n</code>, which is an exact integer division because the deleted term is not an end term. Compare each element with its expected value <code>first + i * d</code>.",
               "Elements before the deleted term sit exactly where expected, and every element after it is shifted by one term, so it mismatches. This makes 'matches the expectation' a monotone predicate (true, true, ..., false, false). Binary search for the first index <code>p</code> that does not match; the missing term is <code>first + p * d</code>. Time O(log n), space O(1). A linear alternative is to subtract the array sum from the sum of the full progression <code>(n + 1) * (first + last) / 2</code>."],
    time="O(log n)", space="O(1)",
    solution='''def missingTerm(nums):
    n = len(nums)
    first = nums[0]
    d = (nums[-1] - first) // n
    lo, hi = 1, n - 1
    while lo < hi:
        mid = (lo + hi) // 2
        if nums[mid] == first + mid * d:
            lo = mid + 1
        else:
            hi = mid
    return first + lo * d
''',
    tests=[[[5, 7, 11, 13]], [[1, 5]], [[10, 4]], [[15, 13, 12, 11]], [[-4, -1, 5, 8]], [[0, 1, 2, 4]], [[0, 2, 3, 4]],
           [[100, 90, 70, 60, 50]], [[INT_MIN, INT_MAX - 1]], [[INT_MAX, -715827881, -2147483645]],
           [[3, 3 + 7, 3 + 21, 3 + 28]]],
)
_r = rnd(8203)


def _ap(r, n, a, d, p_):
    full = [a + i * d for i in range(n + 1)]
    del full[p_]
    return full


p["tests"].append([_ap(_r, 3000, -9000000, 250, 2500)])
p["tests"].append([_ap(_r, 3000, 9000000, -300, 1)])
p["tests"].append([_ap(_r, 3000, 5, 1, 2999)])
p["tests"].append([_ap(_r, 2500, -2000000000, 250000, 1111)])


def b_ap(nums):
    n = len(nums)
    return (n + 1) * (nums[0] + nums[-1]) // 2 - sum(nums)


def g_ap(r):
    n = r.randint(2, 9)
    d = r.choice([-1, 1]) * r.randint(1, 6)
    a = r.randint(-30, 30)
    return [_ap(r, n, a, d, r.randint(1, n - 1))]


def v_ap(tests):
    for t in tests:
        nums = t["args"][0]
        n = len(nums)
        assert 2 <= n <= 10000
        assert (nums[-1] - nums[0]) % n == 0 and nums[-1] != nums[0]
        d = (nums[-1] - nums[0]) // n
        full = [nums[0] + i * d for i in range(n + 1)]
        miss = t["expected"]
        assert miss in full[1:-1]
        full.remove(miss)
        assert full == nums, "not a progression with exactly one interior term removed"
        assert all(INT_MIN <= x <= INT_MAX for x in nums + [miss])


CHECKS["missing-term-arithmetic-progression"] = (b_ap, g_ap, "exact")
VALIDATE["missing-term-arithmetic-progression"] = v_ap

# ---------------------------------------------------------------- MEDIUM

p = add(
    id="count-rotations-sorted-with-duplicates", title="Count Rotations with Duplicates", diff="Medium", topic="Binary Search",
    fn="countRotationsDup", params=[("nums", "int[]")], ret="int", cmp="exact", tier="extra",
    desc="<p>Start with an array sorted in non-decreasing order (equal values are allowed). Repeat this step some number of times: remove the <strong>last</strong> element and insert it at the front. The result is <code>nums</code>.</p><p>Return the <strong>smallest</strong> number of steps <code>k &ge; 0</code> that turns some sorted array into <code>nums</code>. For example <code>[3, 3, 4, 1, 1]</code> comes from <code>[1, 1, 3, 3, 4]</code> after 3 steps, so the answer is <code>3</code>. An array that is already sorted (including one whose values are all equal) has answer <code>0</code>.</p>",
    constraints=["1 &le; nums.length &le; 10,000", "-2<sup>31</sup> &le; nums[i] &le; 2<sup>31</sup> - 1", "nums is a non-decreasing array after some number of the described steps"],
    hints=["Without duplicates the answer is the index of the minimum. With duplicates the minimum value can appear many times; which of its positions counts?",
           "The sorted order starts at the one index whose predecessor is larger than it (index 0 if no such index exists). Equal neighbours never mark the start.",
           "Run the 'compare with <code>nums[hi]</code>' search. When <code>nums[mid] == nums[hi]</code> you cannot tell which side holds the start. If <code>nums[hi - 1] &gt; nums[hi]</code> then <code>hi</code> itself is the start, otherwise discard <code>hi</code> with <code>hi -= 1</code>."],
    editorial=["Since the array is a rotation of a sorted one, at most one position <code>i</code> has <code>nums[i - 1] &gt; nums[i]</code>. If there is none the array is sorted and the answer is 0; otherwise the sorted order begins at that <code>i</code> and the answer is exactly <code>i</code>. Duplicates matter only because they make it impossible to decide in O(1) which half to drop.",
               "Keep a window <code>[lo, hi]</code> containing the start. If <code>nums[mid] &gt; nums[hi]</code>, the descent is right of <code>mid</code>: <code>lo = mid + 1</code>. If <code>nums[mid] &lt; nums[hi]</code>, the descent is at or left of <code>mid</code>: <code>hi = mid</code>. On a tie, first check whether <code>hi</code> is itself the start (<code>nums[hi - 1] &gt; nums[hi]</code>) and return it; if not, <code>hi</code> is not needed and can be dropped, because its left neighbour carries the same or a smaller value. Dropping the minimum value blindly would give a wrong index for arrays like <code>[1, 1, 2, 1]</code>, whose answer is 3.",
               "The tie case removes only one element, so the worst case (for example almost all values equal) is O(n); typical inputs finish in O(log n). No algorithm can beat O(n) in the worst case because the single descent could hide anywhere among equal values. Space is O(1)."],
    time="O(log n) typical, O(n) worst", space="O(1)",
    solution='''def countRotationsDup(nums):
    lo, hi = 0, len(nums) - 1
    while lo < hi:
        mid = (lo + hi) // 2
        if nums[mid] > nums[hi]:
            lo = mid + 1
        elif nums[mid] < nums[hi]:
            hi = mid
        else:
            if nums[hi - 1] > nums[hi]:
                return hi
            hi -= 1
    return lo
''',
    tests=[[[3, 3, 4, 1, 1]], [[2, 2, 2, 0, 1]], [[1, 1, 1]], [[1, 1, 2, 1]], [[1, 2, 1, 1, 1]], [[1, 1, 1, 2, 1, 1]], [[5]],
           [[2, 1]], [[1, 2]], [[2, 2, 1, 2, 2, 2]], [[0, 0, 1, 1, 2, 2]], [[INT_MAX, INT_MAX, INT_MIN, INT_MIN, 0]]],
)
_r = rnd(8204)
p["tests"].append([[1] * 3000 + [0] + [1] * 3999])
p["tests"].append([_right(_dups(_r, 8000, 0, 60), 2345)])
p["tests"].append([_right(_dups(_r, 8000, -3, 3), 7001)])
p["tests"].append([[4] * 7000])


def b_cntd(nums):
    for i in range(1, len(nums)):
        if nums[i - 1] > nums[i]:
            return i
    return 0


def g_cntd(r):
    n = r.randint(1, 10)
    a = _dups(r, n, -3, 3)
    return [_right(a, r.randint(0, n - 1))]


def v_cntd(tests):
    for t in tests:
        nums = t["args"][0]
        assert 1 <= len(nums) <= 10000
        assert all(INT_MIN <= x <= INT_MAX for x in nums)
        assert _is_rotation(nums)
        k = t["expected"]
        s = _left(nums, k)  # undo k right-rotations
        assert s == sorted(s) and _right(s, k) == nums


CHECKS["count-rotations-sorted-with-duplicates"] = (b_cntd, g_cntd, "exact")
VALIDATE["count-rotations-sorted-with-duplicates"] = v_cntd

p = add(
    id="search-in-nearly-sorted-array", title="Search in a Nearly Sorted Array", diff="Medium", topic="Binary Search",
    fn="searchNearlySorted", params=[("nums", "int[]"), ("target", "int")], ret="int", cmp="exact", tier="common",
    desc="<p>Take an array of distinct integers sorted in ascending order and swap some <strong>disjoint</strong> pairs of neighbouring elements (no element takes part in more than one swap). The result is <code>nums</code>. So every element is at most one position away from where it would be in the sorted array. Example: <code>[10, 3, 40, 20, 50, 80, 70]</code> is a sorted array with the pairs <code>(10, 3)</code>... no, read it as <code>[3, 10, 20, 40, 50, 70, 80]</code> with the pairs at indices (0,1), (2,3) and (5,6) swapped.</p><p>Return the index of <code>target</code> in <code>nums</code>, or <code>-1</code> if it is not present. Use O(log n) time.</p>",
    constraints=["1 &le; nums.length &le; 10,000", "All values are distinct", "-2<sup>31</sup> &le; nums[i], target &le; 2<sup>31</sup> - 1", "Every element is at most one position away from its place in the sorted order (disjoint adjacent swaps)"],
    hints=["Ordinary binary search compares only <code>nums[mid]</code>. What can go wrong when the element you want sits right next to <code>mid</code>?",
           "The target, if present, can only be at <code>mid - 1</code>, <code>mid</code> or <code>mid + 1</code> when it belongs 'around' the middle. Check those three cells directly.",
           "If none of the three equals the target, compare the target with <code>nums[mid]</code>: if it is bigger, continue in <code>[mid + 2, hi]</code>, otherwise in <code>[lo, mid - 2]</code>. Skipping the checked neighbours is safe."],
    editorial=["An element is at most one cell away from its sorted position, so a sorted-order comparison with <code>nums[mid]</code> is only reliable up to a margin of one cell on each side. The fix is to test <code>mid - 1</code>, <code>mid</code> and <code>mid + 1</code> for equality at every step, then discard the rest by comparing with <code>nums[mid]</code>.",
               "Why the discarding is correct: suppose none of the three cells holds the target and <code>target &gt; nums[mid]</code>. The value at <code>mid</code> has sorted rank at least <code>mid - 1</code>, the target has a larger rank, so its rank is at least <code>mid</code>, and its actual position is within one of that: at least <code>mid - 1</code>. Since <code>mid - 1</code>, <code>mid</code> and <code>mid + 1</code> are excluded, the target must be at <code>mid + 2</code> or later. The other direction is symmetric. The window at least halves each time, so the time is O(log n) and the space is O(1)."],
    time="O(log n)", space="O(1)",
    solution='''def searchNearlySorted(nums, target):
    lo, hi = 0, len(nums) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if nums[mid] == target:
            return mid
        if mid > lo and nums[mid - 1] == target:
            return mid - 1
        if mid < hi and nums[mid + 1] == target:
            return mid + 1
        if nums[mid] < target:
            lo = mid + 2
        else:
            hi = mid - 2
    return -1
''',
    tests=[[[3, 10, 20, 40, 50, 70, 80][:0] + [10, 3, 40, 20, 50, 80, 70], 40], [[10, 3, 40, 20, 50, 80, 70], 90], [[10, 3, 40, 20, 50, 80, 70], 10],
           [[10, 3, 40, 20, 50, 80, 70], 70], [[5], 5], [[5], 6], [[2, 1], 1], [[2, 1], 2], [[1, 2, 3], 3], [[1, 3, 2, 4], 3],
           [[2, 1, 4, 3, 6, 5], 5], [[INT_MIN, INT_MAX], INT_MAX]],
)
_r = rnd(8205)


def _nearly(r, a, prob):
    a = a[:]
    i = 0
    while i + 1 < len(a):
        if r.random() < prob:
            a[i], a[i + 1] = a[i + 1], a[i]
            i += 2
        else:
            i += 1
    return a


_s = sorted(_distinct(_r, 3500, -10 ** 4, 10 ** 4))
_n = _nearly(_r, _s, 0.7)
p["tests"].append([_n, _s[1749]])
p["tests"].append([_n, _s[3499]])
p["tests"].append([_n, _s[0]])
p["tests"].append([_n, _s[1345] + 1 if _s[1345] + 1 not in set(_s) else -10 ** 4 - 5])


def b_near(nums, target):
    return nums.index(target) if target in nums else -1


def g_near(r):
    n = r.randint(1, 10)
    a = _nearly(r, sorted(_distinct(r, n, -15, 15)), 0.6)
    return [a, r.randint(-16, 16)]


def v_near(tests):
    for t in tests:
        nums, target = t["args"]
        assert 1 <= len(nums) <= 10000
        assert len(set(nums)) == len(nums)
        assert all(INT_MIN <= x <= INT_MAX for x in nums + [target])
        s = sorted(nums)
        pos = {v: i for i, v in enumerate(s)}
        assert all(abs(pos[v] - i) <= 1 for i, v in enumerate(nums)), "element displaced by more than one"


CHECKS["search-in-nearly-sorted-array"] = (b_near, g_near, "exact")
VALIDATE["search-in-nearly-sorted-array"] = v_near

p = add(
    id="count-smaller-in-rotated-sorted-array", title="Count Smaller Values in a Rotated Array", diff="Medium", topic="Binary Search",
    fn="countSmaller", params=[("nums", "int[]"), ("x", "int")], ret="int", cmp="exact", tier="extra",
    desc="<p>A sorted array of distinct integers was cut at some position into a front part and a back part and the two parts were swapped, giving <code>nums</code> (a cut at the very start or end leaves it unchanged). For <code>[0, 1, 2, 4, 5, 6, 7]</code> one possible result is <code>[5, 6, 7, 0, 1, 2, 4]</code>.</p><p>Given <code>nums</code> and an integer <code>x</code> (which need not occur in the array), return how many elements of <code>nums</code> are strictly smaller than <code>x</code>. For <code>nums = [5, 6, 7, 0, 1, 2, 4]</code> and <code>x = 5</code> the answer is <code>4</code> (the values 0, 1, 2 and 4). Use O(log n) time.</p>",
    constraints=["1 &le; nums.length &le; 10,000", "All values are distinct", "-2<sup>31</sup> &le; nums[i], x &le; 2<sup>31</sup> - 1", "nums is a rotation of a sorted array"],
    hints=["In a plain sorted array the answer is the 'insertion position' of <code>x</code>, found by binary search. What blocks that here?",
           "Imagine reading the array circularly from its minimum. That virtual array is sorted, and position <code>j</code> of it is <code>nums[(s + j) % n]</code>, where <code>s</code> is the index of the minimum.",
           "Find <code>s</code> with one binary search, then run a second binary search for the first virtual position whose value is at least <code>x</code>; that position is the count."],
    editorial=["The answer only depends on the multiset of values, not on where they sit. So count in the sorted view: find the first index <code>j</code> in sorted order with value &ge; <code>x</code>; exactly <code>j</code> elements are smaller.",
               "Step 1 finds the start <code>s</code> of the sorted order (compare <code>nums[mid]</code> with <code>nums[hi]</code>; distinct values mean no ties). Step 2 is an ordinary lower-bound search over virtual indices <code>0..n-1</code>, translating each index <code>j</code> to <code>nums[(s + j) % n]</code>. Both are O(log n) and need O(1) space."],
    time="O(log n)", space="O(1)",
    solution='''def countSmaller(nums, x):
    n = len(nums)
    lo, hi = 0, n - 1
    while lo < hi:
        mid = (lo + hi) // 2
        if nums[mid] > nums[hi]:
            lo = mid + 1
        else:
            hi = mid
    s = lo
    lo, hi = 0, n
    while lo < hi:
        mid = (lo + hi) // 2
        if nums[(s + mid) % n] < x:
            lo = mid + 1
        else:
            hi = mid
    return lo
''',
    tests=[[[5, 6, 7, 0, 1, 2, 4], 5], [[5, 6, 7, 0, 1, 2, 4], 3], [[5, 6, 7, 0, 1, 2, 4], 0], [[5, 6, 7, 0, 1, 2, 4], 8],
           [[5, 6, 7, 0, 1, 2, 4], -3], [[1, 2, 3], 2], [[3, 1, 2], 3], [[4], 4], [[4], 5], [[2, 1], 2], [[INT_MAX, INT_MIN, 0], INT_MAX],
           [[INT_MAX, INT_MIN, 0], INT_MIN]],
)
_r = rnd(8206)
_s = sorted(_distinct(_r, 4000, -10 ** 4, 10 ** 4))
p["tests"].append([_left(_s, 1222), _s[2000]])
p["tests"].append([_left(_s, 3000), _s[3999] + 1])
p["tests"].append([_left(_s, 17), _s[2500] - 1])


def b_cs(nums, x):
    return sum(1 for v in nums if v < x)


def g_cs(r):
    n = r.randint(1, 9)
    a = sorted(_distinct(r, n, -15, 15))
    return [_left(a, r.randint(0, n - 1)), r.randint(-17, 17)]


def v_cs(tests):
    for t in tests:
        nums, x = t["args"]
        assert 1 <= len(nums) <= 10000
        assert len(set(nums)) == len(nums)
        assert all(INT_MIN <= v <= INT_MAX for v in nums + [x])
        assert _is_rotation(nums)


CHECKS["count-smaller-in-rotated-sorted-array"] = (b_cs, g_cs, "exact")
VALIDATE["count-smaller-in-rotated-sorted-array"] = v_cs

p = add(
    id="count-pairs-target-sum-rotated-array", title="Count Pairs with Target Sum in a Rotated Array", diff="Medium", topic="Binary Search",
    fn="countPairsRotated", params=[("nums", "int[]"), ("target", "int")], ret="int", cmp="exact", tier="common",
    desc="<p>A sorted array of distinct integers was cut at some position into a front part and a back part and the two parts were swapped, producing <code>nums</code>. For example <code>[11, 15, 6, 8, 9, 10]</code> comes from <code>[6, 8, 9, 10, 11, 15]</code>.</p><p>Return the number of index pairs <code>(i, j)</code> with <code>i &lt; j</code> and <code>nums[i] + nums[j] == target</code>. For the array above and <code>target = 19</code> the answer is <code>2</code> (8 + 11 and 9 + 10). Do not sort or copy the array; O(n) time with O(1) extra space is expected.</p>",
    constraints=["1 &le; nums.length &le; 10,000", "All values are distinct", "-2<sup>31</sup> &le; nums[i], target &le; 2<sup>31</sup> - 1", "nums is a rotation of a sorted array"],
    hints=["For a sorted array the two-pointer technique counts the pairs in linear time. What changes when the array is rotated?",
           "Find the index <code>s</code> of the smallest element. Starting from there and walking circularly gives the sorted order.",
           "Run two pointers over virtual positions <code>0..n-1</code>, reading each value as <code>nums[(s + pos) % n]</code>: if the sum is too small advance the left pointer, if too large retreat the right pointer, and count a hit by moving both."],
    editorial=["The pair sum does not depend on the order of the array, so we can pretend to work on the sorted version. A virtual array <code>v[j] = nums[(s + j) % n]</code> is sorted when <code>s</code> is the index of the minimum, and it costs nothing to build because we only translate indices.",
               "Find <code>s</code> with the binary search that compares <code>nums[mid]</code> to <code>nums[hi]</code> (O(log n)). Then keep <code>left = 0</code> and <code>right = n - 1</code>. While <code>left &lt; right</code>: if <code>v[left] + v[right] &lt; target</code> move <code>left</code> up; if it is larger move <code>right</code> down; if equal count one pair and move both. Because values are distinct, each value takes part in at most one matching pair, so moving both pointers loses nothing. Time O(n), space O(1)."],
    time="O(n)", space="O(1)",
    solution='''def countPairsRotated(nums, target):
    n = len(nums)
    lo, hi = 0, n - 1
    while lo < hi:
        mid = (lo + hi) // 2
        if nums[mid] > nums[hi]:
            lo = mid + 1
        else:
            hi = mid
    s = lo
    left, right = 0, n - 1
    count = 0
    while left < right:
        total = nums[(s + left) % n] + nums[(s + right) % n]
        if total < target:
            left += 1
        elif total > target:
            right -= 1
        else:
            count += 1
            left += 1
            right -= 1
    return count
''',
    tests=[[[11, 15, 6, 8, 9, 10], 19], [[11, 15, 6, 8, 9, 10], 16], [[11, 15, 6, 8, 9, 10], 100], [[1, 2, 3, 4, 5, 6], 7],
           [[4, 5, 6, 1, 2, 3], 7], [[5], 10], [[3, 4], 7], [[4, 3], 8], [[-3, -2, -1, -6, -5, -4], -7],
           [[INT_MAX, INT_MIN, 0, 5], -1], [[INT_MAX, INT_MIN, 0, 5], INT_MAX - 1], [[0, 2, 4, 6, -8, -6, -4, -2], 0]],
)
_r = rnd(8207)
_s = sorted(_distinct(_r, 4000, -10 ** 4, 10 ** 4))
p["tests"].append([_left(_s, 1234), _s[10] + _s[3000]])
_pairs = [_s[i] + _s[3999 - i] for i in range(0, 3000, 7)]
p["tests"].append([_left(_s, 2321), _s[100] + _s[200]])
_sym = sorted(set(range(-3000, 3001)))  # symmetric values: many pairs sum to 0
p["tests"].append([_right(_sym, 1500), 0])


def b_pairs(nums, target):
    n = len(nums)
    return sum(1 for i in range(n) for j in range(i + 1, n) if nums[i] + nums[j] == target)


def g_pairs(r):
    n = r.randint(1, 9)
    a = sorted(_distinct(r, n, -10, 10))
    return [_left(a, r.randint(0, n - 1)), r.randint(-14, 14)]


def v_pairs(tests):
    for t in tests:
        nums, target = t["args"]
        assert 1 <= len(nums) <= 10000
        assert len(set(nums)) == len(nums)
        assert all(INT_MIN <= v <= INT_MAX for v in nums + [target])
        assert _is_rotation(nums)


CHECKS["count-pairs-target-sum-rotated-array"] = (b_pairs, g_pairs, "exact")
VALIDATE["count-pairs-target-sum-rotated-array"] = v_pairs

p = add(
    id="closest-value-in-rotated-sorted-array", title="Closest Value in a Rotated Array", diff="Medium", topic="Binary Search",
    fn="closestRotated", params=[("nums", "int[]"), ("x", "int")], ret="int", cmp="exact", tier="extra",
    desc="<p>A sorted array of distinct integers was cut at some position into a front part and a back part and the two parts were swapped, producing <code>nums</code> (a cut at the very start or end leaves it unchanged).</p><p>Given <code>nums</code> and an integer <code>x</code>, return the <strong>value</strong> in <code>nums</code> that is closest to <code>x</code>, that is, the one minimising <code>|value - x|</code>. If two values are equally close, return the smaller one. For <code>nums = [6, 7, 9, 1, 3, 4]</code>: <code>x = 5</code> gives <code>4</code> (4 and 6 tie, take 4), <code>x = 8</code> gives <code>7</code>, and <code>x = 100</code> gives <code>9</code>. Use O(log n) time.</p>",
    constraints=["1 &le; nums.length &le; 10,000", "All values are distinct", "-2<sup>31</sup> &le; nums[i], x &le; 2<sup>31</sup> - 1", "nums is a rotation of a sorted array"],
    hints=["In a sorted array, the closest value is one of the two neighbours of the position where <code>x</code> would be inserted.",
           "Locate the start <code>s</code> of the sorted order (the minimum). Then you can treat <code>nums[(s + j) % n]</code> as a sorted array indexed by <code>j</code>.",
           "Binary search the first virtual position <code>j</code> with value at least <code>x</code>. Compare the values at <code>j - 1</code> and <code>j</code> (when they exist); on a tie in distance keep the smaller value, which is the one at <code>j - 1</code>."],
    editorial=["First find the start <code>s</code> of the sorted order with the 'compare with <code>nums[hi]</code>' binary search. Then perform a lower-bound search on virtual indices: the first <code>j</code> such that <code>nums[(s + j) % n] &ge; x</code> (or <code>n</code> if none).",
               "The closest value must be one of the two neighbours of that insertion point: the value just before it (largest below <code>x</code>) and the value at it (smallest not below <code>x</code>). If <code>j == 0</code> or <code>j == n</code> only one candidate exists. Otherwise compute the two distances and return the lower one; on equal distance return the smaller value, i.e. the one at <code>j - 1</code>. Two O(log n) searches, O(1) space."],
    time="O(log n)", space="O(1)",
    solution='''def closestRotated(nums, x):
    n = len(nums)
    lo, hi = 0, n - 1
    while lo < hi:
        mid = (lo + hi) // 2
        if nums[mid] > nums[hi]:
            lo = mid + 1
        else:
            hi = mid
    s = lo
    lo, hi = 0, n
    while lo < hi:
        mid = (lo + hi) // 2
        if nums[(s + mid) % n] < x:
            lo = mid + 1
        else:
            hi = mid
    if lo == 0:
        return nums[s]
    if lo == n:
        return nums[(s + n - 1) % n]
    below = nums[(s + lo - 1) % n]
    above = nums[(s + lo) % n]
    return below if x - below <= above - x else above
''',
    tests=[[[6, 7, 9, 1, 3, 4], 5], [[6, 7, 9, 1, 3, 4], 8], [[6, 7, 9, 1, 3, 4], 100], [[6, 7, 9, 1, 3, 4], -100], [[6, 7, 9, 1, 3, 4], 3],
           [[6, 7, 9, 1, 3, 4], 2], [[12], 0], [[2, 1], 2], [[1, 2, 3], 2], [[INT_MAX, INT_MIN, 0], 1], [[INT_MAX, INT_MIN, 0], INT_MAX],
           [[INT_MAX, INT_MIN], 0], [[INT_MAX, INT_MIN], -1]],
)
_r = rnd(8208)
_s = sorted(_distinct(_r, 4000, -10 ** 4, 10 ** 4))
p["tests"].append([_left(_s, 2030), (_s[2000] + _s[2001]) // 2])
p["tests"].append([_left(_s, 4), _s[3999] + 1000])
p["tests"].append([_right(_s, 700), _s[100] + 1])


def b_close(nums, x):
    return min(nums, key=lambda v: (abs(v - x), v))


def g_close(r):
    n = r.randint(1, 9)
    a = sorted(_distinct(r, n, -15, 15))
    return [_left(a, r.randint(0, n - 1)), r.randint(-18, 18)]


def v_close(tests):
    for t in tests:
        nums, x = t["args"]
        assert 1 <= len(nums) <= 10000
        assert len(set(nums)) == len(nums)
        assert all(INT_MIN <= v <= INT_MAX for v in nums + [x])
        assert _is_rotation(nums)


CHECKS["closest-value-in-rotated-sorted-array"] = (b_close, g_close, "exact")
VALIDATE["closest-value-in-rotated-sorted-array"] = v_close

p = add(
    id="count-in-value-range-rotated-duplicates", title="Count Values in a Range of a Rotated Array", diff="Medium", topic="Binary Search",
    fn="countInRange", params=[("nums", "int[]"), ("lo", "int"), ("hi", "int")], ret="int", cmp="exact", tier="extra",
    desc="<p>A non-decreasing array (repeated values allowed) was cut at some position into a front part and a back part and the two parts were swapped, producing <code>nums</code>. For example <code>[3, 4, 4, 5, 1, 1, 2, 3]</code> comes from <code>[1, 1, 2, 3, 3, 4, 4, 5]</code>.</p><p>Given <code>nums</code> and two integers <code>lo &le; hi</code>, return how many elements <code>v</code> satisfy <code>lo &le; v &le; hi</code> (duplicates are counted every time). For the array above, <code>lo = 2</code> and <code>hi = 4</code> the answer is <code>5</code> (the values 2, 3, 3, 4, 4). Aim for O(log n) on typical inputs.</p>",
    constraints=["1 &le; nums.length &le; 10,000", "-2<sup>31</sup> &le; nums[i], lo, hi &le; 2<sup>31</sup> - 1", "lo &le; hi", "nums is a rotation of a non-decreasing array"],
    hints=["If you knew where the sorted order starts, the answer would be 'upper bound of hi' minus 'lower bound of lo' in the sorted view.",
           "Find the start <code>s</code> (the single index whose left neighbour is larger, or 0). With ties, <code>nums[mid] == nums[hi]</code> means you cannot decide: if <code>nums[hi - 1] &gt; nums[hi]</code> then <code>s = hi</code>, otherwise drop <code>hi</code>.",
           "Count = (first virtual position with value &gt; hi) - (first virtual position with value &ge; lo), reading virtual position <code>j</code> as <code>nums[(s + j) % n]</code>."],
    editorial=["Counting values in a range is the same in every rotation of the array, so rebuild the sorted view virtually: position <code>j</code> of the sorted order is <code>nums[(s + j) % n]</code>, where <code>s</code> is the start of the sorted order.",
               "Finding <code>s</code> with duplicates uses the 'compare <code>nums[mid]</code> with <code>nums[hi]</code>' search. A larger middle sends the window right; a smaller middle sends it left; a tie is resolved by checking whether <code>hi</code> is itself the start (<code>nums[hi - 1] &gt; nums[hi]</code>) and otherwise discarding <code>hi</code>. This is O(log n) typically and O(n) in the worst case (for example an array of nearly all equal values).",
               "Then two ordinary binary searches over virtual positions give <code>a</code> = number of values &lt; <code>lo</code> and <code>b</code> = number of values &le; <code>hi</code>. The answer is <code>b - a</code>. Space O(1)."],
    time="O(log n) typical, O(n) worst", space="O(1)",
    solution='''def countInRange(nums, lo, hi):
    n = len(nums)
    a, b = 0, n - 1
    start = None
    while a < b:
        mid = (a + b) // 2
        if nums[mid] > nums[b]:
            a = mid + 1
        elif nums[mid] < nums[b]:
            b = mid
        else:
            if nums[b - 1] > nums[b]:
                start = b
                break
            b -= 1
    if start is None:
        start = a

    def first_at_least(v):
        l, r = 0, n
        while l < r:
            m = (l + r) // 2
            if nums[(start + m) % n] < v:
                l = m + 1
            else:
                r = m
        return l

    return first_at_least(hi + 1) - first_at_least(lo)
''',
    tests=[[[3, 4, 4, 5, 1, 1, 2, 3], 2, 4], [[3, 4, 4, 5, 1, 1, 2, 3], 1, 5], [[3, 4, 4, 5, 1, 1, 2, 3], 6, 9], [[3, 4, 4, 5, 1, 1, 2, 3], -5, 0],
           [[3, 4, 4, 5, 1, 1, 2, 3], 3, 3], [[1, 1, 2, 1], 1, 1], [[1, 1, 2, 1], 2, 2], [[7, 7, 7], 7, 7], [[7, 7, 7], 8, 9], [[5], 5, 5],
           [[2, 1], 1, 2], [[INT_MAX, INT_MAX, INT_MIN, INT_MIN, 0], INT_MIN, INT_MAX], [[INT_MAX, INT_MAX, INT_MIN, INT_MIN, 0], -1, INT_MAX]],
)
_r = rnd(8209)
p["tests"].append([_right(_dups(_r, 8000, -50, 50), 3210), -10, 20])
p["tests"].append([_right(_dups(_r, 8000, 0, 5), 7777), 2, 3])
p["tests"].append([[1] * 4000 + [0] + [1] * 3999, 0, 0])
p["tests"].append([_left(_dups(_r, 8000, -1000, 1000), 4000), -1000, 1000])


def b_range(nums, lo, hi):
    return sum(1 for v in nums if lo <= v <= hi)


def g_range(r):
    n = r.randint(1, 10)
    a = _dups(r, n, -4, 4)
    lo = r.randint(-5, 5)
    return [_left(a, r.randint(0, n - 1)), lo, r.randint(lo, 5)]


def v_range(tests):
    for t in tests:
        nums, lo, hi = t["args"]
        assert 1 <= len(nums) <= 10000
        assert lo <= hi
        assert all(INT_MIN <= v <= INT_MAX for v in nums + [lo, hi])
        assert _is_rotation(nums)


CHECKS["count-in-value-range-rotated-duplicates"] = (b_range, g_range, "exact")
VALIDATE["count-in-value-range-rotated-duplicates"] = v_range

# ---------------------------------------------------------------- HARD

p = add(
    id="minimum-in-rotated-array-with-duplicates", title="Minimum of a Rotated Array with Duplicates", diff="Hard", topic="Binary Search",
    fn="findMinDup", params=[("nums", "int[]")], ret="int", cmp="exact", tier="common",
    desc="<p>A non-decreasing array (repeated values allowed) was cut at some position into a front part and a back part and the two parts were swapped, producing <code>nums</code>. For example <code>[1, 3, 3]</code> may become <code>[3, 3, 1]</code> or <code>[3, 1, 3]</code>, and <code>[2, 2, 2, 0, 1]</code> comes from <code>[0, 1, 2, 2, 2]</code>. A cut at the very start or end leaves the array as it is.</p><p>Return the smallest value in <code>nums</code>. Do better than a plain scan whenever the duplicates allow it, and explain what the worst case is.</p>",
    constraints=["1 &le; nums.length &le; 10,000", "-2<sup>31</sup> &le; nums[i] &le; 2<sup>31</sup> - 1", "nums is a rotation of a non-decreasing array"],
    hints=["The classic search compares <code>nums[mid]</code> with <code>nums[hi]</code>. When values are distinct this decides the side every time. Which comparison outcome becomes ambiguous with duplicates?",
           "If <code>nums[mid] &gt; nums[hi]</code> the minimum is right of <code>mid</code>; if <code>nums[mid] &lt; nums[hi]</code> it is at <code>mid</code> or left. Only <code>nums[mid] == nums[hi]</code> is unclear: the minimum may be on either side.",
           "In the tie case you can safely discard just <code>hi</code>: its value is repeated at <code>mid</code>, so if <code>hi</code> held the minimum, <code>mid</code> still holds that same minimum. Do <code>hi -= 1</code> and continue."],
    editorial=["Keep a window <code>[lo, hi]</code> that always contains a copy of the minimum. If <code>nums[mid] &gt; nums[hi]</code>, the 'cliff' where values drop is right of <code>mid</code>, so <code>mid</code> cannot be the minimum: <code>lo = mid + 1</code>. If <code>nums[mid] &lt; nums[hi]</code>, the segment from <code>mid</code> to <code>hi</code> is increasing, so the minimum is at <code>mid</code> or earlier: <code>hi = mid</code>.",
               "With <code>nums[mid] == nums[hi]</code> nothing is known about the sides: <code>[1, 1, 1, 0, 1]</code> and <code>[1, 0, 1, 1, 1]</code> both have this tie at the first step, yet the minimum lies on opposite sides. What can be said is that removing <code>hi</code> never loses the minimum value, because an equal value stays at <code>mid</code>. So shrink with <code>hi -= 1</code>.",
               "Each tie costs one element, so the worst case is O(n) (an array of all equal values with one smaller value hidden somewhere shows that no algorithm can do better: that single value could be at any index and each comparison reveals at most one position). On inputs with few ties it is O(log n). Space O(1)."],
    time="O(log n) typical, O(n) worst", space="O(1)",
    solution='''def findMinDup(nums):
    lo, hi = 0, len(nums) - 1
    while lo < hi:
        mid = (lo + hi) // 2
        if nums[mid] > nums[hi]:
            lo = mid + 1
        elif nums[mid] < nums[hi]:
            hi = mid
        else:
            hi -= 1
    return nums[lo]
''',
    tests=[[[3, 3, 1, 3]], [[2, 2, 2, 0, 1]], [[1, 3, 3]], [[3, 1, 3]], [[3, 3, 1]], [[1, 1, 1, 0, 1]], [[1, 0, 1, 1, 1]], [[4]], [[5, 5, 5, 5]],
           [[2, 1]], [[1, 2]], [[INT_MAX, INT_MAX, INT_MIN, INT_MAX]], [[0, 0, 0, -1, 0, 0]]],
)
_r = rnd(8210)
p["tests"].append([[1] * 3500 + [0] + [1] * 4500])
p["tests"].append([_right(_dups(_r, 8000, -1000, 1000), 4567)])
p["tests"].append([_left(_dups(_r, 8000, 0, 3), 1234)])
p["tests"].append([[9] * 7777 + [8] + [9] * 222])


def b_mind(nums):
    return min(nums)


def g_mind(r):
    n = r.randint(1, 10)
    a = _dups(r, n, -3, 3)
    return [_left(a, r.randint(0, n - 1))]


def v_mind(tests):
    for t in tests:
        nums = t["args"][0]
        assert 1 <= len(nums) <= 10000
        assert all(INT_MIN <= v <= INT_MAX for v in nums)
        assert _is_rotation(nums)
        assert t["expected"] == min(nums)


CHECKS["minimum-in-rotated-array-with-duplicates"] = (b_mind, g_mind, "exact")
VALIDATE["minimum-in-rotated-array-with-duplicates"] = v_mind

p = add(
    id="first-index-in-rotated-array-with-duplicates", title="First Index of a Value in a Rotated Array with Duplicates", diff="Hard", topic="Binary Search",
    fn="firstIndexRotated", params=[("nums", "int[]"), ("target", "int")], ret="int", cmp="exact", tier="extra",
    desc="<p>A non-decreasing array (repeated values allowed) was cut at some position into a front part and a back part and the two parts were swapped, producing <code>nums</code>. For example <code>[4, 5, 1, 2, 4, 4]</code> comes from <code>[1, 2, 4, 4, 4, 5]</code>: a value can now appear at both ends of the array.</p><p>Return the <strong>smallest index</strong> <code>i</code> such that <code>nums[i] == target</code>, or <code>-1</code> if there is none. For <code>nums = [4, 5, 1, 2, 4, 4]</code> and <code>target = 4</code> the answer is <code>0</code> (not 4), for <code>target = 2</code> it is <code>3</code>, and for <code>target = 3</code> it is <code>-1</code>. Aim for O(log n) on typical inputs.</p>",
    constraints=["1 &le; nums.length &le; 10,000", "-2<sup>31</sup> &le; nums[i], target &le; 2<sup>31</sup> - 1", "nums is a rotation of a non-decreasing array"],
    hints=["Equal values can be split between the front and the back of the array, so finding 'a' match is not enough. First you need a reliable anchor: where does the sorted order start?",
           "Find the start index <code>s</code> of the sorted order. If <code>nums[mid] == nums[hi]</code>, check whether <code>nums[hi - 1] &gt; nums[hi]</code> (then <code>hi</code> is the start); otherwise drop <code>hi</code>. Then the virtual array <code>nums[(s + j) % n]</code> is sorted, and a lower-bound and an upper-bound search give the block of equal values.",
           "That block occupies virtual positions <code>[a, b)</code>. Virtual position <code>j</code> lives at real index <code>s + j</code> if that is below <code>n</code>, otherwise at <code>s + j - n</code>. Any copy that wrapped around has a smaller real index than every copy that did not, so prefer the first wrapped position <code>max(a, n - s)</code> when it is inside the block."],
    editorial=["Step 1: locate the start <code>s</code> of the sorted order, the unique index whose left neighbour is larger (or 0 if the array is sorted). Binary search with window <code>[lo, hi]</code>: a larger <code>nums[mid]</code> than <code>nums[hi]</code> moves <code>lo</code> to <code>mid + 1</code>, a smaller one moves <code>hi</code> to <code>mid</code>, and a tie is resolved by returning <code>hi</code> if <code>nums[hi - 1] &gt; nums[hi]</code> and otherwise dropping <code>hi</code>. This is O(log n) typically and O(n) in the worst case, which cannot be avoided with duplicates.",
               "Step 2: in the virtual sorted array <code>v[j] = nums[(s + j) % n]</code> binary search the first position <code>a</code> with <code>v[a] &ge; target</code> and the first position <code>b</code> with <code>v[b] &gt; target</code>. If <code>a == b</code> the target is absent: return -1.",
               "Step 3: translate back. Positions <code>j &lt; n - s</code> map to real index <code>s + j</code> (these are at or after <code>s</code>), positions <code>j &ge; n - s</code> map to <code>s + j - n</code> (these are before <code>s</code>, hence smaller). So if the block reaches the wrapped region (<code>b - 1 &ge; n - s</code>) the answer is <code>s + max(a, n - s) - n</code>; otherwise it is <code>s + a</code>. Space O(1)."],
    time="O(log n) typical, O(n) worst", space="O(1)",
    solution='''def firstIndexRotated(nums, target):
    n = len(nums)
    lo, hi = 0, n - 1
    s = None
    while lo < hi:
        mid = (lo + hi) // 2
        if nums[mid] > nums[hi]:
            lo = mid + 1
        elif nums[mid] < nums[hi]:
            hi = mid
        else:
            if nums[hi - 1] > nums[hi]:
                s = hi
                break
            hi -= 1
    if s is None:
        s = lo

    def bound(strict):
        l, r = 0, n
        while l < r:
            m = (l + r) // 2
            v = nums[(s + m) % n]
            if v < target or (strict and v == target):
                l = m + 1
            else:
                r = m
        return l

    a, b = bound(False), bound(True)
    if a == b:
        return -1
    if b - 1 >= n - s:
        return s + max(a, n - s) - n
    return s + a
''',
    tests=[[[4, 5, 1, 2, 4, 4], 4], [[4, 5, 1, 2, 4, 4], 2], [[4, 5, 1, 2, 4, 4], 3], [[4, 5, 1, 2, 4, 4], 5], [[4, 5, 1, 2, 4, 4], 1],
           [[4, 5, 6, 6, 7, 0, 1, 2, 4, 4], 4], [[4, 5, 6, 6, 7, 0, 1, 2, 4, 4], 6], [[1, 1, 2, 1], 1], [[1, 1, 2, 1], 2],
           [[2, 2, 2, 3, 2, 2, 2], 3], [[2, 2, 2, 3, 2, 2, 2], 2], [[7], 7], [[7], 8], [[3, 1], 3], [[INT_MAX, INT_MIN, INT_MIN, INT_MAX], INT_MAX]],
)
_r = rnd(8211)
p["tests"].append([_right(_dups(_r, 8000, -40, 40), 3000), 0])
p["tests"].append([_left(_dups(_r, 8000, 0, 9), 5555), 4])
p["tests"].append([[1] * 4000 + [2] + [1] * 3999, 2])
p["tests"].append([_left(_dups(_r, 8000, 0, 2), 2600), 3])


def b_first(nums, target):
    return nums.index(target) if target in nums else -1


def g_first(r):
    n = r.randint(1, 10)
    a = _dups(r, n, -3, 3)
    return [_left(a, r.randint(0, n - 1)), r.randint(-4, 4)]


def v_first(tests):
    for t in tests:
        nums, target = t["args"]
        assert 1 <= len(nums) <= 10000
        assert all(INT_MIN <= v <= INT_MAX for v in nums + [target])
        assert _is_rotation(nums)
        e = t["expected"]
        assert e == -1 or (nums[e] == target and target not in nums[:e])


CHECKS["first-index-in-rotated-array-with-duplicates"] = (b_first, g_first, "exact")
VALIDATE["first-index-in-rotated-array-with-duplicates"] = v_first
