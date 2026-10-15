"""Problems: Dynamic Programming, the longest common subsequence family. See data/lib.py for the registry."""
from itertools import combinations, product
from collections import Counter

from lib import add, rnd, CHECKS, VALIDATE, gen_arr  # noqa: F401

MOD = 10 ** 9 + 7
LOW = "abcdefghijklmnopqrstuvwxyz"


def _rs(r, alpha, lo, hi):
    return "".join(r.choice(alpha) for _ in range(r.randint(lo, hi)))


def _ra(r, lo, hi, vlo, vhi):
    return [r.randint(vlo, vhi) for _ in range(r.randint(lo, hi))]


def _is_sub(w, s):
    it = iter(s)
    return all(c in it for c in w)


def _subseqs(s):
    out = set()
    n = len(s)
    for mask in range(1 << n):
        out.add("".join(s[i] for i in range(n) if mask >> i & 1))
    return out


def _check_strings(tests, limit, alpha=LOW):
    for t in tests:
        for x in t["args"][:2]:
            assert isinstance(x, str) and len(x) <= limit
            assert all(c in alpha for c in x)


# ---------------------------------------------------------------- EASY

p = add(
    id="shortest-common-supersequence-length", title="Shortest Common Supersequence Length", diff="Easy", topic="Dynamic Programming",
    fn="shortestSupersequenceLength", params=[("a", "string"), ("b", "string")], ret="int", cmp="exact",
    desc="<p>A string <code>w</code> is a <em>supersequence</em> of a string <code>x</code> if <code>x</code> can be obtained from <code>w</code> by deleting some characters (possibly none) without reordering the rest. Equivalently, <code>x</code> is a subsequence of <code>w</code>.</p><p>Given strings <code>a</code> and <code>b</code>, return the length of the shortest string that is a supersequence of <b>both</b>.</p><pre>a = \"abac\", b = \"cab\"  ->  5   (\"cabac\" contains both)\na = \"geek\", b = \"eke\"  ->  5   (\"geeke\")\na = \"abc\",  b = \"xyz\"  ->  6</pre>",
    constraints=["0 &le; a.length, b.length &le; 600", "Both strings contain only lowercase English letters"],
    hints=["Writing a and b one after the other always gives a valid answer of length a.length + b.length. When can you do better?",
           "You save one character every time a character of a and a character of b can be written as the <em>same</em> character of the result. Which characters can be shared in this way?",
           "The shared characters form a common subsequence of a and b (their relative order must be preserved in both strings). Share as many as possible: the answer is <code>len(a) + len(b) - LCS(a, b)</code>."],
    editorial=["Build a supersequence by merging a and b like a zip: at every step write a character that advances a, b, or both. Writing a character that advances both is only possible when the two next characters are equal. Every such shared step saves one character compared to plain concatenation. The characters that are shared, read in order, form a string that is a subsequence of a and of b.",
               "Conversely, any common subsequence of length <code>k</code> can be turned into a supersequence of length <code>len(a) + len(b) - k</code>: write the pieces of a and b that lie between consecutive matched characters, then the matched character once. So the shortest supersequence has length <code>len(a) + len(b) - L</code> where <code>L</code> is the length of the longest common subsequence.",
               "Compute L with the usual table, <code>dp[i][j] = dp[i-1][j-1] + 1</code> on a match and <code>max(dp[i-1][j], dp[i][j-1])</code> otherwise, keeping only the previous row."],
    time="O(m &middot; n)", space="O(n)",
    solution='''def shortestSupersequenceLength(a, b):
    m, n = len(a), len(b)
    prev = [0] * (n + 1)
    for i in range(1, m + 1):
        cur = [0] * (n + 1)
        c = a[i - 1]
        for j in range(1, n + 1):
            if c == b[j - 1]:
                cur[j] = prev[j - 1] + 1
            else:
                cur[j] = cur[j - 1] if cur[j - 1] > prev[j] else prev[j]
        prev = cur
    return m + n - prev[n]
''',
    tests=[["abac", "cab"], ["geek", "eke"], ["abc", "xyz"], ["", ""], ["abc", ""], ["", "abcd"], ["a", "a"], ["a", "b"],
           ["abcde", "abcde"], ["aaaa", "aa"], ["abcbdab", "bdcaba"], ["zzzz", "zazaz"]],
    tier="common",
)
_r = rnd(11001)
p["tests"] += [
    [_rs(_r, "abcd", 600, 600), _rs(_r, "abcd", 600, 600)],
    [_rs(_r, LOW, 600, 600), _rs(_r, LOW, 500, 500)],
    ["a" * 600, "a" * 500],
    ["ab" * 300, "ba" * 300],
]


def _b_scs_len(a, b):
    letters = sorted(set(a + b))
    for L in range(max(len(a), len(b)), len(a) + len(b) + 1):
        for w in product(letters, repeat=L):
            if _is_sub(a, w) and _is_sub(b, w):
                return L


def _v_scs_len(tests):
    _check_strings(tests, 600)


CHECKS["shortest-common-supersequence-length"] = (
    _b_scs_len, lambda r: [_rs(r, "abc", 0, 4), _rs(r, "abc", 0, 4)], "exact")
VALIDATE["shortest-common-supersequence-length"] = _v_scs_len


p = add(
    id="count-matching-substring-pairs", title="Count Matching Substring Pairs", diff="Easy", topic="Dynamic Programming",
    fn="countMatchingSubstrings", params=[("s", "string"), ("t", "string")], ret="int", cmp="exact",
    desc="<p>A <em>match</em> is a triple <code>(i, j, len)</code> with <code>len &ge; 1</code> such that the substring of <code>s</code> that starts at index <code>i</code> and has length <code>len</code> is equal to the substring of <code>t</code> that starts at index <code>j</code> and has the same length. Different triples count as different matches even when they spell the same text.</p><p>Return the total number of matches.</p><pre>s = \"aab\", t = \"ab\"   ->  4   (\"a\" at s[0] and s[1] vs t[0], \"b\" vs t[1], and \"ab\" at s[1] vs t[0])\ns = \"aaa\", t = \"aa\"   ->  8   (6 pairs of single letters + 2 pairs of \"aa\")</pre>",
    constraints=["0 &le; s.length, t.length &le; 600", "Both strings contain only lowercase English letters", "The answer is below 2<sup>31</sup> for every allowed input"],
    hints=["Checking every triple by comparing the substrings is far too slow. Fix the <em>end</em> of the two substrings instead of their start.",
           "Let E(i, j) be the number of matches whose substrings end at <code>s[i]</code> and <code>t[j]</code>. If <code>s[i] != t[j]</code> there are none.",
           "If the characters are equal, a match ending here is either the single letter pair, or a match ending at <code>(i-1, j-1)</code> extended by one. So <code>E(i, j) = E(i-1, j-1) + 1</code>, and the answer is the sum of all E values."],
    editorial=["Group the matches by where the two substrings end. A match ending at positions (i, j) requires <code>s[i] == t[j]</code>. Its length is 1, or it is a match ending at (i-1, j-1) with one more equal character appended. Hence <code>E[i][j] = E[i-1][j-1] + 1</code> when the characters are equal and <code>0</code> otherwise, and every match is counted exactly once at its end pair.",
               "The longest common substring problem uses the same table but takes the maximum; here every cell contributes to a sum. Only the previous row is needed, so the memory is O(t.length). The total fits in 32 bits for the stated limits (the worst case is two strings of one repeated letter, about n<sup>3</sup>/3)."],
    time="O(m &middot; n)", space="O(n)",
    solution='''def countMatchingSubstrings(s, t):
    n = len(t)
    prev = [0] * (n + 1)
    total = 0
    for i in range(len(s)):
        cur = [0] * (n + 1)
        c = s[i]
        for j in range(n):
            if c == t[j]:
                v = prev[j] + 1
                cur[j + 1] = v
                total += v
        prev = cur
    return total
''',
    tests=[["aab", "ab"], ["aaa", "aa"], ["", ""], ["abc", ""], ["", "abc"], ["a", "a"], ["a", "b"], ["abc", "abc"],
           ["abab", "baba"], ["abcabc", "bca"], ["zzzz", "zz"], ["abcdefg", "gfedcba"]],
    tier="extra",
)
_r = rnd(11002)
p["tests"] += [
    [_rs(_r, "ab", 600, 600), _rs(_r, "ab", 600, 600)],
    [_rs(_r, LOW, 600, 600), _rs(_r, "abcdefgh", 600, 600)],
    ["a" * 600, "a" * 600],
    ["ab" * 300, "ab" * 290],
]


