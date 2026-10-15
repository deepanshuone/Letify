"""Problems: greedy on strings (third greedy batch). See data/lib.py for the registry."""
from collections import Counter, deque
from functools import lru_cache
from itertools import groupby

from lib import add, rnd, CHECKS, VALIDATE, gen_arr  # noqa: F401

TOPIC = "Greedy"
LOW = "abcdefghijklmnopqrstuvwxyz"


def rs(r, n, alpha=LOW):
    return "".join(r.choice(alpha) for _ in range(n))


# ---------------------------------------------------------------- EASY

p = add(
    id="smallest-string-with-numeric-value", title="Smallest String With a Given Numeric Value", diff="Easy", topic=TOPIC,
    fn="smallestString", params=[("n", "int"), ("k", "int")], ret="string", cmp="exact",
    desc="<p>Give each lowercase letter a value equal to its position in the alphabet: <code>a = 1</code>, <code>b = 2</code>, ..., <code>z = 26</code>. The <em>numeric value</em> of a string is the sum of the values of its letters.</p><p>Given a length <code>n</code> and a target <code>k</code>, return the lexicographically smallest string of length <code>n</code> whose numeric value is exactly <code>k</code>. A valid string always exists for the given inputs.</p><pre>n = 3, k = 27  -> \"aay\"    (1 + 1 + 25)\nn = 5, k = 73  -> \"aaszz\"  (1 + 1 + 19 + 26 + 26)</pre>",
    constraints=["1 &le; n &le; 10,000", "n &le; k &le; 26 &middot; n"],
    hints=["To make a string small in dictionary order you want the leftmost letters to be as small as possible. What is the smallest letter you could ever put first?",
           "Start from <code>n</code> letters <code>a</code> (value <code>n</code>). The leftover <code>k - n</code> has to be absorbed by raising some letters, and each letter can absorb at most 25 more.",
           "Push the leftover into the rightmost positions: walk from the end, raise the current letter by <code>min(25, leftover)</code> and subtract that from the leftover until it reaches 0."],
    editorial=["Lexicographic order is decided by the first position where two strings differ, so the first letter matters most, then the second, and so on. That means we want as many <code>a</code>s as possible at the front and the large letters pushed to the back.",
               "Begin with the string of <code>n</code> letters <code>a</code>, which has value <code>n</code>, so <code>extra = k - n</code> remains to be distributed. Going from the last position to the first, each letter can take up to 25 extra (turning <code>a</code> into <code>z</code>). Give it <code>min(25, extra)</code> and reduce <code>extra</code>. Because <code>k &le; 26n</code> the extra is used up exactly.",
               "Why is this optimal? Any position that is left as small as possible allows the remaining positions to the right to carry the weight, and the suffix always has enough capacity (25 per letter). A smaller letter at an earlier position is therefore never blocked. The loop runs once over the string, O(n)."],
    time="O(n)", space="O(n)",
    solution='''def smallestString(n, k):
    res = ['a'] * n
    extra = k - n
    i = n - 1
    while extra > 0:
        add = min(25, extra)
        res[i] = chr(97 + add)
        extra -= add
        i -= 1
    return ''.join(res)
''',
    tests=[[1, 1], [1, 26], [3, 27], [5, 73], [2, 2], [2, 52], [4, 5], [3, 78], [6, 40], [10, 11], [7, 26 * 7 - 1],
           [10000, 10000], [10000, 130000], [9999, 237000]],
)


def b_numeric(n, k):
    @lru_cache(None)
    def best(n, k):
        if n == 0:
            return "" if k == 0 else None
        res = None
        for v in range(1, 27):
            if v <= k:
                rest = best(n - 1, k - v)
                if rest is not None:
                    cand = chr(96 + v) + rest
                    if res is None or cand < res:
                        res = cand
        return res

    return best(n, k)


def g_numeric(r):
    n = r.randint(1, 6)
    return [n, r.randint(n, 26 * n)]


def v_numeric(tests):
    for t in tests:
        n, k = t["args"]
        assert 1 <= n <= 10000 and n <= k <= 26 * n
        s = t["expected"]
        assert len(s) == n and sum(ord(c) - 96 for c in s) == k


CHECKS["smallest-string-with-numeric-value"] = (b_numeric, g_numeric, "exact")
VALIDATE["smallest-string-with-numeric-value"] = v_numeric


p = add(
    id="remove-chars-no-three-in-a-row", title="Remove Letters to Avoid Three in a Row", diff="Easy", topic=TOPIC,
    fn="avoidTriples", params=[("s", "string")], ret="string", cmp="exact",
    desc="<p>A string is called <em>smooth</em> if it never has three equal letters in a row. Delete the <strong>fewest possible</strong> letters from <code>s</code> so that the result is smooth, and return the resulting string. The remaining letters keep their original order.</p><p>It can be shown that the result is unique.</p><pre>\"leeetcode\"   -> \"leetcode\"\n\"aaabaaaa\"    -> \"aabaa\"\n\"abc\"         -> \"abc\"</pre>",
    constraints=["1 &le; s.length &le; 20,000", "s consists of lowercase English letters"],
    hints=["Only runs of identical letters can cause trouble. Think about what a single run of length <code>L</code> has to look like in the answer.",
           "Deleting a letter from the middle of a run or from its end gives the same text, so which letters you delete does not matter, only how many are kept per run.",
           "Scan left to right and append a letter to the answer unless the last two letters of the answer are already equal to it."],
    editorial=["Two letters that are different never interact, so the problem decomposes into maximal runs of the same letter. A run of length <code>L</code> must be shortened to at most two letters, and cutting it to exactly <code>min(L, 2)</code> deletes the fewest letters. Removing letters never merges two different runs into one, because the neighbours of a run are different letters and that run keeps at least one letter.",
               "Implementation: keep the answer in a list. For each character, check whether the last two entries both equal it; if so skip it, otherwise append. This is one pass over the string, O(n) time."],
    time="O(n)", space="O(n)",
    solution='''def avoidTriples(s):
    out = []
    for ch in s:
        if len(out) >= 2 and out[-1] == ch and out[-2] == ch:
            continue
        out.append(ch)
    return ''.join(out)
''',
    tests=[["leeetcode"], ["aaabaaaa"], ["abc"], ["a"], ["aaaaa"], ["aab"], ["aaabbbccc"], ["ababab"], ["zzzzzyyyzz"],
           ["bbbaaabbbaaa"], ["aabbaabb"]],
)
_r = rnd(7101)
_s = "".join(_r.choice("abc") * _r.randint(1, 7) for _ in range(3500))[:20000]
p["tests"].append([_s])
p["tests"].append(["q" * 20000])
p["tests"].append([rs(_r, 6000, "ab")])


