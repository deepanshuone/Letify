"""Problems: strings, well-known interview classics. See data/lib.py for the registry."""
from collections import Counter, deque  # noqa: F401

from lib import add, rnd, CHECKS, VALIDATE, gen_arr  # noqa: F401

TOPIC = "Strings"
LET = "abcdefghijklmnopqrstuvwxyz"


def _rs(r, n, alpha=LET):
    return "".join(r.choice(alpha) for _ in range(n))


def _lower(s):
    return all("a" <= c <= "z" for c in s)


def _wordlist_ok(s, lo=1, hi=10 ** 9):
    ws = s.split(",")
    return all(lo <= len(w) <= hi and _lower(w) for w in ws)


# ---------------------------------------------------------------- EASY

p = add(
    id="common-prefix-length-of-words", tier="common", title="Common Prefix Length of Words", diff="Easy", topic=TOPIC,
    fn="commonPrefixLength", params=[("words", "string")], ret="int", cmp="exact",
    desc="<p>The string <code>words</code> holds one or more non-empty words separated by single commas, for example <code>\"flower,flow,flight\"</code>.</p><p>Return the length of the longest string that is a prefix of <strong>every</strong> word. If the words share no first letter, return <code>0</code>.</p><pre>words = \"flower,flow,flight\"   -> 2   (\"fl\")\nwords = \"dog,racecar,car\"     -> 0\nwords = \"alone\"               -> 5   (a single word is its own prefix)</pre>",
    constraints=["1 &le; words.length &le; 12,000 (commas included)", "Each word has at least one letter", "Words consist of lowercase English letters"],
    hints=["Take the first word as a candidate prefix and compare it with the other words, one position at a time.",
           "You can scan column by column: at position <code>i</code>, every word must have a letter there and it must equal the first word's letter at <code>i</code>. Stop at the first column that fails.",
           "A shortcut: the common prefix of all words is the common prefix of the alphabetically smallest and the alphabetically largest word, because every other word sorts between them."],
    editorial=["Vertical scanning is the classic approach. Let <code>first</code> be the first word. For column <code>i = 0, 1, ...</code> check that every other word is long enough and has the same letter as <code>first[i]</code>. The first column where this fails (or where some word ends) is the answer. The work is at most the total number of letters, so O(total length).",
               "A neat alternative: in sorted order, all words lie between the smallest and the largest word, so any prefix shared by those two is shared by all words in between. Finding the min and max costs one pass, and comparing the two costs at most the shortest length. Horizontal scanning (shrinking a running prefix word after word) works equally well."],
    time="O(total length)", space="O(1)",
    solution='''def commonPrefixLength(words):
    ws = words.split(",")
    lo, hi = min(ws), max(ws)
    i = 0
    while i < len(lo) and i < len(hi) and lo[i] == hi[i]:
        i += 1
    return i
''',
    tests=[["flower,flow,flight"], ["dog,racecar,car"], ["alone"], ["same,same,same"], ["a,a"], ["ab,abc,abcd"], ["abcd,abc,ab"],
           ["interview,internet,interval,internal"], ["x,y"], ["prefix,pre,prelude,prehistoric"], ["abc,abd,abe,ab"], ["zebra,apple"],
           ["aaaa,aaa,aa,a"]],
)
_r = rnd(8201)
_pre = _rs(_r, 120, "abc")
_ws = [_pre + _rs(_r, _r.randint(1, 30), "abc") for _ in range(58)] + [_pre + "a", _pre + "b"]
_r.shuffle(_ws)
p["tests"].append([",".join(_ws)])
p["tests"].append([",".join("a" * _r.randint(1, 3) for _ in range(3000))])
_pre = _rs(_r, 200, LET)
p["tests"].append([",".join([_pre] * 40)])
p["tests"].append([",".join([_pre[:150] + "x" + _rs(_r, 20)] * 20 + [_pre[:150] + "y"])])


def b_cpl(words):
    ws = words.split(",")
    best = 0
    for L in range(1, min(len(w) for w in ws) + 1):
        if all(w[:L] == ws[0][:L] for w in ws):
            best = L
    return best


def g_cpl(r):
    pre = _rs(r, r.randint(0, 4), "ab")
    return [",".join(pre + _rs(r, r.randint(1 if not pre else 0, 4), "ab") for _ in range(r.randint(1, 5)))]


def v_cpl(tests):
    for t in tests:
        w = t["args"][0]
        assert 1 <= len(w) <= 12000 and _wordlist_ok(w)
        assert t["expected"] == b_cpl(w) if len(w) < 2000 else True


CHECKS["common-prefix-length-of-words"] = (b_cpl, g_cpl, "exact")
VALIDATE["common-prefix-length-of-words"] = v_cpl

p = add(
    id="words-sorted-in-alien-order", tier="common", title="Words Sorted in Alien Order", diff="Easy", topic=TOPIC,
    fn="isAlienSorted", params=[("words", "string"), ("order", "string")], ret="bool", cmp="exact",
    desc="<p>An alien language uses the lowercase English letters, but in a different alphabetical order. The string <code>order</code> lists all 26 letters from the alien-smallest to the alien-largest.</p><p>The string <code>words</code> contains words separated by single commas. Return <code>true</code> if the words appear in non-decreasing order under the alien alphabet, otherwise <code>false</code>. Words are compared like in a dictionary: find the first position where they differ and compare those two letters by their place in <code>order</code>; if one word is a prefix of the other, the shorter one is smaller. Equal neighbours are allowed.</p><pre>words = \"hello,leetcode\", order = \"hlabcdefgijkmnopqrstuvwxyz\"  -> true   (h comes before l)\nwords = \"word,world,row\",  order = \"worldabcefghijkmnpqstuvxyz\"  -> false  (\"world\" has l at index 3, \"word\" has d; d is after l)\nwords = \"apple,app\",       order = \"abcdefghijklmnopqrstuvwxyz\"  -> false  (\"app\" is a prefix of \"apple\" so it must come first)</pre>",
    constraints=["1 &le; number of words &le; 2,000", "1 &le; words[i].length &le; 20", "order is a permutation of the 26 lowercase letters", "words and order consist of lowercase English letters (plus the separating commas)"],
    hints=["It is enough to check that every pair of <em>neighbouring</em> words is in order. Why does sortedness of neighbours imply sortedness of all?",
           "Build a lookup <code>rank[letter]</code> from <code>order</code> so you can compare two letters in O(1).",
           "For a neighbouring pair, scan to the first differing position and compare ranks. If there is no differing position within the shorter word, the first word must not be longer than the second."],
    editorial=["The relation 'comes before or equal in the alien dictionary' is transitive, so a list is sorted exactly when each adjacent pair is. For each adjacent pair <code>(a, b)</code> walk along the letters until the first mismatch: if <code>rank[a[k]] &gt; rank[b[k]]</code> the list is not sorted, if smaller the pair is fine. When no mismatch is found within the length of the shorter word, the pair is fine only if <code>len(a) &le; len(b)</code> (a longer word cannot come before its own prefix).",
               "Building the rank table is O(26) and every adjacent comparison costs at most the word length, so the total is O(total number of letters). A common alternative is to translate every word into ordinary letters using the order (mapping the i-th alien letter to the i-th English letter), after which the list is sorted if and only if it equals its own sorted copy."],
    time="O(total length)", space="O(1)",
    solution='''def isAlienSorted(words, order):
    rank = {c: i for i, c in enumerate(order)}
    ws = words.split(",")
    for a, b in zip(ws, ws[1:]):
        for x, y in zip(a, b):
            if x != y:
                if rank[x] > rank[y]:
                    return False
                break
        else:
            if len(a) > len(b):
                return False
    return True
''',
    tests=[["hello,leetcode", "hlabcdefgijkmnopqrstuvwxyz"], ["word,world,row", "worldabcefghijkmnpqstuvxyz"],
           ["apple,app", LET], ["app,apple", LET], ["solo", "zyxwvutsrqponmlkjihgfedcba"], ["cab,cab", "bcadefghijklmnopqrstuvwxyz"],
           ["ba,ab", "bacdefghijklmnopqrstuvwxyz"], ["ba,ab", LET], ["b,a,c", "bacdefghijklmnopqrstuvwxyz"],
           ["z,y,x,w", "zyxwvutsrqponmlkjihgfedcba"], ["abc,abd,abe,b", "abcdefghijklmnopqrstuvwxyz"],
           ["kite,kit,kitten", "kitenabcdfghjlmopqrsuvwxyz"]],
)
_r = rnd(8203)


