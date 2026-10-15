"""Problems: sliding window, monotonic deque windows. See data/lib.py for the registry."""
from lib import add, rnd, CHECKS, VALIDATE, gen_arr  # noqa: F401

TOPIC = "Sliding Window"


# ---------------------------------------------------------------- EASY

p = add(
    id="first-negative-in-each-window", title="First Negative in Every Window", diff="Easy", topic=TOPIC,
    fn="firstNegativeInWindows", params=[("nums", "int[]"), ("k", "int")], ret="int[]", cmp="exact",
    desc="<p>For every contiguous window of exactly <code>k</code> elements of <code>nums</code>, from left to right, report the <strong>leftmost negative value</strong> inside that window, or <code>0</code> if the window contains no negative value. Return the <code>nums.length - k + 1</code> answers in window order.</p><pre>nums = [12, -1, -7, 8, -15, 30, 16, 28], k = 3\n[12,-1,-7] -> -1    [-1,-7,8] -> -1    [-7,8,-15] -> -7\n[8,-15,30] -> -15   [-15,30,16] -> -15  [30,16,28] -> 0\nresult = [-1, -1, -7, -15, -15, 0]</pre>",
    constraints=["1 &le; k &le; nums.length &le; 8,000", "-10<sup>9</sup> &le; nums[i] &le; 10<sup>9</sup>", "Zero is not negative"],
    hints=["Scanning every window from its left end costs O(n * k) in the worst case.",
           "Only negative values can ever be an answer. Remember where the negatives are, in order of position.",
           "Keep a queue of the indices of negative values. Before answering for a window, drop indices from the front that are left of the window. The front is then the first negative inside it."],
    editorial=["Only negative numbers matter, so keep a queue of their indices in increasing order. Moving the window right by one position appends the new index if the new element is negative, and the indices that fall out of the left edge are removed from the front of the queue.",
               "After that, the front of the queue (if there is one) is the leftmost negative of the window. Each index is pushed once and popped at most once, so the whole scan is O(n) time and O(k) extra space. This is the simplest use of the \"queue of candidates\" idea that the monotonic deque generalises."],
    time="O(n)", space="O(k)",
    solution='''def firstNegativeInWindows(nums, k):
    from collections import deque
    neg = deque()
    res = []
    for i, x in enumerate(nums):
        if x < 0:
            neg.append(i)
        if i >= k - 1:
            while neg and neg[0] <= i - k:
                neg.popleft()
            res.append(nums[neg[0]] if neg else 0)
    return res
''',
    tests=[[[12, -1, -7, 8, -15, 30, 16, 28], 3], [[5], 1], [[-5], 1], [[1, 2, 3], 3], [[1, 2, 3], 2], [[-1, -2, -3], 2],
           [[0, 0, -1, 0], 2], [[3, -2, 4, -1, 5], 1], [[2, -3, 5, -4], 4], [[-1000000000, 1000000000, 0, -1], 2],
           [[-1, 0, 0, 0, 0, 0, -2], 3]],
)
_r = rnd(6101)
_a = [_r.randint(1, 10**9) if _r.random() < 0.97 else -_r.randint(1, 10**9) for _ in range(4000)]
p["tests"].append([_a, 50])
_a = [_r.randint(-10**5, 10**5) for _ in range(5000)]
p["tests"].append([_a, 2500])
_a = [_r.randint(0, 10**5) for _ in range(5000)]
p["tests"].append([_a, 100])


def b_firstneg(nums, k):
    res = []
    for i in range(len(nums) - k + 1):
        v = 0
        for x in nums[i:i + k]:
            if x < 0:
                v = x
                break
        res.append(v)
    return res


def g_firstneg(r):
    a = gen_arr(r, -5, 5, 1, 12)
    return [a, r.randint(1, len(a))]


def v_firstneg(tests):
    for t in tests:
        a, k = t["args"]
        assert 1 <= k <= len(a) <= 8000
        assert all(-10**9 <= x <= 10**9 for x in a)
        assert len(t["expected"]) == len(a) - k + 1


CHECKS["first-negative-in-each-window"] = (b_firstneg, g_firstneg, "exact")
VALIDATE["first-negative-in-each-window"] = v_firstneg


p = add(
    id="queue-with-running-maximum", title="Queue With Constant-Time Maximum", diff="Easy", topic=TOPIC,
    fn="runMaxQueue", params=[("ops", "int[][]")], ret="int[]", cmp="exact",
    desc="<p>Simulate a first-in-first-out queue of integers that supports three operations. Each operation is a pair <code>[type, value]</code>:</p><ul><li><code>[1, x]</code> adds <code>x</code> at the back of the queue.</li><li><code>[2, 0]</code> removes the element at the front of the queue.</li><li><code>[3, 0]</code> reports the <strong>largest value currently in the queue</strong>.</li></ul><p>Return the answers of all type 3 operations in the order they occur. The queue is never empty when a type 2 or type 3 operation is executed, and the input contains at least one type 3 operation. Every operation should take amortized O(1) time.</p><pre>ops = [[1,3],[1,1],[3,0],[2,0],[3,0],[1,5],[3,0],[2,0],[3,0]]\nqueue [3,1] -> max 3;  pop 3 -> [1] -> max 1;  push 5 -> [1,5] -> max 5\npop 1 -> [5] -> max 5\nresult = [3, 1, 5, 5]</pre>",
    constraints=["1 &le; ops.length &le; 8,000", "ops[i] = [type, value] with type in {1, 2, 3}; value is 0 for types 2 and 3", "-10<sup>9</sup> &le; x &le; 10<sup>9</sup> for type 1", "Type 2 and type 3 operations only occur on a non-empty queue"],
    hints=["Calling <code>max()</code> on the queue contents for every query is O(n) per query.",
           "When a large value is pushed, every smaller value that is already in the queue (and was pushed earlier) can never be the maximum again: it leaves the queue before the large one does.",
           "Keep a second deque holding a non-increasing sequence of values. On push, pop smaller values off its back first. On pop, if the removed value equals the front of this deque, remove that front too. The front is the maximum."],
    editorial=["Besides the real queue, keep a deque <code>best</code> of values in non-increasing order. When <code>x</code> is pushed, every smaller value at the back of <code>best</code> is dominated: it is older than <code>x</code> and smaller, so it will be removed from the queue first and can never be the maximum. Pop those values, then append <code>x</code>.",
               "The maximum is always <code>best[0]</code>. When the real queue pops a value <code>v</code>, <code>v</code> is also <code>best[0]</code> exactly when it was the maximum (equal values stay in <code>best</code> because only strictly smaller values are removed), so in that case pop the front of <code>best</code> too. Every value enters and leaves each deque once: O(1) amortized per operation, O(n) space. The same structure is what makes the sliding window maximum run in linear time."],
    time="O(n)", space="O(n)",
    solution='''def runMaxQueue(ops):
    from collections import deque
    q = deque()
    best = deque()
    out = []
    for t, x in ops:
        if t == 1:
            q.append(x)
            while best and best[-1] < x:
                best.pop()
            best.append(x)
        elif t == 2:
            v = q.popleft()
            if best[0] == v:
                best.popleft()
        else:
            out.append(best[0])
    return out
''',
    tests=[[[[1, 3], [1, 1], [3, 0], [2, 0], [3, 0], [1, 5], [3, 0], [2, 0], [3, 0]]],
           [[[1, 7], [3, 0]]],
           [[[1, 4], [1, 4], [1, 2], [3, 0], [2, 0], [3, 0], [2, 0], [3, 0], [2, 0], [1, -3], [3, 0]]],
           [[[1, -5], [1, -9], [3, 0], [2, 0], [3, 0]]],
           [[[1, 1], [1, 2], [1, 3], [1, 4], [3, 0], [2, 0], [3, 0], [2, 0], [3, 0], [2, 0], [3, 0]]],
           [[[1, 9], [1, 8], [1, 7], [3, 0], [2, 0], [3, 0], [2, 0], [3, 0]]],
           [[[1, 2], [3, 0], [3, 0], [3, 0]]],
           [[[1, 1000000000], [1, -1000000000], [2, 0], [3, 0], [1, 1000000000], [2, 0], [3, 0]]],
           [[[1, 5], [1, 3], [1, 5], [2, 0], [3, 0], [2, 0], [3, 0], [1, 6], [2, 0], [3, 0]]],
           [[[1, 0], [2, 0], [1, 0], [3, 0]]]],
)


