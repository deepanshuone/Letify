"""Problems: Dynamic Programming, the edit distance family. See data/lib.py for the registry."""
import heapq
import re
from collections import deque
from functools import lru_cache
from itertools import combinations, product

from lib import add, rnd, CHECKS, VALIDATE, gen_arr  # noqa: F401

TOPIC = "Dynamic Programming"
MOD = 10 ** 9 + 7


def _rs(r, alpha, lo, hi):
    return "".join(r.choice(alpha) for _ in range(r.randint(lo, hi)))


def _mutate(r, s, k, alpha):
    """Apply k random single-character edits (insert / delete / replace) to s."""
    s = list(s)
    for _ in range(k):
        op = r.randint(0, 2)
        if op == 0 or not s:
            s.insert(r.randint(0, len(s)), r.choice(alpha))
        elif op == 1:
            del s[r.randrange(len(s))]
        else:
            s[r.randrange(len(s))] = r.choice(alpha)
    return "".join(s)


def _lev(a, b):
    """Plain Levenshtein distance by memoised recursion (used by several brute forces)."""
    @lru_cache(maxsize=None)
    def go(i, j):
        if i == len(a):
            return len(b) - j
        if j == len(b):
            return len(a) - i
        if a[i] == b[j]:
            return go(i + 1, j + 1)
        return 1 + min(go(i + 1, j + 1), go(i + 1, j), go(i, j + 1))
    return go(0, 0)


def _only_lower(*ss):
    return all(x.isalpha() and x.islower() and x.isascii() for x in ss)


# ---------------------------------------------------------------- EASY

p = add(
    id="rebuild-string-at-tail", title="Rebuild a String at the Tail", diff="Easy", topic=TOPIC, tier="extra",
    fn="minTailMoves", params=[("s", "string"), ("t", "string")], ret="int", cmp="exact",
    desc="<p>You hold a string <code>s</code> and may only change it at its right end. One move is either</p><ul><li>remove the last character, or</li><li>append any lowercase letter to the end.</li></ul><p>Return the minimum number of moves that turn <code>s</code> into <code>t</code>. Removing everything and typing <code>t</code> from scratch always works, so an answer exists. Either string may be empty.</p><pre>s = \"abcde\", t = \"abxy\"  ->  5   (remove e, d, c, then append x, y)\ns = \"same\",  t = \"same\"  ->  0\ns = \"\",      t = \"ab\"    ->  2\ns = \"xyz\",   t = \"abc\"   ->  6</pre>",
    constraints=["0 &le; s.length, t.length &le; 20,000", "Both strings contain only lowercase English letters"],
    hints=["Characters in the middle of the string can never be touched without first removing everything after them. So which part of <code>s</code> can survive unchanged?",
           "The surviving part is a prefix of <code>s</code> that is also a prefix of <code>t</code>. Keeping a longer one is always better, so look at the longest common prefix.",
           "If the longest common prefix has length <code>L</code>, you remove <code>len(s) - L</code> characters and then append <code>len(t) - L</code> characters."],
    editorial=["Because moves only affect the last character, a character at position <code>i</code> of <code>s</code> stays untouched only if nothing at or before the moment of its removal reaches it, which means the final string must start with the same prefix. So the surviving part is a common prefix of <code>s</code> and <code>t</code>. Every character of <code>s</code> beyond it must be removed, and every character of <code>t</code> beyond it must be appended.",
               "A longer surviving prefix saves moves on both sides, so take the longest common prefix of length <code>L</code>. The answer is <code>(len(s) - L) + (len(t) - L)</code>. This is the simplest member of the edit distance family: the only 'alignment' possible is prefix against prefix, so no table is needed. The full edit distance later relaxes exactly this restriction."],
    time="O(min(m, n))", space="O(1)",
    solution='''def minTailMoves(s, t):
    L = 0
    limit = min(len(s), len(t))
    while L < limit and s[L] == t[L]:
        L += 1
    return (len(s) - L) + (len(t) - L)
''',
    tests=[["abcde", "abxy"], ["same", "same"], ["", "ab"], ["xyz", "abc"], ["", ""], ["abc", ""], ["a", "a"], ["abc", "abcd"],
           ["abcd", "abc"], ["aab", "aaa"], ["zebra", "zebras"]],
)
_r = rnd(9101)
_base = _rs(_r, "abc", 6000, 6000)
p["tests"] += [
    [_base, _base[:4000] + _rs(_r, "xyz", 1500, 1500)],
    [_base[:5000], _base],
    [_rs(_r, "ab", 5000, 5000), _rs(_r, "ab", 5000, 5000)],
]


def _b_tail(s, t):
    """Breadth-first search over strings; appended letters only need to come from t."""
    alpha = sorted(set(t))
    cap = max(len(s), len(t))
    dist = {s: 0}
    dq = deque([s])
    while dq:
        u = dq.popleft()
        if u == t:
            return dist[u]
        nxt = []
        if u:
            nxt.append(u[:-1])
        if len(u) < cap:
            nxt += [u + c for c in alpha]
        for v in nxt:
            if v not in dist:
                dist[v] = dist[u] + 1
                dq.append(v)
    raise AssertionError("unreachable")


def _v_tail(tests):
    for t in tests:
        s, u = t["args"]
        assert len(s) <= 20000 and len(u) <= 20000 and _only_lower(*([x for x in (s, u) if x]))


CHECKS["rebuild-string-at-tail"] = (_b_tail, lambda r: [_rs(r, "ab", 0, 4), _rs(r, "ab", 0, 4)], "exact")
VALIDATE["rebuild-string-at-tail"] = _v_tail

p = add(
    id="fewest-replacements-to-contain", title="Fewest Replacements to Contain a Word", diff="Easy", topic=TOPIC, tier="extra",
    fn="minReplacementsToContain", params=[("s", "string"), ("t", "string")], ret="int", cmp="exact",
    desc="<p>In one move you may change a single character of <code>s</code> into any lowercase letter. Return the minimum number of moves after which the word <code>t</code> appears in <code>s</code> as a contiguous block of characters.</p><p>The length of <code>s</code> cannot change, so if <code>t</code> is longer than <code>s</code> the answer is <code>-1</code>.</p><pre>s = \"abcdef\", t = \"cxe\"  ->  1   (change d to x)\ns = \"aaaa\",   t = \"aa\"   ->  0\ns = \"ab\",     t = \"abc\"  -> -1\ns = \"xyxy\",   t = \"yy\"   ->  1</pre>",
    constraints=["1 &le; s.length, t.length &le; 2,000", "Both strings contain only lowercase English letters"],
    hints=["Whatever you do, the final string contains <code>t</code> starting at some position. Pick that position first.",
           "Once the start position is fixed, the cost is the number of aligned pairs where the characters differ. Different start positions do not interact.",
           "Try every start from 0 to <code>len(s) - len(t)</code>, count mismatches in that window, and keep the smallest count."],
    editorial=["Only replacements are allowed, so the characters of <code>s</code> never shift: if <code>t</code> ends up starting at index <code>i</code>, then <code>s[i + k]</code> must become <code>t[k]</code> for every <code>k</code>. Each position already equal costs nothing and each other position costs exactly one replacement. The windows are independent, so the answer is the minimum over all start positions of the number of mismatches (the Hamming distance between <code>t</code> and the window).",
               "There are <code>len(s) - len(t) + 1</code> windows and each costs <code>len(t)</code> comparisons, so the total is at most about <code>n&sup2;/4</code> comparisons, fine for 2,000 characters. When insertions and deletions are also allowed the windows stop being aligned and the problem becomes the approximate substring search solved with a table."],
    time="O((n - m + 1) &middot; m)", space="O(1)",
    solution='''def minReplacementsToContain(s, t):
    n, m = len(s), len(t)
    if m > n:
        return -1
    best = m
    for i in range(n - m + 1):
        bad = 0
        for a, b in zip(s[i:i + m], t):
            if a != b:
                bad += 1
                if bad >= best:
                    break
        if bad < best:
            best = bad
            if best == 0:
                break
    return best
''',
    tests=[["abcdef", "cxe"], ["aaaa", "aa"], ["ab", "abc"], ["xyxy", "yy"], ["a", "a"], ["a", "b"], ["abc", "abc"], ["abc", "xyz"],
           ["zzzzz", "zzzzzz"], ["abababab", "bbb"], ["qwerty", "wex"]],
)
_r = rnd(9102)
_s = _rs(_r, "ab", 2000, 2000)
p["tests"] += [
    [_s, _rs(_r, "ab", 900, 900)],
    [_rs(_r, "abc", 2000, 2000), _rs(_r, "abc", 1000, 1000)],
    [_s, _s[300:1700]],
    [_rs(_r, "a", 2000, 2000), "b" * 1999],
]


