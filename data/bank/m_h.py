"""Problems: approximation and rounding (floor, ceiling, rounding modes, fractions). See data/lib.py for the registry."""
import math
from bisect import bisect_left, bisect_right
from decimal import Decimal, ROUND_HALF_UP, localcontext
from fractions import Fraction
from math import gcd

from lib import add, rnd, CHECKS, VALIDATE, gen_arr  # noqa: F401

INT_MIN, INT_MAX = -(2 ** 31), 2 ** 31 - 1
MOD = 1_000_000_007

# ---------------------------------------------------------------- EASY

p = add(
    id="next-power-of-two-at-least", title="Next Power of Two", diff="Easy", topic="Math & Bit Manipulation",
    fn="nextPowerOfTwo", params=[("n", "int")], ret="int", cmp="exact",
    desc="<p>Given a positive integer <code>n</code>, return the smallest power of two that is greater than or equal to <code>n</code>. The powers of two are 1, 2, 4, 8, 16, and so on.</p><p>If <code>n</code> is already a power of two, return <code>n</code> itself.</p><pre>n = 1   -> 1\nn = 5   -> 8\nn = 16  -> 16\nn = 17  -> 32</pre>",
    constraints=["1 &le; n &le; 2<sup>30</sup>"],
    hints=["Start at 1 and keep doubling while the value is still below n. That works, but can you find the answer without a loop over the powers?",
           "Look at <code>m = n - 1</code> in binary. The answer is the single bit just above the highest set bit of <code>m</code>, or 1 when <code>m</code> is 0.",
           "Set every bit below the highest set bit of <code>m</code> by OR-ing <code>m</code> with shifted copies of itself (shifts of 1, 2, 4, 8 and 16 are enough for 32 bits). Then add 1."],
    editorial=["Doubling from 1 until the value reaches n finds the answer in at most 31 steps, which is already fast enough. The loop is easy to get right, so it makes a good reference point.",
               "A branch-free version works on <code>m = n - 1</code>. After smearing the highest set bit of <code>m</code> into every lower position, <code>m</code> becomes a run of ones, and <code>m + 1</code> is the next power of two. For <code>n = 1</code> the value <code>m</code> is 0 and the answer is 1. The same idea gives <code>n</code> back unchanged when <code>n</code> is already a power of two, because then <code>m</code> is all ones below that power."],
    time="O(1)", space="O(1)",
    solution='''def nextPowerOfTwo(n):
    m = n - 1
    m |= m >> 1
    m |= m >> 2
    m |= m >> 4
    m |= m >> 8
    m |= m >> 16
    return m + 1
''',
    tests=[[1], [2], [3], [4], [5], [7], [8], [9], [16], [17], [1000], [1023], [1024], [1025],
           [1073741824], [999999937]],
)


def b_npow2(n):
    v = 1
    while v < n:
        v *= 2
    return v


def g_npow2(r):
    n = r.randint(1, 2 ** 30) if r.random() < 0.4 else r.randint(1, 70)
    return [n]


def v_npow2(tests):
    for t in tests:
        assert 1 <= t["args"][0] <= 2 ** 30


CHECKS["next-power-of-two-at-least"] = (b_npow2, g_npow2, "exact")
VALIDATE["next-power-of-two-at-least"] = v_npow2

