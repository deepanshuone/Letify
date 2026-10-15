"""Problems: subarray dynamic programming (Kadane variants). See data/lib.py for the registry."""
from lib import add, rnd, CHECKS, VALIDATE, gen_arr  # noqa: F401

TOPIC = "Dynamic Programming"
NEG = float("-inf")


def _rl(r, n, lo, hi):
    return [r.randint(lo, hi) for _ in range(n)]


def _inrange(a, lo, hi):
    assert all(lo <= x <= hi for x in a), "value out of range"


# ---------------------------------------------------------------- EASY

_r = rnd(9101)
_big1 = [_rl(_r, 5000, -9999, 9999)]
_big2 = [[_r.choice([0, 0, 0, 1, -1, 2, -2]) for _ in range(6000)]]
_big3 = [[-_r.randint(1, 9999) for _ in range(3000)]]

add(
    id="maximum-subarray-bounds", title="Maximum Subarray With Boundaries", diff="Easy", topic=TOPIC,
    fn="maxSubarrayBounds", params=[("nums", "int[]")], ret="int[]", cmp="exact",
    desc="<p>Among all non-empty contiguous subarrays of <code>nums</code>, find the ones with the largest sum. Several subarrays can share that largest sum, so pick one canonically: the one with the <strong>smallest start index</strong>, and if there is still a tie, the one with the <strong>smallest end index</strong>.</p><p>Return the three numbers <code>[sum, start, end]</code>, where <code>start</code> and <code>end</code> are 0-based and inclusive.</p><p>Examples: <code>[-2, 1, -3, 4, -1, 2, 1, -5, 4]</code> gives <code>[6, 3, 6]</code>. For <code>[1, -1, 1]</code> the largest sum is 1, reached by <code>[0,0]</code>, <code>[0,2]</code> and <code>[2,2]</code>; the answer is <code>[1, 0, 0]</code>.</p>",
    constraints=["1 &le; nums.length &le; 10,000", "-10,000 &le; nums[i] &le; 10,000"],
    hints=["First compute only the best sum: let <code>cur</code> be the best sum of a subarray ending at the current index. Should the previous run be extended, or should a new run start here?",
           "A previous run is worth extending when its sum is not negative. Remember the start index of the current run alongside <code>cur</code>.",
           "Update the global answer when <code>cur</code> is larger, or when it is equal and <code>(start, end)</code> is lexicographically smaller. When the previous run sums to exactly 0, keep extending: that keeps the earlier start."],
    editorial=["This is Kadane's algorithm with bookkeeping. For every index <code>i</code>, keep the best sum <code>cur</code> of a subarray ending at <code>i</code> and the smallest start <code>s</code> that achieves it. If the run before <code>i</code> has sum <code>&lt; 0</code>, it only hurts, so restart at <code>i</code>. Otherwise extend it. When the earlier run has sum exactly 0, extending gives the same total as restarting but with a smaller start, which is what the tie rule wants.",
               "Any subarray with the globally largest sum must also be the best subarray ending at its own last index (otherwise a better subarray would exist), so looking at the best candidate per end index loses nothing. Compare candidates by <code>(sum desc, start asc, end asc)</code>. One pass, O(n) time and O(1) space."],
    time="O(n)", space="O(1)",
    solution='''def maxSubarrayBounds(nums):
    cur = nums[0]
    start = 0
    best = (-cur, 0, 0)
    for i in range(1, len(nums)):
        if cur < 0:
            cur = nums[i]
            start = i
        else:
            cur += nums[i]
        cand = (-cur, start, i)
        if cand < best:
            best = cand
    return [-best[0], best[1], best[2]]
''',
    tests=[[[-2, 1, -3, 4, -1, 2, 1, -5, 4]], [[1, -1, 1]], [[5]], [[-5]], [[0, 0, 0]], [[-3, -1, -1]], [[0, 0, -1]],
           [[2, -2, 2, -2, 2]], [[-1, 0, 0, -1, 0]], [[1, 2, 3, 4]], [[3, -3, 3, -3, 3, -3]], [[-1, 2, -2, 2, -1, 1]],
           _big1, _big2, _big3],
)


def _b_bounds(nums):
    best = None
    n = len(nums)
    for i in range(n):
        s = 0
        for j in range(i, n):
            s += nums[j]
            if best is None or s > best[0]:
                best = (s, i, j)
    return list(best)


def _v_bounds(tests):
    for t in tests:
        a = t["args"][0]
        assert 1 <= len(a) <= 10000
        _inrange(a, -10000, 10000)


CHECKS["maximum-subarray-bounds"] = (_b_bounds, lambda r: [gen_arr(r, -4, 4, 1, 9)], "exact")
VALIDATE["maximum-subarray-bounds"] = _v_bounds

# ------------------------------------------------------------------

_r = rnd(9102)
_big1 = [_rl(_r, 5000, -9999, 9999)]
_big2 = [[_r.randint(1, 3) * (1 if i % 2 else -1) for i in range(7000)]]
_big3 = [[0] * 4000]