def _b_contain(s, t):
    n = len(s)
    for k in range(n + 1):
        for pos in combinations(range(n), k):
            for rep in product(sorted(set(t)), repeat=k):
                u = list(s)
                for q, ch in zip(pos, rep):
                    u[q] = ch
                if t in "".join(u):
                    return k
    return -1


def _v_contain(tests):
    for t in tests:
        s, u = t["args"]
        assert 1 <= len(s) <= 2000 and 1 <= len(u) <= 2000 and _only_lower(s, u)


CHECKS["fewest-replacements-to-contain"] = (_b_contain, lambda r: [_rs(r, "ab", 1, 6), _rs(r, "ab", 1, 7)], "exact")
VALIDATE["fewest-replacements-to-contain"] = _v_contain

# ---------------------------------------------------------------- MEDIUM

p = add(
    id="weighted-edit-distance", title="Weighted Edit Distance", diff="Medium", topic=TOPIC, tier="common",
    fn="minEditCost", params=[("s", "string"), ("t", "string"), ("insertCost", "int"), ("deleteCost", "int"), ("replaceCost", "int")], ret="int", cmp="exact",
    desc="<p>Turn the string <code>s</code> into the string <code>t</code> using three kinds of operations, each applied to a single character:</p><ul><li><b>insert</b> any lowercase letter at any position, costing <code>insertCost</code>;</li><li><b>delete</b> any character, costing <code>deleteCost</code>;</li><li><b>replace</b> a character by a different letter, costing <code>replaceCost</code>.</li></ul><p>Return the minimum total cost. Note that a replacement can be more expensive than a delete followed by an insert, in which case you should prefer the latter.</p><pre>s = \"kitten\", t = \"sitting\", costs 1, 1, 1  ->  3\ns = \"abc\",    t = \"abd\",     costs 1, 1, 5  ->  2   (delete c, insert d)\ns = \"ab\",     t = \"\",        costs 1, 3, 1  ->  6</pre>",
    constraints=["0 &le; s.length, t.length &le; 500", "Both strings contain only lowercase English letters", "1 &le; insertCost, deleteCost, replaceCost &le; 1,000"],
    hints=["Think about the last character of each prefix. What are the ways the prefixes <code>s[:i]</code> and <code>t[:j]</code> can end?",
           "Let <code>D[i][j]</code> be the cheapest cost to turn the first i characters of s into the first j characters of t. The last step is a match (free), a replace, a delete of <code>s[i-1]</code>, or an insert of <code>t[j-1]</code>.",
           "<code>D[i][j] = min(D[i-1][j-1] + (0 if equal else replaceCost), D[i-1][j] + deleteCost, D[i][j-1] + insertCost)</code>, with <code>D[i][0] = i*deleteCost</code> and <code>D[0][j] = j*insertCost</code>. Only the previous row is needed."],
    editorial=["Define <code>D[i][j]</code> as the minimum cost of turning the first <code>i</code> characters of <code>s</code> into the first <code>j</code> characters of <code>t</code>. Look at how the optimal sequence handles the last character of each prefix: the two last characters are matched together (free if equal, otherwise a replacement), or the last character of <code>s</code> is deleted, or the last character of <code>t</code> is inserted. That gives the three-way minimum above, and the boundary rows are all deletes or all inserts.",
               "The costs only change the numbers inside the minimum, never the structure, so there is no need to treat 'replace is dearer than delete plus insert' specially: the table picks the cheaper route on its own. With a rolling row the memory is O(n). A greedy rule such as always replacing when lengths agree is wrong as soon as the costs are unequal."],
    time="O(m &middot; n)", space="O(n)",
    solution='''def minEditCost(s, t, insertCost, deleteCost, replaceCost):
    n = len(t)
    prev = [j * insertCost for j in range(n + 1)]
    for i in range(1, len(s) + 1):
        a = s[i - 1]
        cur = [i * deleteCost] + [0] * n
        for j in range(1, n + 1):
            if a == t[j - 1]:
                x = prev[j - 1]
            else:
                x = prev[j - 1] + replaceCost
            y = prev[j] + deleteCost
            if y < x:
                x = y
            y = cur[j - 1] + insertCost
            if y < x:
                x = y
            cur[j] = x
        prev = cur
    return prev[n]
''',
    tests=[["kitten", "sitting", 1, 1, 1], ["abc", "abd", 1, 1, 5], ["ab", "", 1, 3, 1], ["", "abc", 4, 1, 1], ["", "", 3, 3, 3],
           ["abc", "abc", 7, 7, 7], ["horse", "ros", 2, 3, 4], ["intention", "execution", 1, 1, 2], ["a", "b", 10, 10, 1],
           ["abcdef", "azced", 5, 1, 2], ["aaaa", "bbbb", 1000, 1000, 1000]],
)
_r = rnd(9103)
_s = _rs(_r, "abcd", 480, 480)
p["tests"] += [
    [_s, _mutate(_r, _s, 60, "abcd"), 3, 2, 4],
    [_rs(_r, "ab", 500, 500), _rs(_r, "ab", 500, 500), 1, 1, 1],
    [_rs(_r, "abc", 400, 400), _rs(_r, "abc", 300, 300), 7, 5, 11],
]


def _b_wed(s, t, ins, dele, rep):
    """Dijkstra over strings for tiny inputs; memoised recursion over suffixes otherwise."""
    alpha = sorted(set(s + t))
    if len(s) + len(t) > 6 or len(alpha) > 3:
        @lru_cache(maxsize=None)
        def go(i, j):
            if i == len(s):
                return (len(t) - j) * ins
            if j == len(t):
                return (len(s) - i) * dele
            best = min(dele + go(i + 1, j), ins + go(i, j + 1))
            best = min(best, go(i + 1, j + 1) + (0 if s[i] == t[j] else rep))
            return best
        return go(0, 0)
    cap = len(s) + len(t)
    dist = {s: 0}
    pq = [(0, s)]
    while pq:
        d, u = heapq.heappop(pq)
        if d > dist[u]:
            continue
        if u == t:
            return d
        nxt = []
        for i in range(len(u)):
            nxt.append((u[:i] + u[i + 1:], dele))
            for c in alpha:
                if c != u[i]:
                    nxt.append((u[:i] + c + u[i + 1:], rep))
        if len(u) < cap:
            for i in range(len(u) + 1):
                for c in alpha:
                    nxt.append((u[:i] + c + u[i:], ins))
        for v, w in nxt:
            if d + w < dist.get(v, 1 << 60):
                dist[v] = d + w
                heapq.heappush(pq, (d + w, v))
    return dist[t]


def _v_wed(tests):
    for t in tests:
        s, u, a, b, c = t["args"]
        assert len(s) <= 500 and len(u) <= 500 and _only_lower(*([x for x in (s, u) if x]))
        assert all(1 <= v <= 1000 for v in (a, b, c))


