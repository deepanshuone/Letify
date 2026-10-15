"""Problems: sliding window, counting subarrays/substrings ("at most k" decomposition). See data/lib.py for the registry."""
from lib import add, rnd, CHECKS, VALIDATE, gen_arr  # noqa: F401

TOPIC = "Sliding Window"
LOWER = "abcdefghijklmnopqrstuvwxyz"
VOWELS = "aeiou"


def _s(r, n, alpha):
    return "".join(r.choice(alpha) for _ in range(n))


# ---------------------------------------------------------------- EASY

p = add(
    id="count-subarrays-sum-at-most-k", title="Count Subarrays With Sum At Most K", diff="Easy", topic=TOPIC, tier="common",
    fn="countSumAtMost", params=[("nums", "int[]"), ("k", "int")], ret="int", cmp="exact",
    desc="<p>Given an array <code>nums</code> of non-negative integers and an integer <code>k</code>, return how many non-empty contiguous subarrays have a sum less than or equal to <code>k</code>.</p><p>Subarrays are counted by position, so equal-looking subarrays at different positions are counted separately.</p><pre>nums = [1, 2, 1], k = 3\n[1] [2] [1] [1, 2] [2, 1] all have sum &le; 3\n[1, 2, 1] has sum 4\nresult = 5</pre>",
    constraints=["1 &le; nums.length &le; 20,000", "0 &le; nums[i] &le; 10,000", "0 &le; k &le; 10<sup>9</sup>"],
    hints=["Counting every subarray with prefix sums is O(n&sup2;). Fix the right end: which left ends are allowed?",
           "All values are non-negative, so shrinking a subarray from the left never increases its sum. For a fixed right end the valid left ends form one contiguous range that ends at the right end itself.",
           "Slide a window: add <code>nums[right]</code>, move <code>left</code> forward while the sum exceeds <code>k</code>, then add <code>right - left + 1</code> (the number of valid subarrays ending at <code>right</code>) to the answer."],
    editorial=["Count subarrays by their right end. Because every element is non-negative, a subarray with sum at most <code>k</code> stays valid when you cut elements off its left side. So for a fixed right end the valid starting points are exactly <code>left..right</code>, where <code>left</code> is the smallest start that keeps the sum within <code>k</code>.",
               "As the right end moves forward, the smallest valid start never moves backwards, so one pass with two pointers is enough. After adding <code>nums[right]</code> and shrinking while the sum is above <code>k</code>, there are <code>right - left + 1</code> valid subarrays ending at <code>right</code> (zero when a single element is already too large). Each index enters and leaves the window once: O(n) time, O(1) space. The result is at most n(n+1)/2, which fits in 32 bits for n up to 20,000."],
    time="O(n)", space="O(1)",
    solution='''def countSumAtMost(nums, k):
    left = 0
    cur = 0
    total = 0
    for right, x in enumerate(nums):
        cur += x
        while cur > k:
            cur -= nums[left]
            left += 1
        total += right - left + 1
    return total
''',
    tests=[[[1, 2, 1], 3], [[5], 4], [[5], 5], [[0], 0], [[1, 2, 3], 0], [[0, 0, 0], 0], [[2, 2, 2, 2], 7], [[10, 1, 1, 1, 10], 3],
           [[1, 2, 3, 4, 5], 100], [[4, 0, 0, 4, 0], 4], [[7, 1, 6, 1, 1, 1, 9], 5]],
)
_r = rnd(4101)
p["tests"].append([[_r.randint(0, 10) for _ in range(8000)], 300])
p["tests"].append([[_r.randint(0, 10000) for _ in range(8000)], 123456])
p["tests"].append([[0] * 6000 + [10000] * 2000, 29999])


def b_sum_at_most(nums, k):
    n = len(nums)
    c = 0
    for i in range(n):
        for j in range(i, n):
            if sum(nums[i:j + 1]) <= k:
                c += 1
    return c


def g_sum_at_most(r):
    return [[r.randint(0, 6) for _ in range(r.randint(1, 10))], r.randint(0, 20)]


def v_sum_at_most(tests):
    for t in tests:
        a, k = t["args"]
        assert 1 <= len(a) <= 20000 and all(0 <= x <= 10000 for x in a)
        assert 0 <= k <= 10 ** 9


CHECKS["count-subarrays-sum-at-most-k"] = (b_sum_at_most, g_sum_at_most, "exact")
VALIDATE["count-subarrays-sum-at-most-k"] = v_sum_at_most


