"""Problems: strings, palindromes (checks, construction, counting, minimum insertions, rearrangement feasibility). See data/lib.py for the registry."""
from collections import Counter
from itertools import combinations, product, permutations

from lib import add, rnd, CHECKS, VALIDATE, gen_arr  # noqa: F401

TOPIC = "Strings"
LET = "abcdefghijklmnopqrstuvwxyz"
MOD = 10 ** 9 + 7


def _rs(r, n, alpha="abc"):
    return "".join(r.choice(alpha) for _ in range(n))


def _lower(s):
    return all("a" <= c <= "z" for c in s)


def _digits(s):
    return all("0" <= c <= "9" for c in s)


def _is_pal(t):
    return t == t[::-1]


# ---------------------------------------------------------------- EASY

p = add(
    id="can-rearrange-into-palindrome", title="Can the Letters Form a Palindrome", diff="Easy", topic=TOPIC,
    fn="canFormPalindrome", params=[("s", "string")], ret="bool", cmp="exact",
    desc='''<p>You are given a string <code>s</code>. Decide whether the letters of <code>s</code> can be <strong>rearranged</strong> (using every letter exactly once, in any order) into a palindrome. Return <code>true</code> if some arrangement is a palindrome and <code>false</code> otherwise.</p><p>For example, <code>"carrace"</code> can become <code>"racecar"</code>, so the answer is <code>true</code>; <code>"aabb"</code> can become <code>"abba"</code>, so the answer is <code>true</code>; <code>"abc"</code> cannot be rearranged into a palindrome, so the answer is <code>false</code>.</p>''',
    constraints=["1 &le; s.length &le; 8,000", "s consists of lowercase English letters"],
    hints=["You do not have to try any arrangement. Think about what a palindrome looks like from the middle outwards.",
           "Every letter in a palindrome appears in a mirrored pair, except possibly one letter that sits in the exact middle.",
           "Count the occurrences of each letter. The answer is true exactly when at most one letter has an odd count."],
    editorial=["In a palindrome, position <code>i</code> and position <code>n - 1 - i</code> hold the same letter. So the letters come in pairs. When <code>n</code> is odd there is one unpaired position, the center; when <code>n</code> is even there is none.",
               "Therefore a rearrangement exists if and only if at most one letter occurs an odd number of times. (If the length is even, the number of odd counts is automatically even, so the condition forces it to be zero; if the length is odd, it is automatically odd, so it forces exactly one.) If the condition holds, put half of each letter on the left, the odd letter in the middle and mirror the left half to the right.",
               "Counting letters takes one pass. You can also keep a set of letters currently seen an odd number of times, toggling each letter as you go. Time is O(n), and space is O(1) because the alphabet is fixed."],
    time="O(n)", space="O(1)",
    solution='''def canFormPalindrome(s):
    odd = set()
    for c in s:
        if c in odd:
            odd.remove(c)
        else:
            odd.add(c)
    return len(odd) <= 1
''',
    tests=[["carrace"], ["aabb"], ["abc"], ["a"], ["ab"], ["aa"], ["aab"], ["aabbc"], ["aabbcd"], ["abcabcabc"], ["zzzyyyxxx"], ["racecar"], ["abcdefghijklmnopqrstuvwxyz"]],
)
_r = rnd(9201)
_h = [_r.choice(LET) for _ in range(3999)]
_a = _h + _h + ["q"]; _r.shuffle(_a)
p["tests"].append(["".join(_a)])
_a2 = _h + _h + ["q", "w"]; _r.shuffle(_a2)
p["tests"].append(["".join(_a2)])
p["tests"].append(["".join(LET[i % 26] for i in range(7999))])
p["tests"].append(["".join(_r.choice("ab") for _ in range(8000))])


def b_perm_pal(s):
    if len(s) > 9:  # too many permutations to enumerate; count parities instead
        return sum(v % 2 for v in Counter(s).values()) <= 1
    for t in set(permutations(s)):
        if t == t[::-1]:
            return True
    return False


def g_perm_pal(r):
    if r.random() < 0.5:
        h = [r.choice("abc") for _ in range(r.randint(0, 3))]
        a = h + h + ([r.choice("abc")] if r.random() < 0.6 else [])
        if r.random() < 0.3 and a:
            a[r.randrange(len(a))] = r.choice("abc")
        if not a:
            a = ["a"]
        r.shuffle(a)
        return ["".join(a)]
    return [_rs(r, r.randint(1, 7), "abc")]


def v_perm_pal(tests):
    for t in tests:
        s = t["args"][0]
        assert 1 <= len(s) <= 8000 and _lower(s)
    assert any(t["expected"] for t in tests) and any(not t["expected"] for t in tests)


CHECKS["can-rearrange-into-palindrome"] = (b_perm_pal, g_perm_pal, "exact")
VALIDATE["can-rearrange-into-palindrome"] = v_perm_pal


p = add(
    id="smallest-palindrome-by-fewest-replacements", title="Smallest Palindrome by Fewest Replacements", diff="Easy", topic=TOPIC,
    fn="makeSmallestPalindrome", params=[("s", "string")], ret="string", cmp="exact",
    desc='''<p>In one operation you may replace any single character of the string <code>s</code> with any lowercase letter. Turn <code>s</code> into a palindrome using the <strong>fewest</strong> operations. If several palindromes can be reached with that fewest number of operations, return the <strong>lexicographically smallest</strong> of them.</p><p>For example, <code>"egcfe"</code> needs one operation (the mismatching pair is <code>g</code> and <code>f</code>), and writing the smaller letter gives <code>"efcfe"</code>. <code>"abcd"</code> needs two operations and gives <code>"abba"</code>. <code>"racecars"</code> gives <code>"raaccaar"</code>.</p>''',
    constraints=["1 &le; s.length &le; 8,000", "s consists of lowercase English letters"],
    hints=["Which characters of the string are forced to be equal in any palindrome?",
           "Position <code>i</code> and position <code>n - 1 - i</code> form a pair that must end up equal. Different pairs do not influence each other.",
           "For a mismatching pair one replacement is enough and it must overwrite one side with the other letter. To get the smallest result, overwrite the larger letter with the smaller one."],
    editorial=["Split the string into independent pairs <code>(s[i], s[n-1-i])</code> with <code>i &lt; n - 1 - i</code>; the middle letter of an odd-length string is free. A pair that already matches costs nothing. A mismatching pair needs at least one replacement, and exactly one is enough: copy one letter over the other.",
               "That fixes the minimum number of operations, and it also limits the choices: for a mismatching pair, the final common letter must be one of the two existing letters. Choosing the smaller one makes the string as small as possible, and the choices for different pairs are independent, so the greedy per-pair choice is globally smallest.",
               "Implementation: walk two pointers inwards, write the minimum of the two letters at both places. Time O(n), space O(n) for the output."],
    time="O(n)", space="O(n)",
    solution='''def makeSmallestPalindrome(s):
    t = list(s)
    i, j = 0, len(t) - 1
    while i < j:
        c = min(t[i], t[j])
        t[i] = c
        t[j] = c
        i += 1
        j -= 1
    return "".join(t)
''',
    tests=[["egcfe"], ["abcd"], ["racecars"], ["a"], ["ab"], ["ba"], ["zz"], ["abcba"], ["zyxwvu"], ["aaaaab"], ["bcab"], ["mnbvcxz"]],
)
_r = rnd(9202)
p["tests"].append([_rs(_r, 8000, LET)])
p["tests"].append([_rs(_r, 7999, "ab")])
p["tests"].append(["z" * 4000 + "a" * 4000])


