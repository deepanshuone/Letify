"""Problems: arrays, single linear scans (second max, leaders, record highs, prefix max/min, longest runs). See data/lib.py for the registry."""
from itertools import combinations

from lib import add, rnd, CHECKS, VALIDATE, gen_arr  # noqa: F401

INT_MIN, INT_MAX = -(2 ** 31), 2 ** 31 - 1
TOPIC = "Arrays & Hashing"


# ---------------------------------------------------------------- EASY

p = add(
    id="second-largest-distinct", title="Second Largest Distinct Value", diff="Easy", topic=TOPIC,
    fn="secondLargest", params=[("nums", "int[]")], ret="int", cmp="exact",
    desc="<p>Given an array <code>nums</code> of non-negative integers, return the second largest <em>distinct</em> value in it. Equal values count as one: in <code>[9, 9, 5]</code> the largest value is 9 and the second largest is 5.</p><p>If the array has fewer than two distinct values, return <code>-1</code>. Do it in a single pass without sorting.</p><p><strong>Example:</strong> <code>nums = [5, 3, 9, 9, 1]</code> returns <code>5</code>.</p>",
    constraints=["1 &le; nums.length &le; 10,000", "0 &le; nums[i] &le; 2<sup>31</sup> - 1"],
    hints=["Sorting works, but a single scan is enough. What do you need to remember about the elements seen so far?",
           "Keep two variables: the largest value so far and the second largest value that is strictly smaller than it.",
           "For each x: if x is bigger than the largest, the old largest becomes the second largest; else if x is strictly between the second and the largest, it replaces the second. Equal values change nothing."],
    editorial=["Track <code>first</code> (the maximum seen) and <code>second</code> (the largest value seen that is strictly below <code>first</code>), both starting at <code>-1</code>. Because every input value is non-negative, <code>-1</code> works as an 'empty' marker and is also exactly the answer to return when no second value exists.",
               "For each <code>x</code>: if <code>x &gt; first</code>, shift <code>first</code> into <code>second</code> and store <code>x</code> as the new <code>first</code>; otherwise, if <code>first &gt; x &gt; second</code>, store <code>x</code> as <code>second</code>. A value equal to <code>first</code> is skipped, which is what keeps duplicates from being counted twice.",
               "This is one pass with two variables. Sorting would cost O(n log n), and a set plus sort uses O(n) memory for no gain."],
    time="O(n)", space="O(1)",
    solution='''def secondLargest(nums):
    first = second = -1
    for x in nums:
        if x > first:
            second = first
            first = x
        elif first > x > second:
            second = x
    return second
''',
    tests=[[[5, 3, 9, 9, 1]], [[7, 7, 7]], [[4]], [[1, 2]], [[0, 0, 1]], [[INT_MAX, INT_MAX - 1, INT_MAX]], [[3, 3, 2, 2, 1, 1]],
           [[10, 9, 8, 7]], [[0]], [[2, 9, 9, 9, 2]], [[1, 5, 5, 4, 5, 3]], [[0, 0, 0, 0]]],
)
_r = rnd(9101)
p["tests"].append([[_r.randint(0, INT_MAX) for _ in range(3000)]])
p["tests"].append([[123456] * 5000])
p["tests"].append([list(range(5000))])


def b_second(nums):
    s = sorted(set(nums))
    return s[-2] if len(s) >= 2 else -1


def v_second(tests):
    for t in tests:
        nums = t["args"][0]
        assert 1 <= len(nums) <= 10000 and all(0 <= x <= INT_MAX for x in nums)


CHECKS["second-largest-distinct"] = (b_second, lambda r: [gen_arr(r, 0, 5, 1, 9)], "exact")
VALIDATE["second-largest-distinct"] = v_second

p = add(
    id="array-leaders", title="Leaders in an Array", diff="Easy", topic=TOPIC,
    fn="arrayLeaders", params=[("nums", "int[]")], ret="int[]", cmp="exact",
    desc="<p>An element of <code>nums</code> is a <em>leader</em> if it is <strong>strictly greater</strong> than every element to its right. The last element has nothing to its right, so it is always a leader.</p><p>Return all leaders in the same left-to-right order in which they appear in <code>nums</code>.</p><p><strong>Example:</strong> <code>nums = [16, 17, 4, 3, 5, 2]</code> returns <code>[17, 5, 2]</code>. The value 16 is not a leader because 17 is to its right; 4 and 3 lose to 5.</p>",
    constraints=["1 &le; nums.length &le; 10,000", "-2<sup>31</sup> &le; nums[i] &le; 2<sup>31</sup> - 1"],
    hints=["Comparing every element with everything on its right works but takes O(n<sup>2</sup>).",
           "Whether an element is a leader depends only on the maximum of the part to its right. Which direction should you scan to know that maximum cheaply?",
           "Scan from right to left, keeping the largest value seen so far. An element that beats it is a leader (the last element always does). Reverse the collected list at the end."],
    editorial=["Looking from the left, you would have to know the future. Looking from the right, you already know it: keep <code>best</code>, the maximum of everything to the right of the current index. If <code>nums[i] &gt; best</code>, then <code>nums[i]</code> is a leader and becomes the new <code>best</code>. Start with <code>best = -infinity</code> so the last element always qualifies.",
               "Leaders are found right to left, so collect them and reverse the list before returning. Note the strict comparison: an element equal to something on its right is not a leader. The leaders always form a strictly decreasing sequence.",
               "Time is O(n) for one pass; the output list is the only extra memory."],
    time="O(n)", space="O(1)",
    solution='''def arrayLeaders(nums):
    res = []
    best = None
    for i in range(len(nums) - 1, -1, -1):
        if best is None or nums[i] > best:
            res.append(nums[i])
            best = nums[i]
    res.reverse()
    return res
''',
    tests=[[[16, 17, 4, 3, 5, 2]], [[1, 2, 3, 4, 5]], [[5, 4, 3, 2, 1]], [[7]], [[5, 5, 5]], [[3, 3, 1, 3, 2, 2]], [[-1, -2, -3]],
           [[INT_MIN, INT_MIN]], [[INT_MAX, INT_MIN, INT_MAX]], [[0, 9, 0, 9, 0]], [[1, 100, 2, 99, 3, 98]]],
)
_r = rnd(9102)
p["tests"].append([[_r.randint(-1000, 1000) for _ in range(5000)]])
p["tests"].append([sorted((_r.randint(-10000, 10000) for _ in range(5000)), reverse=True)])
p["tests"].append([[_r.randint(INT_MIN, INT_MAX) for _ in range(2500)]])


