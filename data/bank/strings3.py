"""Problems: string algorithms (KMP, Z-function, rotations, hashing, suffix automaton). See data/lib.py for the registry."""
from lib import add, rnd, CHECKS, VALIDATE, gen_arr  # noqa: F401

TOPIC = "String Algorithms"
LET = "abcdefghijklmnopqrstuvwxyz"


def _rs(r, n, alpha="abc"):
    return "".join(r.choice(alpha) for _ in range(n))


def _lower(s):
    return all("a" <= c <= "z" for c in s)


# ---------------------------------------------------------------- EASY

p = add(
    id="first-occurrence-of-needle", title="First Occurrence of a Needle", diff="Easy", topic=TOPIC,
    fn="findFirstOccurrence", params=[("haystack", "string"), ("needle", "string")], ret="int", cmp="exact",
    desc="<p>Given two strings <code>haystack</code> and <code>needle</code>, return the smallest index <code>i</code> such that <code>needle</code> appears in <code>haystack</code> starting at position <code>i</code>. If <code>needle</code> does not occur in <code>haystack</code>, return <code>-1</code>.</p><p>For example, <code>needle = \"aba\"</code> first occurs in <code>haystack = \"ccababa\"</code> at index <code>2</code>, while <code>needle = \"abc\"</code> does not occur in <code>\"ababab\"</code>, so the answer is <code>-1</code>.</p><p>Implement the search yourself; a solution that runs in O(n + m) time is possible.</p>",
    constraints=["1 &le; haystack.length, needle.length &le; 20,000", "Both strings consist of lowercase English letters", "needle may be longer than haystack, in which case the answer is -1"],
    hints=["Trying every start position and comparing character by character works, but it can take O(n &middot; m) time on strings like <code>\"aaaa...a\"</code>.",
           "When a partial match fails, the characters you already matched tell you which later start positions are still possible. Precompute, for every prefix of the needle, the length of its longest proper prefix that is also a suffix.",
           "Build that table (the KMP failure function) for <code>needle</code>, then scan <code>haystack</code> once while keeping the current matched length; on a mismatch fall back with the table instead of moving the haystack pointer backwards."],
    editorial=["The naive method aligns the needle at each position and compares until a mismatch. On inputs such as a haystack of 20,000 letters <code>a</code> and a needle of 10,000 <code>a</code>s followed by a <code>b</code>, it repeats almost the whole comparison at every shift, which is O(n &middot; m).",
               "The Knuth-Morris-Pratt algorithm removes that waste. For each prefix of the needle, <code>pi[i]</code> stores the length of the longest proper prefix of <code>needle[0..i]</code> that is also its suffix. While scanning the haystack, keep <code>k</code>, the number of needle characters currently matched. On a mismatch, set <code>k = pi[k-1]</code> until the characters agree or <code>k</code> is zero; on a match, increase <code>k</code>. When <code>k</code> reaches the needle length the match started at <code>i - m + 1</code>.",
               "Every step either increases <code>k</code> by one or decreases it, and <code>k</code> never goes below zero, so the total number of fallback steps is bounded by the number of increases. Building the table and scanning together take O(n + m) time and O(m) space."],
    time="O(n + m)", space="O(m)",
    solution='''def findFirstOccurrence(haystack, needle):
    m = len(needle)
    pi = [0] * m
    k = 0
    for i in range(1, m):
        while k and needle[i] != needle[k]:
            k = pi[k - 1]
        if needle[i] == needle[k]:
            k += 1
        pi[i] = k
    k = 0
    for i, c in enumerate(haystack):
        while k and c != needle[k]:
            k = pi[k - 1]
        if c == needle[k]:
            k += 1
        if k == m:
            return i - m + 1
    return -1
''',
    tests=[["ccababa", "aba"], ["ababab", "abc"], ["a", "a"], ["abc", "abcd"], ["mississippi", "issip"], ["mississippi", "issipi"],
           ["aaaaab", "aab"], ["abcabcabd", "abcabd"], ["xyz", "z"], ["zzzzzz", "zzzzzzz"], ["abababababc", "ababc"]],
)
_r = rnd(8101)
p["tests"].append(["a" * 20000, "a" * 10000 + "b"])
p["tests"].append(["a" * 19999 + "b", "a" * 10000 + "b"])
_h = _rs(_r, 20000, "ab")
p["tests"].append([_h, _h[13000:13040]])
p["tests"].append([_h, _h[-25:]])
p["tests"].append([_rs(_r, 20000, LET), "qwertyqwerty"])
p["tests"].append(["ab" * 9999 + "c", "ab" * 5000 + "c"])


def b_first_occ(h, nd):
    for i in range(len(h) - len(nd) + 1):
        ok = True
        for j in range(len(nd)):
            if h[i + j] != nd[j]:
                ok = False
                break
        if ok:
            return i
    return -1


def g_first_occ(r):
    h = _rs(r, r.randint(1, 14), "ab")
    if r.random() < 0.6 and len(h) > 1:
        i = r.randrange(len(h))
        nd = h[i:i + r.randint(1, 6)]
    else:
        nd = _rs(r, r.randint(1, 5), "ab")
    return [h, nd]


def v_first_occ(tests):
    for t in tests:
        h, nd = t["args"]
        assert 1 <= len(h) <= 20000 and 1 <= len(nd) <= 20000
        assert _lower(h) and _lower(nd)


CHECKS["first-occurrence-of-needle"] = (b_first_occ, g_first_occ, "exact")
VALIDATE["first-occurrence-of-needle"] = v_first_occ

