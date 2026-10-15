"""Problems: arrays & hashing, subarrays with prefix hashing (zero-sum, parity, XOR, remainders, balances). See data/lib.py for the registry."""
from lib import add, rnd, CHECKS, VALIDATE, gen_arr  # noqa: F401

T = "Arrays & Hashing"


# ---------------------------------------------------------------- EASY

p = add(
    id="zero-sum-subarray-exists", title="Zero-Sum Subarray Exists", diff="Easy", topic=T, tier="common",
    fn="hasZeroSumSubarray", params=[("nums", "int[]")], ret="bool", cmp="exact",
    desc="<p>Given an integer array <code>nums</code>, decide whether it contains a non-empty contiguous block of elements whose sum is exactly <code>0</code>. Return <code>true</code> if one exists and <code>false</code> otherwise.</p><pre>nums = [4, 2, -3, 1, 6]  -> true   (2 + -3 + 1 = 0)\nnums = [1, 2, 3]         -> false</pre>",
    constraints=["1 &le; nums.length &le; 10,000", "-100,000 &le; nums[i] &le; 100,000"],
    hints=["Checking every block with a running sum costs O(n<sup>2</sup>). Think about what a zero-sum block says about the sums of the elements before it.",
           "Let <code>prefix[i]</code> be the sum of the first <code>i</code> elements. A block from <code>i</code> to <code>j - 1</code> has sum <code>prefix[j] - prefix[i]</code>.",
           "The block sums to zero exactly when two prefix sums are equal. Keep a set of the prefix sums seen so far (starting with 0 for the empty prefix) and stop as soon as one repeats."],
    editorial=["Define the prefix sum <code>s_i</code> as the sum of the first <code>i</code> elements, with <code>s_0 = 0</code>. The block <code>nums[i..j-1]</code> sums to <code>s_j - s_i</code>, so it is zero if and only if <code>s_i = s_j</code> for some <code>i &lt; j</code>. The question therefore becomes: does the list of prefix sums contain a repeated value?",
               "Walk through the array while maintaining the running sum and a hash set of all earlier prefix sums, seeded with 0. If the new running sum is already in the set, a zero-sum block ends here. Otherwise add it and continue. This is one pass: O(n) time and O(n) space. Note that a single element equal to 0 is also detected, since the running sum does not change."],
    time="O(n)", space="O(n)",
    solution='''def hasZeroSumSubarray(nums):
    seen = {0}
    s = 0
    for x in nums:
        s += x
        if s in seen:
            return True
        seen.add(s)
    return False
''',
    tests=[[[4, 2, -3, 1, 6]], [[1, 2, 3]], [[0]], [[5]], [[-1, 1]], [[3, -3, 5]], [[5, 3, -3]], [[1, 2, -4, 1, 7]],
           [[7, -2, -2, 5]], [[100000, -100000]], [[2, 2, 2, -6, 9]], [[-5, 1, 1, 1, 1, 1, 9]]],
)
_r = rnd(8101)


def _distinct_prefix_array(r, n, lim):
    pre = [0] + r.sample(range(1, lim + 1), n)
    return [pre[i] - pre[i - 1] for i in range(1, n + 1)]


_a = _distinct_prefix_array(_r, 5000, 50000)
p["tests"].append([_a])                                  # false, mixed signs, all prefix sums distinct
p["tests"].append([_a + [-sum(_a)]])                     # true only through the very last element
p["tests"].append([[_r.randint(1, 100000) for _ in range(5000)]])  # all positive, false
_c = [_r.randint(-1000, 1000) for _ in range(8000)]
p["tests"].append([_c])                                  # random, true early


def b_zerosum(nums):
    n = len(nums)
    for i in range(n):
        s = 0
        for j in range(i, n):
            s += nums[j]
            if s == 0:
                return True
    return False


def v_zerosum(tests):
    got = set()
    for t in tests:
        a = t["args"][0]
        assert 1 <= len(a) <= 10000 and all(-100000 <= x <= 100000 for x in a)
        got.add(t["expected"])
    assert got == {True, False}, "need both outcomes"


CHECKS["zero-sum-subarray-exists"] = (b_zerosum, lambda r: [gen_arr(r, -4, 4, 1, 9)], "exact")
VALIDATE["zero-sum-subarray-exists"] = v_zerosum

p = add(
    id="count-subarrays-with-odd-sum", title="Count Subarrays with Odd Sum", diff="Easy", topic=T, tier="extra",
    fn="countOddSumSubarrays", params=[("nums", "int[]")], ret="int", cmp="exact",
    desc="<p>Count the non-empty contiguous subarrays of <code>nums</code> whose sum is an odd number. Subarrays at different positions count separately, even if they hold the same values.</p><pre>nums = [1, 3, 5]\nodd sums: [1], [3], [5], [1, 3, 5]   (the sums 1, 3, 5 and 9)\nresult = 4</pre>",
    constraints=["1 &le; nums.length &le; 10,000", "-10,000 &le; nums[i] &le; 10,000", "The answer is at most n(n + 1) / 2, which fits in a 32-bit integer"],
    hints=["Only the parity (even or odd) of each sum matters, so you never need the real values.",
           "A subarray between prefix positions <code>i &lt; j</code> has an odd sum exactly when the prefix sums at <code>i</code> and <code>j</code> have different parities.",
           "Count how many earlier prefix sums (including the empty prefix) are even and how many are odd. For each new prefix, add the count of the opposite parity."],
    editorial=["Let <code>P_j</code> be the parity of the sum of the first <code>j</code> elements, with <code>P_0 = even</code>. The subarray ending at position <code>j</code> and starting after prefix <code>i</code> has sum <code>P_j - P_i</code>, which is odd precisely when the two parities differ.",
               "So sweep the array, keep how many earlier prefixes were even and how many odd (initially one even, the empty prefix), flip the current parity when you meet an odd element, and add the number of earlier prefixes with the opposite parity to the answer. That is O(n) time with O(1) space. Negative numbers work with <code>x % 2</code> in Python, which returns 0 or 1."],
    time="O(n)", space="O(1)",
    solution='''def countOddSumSubarrays(nums):
    even, odd = 1, 0
    parity = 0
    total = 0
    for x in nums:
        parity ^= x & 1
        if parity:
            total += even
            odd += 1
        else:
            total += odd
            even += 1
    return total
''',
    tests=[[[1, 3, 5]], [[2, 4, 6]], [[1]], [[2]], [[-1]], [[-3, 2, 5, -4]], [[1, 1, 1, 1]], [[0, 0, 7, 0, 0]], [[10000, -9999]],
           [[2, 1, 2, 1, 2]], [[1, 2, 3, 4, 5, 6, 7, 8, 9]]],
)
_r = rnd(8102)
p["tests"].append([[_r.randint(-10000, 10000) for _ in range(8000)]])
p["tests"].append([[_r.choice([1, 3, 5, 7, 9999]) for _ in range(8000)]])
p["tests"].append([[2 * _r.randint(-5000, 5000) for _ in range(4000)] + [1] + [2 * _r.randint(-5000, 5000) for _ in range(4000)]])


