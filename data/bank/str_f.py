"""Problems: strings, part F (parsing and validation of formats, numbers and tokens). See data/lib.py for the registry."""
import re

from lib import add, rnd, CHECKS, VALIDATE, gen_arr  # noqa: F401

INT_MIN, INT_MAX = -(2 ** 31), 2 ** 31 - 1
TOPIC = "Strings"
LET = "abcdefghijklmnopqrstuvwxyz"


def _rs(r, n, alpha=LET):
    return "".join(r.choice(alpha) for _ in range(n))


def _both(tests):
    """A validator helper: the tests of a boolean problem should contain both outcomes."""
    outs = {bool(t["expected"]) for t in tests}
    assert outs == {True, False}, "tests should contain both true and false"


# ================================================================ 1. validate-ipv4-address (Easy)

p = add(
    id="validate-ipv4-address", title="Validate IPv4 Address", diff="Easy", topic=TOPIC,
    fn="isValidIPv4", params=[("s", "string")], ret="bool", cmp="exact",
    desc="<p>An IPv4 address in dotted-decimal notation is written as four <em>octets</em> separated by single dots, such as <code>192.168.0.1</code>. Return <code>true</code> if the string <code>s</code> is a valid address, otherwise <code>false</code>.</p><p>The rules are:</p><ul><li>there are exactly four octets, separated by exactly three <code>.</code> characters;</li><li>each octet is a non-empty sequence of the decimal digits <code>0</code>-<code>9</code> only (no signs, no letters);</li><li>an octet has no leading zero unless it is the single digit <code>0</code>;</li><li>the numeric value of each octet is at most 255.</li></ul><p>For example, <code>192.168.0.1</code> and <code>0.0.0.0</code> are valid. <code>256.1.1.1</code> (too large), <code>1.01.1.1</code> (leading zero), <code>1.1.1</code> (three octets) and <code>1.-1.1.1</code> (a sign) are not.</p>",
    constraints=["1 &le; s.length &le; 100", "s contains digits, letters, and the characters <code>. + -</code>; it has no spaces"],
    hints=["Split the string on <code>.</code> and look at the pieces. How many pieces must there be?",
           "Check each piece separately: non-empty, only digits, at most 3 characters, no leading zero unless it is exactly <code>0</code>, then its value.",
           "Be careful with strings like <code>1..1.1</code> or <code>1.1.1.</code> (empty pieces after splitting) and with <code>+1</code> or <code>-0</code> (a sign is not a digit, so do not rely on a library integer parser alone)."],
    editorial=["The format is local to each octet, so split on dots and validate the pieces independently. The split must give exactly four pieces; this also rejects too few or too many dots, and leading, trailing or doubled dots because those create empty pieces.",
               "For a piece, first reject it if it is empty or longer than three characters, then reject any character outside <code>0</code>-<code>9</code>, then reject a leading zero when the length is more than one, and finally compare the numeric value with 255. Checking the characters yourself matters: library parsers such as <code>int()</code> accept a sign and surrounding spaces, which this format forbids.",
               "Every piece is looked at once and has at most three characters, so the work is linear in the length of <code>s</code>."],
    time="O(n)", space="O(n)",
    solution='''def isValidIPv4(s):
    parts = s.split('.')
    if len(parts) != 4:
        return False
    for part in parts:
        if not part or len(part) > 3:
            return False
        for c in part:
            if c < '0' or c > '9':
                return False
        if len(part) > 1 and part[0] == '0':
            return False
        if int(part) > 255:
            return False
    return True
''',
    tests=[["192.168.0.1"], ["0.0.0.0"], ["256.1.1.1"], ["255.255.255.255"], ["1.1.1"], ["1.1.1.1.1"], ["1.01.1.1"],
           ["1..1.1"], ["1.1.1."], [".1.1.1"], ["1.-1.1.1"], ["+1.2.3.4"], ["1.2.3.a"], ["000.1.1.1"], ["1.2.3.04"],
           ["1.2.3.4a"], ["12.34.56.789"], ["1234.1.1.1"], ["0.0.0.00"], ["10.0.0.255"], ["a"], ["...."],
           ["0000000000000000001.1.1.1"]],
)

_IP_RE = re.compile(r"(?:(?:25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\.){3}(?:25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])")


def b_ipv4(s):
    return _IP_RE.fullmatch(s) is not None


def g_ipv4(r):
    good = ["0", "1", "7", "10", "99", "100", "199", "200", "249", "255"]
    bad = ["256", "300", "01", "00", "007", "1000", "", "a", "-1", "+1", "1a", "2555", "25", "260"]
    cnt = 4 if r.random() < 0.8 else r.choice([3, 5, 2])
    parts = [r.choice(good) if r.random() < 0.7 else r.choice(bad) for _ in range(cnt)]
    s = ".".join(parts)
    if r.random() < 0.1:
        s += r.choice([".", "x", "..", "0"])
    return [s or "0"]


def v_ipv4(tests):
    for t in tests:
        s = t["args"][0]
        assert 1 <= len(s) <= 100 and " " not in s
        assert all(c.isalnum() or c in ".+-" for c in s)
        assert t["expected"] == b_ipv4(s)
    _both(tests)


CHECKS["validate-ipv4-address"] = (b_ipv4, g_ipv4, "exact")
VALIDATE["validate-ipv4-address"] = v_ipv4


# ================================================================ 2. validate-roman-numeral-string (Easy)

p = add(
    id="validate-roman-numeral-string", title="Validate Roman Numeral String", diff="Easy", topic=TOPIC,
    fn="isValidRoman", params=[("s", "string")], ret="bool", cmp="exact",
    desc="<p>Roman numerals use the symbols <code>I V X L C D M</code> (1, 5, 10, 50, 100, 500, 1000). A string is a <em>well-formed Roman numeral</em> if it is the standard (canonical) writing of some integer from 1 to 3999. Return <code>true</code> if <code>s</code> is well-formed, otherwise <code>false</code>.</p><p>The canonical writing is built decimal digit by decimal digit, from thousands to units:</p><ul><li>thousands: up to three <code>M</code>;</li><li>for each of the hundreds, tens and units digit, use one of: nothing, one to three of the \"one\" symbol (<code>C</code>, <code>X</code>, <code>I</code>), the \"five\" symbol (<code>D</code>, <code>L</code>, <code>V</code>) optionally followed by one to three \"one\" symbols, or a subtractive pair: \"one\" + \"five\" (<code>CD</code>, <code>XL</code>, <code>IV</code> for 4) or \"one\" + \"ten\" (<code>CM</code>, <code>XC</code>, <code>IX</code> for 9).</li></ul><p>Valid: <code>I</code>, <code>XLII</code>, <code>MCMXCIV</code>, <code>MMMCMXCIX</code>. Invalid: <code>IIII</code> (use <code>IV</code>), <code>VV</code>, <code>IC</code> (99 is <code>XCIX</code>), <code>MMMM</code> (above 3999), <code>CMC</code>, <code>DCCCC</code>, <code>IXI</code>, <code>VX</code>, <code>ABC</code>.</p>",
    constraints=["1 &le; s.length &le; 10,000", "s contains uppercase letters only"],
    hints=["A valid numeral is a thousands part followed by a hundreds part, a tens part and a units part, always in this order. Each part has a small set of allowed shapes.",
           "Parse greedily with an index: first up to three <code>M</code>; then for each of the three remaining digits try the subtractive pair, otherwise an optional five-symbol followed by at most three one-symbols.",
           "The string is valid only if the index reached the end after the last part, so leftovers such as the second <code>C</code> in <code>CMC</code> or the fifth <code>C</code> in <code>DCCCCC</code> are rejected. Do not forget that a string like <code>VV</code> or <code>IIII</code> is rejected because each part can be used only once."],
    editorial=["Think of the numeral as four independent decimal digits written left to right. The thousands digit is 0-3 copies of <code>M</code>. For each other digit with symbols (one, five, ten) = (<code>C</code>, <code>D</code>, <code>M</code>), (<code>X</code>, <code>L</code>, <code>C</code>), (<code>I</code>, <code>V</code>, <code>X</code>), the allowed spellings are: empty, up to three ones, a pair one+five, a pair one+ten, or the five followed by up to three ones. The spellings of one digit are mutually exclusive, so after matching a pair you must not try to match anything more for that digit.",
               "So parse with an index: read up to three <code>M</code>; for each of the three digit groups, if the text at the index starts with one+ten or one+five consume those two characters, otherwise optionally consume the five symbol and then up to three one symbols. After the last group the index has to equal the length of the string. Any leftover character means a repeated symbol, a wrong order or an illegal subtraction.",
               "Equivalently, the language is the regular expression <code>M{0,3}(CM|CD|D?C{0,3})(XC|XL|L?X{0,3})(IX|IV|V?I{0,3})</code> (also non-empty). The parse takes O(n) time and O(1) space."],
    time="O(n)", space="O(1)",
    solution='''def isValidRoman(s):
    n = len(s)
    i = 0
    cnt = 0
    while i < n and s[i] == 'M' and cnt < 3:
        i += 1
        cnt += 1
    for one, five, ten in (('C', 'D', 'M'), ('X', 'L', 'C'), ('I', 'V', 'X')):
        pair = s[i:i + 2]
        if pair == one + ten or pair == one + five:
            i += 2
        else:
            if i < n and s[i] == five:
                i += 1
            cnt = 0
            while i < n and s[i] == one and cnt < 3:
                i += 1
                cnt += 1
    return i == n
''',
    tests=[["I"], ["XLII"], ["MCMXCIV"], ["MMMCMXCIX"], ["IIII"], ["VV"], ["IC"], ["MMMM"], ["CMC"], ["DCCCC"], ["IXI"], ["VX"],
           ["ABC"], ["MMMDCCCLXXXVIII"], ["XC"], ["XCIX"], ["IL"], ["XM"], ["IIV"], ["LL"], ["CCCC"], ["MCMM"], ["IVI"],
           ["XCX"], ["VIV"], ["MDCCCCX"], ["CDXLIV"], ["CMXC"], ["MIM"], ["DM"], ["M"], ["III"], ["IIIV"], ["VIII"], ["VIIII"],
           ["i"], ["MMMCMXCIXI"]],
)
p["tests"].append(["M" * 5000])
p["tests"].append(["MMMDCCCLXXXVIII" * 600])


