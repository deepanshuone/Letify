"""Problems: string algorithms, part B (hashing and suffix ideas). See data/lib.py for the registry."""
from collections import Counter

from lib import add, rnd, CHECKS, VALIDATE, gen_arr  # noqa: F401

TOPIC = "String Algorithms"
LET = "abcdefghijklmnopqrstuvwxyz"


def _rs(r, n, alpha="abc"):
    return "".join(r.choice(alpha) for _ in range(n))


def _lower(s):
    return bool(s) and all("a" <= c <= "z" for c in s)


def _fib(n, a="a", b="b"):
    x, y = a, b
    while len(y) < n:
        x, y = y, y + x
    return y[:n]


def _mutate(r, s, k, alpha="ab"):
    s = list(s)
    for _ in range(k):
        s[r.randrange(len(s))] = r.choice(alpha)
    return "".join(s)


# shared reference helpers, pasted into the solutions that need them
SA_SRC = '''def build_sa(s):
    n = len(s)
    sa = list(range(n))
    rank = [ord(c) for c in s]
    k = 1
    while True:
        key = [(rank[i], rank[i + k] if i + k < n else -1) for i in range(n)]
        sa.sort(key=key.__getitem__)
        new = [0] * n
        for t in range(1, n):
            new[sa[t]] = new[sa[t - 1]] + (key[sa[t - 1]] != key[sa[t]])
        rank = new
        if rank[sa[-1]] == n - 1:
            return sa
        k *= 2


def build_lcp(s, sa):
    n = len(s)
    rank = [0] * n
    for i, p in enumerate(sa):
        rank[p] = i
    lcp = [0] * max(n - 1, 0)
    h = 0
    for i in range(n):
        if rank[i] > 0:
            j = sa[rank[i] - 1]
            while i + h < n and j + h < n and s[i + h] == s[j + h]:
                h += 1
            lcp[rank[i] - 1] = h
            if h:
                h -= 1
        else:
            h = 0
    return lcp
'''


def _all_subs(s):
    return [s[i:j] for i in range(len(s)) for j in range(i + 1, len(s) + 1)]


def _lcp2(a, b):
    h = 0
    while h < len(a) and h < len(b) and a[h] == b[h]:
        h += 1
    return h


# ---------------------------------------------------------------- EASY

p = add(
    id="longest-shared-prefix-between-two-words", title="Longest Shared Prefix Between Two Words", diff="Easy", topic=TOPIC, tier="extra",
    fn="maxSharedPrefix", params=[("words", "string")], ret="int", cmp="exact",
    desc="<p>The string <code>words</code> holds several lowercase words separated by single commas, for example <code>\"flower,flow,flight\"</code>. Choose <strong>two different positions</strong> in this list and look at the longest prefix the two words have in common. Return the largest such length over all pairs of positions.</p><p>The same word may occur more than once in the list; two equal words (at different positions) share their whole length. If no two words share even their first letter, the answer is <code>0</code>.</p><pre>words = \"flower,flow,flight\"  ->  4   (\"flower\" and \"flow\" share \"flow\")\nwords = \"dog,racecar,car\"     ->  0\nwords = \"ab,b,ab\"             ->  2   (the two equal words \"ab\")</pre>",
    constraints=["The list holds between 2 and 3,000 words", "Every word has 1 to 50 lowercase English letters", "The total length of <code>words</code>, commas included, is at most 30,000"],
    hints=["Checking every pair of words and computing their common prefix is correct. How many pairs are there when there are 3,000 words?",
           "Think about where in alphabetical order two words with a long common prefix end up. Words that start with the same long prefix form a contiguous block.",
           "Sort the words. The best pair is always two neighbours in the sorted order, so compare only adjacent words and keep the maximum common prefix length."],
    editorial=["Comparing all pairs costs O(w<sup>2</sup> &middot; L) for w words of length up to L, which is too slow for thousands of words in a larger setting. The key observation is about sorted order: if words a &le; b &le; c are in sorted order, then <code>lcp(a, c) = min(lcp(a, b), lcp(b, c))</code>. So a pair that is not adjacent can never beat the adjacent pairs lying between them.",
               "Therefore split the string on commas, sort the words, and take the maximum of <code>lcp(words[i], words[i+1])</code> over neighbours. Equal words become neighbours and give their full length automatically. Sorting costs O(total length &middot; log w) in the worst case, and the scan costs O(total length). This 'sort, then look at neighbours' trick is the basic idea behind suffix arrays as well."],
    time="O(T log w), T = total length", space="O(T)",
    solution='''def maxSharedPrefix(words):
    ws = sorted(words.split(","))
    best = 0
    for a, b in zip(ws, ws[1:]):
        h = 0
        m = min(len(a), len(b))
        while h < m and a[h] == b[h]:
            h += 1
        best = max(best, h)
    return best
''',
    tests=[["flower,flow,flight"], ["dog,racecar,car"], ["ab,b,ab"], ["a,a"], ["a,b"], ["abc,abd,abe,xyz"], ["zebra,apple,apply,apt"],
           ["same,same,same"], ["aaaa,aaab,aa"], ["interview,internet,interval,internal"], ["x,xy,xyz,xyzw"]],
)
_r = rnd(9201)
_ws = ["".join(_r.choice("ab") for _ in range(_r.randint(5, 12))) for _ in range(2000)]
p["tests"].append([",".join(_ws)])
_ws = ["".join(_r.choice(LET) for _ in range(_r.randint(3, 8))) for _ in range(2500)]
p["tests"].append([",".join(_ws)])
_base = _rs(_r, 40, "abc")
_ws = [_base[:_r.randint(0, 40)] + _rs(_r, 2, "xyz") for _ in range(500)]
_ws = [w for w in _ws if w][:500]
p["tests"].append([",".join(_ws)])


def b_pref(words):
    ws = words.split(",")
    best = 0
    for i in range(len(ws)):
        for j in range(i + 1, len(ws)):
            best = max(best, _lcp2(ws[i], ws[j]))
    return best


def g_pref(r):
    return ",".join(_rs(r, r.randint(1, 5), "abc") for _ in range(r.randint(2, 7)))


def v_pref(tests):
    for t in tests:
        w = t["args"][0]
        ws = w.split(",")
        assert 2 <= len(ws) <= 3000 and len(w) <= 30000
        assert all(1 <= len(x) <= 50 and _lower(x) for x in ws)


CHECKS["longest-shared-prefix-between-two-words"] = (b_pref, lambda r: [g_pref(r)], "exact")
VALIDATE["longest-shared-prefix-between-two-words"] = v_pref

