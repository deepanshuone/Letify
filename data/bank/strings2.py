"""Problems: strings (second batch). See data/lib.py for the registry."""
from collections import Counter  # noqa: F401

from lib import add, rnd, CHECKS, VALIDATE, gen_arr  # noqa: F401

INT_MIN, INT_MAX = -(2 ** 31), 2 ** 31 - 1
LET = "abcdefghijklmnopqrstuvwxyz"
LD = LET + "0123456789"


def _rs(r, n, alpha=LET):
    return "".join(r.choice(alpha) for _ in range(n))


def _is_ld(s):
    return all(("a" <= c <= "z") or ("0" <= c <= "9") for c in s)


def _to_roman(n):
    """Digit-by-digit Roman numeral builder, used to produce test inputs and as an independent oracle."""
    out = ""
    for d, (one, five, ten) in zip(str(n).zfill(4), (("m", "", ""), ("c", "d", "m"), ("x", "l", "c"), ("i", "v", "x"))):
        d = int(d)
        if d < 4:
            out += one * d
        elif d == 4:
            out += one + five
        elif d < 9:
            out += five + one * (d - 5)
        else:
            out += one + ten
    return out


# ---------------------------------------------------------------- EASY

p = add(
    id="string-rotation-check", title="String Rotation Check", diff="Easy", topic="Strings",
    fn="isRotation", params=[("s", "string"), ("t", "string")], ret="bool", cmp="exact",
    desc="<p>A <em>rotation</em> of a string moves some number of characters (possibly zero) from its front to its back, keeping their order. For example, rotating <code>\"abcde\"</code> by two gives <code>\"cdeab\"</code>.</p><p>Given strings <code>s</code> and <code>t</code>, return <code>true</code> if <code>t</code> is a rotation of <code>s</code>, otherwise <code>false</code>. The two strings may have different lengths, in which case the answer is <code>false</code>.</p><p>For example, <code>\"abcde\"</code> and <code>\"cdeab\"</code> give <code>true</code>; <code>\"abcde\"</code> and <code>\"abced\"</code> give <code>false</code>; <code>\"aab\"</code> and <code>\"aba\"</code> give <code>true</code>.</p>",
    constraints=["1 &le; s.length, t.length &le; 50,000", "s and t consist of lowercase letters and digits"],
    hints=["Trying every rotation of <code>s</code> and comparing it with <code>t</code> works, but costs O(n&sup2;) for long strings. If the lengths differ you can answer immediately.",
           "Write <code>s</code> twice in a row, for example <code>\"abcde\"</code> becomes <code>\"abcdeabcde\"</code>. Where do the rotations of <code>s</code> show up in that doubled string?",
           "Every rotation of <code>s</code> is a substring of length <code>n</code> of <code>s + s</code>, and nothing else of that length is. So after checking the lengths, ask whether <code>t</code> occurs inside <code>s + s</code>."],
    editorial=["If the lengths differ, the answer is false. Otherwise, a rotation by k turns <code>s = XY</code> into <code>YX</code>, where <code>X</code> is the first k characters. The doubled string <code>s + s = XYXY</code> contains <code>YX</code> starting at position k, and the n-length windows of <code>s + s</code> are exactly the n rotations of <code>s</code>. So <code>t</code> is a rotation of <code>s</code> if and only if the lengths are equal and <code>t</code> occurs in <code>s + s</code>.",
               "A naive substring search could cost O(n&sup2;) on repetitive input, so for a guaranteed linear bound use KMP or the Z-function on <code>t + '#' + s + s</code>. Modern built-in substring search is also fast in practice. Comparing all n rotations one by one is the O(n&sup2;) baseline."],
    time="O(n)", space="O(n)",
    solution='''def isRotation(s, t):
    if len(s) != len(t):
        return False
    return t in s + s
''',
    tests=[["abcde", "cdeab"], ["abcde", "abced"], ["aab", "aba"], ["a", "a"], ["a", "b"], ["ab", "abc"], ["abc", "ab"],
           ["aaaa", "aaaa"], ["abab", "baba"], ["abab", "abba"], ["xyz123", "123xyz"], ["xyz123", "12xyz3"], ["xyz123", "3xyz12"]],
)
_r = rnd(8101)
_s = _rs(_r, 50000, LD)
p["tests"].append([_s, _s[17321:] + _s[:17321]])
p["tests"].append([_s, _s[17321:] + _s[:17320] + ("a" if _s[17320] != "a" else "b")])
_s = "a" * 49999 + "b"
p["tests"].append([_s, "a" * 25000 + "b" + "a" * 24999])
p["tests"].append(["a" * 50000, "a" * 49999 + "b"])
_s = _rs(_r, 30000, "ab")
p["tests"].append([_s, _s[::-1]])
p["tests"].append([_s, _s[1:]])


def b_rot(s, t):
    if len(s) != len(t):
        return False
    return any(s[i:] + s[:i] == t for i in range(len(s)))


def g_rot(r):
    s = _rs(r, r.randint(1, 8), "ab")
    k = r.randrange(len(s))
    mode = r.random()
    if mode < 0.5:
        t = s[k:] + s[:k]
    elif mode < 0.8:
        t = _rs(r, len(s), "ab")
    else:
        t = _rs(r, r.randint(1, 9), "ab")
    return [s, t]


def v_rot(tests):
    for t in tests:
        s, u = t["args"]
        assert 1 <= len(s) <= 50000 and 1 <= len(u) <= 50000
        assert _is_ld(s) and _is_ld(u)
    assert any(t["expected"] for t in tests) and any(not t["expected"] for t in tests)