def _gen_ops(r, n, lo, hi, push_bias=0.5):
    ops, size = [], 0
    for _ in range(n):
        c = r.random()
        if size == 0 or c < push_bias:
            ops.append([1, r.randint(lo, hi)])
            size += 1
        elif c < push_bias + (1 - push_bias) / 2:
            ops.append([2, 0])
            size -= 1
        else:
            ops.append([3, 0])
    if not any(o[0] == 3 for o in ops):
        ops.append([3, 0] if size else [1, 0])
        if not size:
            ops.append([3, 0])
    return ops


_r = rnd(6102)
p["tests"].append([_gen_ops(_r, 6000, -10**9, 10**9, 0.5)])
p["tests"].append([_gen_ops(_r, 6000, -10**5, 10**5, 0.7)])
_ops = [[1, v] for v in range(3000)] + [x for _ in range(2000) for x in ([2, 0], [3, 0])]
p["tests"].append([_ops])


def b_maxq(ops):
    q, out = [], []
    for t, x in ops:
        if t == 1:
            q.append(x)
        elif t == 2:
            q.pop(0)
        else:
            out.append(max(q))
    return out


def v_maxq(tests):
    for t in tests:
        ops = t["args"][0]
        assert 1 <= len(ops) <= 8000
        size, queries = 0, 0
        for typ, x in ops:
            assert typ in (1, 2, 3)
            if typ == 1:
                assert -10**9 <= x <= 10**9
                size += 1
            else:
                assert x == 0 and size > 0
                if typ == 2:
                    size -= 1
                else:
                    queries += 1
        assert queries >= 1 and len(t["expected"]) == queries


CHECKS["queue-with-running-maximum"] = (b_maxq, lambda r: [_gen_ops(r, r.randint(2, 30), -4, 4, r.choice([0.4, 0.6, 0.8]))], "exact")
VALIDATE["queue-with-running-maximum"] = v_maxq


# ---------------------------------------------------------------- MEDIUM

p = add(
    id="total-of-window-ranges", title="Total Range of Every Window", diff="Medium", topic=TOPIC,
    fn="totalWindowRange", params=[("nums", "int[]"), ("k", "int")], ret="int", cmp="exact",
    desc="<p>The <em>range</em> of a block of numbers is its largest value minus its smallest value. Slide a window of exactly <code>k</code> elements over <code>nums</code> from left to right and return the <strong>sum of the ranges</strong> of all <code>nums.length - k + 1</code> windows.</p><pre>nums = [3, 1, 4, 1, 5], k = 3\n[3,1,4] range 3    [1,4,1] range 3    [4,1,5] range 4\nresult = 10</pre>",
    constraints=["1 &le; k &le; nums.length &le; 8,000", "-10<sup>5</sup> &le; nums[i] &le; 10<sup>5</sup>", "The answer fits in a signed 32-bit integer"],
    hints=["Computing max and min with a loop over each window costs O(n * k).",
           "You need the window maximum and the window minimum at the same time, for every position.",
           "Maintain two monotonic deques of indices: one with decreasing values (front is the maximum) and one with increasing values (front is the minimum). Drop front indices that left the window, then add <code>nums[max front] - nums[min front]</code> to the total."],
    editorial=["Use one deque for the maximum and one for the minimum, both storing indices. For the max deque, before pushing index <code>i</code> pop every back entry whose value is at most <code>nums[i]</code>, so values decrease from front to back and the front is the maximum. The min deque is the mirror image. Remove the front of a deque when its index is at most <code>i - k</code>.",
               "Once the first window is complete (<code>i &ge; k - 1</code>), add the difference of the two fronts to the total. Each index enters and leaves each deque at most once, so the time is O(n) and the space O(k). The answer is at most 8,000 * 200,000 = 1.6 * 10<sup>9</sup>, which fits in a 32-bit integer."],
    time="O(n)", space="O(k)",
    solution='''def totalWindowRange(nums, k):
    from collections import deque
    mx = deque()
    mn = deque()
    total = 0
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
        if i >= k - 1:
            total += nums[mx[0]] - nums[mn[0]]
    return total
''',
    tests=[[[3, 1, 4, 1, 5], 3], [[7], 1], [[1, 2, 3, 4, 5], 1], [[5, 4, 3, 2, 1], 5], [[2, 2, 2, 2], 2], [[-100000, 100000], 2],
           [[-100000, 100000, -100000, 100000], 2], [[1, 5, 2, 8, 3], 2], [[9, 1, 9, 1, 9, 1], 4], [[0, 0, 7, 0, 0], 3],
           [[-3, -1, -4, -1, -5, -9, -2, -6], 3]],
)
_r = rnd(6103)
p["tests"].append([[_r.randint(-10**5, 10**5) for _ in range(6000)], 40])
p["tests"].append([[(-10**5 if i % 2 else 10**5) for i in range(6000)], 2])
p["tests"].append([[_r.randint(-10**5, 10**5) for _ in range(6000)], 3000])


def b_totrange(nums, k):
    return sum(max(nums[i:i + k]) - min(nums[i:i + k]) for i in range(len(nums) - k + 1))


def g_totrange(r):
    a = gen_arr(r, -9, 9, 1, 12)
    return [a, r.randint(1, len(a))]


