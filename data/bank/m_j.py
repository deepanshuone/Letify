"""Problems: math and bit manipulation (bit counts, XOR ranges, Gray code, digital roots, masks). See data/lib.py for the registry."""
from itertools import permutations
from math import comb

from lib import add, rnd, CHECKS, VALIDATE, gen_arr  # noqa: F401

INT_MIN, INT_MAX = -(2 ** 31), 2 ** 31 - 1
MOD = 1000000007


def _dr_slow(x):
    while x >= 10:
        x = sum(int(c) for c in str(x))
    return x


# ---------------------------------------------------------------- EASY

p = add(
    id="bit-difference-count", title="Differing Bits Between Two Integers", diff="Easy", topic="Math & Bit Manipulation",
    fn="differingBits", params=[("a", "int"), ("b", "int")], ret="int", cmp="exact",
    desc="<p>Given two non-negative integers <code>a</code> and <code>b</code>, count the bit positions at which they differ. Position 0 is the least significant bit.</p><p>Equivalently, count the set bits of <code>a ^ b</code>.</p><pre>a = 1,  b = 4   -> 2   (001 and 100 differ at positions 0 and 2)\na = 10, b = 5   -> 4   (1010 and 0101 differ everywhere)\na = 7,  b = 7   -> 0</pre>",
    constraints=["0 &le; a &le; 2<sup>31</sup> - 1", "0 &le; b &le; 2<sup>31</sup> - 1"],
    hints=["Think about which bit positions differ, rather than about the two values themselves.",
           "The XOR of two numbers has a 1 bit exactly where they differ.",
           "Count the set bits of <code>a ^ b</code>. The trick <code>x &amp;= x - 1</code> clears the lowest set bit, so repeating it counts the bits."],
    editorial=["Two bits differ exactly when their XOR is 1, so the answer is the number of 1 bits in <code>a ^ b</code>. Since both inputs fit in 31 bits, the XOR also fits, and there are at most 31 bits to count.",
               "Counting by clearing the lowest set bit takes one step per set bit. Shifting through the 32 positions and comparing the two bits at each one is equally correct and just as short."],
    time="O(1)", space="O(1)",
    solution='''def differingBits(a, b):
    x = a ^ b
    count = 0
    while x:
        x &= x - 1
        count += 1
    return count
''',
    tests=[[1, 4], [5, 3], [7, 7], [0, 0], [0, 1], [10, 5], [2147483647, 0], [2147483647, 2147483646],
           [1, 2147483647], [123456789, 987654321], [1000000, 1000001], [4, 4], [2, 1]],
)


def b_diffbits(a, b):
    return sum(((a >> i) & 1) != ((b >> i) & 1) for i in range(32))


def g_diffbits(r):
    hi = INT_MAX if r.random() < 0.5 else 255
    return [r.randint(0, hi), r.randint(0, hi)]


def v_diffbits(tests):
    for t in tests:
        a, b = t["args"]
        assert 0 <= a <= INT_MAX and 0 <= b <= INT_MAX
        assert 0 <= t["expected"] <= 31


CHECKS["bit-difference-count"] = (b_diffbits, g_diffbits, "exact")
VALIDATE["bit-difference-count"] = v_diffbits

p = add(
    id="xor-of-integer-range", title="XOR of Every Integer in a Range", diff="Easy", topic="Math & Bit Manipulation",
    fn="xorRange", params=[("lo", "int"), ("hi", "int")], ret="int", cmp="exact",
    desc="<p>Given two integers <code>lo</code> and <code>hi</code>, return the bitwise XOR of every integer from <code>lo</code> to <code>hi</code> inclusive: <code>lo ^ (lo + 1) ^ ... ^ hi</code>.</p><p>The range can be long, so do not loop over it.</p><pre>lo = 1, hi = 3  -> 0   (1 ^ 2 ^ 3)\nlo = 2, hi = 4  -> 5   (2 ^ 3 ^ 4)\nlo = 0, hi = 5  -> 1</pre>",
    constraints=["0 &le; lo &le; hi &le; 10<sup>9</sup>"],
    hints=["Compute the XOR of <code>0..n</code> for small <code>n</code> by hand. Do you notice a pattern that repeats?",
           "Let <code>F(n)</code> be the XOR of <code>0..n</code>. Then the XOR of <code>lo..hi</code> is <code>F(hi) ^ F(lo - 1)</code>, because the numbers below <code>lo</code> cancel out.",
           "<code>F(n)</code> is <code>n</code> when <code>n % 4 == 0</code>, <code>1</code> when <code>n % 4 == 1</code>, <code>n + 1</code> when <code>n % 4 == 2</code>, and <code>0</code> when <code>n % 4 == 3</code>. Let <code>F(-1) = 0</code>."],
    editorial=["XOR cancels equal values, so the XOR of <code>0..n</code> depends only on <code>n</code> modulo 4. Pairing up the numbers as <code>(4k+1, 4k+2)</code>-style blocks shows that each block of four consecutive numbers starting at a multiple of four XORs to zero. What remains is the last few numbers, which gives the four cases of <code>F</code>.",
               "Because XOR is its own inverse, the XOR over <code>[lo, hi]</code> equals <code>F(hi)</code> XOR <code>F(lo - 1)</code>. Each query costs constant time regardless of how long the range is."],
    time="O(1)", space="O(1)",
    solution='''def xorRange(lo, hi):
    def prefix(n):
        if n < 0:
            return 0
        m = n % 4
        if m == 0:
            return n
        if m == 1:
            return 1
        if m == 2:
            return n + 1
        return 0
    return prefix(hi) ^ prefix(lo - 1)
''',
    tests=[[0, 0], [0, 1], [0, 2], [3, 3], [1, 3], [5, 9], [4, 7], [10, 10], [2, 4], [100, 200], [0, 5],
           [0, 1000000000], [999999999, 1000000000], [123456, 654321], [7, 1000000]],
)