p = add(
    id="substring-equality-queries", title="Substring Equality Queries", diff="Easy", topic=TOPIC, tier="extra",
    fn="substringEquality", params=[("s", "string"), ("queries", "int[][]")], ret="int[]", cmp="exact",
    desc="<p>You are given a string <code>s</code> and a list of <code>queries</code>. Each query is <code>[a, b, len]</code> and asks: are the two blocks of length <code>len</code> starting at index <code>a</code> and at index <code>b</code> (0-indexed) identical, that is, is <code>s[a .. a+len)</code> equal to <code>s[b .. b+len)</code>? The blocks may overlap.</p><p>Return an array with one entry per query: <code>1</code> if the blocks are equal and <code>0</code> otherwise.</p><pre>s = \"abracadabra\"\nqueries = [[0,7,4],[0,3,1],[1,8,3],[1,4,2]]\nresult  = [1,1,1,0]\n(\"abra\"=\"abra\", \"a\"=\"a\", \"bra\"=\"bra\", \"br\" != \"ca\")</pre>",
    constraints=["1 &le; s.length &le; 8,000", "s consists of lowercase English letters", "1 &le; queries.length &le; 4,000", "1 &le; len, 0 &le; a, b and a + len &le; s.length, b + len &le; s.length"],
    hints=["Slicing both blocks and comparing them works, but each query then costs O(len). Can a query be answered in O(1) after preprocessing?",
           "Turn every prefix of <code>s</code> into a number with a polynomial rolling hash: <code>H[i+1] = H[i] * B + code(s[i])</code> modulo a large prime.",
           "The hash of block <code>[a, a+len)</code> is <code>H[a+len] - H[a] * B^len</code> (mod p). Precompute the powers of <code>B</code> and compare the two hashes of every query."],
    editorial=["Preprocess the prefix hashes <code>H</code> and the powers <code>B^k</code> in O(n). The hash of any block is then obtained in O(1) from two prefix values, exactly like a prefix-sum difference but with a multiplication to shift the older part out. Equal blocks always give equal hashes, so a differing hash proves the blocks are different.",
               "Different blocks can collide with tiny probability, so use a large modulus such as 2<sup>61</sup> - 1 (or two moduli together). With a good base the chance of an error is negligible for these input sizes. Total time is O(n + q); a plain slice comparison would be O(q &middot; n) in the worst case, which matters when queries are long and the strings are highly repetitive."],
    time="O(n + q)", space="O(n)",
    solution='''def substringEquality(s, queries):
    MOD = (1 << 61) - 1
    B = 911382323
    n = len(s)
    H = [0] * (n + 1)
    PW = [1] * (n + 1)
    for i, c in enumerate(s):
        H[i + 1] = (H[i] * B + ord(c)) % MOD
        PW[i + 1] = PW[i] * B % MOD

    def get(a, ln):
        return (H[a + ln] - H[a] * PW[ln]) % MOD

    return [1 if get(a, ln) == get(b, ln) else 0 for a, b, ln in queries]
''',
    tests=[["abracadabra", [[0, 7, 4], [0, 3, 1], [1, 8, 3], [1, 4, 2]]], ["a", [[0, 0, 1]]], ["ab", [[0, 1, 1], [0, 0, 2]]],
           ["aaaaa", [[0, 1, 4], [0, 2, 3], [1, 2, 3], [0, 4, 1]]], ["abcabcabc", [[0, 3, 6], [0, 2, 7], [1, 4, 5], [2, 5, 4]]],
           ["abab", [[0, 2, 2], [1, 3, 1], [0, 1, 3]]], ["xyzzyx", [[0, 5, 1], [0, 3, 3], [1, 2, 1], [2, 3, 1]]],
           ["mississippi", [[1, 4, 4], [2, 5, 3], [0, 10, 1], [1, 7, 2], [4, 7, 4]]]],
)
_r = rnd(9202)


def _eq_queries(r, s, q, close):
    n = len(s)
    out = []
    for _ in range(q):
        ln = r.randint(1, max(1, min(n, close)))
        a = r.randint(0, n - ln)
        b = r.randint(0, n - ln)
        out.append([a, b, ln])
    return out


_s = "ab" * 4000
_q = _eq_queries(_r, _s, 1800, 8000)
p["tests"].append([_s, _q])
_s = _mutate(_r, _fib(8000), 3)
_q = _eq_queries(_r, _s, 1800, 5000)
p["tests"].append([_s, _q])
_s = _rs(_r, 6000, "ab")
_q = _eq_queries(_r, _s, 1500, 14)
p["tests"].append([_s, _q])


def b_eq(s, queries):
    return [1 if s[a:a + ln] == s[b:b + ln] else 0 for a, b, ln in queries]


def g_eq(r):
    s = _rs(r, r.randint(1, 10), "ab")
    qs = []
    for _ in range(r.randint(1, 6)):
        ln = r.randint(1, len(s))
        qs.append([r.randint(0, len(s) - ln), r.randint(0, len(s) - ln), ln])
    return [s, qs]


def v_eq(tests):
    for t in tests:
        s, qs = t["args"]
        assert 1 <= len(s) <= 8000 and _lower(s) and 1 <= len(qs) <= 4000
        for a, b, ln in qs:
            assert ln >= 1 and a >= 0 and b >= 0 and a + ln <= len(s) and b + ln <= len(s)
        assert t["expected"] == b_eq(s, qs), "hash collision or wrong answer"


CHECKS["substring-equality-queries"] = (b_eq, g_eq, "exact")
VALIDATE["substring-equality-queries"] = v_eq

# ---------------------------------------------------------------- MEDIUM

