"""Problems: sliding window, variable windows (longest window satisfying a rule). See data/lib.py for the registry."""
from collections import Counter

from lib import add, rnd, CHECKS, VALIDATE, gen_arr  # noqa: F401

LOWER = "abcdefghijklmnopqrstuvwxyz"


def _s(r, n, alpha):
    return "".join(r.choice(alpha) for _ in range(n))


# ---------------------------------------------------------------- EASY

p = add(
    id="longest-subarray-sum-at-most-k", title="Longest Subarray With Sum At Most K", diff="Easy", topic="Sliding Window",
    fn="longestSumAtMost", params=[("nums", "int[]"), ("k", "int")], ret="int", cmp="exact",
    desc="<p>Given an array <code>nums</code> of non-negative integers and an integer <code>k</code>, return the length of the longest contiguous subarray whose elements add up to <code>k</code> or less. If no non-empty subarray qualifies, return <code>0</code>.</p><pre>nums = [3, 1, 2, 1, 1], k = 4\n[1, 2, 1] and [2, 1, 1] both sum to 4\nresult = 3</pre>",
    constraints=["1 &le; nums.length &le; 10,000", "0 &le; nums[i] &le; 10,000", "0 &le; k &le; 10<sup>9</sup>"],
    hints=["Checking every subarray works but is O(n&sup2;). What happens to the sum when you extend a subarray to the right?",
           "Because nothing is negative, a longer subarray never has a smaller sum. So if a window is too heavy, only moving its left end can help.",
           "Keep a window <code>[left, right]</code> and its sum. Add <code>nums[right]</code>, then move <code>left</code> forward while the sum exceeds <code>k</code>. Record <code>right - left + 1</code> after each step."],
    editorial=["Since all values are non-negative, the window sum is non-decreasing when the right end moves right and non-increasing when the left end moves right. That monotonicity is exactly what a sliding window needs: for every right end, the valid left ends form a suffix of the possible starts, and the smallest valid left end never moves backwards as the right end advances.",
               "Add each element to the running sum, then shrink from the left while the sum is above <code>k</code>. If a single element is larger than <code>k</code> the window becomes empty (length 0), which correctly contributes nothing. Each index enters and leaves the window at most once, so the time is O(n) with O(1) extra space."],
    time="O(n)", space="O(1)",
    solution='''def longestSumAtMost(nums, k):
    left = 0
    cur = 0
    best = 0
    for right, x in enumerate(nums):
        cur += x
        while cur > k:
            cur -= nums[left]
            left += 1
        best = max(best, right - left + 1)
    return best
''',
    tests=[[[3, 1, 2, 1, 1], 4], [[5], 4], [[5], 5], [[0], 0], [[1, 2, 3], 0], [[0, 0, 0], 0], [[2, 2, 2, 2], 7], [[10, 1, 1, 1, 10], 3],
           [[1, 2, 3, 4, 5], 100], [[4, 0, 0, 4, 0], 4], [[7, 1, 6, 1, 1, 1, 9], 5]],
)
_r = rnd(3101)
p["tests"].append([[_r.randint(0, 10) for _ in range(8000)], 500])
p["tests"].append([[_r.randint(0, 10000) for _ in range(8000)], 123456])
p["tests"].append([[0] * 5000 + [10000] * 3000, 29999])


def b_sum_at_most(nums, k):
    best = 0
    for i in range(len(nums)):
        for j in range(i, len(nums)):
            if sum(nums[i:j + 1]) <= k:
                best = max(best, j - i + 1)
    return best


def g_sum_at_most(r):
    return [[r.randint(0, 6) for _ in range(r.randint(1, 10))], r.randint(0, 20)]


def v_sum_at_most(tests):
    for t in tests:
        a, k = t["args"]
        assert 1 <= len(a) <= 10000 and all(0 <= x <= 10000 for x in a)
        assert 0 <= k <= 10 ** 9


CHECKS["longest-subarray-sum-at-most-k"] = (b_sum_at_most, g_sum_at_most, "exact")
VALIDATE["longest-subarray-sum-at-most-k"] = v_sum_at_most


p = add(
    id="longest-substring-limited-consonants", title="Longest Substring With Limited Consonants", diff="Easy", topic="Sliding Window",
    fn="longestLimitedConsonants", params=[("s", "string"), ("k", "int")], ret="int", cmp="exact", tier="extra",
    desc="<p>The string <code>s</code> consists of lowercase English letters. The vowels are <code>a</code>, <code>e</code>, <code>i</code>, <code>o</code>, <code>u</code>; every other letter is a consonant.</p><p>Return the length of the longest substring that contains at most <code>k</code> consonants (counting repeated consonants each time they occur).</p><pre>s = \"education\", k = 1\n\"atio\" has one consonant (t)\nresult = 4</pre>",
    constraints=["1 &le; s.length &le; 100,000", "s contains only lowercase English letters", "0 &le; k &le; s.length"],
    hints=["Replace each letter by 1 if it is a consonant and 0 if it is a vowel. You want the longest stretch whose total is at most k.",
           "Adding a character to a substring never reduces its consonant count, so the rule is monotone: once a window is invalid, only dropping characters from the left can repair it.",
           "Slide a window: extend <code>right</code>, add one to the consonant count when needed, and while the count exceeds k move <code>left</code> forward (subtracting when you leave a consonant)."],
    editorial=["The condition is about a count that only grows as the window grows, so a two-pointer sweep applies. For every right end the best left end is the smallest index for which the window still has at most <code>k</code> consonants, and that left end never decreases as <code>right</code> increases.",
               "Maintain the number of consonants inside the window. After adding <code>s[right]</code> shrink the window while the count is above <code>k</code>, then update the best length. When <code>k = 0</code> the answer is the longest run of vowels. Time O(n), space O(1)."],
    time="O(n)", space="O(1)",
    solution='''def longestLimitedConsonants(s, k):
    vowels = set("aeiou")
    left = 0
    cons = 0
    best = 0
    for right, ch in enumerate(s):
        if ch not in vowels:
            cons += 1
        while cons > k:
            if s[left] not in vowels:
                cons -= 1
            left += 1
        best = max(best, right - left + 1)
    return best
''',
    tests=[["education", 1], ["education", 0], ["bcdfg", 0], ["bcdfg", 2], ["a", 0], ["b", 0], ["b", 1], ["aeiouaeiou", 0], ["xyzaeixyz", 1],
           ["leetcode", 3], ["abcdefghijklmnopqrstuvwxyz", 5]],
)
_r = rnd(3102)
p["tests"].append([_s(_r, 8000, LOWER), 40])
p["tests"].append([_s(_r, 8000, "aeioub"), 6])
p["tests"].append(["a" * 4000 + "z" * 4000, 0])


