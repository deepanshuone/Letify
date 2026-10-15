"""Problems: string transforms (rotations, letter shifts, run-length, reversals). See data/lib.py for the registry."""
import re
from collections import Counter, deque

from lib import add, rnd, CHECKS, VALIDATE, gen_arr  # noqa: F401

TOPIC = "Strings"
LOW = "abcdefghijklmnopqrstuvwxyz"
UP = LOW.upper()
DIG = "0123456789"


def _rs(r, n, alpha):
    return "".join(r.choice(alpha) for _ in range(n))


# ---------------------------------------------------------------- 1. Caesar shift (Easy)

p = add(
    id="caesar-shift-letters", title="Caesar Shift of Letters", diff="Easy", topic=TOPIC,
    fn="caesarShift", params=[("s", "string"), ("k", "int")], ret="string", cmp="exact",
    desc="<p>A <em>Caesar shift</em> moves every letter <code>k</code> places forward in the alphabet and wraps around: after <code>z</code> comes <code>a</code>, and after <code>Z</code> comes <code>A</code>. Lowercase letters stay lowercase, uppercase letters stay uppercase, and digits are left untouched. A negative <code>k</code> moves the letters backward instead.</p><p>Given <code>s</code> and <code>k</code>, return the shifted string.</p><pre>s = \"Hello2World\", k = 3\nresult = \"Khoor2Zruog\"\n\ns = \"Azb\", k = -1\nresult = \"Zya\"</pre>",
    constraints=["1 &le; s.length &le; 20,000", "s consists of English letters (both cases) and digits", "-10<sup>9</sup> &le; k &le; 10<sup>9</sup>"],
    hints=["Handle one character at a time. Which characters change, and which do not?",
           "Shifting by 26 brings every letter back to itself, so only <code>k mod 26</code> matters. Be careful with negative <code>k</code>.",
           "Convert a letter to its index <code>0..25</code> (subtract <code>'a'</code> or <code>'A'</code>), add <code>k</code>, take the result modulo 26 and convert back, keeping the original case."],
    editorial=["The alphabet is a cycle of length 26, so a shift by <code>k</code> equals a shift by <code>k mod 26</code>. For a letter with index <code>x</code> in its own case (0 for <code>a</code>/<code>A</code>), the new index is <code>(x + k) mod 26</code>. Digits are copied unchanged.",
               "Watch the modulo of negative numbers: Python's <code>%</code> already returns a value in <code>0..25</code>, but in languages whose remainder can be negative you must add 26 before taking the remainder again. The loop visits every character once: O(n) time, O(n) space for the output."],
    time="O(n)", space="O(n)",
    solution='''def caesarShift(s, k):
    k %= 26
    out = []
    for ch in s:
        if 'a' <= ch <= 'z':
            out.append(chr((ord(ch) - 97 + k) % 26 + 97))
        elif 'A' <= ch <= 'Z':
            out.append(chr((ord(ch) - 65 + k) % 26 + 65))
        else:
            out.append(ch)
    return ''.join(out)
''',
    tests=[["Hello2World", 3], ["Azb", -1], ["xyz", 3], ["a", 0], ["a", 26], ["Zz9", 1], ["abc", -27], ["12345", 7],
           ["Az", 1000000000], ["Az", -1000000000], ["aAzZ", 25], ["aAzZ", -25]],
)
_r = rnd(9101)
p["tests"].append([_rs(_r, 20000, LOW + UP + DIG), 987654321])
p["tests"].append([_rs(_r, 12000, LOW + UP), -999999999])


def b_caesar(s, k):
    out = []
    for ch in s:
        if ch.isalpha():
            base = 'a' if ch.islower() else 'A'
            idx = ord(ch) - ord(base)
            for _ in range(abs(k)):
                idx = (idx + (1 if k > 0 else -1)) % 26
            ch = chr(ord(base) + idx)
        out.append(ch)
    return ''.join(out)


def v_caesar(tests):
    for t in tests:
        s, k = t["args"]
        assert 1 <= len(s) <= 20000 and re.fullmatch(r"[A-Za-z0-9]+", s)
        assert -10 ** 9 <= k <= 10 ** 9
        assert len(t["expected"]) == len(s)


CHECKS["caesar-shift-letters"] = (b_caesar, lambda r: [_rs(r, r.randint(1, 8), "aAzZ09bY"), r.randint(-60, 60)], "exact")
VALIDATE["caesar-shift-letters"] = v_caesar

# ---------------------------------------------------------------- 2. Run-length decode (Easy)

p = add(
    id="run-length-decode-string", title="Run-Length Decode", diff="Easy", topic=TOPIC,
    fn="decodeRuns", params=[("s", "string")], ret="string", cmp="exact",
    desc="<p>A string has been compressed with run-length encoding: every run of equal letters was replaced by the letter followed by the length of the run written in decimal. For example, <code>\"aaabcc\"</code> became <code>\"a3b1c2\"</code>.</p><p>Given the encoded string <code>s</code>, return the original string. The encoding is always well formed: it alternates a lowercase letter and a positive number (without leading zeros). The same letter may appear in two neighbouring groups, as in <code>\"a2a1\"</code>, which decodes to <code>\"aaa\"</code>.</p><pre>s = \"a3b1c2\"\nresult = \"aaabcc\"\n\ns = \"x12y1\"\nresult = \"xxxxxxxxxxxxy\"</pre>",
    constraints=["2 &le; s.length &le; 100,000", "s is a sequence of groups: one lowercase letter followed by a count with no leading zeros", "Every count is at least 1, and the decoded string has at most 40,000 characters"],
    hints=["Walk through the string from left to right. A group always starts with a letter.",
           "After reading a letter, keep reading characters while they are digits. The counts can have several digits, such as <code>12</code> or <code>405</code>.",
           "Convert the digit characters to an integer <code>c</code>, append <code>letter * c</code> to a list of pieces, and join the pieces once at the end."],
    editorial=["Scan with an index. At a letter, remember it and advance while the next characters are digits, then convert that digit substring to an integer. Repeat the letter that many times. Because a count may span several digits, you cannot simply read one digit after each letter.",
               "Appending every piece to a list and joining once keeps the total work linear in the size of the input plus the output, O(n + m) time and O(m) space, where m is the decoded length. Repeated string concatenation in a loop is a classic way to turn this into quadratic time in some languages."],
    time="O(n + m)", space="O(m)",
    solution='''def decodeRuns(s):
    out = []
    i, n = 0, len(s)
    while i < n:
        ch = s[i]
        i += 1
        j = i
        while j < n and s[j].isdigit():
            j += 1
        out.append(ch * int(s[i:j]))
        i = j
    return ''.join(out)
''',
    tests=[["a3b1c2"], ["x12y1"], ["a1"], ["z10"], ["a2a1"], ["a1b1c1d1"], ["x12y3x1"], ["a9999"], ["m100n20o3p1"]],
)
_r = rnd(9102)
_enc = "".join(_r.choice(LOW) + str(_r.randint(1, 5)) for _ in range(300))
p["tests"].append([_enc])
_enc = "".join(_r.choice(LOW) + str(_r.randint(1, 19)) for _ in range(2000))
p["tests"].append([_enc])
p["tests"].append(["k39999"])


