"""Problems: prefix sums, 1-D range queries and equilibrium / split points (batch A). See data/lib.py for the registry."""
from bisect import bisect_left, bisect_right
from collections import Counter

from lib import add, rnd, CHECKS, VALIDATE, gen_arr  # noqa: F401

MOD = 10 ** 9 + 7
TOPIC = "Prefix Sums"


# ---------------------------------------------------------------- EASY

p = add(
    id="left-right-sum-differences", title="Left and Right Sum Differences", diff="Easy", topic=TOPIC,
    fn="leftRightDifference", params=[("nums", "int[]")], ret="int[]", cmp="exact",
    desc="<p>For every index <code>i</code> of the integer array <code>nums</code>, let <code>left[i]</code> be the sum of all elements strictly before <code>i</code> and <code>right[i]</code> the sum of all elements strictly after <code>i</code>. An empty side has sum <code>0</code>.</p><p>Return the array <code>answer</code> with <code>answer[i] = |left[i] - right[i]|</code>.</p><pre>nums = [10, 4, 8, 3]\nleft  = [0, 10, 14, 22]\nright = [15, 11, 3, 0]\nanswer = [15, 1, 11, 22]</pre>",
    constraints=["1 &le; nums.length &le; 5,000", "-1,000 &le; nums[i] &le; 1,000"],
    hints=["Computing <code>left[i]</code> and <code>right[i]</code> with two inner loops costs O(n) per index. Which parts of those sums are shared between neighbouring indices?",
           "Going from index <code>i</code> to <code>i + 1</code>, the left sum gains <code>nums[i]</code>. The right sum of <code>i + 1</code> is the right sum of <code>i</code> minus <code>nums[i + 1]</code>.",
           "Compute the total once. Keep a running <code>left</code> and get the right side as <code>total - left - nums[i]</code>, so a single pass is enough."],
    editorial=["Let <code>total</code> be the sum of the whole array and let <code>left</code> be the running sum of the elements before the current index. Everything that is neither on the left nor the element itself is on the right, so <code>right = total - left - nums[i]</code>. For each index append <code>abs(left - right)</code> and then add <code>nums[i]</code> to <code>left</code>.",
               "One pass for the total and one pass for the answers gives O(n) time. Only the output array is extra memory, so the working space beyond it is O(1). Storing full prefix and suffix arrays would give the same time but needs two more arrays."],
    time="O(n)", space="O(1) extra",
    solution='''def leftRightDifference(nums):
    total = sum(nums)
    left = 0
    out = []
    for x in nums:
        right = total - left - x
        out.append(abs(left - right))
        left += x
    return out
''',
    tests=[[[10, 4, 8, 3]], [[1]], [[0]], [[-1, -1]], [[5, 5, 5]], [[1000, -1000, 1000, -1000]], [[0, 0, 0, 0, 0]],
           [[-7, 3, 0, 9, -2]], [[1, 2, 3, 4, 5, 6]]],
)
_r = rnd(9101)
p["tests"].append([[_r.randint(-1000, 1000) for _ in range(3000)]])
p["tests"].append([[1000] * 2500])


def b_lrd(nums):
    return [abs(sum(nums[:i]) - sum(nums[i + 1:])) for i in range(len(nums))]


def v_lrd(tests):
    for t in tests:
        a = t["args"][0]
        assert 1 <= len(a) <= 5000 and all(-1000 <= x <= 1000 for x in a)


CHECKS["left-right-sum-differences"] = (b_lrd, lambda r: [gen_arr(r, -9, 9, 1, 9)], "exact")
VALIDATE["left-right-sum-differences"] = v_lrd

p = add(
    id="three-equal-sum-parts", title="Three Parts With Equal Sum", diff="Easy", topic=TOPIC,
    fn="canThreeParts", params=[("nums", "int[]")], ret="bool", cmp="exact",
    desc="<p>Decide whether the integer array <code>nums</code> can be cut into <strong>three non-empty contiguous parts</strong> (a prefix, a middle block and a suffix) whose sums are all equal. Return <code>true</code> if such a cut exists and <code>false</code> otherwise.</p><p>Values may be negative or zero.</p><pre>[0, 2, 1, -6, 6, -7, 9, 1, 2, 0, 1]  -> true   ([0,2,1] [-6,6,-7,9,1] [2,0,1], each sums to 3)\n[1, 2, 3, 4]                         -> false</pre>",
    constraints=["3 &le; nums.length &le; 8,000", "-10,000 &le; nums[i] &le; 10,000"],
    hints=["If the three parts each sum to <code>s</code>, what must the sum of the whole array be?",
           "The total must be divisible by 3 and each part must sum to <code>total / 3</code>. Walk through the array, accumulating a running sum.",
           "Every time the running sum reaches the target, count one finished part and restart the running sum at 0. If you finish three parts before the array ends (or exactly at the end), the answer is yes; with a total of 0 you may even finish more than three, which is fine."],
    editorial=["The total <code>S</code> must be divisible by 3, and each part has to sum to <code>t = S / 3</code>. Scan from the left with a running sum; whenever it equals <code>t</code>, close a part and reset the running sum to 0. If at least three parts get closed, we can merge any extra ones: the first part closed, the second part closed, and everything after as the third part. That last block sums to <code>S - 2t = t</code> and it is not empty because a third part was closed at or after its start.",
               "The case <code>S = 0</code> works with the same code: <code>t = 0</code> and each zero-sum stretch closes a part. Negative numbers do not break anything because we only compare against the exact target, never prune on size. Time is O(n) and space O(1)."],
    time="O(n)", space="O(1)",
    solution='''def canThreeParts(nums):
    total = sum(nums)
    if total % 3:
        return False
    target = total // 3
    parts = 0
    cur = 0
    for x in nums:
        cur += x
        if cur == target:
            parts += 1
            cur = 0
    return parts >= 3
''',
    tests=[[[0, 2, 1, -6, 6, -7, 9, 1, 2, 0, 1]], [[1, 2, 3, 4]], [[1, 1, 1]], [[0, 0, 0]], [[0, 0, 0, 0, 0]], [[3, 3, 6, 5, -2, 2, 5, 1, -9, 4]],
           [[1, -1, 1, -1]], [[1, 1, 1, 1, -1]], [[2, 1, 3, -3, 3]], [[5, 0, 5, 0, 5]], [[1, 2]][:0] or [[7, -7, 0]]],
)
_r = rnd(9102)


