"""Problems: math and bit manipulation, counting and parity tricks. See data/lib.py for the registry."""
import math
from fractions import Fraction

from lib import add, rnd, CHECKS, VALIDATE, gen_arr  # noqa: F401

INT_MIN, INT_MAX = -(2 ** 31), 2 ** 31 - 1
MOD = 1000000007


# ---------------------------------------------------------------- EASY

p = add(
    id="count-squares-in-range", title="Perfect Squares in a Range", diff="Easy", topic="Math & Bit Manipulation",
    fn="countSquaresInRange", params=[("lo", "int"), ("hi", "int")], ret="int", cmp="exact",
    desc="<p>A perfect square is an integer of the form <code>k * k</code> for some integer <code>k &ge; 0</code>, so <code>0, 1, 4, 9, 16, ...</code> are perfect squares.</p><p>Given two integers <code>lo</code> and <code>hi</code>, return how many perfect squares lie in the closed range <code>[lo, hi]</code>.</p><pre>lo = 1, hi = 10 -> 3   (1, 4, 9)\nlo = 4, hi = 4  -> 1\nlo = 5, hi = 8  -> 0</pre>",
    constraints=["0 &le; lo &le; hi &le; 2<sup>31</sup> - 1"],
    hints=["Start with a single bound: how many perfect squares are there in [0, x]?",
           "The squares in [0, x] are k * k for k = 0, 1, ..., floor(sqrt(x)). So a range count is a difference of two such prefix counts.",
           "Use an exact integer square root such as <code>math.isqrt</code>, and handle <code>lo = 0</code> separately because there is nothing to subtract."],
    editorial=["Let f(x) be the number of perfect squares in [0, x]. The squares there are k * k with 0 &le; k * k &le; x, so k runs over 0 .. floor(sqrt(x)) and f(x) = floor(sqrt(x)) + 1 for x &ge; 0.",
               "The answer for [lo, hi] is f(hi) - f(lo - 1). When lo = 0 the subtracted term is 0, since there are no squares below 0.",
               "An exact integer square root avoids the rounding mistakes that a floating-point square root can make near perfect squares."],
    time="O(1)", space="O(1)",
    solution='''import math

def countSquaresInRange(lo, hi):
    below = math.isqrt(lo - 1) + 1 if lo > 0 else 0
    return math.isqrt(hi) + 1 - below
''',
    tests=[[0, 0], [1, 10], [4, 4], [5, 8], [0, 1], [1, 1], [16, 25], [9, 15], [17, 24], [100, 99999],
           [1000, 1000000], [0, 2147483647], [2147395600, 2147483647], [1, 2147483647]],
)


def b_sq(lo, hi):
    return sum(1 for k in range(0, 200) if lo <= k * k <= hi)


def g_sq(r):
    lo = r.randint(0, 3000)
    return [lo, lo + r.randint(0, 3000)]


def v_sq(tests):
    for t in tests:
        lo, hi = t["args"]
        assert 0 <= lo <= hi <= INT_MAX
        k = 0
        while k * k < lo:
            k += 1
        c = 0
        while k * k <= hi:
            c += 1
            k += 1
        assert c == t["expected"], (lo, hi)


CHECKS["count-squares-in-range"] = (b_sq, g_sq, "exact")
VALIDATE["count-squares-in-range"] = v_sq