add(
    id="max-absolute-subarray-sum", title="Largest Absolute Subarray Sum", diff="Easy", topic=TOPIC,
    fn="maxAbsoluteSubarraySum", params=[("nums", "int[]")], ret="int", cmp="exact",
    desc="<p>For a non-empty contiguous subarray, look at the <em>absolute value</em> of its sum. Return the largest such absolute value over all non-empty subarrays of <code>nums</code>.</p><p>Examples: <code>[1, -3, 2, 3, -4]</code> gives <code>5</code> (the subarray <code>[2, 3]</code>); <code>[-5, 2, -4]</code> gives <code>7</code> (the whole array, sum <code>-7</code>).</p>",
    constraints=["1 &le; nums.length &le; 10,000", "-10,000 &le; nums[i] &le; 10,000"],
    hints=["The absolute value of a sum is large when the sum is very positive or very negative. Solve the two cases separately.",
           "The largest positive sum is classic Kadane. The most negative sum is the same idea with min instead of max.",
           "Alternatively use prefix sums (including the empty prefix 0): a subarray sum is <code>P[j] - P[i]</code>, so the answer is <code>max(P) - min(P)</code>."],
    editorial=["Run Kadane twice: once tracking the maximum sum of a subarray ending at each index, once tracking the minimum. The answer is <code>max(maxSum, -minSum)</code>.",
               "A neater view uses prefix sums <code>P[0] = 0, P[k] = nums[0] + ... + nums[k-1]</code>. Every subarray sum equals <code>P[j] - P[i]</code> with <code>i &lt; j</code>, so the largest absolute value is the gap between the largest and the smallest prefix sum. If both extremes sit at the same position then all prefixes are equal, every element is 0 and the answer 0 is still right. One pass, O(n) time, O(1) space."],
    time="O(n)", space="O(1)",
    solution='''def maxAbsoluteSubarraySum(nums):
    p = lo = hi = 0
    for x in nums:
        p += x
        if p < lo:
            lo = p
        if p > hi:
            hi = p
    return hi - lo
''',
    tests=[[[1, -3, 2, 3, -4]], [[-5, 2, -4]], [[7]], [[-7]], [[0]], [[0, 0, 0]], [[3, 3, 3]], [[-1, -2, -3, 4]],
           [[5, -5, 5, -5]], [[2, -1, 2, -1, 2]], [[-10000, 10000, -10000]], _big1, _big2, _big3],
)


def _b_abs(nums):
    n = len(nums)
    best = 0
    for i in range(n):
        s = 0
        for j in range(i, n):
            s += nums[j]
            best = max(best, abs(s))
    return best


def _v_abs(tests):
    for t in tests:
        a = t["args"][0]
        assert 1 <= len(a) <= 10000
        _inrange(a, -10000, 10000)


CHECKS["max-absolute-subarray-sum"] = (_b_abs, lambda r: [gen_arr(r, -6, 6, 1, 9)], "exact")
VALIDATE["max-absolute-subarray-sum"] = _v_abs

# ---------------------------------------------------------------- MEDIUM

_r = rnd(9103)
_big1 = [_rl(_r, 5000, -9999, 9999)]
_big2 = [[_r.choice([-1, -1, -2, -3, 1]) * _r.randint(1, 50) for _ in range(6000)]]
_big3 = [[-_r.randint(1, 9999) for _ in range(3000)]]

add(
    id="max-subarray-sum-one-deletion", title="Maximum Subarray Sum With One Deletion", diff="Medium", topic=TOPIC,
    fn="maxSumOneDeletion", params=[("nums", "int[]")], ret="int", cmp="exact",
    desc="<p>Choose a non-empty contiguous subarray of <code>nums</code>. You may then delete <strong>at most one</strong> element from it, as long as at least one element remains. The sum of the elements that remain is the score. Return the largest possible score.</p><p>Examples: <code>[1, -2, 0, 3]</code> gives <code>4</code> (take the whole array and delete <code>-2</code>, leaving <code>1 + 0 + 3</code>). For <code>[-1, -1, -1]</code> the answer is <code>-1</code>, since a single element must remain.</p>",
    constraints=["1 &le; nums.length &le; 10,000", "-10,000 &le; nums[i] &le; 10,000"],
    hints=["Without the deletion this is Kadane's maximum subarray. What extra information do you need per index once a deletion is allowed?",
           "Track two values for subarrays ending at index <code>i</code>: <code>keep[i]</code>, no deletion used so far, and <code>skip[i]</code>, one deletion already used somewhere inside.",
           "<code>keep[i] = max(keep[i-1], 0) + a[i]</code>. <code>skip[i] = max(skip[i-1] + a[i], keep[i-1])</code>: either extend a subarray that already deleted, or delete <code>a[i]</code> itself right now. The answer is the best <code>keep</code> or <code>skip</code> over all <code>i</code>."],
    editorial=["Extend Kadane's state with a flag saying whether the deletion has been spent. Let <code>keep</code> be the best sum of a subarray ending at <code>i</code> with no deletion, and <code>skip</code> the best sum with exactly one deletion inside (and at least one element left).",
               "Transitions: <code>keep' = max(keep, 0) + x</code>. For <code>skip'</code> there are two ways: the deletion happened earlier, giving <code>skip + x</code>, or we delete the current element <code>x</code>, which requires a non-empty subarray ending at the previous index, giving <code>keep</code> (the old value). Take the better of the two. The answer is the maximum of every <code>keep</code> and <code>skip</code> seen. Deleting a negative element in the middle glues two good parts together, which is exactly what <code>skip</code> captures. O(n) time, O(1) space."],
    time="O(n)", space="O(1)",
    solution='''def maxSumOneDeletion(nums):
    NEG = float("-inf")
    keep = nums[0]
    skip = NEG
    best = keep
    for x in nums[1:]:
        skip = max(skip + x, keep)
        keep = max(keep, 0) + x
        best = max(best, keep, skip)
    return best
''',
    tests=[[[1, -2, 0, 3]], [[-1, -1, -1]], [[1, -2, -2, 3]], [[5]], [[-5]], [[3, -10, 4]], [[2, 1, -2, -5, -2]],
           [[-1, -2]], [[0, 0]], [[1, 2, 3]], [[4, -1, -1, 4]], [[-2, 1, -3, 4, -1, 2, 1, -5, 4]],
           _big1, _big2, _big3],
)


