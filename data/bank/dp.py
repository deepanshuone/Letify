"""Problems: dp. See data/lib.py for the registry."""
from lib import add, rnd, CHECKS, VALIDATE, gen_arr  # noqa: F401

LETTERS = "abcdefghijklmnopqrstuvwxyz"


# ---------------------------------------------------------------- EASY

add(
    id="min-cost-climbing-stairs", title="Min Cost Climbing Stairs", diff="Easy", topic="Dynamic Programming",
    fn="minCostClimbingStairs", params=[("cost", "int[]")], ret="int", cmp="exact",
    desc="<p>A staircase has steps numbered <code>0</code> to <code>n - 1</code>, and <code>cost[i]</code> is the toll you pay every time you step on step <code>i</code>. You may start on step <code>0</code> or on step <code>1</code> (paying that step's toll), and from any step you can climb either 1 or 2 steps.</p><p>The top of the staircase is the position just past the last step, <code>n</code>. Return the minimum total toll you must pay to reach the top.</p>",
    constraints=["2 &le; cost.length &le; 3,000", "0 &le; cost[i] &le; 999"],
    hints=["Consider the last step you stand on before reaching the top. Which steps could that be?",
           "Let best(i) be the cheapest total toll for a trip that ends by standing on step i (including cost[i]). Then best(i) = cost[i] + min(best(i-1), best(i-2)).",
           "The answer is the cheaper of best(n-1) and best(n-2). You only need the previous two values, so two variables are enough."],
    editorial=["Define <code>best(i)</code> as the minimum toll to stand on step i, tolls included. You can start on step 0 or 1, so <code>best(0) = cost[0]</code> and <code>best(1) = cost[1]</code>. For later steps you arrived from i-1 or i-2, so <code>best(i) = cost[i] + min(best(i-1), best(i-2))</code>. The top can be reached from step n-1 or n-2, so the answer is <code>min(best(n-1), best(n-2))</code>.",
               "Computing it bottom-up while keeping only the last two values uses O(1) extra space. A recursion without memoisation re-solves the same steps over and over and takes exponential time."],
    time="O(n)", space="O(1)",
    solution='''def minCostClimbingStairs(cost):
    prev2, prev1 = cost[0], cost[1]   # best cost of standing on step i-2 and i-1
    for i in range(2, len(cost)):
        prev2, prev1 = prev1, cost[i] + min(prev1, prev2)
    return min(prev1, prev2)
''',
    tests=[[[10, 15, 20]], [[1, 100, 1, 1, 1, 100, 1, 1, 100, 1]], [[5, 3]], [[0, 0]], [[7, 7, 7, 7]], [[0, 0, 0, 0, 999]],
           [[999, 0, 999, 0, 999, 0]], [[1, 2, 3]], [[3, 2, 1]], [[999, 999]]],
)
_r = rnd(5101)
_t = [[_r.randint(0, 999) for _ in range(3000)]]
_t2 = [[999] * 2000]
_t3 = [[999 if i % 2 == 0 else 0 for i in range(2001)]]
_t4 = [[_r.randint(0, 20) for _ in range(3000)]]


def _brute_climb(cost):
    n = len(cost)
    best = None
    for mask in range(1, 1 << n):
        pos = [i for i in range(n) if mask >> i & 1]
        if pos[0] > 1 or pos[-1] < n - 2:
            continue
        if any(b - a > 2 for a, b in zip(pos, pos[1:])):
            continue
        total = sum(cost[i] for i in pos)
        if best is None or total < best:
            best = total
    return best


CHECKS["min-cost-climbing-stairs"] = (_brute_climb, lambda r: [gen_arr(r, 0, 9, 2, 12)], "exact")

# ------------------------------------------------------------------

add(
    id="pascals-triangle", title="Pascal's Triangle", diff="Easy", topic="Dynamic Programming",
    fn="generate", params=[("numRows", "int")], ret="int[][]", cmp="exact",
    desc="<p>Build the first <code>numRows</code> rows of Pascal's triangle and return them as a list of rows. Row <code>i</code> (counting from 0) has <code>i + 1</code> entries. The first and last entry of every row are <code>1</code>, and every other entry is the sum of the two entries directly above it in the previous row.</p>",
    constraints=["1 &le; numRows &le; 30"],
    hints=["Write out the first five rows on paper and look at how each number relates to the row above.",
           "Row 0 is [1]. For row i, entry j is the sum of entries j-1 and j of row i-1 (treat missing neighbours as 0).",
           "Start every row with 1, add the pairwise sums of the previous row, and end with 1."],
    editorial=["Build the triangle row by row. The new row begins with 1, then for each adjacent pair <code>(prev[j-1], prev[j])</code> in the previous row it appends their sum, and it ends with 1. This is a direct dynamic program where each row depends only on the row before it.",
               "Another way is the closed form <code>C(i, j) = C(i, j-1) * (i - j + 1) / j</code>, which creates each row without looking at the previous one. For 30 rows every value fits comfortably in a 32-bit integer (the largest is 77,558,760)."],
    time="O(numRows&sup2;)", space="O(numRows&sup2;)",
    solution='''def generate(numRows):
    rows = [[1]]
    for i in range(1, numRows):
        prev = rows[-1]
        row = [1]
        for j in range(1, i):
            row.append(prev[j - 1] + prev[j])
        row.append(1)
        rows.append(row)
    return rows
''',
    tests=[[5], [1], [3], [2], [4], [10], [30], [20], [15]],
)


def _brute_pascal(n):
    from math import comb
    return [[comb(i, j) for j in range(i + 1)] for i in range(n)]


CHECKS["pascals-triangle"] = (_brute_pascal, lambda r: [r.randint(1, 30)], "exact")

# ------------------------------------------------------------------