CHECKS["weighted-edit-distance"] = (
    _b_wed, lambda r: [_rs(r, "ab", 0, 3), _rs(r, "ab", 0, 3), r.randint(1, 6), r.randint(1, 6), r.randint(1, 9)], "exact")
VALIDATE["weighted-edit-distance"] = _v_wed

p = add(
    id="closest-substring-by-edits", title="Closest Substring by Edits", diff="Medium", topic=TOPIC, tier="common",
    fn="minEditsToSubstring", params=[("text", "string"), ("pattern", "string")], ret="int", cmp="exact",
    desc="<p>Among all substrings of <code>text</code> (contiguous blocks, including the empty block), find the one that is closest to <code>pattern</code> in edit distance, and return that distance. The edit distance counts the minimum number of single-character insertions, deletions and replacements needed to turn one string into the other.</p><p>Equivalently: the fewest edits to <code>pattern</code> so that it occurs inside <code>text</code>.</p><pre>text = \"xxabcdxx\", pattern = \"abd\"  ->  1   (\"abc\" or \"abcd\" is one edit away)\ntext = \"aaaa\",     pattern = \"bbb\"  ->  3\ntext = \"\",         pattern = \"abc\"  ->  3\ntext = \"abc\",      pattern = \"\"     ->  0   (the empty substring)</pre>",
    constraints=["0 &le; text.length &le; 1,000", "0 &le; pattern.length &le; 400", "Both strings contain only lowercase English letters"],
    hints=["Checking every substring with a full edit distance is far too slow: there are about n&sup2; substrings. Is there a way to share work between substrings that end at the same place?",
           "In the ordinary table <code>D[i][j]</code> (first i pattern characters against some text prefix) the first row is <code>D[0][j] = j</code> because the whole text prefix has to be deleted. Which first row would let the match start anywhere for free?",
           "Set <code>D[0][j] = 0</code> for every j, keep the usual recurrence, and take the minimum of the last row <code>D[m][j]</code> over all j (the match may also end anywhere)."],
    editorial=["The standard recurrence aligns two whole strings. To allow the matched part of <code>text</code> to start at any position, make skipping a text prefix free by initialising the row for the empty pattern prefix to zeros: <code>D[0][j] = 0</code>. The column for an empty text prefix keeps its normal value <code>D[i][0] = i</code>, since the pattern characters still have to be produced. This idea is known as Sellers' algorithm.",
               "Ending anywhere is handled at the end: the answer is the minimum over all columns of the last row, <code>min_j D[m][j]</code>. Skipping a text suffix is free in the same sense. The whole table has size <code>m &middot; n</code>, and with a rolling array over the pattern index the memory is O(m). Trying all substrings separately would cost O(n&sup2; &middot; m &middot; n) or worse."],
    time="O(m &middot; n)", space="O(m)",
    solution='''def minEditsToSubstring(text, pattern):
    m = len(pattern)
    col = list(range(m + 1))
    best = col[m]
    for ch in text:
        new = [0] * (m + 1)
        for i in range(1, m + 1):
            if pattern[i - 1] == ch:
                x = col[i - 1]
            else:
                x = col[i - 1] + 1
            y = col[i] + 1
            if y < x:
                x = y
            y = new[i - 1] + 1
            if y < x:
                x = y
            new[i] = x
        col = new
        if col[m] < best:
            best = col[m]
    return best
''',
    tests=[["xxabcdxx", "abd"], ["aaaa", "bbb"], ["", "abc"], ["abc", ""], ["", ""], ["abc", "abc"], ["abcabc", "cab"], ["a", "bcd"],
           ["hello", "yellow"], ["zzzzzzzz", "ab"], ["abcdefgh", "xcdey"]],
)
_r = rnd(9104)
_t = _rs(_r, "abcd", 1000, 1000)
p["tests"] += [
    [_t, _mutate(_r, _t[400:700], 25, "abcd")],
    [_t, _rs(_r, "abcd", 400, 400)],
    [_rs(_r, "ab", 1000, 1000), _rs(_r, "ab", 350, 350)],
]


def _b_sub(text, pattern):
    best = len(pattern)
    n = len(text)
    for i in range(n + 1):
        for j in range(i, n + 1):
            d = _lev(text[i:j], pattern)
            if d < best:
                best = d
    return best


def _v_sub(tests):
    for t in tests:
        a, b = t["args"]
        assert len(a) <= 1000 and len(b) <= 400 and _only_lower(*([x for x in (a, b) if x]))


CHECKS["closest-substring-by-edits"] = (_b_sub, lambda r: [_rs(r, "abc", 0, 7), _rs(r, "abc", 0, 5)], "exact")
VALIDATE["closest-substring-by-edits"] = _v_sub

p = add(
    id="match-with-repeat-counts", title="Match With Repeat Counts", diff="Medium", topic=TOPIC, tier="extra",
    fn="matchesRepeatPattern", params=[("s", "string"), ("p", "string")], ret="bool", cmp="exact",
    desc="<p>A pattern <code>p</code> is a sequence of <em>items</em>. Each item is a lowercase letter or the character <code>.</code> (which matches any single letter), optionally followed by a repeat range written as <code>{lo,hi}</code>, where <code>lo</code> and <code>hi</code> are single digits with <code>lo &le; hi</code>. An item without a range matches exactly one character; an item with a range matches between <code>lo</code> and <code>hi</code> characters (inclusive), each of which must be matched by the letter or the dot.</p><p>Return <code>true</code> if the pattern matches the <b>whole</b> string <code>s</code>.</p><pre>s = \"abbc\",   p = \"ab{1,3}c\"  ->  true\ns = \"ac\",     p = \"ab{1,3}c\"  ->  false  (b must appear at least once)\ns = \"abbbbc\", p = \"ab{1,3}c\"  ->  false  (b may appear at most three times)\ns = \"\",       p = \"a{0,2}\"    ->  true\ns = \"xyz\",    p = \".{2,4}\"     ->  true</pre>",
    constraints=["0 &le; s.length &le; 3,000", "1 &le; p.length &le; 800", "s contains only lowercase letters", "p is well formed: items are letters or <code>.</code>, each optionally followed by exactly one <code>{lo,hi}</code> with single digits 0 &le; lo &le; hi &le; 9"],
    hints=["A recursive search that tries every allowed count for each item can blow up. Think about which positions of <code>s</code> are reachable after processing the first few items.",
           "Keep the set of all text positions that can be reached after the items processed so far. For one item with range {lo,hi}, repeatedly step over characters that match, and collect the positions reached after at least lo and at most hi steps.",
           "The reachable positions fit in a bitmask over <code>0..n</code>. Precompute for every letter a mask of the positions where <code>s</code> has that letter; one matching step is <code>(cur &amp; mask) &lt;&lt; 1</code>. The answer is whether bit n is set at the end."],
    editorial=["Let <code>R</code> be the set of positions <code>i</code> such that the items processed so far can match exactly <code>s[:i]</code>. Start with <code>R = {0}</code>. For an item matching between <code>lo</code> and <code>hi</code> characters, repeat up to <code>hi</code> times: from the current frontier keep the positions whose next character matches the item and move one step to the right. The new <code>R</code> is the union of the frontiers after <code>lo, lo+1, ..., hi</code> steps (and the starting frontier itself if <code>lo = 0</code>). The string matches if position <code>n</code> is in the final set.",
               "Doing this with Python integers as bitsets makes every step a few big-integer operations on 3,000 bits instead of a loop over positions: shift left by one to advance, and AND with a precomputed mask to filter on the letter. The cost is about <code>9 &middot; items</code> bitset operations. The same DP can be written as a table <code>dp[item][pos]</code> with a loop over the counts, which is O(items &middot; n &middot; 9). Plain backtracking is exponential on patterns such as repeated <code>.{0,9}</code>."],
    time="O(items &middot; 9 &middot; n / w)", space="O(n)",
    solution='''def matchesRepeatPattern(s, p):
    n = len(s)
    full = (1 << n) - 1
    masks = {}
    for i, ch in enumerate(s):
        masks[ch] = masks.get(ch, 0) | (1 << i)
    cur = 1
    i = 0
    while i < len(p):
        c = p[i]
        i += 1
        if i < len(p) and p[i] == '{':
            lo = int(p[i + 1])
            hi = int(p[i + 3])
            i += 5
        else:
            lo = hi = 1
        mask = full if c == '.' else masks.get(c, 0)
        new = cur if lo == 0 else 0
        x = cur
        for k in range(1, hi + 1):
            x = (x & mask) << 1
            if not x:
                break
            if k >= lo:
                new |= x
        cur = new
        if not cur:
            return False
    return bool((cur >> n) & 1)
''',
    tests=[["abbc", "ab{1,3}c"], ["ac", "ab{1,3}c"], ["abbbbc", "ab{1,3}c"], ["", "a{0,2}"], ["xyz", ".{2,4}"], ["", "a"],
           ["a", "a{0,0}"], ["aaa", "a{3,3}"], ["aaa", "a{0,2}"], ["abcabc", "abc.{3,3}"], ["abcabc", ".{0,9}c"], ["ba", "a{0,1}b{0,1}"],
           ["aab", "a{1,1}a{1,2}b"]],
)
_r = rnd(9105)