def b_oddsum(nums):
    n = len(nums)
    c = 0
    for i in range(n):
        s = 0
        for j in range(i, n):
            s += nums[j]
            if s % 2:
                c += 1
    return c


def v_oddsum(tests):
    for t in tests:
        a = t["args"][0]
        assert 1 <= len(a) <= 10000 and all(-10000 <= x <= 10000 for x in a)
        assert t["expected"] <= len(a) * (len(a) + 1) // 2


CHECKS["count-subarrays-with-odd-sum"] = (b_oddsum, lambda r: [gen_arr(r, -6, 6, 1, 10)], "exact")
VALIDATE["count-subarrays-with-odd-sum"] = v_oddsum


# ---------------------------------------------------------------- MEDIUM

p = add(
    id="continuous-subarray-sum-multiple-of-k", title="Subarray Sum Multiple of K", diff="Medium", topic=T, tier="must",
    fn="hasMultipleSubarray", params=[("nums", "int[]"), ("k", "int")], ret="bool", cmp="exact",
    desc="<p>Given an array <code>nums</code> of non-negative integers and a positive integer <code>k</code>, decide whether some contiguous subarray of <strong>length at least 2</strong> has a sum that is a multiple of <code>k</code>. A sum of <code>0</code> counts as a multiple of every <code>k</code>.</p><pre>nums = [23, 2, 4, 6, 7], k = 6  -> true   ([2, 4] sums to 6)\nnums = [23, 2, 6, 4, 7], k = 13 -> false</pre>",
    constraints=["1 &le; nums.length &le; 10,000", "0 &le; nums[i] &le; 10<sup>9</sup>", "1 &le; k &le; 2<sup>31</sup> - 1"],
    hints=["Trying all pairs of ends works in O(n<sup>2</sup>) with prefix sums. Look for a way to ask the question about prefix sums <em>modulo k</em>.",
           "A block from prefix <code>i</code> to prefix <code>j</code> has a sum divisible by <code>k</code> exactly when the two prefix sums leave the same remainder when divided by <code>k</code>.",
           "Store, for each remainder, the <em>earliest</em> prefix index where it appeared (remainder 0 at index 0 before any element). When a remainder repeats, check that the two prefixes are at least 2 apart. Do not overwrite the stored index."],
    editorial=["Let <code>r_i</code> be the prefix sum of the first <code>i</code> elements taken modulo <code>k</code>, with <code>r_0 = 0</code>. The subarray covering elements <code>i..j-1</code> has a sum divisible by <code>k</code> if and only if <code>r_i = r_j</code>. The extra requirement is that the subarray has at least two elements, i.e. <code>j - i &ge; 2</code>.",
               "Keep a dictionary from remainder to the first prefix index that produced it. When the current remainder is already present, the farthest possible partner is the first occurrence, so compare against it: if the gap is at least 2 you are done. If the gap is only 1, keep the old index (do not overwrite it) because the earliest index gives the longest subarray for later matches. One pass, O(n) time, and O(min(n, k)) space."],
    time="O(n)", space="O(min(n, k))",
    solution='''def hasMultipleSubarray(nums, k):
    first = {0: 0}
    s = 0
    for j, x in enumerate(nums, 1):
        s = (s + x) % k
        if s in first:
            if j - first[s] >= 2:
                return True
        else:
            first[s] = j
    return False
''',
    tests=[[[23, 2, 4, 6, 7], 6], [[23, 2, 6, 4, 7], 13], [[5, 0, 0, 0], 3], [[0], 1], [[7], 7], [[5, 2], 7], [[1, 2], 5],
           [[0, 1, 0], 5], [[0, 0], 7], [[3, 3], 6], [[1, 1], 1], [[6, 1, 5], 11], [[2, 3, 1000000000], 2147483647],
           [[1000000000, 1000000000, 1000000000], 1000000000]],
)
_r = rnd(8103)


def _no_multiple_array(r, n, k):
    """Prefix remainders: all distinct except that some neighbours may repeat (so some elements are multiples of k)."""
    res = [0]
    pool = r.sample(range(1, k), n)
    for v in pool:
        res.append(v)
        if r.random() < 0.15:
            res.append(v)
    res = res[:n + 1]
    return [(res[i] - res[i - 1]) % k + k * r.randint(0, 5) for i in range(1, len(res))]


_a = _no_multiple_array(_r, 3000, 5000)
p["tests"].append([_a, 5000])
_a = _no_multiple_array(_r, 2500, 1000003)
p["tests"].append([_a, 1000003])
p["tests"].append([[_r.randint(1, 100000) for _ in range(5000)], 2147483647])
p["tests"].append([[_r.randint(0, 10 ** 9) for _ in range(5000)], 997])


def b_multiple(nums, k):
    n = len(nums)
    for i in range(n):
        s = nums[i]
        for j in range(i + 1, n):
            s += nums[j]
            if s % k == 0:
                return True
    return False