p = add(
    id="two-exponent-in-factorial", title="Power of Two Dividing a Factorial", diff="Easy", topic="Math & Bit Manipulation",
    fn="twoExponentInFactorial", params=[("n", "int")], ret="int", cmp="exact",
    desc="<p>For a non-negative integer <code>n</code>, let <code>e</code> be the largest exponent such that <code>2<sup>e</sup></code> divides <code>n!</code>, the product <code>1 * 2 * ... * n</code> (with <code>0! = 1</code>). Return <code>e</code>.</p><p>The factorial is far too large to compute for big <code>n</code>, so count the factors of 2 directly.</p><pre>n = 5  -> 3    (5! = 120 = 8 * 15)\nn = 10 -> 8    (10! = 3628800 = 256 * 14175)\nn = 0  -> 0</pre>",
    constraints=["0 &le; n &le; 10<sup>9</sup>"],
    hints=["Only the even numbers contribute factors of 2, but they contribute several each. Do not multiply the numbers out.",
           "For each power 2<sup>i</sup>, count the multiples of 2<sup>i</sup> in 1..n. Each such multiple contributes one more factor of 2.",
           "The total is the sum of floor(n / 2<sup>i</sup>) for i &ge; 1. This sum equals n minus the number of 1 bits in n."],
    editorial=["A number m contributes one factor of 2 for each power 2<sup>i</sup> (i &ge; 1) that divides it. So the total exponent is the sum over i &ge; 1 of the number of multiples of 2<sup>i</sup> in [1, n], which is floor(n / 2) + floor(n / 4) + floor(n / 8) + ... (Legendre's formula).",
               "Write n in binary. floor(n / 2<sup>i</sup>) keeps only the bits of n at positions at least i, shifted down. A bit of n at position j therefore contributes 2<sup>j-1</sup> + 2<sup>j-2</sup> + ... + 1 = 2<sup>j</sup> - 1 to the sum over all i &ge; 1. Adding over the set bits gives n minus the number of 1 bits of n.",
               "So the answer is <code>n - popcount(n)</code>, computed in O(log n) time with a bit count. It is also the number of trailing zero bits of n!."],
    time="O(log n)", space="O(1)",
    solution='''def twoExponentInFactorial(n):
    return n - bin(n).count("1")
''',
    tests=[[0], [1], [2], [5], [8], [10], [16], [64], [100], [1023], [99999], [536870912], [1000000000],
           [999999999]],
)


def b_two(n):
    f = math.factorial(n)
    e = 0
    while f % 2 == 0:
        f //= 2
        e += 1
    return e


def g_two(r):
    return [r.randint(0, 300)]


def v_two(tests):
    for t in tests:
        n = t["args"][0]
        assert 0 <= n <= 10 ** 9
        assert 0 <= t["expected"] <= n


CHECKS["two-exponent-in-factorial"] = (b_two, g_two, "exact")
VALIDATE["two-exponent-in-factorial"] = v_two

p = add(
    id="clock-hand-smaller-angle", title="Smaller Angle Between Clock Hands", diff="Easy", topic="Math & Bit Manipulation",
    fn="clockAngleHalfDegrees", params=[("h", "int"), ("m", "int")], ret="int", cmp="exact",
    desc="<p>On an analog clock the hour hand and the minute hand both start at the top (12 o'clock) and move around continuously. Given a time written as hour <code>h</code> and minute <code>m</code>, return the smaller of the two angles between the hands. Here <code>12</code> means twelve o'clock.</p><p>To keep the answer an integer, return <strong>twice</strong> the angle in degrees, so a right angle is returned as <code>180</code>.</p><pre>h = 3,  m = 0  -> 180   (90 degrees)\nh = 3,  m = 20 -> 40    (20 degrees)\nh = 12, m = 0  -> 0</pre>",
    constraints=["1 &le; h &le; 12", "0 &le; m &le; 59"],
    hints=["Measure each hand from 12 o'clock in degrees. The minute hand moves 6 degrees per minute; the hour hand moves 30 degrees per hour plus 0.5 degrees per minute.",
           "Use half-degrees so that every value is an integer. The minute hand is at 12m half-degrees and the hour hand at 60h + m half-degrees, so their difference is 60h - 11m.",
           "The difference may be negative or larger than a full turn (720 half-degrees). Reduce it modulo 720 and take the shorter way round, that is min(d, 720 - d)."],
    editorial=["Work in half-degrees so that all values are integers. The minute hand sits at 12m half-degrees from 12 o'clock. The hour hand sits at 60(h mod 12) + m half-degrees, since it moves 30 degrees per hour plus half a degree per minute. Taking h mod 12 turns 12 into 0.",
               "The difference is d = |60(h mod 12) - 11m| reduced modulo 720, which is one full turn in half-degrees. The smaller angle is min(d, 720 - d), always between 0 and 360.",
               "Example: at 3:20 the difference is |180 - 220| = 40 half-degrees, which is 20 degrees."],
    time="O(1)", space="O(1)",
    solution='''def clockAngleHalfDegrees(h, m):
    d = abs(60 * (h % 12) - 11 * m) % 720
    return min(d, 720 - d)
''',
    tests=[[12, 0], [1, 0], [3, 0], [6, 0], [3, 20], [1, 5], [9, 45], [12, 30], [12, 59], [11, 59], [2, 11],
           [5, 25], [4, 35], [7, 0]],
)