def _roman(n):
    out = ""
    for d, (one, five, ten) in zip(str(n).zfill(4), (("M", "", ""), ("C", "D", "M"), ("X", "L", "C"), ("I", "V", "X"))):
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


_ROMANS = {_roman(k) for k in range(1, 4000)}


def b_roman(s):
    return s in _ROMANS


def g_roman(r):
    if r.random() < 0.3:
        return ["".join(r.choice("IVXLCDM") for _ in range(r.randint(1, 8)))]
    s = _roman(r.choice([r.randint(1, 3999), r.randint(1, 60), r.randint(1, 400)]))
    m = r.random()
    if m < 0.35:
        return [s]
    k = r.randrange(len(s))
    if m < 0.55:
        s = s[:k] + r.choice("IVXLCDM") + s[k:]
    elif m < 0.75:
        s = s[:k] + r.choice("IVXLCDM") + s[k + 1:]
    elif m < 0.9 and len(s) > 1:
        s = s[:k] + s[k + 1:]
    elif len(s) > 1:
        j = r.randrange(len(s))
        l = list(s)
        l[k], l[j] = l[j], l[k]
        s = "".join(l)
    return [s]


def v_roman(tests):
    for t in tests:
        s = t["args"][0]
        assert 1 <= len(s) <= 10000 and s.isalpha() and s.isascii()
        assert t["expected"] == b_roman(s)
    _both(tests)


CHECKS["validate-roman-numeral-string"] = (b_roman, g_roman, "exact")
VALIDATE["validate-roman-numeral-string"] = v_roman


# ================================================================ 3. matches-numeric-abbreviation (Easy)

p = add(
    id="matches-numeric-abbreviation", title="Matches Numeric Abbreviation", diff="Easy", topic=TOPIC,
    fn="matchesAbbreviation", params=[("word", "string"), ("abbr", "string")], ret="bool", cmp="exact",
    desc="<p>A word can be abbreviated by replacing some of its non-overlapping, non-adjacent substrings by their lengths written in decimal. For example <code>internationalization</code> can be written as <code>i18n</code> (the 18 letters between <code>i</code> and <code>n</code> are replaced by <code>18</code>) or as <code>i12iz4n</code>, which mixes letters and numbers.</p><p>Given a lowercase <code>word</code> and a string <code>abbr</code> made of lowercase letters and digits, decide whether <code>abbr</code> is a valid abbreviation of <code>word</code>. Read <code>abbr</code> from left to right: each lowercase letter must equal the next unread letter of the word, and each maximal run of digits is a number <em>k</em> that skips the next <em>k</em> letters of the word. The whole word has to be consumed exactly.</p><p>A number may not start with the digit <code>0</code>, so it can neither have leading zeros nor be zero itself (<code>0</code>, <code>05</code> are invalid).</p><p>For example, <code>word = \"substitution\"</code> matches <code>\"s10n\"</code> and <code>\"sub4u4\"</code> and <code>\"12\"</code>, but not <code>\"s55n\"</code> (skips too much), <code>\"s010n\"</code> (leading zero) or <code>\"s0ubstitution\"</code> (zero).</p>",
    constraints=["1 &le; word.length &le; 100,000", "1 &le; abbr.length &le; 100,000", "word contains lowercase letters only; abbr contains lowercase letters and digits only", "every run of digits in abbr is at most 8 characters long"],
    hints=["Walk through the word and the abbreviation at the same time with two pointers.",
           "On a letter, compare it with the current letter of the word. On a digit, read the whole run of digits as a number and advance the word pointer by that amount.",
           "Check the special cases: a run starting with <code>0</code> is invalid, jumping beyond the end of the word is invalid, and at the end the word pointer has to be exactly at the end of the word."],
    editorial=["Keep a pointer <code>i</code> into the word and a pointer <code>j</code> into the abbreviation. If <code>abbr[j]</code> is a letter, it must equal <code>word[i]</code> (and <code>i</code> must still be inside the word); then both pointers advance. If it is a digit, first reject it when it is <code>0</code> (a number cannot start with zero, which also excludes the number zero), then read the maximal digit run into the number <code>k</code>, and advance <code>i</code> by <code>k</code>. If <code>i</code> goes past the end, the abbreviation is too long.",
               "After the abbreviation is used up, the match is valid exactly when <code>i</code> equals the length of the word. Each character of <code>abbr</code> is read once, and the digit runs are short, so the time is O(|abbr|) with O(1) extra space. Because each number is capped at 8 digits there is no overflow worry in fixed-width integers either."],
    time="O(n + m)", space="O(1)",
    solution='''def matchesAbbreviation(word, abbr):
    n, m = len(word), len(abbr)
    i = j = 0
    while j < m:
        c = abbr[j]
        if '0' <= c <= '9':
            if c == '0':
                return False
            k = 0
            while j < m and '0' <= abbr[j] <= '9':
                k = k * 10 + ord(abbr[j]) - 48
                j += 1
            i += k
            if i > n:
                return False
        else:
            if i >= n or word[i] != c:
                return False
            i += 1
            j += 1
    return i == n
''',
    tests=[["substitution", "s10n"], ["substitution", "sub4u4"], ["substitution", "12"], ["substitution", "s55n"],
           ["substitution", "s010n"], ["substitution", "s0ubstitution"], ["apple", "a2e"], ["apple", "a2d"],
           ["apple", "5"], ["apple", "6"], ["apple", "4"], ["apple", "apple"], ["apple", "applee"], ["apple", "appl"],
           ["a", "1"], ["a", "01"], ["a", "a"], ["a", "b"], ["hi", "h1"], ["hi", "2h"], ["internationalization", "i18n"],
           ["internationalization", "i12iz4n"], ["abc", "1b1"], ["abc", "10"], ["abc", "a10"]],
)
_r = rnd(8203)
_w = _rs(_r, 6000, "abc")
_ab = []
_i = 0
while _i < 6000:
    if _r.random() < 0.5 or (_ab and _ab[-1].isdigit()):
        _ab.append(_w[_i]); _i += 1
    else:
        _k = min(_r.randint(1, 40), 6000 - _i)
        _ab.append(str(_k)); _i += _k
_abbr = "".join(_ab)
p["tests"].append([_w, _abbr])
p["tests"].append([_w, _abbr[:-1]])
p["tests"].append([_w, "6000"])
p["tests"].append([_w, "5999a"])
p["tests"].append([_w, "99999999"])


def b_abbr(word, abbr):
    pat = ""
    for t in re.findall(r"[a-z]|[0-9]+", abbr):
        if t[0].isdigit():
            if t[0] == "0":
                return False
            pat += ".{%d}" % int(t)
        else:
            pat += t
    return re.fullmatch(pat, word, re.S) is not None


def g_abbr(r):
    w = _rs(r, r.randint(1, 8), "ab")
    out = []
    i = 0
    while i < len(w):
        if r.random() < 0.5:
            out.append(w[i] if r.random() < 0.9 else r.choice("ab"))
            i += 1
        else:
            k = r.randint(1, len(w) - i)
            out.append(str(k + r.choice([0, 0, 0, 0, 1, -1])) if r.random() < 0.85 else "0" + str(k))
            i += k
    if r.random() < 0.15:
        out.append(r.choice(["a", "1", "0"]))
    return [w, "".join(out) or "a"]


def v_abbr(tests):
    for t in tests:
        w, a = t["args"]
        assert 1 <= len(w) <= 100000 and 1 <= len(a) <= 100000
        assert re.fullmatch(r"[a-z]+", w) and re.fullmatch(r"[a-z0-9]+", a)
        assert all(len(x) <= 8 for x in re.findall(r"[0-9]+", a))
        assert t["expected"] == b_abbr(w, a)
    _both(tests)