p = add(
    id="count-substrings-at-most-k-distinct", title="Count Substrings With At Most K Distinct Letters", diff="Easy", topic=TOPIC, tier="common",
    fn="countAtMostDistinct", params=[("s", "string"), ("k", "int")], ret="int", cmp="exact",
    desc="<p>Given a lowercase string <code>s</code> and an integer <code>k</code>, return the number of non-empty substrings of <code>s</code> that contain at most <code>k</code> different letters.</p><p>Substrings are counted by position: the two <code>a</code> in <code>\"aa\"</code> give two different substrings of length 1.</p><pre>s = \"aabc\", k = 2\nall 10 substrings except \"abc\" and \"aabc\" qualify\nresult = 8</pre>",
    constraints=["1 &le; s.length &le; 20,000", "s contains only lowercase English letters", "1 &le; k &le; 26"],
    hints=["Count substrings by their right end. For one right end, which starting positions are allowed?",
           "If a substring has at most k distinct letters, so does every shorter substring ending at the same place. The allowed starts therefore form one block that reaches up to the right end.",
           "Keep a window with letter counts and the number of distinct letters in it. After adding <code>s[right]</code>, move <code>left</code> forward while the distinct count exceeds <code>k</code>, and add <code>right - left + 1</code> to the answer."],
    editorial=["For a fixed right end, dropping characters from the left can only reduce the number of distinct letters. So the substrings ending at <code>right</code> with at most <code>k</code> distinct letters are exactly those starting in <code>left..right</code>, with <code>left</code> the smallest start that works. That smallest start never decreases when the right end moves forward.",
               "Maintain an array of 26 counters and the current number of distinct letters. Add the new letter, then pop letters off the left until the distinct count is back to at most <code>k</code>, and add the window length to the answer. Time O(n), space O(1).",
               "This function is the building block for many counting problems: the number of substrings with <em>exactly</em> k distinct letters is <code>f(k) - f(k - 1)</code>."],
    time="O(n)", space="O(1)",
    solution='''def countAtMostDistinct(s, k):
    cnt = [0] * 26
    distinct = 0
    left = 0
    total = 0
    for right, ch in enumerate(s):
        c = ord(ch) - 97
        if cnt[c] == 0:
            distinct += 1
        cnt[c] += 1
        while distinct > k:
            d = ord(s[left]) - 97
            cnt[d] -= 1
            if cnt[d] == 0:
                distinct -= 1
            left += 1
        total += right - left + 1
    return total
''',
    tests=[["aabc", 2], ["a", 1], ["abc", 1], ["abc", 3], ["aaaa", 1], ["abab", 2], ["abcabc", 2], ["zzzyx", 2], ["abcdefghijklmnopqrstuvwxyz", 26],
           ["abcdefghijklmnopqrstuvwxyz", 1], ["aabbccdd", 3]],
)
_r = rnd(4102)
p["tests"].append([_s(_r, 8000, "abc"), 2])
p["tests"].append([_s(_r, 8000, LOWER), 5])
p["tests"].append(["a" * 4000 + "b" * 4000, 1])


def b_at_most_distinct(s, k):
    n = len(s)
    c = 0
    for i in range(n):
        for j in range(i, n):
            if len(set(s[i:j + 1])) <= k:
                c += 1
    return c


def g_at_most_distinct(r):
    return [_s(r, r.randint(1, 10), "abcd"), r.randint(1, 5)]


def v_at_most_distinct(tests):
    for t in tests:
        s, k = t["args"]
        assert 1 <= len(s) <= 20000 and s.isalpha() and s.islower()
        assert 1 <= k <= 26


CHECKS["count-substrings-at-most-k-distinct"] = (b_at_most_distinct, g_at_most_distinct, "exact")
VALIDATE["count-substrings-at-most-k-distinct"] = v_at_most_distinct


p = add(
    id="count-binary-substrings-skewed-within-k", title="Count Substrings With Few Zeros or Few Ones", diff="Easy", topic=TOPIC, tier="extra",
    fn="countSkewed", params=[("s", "string"), ("k", "int")], ret="int", cmp="exact",
    desc="<p>A binary string <code>s</code> (characters <code>0</code> and <code>1</code>) is given together with an integer <code>k</code>. A substring is called <em>skewed</em> if it contains <strong>at most k zeros</strong> or <strong>at most k ones</strong> (or both).</p><p>Return the number of non-empty skewed substrings of <code>s</code>, counted by position.</p><pre>s = \"10101\", k = 1\nall 15 substrings except \"0101\", \"1010\", \"10101\" qualify\nresult = 12</pre>",
    constraints=["1 &le; s.length &le; 20,000", "s contains only the characters 0 and 1", "1 &le; k &le; s.length"],
    hints=["Count substrings by right end. Which starts keep the substring skewed?",
           "If a substring is skewed, every substring inside it is skewed too: removing characters cannot raise either count. So for each right end the valid starts are a block that reaches the right end.",
           "Keep the number of zeros and ones in the window. After adding <code>s[right]</code>, while both counts exceed <code>k</code> move <code>left</code> forward. Then add <code>right - left + 1</code>."],
    editorial=["The property \"zeros &le; k or ones &le; k\" is closed under taking sub-substrings, which is what makes a sliding window valid. For a fixed right end the skewed substrings are exactly those that start at <code>left</code> or later, where <code>left</code> is the first start that is still skewed. As the right end grows, that first start can only move to the right.",
               "Maintain the two counters. A window is broken only when <em>both</em> counters are above <code>k</code>, so shrink while that holds. Add the window length for every right end. O(n) time, O(1) space."],
    time="O(n)", space="O(1)",
    solution='''def countSkewed(s, k):
    cnt = [0, 0]
    left = 0
    total = 0
    for right, ch in enumerate(s):
        cnt[ord(ch) - 48] += 1
        while cnt[0] > k and cnt[1] > k:
            cnt[ord(s[left]) - 48] -= 1
            left += 1
        total += right - left + 1
    return total
''',
    tests=[["10101", 1], ["1010", 2], ["1", 1], ["0", 1], ["0000", 1], ["0101", 1], ["110100", 2], ["10101010", 2], ["0011", 1], ["111000111", 3], ["01", 1]],
)
_r = rnd(4103)
p["tests"].append([_s(_r, 8000, "01"), 3])
p["tests"].append([_s(_r, 8000, "01"), 50])
p["tests"].append(["01" * 4000, 1])


def b_skewed(s, k):
    n = len(s)
    c = 0
    for i in range(n):
        for j in range(i, n):
            t = s[i:j + 1]
            if t.count("0") <= k or t.count("1") <= k:
                c += 1
    return c


