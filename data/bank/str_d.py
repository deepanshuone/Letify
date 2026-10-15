"""Problems: strings (numbers written as strings). See data/lib.py for the registry."""
from lib import add, rnd, CHECKS, VALIDATE, gen_arr  # noqa: F401

TOPIC = "Strings"
INT_MIN, INT_MAX = -(2 ** 31), 2 ** 31 - 1
MOD = 10 ** 9 + 7


def _digits(r, n, first_nonzero=True):
    """Random decimal digit string of length n (no leading zero unless n == 1)."""
    s = "".join(r.choice("0123456789") for _ in range(n))
    if first_nonzero and n > 0 and s[0] == "0":
        s = r.choice("123456789") + s[1:]
    return s


def _bits(r, n):
    return "1" + "".join(r.choice("01") for _ in range(n - 1))


def _is_dec(s):
    return len(s) >= 1 and all("0" <= c <= "9" for c in s) and (s == "0" or s[0] != "0")


# ---------------------------------------------------------------- EASY

p = add(
    id="add-decimal-number-strings", title="Add Decimal Number Strings", diff="Easy", topic=TOPIC, tier="must",
    fn="addDecimalStrings", params=[("a", "string"), ("b", "string")], ret="string", cmp="exact",
    desc="<p>The strings <code>a</code> and <code>b</code> each hold a non-negative integer written in decimal. Return their sum as a decimal string.</p><p>The numbers can have thousands of digits, so you must add them digit by digit, the way you do on paper, instead of converting the whole strings to integers.</p><p>Example: <code>a = \"456\"</code>, <code>b = \"77\"</code> gives <code>\"533\"</code>. Example: <code>a = \"999\"</code>, <code>b = \"1\"</code> gives <code>\"1000\"</code>.</p>",
    constraints=["1 &le; a.length, b.length &le; 5,000", "a and b contain only the digits 0-9", "Neither string has leading zeros, except for the string \"0\" itself"],
    hints=["Start at the last digit of each string and walk to the left, remembering a carry.",
           "At each position the column total is <code>digitA + digitB + carry</code>. The digit you write is <code>total % 10</code> and the new carry is <code>total // 10</code>. A string that has run out of digits contributes 0.",
           "Keep going while either string still has digits or the carry is non-zero (so <code>999 + 1</code> grows a new leading digit). Collect digits in a list and reverse it once at the end."],
    editorial=["Use two indices starting at the ends of the strings and a carry initialised to 0. Each step adds the current digit of each string (0 when a string is exhausted) plus the carry, appends <code>total % 10</code> to an output list and sets <code>carry = total // 10</code>. The loop stops when both indices have left their strings and the carry is 0. The output list holds the digits from least to most significant, so it is reversed before joining.",
               "The carry is never more than 1 because the largest possible column total is 9 + 9 + 1 = 19. Since neither input has leading zeros, the result has none either. Time is linear in the longer input; appending to a list and reversing once avoids the quadratic cost of prepending to a string."],
    time="O(n + m)", space="O(n + m)",
    solution='''def addDecimalStrings(a, b):
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
        out.append(chr(48 + total % 10))
        carry = total // 10
    out.reverse()
    return "".join(out) if out else "0"
''',
    tests=[["456", "77"], ["999", "1"], ["0", "0"], ["0", "12345"], ["1", "9"], ["99999", "99999"], ["100", "900"],
           ["123456789", "987654321"], ["5", "5"], ["1000000", "1"]],
)
_r = rnd(9401)
p["tests"].append(["9" * 5000, "1"])
p["tests"].append([_digits(_r, 5000), _digits(_r, 5000)])
p["tests"].append([_digits(_r, 4000), _digits(_r, 12)])
p["tests"].append(["1" + "0" * 4999, "9" * 4999])


def b_adddec(a, b):
    return str(int(a) + int(b))


def g_adddec(r):
    return [_digits(r, r.randint(1, 9)) if r.random() < 0.8 else "0", _digits(r, r.randint(1, 9)) if r.random() < 0.8 else "0"]


def v_adddec(tests):
    for t in tests:
        a, b = t["args"]
        assert 1 <= len(a) <= 5000 and 1 <= len(b) <= 5000 and _is_dec(a) and _is_dec(b)
        assert _is_dec(t["expected"])


CHECKS["add-decimal-number-strings"] = (b_adddec, g_adddec, "exact")
VALIDATE["add-decimal-number-strings"] = v_adddec

p = add(
    id="compare-dotted-versions", title="Compare Dotted Version Numbers", diff="Easy", topic=TOPIC,
    fn="compareVersions", params=[("v1", "string"), ("v2", "string")], ret="int", cmp="exact",
    desc="<p>A version string is a list of non-negative integers called <em>revisions</em>, written in decimal and separated by single dots, for example <code>\"1.02.7\"</code>. A revision may have leading zeros, which do not change its value (<code>02</code> is the number 2).</p><p>Compare <code>v1</code> and <code>v2</code> revision by revision from left to right. The first position where the revision values differ decides: return <code>-1</code> if <code>v1</code> is smaller there, <code>1</code> if it is larger. If one version has fewer revisions, the missing ones count as 0. If all revisions are equal, return <code>0</code>.</p><p>Examples: <code>\"1.01\"</code> and <code>\"1.001\"</code> are equal (0); <code>\"1.0\"</code> and <code>\"1.0.0.0\"</code> are equal (0); <code>\"0.9\"</code> versus <code>\"0.10\"</code> gives <code>-1</code> because 9 &lt; 10.</p>",
    constraints=["1 &le; v1.length, v2.length &le; 5,000", "Each version consists of digits and dots; there is at least one digit between two dots and no dot at either end", "Every revision has at most 9 digits"],
    hints=["Comparing the two strings with ordinary string comparison fails: <code>\"9\"</code> is larger than <code>\"10\"</code> as text.",
           "Split each version at the dots and turn every revision into an integer, so leading zeros disappear.",
           "Walk both lists up to the longer length, using 0 when a list has run out. Return at the first difference. You can also do this with two pointers and no split, parsing one revision at a time."],
    editorial=["Parse the revisions one at a time with two pointers. For each version, read digits until the next dot or the end of the string and accumulate the value <code>x = x * 10 + digit</code>; when a version is already exhausted its revision is 0. Compare the two numbers: if they differ, the answer is -1 or 1, otherwise skip the dots and continue. The loop runs until both versions are exhausted.",
               "Padding with zeros is what makes <code>1.0</code> equal to <code>1.0.0</code>. A common bug is to stop at the shorter version and then decide by length, which wrongly calls <code>1.0.1</code> and <code>1.0</code> the same or <code>1.0.0</code> larger than <code>1</code>. Time is linear in the total length and only O(1) extra space is needed with the pointer method."],
    time="O(n + m)", space="O(1)",
    solution='''def compareVersions(v1, v2):
    i = j = 0
    n, m = len(v1), len(v2)
    while i < n or j < m:
        x = 0
        while i < n and v1[i] != ".":
            x = x * 10 + ord(v1[i]) - 48
            i += 1
        y = 0
        while j < m and v2[j] != ".":
            y = y * 10 + ord(v2[j]) - 48
            j += 1
        if x != y:
            return -1 if x < y else 1
        i += 1
        j += 1
    return 0
''',
    tests=[["1.01", "1.001"], ["1.0", "1.0.0.0"], ["0.9", "0.10"], ["1.2.3", "1.2.4"], ["2", "1.9.9"], ["1.0.1", "1"], ["0", "0.0.0"],
           ["007", "7"], ["1.10", "1.9"], ["3.0.0.0.0.2", "3.0.0.0.0.10"], ["999999999.1", "999999999.01"]],
)
p["tests"].append(["1" + ".0" * 2400, "1" + ".0" * 2000])
p["tests"].append(["1" + ".0" * 2400 + ".1", "1" + ".0" * 2400 + ".01"])
p["tests"].append(["2" + ".5" * 2400 + ".7", "2" + ".5" * 2400 + ".8"])
p["tests"].append(["1." + ".".join(["000000007"] * 450), "1." + ".".join(["7"] * 450) + ".0.0"])