def b_consonants(s, k):
    best = 0
    for i in range(len(s)):
        for j in range(i, len(s)):
            if sum(1 for c in s[i:j + 1] if c not in "aeiou") <= k:
                best = max(best, j - i + 1)
    return best


def g_consonants(r):
    s = _s(r, r.randint(1, 12), "abcdeiz")
    return [s, r.randint(0, len(s))]


def v_consonants(tests):
    for t in tests:
        s, k = t["args"]
        assert 1 <= len(s) <= 100000 and s.isalpha() and s.islower()
        assert 0 <= k <= len(s)


CHECKS["longest-substring-limited-consonants"] = (b_consonants, g_consonants, "exact")
VALIDATE["longest-substring-limited-consonants"] = v_consonants


p = add(
    id="equal-substring-within-budget", title="Equal Substring Within a Budget", diff="Easy", topic="Sliding Window",
    fn="equalSubstring", params=[("s", "string"), ("t", "string"), ("maxCost", "int")], ret="int", cmp="exact", tier="extra",
    desc="<p>The strings <code>s</code> and <code>t</code> have the same length. Turning <code>s[i]</code> into <code>t[i]</code> costs <code>|s[i] - t[i]|</code>, the absolute difference of their positions in the alphabet (so <code>a</code> to <code>d</code> costs 3).</p><p>You may spend at most <code>maxCost</code> in total. Choose a substring of <code>s</code>, i.e. a range of indices <code>[i, j]</code>, and convert it to the substring of <code>t</code> at the same indices. Return the maximum length of a range whose conversion cost is at most <code>maxCost</code>.</p><pre>s = \"abcd\", t = \"bcdf\", maxCost = 3\ncosts per index: 1 1 1 2\nindices 0..2 cost 3\nresult = 3</pre>",
    constraints=["1 &le; s.length = t.length &le; 100,000", "s and t contain only lowercase English letters", "0 &le; maxCost &le; 10<sup>9</sup>"],
    hints=["First turn the two strings into one array of per-index costs.",
           "The question becomes: longest subarray of non-negative numbers with sum at most <code>maxCost</code>.",
           "Use two pointers. Add the cost at <code>right</code>, and while the total exceeds <code>maxCost</code> subtract the cost at <code>left</code> and advance it."],
    editorial=["Compute <code>cost[i] = |s[i] - t[i]|</code>. All costs are non-negative, so the cost of a range grows when it is extended and shrinks when it is trimmed. This is the standard variable-size window: expand to the right, and contract from the left only while the budget is exceeded.",
               "The window never needs to move left, so each index is added once and removed at most once. Time O(n), space O(1) if you compute the costs on the fly instead of storing them."],
    time="O(n)", space="O(1)",
    solution='''def equalSubstring(s, t, maxCost):
    left = 0
    spent = 0
    best = 0
    for right in range(len(s)):
        spent += abs(ord(s[right]) - ord(t[right]))
        while spent > maxCost:
            spent -= abs(ord(s[left]) - ord(t[left]))
            left += 1
        best = max(best, right - left + 1)
    return best
''',
    tests=[["abcd", "bcdf", 3], ["abcd", "cdef", 3], ["abcd", "acde", 0], ["a", "a", 0], ["a", "z", 24], ["a", "z", 25], ["aaaa", "zzzz", 100],
           ["krrgw", "zjxss", 19], ["pxezla", "loewbi", 25], ["abc", "abc", 0], ["zzzz", "aaaa", 50]],
)
_r = rnd(3103)
p["tests"].append([_s(_r, 8000, LOWER), _s(_r, 8000, LOWER), 4000])
_x = _s(_r, 8000, "abcde")
p["tests"].append([_x, "".join(chr(97 + min(25, max(0, ord(c) - 97 + _r.randint(-1, 1)))) for c in _x), 1000])
p["tests"].append(["m" * 8000, "m" * 7999 + "n", 0])


def b_equal_sub(s, t, maxCost):
    best = 0
    for i in range(len(s)):
        for j in range(i, len(s)):
            if sum(abs(ord(s[q]) - ord(t[q])) for q in range(i, j + 1)) <= maxCost:
                best = max(best, j - i + 1)
    return best


def g_equal_sub(r):
    n = r.randint(1, 9)
    return [_s(r, n, "abcdefg"), _s(r, n, "abcdefg"), r.randint(0, 14)]


