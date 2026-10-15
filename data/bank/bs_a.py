"""Problems: binary search on boundaries (lower/upper bound, first/last, closest, counts in a range). See data/lib.py for the registry."""
from bisect import bisect_left, bisect_right, insort

from lib import add, rnd, CHECKS, VALIDATE, gen_arr  # noqa: F401

INT_MIN, INT_MAX = -(2 ** 31), 2 ** 31 - 1
T = "Binary Search"


def _sorted(r, n, lo, hi):
    return sorted(r.randint(lo, hi) for _ in range(n))


def _is_sorted(a):
    return all(a[i] <= a[i + 1] for i in range(len(a) - 1))


# ---------------------------------------------------------------- EASY

p = add(
    id="floor-and-ceiling-indices", title="Floor and Ceiling Indices", diff="Easy", topic=T,
    fn="floorCeilIndices", params=[("nums", "int[]"), ("x", "int")], ret="int[]", cmp="exact",
    desc="<p>The array <code>nums</code> is sorted in non-decreasing order and may contain duplicates. For a query value <code>x</code>, find two indices:</p><ul><li><strong>floor</strong>: the <em>largest</em> index <code>i</code> with <code>nums[i] &le; x</code>, or <code>-1</code> if no element is that small;</li><li><strong>ceiling</strong>: the <em>smallest</em> index <code>j</code> with <code>nums[j] &ge; x</code>, or <code>-1</code> if no element is that large.</li></ul><p>Return <code>[floor, ceiling]</code>. If <code>x</code> occurs in the array, the two indices are the last and the first position of <code>x</code>.</p>",
    constraints=["0 &le; nums.length &le; 8,000", "-2<sup>31</sup> &le; nums[i], x &le; 2<sup>31</sup> - 1", "nums is sorted in non-decreasing order"],
    hints=["A linear scan answers the query. The sorted order lets you discard half of the array with each comparison.",
           "Both answers are boundaries. The ceiling index is the first position where <code>nums[j] &ge; x</code>; the floor index is one step before the first position where <code>nums[i] &gt; x</code>.",
           "Write one routine that returns the first index whose value satisfies a monotone test (false...false true...true). Call it with the test <code>v &ge; x</code> for the ceiling and with <code>v &gt; x</code> for the floor (then subtract one). Map 'index equals n' to <code>-1</code> for the ceiling and 'index equals 0' to <code>-1</code> for the floor."],
    editorial=["Both indices sit next to a boundary in the sorted array. Let <code>lo</code> be the first index with <code>nums[lo] &ge; x</code> (the lower bound, or <code>n</code> if every element is smaller) and <code>hi</code> the first index with <code>nums[hi] &gt; x</code> (the upper bound, or <code>n</code>). The ceiling is <code>lo</code> when <code>lo &lt; n</code>, otherwise <code>-1</code>. The floor is <code>hi - 1</code>, which is <code>-1</code> exactly when <code>hi = 0</code>.",
               "Each bound is found with a half-open binary search on <code>[0, n)</code>: keep <code>lo</code> as the left end and <code>hi</code> as the right end, test the middle element, and move <code>lo</code> past it when the test is still false, otherwise set <code>hi</code> to it. This returns the first index where the predicate turns true. The total cost is two O(log n) searches."],
    time="O(log n)", space="O(1)",
    solution='''def floorCeilIndices(nums, x):
    n = len(nums)

    def first_true(pred):
        lo, hi = 0, n
        while lo < hi:
            mid = (lo + hi) // 2
            if pred(nums[mid]):
                hi = mid
            else:
                lo = mid + 1
        return lo

    ceil_i = first_true(lambda v: v >= x)
    upper = first_true(lambda v: v > x)
    return [upper - 1, ceil_i if ceil_i < n else -1]
''',
    tests=[[[1, 2, 4, 4, 4, 7], 4], [[1, 2, 4, 4, 4, 7], 5], [[1, 2, 4, 4, 4, 7], 0], [[1, 2, 4, 4, 4, 7], 8], [[], 3],
           [[5], 5], [[5], 4], [[5], 6], [[2, 2, 2, 2], 2], [[-9, -3, 0, 6], -3], [[-9, -3, 0, 6], 1],
           [[INT_MIN, 0, INT_MAX], INT_MAX], [[INT_MIN, 0, INT_MAX], INT_MIN + 1], [[INT_MIN, INT_MIN], INT_MIN]],
)
_r = rnd(8101)
_a = _sorted(_r, 7000, -100000, 100000)
p["tests"].append([_a, _a[3456]])
p["tests"].append([_a, 100001])
p["tests"].append([_sorted(_r, 6000, -50, 50), 0])
p["tests"].append([[3] * 8000, 3])


def b_floorceil(nums, x):
    fl = -1
    ce = -1
    for i, v in enumerate(nums):
        if v <= x:
            fl = i
    for j in range(len(nums) - 1, -1, -1):
        if nums[j] >= x:
            ce = j
    return [fl, ce]


def v_floorceil(tests):
    for t in tests:
        nums, x = t["args"]
        assert len(nums) <= 8000 and _is_sorted(nums)
        assert all(INT_MIN <= v <= INT_MAX for v in nums + [x])


CHECKS["floor-and-ceiling-indices"] = (b_floorceil, lambda r: [_sorted(r, r.randint(0, 10), -5, 5), r.randint(-7, 7)], "exact")
VALIDATE["floor-and-ceiling-indices"] = v_floorceil