CHECKS["string-rotation-check"] = (b_rot, g_rot, "exact")
VALIDATE["string-rotation-check"] = v_rot

p = add(
    id="add-binary-strings", title="Add Binary Strings", diff="Easy", topic="Strings",
    fn="addBinary", params=[("a", "string"), ("b", "string")], ret="string", cmp="exact",
    desc="<p>The strings <code>a</code> and <code>b</code> each hold a non-negative integer written in binary. Return their sum, also as a binary string.</p><p>The result must not have leading zeros unless it is exactly <code>\"0\"</code>. The inputs can be far longer than any built-in integer type, so do the addition yourself, digit by digit.</p><p>For example, <code>\"11\"</code> + <code>\"1\"</code> gives <code>\"100\"</code>, and <code>\"1010\"</code> + <code>\"1011\"</code> gives <code>\"10101\"</code>.</p>",
    constraints=["1 &le; a.length, b.length &le; 10,000", "a and b contain only the characters 0 and 1", "Neither string has leading zeros, except for the string \"0\" itself"],
    hints=["Add the way you do on paper: start from the rightmost digits and move left, remembering a carry.",
           "At every position the digit sum is <code>bitA + bitB + carry</code>, which is between 0 and 3. The new digit is that sum modulo 2, and the new carry is the sum divided by 2.",
           "Keep going while either string has digits left or the carry is non-zero. Collect the digits in a list and reverse it at the end instead of prepending to a string."],
    editorial=["Use two pointers starting at the last character of each string and a carry initialised to 0. In each step add the current digit of each string (treating an exhausted string as 0) plus the carry. Append <code>sum % 2</code> to the output and set <code>carry = sum // 2</code>. When both strings are exhausted and the carry is zero, reverse the collected digits to get the answer.",
               "Because both inputs have no leading zeros, the result never has them either, except that <code>\"0\"+\"0\"</code> yields a single <code>\"0\"</code>. Converting to integers and back is not allowed in spirit here: the point is the digit-by-digit procedure, which runs in O(max(n, m)) time and works for numbers of any size."],
    time="O(n + m)", space="O(n + m)",
    solution='''def addBinary(a, b):
    i, j = len(a) - 1, len(b) - 1
    carry = 0
    out = []
    while i >= 0 or j >= 0 or carry:
        total = carry
        if i >= 0:
            total += ord(a[i]) - 48
            i -= 1
        if j >= 0:
            total += ord(b[j]) - 48
            j -= 1
        out.append(chr(48 + total % 2))
        carry = total // 2
    out.reverse()
    return "".join(out) if out else "0"
''',
    tests=[["11", "1"], ["1010", "1011"], ["0", "0"], ["0", "1"], ["1", "1"], ["1", "0"], ["1111", "1"], ["101", "1010101"],
           ["100000", "100000"], ["1", "1" * 20], ["10" * 8, "1" * 7]],
)
_r = rnd(8102)
p["tests"].append(["1" * 10000, "1"])
p["tests"].append(["1" * 10000, "1" * 10000])
p["tests"].append(["1" + _rs(_r, 9999, "01"), "1" + _rs(_r, 9999, "01")])
p["tests"].append(["1" + _rs(_r, 9998, "01"), "1" + _rs(_r, 4000, "01")])
p["tests"].append(["1" + "0" * 9999, "1" + "0" * 9999])


def b_addbin(a, b):
    return bin(int(a, 2) + int(b, 2))[2:]


def g_addbin(r):
    def one():
        n = r.randint(1, 9)
        return "0" if n == 1 and r.random() < 0.3 else "1" + _rs(r, n - 1, "01")
    return [one(), one()]


def v_addbin(tests):
    for t in tests:
        for x in t["args"]:
            assert 1 <= len(x) <= 10000 and set(x) <= {"0", "1"}
            assert x == "0" or x[0] == "1"


CHECKS["add-binary-strings"] = (b_addbin, g_addbin, "exact")
VALIDATE["add-binary-strings"] = v_addbin

p = add(
    id="roman-numeral-to-integer", title="Roman Numeral to Integer", diff="Easy", topic="Strings",
    fn="romanToInt", params=[("s", "string")], ret="int", cmp="exact",
    desc="<p>Roman numerals use seven symbols, written here in lowercase: <code>i</code>=1, <code>v</code>=5, <code>x</code>=10, <code>l</code>=50, <code>c</code>=100, <code>d</code>=500, <code>m</code>=1000.</p><p>Symbols are normally written from largest to smallest, left to right, and their values are added. There are six exceptions where a smaller symbol sits in front of a larger one and is <em>subtracted</em>: <code>iv</code>=4, <code>ix</code>=9, <code>xl</code>=40, <code>xc</code>=90, <code>cd</code>=400, <code>cm</code>=900.</p><p>Given a valid numeral <code>s</code> in this standard form, return the integer it represents. For example, <code>\"iii\"</code> is <code>3</code>, <code>\"lviii\"</code> is <code>58</code> and <code>\"mcmxciv\"</code> is <code>1994</code>.</p>",
    constraints=["1 &le; s.length &le; 15", "s is a valid Roman numeral in standard form, representing an integer from 1 to 3999", "s contains only the lowercase symbols i, v, x, l, c, d, m"],
    hints=["Adding the value of every symbol gets most numerals right. It fails only for the subtractive pairs such as <code>iv</code> and <code>cm</code>.",
           "A symbol should be subtracted exactly when the symbol after it is worth more.",
           "Scan left to right; for each position, add its value, unless the next symbol has a larger value, in which case subtract it."],
    editorial=["Map each symbol to its value. Walk through the string: if the value at position i is smaller than the value at position i+1, it is the small half of a subtractive pair, so subtract it; otherwise add it. For <code>\"mcmxciv\"</code> this computes 1000 - 100 + 1000 - 10 + 100 - 1 + 5 = 1994.",
               "An equivalent view scans right to left, keeping the previous value, and subtracts the current value whenever it is smaller than the one to its right. Either way the string is read once, giving O(n) time and O(1) space (the lookup table has seven entries)."],
    time="O(n)", space="O(1)",
    solution='''def romanToInt(s):
    val = {"i": 1, "v": 5, "x": 10, "l": 50, "c": 100, "d": 500, "m": 1000}
    total = 0
    for i, ch in enumerate(s):
        v = val[ch]
        if i + 1 < len(s) and v < val[s[i + 1]]:
            total -= v
        else:
            total += v
    return total
''',
    tests=[["iii"], ["lviii"], ["mcmxciv"], ["i"], ["iv"], ["ix"], ["xl"], ["xc"], ["cd"], ["cm"], ["mmmcmxcix"],
           ["mmmdccclxxxviii"], ["mmxxvi"], ["dcccxlv"], ["mmcdxliv"], ["xlix"], ["m"]],
)


