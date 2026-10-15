"""Problems: string algorithms, part C (Manacher and palindromic structure, Lyndon words, compression structure, anagram mapping)."""
from collections import deque

from lib import add, rnd, CHECKS, VALIDATE, gen_arr  # noqa: F401

TOPIC = "String Algorithms"
LET = "abcdefghijklmnopqrstuvwxyz"


def _rs(r, n, alpha="abc"):
    return "".join(r.choice(alpha) for _ in range(n))


def _lower(s):
    return all("a" <= c <= "z" for c in s)


# ---------------------------------------------------------------- EASY

p = add(
    id="anagram-index-mapping-stable", title="Anagram Index Mapping", diff="Easy", topic=TOPIC,
    fn="anagramMapping", params=[("s", "string"), ("t", "string")], ret="int[]", cmp="exact",
    desc="<p>The strings <code>s</code> and <code>t</code> are anagrams: <code>t</code> is some rearrangement of the letters of <code>s</code>. Because letters can repeat, there are many ways to say which position of <code>t</code> each letter of <code>s</code> moved to, so use this canonical one: the <em>k</em>-th occurrence of a letter in <code>s</code> (counting from the left) is mapped to the <em>k</em>-th occurrence of the same letter in <code>t</code>.</p><p>Return the array <code>m</code> of length <code>n</code> where <code>m[i]</code> is the 0-based position in <code>t</code> that the letter <code>s[i]</code> is mapped to. For example, with <code>s = \"abca\"</code> and <code>t = \"caab\"</code> the answer is <code>[1, 3, 0, 2]</code>: the first <code>a</code> of <code>s</code> goes to the first <code>a</code> of <code>t</code> (index 1), <code>b</code> goes to index 3, <code>c</code> to index 0 and the second <code>a</code> to the second <code>a</code> of <code>t</code> (index 2).</p>",
    constraints=["1 &le; s.length = t.length &le; 5,000", "s and t consist of lowercase English letters", "t is a rearrangement of s"],
    hints=["Searching <code>t</code> from scratch for every character of <code>s</code> costs O(n&sup2;). You only need to look at positions of one particular letter.",
           "Collect, for every letter, the list of its positions in <code>t</code> in increasing order.",
           "Walk through <code>s</code> from left to right with one pointer per letter: the letter <code>c</code> takes the next unused position from the list of <code>c</code> in <code>t</code>."],
    editorial=["The canonical mapping pairs equal letters in order of appearance, so it is enough to know, for each letter, where it occurs in <code>t</code>. Build 26 lists of positions by scanning <code>t</code> once. Then scan <code>s</code> once; for the letter <code>c</code> keep a counter <code>used[c]</code> and answer <code>pos[c][used[c]]</code>, then increase the counter.",
               "This takes O(n) time and O(n) extra space. A mapping built by repeated searching (<code>t.index</code> after blanking out used characters) gives the same answer but is quadratic. Note that this particular mapping never makes two equal letters cross each other, which is exactly the property that makes it the cheapest way to turn <code>s</code> into <code>t</code> by adjacent swaps (see the related problem on adjacent swaps)."],
    time="O(n)", space="O(n)",
    solution='''def anagramMapping(s, t):
    pos = {}
    for j, c in enumerate(t):
        pos.setdefault(c, []).append(j)
    used = {c: 0 for c in pos}
    out = []
    for c in s:
        out.append(pos[c][used[c]])
        used[c] += 1
    return out
''',
    tests=[["abca", "caab"], ["a", "a"], ["ab", "ba"], ["aa", "aa"], ["aab", "baa"], ["abc", "cba"], ["aabb", "bbaa"],
           ["abcabc", "cbacba"], ["zzyx", "xyzz"], ["abab", "baba"], ["mississippi", "sipsimipsis"]],
)
_r = rnd(9101)
_s = _rs(_r, 4000, "abc")
_t = list(_s); _r.shuffle(_t)
p["tests"].append([_s, "".join(_t)])
_s = _rs(_r, 3000, LET)
_t = list(_s); _r.shuffle(_t)
p["tests"].append([_s, "".join(_t)])
_s = "a" * 1500 + "b" * 1500
p["tests"].append([_s, "b" * 1500 + "a" * 1500])


def b_anamap(s, t):
    out = []
    for i, c in enumerate(s):
        k = s[:i].count(c)
        seen = -1
        for j, d in enumerate(t):
            if d == c:
                seen += 1
                if seen == k:
                    out.append(j)
                    break
    return out


def g_anamap(r):
    s = _rs(r, r.randint(1, 9), "abc")
    t = list(s)
    r.shuffle(t)
    return [s, "".join(t)]


def v_anamap(tests):
    for t in tests:
        s, u = t["args"]
        assert 1 <= len(s) == len(u) <= 5000 and _lower(s) and _lower(u) and sorted(s) == sorted(u)
        m = t["expected"]
        assert sorted(m) == list(range(len(s))) and all(u[m[i]] == s[i] for i in range(len(s)))


CHECKS["anagram-index-mapping-stable"] = (b_anamap, g_anamap, "exact")
VALIDATE["anagram-index-mapping-stable"] = v_anamap

p = add(
    id="minimum-replacements-to-anagram", title="Minimum Replacements to Form an Anagram", diff="Easy", topic=TOPIC,
    fn="minReplacements", params=[("s", "string"), ("t", "string")], ret="int", cmp="exact",
    desc="<p>You are given two strings <code>s</code> and <code>t</code> of the same length. In one step you may pick any position of <code>t</code> and overwrite its letter with any lowercase letter. Return the minimum number of steps needed so that <code>t</code> becomes an anagram of <code>s</code> (a rearrangement of the letters of <code>s</code>). The positions of letters in <code>t</code> do not matter, only which letters it contains.</p><p>For example, <code>s = \"abc\"</code> and <code>t = \"bcd\"</code> need one step: replace the <code>d</code> by <code>a</code> to get <code>\"bca\"</code>. For <code>s = \"aabb\"</code> and <code>t = \"cccc\"</code> the answer is <code>4</code>.</p>",
    constraints=["1 &le; s.length = t.length &le; 20,000", "s and t consist of lowercase English letters"],
    hints=["Order does not matter, so only the letter counts of the two strings are relevant.",
           "A letter that <code>t</code> has too many of must be overwritten; a letter that <code>t</code> lacks is what it should be overwritten with.",
           "Sum, over all 26 letters, the amount by which the count in <code>s</code> exceeds the count in <code>t</code> (only positive differences)."],
    editorial=["Let <code>cs[c]</code> and <code>ct[c]</code> be the number of occurrences of letter <code>c</code> in <code>s</code> and <code>t</code>. The final string must have exactly <code>cs[c]</code> letters <code>c</code>. If <code>ct[c] &gt; cs[c]</code>, some <code>ct[c] - cs[c]</code> copies of <code>c</code> in <code>t</code> are surplus; if <code>ct[c] &lt; cs[c]</code> that many copies are missing.",
               "Both strings have the same length, so the total surplus equals the total deficit, and each step can fix one surplus letter into one missing letter. Each step changes one letter, so we cannot do better than the total deficit <code>sum(max(0, cs[c] - ct[c]))</code>, and that value is reachable. The solution is two counting passes: O(n) time and O(1) extra space (26 counters)."],
    time="O(n)", space="O(1)",
    solution='''def minReplacements(s, t):
    cnt = [0] * 26
    for c in s:
        cnt[ord(c) - 97] += 1
    for c in t:
        cnt[ord(c) - 97] -= 1
    return sum(x for x in cnt if x > 0)
''',
    tests=[["abc", "bcd"], ["aabb", "cccc"], ["a", "a"], ["a", "b"], ["abc", "cab"], ["aaaa", "aaab"], ["xyz", "abc"],
           ["abcabc", "aabbcc"], ["zzzzzz", "yyyyyy"], ["aabbcc", "abcdef"]],
)
_r = rnd(9102)
p["tests"].append([_rs(_r, 20000, LET), _rs(_r, 20000, LET)])
p["tests"].append(["a" * 20000, "b" * 20000])
p["tests"].append([_rs(_r, 15000, "abc"), _rs(_r, 15000, "bcd")])