def b_leaders(nums):
    return [x for i, x in enumerate(nums) if all(x > y for y in nums[i + 1:])]


def v_leaders(tests):
    for t in tests:
        nums = t["args"][0]
        assert 1 <= len(nums) <= 10000
        assert t["expected"] and t["expected"][-1] == nums[-1]


CHECKS["array-leaders"] = (b_leaders, lambda r: [gen_arr(r, -4, 4, 1, 9)], "exact")
VALIDATE["array-leaders"] = v_leaders

p = add(
    id="record-breaking-days", title="Record-Breaking Days", diff="Easy", topic=TOPIC,
    fn="countRecordDays", params=[("visitors", "int[]")], ret="int", cmp="exact",
    desc="<p>A website logs how many people visited it on each of <code>n</code> days: <code>visitors[i]</code> is the count for day <code>i</code>. A day is <em>record-breaking</em> when both conditions hold:</p><ul><li>its count is strictly larger than the count of <strong>every</strong> earlier day (day 0 has no earlier days, so this part is true for it), and</li><li>it is the last day, or its count is strictly larger than the count of the next day.</li></ul><p>Return the number of record-breaking days.</p><p><strong>Example:</strong> <code>visitors = [1, 2, 0, 7, 2, 0, 2, 2]</code> returns <code>2</code>. Day 1 (count 2) beats day 0 and day 2; day 3 (count 7) beats everything before and after. Day 0 does not beat day 1, and the 2s later are not above the record 7.</p>",
    constraints=["1 &le; visitors.length &le; 10,000", "0 &le; visitors[i] &le; 10<sup>9</sup>"],
    hints=["Checking each day against all earlier days works in O(n<sup>2</sup>). What single number summarises 'all earlier days'?",
           "Keep the maximum count of the days before the current one. A day beats all earlier days exactly when it is above that maximum.",
           "While scanning, compare <code>visitors[i]</code> with the running maximum and also with <code>visitors[i + 1]</code> (when it exists). Update the running maximum after the check."],
    editorial=["Beating every earlier day is the same as beating the largest earlier day, so carry a running maximum <code>best</code> (initially below any valid count, for example <code>-1</code>). On day <code>i</code>, the day is a record if <code>visitors[i] &gt; best</code> and (<code>i</code> is last or <code>visitors[i] &gt; visitors[i + 1]</code>). After the test, set <code>best = max(best, visitors[i])</code>.",
               "Strictness matters. Two days with the same count do not break each other's record, so a plateau such as <code>[5, 5, 5]</code> has zero record days. Because the running maximum only grows, a record day is also always a new running maximum, which is why the sequence of records is increasing.",
               "One pass, O(n) time and O(1) space."],
    time="O(n)", space="O(1)",
    solution='''def countRecordDays(visitors):
    n = len(visitors)
    best = -1
    count = 0
    for i in range(n):
        if visitors[i] > best and (i == n - 1 or visitors[i] > visitors[i + 1]):
            count += 1
        best = max(best, visitors[i])
    return count
''',
    tests=[[[1, 2, 0, 7, 2, 0, 2, 2]], [[8]], [[1, 2, 3, 4]], [[4, 3, 2, 1]], [[5, 5, 5]], [[2, 2, 3]], [[0]], [[0, 0]],
           [[3, 1, 4, 1, 5, 9, 2, 6]], [[10 ** 9, 0, 10 ** 9]], [[1, 3, 2, 5, 4, 7, 6, 9, 8]], [[2, 1, 2, 1, 2, 1]]],
)
_r = rnd(9103)
p["tests"].append([[_r.randint(0, 10 ** 9) for _ in range(3000)]])
_a = []
for _i in range(2500):
    _a += [_i * 2 + 1, _i * 2]
p["tests"].append([_a])
p["tests"].append([[_r.randint(0, 1000) for _ in range(5000)]])


def b_records(v):
    n = len(v)
    return sum(1 for i in range(n) if all(v[i] > v[j] for j in range(i)) and (i == n - 1 or v[i] > v[i + 1]))


def v_records(tests):
    for t in tests:
        v = t["args"][0]
        assert 1 <= len(v) <= 10000 and all(0 <= x <= 10 ** 9 for x in v)


CHECKS["record-breaking-days"] = (b_records, lambda r: [gen_arr(r, 0, 6, 1, 9)], "exact")
VALIDATE["record-breaking-days"] = v_records

# ---------------------------------------------------------------- MEDIUM

