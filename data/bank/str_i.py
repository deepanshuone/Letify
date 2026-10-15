"""Problems: counting strings and combinatorial properties of strings. See data/lib.py for the registry."""
import math
from itertools import permutations, product

from lib import add, rnd, CHECKS, VALIDATE, gen_arr  # noqa: F401

TOPIC = "Strings"
LET = "abcdefghijklmnopqrstuvwxyz"
MOD = 10 ** 9 + 7


def _rs(r, n, alpha="abc"):
    return "".join(r.choice(alpha) for _ in range(n))


def _lower(s):
    return all("a" <= c <= "z" for c in s)


# ---------------------------------------------------------------- EASY

p = add(
    id="count-sorted-strings", title="Count Sorted Strings", diff="Easy", topic=TOPIC,
    fn="countSortedStrings", params=[("n", "int"), ("m", "int")], ret="int", cmp="exact",
    desc='<p>Consider strings of length <code>n</code> built only from the first <code>m</code> lowercase letters (<code>a</code>, <code>b</code>, ... in alphabet order). A string is <strong>sorted</strong> if every character is less than or equal to the character after it, for example <code>"aabc"</code>.</p><p>Return the number of sorted strings of length <code>n</code>, modulo <code>1,000,000,007</code>.</p><pre>n = 2, m = 3  ->  6   (aa, ab, ac, bb, bc, cc)\nn = 3, m = 2  ->  4   (aaa, aab, abb, bbb)</pre>',
    constraints=["1 &le; n &le; 5,000", "1 &le; m &le; 26", "The answer is returned modulo 1,000,000,007"],
    hints=["Count the strings by their last character: how many sorted strings of length <code>i</code> end in the letter <code>c</code>?",
           "A sorted string of length <code>i</code> ending in <code>c</code> is a sorted string of length <code>i - 1</code> ending in any letter <code>&le; c</code>, followed by <code>c</code>.",
           "That sum over letters <code>&le; c</code> is a prefix sum of the previous row, so each row is computed in O(m). (There is also a closed form with a binomial coefficient.)"],
    editorial=["Let <code>dp[c]</code> be the number of sorted strings of the current length that end with letter <code>c</code>. For length 1 every letter works, so all entries are 1. To extend to the next length, a string may end in <code>c</code> if the previous character was any letter up to <code>c</code>, so the new <code>dp[c]</code> is the sum of the old <code>dp[0..c]</code>, a running prefix sum. After <code>n - 1</code> such rounds, the answer is the sum of all entries.",
               "This takes O(n &middot; m) time and O(m) space. A sorted string is fully described by how many times each letter occurs, so the answer is also the number of ways to split <code>n</code> into <code>m</code> non-negative counts, which is the binomial coefficient <code>C(n + m - 1, m - 1)</code> (stars and bars); the DP is the safe way to compute it modulo a prime without modular inverses."],
    time="O(n * m)", space="O(m)",
    solution='''def countSortedStrings(n, m):
    MOD = 10 ** 9 + 7
    dp = [1] * m
    for _ in range(n - 1):
        run = 0
        for c in range(m):
            run = (run + dp[c]) % MOD
            dp[c] = run
    return sum(dp) % MOD
''',
    tests=[[2, 3], [3, 2], [1, 1], [1, 26], [5, 1], [2, 26], [10, 26], [26, 26], [100, 2], [1000, 26], [5000, 26], [4999, 13], [5000, 1]],
)


def b_sorted_strings(n, m):
    if m ** n <= 30000:
        return sum(1 for t in product(range(m), repeat=n) if all(t[i] <= t[i + 1] for i in range(n - 1))) % MOD
    return math.comb(n + m - 1, m - 1) % MOD


def g_sorted_strings(r):
    return [r.randint(1, 7), r.randint(1, 5)]


def v_sorted_strings(tests):
    for t in tests:
        n, m = t["args"]
        assert 1 <= n <= 5000 and 1 <= m <= 26


CHECKS["count-sorted-strings"] = (b_sorted_strings, g_sorted_strings, "exact")
VALIDATE["count-sorted-strings"] = v_sorted_strings

p = add(
    id="count-distinct-single-deletions", title="Distinct Results of One Deletion", diff="Easy", topic=TOPIC,
    fn="countDeletionResults", params=[("s", "string")], ret="int", cmp="exact",
    desc='<p>You must delete exactly one character from the string <code>s</code> (choose any position). Different positions can lead to the same resulting string.</p><p>Return the number of <strong>distinct</strong> strings that can be obtained this way. The empty string counts as a string when <code>s</code> has length 1.</p><pre>s = "aabbc"  ->  3   ("abbc", "aabc", "aabb")\ns = "abc"    ->  3\ns = "aaaa"   ->  1</pre>',
    constraints=["1 &le; s.length &le; 50,000", "s consists of lowercase English letters"],
    hints=["Deleting every position and storing the results in a set works for short strings, but each result costs O(n) to build.",
           "When do two different deletions give the same string? Look at deleting positions <code>i &lt; j</code> and compare what is left.",
           "They give the same string exactly when all characters from <code>i</code> to <code>j</code> are equal, so each block of equal adjacent letters contributes one result. Count the blocks."],
    editorial=["Delete position <code>i</code> versus position <code>j &gt; i</code>. The two results agree outside the range <code>[i, j]</code>. Inside it, the first result keeps <code>s[i+1..j]</code> and the second keeps <code>s[i..j-1]</code>. These are equal precisely when <code>s[i] = s[i+1] = ... = s[j]</code>. So deleting any character of a maximal block of equal letters yields the same string, and deleting from different blocks yields different strings.",
               "The answer is therefore the number of maximal runs of equal letters: one plus the number of positions where <code>s[i] != s[i-1]</code>. This is a single O(n) scan with O(1) extra space."],
    time="O(n)", space="O(1)",
    solution='''def countDeletionResults(s):
    count = 0
    for i, c in enumerate(s):
        if i == 0 or s[i - 1] != c:
            count += 1
    return count
''',
    tests=[["aabbc"], ["abc"], ["aaaa"], ["a"], ["ab"], ["aa"], ["abab"], ["aabaa"], ["zzzyyx"], ["abcabcabc"]],
)
_r = rnd(9101)
p["tests"].append([_rs(_r, 40000, "ab")])
p["tests"].append(["a" * 30000])
p["tests"].append([_rs(_r, 20000, LET)])
p["tests"].append(["".join(c * _r.randint(1, 6) for c in _rs(_r, 4000, "xyz"))])