def b_minrep(s, t):
    alpha = sorted(set(s))
    best = len(s)
    n = len(s)
    ss = sorted(s)

    def rec(i, cur):
        nonlocal best
        if i == n:
            if sorted(cur) == ss:
                best = min(best, sum(1 for a, b in zip(cur, t) if a != b))
            return
        for c in alpha:
            cur.append(c)
            rec(i + 1, cur)
            cur.pop()

    rec(0, [])
    return best


def g_minrep(r):
    n = r.randint(1, 6)
    return [_rs(r, n, "abc"), _rs(r, n, "abcd")]


def v_minrep(tests):
    for t in tests:
        s, u = t["args"]
        assert 1 <= len(s) == len(u) <= 20000 and _lower(s) and _lower(u)


CHECKS["minimum-replacements-to-anagram"] = (b_minrep, g_minrep, "exact")
VALIDATE["minimum-replacements-to-anagram"] = v_minrep

# ---------------------------------------------------------------- MEDIUM

p = add(
    id="palindrome-radius-array", title="Palindrome Length at Every Center", diff="Medium", topic=TOPIC,
    fn="palindromeLengths", params=[("s", "string")], ret="int[]", cmp="exact",
    desc="<p>A string of length <code>n</code> has <code>2n - 1</code> possible palindrome <em>centers</em>: the <code>n</code> characters themselves and the <code>n - 1</code> gaps between neighbouring characters. Number them <code>0 .. 2n - 2</code> from left to right, so center <code>2i</code> is the character <code>s[i]</code> and center <code>2i + 1</code> is the gap between <code>s[i]</code> and <code>s[i+1]</code>.</p><p>Return an array of length <code>2n - 1</code> whose entry <code>c</code> is the length of the <em>longest palindromic substring centered exactly at center c</em>. For a character center the length is at least <code>1</code>; for a gap center it is <code>0</code> when the two neighbours differ.</p><p>Example: for <code>s = \"abba\"</code> the answer is <code>[1, 0, 1, 4, 1, 0, 1]</code>; the gap between the two <code>b</code> characters is the center of the whole string, a palindrome of length 4.</p>",
    constraints=["1 &le; s.length &le; 4,000", "s consists of lowercase English letters"],
    hints=["Expanding outwards from every center works and is O(n&sup2;) in the worst case (for example on a string of one repeated letter). Which work is repeated?",
           "Insert a separator such as <code>#</code> between all characters (and at both ends) so that odd and even palindromes become one kind: palindromes of the new string centered at each position.",
           "Maintain the palindrome that reaches furthest to the right (center <code>c</code>, right edge <code>r</code>). For a new center <code>i &lt; r</code>, its mirror <code>2c - i</code> already knows a radius that can be copied, capped by <code>r - i</code>; only extend by direct comparison beyond that."],
    editorial=["This is Manacher's algorithm. Transform <code>s</code> into <code>t = #s0#s1#...#</code> of length <code>2n + 1</code>. A palindrome of <code>s</code> centered at a character or a gap corresponds to a palindrome of <code>t</code> centered at a position of <code>t</code>, and its radius in <code>t</code> equals its length in <code>s</code>. So we need <code>rad[i]</code>, the largest <code>r</code> with <code>t[i-r..i+r]</code> a palindrome.",
               "Keep the rightmost-reaching palindrome <code>[c - rad[c], c + rad[c]]</code>. For a new center <code>i</code> inside it, the mirror position <code>2c - i</code> has the same palindromic surroundings as long as we stay inside the big palindrome, so <code>rad[i]</code> starts at <code>min(rad[2c - i], c + rad[c] - i)</code>. Then try to extend by comparing characters; each successful comparison pushes the right edge further, and the right edge only moves forward.",
               "That amortised argument gives O(n) total time and O(n) space. The entries for <code>t</code> positions <code>1 .. 2n - 1</code> are exactly the requested array (position <code>1</code> is the character <code>s[0]</code>, position <code>2</code> the first gap, and so on)."],
    time="O(n)", space="O(n)",
    solution='''def palindromeLengths(s):
    n = len(s)
    t = '#' + '#'.join(s) + '#'
    m = len(t)
    rad = [0] * m
    c = r = 0
    for i in range(m):
        if i < r:
            rad[i] = min(r - i, rad[2 * c - i])
        a, b = i + rad[i] + 1, i - rad[i] - 1
        while b >= 0 and a < m and t[a] == t[b]:
            rad[i] += 1
            a += 1
            b -= 1
        if i + rad[i] > r:
            c, r = i, i + rad[i]
    return rad[1:m - 1]
''',
    tests=[["abba"], ["a"], ["ab"], ["aa"], ["aba"], ["abc"], ["aaaa"], ["abacaba"], ["cabbac"], ["abcbabcba"], ["aabaaabaa"], ["xyzzyxyz"]],
)
_r = rnd(9103)
p["tests"].append(["a" * 3000])
p["tests"].append([_rs(_r, 3500, "ab")])
p["tests"].append([("ab" * 600 + "c") * 2 + "ab" * 600])
p["tests"].append([_rs(_r, 4000, LET)])


def b_pradius(s):
    n = len(s)
    out = []
    for c in range(2 * n - 1):
        i, j = c // 2, c // 2 + c % 2   # innermost pair (equal for a character center)
        best = 0
        for L in range(1, n + 1):
            if (L % 2) != (c % 2 == 0):
                continue
            lo = i - (L - 1) // 2 if c % 2 == 0 else i - L // 2 + 1
            hi = lo + L
            if lo < 0 or hi > n:
                break
            sub = s[lo:hi]
            # palindrome centered exactly at c iff sub is a palindrome and its center is c
            if sub == sub[::-1]:
                best = L
            else:
                break
        out.append(best)
    return out


def g_pradius(r):
    return [_rs(r, r.randint(1, 12), r.choice(["ab", "abc", "a"]))]


def v_pradius(tests):
    for t in tests:
        s = t["args"][0]
        assert 1 <= len(s) <= 4000 and _lower(s)
        assert len(t["expected"]) == 2 * len(s) - 1


CHECKS["palindrome-radius-array"] = (b_pradius, g_pradius, "exact")
VALIDATE["palindrome-radius-array"] = v_pradius