add(
    id="plus-one", title="Plus One", diff="Easy", topic="Arrays & Hashing",
    fn="plusOne", params=[("digits", "int[]")], ret="int[]", cmp="exact",
    desc="<p>A non-negative integer is stored as an array <code>digits</code> with the most significant digit first, one digit per element. The number has no leading zeros, except for the number zero itself, which is stored as <code>[0]</code>.</p><p>Add one to the number and return its digits in the same format. You may not convert the whole array to a single integer, because the number can have thousands of digits.</p>",
    constraints=["1 &le; digits.length &le; 5,000", "0 &le; digits[i] &le; 9", "digits[0] is not 0 unless the array is exactly [0]"],
    hints=["Add one the way you would on paper: start from the last digit.",
           "If the last digit is below 9, just increase it and you are done. If it is 9, it becomes 0 and a carry moves left.",
           "If the carry falls off the front (all digits were 9), the result needs one extra leading 1."],
    editorial=["Scan from the right. Each digit that equals 9 turns into 0 and passes the carry on; the first digit that is not 9 is increased by one and the answer is ready. Usually this stops after a single step.",
               "Only when every digit is 9 does the loop run to the end. The answer is then a 1 followed by all zeros, so we build it directly. The array is processed once, which is optimal."],
    time="O(n)", space="O(1) extra",
    solution='''def plusOne(digits):
    res = list(digits)
    for i in range(len(res) - 1, -1, -1):
        if res[i] < 9:
            res[i] += 1
            return res
        res[i] = 0
    return [1] + res
''',
    tests=[[[1, 2, 3]], [[9, 9]], [[1, 9, 9]], [[0]], [[9]], [[8, 9, 9, 9]], [[4, 3, 2, 1]], [[1, 0, 0, 0]], [[2, 9, 9, 8, 9]]],
)
_r = rnd(5103)
_P3 = [[9] * 3000, [1] + [_r.randint(0, 9) for _ in range(4998)] + [9], [_r.randint(1, 9)] + [_r.randint(0, 9) for _ in range(1999)]]


def _brute_plus_one(digits):
    return [int(c) for c in str(int("".join(map(str, digits))) + 1)]


def _gen_plus_one(r):
    n = r.randint(1, 8)
    if n == 1 and r.random() < 0.3:
        return [[0]]
    d = [r.randint(1, 9)] + [r.choice([9, 9, r.randint(0, 9)]) for _ in range(n - 1)]
    if r.random() < 0.2:
        d = [9] * n
    return [d]


CHECKS["plus-one"] = (_brute_plus_one, _gen_plus_one, "exact")


def _validate_plus_one(tests):
    for t in tests:
        d = t["args"][0]
        assert 1 <= len(d) <= 5000 and all(0 <= x <= 9 for x in d)
        assert d[0] != 0 or d == [0]


VALIDATE["plus-one"] = _validate_plus_one

# ------------------------------------------------------------------

add(
    id="integer-square-root", title="Integer Square Root", diff="Easy", topic="Binary Search",
    fn="mySqrt", params=[("x", "int")], ret="int", cmp="exact",
    desc="<p>Given a non-negative integer <code>x</code>, return the square root of <code>x</code> rounded down to the nearest integer, that is the largest integer <code>r</code> with <code>r &times; r &le; x</code>.</p><p>Do not use floating-point numbers, <code>pow</code>, <code>sqrt</code> or any similar built-in.</p>",
    constraints=["0 &le; x &le; 2<sup>31</sup> - 1"],
    hints=["Trying r = 0, 1, 2, ... until r&sup2; exceeds x works, but how many steps is that for large x?",
           "The condition 'r &times; r &le; x' is true for small r and false for large r. That is a sorted yes/no pattern you can binary search.",
           "Search r between 0 and x. Compare <code>mid</code> with <code>x / mid</code> instead of multiplying, so that mid &times; mid cannot overflow a 32-bit integer."],
    editorial=["The predicate <code>r*r &le; x</code> is monotone: true up to the answer, false afterwards. Binary search for the last r where it holds. For x &ge; 1 the answer is at most x, and a safe test that avoids overflow is <code>mid &le; x / mid</code> using integer division.",
               "Newton's iteration <code>r = (r + x / r) / 2</code> converges even faster, in a handful of steps, but needs care with the stopping rule. The linear scan is only fine for tiny x because the answer can be as large as 46,340."],
    time="O(log x)", space="O(1)",
    solution='''def mySqrt(x):
    if x < 2:
        return x
    lo, hi = 1, x          # invariant: lo * lo <= x, answer in [lo, hi]
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if mid <= x // mid:
            lo = mid
        else:
            hi = mid - 1
    return lo
''',
    tests=[[4], [8], [0], [1], [2], [3], [15], [16], [17], [2147483647], [2147483646], [46340 * 46340], [46340 * 46340 - 1],
           [46340 * 46340 + 1], [1000000], [999999], [123456789], [2147395599 - 40000]],
)


def _brute_isqrt(x):
    r = 0
    while (r + 1) * (r + 1) <= x:
        r += 1
    return r


def _gen_isqrt(r):
    if r.random() < 0.5:
        return [r.randint(0, 200)]
    k = r.randint(1, 1000)
    return [max(0, k * k + r.choice([-1, 0, 1]))]


CHECKS["integer-square-root"] = (_brute_isqrt, _gen_isqrt, "exact")

# -------------------------------------------------------------- MEDIUM

add(
    id="house-robber", title="House Robber", diff="Medium", topic="Dynamic Programming",
    fn="rob", params=[("nums", "int[]")], ret="int", cmp="exact",
    desc="<p>A row of houses lines a street, and <code>nums[i]</code> is the amount of money inside house <code>i</code>. If you rob two houses that are next to each other, the alarm goes off, so you must never rob two adjacent houses.</p><p>Return the maximum amount of money you can rob in one night. If there are no houses, the answer is <code>0</code>.</p>",
    constraints=["0 &le; nums.length &le; 10,000", "0 &le; nums[i] &le; 99"],
    hints=["For each house you either rob it or skip it. What does robbing it forbid?",
           "Let best(i) be the most you can get from houses 0..i. Then best(i) = max(best(i-1), best(i-2) + nums[i]).",
           "Each value depends only on the previous two, so two variables replace the whole table."],
    editorial=["Let <code>best(i)</code> be the maximum loot using only the first i+1 houses. Skipping house i leaves <code>best(i-1)</code>; robbing it forces you to skip house i-1, giving <code>best(i-2) + nums[i]</code>. Take the larger. The answer is the value for the last house, or 0 for an empty street.",
               "Because only the last two values are ever needed, the table collapses to two variables and the space drops to O(1). The same idea works as a top-down recursion with memoisation, but the loop is shorter and avoids recursion depth limits."],
    time="O(n)", space="O(1)",
    solution='''def rob(nums):
    skip, take = 0, 0      # best loot ignoring / including the previous house's decision
    for x in nums:
        skip, take = max(skip, take), skip + x
    return max(skip, take)
''',
    tests=[[[1, 2, 3, 1]], [[2, 7, 9, 3, 1]], [[2, 1, 1, 2]], [[]], [[5]], [[0, 0, 0]], [[5, 5]], [[10, 1, 1, 10]], [[3, 10, 3, 1, 2]],
           [[99, 1, 1, 99, 1, 1, 99]]],
)
_r = rnd(5105)
_HR = [[_r.randint(0, 99) for _ in range(10000)], [99] * 3000, [99 if i % 2 else 0 for i in range(3000)]]