def b_ver(v1, v2):
    a = [int(x) for x in v1.split(".")]
    b = [int(x) for x in v2.split(".")]
    k = max(len(a), len(b))
    a += [0] * (k - len(a))
    b += [0] * (k - len(b))
    return (a > b) - (a < b)


def _rv(r):
    return ".".join(("0" * r.randint(0, 2)) + str(r.randint(0, 12)) for _ in range(r.randint(1, 4)))


def g_ver(r):
    a = _rv(r)
    c = r.random()
    if c < 0.3:
        b = a + ".0" * r.randint(0, 3)
    elif c < 0.5:
        b = a + "." + str(r.randint(0, 2))
    else:
        b = _rv(r)
    return [a, b] if r.random() < 0.5 else [b, a]


def v_ver(tests):
    for t in tests:
        for s in t["args"]:
            assert 1 <= len(s) <= 5000
            parts = s.split(".")
            assert all(x.isdigit() and 1 <= len(x) <= 9 for x in parts)
        assert t["expected"] in (-1, 0, 1)


CHECKS["compare-dotted-versions"] = (b_ver, g_ver, "exact")
VALIDATE["compare-dotted-versions"] = v_ver

p = add(
    id="int-to-hexadecimal-twos-complement", title="Integer to Hexadecimal", diff="Easy", topic=TOPIC,
    fn="toHexadecimal", params=[("num", "int")], ret="string", cmp="exact",
    desc="<p>Convert the 32-bit signed integer <code>num</code> to its hexadecimal representation and return it as a string of lowercase digits <code>0-9a-f</code>.</p><ul><li>The result has no leading zeros, except that zero itself is <code>\"0\"</code>.</li><li>A negative number is written with its 32-bit two's complement representation, so <code>-1</code> becomes <code>\"ffffffff\"</code> (eight digits).</li></ul><p>Do not use a built-in conversion such as <code>hex()</code> or a format specifier; extract the digits yourself.</p><p>Examples: <code>26</code> gives <code>\"1a\"</code>, <code>-1</code> gives <code>\"ffffffff\"</code>, <code>-2147483648</code> gives <code>\"80000000\"</code>.</p>",
    constraints=["-2<sup>31</sup> &le; num &le; 2<sup>31</sup> - 1"],
    hints=["One hexadecimal digit stores exactly 4 bits, so you can read the number 4 bits at a time with a mask.",
           "<code>num &amp; 15</code> is the lowest hex digit and <code>num &gt;&gt; 4</code> drops it. Repeat until the number is 0, then reverse the collected digits.",
           "For negative numbers, add 2<sup>32</sup> first (or mask with <code>0xFFFFFFFF</code>). That gives the two's complement bit pattern as a non-negative value, and the same loop works."],
    editorial=["A 32-bit two's complement pattern of a negative number <code>x</code> is the unsigned value <code>x + 2<sup>32</sup></code>. After that mapping the problem is plain base-16 conversion of a non-negative number: repeatedly take the low four bits with <code>&amp; 15</code>, look up the digit character and shift right by four.",
               "Digits come out from least to most significant, so reverse them at the end. Zero needs a special case because the loop would produce no digits. There are at most eight digits, so the work is constant. In languages with fixed-width integers use an unsigned shift (or mask) to avoid sign extension looping forever on negative values."],
    time="O(1)", space="O(1)",
    solution='''def toHexadecimal(num):
    if num == 0:
        return "0"
    if num < 0:
        num += 1 << 32
    digits = "0123456789abcdef"
    out = []
    while num:
        out.append(digits[num & 15])
        num >>= 4
    out.reverse()
    return "".join(out)
''',
    tests=[[26], [-1], [0], [1], [15], [16], [255], [-2], [-16], [INT_MAX], [INT_MIN], [305419896], [-305419896], [4096], [-4096]],
)


def b_hex(num):
    return format(num & 0xFFFFFFFF, "x")


def g_hex(r):
    c = r.random()
    if c < 0.4:
        return [r.randint(-300, 300)]
    return [r.randint(INT_MIN, INT_MAX)]


def v_hex(tests):
    for t in tests:
        assert INT_MIN <= t["args"][0] <= INT_MAX
        e = t["expected"]
        assert e == "0" or e[0] != "0"
        assert all(c in "0123456789abcdef" for c in e)


CHECKS["int-to-hexadecimal-twos-complement"] = (b_hex, g_hex, "exact")
VALIDATE["int-to-hexadecimal-twos-complement"] = v_hex

# ---------------------------------------------------------------- MEDIUM

