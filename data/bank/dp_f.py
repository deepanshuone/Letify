"""Problems: dynamic programming, partition and segmentation (cut a sequence into pieces). See data/lib.py for the registry."""
from itertools import combinations, combinations_with_replacement

from lib import add, rnd, CHECKS, VALIDATE, gen_arr  # noqa: F401

TOPIC = "Dynamic Programming"
MOD = 10 ** 9 + 7


# ================================================================ 1. valid partition into short blocks (Easy)

p = add(
    id="valid-block-partition-of-array", title="Valid Partition Into Short Blocks", diff="Easy", topic=TOPIC, tier="common",
    fn="canPartitionBlocks", params=[("nums", "int[]")], ret="bool", cmp="exact",
    desc="<p>Decide whether the array <code>nums</code> can be cut into consecutive blocks so that <strong>every</strong> block has one of these three shapes:</p><ul><li>two equal elements, such as <code>[7,7]</code>;</li><li>three equal elements, such as <code>[5,5,5]</code>;</li><li>three elements that go up by exactly 1 each step, such as <code>[4,5,6]</code>.</li></ul><p>Every element must belong to exactly one block. Return <code>true</code> if such a cutting exists, otherwise <code>false</code>.</p><pre>nums = [4,4,4,5,6]  -> true    ([4,4] and [4,5,6])\nnums = [1,1,1,2]    -> false   (no cutting works)\nnums = [3,4,5]      -> true    (one block of three consecutive values)</pre>",
    constraints=["1 &le; nums.length &le; 6,000", "1 &le; nums[i] &le; 1,000,000"],
    hints=["Look at the end of the array. Which block shapes could be the last block, and what remains in front of them?",
           "Let <code>ok[i]</code> be true when the first <code>i</code> elements can be cut into valid blocks, with <code>ok[0] = true</code>.",
           "<code>ok[i]</code> is true if (<code>ok[i-2]</code> and the last two elements are equal) or (<code>ok[i-3]</code> and the last three elements are all equal or form x, x+1, x+2). The answer is <code>ok[n]</code>."],
    editorial=["A prefix DP works because a block has a fixed small length. Let <code>ok[i]</code> tell whether the first <code>i</code> elements can be cut into valid blocks; the empty prefix is fine, so <code>ok[0] = true</code>. The last block of a good prefix is a pair of equal elements (then <code>ok[i-2]</code> must hold) or a triple of equal or consecutive-increasing elements (then <code>ok[i-3]</code> must hold).",
               "Each state looks at the previous two or three states, so one pass in O(n) time suffices; keeping only the last three booleans reduces memory to O(1). A greedy rule such as 'always take a triple first' fails: <code>[1,1,1,1]</code> needs two pairs, while <code>[1,1,1,2,3]</code> needs a pair and a run, not a triple of ones."],
    time="O(n)", space="O(n)",
    solution='''def canPartitionBlocks(nums):
    n = len(nums)
    ok = [False] * (n + 1)
    ok[0] = True
    for i in range(2, n + 1):
        a = nums[i - 1]
        b = nums[i - 2]
        if ok[i - 2] and a == b:
            ok[i] = True
        elif i >= 3 and ok[i - 3]:
            c = nums[i - 3]
            if (a == b == c) or (b == c + 1 and a == b + 1):
                ok[i] = True
    return ok[n]
''',
    tests=[[[4, 4, 4, 5, 6]], [[1, 1, 1, 2]], [[3, 4, 5]], [[2, 2]], [[9]], [[1, 2]], [[1, 1, 1, 1]], [[1, 1, 1, 2, 3]],
           [[5, 5, 5, 5, 5]], [[1, 2, 3, 3, 4, 5, 7, 7]], [[6, 7, 8, 6, 7, 8, 8]]],
)
_r = rnd(8301)


def _block_seq(r, nblocks, vmax):
    out = []
    for _ in range(nblocks):
        v = r.randint(1, vmax)
        kind = r.randint(0, 2)
        out += [[v, v], [v, v, v], [v, v + 1, v + 2]][kind]
    return out


_a = _block_seq(_r, 2000, 1000)
assert len(_a) <= 6000
p["tests"].append([_a])
_b = _block_seq(_r, 2000, 1000)
_b[-1] += 1000     # breaks the final block
p["tests"].append([_b])
p["tests"].append([[7] * 6000])
p["tests"].append([[7] * 5999])


def _b_valid_blocks(nums):
    n = len(nums)

    def go(i):
        if i == n:
            return True
        if i + 2 <= n and nums[i] == nums[i + 1] and go(i + 2):
            return True
        if i + 3 <= n:
            a, b, c = nums[i:i + 3]
            if (a == b == c or (b == a + 1 and c == b + 1)) and go(i + 3):
                return True
        return False
    return go(0)


def _g_valid_blocks(r):
    if r.random() < 0.6:
        a = _block_seq(r, r.randint(1, 4), 3)
        if r.random() < 0.4:
            a[r.randrange(len(a))] = r.randint(1, 4)
        return [a]
    return [[r.randint(1, 3) for _ in range(r.randint(1, 10))]]


def _v_valid_blocks(tests):
    for t in tests:
        a = t["args"][0]
        assert 1 <= len(a) <= 6000 and all(1 <= x <= 1000000 for x in a)
    assert any(t["expected"] for t in tests) and not all(t["expected"] for t in tests)


CHECKS["valid-block-partition-of-array"] = (_b_valid_blocks, _g_valid_blocks, "exact")
VALIDATE["valid-block-partition-of-array"] = _v_valid_blocks


# ================================================================ 2. single-one blocks (Easy)

p = add(
    id="ways-to-split-into-single-one-blocks", title="Split Into Blocks With Exactly One One", diff="Easy", topic=TOPIC, tier="common",
    fn="countSingleOneSplits", params=[("nums", "int[]")], ret="int", cmp="exact",
    desc="<p>The array <code>nums</code> contains only <code>0</code> and <code>1</code>. Cut it into consecutive, non-empty blocks so that <strong>every block contains exactly one <code>1</code></strong>. Every element must belong to some block.</p><p>Return the number of different ways to cut the array, modulo <code>1,000,000,007</code>. Two ways differ if they place a cut at different positions. If no valid cutting exists, return <code>0</code>.</p><pre>nums = [0,1,0,0,1]  -> 3   ([0,1 | 0,0,1], [0,1,0 | 0,1], [0,1,0,0 | 1])\nnums = [0,1,0]      -> 1   (the whole array)\nnums = [0,0]        -> 0   (there is no 1 at all)</pre>",
    constraints=["1 &le; nums.length &le; 8,000", "nums[i] is 0 or 1"],
    hints=["Every block holds exactly one 1, so the number of blocks equals the number of 1s. What does that say about the zeros before the first 1 and after the last 1?",
           "Look at two neighbouring 1s with some zeros between them. Exactly one cut must be placed somewhere between them. How many places can it go?",
           "If the neighbouring 1s are at indices <code>a &lt; b</code>, the cut can go in any of <code>b - a</code> gaps. The cuts for different pairs are independent, so multiply these numbers (modulo 1,000,000,007)."],
    editorial=["Each block owns one 1, so there is one block per 1, and the zeros before the first 1 or after the last 1 simply join the first or last block (no choice there). Between two consecutive 1s at indices <code>a</code> and <code>b</code> there must be exactly one cut, and it can be placed in any of the <code>b - a</code> gaps between index <code>a</code> and index <code>b</code>.",
               "The choices for different pairs do not influence each other, so the answer is the product of <code>b - a</code> over all neighbouring pairs of 1s, or 0 if the array has no 1. The same result comes from a prefix DP: <code>ways[i]</code> counts the cuttings of the first <code>i</code> elements, and each new 1 multiplies the count by the distance to the previous 1. One pass, O(n) time and O(1) extra space."],
    time="O(n)", space="O(1)",
    solution='''def countSingleOneSplits(nums):
    M = 1000000007
    prev = -1
    ans = 1
    for i, x in enumerate(nums):
        if x == 1:
            if prev != -1:
                ans = ans * (i - prev) % M
            prev = i
    return ans if prev != -1 else 0
''',
    tests=[[[0, 1, 0, 0, 1]], [[0, 1, 0]], [[0, 0]], [[1]], [[0]], [[1, 1, 1]], [[1, 0, 0, 0, 1]], [[0, 1, 1, 0, 1, 0, 0, 1, 0]],
           [[1, 0, 1, 0, 1]], [[0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0]]],
)
_r = rnd(8201)
_a = [0] * 8000
for _i in _r.sample(range(8000), 400):
    _a[_i] = 1