def _b_cmsp(s, t):
    cnt = 0
    for i in range(len(s)):
        for j in range(len(t)):
            ln = 1
            while i + ln <= len(s) and j + ln <= len(t) and s[i:i + ln] == t[j:j + ln]:
                cnt += 1
                ln += 1
    return cnt


def _v_cmsp(tests):
    _check_strings(tests, 600)


CHECKS["count-matching-substring-pairs"] = (
    _b_cmsp, lambda r: [_rs(r, "abc", 0, 9), _rs(r, "abc", 0, 9)], "exact")
VALIDATE["count-matching-substring-pairs"] = _v_cmsp


# ---------------------------------------------------------------- MEDIUM

p = add(
    id="uncrossed-lines-between-arrays", title="Uncrossed Lines", diff="Medium", topic="Dynamic Programming",
    fn="maxUncrossedLines", params=[("top", "int[]"), ("bottom", "int[]")], ret="int", cmp="exact",
    desc="<p>The numbers of <code>top</code> are written in order along an upper row and the numbers of <code>bottom</code> in order along a lower row. You may draw straight line segments, each joining one number of the upper row to an <b>equal</b> number of the lower row.</p><p>No number may be an endpoint of more than one segment, and no two segments may cross each other (segments that would meet at a shared endpoint are not allowed anyway). Return the maximum number of segments you can draw.</p><pre>top = [1, 4, 2], bottom = [1, 2, 4]  ->  2   (join 1-1 and either 4-4 or 2-2, not both)\ntop = [2, 5, 1, 2, 5], bottom = [10, 5, 2, 1, 5, 2]  ->  3</pre>",
    constraints=["0 &le; top.length, bottom.length &le; 800", "1 &le; top[i], bottom[j] &le; 2,000"],
    hints=["Two segments (i1, j1) and (i2, j2) do not cross exactly when <code>i1 &lt; i2</code> and <code>j1 &lt; j2</code>, or the reverse. What kind of structure is a set of pairwise non-crossing segments?",
           "Read the chosen pairs from left to right: the upper indices increase, the lower indices increase, and the values are equal. So the values form a sequence that is a subsequence of both arrays.",
           "The task is the longest common subsequence of the two arrays. Use <code>dp[i][j]</code> for the first i and first j numbers, extending diagonally on equal values and otherwise taking the larger neighbour."],
    editorial=["A segment joins position i of the top row to position j of the bottom row, and two segments avoid crossing exactly when their endpoints are ordered the same way on both rows. Sorting the segments by their upper endpoint therefore also sorts them by their lower endpoint. The values along the segments form a sequence that appears, in order, in both arrays, i.e. a common subsequence. Conversely, any common subsequence gives a valid set of non-crossing segments by matching the chosen positions in order.",
               "So the answer is the length of the longest common subsequence. Let <code>dp[i][j]</code> be that length for the prefixes of sizes i and j. If <code>top[i-1] == bottom[j-1]</code> we can add a segment between them: <code>dp[i][j] = dp[i-1][j-1] + 1</code>. Otherwise one of the two numbers is unused: <code>dp[i][j] = max(dp[i-1][j], dp[i][j-1])</code>. Only the previous row is needed, giving O(n) memory."],
    time="O(m &middot; n)", space="O(n)",
    solution='''def maxUncrossedLines(top, bottom):
    n = len(bottom)
    prev = [0] * (n + 1)
    for x in top:
        cur = [0] * (n + 1)
        for j in range(1, n + 1):
            if x == bottom[j - 1]:
                cur[j] = prev[j - 1] + 1
            else:
                cur[j] = cur[j - 1] if cur[j - 1] > prev[j] else prev[j]
        prev = cur
    return prev[n]
''',
    tests=[[[1, 4, 2], [1, 2, 4]], [[2, 5, 1, 2, 5], [10, 5, 2, 1, 5, 2]], [[1, 3, 7, 1, 7, 5], [1, 9, 2, 5, 1]], [[], []],
           [[1, 2, 3], []], [[], [4]], [[5], [5]], [[5], [6]], [[1, 2, 3], [3, 2, 1]], [[7, 7, 7], [7, 7]],
           [[1, 2, 1, 2], [2, 1, 2, 1]], [[2000, 1, 2000], [2000, 2000, 1, 1]]],
)
_r = rnd(11003)
p["tests"] += [
    [_ra(_r, 800, 800, 1, 4), _ra(_r, 800, 800, 1, 4)],
    [_ra(_r, 800, 800, 1, 30), _ra(_r, 700, 700, 1, 30)],
    [[1] * 800, [1] * 650],
]


def _b_uncrossed(a, b):
    best = 0
    for k in range(min(len(a), len(b)), 0, -1):
        for ia in combinations(range(len(a)), k):
            va = [a[i] for i in ia]
            if _is_sub(va, b):
                return k
    return best


def _v_uncrossed(tests):
    for t in tests:
        for x in t["args"]:
            assert len(x) <= 800 and all(1 <= v <= 2000 for v in x)


CHECKS["uncrossed-lines-between-arrays"] = (
    _b_uncrossed, lambda r: [_ra(r, 0, 7, 1, 3), _ra(r, 0, 7, 1, 3)], "exact")
VALIDATE["uncrossed-lines-between-arrays"] = _v_uncrossed