def b_fancy(s):
    return "".join(ch * min(len(list(g)), 2) for ch, g in groupby(s))


def g_fancy(r):
    return rs(r, r.randint(1, 12), "ab" if r.random() < 0.5 else "abc")


def v_fancy(tests):
    for t in tests:
        s = t["args"][0]
        assert 1 <= len(s) <= 20000 and s.isalpha() and s.islower()
        e = t["expected"]
        assert all(len(list(g)) <= 2 for _, g in groupby(e))


CHECKS["remove-chars-no-three-in-a-row"] = (b_fancy, lambda r: [g_fancy(r)], "exact")
VALIDATE["remove-chars-no-three-in-a-row"] = v_fancy


p = add(
    id="min-triple-covers-for-x-marks", title="Cover Every X With Triples", diff="Easy", topic=TOPIC,
    fn="minTripleCovers", params=[("s", "string")], ret="int", cmp="exact",
    desc="<p>The string <code>s</code> consists of the letters <code>X</code> and <code>O</code>. In one move you choose <strong>three consecutive positions</strong> of <code>s</code> (the window must lie fully inside the string) and turn all three of them into <code>O</code>. Windows may overlap and may include letters that are already <code>O</code>.</p><p>Return the minimum number of moves needed so that <code>s</code> contains no <code>X</code> at all.</p><pre>\"XXOX\"     -> 2\n\"OOOO\"     -> 0\n\"XOOXOOX\"  -> 3</pre>",
    constraints=["3 &le; s.length &le; 20,000", "s contains only <code>X</code> and <code>O</code>"],
    hints=["Look at the leftmost <code>X</code>. Some move has to cover it.",
           "Among all windows that cover the leftmost <code>X</code>, the one that starts exactly at that <code>X</code> reaches furthest to the right, so it is never worse than the others.",
           "Scan left to right. On an <code>X</code> at index <code>i</code>, count one move and jump to <code>i + 3</code>; on an <code>O</code> move to <code>i + 1</code>."],
    editorial=["Consider the first <code>X</code> in the string at index <code>i</code>. Every valid solution contains a window that covers <code>i</code>, and since there is no <code>X</code> before <code>i</code>, a window starting at <code>i</code> clears three positions that matter, while a window starting earlier wastes cells on its left. Exchange argument: replace that window by the one starting at <code>i</code>; everything it covered that is still relevant (positions &ge; i) stays covered.",
               "So the algorithm is: scan; whenever an <code>X</code> is seen, count a move and skip the next two positions. If the window would run past the end of the string it can be slid left without covering fewer <code>X</code>s, because the string has at least three characters, so the count is unaffected. Time is O(n), space O(1)."],
    time="O(n)", space="O(1)",
    solution='''def minTripleCovers(s):
    moves = 0
    i = 0
    n = len(s)
    while i < n:
        if s[i] == 'X':
            moves += 1
            i += 3
        else:
            i += 1
    return moves
''',
    tests=[["XXOX"], ["OOOO"], ["XOOXOOX"], ["XXX"], ["OXO"], ["XOO"], ["OOX"], ["XXXXXXXX"], ["XOXOXOXOX"], ["OXXOOXXO"],
           ["XOOOOOOX"]],
)
_r = rnd(7102)
p["tests"].append(["".join(_r.choice("XO") for _ in range(20000))])
p["tests"].append(["X" * 20000])
p["tests"].append(["".join("X" if _r.random() < 0.08 else "O" for _ in range(15000))])


def b_cover(s):
    n = len(s)
    start = sum(1 << i for i, ch in enumerate(s) if ch == "X")
    seen = {start}
    q = deque([(start, 0)])
    while q:
        m, d = q.popleft()
        if m == 0:
            return d
        for w in range(n - 2):
            nm = m & ~(7 << w)
            if nm not in seen:
                seen.add(nm)
                q.append((nm, d + 1))


def g_cover(r):
    return "".join(r.choice("XO") for _ in range(r.randint(3, 11)))


def v_cover(tests):
    for t in tests:
        s = t["args"][0]
        assert 3 <= len(s) <= 20000 and set(s) <= set("XO")


CHECKS["min-triple-covers-for-x-marks"] = (b_cover, lambda r: [g_cover(r)], "exact")
VALIDATE["min-triple-covers-for-x-marks"] = v_cover


# ---------------------------------------------------------------- MEDIUM