def b_clock(h, m):
    hour = Fraction(h % 12) * 30 + Fraction(m, 2)
    minute = Fraction(6 * m)
    diff = (hour - minute) % 360
    angle = min(diff, 360 - diff)
    return int(2 * angle)


def g_clock(r):
    return [r.randint(1, 12), r.randint(0, 59)]


def v_clock(tests):
    for t in tests:
        h, m = t["args"]
        assert 1 <= h <= 12 and 0 <= m <= 59
        assert 0 <= t["expected"] <= 360


CHECKS["clock-hand-smaller-angle"] = (b_clock, g_clock, "exact")
VALIDATE["clock-hand-smaller-angle"] = v_clock

# ---------------------------------------------------------------- MEDIUM

p = add(
    id="bulbs-on-after-toggle-rounds", title="Bulb Switch Rounds", diff="Medium", topic="Math & Bit Manipulation",
    fn="bulbsOn", params=[("n", "int")], ret="int", cmp="exact", tier="must",
    desc="<p>A row of <code>n</code> bulbs, numbered <code>1</code> to <code>n</code>, starts switched off. The bulbs are switched in <code>n</code> rounds. In round <code>i</code> (for <code>i</code> from 1 to <code>n</code>), every bulb whose number is a multiple of <code>i</code> is toggled: an off bulb is switched on and an on bulb is switched off.</p><p>Return how many bulbs are on after round <code>n</code>.</p><pre>n = 3 -> 1   (after round 1 all are on; round 2 turns bulb 2 off; round 3 turns bulb 3 off)\nn = 4 -> 2   (bulbs 1 and 4 stay on)\nn = 0 -> 0</pre>",
    constraints=["0 &le; n &le; 10<sup>9</sup>"],
    hints=["Simulating the rounds with an array shows a pattern for small n. Which bulbs end up on?",
           "How many times is bulb j toggled? Once for each divisor of j, since round i touches bulb j exactly when i divides j.",
           "A bulb ends on when it is toggled an odd number of times. Divisors pair up around the square root of j, so only a perfect square has an odd number of divisors."],
    editorial=["Bulb j is toggled in round i exactly when i divides j. All divisors of j are at most j, and j is at most n, so every divisor's round happens. The number of toggles equals the number of divisors of j.",
               "Divisors pair up as d and j / d. The only divisor without a partner is sqrt(j), and that happens exactly when j is a perfect square. So bulb j is on at the end exactly when j is a perfect square.",
               "The answer is the number of perfect squares in [1, n], which is floor(sqrt(n)). <code>math.isqrt</code> gives it in constant time, with no simulation."],
    time="O(1)", space="O(1)",
    solution='''import math

def bulbsOn(n):
    return math.isqrt(n)
''',
    tests=[[0], [1], [2], [3], [4], [8], [10], [15], [16], [99], [1000], [123456789], [999999999], [1000000000]],
)


def b_bulb(n):
    on = [False] * (n + 1)
    for i in range(1, n + 1):
        for j in range(i, n + 1, i):
            on[j] = not on[j]
    return sum(on)


def g_bulb(r):
    return [r.randint(0, 400)]


def v_bulb(tests):
    for t in tests:
        n, e = t["args"][0], t["expected"]
        assert 0 <= n <= 10 ** 9
        assert e * e <= n < (e + 1) * (e + 1)


CHECKS["bulbs-on-after-toggle-rounds"] = (b_bulb, g_bulb, "exact")
VALIDATE["bulbs-on-after-toggle-rounds"] = v_bulb