def _rand_pat(r, alpha, items, dotp=0.25, rangep=0.6):
    out = []
    for _ in range(items):
        c = "." if r.random() < dotp else r.choice(alpha)
        if r.random() < rangep:
            lo = r.randint(0, 5)
            hi = r.randint(lo, 9)
            c += "{%d,%d}" % (lo, hi)
        out.append(c)
    return "".join(out)


def _sample_from_pat(r, pat, alpha):
    """Generate a string matched by pat (so that many test answers are true)."""
    res = []
    i = 0
    while i < len(pat):
        c = pat[i]
        i += 1
        if i < len(pat) and pat[i] == "{":
            lo, hi = int(pat[i + 1]), int(pat[i + 3])
            i += 5
        else:
            lo = hi = 1
        for _ in range(r.randint(lo, hi)):
            res.append(r.choice(alpha) if c == "." else c)
    return "".join(res)


_pat = _rand_pat(_r, "ab", 200)
_big = _sample_from_pat(_r, _pat, "ab")
_pat2 = ".{0,9}" * 100 + "ab"
_big2 = _rs(_r, "ab", 2990, 2990) + "ab"
_pat3 = "a{0,9}" * 120
p["tests"] += [
    [_big, _pat],
    [_big + "a", _pat],
    [_big2, _pat2],
    ["a" * 1000, _pat3],
    ["a" * 1080, _pat3],
    ["a" * 1081, _pat3],
]


def _b_rep(s, pat):
    return re.fullmatch(pat, s) is not None


def _g_rep(r):
    alpha = "ab"
    pat = _rand_pat(r, alpha, r.randint(1, 4), 0.3, 0.6)
    s = _sample_from_pat(r, pat, alpha) if r.random() < 0.6 else _rs(r, alpha, 0, 8)
    if s and r.random() < 0.3:
        s = _mutate(r, s, 1, alpha)
    return [s, pat]


def _v_rep(tests):
    for t in tests:
        s, pat = t["args"]
        assert len(s) <= 3000 and 1 <= len(pat) <= 800
        assert not s or _only_lower(s)
        assert re.fullmatch(r"(?:[a-z.](?:\{\d,\d\})?)+", pat), pat
        for lo, hi in re.findall(r"\{(\d),(\d)\}", pat):
            assert int(lo) <= int(hi)


CHECKS["match-with-repeat-counts"] = (_b_rep, _g_rep, "exact")
VALIDATE["match-with-repeat-counts"] = _v_rep

p = add(
    id="count-wildcard-match-ways", title="Count Ways a Wildcard Pattern Matches", diff="Medium", topic=TOPIC, tier="extra",
    fn="countWildcardMatches", params=[("s", "string"), ("p", "string")], ret="int", cmp="exact",
    desc="<p>A pattern <code>p</code> consists of lowercase letters and two special characters: <code>?</code> matches exactly one arbitrary character and <code>*</code> matches any sequence of characters, including the empty one.</p><p>A <em>way to match</em> is a cut of the whole string <code>s</code> into consecutive pieces, one piece per character of <code>p</code> in order, such that a letter takes exactly one character equal to it, a <code>?</code> takes exactly one character, and a <code>*</code> takes any number (possibly zero) of characters. Two ways are different if some pattern character receives a different piece. Return the number of ways, modulo <code>1,000,000,007</code>.</p><pre>s = \"abc\", p = \"*?*\"  ->  3   (the ? can take a, b or c)\ns = \"ab\",  p = \"**\"   ->  3   (the pieces are (\"\",\"ab\"), (\"a\",\"b\"), (\"ab\",\"\"))\ns = \"aa\",  p = \"a*\"   ->  1\ns = \"ab\",  p = \"a?b\"  ->  0\ns = \"\",    p = \"***\"  ->  1</pre>",
    constraints=["0 &le; s.length &le; 600", "0 &le; p.length &le; 600", "s contains only lowercase letters; p contains lowercase letters, <code>?</code> and <code>*</code>"],
    hints=["The yes/no wildcard matching problem uses a table over prefixes of the string and the pattern. What would you store in each cell to count instead of decide?",
           "Let <code>W[i][j]</code> be the number of ways the first j pattern characters can consume exactly the first i characters of s. A letter or <code>?</code> consumes one character, so it only looks at <code>W[i-1][j-1]</code> (if it fits).",
           "For <code>*</code>, the star takes k &ge; 0 characters, so <code>W[i][j]</code> is the sum of <code>W[i-k][j-1]</code> over all k. That sum telescopes: <code>W[i][j] = W[i][j-1] + W[i-1][j]</code>. Take everything modulo 10<sup>9</sup>+7."],
    editorial=["Count paths instead of testing reachability. <code>W[i][j]</code> is the number of ways in which the first <code>j</code> pattern characters match exactly the first <code>i</code> characters of <code>s</code>. The base row is <code>W[0][j] = 1</code> while every pattern character so far is <code>*</code> (each takes the empty piece) and <code>0</code> after the first non-star. The base column is <code>W[i][0] = 0</code> for <code>i &gt; 0</code>.",
               "A letter or <code>?</code> takes one character: <code>W[i][j] = W[i-1][j-1]</code> if it matches <code>s[i-1]</code>, else 0. A star takes <code>k</code> characters for any <code>k</code> from 0 to i, so <code>W[i][j] = sum_k W[i-k][j-1]</code>; subtracting the same formula for <code>i-1</code> shows that this equals <code>W[i][j-1] + W[i-1][j]</code>, so each cell is O(1). The values are reduced modulo 10<sup>9</sup>+7 because the number of ways grows quickly (many stars give binomial-sized counts). A rolling row keeps the memory linear."],
    time="O(m &middot; n)", space="O(n)",
    solution='''def countWildcardMatches(s, p):
    MOD = 10 ** 9 + 7
    n = len(p)
    prev = [0] * (n + 1)
    prev[0] = 1
    for j in range(1, n + 1):
        prev[j] = prev[j - 1] if p[j - 1] == '*' else 0
    for i in range(1, len(s) + 1):
        ch = s[i - 1]
        cur = [0] * (n + 1)
        for j in range(1, n + 1):
            c = p[j - 1]
            if c == '*':
                cur[j] = (cur[j - 1] + prev[j]) % MOD
            elif c == '?' or c == ch:
                cur[j] = prev[j - 1]
        prev = cur
    return prev[n]
''',
    tests=[["abc", "*?*"], ["ab", "**"], ["aa", "a*"], ["ab", "a?b"], ["", "***"], ["", ""], ["a", ""], ["", "a"], ["abc", "abc"],
           ["abc", "???"], ["aaaa", "*a*a*"], ["abcde", "*****"]],
)
_r = rnd(9106)
p["tests"] += [
    ["a" * 600, "*" * 600],
    [_rs(_r, "ab", 600, 600), "*?" * 150 + "*a*b*"],
    [_rs(_r, "ab", 500, 500), _rs(_r, "ab*?", 600, 600)],
    ["a" * 600, "*a" * 300],
]