def _brute_rob(nums):
    n = len(nums)
    best = 0
    for mask in range(1 << n):
        if mask & (mask >> 1):
            continue
        best = max(best, sum(nums[i] for i in range(n) if mask >> i & 1))
    return best


CHECKS["house-robber"] = (_brute_rob, lambda r: [gen_arr(r, 0, 20, 0, 12)], "exact")

# ------------------------------------------------------------------

add(
    id="jump-game", title="Jump Game", diff="Medium", topic="Greedy",
    fn="canJump", params=[("nums", "int[]")], ret="bool", cmp="exact",
    desc="<p>You stand on index <code>0</code> of an array <code>nums</code>. When you are on index <code>i</code> you may jump forward any number of positions from <code>1</code> up to <code>nums[i]</code> (or not at all if <code>nums[i]</code> is <code>0</code>).</p><p>Return <code>true</code> if you can reach the last index, and <code>false</code> otherwise.</p>",
    constraints=["1 &le; nums.length &le; 10,000", "0 &le; nums[i] &le; 100,000"],
    hints=["Exploring every possible jump sequence is exponential. What do you really need to know at each index?",
           "Positions you can reach always form one contiguous block starting at index 0, so only the furthest reachable index matters.",
           "Scan left to right, keeping <code>far</code>. If you ever stand at an index greater than <code>far</code>, you are stuck; otherwise update <code>far = max(far, i + nums[i])</code>."],
    editorial=["Keep <code>far</code>, the furthest index reachable so far. For each index i, if <code>i &gt; far</code> then index i can never be reached and the answer is false. Otherwise extend <code>far</code> with <code>i + nums[i]</code>. If <code>far</code> ever reaches the last index we can stop with true.",
               "Why contiguous? If you can reach index k, you can reach everything below k by shorter jumps from the same earlier position, so reachable indices never have holes before the furthest one. A dynamic program that marks each reachable index works too, but costs O(n&sup2;) in the worst case."],
    time="O(n)", space="O(1)",
    solution='''def canJump(nums):
    far = 0
    for i, x in enumerate(nums):
        if i > far:
            return False
        far = max(far, i + x)
    return far >= len(nums) - 1
''',
    tests=[[[2, 3, 1, 1, 4]], [[3, 2, 1, 0, 4]], [[0]], [[0, 1]], [[1, 0]], [[2, 0, 0]], [[1, 1, 0, 1]], [[100000, 0, 0, 0]],
           [[4, 0, 0, 0, 0, 0]], [[2, 5, 0, 0, 0]], [[1, 2, 0, 0, 0, 1]]],
)
_r = rnd(5106)
_JG = []
_k = 2000
_JG.append([_k - i for i in range(_k)] + [0] + [_r.randint(0, 9) for _ in range(3000)])        # stuck at the 0 on index 2000
_JG.append([1] * 10000)
_JG.append([_k - i if i != 700 else _k - 700 + 1 for i in range(_k)] + [0] + [_r.randint(0, 9) for _ in range(3000)])


def _brute_jump(nums):
    n = len(nums)
    seen = {0}
    stack = [0]
    while stack:
        i = stack.pop()
        for j in range(i + 1, min(n - 1, i + nums[i]) + 1):
            if j not in seen:
                seen.add(j)
                stack.append(j)
    return (n - 1) in seen


CHECKS["jump-game"] = (_brute_jump, lambda r: [gen_arr(r, 0, 3, 1, 12)], "exact")

# ------------------------------------------------------------------

add(
    id="longest-increasing-subsequence", title="Longest Increasing Subsequence", diff="Medium", topic="Dynamic Programming",
    fn="lengthOfLIS", params=[("nums", "int[]")], ret="int", cmp="exact",
    desc="<p>Given an integer array <code>nums</code>, return the length of its longest strictly increasing subsequence. A subsequence keeps the original order of elements but may skip some of them, and strictly increasing means every chosen value is larger than the one before it.</p><p>An O(n&sup2;) solution is easy; try to reach O(n log n).</p>",
    constraints=["1 &le; nums.length &le; 10,000", "-10<sup>9</sup> &le; nums[i] &le; 10<sup>9</sup>"],
    hints=["Let L(i) be the length of the longest increasing subsequence that ends exactly at index i. How does it relate to earlier indices?",
           "L(i) = 1 + max(L(j)) over all j &lt; i with nums[j] &lt; nums[i]. That is the O(n&sup2;) solution.",
           "For O(n log n), keep <code>tails[k]</code>, the smallest possible last value of an increasing subsequence of length k+1. It stays sorted, so each new number can be placed with binary search."],
    editorial=["Maintain a sorted list <code>tails</code> where <code>tails[k]</code> is the smallest tail value among all increasing subsequences of length k+1 seen so far. For each number x, find the first position whose value is &ge; x (binary search). If there is none, append x (a longer subsequence now exists); otherwise overwrite that slot with x, which makes a tail smaller or equal and never hurts. The answer is the length of <code>tails</code>.",
               "Note that <code>tails</code> itself is not a valid subsequence, only its length is meaningful. Searching for the first value &ge; x (not &gt; x) is what makes the subsequence strictly increasing. The simple DP over all pairs needs O(n&sup2;) time, which is too slow for 10,000 elements in a browser."],
    time="O(n log n)", space="O(n)",
    solution='''from bisect import bisect_left


def lengthOfLIS(nums):
    tails = []
    for x in nums:
        k = bisect_left(tails, x)
        if k == len(tails):
            tails.append(x)
        else:
            tails[k] = x
    return len(tails)
''',
    tests=[[[10, 9, 2, 5, 3, 7, 101, 18]], [[0, 1, 0, 3, 2, 3]], [[7, 7, 7, 7]], [[5]], [[1, 2, 3, 4, 5]], [[5, 4, 3, 2, 1]],
           [[-3, -1, -2, 0, -5, 4]], [[10 ** 9, -10 ** 9, 0]], [[3, 4, -1, 0, 6, 2, 3]], [[2, 2, 3, 3, 4, 4]]],
)
_r = rnd(5107)
_LIS = [[_r.randint(0, 999) for _ in range(10000)], list(range(1000)), [_r.randint(-10 ** 9, 10 ** 9) for _ in range(600)],
        list(range(800, 0, -1)), [i % 100 for i in range(1500)]]