p["tests"].append([_a])
p["tests"].append([[1] * 8000])
_a = [0] * 8000
_a[0] = 1
_a[7999] = 1
p["tests"].append([_a])
_a = [0] * 8000
for _i in _r.sample(range(8000), 40):
    _a[_i] = 1
p["tests"].append([_a])


def _b_one_blocks(nums):
    n = len(nums)
    total = 0
    for mask in range(1 << (n - 1)):          # bit i set = cut after index i
        ok = True
        cnt = nums[0]
        for i in range(1, n):
            if (mask >> (i - 1)) & 1:
                if cnt != 1:
                    ok = False
                    break
                cnt = 0
            cnt += nums[i]
        if ok and cnt == 1:
            total += 1
    return total % MOD


def _g_one_blocks(r):
    n = r.randint(1, 12)
    q = r.choice([0.2, 0.4, 0.6])
    return [[1 if r.random() < q else 0 for _ in range(n)]]


def _v_one_blocks(tests):
    for t in tests:
        a = t["args"][0]
        assert 1 <= len(a) <= 8000 and all(x in (0, 1) for x in a)
    assert any(t["expected"] == 0 for t in tests) and any(t["expected"] > 1 for t in tests)


CHECKS["ways-to-split-into-single-one-blocks"] = (_b_one_blocks, _g_one_blocks, "exact")
VALIDATE["ways-to-split-into-single-one-blocks"] = _v_one_blocks


# ================================================================ 3. partition for maximum sum (Medium)

p = add(
    id="partition-array-max-sum-length-capped", title="Partition Into Short Blocks, Replace by Maximum", diff="Medium", topic=TOPIC, tier="common",
    fn="maxSumAfterPartition", params=[("arr", "int[]"), ("k", "int")], ret="int", cmp="exact",
    desc="<p>Cut the array <code>arr</code> into consecutive non-empty blocks, each of length <strong>at most</strong> <code>k</code>. Then overwrite every element of a block with the largest value of that block. Return the largest possible sum of the array after this change.</p><pre>arr = [2,1,3], k = 2  -> 8    (blocks [2] and [1,3] become [2] and [3,3]: 2 + 3 + 3)\narr = [4,4,4], k = 1  -> 12   (every block has length 1, nothing changes)\narr = [1,5,2,2], k = 3 -> 17  (blocks [1,5,2] and [2] become [5,5,5] and [2]: 15 + 2)</pre>",
    constraints=["1 &le; arr.length &le; 4,000", "0 &le; arr[i] &le; 100,000", "1 &le; k &le; min(arr.length, 100)"],
    hints=["Think about the last block of the array. If it has length <code>L</code>, everything before it is a smaller instance of the same question.",
           "Let <code>dp[i]</code> be the best sum for the first <code>i</code> elements. The last block covers positions <code>i-L .. i-1</code> for some <code>L</code> from 1 to <code>k</code> and contributes <code>L * max(arr[i-L..i-1])</code>.",
           "For each <code>i</code>, walk <code>L</code> from 1 up to <code>min(k, i)</code> and keep a running maximum of the block, so every candidate costs O(1): <code>dp[i] = max(dp[i-L] + L * runningMax)</code>."],
    editorial=["Define <code>dp[i]</code> as the maximum sum obtainable from the first <code>i</code> elements, with <code>dp[0] = 0</code>. The block that ends at position <code>i</code> has some length <code>L &le; k</code>. All its elements become the block maximum, so it adds <code>L * max</code>, and the elements before it are an independent subproblem: <code>dp[i] = max over L of dp[i - L] + L * max(arr[i-L..i-1])</code>.",
               "While <code>L</code> grows by one the block extends one step to the left, so the block maximum can be maintained incrementally instead of recomputed. This gives O(n &middot; k) time and O(n) space. The first element of a block never needs to be small: the dp automatically considers every possible block boundary."],
    time="O(n * k)", space="O(n)",
    solution='''def maxSumAfterPartition(arr, k):
    n = len(arr)
    dp = [0] * (n + 1)
    for i in range(1, n + 1):
        m = 0
        best = 0
        for L in range(1, min(k, i) + 1):
            if arr[i - L] > m:
                m = arr[i - L]
            v = dp[i - L] + m * L
            if v > best:
                best = v
        dp[i] = best
    return dp[n]
''',
    tests=[[[2, 1, 3], 2], [[4, 4, 4], 1], [[1, 15, 7, 9, 2, 5, 10], 3], [[7], 1], [[0, 0], 2], [[9, 1, 1, 9], 1], [[9, 1, 1, 9], 4],
           [[1, 2, 3, 4, 5], 2], [[5, 4, 3, 2, 1], 5], [[3, 0, 0, 0, 8, 0], 3]],
)
_r = rnd(8203)
p["tests"].append([[_r.randint(0, 100000) for _ in range(4000)], 100])
p["tests"].append([[_r.randint(0, 100000) for _ in range(4000)], 1])
p["tests"].append([sorted(_r.randint(0, 100000) for _ in range(4000)), 37])
p["tests"].append([[_r.randint(0, 9) * 10000 for _ in range(3000)], 64])


def _b_partition_sum(arr, k):
    n = len(arr)

    def go(i):
        if i == n:
            return 0
        best = 0
        for L in range(1, min(k, n - i) + 1):
            best = max(best, max(arr[i:i + L]) * L + go(i + L))
        return best
    return go(0)


def _g_partition_sum(r):
    n = r.randint(1, 10)
    return [[r.randint(0, 9) for _ in range(n)], r.randint(1, n)]


def _v_partition_sum(tests):
    for t in tests:
        arr, k = t["args"]
        assert 1 <= len(arr) <= 4000 and all(0 <= x <= 100000 for x in arr)
        assert 1 <= k <= min(len(arr), 100)


CHECKS["partition-array-max-sum-length-capped"] = (_b_partition_sum, _g_partition_sum, "exact")
VALIDATE["partition-array-max-sum-length-capped"] = _v_partition_sum


# ================================================================ 4. word wrap (Medium)

