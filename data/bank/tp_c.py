"""Problems: two pointers on strings (palindromes, rule-based reversal, backspaces). See data/lib.py for the registry."""
from collections import deque  # noqa: F401

from lib import add, rnd, CHECKS, VALIDATE, gen_arr  # noqa: F401

LET = "abcdefghijklmnopqrstuvwxyz"
VOW = "aeiouAEIOU"


def _rs(r, n, alpha=LET):
    return "".join(r.choice(alpha) for _ in range(n))


def _is_pal(t):
    return t == t[::-1]


# ---------------------------------------------------------------- EASY

p = add(
    id="valid-palindrome-ii", title="Valid Palindrome II", diff="Easy", topic="Two Pointers", tier="must",
    fn="validPalindromeWithOneDeletion", params=[("s", "string")], ret="bool", cmp="exact",
    desc="<p>Given a string <code>s</code> of lowercase letters, return <code>true</code> if <code>s</code> is a palindrome or can become a palindrome after deleting <strong>at most one</strong> character (at any position). Otherwise return <code>false</code>.</p><p>For example, <code>\"aba\"</code> gives <code>true</code>; <code>\"abca\"</code> gives <code>true</code> (delete <code>b</code> or <code>c</code>); <code>\"abc\"</code> gives <code>false</code>.</p>",
    constraints=["1 &le; s.length &le; 100,000", "s consists of lowercase English letters"],
    hints=["Trying every deletion and testing the result for being a palindrome is O(n&sup2;). Can you find out which deletions are worth trying?",
           "Compare from both ends with two pointers. As long as the characters match, nothing needs to be deleted.",
           "At the first mismatch <code>s[l] != s[r]</code>, the only candidates are deleting <code>s[l]</code> or deleting <code>s[r]</code>. Check whether <code>s[l+1..r]</code> or <code>s[l..r-1]</code> is a palindrome."],
    editorial=["Walk two pointers inward from both ends while the characters are equal. If they meet, the string is already a palindrome. At the first mismatch at positions <code>l</code> and <code>r</code>, one of the two characters has to be deleted, because every pair outside them already matches and a deletion elsewhere cannot repair this pair. So the answer is true exactly when <code>s[l+1..r]</code> or <code>s[l..r-1]</code> is a palindrome.",
               "Each palindrome test is a plain two-pointer scan, and it happens at most twice, so the total time is O(n). The extra space is O(1) if you compare indices instead of slicing."],
    time="O(n)", space="O(1)",
    solution='''def validPalindromeWithOneDeletion(s):
    def pal(i, j):
        while i < j:
            if s[i] != s[j]:
                return False
            i += 1
            j -= 1
        return True

    l, r = 0, len(s) - 1
    while l < r:
        if s[l] != s[r]:
            return pal(l + 1, r) or pal(l, r - 1)
        l += 1
        r -= 1
    return True
''',
    tests=[["aba"], ["abca"], ["abc"], ["a"], ["ab"], ["aaab"], ["abcdef"], ["raceacar"], ["deeee"], ["eeeed"],
           ["abcba"], ["abccbxa"], ["abcxba"]],
)
_r = rnd(9101)
_h = _rs(_r, 14999, "ab")
_pal = _h + "c" + _h[::-1]
p["tests"].append([_pal[:7000] + "z" + _pal[7000:]])                      # one extra letter: true
p["tests"].append([_pal[:7000] + "z" + _pal[7000:20000] + "y" + _pal[20000:]])  # two extra letters: false
_h = _rs(_r, 14999, "ab")
p["tests"].append([_h + "ab" + _h[::-1]])                                  # mismatch in the middle, two ways: true
p["tests"].append([_h + "abc" + _h[::-1]])                                 # false


def b_vp2(s):
    if _is_pal(s):
        return True
    return any(_is_pal(s[:i] + s[i + 1:]) for i in range(len(s)))