def b_decode(s):
    return "".join(c * int(n) for c, n in re.findall(r"([a-z])(\d+)", s))


def g_decode(r):
    return "".join(r.choice("abc") + str(r.randint(1, 13)) for _ in range(r.randint(1, 6)))


def v_decode(tests):
    for t in tests:
        s = t["args"][0]
        assert 2 <= len(s) <= 100000
        assert re.fullmatch(r"([a-z][1-9][0-9]*)+", s)
        assert len(t["expected"]) <= 40000 and t["expected"] == b_decode(s)


CHECKS["run-length-decode-string"] = (b_decode, lambda r: [g_decode(r)], "exact")
VALIDATE["run-length-decode-string"] = v_decode

# ---------------------------------------------------------------- 3. Rotation operations (Easy)

p = add(
    id="apply-rotation-operations", title="Apply Rotation Operations", diff="Easy", topic=TOPIC,
    fn="applyRotations", params=[("s", "string"), ("ops", "int[][]")], ret="string", cmp="exact",
    desc="<p>You are given a string <code>s</code> and a list of operations. Each operation is a pair <code>[dir, k]</code>:</p><ul><li><code>dir = 0</code>: rotate left by <code>k</code>, i.e. move the first <code>k</code> characters to the end (in order);</li><li><code>dir = 1</code>: rotate right by <code>k</code>, i.e. move the last <code>k</code> characters to the front (in order).</li></ul><p>The operations are applied one after another. Return the final string. Note that <code>k</code> may be larger than the length of the string.</p><pre>s = \"abcdef\", ops = [[0, 2], [1, 5], [0, 1]]\nresult = \"efabcd\"</pre><p>The string goes <code>abcdef</code> &rarr; <code>cdefab</code> &rarr; <code>defabc</code> &rarr; <code>efabcd</code>.</p>",
    constraints=["1 &le; s.length &le; 15,000", "0 &le; ops.length &le; 2,000", "dir is 0 or 1", "0 &le; k &le; 10<sup>9</sup>"],
    hints=["Performing every rotation on the string costs O(n) each. Think about what the net result of a long sequence of rotations is.",
           "A rotation to the right by k is the same as a rotation to the left by -k, and rotating by the length n changes nothing. Rotations of a cycle just add up.",
           "Keep a single offset: add k for a left rotation, subtract k for a right rotation. At the end, reduce the offset modulo n and cut the string once: <code>s[off:] + s[:off]</code>."],
    editorial=["All the operations are rotations of the same cyclic sequence, so they compose by adding their shifts. Let the offset be the total number of positions the string was rotated to the left: a left rotation by <code>k</code> adds <code>k</code>, a right rotation subtracts <code>k</code>. Only the offset modulo <code>n</code> matters, because <code>n</code> single steps return to the start.",
               "After processing all operations, the answer is the string rotated left by <code>off mod n</code>, built with one slice concatenation. Total time is O(n + m) for n characters and m operations, with O(n) space for the result."],
    time="O(n + m)", space="O(n)",
    solution='''def applyRotations(s, ops):
    n = len(s)
    off = 0
    for d, k in ops:
        off += k if d == 0 else -k
    off %= n
    return s[off:] + s[:off]
''',
    tests=[["abcdef", [[0, 2], [1, 5], [0, 1]]], ["a", [[0, 5]]], ["abc", []], ["abc", [[0, 3]]], ["abc", [[1, 1000000000]]],
           ["abcdefg", [[0, 1000000000], [1, 999999999]]], ["ab", [[0, 1], [0, 1]]], ["abcde", [[1, 2]]], ["abcde", [[0, 7], [1, 7]]],
           ["hello", [[0, 1], [0, 1], [0, 1], [0, 1], [0, 1]]], ["xyz", [[1, 1], [1, 1], [1, 1], [1, 1]]]],
)
_r = rnd(9103)
p["tests"].append([_rs(_r, 15000, LOW), [[_r.randint(0, 1), _r.randint(0, 10 ** 9)] for _ in range(2000)]])
p["tests"].append([_rs(_r, 6000, "ab"), [[_r.randint(0, 1), _r.randint(0, 20000)] for _ in range(1500)]])


def b_rot(s, ops):
    for d, k in ops:
        k %= len(s)
        s = s[k:] + s[:k] if d == 0 else s[len(s) - k:] + s[:len(s) - k]
    return s


def g_rot(r):
    s = _rs(r, r.randint(1, 8), "abc")
    return [s, [[r.randint(0, 1), r.randint(0, 25)] for _ in range(r.randint(0, 6))]]


def v_rot(tests):
    for t in tests:
        s, ops = t["args"]
        assert 1 <= len(s) <= 15000 and s.islower() and len(ops) <= 2000
        assert all(len(o) == 2 and o[0] in (0, 1) and 0 <= o[1] <= 10 ** 9 for o in ops)
        assert sorted(t["expected"]) == sorted(s)


CHECKS["apply-rotation-operations"] = (b_rot, g_rot, "exact")
VALIDATE["apply-rotation-operations"] = v_rot

# ---------------------------------------------------------------- 4. Shift letters by prefix (Medium)

