from lib import add, rnd, CHECKS, VALIDATE, gen_arr  # noqa: F401
import itertools
import string

INT_MIN, INT_MAX = -(2 ** 31), 2 ** 31 - 1


# ---------------------------------------------------------------- EASY

p = add(
    id="add-digits-until-single", title="Repeated Digit Sum", diff="Easy", topic="Math & Bit Manipulation",
    fn="addDigits", params=[("num", "int")], ret="int", cmp="exact",
    desc="""<p>Given a non-negative integer <code>num</code>, repeatedly replace it with the sum of its decimal digits until only one digit is left. Return that final digit.</p><pre>num = 38  -> 38 -> 11 -> 2, so the answer is 2\nnum = 0   -> 0</pre>""",
    constraints=["0 &le; num &le; 2<sup>31</sup> - 1"],
    hints=["A loop that sums the digits and repeats while the number has two or more digits is correct. Is there a formula that gives the same answer without a loop?",
           "Each power of 10 leaves remainder 1 when divided by 9, so a number and the sum of its digits leave the same remainder modulo 9.",
           "The answer is 0 when num is 0. Otherwise it is 1 + (num - 1) mod 9, which always lands in the range 1 to 9."],
    editorial=["Every digit sum keeps the remainder modulo 9, because 10 is congruent to 1 modulo 9. The final single digit is therefore the remainder of num modulo 9, except that a nonzero multiple of 9 ends at 9 and never at 0. The expression 1 + (num - 1) mod 9 captures both cases, and the special case num = 0 returns 0.",
               "The simulation is also fast: each pass shrinks the number a lot, so only a few passes are needed. The closed form avoids the loop entirely and is the answer to give when an interviewer asks for O(1) time."],
    time="O(1)", space="O(1)",
    solution='''def addDigits(num):
    if num == 0:
        return 0
    return 1 + (num - 1) % 9
''',
    tests=[[0], [1], [9], [10], [38], [99], [100], [1000], [123456789], [493193], [999999999], [2147483647]],
)


def b_add_digits(num):
    while num >= 10:
        num = sum(int(c) for c in str(num))
    return num


def v_add_digits(tests):
    for t in tests:
        num = t["args"][0]
        assert 0 <= num <= INT_MAX
        assert 0 <= t["expected"] <= 9 and (t["expected"] == 0) == (num == 0)


CHECKS["add-digits-until-single"] = (b_add_digits, lambda r: [r.randint(0, 10 ** 6)], "exact")
VALIDATE["add-digits-until-single"] = v_add_digits

p = add(
    id="self-dividing-numbers-in-range", title="Self-Dividing Numbers", diff="Easy", topic="Math & Bit Manipulation",
    fn="selfDividingNumbers", params=[("left", "int"), ("right", "int")], ret="int[]", cmp="exact",
    desc="""<p>A <em>self-dividing</em> number is divisible by each of its own decimal digits. For example, 128 is self-dividing because it is divisible by 1, by 2 and by 8. A number that contains the digit 0 is never self-dividing, because division by zero is undefined.</p><p>Given two integers <code>left</code> and <code>right</code>, return every self-dividing number in the inclusive range from <code>left</code> to <code>right</code>, in increasing order.</p><pre>left = 1, right = 22  -> [1, 2, 3, 4, 5, 6, 7, 8, 9, 11, 12, 15, 22]</pre>""",
    constraints=["1 &le; left &le; right &le; 100,000"],
    hints=["Test each number in the range on its own. Extract the digits with <code>% 10</code> and <code>// 10</code>.",
           "A digit 0 rules a number out at once. Otherwise check whether the whole number is divisible by that digit.",
           "Compare against the original number, not a partly reduced copy of it."],
    editorial=["Scan the range in increasing order. For each candidate, peel off its digits from the right and stop as soon as a digit is 0 or fails to divide the original value. Since the scan goes upward, the result list comes out already sorted.",
               "The range has at most 100,000 numbers of at most six digits, so the scan is comfortably fast. The work is proportional to the range length times the number of digits."],
    time="O((right - left) * digits)", space="O(answer)",
    solution='''def selfDividingNumbers(left, right):
    out = []
    for x in range(left, right + 1):
        y = x
        ok = True
        while y:
            d = y % 10
            if d == 0 or x % d:
                ok = False
                break
            y //= 10
        if ok:
            out.append(x)
    return out
''',
    tests=[[1, 22], [1, 9], [12, 12], [10, 20], [100, 100], [128, 128], [47, 85], [2000, 2050], [1, 10000],
           [98000, 100000], [1, 100000]],
)