def _brute_lis(nums):
    def go(i, last):
        if i == len(nums):
            return 0
        best = go(i + 1, last)
        if last is None or nums[i] > last:
            best = max(best, 1 + go(i + 1, nums[i]))
        return best
    return go(0, None)


CHECKS["longest-increasing-subsequence"] = (_brute_lis, lambda r: [gen_arr(r, -5, 5, 1, 12)], "exact")

# ------------------------------------------------------------------

add(
    id="decode-ways", title="Decode Ways", diff="Medium", topic="Dynamic Programming",
    fn="numDecodings", params=[("s", "string")], ret="int", cmp="exact",
    desc="<p>A message made of letters has been encoded as digits using the mapping <code>A = 1, B = 2, ..., Z = 26</code>. Given the digit string <code>s</code>, count in how many different ways it can be decoded back into letters.</p><p>Every group of digits you decode must be exactly one of the codes <code>1</code> to <code>26</code> written without a leading zero, so <code>06</code> is not a valid code and a lone <code>0</code> cannot be decoded. For example <code>11106</code> can be read as <code>1 1 10 6</code> or <code>11 10 6</code> but not as anything that uses <code>06</code>. If there is no valid decoding, return <code>0</code>. Because the count can be huge, return it modulo 1,000,000,007.</p>",
    constraints=["1 &le; s.length &le; 5,000", "s contains only the digits 0-9 (it may start with 0)"],
    hints=["Look at the end of the string. The last letter came from either the last digit or the last two digits.",
           "Let ways(i) be the number of decodings of the first i digits. The last digit contributes ways(i-1) if it is not '0'; the last two digits contribute ways(i-2) if they form a number from 10 to 26.",
           "Each value needs only the previous two, so keep two variables. Apply the modulo after every addition."],
    editorial=["Let <code>ways(i)</code> be the number of decodings of the first i characters, with <code>ways(0) = 1</code> (the empty prefix). The i-th character alone is a valid code when it is not '0', adding <code>ways(i-1)</code>. The pair of characters ending at i is valid when it lies between \"10\" and \"26\", adding <code>ways(i-2)</code>. Everything is taken modulo 1,000,000,007, and the answer is <code>ways(n)</code>.",
               "A top-down recursion on the suffix with memoisation gives the same recurrence, but recursion depth would reach 5,000. A string such as \"0\" or \"30\" gives 0 because the zero can never be attached to a valid code, and the recurrence handles that automatically: both branches contribute nothing."],
    time="O(n)", space="O(1)",
    solution='''def numDecodings(s):
    MOD = 1_000_000_007
    prev2, prev1 = 0, 1          # ways(i-2), ways(i-1); ways(0) = 1
    for i in range(1, len(s) + 1):
        cur = 0
        if s[i - 1] != '0':
            cur += prev1
        if i >= 2 and '10' <= s[i - 2:i] <= '26':
            cur += prev2
        prev2, prev1 = prev1, cur % MOD
    return prev1
''',
    tests=[["12"], ["226"], ["06"], ["0"], ["10"], ["100"], ["27"], ["2101"], ["1"], ["11106"], ["301"], ["2611055971756562"]],
)
_r = rnd(5108)
_DW = ["1" * 5000, "".join(_r.choice("1212126") for _ in range(5000)), "".join(_r.choice("0123456789") for _ in range(5000)),
       "".join(_r.choice("1111122") for _ in range(2999)) + "30"]


def _brute_decode(s):
    MOD = 1_000_000_007
    codes = {str(i) for i in range(1, 27)}

    def splits(t):
        if t == "":
            yield 1
            return
        for k in (1, 2):
            if len(t) >= k and t[:k] in codes:
                yield from splits(t[k:])
    return sum(splits(s)) % MOD


CHECKS["decode-ways"] = (_brute_decode, lambda r: ["".join(r.choice("0112236789") for _ in range(r.randint(1, 12)))], "exact")

# ------------------------------------------------------------------

add(
    id="longest-common-subsequence", title="Longest Common Subsequence", diff="Medium", topic="Dynamic Programming",
    fn="longestCommonSubsequence", params=[("text1", "string"), ("text2", "string")], ret="int", cmp="exact",
    desc="<p>Given two strings <code>text1</code> and <code>text2</code>, return the length of their longest common subsequence. A subsequence is obtained by deleting zero or more characters from a string without changing the order of the characters that remain.</p><p>If the strings share no characters, the answer is <code>0</code>.</p>",
    constraints=["0 &le; text1.length, text2.length &le; 1,500", "Both strings contain only lowercase English letters"],
    hints=["Compare the last characters of the two strings. What if they are equal? What if they differ?",
           "Let L(i, j) be the answer for the first i characters of text1 and the first j of text2. If the characters match, L(i, j) = L(i-1, j-1) + 1; otherwise L(i, j) = max(L(i-1, j), L(i, j-1)).",
           "Fill an (m+1) x (n+1) table row by row. Row 0 and column 0 are all zeros. Only the previous row is needed, which saves memory."],
    editorial=["Use a table where <code>dp[i][j]</code> is the LCS length of the first i characters of <code>text1</code> and the first j of <code>text2</code>. When the two last characters are equal they can both be matched, giving <code>dp[i-1][j-1] + 1</code>. When they differ, at least one of them is unused, so take <code>max(dp[i-1][j], dp[i][j-1])</code>. The answer is <code>dp[m][n]</code>.",
               "Each row depends only on the one above, so two rows of length n+1 are enough, reducing space from O(m &middot; n) to O(n). Brute force over all subsequences of one string is exponential. The table approach performs about 2.25 million cell updates at the maximum size, well within limits."],
    time="O(m &middot; n)", space="O(n)",
    solution='''def longestCommonSubsequence(text1, text2):
    m, n = len(text1), len(text2)
    prev = [0] * (n + 1)
    for i in range(1, m + 1):
        cur = [0] * (n + 1)
        a = text1[i - 1]
        for j in range(1, n + 1):
            if a == text2[j - 1]:
                cur[j] = prev[j - 1] + 1
            else:
                cur[j] = max(prev[j], cur[j - 1])
        prev = cur
    return prev[n]
''',
    tests=[["abcde", "ace"], ["abc", "abc"], ["abc", "def"], ["", ""], ["", "abc"], ["a", "a"], ["aaaa", "aa"], ["abcba", "abcbcba"],
           ["bl", "yby"], ["oxcpqrsvwf", "shmtulqrypy"]],
)
_r = rnd(5109)
_LC = [["".join(_r.choice("abcd") for _ in range(1500)), "".join(_r.choice("abcd") for _ in range(1500))],
       ["".join(_r.choice(LETTERS) for _ in range(1000)), "".join(_r.choice(LETTERS) for _ in range(800))],
       ["a" * 1200, "a" * 900 + "b" * 100]]


