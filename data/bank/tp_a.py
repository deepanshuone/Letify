"""Problems: two pointers on sorted arrays (pair / triple / quad searches, closest sums, counting under a bound).
See data/lib.py for the registry."""
from itertools import combinations
from math import comb

from lib import add, rnd, CHECKS, VALIDATE, gen_arr  # noqa: F401

TOPIC = "Two Pointers"
MOD = 10 ** 9 + 7


def _sorted_ok(a):
    return all(a[i] <= a[i + 1] for i in range(len(a) - 1))


# ---------------------------------------------------------------- EASY

p = add(
    id="count-pairs-sum-below-target", title="Count Pairs With Sum Below Target", diff="Easy", topic=TOPIC,
    fn="countPairsBelow", params=[("nums", "int[]"), ("target", "int")], ret="int", cmp="exact",
    desc="<p>Given an integer array <code>nums</code> (in any order) and an integer <code>target</code>, count the pairs of positions <code>i &lt; j</code> for which <code>nums[i] + nums[j] &lt; target</code>.</p><p>Pairs are counted by position, so equal values at different positions make different pairs.</p><pre>nums = [3, 1, 4, 2, 5], target = 7\npairs below 7: (3,1) (3,2) (1,4) (1,2) (1,5) (4,2)\nresult = 6</pre>",
    constraints=["0 &le; nums.length &le; 10,000", "-10<sup>9</sup> &le; nums[i] &le; 10<sup>9</sup>", "-2 &times; 10<sup>9</sup> &le; target &le; 2 &times; 10<sup>9</sup>"],
    hints=["Checking all pairs is O(n&sup2;). The positions of a pair do not matter for its sum, so you are free to reorder the array first.",
           "After sorting, take the smallest and the largest element. If their sum is below the target, what do you know about the smallest element and every element between them?",
           "Use <code>lo = 0</code> and <code>hi = n - 1</code>. If <code>a[lo] + a[hi] &lt; target</code>, then <code>a[lo]</code> pairs with all of <code>a[lo+1..hi]</code>: add <code>hi - lo</code> and move <code>lo</code> right. Otherwise move <code>hi</code> left."],
    editorial=["Sorting does not change which pairs of values exist, only their order, and the question depends only on the multiset of values. So sort first.",
               "Keep <code>lo</code> at the start and <code>hi</code> at the end. If <code>a[lo] + a[hi] &lt; target</code>, then every element between them is at most <code>a[hi]</code>, so <code>a[lo]</code> forms a valid pair with each of <code>a[lo+1], ..., a[hi]</code>. That is <code>hi - lo</code> pairs counted at once; then <code>lo</code> is finished and we advance it. If the sum is too big, <code>a[hi]</code> is too big for every remaining left partner (the smallest is already tried), so it is finished and we decrement <code>hi</code>.",
               "Each step finishes one element, so the sweep is O(n) after the O(n log n) sort. The answer can reach about 5 &times; 10<sup>7</sup>, which fits in 32 bits, but the sums of two values need 64 bits in languages with fixed-width integers."],
    time="O(n log n)", space="O(1) extra",
    solution='''def countPairsBelow(nums, target):
    a = sorted(nums)
    lo, hi = 0, len(a) - 1
    count = 0
    while lo < hi:
        if a[lo] + a[hi] < target:
            count += hi - lo
            lo += 1
        else:
            hi -= 1
    return count
''',
    tests=[[[3, 1, 4, 2, 5], 7], [[], 5], [[4], 100], [[1, 1], 3], [[1, 1], 2], [[5, 5, 5, 5], 10], [[5, 5, 5, 5], 11],
           [[-3, 2, -8, 7, 0], -1], [[10 ** 9, 10 ** 9, -10 ** 9], 2 * 10 ** 9], [[10 ** 9, 10 ** 9, -10 ** 9], 2 * 10 ** 9 + 0 - 1],
           [[-10 ** 9, -10 ** 9, -10 ** 9], -2 * 10 ** 9 + 1], [[6, 4, 2, 8, 10, 12], 3]],
)
_r = rnd(7001)
_a = [_r.randint(-10 ** 6, 10 ** 6) for _ in range(5000)]
p["tests"].append([_a, 100000])
_a = [_r.randint(-10 ** 9, 10 ** 9) for _ in range(3000)]
p["tests"].append([_a, -5 * 10 ** 8])
_a = [_r.randint(0, 50) for _ in range(4000)]
p["tests"].append([_a, 51])


def b_below(nums, target):
    n = len(nums)
    return sum(1 for i in range(n) for j in range(i + 1, n) if nums[i] + nums[j] < target)


def v_below(tests):
    for t in tests:
        nums, target = t["args"]
        assert 0 <= len(nums) <= 10000
        assert all(-10 ** 9 <= x <= 10 ** 9 for x in nums)
        assert -2 * 10 ** 9 <= target <= 2 * 10 ** 9


CHECKS["count-pairs-sum-below-target"] = (b_below, lambda r: [gen_arr(r, -8, 8, 0, 10), r.randint(-12, 12)], "exact")
VALIDATE["count-pairs-sum-below-target"] = v_below