p = add(
    id="maximum-dot-product-of-subsequences", title="Maximum Dot Product of Subsequences", diff="Medium", topic="Dynamic Programming",
    fn="maxDotProduct", params=[("a", "int[]"), ("b", "int[]")], ret="int", cmp="exact",
    desc="<p>Choose a <b>non-empty</b> subsequence of <code>a</code> and a non-empty subsequence of <code>b</code> that have the <b>same length</b> <code>k</code>, and pair them up position by position. The score is the sum of the <code>k</code> products of the paired numbers (the dot product of the two subsequences).</p><p>Return the maximum score. Values may be negative, so the best score can itself be negative.</p><pre>a = [2, 1, -2, 5], b = [3, 0, -6]  ->  18   (2*3 + (-2)*(-6))\na = [3, -2], b = [2, -6, 7]        ->  21   (3*7)\na = [-1, -1], b = [1, 1]           ->  -1   (a non-empty choice is forced)</pre>",
    constraints=["1 &le; a.length, b.length &le; 600", "-1,000 &le; a[i], b[j] &le; 1,000"],
    hints=["Think of building the answer by looking at the last element of each array. Each of a[i] and b[j] is either used in the final pairing or left out.",
           "Let <code>dp[i][j]</code> be the best score using only the first i numbers of a and the first j numbers of b (with at least one pair). If both a[i] and b[j] are used, they are the last pair.",
           "<code>dp[i][j] = max(dp[i-1][j], dp[i][j-1], a[i]*b[j] + max(0, dp[i-1][j-1]))</code>. The <code>max(0, ...)</code> covers both 'no earlier pairs' and 'earlier pairs would only hurt'. Be careful to initialise the table so that an empty choice is never allowed."],
    editorial=["Let <code>dp[i][j]</code> be the maximum score for the prefixes a[0..i) and b[0..j) over non-empty equal-length subsequences, and treat it as minus infinity when a prefix is empty. Look at the last numbers x = a[i-1] and y = b[j-1]. Either x is not in the chosen subsequence (<code>dp[i-1][j]</code>), or y is not (<code>dp[i][j-1]</code>), or both are the last pair. In the last case the score is <code>x*y</code> plus the best score of the earlier pairs, which may be empty (add 0) or non-empty (add <code>dp[i-1][j-1]</code>); we pick whichever is larger, i.e. add <code>max(0, dp[i-1][j-1])</code>.",
               "This is the same table shape as the longest common subsequence, but a pair can be formed between <em>any</em> two numbers, not only equal ones, and the value being maximised is a sum of products. The answer is <code>dp[m][n]</code>. Because both subsequences must be non-empty, the all-negative case needs a real pair: with a = [-1, -1] and b = [1, 1] the answer is -1, not 0. The values stay below 600 * 10<sup>6</sup> in magnitude, so 32-bit integers suffice."],
    time="O(m &middot; n)", space="O(n)",
    solution='''def maxDotProduct(a, b):
    NEG = -(10 ** 18)
    n = len(b)
    prev = [NEG] * (n + 1)
    for x in a:
        cur = [NEG] * (n + 1)
        for j in range(1, n + 1):
            best = prev[j] if prev[j] > cur[j - 1] else cur[j - 1]
            gain = prev[j - 1]
            v = x * b[j - 1] + (gain if gain > 0 else 0)
            cur[j] = v if v > best else best
        prev = cur
    return prev[n]
''',
    tests=[[[2, 1, -2, 5], [3, 0, -6]], [[3, -2], [2, -6, 7]], [[-1, -1], [1, 1]], [[5], [4]], [[-5], [4]], [[0], [0]],
           [[1, 2, 3], [1, 2, 3]], [[-1, -2, -3], [4, 5, 6]], [[1000, -1000], [-1000, 1000]], [[3, 0, -3], [-3, 0, 3]],
           [[1, -1, 1, -1], [-1, 1, -1, 1]], [[7, -3, 2, 9, -8], [-2, 5]]],
)
_r = rnd(11004)
p["tests"] += [
    [_ra(_r, 600, 600, -1000, 1000), _ra(_r, 600, 600, -1000, 1000)],
    [_ra(_r, 600, 600, -1000, -1), _ra(_r, 500, 500, 1, 1000)],
    [[1000] * 600, [1000] * 600],
]


def _b_dot(a, b):
    best = None
    for k in range(1, min(len(a), len(b)) + 1):
        for ia in combinations(range(len(a)), k):
            for ib in combinations(range(len(b)), k):
                v = sum(a[i] * b[j] for i, j in zip(ia, ib))
                if best is None or v > best:
                    best = v
    return best


def _v_dot(tests):
    for t in tests:
        for x in t["args"]:
            assert 1 <= len(x) <= 600 and all(-1000 <= v <= 1000 for v in x)


CHECKS["maximum-dot-product-of-subsequences"] = (
    _b_dot, lambda r: [_ra(r, 1, 5, -4, 4), _ra(r, 1, 5, -4, 4)], "exact")
VALIDATE["maximum-dot-product-of-subsequences"] = _v_dot


p = add(
    id="longest-substring-that-is-subsequence-of-other", title="Longest Substring That Is a Subsequence of the Other String", diff="Medium", topic="Dynamic Programming",
    fn="longestEmbeddedSubstring", params=[("s", "string"), ("t", "string")], ret="int", cmp="exact",
    desc="<p>Find the longest <em>contiguous</em> block of <code>s</code> (a substring) that appears in <code>t</code> as a <em>subsequence</em>: its characters occur in <code>t</code> in the same order, but not necessarily next to each other.</p><p>Return the length of that block. It is <code>0</code> if no single character of <code>s</code> occurs in <code>t</code> (or if either string is empty).</p><pre>s = \"abcab\",  t = \"xaybzc\"  ->  3   (\"abc\" sits in t as x[a]y[b]z[c])\ns = \"abcde\",  t = \"aebdc\"   ->  3   (\"abc\")\ns = \"abab\",   t = \"bbaa\"    ->  2   (\"ba\")</pre>",
    constraints=["0 &le; s.length, t.length &le; 800", "Both strings contain only lowercase English letters"],
    hints=["For one fixed start position in s you can extend greedily and match each character to its earliest unused occurrence in t. Doing that for every start is correct but costs O(m &middot; n) per start. Look for a table that reuses work between starts.",
           "Let <code>L[i][j]</code> be the length of the longest suffix of <code>s[0..i)</code> that is a subsequence of <code>t[0..j)</code>. If a suffix of some length works, every shorter suffix works too.",
           "If <code>s[i-1] != t[j-1]</code> then <code>L[i][j] = L[i][j-1]</code>. If they are equal, the character can be matched here, so <code>L[i][j] = max(L[i][j-1], L[i-1][j-1] + 1)</code>. The answer is the largest <code>L[i][n]</code>."],
    editorial=["Because we need a substring of s, it is natural to fix where it <em>ends</em>. Define <code>L[i][j]</code> as the longest suffix of <code>s[:i]</code> that is a subsequence of <code>t[:j]</code>. Note the monotonicity: if a suffix of length k is a subsequence, so is any shorter suffix of it (drop its first characters).",
               "Transition: if the last character <code>s[i-1]</code> differs from <code>t[j-1]</code>, t[j-1] cannot help, so <code>L[i][j] = L[i][j-1]</code>. If they are equal, we either do not use <code>t[j-1]</code> (value <code>L[i][j-1]</code>) or match <code>s[i-1]</code> to it, which needs the rest of the suffix to fit into <code>t[:j-1]</code>, giving <code>L[i-1][j-1] + 1</code> by monotonicity. The answer is the maximum of <code>L[i][len(t)]</code> over all i.",
               "Compare with the longest common <em>subsequence</em> (no contiguity in s, so the best value always carries forward from the row above) and with the longest common <em>substring</em> (contiguous in both strings, so a mismatch resets the value to zero). Here the requirement is contiguous in one string only, which gives this hybrid table. Keep one previous row for O(n) memory."],
    time="O(m &middot; n)", space="O(n)",
    solution='''def longestEmbeddedSubstring(s, t):
    n = len(t)
    prev = [0] * (n + 1)
    best = 0
    for i in range(1, len(s) + 1):
        cur = [0] * (n + 1)
        c = s[i - 1]
        for j in range(1, n + 1):
            v = cur[j - 1]
            if c == t[j - 1] and prev[j - 1] + 1 > v:
                v = prev[j - 1] + 1
            cur[j] = v
        if cur[n] > best:
            best = cur[n]
        prev = cur
    return best
''',
    tests=[["abcab", "xaybzc"], ["abcde", "aebdc"], ["abab", "bbaa"], ["", ""], ["abc", ""], ["", "abc"], ["a", "a"], ["a", "b"],
           ["abc", "abc"], ["abc", "cba"], ["aaaa", "aa"], ["abcdef", "fbdfaceb"], ["xyzxyz", "zzyyxx"]],
)
_r = rnd(11005)
p["tests"] += [
    [_rs(_r, "abcd", 800, 800), _rs(_r, "abcd", 800, 800)],
    [_rs(_r, LOW, 800, 800), _rs(_r, LOW, 800, 800)],
    ["ab" * 400, "a" * 300 + "b" * 300 + "a" * 100 + "b" * 100],
    ["abcdefghij" * 80, "jihgfedcba" * 80],
]