def g_vp2(r):
    n = r.randint(1, 9)
    s = _rs(r, n, r.choice(["ab", "abc"]))
    if r.random() < 0.6:
        h = _rs(r, n // 2, "abc")
        s = h + (r.choice("abc") if n % 2 else "") + h[::-1]
        if r.random() < 0.7 and s:
            i = r.randrange(len(s) + 1)
            s = s[:i] + r.choice("abc") + s[i:]
    return [s]


def v_vp2(tests):
    for t in tests:
        s = t["args"][0]
        assert 1 <= len(s) <= 100000 and all("a" <= c <= "z" for c in s)
    assert any(t["expected"] for t in tests) and not all(t["expected"] for t in tests)


CHECKS["valid-palindrome-ii"] = (b_vp2, g_vp2, "exact")
VALIDATE["valid-palindrome-ii"] = v_vp2

p = add(
    id="reverse-vowels-of-string", title="Reverse Vowels of a String", diff="Easy", topic="Two Pointers",
    fn="reverseVowels", params=[("s", "string")], ret="string", cmp="exact",
    desc="<p>Given a string <code>s</code> of English letters (upper and lower case), reverse the <strong>order of its vowels</strong> and leave every other character where it is. The vowels are <code>a, e, i, o, u</code> in both lower and upper case. Characters keep their case; only the positions of the vowels are swapped among themselves.</p><p>For example, <code>\"hello\"</code> becomes <code>\"holle\"</code>, and <code>\"Education\"</code> becomes <code>\"odicatuEn\"</code> (the vowels <code>E u a i o</code> are rewritten as <code>o i a u E</code>).</p>",
    constraints=["1 &le; s.length &le; 100,000", "s consists of upper and lower case English letters"],
    hints=["Collect the vowels, reverse that list, and write them back. That works with O(n) extra memory. Can you swap in place?",
           "Use one pointer from each end. Move the left one right until it sits on a vowel, and the right one left until it sits on a vowel.",
           "Swap the two vowels, move both pointers one step inward and continue until the pointers meet."],
    editorial=["Keep a pointer <code>i</code> at the start and <code>j</code> at the end of a character array. Advance <code>i</code> while it is not on a vowel and retreat <code>j</code> while it is not on a vowel. If <code>i &lt; j</code>, swap the two characters and move both pointers. When they meet, every vowel pair has been swapped, which is exactly the reversal of the vowel sequence.",
               "Each position is visited at most once, so the time is O(n); the array copy of the string uses O(n) space, which is unavoidable if strings are immutable. Remember to treat upper-case vowels as vowels as well."],
    time="O(n)", space="O(n)",
    solution='''def reverseVowels(s):
    vowels = set("aeiouAEIOU")
    a = list(s)
    i, j = 0, len(a) - 1
    while i < j:
        if a[i] not in vowels:
            i += 1
        elif a[j] not in vowels:
            j -= 1
        else:
            a[i], a[j] = a[j], a[i]
            i += 1
            j -= 1
    return "".join(a)
''',
    tests=[["hello"], ["Education"], ["a"], ["b"], ["aeiou"], ["AbcdE"], ["xyz"], ["Aa"], ["rhythm"], ["queueing"],
           ["bAnAnA"]],
)
_r = rnd(9102)
p["tests"].append([_rs(_r, 8000, "abcdeAEIOUxyzu")])
p["tests"].append([_rs(_r, 8000, "bcdfghjklmnpqrstvwxyz") + "a" + _rs(_r, 4000, "bcdfg") + "E"])
p["tests"].append([_rs(_r, 6000, "aeiouAEIOUb")])


def b_rv(s):
    vs = [c for c in s if c in VOW]
    vs.reverse()
    it = iter(vs)
    return "".join(next(it) if c in VOW else c for c in s)


def g_rv(r):
    return [_rs(r, r.randint(1, 10), "abeEiIxyzAou")]


def v_rv(tests):
    for t in tests:
        s = t["args"][0]
        assert 1 <= len(s) <= 100000 and s.isalpha() and s.isascii()
        assert len(t["expected"]) == len(s)


CHECKS["reverse-vowels-of-string"] = (b_rv, g_rv, "exact")
VALIDATE["reverse-vowels-of-string"] = v_rv

p = add(
    id="backspace-string-compare", title="Compare Texts With Backspaces", diff="Easy", topic="Two Pointers",
    fn="backspaceCompare", params=[("s", "string"), ("t", "string")], ret="bool", cmp="exact",
    desc="<p>Two texts <code>s</code> and <code>t</code> were typed on a keyboard. A lowercase letter types that letter, and the character <code>#</code> is the backspace key, which deletes the character just before the cursor. Pressing backspace when the text is empty does nothing.</p><p>Return <code>true</code> if the two final texts are equal, otherwise <code>false</code>. Two empty final texts are equal.</p><p>For example, <code>\"ab#c\"</code> and <code>\"ad#c\"</code> both end as <code>\"ac\"</code> (<code>true</code>); <code>\"a##c\"</code> and <code>\"#a#c\"</code> both end as <code>\"c\"</code> (<code>true</code>); <code>\"a#c\"</code> ends as <code>\"c\"</code> but <code>\"b\"</code> ends as <code>\"b\"</code> (<code>false</code>).</p><p>Try to solve it with O(1) extra space.</p>",
    constraints=["1 &le; s.length, t.length &le; 200,000", "s and t contain only lowercase letters and '#'"],
    hints=["Building both final texts with a stack and comparing them is easy. How could you compare without building them?",
           "A backspace only affects characters <em>before</em> it, so scanning from the end of each string tells you which characters survive.",
           "Scan both strings from the right with a pointer each. While scanning, keep a counter of pending backspaces: a <code>#</code> increases it, a letter with a pending backspace is skipped and decreases it. Compare the next surviving letters of both strings."],
    editorial=["Processing from the right means every backspace is seen before the characters it deletes. For each string keep a pointer and a count <code>skip</code> of backspaces still to be applied. A helper moves the pointer to the next surviving letter: on <code>#</code> do <code>skip += 1</code>; on a letter with <code>skip &gt; 0</code> do <code>skip -= 1</code>; otherwise the letter survives.",
               "Advance both pointers to their next surviving letters, then compare. If one string has run out while the other has not, or the letters differ, the answer is false. If both run out together, the answer is true. This takes O(n + m) time and O(1) extra space; the stack version has the same time but O(n + m) space."],
    time="O(n + m)", space="O(1)",
    solution='''def backspaceCompare(s, t):
    def nxt(x, i):
        skip = 0
        while i >= 0:
            if x[i] == '#':
                skip += 1
            elif skip > 0:
                skip -= 1
            else:
                return i
            i -= 1
        return -1

    i, j = len(s) - 1, len(t) - 1
    while True:
        i = nxt(s, i)
        j = nxt(t, j)
        if i < 0 or j < 0:
            return i < 0 and j < 0
        if s[i] != t[j]:
            return False
        i -= 1
        j -= 1
''',
    tests=[["ab#c", "ad#c"], ["a##c", "#a#c"], ["a#c", "b"], ["a", "a"], ["#", "##"], ["a#", "b#"], ["ab", "ba"],
           ["abc###", "d#"], ["xy#z", "xz"], ["a#b#c#", "#"], ["ab##", "c#d#"], ["abc#", "ab"]],
)
_r = rnd(9103)


def _typed(r, n):
    return "".join("#" if r.random() < 0.35 else r.choice("abc") for _ in range(n))


def _final(x):
    st = []
    for c in x:
        if c == "#":
            if st:
                st.pop()
        else:
            st.append(c)
    return "".join(st)


_a = _typed(_r, 12000)
_b = "z" * 5 + "#" * 5 + _a  # same final text, different typing
p["tests"].append([_a, _b])
_c = _a[:6000] + "q#" + _a[6000:]
p["tests"].append([_a, _c])
_c = _a + "b#b#"
p["tests"].append([_a + "a", _c + "a"])
_a = "a" * 6000 + "#" * 6000
p["tests"].append([_a, "#"])
p["tests"].append([_typed(_r, 12000), _typed(_r, 12000)])


def b_bs(s, t):
    return _final(s) == _final(t)


def g_bs(r):
    s = _typed(r, r.randint(1, 8))
    t = _typed(r, r.randint(1, 8)) if r.random() < 0.4 else "".join(r.choice("abc#") for _ in range(r.randint(1, 8)))
    if r.random() < 0.5:
        t = r.choice(["", "a#", "b#", "c"]) + s
    return [s, t]


def v_bs(tests):
    for t in tests:
        s, u = t["args"]
        assert 1 <= len(s) <= 200000 and 1 <= len(u) <= 200000
        assert all(c == "#" or "a" <= c <= "z" for c in s + u)
    assert sum(1 for t in tests if t["expected"]) >= 3 and sum(1 for t in tests if not t["expected"]) >= 3


CHECKS["backspace-string-compare"] = (b_bs, g_bs, "exact")
VALIDATE["backspace-string-compare"] = v_bs

# ---------------------------------------------------------------- MEDIUM

p = add(
    id="one-edit-apart", title="One Edit Apart", diff="Medium", topic="Two Pointers",
    fn="isOneEditApart", params=[("s", "string"), ("t", "string")], ret="bool", cmp="exact",
    desc="<p>An <em>edit</em> is one of: inserting a single character anywhere, deleting a single character, or replacing a single character by a different one.</p><p>Given strings <code>s</code> and <code>t</code>, return <code>true</code> if <code>t</code> can be obtained from <code>s</code> with <strong>exactly one</strong> edit, otherwise <code>false</code>. Identical strings need zero edits, so for them the answer is <code>false</code>.</p><p>For example, <code>\"pale\"</code> and <code>\"ple\"</code> give <code>true</code> (delete <code>a</code>); <code>\"pale\"</code> and <code>\"bale\"</code> give <code>true</code> (replace); <code>\"pale\"</code> and <code>\"pale\"</code> give <code>false</code>; <code>\"pale\"</code> and <code>\"bake\"</code> give <code>false</code> (two replacements).</p>",
    constraints=["1 &le; s.length, t.length &le; 100,000", "s and t consist of lowercase letters and digits"],
    hints=["The general edit distance needs a quadratic table. Here you only need to know whether it is exactly 1, which restricts the lengths a lot.",
           "If the lengths differ by more than one, the answer is false. Otherwise find the first position where the strings differ, scanning from the left.",
           "At the first difference: if the lengths are equal, the rests after that position must be equal (replace); if one string is longer by one, the longer string must equal the shorter one when its differing character is skipped (insert/delete). If there is no difference at all, the answer is true only when the lengths differ by one."],
    editorial=["Let <code>s</code> be the shorter (or equal length) string after a possible swap. If <code>len(t) - len(s) &gt; 1</code>, return false. Find the first index <code>i</code> where the strings differ. If none exists inside the shorter string, the strings are equal up to <code>len(s)</code>, so one edit is possible exactly when <code>t</code> has one extra character at the end.",
               "Otherwise there is a difference at <code>i</code>. For equal lengths, a single replacement fixes it only if <code>s[i+1:] == t[i+1:]</code>. For lengths differing by one, the extra character must be <code>t[i]</code>, so we need <code>s[i:] == t[i+1:]</code>. Everything is one scan plus one comparison of suffixes: O(n) time. Greedy matching of the common prefix is safe because the first difference is where the single edit has to happen."],
    time="O(n)", space="O(1)",
    solution='''def isOneEditApart(s, t):
    if abs(len(s) - len(t)) > 1:
        return False
    if len(s) > len(t):
        s, t = t, s
    i = 0
    while i < len(s) and s[i] == t[i]:
        i += 1
    if i == len(s):
        return len(t) == len(s) + 1
    if len(s) == len(t):
        return s[i + 1:] == t[i + 1:]
    return s[i:] == t[i + 1:]
''',
    tests=[["pale", "ple"], ["pale", "bale"], ["pale", "pale"], ["pale", "bake"], ["a", "b"], ["a", "a"], ["a", "ab"],
           ["ab", "a"], ["abc", "abcd"], ["abc", "xabc"], ["abcd", "abxd"], ["ab", "ba"], ["aa", "a"], ["abc", "abcde"]],
)
_r = rnd(9104)
_a = _rs(_r, 15000, "ab")
p["tests"].append([_a, _a[:9000] + _a[9001:]])
p["tests"].append([_a, _a[:12000] + ("a" if _a[12000] == "b" else "b") + _a[12001:]])
p["tests"].append([_a, _a[:3000] + "xy" + _a[3001:]])
p["tests"].append([_a + "b", _a + "a"])


def _lev(a, b):
    prev = list(range(len(b) + 1))
    for i in range(1, len(a) + 1):
        cur = [i] + [0] * len(b)
        for j in range(1, len(b) + 1):
            cur[j] = min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (a[i - 1] != b[j - 1]))
        prev = cur
    return prev[-1]