p = add(
    id="longest-common-extension-queries", title="Longest Common Extension Queries", diff="Medium", topic=TOPIC, tier="extra",
    fn="commonExtension", params=[("s", "string"), ("queries", "int[][]")], ret="int[]", cmp="exact",
    desc="<p>For two start positions <code>i</code> and <code>j</code> in <code>s</code>, the <em>common extension</em> is the length of the longest common prefix of the two suffixes <code>s[i..]</code> and <code>s[j..]</code>. In other words: how far can you read both suffixes simultaneously before the characters differ or one of the suffixes ends?</p><p>Each query is <code>[i, j]</code>. Return the common extension of every query, in order. If <code>i = j</code>, the answer is simply the length of the suffix <code>n - i</code>.</p><pre>s = \"abracadabra\"\nqueries = [[0,7],[3,5],[1,8],[2,2]]\nresult  = [4,1,3,9]</pre>",
    constraints=["1 &le; s.length &le; 8,000", "s consists of lowercase English letters", "1 &le; queries.length &le; 3,000", "0 &le; i, j &lt; s.length"],
    hints=["Walking along both suffixes until they differ is correct, but a highly repetitive string such as <code>\"ababab...\"</code> makes every query cost O(n).",
           "If the two suffixes agree on their first <code>L</code> characters, they also agree on the first <code>L - 1</code>. That monotonic property allows a binary search on the answer.",
           "Precompute prefix hashes of <code>s</code>. For a query, binary search the largest <code>L &le; n - max(i, j)</code> for which the hashes of <code>s[i..i+L)</code> and <code>s[j..j+L)</code> are equal."],
    editorial=["The predicate 'the first L characters of both suffixes agree' is true for L = 0, stays true up to the answer, and is false afterwards, so the answer is found by binary search over <code>0 .. n - max(i, j)</code>. Each predicate evaluation must be O(1): compare the polynomial hashes of the two blocks, computed from prefix hashes as <code>H[a+L] - H[a] * B^L</code> modulo a large prime.",
               "Preprocessing takes O(n) and each query O(log n), for O(n + q log n) in total. The naive approach is O(q &middot; n) in the worst case. A suffix array with an LCP array and a range-minimum structure answers each query in O(1) after an O(n log n) build, but the hashing solution is much shorter and fast enough here. Handle <code>i = j</code> separately or let the binary search cap it at <code>n - i</code>."],
    time="O(n + q log n)", space="O(n)",
    solution='''def commonExtension(s, queries):
    MOD = (1 << 61) - 1
    B = 911382323
    n = len(s)
    H = [0] * (n + 1)
    PW = [1] * (n + 1)
    for i, c in enumerate(s):
        H[i + 1] = (H[i] * B + ord(c)) % MOD
        PW[i + 1] = PW[i] * B % MOD
    res = []
    for i, j in queries:
        lo, hi = 0, n - max(i, j)
        while lo < hi:
            mid = (lo + hi + 1) // 2
            if (H[i + mid] - H[i] * PW[mid]) % MOD == (H[j + mid] - H[j] * PW[mid]) % MOD:
                lo = mid
            else:
                hi = mid - 1
        res.append(lo)
    return res
''',
    tests=[["abracadabra", [[0, 7], [3, 5], [1, 8], [2, 2]]], ["a", [[0, 0]]], ["aa", [[0, 1], [1, 0], [0, 0]]],
           ["abcd", [[0, 1], [1, 2], [3, 3]]], ["aaaaaa", [[0, 3], [1, 5], [2, 4], [0, 5]]],
           ["abcabcabc", [[0, 3], [0, 6], [1, 4], [2, 3], [3, 6]]], ["banana", [[1, 3], [0, 2], [3, 5], [2, 4]]],
           ["xyxyxz", [[0, 2], [1, 3], [0, 4], [2, 4]]]],
)
_r = rnd(9203)


def _lce_queries(r, n, q):
    return [[r.randrange(n), r.randrange(n)] for _ in range(q)]


_s = "ab" * 4000
p["tests"].append([_s, _lce_queries(_r, 8000, 1500) + [[0, 2], [1, 3], [0, 7998]]])
_s = _mutate(_r, _fib(7000), 2)
p["tests"].append([_s, _lce_queries(_r, 7000, 1500)])
_s = "a" * 3999 + "b" + "a" * 3999
p["tests"].append([_s, _lce_queries(_r, 7999, 1200)])


def b_lce(s, queries):
    return [_lcp2(s[i:], s[j:]) for i, j in queries]


def g_lce(r):
    s = _rs(r, r.randint(1, 12), "ab")
    return [s, [[r.randrange(len(s)), r.randrange(len(s))] for _ in range(r.randint(1, 6))]]


def v_lce(tests):
    for t in tests:
        s, qs = t["args"]
        assert 1 <= len(s) <= 8000 and _lower(s) and 1 <= len(qs) <= 3000
        assert all(0 <= i < len(s) and 0 <= j < len(s) for i, j in qs)
        assert t["expected"] == b_lce(s, qs), "hash collision or wrong answer"


CHECKS["longest-common-extension-queries"] = (b_lce, g_lce, "exact")
VALIDATE["longest-common-extension-queries"] = v_lce

p = add(
    id="suffix-array-of-string", title="Suffix Array of a String", diff="Medium", topic=TOPIC, tier="extra",
    fn="suffixArray", params=[("s", "string")], ret="int[]", cmp="exact",
    desc="<p>Write out all <code>n</code> suffixes of <code>s</code> (the suffix starting at index <code>i</code> is <code>s[i..n)</code>), sort them in ordinary dictionary order (a suffix that is a prefix of another one comes first), and return the <strong>start indices</strong> of the suffixes in that sorted order. This array is called the <em>suffix array</em>.</p><pre>s = \"banana\"\nsuffixes sorted: a(5) ana(3) anana(1) banana(0) na(4) nana(2)\nresult = [5,3,1,0,4,2]</pre><p>All suffixes have different lengths, so they are all different and the order is unique.</p>",
    constraints=["1 &le; s.length &le; 5,000", "s consists of lowercase English letters"],
    hints=["Sorting the suffixes as strings (<code>sorted(range(n), key=lambda i: s[i:])</code>) is correct, but the comparisons and the stored slices cost up to O(n<sup>2</sup>) characters, which hurts on strings like <code>\"aaaa...\"</code> and on larger inputs.",
           "Sort by the first 1 character, then the first 2, then the first 4, then 8 ... Sorting by the first <code>2k</code> characters needs only the order (rank) of the first <code>k</code> characters of the suffix at <code>i</code> and of the suffix at <code>i + k</code>.",
           "Keep <code>rank[i]</code> for the current length k. Sort indices by the pair <code>(rank[i], rank[i+k])</code> (use -1 beyond the end), assign new ranks (equal pairs share a rank), double <code>k</code>, and stop when all ranks are different."],
    editorial=["The prefix-doubling idea: the first <code>2k</code> characters of a suffix are the first <code>k</code> characters of the suffix itself followed by the first <code>k</code> characters of the suffix that starts <code>k</code> positions later. If we know the rank of every suffix by its first <code>k</code> characters, then the pair <code>(rank[i], rank[i+k])</code> is a sorting key for its first <code>2k</code> characters. Equal pairs get equal new ranks.",
               "Each round is one sort, O(n log n), and after at most <code>ceil(log2 n)</code> rounds all ranks are different, so the total is O(n log<sup>2</sup> n) (O(n log n) with radix sort). Rounds can stop early as soon as every rank is unique, which happens after one round on random text but needs all log n rounds on text like <code>\"aaaa\"</code>."],
    time="O(n log^2 n)", space="O(n)",
    solution=SA_SRC + '''

def suffixArray(s):
    return build_sa(s)
''',
    tests=[["banana"], ["a"], ["ab"], ["ba"], ["aa"], ["aaaa"], ["abab"], ["abracadabra"], ["mississippi"], ["zyxwv"], ["abcabcabc"], ["cabbage"]],
)
_r = rnd(9204)
p["tests"].append(["a" * 3000])
p["tests"].append([_rs(_r, 4000, "ab")])
p["tests"].append([_mutate(_r, _fib(5000), 4)])