def b_self_div(left, right):
    out = []
    for x in range(left, right + 1):
        s = str(x)
        if "0" not in s and all(x % int(c) == 0 for c in s):
            out.append(x)
    return out


def g_self_div(r):
    a = r.randint(1, 300)
    return [a, a + r.randint(0, 150)]


def v_self_div(tests):
    for t in tests:
        left, right = t["args"]
        assert 1 <= left <= right <= 100000
        out = t["expected"]
        assert out == sorted(out) and all(left <= x <= right for x in out)


CHECKS["self-dividing-numbers-in-range"] = (b_self_div, g_self_div, "exact")
VALIDATE["self-dividing-numbers-in-range"] = v_self_div

p = add(
    id="column-number-to-spreadsheet-label", title="Column Number to Spreadsheet Label", diff="Easy", topic="Math & Bit Manipulation",
    fn="columnLabel", params=[("n", "int")], ret="string", cmp="exact",
    desc="""<p>Spreadsheet columns are labelled with letters: column 1 is <code>A</code>, column 26 is <code>Z</code>, column 27 is <code>AA</code>, and the labels continue in the same order, <code>AB, ..., AZ, BA, ...</code>.</p><p>Given a 1-based column number <code>n</code>, return the label of that column.</p><pre>n = 1   -> "A"\nn = 26  -> "Z"\nn = 27  -> "AA"\nn = 52  -> "AZ"\nn = 702 -> "ZZ"\nn = 703 -> "AAA"</pre>""",
    constraints=["1 &le; n &le; 2<sup>31</sup> - 1"],
    hints=["Write out the first few labels and notice that they form a base-26 numbering with no zero digit.",
           "Subtract 1 from n before each step. Then the remainder modulo 26 gives a letter index from 0 (A) to 25 (Z).",
           "While n is positive: subtract 1, output the letter for <code>n % 26</code>, then divide by 26. Reverse the letters at the end."],
    editorial=["The labels form a bijective base-26 system: there is no digit for zero, so 26 is written Z rather than a two-letter label with a zero digit. Subtracting 1 before each division maps every digit to the range 0 to 25 and makes the representation unique.",
               "The inverse of this conversion (label to number) is a left-to-right loop. Going from number to label, the letters come out least significant first, so they must be reversed. Since n is at most about 2 billion, a label has at most seven letters and the loop is effectively constant time."],
    time="O(log n)", space="O(log n)",
    solution='''def columnLabel(n):
    letters = []
    while n > 0:
        n -= 1
        letters.append(chr(ord('A') + n % 26))
        n //= 26
    return ''.join(reversed(letters))
''',
    tests=[[1], [2], [26], [27], [28], [52], [53], [701], [702], [703], [1000], [16384], [18278], [2147483647]],
)


def b_col_label(n):
    idx = 0
    length = 1
    while True:
        for t in itertools.product(string.ascii_uppercase, repeat=length):
            idx += 1
            if idx == n:
                return "".join(t)
        length += 1


def v_col_label(tests):
    for t in tests:
        n = t["args"][0]
        s = t["expected"]
        assert 1 <= n <= INT_MAX
        assert s.isalpha() and s.isupper() and 1 <= len(s) <= 7


CHECKS["column-number-to-spreadsheet-label"] = (b_col_label, lambda r: [r.randint(1, 1000)], "exact")
VALIDATE["column-number-to-spreadsheet-label"] = v_col_label


# ---------------------------------------------------------------- MEDIUM