def b_r2i(s):
    table = {_to_roman(n): n for n in range(1, 4000)}
    return table[s]


def g_r2i(r):
    return [_to_roman(r.randint(1, 3999) if r.random() < 0.7 else r.randint(1, 60))]


def v_r2i(tests):
    for t in tests:
        s = t["args"][0]
        assert 1 <= len(s) <= 15 and set(s) <= set("ivxlcdm")
        assert 1 <= t["expected"] <= 3999 and _to_roman(t["expected"]) == s, "not a standard numeral"


CHECKS["roman-numeral-to-integer"] = (b_r2i, g_r2i, "exact")
VALIDATE["roman-numeral-to-integer"] = v_r2i

# ---------------------------------------------------------------- MEDIUM

p = add(
    id="integer-to-roman-numeral", title="Integer to Roman Numeral", diff="Medium", topic="Strings",
    fn="intToRoman", params=[("num", "int")], ret="string", cmp="exact",
    desc="<p>Convert a positive integer to its Roman numeral, written with lowercase symbols: <code>i</code>=1, <code>v</code>=5, <code>x</code>=10, <code>l</code>=50, <code>c</code>=100, <code>d</code>=500, <code>m</code>=1000.</p><p>The numeral is built from the decimal digits of the number, thousands first. Each non-zero digit is written with its own symbols and zero digits are skipped. Inside one digit the symbols are written largest to smallest and added, except for the six subtractive forms <code>iv</code>=4, <code>ix</code>=9, <code>xl</code>=40, <code>xc</code>=90, <code>cd</code>=400, <code>cm</code>=900. A symbol is never repeated more than three times in a row.</p><p>For example, <code>3</code> becomes <code>\"iii\"</code>, <code>58</code> becomes <code>\"lviii\"</code> and <code>1994</code> becomes <code>\"mcmxciv\"</code>.</p>",
    constraints=["1 &le; num &le; 3999"],
    hints=["Think of the number one decimal digit at a time. The digit 7 in the tens place is worth 70, which is written <code>lxx</code>.",
           "Each digit position has its own trio of symbols (one, five, ten), such as <code>x</code>, <code>l</code>, <code>c</code> for the tens place. The digit then decides the pattern: 1-3 repeat the 'one' symbol, 4 is one+five, 5-8 is five followed by up to three 'ones', 9 is one+ten.",
           "Alternatively, list all thirteen values in descending order (1000, 900, 500, 400, 100, 90, 50, 40, 10, 9, 5, 4, 1) with their symbols and greedily take the largest value that still fits, appending its symbols each time."],
    editorial=["The greedy method works because the table of thirteen values already contains the six subtractive forms as if they were single symbols. Go through the table from large to small and, while the remaining number is at least the current value, append its symbol string and subtract the value. Because the table is sorted and contains every allowed token, the first token that fits is always the correct next piece of the standard numeral.",
               "The digit-by-digit method gives the same result: split the number into thousands, hundreds, tens and ones and look up each part in a small pattern table. Both approaches do a constant amount of work, since the output never exceeds 15 symbols."],
    time="O(1)", space="O(1)",
    solution='''def intToRoman(num):
    table = [(1000, "m"), (900, "cm"), (500, "d"), (400, "cd"), (100, "c"), (90, "xc"),
             (50, "l"), (40, "xl"), (10, "x"), (9, "ix"), (5, "v"), (4, "iv"), (1, "i")]
    out = []
    for value, sym in table:
        while num >= value:
            out.append(sym)
            num -= value
    return "".join(out)
''',
    tests=[[3], [58], [1994], [1], [4], [9], [40], [90], [400], [900], [3999], [3888], [2026], [1000], [444], [49], [3000], [1666]],
)


def g_i2r(r):
    return [r.randint(1, 3999) if r.random() < 0.7 else r.randint(1, 100)]


def v_i2r(tests):
    for t in tests:
        assert 1 <= t["args"][0] <= 3999
        assert t["expected"] == _to_roman(t["args"][0])


CHECKS["integer-to-roman-numeral"] = (_to_roman, g_i2r, "exact")
VALIDATE["integer-to-roman-numeral"] = v_i2r