def b_xorrange(lo, hi):
    x = 0
    for i in range(lo, hi + 1):
        x ^= i
    return x


def g_xorrange(r):
    lo = r.randint(0, 300)
    return [lo, lo + r.randint(0, 300)]


def v_xorrange(tests):
    for t in tests:
        lo, hi = t["args"]
        assert 0 <= lo <= hi <= 10 ** 9


CHECKS["xor-of-integer-range"] = (b_xorrange, g_xorrange, "exact")
VALIDATE["xor-of-integer-range"] = v_xorrange

# ---------------------------------------------------------------- MEDIUM

p = add(
    id="digital-root-count-in-range", title="Count Numbers With a Given Digital Root", diff="Medium", topic="Math & Bit Manipulation",
    fn="countDigitalRoot", params=[("lo", "int"), ("hi", "int"), ("d", "int")], ret="int", cmp="exact",
    desc="<p>The digital root of a positive integer is found by repeatedly replacing it with the sum of its decimal digits until a single digit remains. For example, 38 becomes 11 and then 2, so its digital root is 2.</p><p>Given <code>lo</code>, <code>hi</code> and a digit <code>d</code>, count the integers <code>x</code> with <code>lo &le; x &le; hi</code> whose digital root equals <code>d</code>. Do not loop over the range: it can contain two billion numbers.</p><pre>lo = 1,  hi = 20, d = 2 -> 3   (2, 11 and 20)\nlo = 10, hi = 18, d = 9 -> 1   (only 18)\nlo = 1,  hi = 9,  d = 9 -> 1   (only 9)</pre>",
    constraints=["1 &le; lo &le; hi &le; 2 * 10<sup>9</sup>", "1 &le; d &le; 9"],
    hints=["Count the qualifying numbers in <code>1..hi</code> and subtract the count in <code>1..lo-1</code>, so you only need a prefix count.",
           "The digital root of <code>x</code> equals <code>d</code> exactly when <code>x</code> leaves remainder <code>d</code> when divided by 9. A digital root of 9 corresponds to remainder 0.",
           "For a remainder <code>r</code>, the numbers <code>1..n</code> with <code>x % 9 == r</code> can be counted with integer division. For <code>r = 0</code> the number 0 must be excluded, because the sequence starts at 1."],
    editorial=["For a positive integer <code>x</code>, the digital root is <code>1 + (x - 1) % 9</code>, because repeated digit sums preserve the value modulo 9, and the only single digits with a given residue are 1 to 9. So digital root <code>d</code> is the same as <code>x mod 9 = d mod 9</code>.",
               "Let <code>r = d % 9</code>. The count of <code>x</code> in <code>[0, n]</code> with <code>x % 9 == r</code> is <code>(n - r) // 9 + 1</code> when <code>n &ge; r</code>, else 0. When <code>r = 0</code>, subtract one for <code>x = 0</code>. Define <code>upto(n)</code> this way and the answer is <code>upto(hi) - upto(lo - 1)</code>.",
               "The whole query takes constant time, and the intermediate results stay within the range of the answer, which is at most two billion."],
    time="O(1)", space="O(1)",
    solution='''def countDigitalRoot(lo, hi, d):
    r = d % 9

    def upto(n):
        if n <= 0:
            return 0
        total = (n - r) // 9 + 1 if n >= r else 0
        if r == 0:
            total -= 1
        return total

    return upto(hi) - upto(lo - 1)
''',
    tests=[[1, 20, 2], [10, 18, 9], [1, 1, 1], [1, 9, 9], [9, 9, 9], [1, 2000000000, 9], [1, 2000000000, 1],
           [2000000000, 2000000000, 2], [123456789, 987654321, 5], [500, 1500, 7], [1, 1000, 3],
           [99999, 100000, 1], [1, 9, 1], [7, 30, 8], [1, 9, 4]],
)