p = add(
    id="largest-suffix-start-index", title="Start of the Largest Suffix", diff="Medium", topic=TOPIC,
    fn="largestSuffixStart", params=[("s", "string")], ret="int", cmp="exact",
    desc="<p>Among all non-empty suffixes of <code>s</code> (the substrings that end at the last character), find the one that comes <em>last</em> in dictionary order and return the 0-based index where it starts. A string that is a proper prefix of another is smaller than it, so for example <code>\"ab\"</code> is smaller than <code>\"abc\"</code>. All suffixes have different lengths and are therefore different strings, so the answer is unique.</p><p>Examples: for <code>s = \"abab\"</code> the suffixes are <code>abab</code>, <code>bab</code>, <code>ab</code>, <code>b</code>; the largest is <code>bab</code>, so the answer is <code>1</code>. For <code>s = \"leetcode\"</code> the answer is <code>3</code>: the suffix <code>tcode</code> starts with the largest letter <code>t</code>.</p>",
    constraints=["1 &le; s.length &le; 20,000", "s consists of lowercase English letters"],
    hints=["Comparing every pair of suffixes directly is O(n&sup2;) per comparison in the worst case, and sorting all suffixes is far too slow for strings like <code>\"aaaa...a\"</code>.",
           "Keep two candidate starts <code>i &lt; j</code> and compare the suffixes character by character, remembering the length <code>k</code> of the common stretch.",
           "If <code>s[i+k] &lt; s[j+k]</code>, then none of the starts <code>i .. i+k</code> can be the maximum (each is beaten by the start shifted by <code>j - i</code>), so jump <code>i</code> past them. If it is larger, jump <code>j</code> by <code>k + 1</code>. Reset <code>k</code> after each jump."],
    editorial=["This is the two-candidate technique behind the minimal-rotation and Lyndon-factorization algorithms, mirrored for the maximum. Maintain candidates <code>i &lt; j</code> and the number <code>k</code> of equal characters already seen after both. Compare <code>s[i+k]</code> and <code>s[j+k]</code>.",
               "Equal: increase <code>k</code>. If <code>s[i+k] &lt; s[j+k]</code>: every start in <code>i .. i+k</code> is smaller than the start shifted by <code>j - i</code>, so skip them: <code>i += k + 1</code>; if that makes <code>i &gt;= j</code>, set <code>j = i + 1</code>. Otherwise symmetrically skip <code>j += k + 1</code>. Reset <code>k = 0</code>. Loop while <code>j + k &lt; n</code> (when the comparison reaches the end of the string the shorter suffix is smaller automatically).",
               "Every jump advances <code>i</code> or <code>j</code> by at least <code>k + 1</code> after spending <code>k</code> comparisons, so the total work is O(n) with O(1) extra space. Answer <code>i</code>."],
    time="O(n)", space="O(1)",
    solution='''def largestSuffixStart(s):
    n = len(s)
    i, j, k = 0, 1, 0
    while j + k < n:
        a, b = s[i + k], s[j + k]
        if a == b:
            k += 1
            continue
        if a < b:
            i += k + 1
            if i >= j:
                j = i + 1
        else:
            j += k + 1
        k = 0
    return i
''',
    tests=[["abab"], ["leetcode"], ["a"], ["ab"], ["ba"], ["aaaa"], ["zzzz"], ["abcabcabc"], ["bab"], ["aabaab"], ["cbacbacb"], ["abzabzab"]],
)
_r = rnd(9104)
p["tests"].append(["a" * 15000])
p["tests"].append(["ab" * 8000])
p["tests"].append(["a" * 9999 + "b" + "a" * 9999])
p["tests"].append([_rs(_r, 20000, "ab")])
p["tests"].append([("abc" * 1500 + "abd") * 2])


def b_lsuf(s):
    return max(range(len(s)), key=lambda i: s[i:])


def g_lsuf(r):
    return [_rs(r, r.randint(1, 12), r.choice(["ab", "abc", "a", "abcd"]))]


def v_lsuf(tests):
    for t in tests:
        s = t["args"][0]
        assert 1 <= len(s) <= 20000 and _lower(s)


CHECKS["largest-suffix-start-index"] = (b_lsuf, g_lsuf, "exact")
VALIDATE["largest-suffix-start-index"] = v_lsuf

p = add(
    id="lyndon-factorization-lengths", title="Lyndon Factorization", diff="Medium", topic=TOPIC,
    fn="lyndonFactors", params=[("s", "string")], ret="int[]", cmp="exact",
    desc="<p>A non-empty string is a <em>Lyndon word</em> if it is strictly smaller (in dictionary order) than each of its proper suffixes. For example <code>\"ab\"</code>, <code>\"aab\"</code> and <code>\"a\"</code> are Lyndon words, while <code>\"ba\"</code>, <code>\"aa\"</code> and <code>\"abab\"</code> are not.</p><p>Every string <code>s</code> can be written in exactly one way as a concatenation <code>w<sub>1</sub> w<sub>2</sub> ... w<sub>k</sub></code> of Lyndon words with <code>w<sub>1</sub> &ge; w<sub>2</sub> &ge; ... &ge; w<sub>k</sub></code> (dictionary order, equal neighbours allowed). Return the lengths <code>|w<sub>1</sub>|, ..., |w<sub>k</sub>|</code> in order.</p><p>Example: <code>s = \"banana\"</code> factorizes as <code>b | an | an | a</code>, so the answer is <code>[1, 2, 2, 1]</code>. For <code>s = \"abab\"</code> the factors are <code>ab | ab</code> and the answer is <code>[2, 2]</code>.</p>",
    constraints=["1 &le; s.length &le; 8,000", "s consists of lowercase English letters"],
    hints=["The first factor <code>w<sub>1</sub></code> is the longest prefix of <code>s</code> that is a Lyndon word. Testing every prefix naively is too slow, so think about growing a prefix and keeping its structure.",
           "Duval's algorithm keeps a pointer <code>i</code> (start of the unfinished part), a position <code>j</code> being examined and a pointer <code>k = j - period</code>. While <code>s[k] &lt;= s[j]</code> the prefix <code>s[i..j]</code> is still (a power of a Lyndon word) plus a prefix of it.",
           "If <code>s[k] &lt; s[j]</code>, the whole block becomes one Lyndon word, so reset <code>k = i</code>; if equal, advance <code>k</code>. When the loop stops, emit the repeated Lyndon word of length <code>j - k</code> as many times as it fits starting from <code>i</code>, then restart from the first position not yet emitted."],
    editorial=["Duval's algorithm. Let the current unprocessed part start at <code>i</code>. Scan with <code>j = i + 1</code> and <code>k = i</code>, where the invariant is that <code>s[i..j-1]</code> is of the form <code>u<sup>m</sup>u'</code> with <code>u</code> a Lyndon word of length <code>j - k</code> and <code>u'</code> a proper prefix of <code>u</code>.",
               "While <code>j &lt; n</code> and <code>s[k] &le; s[j]</code>: if <code>s[k] &lt; s[j]</code> the extended string is itself a Lyndon word (the period becomes the whole length), so <code>k = i</code>; otherwise (equal) just <code>k += 1</code>; then <code>j += 1</code>. When the loop stops, the factor length is <code>L = j - k</code>. Output <code>L</code> repeatedly while <code>i &le; k</code>, advancing <code>i</code> by <code>L</code> each time; the leftover <code>u'</code> is processed again from the new <code>i</code>.",
               "Each character is re-examined only a bounded number of times: at most twice overall, so the total running time is O(n) and the extra space is O(1) besides the output."],
    time="O(n)", space="O(1)",
    solution='''def lyndonFactors(s):
    n = len(s)
    i = 0
    out = []
    while i < n:
        j, k = i + 1, i
        while j < n and s[k] <= s[j]:
            k = i if s[k] < s[j] else k + 1
            j += 1
        L = j - k
        while i <= k:
            out.append(L)
            i += L
    return out
''',
    tests=[["banana"], ["abab"], ["a"], ["ba"], ["ab"], ["aaaa"], ["dcba"], ["abcd"], ["aabaab"], ["cbacbaab"], ["abaabaaab"], ["zazbza"], ["abcabcabx"]],
)
_r = rnd(9105)
p["tests"].append(["a" * 6000])
p["tests"].append(["ab" * 4000])
p["tests"].append([_rs(_r, 8000, "ab")])
p["tests"].append([_rs(_r, 7000, "abc")])