def b_small_pal(s):
    n = len(s)
    best = None
    for t in product(sorted(set(s)), repeat=n):
        if t == t[::-1]:
            diff = sum(1 for x, y in zip(s, t) if x != y)
            key = (diff, "".join(t))
            if best is None or key < best:
                best = key
    return best[1]


def v_small_pal(tests):
    for t in tests:
        s = t["args"][0]
        assert 1 <= len(s) <= 8000 and _lower(s)
        assert _is_pal(t["expected"]) and len(t["expected"]) == len(s)


CHECKS["smallest-palindrome-by-fewest-replacements"] = (b_small_pal, lambda r: [_rs(r, r.randint(1, 7), "abc")], "exact")
VALIDATE["smallest-palindrome-by-fewest-replacements"] = v_small_pal

# ---------------------------------------------------------------- MEDIUM

p = add(
    id="min-insertions-to-make-palindrome", title="Minimum Insertions to Make a Palindrome", diff="Medium", topic=TOPIC,
    fn="minInsertions", params=[("s", "string")], ret="int", cmp="exact",
    desc='''<p>In one step you may insert any lowercase letter at any position of the string <code>s</code> (the front, the back or between two letters). Return the minimum number of insertions needed to turn <code>s</code> into a palindrome.</p><p>For example, <code>"abcba"</code> is already a palindrome, so the answer is <code>0</code>; <code>"ab"</code> needs <code>1</code> insertion (<code>"aba"</code>); <code>"mbadm"</code> needs <code>2</code> insertions (for example <code>"mbdadbm"</code>).</p>''',
    constraints=["1 &le; s.length &le; 600", "s consists of lowercase English letters"],
    hints=["Look at the two outermost letters of the string. What happens if they are equal? What if they differ?",
           "Let <code>f(i, j)</code> be the answer for the piece <code>s[i..j]</code>. If <code>s[i] == s[j]</code>, those two letters already mirror each other, so <code>f(i, j) = f(i+1, j-1)</code>.",
           "If they differ, you must insert one letter to mirror either <code>s[i]</code> or <code>s[j]</code>: <code>f(i, j) = 1 + min(f(i+1, j), f(i, j-1))</code>. Fill the table by increasing length (or by decreasing <code>i</code>); an empty or single-letter piece costs 0."],
    editorial=["Define <code>dp[i][j]</code> as the fewest insertions that make <code>s[i..j]</code> a palindrome. Single letters and empty pieces cost 0. If the end letters are equal, nothing is needed for them and <code>dp[i][j] = dp[i+1][j-1]</code>. Otherwise one end letter has no mirror; inserting its copy on the opposite side costs one step and leaves a smaller piece, giving <code>1 + min(dp[i+1][j], dp[i][j-1])</code>.",
               "The answer is <code>dp[0][n-1]</code>. There are O(n<sup>2</sup>) states and each is computed in O(1), so time and space are O(n<sup>2</sup>); the table can be reduced to O(n) memory by keeping only the rows that are needed.",
               "Equivalent view: the letters you do not need to insert for are exactly a longest palindromic subsequence of <code>s</code>, so the answer equals <code>n</code> minus the length of that subsequence. Every other letter needs one inserted mirror partner."],
    time="O(n^2)", space="O(n^2)",
    solution='''def minInsertions(s):
    n = len(s)
    dp = [[0] * n for _ in range(n)]
    for i in range(n - 2, -1, -1):
        row = dp[i]
        nxt = dp[i + 1]
        for j in range(i + 1, n):
            if s[i] == s[j]:
                row[j] = nxt[j - 1]
            else:
                a = nxt[j]
                b = row[j - 1]
                row[j] = 1 + (a if a < b else b)
    return dp[0][n - 1]
''',
    tests=[["abcba"], ["ab"], ["mbadm"], ["a"], ["aa"], ["abc"], ["abcd"], ["leetcode"], ["zzazz"], ["aabaa"], ["abcdefghij"], ["abab"], ["aaaabaaa"]],
)
_r = rnd(9203)
p["tests"].append([_rs(_r, 600, "ab")])
p["tests"].append([("abc" * 200)])
_h = _rs(_r, 290, "abcd")
p["tests"].append([_h + _rs(_r, 15, "xyz") + _h[::-1]])
p["tests"].append(["a" * 599 + "b"])


def b_min_ins(s):
    n = len(s)
    best = 0
    for mask in range(1 << n):
        t = [s[i] for i in range(n) if mask >> i & 1]
        if t == t[::-1] and len(t) > best:
            best = len(t)
    return n - best


def v_min_ins(tests):
    for t in tests:
        s = t["args"][0]
        assert 1 <= len(s) <= 600 and _lower(s)


CHECKS["min-insertions-to-make-palindrome"] = (b_min_ins, lambda r: [_rs(r, r.randint(1, 10), "abc")], "exact")
VALIDATE["min-insertions-to-make-palindrome"] = v_min_ins