p = add(
    id="break-palindrome-smallest", title="Break a Palindrome Minimally", diff="Medium", topic=TOPIC,
    fn="breakPalindrome", params=[("s", "string")], ret="string", cmp="exact",
    desc="<p>You are given a palindrome <code>s</code> of lowercase letters. Replace <strong>exactly one</strong> character with any lowercase letter so that the new string is <strong>not</strong> a palindrome, and make the new string the lexicographically smallest one possible.</p><p>Return that string. If it is impossible to make <code>s</code> a non-palindrome with one replacement, return the single character <code>-</code>.</p><pre>\"abccba\"  -> \"aaccba\"\n\"aaa\"     -> \"aab\"\n\"a\"       -> \"-\"</pre>",
    constraints=["1 &le; s.length &le; 20,000", "s consists of lowercase English letters", "s is a palindrome"],
    hints=["A string of length 1 is always a palindrome. What about every longer palindrome - can you always break it?",
           "To make the result small you want to lower an early character, ideally to <code>a</code>. But the change must actually destroy the symmetry.",
           "Look at the first half only (not the middle character of an odd-length string, since changing it never breaks a palindrome). The first character there that is not <code>a</code> becomes <code>a</code>. If every character in the first half is already <code>a</code>, change the last character to <code>b</code>."],
    editorial=["Changing the middle letter of an odd palindrome keeps it a palindrome, so only the positions in the first half and their mirrors are useful. A change at index <code>i</code> in the first half breaks the palindrome as long as the new letter differs from its mirror <code>s[n-1-i]</code>.",
               "To get the smallest result, change the leftmost position where a decrease is possible. In the first half, the first letter that is not <code>a</code> can be lowered to <code>a</code>, and the mirror still holds the old, non-<code>a</code> letter, so the string is no longer a palindrome. If the whole first half consists of <code>a</code>s, then (as the string is a palindrome) the whole string is <code>a</code>s apart from possibly the middle. No decrease is possible, so the smallest legal change is to raise the very last character to <code>b</code>, which makes the string larger as late as possible. Length 1 has no valid change.",
               "One pass over half the string: O(n) time."],
    time="O(n)", space="O(n)",
    solution='''def breakPalindrome(s):
    n = len(s)
    if n == 1:
        return '-'
    for i in range(n // 2):
        if s[i] != 'a':
            return s[:i] + 'a' + s[i + 1:]
    return s[:-1] + 'b'
''',
    tests=[["abccba"], ["a"], ["aa"], ["aaa"], ["aba"], ["z"], ["zz"], ["aza"], ["abba"], ["racecar"], ["aabaa"], ["bab"],
           ["aaaabaaaa"]],
)
_r = rnd(7103)
_h = rs(_r, 6000, "bcd")
p["tests"].append([_h + _h[::-1]])
_h = "a" * 6000
p["tests"].append([_h + "c" + _h[::-1]])
_h = "a" * 6000 + "b"
p["tests"].append([_h + _h[::-1][1:]])


def b_break(s):
    best = None
    for i in range(len(s)):
        for c in LOW:
            t = s[:i] + c + s[i + 1:]
            if c != s[i] and t != t[::-1] and (best is None or t < best):
                best = t
    return best if best is not None else "-"


