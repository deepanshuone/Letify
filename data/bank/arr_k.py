"""Problems: arrays of digits (big-number arithmetic with int[]). See data/lib.py for the registry."""
import sys

from lib import add, rnd, CHECKS, VALIDATE, gen_arr  # noqa: F401

if hasattr(sys, "set_int_max_str_digits"):
    sys.set_int_max_str_digits(0)

INT_MIN, INT_MAX = -(2 ** 31), 2 ** 31 - 1
TOPIC = "Arrays & Hashing"

ENC = ("<p><strong>Encoding.</strong> A non-negative integer is stored as an array of its decimal digits, most significant digit first, "
       "one digit per element, with no leading zeros; the number zero is stored as <code>[0]</code>. Results use the same format. "
       "The numbers can have thousands of digits, so you cannot convert a whole array into one machine integer.</p>")


# ---------------------------------------------------------------- helpers (tests and brute force only)

def _num(d):
    return int("".join(map(str, d)))


def _dig(n):
    return [int(c) for c in str(n)]


def _rd(r, n):
    """Random n-digit number (no leading zero unless n == 1)."""
    if n == 1:
        return [r.randint(0, 9)]
    return [r.randint(1, 9)] + [r.randint(0, 9) for _ in range(n - 1)]


def _rd9(r, n):
    """Random n-digit number rich in 9s and 0s, to provoke long carry and borrow chains."""
    if n == 1:
        return [r.choice([0, 9, 9, 5])]
    return [r.choice([1, 9, 9, 8])] + [r.choice([9, 9, 9, 0, 0, 5, r.randint(0, 9)]) for _ in range(n - 1)]


def _gd(r, nmax=6):
    return (_rd9 if r.random() < 0.4 else _rd)(r, r.randint(1, nmax))


def _is_number(d):
    return len(d) >= 1 and all(isinstance(x, int) and 0 <= x <= 9 for x in d) and (d[0] != 0 or d == [0])


# ================================================================ EASY

p = add(
    id="count-carries-adding-digit-arrays", title="Count the Carries When Adding", diff="Easy", topic=TOPIC,
    fn="countCarries", params=[("a", "int[]"), ("b", "int[]")], ret="int", cmp="exact",
    desc=ENC + "<p>Add the numbers <code>a</code> and <code>b</code> column by column the way you do on paper, starting at the units column. A <em>carry operation</em> happens in a column when the digit sum of that column (including the carry coming in from the right) is 10 or more, so a 1 is carried into the next column. Return how many carry operations the addition needs.</p>"
         "<p>Example: <code>a = [4,5]</code>, <code>b = [5,5]</code> (45 + 55). The units column gives 5 + 5 = 10, a carry; the tens column gives 4 + 5 + 1 = 10, another carry. The answer is <code>2</code>.</p>"
         "<p>Example: <code>a = [9,9,9]</code>, <code>b = [1]</code> (999 + 1): all three columns carry, so the answer is <code>3</code>.</p>",
    constraints=["1 &le; a.length, b.length &le; 5,000", "0 &le; a[i], b[i] &le; 9", "No leading zeros, except for the number zero stored as [0]"],
    hints=["Do exactly what you do on paper: go through the columns from the right, with a running carry.",
           "The two arrays can have different lengths. Once one of them runs out, treat its missing digits as 0 (the other digits can still produce a carry).",
           "Per column: <code>s = carry + digitA + digitB</code>; the new carry is 1 when <code>s &ge; 10</code>, else 0. Add the new carry to your counter. Stop after the longer array is done (a final carry creates no further column to count)."],
    editorial=["Walk both arrays from their right ends with two indices and one variable <code>carry</code>. In every column the sum is at most 9 + 9 + 1 = 19, so the carry out is always 0 or 1. Count the columns whose sum reaches 10.",
               "The loop runs for max(a.length, b.length) columns. After the last column a leftover carry only becomes a new leading digit; it is not an extra carry <em>operation</em> because no addition happens in that new column. Time is linear and only a few variables are needed."],
    time="O(n + m)", space="O(1)",
    solution='''def countCarries(a, b):
    i, j = len(a) - 1, len(b) - 1
    carry = 0
    count = 0
    while i >= 0 or j >= 0:
        s = carry
        if i >= 0:
            s += a[i]
            i -= 1
        if j >= 0:
            s += b[j]
            j -= 1
        carry = 1 if s >= 10 else 0
        count += carry
    return count
''',
    tests=[[[4, 5], [5, 5]], [[9, 9, 9], [1]], [[0], [0]], [[1, 2, 3], [4, 5, 6]], [[5], [5]], [[9], [9]],
           [[1, 0, 0, 0], [9, 9, 9]], [[9, 9, 9, 9], [9, 9, 9, 9]], [[8, 9, 5], [2, 5]], [[1], [9, 9, 9, 9, 9]]],
)
_r = rnd(1101)
p["tests"].append([[9] * 4000, [1]])
p["tests"].append([_rd(_r, 4000), _rd(_r, 3500)])
p["tests"].append([[5] * 3000 + [4] * 800, [5] * 3500])
p["tests"].append([[1] + [9, 0] * 1500, [9, 9] * 1500])


def b_carries(a, b):
    x, y = _num(a), _num(b)
    return sum(1 for k in range(1, max(len(a), len(b)) + 1) if x % 10 ** k + y % 10 ** k >= 10 ** k)


def g_carries(r):
    return [_gd(r, 6), _gd(r, 6)]


def v_carries(tests):
    for t in tests:
        a, b = t["args"]
        assert 1 <= len(a) <= 5000 and 1 <= len(b) <= 5000 and _is_number(a) and _is_number(b)
        assert t["expected"] == b_carries(a, b)


CHECKS["count-carries-adding-digit-arrays"] = (b_carries, g_carries, "exact")
VALIDATE["count-carries-adding-digit-arrays"] = v_carries