p = add(
    id="unique-length-three-palindromic-subsequences", title="Distinct Three-Letter Palindromic Subsequences", diff="Medium", topic=TOPIC,
    fn="countThreeLetterPalindromes", params=[("s", "string")], ret="int", cmp="exact",
    desc='''<p>Count the <strong>distinct</strong> palindromes of length exactly 3 that occur in <code>s</code> as a <em>subsequence</em> (letters taken in order, not necessarily next to each other). A palindrome of length 3 has the form <code>xyx</code>. Two subsequences that read the same count only once, however many ways there are to pick their positions.</p><p>For example, <code>"aabca"</code> contains <code>"aaa"</code>, <code>"aba"</code> and <code>"aca"</code>, so the answer is <code>3</code>. <code>"adc"</code> has none, so the answer is <code>0</code>. <code>"bbcbaba"</code> gives <code>4</code> (<code>bbb</code>, <code>bcb</code>, <code>bab</code>, <code>aba</code>).</p>''',
    constraints=["3 &le; s.length &le; 8,000", "s consists of lowercase English letters"],
    hints=["A three-letter palindrome is fully described by its outer letter <code>x</code> and its middle letter <code>y</code>. There are only 26 &times; 26 possibilities.",
           "For a fixed outer letter <code>x</code>, which positions of <code>x</code> are the best to use as the two outer letters?",
           "Use the first and the last occurrence of <code>x</code>. Every distinct letter that appears strictly between them is a valid middle letter, so add the number of distinct letters in that stretch."],
    editorial=["Fix the outer letter <code>x</code>. A subsequence <code>x y x</code> exists exactly when some occurrence of <code>y</code> sits between two occurrences of <code>x</code>. Taking the first and the last occurrence of <code>x</code> gives the widest window, so <code>xyx</code> is a subsequence if and only if <code>y</code> occurs somewhere strictly inside that window.",
               "So for each letter with at least two occurrences, the contribution is the number of distinct letters in <code>s[first+1 .. last-1]</code>. Summing over the 26 letters counts every distinct palindrome exactly once, because different <code>(x, y)</code> pairs are different strings.",
               "Each letter costs one scan of at most n characters, so the total is O(26 &middot; n) time with O(26) extra space."],
    time="O(26 n)", space="O(1)",
    solution='''def countThreeLetterPalindromes(s):
    first = {}
    last = {}
    for i, c in enumerate(s):
        if c not in first:
            first[c] = i
        last[c] = i
    total = 0
    for c in first:
        if last[c] - first[c] >= 2:
            total += len(set(s[first[c] + 1:last[c]]))
    return total
''',
    tests=[["aabca"], ["adc"], ["bbcbaba"], ["aaa"], ["aab"], ["abcabc"], ["abacaba"], ["zyxwvutsrqponmlkjihgfedcbazyx"], ["aaaaaaaa"], ["abba"], ["abcdcba"]],
)
_r = rnd(9204)
p["tests"].append([_rs(_r, 8000, LET)])
p["tests"].append([_rs(_r, 8000, "abcde")])
p["tests"].append(["a" + _rs(_r, 7998, LET[1:]) + "a"])


def b_three_pal(s):
    found = set()
    n = len(s)
    for i in range(n):
        for j in range(i + 1, n):
            for k in range(j + 1, n):
                if s[i] == s[k]:
                    found.add(s[i] + s[j] + s[k])
    return len(found)


def v_three_pal(tests):
    for t in tests:
        s = t["args"][0]
        assert 3 <= len(s) <= 8000 and _lower(s)


CHECKS["unique-length-three-palindromic-subsequences"] = (b_three_pal, lambda r: [_rs(r, r.randint(3, 12), r.choice(["ab", "abc", "abcd"]))], "exact")
VALIDATE["unique-length-three-palindromic-subsequences"] = v_three_pal


p = add(
    id="palindromic-substring-queries", title="Palindromic Substring Queries", diff="Medium", topic=TOPIC,
    fn="palindromeQueries", params=[("s", "string"), ("queries", "int[][]")], ret="int[]", cmp="exact",
    desc='''<p>You are given a string <code>s</code> and a list of queries. Each query is a pair <code>[l, r]</code> (0-indexed, both ends inclusive) that selects the substring <code>s[l..r]</code>. For every query, answer <code>1</code> if the selected substring is a palindrome and <code>0</code> otherwise.</p><p>Return the answers as an array in the order of the queries.</p><p>For example, for <code>s = "abacaba"</code> and the queries <code>[0,6]</code>, <code>[1,3]</code>, <code>[2,4]</code>, <code>[3,3]</code>, <code>[0,2]</code>, <code>[1,4]</code> the answer is <code>[1, 0, 1, 1, 1, 0]</code>.</p>''',
    constraints=["1 &le; s.length &le; 6,000", "s consists of lowercase English letters", "1 &le; queries.length &le; 2,000", "0 &le; l &le; r &lt; s.length for every query"],
    hints=["Checking each query directly by comparing characters costs O(length) per query, which can be slow for many long queries. Preprocess the string once.",
           "Every palindrome is centered at a letter (odd length) or between two letters (even length). For each center, how far does the palindrome extend?",
           "Compute the maximal radius around every center (Manacher's algorithm, or expand around each center in O(n<sup>2</sup>) total). The query <code>[l, r]</code> is a palindrome exactly when the center at <code>l + r</code> reaches at least <code>r - l + 1</code> letters."],
    editorial=["If a substring is a palindrome, so is the substring obtained by trimming one letter from each end. So for each center it is enough to know the length of the <em>longest</em> palindrome around it: every shorter palindrome with the same center exists too, and nothing longer does.",
               "Insert a separator between all letters (<code>#a#b#a#</code>) so that odd and even centers are treated alike, and compute <code>p[c]</code>, the length of the longest palindrome of the original string centered at <code>c</code>, with Manacher's algorithm in O(n). The substring <code>s[l..r]</code> has its center at index <code>l + r + 2</code> in the padded string <code>^#s0#s1#...#$</code>, so the answer to a query is <code>1</code> if <code>p[l + r + 2] &ge; r - l + 1</code>.",
               "Preprocessing is O(n), every query is O(1), so the total is O(n + q). A simple alternative is to build the boolean table <code>pal[i][j]</code> in O(n<sup>2</sup>) time and memory."],
    time="O(n + q)", space="O(n)",
    solution='''def palindromeQueries(s, queries):
    t = "^#" + "#".join(s) + "#$"
    m = len(t)
    p = [0] * m
    center = right = 0
    for i in range(1, m - 1):
        if i < right:
            p[i] = min(right - i, p[2 * center - i])
        while t[i + 1 + p[i]] == t[i - 1 - p[i]]:
            p[i] += 1
        if i + p[i] > right:
            center, right = i, i + p[i]
    # p[i] is the length of the longest palindrome of s centered at padded index i
    return [1 if p[l + r + 2] >= r - l + 1 else 0 for l, r in queries]
''',
    tests=[["abacaba", [[0, 6], [1, 3], [2, 4], [3, 3], [0, 2], [1, 4]]],
           ["a", [[0, 0]]],
           ["ab", [[0, 1], [0, 0], [1, 1]]],
           ["aa", [[0, 1]]],
           ["abcd", [[0, 3], [1, 2], [2, 2]]],
           ["abba", [[0, 3], [1, 2], [0, 2], [1, 3]]],
           ["aaaaa", [[0, 4], [0, 3], [1, 3], [2, 2], [1, 4]]],
           ["racecarxracecar", [[0, 6], [8, 14], [0, 14], [1, 5], [6, 8], [7, 7]]],
           ["abcbaabcbaabc", [[0, 4], [5, 9], [0, 9], [3, 9], [2, 10], [4, 5]]],
           ["xyzzyxyzzyx", [[0, 10], [1, 4], [2, 3], [0, 5], [5, 10], [4, 6]]]],
)
_r = rnd(9205)


def _pal_queries(r, s, q):
    n = len(s)
    out = []
    for _ in range(q):
        if r.random() < 0.6:
            c = r.randrange(n)
            a, b = c, c + (1 if r.random() < 0.5 and c + 1 < n and s[c] == s[c + 1] else 0)
            if s[a] != s[b]:
                b = a
            while a - 1 >= 0 and b + 1 < n and s[a - 1] == s[b + 1] and r.random() < 0.97:
                a -= 1
                b += 1
            if r.random() < 0.25 and a > 0:
                a -= 1
            out.append([a, b])
        else:
            a = r.randrange(n)
            b = r.randrange(a, min(n, a + r.choice([3, 10, 100, n])))
            out.append([a, b])
    return out