def g_break(r):
    n = r.randint(1, 9)
    h = rs(r, (n + 1) // 2, "ab" if r.random() < 0.6 else "abc")
    return [h + h[::-1][n % 2:]]


def v_break(tests):
    for t in tests:
        s = t["args"][0]
        assert 1 <= len(s) <= 20000 and s == s[::-1] and s.islower()


CHECKS["break-palindrome-smallest"] = (b_break, g_break, "exact")
VALIDATE["break-palindrome-smallest"] = v_break


p = add(
    id="longest-happy-string-length", title="Longest String Without Three Equal Letters", diff="Medium", topic=TOPIC,
    tier="extra", fn="longestHappyLength", params=[("a", "int"), ("b", "int"), ("c", "int")], ret="int", cmp="exact",
    desc="<p>You have <code>a</code> letters <code>A</code>, <code>b</code> letters <code>B</code> and <code>c</code> letters <code>C</code>. Build a string using <strong>at most</strong> that many of each letter (you do not have to use all of them) such that no letter appears three times in a row.</p><p>Return the maximum possible length of such a string.</p><pre>a = 1, b = 1, c = 7  -> 8    (for example \"CCACCBCC\")\na = 7, b = 0, c = 0  -> 2    (\"AA\")\na = 2, b = 2, c = 1  -> 5</pre>",
    constraints=["0 &le; a, b, c &le; 10,000", "a + b + c &ge; 1"],
    hints=["Try building the string one letter at a time. Which letter is the most valuable to keep available for later?",
           "A letter with many copies left is the one in danger of being stranded at the end, so use the letter with the most copies left whenever it is allowed.",
           "At each step take the letter with the largest remaining count, except when it is the letter just placed twice in a row; then take the next best letter. Stop when no letter can be placed."],
    editorial=["Greedy: always place the letter with the largest remaining count, unless that would create three equal letters in a row, in which case place the letter with the second largest count. If that one is also unavailable (count 0), stop.",
               "Why it works: the only way letters get wasted is that one letter has so many copies left that the others cannot separate them. Spending the most abundant letter as early as the rules allow keeps the supply of separators balanced. Each step costs O(1) because there are only three letters, so the total time is O(a + b + c).",
               "There is also a closed form: with counts sorted as x &ge; y &ge; z, if x &le; 2(y + z + 1) every letter can be used and the answer is x + y + z; otherwise the largest letter fills every gap between groups of two and the answer is 3(y + z) + 2. The simulation is easier to trust and to adapt."],
    time="O(a + b + c)", space="O(1)",
    solution='''def longestHappyLength(a, b, c):
    cnt = [a, b, c]
    last = -1
    run = 0
    total = 0
    while True:
        order = sorted((0, 1, 2), key=lambda i: -cnt[i])
        picked = -1
        for i in order:
            if cnt[i] == 0:
                break
            if i == last and run == 2:
                continue
            picked = i
            break
        if picked < 0:
            return total
        cnt[picked] -= 1
        total += 1
        if picked == last:
            run += 1
        else:
            last = picked
            run = 1
''',
    tests=[[1, 1, 7], [7, 0, 0], [2, 2, 1], [0, 0, 1], [1, 0, 0], [0, 5, 5], [3, 3, 3], [10, 1, 1], [4, 1, 0], [2, 7, 2],
           [10000, 10000, 10000], [10000, 1, 1], [9000, 100, 50], [5000, 2500, 2501]],
)


def b_happy(a, b, c):
    @lru_cache(None)
    def f(a, b, c, last, run):
        best = 0
        cnt = [a, b, c]
        for i in range(3):
            if cnt[i] == 0 or (i == last and run == 2):
                continue
            cnt[i] -= 1
            best = max(best, 1 + f(cnt[0], cnt[1], cnt[2], i, run + 1 if i == last else 1))
            cnt[i] += 1
        return best

    return f(a, b, c, -1, 0)


def g_happy(r):
    while True:
        a = [r.randint(0, 7) for _ in range(3)]
        if sum(a) >= 1:
            return a


def v_happy(tests):
    for t in tests:
        a, b, c = t["args"]
        assert 0 <= a <= 10000 and 0 <= b <= 10000 and 0 <= c <= 10000 and a + b + c >= 1
        x, y, z = sorted((a, b, c), reverse=True)
        want = x + y + z if x <= 2 * (y + z + 1) else 3 * (y + z) + 2
        assert t["expected"] == want


CHECKS["longest-happy-string-length"] = (b_happy, g_happy, "exact")
VALIDATE["longest-happy-string-length"] = v_happy


p = add(
    id="min-buckets-for-houses", title="Minimum Buckets for Houses", diff="Medium", topic=TOPIC,
    tier="extra", fn="minBuckets", params=[("street", "string")], ret="int", cmp="exact",
    desc="<p>The string <code>street</code> describes a row of plots. A plot is either a house <code>H</code> or an empty plot <code>.</code>. You may put a water bucket on any empty plot (at most one per plot).</p><p>A house is served if there is a bucket on the plot immediately to its left or immediately to its right. Return the minimum number of buckets needed so that <strong>every</strong> house is served, or <code>-1</code> if that cannot be done.</p><pre>\"H..H\"    -> 2\n\".H.H.\"   -> 1\n\".HHH.\"   -> -1</pre><p>In the second example a single bucket on the middle plot serves both houses.</p>",
    constraints=["1 &le; street.length &le; 20,000", "street contains only <code>H</code> and <code>.</code>"],
    hints=["When is the answer <code>-1</code>? Look at a house whose both neighbours are houses or walls.",
           "Process houses from left to right. For the leftmost unserved house, a bucket on its right neighbour is at least as good as one on its left neighbour. Why?",
           "For an unserved house at <code>i</code>: if <code>i+1</code> is empty, put a bucket there (it also serves a house at <code>i+2</code>, so jump to <code>i+3</code>); else if <code>i-1</code> is empty, put a bucket there; otherwise return <code>-1</code>."],
    editorial=["Sweep from left to right. Whenever you meet a house that is not yet served, you must place a bucket next to it. Everything to its left is already served, so a bucket on the left neighbour can only help this one house. A bucket on the right neighbour also helps the house at <code>i + 2</code> if there is one. Hence the right neighbour is never worse (exchange argument), and we use the left one only when the right one is blocked.",
               "Implementation: at a house at index <code>i</code>, if <code>i + 1</code> exists and is <code>.</code>, add a bucket and move to <code>i + 3</code> (the plot <code>i + 2</code>, if a house, is served). Otherwise if <code>i &gt; 0</code> and <code>i - 1</code> is <code>.</code>, add a bucket and move to <code>i + 1</code>; if neither neighbour is empty return <code>-1</code>. A left-neighbour bucket is never placed on a plot that already holds one, because a bucket placed to the right of the earlier house makes us skip the next house. O(n) time, O(1) space."],
    time="O(n)", space="O(1)",
    solution='''def minBuckets(street):
    n = len(street)
    buckets = 0
    i = 0
    while i < n:
        if street[i] == 'H':
            if i + 1 < n and street[i + 1] == '.':
                buckets += 1
                i += 3
            elif i > 0 and street[i - 1] == '.':
                buckets += 1
                i += 1
            else:
                return -1
        else:
            i += 1
    return buckets
''',
    tests=[["H..H"], [".H.H."], [".HHH."], ["H"], ["HH"], ["."], [".H."], ["H.H"], ["HH.HH"], [".HH."], ["H.H.H.H"], ["..H.."], [".H.HH.H."]],
)
_r = rnd(7104)
p["tests"].append(["".join(_r.choice("H..") for _ in range(8000))])
p["tests"].append([".H" * 6000 + "."])
p["tests"].append(["H.H." * 3000])


def b_buckets(street):
    n = len(street)
    spots = [i for i, ch in enumerate(street) if ch == "."]
    houses = [i for i, ch in enumerate(street) if ch == "H"]
    best = -1
    for mask in range(1 << len(spots)):
        chosen = {spots[j] for j in range(len(spots)) if mask >> j & 1}
        if all((h - 1 in chosen) or (h + 1 in chosen) for h in houses):
            if best < 0 or len(chosen) < best:
                best = len(chosen)
    return best


def g_buckets(r):
    return "".join(r.choice("H.." if r.random() < 0.7 else "HH.") for _ in range(r.randint(1, 11)))


def v_buckets(tests):
    for t in tests:
        s = t["args"][0]
        assert 1 <= len(s) <= 20000 and set(s) <= set("H.")
    assert any(t["expected"] == -1 for t in tests) and any(t["expected"] > 0 for t in tests)


CHECKS["min-buckets-for-houses"] = (b_buckets, lambda r: [g_buckets(r)], "exact")
VALIDATE["min-buckets-for-houses"] = v_buckets


p = add(
    id="largest-merge-of-two-strings", title="Largest Merge of Two Strings", diff="Medium", topic=TOPIC,
    tier="extra", fn="largestMerge", params=[("word1", "string"), ("word2", "string")], ret="string", cmp="exact",
    desc="<p>Build a string <code>merge</code> by repeating the following until both words are empty: take the <strong>first letter</strong> of either <code>word1</code> or <code>word2</code>, remove it from that word and append it to <code>merge</code>. The order of letters inside each word is therefore preserved.</p><p>Return the lexicographically <strong>largest</strong> string that can be built this way.</p><pre>word1 = \"cabaa\", word2 = \"bcaaa\"  -> \"cbcabaaaaa\"\nword1 = \"abcabc\", word2 = \"abdcaba\" -> \"abdcabcabcaba\"</pre>",
    constraints=["1 &le; word1.length, word2.length &le; 3,000", "Both words consist of lowercase English letters"],
    hints=["If the first letters of the two words differ, which word should you take from?",
           "If the first letters are equal, you need to look further. Compare the whole remaining words, not just the next letter.",
           "At every step compare the remaining suffixes <code>word1[i:]</code> and <code>word2[j:]</code> as strings and take the first letter of the larger one (either one if they are equal)."],
    editorial=["The final string is built letter by letter, and the largest string takes the largest possible letter first, so when the next letters differ we take the larger. When they are equal, the choice has long-term consequences: taking from the wrong word may bury a large letter behind a small one.",
               "The right rule is to compare the remaining suffixes. If <code>word1[i:] &gt; word2[j:]</code>, taking from <code>word1</code> is at least as good. Intuitively, the greater suffix has a larger letter earlier, and we should reach it before spending the other word's letters. If the suffixes are equal either choice gives the same result.",
               "Each step compares two suffixes, costing up to O(n + m), and there are n + m steps, so the worst case is O((n + m)<sup>2</sup>). With string slicing in a compiled routine this is fast for lengths up to a few thousand; a suffix array would bring it down to O((n + m) log (n + m))."],
    time="O((n + m)^2)", space="O(n + m)",
    solution='''def largestMerge(word1, word2):
    i = j = 0
    out = []
    n, m = len(word1), len(word2)
    while i < n and j < m:
        if word1[i:] >= word2[j:]:
            out.append(word1[i])
            i += 1
        else:
            out.append(word2[j])
            j += 1
    out.append(word1[i:])
    out.append(word2[j:])
    return ''.join(out)
''',
    tests=[["cabaa", "bcaaa"], ["abcabc", "abdcaba"], ["a", "a"], ["a", "b"], ["ab", "ba"], ["aaa", "aa"], ["zaz", "zaa"],
           ["bbab", "bb"], ["abab", "abab"], ["xyz", "x"], ["cacb", "cac"]],
)
_r = rnd(7105)
p["tests"].append([rs(_r, 3000, "ab"), rs(_r, 3000, "ab")])
p["tests"].append(["a" * 3000, "a" * 2999 + "b"])
p["tests"].append([("ab" * 1500)[:3000], ("ab" * 1499 + "ba")[:3000]])
p["tests"].append([rs(_r, 2500, "abc"), rs(_r, 3000, "bc")])


def b_merge(w1, w2):
    @lru_cache(None)
    def best(i, j):
        if i == len(w1):
            return w2[j:]
        if j == len(w2):
            return w1[i:]
        return max(w1[i] + best(i + 1, j), w2[j] + best(i, j + 1))

    return best(0, 0)


def g_merge(r):
    al = "ab" if r.random() < 0.6 else "abc"
    return [rs(r, r.randint(1, 6), al), rs(r, r.randint(1, 6), al)]


def v_merge(tests):
    for t in tests:
        w1, w2 = t["args"]
        assert 1 <= len(w1) <= 3000 and 1 <= len(w2) <= 3000
        assert w1.islower() and w2.islower()
        assert len(t["expected"]) == len(w1) + len(w2)


CHECKS["largest-merge-of-two-strings"] = (b_merge, g_merge, "exact")
VALIDATE["largest-merge-of-two-strings"] = v_merge


p = add(
    id="smallest-string-within-cyclic-budget", title="Smallest String Within a Cyclic Change Budget", diff="Medium", topic=TOPIC,
    tier="extra", fn="smallestWithinBudget", params=[("s", "string"), ("k", "int")], ret="string", cmp="exact",
    desc="<p>The alphabet is <em>cyclic</em>: after <code>z</code> comes <code>a</code> again. The distance between two letters is the shorter way around the cycle, so <code>dist('a','c') = 2</code> and <code>dist('a','z') = 1</code>.</p><p>You may turn <code>s</code> into any string <code>t</code> of the same length as long as the total distance <code>dist(s[0],t[0]) + dist(s[1],t[1]) + ...</code> is at most <code>k</code>. Return the lexicographically smallest string <code>t</code> you can obtain.</p><pre>s = \"zbbz\", k = 3  -> \"aaaz\"\ns = \"xaxcd\", k = 4 -> \"aawcd\"\ns = \"lol\", k = 0   -> \"lol\"</pre>",
    constraints=["1 &le; s.length &le; 20,000", "0 &le; k &le; 2,000", "s consists of lowercase English letters"],
    hints=["Lexicographically smallest: the first letter is the most important. Can you turn it into <code>a</code> within the budget?",
           "The cost of turning a letter into <code>a</code> is <code>min(c, 26 - c)</code> where <code>c</code> is its position in the alphabet counted from 0. Pay it whenever you can afford it, from left to right.",
           "When the cost of reaching <code>a</code> exceeds what is left, spend all the remaining budget moving that letter backwards in the alphabet (<code>chr(ord(c) - left)</code>), then stop: everything to the right stays unchanged."],
    editorial=["A smaller letter at an earlier position beats any gains later, so process the positions from left to right and make each one as small as the remaining budget allows.",
               "For a letter with 0-based index <code>c</code>, reaching <code>a</code> costs <code>d = min(c, 26 - c)</code>. If <code>d &le; left</code>, set the letter to <code>a</code> and subtract <code>d</code>. Otherwise the budget cannot get this letter to <code>a</code>; the smallest reachable letter is obtained by moving it down by exactly <code>left</code> places (cost <code>left</code>), because here <code>left &lt; d &le; 13</code> so going backwards costs exactly its step count. Then the budget is empty and the rest of the string is left unchanged.",
               "Spending budget on an earlier letter is always at least as valuable as on a later one, which justifies the left-to-right order. One pass, O(n)."],
    time="O(n)", space="O(n)",
    solution='''def smallestWithinBudget(s, k):
    out = list(s)
    for i, ch in enumerate(s):
        c = ord(ch) - 97
        d = min(c, 26 - c)
        if d <= k:
            out[i] = 'a'
            k -= d
        else:
            out[i] = chr(ord(ch) - k)
            k = 0
            break
    return ''.join(out)
''',
    tests=[["zbbz", 3], ["xaxcd", 4], ["lol", 0], ["a", 5], ["z", 1], ["n", 12], ["n", 13], ["mmm", 100], ["yzabc", 2],
           ["nnnn", 20], ["qpo", 7]],
)
_r = rnd(7106)
p["tests"].append([rs(_r, 8000), 2000])
p["tests"].append([rs(_r, 8000, "nopqrstuvwxyz"), 1500])
p["tests"].append([rs(_r, 5000, "abc") , 7])


def b_shift(s, k):
    def dist(x, y):
        d = abs(ord(x) - ord(y))
        return min(d, 26 - d)

    @lru_cache(None)
    def best(i, left):
        if i == len(s):
            return ""
        res = None
        for t in LOW:
            d = dist(s[i], t)
            if d <= left:
                cand = t + best(i + 1, left - d)
                if res is None or cand < res:
                    res = cand
        return res

    return best(0, k)


def g_shift(r):
    return [rs(r, r.randint(1, 5)), r.randint(0, 30)]


def v_shift(tests):
    for t in tests:
        s, k = t["args"]
        assert 1 <= len(s) <= 20000 and 0 <= k <= 2000 and s.islower()
        e = t["expected"]
        total = 0
        for x, y in zip(s, e):
            d = abs(ord(x) - ord(y))
            total += min(d, 26 - d)
        assert len(e) == len(s) and total <= k


CHECKS["smallest-string-within-cyclic-budget"] = (b_shift, g_shift, "exact")
VALIDATE["smallest-string-within-cyclic-budget"] = v_shift


p = add(
    id="orderly-queue-smallest-string", title="Orderly Queue", diff="Medium", topic=TOPIC,
    tier="extra", fn="orderlyQueue", params=[("s", "string"), ("k", "int")], ret="string", cmp="exact",
    desc="<p>You are given a string <code>s</code> and an integer <code>k</code>. In one move you choose one of the <strong>first <code>k</code> letters</strong> of the current string (all letters if the string is shorter than <code>k</code>), remove it and append it to the <strong>end</strong> of the string. You may make any number of moves, including none.</p><p>Return the lexicographically smallest string you can end up with.</p><pre>s = \"cba\", k = 1    -> \"acb\"\ns = \"baaca\", k = 3  -> \"aaabc\"</pre>",
    constraints=["1 &le; k &le; 10,000", "1 &le; s.length &le; 5,000", "s consists of lowercase English letters"],
    hints=["Start with <code>k = 1</code>. What strings can you reach by moving the first letter to the back again and again?",
           "With <code>k = 1</code> you can only rotate the string, so try every rotation. With <code>k = 2</code>, think about whether you can swap two neighbouring letters (using the extra letter as a helper).",
           "For <code>k &ge; 2</code> adjacent letters can be exchanged, which means any permutation is reachable, so the answer is simply the sorted string. For <code>k = 1</code> take the smallest rotation."],
    editorial=["If <code>k = 1</code> the only operation is to move the first letter to the back, which rotates the string. The reachable strings are exactly its <code>n</code> rotations, and the answer is the smallest of them. Building all rotations costs O(n<sup>2</sup>) which is fine here; Booth's algorithm or the minimal-rotation trick does it in O(n).",
               "If <code>k &ge; 2</code> we can pick the second letter as well. Think of the string as a circle with a pointer at its start. Moving the first letter to the back just advances the pointer. Moving the second letter to the back takes <code>y</code> out of <code>x y rest</code> and gives <code>x rest y</code>; read as a circle this is <code>y x rest</code> with the pointer at <code>x</code>, so <code>x</code> and <code>y</code> have exchanged places. Pointer moves are free and every neighbouring pair can be brought to the front, so any two adjacent letters can be exchanged. Adjacent exchanges generate every ordering of the letters, so the sorted string is reachable, and nothing is smaller than the sorted order.",
               "So: return <code>sorted(s)</code> when <code>k &gt; 1</code>, and the minimum rotation when <code>k = 1</code>."],
    time="O(n^2) for k = 1, O(n log n) otherwise", space="O(n)",
    solution='''def orderlyQueue(s, k):
    if k > 1:
        return ''.join(sorted(s))
    return min(s[i:] + s[:i] for i in range(len(s)))
''',
    tests=[["cba", 1], ["baaca", 3], ["a", 1], ["a", 2], ["ba", 1], ["ba", 2], ["bcab", 1], ["bcab", 2], ["zyxwv", 4],
           ["abab", 1], ["cabcab", 1], ["dcbaabcd", 1], ["dcbaabcd", 2]],
)
_r = rnd(7107)
p["tests"].append([rs(_r, 5000), 1])
p["tests"].append([("ab" * 2499) + "ba", 1])
p["tests"].append([rs(_r, 5000), 2])


def b_orderly(s, k):
    seen = {s}
    q = deque([s])
    while q:
        cur = q.popleft()
        for i in range(min(k, len(cur))):
            nxt = cur[:i] + cur[i + 1:] + cur[i]
            if nxt not in seen:
                seen.add(nxt)
                q.append(nxt)
    return min(seen)


def g_orderly(r):
    return [rs(r, r.randint(1, 6), "abc"), r.randint(1, 4)]


def v_orderly(tests):
    for t in tests:
        s, k = t["args"]
        assert 1 <= len(s) <= 5000 and 1 <= k <= 10000 and s.islower()
        assert sorted(t["expected"]) == sorted(s)


CHECKS["orderly-queue-smallest-string"] = (b_orderly, g_orderly, "exact")
VALIDATE["orderly-queue-smallest-string"] = v_orderly


# ---------------------------------------------------------------- HARD

p = add(
    id="can-rearrange-letters-k-apart", title="Rearrange Letters at Least K Apart", diff="Hard", topic=TOPIC,
    fn="canSpreadApart", params=[("s", "string"), ("k", "int")], ret="bool", cmp="exact",
    desc="<p>Can the letters of <code>s</code> be rearranged so that any two equal letters are at least <code>k</code> positions apart? Formally, for every pair of equal letters at indices <code>i &lt; j</code> in the new arrangement, <code>j - i &ge; k</code>.</p><p>Return <code>true</code> if such an arrangement exists, otherwise <code>false</code>.</p><pre>s = \"aabbcc\", k = 3   -> true    (\"abcabc\")\ns = \"aaabc\",  k = 3   -> false\ns = \"aaadbbcc\", k = 2 -> true    (\"abacabcd\")</pre><p>For <code>k = 1</code> the answer is always <code>true</code>.</p>",
    constraints=["1 &le; s.length &le; 10,000", "1 &le; k &le; 10,000", "s consists of lowercase English letters"],
    hints=["Think about the most frequent letter. If it appears <code>m</code> times, what is the shortest string that can hold it?",
           "Build the arrangement left to right. At each position, among the letters that were not used in the last <code>k - 1</code> positions, which one is the most urgent?",
           "Use the letter with the largest remaining count among those that are allowed (their last use is at least <code>k</code> positions back). If no letter is allowed while some are still unplaced, the answer is <code>false</code>."],
    editorial=["Simulation by greedy: keep, for each of the 26 letters, how many copies remain and the earliest position where it may be used again. At each position choose, among the letters with copies left that are allowed at this position, the one with the largest remaining count. Place it and forbid it until <code>k</code> positions later. If at some position no letter is allowed, no arrangement exists.",
               "Why the largest count? The letters with many copies are the hardest to place: they need the most slots spaced <code>k</code> apart. Spending them as early as allowed keeps them from being stranded at the end, where only a few positions remain. Each step scans 26 letters, so the cost is O(26 n).",
               "There is also a counting criterion: if the largest count is <code>m</code> and <code>c</code> letters reach that count, the arrangement exists exactly when <code>(m - 1) * k + c &le; n</code>. The <code>m</code> copies of a top letter need <code>m - 1</code> blocks of length <code>k</code> plus a final slot, and the other top letters share that last block. The simulation proves the criterion is also sufficient."],
    time="O(26 n)", space="O(1)",
    solution='''def canSpreadApart(s, k):
    cnt = [0] * 26
    for ch in s:
        cnt[ord(ch) - 97] += 1
    ready = [0] * 26
    for pos in range(len(s)):
        best = -1
        for i in range(26):
            if cnt[i] > 0 and ready[i] <= pos and (best < 0 or cnt[i] > cnt[best]):
                best = i
        if best < 0:
            return False
        cnt[best] -= 1
        ready[best] = pos + k
    return True
''',
    tests=[["aabbcc", 3], ["aaabc", 3], ["aaadbbcc", 2], ["a", 1], ["a", 5], ["aa", 1], ["aa", 2], ["ab", 5], ["aab", 2],
           ["aabb", 3], ["abcdef", 10], ["aaabbbccc", 3], ["aaabbbccc", 4], ["aaaabbbbcc", 3]],
)
_r = rnd(7108)


def _near(s):
    c = Counter(s)
    m = max(c.values())
    top = sum(1 for v in c.values() if v == m)
    return (len(s) - top) // (m - 1) if m > 1 else len(s)


_s = rs(_r, 8000)
_mk = _near(_s)
p["tests"].append([_s, _mk])
p["tests"].append([_s, _mk + 1])
_s = list("a" * 900 + "b" * 900 + "c" * 900 + "d" * 800 + "e" * 400 + rs(_r, 1000, "fghijk"))
_r.shuffle(_s)
_s = "".join(_s)
_mk = _near(_s)
p["tests"].append([_s, _mk])
p["tests"].append([_s, _mk + 1])


def b_apart(s, k):
    n = len(s)
    cnt = Counter(s)
    last = {}

    def dfs(pos):
        if pos == n:
            return True
        for ch in list(cnt):
            if cnt[ch] > 0 and (ch not in last or pos - last[ch] >= k):
                prev = last.get(ch)
                cnt[ch] -= 1
                last[ch] = pos
                ok = dfs(pos + 1)
                cnt[ch] += 1
                if prev is None:
                    del last[ch]
                else:
                    last[ch] = prev
                if ok:
                    return True
        return False

    return dfs(0)


def g_apart(r):
    return [rs(r, r.randint(1, 8), "abc" if r.random() < 0.7 else "abcd"), r.randint(1, 5)]


def v_apart(tests):
    for t in tests:
        s, k = t["args"]
        assert 1 <= len(s) <= 10000 and 1 <= k <= 10000 and s.islower()
        c = Counter(s)
        m = max(c.values())
        top = sum(1 for v in c.values() if v == m)
        assert t["expected"] == ((m - 1) * k + top <= len(s))
    assert any(t["expected"] for t in tests) and any(not t["expected"] for t in tests)


CHECKS["can-rearrange-letters-k-apart"] = (b_apart, g_apart, "exact")
VALIDATE["can-rearrange-letters-k-apart"] = v_apart


p = add(
    id="can-stamp-target-string", title="Stamp the Target String", diff="Hard", topic=TOPIC,
    tier="extra", fn="canStamp", params=[("stamp", "string"), ("target", "string")], ret="bool", cmp="exact",
    desc="<p>You start with a strip of <code>target.length</code> blank cells. In one turn you press the string <code>stamp</code> onto the strip at some position <code>p</code> such that the stamp lies completely inside the strip. The cells <code>p .. p + stamp.length - 1</code> then show the letters of the stamp, replacing whatever was there before (blank or not).</p><p>You can press the stamp any number of times. Return <code>true</code> if the strip can be made to read exactly <code>target</code>, otherwise <code>false</code>.</p><pre>stamp = \"abc\", target = \"ababc\"  -> true    (press at 0, then at 2)\nstamp = \"abc\", target = \"abcba\"  -> false\nstamp = \"ab\",  target = \"abba\"   -> false</pre>",
    constraints=["1 &le; stamp.length &le; target.length &le; 1,000", "Both strings consist of lowercase English letters"],
    hints=["The last press leaves an entire copy of the stamp visible in the target. Reason backwards from the end instead of forwards from a blank strip.",
           "Reverse the process: find a window of the target that equals the stamp, erase it to wildcards, and repeat; a window may match when some of its cells are already wildcards, as long as at least one cell is still a real letter.",
           "Keep for every window the set of cells that still disagree with the stamp. When a window's set becomes empty, erase its remaining letters, remove those cells from the neighbouring windows' sets, and push newly matching windows on a queue. The answer is <code>true</code> if every cell ends up erased."],
    editorial=["Work backwards. The final press shows a complete copy of <code>stamp</code> in the target. Undo it: replace those cells by a wildcard <code>?</code>, which matches any letter (those cells could have been overwritten by earlier presses in any way). The press before that one shows the stamp again, except that cells covered by later presses are now wildcards. So repeatedly undo a window that matches the stamp where wildcards are free, and that still contains at least one real letter (otherwise undoing it is pointless). The target is stampable exactly when everything can be turned into wildcards.",
               "Undoing a window can only create more wildcards and never destroys a possible match elsewhere, so the order in which valid windows are undone does not matter: this is a closure computation, and it is correct to undo any available window greedily.",
               "A naive rescan after each undo is too slow. Instead, for each of the at most <code>n - m + 1</code> windows store its list of matching cells and the set of mismatching cells. When a window's mismatching set is empty, enqueue it. Processing a window turns each of its not-yet-erased matching cells into a wildcard; for every window containing such a cell, delete that cell from its mismatching set and enqueue the window if the set became empty. Every cell is erased once and touches at most <code>m</code> windows, so the total work is O(n &middot; m)."],
    time="O(n * m)", space="O(n * m)",
    solution='''def canStamp(stamp, target):
    m, n = len(stamp), len(target)
    todo = []
    made = []
    queue = []
    for i in range(n - m + 1):
        ok = []
        bad = set()
        for j in range(m):
            if target[i + j] == stamp[j]:
                ok.append(i + j)
            else:
                bad.add(i + j)
        made.append(ok)
        todo.append(bad)
        if not bad:
            queue.append(i)
    erased = [False] * n
    count = 0
    while queue:
        i = queue.pop()
        for pos in made[i]:
            if not erased[pos]:
                erased[pos] = True
                count += 1
                for w in range(max(0, pos - m + 1), min(pos, n - m) + 1):
                    if pos in todo[w]:
                        todo[w].discard(pos)
                        if not todo[w]:
                            queue.append(w)
    return count == n
''',
    tests=[["abc", "ababc"], ["abc", "abcba"], ["ab", "abba"], ["a", "aaaa"], ["a", "b"], ["ab", "ab"], ["ab", "abab"],
           ["ab", "aab"], ["abca", "aabcaca"], ["abca", "abcabca"], ["xyz", "xyzyz"], ["aba", "aabaa"]],
)
_r = rnd(7109)


def _stamped(stamp, n, r):
    m = len(stamp)
    t = ["?"] * n
    while "?" in t:
        pos = r.randint(0, n - m)
        t[pos:pos + m] = stamp
    return "".join(t)


for _n, _m in ((1000, 300), (900, 40), (1000, 600)):
    _st = rs(_r, _m, "ab")
    _t = _stamped(list(_st), _n, _r)
    p["tests"].append([_st, _t])
    _l = list(_t)
    _i = _r.randrange(_n)
    _l[_i] = "c"
    p["tests"].append([_st, "".join(_l)])


def b_stamp(stamp, target):
    n, m = len(target), len(stamp)
    start = "?" * n
    seen = {start}
    q = deque([start])
    while q:
        cur = q.popleft()
        if cur == target:
            return True
        for p0 in range(n - m + 1):
            nxt = cur[:p0] + stamp + cur[p0 + m:]
            if nxt not in seen:
                seen.add(nxt)
                q.append(nxt)
    return False


def g_stamp(r):
    st = rs(r, r.randint(1, 3), "ab")
    n = r.randint(len(st), 7)
    if r.random() < 0.6:
        t = _stamped(list(st), n, r)
        if r.random() < 0.3:
            t = t[:-1] + r.choice("ab")
    else:
        t = rs(r, n, "ab")
    return [st, t]


def v_stamp(tests):
    for t in tests:
        st, tg = t["args"]
        assert 1 <= len(st) <= len(tg) <= 1000 and st.islower() and tg.islower()
    assert any(t["expected"] for t in tests) and any(not t["expected"] for t in tests)


CHECKS["can-stamp-target-string"] = (b_stamp, g_stamp, "exact")
VALIDATE["can-stamp-target-string"] = v_stamp