def v_totrange(tests):
    for t in tests:
        a, k = t["args"]
        assert 1 <= k <= len(a) <= 8000
        assert all(-10**5 <= x <= 10**5 for x in a)


CHECKS["total-of-window-ranges"] = (b_totrange, g_totrange, "exact")
VALIDATE["total-of-window-ranges"] = v_totrange


p = add(
    id="longest-subarray-within-spread-limit", title="Longest Subarray Within a Spread Limit", diff="Medium", topic=TOPIC, tier="must",
    fn="longestWithinLimit", params=[("nums", "int[]"), ("limit", "int")], ret="int", cmp="exact",
    desc="<p>Return the length of the <strong>longest contiguous subarray</strong> of <code>nums</code> in which the difference between the largest and the smallest element is <strong>at most</strong> <code>limit</code>.</p><pre>nums = [5, 1, 3, 4, 2, 9], limit = 3\n[1,3,4,2] has largest 4, smallest 1, difference 3 -> length 4\n[5,1,3,4,2] would have difference 4, so it is not allowed\nresult = 4</pre>",
    constraints=["1 &le; nums.length &le; 8,000", "-10<sup>9</sup> &le; nums[i] &le; 10<sup>9</sup>", "0 &le; limit &le; 2 * 10<sup>9</sup>"],
    hints=["Any single element is a valid subarray, so the answer is at least 1. Checking all O(n<sup>2</sup>) subarrays with a running max and min is too slow for the largest inputs.",
           "If a subarray is valid then every subarray inside it is valid too. That is what makes a two-pointer window work: when the window becomes invalid, only the left end needs to move right.",
           "You need the max and min of the current window while both ends move. Keep a decreasing deque (max) and an increasing deque (min) of indices, and advance the left end while <code>max - min &gt; limit</code>."],
    editorial=["Grow the window one element at a time at the right end. Keep two monotonic deques of indices, one for the maximum (values decreasing) and one for the minimum (values increasing). While the difference between the two front values exceeds <code>limit</code>, move the left end <code>l</code> forward and drop deque fronts whose index is below <code>l</code>. The remaining window is the longest valid window ending at the current position; record its length.",
               "The window never needs to move left again because a valid subarray stays valid when it shrinks, so the left pointer only increases. Each index is pushed and popped at most once in each deque: O(n) time and O(n) space in the worst case."],
    time="O(n)", space="O(n)",
    solution='''def longestWithinLimit(nums, limit):
    from collections import deque
    mx = deque()
    mn = deque()
    left = 0
    best = 0
    for i, x in enumerate(nums):
        while mx and nums[mx[-1]] <= x:
            mx.pop()
        mx.append(i)
        while mn and nums[mn[-1]] >= x:
            mn.pop()
        mn.append(i)
        while nums[mx[0]] - nums[mn[0]] > limit:
            left += 1
            if mx[0] < left:
                mx.popleft()
            if mn[0] < left:
                mn.popleft()
        best = max(best, i - left + 1)
    return best
''',
    tests=[[[5, 1, 3, 4, 2, 9], 3], [[1], 0], [[4, 4, 4], 0], [[1, 2, 3, 4, 5], 0], [[1, 2, 3, 4, 5], 4], [[1, 2, 3, 4, 5], 2],
           [[10, 1, 2, 4, 7, 2], 5], [[8, 2, 4, 7], 4], [[-1000000000, 1000000000, -1000000000], 1999999999],
           [[-1000000000, 1000000000, -1000000000], 2000000000], [[9, 7, 5, 3, 1, 3, 5, 7, 9], 4], [[3, 3, 100, 3, 3, 3], 0]],
)
_r = rnd(6104)
p["tests"].append([[_r.randint(0, 10**6) for _ in range(6000)], 150000])
_a = [0]
for _ in range(5999):
    _a.append(_a[-1] + _r.randint(-5, 5))
p["tests"].append([_a, 60])
p["tests"].append([[_r.randint(-10**4, 10**4) for _ in range(5000)], 20000])


def b_longlim(nums, limit):
    best = 0
    for i in range(len(nums)):
        for j in range(i, len(nums)):
            seg = nums[i:j + 1]
            if max(seg) - min(seg) <= limit:
                best = max(best, j - i + 1)
    return best


def g_longlim(r):
    a = gen_arr(r, -9, 9, 1, 12)
    return [a, r.randint(0, 14)]


def v_longlim(tests):
    for t in tests:
        a, limit = t["args"]
        assert 1 <= len(a) <= 8000 and 0 <= limit <= 2 * 10**9
        assert all(-10**9 <= x <= 10**9 for x in a)
        assert t["expected"] >= 1


CHECKS["longest-subarray-within-spread-limit"] = (b_longlim, g_longlim, "exact")
VALIDATE["longest-subarray-within-spread-limit"] = v_longlim


p = add(
    id="count-subarrays-within-spread-limit", title="Count Subarrays Within a Spread Limit", diff="Medium", topic=TOPIC,
    fn="countWithinLimit", params=[("nums", "int[]"), ("limit", "int")], ret="int", cmp="exact",
    desc="<p>Count the contiguous subarrays of <code>nums</code> (of any length, at least 1) whose largest element minus smallest element is <strong>at most</strong> <code>limit</code>. Subarrays at different positions are counted separately even if their values are equal.</p><pre>nums = [5, 1, 3, 4, 2, 9], limit = 3\nlength 1: 6 subarrays      length 2: [1,3] [3,4] [4,2] -> 3\nlength 3: [1,3,4] [3,4,2] -> 2      length 4: [1,3,4,2] -> 1\nresult = 12</pre>",
    constraints=["1 &le; nums.length &le; 8,000", "-10<sup>9</sup> &le; nums[i] &le; 10<sup>9</sup>", "0 &le; limit &le; 2 * 10<sup>9</sup>", "The answer is at most n(n+1)/2, which fits in a 32-bit integer"],
    hints=["Testing all O(n<sup>2</sup>) subarrays with max and min recomputed each time is too slow. First think about how to count the valid subarrays that end at a fixed position.",
           "If <code>[l, r]</code> is valid then <code>[l+1, r]</code> is valid too. So for each right end <code>r</code> the valid left ends form a contiguous range <code>l..r</code>, and the smallest such <code>l</code> never decreases as <code>r</code> grows.",
           "Slide a window with two monotonic deques (max and min of the window). After shrinking from the left until the spread is within the limit, add <code>r - l + 1</code> to the answer."],
    editorial=["Fix the right end <code>r</code> and let <code>l(r)</code> be the smallest left end for which <code>nums[l..r]</code> is valid. Subarrays only get more constrained when they grow, so every start from <code>l(r)</code> up to <code>r</code> works, which gives <code>r - l(r) + 1</code> valid subarrays ending at <code>r</code>. Also <code>l(r)</code> is non-decreasing in <code>r</code>.",
               "Maintain the window <code>[l, r]</code> with a decreasing deque (maximum) and an increasing deque (minimum) of indices. When a new element makes the spread exceed the limit, advance <code>l</code> and discard deque fronts below <code>l</code>. Add <code>r - l + 1</code> to the total at each step. Linear time because each index enters and leaves each deque at most once."],
    time="O(n)", space="O(n)",
    solution='''def countWithinLimit(nums, limit):
    from collections import deque
    mx = deque()
    mn = deque()
    left = 0
    total = 0
    for i, x in enumerate(nums):
        while mx and nums[mx[-1]] <= x:
            mx.pop()
        mx.append(i)
        while mn and nums[mn[-1]] >= x:
            mn.pop()
        mn.append(i)
        while nums[mx[0]] - nums[mn[0]] > limit:
            left += 1
            if mx[0] < left:
                mx.popleft()
            if mn[0] < left:
                mn.popleft()
        total += i - left + 1
    return total
''',
    tests=[[[5, 1, 3, 4, 2, 9], 3], [[7], 0], [[4, 4, 4], 0], [[1, 2, 3, 4, 5], 0], [[1, 2, 3, 4, 5], 4], [[1, 2, 3, 4, 5], 1],
           [[2, 8, 2, 8, 2], 5], [[2, 8, 2, 8, 2], 6], [[-1000000000, 1000000000, -1000000000], 1999999999],
           [[-1000000000, 1000000000, -1000000000], 2000000000], [[3, 1, 4, 1, 5, 9, 2, 6], 4]],
)
_r = rnd(6105)
p["tests"].append([[_r.randint(0, 10**6) for _ in range(6000)], 150000])
_a = [0]
for _ in range(5999):
    _a.append(_a[-1] + _r.randint(-5, 5))