def b_droot_count(lo, hi, d):
    return sum(1 for x in range(lo, hi + 1) if _dr_slow(x) == d)


def g_droot_count(r):
    lo = r.randint(1, 400)
    return [lo, lo + r.randint(0, 400), r.randint(1, 9)]


def v_droot_count(tests):
    for t in tests:
        lo, hi, d = t["args"]
        assert 1 <= lo <= hi <= 2 * 10 ** 9 and 1 <= d <= 9
        assert 0 <= t["expected"] <= hi - lo + 1


CHECKS["digital-root-count-in-range"] = (b_droot_count, g_droot_count, "exact")
VALIDATE["digital-root-count-in-range"] = v_droot_count

p = add(
    id="total-hamming-distance-pairs", title="Total Bit Differences of All Pairs", diff="Medium", topic="Math & Bit Manipulation",
    fn="totalHamming", params=[("nums", "int[]")], ret="int", cmp="exact", tier="must",
    desc="<p>The Hamming distance between two integers is the number of bit positions at which they differ.</p><p>Given the array <code>nums</code>, return the sum of the Hamming distances over all pairs of indices <code>i &lt; j</code>. Equal values at different indices form separate pairs.</p><pre>nums = [4, 14, 2] -> 6   (distances 2, 2 and 2)\nnums = [4, 14, 4] -> 4   (distances 2, 0 and 2)</pre>",
    constraints=["1 &le; nums.length &le; 4,000", "0 &le; nums[i] &le; 2<sup>31</sup> - 1"],
    hints=["Comparing every pair of numbers bit by bit is too slow when there are thousands of numbers. Can you count per bit position instead?",
           "For a fixed bit position, suppose <code>c</code> numbers have that bit set. Then exactly <code>c * (n - c)</code> pairs differ at that position.",
           "Add <code>c * (n - c)</code> over all 31 bit positions. Each position takes one pass over the array."],
    editorial=["The total is the sum over pairs of the number of differing bit positions. Swap the order of the two sums: for each bit position, count the pairs whose two numbers disagree there. Pairs disagree at a position exactly when one number has the bit and the other does not, so with <code>c</code> ones and <code>n - c</code> zeros there are <code>c * (n - c)</code> such pairs.",
               "Every value fits in 31 bits, so there are 31 positions and the work is <code>O(31 n)</code>, which is linear. The answer is at most about 1.25 * 10<sup>8</sup> with the given limits, so it fits in 32 bits."],
    time="O(31 * n)", space="O(1)",
    solution='''def totalHamming(nums):
    n = len(nums)
    total = 0
    for bit in range(31):
        ones = 0
        for x in nums:
            ones += (x >> bit) & 1
        total += ones * (n - ones)
    return total
''',
    tests=[[[4, 14, 2]], [[4, 14, 4]], [[0]], [[2147483647]], [[0, 0, 0, 0]], [[1, 2, 3, 4, 5]],
           [[2147483647, 0]], [[7, 7, 7, 8]], [[1000000000, 1]], [[15, 0, 15]]],
)
_r = rnd(4401)
_a = [_r.randint(0, INT_MAX) for _ in range(4000)]
p["tests"].append([_a])
_a = [_r.randint(0, 1000) for _ in range(4000)]
p["tests"].append([_a])


def b_total_hamming(nums):
    return sum(bin(nums[i] ^ nums[j]).count("1") for i in range(len(nums)) for j in range(i + 1, len(nums)))


def g_total_hamming(r):
    n = r.randint(1, 9)
    hi = INT_MAX if r.random() < 0.5 else 15
    return [[r.randint(0, hi) for _ in range(n)]]


def v_total_hamming(tests):
    for t in tests:
        nums = t["args"][0]
        assert 1 <= len(nums) <= 4000
        assert all(0 <= x <= INT_MAX for x in nums)
        assert t["expected"] >= 0


CHECKS["total-hamming-distance-pairs"] = (b_total_hamming, g_total_hamming, "exact")
VALIDATE["total-hamming-distance-pairs"] = v_total_hamming

