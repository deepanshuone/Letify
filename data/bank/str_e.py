"""Problems: strings - substrings and subsequences. See data/lib.py for the registry."""
from itertools import product

from lib import add, rnd, CHECKS, VALIDATE, gen_arr  # noqa: F401

TOPIC = "Strings"
LET = "abcdefghijklmnopqrstuvwxyz"
MOD = 10 ** 9 + 7


def _rs(r, n, alpha="abc"):
    return "".join(r.choice(alpha) for _ in range(n))


def _is_sub(t, s):
    it = iter(s)
    return all(c in it for c in t)


def _lower(s):
    return all("a" <= c <= "z" for c in s)


# ---------------------------------------------------------------- EASY

p = add(
    id="min-chars-to-append-for-subsequence", title="Characters to Append for a Subsequence", diff="Easy", topic=TOPIC,
    fn="minAppendForSubsequence", params=[("s", "string"), ("t", "string")], ret="int", cmp="exact",
    desc='<p>You may append any number of lowercase letters to the <em>end</em> of the string <code>s</code>. Return the smallest number of letters you must append so that <code>t</code> becomes a subsequence of the resulting string.</p>'
         '<p>A subsequence is obtained by deleting zero or more characters without changing the order of the rest.</p>'
         '<p>For example, with <code>s = "abracadabra"</code> and <code>t = "arcade"</code> the letters <code>a r c a d</code> can already be found in order inside <code>s</code>, only the final <code>e</code> is missing, so the answer is <code>1</code>. With <code>s = "xyz"</code> and <code>t = "abc"</code> nothing matches, so the answer is <code>3</code>.</p>',
    constraints=["1 &le; s.length, t.length &le; 10,000", "Both strings consist of lowercase English letters"],
    hints=["If you append a copy of the unmatched tail of <code>t</code>, that tail is certainly a subsequence of the new string. The only question is how long the tail has to be.",
           "A longer matched prefix of <code>t</code> inside <code>s</code> means a shorter tail. Which prefix of <code>t</code> is the longest one that is a subsequence of <code>s</code>?",
           "Scan <code>s</code> once with a pointer <code>j</code> into <code>t</code>; whenever <code>s[i] == t[j]</code>, advance <code>j</code>. The answer is <code>len(t) - j</code>."],
    editorial=["Let <code>j</code> be the length of the longest prefix of <code>t</code> that is a subsequence of <code>s</code>. The remaining <code>len(t) - j</code> letters of <code>t</code> must come after everything in <code>s</code> that was used for the prefix; appending exactly those letters is always enough, so the answer is at most <code>len(t) - j</code>.",
               "It cannot be smaller: if fewer letters were appended, the matched part of <code>t</code> inside <code>s</code> would have to be longer than <code>j</code>, contradicting that <code>j</code> is the longest matchable prefix. The greedy scan (match the earliest possible position for every letter of <code>t</code>) finds that longest prefix. It runs in O(|s|) time and O(1) space."],
    time="O(|s|)", space="O(1)",
    solution='''def minAppendForSubsequence(s, t):
    j = 0
    for c in s:
        if j < len(t) and c == t[j]:
            j += 1
    return len(t) - j
''',
    tests=[["abracadabra", "arcade"], ["xyz", "abc"], ["hello", "hell"], ["a", "a"], ["a", "b"], ["abc", "a"], ["abc", "cba"],
           ["z", "zzzz"], ["aaaa", "aa"], ["ab", "ababab"], ["coaching", "coding"]],
)
_r = rnd(9501)
_s = _rs(_r, 9000, LET)
p["tests"].append([_s, _rs(_r, 9000, LET)])
p["tests"].append([_s, _s[::7]])
p["tests"].append(["a" * 10000, "a" * 9999 + "b"])


def b_append(s, t):
    for k in range(len(t) + 1):
        for x in product(sorted(set(t)), repeat=k):
            if _is_sub(t, s + "".join(x)):
                return k


def g_append(r):
    return [_rs(r, r.randint(1, 7)), _rs(r, r.randint(1, 5))]


def v_append(tests):
    for t in tests:
        s, u = t["args"]
        assert 1 <= len(s) <= 10000 and 1 <= len(u) <= 10000 and _lower(s) and _lower(u)


CHECKS["min-chars-to-append-for-subsequence"] = (b_append, g_append, "exact")
VALIDATE["min-chars-to-append-for-subsequence"] = v_append

p = add(
    id="largest-subsequence-lexicographic", title="Lexicographically Largest Subsequence", diff="Easy", topic=TOPIC,
    fn="largestSubsequence", params=[("s", "string")], ret="string", cmp="exact",
    desc='<p>Given a string <code>s</code>, return the lexicographically largest non-empty subsequence of <code>s</code>. A string is larger than another if at the first position where they differ it has the later letter, or if the other one is a proper prefix of it.</p>'
         '<p>For example, for <code>s = "abcab"</code> the answer is <code>"cb"</code>, for <code>s = "zzaz"</code> it is <code>"zzz"</code> and for <code>s = "cba"</code> it is <code>"cba"</code> itself.</p>',
    constraints=["1 &le; s.length &le; 10,000", "s consists of lowercase English letters"],
    hints=["The first letter of the answer should be the biggest letter of the whole string. Which occurrence of it should you take?",
           "Take every occurrence of the biggest letter: more copies make the answer longer, and a longer string beats its own prefix. Then repeat the idea on what is left after the last of them.",
           "Walk from the right and keep a letter exactly when it is at least as large as every letter already kept (equivalently, every letter to its right)."],
    editorial=["The answer must start with the maximum letter <code>m</code> of <code>s</code>; any answer starting with something smaller loses immediately. Taking <em>all</em> occurrences of <code>m</code> is better than taking fewer, because a string with more trailing copies of the same letter is larger than its prefix. After the last occurrence of <code>m</code>, we repeat the same reasoning on the remaining suffix.",
               "Putting it together, a letter belongs to the answer exactly when no letter strictly larger than it appears later in <code>s</code>. Scan from right to left, track the largest letter seen so far, keep the current letter if it is not smaller, then reverse the collected letters. O(n) time, O(n) space for the output."],
    time="O(n)", space="O(n)",
    solution='''def largestSubsequence(s):
    out = []
    best = ""
    for c in reversed(s):
        if c >= best:
            best = c
            out.append(c)
    return "".join(reversed(out))
''',
    tests=[["abcab"], ["zzaz"], ["cba"], ["a"], ["abc"], ["aaaa"], ["bab"], ["abababab"], ["zyxwvu"], ["azbycx"], ["mississippi"]],
)
_r = rnd(9502)
p["tests"].append([_rs(_r, 9000, LET)])
p["tests"].append([_rs(_r, 9000, "ab")])
p["tests"].append(["".join(sorted(_rs(_r, 8000, LET)))])