def _alien_case(r, n, wl, alpha, ordr, sorted_ok):
    ws = [_rs(r, r.randint(1, wl), alpha) for _ in range(n)]
    ws.sort(key=lambda w: [ordr.index(c) for c in w])
    if not sorted_ok:
        # swap two neighbours that are different, so the list is certainly out of order
        ks = [k for k in range(1, n) if ws[k] != ws[k - 1]]
        k = r.choice(ks)
        ws[k - 1], ws[k] = ws[k], ws[k - 1]
    return ",".join(ws)


_ord = list(LET)
_r.shuffle(_ord)
_ord = "".join(_ord)
p["tests"].append([_alien_case(_r, 1500, 6, "abc", _ord, True), _ord])
p["tests"].append([_alien_case(_r, 1500, 6, "abc", _ord, False), _ord])
p["tests"].append([",".join(["a" * k for k in range(1, 21)] * 90), LET])
p["tests"].append([",".join(["a" * k for k in range(1, 21)] * 60 + ["a" * 19]), LET])


def b_alien(words, order):
    tr = str.maketrans(order, LET)
    ws = [w.translate(tr) for w in words.split(",")]
    return ws == sorted(ws)


def g_alien(r):
    o = list(LET)
    r.shuffle(o)
    o = "".join(o)
    alpha = "".join(r.sample(LET, 3))
    ws = [_rs(r, r.randint(1, 4), alpha) for _ in range(r.randint(1, 6))]
    if r.random() < 0.6:
        ws.sort(key=lambda w: [o.index(c) for c in w])
    return [",".join(ws), o]


def v_alien(tests):
    for t in tests:
        w, o = t["args"]
        ws = w.split(",")
        assert 1 <= len(ws) <= 2000 and _wordlist_ok(w, 1, 20)
        assert sorted(o) == list(LET)
    assert any(t["expected"] for t in tests) and not all(t["expected"] for t in tests)


CHECKS["words-sorted-in-alien-order"] = (b_alien, g_alien, "exact")
VALIDATE["words-sorted-in-alien-order"] = v_alien

# ---------------------------------------------------------------- MEDIUM

p = add(
    id="word-break-segmentation", tier="must", title="Word Break", diff="Medium", topic=TOPIC,
    fn="canSegment", params=[("s", "string"), ("words", "string")], ret="bool", cmp="exact",
    desc="<p>You are given a text <code>s</code> and a dictionary. The dictionary is passed as one string <code>words</code> that lists distinct words separated by single commas.</p><p>Return <code>true</code> if <code>s</code> can be cut into one or more consecutive pieces so that every piece is a dictionary word. A word may be used any number of times (or not at all).</p><pre>s = \"applepenapple\", words = \"apple,pen\"             -> true   (apple + pen + apple)\ns = \"catsandog\",     words = \"cats,dog,sand,and,cat\" -> false\ns = \"aaaaaaa\",       words = \"aaaa,aaa\"              -> true   (aaaa + aaa)</pre>",
    constraints=["1 &le; s.length &le; 3,000", "1 &le; number of words &le; 500 and 1 &le; words[i].length &le; 30", "The whole <code>words</code> string has at most 5,000 characters", "s and the words consist of lowercase English letters"],
    hints=["A greedy choice (always take the longest or shortest word) fails: with <code>s = \"aaaaaaa\"</code> and words <code>aaaa, aaa</code> you must plan ahead. Trying every cut recursively is correct but exponential.",
           "Define <code>ok[i]</code> = 'the first <code>i</code> letters of <code>s</code> can be segmented'. The empty prefix is segmentable: <code>ok[0] = true</code>.",
           "<code>ok[i]</code> is true if there is a cut <code>j &lt; i</code> with <code>ok[j]</code> true and <code>s[j:i]</code> a dictionary word. Store the words in a set and only try piece lengths that occur in the dictionary."],
    editorial=["This is a prefix DP. Let <code>ok[i]</code> be true when <code>s[0:i]</code> can be split into dictionary words, with <code>ok[0] = true</code>. For each end position <code>i</code>, look for a last piece <code>s[j:i]</code> that is a word such that <code>ok[j]</code> holds. The answer is <code>ok[n]</code>.",
               "Putting words in a hash set makes each membership test O(piece length). Only the distinct word lengths need to be tried as piece lengths, and there are at most 30 of them, so the running time is about O(n &middot; (number of distinct lengths) &middot; maxLen) instead of O(n&sup2;). Top-down recursion with memoisation on the start index is equivalent. A trie over the dictionary can replace the set and walks forward from each reachable position."],
    time="O(n * L * W) with L distinct word lengths, W max word length", space="O(n + total dictionary size)",
    solution='''def canSegment(s, words):
    ws = set(words.split(","))
    lens = sorted({len(w) for w in ws})
    n = len(s)
    ok = [False] * (n + 1)
    ok[0] = True
    for i in range(1, n + 1):
        for L in lens:
            if L > i:
                break
            if ok[i - L] and s[i - L:i] in ws:
                ok[i] = True
                break
    return ok[n]
''',
    tests=[["applepenapple", "apple,pen"], ["catsandog", "cats,dog,sand,and,cat"], ["aaaaaaa", "aaaa,aaa"], ["a", "a"], ["a", "b"],
           ["abcd", "a,abc,b,cd"], ["leetcode", "leet,code"], ["cars", "car,ca,rs"], ["aaab", "a,aa,aaa"], ["abab", "ab,ba"],
           ["bb", "a,b,bbb,bbbb"], ["xyzxyz", "xy,z,xyzx"]],
)
_r = rnd(8204)
p["tests"].append(["a" * 2999 + "b", ",".join("a" * k for k in range(1, 31))])
p["tests"].append(["a" * 3000, "a" * 29 + "," + "a" * 30])
_d = sorted({_rs(_r, _r.randint(1, 12), "abc") for _ in range(400)})
_s = "".join(_r.choice(_d) for _ in range(500))[:3000]
p["tests"].append([_s, ",".join(_d)])
p["tests"].append([_s[:-1] + ("a" if _s[-1] != "a" else "d"), ",".join(_d)])


def b_wb(s, words):
    ws = words.split(",")

    def go(i):
        if i == len(s):
            return True
        return any(s.startswith(w, i) and go(i + len(w)) for w in ws)
    return go(0)