p = add(
    id="dominant-sign-count", title="Dominant Sign Count", diff="Easy", topic=T,
    fn="signCount", params=[("nums", "int[]")], ret="int", cmp="exact",
    desc="<p>The array <code>nums</code> is sorted in non-decreasing order. Count the negative numbers and count the positive numbers (zero is neither), and return the larger of the two counts.</p><p>An O(log n) solution exists; scanning the whole array is not required.</p>",
    constraints=["1 &le; nums.length &le; 8,000", "-2<sup>31</sup> &le; nums[i] &le; 2<sup>31</sup> - 1", "nums is sorted in non-decreasing order"],
    hints=["Counting with a loop is O(n). The sorted order says all negatives come first, then zeros, then positives.",
           "The number of negatives equals the index of the first element that is <code>&ge; 0</code>.",
           "The number of positives equals <code>n</code> minus the index of the first element that is <code>&gt; 0</code>. Both indices come from a lower-bound style binary search."],
    editorial=["Because the array is sorted, the negatives form a prefix, the zeros a middle block, and the positives a suffix. Let <code>a</code> be the first index with <code>nums[a] &ge; 0</code>: there are exactly <code>a</code> negatives. Let <code>b</code> be the first index with <code>nums[b] &gt; 0</code>: there are <code>n - b</code> positives.",
               "Each of <code>a</code> and <code>b</code> is a standard boundary search on a monotone condition, so the answer <code>max(a, n - b)</code> costs O(log n). Many zeros do not matter, because the two boundary searches skip the whole zero block."],
    time="O(log n)", space="O(1)",
    solution='''def signCount(nums):
    n = len(nums)

    def first_index(pred):
        lo, hi = 0, n
        while lo < hi:
            mid = (lo + hi) // 2
            if pred(nums[mid]):
                hi = mid
            else:
                lo = mid + 1
        return lo

    negatives = first_index(lambda v: v >= 0)
    positives = n - first_index(lambda v: v > 0)
    return max(negatives, positives)
''',
    tests=[[[-2, -1, -1, 1, 2, 3]], [[-3, -2, -1, 0, 0]], [[0, 0, 0]], [[5]], [[-5]], [[0]], [[-4, 0, 0, 0, 7]],
           [[-1, 0, 1]], [[-2, -2, 0, 0, 0, 0, 0, 3]], [[INT_MIN, -1, 0, INT_MAX]], [[INT_MIN, INT_MIN, 1]]],
)
_r = rnd(8102)
p["tests"].append([_sorted(_r, 8000, -10 ** 9, 10 ** 9)])
p["tests"].append([sorted([0] * 3000 + [_r.randint(-9, -1) for _ in range(2500)] + [_r.randint(1, 9) for _ in range(2400)])])
p["tests"].append([[0] * 8000])


def b_sign(nums):
    return max(sum(1 for v in nums if v < 0), sum(1 for v in nums if v > 0))


def v_sign(tests):
    for t in tests:
        nums = t["args"][0]
        assert 1 <= len(nums) <= 8000 and _is_sorted(nums)


CHECKS["dominant-sign-count"] = (b_sign, lambda r: [_sorted(r, r.randint(1, 10), -4, 4)], "exact")
VALIDATE["dominant-sign-count"] = v_sign

p = add(
    id="closest-value-in-sorted-array", title="Closest Value in a Sorted Array", diff="Easy", topic=T,
    fn="closestValue", params=[("nums", "int[]"), ("target", "int")], ret="int", cmp="exact",
    desc="<p>Given a non-empty array <code>nums</code> sorted in non-decreasing order and an integer <code>target</code>, return the element of <code>nums</code> whose absolute difference from <code>target</code> is smallest.</p><p>If two different values are equally close, return the <em>smaller</em> one. The target does not have to appear in the array.</p>",
    constraints=["1 &le; nums.length &le; 8,000", "-2<sup>31</sup> &le; nums[i], target &le; 2<sup>31</sup> - 1", "nums is sorted in non-decreasing order"],
    hints=["Scanning every element and keeping the best difference works in O(n). Use the order to jump straight to the right area.",
           "The closest value is always one of the two neighbours of the place where <code>target</code> would be inserted: the element just before it and the element at it.",
           "Find the lower bound <code>i</code> (first index with <code>nums[i] &ge; target</code>). Candidates are <code>nums[i - 1]</code> (if <code>i &gt; 0</code>) and <code>nums[i]</code> (if <code>i &lt; n</code>). Compare the distances, preferring the left one on a tie."],
    editorial=["Let <code>i</code> be the lower bound of <code>target</code>. Every element left of <code>i</code> is smaller than the target and every element from <code>i</code> on is at least the target. Among the smaller ones, <code>nums[i - 1]</code> is the closest; among the others, <code>nums[i]</code> is the closest. So at most two candidates remain.",
               "If <code>i = 0</code> or <code>i = n</code> only one candidate exists. Otherwise compare <code>target - nums[i - 1]</code> with <code>nums[i] - target</code> and take the left value when its distance is less than or equal to the right one; that rule also implements the 'smaller value wins a tie' requirement. In languages with 32-bit integers, compute the differences in 64 bits."],
    time="O(log n)", space="O(1)",
    solution='''def closestValue(nums, target):
    lo, hi = 0, len(nums)
    while lo < hi:
        mid = (lo + hi) // 2
        if nums[mid] < target:
            lo = mid + 1
        else:
            hi = mid
    if lo == 0:
        return nums[0]
    if lo == len(nums):
        return nums[-1]
    left, right = nums[lo - 1], nums[lo]
    return left if target - left <= right - target else right
''',
    tests=[[[1, 4, 9, 15], 6], [[1, 4, 9, 15], 7], [[1, 4, 9, 15], 100], [[1, 4, 9, 15], -100], [[3], 3], [[3], -8],
           [[2, 2, 2], 2], [[2, 5, 5, 8], 5], [[-10, -4, 0, 6], -7], [[-10, -4, 0, 6], 3],
           [[INT_MIN, INT_MAX], 0], [[INT_MIN, INT_MAX], -1], [[INT_MIN, INT_MAX], INT_MIN + 1]],
)
_r = rnd(8103)
_a = _sorted(_r, 5000, -10 ** 8, 10 ** 8)
p["tests"].append([_a, 12345678])
p["tests"].append([_a, _a[3000] + 1])
p["tests"].append([_sorted(_r, 5000, -300, 300), 0])


def b_closest(nums, target):
    return min(nums, key=lambda v: (abs(v - target), v))


def v_closest(tests):
    for t in tests:
        nums, target = t["args"]
        assert 1 <= len(nums) <= 8000 and _is_sorted(nums)
        assert all(INT_MIN <= v <= INT_MAX for v in nums + [target])


CHECKS["closest-value-in-sorted-array"] = (b_closest, lambda r: [_sorted(r, r.randint(1, 8), -6, 6), r.randint(-9, 9)], "exact")
VALIDATE["closest-value-in-sorted-array"] = v_closest

# ---------------------------------------------------------------- MEDIUM