p = add(
    id="word-wrap-min-raggedness", title="Word Wrap With Least Raggedness", diff="Medium", topic=TOPIC, tier="common",
    fn="minRaggedness", params=[("lens", "int[]"), ("width", "int")], ret="int", cmp="exact",
    desc="<p>A paragraph consists of words in a fixed order; <code>lens[i]</code> is the length of word <code>i</code>. The words are placed on lines of <code>width</code> characters in the given order, and neighbouring words on the same line are separated by exactly one space. A line must not be longer than <code>width</code>, and a word is never split across lines.</p><p>For every line except the last one, the <em>penalty</em> is <code>(width - lineLength)<sup>2</sup></code>, where <code>lineLength</code> counts the letters plus the spaces. The last line has no penalty. Return the smallest total penalty over all valid ways to break the paragraph into lines.</p><pre>lens = [3,2,2,5], width = 6  -> 10   (lines: [3], [2,2], [5] gives 9 + 1 + 0)\nlens = [4,4,4],   width = 4  -> 0    (one word per line, all lines are exactly full)</pre>",
    constraints=["1 &le; lens.length &le; 5,000", "1 &le; width &le; 80", "1 &le; lens[i] &le; width"],
    hints=["A greedy rule such as 'put as many words on each line as fit' can be beaten: sometimes moving one word to the next line makes both lines better. Think about the position where the last line ends.",
           "Let <code>dp[i]</code> be the least penalty to place the first <code>i</code> words so that line <code>i</code> ends exactly after word <code>i-1</code>. The last line of that prefix starts at some word <code>j</code>.",
           "<code>dp[i] = min over valid j of dp[j] + cost(j, i)</code>, where the line made of words <code>j..i-1</code> must fit in <code>width</code>, and the cost is <code>(width - length)^2</code> unless <code>i</code> equals the total number of words (then the cost is 0). A line holds at most about <code>width / 2</code> words, so for each <code>i</code> you only need to look back that far."],
    editorial=["Let <code>dp[i]</code> be the smallest penalty for the first <code>i</code> words, where word <code>i-1</code> ends a line. The last line of this prefix contains words <code>j .. i-1</code> for some <code>j</code>, and it is valid when <code>sum(lens[j..i-1]) + (i - 1 - j) &le; width</code>. Its cost is <code>(width - length)<sup>2</sup></code>, except for the very last line of the whole paragraph (<code>i = n</code>), which is free. Then <code>dp[i] = min(dp[j] + cost)</code> over the valid <code>j</code>, and the answer is <code>dp[n]</code>.",
               "Scan <code>j</code> downward from <code>i - 1</code> while keeping the running line length, and stop as soon as the line gets too long. Because every word has length at least 1, a line contains at most <code>(width + 1) / 2</code> words, so the whole DP is O(n &middot; width) time with O(n) memory. Every word fits on a line of its own, so <code>dp[j]</code> is always finite."],
    time="O(n * width)", space="O(n)",
    solution='''def minRaggedness(lens, width):
    n = len(lens)
    INF = float("inf")
    dp = [INF] * (n + 1)
    dp[0] = 0
    for i in range(1, n + 1):
        total = -1
        best = INF
        for j in range(i - 1, -1, -1):
            total += lens[j] + 1
            if total > width:
                break
            cost = 0 if i == n else (width - total) ** 2
            v = dp[j] + cost
            if v < best:
                best = v
        dp[i] = best
    return dp[n]
''',
    tests=[[[3, 2, 2, 5], 6], [[4, 4, 4], 4], [[5], 5], [[1, 1, 1], 3], [[2, 3, 4, 5], 10], [[1, 2, 3, 4, 5, 6], 7],
           [[7, 7, 7, 7, 7], 7], [[1] * 10, 5], [[3, 3, 3, 3], 7], [[6, 1, 1, 6, 1, 1], 8]],
)
_r = rnd(8204)
p["tests"].append([[_r.randint(1, 15) for _ in range(5000)], 40])
p["tests"].append([[_r.randint(1, 30) for _ in range(5000)], 80])
p["tests"].append([[1] * 4000, 79])
p["tests"].append([[_r.randint(8, 12) for _ in range(3000)], 30])


def _b_wrap(lens, width):
    n = len(lens)

    def go(i):
        if i == n:
            return 0
        best = None
        length = -1
        for j in range(i, n):
            length += lens[j] + 1
            if length > width:
                break
            cost = 0 if j == n - 1 else (width - length) ** 2
            v = cost + go(j + 1)
            if best is None or v < best:
                best = v
        return best
    return go(0)


def _g_wrap(r):
    width = r.randint(1, 12)
    return [[r.randint(1, width) for _ in range(r.randint(1, 9))], width]


def _v_wrap(tests):
    for t in tests:
        lens, w = t["args"]
        assert 1 <= len(lens) <= 5000 and 1 <= w <= 80 and all(1 <= x <= w for x in lens)


CHECKS["word-wrap-min-raggedness"] = (_b_wrap, _g_wrap, "exact")
VALIDATE["word-wrap-min-raggedness"] = _v_wrap


# ================================================================ 5. count cuttings into patterns (Medium)

p = add(
    id="count-cuts-into-known-patterns", title="Count Ways to Cut Into Known Patterns", diff="Medium", topic=TOPIC, tier="common",
    fn="countPatternCuts", params=[("seq", "int[]"), ("patterns", "int[][]")], ret="int", cmp="exact",
    desc="<p>You are given a sequence <code>seq</code> of integers and a list <code>patterns</code> of distinct non-empty integer sequences (each row of <code>patterns</code> is one pattern). A <em>cutting</em> splits <code>seq</code> into consecutive non-empty pieces so that <strong>every piece is exactly equal to one of the patterns</strong>. A pattern may be used any number of times.</p><p>Return the number of different cuttings, modulo <code>1,000,000,007</code>. Two cuttings are different if they put cuts at different positions. Return <code>0</code> if no cutting exists.</p><pre>seq = [1,2,1,2], patterns = [[1],[2],[1,2]]  -> 4   (1|2|1|2, 12|1|2, 1|2|12, 12|12)\nseq = [1,1,1],   patterns = [[1],[1,1]]      -> 3   (1|1|1, 11|1, 1|11)\nseq = [1,2],     patterns = [[2],[3]]        -> 0</pre>",
    constraints=["1 &le; seq.length &le; 5,000", "1 &le; patterns.length &le; 300; 1 &le; patterns[i].length &le; 10; all patterns are distinct", "0 &le; seq[i], patterns[i][j] &le; 1,000"],
    hints=["This is the 'word break' question where you have to count instead of decide. Think about which piece comes last.",
           "Let <code>ways[i]</code> be the number of cuttings of the first <code>i</code> numbers, with <code>ways[0] = 1</code> for the empty prefix.",
           "<code>ways[i]</code> is the sum of <code>ways[i - L]</code> over all pattern lengths <code>L</code> for which the last <code>L</code> numbers of the prefix equal a pattern. Store the patterns as tuples in a set so the comparison is one lookup, and only try the distinct lengths."],
    editorial=["Count prefix cuttings. Let <code>ways[0] = 1</code>. For a prefix of length <code>i</code>, the last piece is a pattern that ends at position <code>i</code>; if it has length <code>L</code> and equals <code>seq[i-L:i]</code>, the part before it can be cut in <code>ways[i-L]</code> ways. Adding these over all matching patterns gives <code>ways[i]</code>. Distinct patterns of equal length cannot both match the same slice, so nothing is counted twice.",
               "Put each pattern (as a tuple) in a hash set and keep the sorted list of distinct lengths (at most 10). For each end position and each length, build the slice as a tuple and test membership. That is about n &middot; 10 lookups of length at most 10, so the cost is O(n &middot; D &middot; L) where D is the number of distinct lengths and L the longest pattern. Remember to take everything modulo 1,000,000,007."],
    time="O(n * D * L)", space="O(n + total pattern size)",
    solution='''def countPatternCuts(seq, patterns):
    M = 1000000007
    pats = set(tuple(q) for q in patterns)
    lens = sorted(set(len(q) for q in patterns))
    n = len(seq)
    ways = [0] * (n + 1)
    ways[0] = 1
    for i in range(1, n + 1):
        total = 0
        for L in lens:
            if L > i:
                break
            if ways[i - L] and tuple(seq[i - L:i]) in pats:
                total += ways[i - L]
        ways[i] = total % M
    return ways[n]
''',
    tests=[[[1, 2, 1, 2], [[1], [2], [1, 2]]], [[1, 1, 1], [[1], [1, 1]]], [[1, 2], [[2], [3]]], [[5], [[5]]], [[5], [[4]]],
           [[0, 0, 0, 0], [[0, 0]]], [[0, 0, 0, 0, 0], [[0, 0]]], [[1, 2, 3, 1, 2, 3], [[1, 2, 3], [1, 2], [3], [3, 1], [2, 3, 1, 2]]],
           [[7, 7, 7, 7, 7, 7, 7], [[7], [7, 7], [7, 7, 7]]]],
)
_r = rnd(8205)