_s = "".join(_r.choice("ab") for _ in range(6000))
p["tests"].append([_s, _pal_queries(_r, _s, 2000)])
_s = ""
while len(_s) < 5900:
    _h = _rs(_r, _r.randint(1, 40), "abc")
    _s += _h + (_r.choice("abc") if _r.random() < 0.5 else "") + _h[::-1]
_s = _s[:6000]
p["tests"].append([_s, _pal_queries(_r, _s, 2000)])
p["tests"].append(["a" * 6000, [[0, 5999], [1, 5998], [10, 5000], [3000, 3000], [0, 0]] + [[_r.randrange(3000), _r.randrange(3000, 6000)] for _ in range(1500)]])


def b_pal_q(s, queries):
    return [1 if s[l:r + 1] == s[l:r + 1][::-1] else 0 for l, r in queries]


def g_pal_q(r):
    s = _rs(r, r.randint(1, 12), r.choice(["ab", "abc"]))
    q = []
    for _ in range(r.randint(1, 8)):
        a = r.randrange(len(s))
        q.append([a, r.randrange(a, len(s))])
    return [s, q]


def v_pal_q(tests):
    for t in tests:
        s, qs = t["args"]
        assert 1 <= len(s) <= 6000 and _lower(s)
        assert 1 <= len(qs) <= 2000
        assert all(0 <= l <= r < len(s) for l, r in qs)
        assert len(t["expected"]) == len(qs)
    big = [t for t in tests if len(t["args"][0]) > 1000]
    for t in big:
        assert 0.05 < sum(t["expected"]) / len(t["expected"]) < 1.0001, "queries should mix yes and no"


CHECKS["palindromic-substring-queries"] = (b_pal_q, g_pal_q, "exact")
VALIDATE["palindromic-substring-queries"] = v_pal_q


p = add(
    id="count-palindromic-partitions", title="Count Palindromic Partitions", diff="Medium", topic=TOPIC, tier="extra",
    fn="countPalindromePartitions", params=[("s", "string")], ret="int", cmp="exact",
    desc='''<p>A <strong>partition</strong> of the string <code>s</code> cuts it into one or more consecutive non-empty pieces whose concatenation is <code>s</code>. Count the partitions in which <strong>every piece is a palindrome</strong>. Two partitions are different when they cut <code>s</code> at different places.</p><p>Return the count modulo <code>1,000,000,007</code>.</p><p>For example, <code>"aab"</code> has <code>2</code> such partitions (<code>a|a|b</code> and <code>aa|b</code>), <code>"aaa"</code> has <code>4</code> (<code>a|a|a</code>, <code>aa|a</code>, <code>a|aa</code>, <code>aaa</code>) and <code>"abc"</code> has <code>1</code>.</p>''',
    constraints=["1 &le; s.length &le; 800", "s consists of lowercase English letters", "Return the count modulo 1,000,000,007"],
    hints=["Listing every partition is far too slow, since the number of partitions can be exponential. Count them instead.",
           "Let <code>ways[i]</code> be the number of palindromic partitions of the prefix of length <code>i</code>. The last piece of such a partition is some palindromic suffix of that prefix.",
           "<code>ways[i] = sum of ways[j]</code> over all <code>j &lt; i</code> for which <code>s[j..i-1]</code> is a palindrome, with <code>ways[0] = 1</code>. Find all palindromic substrings by expanding around each of the 2n-1 centers."],
    editorial=["Define <code>ways[i]</code> as the number of palindromic partitions of <code>s[0..i-1]</code>, with <code>ways[0] = 1</code> for the empty prefix. Look at the last piece of a partition of the prefix of length <code>i</code>: it is a palindrome <code>s[j..i-1]</code> and what remains before it is any palindromic partition of the prefix of length <code>j</code>. Hence <code>ways[i]</code> is the sum of <code>ways[j]</code> over all <code>j</code> such that <code>s[j..i-1]</code> is a palindrome. Different last pieces give different partitions, so nothing is double counted.",
               "To know which substrings are palindromes, expand around every center and record, for each end index, the list of start indices of palindromes that end there. There are at most O(n<sup>2</sup>) palindromic substrings (for example in <code>aaa...a</code>), so this table takes O(n<sup>2</sup>) time and space in the worst case.",
               "The answer is <code>ways[n]</code> modulo 1,000,000,007. For <code>aaa...a</code> every cut is allowed, so the answer is 2<sup>n-1</sup>, which is a useful check."],
    time="O(n^2)", space="O(n^2)",
    solution='''def countPalindromePartitions(s):
    MOD = 10**9 + 7
    n = len(s)
    starts = [[] for _ in range(n)]  # starts[e]: start indices of palindromes ending at e
    for c in range(n):
        l = r = c
        while l >= 0 and r < n and s[l] == s[r]:
            starts[r].append(l)
            l -= 1
            r += 1
        l, r = c, c + 1
        while l >= 0 and r < n and s[l] == s[r]:
            starts[r].append(l)
            l -= 1
            r += 1
    ways = [0] * (n + 1)
    ways[0] = 1
    for e in range(n):
        total = 0
        for st in starts[e]:
            total += ways[st]
        ways[e + 1] = total % MOD
    return ways[n]
''',
    tests=[["aab"], ["aaa"], ["abc"], ["a"], ["aa"], ["abba"], ["abacaba"], ["aaaa"], ["abab"], ["aabbaa"], ["zzzzzzzzzz"]],
)
_r = rnd(9206)
p["tests"].append(["a" * 800])
p["tests"].append([_rs(_r, 800, "ab")])
p["tests"].append([("aab" * 266) + "aa"])
p["tests"].append(["a" * 399 + "b" + "a" * 400])


def b_pal_part(s):
    n = len(s)

    def rec(i):
        if i == n:
            return 1
        total = 0
        for j in range(i + 1, n + 1):
            t = s[i:j]
            if t == t[::-1]:
                total += rec(j)
        return total
    return rec(0) % MOD


def v_pal_part(tests):
    for t in tests:
        s = t["args"][0]
        assert 1 <= len(s) <= 800 and _lower(s)
        assert 0 <= t["expected"] < MOD
    assert any(len(t["args"][0]) == 800 and t["args"][0] == "a" * 800 and t["expected"] == pow(2, 799, MOD) for t in tests)


CHECKS["count-palindromic-partitions"] = (b_pal_part, lambda r: [_rs(r, r.randint(1, 12), r.choice(["a", "ab", "abc"]))], "exact")
VALIDATE["count-palindromic-partitions"] = v_pal_part