def b_oe(s, t):
    return _lev(s, t) == 1


def g_oe(r):
    s = _rs(r, r.randint(1, 6), "ab")
    k = r.random()
    if k < 0.5:
        t = list(s)
        op = r.randint(0, 2)
        i = r.randrange(len(t))
        if op == 0:
            t[i] = r.choice("abc")
        elif op == 1:
            t.insert(i, r.choice("abc"))
        elif len(t) > 1:
            del t[i]
        t = "".join(t)
    else:
        t = _rs(r, r.randint(1, 6), "ab")
    return [s, t]


def v_oe(tests):
    for t in tests:
        s, u = t["args"]
        assert 1 <= len(s) <= 100000 and 1 <= len(u) <= 100000
        assert all(c.isalnum() and c.islower() or c.isdigit() for c in s + u)
    assert any(t["expected"] for t in tests) and not all(t["expected"] for t in tests)


CHECKS["one-edit-apart"] = (b_oe, g_oe, "exact")
VALIDATE["one-edit-apart"] = v_oe

p = add(
    id="count-deletions-making-palindrome", title="Deletion Spots for a Palindrome", diff="Medium", topic="Two Pointers", tier="extra",
    fn="countDeletionSpots", params=[("s", "string")], ret="int", cmp="exact",
    desc="<p>For the string <code>s</code>, count the <strong>positions</strong> <code>i</code> (0-indexed) such that deleting the character <code>s[i]</code> leaves a palindrome. Positions are counted separately even when they produce the same string. The empty string counts as a palindrome.</p><p>For example, <code>\"abca\"</code> gives <code>2</code> (delete <code>b</code> to get <code>\"aca\"</code> or <code>c</code> to get <code>\"aba\"</code>); <code>\"aaabaa\"</code> gives <code>4</code> (deleting any of the first three <code>a</code> or the <code>b</code> works); <code>\"aaaa\"</code> gives <code>4</code>; <code>\"abc\"</code> gives <code>0</code>.</p>",
    constraints=["1 &le; s.length &le; 100,000", "s consists of lowercase English letters"],
    hints=["Testing each of the n deletions costs O(n) each. Think about which deletions could possibly help.",
           "Scan from both ends while characters match. If everything matches, the string is a palindrome; otherwise the first mismatch at <code>l</code> and <code>r</code> limits the candidate characters to <code>s[l]</code> and <code>s[r]</code>.",
           "Deleting any character of a maximal run of equal letters gives the same string, so one successful check is worth the whole run length. For a palindrome itself, only deletions inside the run of equal letters at the centre keep it a palindrome."],
    editorial=["Case 1: <code>s</code> is a palindrome. Deleting position <code>i</code> keeps a palindrome exactly when <code>i</code> lies in the maximal run of equal letters that contains the centre (for even length, the two middle letters are equal and belong to the same run). Deleting anything else shifts one half against the other and breaks the symmetry. The answer is the length of that run.",
               "Case 2: not a palindrome. Let <code>l, r</code> be the first mismatch. Any single deletion that works must remove a letter equal to <code>s[l]</code> from the run containing <code>l</code>, or a letter from the run containing <code>r</code>, because those are the only deletions that change what faces the mismatch. Test <code>s[l+1..r]</code> and <code>s[l..r-1]</code> for being palindromes; for each success add the length of the corresponding run in the whole string (all positions in a run produce the same result string). The two runs are different because <code>s[l] != s[r]</code>.",
               "Everything is linear: one scan, at most two palindrome checks and two run measurements. O(n) time, O(1) extra space apart from slicing."],
    time="O(n)", space="O(1)",
    solution='''def countDeletionSpots(s):
    n = len(s)

    def run(i):
        a = i
        while a > 0 and s[a - 1] == s[i]:
            a -= 1
        b = i
        while b < n - 1 and s[b + 1] == s[i]:
            b += 1
        return b - a + 1

    def pal(i, j):
        while i < j:
            if s[i] != s[j]:
                return False
            i += 1
            j -= 1
        return True

    l, r = 0, n - 1
    while l < r and s[l] == s[r]:
        l += 1
        r -= 1
    if l >= r:
        return run(n // 2)
    total = 0
    if pal(l + 1, r):
        total += run(l)
    if pal(l, r - 1):
        total += run(r)
    return total
''',
    tests=[["abca"], ["aaabaa"], ["aaaa"], ["abc"], ["a"], ["ab"], ["aa"], ["aba"], ["abba"], ["aabbaa"], ["ababa"],
           ["abcdcba"], ["abcddcbea"]],
)
_r = rnd(9105)
p["tests"].append(["a" * 30000])
_h = _rs(_r, 14000, "ab")
p["tests"].append([_h + "c" * 2000 + _h[::-1]])
p["tests"].append([_h + "a" * 2000 + "b" + "a" * 2000 + _h[::-1] + "a"])
p["tests"].append([_h + "ab" + _h[::-1]])