def _tiling_case(r, n, alphabet, npat, minl, maxl):
    pats = set()
    while len(pats) < npat:
        pats.add(tuple(r.randrange(alphabet) for _ in range(r.randint(minl, maxl))))
    pats = [list(q) for q in sorted(pats)]
    seq = []
    while True:
        q = r.choice(pats)
        if len(seq) + len(q) > n:
            break
        seq += q
    return [seq, pats]


p["tests"].append(_tiling_case(_r, 5000, 2, 120, 2, 9))
p["tests"].append(_tiling_case(_r, 5000, 3, 250, 3, 10))
_c = _tiling_case(_r, 4000, 2, 60, 4, 8)
_c[0][-1] = 999     # a value no pattern contains: the last piece cannot exist
p["tests"].append(_c)
p["tests"].append([[0] * 4999, [[0], [0, 0], [0, 0, 0]]])


def _b_cuts(seq, patterns):
    pats = [list(q) for q in patterns]
    n = len(seq)

    def go(i):
        if i == n:
            return 1
        return sum(go(i + len(q)) for q in pats if seq[i:i + len(q)] == q)
    return go(0) % MOD


def _g_cuts(r):
    alpha = r.choice([2, 2, 3])
    pats = set()
    for _ in range(r.randint(1, 5)):
        pats.add(tuple(r.randrange(alpha) for _ in range(r.randint(1, 4))))
    pats = [list(q) for q in sorted(pats)]
    if r.random() < 0.7:
        seq = []
        for _ in range(r.randint(1, 6)):
            seq += r.choice(pats)
        seq = seq[:12]
        if r.random() < 0.3:
            seq[r.randrange(len(seq))] = r.randrange(alpha)
    else:
        seq = [r.randrange(alpha) for _ in range(r.randint(1, 10))]
    return [seq, pats]


def _v_cuts(tests):
    for t in tests:
        seq, pats = t["args"]
        assert 1 <= len(seq) <= 5000 and all(0 <= x <= 1000 for x in seq)
        assert 1 <= len(pats) <= 300
        assert all(1 <= len(q) <= 10 and all(0 <= x <= 1000 for x in q) for q in pats)
        assert len({tuple(q) for q in pats}) == len(pats), "patterns not distinct"
    assert any(t["expected"] == 0 for t in tests) and any(t["expected"] > 1 for t in tests)


CHECKS["count-cuts-into-known-patterns"] = (_b_cuts, _g_cuts, "exact")
VALIDATE["count-cuts-into-known-patterns"] = _v_cuts


# ================================================================ 6. jobs into days (Medium)

p = add(
    id="jobs-into-days-min-total-peak", title="Jobs Into Days: Minimum Total Peak", diff="Medium", topic=TOPIC, tier="common",
    fn="minTotalPeak", params=[("jobs", "int[]"), ("d", "int")], ret="int", cmp="exact",
    desc="<p>The array <code>jobs</code> lists the difficulty of jobs that must be done <strong>in the given order</strong> over exactly <code>d</code> days. Every day you must do at least one job, and a day's jobs form a consecutive part of the list. The <em>peak</em> of a day is the largest difficulty among the jobs done that day.</p><p>Return the smallest possible sum of the <code>d</code> daily peaks, or <code>-1</code> if the jobs cannot be spread over <code>d</code> days (that is, there are fewer than <code>d</code> jobs).</p><pre>jobs = [1,4,2,3], d = 2  -> 5   (day 1: [1], day 2: [4,2,3] gives 1 + 4)\njobs = [3,3,3],   d = 3  -> 9   (one job per day)\njobs = [5,1],     d = 3  -> -1</pre>",
    constraints=["1 &le; jobs.length &le; 300", "0 &le; jobs[i] &le; 1,000", "1 &le; d &le; 10"],
    hints=["Think about the jobs of the last day. They are a suffix of the list. What is left for the first <code>d - 1</code> days?",
           "Let <code>dp[day][i]</code> be the best sum when the first <code>i</code> jobs are done in exactly <code>day</code> days. The last day of that prefix takes jobs <code>t .. i-1</code> and costs their maximum.",
           "<code>dp[day][i] = min over t of dp[day-1][t] + max(jobs[t..i-1])</code>, with <code>t &ge; day - 1</code> so that each earlier day gets at least one job. Move <code>t</code> downward from <code>i - 1</code> and keep a running maximum."],
    editorial=["Layer the DP by the number of days. <code>dp[0][0] = 0</code>, and <code>dp[day][i]</code> is the minimum total peak for splitting the first <code>i</code> jobs into exactly <code>day</code> non-empty consecutive groups. The last group is <code>jobs[t..i-1]</code>; it costs its maximum, and the first <code>t</code> jobs form a subproblem with one day less: <code>dp[day][i] = min(dp[day-1][t] + max(jobs[t..i-1]))</code>.",
               "Iterating <code>t</code> from <code>i - 1</code> down to <code>day - 1</code> lets us update the group maximum in O(1), so one cell costs O(n) and the whole table O(d &middot; n<sup>2</sup>) time. Only the previous layer is needed, so memory is O(n). If there are fewer jobs than days, the answer is -1 straight away."],
    time="O(d * n^2)", space="O(n)",
    solution='''def minTotalPeak(jobs, d):
    n = len(jobs)
    if n < d:
        return -1
    INF = 10 ** 9
    prev = [INF] * (n + 1)
    prev[0] = 0
    for day in range(1, d + 1):
        cur = [INF] * (n + 1)
        for i in range(day, n + 1):
            m = 0
            best = INF
            for t in range(i - 1, day - 2, -1):
                if jobs[t] > m:
                    m = jobs[t]
                v = prev[t] + m
                if v < best:
                    best = v
            cur[i] = best
        prev = cur
    return prev[n]
''',
    tests=[[[1, 4, 2, 3], 2], [[3, 3, 3], 3], [[5, 1], 3], [[7], 1], [[0, 0, 0], 2], [[6, 5, 4, 3, 2, 1], 2], [[1, 2, 3, 4, 5, 6], 3],
           [[9, 1, 1, 1, 9], 2], [[2, 7, 1, 8, 2, 8, 1, 8], 4], [[1000, 0, 1000], 1]],
)
_r = rnd(8206)
p["tests"].append([[_r.randint(0, 1000) for _ in range(300)], 10])
p["tests"].append([[_r.randint(0, 1000) for _ in range(300)], 3])
p["tests"].append([sorted((_r.randint(0, 1000) for _ in range(300)), reverse=True), 7])
p["tests"].append([[_r.randint(0, 1000) for _ in range(300)], 1])


