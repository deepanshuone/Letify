"""Problem bank for Abhyas.

Each problem has a reference solution (Python). Expected outputs for every test
are produced by running that reference, then the reference is cross-checked
against brute force on small random inputs (see checks at the bottom).

To add a problem: copy any `add(...)` block, give it a new id, write the
statement, inputs and reference solution, then run `python3 build.py`.
"""
import random
from collections import deque

P = []


def add(**kw):
    P.append(kw)


def rnd(seed):
    return random.Random(seed)


# ---------------------------------------------------------------- EASY

add(
    id="contains-duplicate", title="Contains Duplicate", diff="Easy", topic="Arrays & Hashing",
    fn="containsDuplicate", params=[("nums", "int[]")], ret="bool", cmp="exact",
    desc="<p>Given an integer array <code>nums</code>, return <code>true</code> if any value appears at least twice, and <code>false</code> if every element is distinct.</p>",
    constraints=["1 &le; nums.length &le; 10,000", "-10<sup>9</sup> &le; nums[i] &le; 10<sup>9</sup>"],
    hints=["Comparing every pair works, but it takes O(n&sup2;) time. Can you remember what you have already seen?",
           "A hash set answers 'have I seen this value?' in O(1).",
           "Alternative: sort the array first, then only neighbours can be equal."],
    editorial=["Walk through the array and keep a set of values seen so far. If the current value is already in the set, a duplicate exists. Otherwise add it and move on.",
               "Sorting also works (check adjacent pairs) at O(n log n) time with no extra set, which is a useful trade-off when memory is tight."],
    time="O(n)", space="O(n)",
    solution='''def containsDuplicate(nums):
    seen = set()
    for x in nums:
        if x in seen:
            return True
        seen.add(x)
    return False
''',
    tests=[[[1, 2, 3, 1]], [[1, 2, 3, 4]], [[1, 1, 1, 3, 3, 4, 3, 2, 4, 2]], [[7]], [[-5, 0, 5, -5]],
           [[10 ** 9, -10 ** 9, 0, 10 ** 9]]],
)
_r = rnd(1)
_a = list(range(10000)); _r.shuffle(_a)
P[-1]["tests"].append([_a[:-1] + [_a[0]]])

add(
    id="valid-anagram", title="Valid Anagram", diff="Easy", topic="Arrays & Hashing",
    fn="isAnagram", params=[("s", "string"), ("t", "string")], ret="bool", cmp="exact",
    desc="<p>Given two lowercase strings <code>s</code> and <code>t</code>, return <code>true</code> if <code>t</code> is an anagram of <code>s</code>, meaning it uses exactly the same letters the same number of times in any order.</p>",
    constraints=["1 &le; s.length, t.length &le; 10,000", "s and t contain only lowercase English letters"],
    hints=["If the lengths differ, the answer is immediately false.",
           "Two strings are anagrams when every letter has the same count in both.",
           "Only 26 letters exist, so a fixed-size count array is enough."],
    editorial=["Count how many times each letter occurs in <code>s</code>, then walk through <code>t</code> and subtract. If a count would go below zero, <code>t</code> has a letter that <code>s</code> does not have enough of.",
               "Sorting both strings and comparing also works, at O(n log n)."],
    time="O(n)", space="O(1)",
    solution='''def isAnagram(s, t):
    if len(s) != len(t):
        return False
    count = {}
    for c in s:
        count[c] = count.get(c, 0) + 1
    for c in t:
        if count.get(c, 0) == 0:
            return False
        count[c] -= 1
    return True
''',
    tests=[["anagram", "nagaram"], ["rat", "car"], ["a", "a"], ["ab", "a"], ["aabbcc", "abcabc"],
           ["abcd", "abce"], ["listen", "silent"]],
)
_r = rnd(2)
_s = "".join(_r.choice("abcdefghijklmnopqrstuvwxyz") for _ in range(10000)); _t = list(_s); _r.shuffle(_t)
P[-1]["tests"].append([_s, "".join(_t)])
_t2 = list(_t); _t2[5] = "z" if _t2[5] != "z" else "y"
P[-1]["tests"].append([_s, "".join(_t2)])

add(
    id="two-sum", title="Two Sum", diff="Easy", topic="Arrays & Hashing",
    fn="twoSum", params=[("nums", "int[]"), ("target", "int")], ret="int[]", cmp="flat",
    desc="<p>Given an array of integers <code>nums</code> and an integer <code>target</code>, return the indices of the two numbers that add up to <code>target</code>.</p><p>Exactly one valid pair exists, and you may not use the same element twice. The indices can be returned in any order.</p>",
    constraints=["2 &le; nums.length &le; 10,000", "-10<sup>9</sup> &le; nums[i], target &le; 10<sup>9</sup>", "Exactly one solution exists"],
    hints=["Checking all pairs is O(n&sup2;). What if, for each number, you looked up the number you still need?",
           "For x, the partner is <code>target - x</code>.",
           "Store each value's index in a hash map as you scan, and check the map before inserting."],
    editorial=["Scan left to right with a map from value to index. For the current value x, if <code>target - x</code> is already in the map, you found the pair. Otherwise store x and continue.",
               "Checking before inserting guarantees you never pair an element with itself, and the whole thing is a single pass."],
    time="O(n)", space="O(n)",
    solution='''def twoSum(nums, target):
    seen = {}
    for i, x in enumerate(nums):
        if target - x in seen:
            return [seen[target - x], i]
        seen[x] = i
    return []
''',
    tests=[[[2, 7, 11, 15], 9], [[3, 2, 4], 6], [[3, 3], 6], [[-1, -2, -3, -4, -5], -8], [[0, 4, 3, 0], 0],
           [[1000000000, -1000000000, 5, 7], 12]],
)
_r = rnd(3)
_nums = _r.sample(range(1, 50001), 7998) + [60000, 70000]  # only 60000 + 70000 can reach 130000
_r.shuffle(_nums)
_tg = 130000
P[-1]["tests"].append([_nums, _tg])

add(
    id="valid-parentheses", title="Valid Parentheses", diff="Easy", topic="Stack",
    fn="isValid", params=[("s", "string")], ret="bool", cmp="exact",
    desc="<p>Given a string <code>s</code> made only of the characters <code>( ) [ ] { }</code>, return <code>true</code> if it is valid.</p><p>A string is valid when every opening bracket is closed by the same type of bracket, and brackets close in the correct order.</p>",
    constraints=["1 &le; s.length &le; 10,000", "s contains only ()[]{}"],
    hints=["The most recently opened bracket must be the first one closed.",
           "That last-in, first-out behaviour is exactly what a stack gives you.",
           "At the end the stack must be empty, otherwise some bracket was never closed."],
    editorial=["Push every opening bracket on a stack. When you see a closing bracket, the top of the stack must be its matching opener; pop it, or return false if it does not match or the stack is empty.",
               "After the scan the stack must be empty. Leftover openers mean unclosed brackets."],
    time="O(n)", space="O(n)",
    solution='''def isValid(s):
    pair = {')': '(', ']': '[', '}': '{'}
    stack = []
    for c in s:
        if c in pair:
            if not stack or stack.pop() != pair[c]:
                return False
        else:
            stack.append(c)
    return not stack
''',
    tests=[["()"], ["()[]{}"], ["(]"], ["([)]"], ["{[]}"], ["((("], ["]"], ["((()))[]{{}}"],
           ["(" * 5000 + ")" * 5000], ["(" * 5000 + ")" * 4999 + "]"]],
)