def v_multiple(tests):
    got = set()
    for t in tests:
        a, k = t["args"]
        assert 1 <= len(a) <= 10000 and all(0 <= x <= 10 ** 9 for x in a)
        assert 1 <= k <= 2 ** 31 - 1
        got.add(t["expected"])
    assert got == {True, False}


CHECKS["continuous-subarray-sum-multiple-of-k"] = (
    b_multiple, lambda r: [gen_arr(r, 0, 9, 1, 8), r.randint(1, 12)], "exact")
VALIDATE["continuous-subarray-sum-multiple-of-k"] = v_multiple

p = add(
    id="count-subarrays-with-xor-target", title="Count Subarrays with XOR Equal to Target", diff="Medium", topic=T, tier="common",
    fn="countXorSubarrays", params=[("nums", "int[]"), ("target", "int")], ret="int", cmp="exact",
    desc="<p>Given an array <code>nums</code> of non-negative integers and an integer <code>target</code>, count the non-empty contiguous subarrays whose bitwise XOR of all elements equals <code>target</code>.</p><pre>nums = [4, 2, 2, 6, 4], target = 6\nmatching subarrays: [4, 2], [2, 2, 6], [6], [4, 2, 2, 6, 4]\nresult = 4</pre>",
    constraints=["1 &le; nums.length &le; 10,000", "0 &le; nums[i] &lt; 2<sup>30</sup>", "0 &le; target &lt; 2<sup>30</sup>", "The answer is at most n(n + 1) / 2 and fits in a 32-bit integer"],
    hints=["XOR behaves like addition without carries: it is associative and every value is its own inverse (<code>x ^ x = 0</code>).",
           "Define <code>px[i]</code> as the XOR of the first <code>i</code> elements. The XOR of a block <code>i..j-1</code> is <code>px[j] ^ px[i]</code>.",
           "The block XORs to <code>target</code> exactly when <code>px[i] = px[j] ^ target</code>. Keep a hash map counting earlier prefix XORs (start with <code>{0: 1}</code>) and, for each new prefix, add the count of <code>prefix ^ target</code>."],
    editorial=["Because <code>a ^ a = 0</code>, the XOR of a block equals the XOR of two prefix values: <code>px[j] ^ px[i]</code>. The subarray ending at position <code>j</code> therefore has XOR <code>target</code> for each earlier prefix with value <code>px[j] ^ target</code>.",
               "This is the same idea as counting subarrays with a given sum, with subtraction replaced by XOR. Maintain a counter of prefix XOR values seen so far (the empty prefix, value 0, counts once). For each element update the running XOR, add <code>count[xor ^ target]</code> to the answer, and then record the running XOR. The pass is O(n) time and O(n) space. Note that <code>target = 0</code> needs no special case: you simply count equal prefix XORs."],
    time="O(n)", space="O(n)",
    solution='''def countXorSubarrays(nums, target):
    count = {0: 1}
    px = 0
    total = 0
    for x in nums:
        px ^= x
        total += count.get(px ^ target, 0)
        count[px] = count.get(px, 0) + 1
    return total
''',
    tests=[[[4, 2, 2, 6, 4], 6], [[5, 6, 7, 8, 9], 5], [[0], 0], [[0], 1], [[7], 7], [[1, 1, 1, 1], 0], [[1, 1, 1, 1], 1],
           [[3, 5, 6], 0], [[8, 8, 8], 8], [[1073741823, 1073741823], 0], [[1073741823, 1], 1073741822], [[2, 4, 8, 16], 31]],
)
_r = rnd(8104)
p["tests"].append([[_r.randint(0, 7) for _ in range(8000)], 5])
p["tests"].append([[0] * 5000, 0])
_a = [_r.randint(0, 2 ** 30 - 1) for _ in range(4000)]
_x = 0
for _v in _a[1200:2900]:
    _x ^= _v
p["tests"].append([_a, _x])
p["tests"].append([[_r.randint(0, 1) for _ in range(8000)], 1])


def b_xorcount(nums, target):
    n = len(nums)
    c = 0
    for i in range(n):
        x = 0
        for j in range(i, n):
            x ^= nums[j]
            if x == target:
                c += 1
    return c


def v_xorcount(tests):
    for t in tests:
        a, tg = t["args"]
        assert 1 <= len(a) <= 10000 and all(0 <= x < 2 ** 30 for x in a)
        assert 0 <= tg < 2 ** 30
        assert t["expected"] <= len(a) * (len(a) + 1) // 2


CHECKS["count-subarrays-with-xor-target"] = (
    b_xorcount, lambda r: [gen_arr(r, 0, 7, 1, 10), r.randint(0, 7)], "exact")
VALIDATE["count-subarrays-with-xor-target"] = v_xorcount