def _b_peak(jobs, d):
    n = len(jobs)
    if n < d:
        return -1

    def go(i, left):
        if left == 1:
            return max(jobs[i:])
        best = None
        for j in range(i + 1, n - left + 2):
            v = max(jobs[i:j]) + go(j, left - 1)
            if best is None or v < best:
                best = v
        return best
    return go(0, d)


def _g_peak(r):
    n = r.randint(1, 9)
    return [[r.randint(0, 9) for _ in range(n)], r.randint(1, min(10, n + 1))]


def _v_peak(tests):
    for t in tests:
        jobs, d = t["args"]
        assert 1 <= len(jobs) <= 300 and all(0 <= x <= 1000 for x in jobs) and 1 <= d <= 10
    assert any(t["expected"] == -1 for t in tests)


CHECKS["jobs-into-days-min-total-peak"] = (_b_peak, _g_peak, "exact")
VALIDATE["jobs-into-days-min-total-peak"] = _v_peak


# ================================================================ 7. group remainders (Medium)

p = add(
    id="max-sum-of-group-remainders", title="Split Into K Groups, Maximize Remainders", diff="Medium", topic=TOPIC, tier="extra",
    fn="maxRemainderScore", params=[("nums", "int[]"), ("k", "int"), ("p", "int")], ret="int", cmp="exact",
    desc="<p>Cut the array <code>nums</code> into exactly <code>k</code> consecutive non-empty groups. The <em>score</em> of a group is the remainder of the sum of its elements when divided by <code>p</code>. Return the largest possible total score (the sum of the <code>k</code> group scores).</p><pre>nums = [3,5,7], k = 2, p = 10  -> 15   ([3,5] scores 8, [7] scores 7)\nnums = [4,6,5], k = 2, p = 5   -> 5    ([4] scores 4, [6,5] has sum 11 and scores 1)</pre>",
    constraints=["1 &le; k &le; nums.length &le; 1,000", "k &le; 10", "2 &le; p &le; 50", "1 &le; nums[i] &le; 1,000,000"],
    hints=["Work with prefix sums reduced modulo <code>p</code>. A group that spans positions <code>t .. i-1</code> scores <code>(pre[i] - pre[t]) mod p</code>.",
           "Let <code>dp[j][i]</code> be the best total score for the first <code>i</code> elements cut into <code>j</code> groups. The last group starts at some <code>t</code>, so you maximize <code>dp[j-1][t] + (pre[i] - pre[t]) mod p</code> over <code>t</code>. Trying every <code>t</code> is too slow.",
           "The only thing about <code>t</code> that matters besides <code>dp[j-1][t]</code> is the residue <code>pre[t]</code>, and there are only <code>p</code> residues. For each residue keep the best <code>dp[j-1][t]</code> seen so far, and for every <code>i</code> scan the <code>p</code> residues."],
    editorial=["Let <code>pre[i]</code> be the prefix sum of the first <code>i</code> elements modulo <code>p</code>. A group <code>t .. i-1</code> has score <code>(pre[i] - pre[t]) mod p</code>, so <code>dp[j][i] = max over t of dp[j-1][t] + (pre[i] - pre[t]) mod p</code>. A direct scan over <code>t</code> costs O(n<sup>2</sup> &middot; k).",
               "The score depends on <code>t</code> only through <code>pre[t]</code>, a value in <code>0..p-1</code>. So for each layer we keep an array <code>best[r]</code> holding the largest <code>dp[j-1][t]</code> among the starts <code>t</code> already seen with <code>pre[t] = r</code>. For a new end <code>i</code> we scan the <code>p</code> residues and take the maximum of <code>best[r] + (pre[i] - r) mod p</code>. The start <code>t = i - 1</code> is added to <code>best</code> just before processing <code>i</code>. Total time O(n &middot; k &middot; p), memory O(n)."],
    time="O(n * k * p)", space="O(n)",
    solution='''def maxRemainderScore(nums, k, p):
    n = len(nums)
    pre = [0] * (n + 1)
    for i, x in enumerate(nums):
        pre[i + 1] = (pre[i] + x) % p
    prev = [-1] * (n + 1)
    prev[0] = 0
    for j in range(1, k + 1):
        cur = [-1] * (n + 1)
        best = [-1] * p
        for i in range(j, n + 1):
            t = i - 1
            if prev[t] > best[pre[t]]:
                best[pre[t]] = prev[t]
            c = pre[i]
            m = -1
            for r in range(p):
                b = best[r]
                if b >= 0:
                    v = b + (c - r) % p
                    if v > m:
                        m = v
            cur[i] = m
        prev = cur
    return prev[n]
''',
    tests=[[[3, 5, 7], 2, 10], [[4, 6, 5], 2, 5], [[7], 1, 4], [[1, 1, 1], 3, 2], [[1, 1, 1], 1, 2], [[2, 2, 2, 2], 2, 4],
           [[9, 8, 7, 6, 5, 4], 3, 11], [[10, 10, 10], 2, 10], [[1, 2, 3, 4, 5, 6, 7], 4, 9], [[1000000, 999999, 5], 2, 50]],
)
_r = rnd(8207)
p["tests"].append([[_r.randint(1, 1000000) for _ in range(1000)], 10, 50])
p["tests"].append([[_r.randint(1, 1000000) for _ in range(1000)], 4, 47])
p["tests"].append([[_r.randint(1, 20) for _ in range(1000)], 10, 7])
p["tests"].append([[_r.randint(1, 1000000) for _ in range(10)], 10, 13])


def _b_remainders(nums, k, p):
    n = len(nums)
    best = -1
    for cuts in combinations(range(1, n), k - 1):
        bounds = (0,) + cuts + (n,)
        total = sum(sum(nums[bounds[g]:bounds[g + 1]]) % p for g in range(k))
        best = max(best, total)
    return best


def _g_remainders(r):
    n = r.randint(1, 9)
    return [[r.randint(1, 30) for _ in range(n)], r.randint(1, min(n, 4)), r.randint(2, 9)]


def _v_remainders(tests):
    for t in tests:
        nums, k, pp = t["args"]
        assert 1 <= k <= len(nums) <= 1000 and k <= 10 and 2 <= pp <= 50
        assert all(1 <= x <= 1000000 for x in nums)


CHECKS["max-sum-of-group-remainders"] = (_b_remainders, _g_remainders, "exact")
VALIDATE["max-sum-of-group-remainders"] = _v_remainders


# ================================================================ 8. capped-sum splits (Medium)