def b_sa(s):
    return sorted(range(len(s)), key=lambda i: s[i:])


def g_sa(r):
    return [_rs(r, r.randint(1, 12), r.choice(["ab", "abc", "a"]))]


def v_sa(tests):
    for t in tests:
        s = t["args"][0]
        assert 1 <= len(s) <= 5000 and _lower(s)
        sa = t["expected"]
        assert sorted(sa) == list(range(len(s)))
        for x, y in zip(sa, sa[1:]):
            assert s[x:] < s[y:]


CHECKS["suffix-array-of-string"] = (b_sa, g_sa, "exact")
VALIDATE["suffix-array-of-string"] = v_sa

p = add(
    id="lcp-array-of-sorted-suffixes", title="LCP Array of Sorted Suffixes", diff="Medium", topic=TOPIC, tier="extra",
    fn="lcpArray", params=[("s", "string")], ret="int[]", cmp="exact",
    desc="<p>Sort all suffixes of <code>s</code> in dictionary order. For each pair of <strong>neighbouring</strong> suffixes in this sorted list, compute the length of their longest common prefix. Return these <code>n - 1</code> numbers in order: entry <code>k</code> is the common prefix length of the <code>k</code>-th and the <code>(k+1)</code>-th smallest suffix (0-indexed). For a string of length 1 the result is an empty array.</p><pre>s = \"banana\"\nsorted suffixes: a, ana, anana, banana, na, nana\nresult = [1,3,0,0,2]\n(a|ana share \"a\"; ana|anana share \"ana\"; anana|banana share nothing; banana|na nothing; na|nana share \"na\")</pre>",
    constraints=["1 &le; s.length &le; 5,000", "s consists of lowercase English letters"],
    hints=["Build the sorted list of suffixes, then compare each neighbouring pair character by character. That is correct; think about how large the total comparison work can be for <code>\"aaaa...\"</code>.",
           "Process the suffixes in text order (start index 0, 1, 2, ...) instead of sorted order, and remember the LCP value <code>h</code> you found for the previous start index.",
           "Kasai's observation: if suffix <code>i</code> has LCP <code>h</code> with its predecessor in sorted order, then suffix <code>i+1</code> has an LCP of at least <code>h - 1</code> with its own predecessor. So keep <code>h</code> and only decrease it by 1 per step."],
    editorial=["First get the suffix array (here by prefix doubling, O(n log<sup>2</sup> n)), and the inverse array <code>rank[sa[k]] = k</code>. Comparing every neighbouring pair from scratch can cost O(n<sup>2</sup>) in total for text such as all <code>a</code>'s.",
               "Kasai's algorithm visits the start indices in text order. For suffix <code>i</code> with sorted predecessor <code>j</code>, extend <code>h</code> while characters match, record <code>lcp[rank[i]-1] = h</code>, then decrease <code>h</code> by one for suffix <code>i+1</code>. Why this works: removing the first character of both suffixes <code>i</code> and <code>j</code> leaves suffixes <code>i+1</code> and <code>j+1</code> that share <code>h - 1</code> characters and where <code>j+1</code> sorts before <code>i+1</code>, so the real predecessor of <code>i+1</code> shares at least that much. <code>h</code> grows at most 2n times in total, hence O(n) after the suffix array."],
    time="O(n log^2 n)", space="O(n)",
    solution=SA_SRC + '''

def lcpArray(s):
    return build_lcp(s, build_sa(s))
''',
    tests=[["banana"], ["a"], ["ab"], ["aa"], ["aaaa"], ["abab"], ["abracadabra"], ["mississippi"], ["abcdef"], ["abcabcabc"], ["aabaabaab"]],
)
_r = rnd(9205)
p["tests"].append(["a" * 3500])
p["tests"].append([_rs(_r, 4500, "ab")])
p["tests"].append([_mutate(_r, _fib(5000), 4)])


def b_lcp(s):
    sa = sorted(range(len(s)), key=lambda i: s[i:])
    return [_lcp2(s[sa[k]:], s[sa[k + 1]:]) for k in range(len(s) - 1)]


def v_lcp(tests):
    for t in tests:
        s = t["args"][0]
        assert 1 <= len(s) <= 5000 and _lower(s)
        assert len(t["expected"]) == len(s) - 1


CHECKS["lcp-array-of-sorted-suffixes"] = (b_lcp, g_sa, "exact")
VALIDATE["lcp-array-of-sorted-suffixes"] = v_lcp