p = add(
    id="billed-seconds-rounded-up-blocks", title="Billing Rounded Up to Whole Blocks", diff="Easy", topic="Math & Bit Manipulation",
    fn="billedSeconds", params=[("durations", "int[]"), ("block", "int")], ret="int", cmp="exact",
    desc="<p>A phone plan bills every call in whole blocks of <code>block</code> seconds. A call that lasts <code>d</code> seconds is billed as the smallest whole number of blocks that covers it, so it is charged <code>ceil(d / block) * block</code> seconds. A call of 0 seconds is charged nothing.</p><p>Given the call lengths in <code>durations</code>, return the total number of billed seconds over all calls.</p><pre>durations = [1, 60, 61], block = 60  -> 60 + 60 + 120 = 240</pre>",
    constraints=["0 &le; durations.length &le; 1,000", "0 &le; durations[i] &le; 100,000", "1 &le; block &le; 3,600"],
    hints=["Work out the charge for one call first. How many blocks does a call of d seconds need?",
           "The number of blocks is the ceiling of d / block. Integer arithmetic can compute it without floats: <code>(d + block - 1) // block</code>.",
           "Multiply the block count by <code>block</code> to get the billed seconds, and add the charges of all calls."],
    editorial=["Each call is independent, so the answer is a sum of per-call charges. Only the charge of one call needs care: rounding up to a multiple of <code>block</code>. The trick <code>(d + block - 1) // block</code> rounds up for non-negative integers, and it gives 0 for a 0-second call, matching the rule.",
               "The total is at most 1,000 times about 100,000 seconds, which fits easily in a 32-bit integer."],
    time="O(n)", space="O(1)",
    solution='''def billedSeconds(durations, block):
    total = 0
    for d in durations:
        total += (d + block - 1) // block * block
    return total
''',
    tests=[[[1, 60, 61], 60], [[], 5], [[0], 7], [[0, 0], 1], [[7], 7], [[8], 7], [[1], 3600],
           [[3600, 3601], 3600], [[5, 10, 15, 20], 5], [[99, 100, 101], 1], [[12, 45, 90, 3], 30]],
)
_r = rnd(201)
p["tests"].append([[_r.randint(0, 100000) for _ in range(1000)], 60])
p["tests"].append([[_r.randint(0, 100000) for _ in range(1000)], 3600])


def b_billed(durations, block):
    return sum(math.ceil(Fraction(d, block)) * block for d in durations)


def g_billed(r):
    return [gen_arr(r, 0, 500, 0, 8), r.randint(1, 120)]


def v_billed(tests):
    for t in tests:
        durations, block = t["args"]
        assert len(durations) <= 1000 and 1 <= block <= 3600
        assert all(0 <= d <= 100000 for d in durations)


CHECKS["billed-seconds-rounded-up-blocks"] = (b_billed, g_billed, "exact")
VALIDATE["billed-seconds-rounded-up-blocks"] = v_billed

# ---------------------------------------------------------------- MEDIUM

p = add(
    id="rounded-mean-ties-away", title="Rounded Mean, Ties Away From Zero", diff="Medium", topic="Math & Bit Manipulation",
    fn="roundedMean", params=[("nums", "int[]")], ret="int", cmp="exact",
    desc="<p>Compute the arithmetic mean of the non-empty array <code>nums</code> and round it to the nearest integer. When the mean lies exactly halfway between two integers, round away from zero, so <code>2.5</code> becomes <code>3</code> and <code>-2.5</code> becomes <code>-3</code>.</p><p>Do not use floating-point numbers: the answer must be exact.</p><pre>[1, 2]       -> 1.5  -> 2\n[-1, -2]     -> -1.5 -> -2\n[1, 2, 3, 4] -> 2.5  -> 3</pre>",
    constraints=["1 &le; nums.length &le; 10,000", "-2<sup>31</sup> &le; nums[i] &le; 2<sup>31</sup> - 1"],
    hints=["The mean is sum / length. Keep the sum and the length as integers and avoid division until you have a reason to use it.",
           "Work with the absolute value of the sum and reapply the sign at the end. Then the question is only about rounding a non-negative fraction.",
           "For a non-negative fraction S / n, the nearest integer with ties rounded up is <code>(2 * S + n) // (2 * n)</code>."],
    editorial=["Let <code>S</code> be the sum and <code>n</code> the length. Rounding <code>S / n</code> to the nearest integer is the same as taking <code>floor(S / n + 1/2)</code>. Multiply through by <code>2n</code> to stay in integers: <code>floor((2S + n) / (2n))</code>. This rounds exact halves upward, which is exactly the rule for non-negative means.",
               "Negative means are handled by symmetry: round the magnitude, which turns a tie at <code>-2.5</code> into a tie at <code>2.5</code>, then restore the sign. Rounding the magnitude is what makes ties go away from zero. Python integers never overflow, but in fixed-width languages the sum can exceed 32 bits, so use 64-bit accumulators there."],
    time="O(n)", space="O(1)",
    solution='''def roundedMean(nums):
    s = sum(nums)
    n = len(nums)
    mag = (2 * abs(s) + n) // (2 * n)
    return mag if s >= 0 else -mag
''',
    tests=[[[1, 2]], [[-1, -2]], [[1, 2, 3, 4]], [[0]], [[-5, -6, -6, -7]], [[2147483647, 2147483647]],
           [[-2147483648, 2147483647]], [[7]], [[10, 11, 12]], [[0, 0, 0, 1]], [[-3, 0, 0, 0]], [[4, 5, 5, 5, 6, 6]]],
)
_r = rnd(202)
p["tests"].append([[_r.randint(INT_MIN, INT_MAX) for _ in range(3000)]])
p["tests"].append([[_r.randint(-50, 50) for _ in range(2000)]])