p = add(
    id="count-splits-with-capped-block-sums", title="Count Cuttings With Capped Block Sums", diff="Medium", topic=TOPIC, tier="common",
    fn="countCappedSplits", params=[("nums", "int[]"), ("cap", "int")], ret="int", cmp="exact",
    desc="<p>Cut the array <code>nums</code> of positive integers into consecutive non-empty blocks so that <strong>the sum of every block is at most <code>cap</code></strong>. Return the number of different ways to do this, modulo <code>1,000,000,007</code>. Two ways are different if they place a cut at different positions.</p><pre>nums = [1,2,1], cap = 3  -> 3   (1|2|1, 1,2|1, 1|2,1; the whole array has sum 4)\nnums = [5,1],   cap = 4  -> 0   (the element 5 can never fit)\nnums = [1,1,1], cap = 9  -> 4   (any cut positions: 2^2 ways)</pre>",
    constraints=["1 &le; nums.length &le; 8,000", "1 &le; nums[i] &le; 10,000", "1 &le; cap &le; 100,000,000"],
    hints=["Consider the last block of a prefix. For a prefix of length <code>i</code>, which starting points <code>j</code> give a legal last block <code>nums[j..i-1]</code>?",
           "Let <code>ways[i]</code> be the number of cuttings of the first <code>i</code> elements, <code>ways[0] = 1</code>. Then <code>ways[i]</code> is the sum of <code>ways[j]</code> over all <code>j &lt; i</code> with <code>prefix[i] - prefix[j] &le; cap</code>. Adding them one by one is O(n<sup>2</sup>).",
           "All numbers are positive, so the legal <code>j</code> form a contiguous range <code>lo .. i-1</code> and <code>lo</code> never moves backwards when <code>i</code> grows. Keep the sum of <code>ways[lo..i-1]</code> in a sliding window."],
    editorial=["With prefix sums <code>pre</code>, the block <code>nums[j..i-1]</code> has sum <code>pre[i] - pre[j]</code>. Then <code>ways[i] = sum of ways[j]</code> over all <code>j &lt; i</code> such that this sum is at most <code>cap</code>. Because all values are positive, <code>pre</code> is strictly increasing, so the valid <code>j</code> are exactly <code>lo .. i-1</code> for a start <code>lo</code> that only moves right as <code>i</code> increases.",
               "Maintain <code>S = ways[lo] + ... + ways[i-1]</code> (modulo 1,000,000,007). When moving to <code>i</code>, add <code>ways[i-1]</code>, then advance <code>lo</code> while the block is too heavy, subtracting <code>ways[lo]</code> as it leaves the window. Then <code>ways[i] = S</code>. This is the sliding-window prefix-sum optimisation of a DP, giving O(n) time and O(n) memory. If some single element exceeds <code>cap</code> the window becomes empty and the answer is 0."],
    time="O(n)", space="O(n)",
    solution='''def countCappedSplits(nums, cap):
    M = 1000000007
    n = len(nums)
    pre = [0] * (n + 1)
    for i, x in enumerate(nums):
        pre[i + 1] = pre[i] + x
    ways = [0] * (n + 1)
    ways[0] = 1
    S = 1
    lo = 0
    for i in range(1, n + 1):
        while lo < i and pre[i] - pre[lo] > cap:
            S -= ways[lo]
            lo += 1
        ways[i] = S % M
        S = (S + ways[i]) % M
    return ways[n]
''',
    tests=[[[1, 2, 1], 3], [[5, 1], 4], [[1, 1, 1], 9], [[7], 7], [[7], 6], [[2, 2, 2, 2], 4], [[3, 1, 4, 1, 5, 9, 2, 6], 10],
           [[1, 1, 1, 1, 1], 2], [[10, 10, 10], 100], [[4, 4, 4, 4], 3]],
)
_r = rnd(8208)
p["tests"].append([[_r.randint(1, 10) for _ in range(8000)], 40])
p["tests"].append([[_r.randint(1, 10000) for _ in range(8000)], 100000000])
p["tests"].append([[_r.randint(1, 3) for _ in range(8000)], 12])
p["tests"].append([[_r.randint(1, 9) for _ in range(7999)] + [10000], 9999])


def _b_capped(nums, cap):
    n = len(nums)
    total = 0
    for mask in range(1 << (n - 1)):
        s = nums[0]
        ok = True
        for i in range(1, n):
            if (mask >> (i - 1)) & 1:
                s = nums[i]
            else:
                s += nums[i]
            if s > cap:
                ok = False
                break
        if ok and nums[0] <= cap:
            total += 1
    return total % MOD


def _g_capped(r):
    n = r.randint(1, 11)
    nums = [r.randint(1, 6) for _ in range(n)]
    return [nums, r.randint(1, 20)]


def _v_capped(tests):
    for t in tests:
        nums, cap = t["args"]
        assert 1 <= len(nums) <= 8000 and all(1 <= x <= 10000 for x in nums) and 1 <= cap <= 10 ** 8
    assert any(t["expected"] == 0 for t in tests) and any(t["expected"] > 1 for t in tests)


CHECKS["count-splits-with-capped-block-sums"] = (_b_capped, _g_capped, "exact")
VALIDATE["count-splits-with-capped-block-sums"] = _v_capped


# ================================================================ 9. split with trimmed cost (Hard)

p = add(
    id="split-array-min-repeat-penalty", title="Split Array With Repeat Penalty", diff="Hard", topic=TOPIC, tier="extra",
    fn="minSplitPenalty", params=[("nums", "int[]"), ("k", "int")], ret="int", cmp="exact",
    desc="<p>Cut <code>nums</code> into any number (at least one) of consecutive non-empty blocks. The penalty of a block is <code>k + r</code>, where <code>r</code> is the number of positions in the block whose value <strong>occurs at least twice inside that block</strong>. For example, the block <code>[4,7,4,4,9]</code> has <code>r = 3</code> because the three 4s are repeated, while 7 and 9 occur only once.</p><p>Return the smallest possible sum of the penalties of all blocks.</p><pre>nums = [1,2,1,2,1], k = 2  -> 6   (blocks [1,2], [1,2], [1]: three blocks, no repeats)\nnums = [5,5,5],     k = 10 -> 13  (one block: 10 + 3; splitting adds more than it saves)</pre>",
    constraints=["1 &le; nums.length &le; 800", "0 &le; nums[i] &le; 1,000,000", "1 &le; k &le; 10,000"],
    hints=["Each block you open costs <code>k</code> up front, but a long block gets more repeated values. Think of dp over prefixes, and about the last block.",
           "Let <code>dp[e]</code> be the best total for the first <code>e</code> elements. For every start <code>s</code> of the last block, the cost is <code>k + r(s, e)</code>. Computing <code>r</code> from scratch for each pair is too slow.",
           "Fix the start <code>s</code> and extend the block one element at a time with a counter of occurrences. When a value's count goes from 1 to 2, <code>r</code> grows by 2 (both copies now count); when it goes from 2 or more upward, <code>r</code> grows by 1. Relax <code>dp[e + 1]</code> with <code>dp[s] + k + r</code> at every step."],
    editorial=["Let <code>dp[e]</code> be the minimum penalty for the first <code>e</code> elements, <code>dp[0] = 0</code>. The last block is <code>nums[s..e-1]</code> and costs <code>k + r(s, e)</code>, so <code>dp[e] = min(dp[s] + k + r(s, e))</code>. We need <code>r(s, e)</code> for all O(n<sup>2</sup>) pairs.",
               "Process the starts in increasing order (when <code>s</code> is processed, <code>dp[s]</code> is final) and for each start sweep <code>e</code> to the right with a fresh occurrence counter. Adding a value whose count was 0 leaves <code>r</code> unchanged; going from 1 to 2 adds 2 (the old copy and the new one now count); going from 2 or more adds 1. After each extension, relax <code>dp[e+1]</code>. The result is O(n<sup>2</sup>) time and O(n) memory. For n up to 800 this is about 320,000 steps."],
    time="O(n^2)", space="O(n)",
    solution='''def minSplitPenalty(nums, k):
    n = len(nums)
    INF = 10 ** 18
    dp = [INF] * (n + 1)
    dp[0] = 0
    for s in range(n):
        base = dp[s] + k
        cnt = {}
        r = 0
        for e in range(s, n):
            x = nums[e]
            c = cnt.get(x, 0)
            if c == 1:
                r += 2
            elif c >= 2:
                r += 1
            cnt[x] = c + 1
            v = base + r
            if v < dp[e + 1]:
                dp[e + 1] = v
    return dp[n]
''',
    tests=[[[1, 2, 1, 2, 1], 2], [[5, 5, 5], 10], [[7], 3], [[1, 1], 1], [[1, 1], 5], [[1, 2, 3, 4], 1], [[1, 2, 3, 4], 100],
           [[3, 3, 3, 3, 3, 3], 2], [[1, 2, 1, 3, 2, 3, 1, 2], 3], [[0, 1000000, 0, 1000000], 2]],
)
_r = rnd(8209)
p["tests"].append([[_r.randint(0, 30) for _ in range(800)], 5])
p["tests"].append([[_r.randint(0, 400) for _ in range(800)], 20])
p["tests"].append([[_r.randint(0, 3) for _ in range(800)], 1])
p["tests"].append([[_r.randint(0, 1000000) for _ in range(800)], 10000])