def g_skewed(r):
    n = r.randint(1, 11)
    return [_s(r, n, "01"), r.randint(1, max(1, n))]


def v_skewed(tests):
    for t in tests:
        s, k = t["args"]
        assert 1 <= len(s) <= 20000 and set(s) <= {"0", "1"}
        assert 1 <= k <= len(s)


CHECKS["count-binary-substrings-skewed-within-k"] = (b_skewed, g_skewed, "exact")
VALIDATE["count-binary-substrings-skewed-within-k"] = v_skewed


# ---------------------------------------------------------------- MEDIUM

p = add(
    id="count-binary-subarrays-with-sum", title="Count Binary Subarrays With Given Sum", diff="Medium", topic=TOPIC, tier="common",
    fn="countBinarySubarrays", params=[("nums", "int[]"), ("goal", "int")], ret="int", cmp="exact",
    desc="<p>The array <code>nums</code> contains only <code>0</code> and <code>1</code>. Return the number of non-empty contiguous subarrays whose sum is <strong>exactly</strong> <code>goal</code>.</p><p>Try to solve it with a sliding window and O(1) extra space, even though a prefix-sum hash map also works.</p><pre>nums = [1, 0, 1, 0, 1], goal = 2\n[1,0,1] [1,0,1,0] [0,1,0,1] [1,0,1]\nresult = 4</pre>",
    constraints=["1 &le; nums.length &le; 20,000", "nums[i] is 0 or 1", "0 &le; goal &le; nums.length"],
    hints=["A window for \"sum exactly goal\" is awkward, because both growing and shrinking can break the condition. Is there a related condition that is easier?",
           "Counting subarrays with sum <em>at most</em> some value is easy with a sliding window, since all values are non-negative.",
           "Let <code>f(g)</code> be the number of subarrays with sum at most <code>g</code>. Then the answer is <code>f(goal) - f(goal - 1)</code>, where <code>f(-1) = 0</code>."],
    editorial=["Every subarray with sum exactly <code>goal</code> has sum at most <code>goal</code>, and it is not among the subarrays with sum at most <code>goal - 1</code>. So <code>exact(goal) = atMost(goal) - atMost(goal - 1)</code>. The counts of sums are non-negative integers, so \"at most goal minus at most goal-1\" isolates precisely sum == goal.",
               "<code>atMost(g)</code> is a standard window count: for each right end, shrink from the left while the sum exceeds <code>g</code> and add the window length. For <code>g &lt; 0</code> there is no valid subarray, so return 0. Two linear passes: O(n) time, O(1) space.",
               "The same subtraction trick turns many \"exactly k\" counting problems (distinct values, odd numbers, ...) into two \"at most\" problems."],
    time="O(n)", space="O(1)",
    solution='''def countBinarySubarrays(nums, goal):
    def at_most(g):
        if g < 0:
            return 0
        left = 0
        cur = 0
        total = 0
        for right, x in enumerate(nums):
            cur += x
            while cur > g:
                cur -= nums[left]
                left += 1
            total += right - left + 1
        return total
    return at_most(goal) - at_most(goal - 1)
''',
    tests=[[[1, 0, 1, 0, 1], 2], [[0, 0, 0, 0, 0], 0], [[1], 1], [[0], 0], [[1], 0], [[0], 1 - 1 + 0], [[1, 1, 1], 2], [[0, 1, 0], 1], [[1, 0, 0, 1, 0, 0, 1], 3],
           [[0, 0, 1, 0, 0], 1], [[1, 1, 0, 0, 1, 1], 4]],
)
_r = rnd(4104)
p["tests"].append([[_r.randint(0, 1) for _ in range(8000)], 40])
p["tests"].append([[1 if _r.random() < 0.1 else 0 for _ in range(8000)], 0])
p["tests"].append([[1 if _r.random() < 0.02 else 0 for _ in range(8000)], 7])
p["tests"].append([[0] * 8000, 0])


def b_binary_sum(nums, goal):
    n = len(nums)
    c = 0
    for i in range(n):
        for j in range(i, n):
            if sum(nums[i:j + 1]) == goal:
                c += 1
    return c


def g_binary_sum(r):
    n = r.randint(1, 11)
    return [[r.randint(0, 1) for _ in range(n)], r.randint(0, min(n, 5))]


def v_binary_sum(tests):
    for t in tests:
        a, g = t["args"]
        assert 1 <= len(a) <= 20000 and set(a) <= {0, 1}
        assert 0 <= g <= len(a)


CHECKS["count-binary-subarrays-with-sum"] = (b_binary_sum, g_binary_sum, "exact")
VALIDATE["count-binary-subarrays-with-sum"] = v_binary_sum