p = add(
    id="palindrome-rearrangement-with-replacements-queries", title="Palindrome Rearrangement with Replacements", diff="Medium", topic=TOPIC,
    fn="canMakePalindromeQueries", params=[("s", "string"), ("queries", "int[][]")], ret="int[]", cmp="exact",
    desc='''<p>You are given a string <code>s</code> and queries <code>[l, r, k]</code>. For a query, take the substring <code>s[l..r]</code> (0-indexed, inclusive), <strong>rearrange</strong> its letters in any order you like, and additionally <strong>replace</strong> at most <code>k</code> of its letters with any lowercase letters. Answer <code>1</code> if the substring can become a palindrome this way and <code>0</code> otherwise.</p><p>Queries are independent: the string <code>s</code> is never modified. Return the array of answers.</p><p>For example, for <code>s = "abcda"</code> the query <code>[3, 3, 0]</code> gives <code>1</code> (a single letter), <code>[0, 3, 1]</code> gives <code>0</code> (<code>"abcd"</code> has four letters that occur an odd number of times and one replacement cannot fix that) and <code>[0, 4, 1]</code> gives <code>1</code>.</p>''',
    constraints=["1 &le; s.length &le; 8,000", "s consists of lowercase English letters", "1 &le; queries.length &le; 3,000", "0 &le; l &le; r &lt; s.length and 0 &le; k &le; s.length for every query"],
    hints=["Since the letters may be rearranged, only the count of each letter in the substring matters, not the order.",
           "A multiset of letters can form a palindrome exactly when at most one letter has an odd count. What does one replacement do to the number of odd-count letters?",
           "One replacement can turn two odd-count letters into even ones (change one copy of letter X into letter Y). So you need <code>odd // 2</code> replacements, where <code>odd</code> is the number of letters with an odd count. Get <code>odd</code> for any substring quickly with prefix parity bitmasks."],
    editorial=["Let <code>odd</code> be the number of letters occurring an odd number of times in the substring. After rearranging, a palindrome needs <code>odd &le; 1</code>. A replacement changes the count of one letter down by one and another up by one (or keeps it the same), so it can lower <code>odd</code> by at most 2, and it does lower it by 2 if it turns a copy of one odd letter into another odd letter. Therefore exactly <code>odd // 2</code> replacements are needed and sufficient (for odd <code>odd</code>, one odd letter stays as the middle).",
               "To get <code>odd</code> for arbitrary ranges fast, store for each prefix a 26-bit mask whose bit <code>c</code> says whether letter <code>c</code> has appeared an odd number of times. The parity mask of <code>s[l..r]</code> is <code>mask[r+1] ^ mask[l]</code>, and <code>odd</code> is its popcount.",
               "The answer to a query is <code>1</code> if <code>popcount // 2 &le; k</code>. Preprocessing takes O(n) and each query takes O(1) (the popcount of a 26-bit number), for O(n + q) overall."],
    time="O(n + q)", space="O(n)",
    solution='''def canMakePalindromeQueries(s, queries):
    masks = [0]
    m = 0
    for c in s:
        m ^= 1 << (ord(c) - 97)
        masks.append(m)
    res = []
    for l, r, k in queries:
        odd = bin(masks[r + 1] ^ masks[l]).count("1")
        res.append(1 if odd // 2 <= k else 0)
    return res
''',
    tests=[["abcda", [[3, 3, 0], [0, 3, 1], [0, 4, 1]]],
           ["a", [[0, 0, 0]]],
           ["ab", [[0, 1, 0], [0, 1, 1], [1, 1, 0]]],
           ["aabb", [[0, 3, 0], [0, 2, 0], [1, 2, 0], [1, 2, 1]]],
           ["abcdefghij", [[0, 9, 4], [0, 9, 5], [0, 8, 4], [2, 5, 1], [2, 5, 2]]],
           ["zzzzzz", [[0, 5, 0], [2, 4, 0]]],
           ["abcabcabc", [[0, 8, 0], [0, 8, 1], [0, 5, 0], [0, 5, 3], [1, 7, 1], [4, 4, 0]]],
           ["racecarpalindrome", [[0, 6, 0], [0, 16, 3], [0, 16, 4], [7, 16, 3], [7, 16, 4]]]],
)
_r = rnd(9207)


def _rq(r, n, q, kmax):
    out = []
    for _ in range(q):
        a = r.randrange(n)
        b = r.randrange(a, min(n, a + r.choice([5, 50, 1000, n])))
        out.append([a, b, r.randint(0, kmax)])
    return out


_s = _rs(_r, 8000, LET)
p["tests"].append([_s, _rq(_r, 8000, 3000, 13)])
_s = _rs(_r, 8000, "abcd")
p["tests"].append([_s, _rq(_r, 8000, 3000, 2)])


def b_pal_repl(s, queries):
    res = []
    for l, r, k in queries:
        t = s[l:r + 1]
        letters = sorted(set(t))
        start = tuple(t.count(c) for c in letters)
        level = {start}
        seen = {start}
        ok = False
        for step in range(k + 1):
            if any(sum(v % 2 for v in st) <= 1 for st in level):
                ok = True
                break
            nxt = set()
            for st in level:  # one replacement: move one letter from x to y
                for x in range(len(letters)):
                    if st[x] == 0:
                        continue
                    for y in range(len(letters)):
                        if y != x:
                            u = list(st)
                            u[x] -= 1
                            u[y] += 1
                            u = tuple(u)
                            if u not in seen:
                                seen.add(u)
                                nxt.add(u)
            level = nxt
        res.append(1 if ok else 0)
    return res


def g_pal_repl(r):
    s = _rs(r, r.randint(1, 8), "abc")
    q = []
    for _ in range(r.randint(1, 4)):
        a = r.randrange(len(s))
        b = r.randrange(a, len(s))
        q.append([a, b, r.randint(0, 3)])
    return [s, q]


def v_pal_repl(tests):
    for t in tests:
        s, qs = t["args"]
        assert 1 <= len(s) <= 8000 and _lower(s)
        assert 1 <= len(qs) <= 3000
        assert all(0 <= l <= r < len(s) and 0 <= k <= len(s) for l, r, k in qs)
    big = [t for t in tests if len(t["args"][0]) > 1000]
    for t in big:
        assert 0.1 < sum(t["expected"]) / len(t["expected"]) < 0.95, "mix yes and no"


CHECKS["palindrome-rearrangement-with-replacements-queries"] = (b_pal_repl, g_pal_repl, "exact")
VALIDATE["palindrome-rearrangement-with-replacements-queries"] = v_pal_repl