def _b_embedded(s, t):
    best = 0
    for i in range(len(s)):
        for j in range(i + 1, len(s) + 1):
            if j - i > best and _is_sub(s[i:j], t):
                best = j - i
    return best


def _v_embedded(tests):
    _check_strings(tests, 800)


CHECKS["longest-substring-that-is-subsequence-of-other"] = (
    _b_embedded, lambda r: [_rs(r, "abc", 0, 8), _rs(r, "abc", 0, 8)], "exact")
VALIDATE["longest-substring-that-is-subsequence-of-other"] = _v_embedded


p = add(
    id="longest-common-substring-with-k-mismatches", title="Longest Common Substring with K Mismatches", diff="Medium", topic="Dynamic Programming",
    fn="longestApproxCommonSubstring", params=[("s", "string"), ("t", "string"), ("k", "int")], ret="int", cmp="exact",
    desc="<p>Find the greatest length <code>L</code> such that some substring of <code>s</code> of length <code>L</code> and some substring of <code>t</code> of the same length <code>L</code> differ in <b>at most</b> <code>k</code> positions (compare them character by character at the same offsets).</p><p>Return <code>L</code>; it is <code>0</code> when no length works (for instance if a string is empty).</p><pre>s = \"abcdef\", t = \"abxdyf\", k = 1  ->  4   (\"abcd\" vs \"abxd\")\ns = \"abcdef\", t = \"abxdyf\", k = 2  ->  6\ns = \"aaaa\",   t = \"bbbb\",   k = 2  ->  2</pre>",
    constraints=["0 &le; s.length, t.length &le; 500", "0 &le; k &le; 500", "Both strings contain only lowercase English letters"],
    hints=["With k = 0 this is the longest common substring. The key observation there is that a pair of substrings is described by their start positions, and the next pair of characters always lies on the same diagonal i - j.",
           "Fix the diagonal <code>d = i - j</code>. Along it you compare <code>s[i]</code> with <code>t[i - d]</code> and get a sequence of match/mismatch flags. The task on one diagonal is: the longest window with at most k mismatches.",
           "Use a sliding window on every diagonal: extend the right end, count mismatches, and move the left end forward while the count exceeds k. Take the best window over all diagonals. There are m + n - 1 diagonals with a total of m &middot; n cells."],
    editorial=["Two equal-length substrings starting at s[i] and t[j] are compared character by character, so the pairs (s[i+x], t[j+x]) all lie on the diagonal with offset <code>i - j</code>. Every candidate pair of substrings therefore corresponds to a contiguous window along one diagonal of the m by n grid whose cell (i, j) is a mismatch when <code>s[i] != t[j]</code>.",
               "The answer is the longest window, over all diagonals, that contains at most k mismatching cells. On a single diagonal this is the classic 'longest window with at most k bad elements' problem solved with two pointers in linear time: advance the right end, add one to the counter if the new cell is a mismatch, and while the counter exceeds k advance the left end (subtracting if the cell it leaves was a mismatch). The window never shrinks below a valid state and each pointer moves at most the diagonal length.",
               "In total the work is the number of grid cells, O(m &middot; n). The naive approach of trying every pair of start positions and every length is O(m &middot; n &middot; min(m, n)) or worse."],
    time="O(m &middot; n)", space="O(1)",
    solution='''def longestApproxCommonSubstring(s, t, k):
    m, n = len(s), len(t)
    best = 0
    for d in range(-(m - 1), n):
        i0 = 0 if d >= 0 else -d
        j0 = i0 + d
        length = min(m - i0, n - j0)
        lo = 0
        bad = 0
        for hi in range(length):
            if s[i0 + hi] != t[j0 + hi]:
                bad += 1
                while bad > k:
                    if s[i0 + lo] != t[j0 + lo]:
                        bad -= 1
                    lo += 1
            if hi - lo + 1 > best:
                best = hi - lo + 1
    return best
''',
    tests=[["abcdef", "abxdyf", 1], ["abcdef", "abxdyf", 2], ["aaaa", "bbbb", 2], ["", "", 0], ["abc", "", 3], ["", "abc", 0],
           ["a", "b", 0], ["a", "b", 1], ["abcde", "xyz", 0], ["abcde", "xyz", 2], ["abcxyz", "xyzabc", 0],
           ["abcabc", "bcabca", 1], ["abcdefg", "gfedcba", 3], ["aaaa", "aa", 0]],
)
_r = rnd(11006)
p["tests"] += [
    [_rs(_r, "abcd", 500, 500), _rs(_r, "abcd", 500, 500), 25],
    [_rs(_r, LOW, 500, 500), _rs(_r, LOW, 400, 400), 3],
    [_rs(_r, "ab", 500, 500), _rs(_r, "ab", 500, 500), 0],
]


def _b_kmis(s, t, k):
    best = 0
    for i in range(len(s)):
        for j in range(len(t)):
            mis = 0
            ln = 0
            while i + ln < len(s) and j + ln < len(t):
                if s[i + ln] != t[j + ln]:
                    mis += 1
                if mis > k:
                    break
                ln += 1
            best = max(best, ln)
    return best


def _v_kmis(tests):
    for t in tests:
        s, u, k = t["args"]
        assert len(s) <= 500 and len(u) <= 500 and 0 <= k <= 500
        assert all(c in LOW for c in s + u)


CHECKS["longest-common-substring-with-k-mismatches"] = (
    _b_kmis, lambda r: [_rs(r, "abc", 0, 9), _rs(r, "abc", 0, 9), r.randint(0, 4)], "exact")
VALIDATE["longest-common-substring-with-k-mismatches"] = _v_kmis


