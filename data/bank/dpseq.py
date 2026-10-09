"""Problems: Dynamic Programming on strings and sequences. See data/lib.py for the registry."""
from itertools import combinations

from lib import add, rnd, CHECKS, VALIDATE, gen_arr  # noqa: F401

MOD = 10 ** 9 + 7


def _rs(r, alpha, lo, hi):
    return "".join(r.choice(alpha) for _ in range(r.randint(lo, hi)))


def _subseqs(s):
    """Every distinct subsequence of s (including the empty one), as a set of strings."""
    out = set()
    n = len(s)
    for mask in range(1 << n):
        out.add("".join(s[i] for i in range(n) if mask >> i & 1))
    return out


def _is_pal(t):
    return t == t[::-1]


# ---------------------------------------------------------------- EASY

p = add(
    id="longest-common-substring-length", title="Longest Common Substring", diff="Easy", topic="Dynamic Programming",
    fn="longestCommonSubstring", params=[("s", "string"), ("t", "string")], ret="int", cmp="exact",
    desc="<p>Given two strings <code>s</code> and <code>t</code>, return the length of the longest string that appears in <b>both</b> of them as a <em>contiguous block</em> of characters (a substring, not merely a subsequence).</p><p>If the strings have no character in common, or one of them is empty, the answer is <code>0</code>.</p><pre>s = \"xabcdy\", t = \"zzabcdq\"  ->  4   (\"abcd\")\ns = \"abab\",   t = \"baba\"     ->  3   (\"aba\" or \"bab\")</pre>",
    constraints=["0 &le; s.length, t.length &le; 1,500", "Both strings contain only lowercase English letters"],
    hints=["Try every pair of starting positions and extend while the characters keep matching. That works, but it repeats a lot of comparisons. How could you reuse the work of a previous pair?",
           "Let L(i, j) be the length of the longest common block that <em>ends exactly</em> at position i of s and position j of t. If the two characters differ, L(i, j) = 0; otherwise L(i, j) = L(i-1, j-1) + 1.",
           "The answer is the maximum value of L(i, j) over all cells, not the last cell. Each row only needs the row above it, so two arrays of length t.length + 1 are enough."],
    editorial=["Define <code>L[i][j]</code> as the length of the longest common substring that ends at <code>s[i-1]</code> and <code>t[j-1]</code>. A common block that ends at these two positions must either be empty (the characters differ) or be one character longer than the block ending at the previous pair of positions, so <code>L[i][j] = L[i-1][j-1] + 1</code> when the characters match and <code>0</code> otherwise.",
               "Unlike the subsequence version, a mismatch resets the run to zero instead of carrying the best value forward, because the block must stay contiguous. The answer is the largest value seen anywhere in the table. Keeping only the previous row gives O(t.length) memory. Comparing every pair of start positions and extending is O(m &middot; n &middot; min(m, n)) in the worst case, far too slow at the upper limits."],
    time="O(m &middot; n)", space="O(n)",
    solution='''def longestCommonSubstring(s, t):
    n = len(t)
    prev = [0] * (n + 1)
    best = 0
    for i in range(1, len(s) + 1):
        cur = [0] * (n + 1)
        c = s[i - 1]
        for j in range(1, n + 1):
            if c == t[j - 1]:
                cur[j] = prev[j - 1] + 1
                if cur[j] > best:
                    best = cur[j]
        prev = cur
    return best
''',
    tests=[["xabcdy", "zzabcdq"], ["abab", "baba"], ["abc", "def"], ["", ""], ["", "abc"], ["abc", ""], ["a", "a"], ["a", "b"],
           ["abcde", "abcde"], ["abcxyz", "xyzabc"], ["aaaa", "aa"], ["abcdefg", "gfedcba"], ["abcabcabc", "cabcab"]],
)
_r = rnd(7301)
_pl = "".join(_r.choice("abcd") for _ in range(300))
p["tests"] += [
    ["".join(_r.choice("abcd") for _ in range(1500)), "".join(_r.choice("abcd") for _ in range(1500))],
    [_rs(_r, "abcdefghijklmnopqrstuvwxyz", 1100, 1100) + _pl + _rs(_r, "xyz", 100, 100),
     _rs(_r, "qrstuvw", 700, 700) + _pl + _rs(_r, "abc", 500, 500)],
    ["a" * 1500, "a" * 1500],
    ["ab" * 750, "ba" * 750],
    ["a" * 1000 + "b" * 500, "b" * 500 + "a" * 1000],
]


def _brute_lcstr(s, t):
    best = 0
    for i in range(len(s)):
        for j in range(i + 1, len(s) + 1):
            if j - i > best and s[i:j] in t:
                best = j - i
    return best


def _v_lcstr(tests):
    for t in tests:
        s, u = t["args"]
        assert len(s) <= 1500 and len(u) <= 1500
        assert all("a" <= c <= "z" for c in s + u)


CHECKS["longest-common-substring-length"] = (
    _brute_lcstr, lambda r: [_rs(r, "abc", 0, 10), _rs(r, "abc", 0, 10)], "exact")
VALIDATE["longest-common-substring-length"] = _v_lcstr