p = add(
    id="max-width-ramp", title="Maximum Width Ramp", diff="Medium", topic=TOPIC,
    fn="maxWidthRamp", params=[("nums", "int[]")], ret="int", cmp="exact",
    desc="<p>A <em>ramp</em> in <code>nums</code> is a pair of indices <code>(i, j)</code> with <code>i &lt; j</code> and <code>nums[i] &le; nums[j]</code>. Its <em>width</em> is <code>j - i</code>.</p><p>Return the largest width of any ramp, or <code>0</code> if there is no ramp at all.</p><p><strong>Example:</strong> <code>nums = [6, 0, 8, 2, 1, 5]</code> returns <code>4</code>, using <code>i = 1</code> (value 0) and <code>j = 5</code> (value 5).</p>",
    constraints=["1 &le; nums.length &le; 10,000", "-2<sup>31</sup> &le; nums[i] &le; 2<sup>31</sup> - 1"],
    hints=["Trying every pair is O(n<sup>2</sup>). For a fixed right end j, which left ends i are even worth considering?",
           "A left end i is useless if some earlier index has a value that is smaller or equal: that earlier index gives a wider ramp for every j. So only strict prefix minima can be the best left end.",
           "Collect the indices of strict prefix minima (their values decrease). Then scan j from the right; while the top candidate has a value &le; nums[j], pop it and record the width. Popped candidates are never needed again, because a smaller j gives a smaller width."],
    editorial=["The best left end is always a position where the prefix minimum drops to a new strict low: if an earlier index <code>k</code> has <code>nums[k] &le; nums[i]</code>, then any ramp starting at <code>i</code> can start at <code>k</code> instead and be wider. List those indices left to right; their values are strictly decreasing.",
               "Now sweep <code>j</code> from the right end to the left. The top of the candidate list is the candidate with the largest index and the smallest value. While it satisfies <code>nums[cand] &le; nums[j]</code>, it forms a ramp with <code>j</code>; record <code>j - cand</code> and discard it. It can be discarded safely: every later <code>j</code> is smaller, so it can only give narrower ramps with this candidate.",
               "Each index enters and leaves the candidate list at most once, so the work is O(n) time and O(n) space. A binary search over the candidate list per <code>j</code> gives O(n log n) and is also acceptable."],
    time="O(n)", space="O(n)",
    solution='''def maxWidthRamp(nums):
    cand = []
    for i, x in enumerate(nums):
        if not cand or x < nums[cand[-1]]:
            cand.append(i)
    best = 0
    for j in range(len(nums) - 1, -1, -1):
        while cand and nums[cand[-1]] <= nums[j]:
            best = max(best, j - cand.pop())
        if not cand:
            break
    return best
''',
    tests=[[[6, 0, 8, 2, 1, 5]], [[9, 8, 1, 0, 1, 9, 4, 0, 4, 1]], [[5, 4, 3, 2, 1]], [[1]], [[2, 2]], [[1, 2]], [[2, 1]], [[3, 3, 3, 3]],
           [[INT_MAX, INT_MIN, INT_MAX]], [[INT_MIN, INT_MAX]], [[4, 7, 1, 3, 0, 6, 2]], [[5, 1, 6, 0, 4, 2, 3]]],
)
_r = rnd(9104)
p["tests"].append([[_r.randint(0, 100000) for _ in range(5000)]])
p["tests"].append([list(range(5000, 0, -1)) + [5000]])
p["tests"].append([sorted((_r.randint(-10000, 10000) for _ in range(4000)), reverse=True) + [_r.randint(-10000, 10000) for _ in range(2000)]])


def b_ramp(nums):
    n = len(nums)
    return max([j - i for i in range(n) for j in range(i + 1, n) if nums[i] <= nums[j]] + [0])


def v_ramp(tests):
    for t in tests:
        assert 1 <= len(t["args"][0]) <= 10000


CHECKS["max-width-ramp"] = (b_ramp, lambda r: [gen_arr(r, -5, 5, 1, 10)], "exact")
VALIDATE["max-width-ramp"] = v_ramp