def v_equal_sub(tests):
    for t in tests:
        s, u, c = t["args"]
        assert len(s) == len(u) and 1 <= len(s) <= 100000
        assert s.islower() and u.islower() and s.isalpha() and u.isalpha()
        assert 0 <= c <= 10 ** 9


CHECKS["equal-substring-within-budget"] = (b_equal_sub, g_equal_sub, "exact")
VALIDATE["equal-substring-within-budget"] = v_equal_sub


# ---------------------------------------------------------------- MEDIUM

p = add(
    id="longest-substring-at-most-k-distinct", title="Longest Substring With At Most K Distinct Characters", diff="Medium", topic="Sliding Window",
    fn="longestKDistinct", params=[("s", "string"), ("k", "int")], ret="int", cmp="exact", tier="must",
    desc="<p>Given a string <code>s</code> of lowercase letters and an integer <code>k</code>, return the length of the longest substring that contains at most <code>k</code> different characters.</p><pre>s = \"eceba\", k = 2\n\"ece\" has two distinct characters\nresult = 3</pre><p>If <code>k = 0</code> no non-empty substring qualifies, so the answer is <code>0</code>.</p>",
    constraints=["1 &le; s.length &le; 100,000", "s contains only lowercase English letters", "0 &le; k &le; 26"],
    hints=["Try every start and extend until the substring has too many distinct letters. That is O(n&sup2;) at least. Can the start pointer avoid going back?",
           "If a window has more than k distinct characters, every longer window that contains it does too. So you only ever need to move the left end forward.",
           "Keep a count per character inside the window and the number of characters with a non-zero count. When that number exceeds k, remove characters from the left until it is back to k."],
    editorial=["Maintain a window <code>[left, right]</code> and a frequency table of its characters. Add <code>s[right]</code>; if the number of distinct characters becomes larger than <code>k</code>, shrink the window from the left, decrementing counts and dropping a character from the table when its count reaches zero. After the window is valid again, its length is a candidate for the answer.",
               "Validity is monotone: any substring of a valid window is also valid, so the smallest valid left end never moves backward. Each index is added once and removed at most once, giving O(n) time. The table has at most k + 1 entries, so the space is O(min(n, k))."],
    time="O(n)", space="O(k)",
    solution='''def longestKDistinct(s, k):
    if k == 0:
        return 0
    cnt = {}
    left = 0
    best = 0
    for right, ch in enumerate(s):
        cnt[ch] = cnt.get(ch, 0) + 1
        while len(cnt) > k:
            c = s[left]
            cnt[c] -= 1
            if cnt[c] == 0:
                del cnt[c]
            left += 1
        best = max(best, right - left + 1)
    return best
''',
    tests=[["eceba", 2], ["aa", 1], ["a", 0], ["a", 1], ["abc", 0], ["abc", 3], ["abc", 26], ["abaccc", 2], ["aabbcc", 1], ["aabbcc", 2],
           ["abcabcabc", 2], ["zzzzyyyyxxxx", 2]],
)
_r = rnd(3104)
p["tests"].append([_s(_r, 8000, LOWER), 5])
p["tests"].append([_s(_r, 8000, "abcd"), 3])
p["tests"].append(["a" * 4000 + "b" * 2000 + "c" * 2000, 2])


def b_kdistinct(s, k):
    best = 0
    for i in range(len(s)):
        for j in range(i, len(s)):
            if len(set(s[i:j + 1])) <= k:
                best = max(best, j - i + 1)
    return best


def g_kdistinct(r):
    return [_s(r, r.randint(1, 12), "abcde"), r.randint(0, 5)]


def v_kdistinct(tests):
    for t in tests:
        s, k = t["args"]
        assert 1 <= len(s) <= 100000 and s.isalpha() and s.islower()
        assert 0 <= k <= 26


CHECKS["longest-substring-at-most-k-distinct"] = (b_kdistinct, g_kdistinct, "exact")
VALIDATE["longest-substring-at-most-k-distinct"] = v_kdistinct


p = add(
    id="longest-subarray-each-value-at-most-k-times", title="Longest Subarray With Bounded Frequencies", diff="Medium", topic="Sliding Window",
    fn="longestBoundedFrequency", params=[("nums", "int[]"), ("k", "int")], ret="int", cmp="exact",
    desc="<p>A subarray is <em>good</em> if no value occurs in it more than <code>k</code> times. Given <code>nums</code> and <code>k</code>, return the length of the longest good subarray.</p><pre>nums = [1, 2, 3, 1, 2, 3, 1, 2], k = 2\n[1, 2, 3, 1, 2, 3] is good (each value twice)\nadding the next 1 would make it three\nresult = 6</pre>",
    constraints=["1 &le; nums.length &le; 100,000", "-10<sup>9</sup> &le; nums[i] &le; 10<sup>9</sup>", "1 &le; k &le; nums.length"],
    hints=["With k = 1 this is the classic longest subarray of distinct values. Think about how that solution generalises.",
           "If a window is good, all of its sub-windows are good. If it is bad, any window containing it is bad.",
           "Keep a frequency map for the window. After adding <code>nums[right]</code>, if its count is now above k, shrink from the left until that same value's count is back to k."],
    editorial=["Only the value that was just added can break the rule, so after extending the window to the right, check the count of <code>nums[right]</code>. If it exceeds <code>k</code>, advance <code>left</code>, decrementing counts, until that count drops back to <code>k</code> (this happens exactly when the earliest copy of that value in the window is removed).",
               "The goodness property is hereditary (sub-windows of good windows are good), which is why the left pointer never has to retreat. Each element is added once and removed at most once, giving O(n) time and O(n) space for the map."],
    time="O(n)", space="O(n)",
    solution='''def longestBoundedFrequency(nums, k):
    cnt = {}
    left = 0
    best = 0
    for right, x in enumerate(nums):
        cnt[x] = cnt.get(x, 0) + 1
        while cnt[x] > k:
            cnt[nums[left]] -= 1
            left += 1
        best = max(best, right - left + 1)
    return best
''',
    tests=[[[1, 2, 3, 1, 2, 3, 1, 2], 2], [[1, 2, 1, 2, 1, 2, 1, 2], 1], [[5, 5, 5, 5, 5, 5, 5], 4], [[7], 1], [[1, 1, 1], 1], [[1, 1, 1], 3],
           [[1, 2, 3, 4], 1], [[2, 2, 1, 2, 2, 1, 1], 2], [[-5, 5, -5, 5, -5], 2], [[1000000000, -1000000000, 1000000000], 1],
           [[3, 1, 3, 1, 3, 1, 3, 2, 2, 2, 2], 2]],
)
_r = rnd(3105)
p["tests"].append([[_r.randint(1, 50) for _ in range(8000)], 150])
p["tests"].append([[_r.randint(-10 ** 9, 10 ** 9) for _ in range(8000)], 1])
p["tests"].append([[_r.randint(1, 3) for _ in range(8000)], 2000])