p = add(
    id="count-subarrays-max-in-range", title="Count Subarrays With Maximum in a Range", diff="Medium", topic=TOPIC, tier="common",
    fn="countMaxInRange", params=[("nums", "int[]"), ("lo", "int"), ("hi", "int")], ret="int", cmp="exact",
    desc="<p>Given an integer array <code>nums</code> and two bounds <code>lo &le; hi</code>, return the number of non-empty contiguous subarrays whose <strong>maximum element</strong> lies between <code>lo</code> and <code>hi</code> inclusive.</p><pre>nums = [2, 1, 4, 3], lo = 2, hi = 3\nqualifying: [2], [2, 1], [3]\nresult = 3</pre>",
    constraints=["1 &le; nums.length &le; 20,000", "0 &le; nums[i] &le; 10<sup>9</sup>", "0 &le; lo &le; hi &le; 10<sup>9</sup>"],
    hints=["The maximum of a subarray is at most <code>hi</code> exactly when every element is at most <code>hi</code>.",
           "Count subarrays whose maximum is at most <code>x</code>: these are the subarrays that lie inside a run of consecutive elements that are all at most <code>x</code>.",
           "The answer is <code>atMost(hi) - atMost(lo - 1)</code>. A run of length L contributes L(L+1)/2 to <code>atMost</code>; you can also count by right end, adding the current run length."],
    editorial=["Let <code>atMost(x)</code> be the number of subarrays whose maximum is at most <code>x</code>. Such a subarray contains only elements &le; x, so it lies inside a maximal run of such elements. Scanning left to right, keep the length of the current run (reset to 0 at an element greater than x) and add it to the total at every position: that counts the subarrays ending there.",
               "A subarray has its maximum in <code>[lo, hi]</code> iff its maximum is at most <code>hi</code> but not at most <code>lo - 1</code>, so the answer is <code>atMost(hi) - atMost(lo - 1)</code>. Both passes are linear: O(n) time and O(1) space. Counting directly (\"the maximum is at least lo\") would need extra bookkeeping about the last big element; the difference form avoids it."],
    time="O(n)", space="O(1)",
    solution='''def countMaxInRange(nums, lo, hi):
    def at_most(x):
        run = 0
        total = 0
        for v in nums:
            run = run + 1 if v <= x else 0
            total += run
        return total
    return at_most(hi) - at_most(lo - 1)
''',
    tests=[[[2, 1, 4, 3], 2, 3], [[5], 5, 5], [[5], 6, 9], [[5], 0, 4], [[1, 1, 1], 1, 1], [[3, 3, 3], 0, 2], [[0, 0], 0, 0], [[10, 1, 10, 1], 1, 9],
           [[1, 2, 3, 4, 5], 2, 4], [[5, 4, 3, 2, 1], 3, 3], [[10 ** 9, 0, 10 ** 9], 0, 10 ** 9]],
)
_r = rnd(4105)
p["tests"].append([[_r.randint(0, 100) for _ in range(8000)], 40, 60])
p["tests"].append([[_r.randint(0, 10 ** 9) for _ in range(8000)], 10 ** 9 - 10 ** 7, 10 ** 9])
p["tests"].append([[_r.randint(0, 5) for _ in range(8000)], 3, 3])


def b_max_in_range(nums, lo, hi):
    n = len(nums)
    c = 0
    for i in range(n):
        for j in range(i, n):
            if lo <= max(nums[i:j + 1]) <= hi:
                c += 1
    return c


def g_max_in_range(r):
    a = [r.randint(0, 8) for _ in range(r.randint(1, 10))]
    lo = r.randint(0, 8)
    return [a, lo, r.randint(lo, 9)]


def v_max_in_range(tests):
    for t in tests:
        a, lo, hi = t["args"]
        assert 1 <= len(a) <= 20000 and all(0 <= x <= 10 ** 9 for x in a)
        assert 0 <= lo <= hi <= 10 ** 9


CHECKS["count-subarrays-max-in-range"] = (b_max_in_range, g_max_in_range, "exact")
VALIDATE["count-subarrays-max-in-range"] = v_max_in_range


p = add(
    id="count-substrings-containing-a-b-c", title="Count Substrings Containing a, b and c", diff="Medium", topic=TOPIC, tier="common",
    fn="countAllThree", params=[("s", "string")], ret="int", cmp="exact",
    desc="<p>The string <code>s</code> consists only of the letters <code>a</code>, <code>b</code> and <code>c</code>. Return the number of substrings that contain <strong>at least one</strong> <code>a</code>, <strong>at least one</strong> <code>b</code> and <strong>at least one</strong> <code>c</code>.</p><p>Substrings are counted by position.</p><pre>s = \"abcabc\"\nabc, abca, abcab, abcabc, bca, bcab, bcabc, cab, cabc, abc\nresult = 10</pre>",
    constraints=["3 &le; s.length &le; 20,000", "s contains only the letters a, b and c"],
    hints=["Count by right end. If a substring ending at <code>right</code> already contains all three letters, what happens when you extend it to the left?",
           "Extending to the left keeps all three letters, so for each right end the valid starts are a prefix <code>0..t</code> of the possible starts (not a suffix as in the \"at most\" problems).",
           "<code>t</code> is the smallest of the last positions of <code>a</code>, <code>b</code> and <code>c</code> seen so far. Equivalently: total substrings minus those with at most 2 distinct letters."],
    editorial=["Fix the right end <code>r</code>. Let <code>la</code>, <code>lb</code>, <code>lc</code> be the most recent indices (at or before <code>r</code>) of each letter. A substring <code>[i, r]</code> has all three letters iff <code>i &le; min(la, lb, lc)</code>, so there are <code>min(la, lb, lc) + 1</code> valid starts once all three letters have appeared (and none before that).",
               "Summing over all right ends gives the answer in a single pass with O(1) memory. Equivalently, substrings with all three letters = all substrings minus substrings with at most 2 distinct letters, which is the \"at most k distinct\" window count with k = 2; the two views give the same number. Time O(n), space O(1)."],
    time="O(n)", space="O(1)",
    solution='''def countAllThree(s):
    last = [-1, -1, -1]
    total = 0
    for i, ch in enumerate(s):
        last[ord(ch) - 97] = i
        total += min(last) + 1
    return total
''',
    tests=[["abcabc"], ["abc"], ["aaabc"], ["cba"], ["aabbcc"], ["abcc"], ["ccbbaa"], ["abacbc"], ["cabcabcab"], ["aaacbbb"], ["bbbbbbbbabc"]],
)
_r = rnd(4106)
p["tests"].append([_s(_r, 8000, "abc")])
p["tests"].append(["a" * 3000 + "b" * 3000 + "c" * 3000])
p["tests"].append(["abc" * 2700])