CHECKS["matches-numeric-abbreviation"] = (b_abbr, g_abbr, "exact")
VALIDATE["matches-numeric-abbreviation"] = v_abbr


# ================================================================ 4. parse-leading-integer-clamped (Medium, must)

p = add(
    id="parse-leading-integer-clamped", title="Parse Leading Integer With Clamping", diff="Medium", topic=TOPIC, tier="must",
    fn="parseInteger", params=[("s", "string")], ret="int", cmp="exact",
    desc="<p>Implement a forgiving integer parser (the classic <em>atoi</em>). Read the string <code>s</code> from the left:</p><ol><li>An optional single sign character, <code>+</code> or <code>-</code>, may come first.</li><li>Then read the longest possible run of decimal digits. Leading zeros are allowed and ignored. Stop at the first character that is not a digit; everything after it is ignored.</li><li>If there is no digit after the optional sign, the result is <code>0</code>.</li><li>Apply the sign. If the value is below <code>-2<sup>31</sup></code> return <code>-2<sup>31</sup></code>; if it is above <code>2<sup>31</sup> - 1</code> return <code>2<sup>31</sup> - 1</code>.</li></ol><p>Examples: <code>\"42\"</code> gives 42, <code>\"-007xyz\"</code> gives -7, <code>\"12.9\"</code> gives 12, <code>\"abc1\"</code> gives 0, <code>\"+-3\"</code> gives 0, <code>\"99999999999\"</code> gives 2147483647 and <code>\"-99999999999\"</code> gives -2147483648.</p><p>Do not rely on a big-integer type: the intended solution should never need a value larger than about <code>2<sup>31</sup></code>.</p>",
    constraints=["1 &le; s.length &le; 10,000", "s contains letters, digits and the characters <code>+ - .</code>; it has no spaces"],
    hints=["First handle the sign: remember whether it is negative and move past it. Only one sign character is allowed.",
           "Accumulate the number with <code>value = value * 10 + digit</code> while you see digits, and stop at the first non-digit.",
           "Detect overflow while accumulating: once the value exceeds the limit (2<sup>31</sup> for the negative side, 2<sup>31</sup> - 1 for the positive side) you can stop reading digits and return the clamped result immediately."],
    editorial=["The parse is a short state machine: optional sign, then digits. Skip the sign (recording whether it is <code>-</code>), then loop over the digits building the value. If there is no digit, the loop never runs and the value stays 0, which is also the required result.",
               "Clamping is where bugs happen. Because the negative limit has a larger magnitude (2<sup>31</sup>) than the positive one (2<sup>31</sup> - 1), compare against the right bound for the sign. A simple way: stop as soon as the magnitude is at least 2<sup>31</sup> and return the clamp for the sign, or cap the magnitude at 2<sup>31</sup> while looping and clamp at the end. Languages with 32-bit integers must check <code>value &gt; (limit - digit) / 10</code> before multiplying.",
               "Each character is read once, so the time is O(n) with O(1) extra space; stopping early on overflow makes long inputs such as thousands of nines cheap."],
    time="O(n)", space="O(1)",
    solution='''def parseInteger(s):
    n = len(s)
    i = 0
    neg = False
    if i < n and (s[i] == '+' or s[i] == '-'):
        neg = s[i] == '-'
        i += 1
    cap = 2 ** 31
    v = 0
    while i < n and '0' <= s[i] <= '9':
        v = v * 10 + ord(s[i]) - 48
        if v >= cap:
            v = cap
            break
        i += 1
    if neg:
        return -v
    return min(v, cap - 1)
''',
    tests=[["42"], ["-007xyz"], ["12.9"], ["abc1"], ["+-3"], ["99999999999"], ["-99999999999"], ["0"], ["-0"], ["+"], ["-"],
           ["2147483647"], ["2147483648"], ["-2147483648"], ["-2147483649"], ["000000000000000000000012"], ["+5-3"],
           ["3-5"], ["--1"], ["4193with9"], [".5"], ["1e5"], ["-a1"], ["00000-1"]],
)
_r = rnd(8204)
p["tests"].append(["0" * 5000 + "123456"])
p["tests"].append(["-" + "9" * 6000])
p["tests"].append(["9" * 3000 + "abc" + "1" * 3000])
p["tests"].append(["-" + "0" * 4000 + "2147483648" + "x" * 100])
p["tests"].append(["+" + "0" * 4000 + "2147483647" + "7"])

_SIGNED = re.compile(r"[+-]?[0-9]+")


def b_atoi(s):
    m = _SIGNED.match(s)
    if not m:
        return 0
    g = m.group()
    sign = -1 if g[0] == "-" else 1
    digits = g.lstrip("+-").lstrip("0") or "0"
    v = 10 ** 12 if len(digits) > 12 else int(digits)
    return max(INT_MIN, min(INT_MAX, sign * v))


def g_atoi(r):
    mode = r.random()
    if mode < 0.35:
        return ["".join(r.choice("+-0123456789ab.") for _ in range(r.randint(1, 8)))]
    sign = r.choice(["", "", "+", "-"])
    digits = r.choice(["0", "7", "42", "2147483647", "2147483648", "2147483649", "99999999999", "00012", "214748364"])
    tail = r.choice(["", "", "x", ".5", "-1", "+2", "9"])
    return [sign + digits + tail]


def v_atoi(tests):
    for t in tests:
        s = t["args"][0]
        assert 1 <= len(s) <= 10000 and " " not in s
        assert all(c.isalnum() or c in "+-." for c in s)
        assert t["expected"] == b_atoi(s)
    assert any(t["expected"] == INT_MAX for t in tests) and any(t["expected"] == INT_MIN for t in tests)
    assert any(t["expected"] == 0 for t in tests)


CHECKS["parse-leading-integer-clamped"] = (b_atoi, g_atoi, "exact")
VALIDATE["parse-leading-integer-clamped"] = v_atoi


# ================================================================ 5. validate-numeric-literal (Hard)

p = add(
    id="validate-numeric-literal", title="Validate Numeric Literal", diff="Hard", topic=TOPIC,
    fn="isNumber", params=[("s", "string")], ret="bool", cmp="exact",
    desc="<p>Decide whether the string <code>s</code> is a valid number literal. A valid literal has a <em>decimal part</em> optionally followed by an <em>exponent</em>, with nothing else around it.</p><ul><li>The decimal part is an optional sign (<code>+</code> or <code>-</code>) followed by one of: digits only (<code>12</code>); digits, a dot and optional digits (<code>12.</code>, <code>12.5</code>); or a dot followed by at least one digit (<code>.5</code>).</li><li>The exponent is the letter <code>e</code> or <code>E</code>, an optional sign, and at least one digit (<code>e10</code>, <code>E-3</code>, <code>e+7</code>). It is allowed only after a decimal part.</li></ul><p>Valid: <code>2</code>, <code>0089</code>, <code>-0.1</code>, <code>+3.14</code>, <code>4.</code>, <code>-.9</code>, <code>2e10</code>, <code>-90E3</code>, <code>3e+7</code>, <code>53.5e93</code>. Invalid: <code>abc</code>, <code>1a</code>, <code>1e</code>, <code>e3</code>, <code>99e2.5</code>, <code>--6</code>, <code>-+3</code>, <code>95a54e53</code>, <code>.</code>, <code>+.</code>, <code>.e1</code>.</p>",
    constraints=["1 &le; s.length &le; 10,000", "s contains letters, digits and the characters <code>+ - .</code>; it has no spaces"],
    hints=["Write the grammar down as a sequence of optional and mandatory parts: sign, integer digits, dot, fraction digits, exponent marker, exponent sign, exponent digits.",
           "Scan left to right with an index. Count how many digits you saw before and after the dot: the decimal part is valid only if at least one of the two counts is positive.",
           "Handle the exponent last: it needs an <code>e</code> or <code>E</code>, an optional sign, and then at least one digit. After a successful scan the index has to be exactly at the end of the string."],
    editorial=["A scanner that follows the grammar directly is the cleanest solution. Skip an optional sign. Count the digits of the integer part. If a dot follows, consume it and count the digits of the fractional part. The decimal part is acceptable only if the two counts add up to more than zero; this accepts <code>4.</code> and <code>.5</code> but rejects a lone <code>.</code>.",
               "Next, if the current character is <code>e</code> or <code>E</code>, consume it, an optional sign, and the exponent digits, requiring at least one digit. If any step fails, return false. The literal is valid when the scan finished exactly at the end of the string, because leftovers such as the extra dot in <code>99e2.5</code> must make it invalid.",
               "The same logic can be written as a finite automaton with states such as <em>start</em>, <em>after sign</em>, <em>integer digits</em>, <em>after dot</em>, <em>fraction digits</em>, <em>after e</em>, <em>exponent sign</em>, <em>exponent digits</em>. The scanner is linear time and constant space."],
    time="O(n)", space="O(1)",
    solution='''def isNumber(s):
    n = len(s)
    i = 0
    if i < n and (s[i] == '+' or s[i] == '-'):
        i += 1
    before = 0
    while i < n and '0' <= s[i] <= '9':
        i += 1
        before += 1
    after = 0
    if i < n and s[i] == '.':
        i += 1
        while i < n and '0' <= s[i] <= '9':
            i += 1
            after += 1
    if before + after == 0:
        return False
    if i < n and (s[i] == 'e' or s[i] == 'E'):
        i += 1
        if i < n and (s[i] == '+' or s[i] == '-'):
            i += 1
        digits = 0
        while i < n and '0' <= s[i] <= '9':
            i += 1
            digits += 1
        if digits == 0:
            return False
    return i == n
''',
    tests=[["2"], ["0089"], ["-0.1"], ["+3.14"], ["4."], ["-.9"], ["2e10"], ["-90E3"], ["3e+7"], ["+6e-1"], ["53.5e93"],
           ["-123.456e789"], ["abc"], ["1a"], ["1e"], ["e3"], ["99e2.5"], ["--6"], ["-+3"], ["95a54e53"], ["."], ["+."],
           [".e1"], ["1.e2"], ["1e+"], ["1e1e1"], ["1..2"], ["0"], ["-"], ["e"], [".1."], ["1.2.3"], ["+.8e-2"], ["6e-1-"]],
)
_r = rnd(8205)
p["tests"].append(["-" + "7" * 4000 + "." + "3" * 4000 + "E+" + "1" * 1500])
p["tests"].append(["." + "0" * 5000 + "e5x"])
p["tests"].append(["9" * 5000 + "." + "e" + "-" + "0" * 3000 + "1"])