p["tests"].append([_a, 60])
p["tests"].append([[_r.randint(-10**4, 10**4) for _ in range(5000)], 20000])


def b_cntlim(nums, limit):
    cnt = 0
    for i in range(len(nums)):
        for j in range(i, len(nums)):
            seg = nums[i:j + 1]
            if max(seg) - min(seg) <= limit:
                cnt += 1
    return cnt


def v_cntlim(tests):
    for t in tests:
        a, limit = t["args"]
        assert 1 <= len(a) <= 8000 and 0 <= limit <= 2 * 10**9
        assert all(-10**9 <= x <= 10**9 for x in a)


CHECKS["count-subarrays-within-spread-limit"] = (b_cntlim, g_longlim, "exact")
VALIDATE["count-subarrays-within-spread-limit"] = v_cntlim


p = add(
    id="max-score-leaping-at-most-k", title="Best Score Leaping Up to K Steps", diff="Medium", topic=TOPIC,
    fn="maxLeapScore", params=[("nums", "int[]"), ("k", "int")], ret="int", cmp="exact",
    desc="<p>You stand on index <code>0</code> of <code>nums</code> and want to reach index <code>nums.length - 1</code>. From index <code>i</code> you may leap to any index <code>j</code> with <code>i &lt; j &le; i + k</code> (and <code>j</code> inside the array). Your <em>score</em> is the sum of <code>nums[i]</code> over every index you stand on, including the first and the last one.</p><p>Return the maximum score over all possible routes.</p><pre>nums = [3, -5, -2, 6, -9, 4], k = 2\nroute 0 -> 1 -> 3 -> 5: 3 + (-5) + 6 + 4 = 8\nroute 0 -> 2 -> 3 -> 5: 3 + (-2) + 6 + 4 = 11\nresult = 11</pre>",
    constraints=["1 &le; nums.length &le; 8,000", "1 &le; k &le; nums.length", "-10<sup>5</sup> &le; nums[i] &le; 10<sup>5</sup>"],
    hints=["Let <code>best[i]</code> be the highest score of a route that ends on index <code>i</code>. What does <code>best[i]</code> depend on?",
           "<code>best[i] = nums[i] + max(best[j])</code> over the previous indices <code>j</code> with <code>i - k &le; j &lt; i</code>. Evaluating this maximum by scanning gives O(n * k).",
           "The maximum of <code>best</code> over the last k indices is a sliding window maximum. Keep a deque of indices whose <code>best</code> values are decreasing, and pop the front when it is more than k behind."],
    editorial=["Define <code>best[0] = nums[0]</code> and <code>best[i] = nums[i] + max(best[j] for j in [i-k, i-1])</code>. The answer is <code>best[n-1]</code>. The recurrence is a plain O(n * k) dynamic program, and the only slow part is the window maximum over the previous k states.",
               "That window moves one step right per index, so a monotonic deque of indices (with decreasing <code>best</code> values) gives the maximum at its front in amortized O(1). Remove the front when its index is less than <code>i - k</code>, compute <code>best[i]</code>, then pop smaller values from the back and push <code>i</code>. Total O(n) time and O(n) space (O(k) if only the deque is kept). Negative values are fine, since you must take the best predecessor even when it is negative."],
    time="O(n)", space="O(n)",
    solution='''def maxLeapScore(nums, k):
    from collections import deque
    n = len(nums)
    best = [0] * n
    best[0] = nums[0]
    dq = deque([0])
    for i in range(1, n):
        while dq[0] < i - k:
            dq.popleft()
        best[i] = nums[i] + best[dq[0]]
        while dq and best[dq[-1]] <= best[i]:
            dq.pop()
        dq.append(i)
    return best[-1]
''',
    tests=[[[3, -5, -2, 6, -9, 4], 2], [[5], 1], [[-7], 1], [[1, -1, -2, 4, -7, 3], 2], [[10, -5, -2, 4, 0, 3], 3], [[1, -5, -20, 4, -1, 3, -6, -3], 2],
           [[2, -9, -9, -9, 2], 1], [[2, -9, -9, -9, 2], 4], [[-1, -2, -3, -4], 3], [[100000, -100000, 100000], 2],
           [[0, 0, 0, 0], 1], [[4, -4, 4, -4, 4, -4, 4], 2]],
)
_r = rnd(6106)
p["tests"].append([[_r.randint(-10**5, 10**5) for _ in range(6000)], 100])
p["tests"].append([[_r.randint(-10**4, 10**4) for _ in range(6000)], 3])
p["tests"].append([[-_r.randint(1, 10**4) for _ in range(6000)], 2500])


def b_leap(nums, k):
    n = len(nums)
    NEG = float("-inf")
    best = [NEG] * n
    best[0] = nums[0]
    for i in range(1, n):
        best[i] = nums[i] + max(best[j] for j in range(max(0, i - k), i))
    return best[-1]


def g_leap(r):
    a = gen_arr(r, -9, 9, 1, 12)
    return [a, r.randint(1, len(a))]


def v_leap(tests):
    for t in tests:
        a, k = t["args"]
        assert 1 <= len(a) <= 8000 and 1 <= k <= len(a)
        assert all(-10**5 <= x <= 10**5 for x in a)