p = add(
    id="monotone-increasing-digits-at-most-n", title="Largest Number With Non-Decreasing Digits", diff="Medium", topic="Math & Bit Manipulation",
    fn="largestMonotoneAtMost", params=[("n", "int")], ret="int", cmp="exact",
    desc="""<p>An integer has <em>non-decreasing digits</em> when every digit is greater than or equal to the digit on its left. For example 1123 and 99 both qualify, while 1213 does not.</p><p>Given <code>n</code>, return the largest integer that is at most <code>n</code> and has non-decreasing digits.</p><pre>n = 20   -> 19\nn = 332  -> 299\nn = 1000 -> 999\nn = 1234 -> 1234</pre>""",
    constraints=["0 &le; n &le; 2<sup>31</sup> - 1"],
    hints=["Counting down from n one step at a time is correct, but the gap can be large: from 1100 the answer is 999, about 100 steps away.",
           "Find a place where a digit is larger than the digit after it. The answer cannot keep that pair, so the left digit must drop and everything after it becomes 9.",
           "Process the positions from right to left. Whenever digit i-1 is greater than digit i, decrease digit i-1 by one and set every digit after it to 9. A decrease can create a new violation further left, and the scan handles that when it reaches it."],
    editorial=["Scan the digits from right to left. Whenever the digit at position i-1 is larger than the digit at position i, the number is not valid: lower digit i-1 by one and fill positions i onward with 9. Filling with 9s keeps the suffix non-decreasing and makes it as large as possible, while lowering the left digit is the smallest change that removes the violation.",
               "Because the scan goes right to left, a decrease that creates a new violation with the digit before it is caught in the next iteration. The result is the largest valid number not above n. The leading zeros that can appear after the decreases disappear when the digits are converted back to an integer. Time is O(d) for d digits and space is O(d)."],
    time="O(d)", space="O(d)",
    solution='''def largestMonotoneAtMost(n):
    s = [int(c) for c in str(n)]
    for i in range(len(s) - 1, 0, -1):
        if s[i - 1] > s[i]:
            s[i - 1] -= 1
            for j in range(i, len(s)):
                s[j] = 9
    return int(''.join(map(str, s)))
''',
    tests=[[0], [1], [9], [10], [20], [100], [120], [332], [1000], [1100], [1234], [10000], [98765], [999999999],
           [1000000000], [2147483647]],
)


def b_mono(n):
    x = n
    while True:
        s = str(x)
        if all(s[k] <= s[k + 1] for k in range(len(s) - 1)):
            return x
        x -= 1


def v_mono(tests):
    for t in tests:
        n = t["args"][0]
        s = str(t["expected"])
        assert 0 <= n <= INT_MAX
        assert 0 <= t["expected"] <= n
        assert all(s[k] <= s[k + 1] for k in range(len(s) - 1))


CHECKS["monotone-increasing-digits-at-most-n"] = (b_mono, lambda r: [r.randint(0, 3000)], "exact")
VALIDATE["monotone-increasing-digits-at-most-n"] = v_mono

p = add(
    id="reverse-add-palindrome-steps", title="Reverse-and-Add to a Palindrome", diff="Medium", topic="Math & Bit Manipulation",
    fn="reverseAddSteps", params=[("n", "int")], ret="int", cmp="exact",
    desc="""<p>Start with a positive integer <code>n</code>. If the current value is a palindrome (it reads the same forwards and backwards), stop. Otherwise replace the value with the sum of itself and its digit reversal, and check again.</p><p>Return the number of additions performed before a palindrome appears. If no palindrome has appeared after 30 additions, return <code>-1</code>.</p><pre>n = 57 -> 57 + 75 = 132 -> 132 + 231 = 363, so the answer is 2\nn = 10 -> 10 + 01 = 11, so the answer is 1\nn = 11 -> already a palindrome, so the answer is 0</pre>""",
    constraints=["1 &le; n &le; 2<sup>31</sup> - 1", "The answer is at most 30, or -1 when no palindrome is reached within 30 additions"],
    hints=["Simulate the process: keep a counter, and in each round reverse the digits, add them to the value and count the round.",
           "Reversing is easiest on the decimal string. Trailing zeros disappear when the reversed digits are read back as an integer, and that is the behaviour the process wants.",
           "Check for a palindrome before testing the limit, so that a palindrome reached on the 30th addition still counts. Return -1 only when the value is still not a palindrome after 30 additions."],
    editorial=["This is a direct simulation with a cap. In each round compare the value with its reversal, and if they differ add the reversal to the value. The check for a palindrome comes first, so the value reached after exactly 30 additions is still accepted.",
               "Values can grow large, but Python integers handle them, and the loop is capped at 30 rounds, so the work is small: each round costs time proportional to the number of digits. Some starting values, such as 196, never produce a palindrome within the cap, which is why the -1 answer exists."],
    time="O(30 * d)", space="O(d)",
    solution='''def reverseAddSteps(n):
    x = n
    steps = 0
    while str(x) != str(x)[::-1]:
        if steps == 30:
            return -1
        x += int(str(x)[::-1])
        steps += 1
    return steps
''',
    tests=[[1], [9], [10], [11], [56], [57], [89], [123], [196], [6553], [1000000], [2147447412], [2147483647]],
)