def _is_lyndon(w):
    return all(w < w[i:] for i in range(1, len(w)))


def b_lyn(s):
    out = []
    pos = 0
    n = len(s)
    while pos < n:
        m = max(m for m in range(1, n - pos + 1) if _is_lyndon(s[pos:pos + m]))
        out.append(m)
        pos += m
    return out


def g_lyn(r):
    return [_rs(r, r.randint(1, 12), r.choice(["ab", "abc", "a", "abcd"]))]


def v_lyn(tests):
    for t in tests:
        s = t["args"][0]
        assert 1 <= len(s) <= 8000 and _lower(s)
        ls = t["expected"]
        assert sum(ls) == len(s)
        if len(s) <= 400:
            pos, prev = 0, None
            for L in ls:
                w = s[pos:pos + L]
                assert _is_lyndon(w) and (prev is None or prev >= w)
                prev = w
                pos += L


CHECKS["lyndon-factorization-lengths"] = (b_lyn, g_lyn, "exact")
VALIDATE["lyndon-factorization-lengths"] = v_lyn

p = add(
    id="compare-run-length-encoded", title="Compare Run-Length Encoded Strings", diff="Medium", topic=TOPIC,
    fn="compareEncoded", params=[("a", "int[][]"), ("b", "int[][]")], ret="int", cmp="exact",
    desc="<p>Two very long strings are stored in run-length form. A string is given as a list of runs, each run <code>[c, k]</code> meaning the letter with code <code>c</code> (<code>1</code> = <code>a</code>, <code>2</code> = <code>b</code>, ..., <code>26</code> = <code>z</code>) repeated <code>k</code> times; the string is the concatenation of all runs in order. Neighbouring runs may use the same letter, so the same string can be written in many different ways: <code>[[1,2],[1,3]]</code> and <code>[[1,5]]</code> both mean <code>aaaaa</code>.</p><p>Compare the two decoded strings in dictionary order and return <code>-1</code> if <code>a</code> is smaller, <code>1</code> if <code>a</code> is larger and <code>0</code> if they are equal. A string that is a proper prefix of the other counts as smaller. The decoded strings can be far too long to build (the run counts go up to a billion).</p><p>Example: <code>a = [[1,2],[2,1]]</code> (<code>aab</code>) and <code>b = [[1,1],[1,1],[3,1]]</code> (<code>aac</code>) give <code>-1</code>.</p>",
    constraints=["1 &le; a.length, b.length &le; 2,000", "each run is [c, k] with 1 &le; c &le; 26 and 1 &le; k &le; 1,000,000,000", "the decoded strings may be much longer than 2<sup>31</sup>; do not build them"],
    hints=["Decoding both strings is impossible for counts near a billion. Compare run by run instead of letter by letter.",
           "Walk through both lists with two pointers, each holding the current letter and how many copies of it are still unconsumed.",
           "If the current letters differ, the answer is decided by them. Otherwise consume <code>min(remaining_a, remaining_b)</code> copies from both and move on when a run is used up. Whichever string ends first (with the other still having letters) is the smaller one."],
    editorial=["Treat each list as a stream of letters, but consume it in bulk. Keep for each string the index of its current run and the number of copies left in it. While both streams have letters, compare the current letters: if they differ, the string with the smaller letter is smaller and we are done. If they are equal, remove <code>t = min(left_a, left_b)</code> copies from both; at least one run is exhausted, so we advance at least one pointer per step.",
               "When one stream runs dry first, the other either also ends at that moment (equal strings, answer 0) or still has letters (the exhausted one is a proper prefix, so it is smaller). Adjacent runs with the same letter need no special treatment because we only ever compare current letters.",
               "The loop performs at most <code>|a| + |b|</code> steps: O(|a| + |b|) time, O(1) extra space. Counts can sum to far more than 32 bits, so languages with fixed-width integers must keep the counts per run and never add them up."],
    time="O(|a| + |b|)", space="O(1)",
    solution='''def compareEncoded(a, b):
    i = j = 0
    ra = a[0][1]
    rb = b[0][1]
    while i < len(a) and j < len(b):
        ca, cb = a[i][0], b[j][0]
        if ca != cb:
            return -1 if ca < cb else 1
        t = min(ra, rb)
        ra -= t
        rb -= t
        if ra == 0:
            i += 1
            if i < len(a):
                ra = a[i][1]
        if rb == 0:
            j += 1
            if j < len(b):
                rb = b[j][1]
    if i == len(a) and j == len(b):
        return 0
    return -1 if i == len(a) else 1
''',
    tests=[[[[1, 2], [2, 1]], [[1, 1], [1, 1], [3, 1]]], [[[1, 2], [1, 3]], [[1, 5]]], [[[1, 1]], [[1, 1]]], [[[1, 3]], [[1, 4]]],
           [[[1, 4]], [[1, 3]]], [[[2, 1]], [[1, 1000000000]]], [[[1, 1000000000], [2, 1]], [[1, 999999999], [1, 1], [2, 2]]],
           [[[26, 1000000000]], [[26, 1000000000]]], [[[1, 5], [2, 5]], [[1, 5], [2, 4], [3, 1]]], [[[3, 2], [1, 7]], [[3, 1], [3, 1], [1, 6], [1, 1]]],
           [[[1, 1000000000], [1, 1000000000], [5, 3]], [[1, 1000000000], [1, 1000000000], [5, 2]]], [[[1, 1], [2, 1], [1, 1]], [[1, 1], [2, 1]]]],
)
_r = rnd(9106)
_runs = [[_r.randint(1, 3), _r.randint(1, 1000000000)] for _ in range(900)]
_split = []
for c, k in _runs:
    if k >= 3 and _r.random() < 0.7:
        x = _r.randint(1, k - 1)
        _split += [[c, x], [c, k - x]]
    else:
        _split.append([c, k])