p = add(
    id="longest-common-subsequence-of-two-permutations", title="Common Subsequence of Two Arrays of Distinct Values", diff="Medium", topic="Dynamic Programming",
    fn="lcsDistinctValues", params=[("a", "int[]"), ("b", "int[]")], ret="int", cmp="exact",
    desc="<p>Each of the arrays <code>a</code> and <code>b</code> contains <b>distinct</b> values (no value repeats inside the same array), although the two arrays may share any number of values, or none.</p><p>Return the length of their longest common subsequence: the longest sequence of values that can be read, in order, from both arrays.</p><p>The arrays are long enough that the usual O(n&middot;m) table is too slow; an O((n + m) log n) solution is expected.</p><pre>a = [3, 1, 2, 5, 4], b = [1, 3, 5, 2, 4]  ->  3   (for example 1, 2, 4)\na = [7, 1, 5, 3],    b = [3, 9, 1, 7]     ->  1\na = [4, 5, 6],       b = [1, 2, 3]        ->  0</pre>",
    constraints=["0 &le; a.length, b.length &le; 3,000", "1 &le; a[i], b[j] &le; 1,000,000", "All values inside a are distinct; all values inside b are distinct"],
    hints=["The table-based longest common subsequence compares every pair of elements. Because values do not repeat inside an array, each value of b has at most one possible partner in a. How can you use that?",
           "Replace every value of b that also occurs in a by its <em>index in a</em>, and drop the values of b that do not occur in a. A common subsequence now corresponds to a sequence of indices that increases from left to right.",
           "So the answer is the length of the longest strictly increasing subsequence of the index sequence. Compute it in O(k log k) with the 'tails' array and binary search."],
    editorial=["Pick any common subsequence. Each of its values occurs exactly once in a, at some index, and exactly once in b. Reading the subsequence from left to right, the indices in a must increase (it is a subsequence of a) and the indices in b must increase as well (it is a subsequence of b). Replace each element of b that also occurs in a by its position in a. The positions in b stay in order, so a common subsequence is exactly a subsequence of this new sequence whose values strictly increase.",
               "Hence the answer is the length of the longest strictly increasing subsequence (LIS) of the translated sequence. The LIS is found in O(k log k) by keeping an array <code>tails</code>, where <code>tails[x]</code> is the smallest possible last value of an increasing subsequence of length <code>x + 1</code>. For each new element, binary-search its position with <code>bisect_left</code> and either append or overwrite.",
               "Building the value-to-index map takes O(n), so the total is O((n + m) log n). The quadratic table would need 9 million cells for the largest inputs here, which is too slow in plain Python. The trick only works because values are distinct; with repeated values one element of b can map to several indices of a."],
    time="O((n + m) log n)", space="O(n + m)",
    solution='''from bisect import bisect_left


def lcsDistinctValues(a, b):
    pos = {v: i for i, v in enumerate(a)}
    tails = []
    for v in b:
        i = pos.get(v)
        if i is None:
            continue
        k = bisect_left(tails, i)
        if k == len(tails):
            tails.append(i)
        else:
            tails[k] = i
    return len(tails)
''',
    tests=[[[3, 1, 2, 5, 4], [1, 3, 5, 2, 4]], [[7, 1, 5, 3], [3, 9, 1, 7]], [[4, 5, 6], [1, 2, 3]], [[], []], [[1, 2], []],
           [[], [1, 2]], [[5], [5]], [[5], [6]], [[1, 2, 3, 4, 5], [1, 2, 3, 4, 5]], [[1, 2, 3, 4, 5], [5, 4, 3, 2, 1]],
           [[10, 20, 30, 40], [40, 10, 30, 20]], [[1000000, 1, 999999], [999999, 1000000, 2, 1]]],
)
_r = rnd(11007)
_base = _r.sample(range(1, 1000001), 3600)
_a = _base[:3000]
_b = list(dict.fromkeys(_r.sample(_base[900:], 2600) + _r.sample(range(1, 1000001), 100)))
p["tests"].append([_a, _b])
p["tests"].append([_r.sample(range(1, 3001), 3000), _r.sample(range(1, 3001), 3000)])
p["tests"].append([list(range(1, 3001)), list(range(3000, 1500, -1)) + list(range(1, 1501))])


def _b_perm(a, b):
    best = 0
    for k in range(min(len(a), len(b)), 0, -1):
        for ia in combinations(a, k):
            if _is_sub(ia, b):
                return k
    return best


def _g_perm(r):
    pool = r.sample(range(1, 12), 11)
    a = pool[:r.randint(0, 7)]
    b = r.sample(pool, r.randint(0, 7))
    return [a, b]


def _v_perm(tests):
    for t in tests:
        a, b = t["args"]
        assert len(a) <= 3000 and len(b) <= 3000
        assert len(set(a)) == len(a) and len(set(b)) == len(b)
        assert all(1 <= v <= 1000000 for v in a + b)


CHECKS["longest-common-subsequence-of-two-permutations"] = (_b_perm, _g_perm, "exact")
VALIDATE["longest-common-subsequence-of-two-permutations"] = _v_perm