def b_bounded_freq(nums, k):
    best = 0
    for i in range(len(nums)):
        for j in range(i, len(nums)):
            if max(Counter(nums[i:j + 1]).values()) <= k:
                best = max(best, j - i + 1)
    return best


def g_bounded_freq(r):
    n = r.randint(1, 11)
    return [[r.randint(1, 4) for _ in range(n)], r.randint(1, n)]


def v_bounded_freq(tests):
    for t in tests:
        a, k = t["args"]
        assert 1 <= len(a) <= 100000 and all(-10 ** 9 <= x <= 10 ** 9 for x in a)
        assert 1 <= k <= len(a)


CHECKS["longest-subarray-each-value-at-most-k-times"] = (b_bounded_freq, g_bounded_freq, "exact")
VALIDATE["longest-subarray-each-value-at-most-k-times"] = v_bounded_freq


p = add(
    id="longest-subarray-pairwise-disjoint-bits", title="Longest Subarray With Pairwise Disjoint Bits", diff="Medium", topic="Sliding Window",
    fn="longestDisjointBits", params=[("nums", "int[]")], ret="int", cmp="exact", tier="extra",
    desc="<p>A subarray is <em>disjoint</em> if for every two elements at different positions inside it, their bitwise AND is <code>0</code> (no bit is set in two elements). A subarray of length 1 is always disjoint.</p><p>Return the length of the longest disjoint subarray of <code>nums</code>.</p><pre>nums = [1, 3, 8, 48, 10]\n[3, 8, 48] : 3&amp;8 = 0, 3&amp;48 = 0, 8&amp;48 = 0\nresult = 3</pre>",
    constraints=["1 &le; nums.length &le; 100,000", "0 &le; nums[i] &le; 10<sup>9</sup>"],
    hints=["Checking all pairs inside every subarray is far too slow. What does 'no two elements share a bit' say about the union of their bits?",
           "In a disjoint window, the bitwise OR of all elements equals their XOR and equals their sum. You can keep it as a single mask.",
           "Before adding <code>nums[right]</code>, while <code>mask &amp; nums[right] != 0</code> remove <code>nums[left]</code> from the mask (<code>mask ^= nums[left]</code>) and advance left. Then add the new element to the mask."],
    editorial=["Keep a mask holding the set of bits used by the elements currently in the window. Because the window is disjoint, every bit belongs to exactly one element, so removing an element is just <code>mask ^= element</code> and adding one is <code>mask |= element</code>.",
               "For a new element <code>x</code>, any conflict with some earlier element shows up as <code>mask &amp; x != 0</code>. Shrink from the left until there is no conflict, then include <code>x</code>. Disjointness is hereditary (sub-windows of a disjoint window stay disjoint), so the left pointer only moves forward. Each element is pushed and popped at most once, so the time is O(n) and the space O(1). An element equal to 0 never conflicts with anything."],
    time="O(n)", space="O(1)",
    solution='''def longestDisjointBits(nums):
    mask = 0
    left = 0
    best = 0
    for right, x in enumerate(nums):
        while mask & x:
            mask ^= nums[left]
            left += 1
        mask |= x
        best = max(best, right - left + 1)
    return best
''',
    tests=[[[1, 3, 8, 48, 10]], [[3, 1, 5, 11, 13]], [[5]], [[0]], [[0, 0, 0, 0]], [[7, 7, 7]], [[1, 2, 4, 8, 16]], [[1, 2, 4, 1, 2, 4]],
           [[1000000000, 1, 0, 1000000000]], [[6, 1, 8, 2, 5]], [[1, 1, 2, 2, 4, 4]], [[2, 4, 0, 1, 2, 4, 8, 0, 3]]],
)
_r = rnd(3106)
p["tests"].append([[1 << _r.randint(0, 29) for _ in range(8000)]])
p["tests"].append([[(1 << _r.randint(0, 29)) | (1 << _r.randint(0, 29)) for _ in range(8000)]])
p["tests"].append([[(1 << (i % 30)) for i in range(8000)]])


def b_disjoint(nums):
    best = 0
    n = len(nums)
    for i in range(n):
        for j in range(i, n):
            seg = nums[i:j + 1]
            if all(seg[a] & seg[b] == 0 for a in range(len(seg)) for b in range(a + 1, len(seg))):
                best = max(best, j - i + 1)
    return best