def _brute_lcs(a, b):
    def is_subseq(t, s):
        it = iter(s)
        return all(c in it for c in t)
    best = 0
    for mask in range(1 << len(a)):
        t = "".join(a[i] for i in range(len(a)) if mask >> i & 1)
        if len(t) > best and is_subseq(t, b):
            best = len(t)
    return best


CHECKS["longest-common-subsequence"] = (
    _brute_lcs,
    lambda r: ["".join(r.choice("abc") for _ in range(r.randint(0, 9))), "".join(r.choice("abc") for _ in range(r.randint(0, 9)))],
    "exact")

# ------------------------------------------------------------------

add(
    id="insert-interval", title="Insert Interval", diff="Medium", topic="Intervals",
    fn="insertInterval", params=[("intervals", "int[][]"), ("newInterval", "int[]")], ret="int[][]", cmp="exact",
    desc="<p>You are given a list of closed intervals <code>[start, end]</code> that is sorted by start and contains no two intervals that share a point (for consecutive intervals, <code>end</code> of one is strictly smaller than <code>start</code> of the next). You are also given one more interval <code>newInterval = [start, end]</code>.</p><p>Insert <code>newInterval</code> into the list. Merge every interval that overlaps with it, where two intervals that only share an endpoint, such as <code>[1, 3]</code> and <code>[3, 5]</code>, also count as overlapping. Return the resulting list, sorted by start and again free of overlaps.</p>",
    constraints=["0 &le; intervals.length &le; 1,000", "0 &le; start &le; end &le; 100,000 for every interval, including newInterval", "intervals is sorted by start, and each interval's end is strictly smaller than the next interval's start"],
    hints=["The existing intervals fall into three groups relative to the new one: entirely before it, overlapping it, and entirely after it.",
           "Copy every interval whose end is smaller than newInterval's start. Then, while the next interval's start is at most newInterval's end, absorb it by widening newInterval.",
           "Append the widened newInterval, then copy the remaining intervals unchanged. Because the input is sorted, one pass is enough."],
    editorial=["Walk through the sorted list once in three phases. Phase one copies intervals that end before the new interval starts. Phase two merges every interval that starts no later than the new interval's end: set the new start to the smaller start and the new end to the larger end. Phase three appends the merged interval followed by all the intervals that remain, which all start after it ends.",
               "Using <code>&le;</code> when comparing a start with the current end is what makes intervals that merely touch merge together. Inserting then re-sorting and merging the whole list also works, but costs O(n log n) while the sorted input lets us finish in O(n)."],
    time="O(n)", space="O(n)",
    solution='''def insertInterval(intervals, newInterval):
    start, end = newInterval
    res = []
    i, n = 0, len(intervals)
    while i < n and intervals[i][1] < start:
        res.append(list(intervals[i]))
        i += 1
    while i < n and intervals[i][0] <= end:
        start = min(start, intervals[i][0])
        end = max(end, intervals[i][1])
        i += 1
    res.append([start, end])
    while i < n:
        res.append(list(intervals[i]))
        i += 1
    return res
''',
    tests=[[[[1, 3], [6, 9]], [2, 5]],
           [[[1, 2], [3, 5], [6, 7], [8, 10], [12, 16]], [4, 8]],
           [[[1, 2], [5, 6]], [3, 4]],
           [[], [5, 7]],
           [[[1, 3]], [3, 5]],
           [[[3, 5]], [1, 2]],
           [[[3, 5]], [6, 8]],
           [[[3, 5]], [4, 4]],
           [[[1, 2], [4, 5], [7, 8]], [0, 100]],
           [[[1, 2], [4, 5], [7, 8]], [2, 4]],
           [[[0, 0], [2, 2], [4, 4]], [1, 1]],
           [[[0, 0], [2, 2], [4, 4]], [3, 3]],
           [[[5, 10]], [5, 10]]],
)


def _make_disjoint(r, count, maxlen, maxgap, start=0):
    out, cur = [], start
    for _ in range(count):
        s = cur
        e = s + r.randint(0, maxlen)
        out.append([s, e])
        cur = e + r.randint(1, maxgap)
    return out


_r = rnd(5110)
_II = []
_iv = _make_disjoint(_r, 700, 30, 30, 5)
_II.append([_iv, [_iv[50][0] + 1, _iv[600][1] - 1]])
_iv = _make_disjoint(_r, 600, 25, 25, 3)
_II.append([_iv, [_iv[300][1] + 1, _iv[300][1] + 3]])
_iv = _make_disjoint(_r, 500, 20, 20, 0)
_II.append([_iv, [_iv[-1][1] + 1, _iv[-1][1] + 5]])


def _brute_insert(intervals, new):
    items = [list(x) for x in intervals] + [list(new)]
    changed = True
    while changed:
        changed = False
        for i in range(len(items)):
            for j in range(i + 1, len(items)):
                a, b = items[i], items[j]
                if a[0] <= b[1] and b[0] <= a[1]:
                    items[i] = [min(a[0], b[0]), max(a[1], b[1])]
                    del items[j]
                    changed = True
                    break
            if changed:
                break
    return sorted(items)


def _gen_insert(r):
    ivs = _make_disjoint(r, r.randint(0, 6), 4, 4, r.randint(0, 3))
    a = r.randint(0, 40)
    return [ivs, [a, a + r.randint(0, 8)]]


CHECKS["insert-interval"] = (_brute_insert, _gen_insert, "exact")