def b_single_del(s):
    return len({s[:i] + s[i + 1:] for i in range(len(s))})


def g_single_del(r):
    return [_rs(r, r.randint(1, 10), "ab" if r.random() < 0.7 else "abc")]


def v_single_del(tests):
    for t in tests:
        s = t["args"][0]
        assert 1 <= len(s) <= 50000 and _lower(s)


CHECKS["count-distinct-single-deletions"] = (b_single_del, g_single_del, "exact")
VALIDATE["count-distinct-single-deletions"] = v_single_del

p = add(
    id="split-into-max-balanced-pieces", title="Split Into Maximum Balanced Pieces", diff="Easy", topic=TOPIC,
    fn="maxBalancedPieces", params=[("s", "string")], ret="int", cmp="exact",
    desc='<p>The string <code>s</code> contains only the letters <code>L</code> and <code>R</code>, and it has the same number of each. A string is <strong>balanced</strong> if it has the same number of <code>L</code> and <code>R</code>.</p><p>Cut <code>s</code> into consecutive non-empty pieces so that every piece is balanced. Return the largest possible number of pieces.</p><pre>s = "RLRRLLRLRL"  ->  4   ("RL" + "RRLL" + "RL" + "RL")\ns = "LLLRRR"      ->  1</pre>',
    constraints=["2 &le; s.length &le; 50,000", "s contains only <code>L</code> and <code>R</code>", "s has equally many <code>L</code> and <code>R</code> (so its length is even)"],
    hints=["A piece is balanced when its number of <code>L</code> equals its number of <code>R</code>. How can you track that while scanning from the left?",
           "Keep a running balance: +1 for <code>L</code>, -1 for <code>R</code>. A piece can end exactly where the balance returns to zero.",
           "Cut greedily at every position where the running balance is zero; cutting as early as possible can never reduce the number of pieces. Count those positions."],
    editorial=["Give <code>L</code> the value +1 and <code>R</code> the value -1 and keep a prefix sum. Pieces <code>s[a..b)</code> are balanced exactly when the prefix sum at <code>a</code> equals the prefix sum at <code>b</code>. Starting from prefix 0 at the front and ending at prefix 0 (the whole string is balanced), a valid cutting is a chain of positions with prefix sum 0.",
               "Using every position with prefix sum 0 as a cut gives the maximum number of pieces, since any valid cutting uses a subset of those positions and the pieces between consecutive zero positions are already balanced. So the answer is the number of times the running balance hits zero. One pass, O(n) time, O(1) space."],
    time="O(n)", space="O(1)",
    solution='''def maxBalancedPieces(s):
    balance = 0
    pieces = 0
    for c in s:
        balance += 1 if c == 'L' else -1
        if balance == 0:
            pieces += 1
    return pieces
''',
    tests=[["RLRRLLRLRL"], ["LLLRRR"], ["RL"], ["LR"], ["RLLR"], ["RRLL"], ["LLRRLR"], ["RLRLRLRL"], ["LRRLLRRL"]],
)
_r = rnd(9102)


def _bal(r, n):
    a = ["L"] * n + ["R"] * n
    r.shuffle(a)
    return "".join(a)


def _bal_blocks(r, blocks, mx):
    out = []
    for _ in range(blocks):
        h = r.randint(1, mx)
        a = ["L"] * h + ["R"] * h
        r.shuffle(a)
        # a random shuffle may split further; that is fine
        out.append("".join(a))
    return "".join(out)


p["tests"].append([_bal(_r, 5000)])
p["tests"].append([_bal_blocks(_r, 3000, 6)])
p["tests"].append(["L" * 25000 + "R" * 25000])
p["tests"].append(["LR" * 20000])


def b_balanced_pieces(s):
    n = len(s)
    best = [-10 ** 9] * (n + 1)
    best[0] = 0
    for i in range(1, n + 1):
        for j in range(i):
            seg = s[j:i]
            if best[j] >= 0 and seg.count("L") == seg.count("R"):
                best[i] = max(best[i], best[j] + 1)
    return best[n]


def g_balanced_pieces(r):
    return [_bal(r, r.randint(1, 6))]


def v_balanced_pieces(tests):
    for t in tests:
        s = t["args"][0]
        assert 2 <= len(s) <= 50000 and set(s) <= {"L", "R"}
        assert s.count("L") == s.count("R")


CHECKS["split-into-max-balanced-pieces"] = (b_balanced_pieces, g_balanced_pieces, "exact")
VALIDATE["split-into-max-balanced-pieces"] = v_balanced_pieces


# ---------------------------------------------------------------- MEDIUM