p = add(
    id="add-integer-to-array-form", title="Add an Integer to a Digit Array", diff="Easy", topic=TOPIC,
    fn="addToArrayForm", params=[("num", "int[]"), ("k", "int")], ret="int[]", cmp="exact",
    desc=ENC + "<p>The array <code>num</code> holds a big non-negative integer, and <code>k</code> is an ordinary non-negative integer. Return the digit array of <code>num + k</code>.</p>"
         "<p>Example: <code>num = [1,2,0,0]</code>, <code>k = 34</code> gives <code>[1,2,3,4]</code>. Example: <code>num = [9,9,9]</code>, <code>k = 1</code> gives <code>[1,0,0,0]</code>.</p>",
    constraints=["1 &le; num.length &le; 5,000", "0 &le; k &le; 2<sup>31</sup> - 1", "0 &le; num[i] &le; 9, no leading zeros except for [0]"],
    hints=["You can add digit by digit from the right, as on paper. What plays the role of the second number?",
           "You do not have to split k into digits first. Keep one variable that starts as <code>k</code>.",
           "Loop while there are digits left <em>or</em> the variable is non-zero: add the next digit of <code>num</code> to it, output <code>value % 10</code> and keep <code>value // 10</code> as the carry. Reverse the output at the end."],
    editorial=["Use <code>k</code> itself as the running carry. Starting from the last digit of <code>num</code>, add that digit to the carry variable, emit its last decimal digit and divide it by 10 to get the carry for the next column. When <code>num</code> is used up, the remaining value (at most ten digits) is emitted digit by digit, which handles a <code>k</code> longer than the array and a final carry at once.",
               "The digits come out least significant first, so reverse the result. No leading zero can appear: the loop ends only after the carry is exhausted, and the last emitted digit is then non-zero (except for 0 + 0, which correctly gives [0]). Time is O(n) for the array plus O(log k) for the integer."],
    time="O(n + log k)", space="O(1) extra",
    solution='''def addToArrayForm(num, k):
    res = []
    i = len(num) - 1
    carry = k
    while i >= 0 or carry:
        if i >= 0:
            carry += num[i]
            i -= 1
        res.append(carry % 10)
        carry //= 10
    res.reverse()
    return res
''',
    tests=[[[1, 2, 0, 0], 34], [[9, 9, 9], 1], [[0], 0], [[0], 7], [[5], 0], [[2, 7, 4], 181], [[1], INT_MAX],
           [[9, 9], INT_MAX], [[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 999999999], [[9], 9]],
)
_r = rnd(1102)
p["tests"].append([_rd(_r, 4000), INT_MAX])
p["tests"].append([[9] * 4000, INT_MAX])
p["tests"].append([[1] + [0] * 4999, 1])


def b_addk(num, k):
    return _dig(_num(num) + k)


def g_addk(r):
    return [_gd(r, 7), r.choice([0, r.randint(0, 9), r.randint(0, 999), r.randint(0, 10 ** 8), r.randint(0, INT_MAX)])]


def v_addk(tests):
    for t in tests:
        num, k = t["args"]
        assert 1 <= len(num) <= 5000 and _is_number(num) and 0 <= k <= INT_MAX
        assert t["expected"] == b_addk(num, k)


CHECKS["add-integer-to-array-form"] = (b_addk, g_addk, "exact")
VALIDATE["add-integer-to-array-form"] = v_addk

p = add(
    id="divide-digit-array-by-integer", title="Divide a Digit Array by an Integer", diff="Easy", topic=TOPIC,
    fn="divideDigits", params=[("digits", "int[]"), ("k", "int")], ret="int[]", cmp="exact",
    desc=ENC + "<p>Divide the big number stored in <code>digits</code> by the positive integer <code>k</code> and return the quotient rounded down, as a digit array. If the quotient is 0, return <code>[0]</code>.</p>"
         "<p>Example: <code>digits = [1,2,3,4]</code>, <code>k = 5</code>: 1234 / 5 = 246.8, so the answer is <code>[2,4,6]</code>. Example: <code>digits = [7]</code>, <code>k = 9</code> gives <code>[0]</code>.</p>",
    constraints=["1 &le; digits.length &le; 5,000", "1 &le; k &le; 10<sup>8</sup>", "0 &le; digits[i] &le; 9, no leading zeros except for [0]"],
    hints=["Think of long division on paper: you bring down one digit at a time.",
           "Maintain a remainder. Bring down the next digit by computing <code>rem * 10 + digit</code>. How large can the quotient digit for this step be?",
           "The quotient digit is <code>(rem * 10 + digit) // k</code>, which is always between 0 and 9, and the new remainder is the value modulo <code>k</code>. Collect the quotient digits and drop the leading zeros at the end (keep one digit)."],
    editorial=["This is schoolbook long division. Process the digits from left to right, keeping the remainder of the part of the number read so far. The remainder is always smaller than k, so <code>rem * 10 + digit</code> is smaller than 10k and the quotient digit is in 0..9.",
               "Because k is at most 10<sup>8</sup>, the intermediate value stays below about 10<sup>9</sup> and fits in a 32-bit integer. The produced digits have the same count as the input, so strip leading zeros at the end (but keep a single 0 if the whole quotient is zero). Single pass, O(n)."],
    time="O(n)", space="O(n)",
    solution='''def divideDigits(digits, k):
    out = []
    rem = 0
    for d in digits:
        rem = rem * 10 + d
        out.append(rem // k)
        rem %= k
    i = 0
    while i < len(out) - 1 and out[i] == 0:
        i += 1
    return out[i:]
''',
    tests=[[[1, 2, 3, 4], 5], [[7], 9], [[0], 5], [[9], 1], [[1, 0, 0, 0], 10], [[9, 9, 9, 9], 3], [[1, 0, 0, 0, 0, 0, 0, 0, 0, 0], 100000000],
           [[5, 0, 0], 7], [[3, 0, 0, 0, 1], 3], [[9, 9, 9, 9, 9, 9, 9, 9, 9], 99999999]],
)
_r = rnd(1103)
p["tests"].append([_rd(_r, 5000), 97])
p["tests"].append([_rd(_r, 4000), 100000000])
p["tests"].append([[9] * 5000, 3])
p["tests"].append([[1] + [0] * 3999, 99999989])


def b_divk(digits, k):
    return _dig(_num(digits) // k)


def g_divk(r):
    return [_gd(r, 8), r.choice([1, 2, 3, 7, 9, 10, r.randint(1, 100), r.randint(1, 10 ** 8)])]


def v_divk(tests):
    for t in tests:
        digits, k = t["args"]
        assert 1 <= len(digits) <= 5000 and _is_number(digits) and 1 <= k <= 10 ** 8
        assert _is_number(t["expected"])
        assert t["expected"] == b_divk(digits, k)


CHECKS["divide-digit-array-by-integer"] = (b_divk, g_divk, "exact")
VALIDATE["divide-digit-array-by-integer"] = v_divk

# ================================================================ MEDIUM

p = add(
    id="next-number-without-digit-four", title="Next Number Without the Digit Four", diff="Medium", topic=TOPIC, tier="extra",
    fn="nextWithoutFour", params=[("digits", "int[]")], ret="int[]", cmp="exact",
    desc=ENC + "<p>In some buildings floor numbers skip every number that contains the digit 4. Given a number <code>digits</code> (which may itself contain 4s), return the smallest number that is <strong>strictly larger</strong> than it and contains no digit 4.</p>"
         "<p>Example: <code>[3,9]</code> (39) gives <code>[5,0]</code>, because 40 to 49 all contain a 4. Example: <code>[4]</code> gives <code>[5]</code>. Example: <code>[9,9]</code> gives <code>[1,0,0]</code>.</p>",
    constraints=["1 &le; digits.length &le; 5,000", "0 &le; digits[i] &le; 9, no leading zeros except for [0]", "The result may be one digit longer than the input"],
    hints=["First add one, exactly as in <em>Plus One</em>. Is the result always valid?",
           "After adding one, look at the leftmost 4 (if any). Every number that keeps the prefix before that 4 and has a 4 in this place is invalid.",
           "Change the leftmost 4 into a 5 and set all digits after it to 0. That is the smallest number that is not smaller than the incremented value and has no 4 at or before this place; digits to its left contain no 4 by choice of the leftmost 4."],
    editorial=["Increment the number with carry propagation (trailing 9s become 0, the first other digit grows by one, and an all-9 number gets a new leading 1). Now find the leftmost 4. If there is none, the incremented number is the answer.",
               "Otherwise every number from the incremented value up to the end of the block that shares the prefix and has 4 at this position contains a 4. The next candidate is therefore the prefix, followed by 5, followed by zeros. The prefix has no 4 (this was the leftmost one) and 5 and 0 are fine, so it is valid and minimal. Two linear passes, O(n)."],
    time="O(n)", space="O(n)",
    solution='''def nextWithoutFour(digits):
    res = list(digits)
    i = len(res) - 1
    while i >= 0 and res[i] == 9:
        res[i] = 0
        i -= 1
    if i < 0:
        res.insert(0, 1)
    else:
        res[i] += 1
    for j in range(len(res)):
        if res[j] == 4:
            res[j] = 5
            for t in range(j + 1, len(res)):
                res[t] = 0
            break
    return res
''',
    tests=[[[3, 9]], [[4]], [[9, 9]], [[0]], [[3]], [[3, 9, 9, 9]], [[1, 4, 4]], [[4, 1]], [[1, 3, 9]], [[8, 9, 9, 8]],
           [[4, 4, 4, 4]], [[1, 0, 3, 9, 9, 9, 3, 9]]],
)
_r = rnd(1104)
p["tests"].append([[3] + [9] * 3999])
p["tests"].append([[9] * 4000])
p["tests"].append([[r_ if r_ != 4 else 3 for r_ in _rd(_r, 4500)]])
p["tests"].append([_rd(_r, 4000)])


def b_no4(digits):
    n = _num(digits) + 1
    while "4" in str(n):
        n += 1
    return _dig(n)


def g_no4(r):
    return [_gd(r, 5)]


def v_no4(tests):
    for t in tests:
        d = t["args"][0]
        assert 1 <= len(d) <= 5000 and _is_number(d)
        e = t["expected"]
        assert _is_number(e) and 4 not in e
        if len(d) <= 12:
            assert e == b_no4(d)
        else:
            assert _num(e) > _num(d)


CHECKS["next-number-without-digit-four"] = (b_no4, g_no4, "exact")
VALIDATE["next-number-without-digit-four"] = v_no4

p = add(
    id="absolute-difference-of-digit-arrays", title="Absolute Difference of Two Digit Arrays", diff="Medium", topic=TOPIC,
    fn="absDifference", params=[("a", "int[]"), ("b", "int[]")], ret="int[]", cmp="exact",
    desc=ENC + "<p>Return the digit array of <code>|a - b|</code>, the absolute difference of the two numbers. If the numbers are equal, return <code>[0]</code>.</p>"
         "<p>Example: <code>a = [1,0,0,0]</code>, <code>b = [9,9,9]</code> gives <code>[1]</code>. Example: <code>a = [2,5]</code>, <code>b = [7,1]</code> gives <code>[4,6]</code>.</p>",
    constraints=["1 &le; a.length, b.length &le; 5,000", "0 &le; a[i], b[i] &le; 9", "No leading zeros, except for the number zero stored as [0]"],
    hints=["Subtraction on paper only works when you subtract the smaller number from the larger one. Decide which is which first.",
           "Without leading zeros, a longer array is a larger number. For equal lengths, compare the digits from the left.",
           "Subtract the digits from the right with a borrow flag: if <code>x - y - borrow</code> is negative, add 10 and set borrow to 1. The result can start with zeros, so drop them (keep one digit)."],
    editorial=["First order the operands. Because there are no leading zeros, the array with more digits is larger; when both lengths are equal the lexicographic comparison of the arrays equals the numeric comparison.",
               "Then do column subtraction from the right with a borrow. The larger number never runs out of digits before the smaller one, and since big &ge; small the final borrow is always 0. Leading zeros created by cancellation (as in 1000 - 999) are removed at the end, leaving a single 0 for equal inputs. Linear time."],
    time="O(n + m)", space="O(n + m)",
    solution='''def absDifference(a, b):
    if len(a) != len(b):
        x, y = (a, b) if len(a) > len(b) else (b, a)
    else:
        x, y = (a, b) if a >= b else (b, a)
    res = []
    borrow = 0
    j = len(y) - 1
    for i in range(len(x) - 1, -1, -1):
        d = x[i] - borrow - (y[j] if j >= 0 else 0)
        j -= 1
        if d < 0:
            d += 10
            borrow = 1
        else:
            borrow = 0
        res.append(d)
    while len(res) > 1 and res[-1] == 0:
        res.pop()
    res.reverse()
    return res
''',
    tests=[[[1, 0, 0, 0], [9, 9, 9]], [[2, 5], [7, 1]], [[0], [0]], [[5], [5]], [[0], [9]], [[1, 2, 3], [1, 2, 3]],
           [[1, 0, 0, 0, 0], [1]], [[4, 0, 2], [3, 9, 8]], [[9, 9, 9], [1, 0, 0, 0]], [[1, 0, 0, 5], [1, 0, 0, 0]]],
)
_r = rnd(1105)
p["tests"].append([[1] + [0] * 3999, [9] * 3999])
p["tests"].append([_rd(_r, 4000), _rd(_r, 3000)])
_x = _rd(_r, 4000)
p["tests"].append([_x, _x[:-1] + [(_x[-1] + 1) % 10]])
p["tests"].append([_rd9(_r, 3500), _rd9(_r, 3500)])


def b_absdiff(a, b):
    return _dig(abs(_num(a) - _num(b)))


def g_absdiff(r):
    return [_gd(r, 6), _gd(r, 6)]


def v_absdiff(tests):
    for t in tests:
        a, b = t["args"]
        assert 1 <= len(a) <= 5000 and 1 <= len(b) <= 5000 and _is_number(a) and _is_number(b)
        assert _is_number(t["expected"]) and t["expected"] == b_absdiff(a, b)


CHECKS["absolute-difference-of-digit-arrays"] = (b_absdiff, g_absdiff, "exact")
VALIDATE["absolute-difference-of-digit-arrays"] = v_absdiff

p = add(
    id="factorial-as-digit-array", title="Factorial as a Digit Array", diff="Medium", topic=TOPIC,
    fn="factorialDigits", params=[("n", "int")], ret="int[]", cmp="exact",
    desc=ENC + "<p>Compute <code>n!</code> (the product of all integers from 1 to <code>n</code>, with <code>0! = 1</code>) and return its digits. The result is far beyond any integer type, so you must multiply with arrays.</p>"
         "<p>Example: <code>n = 5</code> gives <code>[1,2,0]</code>. Example: <code>n = 10</code> gives <code>[3,6,2,8,8,0,0]</code>.</p>",
    constraints=["0 &le; n &le; 600", "600! has 1,409 digits"],
    hints=["Compute 1 &times; 2 &times; 3 &times; ... one factor at a time and keep the running product as an array of digits.",
           "Multiplying a digit array by a small number <code>m</code> works like multiplication on paper: multiply every digit by <code>m</code>, add the carry from the previous digit, keep the last digit and carry the rest.",
           "Store the digits least significant first so that the array grows at its end. After the digits are used up, append the remaining carry digit by digit. Reverse at the very end."],
    editorial=["Keep the product as a list of digits, least significant digit first. To multiply by <code>m &le; 600</code>, go through the list: <code>v = digit * m + carry</code>, store <code>v % 10</code>, carry <code>v // 10</code>. When the list ends, flush the remaining carry as new digits (it can be up to three digits long).",
               "Doing this for m = 2..n costs O(n &middot; D) where D is the number of digits of n!, about n log<sub>10</sub> n. For n = 600 that is a few hundred thousand simple steps. Reverse the list at the end to get the most significant digit first."],
    time="O(n &middot; D) where D = digits of n!", space="O(D)",
    solution='''def factorialDigits(n):
    digs = [1]
    for m in range(2, n + 1):
        carry = 0
        for i in range(len(digs)):
            carry, digs[i] = divmod(digs[i] * m + carry, 10)
        while carry:
            carry, d = divmod(carry, 10)
            digs.append(d)
    digs.reverse()
    return digs
''',
    tests=[[5], [10], [0], [1], [2], [20], [25], [100], [170], [300], [599], [600]],
)


def b_fact(n):
    import math
    return _dig(math.factorial(n))


def g_fact(r):
    return [r.randint(0, 40)]


def v_fact(tests):
    for t in tests:
        n = t["args"][0]
        assert 0 <= n <= 600 and _is_number(t["expected"])
        assert t["expected"] == b_fact(n)


CHECKS["factorial-as-digit-array"] = (b_fact, g_fact, "exact")
VALIDATE["factorial-as-digit-array"] = v_fact

p = add(
    id="sum-of-many-digit-arrays", title="Sum of Many Digit Arrays", diff="Medium", topic=TOPIC,
    fn="sumDigitArrays", params=[("nums", "int[][]")], ret="int[]", cmp="exact",
    desc=ENC + "<p><code>nums</code> is a list of big numbers, each stored as a digit array (the arrays may have different lengths). Return the digit array of their sum.</p>"
         "<p>Example: <code>nums = [[9,9],[9,9],[1]]</code> (99 + 99 + 1) gives <code>[1,9,9]</code>. Example: <code>nums = [[5],[0]]</code> gives <code>[5]</code>.</p>",
    constraints=["1 &le; nums.length &le; 200", "1 &le; nums[i].length &le; 100", "0 &le; nums[i][j] &le; 9, no leading zeros in a number except for [0]"],
    hints=["Adding the numbers one after another with a two-number addition works, but think about doing all of them in a single pass.",
           "Align all numbers on the right. Column sums can be larger than 9 by a lot (up to 9 &times; 200 plus a carry), so a carry is no longer just 0 or 1.",
           "First add up every column into one array of column sums (index from the right end). Then sweep once from the right: digit = <code>(sum + carry) % 10</code>, carry = <code>(sum + carry) // 10</code>, and flush the leftover carry at the end."],
    editorial=["Let W be the longest length. Create an array <code>cols</code> of W column sums where position W-1 is the units column. For each number, add its digits into the columns aligned to the right (a number of length L starts at column W-L).",
               "Then perform a single carry sweep from the units column: <code>v = cols[p] + carry</code>, output <code>v % 10</code>, carry <code>v // 10</code>. The carry can be several digits wide (at most about 1,800 here), so after the last column keep emitting digits while the carry is positive. Reverse the output. The total work is O(total number of digits) with a single carry sweep, instead of one full carry pass per added number."],
    time="O(total digits)", space="O(W)",
    solution='''def sumDigitArrays(nums):
    width = max(len(row) for row in nums)
    cols = [0] * width
    for row in nums:
        shift = width - len(row)
        for i, d in enumerate(row):
            cols[shift + i] += d
    res = []
    carry = 0
    for p in range(width - 1, -1, -1):
        carry, d = divmod(cols[p] + carry, 10)
        res.append(d)
    while carry:
        carry, d = divmod(carry, 10)
        res.append(d)
    while len(res) > 1 and res[-1] == 0:
        res.pop()
    res.reverse()
    return res
''',
    tests=[[[[9, 9], [9, 9], [1]]], [[[5], [0]]], [[[0]]], [[[0], [0], [0]]], [[[1, 2, 3]]], [[[9], [9], [9], [9], [9], [9], [9], [9], [9], [9]]],
           [[[1, 0, 0, 0], [9, 9, 9], [9, 9], [9]]], [[[7, 7, 7], [3], [2, 2]]], [[[9, 9, 9, 9, 9]] * 30]],
)
_r = rnd(1106)
p["tests"].append([[_rd(_r, _r.randint(1, 100)) for _ in range(150)]])
p["tests"].append([[[9] * 100 for _ in range(200)]])
p["tests"].append([[_rd9(_r, _r.randint(60, 100)) for _ in range(120)]])


def b_summany(nums):
    return _dig(sum(_num(x) for x in nums))


def g_summany(r):
    return [[_gd(r, 5) for _ in range(r.randint(1, 6))]]


def v_summany(tests):
    for t in tests:
        nums = t["args"][0]
        assert 1 <= len(nums) <= 200 and all(1 <= len(x) <= 100 and _is_number(x) for x in nums)
        assert _is_number(t["expected"]) and t["expected"] == b_summany(nums)


CHECKS["sum-of-many-digit-arrays"] = (b_summany, g_summany, "exact")
VALIDATE["sum-of-many-digit-arrays"] = v_summany

p = add(
    id="convert-digit-array-between-bases", title="Convert a Digit Array Between Bases", diff="Medium", topic=TOPIC,
    fn="convertBase", params=[("digits", "int[]"), ("fromBase", "int"), ("toBase", "int")], ret="int[]", cmp="exact",
    desc="<p>The array <code>digits</code> holds a non-negative integer written in base <code>fromBase</code>: the most significant digit comes first, every element is one digit with a value from <code>0</code> to <code>fromBase - 1</code> (digit values above 9 are plain integers, for example 35 in base 36). There are no leading zeros; zero is <code>[0]</code>.</p>"
         "<p>Return the same number written in base <code>toBase</code>, in the same format (no leading zeros, most significant digit first). The number can have hundreds of digits, so convert it without using a built-in big integer.</p>"
         "<p>Example: <code>digits = [1,0,1,0]</code>, <code>fromBase = 2</code>, <code>toBase = 10</code> gives <code>[1,0]</code>. Example: <code>digits = [2,5,5]</code>, <code>fromBase = 10</code>, <code>toBase = 16</code> gives <code>[15,15]</code>.</p>",
    constraints=["1 &le; digits.length &le; 400", "2 &le; fromBase, toBase &le; 36", "0 &le; digits[i] &lt; fromBase, no leading zeros except for [0]"],
    hints=["Converting by hand usually means dividing by the new base again and again and writing down the remainders.",
           "Repeatedly divide the whole digit array by <code>toBase</code> using long division carried out in <code>fromBase</code>. The remainder of each division is the next digit of the answer, starting with the least significant one.",
           "In one long-division pass: <code>v = rem * fromBase + digit</code>, the new digit is <code>v // toBase</code> and the new remainder is <code>v % toBase</code>. Repeat until the quotient is zero, then reverse the collected remainders."],
    editorial=["Treat the digit array as a number in base <code>fromBase</code> and divide it by <code>toBase</code> with schoolbook long division. For each digit, <code>v = rem * fromBase + digit</code> with <code>rem &lt; toBase</code>, so <code>v // toBase &lt; fromBase</code> is again a valid digit of the quotient. The final <code>rem</code> is the least significant digit in the target base.",
               "Keep dividing the quotient until it is all zeros (skip its leading zeros with a moving start index so the passes get shorter). The collected remainders are the answer in reverse order. The number of passes equals the number of output digits, so the cost is O(n &middot; m) for n input and m output digits. The input zero needs one pass and yields [0]."],
    time="O(n &middot; m)", space="O(n + m)",
    solution='''def convertBase(digits, fromBase, toBase):
    cur = list(digits)
    n = len(cur)
    start = 0
    out = []
    while start < n:
        rem = 0
        for i in range(start, n):
            v = rem * fromBase + cur[i]
            cur[i] = v // toBase
            rem = v % toBase
        out.append(rem)
        while start < n and cur[start] == 0:
            start += 1
    out.reverse()
    return out
''',
    tests=[[[1, 0, 1, 0], 2, 10], [[2, 5, 5], 10, 16], [[0], 7, 3], [[1], 2, 36], [[1, 2, 3], 10, 10], [[35, 35], 36, 2],
           [[1, 0, 0, 0, 0, 0, 0, 0], 2, 3], [[9, 9, 9, 9], 10, 2], [[1, 0], 36, 10], [[15, 14, 13], 16, 8]],
)
_r = rnd(1107)
p["tests"].append([_rd(_r, 400), 10, 2])
p["tests"].append([[1] + [_r.randint(0, 35) for _ in range(399)], 36, 2])
p["tests"].append([[1] + [_r.randint(0, 1) for _ in range(399)], 2, 36])
p["tests"].append([[1] + [_r.randint(0, 6) for _ in range(399)], 7, 13])


def b_base(digits, fb, tb):
    v = 0
    for d in digits:
        v = v * fb + d
    if v == 0:
        return [0]
    out = []
    while v:
        v, d = divmod(v, tb)
        out.append(d)
    return out[::-1]


def g_base(r):
    fb = r.randint(2, 36)
    tb = r.randint(2, 36)
    n = r.randint(1, 7)
    d = [r.randint(0, fb - 1) for _ in range(n)]
    if n > 1 and d[0] == 0:
        d[0] = r.randint(1, fb - 1)
    if r.random() < 0.1:
        d = [0]
    return [d, fb, tb]


def v_base(tests):
    for t in tests:
        d, fb, tb = t["args"]
        assert 1 <= len(d) <= 400 and 2 <= fb <= 36 and 2 <= tb <= 36
        assert all(0 <= x < fb for x in d) and (d[0] != 0 or d == [0])
        e = t["expected"]
        assert all(0 <= x < tb for x in e) and (e[0] != 0 or e == [0])
        assert e == b_base(d, fb, tb)


CHECKS["convert-digit-array-between-bases"] = (b_base, g_base, "exact")
VALIDATE["convert-digit-array-between-bases"] = v_base

p = add(
    id="add-negabinary-digit-arrays", title="Add Two Base -2 Numbers", diff="Medium", topic=TOPIC, tier="extra",
    fn="addNegabinary", params=[("a", "int[]"), ("b", "int[]")], ret="int[]", cmp="exact",
    desc="<p>A number can be written in base <strong>-2</strong>. An array of bits <code>[b<sub>k</sub>, ..., b<sub>1</sub>, b<sub>0</sub>]</code> (most significant bit first, every element 0 or 1) represents the value <code>b<sub>0</sub>&middot;(-2)<sup>0</sup> + b<sub>1</sub>&middot;(-2)<sup>1</sup> + b<sub>2</sub>&middot;(-2)<sup>2</sup> + ...</code>. For example <code>[1,1,0,1]</code> is -8 + 4 + 0 + 1 = -3. Every integer, positive or negative, has exactly one such representation without leading zeros; zero is <code>[0]</code>.</p>"
         "<p>Given two numbers <code>a</code> and <code>b</code> in this format, return their sum in the same format (no leading zeros). Do not convert to a built-in integer: the arrays can have thousands of bits.</p>"
         "<p>Example: <code>a = [1,1,1,1,1]</code> (11), <code>b = [1,0,1]</code> (5) gives <code>[1,0,0,0,0]</code> (16). Example: <code>a = [1]</code>, <code>b = [1]</code> gives <code>[1,1,0]</code> (4 - 2 + 0 = 2).</p>",
    constraints=["1 &le; a.length, b.length &le; 5,000", "a[i], b[i] are 0 or 1", "No leading zeros, except for the number zero stored as [0]"],
    hints=["Add bit by bit from the right with a carry, like binary addition. What changes in base -2?",
           "In a column the sum <code>s = a_i + b_i + carry</code> can be -1, 0, 1, 2 or 3. The digit you write is always <code>s mod 2</code> (0 or 1). A carry moves to a column whose weight is -2 times larger.",
           "Since <code>s = digit + (-2) * c</code>, the carry for the next column is <code>c = -(s - digit) / 2 = -(s >> 1)</code>. Keep going while a carry remains, then remove leading zeros."],
    editorial=["Do a normal column addition from the right. In column i we need <code>s = a_i + b_i + carry = digit + (-2) &middot; c</code> with digit in {0, 1}; then the unit of weight (-2)<sup>i</sup> contributes <code>digit</code> and the remainder moves to weight (-2)<sup>i+1</sup> as the value <code>c</code>. So <code>digit = s &amp; 1</code> and <code>c = -(s >> 1)</code> (arithmetic shift, rounding down).",
               "The carry only takes the values -1, 0, 1: s = -1 gives digit 1 and carry 1; s = 2 gives digit 0 and carry -1; s = 3 gives digit 1 and carry -1. Continue while there are bits left or a carry is non-zero, then strip leading zeros (a sum like 1 + (-1) = 0 produces them) keeping one 0. Linear time."],
    time="O(n + m)", space="O(n + m)",
    solution='''def addNegabinary(a, b):
    i, j = len(a) - 1, len(b) - 1
    carry = 0
    res = []
    while i >= 0 or j >= 0 or carry:
        s = carry
        if i >= 0:
            s += a[i]
            i -= 1
        if j >= 0:
            s += b[j]
            j -= 1
        res.append(s & 1)
        carry = -(s >> 1)
    while len(res) > 1 and res[-1] == 0:
        res.pop()
    res.reverse()
    return res
''',
    tests=[[[1, 1, 1, 1, 1], [1, 0, 1]], [[1], [1]], [[0], [0]], [[1, 1], [1]], [[1, 1, 0, 1], [0]], [[1, 1], [1, 1, 0]],
           [[1, 0], [1, 0]], [[1, 1, 0, 1], [1, 0, 1, 1]], [[1, 1], [1, 1]], [[1, 0, 1, 0, 1], [1, 1, 0]]],
)
_r = rnd(1108)


def _nb(r, n):
    return [1] + [r.randint(0, 1) for _ in range(n - 1)]


p["tests"].append([_nb(_r, 5000), _nb(_r, 4500)])
p["tests"].append([[1, 1] * 2000, [1, 1] * 1999 + [1, 0]])
p["tests"].append([[1] + [0] * 3999, [1] + [0] * 3998])
p["tests"].append([_nb(_r, 3000), [1, 1] * 1500])


def _nb_val(d):
    v = 0
    w = 1
    for x in reversed(d):
        v += x * w
        w *= -2
    return v


def _nb_of(n):
    if n == 0:
        return [0]
    out = []
    while n:
        r_ = n % 2
        out.append(r_)
        n = (n - r_) // -2
    return out[::-1]


def b_negabin(a, b):
    return _nb_of(_nb_val(a) + _nb_val(b))


def g_negabin(r):
    def one():
        n = r.randint(1, 8)
        d = [r.randint(0, 1) for _ in range(n)]
        if n > 1 and d[0] == 0:
            d[0] = 1
        if r.random() < 0.08:
            d = [0]
        return d
    return [one(), one()]


def v_negabin(tests):
    for t in tests:
        a, b = t["args"]
        for x in (a, b):
            assert 1 <= len(x) <= 5000 and all(v in (0, 1) for v in x) and (x[0] != 0 or x == [0])
        e = t["expected"]
        assert all(v in (0, 1) for v in e) and (e[0] != 0 or e == [0])
        assert e == b_negabin(a, b)


CHECKS["add-negabinary-digit-arrays"] = (b_negabin, g_negabin, "exact")
VALIDATE["add-negabinary-digit-arrays"] = v_negabin

# ================================================================ HARD

p = add(
    id="divide-digit-arrays", title="Divide Two Digit Arrays", diff="Hard", topic=TOPIC, tier="extra",
    fn="divideDigitArrays", params=[("a", "int[]"), ("b", "int[]")], ret="int[]", cmp="exact",
    desc=ENC + "<p>Divide the big number <code>a</code> by the big number <code>b</code> and return the quotient rounded down, as a digit array (<code>[0]</code> if <code>a &lt; b</code>). <code>b</code> is never zero. Neither number fits in a machine integer, and you may not use a built-in big-integer type.</p>"
         "<p>Example: <code>a = [1,0,0,0,0]</code>, <code>b = [3,0,0]</code>: 10000 / 300 = 33.3..., so the answer is <code>[3,3]</code>. Example: <code>a = [4,2]</code>, <code>b = [4,3]</code> gives <code>[0]</code>.</p>",
    constraints=["1 &le; a.length, b.length &le; 400", "b is not [0]", "0 &le; a[i], b[i] &le; 9, no leading zeros except for [0]"],
    hints=["Long division with a single-digit divisor is easy. A multi-digit divisor needs a way to compare and subtract two digit arrays.",
           "Bring down the digits of <code>a</code> one at a time into a remainder array. Each quotient digit says how many times <code>b</code> fits into the current remainder.",
           "For each new digit: append it to the remainder (drop leading zeros), then while <code>remainder &ge; b</code> subtract <code>b</code> and count. The count is at most 9 because the remainder before appending was smaller than <code>b</code>. Comparison: a longer array is larger, equal lengths compare lexicographically."],
    editorial=["Simulate schoolbook long division. Maintain <code>rem</code>, the remainder of the prefix of <code>a</code> processed so far, always without leading zeros and always smaller than <code>b</code> before the next digit is brought down. After appending the next digit, <code>rem &lt; 10 &middot; b</code>, so at most nine subtractions of <code>b</code> bring it below <code>b</code> again; the number of subtractions is the next quotient digit.",
               "Each subtraction is a column subtraction with a borrow over the last len(b) digits of <code>rem</code> (a borrow may reach one digit further left when rem is one digit longer than b). After subtracting, strip leading zeros of <code>rem</code> so that the length comparison stays valid. Each of the at most n quotient steps does at most nine O(m) subtractions: O(9 &middot; n &middot; m). Finally strip leading zeros of the quotient. A faster approach would estimate each quotient digit from the leading digits (Knuth's algorithm D) but is not needed here."],
    time="O(n &middot; m)", space="O(n + m)",
    solution='''def divideDigitArrays(a, b):
    m = len(b)
    rem = []
    q = []
    for d in a:
        if rem or d:
            rem.append(d)
        cnt = 0
        while len(rem) > m or (len(rem) == m and rem >= b):
            borrow = 0
            j = m - 1
            for i in range(len(rem) - 1, len(rem) - m - 1, -1):
                v = rem[i] - b[j] - borrow
                j -= 1
                if v < 0:
                    v += 10
                    borrow = 1
                else:
                    borrow = 0
                rem[i] = v
            if borrow:
                rem[len(rem) - m - 1] -= 1
            k = 0
            while k < len(rem) and rem[k] == 0:
                k += 1
            del rem[:k]
            cnt += 1
        q.append(cnt)
    k = 0
    while k < len(q) - 1 and q[k] == 0:
        k += 1
    return q[k:]
''',
    tests=[[[1, 0, 0, 0, 0], [3, 0, 0]], [[4, 2], [4, 3]], [[0], [7]], [[7], [7]], [[1, 2, 3], [1]], [[9, 9, 9, 9, 9, 9], [9, 9, 9]],
           [[1, 0, 0, 0, 0, 0, 0], [9, 9, 9, 9]], [[5, 0, 0, 0, 1], [5, 0, 0, 0, 2]], [[8, 0, 0, 0, 0, 0, 0, 0], [8]],
           [[1, 2, 3, 4, 5, 6, 7, 8, 9, 0], [9, 8, 7, 6]]],
)
_r = rnd(1109)
p["tests"].append([_rd(_r, 400), _rd(_r, 120)])
p["tests"].append([_rd9(_r, 400), _rd9(_r, 200)])
p["tests"].append([_rd(_r, 400), [9] * 100])
p["tests"].append([[1] + [0] * 399, [1] + [0] * 150 + [1]])


def b_divarr(a, b):
    return _dig(_num(a) // _num(b))


def g_divarr(r):
    b = _gd(r, 4)
    while b == [0]:
        b = _gd(r, 4)
    return [_gd(r, 8), b]


def v_divarr(tests):
    for t in tests:
        a, b = t["args"]
        assert 1 <= len(a) <= 400 and 1 <= len(b) <= 400 and _is_number(a) and _is_number(b) and b != [0]
        assert _is_number(t["expected"]) and t["expected"] == b_divarr(a, b)


CHECKS["divide-digit-arrays"] = (b_divarr, g_divarr, "exact")
VALIDATE["divide-digit-arrays"] = v_divarr

p = add(
    id="next-palindrome-digit-array", title="Next Palindrome of a Digit Array", diff="Hard", topic=TOPIC,
    fn="nextPalindrome", params=[("digits", "int[]")], ret="int[]", cmp="exact",
    desc=ENC + "<p>Return the smallest palindromic number that is <strong>strictly greater</strong> than the number in <code>digits</code>. A number is a palindrome when its digit array reads the same forwards and backwards. The number itself may or may not be a palindrome.</p>"
         "<p>Example: <code>[1,2,3,4]</code> gives <code>[1,3,3,1]</code>. Example: <code>[1,2,9,2,1]</code> gives <code>[1,3,0,3,1]</code>. Example: <code>[9,9]</code> gives <code>[1,0,1]</code>.</p>",
    constraints=["1 &le; digits.length &le; 5,000", "0 &le; digits[i] &le; 9, no leading zeros except for [0]", "The answer can be one digit longer than the input"],
    hints=["A palindrome is decided by its left half (including the middle digit for odd lengths). Try mirroring the left half of the number to the right.",
           "If the mirrored number is larger than the original, it is the answer. Otherwise the left half must grow.",
           "Increase the left half (with the middle digit) by one, propagating carries through 9s, then mirror again. If the left half was all 9s, the number is 99...9 and the answer is <code>1 0...0 1</code> with one more digit."],
    editorial=["Mirror the left half onto the right half. Comparing lists of the same length is lexicographic, which equals numeric comparison, so we can check directly whether the mirrored array exceeds the input. If it does, no smaller palindrome greater than the input exists, because any palindrome with the same left half is this one and any with a smaller left half is smaller than the input.",
               "If not, the next candidate has the next larger left half. Increment the left half (digits 0..(n-1)//2) like Plus One: trailing 9s become 0 and the first non-9 digit grows by one. Mirror again. When the whole left half is 9s, the input must be 99...9 (any other number with an all-9 left half would have been beaten by its mirror), and the answer is 1, then n-1 zeros, then 1. Everything is linear in the number of digits."],
    time="O(n)", space="O(n)",
    solution='''def nextPalindrome(digits):
    n = len(digits)
    res = list(digits)
    for i in range(n // 2):
        res[n - 1 - i] = res[i]
    if res > digits:
        return res
    i = (n - 1) // 2
    while i >= 0 and res[i] == 9:
        res[i] = 0
        i -= 1
    if i < 0:
        return [1] + [0] * (n - 1) + [1]
    res[i] += 1
    for k in range(n // 2):
        res[n - 1 - k] = res[k]
    return res
''',
    tests=[[[1, 2, 3, 4]], [[1, 2, 9, 2, 1]], [[9, 9]], [[0]], [[9]], [[1, 1]], [[1, 2, 1]], [[1, 2, 9, 9]], [[8, 9, 9, 8]],
           [[1, 0, 0, 0, 0]], [[9, 9, 9, 9, 9]], [[2, 9, 9, 9, 9]], [[1, 9, 9, 1]]],
)
_r = rnd(1110)
p["tests"].append([_rd(_r, 5000)])
p["tests"].append([[9] * 5000])
p["tests"].append([[1] + [9] * 2000 + [0] * 500])  # left half is 1 followed by 9s; the mirror is smaller than the input
_h = _rd(_r, 2500)
p["tests"].append([_h + _h[::-1]])


def b_nextpal(digits):
    n = _num(digits) + 1
    while str(n) != str(n)[::-1]:
        n += 1
    return _dig(n)


def g_nextpal(r):
    d = _gd(r, 5)
    if r.random() < 0.3 and len(d) >= 2:  # make it close to a palindrome
        half = d[: (len(d) + 1) // 2]
        d = half + half[: len(d) // 2][::-1]
        if r.random() < 0.5:
            d[-1] = min(9, max(0, d[-1] + r.choice([-1, 1])))
    return [d]


def v_nextpal(tests):
    for t in tests:
        d = t["args"][0]
        assert 1 <= len(d) <= 5000 and _is_number(d)
        e = t["expected"]
        assert _is_number(e) and e == e[::-1] and _num(e) > _num(d)
        if len(d) <= 12:
            assert e == b_nextpal(d)


CHECKS["next-palindrome-digit-array"] = (b_nextpal, g_nextpal, "exact")
VALIDATE["next-palindrome-digit-array"] = v_nextpal