def b_all_three(s):
    n = len(s)
    c = 0
    for i in range(n):
        for j in range(i, n):
            t = s[i:j + 1]
            if "a" in t and "b" in t and "c" in t:
                c += 1
    return c


def g_all_three(r):
    return [_s(r, r.randint(3, 11), "abc")]


def v_all_three(tests):
    for t in tests:
        s = t["args"][0]
        assert 3 <= len(s) <= 20000 and set(s) <= set("abc")


CHECKS["count-substrings-containing-a-b-c"] = (b_all_three, g_all_three, "exact")
VALIDATE["count-substrings-containing-a-b-c"] = v_all_three


p = add(
    id="count-subarrays-max-at-least-k-times", title="Count Subarrays Where the Maximum Appears K Times", diff="Medium", topic=TOPIC, tier="common",
    fn="countMaxAtLeastK", params=[("nums", "int[]"), ("k", "int")], ret="int", cmp="exact",
    desc="<p>Let <code>M</code> be the largest value in the whole array <code>nums</code>. Return the number of non-empty contiguous subarrays in which the value <code>M</code> occurs <strong>at least k times</strong>.</p><pre>nums = [1, 3, 2, 3, 3], k = 2\nM = 3; qualifying subarrays:\n[1,3,2,3] [1,3,2,3,3] [3,2,3] [3,2,3,3] [2,3,3] [3,3]\nresult = 6</pre>",
    constraints=["1 &le; nums.length &le; 20,000", "1 &le; nums[i] &le; 10<sup>6</sup>", "1 &le; k &le; nums.length"],
    hints=["Only the positions of the global maximum <code>M</code> matter. A subarray qualifies as soon as it covers k of them.",
           "Extending a qualifying subarray in either direction keeps it qualifying. So for a fixed right end the valid starts form a prefix of the array.",
           "Slide <code>left</code> as far as possible while the window still holds at least k copies of <code>M</code>. Then every start before the final <code>left</code> works, so add <code>left</code> to the answer for each right end."],
    editorial=["First compute <code>M</code>. Walk the right end through the array and count copies of <code>M</code> in the window. While the window <code>[left, right]</code> contains at least <code>k</code> copies, drop <code>nums[left]</code> and advance <code>left</code>; when the loop stops, the window is no longer enough, but the starts <code>0..left-1</code> all produced windows that were. That is <code>left</code> valid subarrays ending at <code>right</code>.",
               "This is the complement-style counterpart of the \"at most\" window: instead of counting subarrays that stay below a limit, we count those that reach it, and the valid starts form a prefix instead of a suffix. Each pointer only moves forward: O(n) time, O(1) space.",
               "An equivalent view: answer = total subarrays - subarrays with fewer than k copies of M, and the latter is an \"at most k-1\" window count."],
    time="O(n)", space="O(1)",
    solution='''def countMaxAtLeastK(nums, k):
    m = max(nums)
    left = 0
    cnt = 0
    total = 0
    for x in nums:
        if x == m:
            cnt += 1
        while cnt >= k:
            if nums[left] == m:
                cnt -= 1
            left += 1
        total += left
    return total
''',
    tests=[[[1, 3, 2, 3, 3], 2], [[1, 4, 2, 1], 3], [[5], 1], [[5, 5, 5], 3], [[5, 5, 5], 1], [[1, 2, 3], 1], [[3, 1, 3, 1, 3], 2], [[2, 2, 1, 2], 2],
           [[7, 1, 1, 7], 2], [[1, 1, 1, 1], 4], [[4, 9, 9, 4, 9, 4], 2]],
)
_r = rnd(4107)
p["tests"].append([[_r.randint(1, 3) for _ in range(8000)], 100])
p["tests"].append([[_r.randint(1, 1000000) for _ in range(8000)], 1])
p["tests"].append([[1] * 7000 + [2] * 1000, 500])


def b_max_k(nums, k):
    n = len(nums)
    m = max(nums)
    c = 0
    for i in range(n):
        for j in range(i, n):
            if nums[i:j + 1].count(m) >= k:
                c += 1
    return c


def g_max_k(r):
    n = r.randint(1, 11)
    return [[r.randint(1, 4) for _ in range(n)], r.randint(1, min(n, 4))]


def v_max_k(tests):
    for t in tests:
        a, k = t["args"]
        assert 1 <= len(a) <= 20000 and all(1 <= x <= 10 ** 6 for x in a)
        assert 1 <= k <= len(a)


CHECKS["count-subarrays-max-at-least-k-times"] = (b_max_k, g_max_k, "exact")
VALIDATE["count-subarrays-max-at-least-k-times"] = v_max_k