p = add(
    id="longest-mountain-subarray", title="Longest Mountain Subarray", diff="Medium", topic=TOPIC,
    fn="longestMountain", params=[("heights", "int[]")], ret="int", cmp="exact",
    desc="<p>A contiguous piece of <code>heights</code> is a <em>mountain</em> if it has at least 3 elements and there is a peak position strictly inside it such that the values strictly increase up to the peak and then strictly decrease after it.</p><p>Return the length of the longest mountain, or <code>0</code> if none exists. Flat steps (equal neighbours) break a mountain.</p><p><strong>Example:</strong> <code>heights = [2, 1, 4, 7, 3, 2, 5]</code> returns <code>5</code>, for the piece <code>[1, 4, 7, 3, 2]</code>.</p>",
    constraints=["1 &le; heights.length &le; 10,000", "0 &le; heights[i] &le; 100,000"],
    hints=["Checking every subarray costs far too much. Think about what a mountain looks like around its peak.",
           "Every mountain is determined by its peak: it extends left while values strictly decrease going left, and right while values strictly decrease going right. A peak is an index with both neighbours smaller.",
           "For each peak, walk outwards to find the base on each side, record the length, and then continue scanning after the right base. Each index is visited a constant number of times."],
    editorial=["An index <code>i</code> can be a peak only if <code>heights[i - 1] &lt; heights[i] &gt; heights[i + 1]</code>. For such a peak, the longest mountain through it is found by walking left while heights keep strictly decreasing and walking right while they keep strictly decreasing. The mountain length is <code>right - left + 1</code>.",
               "To keep the total work linear, after processing a peak continue the scan just after the right base: the descent you just walked contains no other peak, since a strictly decreasing run has no local maximum. The ascent walk to the left only covers indices after the previous mountain's base, so every index is walked a constant number of times in total.",
               "An equivalent version keeps two counters while scanning, 'steps up' and 'steps down', and resets them on a flat step or when a new ascent starts after a descent. Both run in O(n) time with O(1) space."],
    time="O(n)", space="O(1)",
    solution='''def longestMountain(heights):
    n = len(heights)
    best = 0
    i = 1
    while i < n - 1:
        if heights[i - 1] < heights[i] > heights[i + 1]:
            left = i
            while left > 0 and heights[left - 1] < heights[left]:
                left -= 1
            right = i
            while right < n - 1 and heights[right] > heights[right + 1]:
                right += 1
            best = max(best, right - left + 1)
            i = right + 1
        else:
            i += 1
    return best
''',
    tests=[[[2, 1, 4, 7, 3, 2, 5]], [[2, 2, 2]], [[1, 2, 3]], [[3, 2, 1]], [[1, 3, 2]], [[1, 2, 1, 2, 1]], [[0, 1, 2, 3, 4, 5, 4, 3, 2, 1, 0]],
           [[1, 2, 2, 1]], [[1, 2, 3, 2, 1, 2, 3, 4, 3, 2, 1, 0]], [[1]], [[5, 1, 5]], [[0, 5, 0, 5, 0, 5, 0, 5, 0]]],
)
_r = rnd(9105)
p["tests"].append([list(range(0, 3000)) + list(range(3000, 0, -1))])
_a = []
for _ in range(600):
    _h = _r.randint(1, 6)
    _a += list(range(_r.randint(0, 3), _r.randint(0, 3) + _h)) + list(range(_h, -1, -1))
p["tests"].append([[min(max(x, 0), 100000) for x in _a]])
p["tests"].append([[_r.randint(0, 100000) for _ in range(5000)]])


def b_mountain(h):
    n = len(h)
    best = 0
    for i in range(n):
        for j in range(i + 3, n + 1):
            s = h[i:j]
            k = s.index(max(s))
            if 0 < k < len(s) - 1 and all(s[a] < s[a + 1] for a in range(k)) and all(s[a] > s[a + 1] for a in range(k, len(s) - 1)):
                best = max(best, len(s))
    return best


def v_mountain(tests):
    for t in tests:
        h = t["args"][0]
        assert 1 <= len(h) <= 10000 and all(0 <= x <= 100000 for x in h)


CHECKS["longest-mountain-subarray"] = (b_mountain, lambda r: [gen_arr(r, 0, 4, 1, 11)], "exact")
VALIDATE["longest-mountain-subarray"] = v_mountain

p = add(
    id="maximum-ordered-triplet-value", title="Maximum Ordered Triplet Value", diff="Medium", topic=TOPIC,
    fn="maxTripletValue", params=[("nums", "int[]")], ret="int", cmp="exact",
    desc="<p>Choose three indices <code>i &lt; j &lt; k</code> in <code>nums</code>. The value of the triplet is <code>(nums[i] - nums[j]) * nums[k]</code>.</p><p>Return the maximum value over all triplets. If every triplet has a negative value, return <code>0</code>.</p><p><strong>Example:</strong> <code>nums = [12, 6, 1, 2, 7]</code> returns <code>77</code>, from <code>(12 - 1) * 7</code> with indices 0, 2, 4.</p>",
    constraints=["3 &le; nums.length &le; 10,000", "1 &le; nums[i] &le; 30,000"],
    hints=["Three nested loops are O(n<sup>3</sup>). Fix the middle index j: which i and which k are best for it?",
           "All values are positive, so for a fixed j you want the largest nums[i] to the left of j and the largest nums[k] to the right of j (when the difference is positive).",
           "Keep a running maximum of the values seen so far and a running best difference <code>max(nums[i] - nums[j])</code>. At each position, first try it as k (multiply the best difference by it), then update the difference, then update the maximum."],
    editorial=["Every value is at least 1, so the best <code>nums[k]</code> for a given best difference is simply as large as possible and the best difference is as large as possible; the two choices do not interfere except through ordering (<code>i &lt; j &lt; k</code>).",
               "Scan once, maintaining <code>prefMax</code> (the largest value before the current index) and <code>bestDiff</code> (the largest <code>nums[i] - nums[j]</code> over pairs <code>i &lt; j</code> before the current index). At the current element <code>x</code>: first update the answer with <code>bestDiff * x</code> (x acts as k), then update <code>bestDiff = max(bestDiff, prefMax - x)</code> (x acts as j), then update <code>prefMax = max(prefMax, x)</code> (x acts as i). The order of those three lines guarantees the indices are strictly increasing.",
               "Starting <code>bestDiff</code> at 0 is safe: it makes the product 0, which is the required answer when all triplets are negative. The largest possible result is below 9 * 10<sup>8</sup>, so it fits in 32 bits. Time O(n), space O(1)."],
    time="O(n)", space="O(1)",
    solution='''def maxTripletValue(nums):
    best = 0
    pref_max = 0
    best_diff = 0
    for x in nums:
        best = max(best, best_diff * x)
        best_diff = max(best_diff, pref_max - x)
        pref_max = max(pref_max, x)
    return best
''',
    tests=[[[12, 6, 1, 2, 7]], [[1, 10, 3, 4, 19]], [[1, 2, 3]], [[5, 5, 5]], [[30000, 1, 30000]], [[1, 1, 1, 1]], [[3, 2, 1]],
           [[1, 2, 3, 4, 5, 6]], [[30000, 29999, 1, 30000]], [[2, 9, 1, 8, 1, 9]], [[7, 7, 1, 7, 7, 7]], [[10, 3, 20, 1, 5, 2]]],
)
_r = rnd(9106)
p["tests"].append([[_r.randint(1, 30000) for _ in range(5000)]])
p["tests"].append([[_r.randint(1, 30000) for _ in range(10)] + [1] * 2000 + [30000]])
p["tests"].append([list(range(1, 4001))])