def g_wb(r):
    alpha = "ab"
    ws = sorted({_rs(r, r.randint(1, 4), alpha) for _ in range(r.randint(1, 4))})
    if r.random() < 0.6:
        s = "".join(r.choice(ws) for _ in range(r.randint(1, 4)))
        if r.random() < 0.3:
            k = r.randrange(len(s))
            s = s[:k] + r.choice(alpha) + s[k + 1:]
    else:
        s = _rs(r, r.randint(1, 10), alpha)
    return [s, ",".join(ws)]


def v_wb(tests):
    for t in tests:
        s, w = t["args"]
        ws = w.split(",")
        assert 1 <= len(s) <= 3000 and _lower(s)
        assert 1 <= len(ws) <= 500 and len(w) <= 5000 and len(set(ws)) == len(ws) and _wordlist_ok(w, 1, 30)
    assert any(t["expected"] for t in tests) and not all(t["expected"] for t in tests)


CHECKS["word-break-segmentation"] = (b_wb, g_wb, "exact")
VALIDATE["word-break-segmentation"] = v_wb

p = add(
    id="longest-string-chain", tier="common", title="Longest Word Chain", diff="Medium", topic=TOPIC,
    fn="longestStringChain", params=[("words", "string")], ret="int", cmp="exact",
    desc="<p>The string <code>words</code> holds distinct lowercase words separated by single commas.</p><p>Word <code>a</code> is a <em>predecessor</em> of word <code>b</code> if you can obtain <code>b</code> by inserting exactly one letter anywhere into <code>a</code> without reordering its other letters (for example <code>\"bda\"</code> is a predecessor of <code>\"bdca\"</code>). A <em>chain</em> is a sequence of words from the list in which every word is a predecessor of the next one; a single word is a chain of length 1.</p><p>Return the length of the longest chain that can be built from the given words.</p><pre>words = \"a,b,ba,bca,bda,bdca\"          -> 4   (a, ba, bda, bdca)\nwords = \"xbc,pcxbcf,xb,cxbc,pcxbc\"     -> 5   (xb, xbc, cxbc, pcxbc, pcxbcf)\nwords = \"abcd,dbqca\"                  -> 1</pre>",
    constraints=["1 &le; number of words &le; 1,000", "1 &le; words[i].length &le; 16", "All words are distinct and consist of lowercase English letters"],
    hints=["A predecessor is exactly one letter shorter, so a chain strictly increases the length by one at every step. Process words from short to long.",
           "Let <code>best[w]</code> be the longest chain that ends with word <code>w</code>. To compute it you need the best chain ending at some word that is <code>w</code> with one letter removed.",
           "For each word, try deleting each of its letters in turn (at most 16 candidates); if the result is in the dictionary, take <code>best[w] = max(best[w], best[candidate] + 1)</code>. Words sorted by length guarantee the candidates are already computed."],
    editorial=["Sort the words by length. Keep a dictionary <code>best</code> mapping each processed word to the length of the longest chain ending in it. For a word <code>w</code>, the previous word in an optimal chain must be <code>w</code> with one letter deleted, so there are only <code>len(w)</code> candidates, each looked up in the dictionary in O(len) time. Set <code>best[w] = 1 + max(best[c])</code> over the candidates that exist (or 1 if none). The answer is the largest value in <code>best</code>.",
               "This avoids comparing every pair of words with a two-pointer subsequence test, which would cost O(n&sup2; &middot; L). The deletion trick gives O(n &middot; L&sup2;) total, about 250,000 character operations here. Because a predecessor is always strictly shorter, there are no cycles and a single pass in length order is enough."],
    time="O(n * L^2)", space="O(n * L)",
    solution='''def longestStringChain(words):
    ws = sorted(words.split(","), key=len)
    best = {}
    ans = 1
    for w in ws:
        cur = 1
        for i in range(len(w)):
            c = w[:i] + w[i + 1:]
            if c in best and best[c] + 1 > cur:
                cur = best[c] + 1
        best[w] = cur
        if cur > ans:
            ans = cur
    return ans
''',
    tests=[["a,b,ba,bca,bda,bdca"], ["xbc,pcxbcf,xb,cxbc,pcxbc"], ["abcd,dbqca"], ["a"], ["a,b,c"], ["ab,ba"], ["a,ab,abc,abcd,abcde"],
           ["abcde,abcd,abc,ab,a"], ["a,ac,abc,bc,abcd"], ["ab,b,abb,bab,babb"], ["abc,bca,ab,ca,a,c"], ["z,zz,zzz,zzzz,azzzz,yyyy"]],
)
_r = rnd(8205)


def _chain_words(r, n, chain_len):
    base = _rs(r, 16, "abc")
    ws = {base}
    cur = base
    for _ in range(chain_len - 1):
        k = r.randrange(len(cur))
        cur = cur[:k] + cur[k + 1:]
        ws.add(cur)
    while len(ws) < n:
        ws.add(_rs(r, r.randint(1, 16), "abc"))
    ws = sorted(ws)
    r.shuffle(ws)
    return ws


p["tests"].append([",".join(_chain_words(_r, 1000, 16))])
p["tests"].append([",".join(_chain_words(_r, 1000, 9))])
_all = sorted({_rs(_r, _r.randint(4, 16), LET) for _ in range(1000)})
_r.shuffle(_all)
p["tests"].append([",".join(_all)])


def b_chain(words):
    ws = words.split(",")

    def is_pred(a, b):
        if len(b) != len(a) + 1:
            return False
        i = 0
        for ch in b:
            if i < len(a) and a[i] == ch:
                i += 1
        return i == len(a)

    def go(w):
        return 1 + max([go(x) for x in ws if is_pred(w, x)] + [0])
    return max(go(w) for w in ws)


def g_chain(r):
    ws = set()
    for _ in range(r.randint(1, 7)):
        ws.add(_rs(r, r.randint(1, 4), "abc"))
    return [",".join(sorted(ws))]


def v_chain(tests):
    for t in tests:
        w = t["args"][0]
        ws = w.split(",")
        assert 1 <= len(ws) <= 1000 and len(set(ws)) == len(ws) and _wordlist_ok(w, 1, 16)
        if len(ws) <= 12:
            assert t["expected"] == b_chain(w)


CHECKS["longest-string-chain"] = (b_chain, g_chain, "exact")
VALIDATE["longest-string-chain"] = v_chain