p = add(
    id="clock-hand-overlap-count", title="Clock Hand Overlaps in a Time Window", diff="Medium", topic="Math & Bit Manipulation",
    fn="countHandOverlaps", params=[("a", "int"), ("b", "int")], ret="int", cmp="exact",
    desc="<p>Start a 12-hour analog clock at 12:00 at time <code>t = 0</code>, with the hour hand and the minute hand both pointing at 12. Time <code>t</code> is measured in minutes from that moment and may be any real number, not only whole minutes. The hands move continuously.</p><p>The two hands overlap whenever they point in the same direction. Given integers <code>a</code> and <code>b</code> with <code>a &le; b</code>, return how many moments <code>t</code> with <code>a &le; t &le; b</code> have overlapping hands. Count every overlap, including the one at <code>t = 0</code> if it lies in the range.</p><pre>a = 0, b = 0   -> 1\na = 1, b = 65  -> 0    (the next overlap is at about 65.45 minutes)\na = 1, b = 66  -> 1\na = 0, b = 720 -> 12</pre>",
    constraints=["0 &le; a &le; b &le; 10<sup>9</sup>"],
    hints=["The minute hand gains on the hour hand. By how many degrees per minute, and how long does it take to gain a full turn?",
           "The relative speed is 5.5 degrees per minute, so the hands overlap every 360 / 5.5 = 720 / 11 minutes, starting at t = 0.",
           "The overlap moments are the multiples of 720 / 11. Count the integers k with a &le; 720k / 11 &le; b, using ceiling and floor division on the integers 11a and 11b."],
    editorial=["Let t be minutes after 12:00. The minute hand turns 6 degrees per minute and the hour hand 0.5 degrees per minute, so the minute hand gains 5.5 degrees per minute. The hands coincide when 5.5t is a multiple of 360, that is at t = 720k / 11 for k = 0, 1, 2, ...",
               "We need the number of integers k &ge; 0 with 11a &le; 720k &le; 11b. The smallest such k is ceil(11a / 720) and the largest is floor(11b / 720), so the count is max(0, floor(11b / 720) - ceil(11a / 720) + 1).",
               "In Python, ceiling division is written as <code>-((-x) // y)</code>, which keeps everything in exact integer arithmetic. The answer is at most about 1.6 * 10<sup>7</sup>, well inside 32 bits."],
    time="O(1)", space="O(1)",
    solution='''def countHandOverlaps(a, b):
    first = -((-11 * a) // 720)
    last = (11 * b) // 720
    return max(0, last - first + 1)
''',
    tests=[[0, 0], [1, 65], [1, 66], [0, 720], [0, 1440], [5, 5], [720, 720], [100, 200], [66, 66], [0, 1000],
           [0, 1000000000], [123456789, 987654321], [999999999, 1000000000]],
)


def b_overlap(a, b):
    c = 0
    for s in range(11 * a, 11 * b + 1):
        t = Fraction(s, 11)
        gap = 6 * t - t / 2
        if gap % 360 == 0:
            c += 1
    return c


def g_overlap(r):
    a = r.randint(0, 100)
    return [a, a + r.randint(0, 100)]


def v_overlap(tests):
    for t in tests:
        a, b = t["args"]
        assert 0 <= a <= b <= 10 ** 9
        assert 0 <= t["expected"] <= 11 * b // 720 + 1


CHECKS["clock-hand-overlap-count"] = (b_overlap, g_overlap, "exact")
VALIDATE["clock-hand-overlap-count"] = v_overlap