def b_triplet(nums):
    n = len(nums)
    best = 0
    for i, j, k in combinations(range(n), 3):
        best = max(best, (nums[i] - nums[j]) * nums[k])
    return best


def v_triplet(tests):
    for t in tests:
        a = t["args"][0]
        assert 3 <= len(a) <= 10000 and all(1 <= x <= 30000 for x in a)


CHECKS["maximum-ordered-triplet-value"] = (b_triplet, lambda r: [gen_arr(r, 1, 12, 3, 9)], "exact")
VALIDATE["maximum-ordered-triplet-value"] = v_triplet

p = add(
    id="increasing-run-after-one-removal", title="Longest Increasing Run After One Removal", diff="Medium", topic=TOPIC,
    fn="longestRunAfterRemoval", params=[("nums", "int[]")], ret="int", cmp="exact",
    desc="<p>You may delete <strong>at most one</strong> element of <code>nums</code> (or delete nothing). After the deletion, the remaining elements close up into a shorter array. Return the largest possible length of a contiguous, <em>strictly increasing</em> run in the resulting array.</p><p><strong>Example:</strong> <code>nums = [1, 3, 5, 4, 7]</code> returns <code>4</code>: delete the 4 to get <code>[1, 3, 5, 7]</code>. Deleting the 5 instead gives <code>[1, 3, 4, 7]</code>, also of length 4.</p>",
    constraints=["1 &le; nums.length &le; 10,000", "-10<sup>9</sup> &le; nums[i] &le; 10<sup>9</sup>"],
    hints=["Trying every deletion and rescanning costs O(n<sup>2</sup>). Which pieces of the original array get glued together by a deletion?",
           "Deleting index i glues the strictly increasing run that ends at i - 1 to the strictly increasing run that starts at i + 1. The glue works only if nums[i - 1] &lt; nums[i + 1].",
           "Precompute <code>endHere[i]</code> (length of the increasing run ending at i) and <code>startHere[i]</code> (length of the run starting at i). The answer is the larger of the best plain run and <code>endHere[i - 1] + startHere[i + 1]</code> over all i with <code>nums[i - 1] &lt; nums[i + 1]</code>."],
    editorial=["A deletion can only help by joining two runs that were separated by the deleted element. If we delete index <code>i</code>, the new run through the gap consists of the strictly increasing run ending at <code>i - 1</code> followed by the strictly increasing run starting at <code>i + 1</code>; these two form one run exactly when <code>nums[i - 1] &lt; nums[i + 1]</code>. The deleted element itself does not count towards the length.",
               "Compute <code>endHere</code> with a left-to-right pass (<code>endHere[i] = endHere[i - 1] + 1</code> if <code>nums[i - 1] &lt; nums[i]</code>, else 1) and <code>startHere</code> with a right-to-left pass. The answer is the maximum of the longest run in the untouched array (also the answer with no deletion) and <code>endHere[i - 1] + startHere[i + 1]</code> for each valid <code>i</code> from 1 to n - 2. Deleting the first or last element never creates a longer run than the plain maximum.",
               "Three linear passes, O(n) time and O(n) space. The same idea of 'run ending here + run starting there' solves many 'at most one change' run problems."],
    time="O(n)", space="O(n)",
    solution='''def longestRunAfterRemoval(nums):
    n = len(nums)
    end = [1] * n
    for i in range(1, n):
        if nums[i - 1] < nums[i]:
            end[i] = end[i - 1] + 1
    start = [1] * n
    for i in range(n - 2, -1, -1):
        if nums[i] < nums[i + 1]:
            start[i] = start[i + 1] + 1
    best = max(end)
    for i in range(1, n - 1):
        if nums[i - 1] < nums[i + 1]:
            best = max(best, end[i - 1] + start[i + 1])
    return best
''',
    tests=[[[1, 3, 5, 4, 7]], [[2, 2, 2]], [[5, 4, 3, 2, 1]], [[1]], [[1, 2]], [[2, 1]], [[1, 2, 3, 4]], [[1, 5, 2, 3, 4]], [[1, 2, 10, 5, 7]],
           [[3, 1, 2, 1, 2, 3]], [[-10 ** 9, 10 ** 9, -10 ** 9, 10 ** 9]], [[1, 2, 3, 3, 4, 5]], [[1, 2, 5, 3, 3, 4]]],
)
_r = rnd(9107)
p["tests"].append([[i + _r.choice([0, 0, 0, 0, 0, 7, -7]) for i in range(5000)]])
p["tests"].append([[_r.randint(0, 3) for _ in range(5000)]])
p["tests"].append([list(range(2500)) + [-5] + list(range(2600, 5000))])


def b_runrem(nums):
    best = 0
    for d in range(-1, len(nums)):
        a = nums if d < 0 else nums[:d] + nums[d + 1:]
        cur = 0
        for i in range(len(a)):
            cur = cur + 1 if i and a[i - 1] < a[i] else 1
            best = max(best, cur)
    return best


def v_runrem(tests):
    for t in tests:
        a = t["args"][0]
        assert 1 <= len(a) <= 10000 and all(-10 ** 9 <= x <= 10 ** 9 for x in a)