def _b_del1(nums):
    n = len(nums)
    best = None
    for i in range(n):
        for j in range(i, n):
            seg = nums[i:j + 1]
            s = sum(seg)
            if best is None or s > best:
                best = s
            if len(seg) >= 2:
                for x in seg:
                    best = max(best, s - x)
    return best


def _v_del1(tests):
    for t in tests:
        a = t["args"][0]
        assert 1 <= len(a) <= 10000
        _inrange(a, -10000, 10000)


CHECKS["max-subarray-sum-one-deletion"] = (_b_del1, lambda r: [gen_arr(r, -6, 6, 1, 9)], "exact")
VALIDATE["max-subarray-sum-one-deletion"] = _v_del1

# ------------------------------------------------------------------

_r = rnd(9104)
_big1 = [[_r.choice([-1, 1]) * _r.randint(1, 10 ** 9) for _ in range(4000)]]
_big2 = [[_r.choice([-1, 1, 1]) * _r.randint(1, 10 ** 9) if _r.random() > 0.01 else 0 for _ in range(4000)]]
_big3 = [[-_r.randint(1, 10 ** 9) for _ in range(3001)]]

add(
    id="longest-subarray-positive-product", title="Longest Subarray With Positive Product", diff="Medium", topic=TOPIC,
    fn="longestPositiveProduct", params=[("nums", "int[]")], ret="int", cmp="exact",
    desc="<p>Return the length of the longest contiguous subarray of <code>nums</code> whose product is strictly positive. If no subarray has a positive product, return <code>0</code>.</p><p>The numbers can be huge, so do not compute the product itself: only the signs matter.</p><p>Examples: <code>[1, -2, -3, 4]</code> gives <code>4</code> (product 24); <code>[-1, -2, -3, 0, 5]</code> gives <code>2</code> (the subarray <code>[-1, -2]</code>).</p>",
    constraints=["1 &le; nums.length &le; 10,000", "-10<sup>9</sup> &le; nums[i] &le; 10<sup>9</sup>"],
    hints=["A product is positive exactly when it contains no zero and an even number of negatives. A zero splits the array into independent parts.",
           "For subarrays ending at index <code>i</code>, keep the length of the longest one with a positive product and of the longest one with a negative product.",
           "Positive <code>x</code>: <code>pos = pos + 1</code>, <code>neg = neg + 1</code> if <code>neg &gt; 0</code> else 0. Negative <code>x</code>: swap roles, the new <code>pos</code> is <code>neg + 1</code> if <code>neg &gt; 0</code> else 0, and the new <code>neg</code> is <code>pos + 1</code>. Zero resets both to 0."],
    editorial=["Let <code>pos</code> and <code>neg</code> be the lengths of the longest subarrays ending at the current index whose product is positive / negative (0 when none exists). A positive <code>x</code> keeps signs: <code>pos + 1</code> stays positive, and a negative run extends to <code>neg + 1</code> only if one existed. A negative <code>x</code> flips signs: the new positive run is the old negative run plus one (if it existed), the new negative run is the old positive run plus one. A zero kills both runs.",
               "The answer is the largest <code>pos</code> seen. This is the sign-only cousin of Maximum Product Subarray and avoids big numbers entirely. O(n) time, O(1) space."],
    time="O(n)", space="O(1)",
    solution='''def longestPositiveProduct(nums):
    pos = neg = best = 0
    for x in nums:
        if x > 0:
            pos, neg = pos + 1, (neg + 1 if neg else 0)
        elif x < 0:
            pos, neg = (neg + 1 if neg else 0), pos + 1
        else:
            pos = neg = 0
        best = max(best, pos)
    return best
''',
    tests=[[[1, -2, -3, 4]], [[-1, -2, -3, 0, 5]], [[0]], [[-1]], [[7]], [[0, 0, 0]], [[-1, 2]], [[-1, -1]],
           [[2, -1, 3, -1, 0, 4, 5, 6, -7]], [[-1000000000, 1000000000, -1000000000, 1000000000]],
           [[0, 1, -2, -3, -4]], [[1, 2, 3, 0, -1, -2, 3, -4, 5]], _big1, _big2, _big3],
)


def _b_lpp(nums):
    n = len(nums)
    best = 0
    for i in range(n):
        p = 1
        for j in range(i, n):
            p *= 1 if nums[j] > 0 else (-1 if nums[j] < 0 else 0)
            if p > 0:
                best = max(best, j - i + 1)
    return best


def _v_lpp(tests):
    for t in tests:
        a = t["args"][0]
        assert 1 <= len(a) <= 10000
        _inrange(a, -10 ** 9, 10 ** 9)


CHECKS["longest-subarray-positive-product"] = (_b_lpp, lambda r: [gen_arr(r, -3, 3, 1, 10)], "exact")
VALIDATE["longest-subarray-positive-product"] = _v_lpp

# ------------------------------------------------------------------

_r = rnd(9105)
_big1 = [[_r.choice([-1, 1]) * _r.randint(1, 10 ** 9) for _ in range(5000)]]
_big2 = [[1] * 10000]
_big3 = [[_r.choice([-1, 1, 1, 0]) * _r.randint(1, 100) for _ in range(7000)]]

