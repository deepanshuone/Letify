"""Problems: arrays & hashing, frequency counting. See data/lib.py for the registry."""
from collections import Counter
from math import gcd

from lib import add, rnd, CHECKS, VALIDATE, gen_arr  # noqa: F401

TOPIC = "Arrays & Hashing"
INT_MIN, INT_MAX = -(2 ** 31), 2 ** 31 - 1


# ---------------------------------------------------------------- EASY

p = add(
    id="nearby-duplicate-within-k", title="Nearby Duplicate Within Distance K", diff="Easy", topic=TOPIC,
    fn="hasNearbyDuplicate", params=[("nums", "int[]"), ("k", "int")], ret="bool", cmp="exact",
    desc="<p>Given an integer array <code>nums</code> and an integer <code>k</code>, return <code>true</code> if there are two different indices <code>i</code> and <code>j</code> such that <code>nums[i] == nums[j]</code> and <code>|i - j| &le; k</code>. Otherwise return <code>false</code>.</p><p>For example, <code>nums = [1, 2, 3, 1]</code> with <code>k = 3</code> gives <code>true</code> (indices 0 and 3), while <code>nums = [1, 2, 3, 1, 2, 3]</code> with <code>k = 2</code> gives <code>false</code>: equal values are always three positions apart.</p>",
    constraints=["1 &le; nums.length &le; 10,000", "-2<sup>31</sup> &le; nums[i] &le; 2<sup>31</sup> - 1", "0 &le; k &le; 10,000"],
    hints=["Comparing every pair of indices at distance at most <code>k</code> is correct but can be slow. What do you really need to know about a value you see again?",
           "Only the most recent earlier position of each value matters: if the closest previous equal element is farther than <code>k</code>, every older one is farther still.",
           "Keep a hash map from value to its last index. At index <code>i</code>, if the value is in the map and <code>i - last &le; k</code>, answer true; then store <code>i</code> as the new last index."],
    editorial=["Walk through the array once while remembering, for every value, the last index where it appeared. When the current value was seen before, the best candidate partner is exactly that last index, because any older occurrence is even farther away. If the gap is at most <code>k</code> you are done, otherwise overwrite the stored index with the current one and continue.",
               "This is O(n) time and O(n) space. An equivalent view is a sliding window of the last <code>k</code> elements kept in a set: add the new element, check for a repeat, and drop the element that leaves the window. That variant needs only O(min(n, k)) space."],
    time="O(n)", space="O(n)",
    solution='''def hasNearbyDuplicate(nums, k):
    last = {}
    for i, x in enumerate(nums):
        if x in last and i - last[x] <= k:
            return True
        last[x] = i
    return False
''',
    tests=[[[1, 2, 3, 1], 3], [[1, 0, 1, 1], 1], [[1, 2, 3, 1, 2, 3], 2], [[5], 0], [[7, 7], 0], [[7, 7], 1],
           [[1, 2, 1], 1], [[1, 2, 1], 2], [[-5, 3, -5], 2], [[INT_MAX, 0, 1, INT_MAX], 2],
           [[4, 4, 4, 4], 0], [[9, 8, 7, 6, 5, 4, 3, 2, 1, 9], 9]],
)
_r = rnd(7101)
_a = _r.sample(range(-10 ** 6, 10 ** 6), 3500); _a[3300] = _a[299]            # gap 3001
p["tests"].append([_a[:], 3000])
p["tests"].append([_a[:], 3001])
_a = _r.sample(range(-10 ** 6, 10 ** 6), 3000)
p["tests"].append([_a, 3000])                                                  # all distinct
p["tests"].append([[_r.randint(0, 10 ** 6) for _ in range(3000)], 1])


def b_nearby(nums, k):
    for i in range(len(nums)):
        for j in range(i + 1, min(len(nums), i + k + 1)):
            if nums[i] == nums[j]:
                return True
    return False


def v_nearby(tests):
    for t in tests:
        nums, k = t["args"]
        assert 1 <= len(nums) <= 10000 and 0 <= k <= 10000
        assert all(INT_MIN <= x <= INT_MAX for x in nums)
    ex = [t["expected"] for t in tests]
    assert True in ex and False in ex


CHECKS["nearby-duplicate-within-k"] = (b_nearby, lambda r: [gen_arr(r, 0, 5, 1, 10), r.randint(0, 6)], "exact")
VALIDATE["nearby-duplicate-within-k"] = v_nearby

p = add(
    id="count-identical-pairs", title="Count Identical Pairs", diff="Easy", topic=TOPIC,
    fn="countIdenticalPairs", params=[("nums", "int[]")], ret="int", cmp="exact",
    desc="<p>A pair of indices <code>(i, j)</code> with <code>i &lt; j</code> is <em>identical</em> when <code>nums[i] == nums[j]</code>. Return the number of identical pairs in <code>nums</code>.</p><p>For example, <code>[1, 2, 3, 1, 1, 3]</code> has 4 identical pairs: indices (0,3), (0,4), (3,4) and (2,5).</p>",
    constraints=["1 &le; nums.length &le; 10,000", "-2<sup>31</sup> &le; nums[i] &le; 2<sup>31</sup> - 1", "The answer is at most 49,995,000, so it fits in 32 bits"],
    hints=["Checking all pairs works for small inputs. How many pairs does a value that appears <code>c</code> times contribute on its own?",
           "Pairs can only be formed inside a group of equal values, so you can count each group separately.",
           "A value occurring <code>c</code> times gives <code>c * (c - 1) / 2</code> pairs. Count occurrences with a hash map and add these up (or add the current count each time you see a value again)."],
    editorial=["Group equal values with a frequency map. Inside a group of size <code>c</code> every two elements form a pair, so the group contributes <code>c(c-1)/2</code> pairs; groups of different values never contribute. Summing over all groups gives the answer in O(n).",
               "A one-pass variant keeps a running count per value: when you meet a value that has been seen <code>s</code> times before, it forms exactly <code>s</code> new pairs with those earlier copies, so add <code>s</code> to the total and then increment the count."],
    time="O(n)", space="O(n)",
    solution='''def countIdenticalPairs(nums):
    seen = {}
    total = 0
    for x in nums:
        s = seen.get(x, 0)
        total += s
        seen[x] = s + 1
    return total
''',
    tests=[[[1, 2, 3, 1, 1, 3]], [[1, 1, 1, 1]], [[1, 2, 3]], [[7]], [[5, 5]], [[0, 0, 0, 0, 1, 1]],
           [[-3, 3, -3, 3, -3]], [[INT_MAX, INT_MIN, INT_MAX, INT_MIN]], [[10 ** 9, 10 ** 9, -10 ** 9, 10 ** 9]]],
)
_r = rnd(7102)
p["tests"].append([[4] * 10000])
p["tests"].append([[_r.randint(-50, 50) for _ in range(6000)]])
p["tests"].append([[_r.randint(-10 ** 9, 10 ** 9) for _ in range(6000)]])