def _b_cw(s, pat):
    n, m = len(s), len(pat)

    def go(i, j):
        if j == m:
            return 1 if i == n else 0
        c = pat[j]
        if c == "*":
            return sum(go(i + k, j + 1) for k in range(n - i + 1))
        if i < n and (c == "?" or c == s[i]):
            return go(i + 1, j + 1)
        return 0

    return go(0, 0) % MOD


def _v_cw(tests):
    for t in tests:
        s, pat = t["args"]
        assert len(s) <= 600 and len(pat) <= 600
        assert all(c in "abcdefghijklmnopqrstuvwxyz" for c in s)
        assert all(c in "abcdefghijklmnopqrstuvwxyz?*" for c in pat)


CHECKS["count-wildcard-match-ways"] = (
    _b_cw, lambda r: [_rs(r, "ab", 0, 6), _rs(r, "ab?*", 0, 6)], "exact")
VALIDATE["count-wildcard-match-ways"] = _v_cw

p = add(
    id="edit-distance-within-k", title="Edit Distance Within K", diff="Medium", topic=TOPIC, tier="extra",
    fn="editDistanceAtMostK", params=[("s", "string"), ("t", "string"), ("k", "int")], ret="int", cmp="exact",
    desc="<p>The edit distance between two strings is the minimum number of single-character insertions, deletions and replacements needed to turn one into the other.</p><p>Given <code>s</code>, <code>t</code> and a small integer <code>k</code>, return the edit distance between <code>s</code> and <code>t</code> if it is at most <code>k</code>, and <code>-1</code> otherwise. The strings can be thousands of characters long, so a full <code>m &times; n</code> table is too slow; use the fact that <code>k</code> is small.</p><pre>s = \"kitten\", t = \"sitting\", k = 3  ->  3\ns = \"kitten\", t = \"sitting\", k = 2  -> -1\ns = \"abc\",    t = \"abc\",     k = 0  ->  0\ns = \"abcd\",   t = \"abcdefgh\", k = 3  -> -1   (the length gap alone is 4)</pre>",
    constraints=["0 &le; s.length, t.length &le; 6,000", "0 &le; k &le; 20", "Both strings contain only lowercase English letters"],
    hints=["A full table has up to 36 million cells. Which cells can ever be part of a path of cost at most k?",
           "A cell <code>(i, j)</code> needs at least <code>|i - j|</code> insertions or deletions just to get there, so only cells with <code>|i - j| &le; k</code> matter: a band of width 2k+1 around the diagonal.",
           "Store only the band: index each row by <code>d = j - i + k</code> in <code>[0, 2k]</code>. The diagonal move keeps d, a delete reads d+1 of the previous row, an insert reads d-1 of the current row. Treat everything outside the band as 'more than k'."],
    editorial=["Any alignment that reaches table cell <code>(i, j)</code> has already used at least <code>|i - j|</code> insertions or deletions, because every unit of difference between the two prefix lengths needs one. A path of total cost at most <code>k</code> therefore never leaves the band <code>|i - j| &le; k</code>. Cells outside the band can be treated as infinity, so only <code>2k + 1</code> cells per row need computing. If <code>|len(s) - len(t)| &gt; k</code> the answer is immediately <code>-1</code>.",
               "Index row <code>i</code> by the offset <code>d = j - i + k</code>. The cell above-left (a match or replacement) has the same offset in the previous row, the cell above (a delete) is offset <code>d + 1</code> in the previous row, and the cell to the left (an insert) is offset <code>d - 1</code> in the same row. Clamp values at <code>k + 1</code> to keep numbers small. The final answer is the value at the bottom-right cell if it is at most <code>k</code>. Total time is <code>O(n &middot; k)</code> instead of <code>O(m &middot; n)</code>, which for 6,000 characters and <code>k = 20</code> is about 250,000 cells instead of 36 million."],
    time="O((m + n) &middot; k)", space="O(k)",
    solution='''def editDistanceAtMostK(s, t, k):
    m, n = len(s), len(t)
    if abs(m - n) > k:
        return -1
    INF = k + 1
    w = 2 * k + 1
    prev = [INF] * (w + 1)
    for j in range(0, min(n, k) + 1):
        prev[j + k] = j
    for i in range(1, m + 1):
        cur = [INF] * (w + 1)
        a = s[i - 1]
        for d in range(w):
            j = i + d - k
            if j < 0 or j > n:
                continue
            if j == 0:
                v = i
            else:
                v = prev[d] + (0 if a == t[j - 1] else 1)
                u = prev[d + 1] + 1
                if u < v:
                    v = u
                if d > 0:
                    u = cur[d - 1] + 1
                    if u < v:
                        v = u
            cur[d] = v if v < INF else INF
        prev = cur
    ans = prev[n - m + k]
    return ans if ans <= k else -1
''',
    tests=[["kitten", "sitting", 3], ["kitten", "sitting", 2], ["abc", "abc", 0], ["abcd", "abcdefgh", 3], ["", "", 0], ["", "abc", 3],
           ["", "abc", 2], ["abc", "", 3], ["a", "b", 0], ["a", "b", 1], ["horse", "ros", 3], ["intention", "execution", 5]],
)
_r = rnd(9107)
_s = _rs(_r, "abcd", 6000, 6000)
_t = _mutate(_r, _s, 17, "abcd")
p["tests"] += [
    [_s, _t, 20],
    [_s, _t, 8],
    [_s, _s[:2500] + _rs(_r, "abcd", 3500, 3500), 20],
]


def _b_edk(s, t, k):
    d = _lev(s, t)
    return d if d <= k else -1


def _v_edk(tests):
    for t in tests:
        s, u, k = t["args"]
        assert len(s) <= 6000 and len(u) <= 6000 and 0 <= k <= 20 and _only_lower(*([x for x in (s, u) if x]))


CHECKS["edit-distance-within-k"] = (
    _b_edk, lambda r: [_rs(r, "ab", 0, 8), _rs(r, "ab", 0, 8), r.randint(0, 6)], "exact")
VALIDATE["edit-distance-within-k"] = _v_edk