p = add(
    id="equalize-strings-by-deletions", title="Make Two Strings Equal by Deleting", diff="Easy", topic="Dynamic Programming",
    fn="minDeletionsToEqual", params=[("word1", "string"), ("word2", "string")], ret="int", cmp="exact",
    desc="<p>In one move you may delete a single character from either <code>word1</code> or <code>word2</code>. Return the minimum number of moves needed to make the two strings identical.</p><p>Deleting everything from both strings always works, so an answer exists; two empty strings count as identical.</p><pre>word1 = \"sea\",  word2 = \"eat\"   ->  2   (delete 's' and 't', both become \"ea\")\nword1 = \"abc\",  word2 = \"xyz\"   ->  6</pre>",
    constraints=["0 &le; word1.length, word2.length &le; 1,500", "Both strings contain only lowercase English letters"],
    hints=["Whatever strings remain after all deletions must be equal. What can you say about that remaining string in relation to word1 and to word2?",
           "The remaining string is a subsequence of both words. To use as few deletions as possible, keep as many characters as possible.",
           "If the longest common subsequence has length L, the answer is <code>len(word1) + len(word2) - 2 * L</code>. Compute L with the usual table over prefixes."],
    editorial=["After the deletions the two strings are equal, so the surviving string is a common subsequence of both inputs. Every character of word1 outside it was deleted, as was every character of word2 outside it. If the survivor has length <code>k</code>, the number of deletions is <code>(m - k) + (n - k)</code>, which is smallest when <code>k</code> is as large as possible. So the task is exactly to find the longest common subsequence.",
               "Compute the LCS with <code>dp[i][j] = dp[i-1][j-1] + 1</code> when <code>word1[i-1] == word2[j-1]</code> and <code>max(dp[i-1][j], dp[i][j-1])</code> otherwise, keeping a single previous row to save memory. The answer is <code>m + n - 2 * dp[m][n]</code>. A direct search over which characters to delete is exponential."],
    time="O(m &middot; n)", space="O(n)",
    solution='''def minDeletionsToEqual(word1, word2):
    m, n = len(word1), len(word2)
    prev = [0] * (n + 1)
    for i in range(1, m + 1):
        cur = [0] * (n + 1)
        a = word1[i - 1]
        for j in range(1, n + 1):
            if a == word2[j - 1]:
                cur[j] = prev[j - 1] + 1
            else:
                cur[j] = cur[j - 1] if cur[j - 1] > prev[j] else prev[j]
        prev = cur
    return m + n - 2 * prev[n]
''',
    tests=[["sea", "eat"], ["abc", "xyz"], ["", ""], ["abc", ""], ["", "abcd"], ["a", "a"], ["a", "b"], ["leetcode", "etco"],
           ["abcde", "badce"], ["aaaa", "aa"], ["intention", "execution"], ["zzzz", "zz"]],
)
_r = rnd(7302)
p["tests"] += [
    [_rs(_r, "abcd", 1500, 1500), _rs(_r, "abcd", 1500, 1500)],
    [_rs(_r, "abcdefghijklmnopqrstuvwxyz", 1000, 1000), _rs(_r, "abcdefghijklmnopqrstuvwxyz", 800, 800)],
    ["a" * 1500, "a" * 700],
    ["ab" * 700, "ba" * 600],
]


def _brute_eqdel(a, b):
    sa, sb = _subseqs(a), _subseqs(b)
    return min(len(a) + len(b) - 2 * len(t) for t in sa & sb)


def _v_eqdel(tests):
    for t in tests:
        a, b = t["args"]
        assert len(a) <= 1500 and len(b) <= 1500
        assert all("a" <= c <= "z" for c in a + b)


CHECKS["equalize-strings-by-deletions"] = (
    _brute_eqdel, lambda r: [_rs(r, "abc", 0, 9), _rs(r, "abc", 0, 9)], "exact")
VALIDATE["equalize-strings-by-deletions"] = _v_eqdel


# ---------------------------------------------------------------- MEDIUM

p = add(
    id="longest-palindromic-subsequence-length", title="Longest Palindromic Subsequence", diff="Medium", topic="Dynamic Programming",
    fn="longestPalindromeSubseq", params=[("s", "string")], ret="int", cmp="exact",
    desc="<p>Given a string <code>s</code>, return the length of its longest <em>palindromic subsequence</em>: the longest sequence of characters that can be obtained by deleting zero or more characters of <code>s</code> (keeping the order of the rest) and that reads the same forwards and backwards.</p><p>Do not confuse this with a palindromic <em>substring</em>, which has to be contiguous.</p><pre>s = \"bbbab\"  ->  4   (\"bbbb\")\ns = \"cbbd\"   ->  2   (\"bb\")</pre>",
    constraints=["1 &le; s.length &le; 1,500", "s contains only lowercase English letters"],
    hints=["Look at the first and last characters of the string. If they are equal, can both be part of an optimal palindrome? What if they are different?",
           "Let P(i, j) be the answer for the piece s[i..j]. If s[i] == s[j] then P(i, j) = P(i+1, j-1) + 2, otherwise P(i, j) = max(P(i+1, j), P(i, j-1)). A single character gives P(i, i) = 1 and an empty piece gives 0.",
           "Fill the table by increasing interval length, or by decreasing i and increasing j. Row i only depends on row i+1, so one array plus one saved diagonal value is enough."],
    editorial=["Work on intervals. <code>P[i][j]</code> is the longest palindromic subsequence inside <code>s[i..j]</code>. If both end characters are equal they can wrap an optimal palindrome of the inside, giving <code>P[i+1][j-1] + 2</code>. If they differ, at least one of them is not used, so the best is the larger of dropping the left end or the right end.",
               "The table has about n&sup2;/2 useful cells, around 1.1 million at the limit. Iterate <code>i</code> from the end towards the start and <code>j</code> from <code>i+1</code> rightwards; keeping the value that sat on the diagonal before overwriting it reduces memory to O(n). An equivalent view: the answer equals the LCS of <code>s</code> and its reverse."],
    time="O(n&sup2;)", space="O(n)",
    solution='''def longestPalindromeSubseq(s):
    n = len(s)
    if n == 0:
        return 0
    dp = [0] * n
    for i in range(n - 1, -1, -1):
        dp[i] = 1
        diag = 0                      # value of P(i+1, j-1) for the current j
        for j in range(i + 1, n):
            keep = dp[j]              # P(i+1, j); becomes the diagonal for j+1
            if s[i] == s[j]:
                dp[j] = diag + 2
            else:
                dp[j] = keep if keep > dp[j - 1] else dp[j - 1]
            diag = keep
    return dp[n - 1]
''',
    tests=[["bbbab"], ["cbbd"], ["a"], ["aa"], ["ab"], ["abc"], ["aaaa"], ["abcba"], ["character"], ["agbdba"], ["abcdefgfedcba"],
           ["abacdfgdcaba"], ["abcabcabc"]],
)
_r = rnd(7303)
p["tests"] += [
    [_rs(_r, "abcd", 1500, 1500)],
    [_rs(_r, "abcdefghijklmnopqrstuvwxyz", 1500, 1500)],
    ["a" * 1500],
    ["ab" * 750],
    ["abcdefghijklmnopqrstuvwxyz" * 57],
]


def _brute_lps(s):
    n = len(s)
    best = 0
    for mask in range(1 << n):
        t = "".join(s[i] for i in range(n) if mask >> i & 1)
        if len(t) > best and _is_pal(t):
            best = len(t)
    return best


def _v_lps(tests):
    for t in tests:
        s = t["args"][0]
        assert 1 <= len(s) <= 1500 and all("a" <= c <= "z" for c in s)


CHECKS["longest-palindromic-subsequence-length"] = (
    _brute_lps, lambda r: [_rs(r, "abc", 1, 11)], "exact")
VALIDATE["longest-palindromic-subsequence-length"] = _v_lps