add(
    id="count-subarrays-positive-product", title="Count Subarrays With Positive Product", diff="Medium", topic=TOPIC, tier="extra",
    fn="countPositiveProductSubarrays", params=[("nums", "int[]")], ret="int", cmp="exact",
    desc="<p>Count the contiguous non-empty subarrays of <code>nums</code> whose product is strictly positive. Subarrays at different positions count separately even if their values are equal.</p><p>Example: for <code>[1, -2, -3, 4]</code> the positive-product subarrays are <code>[1]</code>, <code>[4]</code>, <code>[-2, -3]</code>, <code>[1, -2, -3]</code>, <code>[-2, -3, 4]</code> and the whole array, so the answer is <code>6</code>.</p>",
    constraints=["1 &le; nums.length &le; 10,000", "-10<sup>9</sup> &le; nums[i] &le; 10<sup>9</sup>"],
    hints=["Only the signs matter, and a zero cuts the array into independent segments.",
           "For subarrays ending at index <code>i</code>, count how many have a positive product and how many a negative one. Add the positive count to the answer at every index.",
           "Positive <code>x</code>: <code>pos += 1</code>, <code>neg</code> unchanged. Negative <code>x</code>: new <code>pos = neg</code>, new <code>neg = pos + 1</code>. Zero: both become 0."],
    editorial=["Let <code>pos</code> and <code>neg</code> count the subarrays ending at the current index with a positive / negative product. Appending a positive number keeps every sign and adds the one-element subarray <code>[x]</code> to the positive group. Appending a negative number flips every sign (so the two counts swap) and the single-element subarray <code>[x]</code> joins the negative group. A zero makes every subarray ending there have product 0, so both counts reset.",
               "Add <code>pos</code> to the running total at each index. The answer can reach about 5 &times; 10<sup>7</sup>, still inside 32 bits. O(n) time, O(1) space."],
    time="O(n)", space="O(1)",
    solution='''def countPositiveProductSubarrays(nums):
    pos = neg = total = 0
    for x in nums:
        if x > 0:
            pos += 1
        elif x < 0:
            pos, neg = neg, pos + 1
        else:
            pos = neg = 0
        total += pos
    return total
''',
    tests=[[[1, -2, -3, 4]], [[0]], [[5]], [[-5]], [[-1, -1]], [[-1, 1, -1]], [[0, 1, 0, 1]], [[2, 0, -3, -4, 0, 5]],
           [[-1, -2, -3, -4, -5]], [[3, 3, 3]], [[-7, 0, -7]], [[1, -1, 1, -1, 1, -1]], _big1, _big2, _big3],
)


def _b_cpp(nums):
    n = len(nums)
    cnt = 0
    for i in range(n):
        p = 1
        for j in range(i, n):
            p *= 1 if nums[j] > 0 else (-1 if nums[j] < 0 else 0)
            if p > 0:
                cnt += 1
    return cnt


def _v_cpp(tests):
    for t in tests:
        a = t["args"][0]
        assert 1 <= len(a) <= 10000
        _inrange(a, -10 ** 9, 10 ** 9)


CHECKS["count-subarrays-positive-product"] = (_b_cpp, lambda r: [gen_arr(r, -3, 3, 1, 10)], "exact")
VALIDATE["count-subarrays-positive-product"] = _v_cpp

# ------------------------------------------------------------------

_r = rnd(9106)
_big1 = [_rl(_r, 5000, -9999, 9999)]
_big2 = [[_r.randint(-5, 9999) if i % 2 == 0 else _r.randint(-9999, 5) for i in range(5000)]]
_big3 = [[-_r.randint(1, 9999) for _ in range(3000)]]

add(
    id="max-alternating-subarray-sum", title="Maximum Alternating Subarray Sum", diff="Medium", topic=TOPIC, tier="extra",
    fn="maxAlternatingSubarraySum", params=[("nums", "int[]")], ret="int", cmp="exact",
    desc="<p>The <em>alternating sum</em> of a non-empty subarray <code>nums[l..r]</code> is <code>nums[l] - nums[l+1] + nums[l+2] - ...</code>: signs alternate and the first element always has a plus sign.</p><p>Return the largest alternating sum over all non-empty subarrays.</p><p>Examples: <code>[3, 1, 5]</code> gives <code>7</code> (<code>3 - 1 + 5</code>); <code>[1, 5, -1]</code> gives <code>6</code> (the subarray <code>[5, -1]</code>, <code>5 - (-1)</code>).</p>",
    constraints=["1 &le; nums.length &le; 10,000", "-10,000 &le; nums[i] &le; 10,000"],
    hints=["The sign of an element depends on its distance from the start of the chosen subarray, not on its index in the array.",
           "Keep two values for subarrays ending at <code>i</code>: <code>plus</code>, where <code>nums[i]</code> carries a plus sign (it is at an even offset), and <code>minus</code>, where it carries a minus sign.",
           "<code>plus = nums[i] + max(0, minus_prev)</code> (either start fresh at <code>i</code> or continue a run whose last sign was minus). <code>minus = plus_prev - nums[i]</code> (the run must already exist). The answer is the best value of either."],
    editorial=["Think of the subarray as a chain whose signs go +, -, +, ... Let <code>plus[i]</code> be the best total of a chain that ends at <code>i</code> with <code>nums[i]</code> being added, and <code>minus[i]</code> the best total of a chain ending at <code>i</code> with <code>nums[i]</code> being subtracted. A chain whose last element is added either begins at <code>i</code> (total <code>nums[i]</code>) or continues from a chain whose last element was subtracted. A chain whose last element is subtracted can only come from a chain whose last element was added, because the first sign is always plus.",
               "So <code>plus[i] = nums[i] + max(0, minus[i-1])</code> and <code>minus[i] = plus[i-1] - nums[i]</code>. Take the maximum of every <code>plus</code> and <code>minus</code>. It is Kadane on two interleaved states. O(n) time, O(1) space."],
    time="O(n)", space="O(1)",
    solution='''def maxAlternatingSubarraySum(nums):
    NEG = float("-inf")
    plus = nums[0]
    minus = NEG
    best = plus
    for x in nums[1:]:
        new_plus = x + max(0, minus)
        new_minus = plus - x
        plus, minus = new_plus, new_minus
        best = max(best, plus, minus)
    return best
''',
    tests=[[[3, 1, 5]], [[1, 5, -1]], [[4]], [[-4]], [[0, 0]], [[-1, -2]], [[2, -3, 4, -1]], [[-5, 5]], [[5, -5]],
           [[1, 2, 3, 4, 5]], [[-3, -1, -4, -1, -5]], [[10, 1, 1, 10, 1, 1, 10]], _big1, _big2, _big3],
)