CHECKS["max-score-leaping-at-most-k"] = (b_leap, g_leap, "exact")
VALIDATE["max-score-leaping-at-most-k"] = v_leap


p = add(
    id="shortest-subarray-with-spread-at-least-d", title="Shortest Subarray With Spread At Least D", diff="Medium", topic=TOPIC,
    fn="shortestWithSpread", params=[("nums", "int[]"), ("d", "int")], ret="int", cmp="exact",
    desc="<p>Find the length of the <strong>shortest contiguous subarray</strong> of <code>nums</code> whose largest element minus smallest element is <strong>at least</strong> <code>d</code>. Return <code>-1</code> if no subarray qualifies.</p><pre>nums = [4, 7, 5, 6, 9, 5], d = 5\n[4,7,5,6,9] has largest 9, smallest 4, difference 5 -> length 5\nno shorter subarray reaches a difference of 5\nresult = 5</pre>",
    constraints=["1 &le; nums.length &le; 8,000", "-10<sup>9</sup> &le; nums[i] &le; 10<sup>9</sup>", "0 &le; d &le; 2 * 10<sup>9</sup>"],
    hints=["A subarray of length 1 has difference 0, so for d = 0 the answer is 1. For larger d you need at least two elements.",
           "If a subarray reaches spread d, every larger subarray containing it does too. For each right end, you want the largest left end that still satisfies the condition.",
           "Sliding window with a decreasing and an increasing deque: for each right end, while <code>max - min &ge; d</code>, record the length and move the left end forward."],
    editorial=["The property \"spread at least d\" is monotone in the opposite direction from the usual window problems: growing a subarray can only keep or increase its spread. So for each right end <code>r</code> we want to shrink from the left as long as the window still qualifies. Each time it does, record <code>r - l + 1</code> and then move <code>l</code> forward by one.",
               "The max and min of the window come from two monotonic deques of indices (decreasing and increasing). When <code>l</code> advances, remove deque fronts whose index is below <code>l</code>. The left pointer never moves backwards: if the window <code>[l, r]</code> was minimal for <code>r</code>, then for <code>r + 1</code> no start left of <code>l</code> can give a shorter qualifying window. O(n) time, O(n) space."],
    time="O(n)", space="O(n)",
    solution='''def shortestWithSpread(nums, d):
    from collections import deque
    mx = deque()
    mn = deque()
    left = 0
    best = -1
    for i, x in enumerate(nums):
        while mx and nums[mx[-1]] <= x:
            mx.pop()
        mx.append(i)
        while mn and nums[mn[-1]] >= x:
            mn.pop()
        mn.append(i)
        while left <= i and nums[mx[0]] - nums[mn[0]] >= d:
            if best == -1 or i - left + 1 < best:
                best = i - left + 1
            left += 1
            while mx and mx[0] < left:
                mx.popleft()
            while mn and mn[0] < left:
                mn.popleft()
    return best
''',
    tests=[[[4, 7, 5, 6, 9, 5], 5], [[4, 7, 5, 6, 9, 5], 4], [[3], 0], [[3], 1], [[1, 2, 3], 0], [[5, 5, 5, 5], 1], [[1, 2, 3, 4, 5], 4],
           [[1, 2, 3, 4, 5], 5], [[9, 1, 9, 1], 8], [[-1000000000, 1000000000], 2000000000], [[-1000000000, 1000000000], 1999999999],
           [[2, 3, 2, 3, 2, 12, 3, 2], 10], [[10, 4, 8, 2, 9, 1], 6]],
)
_r = rnd(6107)
p["tests"].append([[_r.randint(0, 10**6) for _ in range(6000)], 999000])
_a = [0]
for _ in range(5999):
    _a.append(_a[-1] + _r.randint(-3, 3))
p["tests"].append([_a, 70])
p["tests"].append([[_r.randint(-10**4, 10**4) for _ in range(5000)], 30000])


def b_shortspread(nums, d):
    n = len(nums)
    for length in range(1, n + 1):
        for i in range(n - length + 1):
            seg = nums[i:i + length]
            if max(seg) - min(seg) >= d:
                return length
    return -1


def g_shortspread(r):
    a = gen_arr(r, -9, 9, 1, 12)
    return [a, r.randint(0, 20)]


def v_shortspread(tests):
    for t in tests:
        a, d = t["args"]
        assert 1 <= len(a) <= 8000 and 0 <= d <= 2 * 10**9
        assert all(-10**9 <= x <= 10**9 for x in a)
    assert any(t["expected"] == -1 for t in tests) and any(t["expected"] > 1 for t in tests)


CHECKS["shortest-subarray-with-spread-at-least-d"] = (b_shortspread, g_shortspread, "exact")
VALIDATE["shortest-subarray-with-spread-at-least-d"] = v_shortspread


p = add(
    id="max-sum-subarray-length-between-l-and-r", title="Best Subarray With Length Between L and R", diff="Medium", topic=TOPIC, tier="extra",
    fn="maxSumLengthRange", params=[("nums", "int[]"), ("lo", "int"), ("hi", "int")], ret="int", cmp="exact",
    desc="<p>Among all contiguous subarrays of <code>nums</code> whose length is between <code>lo</code> and <code>hi</code> (both inclusive), return the largest possible sum. At least one such subarray exists.</p><pre>nums = [2, -1, 3, -4, 5], lo = 2, hi = 3\nlength 2 sums: 1, 2, -1, 1      length 3 sums: 4, -2, 4\nresult = 4</pre>",
    constraints=["1 &le; lo &le; hi &le; nums.length &le; 8,000", "-10<sup>4</sup> &le; nums[i] &le; 10<sup>4</sup>"],
    hints=["Trying every start with every allowed length costs O(n * (hi - lo + 1)). Use prefix sums so that any subarray sum is a difference of two numbers.",
           "With prefix sums <code>P</code>, the subarray ending at <code>j</code> with length <code>len</code> has sum <code>P[j] - P[j - len]</code>. For a fixed <code>j</code>, you want the smallest <code>P[i]</code> with <code>j - hi &le; i &le; j - lo</code>.",
           "That is a window minimum over a range of prefix indices that slides right by one for every j. Maintain it with an increasing deque of indices."],
    editorial=["Let <code>P[0] = 0</code> and <code>P[i] = nums[0] + ... + nums[i-1]</code>. A subarray occupying positions <code>i..j-1</code> has sum <code>P[j] - P[i]</code> and length <code>j - i</code>. For each end <code>j</code> from <code>lo</code> to <code>n</code> the allowed starts are <code>i</code> in <code>[j - hi, j - lo]</code>, so the best sum ending there is <code>P[j]</code> minus the minimum of <code>P</code> over that index range.",
               "Both ends of the index range move right by one when <code>j</code> increases by one. Keep a deque of indices with increasing <code>P</code> values: push index <code>j - lo</code> (popping larger values from the back), drop front indices below <code>j - hi</code>, and read the minimum at the front. O(n) time and O(n) space. For <code>hi = n</code> this degenerates to the classic \"best subarray of length at least lo\"."],
    time="O(n)", space="O(n)",
    solution='''def maxSumLengthRange(nums, lo, hi):
    from collections import deque
    n = len(nums)
    P = [0] * (n + 1)
    for i, x in enumerate(nums):
        P[i + 1] = P[i] + x
    dq = deque()
    best = None
    for j in range(lo, n + 1):
        i = j - lo
        while dq and P[dq[-1]] >= P[i]:
            dq.pop()
        dq.append(i)
        while dq[0] < j - hi:
            dq.popleft()
        cand = P[j] - P[dq[0]]
        if best is None or cand > best:
            best = cand
    return best
''',
    tests=[[[2, -1, 3, -4, 5], 2, 3], [[5], 1, 1], [[-5], 1, 1], [[-3, -1, -2], 1, 3], [[-3, -1, -2], 2, 3], [[1, 2, 3, 4], 4, 4], [[1, 2, 3, 4], 1, 4],
           [[4, -10, 4, -10, 4], 1, 2], [[4, -10, 4, -10, 4], 3, 5], [[10000, -10000, 10000, -10000], 2, 3], [[3, 3, -9, 3, 3, 3], 3, 4],
           [[-1, -1, 7, -1, -1, -1], 2, 2]],
)
_r = rnd(6108)
p["tests"].append([[_r.randint(-10**4, 10**4) for _ in range(6000)], 100, 400])
p["tests"].append([[_r.randint(-10**4, 10**4) for _ in range(6000)], 2000, 6000])
p["tests"].append([[_r.randint(-10**4, 10**4) for _ in range(6000)], 5, 5])