p = add(
    id="minimum-ascii-delete-sum-equal-strings", title="Minimum ASCII Delete Sum for Two Strings", diff="Medium", topic="Dynamic Programming",
    fn="minimumDeleteSum", params=[("s1", "string"), ("s2", "string")], ret="int", cmp="exact",
    desc="<p>You may delete characters from <code>s1</code> and from <code>s2</code>. Deleting a character costs its ASCII code (for example <code>'a'</code> costs 97 and <code>'z'</code> costs 122). Return the smallest total cost that makes the two strings equal.</p><p>Deleting every character from both strings is always possible, and two empty strings are equal.</p><pre>s1 = \"sea\",  s2 = \"eat\"  ->  231   (delete 's' = 115 and 't' = 116)\ns1 = \"ab\",   s2 = \"b\"    ->  97    (delete 'a')</pre>",
    constraints=["0 &le; s1.length, s2.length &le; 1,000", "Both strings contain only lowercase English letters"],
    hints=["After the deletions the two strings are equal, so what remains is a common subsequence of both. Everything not in it must be deleted.",
           "Total cost = (sum of ASCII of s1) + (sum of ASCII of s2) - 2 * (ASCII sum of the kept subsequence). So minimising the cost means maximising the ASCII sum of a common subsequence.",
           "Run the longest-common-subsequence table, but when two characters match add their ASCII code instead of 1. Note that the heaviest common subsequence is not always the longest one."],
    editorial=["Whatever survives is a common subsequence <code>K</code>. The cost paid is <code>sum(s1) + sum(s2) - 2 * sum(K)</code>, so we want the common subsequence of maximum <em>weight</em>, where each character weighs its ASCII code. A longest common subsequence is not necessarily the heaviest: for <code>s1 = \"az\"</code> and <code>s2 = \"za\"</code> any single kept letter works but keeping <code>'z'</code> is better than keeping <code>'a'</code>.",
               "Use the LCS recurrence with weights: <code>W[i][j] = W[i-1][j-1] + ord(s1[i-1])</code> if the characters match, else <code>max(W[i-1][j], W[i][j-1])</code>. The answer is <code>total - 2 * W[m][n]</code>. With one rolling row this takes O(n) memory and about a million cell updates at the limit."],
    time="O(m &middot; n)", space="O(n)",
    solution='''def minimumDeleteSum(s1, s2):
    m, n = len(s1), len(s2)
    prev = [0] * (n + 1)
    for i in range(1, m + 1):
        cur = [0] * (n + 1)
        a = s1[i - 1]
        w = ord(a)
        for j in range(1, n + 1):
            if a == s2[j - 1]:
                cur[j] = prev[j - 1] + w
            else:
                cur[j] = cur[j - 1] if cur[j - 1] > prev[j] else prev[j]
        prev = cur
    total = sum(map(ord, s1)) + sum(map(ord, s2))
    return total - 2 * prev[n]
''',
    tests=[["sea", "eat"], ["delete", "leet"], ["ab", "b"], ["", ""], ["a", ""], ["", "zz"], ["a", "a"], ["az", "za"], ["abc", "xyz"],
           ["aaa", "a"], ["zebra", "ebr"], ["baab", "abba"]],
)
_r = rnd(7304)
p["tests"] += [
    [_rs(_r, "abcd", 1000, 1000), _rs(_r, "abcd", 1000, 1000)],
    [_rs(_r, "abcdefghijklmnopqrstuvwxyz", 1000, 1000), _rs(_r, "abcdefghijklmnopqrstuvwxyz", 900, 900)],
    ["z" * 1000, "a" * 1000],
    ["za" * 500, "az" * 500],
]


def _brute_ascii(a, b):
    sa, sb = _subseqs(a), _subseqs(b)
    ta, tb = sum(map(ord, a)), sum(map(ord, b))
    return min(ta + tb - 2 * sum(map(ord, t)) for t in sa & sb)


def _v_ascii(tests):
    for t in tests:
        a, b = t["args"]
        assert len(a) <= 1000 and len(b) <= 1000
        assert all("a" <= c <= "z" for c in a + b)


CHECKS["minimum-ascii-delete-sum-equal-strings"] = (
    _brute_ascii, lambda r: [_rs(r, "abz", 0, 9), _rs(r, "abz", 0, 9)], "exact")
VALIDATE["minimum-ascii-delete-sum-equal-strings"] = _v_ascii


p = add(
    id="interleaving-string-check", title="Interleaving String", diff="Medium", topic="Dynamic Programming",
    fn="isInterleave", params=[("s1", "string"), ("s2", "string"), ("s3", "string")], ret="bool", cmp="exact",
    desc="<p>Say that <code>s3</code> is an <em>interleaving</em> of <code>s1</code> and <code>s2</code> if its characters can be split into two groups, one reading exactly <code>s1</code> and the other exactly <code>s2</code> when each group is read from left to right. The relative order inside <code>s1</code> and inside <code>s2</code> must be preserved, but the two groups may alternate in any pattern.</p><p>Return <code>true</code> if <code>s3</code> is an interleaving of <code>s1</code> and <code>s2</code>, otherwise <code>false</code>.</p><pre>s1 = \"abc\", s2 = \"de\", s3 = \"adbec\"  ->  true\ns1 = \"ab\",  s2 = \"ba\", s3 = \"abab\"   ->  true\ns1 = \"ab\",  s2 = \"cd\", s3 = \"acbd\"   ->  true\ns1 = \"ab\",  s2 = \"cd\", s3 = \"adbc\"   ->  false</pre>",
    constraints=["0 &le; s1.length, s2.length &le; 500", "0 &le; s3.length &le; 1,000", "All three strings contain only lowercase English letters"],
    hints=["If the lengths do not add up the answer is false. Otherwise, the next character of s3 must come either from the front of s1 or from the front of s2.",
           "Let F(i, j) say whether the first i characters of s1 and the first j characters of s2 can interleave into the first i + j characters of s3. Character i + j of s3 must equal s1[i-1] (coming from F(i-1, j)) or s2[j-1] (coming from F(i, j-1)).",
           "Fill the table row by row starting from F(0, 0) = true. Plain recursion without caching is exponential because many (i, j) pairs repeat; memoising or tabulating makes it O(m &middot; n)."],
    editorial=["First check <code>len(s1) + len(s2) == len(s3)</code>. Then define <code>F[i][j]</code> as true when <code>s3[:i+j]</code> is an interleaving of <code>s1[:i]</code> and <code>s2[:j]</code>. The last character <code>s3[i+j-1]</code> was taken from either string: from <code>s1</code> if <code>F[i-1][j]</code> holds and <code>s1[i-1] == s3[i+j-1]</code>, or from <code>s2</code> if <code>F[i][j-1]</code> holds and <code>s2[j-1] == s3[i+j-1]</code>.",
               "The first row and first column use only one string at a time. Only the previous row is needed, so a single boolean array of length n+1 is enough. A backtracking search that tries both options at every character takes exponential time when many characters repeat, for example all <code>a</code>s, which is exactly what the table avoids."],
    time="O(m &middot; n)", space="O(n)",
    solution='''def isInterleave(s1, s2, s3):
    m, n = len(s1), len(s2)
    if m + n != len(s3):
        return False
    dp = [False] * (n + 1)
    dp[0] = True
    for j in range(1, n + 1):
        dp[j] = dp[j - 1] and s2[j - 1] == s3[j - 1]
    for i in range(1, m + 1):
        dp[0] = dp[0] and s1[i - 1] == s3[i - 1]
        for j in range(1, n + 1):
            c = s3[i + j - 1]
            dp[j] = (dp[j] and s1[i - 1] == c) or (dp[j - 1] and s2[j - 1] == c)
    return dp[n]
''',
    tests=[["abc", "de", "adbec"], ["ab", "ba", "abab"], ["ab", "cd", "acbd"], ["ab", "cd", "adbc"], ["", "", ""], ["a", "", "a"],
           ["", "b", "b"], ["", "b", "c"], ["a", "b", "abc"], ["aabcc", "dbbca", "aadbbcbcac"], ["aabcc", "dbbca", "aadbbbaccc"],
           ["aa", "aa", "aaaa"], ["aa", "ab", "aaba"], ["ab", "ab", "aabb"]],
)
_r = rnd(7305)