p = add(
    id="longest-subarray-with-xor-target", title="Longest Subarray with XOR Equal to Target", diff="Medium", topic=T, tier="extra",
    fn="longestXorSubarray", params=[("nums", "int[]"), ("target", "int")], ret="int", cmp="exact",
    desc="<p>Given an array <code>nums</code> of non-negative integers and an integer <code>target</code>, find the <strong>length</strong> of the longest contiguous subarray whose bitwise XOR equals <code>target</code>. If no subarray qualifies, return <code>0</code>.</p><pre>nums = [3, 1, 2, 7, 4], target = 7\nthe block [3, 1, 2, 7] has XOR 7 (the single element [7] also does, but is shorter)\nresult = 4</pre>",
    constraints=["1 &le; nums.length &le; 10,000", "0 &le; nums[i] &lt; 2<sup>30</sup>", "0 &le; target &lt; 2<sup>30</sup>"],
    hints=["The XOR of a block is the XOR of two prefix values. Which two prefix positions give the longest block for a fixed end?",
           "For an ending position <code>j</code> you need an earlier prefix with value <code>px[j] ^ target</code>, and to make the block as long as possible you want the <em>earliest</em> such prefix.",
           "Store only the first index at which each prefix XOR value occurs (value 0 at index 0). Do not overwrite it when the value repeats. For each <code>j</code>, look up <code>px[j] ^ target</code> and update the best length."],
    editorial=["With prefix XORs <code>px[0..n]</code>, the block between prefixes <code>i &lt; j</code> has XOR <code>px[i] ^ px[j]</code>. We want <code>px[i] ^ px[j] = target</code> with <code>j - i</code> maximal. For a fixed <code>j</code> the partner value is <code>px[j] ^ target</code>, and among all prefixes holding that value the smallest <code>i</code> gives the longest block.",
               "So keep a dictionary of the first occurrence of each prefix XOR. While scanning, look up the partner for the current prefix first, then store the current prefix only if it is new (the lookup first matters when <code>target = 0</code>, where the partner is the prefix itself and must come from an earlier position). O(n) time, O(n) space. The contrasting problem, counting such blocks, stores a count per value instead of the first index."],
    time="O(n)", space="O(n)",
    solution='''def longestXorSubarray(nums, target):
    first = {0: 0}
    px = 0
    best = 0
    for j, x in enumerate(nums, 1):
        px ^= x
        i = first.get(px ^ target)
        if i is not None and j - i > best:
            best = j - i
        if px not in first:
            first[px] = j
    return best
''',
    tests=[[[3, 1, 2, 7, 4], 7], [[1, 2, 3], 0], [[5], 5], [[5], 4], [[0, 0, 0], 0], [[6, 6, 1], 1], [[1, 2, 4, 8], 9], [[4, 4, 4, 4], 4],
           [[9, 9], 9], [[1073741823, 1073741823, 5], 5], [[2, 3, 2, 3, 2], 1], [[7, 1, 6], 0]],
)
_r = rnd(8105)
_a = [_r.randint(0, 2 ** 30 - 1) for _ in range(4000)]
_x = 0
for _v in _a[300:3700]:
    _x ^= _v
p["tests"].append([_a, _x])
p["tests"].append([[_r.randint(0, 3) for _ in range(8000)], 2])
p["tests"].append([[_r.randint(0, 255) for _ in range(5000)], 256 + 7])  # unreachable target, answer 0
p["tests"].append([[_r.randint(0, 1) for _ in range(8000)], 0])


def b_xorlong(nums, target):
    n = len(nums)
    best = 0
    for i in range(n):
        x = 0
        for j in range(i, n):
            x ^= nums[j]
            if x == target and j - i + 1 > best:
                best = j - i + 1
    return best


def v_xorlong(tests):
    for t in tests:
        a, tg = t["args"]
        assert 1 <= len(a) <= 10000 and all(0 <= x < 2 ** 30 for x in a)
        assert 0 <= tg < 2 ** 30
    assert any(t["expected"] == 0 for t in tests) and any(t["expected"] > 0 for t in tests)


CHECKS["longest-subarray-with-xor-target"] = (
    b_xorlong, lambda r: [gen_arr(r, 0, 7, 1, 10), r.randint(0, 7)], "exact")
VALIDATE["longest-subarray-with-xor-target"] = v_xorlong

p = add(
    id="count-subarrays-with-k-odd-numbers", title="Count Subarrays with Exactly K Odd Numbers", diff="Medium", topic=T, tier="common",
    fn="countKOddSubarrays", params=[("nums", "int[]"), ("k", "int")], ret="int", cmp="exact",
    desc="<p>Given an integer array <code>nums</code> and an integer <code>k</code>, count the contiguous subarrays that contain <strong>exactly</strong> <code>k</code> odd numbers. Negative numbers can be odd too (for example <code>-3</code>). The value <code>k = 0</code> asks for subarrays with no odd number at all.</p><pre>nums = [1, 1, 2, 1, 1], k = 3\nsubarrays: [1, 1, 2, 1] and [1, 2, 1, 1]\nresult = 2</pre>",
    constraints=["1 &le; nums.length &le; 10,000", "-100,000 &le; nums[i] &le; 100,000", "0 &le; k &le; nums.length", "The answer fits in a 32-bit integer"],
    hints=["Only odd/even matters, so replace every element by 1 (odd) or 0 (even). The task becomes counting subarrays whose sum is exactly <code>k</code>.",
           "Let <code>c[j]</code> be the number of odd values among the first <code>j</code> elements. A block from prefix <code>i</code> to <code>j</code> holds <code>c[j] - c[i]</code> odd values.",
           "You need <code>c[i] = c[j] - k</code>. Since <code>c</code> only grows in steps of 0 or 1, keep an array <code>ways[v]</code> = how many prefixes have exactly <code>v</code> odd values, and add <code>ways[c - k]</code> at every step."],
    editorial=["After mapping each element to its parity bit, this is the classic 'subarray sum equals k' problem on a 0/1 array. For every ending position <code>j</code> with <code>c</code> odd values so far, the valid starts are the earlier prefixes holding exactly <code>c - k</code> odd values, so we add that count to the answer.",
               "Because the prefix counts are small non-negative integers, an array of size <code>n + 1</code> replaces the hash map. The empty prefix contributes <code>ways[0] = 1</code>. The loop is O(n) time and O(n) space. A sliding-window solution (answer for 'at most k' minus 'at most k - 1') also works, but the counting formulation handles <code>k = 0</code> without special care."],
    time="O(n)", space="O(n)",
    solution='''def countKOddSubarrays(nums, k):
    ways = [0] * (len(nums) + 2)
    ways[0] = 1
    odd = 0
    total = 0
    for x in nums:
        odd += x & 1
        if odd >= k:
            total += ways[odd - k]
        ways[odd] += 1
    return total
''',
    tests=[[[1, 1, 2, 1, 1], 3], [[2, 4, 6], 1], [[2, 4, 6], 0], [[2, 2, 2, 1, 2, 2, 1, 2, 2, 2], 2], [[1], 1], [[1], 0], [[2], 0],
           [[-3, 5, 2, -7], 2], [[-1, -1, -1], 3], [[1, 2, 3, 4, 5], 5], [[100000, -99999], 1], [[0, 0, 1, 0, 0], 1]],
)
_r = rnd(8106)
p["tests"].append([[_r.randint(-100000, 100000) for _ in range(6000)], 100])
p["tests"].append([[2 * _r.randint(0, 40000) if _r.random() < 0.95 else 7 for _ in range(8000)], 0])
p["tests"].append([[_r.choice([1, -3, 99999]) for _ in range(8000)], 1])
p["tests"].append([[_r.randint(0, 9) for _ in range(8000)], 2500])