p["tests"].append([_runs, _split])
_split2 = [list(x) for x in _split]
_q = 700
_split2[_q] = [_split2[_q][0], _split2[_q][1] + 1] if _split2[_q][1] < 10 ** 9 else [_split2[_q][0], _split2[_q][1] - 1]
p["tests"].append([_runs, _split2])
_big_a = [[_r.randint(1, 26), _r.randint(1, 1000000000)] for _ in range(1000)]
_big_b = [list(x) for x in _big_a] + [[1, 1]]
p["tests"].append([_big_a, _big_b])
_ra = [[_r.randint(1, 2), _r.randint(1, 5)] for _ in range(1500)]
_rb = [[_r.randint(1, 2), _r.randint(1, 5)] for _ in range(1500)]
p["tests"].append([_ra, _rb])


def _dec(runs):
    return "".join(chr(96 + c) * k for c, k in runs)


def b_cmpenc(a, b):
    x, y = _dec(a), _dec(b)
    return -1 if x < y else (1 if x > y else 0)


def g_cmpenc(r):
    def mk():
        return [[r.randint(1, 3), r.randint(1, 4)] for _ in range(r.randint(1, 4))]
    a = mk()
    if r.random() < 0.4:
        b = []
        for c, k in a:
            if k > 1 and r.random() < 0.6:
                x = r.randint(1, k - 1)
                b += [[c, x], [c, k - x]]
            else:
                b.append([c, k])
        if r.random() < 0.5:
            b.append([r.randint(1, 3), r.randint(1, 2)])
        return [a, b]
    return [a, mk()]


def v_cmpenc(tests):
    seen = set()
    for t in tests:
        a, b = t["args"]
        assert 1 <= len(a) <= 2000 and 1 <= len(b) <= 2000
        for c, k in a + b:
            assert 1 <= c <= 26 and 1 <= k <= 10 ** 9
        seen.add(t["expected"])
    assert seen == {-1, 0, 1}


CHECKS["compare-run-length-encoded"] = (b_cmpenc, g_cmpenc, "exact")
VALIDATE["compare-run-length-encoded"] = v_cmpenc

p = add(
    id="min-adjacent-swaps-to-anagram", title="Minimum Adjacent Swaps to Reach an Anagram", diff="Medium", topic=TOPIC,
    fn="minAdjacentSwaps", params=[("s", "string"), ("t", "string")], ret="int", cmp="exact",
    desc="<p>The strings <code>s</code> and <code>t</code> are anagrams of each other. In one move you may swap two <em>neighbouring</em> characters of <code>s</code>. Return the minimum number of moves needed to turn <code>s</code> into exactly <code>t</code>.</p><p>Example: <code>s = \"aabb\"</code> and <code>t = \"bbaa\"</code> need <code>4</code> moves (each of the two <code>b</code> letters has to pass both <code>a</code> letters). <code>s = \"abc\"</code> and <code>t = \"cba\"</code> need <code>3</code> moves.</p>",
    constraints=["1 &le; s.length = t.length &le; 8,000", "s and t consist of lowercase English letters", "t is a rearrangement of s"],
    hints=["A breadth-first search over all reachable strings is hopeless. First decide <em>which</em> letter of <code>s</code> becomes <em>which</em> letter of <code>t</code>.",
           "Equal letters should never be swapped with each other. So the <em>k</em>-th <code>c</code> of <code>s</code> should end at the position of the <em>k</em>-th <code>c</code> of <code>t</code>. This gives you a permutation of positions.",
           "The minimum number of adjacent swaps that sorts a permutation equals its number of inversions. Count them in O(n log n) with a Fenwick tree or merge sort."],
    editorial=["Map every position of <code>s</code> to a target position in <code>t</code> by matching equal letters in order (the <em>k</em>-th occurrence of a letter to the <em>k</em>-th occurrence in <code>t</code>). Matching in order is optimal because swapping two equal letters never helps, and any other matching would cross two equal letters which only adds inversions.",
               "After the mapping, <code>perm[i]</code> is the final position of the letter now at <code>i</code>. Each adjacent swap changes the number of inversions of <code>perm</code> by exactly one, and the target (identity permutation) has none, so the answer is the number of inversions of <code>perm</code>: pairs <code>i &lt; j</code> with <code>perm[i] &gt; perm[j]</code>.",
               "Count inversions with a Fenwick tree: scan left to right, add the number of earlier elements larger than the current one, then insert the current one. That gives O(n log n) time and O(n) space. The result may be about n&sup2;/4, i.e. up to 16 million here."],
    time="O(n log n)", space="O(n)",
    solution='''def minAdjacentSwaps(s, t):
    n = len(s)
    pos = {}
    for j in range(n - 1, -1, -1):
        pos.setdefault(t[j], []).append(j)
    perm = [pos[c].pop() for c in s]
    tree = [0] * (n + 2)
    inv = 0
    for idx, v in enumerate(perm):
        # count earlier elements with value <= v
        x = v + 1
        le = 0
        while x > 0:
            le += tree[x]
            x -= x & -x
        inv += idx - le
        x = v + 1
        while x <= n:
            tree[x] += 1
            x += x & -x
    return inv
''',
    tests=[["aabb", "bbaa"], ["abc", "cba"], ["a", "a"], ["ab", "ba"], ["aa", "aa"], ["abab", "abab"], ["abab", "baba"], ["aaabbb", "bbbaaa"],
           ["abcabc", "cbacba"], ["aabbcc", "ccbbaa"], ["abcd", "dcba"]],
)
_r = rnd(9107)
_s = _rs(_r, 8000, "abc")
_t = list(_s); _r.shuffle(_t)
p["tests"].append([_s, "".join(_t)])
p["tests"].append(["a" * 4000 + "b" * 4000, "b" * 4000 + "a" * 4000])
_s = _rs(_r, 7000, LET)
_t = list(_s); _r.shuffle(_t)
p["tests"].append([_s, "".join(_t)])


def b_adjswap(s, t):
    if s == t:
        return 0
    seen = {s}
    dq = deque([(s, 0)])
    while dq:
        u, d = dq.popleft()
        for i in range(len(u) - 1):
            if u[i] != u[i + 1]:
                v = u[:i] + u[i + 1] + u[i] + u[i + 2:]
                if v == t:
                    return d + 1
                if v not in seen:
                    seen.add(v)
                    dq.append((v, d + 1))
    return -1


def g_adjswap(r):
    s = _rs(r, r.randint(1, 7), r.choice(["ab", "abc"]))
    t = list(s)
    r.shuffle(t)
    return [s, "".join(t)]


def v_adjswap(tests):
    for t in tests:
        s, u = t["args"]
        assert 1 <= len(s) == len(u) <= 8000 and _lower(s) and _lower(u) and sorted(s) == sorted(u)
        assert t["expected"] >= 0


CHECKS["min-adjacent-swaps-to-anagram"] = (b_adjswap, g_adjswap, "exact")
VALIDATE["min-adjacent-swaps-to-anagram"] = v_adjswap