_NUM = re.compile(r"[+-]?(?:[0-9]+\.[0-9]*|\.[0-9]+|[0-9]+)(?:[eE][+-]?[0-9]+)?")


def b_num(s):
    return _NUM.fullmatch(s) is not None


def g_num(r):
    parts = [r.choice(["", "", "+", "-"]), r.choice(["", "0", "12", "7", "123"]), r.choice(["", ".", "."]),
             r.choice(["", "", "5", "05", "99"])]
    if r.random() < 0.5:
        parts += [r.choice(["e", "E", "e", "x"]), r.choice(["", "", "+", "-"]), r.choice(["", "1", "20", "3"])]
    s = "".join(parts)
    if r.random() < 0.25:
        k = r.randrange(len(s) + 1)
        s = s[:k] + r.choice("+-.eE5a") + s[k:]
    return [s or "."]


def v_num(tests):
    for t in tests:
        s = t["args"][0]
        assert 1 <= len(s) <= 10000 and " " not in s
        assert all(c.isalnum() or c in "+-." for c in s)
        assert t["expected"] == b_num(s)
    _both(tests)


CHECKS["validate-numeric-literal"] = (b_num, g_num, "exact")
VALIDATE["validate-numeric-literal"] = v_num


# ================================================================ 6. validate-compressed-ipv6 (Medium)

p = add(
    id="validate-compressed-ipv6", title="Validate Compressed IPv6 Address", diff="Medium", topic=TOPIC, tier="extra",
    fn="isValidIPv6", params=[("s", "string")], ret="bool", cmp="exact",
    desc="<p>An IPv6 address is written as eight <em>groups</em> separated by single colons. A group is 1 to 4 hexadecimal digits (<code>0</code>-<code>9</code>, <code>a</code>-<code>f</code>, <code>A</code>-<code>F</code>); leading zeros may be dropped, so <code>0</code> and <code>0db8</code> are both fine.</p><p>To shorten an address, <em>one</em> run of one or more consecutive all-zero groups may be replaced by a double colon <code>::</code>. The double colon may appear at the start, in the middle or at the end, and it can be used at most once.</p><p>Return <code>true</code> if <code>s</code> is a valid IPv6 address in this notation, otherwise <code>false</code>. Embedded IPv4 forms are not considered.</p><p>Valid: <code>2001:db8:85a3:0:0:8a2e:370:7334</code>, <code>2001:db8::1</code>, <code>::</code>, <code>::1</code>, <code>1::</code>, <code>1:2:3:4:5:6:7::</code>. Invalid: <code>1:2:3:4:5:6:7</code> (only seven groups, no <code>::</code>), <code>1::2::3</code> (two double colons), <code>:::</code>, <code>1:2:3:4:5:6:7:8::</code> (eight groups plus <code>::</code> leaves nothing to compress), <code>:1:2:3:4:5:6:7</code> (single leading colon), <code>12345::</code> (group too long), <code>g::</code>.</p>",
    constraints=["1 &le; s.length &le; 100", "s contains letters, digits and colons only"],
    hints=["Without any <code>::</code> the rule is simple: split on <code>:</code>, expect exactly 8 groups, and validate each group.",
           "With a <code>::</code>, split the string around it into a left and a right part, split each part on single colons, and validate those groups. How many explicit groups may remain?",
           "The <code>::</code> must stand for at least one group, so at most 7 explicit groups are allowed. Reject a second <code>::</code> and also <code>:::</code>. A lone colon at the start or end leaves an empty group, which fails group validation automatically."],
    editorial=["Handle the two shapes separately. If the string contains no <code>::</code>, it must split on <code>:</code> into exactly eight groups, each of 1-4 hex digits. If it contains <code>::</code>, it may contain it only once and not as part of <code>:::</code>. Split once around the double colon; the left and right parts are each either empty or a colon-separated list of groups. The compressed run covers at least one group, so the total number of explicit groups must be at most 7.",
               "Empty pieces are the main trap and the reason the split-based approach works so well: a string like <code>1:2::</code> splits into left <code>1:2</code> and an empty right side (no groups), which is fine, while <code>:1::2</code> yields the left group list <code>['', '1']</code> whose empty group is rejected, because a single leading colon is not allowed.",
               "Each character is inspected a constant number of times, so the time is O(n)."],
    time="O(n)", space="O(n)",
    solution='''def isValidIPv6(s):
    hexdigits = "0123456789abcdefABCDEF"

    def good(g):
        if not 1 <= len(g) <= 4:
            return False
        for c in g:
            if c not in hexdigits:
                return False
        return True

    if ':::' in s:
        return False
    if '::' in s:
        if s.count('::') > 1:
            return False
        left, right = s.split('::')
        groups = (left.split(':') if left else []) + (right.split(':') if right else [])
        if len(groups) > 7:
            return False
    else:
        groups = s.split(':')
        if len(groups) != 8:
            return False
    return all(good(g) for g in groups)
''',
    tests=[["2001:db8:85a3:0:0:8a2e:370:7334"], ["2001:db8::1"], ["::"], ["::1"], ["1::"], ["1:2:3:4:5:6:7::"],
           ["1:2:3:4:5:6:7"], ["1::2::3"], [":::"], ["1:2:3:4:5:6:7:8::"], [":1:2:3:4:5:6:7"], ["12345::"], ["g::"],
           ["1:2:3:4:5:6:7:8"], ["1:2:3:4:5:6:7:8:9"], ["1:2:3:4:5:6:7:"], ["::1:2:3:4:5:6:7"], ["::1:2:3:4:5:6:7:8"],
           ["FFFF:ffff:FfFf:0:0:0:0:1"], ["1:::2"], ["1::2:"], [":1::2"], ["1:2:3:4::5:6:7:8"], [":"], ["a"], ["::::"],
           ["fe80::1ff:fe23:4567:890a"], ["1:2:3:4:5:6::7"], ["1:2:3:4:5:6:7:8:"], ["12:34:56:78:9a:bc:de:fG"]],
)

_HEXG = re.compile(r"[0-9a-fA-F]{1,4}")


def b_ipv6(s):
    if "::" in s:
        left, _, right = s.partition("::")
        l = left.split(":") if left else []
        rr = right.split(":") if right else []
        for k in range(1, 9):
            groups = l + ["0"] * k + rr
            if len(groups) == 8 and all(_HEXG.fullmatch(g) for g in groups) and "::" not in right:
                return True
        return False
    groups = s.split(":")
    return len(groups) == 8 and all(_HEXG.fullmatch(g) for g in groups)


def g_ipv6(r):
    pool = ["0", "1", "a", "ff", "FFFF", "12345", "g", "", "1f2", "0db8", "7"]
    n = r.randint(0, 9)
    out = ""
    if r.random() < 0.15:
        out += r.choice([":", "::"])
    for i in range(n):
        out += r.choice(pool)
        if i < n - 1:
            out += r.choice([":", ":", ":", "::", "::"]) if r.random() < 0.9 else ":::"
    if r.random() < 0.15:
        out += r.choice([":", "::"])
    return [out or "::"]


def v_ipv6(tests):
    for t in tests:
        s = t["args"][0]
        assert 1 <= len(s) <= 100 and re.fullmatch(r"[0-9a-zA-Z:]+", s)
        assert t["expected"] == b_ipv6(s)
    _both(tests)


CHECKS["validate-compressed-ipv6"] = (b_ipv6, g_ipv6, "exact")
VALIDATE["validate-compressed-ipv6"] = v_ipv6


# ================================================================ 7. validate-simple-email-address (Medium)