add(
    id="best-time-to-buy-and-sell-stock", title="Best Time to Buy and Sell Stock", diff="Easy", topic="Sliding Window",
    fn="maxProfit", params=[("prices", "int[]")], ret="int", cmp="exact",
    desc="<p><code>prices[i]</code> is the price of a stock on day <code>i</code>. You may buy on one day and sell on a later day, once.</p><p>Return the maximum profit you can make. If no profit is possible, return <code>0</code>.</p>",
    constraints=["1 &le; prices.length &le; 10,000", "0 &le; prices[i] &le; 10,000"],
    hints=["Trying every buy/sell pair is O(n&sup2;).",
           "For a fixed selling day, the best buying day is the cheapest day before it.",
           "Keep the lowest price seen so far while scanning."],
    editorial=["Scan once, tracking the minimum price so far. At each day, the best profit selling today is <code>price - minSoFar</code>. Keep the maximum of those.",
               "This is a tiny sliding-window idea: the left edge is the cheapest day, the right edge is today."],
    time="O(n)", space="O(1)",
    solution='''def maxProfit(prices):
    best = 0
    low = prices[0]
    for p in prices:
        low = min(low, p)
        best = max(best, p - low)
    return best
''',
    tests=[[[7, 1, 5, 3, 6, 4]], [[7, 6, 4, 3, 1]], [[1]], [[2, 4, 1]], [[3, 3, 5, 0, 0, 3, 1, 4]], [[1, 2]], [[2, 1]]],
)
_r = rnd(5)
P[-1]["tests"].append([[_r.randint(0, 10000) for _ in range(10000)]])
P[-1]["tests"].append([list(range(5000, 0, -1))])

add(
    id="binary-search", title="Binary Search", diff="Easy", topic="Binary Search",
    fn="search", params=[("nums", "int[]"), ("target", "int")], ret="int", cmp="exact",
    desc="<p>Given an array <code>nums</code> sorted in ascending order with distinct values, and an integer <code>target</code>, return the index of <code>target</code>, or <code>-1</code> if it is not present.</p><p>Your solution must run in O(log n) time.</p>",
    constraints=["1 &le; nums.length &le; 10,000", "All values are distinct and sorted ascending", "-10<sup>9</sup> &le; nums[i], target &le; 10<sup>9</sup>"],
    hints=["A linear scan is O(n). The array being sorted lets you do much better.",
           "Look at the middle element. Is the target in the left half or the right half?",
           "Keep two boundaries <code>lo</code> and <code>hi</code> and shrink them until they cross."],
    editorial=["Compare the middle element with the target. If equal, return it. If the middle is smaller, the target can only be on the right, so move <code>lo</code> past mid; otherwise move <code>hi</code> before mid.",
               "Each step halves the search range, so at most about log2(n) steps are needed. Use <code>lo + (hi - lo) / 2</code> in C++/Java to avoid overflow."],
    time="O(log n)", space="O(1)",
    solution='''def search(nums, target):
    lo, hi = 0, len(nums) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if nums[mid] == target:
            return mid
        if nums[mid] < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return -1
''',
    tests=[[[-1, 0, 3, 5, 9, 12], 9], [[-1, 0, 3, 5, 9, 12], 2], [[5], 5], [[5], -5], [[1, 3], 3], [[1, 3], 1]],
)
_r = rnd(6)
_arr = sorted(_r.sample(range(-10 ** 6, 10 ** 6), 5000))
P[-1]["tests"].append([_arr, _arr[3137]])

add(
    id="climbing-stairs", title="Climbing Stairs", diff="Easy", topic="Dynamic Programming",
    fn="climbStairs", params=[("n", "int")], ret="int", cmp="exact",
    desc="<p>You are climbing a staircase with <code>n</code> steps. Each move you can climb either 1 or 2 steps.</p><p>Return the number of distinct ways to reach the top.</p>",
    constraints=["1 &le; n &le; 45"],
    hints=["Think about the very last move. From which steps could you have arrived at step n?",
           "ways(n) = ways(n-1) + ways(n-2).",
           "Plain recursion repeats work exponentially. Remember results, or just keep the last two."],
    editorial=["To land on step n, your last move was from step n-1 (a 1-step) or from n-2 (a 2-step). So <code>ways(n) = ways(n-1) + ways(n-2)</code>, which is the Fibonacci sequence.",
               "Compute it bottom-up, keeping only the previous two values. A naive recursive version without memoization takes exponential time and will time out for n = 45."],
    time="O(n)", space="O(1)",
    solution='''def climbStairs(n):
    a, b = 1, 1
    for _ in range(n - 1):
        a, b = b, a + b
    return b
''',
    tests=[[2], [3], [1], [10], [30], [45], [20]],
)

# -------------------------------------------------------------- MEDIUM

add(
    id="product-of-array-except-self", title="Product of Array Except Self", diff="Medium", topic="Arrays & Hashing",
    fn="productExceptSelf", params=[("nums", "int[]")], ret="int[]", cmp="exact",
    desc="<p>Given an integer array <code>nums</code>, return an array <code>answer</code> where <code>answer[i]</code> is the product of all elements of <code>nums</code> except <code>nums[i]</code>.</p><p>Do not use division, and solve it in O(n) time.</p>",
    constraints=["2 &le; nums.length &le; 10,000", "-30 &le; nums[i] &le; 30", "Every prefix and suffix product fits in a 32-bit integer"],
    hints=["Without division, think about what is on the left of i and what is on the right.",
           "answer[i] = (product of everything left of i) &times; (product of everything right of i).",
           "Fill the answer with left products in one pass, then multiply in the right products in a second pass, going backwards."],
    editorial=["First pass: <code>answer[i]</code> holds the product of all elements before i (running prefix). Second pass from the right: multiply <code>answer[i]</code> by the running product of all elements after i.",
               "Division fails when the array contains zeros, which is why this prefix/suffix trick is the standard answer. Extra space beyond the output array is O(1)."],
    time="O(n)", space="O(1) extra",
    solution='''def productExceptSelf(nums):
    n = len(nums)
    out = [1] * n
    prefix = 1
    for i in range(n):
        out[i] = prefix
        prefix *= nums[i]
    suffix = 1
    for i in range(n - 1, -1, -1):
        out[i] *= suffix
        suffix *= nums[i]
    return out
''',
    tests=[[[1, 2, 3, 4]], [[-1, 1, 0, -3, 3]], [[2, 3]], [[0, 0, 2]], [[5, 0, 1]], [[-2, -3, 4]]],
)
_r = rnd(7)
P[-1]["tests"].append([[_r.choice([-1, 1]) for _ in range(6000)]])
P[-1]["tests"].append([[_r.choice([-1, 0, 1]) for _ in range(6000)]])