def b_cd(s):
    return sum(1 for i in range(len(s)) if _is_pal(s[:i] + s[i + 1:]))


def g_cd(r):
    n = r.randint(1, 10)
    alpha = r.choice(["ab", "abc", "a"])
    s = _rs(r, n, alpha)
    if r.random() < 0.5:
        h = _rs(r, n // 2, alpha)
        s = h + (r.choice(alpha) if n % 2 else "") + h[::-1]
        if r.random() < 0.6:
            i = r.randrange(len(s) + 1)
            s = s[:i] + r.choice(alpha) + s[i:]
    return [s]


def v_cd(tests):
    for t in tests:
        s = t["args"][0]
        assert 1 <= len(s) <= 100000 and all("a" <= c <= "z" for c in s)
    assert any(t["expected"] == 0 for t in tests) and any(t["expected"] > 2 for t in tests)


CHECKS["count-deletions-making-palindrome"] = (b_cd, g_cd, "exact")
VALIDATE["count-deletions-making-palindrome"] = v_cd

p = add(
    id="can-transform-lr-moves", title="Slide L and R Tokens", diff="Medium", topic="Two Pointers",
    fn="canSlideTransform", params=[("start", "string"), ("end", "string")], ret="bool", cmp="exact",
    desc="<p>A board is a string made of the characters <code>L</code>, <code>R</code> and <code>X</code>, where <code>X</code> is an empty cell. You may repeat the following moves any number of times:</p><ul><li>replace a substring <code>XL</code> by <code>LX</code> (an <code>L</code> slides one cell to the left into an empty cell),</li><li>replace a substring <code>RX</code> by <code>XR</code> (an <code>R</code> slides one cell to the right into an empty cell).</li></ul><p>Given two boards <code>start</code> and <code>end</code> of the same length, return <code>true</code> if <code>end</code> can be reached from <code>start</code> by such moves, otherwise <code>false</code>.</p><p>For example, <code>\"XLXRX\"</code> can become <code>\"LXXXR\"</code> (<code>true</code>), but <code>\"RXL\"</code> cannot become <code>\"LXR\"</code> (<code>false</code>): tokens never pass each other.</p>",
    constraints=["1 &le; start.length = end.length &le; 100,000", "start and end contain only the characters L, R and X"],
    hints=["Searching all reachable boards explodes quickly. Look for invariants of the moves instead.",
           "Tokens never jump over each other, so the sequence of <code>L</code>/<code>R</code> letters (ignoring <code>X</code>) cannot change.",
           "Match the k-th non-X character of <code>start</code> with the k-th non-X character of <code>end</code> using two pointers. An <code>L</code> can only move left, so its index in <code>end</code> must not be larger than in <code>start</code>; an <code>R</code> can only move right, so its index in <code>end</code> must not be smaller."],
    editorial=["Because <code>L</code> only swaps with an <code>X</code> on its left and <code>R</code> only with an <code>X</code> on its right, no two tokens can ever cross. Hence the sequence of tokens with the <code>X</code>s removed is invariant, and the k-th token of <code>start</code> must become the k-th token of <code>end</code>.",
               "Additionally, the k-th token can only travel in its own direction: if it is an <code>L</code> its position in <code>end</code> must be at most its position in <code>start</code>; if it is an <code>R</code> it must be at least. These conditions are also sufficient, since each token can walk to its destination through the gaps that the order-preserving matching leaves free. Two pointers that skip <code>X</code> implement the check in O(n) time and O(1) extra space."],
    time="O(n)", space="O(1)",
    solution='''def canSlideTransform(start, end):
    n = len(start)
    if n != len(end):
        return False
    i = j = 0
    while True:
        while i < n and start[i] == 'X':
            i += 1
        while j < n and end[j] == 'X':
            j += 1
        if i == n or j == n:
            return i == n and j == n
        if start[i] != end[j]:
            return False
        if start[i] == 'L' and i < j:
            return False
        if start[i] == 'R' and i > j:
            return False
        i += 1
        j += 1
''',
    tests=[["XLXRX", "LXXXR"], ["RXL", "LXR"], ["XL", "LX"], ["LX", "XL"], ["RX", "XR"], ["XR", "RX"], ["X", "X"],
           ["L", "L"], ["L", "R"], ["XXXX", "XXXX"], ["RXXLRXRXL", "XRLXXRRLX"], ["LRX", "LXR"], ["XRXLX", "XXRLX"]],
)
_r = rnd(9106)


def _board(r, n):
    return "".join(r.choice("LRXXX") for _ in range(n))


def _slide(r, s, steps):
    a = list(s)
    for _ in range(steps):
        i = r.randrange(len(a) - 1) if len(a) > 1 else 0
        if i + 1 < len(a):
            if a[i] == "X" and a[i + 1] == "L":
                a[i], a[i + 1] = "L", "X"
            elif a[i] == "R" and a[i + 1] == "X":
                a[i], a[i + 1] = "X", "R"
    return "".join(a)


_a = _board(_r, 12000)
p["tests"].append([_a, _slide(_r, _a, 60000)])
p["tests"].append([_a, _a[:5000] + _a[5001:] + _a[5000]])
_a = "X" * 5000 + "L" * 3000 + "R" * 3000 + "X" * 5000
p["tests"].append([_a, "L" * 3000 + "X" * 10000 + "R" * 3000])
p["tests"].append([_a, "L" * 3000 + "X" * 10000 + "R" * 2999 + "L"])
p["tests"].append(["R" * 3000 + "X" * 3000, "X" * 3000 + "R" * 3000])


def b_lr(start, end):
    if start == end:
        return True
    seen = {start}
    dq = deque([start])
    while dq:
        cur = dq.popleft()
        for i in range(len(cur) - 1):
            pair = cur[i:i + 2]
            if pair == "XL":
                nxt = cur[:i] + "LX" + cur[i + 2:]
            elif pair == "RX":
                nxt = cur[:i] + "XR" + cur[i + 2:]
            else:
                continue
            if nxt == end:
                return True
            if nxt not in seen:
                seen.add(nxt)
                dq.append(nxt)
    return False


def g_lr(r):
    n = r.randint(1, 7)
    s = _board(r, n)
    if r.random() < 0.55:
        t = _slide(r, s, r.randint(0, 25))
        if r.random() < 0.15 and n > 1:
            t = t[1:] + t[0]
    else:
        t = "".join(r.sample(s, n))
    return [s, t]


def v_lr(tests):
    for t in tests:
        s, u = t["args"]
        assert len(s) == len(u) and 1 <= len(s) <= 100000
        assert set(s + u) <= set("LRX")
    assert sum(1 for t in tests if t["expected"]) >= 3 and sum(1 for t in tests if not t["expected"]) >= 3


CHECKS["can-transform-lr-moves"] = (b_lr, g_lr, "exact")
VALIDATE["can-transform-lr-moves"] = v_lr

p = add(
    id="push-dominoes-final-state", title="Falling Dominoes", diff="Medium", topic="Two Pointers",
    fn="finalDominoes", params=[("dominoes", "string")], ret="string", cmp="exact",
    desc="<p>A row of dominoes is a string of the characters <code>L</code>, <code>R</code> and <code>.</code>. A domino <code>L</code> has been pushed to the left, <code>R</code> to the right, and <code>.</code> is a domino still standing.</p><p>Every second, a falling domino pushes the standing neighbour in its falling direction: an <code>R</code> pushes the domino to its right, an <code>L</code> pushes the domino to its left. A standing domino that is pushed from <strong>both</strong> sides in the same second stays standing (the forces cancel). A domino that has fallen never changes again, and a falling domino only pushes a domino that is still standing.</p><p>Return the final state when nothing changes any more.</p><p>For example, <code>\"..R...L..\"</code> becomes <code>\"..RR.LL..\"</code>; <code>\".L.R.\"</code> becomes <code>\"LL.RR\"</code>; <code>\"R.L\"</code> stays <code>\"R.L\"</code>.</p>",
    constraints=["1 &le; dominoes.length &le; 100,000", "dominoes contains only the characters L, R and ."],
    hints=["Simulating second by second works but can take O(n) rounds of O(n) work. Look at the row as segments between pushed dominoes.",
           "Add a virtual <code>L</code> at the start and a virtual <code>R</code> at the end of the row; they never change the result but remove special cases. Then look at each pair of consecutive non-dot symbols.",
           "For a pair of neighbours with dots between them: <code>R...L</code> meets in the middle (the middle dot stays if the count is odd), <code>L...R</code> leaves the dots standing, and equal symbols <code>R...R</code> or <code>L...L</code> fill all dots with that symbol."],
    editorial=["Only the nearest pushed domino on each side of a standing domino matters. Scan the string with a pointer <code>prev</code> on the last pushed domino and a pointer <code>i</code> on the next one, with a virtual <code>L</code> in front and a virtual <code>R</code> at the end. The dots strictly between fall in four possible ways: both ends equal means they all fall that way; <code>L</code> then <code>R</code> means they all stay standing since the forces point away; <code>R</code> then <code>L</code> means the left half falls right, the right half falls left, and a single middle dot (odd count) stays up because both forces reach it in the same second.",
               "The virtual ends keep the rule uniform: a leading <code>R</code> after the virtual <code>L</code> gives L-then-R (dots stay, but there are none before it), and a trailing <code>L</code> followed by the virtual <code>R</code> leaves nothing to push. The scan is linear in the length: O(n) time and O(n) space for the output array."],
    time="O(n)", space="O(n)",
    solution='''def finalDominoes(dominoes):
    s = 'L' + dominoes + 'R'
    out = list(s)
    prev = 0
    for i in range(1, len(s)):
        if s[i] == '.':
            continue
        a, b = s[prev], s[i]
        if a == b:
            for k in range(prev + 1, i):
                out[k] = a
        elif a == 'R' and b == 'L':
            lo, hi = prev + 1, i - 1
            while lo < hi:
                out[lo] = 'R'
                out[hi] = 'L'
                lo += 1
                hi -= 1
        prev = i
    return ''.join(out[1:-1])
''',
    tests=[["..R...L.."], [".L.R."], ["R.L"], ["L.R"], ["."], ["L"], ["R"], ["R.."], ["..L"], ["R...L"], ["R..L"],
           ["RR.L"], [".L.R...LR..L.."], ["R.R.L.L"]],
)
_r = rnd(9107)
p["tests"].append(["".join(_r.choice("..........LR") for _ in range(12000))])
p["tests"].append(["R" + "." * 11998 + "L"])
p["tests"].append(["R" + "." * 11999 + "L"])
p["tests"].append(["".join(_r.choice("LR") if _r.random() < 0.5 else "." for _ in range(12000))])


def b_pd(d):
    cur = list(d)
    while True:
        nxt = list(cur)
        for i, c in enumerate(cur):
            if c != ".":
                continue
            left = i > 0 and cur[i - 1] == "R"
            right = i + 1 < len(cur) and cur[i + 1] == "L"
            if left and not right:
                nxt[i] = "R"
            elif right and not left:
                nxt[i] = "L"
        if nxt == cur:
            return "".join(cur)
        cur = nxt


def g_pd(r):
    return ["".join(r.choice("..LR") for _ in range(r.randint(1, 12)))]


def v_pd(tests):
    for t in tests:
        s = t["args"][0]
        assert 1 <= len(s) <= 100000 and set(s) <= set("LR.")
        assert len(t["expected"]) == len(s)


CHECKS["push-dominoes-final-state"] = (b_pd, g_pd, "exact")
VALIDATE["push-dominoes-final-state"] = v_pd

p = add(
    id="longest-word-by-deleting", title="Longest Word by Deleting Letters", diff="Medium", topic="Two Pointers",
    fn="longestWordFromDeletion", params=[("s", "string"), ("words", "string")], ret="string", cmp="exact",
    desc="<p>You are given a string <code>s</code> and a dictionary, written as one string <code>words</code> where the dictionary words are separated by commas, for example <code>\"abc,xyz,ab\"</code>. A word can be <em>made from</em> <code>s</code> by deleting some (possibly zero) characters of <code>s</code> without reordering the rest, that is, if the word is a subsequence of <code>s</code>.</p><p>Return the longest dictionary word that can be made from <code>s</code>. If several have the longest length, return the one that is smallest in dictionary (alphabetical) order. If no word can be made, return <code>\"-\"</code>.</p><p>For example, <code>s = \"xaybzc\"</code> with <code>words = \"abc,xyz,ayz,xbc,ab,az\"</code> gives <code>\"abc\"</code>: four words of length 3 can be made, and <code>abc</code> is the alphabetically smallest. With <code>s = \"abc\"</code> and <code>words = \"d,e\"</code> the answer is <code>\"-\"</code>.</p>",
    constraints=["1 &le; s.length &le; 5,000", "The dictionary has between 1 and 1,000 words; each word has 1 to 50 lowercase letters (duplicates may occur)", "s consists of lowercase letters; words contains lowercase letters and commas only, with no empty word"],
    hints=["For each word you only need a yes/no answer: is it a subsequence of <code>s</code>?",
           "Use one pointer on <code>s</code> and one on the word. Move through <code>s</code>; every time the characters are equal, advance the pointer in the word. The word fits when its pointer reaches the end.",
           "Keep the best word so far and replace it when the new word is longer, or equally long and alphabetically smaller. No sorting is needed."],
    editorial=["Split <code>words</code> at commas. For each word run the standard two-pointer subsequence test: scan <code>s</code> once, and each time <code>s[i]</code> equals the next needed letter of the word, move to the next needed letter. If all letters were matched in order, the word can be made.",
               "Among feasible words keep the one with larger length, breaking ties by the smaller string. Each test costs O(|s|) in the worst case (or less when using a jump such as <code>find</code> from the last matched position), so the total is O(|s| &middot; W) for W words. A pre-sorted dictionary (by length descending, then alphabetically) lets you stop at the first feasible word, but the single pass is simpler and as fast in the worst case."],
    time="O(|s| * W)", space="O(1)",
    solution='''def longestWordFromDeletion(s, words):
    best = ""
    for w in words.split(","):
        pos = 0
        ok = True
        for c in w:
            pos = s.find(c, pos)
            if pos < 0:
                ok = False
                break
            pos += 1
        if ok and (len(w) > len(best) or (len(w) == len(best) and w < best)):
            best = w
    return best if best else "-"
''',
    tests=[["xaybzc", "abc,xyz,ayz,xbc,ab,az"], ["abc", "d,e"], ["abc", "abc"], ["a", "a,b"], ["abcde", "ace,ade,abd"],
           ["abcde", "edcba,eda,ed"], ["aaa", "aa,aaa,aaaa"], ["aaa", "b,a,b"], ["zzzz", "zz,z,zzz,zzz"],
           ["banana", "ban,ana,nan,bnn,aaa,bnna"]],
)
_r = rnd(9108)
_s = _rs(_r, 4000, LET)


def _sub(r, s, k):
    idx = sorted(r.sample(range(len(s)), k))
    return "".join(s[i] for i in idx)


_w = [_sub(_r, _s, _r.randint(3, 40)) for _ in range(300)] + [_rs(_r, _r.randint(3, 40), LET) for _ in range(400)]
p["tests"].append([_s, ",".join(_w)])
_s2 = _rs(_r, 5000, "ab")
_w = [_rs(_r, _r.randint(30, 50), "ab") for _ in range(900)]
p["tests"].append([_s2, ",".join(_w)])
_w = [_sub(_r, _s2, 50) for _ in range(5)] + ["b" * 50]
p["tests"].append([_s2, ",".join(_w)])


def b_lw(s, words):
    def lcs(a, b):
        dp = [[0] * (len(b) + 1) for _ in range(len(a) + 1)]
        for i in range(len(a)):
            for j in range(len(b)):
                dp[i + 1][j + 1] = dp[i][j] + 1 if a[i] == b[j] else max(dp[i][j + 1], dp[i + 1][j])
        return dp[-1][-1]

    ok = [w for w in words.split(",") if lcs(s, w) == len(w)]
    if not ok:
        return "-"
    return sorted(ok, key=lambda w: (-len(w), w))[0]


def g_lw(r):
    s = _rs(r, r.randint(1, 9), "abc")
    ws = [_rs(r, r.randint(1, 5), "abc") for _ in range(r.randint(1, 6))]
    return [s, ",".join(ws)]


def v_lw(tests):
    for t in tests:
        s, words = t["args"]
        ws = words.split(",")
        assert 1 <= len(s) <= 5000 and all("a" <= c <= "z" for c in s)
        assert 1 <= len(ws) <= 1000 and all(1 <= len(w) <= 50 and w.isalpha() and w.islower() for w in ws)
    assert any(t["expected"] == "-" for t in tests) and sum(1 for t in tests if t["expected"] != "-") >= 6


CHECKS["longest-word-by-deleting"] = (b_lw, g_lw, "exact")
VALIDATE["longest-word-by-deleting"] = v_lw

# ---------------------------------------------------------------- HARD

p = add(
    id="longest-chunked-palindrome-decomposition", title="Mirror Chunk Decomposition", diff="Hard", topic="Two Pointers", tier="extra",
    fn="maxMirrorChunks", params=[("s", "string")], ret="int", cmp="exact",
    desc="<p>Split the string <code>s</code> into <code>k</code> non-empty consecutive pieces <code>a<sub>1</sub>, a<sub>2</sub>, ..., a<sub>k</sub></code> (so that <code>s = a<sub>1</sub>a<sub>2</sub>...a<sub>k</sub></code>) such that the sequence of pieces reads the same from both sides: <code>a<sub>i</sub> = a<sub>k+1-i</sub></code> for every <code>i</code>. (When <code>k</code> is odd, the middle piece is compared with itself.)</p><p>Return the largest possible <code>k</code>. Note that <code>k = 1</code> (the whole string as a single piece) is always allowed.</p><p>For example, <code>\"abcxyzabc\"</code> gives <code>3</code> (<code>abc | xyz | abc</code>); <code>\"aaaa\"</code> gives <code>4</code>; <code>\"abcab\"</code> gives <code>3</code> (<code>ab | c | ab</code>); <code>\"abcd\"</code> gives <code>1</code>.</p>",
    constraints=["1 &le; s.length &le; 20,000", "s consists of lowercase English letters"],
    hints=["Try a recursive formulation: choose the first piece, which forces the last piece to be the same string, and recurse on what is left between them.",
           "Is it ever worse to cut the shortest possible matching piece (prefix equal to the suffix at the other end) than a longer one?",
           "Greedy: grow a candidate prefix length one letter at a time and compare it to the suffix of the same length at the other end of the remaining part. The first time they are equal, cut both pieces (count 2) and restart on the inside. A remaining non-empty middle with no match counts as one piece."],
    editorial=["Let <code>y</code> be the shortest string that is both a prefix and a suffix of the remaining part (non-overlapping). Suppose an optimal decomposition starts with a longer first piece <code>x</code>; then <code>x</code> is also a prefix and a suffix of the remaining part, and so is its shortest border, which is a match of length at most <code>|x| / 2</code>. That match cannot be shorter than <code>y</code>, so <code>y</code> itself is a border of <code>x</code> and <code>x = y w y</code> for some (possibly empty) <code>w</code>. Replacing the outer pair <code>x ... x</code> by <code>y | w | y ... y | w | y</code> gives a valid decomposition with more pieces, a contradiction. Hence an optimal decomposition always starts with <code>y</code>, and the greedy choice of the shortest match is safe.",
               "Implementation: keep the remaining range <code>[lo, hi)</code> and a length <code>L</code> growing from 1. When <code>s[lo:lo+L] == s[hi-L:hi]</code>, add 2, shrink the range by <code>L</code> on both sides and reset <code>L</code>. If the range becomes too short to hold two pieces of length <code>L</code>, whatever is left (if anything) is one middle piece and adds 1. Every letter is covered by the slices of at most one growing attempt, so slice comparisons cost O(n<sup>2</sup>) in the worst case with plain slicing (fast in C for these limits) and O(n) with a rolling hash."],
    time="O(n^2) worst case, O(n) with hashing", space="O(1)",
    solution='''def maxMirrorChunks(s):
    n = len(s)
    lo, hi = 0, n
    count = 0
    L = 1
    while hi - lo > 0:
        if 2 * L > hi - lo:
            count += 1
            break
        if s[lo:lo + L] == s[hi - L:hi]:
            count += 2
            lo += L
            hi -= L
            L = 1
        else:
            L += 1
    return count
''',
    tests=[["abcxyzabc"], ["aaaa"], ["abcab"], ["abcd"], ["a"], ["ab"], ["aa"], ["aba"], ["abab"], ["ghiabcdefhelloadamhelloabcdefghi"],
           ["abcabcabc"], ["abaaba"], ["xyxxyx"]],
)
_r = rnd(9109)
p["tests"].append(["a" * 8000])
_ch = [_rs(_r, _r.randint(1, 40), "ab") for _ in range(120)]
p["tests"].append(["".join(_ch) + "c" + "".join(reversed(_ch))])
_u = _rs(_r, 8000, LET)
p["tests"].append([_u])
p["tests"].append([_rs(_r, 3000, "ab") + _rs(_r, 2000, "c") + "".join(reversed(["ab"] * 1))])
p["tests"].append(["ab" * 2500])


def b_mc(s):
    from functools import lru_cache

    @lru_cache(maxsize=None)
    def f(i, j):
        if i >= j:
            return 0
        best = 1
        for L in range(1, (j - i) // 2 + 1):
            if s[i:i + L] == s[j - L:j]:
                best = max(best, 2 + f(i + L, j - L))
        return best

    return f(0, len(s))


def g_mc(r):
    alpha = r.choice(["a", "ab", "abc"])
    if r.random() < 0.5:
        return [_rs(r, r.randint(1, 12), alpha)]
    ch = [_rs(r, r.randint(1, 3), alpha) for _ in range(r.randint(1, 4))]
    mid = _rs(r, r.randint(0, 3), alpha)
    return ["".join(ch) + mid + "".join(reversed(ch))]


def v_mc(tests):
    for t in tests:
        s = t["args"][0]
        assert 1 <= len(s) <= 20000 and all("a" <= c <= "z" for c in s)
        assert 1 <= t["expected"] <= len(s)
    assert any(t["expected"] == 1 for t in tests) and any(t["expected"] >= 7 for t in tests)


CHECKS["longest-chunked-palindrome-decomposition"] = (b_mc, g_mc, "exact")
VALIDATE["longest-chunked-palindrome-decomposition"] = v_mc

p = add(
    id="min-adjacent-swaps-to-palindrome", title="Fewest Adjacent Swaps to a Palindrome", diff="Hard", topic="Two Pointers", tier="extra",
    fn="minSwapsToPalindrome", params=[("s", "string")], ret="int", cmp="exact",
    desc="<p>You are given a string <code>s</code> whose letters can be rearranged into a palindrome. In one move you may swap two <strong>adjacent</strong> characters. Return the minimum number of moves needed to turn <code>s</code> into <em>some</em> palindrome (any palindrome is acceptable, you choose which one).</p><p>For example, <code>\"aabb\"</code> needs <code>2</code> moves (<code>aabb &rarr; abab &rarr; abba</code>); <code>\"abab\"</code> needs <code>1</code> (<code>abab &rarr; abba</code>); <code>\"aab\"</code> needs <code>1</code> (<code>aab &rarr; aba</code>); <code>\"racecar\"</code> needs <code>0</code>.</p>",
    constraints=["1 &le; s.length &le; 2,000", "s consists of lowercase English letters", "At least one palindrome can be formed by rearranging the letters of s"],
    hints=["For a short string you could search over all palindromes you can form and count adjacent swaps for each. That is far too many. Fix the outer pair first.",
           "Look at the first character. Its partner has to end up at the last position; the cheapest partner is the nearest equal character counted from the right end.",
           "Use two pointers <code>l = 0</code> and <code>r = n - 1</code>. Find the rightmost position <code>k</code> with <code>s[k] == s[l]</code>. If <code>k &gt; l</code>, move it to position <code>r</code> with <code>r - k</code> swaps and shrink both pointers. If <code>k == l</code> the character is the single odd one: swap it one step towards the middle (cost 1) and look again."],
    editorial=["Greedy from the outside in. For the leftmost remaining character <code>c</code>, the right end of the remaining window must hold a partner of <code>c</code>. Choosing the nearest copy of <code>c</code> from the right end uses the fewest swaps to carry it to that end, and it does not disturb the relative order of the other characters, so the choice never hurts later steps. After bringing it, the outer pair is final, and we solve the inside window the same way.",
               "If the search from the right finds only <code>l</code> itself, then <code>c</code> is the letter with odd frequency and belongs to the centre. Rather than carrying it to the middle at once, swap it with its right neighbour (cost 1) and repeat; this moves it gradually towards the centre while the pairs of other letters are handled, and its total cost equals the distance it needs to travel. Each outer step costs O(n) for the search and the move, so the algorithm is O(n<sup>2</sup>) time, fine for n up to 2,000."],
    time="O(n^2)", space="O(n)",
    solution='''def minSwapsToPalindrome(s):
    s = list(s)
    l, r = 0, len(s) - 1
    moves = 0
    while l < r:
        k = r
        while k > l and s[k] != s[l]:
            k -= 1
        if k == l:
            s[l], s[l + 1] = s[l + 1], s[l]
            moves += 1
            continue
        ch = s.pop(k)
        s.insert(r, ch)
        moves += r - k
        l += 1
        r -= 1
    return moves
''',
    tests=[["aabb"], ["abab"], ["aab"], ["racecar"], ["a"], ["aa"], ["abba"], ["baab"], ["aabbc"], ["abcabc"],
           ["dcbaabcd"]],
)
_r = rnd(9110)


def _pal_multiset(r, n, alpha):
    half = [r.choice(alpha) for _ in range(n // 2)]
    chars = half + half + ([r.choice(alpha)] if n % 2 else [])
    r.shuffle(chars)
    return "".join(chars)


p["tests"].append([_pal_multiset(_r, 2000, LET)])
p["tests"].append([_pal_multiset(_r, 1999, "abc")])
p["tests"].append(["a" * 1000 + "b" * 1000])
p["tests"].append(["".join(sorted(_pal_multiset(_r, 1500, "abcde")))])
p["tests"].append(["ab" * 499 + "c" + "ba" * 499])


def b_ms(s):
    def pal(x):
        return x == x[::-1]

    if pal(s):
        return 0
    seen = {s}
    cur = [s]
    d = 0
    while cur:
        d += 1
        nxt = []
        for x in cur:
            for i in range(len(x) - 1):
                if x[i] == x[i + 1]:
                    continue
                y = x[:i] + x[i + 1] + x[i] + x[i + 2:]
                if y in seen:
                    continue
                if pal(y):
                    return d
                seen.add(y)
                nxt.append(y)
        cur = nxt
    return -1


def g_ms(r):
    return [_pal_multiset(r, r.randint(1, 7), r.choice(["ab", "abc", "abcd"]))]


def v_ms(tests):
    from collections import Counter
    for t in tests:
        s = t["args"][0]
        assert 1 <= len(s) <= 2000 and all("a" <= c <= "z" for c in s)
        assert sum(v % 2 for v in Counter(s).values()) <= 1, "cannot form a palindrome"
    assert any(t["expected"] == 0 for t in tests) and any(t["expected"] > 50 for t in tests)


CHECKS["min-adjacent-swaps-to-palindrome"] = (b_ms, g_ms, "exact")
VALIDATE["min-adjacent-swaps-to-palindrome"] = v_ms

p = add(
    id="longest-prefix-suffix-palindrome", title="Longest Prefix-Suffix Palindrome", diff="Hard", topic="Two Pointers", tier="extra",
    fn="longestPrefixSuffixPalindrome", params=[("s", "string")], ret="int", cmp="exact",
    desc="<p>Build a string <code>t = a + b</code> where <code>a</code> is a prefix of <code>s</code> (possibly empty), <code>b</code> is a suffix of <code>s</code> (possibly empty), and <code>a</code> and <code>b</code> do <strong>not overlap</strong> in <code>s</code>, i.e. <code>|a| + |b| &le; |s|</code>. Among all such <code>t</code> that are palindromes, return the <strong>length</strong> of the longest one.</p><p>For example, <code>\"abcdfdcecba\"</code> gives <code>9</code> (take <code>a = \"abcdfdc\"</code> and <code>b = \"ba\"</code>, giving the palindrome <code>\"abcdfdcba\"</code>); <code>\"abbaxyzyx\"</code> gives <code>5</code> (<code>a</code> empty, <code>b = \"xyzyx\"</code>); <code>\"abc\"</code> gives <code>1</code>.</p>",
    constraints=["1 &le; s.length &le; 100,000", "s consists of lowercase English letters"],
    hints=["First deal with the characters that already mirror each other at the two ends of <code>s</code>.",
           "Let <code>k</code> be the largest number such that <code>s[i] == s[n-1-i]</code> for all <code>i &lt; k</code>. If these pairs cover the whole string, the answer is <code>n</code>. Otherwise it is always optimal to take those <code>k</code> letters on both sides.",
           "After that, the palindrome continues in the middle part <code>m = s[k..n-k-1]</code> using either only a prefix of <code>m</code> or only a suffix of <code>m</code>. You need the longest palindromic prefix and the longest palindromic suffix of <code>m</code>, which a prefix function (KMP) on <code>m + '#' + reverse(m)</code> gives in linear time."],
    editorial=["Count the matching outer pairs: <code>k</code> is the length of the longest prefix such that <code>s[:k]</code> is the reverse of <code>s[n-k:]</code>, with <code>k</code> limited to <code>n / 2</code>. If the matching covers everything, <code>s</code> is a palindrome and the answer is <code>n</code>. Otherwise, the first and last letters of the middle part <code>m</code> differ. Using fewer than <code>k</code> outer pairs can only lose length (any palindrome using a shorter outer part can be extended to use all <code>k</code>), so the answer has the form <code>2k</code> plus the best palindrome inside <code>m</code> built from just a prefix of <code>m</code> or just a suffix of <code>m</code>: because the ends of <code>m</code> mismatch, a palindrome <code>a + b</code> cannot use letters from both sides of <code>m</code>.",
               "The longest palindromic prefix of <code>m</code> is found by computing the KMP prefix function of <code>m + '#' + m[::-1]</code>; its last value is the longest prefix of <code>m</code> that equals a suffix of the reversed string, i.e. a palindromic prefix. Doing the same with the reversed string gives the longest palindromic suffix. Answer: <code>2k + max(prefixPal, suffixPal)</code>. Time and space are linear."],
    time="O(n)", space="O(n)",
    solution='''def longestPrefixSuffixPalindrome(s):
    n = len(s)
    k = 0
    while 2 * k + 1 < n and s[k] == s[n - 1 - k]:
        k += 1
    if 2 * k + 1 >= n:
        return n
    m = s[k:n - k]

    def pal_prefix(x):
        t = x + '#' + x[::-1]
        pi = [0] * len(t)
        for i in range(1, len(t)):
            j = pi[i - 1]
            while j and t[i] != t[j]:
                j = pi[j - 1]
            if t[i] == t[j]:
                j += 1
            pi[i] = j
        return pi[-1]

    return 2 * k + max(pal_prefix(m), pal_prefix(m[::-1]))
''',
    tests=[["abcdfdcecba"], ["abbaxyzyx"], ["abc"], ["a"], ["ab"], ["aa"], ["aba"], ["abcba"], ["abcd"], ["aabaab" + "c"],
           ["xabbay"], ["abxyyxab" + "z"], ["zabaq"]],
)
_r = rnd(9111)
_h = _rs(_r, 9000, "ab")
_pp = _rs(_r, 2000, "ab")
_pp = _pp + _pp[::-1]
p["tests"].append([_h + "c" + _pp + "d" + _h[::-1]])
p["tests"].append([_h + _pp + "c" + "de" + _h[::-1]])
p["tests"].append([_h + "c" + "d" + _pp + _h[::-1]])
p["tests"].append([_rs(_r, 20000, "ab")])
p["tests"].append(["a" * 9000 + "b" + "a" * 5000])


def b_pp(s):
    n = len(s)
    best = 0
    for i in range(n + 1):
        for j in range(n - i + 1):
            t = s[:i] + (s[n - j:] if j else "")
            if len(t) > best and _is_pal(t):
                best = len(t)
    return best


def g_pp(r):
    alpha = r.choice(["ab", "abc"])
    n = r.randint(1, 10)
    s = _rs(r, n, alpha)
    if r.random() < 0.5:
        k = r.randint(0, 3)
        o = _rs(r, k, alpha)
        mid = _rs(r, r.randint(1, 6), alpha)
        s = o + mid + o[::-1]
    return [s]


def v_pp(tests):
    for t in tests:
        s = t["args"][0]
        assert 1 <= len(s) <= 100000 and all("a" <= c <= "z" for c in s)
        assert 1 <= t["expected"] <= len(s)
    assert any(t["expected"] == len(t["args"][0]) for t in tests) and any(t["expected"] < len(t["args"][0]) for t in tests)


CHECKS["longest-prefix-suffix-palindrome"] = (b_pp, g_pp, "exact")
VALIDATE["longest-prefix-suffix-palindrome"] = v_pp