def b_revadd(n):
    x = n
    for k in range(31):
        s = str(x)
        if s == s[::-1]:
            return k
        x = x + int("".join(reversed(s)))
    return -1


def v_revadd(tests):
    for t in tests:
        n = t["args"][0]
        assert 1 <= n <= INT_MAX
        assert -1 <= t["expected"] <= 30


CHECKS["reverse-add-palindrome-steps"] = (b_revadd, lambda r: [r.randint(1, 10 ** 6)], "exact")
VALIDATE["reverse-add-palindrome-steps"] = v_revadd

p = add(
    id="double-base-palindrome-sum", title="Palindromes in Base 10 and Base 2", diff="Medium", topic="Math & Bit Manipulation",
    fn="doubleBasePalindromeSum", params=[("limit", "int")], ret="int", cmp="exact", tier="extra",
    desc="""<p>A number is a <em>double-base palindrome</em> when its decimal representation (without leading zeros) reads the same forwards and backwards, and its binary representation does too. For example 585 is a decimal palindrome, and its binary form 1001001001 is also a palindrome.</p><p>Given <code>limit</code>, return the sum of all double-base palindromes from 1 to <code>limit</code> inclusive.</p><pre>limit = 10 -> 25    (1 + 3 + 5 + 7 + 9)\nlimit = 1  -> 1</pre>""",
    constraints=["1 &le; limit &le; 10<sup>6</sup>", "The answer fits in a 32-bit signed integer"],
    hints=["Testing every number up to limit in both bases is correct, but it does more work than necessary. Could you enumerate a smaller set of candidates?",
           "Decimal palindromes are rare. Each one is fixed by its first half, so there are only about 2,000 of them below one million.",
           "Build every decimal palindrome of each length from its first half, skip those above limit, and test the binary form of the remaining ones."],
    editorial=["Enumerate the decimal palindromes. For each length L, take every first half of ceil(L / 2) digits, mirror it to get the full palindrome (keeping the middle digit once when L is odd), and skip the value if it exceeds limit. Only about 2,000 candidates survive below one million, and each is tested in binary with a string reversal.",
               "A plain loop from 1 to limit checks every number and is still correct for small limits, but the enumeration reduces the work from linear to roughly the square root of the number of digit strings. Binary palindromes can be checked by reversing bin(x) without its prefix."],
    time="O(10^(d/2))", space="O(d)",
    solution='''def doubleBasePalindromeSum(limit):
    total = 0
    for length in range(1, len(str(limit)) + 1):
        half = (length + 1) // 2
        for pre in range(10 ** (half - 1), 10 ** half):
            s = str(pre)
            full = s + s[::-1] if length % 2 == 0 else s + s[-2::-1]
            x = int(full)
            if x > limit:
                continue
            b = bin(x)[2:]
            if b == b[::-1]:
                total += x
    return total
''',
    tests=[[1], [2], [10], [100], [1000], [3000], [10000], [50000], [123456], [777777], [999999], [1000000]],
)


def b_double_base(limit):
    total = 0
    for x in range(1, limit + 1):
        s = str(x)
        b = bin(x)[2:]
        if s == s[::-1] and b == b[::-1]:
            total += x
    return total


def v_double_base(tests):
    for t in tests:
        limit = t["args"][0]
        assert 1 <= limit <= 10 ** 6
        assert 1 <= t["expected"] <= INT_MAX


CHECKS["double-base-palindrome-sum"] = (b_double_base, lambda r: [r.randint(1, 3000)], "exact")
VALIDATE["double-base-palindrome-sum"] = v_double_base