p = add(
    id="count-distinct-rearrangements", title="Count Distinct Rearrangements", diff="Medium", topic=TOPIC,
    fn="countRearrangements", params=[("s", "string")], ret="int", cmp="exact",
    desc='<p>Given a lowercase string <code>s</code>, count how many <strong>different strings</strong> can be produced by reordering its characters (the original order counts as one of them). Equal strings are counted once, even if they come from different orderings of identical letters.</p><p>Return the count modulo <code>1,000,000,007</code>.</p><pre>s = "aab"  ->  3   ("aab", "aba", "baa")\ns = "abc"  ->  6\ns = "aaaa" ->  1</pre>',
    constraints=["1 &le; s.length &le; 5,000", "s consists of lowercase English letters", "The answer is returned modulo 1,000,000,007"],
    hints=["If all letters were different, there would be <code>n!</code> orderings. What changes when a letter appears several times?",
           "Swapping two equal letters does not change the string, so every distinct string is counted <code>c!</code> times for a letter occurring <code>c</code> times (for each letter independently).",
           "The answer is <code>n! / (c<sub>a</sub>! c<sub>b</sub>! ...)</code>. Precompute factorials modulo the prime and divide using modular inverses (Fermat: <code>x<sup>p-2</sup></code>)."],
    editorial=["Count the orderings of the <code>n</code> positions as if every character were distinguishable: <code>n!</code>. A given resulting string corresponds to exactly <code>c<sub>1</sub>! &middot; c<sub>2</sub>! &middot; ...</code> of these orderings, since the occurrences of each letter can be permuted among their positions freely. So the number of different strings is the multinomial coefficient <code>n! / &prod; c<sub>i</sub>!</code>.",
               "Since the modulus is prime, division is multiplication by the modular inverse, computed with <code>pow(x, MOD - 2, MOD)</code>. Building <code>n!</code> takes O(n) multiplications, plus at most 26 inverses. Total O(n + 26 log MOD) time, O(1) extra space beyond the factorial loop."],
    time="O(n)", space="O(1)",
    solution='''def countRearrangements(s):
    MOD = 10 ** 9 + 7
    fact = [1] * (len(s) + 1)
    for i in range(1, len(s) + 1):
        fact[i] = fact[i - 1] * i % MOD
    cnt = [0] * 26
    for ch in s:
        cnt[ord(ch) - 97] += 1
    result = fact[len(s)]
    for c in cnt:
        result = result * pow(fact[c], MOD - 2, MOD) % MOD
    return result
''',
    tests=[["aab"], ["abc"], ["aaaa"], ["a"], ["ab"], ["aabb"], ["abcdefgh"], ["mississi"], ["zzzzzzzy"], ["aabbccdd"]],
)
_r = rnd(9103)
p["tests"].append([_rs(_r, 5000, LET)])
p["tests"].append([_rs(_r, 4000, "ab")])
p["tests"].append(["a" * 2500 + "b" * 2499 + "c"])
p["tests"].append([LET * 150 + "xyz"])


def b_rearr(s):
    return len(set(permutations(s))) % MOD


def g_rearr(r):
    return [_rs(r, r.randint(1, 8), LET[:r.randint(1, 4)])]


def v_rearr(tests):
    for t in tests:
        s = t["args"][0]
        assert 1 <= len(s) <= 5000 and _lower(s)


CHECKS["count-distinct-rearrangements"] = (b_rearr, g_rearr, "exact")
VALIDATE["count-distinct-rearrangements"] = v_rearr

p = add(
    id="rank-among-distinct-rearrangements", title="Rank Among Distinct Rearrangements", diff="Medium", topic=TOPIC,
    fn="rankOfString", params=[("s", "string")], ret="int", cmp="exact",
    desc='<p>List every <strong>distinct</strong> string that can be formed by reordering the letters of <code>s</code>, in dictionary (lexicographic) order, without repeats. Return the 1-based position of <code>s</code> itself in that list, modulo <code>1,000,000,007</code>.</p><pre>s = "bca"  ->  4   (abc, acb, bac, bca, cab, cba)\ns = "aba"  ->  2   (aab, aba, baa)\ns = "abc"  ->  1</pre>',
    constraints=["1 &le; s.length &le; 5,000", "s consists of lowercase English letters", "The answer is returned modulo 1,000,000,007"],
    hints=["Count how many rearrangements come <em>before</em> <code>s</code>. At the first position where a rearrangement differs from <code>s</code>, it must have a smaller letter.",
           "For position <code>i</code> and each smaller letter <code>c</code> still available, the remaining positions can be filled in (number of distinct rearrangements of the remaining letters after using <code>c</code>) ways.",
           "Keep the current multinomial <code>T = rem! / &prod; cnt!</code>. The count with letter <code>c</code> placed first is <code>T &middot; cnt[c] / rem</code>, so you only need one modular inverse per position and a sum of counts of smaller letters."],
    editorial=["Walk through <code>s</code> from left to right while maintaining the multiset of letters not yet used and <code>T</code>, the number of distinct arrangements of that multiset. Every arrangement smaller than <code>s</code> shares a prefix with <code>s</code> and then has a smaller letter at the first differing position. For position <code>i</code>, the arrangements that place letter <code>c &lt; s[i]</code> there number <code>T &middot; cnt[c] / rem</code>, where <code>rem</code> is the number of unused letters: of the <code>T</code> arrangements, a fraction <code>cnt[c] / rem</code> start with <code>c</code>.",
               "Add up those quantities over all smaller letters (that is <code>T &middot; (sum of cnt[c] for c &lt; s[i]) / rem</code>), then fix <code>s[i]</code>: <code>T</code> becomes <code>T &middot; cnt[s[i]] / rem</code>, the count of <code>s[i]</code> drops by one and <code>rem</code> by one. The rank is the number of smaller arrangements plus one.",
               "All divisions are by <code>rem &le; n &lt; MOD</code>, so modular inverses exist. The cost is O(n &middot; (26 + log MOD)) time, which is fast for n up to 5,000."],
    time="O(n * (26 + log MOD))", space="O(n)",
    solution='''def rankOfString(s):
    MOD = 10 ** 9 + 7
    n = len(s)
    fact = [1] * (n + 1)
    for i in range(1, n + 1):
        fact[i] = fact[i - 1] * i % MOD
    cnt = [0] * 26
    for ch in s:
        cnt[ord(ch) - 97] += 1
    total = fact[n]
    for c in cnt:
        total = total * pow(fact[c], MOD - 2, MOD) % MOD
    smaller_arrangements = 0
    rem = n
    for ch in s:
        idx = ord(ch) - 97
        inv = pow(rem, MOD - 2, MOD)
        less = sum(cnt[:idx])
        smaller_arrangements = (smaller_arrangements + total * less % MOD * inv) % MOD
        total = total * cnt[idx] % MOD * inv % MOD
        cnt[idx] -= 1
        rem -= 1
    return (smaller_arrangements + 1) % MOD
''',
    tests=[["bca"], ["aba"], ["abc"], ["a"], ["cba"], ["aabb"], ["bbaa"], ["dcba"], ["mississi"], ["zyxwvuts"]],
)
_r = rnd(9104)
p["tests"].append([_rs(_r, 5000, LET)])
_a = list("a" * 2000 + "b" * 1500 + "c" * 1000); _r.shuffle(_a)
p["tests"].append(["".join(_a)])
p["tests"].append(["".join(sorted("b" * 2500 + "a" * 2499 + "c"))[::-1]])
p["tests"].append([_rs(_r, 3000, "xyz")])


def b_rank(s):
    return sorted(set(permutations(s))).index(tuple(s)) % MOD + 1


def g_rank(r):
    return [_rs(r, r.randint(1, 8), LET[:r.randint(1, 4)])]