def _validate_insert(tests):
    for t in tests:
        ivs, new = t["args"]
        assert len(ivs) <= 1000
        for a, b in ivs + [new]:
            assert 0 <= a <= b <= 100000
        assert all(x[1] < y[0] for x, y in zip(ivs, ivs[1:]))


VALIDATE["insert-interval"] = _validate_insert

# ------------------------------------------------------------------

add(
    id="meeting-rooms-ii", title="Meeting Rooms II", diff="Medium", topic="Intervals",
    fn="minMeetingRooms", params=[("intervals", "int[][]")], ret="int", cmp="exact",
    desc="<p>Each meeting is described by a pair <code>[start, end)</code>: it begins at time <code>start</code> and finishes at time <code>end</code>. The meetings are given in no particular order.</p><p>Return the minimum number of rooms needed so that no two meetings held in the same room overlap. A meeting that ends at time <code>t</code> does not clash with a meeting that starts at time <code>t</code>, so they can share a room. If there are no meetings, return <code>0</code>.</p>",
    constraints=["0 &le; intervals.length &le; 1,500", "0 &le; start &lt; end &le; 100,000"],
    hints=["The number of rooms you need is the largest number of meetings that are happening at the same moment.",
           "Separate the start times from the end times and sort each list.",
           "Sweep through the starts in order. If the earliest unfinished meeting has already ended (its end &le; this start), reuse its room; otherwise open a new room."],
    editorial=["Sort all start times and all end times independently. Use two pointers: for each start time s in order, if the smallest remaining end time is &le; s, a room has been freed, so advance the end pointer (reuse the room); otherwise we need an additional room. The number of times we could not reuse a room is the answer.",
               "Alternatively keep a min-heap of end times of the meetings in progress: sort meetings by start, pop the heap top if it is &le; the new start, then push the new end. The heap size at the end is the answer. Both run in O(n log n); the two-sorted-lists version avoids the heap."],
    time="O(n log n)", space="O(n)",
    solution='''def minMeetingRooms(intervals):
    starts = sorted(iv[0] for iv in intervals)
    ends = sorted(iv[1] for iv in intervals)
    rooms = 0
    e = 0
    for s in starts:
        if ends[e] <= s:
            e += 1          # a meeting finished, reuse its room
        else:
            rooms += 1
    return rooms
''',
    tests=[[[[0, 30], [5, 10], [15, 20]]], [[[7, 10], [2, 4]]], [[[1, 5], [5, 9], [9, 12]]], [[]], [[[3, 4]]],
           [[[1, 10], [2, 9], [3, 8], [4, 7]]], [[[1, 2], [1, 2], [1, 2]]], [[[0, 5], [5, 10], [3, 7], [7, 12]]],
           [[[10, 20], [0, 10], [5, 15], [15, 25], [20, 30]]], [[[0, 100000], [0, 1], [99999, 100000]]]],
)
_r = rnd(5111)
_MR = []
_MR.append([[(lambda s: [s, s + _r.randint(1, 1000)])(_r.randint(0, 99000)) for _ in range(1500)]])
_MR.append([[[0, 1] for _ in range(1000)]])
_MR.append([[(lambda s: [s, s + 1])(i) for i in range(800)] + [[0, 100000]]])


def _brute_rooms(intervals):
    best = 0
    for t in range(0, 40):
        best = max(best, sum(1 for s, e in intervals if s <= t < e))
    return best


def _gen_rooms(r):
    out = []
    for _ in range(r.randint(0, 9)):
        s = r.randint(0, 20)
        out.append([s, s + r.randint(1, 8)])
    return [out]


CHECKS["meeting-rooms-ii"] = (_brute_rooms, _gen_rooms, "exact")


def _validate_rooms(tests):
    for t in tests:
        iv = t["args"][0]
        assert len(iv) <= 1500 and all(0 <= s < e <= 100000 for s, e in iv)


VALIDATE["meeting-rooms-ii"] = _validate_rooms

# ---------------------------------------------------------------- HARD

add(
    id="longest-valid-parentheses", title="Longest Valid Parentheses", diff="Hard", topic="Stack",
    fn="longestValidParentheses", params=[("s", "string")], ret="int", cmp="exact",
    desc="<p>Given a string <code>s</code> consisting only of the characters <code>(</code> and <code>)</code>, return the length of the longest contiguous substring that is a well-formed (balanced) bracket sequence.</p><p>A sequence is well-formed when every <code>(</code> has a matching <code>)</code> later on and every <code>)</code> has a matching <code>(</code> before it. The empty string has length <code>0</code>.</p>",
    constraints=["0 &le; s.length &le; 10,000", "s contains only ( and )"],
    hints=["Checking every substring costs O(n&sup2;) or O(n&sup3;). Think about how a stack finds matching pairs in a single pass.",
           "Push indices of unmatched characters onto the stack, starting with a sentinel -1. A valid run then extends from the index just under the top of the stack up to the current index.",
           "On '(' push its index. On ')' pop; if the stack is now empty, push the current index as the new sentinel, else the run length is <code>i - stack[-1]</code>."],
    editorial=["Keep a stack of indices, initialised with -1 as a base. For each '(' push its index. For each ')' pop the top; if the stack becomes empty this ')' is unmatched, so push its index as the new base; otherwise the valid substring ending here starts right after the new top, and its length is <code>i - stack[-1]</code>. The answer is the largest such length.",
               "There is an O(1) space alternative: scan left to right counting '(' and ')' and reset both counters when ')' exceeds '('; record 2 * ')' whenever the counts are equal. Then scan right to left with the roles swapped. A DP over end positions also works, but the stack version is the easiest to get right."],
    time="O(n)", space="O(n)",
    solution='''def longestValidParentheses(s):
    stack = [-1]
    best = 0
    for i, c in enumerate(s):
        if c == '(':
            stack.append(i)
        else:
            stack.pop()
            if not stack:
                stack.append(i)
            else:
                best = max(best, i - stack[-1])
    return best
''',
    tests=[["(()"], [")()())"], ["()(())"], [""], ["("], [")"], ["))(("], ["()()"], ["(()()"], ["()(()"], ["(()))())("],
           ["((()))((("], [")(" * 10], ["(" * 20 + ")" * 20], ["()(()()"]],
)
_r = rnd(5112)


def _walk(r, n, p_break):
    out, depth = [], 0
    for _ in range(n):
        if depth == 0:
            c = ")" if r.random() < p_break else "("
        else:
            c = "(" if r.random() < 0.5 else ")"
        if c == "(":
            depth += 1
        elif depth > 0:
            depth -= 1
        out.append(c)
    return "".join(out)