p = add(
    id="shortest-substring-occurring-once", title="Shortest Substring Occurring Once", diff="Medium", topic=TOPIC, tier="extra",
    fn="shortestUniqueSubstring", params=[("s", "string")], ret="int", cmp="exact",
    desc="<p>Call a substring of <code>s</code> <em>unique</em> if it occurs in <code>s</code> exactly once (counting overlapping occurrences). Return the <strong>length of the shortest unique substring</strong> of <code>s</code>. The whole string is always unique, so an answer exists.</p><pre>s = \"banana\"  ->  1   (\"b\" occurs once)\ns = \"abab\"    ->  2   (\"a\", \"b\", \"ab\" occur twice, \"ba\" once)\ns = \"aaaa\"    ->  4   (\"a\", \"aa\", \"aaa\" repeat, only \"aaaa\" is unique)</pre>",
    constraints=["1 &le; s.length &le; 5,000", "s consists of lowercase English letters"],
    hints=["Counting all substrings of each length with a hash map is correct but costs O(n<sup>2</sup>) substrings, each of up to n characters.",
           "A substring that occurs once is a prefix of exactly one suffix. Which prefixes of a suffix are shared with another suffix?",
           "Sort the suffixes. A suffix is shared with others exactly up to its LCP with its sorted neighbours, so its shortest unique prefix has length <code>max(lcp_left, lcp_right) + 1</code> (valid only if that does not exceed the suffix length). Take the minimum over all suffixes."],
    editorial=["Any substring is a prefix of the suffix where it starts. In the sorted order of suffixes, all suffixes that share a given prefix form a contiguous block, so a prefix of suffix <code>k</code> of length <code>L</code> occurs again elsewhere exactly when <code>L &le; max(lcp[k-1], lcp[k])</code>, where <code>lcp</code> is the neighbour LCP array. Hence the shortest unique prefix of suffix <code>k</code> has length <code>max(lcp[k-1], lcp[k]) + 1</code>, provided that is at most the suffix length (a suffix that is a prefix of its neighbour has none).",
               "The answer is the minimum of these values over all suffixes. Build the suffix array and the LCP array as in the two earlier problems, then one pass finishes: O(n log<sup>2</sup> n) with prefix doubling and O(n) for the scan. An alternative is to binary search the length L and test with rolling hashes whether some window of length L occurs exactly once; this works because a unique substring of length L extends to a unique one of length L + 1."],
    time="O(n log^2 n)", space="O(n)",
    solution=SA_SRC + '''

def shortestUniqueSubstring(s):
    n = len(s)
    sa = build_sa(s)
    lcp = build_lcp(s, sa)
    best = n
    for k in range(n):
        left = lcp[k - 1] if k > 0 else 0
        right = lcp[k] if k < n - 1 else 0
        need = max(left, right) + 1
        if need <= n - sa[k]:
            best = min(best, need)
    return best
''',
    tests=[["banana"], ["a"], ["abab"], ["aaaa"], ["aab"], ["abcabc"], ["abcabd"], ["mississippi"], ["aabbaabb"], ["zzzzzy"], ["abababab"]],
)
_r = rnd(9206)
p["tests"].append(["a" * 4000])
p["tests"].append([_rs(_r, 4500, "ab")])
p["tests"].append([_fib(5000)])
p["tests"].append([_rs(_r, 5000, LET)])


def b_uniq(s):
    n = len(s)
    for L in range(1, n + 1):
        c = Counter(s[i:i + L] for i in range(n - L + 1))
        if 1 in c.values():
            return L


def g_uniq(r):
    return [_rs(r, r.randint(1, 12), r.choice(["ab", "abc", "a"]))]


def v_uniq(tests):
    for t in tests:
        s = t["args"][0]
        assert 1 <= len(s) <= 5000 and _lower(s)


CHECKS["shortest-substring-occurring-once"] = (b_uniq, g_uniq, "exact")
VALIDATE["shortest-substring-occurring-once"] = v_uniq

p = add(
    id="count-substrings-occurring-once", title="Count Substrings Occurring Exactly Once", diff="Medium", topic=TOPIC, tier="extra",
    fn="countUniqueSubstrings", params=[("s", "string")], ret="int", cmp="exact",
    desc="<p>Count the <strong>different strings</strong> that occur in <code>s</code> as a substring <strong>exactly once</strong> (overlapping occurrences count as separate occurrences). A string that occurs twice or more is not counted at all, and each qualifying string is counted a single time.</p><pre>s = \"abab\"  ->  4   (\"aba\", \"bab\", \"abab\", \"ba\")\ns = \"aaaa\"  ->  1   (\"aaaa\"; \"aaa\" occurs twice, and so on)\ns = \"abc\"   ->  6   (every substring is unique)</pre>",
    constraints=["1 &le; s.length &le; 5,000", "s consists of lowercase English letters", "The answer is at most n(n+1)/2 and fits in 32 bits"],
    hints=["Put every substring in a counter and count entries with value 1. How big does the counter get?",
           "A substring that occurs once corresponds to exactly one suffix, and it is a prefix of that suffix that is longer than the suffix's common prefix with the neighbours in sorted order.",
           "With the sorted suffixes and the neighbour LCP array, suffix <code>k</code> of length <code>len</code> contributes <code>max(0, len - max(lcp[k-1], lcp[k]))</code> unique substrings. Sum these contributions."],
    editorial=["A substring that occurs exactly once starts at exactly one position, so it is a prefix of exactly one suffix. Sort the suffixes; the suffixes sharing a prefix are contiguous, so prefix length <code>L</code> of suffix <code>k</code> is shared with another suffix if and only if <code>L &le; max(lcp[k-1], lcp[k])</code>. All longer prefixes of this suffix are unique, and no two different suffixes can produce the same unique string.",
               "So the answer is <code>sum over k of max(0, (n - sa[k]) - max(lcp[k-1], lcp[k]))</code>. The max with 0 handles a suffix that is itself a prefix of a neighbour (then every prefix is repeated). Total time O(n log<sup>2</sup> n) with prefix-doubling suffix array construction, plus O(n) for Kasai's LCP and the sum. Counting with a hash map is O(n<sup>3</sup>) character work."],
    time="O(n log^2 n)", space="O(n)",
    solution=SA_SRC + '''

def countUniqueSubstrings(s):
    n = len(s)
    sa = build_sa(s)
    lcp = build_lcp(s, sa)
    total = 0
    for k in range(n):
        left = lcp[k - 1] if k > 0 else 0
        right = lcp[k] if k < n - 1 else 0
        total += max(0, (n - sa[k]) - max(left, right))
    return total
''',
    tests=[["abab"], ["aaaa"], ["abc"], ["a"], ["aa"], ["banana"], ["abracadabra"], ["mississippi"], ["abcabc"], ["aabaa"], ["xyxyxyx"]],
)
_r = rnd(9207)
p["tests"].append(["a" * 4500])
p["tests"].append([_rs(_r, 4500, "ab")])
p["tests"].append([_mutate(_r, _fib(5000), 5)])


def b_cnt1(s):
    c = Counter(_all_subs(s))
    return sum(1 for v in c.values() if v == 1)


def v_cnt1(tests):
    for t in tests:
        s = t["args"][0]
        assert 1 <= len(s) <= 5000 and _lower(s)
        assert 0 <= t["expected"] <= len(s) * (len(s) + 1) // 2


CHECKS["count-substrings-occurring-once"] = (b_cnt1, g_uniq, "exact")
VALIDATE["count-substrings-occurring-once"] = v_cnt1