def b_largest(s):
    n = len(s)
    best = ""
    for mask in range(1, 1 << n):
        t = "".join(s[i] for i in range(n) if mask >> i & 1)
        if t > best:
            best = t
    return best


def g_largest(r):
    return [_rs(r, r.randint(1, 10), "abcd")]


def v_largest(tests):
    for t in tests:
        s = t["args"][0]
        assert 1 <= len(s) <= 10000 and _lower(s)
        assert _is_sub(t["expected"], s) and t["expected"]


CHECKS["largest-subsequence-lexicographic"] = (b_largest, g_largest, "exact")
VALIDATE["largest-subsequence-lexicographic"] = v_largest

# ---------------------------------------------------------------- MEDIUM

p = add(
    id="count-words-that-are-subsequences", title="Count Words That Are Subsequences", diff="Medium", topic=TOPIC,
    fn="countSubsequenceWords", params=[("s", "string"), ("words", "string")], ret="int", cmp="exact",
    desc='<p>You are given a long string <code>s</code> and a list of words, written as one string <code>words</code> in which the words are separated by commas, for example <code>"ace,aec,bb"</code>.</p>'
         '<p>Return how many words of the list are a subsequence of <code>s</code>. A word that appears several times in the list is counted once per appearance.</p>'
         '<p>For example, for <code>s = "abcde"</code> and <code>words = "a,bb,acd,ace,ace"</code> the answer is <code>4</code>: <code>a</code>, <code>acd</code> and both copies of <code>ace</code> fit, <code>bb</code> does not.</p>',
    constraints=["1 &le; s.length &le; 20,000", "The list has 1 to 1,500 words; each word has 1 to 20 lowercase letters", "s consists of lowercase letters; words contains lowercase letters and commas only, with no empty word"],
    hints=["Testing each word separately with two pointers is correct. Think about what it costs when there are many words and <code>s</code> is long.",
           "Scan <code>s</code> only once. For every word, remember which letter it is waiting for next, and group the words by that letter.",
           "When you read a letter <code>c</code> from <code>s</code>, take the whole group waiting for <code>c</code>, advance each word by one letter and put it into the group of its new waiting letter. Words that run out of letters are matches."],
    editorial=["The direct approach checks every word against <code>s</code> with two pointers, which costs O(|s|) per word in the worst case, so O(|s| &middot; W) overall. That is fine for small inputs but wasteful when <code>s</code> is long.",
               "Instead, process <code>s</code> a single time and keep 26 buckets. Bucket <code>c</code> holds the words (with a progress index) whose next unmatched letter is <code>c</code>. For each letter <code>c</code> of <code>s</code> we empty bucket <code>c</code>; each word in it advances one letter, and is either counted as matched (no letters left) or moved to the bucket of its new next letter. Every letter of every word is moved at most once, so the total work is O(|s| + total length of the words)."],
    time="O(|s| + total word length)", space="O(total word length)",
    solution='''def countSubsequenceWords(s, words):
    waiting = [[] for _ in range(26)]
    for w in words.split(","):
        waiting[ord(w[0]) - 97].append((w, 0))
    matched = 0
    for ch in s:
        bucket = waiting[ord(ch) - 97]
        if not bucket:
            continue
        waiting[ord(ch) - 97] = []
        for w, i in bucket:
            i += 1
            if i == len(w):
                matched += 1
            else:
                waiting[ord(w[i]) - 97].append((w, i))
    return matched
''',
    tests=[["abcde", "a,bb,acd,ace,ace"], ["abcde", "ace,aec,bb"], ["a", "a"], ["a", "b"], ["aaa", "a,aa,aaa,aaaa"], ["abc", "cba,abc,c,cc"],
           ["xyz", "x,y,z,xy,yz,xz,xyz,zyx"], ["banana", "ban,nan,bnn,aaa,aaaa,nna"], ["abab", "ab,ba,abab,baba,aab,bb"]],
)
_r = rnd(9503)


def _words(r, cnt, mx, alpha):
    return ",".join(_rs(r, r.randint(1, mx), alpha) for _ in range(cnt))


p["tests"].append([_rs(_r, 20000, "abc"), _words(_r, 1500, 20, "abc")])
p["tests"].append([_rs(_r, 20000, LET), _words(_r, 1500, 4, LET)])
_s = _rs(_r, 18000, "ab")
p["tests"].append([_s, ",".join(_s[::k][:20] for k in range(1, 1000, 2) if _s[::k][:20])])


def _lcs(a, b):
    dp = [[0] * (len(b) + 1) for _ in range(len(a) + 1)]
    for i in range(len(a)):
        for j in range(len(b)):
            dp[i + 1][j + 1] = dp[i][j] + 1 if a[i] == b[j] else max(dp[i][j + 1], dp[i + 1][j])
    return dp[-1][-1]


def b_cnt_words(s, words):
    return sum(1 for w in words.split(",") if _lcs(s, w) == len(w))


def g_cnt_words(r):
    return [_rs(r, r.randint(1, 12)), ",".join(_rs(r, r.randint(1, 4)) for _ in range(r.randint(1, 6)))]


def v_cnt_words(tests):
    for t in tests:
        s, words = t["args"]
        ws = words.split(",")
        assert 1 <= len(s) <= 20000 and _lower(s)
        assert 1 <= len(ws) <= 1500 and all(1 <= len(w) <= 20 and _lower(w) for w in ws)


