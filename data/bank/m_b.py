"""Problems: sequences and series (arithmetic, geometric, triangular, Fibonacci identities). See data/lib.py for the registry."""
import math
from math import isqrt

from lib import add, rnd, CHECKS, VALIDATE, gen_arr  # noqa: F401

INT_MAX = 2 ** 31 - 1
MOD = 1000000007


# ---------------------------------------------------------------- EASY

p = add(
    id="triangular-number-check", title="Triangular Number Check", diff="Easy", topic="Math & Bit Manipulation",
    fn="isTriangular", params=[("n", "int")], ret="bool", cmp="exact",
    desc="<p>The triangular numbers are <code>T<sub>k</sub> = 1 + 2 + ... + k = k(k + 1) / 2</code> for <code>k &ge; 0</code>, so they begin <code>0, 1, 3, 6, 10, 15, 21, ...</code></p><p>Given a non-negative integer <code>n</code>, return <code>true</code> if <code>n</code> is a triangular number and <code>false</code> otherwise.</p><pre>n = 10 -> true   (T<sub>4</sub> = 10)\nn = 11 -> false\nn = 0  -> true   (T<sub>0</sub> = 0)</pre>",
    constraints=["0 &le; n &le; 2<sup>31</sup> - 1"],
    hints=["You could list the triangular numbers one by one and stop once you reach or pass n. That works for small n, but can you decide with a formula?",
           "Multiply the equation k(k + 1) / 2 = n by 8 and add 1. The left side then becomes (2k + 1)<sup>2</sup>, a perfect square.",
           "So n is triangular exactly when 8n + 1 is a perfect square. Test that with an integer square root."],
    editorial=["Rewrite <code>n = k(k + 1) / 2</code> as <code>8n + 1 = (2k + 1)<sup>2</sup></code>. For a non-negative integer n, n is triangular precisely when 8n + 1 is a perfect square; the root of such a square is automatically odd, which is what k needs. Compute the integer square root r of 8n + 1 and check that r * r equals it.",
               "Python integers never overflow, so 8n + 1 is safe even when n is close to 2<sup>31</sup>; a fixed-width language would need a 64-bit type for the product. Walking the triangular numbers one by one would take O(sqrt n) steps, while the formula needs a constant amount of arithmetic."],
    time="O(1)", space="O(1)",
    solution='''from math import isqrt

def isTriangular(n):
    d = 8 * n + 1
    r = isqrt(d)
    return r * r == d
''',
    tests=[[0], [1], [2], [3], [6], [10], [11], [15], [21], [28], [29], [2147450880], [2147450881],
           [2147483647], [999999999]],
)


def b_tri(n):
    k = 0
    while k * (k + 1) // 2 < n:
        k += 1
    return k * (k + 1) // 2 == n