p = add(
    id="cheapest-deletions-to-spell-target", title="Cheapest Deletions to Spell a Target", diff="Medium", topic=TOPIC, tier="extra",
    fn="minDeletionCost", params=[("s", "string"), ("cost", "int[]"), ("t", "string")], ret="int", cmp="exact",
    desc="<p>Deleting the character at position <code>i</code> of <code>s</code> costs <code>cost[i]</code>. Delete some characters (possibly none) so that the string that remains is exactly <code>t</code>, and return the minimum total cost of the deletions. If this is impossible, return <code>-1</code>.</p><pre>s = \"abcab\", cost = [4,1,3,2,5], t = \"ab\"  ->  6   (keep positions 0 and 4, delete 1, 2, 3)\ns = \"xy\",    cost = [1,1],         t = \"yx\"  -> -1\ns = \"aa\",    cost = [5,2],         t = \"a\"   ->  2   (keep the expensive one)\ns = \"abc\",   cost = [1,1,1],       t = \"\"    ->  3</pre>",
    constraints=["0 &le; s.length = cost.length &le; 1,500", "0 &le; t.length &le; 300", "1 &le; cost[i] &le; 1,000", "s and t contain only lowercase English letters"],
    hints=["Total deletion cost = (sum of all costs) - (sum of the costs of the characters you keep). So maximise what you keep.",
           "The kept characters must spell <code>t</code>, in order, as a subsequence of <code>s</code>. Different ways to choose that subsequence keep different total costs.",
           "Let <code>best[j]</code> be the maximum kept cost for matching the first j characters of t using the characters of s seen so far. Process s left to right and update j from high to low: <code>best[j] = max(best[j], best[j-1] + cost[i])</code> when <code>s[i] == t[j-1]</code>."],
    editorial=["The deletion cost equals <code>sum(cost) - kept</code>, where <code>kept</code> is the total cost of the surviving characters. The survivors form a subsequence of <code>s</code> equal to <code>t</code>, so the task becomes: among all occurrences of <code>t</code> as a subsequence of <code>s</code>, find the one with maximum total weight. A plain greedy match picks the earliest positions, which is not necessarily the heaviest.",
               "Use a one-dimensional table: <code>best[j]</code> is the maximum weight with which the first <code>j</code> characters of <code>t</code> can be matched using the prefix of <code>s</code> processed so far, or minus infinity if impossible, with <code>best[0] = 0</code>. For each character of <code>s</code>, scan <code>j</code> downwards so every character of <code>s</code> is used at most once, and apply <code>best[j] = max(best[j], best[j-1] + cost[i])</code> whenever the letters agree. The answer is <code>sum(cost) - best[len(t)]</code>, or <code>-1</code> if <code>best[len(t)]</code> is still minus infinity. The running time is <code>O(len(s) &middot; len(t))</code>."],
    time="O(m &middot; n)", space="O(n)",
    solution='''def minDeletionCost(s, cost, t):
    n = len(t)
    NEG = -1
    best = [NEG] * (n + 1)
    best[0] = 0
    for i, ch in enumerate(s):
        c = cost[i]
        for j in range(min(i + 1, n), 0, -1):
            if t[j - 1] == ch and best[j - 1] >= 0:
                v = best[j - 1] + c
                if v > best[j]:
                    best[j] = v
    if best[n] < 0:
        return -1
    return sum(cost) - best[n]
''',
    tests=[["abcab", [4, 1, 3, 2, 5], "ab"], ["xy", [1, 1], "yx"], ["aa", [5, 2], "a"], ["abc", [1, 1, 1], ""], ["", [], ""], ["", [], "a"],
           ["abc", [3, 2, 1], "abc"], ["aaa", [1, 9, 1], "aa"], ["abab", [5, 1, 1, 5], "ab"], ["ba", [7, 7], "a"],
           ["abcabcabc", [1, 2, 3, 4, 5, 6, 7, 8, 9], "abc"]],
)
_r = rnd(9108)
_s = _rs(_r, "abc", 1500, 1500)
p["tests"] += [
    [_s, [_r.randint(1, 1000) for _ in _s], _rs(_r, "abc", 100, 100)],
    [_s, [_r.randint(1, 1000) for _ in _s], "".join(_s[i] for i in sorted(_r.sample(range(1500), 300)))],
    ["a" * 1500, [_r.randint(1, 1000) for _ in range(1500)], "a" * 300],
]


def _b_cd(s, cost, t):
    n = len(s)
    best = None
    for mask in range(1 << n):
        kept = "".join(s[i] for i in range(n) if mask >> i & 1)
        if kept == t:
            d = sum(cost[i] for i in range(n) if not mask >> i & 1)
            if best is None or d < best:
                best = d
    return -1 if best is None else best


def _g_cd(r):
    s = _rs(r, "ab", 0, 8)
    t = _rs(r, "ab", 0, 3)
    if r.random() < 0.5 and s:
        t = "".join(c for c in s if r.random() < 0.5)
    return [s, [r.randint(1, 9) for _ in s], t]


def _v_cd(tests):
    for t in tests:
        s, cost, u = t["args"]
        assert len(s) == len(cost) <= 1500 and len(u) <= 300
        assert all(1 <= c <= 1000 for c in cost) and _only_lower(*([x for x in (s, u) if x]))


CHECKS["cheapest-deletions-to-spell-target"] = (_b_cd, _g_cd, "exact")
VALIDATE["cheapest-deletions-to-spell-target"] = _v_cd

# ---------------------------------------------------------------- HARD

p = add(
    id="edit-distance-with-adjacent-swaps", title="Edit Distance With Adjacent Swaps", diff="Hard", topic=TOPIC, tier="extra",
    fn="editDistanceWithSwaps", params=[("s", "string"), ("t", "string")], ret="int", cmp="exact",
    desc="<p>Turn <code>s</code> into <code>t</code> with the fewest operations, where one operation on the <em>current</em> string is any of:</p><ul><li>insert a letter anywhere,</li><li>delete a letter,</li><li>replace a letter by a different one,</li><li>swap two <b>neighbouring</b> letters.</li></ul><p>Every operation costs 1, and you may keep editing characters that were produced by an earlier operation (including characters that were swapped). Return the minimum number of operations.</p><pre>s = \"ab\",   t = \"ba\"   ->  1\ns = \"abcd\", t = \"acbd\" ->  1\ns = \"ca\",   t = \"abc\"  ->  2   (swap to get ac, then insert b between a and c)\ns = \"\",     t = \"abc\"  ->  3</pre><p>Note that the third example costs 3 if swaps are not allowed, and that it shows why inserting something between two swapped letters is allowed.</p>",
    constraints=["0 &le; s.length, t.length &le; 500", "Both strings contain only lowercase English letters"],
    hints=["Start from the ordinary edit distance table and think about when a swap helps. A swap fixes two positions at once, when <code>s[i-1] = t[j-2]</code> and <code>s[i-2] = t[j-1]</code>.",
           "The simple case (the two swapped letters are adjacent in both strings) is easy. The hard case is when some letters are inserted or deleted between the swapped pair, as in <code>ca -&gt; abc</code>. Then the swapped letters are far apart in one of the strings.",
           "For the cell (i, j), look at the last position <code>i1 &lt; i</code> where the letter <code>t[j-1]</code> occurs in s, and at the last <code>j1 &lt; j</code> where <code>s[i-1]</code> occurs in t. Transposing them costs <code>D[i1-1][j1-1] + (i-i1-1) deletions + 1 swap + (j-j1-1) insertions</code>."],
    editorial=["Without swaps this is the usual table. With swaps the unrestricted version (true Damerau-Levenshtein distance) has to allow letters to be inserted or deleted <em>between</em> the two letters that get exchanged. Consider cell <code>(i, j)</code> and let <code>i1</code> be the last row before <code>i</code> where <code>s</code> holds the letter <code>t[j-1]</code>, and <code>j1</code> the last column before <code>j</code> where <code>t</code> holds the letter <code>s[i-1]</code>. If both exist, the two letters can be crossed: align <code>s[i1-1]</code> with <code>t[j-1]</code> and <code>s[i-1]</code> with <code>t[j1-1]</code>, delete the <code>i - i1 - 1</code> letters of s between them, insert the <code>j - j1 - 1</code> letters of t between them, and pay 1 for the swap. The cost is <code>D[i1-1][j1-1] + (i - i1 - 1) + 1 + (j - j1 - 1)</code>.",
               "So <code>D[i][j]</code> is the minimum of the usual three options (diagonal with cost 0 or 1, delete, insert) and, when available, the transposition option above. To find <code>i1</code> quickly, keep for every letter the last row of s where it occurred while scanning rows, and keep <code>j1</code> as a running value along the row (the last column where <code>t[j-1] == s[i-1]</code>). This is the classic Lowrance-Wagner algorithm and runs in <code>O(m &middot; n)</code> time and memory (the full table is needed because the transposition option jumps to earlier rows). A table that only allows swaps of letters adjacent in both strings (the restricted 'optimal string alignment' distance) gives 3 for <code>ca -&gt; abc</code>, which is wrong here."],
    time="O(m &middot; n)", space="O(m &middot; n)",
    solution='''def editDistanceWithSwaps(s, t):
    m, n = len(s), len(t)
    INF = m + n
    d = [[0] * (n + 2) for _ in range(m + 2)]
    d[0][0] = INF
    for i in range(m + 1):
        d[i + 1][0] = INF
        d[i + 1][1] = i
    for j in range(n + 1):
        d[0][j + 1] = INF
        d[1][j + 1] = j
    last_row = {}
    for i in range(1, m + 1):
        db = 0
        a = s[i - 1]
        for j in range(1, n + 1):
            i1 = last_row.get(t[j - 1], 0)
            j1 = db
            if a == t[j - 1]:
                cost = 0
                db = j
            else:
                cost = 1
            best = d[i][j] + cost
            v = d[i + 1][j] + 1
            if v < best:
                best = v
            v = d[i][j + 1] + 1
            if v < best:
                best = v
            v = d[i1][j1] + (i - i1 - 1) + 1 + (j - j1 - 1)
            if v < best:
                best = v
            d[i + 1][j + 1] = best
        last_row[a] = i
    return d[m + 1][n + 1]
''',
    tests=[["ab", "ba"], ["abcd", "acbd"], ["ca", "abc"], ["", "abc"], ["", ""], ["abc", ""], ["abc", "abc"], ["abcd", "badc"],
           ["abcd", "dcba"], ["a", "b"], ["ba", "cab"], ["abcde", "badce"], ["xyzw", "yzxw"]],
)
_r = rnd(9109)
_s = _rs(_r, "abcd", 450, 450)