CHECKS["count-words-that-are-subsequences"] = (b_cnt_words, g_cnt_words, "exact")
VALIDATE["count-words-that-are-subsequences"] = v_cnt_words

p = add(
    id="min-source-copies-for-target", title="Fewest Copies to Spell the Target", diff="Medium", topic=TOPIC,
    fn="minCopiesForSubsequence", params=[("source", "string"), ("target", "string")], ret="int", cmp="exact",
    desc='<p>You have an unlimited supply of copies of the string <code>source</code>. Write <code>k</code> copies one after another to form a long string. Return the smallest <code>k</code> such that <code>target</code> is a subsequence of that long string, or <code>-1</code> if no <code>k</code> works.</p>'
         '<p>For example, <code>source = "abc"</code> and <code>target = "abcbc"</code> need <code>2</code> copies: in <code>abcabc</code> the letters <code>a b c</code> come from the first copy and <code>b c</code> from the second. With <code>target = "acdbc"</code> the answer is <code>-1</code> because <code>d</code> never occurs in <code>source</code>.</p>',
    constraints=["1 &le; source.length &le; 3,000", "1 &le; target.length &le; 8,000", "Both strings consist of lowercase English letters"],
    hints=["If a letter of <code>target</code> does not occur in <code>source</code> at all, the answer is <code>-1</code>. Otherwise some finite number of copies always works (at most <code>target.length</code>).",
           "Match the letters of <code>target</code> greedily from left to right. For each letter, use its earliest possible position after the previous one; if there is none left in the current copy, start a new copy.",
           "Store the sorted positions of each letter in <code>source</code>. Keep the index of the next free position in the current copy and find the earliest occurrence of the needed letter at or after it with a binary search (or a precomputed next-occurrence table)."],
    editorial=["Greedy matching is optimal for subsequence tests: placing every letter at the earliest possible position never hurts later letters. We simulate this on the infinite repetition of <code>source</code>, tracking only the position inside the current copy and the number of copies started.",
               "For each letter of <code>target</code>, look up the sorted position list of that letter in <code>source</code>. Binary search for the first position at or after the current pointer. If there is none, a new copy begins and the first position of that letter is used; the copy counter grows by one. Otherwise we stay in the copy. The answer is the final copy counter, or <code>-1</code> if a letter is missing. Total O(|target| log |source|) time and O(|source|) space."],
    time="O(|target| log |source|)", space="O(|source|)",
    solution='''from bisect import bisect_left


def minCopiesForSubsequence(source, target):
    pos = {}
    for i, c in enumerate(source):
        pos.setdefault(c, []).append(i)
    copies = 1
    cur = 0
    for c in target:
        lst = pos.get(c)
        if lst is None:
            return -1
        k = bisect_left(lst, cur)
        if k == len(lst):
            copies += 1
            k = 0
        cur = lst[k] + 1
    return copies
''',
    tests=[["abc", "abcbc"], ["abc", "acdbc"], ["xyz", "xzyxz"], ["a", "a"], ["a", "aaaa"], ["abc", "cba"], ["ab", "ba"],
           ["aab", "bbaaabb"], ["abcde", "edcba"], ["zyx", "xyz"], ["abab", "babab"]],
)
_r = rnd(9504)
_src = _rs(_r, 3000, LET)
p["tests"].append([_src, _rs(_r, 8000, LET)])
p["tests"].append([_rs(_r, 2900, "abc") + "d", _rs(_r, 8000, "abcd")])
p["tests"].append(["".join(sorted(_src)), _rs(_r, 8000, "".join(sorted(set(_src))))])
p["tests"].append(["abc" * 1000, "cba" * 2666])


def b_copies(source, target):
    for k in range(1, len(target) + 1):
        if _is_sub(target, source * k):
            return k
    return -1


def g_copies(r):
    return [_rs(r, r.randint(1, 5), "abcd"), _rs(r, r.randint(1, 9), "abcd")]


def v_copies(tests):
    for t in tests:
        a, b = t["args"]
        assert 1 <= len(a) <= 3000 and 1 <= len(b) <= 8000 and _lower(a) and _lower(b)


CHECKS["min-source-copies-for-target"] = (b_copies, g_copies, "exact")
VALIDATE["min-source-copies-for-target"] = v_copies

p = add(
    id="shortest-non-subsequence-length", title="Shortest String That Is Not a Subsequence", diff="Medium", topic=TOPIC,
    fn="shortestMissingSubsequence", params=[("s", "string"), ("k", "int")], ret="int", cmp="exact",
    desc='<p>The alphabet consists of the first <code>k</code> lowercase letters (<code>a</code>, <code>b</code>, ... ). The string <code>s</code> uses only letters of this alphabet.</p>'
         '<p>Consider every string over this alphabet. Return the length of the shortest one that is <em>not</em> a subsequence of <code>s</code>.</p>'
         '<p>For example, with <code>k = 3</code> and <code>s = "abcab"</code> the answer is <code>2</code>: every single letter occurs in <code>s</code>, but <code>"cc"</code> does not. With <code>k = 2</code> and <code>s = "abab"</code> the answer is <code>3</code>, because all four strings of length 2 are subsequences, while <code>"aaa"</code> is not.</p>',
    constraints=["1 &le; s.length &le; 10,000", "1 &le; k &le; 26", "s uses only the first k lowercase letters (it does not have to use all of them)"],
    hints=["A string of length L is a non-subsequence if you cannot find it in order. Can you tell how long a string can be that is <em>guaranteed</em> to be found, whatever its letters are?",
           "Cut <code>s</code> from the left into blocks: each block ends as soon as it contains all <code>k</code> letters. Any single letter can be found inside one block.",
           "If you can cut out <code>m</code> such complete blocks, every string of length <code>m</code> is a subsequence (pick letter <code>i</code> from block <code>i</code>). The leftover tail misses some letter, so a string of length <code>m + 1</code> is not."],
    editorial=["Scan <code>s</code> from the left and keep the set of letters seen in the current block. As soon as the set has all <code>k</code> letters, close the block, increase a counter <code>m</code> and clear the set. The greedy cut gives the largest possible number of blocks.",
               "Every string of length <code>m</code> is a subsequence: take its i-th letter from the i-th block, which contains every letter. On the other hand, the leftover tail after the last block lacks some letter <code>x</code>. Take the string whose first <code>m</code> letters are the letters that closed the blocks, followed by <code>x</code>. Greedy matching of its first <code>m</code> letters ends exactly at the end of the last block, and the tail has no <code>x</code>, so this string of length <code>m + 1</code> is not a subsequence. Hence the answer is <code>m + 1</code>. Time O(n), space O(k)."],
    time="O(n)", space="O(k)",
    solution='''def shortestMissingSubsequence(s, k):
    seen = set()
    blocks = 0
    for c in s:
        seen.add(c)
        if len(seen) == k:
            blocks += 1
            seen.clear()
    return blocks + 1
''',
    tests=[["abcab", 3], ["abab", 2], ["aab", 2], ["a", 1], ["a", 2], ["aaa", 1], ["abc", 3], ["cba", 3], ["abcabc", 3], ["abcdefghijklmnopqrstuvwxyz", 26],
           ["bbbbb", 3], ["abbaab", 2]],
)
_r = rnd(9505)
p["tests"].append([_rs(_r, 9000, LET[:26]), 26])
p["tests"].append([_rs(_r, 10000, "abc"), 3])
p["tests"].append([_rs(_r, 10000, "ab"), 2])
p["tests"].append([LET * 380, 26])


