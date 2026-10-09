"""Problems: strings. See data/lib.py for the registry."""
from collections import Counter
from itertools import combinations, groupby, product

from lib import add, rnd, CHECKS, VALIDATE, gen_arr  # noqa: F401

INT_MIN, INT_MAX = -(2 ** 31), 2 ** 31 - 1
LET = "abcdefghijklmnopqrstuvwxyz"
LD = LET + "0123456789"


def _rs(r, n, alpha=LET):
    return "".join(r.choice(alpha) for _ in range(n))


# ---------------------------------------------------------------- EASY

p = add(
    id="first-unique-character", title="First Unique Character", diff="Easy", topic="Strings",
    fn="firstUniqChar", params=[("s", "string")], ret="int", cmp="exact",
    desc="<p>Given a string <code>s</code>, find the first character that occurs exactly once in the whole string and return its index (0-based). If every character repeats, return <code>-1</code>.</p><p>For example, in <code>\"planet\"</code> every letter is unique, so the answer is <code>0</code>; in <code>\"aabcb\"</code> the answer is <code>3</code>; in <code>\"abab\"</code> the answer is <code>-1</code>.</p>",
    constraints=["1 &le; s.length &le; 50,000", "s consists of lowercase English letters"],
    hints=["Checking each character against all the others works, but is slow for long strings. What do you need to know about each character?",
           "You only need to know how many times each letter occurs in the entire string.",
           "Make one pass to count the letters, then a second pass from the left to return the first index whose letter has count 1."],
    editorial=["Count the occurrences of every character with a hash map (or an array of 26 counters) in one pass. Then scan the string from the left a second time and return the first index whose character has a count of exactly one. If the scan ends without a hit, return -1.",
               "Comparing every character with every other character is O(n&sup2;) and becomes slow at 50,000 characters. The two-pass counting approach is linear, and the counter table has constant size because the alphabet is fixed."],
    time="O(n)", space="O(1)",
    solution='''def firstUniqChar(s):
    count = {}
    for c in s:
        count[c] = count.get(c, 0) + 1
    for i, c in enumerate(s):
        if count[c] == 1:
            return i
    return -1
''',
    tests=[["planet"], ["aabcb"], ["abab"], ["z"], ["aa"], ["aabbccddx"], ["xxyz"], ["abcabcd"], ["zyxwvutsrqponmlkjihgfedcba"],
           ["qqwweerrttyyuuiioopp"], ["abcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxy"]],
)
_r = rnd(7001)
for _n, _pos in ((50000, 49998), (49999, 25000), (30001, 0), (50000, None)):
    if _pos is None:
        _s = _rs(_r, _n)  # dense random text: every letter repeats
    else:
        _half = [_r.choice(LET[:-1]) for _ in range((_n - 1) // 2)]
        _body = _half + _half
        _r.shuffle(_body)
        _u = "".join(_body)  # every letter in it occurs at least twice; 'z' is absent
        _s = _u[:_pos] + "z" + _u[_pos:]
    p["tests"].append([_s])


def b_first(s):
    for i in range(len(s)):
        if all(s[j] != s[i] for j in range(len(s)) if j != i):
            return i
    return -1


def g_first(r):
    return [_rs(r, r.randint(1, 10), "abcd")]


def v_first(tests):
    for t in tests:
        s = t["args"][0]
        assert 1 <= len(s) <= 50000 and all("a" <= c <= "z" for c in s)


CHECKS["first-unique-character"] = (b_first, g_first, "exact")
VALIDATE["first-unique-character"] = v_first

p = add(
    id="isomorphic-strings", title="Isomorphic Strings", diff="Easy", topic="Strings",
    fn="isIsomorphic", params=[("s", "string"), ("t", "string")], ret="bool", cmp="exact",
    desc="<p>Two strings <code>s</code> and <code>t</code> of the same length are <em>isomorphic</em> if you can rename the characters of <code>s</code> to get exactly <code>t</code>. A renaming assigns each distinct character of <code>s</code> one replacement character, and two different characters of <code>s</code> are never given the same replacement. The order of the characters is preserved.</p><p>For example <code>\"egg\"</code> and <code>\"add\"</code> are isomorphic (<code>e&rarr;a</code>, <code>g&rarr;d</code>), but <code>\"foo\"</code> and <code>\"bar\"</code> are not (the two <code>o</code>s would need different replacements), and neither are <code>\"ab\"</code> and <code>\"cc\"</code> (two characters would share one replacement).</p><p>Return <code>true</code> if the strings are isomorphic.</p>",
    constraints=["1 &le; s.length &le; 50,000", "t.length == s.length", "s and t consist of lowercase letters and digits"],
    hints=["Walking both strings together, each character of <code>s</code> must always meet the same character of <code>t</code>.",
           "That one direction is not enough: <code>\"ab\"</code> vs <code>\"cc\"</code> passes it. The rule must also hold when you look from <code>t</code> back to <code>s</code>.",
           "Keep two maps, s&rarr;t and t&rarr;s, and return false as soon as either one is contradicted."],
    editorial=["Scan both strings at the same index. Store, for the pair <code>(a, b)</code>, that <code>a</code> maps to <code>b</code> and that <code>b</code> maps back to <code>a</code>. If <code>a</code> was already mapped to something other than <code>b</code>, or <code>b</code> was already the image of something other than <code>a</code>, the strings are not isomorphic.",
               "An equivalent trick is to normalise each string by replacing every character with the index of its first occurrence, and compare the two normalised sequences. Both approaches run in linear time; the mapping tables have at most 36 entries because of the alphabet."],
    time="O(n)", space="O(1)",
    solution='''def isIsomorphic(s, t):
    if len(s) != len(t):
        return False
    fwd, back = {}, {}
    for a, b in zip(s, t):
        if fwd.setdefault(a, b) != b or back.setdefault(b, a) != a:
            return False
    return True
''',
    tests=[["egg", "add"], ["foo", "bar"], ["ab", "cc"], ["a", "a"], ["a", "b"], ["paper", "title"], ["badc", "baba"],
           ["abab", "cdcd"], ["abab", "cdce"], ["12321", "abcba"], ["z9z9", "ab" + "ab"], ["aabb", "ccdd"], ["aabb", "cdcd"]],
)
_r = rnd(7002)
_s = _rs(_r, 50000, LD)
_perm = list(LD); _r.shuffle(_perm)
_m = dict(zip(LD, _perm))
_t = "".join(_m[c] for c in _s)
p["tests"].append([_s, _t])
p["tests"].append([_s, _t[:-1] + ("a" if _t[-1] != "a" else "b")])
_s2 = _rs(_r, 50000, "ab")
p["tests"].append([_s2, "".join("x" if c == "a" else "y" for c in _s2)])
p["tests"].append([_s2, "".join("x" if c == "a" else "x" for c in _s2)])
p["tests"].append(["a" * 50000, "b" * 50000])
p["tests"].append([LD * 1000, LD[::-1] * 1000])


def b_iso(s, t):
    def norm(x):
        return [x.index(c) for c in x]
    return len(s) == len(t) and norm(s) == norm(t)


def g_iso(r):
    n = r.randint(1, 8)
    s = _rs(r, n, "abc")
    if r.random() < 0.5:
        al = list("xyzw"); r.shuffle(al)
        t = "".join(al["abc".index(c)] for c in s)
        if r.random() < 0.4:
            i = r.randrange(n)
            t = t[:i] + r.choice("xyzw") + t[i + 1:]
    else:
        t = _rs(r, n, "xyz")
    return [s, t]


def v_iso(tests):
    for t in tests:
        s, u = t["args"]
        assert 1 <= len(s) <= 50000 and len(s) == len(u)
        assert all(c in LD for c in s + u)


CHECKS["isomorphic-strings"] = (b_iso, g_iso, "exact")
VALIDATE["isomorphic-strings"] = v_iso

p = add(
    id="run-length-compressed-length", title="Run-Length Compressed Length", diff="Easy", topic="Strings",
    fn="compressedLength", params=[("s", "string")], ret="int", cmp="exact",
    desc="<p>A <em>run</em> is a maximal block of equal consecutive characters. To compress a string, replace every run by its character followed by the length of the run written in decimal, except that a run of length <code>1</code> is written as just the character (no number).</p><p>For example <code>\"aaabccdddd\"</code> is compressed to <code>\"a3bc2d4\"</code>, and a run of twelve <code>x</code> characters becomes <code>\"x12\"</code>. Return the <strong>length</strong> of the compressed string.</p>",
    constraints=["1 &le; s.length &le; 50,000", "s consists of lowercase English letters"],
    hints=["You do not have to build the compressed string; its length is enough.",
           "Split the string into runs. A run of length 1 contributes 1; a longer run contributes 1 plus the number of decimal digits of its length.",
           "Scan with two indices: start a run at <code>i</code>, advance <code>j</code> while <code>s[j] == s[i]</code>, add the contribution, then continue from <code>j</code>."],
    editorial=["Walk through the string and find each run with a pair of indices. A run of length <code>k</code> costs one character for the letter, plus <code>len(str(k))</code> more characters when <code>k &gt; 1</code>. Summing over all runs gives the answer in a single linear pass.",
               "Note that counts with several digits matter: a run of 10 to 99 letters adds two digits, 100 to 999 adds three, and so on. Forgetting this is the most common mistake. Building the output string explicitly also works, but wastes memory."],
    time="O(n)", space="O(1)",
    solution='''def compressedLength(s):
    total = 0
    n = len(s)
    i = 0
    while i < n:
        j = i
        while j < n and s[j] == s[i]:
            j += 1
        run = j - i
        total += 1
        if run > 1:
            total += len(str(run))
        i = j
    return total
''',
    tests=[["aaabccdddd"], ["a"], ["ab"], ["aa"], ["abc"], ["xxxxxxxxxxxx"], ["aaaaaaaaaabbbbbbbbb"], ["abababab"], ["zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz"],
           ["aabbaabb"], ["abbbbbbbbbbc"]],
)
_r = rnd(7003)
p["tests"].append(["a" * 50000])
p["tests"].append(["ab" * 25000])
p["tests"].append(["a" * 999 + "b" * 1000 + "c" * 100 + "d" * 9 + "e"])
_s = ""
while len(_s) < 49000:
    _s += _r.choice(LET) * _r.choice([1, 1, 2, 3, 9, 10, 11, 99, 100, 101])
p["tests"].append([_s[:50000]])


def b_rle(s):
    out = ""
    for ch, grp in groupby(s):
        k = len(list(grp))
        out += ch + (str(k) if k > 1 else "")
    return len(out)


def g_rle(r):
    s = ""
    for _ in range(r.randint(1, 5)):
        s += r.choice("abc") * r.choice([1, 1, 2, 3, 9, 10, 12])
    return [s]


def v_rle(tests):
    for t in tests:
        s = t["args"][0]
        assert 1 <= len(s) <= 50000 and all("a" <= c <= "z" for c in s)


CHECKS["run-length-compressed-length"] = (b_rle, g_rle, "exact")
VALIDATE["run-length-compressed-length"] = v_rle

p = add(
    id="longest-palindrome-by-rearranging", title="Longest Palindrome by Rearranging", diff="Easy", topic="Strings",
    fn="longestPalindromeLength", params=[("s", "string")], ret="int", cmp="exact",
    desc="<p>You are given a string <code>s</code>. Pick some of its characters (each character of <code>s</code> can be used at most once) and arrange them in any order to form a palindrome. Return the maximum possible length of such a palindrome.</p><p>For example, from <code>\"abccccdd\"</code> you can build <code>\"dccaccd\"</code> of length <code>7</code>. From <code>\"abc\"</code> you can only build a single-character palindrome, so the answer is <code>1</code>.</p>",
    constraints=["1 &le; s.length &le; 50,000", "s consists of lowercase letters and digits"],
    hints=["In a palindrome, every character appears on both sides of the centre, except possibly one in the middle.",
           "A character that occurs <code>c</code> times can contribute <code>c</code> characters if <code>c</code> is even, or <code>c - 1</code> of them as pairs if <code>c</code> is odd.",
           "If any character was left over (some count was odd), one of them can sit in the middle, adding 1."],
    editorial=["Count every character. Each character contributes <code>2 * (count // 2)</code> characters to the two halves of the palindrome. Add up those pair contributions. If the total is smaller than <code>len(s)</code>, at least one character has an odd count and has one unused copy, so one of those can be placed in the centre and the answer is the total plus one.",
               "Equivalently, the answer is <code>len(s)</code> minus the number of characters with an odd count, plus one if that number is positive. No actual arrangement needs to be built."],
    time="O(n)", space="O(1)",
    solution='''def longestPalindromeLength(s):
    count = {}
    for c in s:
        count[c] = count.get(c, 0) + 1
    odd = sum(1 for v in count.values() if v % 2 == 1)
    return len(s) - odd + (1 if odd else 0)
''',
    tests=[["abccccdd"], ["abc"], ["a"], ["aa"], ["aab"], ["abcabc"], ["123321"], ["aaabbbccc"], ["zzzzzzzzzz"], ["abcdefghij0123456789"],
           ["a1a1a1b2b2"]],
)
_r = rnd(7004)
p["tests"].append([_rs(_r, 50000, LD)])
p["tests"].append(["a" * 50000])
p["tests"].append(["a" * 49999])
p["tests"].append([(LD * 1400)[:50000]])


def b_longpal(s):
    alpha = sorted(set(s))
    have = Counter(s)
    if len(alpha) ** (len(s) // 2 + 1) > 20000:
        # too many candidates to enumerate: simulate pairing equal characters off one by one
        pool = list(s)
        total = 0
        while True:
            for i in range(len(pool)):
                j = next((k for k in range(i + 1, len(pool)) if pool[k] == pool[i]), -1)
                if j >= 0:
                    pool.pop(j)
                    pool.pop(i)
                    total += 2
                    break
            else:
                return total + (1 if pool else 0)
    for L in range(len(s), 0, -1):
        mids = [""] if L % 2 == 0 else alpha
        for half in product(alpha, repeat=L // 2):
            h = "".join(half)
            for m in mids:
                cand = h + m + h[::-1]
                if not (Counter(cand) - have):
                    return L
    return 0


def g_longpal(r):
    return [_rs(r, r.randint(1, 9), "abc" if r.random() < 0.6 else "abcd")]


def v_longpal(tests):
    for t in tests:
        s = t["args"][0]
        assert 1 <= len(s) <= 50000 and all(c in LD for c in s)


CHECKS["longest-palindrome-by-rearranging"] = (b_longpal, g_longpal, "exact")
VALIDATE["longest-palindrome-by-rearranging"] = v_longpal


# ---------------------------------------------------------------- MEDIUM

p = add(
    id="longest-palindromic-substring-length", title="Longest Palindromic Substring Length", diff="Medium", topic="Strings",
    fn="longestPalindromicSubstringLength", params=[("s", "string")], ret="int", cmp="exact",
    desc="<p>A palindrome reads the same forwards and backwards. Given a string <code>s</code>, return the length of the longest <em>contiguous substring</em> of <code>s</code> that is a palindrome.</p><p>For example, for <code>\"babad\"</code> the answer is <code>3</code> (<code>\"bab\"</code> or <code>\"aba\"</code>), and for <code>\"cbbd\"</code> the answer is <code>2</code> (<code>\"bb\"</code>).</p>",
    constraints=["1 &le; s.length &le; 2,000", "s consists of lowercase letters and digits"],
    hints=["Testing every substring for being a palindrome takes O(n&sup3;) time. Can a palindrome be grown instead of tested?",
           "Every palindrome has a centre: a character (odd length) or the gap between two characters (even length). Growing outwards from a centre keeps it a palindrome as long as the two new ends match.",
           "Try all 2n-1 centres, expand while the characters at both ends are equal, and keep the best length."],
    editorial=["Expand around centres. For each index <code>i</code> consider the odd-length palindromes centred at <code>i</code> and the even-length palindromes centred between <code>i</code> and <code>i+1</code>. Start with <code>lo</code> and <code>hi</code> at the centre and move them outwards while <code>s[lo] == s[hi]</code>; the length of the last valid window is <code>hi - lo - 1</code> after the loop. The maximum over all centres is the answer.",
               "There are 2n-1 centres and each expansion costs up to O(n), giving O(n&sup2;) total, which is fast for n = 2,000. Manacher's algorithm reduces this to O(n), and dynamic programming over (i, j) pairs gives the same quadratic time with quadratic memory."],
    time="O(n^2)", space="O(1)",
    solution='''def longestPalindromicSubstringLength(s):
    n = len(s)
    best = 1
    for centre in range(2 * n - 1):
        lo = centre // 2
        hi = lo + centre % 2
        while lo >= 0 and hi < n and s[lo] == s[hi]:
            lo -= 1
            hi += 1
        best = max(best, hi - lo - 1)
    return best
''',
    tests=[["babad"], ["cbbd"], ["a"], ["ab"], ["aa"], ["abcde"], ["racecar"], ["abaxyzzyxf"], ["aaaa"], ["abacdfgdcaba"], ["12321x45654y"],
           ["forgeeksskeegfor"]],
)
_r = rnd(7005)
p["tests"].append(["a" * 2000])
p["tests"].append([_rs(_r, 2000, LD)])
p["tests"].append([_rs(_r, 2000, "ab")])
_h = _rs(_r, 700, "abc")
p["tests"].append([_rs(_r, 300, LET) + _h + _r.choice("xyz") + _h[::-1] + _rs(_r, 299, LET)])
p["tests"].append([("ab" * 1000)])
p["tests"].append([("a" * 999) + "b" + ("a" * 1000)])


def b_lps(s):
    best = 0
    n = len(s)
    for i in range(n):
        for j in range(i + 1, n + 1):
            t = s[i:j]
            if t == t[::-1]:
                best = max(best, j - i)
    return best


def g_lps(r):
    return [_rs(r, r.randint(1, 12), "ab" if r.random() < 0.6 else "abc")]


def v_lps(tests):
    for t in tests:
        s = t["args"][0]
        assert 1 <= len(s) <= 2000 and all(c in LD for c in s)


CHECKS["longest-palindromic-substring-length"] = (b_lps, g_lps, "exact")
VALIDATE["longest-palindromic-substring-length"] = v_lps

p = add(
    id="count-palindromic-substrings", title="Count Palindromic Substrings", diff="Medium", topic="Strings",
    fn="countPalindromicSubstrings", params=[("s", "string")], ret="int", cmp="exact",
    desc="<p>Given a string <code>s</code>, count how many of its contiguous substrings are palindromes. Substrings are counted by their position, so two equal substrings taken from different places are counted separately.</p><p>For example, <code>\"aaa\"</code> has 6 palindromic substrings: three single <code>\"a\"</code>, two <code>\"aa\"</code> and one <code>\"aaa\"</code>. The string <code>\"abc\"</code> has 3.</p>",
    constraints=["1 &le; s.length &le; 2,000", "s consists of lowercase letters and digits"],
    hints=["There are about n&sup2;/2 substrings. Checking each one from scratch costs another factor of n.",
           "If the substring from i to j is a palindrome, then growing it by one matching character on each side gives another palindrome.",
           "Take each of the 2n-1 centres (a character or a gap between two), expand while both ends match, and count one palindrome per successful expansion."],
    editorial=["Every palindrome has a unique centre, which is either a single character or the gap between two adjacent characters. For each of the 2n-1 centres, expand outwards while the two end characters are equal; each successful step reveals one more palindromic substring, so you add one to the counter per step.",
               "This takes O(n&sup2;) time in the worst case (a string of identical characters) and O(1) space. A DP table <code>is_pal[i][j]</code> also works but needs O(n&sup2;) memory. The count can reach about two million, which fits easily in 32 bits."],
    time="O(n^2)", space="O(1)",
    solution='''def countPalindromicSubstrings(s):
    n = len(s)
    total = 0
    for centre in range(2 * n - 1):
        lo = centre // 2
        hi = lo + centre % 2
        while lo >= 0 and hi < n and s[lo] == s[hi]:
            total += 1
            lo -= 1
            hi += 1
    return total
''',
    tests=[["aaa"], ["abc"], ["a"], ["ab"], ["aa"], ["abba"], ["racecar"], ["abababab"], ["12321"], ["aabaa"], ["zzzzzzzzzz"]],
)
_r = rnd(7006)
p["tests"].append(["a" * 2000])
p["tests"].append([_rs(_r, 2000, LD)])
p["tests"].append([_rs(_r, 2000, "ab")])
p["tests"].append(["ab" * 1000])
p["tests"].append([("a" * 700 + "b") * 2 + "c" * 598])


def b_cps(s):
    n = len(s)
    cnt = 0
    for i in range(n):
        for j in range(i, n):
            if all(s[i + k] == s[j - k] for k in range((j - i + 1) // 2)):
                cnt += 1
    return cnt


def g_cps(r):
    return [_rs(r, r.randint(1, 12), "ab" if r.random() < 0.6 else "abc")]


def v_cps(tests):
    for t in tests:
        s = t["args"][0]
        assert 1 <= len(s) <= 2000 and all(c in LD for c in s)


CHECKS["count-palindromic-substrings"] = (b_cps, g_cps, "exact")
VALIDATE["count-palindromic-substrings"] = v_cps

p = add(
    id="count-anagram-windows", title="Count Anagram Windows", diff="Medium", topic="Strings",
    fn="countAnagramWindows", params=[("s", "string"), ("p", "string")], ret="int", cmp="exact",
    desc="<p>Given a text <code>s</code> and a pattern <code>p</code>, count the substrings of <code>s</code> that are anagrams of <code>p</code>. A substring is an anagram of <code>p</code> if it has the same length as <code>p</code> and contains exactly the same characters with the same multiplicities (in any order). Substrings are counted by their starting position, so overlapping matches all count.</p><p>For example, with <code>s = \"cbaebabacd\"</code> and <code>p = \"abc\"</code> the matching windows start at indices 0 (<code>cba</code>), 6 (<code>bac</code>), so the answer is <code>2</code>. With <code>s = \"aaaa\"</code> and <code>p = \"aa\"</code> the answer is <code>3</code>. If <code>p</code> is longer than <code>s</code> the answer is <code>0</code>.</p>",
    constraints=["1 &le; s.length, p.length &le; 30,000", "s and p consist of lowercase letters and digits"],
    hints=["Sorting every window of length <code>p.length</code> and comparing with sorted <code>p</code> is correct but slow for big inputs.",
           "Consecutive windows differ by one character leaving and one entering. Maintain character counts instead of recomputing them.",
           "Keep the difference between the needed counts and the window counts, and track how many characters have a non-zero difference. A window matches when that number is zero."],
    editorial=["Slide a window of length <code>m = len(p)</code> over <code>s</code>. Store, for each character, <code>need[c] - window[c]</code>, and keep a counter of how many characters currently have a non-zero value. Adding the new character on the right and removing the old one on the left each update one entry and possibly change the counter by one. Whenever the counter is zero, the window is an anagram of <code>p</code>.",
               "Each step does constant work, so the total time is O(n + m). Recomputing counts from scratch for every window costs O(n &middot; m), and sorting each window O(n &middot; m log m), both too slow when both strings are around 30,000 characters long."],
    time="O(n + m)", space="O(1)",
    solution='''def countAnagramWindows(s, p):
    n, m = len(s), len(p)
    if m > n:
        return 0
    bal = {}
    for c in p:
        bal[c] = bal.get(c, 0) + 1
    nonzero = len(bal)
    count = 0

    def shift(c, d):
        nonlocal nonzero
        before = bal.get(c, 0)
        after = before + d
        bal[c] = after
        if before == 0 and after != 0:
            nonzero += 1
        elif before != 0 and after == 0:
            nonzero -= 1

    for i in range(n):
        shift(s[i], -1)
        if i >= m:
            shift(s[i - m], 1)
        if i >= m - 1 and nonzero == 0:
            count += 1
    return count
''',
    tests=[["cbaebabacd", "abc"], ["aaaa", "aa"], ["abab", "ab"], ["a", "a"], ["a", "b"], ["ab", "abc"], ["abc", "abc"], ["abc", "cba"],
           ["12312345", "321"], ["xyzzyx", "zyx"], ["aabaabaa", "aab"], ["abcdef", "ghi"]],
)
_r = rnd(7007)
p["tests"].append(["a" * 30000, "a" * 15000])
p["tests"].append([_rs(_r, 30000, "ab"), "ab" * 3])
p["tests"].append([_rs(_r, 30000, "abc"), "abcabc"[:5]])
_pt = _rs(_r, 2000, LD)
_txt = ""
while len(_txt) < 29000:
    _w = list(_pt); _r.shuffle(_w)
    _txt += "".join(_w) if _r.random() < 0.5 else _rs(_r, 1500, LD)
p["tests"].append([_txt[:30000], _pt])
p["tests"].append([_rs(_r, 30000, LD), _rs(_r, 30000, LD)])
p["tests"].append(["ab" * 15000, "ba"])


def b_anag(s, pat):
    m = len(pat)
    sp = sorted(pat)
    return sum(1 for i in range(len(s) - m + 1) if sorted(s[i:i + m]) == sp)


def g_anag(r):
    s = _rs(r, r.randint(1, 14), "abc")
    pat = _rs(r, r.randint(1, 4), "abc")
    return [s, pat]


def v_anag(tests):
    for t in tests:
        s, pt = t["args"]
        assert 1 <= len(s) <= 30000 and 1 <= len(pt) <= 30000
        assert all(c in LD for c in s + pt)


CHECKS["count-anagram-windows"] = (b_anag, g_anag, "exact")
VALIDATE["count-anagram-windows"] = v_anag

p = add(
    id="minimum-deletions-a-before-b", title="Minimum Deletions: All A's Before B's", diff="Medium", topic="Strings",
    fn="minDeletionsToOrder", params=[("s", "string")], ret="int", cmp="exact",
    desc="<p>You are given a string <code>s</code> made only of the letters <code>a</code> and <code>b</code>. You may delete any characters you like. After the deletions, the remaining string must be <em>ordered</em>: no <code>b</code> may appear before an <code>a</code> (so it looks like <code>aaa...abbb...b</code>, and either part may be empty).</p><p>Return the minimum number of characters you must delete. For example <code>\"aababbab\"</code> needs <code>2</code> deletions, and <code>\"bbaaaaabb\"</code> needs <code>2</code>. A string that is already ordered needs <code>0</code>.</p>",
    constraints=["1 &le; s.length &le; 50,000", "s[i] is either 'a' or 'b'"],
    hints=["In the final string there is a split point: only a's on the left of it and only b's on the right.",
           "For a fixed split, you must delete every b on the left and every a on the right. Try all n+1 splits using prefix counts.",
           "It can also be done in one pass: keep <code>bCount</code> and <code>best</code>. On 'b' increase <code>bCount</code>; on 'a', set <code>best = min(best + 1, bCount)</code>."],
    editorial=["Fix a split position. Everything left of it should be a and everything right should be b, so the cost is the number of b's on the left plus the number of a's on the right. Computing this for every split with a running count of b's and a total count of a's gives an O(n) solution with a single minimum over the splits.",
               "The one-pass dynamic-programming form is more compact. Let <code>best</code> be the minimum deletions to order the prefix seen so far, and <code>b</code> the number of b's seen. A new <code>b</code> can always be appended (just increment <code>b</code>). A new <code>a</code> either gets deleted (<code>best + 1</code>) or forces all earlier b's to be deleted (<code>b</code>), so <code>best = min(best + 1, b)</code>."],
    time="O(n)", space="O(1)",
    solution='''def minDeletionsToOrder(s):
    b = 0
    best = 0
    for c in s:
        if c == 'b':
            b += 1
        else:
            best = min(best + 1, b)
    return best
''',
    tests=[["aababbab"], ["bbaaaaabb"], ["a"], ["b"], ["ab"], ["ba"], ["aaabbb"], ["bbbaaa"], ["abababab"], ["babababa"], ["bbbbbaaaaabbbbbaaaaa"]],
)
_r = rnd(7008)
p["tests"].append([_rs(_r, 50000, "ab")])
p["tests"].append(["a" * 25000 + "b" * 25000])
p["tests"].append(["b" * 25000 + "a" * 25000])
p["tests"].append(["ab" * 25000])
p["tests"].append([_rs(_r, 50000, "aaaab")])
p["tests"].append([_rs(_r, 50000, "abbbb")])


def b_del(s):
    n = len(s)
    if n > 12:
        # too many subsets: try every split point (a's left, b's right) with direct counting
        return min(s[:k].count("b") + s[k:].count("a") for k in range(n + 1))
    best = n
    for mask in range(1 << n):
        kept = [s[i] for i in range(n) if mask >> i & 1]
        if all(not (kept[i] == "b" and kept[j] == "a") for i in range(len(kept)) for j in range(i + 1, len(kept))):
            best = min(best, n - len(kept))
    return best


def g_del(r):
    return [_rs(r, r.randint(1, 10), "ab")]


def v_del(tests):
    for t in tests:
        s = t["args"][0]
        assert 1 <= len(s) <= 50000 and set(s) <= {"a", "b"}


CHECKS["minimum-deletions-a-before-b"] = (b_del, g_del, "exact")
VALIDATE["minimum-deletions-a-before-b"] = v_del


# ---------------------------------------------------------------- HARD

def _dp_stats(s, t):
    """(answer, largest intermediate dp value) of the classic distinct-subsequence table."""
    m = len(t)
    dp = [0] * (m + 1)
    dp[0] = 1
    mx = 1
    for c in s:
        for j in range(m, 0, -1):
            if t[j - 1] == c:
                dp[j] += dp[j - 1]
                mx = max(mx, dp[j])
    return dp[m], mx


p = add(
    id="distinct-subsequences-count", title="Distinct Subsequences", diff="Hard", topic="Strings",
    fn="numDistinct", params=[("s", "string"), ("t", "string")], ret="int", cmp="exact",
    desc="<p>Given two strings <code>s</code> and <code>t</code>, count in how many different ways <code>t</code> can be obtained as a subsequence of <code>s</code>. A subsequence keeps the original order of the characters it keeps; two ways are different if they use a different set of <em>positions</em> in <code>s</code>, even when the resulting letters are the same.</p><p>For example, <code>t = \"rabbit\"</code> can be picked from <code>s = \"rabbbit\"</code> in <code>3</code> ways (any one of the three <code>b</code>s can be left out), and <code>t = \"bag\"</code> can be picked from <code>s = \"babgbag\"</code> in <code>5</code> ways. If <code>t</code> cannot be formed, return <code>0</code>.</p>",
    constraints=["1 &le; s.length, t.length &le; 1,000", "s and t consist of lowercase letters and digits", "The answer (and every intermediate count in the standard table) fits in a signed 32-bit integer"],
    hints=["Enumerating every subsequence of <code>s</code> is exponential. Look at the last character of <code>s</code> and ask how it can be used.",
           "Let <code>ways[i][j]</code> be the number of ways to form the first <code>j</code> characters of <code>t</code> from the first <code>i</code> characters of <code>s</code>. The last character of <code>s</code> is either skipped or, if it equals <code>t[j-1]</code>, used as the last character of the match.",
           "<code>ways[i][j] = ways[i-1][j] + (ways[i-1][j-1] if s[i-1] == t[j-1] else 0)</code>, with <code>ways[i][0] = 1</code>. The table can be compressed to one row if <code>j</code> is iterated downwards."],
    editorial=["Use dynamic programming over prefixes. Let <code>ways[i][j]</code> be the number of ways the prefix <code>t[:j]</code> is a subsequence of <code>s[:i]</code>. The empty target can be formed in exactly one way (take nothing), so <code>ways[i][0] = 1</code>, and a non-empty target cannot be formed from an empty source, so <code>ways[0][j] = 0</code> for <code>j &gt; 0</code>. For the general case, either the character <code>s[i-1]</code> is not used, contributing <code>ways[i-1][j]</code>, or it is matched with <code>t[j-1]</code> (only possible when they are equal), contributing <code>ways[i-1][j-1]</code>.",
               "Each row depends only on the previous one, so a single array of length <code>len(t)+1</code> suffices as long as the inner loop runs from high <code>j</code> to low <code>j</code>; this avoids using the character <code>s[i-1]</code> twice. Time is O(|s| &middot; |t|), about a million updates for the largest input. Plain recursion without memoisation repeats the same sub-problems and is exponential."],
    time="O(|s| * |t|)", space="O(|t|)",
    solution='''def numDistinct(s, t):
    m = len(t)
    dp = [0] * (m + 1)
    dp[0] = 1
    for c in s:
        for j in range(m, 0, -1):
            if t[j - 1] == c:
                dp[j] += dp[j - 1]
    return dp[m]
''',
    tests=[["rabbbit", "rabbit"], ["babgbag", "bag"], ["a", "a"], ["a", "b"], ["abc", "abcd"], ["aaaa", "aa"], ["abcabc", "abc"],
           ["a" * 33, "a" * 16], ["12121", "121"], ["xyz", "zyx"], ["aabbcc", "abc"], ["ab" * 6, "ab" * 3]],
)
_r = rnd(7009)
p["tests"].append(["a" * 1000, "a" * 3])
p["tests"].append(["a" * 1000, "a" * 2])
p["tests"].append(["a" * 1000, "a"])
p["tests"].append(["a" * 1000, "b"])


def _big_case(r, n, mlen, alpha, hit):
    for _ in range(200):
        s = _rs(r, n, alpha)
        if hit:
            idx = sorted(r.sample(range(n), mlen))
            t = "".join(s[i] for i in idx)
        else:
            t = _rs(r, mlen, alpha)
        ans, mx = _dp_stats(s, t)
        if mx <= INT_MAX and (ans > 0) == hit:
            return [s, t]
    raise RuntimeError("could not build a bounded case")


p["tests"].append(_big_case(_r, 1000, 10, LD, True))
p["tests"].append(_big_case(_r, 1000, 3, "abc", True))
p["tests"].append(_big_case(_r, 1000, 6, LD, True))
p["tests"].append(_big_case(_r, 1000, 12, LD, True))
p["tests"].append(_big_case(_r, 1000, 4, "abcdef", True))
p["tests"].append(_big_case(_r, 1000, 1, "ab", True))
p["tests"].append(["a" * 600 + "b" * 400, "b" + "a" * 10])
p["tests"].append(["ab" * 500, "bab"])
p["tests"].append(["a" * 100 + "b" * 100 + "c" * 100 + "d" * 100 + "e" * 600, "abcd"])
for _s_, _t_ in ((LD * 2, LD), (LD * 3, LD), (LD * 27, LD[:12])):
    if _dp_stats(_s_, _t_)[1] <= INT_MAX:
        p["tests"].append([_s_, _t_])


def b_dist(s, t):
    n, m = len(s), len(t)
    from math import comb
    if comb(n, m) > 100000:
        from functools import lru_cache

        @lru_cache(maxsize=None)
        def go(i, j):
            if j == m:
                return 1
            if i == n:
                return 0
            return go(i + 1, j) + (go(i + 1, j + 1) if s[i] == t[j] else 0)
        import sys
        sys.setrecursionlimit(10000)
        return go(0, 0)
    return sum(1 for idx in combinations(range(n), m) if all(s[i] == c for i, c in zip(idx, t)))


def g_dist(r):
    alpha = "ab" if r.random() < 0.6 else "abc"
    return [_rs(r, r.randint(1, 10), alpha), _rs(r, r.randint(1, 4), alpha)]


def v_dist(tests):
    for t in tests:
        s, u = t["args"]
        assert 1 <= len(s) <= 1000 and 1 <= len(u) <= 1000
        assert all(c in LD for c in s + u)
        ans, mx = _dp_stats(s, u)
        assert mx <= INT_MAX, ("intermediate overflow", s[:20], u[:20])
        assert t["expected"] == ans


CHECKS["distinct-subsequences-count"] = (b_dist, g_dist, "exact")
VALIDATE["distinct-subsequences-count"] = v_dist

p = add(
    id="shortest-palindrome-length", title="Shortest Palindrome Length", diff="Hard", topic="Strings",
    fn="shortestPalindromeLength", params=[("s", "string")], ret="int", cmp="exact",
    desc="<p>You may add characters only at the <strong>front</strong> of the string <code>s</code>; nothing can be inserted in the middle or at the end. Find the shortest palindrome you can create this way and return its length.</p><p>For example, for <code>s = \"aacecaaa\"</code> you can prepend a single <code>a</code> to get <code>\"aaacecaaa\"</code>, so the answer is <code>9</code>. For <code>s = \"abcd\"</code> you must prepend <code>\"dcb\"</code> to get <code>\"dcbabcd\"</code>, so the answer is <code>7</code>. If <code>s</code> is already a palindrome the answer is <code>len(s)</code>.</p>",
    constraints=["1 &le; s.length &le; 10,000", "s consists of lowercase letters and digits"],
    hints=["Whatever you add is determined by how much of the start of <code>s</code> is already a palindrome.",
           "If the longest palindromic <em>prefix</em> of <code>s</code> has length <code>k</code>, the remaining <code>n - k</code> characters must be mirrored in front, so the answer is <code>2n - k</code>.",
           "Find <code>k</code> in linear time with the KMP prefix function on <code>s + '#' + reverse(s)</code>: the last value of the prefix function is the length of the longest prefix of <code>s</code> that equals a suffix of <code>reverse(s)</code>, i.e. a palindromic prefix."],
    editorial=["Let <code>k</code> be the length of the longest prefix of <code>s</code> that is a palindrome. The characters after that prefix cannot be part of the palindromic core, so their reverse must be placed in front, giving a result of length <code>n + (n - k) = 2n - k</code>. Any shorter result would need a longer palindromic prefix, contradicting maximality of <code>k</code>.",
               "Checking every prefix for palindromicity costs O(n&sup2;), acceptable only for small inputs. To get O(n), build <code>t = s + '#' + reverse(s)</code> and compute the KMP failure (prefix) function. The final value <code>pi[-1]</code> is exactly <code>k</code>: a prefix of <code>s</code> that matches a suffix of <code>reverse(s)</code> is a prefix that equals its own reversal. The separator keeps the match from crossing the boundary (the alphabet never contains <code>#</code>)."],
    time="O(n)", space="O(n)",
    solution='''def shortestPalindromeLength(s):
    n = len(s)
    t = s + '#' + s[::-1]
    pi = [0] * len(t)
    for i in range(1, len(t)):
        k = pi[i - 1]
        while k and t[i] != t[k]:
            k = pi[k - 1]
        if t[i] == t[k]:
            k += 1
        pi[i] = k
    return 2 * n - pi[-1]
''',
    tests=[["aacecaaa"], ["abcd"], ["a"], ["ab"], ["aa"], ["aba"], ["abb"], ["abab"], ["aabba"], ["123"], ["abcba"], ["zzzzy"], ["abacabad"]],
)
_r = rnd(7010)
p["tests"].append([_rs(_r, 10000, LD)])
p["tests"].append(["a" * 9999 + "b"])
p["tests"].append(["b" + "a" * 9999])
_h = _rs(_r, 5000, "ab")
p["tests"].append([_h + _h[::-1]])
p["tests"].append([_h + _h[::-1][1:]])
_core = _rs(_r, 3000, "abc")
p["tests"].append([_core + "x" + _core[::-1] + _rs(_r, 3999, "abc")])
p["tests"].append([_rs(_r, 10000, "ab")])
p["tests"].append(["ab" * 5000])


def b_shortpal(s):
    n = len(s)
    for add_ in range(n + 1):
        cand = s[n - add_:][::-1] + s if add_ else s
        if cand == cand[::-1]:
            return len(cand)
    return 2 * n


def g_shortpal(r):
    if r.random() < 0.4:
        h = _rs(r, r.randint(1, 4), "ab")
        return [h + r.choice(["", "a", "b"]) + h[::-1] + _rs(r, r.randint(0, 3), "ab")]
    return [_rs(r, r.randint(1, 10), "ab" if r.random() < 0.7 else "abc")]


def v_shortpal(tests):
    for t in tests:
        s = t["args"][0]
        assert 1 <= len(s) <= 10000 and all(c in LD for c in s)


CHECKS["shortest-palindrome-length"] = (b_shortpal, g_shortpal, "exact")
VALIDATE["shortest-palindrome-length"] = v_shortpal
