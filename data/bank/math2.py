"""Problems: math, digits and number theory. See data/lib.py for the registry."""
import math

from lib import add, rnd, CHECKS, VALIDATE, gen_arr  # noqa: F401

INT_MIN, INT_MAX = -(2 ** 31), 2 ** 31 - 1


def _is_prime(x):
    if x < 2:
        return False
    i = 2
    while i * i <= x:
        if x % i == 0:
            return False
        i += 1
    return True


# ---------------------------------------------------------------- EASY

p = add(
    id="palindrome-integer-check", title="Palindrome Integer", diff="Easy", topic="Math & Bit Manipulation",
    fn="isPalindromeInteger", params=[("x", "int")], ret="bool", cmp="exact",
    desc="<p>Given an integer <code>x</code>, return <code>true</code> if its decimal digits read the same from left to right as from right to left, and <code>false</code> otherwise.</p><p>A negative number is never a palindrome, because its leading minus sign has no counterpart at the other end. Try to solve it without converting the integer to a string.</p><pre>x = 12321   -> true\nx = 1210    -> false\nx = -121    -> false</pre>",
    constraints=["-2<sup>31</sup> &le; x &le; 2<sup>31</sup> - 1"],
    hints=["Converting to a string and comparing it with its reverse works. Can you do the same using only arithmetic?",
           "Negative numbers and numbers that end in 0 (other than 0 itself) can be rejected immediately.",
           "Build the reverse of the number digit by digit using <code>% 10</code> and <code>// 10</code>, but stop once the reversed half is at least as large as what remains. Then compare the two halves."],
    editorial=["Reject negatives at once. A number ending in 0 can only be a palindrome if it is 0 itself, since a palindrome cannot start with 0.",
               "Peel digits off the right end of <code>x</code> and push them onto a number <code>rev</code>. Stop when <code>rev &ge; x</code>: by then <code>rev</code> holds the reversed second half. For an even digit count the halves must be equal; for an odd digit count the middle digit sits at the end of <code>rev</code>, so compare with <code>rev // 10</code>.",
               "Reversing only half of the digits also avoids any chance of overflowing a 32-bit integer, which a full reversal could do for values near 2<sup>31</sup>."],
    time="O(log x)", space="O(1)",
    solution='''def isPalindromeInteger(x):
    if x < 0 or (x % 10 == 0 and x != 0):
        return False
    rev = 0
    while x > rev:
        rev = rev * 10 + x % 10
        x //= 10
    return x == rev or x == rev // 10
''',
    tests=[[121], [-121], [10], [0], [7], [11], [12321], [1221], [1210], [100], [-1], [1000021],
           [INT_MAX], [INT_MIN], [2147447412], [1000000001], [1234567899]],
)


def b_pal_int(x):
    s = str(x)
    return s == s[::-1]


def g_pal_int(r):
    c = r.random()
    if c < 0.5:
        h = str(r.randint(0, 9999))
        full = h + h[::-1] if r.random() < 0.5 else h + h[-2::-1]
        v = int(full)
    elif c < 0.7:
        v = r.randint(-500, 500)
    else:
        v = r.randint(0, 100000)
    return [v]


def v_pal_int(tests):
    for t in tests:
        assert INT_MIN <= t["args"][0] <= INT_MAX
    assert any(t["expected"] for t in tests) and any(not t["expected"] for t in tests)


CHECKS["palindrome-integer-check"] = (b_pal_int, lambda r: g_pal_int(r), "exact")
VALIDATE["palindrome-integer-check"] = v_pal_int

p = add(
    id="excel-column-title-to-number", title="Spreadsheet Column Number", diff="Easy", topic="Math & Bit Manipulation",
    fn="columnNumber", params=[("title", "string")], ret="int", cmp="exact",
    desc="<p>Spreadsheet columns are labelled <code>A, B, ..., Z, AA, AB, ..., AZ, BA, ..., ZZ, AAA, ...</code> Given the label <code>title</code> of a column, return its 1-based position.</p><pre>\"A\"  -> 1\n\"Z\"  -> 26\n\"AA\" -> 27\n\"AZ\" -> 52\n\"ZY\" -> 701</pre>",
    constraints=["1 &le; title.length &le; 7", "title consists of uppercase English letters only", "The column number is at most 2<sup>31</sup> - 1 (the largest valid title is \"FXSHRXW\")"],
    hints=["Look at \"AB\": it is like a two-digit number, but the digits are letters.",
           "This is a base-26 number system where the digits run from 1 (<code>A</code>) to 26 (<code>Z</code>) instead of 0 to 25.",
           "Scan left to right keeping <code>result</code>; for each letter do <code>result = result * 26 + (letter - 'A' + 1)</code>."],
    editorial=["Treat the label as a number in base 26 whose digits are <code>A=1, ..., Z=26</code>. There is no zero digit, which is why the system is called bijective base 26. Reading from the most significant letter, the usual positional rule applies: multiply what you have by 26 and add the value of the next letter.",
               "For example <code>\"ZY\" = 26 * 26 + 25 = 701</code>. The loop touches each letter once, so the work is proportional to the label length, and the result stays within 32 bits by the constraint."],
    time="O(L)", space="O(1)",
    solution='''def columnNumber(title):
    result = 0
    for ch in title:
        result = result * 26 + (ord(ch) - 64)
    return result
''',
    tests=[["A"], ["B"], ["Z"], ["AA"], ["AB"], ["AZ"], ["BA"], ["ZY"], ["ZZ"], ["AAA"], ["ABC"], ["FXSHRXW"],
           ["FXSHRXV"], ["XFD"], ["AAAAAAA"], ["MNOPQR"], ["CAFEBA"]],
)