p = add(
    id="closest-pair-sum-to-target", title="Closest Pair Sum in a Sorted Array", diff="Easy", topic=TOPIC,
    fn="closestPairSum", params=[("nums", "int[]"), ("target", "int")], ret="int", cmp="exact",
    desc="<p>The array <code>nums</code> is sorted in non-decreasing order and has at least two elements. Among all sums <code>nums[i] + nums[j]</code> with <code>i &lt; j</code>, return the sum that is closest to <code>target</code> (smallest absolute difference).</p><p>If two different sums are equally close, return the <strong>smaller</strong> of them. Return the sum itself, not the positions.</p><pre>nums = [1, 3, 8, 10, 15], target = 12\nsums 11 (=1+10 or 3+8) and 13 (=3+10) are both at distance 1\nresult = 11</pre>",
    constraints=["2 &le; nums.length &le; 10,000", "-10<sup>9</sup> &le; nums[i] &le; 10<sup>9</sup>, sorted in non-decreasing order", "-2 &times; 10<sup>9</sup> &le; target &le; 2 &times; 10<sup>9</sup>"],
    hints=["Trying every pair works but takes O(n&sup2;). Use the sorted order.",
           "Look at the smallest and the largest element. If their sum is below the target, can the smallest element do better with a partner other than the largest one?",
           "Keep two pointers at the ends. Record the current sum if it beats the best one (closer, or equally close and smaller). Move <code>lo</code> right when the sum is below the target, <code>hi</code> left when above, and stop immediately on equality."],
    editorial=["Set <code>lo = 0</code>, <code>hi = n - 1</code>. At each step look at <code>s = a[lo] + a[hi]</code> and compare it with the best sum so far using the key <code>(|s - target|, s)</code>, which also encodes the tie rule. If <code>s == target</code> nothing can be closer, so return it.",
               "If <code>s &lt; target</code>, the element at <code>lo</code> combined with any partner at or before <code>hi</code> gives a sum at most <code>s</code>, which is even further below the target, so <code>lo</code> can be discarded. Symmetrically, when <code>s &gt; target</code> the element at <code>hi</code> is discarded. Each step removes one index: O(n) time and O(1) space.",
               "The same discard argument is the engine of 3Sum, 4Sum and their closest-sum variants: fix some elements, then sweep the rest with two pointers."],
    time="O(n)", space="O(1)",
    solution='''def closestPairSum(nums, target):
    lo, hi = 0, len(nums) - 1
    best = None
    while lo < hi:
        s = nums[lo] + nums[hi]
        key = (abs(s - target), s)
        if best is None or key < best:
            best = key
        if s == target:
            break
        if s < target:
            lo += 1
        else:
            hi -= 1
    return best[1]
''',
    tests=[[[1, 3, 8, 10, 15], 12], [[1, 2], 100], [[1, 2], -100], [[1, 2], 3], [[-5, -5], 0], [[0, 0, 0], 1],
           [[-9, -4, 0, 3, 7], -2], [[-9, -4, 0, 3, 7], 5], [[2, 4, 6, 8], 9], [[2, 4, 6, 8], 11],
           [[-10 ** 9, -10 ** 9, 10 ** 9, 10 ** 9], 0], [[-10 ** 9, 10 ** 9], 2 * 10 ** 9], [[5, 5, 5, 5, 5], 4]],
)
_r = rnd(7002)
p["tests"].append([sorted(_r.randint(-10 ** 6, 10 ** 6) for _ in range(5000)), 123456])
p["tests"].append([sorted(_r.randint(-10 ** 9, 10 ** 9) for _ in range(3000)), -777777777])
p["tests"].append([sorted(_r.randint(0, 1000) for _ in range(4000)), 1999])


def b_closest(nums, target):
    n = len(nums)
    return min((abs(nums[i] + nums[j] - target), nums[i] + nums[j]) for i in range(n) for j in range(i + 1, n))[1]


def g_closest(r):
    return [sorted(gen_arr(r, -9, 9, 2, 9)), r.randint(-20, 20)]


def v_closest(tests):
    for t in tests:
        nums, target = t["args"]
        assert 2 <= len(nums) <= 10000 and _sorted_ok(nums)
        assert all(-10 ** 9 <= x <= 10 ** 9 for x in nums)
        assert -2 * 10 ** 9 <= target <= 2 * 10 ** 9


CHECKS["closest-pair-sum-to-target"] = (b_closest, g_closest, "exact")
VALIDATE["closest-pair-sum-to-target"] = v_closest


# ---------------------------------------------------------------- MEDIUM

p = add(
    id="count-value-pairs-with-difference-k", title="Distinct Value Pairs With Difference K", diff="Medium", topic=TOPIC,
    fn="countDiffPairs", params=[("nums", "int[]"), ("k", "int")], ret="int", cmp="exact",
    desc="<p>The array <code>nums</code> is sorted in non-decreasing order and may contain repeated values. Count the <strong>distinct pairs of values</strong> <code>(x, y)</code> with <code>y - x = k</code> such that <code>x</code> and <code>y</code> can be taken from two different positions of the array.</p><p>Two pairs are the same when they have the same <code>(x, y)</code>, however many times those values occur. For <code>k = 0</code> a value counts only when it occurs at least twice.</p><pre>nums = [1, 1, 3, 3, 5, 5, 5, 7], k = 2\ndistinct value pairs: (1,3) (3,5) (5,7)\nresult = 3</pre>",
    constraints=["0 &le; nums.length &le; 10,000", "-10<sup>9</sup> &le; nums[i] &le; 10<sup>9</sup>, sorted in non-decreasing order", "0 &le; k &le; 2 &times; 10<sup>9</sup>"],
    hints=["A set of seen values answers the question for k &gt; 0, but there is a sorted array to exploit and k = 0 needs extra care. Think about two pointers that both move forward.",
           "Let <code>i</code> point at a value <code>x</code> and <code>j</code> at the first element after <code>i</code> with <code>a[j] - a[i] &ge; k</code>. When <code>i</code> advances, can <code>j</code> ever need to move backwards?",
           "No: both pointers only move right. Skip an <code>i</code> whose value equals the previous one, force <code>j &gt; i</code>, and count when <code>a[j] - a[i] == k</code>."],
    editorial=["Walk <code>i</code> over the array but process each distinct value only once (skip <code>i</code> when <code>a[i] == a[i-1]</code>). Keep <code>j</code> as the first index after <code>i</code> with <code>a[j] - a[i] &ge; k</code>. If that difference equals <code>k</code> exactly, the value pair <code>(a[i], a[i]+k)</code> exists: count it.",
               "Because the array is sorted, a larger <code>i</code> never needs an earlier <code>j</code>, so <code>j</code> never moves back and both pointers travel at most n steps: O(n) time, O(1) space. Forcing <code>j &ge; i + 1</code> makes the case k = 0 work by itself: it only counts when another element equal to <code>a[i]</code> follows it.",
               "A hash set also works in O(n) but needs O(n) memory and a separate branch for k = 0."],
    time="O(n)", space="O(1)",
    solution='''def countDiffPairs(nums, k):
    n = len(nums)
    count = 0
    j = 0
    for i in range(n):
        if i > 0 and nums[i] == nums[i - 1]:
            continue
        if j < i + 1:
            j = i + 1
        while j < n and nums[j] - nums[i] < k:
            j += 1
        if j < n and nums[j] - nums[i] == k:
            count += 1
    return count
''',
    tests=[[[1, 1, 3, 3, 5, 5, 5, 7], 2], [[], 0], [[4], 0], [[4, 4], 0], [[4, 5], 0], [[1, 2, 3, 4, 5], 1], [[1, 2, 3, 4, 5], 0],
           [[1, 1, 1, 2, 2], 0], [[1, 3, 5], 10], [[-3, -1, -1, 1, 3, 3], 2], [[-10 ** 9, 10 ** 9], 2 * 10 ** 9],
           [[-10 ** 9, 0, 0, 10 ** 9], 10 ** 9], [[2, 2, 2, 2], 0], [[0, 0, 7, 7, 14, 14], 7]],
)
_r = rnd(7003)
p["tests"].append([sorted(_r.randint(-3000, 3000) for _ in range(5000)), 7])
p["tests"].append([sorted(_r.randint(-10 ** 9, 10 ** 9) for _ in range(3000)), 0])
p["tests"].append([sorted(_r.randint(0, 2500) for _ in range(5000)), 0])