def g_disjoint(r):
    return [[r.randint(0, 15) for _ in range(r.randint(1, 10))]]


def v_disjoint(tests):
    for t in tests:
        a = t["args"][0]
        assert 1 <= len(a) <= 100000 and all(0 <= x <= 10 ** 9 for x in a)


CHECKS["longest-subarray-pairwise-disjoint-bits"] = (b_disjoint, g_disjoint, "exact")
VALIDATE["longest-subarray-pairwise-disjoint-bits"] = v_disjoint


p = add(
    id="max-frequency-after-k-increments", title="Maximum Frequency After K Increments", diff="Medium", topic="Sliding Window",
    fn="maxFrequencyAfterIncrements", params=[("nums", "int[]"), ("k", "int")], ret="int", cmp="exact",
    desc="<p>In one operation you pick any element of <code>nums</code> and increase it by <code>1</code>. You may perform at most <code>k</code> operations in total.</p><p>Return the largest possible frequency of any single value in the array after the operations, i.e. how many elements can be made equal to one common value.</p><pre>nums = [1, 2, 4], k = 5\n1 -> 4 costs 3, 2 -> 4 costs 2, total 5\nall three become 4\nresult = 3</pre>",
    constraints=["1 &le; nums.length &le; 100,000", "1 &le; nums[i] &le; 100,000", "0 &le; k &le; 100,000"],
    hints=["Elements can only go up, so the common value is never smaller than the biggest element you pick. Which elements are the cheapest to raise to a given target?",
           "Sort the array. For a target equal to <code>nums[right]</code>, the cheapest group to raise is a contiguous block ending at <code>right</code>.",
           "For the window <code>[left, right]</code> the cost is <code>nums[right] * length - windowSum</code>. Shrink from the left while the cost exceeds k; the answer is the longest window seen."],
    editorial=["After sorting, if the final common value is <code>v = nums[right]</code> then the elements worth raising are the ones closest to <code>v</code> from below, which form a block <code>nums[left..right]</code>. Raising all of them to <code>v</code> costs <code>v * (right - left + 1) - sum(nums[left..right])</code>.",
               "For a fixed <code>right</code> the cost grows as <code>left</code> decreases, and for a fixed <code>left</code> it grows as <code>right</code> increases. Hence the best left end is monotone and a two-pointer sweep finds the largest affordable window. Sorting dominates: O(n log n) time, O(1) extra space beyond the sorted copy."],
    time="O(n log n)", space="O(n)",
    solution='''def maxFrequencyAfterIncrements(nums, k):
    a = sorted(nums)
    left = 0
    total = 0
    best = 1
    for right, v in enumerate(a):
        total += v
        while v * (right - left + 1) - total > k:
            total -= a[left]
            left += 1
        best = max(best, right - left + 1)
    return best
''',
    tests=[[[1, 2, 4], 5], [[1, 4, 8, 13], 5], [[3, 9, 6], 2], [[5], 0], [[5], 100], [[1, 1, 1], 0], [[1, 100000], 99999], [[1, 100000], 99998],
           [[2, 2, 2, 7], 4], [[9, 1, 5, 1, 5], 8], [[4, 4, 4, 5, 6, 6], 0]],
)
_r = rnd(3107)
p["tests"].append([[_r.randint(1, 100000) for _ in range(8000)], 100000])
p["tests"].append([[_r.randint(1, 10) for _ in range(8000)], 77])
p["tests"].append([[100000 - i % 40 for i in range(8000)], 100000])


def b_max_freq(nums, k):
    best = 1
    for v in set(nums):
        costs = sorted(v - x for x in nums if x <= v)
        used = 0
        cnt = 0
        for c in costs:
            if used + c > k:
                break
            used += c
            cnt += 1
        best = max(best, cnt)
    return best


def g_max_freq(r):
    return [[r.randint(1, 12) for _ in range(r.randint(1, 9))], r.randint(0, 20)]


def v_max_freq(tests):
    for t in tests:
        a, k = t["args"]
        assert 1 <= len(a) <= 100000 and all(1 <= x <= 100000 for x in a)
        assert 0 <= k <= 100000


CHECKS["max-frequency-after-k-increments"] = (b_max_freq, g_max_freq, "exact")
VALIDATE["max-frequency-after-k-increments"] = v_max_freq