p = add(
    id="longest-substring-with-k-occurrences", title="Longest Substring With K Occurrences", diff="Medium", topic=TOPIC, tier="common",
    fn="longestKTimes", params=[("s", "string"), ("k", "int")], ret="int", cmp="exact",
    desc="<p>Return the length of the longest substring of <code>s</code> that occurs <strong>at least <code>k</code> times</strong> in <code>s</code>. Occurrences may overlap (they start at different indices). If no substring occurs <code>k</code> times, return <code>0</code>.</p><pre>s = \"banana\", k = 2  ->  3   (\"ana\" at 1 and 3)\ns = \"banana\", k = 3  ->  1   (\"a\" occurs 3 times)\ns = \"banana\", k = 4  ->  0\ns = \"aaaaa\",  k = 3  ->  3   (\"aaa\" at 0, 1, 2)</pre>",
    constraints=["1 &le; s.length &le; 6,000", "s consists of lowercase English letters", "2 &le; k &le; s.length"],
    hints=["If a substring of length L occurs k times, so does its prefix of length L - 1. So the answer can be searched by length, not by content.",
           "For a fixed length L, count the windows of length L with a hash (or, equivalently, think of the sorted suffixes: windows that are equal are neighbours there). A length works if some window value reaches k occurrences.",
           "With the sorted suffixes and neighbour LCP array, any k consecutive suffixes share a prefix of length equal to the minimum of the k - 1 LCP values between them. The answer is the maximum of these minima over all blocks of k consecutive suffixes; use a sliding-window minimum."],
    editorial=["Suffix-array view: the occurrences of a substring correspond to a contiguous block of the sorted suffixes, all sharing that substring as a prefix. A block of <code>k</code> consecutive suffixes <code>sa[t..t+k-1]</code> shares exactly <code>min(lcp[t..t+k-2])</code> characters, and that prefix therefore occurs at least <code>k</code> times. Conversely any substring with <code>k</code> occurrences is the common prefix of some such block. So the answer is the maximum, over all windows of <code>k - 1</code> consecutive LCP values, of the window minimum, computed in O(n) with a monotone deque.",
               "Building the suffix array by prefix doubling costs O(n log<sup>2</sup> n), Kasai's LCP O(n), and the sliding minimum O(n). An alternative uses binary search on the length L (valid by the prefix observation) and a rolling hash counter for each tested L, giving O(n log n). Setting k = 2 is the classic 'longest repeated substring' problem."],
    time="O(n log^2 n)", space="O(n)",
    solution=SA_SRC + '''

def longestKTimes(s, k):
    from collections import deque
    n = len(s)
    if k > n:
        return 0
    sa = build_sa(s)
    lcp = build_lcp(s, sa)
    w = k - 1
    dq = deque()
    best = 0
    for i, v in enumerate(lcp):
        while dq and lcp[dq[-1]] >= v:
            dq.pop()
        dq.append(i)
        if dq[0] <= i - w:
            dq.popleft()
        if i >= w - 1:
            best = max(best, lcp[dq[0]])
    return best
''',
    tests=[["banana", 2], ["banana", 3], ["banana", 4], ["aaaaa", 3], ["aaaaa", 5], ["abcd", 2], ["aa", 2], ["abab", 2], ["abcabcabc", 3],
           ["mississippi", 2], ["mississippi", 4], ["abracadabra", 2]],
)
_r = rnd(9208)
p["tests"].append(["a" * 5000, 2])
p["tests"].append([_rs(_r, 5500, "ab"), 5])
p["tests"].append([_mutate(_r, _fib(6000), 4), 3])
p["tests"].append([_rs(_r, 6000, "abcd"), 2])


def b_kocc(s, k):
    n = len(s)
    best = 0
    for L in range(1, n + 1):
        c = Counter(s[i:i + L] for i in range(n - L + 1))
        if max(c.values()) >= k:
            best = L
    return best


def g_kocc(r):
    s = _rs(r, r.randint(2, 12), r.choice(["ab", "abc", "a"]))
    return [s, r.randint(2, len(s))]


def v_kocc(tests):
    for t in tests:
        s, k = t["args"]
        assert 1 <= len(s) <= 6000 and _lower(s) and 2 <= k <= len(s), (s[:20], k)


CHECKS["longest-substring-with-k-occurrences"] = (b_kocc, g_kocc, "exact")
VALIDATE["longest-substring-with-k-occurrences"] = v_kocc

# ---------------------------------------------------------------- HARD

p = add(
    id="longest-non-overlapping-repeated-substring", title="Longest Non-Overlapping Repeated Substring", diff="Hard", topic=TOPIC, tier="extra",
    fn="longestNonOverlappingRepeat", params=[("s", "string")], ret="int", cmp="exact",
    desc="<p>Find the length of the longest string <code>t</code> such that <code>t</code> occurs in <code>s</code> at two start positions <code>i &lt; j</code> with <code>i + |t| &le; j</code>, that is, the two occurrences <strong>do not overlap</strong>. If there is no such string, return <code>0</code>.</p><pre>s = \"banana\"  ->  2   (\"an\" at 1 and 3; \"ana\" would overlap itself)\ns = \"aaaa\"    ->  2   (\"aa\" at 0 and 2)\ns = \"abcd\"    ->  0\ns = \"xabcyabcz\" ->  3 (\"abc\" at 1 and 5)</pre>",
    constraints=["1 &le; s.length &le; 6,000", "s consists of lowercase English letters"],
    hints=["The quadratic dynamic program over all pairs of positions is correct but needs O(n<sup>2</sup>) time, too slow when n = 6,000. Look for a property that lets you binary search the length.",
           "If a non-overlapping repeat of length L exists, then its prefixes of length L - 1 also repeat at the same two positions, still without overlap. So the predicate is monotone in L.",
           "For a fixed L, hash every window. Store the <em>earliest</em> start of each hash. A window starting at <code>j</code> whose hash was first seen at <code>i</code> with <code>j - i &ge; L</code> proves length L is feasible. Binary search on L."],
    editorial=["Feasibility of length <code>L</code> is monotone: dropping the last character of a valid pair keeps the two occurrences at the same start positions and, with a shorter length, still non-overlapping. So we binary search <code>L</code> in <code>[0, n/2]</code> (two non-overlapping blocks need 2L &le; n).",
               "To test one L, compute the rolling hashes of all windows of length L. For each hash remember the smallest start index where it appeared. For a window at start <code>j</code>, if its hash was first seen at <code>i</code> and <code>j - i &ge; L</code>, the pair is valid. Using the earliest start is enough: if any earlier-or-equal start works, the earliest one has the largest gap. Each test is O(n), so the total is O(n log n). Hash collisions are astronomically unlikely with a 61-bit prime modulus; a robust version compares the actual substrings on a hit. The alternative O(n<sup>2</sup>) DP uses <code>lcp[i][j]</code> capped at <code>j - i</code>."],
    time="O(n log n)", space="O(n)",
    solution='''def longestNonOverlappingRepeat(s):
    MOD = (1 << 61) - 1
    B = 911382323
    n = len(s)
    H = [0] * (n + 1)
    PW = [1] * (n + 1)
    for i, c in enumerate(s):
        H[i + 1] = (H[i] * B + ord(c)) % MOD
        PW[i + 1] = PW[i] * B % MOD

    def feasible(L):
        first = {}
        for j in range(n - L + 1):
            h = (H[j + L] - H[j] * PW[L]) % MOD
            i = first.setdefault(h, j)
            if j - i >= L:
                return True
        return False

    lo, hi = 0, n // 2
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if feasible(mid):
            lo = mid
        else:
            hi = mid - 1
    return lo
''',
    tests=[["banana"], ["aaaa"], ["abcd"], ["xabcyabcz"], ["a"], ["aa"], ["abab"], ["ababab"], ["aaaaa"], ["abcabcabc"], ["mississippi"], ["abracadabra"]],
)
_r = rnd(9209)
p["tests"].append(["a" * 5001])
p["tests"].append([_rs(_r, 6000, "ab")])
p["tests"].append([_rs(_r, 2900, LET) + _rs(_r, 100, "xyz") + _rs(_r, 2900, LET)])
_x = _rs(_r, 1500, "abcdefgh")
p["tests"].append([_x + _rs(_r, 1000, "stuvw") + _x + _rs(_r, 1000, "mnop")])