def b_lenrange(nums, lo, hi):
    n = len(nums)
    best = None
    for i in range(n):
        for j in range(i + lo, min(n, i + hi) + 1):
            s = sum(nums[i:j])
            if best is None or s > best:
                best = s
    return best


def g_lenrange(r):
    a = gen_arr(r, -9, 9, 1, 12)
    lo = r.randint(1, len(a))
    return [a, lo, r.randint(lo, len(a))]


def v_lenrange(tests):
    for t in tests:
        a, lo, hi = t["args"]
        assert 1 <= lo <= hi <= len(a) <= 8000
        assert all(-10**4 <= x <= 10**4 for x in a)


CHECKS["max-sum-subarray-length-between-l-and-r"] = (b_lenrange, g_lenrange, "exact")
VALIDATE["max-sum-subarray-length-between-l-and-r"] = v_lenrange


# ---------------------------------------------------------------- HARD

p = add(
    id="max-value-of-point-pair-equation", title="Best Point Pair Within a Horizontal Gap", diff="Hard", topic=TOPIC,
    fn="maxPairEquation", params=[("points", "int[][]"), ("k", "int")], ret="int", cmp="exact",
    desc="<p>You are given <code>points</code>, a list of <code>[x, y]</code> pairs sorted by <code>x</code> in strictly increasing order. For two points <code>i &lt; j</code> with <code>x<sub>j</sub> - x<sub>i</sub> &le; k</code>, define its value as</p><pre>y_i + y_j + |x_i - x_j|</pre><p>Return the maximum value over all such pairs. At least one pair satisfies the gap condition.</p><pre>points = [[1,5],[3,1],[4,8],[8,2]], k = 3\n(1,3): 5 + 1 + 2 = 8\n(3,4): 1 + 8 + 1 = 10\n(1,4): 5 + 8 + 3 = 16   (gap 3)\n(4,8) has gap 4 &gt; 3 and is not allowed\nresult = 16</pre>",
    constraints=["2 &le; points.length &le; 4,000", "points[i] = [x, y] with -10<sup>8</sup> &le; x, y &le; 10<sup>8</sup>", "x values are strictly increasing", "1 &le; k &le; 2 * 10<sup>8</sup>", "At least one pair of points has x<sub>j</sub> - x<sub>i</sub> &le; k"],
    hints=["Checking all pairs is O(n<sup>2</sup>), which is already acceptable for 4,000 points, but try to find a linear approach. Start by removing the absolute value.",
           "Since the points are sorted and <code>i &lt; j</code>, <code>|x_i - x_j| = x_j - x_i</code>. The value becomes <code>(y_i - x_i) + (y_j + x_j)</code>.",
           "For each j you want the largest <code>y_i - x_i</code> among earlier points with <code>x_j - x_i &le; k</code>. Keep a deque of earlier points whose <code>y - x</code> values are decreasing; drop the front while it is too far left."],
    editorial=["Because the points are sorted by x and <code>i &lt; j</code>, the absolute value disappears: the value of a pair is <code>(y_i - x_i) + (y_j + x_j)</code>. The two parts separate, so for every j we only need the maximum of <code>y_i - x_i</code> over earlier points that are within horizontal distance k.",
               "The set of eligible earlier points is a window whose left edge moves right as x grows (x is increasing). Maintain a deque of earlier points ordered so that <code>y - x</code> decreases from front to back. For a new point j: pop the front while <code>x_j - x_front &gt; k</code>; if the deque is not empty, update the answer with <code>front(y - x) + y_j + x_j</code>; then pop from the back every point whose <code>y - x</code> is not larger than the new one and push j. Every point enters and leaves once: O(n) time and O(n) space."],
    time="O(n)", space="O(n)",
    solution='''def maxPairEquation(points, k):
    from collections import deque
    dq = deque()
    best = None
    for x, y in points:
        while dq and x - dq[0][1] > k:
            dq.popleft()
        if dq:
            cand = dq[0][0] + y + x
            if best is None or cand > best:
                best = cand
        v = y - x
        while dq and dq[-1][0] <= v:
            dq.pop()
        dq.append((v, x))
    return best
''',
    tests=[[[[1, 5], [3, 1], [4, 8], [8, 2]], 3], [[[0, 0], [3, 0], [9, 2]], 3], [[[1, 3], [2, 0], [5, 10], [6, -10]], 1],
           [[[-5, -5], [-4, -4]], 1], [[[-100000000, 100000000], [100000000, 100000000]], 200000000], [[[0, 5], [1, 1], [2, 9], [3, 0]], 2],
           [[[0, 10], [5, -10], [6, -10], [7, 10]], 7], [[[0, 10], [5, -10], [6, -10], [7, 10]], 2], [[[1, 1], [2, 2], [3, 3], [4, 4], [5, 5]], 1],
           [[[1, 1], [2, 2], [3, 3], [4, 4], [5, 5]], 4], [[[-3, 7], [-2, -7], [0, 7]], 5]],
)
_r = rnd(6109)