def _b_penalty(nums, k):
    from collections import Counter
    n = len(nums)

    def pen(block):
        c = Counter(block)
        return k + sum(v for v in c.values() if v >= 2)

    def go(i):
        if i == n:
            return 0
        return min(pen(nums[i:j]) + go(j) for j in range(i + 1, n + 1))
    return go(0)


def _g_penalty(r):
    n = r.randint(1, 9)
    return [[r.randint(0, 3) for _ in range(n)], r.randint(1, 5)]


def _v_penalty(tests):
    for t in tests:
        nums, k = t["args"]
        assert 1 <= len(nums) <= 800 and all(0 <= x <= 1000000 for x in nums) and 1 <= k <= 10000


CHECKS["split-array-min-repeat-penalty"] = (_b_penalty, _g_penalty, "exact")
VALIDATE["split-array-min-repeat-penalty"] = _v_penalty


# ================================================================ 10. mailbox allocation (Hard)

p = add(
    id="mailbox-allocation-min-distance", title="Place K Mailboxes", diff="Hard", topic=TOPIC, tier="extra",
    fn="minTotalDistance", params=[("houses", "int[]"), ("k", "int")], ret="int", cmp="exact",
    desc="<p>Houses stand on a straight street; <code>houses[i]</code> is the position of house <code>i</code> (the positions are in no particular order and may repeat). You may place exactly <code>k</code> mailboxes at integer positions of your choice. Every house walks to the closest mailbox. Return the smallest possible sum of all these walking distances.</p><pre>houses = [1,4,8,10,20], k = 3  -> 5   (mailboxes at 4, 9, 20: distances 3 + 1 + 1 + 0)\nhouses = [2,3,5,12,18], k = 2  -> 9   (mailboxes at 3 and 12: distances 1 + 0 + 2 + 0 + 6)\nhouses = [7,7,7],       k = 1  -> 0</pre>",
    constraints=["1 &le; k &le; houses.length &le; 150", "k &le; 30", "0 &le; houses[i] &le; 100,000"],
    hints=["After sorting the houses, the houses served by one mailbox form a consecutive group. So you are cutting the sorted list into <code>k</code> consecutive groups.",
           "For one group, the best mailbox position is the median house of the group. Precompute <code>cost[i][j]</code>, the total distance when houses <code>i..j</code> share one mailbox, using prefix sums.",
           "Let <code>dp[g][i]</code> be the best cost for the first <code>i</code> sorted houses using <code>g</code> mailboxes: <code>dp[g][i] = min over t of dp[g-1][t] + cost[t][i-1]</code>."],
    editorial=["Sort the houses. Whenever two mailboxes exist, each house prefers the nearer one, and that makes the houses of one mailbox a contiguous block of the sorted order. So the task is to cut the sorted list into <code>k</code> blocks and to pay, for each block, the cost of the best single mailbox.",
               "For a block, the sum of absolute distances is minimized at the median house (any point between the two middle houses works for even sizes). With prefix sums <code>P</code> of the sorted positions and median index <code>m = (i + j) / 2</code>, the cost is <code>a[m]*(m-i) - (P[m]-P[i]) + (P[j+1]-P[m+1]) - a[m]*(j-m)</code>, available in O(1) after O(n) preparation, giving the table <code>cost[i][j]</code> in O(n<sup>2</sup>). The DP <code>dp[g][i] = min(dp[g-1][t] + cost[t][i-1])</code> then takes O(k &middot; n<sup>2</sup>) time. For the answer, only integer positions are needed, and the median is always a house position, so integer placement loses nothing."],
    time="O(n^2 * k)", space="O(n^2)",
    solution='''def minTotalDistance(houses, k):
    a = sorted(houses)
    n = len(a)
    P = [0] * (n + 1)
    for i, x in enumerate(a):
        P[i + 1] = P[i] + x
    C = [[0] * n for _ in range(n)]
    for i in range(n):
        for j in range(i, n):
            m = (i + j) // 2
            C[i][j] = a[m] * (m - i) - (P[m] - P[i]) + (P[j + 1] - P[m + 1]) - a[m] * (j - m)
    INF = 10 ** 18
    prev = [INF] * (n + 1)
    prev[0] = 0
    for g in range(1, k + 1):
        cur = [INF] * (n + 1)
        for i in range(g, n + 1):
            best = INF
            for t in range(g - 1, i):
                v = prev[t] + C[t][i - 1]
                if v < best:
                    best = v
            cur[i] = best
        prev = cur
    return prev[n]
''',
    tests=[[[1, 4, 8, 10, 20], 3], [[2, 3, 5, 12, 18], 2], [[7, 7, 7], 1], [[5], 1], [[1, 100000], 1], [[1, 100000], 2], [[3, 1, 2], 3],
           [[1, 2, 3, 4, 5, 6], 1], [[10, 0, 10, 0, 5], 2], [[1, 2, 3, 50, 51, 52, 100, 101], 3]],
)
_r = rnd(8210)
p["tests"].append([[_r.randint(0, 100000) for _ in range(150)], 30])
p["tests"].append([[_r.randint(0, 100000) for _ in range(150)], 7])
p["tests"].append([[_r.randint(0, 100000) for _ in range(150)], 1])
p["tests"].append([[_r.randint(0, 1000) for _ in range(120)], 29])


def _b_mailbox(houses, k):
    lo, hi = min(houses), max(houses)
    best = None
    for boxes in combinations_with_replacement(range(lo, hi + 1), k):
        v = sum(min(abs(h - b) for b in boxes) for h in houses)
        if best is None or v < best:
            best = v
    return best