def b_diff(nums, k):
    n = len(nums)
    return len({(nums[i], nums[j]) for i in range(n) for j in range(i + 1, n) if nums[j] - nums[i] == k})


def g_diff(r):
    return [sorted(gen_arr(r, -6, 6, 0, 11)), r.randint(0, 6)]


def v_diff(tests):
    for t in tests:
        nums, k = t["args"]
        assert 0 <= len(nums) <= 10000 and _sorted_ok(nums)
        assert all(-10 ** 9 <= x <= 10 ** 9 for x in nums)
        assert 0 <= k <= 2 * 10 ** 9


CHECKS["count-value-pairs-with-difference-k"] = (b_diff, g_diff, "exact")
VALIDATE["count-value-pairs-with-difference-k"] = v_diff

p = add(
    id="three-sum-closest", title="3Sum Closest", diff="Medium", topic=TOPIC,
    fn="threeSumClosest", params=[("nums", "int[]"), ("target", "int")], ret="int", cmp="exact",
    desc="<p>Given an integer array <code>nums</code> with at least three elements (any order) and an integer <code>target</code>, choose three elements at three different positions so that their sum is as close to <code>target</code> as possible. Return that sum.</p><p>If two different sums are equally close to the target, return the <strong>smaller</strong> one.</p><pre>nums = [4, -2, 7, 1, -5], target = 10\nbest triple: -2 + 4 + 7 = 9 (distance 1); 1 + 4 + 7 = 12 is farther away\nresult = 9</pre>",
    constraints=["3 &le; nums.length &le; 800", "-10<sup>6</sup> &le; nums[i] &le; 10<sup>6</sup>", "-3 &times; 10<sup>6</sup> &le; target &le; 3 &times; 10<sup>6</sup>"],
    hints=["Three nested loops give O(n&sup3;). Fix one element and see what is left to solve.",
           "With the first element fixed, you need the pair among the remaining elements whose sum is closest to <code>target - nums[i]</code>. That is the sorted closest-pair problem.",
           "Sort once. For every index <code>i</code> run <code>lo = i + 1</code>, <code>hi = n - 1</code>, compare each triple sum with the best one by <code>(distance, sum)</code>, and move the pointer that brings the sum toward the target."],
    editorial=["Sort the array. For each index <code>i</code>, sweep the suffix after it with two pointers <code>lo</code> and <code>hi</code>. The current sum is <code>s = a[i] + a[lo] + a[hi]</code>. Compare the key <code>(|s - target|, s)</code> to the best key found so far; the second component implements the tie rule. If <code>s &lt; target</code> increase <code>lo</code>, if <code>s &gt; target</code> decrease <code>hi</code>, and if <code>s == target</code> return it at once.",
               "The discarding argument is the same as for two sums: if <code>s</code> is below the target, no partner of <code>a[lo]</code> inside the window can give a bigger sum than <code>a[hi]</code> does, so <code>a[lo]</code> is useless for this <code>i</code>. Total time is O(n&sup2;) with O(1) extra space, versus O(n&sup3;) for brute force.",
               "Pitfall: remember that the three elements must come from different positions, so the pointers always stay strictly to the right of <code>i</code> and <code>lo &lt; hi</code>."],
    time="O(n&sup2;)", space="O(1) extra",
    solution='''def threeSumClosest(nums, target):
    a = sorted(nums)
    n = len(a)
    best = None
    for i in range(n - 2):
        lo, hi = i + 1, n - 1
        while lo < hi:
            s = a[i] + a[lo] + a[hi]
            key = (abs(s - target), s)
            if best is None or key < best:
                best = key
            if s == target:
                return s
            if s < target:
                lo += 1
            else:
                hi -= 1
    return best[1]
''',
    tests=[[[4, -2, 7, 1, -5], 10], [[0, 0, 0], 1], [[1, 1, 1], 0], [[-1, 2, 1, -4], 1], [[1, 2, 3], 3],
           [[5, 5, 5, 5], 14], [[-10 ** 6, -10 ** 6, -10 ** 6, 10 ** 6], 3 * 10 ** 6], [[10 ** 6, 10 ** 6, 10 ** 6], -3 * 10 ** 6],
           [[-5, -3, 2, 4, 9], 0], [[0, 2, 4, 6], 5], [[3, -3, 8, -8, 1], 100], [[1, 3, 5, 7, 9], 10], [[-2, 0, 2, 10], 7]],
)
_r = rnd(7004)
p["tests"].append([[_r.randint(-10 ** 6, 10 ** 6) for _ in range(800)], 123456])
p["tests"].append([[_r.randint(-10 ** 6, 10 ** 6) for _ in range(800)], -2999999])
p["tests"].append([[_r.randint(-500, 500) * 1000 for _ in range(600)], 1])


def b_closest3(nums, target):
    return min((abs(sum(c) - target), sum(c)) for c in combinations(nums, 3))[1]


def g_closest3(r):
    return [gen_arr(r, -9, 9, 3, 9), r.randint(-20, 20)]


def v_closest3(tests):
    for t in tests:
        nums, target = t["args"]
        assert 3 <= len(nums) <= 800
        assert all(-10 ** 6 <= x <= 10 ** 6 for x in nums)
        assert -3 * 10 ** 6 <= target <= 3 * 10 ** 6


CHECKS["three-sum-closest"] = (b_closest3, g_closest3, "exact")
VALIDATE["three-sum-closest"] = v_closest3

