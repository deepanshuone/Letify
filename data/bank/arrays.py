"""Problems: arrays. See data/lib.py for the registry."""
from collections import Counter

from lib import add, rnd, CHECKS, VALIDATE, gen_arr  # noqa: F401

INT_MIN, INT_MAX = -(2 ** 31), 2 ** 31 - 1


# ---------------------------------------------------------------- EASY

p = add(
    id="majority-element", title="Majority Element", diff="Easy", topic="Arrays & Hashing",
    fn="majorityElement", params=[("nums", "int[]")], ret="int", cmp="exact",
    desc="<p>Given an integer array <code>nums</code> of length <code>n</code>, return the value that appears more than <code>n / 2</code> times.</p><p>The input is guaranteed to contain such a value, so there is always exactly one answer. A solution that uses O(1) extra space is possible.</p>",
    constraints=["1 &le; nums.length &le; 10,000", "-2<sup>31</sup> &le; nums[i] &le; 2<sup>31</sup> - 1", "A value occurring more than nums.length / 2 times always exists"],
    hints=["Counting every value with a hash map works. Can you do it without the map?",
           "The majority value outnumbers all the other values put together.",
           "Keep one candidate and a counter: same value as the candidate adds one, a different value subtracts one, and a counter of zero lets the next element become the candidate."],
    editorial=["Use the Boyer-Moore voting idea. Hold a candidate and a counter. For each element, if the counter is zero take the element as the new candidate; then add one if it equals the candidate and subtract one otherwise. Every subtraction cancels one majority element against one non-majority element, and since the majority has more than half of all elements, it is the one left standing.",
               "A hash map of counts is simpler and also O(n) time, at the cost of O(n) space. Sorting the array and reading the middle element works too, because the majority value must cover the middle position, but it costs O(n log n)."],
    time="O(n)", space="O(1)",
    solution='''def majorityElement(nums):
    candidate = nums[0]
    count = 0
    for x in nums:
        if count == 0:
            candidate = x
        count += 1 if x == candidate else -1
    return candidate
''',
    tests=[[[3, 2, 3]], [[2, 2, 1, 1, 1, 2, 2]], [[5]], [[4, 4]], [[-7, 3, -7, 3, -7]], [[1, 2, 2, 1, 1]],
           [[1, 2, 3, 3, 3, 3]], [[INT_MIN, INT_MAX, INT_MIN]], [[0, 0, 0, 0]]],
)
_r = rnd(101)
_a = [42] * 5000 + [_r.randint(-99, 99) for _ in range(4999)]; _r.shuffle(_a)
p["tests"].append([_a])
_a = [INT_MAX] * 1001 + [_r.randint(INT_MIN, INT_MAX) for _ in range(1000)]; _r.shuffle(_a)
p["tests"].append([_a])
_a = [7] * 5001 + [8] * 2500 + [9] * 2499; _r.shuffle(_a)
p["tests"].append([_a])


def b_majority(nums):
    n = len(nums)
    for x in nums:
        if nums.count(x) * 2 > n:
            return x


