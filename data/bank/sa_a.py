"""Problems: string algorithms (KMP, Z-function, borders, periods). See data/lib.py for the registry."""
from lib import add, rnd, CHECKS, VALIDATE, gen_arr  # noqa: F401

TOPIC = "String Algorithms"
MOD = 1_000_000_007


def _rs(r, n, alpha="ab"):
    return "".join(r.choice(alpha) for _ in range(n))


def _lower(s):
    return all("a" <= c <= "z" for c in s)


def _fib(n):
    a, b = "a", "ab"
    while len(b) < n:
        a, b = b, b + a
    return b[:n]


def _periodic(r, n, plen, alpha="ab", mutate=0):
    u = _rs(r, plen, alpha)
    s = list((u * (n // plen + 1))[:n])
    for _ in range(mutate):
        s[r.randrange(n)] = r.choice(alpha)
    return "".join(s)


def _g_small(r, nmax=14):
    """Random small string; often with periodic / bordered structure so that borders matter."""
    n = r.randint(1, nmax)
    t = r.random()
    if t < 0.35:
        return _rs(r, n, "ab")
    if t < 0.5:
        return _rs(r, n, "abc")
    if t < 0.9:
        return _periodic(r, n, r.randint(1, 4), "ab", r.choice([0, 0, 1]))
    return "a" * n


# ---------------------------------------------------------------- EASY

p = add(
    id="prefix-function-array", title="Prefix Function Array", diff="Easy", topic=TOPIC, tier="must",
    fn="prefixFunction", params=[("s", "string")], ret="int[]", cmp="exact",
    desc="<p>For a string <code>s</code> of length <code>n</code>, build the array <code>pi</code> of length <code>n</code> where <code>pi[i]</code> is the length of the longest <em>proper</em> prefix of <code>s[0..i]</code> that is also a suffix of <code>s[0..i]</code>. A proper prefix is shorter than the whole substring, so <code>pi[0]</code> is always <code>0</code>.</p><p>Example: for <code>s = \"aabaaab\"</code> the answer is <code>[0,1,0,1,2,2,3]</code>. For the last prefix <code>\"aabaaab\"</code> the longest proper prefix that is also a suffix is <code>\"aab\"</code>, which has length 3.</p><p>Return the array. A solution that runs in O(n) time exists (this array is the heart of the KMP algorithm).</p>",
    constraints=["1 &le; s.length &le; 4,000", "s consists of lowercase English letters"],
    hints=["Computing every <code>pi[i]</code> by comparing all candidate lengths is O(n<sup>2</sup>) or worse. Look for a relation between <code>pi[i]</code> and <code>pi[i-1]</code>.",
           "If the prefix of length <code>k = pi[i-1]</code> can be extended, that is <code>s[k] == s[i]</code>, then <code>pi[i] = k + 1</code>.",
           "If <code>s[k] != s[i]</code>, the next best candidate border of <code>s[0..i-1]</code> is the border of the border, <code>k = pi[k-1]</code>. Repeat until the characters agree or <code>k</code> is zero."],
    editorial=["Process the string left to right and keep <code>k</code>, the length of the longest border of the previous prefix. Every border of <code>s[0..i]</code> that has length at least 1 is a border of <code>s[0..i-1]</code> extended by the character <code>s[i]</code>. So we look through the borders of <code>s[0..i-1]</code> from the longest to the shortest, and take the first one that is followed by the character <code>s[i]</code>.",
               "The borders of a prefix form a chain: after the longest border of length <code>k</code>, the next longest is <code>pi[k-1]</code>, then <code>pi[pi[k-1]-1]</code> and so on. This is why a mismatch is handled by <code>k = pi[k-1]</code>.",
               "Amortised analysis: <code>k</code> grows by at most one per character and every fallback step strictly decreases it, never below zero. The total number of fallback steps is therefore at most <code>n</code>, giving O(n) time and O(n) space for the output."],
    time="O(n)", space="O(n)",
    solution='''def prefixFunction(s):
    n = len(s)
    pi = [0] * n
    k = 0
    for i in range(1, n):
        while k and s[i] != s[k]:
            k = pi[k - 1]
        if s[i] == s[k]:
            k += 1
        pi[i] = k
    return pi
''',
    tests=[["aabaaab"], ["abab"], ["a"], ["ab"], ["aaaa"], ["abcd"], ["abcabcabc"], ["aabaabaaa"], ["abacabadabacaba"],
           ["abaabaaba"], ["zzzzyzzzzz"]],
)
_r = rnd(9101)
p["tests"].append(["a" * 3500 + "b"])
p["tests"].append([_fib(3000)])
p["tests"].append([_rs(_r, 3500, "ab")])


def b_prefix_function(s):
    out = []
    for i in range(len(s)):
        sub = s[:i + 1]
        best = 0
        for L in range(1, len(sub)):
            if sub[:L] == sub[-L:]:
                best = L
        out.append(best)
    return out


def v_prefix_function(tests):
    for t in tests:
        s = t["args"][0]
        assert 1 <= len(s) <= 4000 and _lower(s)
        assert len(t["expected"]) == len(s) and t["expected"][0] == 0


CHECKS["prefix-function-array"] = (b_prefix_function, lambda r: [_g_small(r)], "exact")
VALIDATE["prefix-function-array"] = v_prefix_function

p = add(
    id="pattern-occurrence-positions", title="All Occurrences of a Pattern", diff="Easy", topic=TOPIC,
    fn="findAllOccurrences", params=[("text", "string"), ("pattern", "string")], ret="int[]", cmp="exact",
    desc="<p>Return the start index of every occurrence of <code>pattern</code> inside <code>text</code>, in increasing order. Occurrences may overlap. If <code>pattern</code> does not occur, return an empty array.</p><p>Example: <code>text = \"aaabaaa\"</code> and <code>pattern = \"aa\"</code> give <code>[0,1,4,5]</code>, because <code>\"aa\"</code> starts at indices 0, 1, 4 and 5.</p>",
    constraints=["1 &le; text.length, pattern.length &le; 5,000", "Both strings consist of lowercase English letters", "pattern may be longer than text, in which case the answer is empty"],
    hints=["Checking every start index with a slice comparison is O(n &middot; m) in the worst case. Is that acceptable for these limits? Can it be made linear?",
           "After a full match, you do not have to restart from scratch: the pattern's longest border says how much of the match can be reused for the next, overlapping, occurrence.",
           "Run KMP: build the prefix function of <code>pattern</code>, scan <code>text</code> with a matched-length counter <code>k</code>, record <code>i - m + 1</code> whenever <code>k == m</code>, and then set <code>k = pi[k-1]</code> to continue."],
    editorial=["Build the prefix function <code>pi</code> of the pattern. Scan the text with a counter <code>k</code> of currently matched pattern characters: on a mismatch fall back with <code>k = pi[k-1]</code>, on a match increase <code>k</code>. When <code>k</code> reaches the pattern length <code>m</code>, an occurrence ends at the current index <code>i</code>, so it starts at <code>i - m + 1</code>.",
               "To find the next occurrence, which may overlap this one, continue with <code>k = pi[m-1]</code>, the longest border of the pattern. Everything before that is already known to match.",
               "Total work is O(n + m) because <code>k</code> grows by at most one per text character and each fallback lowers it. The same code works as a Z-function approach on <code>pattern + '#' + text</code>, where each value equal to <code>m</code> marks an occurrence."],
    time="O(n + m)", space="O(m)",
    solution='''def findAllOccurrences(text, pattern):
    m = len(pattern)
    pi = [0] * m
    k = 0
    for i in range(1, m):
        while k and pattern[i] != pattern[k]:
            k = pi[k - 1]
        if pattern[i] == pattern[k]:
            k += 1
        pi[i] = k
    res = []
    k = 0
    for i, c in enumerate(text):
        while k and c != pattern[k]:
            k = pi[k - 1]
        if c == pattern[k]:
            k += 1
        if k == m:
            res.append(i - m + 1)
            k = pi[k - 1]
    return res
''',
    tests=[["aaabaaa", "aa"], ["abababab", "abab"], ["abc", "d"], ["a", "a"], ["abc", "abcd"], ["mississippi", "issi"],
           ["aaaa", "aaaa"], ["abcabcabc", "bc"], ["xyz", "z"], ["abaababaabaab", "abaab"]],
)
_r = rnd(9102)
p["tests"].append(["a" * 5000, "aa"])
_t = _rs(_r, 5000, "ab")
p["tests"].append([_t, "ab"])
p["tests"].append([_t, _t[2000:2030]])


def b_occ_positions(text, pattern):
    m = len(pattern)
    return [i for i in range(len(text) - m + 1) if text[i:i + m] == pattern]


def g_occ_positions(r):
    t = _rs(r, r.randint(1, 16), "ab")
    if r.random() < 0.7 and len(t) > 1:
        i = r.randrange(len(t))
        pt = t[i:i + r.randint(1, 5)]
    else:
        pt = _rs(r, r.randint(1, 4), "ab")
    return [t, pt]


def v_occ_positions(tests):
    for t in tests:
        a, b = t["args"]
        assert 1 <= len(a) <= 5000 and 1 <= len(b) <= 5000 and _lower(a) and _lower(b)
        assert t["expected"] == sorted(t["expected"])


CHECKS["pattern-occurrence-positions"] = (b_occ_positions, g_occ_positions, "exact")
VALIDATE["pattern-occurrence-positions"] = v_occ_positions

# ---------------------------------------------------------------- MEDIUM

p = add(
    id="all-border-lengths", title="All Border Lengths", diff="Medium", topic=TOPIC,
    fn="allBorders", params=[("s", "string")], ret="int[]", cmp="exact",
    desc="<p>A <em>border</em> of a string <code>s</code> is a non-empty proper prefix of <code>s</code> that is also a suffix of <code>s</code>. Return the lengths of <strong>all</strong> borders of <code>s</code> in increasing order. If <code>s</code> has no border, return an empty array.</p><p>Example: <code>s = \"abaabaaba\"</code> has the borders <code>\"a\"</code>, <code>\"aba\"</code> and <code>\"abaaba\"</code>, so the answer is <code>[1,3,6]</code>.</p>",
    constraints=["1 &le; s.length &le; 10,000", "s consists of lowercase English letters"],
    hints=["Comparing every prefix length with the same-length suffix is O(n<sup>2</sup>). Do you really need to examine every length?",
           "The longest border can be read from the prefix function: it is <code>pi[n-1]</code>.",
           "Every shorter border of <code>s</code> is also a border of the longest border. So walk the chain <code>k = pi[n-1]</code>, then <code>pi[k-1]</code>, then <code>pi[pi[k-1]-1]</code>, ... until it reaches zero, and reverse the collected lengths."],
    editorial=["Compute the prefix function of <code>s</code>. The longest border has length <code>b = pi[n-1]</code>. A shorter border <code>c</code> is both a prefix and a suffix of <code>s</code>; since it is a prefix of the longest border and also a suffix of it (it sits at the end of <code>s</code>, inside the final <code>b</code> characters), <code>c</code> is a border of <code>s[0..b-1]</code> as well. Its longest such border has length <code>pi[b-1]</code>, and so on.",
               "So the full list of borders is the chain <code>b, pi[b-1], pi[pi[b-1]-1], ...</code> until the value hits 0. Collect it and reverse it to get increasing order.",
               "Building <code>pi</code> costs O(n); the chain has at most n links. Total O(n) time. The Z-function gives an alternative: position <code>i</code> starts a border exactly when <code>i + z[i] == n</code>, and its length is <code>n - i</code>."],
    time="O(n)", space="O(n)",
    solution='''def allBorders(s):
    n = len(s)
    pi = [0] * n
    k = 0
    for i in range(1, n):
        while k and s[i] != s[k]:
            k = pi[k - 1]
        if s[i] == s[k]:
            k += 1
        pi[i] = k
    res = []
    k = pi[-1]
    while k:
        res.append(k)
        k = pi[k - 1]
    res.reverse()
    return res
''',
    tests=[["abaabaaba"], ["aaaa"], ["abcd"], ["a"], ["abab"], ["abacaba"], ["aabaabaa"], ["abcabcabcabc"], ["xyzxy"],
           ["aabaaabaabaaabaa"]],
)
_r = rnd(9103)
p["tests"].append(["a" * 4000])
p["tests"].append([_fib(4000)])
p["tests"].append([_periodic(_r, 4000, 7, "abc")])


def b_all_borders(s):
    n = len(s)
    return [L for L in range(1, n) if s[:L] == s[n - L:]]


def v_all_borders(tests):
    for t in tests:
        s = t["args"][0]
        assert 1 <= len(s) <= 10000 and _lower(s)
        e = t["expected"]
        assert e == sorted(set(e)) and all(1 <= x < len(s) for x in e)


CHECKS["all-border-lengths"] = (b_all_borders, lambda r: [_g_small(r, 16)], "exact")
VALIDATE["all-border-lengths"] = v_all_borders

p = add(
    id="prefix-repetition-counts", title="Prefix Repetition Counts", diff="Medium", topic=TOPIC,
    fn="prefixRepetitions", params=[("s", "string")], ret="int[]", cmp="exact",
    desc="<p>For each prefix <code>s[0..i]</code> of the string <code>s</code>, find the largest integer <code>k &ge; 1</code> such that the prefix can be written as some block <code>u</code> repeated exactly <code>k</code> times (<code>u + u + ... + u</code>, with <code>u</code> non-empty). Return an array of length <code>n</code> whose entry <code>i</code> is that <code>k</code> for the prefix of length <code>i + 1</code>.</p><p>Example: <code>s = \"aabaabaabaab\"</code> gives <code>[1,2,1,1,1,2,1,1,3,1,1,4]</code>. The prefix <code>\"aa\"</code> is <code>\"a\"</code> twice, <code>\"aabaab\"</code> is <code>\"aab\"</code> twice, <code>\"aabaabaab\"</code> is <code>\"aab\"</code> three times, and the whole string is <code>\"aab\"</code> four times. A prefix that is not a repetition counts as <code>1</code>.</p>",
    constraints=["1 &le; s.length &le; 4,000", "s consists of lowercase English letters"],
    hints=["Checking every divisor of every prefix length against the prefix is far too slow. Use something that already knows the structure of every prefix.",
           "A prefix of length <code>L</code> has smallest period <code>L - pi[L-1]</code>. The prefix is a perfect repetition of a block when this period divides <code>L</code>.",
           "If <code>p = L - pi[L-1]</code> and <code>L % p == 0</code>, the answer for this prefix is <code>L / p</code>; otherwise it is 1. The smallest block gives the largest repeat count."],
    editorial=["Let <code>pi</code> be the prefix function. For a string of length <code>L</code>, the length of the shortest period is <code>p = L - pi[L-1]</code> (a border of length <code>b</code> means the string repeats with shift <code>L - b</code>). The string is an exact power of a block precisely when it has a period that divides <code>L</code>, and in that case the smallest period <code>p</code> divides <code>L</code> too (this is the periodicity lemma for the smallest period).",
               "So for each prefix length <code>L</code>: if <code>L % p == 0</code> the answer is <code>L / p</code>, otherwise there is no proper repetition and the answer is 1. Using the smallest block yields the largest <code>k</code>.",
               "One pass to build <code>pi</code> and one pass over the prefixes: O(n) time, O(n) space."],
    time="O(n)", space="O(n)",
    solution='''def prefixRepetitions(s):
    n = len(s)
    pi = [0] * n
    k = 0
    for i in range(1, n):
        while k and s[i] != s[k]:
            k = pi[k - 1]
        if s[i] == s[k]:
            k += 1
        pi[i] = k
    res = []
    for i in range(n):
        L = i + 1
        per = L - pi[i]
        res.append(L // per if L % per == 0 else 1)
    return res
''',
    tests=[["aabaabaabaab"], ["aaaa"], ["abcd"], ["a"], ["abab"], ["abcabcab"], ["aabaaab"], ["ababababab"],
           ["abaababaabaab"], ["zzzzzzzzzzzz"]],
)
_r = rnd(9104)
p["tests"].append(["a" * 4000])
p["tests"].append([_periodic(_r, 4000, 6, "ab", 1)])
p["tests"].append([_fib(3500)])


def b_prefix_rep(s):
    res = []
    for L in range(1, len(s) + 1):
        pre = s[:L]
        best = 1
        for k in range(L, 0, -1):
            if L % k == 0 and pre[:L // k] * k == pre:
                best = k
                break
        res.append(best)
    return res


def v_prefix_rep(tests):
    for t in tests:
        s = t["args"][0]
        assert 1 <= len(s) <= 4000 and _lower(s)
        assert len(t["expected"]) == len(s) and all(x >= 1 for x in t["expected"])


CHECKS["prefix-repetition-counts"] = (b_prefix_rep, lambda r: [_g_small(r, 16)], "exact")
VALIDATE["prefix-repetition-counts"] = v_prefix_rep

p = add(
    id="border-reappearing-inside", title="Border That Reappears Inside", diff="Medium", topic=TOPIC,
    fn="longestInnerBorder", params=[("s", "string")], ret="int", cmp="exact",
    desc="<p>Find the length of the longest string <code>t</code> that satisfies all three conditions:</p><ul><li><code>t</code> is a non-empty proper prefix of <code>s</code>;</li><li><code>t</code> is also a suffix of <code>s</code>;</li><li><code>t</code> occurs a third time inside <code>s</code>, starting at some index <code>i</code> with <code>0 &lt; i &lt; n - |t|</code> (so this occurrence is neither the prefix nor the suffix; it may overlap them).</li></ul><p>Return <code>|t|</code>, or <code>0</code> if no such string exists.</p><p>Example: for <code>s = \"abcabcab\"</code> the border <code>\"abcab\"</code> has no third copy, but the border <code>\"ab\"</code> also occurs at index 3, so the answer is <code>2</code>. For <code>s = \"aaaa\"</code> the answer is <code>2</code>: the string <code>\"aa\"</code> is a prefix, a suffix, and also occurs at index 1.</p>",
    constraints=["1 &le; s.length &le; 10,000", "s consists of lowercase English letters"],
    hints=["First list the candidates: only borders of <code>s</code> can be <code>t</code>. Which of them have a third occurrence?",
           "A prefix of length <code>L</code> occurs ending at index <code>j</code> (with <code>j &le; n-2</code>) as soon as <code>pi[j] &ge; L</code>. So all you need is <code>M = max(pi[0..n-2])</code>.",
           "Walk the border chain <code>pi[n-1], pi[pi[n-1]-1], ...</code> from the longest to the shortest and return the first value that is at most <code>M</code>; if the chain ends, return 0."],
    editorial=["Candidate strings are the borders of <code>s</code>; they form the chain <code>b1 &gt; b2 &gt; ...</code> where <code>b1 = pi[n-1]</code> and <code>b_{k+1} = pi[b_k - 1]</code>.",
               "A border of length <code>L</code> has an inner occurrence if and only if some position <code>j &le; n-2</code> has <code>pi[j] &ge; L</code>. If <code>pi[j] &ge; L</code>, the prefix of length <code>pi[j]</code> ends at <code>j</code> and starts at <code>j - pi[j] + 1 &ge; 1</code>, and its first <code>L</code> characters are a copy of <code>s[0..L-1]</code> that starts at the same index and ends no later than <code>j &le; n-2</code>, so the copy is strictly inside. Conversely an inner occurrence ending at <code>j</code> forces <code>pi[j] &ge; L</code>.",
               "Therefore compute <code>M = max(pi[0..n-2])</code> and take the first border in the chain with length at most <code>M</code>. Everything is O(n)."],
    time="O(n)", space="O(n)",
    solution='''def longestInnerBorder(s):
    n = len(s)
    pi = [0] * n
    k = 0
    for i in range(1, n):
        while k and s[i] != s[k]:
            k = pi[k - 1]
        if s[i] == s[k]:
            k += 1
        pi[i] = k
    if n < 3:
        return 0
    m = max(pi[:-1])
    k = pi[-1]
    while k > m:
        k = pi[k - 1]
    return k
''',
    tests=[["abcabcab"], ["aaaa"], ["abcd"], ["a"], ["aa"], ["aaa"], ["abaxabaxaba"], ["abacaba"], ["xyxyxyxy"],
           ["fixprefixsuffix"], ["abcxabcyabc"], ["aabaabaabaa"]],
)
_r = rnd(9105)
p["tests"].append(["a" * 7000])
p["tests"].append([_fib(7000)])
p["tests"].append(["ab" + _rs(_r, 6000, "cd") + "ab" + _rs(_r, 500, "cd") + "ab"])


def b_inner_border(s):
    n = len(s)
    for L in range(n - 1, 0, -1):
        if s[:L] == s[n - L:]:
            for i in range(1, n - L):
                if s[i:i + L] == s[:L]:
                    return L
    return 0


def v_inner_border(tests):
    for t in tests:
        s = t["args"][0]
        assert 1 <= len(s) <= 10000 and _lower(s)
        assert 0 <= t["expected"] < len(s)


CHECKS["border-reappearing-inside"] = (b_inner_border, lambda r: [_g_small(r, 16)], "exact")
VALIDATE["border-reappearing-inside"] = v_inner_border

p = add(
    id="pattern-prefix-match-lengths", title="Pattern Prefix Match at Every Position", diff="Medium", topic=TOPIC,
    fn="prefixMatchLengths", params=[("pattern", "string"), ("text", "string")], ret="int[]", cmp="exact",
    desc="<p>For every index <code>i</code> of <code>text</code>, compute the length of the longest prefix of <code>pattern</code> that appears in <code>text</code> starting exactly at <code>i</code>. In other words, the length of the longest common prefix of <code>pattern</code> and <code>text[i..]</code>. Return an array with one entry per position of <code>text</code>.</p><p>Example: <code>pattern = \"aab\"</code> and <code>text = \"aabaaab\"</code> give <code>[3,1,0,2,3,1,0]</code>. At index 3 the text continues with <code>\"aaab\"</code>, which shares only <code>\"aa\"</code> with the pattern, so the value is 2.</p>",
    constraints=["1 &le; pattern.length, text.length &le; 4,000", "Both strings consist of lowercase English letters"],
    hints=["Extending each position character by character is O(n &middot; m) in the worst case (think <code>\"aaaa...\"</code>). You need to reuse earlier work.",
           "The Z-function of a string gives, at each index, the longest common prefix with the whole string. Can you turn the pattern and the text into one string?",
           "Compute the Z-function of <code>pattern + '#' + text</code> (the separator is not a lowercase letter, so matches never run past the pattern). The values after the separator are the answers."],
    editorial=["Concatenate <code>pattern</code>, a separator that cannot occur in the input such as <code>'#'</code>, and <code>text</code>. The Z-function <code>z[j]</code> is the length of the longest common prefix of the concatenation and its suffix starting at <code>j</code>. For positions inside the text part, that prefix is a prefix of the pattern, and it is automatically capped at <code>m</code> by the separator.",
               "So the answer for text index <code>i</code> is <code>z[m + 1 + i]</code>. The Z-algorithm keeps a window <code>[l, r)</code> that matches the string's prefix; positions inside the window start from the already known value <code>z[j - l]</code> (capped by the window end) and extend only beyond the window, which gives linear total work.",
               "Time O(n + m) and space O(n + m). The result is also the 'matching statistics against a prefix' that KMP implicitly computes, but with the Z-function it is available for every position, not only where the match is maximal."],
    time="O(n + m)", space="O(n + m)",
    solution='''def prefixMatchLengths(pattern, text):
    m = len(pattern)
    s = pattern + '#' + text
    n = len(s)
    z = [0] * n
    l = r = 0
    for i in range(1, n):
        if i < r:
            z[i] = min(r - i, z[i - l])
        while i + z[i] < n and s[z[i]] == s[i + z[i]]:
            z[i] += 1
        if i + z[i] > r:
            l, r = i, i + z[i]
    return z[m + 1:]
''',
    tests=[["aab", "aabaaab"], ["abc", "abcabcabd"], ["a", "bbb"], ["abab", "ababab"], ["zz", "zzzz"], ["abc", "x"],
           ["aaaa", "aaabaaaa"], ["abcd", "abcdabcd"], ["xyz", "abc"], ["ab", "b"]],
)
_r = rnd(9106)
p["tests"].append(["a" * 2000, "a" * 3999 + "b"])
_t = _rs(_r, 4000, "ab")
p["tests"].append([_t[100:160], _t])
p["tests"].append([_fib(1500), _fib(4000)])


def b_pm(pattern, text):
    res = []
    for i in range(len(text)):
        k = 0
        while k < len(pattern) and i + k < len(text) and text[i + k] == pattern[k]:
            k += 1
        res.append(k)
    return res


def g_pm(r):
    t = _rs(r, r.randint(1, 14), "ab")
    if r.random() < 0.6 and len(t) > 1:
        i = r.randrange(len(t))
        pt = t[i:i + r.randint(1, 6)]
    else:
        pt = _rs(r, r.randint(1, 5), "ab")
    return [pt, t]


def v_pm(tests):
    for t in tests:
        a, b = t["args"]
        assert 1 <= len(a) <= 4000 and 1 <= len(b) <= 4000 and _lower(a) and _lower(b)
        assert len(t["expected"]) == len(b)


CHECKS["pattern-prefix-match-lengths"] = (b_pm, g_pm, "exact")
VALIDATE["pattern-prefix-match-lengths"] = v_pm

p = add(
    id="circular-text-occurrences", title="Occurrences in a Circular Text", diff="Medium", topic=TOPIC,
    fn="countCircularOccurrences", params=[("text", "string"), ("pattern", "string")], ret="int", cmp="exact",
    desc="<p>Imagine <code>text</code> written around a circle, so that after its last character comes its first character again. For a start index <code>i</code> (<code>0 &le; i &lt; n</code>), read <code>m</code> consecutive characters clockwise from <code>i</code>, wrapping around the end when needed. Count the start indices for which the characters read equal <code>pattern</code>.</p><p>Example: <code>text = \"abaab\"</code> and <code>pattern = \"aba\"</code>. Starting at 0 gives <code>\"aba\"</code> and starting at 3 gives <code>\"ab\"</code> followed by the wrapped-around <code>\"a\"</code>, which is <code>\"aba\"</code> as well. The answer is <code>2</code>.</p>",
    constraints=["1 &le; pattern.length &le; text.length &le; 20,000", "Both strings consist of lowercase English letters"],
    hints=["Building each of the n windows by taking indices modulo n and comparing is O(n &middot; m).",
           "Occurrences that wrap around the end are ordinary occurrences in a longer, unrolled string.",
           "Search for <code>pattern</code> in <code>text + text[:m-1]</code> with KMP (or the Z-function) and count the matches. Every start index <code>0..n-1</code> is covered exactly once, with no double counting, because the extended string has length <code>n + m - 1</code>."],
    editorial=["Unroll the circle. A window starting at index <code>i</code> that does not wrap is a window of <code>text</code>; one that wraps reads the tail of <code>text</code> and then a prefix of it. Both kinds are windows of <code>t = text + text[:m-1]</code>, which has <code>n + m - 1</code> characters and therefore exactly <code>n</code> windows of length <code>m</code>, starting at <code>0..n-1</code>: one per circular start.",
               "Because <code>m &le; n</code>, the extra <code>m - 1</code> characters never need to wrap a second time. Count the occurrences of the pattern in <code>t</code> with KMP: build <code>pi</code> of the pattern, scan <code>t</code>, and count every time the matched length reaches <code>m</code>, falling back by <code>pi[m-1]</code> afterwards.",
               "O(n + m) time, O(n + m) space. A common alternative is to pass over <code>text + text</code>, but then you must stop after n start positions to avoid counting a window twice."],
    time="O(n + m)", space="O(n + m)",
    solution='''def countCircularOccurrences(text, pattern):
    m = len(pattern)
    t = text + text[:m - 1]
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
    for c in t:
        while k and c != pattern[k]:
            k = pi[k - 1]
        if c == pattern[k]:
            k += 1
        if k == m:
            count += 1
            k = pi[k - 1]
    return count
''',
    tests=[["abaab", "aba"], ["aaaa", "aa"], ["aaaa", "aaaa"], ["abc", "cab"], ["a", "a"], ["ab", "ba"], ["abcabc", "bca"],
           ["abab", "abab"], ["xyzxyz", "zx"], ["abcd", "dcb"], ["aabaa", "aaa"]],
)
_r = rnd(9107)
p["tests"].append(["a" * 20000, "a" * 9999])
_t = _rs(_r, 20000, "ab")
p["tests"].append([_t, _t[-6:] + _t[:6]])
p["tests"].append([_periodic(_r, 20000, 5, "ab"), "ababa"])


def b_circ(text, pattern):
    n, m = len(text), len(pattern)
    return sum(1 for i in range(n) if all(text[(i + j) % n] == pattern[j] for j in range(m)))


def g_circ(r):
    n = r.randint(1, 12)
    t = _rs(r, n, "ab") if r.random() < 0.7 else _periodic(r, n, r.randint(1, 3))
    m = r.randint(1, n)
    if r.random() < 0.7:
        i = r.randrange(n)
        pt = "".join(t[(i + j) % n] for j in range(m))
    else:
        pt = _rs(r, m, "ab")
    return [t, pt]


def v_circ(tests):
    for t in tests:
        a, b = t["args"]
        assert 1 <= len(b) <= len(a) <= 20000 and _lower(a) and _lower(b)


CHECKS["circular-text-occurrences"] = (b_circ, g_circ, "exact")
VALIDATE["circular-text-occurrences"] = v_circ

p = add(
    id="minimum-appends-to-repeat", title="Minimum Appends to Make a Repetition", diff="Medium", topic=TOPIC, tier="extra",
    fn="minAppendsToRepeat", params=[("s", "string")], ret="int", cmp="exact",
    desc="<p>You may append lowercase letters, of your choice, to the <strong>end</strong> of <code>s</code>. Return the minimum number of letters that must be appended so that the resulting string consists of some non-empty block repeated <strong>at least twice</strong> (<code>u + u</code>, <code>u + u + u</code>, ...).</p><p>Example: for <code>s = \"abaab\"</code> appending the single letter <code>a</code> gives <code>\"abaaba\" = \"aba\" + \"aba\"</code>, so the answer is <code>1</code>. If <code>s</code> is already such a repetition, e.g. <code>\"abab\"</code>, the answer is <code>0</code>. For <code>s = \"a\"</code> the answer is <code>1</code>, giving <code>\"aa\"</code>.</p>",
    constraints=["1 &le; s.length &le; 10,000", "s consists of lowercase English letters"],
    hints=["If the final string is <code>u</code> repeated, every character <code>s[i]</code> must equal <code>s[i + |u|]</code> whenever both exist. Which block lengths <code>p</code> make that true for the given <code>s</code>?",
           "Such a block length <code>p</code> is a <em>period</em> of <code>s</code>; periods correspond to borders: <code>p</code> is a period exactly when <code>s</code> has a border of length <code>n - p</code> (and <code>p = n</code> is always a period).",
           "For a period <code>p &lt; n</code> you must reach the next multiple of <code>p</code>, costing <code>(-n) mod p</code> letters. The block <code>u = s</code> itself (<code>p = n</code>) costs <code>n</code>. Take the minimum over all periods, not only the shortest one."],
    editorial=["The result has length <code>L</code> and is a block of length <code>p</code> repeated <code>L / p &ge; 2</code> times. The first <code>n</code> characters are our <code>s</code>, so <code>s</code> must itself obey <code>s[i] = s[i+p]</code> for all valid <code>i</code>: that is, <code>p</code> is a period of <code>s</code> (when <code>p &ge; n</code> there is no constraint, but then <code>L &ge; 2p &ge; 2n</code>, which is never better than the choice <code>p = n</code> costing exactly <code>n</code>).",
               "For a period <code>p &lt; n</code> the smallest valid length is the next multiple of <code>p</code> at or after <code>n</code>, which is at least <code>2p</code> because <code>n &gt; p</code>; the cost is <code>(p - n % p) % p</code>. The appended letters are forced to continue the periodic pattern, so they always exist.",
               "All periods are <code>n - b</code> for the borders <code>b</code> of <code>s</code>, which come from the chain <code>pi[n-1], pi[pi[n-1]-1], ...</code>. The shortest period is not always the best choice (for example a longer period may divide <code>n</code>-adjacent lengths better), so evaluate every period and keep the minimum. Total O(n)."],
    time="O(n)", space="O(n)",
    solution='''def minAppendsToRepeat(s):
    n = len(s)
    pi = [0] * n
    k = 0
    for i in range(1, n):
        while k and s[i] != s[k]:
            k = pi[k - 1]
        if s[i] == s[k]:
            k += 1
        pi[i] = k
    best = n
    b = pi[-1]
    while b:
        p = n - b
        best = min(best, (-n) % p)
        b = pi[b - 1]
    return best
''',
    tests=[["abaab"], ["abab"], ["a"], ["ab"], ["aaa"], ["abcabcab"], ["abcd"], ["aabaa"], ["abaabaabaa"], ["xyxxyx"],
           ["aabaabaaab"]],
)
_r = rnd(9108)
p["tests"].append(["a" * 9999 + "b"])
p["tests"].append([_periodic(_r, 9999, 37, "abc")])
p["tests"].append([_rs(_r, 9000, "abc")])


def b_appends(s):
    n = len(s)
    for k in range(0, n + 1):
        total = n + k
        for p in range(1, total // 2 + 1):
            if total % p:
                continue
            if all(s[i] == s[i + p] for i in range(n - p)):
                return k
    return n


def v_appends(tests):
    for t in tests:
        s = t["args"][0]
        assert 1 <= len(s) <= 10000 and _lower(s)
        assert 0 <= t["expected"] <= len(s)


CHECKS["minimum-appends-to-repeat"] = (b_appends, lambda r: [_g_small(r, 16)], "exact")
VALIDATE["minimum-appends-to-repeat"] = v_appends

# ---------------------------------------------------------------- HARD

p = add(
    id="shortest-covering-prefix", title="Shortest Covering Prefix", diff="Hard", topic=TOPIC, tier="extra",
    fn="shortestCover", params=[("s", "string")], ret="int", cmp="exact",
    desc="<p>A prefix <code>c</code> of <code>s</code> <em>covers</em> <code>s</code> if every position of <code>s</code> lies inside at least one occurrence of <code>c</code> in <code>s</code>. Occurrences may overlap. The whole string always covers itself.</p><p>Return the length of the shortest covering prefix.</p><p>Examples: <code>\"abaababaab\"</code> is covered by <code>\"abaab\"</code> (occurrences at indices 0 and 5), so the answer is <code>5</code>. <code>\"abababa\"</code> is covered by <code>\"aba\"</code> at indices 0, 2 and 4, so the answer is <code>3</code>. <code>\"aabaaaab\"</code> has no shorter cover, so the answer is <code>8</code>.</p>",
    constraints=["1 &le; s.length &le; 8,000", "s consists of lowercase English letters"],
    hints=["Testing every prefix length with a full search for its occurrences costs O(n<sup>2</sup>) or worse. Which prefixes can be covers at all?",
           "A cover must start and end the string, so it is a border of <code>s</code> (or <code>s</code> itself). Its occurrences must also leave no gap: consecutive occurrence ends must be at most <code>|c|</code> apart.",
           "Compute <code>cover[i]</code>, the shortest cover of every prefix, in increasing <code>i</code>. For prefix <code>i</code> let <code>c = cover[pi[i]]</code>; this <code>c</code> also covers the prefix of length <code>i</code> if the previous occurrence of the prefix of length <code>c</code> ended at most <code>c</code> positions before <code>i</code>. Remember <code>last[c]</code>, the end of the latest occurrence."],
    editorial=["Work on every prefix of <code>s</code>, not only on <code>s</code>. Let <code>cover[L]</code> be the length of the shortest covering prefix of the prefix <code>s[0..L-1]</code>; by default it is <code>L</code> itself. A covering prefix of a string is a border of it, so for prefix length <code>L</code> the only candidate that could be better than <code>L</code> is a cover of the longest border <code>b = pi[L-1]</code>, namely <code>c = cover[b]</code> (a shorter border cannot do better than what the longest border already achieved).",
               "The candidate <code>c</code> works for the prefix of length <code>L</code> if and only if it leaves no gap before the new occurrence that ends at <code>L</code>. Keep <code>last[c]</code>, the end of the most recent occurrence of the prefix <code>s[:c]</code> that was used as a cover. If <code>L - last[c] &le; c</code>, the new occurrence overlaps or touches the covered region, so set <code>cover[L] = c</code> and <code>last[c] = L</code>. Otherwise <code>cover[L] = L</code> and <code>last[L] = L</code>.",
               "Answer <code>cover[n]</code>. Each prefix is handled in O(1) after the prefix function, so the algorithm is O(n) time and space. A brute-force check (mark all occurrences of each prefix and test full coverage) is O(n<sup>2</sup>) and is a good way to test your implementation."],
    time="O(n)", space="O(n)",
    solution='''def shortestCover(s):
    n = len(s)
    pi = [0] * n
    k = 0
    for i in range(1, n):
        while k and s[i] != s[k]:
            k = pi[k - 1]
        if s[i] == s[k]:
            k += 1
        pi[i] = k
    cover = [0] * (n + 1)
    last = [0] * (n + 1)
    for L in range(1, n + 1):
        cover[L] = L
        b = pi[L - 1]
        if b:
            c = cover[b]
            if L - last[c] <= c:
                cover[L] = c
                last[c] = L
                continue
        last[L] = L
    return cover[n]
''',
    tests=[["abaababaab"], ["abababa"], ["aabaaaab"], ["a"], ["aaaa"], ["abcd"], ["abcabcabc"], ["aabaabaa"], ["ababaab"],
           ["abaabaaba"], ["abcabcabcab"], ["aabaabaabaabaa"]],
)
_r = rnd(9109)
p["tests"].append(["a" * 8000])
p["tests"].append([_fib(8000)])
_u = _rs(_r, 40, "abc")
p["tests"].append([(_u + _u[10:] + _u[3:] + _u[20:] + _u[7:]) * 25 + _u])


def b_cover(s):
    n = len(s)
    for L in range(1, n + 1):
        c = s[:L]
        mark = [False] * n
        for i in range(n - L + 1):
            if s[i:i + L] == c:
                for j in range(i, i + L):
                    mark[j] = True
        if all(mark):
            return L
    return n


def g_cover(r):
    n = r.randint(1, 16)
    t = r.random()
    if t < 0.4:
        return _rs(r, n, "ab")
    if t < 0.8:
        # overlapping copies of a block, glued with random overlaps
        u = _rs(r, r.randint(1, 5), "ab")
        s = u
        while len(s) < n:
            ov = r.randint(0, len(u))
            s += u[ov:] if r.random() < 0.8 else _rs(r, 1, "ab") + u
        return s[:n]
    return _periodic(r, n, r.randint(1, 4), "ab", r.choice([0, 1]))


def v_cover(tests):
    for t in tests:
        s = t["args"][0]
        assert 1 <= len(s) <= 8000 and _lower(s)
        assert 1 <= t["expected"] <= len(s)


CHECKS["shortest-covering-prefix"] = (b_cover, lambda r: [g_cover(r)], "exact")
VALIDATE["shortest-covering-prefix"] = v_cover

p = add(
    id="count-strings-avoiding-pattern", title="Count Strings Avoiding a Pattern", diff="Hard", topic=TOPIC, tier="extra",
    fn="countAvoiding", params=[("pattern", "string"), ("n", "int"), ("k", "int")], ret="int", cmp="exact",
    desc="<p>Consider strings of length <code>n</code> over the alphabet of the first <code>k</code> lowercase letters (<code>'a'</code>, <code>'b'</code>, ... ). Count how many of them do <strong>not</strong> contain <code>pattern</code> as a contiguous substring. Return the count modulo <code>1,000,000,007</code>.</p><p>Example: <code>pattern = \"ab\"</code>, <code>n = 3</code>, <code>k = 2</code>: of the 8 strings over <code>{a,b}</code> only <code>aaa</code>, <code>baa</code>, <code>bba</code> and <code>bbb</code> avoid <code>\"ab\"</code>, so the answer is <code>4</code>. For <code>pattern = \"aa\"</code>, <code>n = 4</code>, <code>k = 2</code> the answer is <code>8</code>.</p>",
    constraints=["1 &le; pattern.length &le; 40", "1 &le; n &le; 500", "1 &le; k &le; 26", "pattern uses only the first k lowercase letters"],
    hints=["Count with dynamic programming over the length of the string built so far. What is the minimum information about the prefix that tells you whether the pattern can still appear?",
           "Only the length of the longest suffix of the current string that is a prefix of the pattern matters. That is the KMP state, a number from 0 to m-1 (reaching m means the pattern appeared, which is forbidden).",
           "Precompute the transition table <code>go[state][letter]</code> with the prefix function (for a mismatch use <code>go[pi[state-1]][letter]</code>). Then do <code>dp[i+1][go[j][c]] += dp[i][j]</code> for every state and letter, skipping transitions into state m."],
    editorial=["Let <code>m = |pattern|</code> and let <code>pi</code> be its prefix function. After reading any string, the relevant state is the length <code>j</code> of the longest suffix that is a prefix of the pattern. From state <code>j</code> and the letter <code>c</code>: if <code>pattern[j] == c</code> the new state is <code>j + 1</code>; otherwise it is the transition from the border state, <code>go[pi[j-1]][c]</code> (and 0 when <code>j = 0</code>). This table is the KMP automaton and can be built in O(m &middot; k).",
               "Let <code>dp[j]</code> be the number of strings of the current length that end in state <code>j</code> without having reached state <code>m</code>. Start with <code>dp[0] = 1</code>. For every one of the <code>n</code> steps, push each <code>dp[j]</code> along all <code>k</code> letters, dropping the transitions that lead to state <code>m</code>. The answer is the sum of <code>dp</code> after <code>n</code> steps, modulo <code>10<sup>9</sup>+7</code>.",
               "Most letters from a state lead back to state 0, so grouping the letters by target state makes a step cost only the number of distinct targets. In any case the plain version takes O(n &middot; m &middot; k), at most 500 &times; 40 &times; 26 operations here."],
    time="O(m*k + n*m*k)", space="O(m*k)",
    solution='''def countAvoiding(pattern, n, k):
    MOD = 1000000007
    m = len(pattern)
    pi = [0] * m
    t = 0
    for i in range(1, m):
        while t and pattern[i] != pattern[t]:
            t = pi[t - 1]
        if pattern[i] == pattern[t]:
            t += 1
        pi[i] = t
    letters = [chr(97 + c) for c in range(k)]
    go = [[0] * k for _ in range(m + 1)]
    for j in range(m + 1):
        for c, ch in enumerate(letters):
            if j < m and pattern[j] == ch:
                go[j][c] = j + 1
            elif j == 0:
                go[j][c] = 0
            else:
                go[j][c] = go[pi[j - 1]][c]
    # group letters by target state, dropping the forbidden state m
    trans = []
    for j in range(m):
        cnt = {}
        for c in range(k):
            tgt = go[j][c]
            if tgt != m:
                cnt[tgt] = cnt.get(tgt, 0) + 1
        trans.append(list(cnt.items()))
    dp = [0] * m
    dp[0] = 1
    for _ in range(n):
        nd = [0] * m
        for j in range(m):
            v = dp[j]
            if v:
                for tgt, w in trans[j]:
                    nd[tgt] = (nd[tgt] + v * w) % MOD
        dp = nd
    return sum(dp) % MOD
''',
    tests=[["ab", 3, 2], ["aa", 4, 2], ["a", 5, 1], ["a", 5, 2], ["abc", 1, 3], ["abc", 2, 3], ["aba", 6, 2], ["abab", 10, 2],
           ["zz", 3, 26], ["abcabd", 12, 4], ["aaaa", 30, 2], ["abc", 7, 3]],
)
p["tests"].append(["abcabdabcabe", 500, 26])
p["tests"].append(["aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa", 500, 3])
p["tests"].append(["abababababababababababababababababababab", 500, 2])


def b_avoid(pattern, n, k):
    # independent method: count over the last (m-1) characters kept as plain strings
    m = len(pattern)
    letters = [chr(97 + c) for c in range(k)]
    cur = {"": 1}
    for _ in range(n):
        nxt = {}
        for tail, v in cur.items():
            for ch in letters:
                w = tail + ch
                if w.endswith(pattern):
                    continue
                key = w[-(m - 1):] if m > 1 else ""
                nxt[key] = (nxt.get(key, 0) + v) % MOD
        cur = nxt
    return sum(cur.values()) % MOD


def g_avoid(r):
    k = r.randint(1, 3)
    n = r.randint(1, 7 if k == 3 else 9)
    m = r.randint(1, 4)
    pt = "".join(chr(97 + r.randrange(k)) for _ in range(m))
    return [pt, n, k]


def v_avoid(tests):
    for t in tests:
        pt, n, k = t["args"]
        assert 1 <= len(pt) <= 40 and 1 <= n <= 500 and 1 <= k <= 26
        assert _lower(pt) and all(ord(c) - 97 < k for c in pt)
        assert 0 <= t["expected"] < MOD


CHECKS["count-strings-avoiding-pattern"] = (b_avoid, g_avoid, "exact")
VALIDATE["count-strings-avoiding-pattern"] = v_avoid

p = add(
    id="occurrences-with-one-mismatch", title="Occurrences With At Most One Mismatch", diff="Hard", topic=TOPIC, tier="extra",
    fn="countNearMatches", params=[("text", "string"), ("pattern", "string")], ret="int", cmp="exact",
    desc="<p>Count the start indices <code>i</code> for which the window <code>text[i..i+m-1]</code> (where <code>m = |pattern|</code>) differs from <code>pattern</code> in <strong>at most one</strong> position. An exact match counts as well.</p><p>Example: <code>text = \"abcabd\"</code>, <code>pattern = \"abc\"</code>. The windows are <code>\"abc\"</code> (0 differences), <code>\"bca\"</code> (3), <code>\"cab\"</code> (3) and <code>\"abd\"</code> (1), so the answer is <code>2</code>. If <code>pattern</code> is longer than <code>text</code>, the answer is 0.</p>",
    constraints=["1 &le; text.length, pattern.length &le; 8,000", "Both strings consist of lowercase English letters"],
    hints=["Comparing each window with the pattern takes O(n &middot; m). Think about what a window with at most one mismatch looks like: a matching prefix, one wrong character, then a matching suffix.",
           "For every window compute <code>pre</code> = the length of the longest common prefix of the window and the pattern. Z-function of <code>pattern + '#' + text</code> gives this for all windows at once.",
           "Do the same on the reversed strings to get <code>suf</code> = the longest common suffix of the window and the pattern. The window has at most one mismatch exactly when <code>pre + suf &ge; m - 1</code>."],
    editorial=["Let <code>pre[i]</code> be the length of the longest common prefix of <code>pattern</code> and <code>text[i..]</code>, capped at <code>m</code>, and <code>suf[i]</code> the length of the longest common suffix of <code>pattern</code> and <code>text[..i+m-1]</code>. Both come from Z-functions: <code>pre</code> from <code>pattern + '#' + text</code> and <code>suf</code> from the same construction on the reversed strings.",
               "If <code>pre[i] = m</code> the window is an exact match. Otherwise the first mismatch is at offset <code>pre[i]</code>, and the window is acceptable exactly when everything after that offset matches, that is, when the common suffix covers the remaining <code>m - pre[i] - 1</code> characters: <code>suf[i] &ge; m - pre[i] - 1</code>. This is equivalent to the single test <code>pre[i] + suf[i] &ge; m - 1</code> which is also true for exact matches.",
               "Two linear Z-function passes and one scan give O(n + m) time and space. The idea generalises to k mismatches by repeating 'jump over the next common prefix' k times, using a data structure for longest-common-extension queries."],
    time="O(n + m)", space="O(n + m)",
    solution='''def countNearMatches(text, pattern):
    n, m = len(text), len(pattern)
    if m > n:
        return 0

    def zfunc(s):
        L = len(s)
        z = [0] * L
        l = r = 0
        for i in range(1, L):
            if i < r:
                z[i] = min(r - i, z[i - l])
            while i + z[i] < L and s[z[i]] == s[i + z[i]]:
                z[i] += 1
            if i + z[i] > r:
                l, r = i, i + z[i]
        return z

    zf = zfunc(pattern + '#' + text)
    zb = zfunc(pattern[::-1] + '#' + text[::-1])
    count = 0
    for i in range(n - m + 1):
        pre = zf[m + 1 + i]
        end = i + m - 1
        suf = zb[m + 1 + (n - 1 - end)]
        if pre + suf >= m - 1:
            count += 1
    return count
''',
    tests=[["abcabd", "abc"], ["aaaa", "ab"], ["abc", "abcd"], ["a", "b"], ["abab", "ba"], ["aaaaa", "aaa"], ["abcdef", "xbcdex"],
           ["abcabcabc", "abd"], ["xyz", "xyz"], ["ababab", "bbb"], ["abcde", "z"]],
)
_r = rnd(9110)
_t = _rs(_r, 8000, "ab")
p["tests"].append([_t, _t[100:140]])
p["tests"].append(["a" * 8000, "a" * 3999 + "b" + "a" * 3999])
p["tests"].append([_rs(_r, 8000, "abc"), _rs(_r, 12, "abc")])


def b_near(text, pattern):
    n, m = len(text), len(pattern)
    cnt = 0
    for i in range(n - m + 1):
        d = 0
        for j in range(m):
            if text[i + j] != pattern[j]:
                d += 1
        if d <= 1:
            cnt += 1
    return cnt


def g_near(r):
    t = _rs(r, r.randint(1, 14), "ab")
    if r.random() < 0.7 and len(t) > 1:
        i = r.randrange(len(t))
        pt = list(t[i:i + r.randint(1, 6)])
        if r.random() < 0.6:
            pt[r.randrange(len(pt))] = r.choice("ab")
        pt = "".join(pt)
    else:
        pt = _rs(r, r.randint(1, 5), "ab")
    return [t, pt]


def v_near(tests):
    for t in tests:
        a, b = t["args"]
        assert 1 <= len(a) <= 8000 and 1 <= len(b) <= 8000 and _lower(a) and _lower(b)
        assert 0 <= t["expected"] <= len(a)


CHECKS["occurrences-with-one-mismatch"] = (b_near, g_near, "exact")
VALIDATE["occurrences-with-one-mismatch"] = v_near