p = add(
    id="smallest-repunit-divisible-by-k", title="Smallest Repunit Divisible by K", diff="Medium", topic="Math & Bit Manipulation",
    fn="smallestRepunitLength", params=[("k", "int")], ret="int", cmp="exact", tier="extra",
    desc="""<p>A <em>repunit</em> is a positive integer whose decimal digits are all 1: 1, 11, 111, 1111, and so on. Given a positive integer <code>k</code>, find the smallest repunit that is divisible by <code>k</code>, and return its number of digits.</p><p>If no repunit is divisible by <code>k</code>, return <code>-1</code>.</p><pre>k = 3 -> 3    (111 = 3 * 37)\nk = 7 -> 6    (111111 = 7 * 15873)\nk = 2 -> -1</pre>""",
    constraints=["1 &le; k &le; 100,000"],
    hints=["Build the repunits one digit at a time. A repunit is 10 times the previous one plus 1.",
           "Keep only the remainder modulo k. Because the remainder takes one of k values, a repeat must occur within k steps, so the search can stop after k lengths.",
           "Every repunit ends in the digit 1, so it can never be divisible by 2 or by 5. Those values of k can be answered at once."],
    editorial=["Let r_L be the repunit with L digits. Then r_L = 10 * r_(L-1) + 1, so the remainder of r_L modulo k can be updated from the previous remainder without ever forming the big number. Scan the lengths from 1 upward and stop at the first zero remainder.",
               "Why k lengths are enough: consider r_0 = 0 together with r_1 to r_k, which gives k + 1 remainders with only k possible values, so two of them coincide. The difference of those two repunits is 10^i times a repunit, so when k is coprime to 10 the shorter repunit is also divisible by k. If k is even or divisible by 5 no repunit can qualify. The time is O(k) and the space is O(1)."],
    time="O(k)", space="O(1)",
    solution='''def smallestRepunitLength(k):
    if k % 2 == 0 or k % 5 == 0:
        return -1
    r = 0
    for length in range(1, k + 1):
        r = (r * 10 + 1) % k
        if r == 0:
            return length
    return -1
''',
    tests=[[1], [2], [3], [4], [5], [7], [9], [11], [13], [41], [271], [1001], [65537], [99999], [99991], [100000]],
)


def b_repunit(k):
    for length in range(1, k + 1):
        if int("1" * length) % k == 0:
            return length
    return -1


def v_repunit(tests):
    for t in tests:
        k = t["args"][0]
        assert 1 <= k <= 100000
        assert t["expected"] == -1 or 1 <= t["expected"] <= k
        if k % 2 == 0 or k % 5 == 0:
            assert t["expected"] == -1


CHECKS["smallest-repunit-divisible-by-k"] = (b_repunit, lambda r: [r.randint(1, 300)], "exact")
VALIDATE["smallest-repunit-divisible-by-k"] = v_repunit

p = add(
    id="rotated-digits-good-count", title="Good Rotated Numbers", diff="Medium", topic="Math & Bit Manipulation",
    fn="countGoodRotated", params=[("n", "int")], ret="int", cmp="exact",
    desc="""<p>Rotate every digit of a number by 180 degrees, as if the number were printed on paper and turned upside down. The digits 0, 1 and 8 look the same after rotation, the digits 2 and 5 swap with each other, the digits 6 and 9 swap with each other, and the digits 3, 4 and 7 are not valid after rotation.</p><p>A number is <em>good</em> when every one of its digits is valid after rotation and the rotated number differs from the original. Given <code>n</code>, count the good numbers from 1 to <code>n</code> inclusive.</p><pre>n = 10 -> 4    (2, 5, 6 and 9 are good; 1, 8 and 10 are not)</pre>""",
    constraints=["1 &le; n &le; 100,000"],
    hints=["A number with a 3, 4 or 7 in it is never good. Otherwise it is good exactly when at least one of its digits is 2, 5, 6 or 9.",
           "Map each digit to its rotated digit with a lookup table, then compare the rotated string with the original string.",
           "With n up to 100,000, a direct loop over 1 to n with string translation is fast enough, so you do not need a digit DP."],
    editorial=["Work with the decimal string of each candidate. Reject it if it contains 3, 4 or 7. Otherwise translate each digit with the rotation table (0, 1 and 8 map to themselves, 2 and 5 swap, 6 and 9 swap) and check whether the translated string differs from the original.",
               "A translation table turns each candidate into a single C-level operation, so checking every number up to 100,000 stays well inside the time budget. A digit DP over the digits of n would also work, but it is more code than the limit requires."],
    time="O(n * d)", space="O(d)",
    solution='''def countGoodRotated(n):
    table = str.maketrans('0125689', '0152986')
    count = 0
    for x in range(1, n + 1):
        s = str(x)
        if '3' in s or '4' in s or '7' in s:
            continue
        if s.translate(table) != s:
            count += 1
    return count
''',
    tests=[[1], [2], [5], [10], [11], [20], [100], [1000], [9999], [12345], [50000], [65432], [88888], [99999], [100000]],
)