p = add(
    id="shift-letters-by-prefix", title="Shift Letters by Prefix", diff="Medium", topic=TOPIC,
    fn="shiftPrefixes", params=[("s", "string"), ("shifts", "int[]")], ret="string", cmp="exact",
    desc="<p>You are given a lowercase string <code>s</code> and an array <code>shifts</code> of the same length. Process <code>i = 0, 1, ..., n - 1</code> in order: the <code>i</code>-th step shifts <em>each of the first <code>i + 1</code> letters</em> forward through the alphabet by <code>shifts[i]</code> places, wrapping from <code>z</code> to <code>a</code>.</p><p>Return the string after all steps.</p><pre>s = \"xyz\", shifts = [1, 2, 4]\nresult = \"eed\"</pre><p>The first letter is shifted by 1 + 2 + 4 = 7 (<code>x</code> &rarr; <code>e</code>), the second by 2 + 4 = 6 (<code>y</code> &rarr; <code>e</code>) and the third by 4 (<code>z</code> &rarr; <code>d</code>).</p>",
    constraints=["1 &le; s.length = shifts.length &le; 5,000", "s consists of lowercase English letters", "0 &le; shifts[i] &le; 10<sup>9</sup>"],
    hints=["Applying every step to a whole prefix costs O(n) per step. Consider one single letter: which steps touch it?",
           "Letter <code>j</code> is inside the prefix of every step <code>i &ge; j</code>, so its total shift is <code>shifts[j] + shifts[j+1] + ... + shifts[n-1]</code>.",
           "These are suffix sums. Walk from the right end keeping a running total (reduced modulo 26) and shift each letter by that total."],
    editorial=["Shifts commute and only their sum matters for each letter. Letter <code>j</code> belongs to the first <code>i + 1</code> letters exactly when <code>i &ge; j</code>, so it receives the sum of <code>shifts[j..n-1]</code>.",
               "Compute the suffix sums from right to left in one pass. Because the alphabet has 26 letters, keep the running sum modulo 26 (the true sum can reach 5 &times; 10<sup>12</sup>, which would overflow 32-bit integers in some languages). Then letter <code>j</code> becomes <code>(letter + total) mod 26</code>. Time O(n), space O(n)."],
    time="O(n)", space="O(n)",
    solution='''def shiftPrefixes(s, shifts):
    n = len(s)
    out = [''] * n
    total = 0
    for j in range(n - 1, -1, -1):
        total = (total + shifts[j]) % 26
        out[j] = chr((ord(s[j]) - 97 + total) % 26 + 97)
    return ''.join(out)
''',
    tests=[["xyz", [1, 2, 4]], ["a", [0]], ["a", [26]], ["z", [1]], ["abc", [0, 0, 0]], ["abc", [3, 5, 9]], ["zz", [1000000000, 1000000000]],
           ["abcdefghij", [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]], ["aaaa", [25, 1, 0, 0]], ["mnop", [13, 13, 13, 13]]],
)
_r = rnd(9104)
p["tests"].append([_rs(_r, 5000, LOW), [_r.randint(0, 10 ** 9) for _ in range(5000)]])
p["tests"].append([_rs(_r, 3000, "az"), [_r.randint(0, 30) for _ in range(3000)]])


def b_shiftpre(s, shifts):
    a = [ord(c) - 97 for c in s]
    for i, sh in enumerate(shifts):
        for j in range(i + 1):
            a[j] = (a[j] + sh) % 26
    return "".join(chr(x + 97) for x in a)


def g_shiftpre(r):
    n = r.randint(1, 8)
    return [_rs(r, n, "axyz"), [r.randint(0, 60) for _ in range(n)]]


def v_shiftpre(tests):
    for t in tests:
        s, sh = t["args"]
        assert 1 <= len(s) <= 5000 and len(s) == len(sh) and s.islower()
        assert all(0 <= x <= 10 ** 9 for x in sh)


CHECKS["shift-letters-by-prefix"] = (b_shiftpre, g_shiftpre, "exact")
VALIDATE["shift-letters-by-prefix"] = v_shiftpre

# ---------------------------------------------------------------- 5. Symmetric segment reversals (Medium)