def b_shortest(s, k):
    alpha = LET[:k]
    L = 1
    while True:
        for x in product(alpha, repeat=L):
            if not _is_sub("".join(x), s):
                return L
        L += 1


def g_shortest(r):
    k = r.randint(1, 3)
    return [_rs(r, r.randint(1, 7), LET[:k]), k]


def v_shortest(tests):
    for t in tests:
        s, k = t["args"]
        assert 1 <= len(s) <= 10000 and 1 <= k <= 26 and set(s) <= set(LET[:k])


CHECKS["shortest-non-subsequence-length"] = (b_shortest, g_shortest, "exact")
VALIDATE["shortest-non-subsequence-length"] = v_shortest

p = add(
    id="count-sorted-abc-subsequences", title="Count a-then-b-then-c Subsequences", diff="Medium", topic=TOPIC,
    fn="countSortedSubsequences", params=[("s", "string")], ret="int", cmp="exact",
    desc='<p>The string <code>s</code> contains only the letters <code>a</code>, <code>b</code> and <code>c</code>. Count the subsequences of <code>s</code> that consist of <strong>at least one</strong> <code>a</code>, followed by <strong>at least one</strong> <code>b</code>, followed by <strong>at least one</strong> <code>c</code> (such as <code>abc</code>, <code>aabbc</code> or <code>abcc</code>).</p>'
         '<p>Two subsequences are different if they use different sets of positions, even when they spell the same word. Return the count modulo <code>1,000,000,007</code>.</p>'
         '<p>For example, <code>s = "abc"</code> gives <code>1</code>, <code>s = "aabc"</code> gives <code>3</code> (the a-part is the first <code>a</code>, the second <code>a</code> or both, followed by the only <code>b</code> and <code>c</code>), and <code>s = "cba"</code> gives <code>0</code>.</p>',
    constraints=["1 &le; s.length &le; 10,000", "s consists only of the letters a, b and c"],
    hints=["Enumerating all subsequences is exponential. Try to count them as you scan the string once, using a few counters.",
           "Keep three counters: the number of subsequences of the form <code>a+</code>, of the form <code>a+b+</code>, and of the form <code>a+b+c+</code> seen so far.",
           "On an <code>a</code>: A = 2A + 1 (extend each old one or not, or start a new one). On a <code>b</code>: B = 2B + A. On a <code>c</code>: C = 2C + B. The answer is C."],
    editorial=["Let A, B, C be the number of subsequences of the prefix read so far that match the shapes <code>a+</code>, <code>a+b+</code> and <code>a+b+c+</code>. Reading a new letter changes only one of them.",
               "A new <code>a</code> can either extend any existing <code>a+</code> subsequence (A of them), stay out of every old one (those remain, A more), or start a fresh subsequence consisting of just this <code>a</code>: <code>A = 2A + 1</code>. A new <code>b</code> can extend an existing <code>a+b+</code> subsequence (B choices) or be placed after an <code>a+</code> subsequence to begin the b-part (A choices), plus the old ones stay: <code>B = 2B + A</code>. Similarly <code>C = 2C + B</code> for a <code>c</code>. All values are kept modulo 1,000,000,007. One pass, O(n) time, O(1) space."],
    time="O(n)", space="O(1)",
    solution='''def countSortedSubsequences(s):
    M = 1000000007
    a = b = c = 0
    for ch in s:
        if ch == "a":
            a = (2 * a + 1) % M
        elif ch == "b":
            b = (2 * b + a) % M
        else:
            c = (2 * c + b) % M
    return c
''',
    tests=[["abc"], ["aabc"], ["cba"], ["a"], ["aabbcc"], ["abcabc"], ["ccc"], ["aaabbbccc"], ["bac"], ["abbc"], ["acacbcbc"]],
)
_r = rnd(9506)
p["tests"].append([_rs(_r, 9000, "abc")])
p["tests"].append(["a" * 3000 + "b" * 3000 + "c" * 3000])
p["tests"].append(["abc" * 3300])


def b_abc(s):
    import re
    n = len(s)
    tot = 0
    for mask in range(1, 1 << n):
        t = "".join(s[i] for i in range(n) if mask >> i & 1)
        if re.fullmatch(r"a+b+c+", t):
            tot += 1
    return tot % MOD


def g_abc(r):
    return [_rs(r, r.randint(1, 12), "abc")]