p = add(
    id="smallest-string-with-swaps", tier="common", title="Smallest String With Allowed Swaps", diff="Medium", topic=TOPIC,
    fn="smallestStringWithSwaps", params=[("s", "string"), ("pairs", "int[][]")], ret="string", cmp="exact",
    desc="<p>You are given a string <code>s</code> and a list <code>pairs</code> of index pairs <code>[a, b]</code> (0-indexed). For every listed pair you may swap the letters at positions <code>a</code> and <code>b</code>, as many times as you like, in any order, and pairs may be used repeatedly.</p><p>Return the lexicographically smallest string that can be produced.</p><pre>s = \"dcab\", pairs = [[0,3],[1,2]]         -> \"bacd\"   (swap 0&#8596;3 to get \"bcad\", swap 1&#8596;2 to get \"bacd\")\ns = \"dcab\", pairs = [[0,3],[1,2],[0,2]]   -> \"abcd\"   (all four positions are linked)\ns = \"cba\",  pairs = [[0,1],[1,2]]         -> \"abc\"</pre>",
    constraints=["1 &le; s.length &le; 3,000", "0 &le; pairs.length &le; 3,000", "pairs[i] = [a, b] with 0 &le; a, b &lt; s.length", "s consists of lowercase English letters"],
    hints=["If you can swap positions 0&ndash;1 and 1&ndash;2, can you also bring any letter of those three positions to any other of them?",
           "Positions connected through chains of allowed swaps form a group, and inside a group the letters can be arranged in <em>any</em> order. Think of the pairs as edges of a graph on the positions.",
           "Find the groups (union-find or DFS). For each group, sort its letters and sort its positions, then write the smallest letter at the smallest position, and so on."],
    editorial=["Adjacent-style swapping along a chain of pairs lets you realise any permutation inside a connected component of the graph whose vertices are the positions and whose edges are the pairs (just like bubble sort moves letters step by step along a path). Letters can never leave their component. So the best string places, within each component, the sorted letters on the sorted positions, which makes every position as small as possible from left to right.",
               "Implementation: union-find over positions to label components, bucket positions by their root (positions are naturally collected in increasing order), sort each bucket's letters, and write them back. Time is O((n + m) &alpha;(n) + n log n) and space O(n)."],
    time="O((n + m) * alpha(n) + n log n)", space="O(n)",
    solution='''def smallestStringWithSwaps(s, pairs):
    n = len(s)
    parent = list(range(n))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for a, b in pairs:
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb
    groups = {}
    for i in range(n):
        groups.setdefault(find(i), []).append(i)
    res = list(s)
    for pos in groups.values():
        letters = sorted(s[i] for i in pos)
        for i, ch in zip(pos, letters):
            res[i] = ch
    return "".join(res)
''',
    tests=[["dcab", [[0, 3], [1, 2]]], ["dcab", [[0, 3], [1, 2], [0, 2]]], ["cba", [[0, 1], [1, 2]]], ["a", []], ["ba", []],
           ["ba", [[0, 0]]], ["ba", [[1, 0]]], ["zyxwv", [[0, 4], [4, 0]]], ["dcba", [[0, 1], [2, 3]]], ["bca", [[0, 2], [1, 2]]],
           ["cabbage", [[6, 0], [1, 5], [2, 3]]], ["aaabbb", [[0, 5], [1, 4]]]],
)
_r = rnd(8206)
_s = _rs(_r, 3000)
p["tests"].append([_s, [[_r.randrange(3000), _r.randrange(3000)] for _ in range(3000)]])
p["tests"].append([_s, [[i, i + 1] for i in range(0, 2999, 3)]])
p["tests"].append([_s, [[_r.randrange(3000), _r.randrange(3000)] for _ in range(1300)]])


def b_swaps(s, pairs):
    seen = {s}
    q = deque([s])
    while q:
        cur = q.popleft()
        for a, b in pairs:
            x = list(cur)
            x[a], x[b] = x[b], x[a]
            x = "".join(x)
            if x not in seen:
                seen.add(x)
                q.append(x)
    return min(seen)


def g_swaps(r):
    n = r.randint(1, 6)
    s = _rs(r, n, "abcd")
    return [s, [[r.randrange(n), r.randrange(n)] for _ in range(r.randint(0, 5))]]


def v_swaps(tests):
    for t in tests:
        s, pr = t["args"]
        assert 1 <= len(s) <= 3000 and _lower(s) and len(pr) <= 3000
        assert all(len(x) == 2 and 0 <= x[0] < len(s) and 0 <= x[1] < len(s) for x in pr)
        assert len(t["expected"]) == len(s) and sorted(t["expected"]) == sorted(s)


CHECKS["smallest-string-with-swaps"] = (b_swaps, g_swaps, "exact")
VALIDATE["smallest-string-with-swaps"] = v_swaps


p = add(
    id="minimum-frogs-croaking", tier="extra", title="Minimum Number of Croaking Frogs", diff="Medium", topic=TOPIC,
    fn="minNumberOfFrogs", params=[("croak", "string")], ret="int", cmp="exact",
    desc="<p>Several frogs sit by a pond. A frog that croaks says the word <code>\"croak\"</code> by emitting its letters <code>c, r, o, a, k</code> one after another, in this order, with no pause. A frog can only start a new croak after it finished the previous one. Different frogs may croak at the same time, so their letters interleave in one recording.</p><p>The string <code>croak</code> is the whole recording. Return the minimum number of different frogs needed to produce it, or <code>-1</code> if the recording cannot be a mixture of complete croaks (a letter is out of order or some croak is unfinished).</p><pre>\"croakcroak\"  -> 1   (one frog croaks twice)\n\"crcoakroak\"  -> 2   (two overlapping croaks)\n\"croakcrook\"  -> -1  (the second word is broken)\n\"croa\"        -> -1  (unfinished croak)</pre>",
    constraints=["1 &le; croak.length &le; 20,000", "croak consists only of the letters c, r, o, a and k"],
    hints=["Whenever a letter other than <code>c</code> arrives it must continue some frog that is currently waiting for exactly that letter. A <code>c</code> starts a croak.",
           "Keep a counter for how many frogs are in each stage: just said <code>c</code>, said <code>cr</code>, said <code>cro</code>, said <code>croa</code>. A letter moves one frog from the stage before to the next, and the recording is invalid if no frog is in the stage before.",
           "The number of frogs needed is the largest number of frogs that are mid-croak at the same time. Frogs that said <code>k</code> are free again. At the end no frog may be mid-croak."],
    editorial=["Frogs are interchangeable, so only the number of frogs in each stage matters. Let <code>cnt[i]</code> be the number of frogs that have said the first <code>i + 1</code> letters of <code>croak</code> and now wait for the next letter (<code>i = 0..3</code>). On <code>c</code> a croak begins: <code>cnt[0]</code> and the number of busy frogs go up. On <code>r</code>, <code>o</code>, <code>a</code> one frog moves from stage <code>i - 1</code> to stage <code>i</code>; if no frog is in the stage before, the letter has no owner and the recording is invalid. On <code>k</code> a frog leaves stage 3 and becomes free, which lowers the number of busy frogs.",
               "A frog that has just finished can start the next croak, so the number of frogs needed is the maximum number of simultaneously busy frogs. If someone is still busy after the last letter, a croak is unfinished and the answer is -1. This is one pass with four counters: O(n) time and O(1) space."],
    time="O(n)", space="O(1)",
    solution='''def minNumberOfFrogs(croak):
    cnt = [0, 0, 0, 0]
    idx = {"r": 1, "o": 2, "a": 3, "k": 4}
    busy = 0
    best = 0
    for ch in croak:
        if ch == "c":
            cnt[0] += 1
            busy += 1
            if busy > best:
                best = busy
        else:
            k = idx[ch]
            if cnt[k - 1] == 0:
                return -1
            cnt[k - 1] -= 1
            if k < 4:
                cnt[k] += 1
            else:
                busy -= 1
    return best if busy == 0 else -1
''',
    tests=[["croakcroak"], ["crcoakroak"], ["croakcrook"], ["croa"], ["c"], ["k"], ["croak"], ["ccrrooaakk"], ["crcrooakak"],
           ["croakcroakcroak"], ["cccrrroooaaakkk"], ["ccroakroak"], ["croakk"], ["rcoak"], ["ccroakcroakroak"]],
)
_r = rnd(8207)