p = add(
    id="count-common-subsequence-pairs", title="Count Common Subsequence Pairs", diff="Medium", topic="Dynamic Programming",
    fn="countCommonSubsequencePairs", params=[("s", "string"), ("t", "string")], ret="int", cmp="exact",
    desc="<p>Choose a set of positions in <code>s</code> and a set of positions in <code>t</code> (either set may be empty). The two choices form a <em>matching pair</em> if the characters picked from <code>s</code>, read left to right, spell exactly the same string as the characters picked from <code>t</code>.</p><p>Count the matching pairs of position sets. Two pairs are different when their position sets differ, even if they spell the same text, and the pair of two empty sets counts. Return the count modulo <code>1,000,000,007</code>.</p><pre>s = \"ab\",  t = \"ab\"  ->  4   (empty/empty, a/a, b/b, ab/ab)\ns = \"aa\",  t = \"a\"   ->  3   (empty/empty, s[0]/t[0], s[1]/t[0])\ns = \"abc\", t = \"xyz\"  ->  1   (only empty/empty)</pre>",
    constraints=["0 &le; s.length, t.length &le; 600", "Both strings contain only lowercase English letters"],
    hints=["Count prefixes first: let <code>f(i, j)</code> be the number of matching pairs that use only the first i characters of s and the first j characters of t. What is <code>f(0, j)</code>?",
           "Split the pairs counted by <code>f(i, j)</code> by whether s[i] is used and whether t[j] is used. The pairs where s[i] is unused number <code>f(i-1, j)</code>, those where t[j] is unused number <code>f(i, j-1)</code>, and those where neither is used are counted twice.",
           "Pairs that use <em>both</em> s[i] and t[j] as their last characters exist only if <code>s[i] == t[j]</code>, and there are exactly <code>f(i-1, j-1)</code> of them. So <code>f(i, j) = f(i-1, j) + f(i, j-1) - f(i-1, j-1) + (f(i-1, j-1) if s[i] == t[j])</code>."],
    editorial=["Let <code>f(i, j)</code> count matching pairs inside the prefixes <code>s[:i]</code> and <code>t[:j]</code>. When one prefix is empty the only possible pair is the empty one, so <code>f(0, j) = f(i, 0) = 1</code>.",
               "For i, j &ge; 1 split by the last characters. Pairs that do not use <code>s[i-1]</code> are counted by <code>f(i-1, j)</code>; pairs that do not use <code>t[j-1]</code> by <code>f(i, j-1)</code>; pairs that use neither are in both, and there are <code>f(i-1, j-1)</code> of them, so inclusion-exclusion removes them once. What remains are pairs that use both last characters. For such a pair, both position sets end in the last character, so the two last characters must be equal, and what is left is any matching pair of the shorter prefixes: <code>f(i-1, j-1)</code> choices. This term is added only if <code>s[i-1] == t[j-1]</code>.",
               "Note that this counts pairs of <em>position sets</em>, unlike the count of distinct common strings, which needs a different technique. Apply the modulus at each cell (subtracting can go negative, so reduce with <code>% MOD</code> after adding). Two rolling rows give O(n) memory."],
    time="O(m &middot; n)", space="O(n)",
    solution='''def countCommonSubsequencePairs(s, t):
    MOD = 10 ** 9 + 7
    n = len(t)
    prev = [1] * (n + 1)
    for i in range(1, len(s) + 1):
        cur = [1] * (n + 1)
        c = s[i - 1]
        for j in range(1, n + 1):
            v = prev[j] + cur[j - 1] - prev[j - 1]
            if c == t[j - 1]:
                v += prev[j - 1]
            cur[j] = v % MOD
        prev = cur
    return prev[n]
''',
    tests=[["ab", "ab"], ["aa", "a"], ["abc", "xyz"], ["", ""], ["abc", ""], ["", "abc"], ["a", "a"], ["aba", "ab"], ["aaa", "aaa"],
           ["abab", "baba"], ["abcabc", "cba"], ["aaaaaaaaaaaaaaaaaaaa", "aaaaaaaaaaaaaaaaaaaa"]],
)
_r = rnd(11008)
p["tests"] += [
    [_rs(_r, "ab", 600, 600), _rs(_r, "ab", 600, 600)],
    [_rs(_r, LOW, 600, 600), _rs(_r, "abcdefgh", 600, 600)],
    ["a" * 600, "a" * 600],
]


def _b_cps(s, t):
    cs, ct = Counter(), Counter()
    for mask in range(1 << len(s)):
        cs["".join(s[i] for i in range(len(s)) if mask >> i & 1)] += 1
    for mask in range(1 << len(t)):
        ct["".join(t[i] for i in range(len(t)) if mask >> i & 1)] += 1
    return sum(v * ct[k] for k, v in cs.items()) % MOD


def _v_cps(tests):
    _check_strings(tests, 600)


CHECKS["count-common-subsequence-pairs"] = (
    _b_cps, lambda r: [_rs(r, "abc", 0, 8), _rs(r, "abc", 0, 8)], "exact")
VALIDATE["count-common-subsequence-pairs"] = _v_cps


# ---------------------------------------------------------------- HARD

p = add(
    id="longest-common-subsequence-containing-pattern", title="Longest Common Subsequence Containing a Pattern", diff="Hard", topic="Dynamic Programming",
    fn="longestCommonWithPattern", params=[("s", "string"), ("t", "string"), ("pattern", "string")], ret="int", cmp="exact",
    desc="<p>Among all strings that are subsequences of <b>both</b> <code>s</code> and <code>t</code> <em>and</em> that also contain <code>pattern</code> as a subsequence, find the length of the longest one.</p><p>Return <code>-1</code> if no common subsequence of <code>s</code> and <code>t</code> contains <code>pattern</code>. An empty pattern is contained in every string, so then the answer is the ordinary longest common subsequence length.</p><pre>s = \"abcbdab\", t = \"bdcaba\", pattern = \"ba\"  ->  4   (\"bdab\" contains b ... a)\ns = \"abcbdab\", t = \"bdcaba\", pattern = \"aa\"  ->  3\ns = \"abcbdab\", t = \"bdcaba\", pattern = \"ac\"  ->  -1  (no common subsequence has an a before a c)</pre>",
    constraints=["0 &le; s.length, t.length &le; 100", "0 &le; pattern.length &le; 20", "All strings contain only lowercase English letters"],
    hints=["Without the pattern this is the ordinary longest common subsequence table. Which extra piece of information must a state remember to know whether the pattern is contained?",
           "Add a third index k: let <code>f[i][j][k]</code> be the length of the longest common subsequence of the first i characters of s and the first j characters of t that contains the first k characters of the pattern as a subsequence (or minus infinity if none does).",
           "When <code>s[i-1] == t[j-1] == c</code>, you can append c either as a plain extra character, from <code>f[i-1][j-1][k]</code>, or, if <code>c == pattern[k-1]</code>, as the last character needed for the first k pattern characters, from <code>f[i-1][j-1][k-1]</code>. The answer is <code>f[m][n][len(pattern)]</code>."],
    editorial=["Extend the LCS table with the number k of pattern characters that must be contained. Define <code>f[i][j][k]</code> as the maximum length of a common subsequence of <code>s[:i]</code> and <code>t[:j]</code> that contains <code>pattern[:k]</code> as a subsequence, and minus infinity if there is none. The base cases are <code>f[i][j][0]</code> = the plain LCS (starting from 0 for the empty prefix) and <code>f[i][j][k] = -inf</code> for k &gt; 0 when one prefix is empty.",
               "For the transition, an optimal string either does not use <code>s[i-1]</code> (value <code>f[i-1][j][k]</code>), does not use <code>t[j-1]</code> (value <code>f[i][j-1][k]</code>), or ends with a character matched to both of them, which requires <code>s[i-1] == t[j-1] = c</code>. Remove that last character c from the string. What is left is a common subsequence of the shorter prefixes. If it still contains <code>pattern[:k]</code>, the value is <code>f[i-1][j-1][k] + 1</code>. Otherwise the string contained <code>pattern[:k]</code> only thanks to the final c, which forces <code>c == pattern[k-1]</code> and the rest to contain <code>pattern[:k-1]</code>, so the value is <code>f[i-1][j-1][k-1] + 1</code>.",
               "The final answer is <code>f[m][n][L]</code> with L the pattern length, or -1 when that is minus infinity. The table has m &middot; n &middot; (L + 1) cells with O(1) work each. Keeping only the previous row of i reduces memory to O(n &middot; L)."],
    time="O(m &middot; n &middot; L)", space="O(n &middot; L)",
    solution='''def longestCommonWithPattern(s, t, pattern):
    NEG = -10 ** 9
    n, L = len(t), len(pattern)
    prev = [[0] + [NEG] * L for _ in range(n + 1)]
    for i in range(1, len(s) + 1):
        c = s[i - 1]
        cur = [[0] + [NEG] * L] + [None] * n
        for j in range(1, n + 1):
            up, left = prev[j], cur[j - 1]
            row = [up[k] if up[k] > left[k] else left[k] for k in range(L + 1)]
            if c == t[j - 1]:
                diag = prev[j - 1]
                for k in range(L + 1):
                    if diag[k] + 1 > row[k]:
                        row[k] = diag[k] + 1
                    if k and c == pattern[k - 1] and diag[k - 1] + 1 > row[k]:
                        row[k] = diag[k - 1] + 1
            cur[j] = row
        prev = cur
    best = prev[n][L]
    return best if best >= 0 else -1
''',
    tests=[["abcbdab", "bdcaba", "ba"], ["abcbdab", "bdcaba", "aa"], ["abcbdab", "bdcaba", "ac"], ["abcbdab", "bdcaba", ""],
           ["", "", ""], ["", "", "a"], ["abc", "abc", "abc"], ["abc", "abc", "abcd"], ["abc", "cba", "ab"], ["aab", "ab", "aab"],
           ["aaaa", "aaa", "aa"], ["xyzxyz", "zyxzyx", "zx"], ["abcabcabc", "cbacbacba", "bb"]],
)
_r = rnd(11009)
p["tests"] += [
    [_rs(_r, "abc", 100, 100), _rs(_r, "abc", 100, 100), _rs(_r, "abc", 15, 15)],
    [_rs(_r, "ab", 100, 100), _rs(_r, "ab", 100, 100), "ab" * 10],
    [_rs(_r, LOW, 100, 100), _rs(_r, "abcdefghij", 100, 100), "ace"],
    ["a" * 100, "a" * 100, "a" * 20],
]