def v_abc(tests):
    for t in tests:
        s = t["args"][0]
        assert 1 <= len(s) <= 10000 and set(s) <= set("abc")


CHECKS["count-sorted-abc-subsequences"] = (b_abc, g_abc, "exact")
VALIDATE["count-sorted-abc-subsequences"] = v_abc

p = add(
    id="longest-ideal-subsequence", title="Longest Ideal Subsequence", diff="Medium", topic=TOPIC,
    fn="longestIdealSubsequence", params=[("s", "string"), ("k", "int")], ret="int", cmp="exact",
    desc='<p>A subsequence of a lowercase string is called <em>ideal</em> if for every two neighbouring letters of the subsequence, their positions in the alphabet differ by at most <code>k</code>. For instance, with <code>k = 2</code>, <code>c</code> may be followed by <code>a</code>, <code>b</code>, <code>c</code>, <code>d</code> or <code>e</code>.</p>'
         '<p>Return the length of the longest ideal subsequence of <code>s</code>. The letters need not be different, and the difference <code>0</code> is always allowed.</p>'
         '<p>For example, <code>s = "acfgbd"</code> with <code>k = 2</code> gives <code>4</code> (for example <code>a c b d</code>), and <code>s = "abcd"</code> with <code>k = 0</code> gives <code>1</code>.</p>',
    constraints=["1 &le; s.length &le; 10,000", "0 &le; k &le; 25", "s consists of lowercase English letters"],
    hints=["Think of the best ideal subsequence that ends with a particular letter. How does it change when a new character arrives?",
           "Keep <code>dp[x]</code>, the length of the longest ideal subsequence seen so far that ends with letter <code>x</code> (26 values).",
           "For a new letter <code>x</code>: <code>dp[x] = 1 + max(dp[y])</code> over all letters <code>y</code> with <code>|x - y| &le; k</code>. The answer is the largest <code>dp</code> value at the end."],
    editorial=["A position-by-position DP over pairs of positions would be O(n&sup2;). The key observation is that the only thing about a subsequence that matters for extending it is its last letter. So it is enough to remember, for each of the 26 letters, the best length of an ideal subsequence ending in that letter.",
               "When the next character <code>x</code> of <code>s</code> comes, it can extend the best subsequence ending in any letter within distance <code>k</code> of <code>x</code> (including <code>x</code> itself), so the new best length ending in <code>x</code> is one more than the maximum of those values. Updating in place is safe because the new value for <code>x</code> is never smaller than the old one. The answer is the maximum entry. Time O(26 &middot; n), space O(26)."],
    time="O(26 n)", space="O(1)",
    solution='''def longestIdealSubsequence(s, k):
    dp = [0] * 26
    for ch in s:
        x = ord(ch) - 97
        dp[x] = max(dp[max(0, x - k):x + k + 1]) + 1
    return max(dp)
''',
    tests=[["acfgbd", 2], ["abcd", 0], ["a", 0], ["a", 25], ["az", 25], ["az", 24], ["zyxwv", 1], ["abcabc", 1], ["aaaaa", 0], ["badcfe", 1],
           ["acegik", 1], ["acegik", 2]],
)
_r = rnd(9507)
p["tests"].append([_rs(_r, 9000, LET), 3])
p["tests"].append([_rs(_r, 9000, LET), 0])
p["tests"].append([_rs(_r, 9500, LET), 25])
p["tests"].append([_rs(_r, 9000, "acegikmoqsuwy"), 2])


def b_ideal(s, k):
    n = len(s)
    best = 0
    for mask in range(1, 1 << n):
        t = [ord(s[i]) - 97 for i in range(n) if mask >> i & 1]
        if all(abs(t[i] - t[i + 1]) <= k for i in range(len(t) - 1)):
            best = max(best, len(t))
    return best


def g_ideal(r):
    return [_rs(r, r.randint(1, 11), "abcdefg"), r.randint(0, 6)]


def v_ideal(tests):
    for t in tests:
        s, k = t["args"]
        assert 1 <= len(s) <= 10000 and _lower(s) and 0 <= k <= 25


CHECKS["longest-ideal-subsequence"] = (b_ideal, g_ideal, "exact")
VALIDATE["longest-ideal-subsequence"] = v_ideal