CHECKS["increasing-run-after-one-removal"] = (b_runrem, lambda r: [gen_arr(r, 0, 5, 1, 10)], "exact")
VALIDATE["increasing-run-after-one-removal"] = v_runrem

p = add(
    id="max-chunks-sorted-permutation", title="Max Chunks to Sort a Permutation", diff="Medium", topic=TOPIC,
    fn="maxChunksToSorted", params=[("arr", "int[]")], ret="int", cmp="exact",
    desc="<p><code>arr</code> is a permutation of the integers <code>0..n-1</code>. Cut it into some number of contiguous chunks, sort every chunk on its own, and glue the chunks back together in their original order. You want the glued result to be the fully sorted array <code>[0, 1, ..., n-1]</code>.</p><p>Return the largest number of chunks for which this works.</p><p><strong>Example:</strong> <code>arr = [1, 0, 2, 3, 4]</code> returns <code>4</code>: chunks <code>[1, 0]</code>, <code>[2]</code>, <code>[3]</code>, <code>[4]</code>.</p>",
    constraints=["1 &le; arr.length &le; 10,000", "arr is a permutation of 0 .. arr.length - 1"],
    hints=["A cut after position i is allowed only if everything on its left belongs to the left part of the sorted array. Which values must be on the left?",
           "After a cut at i (left part has i + 1 elements), the left part must contain exactly the values 0..i.",
           "Because arr is a permutation, the left part {arr[0..i]} equals {0..i} exactly when the maximum of arr[0..i] equals i. Count such positions."],
    editorial=["Sorting a chunk puts its values in order inside the chunk's own positions, so the final array is sorted only if each chunk, occupying positions <code>l..r</code>, contains exactly the values <code>l..r</code>. A cut after index <code>i</code> is therefore valid precisely when the first <code>i + 1</code> elements are the values <code>0..i</code>.",
               "For a permutation, the first <code>i + 1</code> elements are <code>i + 1</code> distinct values from <code>0..n-1</code>, so their maximum is at least <code>i</code>; it equals <code>i</code> exactly when they are <code>0..i</code>. Scan with a running maximum and count the indices where <code>max == i</code>. Each such index ends a chunk, and since cutting at every valid place gives the most chunks, that count is the answer.",
               "One pass: O(n) time, O(1) space. (When values repeat or are arbitrary, this no longer works; the harder version compares a prefix maximum with a suffix minimum.)"],
    time="O(n)", space="O(1)",
    solution='''def maxChunksToSorted(arr):
    mx = -1
    chunks = 0
    for i, x in enumerate(arr):
        mx = max(mx, x)
        if mx == i:
            chunks += 1
    return chunks
''',
    tests=[[[1, 0, 2, 3, 4]], [[4, 3, 2, 1, 0]], [[0]], [[0, 1, 2, 3]], [[1, 0]], [[2, 1, 0, 3]], [[1, 2, 0, 4, 3]], [[3, 0, 1, 2, 5, 4]],
           [[0, 2, 1, 4, 3, 6, 5]], [[2, 0, 1, 3, 5, 4, 7, 6]], [[1, 0, 3, 2, 5, 4, 7, 6, 9, 8]]],
)
_r = rnd(9108)
_p = list(range(5000)); _r.shuffle(_p)
p["tests"].append([_p])
_p = []
_b = 0
while _b < 5000:
    _s = min(_r.randint(1, 6), 5000 - _b)
    _blk = list(range(_b, _b + _s)); _r.shuffle(_blk)
    _p += _blk
    _b += _s
p["tests"].append([_p])
p["tests"].append([list(range(5000))])
p["tests"].append([list(range(4999, -1, -1))])


def b_chunks(arr):
    n = len(arr)
    target = sorted(arr)
    best = 0
    for mask in range(1 << (n - 1)):
        cuts = [0] + [i + 1 for i in range(n - 1) if mask >> i & 1] + [n]
        out = []
        for a, b in zip(cuts, cuts[1:]):
            out += sorted(arr[a:b])
        if out == target:
            best = max(best, len(cuts) - 1)
    return best


def g_chunks(r):
    a = list(range(r.randint(1, 9)))
    r.shuffle(a)
    return [a]


def v_chunks(tests):
    for t in tests:
        a = t["args"][0]
        assert 1 <= len(a) <= 10000 and sorted(a) == list(range(len(a)))


CHECKS["max-chunks-sorted-permutation"] = (b_chunks, g_chunks, "exact")
VALIDATE["max-chunks-sorted-permutation"] = v_chunks