p = add(
    id="three-sum-smaller-count", title="Count Triplets With Sum Below Target", diff="Medium", topic=TOPIC,
    fn="countTripletsBelow", params=[("nums", "int[]"), ("target", "int")], ret="int", cmp="exact",
    desc="<p>Given an integer array <code>nums</code> (any order) and an integer <code>target</code>, count the triples of positions <code>i &lt; j &lt; k</code> with <code>nums[i] + nums[j] + nums[k] &lt; target</code>.</p><pre>nums = [-2, 0, 1, 3], target = 2\nvalid triples: (-2,0,1) and (-2,0,3)\nresult = 2</pre><p>The triples are counted by position, so repeated values produce separate triples.</p>",
    constraints=["0 &le; nums.length &le; 800", "-10<sup>6</sup> &le; nums[i] &le; 10<sup>6</sup>", "-3 &times; 10<sup>6</sup> &le; target &le; 3 &times; 10<sup>6</sup>"],
    hints=["Enumerating all triples is O(n&sup3;). The condition only depends on the values, not on their order.",
           "Sort the array and fix the smallest element of the triple by index. Now count the pairs after it whose sum is below <code>target - a[i]</code>.",
           "For the pair part, use <code>lo</code> and <code>hi</code>: if <code>a[i] + a[lo] + a[hi] &lt; target</code>, then <code>a[lo]</code> works with every index in <code>lo+1..hi</code>, which adds <code>hi - lo</code> triples at once."],
    editorial=["After sorting, every triple of positions maps to a triple of sorted positions with the same values, so counting sorted triples <code>i &lt; lo &lt; hi</code> is enough. For a fixed <code>i</code>, let <code>lo = i + 1</code>, <code>hi = n - 1</code>. If the sum is below the target, all middle indices <code>lo+1..hi</code> are at most <code>a[hi]</code>, so the pairs <code>(lo, lo+1), ..., (lo, hi)</code> all qualify: add <code>hi - lo</code> and advance <code>lo</code>. Otherwise decrease <code>hi</code>.",
               "The inner sweep is linear, so the total is O(n&sup2;) after the sort. This is the &ldquo;count under a bound&rdquo; version of 3Sum: because we only need a number, we can add whole ranges at once instead of listing triples, and duplicates need no special handling."],
    time="O(n&sup2;)", space="O(1) extra",
    solution='''def countTripletsBelow(nums, target):
    a = sorted(nums)
    n = len(a)
    count = 0
    for i in range(n - 2):
        lo, hi = i + 1, n - 1
        while lo < hi:
            if a[i] + a[lo] + a[hi] < target:
                count += hi - lo
                lo += 1
            else:
                hi -= 1
    return count
''',
    tests=[[[-2, 0, 1, 3], 2], [[], 0], [[1], 5], [[1, 2], 100], [[1, 2, 3], 6], [[1, 2, 3], 7], [[0, 0, 0, 0], 1], [[0, 0, 0, 0], 0],
           [[-5, -5, -5, -5, -5], -14], [[10 ** 6, 10 ** 6, 10 ** 6, -10 ** 6], 10 ** 6], [[3, -1, 4, -1, 5, -9, 2, 6], 4],
           [[10 ** 6] * 4 + [-10 ** 6], 3 * 10 ** 6]],
)
_r = rnd(7005)
p["tests"].append([[_r.randint(-10 ** 6, 10 ** 6) for _ in range(800)], 0])
p["tests"].append([[_r.randint(-10 ** 6, 10 ** 6) for _ in range(800)], 1000000])
p["tests"].append([[_r.randint(-20, 20) for _ in range(700)], -3])


def b_smaller(nums, target):
    return sum(1 for c in combinations(nums, 3) if sum(c) < target)


def v_smaller(tests):
    for t in tests:
        nums, target = t["args"]
        assert 0 <= len(nums) <= 800
        assert all(-10 ** 6 <= x <= 10 ** 6 for x in nums)
        assert -3 * 10 ** 6 <= target <= 3 * 10 ** 6


CHECKS["three-sum-smaller-count"] = (b_smaller, lambda r: [gen_arr(r, -7, 7, 0, 10), r.randint(-12, 12)], "exact")
VALIDATE["three-sum-smaller-count"] = v_smaller

p = add(
    id="valid-triangle-triplets-count", title="Count Triangle Triplets", diff="Medium", topic=TOPIC,
    fn="countTriangles", params=[("sides", "int[]")], ret="int", cmp="exact",
    desc="<p>The array <code>sides</code> holds non-negative stick lengths. Count the triples of positions <code>i &lt; j &lt; k</code> such that the three lengths can be the sides of a triangle with positive area, that is, each length is strictly smaller than the sum of the other two.</p><pre>sides = [2, 2, 3, 4]\nvalid triples: (2,2,3), (2,3,4), (2,3,4)\nresult = 3</pre><p>Sticks of length 0 never take part in a valid triangle. Equal lengths at different positions count as different sticks.</p>",
    constraints=["0 &le; sides.length &le; 1,000", "0 &le; sides[i] &le; 10<sup>6</sup>"],
    hints=["For three lengths <code>a &le; b &le; c</code>, which of the three triangle inequalities is the only one that can fail?",
           "Only <code>a + b &gt; c</code> matters (the others hold automatically for sorted values). Sort the array and fix the longest side <code>c</code> by index.",
           "With <code>c = s[k]</code> fixed, use <code>i = 0</code> and <code>j = k - 1</code>. If <code>s[i] + s[j] &gt; s[k]</code>, all of <code>s[i..j-1]</code> pair with <code>s[j]</code>: add <code>j - i</code> and decrement <code>j</code>. Otherwise increment <code>i</code>."],
    editorial=["Sort the lengths. For sorted values <code>a &le; b &le; c</code>, the inequalities <code>a + c &gt; b</code> and <code>b + c &gt; a</code> are automatic when the lengths are positive, so the triple is valid exactly when <code>a + b &gt; c</code>. With zeros, <code>a = 0</code> gives <code>b &gt; c</code>, which contradicts <code>b &le; c</code>, so zero sticks are rejected by the same test.",
               "Fix the longest side at sorted index <code>k</code> and search the prefix <code>0..k-1</code> for pairs <code>(i, j)</code> with <code>s[i] + s[j] &gt; s[k]</code>. Start with <code>i = 0</code>, <code>j = k - 1</code>. If <code>s[i] + s[j] &gt; s[k]</code>, then every index between <code>i</code> and <code>j - 1</code> also works with <code>j</code> (they are at least as big as <code>s[i]</code>), which adds <code>j - i</code> pairs; then <code>j</code> is done. If the sum is not big enough, <code>i</code> can never help with a partner at most <code>s[j]</code>, so advance <code>i</code>.",
               "This is O(n&sup2;) in total (a linear sweep for each of the n choices of <code>k</code>) plus the sort."],
    time="O(n&sup2;)", space="O(1) extra",
    solution='''def countTriangles(sides):
    s = sorted(sides)
    n = len(s)
    count = 0
    for k in range(2, n):
        i, j = 0, k - 1
        while i < j:
            if s[i] + s[j] > s[k]:
                count += j - i
                j -= 1
            else:
                i += 1
    return count
''',
    tests=[[[2, 2, 3, 4]], [[]], [[5]], [[3, 4]], [[3, 4, 5]], [[1, 2, 3]], [[0, 0, 0]], [[0, 5, 5]], [[7, 7, 7, 7]],
           [[1, 1, 1, 100, 100, 100]], [[10 ** 6, 10 ** 6, 1]], [[1, 2, 4, 8, 16, 32]], [[4, 2, 3, 4, 6, 1, 9, 8]]],
)
_r = rnd(7006)
p["tests"].append([[_r.randint(0, 10 ** 6) for _ in range(900)]])
p["tests"].append([[_r.randint(1, 100) for _ in range(1000)]])
p["tests"].append([[2 ** _r.randint(0, 19) for _ in range(800)]])