def _interleave(r, a, b):
    out = []
    i = j = 0
    while i < len(a) or j < len(b):
        if j >= len(b) or (i < len(a) and r.random() < 0.5):
            out.append(a[i]); i += 1
        else:
            out.append(b[j]); j += 1
    return "".join(out)


def _swap_two(r, s):
    s = list(s)
    i, j = r.randrange(len(s)), r.randrange(len(s))
    s[i], s[j] = s[j], s[i]
    return "".join(s)


_a, _b = _rs(_r, "ab", 500, 500), _rs(_r, "ab", 500, 500)
_c = _interleave(_r, _a, _b)
_c2 = _c[:-2] + _c[-1] + _c[-2]
_a3, _b3 = _rs(_r, "abc", 480, 480), _rs(_r, "abc", 500, 500)
_c3 = _interleave(_r, _a3, _b3)
p["tests"] += [
    [_a, _b, _c],
    [_a, _b, _c2],
    [_a3, _b3, _c3],
    [_a3, _b3, _swap_two(_r, _c3)],
    ["a" * 500, "a" * 500, "a" * 1000],
    ["a" * 500, "a" * 499 + "b", "a" * 999 + "b"],
    ["a" * 500, "a" * 499 + "b", "a" * 998 + "ba"],
    ["ab" * 250, "ab" * 250, "ab" * 500],
]


def _brute_interleave(s1, s2, s3):
    m, n = len(s1), len(s2)
    if m + n != len(s3):
        return False
    for pos in combinations(range(m + n), m):
        chosen = set(pos)
        rest = [k for k in range(m + n) if k not in chosen]
        if "".join(s3[k] for k in pos) == s1 and "".join(s3[k] for k in rest) == s2:
            return True
    return False


def _gen_interleave(r):
    a, b = _rs(r, "ab", 0, 5), _rs(r, "ab", 0, 5)
    mode = r.random()
    if mode < 0.5:
        c = _interleave(r, a, b)
        if r.random() < 0.4 and c:
            c = _swap_two(r, c)
    elif mode < 0.9:
        c = _rs(r, "ab", len(a) + len(b), len(a) + len(b))
    else:
        c = _rs(r, "ab", 0, 10)
    return [a, b, c]


def _v_interleave(tests):
    for t in tests:
        s1, s2, s3 = t["args"]
        assert len(s1) <= 500 and len(s2) <= 500 and len(s3) <= 1000
        assert all("a" <= c <= "z" for c in s1 + s2 + s3)
    assert any(t["expected"] for t in tests) and any(not t["expected"] for t in tests)


CHECKS["interleaving-string-check"] = (_brute_interleave, _gen_interleave, "exact")
VALIDATE["interleaving-string-check"] = _v_interleave


p = add(
    id="wildcard-pattern-matching", title="Wildcard Pattern Matching", diff="Medium", topic="Dynamic Programming",
    fn="isWildcardMatch", params=[("s", "string"), ("p", "string")], ret="bool", cmp="exact",
    desc="<p>Implement matching of a text <code>s</code> against a pattern <code>p</code> that may contain two special characters:</p><ul><li><code>?</code> matches exactly one arbitrary character.</li><li><code>*</code> matches any sequence of characters, including the empty sequence.</li></ul><p>Every other character in the pattern matches only itself. The match must cover the <b>entire</b> text, not just a part of it. Return <code>true</code> if the pattern matches the whole text.</p><pre>s = \"adceb\", p = \"*a*b\"  ->  true\ns = \"abc\",   p = \"a?d\"   ->  false\ns = \"\",      p = \"***\"   ->  true</pre>",
    constraints=["0 &le; s.length, p.length &le; 2,000", "s contains only lowercase English letters", "p contains only lowercase English letters, '?' and '*'"],
    hints=["Compare the first character of the pattern with the first character of the text. Ordinary letters and '?' consume exactly one character each. The tricky one is '*'.",
           "Let M(i, j) say whether s[i:] matches p[j:]. For '*' there are two choices: let it match nothing (go to M(i, j+1)) or let it swallow one more character of s (go to M(i+1, j)).",
           "A table of (m+1) x (n+1) booleans solves it in O(m &middot; n). A greedy alternative also works: remember the position of the latest '*' and, after a mismatch, retry by letting that '*' absorb one more character."],
    editorial=["Dynamic programming: <code>M[i][j]</code> is true if <code>s[i:]</code> matches <code>p[j:]</code>. The base case is <code>M[m][n] = true</code>, and <code>M[m][j]</code> is true only when the rest of the pattern consists solely of stars. For <code>p[j] == '*'</code>, <code>M[i][j] = M[i][j+1] or M[i+1][j]</code> (star matches empty, or star takes one more character). Otherwise <code>M[i][j] = (p[j] == '?' or p[j] == s[i]) and M[i+1][j+1]</code>.",
               "The greedy method is lighter on memory and usually much faster. Walk both strings in step while characters match or the pattern has '?'. When you meet a '*', record its position and the current text index, then continue as if it matched nothing. On a later mismatch, return to the recorded star, let it consume one more character, and resume. Only the most recent star ever needs to be retried, because earlier stars could already absorb anything. After the text is used up, the rest of the pattern must be all stars. Worst-case time is O(m &middot; n), typical time is near linear. Plain recursion without caching can be exponential on patterns with many stars."],
    time="O(m &middot; n)", space="O(1)",
    solution='''def isWildcardMatch(s, p):
    i = j = 0
    m, n = len(s), len(p)
    star = -1          # index of the latest '*' in p
    mark = 0           # index in s where that star started absorbing
    while i < m:
        if j < n and (p[j] == '?' or p[j] == s[i]):
            i += 1
            j += 1
        elif j < n and p[j] == '*':
            star = j
            mark = i
            j += 1
        elif star != -1:
            j = star + 1
            mark += 1
            i = mark
        else:
            return False
    while j < n and p[j] == '*':
        j += 1
    return j == n
''',
    tests=[["adceb", "*a*b"], ["abc", "a?d"], ["", "***"], ["", ""], ["", "?"], ["a", ""], ["aa", "a"], ["aa", "*"], ["cb", "?a"],
           ["acdcb", "a*c?b"], ["abcde", "a*e"], ["abcde", "*?*?*?*?*?*"], ["abcde", "*?*?*?*?*?*?"], ["mississippi", "m??*ss*?i*pi"],
           ["abc", "abc*"], ["abc", "*abcd"], ["aaaa", "***a"], ["ab", "?*"], ["b", "*a*"]],
)
_r = rnd(7306)