def b_rmean(nums):
    q = Fraction(sum(nums), len(nums))
    m = math.floor(abs(q) + Fraction(1, 2))
    return m if q >= 0 else -m


def g_rmean(r):
    return [[r.randint(-20, 20) for _ in range(r.randint(1, 9))]]


CHECKS["rounded-mean-ties-away"] = (b_rmean, g_rmean, "exact")

p = add(
    id="round-decimal-string-half-even", title="Round a Decimal String, Ties to Even", diff="Medium", topic="Math & Bit Manipulation",
    fn="roundHalfEven", params=[("value", "string")], ret="int", cmp="exact",
    desc="<p>The string <code>value</code> is a decimal number. It has an optional leading <code>-</code>, a whole part of digits, and an optional fractional part introduced by a dot.</p><p>Round the number to the nearest integer using banker's rounding: an exact tie (fraction exactly one half) goes to the even integer. Return the rounded integer.</p><pre>\"2.5\"     -> 2\n\"3.5\"     -> 4\n\"-2.5\"    -> -2\n\"2.5001\"  -> 3\n\"11.5\"    -> 12</pre>",
    constraints=["The whole part has at most 9 digits", "The fractional part, if present, has at most 1,000 digits", "The string matches -?[0-9]+(\\.[0-9]+)?"],
    hints=["Only the fractional part decides the rounding. Compare its first digit with 5, and check whether any later digit is non-zero.",
           "An exact tie happens when the first fractional digit is 5 and every later digit is 0. Only then does the parity of the whole part matter.",
           "Handle the sign by working with the digits as a magnitude. Round the magnitude up when the fraction is above one half, or is exactly one half and the whole part is odd, then reapply the sign."],
    editorial=["Parse the string into a whole part and a fraction without converting the decimal to a binary float, because floats cannot represent most decimals exactly. The integer part is <code>int(whole)</code>. The fraction is compared with one half: the first digit alone decides everything unless it is exactly 5.",
               "When the first fractional digit is 5, the value is a tie only if no later digit is non-zero. A tie rounds to the even neighbour, so the whole part is rounded up exactly when it is odd. Negative values follow the same rule on the magnitude, and a result of zero is simply 0."],
    time="O(L)", space="O(L)",
    solution='''def roundHalfEven(value):
    neg = value.startswith("-")
    body = value[1:] if neg else value
    whole, _, frac = body.partition(".")
    n = int(whole)
    first = int(frac[0]) if frac else 0
    rest_nonzero = frac[1:].strip("0") != ""
    if first > 5 or (first == 5 and rest_nonzero):
        up = True
    elif first == 5:
        up = n % 2 == 1
    else:
        up = False
    mag = n + (1 if up else 0)
    return -mag if neg else mag
''',
    tests=[["2.5"], ["3.5"], ["-2.5"], ["-3.5"], ["2.5000001"], ["-0.5"], ["0.5"], ["7"], ["10.50"], ["11.5"],
           ["12.500"], ["0.49999999"], ["-7.5"], ["999999999.5"], ["123456788." + "5" + "0" * 900],
           ["123456788." + "4" + "9" * 900]],
)


def b_half_even(value):
    return int(round(Fraction(value)))


def g_half_even(r):
    s = str(r.randint(0, 40))
    if r.random() < 0.8:
        digits = "".join(r.choice("0123456789") if r.random() < 0.5 else r.choice("05") for _ in range(r.randint(1, 4)))
        s += "." + digits
    if r.random() < 0.5:
        s = "-" + s
    return [s]


def v_half_even(tests):
    import re
    for t in tests:
        assert re.fullmatch(r"-?[0-9]+(\.[0-9]+)?", t["args"][0]), t["args"][0]


CHECKS["round-decimal-string-half-even"] = (b_half_even, g_half_even, "exact")
VALIDATE["round-decimal-string-half-even"] = v_half_even