p = add(
    id="total-set-bits-up-to-n", title="Total Set Bits From 0 to N", diff="Medium", topic="Math & Bit Manipulation",
    fn="totalSetBits", params=[("n", "int")], ret="int", cmp="exact",
    desc="<p>Write every integer from <code>0</code> to <code>n</code> inclusive in binary, and count the 1 bits across all of those representations together. The total can be large, so return it modulo <code>1000000007</code>.</p><pre>n = 0 -> 0\nn = 3 -> 4    (0, 1, 10 and 11 have 0, 1, 1 and 2 one-bits)\nn = 5 -> 7    (4 = 100 and 5 = 101 add 1 + 2 to the previous 4)</pre>",
    constraints=["0 &le; n &le; 10<sup>9</sup>"],
    hints=["Counting the bits of each number separately is too slow near n = 10<sup>9</sup>. Count bit by bit instead: for each bit position, how many numbers have that bit set?",
           "Bit i repeats in a cycle of length 2<sup>i+1</sup>. In each cycle the first 2<sup>i</sup> numbers have the bit off, and the next 2<sup>i</sup> have it on.",
           "Count the full cycles that fit into the m = n + 1 numbers, then add the part of the last partial cycle beyond its first half. Sum over all bit positions that can be set in a number up to n."],
    editorial=["Swap the order of the counting. Instead of summing popcounts number by number, sum for each bit position i how many numbers in [0, n] have that bit set.",
               "Bit i is set for x in the blocks [2<sup>i</sup>, 2<sup>i+1</sup>), [3 * 2<sup>i</sup>, 4 * 2<sup>i</sup>), and so on. The pattern has period P = 2<sup>i+1</sup>, and in each period the bit is set in the second half, which holds 2<sup>i</sup> numbers. With m = n + 1 numbers there are m // P full periods, contributing (m // P) * 2<sup>i</sup>, and the leftover r = m mod P adds max(0, r - 2<sup>i</sup>).",
               "A bit position only contributes when 2<sup>i</sup> &le; n, so at most 30 positions are visited. The exact total is at most about 1.5 * 10<sup>10</sup>; Python integers hold it exactly and the modulo is applied at the end."],
    time="O(log n)", space="O(1)",
    solution='''def totalSetBits(n):
    total = 0
    m = n + 1
    i = 0
    while (1 << i) <= n:
        block = 1 << (i + 1)
        half = 1 << i
        total += (m // block) * half + max(0, m % block - half)
        i += 1
    return total % 1000000007
''',
    tests=[[0], [1], [2], [3], [5], [8], [16], [100], [255], [1000], [999999999], [1000000000], [536870911]],
)


def b_bits(n):
    return sum(bin(x).count("1") for x in range(n + 1)) % 1000000007


def g_bits(r):
    return [r.randint(0, 800)]


def v_bits(tests):
    for t in tests:
        assert 0 <= t["args"][0] <= 10 ** 9
        assert 0 <= t["expected"] < MOD


CHECKS["total-set-bits-up-to-n"] = (b_bits, g_bits, "exact")
VALIDATE["total-set-bits-up-to-n"] = v_bits

p = add(
    id="count-even-popcount-up-to-n", title="Count Integers With an Even Number of One Bits", diff="Medium", topic="Math & Bit Manipulation",
    fn="countEvenPopcount", params=[("n", "int")], ret="int", cmp="exact",
    desc="<p>Count the integers <code>x</code> with <code>0 &le; x &le; n</code> whose binary representation contains an even number of 1 bits. Zero has no 1 bits, so it counts.</p><pre>n = 0 -> 1   (only 0)\nn = 3 -> 2   (0, and 3 = 11 in binary)\nn = 7 -> 4   (0, 3, 5 = 101 and 6 = 110)</pre>",
    constraints=["0 &le; n &le; 10<sup>9</sup>"],
    hints=["Make a small table of 0 to 7 with the number of 1 bits of each. Do you see a pattern in the parity of the counts?",
           "Go through the bits of n from the top. Each time n has a 1 at position i, you may place a 0 there instead and let the i lower bits take any value.",
           "If i is at least 1, exactly half of the 2<sup>i</sup> choices for the lower bits give an even total. Handle the lowest bit on its own, and finish by checking n itself."],
    editorial=["Walk down the bits of n from the top, keeping <code>ones</code>, the number of 1 bits in the prefix of n matched so far. A number below n is classified by the first position i where it differs from n. At that position n has a 1 and the number has a 0, the bits above i agree with n, and the i lower bits are free.",
               "The free bits give 2<sup>i</sup> numbers. If i &ge; 1, the lower bits have an even popcount for exactly half of them, so exactly 2<sup>i-1</sup> of them give an even total no matter what <code>ones</code> is. If i = 0 there is a single candidate, and it counts when <code>ones</code> is even.",
               "Finally n itself counts if its popcount is even. The loop runs over the bits of n, so the whole count takes O(log n) time."],
    time="O(log n)", space="O(1)",
    solution='''def countEvenPopcount(n):
    result = 0
    ones = 0
    for i in range(n.bit_length() - 1, -1, -1):
        if (n >> i) & 1:
            if i == 0:
                result += 1 if ones % 2 == 0 else 0
            else:
                result += 1 << (i - 1)
            ones += 1
    if ones % 2 == 0:
        result += 1
    return result
''',
    tests=[[0], [1], [2], [3], [6], [7], [8], [100], [255], [1000], [999999999], [1000000000], [536870911]],
)


