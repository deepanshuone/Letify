"""Problems: two pointers, partitioning and deduplication in place. See data/lib.py for the registry."""
from collections import Counter, deque  # noqa: F401

from lib import add, rnd, CHECKS, VALIDATE, gen_arr  # noqa: F401

INT_MIN, INT_MAX = -(2 ** 31), 2 ** 31 - 1
TOPIC = "Two Pointers"


# ---------------------------------------------------------------- EASY

p = add(
    id="duplicate-zeros-shift-right", title="Duplicate Zeros", diff="Easy", topic=TOPIC, tier="common",
    fn="duplicateZeros", params=[("arr", "int[]")], ret="int[]", cmp="exact",
    desc="<p>Given an integer array <code>arr</code>, write every <code>0</code> twice and push the elements that follow it to the right. The array keeps its original length, so whatever is pushed past the last position is discarded. Return the resulting array.</p>"
         "<pre>arr = [1, 0, 2, 3, 0, 4, 5, 0]\nresult = [1, 0, 0, 2, 3, 0, 0, 4]</pre>"
         "<p>The expanded sequence would be <code>1 0 0 2 3 0 0 4 5 0 0</code>; only its first 8 values fit. Try to do it in place with O(1) extra space.</p>",
    constraints=["0 &le; arr.length &le; 10,000", "-2<sup>31</sup> &le; arr[i] &le; 2<sup>31</sup> - 1"],
    hints=["Building the fully expanded list and cutting it to the original length works, but it needs O(n) extra memory.",
           "Shifting values to the right is safe only if you write from the back, otherwise you overwrite values you have not read yet. First count the zeros so you know where the last kept element ends up.",
           "Let <code>j = n + zeros - 1</code> be the index in the imaginary expanded array of the last element. Walk <code>i</code> from the right; write <code>arr[i]</code> at <code>j</code> only when <code>j &lt; n</code>, step <code>j</code> down, and for a zero write one more <code>0</code> at the next <code>j</code> (again only if it is inside the array)."],
    editorial=["Imagine the expanded array, which has length <code>n + zeros</code>. The element at original index <code>i</code> sits at expanded index <code>i + (zeros before i)</code>, and a zero occupies two cells. We only keep the cells with index below <code>n</code>.",
               "Copying from the left would overwrite unread values, so go from right to left with two pointers: <code>i</code> reads the original array and <code>j</code> is the position inside the expanded array. At each <code>i</code> write the value to <code>j</code> if <code>j &lt; n</code>; if the value is zero, step <code>j</code> down once more and write a second zero if that cell is also inside the array; then step <code>j</code> down. Because <code>j &ge; i</code> at every moment, a write never destroys a value that is still to be read.",
               "One pass to count the zeros and one pass to write: O(n) time, O(1) extra space."],
    time="O(n)", space="O(1)",
    solution='''def duplicateZeros(arr):
    a = list(arr)
    n = len(a)
    j = n + a.count(0) - 1
    for i in range(n - 1, -1, -1):
        if j < n:
            a[j] = a[i]
        if a[i] == 0:
            j -= 1
            if j < n:
                a[j] = 0
        j -= 1
    return a
''',
    tests=[[[1, 0, 2, 3, 0, 4, 5, 0]], [[1, 2, 3]], [[]], [[0]], [[7]], [[0, 0, 0]], [[0, 1, 2, 3]], [[1, 2, 0]], [[1, 0, 2]],
           [[0, 0, 1, 0]], [[8, 4, 5, 0, 0, 0, 0, 7]], [[INT_MIN, 0, INT_MAX, 0, -1]]],
)
_r = rnd(7101)
p["tests"].append([[_r.choice([0, 0, _r.randint(-99, 99)]) for _ in range(5000)]])
p["tests"].append([[_r.randint(1, 9) if _r.random() < 0.9 else 0 for _ in range(5000)]])
p["tests"].append([[0] * 3000])


def b_dz(arr):
    out = []
    for x in arr:
        out.append(x)
        if x == 0:
            out.append(0)
    return out[:len(arr)]


def v_dz(tests):
    for t in tests:
        assert 0 <= len(t["args"][0]) <= 10000 and len(t["expected"]) == len(t["args"][0])


CHECKS["duplicate-zeros-shift-right"] = (b_dz, lambda r: [gen_arr(r, -2, 2, 0, 12)], "exact")
VALIDATE["duplicate-zeros-shift-right"] = v_dz


p = add(
    id="parity-positions-min-swaps", title="Fix Parity Positions", diff="Easy", topic=TOPIC, tier="extra",
    fn="minSwapsParity", params=[("nums", "int[]")], ret="int", cmp="exact",
    desc="<p>The array <code>nums</code> has even length <code>n</code> and contains exactly <code>n / 2</code> even numbers (so the other <code>n / 2</code> are odd). In one move you may swap any two elements.</p>"
         "<p>Return the minimum number of moves after which every even index holds an even number and every odd index holds an odd number.</p>"
         "<pre>nums = [4, 2, 5, 7]\nresult = 1</pre>"
         "<p>Here <code>2</code> sits at index 1 and <code>5</code> sits at index 2; swapping them fixes both.</p>",
    constraints=["2 &le; nums.length &le; 10,000 and nums.length is even", "-2<sup>31</sup> &le; nums[i] &le; 2<sup>31</sup> - 1", "Exactly nums.length / 2 values are even"],
    hints=["Call a position <em>wrong</em> if its parity does not match its index. Which wrong positions can a single swap repair?",
           "A swap repairs two positions at once when it exchanges an odd value standing at an even index with an even value standing at an odd index.",
           "Because exactly half of the values are even, the number of odd values at even indices always equals the number of even values at odd indices. The answer is that common number, so one counting pass is enough."],
    editorial=["Split the wrong positions in two groups: odd values sitting at even indices (call this count <code>a</code>) and even values sitting at odd indices (count <code>b</code>). The array has <code>n / 2</code> even indices and <code>n / 2</code> even values. The even indices are filled by <code>n / 2 - a</code> even values, so <code>n / 2 - (n / 2 - a) = a</code> even values live at odd indices, hence <code>a = b</code>.",
               "A swap can fix at most two wrong positions, and swapping one wrong item of each group fixes exactly two. So <code>a</code> swaps are necessary and sufficient.",
               "Counting takes one pass: O(n) time and O(1) space. Careful with negative numbers: use <code>x % 2</code> (or <code>x &amp; 1</code>), not a comparison with 1 after a remainder operator that keeps the sign."],
    time="O(n)", space="O(1)",
    solution='''def minSwapsParity(nums):
    wrong = 0
    for i in range(0, len(nums), 2):
        if nums[i] % 2 != 0:
            wrong += 1
    return wrong
''',
    tests=[[[4, 2, 5, 7]], [[1, 0]], [[0, 1]], [[2, 4, 1, 3]], [[1, 3, 2, 4]], [[-3, -2, -5, -4]], [[6, 1, 2, 3, 4, 5]],
           [[INT_MAX, INT_MIN, INT_MIN, INT_MAX]], [[5, 5, 5, 2, 2, 2]], [[3, 8, 1, 6, 5, 4, 7, 2]]],
)
_r = rnd(7102)