p = add(
    id="gray-code-flip-position-sum", title="Gray Code Bit-Flip Sum", diff="Medium", topic="Math & Bit Manipulation",
    fn="grayFlipSum", params=[("k", "int")], ret="int", cmp="exact",
    desc="<p>The reflected binary Gray code of an integer <code>i</code> is <code>g(i) = i ^ (i &gt;&gt; 1)</code>. Consecutive codes <code>g(0), g(1), g(2), ...</code> differ in exactly one bit.</p><p>For a given <code>k</code>, consider the <code>k</code> steps from <code>g(i-1)</code> to <code>g(i)</code> for <code>i = 1, 2, ..., k</code>. Each step flips exactly one bit; number the positions from 0 for the least significant bit. Return the sum of the flipped positions over these steps.</p><pre>k = 0 -> 0   (no steps)\nk = 1 -> 0   (0 to 1 flips bit 0)\nk = 2 -> 1   (the steps flip bits 0 and 1)\nk = 4 -> 3   (the steps flip bits 0, 1, 0 and 2)</pre>",
    constraints=["0 &le; k &le; 2 * 10<sup>9</sup>"],
    hints=["Write out <code>g(0)</code> to <code>g(8)</code> and look at which bit changes at each step.",
           "The bit that changes when moving to <code>g(i)</code> is the lowest set bit of <code>i</code>, so its position is the number of trailing zeros of <code>i</code>.",
           "Sum the trailing zero counts: for each <code>j &ge; 1</code>, the number of <code>i</code> in <code>1..k</code> divisible by <code>2<sup>j</sup></code> is <code>k // 2<sup>j</sup></code>. Add these counts up."],
    editorial=["Going from <code>g(i-1)</code> to <code>g(i)</code> flips the bit at position <code>t</code>, where <code>2<sup>t</sup></code> is the lowest set bit of <code>i</code>. A short check on small values confirms this, and it is why the Gray sequence is called a reflected code: the flips follow the ruler sequence 0, 1, 0, 2, 0, 1, 0, 3, ...",
               "Instead of adding the positions one at a time, count contributions by level. Position <code>t</code> is credited once for every <code>i</code> that is a multiple of <code>2<sup>t</sup></code>, and adding the credits for <code>t = 1, 2, ...</code> gives the answer, since <code>sum of ctz(i) = sum over j &ge; 1 of floor(k / 2<sup>j</sup>)</code>. The loop runs about log<sub>2</sub> k times."],
    time="O(log k)", space="O(1)",
    solution='''def grayFlipSum(k):
    total = 0
    p = 2
    while p <= k:
        total += k // p
        p *= 2
    return total
''',
    tests=[[0], [1], [2], [3], [4], [5], [8], [15], [16], [1000], [1023], [1024], [65536], [999999],
           [1073741824], [1999999999], [2000000000]],
)


def b_gray_flips(k):
    prev, total = 0, 0
    for i in range(1, k + 1):
        g = i ^ (i >> 1)
        total += (g ^ prev).bit_length() - 1
        prev = g
    return total


def g_gray_flips(r):
    return [r.randint(0, 600)]


def v_gray_flips(tests):
    for t in tests:
        k = t["args"][0]
        assert 0 <= k <= 2 * 10 ** 9
        assert 0 <= t["expected"] <= k


CHECKS["gray-code-flip-position-sum"] = (b_gray_flips, g_gray_flips, "exact")
VALIDATE["gray-code-flip-position-sum"] = v_gray_flips

p = add(
    id="byte-pairs-covering-all-bits", title="Byte Pairs That Cover Every Bit", diff="Medium", topic="Math & Bit Manipulation",
    fn="coveringPairs", params=[("vals", "int[]")], ret="int", cmp="exact",
    desc="<p>Each value in <code>vals</code> is an 8-bit pattern, between 0 and 255. Count the pairs of positions <code>i &lt; j</code> for which <code>vals[i] | vals[j]</code> equals 255, that is, every one of the 8 bits is set in at least one of the two values.</p><p>Equal values at different positions form separate pairs.</p><pre>vals = [255, 0]                  -> 1\nvals = [1, 2, 4, 8, 16, 32, 64, 128] -> 0\nvals = [240, 15, 15, 240, 255]   -> 8</pre>",
    constraints=["1 &le; vals.length &le; 5,000", "0 &le; vals[i] &le; 255"],
    hints=["Two bytes cover all 8 bits exactly when their bitwise OR (<code>|</code>) is 255.",
           "Count how many times each byte value occurs. The answer depends only on those 256 counts, not on the order of the array.",
           "For every unordered pair of byte values <code>a &lt; b</code> with <code>a | b == 255</code>, multiply their counts. The value 255 pairs with itself, and then the count is <code>f * (f - 1) / 2</code>."],
    editorial=["A pair covers the byte when every bit is present in at least one of its values. Equivalently the OR is 255. Since the condition depends only on the values, group equal values together with a frequency table of size 256.",
               "Walk over all pairs of byte values, at most 256 * 256 / 2 of them, and add the product of their frequencies whenever the OR is 255. Equal values can pair only when that value is 255, in which case any two of its copies form a pair. The table is built in one pass over the input, so the total time is linear in the array length plus a constant."],
    time="O(n + 256 * 256)", space="O(256)",
    solution='''def coveringPairs(vals):
    freq = [0] * 256
    for v in vals:
        freq[v] += 1
    total = 0
    for a in range(256):
        if freq[a] == 0:
            continue
        for b in range(a, 256):
            if freq[b] == 0 or (a | b) != 255:
                continue
            if a == b:
                total += freq[a] * (freq[a] - 1) // 2
            else:
                total += freq[a] * freq[b]
    return total
''',
    tests=[[[255, 0]], [[1, 2, 4, 8, 16, 32, 64, 128]], [[240, 15, 15, 240, 255]], [[255, 255, 255]], [[7]],
           [[0, 0, 0]], [[127, 128]], [[15, 240, 0, 255]], [[3, 252, 3, 252, 0, 255]], [[128, 127, 127, 128]]],
)
_r = rnd(4406)
_a = [_r.randint(0, 255) for _ in range(5000)]
p["tests"].append([_a])
_a = [_r.choice([127, 128, 255, 0, 1, 254]) for _ in range(5000)]
p["tests"].append([_a])