p = add(
    id="longest-subarray-sum-at-most-k-with-negatives", title="Longest Subarray With Sum At Most K (Negatives Allowed)", diff="Medium", topic="Sliding Window",
    fn="longestSumAtMostWithNegatives", params=[("nums", "int[]"), ("k", "int")], ret="int", cmp="exact", tier="extra",
    desc="<p>Given an integer array <code>nums</code> that may contain negative numbers, and an integer <code>k</code> (which may also be negative), return the length of the longest contiguous subarray whose sum is at most <code>k</code>. If no non-empty subarray qualifies, return <code>0</code>.</p><p>Careful: with negative numbers the usual two-pointer window no longer works, because removing an element from the left can make the sum larger.</p><pre>nums = [4, -3, 2, -1, 5], k = 2\n[-3, 2, -1] sums to -2, and [4, -3, 2, -1] sums to 2\nresult = 4</pre>",
    constraints=["1 &le; nums.length &le; 100,000", "-10,000 &le; nums[i] &le; 10,000", "-10<sup>9</sup> &le; k &le; 10<sup>9</sup>"],
    hints=["Test the window idea on <code>[5, -10, 1]</code> with a small k: when the sum is too large, is dropping the leftmost element guaranteed to help?",
           "Switch to prefix sums <code>P</code>. A subarray <code>(i, j]</code> has sum <code>P[j] - P[i]</code>, so you need the smallest <code>i &lt; j</code> with <code>P[i] &ge; P[j] - k</code>.",
           "The smallest such i is always a new running maximum of the prefix sums (every earlier prefix is smaller than the target). Keep those running-maximum prefixes in a list; their values increase, so binary search finds the first one that is large enough."],
    editorial=["Without sign restrictions the sum of a window is not monotone in either end, so shrinking from the left cannot be trusted. Use prefix sums instead: the subarray between prefix indices <code>i &lt; j</code> has sum <code>P[j] - P[i]</code>, and it is acceptable when <code>P[i] &ge; P[j] - k</code>. For each <code>j</code> we want the smallest such <code>i</code>.",
               "Let <code>i*</code> be the smallest index with <code>P[i*] &ge; target</code>. Every earlier prefix is smaller than the target and therefore smaller than <code>P[i*]</code>, so <code>i*</code> is a strict prefix maximum. Store only the strict prefix maxima (indices and values, both increasing) and binary-search the target among the values. This is a sliding-window-style idea (best left end for each right end) with the monotonic structure supplied by prefix maxima. Time O(n log n), space O(n)."],
    time="O(n log n)", space="O(n)",
    solution='''def longestSumAtMostWithNegatives(nums, k):
    from bisect import bisect_left
    idxs = []
    vals = []
    pref = 0
    prefix = [0]
    for x in nums:
        pref += x
        prefix.append(pref)
    best = 0
    for j in range(1, len(prefix)):
        i = j - 1
        if not vals or prefix[i] > vals[-1]:
            idxs.append(i)
            vals.append(prefix[i])
        pos = bisect_left(vals, prefix[j] - k)
        if pos < len(vals):
            best = max(best, j - idxs[pos])
    return best
''',
    tests=[[[4, -3, 2, -1, 5], 2], [[5], 4], [[5], 5], [[-5], -6], [[-5], -5], [[5, -10, 1], 0], [[1, 2, 3], -1], [[-1, -1, -1], -2],
           [[3, -3, 3, -3, 3], 0], [[10, -10, 10, -10], -1], [[2, -1, -1, 2, -1, -1, 2], 0], [[-4, 5, -4, 5, -4], 1]],
)
_r = rnd(3108)
p["tests"].append([[_r.randint(-10000, 10000) for _ in range(8000)], 5000])
p["tests"].append([[_r.randint(-10, 12) for _ in range(8000)], -300])
p["tests"].append([[_r.randint(-5, 5) for _ in range(8000)], 0])


def b_neg_at_most(nums, k):
    best = 0
    for i in range(len(nums)):
        s = 0
        for j in range(i, len(nums)):
            s += nums[j]
            if s <= k:
                best = max(best, j - i + 1)
    return best


def g_neg_at_most(r):
    return [[r.randint(-6, 6) for _ in range(r.randint(1, 10))], r.randint(-12, 12)]


def v_neg_at_most(tests):
    for t in tests:
        a, k = t["args"]
        assert 1 <= len(a) <= 100000 and all(-10000 <= x <= 10000 for x in a)
        assert -10 ** 9 <= k <= 10 ** 9


CHECKS["longest-subarray-sum-at-most-k-with-negatives"] = (b_neg_at_most, g_neg_at_most, "exact")
VALIDATE["longest-subarray-sum-at-most-k-with-negatives"] = v_neg_at_most


p = add(
    id="max-sum-subarray-unique-elements", title="Maximum Sum of a Subarray With Unique Elements", diff="Medium", topic="Sliding Window",
    fn="maxUniqueSubarraySum", params=[("nums", "int[]")], ret="int", cmp="exact",
    desc="<p>Choose a contiguous, non-empty subarray of <code>nums</code> in which all elements are different from each other. Its score is the sum of its elements. Return the maximum score you can obtain.</p><pre>nums = [4, 2, 4, 5, 6]\n[2, 4, 5, 6] has distinct values and sum 17\nresult = 17</pre>",
    constraints=["1 &le; nums.length &le; 100,000", "1 &le; nums[i] &le; 10,000"],
    hints=["A subarray with a repeated value is not allowed, but every sub-subarray of an allowed subarray is allowed.",
           "Keep a window of distinct values together with its sum. When the incoming value is already inside the window, drop elements from the left until the earlier copy is gone.",
           "Because all numbers are positive, the best valid window ending at each position is the longest one, so after fixing the duplicate just compare the running sum with the best so far."],
    editorial=["Use a window with a set of its values (or a map of last positions) and its running sum. When <code>nums[right]</code> is already in the set, advance <code>left</code>, removing values and subtracting them, until the duplicate has been removed; then add <code>nums[right]</code>. Record the sum.",
               "Positivity matters: for a fixed right end, a longer valid window has a larger sum, so it is enough to look at the maximal valid window ending at each index. With a map of last occurrences the left end can jump straight past the previous copy. Time O(n), space O(min(n, 10,000)). If negative values were allowed, shrinking would not be optimal and a different approach would be needed."],
    time="O(n)", space="O(n)",
    solution='''def maxUniqueSubarraySum(nums):
    seen = set()
    left = 0
    cur = 0
    best = 0
    for x in nums:
        while x in seen:
            seen.remove(nums[left])
            cur -= nums[left]
            left += 1
        seen.add(x)
        cur += x
        best = max(best, cur)
    return best
''',
    tests=[[[4, 2, 4, 5, 6]], [[5, 2, 1, 2, 5, 2, 1, 2, 5]], [[7]], [[3, 3, 3]], [[1, 2, 3, 4, 5]], [[10000, 10000]], [[1, 2, 1, 3, 1, 4]],
           [[5, 1, 5, 9, 1, 9]], [[2, 1, 2, 1, 2, 1, 3]], [[6, 1, 2, 3, 6]], [[9, 8, 7, 9, 1, 2, 3, 4]]],
)
_r = rnd(3109)
p["tests"].append([[_r.randint(1, 10000) for _ in range(8000)]])
p["tests"].append([[_r.randint(1, 100) for _ in range(8000)]])
p["tests"].append([[(i % 9999) + 1 for i in range(8000)]])