p = add(
    id="count-substrings-with-frequent-letter", title="Count Substrings With a Frequent Letter", diff="Medium", topic=TOPIC, tier="extra",
    fn="countFrequentLetter", params=[("s", "string"), ("k", "int")], ret="int", cmp="exact",
    desc="<p>Given a lowercase string <code>s</code> and an integer <code>k</code>, count the substrings in which <strong>at least one letter appears k or more times</strong>. Substrings are counted by position.</p><pre>s = \"abacb\", k = 2\nqualifying: \"aba\", \"abac\", \"abacb\", \"bacb\"\nresult = 4</pre>",
    constraints=["1 &le; s.length &le; 20,000", "s contains only lowercase English letters", "1 &le; k &le; s.length"],
    hints=["Counting substrings that <em>have</em> a frequent letter directly is hard. What about the substrings that do <em>not</em>?",
           "A substring has no frequent letter when every letter appears at most k-1 times. That property survives when you remove characters, so a sliding window can maintain it.",
           "Answer = total number of substrings, n(n+1)/2, minus the number of substrings in which every letter count is at most k-1. After adding <code>s[right]</code>, only that letter can break the rule, so shrink while its count reaches k."],
    editorial=["Count the complement. Call a substring <em>calm</em> if each letter occurs at most <code>k - 1</code> times in it. Every substring of a calm substring is calm, so for a fixed right end the calm substrings are those starting in <code>left..right</code>.",
               "Add <code>s[right]</code>. If that letter's count has reached <code>k</code>, it is the only letter that can be over the limit, so advance <code>left</code> (decrementing counts) until the count of that letter is below <code>k</code> again. Then the window holds <code>right - left + 1</code> calm substrings ending at <code>right</code>. Sum these and subtract from <code>n(n+1)/2</code>.",
               "With <code>k = 1</code> every letter that occurs is frequent, so every substring counts. Time O(n), space O(1)."],
    time="O(n)", space="O(1)",
    solution='''def countFrequentLetter(s, k):
    n = len(s)
    cnt = [0] * 26
    left = 0
    calm = 0
    for right, ch in enumerate(s):
        c = ord(ch) - 97
        cnt[c] += 1
        while cnt[c] >= k:
            cnt[ord(s[left]) - 97] -= 1
            left += 1
        calm += right - left + 1
    return n * (n + 1) // 2 - calm
''',
    tests=[["abacb", 2], ["abcde", 1], ["abcde", 2], ["aaaa", 2], ["aaaa", 4], ["a", 1], ["abab", 2], ["abcabcabc", 3], ["zzzzyz", 3], ["abcabc", 2], ["aabbaabb", 3]],
)
_r = rnd(4108)
p["tests"].append([_s(_r, 8000, LOWER), 3])
p["tests"].append([_s(_r, 8000, "abc"), 60])
p["tests"].append([_s(_r, 8000, "ab"), 4000])


def b_frequent(s, k):
    n = len(s)
    c = 0
    for i in range(n):
        for j in range(i, n):
            t = s[i:j + 1]
            if any(t.count(ch) >= k for ch in set(t)):
                c += 1
    return c


def g_frequent(r):
    n = r.randint(1, 11)
    return [_s(r, n, "abc"), r.randint(1, min(n, 5))]


def v_frequent(tests):
    for t in tests:
        s, k = t["args"]
        assert 1 <= len(s) <= 20000 and s.isalpha() and s.islower()
        assert 1 <= k <= len(s)


CHECKS["count-substrings-with-frequent-letter"] = (b_frequent, g_frequent, "exact")
VALIDATE["count-substrings-with-frequent-letter"] = v_frequent


p = add(
    id="count-subarrays-score-below-k", title="Count Subarrays With Score Below K", diff="Medium", topic=TOPIC, tier="common",
    fn="countScoreBelow", params=[("nums", "int[]"), ("k", "int")], ret="int", cmp="exact",
    desc="<p>The <em>score</em> of an array is its sum multiplied by its length. For example, the score of <code>[1, 2, 3]</code> is <code>(1 + 2 + 3) * 3 = 18</code>.</p><p>Given an array <code>nums</code> of positive integers and an integer <code>k</code>, return the number of non-empty contiguous subarrays whose score is <strong>strictly less than</strong> <code>k</code>.</p><pre>nums = [2, 1, 4, 3, 5], k = 10\nqualifying: [2] [1] [4] [3] [5] [2, 1]\n[2, 1] has score 3 * 2 = 6; [1, 4] has 5 * 2 = 10, not below 10\nresult = 6</pre>",
    constraints=["1 &le; nums.length &le; 20,000", "1 &le; nums[i] &le; 100,000", "1 &le; k &le; 10<sup>9</sup>"],
    hints=["What happens to the score of a subarray when you extend it by one element? And when you remove one from an end?",
           "Elements are positive, so both the sum and the length grow when you extend. The score strictly increases. Hence cutting from the left can only lower it, and the valid starts for a fixed right end form one contiguous block.",
           "Keep a running window sum. After adding <code>nums[right]</code>, move <code>left</code> forward while <code>sum * (right - left + 1) &ge; k</code>, then add <code>right - left + 1</code>."],
    editorial=["Because all numbers are positive, the score <code>sum * length</code> is strictly increasing when the subarray grows and strictly decreasing when it shrinks. That monotonicity is exactly the condition for a two-pointer count: for each right end, the starts that give a score below <code>k</code> are <code>left..right</code>, and the smallest such start never moves backwards.",
               "Maintain the window sum. For every right end shrink while <code>sum * (right - left + 1) &ge; k</code>, then add the window length. The product can exceed 32 bits inside the loop (up to about 4*10<sup>13</sup>), but the returned count is at most n(n+1)/2 &le; 2*10<sup>8</sup>. Python integers are unbounded; in fixed-width languages use 64 bits for the product. Time O(n), space O(1)."],
    time="O(n)", space="O(1)",
    solution='''def countScoreBelow(nums, k):
    left = 0
    cur = 0
    total = 0
    for right, x in enumerate(nums):
        cur += x
        while cur * (right - left + 1) >= k:
            cur -= nums[left]
            left += 1
        total += right - left + 1
    return total
''',
    tests=[[[2, 1, 4, 3, 5], 10], [[1, 1, 1], 5], [[1, 1, 1], 1], [[1, 1, 1], 2], [[5], 5], [[5], 6], [[100000], 1000000000], [[1, 2, 3], 18], [[1, 2, 3], 19],
           [[3, 3, 3, 3], 20], [[9, 1, 9, 1], 12]],
)
_r = rnd(4109)
p["tests"].append([[_r.randint(1, 10) for _ in range(8000)], 1000])
p["tests"].append([[_r.randint(1, 100000) for _ in range(8000)], 10 ** 9])
p["tests"].append([[1] * 8000, 10 ** 9])


