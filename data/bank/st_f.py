"""Problems: stack contribution tricks (who owns a subarray, greedy lexicographic stacks). See data/lib.py for the registry."""
import itertools
from functools import lru_cache

from lib import add, rnd, CHECKS, VALIDATE, gen_arr  # noqa: F401

INT_MIN, INT_MAX = -(2 ** 31), 2 ** 31 - 1
MOD = 10 ** 9 + 7


# ---------------------------------------------------------------- EASY

p = add(
    id="subarray-maximum-ownership-counts", title="Subarray Maximum Ownership Counts", diff="Easy", topic="Stack", tier="extra",
    fn="ownershipCounts", params=[("nums", "int[]")], ret="int[]", cmp="exact",
    desc="<p>Every non-empty contiguous subarray of <code>nums</code> has a maximum value. When the maximum occurs several times in the subarray, the <em>leftmost</em> occurrence is said to <em>own</em> the subarray. So each subarray has exactly one owner.</p><p>Return an array <code>counts</code> of the same length as <code>nums</code> where <code>counts[i]</code> is the number of subarrays owned by index <code>i</code>.</p><p>Example: for <code>[2, 1, 2]</code> the six subarrays are owned like this: <code>[2]</code> (index 0), <code>[1]</code> (index 1), <code>[2]</code> (index 2), <code>[2, 1]</code> (index 0), <code>[1, 2]</code> (index 2) and <code>[2, 1, 2]</code> (index 0), so the answer is <code>[3, 1, 2]</code>.</p>",
    constraints=["1 &le; nums.length &le; 10,000", "-10<sup>9</sup> &le; nums[i] &le; 10<sup>9</sup>"],
    hints=["Index <code>i</code> owns a subarray <code>[l, r]</code> only if <code>l &le; i &le; r</code> and nothing in the subarray beats <code>nums[i]</code>. How far can <code>l</code> go to the left and <code>r</code> to the right?",
           "Because the leftmost maximum owns the subarray, the elements to the left of <code>i</code> inside the subarray must be strictly smaller, and the elements to the right must be smaller or equal.",
           "Let <code>L</code> be the nearest index to the left with <code>nums[L] &ge; nums[i]</code> and <code>R</code> the nearest index to the right with <code>nums[R] &gt; nums[i]</code> (use -1 and n when there is none). Then <code>counts[i] = (i - L) * (R - i)</code>. Find <code>L</code> and <code>R</code> for all indices with monotonic stacks."],
    editorial=["Fix an index <code>i</code> and ask which subarrays it owns. A subarray <code>[l, r]</code> containing <code>i</code> is owned by <code>i</code> exactly when every element to the left of <code>i</code> in the subarray is strictly smaller than <code>nums[i]</code> and every element to the right is at most <code>nums[i]</code>. The left end can therefore be anything strictly after the nearest index <code>L</code> on the left holding a value <code>&ge; nums[i]</code>, and the right end anything strictly before the nearest index <code>R</code> on the right holding a value <code>&gt; nums[i]</code>. The choices are independent, so <code>counts[i] = (i - L) * (R - i)</code>.",
               "The asymmetric comparison (<code>&ge;</code> on one side, <code>&gt;</code> on the other) is what makes every subarray have exactly one owner; the counts always add up to <code>n(n+1)/2</code>. Both nearest-bigger indices come from a monotonic stack: scan left to right popping smaller values for <code>L</code>, and right to left popping smaller-or-equal values for <code>R</code>. Each index is pushed and popped once, so the total time is O(n). This <em>contribution</em> view, counting for each element how many subarrays it decides, is the basis of sum-of-subarray-minimums style problems."],
    time="O(n)", space="O(n)",
    solution='''def ownershipCounts(nums):
    n = len(nums)
    left = [-1] * n    # nearest index on the left with value >= nums[i]
    right = [n] * n    # nearest index on the right with value > nums[i]
    stack = []
    for i in range(n):
        while stack and nums[stack[-1]] < nums[i]:
            stack.pop()
        left[i] = stack[-1] if stack else -1
        stack.append(i)
    stack = []
    for i in range(n - 1, -1, -1):
        while stack and nums[stack[-1]] <= nums[i]:
            stack.pop()
        right[i] = stack[-1] if stack else n
        stack.append(i)
    return [(i - left[i]) * (right[i] - i) for i in range(n)]
''',
    tests=[[[2, 1, 2]], [[5]], [[1, 2, 3]], [[3, 2, 1]], [[4, 4, 4, 4]], [[1, 3, 2, 3, 1]], [[-5, -5, 0, -5]], [[10 ** 9 // 2, -10 ** 9, 10 ** 9]],
           [[7, 1, 7, 1, 7]]],
)
_r = rnd(9601)
p["tests"].append([[_r.randint(-50, 50) for _ in range(3000)]])
p["tests"].append([list(range(2500))])
p["tests"].append([[_r.choice([1, 2]) for _ in range(3000)]])


def b_owner(nums):
    n = len(nums)
    res = [0] * n
    for l in range(n):
        for r in range(l, n):
            m = max(nums[l:r + 1])
            res[nums[l:r + 1].index(m) + l] += 1
    return res


def v_owner(tests):
    for t in tests:
        nums = t["args"][0]
        n = len(nums)
        assert 1 <= n <= 10000 and all(-10 ** 9 <= v <= 10 ** 9 for v in nums)
        assert sum(t["expected"]) == n * (n + 1) // 2


CHECKS["subarray-maximum-ownership-counts"] = (b_owner, lambda r: [gen_arr(r, -3, 3, 1, 9)], "exact")
VALIDATE["subarray-maximum-ownership-counts"] = v_owner


p = add(
    id="remove-one-digit-to-maximize", title="Remove One Digit to Maximize the Number", diff="Easy", topic="Stack", tier="extra",
    fn="removeDigit", params=[("num", "string"), ("digit", "int")], ret="string", cmp="exact",
    desc="<p>The string <code>num</code> is a positive integer written with the digits <code>1</code> to <code>9</code> only. You must delete <em>exactly one</em> character from <code>num</code>, and it has to be a character equal to the digit <code>digit</code>. Return the largest resulting number, again as a string.</p><p>Example: <code>num = \"1231\"</code> and <code>digit = 1</code> gives <code>\"231\"</code> (deleting the first 1) rather than <code>\"123\"</code>.</p>",
    constraints=["2 &le; num.length &le; 10,000", "num[i] is a digit between '1' and '9'", "1 &le; digit &le; 9 and digit occurs at least once in num"],
    hints=["All candidates have the same length, so the largest number is also the lexicographically largest string. You could try deleting each occurrence and keep the best.",
           "Compare the candidates from deleting two different occurrences: the strings agree up to the earlier position, so the first difference decides. What does the character right after a deleted digit do to the result?",
           "Delete the first occurrence of <code>digit</code> that is followed by a larger digit, because that moves a bigger digit forward. If there is no such occurrence, delete the last occurrence."],
    editorial=["Deleting position <code>i</code> makes the digit that used to be at <code>i + 1</code> take its place. So compared with leaving the number alone, deleting an occurrence followed by a larger digit increases the value at that position, and the earlier such an increase happens the more it is worth. Hence the first occurrence of <code>digit</code> whose right neighbour is larger is the best deletion.",
               "If no occurrence has a larger right neighbour, every deletion either lowers or keeps the digit that takes its place, and the damage is smallest when it happens as far to the right as possible, so delete the last occurrence. This is the one-digit special case of the greedy stack used for 'remove k digits'. One pass, O(n) time."],
    time="O(n)", space="O(n)",
    solution='''def removeDigit(num, digit):
    d = str(digit)
    last = -1
    for i, ch in enumerate(num):
        if ch == d:
            last = i
            if i + 1 < len(num) and num[i + 1] > ch:
                return num[:i] + num[i + 1:]
    return num[:last] + num[last + 1:]
''',
    tests=[["1231", 1], ["551", 5], ["321", 1], ["12", 1], ["12", 2], ["99", 9], ["123", 3], ["1919", 9], ["1111", 1], ["54321", 3],
           ["2121212", 2], ["9999999", 9]],
)
_r = rnd(9602)
p["tests"].append(["".join(_r.choice("123456789") for _ in range(9000)), 5])
p["tests"].append(["9" * 9999 + "8", 9])
p["tests"].append(["".join(_r.choice("12") for _ in range(10000)), 1])


def b_remdig(num, digit):
    d = str(digit)
    return max(num[:i] + num[i + 1:] for i in range(len(num)) if num[i] == d)


def g_remdig(r):
    n = r.randint(2, 9)
    num = "".join(r.choice("1234") for _ in range(n))
    return [num, int(r.choice(num))]


def v_remdig(tests):
    for t in tests:
        num, digit = t["args"]
        assert 2 <= len(num) <= 10000 and set(num) <= set("123456789")
        assert 1 <= digit <= 9 and str(digit) in num


CHECKS["remove-one-digit-to-maximize"] = (b_remdig, g_remdig, "exact")
VALIDATE["remove-one-digit-to-maximize"] = v_remdig


# ---------------------------------------------------------------- MEDIUM

p = add(
    id="sum-of-subarray-ranges-mod", title="Sum of Subarray Ranges", diff="Medium", topic="Stack", tier="common",
    fn="sumOfRanges", params=[("nums", "int[]")], ret="int", cmp="exact",
    desc="<p>The <em>range</em> of a subarray is its largest value minus its smallest value (a single element has range 0). Return the sum of the ranges of all non-empty contiguous subarrays of <code>nums</code>, taken modulo <code>1,000,000,007</code>.</p><p>Example: for <code>[1, 3, 3]</code> the subarrays <code>[1,3]</code> and <code>[1,3,3]</code> have range 2 and all others have range 0, so the answer is <code>4</code>.</p>",
    constraints=["1 &le; nums.length &le; 100,000", "-10<sup>9</sup> &le; nums[i] &le; 10<sup>9</sup>", "Return the sum modulo 1,000,000,007 (the true sum is never negative)"],
    hints=["Looking at all O(n<sup>2</sup>) subarrays and tracking a running max and min works for small inputs. Try to split the answer into (sum of maxima) minus (sum of minima).",
           "For the sum of maxima, ask for each element how many subarrays it is the maximum of. If <code>nums[i]</code> can extend <code>a</code> steps to the left and <code>b</code> steps to the right before meeting a bigger element, it is the maximum of <code>a * b</code> subarrays.",
           "Break ties so each subarray has one owner (strictly greater on one side, greater-or-equal on the other). Compute both distances with monotonic stacks. The minima work the same way, or negate the array and reuse the code."],
    editorial=["The range sum equals (sum over all subarrays of the maximum) minus (sum over all subarrays of the minimum). For the maximum, count how many subarrays each element decides. Index <code>i</code> is the owner of exactly <code>(i - left) * (right - i)</code> subarrays, where <code>left</code> is the nearest index on the left with a value <code>&ge; nums[i]</code> and <code>right</code> the nearest index on the right with a value <code>&gt; nums[i]</code>; the unequal comparisons make every subarray counted once even with duplicates.",
               "A monotonic stack finds all <code>left</code> values in one left-to-right pass and all <code>right</code> values in one right-to-left pass. The contribution of <code>i</code> is <code>nums[i]</code> times its count. For the minima, apply the same function to the negated array: the sum of minima is minus the sum of maxima of the negated values, so <code>range sum = f(nums) + f(-nums)</code>. Total time O(n), space O(n). The exact sum can be huge, so reduce modulo 10<sup>9</sup>+7 at the end (Python integers do not overflow; in other languages reduce per term)."],
    time="O(n)", space="O(n)",
    solution='''def sumOfRanges(nums):
    MOD = 10 ** 9 + 7

    def sum_of_maxima(a):
        n = len(a)
        left = [-1] * n
        right = [n] * n
        stack = []
        for i in range(n):
            while stack and a[stack[-1]] < a[i]:
                stack.pop()
            left[i] = stack[-1] if stack else -1
            stack.append(i)
        stack = []
        for i in range(n - 1, -1, -1):
            while stack and a[stack[-1]] <= a[i]:
                stack.pop()
            right[i] = stack[-1] if stack else n
            stack.append(i)
        return sum(a[i] * (i - left[i]) * (right[i] - i) for i in range(n))

    total = sum_of_maxima(nums) + sum_of_maxima([-x for x in nums])  # maxima minus minima
    return total % MOD
''',
    tests=[[[1, 2, 3]], [[1, 3, 3]], [[4, -2, -3, 4, 1]], [[7]], [[5, 5, 5, 5]], [[3, 2, 1]], [[1, 1000000000, 1]], [[-1000000000, 1000000000]],
           [[2, 9, 4, 9, 2]]],
)
_r = rnd(9603)
p["tests"].append([[_r.randint(-10 ** 9, 10 ** 9) for _ in range(5000)]])
p["tests"].append([[(10 ** 9 if i % 2 else -10 ** 9) for i in range(4000)]])
p["tests"].append([list(range(-2000, 2000))])
p["tests"].append([[_r.randint(0, 3) for _ in range(5000)]])


def b_ranges(nums):
    total = 0
    for l in range(len(nums)):
        hi = lo = nums[l]
        for r in range(l, len(nums)):
            hi = max(hi, nums[r])
            lo = min(lo, nums[r])
            total += hi - lo
    return total % MOD


def v_ranges(tests):
    for t in tests:
        nums = t["args"][0]
        assert 1 <= len(nums) <= 100000 and all(-10 ** 9 <= v <= 10 ** 9 for v in nums)
        if len(nums) <= 1500:
            assert b_ranges(nums) == t["expected"]


CHECKS["sum-of-subarray-ranges-mod"] = (b_ranges, lambda r: [gen_arr(r, -5, 5, 1, 10)], "exact")
VALIDATE["sum-of-subarray-ranges-mod"] = v_ranges


p = add(
    id="subarrays-with-maximum-at-both-ends", title="Subarrays With the Maximum at Both Ends", diff="Medium", topic="Stack", tier="common",
    fn="countMaxAtBothEnds", params=[("nums", "int[]")], ret="int", cmp="exact",
    desc="<p>Count the non-empty contiguous subarrays of <code>nums</code> whose <strong>first element and last element are both equal to the maximum of the subarray</strong>. A subarray with a single element always qualifies. Subarrays at different positions count separately even if they hold the same values.</p><p>Example: for <code>[1, 4, 3, 3, 2]</code> the answer is <code>6</code>: the five single elements and <code>[3, 3]</code>. For <code>[3, 3, 3]</code> the answer is <code>6</code> as well: three single elements, two subarrays <code>[3, 3]</code> and one <code>[3, 3, 3]</code>.</p>",
    constraints=["1 &le; nums.length &le; 50,000", "-10<sup>9</sup> &le; nums[i] &le; 10<sup>9</sup>"],
    hints=["A qualifying subarray ends at some index <code>r</code>, and its start <code>l &le; r</code> must hold the same value as <code>nums[r]</code> with nothing larger in between. Count the valid starts for each end <code>r</code>.",
           "For a fixed end <code>r</code> the valid starts are the earlier indices <code>l</code> with <code>nums[l] == nums[r]</code> such that every element between them is at most <code>nums[r]</code>, plus <code>r</code> itself. A larger element between two equal values cuts them off from each other.",
           "Keep a stack of <code>[value, count]</code> pairs with strictly decreasing values from bottom to top. For a new value <code>x</code>, pop all pairs with a value smaller than <code>x</code>; if the top now has value <code>x</code> increase its count, otherwise push <code>[x, 1]</code>. The top count is the number of valid starts for this end, so add it to the answer."],
    editorial=["Count the subarrays by their last index <code>r</code>. The first element <code>l</code> must satisfy <code>nums[l] == nums[r]</code> and no element in between may exceed that value, otherwise the maximum would differ from the ends. So for each <code>r</code> we need the number of indices <code>l &le; r</code> that are still 'visible' to <code>r</code> with the same value, counting <code>r</code> itself.",
               "A monotonic stack of <code>[value, count]</code> pairs maintains exactly that. When a larger value arrives, every smaller value on the stack is blocked for all later ends, so it is popped. If the new top equals the new value, those earlier copies are still reachable and the new copy joins the group (count + 1); otherwise a new group with count 1 is started. The group count at the top is the number of valid starts for the current end. Each element is pushed and popped at most once, so the time is O(n); space is O(n). The answer is at most n(n+1)/2, which fits into 32 bits for n &le; 50,000."],
    time="O(n)", space="O(n)",
    solution='''def countMaxAtBothEnds(nums):
    total = 0
    stack = []  # [value, count] pairs, values strictly decreasing from bottom to top
    for x in nums:
        while stack and stack[-1][0] < x:
            stack.pop()
        if stack and stack[-1][0] == x:
            stack[-1][1] += 1
        else:
            stack.append([x, 1])
        total += stack[-1][1]
    return total
''',
    tests=[[[1, 4, 3, 3, 2]], [[3, 3, 3]], [[9]], [[1, 2, 3, 4]], [[4, 3, 2, 1]], [[2, 1, 2]], [[2, 3, 2]], [[-5, -5, 0, -5, -5]], [[0, 0]],
           [[10 ** 9, -10 ** 9, 10 ** 9, 10 ** 9]]],
)
_r = rnd(9604)
p["tests"].append([[_r.randint(-1000, 1000) for _ in range(6000)]])
p["tests"].append([[4] * 6000])
p["tests"].append([[_r.randint(0, 2) for _ in range(6000)]])
p["tests"].append([[(i % 7) for i in range(6000)]])


def b_both_ends(nums):
    c = 0
    for l in range(len(nums)):
        for r in range(l, len(nums)):
            m = max(nums[l:r + 1])
            if nums[l] == m and nums[r] == m:
                c += 1
    return c


def v_both_ends(tests):
    for t in tests:
        nums = t["args"][0]
        assert 1 <= len(nums) <= 50000 and all(-10 ** 9 <= v <= 10 ** 9 for v in nums)
        if len(nums) <= 400:
            assert b_both_ends(nums) == t["expected"]


CHECKS["subarrays-with-maximum-at-both-ends"] = (b_both_ends, lambda r: [gen_arr(r, -3, 3, 1, 10)], "exact")
VALIDATE["subarrays-with-maximum-at-both-ends"] = v_both_ends


p = add(
    id="maximum-subarray-min-product-mod", title="Maximum Subarray Min-Product", diff="Medium", topic="Stack", tier="common",
    fn="maxMinProduct", params=[("nums", "int[]")], ret="int", cmp="exact",
    desc="<p>The <em>min-product</em> of a non-empty subarray is the minimum value of the subarray multiplied by the sum of the subarray. Find the largest min-product over all non-empty subarrays of <code>nums</code> and return it modulo <code>1,000,000,007</code>. The maximum must be chosen by its true value, before taking the remainder.</p><p>Example: for <code>[1, 2, 3, 2]</code> the best subarray is <code>[2, 3, 2]</code> with minimum 2 and sum 7, giving <code>14</code>.</p>",
    constraints=["1 &le; nums.length &le; 100,000", "1 &le; nums[i] &le; 10<sup>7</sup>", "The true maximum can exceed 32 bits; only its remainder modulo 1,000,000,007 is returned"],
    hints=["For a fixed minimum value, which subarray is the best? All values are positive, so a longer subarray has a larger sum.",
           "Assume <code>nums[i]</code> is the minimum. Extend the subarray left and right as far as every element stays <code>&ge; nums[i]</code>. That subarray has the best sum among those with minimum at least <code>nums[i]</code> around <code>i</code>.",
           "Use prefix sums for the sum and a monotonic stack of increasing values to find the extent: when an element pops a taller bar, the popped element's range ends just before the current index and starts after the new stack top. Append a sentinel 0 so everything is popped at the end."],
    editorial=["Because every value is positive, enlarging a subarray without lowering its minimum only increases the sum. So the optimal subarray is the maximal one around some index <code>i</code> in which <code>nums[i]</code> is the minimum, namely the span from just after the nearest smaller element on the left to just before the nearest smaller element on the right. There are only n such spans.",
               "Build prefix sums <code>pre</code>. Scan the array with a stack of indices whose values are non-decreasing. When the current value is smaller than the value on top, pop that index <code>m</code>: its span ends at <code>cur - 1</code> and starts at <code>stack[-1] + 1</code> (or 0 when the stack is empty). The candidate is <code>nums[m] * (pre[cur] - pre[start])</code>. A final sentinel value 0 flushes the stack. Keep the maximum as an exact integer and reduce modulo 10<sup>9</sup>+7 only at the end, because taking remainders earlier would break the comparison. Time O(n)."],
    time="O(n)", space="O(n)",
    solution='''def maxMinProduct(nums):
    n = len(nums)
    pre = [0] * (n + 1)
    for i, x in enumerate(nums):
        pre[i + 1] = pre[i] + x
    best = 0
    stack = []
    for cur in range(n + 1):
        value = nums[cur] if cur < n else 0
        while stack and nums[stack[-1]] >= value:
            m = stack.pop()
            start = stack[-1] + 1 if stack else 0
            best = max(best, nums[m] * (pre[cur] - pre[start]))
        stack.append(cur)
    return best % (10 ** 9 + 7)
''',
    tests=[[[1, 2, 3, 2]], [[2, 3, 3, 1, 2]], [[3, 1, 5, 6, 4, 2]], [[5]], [[1, 1, 1, 1]], [[10000000] * 5], [[4, 3, 2, 1]], [[1, 2, 3, 4]],
           [[10000000, 1, 10000000]]],
)
_r = rnd(9605)
p["tests"].append([[_r.randint(1, 10 ** 7) for _ in range(6000)]])
p["tests"].append([[10 ** 7] * 6000])
p["tests"].append([[_r.randint(9 * 10 ** 6, 10 ** 7) for _ in range(5000)]])
p["tests"].append([[_r.randint(1, 5) for _ in range(6000)]])


def b_minprod(nums):
    best = 0
    for l in range(len(nums)):
        lo = nums[l]
        s = 0
        for r in range(l, len(nums)):
            lo = min(lo, nums[r])
            s += nums[r]
            best = max(best, lo * s)
    return best % MOD


def v_minprod(tests):
    for t in tests:
        nums = t["args"][0]
        assert 1 <= len(nums) <= 100000 and all(1 <= v <= 10 ** 7 for v in nums)
        if len(nums) <= 1500:
            assert b_minprod(nums) == t["expected"]


CHECKS["maximum-subarray-min-product-mod"] = (b_minprod, lambda r: [gen_arr(r, 1, 6, 1, 10)], "exact")
VALIDATE["maximum-subarray-min-product-mod"] = v_minprod


p = add(
    id="max-of-window-minimums-by-size", title="Best Minimum for Every Window Size", diff="Medium", topic="Stack", tier="extra",
    fn="bestMinimumPerSize", params=[("nums", "int[]")], ret="int[]", cmp="exact",
    desc="<p>For every window size <code>k</code> from 1 to <code>n</code>, look at all contiguous windows of <code>k</code> consecutive elements of <code>nums</code> and take the minimum of each window. Let <code>ans[k-1]</code> be the <em>largest</em> of those minimums. Return the array <code>ans</code> of length <code>n</code>.</p><p>Example: for <code>[10, 20, 30, 50, 10, 70, 30]</code> the answer is <code>[70, 30, 20, 10, 10, 10, 10]</code>. For size 2 the window minimums are 10, 20, 30, 10, 10, 30, whose maximum is 30.</p>",
    constraints=["1 &le; nums.length &le; 100,000", "-10<sup>9</sup> &le; nums[i] &le; 10<sup>9</sup>"],
    hints=["Computing every window minimum for every size is O(n<sup>2</sup>) with a running minimum. Instead of fixing the size, fix the element that is the minimum.",
           "If <code>nums[i]</code> is the smallest element in a stretch of length <code>len</code> (bounded by smaller elements on both sides), then <code>nums[i]</code> is the minimum of some window of every size from 1 up to <code>len</code>.",
           "Compute <code>len</code> for each <code>i</code> with a monotonic stack and record <code>ans[len-1] = max(ans[len-1], nums[i])</code>. Then sweep from large sizes to small ones doing <code>ans[k] = max(ans[k], ans[k+1])</code>, since a window of size k+1 contains a window of size k with a minimum at least as big."],
    editorial=["For an index <code>i</code> let <code>L</code> and <code>R</code> be the nearest strictly smaller elements on each side (or the borders). The stretch <code>L+1..R-1</code> has length <code>len = R - L - 1</code> and <code>nums[i]</code> is its minimum. A window of size exactly <code>len</code> placed on that stretch has minimum <code>nums[i]</code>, so <code>ans[len-1] &ge; nums[i]</code>. Shorter windows inside the stretch that still contain <code>i</code> also have minimum <code>nums[i]</code>, which is handled by the sweep below.",
               "The answer is non-increasing in the window size: any window of size k+1 contains a window of size k whose minimum is at least as large. After placing every <code>nums[i]</code> at <code>ans[len-1]</code>, a backward pass <code>ans[k] = max(ans[k], ans[k+1])</code> propagates the values to smaller sizes. Size n always has an entry because the global minimum owns a stretch of length n. The stacks give all stretch lengths in O(n), so the whole algorithm is O(n)."],
    time="O(n)", space="O(n)",
    solution='''def bestMinimumPerSize(nums):
    n = len(nums)
    left = [-1] * n
    right = [n] * n
    stack = []
    for i in range(n):
        while stack and nums[stack[-1]] >= nums[i]:
            right[stack.pop()] = i
        left[i] = stack[-1] if stack else -1
        stack.append(i)
    NEG = -(10 ** 18)
    ans = [NEG] * (n + 1)
    for i in range(n):
        length = right[i] - left[i] - 1
        if nums[i] > ans[length]:
            ans[length] = nums[i]
    for k in range(n - 1, 0, -1):
        if ans[k + 1] > ans[k]:
            ans[k] = ans[k + 1]
    return ans[1:]
''',
    tests=[[[10, 20, 30, 50, 10, 70, 30]], [[5]], [[1, 2, 3]], [[3, 2, 1]], [[4, 4, 4]], [[-3, 5, -7, 2]], [[2, 1, 2]], [[-10 ** 9 // 2, 10 ** 9]],
           [[7, 7, 1, 7, 7]]],
)
_r = rnd(9606)
p["tests"].append([[_r.randint(-10 ** 5, 10 ** 5) for _ in range(3500)]])
p["tests"].append([list(range(3000, 0, -1))])
p["tests"].append([[_r.randint(1, 4) for _ in range(3500)]])


def b_windows(nums):
    n = len(nums)
    res = []
    for k in range(1, n + 1):
        res.append(max(min(nums[i:i + k]) for i in range(n - k + 1)))
    return res


def v_windows(tests):
    for t in tests:
        nums = t["args"][0]
        assert 1 <= len(nums) <= 100000 and all(-10 ** 9 <= v <= 10 ** 9 for v in nums)
        if len(nums) <= 300:
            assert b_windows(nums) == t["expected"]


CHECKS["max-of-window-minimums-by-size"] = (b_windows, lambda r: [gen_arr(r, -4, 4, 1, 10)], "exact")
VALIDATE["max-of-window-minimums-by-size"] = v_windows


p = add(
    id="smallest-subsequence-each-letter-once", title="Smallest Subsequence With Every Letter Once", diff="Medium", topic="Stack", tier="must",
    fn="smallestDistinctSubsequence", params=[("s", "string")], ret="string", cmp="exact",
    desc="<p>Given a string <code>s</code> of lowercase letters, return the lexicographically smallest <em>subsequence</em> of <code>s</code> that contains every distinct letter of <code>s</code> exactly once. A subsequence keeps the original relative order of the characters it keeps.</p><p>Example: <code>s = \"cbacdcbc\"</code> gives <code>\"acdb\"</code>, and <code>s = \"bcabc\"</code> gives <code>\"abc\"</code>.</p>",
    constraints=["1 &le; s.length &le; 10,000", "s consists of lowercase English letters"],
    hints=["Every distinct letter has to appear once, so the answer has as many characters as there are distinct letters. The question is which occurrence of each letter to keep.",
           "Build the answer from left to right. When a new letter <code>c</code> arrives and the last kept letter is larger than <code>c</code>, removing that larger letter would improve the result, but only if it still occurs later in the string.",
           "Keep a stack for the answer, a set of letters already on the stack, and the last index of each letter. Skip letters already on the stack. Otherwise pop while the top is larger than <code>c</code> and appears again later, then push <code>c</code>."],
    editorial=["Scan left to right with a stack that holds the answer so far. A letter that is already on the stack is skipped: the earlier copy sits at least as far left, which can only help. For a new letter <code>c</code>, look at the top of the stack. If the top is larger than <code>c</code> and the same letter occurs again later in <code>s</code>, then dropping it and placing it later gives a smaller string and loses nothing, so pop it and repeat. Finally push <code>c</code>.",
               "The condition 'occurs again later' is answered in O(1) from a table of last occurrences, and membership from a boolean array of 26 entries. Each character is pushed and popped at most once, so the time is O(n) and the extra space is O(1) besides the stack (at most 26 characters). This is the same greedy as 'remove k digits', except that the amount we may delete is dictated by which letters still have a spare copy ahead."],
    time="O(n)", space="O(1)",
    solution='''def smallestDistinctSubsequence(s):
    last = {ch: i for i, ch in enumerate(s)}
    stack = []
    on_stack = set()
    for i, ch in enumerate(s):
        if ch in on_stack:
            continue
        while stack and stack[-1] > ch and last[stack[-1]] > i:
            on_stack.discard(stack.pop())
        stack.append(ch)
        on_stack.add(ch)
    return "".join(stack)
''',
    tests=[["cbacdcbc"], ["bcabc"], ["a"], ["aaaa"], ["abc"], ["cba"], ["abacb"], ["edebace"], ["zyxzyx"], ["bbcaac"], ["leetcode"]],
)
_r = rnd(9607)
p["tests"].append(["".join(_r.choice("abcdefghijklmnopqrstuvwxyz") for _ in range(8000))])
p["tests"].append(["".join(_r.choice("abcde") for _ in range(9000))])
p["tests"].append(["zyxwvutsrqponmlkjihgfedcba" * 300])
p["tests"].append(["abcdefghijklmnopqrstuvwxyz" * 300])


def b_distinct_sub(s):
    need = len(set(s))
    best = None
    n = len(s)
    for mask in range(1 << n):
        if bin(mask).count("1") != need:
            continue
        t = "".join(s[i] for i in range(n) if mask >> i & 1)
        if len(set(t)) == need and (best is None or t < best):
            best = t
    return best


def g_distinct_sub(r):
    return ["".join(r.choice("abcd") for _ in range(r.randint(1, 11)))]


def v_distinct_sub(tests):
    for t in tests:
        s = t["args"][0]
        assert 1 <= len(s) <= 10000 and set(s) <= set("abcdefghijklmnopqrstuvwxyz")
        e = t["expected"]
        assert sorted(e) == sorted(set(s))
        it = iter(s)
        assert all(ch in it for ch in e), "not a subsequence"


CHECKS["smallest-subsequence-each-letter-once"] = (b_distinct_sub, g_distinct_sub, "exact")
VALIDATE["smallest-subsequence-each-letter-once"] = v_distinct_sub


p = add(
    id="lexicographically-smallest-subsequence-k", title="Most Competitive Subsequence of Length K", diff="Medium", topic="Stack", tier="common",
    fn="smallestSubsequenceOfLengthK", params=[("nums", "int[]"), ("k", "int")], ret="int[]", cmp="exact",
    desc="<p>Choose exactly <code>k</code> elements of <code>nums</code>, keeping their original order, so that the chosen sequence is as small as possible in lexicographic order. Sequences are compared element by element from the left; the first position where they differ decides, and the one with the smaller value there is smaller.</p><p>Return that smallest subsequence. Example: <code>nums = [3, 5, 2, 6]</code> and <code>k = 2</code> gives <code>[2, 6]</code>.</p>",
    constraints=["1 &le; k &le; nums.length &le; 100,000", "-10<sup>9</sup> &le; nums[i] &le; 10<sup>9</sup>"],
    hints=["Compare candidate answers: the very first element matters most, so you want the smallest possible first element. How far to the right can the first element sit and still leave room for k-1 more?",
           "Deleting <code>n - k</code> elements is the same as choosing <code>k</code>. When a new element is smaller than the last kept one, removing the last kept one makes the sequence smaller, as long as enough elements remain to still reach length <code>k</code>.",
           "Keep a stack. For each element at index <code>i</code>, pop while the top is larger than it and <code>len(stack) - 1 + (n - i) &ge; k</code> (so after the pop there are still enough elements left). Push the element if the stack has fewer than <code>k</code> items. The stack is the answer."],
    editorial=["This is the 'remove digits to make the smallest number' greedy on arbitrary values. Process the elements left to right and keep a stack that is the best sequence found so far. If the current value is smaller than the top and we can afford to drop the top (the elements still unread plus the stack minus one are enough to fill <code>k</code> slots), dropping it can only make the sequence lexicographically smaller, because the current value now takes an earlier position.",
               "After the pops, push the current element only if the stack has fewer than <code>k</code> elements; otherwise the element is discarded, since a full stack that could not be improved by it must be kept as is. Every element enters and leaves the stack at most once, so the time is O(n) and the space O(k)."],
    time="O(n)", space="O(k)",
    solution='''def smallestSubsequenceOfLengthK(nums, k):
    n = len(nums)
    stack = []
    for i, x in enumerate(nums):
        while stack and stack[-1] > x and len(stack) - 1 + (n - i) >= k:
            stack.pop()
        if len(stack) < k:
            stack.append(x)
    return stack
''',
    tests=[[[3, 5, 2, 6], 2], [[2, 4, 3, 3, 5, 4, 9, 6], 4], [[7], 1], [[5, 4, 3, 2, 1], 3], [[1, 2, 3, 4, 5], 3], [[2, 2, 2, 2], 2],
           [[9, 1, 8, 1, 7], 3], [[-1, -5, 3, -5, 0], 2], [[4, 6, 5], 3], [[10 ** 9, -10 ** 9, 10 ** 9], 1]],
)
_r = rnd(9608)
_a = [_r.randint(-10 ** 6, 10 ** 6) for _ in range(6000)]
p["tests"].append([_a, 2500])
p["tests"].append([_a, 1])
p["tests"].append([[_r.randint(0, 9) for _ in range(6000)], 5999])
p["tests"].append([list(range(6000, 0, -1)), 3000])


def b_compete(nums, k):
    return list(min(itertools.combinations(nums, k)))


def g_compete(r):
    a = gen_arr(r, -3, 3, 1, 9)
    return [a, r.randint(1, len(a))]


def v_compete(tests):
    for t in tests:
        nums, k = t["args"]
        assert 1 <= k <= len(nums) <= 100000 and all(-10 ** 9 <= v <= 10 ** 9 for v in nums)
        assert len(t["expected"]) == k
        it = iter(nums)
        assert all(x in it for x in t["expected"]), "not a subsequence"


CHECKS["lexicographically-smallest-subsequence-k"] = (b_compete, g_compete, "exact")
VALIDATE["lexicographically-smallest-subsequence-k"] = v_compete


p = add(
    id="largest-value-ending-132-pattern", title="Largest Value That Can End a 132 Pattern", diff="Medium", topic="Stack", tier="extra",
    fn="largestEndOf132", params=[("nums", "int[]")], ret="int", cmp="exact",
    desc="<p>A <em>132 pattern</em> is a triple of indices <code>i &lt; j &lt; k</code> with <code>nums[i] &lt; nums[k] &lt; nums[j]</code>. Among all 132 patterns in <code>nums</code>, find the largest possible value of <code>nums[k]</code> (the last element of the pattern) and return it. If the array contains no 132 pattern, return <code>-1</code>.</p><p>Example: <code>[3, 1, 4, 2]</code> contains the pattern (1, 4, 2) and no other, so the answer is <code>2</code>. In <code>[1, 6, 4, 5, 3, 2, 7]</code> the best pattern is (1, 6, 5), so the answer is <code>5</code>.</p>",
    constraints=["1 &le; nums.length &le; 100,000", "1 &le; nums[i] &le; 10<sup>9</sup>"],
    hints=["Checking all triples is O(n<sup>3</sup>). Fix the <code>nums[i]</code> and ask: among the elements to its right, which values can play the '2' of a 132 pair, meaning some earlier larger element exists between <code>i</code> and it?",
           "Scan from right to left. For the suffix after <code>i</code> let <code>third</code> be the largest value that has a strictly larger element somewhere to its left inside that suffix. If <code>third &gt; nums[i]</code>, then <code>nums[i]</code> works as the '1' with that value.",
           "Maintain a stack of values, popping all values smaller than the current element and updating <code>third = max(third, popped)</code> (those popped values have a bigger element on their left, the current one). Before processing an element <code>x</code>, if <code>x &lt; third</code> the value <code>third</code> is achievable; the answer is the largest such <code>third</code>."],
    editorial=["Scanning from the right, let <code>third</code> be the maximum over all pairs (j, k) in the suffix with <code>j &lt; k</code> and <code>nums[k] &lt; nums[j]</code> of <code>nums[k]</code>. A pattern with first element <code>nums[i]</code> exists exactly when <code>nums[i] &lt; third</code>, and then the best last element is <code>third</code> itself, because any larger candidate would already be included in the maximum. So the answer is the largest <code>third</code> seen at an index where <code>nums[i] &lt; third</code>.",
               "To maintain <code>third</code>, keep a stack of the values to the right of the current position, with the largest values nearest the bottom (the stack is non-increasing from bottom to top). When the current value <code>x</code> arrives, pop every stack value smaller than <code>x</code>: each popped value has <code>x</code> as a larger element on its left, so it is a valid '2' and may raise <code>third</code>. Then push <code>x</code>. Because <code>third</code> never decreases as the scan moves left, we simply record <code>third</code> whenever the current element lies below it and keep the maximum. Every value is pushed and popped once, so the time is O(n) and the space O(n)."],
    time="O(n)", space="O(n)",
    solution='''def largestEndOf132(nums):
    stack = []
    third = 0      # best '2' value found in the suffix (values are >= 1)
    best = -1
    for i in range(len(nums) - 1, -1, -1):
        x = nums[i]
        if x < third:
            best = max(best, third)
        while stack and stack[-1] < x:
            third = max(third, stack.pop())
        stack.append(x)
    return best
''',
    tests=[[[3, 1, 4, 2]], [[1, 6, 4, 5, 3, 2, 7]], [[1, 3, 2]], [[4, 3, 2, 1]], [[1, 2, 3, 4]], [[5]], [[1, 1, 1]], [[2, 4, 1, 3]], [[1, 4, 3, 3]],
           [[1, 10 ** 9, 5, 10 ** 9 - 1]]],
)
_r = rnd(9609)
p["tests"].append([[_r.randint(1, 10 ** 9) for _ in range(5000)]])
p["tests"].append([list(range(6000, 0, -1))])
p["tests"].append([list(range(1, 6001))])
p["tests"].append([[_r.randint(1, 30) for _ in range(5000)]])
p["tests"].append([[6000 - i if i % 2 == 0 else 7000 + i for i in range(1, 5001)]])


def b_132(nums):
    n = len(nums)
    best = -1
    for i in range(n):
        for j in range(i + 1, n):
            for k in range(j + 1, n):
                if nums[i] < nums[k] < nums[j]:
                    best = max(best, nums[k])
    return best


def v_132(tests):
    for t in tests:
        nums = t["args"][0]
        assert 1 <= len(nums) <= 100000 and all(1 <= v <= 10 ** 9 for v in nums)
        if len(nums) <= 60:
            assert b_132(nums) == t["expected"]


CHECKS["largest-value-ending-132-pattern"] = (b_132, lambda r: [gen_arr(r, 1, 8, 1, 10)], "exact")
VALIDATE["largest-value-ending-132-pattern"] = v_132


# ---------------------------------------------------------------- HARD

p = add(
    id="total-strength-of-wizard-groups", title="Total Strength of Every Contiguous Group", diff="Hard", topic="Stack", tier="extra",
    fn="totalStrength", params=[("strength", "int[]")], ret="int", cmp="exact",
    desc="<p>A row of wizards has individual strengths given by <code>strength</code>. The strength of a contiguous group is defined as <em>(the weakest wizard in the group) &times; (the sum of all strengths in the group)</em>.</p><p>Return the sum of the strengths of <em>all</em> non-empty contiguous groups, modulo <code>1,000,000,007</code>.</p><p>Example: for <code>[1, 3, 1, 2]</code> the answer is <code>44</code>. For <code>[5, 4, 6]</code> it is <code>213</code>.</p>",
    constraints=["1 &le; strength.length &le; 100,000", "1 &le; strength[i] &le; 10<sup>9</sup>", "Return the sum modulo 1,000,000,007"],
    hints=["The number of groups is O(n<sup>2</sup>); for n = 100,000 you need something like O(n). Use the contribution idea: handle all groups at once by the position of their weakest wizard.",
           "For wizard <code>i</code>, let <code>L</code> and <code>R</code> be the boundaries within which it is the minimum (tie-break so each group has one owner). The groups it owns are all <code>[l, r]</code> with <code>L &lt; l &le; i &le; r &lt; R</code>. You need the sum of the group sums over this whole family, multiplied by <code>strength[i]</code>.",
           "With prefix sums <code>P</code>, a group sum is <code>P[r+1] - P[l]</code>. Summing it over all pairs (l, r) needs sums of consecutive prefix sums, so build prefix sums <code>Q</code> of <code>P</code>. Then the total over the family is <code>(i-L) * (sum of P[i+1..R]) - (R-i) * (sum of P[L+1..i])</code>, each a difference of two <code>Q</code> values."],
    editorial=["Let <code>L</code> be the nearest index on the left with a strictly smaller strength (or -1) and <code>R</code> the nearest index on the right with a smaller-or-equal strength (or n); with this tie-break each group is owned by exactly one wizard. Wizard <code>i</code> owns every group <code>[l, r]</code> with <code>L &lt; l &le; i</code> and <code>i &le; r &lt; R</code>, and contributes <code>strength[i] * sum(group sums)</code>.",
               "Let <code>P[t]</code> be the sum of the first <code>t</code> strengths, and <code>Q[t] = P[0] + ... + P[t-1]</code>. Then summing over r and l independently gives total group sums <code>(i - L) * (Q[R+1] - Q[i+1]) - (R - i) * (Q[i+1] - Q[L+1])</code>: the first term adds <code>P[r+1]</code> for each of the <code>i - L</code> choices of l, the second subtracts <code>P[l]</code> for each of the <code>R - i</code> choices of r. The boundaries <code>L</code> and <code>R</code> come from monotonic stacks. The whole thing is O(n) time and space. Python integers are unbounded; in fixed-width languages keep all values reduced modulo 10<sup>9</sup>+7 and take care with the subtraction."],
    time="O(n)", space="O(n)",
    solution='''def totalStrength(strength):
    MOD = 10 ** 9 + 7
    n = len(strength)
    P = [0] * (n + 1)
    for i, x in enumerate(strength):
        P[i + 1] = P[i] + x
    Q = [0] * (n + 2)
    for t in range(n + 1):
        Q[t + 1] = Q[t] + P[t]
    left = [-1] * n    # nearest strictly smaller on the left
    right = [n] * n    # nearest smaller-or-equal on the right
    stack = []
    for i in range(n):
        while stack and strength[stack[-1]] >= strength[i]:
            right[stack.pop()] = i
        left[i] = stack[-1] if stack else -1
        stack.append(i)
    total = 0
    for i in range(n):
        L, R = left[i], right[i]
        sums = (i - L) * (Q[R + 1] - Q[i + 1]) - (R - i) * (Q[i + 1] - Q[L + 1])
        total += strength[i] * sums
    return total % MOD
''',
    tests=[[[1, 3, 1, 2]], [[5, 4, 6]], [[7]], [[1, 1, 1]], [[1, 2, 3, 4, 5]], [[5, 4, 3, 2, 1]], [[10 ** 9, 10 ** 9]], [[2, 9, 2, 9, 2]],
           [[3, 1, 3, 1, 3, 1]]],
)
_r = rnd(9610)
p["tests"].append([[_r.randint(1, 10 ** 9) for _ in range(6000)]])
p["tests"].append([[10 ** 9] * 5000])
p["tests"].append([[_r.randint(1, 10) for _ in range(6000)]])
p["tests"].append([list(range(1, 5001))])


def b_strength(strength):
    total = 0
    for l in range(len(strength)):
        lo = strength[l]
        s = 0
        for r in range(l, len(strength)):
            lo = min(lo, strength[r])
            s += strength[r]
            total += lo * s
    return total % MOD


def v_strength(tests):
    for t in tests:
        a = t["args"][0]
        assert 1 <= len(a) <= 100000 and all(1 <= v <= 10 ** 9 for v in a)
        if len(a) <= 1500:
            assert b_strength(a) == t["expected"]


CHECKS["total-strength-of-wizard-groups"] = (b_strength, lambda r: [gen_arr(r, 1, 6, 1, 10)], "exact")
VALIDATE["total-strength-of-wizard-groups"] = v_strength


p = add(
    id="create-maximum-number-from-two-arrays", title="Create the Maximum Number From Two Digit Arrays", diff="Hard", topic="Stack", tier="extra",
    fn="createMaxNumber", params=[("nums1", "int[]"), ("nums2", "int[]"), ("k", "int")], ret="int[]", cmp="exact",
    desc="<p>The arrays <code>nums1</code> and <code>nums2</code> hold decimal digits (values 0 to 9). Build a sequence of exactly <code>k</code> digits by choosing some digits from <code>nums1</code> and some from <code>nums2</code> (possibly none from one of them). The chosen digits from each array must keep their relative order from that array, but digits of the two arrays may be interleaved in any way.</p><p>Return the digit sequence that, read as a number, is the largest. All candidates have exactly <code>k</code> digits, so this is the lexicographically largest sequence.</p><p>Example: <code>nums1 = [3, 4, 6, 5]</code>, <code>nums2 = [9, 1, 2, 5, 8, 3]</code>, <code>k = 5</code> gives <code>[9, 8, 6, 5, 3]</code>.</p>",
    constraints=["1 &le; nums1.length, nums2.length &le; 200", "0 &le; nums1[i], nums2[i] &le; 9", "1 &le; k &le; nums1.length + nums2.length"],
    hints=["If you knew how many digits <code>i</code> come from <code>nums1</code> (and <code>k - i</code> from <code>nums2</code>), the problem would split into two simpler ones. Try every feasible <code>i</code>.",
           "For a single array, the best subsequence of length <code>t</code> is found with a monotonic stack: drop smaller digits in front of a larger digit while you still have spare deletions (the 'remove k digits' idea, maximizing instead of minimizing).",
           "Merge two chosen subsequences greedily: at each step take the next digit from the sequence whose <em>remaining suffix</em> is lexicographically larger (not just the larger next digit, ties must be broken by looking further). Compare all <code>i</code> results and keep the largest."],
    editorial=["Split by the number of digits taken from the first array. For each feasible <code>i</code> (from <code>max(0, k - len(nums2))</code> to <code>min(k, len(nums1))</code>), take the best length-<code>i</code> subsequence of <code>nums1</code> and the best length-<code>(k-i)</code> subsequence of <code>nums2</code>. The best subsequence of a single array is found by a monotonic stack that pops a smaller digit when a larger one arrives and deletions are still available (at most <code>len - t</code> of them).",
               "Then merge the two subsequences into the largest sequence. At each step compare the remaining parts of the two sequences as lists (the comparison of suffixes, not only of their first digits, because equal leading digits must be resolved by looking further) and take the head of the larger one. The best result over all <code>i</code> is the answer. Choosing the subsequences independently is safe because merging cannot reorder digits inside a subsequence, and the optimal final sequence uses the optimal subsequence of each array for its own counts. Complexity is O(k * (m + n)) for the stacks plus O(k) merges per split, each merge costing up to O(k) in comparisons; with m, n &le; 200 this is tiny."],
    time="O(k * (m + n) * k) worst case, small for m, n ≤ 200", space="O(k)",
    solution='''def createMaxNumber(nums1, nums2, k):
    def best_of(nums, t):
        drop = len(nums) - t
        stack = []
        for d in nums:
            while drop and stack and stack[-1] < d:
                stack.pop()
                drop -= 1
            stack.append(d)
        return stack[:t]

    def merge(a, b):
        res = []
        i = j = 0
        while i < len(a) or j < len(b):
            if a[i:] >= b[j:]:
                res.append(a[i])
                i += 1
            else:
                res.append(b[j])
                j += 1
        return res

    best = []
    for i in range(max(0, k - len(nums2)), min(k, len(nums1)) + 1):
        cand = merge(best_of(nums1, i), best_of(nums2, k - i))
        if cand > best:
            best = cand
    return best
''',
    tests=[[[3, 4, 6, 5], [9, 1, 2, 5, 8, 3], 5], [[6, 7], [6, 0, 4], 5], [[3, 9], [8, 9], 3], [[5], [5], 1], [[0], [0, 0], 3], [[1, 2, 3], [4, 5, 6], 6],
           [[9, 9, 9], [9, 9], 4], [[2, 5, 6, 4, 4, 0], [7, 3, 8, 0, 6, 5, 7, 6, 2], 15], [[8, 9], [3], 2], [[1, 6, 5, 4, 7, 3, 9, 5, 3, 7, 8, 4, 1, 1, 4], [4, 3, 1, 3, 5, 9], 21]],
)
_r = rnd(9611)
p["tests"].append([[_r.randint(0, 9) for _ in range(200)], [_r.randint(0, 9) for _ in range(200)], 200])
p["tests"].append([[_r.randint(0, 9) for _ in range(200)], [_r.randint(0, 9) for _ in range(200)], 400])
p["tests"].append([[7] * 200, [7] * 200, 250])
p["tests"].append([[_r.choice([0, 1]) for _ in range(200)], [_r.choice([0, 1]) for _ in range(180)], 150])


def b_maxnum(nums1, nums2, k):
    @lru_cache(maxsize=None)
    def f(i, j, rem):
        if rem == 0:
            return ()
        best = None
        for cand in ((nums1[i],) + f(i + 1, j, rem - 1) if i < len(nums1) and f(i + 1, j, rem - 1) is not None else None,
                     (nums2[j],) + f(i, j + 1, rem - 1) if j < len(nums2) and f(i, j + 1, rem - 1) is not None else None,
                     f(i + 1, j, rem) if i < len(nums1) else None,
                     f(i, j + 1, rem) if j < len(nums2) else None):
            if cand is not None and (best is None or cand > best):
                best = cand
        return best
    nums1, nums2 = tuple(nums1), tuple(nums2)
    return list(f(0, 0, k))


def g_maxnum(r):
    m, n = r.randint(1, 6), r.randint(1, 6)
    d = r.choice([2, 4, 10])
    return [[r.randrange(d) for _ in range(m)], [r.randrange(d) for _ in range(n)], r.randint(1, m + n)]


def v_maxnum(tests):
    for t in tests:
        a, b, k = t["args"]
        assert 1 <= len(a) <= 200 and 1 <= len(b) <= 200 and 1 <= k <= len(a) + len(b)
        assert all(0 <= v <= 9 for v in a + b)
        assert len(t["expected"]) == k


CHECKS["create-maximum-number-from-two-arrays"] = (b_maxnum, g_maxnum, "exact")
VALIDATE["create-maximum-number-from-two-arrays"] = v_maxnum