def _swap_some(r, s, k):
    s = list(s)
    for _ in range(k):
        i = r.randrange(len(s) - 1)
        s[i], s[i + 1] = s[i + 1], s[i]
    return "".join(s)


p["tests"] += [
    [_s, _mutate(_r, _swap_some(_r, _s, 60), 20, "abcd")],
    [_rs(_r, "ab", 500, 500), _rs(_r, "ab", 500, 500)],
    [_rs(_r, "abcdefgh", 400, 400), _rs(_r, "abcdefgh", 450, 450)],
]


def _b_dls(s, t):
    """Breadth-first search over strings (tiny inputs only)."""
    alpha = sorted(set(s + t))
    cap = max(len(s), len(t)) + 1
    dist = {s: 0}
    dq = deque([s])
    while dq:
        u = dq.popleft()
        if u == t:
            return dist[u]
        nxt = []
        for i in range(len(u)):
            nxt.append(u[:i] + u[i + 1:])
            for c in alpha:
                if c != u[i]:
                    nxt.append(u[:i] + c + u[i + 1:])
            if i + 1 < len(u) and u[i] != u[i + 1]:
                nxt.append(u[:i] + u[i + 1] + u[i] + u[i + 2:])
        if len(u) < cap:
            for i in range(len(u) + 1):
                for c in alpha:
                    nxt.append(u[:i] + c + u[i:])
        for v in nxt:
            if v not in dist:
                dist[v] = dist[u] + 1
                dq.append(v)
    raise AssertionError("unreachable")


def _v_dls(tests):
    for t in tests:
        s, u = t["args"]
        assert len(s) <= 500 and len(u) <= 500 and _only_lower(*([x for x in (s, u) if x]))


CHECKS["edit-distance-with-adjacent-swaps"] = (_b_dls, lambda r: [_rs(r, "abc", 0, 4), _rs(r, "abc", 0, 4)], "exact")
VALIDATE["edit-distance-with-adjacent-swaps"] = _v_dls

p = add(
    id="count-optimal-edit-scripts", title="Count Optimal Edit Scripts", diff="Hard", topic=TOPIC, tier="extra",
    fn="countOptimalScripts", params=[("s", "string"), ("t", "string")], ret="int", cmp="exact",
    desc="<p>An <em>edit script</em> from <code>s</code> to <code>t</code> reads both strings from left to right, one step at a time. Every step is one of:</p><ul><li><b>keep</b>: the next characters of <code>s</code> and <code>t</code> are equal, consume both (cost 0);</li><li><b>replace</b>: the next characters are different, consume both (cost 1);</li><li><b>delete</b>: consume one character of <code>s</code> (cost 1);</li><li><b>insert</b>: consume one character of <code>t</code> (cost 1).</li></ul><p>The script ends when both strings are fully consumed. Count how many different scripts have the minimum possible total cost (the edit distance), modulo <code>1,000,000,007</code>. Two scripts are different if their sequences of steps differ. When the next characters are equal, the only way to consume both together is <em>keep</em>.</p><pre>s = \"cat\", t = \"cut\"  ->  1   (keep, replace, keep)\ns = \"ab\",  t = \"ba\"   ->  3   (replace twice; delete a, keep b, insert a; insert b, keep a, delete b)\ns = \"a\",   t = \"b\"    ->  1\ns = \"\",    t = \"\"     ->  1   (the empty script)</pre>",
    constraints=["0 &le; s.length, t.length &le; 400", "Both strings contain only lowercase English letters"],
    hints=["First compute the ordinary edit distance table. A script is a monotone path from the top-left to the bottom-right cell; which paths are optimal?",
           "Store in every cell a pair: the minimum cost to reach it and the number of different paths that achieve that minimum.",
           "For a cell, look at its three predecessors (diagonal, above, left) with their added costs. The new minimum is the smallest total; the count is the sum of the counts of all predecessors that reach exactly that minimum. Reduce modulo 10<sup>9</sup>+7."],
    editorial=["Every script is a path in the grid of prefix pairs <code>(i, j)</code>: a diagonal step consumes one character of each string, a vertical step deletes, a horizontal step inserts. Keeping and replacing are the two kinds of diagonal step, chosen by whether the characters are equal. So counting optimal scripts means counting the cheapest paths in a grid with these step costs.",
               "Each cell stores <code>(cost, ways)</code>. To fill it, compute the three candidate costs: <code>cost[i-1][j-1] + (0 if equal else 1)</code>, <code>cost[i-1][j] + 1</code> and <code>cost[i][j-1] + 1</code>. The cell's cost is the smallest candidate, and its ways is the sum of <code>ways</code> over all predecessors whose candidate equals that smallest value, modulo 10<sup>9</sup>+7. This works because the cost of a path is additive, so a cheapest path to a cell extends a cheapest path to one of its predecessors. Do not take the maximum or the minimum of counts across different costs: only predecessors that tie for the best cost are summed. Row-wise rolling arrays are enough, so the memory is linear."],
    time="O(m &middot; n)", space="O(n)",
    solution='''def countOptimalScripts(s, t):
    MOD = 10 ** 9 + 7
    n = len(t)
    prev_c = list(range(n + 1))
    prev_w = [1] * (n + 1)
    for i in range(1, len(s) + 1):
        a = s[i - 1]
        cur_c = [i] + [0] * n
        cur_w = [1] + [0] * n
        for j in range(1, n + 1):
            if a == t[j - 1]:
                c = prev_c[j - 1]
            else:
                c = prev_c[j - 1] + 1
            w = prev_w[j - 1]
            e = prev_c[j] + 1
            if e < c:
                c = e
                w = prev_w[j]
            elif e == c:
                w += prev_w[j]
            e = cur_c[j - 1] + 1
            if e < c:
                c = e
                w = cur_w[j - 1]
            elif e == c:
                w += cur_w[j - 1]
            cur_c[j] = c
            cur_w[j] = w % MOD
        prev_c, prev_w = cur_c, cur_w
    return prev_w[n] % MOD
''',
    tests=[["cat", "cut"], ["ab", "ba"], ["a", "b"], ["", ""], ["", "abc"], ["abc", ""], ["abc", "abc"], ["aa", "a"], ["ab", "cd"],
           ["abc", "bca"], ["kitten", "sitting"]],
)
_r = rnd(9110)
_s = _rs(_r, "ab", 400, 400)
p["tests"] += [
    [_s, _rs(_r, "ab", 400, 400)],
    ["a" * 400, "a" * 399 + "b"],
    ["ab" * 200, "ba" * 200],
]