p = add(
    id="round-to-significant-digits", title="Round to Significant Digits", diff="Medium", topic="Math & Bit Manipulation",
    fn="roundToSignificant", params=[("n", "int"), ("k", "int")], ret="int", cmp="exact",
    desc="<p>Round the integer <code>n</code> to <code>k</code> significant digits. Keep the <code>k</code> leading digits of <code>n</code> and replace every digit after them with a zero. When the first dropped part is exactly half of the rounding unit, round away from zero.</p><p>Return the rounded integer. Zero stays zero.</p><pre>n = 123456, k = 2  -> 120000\nn = 995, k = 2     -> 1000\nn = -4567, k = 1   -> -5000\nn = 125, k = 2     -> 130\nn = 7, k = 3       -> 7</pre>",
    constraints=["-10<sup>9</sup> &le; n &le; 10<sup>9</sup>", "1 &le; k &le; 10"],
    hints=["Count the digits of <code>|n|</code>. If there are at most <code>k</code> of them, nothing changes. Otherwise the digits to drop are the last <code>digits - k</code> ones.",
           "Let <code>p = 10<sup>digits - k</sup></code>. Then <code>|n| // p</code> is the kept part and <code>|n| % p</code> is the dropped part, which is compared with <code>p / 2</code>.",
           "Round the magnitude with <code>(|n| + p // 2) // p * p</code>, which rounds halves up. Then reapply the sign. Carries are automatic: 995 rounds to 1000."],
    editorial=["Only the magnitude matters for the digits, so work with <code>a = |n|</code> and restore the sign at the end. Let <code>d</code> be the number of digits of <code>a</code>. If <code>d &le; k</code>, the number already has at most <code>k</code> significant digits and is returned unchanged.",
               "Otherwise let <code>p = 10<sup>d - k</sup></code>. Adding <code>p // 2</code> before the integer division by <code>p</code> rounds half up: a remainder of at least <code>p / 2</code> carries into the kept digits. Since <code>d - k &ge; 1</code>, the value <code>p</code> is even, so <code>p // 2</code> is exact. A carry that overflows the digit count, such as 995 to 1000, still gives the right answer, because the result is still a multiple of <code>p</code> and has the right number of significant digits."],
    time="O(log n)", space="O(1)",
    solution='''def roundToSignificant(n, k):
    if n == 0:
        return 0
    a = abs(n)
    digits = len(str(a))
    if digits <= k:
        return n
    p = 10 ** (digits - k)
    r = (a + p // 2) // p * p
    return r if n > 0 else -r
''',
    tests=[[0, 1], [123456, 2], [995, 2], [-4567, 1], [125, 2], [-125, 2], [7, 3], [1000000000, 1],
           [999999999, 1], [-999999999, 9], [5, 1], [-5, 1], [1, 10], [1234, 4], [45, 1], [-44, 1]],
)


def b_sig(n, k):
    with localcontext() as c:
        c.prec = k
        c.rounding = ROUND_HALF_UP
        return int(+Decimal(n))


def g_sig(r):
    n = r.randint(-5000, 5000) if r.random() < 0.7 else r.randint(-10 ** 9, 10 ** 9)
    return [n, r.randint(1, 6)]


CHECKS["round-to-significant-digits"] = (b_sig, g_sig, "exact")