_LP = ["()" * 5000, "(" * 5000 + ")" * 5000, "".join(_r.choice("()") for _ in range(10000)), _walk(_r, 10000, 0.02),
       "(" * 3000 + "()" * 2000 + ")" * 2000 + ")" * 1000]


def _brute_lvp(s):
    best = 0
    n = len(s)
    for i in range(n):
        for j in range(i + 2, n + 1, 2):
            bal = 0
            ok = True
            for c in s[i:j]:
                bal += 1 if c == "(" else -1
                if bal < 0:
                    ok = False
                    break
            if ok and bal == 0:
                best = max(best, j - i)
    return best


CHECKS["longest-valid-parentheses"] = (_brute_lvp, lambda r: ["".join(r.choice("()") for _ in range(r.randint(0, 14)))], "exact")

# ------------------------------------------------------------------

add(
    id="burst-balloons", title="Burst Balloons", diff="Hard", topic="Dynamic Programming",
    fn="maxCoins", params=[("nums", "int[]")], ret="int", cmp="exact",
    desc="<p>There are <code>n</code> balloons in a row, and balloon <code>i</code> is painted with the number <code>nums[i]</code>. You burst all of them one at a time, in an order you choose. Bursting balloon <code>i</code> earns <code>left * nums[i] * right</code> coins, where <code>left</code> and <code>right</code> are the numbers on the nearest balloons that have not burst yet on either side. If there is no such balloon on a side, use <code>1</code> for that side.</p><p>Return the maximum number of coins you can collect by bursting every balloon. With no balloons, the answer is <code>0</code>.</p>",
    constraints=["0 &le; nums.length &le; 300", "0 &le; nums[i] &le; 100"],
    hints=["Choosing which balloon to burst first splits the row in a way that makes the two parts depend on each other. Try thinking about which balloon is burst last instead.",
           "If balloon k is the last one to burst inside the open range (l, r), its neighbours at that moment are exactly l and r, and the two sides (l, k) and (k, r) are independent subproblems.",
           "Pad the array with a 1 at both ends. Let dp[l][r] be the best total for the balloons strictly between l and r. Then dp[l][r] = max over k of dp[l][k] + dp[k][r] + a[l]*a[k]*a[r]. Fill by increasing interval length."],
    editorial=["Pad the array: <code>a = [1] + nums + [1]</code>. Define <code>dp[l][r]</code> as the maximum coins from bursting all balloons strictly between indices l and r. Pick k as the balloon that bursts <em>last</em> in that range: at that time only l and r are left beside it, so it yields <code>a[l] * a[k] * a[r]</code>, and the balloons on each side were burst earlier within their own independent ranges. So <code>dp[l][r] = max_k (dp[l][k] + dp[k][r] + a[l]*a[k]*a[r])</code>, filled by increasing gap r - l. The answer is <code>dp[0][n+1]</code>.",
               "Thinking about the first balloon to burst fails because after removing it, its neighbours become adjacent and the subproblems are no longer independent. Choosing the last one fixes this. There are O(n&sup2;) ranges and O(n) choices of k each, hence O(n&sup3;) in total; with n = 300 and values at most 100 the answer stays well below 2<sup>31</sup>."],
    time="O(n&sup3;)", space="O(n&sup2;)",
    solution='''def maxCoins(nums):
    a = [1] + list(nums) + [1]
    m = len(a)
    dp = [[0] * m for _ in range(m)]
    for gap in range(2, m):
        for l in range(m - gap):
            r = l + gap
            lr = a[l] * a[r]
            best = 0
            for k in range(l + 1, r):
                v = dp[l][k] + dp[k][r] + lr * a[k]
                if v > best:
                    best = v
            dp[l][r] = best
    return dp[0][m - 1]
''',
    tests=[[[3, 1, 5, 8]], [[1, 5]], [[7]], [[]], [[0]], [[0, 0, 0]], [[100, 100]], [[2, 3, 4, 5, 6]], [[9, 76, 64, 21]],
           [[8, 2, 6, 0, 9, 8, 1]]],
)
_r = rnd(5113)
_BB = [[_r.randint(0, 100) for _ in range(300)], [100] * 250, [_r.randint(1, 100) for _ in range(120)]]


def _brute_balloons(nums):
    def go(arr):
        if not arr:
            return 0
        best = 0
        for i in range(len(arr)):
            left = arr[i - 1] if i > 0 else 1
            right = arr[i + 1] if i + 1 < len(arr) else 1
            best = max(best, left * arr[i] * right + go(arr[:i] + arr[i + 1:]))
        return best
    return go(list(nums))


CHECKS["burst-balloons"] = (_brute_balloons, lambda r: [gen_arr(r, 0, 9, 0, 7)], "exact")


def _validate_balloons(tests):
    for t in tests:
        nums = t["args"][0]
        assert len(nums) <= 300 and all(0 <= x <= 100 for x in nums)
        assert t["expected"] <= 2 ** 31 - 1


VALIDATE["burst-balloons"] = _validate_balloons

# ------------------------------------------------------------------