def g_tri(rg):
    if rg.random() < 0.5:
        k = rg.randint(0, 80)
        return [k * (k + 1) // 2]
    return [rg.randint(0, 3000)]


def v_tri(tests):
    for t in tests:
        assert 0 <= t["args"][0] <= INT_MAX
    assert any(t["expected"] for t in tests) and any(not t["expected"] for t in tests)


CHECKS["triangular-number-check"] = (b_tri, g_tri, "exact")
VALIDATE["triangular-number-check"] = v_tri

p = add(
    id="fibonacci-index-at-least", title="Fibonacci Index At Least N", diff="Easy", topic="Math & Bit Manipulation",
    fn="fibIndexAtLeast", params=[("n", "int")], ret="int", cmp="exact",
    desc="<p>The Fibonacci sequence used here starts <code>F<sub>1</sub> = 1</code> and <code>F<sub>2</sub> = 1</code>, and every later term is the sum of the two before it: <code>1, 1, 2, 3, 5, 8, 13, ...</code></p><p>Given a positive integer <code>n</code>, return the smallest index <code>k &ge; 1</code> such that <code>F<sub>k</sub> &ge; n</code>.</p><pre>n = 1       -> 1   (F<sub>1</sub> = 1)\nn = 2       -> 3   (F<sub>3</sub> = 2)\nn = 6       -> 6   (F<sub>5</sub> = 5 is too small, F<sub>6</sub> = 8)\nn = 832040  -> 30  (F<sub>30</sub> = 832040)</pre>",
    constraints=["1 &le; n &le; 10<sup>9</sup>"],
    hints=["Generate the Fibonacci numbers in order and count as you go until one is large enough.",
           "Only about 45 terms are needed before the values pass 10<sup>9</sup>, so a plain loop is fast.",
           "Keep the current term and the next term in two variables and advance both together."],
    editorial=["Walk the sequence from the start. Keep <code>a = F<sub>k</sub></code> and <code>b = F<sub>k+1</sub></code>; while a is smaller than n, shift the pair one step forward and increase k. The first k at which a reaches n is the answer.",
               "The terms grow exponentially, so the loop runs only about 45 times for n up to 10<sup>9</sup>. A binary search over precomputed terms would also work, but at this size it is not needed."],
    time="O(log n)", space="O(1)",
    solution='''def fibIndexAtLeast(n):
    k, a, b = 1, 1, 1  # a = F_k, b = F_(k+1)
    while a < n:
        a, b = b, a + b
        k += 1
    return k
''',
    tests=[[1], [2], [3], [4], [5], [6], [8], [9], [13], [14], [100], [832040], [832041], [999999999],
           [1000000000]],
)


def b_fib_idx(n):
    f = [0, 1]
    while len(f) < 60:
        f.append(f[-1] + f[-2])
    k = 1
    while f[k] < n:
        k += 1
    return k


def v_fib_idx(tests):
    f = [0, 1]
    while len(f) < 60:
        f.append(f[-1] + f[-2])
    for t in tests:
        n, k = t["args"][0], t["expected"]
        assert 1 <= n <= 10 ** 9
        assert f[k] >= n and f[k - 1] < n


CHECKS["fibonacci-index-at-least"] = (b_fib_idx, lambda rg: [rg.randint(1, 600)], "exact")
VALIDATE["fibonacci-index-at-least"] = v_fib_idx

# ---------------------------------------------------------------- MEDIUM

p = add(
    id="consecutive-sum-representations", title="Consecutive Sum Representations", diff="Medium", topic="Math & Bit Manipulation",
    fn="consecutiveSumWays", params=[("n", "int")], ret="int", cmp="exact",
    desc="<p>Some numbers can be written as a sum of consecutive positive integers, sometimes in several ways. Count the ways to write <code>n</code> as a sum of one or more consecutive positive integers. A single term (<code>n</code> itself) counts as one way. Two ways are different when their first term or their number of terms differs.</p><pre>n = 5  -> 2   (5, and 2 + 3)\nn = 8  -> 1   (only 8)\nn = 9  -> 3   (9, 4 + 5, 2 + 3 + 4)\nn = 15 -> 4   (15, 7 + 8, 4 + 5 + 6, 1 + 2 + 3 + 4 + 5)</pre>",
    constraints=["1 &le; n &le; 10<sup>9</sup>"],
    hints=["A run of k terms starting at a has sum k * a + k(k - 1) / 2. Try expressing a in terms of n and k.",
           "Multiply the sum by 2: 2n = k * (2a + k - 1). So the run length k is one factor of 2n, and the other factor is determined by it.",
           "The two factors have opposite parity, and each valid pair corresponds to one odd divisor of n. Count the odd divisors."],
    editorial=["A run of k terms starting at a sums to <code>k * a + k(k - 1) / 2</code>. Doubling gives <code>2n = k * m</code> with <code>m = 2a + k - 1</code>. Because a is at least 1, m is larger than k; and because m - k + 1 = 2a is even, k and m have opposite parity. Conversely, any factorization <code>2n = k * m</code> with k &lt; m and opposite parity gives a valid run with <code>a = (m - k + 1) / 2 &ge; 1</code>. So the ways correspond one-to-one with the factorizations of 2n into two factors of opposite parity.",
               "Write <code>n = 2<sup>e</sup> * o</code> with o odd. The even factor must carry all the powers of two, so the odd factor is an odd divisor d of o, and the pair is {d, 2n / d}. Each odd divisor gives exactly one way, so the answer is the number of odd divisors of n. Remove the factors of 2 and count the divisors of the odd part by trial division up to its square root, which costs O(sqrt n)."],
    time="O(sqrt n)", space="O(1)",
    solution='''def consecutiveSumWays(n):
    while n % 2 == 0:
        n //= 2
    ways = 1
    p = 3
    while p * p <= n:
        if n % p == 0:
            e = 0
            while n % p == 0:
                n //= p
                e += 1
            ways *= e + 1
        p += 2
    if n > 1:
        ways *= 2
    return ways
''',
    tests=[[1], [2], [3], [5], [8], [9], [15], [16], [45], [1000], [536870912], [735134400], [963761198],
           [999999937], [1000000000]],
)


def b_consec(n):
    count = 0
    for a in range(1, n + 1):
        s = 0
        x = a
        while s < n:
            s += x
            x += 1
        if s == n:
            count += 1
    return count


def v_consec(tests):
    for t in tests:
        assert 1 <= t["args"][0] <= 10 ** 9
        assert t["expected"] >= 1


CHECKS["consecutive-sum-representations"] = (b_consec, lambda rg: [rg.randint(1, 400)], "exact")
VALIDATE["consecutive-sum-representations"] = v_consec

p = add(
    id="geometric-series-sum-mod", title="Geometric Series Sum Modulo", diff="Medium", topic="Math & Bit Manipulation",
    fn="geometricSumMod", params=[("r", "int"), ("n", "int")], ret="int", cmp="exact",
    desc="<p>Compute the sum of the first <code>n</code> terms of the geometric sequence with first term 1 and ratio <code>r</code>:</p><p><code>S = 1 + r + r<sup>2</sup> + ... + r<sup>n-1</sup></code></p><p>Return <code>S</code> modulo <code>1,000,000,007</code>, as a value in the range <code>0 .. 1,000,000,006</code>. The true sum is far too large to compute directly.</p><pre>r = 2, n = 10         -> 1023\nr = 0, n = 5          -> 1   (the first term is 0<sup>0</sup> = 1)\nr = 1000000008, n = 3 -> 3   (r is congruent to 1 modulo the prime)</pre>",
    constraints=["0 &le; r &le; 2<sup>31</sup> - 1", "1 &le; n &le; 10<sup>9</sup>"],
    hints=["Split the sum in halves: the first 2m terms equal the first m terms plus r<sup>m</sup> times that same partial sum.",
           "Recurse on n / 2 while tracking r<sup>n</sup> alongside the partial sum; this takes O(log n) multiplications.",
           "Reduce r modulo 1,000,000,007 first, so that every intermediate value stays below the modulus."],
    editorial=["Let <code>S(k)</code> be the sum of the first k terms and <code>P(k) = r<sup>k</sup></code>. For even k = 2m, <code>S(2m) = S(m) * (1 + P(m))</code> and <code>P(2m) = P(m)<sup>2</sup></code>. For odd k, <code>S(k) = S(k-1) + P(k-1)</code> and <code>P(k) = P(k-1) * r</code>. Halving k computes both values in O(log n) multiplications, the same idea as fast exponentiation.",
               "The closed form <code>(r<sup>n</sup> - 1) / (r - 1)</code> is tempting, but it needs a modular inverse and breaks when r is congruent to 1 modulo the prime, which the sample with r = 1000000008 exercises. The doubling recursion has no such special case."],
    time="O(log n)", space="O(log n)",
    solution='''MOD = 1000000007

def geometricSumMod(r, n):
    r %= MOD

    def go(k):
        # returns (S(k), r^k) modulo MOD
        if k == 0:
            return 0, 1
        if k % 2 == 1:
            s, pw = go(k - 1)
            return (s + pw) % MOD, pw * r % MOD
        s, pw = go(k // 2)
        return (s + pw * s) % MOD, pw * pw % MOD

    return go(n)[0]
''',
    tests=[[2, 10], [0, 5], [1, 1], [1, 10], [1000000008, 3], [1000000007, 7], [1000000008, 1000000000],
           [2147483647, 999999999], [3, 1000000000], [2, 31], [7, 1], [0, 1]],
)


def b_geo(r, n):
    return sum(r ** i for i in range(n)) % MOD


def g_geo(rg):
    choices = [0, 1, 2, 3, 7, MOD, MOD + 1, MOD - 1, rg.randint(0, INT_MAX)]
    return [rg.choice(choices), rg.randint(1, 30)]


def v_geo(tests):
    for t in tests:
        r, n = t["args"]
        assert 0 <= r <= INT_MAX and 1 <= n <= 10 ** 9
        assert 0 <= t["expected"] < MOD


CHECKS["geometric-series-sum-mod"] = (b_geo, g_geo, "exact")
VALIDATE["geometric-series-sum-mod"] = v_geo

p = add(
    id="missing-triangular-numbers", title="Missing Triangular Numbers", diff="Medium", topic="Math & Bit Manipulation",
    fn="missingTriangular", params=[("nums", "int[]")], ret="int[]", cmp="exact",
    desc="<p>The triangular numbers are <code>1, 3, 6, 10, 15, 21, ...</code>, where the k-th one equals <code>1 + 2 + ... + k</code>.</p><p>You are given an array <code>nums</code> of distinct triangular numbers, in no particular order. Return every triangular number that is at least 1, is no larger than the largest value in <code>nums</code>, and does not appear in <code>nums</code>. Give them in increasing order. If <code>nums</code> is empty, return an empty array.</p><pre>nums = [1, 6, 10]                -> [3]\nnums = [15, 3, 6]                -> [1, 10]\nnums = [1, 3, 6, 10, 15, 21, 28] -> []</pre>",
    constraints=["0 &le; nums.length &le; 2,000", "Each nums[i] is a triangular number with 1 &le; nums[i] &le; 10<sup>6</sup>", "All values in nums are distinct"],
    hints=["List the triangular numbers up to the largest value in nums and check each one against nums.",
           "Store the values of nums in a hash set so that each membership test takes constant time.",
           "Generate the triangular numbers incrementally: the next one is the previous one plus the next integer."],
    editorial=["Let M be the largest value in nums; the answer only involves triangular numbers up to M. Generate them incrementally: T<sub>1</sub> = 1, and T<sub>k+1</sub> = T<sub>k</sub> + (k + 1). Put nums in a set and append each generated value that is missing from it. The output is already in increasing order because the sequence is generated that way.",
               "Every value is at most 10<sup>6</sup>, so there are only about 1,400 triangular numbers to examine. The algorithm runs in O(n + sqrt M) time with O(n) space for the set. Sorting nums and walking both sequences together is an equally good alternative."],
    time="O(n + sqrt(M))", space="O(n)",
    solution='''def missingTriangular(nums):
    if not nums:
        return []
    present = set(nums)
    top = max(nums)
    result = []
    t, k = 1, 1
    while t <= top:
        if t not in present:
            result.append(t)
        k += 1
        t += k
    return result
''',
    tests=[[[1, 6, 10]], [[15, 3, 6]], [[]], [[1]], [[3]], [[10, 1]], [[1, 3, 6, 10, 15, 21, 28]], [[28]],
           [[21, 1, 36]], [[36, 28, 21, 15, 10, 6, 3, 1, 45]]],
)
_r = rnd(601)
_ks = list(range(1, 1414)); _r.shuffle(_ks)  # T_1413 = 998991 is the largest one not above 10^6
p["tests"].append([[k * (k + 1) // 2 for k in _ks[:1000]]])
p["tests"].append([[k * (k + 1) // 2 for k in _ks[:300]]])


def b_missing_tri(nums):
    if not nums:
        return []
    top = max(nums)
    tri = [k * (k + 1) // 2 for k in range(1, 2000) if k * (k + 1) // 2 <= top]
    return [t for t in tri if t not in nums]


def g_missing_tri(rg):
    ks = rg.sample(range(1, 40), rg.randint(0, 15))
    arr = [k * (k + 1) // 2 for k in ks]
    rg.shuffle(arr)
    return [arr]


def v_missing_tri(tests):
    for t in tests:
        nums = t["args"][0]
        assert len(nums) <= 2000 and len(set(nums)) == len(nums)
        for x in nums:
            assert 1 <= x <= 10 ** 6
            assert isqrt(8 * x + 1) ** 2 == 8 * x + 1, "not triangular"


CHECKS["missing-triangular-numbers"] = (b_missing_tri, g_missing_tri, "exact")
VALIDATE["missing-triangular-numbers"] = v_missing_tri

p = add(
    id="fibonacci-square-sum-mod", title="Sum of Squared Fibonacci Numbers", diff="Medium", topic="Math & Bit Manipulation",
    fn="fibSquareSumMod", params=[("n", "int")], ret="int", cmp="exact",
    desc="<p>Let <code>F<sub>1</sub> = 1</code>, <code>F<sub>2</sub> = 1</code>, and <code>F<sub>i</sub> = F<sub>i-1</sub> + F<sub>i-2</sub></code>. Given <code>n</code>, compute <code>F<sub>1</sub><sup>2</sup> + F<sub>2</sub><sup>2</sup> + ... + F<sub>n</sub><sup>2</sup></code> modulo <code>1,000,000,007</code>.</p><pre>n = 3  -> 1 + 1 + 4 = 6\nn = 5  -> 1 + 1 + 4 + 9 + 25 = 40\nn = 10 -> 4895</pre>",
    constraints=["1 &le; n &le; 10<sup>9</sup>"],
    hints=["Adding the squares one at a time needs n steps, which is too slow for n = 10<sup>9</sup>. Compute the first few partial sums and look for a pattern.",
           "The partial sums are 1, 2, 6, 15, 40, ... Compare them with products of two neighbouring Fibonacci numbers.",
           "The identity says the sum equals F<sub>n</sub> * F<sub>n+1</sub>. Compute that pair modulo the prime with fast doubling."],
    editorial=["The partial sums for small n are 1, 2, 6, 15, 40, and these equal <code>F<sub>n</sub> * F<sub>n+1</sub></code>: 1*1, 1*2, 2*3, 3*5, 5*8. A short induction proves it: if the identity holds for n, then adding <code>F<sub>n+1</sub><sup>2</sup></code> gives <code>F<sub>n+1</sub>(F<sub>n</sub> + F<sub>n+1</sub>) = F<sub>n+1</sub>F<sub>n+2</sub></code>.",
               "So the answer is <code>F<sub>n</sub> * F<sub>n+1</sub></code> modulo the prime. Get the pair (F<sub>n</sub>, F<sub>n+1</sub>) with fast doubling: <code>F<sub>2k</sub> = F<sub>k</sub>(2F<sub>k+1</sub> - F<sub>k</sub>)</code> and <code>F<sub>2k+1</sub> = F<sub>k</sub><sup>2</sup> + F<sub>k+1</sub><sup>2</sup></code>. The subtraction is taken modulo the prime so that values stay non-negative. This takes O(log n) multiplications."],
    time="O(log n)", space="O(log n)",
    solution='''MOD = 1000000007

def fibPair(n):
    # returns (F_n, F_(n+1)) modulo MOD
    if n == 0:
        return 0, 1
    a, b = fibPair(n // 2)
    c = a * ((2 * b - a) % MOD) % MOD  # F_(2k)
    d = (a * a + b * b) % MOD          # F_(2k+1)
    if n % 2 == 0:
        return c, d
    return d, (c + d) % MOD

def fibSquareSumMod(n):
    fn, fn1 = fibPair(n)
    return fn * fn1 % MOD
''',
    tests=[[1], [2], [3], [5], [10], [11], [100], [1000], [65536], [123456789], [999999999], [1000000000],
           [4294967], [77777]],
)


def b_fss(n):
    a, b, s = 1, 1, 0
    for _ in range(n):
        s += a * a
        a, b = b, a + b
    return s % MOD


def v_fss(tests):
    for t in tests:
        assert 1 <= t["args"][0] <= 10 ** 9
        assert 0 <= t["expected"] < MOD


CHECKS["fibonacci-square-sum-mod"] = (b_fss, lambda rg: [rg.randint(1, 300)], "exact")
VALIDATE["fibonacci-square-sum-mod"] = v_fss

p = add(
    id="fibonacci-mod-period", title="Fibonacci Modulo Period", diff="Medium", topic="Math & Bit Manipulation",
    fn="pisanoPeriod", params=[("m", "int")], ret="int", cmp="exact",
    desc="<p>Reduce the Fibonacci sequence modulo <code>m</code>: it begins <code>0, 1, 1, 2, 3, ...</code> and each term is the sum of the two before it, taken modulo <code>m</code>. Each term depends only on the previous two, so the sequence eventually returns to the pair <code>0, 1</code>.</p><p>The Pisano period <code>&pi;(m)</code> is the smallest <code>p &ge; 1</code> such that <code>F<sub>p</sub></code> is congruent to 0 and <code>F<sub>p+1</sub></code> is congruent to 1 modulo <code>m</code>. Return <code>&pi;(m)</code>.</p><pre>m = 2  -> 3   (0 1 1 0 1 1 ...)\nm = 3  -> 8\nm = 10 -> 60</pre>",
    constraints=["1 &le; m &le; 20,000"],
    hints=["Simulate the sequence modulo m, keeping only the last two terms, and stop when the pair (0, 1) appears again.",
           "Start from the pair (F<sub>0</sub>, F<sub>1</sub>) = (0, 1) and count the steps until that pair comes back.",
           "The period never exceeds 6m, so a loop of at most 6m steps always finishes. For m up to 20,000 that is fast."],
    editorial=["Keep the current pair <code>(a, b) = (F<sub>k</sub> mod m, F<sub>k+1</sub> mod m)</code>, starting at <code>(0, 1 mod m)</code>. Each step replaces the pair by <code>(b, (a + b) mod m)</code>. The pair is a deterministic function of its predecessor and it starts at (0, 1), so the first step at which it returns to (0, 1) is exactly the period.",
               "The period is known to be at most 6m, so the loop runs at most 120,000 steps for m = 20,000. Smaller moduli often have much shorter periods, as with pi(2) = 3, but simulation handles every case without special treatment."],
    time="O(m)", space="O(1)",
    solution='''def pisanoPeriod(m):
    a, b = 0, 1 % m
    steps = 0
    while True:
        a, b = b, (a + b) % m
        steps += 1
        if a == 0 and b == 1 % m:
            return steps
''',
    tests=[[1], [2], [3], [4], [5], [7], [9], [10], [16], [100], [1000], [9999], [19999], [20000]],
)


def b_pisano(m):
    f = [0, 1 % m]
    for _ in range(6 * m + 5):
        f.append((f[-1] + f[-2]) % m)
    for q in range(1, len(f) - 1):
        if f[q] == 0 and f[q + 1] == 1 % m:
            return q


def v_pisano(tests):
    for t in tests:
        m = t["args"][0]
        assert 1 <= m <= 20000
        assert 1 <= t["expected"] <= 6 * m


CHECKS["fibonacci-mod-period"] = (b_pisano, lambda rg: [rg.randint(1, 400)], "exact")
VALIDATE["fibonacci-mod-period"] = v_pisano

# ---------------------------------------------------------------- HARD

p = add(
    id="fibonacci-gcd-mod", title="GCD of Two Fibonacci Numbers", diff="Hard", topic="Math & Bit Manipulation", tier="extra",
    fn="fibonacciGcdMod", params=[("m", "int"), ("n", "int")], ret="int", cmp="exact",
    desc="<p>Let <code>F<sub>1</sub> = 1</code>, <code>F<sub>2</sub> = 1</code>, and <code>F<sub>i</sub> = F<sub>i-1</sub> + F<sub>i-2</sub></code>. Given two positive integers <code>m</code> and <code>n</code>, compute <code>gcd(F<sub>m</sub>, F<sub>n</sub>)</code> and return it modulo <code>1,000,000,007</code>.</p><p>The Fibonacci numbers are far too large to compute, so the answer has to come from a number-theoretic identity.</p><pre>m = 12, n = 18 -> 8   (F<sub>12</sub> = 144, F<sub>18</sub> = 2584, gcd = 8 = F<sub>6</sub>)\nm = 8,  n = 12 -> 3   (gcd(21, 144) = 3 = F<sub>4</sub>)\nm = 6,  n = 9  -> 2   (gcd(8, 34) = 2 = F<sub>3</sub>)</pre>",
    constraints=["1 &le; m, n &le; 10<sup>9</sup>"],
    hints=["Work out a few small cases by hand, such as gcd(F<sub>6</sub>, F<sub>9</sub>) = gcd(8, 34) = 2, and compare the indices with the gcd.",
           "The gcd of two Fibonacci numbers is itself a Fibonacci number, whose index is gcd(m, n).",
           "So the answer is F<sub>gcd(m, n)</sub> modulo the prime. Find the gcd of the indices first, then use fast doubling."],
    editorial=["The key identity is <code>gcd(F<sub>m</sub>, F<sub>n</sub>) = F<sub>gcd(m, n)</sub></code>. The identity <code>F<sub>m+n</sub> = F<sub>m</sub>F<sub>n+1</sub> + F<sub>m-1</sub>F<sub>n</sub></code> together with <code>gcd(F<sub>n</sub>, F<sub>n+1</sub>) = 1</code> shows that <code>gcd(F<sub>m</sub>, F<sub>n</sub>) = gcd(F<sub>m-n</sub>, F<sub>n</sub>)</code> for m &gt; n. The index pair then follows exactly the subtraction steps of Euclid's algorithm, and it ends with <code>gcd(F<sub>g</sub>, F<sub>0</sub>) = F<sub>g</sub></code>, where <code>g = gcd(m, n)</code>.",
               "So compute g with Euclid's algorithm and then F<sub>g</sub> modulo 1,000,000,007 with fast doubling, using <code>F<sub>2k</sub> = F<sub>k</sub>(2F<sub>k+1</sub> - F<sub>k</sub>)</code> and <code>F<sub>2k+1</sub> = F<sub>k</sub><sup>2</sup> + F<sub>k+1</sub><sup>2</sup></code>. The total cost is O(log max(m, n)) arithmetic operations."],
    time="O(log(m + n))", space="O(log(m + n))",
    solution='''from math import gcd

MOD = 1000000007

def fibPair(n):
    # returns (F_n, F_(n+1)) modulo MOD
    if n == 0:
        return 0, 1
    a, b = fibPair(n // 2)
    c = a * ((2 * b - a) % MOD) % MOD
    d = (a * a + b * b) % MOD
    if n % 2 == 0:
        return c, d
    return d, (c + d) % MOD

def fibonacciGcdMod(m, n):
    g = gcd(m, n)
    return fibPair(g)[0]
''',
    tests=[[1, 1], [2, 2], [6, 9], [8, 12], [12, 18], [10, 15], [7, 13], [6, 4], [46368, 75025],
           [123456, 654321], [1000000000, 500000000], [999999999, 1000000000], [999999937, 999999929]],
)


def b_fgcd(m, n):
    f = [0, 1]
    while len(f) <= max(m, n):
        f.append(f[-1] + f[-2])
    return math.gcd(f[m], f[n]) % MOD


def g_fgcd(rg):
    g0 = rg.randint(1, 20)
    return [g0 * rg.randint(1, 15), g0 * rg.randint(1, 15)]


def v_fgcd(tests):
    for t in tests:
        m, n = t["args"]
        assert 1 <= m <= 10 ** 9 and 1 <= n <= 10 ** 9
        assert 0 <= t["expected"] < MOD


CHECKS["fibonacci-gcd-mod"] = (b_fgcd, g_fgcd, "exact")
VALIDATE["fibonacci-gcd-mod"] = v_fgcd

p = add(
    id="common-progression-terms", title="Common Terms of Two Progressions", diff="Hard", topic="Math & Bit Manipulation", tier="common",
    fn="commonProgressionTerms", params=[("a1", "int"), ("d1", "int"), ("a2", "int"), ("d2", "int"), ("limit", "int")],
    ret="int", cmp="exact",
    desc="<p>Two infinite arithmetic progressions are given. The first is <code>A: a1, a1 + d1, a1 + 2d1, ...</code> and the second is <code>B: a2, a2 + d2, a2 + 2d2, ...</code></p><p>Count the integers <code>x</code> with <code>0 &le; x &le; limit</code> that appear in both progressions.</p><pre>a1 = 2, d1 = 3, a2 = 3, d2 = 4, limit = 50 -> 4   (11, 23, 35, 47)\na1 = 5, d1 = 5, a2 = 0, d2 = 7, limit = 30 -> 0\na1 = 0, d1 = 6, a2 = 0, d2 = 4, limit = 100 -> 9   (0, 12, 24, ..., 96)</pre>",
    constraints=["0 &le; a1, a2 &le; 10<sup>9</sup>", "1 &le; d1, d2 &le; 10<sup>9</sup>", "0 &le; limit &le; 10<sup>9</sup>"],
    hints=["A value x is in A exactly when x &ge; a1 and x - a1 is divisible by d1. Write the same condition for B: that gives two congruences on x.",
           "Common terms, when they exist, form one progression with step lcm(d1, d2). Its first term solves both congruences, which the Chinese Remainder Theorem handles.",
           "A solution exists only when g = gcd(d1, d2) divides a2 - a1. Then write x = a1 + d1 * t, and solve d1 * t = a2 - a1 modulo d2 using a modular inverse."],
    editorial=["A value x lies in progression A exactly when <code>x &ge; a1</code> and <code>x - a1</code> is divisible by d1; the same holds for B. So the common values are the x at or above <code>max(a1, a2)</code> satisfying <code>x = a1 (mod d1)</code> and <code>x = a2 (mod d2)</code>. By the Chinese Remainder Theorem, the solutions of two such congruences are either none or a single residue class modulo <code>L = lcm(d1, d2)</code>.",
               "Let <code>g = gcd(d1, d2)</code>. If g does not divide a2 - a1 there are no common terms. Otherwise write <code>x = a1 + d1 * t</code>; the second congruence becomes <code>(d1/g) * t = (a2 - a1)/g (mod d2/g)</code>, and since d1/g and d2/g are coprime, t has a unique residue. That gives the smallest common term x0 at or above a1. Move x0 up to the first term at or above max(a1, a2) in steps of L, then count the terms of the class not above limit. Python's <code>pow(v, -1, m)</code> computes the inverse, and it returns 0 when m is 1, which covers d2/g = 1."],
    time="O(log(d1 + d2))", space="O(1)",
    solution='''from math import gcd

def commonProgressionTerms(a1, d1, a2, d2, limit):
    g = gcd(d1, d2)
    if (a2 - a1) % g != 0:
        return 0
    m = d2 // g
    t = ((a2 - a1) // g) * pow(d1 // g, -1, m) % m
    x0 = a1 + d1 * t
    L = d1 // g * d2
    start = max(a1, a2)
    if x0 < start:
        x0 += (start - x0 + L - 1) // L * L
    if x0 > limit:
        return 0
    return (limit - x0) // L + 1
''',
    tests=[[2, 3, 3, 4, 50], [5, 5, 0, 7, 30], [0, 6, 0, 4, 100], [7, 1, 3, 1, 0], [0, 2, 1, 2, 100],
           [1000000000, 1000000000, 0, 1, 1000000000], [0, 4, 2, 6, 1000000000], [5, 6, 5, 9, 1000000000],
           [17, 12, 3, 8, 999999999], [123456789, 987654, 555555555, 123456, 999999999], [3, 1000000000, 999999999, 999999937, 1000000000],
           [0, 1, 0, 1, 1000000000]],
)


def b_common(a1, d1, a2, d2, limit):
    cnt = 0
    for x in range(0, limit + 1):
        if x >= a1 and (x - a1) % d1 == 0 and x >= a2 and (x - a2) % d2 == 0:
            cnt += 1
    return cnt


def g_common(rg):
    return [rg.randint(0, 40), rg.randint(1, 30), rg.randint(0, 40), rg.randint(1, 30), rg.randint(0, 400)]


def v_common(tests):
    for t in tests:
        a1, d1, a2, d2, limit = t["args"]
        assert 0 <= a1 <= 10 ** 9 and 0 <= a2 <= 10 ** 9 and 1 <= d1 <= 10 ** 9 and 1 <= d2 <= 10 ** 9
        assert 0 <= limit <= 10 ** 9
        assert t["expected"] >= 0


CHECKS["common-progression-terms"] = (b_common, g_common, "exact")
VALIDATE["common-progression-terms"] = v_common

p = add(
    id="power-sum-up-to-n-mod", title="Sum of Powers Up To N", diff="Hard", topic="Math & Bit Manipulation", tier="extra",
    fn="powerSumMod", params=[("n", "int"), ("k", "int")], ret="int", cmp="exact",
    desc="<p>Given <code>n</code> and <code>k</code>, compute <code>S = 1<sup>k</sup> + 2<sup>k</sup> + ... + n<sup>k</sup></code> and return <code>S</code> modulo <code>1,000,000,007</code>, as a value in <code>0 .. 1,000,000,006</code>. When <code>k = 0</code> every term is 1, so the result is <code>n</code> modulo the prime.</p><pre>n = 10, k = 1 -> 55\nn = 10, k = 2 -> 385\nn = 5,  k = 0 -> 5</pre>",
    constraints=["1 &le; n &le; 10<sup>9</sup>", "0 &le; k &le; 10"],
    hints=["Adding n terms directly is too slow when n is 10<sup>9</sup>. Think about what kind of function of n the sum is.",
           "For a fixed k, S(n) is a polynomial in n of degree k + 1. A polynomial of degree d is determined by d + 1 of its values.",
           "Compute S(0), S(1), ..., S(k + 1) directly, then use Lagrange interpolation to evaluate the polynomial at n, all modulo the prime."],
    editorial=["Faulhaber's formula says that <code>1<sup>k</sup> + ... + n<sup>k</sup></code> is a polynomial in n of degree k + 1. With k at most 10 we only need k + 2 sample points, and all the denominators in the interpolation are products of small integers, which are invertible modulo the prime 1,000,000,007.",
               "Take the points x = 0, 1, ..., k + 1, with S(0) = 0, and compute their values directly. Lagrange's formula then gives S(n) as the sum over i of <code>y<sub>i</sub> * prod<sub>j != i</sub> (n - j) / (i - j)</code>. Each inverse is computed with Fermat's little theorem. If n is one of the sample points, return its value directly. The work is O(k<sup>2</sup> log p) regardless of n."],
    time="O(k^2 log p)", space="O(k)",
    solution='''MOD = 1000000007

def powerSumMod(n, k):
    d = k + 1  # the sum is a polynomial in n of degree d
    ys = [0]
    total = 0
    for x in range(1, d + 1):
        total = (total + pow(x, k, MOD)) % MOD
        ys.append(total)
    if n <= d:
        return ys[n]
    result = 0
    for i in range(d + 1):
        num, den = 1, 1
        for j in range(d + 1):
            if j != i:
                num = num * ((n - j) % MOD) % MOD
                den = den * ((i - j) % MOD) % MOD
        term = ys[i] * num % MOD * pow(den, MOD - 2, MOD) % MOD
        result = (result + term) % MOD
    return result
''',
    tests=[[1, 0], [5, 0], [10, 1], [10, 2], [3, 10], [11, 10], [12, 10], [2, 9], [1000000000, 1],
           [1000000000, 10], [999999, 7], [123456789, 6], [1000000000, 0]],
)


def b_psum(n, k):
    return sum(i ** k for i in range(1, n + 1)) % MOD


def g_psum(rg):
    return [rg.randint(1, 300), rg.randint(0, 10)]


def v_psum(tests):
    for t in tests:
        n, k = t["args"]
        assert 1 <= n <= 10 ** 9 and 0 <= k <= 10
        assert 0 <= t["expected"] < MOD


CHECKS["power-sum-up-to-n-mod"] = (b_psum, g_psum, "exact")
VALIDATE["power-sum-up-to-n-mod"] = v_psum