def _b_alt(nums):
    n = len(nums)
    best = None
    for i in range(n):
        s = 0
        sign = 1
        for j in range(i, n):
            s += sign * nums[j]
            sign = -sign
            if best is None or s > best:
                best = s
    return best


def _v_alt(tests):
    for t in tests:
        a = t["args"][0]
        assert 1 <= len(a) <= 10000
        _inrange(a, -10000, 10000)


CHECKS["max-alternating-subarray-sum"] = (_b_alt, lambda r: [gen_arr(r, -6, 6, 1, 9)], "exact")
VALIDATE["max-alternating-subarray-sum"] = _v_alt

# ------------------------------------------------------------------

_r = rnd(9107)
_big1 = [_rl(_r, 5000, -9999, 9999)]
_big2 = [[-_r.randint(1, 3) if _r.random() < 0.8 else _r.randint(1, 3) for _ in range(6000)]]
_big3 = [[-_r.randint(1, 10000) for _ in range(3000)]]

add(
    id="max-subarray-sum-after-one-squaring", title="Maximum Subarray Sum After One Squaring", diff="Medium", topic=TOPIC,
    fn="maxSubarraySumOneSquare", params=[("nums", "int[]")], ret="int", cmp="exact",
    desc="<p>You may replace <strong>at most one</strong> element <code>nums[i]</code> with its square <code>nums[i] * nums[i]</code>. After that, pick a non-empty contiguous subarray. Return the largest subarray sum you can reach.</p><p>Examples: <code>[2, -3, 1]</code> gives <code>12</code> (square <code>-3</code> to get <code>[2, 9, 1]</code>); <code>[-1, -1]</code> gives <code>1</code> (square one of them and take that single element).</p>",
    constraints=["1 &le; nums.length &le; 10,000", "-10,000 &le; nums[i] &le; 10,000"],
    hints=["Squaring never makes an element smaller (<code>x*x &ge; x</code> for integers), so using the operation is never bad. Which element should you square?",
           "That depends on the chosen subarray, so run a DP with a flag: <code>plain[i]</code>, best subarray ending at <code>i</code> with no squaring, and <code>sq[i]</code>, best subarray ending at <code>i</code> that contains the squared element.",
           "<code>plain[i] = max(plain[i-1], 0) + a[i]</code>. <code>sq[i] = max(sq[i-1] + a[i], max(plain[i-1], 0) + a[i]*a[i])</code>: either the square was placed earlier, or it is placed on <code>a[i]</code> now."],
    editorial=["Kadane with one extra bit of state. <code>plain</code> is the usual best sum of a subarray ending at <code>i</code>. <code>sq</code> is the best sum of a subarray ending at <code>i</code> that includes the single squared element somewhere in it.",
               "At index <code>i</code> the squared element is either already inside the run (<code>sq_prev + a[i]</code>) or it is <code>a[i]</code> itself, in which case the rest of the run is whatever best non-squared run ended at <code>i-1</code>, or nothing (<code>max(plain_prev, 0) + a[i]^2</code>). The answer is the maximum over all <code>plain</code> and <code>sq</code>. Because squaring never lowers a value, allowing 'at most one' is the same as 'exactly one'. O(n) time, O(1) space."],
    time="O(n)", space="O(1)",
    solution='''def maxSubarraySumOneSquare(nums):
    plain = nums[0]
    sq = nums[0] * nums[0]
    best = max(plain, sq)
    for x in nums[1:]:
        new_sq = max(sq + x, max(plain, 0) + x * x)
        plain = max(plain, 0) + x
        sq = new_sq
        best = max(best, plain, sq)
    return best
''',
    tests=[[[2, -3, 1]], [[-1, -1]], [[-5]], [[0]], [[3]], [[1, 2, 3]], [[-4, -4, -4]], [[10000, -10000, 10000]],
           [[-2, 1, -3, 4, -1, 2, 1, -5, 4]], [[0, 0, 0]], [[1, -10, 1]], [[-3, 2, -3, 2]], _big1, _big2, _big3],
)


def _b_sq(nums):
    n = len(nums)
    best = None
    for i in range(n):
        for k in [None] + list(range(n)):
            b = list(nums)
            if k is not None:
                b[k] = b[k] * b[k]
            s = 0
            for j in range(i, n):
                s += b[j]
                if best is None or s > best:
                    best = s
    return best


def _v_sq(tests):
    for t in tests:
        a = t["args"][0]
        assert 1 <= len(a) <= 10000
        _inrange(a, -10000, 10000)


CHECKS["max-subarray-sum-after-one-squaring"] = (_b_sq, lambda r: [gen_arr(r, -6, 6, 1, 8)], "exact")
VALIDATE["max-subarray-sum-after-one-squaring"] = _v_sq

# ------------------------------------------------------------------

_r = rnd(9108)
_big1 = [_rl(_r, 5000, -9999, 9999)]
_big2 = [[(-1) ** i * _r.randint(1, 9999) for i in range(6000)]]
_big3 = [[-_r.randint(1, 9999) for _ in range(3000)]]