p = add(
    id="validate-simple-email-address", title="Validate Simple Email Address", diff="Medium", topic=TOPIC, tier="extra",
    fn="isValidEmail", params=[("s", "string")], ret="bool", cmp="exact",
    desc="<p>A simplified e-mail address has the form <code>local@domain</code>, with exactly one <code>@</code>. Return <code>true</code> if <code>s</code> follows all of these rules, otherwise <code>false</code>.</p><p><strong>Local part</strong></p><ul><li>1 to 64 characters, each a lowercase letter, a digit, <code>.</code>, <code>_</code> or <code>-</code>;</li><li>it does not start or end with <code>.</code>, and it does not contain two dots in a row.</li></ul><p><strong>Domain</strong></p><ul><li>a list of at least two <em>labels</em> separated by single dots;</li><li>every label has 1 to 63 characters, each a lowercase letter, a digit or <code>-</code>, and does not start or end with <code>-</code>;</li><li>the last label (the top-level domain) consists of lowercase letters only and has at least 2 characters.</li></ul><p>Valid: <code>a@b.co</code>, <code>john.doe_1@mail-server.example.org</code>, <code>-x-@1.io</code>. Invalid: <code>a@b</code> (one label), <code>a..b@c.com</code>, <code>.a@c.com</code>, <code>a@-c.com</code>, <code>a@c.c</code> (top-level domain too short), <code>a@c.c0m</code>, <code>A@c.com</code> (uppercase), <code>a@@c.com</code>.</p>",
    constraints=["1 &le; s.length &le; 500", "s contains letters, digits and the characters <code>@ . _ - +</code>"],
    hints=["Split the string at the <code>@</code> first; if the number of <code>@</code> characters is not exactly one, the answer is false immediately.",
           "Validate the local part with simple character and position checks, then split the domain on dots and validate every label.",
           "Remember the corner cases: empty labels from <code>a@b..com</code> or <code>a@.com</code>, a label of 64 characters, a hyphen at the label edges, a top-level domain that contains digits or hyphens, and a local part of exactly 64 versus 65 characters."],
    editorial=["The rules apply independently to the two halves, so the code splits on <code>@</code> and checks each half. For the local part check the length range, the allowed alphabet, that the first and last characters are not dots, and that <code>..</code> does not occur.",
               "For the domain, split on dots. Fewer than two labels fails. Every label (an empty one from consecutive dots fails the length check) must have 1-63 characters from the label alphabet and must not begin or end with a hyphen. Finally, the last label must be made of letters only and be at least two long. Doing the checks in a fixed order and returning early keeps the code short.",
               "The total work is proportional to the length of the string."],
    time="O(n)", space="O(n)",
    solution='''def isValidEmail(s):
    if s.count('@') != 1:
        return False
    local, domain = s.split('@')
    if not 1 <= len(local) <= 64:
        return False
    if local[0] == '.' or local[-1] == '.' or '..' in local:
        return False
    for c in local:
        if not ('a' <= c <= 'z' or '0' <= c <= '9' or c in '._-'):
            return False
    labels = domain.split('.')
    if len(labels) < 2:
        return False
    for lab in labels:
        if not 1 <= len(lab) <= 63:
            return False
        if lab[0] == '-' or lab[-1] == '-':
            return False
        for c in lab:
            if not ('a' <= c <= 'z' or '0' <= c <= '9' or c == '-'):
                return False
    tld = labels[-1]
    if len(tld) < 2:
        return False
    for c in tld:
        if not 'a' <= c <= 'z':
            return False
    return True
''',
    tests=[["a@b.co"], ["john.doe_1@mail-server.example.org"], ["-x-@1.io"], ["a@b"], ["a..b@c.com"], [".a@c.com"],
           ["a.@c.com"], ["a@-c.com"], ["a@c-.com"], ["a@c.c"], ["a@c.c0m"], ["A@c.com"], ["a@@c.com"], ["a@c.com@d.com"],
           ["@c.com"], ["a@.com"], ["a@c..com"], ["a@c.com."], ["a+b@c.com"], ["a@c_d.com"], ["a@c.co-"], ["a@c.c-m"],
           ["x.y.z@a.b.c.dd"], ["abc"], ["a@1.23"], ["a@1.ab"]],
)
_lab63 = "a" + "b" * 61 + "c"
p["tests"].append(["x" * 64 + "@" + _lab63 + ".com"])
p["tests"].append(["x" * 65 + "@" + _lab63 + ".com"])
p["tests"].append(["x@" + _lab63 + "d.com"])
p["tests"].append(["x@" + _lab63 + "." + _lab63 + "." + _lab63 + ".org"])
p["tests"].append(["x@a." + "z" * 63])
p["tests"].append(["x@a." + "z" * 64])

_EM_LOCAL = re.compile(r"[a-z0-9_-]+(?:\.[a-z0-9_-]+)*")
_EM_DOM = re.compile(r"(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z]{2,63}")


def b_email(s):
    if s.count("@") != 1:
        return False
    local, domain = s.split("@")
    return 1 <= len(local) <= 64 and _EM_LOCAL.fullmatch(local) is not None and _EM_DOM.fullmatch(domain) is not None


def g_email(r):
    loc_pool = ["a", "ab", "a.b", "a..b", ".a", "a.", "a_b-c", "A", "a+b", "x1", "-", "_"]
    lab_pool = ["b", "ab", "a-b", "-a", "a-", "1", "9z", "", "B", "a_b", "com", "co", "c", "c0"]
    local = r.choice(loc_pool)
    k = r.randint(1, 3)
    dom = ".".join(r.choice(lab_pool) for _ in range(k))
    s = local + "@" + dom
    if r.random() < 0.15:
        s = local + r.choice(["", "@@", "@"]) + dom
    if r.random() < 0.2:
        s = s.replace("@", "@" + r.choice(["a.", "", "b."]), 1)
    return [s]


def v_email(tests):
    for t in tests:
        s = t["args"][0]
        assert 1 <= len(s) <= 500 and re.fullmatch(r"[0-9a-zA-Z@._+-]+", s)
        assert t["expected"] == b_email(s)
    _both(tests)


CHECKS["validate-simple-email-address"] = (b_email, g_email, "exact")
VALIDATE["validate-simple-email-address"] = v_email


# ================================================================ 8. balanced-brackets-with-quoted-text (Medium)

p = add(
    id="balanced-brackets-with-quoted-text", title="Balanced Brackets Ignoring Quoted Text", diff="Medium", topic=TOPIC,
    fn="isBalancedCode", params=[("s", "string")], ret="bool", cmp="exact",
    desc="<p>A snippet of source code contains the three kinds of brackets <code>( )</code>, <code>[ ]</code> and <code>{ }</code>, string literals, and other characters. Decide whether the brackets are balanced, but brackets inside string literals do not count.</p><ul><li>A string literal starts at a single quote <code>'</code> or a double quote <code>\"</code> and ends at the next quote of the <em>same</em> kind. Everything in between, including brackets and the other kind of quote, belongs to the literal and is ignored.</li><li>Inside a literal, a backslash <code>\\</code> escapes the next character, whatever it is, so <code>\\'</code> does not end a literal that was opened with <code>'</code>. The escaped character and the backslash are both part of the literal.</li><li>Outside literals the backslash is an ordinary character.</li><li>A literal that is never closed makes the snippet invalid.</li><li>Outside literals, every opening bracket must be closed by a bracket of the same kind in the correct nesting order, and no closing bracket may be left over.</li></ul><p>Return <code>true</code> if the snippet is valid. For example <code>f(a[')'])</code> is valid (the <code>)</code> is inside a literal), <code>\"{\"(</code> is invalid (the <code>(</code> is never closed), <code>'a\\'b'</code> is valid (one literal containing an escaped quote) and <code>'abc</code> is invalid.</p>",
    constraints=["1 &le; s.length &le; 20,000", "s contains letters, digits, the brackets <code>( ) [ ] { }</code>, the quotes <code>'</code> and <code>\"</code>, and the backslash; it has no spaces"],
    hints=["Without literals this is the classic stack of opening brackets. What changes is that sometimes you have to ignore the characters you read.",
           "Scan with an index. When you meet a quote, run an inner loop that skips to the matching closing quote, jumping over two characters whenever you see a backslash.",
           "If the inner loop falls off the end of the string, the literal is unterminated and the answer is false. Otherwise continue after the closing quote; brackets outside literals use the stack as usual, and the stack must be empty at the end."],
    editorial=["This is the standard bracket-matching stack with a tiny tokenizer on top. Scan the string left to right. For an opening bracket push it; for a closing bracket the stack must be non-empty and its top must be the matching opening bracket, which is then popped; any other character is ignored.",
               "The new rule is the literal: when the current character is a quote, remember which one it is and advance until the same quote appears. Inside the literal a backslash consumes itself and the next character (so an escaped quote never terminates it). If the end of the string is reached before the closing quote, return false. After the closing quote, continue with the normal scan.",
               "Each character is processed once and the stack holds at most n brackets, so the solution runs in O(n) time with O(n) space."],
    time="O(n)", space="O(n)",
    solution=r'''def isBalancedCode(s):
    closer = {')': '(', ']': '[', '}': '{'}
    stack = []
    i, n = 0, len(s)
    while i < n:
        c = s[i]
        if c == "'" or c == '"':
            i += 1
            while i < n and s[i] != c:
                if s[i] == '\\':
                    i += 1
                i += 1
            if i >= n:
                return False
            i += 1
        else:
            if c in '([{':
                stack.append(c)
            elif c in closer:
                if not stack or stack.pop() != closer[c]:
                    return False
            i += 1
    return not stack
''',
    tests=[["f(a[')'])"], ["\"{\"("], ["'a\\'b'"], ["'abc"], ["()"], ["([{}])"], ["([)]"], ["(("], ["))"], ["a"],
           ["'('"], ["\"'\"()"], ["'\"'\"'"], ["'\\\\'"], ["'\\\\''"], ["\"\\\"\")"], ["(\"\\\"\"]"], ["\\(\\)"], ["\\'(')"],
           ["{[('x')]}'}'"], ["('}')]"], ["x='\\'';y=\"[\";z=(1)"], ["'\\"], ["\"a'b\"'c\"'"], ["{'a':[1,2],\"b\":{}}"]],
)
_r = rnd(8206)