def b_excel(title):
    L = len(title)
    if L <= 3:
        # walk the label sequence A, B, ..., Z, AA, ... one step at a time until we reach the title
        cur = "A"
        n = 1
        while cur != title:
            chars = list(cur)
            i = len(chars) - 1
            while i >= 0 and chars[i] == "Z":
                chars[i] = "A"
                i -= 1
            if i < 0:
                chars = ["A"] + chars
            else:
                chars[i] = chr(ord(chars[i]) + 1)
            cur = "".join(chars)
            n += 1
        return n
    # longer labels: count every shorter label, then add the rank among labels of the same length
    shorter = sum(26 ** k for k in range(1, L))
    rank = 0
    for ch in title:
        rank = rank * 26 + (ord(ch) - ord("A"))
    return shorter + rank + 1


def g_excel(r):
    return ["".join(r.choice("ABCDXYZ") for _ in range(r.randint(1, 3)))]


def v_excel(tests):
    for t in tests:
        s = t["args"][0]
        assert 1 <= len(s) <= 7 and s.isalpha() and s.isupper()
        assert 1 <= t["expected"] <= INT_MAX


CHECKS["excel-column-title-to-number"] = (b_excel, g_excel, "exact")
VALIDATE["excel-column-title-to-number"] = v_excel