p = add(
    id="multiply-decimal-strings", title="Multiply Decimal Strings", diff="Medium", topic="Strings",
    fn="multiply", params=[("num1", "string"), ("num2", "string")], ret="string", cmp="exact",
    desc="<p>The strings <code>num1</code> and <code>num2</code> each hold a non-negative integer in decimal. Return their product as a string.</p><p>The numbers can have hundreds of digits, so they do not fit in the built-in integer types. Do the multiplication yourself on the digits, the way it is done by hand, instead of converting the whole strings to integers.</p><p>For example, <code>\"12\"</code> &times; <code>\"12\"</code> is <code>\"144\"</code>, and <code>\"123\"</code> &times; <code>\"0\"</code> is <code>\"0\"</code>.</p>",
    constraints=["1 &le; num1.length, num2.length &le; 200", "num1 and num2 contain only digits 0-9", "Neither number has leading zeros, except the number 0 itself"],
    hints=["Remember long multiplication: every digit of one number multiplies every digit of the other, and the partial products are added at shifted positions.",
           "The product of a digit at position <code>i</code> (counted from the right in <code>num1</code>) and one at position <code>j</code> in <code>num2</code> contributes to position <code>i + j</code> of the result. The result has at most <code>n + m</code> digits.",
           "Accumulate all products into an array of size <code>n + m</code> first, then do one pass from the lowest position upward to propagate carries. Finally strip leading zeros, keeping at least one digit."],
    editorial=["Reverse both numbers so that index 0 is the ones digit. Allocate <code>res</code> of length <code>n + m</code>. For each pair <code>(i, j)</code>, add <code>a[i] * b[j]</code> to <code>res[i + j]</code>. No entry can get large, since each holds at most min(n, m) products of at most 81 each.",
               "Then make one carry pass: for k from 0 upward, <code>total = res[k] + carry</code>, store <code>total % 10</code> and carry <code>total // 10</code>. Drop leading zeros from the high end (leave a single 0 if the product is zero) and reverse the digits into a string. The running time is O(n &middot; m), which is fine for 200 digits."],
    time="O(n * m)", space="O(n + m)",
    solution='''def multiply(num1, num2):
    a = [ord(c) - 48 for c in reversed(num1)]
    b = [ord(c) - 48 for c in reversed(num2)]
    res = [0] * (len(a) + len(b))
    for i, x in enumerate(a):
        if x == 0:
            continue
        for j, y in enumerate(b):
            res[i + j] += x * y
    carry = 0
    for k in range(len(res)):
        total = res[k] + carry
        res[k] = total % 10
        carry = total // 10
    while len(res) > 1 and res[-1] == 0:
        res.pop()
    return "".join(chr(48 + d) for d in reversed(res))
''',
    tests=[["12", "12"], ["123", "456"], ["123", "0"], ["0", "0"], ["1", "1"], ["9", "9"], ["99", "99"], ["1000", "1000"],
           ["999999999", "999999999"], ["12345678901234567890", "98765432109876543210"], ["5", "20"], ["100", "7"]],
)
_r = rnd(8103)
p["tests"].append(["9" * 200, "9" * 200])
p["tests"].append(["1" + "0" * 199, "1" + "0" * 199])
p["tests"].append(["1" + _rs(_r, 199, "0123456789"), "1" + _rs(_r, 199, "0123456789")])
p["tests"].append(["1" + _rs(_r, 199, "0123456789"), "0"])
p["tests"].append(["8" + _rs(_r, 199, "0123456789"), "1"])
p["tests"].append(["1" + _rs(_r, 150, "0123456789"), "9" + _rs(_r, 30, "0123456789")])


def b_mul(a, b):
    return str(int(a) * int(b))


def g_mul(r):
    def one():
        n = r.randint(1, 8)
        return "0" if r.random() < 0.1 else str(r.randint(1, 9)) + _rs(r, n - 1, "0123456789")
    return [one(), one()]


def v_mul(tests):
    for t in tests:
        for x in t["args"]:
            assert 1 <= len(x) <= 200 and x.isdigit()
            assert x == "0" or x[0] != "0"


CHECKS["multiply-decimal-strings"] = (b_mul, g_mul, "exact")
VALIDATE["multiply-decimal-strings"] = v_mul