p = add(
    id="best-sightseeing-pair", title="Best Sightseeing Pair", diff="Medium", topic=TOPIC,
    fn="bestSightseeingPair", params=[("scores", "int[]")], ret="int", cmp="exact",
    desc="<p>Along a trail, spot <code>i</code> has a beauty score <code>scores[i]</code>. You choose two spots <code>i &lt; j</code> to visit. The value of the pair is the sum of the two scores minus the distance between them:</p><p><code>scores[i] + scores[j] - (j - i)</code></p><p>Return the maximum value over all pairs.</p><p><strong>Example:</strong> <code>scores = [8, 1, 5, 2, 6]</code> returns <code>11</code>, from spots 0 and 2: <code>8 + 5 - 2</code>.</p>",
    constraints=["2 &le; scores.length &le; 10,000", "1 &le; scores[i] &le; 10<sup>9</sup>"],
    hints=["Trying all pairs is O(n<sup>2</sup>). Rewrite the value so that the part depending on i and the part depending on j are separate.",
           "scores[i] + scores[j] - (j - i) = (scores[i] + i) + (scores[j] - j).",
           "Scan j from left to right while keeping the maximum of <code>scores[i] + i</code> over all earlier i. At each j the best pair ending at j is that maximum plus <code>scores[j] - j</code>."],
    editorial=["The value splits into <code>(scores[i] + i) + (scores[j] - j)</code>. For a fixed <code>j</code>, only the first bracket depends on <code>i</code>, and we want it as large as possible over all <code>i &lt; j</code>. That is a prefix maximum.",
               "Initialise <code>left = scores[0] + 0</code>. For each <code>j</code> from 1 to <code>n - 1</code>, update <code>best = max(best, left + scores[j] - j)</code> and then <code>left = max(left, scores[j] + j)</code>. The order matters: <code>j</code> must not pair with itself.",
               "O(n) time and O(1) space. The largest possible answer is just under 2 * 10<sup>9</sup>, which still fits in a signed 32-bit integer."],
    time="O(n)", space="O(1)",
    solution='''def bestSightseeingPair(scores):
    left = scores[0]
    best = None
    for j in range(1, len(scores)):
        cand = left + scores[j] - j
        if best is None or cand > best:
            best = cand
        left = max(left, scores[j] + j)
    return best
''',
    tests=[[[8, 1, 5, 2, 6]], [[1, 2]], [[1, 1, 1, 1]], [[5, 1, 1, 1, 1, 1, 5]], [[10 ** 9, 10 ** 9]], [[3, 1]], [[1, 10 ** 9]],
           [[7, 7, 7]], [[2, 9, 3, 3, 9, 2]], [[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 100]], [[100, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]], [[4, 6, 5, 4, 3, 2, 1]]],
)
_r = rnd(9109)
p["tests"].append([[_r.randint(1, 10 ** 9) for _ in range(3000)]])
p["tests"].append([[_r.randint(1, 50) for _ in range(5000)]])
p["tests"].append([[1] * 4000 + [10 ** 9] + [1] * 1000])


def b_sight(s):
    n = len(s)
    return max(s[i] + s[j] - (j - i) for i in range(n) for j in range(i + 1, n))


def v_sight(tests):
    for t in tests:
        a = t["args"][0]
        assert 2 <= len(a) <= 10000 and all(1 <= x <= 10 ** 9 for x in a)


CHECKS["best-sightseeing-pair"] = (b_sight, lambda r: [gen_arr(r, 1, 12, 2, 10)], "exact")
VALIDATE["best-sightseeing-pair"] = v_sight

# ---------------------------------------------------------------- HARD

p = add(
    id="max-chunks-sorted-with-duplicates", title="Max Chunks to Sort (Any Values)", diff="Hard", topic=TOPIC, tier="extra",
    fn="maxChunksToSortedAny", params=[("arr", "int[]")], ret="int", cmp="exact",
    desc="<p>Cut the integer array <code>arr</code> into contiguous chunks, sort each chunk on its own, and concatenate the chunks in their original order. The values may be negative and may repeat. You want the concatenation to equal <code>arr</code> sorted in non-decreasing order.</p><p>Return the maximum number of chunks that makes this possible.</p><p><strong>Example:</strong> <code>arr = [2, 1, 3, 4, 4]</code> returns <code>4</code>: chunks <code>[2, 1]</code>, <code>[3]</code>, <code>[4]</code>, <code>[4]</code>.</p>",
    constraints=["1 &le; arr.length &le; 10,000", "-2<sup>31</sup> &le; arr[i] &le; 2<sup>31</sup> - 1"],
    hints=["When is a cut between position i and i + 1 allowed? Think about the values on each side, not their positions.",
           "After sorting each chunk, the glued array is sorted only if every element on the left of a cut is &le; every element on the right of it.",
           "That condition is: max of the prefix arr[0..i] &le; min of the suffix arr[i+1..]. Precompute suffix minimums, sweep with a running prefix maximum, and count the allowed cuts; the answer is cuts + 1."],
    editorial=["Consider a single cut. The chunks on the left are sorted among themselves and so are those on the right, so the final array is sorted if and only if no element on the left is greater than any element on the right at every cut simultaneously. For one cut between <code>i</code> and <code>i + 1</code> that means <code>max(arr[0..i]) &le; min(arr[i+1..])</code>. Equal values are fine on both sides, which is the key difference from the permutation version, where the test reduces to <code>max == i</code>.",
               "Cuts are independent: if every individual cut passes the test, using all of them is valid, because each chunk then sits between neighbours that are no larger and no smaller than it should be. Using all allowed cuts gives the maximum, so the answer is the number of allowed cuts plus one.",
               "Build <code>sufMin</code> from the right, then sweep from the left with a running maximum. Both passes are O(n); memory is O(n) for the suffix minimums. (A monotonic stack that keeps one maximum per chunk gives the same answer in one pass.)"],
    time="O(n)", space="O(n)",
    solution='''def maxChunksToSortedAny(arr):
    n = len(arr)
    suf = [0] * n
    suf[-1] = arr[-1]
    for i in range(n - 2, -1, -1):
        suf[i] = min(arr[i], suf[i + 1])
    chunks = 1
    mx = arr[0]
    for i in range(n - 1):
        mx = max(mx, arr[i])
        if mx <= suf[i + 1]:
            chunks += 1
    return chunks
''',
    tests=[[[2, 1, 3, 4, 4]], [[5, 4, 3, 2, 1]], [[1, 1, 1]], [[1]], [[3, 3, 1, 1]], [[1, 2, 3]], [[0, 0, 1, 1, 0]], [[-5, -5, 7, -9, 8, 8]],
           [[INT_MAX, INT_MIN]], [[INT_MIN, INT_MAX, INT_MIN, INT_MAX]], [[2, 1, 2, 1, 2, 1]], [[1, 0, 1, 3, 2]]],
)
_r = rnd(9110)
p["tests"].append([[_r.randint(0, 20) for _ in range(5000)]])
p["tests"].append([sorted(_r.randint(-1000, 1000) for _ in range(3000))])
_a = []
for _i in range(800):
    _blk = [_i * 10 + _r.randint(0, 9) for _ in range(_r.randint(1, 6))]
    _a += _blk