def b_cover_pairs(vals):
    return sum(1 for i in range(len(vals)) for j in range(i + 1, len(vals)) if (vals[i] | vals[j]) == 255)


def g_cover_pairs(r):
    n = r.randint(0, 10)
    return [[r.choice([0, 1, 15, 127, 128, 240, 254, 255, r.randint(0, 255)]) for _ in range(n)]]


def v_cover_pairs(tests):
    for t in tests:
        vals = t["args"][0]
        assert 1 <= len(vals) <= 5000
        assert all(0 <= v <= 255 for v in vals)
        assert t["expected"] >= 0


CHECKS["byte-pairs-covering-all-bits"] = (b_cover_pairs, g_cover_pairs, "exact")
VALIDATE["byte-pairs-covering-all-bits"] = v_cover_pairs

p = add(
    id="digital-root-range-sum-queries", title="Digital Root Sums Over Ranges", diff="Medium", topic="Math & Bit Manipulation",
    fn="digitalRootSums", params=[("queries", "int[][]")], ret="int[]", cmp="exact",
    desc="<p>The digital root of a positive integer is found by repeatedly replacing it with the sum of its decimal digits until a single digit remains. For example, 38 becomes 11 and then 2, so its digital root is 2.</p><p>Each query is a pair <code>[l, r]</code>. For each query, compute the sum of the digital roots of all integers from <code>l</code> to <code>r</code> inclusive, and return that sum modulo 1000000007. Return the answers in query order.</p><pre>queries = [[1, 9], [10, 18], [1, 20]] -> [45, 45, 93]\nqueries = [[5, 5]]                    -> [5]</pre>",
    constraints=["1 &le; queries.length &le; 2,000", "1 &le; l &le; r &le; 10<sup>9</sup>"],
    hints=["Summing digital roots one at a time is too slow when the ranges reach 10<sup>9</sup>. Define a prefix function <code>S(n)</code> that gives the sum for <code>1..n</code>, and answer each query as a difference.",
           "Nine consecutive integers have digital roots 1 through 9, one each, so every full block of nine contributes 45.",
           "The leftover <code>m = n % 9</code> numbers at the end of <code>1..n</code> have digital roots <code>1, 2, ..., m</code>, which add up to <code>m * (m + 1) / 2</code>."],
    editorial=["For positive <code>x</code> the digital root is <code>1 + (x - 1) % 9</code>. So the digital roots repeat with period 9, with values 1 through 9 in each period. Define <code>S(n) = 45 * (n // 9) + m * (m + 1) / 2</code> with <code>m = n % 9</code>, which is the sum over <code>1..n</code>.",
               "Each query is <code>S(r) - S(l - 1)</code>, reduced modulo 1000000007. The Python integers are exact, so the subtraction cannot overflow, and the modulo keeps the result inside 32 bits. Every query takes constant time."],
    time="O(q)", space="O(q)",
    solution='''MOD = 1000000007


def digitalRootSums(queries):
    def prefix(n):
        m = n % 9
        return 45 * (n // 9) + m * (m + 1) // 2

    out = []
    for l, r in queries:
        out.append((prefix(r) - prefix(l - 1)) % MOD)
    return out
''',
    tests=[[[[1, 9], [10, 18], [1, 20]]], [[[5, 5]]], [[[1, 1]]], [[[9, 9]]], [[[1, 1000000000]]],
           [[[999999999, 1000000000]]], [[[123456789, 987654321]]], [[[10, 10], [100, 200]]], [[[1, 8], [2, 2], [3, 30]]]],
)
_r = rnd(4411)
_qs = []
for _ in range(1500):
    _l = _r.randint(1, 10 ** 9)
    _qs.append([_l, _r.randint(_l, 10 ** 9)])