def _valid_recording(r, croaks, frogs=None):
    """A valid recording of `croaks` croaks, produced by a random choice among `frogs` frogs."""
    frogs = frogs or r.randint(1, 6)
    state = [0] * frogs
    left = croaks
    out = []
    while left > 0 or any(state):
        options = [i for i in range(frogs) if state[i] > 0 or left > 0]
        i = r.choice(options)
        if state[i] == 0:
            left -= 1
        out.append("croak"[state[i]])
        state[i] = (state[i] + 1) % 5
    return "".join(out)


_v = _valid_recording(_r, 3000, 40)
p["tests"].append([_v])
_v2 = list(_v)
_v2[len(_v2) // 2] = "o" if _v[len(_v) // 2] != "o" else "a"
p["tests"].append(["".join(_v2)])
p["tests"].append([_valid_recording(_r, 3500, 1)])
p["tests"].append(["c" * 3500 + "r" * 3500 + "o" * 3500 + "a" * 3500 + "k" * 3500])


def b_frogs(croak):
    best = [None]

    def go(i, st, total):
        if i == len(croak):
            if sum(st[1:]) == 0 and (best[0] is None or total < best[0]):
                best[0] = total
            return
        k = "croak".index(croak[i])
        if k == 0:
            if st[0] > 0:
                s2 = list(st)
                s2[0] -= 1
                s2[1] += 1
                go(i + 1, tuple(s2), total)
            s2 = list(st)
            s2[1] += 1
            go(i + 1, tuple(s2), total + 1)
        elif st[k] > 0:
            s2 = list(st)
            s2[k] -= 1
            s2[(k + 1) % 5] += 1
            go(i + 1, tuple(s2), total)

    go(0, (0, 0, 0, 0, 0), 0)
    return -1 if best[0] is None else best[0]


def g_frogs(r):
    if r.random() < 0.55:
        s = _valid_recording(r, r.randint(1, 3))
        if r.random() < 0.3:
            k = r.randrange(len(s))
            s = s[:k] + r.choice("croak") + s[k + 1:]
        return [s]
    return ["".join(r.choice("croak") for _ in range(r.randint(1, 10)))]


def v_frogs(tests):
    for t in tests:
        c = t["args"][0]
        assert 1 <= len(c) <= 20000 and set(c) <= set("croak")
        if len(c) <= 15:
            assert t["expected"] == b_frogs(c)
    assert any(t["expected"] == -1 for t in tests) and any(t["expected"] > 1 for t in tests)


CHECKS["minimum-frogs-croaking"] = (b_frogs, g_frogs, "exact")
VALIDATE["minimum-frogs-croaking"] = v_frogs

p = add(
    id="max-product-of-word-lengths-no-shared-letters", tier="extra", title="Max Product of Word Lengths", diff="Medium", topic=TOPIC,
    fn="maxLengthProduct", params=[("words", "string")], ret="int", cmp="exact",
    desc="<p>The string <code>words</code> contains lowercase words separated by single commas. Choose two different entries of the list (two entries with the same text count as different words, but they trivially share letters) such that the two words have <strong>no letter in common</strong>.</p><p>Return the largest possible value of <code>length(first) * length(second)</code> over all such pairs, or <code>0</code> if every pair shares a letter.</p><pre>words = \"abcw,baz,foo,bar,xtfn,abcdef\"  -> 16   (\"abcw\" and \"xtfn\")\nwords = \"a,ab,abc,d,cd,bcd,abcd\"        -> 4    (\"ab\" and \"cd\")\nwords = \"a,aa,aaa,aaaa\"                  -> 0</pre>",
    constraints=["2 &le; number of words &le; 1,000", "1 &le; words[i].length &le; 40", "Words consist of lowercase English letters"],
    hints=["Comparing two words letter by letter for every pair is slow. Can you describe the set of letters of a word in a single number?",
           "Each word uses a subset of the 26 letters, so it can be stored as a 26-bit mask. Two words share no letter exactly when <code>maskA &amp; maskB == 0</code>.",
           "Words with the same mask are interchangeable except for their length, so keep only the longest word per mask. Then test all pairs of distinct masks."],
    editorial=["Turn every word into a bitmask: bit <code>c - 'a'</code> is set when the word contains the letter. Then 'no common letter' is the single operation <code>maskA &amp; maskB == 0</code>, which takes O(1) instead of O(L).",
               "Only the longest word for each distinct mask can be part of an optimal pair, because swapping a word for a longer one with the same letter set keeps the pair valid and never lowers the product. At most 1,000 masks remain, so checking all pairs is about 500,000 AND operations. Computing the masks costs O(total letters). Note that a pair of words with identical masks always shares letters, so it never needs to be considered."],
    time="O(total letters + m^2) for m distinct masks", space="O(m)",
    solution='''def maxLengthProduct(words):
    best = {}
    for w in words.split(","):
        m = 0
        for c in w:
            m |= 1 << (ord(c) - 97)
        if len(w) > best.get(m, 0):
            best[m] = len(w)
    items = list(best.items())
    ans = 0
    for i in range(len(items)):
        mi, li = items[i]
        for j in range(i + 1, len(items)):
            mj, lj = items[j]
            if mi & mj == 0 and li * lj > ans:
                ans = li * lj
    return ans
''',
    tests=[["abcw,baz,foo,bar,xtfn,abcdef"], ["a,ab,abc,d,cd,bcd,abcd"], ["a,aa,aaa,aaaa"], ["ab,cd"], ["ab,bc"], ["a,a"],
           ["abc,def,ghi,abcdef"], ["zzzz,y,yy,zzzzz"], ["abcdefghijklmnopqrstuvwxyz,a"], ["abcdefghijklm,nopqrstuvwxyz,abc"],
           ["ab,ab,cd,cd"]],
)
_r = rnd(8208)
p["tests"].append([",".join(_rs(_r, _r.randint(1, 40), LET[:_r.randint(2, 12)]) for _ in range(1000))])
p["tests"].append([",".join(_rs(_r, _r.randint(1, 40), LET[i % 20:i % 20 + 3]) if _r.random() < 0.9 else _rs(_r, 30, LET[:26]) for i in range(1000))])
p["tests"].append([",".join(_rs(_r, _r.randint(1, 40), LET) for _ in range(1000))])


def b_maxprod(words):
    ws = words.split(",")
    best = 0
    for i in range(len(ws)):
        for j in range(i + 1, len(ws)):
            if not set(ws[i]) & set(ws[j]):
                best = max(best, len(ws[i]) * len(ws[j]))
    return best


def g_maxprod(r):
    return [",".join(_rs(r, r.randint(1, 5), LET[:r.randint(1, 6)]) for _ in range(r.randint(2, 7)))]


def v_maxprod(tests):
    for t in tests:
        w = t["args"][0]
        ws = w.split(",")
        assert 2 <= len(ws) <= 1000 and _wordlist_ok(w, 1, 40)
        if len(ws) <= 12:
            assert t["expected"] == b_maxprod(w)
    assert any(t["expected"] == 0 for t in tests) and sum(1 for t in tests if t["expected"] > 0) >= 8


CHECKS["max-product-of-word-lengths-no-shared-letters"] = (b_maxprod, g_maxprod, "exact")
VALIDATE["max-product-of-word-lengths-no-shared-letters"] = v_maxprod

p = add(
    id="count-and-say-sequence", tier="common", title="Count and Say", diff="Medium", topic=TOPIC,
    fn="countAndSay", params=[("n", "int")], ret="string", cmp="exact",
    desc="<p>The <em>count-and-say</em> sequence is a sequence of digit strings. Its first term is <code>\"1\"</code>. Every later term describes the previous term by reading it aloud from left to right: split the previous term into maximal groups of equal consecutive digits, and for each group write how many digits it has, followed by the digit itself.</p><p>Return the <code>n</code>-th term of the sequence.</p><pre>term 1: \"1\"        (one 1)\nterm 2: \"11\"       (one 1  ->  \"1\" \"1\")\nterm 3: \"21\"       (two 1s ->  \"2\" \"1\")\nterm 4: \"1211\"     (one 2, one 1)\nterm 5: \"111221\"   (one 1, one 2, two 1s)\n\nn = 4  -> \"1211\"</pre>",
    constraints=["1 &le; n &le; 30", "The 30th term has 4,462 digits"],
    hints=["To get term <code>k + 1</code> you only need term <code>k</code>, so build the terms one after another starting from <code>\"1\"</code>.",
           "Scan the current term with two indices: one at the start of a group, one that runs to the end of the group of equal digits.",
           "For each group append the group length and then the digit. Collect the pieces in a list and join once, so that building a term costs time linear in its length."],
    editorial=["Simulate. Start with <code>\"1\"</code> and repeat <code>n - 1</code> times: walk through the current term, find the end of each run of equal digits, and write <code>length</code> followed by <code>digit</code> into the next term. The digits only ever are 1, 2 and 3 (a run longer than 3 cannot occur), but the algorithm does not rely on this.",
               "The length of the terms grows by a factor of about 1.30 per step (Conway's constant), so the 30th term has 4,462 digits and the total work over all terms is dominated by the last few ones: O(length of term n), which is exponential in n but tiny for n &le; 30. Use a list of string pieces and a single <code>join</code>, instead of repeatedly concatenating to a growing string."],
    time="O(L) where L is the length of term n", space="O(L)",
    solution='''def countAndSay(n):
    cur = "1"
    for _ in range(n - 1):
        out = []
        i = 0
        while i < len(cur):
            j = i
            while j < len(cur) and cur[j] == cur[i]:
                j += 1
            out.append(str(j - i))
            out.append(cur[i])
            i = j
        cur = "".join(out)
    return cur
''',
    tests=[[1], [2], [3], [4], [5], [6], [7], [8], [10], [12], [15], [18], [22], [26], [30]],
)


def b_cas(n):
    from itertools import groupby
    t = "1"
    for _ in range(n - 1):
        t = "".join(str(len(list(g))) + k for k, g in groupby(t))
    return t


def v_cas(tests):
    for t in tests:
        n = t["args"][0]
        assert 1 <= n <= 30 and t["expected"] == b_cas(n)
    assert max(len(t["expected"]) for t in tests) == 4462


CHECKS["count-and-say-sequence"] = (b_cas, lambda r: [r.randint(1, 22)], "exact")
VALIDATE["count-and-say-sequence"] = v_cas

# ---------------------------------------------------------------- HARD

p = add(
    id="text-justification-lines", tier="extra", title="Full Text Justification", diff="Hard", topic=TOPIC,
    fn="justifyText", params=[("words", "string"), ("width", "int")], ret="string", cmp="exact",
    desc="<p>Format a paragraph into lines of exactly <code>width</code> characters. The paragraph is the string <code>words</code>: lowercase words separated by single commas, in reading order.</p><p>Pack words greedily: put as many consecutive words as possible on a line, with at least one space between neighbouring words, without exceeding <code>width</code>. Then pad every line to exactly <code>width</code> characters:</p><ul><li>A line with two or more words that is <strong>not the last</strong> line is justified: the extra spaces are spread as evenly as possible over the gaps between words. If they do not divide evenly, the gaps on the left get one more space than the gaps on the right.</li><li>A line with a single word, and the last line, are left-justified: words are separated by exactly one space and the rest of the line is padded with spaces on the right.</li></ul><p>To keep the answer a single token, return all lines joined with the character <code>|</code>, and write every space as an underscore <code>_</code>. Words never contain these characters.</p><pre>words = \"this,is,an,example,of,text,justification\", width = 16\n-> \"this____is____an|example__of_text|justification___\"\n\nline 1: this + is + an = 8 letters, 8 spaces over 2 gaps -> 4 + 4\nline 2: example + of + text = 13 letters, 3 spaces over 2 gaps -> 2 + 1\nline 3 (last): justification, padded on the right\n\nwords = \"a,b,c\", width = 3   -> \"a_b|c__\"   (a single-word last line is also padded)</pre>",
    constraints=["1 &le; number of words &le; 2,000", "1 &le; words[i].length &le; width", "1 &le; width &le; 100", "The whole <code>words</code> string has at most 10,000 characters", "Words consist of lowercase English letters"],
    hints=["Split the work into two phases: first decide which words go on which line, then build each line's text.",
           "Phase 1 is greedy: keep adding the next word while <code>letters so far + (words so far - 1) minimal gaps + next word</code> still fits in <code>width</code>.",
           "Phase 2: for a normal line with <code>g</code> gaps and <code>S</code> spaces to place, every gap gets <code>S // g</code> spaces and the first <code>S % g</code> gaps get one more. Treat the last line and single-word lines separately: single spaces, then pad on the right."],
    editorial=["The two phases are independent. For line breaking, start at word <code>i</code> and extend <code>j</code> while the line made of words <code>i..j</code> separated by single spaces still has at most <code>width</code> characters. Each word is placed once, so this phase is linear in the number of words.",
               "For the layout of a line holding words <code>i..j</code>: if it is the last line or has only one word, join with single spaces and pad on the right. Otherwise let <code>gaps = j - i</code> and <code>spaces = width - letters</code>; give each gap <code>spaces // gaps</code> spaces plus one extra for the first <code>spaces % gaps</code> gaps. Finally replace spaces with underscores and join the lines with <code>|</code> for the single-token output. Every output character is produced once, so the total cost is O(total output length) = O(lines &middot; width)."],
    time="O(n + lines * width)", space="O(lines * width)",
    solution='''def justifyText(words, width):
    ws = words.split(",")
    n = len(ws)
    lines = []
    i = 0
    while i < n:
        j = i
        total = len(ws[i])
        while j + 1 < n and total + 1 + len(ws[j + 1]) <= width:
            j += 1
            total += 1 + len(ws[j])
        line = ws[i:j + 1]
        if j == n - 1 or len(line) == 1:
            text = " ".join(line)
            text += " " * (width - len(text))
        else:
            gaps = len(line) - 1
            spaces = width - sum(len(w) for w in line)
            q, extra = divmod(spaces, gaps)
            parts = []
            for k in range(gaps):
                parts.append(line[k])
                parts.append(" " * (q + (1 if k < extra else 0)))
            parts.append(line[-1])
            text = "".join(parts)
        lines.append(text.replace(" ", "_"))
        i = j + 1
    return "|".join(lines)
''',
    tests=[["this,is,an,example,of,text,justification", 16], ["a,b,c", 3], ["a", 1], ["hello", 10], ["a,b", 3],
           ["what,must,be,acknowledgment,shall,be", 16], ["science,is,what,we,understand,well,enough,to,explain,to,a,computer", 20],
           ["a,b,c,d,e", 3], ["ab,cd,ef", 5], ["aaa,bbb,ccc", 3], ["x,y,z,w,v,u", 100], ["abcdef,ghi", 7], ["one,two,three,four,five", 9]],
)
_r = rnd(8209)
_w = [_rs(_r, _r.randint(1, 12)) for _ in range(1000)]
p["tests"].append([",".join(_w), 60])
_w = [_rs(_r, _r.randint(1, 6)) for _ in range(1500)]
p["tests"].append([",".join(_w), 30])
_w = [_rs(_r, _r.randint(1, 4)) for _ in range(1500)] + [_rs(_r, 100)]
p["tests"].append([",".join(_w), 100])


def b_justify(words, width):
    ws = words.split(",")
    # break into lines recursively by exact greedy rule, then lay out by handing out spaces one at a time
    out = []
    cur = []
    for w in ws:
        if cur and sum(map(len, cur)) + len(cur) + len(w) > width:
            out.append(cur)
            cur = []
        cur.append(w)
    out.append(cur)
    res = []
    for k, line in enumerate(out):
        if k == len(out) - 1 or len(line) == 1:
            s = " ".join(line)
            res.append(s + " " * (width - len(s)))
            continue
        gaps = [1] * (len(line) - 1)
        left = width - sum(map(len, line)) - len(gaps)
        g = 0
        while left > 0:
            gaps[g % len(gaps)] += 1
            g += 1
            left -= 1
        s = line[0]
        for gp, w in zip(gaps, line[1:]):
            s += " " * gp + w
        res.append(s)
    return "|".join(x.replace(" ", "_") for x in res)


def g_justify(r):
    width = r.randint(1, 12)
    ws = [_rs(r, r.randint(1, width), "abc") for _ in range(r.randint(1, 10))]
    return [",".join(ws), width]


def v_justify(tests):
    for t in tests:
        w, width = t["args"]
        ws = w.split(",")
        assert 1 <= len(ws) <= 2000 and len(w) <= 10000 and 1 <= width <= 100 and _wordlist_ok(w, 1, width)
        lines = t["expected"].split("|")
        assert all(len(l) == width for l in lines)
        assert [x for l in lines for x in l.split("_") if x] == ws
        # greedy: the first word of the next line would not have fit on this line
        for a, b in zip(lines, lines[1:]):
            parts = [x for x in a.split("_") if x]
            used = sum(map(len, parts)) + len(parts) - 1
            assert used + 1 + len(b.split("_")[0]) > width
    assert any(len(t["expected"].split("|")) > 50 for t in tests)


CHECKS["text-justification-lines"] = (b_justify, g_justify, "exact")
VALIDATE["text-justification-lines"] = v_justify

p = add(
    id="stickers-to-spell-word", tier="extra", title="Stickers to Spell a Word", diff="Hard", topic=TOPIC,
    fn="minStickers", params=[("stickers", "string"), ("target", "string")], ret="int", cmp="exact",
    desc="<p>The string <code>stickers</code> lists sticker designs separated by single commas; each design is a word of lowercase letters printed on a sticker, and you own <strong>unlimited copies</strong> of every design. You want to spell the word <code>target</code>.</p><p>From any sticker you may cut out individual letters (each printed letter can be used at most once) and arrange the cut-out letters freely in any order. Return the minimum number of stickers you need to cut up so that all letters of <code>target</code> are obtained, or <code>-1</code> if it is impossible.</p><pre>stickers = \"ab,bc,ca\", target = \"aabbcc\"     -> 3   (each sticker gives two of the six letters)\nstickers = \"xy,yz\",     target = \"xyzz\"       -> 3\nstickers = \"ab,cd\",     target = \"abe\"        -> -1  (no sticker contains e)</pre>",
    constraints=["1 &le; number of stickers &le; 50 and 1 &le; stickers[i].length &le; 10", "1 &le; target.length &le; 15", "All strings consist of lowercase English letters"],
    hints=["Only the multiset of letters still missing matters, not the order of the stickers. The number of different missing-letter states is small because the target has at most 15 letters.",
           "Search with memoisation: <code>f(missing)</code> = fewest stickers to cover the missing letters. Take any sticker, remove the letters it can supply and recurse.",
           "Prune hard: always branch on the <em>first</em> missing letter, because some sticker in the answer must supply it, so only stickers containing that letter need to be tried. Also, ignore letters of stickers that are not in the target."],
    editorial=["Represent the state as the counts of target letters that are still missing. The target has at most 15 letters, so there are at most 2<sup>15</sup> = 32,768 states (a state is a sub-multiset of the target). Let <code>f(state)</code> be the minimum number of stickers needed to cover it, with <code>f(empty) = 0</code>.",
               "Transition: in any optimal solution, some sticker supplies the first missing letter, and the stickers can be used in any order. So branch only over stickers containing that letter, subtract as many letters as the sticker offers (using more letters never hurts), and recurse with one more sticker. Memoise on the state. The recursion returns infinity when no sticker has the first missing letter, and the final answer is -1 in that case.",
               "Complexity: at most 2<sup>15</sup> states, each tries only the stickers holding one particular letter, and a transition costs O(number of distinct target letters), so roughly 2<sup>15</sup> &middot; 50 &middot; 15 operations in the worst case and much less in practice. Removing stickers that are dominated by another sticker (after restricting to target letters) is a cheap extra speed-up."],
    time="O(2^|target| * S * |target|)", space="O(2^|target|)",
    solution='''def minStickers(stickers, target):
    from functools import lru_cache
    letters = sorted(set(target))
    pos = {c: i for i, c in enumerate(letters)}
    need0 = [0] * len(letters)
    for c in target:
        need0[pos[c]] += 1
    vecs = []
    for st in stickers.split(","):
        v = [0] * len(letters)
        for c in st:
            if c in pos:
                v[pos[c]] += 1
        if any(v):
            vecs.append(v)
    by_letter = [[v for v in vecs if v[i]] for i in range(len(letters))]
    INF = float("inf")

    @lru_cache(maxsize=None)
    def f(need):
        first = -1
        for i, x in enumerate(need):
            if x:
                first = i
                break
        if first < 0:
            return 0
        best = INF
        for v in by_letter[first]:
            nxt = tuple(x - y if x > y else 0 for x, y in zip(need, v))
            r = f(nxt)
            if r + 1 < best:
                best = r + 1
        return best

    ans = f(tuple(need0))
    return -1 if ans == INF else ans
''',
    tests=[["ab,bc,ca", "aabbcc"], ["xy,yz", "xyzz"], ["ab,cd", "abe"], ["a", "a"], ["a", "aaaaaaaaaaaaaaa"], ["abc", "cab"],
           ["with,example,science", "thehat"], ["with,example,science", "thatwith"], ["notice,possible", "basicbasic"],
           ["abcde,fghij,klmno", "abcdefghijklmno"], ["ab,ba", "aabb"], ["zz", "zzz"], ["aab,bcc", "abcabc"]],
)
_r = rnd(8210)
_st = [_rs(_r, _r.randint(1, 4), LET[:15]) for _ in range(50)]
p["tests"].append([",".join(_st), "".join(LET[:15])])
_st = [_rs(_r, _r.randint(2, 6), LET[:12]) for _ in range(50)]
p["tests"].append([",".join(_st), _rs(_r, 15, LET[:12])])
_st = [_rs(_r, _r.randint(1, 3), LET[:15]) for _ in range(50)]
p["tests"].append([",".join(_st), LET[:15][::-1]])


def b_stickers(stickers, target):
    sts = stickers.split(",")
    start = "".join(sorted(target))
    seen = {start}
    q = deque([(start, 0)])
    while q:
        cur, d = q.popleft()
        if not cur:
            return d
        for st in sts:
            c = list(cur)
            for ch in st:
                if ch in c:
                    c.remove(ch)
            nxt = "".join(c)
            if nxt not in seen:
                seen.add(nxt)
                q.append((nxt, d + 1))
    return -1


def g_stickers(r):
    k = r.randint(2, 5)
    alpha = LET[:r.randint(2, 5)]
    sts = [_rs(r, r.randint(1, 4), alpha) for _ in range(k)]
    return [",".join(sts), _rs(r, r.randint(1, 6), alpha + ("z" if r.random() < 0.1 else ""))]


def v_stickers(tests):
    for t in tests:
        s, tg = t["args"]
        ss = s.split(",")
        assert 1 <= len(ss) <= 50 and _wordlist_ok(s, 1, 10) and 1 <= len(tg) <= 15 and _lower(tg)
        if len(tg) <= 6:
            assert t["expected"] == b_stickers(s, tg)
    assert any(t["expected"] == -1 for t in tests)


CHECKS["stickers-to-spell-word"] = (b_stickers, g_stickers, "exact")
VALIDATE["stickers-to-spell-word"] = v_stickers

p = add(
    id="palindrome-pair-count", tier="extra", title="Palindrome Pairs", diff="Hard", topic=TOPIC,
    fn="countPalindromePairs", params=[("words", "string")], ret="int", cmp="exact",
    desc="<p>The string <code>words</code> lists distinct non-empty lowercase words separated by single commas.</p><p>Count the <strong>ordered</strong> pairs of different list positions <code>(i, j)</code>, <code>i != j</code>, for which the concatenation <code>words[i] + words[j]</code> is a palindrome. The pairs <code>(i, j)</code> and <code>(j, i)</code> are counted separately when both qualify.</p><pre>words = \"abcd,dcba,lls,s,sssll\"  -> 4\n  abcd+dcba = \"abcddcba\", dcba+abcd = \"dcbaabcd\", s+lls = \"slls\", lls+sssll = \"llssssll\"\nwords = \"bat,tab,cat\"            -> 2   (bat+tab and tab+bat)\nwords = \"a,b,c\"                  -> 0</pre>",
    constraints=["2 &le; number of words &le; 1,000", "1 &le; words[i].length &le; 12", "All words are distinct and consist of lowercase English letters"],
    hints=["Checking all n&sup2; ordered pairs and testing each concatenation costs O(n&sup2; &middot; L), about 12 million character steps for n = 1,000. Think about how a palindrome concatenation is structured.",
           "If <code>a + b</code> is a palindrome and <code>a</code> is at least as long as <code>b</code>, then <code>a</code> splits into <code>P + Q</code> where <code>Q</code> is itself a palindrome and <code>P</code> is the reverse of <code>b</code>.",
           "So for every word and every split point, test whether one part is a palindrome and look up the reverse of the other part in a hash map of all words. Handle the case where the whole word is the 'other part' carefully so that no pair is counted twice and no word is paired with itself."],
    editorial=["Store every word in a dictionary. Consider a pair <code>(a, b)</code> with <code>a + b</code> a palindrome. Because the concatenation reads the same backwards, the shorter word must be the reverse of the matching end of the longer word, and what remains in the middle must be a palindrome. If <code>b</code> is the longer (or equal) word, <code>b = P + Q</code> with <code>P</code> a palindrome and <code>a = reverse(Q)</code>. If <code>a</code> is strictly longer, <code>a = P + Q</code> with <code>Q</code> a palindrome and <code>b = reverse(P)</code>.",
               "So, for each word <code>w</code> and each split <code>w = left + right</code> (with <code>left</code> possibly empty, or <code>right</code> possibly empty): if <code>left</code> is a palindrome, the word <code>reverse(right)</code> placed before <code>w</code> gives a pair <code>(reverse(right), w)</code>; if <code>right</code> is a palindrome and non-empty, the word <code>reverse(left)</code> placed after <code>w</code> gives a pair <code>(w, reverse(left))</code>. Requiring <code>right</code> to be non-empty in the second case is what prevents double counting equal-length pairs, which the first case finds from the other word. Skip the match when it is <code>w</code> itself (a palindromic word is its own reverse). Because every ordered pair is generated exactly once, the counts add up directly. Cost: O(n &middot; L&sup2;) for palindrome tests and dictionary look-ups, about 150,000 character steps."],
    time="O(n * L^2)", space="O(n * L)",
    solution='''def countPalindromePairs(words):
    ws = words.split(",")
    index = {w: i for i, w in enumerate(ws)}
    count = 0
    for i, w in enumerate(ws):
        n = len(w)
        for k in range(n + 1):
            left, right = w[:k], w[k:]
            if left == left[::-1]:
                j = index.get(right[::-1])
                if j is not None and j != i:
                    count += 1
            if right and right == right[::-1]:
                j = index.get(left[::-1])
                if j is not None and j != i:
                    count += 1
    return count
''',
    tests=[["abcd,dcba,lls,s,sssll"], ["bat,tab,cat"], ["a,b,c"], ["a,aa"], ["a,aa,aaa"], ["ab,ba"], ["abc,cba,b"], ["race,car"],
           ["xy,yx,x,y,xyx"], ["ab,ba,abc,cba,a,b"], ["zz,z,zzz,y"], ["abab,baba,aba,b"]],
)
_r = rnd(8212)
p["tests"].append([",".join(sorted({_rs(_r, _r.randint(1, 12), "ab") for _ in range(3000)})[:1000])])
_ws = set()
while len(_ws) < 1000:
    _ws.add(_rs(_r, _r.randint(2, 12), "abc"))
_ws = sorted(_ws)
_r.shuffle(_ws)
p["tests"].append([",".join(_ws)])
_ws = set()
while len(_ws) < 500:
    _x = _rs(_r, _r.randint(1, 6), "abc")
    _ws.add(_x)
    _ws.add(_x[::-1] + _rs(_r, _r.randint(0, 3), "aa"))
_ws = sorted(_ws)[:1000]
_r.shuffle(_ws)
p["tests"].append([",".join(_ws)])


def b_pp(words):
    ws = words.split(",")
    c = 0
    for i in range(len(ws)):
        for j in range(len(ws)):
            if i != j:
                x = ws[i] + ws[j]
                if x == x[::-1]:
                    c += 1
    return c


def g_pp(r):
    alpha = "ab" if r.random() < 0.7 else "abc"
    ws = set()
    for _ in range(r.randint(2, 8)):
        ws.add(_rs(r, r.randint(1, 4), alpha))
    while len(ws) < 2:
        ws.add(_rs(r, r.randint(1, 4), alpha))
    ws = sorted(ws)
    r.shuffle(ws)
    return [",".join(ws)]


def v_pp(tests):
    for t in tests:
        w = t["args"][0]
        ws = w.split(",")
        assert 2 <= len(ws) <= 1000 and len(set(ws)) == len(ws) and _wordlist_ok(w, 1, 12)
        if len(ws) <= 20:
            assert t["expected"] == b_pp(w)
    assert sum(1 for t in tests if t["expected"] > 100) >= 2


CHECKS["palindrome-pair-count"] = (b_pp, g_pp, "exact")
VALIDATE["palindrome-pair-count"] = v_pp