add(
    id="longest-consecutive-sequence", title="Longest Consecutive Sequence", diff="Medium", topic="Arrays & Hashing",
    fn="longestConsecutive", params=[("nums", "int[]")], ret="int", cmp="exact",
    desc="<p>Given an unsorted array of integers <code>nums</code>, return the length of the longest run of consecutive integers (like 4, 5, 6, 7) that can be formed from its values. The run does not have to appear in order inside the array.</p><p>Aim for O(n) time.</p>",
    constraints=["0 &le; nums.length &le; 10,000", "-10<sup>9</sup> &le; nums[i] &le; 10<sup>9</sup>"],
    hints=["Sorting works in O(n log n). Can you avoid it?",
           "Put everything in a set. A number starts a run only if <code>x - 1</code> is not in the set.",
           "From each run start, count upward while <code>y + 1</code> is in the set. Each number is visited once overall."],
    editorial=["Store all numbers in a hash set. For every number x whose predecessor <code>x - 1</code> is missing, x is the start of a run. Walk <code>x, x+1, x+2, ...</code> as long as they are in the set and track the longest length.",
               "Although there is a nested loop, each element is only walked over as part of one run, so the total work is O(n)."],
    time="O(n)", space="O(n)",
    solution='''def longestConsecutive(nums):
    s = set(nums)
    best = 0
    for x in s:
        if x - 1 not in s:
            y = x
            while y + 1 in s:
                y += 1
            best = max(best, y - x + 1)
    return best
''',
    tests=[[[100, 4, 200, 1, 3, 2]], [[0, 3, 7, 2, 5, 8, 4, 6, 0, 1]], [[]], [[1, 2, 0, 1]], [[9, 1, 4, 7, 3, -1, 0, 5, 8, -1, 6]],
           [[5]]],
)
_r = rnd(8)
_a = list(range(-5000, 5000)); _r.shuffle(_a)
P[-1]["tests"].append([_a])
_a2 = [x * 2 for x in range(5000)] + [x * 2 + 1 for x in range(0, 5000, 3)]; _r.shuffle(_a2)
P[-1]["tests"].append([_a2])

add(
    id="maximum-subarray", title="Maximum Subarray", diff="Medium", topic="Dynamic Programming",
    fn="maxSubArray", params=[("nums", "int[]")], ret="int", cmp="exact",
    desc="<p>Given an integer array <code>nums</code>, find the contiguous subarray (containing at least one number) with the largest sum, and return that sum.</p>",
    constraints=["1 &le; nums.length &le; 10,000", "-10,000 &le; nums[i] &le; 10,000"],
    hints=["Checking every subarray is O(n&sup2;) at best.",
           "At each position, decide: extend the previous subarray, or start fresh here.",
           "Starting fresh is better exactly when the running sum so far is negative."],
    editorial=["Let <code>cur</code> be the best sum of a subarray ending at the current index. Then <code>cur = max(x, cur + x)</code>: either extend or restart. The answer is the maximum <code>cur</code> seen anywhere.",
               "This is Kadane's algorithm, a one-line dynamic program. Initialise with the first element, not 0, so all-negative arrays work."],
    time="O(n)", space="O(1)",
    solution='''def maxSubArray(nums):
    best = cur = nums[0]
    for x in nums[1:]:
        cur = max(x, cur + x)
        best = max(best, cur)
    return best
''',
    tests=[[[-2, 1, -3, 4, -1, 2, 1, -5, 4]], [[1]], [[5, 4, -1, 7, 8]], [[-3, -2, -1]], [[-2, -1]], [[0, 0, 0]], [[8, -19, 5, -4, 20]]],
)
_r = rnd(9)
P[-1]["tests"].append([[_r.randint(-100, 100) for _ in range(10000)]])
P[-1]["tests"].append([[_r.randint(-10000, 9000) for _ in range(4000)]])

add(
    id="3sum", title="3Sum", diff="Medium", topic="Two Pointers",
    fn="threeSum", params=[("nums", "int[]")], ret="int[][]", cmp="rows",
    desc="<p>Given an integer array <code>nums</code>, return all unique triplets <code>[a, b, c]</code> from different positions such that <code>a + b + c = 0</code>.</p><p>The answer must not contain duplicate triplets. The order of triplets and the order inside a triplet do not matter.</p>",
    constraints=["3 &le; nums.length &le; 1,500", "-10<sup>5</sup> &le; nums[i] &le; 10<sup>5</sup>"],
    hints=["Three nested loops are O(n&sup3;). Fix one number and the problem becomes Two Sum.",
           "Sort the array first. Then for a fixed first number, move two pointers inward from both ends.",
           "To avoid duplicates, skip repeated values for the first number and after each found triplet."],
    editorial=["Sort the array. For each index i (skipping equal neighbours), use <code>lo = i + 1</code> and <code>hi = n - 1</code>. If the sum is too small, move lo right; too large, move hi left; if zero, record it and move lo past duplicates.",
               "Sorting costs O(n log n) and the double loop is O(n&sup2;), so the total is O(n&sup2;)."],
    time="O(n&sup2;)", space="O(1) extra",
    solution='''def threeSum(nums):
    nums = sorted(nums)
    res = []
    n = len(nums)
    for i in range(n - 2):
        if i > 0 and nums[i] == nums[i - 1]:
            continue
        lo, hi = i + 1, n - 1
        while lo < hi:
            total = nums[i] + nums[lo] + nums[hi]
            if total < 0:
                lo += 1
            elif total > 0:
                hi -= 1
            else:
                res.append([nums[i], nums[lo], nums[hi]])
                lo += 1
                while lo < hi and nums[lo] == nums[lo - 1]:
                    lo += 1
    return res
''',
    tests=[[[-1, 0, 1, 2, -1, -4]], [[0, 1, 1]], [[0, 0, 0]], [[0, 0, 0, 0]], [[-2, 0, 1, 1, 2]], [[3, -2, 1, 0, -1, 2, -3]],
           [[1, 2, 3]]],
)
_r = rnd(10)
P[-1]["tests"].append([[_r.randint(-60, 60) for _ in range(1500)]])
P[-1]["tests"].append([[_r.randint(-100000, 100000) for _ in range(1500)]])

add(
    id="container-with-most-water", title="Container With Most Water", diff="Medium", topic="Two Pointers",
    fn="maxArea", params=[("height", "int[]")], ret="int", cmp="exact",
    desc="<p>You are given an array <code>height</code> where <code>height[i]</code> is the height of a vertical line at position <code>i</code>. Pick two lines that, together with the x-axis, form a container holding the most water.</p><p>Return the maximum amount of water a container can store. The container cannot be tilted.</p>",
    constraints=["2 &le; height.length &le; 10,000", "0 &le; height[i] &le; 10,000"],
    hints=["The water between lines i &lt; j is <code>min(height[i], height[j]) * (j - i)</code>.",
           "Start with the widest container (first and last line). How can you possibly improve it?",
           "Moving the taller line inward can never help, because the shorter line still limits the height. Move the shorter one."],
    editorial=["Use two pointers at both ends. Compute the area, then move the pointer at the shorter line inward. Moving the taller line only reduces the width without any chance to raise the limiting height, so the best answer is never lost.",
               "Each step shrinks the range by one, so the loop is O(n)."],
    time="O(n)", space="O(1)",
    solution='''def maxArea(height):
    lo, hi = 0, len(height) - 1
    best = 0
    while lo < hi:
        best = max(best, min(height[lo], height[hi]) * (hi - lo))
        if height[lo] < height[hi]:
            lo += 1
        else:
            hi -= 1
    return best
''',
    tests=[[[1, 8, 6, 2, 5, 4, 8, 3, 7]], [[1, 1]], [[4, 3, 2, 1, 4]], [[1, 2, 1]], [[0, 0]], [[2, 3, 4, 5, 18, 17, 6]]],
)
_r = rnd(11)
P[-1]["tests"].append([[_r.randint(0, 10000) for _ in range(10000)]])
P[-1]["tests"].append([[_r.randint(0, 100) for _ in range(10000)]])