p["tests"].append([_qs])
_qs = []
for _ in range(1000):
    _l = _r.randint(1, 5000)
    _qs.append([_l, _l + _r.randint(0, 5000)])
p["tests"].append([_qs])


def b_dr_sums(queries):
    out = []
    for lo_, hi_ in queries:
        out.append(sum(_dr_slow(x) for x in range(lo_, hi_ + 1)) % MOD)
    return out


def g_dr_sums(r):
    qs = []
    for _ in range(r.randint(1, 4)):
        lo_ = r.randint(1, 300)
        qs.append([lo_, lo_ + r.randint(0, 300)])
    return [qs]


def v_dr_sums(tests):
    for t in tests:
        qs = t["args"][0]
        assert 1 <= len(qs) <= 2000
        for l, r_ in qs:
            assert 1 <= l <= r_ <= 10 ** 9
        assert len(t["expected"]) == len(qs)


CHECKS["digital-root-range-sum-queries"] = (b_dr_sums, g_dr_sums, "exact")
VALIDATE["digital-root-range-sum-queries"] = v_dr_sums

p = add(
    id="count-numbers-same-popcount-as-n", title="Numbers Up to N With the Same Bit Count", diff="Medium", topic="Math & Bit Manipulation",
    fn="countSameBitCount", params=[("n", "int")], ret="int", cmp="exact",
    desc="<p>Let <code>k</code> be the number of 1 bits in the binary form of <code>n</code>. Count the integers <code>x</code> with <code>1 &le; x &le; n</code> that also have exactly <code>k</code> bits set.</p><p>The range is too large to enumerate, so count combinatorially.</p><pre>n = 5 -> 2   (3 = 11 and 5 = 101)\nn = 8 -> 4   (1, 2, 4 and 8)\nn = 7 -> 1   (only 7 itself)</pre>",
    constraints=["1 &le; n &le; 2<sup>31</sup> - 1"],
    hints=["Group the numbers below <code>n</code> by the highest bit position where they differ from <code>n</code>. Such a number has a 0 where <code>n</code> has a 1, and it matches <code>n</code> above that position.",
           "If that position is <code>i</code>, the bits below it are completely free. Only the number of ones among those <code>i</code> bits matters, so it is a binomial coefficient.",
           "Walk the set bits of <code>n</code> from the top. With <code>seen</code> ones above the current bit, add <code>comb(i, k - seen)</code> when that is valid, then add 1 for <code>n</code> itself."],
    editorial=["Let <code>k</code> be the popcount of <code>n</code>. A number <code>x &lt; n</code> is determined by the highest position <code>i</code> where it differs from <code>n</code>; at that position <code>n</code> has a 1 and <code>x</code> has a 0. Above <code>i</code> the two agree, so <code>x</code> already has <code>seen</code> ones, where <code>seen</code> counts the set bits of <code>n</code> above <code>i</code>.",
               "The <code>i</code> lower bits of <code>x</code> are unconstrained, and <code>x</code> needs exactly <code>k - seen</code> ones among them, which gives <code>comb(i, k - seen)</code> choices. Summing this over the set bits of <code>n</code> counts every <code>x &lt; n</code>, and <code>n</code> itself is added at the end. The loop runs over at most 31 bit positions."],
    time="O(log n)", space="O(1)",
    solution='''from math import comb


def countSameBitCount(n):
    k = bin(n).count("1")
    total = 0
    seen = 0
    for i in range(n.bit_length() - 1, -1, -1):
        if (n >> i) & 1:
            need = k - seen
            if 0 <= need <= i:
                total += comb(i, need)
            seen += 1
    return total + 1
''',
    tests=[[1], [2], [3], [5], [7], [8], [255], [256], [1000], [1431655765], [2147483647], [1073741824],
           [123456789], [987654321], [1000000000]],
)


def b_same_pop(n):
    k = bin(n).count("1")
    return sum(1 for x in range(1, n + 1) if bin(x).count("1") == k)


def g_same_pop(r):
    return [r.randint(1, 4000)]


def v_same_pop(tests):
    for t in tests:
        n = t["args"][0]
        assert 1 <= n <= INT_MAX
        assert 1 <= t["expected"] <= n