p = add(
    id="max-removable-characters", title="Remove Characters, Keep the Pattern", diff="Medium", topic=TOPIC,
    fn="maxRemovable", params=[("s", "string"), ("p", "string"), ("removable", "int[]")], ret="int", cmp="exact",
    desc='<p>You are given strings <code>s</code> and <code>p</code> where <code>p</code> is a subsequence of <code>s</code>, and an array <code>removable</code> of distinct indices of <code>s</code>.</p>'
         '<p>You will delete characters of <code>s</code> in the order given by <code>removable</code>: first <code>s[removable[0]]</code>, then <code>s[removable[1]]</code>, and so on (the indices always refer to the <em>original</em> positions). Find the largest <code>k</code> such that after deleting the first <code>k</code> of these characters, <code>p</code> is still a subsequence of what remains of <code>s</code>.</p>'
         '<p>For example, <code>s = "abcbddddd"</code>, <code>p = "abcd"</code>, <code>removable = [3, 2, 1, 4, 5, 6]</code> gives <code>1</code>: after deleting position 3 the string <code>abcddddd</code> still contains <code>abcd</code>, but deleting position 2 as well removes the only <code>c</code>.</p>',
    constraints=["1 &le; p.length &le; s.length &le; 10,000", "0 &le; removable.length &le; s.length", "The values of removable are distinct and in [0, s.length - 1]", "p is a subsequence of s; both strings consist of lowercase letters"],
    hints=["Deleting more characters can only make it harder for <code>p</code> to survive. What does that monotonicity allow you to do?",
           "If you can delete the first <code>k</code> characters while keeping <code>p</code>, you can also delete any smaller number. So the feasible <code>k</code> values form a prefix of 0..len(removable).",
           "Binary search on <code>k</code>. To test a value, mark the first <code>k</code> indices as deleted and run the usual two-pointer subsequence check that skips deleted positions."],
    editorial=["If <code>p</code> is still a subsequence after deleting the first <code>k</code> listed characters, it is also a subsequence after deleting fewer of them (a smaller set of deletions leaves a superstring-in-order). So the predicate &ldquo;k deletions are fine&rdquo; is true for <code>k = 0</code> up to some threshold and false afterwards, which is exactly the shape binary search needs.",
               "To test a candidate <code>k</code> in O(n), precompute for each index of <code>s</code> the time at which it is deleted (its position in <code>removable</code>, or infinity). Then walk through <code>s</code>, skip every index with deletion time below <code>k</code>, and advance a pointer in <code>p</code> on equal letters. The check passes if the pointer reaches the end of <code>p</code>. Total O(n log n) time, O(n) space."],
    time="O(n log n)", space="O(n)",
    solution='''def maxRemovable(s, p, removable):
    inf = len(removable)
    when = [inf] * len(s)
    for idx, pos in enumerate(removable):
        when[pos] = idx

    def ok(k):
        j = 0
        for i, c in enumerate(s):
            if j < len(p) and when[i] >= k and c == p[j]:
                j += 1
        return j == len(p)

    lo, hi = 0, len(removable)
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if ok(mid):
            lo = mid
        else:
            hi = mid - 1
    return lo
''',
    tests=[["abcacb", "ab", [3, 1, 0]], ["abcbddddd", "abcd", [3, 2, 1, 4, 5, 6]], ["abcab", "abc", [0, 1, 2, 3, 4]], ["a", "a", []],
           ["aa", "a", [0]], ["aa", "a", [0, 1]], ["abab", "ab", [1, 0, 2, 3]], ["xxyxxyxx", "xy", [0, 1, 3, 4, 6, 7, 2]],
           ["abcde", "ace", [1, 3]], ["abcde", "ace", [1, 3, 0]]],
)
_r = rnd(9508)
for _n, _pl, _rl in ((6000, 2500, 6000), (5000, 40, 4999), (6000, 3000, 3000)):
    _s = _rs(_r, _n, "abc")
    _keep = sorted(_r.sample(range(_n), _pl))
    _pp = "".join(_s[i] for i in _keep)
    _perm = list(range(_n))
    _r.shuffle(_perm)
    p["tests"].append([_s, _pp, _perm[:_rl]])


def b_remove(s, p, removable):
    best = 0
    for k in range(len(removable) + 1):
        rs = set(removable[:k])
        t = "".join(c for i, c in enumerate(s) if i not in rs)
        if _is_sub(p, t):
            best = k
    return best


def g_remove(r):
    n = r.randint(1, 10)
    s = _rs(r, n, "ab")
    keep = sorted(r.sample(range(n), r.randint(1, n)))
    pp = "".join(s[i] for i in keep)
    rem = r.sample(range(n), r.randint(0, n - 1))
    return [s, pp, rem]


def v_remove(tests):
    for t in tests:
        s, pp, rem = t["args"]
        assert 1 <= len(pp) <= len(s) <= 10000 and _lower(s) and _lower(pp)
        assert len(rem) <= len(s) and len(set(rem)) == len(rem) and all(0 <= x < len(s) for x in rem)
        assert _is_sub(pp, s)


CHECKS["max-removable-characters"] = (b_remove, g_remove, "exact")
VALIDATE["max-removable-characters"] = v_remove

p = add(
    id="maximize-pattern-subsequence-count", title="Insert One Letter to Maximize Pattern Matches", diff="Medium", topic=TOPIC,
    fn="maxPatternSubsequences", params=[("s", "string"), ("pattern", "string")], ret="int", cmp="exact",
    desc='<p>The string <code>pattern</code> has exactly two letters. You must insert <strong>exactly one</strong> lowercase letter of your choice into <code>s</code>, at any position (including the very beginning or the very end).</p>'
         '<p>Count how many times <code>pattern</code> occurs as a subsequence of the new string, where two occurrences are different if they use different sets of positions. Return the largest count you can reach.</p>'
         '<p>For example, <code>s = "abdcdbc"</code>, <code>pattern = "ac"</code> gives <code>4</code> (insert an <code>a</code> at the front: 2 letters <code>a</code> times 2 letters <code>c</code>). For <code>s = "aabb"</code>, <code>pattern = "ab"</code> the answer is <code>6</code>, and for <code>s = "abaa"</code>, <code>pattern = "aa"</code> it is <code>6</code>.</p>',
    constraints=["1 &le; s.length &le; 20,000", "pattern.length = 2", "s and pattern consist of lowercase English letters", "The answer fits in a 32-bit integer for every allowed input"],
    hints=["Only the two letters of <code>pattern</code> can ever help. Which of them is worth inserting, and where?",
           "Inserting the first pattern letter is best at the very front (it pairs with every later copy of the second letter); inserting the second letter is best at the very end.",
           "Count the existing occurrences with one pass (keep the number of first letters seen so far). The answer is that count plus the larger of the two letter totals; if both pattern letters are equal and there are <code>c</code> of them, the answer is <code>c(c+1)/2</code>."],
    editorial=["Inserting a letter that is not part of the pattern changes nothing. Suppose the pattern is <code>xy</code> with <code>x &ne; y</code>. An inserted <code>x</code> forms a new occurrence with every <code>y</code> to its right, so it is best placed in front of everything and creates <code>count(y)</code> new occurrences. Symmetrically, an inserted <code>y</code> at the very end creates <code>count(x)</code> new ones. The result is <code>existing + max(count(x), count(y))</code>, where <code>existing</code> is computed in one scan by adding the number of <code>x</code> seen so far at every <code>y</code>.",
               "If the pattern is <code>xx</code>, the number of occurrences is the number of pairs of positions among the <code>c</code> letters <code>x</code>, which is <code>c(c-1)/2</code>; one more <code>x</code> (anywhere) gives <code>(c+1)c/2</code>. The input bound keeps all values in 32 bits. O(n) time, O(1) space."],
    time="O(n)", space="O(1)",
    solution='''def maxPatternSubsequences(s, pattern):
    x, y = pattern[0], pattern[1]
    if x == y:
        c = s.count(x)
        return c * (c + 1) // 2
    cx = cy = pairs = 0
    for ch in s:
        if ch == y:
            pairs += cx
            cy += 1
        if ch == x:
            cx += 1
    return pairs + max(cx, cy)
''',
    tests=[["abdcdbc", "ac"], ["aabb", "ab"], ["abaa", "aa"], ["a", "aa"], ["a", "ab"], ["b", "ab"], ["zzzz", "ab"], ["ba", "ab"], ["abab", "ba"],
           ["ccc", "cc"], ["xyxyxy", "xy"], ["qwerty", "ty"]],
)
_r = rnd(9509)
p["tests"].append([_rs(_r, 20000, "ab"), "ab"])
p["tests"].append(["a" * 10000 + "b" * 10000, "ab"])
p["tests"].append([_rs(_r, 20000, "abc"), "aa"])