add(
    id="max-sum-two-disjoint-subarrays", title="Maximum Sum of Two Disjoint Subarrays", diff="Medium", topic=TOPIC,
    fn="maxTwoDisjointSubarrays", params=[("nums", "int[]")], ret="int", cmp="exact",
    desc="<p>Choose <strong>two</strong> non-empty contiguous subarrays of <code>nums</code> that do not share any index (they may touch, i.e. the second may start right after the first ends). Return the largest possible total of the two sums.</p><p>Both subarrays are mandatory, so for an all-negative array the answer is negative.</p><p>Examples: <code>[1, -2, 3, -1, 4]</code> gives <code>7</code>; <code>[-5, -1, -3]</code> gives <code>-4</code> (take <code>-1</code> and <code>-3</code>).</p>",
    constraints=["2 &le; nums.length &le; 10,000", "-10,000 &le; nums[i] &le; 10,000"],
    hints=["Two disjoint subarrays are separated by some cut position: the first lies entirely to the left of the cut, the second entirely to the right.",
           "Let <code>left[i]</code> be the best subarray sum inside <code>nums[0..i]</code>, computed with Kadane and a running maximum. Compute <code>right[i]</code>, the best sum inside <code>nums[i..n-1]</code>, symmetrically.",
           "Try every cut: the answer is the maximum of <code>left[i] + right[i+1]</code> for <code>i</code> from 0 to <code>n-2</code>."],
    editorial=["If the first subarray ends at index <code>i</code> or earlier and the second starts at <code>i + 1</code> or later, then for a fixed cut the best choice is independent on both sides. Define <code>left[i]</code> as the best non-empty subarray sum within the prefix <code>[0..i]</code> (Kadane's best-ending-here, then a prefix maximum) and <code>right[i]</code> as the same within the suffix <code>[i..n-1]</code>.",
               "The answer is <code>max(left[i] + right[i+1])</code>. Every valid pair is considered, since its two subarrays are separated by at least one cut. Three linear passes, O(n) time and O(n) space."],
    time="O(n)", space="O(n)",
    solution='''def maxTwoDisjointSubarrays(nums):
    n = len(nums)
    left = [0] * n
    cur = best = nums[0]
    left[0] = best
    for i in range(1, n):
        cur = max(cur, 0) + nums[i]
        best = max(best, cur)
        left[i] = best
    right = [0] * n
    cur = best = nums[n - 1]
    right[n - 1] = best
    for i in range(n - 2, -1, -1):
        cur = max(cur, 0) + nums[i]
        best = max(best, cur)
        right[i] = best
    return max(left[i] + right[i + 1] for i in range(n - 1))
''',
    tests=[[[1, -2, 3, -1, 4]], [[-5, -1, -3]], [[2, 3]], [[-2, -3]], [[5, -100, 5]], [[1, 2, 3, 4]], [[0, 0, 0]],
           [[-1, 5, -1, -1, 5, -1]], [[4, -1, 2, -10, 3, 3, -1]], [[-10000, 10000, -10000, 10000, -10000]],
           [[3, -1, 3]], [[7, 7, -20, 7, 7, -20, 7, 7]], _big1, _big2, _big3],
)


def _b_two(nums):
    n = len(nums)
    best = None
    segs = [(i, j) for i in range(n) for j in range(i, n)]
    for a, b in segs:
        for c, d in segs:
            if c > b:
                s = sum(nums[a:b + 1]) + sum(nums[c:d + 1])
                if best is None or s > best:
                    best = s
    return best


def _v_two(tests):
    for t in tests:
        a = t["args"][0]
        assert 2 <= len(a) <= 10000
        _inrange(a, -10000, 10000)


CHECKS["max-sum-two-disjoint-subarrays"] = (_b_two, lambda r: [gen_arr(r, -6, 6, 2, 9)], "exact")
VALIDATE["max-sum-two-disjoint-subarrays"] = _v_two

# ------------------------------------------------------------------

_r = rnd(9109)
_big1 = [_rl(_r, 5000, -9999, 9999)]
_big2 = [[_r.randint(-5000, 9999) for _ in range(5000)]]
_big3 = [[-_r.randint(1, 9999) for _ in range(3000)]]

add(
    id="max-sum-even-length-subarray", title="Maximum Sum of an Even-Length Subarray", diff="Medium", topic=TOPIC, tier="extra",
    fn="maxEvenLengthSum", params=[("nums", "int[]")], ret="int", cmp="exact",
    desc="<p>Among all contiguous subarrays of <code>nums</code> whose length is <strong>even</strong> (2, 4, 6, ...), return the largest sum.</p><p>Examples: <code>[1, -2, 3, 4]</code> gives <code>7</code> (the subarray <code>[3, 4]</code>); <code>[-5, -1, -2]</code> gives <code>-3</code> (the subarray <code>[-1, -2]</code>).</p>",
    constraints=["2 &le; nums.length &le; 10,000", "-10,000 &le; nums[i] &le; 10,000"],
    hints=["Plain Kadane forgets the length. Which extra piece of information must a DP state remember here?",
           "Only the parity of the length matters. Track <code>even[i]</code> and <code>odd[i]</code>: the best sums of subarrays ending at <code>i</code> with an even / odd length (when such a subarray exists).",
           "<code>odd[i] = nums[i] + max(0, even[i-1])</code> (start fresh or extend an even run). <code>even[i] = odd[i-1] + nums[i]</code>. The answer is the best <code>even[i]</code>."],
    editorial=["Adding one element flips the parity of the length, so the states just trade places. For a subarray ending at <code>i</code> with an odd length, either it is the single element <code>[nums[i]]</code>, or it extends an even-length subarray ending at <code>i-1</code>. A subarray with an even length must extend an odd-length subarray ending at <code>i-1</code> (a lone element is odd, so an even run never starts fresh).",
               "Hence <code>odd' = nums[i] + max(0, even)</code> and <code>even' = odd + nums[i]</code>, where an even run that does not exist yet counts as minus infinity. The answer is the maximum <code>even</code> over all indices. A prefix-sum alternative: the best even-length sum ending at <code>j</code> is <code>P[j+1]</code> minus the smallest prefix sum at an index of the same parity, apart from <code>j+1</code> itself. O(n) time, O(1) space."],
    time="O(n)", space="O(1)",
    solution='''def maxEvenLengthSum(nums):
    NEG = float("-inf")
    odd = nums[0]
    even = NEG
    best = NEG
    for x in nums[1:]:
        new_even = odd + x
        new_odd = x + max(0, even)
        even, odd = new_even, new_odd
        best = max(best, even)
    return best
''',
    tests=[[[1, -2, 3, 4]], [[-5, -1, -2]], [[2, 3]], [[-2, -3]], [[0, 0]], [[5, -10, 5]], [[1, 2, 3]],
           [[9, -20, 9, 9, -20, 9]], [[-1, 10, -1, -1]], [[3, 3, 3, 3, 3]], [[-10000, -10000]], [[1, -1, 1, -1, 1]],
           _big1, _big2, _big3],
)