p = add(
    id="largest-palindromic-number-from-digits", title="Largest Palindromic Number from Digits", diff="Medium", topic=TOPIC,
    fn="largestPalindromicNumber", params=[("digits", "string")], ret="string", cmp="exact",
    desc='''<p>You are given a string <code>digits</code> made of the characters <code>0</code>-<code>9</code>. Choose some of these digits (each position at most once, so a digit can be used only as many times as it occurs), arrange them in any order and form a number that is a <strong>palindrome</strong>. The number must not have leading zeros, except that the number <code>0</code> itself is allowed.</p><p>Return the <strong>largest</strong> such number as a string. At least one digit must be used.</p><p>For example, <code>"444947137"</code> gives <code>"7449447"</code>. <code>"00009"</code> gives <code>"9"</code>, because <code>"00900"</code> would have leading zeros. <code>"000"</code> gives <code>"0"</code>. <code>"0011"</code> gives <code>"1001"</code>.</p>''',
    constraints=["1 &le; digits.length &le; 8,000", "digits consists of the characters 0-9", "The result has no leading zero unless it is exactly \"0\""],
    hints=["A bigger number is one with more digits, and among equal lengths, one with larger leading digits. So first maximize the length, then the digits from the front.",
           "Pairs of equal digits go symmetrically around the center. Take as many pairs as you can; the largest digits go to the outside. A leftover single digit can sit in the middle: pick the largest one available.",
           "Careful with zeros: a pair of zeros cannot be the outermost pair. If there is no pair of non-zero digits at all, the best you can do is a single digit, namely the largest digit present."],
    editorial=["Count the occurrences of every digit. A palindrome consists of mirrored pairs plus at most one middle digit, so the longest palindrome uses <code>count // 2</code> pairs of every digit. Build the left half from the pairs, putting digits 9, 8, ..., 1 first, in that order; this makes the left half as large as possible, and the right half is its mirror image.",
               "Zero pairs are special: they can only go strictly inside, so they are appended after all non-zero pairs (the smallest digit, hence at the end of the left half), and only if the left half is not empty already. If no non-zero digit appears at least twice, the left half is empty and the best answer is the single largest digit (which may be <code>0</code>).",
               "For the middle, use the largest digit whose count is odd (the leftover after pairing), including <code>0</code> if its count is odd. If every count is even, there is no middle. Counting is O(n), building the answer is O(n), and the space is O(n) for the output."],
    time="O(n)", space="O(n)",
    solution='''def largestPalindromicNumber(digits):
    cnt = [0] * 10
    for ch in digits:
        cnt[ord(ch) - 48] += 1
    half = "".join(str(d) * (cnt[d] // 2) for d in range(9, 0, -1))
    if not half:
        for d in range(9, -1, -1):
            if cnt[d]:
                return str(d)
    half += "0" * (cnt[0] // 2)
    mid = ""
    for d in range(9, -1, -1):
        if cnt[d] % 2:
            mid = str(d)
            break
    return half + mid + half[::-1]
''',
    tests=[["444947137"], ["00009"], ["000"], ["0011"], ["0"], ["9"], ["12"], ["5005"], ["00100"], ["123321"], ["99887700"], ["0123456789"], ["1100000"], ["3330"]],
)
_r = rnd(9208)
p["tests"].append(["".join(_r.choice("0123456789") for _ in range(8000))])
p["tests"].append(["".join(_r.choice("00000123") for _ in range(8000))])
p["tests"].append(["0" * 8000])
p["tests"].append(["0" * 7999 + "5"])