def _count_pat(s, pat):
    cx = pairs = 0
    ways = [0, 0]
    # dynamic programming over positions: ways[0] = count of pat[0], ways[1] = count of pat
    for ch in s:
        if ch == pat[1]:
            ways[1] += ways[0]
        if ch == pat[0]:
            ways[0] += 1
    return ways[1]


def b_pattern(s, pattern):
    best = 0
    for i in range(len(s) + 1):
        for c in set(pattern) | {"a", "z"}:
            best = max(best, _count_pat(s[:i] + c + s[i:], pattern))
    return best


def g_pattern(r):
    return [_rs(r, r.randint(1, 10), "abcd"), _rs(r, 2, "abc")]


def v_pattern(tests):
    for t in tests:
        s, pat = t["args"]
        assert 1 <= len(s) <= 20000 and len(pat) == 2 and _lower(s) and _lower(pat)


CHECKS["maximize-pattern-subsequence-count"] = (b_pattern, g_pattern, "exact")
VALIDATE["maximize-pattern-subsequence-count"] = v_pattern

# ---------------------------------------------------------------- HARD

p = add(
    id="kth-distinct-subsequence", title="K-th Distinct Subsequence", diff="Hard", topic=TOPIC, tier="extra",
    fn="kthDistinctSubsequence", params=[("s", "string"), ("k", "int")], ret="string", cmp="exact",
    desc='<p>Look at all <strong>distinct non-empty strings</strong> that can be obtained as a subsequence of <code>s</code>, and sort them in dictionary order (a string comes before every longer string that starts with it). Return the <code>k</code>-th string in this order (counting from 1), or <code>"-"</code> if there are fewer than <code>k</code> such strings.</p>'
         '<p>For example, for <code>s = "aba"</code> the distinct subsequences in order are <code>a, aa, ab, aba, b, ba</code>, so <code>k = 4</code> gives <code>"aba"</code> and <code>k = 7</code> gives <code>"-"</code>.</p>',
    constraints=["1 &le; s.length &le; 3,000", "1 &le; k &le; 10<sup>9</sup>", "s consists of lowercase English letters"],
    hints=["Generating all subsequences is hopeless. Build the answer letter by letter instead, like looking up a word in a dictionary, and count how many strings start with each candidate letter.",
           "To count distinct subsequences without double counting, always match a letter at its <em>first</em> occurrence after the current position. Let <code>f[i]</code> be the number of distinct subsequences of <code>s[i:]</code> including the empty one; then <code>f[i] = 1 + sum over letters c of f[next(i, c) + 1]</code>.",
           "Walk through letters a..z at the current position: the strings starting with letter <code>c</code> number <code>f[next+1]</code>. If <code>k</code> is within that count, take <code>c</code> (the string <code>c</code> alone is the first of them), otherwise subtract the count and try the next letter. Cap the counts at about 2&middot;10<sup>9</sup> to keep numbers small."],
    editorial=["Precompute <code>nxt[i][c]</code>, the first index at or after <code>i</code> where letter <code>c</code> occurs (or -1). Any distinct subsequence corresponds to exactly one greedy embedding that always uses the earliest possible position, so counting along these embeddings counts each distinct string once. With <code>f[i]</code> as the number of distinct subsequences of the suffix <code>s[i:]</code> including the empty one, we get <code>f[n] = 1</code> and <code>f[i] = 1 + &sum;<sub>c</sub> f[nxt[i][c] + 1]</code>. These numbers explode, so cap them at a bound larger than the maximum <code>k</code>; capping is safe because we only compare them with <code>k</code>.",
               "Now descend like in a trie. At position <code>pos</code>, try letters in alphabetical order. The strings that begin with <code>c</code> (using its first occurrence <code>j</code>) number <code>f[j+1]</code>. If <code>k &le; f[j+1]</code>, the answer starts with <code>c</code>: if <code>k = 1</code> the string <code>c</code> itself is the answer, otherwise subtract 1 for it and continue from <code>pos = j + 1</code>. If not, subtract <code>f[j+1]</code> and try the next letter; if no letter is left at the top level, the answer is <code>\"-\"</code>. Table and counts cost O(26 n); the descent costs O(26 n) as well. Memory O(26 n)."],
    time="O(26 n)", space="O(26 n)",
    solution='''def kthDistinctSubsequence(s, k):
    n = len(s)
    CAP = 2 * 10 ** 9
    nxt = [None] * (n + 1)
    nxt[n] = [-1] * 26
    for i in range(n - 1, -1, -1):
        row = nxt[i + 1][:]
        row[ord(s[i]) - 97] = i
        nxt[i] = row
    f = [0] * (n + 1)
    f[n] = 1
    for i in range(n - 1, -1, -1):
        tot = 1
        for j in nxt[i]:
            if j >= 0:
                tot += f[j + 1]
        f[i] = min(tot, CAP)
    pos = 0
    res = []
    while True:
        for c in range(26):
            j = nxt[pos][c]
            if j < 0:
                continue
            cnt = f[j + 1]
            if k <= cnt:
                res.append(chr(97 + c))
                if k == 1:
                    return "".join(res)
                k -= 1
                pos = j + 1
                break
            k -= cnt
        else:
            return "-"
''',
    tests=[["aba", 4], ["aba", 7], ["aba", 1], ["aba", 6], ["a", 1], ["a", 2], ["abc", 7], ["abc", 8], ["aaa", 3], ["bab", 5], ["zyx", 4], ["abcabc", 20]],
)
_r = rnd(9510)
p["tests"].append(["a" * 3000, 2999])
p["tests"].append(["a" * 3000, 3001])
p["tests"].append([_rs(_r, 3000, LET), 10 ** 9])
p["tests"].append([_rs(_r, 3000, "ab"), 999999937])
p["tests"].append([_rs(_r, 45, "abc"), 12345678])