def _b_even(nums):
    n = len(nums)
    best = None
    for i in range(n):
        s = 0
        for j in range(i, n):
            s += nums[j]
            if (j - i + 1) % 2 == 0 and (best is None or s > best):
                best = s
    return best


def _v_even(tests):
    for t in tests:
        a = t["args"][0]
        assert 2 <= len(a) <= 10000
        _inrange(a, -10000, 10000)


CHECKS["max-sum-even-length-subarray"] = (_b_even, lambda r: [gen_arr(r, -6, 6, 2, 9)], "exact")
VALIDATE["max-sum-even-length-subarray"] = _v_even

# ---------------------------------------------------------------- HARD

_r = rnd(9110)
_big1 = [_rl(_r, 5000, -9999, 9999), 50]
_big2 = [[_r.choice([-1, 1, 1]) * _r.randint(1, 9999) for _ in range(5000)], 7]
_big3 = [[-_r.randint(1, 9999) for _ in range(3000)], 40]

add(
    id="max-subarray-sum-k-deletions", title="Maximum Subarray Sum With Up To K Deletions", diff="Hard", topic=TOPIC, tier="extra",
    fn="maxSumWithDeletions", params=[("nums", "int[]"), ("k", "int")], ret="int", cmp="exact",
    desc="<p>Choose a contiguous subarray of <code>nums</code>, then delete <strong>at most <code>k</code></strong> elements from inside it, as long as at least one element remains. The score is the sum of the surviving elements. Return the largest score.</p><p>Equivalently, you pick a non-empty set of indices to keep such that the span from the first kept index to the last kept index contains at most <code>k</code> indices that are not kept.</p><p>Examples: <code>nums = [1, -5, 2, -6, 3]</code> gives <code>3</code> for <code>k = 0</code>, <code>5</code> for <code>k = 1</code> (keep <code>2</code> and <code>3</code>) and <code>6</code> for <code>k = 2</code> (keep <code>1, 2, 3</code>).</p>",
    constraints=["1 &le; nums.length &le; 5,000", "-10,000 &le; nums[i] &le; 10,000", "0 &le; k &le; 50"],
    hints=["For k = 1 you needed two states (deletion used or not). What is the natural generalization to k deletions?",
           "Let <code>E[i][j]</code> be the best sum of a subarray ending at index <code>i</code> where <code>nums[i]</code> is kept and exactly <code>j</code> deletions were used inside. Let <code>D[i][j]</code> be the same, but <code>nums[i]</code> itself is the j-th deleted element.",
           "<code>E[i][j] = nums[i] + max(E[i-1][j], D[i-1][j])</code>, plus the option to start fresh when <code>j = 0</code>. <code>D[i][j] = max(E[i-1][j-1], D[i-1][j-1])</code>. Answer: the best <code>E[i][j]</code> with <code>j &le; k</code>."],
    editorial=["The state is (index, deletions used, whether the current element was deleted). Keeping the last element in the state lets us handle runs of consecutive deletions without trying every run length: a deleted element simply passes the previous value along while consuming one deletion.",
               "With <code>E[i][j]</code> (element <code>i</code> kept) and <code>D[i][j]</code> (element <code>i</code> deleted, having a kept element somewhere before it): <code>E[i][j] = nums[i] + max(E[i-1][j], D[i-1][j])</code>, and for <code>j = 0</code> also the fresh start <code>nums[i] + max(0, E[i-1][0])</code>; <code>D[i][j] = max(E[i-1][j-1], D[i-1][j-1])</code> for <code>j &ge; 1</code>. We never need a fresh start with deletions because deleting leading elements is the same as starting later. The answer is the maximum of <code>E[i][j]</code> over all <code>i</code> and <code>j &le; k</code> (a trailing deleted element would only waste a deletion). Rolling over <code>i</code> keeps O(k) memory, total O(n &middot; k) time."],
    time="O(n * k)", space="O(k)",
    solution='''def maxSumWithDeletions(nums, k):
    NEG = float("-inf")
    E = [NEG] * (k + 1)
    D = [NEG] * (k + 1)
    best = NEG
    for i, x in enumerate(nums):
        nE = [NEG] * (k + 1)
        nD = [NEG] * (k + 1)
        for j in range(k + 1):
            prev = max(E[j], D[j])
            if j == 0:
                prev = max(prev, 0)
            nE[j] = x + prev
            if j >= 1:
                nD[j] = max(E[j - 1], D[j - 1])
            if nE[j] > best:
                best = nE[j]
        E, D = nE, nD
    return best
''',
    tests=[[[1, -5, 2, -6, 3], 0], [[1, -5, 2, -6, 3], 1], [[1, -5, 2, -6, 3], 2], [[5], 3], [[-5], 0], [[-5, -2], 1],
           [[-1, -1, -1], 2], [[4, -10, -10, 4], 2], [[4, -10, -10, 4], 1], [[3, -1, 3, -1, 3], 2],
           [[0, 0, 0], 1], [[-3, 8, -20, -20, -20, 9, -1], 3], _big1, _big2, _big3],
)