def _g_mailbox(r):
    n = r.randint(1, 7)
    return [[r.randint(0, 12) for _ in range(n)], r.randint(1, min(n, 4))]


def _v_mailbox(tests):
    for t in tests:
        h, k = t["args"]
        assert 1 <= k <= len(h) <= 150 and k <= 30 and all(0 <= x <= 100000 for x in h)


CHECKS["mailbox-allocation-min-distance"] = (_b_mailbox, _g_mailbox, "exact")
VALIDATE["mailbox-allocation-min-distance"] = _v_mailbox


# ================================================================ 11. decode with wildcards (Hard)

p = add(
    id="decode-ways-with-wildcards", title="Decode Ways With Wildcards", diff="Hard", topic=TOPIC, tier="extra",
    fn="countDecodingsWild", params=[("symbols", "int[]")], ret="int", cmp="exact",
    desc="<p>A message is encoded with the rule <code>1 -> A, 2 -> B, ..., 26 -> Z</code>. The encoded text is given as an array <code>symbols</code>. Each entry is either a digit <code>0</code>..<code>9</code>, or <code>-1</code>, a <em>wildcard</em> that stands for <strong>any one digit from 1 to 9</strong> (a wildcard is never 0).</p><p>A <em>decoding</em> chooses a digit for every wildcard and then cuts the digits into pieces of one or two digits, where every piece is a number from 1 to 26 without a leading zero (so <code>6</code>, <code>12</code>, <code>26</code> are valid; <code>0</code>, <code>06</code>, <code>27</code> are not). Count the decodings, where two decodings are different if they choose different digits for some wildcard or cut at different places. Return the count modulo <code>1,000,000,007</code>.</p><pre>symbols = [-1]      -> 9    (the digit can be 1..9, each decodes as one letter)\nsymbols = [1,-1]    -> 18   (digits 11..19: 9 two-digit readings plus 9 one-by-one readings)\nsymbols = [-1,-1]   -> 96\nsymbols = [0]       -> 0</pre>",
    constraints=["1 &le; symbols.length &le; 8,000", "symbols[i] is -1 or a digit from 0 to 9"],
    hints=["Without wildcards this is the classic Decode Ways with a prefix DP: the last piece is one digit or two digits. Keep that skeleton.",
           "Let <code>dp[i]</code> be the number of decodings of the first <code>i</code> symbols. Then <code>dp[i] = dp[i-1] * one(s[i-1]) + dp[i-2] * two(s[i-2], s[i-1])</code>, where <code>one</code> and <code>two</code> count how many digit choices make the piece valid.",
           "<code>one(x)</code>: 9 for a wildcard, 0 for the digit 0, otherwise 1. <code>two(a, b)</code>: for two wildcards 15 (11..19 and 21..26); for wildcard then digit b, 2 choices (a = 1 or 2) when b &le; 6, else 1; for digit then wildcard, 9 if a = 1, 6 if a = 2, else 0; for two digits, 1 if the number is 10..26, else 0."],
    editorial=["The skeleton is the standard prefix DP: the last piece of the first <code>i</code> symbols is either the single symbol <code>s[i-1]</code> or the pair <code>s[i-2], s[i-1]</code>, so <code>dp[i] = dp[i-1] * one + dp[i-2] * two</code>. The new part is that a piece can stand for several digit strings, and each valid substitution multiplies the number of decodings. Because the pieces of a cutting use disjoint wildcards, the counts multiply.",
               "<code>one(x)</code> is 9 for a wildcard (1..9), 0 for the digit 0, and 1 for a digit 1..9. <code>two(a, b)</code> counts the two-digit values 10..26: both wildcards give 11..19 and 21..26, which is 15 (10 and 20 are excluded because a wildcard is never 0). Wildcard first then a digit <code>b</code>: the first digit may be 1 (always valid) or 2 (valid when <code>b</code> &le; 6), so 2 or 1. Digit <code>a</code> then wildcard: 9 for <code>a = 1</code> (11..19), 6 for <code>a = 2</code> (21..26), otherwise 0. Two plain digits give 1 for 10..26 and 0 otherwise (this also rejects a leading 0). Using only the last two values makes it O(n) time and O(1) space, always reducing modulo 1,000,000,007."],
    time="O(n)", space="O(1)",
    solution='''def countDecodingsWild(symbols):
    M = 1000000007

    def one(x):
        if x == -1:
            return 9
        return 0 if x == 0 else 1

    def two(a, b):
        if a == -1 and b == -1:
            return 15
        if a == -1:
            return 2 if b <= 6 else 1
        if b == -1:
            if a == 1:
                return 9
            if a == 2:
                return 6
            return 0
        return 1 if 10 <= a * 10 + b <= 26 else 0

    p2, p1 = 0, 1       # dp[i-2], dp[i-1]; dp[0] = 1
    for i, x in enumerate(symbols):
        cur = p1 * one(x)
        if i >= 1:
            cur += p2 * two(symbols[i - 1], x)
        p2, p1 = p1, cur % M
    return p1
''',
    tests=[[[-1]], [[1, -1]], [[-1, -1]], [[0]], [[1, 2, 6]], [[2, 7]], [[-1, 0]], [[0, -1]], [[3, -1, 6, 0, -1]],
           [[-1, 7, -1, -1, 5]], [[1, 0, 2, 0]], [[2, -1, -1, 1]]],
)
_r = rnd(8211)


def _wild_seq(r, n, pwild, pzero):
    out = []
    for _ in range(n):
        u = r.random()
        if u < pwild:
            out.append(-1)
        elif u < pwild + pzero:
            out.append(0)
        else:
            out.append(r.randint(1, 9))
    return out


p["tests"].append([_wild_seq(_r, 8000, 0.5, 0.0)])
p["tests"].append([_wild_seq(_r, 8000, 0.15, 0.03)])
p["tests"].append([[-1] * 8000])
p["tests"].append([[_r.choice([1, 2]) for _ in range(8000)]])


def _b_wild(symbols):
    wild = [i for i, x in enumerate(symbols) if x == -1]
    n = len(symbols)
    total = 0
    for fill in range(9 ** len(wild)):
        digits = list(symbols)
        f = fill
        for i in wild:
            digits[i] = f % 9 + 1
            f //= 9

        def go(i):
            if i == n:
                return 1
            if digits[i] == 0:
                return 0
            res = go(i + 1)
            if i + 1 < n and digits[i] * 10 + digits[i + 1] <= 26:
                res += go(i + 2)
            return res
        total += go(0)
    return total % MOD


def _g_wild(r):
    n = r.randint(1, 7)
    out = []
    wilds = 0
    for _ in range(n):
        if wilds < 3 and r.random() < 0.35:
            out.append(-1)
            wilds += 1
        else:
            out.append(r.choice([0, 1, 1, 2, 2, 3, 6, 7, 9]))
    return [out]


def _v_wild(tests):
    for t in tests:
        s = t["args"][0]
        assert 1 <= len(s) <= 8000 and all(x == -1 or 0 <= x <= 9 for x in s)
    assert any(t["expected"] == 0 for t in tests) and any(t["expected"] > 100 for t in tests)


CHECKS["decode-ways-with-wildcards"] = (_b_wild, _g_wild, "exact")
VALIDATE["decode-ways-with-wildcards"] = _v_wild