def v_rank(tests):
    for t in tests:
        s = t["args"][0]
        assert 1 <= len(s) <= 5000 and _lower(s)


CHECKS["rank-among-distinct-rearrangements"] = (b_rank, g_rank, "exact")
VALIDATE["rank-among-distinct-rearrangements"] = v_rank

p = add(
    id="count-distinct-tile-sequences", title="Count Distinct Tile Sequences", diff="Medium", topic=TOPIC,
    fn="countTileSequences", params=[("tiles", "string")], ret="int", cmp="exact",
    desc='<p>You own letter tiles, given as the string <code>tiles</code> (one tile per character). Form a <strong>non-empty</strong> sequence by placing some of the tiles (at most one use of each tile) in a row. Return how many <strong>different</strong> strings can be formed this way, modulo <code>1,000,000,007</code>.</p><pre>tiles = "aab"  ->  8   (a, b, aa, ab, ba, aab, aba, baa)\ntiles = "abc"  ->  15\ntiles = "zzz"  ->  3   (z, zz, zzz)</pre>',
    constraints=["1 &le; tiles.length &le; 600", "tiles consists of lowercase English letters", "The answer is returned modulo 1,000,000,007"],
    hints=["Fix how many tiles of each letter you use, say <code>j<sub>1</sub>, j<sub>2</sub>, ...</code>. How many different strings does that choice give?",
           "For a fixed choice with <code>L</code> tiles in total the answer is the multinomial <code>L! / (j<sub>1</sub>! j<sub>2</sub>! ...)</code>. So you need the sum of such terms over all choices, grouped by <code>L</code>.",
           "Process the letters one at a time. Keep <code>e[L] = (sum over choices with total L) of 1 / (j<sub>1</sub>! j<sub>2</sub>! ...)</code>. A letter with <code>c</code> tiles multiplies this polynomial by <code>1 + x + x<sup>2</sup>/2! + ... + x<sup>c</sup>/c!</code>. The final answer is the sum of <code>L! &middot; e[L]</code> for <code>L &ge; 1</code>."],
    editorial=["Choosing <code>j<sub>i</sub></code> tiles of letter <code>i</code> (with <code>0 &le; j<sub>i</sub> &le; c<sub>i</sub></code>) and arranging them gives <code>L! / &prod; j<sub>i</sub>!</code> distinct strings, where <code>L = &sum; j<sub>i</sub></code>. Different choices of the <code>j</code> vectors give different strings, because the letter counts of a string determine <code>j</code>. So the answer is the sum of those multinomials over all choices, excluding <code>L = 0</code>.",
               "That sum is the coefficient extraction of an exponential generating function: multiply the polynomials <code>&sum;<sub>j=0..c</sub> x<sup>j</sup>/j!</code> for every letter, and the answer is <code>&sum;<sub>L&ge;1</sub> L! &middot; [x<sup>L</sup>]</code>. Polynomial multiplication by a letter with <code>c</code> tiles costs O(L &middot; c), and the total over all letters is O(n<sup>2</sup>).",
               "Work modulo the prime with precomputed factorials and inverse factorials. A brute-force search over all sequences only scales to about 8 tiles."],
    time="O(n^2)", space="O(n)",
    solution='''def countTileSequences(tiles):
    MOD = 10 ** 9 + 7
    n = len(tiles)
    fact = [1] * (n + 1)
    for i in range(1, n + 1):
        fact[i] = fact[i - 1] * i % MOD
    inv = [pow(f, MOD - 2, MOD) for f in fact]
    counts = {}
    for ch in tiles:
        counts[ch] = counts.get(ch, 0) + 1
    e = [1]
    for c in counts.values():
        new = [0] * (len(e) + c)
        for k, v in enumerate(e):
            if v:
                for j in range(c + 1):
                    new[k + j] = (new[k + j] + v * inv[j]) % MOD
        e = new
    return sum(fact[L] * e[L] for L in range(1, len(e))) % MOD
''',
    tests=[["aab"], ["abc"], ["zzz"], ["a"], ["ab"], ["aabb"], ["aaabbc"], ["abcdefg"], ["aaaaaaa"]],
)
_r = rnd(9105)
p["tests"].append([_rs(_r, 600, LET)])
p["tests"].append([_rs(_r, 600, "abc")])
p["tests"].append(["a" * 300 + "b" * 299 + "c"])
p["tests"].append([LET * 22 + "abcdefghijklmnopqrstuvwx"])


def b_tiles(tiles):
    seen = set()
    for k in range(1, len(tiles) + 1):
        for t in permutations(tiles, k):
            seen.add(t)
    return len(seen) % MOD


def g_tiles(r):
    return [_rs(r, r.randint(1, 6), LET[:r.randint(1, 4)])]


def v_tiles(tests):
    for t in tests:
        s = t["args"][0]
        assert 1 <= len(s) <= 600 and _lower(s)


CHECKS["count-distinct-tile-sequences"] = (b_tiles, g_tiles, "exact")
VALIDATE["count-distinct-tile-sequences"] = v_tiles