p["tests"].append([_a])
_a = sorted(_r.randint(-10000, 10000) for _ in range(5000))
for _ in range(400):
    _x = _r.randint(0, 4990)
    _y = _x + _r.randint(1, 9)
    _a[_x], _a[_y] = _a[_y], _a[_x]
p["tests"].append([_a])


def b_chunks2(arr):
    n = len(arr)
    target = sorted(arr)
    best = 0
    for mask in range(1 << (n - 1)):
        cuts = [0] + [i + 1 for i in range(n - 1) if mask >> i & 1] + [n]
        out = []
        for a, b in zip(cuts, cuts[1:]):
            out += sorted(arr[a:b])
        if out == target:
            best = max(best, len(cuts) - 1)
    return best


def v_chunks2(tests):
    for t in tests:
        a = t["args"][0]
        assert 1 <= len(a) <= 10000


CHECKS["max-chunks-sorted-with-duplicates"] = (b_chunks2, lambda r: [gen_arr(r, -3, 3, 1, 9)], "exact")
VALIDATE["max-chunks-sorted-with-duplicates"] = v_chunks2

p = add(
    id="min-range-increments-to-target", title="Minimum Range Increments to Build Target", diff="Hard", topic=TOPIC, tier="extra",
    fn="minRangeIncrements", params=[("target", "int[]")], ret="int", cmp="exact",
    desc="<p>You start with an array of <code>n</code> zeros. In one operation you choose any contiguous range of positions and add <code>1</code> to every element in that range.</p><p>Given the array <code>target</code>, return the minimum number of operations needed to turn the zero array into <code>target</code>.</p><p><strong>Example:</strong> <code>target = [3, 1, 5, 4, 2]</code> returns <code>7</code>. The target climbs by 3 at the first position (from the imaginary 0 to 3) and by 4 at the third (from 1 to 5); the other steps are flat or falls. That is 3 + 4 = 7 ranges, and fewer cannot create those climbs.</p>",
    constraints=["1 &le; target.length &le; 10,000", "0 &le; target[i] &le; 100,000"],
    hints=["Work out what each operation does to the differences between neighbours, <code>target[i] - target[i-1]</code>.",
           "A range operation adds 1 to the difference at its left end and subtracts 1 from the difference just after its right end. Everything else is unchanged.",
           "Every position where the target climbs (<code>target[i] &gt; target[i-1]</code>, with an imaginary 0 before the first element) needs at least that many ranges to <em>start</em> there. Sum the climbs."],
    editorial=["Treat <code>target[-1] = 0</code>. Each operation increases the difference at its first position by 1, decreases the difference just after its last position by 1 (if that position exists), and changes no other difference. To create a climb of size <code>d = target[i] - target[i-1] &gt; 0</code> we need at least <code>d</code> ranges that start at <code>i</code>. Falls never need extra ranges: they are produced by ending ranges that are already open.",
               "So the lower bound is the sum of all positive rises: <code>target[0] + sum(max(0, target[i] - target[i-1]))</code>. It is also achievable: whenever the target rises, start exactly that many new ranges; whenever it falls, end that many of the currently open ranges. Thus the lower bound is exact.",
               "One pass over the array, O(n) time and O(1) space. The answer is at most about 5 * 10<sup>8</sup> here, which fits in 32 bits."],
    time="O(n)", space="O(1)",
    solution='''def minRangeIncrements(target):
    total = 0
    prev = 0
    for x in target:
        if x > prev:
            total += x - prev
        prev = x
    return total
''',
    tests=[[[3, 1, 5, 4, 2]], [[1, 2, 3, 2, 1]], [[3, 1, 1, 2]], [[0]], [[5]], [[0, 0, 0]], [[1, 1, 1]], [[2, 0, 2]], [[100000, 0, 100000, 0]],
           [[0, 1, 0, 1, 0, 1]], [[4, 3, 2, 1]], [[1, 2, 3, 4]]],
)
_r = rnd(9111)
p["tests"].append([[_r.randint(0, 1000) for _ in range(5000)]])
p["tests"].append([[(i % 2) * 100000 for i in range(4000)]])
p["tests"].append([[_r.randint(0, 100000) for _ in range(3000)]])


def b_incr(t):
    def go(l, r, base):
        if l >= r:
            return 0
        m = min(t[l:r])
        cost = m - base
        i = l
        while i < r:
            if t[i] == m:
                i += 1
                continue
            j = i
            while j < r and t[j] != m:
                j += 1
            cost += go(i, j, m)
            i = j
        return cost
    return go(0, len(t), 0)


def v_incr(tests):
    for t in tests:
        a = t["args"][0]
        assert 1 <= len(a) <= 10000 and all(0 <= x <= 100000 for x in a)


CHECKS["min-range-increments-to-target"] = (b_incr, lambda r: [gen_arr(r, 0, 5, 1, 9)], "exact")
VALIDATE["min-range-increments-to-target"] = v_incr