def b_rotated(n):
    rot = {"0": "0", "1": "1", "8": "8", "2": "5", "5": "2", "6": "9", "9": "6"}
    count = 0
    for x in range(1, n + 1):
        s = str(x)
        if any(ch not in rot for ch in s):
            continue
        r = "".join(rot[ch] for ch in s)
        if r != s:
            count += 1
    return count


def v_rotated(tests):
    for t in tests:
        n = t["args"][0]
        assert 1 <= n <= 100000
        assert 0 <= t["expected"] <= n


CHECKS["rotated-digits-good-count"] = (b_rotated, lambda r: [r.randint(1, 600)], "exact")
VALIDATE["rotated-digits-good-count"] = v_rotated


# ---------------------------------------------------------------- HARD

p = add(
    id="closest-palindrome-number", title="Closest Palindrome Number", diff="Hard", topic="Math & Bit Manipulation",
    fn="nearestPalindrome", params=[("n", "int")], ret="int", cmp="exact",
    desc="""<p>A palindrome reads the same forwards and backwards. Given a positive integer <code>n</code>, find the palindrome closest to <code>n</code> among the positive integers other than <code>n</code> itself. Distance is the absolute difference. If two palindromes are equally close, return the smaller one.</p><pre>n = 99   -> 101   (distance 2; 88 is at distance 11)\nn = 1    -> 2\nn = 1000 -> 999   (999 and 1001 are both at distance 1, so the smaller one wins)</pre>""",
    constraints=["1 &le; n &le; 10<sup>9</sup>"],
    hints=["The closest palindrome is nearly always obtained by mirroring the first half of n, or the first half changed by plus or minus one.",
           "Mirror the first ceil(L / 2) digits of n for prefixes p-1, p and p+1. Two extra candidates cover prefixes that carry across a power of 10: the number 99...9 with one digit fewer, and 10...01 with one digit more.",
           "Collect these candidates, discard any that equal n or are not positive, and pick the one with the smallest distance. On a tie, take the smaller value."],
    editorial=["Let L be the number of digits of n and let p be its first ceil(L / 2) digits. Mirroring p gives a palindrome of the same length, and changing p by one gives the next and previous palindromes of that length, which are the only ones that can be nearest, except when the carry changes the digit count. For those cases add the largest palindrome with L - 1 digits, 10^(L-1) - 1, and the smallest palindrome with L + 1 digits, 10^L + 1.",
               "With at most five candidates the answer is a constant-time selection. Sorting the candidates by the key (distance, value) gives the tie rule for free. The cost is O(d) for the string work on d digits."],
    time="O(d)", space="O(d)",
    solution='''def nearestPalindrome(n):
    s = str(n)
    L = len(s)
    half = (L + 1) // 2
    pre = int(s[:half])
    cands = {10 ** (L - 1) - 1, 10 ** L + 1}
    for d in (-1, 0, 1):
        q = str(pre + d)
        if len(q) != half:
            continue
        cands.add(int(q + q[-2::-1]) if L % 2 else int(q + q[::-1]))
    best = None
    for c in cands:
        if c < 1 or c == n:
            continue
        key = (abs(c - n), c)
        if best is None or key < best:
            best = key
    return best[1]
''',
    tests=[[1], [2], [9], [10], [11], [21], [99], [100], [101], [808], [1000], [1234], [11111], [10000], [12321],
           [123456], [999999999], [1000000000], [987654321], [100000000]],
)