p = add(
    id="symmetric-segment-reversals", title="Symmetric Segment Reversals", diff="Medium", topic=TOPIC,
    fn="reverseSymmetric", params=[("s", "string"), ("ops", "int[]")], ret="string", cmp="exact",
    desc="<p>Let <code>n</code> be the length of the string <code>s</code>. An operation with value <code>a</code> (positions counted from 1) reverses the substring that starts at position <code>a</code> and ends at position <code>n + 1 - a</code>; in 0-indexed terms, the slice <code>s[a-1 .. n-a]</code>. Such a substring is centred in the middle of the string.</p><p>Apply the operations in the given order and return the final string.</p><pre>s = \"abcdef\", ops = [1, 2]\nresult = \"fbcdea\"</pre><p>The string goes <code>abcdef</code> &rarr; <code>fedcba</code> (reverse positions 1..6) &rarr; <code>fbcdea</code> (reverse positions 2..5).</p>",
    constraints=["1 &le; s.length &le; 12,000", "s consists of lowercase English letters", "0 &le; ops.length &le; 6,000", "1 &le; ops[j] &le; (s.length + 1) / 2 (integer division), so every substring is non-empty"],
    hints=["Simulating each reversal costs O(n) per operation, and there can be many operations. Look at what a symmetric reversal does to a pair of positions <code>i</code> and <code>n-1-i</code>.",
           "A reversal of <code>s[a-1 .. n-a]</code> swaps every pair <code>(i, n-1-i)</code> with <code>i &ge; a-1</code> and leaves the outer pairs alone. Pairs never move to a different pair.",
           "Count, for each pair index <code>i</code>, how many operations have <code>a - 1 &le; i</code> (a prefix count over the operation values). If that count is odd, the pair ends up swapped."],
    editorial=["Reversing a centred segment maps position <code>i</code> to position <code>n-1-i</code> for every position inside the segment. So the characters always stay on their own pair <code>{i, n-1-i}</code>; each operation either swaps the two characters of a pair (if the pair is inside the segment) or does nothing. Two swaps cancel, so only the parity matters.",
               "Pair <code>i</code> (for <code>i &lt; n/2</code>) is inside the segment of operation <code>a</code> exactly when <code>a - 1 &le; i</code>. Mark each operation at index <code>a-1</code>, sweep <code>i</code> from the left while keeping the XOR of the marks seen so far, and swap the pair when that parity is 1. The middle character of an odd-length string never moves. Time O(n + m), space O(n)."],
    time="O(n + m)", space="O(n)",
    solution='''def reverseSymmetric(s, ops):
    n = len(s)
    half = n // 2
    mark = [0] * (half + 1)
    for a in ops:
        mark[min(a - 1, half)] ^= 1
    arr = list(s)
    parity = 0
    for i in range(half):
        parity ^= mark[i]
        if parity:
            arr[i], arr[n - 1 - i] = arr[n - 1 - i], arr[i]
    return ''.join(arr)
''',
    tests=[["abcdef", [1, 2]], ["a", [1]], ["ab", [1]], ["ab", []], ["abc", [2]], ["abc", [1, 1]], ["abcde", [3, 3, 3]], ["abcdefg", [2, 4]],
           ["abcdefgh", [4]], ["abcdefgh", [1, 3, 2, 3, 1]], ["abcdefgh", [1, 2, 3, 4, 4, 3, 2, 1]]],
)
_r = rnd(9105)
_n = 12000
p["tests"].append([_rs(_r, _n, LOW), [_r.randint(1, (_n + 1) // 2) for _ in range(6000)]])
_n = 5001
p["tests"].append([_rs(_r, _n, "abc"), [_r.randint(1, (_n + 1) // 2) for _ in range(2500)]])


def b_symrev(s, ops):
    n = len(s)
    for a in ops:
        s = s[:a - 1] + s[a - 1:n - a + 1][::-1] + s[n - a + 1:]
    return s


def g_symrev(r):
    n = r.randint(1, 10)
    return [_rs(r, n, "abcd"), [r.randint(1, (n + 1) // 2) for _ in range(r.randint(0, 6))]]


def v_symrev(tests):
    for t in tests:
        s, ops = t["args"]
        n = len(s)
        assert 1 <= n <= 12000 and s.islower() and len(ops) <= 6000
        assert all(1 <= a <= (n + 1) // 2 for a in ops)


CHECKS["symmetric-segment-reversals"] = (b_symrev, g_symrev, "exact")
VALIDATE["symmetric-segment-reversals"] = v_symrev

# ---------------------------------------------------------------- 6. Smallest string after one reversal (Medium)

p = add(
    id="smallest-after-one-reversal", title="Smallest String After One Reversal", diff="Medium", topic=TOPIC,
    fn="smallestAfterReversal", params=[("s", "string")], ret="string", cmp="exact",
    desc="<p>You may choose one substring of <code>s</code> (possibly of length 1, which changes nothing) and reverse it in place. Return the lexicographically smallest string you can obtain this way.</p><pre>s = \"dcba\"\nresult = \"abcd\"\n\ns = \"abab\"\nresult = \"aabb\"\n\ns = \"bcab\"\nresult = \"acbb\"</pre><p>In the last example reversing <code>\"bca\"</code> gives <code>\"acb\"</code> followed by the final <code>b</code>.</p>",
    constraints=["1 &le; s.length &le; 5,000", "s consists of lowercase English letters"],
    hints=["Trying every substring is O(n&sup2;) reversals of O(n) each. Think about which position should be the left end of the reversed substring.",
           "The string can only improve at the first position <code>i</code> where some later letter is smaller than <code>s[i]</code>. Before that position every letter is already no larger than everything after it.",
           "Start the reversal at that <code>i</code>. The end <code>j</code> must hold the smallest letter that occurs after <code>i</code>; try each such <code>j</code> and keep the smallest resulting string."],
    editorial=["Let <code>i</code> be the first index with <code>s[i] &gt; min(s[i+1:])</code>. If there is none, the string is already the best possible (every letter is at most all letters after it, so the string is sorted) and the answer is <code>s</code>. Otherwise the prefix <code>s[:i]</code> cannot be improved, and a reversal that starts at <code>i</code> brings a strictly smaller letter to position <code>i</code>, so the reversal must start exactly there.",
               "The letter that lands on position <code>i</code> is <code>s[j]</code>, and it must be the minimum letter <code>m</code> of <code>s[i+1:]</code>. Among all <code>j &gt; i</code> with <code>s[j] = m</code>, build the candidate <code>s[:i] + reverse(s[i:j+1]) + s[j+1:]</code> and keep the smallest. There can be O(n) candidates of length O(n), so this is O(n&sup2;) in the worst case but with a tiny constant (slicing and comparison run at memory speed), which is fine for n &le; 5,000."],
    time="O(n^2)", space="O(n)",
    solution='''def smallestAfterReversal(s):
    n = len(s)
    suffix_min = [''] * (n + 1)
    suffix_min[n] = '{'
    for k in range(n - 1, -1, -1):
        suffix_min[k] = min(s[k], suffix_min[k + 1])
    start = -1
    for k in range(n - 1):
        if s[k] > suffix_min[k + 1]:
            start = k
            break
    if start == -1:
        return s
    m = suffix_min[start + 1]
    best = None
    for j in range(start + 1, n):
        if s[j] == m:
            cand = s[start:j + 1][::-1] + s[j + 1:]
            if best is None or cand < best:
                best = cand
    return s[:start] + best
''',
    tests=[["dcba"], ["abab"], ["bcab"], ["a"], ["ab"], ["ba"], ["aaaa"], ["abcde"], ["zyx"], ["cbacba"], ["bbaabba"], ["abacaba"],
           ["aabbaabbccbbaa"]],
)
_r = rnd(9106)
p["tests"].append([_rs(_r, 5000, "ab")])
p["tests"].append(["c" + "ba" * 2499 + "b"])
p["tests"].append(["z" + "a" * 4999])
p["tests"].append([_rs(_r, 4000, "abc")])


def b_smallrev(s):
    best = s
    n = len(s)
    for i in range(n):
        for j in range(i, n):
            c = s[:i] + s[i:j + 1][::-1] + s[j + 1:]
            if c < best:
                best = c
    return best


def v_smallrev(tests):
    for t in tests:
        s = t["args"][0]
        assert 1 <= len(s) <= 5000 and s.islower()
        assert sorted(t["expected"]) == sorted(s) and t["expected"] <= s


CHECKS["smallest-after-one-reversal"] = (b_smallrev, lambda r: [_rs(r, r.randint(1, 10), "abc")], "exact")
VALIDATE["smallest-after-one-reversal"] = v_smallrev

# ---------------------------------------------------------------- 7. Cheapest Caesar alignment (Medium)

p = add(
    id="cheapest-caesar-alignment", title="Cheapest Letter Shifts to a Target", diff="Medium", topic=TOPIC,
    fn="minShiftCost", params=[("s", "string"), ("t", "string"), ("forward", "int[]"), ("backward", "int[]")], ret="int", cmp="exact",
    desc="<p>You want to turn the lowercase string <code>s</code> into the string <code>t</code> of the same length. In one move you pick a position and change its letter to the next letter of the alphabet (<code>z</code> wraps to <code>a</code>) or to the previous one (<code>a</code> wraps to <code>z</code>). Letters are numbered <code>0..25</code>.</p><ul><li>Moving letter <code>c</code> to the next letter costs <code>forward[c]</code>.</li><li>Moving letter <code>c</code> to the previous letter costs <code>backward[c]</code>.</li></ul><p>Positions are independent and any number of moves may be used on each. Return the minimum total cost to make <code>s</code> equal to <code>t</code>.</p><pre>s = \"ab\", t = \"ba\", forward = [1, 1, ..., 1], backward = [3, 3, ..., 3]\nresult = 4</pre><p>Turning <code>a</code> into <code>b</code> costs 1 (one forward move) and turning <code>b</code> into <code>a</code> costs 3 (one backward move).</p>",
    constraints=["1 &le; s.length = t.length &le; 20,000", "s and t consist of lowercase English letters", "forward.length = backward.length = 26", "0 &le; forward[c], backward[c] &le; 400"],
    hints=["Each position can be handled on its own. How many different ways are there to get from one letter to another on a cycle of 26 letters?",
           "Only two routes matter: go forward all the way around to the target, or go backward all the way. Going back and forth or around twice never helps, because costs are not negative.",
           "Precompute a 26 &times; 26 table of the cheaper route for each (from, to) pair using sums of consecutive costs, then add up the table entries for all positions."],
    editorial=["On a cycle, the only simple paths between two letters are the forward arc and the backward arc. A longer walk repeats edges and cannot be cheaper because every cost is non-negative. For letters <code>a</code> to <code>b</code>, the forward cost is <code>forward[a] + forward[a+1] + ...</code> up to the letter before <code>b</code>, and the backward cost is <code>backward[a] + backward[a-1] + ...</code> down to the letter after <code>b</code>.",
               "Build a table <code>cost[a][b] = min(forward arc, backward arc)</code> in O(26&sup2;) by extending a running sum around the cycle. Then count how many positions need each (from, to) pair and sum <code>count * cost</code>, or simply add <code>cost[s[i]][t[i]]</code> for each position. Total O(n + 26&sup2;). The answer is at most 20,000 &times; 10,400, which fits in 32 bits."],
    time="O(n + 26^2)", space="O(26^2)",
    solution='''def minShiftCost(s, t, forward, backward):
    fwd = [[0] * 26 for _ in range(26)]
    bwd = [[0] * 26 for _ in range(26)]
    for a in range(26):
        run = 0
        for d in range(26):
            fwd[a][(a + d) % 26] = run
            run += forward[(a + d) % 26]
        run = 0
        for d in range(26):
            bwd[a][(a - d) % 26] = run
            run += backward[(a - d) % 26]
    total = 0
    for (x, y), c in Counter(zip(s, t)).items():
        a, b = ord(x) - 97, ord(y) - 97
        total += c * min(fwd[a][b], bwd[a][b])
    return total
''',
    tests=[],
)
p["solution"] = "from collections import Counter\n\n" + p["solution"]
_r = rnd(9107)
_ones = [1] * 26
_threes = [3] * 26
_cheap_back = [400] * 26
_free = [0] * 26
p["tests"] += [
    ["ab", "ba", _ones, _threes],
    ["a", "a", _ones, _ones],
    ["a", "z", _ones, _ones],
    ["z", "a", _ones, _ones],
    ["abc", "xyz", _ones, _threes],
    ["aaaa", "nnnn", _ones, _ones],
    ["hello", "world", [_r.randint(0, 400) for _ in range(26)], [_r.randint(0, 400) for _ in range(26)]],
    ["abcdef", "fedcba", _free, _cheap_back],
    ["abcdef", "fedcba", _cheap_back, _free],
    ["mmm", "nnn", _cheap_back, _cheap_back],
    ["zzzz", "aaaa", [_r.randint(1, 400) for _ in range(26)], [_r.randint(1, 400) for _ in range(26)]],
]
p["tests"].append([_rs(_r, 20000, LOW), _rs(_r, 20000, LOW), [_r.randint(0, 400) for _ in range(26)], [_r.randint(0, 400) for _ in range(26)]])
p["tests"].append([_rs(_r, 15000, "az"), _rs(_r, 15000, "mn"), [_r.randint(300, 400) for _ in range(26)], [_r.randint(300, 400) for _ in range(26)]])


def b_shiftcost(s, t, forward, backward):
    INF = float("inf")
    d = [[INF] * 26 for _ in range(26)]
    for c in range(26):
        d[c][c] = 0
        d[c][(c + 1) % 26] = min(d[c][(c + 1) % 26], forward[c])
        d[c][(c - 1) % 26] = min(d[c][(c - 1) % 26], backward[c])
    for k in range(26):
        for i in range(26):
            for j in range(26):
                if d[i][k] + d[k][j] < d[i][j]:
                    d[i][j] = d[i][k] + d[k][j]
    return sum(d[ord(x) - 97][ord(y) - 97] for x, y in zip(s, t))


def g_shiftcost(r):
    n = r.randint(1, 8)
    hi = r.choice([3, 10, 400])
    return [_rs(r, n, LOW), _rs(r, n, LOW), [r.randint(0, hi) for _ in range(26)], [r.randint(0, hi) for _ in range(26)]]


def v_shiftcost(tests):
    for t in tests:
        s, tt, f, b = t["args"]
        assert 1 <= len(s) <= 20000 and len(s) == len(tt) and s.islower() and tt.islower()
        assert len(f) == 26 and len(b) == 26 and all(0 <= x <= 400 for x in f + b)


CHECKS["cheapest-caesar-alignment"] = (b_shiftcost, g_shiftcost, "exact")
VALIDATE["cheapest-caesar-alignment"] = v_shiftcost

# ---------------------------------------------------------------- 8. Rank among rotations (Medium)

p = add(
    id="rank-among-rotations", title="Rank of a String Among Its Rotations", diff="Medium", topic=TOPIC,
    fn="rotationRank", params=[("s", "string")], ret="int", cmp="exact", tier="extra",
    desc="<p>The <em>rotations</em> of a string <code>s</code> are the strings obtained by moving some number of leading characters (0 up to <code>n - 1</code>) to the back. Different shifts can give the same rotation (for <code>\"abab\"</code> there are only two distinct rotations).</p><p>Return how many <em>distinct</em> rotations of <code>s</code> are lexicographically smaller than <code>s</code> itself.</p><pre>s = \"bab\"      rotations: bab, abb, bba      result = 1\ns = \"baba\"     distinct: baba, abab          result = 1\ns = \"abab\"                                   result = 0</pre>",
    constraints=["1 &le; s.length &le; 20,000", "s consists of lowercase English letters"],
    hints=["Building all rotations and sorting them is too slow for long strings: there are n rotations of length n each.",
           "Rotation <code>i</code> is <code>(s+s)[i : i+n]</code>. To compare it with <code>s</code> you only need the length of their longest common prefix, then one character comparison. The Z-function of <code>s + '#' + s + s</code> gives all those prefix lengths at once.",
           "Rotations repeat with period <code>p</code>, the smallest <code>i &ge; 1</code> for which rotation <code>i</code> equals <code>s</code> (or <code>n</code> if there is none). Count the rotations <code>i</code> in <code>1..p-1</code> that are smaller than <code>s</code>; each of those is a different string."],
    editorial=["Let <code>d = s + s</code>. Rotation <code>i</code> is <code>d[i : i+n]</code>. Compute the Z-function of <code>s + '#' + d</code>: the value at the position of <code>d[i]</code> is the length of the longest common prefix <code>l</code> of rotation <code>i</code> and <code>s</code> (the separator stops matches at <code>n</code>). If <code>l = n</code> the rotation equals <code>s</code>; otherwise rotation <code>i</code> is smaller than <code>s</code> exactly when <code>d[i + l] &lt; s[l]</code>.",
               "The sequence of rotations repeats every <code>p</code> steps, where <code>p</code> is the first <code>i &ge; 1</code> with rotation <code>i</code> equal to <code>s</code> (and <code>p = n</code> when the string is not periodic). So the distinct rotations are exactly rotations <code>0..p-1</code>; rotation 0 is <code>s</code> itself, and the answer is the number of <code>i</code> in <code>1..p-1</code> whose rotation is smaller. Time O(n), space O(n)."],
    time="O(n)", space="O(n)",
    solution='''def rotationRank(s):
    n = len(s)
    d = s + s
    t = s + '#' + d
    m = len(t)
    z = [0] * m
    l = r = 0
    for i in range(1, m):
        if i < r:
            z[i] = min(r - i, z[i - l])
        while i + z[i] < m and t[z[i]] == t[i + z[i]]:
            z[i] += 1
        if i + z[i] > r:
            l, r = i, i + z[i]
    lcp = [z[n + 1 + i] for i in range(n)]
    period = n
    for i in range(1, n):
        if lcp[i] >= n:
            period = i
            break
    count = 0
    for i in range(1, period):
        if d[i + lcp[i]] < s[lcp[i]]:
            count += 1
    return count
''',
    tests=[["bab"], ["baba"], ["abab"], ["a"], ["b"], ["ba"], ["ab"], ["aaaa"], ["zyxwv"], ["abcde"], ["cabcab"], ["bbbbab"], ["abaabaab"]],
)
_r = rnd(9108)
p["tests"].append([_rs(_r, 20000, "ab")])
p["tests"].append(["abaab" * 4000])
p["tests"].append(["b" + "a" * 19999])
p["tests"].append([_rs(_r, 12000, LOW)])


def b_rank(s):
    n = len(s)
    return len({s[i:] + s[:i] for i in range(n) if s[i:] + s[:i] < s})


def g_rank(r):
    if r.random() < 0.4:
        return [_rs(r, r.randint(1, 4), "ab") * r.randint(1, 4)]
    return [_rs(r, r.randint(1, 10), "abc")]


def v_rank(tests):
    for t in tests:
        s = t["args"][0]
        assert 1 <= len(s) <= 20000 and s.islower()
        assert 0 <= t["expected"] < len(s)


CHECKS["rank-among-rotations"] = (b_rank, g_rank, "exact")
VALIDATE["rank-among-rotations"] = v_rank

# ---------------------------------------------------------------- 9. Optimal repeat compression (Hard)

p = add(
    id="optimal-repeat-compression-length", title="Optimal Repeat Compression", diff="Hard", topic=TOPIC,
    fn="minEncodedLength", params=[("s", "string")], ret="int", cmp="exact", tier="extra",
    desc="<p>You compress a lowercase string <code>s</code> by cutting it into consecutive pieces and writing every piece in one of two ways:</p><ul><li>a single letter is written as it is, and costs 1;</li><li>a piece that consists of a non-empty block <code>u</code> repeated <code>r &ge; 2</code> times is written as the decimal number <code>r</code> followed by the block <code>u</code>, and costs <code>digits(r) + |u|</code>.</li></ul><p>The pieces are written one after another and the cost of the encoding is the sum of the costs. Return the minimum possible cost.</p><pre>s = \"aaaaaaaaaaaa\"    (12 times a)   result = 3    (\"12a\")\ns = \"abababab\"                       result = 3    (\"4ab\")\ns = \"abcabcabcxyz\"                   result = 7    (\"3abc\" + \"x\" + \"y\" + \"z\")</pre>",
    constraints=["1 &le; s.length &le; 600", "s consists of lowercase English letters"],
    hints=["Let <code>dp[i]</code> be the best cost for the first <code>i</code> letters. A new piece ends at <code>i</code>: it is either one letter or a repeated block.",
           "For a fixed start <code>j</code>, which substrings <code>s[j:j+L]</code> are a block repeated at least twice? A substring of length <code>L</code> is a repetition of its shortest period <code>d</code> exactly when <code>d</code> divides <code>L</code> (and then <code>r = L / d</code>).",
           "Compute the prefix function (KMP failure array) of <code>s[j:]</code> for each start <code>j</code>. For every length <code>L</code>, the shortest period is <code>d = L - pi[L-1]</code>; if <code>d</code> divides <code>L</code> and <code>L/d &ge; 2</code>, relax <code>dp[j+L]</code> with <code>dp[j] + digits(L/d) + d</code>."],
    editorial=["This is a shortest-path / DP over positions: <code>dp[i]</code> is the minimum cost for the prefix of length <code>i</code>, with <code>dp[0] = 0</code>. From a state <code>dp[j]</code> there is the single-letter transition to <code>j+1</code> with cost 1, and one transition to <code>j+L</code> for every <code>L</code> such that <code>s[j:j+L]</code> is a block repeated at least twice. There is no need to try blocks that are not the shortest period: a longer block <code>u</code> repeated fewer times saves at most as many digits as it adds letters, so it is never strictly cheaper.",
               "The shortest period of every prefix of <code>s[j:]</code> comes from one run of the KMP prefix function: the prefix of length <code>L</code> has period <code>d = L - pi[L-1]</code>, and it is an exact repetition when <code>d</code> divides <code>L</code>. Doing this for every start <code>j</code> costs O(n) each, so O(n&sup2;) in total, which is fine for n &le; 600. The memory is O(n)."],
    time="O(n^2)", space="O(n)",
    solution='''def minEncodedLength(s):
    n = len(s)
    dp = [10 ** 9] * (n + 1)
    dp[0] = 0
    for j in range(n):
        if dp[j] + 1 < dp[j + 1]:
            dp[j + 1] = dp[j] + 1
        t = s[j:]
        m = len(t)
        pi = [0] * m
        k = 0
        for i in range(1, m):
            while k and t[i] != t[k]:
                k = pi[k - 1]
            if t[i] == t[k]:
                k += 1
            pi[i] = k
        for L in range(2, m + 1):
            d = L - pi[L - 1]
            if L % d == 0 and L // d >= 2:
                c = dp[j] + d + len(str(L // d))
                if c < dp[j + L]:
                    dp[j + L] = c
    return dp[n]
''',
    tests=[["a"], ["aa"], ["aaa"], ["aaaaaaaaaaaa"], ["abababab"], ["abcabcabcxyz"], ["abcd"], ["aabbaabb"], ["abcabcabcabcabcabc"],
           ["xaaaaaaaaaay"], ["ababababababababababababababababab" + "cdcdcd"], ["aaaaaaaaabaaaaaaaaab"]],
)
_r = rnd(9109)
p["tests"].append(["a" * 600])
p["tests"].append([(("ab" * 40 + "c") * 6 + _rs(_r, 40, "abc"))[:600]])
p["tests"].append([_rs(_r, 600, "ab")])
p["tests"].append(["".join(_rs(_r, _r.randint(1, 4), "abc") * _r.randint(1, 30) for _ in range(40))[:600]])


def b_compress(s):
    n = len(s)
    memo = {}

    def f(i):
        if i == n:
            return 0
        if i in memo:
            return memo[i]
        best = 1 + f(i + 1)
        for L in range(2, n - i + 1):
            piece = s[i:i + L]
            for d in range(1, L // 2 + 1):
                if L % d == 0 and piece[:d] * (L // d) == piece:
                    best = min(best, len(str(L // d)) + d + f(i + L))
        memo[i] = best
        return best

    return f(0)


def g_compress(r):
    if r.random() < 0.5:
        return [_rs(r, r.randint(1, 4), "ab") * r.randint(1, 12) + _rs(r, r.randint(0, 3), "ab")]
    return [_rs(r, r.randint(1, 14), "ab")]


def v_compress(tests):
    for t in tests:
        s = t["args"][0]
        assert 1 <= len(s) <= 600 and s.islower()
        assert 1 <= t["expected"] <= len(s)


CHECKS["optimal-repeat-compression-length"] = (b_compress, g_compress, "exact")
VALIDATE["optimal-repeat-compression-length"] = v_compress

# ---------------------------------------------------------------- 10. Adjacent swaps to a target anagram (Hard)

p = add(
    id="adjacent-swaps-to-target-anagram", title="Adjacent Swaps to a Target Anagram", diff="Hard", topic=TOPIC,
    fn="minAdjacentSwaps", params=[("s", "string"), ("t", "string")], ret="int", cmp="exact", tier="extra",
    desc="<p>The strings <code>s</code> and <code>t</code> have the same length and contain exactly the same letters with the same multiplicities (<code>t</code> is an anagram of <code>s</code>). In one move you may swap two <em>neighbouring</em> characters of <code>s</code>.</p><p>Return the minimum number of moves needed to turn <code>s</code> into <code>t</code>.</p><pre>s = \"abc\", t = \"cba\"   result = 3\ns = \"aabb\", t = \"bbaa\" result = 4</pre>",
    constraints=["1 &le; s.length = t.length &le; 20,000", "s and t consist of lowercase English letters", "t is a rearrangement of s"],
    hints=["If all letters were different, the target would tell you where each letter of <code>s</code> must go. What do you do when letters repeat?",
           "Equal letters never need to cross each other, so the <em>k</em>-th occurrence of a letter in <code>s</code> should become the <em>k</em>-th occurrence of that letter in <code>t</code>. This turns the task into sorting a permutation by adjacent swaps.",
           "The minimum number of adjacent swaps to sort a permutation is its number of inversions. Build the permutation from <code>t</code> and count inversions in O(n log n) with a Fenwick tree (or merge sort)."],
    editorial=["Match equal letters in order: the <em>k</em>-th <code>c</code> of <code>t</code> is paired with the <em>k</em>-th <code>c</code> of <code>s</code>. Crossing two equal letters is wasted effort, so this matching is optimal. Let <code>pos[i]</code> be the index in <code>s</code> of the letter matched with <code>t[i]</code>; this is a permutation of <code>0..n-1</code>.",
               "Turning <code>s</code> into <code>t</code> now means sorting <code>pos</code> by adjacent swaps, since each adjacent swap fixes at most one inversion, and bubble sort fixes exactly one per swap. So the answer is the number of inversions of <code>pos</code>. Count them with a Fenwick tree: scan <code>pos</code> left to right and, for each value, add the number of already seen values that are larger. Time O(n log n), space O(n). The answer can reach n(n-1)/2 &asymp; 2 &times; 10<sup>8</sup>, which fits in 32 bits."],
    time="O(n log n)", space="O(n)",
    solution='''from collections import defaultdict, deque


def minAdjacentSwaps(s, t):
    n = len(s)
    where = defaultdict(deque)
    for i, ch in enumerate(s):
        where[ch].append(i)
    pos = [where[ch].popleft() for ch in t]
    tree = [0] * (n + 1)
    inv = 0
    for seen, p in enumerate(pos):
        # count earlier values <= p, the rest are larger than p
        i = p + 1
        smaller = 0
        while i > 0:
            smaller += tree[i]
            i -= i & -i
        inv += seen - smaller
        i = p + 1
        while i <= n:
            tree[i] += 1
            i += i & -i
    return inv
''',
    tests=[["abc", "cba"], ["aabb", "bbaa"], ["a", "a"], ["ab", "ba"], ["ab", "ab"], ["aaaa", "aaaa"], ["abcd", "abcd"], ["abcd", "dcba"],
           ["abcabc", "cbacba"], ["aabbcc", "ccbbaa"], ["abab", "baba"], ["aaabbb", "bbbaaa"]],
)
_r = rnd(9110)
_s = _rs(_r, 20000, "abc")
_t = list(_s); _r.shuffle(_t)
p["tests"].append([_s, "".join(_t)])
p["tests"].append(["a" * 10000 + "b" * 10000, "b" * 10000 + "a" * 10000])
_s = _rs(_r, 15000, LOW)
p["tests"].append([_s, _s[::-1]])


def b_swaps(s, t):
    if s == t:
        return 0
    seen = {s}
    q = deque([(s, 0)])
    while q:
        cur, dist = q.popleft()
        for i in range(len(cur) - 1):
            if cur[i] != cur[i + 1]:
                nxt = cur[:i] + cur[i + 1] + cur[i] + cur[i + 2:]
                if nxt == t:
                    return dist + 1
                if nxt not in seen:
                    seen.add(nxt)
                    q.append((nxt, dist + 1))


def g_swaps(r):
    s = _rs(r, r.randint(1, 7), "abc")
    t = list(s)
    r.shuffle(t)
    return [s, "".join(t)]


def v_swaps(tests):
    for t in tests:
        s, tt = t["args"]
        assert 1 <= len(s) <= 20000 and len(s) == len(tt) and s.islower() and tt.islower()
        assert sorted(s) == sorted(tt)
        assert 0 <= t["expected"] <= len(s) * (len(s) - 1) // 2


CHECKS["adjacent-swaps-to-target-anagram"] = (b_swaps, g_swaps, "exact")
VALIDATE["adjacent-swaps-to-target-anagram"] = v_swaps

# ---------------------------------------------------------------- 11. Shift-equivalent window pairs (Medium)

p = add(
    id="count-shift-equivalent-window-pairs", title="Count Shift-Equivalent Window Pairs", diff="Medium", topic=TOPIC,
    fn="countShiftedPairs", params=[("s", "string"), ("k", "int")], ret="int", cmp="exact", tier="extra",
    desc="<p>Two strings of the same length are <em>shift-equivalent</em> if one is obtained from the other by shifting every letter by the same number of places in the alphabet, wrapping around from <code>z</code> to <code>a</code>. A shift by 0 is allowed, so equal strings are shift-equivalent; for example <code>\"abc\"</code> and <code>\"bcd\"</code> (shift 1) or <code>\"yza\"</code> and <code>\"abc\"</code> (shift 2).</p><p>Given the lowercase string <code>s</code> and a length <code>k</code>, consider all windows (substrings) of length <code>k</code>, taken at starting positions <code>0..n-k</code>. Return the number of pairs of different starting positions <code>i &lt; j</code> whose windows are shift-equivalent.</p><pre>s = \"abcbcd\", k = 3\nwindows: abc, bcb, cbc, bcd\nresult = 1     (abc and bcd)</pre>",
    constraints=["1 &le; k &le; s.length &le; 5,000", "s consists of lowercase English letters"],
    hints=["Comparing every pair of windows letter by letter is far too slow: there are O(n&sup2;) pairs, each costing O(k).",
           "Two windows are shift-equivalent exactly when their sequences of differences between neighbouring letters (modulo 26) are identical. Why does the common shift disappear in the differences?",
           "Turn every window into a canonical key: the tuple (or bytes) of its <code>k - 1</code> neighbour differences modulo 26. Count how many windows share each key; a key seen <code>c</code> times contributes <code>c (c - 1) / 2</code> pairs."],
    editorial=["If window <code>B</code> is window <code>A</code> shifted by <code>d</code>, all neighbour differences <code>(A[x+1] - A[x]) mod 26</code> are equal for both, because the shift cancels in a difference. Conversely, if two windows have equal difference sequences, then every letter of one differs from the corresponding letter of the other by the same amount as the first letters do, so they are shift-equivalent. The difference sequence is therefore a complete canonical form.",
               "Compute the difference array of the whole string once, <code>diff[x] = (s[x+1] - s[x]) mod 26</code>, and use the slice <code>diff[i : i+k-1]</code> (as a bytes object or a rolling hash) as the key of the window starting at <code>i</code>. Group windows with a hash map and add <code>c(c-1)/2</code> for every group of size <code>c</code>. With slices as keys the cost is O(n k) memory-bound work, with a rolling hash it becomes O(n). For <code>k = 1</code> every window has an empty key, so all windows are equivalent and the answer is <code>C(n, 2)</code>."],
    time="O(n * k) with slice keys, O(n) with rolling hash", space="O(n * k) worst case with slice keys, O(n) with hashing",
    solution='''from collections import Counter


def countShiftedPairs(s, k):
    n = len(s)
    diff = bytes((ord(s[x + 1]) - ord(s[x])) % 26 for x in range(n - 1))
    groups = Counter(diff[i:i + k - 1] for i in range(n - k + 1))
    return sum(c * (c - 1) // 2 for c in groups.values())
''',
    tests=[["abcbcd", 3], ["a", 1], ["ab", 1], ["abc", 3], ["aaaa", 2], ["abcabc", 3], ["yzabc", 3], ["abcdefgh", 1], ["azazaz", 2], ["zabzab", 3],
           ["abcdefghijklmnopqrstuvwxyz", 13], ["ababab", 4]],
)
_r = rnd(9111)
p["tests"].append([_rs(_r, 5000, "ab"), 6])
p["tests"].append([_rs(_r, 5000, "abc"), 2500])
p["tests"].append(["abc" * 1666 + "ab", 1000])
p["tests"].append([_rs(_r, 4000, LOW), 1])


def b_shifted(s, k):
    n = len(s)
    wins = [s[i:i + k] for i in range(n - k + 1)]
    cnt = 0
    for i in range(len(wins)):
        for j in range(i + 1, len(wins)):
            if len({(ord(a) - ord(b)) % 26 for a, b in zip(wins[i], wins[j])}) == 1:
                cnt += 1
    return cnt


def g_shifted(r):
    n = r.randint(1, 12)
    return [_rs(r, n, r.choice(["ab", "abc", "az", "xyza"])), r.randint(1, n)]


def v_shifted(tests):
    for t in tests:
        s, k = t["args"]
        assert 1 <= k <= len(s) <= 5000 and s.islower()
        m = len(s) - k + 1
        assert 0 <= t["expected"] <= m * (m - 1) // 2


CHECKS["count-shift-equivalent-window-pairs"] = (b_shifted, g_shifted, "exact")
VALIDATE["count-shift-equivalent-window-pairs"] = v_shifted