p = add(
    id="successful-spell-pairs", title="Successful Spell Pairs", diff="Medium", topic=T,
    fn="successfulPairs", params=[("spells", "int[]"), ("potions", "int[]"), ("success", "int")], ret="int[]", cmp="exact",
    desc="<p>A spell with strength <code>s</code> and a potion with strength <code>p</code> form a <em>successful pair</em> when <code>s * p &ge; success</code>.</p><p>For every spell <code>spells[i]</code>, count the potions (any element of <code>potions</code>) that make a successful pair with it. Return the counts as an array in the same order as <code>spells</code>. The arrays are not sorted, and the same potion can be paired with many spells.</p>",
    constraints=["1 &le; spells.length, potions.length &le; 3,000", "1 &le; spells[i], potions[j] &le; 100,000", "1 &le; success &le; 2<sup>31</sup> - 1"],
    hints=["Testing every spell against every potion is O(n * m). Preprocess one of the arrays so each spell needs only O(log m).",
           "Sort <code>potions</code>. For a fixed spell <code>s</code>, the condition <code>s * p &ge; success</code> is true for all large potions and false for all small ones.",
           "The smallest potion that works is at least <code>ceil(success / s)</code>. Find its position with a lower bound; the answer is the number of potions from that position to the end."],
    editorial=["Sort the potions once. For a spell of strength <code>s</code>, a potion <code>p</code> is successful exactly when <code>p &ge; ceil(success / s)</code>, so the successful potions are a suffix of the sorted array. A lower-bound search for <code>need = ceil(success / s)</code> gives the index where that suffix begins, and the count is <code>m - index</code>.",
               "Computing the threshold with integer arithmetic, <code>(success + s - 1) // s</code>, avoids floating-point trouble. The total cost is O(m log m) for the sort plus O(n log m) for the searches. Sorting the spells and using two pointers is an alternative with the same main cost."],
    time="O((n + m) log m)", space="O(m)",
    solution='''from bisect import bisect_left

def successfulPairs(spells, potions, success):
    pots = sorted(potions)
    m = len(pots)
    out = []
    for s in spells:
        need = (success + s - 1) // s
        out.append(m - bisect_left(pots, need))
    return out
''',
    tests=[[[5, 1, 3], [1, 2, 3, 4, 5], 7], [[3, 1, 2], [8, 5, 8], 16], [[1], [1], 1], [[1], [1], 2],
           [[100000], [100000], 10 ** 9], [[100000], [100000], 10 ** 10 // 5], [[2, 2, 2], [1, 1, 1, 1], 3],
           [[4, 7, 1], [3, 3, 3], 12], [[1, 2, 3], [100000, 100000], INT_MAX], [[100000, 99999], [100000, 99999, 1], 9999900000 // 10]],
)
_r = rnd(8104)
p["tests"].append([[_r.randint(1, 100000) for _ in range(3000)], [_r.randint(1, 100000) for _ in range(3000)], 2 * 10 ** 9])
p["tests"].append([[_r.randint(1, 1000) for _ in range(3000)], [_r.randint(1, 1000) for _ in range(3000)], 500000])
p["tests"].append([[_r.randint(1, 30) for _ in range(3000)], [_r.randint(1, 30) for _ in range(3000)], 400])


def b_spells(spells, potions, success):
    return [sum(1 for q in potions if s * q >= success) for s in spells]


def g_spells(r):
    return [[r.randint(1, 8) for _ in range(r.randint(1, 8))], [r.randint(1, 8) for _ in range(r.randint(1, 8))], r.randint(1, 60)]


def v_spells(tests):
    for t in tests:
        sp, po, su = t["args"]
        assert 1 <= len(sp) <= 3000 and 1 <= len(po) <= 3000
        assert all(1 <= v <= 100000 for v in sp + po) and 1 <= su <= INT_MAX


CHECKS["successful-spell-pairs"] = (b_spells, g_spells, "exact")
VALIDATE["successful-spell-pairs"] = v_spells

p = add(
    id="time-travel-key-lookup", title="Time-Travel Key Lookup", diff="Medium", topic=T,
    fn="timeLookup", params=[("ops", "int[][]")], ret="int[]", cmp="exact",
    desc="<p>A store keeps a history of values for integer keys. It receives a list of operations <code>ops</code>; each operation is an array of four integers <code>[type, key, time, value]</code>:</p><ul><li><code>[1, key, time, value]</code> &ndash; <strong>set</strong>: record that at moment <code>time</code> the key <code>key</code> was given the value <code>value</code>.</li><li><code>[2, key, time, 0]</code> &ndash; <strong>get</strong>: report the value of <code>key</code> as it was at moment <code>time</code>, which is the value of the set operation on this key with the <em>largest</em> recorded time that is <code>&le; time</code>. If the key had no set at or before that moment, the answer is <code>-1</code>. (The last field of a get is always <code>0</code> and is ignored.)</li></ul><p>Process the operations in order and return the answers of all <strong>get</strong> operations, in order. For one key, set operations always come with strictly increasing times, but get times can be arbitrary and gets may ask about moments in the past.</p>",
    constraints=["1 &le; ops.length &le; 2,500, and at least one operation is a get", "type is 1 or 2; 0 &le; key &le; 10<sup>9</sup>", "0 &le; time &le; 10<sup>9</sup>; 0 &le; value &le; 10<sup>9</sup> for sets", "For each key, the times of its set operations are strictly increasing in the order they appear"],
    hints=["Remember, for each key, all its sets in order. A get is a search in that history.",
           "Because the set times of one key only grow, the history of each key is already sorted by time. Store two parallel lists per key: times and values.",
           "For a get, binary search the key's time list for the first time that is <em>greater than</em> the query time (an upper bound). The element just before it is the latest set at or before the query; if the upper bound is 0, answer <code>-1</code>."],
    editorial=["Keep a dictionary from key to two parallel lists, <code>times</code> and <code>values</code>. A set appends to both lists; the append keeps <code>times</code> sorted because the times of one key are strictly increasing. A get looks at the lists of its key (an unknown key means <code>-1</code>).",
               "The answer to a get is the value at the last position whose time is &le; the query time. That is <code>bisect_right(times, t) - 1</code>: the upper bound minus one. If that index is negative, no set happened yet and the answer is <code>-1</code>. Each set costs O(1) amortized and each get O(log k) where k is the number of sets of that key, so the total is O(q log q) for q operations."],
    time="O(q log q)", space="O(q)",
    solution='''from bisect import bisect_right

def timeLookup(ops):
    hist = {}
    out = []
    for typ, key, t, val in ops:
        if typ == 1:
            times, values = hist.setdefault(key, ([], []))
            times.append(t)
            values.append(val)
        else:
            if key not in hist:
                out.append(-1)
                continue
            times, values = hist[key]
            i = bisect_right(times, t) - 1
            out.append(values[i] if i >= 0 else -1)
    return out
''',
    tests=[[[[1, 1, 5, 100], [2, 1, 5, 0], [2, 1, 4, 0], [2, 1, 9, 0], [1, 1, 8, 200], [2, 1, 7, 0], [2, 1, 8, 0], [2, 1, 99, 0]]],
           [[[2, 7, 3, 0]]], [[[1, 7, 3, 0], [2, 7, 3, 0], [2, 7, 2, 0]]],
           [[[1, 1, 1, 10], [1, 2, 2, 20], [1, 1, 3, 30], [2, 2, 1, 0], [2, 2, 2, 0], [2, 1, 2, 0], [2, 3, 5, 0], [2, 1, 3, 0]]],
           [[[1, 10 ** 9, 10 ** 9, 10 ** 9], [2, 10 ** 9, 10 ** 9, 0], [2, 10 ** 9, 10 ** 9 - 1, 0], [2, 0, 0, 0]]],
           [[[1, 4, 0, 6], [1, 4, 1, 7], [1, 4, 2, 8], [2, 4, 0, 0], [2, 4, 1, 0], [2, 4, 2, 0], [2, 4, 3, 0]]],
           [[[2, 1, 0, 0], [2, 1, 1, 0], [1, 1, 1, 5], [2, 1, 0, 0], [2, 1, 1, 0]]]],
)
_r = rnd(8105)


def _gen_ops(r, n, keys, tmax_step, gets):
    ops = []
    clock = {}
    glob = 0
    for _ in range(n):
        if r.random() < gets and ops:
            k = r.randint(0, keys - 1) * 7
            ops.append([2, k, r.randint(0, glob + 3), 0])
        else:
            k = r.randint(0, keys - 1) * 7
            glob += r.randint(1, tmax_step)
            ops.append([1, k, glob, r.randint(0, 10 ** 9 if tmax_step > 5 else 20)])
        clock[k] = glob
    if all(o[0] == 1 for o in ops):
        ops.append([2, 0, glob, 0])
    return ops


p["tests"].append([_gen_ops(_r, 2400, 3, 50, 0.5)])
p["tests"].append([_gen_ops(_r, 2400, 400, 2000, 0.5)])
p["tests"].append([[[1, 5, i, i * 3] for i in range(1200)] + [[2, 5, i * 2, 0] for i in range(1200)]])


def b_time(ops):
    rec = []
    out = []
    for typ, key, t, val in ops:
        if typ == 1:
            rec.append((key, t, val))
        else:
            best_t, best_v = -1, -1
            for k2, t2, v2 in rec:
                if k2 == key and t2 <= t and t2 > best_t:
                    best_t, best_v = t2, v2
            out.append(best_v)
    return out


def g_time(r):
    return [_gen_ops(r, r.randint(1, 14), 3, 4, 0.5)]


def v_time(tests):
    for t in tests:
        ops = t["args"][0]
        assert 1 <= len(ops) <= 2500 and any(o[0] == 2 for o in ops)
        last = {}
        for o in ops:
            assert len(o) == 4 and o[0] in (1, 2)
            assert all(0 <= v <= 10 ** 9 for v in o[1:])
            if o[0] == 1:
                assert o[2] > last.get(o[1], -1), "set times must strictly increase per key"
                last[o[1]] = o[2]
            else:
                assert o[3] == 0


CHECKS["time-travel-key-lookup"] = (b_time, g_time, "exact")
VALIDATE["time-travel-key-lookup"] = v_time

p = add(
    id="find-right-interval-indices", title="Find the Right Interval", diff="Medium", topic=T, tier="extra",
    fn="rightIntervals", params=[("intervals", "int[][]")], ret="int[]", cmp="exact",
    desc="<p>You are given <code>intervals</code>, where <code>intervals[i] = [start, end]</code> with <code>start &le; end</code>. All start values are distinct.</p><p>The <em>right neighbour</em> of interval <code>i</code> is the interval <code>j</code> (possibly <code>j = i</code>) with the <strong>smallest start</strong> that is still <code>&ge; end</code> of interval <code>i</code>. Return an array whose entry <code>i</code> is the index <code>j</code> of the right neighbour of interval <code>i</code>, or <code>-1</code> when no interval starts at or after <code>intervals[i][1]</code>.</p>",
    constraints=["1 &le; intervals.length &le; 3,000", "-10<sup>9</sup> &le; start &le; end &le; 10<sup>9</sup>", "All start values are distinct"],
    hints=["Checking every other interval for every interval is O(n&sup2;). Think about which question each interval asks: 'what is the first start that is at least my end?'",
           "Sort the start values together with their interval indices. The question is exactly a lower-bound query on that sorted list.",
           "For each interval, run <code>lower_bound(end)</code> over the sorted starts. If the result is past the last element, answer <code>-1</code>; otherwise answer the original index stored with that start."],
    editorial=["Build a list of pairs <code>(start, index)</code> sorted by start; since starts are distinct, the order is unambiguous and the answer of every query is unique. For interval <code>i</code> with end <code>e</code>, the right neighbour is the first pair whose start is &ge; <code>e</code>, i.e. the lower bound of <code>e</code> in the list of starts.",
               "Sorting costs O(n log n) and each of the n lower-bound searches costs O(log n), for O(n log n) overall. Note that an interval can be its own right neighbour when <code>start == end</code>, because its own start is then &ge; its end."],
    time="O(n log n)", space="O(n)",
    solution='''from bisect import bisect_left

def rightIntervals(intervals):
    order = sorted(range(len(intervals)), key=lambda i: intervals[i][0])
    starts = [intervals[i][0] for i in order]
    out = []
    for s, e in intervals:
        k = bisect_left(starts, e)
        out.append(order[k] if k < len(order) else -1)
    return out
''',
    tests=[[[[1, 2]]], [[[3, 4], [2, 3], [1, 2]]], [[[1, 4], [2, 3], [3, 4]]], [[[5, 5]]], [[[0, 10], [1, 2], [3, 9]]],
           [[[-5, -2], [-3, 0], [0, 7], [4, 4]]], [[[1, 100], [2, 99], [3, 98]]], [[[10, 20], [5, 10], [1, 5]]],
           [[[-10 ** 9, 10 ** 9], [10 ** 9, 10 ** 9]]], [[[-10 ** 9, -10 ** 9], [-10 ** 9 + 1, 0]]]],
)
_r = rnd(8106)


def _gen_intervals(r, n, lo, hi, maxlen):
    starts = r.sample(range(lo, hi + 1), n)
    return [[s, min(hi, s + r.randint(0, maxlen))] for s in starts]


p["tests"].append([_gen_intervals(_r, 3000, -10 ** 9, 10 ** 9, 10 ** 8)])
p["tests"].append([_gen_intervals(_r, 3000, -5000, 5000, 40)])
p["tests"].append([[[i, i] for i in range(3000)]])


def b_right(intervals):
    out = []
    for s, e in intervals:
        best = -1
        for j, (s2, _) in enumerate(intervals):
            if s2 >= e and (best == -1 or s2 < intervals[best][0]):
                best = j
        out.append(best)
    return out


def g_right(r):
    n = r.randint(1, 8)
    return [_gen_intervals(r, n, -10, 10, 6)]


def v_right(tests):
    for t in tests:
        iv = t["args"][0]
        assert 1 <= len(iv) <= 3000
        assert len({s for s, _ in iv}) == len(iv), "starts must be distinct"
        assert all(-10 ** 9 <= s <= e <= 10 ** 9 for s, e in iv)


CHECKS["find-right-interval-indices"] = (b_right, g_right, "exact")
VALIDATE["find-right-interval-indices"] = v_right

p = add(
    id="obstacle-course-run-lengths", title="Obstacle Course Run Lengths", diff="Medium", topic=T,
    fn="runLengths", params=[("heights", "int[]")], ret="int[]", cmp="exact",
    desc="<p>An obstacle course has obstacles in a row with heights <code>heights[0..n-1]</code>. For each position <code>i</code>, build the longest possible sequence of obstacles that</p><ul><li>uses obstacle <code>i</code> as its <em>last</em> element,</li><li>only uses obstacles at positions <code>0..i</code>, taken in increasing position order (you may skip obstacles), and</li><li>has heights in <strong>non-decreasing</strong> order (equal heights are allowed).</li></ul><p>Return an array whose entry <code>i</code> is the length of that longest sequence for position <code>i</code>.</p>",
    constraints=["1 &le; heights.length &le; 4,000", "1 &le; heights[i] &le; 10<sup>7</sup>"],
    hints=["A DP where <code>len[i] = 1 + max(len[j])</code> over earlier <code>j</code> with <code>heights[j] &le; heights[i]</code> is O(n&sup2;). The goal is O(n log n).",
           "Maintain <code>tails[k]</code>: the smallest possible last height of a non-decreasing sequence of length <code>k + 1</code> among the obstacles seen so far. This list stays sorted.",
           "For a new height <code>h</code>, find the first position in <code>tails</code> whose value is <em>strictly greater</em> than <code>h</code> (an upper bound). Put <code>h</code> there (or append it); the answer for this position is that index plus one. Equal heights must extend a sequence, which is why it is the upper bound and not the lower bound."],
    editorial=["Process the obstacles left to right while keeping the array <code>tails</code>. If <code>tails[k]</code> is the smallest possible last height of a non-decreasing sequence with <code>k + 1</code> obstacles, then <code>tails</code> is non-decreasing. A new height <code>h</code> can extend the longest sequence whose last height is &le; <code>h</code>, so its run length is (the number of entries of <code>tails</code> that are &le; <code>h</code>) + 1 = <code>bisect_right(tails, h) + 1</code>.",
               "After finding that index <code>k</code>, we write <code>tails[k] = h</code> (replacing the first entry that is larger, or appending when none is larger). That keeps every entry minimal and the list sorted. The index returned by the upper bound plus one is exactly the answer for the current position. Each obstacle costs one binary search: O(n log n) total."],
    time="O(n log n)", space="O(n)",
    solution='''from bisect import bisect_right

def runLengths(heights):
    tails = []
    out = []
    for h in heights:
        k = bisect_right(tails, h)
        if k == len(tails):
            tails.append(h)
        else:
            tails[k] = h
        out.append(k + 1)
    return out
''',
    tests=[[[1, 2, 3, 2]], [[2, 2, 1]], [[3, 1, 5, 6, 4, 2]], [[7]], [[5, 5, 5, 5]], [[4, 3, 2, 1]], [[1, 2, 3, 4, 5]],
           [[1, 3, 2, 3, 2, 3]], [[10 ** 7, 1, 10 ** 7, 1, 10 ** 7]], [[2, 1, 2, 1, 2, 1, 2]]],
)
_r = rnd(8107)
p["tests"].append([[_r.randint(1, 10 ** 7) for _ in range(4000)]])
p["tests"].append([[_r.randint(1, 60) for _ in range(4000)]])
p["tests"].append([[4000 - i for i in range(4000)]])


def b_runs(heights):
    out = []
    for i, h in enumerate(heights):
        best = 1
        for j in range(i):
            if heights[j] <= h:
                best = max(best, out[j] + 1)
        out.append(best)
    return out


def v_runs(tests):
    for t in tests:
        h = t["args"][0]
        assert 1 <= len(h) <= 4000 and all(1 <= v <= 10 ** 7 for v in h)


CHECKS["obstacle-course-run-lengths"] = (b_runs, lambda r: [gen_arr(r, 1, 5, 1, 10)], "exact")
VALIDATE["obstacle-course-run-lengths"] = v_runs

p = add(
    id="range-value-frequency-queries", title="Range Value Frequency Queries", diff="Medium", topic=T,
    fn="rangeFrequency", params=[("nums", "int[]"), ("queries", "int[][]")], ret="int[]", cmp="exact",
    desc="<p>You are given an integer array <code>nums</code> (not sorted) and a list of queries. Each query is <code>[left, right, value]</code>; its answer is the number of indices <code>i</code> with <code>left &le; i &le; right</code> and <code>nums[i] == value</code>.</p><p>Return the answers to all queries as an array, in the order of the queries.</p>",
    constraints=["1 &le; nums.length &le; 3,000", "1 &le; queries.length &le; 1,500", "-10<sup>9</sup> &le; nums[i], value &le; 10<sup>9</sup>", "0 &le; left &le; right &lt; nums.length"],
    hints=["Counting inside each range costs O(n) per query, which can be too slow for many queries. Think about the positions of one value.",
           "For every distinct value, store the sorted list of indices where it occurs (build it with one left-to-right pass).",
           "A query asks how many positions in that sorted list fall in <code>[left, right]</code>. That is <code>upper_bound(right) - lower_bound(left)</code> inside the list; an unseen value gives 0."],
    editorial=["Group the indices by value: <code>positions[v]</code> is the list of indices holding <code>v</code>, which is already sorted because we append while scanning from left to right. For a query <code>(l, r, v)</code> the answer is the number of entries of <code>positions[v]</code> between <code>l</code> and <code>r</code> inclusive.",
               "In a sorted list that count is the index of the first entry greater than <code>r</code> (upper bound) minus the index of the first entry at least <code>l</code> (lower bound). The preprocessing is O(n); every query costs O(log n), so the total is O(n + q log n). The same idea answers 'how many elements of a sorted array lie in [lo, hi]' with two bounds."],
    time="O(n + q log n)", space="O(n)",
    solution='''from bisect import bisect_left, bisect_right

def rangeFrequency(nums, queries):
    positions = {}
    for i, v in enumerate(nums):
        positions.setdefault(v, []).append(i)
    out = []
    for l, r, v in queries:
        lst = positions.get(v)
        if not lst:
            out.append(0)
        else:
            out.append(bisect_right(lst, r) - bisect_left(lst, l))
    return out
''',
    tests=[[[1, 2, 1, 3, 1], [[0, 4, 1], [1, 3, 1], [2, 2, 1], [0, 0, 2], [3, 4, 3]]], [[5], [[0, 0, 5], [0, 0, 6]]],
           [[7, 7, 7, 7], [[0, 3, 7], [1, 2, 7], [3, 3, 7], [0, 0, 8]]], [[1, 2, 3, 4], [[0, 3, 5], [1, 2, 2], [1, 2, 3]]],
           [[-5, 0, -5, 10 ** 9, -10 ** 9, -5], [[0, 5, -5], [1, 4, -5], [3, 4, 10 ** 9], [4, 4, -10 ** 9], [0, 2, -10 ** 9]]],
           [[2, 3, 2, 3, 2, 3], [[0, 5, 2], [0, 5, 3], [1, 4, 2], [1, 4, 3], [2, 2, 2], [2, 2, 3]]]],
)
_r = rnd(8108)


def _gen_rfq(r, n, vals, q):
    nums = [r.choice(vals) for _ in range(n)]
    qs = []
    for _ in range(q):
        l = r.randint(0, n - 1)
        rr = r.randint(l, n - 1)
        qs.append([l, rr, r.choice(vals) if r.random() < 0.9 else 12345])
    return [nums, qs]


p["tests"].append(_gen_rfq(_r, 3000, list(range(-8, 9)), 1500))
p["tests"].append(_gen_rfq(_r, 3000, [_r.randint(-10 ** 9, 10 ** 9) for _ in range(400)], 1500))
p["tests"].append(_gen_rfq(_r, 3000, [4], 1500))


def b_rfq(nums, queries):
    return [sum(1 for i in range(l, r + 1) if nums[i] == v) for l, r, v in queries]


def g_rfq(r):
    return _gen_rfq(r, r.randint(1, 9), [0, 1, 2, 3], r.randint(1, 6))


def v_rfq(tests):
    for t in tests:
        nums, qs = t["args"]
        assert 1 <= len(nums) <= 3000 and 1 <= len(qs) <= 1500
        assert all(len(q) == 3 and 0 <= q[0] <= q[1] < len(nums) for q in qs)
        assert all(-10 ** 9 <= v <= 10 ** 9 for v in nums) and all(-10 ** 9 <= q[2] <= 10 ** 9 for q in qs)


CHECKS["range-value-frequency-queries"] = (b_rfq, g_rfq, "exact")
VALIDATE["range-value-frequency-queries"] = v_rfq

# ---------------------------------------------------------------- HARD

p = add(
    id="nested-envelopes-max-chain", title="Nested Envelopes Chain", diff="Hard", topic=T, tier="extra",
    fn="maxNested", params=[("envelopes", "int[][]")], ret="int", cmp="exact",
    desc="<p>Each envelope is given as <code>[w, h]</code>, its width and height. Envelope A fits inside envelope B only if <strong>both</strong> <code>A.w &lt; B.w</code> and <code>A.h &lt; B.h</code> (strictly smaller in each dimension; envelopes cannot be rotated).</p><p>Return the largest number of envelopes in a chain where each one fits inside the next. A single envelope is a chain of length 1.</p>",
    constraints=["1 &le; envelopes.length &le; 3,000", "1 &le; w, h &le; 10<sup>9</sup>", "Equal widths or equal heights do not nest"],
    hints=["Once the envelopes are ordered by width, the question about widths is mostly settled and you are left with a question about heights. It looks like a longest increasing subsequence.",
           "The danger is envelopes with equal widths: they must not both be used. Sort by width ascending and, for equal widths, by height <em>descending</em>.",
           "Now find the length of the longest <em>strictly</em> increasing subsequence of the heights with the 'tails' technique: for each height use a lower-bound search in the sorted tails list and overwrite (or append)."],
    editorial=["Sort the envelopes by width ascending, breaking ties by height descending. A chain is now a subsequence in which widths strictly increase and heights strictly increase. Within a group of equal widths the heights are in descending order, so no strictly increasing subsequence of heights can take two of them: this makes the width condition automatic and leaves only the longest strictly increasing subsequence (LIS) of the heights.",
               "Compute that LIS in O(n log n) with the tails array: <code>tails[k]</code> is the smallest possible last height of an increasing subsequence of length <code>k + 1</code>. For each height <code>h</code>, the lower bound <code>bisect_left(tails, h)</code> is the first entry that is &ge; <code>h</code>; replace it by <code>h</code>, or append <code>h</code> when none exists. Using the lower bound (not the upper bound) keeps the subsequence strictly increasing. The final length of <code>tails</code> is the answer."],
    time="O(n log n)", space="O(n)",
    solution='''from bisect import bisect_left

def maxNested(envelopes):
    envs = sorted(envelopes, key=lambda e: (e[0], -e[1]))
    tails = []
    for _, h in envs:
        k = bisect_left(tails, h)
        if k == len(tails):
            tails.append(h)
        else:
            tails[k] = h
    return len(tails)
''',
    tests=[[[[5, 4], [6, 4], [6, 7], [2, 3]]], [[[1, 1], [1, 1], [1, 1]]], [[[3, 3]]], [[[1, 1], [2, 2], [3, 3], [4, 4]]],
           [[[4, 4], [3, 3], [2, 2], [1, 1]]], [[[1, 5], [2, 4], [3, 3], [4, 2], [5, 1]]], [[[1, 1], [1, 2], [1, 3], [2, 1], [2, 2], [2, 3]]],
           [[[2, 100], [3, 200], [4, 300], [5, 500], [5, 400], [5, 250], [6, 370], [6, 360], [7, 380]]],
           [[[10 ** 9, 10 ** 9], [1, 1], [10 ** 9 - 1, 10 ** 9 - 1]]], [[[1, 2], [2, 1]]]],
)
_r = rnd(8109)
p["tests"].append([[[_r.randint(1, 10 ** 9), _r.randint(1, 10 ** 9)] for _ in range(2500)]])
p["tests"].append([[[_r.randint(1, 300), _r.randint(1, 300)] for _ in range(2500)]])
p["tests"].append([[[i + 1, i + 1] for i in range(2000)]])
p["tests"].append([[[i // 3 + 1, 2000 - i] for i in range(2000)]])


def b_nested(envelopes):
    envs = sorted(envelopes)
    n = len(envs)
    best = [1] * n
    for i in range(n):
        for j in range(i):
            if envs[j][0] < envs[i][0] and envs[j][1] < envs[i][1]:
                best[i] = max(best[i], best[j] + 1)
    return max(best)


def g_nested(r):
    return [[[r.randint(1, 6), r.randint(1, 6)] for _ in range(r.randint(1, 10))]]


def v_nested(tests):
    for t in tests:
        e = t["args"][0]
        assert 1 <= len(e) <= 3000 and all(len(x) == 2 and 1 <= x[0] <= 10 ** 9 and 1 <= x[1] <= 10 ** 9 for x in e)


CHECKS["nested-envelopes-max-chain"] = (b_nested, g_nested, "exact")
VALIDATE["nested-envelopes-max-chain"] = v_nested

p = add(
    id="weighted-job-scheduling-profit", title="Weighted Job Scheduling", diff="Hard", topic=T,
    fn="maxJobProfit", params=[("jobs", "int[][]")], ret="int", cmp="exact",
    desc="<p>Each job is given as <code>[start, end, profit]</code> and occupies the time interval from <code>start</code> to <code>end</code>. You can do only one job at a time. Two chosen jobs are compatible if one ends no later than the other starts: a job that ends at time <code>t</code> may be followed by a job that starts at time <code>t</code>.</p><p>Return the maximum total profit of a set of pairwise compatible jobs (the empty set has profit 0).</p>",
    constraints=["1 &le; jobs.length &le; 1,200", "0 &le; start &lt; end &le; 10<sup>9</sup>", "1 &le; profit &le; 10,000"],
    hints=["A greedy choice (earliest end, highest profit) fails here because profits differ. Think of a DP over jobs ordered by end time.",
           "Sort jobs by end time. Let <code>dp[i]</code> be the best profit using only the first <code>i</code> jobs of that order. Either skip job <code>i</code>, or take it together with the best result among jobs that finish by its start.",
           "The number of jobs that end at or before <code>start</code> of job <code>i</code> is an upper-bound search in the sorted array of end times. Then <code>dp[i] = max(dp[i-1], dp[that count] + profit)</code>."],
    editorial=["Sort the jobs by end time and let <code>ends</code> be the sorted end times. Define <code>dp[i]</code> as the best profit using only the first <code>i</code> jobs in this order (<code>dp[0] = 0</code>). For job number <code>i</code> (1-based) there are two choices: skip it, giving <code>dp[i - 1]</code>; or take it, which allows exactly those earlier jobs that end at or before its start. Because the list is sorted by end, those jobs are a prefix of it, and the prefix length is <code>bisect_right(ends, start)</code> (jobs ending exactly at <code>start</code> are allowed). The value is <code>dp[prefix] + profit</code>.",
               "The prefix can be found only among the jobs before <code>i</code>; since the job itself has <code>end &gt; start</code>, the upper bound is never beyond <code>i - 1</code>, so the lookup is safe. Sorting takes O(n log n), and the n binary searches another O(n log n). The result is <code>dp[n]</code>. The profits sum to at most 1,200 &times; 10,000, so there is no overflow."],
    time="O(n log n)", space="O(n)",
    solution='''from bisect import bisect_right

def maxJobProfit(jobs):
    jobs = sorted(jobs, key=lambda j: j[1])
    ends = [j[1] for j in jobs]
    dp = [0] * (len(jobs) + 1)
    for i, (s, e, w) in enumerate(jobs, 1):
        k = bisect_right(ends, s)
        dp[i] = max(dp[i - 1], dp[k] + w)
    return dp[-1]
''',
    tests=[[[[1, 3, 50], [2, 4, 10], [3, 5, 40], [3, 6, 70]]], [[[1, 2, 5], [2, 3, 6], [3, 4, 5], [1, 4, 10]]], [[[0, 10, 7]]],
           [[[0, 5, 10], [5, 10, 10], [0, 10, 19]]], [[[0, 5, 10], [5, 10, 10], [0, 10, 21]]], [[[1, 2, 1], [1, 2, 3], [1, 2, 2]]],
           [[[1, 10, 100], [2, 3, 30], [4, 5, 30], [6, 7, 30], [8, 9, 30]]], [[[0, 10 ** 9, 10000], [0, 5 * 10 ** 8, 6000], [5 * 10 ** 8, 10 ** 9, 6000]]],
           [[[1, 4, 3], [3, 5, 2], [0, 6, 4], [4, 7, 5], [5, 9, 1], [6, 10, 6]]], [[[0, 1, 1], [1, 2, 1], [2, 3, 1], [3, 4, 1]]]],
)
_r = rnd(8110)


def _gen_jobs(r, n, tmax, maxlen):
    out = []
    for _ in range(n):
        s = r.randint(0, tmax - 1)
        out.append([s, min(tmax, s + r.randint(1, maxlen)), r.randint(1, 10000)])
    return out


p["tests"].append([_gen_jobs(_r, 1200, 10 ** 9, 10 ** 8)])
p["tests"].append([_gen_jobs(_r, 1200, 5000, 60)])
p["tests"].append([_gen_jobs(_r, 1200, 3000, 3000)])
p["tests"].append([[[i, i + 1, 10000] for i in range(1200)]])


def b_jobs(jobs):
    n = len(jobs)
    best = 0
    for mask in range(1 << n):
        ch = [jobs[i] for i in range(n) if mask >> i & 1]
        ch.sort()
        if all(ch[i][1] <= ch[i + 1][0] for i in range(len(ch) - 1)):
            best = max(best, sum(j[2] for j in ch))
    return best


def g_jobs(r):
    return [_gen_jobs(r, r.randint(1, 8), 12, 5)]


def v_jobs(tests):
    for t in tests:
        jobs = t["args"][0]
        assert 1 <= len(jobs) <= 1200
        assert all(0 <= s < e <= 10 ** 9 and 1 <= w <= 10000 for s, e, w in jobs)


CHECKS["weighted-job-scheduling-profit"] = (b_jobs, g_jobs, "exact")
VALIDATE["weighted-job-scheduling-profit"] = v_jobs

p = add(
    id="max-rectangle-sum-at-most-k", title="Maximum Rectangle Sum Not Above K", diff="Hard", topic=T, tier="extra",
    fn="maxRectSumAtMost", params=[("matrix", "int[][]"), ("k", "int")], ret="int", cmp="exact",
    desc="<p>Given an <code>m x n</code> integer matrix and an integer <code>k</code>, consider every non-empty rectangle of consecutive rows and consecutive columns. Return the <strong>largest</strong> sum of the cells of a rectangle whose sum is <strong>at most</strong> <code>k</code>.</p><p>The input guarantees that at least one rectangle has a sum that does not exceed <code>k</code>, so the answer always exists. The matrix may contain negative numbers.</p>",
    constraints=["1 &le; m, n &le; 60", "-100 &le; matrix[i][j] &le; 100", "-10<sup>6</sup> &le; k &le; 10<sup>6</sup>", "At least one rectangle has a sum that is at most k"],
    hints=["Enumerating all rectangles with a 2-D prefix sum is O(m&sup2;n&sup2;). Reduce the problem to one dimension: fix the top and bottom row.",
           "For a fixed pair of rows, add the rows column by column to get a 1-D array of column sums. You need the best subarray sum that is at most k in that array.",
           "With prefix sums <code>P</code> of the 1-D array, a subarray ending at <code>j</code> has sum <code>P[j] - P[i]</code>. To make it as large as possible while &le; k you need the <em>smallest</em> earlier prefix that is &ge; <code>P[j] - k</code>: a lower-bound query on a sorted list of earlier prefixes."],
    editorial=["Choose the thinner dimension as the 'column' side by transposing when needed (here m &le; n is not required for correctness, only for speed). For every pair of rows <code>(top, bottom)</code> maintain the array <code>col[c]</code> = sum of column <code>c</code> between those rows. The best rectangle with these rows is the best subarray of <code>col</code> with sum &le; k.",
               "Scan <code>col</code> with a running prefix sum <code>P</code> and a sorted list <code>seen</code> of the earlier prefixes (initially <code>[0]</code>). The subarray ending here that starts after an earlier prefix <code>q</code> has sum <code>P - q</code>. It is &le; k exactly when <code>q &ge; P - k</code>, and it is maximal for the smallest such <code>q</code>. The lower bound <code>bisect_left(seen, P - k)</code> finds that <code>q</code> (if the index is inside the list), then insert <code>P</code> into <code>seen</code> to keep it sorted.",
               "The cost is O(m&sup2; &middot; n log n) when the loop over row pairs is on the smaller dimension. Inserting into a Python list is O(n) in the worst case but very fast in practice for n &le; 60. A common shortcut: if you find a sum exactly equal to <code>k</code> you can stop, since nothing larger is allowed."],
    time="O(min(m,n)^2 * max(m,n) log max(m,n))", space="O(max(m,n))",
    solution='''from bisect import bisect_left, insort

def maxRectSumAtMost(matrix, k):
    m, n = len(matrix), len(matrix[0])
    if m > n:
        matrix = [list(col) for col in zip(*matrix)]
        m, n = n, m
    best = None
    for top in range(m):
        col = [0] * n
        for bottom in range(top, m):
            row = matrix[bottom]
            for c in range(n):
                col[c] += row[c]
            seen = [0]
            pref = 0
            for c in range(n):
                pref += col[c]
                i = bisect_left(seen, pref - k)
                if i < len(seen):
                    cand = pref - seen[i]
                    if best is None or cand > best:
                        best = cand
                        if best == k:
                            return k
                insort(seen, pref)
    return best
''',
    tests=[[[[1, 0, 1], [0, -2, 3]], 2], [[[2, 2, -1]], 3], [[[2, 2, -1]], 0], [[[5]], 5], [[[-7]], -7], [[[-7]], 100],
           [[[1, 2], [3, 4]], 3], [[[1, 2], [3, 4]], 100], [[[-1, -2], [-3, -4]], -5], [[[-1, -2], [-3, -4]], -1],
           [[[5], [-3], [4], [-6]], 2], [[[100, -100], [-100, 100]], 0], [[[1, 1, 1, 1]], 2]],
)
_r = rnd(8111)
p["tests"].append([[[_r.randint(-100, 100) for _ in range(60)] for _ in range(60)], 1500])
p["tests"].append([[[_r.randint(-100, 100) for _ in range(60)] for _ in range(60)], -50])
p["tests"].append([[[_r.randint(-100, 100) for _ in range(60)] for _ in range(8)], 777])
p["tests"].append([[[_r.randint(-100, 100) for _ in range(5)] for _ in range(60)], 123])


def b_rect(matrix, k):
    m, n = len(matrix), len(matrix[0])
    pre = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(m):
        for j in range(n):
            pre[i + 1][j + 1] = matrix[i][j] + pre[i][j + 1] + pre[i + 1][j] - pre[i][j]
    best = None
    for a in range(m):
        for b in range(a, m):
            for c in range(n):
                for d in range(c, n):
                    s = pre[b + 1][d + 1] - pre[a][d + 1] - pre[b + 1][c] + pre[a][c]
                    if s <= k and (best is None or s > best):
                        best = s
    return best


def g_rect(r):
    m, n = r.randint(1, 4), r.randint(1, 4)
    mat = [[r.randint(-6, 6) for _ in range(n)] for _ in range(m)]
    lo = min(min(row) for row in mat)
    return [mat, r.randint(lo, lo + 14)]


def v_rect(tests):
    for t in tests:
        mat, k = t["args"]
        m, n = len(mat), len(mat[0])
        assert 1 <= m <= 60 and 1 <= n <= 60 and all(len(row) == n for row in mat)
        assert all(-100 <= v <= 100 for row in mat for v in row)
        assert -10 ** 6 <= k <= 10 ** 6
        assert t["expected"] is not None and t["expected"] <= k, "no rectangle sums to at most k"


CHECKS["max-rectangle-sum-at-most-k"] = (b_rect, g_rect, "exact")
VALIDATE["max-rectangle-sum-at-most-k"] = v_rect