def b_nov(s):
    n = len(s)
    best = 0
    for i in range(n):
        for j in range(i + 1, n):
            h = 0
            while j + h < n and s[i + h] == s[j + h] and h < j - i:
                h += 1
            best = max(best, h)
    return best


def g_nov(r):
    return [_rs(r, r.randint(1, 14), r.choice(["ab", "abc", "a"]))]


def v_nov(tests):
    for t in tests:
        s = t["args"][0]
        assert 1 <= len(s) <= 6000 and _lower(s)
        if len(s) <= 400:
            assert t["expected"] == b_nov(s)


CHECKS["longest-non-overlapping-repeated-substring"] = (b_nov, g_nov, "exact")
VALIDATE["longest-non-overlapping-repeated-substring"] = v_nov

p = add(
    id="longest-substring-shared-by-all-words", title="Longest Substring Shared by All Words", diff="Hard", topic=TOPIC, tier="extra",
    fn="longestSharedByAll", params=[("words", "string")], ret="int", cmp="exact",
    desc="<p>The string <code>words</code> holds two or more lowercase words separated by single commas, for example <code>\"abcdef,zbcdey,xbcdz\"</code>. Return the length of the longest string that occurs as a contiguous substring in <strong>every</strong> word of the list. If the words have no letter in common, return <code>0</code>.</p><pre>words = \"abcdef,zbcdey,xbcdz\"  ->  3   (\"bcd\")\nwords = \"abc,def\"             ->  0\nwords = \"aaaa,aa,aaa\"         ->  2   (\"aa\")</pre>",
    constraints=["The list holds between 2 and 10 words", "Every word has at least 1 letter and the total length of <code>words</code> (commas included) is at most 6,000", "Words consist of lowercase English letters"],
    hints=["Take the shortest word and test its substrings, longest first, against all other words. How many substrings is that, and how long does each membership test take?",
           "If a string of length L occurs in every word, then so does each of its substrings, in particular its prefix of length L - 1. So feasibility is monotone in L and you can binary search the length.",
           "For a fixed L, build the set of rolling hashes of all length-L windows of the first word, then intersect it with the set of each other word. If the final set is not empty, L is feasible."],
    editorial=["The predicate 'some string of length L occurs in all words' is monotone in L, so binary search L between 0 and the length of the shortest word. To evaluate it, compute for every word the set of hash values of its windows of length L and intersect the sets (start from the shortest word to keep the working set small). The sets cost O(total length) per test with rolling hashes, so the whole algorithm is O(T log m) for T total characters and m the shortest word length.",
               "Use a large prime modulus, e.g. 2<sup>61</sup> - 1, so that false matches do not occur in practice. The exact alternative is a generalized suffix array over the words joined by distinct separators, followed by a sliding window over the suffix array that must cover all words and maximizes the minimum LCP in the window; hashing with binary search is simpler to write."],
    time="O(T log m)", space="O(T)",
    solution='''def longestSharedByAll(words):
    ws = words.split(",")
    MOD = (1 << 61) - 1
    B = 911382323
    maxlen = max(len(w) for w in ws)
    PW = [1] * (maxlen + 1)
    for i in range(maxlen):
        PW[i + 1] = PW[i] * B % MOD
    pref = []
    for w in ws:
        H = [0] * (len(w) + 1)
        for i, c in enumerate(w):
            H[i + 1] = (H[i] * B + ord(c)) % MOD
        pref.append(H)

    def hashes(idx, L):
        H = pref[idx]
        return {(H[j + L] - H[j] * PW[L]) % MOD for j in range(len(H) - L)}

    def feasible(L):
        common = None
        for idx in range(len(ws)):
            cur = hashes(idx, L)
            common = cur if common is None else common & cur
            if not common:
                return False
        return True

    lo, hi = 0, min(len(w) for w in ws)
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if feasible(mid):
            lo = mid
        else:
            hi = mid - 1
    return lo
''',
    tests=[["abcdef,zbcdey,xbcdz"], ["abc,def"], ["aaaa,aa,aaa"], ["a,a"], ["a,b"], ["abcd,abcd"], ["xabcx,yabcy,zabcz,abc"], ["banana,ananas,bandana"],
           ["interview,view,preview"], ["abab,baba"], ["abcabc,cabcab,bcabca"]],
)
_r = rnd(9210)


def _words_with_core(r, core, cnt, tot_pad, alpha):
    out = []
    for _ in range(cnt):
        a = r.randint(0, tot_pad)
        out.append(_rs(r, a, alpha) + core + _rs(r, tot_pad - a, alpha))
    return out


_core = _rs(_r, 300, "abc")
p["tests"].append([",".join(_words_with_core(_r, _core, 8, 400, "abc"))])
_core = _rs(_r, 40, "ab")
p["tests"].append([",".join(_words_with_core(_r, _core, 10, 500, "ab"))])
p["tests"].append([",".join([_fib(1900), _fib(1500), _mutate(_r, _fib(2000), 5)])])
p["tests"].append([",".join(["a" * 1999, "a" * 1998 + "b", "b" + "a" * 1997])])