def b_kodd(nums, k):
    n = len(nums)
    c = 0
    for i in range(n):
        odd = 0
        for j in range(i, n):
            odd += nums[j] % 2
            if odd == k:
                c += 1
    return c


def v_kodd(tests):
    for t in tests:
        a, k = t["args"]
        assert 1 <= len(a) <= 10000 and all(-100000 <= x <= 100000 for x in a)
        assert 0 <= k <= len(a)


CHECKS["count-subarrays-with-k-odd-numbers"] = (
    b_kodd, lambda r: [gen_arr(r, -5, 5, 1, 11), r.randint(0, 6)], "exact")
VALIDATE["count-subarrays-with-k-odd-numbers"] = v_kodd

p = add(
    id="shortest-removal-sum-divisible-by-p", title="Shortest Removal to Make Sum Divisible", diff="Medium", topic=T, tier="extra",
    fn="minRemovalDivisible", params=[("nums", "int[]"), ("p", "int")], ret="int", cmp="exact",
    desc="<p>You may delete one contiguous block of elements (possibly empty) from the array <code>nums</code> of positive integers so that the sum of the <strong>remaining</strong> elements is divisible by <code>p</code>. You are not allowed to delete the whole array.</p><p>Return the minimum number of elements you must delete, or <code>-1</code> if it is impossible.</p><pre>nums = [3, 1, 4, 2], p = 6  -> 1   (delete [4]; the rest sums to 6)\nnums = [6, 3, 5, 2], p = 9  -> 2   (delete [5, 2]; the rest sums to 9)\nnums = [1, 2, 3],    p = 7  -> -1</pre>",
    constraints=["1 &le; nums.length &le; 10,000", "1 &le; nums[i] &le; 10<sup>9</sup>", "1 &le; p &le; 10<sup>9</sup>"],
    hints=["Let <code>need = total % p</code>. If it is 0 the answer is 0. Otherwise you must delete a block whose sum leaves remainder <code>need</code> modulo <code>p</code>.",
           "Use prefix sums modulo <code>p</code>. A block ending at prefix <code>j</code> and starting after prefix <code>i</code> has remainder <code>(r_j - r_i) mod p</code>, which should equal <code>need</code>.",
           "For each <code>j</code>, look up the <em>latest</em> earlier prefix with remainder <code>(r_j - need) mod p</code> in a dictionary (storing the last index for every remainder, remainder 0 at index 0). Minimise <code>j - i</code>, and reject the answer <code>n</code> (whole array)."],
    editorial=["Removing a block changes the total by the block sum, so the remaining sum is divisible by <code>p</code> exactly when the block sum is congruent to <code>need = total mod p</code>. If <code>need = 0</code> nothing has to be removed.",
               "Otherwise scan the prefix remainders <code>r_j</code>. A block ending at prefix <code>j</code> must start right after a prefix <code>i</code> with <code>r_i = (r_j - need) mod p</code>; the shortest block uses the <em>latest</em> such <code>i</code>, so store the most recent index per remainder and update it after the lookup. Track the minimum length. If the best block is the whole array (length n) it is not allowed, so report -1. O(n) time and O(min(n, p)) space."],
    time="O(n)", space="O(min(n, p))",
    solution='''def minRemovalDivisible(nums, p):
    n = len(nums)
    need = sum(nums) % p
    if need == 0:
        return 0
    last = {0: 0}
    r = 0
    best = n
    for j, x in enumerate(nums, 1):
        r = (r + x) % p
        i = last.get((r - need) % p)
        if i is not None and j - i < best:
            best = j - i
        last[r] = j
    return -1 if best == n else best
''',
    tests=[[[3, 1, 4, 2], 6], [[6, 3, 5, 2], 9], [[1, 2, 3], 7], [[1, 2, 3], 3], [[5], 5], [[5], 3], [[1, 1, 1, 1], 3], [[4, 4, 4], 6],
           [[1000000000, 1000000000], 999999999], [[2, 3], 5], [[8, 1, 1, 8], 5], [[1000000000], 1000000000]],
)
_r = rnd(8107)
p["tests"].append([[1] * 7002, 5000])
p["tests"].append([[_r.randint(1, 10) for _ in range(3000)], 1000000000])
p["tests"].append([[_r.randint(1, 10 ** 9) for _ in range(5000)], 1000000000])
p["tests"].append([[_r.randint(1, 100) for _ in range(8000)], 7919])


def b_removal(nums, p):
    n = len(nums)
    total = sum(nums)
    best = None
    for i in range(n):
        s = 0
        for j in range(i, n):
            s += nums[j]
            if (total - s) % p == 0 and (j - i + 1) < n:
                ln = j - i + 1
                if best is None or ln < best:
                    best = ln
    if total % p == 0:
        return 0
    return -1 if best is None else best


def v_removal(tests):
    res = set()
    for t in tests:
        a, p_ = t["args"]
        assert 1 <= len(a) <= 10000 and all(1 <= x <= 10 ** 9 for x in a)
        assert 1 <= p_ <= 10 ** 9
        res.add(t["expected"] == -1)
    assert res == {True, False}


CHECKS["shortest-removal-sum-divisible-by-p"] = (
    b_removal, lambda r: [gen_arr(r, 1, 9, 1, 9), r.randint(1, 13)], "exact")
VALIDATE["shortest-removal-sum-divisible-by-p"] = v_removal