def b_identical(nums):
    return sum(1 for i in range(len(nums)) for j in range(i + 1, len(nums)) if nums[i] == nums[j])


def v_identical(tests):
    for t in tests:
        nums = t["args"][0]
        assert 1 <= len(nums) <= 10000 and all(INT_MIN <= x <= INT_MAX for x in nums)


CHECKS["count-identical-pairs"] = (b_identical, lambda r: [gen_arr(r, -3, 3, 1, 12)], "exact")
VALIDATE["count-identical-pairs"] = v_identical

p = add(
    id="most-frequent-even-element", title="Most Frequent Even Element", diff="Easy", topic=TOPIC,
    fn="mostFrequentEven", params=[("nums", "int[]")], ret="int", cmp="exact",
    desc="<p>Among the <strong>even</strong> numbers in <code>nums</code>, return the one that occurs most often. If several even numbers tie for the highest count, return the smallest of them. If <code>nums</code> contains no even number, return <code>-1</code>.</p><p>For example, <code>[0, 1, 2, 2, 4, 4, 1]</code> gives <code>2</code> (both 2 and 4 occur twice, and 2 is smaller), and <code>[1, 3, 5]</code> gives <code>-1</code>.</p>",
    constraints=["1 &le; nums.length &le; 10,000", "0 &le; nums[i] &le; 100,000"],
    hints=["First decide how to ignore the odd numbers; then you need the count of every even value.",
           "A hash map from value to count gives all frequencies in one pass over the array.",
           "Pick the entry with the larger count, and on equal counts the smaller value. Compare on the pair <code>(count, -value)</code> or update the answer only when the count is strictly larger or equal with a smaller value."],
    editorial=["Count the even values with a hash map (a Counter). Then scan the map and keep the best candidate under the ordering 'higher count wins, ties go to the smaller value'. If the map is empty there was no even number, so the answer is -1.",
               "Time is O(n) for counting plus O(d) for scanning the d distinct even values, space is O(d). Sorting the distinct values first would also settle ties but is unnecessary."],
    time="O(n)", space="O(n)",
    solution='''def mostFrequentEven(nums):
    cnt = {}
    for x in nums:
        if x % 2 == 0:
            cnt[x] = cnt.get(x, 0) + 1
    best, best_c = -1, 0
    for v, c in cnt.items():
        if c > best_c or (c == best_c and v < best):
            best, best_c = v, c
    return best
''',
    tests=[[[0, 1, 2, 2, 4, 4, 1]], [[1, 3, 5]], [[4, 4, 4, 9, 9, 9, 9]], [[2]], [[0]], [[1]],
           [[100000, 99998, 99998, 100000]], [[6, 8, 6, 8, 7, 7, 7]], [[5, 5, 5, 2, 4]], [[0, 0, 2, 2, 2, 0]]],
)
_r = rnd(7103)
p["tests"].append([[_r.randint(0, 100000) for _ in range(8000)]])
p["tests"].append([[_r.choice([1, 3, 5, 7, 9, 99999]) for _ in range(5000)]])
_a = [_r.randint(0, 40) for _ in range(8000)]
p["tests"].append([_a])


def b_even(nums):
    evens = sorted(set(x for x in nums if x % 2 == 0))
    if not evens:
        return -1
    top = max(nums.count(v) for v in evens)
    return [v for v in evens if nums.count(v) == top][0]


def v_even(tests):
    for t in tests:
        nums = t["args"][0]
        assert 1 <= len(nums) <= 10000 and all(0 <= x <= 100000 for x in nums)
    assert any(t["expected"] == -1 for t in tests)


CHECKS["most-frequent-even-element"] = (b_even, lambda r: [gen_arr(r, 0, 9, 1, 12)], "exact")
VALIDATE["most-frequent-even-element"] = v_even

# ---------------------------------------------------------------- MEDIUM