def b_even(n):
    return sum(1 for x in range(n + 1) if bin(x).count("1") % 2 == 0)


def g_even(r):
    return [r.randint(0, 600)]


def v_even(tests):
    for t in tests:
        n = t["args"][0]
        assert 0 <= n <= 10 ** 9
        assert 0 <= t["expected"] <= n + 1


CHECKS["count-even-popcount-up-to-n"] = (b_even, g_even, "exact")
VALIDATE["count-even-popcount-up-to-n"] = v_even

p = add(
    id="nim-winning-first-moves", title="Winning First Moves in Nim", diff="Medium", topic="Math & Bit Manipulation",
    fn="winningFirstMoves", params=[("piles", "int[]")], ret="int", cmp="exact",
    desc="<p>Several piles of stones lie on the table. In a move, a player chooses one non-empty pile and removes at least one stone from it, so the pile becomes any size from 0 up to its current size minus 1. Players alternate. The player who cannot move, because every pile is empty, loses; equivalently, the player who takes the last stone wins.</p><p>Given the pile sizes <code>piles</code>, count the first moves that leave a position in which the second player, who moves next, is losing. A move is identified by its pile index and the new size of that pile, so each (pile, new size) pair is counted separately.</p><pre>piles = [1, 2]    -> 1   (reduce the 2-pile to 1)\npiles = [1, 2, 3] -> 0   (already a losing position for the player to move)\npiles = [5]       -> 1   (take all 5 stones)</pre>",
    constraints=["1 &le; piles.length &le; 1000", "0 &le; piles[i] &le; 10<sup>9</sup>"],
    hints=["Think about the position as a whole, not pile by pile. When is a position losing for the player who must move?",
           "A position is losing exactly when the XOR (<code>^</code>) of all pile sizes is 0. A move changes one pile from x to a smaller size.",
           "Let X be the XOR of all piles. To make the total XOR zero by changing pile x, its new size must be x ^ X, and that is a legal move only when x ^ X &lt; x. Count the piles for which this holds."],
    editorial=["This is Nim. The classic result (Bouton's theorem) says a position is losing for the player to move exactly when the XOR of the pile sizes is 0. From XOR 0 every move makes the XOR nonzero, and from a nonzero XOR some move always restores zero.",
               "Let X be the total XOR. Changing a single pile x to make the total zero requires its new size to be exactly x ^ X, so each pile offers at most one winning move. That move is legal only when x ^ X &lt; x. This holds precisely when the highest set bit of X is set in x: XOR with X clears that bit and leaves the higher bits of x unchanged, which makes the value smaller.",
               "So the answer is the number of piles with (x ^ X) &lt; x, found in one pass. When X is 0 no pile satisfies the test, so the formula gives 0 with no special case."],
    time="O(n)", space="O(1)",
    solution='''def winningFirstMoves(piles):
    total = 0
    for x in piles:
        total ^= x
    return sum(1 for x in piles if (x ^ total) < x)
''',
    tests=[[[1, 2]], [[1, 2, 3]], [[0]], [[5]], [[7, 7]], [[3, 5, 6]], [[1, 1, 1]], [[4, 8, 15, 16, 23, 42]],
           [[10, 10, 10, 10]], [[0, 0, 0]]],
)


def b_nim(piles):
    cnt = 0
    for i, x in enumerate(piles):
        for y in range(x):
            t = 0
            for j, z in enumerate(piles):
                t ^= y if j == i else z
            if t == 0:
                cnt += 1
    return cnt


def g_nim(r):
    return [[r.randint(0, 15) for _ in range(r.randint(1, 5))]]


def v_nim(tests):
    for t in tests:
        piles = t["args"][0]
        assert 1 <= len(piles) <= 1000 and all(0 <= x <= 10 ** 9 for x in piles)
        assert 0 <= t["expected"] <= len(piles)
        x = 0
        for v in piles:
            x ^= v
        if x == 0:
            assert t["expected"] == 0


CHECKS["nim-winning-first-moves"] = (b_nim, g_nim, "exact")
VALIDATE["nim-winning-first-moves"] = v_nim
_r = rnd(8801)
p["tests"].append([[_r.randint(0, 10 ** 9) for _ in range(1000)]])
_a = [_r.randint(0, 10 ** 9) for _ in range(999)]
_x = 0
for _v in _a:
    _x ^= _v