p = add(
    id="count-overlapping-occurrences", title="Count Overlapping Occurrences", diff="Easy", topic=TOPIC,
    fn="countOccurrences", params=[("text", "string"), ("pattern", "string")], ret="int", cmp="exact",
    desc="<p>Count how many positions of <code>text</code> start a copy of <code>pattern</code>. Occurrences are allowed to overlap.</p><p>For example, <code>pattern = \"aa\"</code> occurs <code>3</code> times in <code>text = \"aaaa\"</code> (at positions 0, 1 and 2), and <code>pattern = \"aba\"</code> occurs <code>2</code> times in <code>\"ababa\"</code>. If the pattern is longer than the text the answer is <code>0</code>.</p>",
    constraints=["1 &le; text.length, pattern.length &le; 20,000", "Both strings consist of lowercase English letters"],
    hints=["Checking every start position with a direct comparison is correct. Think about when that becomes slow.",
           "After a full match you do not need to restart from scratch: the end of the match may already be the beginning of the next one.",
           "Use the prefix function (failure table) of the pattern. When the matched length reaches the pattern length, count one occurrence and fall back to <code>pi[len - 1]</code> instead of resetting to 0."],
    editorial=["Compute the prefix function <code>pi</code> of the pattern: <code>pi[i]</code> is the length of the longest proper prefix of <code>pattern[0..i]</code> that is also a suffix of it. Then scan the text with a matched length <code>k</code> exactly as in KMP search.",
               "The only change compared with finding the first occurrence is what happens on a full match. Instead of stopping, increment the counter and set <code>k = pi[m - 1]</code>. That value is the length of the longest border of the pattern, so it keeps exactly the characters that can also start the next, overlapping, occurrence.",
               "Running time is O(n + m) and the extra memory is the O(m) table. Skipping past each match (restarting at <code>i + m</code>) would be a bug: it counts non-overlapping occurrences only."],
    time="O(n + m)", space="O(m)",
    solution='''def countOccurrences(text, pattern):
    m = len(pattern)
    pi = [0] * m
    k = 0
    for i in range(1, m):
        while k and pattern[i] != pattern[k]:
            k = pi[k - 1]
        if pattern[i] == pattern[k]:
            k += 1
        pi[i] = k
    count = 0
    k = 0
    for c in text:
        while k and c != pattern[k]:
            k = pi[k - 1]
        if c == pattern[k]:
            k += 1
        if k == m:
            count += 1
            k = pi[k - 1]
    return count
''',
    tests=[["aaaa", "aa"], ["ababa", "aba"], ["abc", "d"], ["a", "a"], ["a", "aa"], ["abcabcabc", "abc"], ["aaaaaaaaaa", "aaa"],
           ["abababab", "abab"], ["xyzxyz", "zx"], ["aabaabaaab", "aab"], ["cccc", "cccc"]],
)
_r = rnd(8102)
p["tests"].append(["a" * 20000, "a"])
p["tests"].append(["a" * 20000, "a" * 7000])
p["tests"].append(["ab" * 10000, "abab"])
p["tests"].append([_rs(_r, 20000, "ab"), "aba"])
p["tests"].append([_rs(_r, 20000, "abc"), "abcab"])
p["tests"].append(["abaab" * 4000, "abaababaab"])


def b_count_occ(t, pt):
    c = 0
    for i in range(len(t) - len(pt) + 1):
        if t[i:i + len(pt)] == pt:
            c += 1
    return c


def g_count_occ(r):
    return [_rs(r, r.randint(1, 15), "ab"), _rs(r, r.randint(1, 4), "ab")]


def v_count_occ(tests):
    for t in tests:
        s, pt = t["args"]
        assert 1 <= len(s) <= 20000 and 1 <= len(pt) <= 20000
        assert _lower(s) and _lower(pt)


CHECKS["count-overlapping-occurrences"] = (b_count_occ, g_count_occ, "exact")
VALIDATE["count-overlapping-occurrences"] = v_count_occ

p = add(
    id="smallest-repeating-unit-length", title="Smallest Repeating Unit Length", diff="Easy", topic=TOPIC,
    fn="repeatingUnitLength", params=[("s", "string")], ret="int", cmp="exact",
    desc="<p>A string <code>s</code> is built from a <em>unit</em> <code>u</code> if <code>s</code> equals <code>u</code> written one or more times in a row. Every string is built from itself, so a unit always exists. Return the length of the shortest unit of <code>s</code>.</p><p>For example, <code>\"abcabcabc\"</code> has shortest unit <code>\"abc\"</code> (length <code>3</code>); <code>\"aaaa\"</code> has length <code>1</code>; <code>\"abaab\"</code> has no smaller unit than itself, so the answer is <code>5</code>.</p>",
    constraints=["1 &le; s.length &le; 20,000", "s consists of lowercase English letters"],
    hints=["The unit length must divide <code>s.length</code>. How many candidate lengths is that, and how can you test one?",
           "A string of length <code>n</code> has period <code>p</code> if <code>s[i] == s[i + p]</code> for all valid <code>i</code>. The unit must also be a period, and the string must split evenly.",
           "Compute the prefix function. The smallest period of the whole string is <code>n - pi[n-1]</code>; it is a unit length exactly when it divides <code>n</code>, otherwise the answer is <code>n</code>."],
    editorial=["Testing every divisor <code>d</code> of <code>n</code> by comparing <code>s</code> with <code>s[:d]</code> repeated works and is fast enough here, but a single linear pass is possible.",
               "Let <code>b = pi[n-1]</code> be the length of the longest proper border of <code>s</code> (a prefix that is also a suffix). Then <code>s</code> has smallest period <code>p = n - b</code>. If <code>p</code> divides <code>n</code>, the string is exactly <code>n / p</code> copies of its first <code>p</code> characters, and no shorter unit exists because any unit length is also a period and <code>p</code> is the smallest one.",
               "If <code>p</code> does not divide <code>n</code>, the string only repeats its prefix a fractional number of times. Then any unit would have to be a period that divides <code>n</code>; one smaller than <code>n</code> would force the smallest period to divide <code>n</code> as well (a consequence of the periodicity lemma), which it does not. So the answer is <code>n</code>. Time O(n), space O(n)."],
    time="O(n)", space="O(n)",
    solution='''def repeatingUnitLength(s):
    n = len(s)
    pi = [0] * n
    k = 0
    for i in range(1, n):
        while k and s[i] != s[k]:
            k = pi[k - 1]
        if s[i] == s[k]:
            k += 1
        pi[i] = k
    period = n - pi[-1]
    return period if n % period == 0 else n
''',
    tests=[["abcabcabc"], ["aaaa"], ["abaab"], ["a"], ["ab"], ["abab"], ["ababa"], ["abcabcab"], ["xyxyxyxyxy"], ["aabaab"], ["aabaabaab"],
           ["abcdefgh"]],
)
_r = rnd(8103)
p["tests"].append(["a" * 20000])
p["tests"].append(["ab" * 10000])
_u = _rs(_r, 125, "ab")
p["tests"].append([_u * 160])
_u = _rs(_r, 9999, "abc")
p["tests"].append([_u + _u[:5]])
p["tests"].append([_rs(_r, 20000, LET)])
p["tests"].append(["a" * 19999 + "b"])