def _mk_three(r, n, target, yes=True):
    # build three blocks with equal sums, then (optionally) break the equality by +1 in one cell
    sizes = [n // 3, n // 3, n - 2 * (n // 3)]
    out = []
    for sz in sizes:
        blk = [r.randint(-50, 50) for _ in range(sz - 1)]
        blk.append(target - sum(blk))
        out += blk
    if not yes:
        out[r.randrange(n)] += 1
    return out


p["tests"].append([_mk_three(_r, 6000, 123, True)])
p["tests"].append([_mk_three(_r, 7000, -77, False)])
p["tests"].append([[0] * 8000])
p["tests"].append([[1] * 7998])


def b_three(nums):
    n = len(nums)
    for i in range(1, n - 1):
        for j in range(i + 1, n):
            if sum(nums[:i]) == sum(nums[i:j]) == sum(nums[j:]):
                return True
    return False


def g_three(r):
    if r.random() < 0.5:
        n = r.randint(3, 10)
        return [_mk_three(r, n, r.randint(-3, 3), r.random() < 0.7)]
    return [gen_arr(r, -2, 2, 3, 10)]


def v_three(tests):
    for t in tests:
        a = t["args"][0]
        assert 3 <= len(a) <= 8000 and all(-10000 <= x <= 10000 for x in a)
    assert any(t["expected"] for t in tests) and not all(t["expected"] for t in tests)


CHECKS["three-equal-sum-parts"] = (b_three, g_three, "exact")
VALIDATE["three-equal-sum-parts"] = v_three

p = add(
    id="max-score-after-binary-split", title="Best Score of a Binary Split", diff="Easy", topic=TOPIC,
    fn="maxSplitScore", params=[("bits", "int[]")], ret="int", cmp="exact",
    desc="<p>The array <code>bits</code> contains only <code>0</code> and <code>1</code>. Cut it at one position into two <strong>non-empty</strong> contiguous parts, a left part and a right part. The score of the cut is the number of <code>0</code>s in the left part plus the number of <code>1</code>s in the right part.</p><p>Return the largest score over all possible cuts.</p><pre>bits = [0, 1, 1, 0, 1]\ncut after index 0: left [0] has 1 zero, right [1,1,0,1] has 3 ones -> 4\ncut after index 3: left [0,1,1,0] has 2 zeros, right [1] has 1 one -> 3\nanswer = 4</pre>",
    constraints=["2 &le; bits.length &le; 10,000", "bits[i] is 0 or 1"],
    hints=["There are only <code>n - 1</code> cut positions. Counting zeros and ones for each cut from scratch is O(n) each; how can neighbouring cuts share work?",
           "Moving the cut one step to the right moves a single element from the right part to the left part. How does the score change if that element is a 0? If it is a 1?",
           "Start with the total number of ones as the 'right ones'. Sweep the cut from left to right: a moved 0 adds one to the zeros on the left, a moved 1 removes one from the ones on the right. Track the best score over the n - 1 valid cuts."],
    editorial=["Let <code>zerosLeft</code> be the zeros in the left part and <code>onesRight</code> the ones in the right part. Start with an empty left part: <code>zerosLeft = 0</code> and <code>onesRight = total ones</code>. Extend the left part one element at a time: a 0 increases <code>zerosLeft</code>, a 1 decreases <code>onesRight</code>. After each extension (but only while the right part is still non-empty) evaluate <code>zerosLeft + onesRight</code> and keep the maximum.",
               "Equivalently, the score is <code>zeros(prefix) + (ones_total - ones(prefix))</code>, a prefix-sum expression. The sweep runs in O(n) time with O(1) memory. Mind the non-empty rule: the cut after the last element is not allowed, so the loop stops one element early."],
    time="O(n)", space="O(1)",
    solution='''def maxSplitScore(bits):
    ones_right = sum(bits)
    zeros_left = 0
    best = -1
    for i in range(len(bits) - 1):
        if bits[i] == 0:
            zeros_left += 1
        else:
            ones_right -= 1
        best = max(best, zeros_left + ones_right)
    return best
''',
    tests=[[[0, 1, 1, 0, 1]], [[0, 0]], [[1, 1]], [[1, 0]], [[0, 1]], [[1, 1, 1, 1]], [[0, 0, 0, 0, 0]], [[1, 0, 0, 1, 1, 0]],
           [[0, 1, 0, 1, 0, 1, 0, 1]], [[1, 0, 1, 0, 1, 0, 1]]],
)
_r = rnd(9103)
p["tests"].append([[_r.randint(0, 1) for _ in range(8000)]])
p["tests"].append([[1] * 5000 + [0] * 3000])
p["tests"].append([[0] * 4000 + [1] * 4000])


def b_split(bits):
    return max(bits[:i].count(0) + bits[i:].count(1) for i in range(1, len(bits)))


def v_split(tests):
    for t in tests:
        a = t["args"][0]
        assert 2 <= len(a) <= 10000 and all(x in (0, 1) for x in a)


CHECKS["max-score-after-binary-split"] = (b_split, lambda r: [gen_arr(r, 0, 1, 2, 10)], "exact")
VALIDATE["max-score-after-binary-split"] = v_split


# ---------------------------------------------------------------- MEDIUM

p = add(
    id="minimum-average-difference-split", title="Minimum Average Difference", diff="Medium", topic=TOPIC,
    fn="minAvgDiffIndex", params=[("nums", "int[]")], ret="int", cmp="exact",
    desc="<p>For an index <code>i</code> of the array <code>nums</code>, split the array into the first <code>i + 1</code> elements (the <em>head</em>) and the remaining <code>n - i - 1</code> elements (the <em>tail</em>). The <em>average difference</em> of <code>i</code> is the absolute value of <code>floor(average of head) - floor(average of tail)</code>. The average of an empty tail is defined as <code>0</code>, and an average is the sum divided by the element count, rounded down.</p><p>Return the index with the <strong>smallest</strong> average difference. If several indices tie, return the smallest of them.</p><pre>nums = [2, 5, 3, 9, 5, 3]\ni=0: |2 - 5| = 3   i=1: |3 - 5| = 2   i=2: |3 - 5| = 2\ni=3: |4 - 4| = 0   i=4: |4 - 3| = 1   i=5: |4 - 0| = 4\nanswer = 3</pre>",
    constraints=["1 &le; nums.length &le; 10,000", "0 &le; nums[i] &le; 100,000"],
    hints=["Each index needs the sum of its head and the sum of its tail. Recomputing both costs O(n) per index.",
           "The head sum grows by <code>nums[i]</code> as <code>i</code> moves right, and the tail sum is the total minus the head sum.",
           "Keep a running head sum, derive the tail sum from the total, divide with integer (floor) division by <code>i + 1</code> and by <code>n - i - 1</code> (use 0 when the tail is empty), and update the best only on a strictly smaller difference so ties keep the earliest index."],
    editorial=["Compute the total once. Sweeping <code>i</code> from left to right, maintain <code>head</code>, the sum of <code>nums[0..i]</code>. Then <code>tail = total - head</code>, and both averages come from floor division. The tail average is 0 when <code>i = n - 1</code>. Keep the index with the smallest difference; replacing the best only when the new difference is strictly smaller yields the smallest index among ties.",
               "This is a one-pass prefix-sum sweep: O(n) time and O(1) space. The sums stay below 10<sup>9</sup> (10,000 elements of at most 100,000), which fits in 32 bits, although the averages are all that matter for the comparison. Because every value is non-negative, floor division behaves the same in every language."],
    time="O(n)", space="O(1)",
    solution='''def minAvgDiffIndex(nums):
    n = len(nums)
    total = sum(nums)
    head = 0
    best, best_i = None, 0
    for i, x in enumerate(nums):
        head += x
        tail = total - head
        a = head // (i + 1)
        b = tail // (n - i - 1) if i < n - 1 else 0
        d = abs(a - b)
        if best is None or d < best:
            best, best_i = d, i
    return best_i
''',
    tests=[[[2, 5, 3, 9, 5, 3]], [[0]], [[4, 5]], [[0, 0, 0]], [[1, 1, 1, 1]], [[5, 0, 0, 0]], [[0, 0, 0, 7]], [[100000, 0, 100000]],
           [[3, 1, 4, 1, 5, 9, 2, 6]], [[8, 8, 1, 1, 8, 8]]],
)
_r = rnd(9104)
p["tests"].append([[_r.randint(0, 100000) for _ in range(6000)]])
p["tests"].append([[_r.randint(0, 3) for _ in range(8000)]])
p["tests"].append([[100000] * 6000])


def b_minavg(nums):
    n = len(nums)
    best = None
    bi = 0
    for i in range(n):
        a = sum(nums[:i + 1]) // (i + 1)
        b = sum(nums[i + 1:]) // (n - i - 1) if i < n - 1 else 0
        d = abs(a - b)
        if best is None or d < best:
            best, bi = d, i
    return bi


def v_minavg(tests):
    for t in tests:
        a = t["args"][0]
        assert 1 <= len(a) <= 10000 and all(0 <= x <= 100000 for x in a)


CHECKS["minimum-average-difference-split"] = (b_minavg, lambda r: [gen_arr(r, 0, 12, 1, 9)], "exact")
VALIDATE["minimum-average-difference-split"] = v_minavg

p = add(
    id="fair-array-removal-count", title="Fair Array After One Removal", diff="Medium", topic=TOPIC,
    fn="countFairRemovals", params=[("nums", "int[]")], ret="int", cmp="exact",
    desc="<p>An array is <em>fair</em> if the sum of its elements at even positions (0, 2, 4, ...) equals the sum of its elements at odd positions (1, 3, 5, ...).</p><p>Count the indices <code>i</code> such that removing <code>nums[i]</code> leaves a fair array. After a removal, all later elements shift one position to the left, so their parity of position flips. Each index is tested independently on the original array. An array with a single element left (position 0, no odd elements) is fair only if that element is <code>0</code>; an empty array is fair.</p><pre>nums = [2, 1, 6, 4]\nremove index 0 -> [1, 6, 4]: even 5, odd 6\nremove index 1 -> [2, 6, 4]: even 6, odd 6  fair\nremove index 2 -> [2, 1, 4]: even 6, odd 1\nremove index 3 -> [2, 1, 6]: even 8, odd 1\nanswer = 1</pre>",
    constraints=["1 &le; nums.length &le; 10,000", "-10,000 &le; nums[i] &le; 10,000"],
    hints=["Simulating each removal and re-summing is O(n) per index, O(n<sup>2</sup>) in total. What part of the array keeps its parities after removing index <code>i</code>?",
           "Elements before <code>i</code> keep their positions. Elements after <code>i</code> all move one place left, so even-position elements there become odd-position ones and vice versa.",
           "Prefix sums of even-position and odd-position elements give the sums before <code>i</code>; the matching suffix sums come from the totals. New even sum = even before <code>i</code> + odd after <code>i</code>, new odd sum = odd before <code>i</code> + even after <code>i</code>."],
    editorial=["Let <code>E</code> and <code>O</code> be the sums of the original even- and odd-position elements. While scanning, keep <code>pe</code> and <code>po</code>: the even- and odd-position sums strictly before the current index. The sums strictly after index <code>i</code> are then <code>E - pe - (nums[i] if i is even)</code> for even positions and <code>O - po - (nums[i] if i is odd)</code> for odd positions; call them <code>se</code> and <code>so</code>.",
               "After removing index <code>i</code> the elements before it are unchanged, and those after it swap parity. The array is fair exactly when <code>pe + so == po + se</code>. Count the indices for which this holds. One pass with O(1) extra state gives O(n) time and O(1) space. The empty and single-element cases fall out of the same formula."],
    time="O(n)", space="O(1)",
    solution='''def countFairRemovals(nums):
    E = sum(nums[0::2])
    O = sum(nums[1::2])
    pe = po = 0
    count = 0
    for i, x in enumerate(nums):
        se = E - pe - (x if i % 2 == 0 else 0)
        so = O - po - (x if i % 2 == 1 else 0)
        if pe + so == po + se:
            count += 1
        if i % 2 == 0:
            pe += x
        else:
            po += x
    return count
''',
    tests=[[[2, 1, 6, 4]], [[1, 1, 1]], [[1, 2, 3]], [[5]], [[0]], [[0, 0, 0, 0]], [[1, -1]], [[3, 3, 3, 3, 3]], [[4, 1, 4, 1, 4, 1, 4]],
           [[-5, 5, -5, 5, 0]]],
)
_r = rnd(9105)
p["tests"].append([[_r.randint(-10000, 10000) for _ in range(6000)]])
p["tests"].append([[_r.randint(-1, 1) for _ in range(8000)]])
p["tests"].append([[0] * 7000])


def b_fair(nums):
    c = 0
    for i in range(len(nums)):
        a = nums[:i] + nums[i + 1:]
        if sum(a[0::2]) == sum(a[1::2]):
            c += 1
    return c


def v_fair(tests):
    for t in tests:
        a = t["args"][0]
        assert 1 <= len(a) <= 10000 and all(-10000 <= x <= 10000 for x in a)


CHECKS["fair-array-removal-count"] = (b_fair, lambda r: [gen_arr(r, -2, 2, 1, 9)], "exact")
VALIDATE["fair-array-removal-count"] = v_fair

p = add(
    id="circular-range-sum-queries", title="Circular Range Sums", diff="Medium", topic=TOPIC,
    fn="circularSums", params=[("nums", "int[]"), ("queries", "int[][]")], ret="int[]", cmp="exact",
    desc="<p>The array <code>nums</code> is arranged on a circle: after the last element comes the first one again. Each query is a pair <code>[start, length]</code>. It asks for the sum of <code>length</code> consecutive elements read clockwise from index <code>start</code>, wrapping around the end of the array as often as needed (a length larger than <code>n</code> goes around the circle more than once).</p><p>Return the answer of every query, in order.</p><pre>nums = [3, -1, 4, 1, 5]\n[1, 3]  -> -1 + 4 + 1 = 4\n[3, 4]  -> 1 + 5 + 3 + (-1) = 8\n[0, 12] -> two full laps (24) + 3 + (-1) = 26\nresult = [4, 8, 26]</pre>",
    constraints=["1 &le; nums.length &le; 5,000", "-1,000 &le; nums[i] &le; 1,000", "1 &le; queries.length &le; 5,000", "0 &le; start &lt; nums.length, 1 &le; length &le; 100,000"],
    hints=["Simulating each query costs O(length). With long queries and many of them that is far too slow.",
           "A query of length <code>L</code> contains <code>L // n</code> complete laps, each worth exactly the total sum of the array, plus a leftover of <code>L % n</code> elements.",
           "Build a prefix sum array <code>pre</code>. The leftover starts at <code>start</code> and may wrap: if <code>start + rem &le; n</code> it is <code>pre[start + rem] - pre[start]</code>, otherwise it is <code>pre[n] - pre[start] + pre[start + rem - n]</code>."],
    editorial=["Split the query into whole laps and a remainder: <code>laps, rem = divmod(length, n)</code>. The laps contribute <code>laps * total</code>. The remainder is a window of <code>rem &lt; n</code> elements beginning at <code>start</code>. If it does not cross the end of the array (<code>start + rem &le; n</code>) it is an ordinary prefix-sum difference. Otherwise it is the tail from <code>start</code> to the end plus the head of length <code>start + rem - n</code>, each of which is a prefix-sum difference as well.",
               "Preprocessing is O(n) and each query O(1), so the total is O(n + q). The largest possible answer is 100,000 &times; 1,000 = 10<sup>8</sup> in absolute value, which fits in 32 bits."],
    time="O(n + q)", space="O(n)",
    solution='''def circularSums(nums, queries):
    n = len(nums)
    pre = [0]
    for x in nums:
        pre.append(pre[-1] + x)
    total = pre[n]
    out = []
    for start, length in queries:
        laps, rem = divmod(length, n)
        end = start + rem
        if end <= n:
            part = pre[end] - pre[start]
        else:
            part = pre[n] - pre[start] + pre[end - n]
        out.append(laps * total + part)
    return out
''',
    tests=[[[3, -1, 4, 1, 5], [[1, 3], [3, 4], [0, 12]]], [[7], [[0, 1], [0, 5]]], [[1, 2, 3], [[2, 1], [2, 2], [2, 3], [2, 4]]],
           [[-2, -3], [[1, 100000], [0, 99999]]], [[0, 0, 0], [[1, 7]]], [[1000, 1000, 1000, 1000], [[3, 100000], [1, 4], [0, 1]]],
           [[5, -5, 5, -5, 5], [[4, 2], [4, 6], [0, 5], [2, 11]]], [[9, 8, 7, 6], [[3, 2], [2, 3], [1, 8]]]],
)
_r = rnd(9106)
_a = [_r.randint(-1000, 1000) for _ in range(5000)]
p["tests"].append([_a, [[_r.randrange(5000), _r.randint(1, 100000)] for _ in range(3500)]])
_a = [_r.randint(-5, 5) for _ in range(4000)]
p["tests"].append([_a, [[_r.randrange(4000), _r.randint(1, 9000)] for _ in range(1500)]])
p["tests"].append([[1000] * 5000, [[4999, 100000], [0, 99999], [2500, 5000]]])


def b_circ(nums, queries):
    n = len(nums)
    return [sum(nums[(s + k) % n] for k in range(L)) for s, L in queries]


def g_circ(r):
    nums = gen_arr(r, -9, 9, 1, 7)
    n = len(nums)
    return [nums, [[r.randrange(n), r.randint(1, 25)] for _ in range(r.randint(1, 6))]]


def v_circ(tests):
    for t in tests:
        nums, qs = t["args"]
        assert 1 <= len(nums) <= 5000 and all(-1000 <= x <= 1000 for x in nums)
        assert 1 <= len(qs) <= 5000
        assert all(0 <= s < len(nums) and 1 <= L <= 100000 for s, L in qs)


CHECKS["circular-range-sum-queries"] = (b_circ, g_circ, "exact")
VALIDATE["circular-range-sum-queries"] = v_circ

p = add(
    id="binary-array-three-equal-ones-ways", title="Split Into Three With Equal Ones", diff="Medium", topic=TOPIC,
    fn="countEqualOnesSplits", params=[("bits", "int[]")], ret="int", cmp="exact",
    desc="<p>The array <code>bits</code> contains only <code>0</code> and <code>1</code>. Count the ways to cut it into <strong>three non-empty contiguous parts</strong> so that every part contains the same number of <code>1</code>s. Two ways are different if their cut positions differ.</p><p>Return the count modulo <code>1,000,000,007</code>.</p><pre>bits = [1, 0, 1, 0, 1]  -> 4\n[1 | 0 1 | 0 1]  [1 | 0 1 0 | 1]  [1 0 | 1 | 0 1]  [1 0 | 1 0 | 1]\nbits = [0, 0, 0, 0]     -> 3   (any two of the three gaps)</pre>",
    constraints=["3 &le; bits.length &le; 10,000", "bits[i] is 0 or 1"],
    hints=["Count the ones first. If the count is not divisible by 3, no cut can work.",
           "If there are no ones at all, any two distinct cut positions work. Otherwise each part needs exactly <code>k = ones / 3</code> ones, which pins down which ones belong to which part.",
           "Let <code>pos</code> list the indices of the ones. The first cut can be anywhere in the run of zeros between <code>pos[k-1]</code> and <code>pos[k]</code>, and the second cut anywhere between <code>pos[2k-1]</code> and <code>pos[2k]</code>. Multiply the two choice counts."],
    editorial=["Let <code>ones</code> be the number of 1s. If <code>ones % 3 != 0</code> the answer is 0. If <code>ones == 0</code> every pair of the <code>n - 1</code> cut gaps is valid, giving <code>(n - 1)(n - 2) / 2</code> ways.",
               "Otherwise let <code>k = ones / 3</code> and <code>pos</code> the list of positions of the ones (0-indexed). The first part must contain <code>pos[0..k-1]</code> and none of <code>pos[k..]</code>, so its right end can be any index from <code>pos[k-1]</code> up to <code>pos[k] - 1</code>: that is <code>pos[k] - pos[k-1]</code> choices. In the same way the second cut has <code>pos[2k] - pos[2k-1]</code> choices. The two choices are independent, so the answer is their product, taken modulo 10<sup>9</sup>+7.",
               "This is prefix counting in disguise: the cut positions are the places where the prefix count of ones equals <code>k</code> and <code>2k</code>. Time O(n), space O(n) for <code>pos</code> (or O(1) when counting runs on the fly)."],
    time="O(n)", space="O(n)",
    solution='''def countEqualOnesSplits(bits):
    MOD = 1000000007
    n = len(bits)
    pos = [i for i, b in enumerate(bits) if b == 1]
    ones = len(pos)
    if ones % 3:
        return 0
    if ones == 0:
        return (n - 1) * (n - 2) // 2 % MOD
    k = ones // 3
    return (pos[k] - pos[k - 1]) * (pos[2 * k] - pos[2 * k - 1]) % MOD
''',
    tests=[[[1, 0, 1, 0, 1]], [[0, 0, 0, 0]], [[0, 0, 0]], [[1, 1, 1]], [[1, 1, 0]], [[1, 0, 0, 1, 1, 0, 0, 1, 0, 1, 0, 0]],
           [[0, 1, 0, 1, 0, 1, 0]], [[1, 1, 1, 1, 1, 1]], [[1, 0, 1, 0, 1, 0, 0]], [[1, 1, 0, 1, 1, 0, 1, 1]]],
)
_r = rnd(9107)
p["tests"].append([[0] * 10000])
p["tests"].append([[1] + [0] * 3000 + [1] + [0] * 3000 + [1] + [0] * 3995])
_a = [_r.randint(0, 1) for _ in range(9000)]
while sum(_a) % 3:
    _a[_r.randrange(9000)] ^= 1
p["tests"].append([_a])


def b_ones(bits):
    n = len(bits)
    pre = [0]
    for b in bits:
        pre.append(pre[-1] + b)
    c = 0
    for i in range(1, n - 1):
        for j in range(i + 1, n):
            if pre[i] == pre[j] - pre[i] == pre[n] - pre[j]:
                c += 1
    return c % MOD


def v_ones(tests):
    for t in tests:
        a = t["args"][0]
        assert 3 <= len(a) <= 10000 and all(x in (0, 1) for x in a)
    assert any(t["expected"] == 0 for t in tests) and any(t["expected"] > 0 for t in tests)


CHECKS["binary-array-three-equal-ones-ways"] = (b_ones, lambda r: [gen_arr(r, 0, 1, 3, 12)], "exact")
VALIDATE["binary-array-three-equal-ones-ways"] = v_ones

p = add(
    id="balanced-range-split-queries", title="Balanced Split in a Range", diff="Medium", topic=TOPIC,
    fn="balancedRangeQueries", params=[("nums", "int[]"), ("queries", "int[][]")], ret="int[]", cmp="exact",
    desc="<p>You are given an array <code>nums</code> of <strong>positive</strong> integers and a list of queries <code>[l, r]</code>. For a query, look only at the subarray <code>nums[l..r]</code> (both ends included) and decide whether it can be cut at one place into two <strong>non-empty</strong> parts, a left part and a right part, with equal sums.</p><p>Return an array with one entry per query, in order: <code>1</code> if such a cut exists and <code>0</code> otherwise. A subarray with a single element can never be cut.</p><pre>nums = [2, 1, 1, 4, 3, 5]\n[0, 2] -> 1   ([2] | [1, 1])\n[1, 3] -> 0   (total 6, but prefixes 1, 2, 6 never reach 3)\n[0, 5] -> 1   ([2,1,1,4] | [3,5], both 8)\n[3, 3] -> 0\nresult = [1, 0, 1, 0]</pre>",
    constraints=["1 &le; nums.length &le; 5,000", "1 &le; nums[i] &le; 1,000", "1 &le; queries.length &le; 5,000", "0 &le; l &le; r &lt; nums.length"],
    hints=["For one query you could try every cut and compare the two sums, but that is O(length) per query. What must be true about the total of the subarray?",
           "With prefix sums <code>pre</code>, the subarray total is <code>pre[r+1] - pre[l]</code>. A balanced cut has a left part summing to exactly half of that, so the total must be even.",
           "All values are positive, so the prefix sums are strictly increasing and every value occurs at most once. Look up the wanted prefix value <code>pre[l] + total/2</code> in a dictionary that maps prefix value to index; any hit lies strictly inside the range automatically."],
    editorial=["Build the prefix array <code>pre</code> with <code>pre[0] = 0</code>. For a query <code>[l, r]</code> the sum is <code>total = pre[r+1] - pre[l]</code>. If <code>total</code> is odd there is no equal split. Otherwise a cut after index <code>m</code> (with <code>l &le; m &lt; r</code>) works exactly when <code>pre[m+1] = pre[l] + total/2</code>.",
               "Because every element is positive, the prefix sums strictly increase. So each value is attained at most once and we can store them in a dictionary for O(1) lookup. If the wanted value is present, it is strictly greater than <code>pre[l]</code> and strictly smaller than <code>pre[r+1]</code> (since <code>total &gt; 0</code> whenever the range is non-empty), so it corresponds to a valid non-empty split. For a single element <code>total/2</code> is positive and smaller than the element, so no prefix value matches, which agrees with the rule.",
               "Preprocessing is O(n) and each query O(1): O(n + q) overall. If zeros or negatives were allowed, the lookup would need the first/last occurrence of each value and a binary search on the positions."],
    time="O(n + q)", space="O(n)",
    solution='''def balancedRangeQueries(nums, queries):
    pre = [0]
    for x in nums:
        pre.append(pre[-1] + x)
    where = {v: i for i, v in enumerate(pre)}
    out = []
    for l, r in queries:
        total = pre[r + 1] - pre[l]
        if total % 2:
            out.append(0)
        else:
            out.append(1 if (pre[l] + total // 2) in where else 0)
    return out
''',
    tests=[[[2, 1, 1, 4, 3, 5], [[0, 2], [1, 3], [0, 5], [3, 3]]], [[5], [[0, 0]]], [[4, 4], [[0, 1], [0, 0], [1, 1]]],
           [[1, 2, 3], [[0, 2], [0, 1], [1, 2]]], [[1, 1, 1, 1], [[0, 3], [0, 2], [1, 2], [1, 3]]], [[3, 1, 2, 2, 1, 3], [[0, 5], [1, 4], [2, 3], [0, 3]]],
           [[1000, 1000, 1000], [[0, 2], [0, 1]]], [[1, 1, 2, 4, 8, 16], [[0, 5], [0, 4], [2, 5], [1, 5]]]],
)
_r = rnd(9108)
_a = [_r.randint(1, 1000) for _ in range(5000)]
_q = []
for _ in range(3500):
    _l = _r.randrange(5000)
    _q.append([_l, _r.randint(_l, 4999)])
p["tests"].append([_a, _q])
_a = [_r.randint(1, 3) for _ in range(5000)]
_q = []
for _ in range(2500):
    _l = _r.randrange(5000)
    _q.append([_l, min(4999, _l + _r.randint(0, 40))])
p["tests"].append([_a, _q])
p["tests"].append([[1] * 5000, [[0, 4999], [0, 4998], [10, 20], [3, 3], [7, 8]]])


def b_balrange(nums, queries):
    out = []
    for l, r in queries:
        sub = nums[l:r + 1]
        ok = 0
        for m in range(1, len(sub)):
            if sum(sub[:m]) == sum(sub[m:]):
                ok = 1
        out.append(ok)
    return out


def g_balrange(r):
    nums = gen_arr(r, 1, 4, 1, 10)
    qs = []
    for _ in range(r.randint(1, 8)):
        l = r.randrange(len(nums))
        qs.append([l, r.randint(l, len(nums) - 1)])
    return [nums, qs]


def v_balrange(tests):
    for t in tests:
        nums, qs = t["args"]
        assert 1 <= len(nums) <= 5000 and all(1 <= x <= 1000 for x in nums)
        assert 1 <= len(qs) <= 5000 and all(0 <= l <= r < len(nums) for l, r in qs)
    ex = [v for t in tests for v in t["expected"]]
    assert 0 in ex and 1 in ex


CHECKS["balanced-range-split-queries"] = (b_balrange, g_balrange, "exact")
VALIDATE["balanced-range-split-queries"] = v_balrange

p = add(
    id="equal-sum-split-with-one-move", title="Equal Halves After Moving One Element", diff="Medium", topic=TOPIC,
    fn="canBalanceWithOneMove", params=[("nums", "int[]")], ret="bool", cmp="exact",
    desc="<p>Cut the array <code>nums</code> at some position into a non-empty left part (a prefix) and a non-empty right part (the rest). You may then <strong>move at most one element</strong> from one part into the other part (its position inside the receiving part does not matter, only the sums do). The move must not empty the part it comes from.</p><p>Return <code>true</code> if some cut together with at most one such move makes the two parts have equal sums, and <code>false</code> otherwise. Values may be negative.</p><pre>[2, 4, 1, 3]  -> true   (cut [2] | [4, 1, 3]; move 3 left: [2, 3] and [4, 1], both 5)\n[1, 1, 1, 10] -> false</pre>",
    constraints=["2 &le; nums.length &le; 8,000", "-1,000 &le; nums[i] &le; 1,000"],
    hints=["Fix a cut and let <code>d = leftSum - rightSum</code>. If <code>d = 0</code> you are already done. What does moving one element <code>x</code> do to <code>d</code>?",
           "Moving <code>x</code> from the left part to the right part changes <code>d</code> by <code>-2x</code>; moving from right to left changes it by <code>+2x</code>. So you need <code>d</code> to be even and an element of value exactly <code>d / 2</code> in the left part, or of value <code>-d / 2</code> in the right part (values can be negative, so either side may help whatever the sign of <code>d</code>).",
           "Sweep the cut to the right while maintaining a set of the values in the left part and a counter for the right part. At each cut check the three cases: <code>d = 0</code>; <code>d</code> even and the left part holds <code>d/2</code> (with at least 2 elements on the left); <code>d</code> even and the right part holds <code>-d/2</code> (with at least 2 elements on the right)."],
    editorial=["For a fixed cut let <code>d = L - R</code>. Moving an element of value <code>x</code> from the left to the right gives sums <code>L - x</code> and <code>R + x</code>, which are equal exactly when <code>d = 2x</code>. Moving from the right to the left needs <code>-d = 2x</code>. Hence a cut works if <code>d = 0</code>, or if <code>d</code> is even and the left part contains the value <code>d/2</code>, or if <code>d</code> is even and the right part contains the value <code>-d/2</code>. Because elements may be negative, both options must be tried whatever the sign of <code>d</code>. The side we take an element from must have at least two elements so that it stays non-empty.",
               "Slide the cut from left to right. The prefix sum gives <code>L</code> and <code>R = total - L</code>. Keep a set with the distinct values of the left part and a <code>Counter</code> for the right part; moving the cut one step transfers a single element from the counter to the set. Every cut is processed in O(1), so the whole algorithm runs in O(n) time with O(n) space."],
    time="O(n)", space="O(n)",
    solution='''def canBalanceWithOneMove(nums):
    n = len(nums)
    total = sum(nums)
    left_vals = set()
    right_cnt = {}
    for x in nums:
        right_cnt[x] = right_cnt.get(x, 0) + 1
    L = 0
    for p in range(1, n):
        x = nums[p - 1]
        L += x
        left_vals.add(x)
        right_cnt[x] -= 1
        d = L - (total - L)
        if d == 0:
            return True
        if d % 2:
            continue
        h = d // 2
        if p >= 2 and h in left_vals:
            return True
        if n - p >= 2 and right_cnt.get(-h, 0) > 0:
            return True
    return False
''',
    tests=[[[2, 4, 1, 3]], [[1, 1, 1, 10]], [[1, 1]], [[1, 2]], [[5, 1, 1, 1, 1, 1]], [[1, 2, 3, 4, 5]], [[0, 0, 7]], [[-3, 6, 1, 2]],
           [[10, -10, 3]], [[4, 4, 4, 4, 1]], [[1, 3, 4, 100]], [[2, 2, 2, 2, 2, 2, 7]]],
)
_r = rnd(9109)
_a = [_r.randint(-1000, 1000) for _ in range(6000)]
p["tests"].append([_a])
_a = [2 * _r.randint(1, 500) for _ in range(7000)]   # all even
_a.append(1)
p["tests"].append([_a])
p["tests"].append([[1000] * 7999 + [999]])


def b_move(nums):
    n = len(nums)
    for p in range(1, n):
        A, B = nums[:p], nums[p:]
        if sum(A) == sum(B):
            return True
        for i in range(len(A)):
            if len(A) >= 2 and sum(A) - A[i] == sum(B) + A[i]:
                return True
        for i in range(len(B)):
            if len(B) >= 2 and sum(A) + B[i] == sum(B) - B[i]:
                return True
    return False


def v_move(tests):
    for t in tests:
        a = t["args"][0]
        assert 2 <= len(a) <= 8000 and all(-1000 <= x <= 1000 for x in a)
    assert any(t["expected"] for t in tests) and not all(t["expected"] for t in tests)


CHECKS["equal-sum-split-with-one-move"] = (b_move, lambda r: [gen_arr(r, -5, 5, 2, 8)], "exact")
VALIDATE["equal-sum-split-with-one-move"] = v_move


# ---------------------------------------------------------------- HARD

p = add(
    id="max-pivots-after-one-change", title="Most Pivots After One Change", diff="Hard", topic=TOPIC, tier="extra",
    fn="maxPivotsAfterChange", params=[("nums", "int[]"), ("k", "int")], ret="int", cmp="exact",
    desc="<p>A <em>pivot</em> of an array is a position <code>p</code> with <code>1 &le; p &le; n - 1</code> such that <code>nums[0] + ... + nums[p-1] = nums[p] + ... + nums[n-1]</code>, i.e. the prefix before <code>p</code> and the suffix from <code>p</code> have the same sum.</p><p>You may replace <strong>at most one</strong> element of <code>nums</code> by the value <code>k</code> (or leave the array alone). Return the largest possible number of pivots.</p><pre>nums = [2, -1, 2], k = 3\nno change: pivots 0 (p=1: 2 vs 1, p=2: 1 vs 2)\nchange nums[0] to 3 -> [3, -1, 2]: p=2 gives 2 vs 2, so 1 pivot\nanswer = 1</pre>",
    constraints=["2 &le; nums.length &le; 6,000", "-100,000 &le; nums[i], k &le; 100,000"],
    hints=["Trying every index and re-counting pivots takes O(n) per index, O(n<sup>2</sup>) in total. For a fixed position <code>p</code>, let <code>diff[p] = prefixSum(p) - suffixSum(p)</code>; a pivot is just <code>diff[p] = 0</code>.",
           "Changing <code>nums[i]</code> by <code>delta = k - nums[i]</code> shifts <code>diff[p]</code> by <code>+delta</code> for every split <code>p &gt; i</code> (element in the left part) and by <code>-delta</code> for every split <code>p &le; i</code> (element in the right part). Splits are affected on only two sides.",
           "Store the <code>diff</code> values of the splits on each side of <code>i</code> in two hash counters. The pivots after changing index <code>i</code> number <code>right[-delta] + left[delta]</code>. Sweep <code>i</code> from left to right, moving split <code>p = i</code> from the right counter to the left one, and take the maximum together with the unchanged count."],
    editorial=["Let <code>pre[p]</code> be the sum of the first <code>p</code> elements and <code>diff[p] = pre[p] - (total - pre[p])</code> for <code>p = 1..n-1</code>. The array has as many pivots as there are zeros among the <code>diff</code> values.",
               "Replace <code>nums[i]</code> by <code>k</code> and put <code>delta = k - nums[i]</code>. Splits <code>p &gt; i</code> have element <code>i</code> in their left part: left grows by <code>delta</code>, the right is unchanged, so <code>diff[p] + delta</code> must be 0. Splits <code>p &le; i</code> have it in their right part, so <code>diff[p] - delta</code> must be 0. The number of pivots after this change is therefore <code>#{p &gt; i : diff[p] = -delta} + #{p &le; i : diff[p] = delta}</code>.",
               "Keep a counter <code>right</code> filled with all diffs and an empty counter <code>left</code>. For <code>i = 0..n-1</code>, first move <code>diff[i]</code> (if <code>1 &le; i &le; n-1</code>) from <code>right</code> to <code>left</code>, then evaluate the formula in O(1). The answer is the maximum of that and the count with no change. Time O(n), space O(n). All intermediate values fit comfortably in 64-bit integers (and the sums stay within 10<sup>9</sup>)."],
    time="O(n)", space="O(n)",
    solution='''def maxPivotsAfterChange(nums, k):
    n = len(nums)
    pre = [0]
    for x in nums:
        pre.append(pre[-1] + x)
    total = pre[n]
    diff = [0] * n
    right = {}
    for q in range(1, n):
        diff[q] = 2 * pre[q] - total
        right[diff[q]] = right.get(diff[q], 0) + 1
    left = {}
    best = right.get(0, 0)
    for i in range(n):
        if 1 <= i <= n - 1:
            d = diff[i]
            right[d] -= 1
            left[d] = left.get(d, 0) + 1
        delta = k - nums[i]
        best = max(best, right.get(-delta, 0) + left.get(delta, 0))
    return best
''',
    tests=[[[2, -1, 2], 3], [[0, 0, 0], 1], [[0, 0, 0], 0], [[22, 4, -25, -20, -15, 15, -16, 7, 19, -10, 0, -13, -14], -33], [[1, 1], 1],
           [[1, 2], 2], [[5, 5], 100000], [[3, 1, 2], 0], [[1, -1, 1, -1, 1, -1], 1], [[4, 1, 3, 4, 1, 3], 7], [[-100000, 100000, 0], -100000]],
)
_r = rnd(9110)
_a = [(1 if i % 2 == 0 else -1) for i in range(5000)]
p["tests"].append([_a, 1])
_a = [_r.randint(-3, 3) for _ in range(5500)]
p["tests"].append([_a, _r.randint(-3, 3)])
_a = [_r.randint(-100000, 100000) for _ in range(5000)]
p["tests"].append([_a, 99999])
_a = [0] * 3000 + [5] + [0] * 2999
p["tests"].append([_a, 0])


def b_pivots(nums, k):
    def cnt(a):
        return sum(1 for q in range(1, len(a)) if sum(a[:q]) == sum(a[q:]))
    best = cnt(nums)
    for i in range(len(nums)):
        a = nums[:]
        a[i] = k
        best = max(best, cnt(a))
    return best


def g_pivots(r):
    n = r.randint(2, 9)
    a = [r.randint(-3, 3) for _ in range(n)]
    if r.random() < 0.5:
        a = [r.choice([-1, 0, 1]) for _ in range(n)]
    return [a, r.randint(-3, 3)]


def v_pivots(tests):
    for t in tests:
        a, k = t["args"]
        assert 2 <= len(a) <= 6000 and all(-100000 <= x <= 100000 for x in a) and -100000 <= k <= 100000
    assert len({t["expected"] for t in tests}) >= 4


CHECKS["max-pivots-after-one-change"] = (b_pivots, g_pivots, "exact")
VALIDATE["max-pivots-after-one-change"] = v_pivots

p = add(
    id="count-nondecreasing-three-way-splits", title="Count Ordered Three-Way Splits", diff="Hard", topic=TOPIC, tier="extra",
    fn="countOrderedSplits", params=[("nums", "int[]")], ret="int", cmp="exact",
    desc="<p>Choose two cut positions <code>i</code> and <code>j</code> with <code>1 &le; i &lt; j &le; n - 1</code> to split <code>nums</code> into three non-empty contiguous parts: <code>A = nums[0..i-1]</code>, <code>B = nums[i..j-1]</code> and <code>C = nums[j..n-1]</code>.</p><p>The split is <em>ordered</em> if <code>sum(A) &le; sum(B) &le; sum(C)</code>. Return the number of ordered splits. Elements may be negative or zero, so the usual two-pointer argument for positive numbers does not apply.</p><pre>nums = [1, 2, 2, 2, 5, 0]\n(i=1,j=2): 1 | 2 | 2 2 5 0 -> sums 1, 2, 9  ordered\n(i=1,j=3): 1 | 2 2 | 2 5 0 -> sums 1, 4, 7  ordered\n(i=1,j=4): 1 | 2 2 2 | 5 0 -> sums 1, 6, 5  not ordered\n(i=2,j=4): 1 2 | 2 2 | 5 0 -> sums 3, 4, 5  ordered\nall other pairs fail, so the answer is 3</pre>",
    constraints=["3 &le; nums.length &le; 8,000", "-1,000 &le; nums[i] &le; 1,000", "The answer is at most about 3.2 &times; 10<sup>7</sup>, so it fits in 32 bits"],
    hints=["Checking all pairs <code>(i, j)</code> is O(n<sup>2</sup>) with prefix sums, which is too slow for n = 8,000 in many settings and gives no insight. Rewrite the two conditions in terms of prefix sums <code>pre[i]</code> and <code>pre[j]</code> and the total <code>T</code>.",
           "<code>sum(A) &le; sum(B)</code> is <code>2 pre[i] &le; pre[j]</code>, and <code>sum(B) &le; sum(C)</code> is <code>pre[i] &ge; 2 pre[j] - T</code>. For a fixed <code>j</code> you want to count the earlier indices <code>i &lt; j</code> whose prefix sum lies in a value interval.",
           "Process <code>j</code> from left to right, inserting <code>pre[i]</code> for each new <code>i = j - 1</code> into a Fenwick tree over the coordinate-compressed prefix values, and for each <code>j</code> query how many inserted values fall in <code>[2 pre[j] - T, floor(pre[j] / 2)]</code>."],
    editorial=["With <code>pre[x]</code> the sum of the first <code>x</code> elements and <code>T = pre[n]</code>: <code>sum(A) = pre[i]</code>, <code>sum(B) = pre[j] - pre[i]</code> and <code>sum(C) = T - pre[j]</code>. The ordering becomes <code>2 pre[i] &le; pre[j]</code> and <code>2 pre[j] - T &le; pre[i]</code>. For a fixed <code>j</code> that means <code>pre[i]</code> lies in <code>[2 pre[j] - T, floor(pre[j] / 2)]</code>; the floor is correct for negative values too because <code>2x &le; p</code> holds exactly when <code>x &le; floor(p / 2)</code>.",
               "With only positive numbers the valid <code>i</code> would form a contiguous range found by two pointers. With negative numbers the prefix sums are not monotone, so we count <em>values</em> in an interval among the earlier indices. Sort the distinct prefix values <code>pre[1..n-2]</code> and use a Fenwick tree (BIT) of counts over them. For <code>j = 2..n-1</code> insert <code>pre[j-1]</code>, then locate the interval ends with binary search and take a difference of two prefix queries.",
               "Every step costs O(log n), so the total time is O(n log n) with O(n) space. A 2D-looking counting problem became a one-dimensional range count by moving the dependence on <code>i</code> into the data structure."],
    time="O(n log n)", space="O(n)",
    solution='''def countOrderedSplits(nums):
    from bisect import bisect_left, bisect_right
    n = len(nums)
    pre = [0]
    for x in nums:
        pre.append(pre[-1] + x)
    T = pre[n]
    vals = sorted(set(pre[1:n - 1]))
    m = len(vals)
    tree = [0] * (m + 1)

    def add(pos):
        pos += 1
        while pos <= m:
            tree[pos] += 1
            pos += pos & -pos

    def query(cnt):  # number of inserted values among the first cnt distinct values
        s = 0
        while cnt > 0:
            s += tree[cnt]
            cnt -= cnt & -cnt
        return s

    total = 0
    for j in range(2, n):
        add(bisect_left(vals, pre[j - 1]))
        lo = 2 * pre[j] - T
        hi = pre[j] // 2
        if lo <= hi:
            total += query(bisect_right(vals, hi)) - query(bisect_left(vals, lo))
    return total
''',
    tests=[[[1, 2, 2, 2, 5, 0]], [[1, 1, 1]], [[0, 0, 0]], [[3, 2, 1]], [[-1, -1, -1]], [[0, 0, 0, 0, 0, 0]], [[1, 2, 3, 4, 5, 6, 7]],
           [[-5, 5, 0, 0, 5, -5, 10]], [[5, -3, 8, -2, 4, 7, -6, 9]], [[1, -1, 1, -1, 1, -1, 1, -1]], [[7, 0, 0, 0, 7]]],
)
_r = rnd(9111)
p["tests"].append([[_r.randint(-1000, 1000) for _ in range(5000)]])
p["tests"].append([[_r.randint(0, 3) for _ in range(6000)]])
p["tests"].append([[_r.randint(-5, 30) for _ in range(5000)]])
p["tests"].append([[0] * 4000])


def b_ordered(nums):
    n = len(nums)
    pre = [0]
    for x in nums:
        pre.append(pre[-1] + x)
    c = 0
    for i in range(1, n - 1):
        for j in range(i + 1, n):
            if pre[i] <= pre[j] - pre[i] <= pre[n] - pre[j]:
                c += 1
    return c


def v_ordered(tests):
    for t in tests:
        a = t["args"][0]
        assert 3 <= len(a) <= 8000 and all(-1000 <= x <= 1000 for x in a)
    assert any(t["expected"] == 0 for t in tests) and any(t["expected"] > 0 for t in tests)


CHECKS["count-nondecreasing-three-way-splits"] = (b_ordered, lambda r: [gen_arr(r, -5, 5, 3, 12)], "exact")
VALIDATE["count-nondecreasing-three-way-splits"] = v_ordered