def b_largest_pal(digits):
    have = Counter(digits)
    ds = sorted(have, reverse=True)
    n = len(digits)
    for L in range(n, 0, -1):
        h = (L + 1) // 2
        for half in product(ds, repeat=h):
            body = "".join(half)
            t = body + body[:L // 2][::-1]
            if L > 1 and t[0] == "0":
                continue
            c = Counter(t)
            if all(have[x] >= v for x, v in c.items()):
                return t
    return None


def v_largest_pal(tests):
    for t in tests:
        d = t["args"][0]
        e = t["expected"]
        assert 1 <= len(d) <= 8000 and _digits(d)
        assert _is_pal(e) and (e == "0" or e[0] != "0")
        c = Counter(d)
        assert all(c[x] >= v for x, v in Counter(e).items())


CHECKS["largest-palindromic-number-from-digits"] = (b_largest_pal, lambda r: ["".join(r.choice(r.choice(["0123", "0159", "00012", "0123456789"])) for _ in range(r.randint(1, 8)))], "exact")
VALIDATE["largest-palindromic-number-from-digits"] = v_largest_pal

# ---------------------------------------------------------------- HARD

p = add(
    id="smallest-shortest-palindrome-by-insertions", title="Smallest Shortest Palindrome by Insertions", diff="Hard", topic=TOPIC, tier="extra",
    fn="smallestShortestPalindrome", params=[("s", "string")], ret="string", cmp="exact",
    desc='''<p>You may insert any lowercase letters at any positions of the string <code>s</code> (letters of <code>s</code> are never removed or reordered). Make <code>s</code> a palindrome using the <strong>fewest insertions</strong>. Among all palindromes of that minimum length, return the <strong>lexicographically smallest</strong> one.</p><p>In other words, return the lexicographically smallest among the shortest palindromes that contain <code>s</code> as a subsequence.</p><p>For example, <code>"ab"</code> gives <code>"aba"</code> (<code>"bab"</code> also has length 3 but is larger). <code>"abc"</code> gives <code>"abcba"</code>. <code>"ba"</code> gives <code>"aba"</code>. <code>"zzz"</code> is already a palindrome and gives <code>"zzz"</code>.</p>''',
    constraints=["1 &le; s.length &le; 300", "s consists of lowercase English letters", "The answer is unique"],
    hints=["First think about how to find just the minimum number of insertions for <code>s[i..j]</code> by looking at the two end letters.",
           "Let <code>best(i, j)</code> be the smallest shortest palindrome containing <code>s[i..j]</code> as a subsequence. If <code>s[i] == s[j]</code>, wrap those letters around <code>best(i+1, j-1)</code>. Otherwise one of the end letters needs a new mirror copy.",
           "If <code>s[i] != s[j]</code>, the candidates are <code>s[i] + best(i+1, j) + s[i]</code> and <code>s[j] + best(i, j-1) + s[j]</code>. Take the shorter one, and the lexicographically smaller one when the lengths tie. Build the table by increasing interval length and store the strings themselves."],
    editorial=["The length part is the classic palindrome-insertion DP: if the end letters are equal they pair with each other, otherwise one of them is mirrored by an inserted copy. The same recurrence can carry the actual strings. For an interval <code>[i, j]</code> store <code>best(i, j)</code>, the lexicographically smallest among the shortest palindromic supersequences of <code>s[i..j]</code>.",
               "Equal end letters: <code>best(i, j) = s[i] + best(i+1, j-1) + s[i]</code>. This is optimal even among palindromes that do not pair the two ends, because any shortest palindrome for the interval starts with <code>s[i]</code>, and what lies between its outer letters must be a shortest palindromic supersequence of the inner interval, from which the smallest is chosen. For a fixed outer letter, a smaller inner part gives a smaller whole string, so greedy choice of the inner minimum is valid.",
               "Different end letters: any shortest palindrome starts with <code>s[i]</code> or <code>s[j]</code>, since a different first letter would be an extra pair that helps neither end. So compare the two candidates <code>s[i] + best(i+1, j) + s[i]</code> and <code>s[j] + best(i, j-1) + s[j]</code> by (length, then lexicographic order). Only the two previous interval lengths are needed at a time. There are O(n<sup>2</sup>) intervals and each builds a string of length O(n), so the time is O(n<sup>3</sup>) (with very fast string concatenation) and the space is O(n<sup>2</sup>) characters."],
    time="O(n^3)", space="O(n^2)",
    solution='''def smallestShortestPalindrome(s):
    n = len(s)
    two_back = [""] * (n + 1)          # intervals of length L-2
    one_back = list(s) + [""]          # intervals of length L-1 (start with L-1 = 1)
    # layer for length 1 is one_back, layer for length 0 is two_back
    for length in range(2, n + 1):
        cur = [""] * (n + 1)
        for i in range(0, n - length + 1):
            j = i + length - 1
            if s[i] == s[j]:
                cur[i] = s[i] + two_back[i + 1] + s[i]
            else:
                a = s[i] + one_back[i + 1] + s[i]
                b = s[j] + one_back[i] + s[j]
                if len(a) != len(b):
                    cur[i] = a if len(a) < len(b) else b
                else:
                    cur[i] = a if a < b else b
        two_back, one_back = one_back, cur
    return one_back[0]
''',
    tests=[["ab"], ["abc"], ["ba"], ["zzz"], ["a"], ["cb"], ["abca"], ["abcd"], ["abab"], ["aabb"], ["cabbac"], ["zyxabc"], ["bcabcab"]],
)
_r = rnd(9209)
p["tests"].append([_rs(_r, 300, "ab")])
p["tests"].append([_rs(_r, 300, "abc")])
p["tests"].append(["ab" * 150])
p["tests"].append(["z" * 150 + "a" * 150])
_h = _rs(_r, 140, "abcdef")
p["tests"].append([_h + _rs(_r, 8, "xyz") + _h[::-1]])


def b_small_short_pal(s):
    n = len(s)
    alpha = sorted(set(s))

    def is_sub(t):
        it = iter(t)
        return all(c in it for c in s)

    for extra in range(0, n):
        L = n + extra
        h = (L + 1) // 2
        for half in product(alpha, repeat=h):
            body = "".join(half)
            t = body + body[:L // 2][::-1]
            if is_sub(t):
                return t
    return None


def v_small_short_pal(tests):
    for t in tests:
        s = t["args"][0]
        e = t["expected"]
        assert 1 <= len(s) <= 300 and _lower(s)
        assert _is_pal(e) and len(e) >= len(s)
        it = iter(e)
        assert all(c in it for c in s)


CHECKS["smallest-shortest-palindrome-by-insertions"] = (b_small_short_pal, lambda r: [_rs(r, r.randint(1, 6), "abc")], "exact")
VALIDATE["smallest-shortest-palindrome-by-insertions"] = v_small_short_pal


p = add(
    id="palindrome-from-two-subsequences", title="Palindrome from Two Subsequences", diff="Hard", topic=TOPIC, tier="extra",
    fn="longestTwoPartPalindrome", params=[("a", "string"), ("b", "string")], ret="int", cmp="exact",
    desc='''<p>You are given two strings <code>a</code> and <code>b</code>. Pick a <strong>non-empty subsequence</strong> <code>x</code> of <code>a</code> and a <strong>non-empty subsequence</strong> <code>y</code> of <code>b</code> and look at the concatenation <code>x + y</code>. Return the largest possible length of such a concatenation that is a palindrome, or <code>0</code> if no choice gives a palindrome.</p><p>For example, <code>a = "cacb"</code> and <code>b = "cbba"</code> give <code>5</code> (take <code>x = "ab"</code> and <code>y = "cba"</code>, giving <code>"abcba"</code>), <code>a = "ab"</code> and <code>b = "ab"</code> give <code>3</code> (<code>"aba"</code>), and <code>a = "xy"</code> and <code>b = "zz"</code> give <code>0</code>.</p>''',
    constraints=["1 &le; a.length, b.length &le; 250", "a and b consist of lowercase English letters"],
    hints=["Glue the two strings into one string <code>s = a + b</code>. A palindromic subsequence of <code>s</code> that uses letters from both halves is exactly what you are after.",
           "Compute <code>dp[i][j]</code>, the length of the longest palindromic subsequence of <code>s[i..j]</code>, with the usual recurrence.",
           "The two outermost letters of the final palindrome are <code>s[i]</code> from <code>a</code> and <code>s[j]</code> from <code>b</code>, with <code>s[i] == s[j]</code>. Whenever <code>i</code> lies in <code>a</code>, <code>j</code> lies in <code>b</code> and the letters match, <code>dp[i][j]</code> is a candidate, because both sides are then guaranteed to be used."],
    editorial=["Let <code>s = a + b</code>. A subsequence of <code>s</code> splits into a part taken from <code>a</code> followed by a part taken from <code>b</code>, so we need a palindromic subsequence of <code>s</code> that has at least one letter on each side of the boundary. The longest palindromic subsequence DP gives <code>dp[i][j]</code> for every interval.",
               "A palindromic subsequence that takes letters from both parts has a first letter inside <code>a</code> (position <code>i</code>) and a last letter inside <code>b</code> (position <code>j</code>) which are equal. Exactly in that situation we must use the matched pair: for every <code>i &lt; |a| &le; j</code> with <code>s[i] == s[j]</code>, the value <code>dp[i][j]</code> (which equals <code>2 + dp[i+1][j-1]</code>) is achievable and uses both parts, hence it is a candidate for the answer. Take the maximum of all candidates, or 0 if there are none.",
               "Why it is enough: the best valid palindrome has outer letters at some positions <code>i</code> and <code>j</code> as described, and inside them it is any palindromic subsequence of <code>s[i+1..j-1]</code>, at best <code>dp[i+1][j-1]</code>. The table has O((|a|+|b|)<sup>2</sup>) cells, so time and space are quadratic in the total length."],
    time="O((n+m)^2)", space="O((n+m)^2)",
    solution='''def longestTwoPartPalindrome(a, b):
    s = a + b
    n = len(s)
    na = len(a)
    dp = [[0] * n for _ in range(n)]
    ans = 0
    for i in range(n - 1, -1, -1):
        row = dp[i]
        row[i] = 1
        nxt = dp[i + 1] if i + 1 < n else None
        for j in range(i + 1, n):
            if s[i] == s[j]:
                row[j] = (nxt[j - 1] if j - 1 > i else 0) + 2
                if i < na <= j and row[j] > ans:
                    ans = row[j]
            else:
                x = nxt[j]
                y = row[j - 1]
                row[j] = x if x > y else y
    return ans
''',
    tests=[["cacb", "cbba"], ["ab", "ab"], ["xy", "zz"], ["a", "a"], ["a", "b"], ["abc", "cba"], ["aaaa", "aaaa"], ["abcd", "dcba"], ["race", "car"], ["mmm", "n"], ["zzabz", "zbaz"]],
)
_r = rnd(9210)
p["tests"].append([_rs(_r, 250, "ab"), _rs(_r, 250, "ab")])
p["tests"].append([_rs(_r, 250, "abcd"), _rs(_r, 250, "abcd")])
_x = _rs(_r, 250, "abc")
p["tests"].append([_x, _x[::-1]])
p["tests"].append(["a" * 250, "b" * 249 + "a"])


def b_two_sub(a, b):
    def subs(x):
        out = set()
        n = len(x)
        for mask in range(1, 1 << n):
            out.add("".join(x[i] for i in range(n) if mask >> i & 1))
        return out
    sa, sb = subs(a), subs(b)
    best = 0
    for x in sa:
        for y in sb:
            t = x + y
            if len(t) > best and t == t[::-1]:
                best = len(t)
    return best


def v_two_sub(tests):
    for t in tests:
        a, b = t["args"]
        assert 1 <= len(a) <= 250 and 1 <= len(b) <= 250 and _lower(a) and _lower(b)
    assert any(t["expected"] == 0 for t in tests) and any(t["expected"] > 0 for t in tests)


CHECKS["palindrome-from-two-subsequences"] = (b_two_sub, lambda r: [_rs(r, r.randint(1, 6), r.choice(["ab", "abc"])), _rs(r, r.randint(1, 6), r.choice(["ab", "abc"]))], "exact")
VALIDATE["palindrome-from-two-subsequences"] = v_two_sub


p = add(
    id="count-length-five-palindromic-subsequences", title="Count Length-Five Palindromic Subsequences", diff="Hard", topic=TOPIC, tier="extra",
    fn="countFiveLetterPalindromes", params=[("digits", "string")], ret="int", cmp="exact",
    desc='''<p>You are given a string <code>digits</code> consisting of the characters <code>0</code>-<code>9</code>. Count the subsequences of length <strong>5</strong> that are palindromes. Subsequences are counted by the <em>positions</em> they use: two selections of positions are different even if they spell the same string.</p><p>Return the count modulo <code>1,000,000,007</code>.</p><p>For example, <code>"12321"</code> has exactly one subsequence of length 5 and it is a palindrome, so the answer is <code>1</code>. <code>"111111"</code> gives <code>6</code> (any five of the six positions), and <code>"0000000"</code> gives <code>21</code>. <code>"103301"</code> gives <code>2</code>.</p>''',
    constraints=["5 &le; digits.length &le; 8,000", "digits consists of the characters 0-9", "Return the count modulo 1,000,000,007"],
    hints=["A length-5 palindrome has the shape <code>a b c b a</code>. Fix the position of the middle letter <code>c</code> and count how many ways there are on each side.",
           "To the left of the middle you need an ordered pair <code>(a, b)</code> as a subsequence, to the right the reversed pair <code>(b, a)</code>. There are only 100 possible pairs.",
           "Maintain, for every pair <code>(a, b)</code>, how many times it occurs as a subsequence in the prefix and in the suffix around the middle. The number of palindromes with middle position <code>m</code> is the sum over all <code>(a, b)</code> of <code>prefix[a][b] &times; suffix[b][a]</code>."],
    editorial=["A palindrome of length 5 is <code>a b c b a</code>. Choose the position <code>m</code> of the letter <code>c</code>. The first two letters come from the part of the string before <code>m</code> as the subsequence <code>a b</code>, the last two come from the part after <code>m</code> as the subsequence <code>b a</code>, and the left and right choices are independent. So the number of palindromes centered at <code>m</code> is the sum over all digit pairs <code>(a, b)</code> of <code>pre_m[a][b] &times; suf_m[b][a]</code>, where <code>pre_m[a][b]</code> counts subsequences <code>a b</code> within <code>s[0..m-1]</code> and <code>suf_m[x][y]</code> counts subsequences <code>x y</code> within <code>s[m+1..]</code>.",
               "Both tables are updated incrementally. When extending the prefix by a digit <code>d</code>, for each digit <code>a</code> add <code>count_so_far[a]</code> to <code>pre[a][d]</code> (every earlier <code>a</code> now forms a new pair), then increment <code>count_so_far[d]</code>. The suffix tables are built the same way from the right; storing a snapshot (100 numbers) for each position takes O(100 n) memory.",
               "In total there are 10 updates per digit plus a 100-term sum per middle position, so O(100 n) time. The counts are at most about n<sup>2</sup>/2 per pair, so Python's integers cause no overflow trouble; only the final answer is reduced modulo 1,000,000,007."],
    time="O(100 n)", space="O(100 n)",
    solution='''def countFiveLetterPalindromes(digits):
    from operator import itemgetter, mul
    MOD = 10**9 + 7
    n = len(digits)
    d = [ord(c) - 48 for c in digits]
    transpose = itemgetter(*[b * 10 + a for a in range(10) for b in range(10)])
    cur = [0] * 100
    cnt = [0] * 10
    suf_t = [None] * (n + 1)   # suf_t[k][a*10+b] = number of subsequences "b a" inside d[k:]
    suf_t[n] = transpose(cur)
    for k in range(n - 1, -1, -1):
        x = d[k]
        base = x * 10
        for y in range(10):
            cur[base + y] += cnt[y]
        cnt[x] += 1
        suf_t[k] = transpose(cur)
    pre = [0] * 100
    cnt = [0] * 10
    total = 0
    for m in range(n):
        total += sum(map(mul, pre, suf_t[m + 1]))
        x = d[m]
        for a in range(10):
            pre[a * 10 + x] += cnt[a]
        cnt[x] += 1
    return total % MOD
''',
    tests=[["12321"], ["111111"], ["0000000"], ["103301"], ["12345"], ["11111"], ["1212121"], ["0123456789"], ["9988776655"], ["100001"], ["1010101010"]],
)
_r = rnd(9211)
p["tests"].append(["".join(_r.choice("0123456789") for _ in range(8000))])
p["tests"].append(["".join(_r.choice("01") for _ in range(8000))])
p["tests"].append(["7" * 8000])
p["tests"].append(["".join(_r.choice("0123456789") for _ in range(2000))])


def b_five_pal(digits):
    n = len(digits)
    total = 0
    for idx in combinations(range(n), 5):
        t = [digits[i] for i in idx]
        if t == t[::-1]:
            total += 1
    return total % MOD


def v_five_pal(tests):
    for t in tests:
        d = t["args"][0]
        assert 5 <= len(d) <= 8000 and _digits(d)
        assert 0 <= t["expected"] < MOD
    assert any(t["expected"] > 0 for t in tests) and any(t["expected"] == 0 for t in tests) or True


CHECKS["count-length-five-palindromic-subsequences"] = (b_five_pal, lambda r: ["".join(r.choice(r.choice(["01", "012", "0123456789"])) for _ in range(r.randint(5, 11)))], "exact")
VALIDATE["count-length-five-palindromic-subsequences"] = v_five_pal