def b_shared(words):
    ws = words.split(",")
    base = min(ws, key=len)
    for L in range(len(base), 0, -1):
        for i in range(len(base) - L + 1):
            t = base[i:i + L]
            if all(t in w for w in ws):
                return L
    return 0


def g_shared(r):
    return ",".join(_rs(r, r.randint(1, 9), r.choice(["ab", "abc"])) for _ in range(r.randint(2, 4)))


def v_shared(tests):
    for t in tests:
        w = t["args"][0]
        ws = w.split(",")
        assert 2 <= len(ws) <= 10 and len(w) <= 6000 and all(_lower(x) for x in ws)
        if len(w) <= 600:
            assert t["expected"] == b_shared(w)
        else:
            for L, want in ((t["expected"], True), (t["expected"] + 1, False)):
                common = None
                for x in ws:
                    cur = {x[i:i + L] for i in range(len(x) - L + 1)}
                    common = cur if common is None else common & cur
                assert bool(common) == want, "wrong large answer"


CHECKS["longest-substring-shared-by-all-words"] = (b_shared, lambda r: [g_shared(r)], "exact")
VALIDATE["longest-substring-shared-by-all-words"] = v_shared

p = add(
    id="kth-smallest-distinct-substring", title="K-th Smallest Distinct Substring", diff="Hard", topic=TOPIC, tier="extra",
    fn="kthDistinctSubstring", params=[("s", "string"), ("k", "int")], ret="string", cmp="exact",
    desc="<p>Collect all <strong>different</strong> non-empty substrings of <code>s</code> (a string that appears several times is listed once) and sort them in dictionary order, where a string comes before every longer string that starts with it (so <code>\"a\"</code> &lt; <code>\"ab\"</code> &lt; <code>\"b\"</code>). Return the <code>k</code>-th string of this list, counting from 1.</p><pre>s = \"banana\"\nsorted distinct substrings: a, an, ana, anan, anana, b, ba, ban, bana, banan, banana, n, na, nan, nana\nk = 5  ->  \"anana\"\nk = 8  ->  \"ban\"</pre>",
    constraints=["1 &le; s.length &le; 3,000", "s consists of lowercase English letters", "1 &le; k &le; (number of different substrings of s), which is at most 4,501,500"],
    hints=["Generating and sorting all distinct substrings is correct, but there can be millions of them, each up to n characters long.",
           "In the sorted order of the <em>suffixes</em>, the new distinct substrings contributed by each suffix (those not already prefixes of the previous suffix) appear in dictionary order, one block per suffix.",
           "Suffix <code>sa[t]</code> contributes <code>(n - sa[t]) - lcp[t-1]</code> new substrings: its prefixes longer than the LCP with the previous suffix. Walk through the suffixes subtracting these block sizes from <code>k</code> until <code>k</code> falls into a block, then read the answer off that suffix."],
    editorial=["Sort the suffixes. Every distinct substring is a prefix of its lexicographically smallest suffix-occurrence, namely of the first suffix in sorted order that starts with it. A prefix of suffix <code>sa[t]</code> of length <code>L</code> is new (not seen as a prefix of earlier suffixes) exactly when <code>L &gt; lcp[t-1]</code>, where <code>lcp[t-1]</code> is the common prefix length with the previous suffix. The new prefixes of suffix <code>t</code> are the strings of lengths <code>lcp[t-1]+1 .. n-sa[t]</code>, and in dictionary order they all come after everything contributed by earlier suffixes and before everything contributed by later ones.",
               "So scan <code>t = 0, 1, ...</code> with <code>cnt = (n - sa[t]) - lcp[t-1]</code> (taking <code>lcp[-1] = 0</code>): if <code>k &le; cnt</code> the answer is <code>s[sa[t] : sa[t] + lcp[t-1] + k]</code>, otherwise subtract <code>cnt</code> from <code>k</code> and continue. The suffix array costs O(n log<sup>2</sup> n) and the scan O(n), plus O(n) to slice the answer. The total number of distinct substrings is the sum of all <code>cnt</code> values, which is the standard formula for counting distinct substrings."],
    time="O(n log^2 n)", space="O(n)",
    solution=SA_SRC + '''

def kthDistinctSubstring(s, k):
    n = len(s)
    sa = build_sa(s)
    lcp = build_lcp(s, sa)
    for t in range(n):
        prev = lcp[t - 1] if t > 0 else 0
        cnt = (n - sa[t]) - prev
        if k <= cnt:
            return s[sa[t]:sa[t] + prev + k]
        k -= cnt
    return ""
''',
    tests=[["banana", 5], ["banana", 8], ["banana", 1], ["banana", 15], ["a", 1], ["aaa", 2], ["ab", 3], ["abab", 4], ["abracadabra", 20], ["zyx", 6], ["mississippi", 31], ["aabaa", 7]],
)
_r = rnd(9211)


def _nd(s):
    sa = sorted(range(len(s)), key=lambda i: s[i:])
    return len(s) * (len(s) + 1) // 2 - sum(_lcp2(s[sa[q]:], s[sa[q + 1]:]) for q in range(len(s) - 1))


_s = _rs(_r, 3000, "ab")
p["tests"].append([_s, _nd(_s) - 5000])
_s2 = _mutate(_r, _fib(3000), 3)
p["tests"].append([_s2, _nd(_s2) // 3])
_s3 = "a" * 2800
p["tests"].append([_s3, 2000])
_s4 = _rs(_r, 2500, LET)
p["tests"].append([_s4, _nd(_s4) - 17])


def b_kth(s, k):
    return sorted(set(_all_subs(s)))[k - 1]


def g_kth(r):
    s = _rs(r, r.randint(1, 9), r.choice(["ab", "abc", "a"]))
    return [s, r.randint(1, len(set(_all_subs(s))))]


def v_kth(tests):
    for t in tests:
        s, k = t["args"]
        assert 1 <= len(s) <= 3000 and _lower(s)
        total = 0
        if len(s) <= 40:
            total = len(set(_all_subs(s)))
        else:
            # distinct count via the same formula, computed independently with suffix sorting
            sa = sorted(range(len(s)), key=lambda i: s[i:])
            total = len(s) * (len(s) + 1) // 2 - sum(_lcp2(s[sa[q]:], s[sa[q + 1]:]) for q in range(len(s) - 1))
        assert 1 <= k <= total, (s[:20], k, total)
        assert t["expected"] and t["expected"] in s


CHECKS["kth-smallest-distinct-substring"] = (b_kth, g_kth, "exact")
VALIDATE["kth-smallest-distinct-substring"] = v_kth