add(
    id="longest-substring-without-repeating-characters", title="Longest Substring Without Repeating Characters", diff="Medium", topic="Sliding Window",
    fn="lengthOfLongestSubstring", params=[("s", "string")], ret="int", cmp="exact",
    desc="<p>Given a string <code>s</code>, return the length of the longest substring that contains no repeated character.</p><p>A substring is a contiguous part of the string.</p>",
    constraints=["0 &le; s.length &le; 20,000", "s contains lowercase English letters"],
    hints=["Checking every substring is O(n&sup2;) or worse.",
           "Keep a window <code>[start, i]</code> that always has unique characters.",
           "When s[i] already occurred inside the window, move <code>start</code> just past its previous position."],
    editorial=["Store the last index where each character was seen. Move the right edge one character at a time. If the character was last seen inside the current window, jump the left edge to just after that index.",
               "The window never moves backwards, so each character is processed once: O(n). An empty string returns 0."],
    time="O(n)", space="O(1)",
    solution='''def lengthOfLongestSubstring(s):
    last = {}
    start = best = 0
    for i, c in enumerate(s):
        if c in last and last[c] >= start:
            start = last[c] + 1
        last[c] = i
        best = max(best, i - start + 1)
    return best
''',
    tests=[["abcabcbb"], ["bbbbb"], ["pwwkew"], [""], ["a"], ["abba"], ["dvdf"], ["tmmzuxt"]],
)
_r = rnd(12)
P[-1]["tests"].append(["".join(_r.choice("abcdefghijklmnopqrstuvwxyz") for _ in range(20000))])
P[-1]["tests"].append(["abcdefghijklmnopqrstuvwxyz" * 700 + "a"])