def _b_kdel(nums, k):
    n = len(nums)
    best = None
    for mask in range(1, 1 << n):
        idx = [i for i in range(n) if mask >> i & 1]
        if idx[-1] - idx[0] + 1 - len(idx) <= k:
            s = sum(nums[i] for i in idx)
            if best is None or s > best:
                best = s
    return best


def _v_kdel(tests):
    for t in tests:
        a, k = t["args"]
        assert 1 <= len(a) <= 5000
        _inrange(a, -10000, 10000)
        assert 0 <= k <= 50


def _g_kdel(r):
    return [gen_arr(r, -6, 6, 1, 9), r.randint(0, 4)]


CHECKS["max-subarray-sum-k-deletions"] = (_b_kdel, _g_kdel, "exact")
VALIDATE["max-subarray-sum-k-deletions"] = _v_kdel

# ------------------------------------------------------------------

_r = rnd(9111)
_big1 = [_rl(_r, 5000, -9999, 9999), 1700]
_big2 = [_rl(_r, 4000, -9999, 9999), 3999]
_big3 = [[-_r.randint(1, 9999) for _ in range(3000)], 1200]

add(
    id="circular-subarray-sum-length-at-most-k", title="Circular Subarray Sum With Length Limit", diff="Hard", topic=TOPIC, tier="extra",
    fn="maxCircularSumAtMostK", params=[("nums", "int[]"), ("k", "int")], ret="int", cmp="exact",
    desc="<p>The array <code>nums</code> is circular: after the last element comes the first again. A <em>circular subarray</em> starts at any index and takes consecutive elements, wrapping around the end if needed, without using an index twice. It must contain at least 1 and at most <code>k</code> elements.</p><p>Return the largest sum of such a circular subarray.</p><p>Examples: for <code>nums = [5, -3, 5]</code>, <code>k = 2</code> the answer is <code>10</code> (the two fives, which are neighbours around the end); with <code>k = 1</code> it is <code>5</code>; with <code>k = 3</code> it is <code>10</code> as well, because adding the <code>-3</code> cannot help. For <code>[-2, -3, -1]</code> and <code>k = 2</code> the answer is <code>-1</code>.</p>",
    constraints=["1 &le; nums.length &le; 5,000", "-10,000 &le; nums[i] &le; 10,000", "1 &le; k &le; nums.length"],
    hints=["Unroll the circle: a wrapping subarray is an ordinary subarray of <code>nums + nums</code> that starts in the first copy.",
           "With prefix sums <code>P</code> of the doubled array, a subarray <code>(s, e]</code> has sum <code>P[e] - P[s]</code>. For each end <code>e</code>, you want the smallest <code>P[s]</code> among the allowed starts <code>s &isin; [e-k, e-1]</code>.",
           "A sliding-window minimum answers this in amortised O(1): keep a deque of indices whose prefix sums are increasing, drop indices that fell out of the window from the front, and drop larger values from the back before pushing the new one."],
    editorial=["Concatenate the array with itself so wrapping subarrays become ordinary ones, and build prefix sums <code>P</code> of length <code>2n + 1</code>. A subarray of length between 1 and <code>k</code> ending at doubled position <code>e</code> (exclusive) has sum <code>P[e] - P[s]</code> with <code>e - k &le; s &le; e - 1</code>. Because <code>k &le; n</code>, no index is ever used twice, and any circular subarray appears with its start in the first copy.",
               "For each <code>e</code> from 1 to <code>2n</code> we need the minimum <code>P[s]</code> over a window of the last <code>k</code> prefix positions. That is the classic sliding-window minimum: a monotonic deque stores candidate indices with increasing <code>P</code>. Pop from the front when the index leaves the window, pop from the back while the back's value is not smaller than the new one, then the front is the minimum. Overall O(n) time and O(n) space. A direct double loop is O(n &middot; k)."],
    time="O(n)", space="O(n)",
    solution='''def maxCircularSumAtMostK(nums, k):
    from collections import deque
    n = len(nums)
    m = 2 * n
    P = [0] * (m + 1)
    for i in range(m):
        P[i + 1] = P[i] + nums[i % n]
    best = None
    dq = deque()
    for e in range(1, m + 1):
        s_new = e - 1
        while dq and P[dq[-1]] >= P[s_new]:
            dq.pop()
        dq.append(s_new)
        while dq[0] < e - k:
            dq.popleft()
        val = P[e] - P[dq[0]]
        if best is None or val > best:
            best = val
    return best
''',
    tests=[[[5, -3, 5], 2], [[5, -3, 5], 1], [[5, -3, 5], 3], [[-2, -3, -1], 2], [[7], 1], [[-7], 1],
           [[3, -1, 2, -1], 4], [[3, -1, 2, -1], 3], [[1, 2, 3, 4], 2], [[-5, 6, -5, 6, -5], 3],
           [[8, -20, 1, 1, -20, 8], 2], [[0, 0, 0], 3], _big1, _big2, _big3],
)


def _b_circ(nums, k):
    n = len(nums)
    best = None
    for s in range(n):
        t = 0
        for L in range(1, k + 1):
            t += nums[(s + L - 1) % n]
            if best is None or t > best:
                best = t
    return best


def _v_circ(tests):
    for t in tests:
        a, k = t["args"]
        assert 1 <= len(a) <= 5000
        _inrange(a, -10000, 10000)
        assert 1 <= k <= len(a)


def _g_circ(r):
    a = gen_arr(r, -6, 6, 1, 9)
    return [a, r.randint(1, len(a))]


CHECKS["circular-subarray-sum-length-at-most-k"] = (_b_circ, _g_circ, "exact")
VALIDATE["circular-subarray-sum-length-at-most-k"] = _v_circ