p = add(
    id="count-strings-without-long-runs", title="Count Strings Without Long Runs", diff="Medium", topic=TOPIC,
    fn="countRunLimited", params=[("n", "int"), ("m", "int"), ("k", "int")], ret="int", cmp="exact",
    desc='<p>An alphabet has <code>m</code> distinct letters. Count the strings of length <code>n</code> over this alphabet in which <strong>no letter appears more than <code>k</code> times in a row</strong> (that is, every maximal block of equal letters has length at most <code>k</code>).</p><p>Return the count modulo <code>1,000,000,007</code>.</p><pre>n = 3, m = 2, k = 2  ->  6   (all 8 strings over {a, b} except "aaa" and "bbb")\nn = 2, m = 2, k = 1  ->  2   ("ab", "ba")\nn = 4, m = 1, k = 4  ->  1</pre>',
    constraints=["1 &le; n &le; 100,000", "1 &le; m &le; 1,000,000,000", "1 &le; k &le; 100,000", "The answer is returned modulo 1,000,000,007"],
    hints=["Look at the last block of equal letters. If it has length <code>j</code>, what is the letter just before it allowed to be, and how long can the prefix be?",
           "Let <code>h[i]</code> be the number of valid strings of length <code>i</code>. A string whose last block has length <code>j &lt; i</code> is a valid string of length <code>i - j</code> followed by <code>j</code> copies of one of the <code>m - 1</code> letters different from its last letter.",
           "So <code>h[i] = (m - 1) &middot; (h[i-1] + ... + h[i-k])</code>, restricted to indices <code>&ge; 1</code>, plus <code>m</code> if the whole string is one block (<code>i &le; k</code>). Maintain prefix sums of <code>h</code> to evaluate the window sum in O(1)."],
    editorial=["Classify a valid string of length <code>i</code> by the length <code>j</code> of its last block (1 &le; j &le; k). If <code>j = i</code> the string is a single repeated letter: <code>m</code> strings, allowed when <code>i &le; k</code>. Otherwise the part before the block is a valid string of length <code>i - j &ge; 1</code>, and the block can use any letter except the last letter of that part: <code>m - 1</code> choices. This gives <code>h[i] = (m - 1) &middot; &sum;<sub>j=1..min(k, i-1)</sub> h[i - j] + (m if i &le; k else 0)</code>.",
               "The inner sum is a sliding window over the previous <code>k</code> values, which a prefix-sum array answers in constant time: <code>pre[i-1] - pre[max(0, i-k-1)]</code>. The whole DP is O(n) time and O(n) space. Note the recurrence stays correct for <code>m = 1</code> (the factor <code>m - 1</code> is zero) and it never needs a modular inverse."],
    time="O(n)", space="O(n)",
    solution='''def countRunLimited(n, m, k):
    MOD = 10 ** 9 + 7
    pre = [0] * (n + 1)
    h = 0
    for i in range(1, n + 1):
        lo = max(0, i - k - 1)
        h = (m - 1) * (pre[i - 1] - pre[lo]) % MOD
        if i <= k:
            h = (h + m) % MOD
        pre[i] = (pre[i - 1] + h) % MOD
    return h % MOD
''',
    tests=[[3, 2, 2], [2, 2, 1], [4, 1, 4], [1, 1, 1], [1, 5, 1], [5, 1, 4], [5, 1, 5], [6, 3, 1], [10, 2, 3], [20, 26, 2],
           [100000, 1000000000, 1], [100000, 26, 5], [100000, 2, 50000], [99999, 3, 100000]],
)


def b_runs(n, m, k):
    if m ** n <= 30000:
        total = 0
        for t in product(range(m), repeat=n):
            run = 1
            ok = True
            for i in range(1, n):
                run = run + 1 if t[i] == t[i - 1] else 1
                if run > k:
                    ok = False
                    break
            if ok and k >= 1:
                total += 1
        return total % MOD
    # state DP on (current run length)
    dp = {1: m % MOD}
    for _ in range(n - 1):
        new = {}
        for run, v in dp.items():
            new[1] = (new.get(1, 0) + v * (m - 1)) % MOD
            if run + 1 <= k:
                new[run + 1] = (new.get(run + 1, 0) + v) % MOD
        dp = new
    return sum(dp.values()) % MOD if k >= 1 else 0


def g_runs(r):
    return [r.randint(1, 8), r.randint(1, 3), r.randint(1, 5)]


def v_runs(tests):
    for t in tests:
        n, m, k = t["args"]
        assert 1 <= n <= 100000 and 1 <= m <= 10 ** 9 and 1 <= k <= 100000


CHECKS["count-strings-without-long-runs"] = (b_runs, g_runs, "exact")
VALIDATE["count-strings-without-long-runs"] = v_runs

p = add(
    id="count-strings-with-k-equal-neighbors", title="Strings With Exactly K Equal Neighbors", diff="Medium", topic=TOPIC,
    fn="countEqualNeighbors", params=[("n", "int"), ("m", "int"), ("k", "int")], ret="int", cmp="exact",
    desc='<p>An alphabet has <code>m</code> distinct letters. Count the strings of length <code>n</code> over it that contain <strong>exactly <code>k</code> positions <code>i</code></strong> (with <code>0 &le; i &lt; n - 1</code>) where the character at <code>i</code> equals the character at <code>i + 1</code>.</p><p>Return the count modulo <code>1,000,000,007</code>.</p><pre>n = 3, m = 2, k = 1  ->  4   ("aab", "abb", "baa", "bba")\nn = 3, m = 2, k = 0  ->  2   ("aba", "bab")\nn = 3, m = 3, k = 2  ->  3   ("aaa", "bbb", "ccc")</pre>',
    constraints=["1 &le; n &le; 100,000", "1 &le; m &le; 1,000,000,000", "0 &le; k &le; n - 1", "The answer is returned modulo 1,000,000,007"],
    hints=["Think of the <code>n - 1</code> gaps between neighbouring characters. Each gap is either an 'equal' gap or a 'different' gap.",
           "Once you decide which <code>k</code> gaps are 'equal', the string is fixed by choosing its first character and then, for every 'different' gap, a letter distinct from the previous one.",
           "That gives <code>m</code> choices for the first letter, <code>m - 1</code> choices for each of the <code>n - 1 - k</code> different gaps, and <code>C(n - 1, k)</code> ways to pick the equal gaps. Evaluate it with factorials and a modular inverse."],
    editorial=["Describe a string by its first letter and, for each of the <code>n - 1</code> gaps, whether the neighbours are equal (the next letter is forced) or different (the next letter is any of the other <code>m - 1</code> letters). A pattern of gaps with exactly <code>k</code> equal gaps can be chosen in <code>C(n - 1, k)</code> ways, and each pattern yields <code>m &middot; (m - 1)<sup>n-1-k</sup></code> strings. Different (first letter, gap pattern, choices) triples give different strings, so the answer is <code>m &middot; C(n - 1, k) &middot; (m - 1)<sup>n-1-k</sup></code>.",
               "Compute the binomial with factorials up to <code>n</code> and one modular inverse, and the power by fast exponentiation. When <code>m = 1</code> the factor <code>(m-1)<sup>0</sup> = 1</code> only for <code>k = n - 1</code>, otherwise the power is zero, which correctly reports that a one-letter alphabet only produces the all-equal string. The running time is O(n + log n) with O(n) memory. A DP over (position, equal gaps so far) is O(n &middot; k) and too slow for the limits."],
    time="O(n)", space="O(n)",
    solution='''def countEqualNeighbors(n, m, k):
    MOD = 10 ** 9 + 7
    fact = [1] * n
    for i in range(1, n):
        fact[i] = fact[i - 1] * i % MOD
    binom = fact[n - 1] * pow(fact[k], MOD - 2, MOD) % MOD * pow(fact[n - 1 - k], MOD - 2, MOD) % MOD
    return m % MOD * binom % MOD * pow(m - 1, n - 1 - k, MOD) % MOD
''',
    tests=[[3, 2, 1], [3, 2, 0], [3, 3, 2], [1, 1, 0], [1, 7, 0], [2, 5, 0], [2, 5, 1], [4, 1, 3], [4, 1, 1], [10, 3, 4],
           [100000, 1000000000, 0], [100000, 26, 50000], [99999, 2, 99998], [100000, 1000000000, 99999], [77777, 3, 12345]],
)