p = add(
    id="count-nice-pairs-with-reversal", title="Count Nice Pairs", diff="Medium", topic=TOPIC,
    fn="countNicePairs", params=[("nums", "int[]")], ret="int", cmp="exact",
    desc="<p>For a non-negative integer <code>x</code>, let <code>rev(x)</code> be <code>x</code> with its decimal digits reversed; leading zeros after reversing disappear, so <code>rev(120) = 21</code>.</p><p>A pair of indices <code>(i, j)</code> with <code>i &lt; j</code> is <em>nice</em> if <code>nums[i] + rev(nums[j]) == nums[j] + rev(nums[i])</code>. Return the number of nice pairs.</p><p>For example, <code>[42, 11, 1, 97]</code> has 2 nice pairs: (42, 97) and (11, 1).</p>",
    constraints=["1 &le; nums.length &le; 10,000", "0 &le; nums[i] &le; 10<sup>9</sup>", "The answer is at most 49,995,000"],
    hints=["Trying all pairs is O(n<sup>2</sup>). Look at the condition: can you move everything about <code>nums[i]</code> to one side and everything about <code>nums[j]</code> to the other?",
           "Rearranged, the condition says <code>nums[i] - rev(nums[i]) == nums[j] - rev(nums[j])</code>.",
           "Compute <code>key = x - rev(x)</code> for every element. Two elements form a nice pair exactly when their keys are equal, so count equal keys with a hash map."],
    editorial=["Subtract <code>rev(nums[i]) + nums[j]</code> from both sides of the condition and it becomes <code>nums[i] - rev(nums[i]) == nums[j] - rev(nums[j])</code>. The problem is therefore the same as counting pairs of equal keys, where the key of an element is <code>x - rev(x)</code>.",
               "Process the array left to right with a map from key to number of earlier elements with that key; each new element forms that many new pairs, then increments its key's count. Reversing a number costs O(log x), so the total is O(n log M) time and O(n) space."],
    time="O(n log M)", space="O(n)",
    solution='''def countNicePairs(nums):
    seen = {}
    total = 0
    for x in nums:
        key = x - int(str(x)[::-1])
        s = seen.get(key, 0)
        total += s
        seen[key] = s + 1
    return total
''',
    tests=[[[42, 11, 1, 97]], [[13, 10, 35, 24, 76]], [[0]], [[0, 0]], [[121, 343, 5]], [[120, 21, 12]], [[10, 1]],
           [[1000000000, 1, 1000000000]], [[19, 91, 28, 82]], [[7, 70, 700]]],
)
_r = rnd(7106)


def _mk_nice(r, n):
    out = []
    for _ in range(n):
        t = r.random()
        if t < 0.4:                                # palindromes: key 0
            h = str(r.randint(1, 9999))
            out.append(int(h + h[::-1]))
        elif t < 0.6:                              # two-digit numbers: key is a multiple of 9
            out.append(r.randint(10, 99))
        else:
            out.append(r.randint(0, 10 ** 9))
    return out


p["tests"].append([_mk_nice(_r, 5000)])
p["tests"].append([[_r.randint(0, 99) for _ in range(6000)]])
p["tests"].append([[int(str(_r.randint(1, 999)) * 2) if _r.random() < 0.7 else _r.randint(0, 10 ** 9) for _ in range(5000)]])


def b_nice(nums):
    rv = lambda x: int(str(x)[::-1])
    return sum(1 for i in range(len(nums)) for j in range(i + 1, len(nums))
               if nums[i] + rv(nums[j]) == nums[j] + rv(nums[i]))


def v_nice(tests):
    for t in tests:
        nums = t["args"][0]
        assert 1 <= len(nums) <= 10000 and all(0 <= x <= 10 ** 9 for x in nums)
        assert t["expected"] <= 49995000


CHECKS["count-nice-pairs-with-reversal"] = (b_nice, lambda r: [gen_arr(r, 0, 130, 1, 12)], "exact")
VALIDATE["count-nice-pairs-with-reversal"] = v_nice

p = add(
    id="count-equal-ratio-rectangles", title="Count Rectangle Pairs With Equal Ratio", diff="Medium", topic=TOPIC,
    fn="countEqualRatioPairs", params=[("rects", "int[][]")], ret="int", cmp="exact",
    desc="<p>Each element <code>rects[i] = [w, h]</code> describes the width and height of a rectangle. Two rectangles are <em>interchangeable</em> when their width-to-height ratios are equal, that is <code>w<sub>i</sub> / h<sub>i</sub> == w<sub>j</sub> / h<sub>j</sub></code> as exact fractions.</p><p>Return the number of pairs <code>(i, j)</code> with <code>i &lt; j</code> whose rectangles are interchangeable.</p><p>For example, <code>[[4, 8], [3, 6], [10, 20], [15, 25]]</code> gives <code>3</code>: the first three rectangles all have ratio 1/2.</p>",
    constraints=["1 &le; rects.length &le; 4,000", "rects[i].length == 2", "1 &le; w, h &le; 100,000", "The answer fits in 32 bits"],
    hints=["Comparing the ratios of every two rectangles is O(n<sup>2</sup>). Is there a single value that identifies a ratio?",
           "Dividing floating point numbers can make equal ratios look different. Use an exact canonical form instead.",
           "Divide both sides by <code>gcd(w, h)</code> to get the reduced fraction <code>(w/g, h/g)</code>. Equal ratios have equal reduced pairs, so count identical pairs with a hash map of reduced fractions."],
    editorial=["Two fractions are equal exactly when they have the same reduced form, and the reduced form of <code>w / h</code> is <code>(w / g, h / g)</code> with <code>g = gcd(w, h)</code>. This gives a hashable key without any floating point error.",
               "Go through the rectangles, keep a map from key to the number of earlier rectangles with that key, and add that count to the answer before incrementing it. Time O(n log M) for the gcds, space O(n)."],
    time="O(n log M)", space="O(n)",
    solution='''from math import gcd

def countEqualRatioPairs(rects):
    seen = {}
    total = 0
    for w, h in rects:
        g = gcd(w, h)
        key = (w // g, h // g)
        s = seen.get(key, 0)
        total += s
        seen[key] = s + 1
    return total
''',
    tests=[[[[4, 8], [3, 6], [10, 20], [15, 25]]], [[[4, 5], [7, 8]]], [[[1, 1]]], [[[1, 1], [2, 2], [3, 3], [4, 4]]],
           [[[1, 2], [2, 1]]], [[[6, 4], [3, 2], [9, 6], [2, 3]]], [[[100000, 1], [99999, 1], [100000, 1]]],
           [[[100000, 100000], [1, 1], [99999, 99999]]], [[[2, 3], [4, 6], [6, 9], [8, 12], [3, 2]]]],
)
_r = rnd(7108)