p = add(
    id="zigzag-conversion-rows", title="Zigzag Conversion", diff="Medium", topic="Strings",
    fn="convertZigzag", params=[("s", "string"), ("numRows", "int")], ret="string", cmp="exact",
    desc="<p>Write the characters of <code>s</code> in a zigzag over <code>numRows</code> rows: go down one character per row from the first row to the last, then go diagonally up one character per row until you are back at the first row, and repeat. Then read the rows one after another, top to bottom, left to right, and join them into a new string.</p><p>For <code>s = \"paypalishiring\"</code> and <code>numRows = 3</code> the layout is</p><pre>p   a   h   n\na p l s i i g\ny   i   r</pre><p>and the answer is <code>\"pahnaplsiigyir\"</code>. With <code>numRows = 1</code> the string is returned unchanged.</p>",
    constraints=["1 &le; s.length &le; 5,000", "1 &le; numRows &le; 1,000", "s consists of lowercase letters and digits"],
    hints=["You do not need to build the 2D picture. The only thing that matters is which row each character lands on.",
           "Walk through the string keeping a current row and a direction. The row goes 0, 1, ..., numRows-1, then back down numRows-2, ..., 0 and so on. Flip the direction at the first and last rows (careful when <code>numRows == 1</code>).",
           "Append each character to the bucket of its row, then join the buckets. For an O(1)-extra-space version, use the cycle length <code>2 * (numRows - 1)</code>: row <code>r</code> takes the characters at <code>r + k*cycle</code> and <code>cycle*(k+1) - r</code>."],
    editorial=["Simulation: keep a list of numRows buckets. For each character, append it to the bucket for the current row, then move the row by +1 or -1. When the row reaches 0 or numRows-1, reverse the direction. The special case numRows = 1 (or numRows &ge; len(s)) returns s directly, since there is no zigzag to speak of. Concatenating the buckets gives the answer in O(n).",
               "Direct indexing works too. The pattern repeats every <code>cycle = 2 * (numRows - 1)</code> characters. In row r, the characters at indices <code>r, r + cycle, r + 2*cycle, ...</code> belong to the 'vertical' strokes, and for rows strictly between the first and the last there is one extra character per cycle, at index <code>k*cycle + cycle - r</code>, on the diagonal stroke."],
    time="O(n)", space="O(n)",
    solution='''def convertZigzag(s, numRows):
    if numRows == 1 or numRows >= len(s):
        return s
    rows = [[] for _ in range(numRows)]
    r, step = 0, 1
    for ch in s:
        rows[r].append(ch)
        if r == 0:
            step = 1
        elif r == numRows - 1:
            step = -1
        r += step
    return "".join("".join(row) for row in rows)
''',
    tests=[["paypalishiring", 3], ["paypalishiring", 4], ["ab", 1], ["a", 1], ["a", 5], ["abc", 2], ["abcd", 3], ["abcdef", 2],
           ["abcdefghij", 10], ["abcdefghij", 9], ["abcdefghij", 100], ["0123456789", 4]],
)
_r = rnd(8104)
for _n, _k in ((5000, 1), (5000, 2), (5000, 3), (5000, 7), (4999, 100), (5000, 999), (5000, 1000), (3000, 777)):
    p["tests"].append([_rs(_r, _n, LD), _k])


def b_zig(s, numRows):
    # explicit grid: down one column, then up the diagonal, one column per step
    grid = [[""] * (len(s) + 1) for _ in range(numRows)]
    row, col, down = 0, 0, True
    for ch in s:
        grid[row][col] = ch
        if numRows == 1:
            col += 1
        elif down:
            if row == numRows - 1:
                down = False
                row -= 1
                col += 1
            else:
                row += 1
        else:
            if row == 0:
                down = True
                row += 1
            else:
                row -= 1
                col += 1
    return "".join("".join(line) for line in grid)


def g_zig(r):
    return [_rs(r, r.randint(1, 14), LD), r.randint(1, 7) if r.random() < 0.9 else r.randint(8, 20)]


def v_zig(tests):
    for t in tests:
        s, k = t["args"]
        assert 1 <= len(s) <= 5000 and _is_ld(s) and 1 <= k <= 1000
        assert sorted(t["expected"]) == sorted(s)


CHECKS["zigzag-conversion-rows"] = (b_zig, g_zig, "exact")
VALIDATE["zigzag-conversion-rows"] = v_zig

p = add(
    id="longest-substring-each-char-at-least-k", title="Longest Substring With Every Character Repeated K Times", diff="Medium", topic="Strings",
    fn="longestSubstringAtLeastK", params=[("s", "string"), ("k", "int")], ret="int", cmp="exact",
    desc="<p>Given a string <code>s</code> and an integer <code>k</code>, find the longest substring of <code>s</code> in which <em>every</em> character that appears does so at least <code>k</code> times <em>within that substring</em>. Return its length, or <code>0</code> if no such substring exists.</p><p>For example, for <code>s = \"aaabb\"</code> and <code>k = 3</code> the answer is <code>3</code> (the substring <code>\"aaa\"</code>), for <code>s = \"ababbc\"</code> and <code>k = 2</code> it is <code>5</code> (the substring <code>\"ababb\"</code>), and for <code>s = \"abc\"</code> and <code>k = 2</code> it is <code>0</code>.</p>",
    constraints=["1 &le; s.length &le; 20,000", "1 &le; k &le; 20,000", "s consists of lowercase English letters"],
    hints=["Checking every substring with a frequency table is O(n&sup2;) and too slow for 20,000 characters. Look for characters that can never be part of an answer.",
           "Count the letters of the whole string. A letter that occurs fewer than k times in total cannot occur k times in any substring, so no valid substring contains it.",
           "Split the string at every such letter and solve each piece on its own, using the same rule again. If a piece has no rare letter at all, it is valid as a whole. The recursion is at most 26 levels deep."],
    editorial=["Divide and conquer. Count the characters of the current segment. If every character occurs at least k times, the whole segment is valid and its length is returned. Otherwise, any character with count below k can never belong to a valid substring inside this segment (its count in a sub-segment is at most its count here), so cut the segment at each occurrence of such characters and recurse on the pieces; the answer is the best piece.",
               "Each recursion level removes at least one distinct letter from consideration, so the depth is at most 26 and each level scans every character at most once: O(26 &middot; n) time. A sliding window variant also works: for each target number of distinct letters from 1 to 26, run a window that keeps exactly that many distinct letters and tracks how many of them have reached k."],
    time="O(26 * n)", space="O(n)",
    solution='''from collections import Counter


def longestSubstringAtLeastK(s, k):
    def solve(t):
        if len(t) < k:
            return 0
        cnt = Counter(t)
        bad = {c for c, v in cnt.items() if v < k}
        if not bad:
            return len(t)
        best = 0
        start = 0
        for i, c in enumerate(t):
            if c in bad:
                if i - start >= k:
                    best = max(best, solve(t[start:i]))
                start = i + 1
        if len(t) - start >= k:
            best = max(best, solve(t[start:]))
        return best

    return solve(s)
''',
    tests=[["aaabb", 3], ["ababbc", 2], ["abc", 2], ["a", 1], ["a", 2], ["aaaa", 1], ["aabbcc", 2], ["aabbcc", 3], ["abcabcabc", 3],
           ["weitong", 2], ["bbaaacbd", 3], ["ababacb", 3], ["zzzzzyzzzzz", 5]],
)
_r = rnd(8105)
p["tests"].append(["a" * 20000, 20000])
p["tests"].append(["a" * 19999 + "b", 2])
p["tests"].append([_rs(_r, 20000), 2])
p["tests"].append([_rs(_r, 20000, "abc"), 3000])
p["tests"].append([_rs(_r, 20000, "ab"), 5])
_blocks = []
for _i in range(26):
    _blocks.append(LET[_i] * (3 + _i))  # letter i appears often enough everywhere except where it is cut off