def _wild_from_text(r, s, p_star, p_q):
    out = []
    i = 0
    while i < len(s):
        x = r.random()
        if x < p_star:
            out.append("*")
            i += r.randint(0, 5)
        elif x < p_star + p_q:
            out.append("?")
            i += 1
        else:
            out.append(s[i])
            i += 1
    return "".join(out)


_s1 = _rs(_r, "ab", 1990, 1990)
_s2 = _rs(_r, "abc", 2000, 2000)
p["tests"] += [
    ["a" * 2000, "*" * 1000 + "a" * 3],
    ["a" * 2000, "*a" * 999 + "b"],
    ["a" * 1999 + "b", "*a" * 700 + "*b"],
    ["a" * 1000 + "b" * 1000, "*" + "a*" * 300 + "b" * 5],
    [_s1, _wild_from_text(_r, _s1, 0.02, 0.05)],
    [_s1, _wild_from_text(_r, _s1, 0.02, 0.05)[:-1] + "c"],
    [_s2, _wild_from_text(_r, _s2, 0.03, 0.1)],
    [_s2, "?" * 2000],
    [_s2, "?" * 1999],
    ["ab" * 1000, "*ab" * 600 + "*"],
]


def _brute_wild(s, p):
    def go(s, p):
        if not p:
            return not s
        if p[0] == "*":
            return any(go(s[k:], p[1:]) for k in range(len(s) + 1))
        return bool(s) and (p[0] == "?" or p[0] == s[0]) and go(s[1:], p[1:])
    return go(s, p)


def _gen_wild(r):
    s = _rs(r, "ab", 0, 8)
    if r.random() < 0.6:
        p = _wild_from_text(r, s, 0.25, 0.2)
        if r.random() < 0.3:
            p += r.choice("ab*?")
    else:
        p = _rs(r, "ab?*", 0, 7)
    return [s, p]


def _v_wild(tests):
    for t in tests:
        s, p = t["args"]
        assert len(s) <= 2000 and len(p) <= 2000
        assert all("a" <= c <= "z" for c in s)
        assert all(("a" <= c <= "z") or c in "?*" for c in p)
    assert any(t["expected"] for t in tests) and any(not t["expected"] for t in tests)


CHECKS["wildcard-pattern-matching"] = (_brute_wild, _gen_wild, "exact")
VALIDATE["wildcard-pattern-matching"] = _v_wild


p = add(
    id="longest-repeating-subsequence-distinct-positions", title="Longest Repeating Subsequence", diff="Medium", topic="Dynamic Programming",
    fn="longestRepeatingSubsequence", params=[("s", "string")], ret="int", cmp="exact",
    desc="<p>Find the length of the longest string <code>t</code> that occurs <em>twice</em> as a subsequence of <code>s</code>, where the two occurrences never use the same index of <code>s</code> for the same character of <code>t</code>.</p><p>Formally, <code>t</code> of length <code>L</code> qualifies if there are two index sequences <code>a<sub>1</sub> &lt; ... &lt; a<sub>L</sub></code> and <code>b<sub>1</sub> &lt; ... &lt; b<sub>L</sub></code> with <code>s[a<sub>k</sub>] = s[b<sub>k</sub>] = t[k]</code> and <code>a<sub>k</sub> &ne; b<sub>k</sub></code> for every <code>k</code>. The two sequences may share indices in different positions of <code>t</code>.</p><pre>s = \"aabebcdd\"  ->  3   (\"abd\")\ns = \"axxxy\"     ->  2   (\"xx\")\ns = \"abc\"       ->  0</pre>",
    constraints=["1 &le; s.length &le; 1,500", "s contains only lowercase English letters"],
    hints=["Imagine writing s twice, one copy above the other, and drawing lines between equal characters. Which pairs of positions are not allowed to be joined?",
           "This is the longest common subsequence of s with itself, except that position i of the first copy cannot be matched with position i of the second copy.",
           "Use the LCS table dp[i][j] over prefixes of s and s. On a match, only extend the diagonal when i != j; otherwise take the better of dp[i-1][j] and dp[i][j-1]."],
    editorial=["Compare <code>s</code> against a second copy of itself using the standard LCS table. If the two chosen indices <code>i</code> and <code>j</code> were allowed to be equal, the answer would trivially be <code>len(s)</code>, because the whole string matches itself. Forbidding <code>i == j</code> exactly encodes the rule that the two occurrences must use different indices for each character.",
               "So <code>dp[i][j] = dp[i-1][j-1] + 1</code> when <code>s[i-1] == s[j-1]</code> and <code>i != j</code>; otherwise <code>dp[i][j] = max(dp[i-1][j], dp[i][j-1])</code>. Because the index sequences are strictly increasing, each step of the LCS pairs index <code>a<sub>k</sub></code> with <code>b<sub>k</sub></code>, and the condition <code>i != j</code> is the requirement <code>a<sub>k</sub> &ne; b<sub>k</sub></code>. The answer is <code>dp[n][n]</code>, computed with a single rolling row in O(n) memory."],
    time="O(n&sup2;)", space="O(n)",
    solution='''def longestRepeatingSubsequence(s):
    n = len(s)
    prev = [0] * (n + 1)
    for i in range(1, n + 1):
        cur = [0] * (n + 1)
        c = s[i - 1]
        for j in range(1, n + 1):
            if c == s[j - 1] and i != j:
                cur[j] = prev[j - 1] + 1
            else:
                cur[j] = cur[j - 1] if cur[j - 1] > prev[j] else prev[j]
        prev = cur
    return prev[n]
''',
    tests=[["aabebcdd"], ["axxxy"], ["abc"], ["a"], ["aa"], ["aaa"], ["aaaa"], ["abab"], ["abcabc"], ["aabb"], ["abacbc"], ["zzzzzzz"],
           ["abcdefgabcdefg"]],
)
_r = rnd(7307)
_half = _rs(_r, "abcdefghij", 700, 700)
p["tests"] += [
    [_rs(_r, "abcd", 1500, 1500)],
    [_rs(_r, "abcdefghijklmnopqrstuvwxyz", 1500, 1500)],
    ["a" * 1500],
    [_half + _half],
    ["abcdefghijklmnopqrstuvwxyz" * 57],
]