def _par(n, r, shuffle=True):
    a = [r.randint(-10 ** 6, 10 ** 6) * 2 for _ in range(n // 2)] + [r.randint(-10 ** 6, 10 ** 6) * 2 + 1 for _ in range(n // 2)]
    if shuffle:
        r.shuffle(a)
    return a


p["tests"].append([_par(8000, _r)])
p["tests"].append([[x for pair in zip([_r.randint(1, 99) * 2 + 1 for _ in range(2500)], [_r.randint(1, 99) * 2 for _ in range(2500)]) for x in pair]])
p["tests"].append([_par(4000, _r, False)])


def b_par(nums):
    # breadth-first search over swaps on the pattern of "is the value even"
    start = tuple(x % 2 for x in nums)
    goal = tuple(i % 2 for i in range(len(nums)))
    seen = {start}
    dq = deque([(start, 0)])
    while dq:
        s, d = dq.popleft()
        if s == goal:
            return d
        for i in range(len(s)):
            for j in range(i + 1, len(s)):
                if s[i] != s[j]:
                    t = list(s)
                    t[i], t[j] = t[j], t[i]
                    t = tuple(t)
                    if t not in seen:
                        seen.add(t)
                        dq.append((t, d + 1))


def g_par(r):
    h = r.randint(1, 3)
    return [_par(2 * h, r)]


def v_par(tests):
    for t in tests:
        nums = t["args"][0]
        assert 2 <= len(nums) <= 10000 and len(nums) % 2 == 0
        assert sum(1 for x in nums if x % 2 == 0) == len(nums) // 2


CHECKS["parity-positions-min-swaps"] = (b_par, g_par, "exact")
VALIDATE["parity-positions-min-swaps"] = v_par


p = add(
    id="merge-equal-neighbors-shift-zeros", title="Merge Equal Neighbors, Shift Zeros", diff="Easy", topic=TOPIC, tier="extra",
    fn="applyOperations", params=[("nums", "int[]")], ret="int[]", cmp="exact",
    desc="<p>You are given an array <code>nums</code> of non-negative integers. Perform these operations one after another for <code>i = 0, 1, ..., n - 2</code> (using the values the array holds at that moment):</p>"
         "<ul><li>if <code>nums[i] == nums[i + 1]</code>, set <code>nums[i]</code> to <code>2 * nums[i]</code> and <code>nums[i + 1]</code> to <code>0</code>;</li><li>otherwise do nothing.</li></ul>"
         "<p>After all operations, move every <code>0</code> to the end of the array, keeping the order of the non-zero values. Return the resulting array.</p>"
         "<pre>nums = [1, 2, 2, 1, 1, 0]\nafter the operations: [1, 4, 0, 2, 0, 0]\nresult = [1, 4, 2, 0, 0, 0]</pre>",
    constraints=["1 &le; nums.length &le; 10,000", "0 &le; nums[i] &le; 1,000"],
    hints=["Do what the statement says: one pass for the operations, then a second job for the zeros. Keep the two phases separate at first.",
           "Operations only look at <code>nums[i]</code> and <code>nums[i + 1]</code> and only change them, so a simple left-to-right loop in place is correct (a zero created at <code>i + 1</code> is then compared with <code>nums[i + 2]</code>).",
           "To move zeros to the end keep a write pointer: for every non-zero value, put it at the write position and advance; finally fill the rest with zeros."],
    editorial=["Phase 1 is a direct simulation: a single loop over adjacent pairs. A value is doubled at most once, because after a merge the right neighbour becomes zero and the left neighbour has already been compared with its right side. Values therefore stay at most 2,000.",
               "Phase 2 is the standard compaction with two pointers: <code>write</code> is the next free slot for a non-zero value and <code>read</code> scans the array. Copy every non-zero value to <code>write</code> and advance it, then overwrite the tail with zeros.",
               "Both phases are linear: O(n) time and O(1) extra space when done in place."],
    time="O(n)", space="O(1)",
    solution='''def applyOperations(nums):
    a = list(nums)
    n = len(a)
    for i in range(n - 1):
        if a[i] == a[i + 1]:
            a[i] *= 2
            a[i + 1] = 0
    write = 0
    for read in range(n):
        if a[read] != 0:
            a[write] = a[read]
            write += 1
    for k in range(write, n):
        a[k] = 0
    return a
''',
    tests=[[[1, 2, 2, 1, 1, 0]], [[0, 1]], [[1]], [[0]], [[0, 0, 0]], [[3, 3, 3, 3]], [[5, 5, 5]], [[1, 2, 3, 4]], [[0, 7, 7, 0, 9]],
           [[4, 4, 0, 4, 4]], [[1000, 1000, 1000, 1000, 0, 1000]], [[2, 2, 4, 4, 8, 8, 16]]],
)
_r = rnd(7103)
p["tests"].append([[_r.randint(0, 3) for _ in range(6000)]])
p["tests"].append([[_r.choice((0, 1000, 999)) for _ in range(5000)]])
p["tests"].append([[7] * 4001])


def b_apply(nums):
    a = list(nums)
    for i in range(len(a) - 1):
        if a[i] == a[i + 1]:
            a[i], a[i + 1] = a[i] * 2, 0
    return [x for x in a if x != 0] + [0] * a.count(0)


def v_apply(tests):
    for t in tests:
        nums = t["args"][0]
        assert 1 <= len(nums) <= 10000 and all(0 <= x <= 1000 for x in nums)


CHECKS["merge-equal-neighbors-shift-zeros"] = (b_apply, lambda r: [gen_arr(r, 0, 3, 1, 12)], "exact")
VALIDATE["merge-equal-neighbors-shift-zeros"] = v_apply


# ---------------------------------------------------------------- MEDIUM

p = add(
    id="remove-duplicates-keep-at-most-k", title="Remove Duplicates, Keep At Most K Copies", diff="Medium", topic=TOPIC, tier="must",
    fn="removeDuplicatesK", params=[("nums", "int[]"), ("k", "int")], ret="int[]", cmp="exact",
    desc="<p>The array <code>nums</code> is sorted in non-decreasing order. Remove surplus copies so that every distinct value appears <strong>at most <code>k</code> times</strong>, keeping the remaining values in their original order. Return the resulting array.</p>"
         "<pre>nums = [1, 1, 1, 2, 2, 3], k = 2\nresult = [1, 1, 2, 2, 3]</pre>"
         "<pre>nums = [0, 0, 1, 1, 1, 1, 2, 3, 3], k = 1\nresult = [0, 1, 2, 3]</pre>"
         "<p>Aim for O(n) time and O(1) extra space by overwriting the array in place.</p>",
    constraints=["0 &le; nums.length &le; 10,000", "1 &le; k &le; 10,000", "-2<sup>31</sup> &le; nums[i] &le; 2<sup>31</sup> - 1", "nums is sorted in non-decreasing order"],
    hints=["Since the array is sorted, equal values are adjacent. A value is a surplus copy when at least <code>k</code> copies of it were already kept.",
           "Keep a write pointer <code>w</code>: the number of elements kept so far. The kept prefix is itself sorted, so the last <code>k</code> kept elements tell you how many copies of the current value you already hold.",
           "Accept <code>nums[i]</code> if <code>w &lt; k</code> or <code>nums[i] != nums[w - k]</code>; in that case write it at <code>nums[w]</code> and increment <code>w</code>. If <code>nums[w - k]</code> already equals the value, then all k kept elements after it are equal too."],
    editorial=["Scan with a read index <code>i</code> and keep the result in the prefix <code>nums[0:w]</code>. When we consider <code>x = nums[i]</code>, the kept prefix is sorted and its last element is at most <code>x</code>. The number of kept copies of <code>x</code> is at least <code>k</code> exactly when <code>nums[w - k] == x</code> (the element <code>k</code> places before the end of the kept prefix is equal to <code>x</code>, and everything between them is sandwiched, so equal too).",
               "Therefore <code>x</code> is accepted iff <code>w &lt; k</code> or <code>nums[w - k] != x</code>. This one-line test is the whole algorithm and it works for every <code>k</code> without a separate counter; for <code>k = 1</code> it is the classic dedup and for <code>k = 2</code> the 'at most twice' version.",
               "Each element is read once and written at most once: O(n) time, O(1) extra space."],
    time="O(n)", space="O(1)",
    solution='''def removeDuplicatesK(nums, k):
    a = list(nums)
    w = 0
    for x in a:
        if w < k or a[w - k] != x:
            a[w] = x
            w += 1
    return a[:w]
''',
    tests=[[[1, 1, 1, 2, 2, 3], 2], [[0, 0, 1, 1, 1, 1, 2, 3, 3], 1], [[], 3], [[5], 1], [[4, 4, 4, 4], 2], [[4, 4, 4, 4], 4],
           [[4, 4, 4, 4], 10], [[1, 2, 3], 1], [[-2, -2, -2, 0, 0, 7, 7, 7, 7], 3], [[1, 1, 2, 2, 2, 2, 2, 3], 2],
           [[INT_MIN, INT_MIN, INT_MIN, INT_MAX, INT_MAX], 2]],
)
_r = rnd(7104)
p["tests"].append([sorted(_r.randint(-300, 300) for _ in range(6000)), 3])
p["tests"].append([sorted(_r.choice((-5, 0, 5)) for _ in range(8000)), 1])
p["tests"].append([sorted(_r.randint(-5, 5) for _ in range(5000)), 1000])


def b_rdk(nums, k):
    c = Counter()
    out = []
    for x in nums:
        c[x] += 1
        if c[x] <= k:
            out.append(x)
    return out


def g_rdk(r):
    return [sorted(gen_arr(r, -3, 3, 0, 12)), r.randint(1, 4)]


def v_rdk(tests):
    for t in tests:
        nums, k = t["args"]
        assert len(nums) <= 10000 and 1 <= k <= 10000 and nums == sorted(nums)
        assert all(v <= k for v in Counter(t["expected"]).values())


CHECKS["remove-duplicates-keep-at-most-k"] = (b_rdk, g_rdk, "exact")
VALIDATE["remove-duplicates-keep-at-most-k"] = v_rdk


p = add(
    id="drop-all-repeated-values-sorted", title="Drop Every Repeated Value", diff="Medium", topic=TOPIC, tier="common",
    fn="keepSingles", params=[("nums", "int[]")], ret="int[]", cmp="exact",
    desc="<p>The array <code>nums</code> is sorted in non-decreasing order. Delete <strong>every</strong> element whose value occurs more than once (all of its copies, not just the extra ones) and return what is left, in order.</p>"
         "<pre>nums = [1, 2, 2, 3, 4, 4, 4, 5]\nresult = [1, 3, 5]</pre>"
         "<pre>nums = [7, 7, 7]\nresult = []</pre>"
         "<p>Use O(1) extra space apart from the returned array.</p>",
    constraints=["0 &le; nums.length &le; 10,000", "-2<sup>31</sup> &le; nums[i] &le; 2<sup>31</sup> - 1", "nums is sorted in non-decreasing order"],
    hints=["Equal values form contiguous runs. A value survives only if its run has length exactly 1.",
           "A value at index <code>i</code> is unique when it differs from both its left neighbour and its right neighbour (a missing neighbour counts as different).",
           "Walk <code>i</code> through the array with a write pointer. Copy <code>nums[i]</code> to <code>nums[write]</code> only if <code>nums[i] != nums[i - 1]</code> and <code>nums[i] != nums[i + 1]</code> (checking bounds)."],
    editorial=["Because the array is sorted, a repeated value must be adjacent to one of its copies. Therefore an element is a single exactly when it is different from the element before it and from the element after it. This turns the problem into a filter with a local test.",
               "Run a read index over the array and compact the survivors with a write pointer, just like in the usual removal of duplicates. Do not overwrite values that you still have to look at: since <code>write &le; read</code> and you only ever need <code>nums[i - 1]</code>, keep the previous original value in a variable (or read from the untouched copy) instead of from the partially overwritten array.",
               "A single pass gives O(n) time and O(1) extra space."],
    time="O(n)", space="O(1)",
    solution='''def keepSingles(nums):
    a = list(nums)
    n = len(a)
    w = 0
    prev = None
    for i in range(n):
        x = a[i]
        nxt = a[i + 1] if i + 1 < n else None
        if n and x != prev and x != nxt:
            a[w] = x
            w += 1
        prev = x
    return a[:w]
''',
    tests=[[[1, 2, 2, 3, 4, 4, 4, 5]], [[7, 7, 7]], [[]], [[9]], [[1, 1, 2]], [[1, 2, 2]], [[1, 2, 3]], [[3, 3, 4, 4]], [[-5, -5, 0, 1, 1, 2, 8, 8, 8, 9]],
           [[INT_MIN, INT_MIN, -1, INT_MAX]], [[0, 0, 0, 1, 2, 2, 3]]],
)
_r = rnd(7105)
p["tests"].append([sorted(_r.sample(range(-5000, 5000), 2000) + _r.sample(range(-5000, 5000), 1000) * 2)])
p["tests"].append([sorted(_r.randint(-4000, 4000) for _ in range(5000))])
p["tests"].append([list(range(-2000, 2000)) + [10 ** 6] * 3000])


def b_ks(nums):
    c = Counter(nums)
    return [x for x in nums if c[x] == 1]


def v_ks(tests):
    for t in tests:
        nums = t["args"][0]
        assert len(nums) <= 10000 and nums == sorted(nums)


CHECKS["drop-all-repeated-values-sorted"] = (b_ks, lambda r: [sorted(gen_arr(r, -3, 3, 0, 12))], "exact")
VALIDATE["drop-all-repeated-values-sorted"] = v_ks


p = add(
    id="partition-around-pivot-keep-order", title="Partition Around a Pivot, Keep Order", diff="Medium", topic=TOPIC, tier="extra",
    fn="pivotPartition", params=[("nums", "int[]"), ("pivot", "int")], ret="int[]", cmp="exact",
    desc="<p>Rearrange <code>nums</code> around the value <code>pivot</code> (which may or may not occur in the array) so that:</p>"
         "<ul><li>all values smaller than <code>pivot</code> come first,</li><li>then all values equal to <code>pivot</code>,</li><li>then all values greater than <code>pivot</code>;</li></ul>"
         "<p>and, inside each of the three groups, the values keep the relative order they had in <code>nums</code>. Return the resulting array.</p>"
         "<pre>nums = [9, 12, 5, 10, 14, 3, 10], pivot = 10\nresult = [9, 5, 3, 10, 10, 12, 14]</pre>",
    constraints=["0 &le; nums.length &le; 10,000", "-2<sup>31</sup> &le; nums[i], pivot &le; 2<sup>31</sup> - 1"],
    hints=["Three stable groups: you could collect them in three lists and concatenate. That is already O(n). Can the result be written directly into one output array of the same size?",
           "The smaller group starts at the front and the larger group ends at the back; the pivots simply fill the middle. Only the position where each group is written matters.",
           "Fill the output with <code>pivot</code>. Write the smaller values from index 0 upward while scanning <code>nums</code> left to right. Write the larger values from the last index downward while scanning <code>nums</code> right to left, so they end up in their original order."],
    editorial=["The result consists of <code>L</code> smaller values, then <code>E</code> pivots, then <code>G</code> larger values. The two outer groups can be written independently with two write pointers: <code>lo</code> starts at 0 and moves right, <code>hi</code> starts at <code>n - 1</code> and moves left.",
               "Scanning <code>nums</code> from the left, every value smaller than the pivot goes to <code>out[lo++]</code>, which keeps the smaller values in order. To keep the larger values in order while filling from the back, scan <code>nums</code> from the right and send every larger value to <code>out[hi--]</code>. Everything that was never written is a pivot copy, so initialising <code>out</code> with the pivot handles the middle for free.",
               "Two passes, O(n) time, and the O(n) output array is the only extra memory. (A stable partition with O(1) extra memory is much harder and not requested here; the order requirement is what makes the answer unique.)"],
    time="O(n)", space="O(n)",
    solution='''def pivotPartition(nums, pivot):
    n = len(nums)
    out = [pivot] * n
    lo = 0
    for x in nums:
        if x < pivot:
            out[lo] = x
            lo += 1
    hi = n - 1
    for i in range(n - 1, -1, -1):
        if nums[i] > pivot:
            out[hi] = nums[i]
            hi -= 1
    return out
''',
    tests=[[[9, 12, 5, 10, 14, 3, 10], 10], [[], 5], [[4], 4], [[4], 9], [[4], -9], [[1, 2, 3, 4], 0], [[1, 2, 3, 4], 5], [[3, 3, 3], 3],
           [[-1, 5, -3, 5, 0, 8, -2], 0], [[6, 1, 6, 1, 6, 1], 2], [[INT_MAX, INT_MIN, 0, INT_MAX, INT_MIN], 0]],
)
_r = rnd(7106)
p["tests"].append([[_r.randint(-500, 500) for _ in range(6000)], 17])
p["tests"].append([[_r.randint(0, 2) for _ in range(7000)], 1])
p["tests"].append([[_r.randint(INT_MIN, INT_MAX) for _ in range(1500)], 0])


def b_pp(nums, pivot):
    return [x for x in nums if x < pivot] + [x for x in nums if x == pivot] + [x for x in nums if x > pivot]


def v_pp(tests):
    for t in tests:
        nums, pivot = t["args"]
        assert len(nums) <= 10000 and INT_MIN <= pivot <= INT_MAX


CHECKS["partition-around-pivot-keep-order"] = (b_pp, lambda r: [gen_arr(r, -4, 4, 0, 12), r.randint(-4, 4)], "exact")
VALIDATE["partition-around-pivot-keep-order"] = v_pp


p = add(
    id="sort-k-colors-in-place", title="Sort K Colors", diff="Medium", topic=TOPIC, tier="common",
    fn="sortKColors", params=[("nums", "int[]"), ("k", "int")], ret="int[]", cmp="exact",
    desc="<p>The array <code>nums</code> holds colours numbered <code>1</code> to <code>k</code>. Sort the array in non-decreasing order of colour and return it.</p>"
         "<pre>nums = [3, 2, 2, 1, 4], k = 4\nresult = [1, 2, 2, 3, 4]</pre>"
         "<p>Do it without a comparison sort and without counting every colour into a table of size <code>k</code>: the intended solution partitions the array in place and runs in O(n log k) time with O(1) extra space (apart from the recursion/stack). It generalises the three-colour Dutch flag problem.</p>",
    constraints=["0 &le; nums.length &le; 10,000", "1 &le; k &le; 10,000", "1 &le; nums[i] &le; k"],
    hints=["With k = 2 this is a single partition: move the 1s to the left and the 2s to the right with two pointers.",
           "For larger k, split the colour range in halves. Partition the array so that colours in the lower half come first, then repeat on each part with the half range.",
           "Recurse (or use an explicit stack) on triples <code>(left, right, lowColor, highColor)</code>. Take <code>mid = (lowColor + highColor) // 2</code>, partition <code>nums[left..right]</code> so that colours <code>&le; mid</code> are on the left, then process the two sides with ranges <code>[lowColor, mid]</code> and <code>[mid + 1, highColor]</code>. Stop when the segment is empty or the colour range has one value."],
    editorial=["This is a recursive version of quicksort's partition where the pivot is a colour boundary instead of an element. Splitting the colour range at its midpoint guarantees a depth of about log<sub>2</sub> k, and at every level each element is touched once by a partition step, so the total work is O(n log k).",
               "A two-pointer partition for the range <code>[l, r]</code>: <code>i</code> moves right while <code>nums[i] &le; mid</code>, <code>j</code> moves left while <code>nums[j] &gt; mid</code>, and if <code>i &lt; j</code> the two elements are swapped. When the pointers cross, <code>[l, j]</code> holds the low colours and <code>[i, r]</code> the high colours.",
               "Counting the occurrences of each colour in an array of size k is also O(n + k) and perfectly fine in practice; the partition approach shines when k is large and memory is tight, or when the elements are heavy records that you do not want to copy."],
    time="O(n log k)", space="O(log k)",
    solution='''def sortKColors(nums, k):
    a = list(nums)
    stack = [(0, len(a) - 1, 1, k)]
    while stack:
        left, right, lo, hi = stack.pop()
        if left >= right or lo >= hi:
            continue
        mid = (lo + hi) // 2
        i, j = left, right
        while i <= j:
            while i <= j and a[i] <= mid:
                i += 1
            while i <= j and a[j] > mid:
                j -= 1
            if i < j:
                a[i], a[j] = a[j], a[i]
                i += 1
                j -= 1
        stack.append((left, j, lo, mid))
        stack.append((i, right, mid + 1, hi))
    return a
''',
    tests=[[[3, 2, 2, 1, 4], 4], [[], 3], [[1], 1], [[5], 9], [[2, 1], 2], [[1, 1, 1], 1], [[3, 3, 3, 3], 3], [[4, 3, 2, 1], 4], [[1, 2, 3, 4], 4],
           [[10, 1, 10, 1, 5, 5, 7], 10], [[6, 5, 4, 3, 2, 1, 6, 5, 4, 3, 2, 1], 6], [[9999, 1, 10000, 5000, 1, 10000], 10000]],
)
_r = rnd(7107)
p["tests"].append([[_r.randint(1, 10) for _ in range(8000)], 10])
p["tests"].append([[_r.randint(1, 10000) for _ in range(4500)], 10000])
p["tests"].append([[_r.choice((1, 4000, 8000)) for _ in range(6000)], 8000])


def b_kc(nums, k):
    return sorted(nums)


def g_kc(r):
    k = r.randint(1, 8)
    return [[r.randint(1, k) for _ in range(r.randint(0, 14))], k]


def v_kc(tests):
    for t in tests:
        nums, k = t["args"]
        assert len(nums) <= 10000 and 1 <= k <= 10000 and all(1 <= x <= k for x in nums)


CHECKS["sort-k-colors-in-place"] = (b_kc, g_kc, "exact")
VALIDATE["sort-k-colors-in-place"] = v_kc


p = add(
    id="alternate-signs-keep-order", title="Alternate Signs, Keep Order", diff="Medium", topic=TOPIC, tier="common",
    fn="alternateSigns", params=[("nums", "int[]")], ret="int[]", cmp="exact",
    desc="<p>Rearrange <code>nums</code> so that non-negative and negative values alternate, starting with a non-negative value. Non-negative values keep their relative order among themselves and negative values keep theirs. When one kind runs out, all remaining values of the other kind are appended at the end in their original order. Return the rearranged array.</p>"
         "<pre>nums = [3, -1, -2, 5, 4, -7, -8, -9]\nresult = [3, -1, 5, -2, 4, -7, -8, -9]</pre>"
         "<pre>nums = [-4, -5, 0]\nresult = [0, -4, -5]</pre>"
         "<p>Zero counts as non-negative.</p>",
    constraints=["0 &le; nums.length &le; 10,000", "-2<sup>31</sup> &le; nums[i] &le; 2<sup>31</sup> - 1"],
    hints=["Sorting by sign does not alternate the values. Think of the answer as built by drawing alternately from two queues: one of the non-negative values, one of the negative values.",
           "Use two read pointers, <code>p</code> over the next non-negative value and <code>q</code> over the next negative value, both advancing through <code>nums</code> from the left.",
           "While both kinds are still available, output one non-negative then one negative (move <code>p</code> and <code>q</code> to the next element of their kind). Afterwards output all remaining elements of whichever kind is left, in order."],
    editorial=["The answer is a merge of two subsequences, the non-negative one and the negative one, taken one element at a time starting with a non-negative. When one subsequence is exhausted the other is simply appended, which is exactly what the statement asks.",
               "Implementing it with two pointers avoids building the lists: <code>p</code> and <code>q</code> are the indices of the next unused non-negative and negative value; after taking one, advance the pointer to the next element of the same sign. Each pointer only moves forward, so the total number of steps is at most 2n.",
               "Time O(n); the output array is the only extra memory, O(n). Doing this in O(1) extra space while preserving order is a famous hard exercise (it needs rotations), which is why this version returns a new array."],
    time="O(n)", space="O(n)",
    solution='''def alternateSigns(nums):
    n = len(nums)
    out = []
    p = q = 0
    while p < n and nums[p] < 0:
        p += 1
    while q < n and nums[q] >= 0:
        q += 1
    take_pos = True
    while p < n and q < n:
        if take_pos:
            out.append(nums[p])
            p += 1
            while p < n and nums[p] < 0:
                p += 1
        else:
            out.append(nums[q])
            q += 1
            while q < n and nums[q] >= 0:
                q += 1
        take_pos = not take_pos
    while p < n:
        if nums[p] >= 0:
            out.append(nums[p])
        p += 1
    while q < n:
        if nums[q] < 0:
            out.append(nums[q])
        q += 1
    return out
''',
    tests=[[[3, -1, -2, 5, 4, -7, -8, -9]], [[-4, -5, 0]], [[]], [[0]], [[-1]], [[1, 2, 3]], [[-1, -2, -3]], [[-1, 1]], [[1, -1]],
           [[1, 2, -1, -2, -3, -4]], [[5, 6, 7, 8, -1, -2]], [[0, -0, -9, 4, INT_MIN, INT_MAX, -3, 2]]],
)
_r = rnd(7108)
p["tests"].append([[_r.randint(-999, 999) for _ in range(6000)]])
p["tests"].append([[-_r.randint(1, 99) for _ in range(2000)] + [_r.randint(0, 99) for _ in range(3000)]])
p["tests"].append([[_r.choice((-1, 1)) * _r.randint(1, 9) for _ in range(5000)]])


def b_as(nums):
    pos = [x for x in nums if x >= 0]
    neg = [x for x in nums if x < 0]
    out = []
    for a, b in zip(pos, neg):
        out += [a, b]
    m = min(len(pos), len(neg))
    return out + pos[m:] + neg[m:]


def v_as(tests):
    for t in tests:
        assert len(t["args"][0]) <= 10000


CHECKS["alternate-signs-keep-order"] = (b_as, lambda r: [gen_arr(r, -4, 4, 0, 12)], "exact")
VALIDATE["alternate-signs-keep-order"] = v_as


p = add(
    id="smallest-left-part-not-exceeding-right", title="Smallest Left Part Not Exceeding the Right", diff="Medium", topic=TOPIC, tier="common",
    fn="leftPartLength", params=[("nums", "int[]")], ret="int", cmp="exact",
    desc="<p>Split <code>nums</code> into two non-empty contiguous parts <code>left</code> and <code>right</code> (a prefix and the remaining suffix) such that <strong>every element of <code>left</code> is less than or equal to every element of <code>right</code></strong>. Return the smallest possible length of <code>left</code>.</p>"
         "<pre>nums = [5, 0, 3, 8, 6]\nresult = 3     (left = [5, 0, 3], right = [8, 6])</pre>"
         "<pre>nums = [1, 1, 1, 0, 6, 12]\nresult = 4</pre>"
         "<p>The input is guaranteed to admit at least one valid split.</p>",
    constraints=["2 &le; nums.length &le; 10,000", "-2<sup>31</sup> &le; nums[i] &le; 2<sup>31</sup> - 1", "At least one valid split exists"],
    hints=["Checking each split point with a fresh max of the prefix and min of the suffix costs O(n<sup>2</sup>). Precompute them.",
           "A split after index <code>i</code> is valid exactly when <code>max(nums[0..i]) &le; min(nums[i+1..n-1])</code>. Build a suffix-minimum array and sweep with a running prefix maximum.",
           "For O(1) extra space keep two values while sweeping: <code>leftMax</code> (maximum of the current left part) and <code>seenMax</code> (maximum of everything scanned). If a new element is smaller than <code>leftMax</code>, it must join the left part: extend the left part to it and set <code>leftMax = seenMax</code>."],
    editorial=["Suffix minima approach: compute <code>sufMin[i] = min(nums[i:])</code> and scan left to right with the running prefix maximum; the first <code>i</code> with <code>prefMax(i) &le; sufMin[i + 1]</code> gives the answer <code>i + 1</code>. This is O(n) time and O(n) space.",
               "The two-pointer version starts with the left part equal to <code>[nums[0]]</code>. Scanning the remaining elements, any element smaller than the current left maximum cannot be in the right part, so the left part must grow to include it, and then the maximum of the left part becomes the largest value seen so far (including those just swallowed). Elements not smaller than <code>leftMax</code> just update <code>seenMax</code>.",
               "A single pass: O(n) time, O(1) extra space. Equal values are allowed on both sides, which is why the comparison with <code>leftMax</code> is strict."],
    time="O(n)", space="O(1)",
    solution='''def leftPartLength(nums):
    left_max = nums[0]
    seen_max = nums[0]
    length = 1
    for i in range(1, len(nums)):
        x = nums[i]
        if x < left_max:
            length = i + 1
            left_max = seen_max
        elif x > seen_max:
            seen_max = x
    return length
''',
    tests=[[[5, 0, 3, 8, 6]], [[1, 1, 1, 0, 6, 12]], [[1, 2]], [[2, 1, 3]], [[1, 1]], [[3, 2, 1, 4]], [[1, 2, 3, 4, 5]], [[4, 3, 2, 1, 5, 5]],
           [[2, 2, 2, 2]], [[-5, -9, -1, -3, 0, 2]], [[INT_MAX, INT_MIN, INT_MAX]], [[6, 1, 9, 1, 7, 9, 8, 10]]],
)
_r = rnd(7109)
p["tests"].append([[_r.randint(0, 5) for _ in range(5)] + [_r.randint(100, 200) for _ in range(5000)]])
p["tests"].append([[x for x in sorted(_r.randint(-1000, 1000) for _ in range(6000))]])
p["tests"].append([[_r.randint(0, 3000) for _ in range(3000)] + [_r.randint(3000, 6000) for _ in range(3000)]])


def b_lp(nums):
    for s in range(1, len(nums)):
        if max(nums[:s]) <= min(nums[s:]):
            return s


def g_lp(r):
    while True:
        a = gen_arr(r, -4, 4, 2, 10)
        if b_lp(a) is not None:
            return [a]


def v_lp(tests):
    for t in tests:
        nums = t["args"][0]
        assert 2 <= len(nums) <= 10000
        pre = nums[0]
        suf = [0] * len(nums)
        m = nums[-1]
        for i in range(len(nums) - 1, -1, -1):
            m = min(m, nums[i])
            suf[i] = m
        ok = False
        for i in range(len(nums) - 1):
            pre = max(pre, nums[i])
            if pre <= suf[i + 1]:
                ok = True
                break
        assert ok, "no valid split"


CHECKS["smallest-left-part-not-exceeding-right"] = (b_lp, g_lp, "exact")
VALIDATE["smallest-left-part-not-exceeding-right"] = v_lp


# ---------------------------------------------------------------- HARD

p = add(
    id="max-chunks-to-sort-with-duplicates", title="Maximum Chunks to Sort an Array", diff="Hard", topic=TOPIC, tier="common",
    fn="maxChunks", params=[("nums", "int[]")], ret="int", cmp="exact",
    desc="<p>Cut <code>nums</code> into contiguous <strong>chunks</strong>. Then sort every chunk on its own (ascending) and glue the chunks back together in their original order. Return the largest number of chunks for which the glued result is the whole array sorted in ascending order.</p>"
         "<pre>nums = [2, 1, 3, 4, 4]\nresult = 4     ([2, 1] [3] [4] [4])</pre>"
         "<pre>nums = [5, 4, 3, 2, 1]\nresult = 1</pre>"
         "<p>Values may repeat, which makes this harder than the permutation version of the puzzle.</p>",
    constraints=["1 &le; nums.length &le; 10,000", "-2<sup>31</sup> &le; nums[i] &le; 2<sup>31</sup> - 1"],
    hints=["A cut between positions <code>i</code> and <code>i + 1</code> is allowed in the final answer only if nothing on the left needs to move past the cut.",
           "The cut is safe exactly when every value on the left is less than or equal to every value on the right: <code>max(nums[0..i]) &le; min(nums[i+1..])</code>. Cuts are independent of one another, so count the safe ones.",
           "Compute suffix minima, sweep with a running prefix maximum, count the indices <code>i &lt; n - 1</code> with <code>prefMax &le; sufMin[i + 1]</code> and answer <code>count + 1</code>. (A monotonic stack that stores the maximum of each chunk gives the same result in one pass.)"],
    editorial=["Sorting chunks independently and concatenating gives the globally sorted array iff, at every boundary, the left side only contains values that are no larger than anything on the right. If some left value were larger than a right value, the sorted chunks would leave those two in the wrong order; conversely, if each boundary satisfies the condition, then the sorted concatenation is sorted.",
               "The conditions at different boundaries are independent, so the maximum number of chunks is one plus the number of positions <code>i</code> (between <code>i</code> and <code>i + 1</code>) with <code>max(nums[0..i]) &le; min(nums[i+1..n-1])</code>. Equality is allowed because equal values can sit on either side of a cut without breaking the order.",
               "Prefix maxima and suffix minima are computed in O(n), so the total is O(n) time and O(n) space. The stack alternative keeps one maximum per chunk: for each element, pop every chunk whose maximum is greater than the element and merge them into one chunk that keeps the largest of the popped maxima."],
    time="O(n)", space="O(n)",
    solution='''def maxChunks(nums):
    n = len(nums)
    suf = [0] * (n + 1)
    suf[n] = float("inf")
    for i in range(n - 1, -1, -1):
        suf[i] = min(suf[i + 1], nums[i])
    chunks = 1
    pref = nums[0]
    for i in range(n - 1):
        pref = max(pref, nums[i])
        if pref <= suf[i + 1]:
            chunks += 1
    return chunks
''',
    tests=[[[2, 1, 3, 4, 4]], [[5, 4, 3, 2, 1]], [[1]], [[1, 1]], [[2, 1]], [[1, 2, 3, 4]], [[4, 3, 2, 1, 5]], [[1, 0, 1, 3, 2]],
           [[3, 3, 3, 3]], [[0, 2, 1, 4, 3, 6, 5]], [[-1, -3, -2, 0, 0, 5, 4]], [[INT_MAX, INT_MIN, INT_MAX, INT_MAX]]],
)
_r = rnd(7110)
p["tests"].append([[_r.randint(i // 4 - 6, i // 4 + 6) for i in range(6000)]])
p["tests"].append([sorted(_r.randint(-500, 500) for _ in range(4000))])
p["tests"].append([[i // 3 if i % 2 else 3000 - i // 3 for i in range(6000)]])


def b_mc(nums):
    n = len(nums)
    target = sorted(nums)
    best = 0
    for mask in range(1 << (n - 1)):
        out = []
        start = 0
        cnt = 1
        for i in range(n - 1):
            if mask >> i & 1:
                out += sorted(nums[start:i + 1])
                start = i + 1
                cnt += 1
        out += sorted(nums[start:])
        if out == target:
            best = max(best, cnt)
    return best


def v_mc(tests):
    for t in tests:
        assert 1 <= len(t["args"][0]) <= 10000


CHECKS["max-chunks-to-sort-with-duplicates"] = (b_mc, lambda r: [gen_arr(r, -3, 3, 1, 9)], "exact")
VALIDATE["max-chunks-to-sort-with-duplicates"] = v_mc


p = add(
    id="min-swaps-sort-three-values", title="Fewest Swaps to Sort 0, 1 and 2", diff="Hard", topic=TOPIC, tier="extra",
    fn="minSwapsSort012", params=[("nums", "int[]")], ret="int", cmp="exact",
    desc="<p>Every element of <code>nums</code> is <code>0</code>, <code>1</code> or <code>2</code>. In one move you may swap <em>any</em> two elements. Return the minimum number of moves needed to sort the array in non-decreasing order.</p>"
         "<pre>nums = [2, 1, 0]\nresult = 1</pre>"
         "<pre>nums = [1, 2, 0]\nresult = 2</pre>"
         "<p>In the second example no single swap works: all three elements are out of place and they are rotated cyclically.</p>",
    constraints=["1 &le; nums.length &le; 10,000", "nums[i] is 0, 1 or 2"],
    hints=["The sorted target is known: it is determined by how many 0s, 1s and 2s there are. Compare each position with the value it should hold.",
           "Count the misplaced positions by pair: <code>c[a][b]</code> = positions that should hold <code>a</code> but hold <code>b</code>. A single swap fixes two positions when it exchanges a <code>(a, b)</code> position with a <code>(b, a)</code> position.",
           "First match as many such pairs as possible: <code>min(c[a][b], c[b][a])</code> for each of the three pairs of values, each costing 1 swap. The positions that remain form 3-cycles (like 0 &rarr; 1 &rarr; 2 &rarr; 0) and every 3-cycle needs 2 swaps."],
    editorial=["Let the sorted array be <code>t</code>. For each position with <code>nums[i] != t[i]</code> record the pair <code>(t[i], nums[i])</code>, meaning 'wants <code>t[i]</code>, has <code>nums[i]</code>'. There are six pair types. A swap of positions of type <code>(a, b)</code> and <code>(b, a)</code> repairs both at the cost of one swap, and no swap can repair more than two positions, so we should take as many such 2-cycles as possible: <code>min(c[a][b], c[b][a])</code> for each pair of values.",
               "After removing these matches, what remains is balanced (every value leaves as many positions as it fills) and for each of the three value pairs only one direction survives. The leftover must therefore decompose into cycles <code>(0,1) (1,2) (2,0)</code> or <code>(0,2) (2,1) (1,0)</code>, each of three misplaced positions. A 3-cycle needs exactly 2 swaps. If <code>r</code> positions are left, the cost is <code>2 * r / 3</code>.",
               "Counting takes one pass, so the algorithm is O(n) time and O(1) space. The total answer is <code>pairs + 2 * (remaining / 3)</code>. Sorting and counting inversions would be wrong here: swaps may exchange any two elements, not only neighbours."],
    time="O(n)", space="O(1)",
    solution='''def minSwapsSort012(nums):
    n = len(nums)
    counts = [nums.count(0), nums.count(1), nums.count(2)]
    target = [0] * counts[0] + [1] * counts[1] + [2] * counts[2]
    c = [[0] * 3 for _ in range(3)]
    for i in range(n):
        if nums[i] != target[i]:
            c[target[i]][nums[i]] += 1
    swaps = 0
    for a in range(3):
        for b in range(a + 1, 3):
            m = min(c[a][b], c[b][a])
            swaps += m
            c[a][b] -= m
            c[b][a] -= m
    rest = sum(c[a][b] for a in range(3) for b in range(3))
    return swaps + 2 * (rest // 3)
''',
    tests=[[[2, 1, 0]], [[1, 2, 0]], [[0]], [[2]], [[0, 1, 2]], [[2, 2, 1, 1, 0, 0]], [[1, 0]], [[2, 0]], [[1, 1, 1]], [[1, 2, 0, 1, 2, 0]],
           [[2, 0, 1, 2, 0, 1, 2, 0, 1]], [[0, 0, 2, 2, 1, 1, 1, 0]]],
)
_r = rnd(7111)
p["tests"].append([[_r.randint(0, 2) for _ in range(8000)]])
p["tests"].append([[1, 2, 0] * 3000])
p["tests"].append([[2] * 2500 + [1] * 2500 + [0] * 2500])

_bfs_cache = {}


def b_ms(nums):
    key = (nums.count(0), nums.count(1), nums.count(2))
    if key not in _bfs_cache:
        goal = tuple([0] * key[0] + [1] * key[1] + [2] * key[2])
        dist = {goal: 0}
        dq = deque([goal])
        while dq:
            s = dq.popleft()
            for i in range(len(s)):
                for j in range(i + 1, len(s)):
                    if s[i] != s[j]:
                        t = list(s)
                        t[i], t[j] = t[j], t[i]
                        t = tuple(t)
                        if t not in dist:
                            dist[t] = dist[s] + 1
                            dq.append(t)
        _bfs_cache[key] = dist
    return _bfs_cache[key][tuple(nums)]


def v_ms(tests):
    for t in tests:
        nums = t["args"][0]
        assert 1 <= len(nums) <= 10000 and all(x in (0, 1, 2) for x in nums)


CHECKS["min-swaps-sort-three-values"] = (b_ms, lambda r: [[r.randint(0, 2) for _ in range(r.randint(1, 8))]], "exact")
VALIDATE["min-swaps-sort-three-values"] = v_ms