def b_unit(s):
    n = len(s)
    for d in range(1, n + 1):
        if n % d == 0 and s[:d] * (n // d) == s:
            return d


def g_unit(r):
    u = _rs(r, r.randint(1, 4), "ab")
    s = u * r.randint(1, 4)
    if r.random() < 0.4:
        s += u[:r.randint(0, len(u))]
    if r.random() < 0.2 and s:
        i = r.randrange(len(s))
        s = s[:i] + r.choice("ab") + s[i + 1:]
    return [s]


def v_unit(tests):
    for t in tests:
        s = t["args"][0]
        assert 1 <= len(s) <= 20000 and _lower(s)


CHECKS["smallest-repeating-unit-length"] = (b_unit, g_unit, "exact")
VALIDATE["smallest-repeating-unit-length"] = v_unit

# ---------------------------------------------------------------- MEDIUM

p = add(
    id="longest-border-length", title="Longest Border Length", diff="Medium", topic=TOPIC,
    fn="longestBorder", params=[("s", "string")], ret="int", cmp="exact",
    desc="<p>A <em>border</em> of a string <code>s</code> is a non-empty string that is both a prefix and a suffix of <code>s</code> and is strictly shorter than <code>s</code> itself. Return the length of the longest border of <code>s</code>, or <code>0</code> if <code>s</code> has none.</p><p>Borders may overlap: the string <code>\"aaaa\"</code> has longest border <code>\"aaa\"</code> (length <code>3</code>), and <code>\"ababab\"</code> has longest border <code>\"abab\"</code> (length <code>4</code>). The string <code>\"abcd\"</code> has none.</p>",
    constraints=["1 &le; s.length &le; 20,000", "s consists of lowercase English letters"],
    hints=["Comparing every prefix length with the matching suffix works but costs O(n&sup2;) in the worst case. Look for reuse between neighbouring prefixes.",
           "If the longest border of <code>s[0..i-1]</code> has length <code>k</code> and <code>s[i] == s[k]</code>, then the border of <code>s[0..i]</code> is at least <code>k + 1</code>. What if they differ?",
           "On a mismatch, the next candidate border is the longest border of the border: <code>k = pi[k-1]</code>. Run this for the whole string; the answer is the last <code>pi</code> value."],
    editorial=["Define <code>pi[i]</code> as the length of the longest border of the prefix <code>s[0..i]</code>. The answer is <code>pi[n-1]</code>. The values build on each other: a border of <code>s[0..i]</code> of length <code>k + 1</code> is a border of <code>s[0..i-1]</code> of length <code>k</code> extended by one equal character.",
               "So keep <code>k = pi[i-1]</code>. While <code>k &gt; 0</code> and <code>s[i] != s[k]</code>, replace <code>k</code> by <code>pi[k-1]</code>, which enumerates all borders of the previous prefix from longest to shortest (borders of borders are borders). If now <code>s[i] == s[k]</code>, increment <code>k</code>. Set <code>pi[i] = k</code>.",
               "Amortised analysis: <code>k</code> increases by at most one per character and every fallback decreases it, so the total work is O(n). Memory is O(n) for the table. A hashing approach (compare prefix and suffix hashes for each length) also gives O(n) expected time but needs care with collisions."],
    time="O(n)", space="O(n)",
    solution='''def longestBorder(s):
    n = len(s)
    pi = [0] * n
    k = 0
    for i in range(1, n):
        while k and s[i] != s[k]:
            k = pi[k - 1]
        if s[i] == s[k]:
            k += 1
        pi[i] = k
    return pi[-1]
''',
    tests=[["aaaa"], ["ababab"], ["abcd"], ["a"], ["aa"], ["abcabc"], ["abacaba"], ["aabaaab"], ["level"], ["abcabcabcab"], ["xyzzyx"], ["aabaabaaa"]],
)
_r = rnd(8104)
p["tests"].append(["a" * 20000])
p["tests"].append(["a" * 19999 + "b"])
p["tests"].append(["ab" * 9999 + "a"])
_u = _rs(_r, 4000, "ab")
p["tests"].append([_u + _rs(_r, 12000, "ab") + _u])
p["tests"].append([_rs(_r, 20000, LET)])
p["tests"].append(["abaab" * 3999 + "aba"])


def b_border(s):
    n = len(s)
    for k in range(n - 1, 0, -1):
        if s[:k] == s[n - k:]:
            return k
    return 0


def g_border(r):
    if r.random() < 0.5:
        return [_rs(r, r.randint(1, 14), "ab")]
    u = _rs(r, r.randint(1, 4), "ab")
    return [u * r.randint(1, 4) + u[:r.randint(0, len(u))]]


def v_border(tests):
    for t in tests:
        s = t["args"][0]
        assert 1 <= len(s) <= 20000 and _lower(s)


CHECKS["longest-border-length"] = (b_border, g_border, "exact")
VALIDATE["longest-border-length"] = v_border

p = add(
    id="repeated-string-match-count", title="Repeated String Match Count", diff="Medium", topic=TOPIC,
    fn="repeatsToContain", params=[("a", "string"), ("b", "string")], ret="int", cmp="exact",
    desc="<p>You may write the string <code>a</code> one or more times in a row to form a longer string. Return the smallest number of copies of <code>a</code> such that <code>b</code> is a contiguous substring of the result. If no number of copies works, return <code>-1</code>.</p><p>For example, with <code>a = \"abc\"</code> and <code>b = \"cabcabca\"</code> the answer is <code>4</code>, because <code>\"abcabcabcabc\"</code> contains <code>b</code> but three copies do not. With <code>a = \"abc\"</code> and <code>b = \"acb\"</code> the answer is <code>-1</code>.</p>",
    constraints=["1 &le; a.length, b.length &le; 10,000", "Both strings consist of lowercase English letters"],
    hints=["Appending copies of <code>a</code> forever cannot help once the text is long enough. How many copies are certainly enough to be able to decide?",
           "You need at least <code>ceil(b.length / a.length)</code> copies just for the length. Because <code>b</code> can start in the middle of a copy, one more copy may be needed, but no more than that.",
           "Build the strings with <code>k0 = ceil(|b| / |a|)</code> and <code>k0 + 1</code> copies and test each for <code>b</code> with a linear substring search (KMP); return the first that works, else <code>-1</code>."],
    editorial=["Let <code>k0 = ceil(|b| / |a|)</code>. With fewer than <code>k0</code> copies the text is shorter than <code>b</code>, so no answer is below <code>k0</code>.",
               "Suppose <code>b</code> occurs in some number of copies of <code>a</code>, starting inside copy number <code>t</code> (0-based) of the text. Then the same occurrence also exists if we delete the first <code>t</code> copies, because the text is periodic with period <code>|a|</code>. After that it begins inside the first copy and spans at most <code>|b|</code> characters, so it fits within <code>ceil((|b| + |a| - 1) / |a|)</code> copies, which is at most <code>k0 + 1</code>. Hence only <code>k0</code> and <code>k0 + 1</code> need testing.",
               "Each test is a substring search. A KMP search (build the failure table of <code>b</code>, scan the repeated text) takes O(|a| &middot; k0 + |b|) = O(|a| + |b|) time and avoids the quadratic worst case of naive matching."],
    time="O(|a| + |b|)", space="O(|b|)",
    solution='''def repeatsToContain(a, b):
    m = len(b)
    pi = [0] * m
    k = 0
    for i in range(1, m):
        while k and b[i] != b[k]:
            k = pi[k - 1]
        if b[i] == b[k]:
            k += 1
        pi[i] = k

    def contains(t):
        k = 0
        for c in t:
            while k and c != b[k]:
                k = pi[k - 1]
            if c == b[k]:
                k += 1
            if k == m:
                return True
        return False

    k0 = -(-m // len(a))
    if contains(a * k0):
        return k0
    if contains(a * (k0 + 1)):
        return k0 + 1
    return -1
''',
    tests=[["abc", "cabcabca"], ["abc", "acb"], ["a", "a"], ["a", "aaaa"], ["abcd", "cdabcdab"], ["abcd", "d"], ["ab", "bab"], ["abab", "baba"],
           ["aa", "aaa"], ["abc", "abcabcabc"], ["xyz", "yzxyzxy"], ["abc", "abd"]],
)
_r = rnd(8105)
p["tests"].append(["a", "a" * 10000])
p["tests"].append(["a" * 5000, "a" * 9999])
_u = _rs(_r, 3000, "ab")
p["tests"].append([_u, (_u * 4)[2999:2999 + 9000]])
p["tests"].append([_u, (_u * 4)[2999:2999 + 9000] + "c"])
p["tests"].append(["ab" * 5000, "ba" * 4999 + "b"])
p["tests"].append([_rs(_r, 9999, "ab"), _rs(_r, 10000, "ab")])
p["tests"].append(["abcde" * 1999, ("abcde" * 2001)[3:10000]])


def b_repeat(a, b):
    for k in range(1, len(b) + 3):
        t = a * k
        for i in range(len(t) - len(b) + 1):
            if t[i:i + len(b)] == b:
                return k
    return -1


def g_repeat(r):
    a = _rs(r, r.randint(1, 4), "ab")
    if r.random() < 0.7:
        t = a * 5
        i = r.randrange(len(a))
        b = t[i:i + r.randint(1, 12)]
        if r.random() < 0.2:
            j = r.randrange(len(b))
            b = b[:j] + r.choice("ab") + b[j + 1:]
    else:
        b = _rs(r, r.randint(1, 8), "ab")
    return [a, b]


def v_repeat(tests):
    for t in tests:
        a, b = t["args"]
        assert 1 <= len(a) <= 10000 and 1 <= len(b) <= 10000
        assert _lower(a) and _lower(b)


CHECKS["repeated-string-match-count"] = (b_repeat, g_repeat, "exact")
VALIDATE["repeated-string-match-count"] = v_repeat

p = add(
    id="z-function-sum", title="Z-Function Sum", diff="Medium", topic=TOPIC,
    fn="zSum", params=[("s", "string")], ret="int", cmp="exact",
    desc="<p>For a string <code>s</code> of length <code>n</code>, let <code>z[i]</code> be the length of the longest common prefix of <code>s</code> and the suffix <code>s[i..n-1]</code>. By definition <code>z[0] = n</code>. Return the sum <code>z[0] + z[1] + ... + z[n-1]</code>.</p><p>For example, <code>s = \"ababa\"</code> has <code>z = [5, 0, 3, 0, 1]</code>, so the answer is <code>9</code>. For <code>s = \"aaa\"</code>, <code>z = [3, 2, 1]</code> and the answer is <code>6</code>.</p>",
    constraints=["1 &le; s.length &le; 20,000", "s consists of lowercase English letters", "The answer is at most n(n+1)/2 and fits in a 32-bit integer"],
    hints=["Computing each <code>z[i]</code> by comparing characters from scratch is O(n&sup2;) in the worst case, for example on a string of all equal letters.",
           "Keep the rightmost segment <code>[l, r)</code> found so far that matches a prefix of <code>s</code>. For a position <code>i</code> inside it, <code>s[i..r)</code> equals <code>s[i-l..r-l)</code>, so <code>z[i]</code> is at least <code>min(r - i, z[i - l])</code>.",
           "Start from that lower bound and extend by direct comparison only while characters keep matching; update <code>[l, r)</code> whenever you extend beyond <code>r</code>. Finally sum the array."],
    editorial=["The Z-algorithm computes the whole array in linear time. Maintain a window <code>[l, r)</code> with the largest right end among all segments <code>s[i..i+z[i])</code> seen so far; this window is a copy of the prefix <code>s[0..r-l)</code>.",
               "For a new index <code>i &lt; r</code>, the substring <code>s[i..r)</code> mirrors <code>s[i-l..r-l)</code>, so <code>z[i]</code> starts at <code>min(r - i, z[i - l])</code>. For <code>i &ge; r</code> start from zero. Then extend with character comparisons while <code>s[z[i]] == s[i + z[i]]</code>. If the match reaches beyond <code>r</code>, move the window to <code>[i, i + z[i])</code>.",
               "Every comparison that succeeds pushes <code>r</code> to the right, and <code>r</code> never moves back, so the total number of extension steps is at most <code>n</code>; the total running time is O(n). The sum for the maximum input (all equal letters) is 200,010,000, safely below 2<sup>31</sup>."],
    time="O(n)", space="O(n)",
    solution='''def zSum(s):
    n = len(s)
    z = [0] * n
    z[0] = n
    l = r = 0
    for i in range(1, n):
        if i < r:
            z[i] = min(r - i, z[i - l])
        while i + z[i] < n and s[z[i]] == s[i + z[i]]:
            z[i] += 1
        if i + z[i] > r:
            l, r = i, i + z[i]
    return sum(z)
''',
    tests=[["ababa"], ["aaa"], ["a"], ["ab"], ["abcd"], ["abababab"], ["aabxaabxcaabxaabxay"], ["abcabcabc"], ["aaaab"], ["baaaa"], ["abaabaabaab"]],
)
_r = rnd(8106)
p["tests"].append(["a" * 20000])
p["tests"].append(["a" * 19999 + "b"])
p["tests"].append(["ab" * 10000])
p["tests"].append([_rs(_r, 20000, "ab")])
p["tests"].append([_rs(_r, 20000, LET)])
p["tests"].append(["abaab" * 4000])
_u = _rs(_r, 40, "abc")
p["tests"].append([(_u * 500)])


def b_zsum(s):
    n = len(s)
    total = 0
    for i in range(n):
        k = 0
        while i + k < n and s[k] == s[i + k]:
            k += 1
        total += k
    return total


def g_zsum(r):
    if r.random() < 0.5:
        return [_rs(r, r.randint(1, 14), "ab")]
    u = _rs(r, r.randint(1, 4), "ab")
    return [u * r.randint(1, 5) + _rs(r, r.randint(0, 2), "ab")]


def v_zsum(tests):
    for t in tests:
        s = t["args"][0]
        assert 1 <= len(s) <= 20000 and _lower(s)


CHECKS["z-function-sum"] = (b_zsum, g_zsum, "exact")
VALIDATE["z-function-sum"] = v_zsum

p = add(
    id="lexicographically-smallest-rotation", title="Lexicographically Smallest Rotation", diff="Medium", topic=TOPIC,
    fn="smallestRotation", params=[("s", "string")], ret="string", cmp="exact",
    desc="<p>A <em>rotation</em> of a string moves some number of characters from the front to the back: rotating <code>\"abcde\"</code> by two gives <code>\"cdeab\"</code>. Among all <code>n</code> rotations of <code>s</code> (including the unrotated string), return the one that is smallest in dictionary order.</p><p>For example, the rotations of <code>\"bca\"</code> are <code>\"bca\"</code>, <code>\"cab\"</code> and <code>\"abc\"</code>, so the answer is <code>\"abc\"</code>. For <code>\"cbaab\"</code> the answer is <code>\"aabcb\"</code>.</p>",
    constraints=["1 &le; s.length &le; 20,000", "s consists of lowercase English letters"],
    hints=["Generating all rotations and taking the minimum costs O(n&sup2;) time (and memory if you store them). Think about how to compare two rotations without building them.",
           "Two candidate start positions <code>i</code> and <code>j</code> can be compared character by character using indices modulo <code>n</code>. If they agree for <code>k</code> characters and then <code>s[i+k] &gt; s[j+k]</code>, then none of the starts <code>i, i+1, ..., i+k</code> can be the best.",
           "Keep two candidates and a match length <code>k</code>. On a difference, the larger candidate jumps by <code>k + 1</code>; if the candidates collide, move one forward. Stop when one candidate or <code>k</code> reaches <code>n</code>; the answer starts at the smaller candidate."],
    editorial=["The two-candidate method (a form of Booth's / Duval-style minimal representation) works in linear time. Hold two start indices <code>i = 0</code>, <code>j = 1</code> and a counter <code>k</code> of characters that already agree. Compare <code>s[(i+k) % n]</code> with <code>s[(j+k) % n]</code>.",
               "If they are equal, increase <code>k</code>. If the character at <code>i</code> is larger, then every start <code>i, i+1, ..., i+k</code> is beaten by the corresponding start shifted by <code>j - i</code>, so set <code>i += k + 1</code>; symmetrically for <code>j</code>. After a jump, if the two candidates coincide push <code>j</code> forward by one, and reset <code>k = 0</code>.",
               "Each step advances at least one of <code>i</code> or <code>j</code> (or <code>k</code> towards <code>n</code>), and both candidates stay below <code>n</code>, so the loop makes O(n) iterations. When it ends, <code>min(i, j)</code> is the starting index of the smallest rotation (when <code>k</code> reaches <code>n</code> the string is periodic and both candidates give the same rotation). Return <code>s[start:] + s[:start]</code>."],
    time="O(n)", space="O(n)",
    solution='''def smallestRotation(s):
    n = len(s)
    i, j, k = 0, 1, 0
    while i < n and j < n and k < n:
        a = s[(i + k) % n]
        b = s[(j + k) % n]
        if a == b:
            k += 1
            continue
        if a > b:
            i += k + 1
        else:
            j += k + 1
        if i == j:
            j += 1
        k = 0
    start = min(i, j)
    return s[start:] + s[:start]
''',
    tests=[["bca"], ["cbaab"], ["a"], ["ba"], ["aaaa"], ["abab"], ["baba"], ["zzzya"], ["abcabcabd"], ["dcba"], ["bbaabbaab"], ["cabacabac"]],
)
_r = rnd(8107)
p["tests"].append(["z" + "a" * 19999])
p["tests"].append(["a" * 19999 + "b"])
p["tests"].append(["ba" * 10000])
p["tests"].append([_rs(_r, 20000, "ab")])
p["tests"].append([_rs(_r, 20000, LET)])
_u = _rs(_r, 100, "ab")
p["tests"].append([_u * 200])
p["tests"].append([("ab" * 5000 + "a") * 1 + "b" * 3000 + "a" * 5999])


def b_rot(s):
    n = len(s)
    return min(s[i:] + s[:i] for i in range(n))


def g_rot(r):
    if r.random() < 0.3:
        u = _rs(r, r.randint(1, 3), "ab")
        return [u * r.randint(1, 4)]
    return [_rs(r, r.randint(1, 12), "abc")]


def v_rot(tests):
    for t in tests:
        s = t["args"][0]
        assert 1 <= len(s) <= 20000 and _lower(s)
        out = t["expected"]
        assert len(out) == len(s) and out in s + s


CHECKS["lexicographically-smallest-rotation"] = (b_rot, g_rot, "exact")
VALIDATE["lexicographically-smallest-rotation"] = v_rot

p = add(
    id="wildcard-pattern-match", title="Wildcard Pattern Match", diff="Medium", topic=TOPIC,
    fn="isWildcardMatch", params=[("s", "string"), ("p", "string")], ret="bool", cmp="exact",
    desc="<p>Decide whether the whole string <code>s</code> is matched by the pattern <code>p</code>. The pattern may contain lowercase letters and two special characters:</p><ul><li><code>?</code> matches exactly one arbitrary character.</li><li><code>*</code> matches any sequence of characters, including the empty sequence.</li></ul><p>The match must cover the entire string, not just a part of it. For example, <code>s = \"adceb\"</code> matches <code>p = \"*a*b\"</code>, and <code>s = \"acdcb\"</code> does not match <code>p = \"a*c?b\"</code>.</p>",
    constraints=["1 &le; s.length, p.length &le; 2,000", "s consists of lowercase English letters", "p consists of lowercase English letters, '?' and '*'"],
    hints=["Try a dynamic programme over prefixes: <code>dp[i][j]</code> says whether <code>s[:i]</code> matches <code>p[:j]</code>. Work out the transition for a letter, for <code>?</code>, and for <code>*</code>.",
           "A star can be either empty (<code>dp[i][j-1]</code>) or consume one more character (<code>dp[i-1][j]</code>). That gives an O(n &middot; m) table; can you do better on memory?",
           "Greedy alternative: remember the position of the most recent <code>*</code> and the text index it currently covers up to. On a mismatch, extend that star by one more character and retry the pattern after it. Only the latest star ever needs revisiting."],
    editorial=["Dynamic programming: let <code>dp[i][j]</code> be true when the first <code>i</code> characters of <code>s</code> match the first <code>j</code> of <code>p</code>. Base case <code>dp[0][0] = true</code>, and <code>dp[0][j]</code> is true only while the pattern prefix consists of stars. For a letter or <code>?</code>, <code>dp[i][j] = dp[i-1][j-1]</code> when the characters are compatible. For a star, <code>dp[i][j] = dp[i][j-1] or dp[i-1][j]</code>. Rolling rows reduce space to O(m); time is O(n &middot; m).",
               "A tighter greedy exists because stars are so permissive. Walk through <code>s</code> and <code>p</code> with two pointers. When <code>p[j]</code> is a letter equal to <code>s[i]</code> or a <code>?</code>, advance both. When it is a star, record <code>star = j</code> and <code>mark = i</code>, and advance only <code>j</code> (the star starts by matching nothing). On a mismatch with a recorded star, return to <code>star + 1</code> and let the star swallow one more character: <code>mark += 1; i = mark</code>. A mismatch without a star means no match.",
               "Why only the last star matters: everything before the last star is already matched in the cheapest possible way, and by earlier choices the later star can absorb whatever is needed, so any assignment that works for an earlier star can be shifted onto the latest one. After the text is consumed, the remaining pattern must be only stars. The greedy is O(n &middot; m) in the worst case but O(n + m) on typical inputs and uses O(1) extra space."],
    time="O(n * m)", space="O(1)",
    solution='''def isWildcardMatch(s, p):
    n, m = len(s), len(p)
    i = j = 0
    star = -1
    mark = 0
    while i < n:
        if j < m and (p[j] == '?' or p[j] == s[i]):
            i += 1
            j += 1
        elif j < m and p[j] == '*':
            star = j
            mark = i
            j += 1
        elif star != -1:
            j = star + 1
            mark += 1
            i = mark
        else:
            return False
    while j < m and p[j] == '*':
        j += 1
    return j == m
''',
    tests=[["adceb", "*a*b"], ["acdcb", "a*c?b"], ["a", "?"], ["a", "*"], ["abc", "abc"], ["abc", "ab"], ["ab", "a?c"], ["abcde", "*"], ["abcde", "*e"],
           ["abcde", "a*c*e"], ["mississippi", "m??*ss*?*"], ["mississippi", "m*iss*p?"], ["aaa", "a*a*a*a"], ["abc", "***"], ["abc", "?*?*?*?"]],
)
_r = rnd(8108)
p["tests"].append(["a" * 2000, "*" + "a" * 1000 + "b"])
p["tests"].append(["a" * 1999 + "b", "*" + "a" * 1000 + "b"])
p["tests"].append(["ab" * 1000, "*a*b" * 400 + "*"])
p["tests"].append(["ab" * 1000, "a*" * 999 + "b"])
p["tests"].append([_rs(_r, 2000, "abc"), "*" * 2000])
p["tests"].append(["a" * 2000, "?" * 2000])
p["tests"].append(["a" * 2000, "?" * 1999])
p["tests"].append([_rs(_r, 1500, "ab"), "*?" * 700 + "*"])


def b_wild(s, pt):
    def go(i, j):
        if j == len(pt):
            return i == len(s)
        if pt[j] == "*":
            for t in range(i, len(s) + 1):
                if go(t, j + 1):
                    return True
            return False
        return i < len(s) and (pt[j] == "?" or pt[j] == s[i]) and go(i + 1, j + 1)
    return go(0, 0)


def g_wild(r):
    s = _rs(r, r.randint(1, 8), "ab")
    if r.random() < 0.55:
        pt = ""
        for c in s:
            x = r.random()
            if x < 0.2:
                pt += "?"
            elif x < 0.35:
                pt += "*"
            elif x < 0.45:
                pt += "*" + c
            else:
                pt += c
        if r.random() < 0.3:
            pt += "*"
        if r.random() < 0.2 and len(pt) > 1:
            k = r.randrange(len(pt))
            pt = pt[:k] + r.choice("ab?*") + pt[k + 1:]
    else:
        pt = _rs(r, r.randint(1, 7), "ab?*")
    return [s, pt]


def v_wild(tests):
    for t in tests:
        s, pt = t["args"]
        assert 1 <= len(s) <= 2000 and 1 <= len(pt) <= 2000
        assert _lower(s)
        assert all(_lower(c) or c in "?*" for c in pt)


CHECKS["wildcard-pattern-match"] = (b_wild, g_wild, "exact")
VALIDATE["wildcard-pattern-match"] = v_wild

# ---------------------------------------------------------------- HARD

p = add(
    id="count-distinct-substrings", title="Count Distinct Substrings", diff="Hard", topic=TOPIC,
    fn="countDistinctSubstrings", params=[("s", "string")], ret="int", cmp="exact",
    desc="<p>Return the number of different non-empty substrings of <code>s</code>. Two substrings are the same if they consist of the same characters in the same order, no matter where in <code>s</code> they occur.</p><p>For example, <code>\"aaa\"</code> has the 3 distinct substrings <code>\"a\"</code>, <code>\"aa\"</code>, <code>\"aaa\"</code>, and <code>\"abab\"</code> has 7: <code>a</code>, <code>b</code>, <code>ab</code>, <code>ba</code>, <code>aba</code>, <code>bab</code>, <code>abab</code>.</p>",
    constraints=["1 &le; s.length &le; 20,000", "s consists of lowercase English letters", "The answer is at most n(n+1)/2, which is below 2<sup>31</sup>"],
    hints=["Putting every substring into a set needs O(n&sup2;) strings, each up to n long. That is far too much at n = 20,000.",
           "Each substring is a prefix of some suffix. If you sort the suffixes, the number of new substrings a suffix contributes depends only on how much it shares with its neighbour in sorted order.",
           "Either use a suffix array with the LCP array (answer = n(n+1)/2 minus the sum of LCPs), or build a suffix automaton: every state <code>v</code> represents <code>len[v] - len[link[v]]</code> distinct substrings, and the answer is the sum over states."],
    editorial=["Counting by brute force with a set of all slices is O(n&sup3;) time-ish and O(n&sup2;) memory, only usable for very short strings. A trie of all suffixes reduces the time to O(n&sup2;) but still creates up to n&sup2;/2 nodes.",
               "Suffix array approach: sort the suffixes, compute the LCP of each adjacent pair (for instance with Kasai's algorithm). Every suffix of length <code>L</code> introduces <code>L</code> prefixes, but the first <code>lcp</code> of them already appeared as prefixes of the previous suffix in sorted order. So the answer is <code>n(n+1)/2 - sum(lcp)</code>.",
               "Suffix automaton approach: the automaton is the smallest DFA that accepts all suffixes, and can be built online in O(n) amortised time. Its states partition all substrings into classes; state <code>v</code> contains the substrings with lengths in <code>(len[link[v]], len[v]]</code>, so it contributes <code>len[v] - len[link[v]]</code> distinct substrings. Summing over all non-root states gives the answer. The automaton has at most <code>2n</code> states, so memory is O(n) for a fixed alphabet."],
    time="O(n)", space="O(n)",
    solution='''def countDistinctSubstrings(s):
    nxt = [{}]
    link = [-1]
    length = [0]
    last = 0
    for c in s:
        cur = len(nxt)
        nxt.append({})
        length.append(length[last] + 1)
        link.append(0)
        p = last
        while p != -1 and c not in nxt[p]:
            nxt[p][c] = cur
            p = link[p]
        if p == -1:
            link[cur] = 0
        else:
            q = nxt[p][c]
            if length[p] + 1 == length[q]:
                link[cur] = q
            else:
                clone = len(nxt)
                nxt.append(dict(nxt[q]))
                length.append(length[p] + 1)
                link.append(link[q])
                while p != -1 and nxt[p].get(c) == q:
                    nxt[p][c] = clone
                    p = link[p]
                link[q] = clone
                link[cur] = clone
        last = cur
    return sum(length[v] - length[link[v]] for v in range(1, len(nxt)))
''',
    tests=[["aaa"], ["abab"], ["a"], ["ab"], ["abc"], ["aaaa"], ["abcabc"], ["banana"], ["mississippi"], ["abacabadabacaba"], ["aabaa"], ["zyxwvu"]],
)
_r = rnd(8109)
p["tests"].append(["a" * 20000])
p["tests"].append([_rs(_r, 20000, "ab")])
p["tests"].append([_rs(_r, 20000, LET)])
p["tests"].append(["ab" * 10000])
_f = ["a", "b"]
while len(_f[-1]) < 20000:
    _f.append(_f[-1] + _f[-2])
p["tests"].append([_f[-1][:20000]])  # Fibonacci word: highly repetitive
p["tests"].append([_rs(_r, 10000, "abc") + "a" * 10000])


def b_distinct(s):
    seen = set()
    for i in range(len(s)):
        for j in range(i + 1, len(s) + 1):
            seen.add(s[i:j])
    return len(seen)


def g_distinct(r):
    if r.random() < 0.4:
        u = _rs(r, r.randint(1, 3), "ab")
        return [(u * r.randint(1, 5))[:r.randint(1, 14)]]
    return [_rs(r, r.randint(1, 14), r.choice(["ab", "abc", "a"]))]


def v_distinct(tests):
    for t in tests:
        s = t["args"][0]
        assert 1 <= len(s) <= 20000 and _lower(s)
        assert t["expected"] <= len(s) * (len(s) + 1) // 2


CHECKS["count-distinct-substrings"] = (b_distinct, g_distinct, "exact")
VALIDATE["count-distinct-substrings"] = v_distinct

p = add(
    id="longest-shared-substring-two-strings", title="Longest Shared Substring of Two Strings", diff="Hard", topic=TOPIC,
    fn="longestSharedSubstring", params=[("a", "string"), ("b", "string")], ret="int", cmp="exact",
    desc="<p>Return the length of the longest string that appears as a contiguous substring in <strong>both</strong> <code>a</code> and <code>b</code>. If the two strings share no character, return <code>0</code>.</p><p>For example, <code>a = \"xabcdy\"</code> and <code>b = \"zzabcdq\"</code> share <code>\"abcd\"</code>, so the answer is <code>4</code>. For <code>a = \"abc\"</code> and <code>b = \"def\"</code> the answer is <code>0</code>. Note that a substring is contiguous, unlike a subsequence.</p>",
    constraints=["1 &le; a.length, b.length &le; 10,000", "Both strings consist of lowercase English letters"],
    hints=["The classic dynamic programme <code>dp[i][j]</code> (length of the common suffix of <code>a[:i]</code> and <code>b[:j]</code>) takes O(|a| &middot; |b|) time, which is 10<sup>8</sup> steps at the limit. Look for something near-linear.",
           "If a shared substring of length <code>L</code> exists, then shared substrings of every smaller length exist too. That allows a binary search on <code>L</code> if you can test one length quickly.",
           "A suffix automaton of <code>a</code> recognises exactly the substrings of <code>a</code>. Feed <code>b</code> through it character by character, keeping the current state and the length of the match; when a transition is missing, follow suffix links until one exists. The maximum match length seen is the answer."],
    editorial=["The table DP compares every pair of positions: <code>dp[i][j] = dp[i-1][j-1] + 1</code> if <code>a[i-1] == b[j-1]</code>, else 0, and the answer is the maximum entry. It needs O(|a| &middot; |b|) time, which is too slow for the largest inputs here, although it is a good way to check a faster method on small cases.",
               "Binary search with hashing is one faster route: for a candidate length <code>L</code>, put the hashes of all length-<code>L</code> windows of <code>a</code> into a set and look for a window of <code>b</code> with a hash in it. The test is monotone in <code>L</code>, giving O((|a| + |b|) log n) expected time.",
               "The deterministic linear method builds the suffix automaton of <code>a</code> (at most <code>2|a|</code> states, built online). Then walk through <code>b</code> with a state <code>v</code> and a length <code>len</code>: for each character <code>c</code>, while <code>v</code> has no transition on <code>c</code> and is not the root, set <code>v = link[v]</code> and <code>len = length[v]</code>; if a transition exists, move along it and increase <code>len</code>. At every step <code>len</code> is the longest suffix of the processed part of <code>b</code> that is a substring of <code>a</code>, so the answer is the largest <code>len</code> reached. Time O(|a| + |b|), space O(|a|)."],
    time="O(|a| + |b|)", space="O(|a|)",
    solution='''def longestSharedSubstring(a, b):
    nxt = [{}]
    link = [-1]
    length = [0]
    last = 0
    for c in a:
        cur = len(nxt)
        nxt.append({})
        length.append(length[last] + 1)
        link.append(0)
        p = last
        while p != -1 and c not in nxt[p]:
            nxt[p][c] = cur
            p = link[p]
        if p == -1:
            link[cur] = 0
        else:
            q = nxt[p][c]
            if length[p] + 1 == length[q]:
                link[cur] = q
            else:
                clone = len(nxt)
                nxt.append(dict(nxt[q]))
                length.append(length[p] + 1)
                link.append(link[q])
                while p != -1 and nxt[p].get(c) == q:
                    nxt[p][c] = clone
                    p = link[p]
                link[q] = clone
                link[cur] = clone
        last = cur
    v = 0
    cur_len = 0
    best = 0
    for c in b:
        while v != 0 and c not in nxt[v]:
            v = link[v]
            cur_len = length[v]
        if c in nxt[v]:
            v = nxt[v][c]
            cur_len += 1
        if cur_len > best:
            best = cur_len
    return best
''',
    tests=[["xabcdy", "zzabcdq"], ["abc", "def"], ["a", "a"], ["a", "b"], ["abcde", "abcde"], ["abcde", "cdeab"], ["aaaa", "aa"], ["abab", "baba"],
           ["zabcz", "yabcy"], ["mississippi", "issue"], ["abcdefg", "xyzabcdefgxyz"], ["aabaa", "baab"]],
)
_r = rnd(8110)
p["tests"].append(["a" * 10000, "a" * 10000])
p["tests"].append(["a" * 10000, "a" * 9999 + "b"])
p["tests"].append([_rs(_r, 10000, LET), _rs(_r, 10000, LET)])
p["tests"].append([_rs(_r, 10000, "ab"), _rs(_r, 10000, "ab")])
_c = _rs(_r, 3000, "abc")
p["tests"].append([_rs(_r, 4000, "ab") + _c + _rs(_r, 3000, "ab"), _rs(_r, 2000, "ab") + _c + _rs(_r, 5000, "ab")])
p["tests"].append(["ab" * 5000, "ba" * 5000])
p["tests"].append([_rs(_r, 10000, "abc"), "d" * 10000])


def b_shared(a, b):
    best = 0
    prev = [0] * (len(b) + 1)
    for i in range(1, len(a) + 1):
        cur = [0] * (len(b) + 1)
        for j in range(1, len(b) + 1):
            if a[i - 1] == b[j - 1]:
                cur[j] = prev[j - 1] + 1
                if cur[j] > best:
                    best = cur[j]
        prev = cur
    return best


def g_shared(r):
    alpha = r.choice(["ab", "abc", "abcd"])
    a = _rs(r, r.randint(1, 12), alpha)
    if r.random() < 0.6:
        i = r.randrange(len(a))
        mid = a[i:i + r.randint(1, 6)]
        b = _rs(r, r.randint(0, 4), alpha) + mid + _rs(r, r.randint(0, 4), alpha)
    else:
        b = _rs(r, r.randint(1, 12), alpha)
    return [a, b]


def v_shared(tests):
    for t in tests:
        a, b = t["args"]
        assert 1 <= len(a) <= 10000 and 1 <= len(b) <= 10000
        assert _lower(a) and _lower(b)
        assert 0 <= t["expected"] <= min(len(a), len(b))


CHECKS["longest-shared-substring-two-strings"] = (b_shared, g_shared, "exact")
VALIDATE["longest-shared-substring-two-strings"] = v_shared