_s = "".join(_blocks * 3)
p["tests"].append([_s[:20000], 5])
_s = ""
for _i in range(26):
    _s += LET[_i] * 700 + LET[(_i + 1) % 26] * 5
p["tests"].append([_s[:20000], 700])
p["tests"].append(["".join(_r.choice("abcdefghij") * _r.randint(1, 40) for _ in range(900))[:20000], 12])


def b_lsk(s, k):
    best = 0
    n = len(s)
    for i in range(n):
        for j in range(i + 1, n + 1):
            c = Counter(s[i:j])
            if all(v >= k for v in c.values()):
                best = max(best, j - i)
    return best


def g_lsk(r):
    return [_rs(r, r.randint(1, 14), "abc" if r.random() < 0.7 else "abcd"), r.randint(1, 4)]


def v_lsk(tests):
    for t in tests:
        s, k = t["args"]
        assert 1 <= len(s) <= 20000 and 1 <= k <= 20000
        assert all("a" <= c <= "z" for c in s)


CHECKS["longest-substring-each-char-at-least-k"] = (b_lsk, g_lsk, "exact")
VALIDATE["longest-substring-each-char-at-least-k"] = v_lsk

p = add(
    id="longest-even-vowel-substring", title="Longest Substring With Even Vowel Counts", diff="Medium", topic="Strings",
    fn="longestEvenVowels", params=[("s", "string")], ret="int", cmp="exact",
    desc="<p>Given a string <code>s</code> of lowercase letters, find the longest substring in which each of the five vowels <code>a</code>, <code>e</code>, <code>i</code>, <code>o</code>, <code>u</code> appears an <em>even</em> number of times (zero counts as even). Return its length.</p><p>The empty substring always qualifies, so the answer is never negative. For example, in <code>\"bcbcbc\"</code> there are no vowels at all, so the answer is <code>6</code>; in <code>\"aeiou\"</code> the best substring is empty, so the answer is <code>0</code>; in <code>\"aabeb\"</code> the answer is <code>3</code> (<code>\"aab\"</code>).</p>",
    constraints=["1 &le; s.length &le; 50,000", "s consists of lowercase English letters"],
    hints=["Trying every substring and counting its vowels is O(n&sup2;). Think about prefixes instead of substrings.",
           "Only the parity (odd or even) of each vowel count matters, so the state of a prefix fits in 5 bits.",
           "A substring has all-even counts exactly when the prefix before it and the prefix at its end have the same parity mask. Store the first index at which each of the 32 masks appears, and at every position look up the current mask."],
    editorial=["Let <code>mask(i)</code> be a 5-bit number whose bit v is 1 when the vowel v has appeared an odd number of times in <code>s[0..i)</code>. The substring <code>s[i..j)</code> has all-even vowel counts exactly when <code>mask(i) == mask(j)</code>, because XOR-ing two equal masks gives zero.",
               "So, scanning left to right, we maintain the running mask and a table <code>first[mask]</code> with the earliest prefix length at which each mask was seen (the empty prefix has mask 0 at length 0). At prefix length j with mask m, if m was seen before at length i, the substring has length <code>j - i</code>; otherwise record j. The answer is the maximum. This is O(n) time and O(32) space."],
    time="O(n)", space="O(1)",
    solution='''def longestEvenVowels(s):
    bit = {"a": 1, "e": 2, "i": 4, "o": 8, "u": 16}
    first = {0: 0}
    mask = 0
    best = 0
    for j, ch in enumerate(s, 1):
        mask ^= bit.get(ch, 0)
        if mask in first:
            best = max(best, j - first[mask])
        else:
            first[mask] = j
    return best
''',
    tests=[["bcbcbc"], ["aeiou"], ["aabeb"], ["a"], ["b"], ["aa"], ["leetcodeisgreat"], ["eleetminicoworoep"], ["aeiouaeiou"], ["xaybzaw"],
           ["uuuuuuuu"], ["abababab"]],
)
_r = rnd(8106)
p["tests"].append([_rs(_r, 50000)])
p["tests"].append([_rs(_r, 50000, "bcdfg")])
p["tests"].append(["a" + _rs(_r, 49998, "bcdfghjklmnpqrstvwxyz") + "e"])
p["tests"].append([_rs(_r, 50000, "aeiou")])
p["tests"].append([_rs(_r, 50000, "aeioubcd")])
p["tests"].append(["a" * 49999 + "b"])