def g_majority(r):
    n = r.randint(1, 9)
    m = r.randint(-3, 3)
    a = [m] * (n // 2 + 1) + [r.randint(-3, 3) for _ in range(n - n // 2 - 1)]
    r.shuffle(a)
    return a


def v_majority(tests):
    for t in tests:
        nums = t["args"][0]
        assert 1 <= len(nums) <= 10000
        assert nums.count(t["expected"]) * 2 > len(nums), "no majority"


CHECKS["majority-element"] = (b_majority, lambda r: [g_majority(r)], "exact")
VALIDATE["majority-element"] = v_majority

p = add(
    id="single-number", title="Single Number", diff="Easy", topic="Math & Bit Manipulation",
    fn="singleNumber", params=[("nums", "int[]")], ret="int", cmp="exact",
    desc="<p>In the integer array <code>nums</code>, every value appears exactly twice except for one value that appears exactly once. Return that single value.</p><p>Aim for O(n) time and O(1) extra space.</p>",
    constraints=["1 &le; nums.length &le; 9,999 and nums.length is odd", "-2<sup>31</sup> &le; nums[i] &le; 2<sup>31</sup> - 1", "Exactly one value appears once; all others appear exactly twice"],
    hints=["A hash set or a count map solves it, but uses O(n) memory.",
           "What happens when you combine a number with itself using XOR (<code>^</code>)? And with 0?",
           "XOR is commutative and associative, so XOR-ing the whole array cancels every pair and leaves the single value."],
    editorial=["For any x, <code>x ^ x = 0</code> and <code>x ^ 0 = x</code>. XOR also does not care about order. So XOR-ing all elements together makes each pair vanish and leaves exactly the value that has no partner.",
               "The set approach (add on first sight, remove on second) or a sum trick such as <code>2 * sum(set(nums)) - sum(nums)</code> also works, but both need O(n) extra memory and the sum version can overflow in fixed-width integer types. XOR never overflows."],
    time="O(n)", space="O(1)",
    solution='''def singleNumber(nums):
    result = 0
    for x in nums:
        result ^= x
    return result
''',
    tests=[[[2, 2, 1]], [[4, 1, 2, 1, 2]], [[1]], [[-1, -1, -5]], [[0, 9, 9]], [[INT_MIN, 3, 3]],
           [[INT_MAX, INT_MIN, INT_MAX]], [[5, -5, 7, 5, 7]], [[10, 20, 30, 20, 10, 40, 30]]],
)
_r = rnd(102)
_v = _r.sample(range(-999, 999), 1500)
_a = _v + _v[1:]; _r.shuffle(_a)  # _v[0] is the single one
p["tests"].append([_a])
_v = _r.sample(range(INT_MIN, INT_MAX), 1000)
_a = _v + _v[:-1]; _r.shuffle(_a)
p["tests"].append([_a])


def b_single(nums):
    for x in nums:
        if nums.count(x) == 1:
            return x


def g_single(r):
    v = r.sample(range(-20, 20), r.randint(1, 6))
    a = v + v[1:]
    r.shuffle(a)
    return a


def v_single(tests):
    for t in tests:
        nums = t["args"][0]
        assert len(nums) % 2 == 1 and len(nums) <= 9999
        c = Counter(nums)
        assert sorted(c.values()).count(1) == 1 and all(v in (1, 2) for v in c.values())


CHECKS["single-number"] = (b_single, lambda r: [g_single(r)], "exact")
VALIDATE["single-number"] = v_single

p = add(
    id="missing-number", title="Missing Number", diff="Easy", topic="Math & Bit Manipulation",
    fn="missingNumber", params=[("nums", "int[]")], ret="int", cmp="exact",
    desc="<p>The array <code>nums</code> holds <code>n</code> distinct integers, each taken from the range <code>0..n</code> inclusive. That range has <code>n + 1</code> numbers, so exactly one of them is absent. Return the absent number.</p><p>The array may be in any order. Try to use O(1) extra space.</p>",
    constraints=["0 &le; nums.length &le; 10,000", "0 &le; nums[i] &le; nums.length", "All values are distinct"],
    hints=["Putting everything in a set and testing 0..n works. Is there a way to avoid the set?",
           "You know which numbers <em>should</em> be there: all of 0..n. Compare that with what <em>is</em> there.",
           "Either subtract <code>sum(nums)</code> from <code>n(n+1)/2</code>, or XOR all indices 0..n together with all values."],
    editorial=["The sum of 0..n is <code>n(n+1)/2</code>. Subtract the sum of the array and the difference is the missing number. In fixed-width languages, the sum stays tiny for n &le; 10,000, so there is no overflow concern here.",
               "A more overflow-proof variant XORs every index from 0 to n with every array value; each present number appears twice and cancels, leaving the missing one. Sorting and looking for the first index where <code>nums[i] != i</code> also works at O(n log n)."],
    time="O(n)", space="O(1)",
    solution='''def missingNumber(nums):
    n = len(nums)
    result = n
    for i, x in enumerate(nums):
        result ^= i ^ x
    return result
''',
    tests=[[[3, 0, 1]], [[0, 1]], [[9, 6, 4, 2, 3, 5, 7, 0, 1]], [[]], [[0]], [[1]], [[1, 2, 3]], [[0, 1, 2]],
           [[4, 2, 0, 1]], [[1, 0, 3, 4, 5, 6]]],
)
_r = rnd(103)
_a = list(range(10001)); _a.remove(4321); _r.shuffle(_a)
p["tests"].append([_a])
_a = list(range(1001)); _a.remove(0); _r.shuffle(_a)
p["tests"].append([_a])
_a = list(range(1001)); _a.remove(1000); _r.shuffle(_a)
p["tests"].append([_a])


def b_missing(nums):
    for x in range(len(nums) + 1):
        if x not in nums:
            return x


def g_missing(r):
    n = r.randint(0, 9)
    a = list(range(n + 1))
    a.remove(r.randint(0, n))
    r.shuffle(a)
    return a


def v_missing(tests):
    for t in tests:
        nums = t["args"][0]
        n = len(nums)
        assert len(set(nums)) == n and all(0 <= x <= n for x in nums)


CHECKS["missing-number"] = (b_missing, lambda r: [g_missing(r)], "exact")
VALIDATE["missing-number"] = v_missing

p = add(
    id="valid-palindrome", title="Valid Palindrome", diff="Easy", topic="Two Pointers",
    fn="isPalindrome", params=[("s", "string")], ret="bool", cmp="exact",
    desc="<p>The string <code>s</code> contains letters (upper or lower case), digits and the dash character <code>-</code>. Ignore every dash and ignore the difference between upper and lower case. Return <code>true</code> if what remains reads the same forwards and backwards, otherwise return <code>false</code>.</p><p>A string with nothing left after ignoring dashes counts as a palindrome.</p>",
    constraints=["0 &le; s.length &le; 10,000", "s contains only letters, digits and '-'"],
    hints=["You could build a cleaned copy and compare it with its reverse. Can you compare in place instead?",
           "Put one pointer at each end and compare the characters they point to.",
           "Before each comparison, move a pointer inward while it sits on a dash. Compare the lower-cased characters."],
    editorial=["Start with <code>i = 0</code> and <code>j = n - 1</code>. Move <code>i</code> forward while <code>s[i]</code> is a dash, and <code>j</code> backward while <code>s[j]</code> is a dash. If the pointers have not crossed, the lower-cased characters must match; if they do not, return false. Otherwise step both inward and repeat until the pointers meet.",
               "Building the cleaned, lower-cased string and comparing it with its reverse is just as correct and easier to write, but it allocates O(n) extra memory. The two-pointer version uses O(1) extra space and stops at the first mismatch."],
    time="O(n)", space="O(1)",
    solution='''def isPalindrome(s):
    i, j = 0, len(s) - 1
    while i < j:
        if s[i] == '-':
            i += 1
        elif s[j] == '-':
            j -= 1
        else:
            if s[i].lower() != s[j].lower():
                return False
            i += 1
            j -= 1
    return True
''',
    tests=[["A-man-a-plan-a-canal-Panama"], ["race-a-car"], ["-"], [""], ["a"], ["Aa"], ["ab"], ["--a--b--B--A--"],
           ["12-3-21"], ["0P"], ["ab-ba-x"], ["----"]],
)
_r = rnd(104)
_ALNUM = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"


def _make_pal(r, half, dash_p=0.3):
    base = [r.choice(_ALNUM) for _ in range(half)]
    mid = [r.choice(_ALNUM)] if r.random() < 0.5 else []
    full = base + mid + [c.swapcase() if r.random() < 0.5 else c for c in reversed(base)]
    out = []
    for c in full:
        while r.random() < dash_p:
            out.append("-")
        out.append(c)
    return out


_a = _make_pal(_r, 3000)
p["tests"].append(["".join(_a)])
_a = _make_pal(_r, 3000)
_alnum_idx = [k for k, c in enumerate(_a) if c != "-"]
_k = _alnum_idx[len(_alnum_idx) // 3]
_a[_k] = "R" if _a[_k].lower() == "q" else "Q"  # one mismatch, far from the centre
p["tests"].append(["".join(_a)])
_a = _make_pal(_r, 4900, 0.02)
p["tests"].append(["".join(_a)[:10000]])
p["tests"].append(["-" * 10000])


def b_pal(s):
    cleaned = [c.lower() for c in s if c != "-"]
    return cleaned == cleaned[::-1]


def g_pal(r):
    if r.random() < 0.5:
        return "".join(_make_pal(r, r.randint(0, 4), 0.3))
    return "".join(r.choice("aAbB1-") for _ in range(r.randint(0, 8)))


def v_pal(tests):
    for t in tests:
        s = t["args"][0]
        assert len(s) <= 10000 and all(c.isalnum() and c.isascii() or c == "-" for c in s)


CHECKS["valid-palindrome"] = (b_pal, lambda r: [g_pal(r)], "exact")
VALIDATE["valid-palindrome"] = v_pal

p = add(
    id="is-subsequence", title="Is Subsequence", diff="Easy", topic="Two Pointers",
    fn="isSubsequence", params=[("s", "string"), ("t", "string")], ret="bool", cmp="exact",
    desc="<p>Return <code>true</code> if string <code>s</code> is a subsequence of string <code>t</code>, and <code>false</code> otherwise.</p><p>A subsequence is obtained by deleting zero or more characters from <code>t</code> without changing the order of the characters that remain. The empty string is a subsequence of every string.</p>",
    constraints=["0 &le; s.length, t.length &le; 10,000", "s and t contain only lowercase English letters"],
    hints=["Try to match the characters of s inside t one after the other, in order.",
           "Use a pointer <code>i</code> into s. Scan t from left to right.",
           "Whenever <code>t[j] == s[i]</code>, advance i. At the end, s is a subsequence exactly when i reached the length of s."],
    editorial=["Walk through <code>t</code> once. Keep an index <code>i</code> of the next character of <code>s</code> still to be matched. If the current character of <code>t</code> equals <code>s[i]</code>, matching greedily is always safe, so increment <code>i</code>. If <code>i</code> reaches <code>len(s)</code> every character was matched in order.",
               "Matching each character at its earliest possible position never hurts later characters, which is why the greedy scan is correct. The cost is a single pass over t. (If you had to answer many queries against the same t, you would precompute for each position the next occurrence of each letter instead.)"],
    time="O(n)", space="O(1)",
    solution='''def isSubsequence(s, t):
    i = 0
    for c in t:
        if i < len(s) and c == s[i]:
            i += 1
    return i == len(s)
''',
    tests=[["abc", "ahbgdc"], ["axc", "ahbgdc"], ["", "ahbgdc"], ["", ""], ["a", ""], ["a", "a"], ["b", "a"],
           ["abc", "cba"], ["aaa", "aa"], ["aab", "abab"], ["abc", "abc"], ["abcd", "abc"]],
)
_r = rnd(105)
_t = "".join(_r.choice("abcdefghij") for _ in range(10000))
_keep = sorted(_r.sample(range(10000), 3000))
p["tests"].append(["".join(_t[k] for k in _keep), _t])
_keep = sorted(_r.sample(range(10000), 3000))
_s = [_t[k] for k in _keep]; _s[-1] = "z"
p["tests"].append(["".join(_s), _t])
p["tests"].append(["a" * 5000, "a" * 4999])
p["tests"].append(["a" * 5000, "a" * 5000 + "b" * 5000])


def b_subseq(s, t):
    n = len(t)
    for mask in range(1 << n):
        if "".join(t[i] for i in range(n) if mask >> i & 1) == s:
            return True
    return False


def g_subseq(r):
    t = "".join(r.choice("abc") for _ in range(r.randint(0, 9)))
    if r.random() < 0.5:
        s = "".join(c for c in t if r.random() < 0.6)
    else:
        s = "".join(r.choice("abc") for _ in range(r.randint(0, 4)))
    return [s, t]


CHECKS["is-subsequence"] = (b_subseq, g_subseq, "exact")


# -------------------------------------------------------------- MEDIUM

p = add(
    id="top-k-frequent-elements", title="Top K Frequent Elements", diff="Medium", topic="Arrays & Hashing",
    fn="topKFrequent", params=[("nums", "int[]"), ("k", "int")], ret="int[]", cmp="flat",
    desc="<p>Given an integer array <code>nums</code> and an integer <code>k</code>, return the <code>k</code> distinct values that occur most often in <code>nums</code>. The values may be returned in any order.</p><p>The input is chosen so that the answer is unique: the <code>k</code>-th most frequent value occurs strictly more often than the next most frequent value (if there is one). Your running time should be better than O(n log n).</p>",
    constraints=["1 &le; nums.length &le; 10,000", "-10<sup>9</sup> &le; nums[i] &le; 10<sup>9</sup>", "1 &le; k &le; number of distinct values in nums", "The k-th most frequent value is strictly more frequent than the (k+1)-th, so the answer is unique"],
    hints=["First work out how many times each value occurs. A hash map does that in one pass.",
           "Sorting the distinct values by count costs O(d log d). Notice that a count is never larger than n, the length of the array.",
           "Make an array of buckets where bucket c holds every value that occurs exactly c times, then read the buckets from c = n down to 1 until you have collected k values."],
    editorial=["Count occurrences with a hash map. Then use bucket sort on the counts: create n + 1 lists and put each value into the list indexed by its count. Walk the lists from the largest index downward and append values to the answer until it contains k of them. Every step is linear, so the total is O(n).",
               "A min-heap of size k over (count, value) pairs gives O(n log k), which is better when k is small and the number of distinct values is large. Sorting all distinct values by count is the simplest approach at O(n log n)."],
    time="O(n)", space="O(n)",
    solution='''def topKFrequent(nums, k):
    count = {}
    for x in nums:
        count[x] = count.get(x, 0) + 1
    buckets = [[] for _ in range(len(nums) + 1)]
    for x, c in count.items():
        buckets[c].append(x)
    res = []
    for c in range(len(nums), 0, -1):
        for x in buckets[c]:
            res.append(x)
            if len(res) == k:
                return res
    return res
''',
    tests=[[[1, 1, 1, 2, 2, 3], 2], [[1], 1], [[4, 4, 4, 5, 5, 6, 7], 2], [[1, 2, 3], 3], [[5, 5, 5, 5, 8], 1],
           [[-1, -1, -2, -2, -2, 9], 2], [[INT_MIN, INT_MAX, INT_MAX, INT_MIN, INT_MIN, 0], 2],
           [[7, 7, 7, 2, 2, 3, 3, 4], 3], [[9, 9, 9, 9], 1]],
)


def make_topk(r, d, maxf, lo, hi):
    """d distinct values with random frequencies; k is chosen so the answer set is unique."""
    vals = r.sample(range(lo, hi + 1), d)
    freqs = [r.randint(1, maxf) for _ in range(d)]
    order = sorted(range(d), key=lambda i: -freqs[i])
    fs = [freqs[i] for i in order]
    ks = [i for i in range(1, d + 1) if i == d or fs[i - 1] > fs[i]]
    nums = []
    for v, f in zip(vals, freqs):
        nums += [v] * f
    r.shuffle(nums)
    return nums, r.choice(ks)


_r = rnd(106)
p["tests"].append(list(make_topk(_r, 400, 40, -999, 999)))
p["tests"].append(list(make_topk(_r, 800, 5, -10 ** 9, 10 ** 9)))
p["tests"].append(list(make_topk(_r, 50, 150, -99, 99)))


def b_topk(nums, k):
    vals = set(nums)
    cnt = {x: nums.count(x) for x in vals}
    return [x for x in vals if sum(1 for y in vals if cnt[y] > cnt[x]) < k]


def v_topk(tests):
    for t in tests:
        nums, k = t["args"]
        fs = sorted(Counter(nums).values(), reverse=True)
        assert 1 <= len(nums) <= 10000 and 1 <= k <= len(fs)
        assert k == len(fs) or fs[k - 1] > fs[k], "top-k answer is not unique"
        assert len(t["expected"]) == k


CHECKS["top-k-frequent-elements"] = (b_topk, lambda r: list(make_topk(r, r.randint(1, 6), 4, -5, 5)), "flat")
VALIDATE["top-k-frequent-elements"] = v_topk

p = add(
    id="two-sum-ii-sorted-input", title="Two Sum II (Sorted Input)", diff="Medium", topic="Two Pointers",
    fn="twoSumSorted", params=[("numbers", "int[]"), ("target", "int")], ret="int[]", cmp="exact",
    desc="<p>The array <code>numbers</code> is sorted in non-decreasing order. Find the two elements at different positions whose sum equals <code>target</code>, and return their <strong>1-based</strong> positions <code>[i, j]</code> with <code>i &lt; j</code>.</p><p>Exactly one such pair of positions exists. Use only O(1) extra space.</p>",
    constraints=["2 &le; numbers.length &le; 10,000", "-10<sup>9</sup> &le; numbers[i] &le; 10<sup>9</sup>, sorted in non-decreasing order", "Exactly one pair of positions i &lt; j has numbers[i] + numbers[j] = target"],
    hints=["A hash map would work, but it needs extra space and ignores that the array is sorted.",
           "Look at the smallest and the largest element together. Is their sum too small, too large, or just right?",
           "Put one pointer at each end. If the sum is too small, move the left pointer right; if too large, move the right pointer left."],
    editorial=["Keep <code>lo = 0</code> and <code>hi = n - 1</code>. If <code>numbers[lo] + numbers[hi]</code> equals the target, return the 1-based positions. If it is smaller, the element at <code>lo</code> cannot belong to any pair with a partner at or before <code>hi</code> (even the largest partner is not enough), so move <code>lo</code> right. If it is larger, symmetrically move <code>hi</code> left.",
               "Every step discards one index, so the scan is O(n) time with two integer variables of extra space. Binary searching the partner of each element is O(n log n), and a hash map is O(n) time but O(n) space; the two-pointer sweep is the only one that is both fast and constant-memory."],
    time="O(n)", space="O(1)",
    solution='''def twoSumSorted(numbers, target):
    lo, hi = 0, len(numbers) - 1
    while lo < hi:
        total = numbers[lo] + numbers[hi]
        if total == target:
            return [lo + 1, hi + 1]
        if total < target:
            lo += 1
        else:
            hi -= 1
    return []
''',
    tests=[[[2, 7, 11, 15], 9], [[2, 3, 4], 6], [[-1, 0], -1], [[1, 2, 2, 4], 4],
           [[0, 0, 3, 4], 0], [[-10, -3, 2, 8, 20], 17], [[-5, -4, -3, -2], -9],
           [[1, 5, 9, 14, 30], 44], [[-10 ** 9, -5, 0, 7, 10 ** 9], 10 ** 9 + 7]],
)


def pair_count(nums, t):
    c = Counter(nums)
    tot = 0
    for x, cx in c.items():
        y = t - x
        if y == x:
            tot += cx * (cx - 1) // 2
        elif x < y and y in c:
            tot += cx * c[y]
    return tot


def make_pair_case(r, n, lo, hi, distinct):
    while True:
        if distinct:
            nums = sorted(r.sample(range(lo, hi + 1), n))
        else:
            nums = sorted(r.randint(lo, hi) for _ in range(n))
        i, j = sorted(r.sample(range(n), 2))
        t = nums[i] + nums[j]
        if pair_count(nums, t) == 1:
            return nums, t


_r = rnd(107)
p["tests"].append(list(make_pair_case(_r, 2000, -10 ** 9, 10 ** 9, True)))
p["tests"].append(list(make_pair_case(_r, 5000, -10 ** 6, 10 ** 6, True)))
p["tests"].append(list(make_pair_case(_r, 800, -10 ** 9, 10 ** 9, True)))
p["tests"].append([[-10 ** 9, 10 ** 9], 0])


def b_twosum2(numbers, target):
    found = [[i + 1, j + 1] for i in range(len(numbers)) for j in range(i + 1, len(numbers)) if numbers[i] + numbers[j] == target]
    assert len(found) == 1
    return found[0]


def g_twosum2(r):
    while True:
        n = r.randint(2, 8)
        nums = sorted(r.randint(-6, 6) for _ in range(n))
        i, j = sorted(r.sample(range(n), 2))
        t = nums[i] + nums[j]
        if sum(1 for a in range(n) for b in range(a + 1, n) if nums[a] + nums[b] == t) == 1:
            return [nums, t]


def v_twosum2(tests):
    for t in tests:
        nums, target = t["args"]
        assert 2 <= len(nums) <= 10000 and nums == sorted(nums)
        assert all(-10 ** 9 <= x <= 10 ** 9 for x in nums)
        assert pair_count(nums, target) == 1, "not exactly one pair"
        i, j = t["expected"]
        assert 1 <= i < j <= len(nums) and nums[i - 1] + nums[j - 1] == target


CHECKS["two-sum-ii-sorted-input"] = (b_twosum2, g_twosum2, "exact")
VALIDATE["two-sum-ii-sorted-input"] = v_twosum2

p = add(
    id="find-minimum-in-rotated-sorted-array", title="Find Minimum in Rotated Sorted Array", diff="Medium", topic="Binary Search",
    fn="findMin", params=[("nums", "int[]")], ret="int", cmp="exact",
    desc="<p>An array of distinct integers that was sorted in ascending order has been rotated: some number of elements from the front were moved to the back, keeping their order. For example <code>[0,1,2,4,5,6,7]</code> rotated by 4 becomes <code>[5,6,7,0,1,2,4]</code>. A rotation by 0 leaves the array unchanged.</p><p>Given the rotated array <code>nums</code>, return its minimum value. Your solution must run in O(log n) time.</p>",
    constraints=["1 &le; nums.length &le; 10,000", "All values are distinct", "-2<sup>31</sup> &le; nums[i] &le; 2<sup>31</sup> - 1", "nums is a sorted array rotated by some amount between 0 and nums.length - 1"],
    hints=["Scanning for the smallest value is O(n). The sorted structure should let you skip half of the array each time.",
           "Compare the middle element with the last element. Which side of the middle can the minimum be on?",
           "If <code>nums[mid] &gt; nums[hi]</code> the minimum is strictly to the right of mid; otherwise it is at mid or to its left."],
    editorial=["Maintain a range <code>[lo, hi]</code> that is guaranteed to contain the minimum. Look at <code>mid</code>. If <code>nums[mid] &gt; nums[hi]</code>, the rotation point lies between mid and hi, so the minimum is to the right: set <code>lo = mid + 1</code>. Otherwise the segment from mid to hi is sorted, so the minimum is at mid or earlier: set <code>hi = mid</code>. When lo equals hi, that index holds the minimum.",
               "The range halves every step, giving O(log n). Comparing with <code>nums[hi]</code> instead of <code>nums[lo]</code> avoids a special case for arrays that were not rotated at all. Distinct values matter: with duplicates the comparison can be a tie and the halving argument breaks down."],
    time="O(log n)", space="O(1)",
    solution='''def findMin(nums):
    lo, hi = 0, len(nums) - 1
    while lo < hi:
        mid = (lo + hi) // 2
        if nums[mid] > nums[hi]:
            lo = mid + 1
        else:
            hi = mid
    return nums[lo]
''',
    tests=[[[3, 4, 5, 1, 2]], [[4, 5, 6, 7, 0, 1, 2]], [[2, 1]], [[11, 13, 15, 17]], [[1]], [[1, 2]], [[5, 1, 2, 3, 4]],
           [[2, 3, 4, 5, 1]], [[-3, -2, -1, -10, -5]], [[INT_MAX, INT_MIN]], [[0, INT_MAX, INT_MIN]], [[10, 20, 30, 40, 50, 60, 5]]],
)


def rotated(r, n, lo, hi):
    a = sorted(r.sample(range(lo, hi + 1), n))
    k = r.randint(0, n - 1)
    return a[k:] + a[:k]


_r = rnd(108)
p["tests"].append([rotated(_r, 6000, -30000, 30000)])
_a = sorted(_r.sample(range(INT_MIN, INT_MAX), 800))
p["tests"].append([_a[1:] + _a[:1]])
p["tests"].append([_a[-1:] + _a[:-1]])
p["tests"].append([_a])


def b_findmin(nums):
    return sorted(nums)[0]


def v_findmin(tests):
    for t in tests:
        nums = t["args"][0]
        assert 1 <= len(nums) <= 10000 and len(set(nums)) == len(nums)
        descents = [i for i in range(len(nums) - 1) if nums[i] > nums[i + 1]]
        assert len(descents) <= 1
        if descents:
            assert nums[-1] < nums[0]


CHECKS["find-minimum-in-rotated-sorted-array"] = (b_findmin, lambda r: [rotated(r, r.randint(1, 9), -20, 20)], "exact")
VALIDATE["find-minimum-in-rotated-sorted-array"] = v_findmin

p = add(
    id="longest-repeating-character-replacement", title="Longest Repeating Character Replacement", diff="Medium", topic="Sliding Window",
    fn="characterReplacement", params=[("s", "string"), ("k", "int")], ret="int", cmp="exact",
    desc="<p>You are given a string <code>s</code> of uppercase letters and an integer <code>k</code>. In one operation you may pick any position of <code>s</code> and change its letter to any other uppercase letter. You may perform at most <code>k</code> operations in total.</p><p>Return the length of the longest substring that can be made to consist of one single repeated letter using at most <code>k</code> operations.</p>",
    constraints=["0 &le; s.length &le; 10,000", "s contains only uppercase English letters", "0 &le; k &le; s.length"],
    hints=["Try every substring and ask how many letters would have to change to make it uniform.",
           "For a window, the cheapest target letter is the one that already appears most often. The cost is <code>window length - highest letter count</code>.",
           "Grow a window to the right. Whenever its cost exceeds k, shrink it from the left. The longest window that was ever valid is the answer."],
    editorial=["A window is valid when <code>length - maxCount &le; k</code>, where <code>maxCount</code> is the count of its most frequent letter. Slide the right edge across the string, adding letters to a 26-entry count table. While the window is not valid, remove the left letter and advance the left edge. Record the largest valid window length.",
               "Each index enters and leaves the window at most once and a validity check costs at most 26 operations, so the total is O(26 n), i.e. linear. Because windows only shrink when invalid, the left edge never moves backwards. A known refinement keeps <code>maxCount</code> from ever decreasing, saving the 26-step scan, but the straightforward version is easier to trust."],
    time="O(n)", space="O(1)",
    solution='''def characterReplacement(s, k):
    count = {}
    left = 0
    best = 0
    for right, c in enumerate(s):
        count[c] = count.get(c, 0) + 1
        while (right - left + 1) - max(count.values()) > k:
            count[s[left]] -= 1
            left += 1
        best = max(best, right - left + 1)
    return best
''',
    tests=[["ABAB", 2], ["AABABBA", 1], ["AAAA", 0], ["", 0], ["A", 0], ["A", 1], ["ABCDE", 0], ["ABCDE", 5],
           ["ABBB", 2], ["AABBCC", 2], ["ZZYZZYYZ", 1], ["BAAAB", 2]],
)
_r = rnd(109)
p["tests"].append(["".join(_r.choice("ABC") for _ in range(10000)), 100])
p["tests"].append(["ABCDEFGHIJKLMNOPQRSTUVWXYZ" * 384 + "ABCD", 0])
p["tests"].append(["".join(_r.choice("AB") for _ in range(10000)), 5000])
p["tests"].append(["".join(_r.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ") for _ in range(10000)), 2000])


def b_charrep(s, k):
    best = 0
    for i in range(len(s)):
        for j in range(i, len(s)):
            sub = s[i:j + 1]
            if len(sub) - max(sub.count(c) for c in set(sub)) <= k:
                best = max(best, len(sub))
    return best


def g_charrep(r):
    s = "".join(r.choice("ABC") for _ in range(r.randint(0, 10)))
    return [s, r.randint(0, len(s))]


def v_charrep(tests):
    for t in tests:
        s, k = t["args"]
        assert len(s) <= 10000 and 0 <= k <= len(s) and all("A" <= c <= "Z" for c in s)


CHECKS["longest-repeating-character-replacement"] = (b_charrep, g_charrep, "exact")
VALIDATE["longest-repeating-character-replacement"] = v_charrep

p = add(
    id="minimum-size-subarray-sum", title="Minimum Size Subarray Sum", diff="Medium", topic="Sliding Window",
    fn="minSubArrayLen", params=[("target", "int"), ("nums", "int[]")], ret="int", cmp="exact",
    desc="<p>Given a positive integer <code>target</code> and an array <code>nums</code> of positive integers, return the length of the shortest contiguous subarray whose sum is greater than or equal to <code>target</code>.</p><p>If no subarray reaches the target, return <code>0</code>.</p>",
    constraints=["1 &le; target &le; 10<sup>9</sup>", "0 &le; nums.length &le; 10,000", "1 &le; nums[i] &le; 10,000"],
    hints=["Checking every subarray works in O(n&sup2;). The fact that all numbers are positive is a big clue.",
           "Adding an element on the right can only increase the sum; removing one from the left can only decrease it.",
           "Expand the right edge until the sum reaches the target, then shrink from the left as long as the sum still reaches it, recording the length each time."],
    editorial=["Use a sliding window with a running sum. For each new right index add <code>nums[right]</code>. While the sum is at least the target, record <code>right - left + 1</code>, subtract <code>nums[left]</code> and advance <code>left</code>. The best recorded length is the answer, or 0 if none was recorded.",
               "Positivity is what makes the window monotone: with negative numbers shrinking the window could increase the sum and the method fails. Each index enters and leaves once, so the work is O(n). A prefix-sum array with binary search for each right edge gives O(n log n) and also works."],
    time="O(n)", space="O(1)",
    solution='''def minSubArrayLen(target, nums):
    best = 0
    left = 0
    total = 0
    for right, x in enumerate(nums):
        total += x
        while total >= target:
            length = right - left + 1
            if best == 0 or length < best:
                best = length
            total -= nums[left]
            left += 1
    return best
''',
    tests=[[7, [2, 3, 1, 2, 4, 3]], [4, [1, 4, 4]], [11, [1, 1, 1, 1, 1, 1, 1, 1]], [5, []], [1, [1]], [2, [1]],
           [15, [1, 2, 3, 4, 5]], [16, [1, 2, 3, 4, 5]], [3, [1, 1, 1, 1, 1]], [6, [10, 2, 3]], [8, [3, 1, 1, 1, 5, 1]],
           [10 ** 9, [10000, 10000]]],
)
_r = rnd(110)
p["tests"].append([50000, [_r.randint(1, 100) for _ in range(10000)]])
_a = [_r.randint(1, 10000) for _ in range(3000)]
p["tests"].append([10 ** 9, _a])
p["tests"].append([sum(_a) - 1000, _a])
p["tests"].append([10000, [1] * 5000 + [10000]])
p["tests"].append([77777, [10000] * 2000])


def b_minsub(target, nums):
    best = 0
    for i in range(len(nums)):
        for j in range(i, len(nums)):
            if sum(nums[i:j + 1]) >= target and (best == 0 or j - i + 1 < best):
                best = j - i + 1
    return best


def v_minsub(tests):
    for t in tests:
        target, nums = t["args"]
        assert 1 <= target <= 10 ** 9 and len(nums) <= 10000 and all(1 <= x <= 10000 for x in nums)


CHECKS["minimum-size-subarray-sum"] = (b_minsub, lambda r: [r.randint(1, 30), [r.randint(1, 6) for _ in range(r.randint(0, 9))]], "exact")
VALIDATE["minimum-size-subarray-sum"] = v_minsub

p = add(
    id="subarray-sum-equals-k", title="Subarray Sum Equals K", diff="Medium", topic="Arrays & Hashing",
    fn="subarraySum", params=[("nums", "int[]"), ("k", "int")], ret="int", cmp="exact",
    desc="<p>Given an integer array <code>nums</code> (negative numbers and zeros are allowed) and an integer <code>k</code>, return how many contiguous, non-empty subarrays have a sum equal to <code>k</code>.</p><p>Subarrays at different positions count separately even if they hold the same values.</p>",
    constraints=["0 &le; nums.length &le; 10,000", "-1,000 &le; nums[i] &le; 1,000", "-10<sup>7</sup> &le; k &le; 10<sup>7</sup>"],
    hints=["Trying all start and end positions gives O(n&sup2;) subarrays. Think about prefix sums.",
           "The sum of <code>nums[i..j]</code> equals <code>prefix[j+1] - prefix[i]</code>.",
           "While scanning, for the current prefix sum P, add the number of earlier prefixes equal to <code>P - k</code>. Keep a hash map from prefix value to how often it occurred."],
    editorial=["Let <code>P_j</code> be the sum of the first j elements. A subarray ending at index j sums to k exactly when some earlier prefix equals <code>P_j - k</code>. Scan once, keep a map of prefix-sum frequencies (seeded with prefix 0 occurring once for the empty prefix), and add <code>map[P - k]</code> to the answer before recording the current prefix.",
               "A sliding window does not work here because negative values break monotonicity: extending a window can lower the sum. The prefix-sum map is O(n) time and O(n) space. The brute force over all pairs of boundaries is O(n&sup2;) with running sums."],
    time="O(n)", space="O(n)",
    solution='''def subarraySum(nums, k):
    seen = {0: 1}
    prefix = 0
    count = 0
    for x in nums:
        prefix += x
        count += seen.get(prefix - k, 0)
        seen[prefix] = seen.get(prefix, 0) + 1
    return count
''',
    tests=[[[1, 1, 1], 2], [[1, 2, 3], 3], [[1, -1, 0], 0], [[], 0], [[], 5], [[5], 5], [[5], 0], [[0, 0, 0], 0],
           [[3, 4, 7, 2, -3, 1, 4, 2], 7], [[-1, -1, 1], 0], [[1000, -1000, 1000, -1000], 0], [[2, 2, 2], 7],
           [[1, 1, 1, 1], 4]],
)
_r = rnd(111)
p["tests"].append([[0] * 10000, 0])
p["tests"].append([[1, -1] * 2000, 0])
p["tests"].append([[_r.randint(-1000, 1000) for _ in range(3000)], 0])
_a = [_r.randint(-5, 5) for _ in range(6000)]
p["tests"].append([_a, 7])
p["tests"].append([[1000] * 1500, 10 ** 6])


def b_subsum(nums, k):
    n = len(nums)
    return sum(1 for i in range(n) for j in range(i, n) if sum(nums[i:j + 1]) == k)


def v_subsum(tests):
    for t in tests:
        nums, k = t["args"]
        assert len(nums) <= 10000 and all(-1000 <= x <= 1000 for x in nums) and -10 ** 7 <= k <= 10 ** 7


CHECKS["subarray-sum-equals-k"] = (b_subsum, lambda r: [gen_arr(r, -3, 3, 0, 9), r.randint(-4, 4)], "exact")
VALIDATE["subarray-sum-equals-k"] = v_subsum


# ---------------------------------------------------------------- HARD

p = add(
    id="median-of-two-sorted-arrays", title="Lower Median of Two Sorted Arrays", diff="Hard", topic="Binary Search",
    fn="findLowerMedian", params=[("a", "int[]"), ("b", "int[]")], ret="int", cmp="exact",
    desc="<p>You are given two integer arrays <code>a</code> and <code>b</code>, each sorted in non-decreasing order, and at least one of them is non-empty. Imagine merging them into one sorted array of length <code>m + n</code>.</p><p>Return the element of the merged array at 0-based index <code>(m + n - 1) / 2</code> (integer division). This is the <em>lower median</em>: for an odd total it is the middle element, and for an even total it is the smaller of the two middle elements. Your solution should run in O(log(min(m, n))) time.</p>",
    constraints=["0 &le; a.length, b.length &le; 10,000", "1 &le; a.length + b.length", "-2<sup>31</sup> &le; a[i], b[i] &le; 2<sup>31</sup> - 1", "Both arrays are sorted in non-decreasing order"],
    hints=["Merging the arrays and indexing is O(m + n). To beat that you cannot look at every element.",
           "Let L = (m + n - 1) / 2 + 1. The answer is the largest of the L smallest elements overall. Suppose you take i of them from a and L - i from b: which condition makes that split correct?",
           "Binary search on i in the shorter array. The split is right when the last taken element of each array is no larger than the first untaken element of the other array. The answer is the larger of the two last taken elements."],
    editorial=["Make <code>a</code> the shorter array. The first L = (m + n - 1) / 2 + 1 merged elements consist of some i elements of <code>a</code> and L - i elements of <code>b</code>. The split is correct exactly when <code>a[i-1] &le; b[L-i]</code> and <code>b[L-i-1] &le; a[i]</code> (ignoring indices that fall outside the arrays). Binary search for the smallest i with <code>a[i] &ge; b[L-i-1]</code>; i is limited to <code>[max(0, L - n), min(m, L)]</code> so both counts stay valid. The answer is the larger of <code>a[i-1]</code> and <code>b[L-i-1]</code> that exist.",
               "Searching the shorter array keeps the cost at O(log(min(m, n))). A simpler approach is the two-pointer merge that stops at index L - 1, costing O(m + n). The lower-median definition removes the usual averaging step for even totals, so the result is always an element of one of the arrays and fits in a 32-bit integer."],
    time="O(log(min(m, n)))", space="O(1)",
    solution='''def findLowerMedian(a, b):
    if len(a) > len(b):
        a, b = b, a
    m, n = len(a), len(b)
    L = (m + n - 1) // 2 + 1          # how many of the smallest elements form the left part
    lo, hi = max(0, L - n), min(m, L)  # i = how many of them come from a
    while lo < hi:
        i = (lo + hi) // 2
        j = L - i
        if a[i] < b[j - 1]:
            lo = i + 1
        else:
            hi = i
    i = lo
    j = L - i
    best = None
    if i > 0:
        best = a[i - 1]
    if j > 0 and (best is None or b[j - 1] > best):
        best = b[j - 1]
    return best
''',
    tests=[[[1, 3], [2]], [[1, 2], [3, 4]], [[], [5]], [[7], []], [[0, 0], [0, 0]], [[], [1, 2, 3, 4]], [[1, 2, 3], []],
           [[1, 2, 3], [10, 20, 30]], [[10, 20, 30], [1, 2, 3]], [[1, 1, 1], [1, 1]], [[-5, -3, -1], [-4, -2, 0, 2]],
           [[INT_MIN, 0], [INT_MAX]], [[INT_MIN, INT_MIN], [INT_MAX, INT_MAX]], [[2], [1]], [[1, 5, 9], [2, 3, 4, 6, 7, 8]]],
)
_r = rnd(112)


def sorted_rand(r, n, lo, hi):
    return sorted(r.randint(lo, hi) for _ in range(n))


p["tests"].append([sorted_rand(_r, 10000, 0, 99), sorted_rand(_r, 10000, 0, 99)])
p["tests"].append([sorted_rand(_r, 2000, INT_MIN, INT_MAX), sorted_rand(_r, 1, INT_MIN, INT_MAX)])
p["tests"].append([sorted_rand(_r, 1000, -50, 50), sorted_rand(_r, 3000, -50, 50)])
p["tests"].append([list(range(1500)), list(range(5000, 6200))])
p["tests"].append([list(range(5000, 6200)), list(range(1500))])
p["tests"].append([[5] * 1500, [5] * 1500])
p["tests"].append([sorted_rand(_r, 1500, -1000, 1000), []])


def b_median(a, b):
    return sorted(a + b)[(len(a) + len(b) - 1) // 2]


def g_median(r):
    while True:
        a = sorted_rand(r, r.randint(0, 7), -8, 8)
        b = sorted_rand(r, r.randint(0, 7), -8, 8)
        if a or b:
            return [a, b]


def v_median(tests):
    for t in tests:
        a, b = t["args"]
        assert len(a) + len(b) >= 1 and len(a) <= 10000 and len(b) <= 10000
        assert a == sorted(a) and b == sorted(b)


CHECKS["median-of-two-sorted-arrays"] = (b_median, g_median, "exact")
VALIDATE["median-of-two-sorted-arrays"] = v_median

p = add(
    id="first-missing-positive", title="First Missing Positive", diff="Hard", topic="Arrays & Hashing",
    fn="firstMissingPositive", params=[("nums", "int[]")], ret="int", cmp="exact",
    desc="<p>Given an unsorted integer array <code>nums</code>, return the smallest positive integer (1, 2, 3, ...) that does not appear in it. The array may contain negative numbers, zeros, duplicates and huge values.</p><p>Your algorithm should run in O(n) time and use only O(1) extra space, so you are allowed to rearrange the array itself.</p>",
    constraints=["0 &le; nums.length &le; 10,000", "-2<sup>31</sup> &le; nums[i] &le; 2<sup>31</sup> - 1"],
    hints=["A set of the values and a loop over 1, 2, 3, ... works, but uses O(n) extra memory.",
           "With n numbers, the answer is always in the range 1..n+1. Values outside 1..n can never matter.",
           "Use the array as its own hash table: try to place each value v in 1..n at index v - 1 by swapping. Afterwards the first index i with <code>nums[i] != i + 1</code> gives the answer i + 1."],
    editorial=["The answer is at most n + 1, because n numbers cannot cover more than n positive values. So only values in 1..n are interesting. For each position i, while <code>nums[i]</code> is in 1..n and is not already sitting at its home index (<code>nums[nums[i] - 1] != nums[i]</code>), swap it into its home. The duplicate check guarantees termination. Every swap puts one value at its final position, so there are at most n swaps in total.",
               "Then scan once: the first index i where <code>nums[i] != i + 1</code> means i + 1 is missing; if every index matches, the answer is n + 1. A hash set gives a simpler O(n) time, O(n) space solution; sorting gives O(n log n) with O(1) extra space. The in-place swap method meets both bounds at once by treating array indices as hash buckets."],
    time="O(n)", space="O(1)",
    solution='''def firstMissingPositive(nums):
    n = len(nums)
    for i in range(n):
        while 1 <= nums[i] <= n and nums[nums[i] - 1] != nums[i]:
            j = nums[i] - 1
            nums[i], nums[j] = nums[j], nums[i]
    for i in range(n):
        if nums[i] != i + 1:
            return i + 1
    return n + 1
''',
    tests=[[[1, 2, 0]], [[3, 4, -1, 1]], [[7, 8, 9, 11, 12]], [[]], [[1]], [[2]], [[2, 1]], [[1, 1]], [[-1, -2, -3]],
           [[0]], [[1, 2, 3, 4, 5]], [[2, 2, 2, 2]], [[INT_MAX, INT_MIN, 1]], [[INT_MAX, 2, 3, INT_MIN]],
           [[4, 3, 2, 1, 6, 7]], [[1, 1000, 2, 3, 3, 5]]],
)
_r = rnd(113)
_a = list(range(1, 5001)); _r.shuffle(_a)
p["tests"].append([_a])
_a = list(range(1, 2001)); _a.remove(777); _r.shuffle(_a)
p["tests"].append([_a])
_a = list(range(1, 2001)); _a.remove(1); _r.shuffle(_a)
p["tests"].append([_a])
p["tests"].append([[_r.randint(INT_MIN, INT_MAX) for _ in range(1000)]])
p["tests"].append([[_r.randint(-5, 2000) for _ in range(2000)]])
p["tests"].append([[_r.randint(1, 100) for _ in range(4000)]])


def b_firstmissing(nums):
    s = set(nums)
    x = 1
    while x in s:
        x += 1
    return x


def v_firstmissing(tests):
    for t in tests:
        assert len(t["args"][0]) <= 10000


CHECKS["first-missing-positive"] = (b_firstmissing, lambda r: [gen_arr(r, -3, 10, 0, 9)], "exact")
VALIDATE["first-missing-positive"] = v_firstmissing