def b_unique_sum(nums):
    best = 0
    for i in range(len(nums)):
        for j in range(i, len(nums)):
            seg = nums[i:j + 1]
            if len(set(seg)) == len(seg):
                best = max(best, sum(seg))
    return best


def g_unique_sum(r):
    return [[r.randint(1, 7) for _ in range(r.randint(1, 11))]]


def v_unique_sum(tests):
    for t in tests:
        a = t["args"][0]
        assert 1 <= len(a) <= 100000 and all(1 <= x <= 10000 for x in a)


CHECKS["max-sum-subarray-unique-elements"] = (b_unique_sum, g_unique_sum, "exact")
VALIDATE["max-sum-subarray-unique-elements"] = v_unique_sum


# ---------------------------------------------------------------- HARD

p = add(
    id="max-fruits-harvested-within-k-steps", title="Maximum Fruits Harvested Within K Steps", diff="Hard", topic="Sliding Window",
    fn="maxFruits", params=[("fruits", "int[][]"), ("startPos", "int"), ("k", "int")], ret="int", cmp="exact", tier="extra",
    desc="<p>Fruit trees stand along an infinite number line. <code>fruits[i] = [position, amount]</code> says that position <code>position</code> holds <code>amount</code> fruits. The rows are sorted by position and all positions are different.</p><p>You start at <code>startPos</code>. One step moves you one unit to the left or to the right. You may take at most <code>k</code> steps in total. Whenever you stand on a position you collect all the fruit there (each position can be harvested only once). Return the maximum total amount of fruit you can collect.</p><pre>fruits = [[2, 8], [6, 3], [8, 6]], startPos = 5, k = 4\nwalk right: 5 -> 6 -> 8 (3 steps) collects 3 + 6\nresult = 9</pre>",
    constraints=["1 &le; fruits.length &le; 100,000", "0 &le; fruits[i][0] &le; 200,000, positions strictly increasing", "1 &le; fruits[i][1] &le; 10,000", "0 &le; startPos &le; 200,000", "0 &le; k &le; 200,000"],
    hints=["Whatever you do, the set of positions you visit is one contiguous interval around the start. So the answer is the best interval you can afford.",
           "To cover the interval from position L to R, starting at S, you go to the nearer end first and then sweep to the other: cost <code>(R - L) + min(|S - L|, |S - R|)</code> (when S lies outside the interval, this is also valid).",
           "Slide a window over the fruit rows. For each right index, move the left index forward while the cost of covering <code>[pos[left], pos[right]]</code> exceeds k, and keep the best fruit sum of the window using a running total."],
    editorial=["The visited positions always form an interval <code>[L, R]</code> that contains the start (or is reached from it). The cheapest way to harvest all of it is to walk to the closer endpoint first, then walk across to the other one, so the cost is <code>(R - L) + min(|S - L|, |S - R|)</code>. Using other routes (e.g. zig-zagging) only costs more. It is enough to consider intervals whose endpoints are fruit positions, because shrinking an interval to its outermost fruits never hurts.",
               "For the fruit window <code>[left, right]</code> this cost is non-decreasing in <code>right</code> and non-increasing in <code>left</code>, so a two-pointer sweep applies: add the amount at <code>right</code>, move <code>left</code> forward while the cost is above <code>k</code> (the window may become empty), and record the sum. Time O(n), space O(1)."],
    time="O(n)", space="O(1)",
    solution='''def maxFruits(fruits, startPos, k):
    n = len(fruits)
    left = 0
    total = 0
    best = 0
    for right in range(n):
        total += fruits[right][1]
        while left <= right:
            lo = fruits[left][0]
            hi = fruits[right][0]
            cost = (hi - lo) + min(abs(startPos - lo), abs(startPos - hi))
            if cost <= k:
                break
            total -= fruits[left][1]
            left += 1
        best = max(best, total)
    return best
''',
    tests=[[[[2, 8], [6, 3], [8, 6]], 5, 4], [[[0, 9], [4, 1], [5, 7], [6, 2], [7, 4], [10, 9]], 5, 4], [[[0, 3], [6, 4], [8, 5]], 3, 2], [[[5, 7]], 5, 0],
           [[[5, 7]], 4, 0], [[[5, 7]], 4, 1], [[[5, 7]], 0, 4], [[[1, 5], [2, 5], [3, 5]], 2, 1], [[[1, 5], [2, 5], [3, 5]], 100, 97], [[[0, 1], [100, 50]], 50, 50],
           [[[0, 1], [100, 50]], 50, 49], [[[2, 4], [5, 1], [9, 8], [11, 2]], 6, 7]],
)
_r = rnd(3110)
_pos = sorted(_r.sample(range(0, 200001), 3000))
p["tests"].append([[[x, _r.randint(1, 10000)] for x in _pos], 100000, 60000])
_pos = sorted(_r.sample(range(0, 20001), 3000))
p["tests"].append([[[x, _r.randint(1, 10000)] for x in _pos], 5000, 9000])
p["tests"].append([[[i * 3, 1 + i % 7] for i in range(3000)], 4500, 200000])