p = add(
    id="subtract-decimal-strings", title="Subtract Decimal Strings", diff="Medium", topic=TOPIC,
    fn="subtractDecimalStrings", params=[("a", "string"), ("b", "string")], ret="string", cmp="exact",
    desc="<p>The strings <code>a</code> and <code>b</code> each hold a non-negative integer in decimal. Return <code>a - b</code> as a decimal string.</p><ul><li>If the result is negative, the string starts with a single minus sign <code>-</code>.</li><li>The result has no leading zeros, and zero is written as <code>\"0\"</code> (never <code>\"-0\"</code>).</li></ul><p>The numbers can have thousands of digits, so converting them to integers is not an option; work digit by digit.</p><p>Examples: <code>\"1000\"</code> minus <code>\"1\"</code> is <code>\"999\"</code>; <code>\"12\"</code> minus <code>\"100\"</code> is <code>\"-88\"</code>; <code>\"505\"</code> minus <code>\"505\"</code> is <code>\"0\"</code>.</p>",
    constraints=["1 &le; a.length, b.length &le; 5,000", "a and b contain only the digits 0-9", "Neither string has leading zeros, except for the string \"0\" itself"],
    hints=["Subtracting the smaller number from the larger one is easy on paper. What if <code>a</code> is smaller than <code>b</code>?",
           "Compare the numbers first: a longer string is larger (no leading zeros); for equal lengths the usual string comparison decides. If <code>a &lt; b</code>, swap them and remember to put a minus sign in front.",
           "Subtract column by column from the right with a borrow: if <code>digitA - digitB - borrow</code> is negative, add 10 and set borrow to 1. Finally strip leading zeros, keeping at least one digit."],
    editorial=["First decide which number is larger. Because there are no leading zeros, a string with more digits is the bigger number, and for equal lengths lexicographic comparison agrees with numeric comparison. If <code>a</code> is smaller than <code>b</code>, swap them and remember that the answer is negative.",
               "Now the larger number <code>x</code> minus the smaller <code>y</code> is computed from the right: <code>d = x[i] - y[i] - borrow</code>; if <code>d &lt; 0</code>, use <code>d + 10</code> and borrow 1 from the next column, otherwise borrow 0. A shorter <code>y</code> contributes 0 beyond its length. Since <code>x &ge; y</code> no borrow is left at the end. Remove leading zeros (for instance <code>1000 - 999 = 0001</code>), keep one zero if everything cancelled, and add the minus sign only when the result is non-zero. Time and space are linear."],
    time="O(n + m)", space="O(n + m)",
    solution='''def subtractDecimalStrings(a, b):
    neg = False
    if len(a) < len(b) or (len(a) == len(b) and a < b):
        a, b = b, a
        neg = True
    i, j = len(a) - 1, len(b) - 1
    borrow = 0
    out = []
    while i >= 0:
        d = ord(a[i]) - 48 - borrow
        if j >= 0:
            d -= ord(b[j]) - 48
        if d < 0:
            d += 10
            borrow = 1
        else:
            borrow = 0
        out.append(chr(48 + d))
        i -= 1
        j -= 1
    while len(out) > 1 and out[-1] == "0":
        out.pop()
    out.reverse()
    res = "".join(out)
    return "-" + res if neg and res != "0" else res
''',
    tests=[["1000", "1"], ["12", "100"], ["505", "505"], ["0", "0"], ["0", "7"], ["7", "0"], ["100", "99"], ["99", "100"],
           ["123456", "123455"], ["10", "10"], ["1000000", "999999"], ["5", "9"]],
)
_r = rnd(9402)
p["tests"].append(["1" + "0" * 4999, "1"])
_a = _digits(_r, 5000)
p["tests"].append([_a, _a])
p["tests"].append([_digits(_r, 5000), _digits(_r, 4990)])
p["tests"].append([_digits(_r, 3000), _digits(_r, 5000)])
p["tests"].append(["1" + "0" * 4999, "9" * 4999])


def b_subdec(a, b):
    return str(int(a) - int(b))


def g_subdec(r):
    def one():
        return _digits(r, r.randint(1, 6)) if r.random() < 0.9 else "0"
    a = one()
    c = r.random()
    if c < 0.15:
        return [a, a]
    if c < 0.3:
        return [a, str(max(0, int(a) - r.randint(0, 3)))]
    return [a, one()]


def v_subdec(tests):
    for t in tests:
        a, b = t["args"]
        assert 1 <= len(a) <= 5000 and 1 <= len(b) <= 5000 and _is_dec(a) and _is_dec(b)
        e = t["expected"]
        body = e[1:] if e.startswith("-") else e
        assert _is_dec(body) and e != "-0"


CHECKS["subtract-decimal-strings"] = (b_subdec, g_subdec, "exact")
VALIDATE["subtract-decimal-strings"] = v_subdec

p = add(
    id="largest-number-by-concatenation", title="Largest Number by Concatenation", diff="Medium", topic=TOPIC,
    fn="largestNumber", params=[("nums", "int[]")], ret="string", cmp="exact",
    desc="<p>Given an array <code>nums</code> of non-negative integers, arrange them in some order and glue their decimal representations together to form one big number. Return the largest number that can be formed, as a string.</p><p>The result can be far too large for any integer type, hence the string. If the array contains only zeros, return <code>\"0\"</code> (not <code>\"000\"</code>).</p><p>Example: <code>[3, 30, 34, 5, 9]</code> gives <code>\"9534330\"</code>. Example: <code>[10, 2]</code> gives <code>\"210\"</code>.</p>",
    constraints=["1 &le; nums.length &le; 3,000", "0 &le; nums[i] &le; 10<sup>9</sup>"],
    hints=["Sorting the numbers in descending order does not work: <code>[3, 30]</code> must give <code>\"330\"</code>, while <code>\"303\"</code> is smaller.",
           "For two numbers x and y, only two orders exist: <code>x</code> then <code>y</code>, or <code>y</code> then <code>x</code>. Compare the two concatenated strings <code>x+y</code> and <code>y+x</code>.",
           "Sort with the rule \"x comes before y if <code>x+y &gt; y+x</code> as strings\". This rule is transitive, so a sort works. Join the result; if the first character is <code>'0'</code>, the answer is <code>\"0\"</code>."],
    editorial=["Two numbers a and b should appear as <code>ab</code> when the string <code>a+b</code> is larger than <code>b+a</code>. Both concatenations have the same length, so comparing them as text is the same as comparing them as numbers. This defines a total preorder on the numbers (it is transitive), and an exchange argument shows that sorting by it is optimal: if two neighbours were in the wrong order, swapping them would produce a larger number without touching anything else.",
               "Sort the decimal strings with a comparator based on that rule, join them, and handle the all-zero case by returning <code>\"0\"</code> when the first character of the joined string is <code>'0'</code> (the maximum arrangement starts with 0 only if every number is 0). Sorting costs O(n log n) comparisons of strings of length up to 20."],
    time="O(n log n)", space="O(n)",
    solution='''from functools import cmp_to_key


def largestNumber(nums):
    words = [str(x) for x in nums]
    words.sort(key=cmp_to_key(lambda x, y: -1 if x + y > y + x else (1 if x + y < y + x else 0)))
    res = "".join(words)
    return "0" if res[0] == "0" else res
''',
    tests=[[[3, 30, 34, 5, 9]], [[10, 2]], [[0]], [[0, 0, 0]], [[1]], [[20, 1]], [[121, 12]], [[12, 121]], [[432, 43243]],
           [[999999999, 99999999, 9, 1000000000]], [[8308, 8308, 830]], [[0, 0, 5]]],
)
_r = rnd(9403)
p["tests"].append([[_r.randint(0, 10 ** 9) for _ in range(2000)]])
p["tests"].append([[_r.choice([1, 12, 121, 1212, 10, 100, 0, 11, 111]) for _ in range(2000)]])
p["tests"].append([[_r.randint(1, 9) * 10 ** _r.randint(0, 8) for _ in range(2500)]])