def b_eq_neighbors(n, m, k):
    if m ** n <= 30000:
        return sum(1 for t in product(range(m), repeat=n) if sum(t[i] == t[i + 1] for i in range(n - 1)) == k) % MOD
    dp = [0] * (k + 2)
    dp[0] = m % MOD
    for _ in range(n - 1):
        new = [0] * (k + 2)
        for j in range(k + 1):
            if dp[j]:
                new[j] = (new[j] + dp[j] * (m - 1)) % MOD
                new[j + 1] = (new[j + 1] + dp[j]) % MOD
        dp = new
    return dp[k] % MOD


def g_eq_neighbors(r):
    n = r.randint(1, 8)
    return [n, r.randint(1, 3), r.randint(0, n - 1)]


def v_eq_neighbors(tests):
    for t in tests:
        n, m, k = t["args"]
        assert 1 <= n <= 100000 and 1 <= m <= 10 ** 9 and 0 <= k <= n - 1


CHECKS["count-strings-with-k-equal-neighbors"] = (b_eq_neighbors, g_eq_neighbors, "exact")
VALIDATE["count-strings-with-k-equal-neighbors"] = v_eq_neighbors


# ---------------------------------------------------------------- HARD

p = add(
    id="count-distinct-single-reversals", title="Distinct Results of One Reversal", diff="Hard", topic=TOPIC, tier="extra",
    fn="countReversalResults", params=[("s", "string")], ret="int", cmp="exact",
    desc='<p>You may choose any contiguous substring of <code>s</code> (of length 1 up to the whole string) and reverse it in place. Reversing a substring of length 1 changes nothing, so the original string is always one possible result.</p><p>Return the number of <strong>distinct</strong> strings that can be obtained with exactly one such reversal.</p><pre>s = "aab"  ->  3   ("aab", "baa", "aba")\ns = "abc"  ->  4   ("abc", "bac", "cba", "acb")\ns = "aaaa" ->  1</pre>',
    constraints=["1 &le; s.length &le; 60,000", "s consists of lowercase English letters"],
    hints=["There are about <code>n<sup>2</sup>/2</code> substrings, and you cannot afford to build each result. Think about which reversals produce the same string.",
           "Reversing <code>[i, j]</code> when <code>s[i] == s[j]</code> gives the same string as reversing the inner substring <code>[i+1, j-1]</code>. So only reversals whose two end characters differ can produce something new.",
           "Show that two different reversals with <code>s[i] != s[j]</code> always give different strings (the first and last changed positions are exactly <code>i</code> and <code>j</code>). The answer is <code>1 + (number of pairs i &lt; j with s[i] != s[j])</code>."],
    editorial=["Take a reversal of <code>[i, j]</code>. If <code>s[i] == s[j]</code>, the outer two characters swap with themselves, so the result equals the reversal of <code>[i+1, j-1]</code>. Repeating this argument, such a reversal equals either the original string (inner range empty or of length 1) or a reversal whose end characters differ. So every reachable string is either <code>s</code> or the result of a reversal with <code>s[i] != s[j]</code>.",
               "Now take a reversal of <code>[i, j]</code> with <code>s[i] != s[j]</code>. Position <code>i</code> receives <code>s[j]</code> and position <code>j</code> receives <code>s[i]</code>, so both change, while everything outside <code>[i, j]</code> is untouched. Hence the first and last positions where the result differs from <code>s</code> are exactly <code>i</code> and <code>j</code>, which means different pairs give different strings, and none of them equals <code>s</code>.",
               "The answer is therefore <code>1 + #{(i, j): i &lt; j, s[i] != s[j]} = 1 + C(n, 2) - &sum;<sub>letters</sub> C(cnt, 2)</code>, computed from 26 letter counts in O(n) time and O(1) space. The maximum, about 1.8 billion for n = 60,000, still fits in a signed 32-bit integer."],
    time="O(n)", space="O(1)",
    solution='''def countReversalResults(s):
    n = len(s)
    cnt = [0] * 26
    for ch in s:
        cnt[ord(ch) - 97] += 1
    result = 1 + n * (n - 1) // 2
    for c in cnt:
        result -= c * (c - 1) // 2
    return result
''',
    tests=[["aab"], ["abc"], ["aaaa"], ["a"], ["ab"], ["aa"], ["abab"], ["abcabc"], ["racecar"], ["zzzzzzzzza"]],
)
_r = rnd(9106)
p["tests"].append([_rs(_r, 60000, LET)])
p["tests"].append(["a" * 30000 + "b" * 30000])
p["tests"].append([_rs(_r, 8000, "abc")])


def b_reversal(s):
    n = len(s)
    return len({s[:i] + s[i:j + 1][::-1] + s[j + 1:] for i in range(n) for j in range(i, n)})


def g_reversal(r):
    return [_rs(r, r.randint(1, 10), LET[:r.randint(1, 4)])]


def v_reversal(tests):
    for t in tests:
        s = t["args"][0]
        assert 1 <= len(s) <= 60000 and _lower(s)


CHECKS["count-distinct-single-reversals"] = (b_reversal, g_reversal, "exact")
VALIDATE["count-distinct-single-reversals"] = v_reversal