def _b_ces(s, t):
    m, n = len(s), len(t)
    res = {}

    def go(i, j, cost):
        if i == m and j == n:
            res[cost] = res.get(cost, 0) + 1
            return
        if i < m and j < n:
            go(i + 1, j + 1, cost + (0 if s[i] == t[j] else 1))
        if i < m:
            go(i + 1, j, cost + 1)
        if j < n:
            go(i, j + 1, cost + 1)

    go(0, 0, 0)
    return res[min(res)] % MOD


def _v_ces(tests):
    for t in tests:
        s, u = t["args"]
        assert len(s) <= 400 and len(u) <= 400 and _only_lower(*([x for x in (s, u) if x]))


CHECKS["count-optimal-edit-scripts"] = (_b_ces, lambda r: [_rs(r, "ab", 0, 5), _rs(r, "ab", 0, 5)], "exact")
VALIDATE["count-optimal-edit-scripts"] = _v_ces

p = add(
    id="min-edits-to-match-wildcard-pattern", title="Fewest Edits to Match a Wildcard Pattern", diff="Hard", topic=TOPIC, tier="extra",
    fn="minEditsToMatchPattern", params=[("s", "string"), ("p", "string")], ret="int", cmp="exact",
    desc="<p>The pattern <code>p</code> contains lowercase letters, <code>?</code> (matches exactly one arbitrary letter) and <code>*</code> (matches any sequence of letters, including the empty one). You may edit the string <code>s</code> with single-letter operations, each costing 1: insert a letter anywhere, delete a letter, or replace a letter by another one.</p><p>Return the minimum number of edits after which the edited string matches the <b>whole</b> pattern. Pattern characters are never edited.</p><pre>s = \"abc\", p = \"a*c\"   ->  0\ns = \"abc\", p = \"a?\"    ->  1   (delete c; the ? takes b)\ns = \"\",    p = \"a?*\"   ->  2   (insert a, then any letter for ?; the star is empty)\ns = \"xyz\", p = \"abc\"   ->  3\ns = \"abcd\", p = \"b*\"   ->  1   (replace or delete the first letter)</pre>",
    constraints=["0 &le; s.length &le; 500", "0 &le; p.length &le; 500", "s contains only lowercase letters; p contains lowercase letters, <code>?</code> and <code>*</code>"],
    hints=["Combine the ideas of edit distance and of wildcard matching: a table over prefixes of s and prefixes of p whose cells hold a minimum number of edits instead of a boolean.",
           "Let <code>F[i][j]</code> be the fewest edits making <code>s[:i]</code> match <code>p[:j]</code>. A pattern letter can be aligned with <code>s[i-1]</code> (cost 0 if equal, else 1), or <code>s[i-1]</code> can be deleted (+1), or the letter can be inserted (+1). A <code>?</code> aligns with any letter at cost 0.",
           "A star is free: it can be empty (<code>F[i][j-1]</code>) or swallow one more letter of s (<code>F[i-1][j]</code>). Base: <code>F[i][0] = i</code>; <code>F[0][j]</code> is the number of non-star characters in <code>p[:j]</code>."],
    editorial=["Think of an alignment between <code>s</code> and the pattern. Each pattern character is either aligned with one character of <code>s</code> or has no partner (it must then be produced by an insertion, except a star which simply stays empty). Each character of <code>s</code> is either aligned, deleted, or swallowed by a star. This is the edit distance alignment with wildcard-specific costs: a literal aligned with a different letter costs 1 (replace), a literal with no partner costs 1 (insert), a <code>?</code> aligned with anything costs 0, a <code>?</code> without partner costs 1 (insert an arbitrary letter), and a star costs 0 however many letters it swallows.",
               "That gives <code>F[i][j]</code> for a literal <code>c = p[j-1]</code> as <code>min(F[i-1][j-1] + (s[i-1] != c), F[i-1][j] + 1, F[i][j-1] + 1)</code>; for <code>?</code> the first term has no mismatch cost; for <code>*</code> it is <code>min(F[i][j-1], F[i-1][j])</code>. Deleting a letter next to a star is never better than letting the star swallow it, so the star rule needs no extra +1. The base values are <code>F[i][0] = i</code> (delete everything) and <code>F[0][j] = F[0][j-1] + (0 if p[j-1] is a star else 1)</code>. Time and space are linear in the table size, and a rolling row brings the memory down to O(n)."],
    time="O(m &middot; n)", space="O(n)",
    solution='''def minEditsToMatchPattern(s, p):
    n = len(p)
    prev = [0] * (n + 1)
    for j in range(1, n + 1):
        prev[j] = prev[j - 1] + (0 if p[j - 1] == '*' else 1)
    for i in range(1, len(s) + 1):
        a = s[i - 1]
        cur = [i] + [0] * n
        for j in range(1, n + 1):
            c = p[j - 1]
            if c == '*':
                x = prev[j]
                y = cur[j - 1]
                cur[j] = x if x < y else y
            else:
                x = prev[j - 1] + (0 if (c == '?' or c == a) else 1)
                y = prev[j] + 1
                if y < x:
                    x = y
                y = cur[j - 1] + 1
                if y < x:
                    x = y
                cur[j] = x
        prev = cur
    return prev[n]
''',
    tests=[["abc", "a*c"], ["abc", "a?"], ["", "a?*"], ["xyz", "abc"], ["abcd", "b*"], ["", ""], ["", "***"], ["abc", ""], ["abc", "???"],
           ["abc", "*"], ["aaaa", "b*b"], ["hello", "h?l*o?"], ["abc", "*c?a*"]],
)
_r = rnd(9111)
p["tests"] += [
    [_rs(_r, "abc", 500, 500), _rs(_r, "abc?*", 500, 500)],
    [_rs(_r, "ab", 480, 480), "".join(_r.choice("ab??") for _ in range(250)) + "*" + "".join(_r.choice("ab?") for _ in range(100))],
    [_rs(_r, "abcdef", 300, 300), "*".join(_rs(_r, "abcdef", 3, 3) for _ in range(60))],
]


def _b_wp(s, pat):
    alpha = sorted(set(s) | {c for c in pat if c not in "?*"}) or ["a"]
    best = len(s) + len(pat)
    L = len(s)
    options = []
    for c in pat:
        if c == "*":
            options.append(["".join(x) for k in range(L + 1) for x in product(alpha, repeat=k)])
        elif c == "?":
            options.append(alpha)
        else:
            options.append([c])
    for combo in product(*options):
        d = _lev(s, "".join(combo))
        if d < best:
            best = d
    return best


def _g_wp(r):
    pat = _rs(r, "ab?*", 0, 4)
    while pat.count("*") > 2:
        pat = pat.replace("*", "a", 1)
    return [_rs(r, "ab", 0, 4), pat]


def _v_wp(tests):
    for t in tests:
        s, pat = t["args"]
        assert len(s) <= 500 and len(pat) <= 500
        assert all(c in "abcdefghijklmnopqrstuvwxyz" for c in s)
        assert all(c in "abcdefghijklmnopqrstuvwxyz?*" for c in pat)


CHECKS["min-edits-to-match-wildcard-pattern"] = (_b_wp, _g_wp, "exact")
VALIDATE["min-edits-to-match-wildcard-pattern"] = _v_wp