p["tests"].append([_a + [_x]])  # total XOR is 0, so no winning move
p["tests"].append([[_r.randint(0, 10 ** 9) for _ in range(1000)]])

p = add(
    id="pairs-with-square-product", title="Pairs Whose Product Is a Perfect Square", diff="Hard", topic="Math & Bit Manipulation",
    fn="countSquareProductPairs", params=[("nums", "int[]")], ret="int", cmp="exact",
    desc="<p>Given an integer array <code>nums</code>, count the pairs of indices <code>(i, j)</code> with <code>i &lt; j</code> such that the product <code>nums[i] * nums[j]</code> is a perfect square, meaning the square of some integer.</p><pre>nums = [2, 8, 9, 4, 6, 3] -> 2   (2 * 8 = 16 and 9 * 4 = 36)\nnums = [1, 4, 9, 16]      -> 6   (the product of any two of these squares is a square)\nnums = [2, 3, 5]          -> 0</pre>",
    constraints=["1 &le; nums.length &le; 3,000", "1 &le; nums[i] &le; 10<sup>6</sup>"],
    hints=["Factor each number into primes. When is a product a perfect square, in terms of the exponents of its primes?",
           "A product is a perfect square exactly when every prime appears with an even exponent. So reduce each number to its square-free part by removing every square factor.",
           "Two numbers have a square product exactly when their square-free parts are equal. Group the numbers by square-free part, and count the pairs inside each group."],
    editorial=["Write each number as x = k * s<sup>2</sup> where k is square-free, meaning no prime divides k twice. The parities of the prime exponents of x form exactly the pattern of k, and k is the square-free part of x.",
               "For x * y to be a perfect square, every prime must have an even total exponent. That means the exponent parities of x and y must match, which is the same as saying k(x) = k(y). So x * y is a perfect square exactly when the square-free parts are equal.",
               "To get the square-free part, trial-divide by primes up to 1000, since x is at most 10<sup>6</sup>. Keep each prime whose exponent is odd. Whatever remains has no prime factor below the trial bound, so it is 1 or a single prime. Then count groups with a hash map: a group of c equal keys gives c(c - 1) / 2 pairs. The trial division costs about 168 steps per number, and the answer is at most 4.5 * 10<sup>6</sup>."],
    time="O(n)", space="O(n)",
    solution='''def countSquareProductPairs(nums):
    limit = 1000
    sieve = bytearray([1]) * (limit + 1)
    sieve[0] = sieve[1] = 0
    primes = []
    for i in range(2, limit + 1):
        if sieve[i]:
            primes.append(i)
            for j in range(i * i, limit + 1, i):
                sieve[j] = 0

    def squarefree_part(x):
        k = 1
        for p in primes:
            if p * p > x:
                break
            if x % p == 0:
                e = 0
                while x % p == 0:
                    x //= p
                    e += 1
                if e % 2:
                    k *= p
        return k * x  # the leftover x is 1 or a single prime

    counts = {}
    for v in nums:
        key = squarefree_part(v)
        counts[key] = counts.get(key, 0) + 1
    return sum(c * (c - 1) // 2 for c in counts.values())
''',
    tests=[[[2, 8, 9, 4, 6, 3]], [[1, 4, 9, 16]], [[2, 3, 5]], [[1]], [[1, 1]], [[4, 9]], [[2, 2, 2]],
           [[12, 27, 48, 3, 75]], [[6, 6, 6, 6]], [[999999, 1000000, 1]]],
)


def b_sqprod(nums):
    c = 0
    n = len(nums)
    for i in range(n):
        for j in range(i + 1, n):
            prod = nums[i] * nums[j]
            s = math.isqrt(prod)
            if s * s == prod:
                c += 1
    return c


def g_sqprod(r):
    return [[r.randint(1, 60) for _ in range(r.randint(1, 12))]]


def v_sqprod(tests):
    for t in tests:
        nums = t["args"][0]
        n = len(nums)
        assert 1 <= n <= 3000 and all(1 <= x <= 10 ** 6 for x in nums)
        assert 0 <= t["expected"] <= n * (n - 1) // 2