add(
    id="daily-temperatures", title="Daily Temperatures", diff="Medium", topic="Stack",
    fn="dailyTemperatures", params=[("temperatures", "int[]")], ret="int[]", cmp="exact",
    desc="<p>Given an array <code>temperatures</code> of daily temperatures, return an array <code>answer</code> where <code>answer[i]</code> is the number of days you must wait after day <code>i</code> to get a warmer temperature. If there is no future warmer day, <code>answer[i]</code> is <code>0</code>.</p>",
    constraints=["1 &le; temperatures.length &le; 10,000", "30 &le; temperatures[i] &le; 100"],
    hints=["For each day, scanning forward is O(n&sup2;) in the worst case.",
           "Days still waiting for a warmer day form a pile; the newest waiting day is on top.",
           "Keep a stack of indices with decreasing temperatures. A warmer day resolves everything colder on top of the stack."],
    editorial=["Maintain a stack of indices whose temperatures are in decreasing order (they are still waiting). For the current day i, while the top of the stack has a lower temperature, pop it as j and set <code>answer[j] = i - j</code>. Then push i.",
               "This is the classic monotonic stack: every index is pushed and popped at most once."],
    time="O(n)", space="O(n)",
    solution='''def dailyTemperatures(temperatures):
    ans = [0] * len(temperatures)
    stack = []
    for i, t in enumerate(temperatures):
        while stack and temperatures[stack[-1]] < t:
            j = stack.pop()
            ans[j] = i - j
        stack.append(i)
    return ans
''',
    tests=[[[73, 74, 75, 71, 69, 72, 76, 73]], [[30, 40, 50, 60]], [[30, 60, 90]], [[90, 80, 70]], [[55]], [[70, 70, 70]]],
)
_r = rnd(13)
P[-1]["tests"].append([[100 - (i * 70) // 10000 for i in range(10000)]])
P[-1]["tests"].append([[_r.randint(30, 100) for _ in range(5000)]])

add(
    id="search-in-rotated-sorted-array", title="Search in Rotated Sorted Array", diff="Medium", topic="Binary Search",
    fn="search", params=[("nums", "int[]"), ("target", "int")], ret="int", cmp="exact",
    desc="<p>A sorted array of distinct integers was rotated at an unknown pivot, for example <code>[0,1,2,4,5,6,7]</code> became <code>[4,5,6,7,0,1,2]</code>.</p><p>Given the rotated array <code>nums</code> and an integer <code>target</code>, return the index of <code>target</code>, or <code>-1</code> if it is not there. Your algorithm must run in O(log n).</p>",
    constraints=["1 &le; nums.length &le; 10,000", "All values are distinct", "-10<sup>9</sup> &le; nums[i], target &le; 10<sup>9</sup>"],
    hints=["Even though the whole array is not sorted, one half around the middle always is.",
           "Compare <code>nums[lo]</code> with <code>nums[mid]</code> to find which half is sorted.",
           "Then check whether the target lies inside the sorted half's range; if yes go there, otherwise go to the other half."],
    editorial=["At every step, at least one of <code>[lo, mid]</code> or <code>[mid, hi]</code> is sorted. If <code>nums[lo] &le; nums[mid]</code> the left half is sorted: if the target is within <code>[nums[lo], nums[mid])</code> search left, else right. Otherwise the right half is sorted, and the same check applies.",
               "Each iteration halves the range, so the total is O(log n)."],
    time="O(log n)", space="O(1)",
    solution='''def search(nums, target):
    lo, hi = 0, len(nums) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if nums[mid] == target:
            return mid
        if nums[lo] <= nums[mid]:
            if nums[lo] <= target < nums[mid]:
                hi = mid - 1
            else:
                lo = mid + 1
        else:
            if nums[mid] < target <= nums[hi]:
                lo = mid + 1
            else:
                hi = mid - 1
    return -1
''',
    tests=[[[4, 5, 6, 7, 0, 1, 2], 0], [[4, 5, 6, 7, 0, 1, 2], 3], [[1], 0], [[1], 1], [[3, 1], 1], [[5, 1, 3], 5], [[1, 3], 3]],
)
_r = rnd(14)
_arr = sorted(_r.sample(range(-10 ** 6, 10 ** 6), 5000)); _k = 2222
_rot = _arr[_k:] + _arr[:_k]
P[-1]["tests"].append([_rot, _arr[4000]])

add(
    id="koko-eating-bananas", title="Koko Eating Bananas", diff="Medium", topic="Binary Search",
    fn="minEatingSpeed", params=[("piles", "int[]"), ("h", "int")], ret="int", cmp="exact",
    desc="<p>Koko has <code>piles[i]</code> bananas in the i-th pile and <code>h</code> hours before the guards return. Each hour she picks one pile and eats <code>k</code> bananas from it (if the pile has fewer than <code>k</code>, she eats all of it and wastes the rest of the hour).</p><p>Return the minimum integer eating speed <code>k</code> so that she finishes all bananas within <code>h</code> hours.</p>",
    constraints=["1 &le; piles.length &le; 10,000", "piles.length &le; h &le; 10<sup>9</sup>", "1 &le; piles[i] &le; 10<sup>9</sup>", "The total hours can exceed a 32-bit int, so use long / long long in C++ and Java"],
    hints=["If speed k works, any larger speed also works. That monotonic behaviour is the key.",
           "The answer lies between 1 and the largest pile.",
           "Binary search on k. To test a speed, sum <code>ceil(pile / k)</code> over all piles and compare with h."],
    editorial=["Binary search on the answer instead of on the array. For a candidate speed <code>mid</code>, hours needed is <code>sum(ceil(p / mid))</code>. If it fits within h, try a smaller speed (<code>hi = mid</code>); otherwise a bigger one (<code>lo = mid + 1</code>).",
               "Total time is O(n log max(piles)). Use 64-bit integers for the hour total because it can exceed 2<sup>31</sup>."],
    time="O(n log m)", space="O(1)",
    solution='''def minEatingSpeed(piles, h):
    lo, hi = 1, max(piles)
    while lo < hi:
        mid = (lo + hi) // 2
        hours = sum((p + mid - 1) // mid for p in piles)
        if hours <= h:
            hi = mid
        else:
            lo = mid + 1
    return lo
''',
    tests=[[[3, 6, 7, 11], 8], [[30, 11, 23, 4, 20], 5], [[30, 11, 23, 4, 20], 6], [[1000000000], 2],
           [[312884470], 312884469], [[1, 1, 1, 1], 4], [[1000000000, 1000000000, 1000000000], 1000000000]],
)
_r = rnd(15)
P[-1]["tests"].append([[_r.randint(1, 10 ** 9) for _ in range(5000)], 8000])
P[-1]["tests"].append([[_r.randint(1, 10 ** 6) for _ in range(5000)], 10 ** 9])

add(
    id="merge-intervals", title="Merge Intervals", diff="Medium", topic="Intervals",
    fn="merge", params=[("intervals", "int[][]")], ret="int[][]", cmp="exact",
    desc="<p>Given an array of <code>intervals</code> where <code>intervals[i] = [start, end]</code>, merge all overlapping intervals and return the non-overlapping intervals that cover the same ranges, sorted by start.</p><p>Intervals that only touch, like <code>[1,4]</code> and <code>[4,5]</code>, count as overlapping.</p>",
    constraints=["1 &le; intervals.length &le; 10,000", "0 &le; start &le; end &le; 10<sup>6</sup>"],
    hints=["It is hard to merge intervals that are in random order. What order makes it easy?",
           "Sort by start. Then an interval can only overlap with the last merged one.",
           "If <code>start &le; lastEnd</code>, extend lastEnd to the larger end; otherwise begin a new interval."],
    editorial=["Sort the intervals by start. Keep a result list; for each interval, if its start is at most the end of the last result interval they overlap, so set that end to <code>max(lastEnd, end)</code>. Otherwise append it as a new interval.",
               "Sorting dominates the cost: O(n log n)."],
    time="O(n log n)", space="O(n)",
    solution='''def merge(intervals):
    intervals = sorted(intervals)
    res = []
    for s, e in intervals:
        if res and s <= res[-1][1]:
            res[-1][1] = max(res[-1][1], e)
        else:
            res.append([s, e])
    return res
''',
    tests=[[[[1, 3], [2, 6], [8, 10], [15, 18]]], [[[1, 4], [4, 5]]], [[[1, 4], [0, 4]]], [[[1, 4], [2, 3]]],
           [[[1, 4], [0, 0]]], [[[5, 6]]], [[[2, 3], [4, 5], [6, 7], [8, 9], [1, 10]]]],
)
_r = rnd(16)
_iv = []
for _ in range(4000):
    _s = _r.randint(0, 10 ** 6 - 50); _iv.append([_s, _s + _r.randint(0, 40)])
P[-1]["tests"].append([_iv])
_iv2 = []
for _ in range(3000):
    _s = _r.randint(0, 10 ** 6 - 5000); _iv2.append([_s, _s + _r.randint(0, 4000)])
P[-1]["tests"].append([_iv2])

add(
    id="coin-change", title="Coin Change", diff="Medium", topic="Dynamic Programming",
    fn="coinChange", params=[("coins", "int[]"), ("amount", "int")], ret="int", cmp="exact",
    desc="<p>You have coins of different denominations in <code>coins</code> and an integer <code>amount</code>. Each coin can be used any number of times.</p><p>Return the fewest coins needed to make exactly <code>amount</code>, or <code>-1</code> if it is impossible.</p>",
    constraints=["1 &le; coins.length &le; 12", "1 &le; coins[i] &le; 10,000", "0 &le; amount &le; 10,000"],
    hints=["A greedy 'always take the largest coin' fails, for example coins [1, 3, 4] and amount 6.",
           "Let <code>dp[a]</code> be the fewest coins for amount a. How does dp[a] relate to smaller amounts?",
           "dp[a] = 1 + min(dp[a - c]) over all coins c &le; a. Start with dp[0] = 0."],
    editorial=["Build a table <code>dp[0..amount]</code>. For each amount a and each coin c &le; a, a candidate is <code>dp[a - c] + 1</code>. Initialise unreachable states with a large sentinel (such as amount + 1) and convert it to -1 at the end.",
               "There are amount &times; coins transitions, so O(amount &times; n) time. Plain recursion without memoization is exponential."],
    time="O(amount &middot; n)", space="O(amount)",
    solution='''def coinChange(coins, amount):
    INF = amount + 1
    dp = [0] + [INF] * amount
    for a in range(1, amount + 1):
        for c in coins:
            if c <= a and dp[a - c] + 1 < dp[a]:
                dp[a] = dp[a - c] + 1
    return dp[amount] if dp[amount] != INF else -1
''',
    tests=[[[1, 2, 5], 11], [[2], 3], [[1], 0], [[186, 419, 83, 408], 6249], [[2, 5, 10, 1], 27], [[1, 3, 4], 6], [[5, 7], 3],
           [[1, 5, 10, 25, 50, 100, 200, 500, 1000, 2000], 9999], [[7, 13, 29, 101], 9973], [[2, 4, 6, 8], 9999]],
)

add(
    id="number-of-islands", title="Number of Islands", diff="Medium", topic="Graphs",
    fn="numIslands", params=[("grid", "int[][]")], ret="int", cmp="exact",
    desc="<p>You are given a 2D <code>grid</code> of <code>1</code>s (land) and <code>0</code>s (water). An island is a group of land cells connected horizontally or vertically.</p><p>Return the number of islands.</p>",
    constraints=["1 &le; rows, cols &le; 100", "grid[r][c] is 0 or 1", "Diagonal cells are not connected"],
    hints=["Treat each land cell as a node connected to its 4 neighbours.",
           "When you find an unvisited land cell, you found a new island. Mark the whole island as visited.",
           "Use DFS or BFS (with an explicit stack or queue to avoid deep recursion) to flood the island."],
    editorial=["Scan every cell. Whenever you meet land that has not been visited, increase the island count and flood fill from it (DFS or BFS), marking every connected land cell as visited so it is never counted again.",
               "Each cell is visited a constant number of times, so the time is O(rows &times; cols). An iterative flood fill avoids recursion-depth problems on large islands."],
    time="O(R &middot; C)", space="O(R &middot; C)",
    solution='''def numIslands(grid):
    rows, cols = len(grid), len(grid[0])
    seen = [[False] * cols for _ in range(rows)]
    count = 0
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == 1 and not seen[r][c]:
                count += 1
                seen[r][c] = True
                stack = [(r, c)]
                while stack:
                    y, x = stack.pop()
                    for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        ny, nx = y + dy, x + dx
                        if 0 <= ny < rows and 0 <= nx < cols and grid[ny][nx] == 1 and not seen[ny][nx]:
                            seen[ny][nx] = True
                            stack.append((ny, nx))
    return count
''',
    tests=[[[[1, 1, 1, 1, 0], [1, 1, 0, 1, 0], [1, 1, 0, 0, 0], [0, 0, 0, 0, 0]]],
           [[[1, 1, 0, 0, 0], [1, 1, 0, 0, 0], [0, 0, 1, 0, 0], [0, 0, 0, 1, 1]]],
           [[[1]]], [[[0]]], [[[1, 0, 1], [0, 1, 0], [1, 0, 1]]], [[[1, 1, 1], [1, 1, 1], [1, 1, 1]]]],
)
_r = rnd(18)
P[-1]["tests"].append([[[1 if _r.random() < 0.45 else 0 for _ in range(100)] for _ in range(100)]])
P[-1]["tests"].append([[[1 if (i + j) % 2 == 0 else 0 for j in range(100)] for i in range(100)]])

add(
    id="subsets", title="Subsets", diff="Medium", topic="Backtracking",
    fn="subsets", params=[("nums", "int[]")], ret="int[][]", cmp="rows",
    desc="<p>Given an integer array <code>nums</code> of unique elements, return all possible subsets (the power set), including the empty subset and the full array.</p><p>The solution set must not contain duplicate subsets. You can return the subsets in any order.</p>",
    constraints=["1 &le; nums.length &le; 12", "-10 &le; nums[i] &le; 10", "All numbers are unique"],
    hints=["For every element you have exactly two choices: include it or skip it.",
           "That is a decision tree of depth n with 2<sup>n</sup> leaves.",
           "Recurse over the index. After exploring 'include', undo the choice (backtrack) before exploring 'skip'."],
    editorial=["Use recursion on the index i with a current list. At i == n, record a copy of the current list. Otherwise first skip nums[i]; then include it, recurse, and remove it again (backtracking).",
               "There are 2<sup>n</sup> subsets and copying each costs up to n, so O(n &middot; 2<sup>n</sup>) time. That is unavoidable because the output itself has that size."],
    time="O(n &middot; 2<sup>n</sup>)", space="O(n) extra",
    solution='''def subsets(nums):
    res = []
    def go(i, cur):
        if i == len(nums):
            res.append(cur[:])
            return
        go(i + 1, cur)
        cur.append(nums[i])
        go(i + 1, cur)
        cur.pop()
    go(0, [])
    return res
''',
    tests=[[[1, 2, 3]], [[0]], [[1, 2]], [[3, 1, 4, 2]], [[-1, 5]], [[10, -10, 0, 7, 3, 2, 1, -3, -7, 8]],
           [[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, -1, -2]]],
)

# ---------------------------------------------------------------- HARD

add(
    id="trapping-rain-water", title="Trapping Rain Water", diff="Hard", topic="Two Pointers",
    fn="trap", params=[("height", "int[]")], ret="int", cmp="exact",
    desc="<p>Given <code>n</code> non-negative integers representing an elevation map where each bar has width 1, compute how much water it can trap after raining.</p>",
    constraints=["1 &le; height.length &le; 10,000", "0 &le; height[i] &le; 10,000"],
    hints=["Water above a bar is limited by the shorter of the tallest bar to its left and the tallest bar to its right, minus the bar's own height.",
           "You can precompute 'tallest to the left' and 'tallest to the right' arrays, giving O(n) time and O(n) space.",
           "To reach O(1) space: use two pointers and always process the side with the smaller current bar."],
    editorial=["For each index, trapped water = <code>min(maxLeft, maxRight) - height[i]</code>. Two pointers avoid the extra arrays: if <code>height[lo] &lt; height[hi]</code>, the left side is the limiting one, so update <code>maxLeft</code> and add the water at lo; otherwise do the symmetrical step on the right.",
               "Both pointers walk inward once: O(n) time, O(1) space. A monotonic stack gives another O(n) solution."],
    time="O(n)", space="O(1)",
    solution='''def trap(height):
    lo, hi = 0, len(height) - 1
    left = right = water = 0
    while lo < hi:
        if height[lo] < height[hi]:
            left = max(left, height[lo])
            water += left - height[lo]
            lo += 1
        else:
            right = max(right, height[hi])
            water += right - height[hi]
            hi -= 1
    return water
''',
    tests=[[[0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1]], [[4, 2, 0, 3, 2, 5]], [[1]], [[3, 0, 3]], [[5, 4, 3, 2, 1]], [[2, 0, 2]]],
)
_r = rnd(21)
P[-1]["tests"].append([[_r.randint(0, 10000) for _ in range(10000)]])
P[-1]["tests"].append([[abs(i - 2000) for i in range(4000)]])

add(
    id="largest-rectangle-in-histogram", title="Largest Rectangle in Histogram", diff="Hard", topic="Stack",
    fn="largestRectangleArea", params=[("heights", "int[]")], ret="int", cmp="exact",
    desc="<p>Given an array <code>heights</code> where each element is the height of a histogram bar of width 1, return the area of the largest rectangle that fits inside the histogram.</p>",
    constraints=["1 &le; heights.length &le; 10,000", "0 &le; heights[i] &le; 10,000"],
    hints=["For each bar, the best rectangle using its full height extends left and right until it meets a shorter bar.",
           "Finding the nearest shorter bar on each side for every position naively is O(n&sup2;).",
           "A stack of increasing heights tells you the left boundary; when a shorter bar arrives, pop and compute areas."],
    editorial=["Keep a stack of (start index, height) with increasing heights. When the new bar is shorter than the top, pop the top: it can extend from its start to the current index, so its area is <code>height &times; (i - start)</code>. The popped bar's start becomes the new bar's start, because the new bar can extend left over it.",
               "Appending a sentinel 0 at the end flushes the remaining stack. Every bar is pushed and popped once: O(n)."],
    time="O(n)", space="O(n)",
    solution='''def largestRectangleArea(heights):
    stack = []
    best = 0
    for i, h in enumerate(heights + [0]):
        start = i
        while stack and stack[-1][1] >= h:
            idx, height = stack.pop()
            best = max(best, height * (i - idx))
            start = idx
        stack.append((start, h))
    return best
''',
    tests=[[[2, 1, 5, 6, 2, 3]], [[2, 4]], [[1]], [[1, 1, 1, 1]], [[6, 2, 5, 4, 5, 1, 6]], [[0, 9]], [[5, 4, 3, 2, 1]]],
)
_r = rnd(22)
P[-1]["tests"].append([[_r.randint(0, 10000) for _ in range(10000)]])
P[-1]["tests"].append([[_r.randint(5000, 10000) for _ in range(5000)]])

add(
    id="sliding-window-maximum", title="Sliding Window Maximum", diff="Hard", topic="Sliding Window",
    fn="maxSlidingWindow", params=[("nums", "int[]"), ("k", "int")], ret="int[]", cmp="exact",
    desc="<p>You are given an array <code>nums</code> and a window of size <code>k</code> that moves from the far left to the far right, one position at a time.</p><p>Return an array containing the maximum value of each window position.</p>",
    constraints=["1 &le; k &le; nums.length &le; 10,000", "-10<sup>4</sup> &le; nums[i] &le; 10<sup>4</sup>"],
    hints=["Taking the max of each window directly costs O(n &middot; k).",
           "Elements that are smaller than a newer element to their right can never be a window maximum again.",
           "Keep a deque of indices whose values are decreasing. The front is always the current maximum."],
    editorial=["Maintain a deque of indices with decreasing values. For each new element, pop from the back while the back value is smaller or equal (they can never win again), then push the new index. Pop from the front if its index has left the window. Once i &ge; k - 1, the front is the maximum of the window.",
               "Each index enters and leaves the deque once: O(n)."],
    time="O(n)", space="O(k)",
    solution='''from collections import deque

def maxSlidingWindow(nums, k):
    dq = deque()
    out = []
    for i, x in enumerate(nums):
        while dq and nums[dq[-1]] <= x:
            dq.pop()
        dq.append(i)
        if dq[0] <= i - k:
            dq.popleft()
        if i >= k - 1:
            out.append(nums[dq[0]])
    return out
''',
    tests=[[[1, 3, -1, -3, 5, 3, 6, 7], 3], [[1], 1], [[1, -1], 1], [[9, 11], 2], [[4, 3, 2, 1], 2], [[7, 2, 4], 2]],
)
_r = rnd(23)
P[-1]["tests"].append([[_r.randint(-10000, 10000) for _ in range(10000)], 2500])
P[-1]["tests"].append([[6000 - i for i in range(6000)], 3000])

_r = rnd(24)
_bg = "".join(_r.choice("abcdefghijklm") for _ in range(10000))
_bg = _bg[:2000] + "X" + _bg[2001:6000] + "Y" + _bg[6001:6004] + "Z" + _bg[6005:]
add(
    id="minimum-window-substring", title="Minimum Window Substring", diff="Hard", topic="Sliding Window",
    fn="minWindow", params=[("s", "string"), ("t", "string")], ret="string", cmp="exact",
    desc="<p>Given two strings <code>s</code> and <code>t</code>, return the smallest substring of <code>s</code> that contains every character of <code>t</code> (including duplicates). If no such substring exists, return the empty string.</p><p>The test data guarantees the answer is unique when it exists.</p>",
    constraints=["1 &le; s.length, t.length &le; 10,000", "s and t contain English letters (case-sensitive)"],
    hints=["Expand the right end until the window contains everything required.",
           "Then shrink from the left while it still contains everything, recording the smallest window.",
           "Track how many characters of t are still missing using a count map, so you never rescan the window."],
    editorial=["Count the required characters of t. Move the right pointer; a character that is still needed decreases the <code>missing</code> counter. While <code>missing == 0</code> the window is valid: record it if it is shorter, then move the left pointer and put that character back (if it becomes needed again, <code>missing</code> grows).",
               "Both pointers only move forward, so the algorithm is O(|s| + |t|). Return <code>\"\"</code> if no valid window was ever found."],
    time="O(n + m)", space="O(1)",
    solution='''def minWindow(s, t):
    need = {}
    for c in t:
        need[c] = need.get(c, 0) + 1
    missing = len(t)
    best_start, best_len = 0, len(s) + 1
    left = 0
    for right, c in enumerate(s):
        if need.get(c, 0) > 0:
            missing -= 1
        need[c] = need.get(c, 0) - 1
        while missing == 0:
            if right - left + 1 < best_len:
                best_start, best_len = left, right - left + 1
            need[s[left]] += 1
            if need[s[left]] > 0:
                missing += 1
            left += 1
    return "" if best_len > len(s) else s[best_start:best_start + best_len]
''',
    tests=[["ADOBECODEBANC", "ABC"], ["a", "a"], ["a", "aa"], ["ab", "b"], ["aa", "aa"], ["cabwefgewcwaefgcf", "cae"],
           [_bg, "XYZ"]],
)

add(
    id="edit-distance", title="Edit Distance", diff="Hard", topic="Dynamic Programming",
    fn="minDistance", params=[("word1", "string"), ("word2", "string")], ret="int", cmp="exact",
    desc="<p>Given two strings <code>word1</code> and <code>word2</code>, return the minimum number of operations needed to convert <code>word1</code> into <code>word2</code>.</p><p>You may insert a character, delete a character, or replace a character. Each counts as one operation.</p>",
    constraints=["0 &le; word1.length, word2.length &le; 700", "Lowercase English letters only", "An empty string is written as \"\" in the input"],
    hints=["Compare the last characters of both strings. If equal, they cost nothing.",
           "If they differ you have three choices: insert, delete or replace. Each reduces to a smaller subproblem.",
           "Let dp[i][j] be the distance between the first i characters of word1 and the first j of word2."],
    editorial=["Define <code>dp[i][j]</code> as the edit distance between <code>word1[:i]</code> and <code>word2[:j]</code>. Base cases: <code>dp[i][0] = i</code> and <code>dp[0][j] = j</code>. If the characters match, <code>dp[i][j] = dp[i-1][j-1]</code>; otherwise <code>1 + min(dp[i-1][j-1] (replace), dp[i-1][j] (delete), dp[i][j-1] (insert))</code>.",
               "Only the previous row is needed, so space can be reduced to O(m). Time is O(n &middot; m)."],
    time="O(n &middot; m)", space="O(m)",
    solution='''def minDistance(word1, word2):
    n, m = len(word1), len(word2)
    prev = list(range(m + 1))
    for i in range(1, n + 1):
        cur = [i] + [0] * m
        for j in range(1, m + 1):
            if word1[i - 1] == word2[j - 1]:
                cur[j] = prev[j - 1]
            else:
                cur[j] = 1 + min(prev[j - 1], prev[j], cur[j - 1])
        prev = cur
    return prev[m]
''',
    tests=[["horse", "ros"], ["intention", "execution"], ["", "a"], ["", ""], ["a", "a"], ["abc", "yabd"], ["sunday", "saturday"]],
)
_r = rnd(25)
P[-1]["tests"].append(["".join(_r.choice("abcd") for _ in range(700)), "".join(_r.choice("abcd") for _ in range(700))])
P[-1]["tests"].append(["".join(_r.choice("ab") for _ in range(600)), "".join(_r.choice("abc") for _ in range(650))])

add(
    id="n-queens-ii", title="N-Queens II", diff="Hard", topic="Backtracking",
    fn="totalNQueens", params=[("n", "int")], ret="int", cmp="exact",
    desc="<p>Place <code>n</code> queens on an <code>n &times; n</code> chessboard so that no two queens attack each other (no shared row, column or diagonal).</p><p>Return the number of distinct solutions.</p>",
    constraints=["1 &le; n &le; 9"],
    hints=["Place queens one row at a time; each row gets exactly one queen.",
           "Track which columns and diagonals are already occupied so you can reject a square in O(1).",
           "On a diagonal, <code>row - col</code> is constant; on an anti-diagonal, <code>row + col</code> is constant."],
    editorial=["Recurse row by row. For each column in the current row, skip it if the column, the diagonal <code>r - c</code> or the anti-diagonal <code>r + c</code> is taken. Otherwise mark them, recurse to the next row, then unmark (backtrack). Reaching row n means one complete solution.",
               "The search is pruned heavily compared with trying all n<sup>n</sup> placements, and n = 9 finishes instantly."],
    time="O(n!)", space="O(n)",
    solution='''def totalNQueens(n):
    cols, d1, d2 = set(), set(), set()

    def place(r):
        if r == n:
            return 1
        total = 0
        for c in range(n):
            if c in cols or (r - c) in d1 or (r + c) in d2:
                continue
            cols.add(c)
            d1.add(r - c)
            d2.add(r + c)
            total += place(r + 1)
            cols.remove(c)
            d1.remove(r - c)
            d2.remove(r + c)
        return total

    return place(0)
''',
    tests=[[4], [1], [5], [6], [8], [9], [7]],
)

# ------------------------------------------------------------------------
# Brute-force cross checks (run by build.py). Each entry: id -> (brute, generator)

def _canon_rows(rows):
    return sorted(sorted(r) for r in rows)


def _gen_arr(r, lo=-6, hi=6, nmin=0, nmax=9):
    return [r.randint(lo, hi) for _ in range(r.randint(nmin, nmax))]


def b_three(nums):
    s = set()
    n = len(nums)
    for i in range(n):
        for j in range(i + 1, n):
            for k in range(j + 1, n):
                if nums[i] + nums[j] + nums[k] == 0:
                    s.add(tuple(sorted((nums[i], nums[j], nums[k]))))
    return [list(t) for t in s]


def b_maxsub(nums):
    return max(sum(nums[i:j]) for i in range(len(nums)) for j in range(i + 1, len(nums) + 1))


def b_prod(nums):
    out = []
    for i in range(len(nums)):
        p = 1
        for j, x in enumerate(nums):
            if j != i:
                p *= x
        out.append(p)
    return out


def b_consec(nums):
    best = 0
    for x in set(nums):
        y = x
        while y in set(nums):
            y += 1
        best = max(best, y - x)
    return best


def b_area(h):
    return max(min(h[i], h[j]) * (j - i) for i in range(len(h)) for j in range(i + 1, len(h)))


def b_sub(s):
    best = 0
    for i in range(len(s)):
        for j in range(i, len(s)):
            if len(set(s[i:j + 1])) == j - i + 1:
                best = max(best, j - i + 1)
    return best


def b_temp(t):
    return [next((j - i for j in range(i + 1, len(t)) if t[j] > t[i]), 0) for i in range(len(t))]


def b_rot(nums, target):
    return nums.index(target) if target in nums else -1


def b_koko(piles, h):
    k = 1
    while sum((p + k - 1) // k for p in piles) > h:
        k += 1
    return k


def b_coin(coins, amount):
    best = [None] * (amount + 1)
    best[0] = 0
    for a in range(1, amount + 1):
        for c in coins:
            if c <= a and best[a - c] is not None and (best[a] is None or best[a - c] + 1 < best[a]):
                best[a] = best[a - c] + 1
    return -1 if best[amount] is None else best[amount]


def b_isl(grid):
    rows, cols = len(grid), len(grid[0])
    parent = list(range(rows * cols))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for r in range(rows):
        for c in range(cols):
            if grid[r][c]:
                for dr, dc in ((1, 0), (0, 1)):
                    nr, nc = r + dr, c + dc
                    if nr < rows and nc < cols and grid[nr][nc]:
                        parent[find(r * cols + c)] = find(nr * cols + nc)
    return len({find(r * cols + c) for r in range(rows) for c in range(cols) if grid[r][c]})


def b_subsets(nums):
    n = len(nums)
    return [[nums[i] for i in range(n) if m >> i & 1] for m in range(1 << n)]


def b_trap(h):
    return sum(max(0, min(max(h[:i + 1]), max(h[i:])) - h[i]) for i in range(len(h)))


def b_hist(h):
    return max(min(h[i:j + 1]) * (j - i + 1) for i in range(len(h)) for j in range(i, len(h)))


def b_win(nums, k):
    return [max(nums[i:i + k]) for i in range(len(nums) - k + 1)]


def b_minwin(s, t):
    from collections import Counter
    need = Counter(t)
    best = ""
    for i in range(len(s)):
        for j in range(i + 1, len(s) + 1):
            c = Counter(s[i:j])
            if all(c[k] >= v for k, v in need.items()):
                if best == "" or j - i < len(best):
                    best = s[i:j]
                break
    return best


def b_edit(a, b):
    from functools import lru_cache

    @lru_cache(None)
    def f(i, j):
        if i == 0:
            return j
        if j == 0:
            return i
        if a[i - 1] == b[j - 1]:
            return f(i - 1, j - 1)
        return 1 + min(f(i - 1, j), f(i, j - 1), f(i - 1, j - 1))

    return f(len(a), len(b))


def _sorted_rot(r):
    n = r.randint(1, 9)
    a = sorted(r.sample(range(-20, 20), n))
    k = r.randint(0, n - 1)
    return a[k:] + a[:k]


def _uniq_minwin_case(r):
    while True:
        s = "".join(r.choice("abc") for _ in range(r.randint(1, 10)))
        t = "".join(r.choice("abc") for _ in range(r.randint(1, 3)))
        from collections import Counter
        need = Counter(t)
        wins = []
        for i in range(len(s)):
            for j in range(i + 1, len(s) + 1):
                c = Counter(s[i:j])
                if all(c[k] >= v for k, v in need.items()):
                    wins.append((j - i, i))
        if not wins:
            return s, t
        m = min(w[0] for w in wins)
        if sum(1 for w in wins if w[0] == m) == 1:
            return s, t


CHECKS = {
    "3sum": (b_three, lambda r: [_gen_arr(r, -5, 5, 0, 9)], "rows"),
    "maximum-subarray": (b_maxsub, lambda r: [_gen_arr(r, -9, 9, 1, 9)], "exact"),
    "product-of-array-except-self": (b_prod, lambda r: [_gen_arr(r, -4, 4, 2, 7)], "exact"),
    "longest-consecutive-sequence": (b_consec, lambda r: [_gen_arr(r, -6, 6, 0, 10)], "exact"),
    "container-with-most-water": (b_area, lambda r: [_gen_arr(r, 0, 9, 2, 9)], "exact"),
    "longest-substring-without-repeating-characters": (b_sub, lambda r: ["".join(r.choice("abcd") for _ in range(r.randint(0, 10)))], "exact"),
    "daily-temperatures": (b_temp, lambda r: [_gen_arr(r, 30, 40, 1, 9)], "exact"),
    "search-in-rotated-sorted-array": (b_rot, lambda r: (lambda a: [a, r.randint(-22, 22)])(_sorted_rot(r)), "exact"),
    "koko-eating-bananas": (b_koko, lambda r: (lambda p: [p, r.randint(len(p), len(p) + 12)])([r.randint(1, 15) for _ in range(r.randint(1, 5))]), "exact"),
    "coin-change": (b_coin, lambda r: [[r.randint(1, 8) for _ in range(r.randint(1, 4))], r.randint(0, 30)], "exact"),
    "number-of-islands": (b_isl, lambda r: [[[r.randint(0, 1) for _ in range(5)] for _ in range(4)]], "exact"),
    "subsets": (b_subsets, lambda r: [r.sample(range(-5, 6), r.randint(1, 6))], "rows"),
    "trapping-rain-water": (b_trap, lambda r: [_gen_arr(r, 0, 9, 1, 10)], "exact"),
    "largest-rectangle-in-histogram": (b_hist, lambda r: [_gen_arr(r, 0, 9, 1, 9)], "exact"),
    "sliding-window-maximum": (b_win, lambda r: (lambda a: [a, r.randint(1, len(a))])(_gen_arr(r, -9, 9, 1, 10)), "exact"),
    "minimum-window-substring": (b_minwin, lambda r: list(_uniq_minwin_case(r)), "exact"),
    "edit-distance": (b_edit, lambda r: ["".join(r.choice("abc") for _ in range(r.randint(0, 7))), "".join(r.choice("abc") for _ in range(r.randint(0, 7)))], "exact"),
}

KNOWN_QUEENS = {1: 1, 2: 0, 3: 0, 4: 2, 5: 10, 6: 4, 7: 40, 8: 92, 9: 352}