def _code(r, n):
    """A random valid snippet of roughly n characters with nested brackets and literals."""
    pairs = ["()", "[]", "{}"]
    out = []
    stack = []
    while sum(map(len, out)) < n or stack:
        if sum(map(len, out)) >= n:
            out.append(stack.pop())
            continue
        x = r.random()
        if x < 0.3:
            pr = r.choice(pairs)
            out.append(pr[0])
            stack.append(pr[1])
        elif x < 0.55 and stack:
            out.append(stack.pop())
        elif x < 0.75:
            q = r.choice("'\"")
            body = "".join(r.choice(["a", "(", ")", "[", "{", "\\" + q, "\\\\", "b", "'" if q == '"' else '"']) for _ in range(r.randint(0, 6)))
            out.append(q + body + q)
        else:
            out.append(r.choice("abxy12;,."))
    return "".join(out)


_v = _code(_r, 6000)
p["tests"].append([_v])
p["tests"].append([_v + ")"])
p["tests"].append([_v[:-1]])
p["tests"].append(["(" * 7000 + "')'" + ")" * 7000])
p["tests"].append(["(" * 7000 + "')'" + ")" * 6999])
p["tests"].append(["'" + "\\'" * 4000])
p["tests"].append(["\"" + "\\'" * 4000 + "\""])

_LIT = re.compile(r"'(?:\\.|[^'\\])*'|\"(?:\\.|[^\"\\])*\"", re.S)


def b_code(s):
    t = _LIT.sub("", s)
    if "'" in t or '"' in t:
        return False
    t = "".join(c for c in t if c in "()[]{}")
    while True:
        u = t.replace("()", "").replace("[]", "").replace("{}", "")
        if u == t:
            break
        t = u
    return t == ""


def g_code(r):
    alpha = "()[]{}'\"\\ab"
    if r.random() < 0.5:
        return ["".join(r.choice(alpha) for _ in range(r.randint(1, 10)))]
    s = _code(r, r.randint(1, 12))
    if r.random() < 0.5:
        k = r.randrange(len(s) + 1)
        s = s[:k] + r.choice(alpha) + s[k:]
    return [s or "a"]


def v_code(tests):
    for t in tests:
        s = t["args"][0]
        assert 1 <= len(s) <= 20000 and re.fullmatch(r"[0-9a-zA-Z()\[\]{}'\"\\;,.=:]+", s)
        if len(s) < 3000:
            assert t["expected"] == b_code(s), s
    _both(tests)


CHECKS["balanced-brackets-with-quoted-text"] = (b_code, g_code, "exact")
VALIDATE["balanced-brackets-with-quoted-text"] = v_code


# ================================================================ 9. first-bracket-error-position (Medium)

p = add(
    id="first-bracket-error-position", title="First Bracket Error Position", diff="Medium", topic=TOPIC,
    fn="firstBracketError", params=[("s", "string")], ret="int", cmp="exact",
    desc="<p>A code checker reads a string <code>s</code> that contains the brackets <code>( ) [ ] { }</code> mixed with ordinary characters, which it ignores. It must report <em>where</em> the first problem is, not only whether there is one.</p><p>Scan <code>s</code> from left to right, keeping the opening brackets that are still waiting for their partner. The first problem is the first of the following events:</p><ul><li>a closing bracket arrives and there is no waiting opening bracket, or the most recent waiting one is of a different kind: the problem is that closing bracket;</li><li>the string ends while opening brackets are still waiting: the problem is the <em>earliest</em> opening bracket that is still waiting.</li></ul><p>Return the 1-based position of the problem character in <code>s</code> (ordinary characters count for positions), or <code>0</code> if all brackets are matched.</p><p>Examples: <code>foo(bar);</code> gives 0; <code>{[}</code> gives 3; <code>foo(bar[i);</code> gives 10; <code>((</code> gives 1; <code>(()</code> gives 1; <code>a)b</code> gives 2.</p>",
    constraints=["1 &le; s.length &le; 100,000", "s contains letters, digits, brackets <code>( ) [ ] { }</code> and the characters <code>; , .</code>; it has no spaces"],
    hints=["Use a stack of the opening brackets that are still waiting. What must you store besides the bracket character itself?",
           "Store the position together with each opening bracket. When a closing bracket does not match the top of the stack (or the stack is empty), that closing bracket's position is the answer.",
           "If the scan ends with a non-empty stack, the answer is the position of the bottom element of the stack, i.e. the earliest opening bracket that never got closed. Return 0 only if no problem was found at all."],
    editorial=["Run the standard stack algorithm and enrich each stack entry with its 1-based index. Opening brackets are pushed with their index. For a closing bracket, if the stack is empty or its top is not the matching opening type, the scan stops and that closing bracket's index is returned: an earlier unmatched opener cannot be blamed, because the closing bracket is the first place where the string becomes impossible to repair by looking only at the prefix.",
               "If the whole string is consumed, any bracket still on the stack is unmatched. The question asks for the earliest one, which is the element at the bottom of the stack, because the stack keeps openers in the order they appeared. If the stack is empty, there is no error and the answer is 0.",
               "Each character is pushed and popped at most once, so the time is O(n); the stack uses O(n) space."],
    time="O(n)", space="O(n)",
    solution='''def firstBracketError(s):
    match = {')': '(', ']': '[', '}': '{'}
    stack = []
    for i, c in enumerate(s, 1):
        if c in '([{':
            stack.append((c, i))
        elif c in match:
            if not stack or stack[-1][0] != match[c]:
                return i
            stack.pop()
    return stack[0][1] if stack else 0
''',
    tests=[["foo(bar);"], ["{[}"], ["foo(bar[i);"], ["(("], ["(()"], ["a)b"], ["()"], ["([{}])"], ["}"], ["(]"],
           ["([)]"], ["{{{{"], ["a(b[c]d"], ["x"], ["{[()]}(]"], ["(a)(b)(c)}"], ["[[[[]]]]]"], ["((((()))))("],
           ["a{b(c)d[e]f}g"], ["{(})"], ["]["]],
)
_r = rnd(8207)


def _bal(r, n):
    out = []
    st = []
    pairs = ["()", "[]", "{}"]
    while len(out) < n or st:
        if len(out) >= n:
            out.append(st.pop())
        elif st and r.random() < 0.45:
            out.append(st.pop())
        elif r.random() < 0.6:
            pr = r.choice(pairs)
            out.append(pr[0])
            st.append(pr[1])
        else:
            out.append(r.choice("abcxy12;,."))
    return "".join(out)


_v = _bal(_r, 6000)
p["tests"].append([_v])
_l = list(_v)
_k = len(_l) * 2 // 3
while _l[_k] not in ")]}":
    _k += 1
_l[_k] = {")": "]", "]": "}", "}": ")"}[_l[_k]]
p["tests"].append(["".join(_l)])
p["tests"].append([_v[:-1]])
p["tests"].append(["(" * 20000 + ")" * 19999 + "]"])
p["tests"].append(["x" * 30000 + "[" + "y" * 30000 + "("])


def b_first(s):
    items = [(c, i) for i, c in enumerate(s, 1) if c in "()[]{}"]
    changed = True
    while changed:
        changed = False
        for k in range(len(items) - 1):
            if items[k][0] + items[k + 1][0] in ("()", "[]", "{}"):
                del items[k:k + 2]
                changed = True
                break
    for c, i in items:
        if c in ")]}":
            return i
    return items[0][1] if items else 0


def g_first(r):
    if r.random() < 0.4:
        return ["".join(r.choice("()[]{}a") for _ in range(r.randint(1, 10)))]
    s = _bal(r, r.randint(1, 12))
    if r.random() < 0.7:
        k = r.randrange(len(s) + 1)
        s = s[:k] + r.choice("()[]{}") + s[k:]
    if r.random() < 0.2 and len(s) > 1:
        k = r.randrange(len(s))
        s = s[:k] + s[k + 1:]
    return [s]