p = add(
    id="largest-remainder-seat-split", title="Seats by Largest Remainder", diff="Medium", topic="Math & Bit Manipulation",
    fn="apportionSeats", params=[("total", "int"), ("weights", "int[]")], ret="int[]", cmp="exact",
    desc="<p>Split <code>total</code> seats among several parties in proportion to their weights, using whole seats only. This is the largest remainder method:</p><ol><li>Let <code>S</code> be the sum of the weights. Give party <code>i</code> the floor of <code>total * weights[i] / S</code> seats.</li><li>Some seats are still unassigned, because each floor drops a fraction. Hand the leftover seats out one at a time to the parties with the largest fractional parts.</li><li>Break ties in the fractional parts in favour of the smaller index.</li></ol><p>Return the seats of every party in the original order.</p><pre>total = 10, weights = [1, 1, 1]  -> [4, 3, 3]\ntotal = 7,  weights = [3, 2, 1]  -> [4, 2, 1]</pre>",
    constraints=["0 &le; total &le; 1,000,000", "1 &le; weights.length &le; 2,000", "1 &le; weights[i] &le; 1,000,000"],
    hints=["The exact quota of party <code>i</code> is <code>total * weights[i] / S</code>. Its integer part is the floor, which you can compute with integer division.",
           "The fractional part of the quota is <code>(total * weights[i]) % S</code> divided by <code>S</code>. Compare these numerators directly to avoid fractions.",
           "Count the leftover seats as <code>total</code> minus the sum of the floors. Sort the indices by remainder, largest first, then by index, and give one extra seat to each of the first leftover-many indices."],
    editorial=["Every quota is a rational number with denominator <code>S</code>. Its floor is <code>total * w // S</code>. The floors sum to at most <code>total</code>, and the shortfall is always less than the number of parties, because each of the fractional parts is below 1.",
               "The remainders <code>(total * w) % S</code> are integers, so the ordering by fractional part is exact, with no floating point involved. Sorting the indices by <code>(-remainder, index)</code> implements the tie-break, and the first <code>leftover</code> indices each receive one extra seat. The work is O(n log n) for the sort, dominated by the sort of at most 2,000 parties."],
    time="O(n log n)", space="O(n)",
    solution='''def apportionSeats(total, weights):
    S = sum(weights)
    seats = [total * w // S for w in weights]
    left = total - sum(seats)
    order = sorted(range(len(weights)), key=lambda i: (-(total * weights[i] % S), i))
    for i in order[:left]:
        seats[i] += 1
    return seats
''',
    tests=[[10, [1, 1, 1]], [7, [3, 2, 1]], [0, [5, 9]], [1, [1]], [5, [2, 2, 2, 2]], [100, [1, 1000000]],
           [9, [4, 4, 1]], [11, [2, 3, 5, 7]], [6, [1, 2]], [13, [5, 5, 5, 1]]],
)
_r = rnd(203)
p["tests"].append([1000000, [_r.randint(1, 1000000) for _ in range(2000)]])
p["tests"].append([999999, [_r.randint(1, 1000000) for _ in range(1000)]])


def b_apportion(total, weights):
    S = sum(weights)
    quotas = [Fraction(total * w, S) for w in weights]
    seats = [math.floor(q) for q in quotas]
    left = total - sum(seats)
    order = sorted(range(len(weights)), key=lambda i: (-(quotas[i] - seats[i]), i))
    for i in order[:left]:
        seats[i] += 1
    return seats


def g_apportion(r):
    return [r.randint(0, 30), [r.randint(1, 6) for _ in range(r.randint(1, 5))]]


def v_apportion(tests):
    for t in tests:
        total, weights = t["args"]
        assert sum(t["expected"]) == total and len(weights) <= 2000
        assert all(x >= 0 for x in t["expected"])


CHECKS["largest-remainder-seat-split"] = (b_apportion, g_apportion, "exact")
VALIDATE["largest-remainder-seat-split"] = v_apportion

p = add(
    id="count-pairs-floor-quotient", title="Pairs With a Fixed Floored Quotient", diff="Medium", topic="Math & Bit Manipulation",
    fn="countFloorQuotientPairs", params=[("values", "int[]"), ("k", "int")], ret="int", cmp="exact",
    desc="<p>Given positive integers <code>values</code> and a non-negative integer <code>k</code>, count the ordered pairs of positions <code>(i, j)</code> with <code>i != j</code> such that <code>floor(values[i] / values[j]) = k</code>.</p><p>Positions are what matter: two equal values at different positions form a valid pair.</p><pre>values = [3, 6, 7, 2], k = 2  -> 2   (pairs (6, 3) and (7, 3))</pre>",
    constraints=["1 &le; values.length &le; 3,000", "1 &le; values[i] &le; 10<sup>9</sup>", "0 &le; k &le; 10<sup>9</sup>"],
    hints=["Checking every ordered pair works, but with 3,000 values that is about nine million checks. Fix the divisor <code>d = values[j]</code> and look for the dividends instead.",
           "For a fixed positive <code>d</code>, <code>floor(x / d) = k</code> exactly when <code>k * d &le; x &le; k * d + d - 1</code>. That is an interval of values.",
           "Sort the values and count the ones inside each interval with binary search. Then remove the case where <code>i = j</code>, which lands in the interval only when <code>k = 1</code>."],
    editorial=["Fix the divisor <code>d = values[j]</code>. The condition <code>floor(x / d) = k</code> means <code>k * d &le; x &le; k * d + d - 1</code>, an interval whose endpoints are known from <code>d</code> and <code>k</code>. Counting the sorted values inside that interval takes two binary searches, so the total is O(n log n) instead of O(n<sup>2</sup>).",
               "The count includes position <code>i = j</code> whenever <code>d</code> itself lies in the interval. That check is one comparison, and it is true only for <code>k = 1</code>, so the code subtracts it in that case. Positions with equal values are still counted, as the statement requires."],
    time="O(n log n)", space="O(n)",
    solution='''from bisect import bisect_left, bisect_right

def countFloorQuotientPairs(values, k):
    s = sorted(values)
    total = 0
    for d in values:
        lo = k * d
        hi = k * d + d - 1
        c = bisect_right(s, hi) - bisect_left(s, lo)
        if lo <= d <= hi:
            c -= 1
        total += c
    return total
''',
    tests=[[[3, 6, 7, 2], 2], [[1, 2, 4], 1], [[5], 0], [[1, 1], 1], [[2, 2, 2], 1], [[10, 3, 1, 7], 0],
           [[4, 9, 2, 8, 3], 3], [[6, 6, 6, 6], 0], [[1, 2, 3, 4, 5, 6], 2]],
)
_r = rnd(204)
p["tests"].append([[_r.randint(1, 10 ** 9) for _ in range(3000)], 0])
p["tests"].append([[_r.randint(1, 60) for _ in range(3000)], 1])