p = add(
    id="factorial-trailing-zeros-count", title="Trailing Zeros of a Factorial", diff="Easy", topic="Math & Bit Manipulation",
    fn="trailingZerosOfFactorial", params=[("n", "int")], ret="int", cmp="exact",
    desc="<p>Given a non-negative integer <code>n</code>, return the number of zeros at the end of the decimal representation of <code>n!</code> (that is, <code>1 * 2 * ... * n</code>, with <code>0! = 1</code>).</p><p>The factorial itself is astronomically large for big <code>n</code>, so you cannot compute it directly.</p><pre>n = 5   -> 5! = 120        -> 1\nn = 10  -> 10! = 3628800   -> 2\nn = 25  -> 25! ends in 6 zeros</pre>",
    constraints=["0 &le; n &le; 10<sup>9</sup>"],
    hints=["Each trailing zero comes from one factor of 10 in the product.",
           "10 = 2 * 5, and there are always more factors of 2 than factors of 5 in <code>n!</code>, so count the 5s.",
           "Multiples of 25 contribute two 5s, multiples of 125 three, and so on. Sum <code>n//5 + n//25 + n//125 + ...</code>."],
    editorial=["The number of trailing zeros equals the exponent of 10 in <code>n!</code>, which is the smaller of the exponents of 2 and 5. Factors of 2 are far more plentiful, so the exponent of 5 decides.",
               "Every multiple of 5 up to <code>n</code> contributes at least one 5: there are <code>n // 5</code> of them. Every multiple of 25 contributes an extra one: <code>n // 25</code> more, then <code>n // 125</code>, and so on. The terms shrink geometrically, so the loop runs about <code>log<sub>5</sub> n</code> times."],
    time="O(log n)", space="O(1)",
    solution='''def trailingZerosOfFactorial(n):
    count = 0
    while n:
        n //= 5
        count += n
    return count
''',
    tests=[[0], [1], [4], [5], [9], [10], [24], [25], [49], [50], [100], [125], [625], [3125], [1000000],
           [999999999], [1000000000], [INT_MAX // 3]],
)


def b_ftz(n):
    f = math.factorial(n)
    c = 0
    while f % 10 == 0:
        f //= 10
        c += 1
    return c


def v_ftz(tests):
    for t in tests:
        assert 0 <= t["args"][0] <= 10 ** 9


CHECKS["factorial-trailing-zeros-count"] = (b_ftz, lambda r: [r.randint(0, 400)], "exact")
VALIDATE["factorial-trailing-zeros-count"] = v_ftz

# ---------------------------------------------------------------- MEDIUM

p = add(
    id="reverse-integer-int32-overflow", title="Reverse Integer Within 32 Bits", diff="Medium", topic="Math & Bit Manipulation",
    fn="reverseInteger", params=[("x", "int")], ret="int", cmp="exact",
    desc="<p>Given a signed 32-bit integer <code>x</code>, return the integer whose decimal digits are those of <code>x</code> in reverse order, keeping the sign. Trailing zeros of <code>x</code> disappear (<code>120</code> becomes <code>21</code>).</p><p>If the reversed value does not fit in a signed 32-bit integer, i.e. it lies outside <code>[-2<sup>31</sup>, 2<sup>31</sup> - 1]</code>, return <code>0</code>. Assume your environment cannot store 64-bit integers, so decide about overflow before it happens.</p><pre>x = 123         -> 321\nx = -4560       -> -654\nx = 1534236469  -> 0   (9646324351 is too large)</pre>",
    constraints=["-2<sup>31</sup> &le; x &le; 2<sup>31</sup> - 1"],
    hints=["Pop the last digit with <code>x % 10</code> and push it with <code>rev = rev * 10 + digit</code>. Handle the sign separately.",
           "The danger is the push step. The multiplication <code>rev * 10 + digit</code> may leave the 32-bit range.",
           "Before pushing, check <code>rev</code> against <code>(2<sup>31</sup> - 1) // 10 = 214748364</code>: if it is larger, overflow is certain; if it is equal, the pushed digit must not exceed 7 (or 8 for the negative bound)."],
    editorial=["Work with the absolute value, remember the sign, and build the reversal digit by digit. In Python the integers never overflow, so you could simply compare the final answer with the 32-bit limits, but the point of the exercise is to detect the overflow in advance.",
               "Let <code>LIMIT = 2<sup>31</sup> - 1</code> for positive numbers and <code>2<sup>31</sup></code> for negative ones. Before executing <code>rev = rev * 10 + d</code>, return 0 if <code>rev &gt; LIMIT // 10</code>, or if <code>rev == LIMIT // 10</code> and <code>d &gt; LIMIT % 10</code>. Note that the input itself is always valid, so the first nine digits of any reversal fit; only the tenth push can overflow.",
               "Using a string reversal is shorter, but then you convert back and still need the range check. Either way the time is proportional to the number of digits, at most 10."],
    time="O(log |x|)", space="O(1)",
    solution='''def reverseInteger(x):
    neg = x < 0
    x = -x if neg else x
    limit = 2 ** 31 if neg else 2 ** 31 - 1
    rev = 0
    while x:
        d = x % 10
        x //= 10
        if rev > limit // 10 or (rev == limit // 10 and d > limit % 10):
            return 0
        rev = rev * 10 + d
    return -rev if neg else rev
''',
    tests=[[123], [-123], [120], [0], [5], [-8], [100000], [-4560], [1534236469], [-1534236469],
           [1463847412], [-1463847412], [1463847413], [INT_MAX], [INT_MIN], [-2143847412], [-2143847413],
           [1000000003], [1999999999], [-900000009]],
)


def b_reverse(x):
    s = str(abs(x))[::-1]
    v = int(s)
    if x < 0:
        v = -v
    return v if INT_MIN <= v <= INT_MAX else 0


def g_reverse(r):
    c = r.random()
    if c < 0.4:
        v = r.randint(-100000, 100000)
    elif c < 0.7:
        v = r.randint(10 ** 9, INT_MAX) * r.choice([1, -1])
    else:
        v = r.randint(INT_MIN, INT_MAX)
    return [max(INT_MIN, min(INT_MAX, v))]


def v_reverse(tests):
    for t in tests:
        assert INT_MIN <= t["args"][0] <= INT_MAX
    assert any(t["expected"] == 0 and t["args"][0] != 0 for t in tests)


CHECKS["reverse-integer-int32-overflow"] = (b_reverse, g_reverse, "exact")
VALIDATE["reverse-integer-int32-overflow"] = v_reverse

p = add(
    id="nth-digit-of-concatenated-integers", title="Nth Digit of the Infinite Integer String", diff="Medium", topic="Math & Bit Manipulation",
    fn="findNthDigit", params=[("n", "int")], ret="int", cmp="exact",
    desc="<p>Write the positive integers one after another without separators to form the infinite string <code>123456789101112131415...</code></p><p>Given <code>n</code>, return the digit at position <code>n</code> of that string, counting from 1.</p><pre>n = 3   -> 3\nn = 11  -> 0   (the string starts 1234567891011...; the 11th character is the 0 of \"10\")\nn = 15  -> 2</pre>",
    constraints=["1 &le; n &le; 2<sup>31</sup> - 1"],
    hints=["Building the string until it is long enough works for small <code>n</code> but is hopeless for n near 2 billion.",
           "Numbers with the same number of digits form blocks: 9 one-digit numbers, 90 two-digit numbers, 900 three-digit numbers, and so on.",
           "Skip whole blocks by subtracting <code>digits * count</code> while <code>n</code> is larger. Then locate which number inside the block holds the digit and which of its digits it is."],
    editorial=["Block <code>d</code> consists of the <code>9 * 10<sup>d-1</sup></code> numbers with exactly <code>d</code> digits, and spans <code>d * 9 * 10<sup>d-1</sup></code> characters of the string. Subtract block sizes from <code>n</code> until <code>n</code> falls inside the current block.",
               "Inside block <code>d</code> (starting at <code>start = 10<sup>d-1</sup></code>), the zero-based offset <code>n - 1</code> tells us the number: <code>start + (n - 1) // d</code>, and the digit position inside it: <code>(n - 1) % d</code>.",
               "At most 10 blocks are examined, so the algorithm is effectively constant time; only the final number is converted to a string."],
    time="O(log n)", space="O(1)",
    solution='''def findNthDigit(n):
    digits, count, start = 1, 9, 1
    while n > digits * count:
        n -= digits * count
        digits += 1
        count *= 10
        start *= 10
    num = start + (n - 1) // digits
    return int(str(num)[(n - 1) % digits])
''',
    tests=[[1], [3], [9], [10], [11], [12], [15], [189], [190], [191], [192], [2889], [2890], [2892],
           [100000], [999999999], [INT_MAX], [INT_MAX - 1], [1000000000]],
)


def b_nth(n):
    parts = []
    total = 0
    i = 1
    while total < n:
        s = str(i)
        parts.append(s)
        total += len(s)
        i += 1
    return int("".join(parts)[n - 1])


def v_nth(tests):
    for t in tests:
        assert 1 <= t["args"][0] <= INT_MAX
        assert 0 <= t["expected"] <= 9


CHECKS["nth-digit-of-concatenated-integers"] = (b_nth, lambda r: [r.randint(1, 3500) if r.random() < 0.8 else r.randint(1, 60)], "exact")
VALIDATE["nth-digit-of-concatenated-integers"] = v_nth

p = add(
    id="count-primes-below-n", title="Count Primes Below N", diff="Medium", topic="Number Theory",
    fn="countPrimesBelow", params=[("n", "int")], ret="int", cmp="exact",
    desc="<p>Given a non-negative integer <code>n</code>, return how many prime numbers are strictly less than <code>n</code>.</p><p>A prime is an integer greater than 1 whose only positive divisors are 1 and itself. Testing every number separately by trial division is too slow for the largest inputs.</p><pre>n = 10 -> 4   (2, 3, 5, 7)\nn = 2  -> 0\nn = 20 -> 8</pre>",
    constraints=["0 &le; n &le; 1,000,000"],
    hints=["Checking each number up to <code>n</code> for divisibility is O(n sqrt n) at best. Think about crossing off whole families of numbers instead.",
           "If a number is prime, every proper multiple of it is composite. Keep a boolean table and mark multiples as composite.",
           "This is the Sieve of Eratosthenes. For each prime <code>i</code> with <code>i * i &lt; n</code>, start marking at <code>i * i</code> (smaller multiples were already marked by smaller primes) and step by <code>i</code>."],
    editorial=["Create an array <code>is_prime</code> of length <code>n</code>, initially true except for 0 and 1. For each <code>i</code> from 2 while <code>i * i &lt; n</code>, if <code>i</code> is still marked prime, mark <code>i*i, i*i + i, i*i + 2i, ...</code> as composite. Finally count the entries that stayed true.",
               "Starting at <code>i * i</code> is safe because any smaller multiple <code>i * k</code> with <code>k &lt; i</code> has a smaller prime factor and has been crossed off already. The total work is about <code>n log log n</code>, which is nearly linear."],
    time="O(n log log n)", space="O(n)",
    solution='''def countPrimesBelow(n):
    if n < 3:
        return 0
    sieve = bytearray([1]) * n
    sieve[0] = sieve[1] = 0
    i = 2
    while i * i < n:
        if sieve[i]:
            for j in range(i * i, n, i):
                sieve[j] = 0
        i += 1
    return sum(sieve)
''',
    tests=[[0], [1], [2], [3], [4], [5], [10], [11], [20], [97], [100], [1000], [10000], [99991], [100000],
           [999983], [999984], [1000000]],
)


def b_primes(n):
    c = 0
    for k in range(2, n):
        if all(k % d for d in range(2, k)):
            c += 1
    return c


def v_primes(tests):
    known = {10: 4, 100: 25, 1000: 168, 10000: 1229, 100000: 9592, 1000000: 78498}
    for t in tests:
        n = t["args"][0]
        assert 0 <= n <= 1000000
        if n in known:
            assert t["expected"] == known[n]


CHECKS["count-primes-below-n"] = (b_primes, lambda r: [r.randint(0, 150)], "exact")
VALIDATE["count-primes-below-n"] = v_primes

p = add(
    id="modular-exponentiation-fast", title="Fast Modular Exponentiation", diff="Medium", topic="Number Theory",
    fn="powerMod", params=[("base", "int"), ("exp", "int"), ("mod", "int")], ret="int", cmp="exact",
    desc="<p>Compute <code>base<sup>exp</sup> mod mod</code>, that is, the remainder when <code>base</code> raised to the power <code>exp</code> is divided by <code>mod</code>. The exponent can be as large as about two billion, so multiplying <code>base</code> by itself <code>exp</code> times is far too slow, and the true power is far too large to store.</p><p>By convention <code>base<sup>0</sup> = 1</code> (so the answer for <code>exp = 0</code> is <code>1 mod mod</code>).</p><pre>base = 2, exp = 10, mod = 1000   -> 24\nbase = 3, exp = 0, mod = 7       -> 1\nbase = 5, exp = 3, mod = 1       -> 0</pre>",
    constraints=["0 &le; base &le; 2<sup>31</sup> - 1", "0 &le; exp &le; 2<sup>31</sup> - 1", "1 &le; mod &le; 10<sup>7</sup>"],
    hints=["Use the rule <code>(a * b) mod m = ((a mod m) * (b mod m)) mod m</code> so numbers never grow beyond <code>mod<sup>2</sup></code>.",
           "Squaring repeatedly gives <code>base<sup>1</sup>, base<sup>2</sup>, base<sup>4</sup>, base<sup>8</sup>, ...</code> in only about 31 steps.",
           "Write <code>exp</code> in binary. Whenever a bit is 1, multiply the result by the current square. Shift <code>exp</code> right and square the base each round."],
    editorial=["Binary exponentiation: <code>base<sup>exp</sup></code> is the product of <code>base<sup>2<sup>k</sup></sup></code> over every bit <code>k</code> that is set in <code>exp</code>. Keep a running <code>result</code> (start at <code>1 % mod</code>) and a running power <code>cur = base % mod</code>. For each bit of <code>exp</code>, from least significant: if the bit is set, <code>result = result * cur % mod</code>; then <code>cur = cur * cur % mod</code>.",
               "Because every intermediate value is reduced below <code>mod &le; 10<sup>7</sup></code>, products stay below 10<sup>14</sup>, which even a double-precision number can hold exactly. The loop runs once per bit of <code>exp</code>, at most 31 times."],
    time="O(log exp)", space="O(1)",
    solution='''def powerMod(base, exp, mod):
    result = 1 % mod
    cur = base % mod
    while exp > 0:
        if exp & 1:
            result = result * cur % mod
        cur = cur * cur % mod
        exp >>= 1
    return result
''',
    tests=[[2, 10, 1000], [3, 0, 7], [5, 3, 1], [0, 0, 1], [0, 0, 5], [0, 5, 7], [1, INT_MAX, 10 ** 7], [7, 1, 10],
           [10, 9, 1000000], [2, 31, 10 ** 7], [123456789, 987654321, 9999991], [INT_MAX, INT_MAX, 10 ** 7],
           [2, INT_MAX, 9999991], [9999991, 5, 9999991], [999, 2000000000, 10000000], [17, 1000000, 65537]],
)


def b_powmod(base, exp, mod):
    r = 1 % mod
    for _ in range(exp):
        r = (r * base) % mod
    return r


def g_powmod(r):
    return [r.randint(0, 40), r.randint(0, 60), r.randint(1, 50)]


def v_powmod(tests):
    for t in tests:
        b, e, m = t["args"]
        assert 0 <= b <= INT_MAX and 0 <= e <= INT_MAX and 1 <= m <= 10 ** 7
        assert t["expected"] == pow(b, e, m)


CHECKS["modular-exponentiation-fast"] = (b_powmod, g_powmod, "exact")
VALIDATE["modular-exponentiation-fast"] = v_powmod

p = add(
    id="super-pow-digit-exponent", title="Power With a Huge Digit-Array Exponent", diff="Medium", topic="Number Theory",
    fn="superPow", params=[("a", "int"), ("b", "int[]")], ret="int", cmp="exact",
    desc="<p>Compute <code>a<sup>B</sup> mod 1337</code>, where <code>B</code> is a very large non-negative integer given as an array of its decimal digits <code>b</code>, most significant digit first. The number <code>B</code> can have up to 2,000 digits, so it fits in no ordinary integer type.</p><pre>a = 2, b = [1, 0]       -> 2^10 mod 1337 = 1024\na = 3, b = [0]          -> 1\na = 2, b = [1, 0, 0]    -> 2^100 mod 1337 = 1198</pre>",
    constraints=["1 &le; a &le; 2<sup>31</sup> - 1", "1 &le; b.length &le; 2,000", "0 &le; b[i] &le; 9 and b has no leading zero (except for the single array [0])"],
    hints=["You cannot convert <code>b</code> into a normal integer. Process it one digit at a time instead.",
           "If you already know <code>X = a<sup>P</sup> mod 1337</code> for the prefix <code>P</code>, then for the prefix extended by digit <code>d</code> (which is <code>10P + d</code>) the answer is <code>X<sup>10</sup> * a<sup>d</sup> mod 1337</code>.",
           "Implement a small helper <code>pw(x, k)</code> that computes <code>x<sup>k</sup> mod 1337</code> by fast exponentiation (or plain repeated multiplication, since <code>k &le; 10</code>), reduce <code>a</code> mod 1337 first, and fold the digits in from left to right."],
    editorial=["Start with <code>result = 1</code>, which represents <code>a<sup>0</sup></code>. For each digit <code>d</code> from left to right, the exponent so far goes from <code>P</code> to <code>10P + d</code>, so <code>a<sup>10P + d</sup> = (a<sup>P</sup>)<sup>10</sup> * a<sup>d</sup></code>. Update <code>result = pw(result, 10) * pw(a, d) mod 1337</code>.",
               "Every exponent used by the helper is at most 10, so the whole algorithm is linear in the number of digits. Reduce <code>a</code> modulo 1337 once at the start so every product stays tiny.",
               "An alternative uses Euler's theorem: 1337 = 7 * 191, so for <code>a</code> coprime to 1337 the exponent can be reduced modulo phi(1337) = 6 * 190 = 1140. That route needs extra care when <code>a</code> shares a factor with 1337, so the digit-by-digit method is both simpler and always correct."],
    time="O(L)", space="O(1)",
    solution='''def superPow(a, b):
    MOD = 1337

    def pw(x, k):
        r = 1
        while k:
            if k & 1:
                r = r * x % MOD
            x = x * x % MOD
            k >>= 1
        return r

    a %= MOD
    result = 1
    for d in b:
        result = pw(result, 10) * pw(a, d) % MOD
    return result
''',
    tests=[[2, [1, 0]], [3, [0]], [2, [1, 0, 0]], [1, [9, 9, 9]], [2, [3]], [1337, [5]], [2674, [1, 2]],
           [7, [0]], [191, [4, 0]], [INT_MAX, [1, 2, 3, 4, 5, 6, 7, 8, 9]], [2, [2, 1, 4, 7, 4, 8, 3, 6, 4, 7]],
           [1336, [1, 0, 0, 0, 0, 1]], [1338, [8, 7, 6]]],
)
_r = rnd(7301)
p["tests"].append([_r.randint(2, INT_MAX), [_r.randint(1, 9)] + [_r.randint(0, 9) for _ in range(1999)]])
p["tests"].append([_r.randint(2, INT_MAX), [9] * 2000])
p["tests"].append([_r.randint(2, INT_MAX), [1] + [0] * 1999])


def b_superpow(a, b):
    e = int("".join(map(str, b)))
    # walk a^0, a^1, a^2, ... mod 1337 until a value repeats, then jump over whole cycles
    seen = {}
    seq = []
    r = 1
    k = 0
    while r not in seen:
        seen[r] = k
        seq.append(r)
        r = (r * a) % 1337
        k += 1
    start = seen[r]
    cycle = k - start
    if e < len(seq):
        return seq[e]
    return seq[start + (e - start) % cycle]


def g_superpow(r):
    k = r.randint(1, 3)
    digits = [r.randint(1, 9)] + [r.randint(0, 9) for _ in range(k - 1)]
    if r.random() < 0.1:
        digits = [0]
    a = r.choice([r.randint(1, 3000), r.randint(1, INT_MAX), 1337 * r.randint(1, 5), 7 * r.randint(1, 100)])
    return [a, digits]


def v_superpow(tests):
    for t in tests:
        a, b = t["args"]
        assert 1 <= a <= INT_MAX and 1 <= len(b) <= 2000
        assert all(0 <= d <= 9 for d in b)
        assert b[0] != 0 or len(b) == 1
        assert t["expected"] == pow(a, int("".join(map(str, b))), 1337)


CHECKS["super-pow-digit-exponent"] = (b_superpow, g_superpow, "exact")
VALIDATE["super-pow-digit-exponent"] = v_superpow

# ---------------------------------------------------------------- HARD

p = add(
    id="count-digit-one-occurrences", title="Count Digit One in 1..n", diff="Hard", topic="Math & Bit Manipulation",
    fn="countDigitOne", params=[("n", "int")], ret="int", cmp="exact",
    desc="<p>Given a non-negative integer <code>n</code>, count how many times the digit <code>1</code> appears in the decimal representations of all integers from <code>0</code> to <code>n</code> inclusive. A number such as <code>111</code> contributes three.</p><pre>n = 13  -> 6   (1, 10, 11 (two), 12, 13)\nn = 0   -> 0\nn = 99  -> 20</pre><p>Looping over every number is too slow when <code>n</code> is close to a billion.</p>",
    constraints=["0 &le; n &le; 10<sup>9</sup>"],
    hints=["Count the ones separately for each digit position (units, tens, hundreds, ...) and add the totals.",
           "For position with place value <code>m</code>, split <code>n</code> into <code>high = n // (m*10)</code>, <code>cur = (n // m) % 10</code> and <code>low = n % m</code>. Full cycles of the lower positions contribute <code>high * m</code> ones.",
           "Then add depending on <code>cur</code>: if <code>cur &gt; 1</code> an extra full block of <code>m</code> ones; if <code>cur == 1</code> the partial block adds <code>low + 1</code>; if <code>cur == 0</code> nothing more."],
    editorial=["Look at one position at a time, say the hundreds place with <code>m = 100</code>. As the numbers run from 0 upward, that digit is 1 for exactly 100 consecutive numbers (x100 to x199) in every window of 1000 consecutive numbers. So the <code>high</code> full windows (<code>high = n // 1000</code>) contribute <code>high * 100</code> ones.",
               "Then consider the incomplete last window, which starts with the hundreds digit equal to <code>cur</code>. If <code>cur = 0</code> the digit has not reached 1 yet: no extra. If <code>cur = 1</code>, the digit is 1 for the numbers from the start of the hundreds-1 block up to <code>n</code>, which is <code>low + 1</code> numbers, where <code>low = n % 100</code>. If <code>cur &ge; 2</code> the whole hundreds-1 block is complete and adds 100.",
               "Repeat for every place value up to the highest digit of <code>n</code>. The loop runs at most 10 times. The total fits in 32 bits for <code>n &le; 10<sup>9</sup></code> (the maximum is 900,000,001)."],
    time="O(log n)", space="O(1)",
    solution='''def countDigitOne(n):
    total = 0
    m = 1
    while m <= n:
        high = n // (m * 10)
        cur = (n // m) % 10
        low = n % m
        if cur == 0:
            total += high * m
        elif cur == 1:
            total += high * m + low + 1
        else:
            total += (high + 1) * m
        m *= 10
    return total
''',
    tests=[[0], [1], [2], [9], [10], [11], [13], [19], [20], [99], [100], [101], [110], [111], [199], [1000],
           [12345], [99999], [1410065408], [1000000000], [999999999], [123456789], [1111111111 // 2]],
)
p["tests"] = [t for t in p["tests"] if t[0] <= 10 ** 9]


def b_digit_one(n):
    return sum(str(i).count("1") for i in range(n + 1))


def v_digit_one(tests):
    for t in tests:
        assert 0 <= t["args"][0] <= 10 ** 9
        assert 0 <= t["expected"] <= INT_MAX
    for t in tests:
        if t["args"][0] == 10 ** 9:
            assert t["expected"] == 900000001


CHECKS["count-digit-one-occurrences"] = (b_digit_one, lambda r: [r.randint(0, 1500) if r.random() < 0.8 else r.randint(0, 40)], "exact")
VALIDATE["count-digit-one-occurrences"] = v_digit_one

p = add(
    id="binomial-mod-small-prime", title="Binomial Coefficient Modulo a Prime", diff="Hard", topic="Number Theory",
    fn="binomialModPrime", params=[("n", "int"), ("r", "int"), ("p", "int")], ret="int", cmp="exact",
    desc="<p>Given integers <code>n</code>, <code>r</code> and a prime <code>p</code>, return the binomial coefficient <code>C(n, r)</code> (the number of ways to choose <code>r</code> items from <code>n</code>) modulo <code>p</code>.</p><p>Here <code>n</code> can be as large as about two billion while <code>p</code> is a small prime (at most 1,000), so <code>n</code> may be far larger than <code>p</code> and the usual shortcut with factorials fails, because <code>n!</code> is divisible by <code>p</code>.</p><pre>n = 5, r = 2, p = 7        -> C(5,2) = 10 -> 3\nn = 10, r = 5, p = 3       -> C(10,5) = 252 -> 0\nn = 2000000000, r = 3, p = 2 -> 0</pre>",
    constraints=["0 &le; r &le; n &le; 2<sup>31</sup> - 1", "p is a prime with 2 &le; p &le; 1,000"],
    hints=["If <code>n &lt; p</code>, the answer is <code>n! / (r! (n-r)!)</code> computed with modular inverses (Fermat: <code>x<sup>-1</sup> = x<sup>p-2</sup> mod p</code>). What breaks when <code>n &ge; p</code>?",
           "Write <code>n</code> and <code>r</code> in base <code>p</code>. Lucas' theorem says <code>C(n, r)</code> is congruent modulo <code>p</code> to the product of <code>C(n<sub>i</sub>, r<sub>i</sub>)</code> over corresponding base-<code>p</code> digits.",
           "Precompute factorials modulo <code>p</code> up to <code>p - 1</code>. For each pair of digits, return 0 as soon as <code>r<sub>i</sub> &gt; n<sub>i</sub></code>; otherwise multiply in the small binomial computed with factorials and inverse factorials."],
    editorial=["Lucas' theorem: if <code>n = n<sub>k</sub>p<sup>k</sup> + ... + n<sub>0</sub></code> and <code>r = r<sub>k</sub>p<sup>k</sup> + ... + r<sub>0</sub></code> in base <code>p</code>, then <code>C(n, r) &equiv; &prod; C(n<sub>i</sub>, r<sub>i</sub>) (mod p)</code>, where <code>C(a, b) = 0</code> if <code>b &gt; a</code>. Each digit is below <code>p</code>, so each small binomial can be evaluated with factorials mod <code>p</code> without any factor of <code>p</code> appearing.",
               "Precompute <code>fact[0..p-1]</code> mod <code>p</code>. A small binomial is <code>fact[a] * inv(fact[b]) * inv(fact[a-b]) mod p</code>, where the inverse of <code>x</code> is <code>x<sup>p-2</sup> mod p</code> by Fermat's little theorem (all values involved are non-zero modulo <code>p</code> since they are below <code>p</code>).",
               "The loop runs once per base-<code>p</code> digit, at most 31 times (for <code>p = 2</code>), and each step costs a logarithmic modular power. Setup is O(p). Early exit on a zero result is a nice optimization: it happens exactly when some digit of <code>r</code> exceeds the corresponding digit of <code>n</code>."],
    time="O(p + log<sub>p</sub>(n) * log p)", space="O(p)",
    solution='''def binomialModPrime(n, r, p):
    fact = [1] * p
    for i in range(1, p):
        fact[i] = fact[i - 1] * i % p

    def small(a, b):
        if b > a:
            return 0
        return fact[a] * pow(fact[b] * fact[a - b] % p, p - 2, p) % p

    result = 1
    while n or r:
        result = result * small(n % p, r % p) % p
        if result == 0:
            return 0
        n //= p
        r //= p
    return result
''',
    tests=[[5, 2, 7], [10, 5, 3], [2000000000, 3, 2], [0, 0, 2], [0, 0, 997], [1, 0, 2], [1, 1, 2], [6, 3, 5],
           [7, 3, 7], [8, 4, 2], [100, 50, 101], [100, 50, 13], [1000, 500, 11], [1000000, 3, 997],
           [INT_MAX, 12345, 997], [INT_MAX, INT_MAX, 3], [INT_MAX, 1, 1000 - 3], [INT_MAX, INT_MAX // 2, 5],
           [2 ** 30 - 1, 2 ** 29, 2], [2 ** 30 - 1, 2 ** 29 - 1, 2], [1000000000, 123456789, 983], [999, 998, 997]],
)
for _t in p["tests"]:
    assert _is_prime(_t[2]) and 0 <= _t[1] <= _t[0] <= INT_MAX, _t


def b_binom(n, r, pr):
    return math.comb(n, r) % pr


def g_binom(r):
    pr = r.choice([2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 97])
    n = r.randint(0, 300)
    return [n, r.randint(0, n), pr]


def v_binom(tests):
    for t in tests:
        n, r, pr = t["args"]
        assert 0 <= r <= n <= INT_MAX and _is_prime(pr) and 2 <= pr <= 1000
        assert 0 <= t["expected"] < pr
    assert any(t["expected"] == 0 for t in tests) and any(t["expected"] != 0 for t in tests)


CHECKS["binomial-mod-small-prime"] = (b_binom, g_binom, "exact")
VALIDATE["binomial-mod-small-prime"] = v_binom