def b_fruits(fruits, startPos, k):
    amount = {x: a for x, a in fruits}
    best = 0
    for a in range(0, k + 1):
        for b in range(0, k + 1):
            if min(2 * a + b, a + 2 * b) <= k:
                lo, hi = startPos - a, startPos + b
                best = max(best, sum(v for x, v in amount.items() if lo <= x <= hi))
    return best


def g_fruits(r):
    pos = sorted(r.sample(range(0, 16), r.randint(1, 7)))
    return [[[x, r.randint(1, 9)] for x in pos], r.randint(0, 15), r.randint(0, 12)]


def v_fruits(tests):
    for t in tests:
        f, s, k = t["args"]
        assert 1 <= len(f) <= 100000
        assert all(0 <= x <= 200000 and 1 <= a <= 10000 for x, a in f)
        assert all(f[i][0] < f[i + 1][0] for i in range(len(f) - 1))
        assert 0 <= s <= 200000 and 0 <= k <= 200000


CHECKS["max-fruits-harvested-within-k-steps"] = (b_fruits, g_fruits, "exact")
VALIDATE["max-fruits-harvested-within-k-steps"] = v_fruits


p = add(
    id="max-equal-elements-with-k-adjustments", title="Maximum Equal Elements With K Adjustments", diff="Hard", topic="Sliding Window",
    fn="maxEqualWithAdjustments", params=[("nums", "int[]"), ("k", "int")], ret="int", cmp="exact", tier="extra",
    desc="<p>In one operation you choose an element of <code>nums</code> and either increase it by <code>1</code> or decrease it by <code>1</code>. You may perform at most <code>k</code> operations in total.</p><p>Return the largest number of elements that can be made equal to one common value (the value itself is your choice and may be any integer).</p><pre>nums = [1, 2, 6, 4], k = 3\nmake 1, 2, 4 all equal to 2: costs 1 + 0 + 2 = 3\nresult = 3</pre>",
    constraints=["1 &le; nums.length &le; 100,000", "1 &le; nums[i] &le; 10<sup>9</sup>", "0 &le; k &le; 2 &times; 10<sup>9</sup>"],
    hints=["Order does not matter, so sort first. Which elements should be made equal to each other? Elements that are close in sorted order.",
           "For a sorted block <code>[l, r]</code> the cheapest common value is its median, and the cost is the sum of distances to that median. Prefix sums let you compute this in O(1).",
           "The cost of a block only grows when you widen it. So use two pointers: for each right end, advance left while the median cost is above k."],
    editorial=["Sort the array. The elements that end up equal form, w.l.o.g., a contiguous block of the sorted order (swapping a far element for a nearer one never increases the cost). For a block, the total adjustment distance <code>sum |x - v|</code> is minimised at the median <code>v = a[m]</code> with <code>m = (l + r) // 2</code>.",
               "With prefix sums <code>P</code>, the cost is <code>a[m] * (m - l) - (P[m] - P[l]) + (P[r + 1] - P[m + 1]) - a[m] * (r - m)</code>. Widening a block can only increase this cost, so the left end of the best block is monotone in the right end, and a two-pointer sweep suffices. Total time O(n log n) for sorting plus O(n) for the sweep, O(n) space. The block costs can reach about 10^14, so use 64-bit arithmetic in fixed-width languages."],
    time="O(n log n)", space="O(n)",
    solution='''def maxEqualWithAdjustments(nums, k):
    a = sorted(nums)
    n = len(a)
    pre = [0] * (n + 1)
    for i, x in enumerate(a):
        pre[i + 1] = pre[i] + x

    def cost(l, r):
        m = (l + r) // 2
        left_part = a[m] * (m - l) - (pre[m] - pre[l])
        right_part = (pre[r + 1] - pre[m + 1]) - a[m] * (r - m)
        return left_part + right_part

    left = 0
    best = 1
    for right in range(n):
        while cost(left, right) > k:
            left += 1
        best = max(best, right - left + 1)
    return best
''',
    tests=[[[1, 2, 6, 4], 3], [[1, 4, 4, 2, 4], 0], [[5], 0], [[5], 1000], [[1, 10], 8], [[1, 10], 9], [[1, 1000000000], 999999999],
           [[1, 1000000000], 999999998], [[1, 2, 3, 4, 5], 6], [[1, 2, 3, 4, 5], 5], [[7, 7, 7, 1, 20], 6], [[10, 1, 10, 1, 10, 1], 9]],
)
_r = rnd(3111)
p["tests"].append([[_r.randint(1, 10 ** 9) for _ in range(8000)], 10 ** 9])
p["tests"].append([[_r.randint(1, 1000) for _ in range(8000)], 100000])
p["tests"].append([[_r.randint(1, 10 ** 6) for _ in range(8000)], 2 * 10 ** 9])


def b_equalize(nums, k):
    best = 1
    for v in set(nums):
        costs = sorted(abs(x - v) for x in nums)
        used = 0
        cnt = 0
        for c in costs:
            if used + c > k:
                break
            used += c
            cnt += 1
        best = max(best, cnt)
    return best


def g_equalize(r):
    return [[r.randint(1, 15) for _ in range(r.randint(1, 9))], r.randint(0, 25)]


def v_equalize(tests):
    for t in tests:
        a, k = t["args"]
        assert 1 <= len(a) <= 100000 and all(1 <= x <= 10 ** 9 for x in a)
        assert 0 <= k <= 2 * 10 ** 9


CHECKS["max-equal-elements-with-k-adjustments"] = (b_equalize, g_equalize, "exact")
VALIDATE["max-equal-elements-with-k-adjustments"] = v_equalize