def b_fq(values, k):
    return sum(1 for i in range(len(values)) for j in range(len(values))
               if i != j and values[i] // values[j] == k)


def g_fq(r):
    return [[r.randint(1, 40) for _ in range(r.randint(1, 9))], r.randint(0, 4)]


CHECKS["count-pairs-floor-quotient"] = (b_fq, g_fq, "exact")

p = add(
    id="nth-digit-of-fraction", title="Nth Digit of a Fraction", diff="Medium", topic="Math & Bit Manipulation",
    fn="fractionDigit", params=[("p", "int"), ("q", "int"), ("n", "int")], ret="int", cmp="exact",
    desc="<p>Write <code>p / q</code> in decimal as <code>I.d<sub>1</sub>d<sub>2</sub>d<sub>3</sub>...</code>, where <code>I</code> is the integer part. Return the digit <code>d<sub>n</sub></code>, the <code>n</code>-th digit after the decimal point. Digits past the end of a terminating expansion are 0.</p><p>The expansion can be very long, so compute the digit directly instead of generating all the digits before it.</p><pre>p = 1, q = 3, n = 5  -> 3\np = 1, q = 8, n = 3  -> 5\np = 22, q = 7, n = 2 -> 4   (22 / 7 = 3.142857...)</pre>",
    constraints=["0 &le; p &le; 10<sup>9</sup>", "1 &le; q &le; 10<sup>9</sup>", "1 &le; n &le; 10<sup>9</sup>"],
    hints=["Long division produces the digits one at a time. The digit at position n depends only on the remainder left after n - 1 steps.",
           "That remainder is <code>(p * 10<sup>n-1</sup>) mod q</code>. Modular exponentiation computes it in O(log n) steps without producing the earlier digits.",
           "If <code>s</code> is that remainder, the next digit is <code>(10 * s) // q</code>. Python's <code>pow(10, n - 1, q)</code> gives the power modulo q."],
    editorial=["Let <code>x = p / q</code>. The digits after the point are fixed by the fractional part of <code>10<sup>n-1</sup> x</code>, and the nth digit is the integer part of <code>10</code> times that fractional part. Since <code>10<sup>n-1</sup> p = m q + s</code> with <code>0 &le; s &lt; q</code>, the fractional part of <code>10<sup>n-1</sup> x</code> is exactly <code>s / q</code>.",
               "So the digit is <code>(10 * s) // q</code> with <code>s = (p * 10<sup>n-1</sup>) mod q</code>. Modular exponentiation keeps every intermediate value below q squared, so a billion-sized n costs about 30 multiplications. Long division by hand gives the same digits and is useful as a brute force check."],
    time="O(log n)", space="O(1)",
    solution='''def fractionDigit(p, q, n):
    s = p * pow(10, n - 1, q) % q
    return 10 * s // q
''',
    tests=[[1, 3, 5], [1, 8, 3], [22, 7, 1], [22, 7, 2], [0, 5, 10], [5, 1, 1000], [999999999, 1000000000, 1],
           [1, 999999937, 1000000000], [1000000000, 999999999, 123456789], [7, 2, 1], [123, 1000, 2], [1, 6, 2]],
)


def b_fdig(p, q, n):
    r = p % q
    d = 0
    for _ in range(n):
        r *= 10
        d = r // q
        r %= q
    return d


def g_fdig(r):
    return [r.randint(0, 300), r.randint(1, 300), r.randint(1, 80)]


CHECKS["nth-digit-of-fraction"] = (b_fdig, g_fdig, "exact")

# ---------------------------------------------------------------- HARD

p = add(
    id="floor-sum-linear-mod", title="Sum of Floored Linear Values", diff="Hard", topic="Math & Bit Manipulation", tier="extra",
    fn="floorSumMod", params=[("n", "int"), ("m", "int"), ("a", "int"), ("b", "int")], ret="int", cmp="exact",
    desc="<p>Compute <code>S = sum of floor((a * i + b) / m)</code> for every integer <code>i</code> from <code>0</code> to <code>n - 1</code>, and return <code>S</code> modulo 1000000007.</p><p>The values of <code>n</code> and <code>a</code> can be large, so a loop over <code>i</code> is too slow. The answer for the example below is 4, because the terms are 0, 1, 1 and 2.</p><pre>n = 4, m = 3, a = 2, b = 1  -> 4</pre>",
    constraints=["0 &le; n &le; 10<sup>9</sup>", "1 &le; m &le; 10<sup>9</sup>", "0 &le; a &le; 10<sup>9</sup>", "0 &le; b &le; 10<sup>9</sup>"],
    hints=["A direct loop is O(n), and n can be a billion. Look for structure: when <code>a &lt; m</code> the quotient changes slowly as i grows.",
           "Write <code>a = qa * m + ra</code> and <code>b = qb * m + rb</code>. The parts with <code>qa</code> and <code>qb</code> are arithmetic sums with a closed form, which leaves a problem with smaller coefficients.",
           "What remains is a Euclid-like recursion: the top value <code>y = a * n + b</code> counts the lattice points under the line, and swapping the roles of <code>m</code> and <code>a</code> makes the step count logarithmic. Keep all values as exact integers and reduce modulo the prime at the end."],
    editorial=["This is the classic 'floor sum' algorithm, the same one used to count lattice points under a line. It works in O(log m) rounds, each shaped like one step of the Euclidean algorithm.",
               "In each round, first remove whole multiples: if <code>a &ge; m</code>, every term gains <code>floor(a / m)</code> times the index, which sums to <code>(n - 1) n / 2 * (a // m)</code>. If <code>b &ge; m</code>, every term gains <code>b // m</code>. After that <code>0 &le; a, b &lt; m</code>. The remaining sum counts lattice points under the line, and it equals the same kind of sum with <code>n</code> replaced by <code>y // m</code> and <code>m</code> and <code>a</code> swapped, where <code>y = a * n + b</code>. The loop ends when <code>y &lt; m</code>, because then every remaining term is 0.",
               "Python integers are exact, so the running total never overflows. Reduce it modulo 1000000007 once at the end."],
    time="O(log m)", space="O(1)",
    solution='''def floorSumMod(n, m, a, b):
    ans = 0
    while True:
        if a >= m:
            ans += (n - 1) * n // 2 * (a // m)
            a %= m
        if b >= m:
            ans += n * (b // m)
            b %= m
        y_max = a * n + b
        if y_max < m:
            break
        n, b = divmod(y_max, m)
        m, a = a, m
    return ans % 1000000007
''',
    tests=[[4, 3, 2, 1], [0, 5, 3, 4], [1, 1, 0, 0], [5, 2, 1, 0], [6, 4, 7, 9], [10, 7, 5, 3], [3, 1, 2, 5],
           [1000000000, 999999937, 999999999, 999999998], [123456789, 987654321, 555555555, 123456789],
           [1000000000, 1, 1000000000, 0], [1000000000, 2, 999999999, 1000000000], [999999999, 1000000000, 1, 1]],
)


def b_fsum(n, m, a, b):
    return sum((a * i + b) // m for i in range(n)) % MOD


def g_fsum(r):
    return [r.randint(0, 40), r.randint(1, 30), r.randint(0, 60), r.randint(0, 60)]


CHECKS["floor-sum-linear-mod"] = (b_fsum, g_fsum, "exact")

p = add(
    id="closest-fraction-with-denominator-limit", title="Closest Fraction With a Denominator Limit", diff="Hard", topic="Math & Bit Manipulation", tier="extra",
    fn="closestFraction", params=[("p", "int"), ("q", "int"), ("limit", "int")], ret="string", cmp="exact",
    desc="<p>Given the fraction <code>p / q</code>, find the fraction <code>a / b</code> whose value is closest to it, among all fractions with <code>a</code> a non-negative integer and <code>1 &le; b &le; limit</code>.</p><p>Ties are broken as follows: prefer the smaller denominator <code>b</code>; if the denominators are also equal, prefer the smaller numerator <code>a</code>. Report the answer in lowest terms as the string <code>\"a/b\"</code>, so a whole number is written as <code>\"a/1\"</code>.</p><pre>p = 7, q = 3, limit = 2  -> \"5/2\"   (5/2 is 1/6 away, 2/1 is 1/3 away)\np = 9, q = 4, limit = 3  -> \"7/3\"\np = 1, q = 2, limit = 1  -> \"0/1\"   (0/1 and 1/1 tie; the smaller numerator wins)</pre>",
    constraints=["0 &le; p &le; 1,000,000", "1 &le; q &le; 1,000,000", "1 &le; limit &le; 20,000"],
    hints=["For a fixed denominator <code>b</code>, only the two numerators next to <code>p * b / q</code> can be closest. So you need at most two candidates per denominator.",
           "Compare distances exactly. The distance of <code>a / b</code> from <code>p / q</code> is <code>|a * q - p * b| / (b * q)</code>, and two such distances can be compared by cross-multiplying.",
           "Go through the denominators in increasing order and replace the best candidate only on a strictly smaller distance. Try the floor numerator before the ceiling one, and reduce the final fraction by the gcd."],
    editorial=["Any candidate <code>a / b</code> with a fixed <code>b</code> is best when <code>a</code> is the integer nearest to <code>p * b / q</code>, so only <code>floor(p * b / q)</code> and the next integer need checking. Over all denominators up to <code>limit</code> that is at most 40,000 candidates.",
               "Distances are rational, so compare them without floating point: the distance <code>nd / dd</code> is smaller than <code>best_nd / best_dd</code> exactly when <code>nd * best_dd &lt; best_nd * dd</code>. Because the denominators are scanned in increasing order and only a strictly better candidate replaces the current one, ties keep the smaller denominator. Within one denominator the smaller numerator is tried first and wins ties. Equal fractions with a larger denominator are never chosen, so the final answer is already in lowest terms, and the gcd only removes a common factor if one slipped through."],
    time="O(limit)", space="O(1)",
    solution='''from math import gcd

def closestFraction(p, q, limit):
    best_a, best_b = 0, 1
    best_nd, best_dd = None, None
    for b in range(1, limit + 1):
        lo = p * b // q
        for a in (lo, lo + 1):
            nd = abs(a * q - p * b)
            dd = b * q
            if best_nd is None or nd * best_dd < best_nd * dd:
                best_nd, best_dd, best_a, best_b = nd, dd, a, b
    g = gcd(best_a, best_b)
    return str(best_a // g) + "/" + str(best_b // g)
''',
    tests=[[7, 3, 2], [9, 4, 3], [1, 2, 1], [0, 5, 4], [5, 1, 3], [22, 7, 10], [1, 3, 1], [3, 7, 1],
           [314159, 100000, 5000], [987654, 333333, 20000], [1000000, 999983, 20000], [1, 1000000, 20000]],
)


def b_closest(p, q, limit):
    best = None
    for b in range(1, limit + 1):
        for a in range(0, p * b // q + 3):
            key = (abs(Fraction(a, b) - Fraction(p, q)), b, a)
            if best is None or key < best[0]:
                best = (key, a, b)
    f = Fraction(best[1], best[2])
    return str(f.numerator) + "/" + str(f.denominator)


def g_closest(r):
    return [r.randint(0, 60), r.randint(1, 40), r.randint(1, 25)]


CHECKS["closest-fraction-with-denominator-limit"] = (b_closest, g_closest, "exact")