def b_nearest_pal(n):
    d = 1
    while True:
        lo = n - d
        if lo >= 1 and str(lo) == str(lo)[::-1]:
            return lo
        hi = n + d
        if str(hi) == str(hi)[::-1]:
            return hi
        d += 1


def v_nearest_pal(tests):
    for t in tests:
        n = t["args"][0]
        c = t["expected"]
        assert 1 <= n <= 10 ** 9
        assert 1 <= c <= INT_MAX and c != n
        assert str(c) == str(c)[::-1]


CHECKS["closest-palindrome-number"] = (b_nearest_pal, lambda r: [r.randint(1, 100000)], "exact")
VALIDATE["closest-palindrome-number"] = v_nearest_pal

p = add(
    id="next-same-digit-sum-number", title="Next Number With the Same Digit Sum", diff="Hard", topic="Math & Bit Manipulation",
    fn="nextSameDigitSum", params=[("n", "int")], ret="int", cmp="exact", tier="extra",
    desc="""<p>Given a positive integer <code>n</code>, return the smallest integer greater than <code>n</code> whose decimal digits add up to the same total as the digits of <code>n</code>.</p><pre>n = 1  -> 10    (digit sum 1)\nn = 19 -> 28    (digit sum 10)\nn = 99 -> 189   (digit sum 18)</pre>""",
    constraints=["1 &le; n &le; 99,999,999"],
    hints=["Adding one at a time until the digit sum matches is correct but can be slow: from 1999 the next match is 2899.",
           "The answer keeps the longest possible prefix of n. Look for the rightmost position i where you can raise the digit and still complete the number with the right total.",
           "Once the prefix and the raised digit are fixed, the remaining digits must sum to a known total. The smallest filler of a given length and sum puts the smallest digits on the left, and it exists whenever the sum is between 0 and 9 times the length."],
    editorial=["Pad n with a leading 0 so that a longer answer is possible. The answer agrees with n on a prefix, has a larger digit at some position i, and then has a free tail. A longer common prefix always gives a smaller result, so try positions from right to left and, for each one, the smallest raised digit d that leaves a feasible tail. The first feasible position wins.",
               "The tail needs the digit sum total - prefix_sum - d, spread over the remaining positions. The smallest tail of that sum and length is built greedily from the left: at each position choose the smallest digit that still leaves a sum the remaining positions can reach. The whole procedure is O(d^2) for d digits, which is trivial for n below 10^8."],
    time="O(d^2)", space="O(d)",
    solution='''def nextSameDigitSum(n):
    s = [0] + [int(c) for c in str(n)]
    L = len(s)
    total = sum(s)
    pref = [0] * (L + 1)
    for i in range(L):
        pref[i + 1] = pref[i] + s[i]
    for i in range(L - 1, -1, -1):
        rem = L - i - 1
        for d in range(s[i] + 1, 10):
            need = total - pref[i] - d
            if 0 <= need <= 9 * rem:
                tail = []
                left = need
                for j in range(rem):
                    slots_after = rem - j - 1
                    for c in range(10):
                        if 0 <= left - c <= 9 * slots_after:
                            tail.append(c)
                            left -= c
                            break
                return int(''.join(map(str, s[:i] + [d] + tail)))
    return -1
''',
    tests=[[1], [2], [8], [9], [10], [18], [19], [20], [99], [100], [999], [1000], [1999], [12345], [50000000],
           [98765432], [99999999], [10000000]],
)


def b_next_sum(n):
    target = sum(int(c) for c in str(n))
    m = n + 1
    while sum(int(c) for c in str(m)) != target:
        m += 1
    return m


def v_next_sum(tests):
    for t in tests:
        n = t["args"][0]
        m = t["expected"]
        assert 1 <= n <= 99999999
        assert n < m <= 999999999
        assert sum(map(int, str(m))) == sum(map(int, str(n)))


CHECKS["next-same-digit-sum-number"] = (b_next_sum, lambda r: [r.randint(1, 2000)], "exact")
VALIDATE["next-same-digit-sum-number"] = v_next_sum