def _brute_lrs(s):
    n = len(s)
    for L in range(n // 1, 0, -1):
        groups = {}
        for idx in combinations(range(n), L):
            groups.setdefault("".join(s[i] for i in idx), []).append(idx)
        for tups in groups.values():
            for x in range(len(tups)):
                for y in range(x + 1, len(tups)):
                    if all(a != b for a, b in zip(tups[x], tups[y])):
                        return L
    return 0


def _v_lrs(tests):
    for t in tests:
        s = t["args"][0]
        assert 1 <= len(s) <= 1500 and all("a" <= c <= "z" for c in s)


CHECKS["longest-repeating-subsequence-distinct-positions"] = (
    _brute_lrs, lambda r: [_rs(r, "abc", 1, 9)], "exact")
VALIDATE["longest-repeating-subsequence-distinct-positions"] = _v_lrs


p = add(
    id="longest-common-subsequence-of-three-strings", title="Longest Common Subsequence of Three Strings", diff="Medium", topic="Dynamic Programming",
    fn="lcsOfThree", params=[("a", "string"), ("b", "string"), ("c", "string")], ret="int", cmp="exact",
    desc="<p>Given three strings <code>a</code>, <code>b</code> and <code>c</code>, return the length of the longest string that is a subsequence of <b>all three</b> of them. A subsequence keeps the relative order of the characters it takes but may skip characters.</p><p>If the three strings have no common character, return <code>0</code>.</p><pre>a = \"abcde\", b = \"ace\",  c = \"aecd\"  ->  2   (\"ac\" or \"ae\")\na = \"geeks\", b = \"geeksfor\", c = \"geeksforgeeks\"  ->  5</pre>",
    constraints=["0 &le; a.length, b.length, c.length &le; 100", "All three strings contain only lowercase English letters"],
    hints=["The two-string LCS looks at one position in each string. What would a state look like with three strings?",
           "Let T(i, j, k) be the answer for the first i characters of a, the first j of b and the first k of c. If all three last characters are equal, T = T(i-1, j-1, k-1) + 1.",
           "Otherwise at least one of the three last characters is not used by the best answer, so take the maximum of T(i-1, j, k), T(i, j-1, k) and T(i, j, k-1). Fill the cube layer by layer over i."],
    editorial=["Extend the pairwise recurrence to three dimensions. <code>T[i][j][k]</code> is the LCS length of the three prefixes. When <code>a[i-1] == b[j-1] == c[k-1]</code> the three characters can be matched together: <code>T[i-1][j-1][k-1] + 1</code>. When they are not all equal, an optimal common subsequence cannot end with all three of them, so one of them is dropped, and the answer is the maximum of the three states obtained by dropping one last character.",
               "The cube has up to 101<sup>3</sup>, about one million, cells. Layer <code>i</code> depends only on layer <code>i-1</code> and itself, so two 2-D layers are enough. Note that computing the LCS of two strings and then comparing the result with the third string is <em>not</em> valid: the best pairwise subsequence may be unrelated to the best three-way one."],
    time="O(|a| &middot; |b| &middot; |c|)", space="O(|b| &middot; |c|)",
    solution='''def lcsOfThree(a, b, c):
    nb, nc = len(b), len(c)
    prev = [[0] * (nc + 1) for _ in range(nb + 1)]
    for i in range(1, len(a) + 1):
        cur = [[0] * (nc + 1) for _ in range(nb + 1)]
        x = a[i - 1]
        for j in range(1, nb + 1):
            y = b[j - 1]
            row, prow, crow = cur[j], prev[j], cur[j - 1]
            pdiag = prev[j - 1]
            for k in range(1, nc + 1):
                if x == y == c[k - 1]:
                    row[k] = pdiag[k - 1] + 1
                else:
                    best = prow[k]
                    if crow[k] > best:
                        best = crow[k]
                    if row[k - 1] > best:
                        best = row[k - 1]
                    row[k] = best
        prev = cur
    return prev[nb][nc]
''',
    tests=[["abcde", "ace", "aecd"], ["geeks", "geeksfor", "geeksforgeeks"], ["abc", "abc", "abc"], ["abc", "def", "ghi"], ["", "", ""],
           ["abc", "", "abc"], ["a", "a", "a"], ["a", "a", "b"], ["abcd", "abcd", "dcba"], ["aaaa", "aa", "aaa"], ["abcabc", "bcaabc", "cabcab"],
           ["xyz", "xzy", "yxz"]],
)
_r = rnd(7308)
p["tests"] += [
    [_rs(_r, "abc", 100, 100), _rs(_r, "abc", 100, 100), _rs(_r, "abc", 100, 100)],
    [_rs(_r, "abcdefghijklmnopqrstuvwxyz", 100, 100), _rs(_r, "abcdefghijklmnopqrstuvwxyz", 100, 100), _rs(_r, "abcdefghijklmnopqrstuvwxyz", 100, 100)],
    ["a" * 100, "a" * 100, "a" * 100],
    ["ab" * 50, "ba" * 50, "ab" * 50],
    [_rs(_r, "ab", 100, 100), _rs(_r, "ab", 60, 60), _rs(_r, "ab", 90, 90)],
]


def _brute_lcs3(a, b, c):
    common = _subseqs(a) & _subseqs(b) & _subseqs(c)
    return max(len(t) for t in common)


def _v_lcs3(tests):
    for t in tests:
        assert all(len(x) <= 100 and all("a" <= ch <= "z" for ch in x) for x in t["args"])


CHECKS["longest-common-subsequence-of-three-strings"] = (
    _brute_lcs3, lambda r: [_rs(r, "abc", 0, 8), _rs(r, "abc", 0, 8), _rs(r, "abc", 0, 8)], "exact")
VALIDATE["longest-common-subsequence-of-three-strings"] = _v_lcs3


# ---------------------------------------------------------------- HARD

p = add(
    id="count-distinct-palindromic-subsequences", title="Count Distinct Palindromic Subsequences", diff="Hard", topic="Dynamic Programming",
    fn="countPalindromicSubsequences", params=[("s", "string")], ret="int", cmp="exact",
    desc="<p>Given a string <code>s</code> made only of the letters <code>a</code>, <code>b</code>, <code>c</code> and <code>d</code>, count the <b>distinct</b> non-empty palindromic strings that can be obtained as a subsequence of <code>s</code>. Two subsequences that spell the same string count once, even if they use different indices.</p><p>The count can be huge, so return it modulo <code>1,000,000,007</code>.</p><pre>s = \"bccb\"  ->  6    (b, c, bb, cc, bcb, bccb)\ns = \"aaa\"   ->  3    (a, aa, aaa)\ns = \"abcd\"  ->  4</pre>",
    constraints=["1 &le; s.length &le; 1,000", "s contains only the characters 'a', 'b', 'c' and 'd'"],
    hints=["Count palindromes inside intervals: D(i, j) is the number of distinct non-empty palindromic subsequences of s[i..j]. If the end characters differ, use inclusion-exclusion over the two shorter intervals.",
           "If the end characters are equal to c, every palindrome that starts and ends with c has the form c + X + c where X is empty or a palindrome from the inside, plus the single 'c'. Duplicates arise when c also occurs inside, so look at the first and last occurrence of c strictly inside the interval.",
           "Let l and r be the first and last c strictly inside (i, j). None inside: 2 * D(i+1, j-1) + 2. Exactly one (l == r): 2 * D(i+1, j-1) + 1. Two or more: 2 * D(i+1, j-1) - D(l+1, r-1). Precompute previous/next occurrence arrays for O(1) lookup."],
    editorial=["If <code>s[i] != s[j]</code>, a palindrome in <code>s[i..j]</code> either avoids the left end or avoids the right end, so by inclusion-exclusion <code>D[i][j] = D[i+1][j] + D[i][j-1] - D[i+1][j-1]</code>.",
               "If <code>s[i] == s[j] == c</code>, the distinct palindromes of <code>s[i..j]</code> are the ones that already exist strictly inside, counted by <code>D[i+1][j-1]</code>, plus new ones that wrap an inside palindrome in c: one string <code>c X c</code> for every inside palindrome <code>X</code>, and also <code>c</code> and <code>cc</code> (the empty <code>X</code>). That gives <code>2 * D[i+1][j-1] + 2</code> candidates, but some of them may already be present inside. Let <code>l</code> and <code>r</code> be the first and last occurrences of c strictly between <code>i</code> and <code>j</code>. If there is none, nothing is double counted: <code>2 * D[i+1][j-1] + 2</code>. If there is exactly one, the string <code>c</code> is already inside: <code>2 * D[i+1][j-1] + 1</code>. If there are two or more, both <code>c</code> and <code>cc</code> are already inside, and a string <code>c X c</code> is already inside exactly when <code>X</code> can be found between <code>l</code> and <code>r</code>, so subtract <code>D[l+1][r-1]</code> and drop the +2: <code>2 * D[i+1][j-1] - D[l+1][r-1]</code>.",
               "Precompute for every index the next and previous index holding the same letter so each cell costs O(1). Total time is O(n&sup2;) with an n &times; n table (about a million cells), taking all values modulo 10<sup>9</sup>+7. Enumerating subsequences and inserting them into a set is exponential."],
    time="O(n&sup2;)", space="O(n&sup2;)",
    solution='''def countPalindromicSubsequences(s):
    MOD = 10 ** 9 + 7
    n = len(s)
    prv = [-1] * n      # previous index with the same letter
    nxt = [n] * n       # next index with the same letter
    last = {}
    for i in range(n):
        prv[i] = last.get(s[i], -1)
        last[s[i]] = i
    last = {}
    for i in range(n - 1, -1, -1):
        nxt[i] = last.get(s[i], n)
        last[s[i]] = i
    dp = [[0] * n for _ in range(n)]
    for i in range(n):
        dp[i][i] = 1
    for length in range(2, n + 1):
        for i in range(n - length + 1):
            j = i + length - 1
            inner = dp[i + 1][j - 1]
            if s[i] != s[j]:
                v = dp[i + 1][j] + dp[i][j - 1] - inner
            else:
                l, r = nxt[i], prv[j]
                if l > r:
                    v = 2 * inner + 2
                elif l == r:
                    v = 2 * inner + 1
                else:
                    v = 2 * inner - dp[l + 1][r - 1]
            dp[i][j] = v % MOD
    return dp[0][n - 1]
''',
    tests=[["bccb"], ["aaa"], ["abcd"], ["a"], ["ab"], ["aa"], ["aba"], ["abba"], ["abcdbbcadcbad"],
           ["abcdcba"], ["aabbaabb"], ["dcbaabcd"], ["abacabad"]],
)
_r = rnd(7309)
p["tests"] += [
    [_rs(_r, "abcd", 1000, 1000)],
    [_rs(_r, "abcd", 1000, 1000)],
    [_rs(_r, "ab", 1000, 1000)],
    ["a" * 1000],
    ["abcd" * 250],
    ["ab" * 500],
    [_rs(_r, "abcd", 400, 400) + "abcd" * 50],
]


def _brute_cdps(s):
    n = len(s)
    seen = set()
    for mask in range(1, 1 << n):
        t = "".join(s[i] for i in range(n) if mask >> i & 1)
        if _is_pal(t):
            seen.add(t)
    return len(seen) % MOD


def _v_cdps(tests):
    for t in tests:
        s = t["args"][0]
        assert 1 <= len(s) <= 1000 and set(s) <= set("abcd")


CHECKS["count-distinct-palindromic-subsequences"] = (
    _brute_cdps, lambda r: [_rs(r, "abcd" if r.random() < 0.5 else "ab", 1, 12)], "exact")
VALIDATE["count-distinct-palindromic-subsequences"] = _v_cdps


p = add(
    id="scramble-string-check", title="Scramble String", diff="Hard", topic="Dynamic Programming",
    fn="isScramble", params=[("s1", "string"), ("s2", "string")], ret="bool", cmp="exact",
    desc="<p>A string can be <em>scrambled</em> with this recursive procedure. If the string has length 1, stop. Otherwise cut it at some position into two non-empty parts <code>x</code> and <code>y</code>, optionally swap them so the string becomes <code>y + x</code> instead of <code>x + y</code>, and then apply the same procedure independently to each of the two parts (each part may use a different cut and a different swap decision).</p><p>Given two strings <code>s1</code> and <code>s2</code> of the same length, return <code>true</code> if <code>s2</code> can be produced from <code>s1</code> by some sequence of such choices.</p><pre>s1 = \"great\", s2 = \"rgeat\"  ->  true\ns1 = \"abcde\", s2 = \"caebd\"  ->  false\ns1 = \"a\",     s2 = \"a\"      ->  true</pre>",
    constraints=["1 &le; s1.length &le; 40", "s2.length == s1.length", "Both strings contain only lowercase English letters"],
    hints=["If s2 is a scramble of s1, then at the top-level cut each half of s1 matches some block of s2 as a scramble. Which blocks of s2 can that be?",
           "For a cut of length k there are two possibilities: no swap (the first k characters of s1 against the first k of s2, the rest against the rest) or swap (the first k of s1 against the <em>last</em> k of s2, the rest against the first part).",
           "Memoise on (start in s1, start in s2, length). Prune quickly: two blocks can only be scrambles if they contain exactly the same multiset of letters, and equal blocks are trivially scrambles."],
    editorial=["Let <code>S(i, j, L)</code> be true when <code>s1[i:i+L]</code> can be scrambled into <code>s2[j:j+L]</code>. A block of length 1 matches if the characters are equal. For longer blocks, try every cut <code>k</code> from 1 to <code>L-1</code>. Without a swap we need <code>S(i, j, k)</code> and <code>S(i+k, j+k, L-k)</code>. With a swap the first part of s1 lands at the end of s2, so we need <code>S(i, j+L-k, k)</code> and <code>S(i+k, j, L-k)</code>.",
               "There are about n<sup>3</sup>/3 states and each tries up to n cuts, so the time is O(n<sup>4</sup>), which is tiny for n &le; 40. Without memoisation the same sub-blocks are re-solved over and over and the search is exponential. Cheap pruning makes it much faster in practice: if the two blocks are identical return true immediately, and if their sorted letters differ return false, since scrambling only rearranges characters."],
    time="O(n<sup>4</sup>)", space="O(n<sup>3</sup>)",
    solution='''def isScramble(s1, s2):
    n = len(s1)
    if n != len(s2):
        return False
    memo = {}

    def go(i, j, L):
        key = (i, j, L)
        if key in memo:
            return memo[key]
        a = s1[i:i + L]
        b = s2[j:j + L]
        if a == b:
            res = True
        elif sorted(a) != sorted(b):
            res = False
        else:
            res = False
            for k in range(1, L):
                if go(i, j, k) and go(i + k, j + k, L - k):
                    res = True
                    break
                if go(i, j + L - k, k) and go(i + k, j, L - k):
                    res = True
                    break
        memo[key] = res
        return res

    return go(0, 0, n)
''',
    tests=[["great", "rgeat"], ["abcde", "caebd"], ["a", "a"], ["a", "b"], ["ab", "ba"], ["ab", "ab"], ["abc", "bca"], ["abc", "acb"],
           ["abcd", "bdac"], ["abcdbdacbdac", "bdacabcdbdac"], ["aabb", "abab"], ["abcdefgh", "hgfedcba"], ["abcdefgh", "badcfehg"],
           ["abcdefgh", "ghabcdef"]],
)
_r = rnd(7310)


def _make_scramble(r, s):
    if len(s) <= 1:
        return s
    k = r.randint(1, len(s) - 1)
    x, y = _make_scramble(r, s[:k]), _make_scramble(r, s[k:])
    return x + y if r.random() < 0.5 else y + x


_big = _rs(_r, "abcdefghijklmnopqrstuvwxyz", 40, 40)
_dup = _rs(_r, "abc", 40, 40)
_dup2 = _rs(_r, "ab", 40, 40)
_sc = _make_scramble(_r, _big)
_sc_dup = _make_scramble(_r, _dup)
_sc_dup2 = _make_scramble(_r, _dup2)


def _adj_swap(r, s):
    s = list(s)
    i = r.randrange(len(s) - 1)
    s[i], s[i + 1] = s[i + 1], s[i]
    return "".join(s)


p["tests"] += [
    [_big, _sc],
    [_big, _swap_two(_r, _sc)],
    [_dup, _sc_dup],
    [_dup, _adj_swap(_r, _sc_dup)],
    [_dup2, _sc_dup2],
    [_dup2, _adj_swap(_r, _sc_dup2)],
    ["ab" * 20, "ba" * 20],
    ["a" * 40, "a" * 40],
    ["a" * 39 + "b", "b" + "a" * 39],
    ["a" * 20 + "b" * 20, "b" * 20 + "a" * 20],
    [_big, _big[::-1]],
]


def _all_scrambles(s, memo=None):
    memo = {} if memo is None else memo
    if s in memo:
        return memo[s]
    if len(s) == 1:
        memo[s] = {s}
        return memo[s]
    out = set()
    for k in range(1, len(s)):
        for x in _all_scrambles(s[:k], memo):
            for y in _all_scrambles(s[k:], memo):
                out.add(x + y)
                out.add(y + x)
    memo[s] = out
    return out


def _brute_scramble(s1, s2):
    return s2 in _all_scrambles(s1)


def _gen_scramble(r):
    s = _rs(r, "abc", 1, 7)
    mode = r.random()
    if mode < 0.45:
        t = _make_scramble(r, s)
    elif mode < 0.8:
        t = _make_scramble(r, s)
        if len(t) > 1:
            t = _swap_two(r, t)
    else:
        t = list(s)
        r.shuffle(t)
        t = "".join(t)
    return [s, t]


def _v_scramble(tests):
    for t in tests:
        s1, s2 = t["args"]
        assert 1 <= len(s1) <= 40 and len(s1) == len(s2)
        assert all("a" <= c <= "z" for c in s1 + s2)
    assert any(t["expected"] for t in tests) and any(not t["expected"] for t in tests)


CHECKS["scramble-string-check"] = (_brute_scramble, _gen_scramble, "exact")
VALIDATE["scramble-string-check"] = _v_scramble