p = add(
    id="longest-well-performing-stretch", title="Longest Well-Performing Stretch", diff="Medium", topic=T, tier="extra",
    fn="longestWellPerformingStretch", params=[("hours", "int[]")], ret="int", cmp="exact",
    desc="<p>The array <code>hours</code> records how many hours an employee worked on each consecutive day. A day is <strong>tiring</strong> if the employee worked strictly more than <code>8</code> hours, otherwise it is a normal day.</p><p>A stretch of consecutive days is <strong>well-performing</strong> if it contains strictly more tiring days than normal days. Return the length of the longest well-performing stretch (<code>0</code> if there is none).</p><pre>hours = [9, 9, 6, 0, 6, 6, 9]\nlongest stretch: [9, 9, 6] (two tiring days, one normal)\nresult = 3</pre>",
    constraints=["1 &le; hours.length &le; 10,000", "0 &le; hours[i] &le; 16"],
    hints=["Convert each day to +1 (tiring) or -1 (normal). A stretch is well-performing exactly when its sum is positive.",
           "With prefix sums <code>s</code>, you want the longest range with <code>s[j] - s[i] &gt; 0</code>. If the whole prefix <code>s[j]</code> is already positive, the stretch can start at day 1.",
           "Otherwise <code>s[j]</code> is zero or negative. Because the prefix moves by only +1 or -1, the earliest earlier prefix that is smaller than <code>s[j]</code> must have the value exactly <code>s[j] - 1</code>. Store the first index of each prefix value in a dictionary."],
    editorial=["Map days to +1/-1 and take prefix sums <code>s</code>. We need the maximum <code>j - i</code> with <code>s[j] &gt; s[i]</code>. If <code>s[j] &gt; 0</code> then <code>i = 0</code> works and the stretch is the whole prefix. If <code>s[j] &le; 0</code>, we need some earlier prefix with a smaller value. Prefix sums change by one unit at a time, so the walk starts at 0, which is at least <code>s[j]</code>, so to reach any smaller value it must first step onto <code>s[j] - 1</code>. Hence the first time the walk hits the value <code>s[j] - 1</code> is the earliest index holding a smaller value.",
               "So record the first index at which each value is seen and, for every <code>j</code>, look up <code>s[j] - 1</code>. One pass, O(n) time and O(n) space. A monotonic stack over prefix sums also solves it but is more code."],
    time="O(n)", space="O(n)",
    solution='''def longestWellPerformingStretch(hours):
    score = 0
    first = {}
    best = 0
    for j, h in enumerate(hours, 1):
        score += 1 if h > 8 else -1
        if score > 0:
            best = j
        else:
            if score not in first:
                first[score] = j
            i = first.get(score - 1)
            if i is not None and j - i > best:
                best = j - i
    return best
''',
    tests=[[[9, 9, 6, 0, 6, 6, 9]], [[6, 6, 6]], [[9]], [[8]], [[9, 6]], [[6, 9, 9]], [[6, 6, 9, 9, 9, 6, 6]], [[9, 6, 9, 6, 9, 6]],
           [[16, 0, 16, 0, 16]], [[6, 9, 6, 9, 9, 6, 6]], [[0, 0, 12, 12, 12, 0]], [[8, 9, 8, 9, 8, 9, 8, 9, 9]]],
)
_r = rnd(8108)
p["tests"].append([[_r.randint(0, 16) for _ in range(8000)]])
p["tests"].append([[_r.choice([6, 12]) for _ in range(8000)]])
p["tests"].append([[6] * 3000 + [10] * 2000 + [6] * 1000])
p["tests"].append([[9 if _r.random() < 0.4 else 4 for _ in range(8000)]])


def b_well(hours):
    n = len(hours)
    best = 0
    for i in range(n):
        s = 0
        for j in range(i, n):
            s += 1 if hours[j] > 8 else -1
            if s > 0 and j - i + 1 > best:
                best = j - i + 1
    return best


def v_well(tests):
    for t in tests:
        a = t["args"][0]
        assert 1 <= len(a) <= 10000 and all(0 <= x <= 16 for x in a)


CHECKS["longest-well-performing-stretch"] = (
    b_well, lambda r: [gen_arr(r, 4, 12, 1, 12)], "exact")
VALIDATE["longest-well-performing-stretch"] = v_well


# ---------------------------------------------------------------- HARD

p = add(
    id="count-subarrays-with-median-k", title="Count Subarrays with Median K", diff="Hard", topic=T, tier="extra",
    fn="countMedianSubarrays", params=[("nums", "int[]"), ("k", "int")], ret="int", cmp="exact",
    desc="<p><code>nums</code> is a permutation of the integers <code>1..n</code> (each appears exactly once) and <code>k</code> is one of those values. Count the non-empty subarrays whose <strong>median equals k</strong>.</p><p>The median of a list is the middle element after sorting it. For an even-length list, take the <em>left</em> of the two middle elements. For example the median of <code>[2, 3, 1, 4]</code> is <code>2</code> and the median of <code>[5, 2, 3]</code> is <code>3</code>.</p><pre>nums = [3, 2, 1, 4, 5], k = 4\nsubarrays: [4], [4, 5], [1, 4, 5]\nresult = 3</pre>",
    constraints=["1 &le; nums.length &le; 10,000", "nums is a permutation of 1..nums.length", "1 &le; k &le; nums.length"],
    hints=["Any qualifying subarray must contain the position of <code>k</code>. Compare every other element only with <code>k</code>: greater, or smaller.",
           "Give each element a score: +1 if greater than k, -1 if smaller, 0 for k itself. A subarray containing k has median k when the total score is 0 (odd length) or 1 (even length, since the left middle must be k).",
           "Split at the position of k. Count, with a hash map, how many ways the left part (ending just before k, possibly empty) can have each score, then for every right part (starting at k, extending right) add the number of left parts that bring the total to 0 or 1."],
    editorial=["Because all values are distinct, 'median is k' depends only on how many elements are greater and how many are smaller than k. If a subarray contains k, let <code>g</code> and <code>s</code> be the counts of greater and smaller elements. The sorted order puts k at index <code>s</code>, and the (left) median is at index <code>(len - 1) / 2</code> with <code>len = g + s + 1</code>. This equals <code>s</code> exactly when <code>g - s</code> is 0 or 1.",
               "Walk left from the position of k, accumulating the balance (+1 for greater, -1 for smaller) and count how many left extensions give each balance (the empty extension has balance 0). Then walk right from k, again accumulating the balance, and for each right extension (including the one that stops at k) add <code>left[-b] + left[1 - b]</code>. The total is O(n) time and O(n) space; a brute force over all subarrays with sorting would take O(n<sup>3</sup> log n)."],
    time="O(n)", space="O(n)",
    solution='''def countMedianSubarrays(nums, k):
    pos = nums.index(k)
    left = {0: 1}
    bal = 0
    for i in range(pos - 1, -1, -1):
        bal += 1 if nums[i] > k else -1
        left[bal] = left.get(bal, 0) + 1
    total = left.get(0, 0) + left.get(1, 0)
    bal = 0
    for i in range(pos + 1, len(nums)):
        bal += 1 if nums[i] > k else -1
        total += left.get(-bal, 0) + left.get(1 - bal, 0)
    return total
''',
    tests=[[[3, 2, 1, 4, 5], 4], [[2, 3, 1], 1], [[1], 1], [[1, 2], 1], [[1, 2], 2], [[2, 1], 2], [[2, 1], 1], [[1, 2, 3], 2],
           [[3, 1, 2], 2], [[4, 3, 2, 1], 3], [[1, 2, 3, 4, 5, 6, 7], 4], [[7, 1, 6, 2, 5, 3, 4], 4], [[5, 4, 3, 2, 1], 5]],
)
_r = rnd(8109)
_a = list(range(1, 6001)); _r.shuffle(_a)
p["tests"].append([_a, 3000])
_a = list(range(1, 6001)); _r.shuffle(_a)
p["tests"].append([_a, 2999])
_a = list(range(1, 8001))
p["tests"].append([_a, 4000])
_a = [v for pair in zip(range(1, 4001), range(8000, 4000, -1)) for v in pair]  # alternates small, large
p["tests"].append([_a, 3000])