def b_tri(sides):
    cnt = 0
    for x, y, z in combinations(sides, 3):
        if x + y > z and x + z > y and y + z > x:
            cnt += 1
    return cnt


def v_tri(tests):
    for t in tests:
        s = t["args"][0]
        assert 0 <= len(s) <= 1000
        assert all(0 <= x <= 10 ** 6 for x in s)


CHECKS["valid-triangle-triplets-count"] = (b_tri, lambda r: [gen_arr(r, 0, 9, 0, 11)], "exact")
VALIDATE["valid-triangle-triplets-count"] = v_tri

p = add(
    id="count-pairs-sum-in-range", title="Count Pairs With Sum in a Range", diff="Medium", topic=TOPIC,
    fn="countPairsInRange", params=[("nums", "int[]"), ("lower", "int"), ("upper", "int")], ret="int", cmp="exact",
    desc="<p>Given an integer array <code>nums</code> (any order) and two integers <code>lower &le; upper</code>, count the pairs of positions <code>i &lt; j</code> with <code>lower &le; nums[i] + nums[j] &le; upper</code>.</p><pre>nums = [1, 7, 3, 5, 2], lower = 6, upper = 9\npairs: 1+5=6, 1+7=8, 7+2=9, 3+5=8, 5+2=7\nresult = 5</pre>",
    constraints=["0 &le; nums.length &le; 10,000", "-10<sup>9</sup> &le; nums[i] &le; 10<sup>9</sup>", "-2 &times; 10<sup>9</sup> &le; lower &le; upper &le; 2 &times; 10<sup>9</sup>"],
    hints=["Counting pairs with a sum between two bounds is awkward directly. Can you express it using counts of the form &ldquo;sum at most X&rdquo;?",
           "The number of pairs with sum in <code>[lower, upper]</code> equals (pairs with sum &le; upper) minus (pairs with sum &le; lower - 1).",
           "Sort once. To count pairs with sum &le; X, put <code>lo</code> at the start and <code>hi</code> at the end: if <code>a[lo] + a[hi] &le; X</code> add <code>hi - lo</code> and move <code>lo</code>; else move <code>hi</code>."],
    editorial=["Define <code>f(X)</code> = the number of pairs with sum at most <code>X</code>. All pairs with a sum in the range are exactly those counted by <code>f(upper)</code> but not by <code>f(lower - 1)</code>, because the sums are integers. So the answer is <code>f(upper) - f(lower - 1)</code>.",
               "Compute <code>f</code> on the sorted array with two pointers: when <code>a[lo] + a[hi] &le; X</code>, element <code>lo</code> pairs with all of <code>lo+1..hi</code>, so add <code>hi - lo</code> and advance <code>lo</code>; otherwise <code>a[hi]</code> is too large for every remaining partner and is dropped. Each call is O(n), so the whole algorithm is O(n log n) for the sort plus O(n).",
               "Binary searching the partner range of every element gives the same answer in O(n log n) too; the two-pointer sweep avoids the logarithm after sorting. The count of pairs fits in 32 bits (at most about 5 &times; 10<sup>7</sup>)."],
    time="O(n log n)", space="O(1) extra",
    solution='''def countPairsInRange(nums, lower, upper):
    a = sorted(nums)

    def at_most(x):
        lo, hi = 0, len(a) - 1
        count = 0
        while lo < hi:
            if a[lo] + a[hi] <= x:
                count += hi - lo
                lo += 1
            else:
                hi -= 1
        return count

    return at_most(upper) - at_most(lower - 1)
''',
    tests=[[[1, 7, 3, 5, 2], 6, 9], [[], 0, 0], [[5], 0, 10], [[1, 1], 2, 2], [[1, 1], 3, 4], [[0, 0, 0, 0], 0, 0],
           [[-4, -1, 0, 3, 8], -1, 3], [[4, 4, 4], 8, 8], [[10 ** 9, 10 ** 9, -10 ** 9, -10 ** 9], 0, 0],
           [[10 ** 9, 10 ** 9, -10 ** 9, -10 ** 9], -2 * 10 ** 9, 2 * 10 ** 9], [[10 ** 9, 10 ** 9, 5], 2 * 10 ** 9, 2 * 10 ** 9],
           [[3, 9, 6, 12, 15, 1], 10, 13]],
)
_r = rnd(7007)
p["tests"].append([[_r.randint(-10 ** 6, 10 ** 6) for _ in range(5000)], -100000, 250000])
p["tests"].append([[_r.randint(-10 ** 9, 10 ** 9) for _ in range(3000)], -10 ** 8, 10 ** 9])
p["tests"].append([[_r.randint(0, 60) for _ in range(4000)], 50, 70])


def b_range(nums, lower, upper):
    n = len(nums)
    return sum(1 for i in range(n) for j in range(i + 1, n) if lower <= nums[i] + nums[j] <= upper)


def g_range(r):
    lo = r.randint(-12, 12)
    return [gen_arr(r, -8, 8, 0, 10), lo, lo + r.randint(0, 10)]


def v_range(tests):
    for t in tests:
        nums, lower, upper = t["args"]
        assert 0 <= len(nums) <= 10000
        assert all(-10 ** 9 <= x <= 10 ** 9 for x in nums)
        assert -2 * 10 ** 9 <= lower <= upper <= 2 * 10 ** 9


CHECKS["count-pairs-sum-in-range"] = (b_range, g_range, "exact")
VALIDATE["count-pairs-sum-in-range"] = v_range