def b_vowels(s):
    best = 0
    n = len(s)
    for i in range(n):
        for j in range(i, n + 1):
            sub = s[i:j]
            if all(sub.count(v) % 2 == 0 for v in "aeiou"):
                best = max(best, j - i)
    return best


def g_vowels(r):
    return [_rs(r, r.randint(1, 16), "aeioubc" if r.random() < 0.6 else LET)]


def v_vowels(tests):
    for t in tests:
        s = t["args"][0]
        assert 1 <= len(s) <= 50000 and all("a" <= c <= "z" for c in s)


CHECKS["longest-even-vowel-substring"] = (b_vowels, g_vowels, "exact")
VALIDATE["longest-even-vowel-substring"] = v_vowels

# ---------------------------------------------------------------- HARD

p = add(
    id="minimum-window-subsequence-length", title="Minimum Window Subsequence Length", diff="Hard", topic="Strings",
    fn="minWindowSubsequence", params=[("s", "string"), ("t", "string")], ret="int", cmp="exact",
    desc="<p>Find the shortest contiguous substring (window) of <code>s</code> that contains <code>t</code> as a <em>subsequence</em>, that is, all characters of <code>t</code> appear inside the window in the same order, though not necessarily next to each other. Return the length of that window, or <code>0</code> if no window works.</p><p>For example, for <code>s = \"abcdebdde\"</code> and <code>t = \"bde\"</code> the answer is <code>4</code> (the window <code>\"bcde\"</code>). For <code>s = \"axbxc\"</code> and <code>t = \"abc\"</code> the answer is <code>5</code>, and for <code>s = \"abc\"</code> and <code>t = \"ca\"</code> it is <code>0</code>.</p>",
    constraints=["1 &le; s.length &le; 10,000", "1 &le; t.length &le; 100", "s and t consist of lowercase letters and digits"],
    hints=["Checking every substring of <code>s</code> for the subsequence property is far too slow. First think about the cheaper question: for a fixed end position, where is the best place to start?",
           "For each prefix of <code>t</code> of length j, track the largest start index such that <code>t[0..j)</code> is a subsequence of the window starting there and ending at the current position of <code>s</code>.",
           "When you read <code>s[i]</code> and it equals <code>t[j-1]</code>, the best start for prefix j becomes the best start for prefix j-1 (as it was before this character). Process j in decreasing order so a character is not used twice. Whenever the full <code>t</code> has a start, <code>i - start + 1</code> is a candidate window."],
    editorial=["Let <code>start[j]</code> be the maximum index p such that <code>t[0..j)</code> is a subsequence of <code>s[p..i]</code>, or -1 if none exists. Reading the next character <code>s[i]</code>, for every j with <code>t[j-1] == s[i]</code> we can finish prefix j here, using the best start of prefix j-1 from before: <code>start[j] = start[j-1]</code> (for j = 1 the start is simply i). Updating j from high to low prevents the same character of <code>s</code> from matching two positions of <code>t</code>.",
               "Each time <code>start[m]</code> (m = len(t)) is set, the window <code>[start[m], i]</code> is a candidate and the shortest candidate is the answer. Keeping the latest start is right because a later start only shortens the window. The cost is O(|s| &middot; |t|) in the worst case; indexing, for every character, the positions in t where it occurs lets the loop skip non-matching j. A naive search that tries all starts and greedily matches is O(|s|&sup2;) and too slow at 10,000."],
    time="O(n * m)", space="O(m)",
    solution='''def minWindowSubsequence(s, t):
    m = len(t)
    where = {}
    for j, c in enumerate(t, 1):
        where.setdefault(c, []).append(j)
    for c in where:
        where[c].reverse()  # descending j
    start = [-1] * (m + 1)
    best = 0
    for i, ch in enumerate(s):
        for j in where.get(ch, ()):
            if j == 1:
                start[1] = i
            elif start[j - 1] != -1:
                start[j] = start[j - 1]
            if j == m and start[m] != -1:
                length = i - start[m] + 1
                if best == 0 or length < best:
                    best = length
    return best
''',
    tests=[["abcdebdde", "bde"], ["axbxc", "abc"], ["abc", "ca"], ["a", "a"], ["a", "b"], ["abc", "abc"], ["aaaa", "aa"], ["aaaa", "aaaaa"],
           ["abcabc", "cb"], ["xxaxxbxxcxx", "abc"], ["cnhczmccqouqadqtmjjzl", "mm"], ["fgrqsqsnodwmxzkzxwqegkndaa", "fnok"],
           ["abababab", "bbb"], ["12345123", "513"]],
)
_r = rnd(8107)
p["tests"].append([_rs(_r, 10000, "abc"), "abcabcabcabc"])
p["tests"].append([_rs(_r, 10000), "".join(_r.choice(LET) for _ in range(5))])
p["tests"].append(["a" * 10000, "a" * 100])
p["tests"].append(["a" * 9999 + "b", "a" * 99 + "b"])
p["tests"].append([_rs(_r, 10000, "ab"), "ab" * 50])
p["tests"].append([_rs(_r, 10000, "ab"), "a" * 60 + "b" * 40])
p["tests"].append(["ab" * 5000, "a" * 100])
_t = _rs(_r, 100, "abcd")
_s = ""
for _c in _t:
    _s += _rs(_r, _r.randint(0, 60), "abcd") + _c
p["tests"].append([(_rs(_r, 3000, "abcd") + _s + _rs(_r, 3000, "abcd"))[:10000], _t])