CHECKS["count-numbers-same-popcount-as-n"] = (b_same_pop, g_same_pop, "exact")
VALIDATE["count-numbers-same-popcount-as-n"] = v_same_pop

# ---------------------------------------------------------------- HARD

p = add(
    id="max-product-disjoint-bits-pair", title="Largest Product of Two Bit-Disjoint Numbers", diff="Hard", topic="Math & Bit Manipulation",
    fn="maxDisjointProduct", params=[("nums", "int[]")], ret="int", cmp="exact", tier="extra",
    desc="<p>Two numbers are <em>bit-disjoint</em> when their bitwise AND (<code>&amp;</code>) is 0, meaning they never have a 1 bit in the same position.</p><p>Choose two different indices <code>i != j</code> whose values are bit-disjoint and maximise <code>nums[i] * nums[j]</code>. Return that maximum product, or 0 if no such pair exists.</p><pre>nums = [1, 2, 4, 8]   -> 32   (4 and 8)\nnums = [2, 4, 8, 3]   -> 32   (4 and 8)\nnums = [3, 5, 7]      -> 0    (every pair shares a bit)</pre>",
    constraints=["2 &le; nums.length &le; 5,000", "0 &le; nums[i] &le; 4095"],
    hints=["Checking all pairs takes quadratic time, which is too slow for 5,000 numbers. For a value <code>x</code>, which values are bit-disjoint with it?",
           "A value is disjoint from <code>x</code> exactly when it is a submask of the complement <code>4095 ^ x</code>. So let <code>best[m]</code> be the largest present value that is a submask of <code>m</code>; the best partner for <code>x</code> is <code>best[4095 ^ x]</code>.",
           "Compute <code>best</code> with the subset-sum (SOS) dynamic programme: for each bit <code>b</code>, every mask containing <code>b</code> takes the maximum of its own value and the value of the mask with <code>b</code> removed."],
    editorial=["Values fit in 12 bits, so let <code>FULL = 4095</code>. For any value <code>x</code>, the bit-disjoint values are exactly the submasks of <code>FULL ^ x</code>. Since the product grows with each factor, for a fixed <code>x</code> the best partner is the largest submask value present.",
               "Build <code>best[m]</code>, the largest present value that is a submask of <code>m</code>, for all 4096 masks with the SOS DP: initialise <code>best[v] = v</code> for present values, then for each bit <code>b</code> and each mask <code>m</code> with bit <code>b</code> set, update <code>best[m] = max(best[m], best[m without b])</code>. Then scan the distinct values. The DP costs <code>12 * 4096</code> steps and the scan is linear in the input.",
               "Zero is disjoint with everything, but it only gives products of 0, which is the default answer. Two equal values are never disjoint unless both are 0, so working with the distinct values is enough."],
    time="O(n + B * 2^B) with B = 12", space="O(2^B)",
    solution='''def maxDisjointProduct(nums):
    FULL = 4095
    present = set(nums)
    best = [-1] * 4096
    for v in present:
        best[v] = v
    for bit in range(12):
        for m in range(4096):
            if (m >> bit) & 1:
                if best[m ^ (1 << bit)] > best[m]:
                    best[m] = best[m ^ (1 << bit)]
    answer = 0
    for a in present:
        b = best[FULL ^ a]
        if b > 0:
            answer = max(answer, a * b)
    return answer
''',
    tests=[[[1, 2, 4, 8]], [[2, 4, 8, 3]], [[3, 5, 7]], [[0, 0]], [[0, 5]], [[4095, 0, 1]], [[15, 16]],
           [[1023, 1024, 3, 12]], [[7, 8, 8, 7, 0]], [[4095, 4095]]],
)
_r = rnd(4421)
_a = [_r.randint(0, 4095) for _ in range(5000)]
p["tests"].append([_a])
_a = [_r.randint(0, 63) for _ in range(5000)]
p["tests"].append([_a])


def b_disjoint_prod(nums):
    best = 0
    for i in range(len(nums)):
        for j in range(i + 1, len(nums)):
            if (nums[i] & nums[j]) == 0:
                best = max(best, nums[i] * nums[j])
    return best


def g_disjoint_prod(r):
    n = r.randint(2, 12)
    hi = r.choice([7, 63, 4095])
    return [[r.randint(0, hi) for _ in range(n)]]


def v_disjoint_prod(tests):
    for t in tests:
        nums = t["args"][0]
        assert 2 <= len(nums) <= 5000
        assert all(0 <= v <= 4095 for v in nums)
        assert 0 <= t["expected"] <= 4095 * 4095


CHECKS["max-product-disjoint-bits-pair"] = (b_disjoint_prod, g_disjoint_prod, "exact")
VALIDATE["max-product-disjoint-bits-pair"] = v_disjoint_prod