CHECKS["pairs-with-square-product"] = (b_sqprod, g_sqprod, "exact")
VALIDATE["pairs-with-square-product"] = v_sqprod
_r = rnd(9901)
_kern = [2, 3, 5, 6, 7, 10, 11, 13, 14, 15, 17, 19, 21, 22, 23, 26, 29, 30]
_big = []
for _ in range(3000):
    _k = _r.choice(_kern)
    _s = _r.randint(1, int((10 ** 6 // _k) ** 0.5))
    _big.append(_k * _s * _s)
p["tests"].append([_big])
p["tests"].append([[_r.randint(1, 1000) ** 2 for _ in range(3000)]])  # every product is a square
p["tests"].append([[_r.randint(1, 10 ** 6) for _ in range(3000)]])

p = add(
    id="factorial-zero-preimage-count", title="Factorials With Exactly K Trailing Zeros", diff="Hard", topic="Math & Bit Manipulation",
    fn="countFactorialsWithZeros", params=[("k", "int")], ret="int", cmp="exact", tier="extra",
    desc="<p>Let <code>Z(n)</code> be the number of trailing zeros in the decimal form of <code>n!</code>, for a non-negative integer <code>n</code> with <code>0! = 1</code>, so <code>Z(0) = 0</code>. For example <code>Z(5) = 1</code> because <code>5! = 120</code>, and <code>Z(10) = 2</code> because <code>10! = 3628800</code>.</p><p>Given <code>k</code>, return how many non-negative integers <code>n</code> satisfy <code>Z(n) = k</code>.</p><pre>k = 0 -> 5   (n = 0, 1, 2, 3, 4)\nk = 1 -> 5   (n = 5, ..., 9)\nk = 5 -> 0   (no factorial ends in exactly five zeros)\nk = 6 -> 5   (n = 25, ..., 29)</pre>",
    constraints=["0 &le; k &le; 10<sup>9</sup>"],
    hints=["Each trailing zero comes from a factor 10 = 2 * 5, and the factors 5 are the scarce ones. Find a formula for Z(n) using the multiples of 5, 25, 125, and so on.",
           "Z never decreases, and it only changes when n is a multiple of 5. Binary search can find the smallest n with Z(n) at least k.",
           "Each multiple of 5 raises Z, so the n with Z(n) = k form a single block of consecutive numbers, or none at all. Check whether the smallest n with Z(n) at least k really gives exactly k."],
    editorial=["Z(n) = n // 5 + n // 25 + n // 125 + ... (Legendre's formula). Going from n - 1 to n, Z increases by the exponent of 5 in n, which is at least 1 exactly when 5 divides n. So Z is constant on each run 5m, 5m+1, ..., 5m+4 and strictly increases from one run to the next.",
               "Hence the set of n with Z(n) = k is either empty or exactly one such run of five numbers. Whether it is empty depends only on the value at the start of the run.",
               "Binary search for the smallest n with Z(n) &ge; k in the range [0, 5(k + 1)]. The upper end always works, because Z(5m) &ge; m. If Z at that n equals k the answer is 5, otherwise it is 0. The search takes O(log k) steps, each costing O(log n)."],
    time="O(log^2 k)", space="O(1)",
    solution='''def countFactorialsWithZeros(k):
    def zeros(n):
        c = 0
        while n:
            n //= 5
            c += n
        return c

    lo, hi = 0, 5 * (k + 1)
    while lo < hi:
        mid = (lo + hi) // 2
        if zeros(mid) >= k:
            hi = mid
        else:
            lo = mid + 1
    return 5 if zeros(lo) == k else 0
''',
    tests=[[0], [1], [5], [6], [10], [25], [30], [124], [126], [300], [999999999], [1000000000], [123456789]],
)


def b_pre(k):
    c = 0
    f = 1
    for n in range(0, 5 * k + 10):
        if n > 1:
            f *= n
        s = str(f)
        z = len(s) - len(s.rstrip("0"))
        if z == k:
            c += 1
    return c


def g_pre(r):
    return [r.randint(0, 60)]


def v_pre(tests):
    for t in tests:
        assert 0 <= t["args"][0] <= 10 ** 9
        assert t["expected"] in (0, 5)


CHECKS["factorial-zero-preimage-count"] = (b_pre, g_pre, "exact")
VALIDATE["factorial-zero-preimage-count"] = v_pre