def b_large(nums):
    from itertools import permutations
    best = max("".join(map(str, pm)) for pm in permutations(nums))
    return "0" if best[0] == "0" else best


def g_large(r):
    n = r.randint(1, 6)
    pool = r.choice([[0, 1, 2, 3], [1, 10, 11, 12, 121, 21], [0, 5, 50, 505, 55, 9], list(range(0, 120, 7))])
    return [[r.choice(pool) for _ in range(n)]]


def v_large(tests):
    for t in tests:
        nums = t["args"][0]
        assert 1 <= len(nums) <= 3000 and all(0 <= x <= 10 ** 9 for x in nums)
        e = t["expected"]
        assert len(e) == sum(len(str(x)) for x in nums) or e == "0"


CHECKS["largest-number-by-concatenation"] = (b_large, g_large, "exact")
VALIDATE["largest-number-by-concatenation"] = v_large

p = add(
    id="fraction-to-recurring-decimal", title="Fraction to Recurring Decimal", diff="Medium", topic=TOPIC,
    fn="fractionToDecimal", params=[("numerator", "int"), ("denominator", "int")], ret="string", cmp="exact",
    desc="<p>Write the fraction <code>numerator / denominator</code> as a decimal string.</p><ul><li>If the fractional part is empty, return just the integer part (<code>2/1</code> gives <code>\"2\"</code>).</li><li>If the decimal expansion terminates, return it exactly (<code>1/2</code> gives <code>\"0.5\"</code>).</li><li>If it repeats forever, put the shortest repeating block of digits in parentheses, starting from the first digit that begins the repetition (<code>1/3</code> gives <code>\"0.(3)\"</code>, <code>1/6</code> gives <code>\"0.1(6)\"</code>, <code>4/333</code> gives <code>\"0.(012)\"</code>).</li><li>A negative value starts with <code>-</code>; zero is just <code>\"0\"</code>.</li></ul><p>The result of every test is a valid, unique string under these rules.</p>",
    constraints=["-2<sup>31</sup> &le; numerator &le; 2<sup>31</sup> - 1", "denominator &ne; 0 and |denominator| &le; 5,000", "The result has at most about 5,000 fractional digits"],
    hints=["Do long division by hand: the integer part first, then repeatedly multiply the remainder by 10 and divide again to get the next digit.",
           "The expansion ends if a remainder of 0 appears. Otherwise there are fewer than |denominator| different remainders, so some remainder must eventually repeat, and from then on the digits repeat too.",
           "Store, for every remainder you have seen, the position in the digit list where it first occurred. When a remainder shows up again, insert <code>(</code> at its stored position and <code>)</code> at the end. Handle the sign and the zero numerator before dividing, using absolute values."],
    editorial=["Work with absolute values and a sign computed from the two operands (no sign for a zero numerator). The integer part is <code>n // d</code>; if the remainder is 0 you are done. Otherwise generate fractional digits by long division: <code>rem *= 10</code>, the next digit is <code>rem // d</code>, and the new remainder is <code>rem % d</code>.",
               "The next digit and all following ones depend only on the current remainder. So the first time a remainder repeats, the digits between its earlier appearance and now form the repeating block. A dictionary from remainder to digit index gives that index in O(1). The loop ends when the remainder becomes 0 (terminating) or repeats, which takes at most |denominator| steps because there are only that many possible remainders.",
               "Use Python integers or 64-bit types in other languages: <code>-2<sup>31</sup> / -1</code> overflows 32 bits."],
    time="O(|d|)", space="O(|d|)",
    solution='''def fractionToDecimal(numerator, denominator):
    if numerator == 0:
        return "0"
    sign = "-" if (numerator < 0) != (denominator < 0) else ""
    n, d = abs(numerator), abs(denominator)
    q, rem = divmod(n, d)
    head = sign + str(q)
    if rem == 0:
        return head
    digits = []
    seen = {}
    while rem and rem not in seen:
        seen[rem] = len(digits)
        rem *= 10
        digits.append(str(rem // d))
        rem %= d
    if rem == 0:
        return head + "." + "".join(digits)
    i = seen[rem]
    return head + "." + "".join(digits[:i]) + "(" + "".join(digits[i:]) + ")"
''',
    tests=[[1, 2], [2, 1], [1, 3], [1, 6], [4, 333], [0, 5], [-50, 8], [7, -12], [-22, -7], [1, 7], [INT_MIN, -1], [INT_MIN, 7],
           [INT_MAX, 4999], [1, 4999], [1, 4096], [-1, 1250], [100, 99], [5, -4999]],
)