def b_kth(s, k):
    n = len(s)
    seen = set()
    for mask in range(1, 1 << n):
        seen.add("".join(s[i] for i in range(n) if mask >> i & 1))
    allv = sorted(seen)
    return allv[k - 1] if k <= len(allv) else "-"


def g_kth(r):
    s = _rs(r, r.randint(1, 10), "abc")
    return [s, r.randint(1, 60)]


def v_kth(tests):
    for t in tests:
        s, k = t["args"]
        assert 1 <= len(s) <= 3000 and _lower(s) and 1 <= k <= 10 ** 9
        e = t["expected"]
        assert e == "-" or (_is_sub(e, s) and _lower(e))
    ex = [t["expected"] for t in tests]
    assert "-" in ex and any(x != "-" for x in ex)


CHECKS["kth-distinct-subsequence"] = (b_kth, g_kth, "exact")
VALIDATE["kth-distinct-subsequence"] = v_kth

p = add(
    id="count-equal-frequency-subsequences", title="Subsequences With Equal Letter Counts", diff="Hard", topic=TOPIC, tier="extra",
    fn="countGoodSubsequences", params=[("s", "string")], ret="int", cmp="exact",
    desc='<p>Call a non-empty subsequence of <code>s</code> <em>balanced</em> if every letter that occurs in it occurs the same number of times. For example <code>"abab"</code> and <code>"c"</code> are balanced, while <code>"aab"</code> is not.</p>'
         '<p>Count the balanced subsequences of <code>s</code>. Two subsequences are different if they use different sets of positions, even if they spell the same word. Return the count modulo <code>1,000,000,007</code>.</p>'
         '<p>For example, <code>s = "aabb"</code> gives <code>11</code>: the 4 single letters, the 4 subsequences <code>ab</code> (one <code>a</code> and one <code>b</code>), and <code>aa</code>, <code>bb</code>, <code>aabb</code>.</p>',
    constraints=["1 &le; s.length &le; 10,000", "s consists of lowercase English letters"],
    hints=["Enumerating subsequences is exponential. Fix the common frequency <code>f</code> that every used letter must have and count the subsequences for that single <code>f</code>.",
           "For a fixed <code>f</code>, each letter independently either is not used, or contributes exactly <code>f</code> of its occurrences, in <code>C(cnt, f)</code> ways.",
           "For a fixed <code>f</code> the count is <code>(product over letters of (1 + C(cnt_c, f))) - 1</code>, the minus one removing the empty choice. Sum over <code>f = 1 .. max count</code>, with factorials precomputed modulo 1,000,000,007."],
    editorial=["Let <code>cnt_c</code> be the number of occurrences of letter <code>c</code> in <code>s</code>. Only these counts matter, not the order of letters, because a subsequence is just a choice of positions and being balanced depends only on how many positions are chosen per letter.",
               "Fix a frequency <code>f &ge; 1</code>. Every letter either contributes nothing, or exactly <code>f</code> chosen positions out of its <code>cnt_c</code>, which can be done in <code>C(cnt_c, f)</code> ways. Choices for different letters are independent, so the number of ways (including the all-empty choice) is the product of <code>(1 + C(cnt_c, f))</code>. Subtract one for the empty subsequence and sum over all <code>f</code> from 1 to the largest <code>cnt_c</code>. With precomputed factorials and inverse factorials the binomials cost O(1), so the total is O(max count &middot; 26) &le; O(26 n) time and O(n) space."],
    time="O(26 n)", space="O(n)",
    solution='''from collections import Counter


def countGoodSubsequences(s):
    M = 1000000007
    cnts = list(Counter(s).values())
    mx = max(cnts)
    fact = [1] * (mx + 1)
    for i in range(1, mx + 1):
        fact[i] = fact[i - 1] * i % M
    inv = [1] * (mx + 1)
    inv[mx] = pow(fact[mx], M - 2, M)
    for i in range(mx, 0, -1):
        inv[i - 1] = inv[i] * i % M
    total = 0
    for f in range(1, mx + 1):
        prod = 1
        for c in cnts:
            if c >= f:
                prod = prod * (1 + fact[c] * inv[f] % M * inv[c - f]) % M
        total += prod - 1
    return total % M
''',
    tests=[["aabb"], ["a"], ["ab"], ["aaa"], ["abc"], ["aabbcc"], ["abcabc"], ["aaab"], ["zzzzzzzzzz"], ["abacabad"], ["mississippi"]],
)
_r = rnd(9511)
p["tests"].append([_rs(_r, 9000, LET)])
p["tests"].append([_rs(_r, 9000, "abc")])
p["tests"].append(["a" * 9000])
p["tests"].append(["a" * 4500 + "b" * 4500])


def b_good(s):
    from collections import Counter
    n = len(s)
    tot = 0
    for mask in range(1, 1 << n):
        c = Counter(s[i] for i in range(n) if mask >> i & 1)
        if len(set(c.values())) == 1:
            tot += 1
    return tot % MOD


def g_good(r):
    return [_rs(r, r.randint(1, 12), "abcd")]


def v_good(tests):
    for t in tests:
        s = t["args"][0]
        assert 1 <= len(s) <= 10000 and _lower(s)


CHECKS["count-equal-frequency-subsequences"] = (b_good, g_good, "exact")
VALIDATE["count-equal-frequency-subsequences"] = v_good