p = add(
    id="count-distinct-palindromic-substrings", title="Count Distinct Palindromic Substrings", diff="Medium", topic=TOPIC, tier="extra",
    fn="countDistinctPalindromes", params=[("s", "string")], ret="int", cmp="exact",
    desc="<p>Return the number of <em>different</em> non-empty palindromic substrings of <code>s</code>. A substring that occurs at several places is counted once.</p><p>For example, <code>s = \"aaa\"</code> has three distinct palindromic substrings (<code>a</code>, <code>aa</code>, <code>aaa</code>), and <code>s = \"abaab\"</code> has five: <code>a</code>, <code>b</code>, <code>aba</code>, <code>aa</code>, <code>baab</code>.</p>",
    constraints=["1 &le; s.length &le; 20,000", "s consists of lowercase English letters"],
    hints=["Storing every palindromic substring in a set takes O(n&sup2;) time and memory in the worst case. Try to bound how many <em>new</em> palindromes a single new character can create.",
           "Appending one character to a string creates at most one new distinct palindromic substring: the longest palindromic suffix is the only candidate, all shorter palindromic suffixes already occurred earlier.",
           "Build a palindromic tree (eertree): nodes are distinct palindromes, edges add the same character on both sides, and a suffix link points to the longest proper palindromic suffix. The number of nodes (minus the two roots) is the answer."],
    editorial=["Claim: when you append the character <code>s[i]</code>, at most one new palindrome appears. Any new palindromic suffix other than the longest one is a prefix-mirror of a longer palindromic suffix, hence it already occurred earlier in the string. So the total number of distinct palindromes is at most <code>n</code>, and we only have to detect whether the longest palindromic suffix of <code>s[0..i]</code> is new.",
               "The eertree has two roots (length <code>-1</code> and length <code>0</code>), and for each node a map of children by letter and a suffix link. To process <code>s[i]</code>: start from the node of the longest palindromic suffix of the previous prefix and follow suffix links until a node <code>v</code> with <code>s[i - len(v) - 1] == s[i]</code>. If the child by <code>s[i]</code> exists, move to it. Otherwise create it with length <code>len(v) + 2</code> and compute its suffix link by following links from <code>link[v]</code> in the same way.",
               "Both walks are amortised O(1) per character because the depth of the 'current suffix' node increases by at most one per step. Total time O(n) (times the alphabet size for the children dictionaries) and O(n) space. The answer is the number of nodes created."],
    time="O(n)", space="O(n)",
    solution='''def countDistinctPalindromes(s):
    length = [-1, 0]
    link = [0, 0]
    nxt = [{}, {}]
    last = 1
    for i, ch in enumerate(s):
        cur = last
        while True:
            l = length[cur]
            if i - l - 1 >= 0 and s[i - l - 1] == ch:
                break
            cur = link[cur]
        if ch in nxt[cur]:
            last = nxt[cur][ch]
            continue
        new = len(length)
        length.append(length[cur] + 2)
        nxt.append({})
        if length[new] == 1:
            link.append(1)
        else:
            q = link[cur]
            while True:
                l = length[q]
                if i - l - 1 >= 0 and s[i - l - 1] == ch:
                    break
                q = link[q]
            link.append(nxt[q][ch])
        nxt[cur][ch] = new
        last = new
    return len(length) - 2
''',
    tests=[["aaa"], ["abaab"], ["a"], ["ab"], ["abc"], ["abba"], ["abacaba"], ["aabaa"], ["abcabcabc"], ["zzzyzzz"], ["abababab"], ["aabbaabb"]],
)
_r = rnd(9108)
p["tests"].append(["a" * 20000])
p["tests"].append([_rs(_r, 20000, "ab")])
p["tests"].append([_rs(_r, 20000, LET)])
p["tests"].append([("ab" * 2500 + "c") * 3 + "ba" * 2000])


def b_dpal(s):
    seen = set()
    n = len(s)
    for i in range(n):
        for j in range(i + 1, n + 1):
            sub = s[i:j]
            if sub == sub[::-1]:
                seen.add(sub)
    return len(seen)


def g_dpal(r):
    return [_rs(r, r.randint(1, 14), r.choice(["ab", "abc", "a"]))]


def v_dpal(tests):
    for t in tests:
        s = t["args"][0]
        assert 1 <= len(s) <= 20000 and _lower(s)
        assert 1 <= t["expected"] <= len(s)


CHECKS["count-distinct-palindromic-substrings"] = (b_dpal, g_dpal, "exact")
VALIDATE["count-distinct-palindromic-substrings"] = v_dpal

# ---------------------------------------------------------------- HARD

p = add(
    id="max-product-two-disjoint-odd-palindromes", title="Product of Two Disjoint Odd Palindromes", diff="Hard", topic=TOPIC,
    fn="maxPalindromeProduct", params=[("s", "string")], ret="int", cmp="exact",
    desc="<p>Choose two non-overlapping substrings of <code>s</code>, both palindromes of <em>odd</em> length. Non-overlapping means they share no position; they do not have to be adjacent. Return the largest possible product of their lengths.</p><p>Example: for <code>s = \"ababbb\"</code> pick <code>aba</code> and <code>bbb</code> and get <code>3 * 3 = 9</code>. For <code>s = \"zaaaxbbby\"</code> pick <code>aaa</code> and <code>bbb</code> for <code>9</code>.</p>",
    constraints=["2 &le; s.length &le; 6,000", "s consists of lowercase English letters"],
    hints=["Any single character is an odd palindrome, so a valid answer always exists. Split the string at a boundary: the best pair is (best palindrome entirely to the left) times (best palindrome entirely to the right) for some boundary.",
           "You need, for every position, the longest odd palindrome that ends exactly there and the longest that starts exactly there. Manacher's algorithm gives the longest odd palindrome around every center in O(n).",
           "A palindrome of length <code>L</code> ending at <code>e</code> implies one of length <code>L - 2</code> ending at <code>e - 1</code> (same center). Propagate this with a single sweep, then take prefix maxima from the left and suffix maxima from the right, and maximise <code>left[i] * right[i + 1]</code>."],
    editorial=["Run Manacher's algorithm for odd palindromes: <code>d[c]</code> is the number of palindromes centered at <code>c</code>, so the longest has length <code>2 d[c] - 1</code> and ends at <code>c + d[c] - 1</code>. Set <code>endAt[c + d[c] - 1]</code> to at least that length and <code>startAt[c - d[c] + 1]</code> likewise.",
               "Shrinking a palindrome by one letter on each side keeps its center, so a palindrome of length <code>L</code> ending at <code>e</code> gives one of length <code>L - 2</code> ending at <code>e - 1</code>. Hence sweeping right to left with <code>endAt[i] = max(endAt[i], endAt[i + 1] - 2)</code> yields the longest odd palindrome ending exactly at every index; the mirrored sweep gives <code>startAt</code>. Initialise both with 1 (single letters).",
               "Let <code>pre[i]</code> be the maximum of <code>endAt[0..i]</code> and <code>suf[i]</code> the maximum of <code>startAt[i..n-1]</code>. The two palindromes are separated by some boundary, so the answer is the maximum of <code>pre[i] * suf[i + 1]</code> over <code>i = 0 .. n-2</code>. Total O(n) time and space. The product is at most about 9 million for n = 6000."],
    time="O(n)", space="O(n)",
    solution='''def maxPalindromeProduct(s):
    n = len(s)
    d = [0] * n
    l, r = 0, -1
    for i in range(n):
        k = 1 if i > r else min(d[l + r - i], r - i + 1)
        while i - k >= 0 and i + k < n and s[i - k] == s[i + k]:
            k += 1
        d[i] = k
        if i + k - 1 > r:
            l, r = i - k + 1, i + k - 1
    end = [1] * n
    start = [1] * n
    for i in range(n):
        e = i + d[i] - 1
        if 2 * d[i] - 1 > end[e]:
            end[e] = 2 * d[i] - 1
        b = i - d[i] + 1
        if 2 * d[i] - 1 > start[b]:
            start[b] = 2 * d[i] - 1
    for i in range(n - 2, -1, -1):
        if end[i + 1] - 2 > end[i]:
            end[i] = end[i + 1] - 2
    for i in range(1, n):
        if start[i - 1] - 2 > start[i]:
            start[i] = start[i - 1] - 2
    pre = end[:]
    for i in range(1, n):
        pre[i] = max(pre[i], pre[i - 1])
    suf = start[:]
    for i in range(n - 2, -1, -1):
        suf[i] = max(suf[i], suf[i + 1])
    return max(pre[i] * suf[i + 1] for i in range(n - 1))
''',
    tests=[["ababbb"], ["zaaaxbbby"], ["ab"], ["aa"], ["aaa"], ["abc"], ["aaaaaa"], ["abcba"], ["abacabadabacaba"], ["xaabaax"], ["aaabaaaabbb"], ["racecarannakayak"]],
)
_r = rnd(9109)
p["tests"].append(["a" * 6000])
p["tests"].append([_rs(_r, 6000, "ab")])
p["tests"].append([_rs(_r, 6000, LET)])
p["tests"].append(["a" * 2999 + "b" + "a" * 2999 + "c" * 1])