def v_first(tests):
    for t in tests:
        s = t["args"][0]
        assert 1 <= len(s) <= 100000 and re.fullmatch(r"[0-9a-zA-Z()\[\]{};,.]+", s)
        if len(s) < 3000:
            assert t["expected"] == b_first(s), s
    ex = [t["expected"] for t in tests]
    assert 0 in ex and any(e > 0 for e in ex)


CHECKS["first-bracket-error-position"] = (b_first, g_first, "exact")
VALIDATE["first-bracket-error-position"] = v_first


# ================================================================ 10. validate-nested-tag-markup (Hard)

p = add(
    id="validate-nested-tag-markup", title="Validate Nested Tag Markup", diff="Hard", topic=TOPIC, tier="extra",
    fn="isValidMarkup", params=[("s", "string")], ret="bool", cmp="exact",
    desc="<p>A tiny markup language has <em>elements</em> of the form <code>&lt;NAME&gt;content&lt;/NAME&gt;</code>. The rules are:</p><ul><li><code>NAME</code> is 1 to 9 uppercase letters, and the closing tag repeats the name of the opening tag exactly.</li><li><code>content</code> may be empty. Otherwise it is a sequence of <em>items</em>, where each item is either a complete element or one plain character. A plain character is any character except <code>&lt;</code> (so <code>&gt;</code>, <code>/</code>, letters and digits are all fine as text).</li><li>A complete document is exactly one element: nothing may come before its opening tag or after its closing tag.</li></ul><p>Return <code>true</code> if <code>s</code> is a valid document. For example <code>&lt;A&gt;&lt;/A&gt;</code>, <code>&lt;DIV&gt;x&lt;B&gt;1&lt;/B&gt;y&lt;/DIV&gt;</code> and <code>&lt;A&gt;a&gt;b/c&lt;/A&gt;</code> are valid. <code>&lt;A&gt;&lt;/B&gt;</code> (names differ), <code>&lt;A&gt;&lt;B&gt;&lt;/A&gt;&lt;/B&gt;</code> (bad nesting), <code>&lt;A&gt;&lt;/A&gt;x</code> (text after the root), <code>&lt;A&gt;&lt;/A&gt;&lt;B&gt;&lt;/B&gt;</code> (two roots), <code>&lt;a&gt;&lt;/a&gt;</code> (lowercase), <code>&lt;&gt;&lt;/&gt;</code> (empty name), <code>&lt;ABCDEFGHIJ&gt;&lt;/ABCDEFGHIJ&gt;</code> (10 letters) and <code>&lt;A&gt;&lt;B&lt;/A&gt;</code> (a stray <code>&lt;</code>) are not.</p>",
    constraints=["1 &le; s.length &le; 50,000", "s contains letters, digits and the characters <code>&lt; &gt; /</code>; it has no spaces"],
    hints=["Opening and closing tags must nest properly, so think of a stack that holds the names of the elements that are currently open.",
           "Whenever you see <code>&lt;</code>, find the next <code>&gt;</code> and look at the text in between: <code>/NAME</code> is a closing tag, <code>NAME</code> is an opening tag. Validate the name (1-9 uppercase letters) before using it.",
           "The whole input must be a single root element: if the stack becomes empty before the end of the string, the document is valid only when that happened exactly at the last character; text or tags outside the root are invalid. Remember to reject a string that ends with elements still open."],
    editorial=["Scan from the left with an index and a stack of open tag names. The string must start with <code>&lt;</code>. At a <code>&lt;</code>, locate the next <code>&gt;</code> (if there is none, return false) and take the text between them. If it starts with <code>/</code> the tag is a closing tag and the name is the rest; otherwise it is an opening tag. A name is valid only if it has 1-9 characters, all uppercase letters; a name that contains a stray <code>&lt;</code>, <code>/</code> or digit fails here. Push a name on an opening tag; on a closing tag the stack must be non-empty and its top must equal the name, which is then popped.",
               "The single-root rule is checked at the moment the stack becomes empty after a pop: the closing tag has to end exactly at the last character, otherwise something follows the root and the document is invalid. Plain characters are allowed only while the stack is non-empty, which together with the requirement that the first character is <code>&lt;</code> excludes text before the root. If the scan ends and the root never closed, return false.",
               "Because the nesting can be tens of thousands of levels deep, use an explicit stack rather than recursion. Every character is read once, so the time is O(n) and the stack may hold O(n) names in total length."],
    time="O(n)", space="O(n)",
    solution='''def isValidMarkup(s):
    n = len(s)
    if s[0] != '<':
        return False
    stack = []
    i = 0
    while i < n:
        if s[i] == '<':
            j = s.find('>', i + 1)
            if j == -1:
                return False
            closing = i + 1 < n and s[i + 1] == '/'
            name = s[i + 2:j] if closing else s[i + 1:j]
            if not 1 <= len(name) <= 9:
                return False
            for c in name:
                if c < 'A' or c > 'Z':
                    return False
            if closing:
                if not stack or stack.pop() != name:
                    return False
                if not stack:
                    return j == n - 1
            else:
                stack.append(name)
            i = j + 1
        else:
            if not stack:
                return False
            i += 1
    return False
''',
    tests=[["<A></A>"], ["<DIV>x<B>1</B>y</DIV>"], ["<A>a>b/c</A>"], ["<A></B>"], ["<A><B></A></B>"], ["<A></A>x"],
           ["<A></A><B></B>"], ["<a></a>"], ["<></>"], ["<ABCDEFGHIJ></ABCDEFGHIJ>"], ["<A><B</A>"], ["<ABCDEFGHI></ABCDEFGHI>"],
           ["x<A></A>"], ["<A>"], ["</A>"], ["<A></A"], ["<A>text"], ["<A/>"], ["<A1></A1>"], ["<A><A><A></A></A></A>"],
           ["<A><B></B><C></C></A>"], ["<A> </A>".replace(" ", "x")], ["<A></AA>"], ["<AB></A>"], ["<A><</A>"], ["<A>>></A>"],
           ["<A></ A>".replace(" ", "")], ["<A><B>x</B>"], ["<A>1<B>2<C>3</C>4</B>5</A>"], ["<A></A></A>"], ["a"], ["<"]],
)
_r = rnd(8208)
p["tests"].append(["<A>" * 2500 + "x" + "</A>" * 2500])
p["tests"].append(["<AB>" * 2500 + "x" + "</AB>" * 2499 + "</A>"])
p["tests"].append(["<R>" + "<B>x</B>" * 3000 + "</R>"])
p["tests"].append(["<R>" + "<B>x</B>" * 3000 + "</R>y"])


def _mk(r, depth, budget):
    name = "".join(r.choice("ABC") for _ in range(r.randint(1, 3)))
    body = []
    for _ in range(r.randint(0, 3)):
        if depth > 0 and r.random() < 0.5 and budget[0] > 0:
            budget[0] -= 1
            body.append(_mk(r, depth - 1, budget))
        else:
            body.append("".join(r.choice(["x", "1", ">", "/", "ab"]) for _ in range(r.randint(1, 2))))
    return "<" + name + ">" + "".join(body) + "</" + name + ">"


def _elem(s, i):
    """Recursive-descent parse of one element starting at i; returns the end index or -1."""
    n = len(s)
    if i >= n or s[i] != "<":
        return -1
    j = i + 1
    while j < n and "A" <= s[j] <= "Z":
        j += 1
    name = s[i + 1:j]
    if not 1 <= len(name) <= 9 or j >= n or s[j] != ">":
        return -1
    k = j + 1
    while True:
        if k >= n:
            return -1
        if s.startswith("</", k):
            break
        if s[k] == "<":
            k = _elem(s, k)
            if k < 0:
                return -1
        else:
            k += 1
    close = "</" + name + ">"
    if not s.startswith(close, k):
        return -1
    return k + len(close)


def b_markup(s):
    return _elem(s, 0) == len(s)


def g_markup(r):
    s = _mk(r, 3, [4])
    if r.random() < 0.6:
        k = r.randrange(len(s) + 1)
        m = r.random()
        if m < 0.4:
            s = s[:k] + r.choice("<>/ABa1") + s[k + 1:]
        elif m < 0.7:
            s = s[:k] + r.choice("<>/ABa1") + s[k:]
        else:
            s = s[:k] + s[k + 1:]
    return [s or "<"]


def v_markup(tests):
    for t in tests:
        s = t["args"][0]
        assert 1 <= len(s) <= 50000 and re.fullmatch(r"[0-9a-zA-Z<>/]+", s)
        if len(s) < 3000:
            assert t["expected"] == b_markup(s), s
    _both(tests)


CHECKS["validate-nested-tag-markup"] = (b_markup, g_markup, "exact")
VALIDATE["validate-nested-tag-markup"] = v_markup


# ================================================================ 11. glob-match-with-character-classes (Hard)