def b_score(nums, k):
    n = len(nums)
    c = 0
    for i in range(n):
        for j in range(i, n):
            if sum(nums[i:j + 1]) * (j - i + 1) < k:
                c += 1
    return c


def g_score(r):
    return [[r.randint(1, 6) for _ in range(r.randint(1, 10))], r.randint(1, 80)]


def v_score(tests):
    for t in tests:
        a, k = t["args"]
        assert 1 <= len(a) <= 20000 and all(1 <= x <= 100000 for x in a)
        assert 1 <= k <= 10 ** 9


CHECKS["count-subarrays-score-below-k"] = (b_score, g_score, "exact")
VALIDATE["count-subarrays-score-below-k"] = v_score


# ---------------------------------------------------------------- HARD

p = add(
    id="count-substrings-all-vowels-exact-consonants", title="Substrings With All Vowels and Exactly K Consonants", diff="Hard", topic=TOPIC, tier="extra",
    fn="countAllVowelsExactK", params=[("s", "string"), ("k", "int")], ret="int", cmp="exact",
    desc="<p>The string <code>s</code> consists of lowercase letters. The vowels are <code>a</code>, <code>e</code>, <code>i</code>, <code>o</code>, <code>u</code>; all other letters are consonants.</p><p>Return the number of substrings that contain <strong>every vowel at least once</strong> and <strong>exactly k consonants</strong>. Substrings are counted by position.</p><pre>s = \"ieaouqqieaouqq\", k = 1\nqualifying: s[0..5] = \"ieaouq\", s[6..11] = \"qieaou\", s[7..12] = \"ieaouq\"\nresult = 3</pre>",
    constraints=["5 &le; s.length &le; 20,000", "s contains only lowercase English letters", "0 &le; k &le; s.length - 5"],
    hints=["Two conditions at once: all five vowels present, and the consonant count is exactly k. Handle them one at a time.",
           "Let <code>g(k)</code> be the number of substrings with all five vowels and <em>at least</em> k consonants. Such substrings stay valid when extended in either direction.",
           "The answer is <code>g(k) - g(k + 1)</code>. Compute <code>g</code> with two pointers: for each right end, advance <code>left</code> while the window is still valid, then add <code>left</code> (all earlier starts are valid)."],
    editorial=["Define <code>g(m)</code> as the number of substrings that contain all five vowels and at least <code>m</code> consonants. A substring with exactly <code>k</code> consonants is counted by <code>g(k)</code> but not by <code>g(k + 1)</code>, and every substring counted by <code>g(k + 1)</code> is also counted by <code>g(k)</code>. So the answer is <code>g(k) - g(k + 1)</code>.",
               "Both requirements (\"all vowels\", \"consonants &ge; m\") are preserved when a substring grows. So for a fixed right end the valid starts are a prefix <code>0..t</code> of the starts. Keep a window <code>[left, right]</code>; while it is still valid, remove <code>s[left]</code> (updating the vowel counts and the consonant count) and move <code>left</code> forward. When the loop ends, the starts <code>0..left-1</code> each gave a valid substring ending at <code>right</code>, so add <code>left</code>.",
               "Two linear passes with O(1) memory (five vowel counters). Time O(n), space O(1)."],
    time="O(n)", space="O(1)",
    solution='''def countAllVowelsExactK(s, k):
    idx = {'a': 0, 'e': 1, 'i': 2, 'o': 3, 'u': 4}

    def at_least(m):
        cnt = [0] * 5
        have = 0
        cons = 0
        left = 0
        total = 0
        for ch in s:
            j = idx.get(ch)
            if j is None:
                cons += 1
            else:
                if cnt[j] == 0:
                    have += 1
                cnt[j] += 1
            while have == 5 and cons >= m:
                d = idx.get(s[left])
                if d is None:
                    cons -= 1
                else:
                    cnt[d] -= 1
                    if cnt[d] == 0:
                        have -= 1
                left += 1
            total += left
        return total

    return at_least(k) - at_least(k + 1)
''',
    tests=[["ieaouqqieaouqq", 1], ["aeiou", 0], ["aeioqq", 1], ["aeiouq", 1], ["aeiouaeiou", 0], ["baeiouc", 2], ["baeiouc", 1], ["uoieabcde", 2], ["aeeiiooouuu", 0],
           ["xaeioux", 0], ["qqaeiouqqaeiouqq", 3]],
)
_r = rnd(4110)
p["tests"].append([_s(_r, 8000, "aeioubcd"), 2])
p["tests"].append([_s(_r, 8000, "aeiouaeioubc"), 10])
p["tests"].append([_s(_r, 8000, LOWER), 0])


def b_vowels_exact(s, k):
    n = len(s)
    c = 0
    for i in range(n):
        for j in range(i, n):
            t = s[i:j + 1]
            if all(v in t for v in VOWELS) and sum(1 for ch in t if ch not in VOWELS) == k:
                c += 1
    return c