def b_mp(s):
    n = len(s)
    pals = []
    for i in range(n):
        for j in range(i, n, 2):
            sub = s[i:j + 1]
            if sub == sub[::-1]:
                pals.append((i, j))
    best = 0
    for a in pals:
        for b in pals:
            if a[1] < b[0]:
                best = max(best, (a[1] - a[0] + 1) * (b[1] - b[0] + 1))
    return best


def g_mp(r):
    return [_rs(r, r.randint(2, 13), r.choice(["ab", "abc", "a"]))]


def v_mp(tests):
    for t in tests:
        s = t["args"][0]
        assert 2 <= len(s) <= 6000 and _lower(s)
        assert t["expected"] >= 1


CHECKS["max-product-two-disjoint-odd-palindromes"] = (b_mp, g_mp, "exact")
VALIDATE["max-product-two-disjoint-odd-palindromes"] = v_mp

p = add(
    id="longest-near-palindrome-substring", title="Longest Substring Within K Mismatches of a Palindrome", diff="Hard", topic=TOPIC,
    fn="longestNearPalindrome", params=[("s", "string"), ("k", "int")], ret="int", cmp="exact",
    desc="<p>For a string <code>w</code>, call a pair of positions <code>(i, |w| - 1 - i)</code> with <code>i &lt; |w| - 1 - i</code> a <em>mirror pair</em>. The string is <em>k-close to a palindrome</em> if at most <code>k</code> of its mirror pairs hold different letters (equivalently, you can make it a palindrome by changing at most <code>k</code> letters).</p><p>Return the length of the longest substring of <code>s</code> that is k-close to a palindrome.</p><p>Example: for <code>s = \"abcde\"</code> and <code>k = 1</code> the answer is <code>3</code> (<code>abc</code> has one differing pair); with <code>k = 2</code> the answer is <code>5</code>. With <code>k = 0</code> this is the usual longest palindromic substring.</p>",
    constraints=["1 &le; s.length &le; 2,000", "0 &le; k &le; 3", "s consists of lowercase English letters"],
    hints=["For a fixed center, extend outwards and count mirror pairs that differ; stop when more than <code>k</code> differ. Doing this letter by letter is O(n&sup2;) on strings like <code>\"aaaa...\"</code>.",
           "Between two mismatches the extension is just a longest-common-extension query: how far do <code>s</code> read leftwards from <code>l</code> and <code>s</code> read rightwards from <code>r</code> agree? That is the longest common prefix of the reversed string and the original string at two positions.",
           "Answer such queries in O(log n) with prefix hashes and binary search. For each of the <code>2n - 1</code> centers, jump over the matching stretch, spend one of the <code>k</code> allowed mismatches on the next pair, and repeat at most <code>k + 1</code> times."],
    editorial=["Fix a center (a character or a gap). The substring around it is determined by how far we extend. Walking outward, a mirror pair either matches or is a mismatch. The longest extension that uses at most <code>k</code> mismatches is found by alternating <em>maximal runs of matches</em> and <em>single mismatches</em>: at most <code>k + 1</code> runs.",
               "A run of matches starting at positions <code>l</code> (going left) and <code>r</code> (going right) has length equal to the longest common prefix of <code>reverse(s)</code> starting at <code>n - 1 - l</code> and <code>s</code> starting at <code>r</code>. Compute it by binary search on a polynomial rolling hash (use a modulus such as 2<sup>61</sup> - 1 to make collisions negligible) or with a suffix array and sparse table for a deterministic version.",
               "For each center do up to <code>k + 1</code> LCE queries, so the total is O(n k log n) time and O(n) space. The answer is the largest extension over all centers, where the final substring length is <code>r - l - 1</code> for the first unusable pair <code>(l, r)</code>."],
    time="O(n k log n)", space="O(n)",
    solution='''def longestNearPalindrome(s, k):
    n = len(s)
    M = (1 << 61) - 1
    B = 911382323
    pw = [1] * (n + 1)
    for i in range(n):
        pw[i + 1] = pw[i] * B % M
    rs = s[::-1]

    def prefix(x):
        h = [0] * (n + 1)
        for i, ch in enumerate(x):
            h[i + 1] = (h[i] * B + ord(ch)) % M
        return h

    hs, hr = prefix(s), prefix(rs)

    def sub(h, a, ln):
        return (h[a + ln] - h[a] * pw[ln]) % M

    def lce(l, r):
        # number of t >= 0 with s[l - u] == s[r + u] for all u < t
        mx = min(l + 1, n - r)
        lo, hi = 0, mx
        a = n - 1 - l
        while lo < hi:
            mid = (lo + hi + 1) // 2
            if sub(hr, a, mid) == sub(hs, r, mid):
                lo = mid
            else:
                hi = mid - 1
        return lo

    best = 1
    for c in range(2 * n - 1):
        l = c // 2
        r = l + (c % 2)
        if c % 2 == 0:
            l -= 1
            r += 1
        rem = k
        while l >= 0 and r < n:
            t = lce(l, r)
            l -= t
            r += t
            if l < 0 or r >= n or rem == 0:
                break
            rem -= 1
            l -= 1
            r += 1
        length = r - l - 1
        if length > best:
            best = length
    return best
''',
    tests=[["abcde", 1], ["abcde", 2], ["abcde", 0], ["a", 0], ["a", 3], ["ab", 0], ["ab", 1], ["abca", 0], ["abca", 1], ["aaaa", 0],
           ["abcdefg", 3], ["xyzzyabcba", 1], ["abacabadabacaba", 0], ["abcbaabxba", 2]],
)
_r = rnd(9110)
p["tests"].append(["a" * 2000, 0])
p["tests"].append([_rs(_r, 2000, "ab"), 3])
p["tests"].append([_rs(_r, 2000, LET), 2])
p["tests"].append(["a" * 1000 + "b" + "a" * 999, 1])