def b_mws(s, t):
    def sub(window):
        it = iter(window)
        return all(c in it for c in t)
    best = 0
    n = len(s)
    for i in range(n):
        for j in range(i + 1, n + 1):
            if (best == 0 or j - i < best) and sub(s[i:j]):
                best = j - i
    return best


def g_mws(r):
    s = _rs(r, r.randint(1, 14), "abc")
    t = _rs(r, r.randint(1, 4), "abc")
    return [s, t]


def v_mws(tests):
    for t in tests:
        s, u = t["args"]
        assert 1 <= len(s) <= 10000 and 1 <= len(u) <= 100 and _is_ld(s) and _is_ld(u)
    assert any(t["expected"] == 0 for t in tests) and any(t["expected"] > 0 for t in tests)


CHECKS["minimum-window-subsequence-length"] = (b_mws, g_mws, "exact")
VALIDATE["minimum-window-subsequence-length"] = v_mws

p = add(
    id="longest-duplicate-substring-length", title="Longest Duplicate Substring Length", diff="Hard", topic="Strings",
    fn="longestDuplicateLength", params=[("s", "string")], ret="int", cmp="exact",
    desc="<p>Find the length of the longest substring of <code>s</code> that occurs at least twice in <code>s</code>. The two occurrences may overlap, but they must start at different positions. If no substring repeats, return <code>0</code>.</p><p>For example, <code>\"banana\"</code> gives <code>3</code> (<code>\"ana\"</code> occurs at positions 1 and 3, overlapping), <code>\"abcd\"</code> gives <code>0</code>, and <code>\"aaaa\"</code> gives <code>3</code>.</p>",
    constraints=["1 &le; s.length &le; 20,000", "s consists of lowercase letters and digits"],
    hints=["Comparing every pair of start positions character by character can take O(n&sup3;) in total. Suppose someone told you a length L: how would you test whether some substring of length L repeats?",
           "If a substring of length L occurs twice, then so does every shorter prefix of it. So the property 'some duplicate of length L exists' is monotonic in L, and you can binary search on L.",
           "To test a single L in linear time, slide a window of length L along the string and keep a rolling hash of the window in a map from hash to start positions. When a hash is seen again, compare the actual substrings to rule out collisions."],
    editorial=["Binary search the answer. If a duplicate of length L exists, cutting one character off both copies gives a duplicate of length L-1, so feasibility is monotonic. The search range is 0 to n-1, taking about 15 steps for n = 20,000.",
               "Each feasibility check slides a window across the string while maintaining a polynomial rolling hash modulo a large prime: when the window moves, remove the contribution of the outgoing character, multiply by the base and add the incoming character. Hash values are stored in a dictionary together with their start indices; on a hash hit, compare the two substrings directly so a collision can never produce a wrong answer. The expected cost of the whole algorithm is O(n log n).",
               "Alternatives are a suffix array with an LCP array (the answer is the maximum LCP value) or a suffix automaton, both of which give deterministic bounds without hashing."],
    time="O(n log n)", space="O(n)",
    solution='''def longestDuplicateLength(s):
    n = len(s)
    MOD = (1 << 61) - 1
    BASE = 911382323
    vals = [ord(c) for c in s]

    def has_dup(L):
        h = 0
        for i in range(L):
            h = (h * BASE + vals[i]) % MOD
        top = pow(BASE, L - 1, MOD)
        seen = {h: [0]}
        for i in range(1, n - L + 1):
            h = ((h - vals[i - 1] * top) * BASE + vals[i + L - 1]) % MOD
            if h in seen:
                sub = s[i:i + L]
                for j in seen[h]:
                    if s[j:j + L] == sub:
                        return True
                seen[h].append(i)
            else:
                seen[h] = [i]
        return False

    lo, hi = 0, n - 1
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if has_dup(mid):
            lo = mid
        else:
            hi = mid - 1
    return lo
''',
    tests=[["banana"], ["abcd"], ["aaaa"], ["a"], ["aa"], ["ab"], ["abab"], ["abcabcabc"], ["zyxzyx"], ["1234512345"], ["mississippi"],
           ["abcdefgabcdefg"], ["aabaab"]],
)
_r = rnd(8108)
p["tests"].append(["a" * 20000])
p["tests"].append(["a" * 10000 + "b" + "a" * 9999])
p["tests"].append([_rs(_r, 20000)])
p["tests"].append([_rs(_r, 20000, "ab")])
p["tests"].append([_rs(_r, 20000, LD)])
_u = _rs(_r, 7000)
p["tests"].append([(_u + _rs(_r, 500) + _u + _rs(_r, 200))[:20000]])
_u = _rs(_r, 9000, "abc")
p["tests"].append([_u + _u[:9000][::-1]])
p["tests"].append(["ab" * 10000])
p["tests"].append([_rs(_r, 20000, "a" * 30 + "b")])


def b_dup(s):
    n = len(s)
    for L in range(n - 1, 0, -1):
        seen = set()
        for i in range(n - L + 1):
            w = s[i:i + L]
            if w in seen:
                return L
            seen.add(w)
    return 0


def g_dup(r):
    return [_rs(r, r.randint(1, 16), "ab" if r.random() < 0.6 else "abcd")]


def v_dup(tests):
    for t in tests:
        s = t["args"][0]
        assert 1 <= len(s) <= 20000 and _is_ld(s)
        assert 0 <= t["expected"] < len(s)
    assert any(t["expected"] == 0 for t in tests) and any(t["expected"] > 0 for t in tests)


CHECKS["longest-duplicate-substring-length"] = (b_dup, g_dup, "exact")
VALIDATE["longest-duplicate-substring-length"] = v_dup