p = add(
    id="min-xor-sum-of-two-arrays", title="Minimum XOR Sum of Two Arrays", diff="Hard", topic="Math & Bit Manipulation",
    fn="minXorSum", params=[("a", "int[]"), ("b", "int[]")], ret="int", cmp="exact",
    desc="<p>Two arrays <code>a</code> and <code>b</code> have the same length <code>n</code>. Pair every element of <code>a</code> with a different element of <code>b</code>, so that each element of <code>b</code> is used exactly once. The cost of a pair is the XOR of its two values, and the cost of a pairing is the sum of its pair costs.</p><p>Return the minimum possible total cost.</p><pre>a = [1, 2], b = [2, 3] -> 2   (pair 1 with 3 and 2 with 2: cost 2 + 0)\na = [5], b = [9]       -> 12</pre>",
    constraints=["1 &le; n &le; 12, where n = a.length = b.length", "0 &le; a[i], b[i] &le; 10<sup>6</sup>"],
    hints=["Try a recursion over the elements of <code>a</code>: element <code>i</code> is matched with some element of <code>b</code> that has not been used yet. What must the state remember?",
           "The only thing that matters is which elements of <code>b</code> are already used. The number of used <code>b</code> elements tells you which element of <code>a</code> comes next, so a bitmask over <code>b</code> is a sufficient state.",
           "Let <code>dp[mask]</code> be the minimum cost of matching the first <code>popcount(mask)</code> elements of <code>a</code> to the elements of <code>b</code> in <code>mask</code>. Extend each mask by one unused index of <code>b</code>."],
    editorial=["Any pairing matches <code>a[0]</code> with some <code>b</code>-element, then <code>a[1]</code> with another, and so on. The cost of the remaining choices depends only on which <code>b</code>-elements are still free, so memoising over subsets of <code>b</code> removes the factorial blow-up of trying all permutations.",
               "The DP has <code>2^n</code> states, and each state tries at most <code>n</code> extensions, so the work is <code>O(2^n * n)</code>, which is about 50,000 steps for <code>n = 12</code>. Every mask is reachable, since any subset of <code>b</code> can be matched with the first <code>|mask|</code> elements of <code>a</code>, and the answer is <code>dp[full]</code>."],
    time="O(2^n * n)", space="O(2^n)",
    solution='''def minXorSum(a, b):
    n = len(a)
    INF = 10 ** 18
    full = 1 << n
    dp = [INF] * full
    dp[0] = 0
    for mask in range(full):
        cur = dp[mask]
        if cur == INF:
            continue
        i = bin(mask).count("1")
        if i == n:
            continue
        for j in range(n):
            if not (mask >> j) & 1:
                nm = mask | (1 << j)
                c = cur + (a[i] ^ b[j])
                if c < dp[nm]:
                    dp[nm] = c
    return dp[full - 1]
''',
    tests=[[[1, 2], [2, 3]], [[5], [9]], [[0, 0, 0], [0, 0, 0]], [[1, 2, 3], [1, 2, 3]], [[1, 1, 1, 1], [2, 2, 2, 2]],
           [[1000000, 0], [0, 1000000]], [[7, 3, 9], [1, 8, 2]], [[12, 5, 0, 9, 4], [3, 3, 11, 6, 2]]],
)
_r = rnd(4431)
_a = [_r.randint(0, 10 ** 6) for _ in range(12)]
_b = [_r.randint(0, 10 ** 6) for _ in range(12)]
p["tests"].append([_a, _b])
_a = [_r.randint(0, 1000) for _ in range(12)]
_b = [_r.randint(0, 10 ** 6) for _ in range(12)]
p["tests"].append([_a, _b])
_a = [_r.randint(0, 10 ** 6) for _ in range(11)]
_b = list(_a)
_r.shuffle(_b)
p["tests"].append([_a, _b])


def b_minxor(a, b):
    n = len(a)
    return min(sum(a[i] ^ b[q[i]] for i in range(n)) for q in permutations(range(n)))


def g_minxor(r):
    n = r.randint(1, 6)
    a = [r.randint(0, 50) for _ in range(n)]
    b = [r.randint(0, 50) for _ in range(n)]
    return [a, b]


def v_minxor(tests):
    for t in tests:
        a, b = t["args"]
        assert 1 <= len(a) <= 12 and len(a) == len(b)
        assert all(0 <= v <= 10 ** 6 for v in a + b)
        assert t["expected"] >= 0


CHECKS["min-xor-sum-of-two-arrays"] = (b_minxor, g_minxor, "exact")
VALIDATE["min-xor-sum-of-two-arrays"] = v_minxor