p = add(
    id="count-strings-with-allowed-adjacent-pairs", title="Count Strings With Allowed Adjacent Pairs", diff="Hard", topic=TOPIC, tier="extra",
    fn="countAllowedStrings", params=[("n", "int"), ("k", "int"), ("pairs", "int[][]")], ret="int", cmp="exact",
    desc='<p>The alphabet has <code>k</code> letters, numbered <code>0</code> to <code>k - 1</code>. The array <code>pairs</code> lists the allowed ordered neighbours: each entry <code>[x, y]</code> means that letter <code>y</code> may directly follow letter <code>x</code>. Every pair appears at most once, and a pair that is not listed is forbidden.</p><p>Count the strings of length <code>n</code> in which every two adjacent letters form an allowed pair. Return the count modulo <code>1,000,000,007</code>. A string of length 1 has no neighbours, so all <code>k</code> single letters are valid.</p><pre>n = 3, k = 2, pairs = [[0,1],[1,0],[1,1]]  ->  5\n  (only the pair "aa" is forbidden: aba, abb, bab, bba, bbb)\nn = 5, k = 5, pairs = [[0,1],[1,0],[1,2],[2,0],[2,1],[2,3],[2,4],[3,2],[3,4],[4,0]]  ->  68</pre>',
    constraints=["1 &le; n &le; 1,000,000,000", "1 &le; k &le; 10", "1 &le; pairs.length &le; k &middot; k", "pairs[i] = [x, y] with 0 &le; x, y &lt; k; all pairs are distinct", "The answer is returned modulo 1,000,000,007"],
    hints=["For small <code>n</code> a DP works: let <code>ways[c]</code> be the number of valid strings of the current length ending with letter <code>c</code>, and move to the next length through the allowed pairs.",
           "That DP step is a fixed linear map: <code>new = A &middot; old</code> where <code>A</code> is the 0/1 matrix of allowed pairs. Doing it <code>n - 1</code> times is too slow for <code>n</code> up to a billion.",
           "Apply the matrix <code>n - 1</code> times with fast exponentiation (square the matrix, multiply it into the vector when the bit is set). With <code>k &le; 10</code> each matrix product is only 1,000 multiplications, and about 30 squarings suffice."],
    editorial=["Let <code>M[x][y] = 1</code> if the pair <code>[x, y]</code> is allowed. The number of valid strings of length <code>n</code> that start with letter <code>x</code> is the number of walks with <code>n - 1</code> steps starting at <code>x</code> in the directed graph with adjacency matrix <code>M</code>. Counting them step by step is the DP <code>v' = M v</code> starting from the all-ones vector (a string of length 1 is always valid), so the vector after <code>n - 1</code> steps is <code>M<sup>n-1</sup> &middot; 1</code> and the answer is the sum of its entries.",
               "Because powers of <code>M</code> commute, <code>M<sup>n-1</sup></code> can be applied with binary exponentiation: loop over the bits of <code>n - 1</code>, multiply the current vector by the current matrix when the bit is set, and square the matrix. That costs O(k<sup>3</sup> log n) time (about 30 &middot; 1,000 multiplications here) and O(k<sup>2</sup>) space, everything modulo 1,000,000,007.",
               "The second example is the well-known vowel rule set (a is followed only by e, e by a or i, i by anything except i, o by i or u, u only by a), which gives 68 strings of length 5."],
    time="O(k^3 log n)", space="O(k^2)",
    solution='''def countAllowedStrings(n, k, pairs):
    MOD = 10 ** 9 + 7
    M = [[0] * k for _ in range(k)]
    for x, y in pairs:
        M[x][y] = 1

    def mat_mul(A, B):
        C = [[0] * k for _ in range(k)]
        for i in range(k):
            Ai = A[i]
            Ci = C[i]
            for t in range(k):
                a = Ai[t]
                if a:
                    Bt = B[t]
                    for j in range(k):
                        Ci[j] += a * Bt[j]
            for j in range(k):
                Ci[j] %= MOD
        return C

    v = [1] * k
    e = n - 1
    while e:
        if e & 1:
            v = [sum(M[i][j] * v[j] for j in range(k)) % MOD for i in range(k)]
        M = mat_mul(M, M)
        e >>= 1
    return sum(v) % MOD
''',
    tests=[[3, 2, [[0, 1], [1, 0], [1, 1]]],
           [5, 5, [[0, 1], [1, 0], [1, 2], [2, 0], [2, 1], [2, 3], [2, 4], [3, 2], [3, 4], [4, 0]]],
           [1, 3, [[0, 1]]], [2, 3, [[0, 1], [2, 2]]], [4, 1, [[0, 0]]], [6, 2, [[0, 1], [1, 0]]], [5, 3, [[0, 1], [1, 2]]],
           [2, 4, [[0, 0], [1, 1], [2, 2], [3, 3]]], [30, 3, [[0, 0], [0, 1], [1, 2], [2, 0]]]],
)
_r = rnd(9107)
_full = [[x, y] for x in range(10) for y in range(10)]
p["tests"].append([1000000000, 10, _full])
_sub = [pr for pr in _full if _r.random() < 0.4]
p["tests"].append([1000000000, 10, _sub])
_sub = [pr for pr in _full if _r.random() < 0.15]
p["tests"].append([999999999, 10, _sub])
p["tests"].append([123456789, 6, [[0, 1], [1, 2], [2, 3], [3, 4], [4, 5], [5, 0], [0, 0], [3, 3]]])
p["tests"].append([1000, 4, [[0, 1], [1, 2], [2, 3], [3, 0], [0, 3], [1, 1]]])


def b_allowed(n, k, pairs):
    allowed = {tuple(pr) for pr in pairs}
    if n <= 6 and k <= 4:
        return sum(1 for t in product(range(k), repeat=n) if all((t[i], t[i + 1]) in allowed for i in range(n - 1))) % MOD
    ways = [1] * k
    for _ in range(n - 1):
        ways = [sum(ways[x] for x in range(k) if (x, y) in allowed) % MOD for y in range(k)]
    return sum(ways) % MOD


def g_allowed(r):
    k = r.randint(1, 4)
    allp = [[x, y] for x in range(k) for y in range(k)]
    pairs = [pr for pr in allp if r.random() < 0.5] or [allp[0]]
    return [r.randint(1, 8), k, pairs]