def _mk_points(r, n, step, ylo, yhi, x0=-10**8):
    xs, x = [], x0
    for _ in range(n):
        xs.append(x)
        x += r.randint(1, step)
    return [[x, r.randint(ylo, yhi)] for x in xs]


p["tests"].append([_mk_points(_r, 3500, 50000, -10**8, 10**8), 300000])
p["tests"].append([_mk_points(_r, 3500, 20, -1000, 1000, 0), 2000])
p["tests"].append([_mk_points(_r, 3500, 20000, -10**8, 10**8), 200000000])


def b_equation(points, k):
    best = None
    for i in range(len(points)):
        for j in range(i + 1, len(points)):
            if points[j][0] - points[i][0] <= k:
                v = points[i][1] + points[j][1] + abs(points[i][0] - points[j][0])
                if best is None or v > best:
                    best = v
    return best


def g_equation(r):
    n = r.randint(2, 10)
    pts = _mk_points(r, n, 4, -9, 9, r.randint(-5, 5))
    return [pts, r.randint(max(1, pts[1][0] - pts[0][0]), 10)]


def v_equation(tests):
    for t in tests:
        pts, k = t["args"]
        assert 2 <= len(pts) <= 4000 and 1 <= k <= 2 * 10**8
        assert all(-10**8 <= x <= 10**8 and -10**8 <= y <= 10**8 for x, y in pts)
        assert all(pts[i][0] < pts[i + 1][0] for i in range(len(pts) - 1))
        assert any(pts[i + 1][0] - pts[i][0] <= k for i in range(len(pts) - 1))
        assert t["expected"] is not None


CHECKS["max-value-of-point-pair-equation"] = (b_equation, g_equation, "exact")
VALIDATE["max-value-of-point-pair-equation"] = v_equation


p = add(
    id="max-robots-within-budget", title="Most Robots Running Within a Budget", diff="Hard", topic=TOPIC, tier="common",
    fn="maxRobotsWithinBudget", params=[("charge", "int[]"), ("running", "int[]"), ("budget", "int")], ret="int", cmp="exact",
    desc="<p>A factory has <code>n</code> robots in a row. Robot <code>i</code> needs <code>charge[i]</code> units of charge to start and then costs <code>running[i]</code> units per hour to run. You choose a group of <strong>consecutive</strong> robots and run them together. Starting them all costs only the largest charge in the group, and running them costs the sum of their running costs <em>times the group size</em>:</p><pre>cost(group) = max(charge in group) + size * sum(running in group)</pre><p>Return the largest group size whose cost is <strong>at most</strong> <code>budget</code>, or <code>0</code> if even a single robot is too expensive.</p><pre>charge = [4, 2, 7, 3], running = [1, 2, 1, 2], budget = 19\n[4,2,7]: 7 + 3 * (1+2+1) = 19  -> allowed\nno group of 4 fits (7 + 4 * 6 = 31)\nresult = 3</pre>",
    constraints=["1 &le; n = charge.length = running.length &le; 4,000", "1 &le; charge[i] &le; 10<sup>5</sup>", "0 &le; running[i] &le; 10<sup>5</sup>", "0 &le; budget &le; 2 * 10<sup>9</sup>"],
    hints=["Compute the cost of any single group directly, then ask how the cost changes when a group grows. Checking all O(n<sup>2</sup>) groups is the baseline.",
           "Adding a robot to a group never lowers its cost (the maximum, the sum and the size can only go up). So if a group is affordable, every smaller group inside it is too, and a sliding window works.",
           "While extending the window to the right, maintain the sum of running costs and a decreasing deque of charges for the maximum. If the cost exceeds the budget, move the left end forward (removing the front of the deque when it leaves) until the window is affordable again."],
    editorial=["The cost function is monotone: for groups <code>A &sub; B</code>, <code>cost(A) &le; cost(B)</code>, since all three ingredients (maximum charge, number of robots, total running cost) are non-decreasing when robots are added. Therefore for each right end <code>r</code> the set of affordable left ends is a suffix <code>l..r</code>, and the smallest affordable <code>l</code> never moves left as <code>r</code> grows. That is exactly the two-pointer window pattern.",
               "Maintain the running sum of the window and a monotonic deque of charge indices (decreasing values) to get the window maximum in O(1). After adding robot <code>r</code>, while <code>charge[deque front] + (r - l + 1) * sum &gt; budget</code>, remove robot <code>l</code>: subtract its running cost and pop the deque front if it is <code>l</code>. The window can become empty when a single robot is too expensive. Track the largest window size seen. O(n) time, O(n) space."],
    time="O(n)", space="O(n)",
    solution='''def maxRobotsWithinBudget(charge, running, budget):
    from collections import deque
    dq = deque()
    left = 0
    total = 0
    best = 0
    for r in range(len(charge)):
        while dq and charge[dq[-1]] <= charge[r]:
            dq.pop()
        dq.append(r)
        total += running[r]
        while left <= r and charge[dq[0]] + (r - left + 1) * total > budget:
            total -= running[left]
            if dq[0] == left:
                dq.popleft()
            left += 1
            if left > r:
                dq.clear()
        best = max(best, r - left + 1)
    return best
''',
    tests=[[[4, 2, 7, 3], [1, 2, 1, 2], 19], [[3, 6, 1, 3, 4], [2, 1, 3, 4, 5], 25], [[11, 12, 19], [10, 8, 7], 19], [[5], [0], 5], [[5], [0], 4],
           [[1, 1, 1], [0, 0, 0], 1], [[1, 1, 1], [0, 0, 0], 0], [[10, 1, 1, 1, 10], [1, 1, 1, 1, 1], 14], [[100000, 100000], [100000, 100000], 2000000000],
           [[2, 9, 2, 2, 9, 2], [3, 0, 0, 3, 0, 0], 20], [[8, 3, 5, 7, 2], [2, 2, 2, 2, 2], 23]],
)
_r = rnd(6110)
p["tests"].append([[_r.randint(1, 10**5) for _ in range(3500)], [_r.randint(0, 100) for _ in range(3500)], 40000000])
p["tests"].append([[_r.randint(1, 10**5) for _ in range(3500)], [_r.randint(0, 10**5) for _ in range(3500)], 1500000000])
p["tests"].append([[_r.randint(1, 1000) for _ in range(3500)], [_r.randint(0, 3) for _ in range(3500)], 2000000000])


def b_robots(charge, running, budget):
    best = 0
    n = len(charge)
    for i in range(n):
        for j in range(i, n):
            size = j - i + 1
            if max(charge[i:j + 1]) + size * sum(running[i:j + 1]) <= budget:
                best = max(best, size)
    return best


def g_robots(r):
    n = r.randint(1, 10)
    return [[r.randint(1, 9) for _ in range(n)], [r.randint(0, 5) for _ in range(n)], r.randint(0, 60)]