def b_near(s, k):
    n = len(s)
    best = 1
    for i in range(n):
        for j in range(i, n):
            w = s[i:j + 1]
            bad = sum(1 for q in range(len(w) // 2) if w[q] != w[-1 - q])
            if bad <= k:
                best = max(best, len(w))
    return best


def g_near(r):
    return [_rs(r, r.randint(1, 13), r.choice(["ab", "abc", "abcd"])), r.randint(0, 3)]


def v_near(tests):
    for t in tests:
        s, k = t["args"]
        assert 1 <= len(s) <= 2000 and _lower(s) and 0 <= k <= 3
        assert 1 <= t["expected"] <= len(s)


CHECKS["longest-near-palindrome-substring"] = (b_near, g_near, "exact")
VALIDATE["longest-near-palindrome-substring"] = v_near

p = add(
    id="shortest-nested-encoding-length", title="Shortest Nested Repetition Encoding", diff="Hard", topic=TOPIC,
    fn="shortestEncodingLength", params=[("s", "string")], ret="int", cmp="exact",
    desc="<p>An <em>encoding</em> of a string is a sequence of pieces, where a piece is either a single lowercase letter or <code>k[E]</code> with an integer <code>k &ge; 2</code> (written in decimal without leading zeros) followed by a non-empty encoding <code>E</code> in square brackets; <code>k[E]</code> stands for the decoding of <code>E</code> repeated <code>k</code> times. Pieces can be nested. The length of an encoding is the number of characters it is written with, counting digits and brackets.</p><p>Return the length of the <strong>shortest</strong> encoding that decodes to <code>s</code>. Always possible: <code>s</code> itself (all letters) is an encoding.</p><p>Examples: <code>\"abababab\"</code> becomes <code>4[ab]</code> (length 5); <code>\"aaaaaaaaaabaaaaaaaaaab\"</code> becomes <code>2[10[a]b]</code> (length 9); <code>\"abcd\"</code> stays as is (length 4).</p>",
    constraints=["1 &le; s.length &le; 120", "s consists of lowercase English letters"],
    hints=["Encodings are recursive, so think of the best encoding of every substring <code>s[i..j]</code> as a subproblem (interval DP).",
           "A substring's best encoding is either: the substring itself, a concatenation of the best encodings of two parts, or a repetition <code>k[E]</code> where the substring is some block repeated <code>k</code> times.",
           "For the repetition case, find the smallest period <code>p</code> of the substring that divides its length (the first position where the substring re-appears inside <code>sub + sub</code>). If <code>p</code> is smaller than the length, the cost is <code>digits(k) + 2 + best(block)</code> with <code>k = length / p</code>."],
    editorial=["Let <code>f[i][j]</code> be the shortest encoding length of <code>s[i..j]</code>. A single letter costs 1. Otherwise the candidates are (a) the raw length <code>j - i + 1</code>, (b) a split <code>f[i][m] + f[m+1][j]</code> for every <code>m</code>, and (c) a repetition: if the substring equals a block <code>u</code> repeated <code>k &ge; 2</code> times, then <code>digits(k) + 2 + f[block]</code>.",
               "For (c) only the shortest block (the smallest period dividing the length) needs to be tried. A longer block <code>u<sup>m</sup></code> repeated <code>k'</code> times can only be encoded as <code>k'[...]</code> around an encoding of <code>u<sup>m</sup></code>, and that costs at least as much as <code>k'm</code> written once around the encoding of <code>u</code>, since <code>digits(k' m) &le; digits(k') + digits(m)</code> and the extra brackets cost two more. To find the smallest period, search <code>sub</code> inside <code>sub + sub</code> starting from offset 1; the first hit is the period (equal to the length if the substring is not periodic).",
               "Interval DP is O(n<sup>3</sup>) for the splits plus O(n) per interval for the period test, so O(n<sup>3</sup>) overall with n &le; 120, and O(n<sup>2</sup>) space. Process intervals by increasing length so that every sub-interval is ready."],
    time="O(n^3)", space="O(n^2)",
    solution='''def shortestEncodingLength(s):
    n = len(s)
    f = [[0] * n for _ in range(n)]
    for L in range(1, n + 1):
        for i in range(n - L + 1):
            j = i + L - 1
            if L == 1:
                f[i][j] = 1
                continue
            best = L
            fi = f[i]
            for m in range(i, j):
                v = fi[m] + f[m + 1][j]
                if v < best:
                    best = v
            sub = s[i:j + 1]
            idx = (sub + sub).find(sub, 1)
            if idx < L:
                v = len(str(L // idx)) + 2 + f[i][i + idx - 1]
                if v < best:
                    best = v
            f[i][j] = best
    return f[0][n - 1]
''',
    tests=[["abababab"], ["aaaaaaaaaabaaaaaaaaaab"], ["abcd"], ["a"], ["aa"], ["aaaaaaaaaa"], ["aabaab"], ["abcabcabcabcx"],
           ["abbbabbbabbbabbbabbb"], ["xyxyxyxyzxyxyxyxyz"]],
)
_r = rnd(9111)
p["tests"].append(["a" * 120])
p["tests"].append([("ab" * 5 + "c") * 10 + "d"])
p["tests"].append([("a" * 9 + "b") * 12])
p["tests"].append([_rs(_r, 120, "ab")])
p["tests"].append([(_rs(_r, 6, "abc") * 4 + "z") * 4 + _rs(_r, 12, "ab")])


def b_enc(s):
    memo = {}

    def go(u):
        if u in memo:
            return memo[u]
        n = len(u)
        best = n
        for m in range(1, n):
            best = min(best, go(u[:m]) + go(u[m:]))
        for d in range(1, n):
            if n % d == 0 and u == u[:d] * (n // d):
                best = min(best, len(str(n // d)) + 2 + go(u[:d]))
        memo[u] = best
        return best

    return go(s)


def g_enc(r):
    if r.random() < 0.5:
        u = _rs(r, r.randint(1, 3), "ab")
        s = u * r.randint(1, 5)
        if r.random() < 0.5:
            s += _rs(r, r.randint(0, 3), "ab")
        return [s[:11]]
    return [_rs(r, r.randint(1, 10), "ab")]


def v_enc(tests):
    for t in tests:
        s = t["args"][0]
        assert 1 <= len(s) <= 120 and _lower(s)
        assert 1 <= t["expected"] <= len(s)


CHECKS["shortest-nested-encoding-length"] = (b_enc, g_enc, "exact")
VALIDATE["shortest-nested-encoding-length"] = v_enc

for _p in __import__("lib").P:
    if _p["id"] in ("lyndon-factorization-lengths", "longest-near-palindrome-substring", "shortest-nested-encoding-length",
                    "largest-suffix-start-index", "compare-run-length-encoded", "min-adjacent-swaps-to-anagram"):
        _p["tier"] = "extra"