def _mk_rects(r, n, bases, maxm):
    out = []
    for _ in range(n):
        a, b = r.choice(bases)
        m = r.randint(1, maxm // max(a, b))
        out.append([a * m, b * m])
    return out


_bases = [(a, b) for a in range(1, 8) for b in range(1, 8) if gcd(a, b) == 1]
p["tests"].append([_mk_rects(_r, 3500, _bases, 100000)])
p["tests"].append([_mk_rects(_r, 3000, [(1, 1), (1, 2), (2, 1)], 100000)])
p["tests"].append([[[_r.randint(1, 100000), _r.randint(1, 100000)] for _ in range(3000)]])


def b_rects(rects):
    return sum(1 for i in range(len(rects)) for j in range(i + 1, len(rects))
               if rects[i][0] * rects[j][1] == rects[j][0] * rects[i][1])


def g_rects(r):
    return [[[r.randint(1, 12), r.randint(1, 12)] for _ in range(r.randint(1, 10))]]


def v_rects(tests):
    for t in tests:
        rects = t["args"][0]
        assert 1 <= len(rects) <= 4000
        assert all(len(x) == 2 and 1 <= x[0] <= 100000 and 1 <= x[1] <= 100000 for x in rects)


CHECKS["count-equal-ratio-rectangles"] = (b_rects, g_rects, "exact")
VALIDATE["count-equal-ratio-rectangles"] = v_rects



p = add(
    id="least-distinct-after-k-removals", title="Fewest Distinct Values After K Removals", diff="Medium", topic=TOPIC,
    fn="minDistinctAfterRemovals", params=[("nums", "int[]"), ("k", "int")], ret="int", cmp="exact",
    desc="<p>You must remove <strong>exactly</strong> <code>k</code> elements from <code>nums</code> (you choose which ones). Return the smallest possible number of <em>distinct values</em> left in the array afterwards.</p><p>For example, <code>nums = [5, 5, 4]</code>, <code>k = 1</code> gives <code>1</code> (remove the 4), and <code>nums = [4, 3, 1, 1, 3, 3, 2]</code>, <code>k = 3</code> gives <code>2</code>: remove the 4, the 2 and one 1, leaving the values 1 and 3.</p>",
    constraints=["1 &le; nums.length &le; 10,000", "-2<sup>31</sup> &le; nums[i] &le; 2<sup>31</sup> - 1", "0 &le; k &le; nums.length"],
    hints=["A value disappears only if <em>all</em> of its copies are removed. Which values are cheapest to eliminate?",
           "The cost of eliminating a value is its frequency, so you should spend the removals on the values with the smallest frequencies first.",
           "Count frequencies, sort them ascending, and walk through them subtracting each frequency from <code>k</code> while <code>k</code> still covers it. The number of frequencies you could not fully remove is the answer."],
    editorial=["Removing part of a value's copies never reduces the distinct count, so every removal should go toward wiping out whole values. To wipe out as many values as possible with a budget of <code>k</code> removals, take the values in order of increasing frequency (an exchange argument: replacing a chosen value by a cheaper unchosen one never hurts).",
               "Build a frequency map, sort the frequencies, and eliminate values while the remaining budget is at least the next frequency. Any leftover budget is spent on arbitrary elements of the values that stay, which changes nothing. The answer is the number of distinct values minus the number eliminated. Time O(n log n), or O(n) with a counting sort of the frequencies."],
    time="O(n log n)", space="O(n)",
    solution='''def minDistinctAfterRemovals(nums, k):
    cnt = {}
    for x in nums:
        cnt[x] = cnt.get(x, 0) + 1
    freqs = sorted(cnt.values())
    gone = 0
    for f in freqs:
        if k >= f:
            k -= f
            gone += 1
        else:
            break
    return len(freqs) - gone
''',
    tests=[[[5, 5, 4], 1], [[4, 3, 1, 1, 3, 3, 2], 3], [[1], 0], [[1], 1], [[1, 2, 3], 0], [[1, 2, 3], 3],
           [[1, 1, 2, 2, 3, 3], 3], [[1, 1, 2, 2, 3, 3], 4], [[INT_MIN, INT_MAX, INT_MAX], 1],
           [[7, 7, 7, 7, 8], 4], [[2, 2, 3, 3, 3, 4, 4, 4, 4], 5]],
)
_r = rnd(7112)
p["tests"].append([[_r.randint(-10 ** 9, 10 ** 9) for _ in range(3000)], 1500])
p["tests"].append([[int(_r.random() ** 2 * 400) for _ in range(5000)], 2500])
p["tests"].append([[int(_r.random() ** 3 * 100) for _ in range(5000)], 4000])


def b_distinct_rem(nums, k):
    from itertools import combinations
    n = len(nums)
    best = n
    for rem in combinations(range(n), k):
        rs = set(rem)
        best = min(best, len({nums[i] for i in range(n) if i not in rs}))
    return best


def g_distinct_rem(r):
    a = gen_arr(r, 0, 4, 1, 9)
    return [a, r.randint(0, len(a))]


def v_distinct_rem(tests):
    for t in tests:
        nums, k = t["args"]
        assert 1 <= len(nums) <= 10000 and 0 <= k <= len(nums)
        assert all(INT_MIN <= x <= INT_MAX for x in nums)


CHECKS["least-distinct-after-k-removals"] = (b_distinct_rem, g_distinct_rem, "exact")
VALIDATE["least-distinct-after-k-removals"] = v_distinct_rem

p = add(
    id="min-rounds-to-finish-tasks", title="Minimum Rounds to Finish Tasks", diff="Medium", topic=TOPIC,
    fn="minimumRounds", params=[("tasks", "int[]")], ret="int", cmp="exact",
    desc="<p><code>tasks[i]</code> is the difficulty level of the <code>i</code>-th task. In one round you may complete either <strong>2</strong> or <strong>3</strong> tasks, and all tasks completed in the same round must have the same difficulty.</p><p>Return the minimum number of rounds needed to complete every task, or <code>-1</code> if it is impossible.</p><p>For example, <code>[2, 2, 3, 3, 2, 4, 4, 4, 4, 4]</code> gives <code>4</code>: the three 2s in one round, the two 3s in one round, and the five 4s in two rounds (3 + 2). The array <code>[2, 3, 3]</code> gives <code>-1</code> because the single 2 can never be grouped.</p>",
    constraints=["1 &le; tasks.length &le; 10,000", "1 &le; tasks[i] &le; 10<sup>9</sup>"],
    hints=["Tasks of different difficulties never share a round, so the problem splits into independent groups, one per difficulty.",
           "For one group of size <code>c</code> you need the fewest numbers from {2, 3} that add up to <code>c</code>. When is that impossible?",
           "Only <code>c = 1</code> is impossible. Otherwise use as many 3s as possible: the answer is <code>ceil(c / 3)</code> rounds, because a remainder of 1 or 2 can be absorbed by turning one 3 into 2 + 2 or adding a single 2."],
    editorial=["Count how many tasks each difficulty has. A group of size 1 cannot be completed, so the answer is -1 if any count is 1. Every size <code>c &ge; 2</code> can be written as a sum of 2s and 3s: for <code>c mod 3 = 0</code> use all 3s, for <code>c mod 3 = 2</code> use 3s plus one 2, and for <code>c mod 3 = 1</code> (with <code>c &ge; 4</code>) replace one 3 by two 2s, for example 7 = 3 + 2 + 2.",
               "Since every round handles at most 3 tasks, <code>ceil(c / 3)</code> is also a lower bound, and the construction above reaches it in each case. Summing <code>(c + 2) // 3</code> over all groups gives the answer in O(n) time with a frequency map."],
    time="O(n)", space="O(n)",
    solution='''def minimumRounds(tasks):
    cnt = {}
    for t in tasks:
        cnt[t] = cnt.get(t, 0) + 1
    rounds = 0
    for c in cnt.values():
        if c == 1:
            return -1
        rounds += (c + 2) // 3
    return rounds
''',
    tests=[[[2, 2, 3, 3, 2, 4, 4, 4, 4, 4]], [[2, 3, 3]], [[5]], [[5, 5]], [[5, 5, 5]], [[5, 5, 5, 5]],
           [[1, 1, 1, 1, 1, 1, 1]], [[1, 1, 2, 2, 3, 3, 3, 3]], [[10 ** 9] * 10], [[9, 9, 9, 9, 9, 8]],
           [[6, 6, 7, 7, 7, 7, 7, 7, 7]]],
)
_r = rnd(7113)
_a = []
for _v in range(1, 800):
    _a += [_v] * _r.randint(2, 15)
_r.shuffle(_a)
p["tests"].append([_a[:6000]])
_a = [_r.randint(1, 10 ** 9) for _ in range(4000)]
p["tests"].append([_a])
p["tests"].append([[3] * 9999 + [4] * 1])


def b_rounds(tasks):
    total = 0
    for v in set(tasks):
        c = tasks.count(v)
        dp = [0] + [10 ** 9] * c
        for i in range(2, c + 1):
            dp[i] = min(dp[i - 2], dp[i - 3] if i >= 3 else 10 ** 9) + 1
        if dp[c] >= 10 ** 9:
            return -1
        total += dp[c]
    return total


def g_rounds(r):
    a = []
    for v in range(r.randint(1, 4)):
        a += [v] * r.randint(1, 9)
    r.shuffle(a)
    return [a]


def v_rounds(tests):
    for t in tests:
        tasks = t["args"][0]
        assert 1 <= len(tasks) <= 10000 and all(1 <= x <= 10 ** 9 for x in tasks)
    assert any(t["expected"] == -1 for t in tests) and any(t["expected"] > 0 for t in tests)


CHECKS["min-rounds-to-finish-tasks"] = (b_rounds, g_rounds, "exact")
VALIDATE["min-rounds-to-finish-tasks"] = v_rounds

p = add(
    id="equal-row-column-pairs", title="Equal Row and Column Pairs", diff="Medium", topic=TOPIC,
    fn="equalRowColumnPairs", params=[("grid", "int[][]")], ret="int", cmp="exact",
    desc="<p>Given an <code>n x n</code> integer matrix <code>grid</code>, return the number of pairs <code>(r, c)</code> (0-indexed, both from <code>0</code> to <code>n - 1</code>) such that row <code>r</code> and column <code>c</code> contain the same numbers in the same order.</p><p>For example, <code>[[3, 2, 1], [1, 7, 6], [2, 7, 7]]</code> gives <code>1</code>: row 2 is <code>[2, 7, 7]</code> and column 1 is also <code>[2, 7, 7]</code>.</p>",
    constraints=["n == grid.length == grid[i].length", "1 &le; n &le; 60", "1 &le; grid[i][j] &le; 100,000"],
    hints=["Comparing every row against every column element by element costs O(n<sup>3</sup>). Can a whole row be turned into something you can look up quickly?",
           "A row is a sequence; as a tuple (or a string with separators) it can be used as a hash map key.",
           "Count how often each row occurs in a map keyed by the row's tuple, then for every column build its tuple and add the number of rows equal to it."],
    editorial=["Turn every row into a hashable key (a tuple of its values) and store how many times each key occurs. Then build each column, in order from top to bottom, as a tuple and add the stored count for that key. Duplicated rows are all counted, because each of them forms a valid pair with the matching column.",
               "Building the keys costs O(n<sup>2</sup>) for rows and for columns, and hashing a tuple of length n costs O(n) per lookup, so the total is O(n<sup>2</sup>) time and O(n<sup>2</sup>) space. Do not compare sorted rows: the order of the values must match."],
    time="O(n^2)", space="O(n^2)",
    solution='''def equalRowColumnPairs(grid):
    n = len(grid)
    rows = {}
    for row in grid:
        key = tuple(row)
        rows[key] = rows.get(key, 0) + 1
    total = 0
    for c in range(n):
        key = tuple(grid[r][c] for r in range(n))
        total += rows.get(key, 0)
    return total
''',
    tests=[[[[3, 2, 1], [1, 7, 6], [2, 7, 7]]], [[[3, 1, 2, 2], [1, 4, 4, 5], [2, 4, 2, 2], [2, 4, 2, 2]]], [[[5]]],
           [[[1, 2], [3, 4]]], [[[1, 2], [2, 1]]], [[[7, 7], [7, 7]]], [[[1, 2, 3], [4, 5, 6], [7, 8, 9]]],
           [[[1, 4, 7], [2, 5, 8], [3, 6, 9]]], [[[100000, 1], [1, 100000]]], [[[1, 1, 1], [1, 1, 1], [1, 1, 1]]]],
)
_r = rnd(7114)
p["tests"].append([[[(i * j) % 7 + 1 for j in range(60)] for i in range(60)]])
p["tests"].append([[[1] * 60 for _ in range(60)]])
_m = [[0] * 50 for _ in range(50)]
for _i in range(50):
    for _j in range(_i, 50):
        _m[_i][_j] = _m[_j][_i] = _r.randint(1, 3)
p["tests"].append([_m])
p["tests"].append([[[_r.randint(1, 2) for _ in range(40)] for _ in range(40)]])


def b_rowcol(grid):
    n = len(grid)
    return sum(1 for r in range(n) for c in range(n) if all(grid[r][k] == grid[k][c] for k in range(n)))


def g_rowcol(r):
    n = r.randint(1, 5)
    return [[[r.randint(1, 2) for _ in range(n)] for _ in range(n)]]


def v_rowcol(tests):
    for t in tests:
        g = t["args"][0]
        n = len(g)
        assert 1 <= n <= 60 and all(len(row) == n and all(1 <= x <= 100000 for x in row) for row in g)


CHECKS["equal-row-column-pairs"] = (b_rowcol, g_rowcol, "exact")
VALIDATE["equal-row-column-pairs"] = v_rowcol

p = add(
    id="count-digit-permutation-pairs", title="Count Digit-Permutation Pairs", diff="Medium", topic=TOPIC,
    fn="countDigitPermutationPairs", params=[("nums", "int[]")], ret="int", cmp="exact",
    desc="<p>Two positive integers are <em>digit twins</em> when the decimal digits of one can be rearranged to give the other, using exactly the same digits with the same multiplicities (so <code>123</code> and <code>321</code> are twins, but <code>12</code> and <code>102</code> or <code>112</code> and <code>122</code> are not).</p><p>Return the number of pairs of indices <code>(i, j)</code> with <code>i &lt; j</code> for which <code>nums[i]</code> and <code>nums[j]</code> are digit twins.</p><p>For example, <code>[123, 321, 213, 456, 654, 12]</code> gives <code>4</code>: three pairs among 123, 321, 213 and one pair (456, 654).</p>",
    constraints=["1 &le; nums.length &le; 10,000", "1 &le; nums[i] &le; 10<sup>9</sup>", "The answer is at most 49,995,000"],
    hints=["Comparing every pair of numbers digit by digit is too slow for 10,000 elements. Is there a form that is identical for all rearrangements of a number?",
           "Sort the digits of each number (or count how many times each digit 0-9 occurs). Two numbers are twins exactly when this canonical form is equal.",
           "Use the sorted digit string (or the 10-count tuple) as a hash map key. For each element add the number of earlier elements with the same key to the answer, then record the current element."],
    editorial=["Rearranging digits does not change the multiset of digits, and the multiset determines the numbers it can form. So the sorted digit string is a complete signature: two numbers are twins if and only if their signatures match. Leading zeros are not an issue, because a zero digit is part of the signature and a number never begins with it.",
               "Compute the signature for each number in O(d) or O(d log d) with d &le; 10 digits, then count equal-signature pairs with a hash map exactly as in 'count identical pairs'. A group of size <code>c</code> contributes <code>c(c-1)/2</code>. Total time O(n d log d), space O(n)."],
    time="O(n * d log d)", space="O(n)",
    solution='''def countDigitPermutationPairs(nums):
    seen = {}
    total = 0
    for x in nums:
        key = ''.join(sorted(str(x)))
        s = seen.get(key, 0)
        total += s
        seen[key] = s + 1
    return total
''',
    tests=[[[123, 321, 213, 456, 654, 12]], [[5]], [[12, 102]], [[112, 122, 211]], [[100, 10, 1]], [[100, 10, 1, 1, 100]],
           [[1000000000, 1000000000, 100000000]], [[123456789, 987654321, 918273645, 123456798]],
           [[11, 11, 11]], [[121, 112, 211, 122]], [[90, 9, 900, 909, 990]]],
)
_r = rnd(7115)


def _twin_pool(r, groups, per, hi_digits):
    pool = []
    for _ in range(groups):
        d = [r.randint(0, 9) for _ in range(r.randint(1, hi_digits))]
        d[0] = r.randint(1, 9)
        for _ in range(per):
            e = d[:]
            r.shuffle(e)
            if e[0] == 0:
                e.sort(reverse=True)
            pool.append(int(''.join(map(str, e))))
    return pool


_a = _twin_pool(_r, 400, 12, 9); _r.shuffle(_a)
p["tests"].append([_a])
_a = _twin_pool(_r, 30, 100, 4) + [_r.randint(1, 10 ** 9) for _ in range(1500)]; _r.shuffle(_a)
p["tests"].append([_a])
p["tests"].append([[_r.randint(1, 999) for _ in range(5000)]])


def b_twins(nums):
    sd = [sorted(str(x)) for x in nums]
    return sum(1 for i in range(len(nums)) for j in range(i + 1, len(nums)) if sd[i] == sd[j])


def v_twins(tests):
    for t in tests:
        nums = t["args"][0]
        assert 1 <= len(nums) <= 10000 and all(1 <= x <= 10 ** 9 for x in nums)
        assert t["expected"] <= 49995000


CHECKS["count-digit-permutation-pairs"] = (b_twins, lambda r: [gen_arr(r, 1, 130, 1, 12)], "exact")
VALIDATE["count-digit-permutation-pairs"] = v_twins

# ---------------------------------------------------------------- HARD

p = add(
    id="sliding-window-mode-values", title="Sliding Window Mode", diff="Hard", topic=TOPIC, tier="extra",
    fn="windowModes", params=[("nums", "int[]"), ("k", "int")], ret="int[]", cmp="exact",
    desc="<p>For every window of <code>k</code> consecutive elements of <code>nums</code>, find its <em>mode</em>: the value that occurs most often inside the window. If several values tie for the highest count, the mode is the <strong>smallest</strong> of them. Return the array of modes, one per window, from left to right (it has <code>nums.length - k + 1</code> entries).</p><p>For example, <code>nums = [1, 2, 2, 3, 3, 1]</code> and <code>k = 3</code> gives <code>[2, 2, 3, 3]</code>: the windows are <code>[1,2,2]</code>, <code>[2,2,3]</code>, <code>[2,3,3]</code> and <code>[3,3,1]</code>.</p>",
    constraints=["1 &le; k &le; nums.length &le; 10,000", "-2<sup>31</sup> &le; nums[i] &le; 2<sup>31</sup> - 1"],
    hints=["Recounting every window costs O(n k). When the window slides, only two values change their frequency by one.",
           "Keep a hash map of frequencies for the current window. The remaining difficulty is getting the best (highest count, then smallest value) entry quickly after every change.",
           "Use a min-heap of pairs <code>(-count, value)</code>. Whenever a value's count changes push its new pair; when you read the top, discard it if its count no longer matches the map (lazy deletion). Each push is discarded at most once."],
    editorial=["Maintain <code>freq[value]</code> for the window: add the entering element, decrement the leaving element (deleting the key at zero). After every change to a value push <code>(-freq, value)</code> on a heap, so the heap always holds a correct entry for every value currently in the window, plus some stale ones.",
               "The heap order is exactly 'higher count first, then smaller value'. To read the window's mode, pop while the top pair is stale, that is, while <code>freq.get(value) != -count</code>; the first valid top is the answer. Stale entries are removed once each, so there are O(n) pushes and pops overall: O(n log n) time and O(n) space. Alternative designs use a sorted container ordered by (count, value) with the same complexity."],
    time="O(n log n)", space="O(n)",
    solution='''import heapq

def windowModes(nums, k):
    freq = {}
    heap = []
    out = []
    for i, x in enumerate(nums):
        f = freq.get(x, 0) + 1
        freq[x] = f
        heapq.heappush(heap, (-f, x))
        if i >= k:
            y = nums[i - k]
            g = freq[y] - 1
            if g:
                freq[y] = g
                heapq.heappush(heap, (-g, y))
            else:
                del freq[y]
        if i >= k - 1:
            while freq.get(heap[0][1], 0) != -heap[0][0]:
                heapq.heappop(heap)
            out.append(heap[0][1])
    return out
''',
    tests=[[[1, 2, 2, 3, 3, 1], 3], [[4, 4, 5, 5], 4], [[9], 1], [[3, 1, 2], 1], [[3, 1, 2], 2], [[3, 1, 2], 3],
           [[2, 2, 2, 2], 2], [[1, 1, 2, 2, 1, 1, 2, 2], 4], [[INT_MIN, INT_MAX, INT_MAX, INT_MIN, INT_MIN], 3],
           [[-1, -1, 5, 5, -1, 5, 5], 5], [[7, 8, 7, 8, 7, 8, 8], 6]],
)
_r = rnd(7116)
p["tests"].append([[_r.randint(-5, 5) for _ in range(3000)], 40])
p["tests"].append([[_r.randint(-10 ** 9, 10 ** 9) if _r.random() < 0.5 else _r.randint(0, 3) for _ in range(3000)], 700])
p["tests"].append([[int(_r.random() ** 2 * 50) for _ in range(3000)], 3000])


def b_wmode(nums, k):
    out = []
    for i in range(len(nums) - k + 1):
        w = nums[i:i + k]
        out.append(min(w, key=lambda v: (-w.count(v), v)))
    return out


def g_wmode(r):
    a = gen_arr(r, -3, 3, 1, 14)
    return [a, r.randint(1, len(a))]


def v_wmode(tests):
    for t in tests:
        nums, k = t["args"]
        assert 1 <= k <= len(nums) <= 10000 and all(INT_MIN <= x <= INT_MAX for x in nums)


CHECKS["sliding-window-mode-values"] = (b_wmode, g_wmode, "exact")
VALIDATE["sliding-window-mode-values"] = v_wmode

p = add(
    id="range-majority-queries", title="Range Majority Queries", diff="Hard", topic=TOPIC, tier="extra",
    fn="rangeMajority", params=[("nums", "int[]"), ("queries", "int[][]")], ret="int[]", cmp="exact",
    desc="<p>You are given an array <code>nums</code> and a list of queries. Each query is <code>[l, r, t]</code> and asks: is there a value that occurs <strong>at least</strong> <code>t</code> times in the subarray <code>nums[l..r]</code> (both ends included)? Every query satisfies <code>2 * t &gt; r - l + 1</code>, so such a value, if it exists, is unique (it is a strict majority of the subarray).</p><p>Return an array with one answer per query: the value, or <code>-1</code> if no value occurs at least <code>t</code> times.</p><p>For example, <code>nums = [1, 1, 2, 2, 1, 1]</code> with queries <code>[[0, 5, 4], [0, 3, 3], [2, 3, 2]]</code> gives <code>[1, -1, 2]</code>.</p>",
    constraints=["1 &le; nums.length &le; 10,000", "1 &le; nums[i] &le; 10<sup>9</sup>", "1 &le; queries.length &le; 10,000", "0 &le; l &le; r &lt; nums.length, and (r - l + 1) / 2 &lt; t &le; r - l + 1"],
    hints=["Counting inside every query range takes O(n) per query. The guarantee <code>2t &gt; length</code> means any answer is a strict majority of the range, which is a very strong property.",
           "If a value is a strict majority of a range, the Boyer-Moore voting candidate of that range is that value. Voting results of two adjacent pieces can be merged, so they can be precomputed in a segment tree.",
           "Store (candidate, surplus) in each segment tree node and merge two nodes: equal candidates add surplus, otherwise the larger surplus wins with the difference. Then verify the candidate of the query range with binary search on the sorted list of positions of that value."],
    editorial=["Voting gives only a <em>candidate</em>: if a majority exists it is the candidate, but the candidate may be wrong when there is none. So the plan has two parts. First find the candidate of <code>nums[l..r]</code> in O(log n) using a segment tree whose nodes hold Boyer-Moore pairs (value, surplus); two pairs merge by adding surplus when the values match and otherwise keeping the pair with the larger surplus, reduced by the smaller one. The merge is associative enough for majority detection, because cancelling two different values never removes a strict majority.",
               "Second, verify the candidate. For every value store the sorted list of its positions; the occurrences inside <code>[l, r]</code> equal <code>bisect_right(pos, r) - bisect_left(pos, l)</code>. If that is at least <code>t</code> return the candidate, else -1. Total time is O((n + q) log n), space O(n). A randomised alternative samples a few random positions in the range and checks each with the same binary search."],
    time="O((n + q) log n)", space="O(n)",
    solution='''from bisect import bisect_left, bisect_right

def rangeMajority(nums, queries):
    n = len(nums)
    size = 1
    while size < n:
        size *= 2
    val = [0] * (2 * size)
    cnt = [0] * (2 * size)
    pos = {}
    for i, x in enumerate(nums):
        val[size + i] = x
        cnt[size + i] = 1
        pos.setdefault(x, []).append(i)

    def merge(v1, c1, v2, c2):
        if v1 == v2:
            return v1, c1 + c2
        if c1 >= c2:
            return v1, c1 - c2
        return v2, c2 - c1

    for i in range(size - 1, 0, -1):
        val[i], cnt[i] = merge(val[2 * i], cnt[2 * i], val[2 * i + 1], cnt[2 * i + 1])
    out = []
    for l, r, t in queries:
        lo, hi = l + size, r + size + 1
        v, c = 0, 0
        while lo < hi:
            if lo & 1:
                v, c = merge(v, c, val[lo], cnt[lo])
                lo += 1
            if hi & 1:
                hi -= 1
                v, c = merge(v, c, val[hi], cnt[hi])
            lo >>= 1
            hi >>= 1
        if c > 0 and bisect_right(pos[v], r) - bisect_left(pos[v], l) >= t:
            out.append(v)
        else:
            out.append(-1)
    return out
''',
    tests=[[[1, 1, 2, 2, 1, 1], [[0, 5, 4], [0, 3, 3], [2, 3, 2]]], [[7], [[0, 0, 1]]], [[5, 6], [[0, 1, 2], [0, 0, 1], [1, 1, 1]]],
           [[3, 3, 3, 3], [[0, 3, 3], [1, 2, 2], [0, 3, 4]]], [[1, 2, 3, 4, 5], [[0, 4, 3], [1, 3, 2], [2, 2, 1]]],
           [[2, 1, 2, 1, 2, 1, 2], [[0, 6, 4], [0, 5, 4], [1, 5, 3], [0, 6, 7]]],
           [[10 ** 9, 1, 10 ** 9, 10 ** 9, 1], [[0, 4, 3], [1, 4, 3], [0, 1, 2], [2, 4, 2]]],
           [[4, 4, 5, 5, 5, 4, 4, 4], [[0, 7, 5], [2, 4, 3], [0, 4, 3], [3, 7, 3], [5, 7, 2]]]],
)
_r = rnd(7117)


def _mk_rm(r, n, q, probs, vals):
    a = [r.choices(vals, probs)[0] for _ in range(n)]
    qs = []
    for _ in range(q):
        l = r.randint(0, n - 1)
        rr = min(n - 1, l + int(r.random() ** 2 * 300))
        ln = rr - l + 1
        t = r.randint(ln // 2 + 1, ln)
        if r.random() < 0.6:
            t = ln // 2 + 1
        qs.append([l, rr, t])
    return a, qs


p["tests"].append(list(_mk_rm(_r, 4000, 2500, [60, 30, 10], [11, 22, 10 ** 9])))
p["tests"].append(list(_mk_rm(_r, 4000, 2500, [1, 1, 1, 1, 1, 1], [1, 2, 3, 4, 5, 6])))
_a = [(5 if i % 2 == 0 else 9) for i in range(3001)]
p["tests"].append([_a, [[0, 3000, 1501], [1, 2999, 1500], [0, 2999, 1501], [5, 5, 1], [0, 1, 2]]])


def b_rangemaj(nums, queries):
    out = []
    for l, r, t in queries:
        c = Counter(nums[l:r + 1])
        v, f = c.most_common(1)[0]
        out.append(v if f >= t else -1)
    return out


def g_rangemaj(r):
    n = r.randint(1, 12)
    a = [r.randint(1, 3) for _ in range(n)]
    qs = []
    for _ in range(r.randint(1, 8)):
        l = r.randint(0, n - 1)
        rr = r.randint(l, n - 1)
        ln = rr - l + 1
        qs.append([l, rr, r.randint(ln // 2 + 1, ln)])
    return [a, qs]


def v_rangemaj(tests):
    for t in tests:
        nums, qs = t["args"]
        assert 1 <= len(nums) <= 10000 and all(1 <= x <= 10 ** 9 for x in nums)
        assert 1 <= len(qs) <= 10000
        for l, r, th in qs:
            assert 0 <= l <= r < len(nums) and 2 * th > r - l + 1 and th <= r - l + 1
    assert any(-1 in t["expected"] for t in tests) and any(max(t["expected"]) > 0 for t in tests)


CHECKS["range-majority-queries"] = (b_rangemaj, g_rangemaj, "exact")
VALIDATE["range-majority-queries"] = v_rangemaj