add(
    id="regular-expression-matching", title="Regular Expression Matching", diff="Hard", topic="Dynamic Programming",
    fn="isMatch", params=[("s", "string"), ("p", "string")], ret="bool", cmp="exact",
    desc="<p>Implement a tiny pattern matcher. Given a text <code>s</code> and a pattern <code>p</code>, return <code>true</code> if the pattern matches the <em>entire</em> text, and <code>false</code> otherwise.</p><p>The pattern supports two special characters. <code>.</code> matches any single character. <code>*</code> means &quot;zero or more copies of the element right before it&quot;, where that element is either a letter or a <code>.</code>. For example <code>a*</code> matches <code>\"\"</code>, <code>a</code>, <code>aaa</code>, and <code>.*</code> matches any string at all. The pattern is well-formed: a <code>*</code> never appears first and never directly follows another <code>*</code>.</p>",
    constraints=["0 &le; s.length, p.length &le; 1,000", "s contains only lowercase English letters", "p contains only lowercase English letters, '.' and '*'", "In p, every '*' has a letter or '.' directly before it"],
    hints=["Compare the pattern and the text from the front. A plain character or '.' consumes exactly one text character; the interesting case is a '*'.",
           "Let match(i, j) say whether s[i:] matches p[j:]. If p[j+1] is '*', you either skip the pair p[j], p[j+1] entirely, or (when s[i] fits p[j]) consume one text character and stay on the same pattern position.",
           "Fill a table from the ends toward the front, or memoise the recursion. There are only (|s|+1) x (|p|+1) distinct states."],
    editorial=["Define <code>dp[i][j]</code> as true when <code>s[i:]</code> matches <code>p[j:]</code>. The base case is <code>dp[|s|][|p|] = true</code>. For a state, let <code>first</code> be true when <code>i &lt; |s|</code> and <code>p[j]</code> is equal to <code>s[i]</code> or is '.'. If <code>p[j+1]</code> is '*', then <code>dp[i][j] = dp[i][j+2] or (first and dp[i+1][j])</code>: use zero copies, or use one copy and stay on the same starred element. Otherwise <code>dp[i][j] = first and dp[i+1][j+1]</code>.",
               "Filling the table from the bottom-right corner needs only two rows at a time. A plain recursion without memoisation repeats the same states exponentially often (patterns like <code>a*a*a*a*b</code> are the classic killer), which is why the table matters. Because the whole text must match, an empty text can still match a pattern like <code>a*b*</code>."],
    time="O(|s| &middot; |p|)", space="O(|p|)",
    solution='''def isMatch(s, p):
    m, n = len(s), len(p)
    nxt = [False] * (n + 1)          # row i + 1; start with i = m (empty rest of text)
    nxt[n] = True
    for j in range(n - 2, -1, -1):
        nxt[j] = p[j + 1] == '*' and nxt[j + 2]
    # nxt now describes i = m
    for i in range(m - 1, -1, -1):
        cur = [False] * (n + 1)
        for j in range(n - 1, -1, -1):
            first = p[j] == s[i] or p[j] == '.'
            if j + 1 < n and p[j + 1] == '*':
                cur[j] = cur[j + 2] or (first and nxt[j])
            else:
                cur[j] = first and nxt[j + 1]
        nxt = cur
    return nxt[0]
''',
    tests=[["aa", "a"], ["aa", "a*"], ["ab", ".*"], ["", ""], ["", "a*"], ["", "a*b*"], ["a", ""], ["aab", "c*a*b"],
           ["mississippi", "mis*is*p*."], ["mississippi", "mis*is*ip*."], ["ab", ".*c"], ["aaa", "ab*a*c*a"], ["a", "ab*"],
           ["abcd", "d*"], ["abc", "..."], ["abc", ".."], ["aaa", "a*a"], ["aaa", "aaaa"], ["ab", ".*.."]],
)
_r = rnd(5114)


def _expand(r, tokens, max_rep):
    out = []
    for ch, star in tokens:
        reps = r.randint(0, max_rep) if star else 1
        for _ in range(reps):
            out.append(r.choice("abc") if ch == "." else ch)
    return "".join(out)


def _rand_tokens(r, count, alphabet, p_star):
    return [(r.choice(alphabet), r.random() < p_star) for _ in range(count)]


def _tokens_to_pat(tokens):
    return "".join(ch + ("*" if star else "") for ch, star in tokens)


_RX = [["a" * 1000, "a*" * 500], ["a" * 999 + "b", "a*" * 500],
       ["".join(_r.choice("abc") for _ in range(1000)), ".*" * 500]]
for _alpha, _ps in (("abc.", 0.6), ("ab..", 0.5), ("a.", 0.7)):
    _tk = _rand_tokens(_r, 420, _alpha, _ps)
    while len(_tokens_to_pat(_tk)) > 1000:
        _tk.pop()
    _s = _expand(_r, _tk, 3)[:1000]
    _RX.append([_s, _tokens_to_pat(_tk)])
    _RX.append([_s[:-1] + ("a" if _s[-1:] != "a" else "b"), _tokens_to_pat(_tk)])
_RX.append(["a" * 500 + "b" * 500, "a*b*a*b*a*b*" + "." * 4 + ".*"])
_RX.append(["ab" * 400, "a*b*" * 200 + "ab" * 100])


def _brute_regex(s, p):
    def go(s, p):
        if not p:
            return not s
        first = bool(s) and p[0] in (s[0], ".")
        if len(p) >= 2 and p[1] == "*":
            return go(s, p[2:]) or (first and go(s[1:], p))
        return first and go(s[1:], p[1:])
    return bool(go(s, p))


def _gen_regex(r):
    tokens = _rand_tokens(r, r.randint(0, 6), "ab.", 0.4)
    p = _tokens_to_pat(tokens)
    if r.random() < 0.5:
        s = _expand(r, tokens, 3)
        if r.random() < 0.3 and s:
            i = r.randrange(len(s))
            s = s[:i] + r.choice("ab") + s[i + 1:]
        s = s[:14]
    else:
        s = "".join(r.choice("ab") for _ in range(r.randint(0, 12)))
    return [s, p]


CHECKS["regular-expression-matching"] = (_brute_regex, _gen_regex, "exact")


def _validate_regex(tests):
    for t in tests:
        s, p = t["args"]
        assert len(s) <= 1000 and len(p) <= 1000
        assert all("a" <= c <= "z" for c in s)
        assert all(("a" <= c <= "z") or c in ".*" for c in p)
        for i, c in enumerate(p):
            if c == "*":
                assert i > 0 and p[i - 1] != "*"


VALIDATE["regular-expression-matching"] = _validate_regex


# ------------------------------------------------------------------ extra (large) tests
def _extend(pid, cases):
    for p_ in _P:
        if p_["id"] == pid:
            p_["tests"].extend(cases)
            return
    raise KeyError(pid)


from lib import P as _P  # noqa: E402

_extend("min-cost-climbing-stairs", [_t, _t2, _t3, _t4])
_extend("plus-one", [[d] for d in _P3])
_extend("house-robber", [[a] for a in _HR])
_extend("jump-game", [[a] for a in _JG])
_extend("longest-increasing-subsequence", [[a] for a in _LIS])
_extend("decode-ways", [[s] for s in _DW])
_extend("longest-common-subsequence", _LC)
_extend("insert-interval", _II)
_extend("meeting-rooms-ii", _MR)
_extend("longest-valid-parentheses", [[s] for s in _LP])
_extend("burst-balloons", [[a] for a in _BB])
_extend("regular-expression-matching", _RX)