def _b_lcs_pat(s, t, pat):
    best = -1
    for mask in range(1 << len(s)):
        w = "".join(s[i] for i in range(len(s)) if mask >> i & 1)
        if len(w) > best and _is_sub(w, t) and _is_sub(pat, w):
            best = len(w)
    return best


def _v_lcs_pat(tests):
    for t in tests:
        s, u, pat = t["args"]
        assert len(s) <= 100 and len(u) <= 100 and len(pat) <= 20
        assert all(c in LOW for c in s + u + pat)


CHECKS["longest-common-subsequence-containing-pattern"] = (
    _b_lcs_pat, lambda r: [_rs(r, "abc", 0, 8), _rs(r, "abc", 0, 8), _rs(r, "abc", 0, 3)], "exact")
VALIDATE["longest-common-subsequence-containing-pattern"] = _v_lcs_pat


p = add(
    id="lexicographically-smallest-shortest-supersequence", title="Lexicographically Smallest Shortest Supersequence", diff="Hard", topic="Dynamic Programming",
    fn="smallestShortestSupersequence", params=[("a", "string"), ("b", "string")], ret="string", cmp="exact",
    desc="<p>Among all strings of the minimum possible length that contain both <code>a</code> and <code>b</code> as subsequences, return the one that comes first in alphabetical (lexicographic) order.</p><p>If both inputs are empty, return the empty string.</p><pre>a = \"abac\", b = \"cab\"  ->  \"cabac\"\na = \"ab\",   b = \"ba\"   ->  \"aba\"   (\"bab\" is as short but alphabetically later)\na = \"\",     b = \"xy\"   ->  \"xy\"</pre>",
    constraints=["0 &le; a.length, b.length &le; 600", "Both strings contain only lowercase English letters"],
    hints=["First find only the <em>length</em> of the shortest common supersequence. Let <code>f(i, j)</code> be that length for the suffixes <code>a[i:]</code> and <code>b[j:]</code>.",
           "<code>f(i, j) = 1 + f(i+1, j+1)</code> if <code>a[i] == b[j]</code>, else <code>1 + min(f(i+1, j), f(i, j+1))</code>. Fill the table from the end of both strings, with <code>f(m, j) = n - j</code> and <code>f(i, n) = m - i</code>.",
           "Build the answer from the front. At (i, j): equal characters are always written once and both pointers advance. Otherwise write <code>a[i]</code> if moving to (i+1, j) keeps the length optimal, or <code>b[j]</code> if (i, j+1) does; when both keep it optimal, write the smaller of the two characters. Append the rest of the other string when one is used up."],
    editorial=["Work with suffixes so the answer can be produced front to back. Let <code>f[i][j]</code> be the length of the shortest common supersequence of <code>a[i:]</code> and <code>b[j:]</code>. If <code>a[i] == b[j]</code>, a shortest supersequence can always start with this letter shared by both strings, so <code>f[i][j] = 1 + f[i+1][j+1]</code>. Otherwise the first character of an optimal answer must be <code>a[i]</code> or <code>b[j]</code> (any other letter would be wasted), giving <code>1 + min(f[i+1][j], f[i][j+1])</code>.",
               "To make the result lexicographically smallest among strings of equal (minimum) length, decide each character greedily from the left, because with equal lengths the first differing character settles the order. At state (i, j): when the characters are equal, any optimal answer can start with that letter and advancing both pointers loses nothing, and no other first letter is possible. When they differ, the candidate first letters are <code>a[i]</code> (allowed only if <code>f[i+1][j] + 1 == f[i][j]</code>) and <code>b[j]</code> (allowed only if <code>f[i][j+1] + 1 == f[i][j]</code>). Two different letters can never tie, so we simply take the smaller allowed one, and the rest of the answer is the best answer from the new state.",
               "When one string is used up, the remainder of the other is forced. The table costs O(m &middot; n) time and memory, and the reconstruction is O(m + n). Writing any valid shortest supersequence is easier, but would not be unique, which is why the problem asks for the alphabetically smallest."],
    time="O(m &middot; n)", space="O(m &middot; n)",
    solution='''def smallestShortestSupersequence(a, b):
    m, n = len(a), len(b)
    f = [[0] * (n + 1) for _ in range(m + 1)]
    for j in range(n + 1):
        f[m][j] = n - j
    for i in range(m - 1, -1, -1):
        f[i][n] = m - i
        row, nxt = f[i], f[i + 1]
        ai = a[i]
        for j in range(n - 1, -1, -1):
            if ai == b[j]:
                row[j] = 1 + nxt[j + 1]
            else:
                x, y = nxt[j], row[j + 1]
                row[j] = 1 + (x if x < y else y)
    i = j = 0
    out = []
    while i < m and j < n:
        if a[i] == b[j]:
            out.append(a[i])
            i += 1
            j += 1
        else:
            can_a = f[i + 1][j] + 1 == f[i][j]
            can_b = f[i][j + 1] + 1 == f[i][j]
            if can_a and (not can_b or a[i] < b[j]):
                out.append(a[i])
                i += 1
            else:
                out.append(b[j])
                j += 1
    out.append(a[i:])
    out.append(b[j:])
    return "".join(out)
''',
    tests=[["abac", "cab"], ["ab", "ba"], ["", "xy"], ["xy", ""], ["", ""], ["a", "a"], ["a", "b"], ["b", "a"], ["geek", "eke"],
           ["bbbaaaba", "bbababbb"], ["abc", "abc"], ["aaaa", "aa"], ["zyx", "xyz"], ["abcbdab", "bdcaba"]],
)
_r = rnd(11010)
p["tests"] += [
    [_rs(_r, "abcd", 600, 600), _rs(_r, "abcd", 600, 600)],
    [_rs(_r, LOW, 600, 600), _rs(_r, LOW, 500, 500)],
    ["ba" * 300, "ab" * 300],
]