def v_allowed(tests):
    for t in tests:
        n, k, pairs = t["args"]
        assert 1 <= n <= 10 ** 9 and 1 <= k <= 10
        assert 1 <= len(pairs) <= k * k
        assert len({tuple(pr) for pr in pairs}) == len(pairs)
        assert all(len(pr) == 2 and 0 <= pr[0] < k and 0 <= pr[1] < k for pr in pairs)


CHECKS["count-strings-with-allowed-adjacent-pairs"] = (b_allowed, g_allowed, "exact")
VALIDATE["count-strings-with-allowed-adjacent-pairs"] = v_allowed

p = add(
    id="count-rearrangements-no-equal-neighbors", title="Rearrangements With No Equal Neighbors", diff="Hard", topic=TOPIC, tier="extra",
    fn="countNoEqualNeighbors", params=[("s", "string")], ret="int", cmp="exact",
    desc='<p>Given a lowercase string <code>s</code>, count the <strong>distinct</strong> strings that can be made by reordering its letters so that <strong>no two adjacent characters are equal</strong>. Equal strings are counted once.</p><p>Return the count modulo <code>1,000,000,007</code>.</p><pre>s = "aabb"  ->  2   ("abab", "baba")\ns = "aab"   ->  1   ("aba")\ns = "aaab"  ->  0\ns = "abc"   ->  6</pre>',
    constraints=["1 &le; s.length &le; 500", "s consists of lowercase English letters", "The answer is returned modulo 1,000,000,007"],
    hints=["Counting all arrangements and subtracting the bad ones directly is messy because bad pairs overlap. Think of inclusion-exclusion over where equal letters are glued together.",
           "Suppose a letter with <code>c</code> copies is cut into <code>g</code> blocks (compositions of <code>c</code> into <code>g</code> positive parts: <code>C(c-1, g-1)</code> ways). Arranging <code>G</code> blocks in total, where blocks of the same letter are identical, gives <code>G! / &prod; g<sub>i</sub>!</code> orders.",
           "Forcing blocks to be glued corresponds to the sign <code>(-1)<sup>c-g</sup></code>. Multiply, over all letters, the polynomials <code>&sum;<sub>g</sub> (-1)<sup>c-g</sup> C(c-1, g-1) x<sup>g</sup> / g!</code>; the answer is <code>&sum;<sub>G</sub> G! &middot; [x<sup>G</sup>]</code> of the product."],
    editorial=["For one letter occurring <code>c</code> times, call a <em>block</em> a maximal group of copies that were glued together in the inclusion-exclusion. If the copies are glued into exactly <code>g</code> blocks, there are <code>C(c-1, g-1)</code> ways to choose the block sizes, and the sign is <code>(-1)<sup>c-g</sup></code> (one factor of -1 for every glue that was used, and <code>c - g</code> glues are used). Then every arrangement of the <code>G = &sum; g</code> blocks, with blocks of equal letters indistinguishable, is counted by <code>G! / &prod; g<sub>i</sub>!</code>. Summing over all gluings gives exactly the arrangements with no equal neighbours: an arrangement that has equal neighbours is cancelled by the alternating signs.",
               "So the answer is <code>&sum;<sub>G</sub> G! &middot; [x<sup>G</sup>] &prod;<sub>letters</sub> f<sub>c</sub>(x)</code> where <code>f<sub>c</sub>(x) = &sum;<sub>g=1..c</sub> (-1)<sup>c-g</sup> C(c-1, g-1) x<sup>g</sup> / g!</code>. Multiply the polynomials one letter at a time (modulo the prime, using inverse factorials) in O(n<sup>2</sup>) total.",
               "An alternative formulation inserts the letters one by one into the current arrangement while tracking the number of equal adjacent pairs; it reaches the same recurrence with a somewhat heavier state. Brute force over permutations only works up to about 9 letters."],
    time="O(n^2)", space="O(n)",
    solution='''def countNoEqualNeighbors(s):
    MOD = 10 ** 9 + 7
    n = len(s)
    fact = [1] * (n + 1)
    for i in range(1, n + 1):
        fact[i] = fact[i - 1] * i % MOD
    inv = [pow(f, MOD - 2, MOD) for f in fact]

    def binom(a, b):
        return fact[a] * inv[b] % MOD * inv[a - b] % MOD

    counts = {}
    for ch in s:
        counts[ch] = counts.get(ch, 0) + 1
    poly = [1]
    for c in counts.values():
        f = [0] * (c + 1)
        for g in range(1, c + 1):
            term = binom(c - 1, g - 1) * inv[g] % MOD
            f[g] = term if (c - g) % 2 == 0 else (MOD - term) % MOD
        new = [0] * (len(poly) + c)
        for i, a in enumerate(poly):
            if a:
                for g in range(1, c + 1):
                    new[i + g] = (new[i + g] + a * f[g]) % MOD
        poly = new
    return sum(fact[G] * poly[G] for G in range(len(poly))) % MOD
''',
    tests=[["aabb"], ["aab"], ["aaab"], ["abc"], ["a"], ["aa"], ["ab"], ["aabbcc"], ["aaabbb"], ["aabbccdd"], ["abcdefg"]],
)
_r = rnd(9108)
p["tests"].append([_rs(_r, 500, LET)])
p["tests"].append([_rs(_r, 500, "ab")])
p["tests"].append(["a" * 250 + "b" * 250])
p["tests"].append(["a" * 251 + "b" * 249])
p["tests"].append([_rs(_r, 400, "abcde")])


def b_no_equal(s):
    from functools import lru_cache
    letters = sorted(set(s))
    start = tuple(s.count(c) for c in letters)

    @lru_cache(maxsize=None)
    def go(counts, last):
        if sum(counts) == 0:
            return 1
        total = 0
        for i, c in enumerate(counts):
            if c and i != last:
                nxt = counts[:i] + (c - 1,) + counts[i + 1:]
                total += go(nxt, i)
        return total

    return go(start, -1) % MOD


def g_no_equal(r):
    return [_rs(r, r.randint(1, 9), LET[:r.randint(1, 4)])]


def v_no_equal(tests):
    for t in tests:
        s = t["args"][0]
        assert 1 <= len(s) <= 500 and _lower(s)


CHECKS["count-rearrangements-no-equal-neighbors"] = (b_no_equal, g_no_equal, "exact")
VALIDATE["count-rearrangements-no-equal-neighbors"] = v_no_equal