def b_median(nums, k):
    n = len(nums)
    c = 0
    for i in range(n):
        for j in range(i, n):
            sub = sorted(nums[i:j + 1])
            if sub[(len(sub) - 1) // 2] == k:
                c += 1
    return c


def g_median(r):
    n = r.randint(1, 9)
    a = list(range(1, n + 1))
    r.shuffle(a)
    return [a, r.randint(1, n)]


def v_median(tests):
    for t in tests:
        a, k = t["args"]
        assert 1 <= len(a) <= 10000 and sorted(a) == list(range(1, len(a) + 1))
        assert 1 <= k <= len(a)


CHECKS["count-subarrays-with-median-k"] = (b_median, g_median, "exact")
VALIDATE["count-subarrays-with-median-k"] = v_median

p = add(
    id="count-submatrices-with-sum-target", title="Count Submatrices with Target Sum", diff="Hard", topic=T, tier="common",
    fn="countSubmatrices", params=[("matrix", "int[][]"), ("target", "int")], ret="int", cmp="exact",
    desc="<p>Given a rectangular grid of integers <code>matrix</code> and an integer <code>target</code>, count the non-empty <strong>submatrices</strong> whose elements add up to <code>target</code>. A submatrix is a block of consecutive rows and consecutive columns; two submatrices are different if their top-left or bottom-right corners differ.</p><pre>matrix = [[1, -1],\n          [-1, 1]], target = 0\nmatching: the two rows, the two columns and the whole 2x2 grid\nresult = 5</pre>",
    constraints=["1 &le; rows, columns &le; 60", "-100 &le; matrix[i][j] &le; 100", "-1,000,000 &le; target &le; 1,000,000", "The answer fits in a 32-bit integer"],
    hints=["Fix the top and bottom rows of the submatrix. What remains is choosing a range of columns.",
           "For a fixed pair of rows, sum each column between them to get a 1D array. A submatrix is then a contiguous subarray of this array.",
           "Counting 1D subarrays with sum exactly <code>target</code> is done with prefix sums and a hash map of how often each prefix sum occurred. Repeat for all O(R<sup>2</sup>) row pairs, extending the column sums as the bottom row moves down."],
    editorial=["Fix the top row <code>t</code> and sweep the bottom row <code>b</code> from <code>t</code> downwards, maintaining <code>col[c]</code> = the sum of column <code>c</code> over rows <code>t..b</code>; adding one row is O(C). Every submatrix with these two row bounds corresponds to a contiguous range of columns, whose sum is a subarray sum of <code>col</code>.",
               "Count subarrays of <code>col</code> with sum <code>target</code> using a dictionary of prefix sums (starting with {0: 1}): for each column prefix <code>P</code>, add <code>seen[P - target]</code> and then record <code>P</code>. This gives O(R<sup>2</sup> C) time and O(C) space, versus O(R<sup>2</sup> C<sup>2</sup>) for a straightforward 2D prefix-sum enumeration. Make rows the smaller dimension in an implementation if you want the best constant factor."],
    time="O(R^2 * C)", space="O(C)",
    solution='''def countSubmatrices(matrix, target):
    R, C = len(matrix), len(matrix[0])
    total = 0
    for top in range(R):
        col = [0] * C
        for bottom in range(top, R):
            row = matrix[bottom]
            seen = {0: 1}
            pre = 0
            for c in range(C):
                col[c] += row[c]
                pre += col[c]
                total += seen.get(pre - target, 0)
                seen[pre] = seen.get(pre, 0) + 1
    return total
''',
    tests=[[[[1, -1], [-1, 1]], 0], [[[5]], 5], [[[5]], 4], [[[0, 0], [0, 0]], 0], [[[1, 2, 3]], 6], [[[1], [2], [3]], 5],
           [[[1, 1, 1], [1, 1, 1], [1, 1, 1]], 4], [[[0, 1, 0], [1, 1, 1], [0, 1, 0]], 0], [[[-1, 2], [3, -4]], 0],
           [[[100, -100], [-100, 100]], 100], [[[2, 2], [2, 2], [2, 2]], 8]],
)
_r = rnd(8110)
p["tests"].append([[[0] * 60 for _ in range(60)], 0])
p["tests"].append([[[_r.randint(-3, 3) for _ in range(60)] for _ in range(60)], 0])
p["tests"].append([[[_r.randint(0, 1) for _ in range(60)] for _ in range(60)], 6])
p["tests"].append([[[_r.randint(-100, 100) for _ in range(60)] for _ in range(60)], 50])
p["tests"].append([[[_r.randint(-5, 5) for _ in range(60)]], 3])
p["tests"].append([[[_r.randint(-5, 5)] for _ in range(60)], 3])


def b_submatrix(matrix, target):
    R, C = len(matrix), len(matrix[0])
    cnt = 0
    for r1 in range(R):
        for r2 in range(r1, R):
            for c1 in range(C):
                for c2 in range(c1, C):
                    s = sum(matrix[i][j] for i in range(r1, r2 + 1) for j in range(c1, c2 + 1))
                    if s == target:
                        cnt += 1
    return cnt


def g_submatrix(r):
    R, C = r.randint(1, 5), r.randint(1, 5)
    return [[[r.randint(-3, 3) for _ in range(C)] for _ in range(R)], r.randint(-4, 4)]


def v_submatrix(tests):
    for t in tests:
        m, tg = t["args"]
        assert 1 <= len(m) <= 60 and 1 <= len(m[0]) <= 60 and all(len(row) == len(m[0]) for row in m)
        assert all(-100 <= v <= 100 for row in m for v in row)
        assert -10 ** 6 <= tg <= 10 ** 6


CHECKS["count-submatrices-with-sum-target"] = (b_submatrix, g_submatrix, "exact")
VALIDATE["count-submatrices-with-sum-target"] = v_submatrix

p = add(
    id="count-palindrome-rearrangeable-subarrays", title="Count Subarrays That Can Form a Palindrome", diff="Hard", topic=T, tier="extra",
    fn="countPalindromeSubarrays", params=[("digits", "int[]")], ret="int", cmp="exact",
    desc="<p>The array <code>digits</code> contains values from <code>0</code> to <code>9</code>. A non-empty subarray is <strong>palindrome-friendly</strong> if its elements can be reordered into a sequence that reads the same forwards and backwards. Count the palindrome-friendly subarrays (different positions count separately).</p><p>Equivalently, in the subarray at most one value occurs an odd number of times.</p><pre>digits = [1, 1, 2]\nsubarrays: [1], [1], [2], [1, 1], [1, 1, 2]\nresult = 5     ([1, 2] is not palindrome-friendly)</pre>",
    constraints=["1 &le; digits.length &le; 10,000", "0 &le; digits[i] &le; 9", "The answer is at most n(n + 1) / 2 and fits in a 32-bit integer"],
    hints=["Only the parity (odd or even) of each value's count matters, not the counts themselves.",
           "Encode the parities of the ten values as a 10-bit mask, flipping one bit per element. The mask of a subarray is the XOR of two prefix masks.",
           "A subarray is palindrome-friendly if its mask is 0 or has exactly one bit set. For each prefix mask <code>m</code>, add the number of earlier prefixes with mask <code>m</code> and with mask <code>m ^ (1 &lt;&lt; b)</code> for each of the 10 bits."],
    editorial=["Let <code>mask_j</code> be the parity mask after the first <code>j</code> elements (bit d is 1 if digit d occurred an odd number of times). The subarray between prefixes <code>i &lt; j</code> has mask <code>mask_i ^ mask_j</code>. It can be rearranged into a palindrome exactly when that mask has at most one set bit.",
               "So for every <code>j</code> we count earlier prefixes <code>i</code> such that <code>mask_i = mask_j</code> (subarray mask 0) or <code>mask_i = mask_j ^ (1 &lt;&lt; b)</code> for one of the 10 bits. Keep a frequency array of size 1024 (seeded with the empty prefix, mask 0 once). Each element does 11 lookups, so the time is O(11 n) = O(n) and the space is O(2<sup>10</sup>). The same trick generalises to any alphabet of size A with O(n A) time and O(2<sup>A</sup>) space."],
    time="O(n * 10)", space="O(1024)",
    solution='''def countPalindromeSubarrays(digits):
    freq = [0] * 1024
    freq[0] = 1
    mask = 0
    total = 0
    for d in digits:
        mask ^= 1 << d
        total += freq[mask]
        for b in range(10):
            total += freq[mask ^ (1 << b)]
        freq[mask] += 1
    return total
''',
    tests=[[[1, 1, 2]], [[5]], [[1, 2]], [[3, 3]], [[0, 1, 2, 3, 4, 5, 6, 7, 8, 9]], [[9, 9, 9, 9]], [[1, 2, 1, 2, 3]], [[0, 0, 0]],
           [[4, 5, 4, 6, 6, 5, 7]], [[9, 0, 9, 0, 9, 0]], [[1, 2, 3, 1, 2, 3]], [[8, 7, 6, 7, 8]]],
)
_r = rnd(8111)
p["tests"].append([[_r.randint(0, 9) for _ in range(8000)]])
p["tests"].append([[_r.randint(0, 1) for _ in range(8000)]])
p["tests"].append([[7] * 8000])
p["tests"].append([[_r.randint(0, 2) for _ in range(8000)]])


def b_pal(digits):
    n = len(digits)
    c = 0
    for i in range(n):
        cnt = [0] * 10
        odd = 0
        for j in range(i, n):
            d = digits[j]
            cnt[d] += 1
            odd += 1 if cnt[d] % 2 else -1
            if odd <= 1:
                c += 1
    return c


def v_pal(tests):
    for t in tests:
        a = t["args"][0]
        assert 1 <= len(a) <= 10000 and all(0 <= x <= 9 for x in a)
        assert t["expected"] <= len(a) * (len(a) + 1) // 2


CHECKS["count-palindrome-rearrangeable-subarrays"] = (
    b_pal, lambda r: [gen_arr(r, 0, r.choice([1, 3, 9]), 1, 12)], "exact")
VALIDATE["count-palindrome-rearrangeable-subarrays"] = v_pal