def _b_lex_scs(a, b):
    letters = sorted(set(a + b))
    for L in range(max(len(a), len(b)), len(a) + len(b) + 1):
        for w in product(letters, repeat=L):
            if _is_sub(a, w) and _is_sub(b, w):
                return "".join(w)


def _v_lex_scs(tests):
    _check_strings(tests, 600)


CHECKS["lexicographically-smallest-shortest-supersequence"] = (
    _b_lex_scs, lambda r: [_rs(r, "abc", 0, 4), _rs(r, "abc", 0, 4)], "exact")
VALIDATE["lexicographically-smallest-shortest-supersequence"] = _v_lex_scs


p = add(
    id="count-distinct-longest-common-subsequences", title="Count Distinct Longest Common Subsequences", diff="Hard", topic="Dynamic Programming",
    fn="countDistinctLCS", params=[("s", "string"), ("t", "string")], ret="int", cmp="exact",
    desc="<p>The longest common subsequence of two strings is often not unique: several different strings can have the maximum length. Count how many <b>distinct strings</b> (as texts, not as position choices) are common subsequences of <code>s</code> and <code>t</code> with the maximum possible length.</p><p>Return the count modulo <code>1,000,000,007</code>. If the strings have no common character the only longest common subsequence is the empty string, so the answer is <code>1</code>.</p><pre>s = \"acac\", t = \"caca\"  ->  2   (\"aca\" and \"cac\")\ns = \"aaa\",  t = \"aa\"    ->  1   (\"aa\")\ns = \"ac\",   t = \"ca\"    ->  2   (\"a\" and \"c\")</pre>",
    constraints=["0 &le; s.length, t.length &le; 300", "Both strings contain only the letters a, c, g and t"],
    hints=["First compute the usual LCS length table on suffixes: <code>L[i][j]</code> is the LCS length of <code>s[i:]</code> and <code>t[j:]</code>. Counting position choices would count the same text many times, so count texts instead.",
           "Group the longest common subsequences by their first letter c. For a fixed c, the string <code>c + w</code> is a common subsequence exactly when w is a common subsequence of what follows the <em>first</em> occurrence of c in s[i:] and the first occurrence of c in t[j:].",
           "Let <code>g(i, j)</code> be the number of distinct LCS strings of the suffixes. For every letter c with first occurrences p in s[i:] and q in t[j:], add <code>g(p+1, q+1)</code> if <code>L[p+1][q+1] == L[i][j] - 1</code>. With <code>L[i][j] == 0</code>, <code>g = 1</code> (only the empty string)."],
    editorial=["Let <code>L[i][j]</code> be the LCS length for the suffixes <code>s[i:]</code> and <code>t[j:]</code>, and <code>g[i][j]</code> the number of distinct strings of length <code>L[i][j]</code> that are common subsequences of those suffixes. If <code>L[i][j] = 0</code>, only the empty string qualifies, so <code>g = 1</code>.",
               "Otherwise classify the strings by their first letter c. A string <code>c + w</code> is a subsequence of <code>s[i:]</code> iff w is a subsequence of the part of s after the <em>first</em> occurrence of c (greedy earliest matching is always at least as good), and the same holds for t. So for each letter c let p be its first position at or after i in s and q its first position at or after j in t (skip the letter if either does not exist). The strings starting with c that have maximum length correspond to maximum-length strings w for the pair (p+1, q+1), but only if that pair can reach length <code>L[i][j] - 1</code>, i.e. <code>L[p+1][q+1] == L[i][j] - 1</code>. Then add <code>g[p+1][q+1]</code>. Different first letters give different strings, and different w give different strings, so nothing is counted twice.",
               "The answer is <code>g[0][0] mod 1,000,000,007</code>. Precompute the next-occurrence index of each letter for s and t, which makes each cell cost O(sigma) with sigma = 4. The total time is O(sigma &middot; m &middot; n). A brute-force approach that enumerates all common subsequences is exponential, and counting position choices (as in the matching-pairs problem) would count one text many times."],
    time="O(&sigma; &middot; m &middot; n)", space="O(m &middot; n)",
    solution='''def countDistinctLCS(s, t):
    MOD = 10 ** 9 + 7
    letters = "acgt"
    m, n = len(s), len(t)

    def next_table(x):
        size = len(x)
        nxt = [[-1] * 4 for _ in range(size + 1)]
        for i in range(size - 1, -1, -1):
            nxt[i] = nxt[i + 1][:]
            nxt[i][letters.index(x[i])] = i
        return nxt

    ns, nt = next_table(s), next_table(t)
    L = [[0] * (n + 2) for _ in range(m + 2)]
    for i in range(m - 1, -1, -1):
        for j in range(n - 1, -1, -1):
            if s[i] == t[j]:
                L[i][j] = L[i + 1][j + 1] + 1
            else:
                L[i][j] = max(L[i + 1][j], L[i][j + 1])
    g = [[1] * (n + 2) for _ in range(m + 2)]
    for i in range(m - 1, -1, -1):
        for j in range(n - 1, -1, -1):
            if L[i][j] == 0:
                continue
            total = 0
            for c in range(4):
                p, q = ns[i][c], nt[j][c]
                if p >= 0 and q >= 0 and L[p + 1][q + 1] == L[i][j] - 1:
                    total += g[p + 1][q + 1]
            g[i][j] = total % MOD
    return g[0][0] % MOD
''',
    tests=[["acac", "caca"], ["aaa", "aa"], ["ac", "ca"], ["", ""], ["acgt", ""], ["", "acgt"], ["a", "a"], ["a", "c"], ["acgt", "acgt"],
           ["acgtacgt", "tgcatgca"], ["aaaa", "aaaa"], ["cagt", "gact"], ["acacacac", "cacacaca"]],
)
_r = rnd(11011)
p["tests"] += [
    [_rs(_r, "acgt", 300, 300), _rs(_r, "acgt", 300, 300)],
    [_rs(_r, "ac", 300, 300), _rs(_r, "ac", 300, 300)],
    ["ac" * 150, "ca" * 150],
]


def _b_dlcs(s, t):
    common = _subseqs(s) & _subseqs(t)
    top = max(len(w) for w in common)
    return sum(1 for w in common if len(w) == top) % MOD


def _g_dlcs(r):
    alpha = r.choice(["ac", "acg", "acgt"])
    return [_rs(r, alpha, 0, 9), _rs(r, alpha, 0, 9)]


def _v_dlcs(tests):
    _check_strings(tests, 300, "acgt")


CHECKS["count-distinct-longest-common-subsequences"] = (_b_dlcs, _g_dlcs, "exact")
VALIDATE["count-distinct-longest-common-subsequences"] = _v_dlcs


import lib as _lib  # noqa: E402

_TIERS = {
    "count-matching-substring-pairs": "extra",
    "longest-substring-that-is-subsequence-of-other": "extra",
    "longest-common-substring-with-k-mismatches": "extra",
    "longest-common-subsequence-of-two-permutations": "extra",
    "count-common-subsequence-pairs": "extra",
    "longest-common-subsequence-containing-pattern": "extra",
    "lexicographically-smallest-shortest-supersequence": "extra",
    "count-distinct-longest-common-subsequences": "extra",
}
for _q in _lib.P:
    if _q["id"] in _TIERS:
        _q["tier"] = _TIERS[_q["id"]]