def g_vowels_exact(r):
    n = r.randint(5, 14)
    return [_s(r, n, "aeioubc"), r.randint(0, min(4, n - 5))]


def v_vowels_exact(tests):
    for t in tests:
        s, k = t["args"]
        assert 5 <= len(s) <= 20000 and s.isalpha() and s.islower()
        assert 0 <= k <= len(s) - 5


CHECKS["count-substrings-all-vowels-exact-consonants"] = (b_vowels_exact, g_vowels_exact, "exact")
VALIDATE["count-substrings-all-vowels-exact-consonants"] = v_vowels_exact


p = add(
    id="count-subarrays-with-exact-min-and-max", title="Count Subarrays With Given Minimum and Maximum", diff="Hard", topic=TOPIC, tier="extra",
    fn="countFixedMinMax", params=[("nums", "int[]"), ("minK", "int"), ("maxK", "int")], ret="int", cmp="exact",
    desc="<p>Given an integer array <code>nums</code> and two values <code>minK &le; maxK</code>, return the number of non-empty contiguous subarrays whose <strong>minimum equals <code>minK</code></strong> and whose <strong>maximum equals <code>maxK</code></strong>.</p><pre>nums = [1, 3, 5, 2, 7, 5], minK = 1, maxK = 5\nqualifying: [1,3,5] and [1,3,5,2]\nresult = 2</pre>",
    constraints=["1 &le; nums.length &le; 20,000", "1 &le; nums[i] &le; 10<sup>6</sup>", "1 &le; minK &le; maxK &le; 10<sup>6</sup>"],
    hints=["Elements outside <code>[minK, maxK]</code> split the array into independent segments. Inside a segment, what still has to be checked?",
           "A subarray whose elements all lie in <code>[minK, maxK]</code> has minimum exactly minK unless all its elements are &gt; minK, and maximum exactly maxK unless all its elements are &lt; maxK.",
           "Let <code>f(lo, hi)</code> be the number of subarrays with every element in <code>[lo, hi]</code> (0 if lo &gt; hi). Use inclusion-exclusion: <code>f(minK, maxK) - f(minK+1, maxK) - f(minK, maxK-1) + f(minK+1, maxK-1)</code>."],
    editorial=["Define <code>f(lo, hi)</code> = number of subarrays whose elements all lie in <code>[lo, hi]</code>; it is a sum of <code>L(L+1)/2</code> over maximal runs of such elements, computed in one pass (add the current run length at every position). If <code>lo &gt; hi</code> the range is empty and the count is 0.",
               "Among subarrays inside <code>[minK, maxK]</code>, those that fail the minimum condition have all elements in <code>[minK+1, maxK]</code>, and those that fail the maximum condition have all elements in <code>[minK, maxK-1]</code>. The ones failing both lie in <code>[minK+1, maxK-1]</code>. By inclusion-exclusion the answer is <code>f(minK, maxK) - f(minK+1, maxK) - f(minK, maxK-1) + f(minK+1, maxK-1)</code>.",
               "This is the \"at most\" subtraction trick in two dimensions. When <code>minK == maxK</code> the last three terms are 0 and the answer is just the number of subarrays made of equal values <code>minK</code>. Four linear passes: O(n) time, O(1) space. (A single pass that tracks the last positions of minK, maxK and the last out-of-range element also works.)"],
    time="O(n)", space="O(1)",
    solution='''def countFixedMinMax(nums, minK, maxK):
    def inside(lo, hi):
        if lo > hi:
            return 0
        run = 0
        total = 0
        for v in nums:
            run = run + 1 if lo <= v <= hi else 0
            total += run
        return total
    return (inside(minK, maxK) - inside(minK + 1, maxK)
            - inside(minK, maxK - 1) + inside(minK + 1, maxK - 1))
''',
    tests=[[[1, 3, 5, 2, 7, 5], 1, 5], [[1, 1, 1, 1], 1, 1], [[5], 5, 5], [[5], 4, 5], [[2, 3], 2, 3], [[3, 2], 2, 3], [[2, 2, 3, 3], 2, 3], [[1, 5, 1, 5, 9], 1, 5],
           [[4, 4, 4], 4, 5], [[1, 2, 3, 4, 5], 2, 4], [[3, 1, 4, 1, 5, 9, 2, 6], 1, 5]],
)
_r = rnd(4111)
p["tests"].append([[_r.randint(1, 10) for _ in range(8000)], 3, 8])
p["tests"].append([[_r.randint(1, 1000000) for _ in range(8000)], 1, 1000000])
p["tests"].append([[_r.choice([2, 3, 4]) for _ in range(8000)], 2, 4])


def b_exact_min_max(nums, mn, mx):
    n = len(nums)
    c = 0
    for i in range(n):
        for j in range(i, n):
            t = nums[i:j + 1]
            if min(t) == mn and max(t) == mx:
                c += 1
    return c


def g_exact_min_max(r):
    a = [r.randint(1, 6) for _ in range(r.randint(1, 11))]
    mn = r.randint(1, 5)
    return [a, mn, r.randint(mn, 6)]


def v_exact_min_max(tests):
    for t in tests:
        a, mn, mx = t["args"]
        assert 1 <= len(a) <= 20000 and all(1 <= x <= 10 ** 6 for x in a)
        assert 1 <= mn <= mx <= 10 ** 6


CHECKS["count-subarrays-with-exact-min-and-max"] = (b_exact_min_max, g_exact_min_max, "exact")
VALIDATE["count-subarrays-with-exact-min-and-max"] = v_exact_min_max