def b_frac(numerator, denominator):
    from fractions import Fraction
    if numerator == 0:
        return "0"
    f = Fraction(abs(numerator), abs(denominator))
    sign = "-" if (numerator < 0) != (denominator < 0) else ""
    ip = f.numerator // f.denominator
    fp = f - ip
    if fp == 0:
        return sign + str(ip)
    den = fp.denominator
    a = b = 0
    while den % 2 == 0:
        den //= 2
        a += 1
    while den % 5 == 0:
        den //= 5
        b += 1
    pre = max(a, b)
    if den == 1:
        k = pre
        txt = str(fp.numerator * 10 ** k // fp.denominator).zfill(k)
        return sign + str(ip) + "." + txt
    per, x = 1, 10 % den
    while x != 1:
        x = x * 10 % den
        per += 1
    k = pre + per
    txt = str(fp.numerator * 10 ** k // fp.denominator).zfill(k)
    return sign + str(ip) + "." + txt[:pre] + "(" + txt[pre:] + ")"


def g_frac(r):
    c = r.random()
    d = r.choice([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 16, 25, 27, 37, 40, 41, 44, 60, 101, 250, 333, 999, 1024]) if c < 0.7 else r.randint(1, 600)
    if r.random() < 0.5:
        d = -d
    n = r.randint(-50, 50) if r.random() < 0.7 else r.randint(INT_MIN, INT_MAX)
    return [n, d]


def v_frac(tests):
    for t in tests:
        n, d = t["args"]
        assert d != 0 and abs(d) <= 5000 and INT_MIN <= n <= INT_MAX
        e = t["expected"]
        assert "." not in e or len(e) <= 5000 + 15
        assert e == b_frac(n, d)


CHECKS["fraction-to-recurring-decimal"] = (b_frac, g_frac, "exact")
VALIDATE["fraction-to-recurring-decimal"] = v_frac

p = add(
    id="steps-to-reduce-binary-string-to-one", title="Steps to Reduce a Binary Number to One", diff="Medium", topic=TOPIC, tier="extra",
    fn="stepsToOne", params=[("s", "string")], ret="int", cmp="exact",
    desc="<p>The string <code>s</code> is the binary representation of a positive integer. Repeat the following until the number equals 1, and return how many steps are needed:</p><ul><li>If the number is even, divide it by 2.</li><li>If the number is odd, add 1 to it.</li></ul><p>The number can have thousands of bits, so you cannot convert it to a machine integer.</p><p>Example: <code>\"1101\"</code> is 13. The sequence is 13, 14, 7, 8, 4, 2, 1, which takes 6 steps. Example: <code>\"10\"</code> takes 1 step; <code>\"1\"</code> takes 0.</p>",
    constraints=["1 &le; s.length &le; 8,000", "s contains only 0 and 1 and starts with 1"],
    hints=["Dividing an even number by 2 removes its last bit (a 0). Adding 1 to an odd number turns trailing ones into zeros and creates a carry.",
           "Process the bits from the right, keeping a carry that says whether a +1 has already been pushed into the current bit.",
           "Look at <code>bit + carry</code>: if it is 1 (the number is odd) you need 2 steps (add 1, then divide) and the carry becomes 1; if it is 0 or 2 (even) you need 1 step (divide), and the carry is 1 only for 2. Do this for every bit except the leading one, then add the final carry."],
    editorial=["Simulating the process on a big integer would be quadratic. Instead, look at the number from its lowest bit. Every bit except the leading one has to be removed by a division, which costs 1 step. An odd value in the lowest position additionally costs an add-one step, and that addition changes the number: it flips the trailing ones to zeros and carries into the next bit.",
               "Track this with a carry. Going from the second-to-last bit down to bit 1 (the leading bit at index 0 stays), compute <code>v = bit + carry</code>. If <code>v == 1</code> the current lowest bit is odd: spend 2 steps and the carry stays 1. If <code>v == 0</code> spend 1 step and the carry is 0. If <code>v == 2</code> the bit is effectively 0 with a carry: spend 1 step and keep carry 1. When only the leading 1 remains, a pending carry means the value is 2, which needs one more step. So the answer is the step count plus the carry. One pass, O(n)."],
    time="O(n)", space="O(1)",
    solution='''def stepsToOne(s):
    steps = 0
    carry = 0
    for i in range(len(s) - 1, 0, -1):
        v = (ord(s[i]) - 48) + carry
        if v == 1:
            steps += 2
            carry = 1
        else:
            steps += 1
            carry = 1 if v == 2 else 0
    return steps + carry
''',
    tests=[["1101"], ["10"], ["1"], ["11"], ["111"], ["1000"], ["1111"], ["101"], ["100000"], ["1011011"], ["110010111"], ["11111111"]],
)
_r = rnd(9404)
p["tests"].append(["1" * 8000])
p["tests"].append(["1" + "0" * 7999])
p["tests"].append([_bits(_r, 8000)])
p["tests"].append([_bits(_r, 5000)])


def b_steps(s):
    x = int(s, 2)
    c = 0
    while x != 1:
        x = x // 2 if x % 2 == 0 else x + 1
        c += 1
    return c


def g_steps(r):
    return [_bits(r, r.randint(1, 20))]


def v_steps(tests):
    for t in tests:
        s = t["args"][0]
        assert 1 <= len(s) <= 8000 and s[0] == "1" and set(s) <= {"0", "1"}


CHECKS["steps-to-reduce-binary-string-to-one"] = (b_steps, g_steps, "exact")
VALIDATE["steps-to-reduce-binary-string-to-one"] = v_steps

p = add(
    id="prefix-divisibility-flags", title="Divisible Prefixes of a Digit String", diff="Medium", topic=TOPIC, tier="extra",
    fn="divisiblePrefixes", params=[("word", "string"), ("m", "int")], ret="int[]", cmp="exact",
    desc="<p>The string <code>word</code> consists of decimal digits (leading zeros are allowed). For every prefix of <code>word</code>, read it as a decimal number. Return an array <code>flags</code> of the same length as <code>word</code> where <code>flags[i]</code> is <code>1</code> if the number formed by <code>word[0..i]</code> is divisible by <code>m</code>, and <code>0</code> otherwise.</p><p>The prefixes can be thousands of digits long, so they cannot be converted to machine integers.</p><p>Example: <code>word = \"9210\"</code>, <code>m = 3</code>: the prefixes are 9, 92, 921, 9210, of which 9, 921 and 9210 are multiples of 3, so the answer is <code>[1, 0, 1, 1]</code>.</p>",
    constraints=["1 &le; word.length &le; 8,000", "word contains only the digits 0-9", "1 &le; m &le; 10<sup>9</sup>"],
    hints=["Testing each prefix from scratch costs O(n) per prefix and the numbers are huge.",
           "Going from prefix <code>P</code> to the next prefix gives the number <code>P * 10 + digit</code>.",
           "You only need the remainder: <code>rem = (rem * 10 + digit) % m</code> is the remainder of the new prefix, because remainders respect addition and multiplication. A prefix is divisible exactly when its remainder is 0."],
    editorial=["Keep <code>rem</code>, the remainder of the current prefix modulo <code>m</code>. Appending a digit transforms the number <code>P</code> into <code>10P + d</code>, and modular arithmetic gives <code>(10P + d) mod m = (10 (P mod m) + d) mod m</code>. So one pass with a single running remainder answers every prefix.",
               "The intermediate value <code>rem * 10 + d</code> is below 10<sup>10</sup>, which exceeds 32 bits, so use 64-bit integers in languages without arbitrary precision. Total time is O(n) and the output has one entry per character. Note that a prefix like <code>\"000\"</code> is the number 0, which is divisible by every m."],
    time="O(n)", space="O(n)",
    solution='''def divisiblePrefixes(word, m):
    rem = 0
    out = []
    for ch in word:
        rem = (rem * 10 + ord(ch) - 48) % m
        out.append(1 if rem == 0 else 0)
    return out
''',
    tests=[["9210", 3], ["1", 1], ["0", 5], ["000", 7], ["10203", 2], ["998244353", 1000000000], ["123456789", 9], ["5555555", 5],
           ["1010101", 11], ["7", 7], ["100", 4], ["8", 3]],
)
_r = rnd(9405)
p["tests"].append(["".join(_r.choice("0123456789") for _ in range(5000)), 3])
p["tests"].append(["".join(_r.choice("0123456789") for _ in range(5000)), 7])
p["tests"].append(["".join(_r.choice("0123456789") for _ in range(5000)), 999999937])
p["tests"].append(["0" * 4000 + "1" * 4000, 11])


def b_divpre(word, m):
    return [1 if int(word[:i + 1]) % m == 0 else 0 for i in range(len(word))]


def g_divpre(r):
    n = r.randint(1, 12)
    return ["".join(r.choice("0123456789") for _ in range(n)), r.choice([1, 2, 3, 4, 5, 6, 7, 9, 11, 13, 25, 97, 1000, r.randint(1, 10 ** 9)])]


def v_divpre(tests):
    for t in tests:
        w, m = t["args"]
        assert 1 <= len(w) <= 8000 and w.isdigit() and 1 <= m <= 10 ** 9
        assert len(t["expected"]) == len(w)


CHECKS["prefix-divisibility-flags"] = (b_divpre, g_divpre, "exact")
VALIDATE["prefix-divisibility-flags"] = v_divpre

# ---------------------------------------------------------------- HARD

p = add(
    id="integer-to-english-words", title="Integer to English Words", diff="Hard", topic=TOPIC,
    fn="numberToWords", params=[("num", "int")], ret="string", cmp="exact",
    desc="<p>Convert the non-negative integer <code>num</code> to its English words. To keep the answer a single token, write every word with a capital first letter and join the words with <strong>no separators</strong> (no spaces, no hyphens, no \"And\").</p><p>Use the words <code>One</code> to <code>Nineteen</code>, <code>Twenty</code>, <code>Thirty</code>, <code>Forty</code>, <code>Fifty</code>, <code>Sixty</code>, <code>Seventy</code>, <code>Eighty</code>, <code>Ninety</code>, and the scale words <code>Hundred</code>, <code>Thousand</code>, <code>Million</code>, <code>Billion</code>. Zero is <code>\"Zero\"</code>. A scale word is written only if its group is non-zero, so 1,000,010 is <code>\"OneMillionTen\"</code>.</p><p>Examples: <code>123</code> gives <code>\"OneHundredTwentyThree\"</code>; <code>12345</code> gives <code>\"TwelveThousandThreeHundredFortyFive\"</code>; <code>1000000</code> gives <code>\"OneMillion\"</code>.</p>",
    constraints=["0 &le; num &le; 2<sup>31</sup> - 1"],
    hints=["Split the number into groups of three digits: billions, millions, thousands and the last three digits. Each group is written like a number below 1000 followed by its scale word.",
           "Write a helper for numbers 1..999: hundreds digit plus <code>Hundred</code>, then the remaining two digits. Numbers below 20 have their own words; for 20..99 use a tens word and then the ones digit.",
           "Skip groups that are zero (otherwise you would print things like <code>ZeroThousand</code>), handle <code>num == 0</code> separately, and concatenate the pieces from the largest group to the smallest."],
    editorial=["Every number below 2<sup>31</sup> has at most four groups of three digits. Process the groups from the largest scale (10<sup>9</sup>) to 1, using <code>q = num // scale</code> and <code>num %= scale</code>. When <code>q</code> is non-zero, append the words for <code>q</code> followed by the scale word.",
               "The words for a group <code>q</code> in 1..999 are built from lookup tables: if <code>q &ge; 100</code> add <code>ones[q // 100] + \"Hundred\"</code> and reduce <code>q %= 100</code>; if <code>q &ge; 20</code> add <code>tens[q // 10]</code> and reduce <code>q %= 10</code>; finally add <code>ones[q]</code> (where <code>ones[0]</code> is the empty string and the table continues through Nineteen). The hard part is not the algorithm but the details: the teens, zero groups in the middle (1,000,010), and the special case 0. Time is constant."],
    time="O(1)", space="O(1)",
    solution='''def numberToWords(num):
    ones = ["", "One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine", "Ten", "Eleven", "Twelve",
            "Thirteen", "Fourteen", "Fifteen", "Sixteen", "Seventeen", "Eighteen", "Nineteen"]
    tens = ["", "", "Twenty", "Thirty", "Forty", "Fifty", "Sixty", "Seventy", "Eighty", "Ninety"]

    def below_thousand(n):
        s = ""
        if n >= 100:
            s += ones[n // 100] + "Hundred"
            n %= 100
        if n >= 20:
            s += tens[n // 10]
            n %= 10
        return s + ones[n]

    if num == 0:
        return "Zero"
    parts = []
    for scale, word in ((10 ** 9, "Billion"), (10 ** 6, "Million"), (1000, "Thousand"), (1, "")):
        q, num = divmod(num, scale)
        if q:
            parts.append(below_thousand(q) + word)
    return "".join(parts)
''',
    tests=[[123], [12345], [1000000], [0], [5], [10], [13], [20], [21], [100], [101], [110], [1000], [1001], [1000010], [100000], [999999999], [1000000000],
           [2147483647], [90090090], [19019019], [700000000]],
)

_ONES = ["", "One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine", "Ten", "Eleven", "Twelve", "Thirteen",
         "Fourteen", "Fifteen", "Sixteen", "Seventeen", "Eighteen", "Nineteen"]
_TENS = {20: "Twenty", 30: "Thirty", 40: "Forty", 50: "Fifty", 60: "Sixty", 70: "Seventy", 80: "Eighty", 90: "Ninety"}


def _words(n):
    """Recursive oracle: peel off the largest matching scale."""
    if n < 20:
        return _ONES[n]
    if n < 100:
        return _TENS[n - n % 10] + _words(n % 10)
    for scale, w in ((10 ** 9, "Billion"), (10 ** 6, "Million"), (1000, "Thousand"), (100, "Hundred")):
        if n >= scale:
            return _words(n // scale) + w + _words(n % scale)


def b_words(num):
    return "Zero" if num == 0 else _words(num)


def g_words(r):
    c = r.random()
    if c < 0.2:
        return [r.randint(0, 120)]
    if c < 0.4:
        return [r.randint(0, 5000)]
    n = r.randint(0, 10 ** r.randint(1, 10))
    if r.random() < 0.3:
        n -= n % r.choice([10, 100, 1000, 10 ** 6])
    return [min(n, INT_MAX)]


def v_words(tests):
    for t in tests:
        assert 0 <= t["args"][0] <= INT_MAX
        e = t["expected"]
        assert e.isalpha() and e[0].isupper() and e == b_words(t["args"][0])


CHECKS["integer-to-english-words"] = (b_words, g_words, "exact")
VALIDATE["integer-to-english-words"] = v_words

p = add(
    id="kth-number-in-lexicographic-order", title="K-th Number in Lexicographic Order", diff="Hard", topic=TOPIC,
    fn="findKthNumber", params=[("n", "int"), ("k", "int")], ret="int", cmp="exact",
    desc="<p>Write the integers <code>1, 2, ..., n</code> as decimal strings and sort them as strings (dictionary order). Return the <code>k</code>-th number of this order, counting from 1.</p><p>For <code>n = 13</code> the order is <code>1, 10, 11, 12, 13, 2, 3, 4, 5, 6, 7, 8, 9</code>, so <code>k = 2</code> gives <code>10</code> and <code>k = 3</code> gives <code>11</code>.</p><p><code>n</code> can be as large as 10<sup>9</sup>, so you cannot list the numbers.</p>",
    constraints=["1 &le; k &le; n &le; 10<sup>9</sup>"],
    hints=["Dictionary order is a walk through a tree: the children of a prefix <code>x</code> are <code>10x</code> ... <code>10x+9</code>, and a prefix comes before its children.",
           "For a prefix <code>cur</code>, count how many valid numbers (at most <code>n</code>) start with it: those lie in the ranges <code>[cur, cur+1)</code>, <code>[10cur, 10cur+10)</code>, <code>[100cur, 100cur+100)</code>, ... clipped at <code>n+1</code>.",
           "Start at <code>cur = 1</code> and with <code>k - 1</code> steps left. If the subtree of <code>cur</code> has at most that many numbers, skip it (move to <code>cur + 1</code>); otherwise go one level down (<code>cur * 10</code>), which uses one step."],
    editorial=["Imagine a 10-ary tree whose root's children are 1..9 and where the children of <code>x</code> are <code>10x .. 10x+9</code> (only values &le; n exist). The dictionary order is exactly the pre-order traversal of this tree. We need the k-th node of the pre-order without visiting all nodes.",
               "Maintain the current node <code>cur</code> (initially 1, the first number) and <code>k -= 1</code> remaining moves. Count the size of the subtree under <code>cur</code> level by level: the level below holds the interval <code>[lo, hi) = [cur, cur+1)</code>, then <code>[10 lo, 10 hi)</code>, and so on while <code>lo &le; n</code>, each clipped to <code>n + 1</code>. If <code>size &le; k</code>, the answer is not in this subtree: subtract the size and go to the next sibling <code>cur + 1</code>. Otherwise it is inside: descend to the first child <code>cur * 10</code> and subtract 1 (the node <code>cur</code> itself). Each descent or skip is O(log n) work, and there are O(log n) levels of descent plus at most 9 skips per level, so O(log<sup>2</sup> n) overall."],
    time="O(log^2 n)", space="O(1)",
    solution='''def findKthNumber(n, k):
    cur = 1
    k -= 1
    while k > 0:
        size = 0
        lo, hi = cur, cur + 1
        while lo <= n:
            size += min(n + 1, hi) - lo
            lo *= 10
            hi *= 10
        if size <= k:
            k -= size
            cur += 1
        else:
            cur *= 10
            k -= 1
    return cur
''',
    tests=[[13, 2], [13, 3], [13, 13], [1, 1], [10, 10], [100, 90], [9, 9], [20, 5], [1000, 1000], [1000000000, 1], [1000000000, 1000000000],
           [1000000000, 123456789], [999999999, 500000000], [12345, 6789], [100000, 99999], [10 ** 9, 10 ** 9 - 7]],
)


def b_kth(n, k):
    return sorted(range(1, n + 1), key=str)[k - 1]


def g_kth(r):
    n = r.choice([r.randint(1, 30), r.randint(1, 300), r.randint(90, 1200), r.choice([9, 10, 11, 99, 100, 101, 999, 1000, 1001])])
    return [n, r.randint(1, n)]


def v_kth(tests):
    for t in tests:
        n, k = t["args"]
        assert 1 <= k <= n <= 10 ** 9
        assert 1 <= t["expected"] <= n


CHECKS["kth-number-in-lexicographic-order"] = (b_kth, g_kth, "exact")
VALIDATE["kth-number-in-lexicographic-order"] = v_kth

p = add(
    id="count-integers-by-digit-sum-in-range", title="Count Integers in a Range by Digit Sum", diff="Hard", topic=TOPIC, tier="extra",
    fn="countByDigitSum", params=[("low", "string"), ("high", "string"), ("minSum", "int"), ("maxSum", "int")], ret="int", cmp="exact",
    desc="<p>The strings <code>low</code> and <code>high</code> are decimal integers with <code>low &le; high</code>. Count the integers <code>x</code> with <code>low &le; x &le; high</code> whose digit sum lies between <code>minSum</code> and <code>maxSum</code> inclusive. The digit sum of <code>x</code> is the sum of its decimal digits.</p><p>The count can be huge, so return it modulo <code>10<sup>9</sup> + 7</code>.</p><p>Example: <code>low = \"1\"</code>, <code>high = \"12\"</code>, <code>minSum = 1</code>, <code>maxSum = 8</code>: the numbers 1 to 8 qualify, as do 10 (sum 1), 11 (sum 2) and 12 (sum 3), while 9 (sum 9) does not. The answer is 11.</p>",
    constraints=["1 &le; low &le; high &le; 10<sup>100</sup> - 1; both strings have at most 100 digits and no leading zeros", "1 &le; minSum &le; maxSum &le; 900"],
    hints=["Counting by looping over the range is impossible with up to 100 digits. Think of a number as a string of digits and count strings instead.",
           "Let <code>F(s, T)</code> be the number of integers in <code>[0, s]</code> with digit sum at most <code>T</code>. Then the count for the range is a combination of <code>F(high, ...)</code> and <code>F(low, ...)</code> with a correction for <code>low</code> itself.",
           "To compute <code>F</code>: precompute <code>ways[len][t]</code>, the number of digit strings of length <code>len</code> (leading zeros allowed) with digit sum at most <code>t</code>. Then scan <code>s</code> from the left: at each position, for every digit smaller than <code>s[i]</code> add <code>ways[remaining][T - prefixSum - digit]</code>, and continue along the digits of <code>s</code> itself."],
    editorial=["This is a digit DP. First tabulate <code>exact[l][t]</code>: the number of length-<code>l</code> digit strings (leading zeros allowed) with digit sum exactly <code>t</code>. It satisfies <code>exact[l][t] = sum of exact[l-1][t-d]</code> over digits d = 0..9, which a prefix sum evaluates in O(1) per cell. Taking prefix sums over <code>t</code> gives <code>ways[l][t]</code>, the number of strings with sum at most t.",
               "Define <code>F(s, T)</code> as the number of integers in <code>[0, s]</code> with digit sum &le; T (0 if T &lt; 0). Walk along <code>s</code>: at position i with prefix digit sum <code>pre</code>, every smaller digit <code>d</code> at this position makes the rest free, contributing <code>ways[n-i-1][T - pre - d]</code> when that index is not negative. Then follow the digit <code>s[i]</code> itself; if <code>pre</code> exceeds T, stop; if the whole string is traversed within the limit, <code>s</code> itself counts +1.",
               "The number of qualifying integers up to <code>s</code> is <code>G(s) = F(s, maxSum) - F(s, minSum - 1)</code>. The answer is <code>G(high) - G(low)</code> plus 1 if <code>low</code> itself qualifies (since <code>G(high) - G(low)</code> excludes it). All arithmetic is modulo 10<sup>9</sup>+7. The table has about 100 &times; 900 cells and each query scans at most 100 &times; 10 states."],
    time="O(L * S + L * 10)", space="O(L * S)",
    solution='''def countByDigitSum(low, high, minSum, maxSum):
    MOD = 10 ** 9 + 7
    L = max(len(low), len(high))
    W = maxSum + 1
    exact = [[0] * W for _ in range(L + 1)]
    exact[0][0] = 1
    for l in range(1, L + 1):
        prev = exact[l - 1]
        pre = [0] * (W + 1)
        for t in range(W):
            pre[t + 1] = pre[t] + prev[t]
        cur = exact[l]
        for t in range(W):
            cur[t] = (pre[t + 1] - pre[max(0, t - 9)]) % MOD
    ways = []
    for l in range(L + 1):
        run = 0
        row = []
        for t in range(W):
            run = (run + exact[l][t]) % MOD
            row.append(run)
        ways.append(row)

    def upto(s, T):
        if T < 0:
            return 0
        n = len(s)
        res = 0
        pre = 0
        for i, ch in enumerate(s):
            d = int(ch)
            rem = n - i - 1
            for dd in range(d):
                t = T - pre - dd
                if t < 0:
                    break
                res += ways[rem][t]
            pre += d
            if pre > T:
                return res % MOD
        return (res + 1) % MOD

    def good(s):
        return (upto(s, maxSum) - upto(s, minSum - 1)) % MOD

    ans = good(high) - good(low)
    if minSum <= sum(int(c) for c in low) <= maxSum:
        ans += 1
    return ans % MOD
''',
    tests=[["1", "12", 1, 8], ["1", "5", 1, 5], ["1", "1", 1, 1], ["10", "10", 1, 1], ["10", "10", 2, 9], ["1", "100", 10, 10], ["1", "1000", 1, 27],
           ["123", "456", 5, 12], ["99", "100", 1, 1], ["1000", "9999", 36, 36]],
)
_r = rnd(9406)
p["tests"].append(["1", "9" * 100, 1, 900])
p["tests"].append(["1", "9" * 100, 450, 450])
_lo, _hi = _digits(_r, 60), _digits(_r, 100)
p["tests"].append([_lo, _hi, 100, 300])
_lo = _digits(_r, 100)
_hi = _lo[:50] + "9" * 50
p["tests"].append([_lo, _hi, 200, 600])
p["tests"].append(["1" + "0" * 98, "1" + "0" * 99, 1, 900])


def b_digsum(low, high, minSum, maxSum):
    c = 0
    for x in range(int(low), int(high) + 1):
        if minSum <= sum(map(int, str(x))) <= maxSum:
            c += 1
    return c % MOD


def g_digsum(r):
    lo = r.randint(1, 3000)
    hi = lo + r.randint(0, 3000)
    a = r.randint(1, 30)
    b = a + r.randint(0, 20)
    return [str(lo), str(hi), a, b]


def v_digsum(tests):
    for t in tests:
        lo, hi, a, b = t["args"]
        assert _is_dec(lo) and _is_dec(hi) and lo != "0" and len(lo) <= 100 and len(hi) <= 100
        assert (len(lo), lo) <= (len(hi), hi)
        assert 1 <= a <= b <= 900
        assert 0 <= t["expected"] < MOD


CHECKS["count-integers-by-digit-sum-in-range"] = (b_digsum, g_digsum, "exact")
VALIDATE["count-integers-by-digit-sum-in-range"] = v_digsum