def v_robots(tests):
    for t in tests:
        c, ru, b = t["args"]
        assert len(c) == len(ru) and 1 <= len(c) <= 4000 and 0 <= b <= 2 * 10**9
        assert all(1 <= x <= 10**5 for x in c) and all(0 <= x <= 10**5 for x in ru)
    assert any(t["expected"] == 0 for t in tests) and any(t["expected"] >= 2 for t in tests)


CHECKS["max-robots-within-budget"] = (b_robots, g_robots, "exact")
VALIDATE["max-robots-within-budget"] = v_robots


p = add(
    id="min-block-maximum-total-with-sum-cap", title="Cheapest Split Into Capped Blocks", diff="Hard", topic=TOPIC, tier="extra",
    fn="minBlockMaxTotal", params=[("nums", "int[]"), ("cap", "int")], ret="int", cmp="exact",
    desc="<p>Cut <code>nums</code> into consecutive non-empty blocks (every element belongs to exactly one block, order preserved). The <strong>sum of each block must be at most</strong> <code>cap</code>. The cost of a split is the total of the <strong>maximum element of every block</strong>. Return the minimum possible cost.</p><p>Every element is at most <code>cap</code>, so a valid split always exists.</p><pre>nums = [3, 1, 4, 1, 5], cap = 8\n[3,1,4] [1,5]  -> blocks sums 8 and 6, cost 4 + 5 = 9\n[3,1] [4,1] [5] -> cost 3 + 4 + 5 = 12\n[3,1,4,1] [5]  -> sum 9 &gt; 8, not allowed\n[3] [1,4,1] [5] -> cost 3 + 4 + 5 = 12\nresult = 9</pre>",
    constraints=["1 &le; nums.length &le; 8,000", "1 &le; nums[i] &le; cap &le; 10<sup>5</sup>", "The answer fits in a 32-bit integer (it is at most the sum of nums)"],
    hints=["Let <code>dp[i]</code> be the best cost for the first i elements. The last block is <code>nums[j+1..i]</code> for some j, so <code>dp[i] = min(dp[j] + max(nums[j+1..i]))</code> over the j whose block sum is within cap. That is O(n<sup>2</sup>).",
           "Because all numbers are positive, <code>dp</code> is non-decreasing, and the smallest allowed j for each i never decreases. As i grows, the maximum of the last block takes only a few distinct values: the entries of a decreasing monotonic deque.",
           "For a deque element k with predecessor p, all starts j in [p, k-1] have block maximum <code>nums[k]</code>, and the best of them is j = p (dp is non-decreasing). Candidate: <code>dp[p] + nums[k]</code>. Keep the candidates in a min-heap with lazy deletion, plus handle the front element separately using the left boundary of the cap."],
    editorial=["The dynamic program is <code>dp[i] = min over j of dp[j] + max(nums[j+1..i])</code> for all j with <code>sum(nums[j+1..i]) &le; cap</code>. The valid j form a window <code>[L, i-1]</code> whose left end <code>L</code> only moves right. Positive numbers make <code>dp</code> non-decreasing: dropping the last element of an optimal split of the first i+1 elements gives a valid split of the first i elements that costs no more.",
               "Keep a deque of indices of strictly decreasing values (the suffix maxima of the current prefix). For deque element <code>k</code> with predecessor <code>p</code>, every start j in [p, k-1] sees block maximum <code>nums[k]</code>, and by monotonicity the cheapest is j = p, giving candidate <code>dp[p] + nums[k]</code>. For the front element the lower bound is <code>L</code> instead of a predecessor, giving <code>dp[L] + nums[front]</code>. Candidates of non-front elements never change while the element is in the deque, so they sit in a min-heap with lazy deletion (skip entries whose element has left the deque or became the front).",
               "Each index is pushed and popped at most once in the deque and the heap, so the total time is O(n log n) and the space O(n). A variant with a balanced multiset gives the same bounds; the simple O(n * cap) approach of scanning the window is the brute-force baseline."],
    time="O(n log n)", space="O(n)",
    solution='''def minBlockMaxTotal(nums, cap):
    from collections import deque
    import heapq
    n = len(nums)
    a = [0] + nums
    pref = [0] * (n + 1)
    for i in range(1, n + 1):
        pref[i] = pref[i - 1] + a[i]
    dp = [0] * (n + 1)
    alive = [False] * (n + 1)
    dq = deque()
    heap = []
    L = 0
    for i in range(1, n + 1):
        while pref[i] - pref[L] > cap:
            L += 1
        while dq and a[dq[-1]] <= a[i]:
            alive[dq.pop()] = False
        if dq:
            heapq.heappush(heap, (dp[dq[-1]] + a[i], i))
        dq.append(i)
        alive[i] = True
        while dq[0] <= L:
            alive[dq.popleft()] = False
        front = dq[0]
        best = dp[L] + a[front]
        while heap and (not alive[heap[0][1]] or heap[0][1] == front):
            heapq.heappop(heap)
        if heap and heap[0][0] < best:
            best = heap[0][0]
        dp[i] = best
    return dp[n]
''',
    tests=[[[3, 1, 4, 1, 5], 8], [[7], 7], [[1, 1, 1, 1], 4], [[1, 1, 1, 1], 1], [[5, 5, 5], 10], [[2, 9, 2, 9, 2], 11], [[1, 2, 3, 4, 5, 6], 7],
           [[6, 5, 4, 3, 2, 1], 9], [[10000, 10000, 10000], 10000], [[10000, 1, 10000], 10001], [[4, 1, 1, 1, 4, 1, 1, 1, 4], 6]],
)
_r = rnd(6111)
p["tests"].append([[_r.randint(1, 10000) for _ in range(6000)], 10000])
p["tests"].append([[_r.randint(1, 100) for _ in range(6000)], 5000])
p["tests"].append([[_r.randint(1, 50) for _ in range(6000)], 9000])


def b_blocks(nums, cap):
    n = len(nums)
    INF = float("inf")
    dp = [INF] * (n + 1)
    dp[0] = 0
    for i in range(1, n + 1):
        s, m = 0, 0
        for j in range(i - 1, -1, -1):
            s += nums[j]
            if s > cap:
                break
            m = max(m, nums[j])
            dp[i] = min(dp[i], dp[j] + m)
    return dp[n]


def g_blocks(r):
    n = r.randint(1, 12)
    cap = r.randint(1, 15)
    return [[r.randint(1, cap) for _ in range(n)], cap]


def v_blocks(tests):
    for t in tests:
        a, cap = t["args"]
        assert 1 <= len(a) <= 8000 and 1 <= cap <= 10**5
        assert all(1 <= x <= cap for x in a)


CHECKS["min-block-maximum-total-with-sum-cap"] = (b_blocks, g_blocks, "exact")
VALIDATE["min-block-maximum-total-with-sum-cap"] = v_blocks