p = add(
    id="glob-match-with-character-classes", title="Glob Match With Character Classes", diff="Hard", topic=TOPIC, tier="extra",
    fn="globMatch", params=[("s", "string"), ("pattern", "string")], ret="bool", cmp="exact",
    desc="<p>Implement file-name style globbing. The pattern <code>pattern</code> is made of the following elements, and the pattern has to match the <em>entire</em> string <code>s</code>:</p><ul><li>a lowercase letter or digit matches exactly itself;</li><li><code>?</code> matches any single character;</li><li><code>*</code> matches any sequence of characters, including the empty one;</li><li>a <em>class</em> <code>[...]</code> matches one character from a set. Inside the brackets there is a list of members, each either a single character (a lowercase letter or digit) or a range <code>x-y</code> meaning every character from <code>x</code> to <code>y</code> inclusive (<code>x &le; y</code>, both of the same kind: letters with letters or digits with digits). If the very first character after <code>[</code> is <code>^</code>, the class is negated: it matches any single character that is <em>not</em> in the set.</li></ul><p>Classes are never empty and never nested; <code>-</code> appears only as a range operator between two members, and <code>]</code> only as the end of a class. The pattern is always well formed.</p><p>Examples: <code>s = \"hello3\"</code> matches <code>h[a-f]llo?</code> and <code>*[0-9]</code> and <code>[^xyz]*</code>, but does not match <code>h[^e]llo3</code> or <code>hello</code>.</p>",
    constraints=["1 &le; s.length &le; 1,000, lowercase letters and digits only", "1 &le; pattern.length &le; 500, made of lowercase letters, digits and the characters <code>? * [ ] ^ -</code>", "The pattern is well formed as described"],
    hints=["Compare with the plain wildcard problem (<code>?</code> and <code>*</code>): the new part is only that one pattern element can now match a set of characters. First turn the pattern into a list of elements, where a class is one element.",
           "Write a helper <code>matches(element, ch)</code> for single-character elements (a literal, <code>?</code>, or a class). Then use the standard two-pointer wildcard scan or a DP over (string position, element index).",
           "For the two-pointer scan remember the last <code>*</code> and the string position where it started matching. On a mismatch, jump back to the star, let it absorb one more character and retry. At the end only stars may remain in the pattern."],
    editorial=["First tokenize the pattern into a list of elements: a star, a question mark, a literal, or a class holding its negation flag and its list of ranges (a single member is a range of length one). Parsing a class is a short loop: after an optional <code>^</code>, read members until <code>]</code>, treating <code>x-y</code> as a range when the next character is a dash.",
               "Matching one character against an element is then trivial: a literal compares equal, <code>?</code> always succeeds, and a class succeeds when the character is in one of the ranges, flipped by the negation flag. With that helper, the classic greedy wildcard algorithm applies. Walk through the string; if the current element is a star, remember its index and the current string position, and skip the star; if the element matches the current character, advance both; otherwise, if a star was seen, backtrack to it, advance the remembered string position by one and resume right after the star; otherwise fail. Once the string is consumed, skip trailing stars and succeed only if the whole pattern was used.",
               "Only the most recent star ever needs to be retried, which is why the greedy method is correct. The worst case is O(n * m) for string length n and pattern length m, about 500,000 steps for the largest inputs here. A dynamic programming table over (position, element) gives the same bound with O(n * m) memory."],
    time="O(n * m)", space="O(m)",
    solution='''def globMatch(s, pattern):
    toks = []
    i, m = 0, len(pattern)
    while i < m:
        c = pattern[i]
        if c == '*':
            toks.append(('*', None))
            i += 1
        elif c == '?':
            toks.append(('?', None))
            i += 1
        elif c == '[':
            i += 1
            neg = False
            if pattern[i] == '^':
                neg = True
                i += 1
            ranges = []
            while pattern[i] != ']':
                if pattern[i + 1] == '-':
                    ranges.append((pattern[i], pattern[i + 2]))
                    i += 3
                else:
                    ranges.append((pattern[i], pattern[i]))
                    i += 1
            i += 1
            toks.append(('[', (neg, ranges)))
        else:
            toks.append(('c', c))
            i += 1

    def hit(t, ch):
        kind, data = t
        if kind == '?':
            return True
        if kind == 'c':
            return data == ch
        neg, ranges = data
        inside = False
        for lo, hi in ranges:
            if lo <= ch <= hi:
                inside = True
                break
        return inside != neg

    n, k = len(s), len(toks)
    i = j = 0
    star = -1
    mark = 0
    while i < n:
        if j < k and toks[j][0] == '*':
            star = j
            mark = i
            j += 1
        elif j < k and hit(toks[j], s[i]):
            i += 1
            j += 1
        elif star != -1:
            mark += 1
            i = mark
            j = star + 1
        else:
            return False
    while j < k and toks[j][0] == '*':
        j += 1
    return j == k
''',
    tests=[["hello3", "h[a-f]llo?"], ["hello3", "*[0-9]"], ["hello3", "[^xyz]*"], ["hello3", "h[^e]llo3"], ["hello3", "hello"],
           ["abc", "abc"], ["abc", "a?c"], ["abc", "*"], ["abc", "[a-c][a-c][a-c]"], ["abc", "[^a]bc"], ["abc", "[^d]*"],
           ["a", "[^a]"], ["a", "[a]"], ["a", "?*?"], ["ab", "?*?"], ["ab12", "[a-b]*[0-9]?"], ["ab12", "[a-b]*[0-9]"],
           ["ab12", "*[1-2]*[1-2]"], ["ab12", "*[1-2]*[1-2]*[1-2]"], ["z9", "[a-y0-8]*"], ["z9", "[xyz]9"], ["z9", "[x-z][0-9]"],
           ["abcabc", "*abc"], ["abcabc", "abc*abc"], ["abcab", "*abc"], ["aaaa", "a*a*a*a"], ["aaa", "a*a*a*a"],
           ["a0b1", "[a-z][0-9][a-z][0-9]"], ["a0b1", "[a-z0-9]*[^0-9]"], ["x", "[^a-w]"], ["x", "[^a-x]"]],
)
_r = rnd(8209)
_s = "".join(_r.choice("ab") for _ in range(1000))
p["tests"].append([_s, "*a*b*a*b*a*b*a*b*a*b*a*b*a*b*a*b*"])
p["tests"].append(["a" * 1000, "*a" * 100 + "b"])
p["tests"].append(["a" * 999 + "b", "*a" * 150 + "*b"])
p["tests"].append(["a" * 1000, "[a-c]" * 99 + "*"])
p["tests"].append(["a" * 1000, "[^b]" * 100 + "*a"])
p["tests"].append(["ab" * 500, "*[a-b]*" * 60 + "[^a]"])
p["tests"].append(["".join(_r.choice("abc123") for _ in range(900)), "*[1-3]?[^b]*c[a-b]*"])


def b_glob(s, pattern):
    return re.fullmatch(pattern.replace("*", ".*").replace("?", "."), s, re.S) is not None


def _gpat(r):
    toks = ["a", "b", "1", "?", "*", "[ab]", "[^a]", "[a-b]", "[0-9]", "[a-c1]", "[^b-c]", "[^1]", "c", "*", "?"]
    return [r.choice(toks) for _ in range(r.randint(1, 6))]


def _ginst(r, ptoks):
    out = []
    for t in ptoks:
        if t == "*":
            out.append("".join(r.choice("abc1") for _ in range(r.randint(0, 3))))
        elif t == "?":
            out.append(r.choice("abc1"))
        elif t.startswith("[^"):
            ok = [c for c in "abc1" if not re.fullmatch(t, c)]
            out.append(r.choice(ok or ["a"]))
        elif t.startswith("["):
            ok = [c for c in "abc1" if re.fullmatch(t, c)]
            out.append(r.choice(ok or ["a"]))
        else:
            out.append(t)
    return "".join(out)


def g_glob(r):
    pt = _gpat(r)
    s = _ginst(r, pt) if r.random() < 0.65 else "".join(r.choice("abc1") for _ in range(r.randint(1, 6)))
    if r.random() < 0.3 and s:
        k = r.randrange(len(s))
        s = s[:k] + r.choice("abc1") + s[k + 1:]
    return [s or "a", "".join(pt)]


def v_glob(tests):
    for t in tests:
        s, pat = t["args"]
        assert 1 <= len(s) <= 1000 and re.fullmatch(r"[a-z0-9]+", s)
        assert 1 <= len(pat) <= 500 and re.fullmatch(r"[a-z0-9?*\[\]^-]+", pat)
        assert re.fullmatch(r"(?:[a-z0-9?*]|\[\^?(?:[a-z0-9]-[a-z0-9]|[a-z0-9])+\])+", pat), pat
        for lo, hi in re.findall(r"([a-z0-9])-([a-z0-9])", pat):
            assert lo <= hi and lo.isdigit() == hi.isdigit()
        if len(pat) < 120 or pat.count("*") <= 3:
            assert t["expected"] == b_glob(s, pat), (s, pat)
    _both(tests)


CHECKS["glob-match-with-character-classes"] = (b_glob, g_glob, "exact")
VALIDATE["glob-match-with-character-classes"] = v_glob