p = add(
    id="min-spread-triple-three-sorted-arrays", title="Smallest Spread Across Three Sorted Arrays", diff="Medium", topic=TOPIC, tier="extra",
    fn="minSpreadTriple", params=[("a", "int[]"), ("b", "int[]"), ("c", "int[]")], ret="int", cmp="exact",
    desc="<p>You get three non-empty integer arrays <code>a</code>, <code>b</code>, <code>c</code>, each sorted in non-decreasing order. Choose one element from each array and let the <em>spread</em> of the choice be <code>max - min</code> of the three chosen values.</p><p>Return the smallest possible spread.</p><pre>a = [1, 4, 10], b = [2, 15, 20], c = [10, 12]\nchoose 10, 15, 10 &rarr; spread 15 - 10 = 5\nresult = 5</pre>",
    constraints=["1 &le; a.length, b.length, c.length &le; 3,000", "-10<sup>9</sup> &le; every value &le; 10<sup>9</sup>", "Each array is sorted in non-decreasing order"],
    hints=["Trying all triples costs the product of the lengths. Use the sortedness: start with the three smallest elements.",
           "In the current triple, the minimum element is the one that limits the spread. Which pointer should move to have any chance of improving?",
           "Always advance the pointer that points at the current minimum (moving the others can only increase the maximum). Record <code>max - min</code> at every step and stop when one array is exhausted."],
    editorial=["Keep one pointer per array, all starting at 0. At every step compute the spread of the three current values and update the best. Then advance the pointer whose value is the smallest of the three.",
               "Why this is safe: let <code>m</code> be the current minimum, belonging to array X. Any triple that uses this element of X together with later elements of the other two arrays has a maximum at least as large as today's maximum, and the same minimum <code>m</code> (or smaller), so its spread is no better than today's. The element is therefore finished and can be skipped without losing the optimum.",
               "Every step advances one pointer, so there are at most <code>|a| + |b| + |c|</code> steps: O(n) time, O(1) space. The same idea, extended to k arrays with a heap, gives the classic &ldquo;smallest range covering elements from k lists&rdquo; problem."],
    time="O(|a| + |b| + |c|)", space="O(1)",
    solution='''def minSpreadTriple(a, b, c):
    i = j = k = 0
    best = None
    while i < len(a) and j < len(b) and k < len(c):
        x, y, z = a[i], b[j], c[k]
        lo, hi = min(x, y, z), max(x, y, z)
        if best is None or hi - lo < best:
            best = hi - lo
        if best == 0:
            break
        if x == lo:
            i += 1
        elif y == lo:
            j += 1
        else:
            k += 1
    return best
''',
    tests=[[[1, 4, 10], [2, 15, 20], [10, 12]], [[5], [5], [5]], [[1], [100], [50]], [[1, 2, 3], [4, 5, 6], [7, 8, 9]],
           [[-5, 0, 5], [-4, 1, 6], [-3, 2, 7]], [[1, 1, 1], [1, 1], [1]], [[0, 10 ** 9], [-10 ** 9, 0], [10 ** 9]],
           [[-10 ** 9], [10 ** 9], [0]], [[3, 3, 3, 9], [9, 9], [1, 2, 9]], [[1, 100, 200], [50, 101, 300], [99, 150, 400]],
           [[7, 8], [1, 2, 3, 4, 5, 6], [10, 11, 12]]],
)
_r = rnd(7008)
p["tests"].append([sorted(_r.randint(-10 ** 9, 10 ** 9) for _ in range(1000)), sorted(_r.randint(-10 ** 9, 10 ** 9) for _ in range(800)),
                   sorted(_r.randint(-10 ** 9, 10 ** 9) for _ in range(1200))])
p["tests"].append([sorted(_r.randint(0, 10 ** 6) * 2 for _ in range(2500)), sorted(_r.randint(0, 10 ** 6) * 2 + 1 for _ in range(2500)),
                   sorted(_r.randint(10 ** 6, 2 * 10 ** 6) for _ in range(2500))])


def b_spread(a, b, c):
    return min(max(x, y, z) - min(x, y, z) for x in a for y in b for z in c)


def g_spread(r):
    return [sorted(gen_arr(r, -12, 12, 1, 6)) for _ in range(3)]


def v_spread(tests):
    for t in tests:
        for arr in t["args"]:
            assert 1 <= len(arr) <= 3000 and _sorted_ok(arr)
            assert all(-10 ** 9 <= x <= 10 ** 9 for x in arr)


CHECKS["min-spread-triple-three-sorted-arrays"] = (b_spread, g_spread, "exact")
VALIDATE["min-spread-triple-three-sorted-arrays"] = v_spread


# ---------------------------------------------------------------- HARD

p = add(
    id="kth-smallest-pair-sum-in-array", title="K-th Smallest Pair Sum", diff="Hard", topic=TOPIC, tier="extra",
    fn="kthSmallestPairSum", params=[("nums", "int[]"), ("k", "int")], ret="int", cmp="exact",
    desc="<p>Consider the sums <code>nums[i] + nums[j]</code> over all pairs of positions <code>i &lt; j</code>. Sort these sums in non-decreasing order (equal sums are listed as many times as they occur) and return the <code>k</code>-th one, counting from 1.</p><pre>nums = [1, 4, 2, 3], k = 4\nall pair sums sorted: 3, 4, 5, 5, 6, 7\nresult = 5</pre><p>There can be about n&sup2;/2 pair sums, so listing them is too slow.</p>",
    constraints=["2 &le; nums.length &le; 8,000", "-10<sup>9</sup> &le; nums[i] &le; 10<sup>9</sup>", "1 &le; k &le; nums.length &times; (nums.length - 1) / 2"],
    hints=["Generating and sorting all pair sums costs O(n&sup2; log n) time and O(n&sup2;) memory. Try to avoid listing them.",
           "Binary search on the answer value <code>x</code>: if you can count how many pair sums are at most <code>x</code>, the k-th smallest is the smallest <code>x</code> whose count is at least <code>k</code>.",
           "Count pairs with sum &le; x on the sorted array with two pointers in O(n): as <code>i</code> grows, the largest valid partner index <code>j</code> only moves left."],
    editorial=["Sort <code>nums</code>. Define <code>count(x)</code> as the number of pairs <code>i &lt; j</code> with sum at most <code>x</code>; it is non-decreasing in <code>x</code>. The answer is the smallest <code>x</code> with <code>count(x) &ge; k</code>, and it is always an actual pair sum. So binary search on <code>x</code> between the smallest possible sum <code>a[0] + a[1]</code> and the largest <code>a[n-2] + a[n-1]</code>.",
               "To evaluate <code>count(x)</code> keep <code>j</code> at the last index and sweep <code>i</code> from the left: while <code>a[i] + a[j] &gt; x</code> decrease <code>j</code>; if <code>j &gt; i</code>, the element <code>i</code> pairs with every index in <code>i+1..j</code>, so add <code>j - i</code>. Since <code>a[i]</code> grows with <code>i</code>, the boundary <code>j</code> never moves right, and one evaluation takes O(n).",
               "Total time is O(n log n) for the sort plus O(n log R) for the search, where R &asymp; 4 &times; 10<sup>9</sup> is the range of sums (about 32 iterations). Memory is O(1) extra. The same &ldquo;binary search on the answer + two pointers to count&rdquo; template solves k-th smallest pair distance and k-th smallest in sorted matrices."],
    time="O(n log n + n log R)", space="O(1) extra",
    solution='''def kthSmallestPairSum(nums, k):
    a = sorted(nums)
    n = len(a)

    def count_at_most(x):
        total = 0
        j = n - 1
        for i in range(n - 1):
            while j > i and a[i] + a[j] > x:
                j -= 1
            if j <= i:
                break
            total += j - i
        return total

    lo, hi = a[0] + a[1], a[-1] + a[-2]
    while lo < hi:
        mid = (lo + hi) // 2
        if count_at_most(mid) >= k:
            hi = mid
        else:
            lo = mid + 1
    return lo
''',
    tests=[[[1, 4, 2, 3], 4], [[1, 4, 2, 3], 1], [[1, 4, 2, 3], 6], [[5, 9], 1], [[-3, -3], 1], [[0, 0, 0], 2], [[2, 2, 2, 2], 6],
           [[-5, 8, -1, 3, 0, 7], 7], [[-5, 8, -1, 3, 0, 7], 15], [[10 ** 9, 10 ** 9, -10 ** 9, -10 ** 9], 3],
           [[10 ** 9, 10 ** 9, -10 ** 9, -10 ** 9], 6], [[1, 2, 3, 4, 5, 6, 7, 8], 14]],
)
_r = rnd(7009)
_a = [_r.randint(-10 ** 9, 10 ** 9) for _ in range(3500)]
p["tests"].append([_a, 3500 * 3499 // 4])
_a = [_r.randint(-10 ** 5, 10 ** 5) for _ in range(5000)]
p["tests"].append([_a, 7777777])
_a = [_r.randint(0, 30) for _ in range(4000)]
p["tests"].append([_a, 1000])


def b_kth_sum(nums, k):
    n = len(nums)
    return sorted(nums[i] + nums[j] for i in range(n) for j in range(i + 1, n))[k - 1]


def g_kth_sum(r):
    a = gen_arr(r, -8, 8, 2, 9)
    return [a, r.randint(1, len(a) * (len(a) - 1) // 2)]


def v_kth_sum(tests):
    for t in tests:
        nums, k = t["args"]
        n = len(nums)
        assert 2 <= n <= 8000
        assert all(-10 ** 9 <= x <= 10 ** 9 for x in nums)
        assert 1 <= k <= n * (n - 1) // 2


CHECKS["kth-smallest-pair-sum-in-array"] = (b_kth_sum, g_kth_sum, "exact")
VALIDATE["kth-smallest-pair-sum-in-array"] = v_kth_sum

p = add(
    id="closest-subset-sum-to-goal", title="Closest Subset Sum to a Goal", diff="Hard", topic=TOPIC, tier="extra",
    fn="minSubsetSumGap", params=[("nums", "int[]"), ("goal", "int")], ret="int", cmp="exact",
    desc="<p>You may pick any subset of <code>nums</code> (the empty subset is allowed, its sum is 0). Let <code>S</code> be the sum of the picked elements. Return the minimum possible value of <code>|S - goal|</code>.</p><pre>nums = [7, -9, 15, -2], goal = -5\nbest subset: {-9, 7, -2} with sum -4\nresult = 1</pre><p>Elements can be negative, so the usual knapsack table over sums does not apply.</p>",
    constraints=["0 &le; nums.length &le; 30", "-10<sup>7</sup> &le; nums[i] &le; 10<sup>7</sup>", "-10<sup>9</sup> &le; goal &le; 10<sup>9</sup>"],
    hints=["There are 2<sup>30</sup> subsets, which is too many to enumerate, and the sums are too large for a DP table. Split the array in two halves.",
           "Each half has at most 2<sup>15</sup> subsets. Any subset of the whole array is a subset of the left half plus a subset of the right half. List the sums of both halves.",
           "Sort both lists of sums. For each left sum <code>x</code>, you need the right sum closest to <code>goal - x</code>. As <code>x</code> increases, that target decreases, so a pointer on the right list only moves down: two pointers."],
    editorial=["This is the meet-in-the-middle technique. Split <code>nums</code> into a left half and a right half of at most 15 elements each and list all subset sums of each half (at most 32,768 values per list). A subset of the whole array corresponds to exactly one pair (left sum, right sum), and the total is their sum.",
               "Sort both lists, <code>L</code> ascending and <code>R</code> ascending. For each <code>x</code> in <code>L</code> in increasing order, we want the value <code>y</code> in <code>R</code> closest to <code>goal - x</code>. Keep a pointer <code>j</code> at the largest index with <code>x + R[j] &le; goal</code>; as <code>x</code> grows, <code>j</code> can only move left, so the pointer travels at most |R| steps in total. The best partner is either <code>R[j]</code> (just below or on the goal) or <code>R[j+1]</code> (just above it); evaluate both and keep the smallest distance.",
               "Time is O(2<sup>n/2</sup> &middot; n) for generating and sorting the lists, plus O(2<sup>n/2</sup>) for the sweep, instead of O(2<sup>n</sup>). Memory is O(2<sup>n/2</sup>). Initialise the answer with <code>|goal|</code>, the empty subset, which also covers an empty array."],
    time="O(2^(n/2) * n)", space="O(2^(n/2))",
    solution='''def minSubsetSumGap(nums, goal):
    def subset_sums(arr):
        sums = [0]
        for v in arr:
            sums += [s + v for s in sums]
        sums.sort()
        return sums

    mid = len(nums) // 2
    left = subset_sums(nums[:mid])
    right = subset_sums(nums[mid:])
    best = abs(goal)
    j = len(right) - 1
    for x in left:
        while j >= 0 and x + right[j] > goal:
            j -= 1
        if j >= 0:
            best = min(best, goal - x - right[j])
        if j + 1 < len(right):
            best = min(best, x + right[j + 1] - goal)
    return best
''',
    tests=[[[7, -9, 15, -2], -5], [[], 17], [[], -4], [[5], 5], [[5], 3], [[5], 100], [[-8], -3], [[1, 2, 3], 7], [[1, 2, 3], 4],
           [[-3, -3, -3], 1], [[10 ** 7, 10 ** 7, 10 ** 7, 10 ** 7], 10 ** 9], [[10 ** 7, -10 ** 7, 10 ** 7, -10 ** 7], -10 ** 9],
           [[3, 34, 4, 12, 5, 2], 30], [[-7, 9, 14, -20, 31, 2, 8], 1]],
)
_r = rnd(7010)
p["tests"].append([[_r.randint(-10 ** 7, 10 ** 7) for _ in range(30)], 123456789])
p["tests"].append([[_r.randint(-10 ** 7, 10 ** 7) for _ in range(30)], -33333333])
p["tests"].append([[_r.randint(1, 10 ** 7) for _ in range(28)], 987654321])


def b_subset(nums, goal):
    best = abs(goal)
    n = len(nums)
    for mask in range(1 << n):
        s = sum(nums[i] for i in range(n) if mask >> i & 1)
        best = min(best, abs(s - goal))
    return best


def g_subset(r):
    return [gen_arr(r, -15, 15, 0, 11), r.randint(-40, 40)]


def v_subset(tests):
    for t in tests:
        nums, goal = t["args"]
        assert 0 <= len(nums) <= 30
        assert all(-10 ** 7 <= x <= 10 ** 7 for x in nums)
        assert -10 ** 9 <= goal <= 10 ** 9


CHECKS["closest-subset-sum-to-goal"] = (b_subset, g_subset, "exact")
VALIDATE["closest-subset-sum-to-goal"] = v_subset

p = add(
    id="four-sum-value-multiplicity-count", title="4Sum With Multiplicity", diff="Hard", topic=TOPIC, tier="extra",
    fn="fourSumCount", params=[("arr", "int[]"), ("target", "int")], ret="int", cmp="exact",
    desc="<p>The array <code>arr</code> contains integers between 0 and 100, with many repeated values. Count the quadruples of positions <code>i &lt; j &lt; k &lt; l</code> with <code>arr[i] + arr[j] + arr[k] + arr[l] = target</code>.</p><p>Because the count can be huge, return it <strong>modulo 1,000,000,007</strong>.</p><pre>arr = [1, 1, 2, 2, 3, 3], target = 8\nvalue multisets: {1,2,2,3} (2&middot;1&middot;2 = 4 ways), {1,1,3,3} (1 way)\nresult = 5</pre>",
    constraints=["1 &le; arr.length &le; 3,000", "0 &le; arr[i] &le; 100", "0 &le; target &le; 400"],
    hints=["Quadruples of positions can be 10<sup>12</sup>, so you cannot enumerate them. But there are only 101 distinct values. Count by <em>values</em> instead of positions.",
           "Enumerate value multisets <code>a &le; b &le; c &le; d</code> with the right sum. For each, the number of position quadruples is the product, over distinct values v used m times, of <code>C(count[v], m)</code>.",
           "Loop over <code>a &le; b</code> on the list of distinct values and find the pairs <code>c &le; d</code> (with <code>c</code> at or after <code>b</code>) with <code>c + d = target - a - b</code> using two pointers from both ends of that list."],
    editorial=["Let <code>cnt[v]</code> be how many times value <code>v</code> occurs and <code>vals</code> the sorted list of distinct values (at most 101). Every position quadruple has a sorted value multiset <code>a &le; b &le; c &le; d</code>, and each multiset arises from <code>prod C(cnt[v], m_v)</code> quadruples, where <code>m_v</code> is how often <code>v</code> appears in the multiset. For example, {2,2,2,5} uses C(cnt[2], 3) &middot; cnt[5] quadruples. When a value is requested more times than it occurs, the binomial is 0.",
               "Enumerate the multisets without duplicates: choose <code>a = vals[ia]</code> and <code>b = vals[ib]</code> with <code>ib &ge; ia</code>, then find all <code>c = vals[lo]</code>, <code>d = vals[hi]</code> with <code>ib &le; lo &le; hi</code> and <code>c + d = rest</code> by moving two pointers inward: advance <code>lo</code> if the pair sum is too small, retreat <code>hi</code> if too large, and on a match record the term and move both. Distinct values guarantee each pair is found exactly once, and allowing <code>lo == hi</code> covers c = d.",
               "That is O(V<sup>2</sup>) pairs (a, b) times O(V) for the sweep, about 10<sup>5</sup> to 10<sup>6</sup> cheap steps for V = 101, independent of n. Sum the exact integer terms (Python integers do not overflow) and apply the modulus once at the end; in a fixed-width language reduce after each term."],
    time="O(V^3) with V = 101 distinct values", space="O(V)",
    solution='''def fourSumCount(arr, target):
    from collections import Counter
    from math import comb
    MOD = 1000000007
    cnt = Counter(arr)
    vals = sorted(cnt)
    m = len(vals)

    def ways(q):
        res = 1
        i = 0
        while i < 4:
            j = i
            while j < 4 and q[j] == q[i]:
                j += 1
            res *= comb(cnt[q[i]], j - i)
            if res == 0:
                return 0
            i = j
        return res

    total = 0
    for ia in range(m):
        for ib in range(ia, m):
            rest = target - vals[ia] - vals[ib]
            lo, hi = ib, m - 1
            while lo <= hi:
                s = vals[lo] + vals[hi]
                if s < rest:
                    lo += 1
                elif s > rest:
                    hi -= 1
                else:
                    total += ways((vals[ia], vals[ib], vals[lo], vals[hi]))
                    lo += 1
                    hi -= 1
    return total % MOD
''',
    tests=[[[1, 1, 2, 2, 3, 3], 8], [[1], 1], [[1, 2, 3], 6], [[0, 0, 0, 0], 0], [[0, 0, 0, 0, 0], 0], [[2, 2, 2, 2], 8],
           [[2, 2, 2, 2], 9], [[100, 100, 100, 100, 100], 400], [[100, 100, 100, 99, 99], 399], [[1, 2, 3, 4, 5, 6, 7, 8], 18],
           [[5, 5, 5, 5, 10, 10, 15, 15], 30], [[0, 100, 0, 100, 50, 50], 200]],
)
_r = rnd(7011)
p["tests"].append([[_r.randint(0, 100) for _ in range(3000)], 200])
p["tests"].append([[_r.randint(0, 100) for _ in range(3000)], 173])
p["tests"].append([[_r.randint(0, 40) for _ in range(3000)], 90])
p["tests"].append([[50] * 3000, 200])


def b_four_mult(arr, target):
    return sum(1 for c in combinations(arr, 4) if sum(c) == target) % MOD


def g_four_mult(r):
    return [gen_arr(r, 0, 6, 1, 10), r.randint(0, 24)]


def v_four_mult(tests):
    for t in tests:
        arr, target = t["args"]
        assert 1 <= len(arr) <= 3000
        assert all(0 <= x <= 100 for x in arr)
        assert 0 <= target <= 400


CHECKS["four-sum-value-multiplicity-count"] = (b_four_mult, g_four_mult, "exact")
VALIDATE["four-sum-value-multiplicity-count"] = v_four_mult
