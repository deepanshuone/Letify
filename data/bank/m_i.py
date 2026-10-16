"""Problems: combinatorial sums and counts (binomial rows, subsets, Catalan-like paths, stars and bars).
See data/lib.py for the registry."""
import itertools
import math
from collections import defaultdict
from functools import lru_cache

from lib import add, rnd, CHECKS, VALIDATE, gen_arr  # noqa: F401

MOD = 10 ** 9 + 7
TOPIC = "Math & Bit Manipulation"


def _vspec(*spec):
    """VALIDATE helper. An int argument is a (lo, hi) pair; a list argument is (lo, hi, max_len)."""
    def check(tests):
        for t in tests:
            assert len(t["args"]) == len(spec), "arg count"
            for a, s in zip(t["args"], spec):
                if isinstance(a, list):
                    lo, hi, mx = s
                    assert len(a) <= mx, ("list too long", len(a))
                    for x in a:
                        assert lo <= x <= hi, ("list value out of range", x)
                else:
                    lo, hi = s
                    assert lo <= a <= hi, ("value out of range", a)
    return check


# ---------------------------------------------------------------- EASY

p = add(
    id="prefix-pascal-row-sum", title="Partial Sum of a Pascal Row", diff="Easy", topic=TOPIC,
    fn="prefixPascalRowSum", params=[("n", "int"), ("k", "int")], ret="int", cmp="exact",
    desc="<p>Row <code>n</code> of Pascal's triangle holds the binomial coefficients <code>C(n, 0), C(n, 1), ..., C(n, n)</code>. Given <code>n</code> and <code>k</code>, return the sum of the entries <code>C(n, i)</code> for every <code>i</code> with <code>0 &le; i &le; min(k, n)</code>, taken modulo <code>1,000,000,007</code>.</p><pre>n = 5, k = 2   -> 1 + 5 + 10 = 16\nn = 4, k = 10  -> 16   (the whole row)\nn = 0, k = 0   -> 1</pre>",
    constraints=["0 &le; n &le; 100,000", "0 &le; k &le; 100,000"],
    hints=["Each entry C(n, i) can be computed on its own, but recomputing every one from scratch is wasteful. Can you get the entries from a shared table?",
           "Write C(n, i) = n! / (i! (n - i)!). Modulo a prime, division is multiplication by a modular inverse.",
           "Precompute n! and all the inverse factorials once, then add the terms for i from 0 to min(k, n)."],
    editorial=["A partial row of Pascal's triangle has no simple closed form, so we add the terms one by one. Each term is <code>n! * inv(i!) * inv((n - i)!)</code>, and once the factorials and their inverses are tabulated every term costs O(1).",
               "The modular inverses come from Fermat's little theorem: 1,000,000,007 is prime, so <code>x<sup>p-2</sup></code> is the inverse of <code>x</code>. The inverse factorials can be filled backwards from a single inverse, since <code>inv((i-1)!) = inv(i!) * i</code>.",
               "The running time is O(n + k) and the memory is O(n). As a check, the answer for k &ge; n must be 2<sup>n</sup> modulo the prime."],
    time="O(n + k)", space="O(n)",
    solution='''def prefixPascalRowSum(n, k):
    MOD = 10 ** 9 + 7
    fact = [1] * (n + 1)
    for i in range(1, n + 1):
        fact[i] = fact[i - 1] * i % MOD
    inv_fact = [1] * (n + 1)
    inv_fact[n] = pow(fact[n], MOD - 2, MOD)
    for i in range(n, 0, -1):
        inv_fact[i - 1] = inv_fact[i] * i % MOD
    total = 0
    for i in range(min(k, n) + 1):
        total = (total + fact[n] * inv_fact[i] % MOD * inv_fact[n - i]) % MOD
    return total
''',
    tests=[[0, 0], [1, 0], [5, 2], [4, 10], [10, 10], [10, 20], [3, 100], [60, 30], [100, 50], [1000, 500],
           [1000, 3], [100000, 0], [100000, 50000], [99999, 1]],
)


def b_prefix_pascal(n, k):
    return sum(math.comb(n, i) for i in range(min(k, n) + 1)) % MOD


CHECKS["prefix-pascal-row-sum"] = (b_prefix_pascal, lambda r: [r.randint(0, 60), r.randint(0, 70)], "exact")
VALIDATE["prefix-pascal-row-sum"] = _vspec((0, 100000), (0, 100000))

p = add(
    id="total-of-k-subset-sums", title="Sum Over All k-Subsets", diff="Easy", topic=TOPIC,
    fn="totalOfKSubsetSums", params=[("nums", "int[]"), ("k", "int")], ret="int", cmp="exact",
    desc="<p>Consider every way to choose exactly <code>k</code> positions of the array <code>nums</code>. Positions are what matter, so two choices that hold equal values in different positions count separately. For each choice add up the chosen values, and return the total of all these sums, modulo <code>1,000,000,007</code>.</p><pre>nums = [1, 2, 3], k = 2  ->  (1 + 2) + (1 + 3) + (2 + 3) = 12\nnums = [7, 7, 7], k = 3  ->  7</pre>",
    constraints=["1 &le; k &le; nums.length &le; 5,000", "0 &le; nums[i] &le; 10<sup>9</sup>"],
    hints=["Try a tiny case by hand: with nums = [a, b, c] and k = 2, how often does each value appear in the total?",
           "Every position appears in the same number of k-subsets. Count how many k-subsets contain one fixed position.",
           "A fixed position is in C(n - 1, k - 1) of the k-subsets, so the answer is sum(nums) * C(n - 1, k - 1) modulo the prime."],
    editorial=["Swap the order of summation. The total equals the sum over positions i of <code>nums[i]</code> times the number of k-subsets that contain position i. Symmetry means that count is the same for every position.",
               "Choosing the other k - 1 members of a subset that already contains position i can be done in C(n - 1, k - 1) ways, so the answer is <code>sum(nums) * C(n - 1, k - 1)</code>. Only the binomial coefficient needs care, and Python's math.comb handles it exactly before the final reduction.",
               "Checking the example: sum = 6, n = 3, k = 2 gives 6 * C(2, 1) = 12, which matches the three pair sums 3 + 4 + 5."],
    time="O(n)", space="O(1)",
    solution='''def totalOfKSubsetSums(nums, k):
    import math
    MOD = 10 ** 9 + 7
    n = len(nums)
    return sum(nums) % MOD * (math.comb(n - 1, k - 1) % MOD) % MOD
''',
    tests=[[[1, 2, 3], 2], [[5], 1], [[7, 7, 7], 3], [[0, 0, 0, 0], 2], [[1, 2, 3, 4], 1], [[10, 20, 30, 40, 50], 3],
           [[1000000000, 1000000000], 1], [[4, 9, 2, 6, 1, 8], 4], [[1, 1, 1, 1, 1, 1, 1, 1], 8],
           [[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], 5]],
)
_r = rnd(201)
p["tests"].append([[_r.randint(0, 10 ** 9) for _ in range(3000)], 1500])
p["tests"].append([[_r.randint(0, 10 ** 9) for _ in range(2000)], 1])
p["tests"].append([[_r.randint(0, 999) for _ in range(1200)], 600])


def b_k_subset_sums(nums, k):
    total = 0
    for c in itertools.combinations(range(len(nums)), k):
        total += sum(nums[i] for i in c)
    return total % MOD


def g_k_subset_sums(r):
    n = r.randint(1, 8)
    return [[r.randint(0, 30) for _ in range(n)], r.randint(1, n)]


def v_k_subset_sums(tests):
    for t in tests:
        nums, k = t["args"]
        assert 1 <= k <= len(nums) <= 5000
        assert all(0 <= x <= 10 ** 9 for x in nums)


CHECKS["total-of-k-subset-sums"] = (b_k_subset_sums, g_k_subset_sums, "exact")
VALIDATE["total-of-k-subset-sums"] = v_k_subset_sums

p = add(
    id="identical-items-min-per-box", title="Identical Items With a Minimum per Box", diff="Easy", topic=TOPIC,
    fn="countMinimumDistributions", params=[("n", "int"), ("k", "int"), ("minEach", "int")], ret="int", cmp="exact",
    desc="<p>There are <code>n</code> identical balls and <code>k</code> distinct boxes. Every box must receive at least <code>minEach</code> balls, and all the balls must be placed. Two placements are different when some box holds a different number of balls. Return the number of placements, modulo <code>1,000,000,007</code>, or <code>0</code> if no placement exists.</p><pre>n = 5, k = 2, minEach = 0  -> 6\nn = 10, k = 3, minEach = 2 -> 15\nn = 3, k = 5, minEach = 1  -> 0</pre>",
    constraints=["0 &le; n &le; 1,000,000", "1 &le; k &le; 1,000", "0 &le; minEach &le; 1,000,000"],
    hints=["Give every box its minimum first. What is left over, and how is it shared out when there are no further restrictions?",
           "Distributing m identical balls into k boxes with no restriction is the stars and bars count C(m + k - 1, k - 1).",
           "Subtract k * minEach from n. If the result is negative the answer is 0; otherwise apply stars and bars to what remains."],
    editorial=["Stars and bars: arrange m stars and k - 1 bars in a row. The stars before the first bar go to box one, the stars between the first and second bars go to box two, and so on. There are C(m + k - 1, k - 1) such rows.",
               "Setting aside the minimum leaves m = n - k * minEach balls to share with no restriction, so the answer is C(m + k - 1, k - 1). If m is negative, no placement exists.",
               "The binomial coefficient is computed as a product of k - 1 terms divided by (k - 1)!, with a modular inverse for the division. Because the top argument stays below the prime, the product is taken modulo 1,000,000,007 without special cases."],
    time="O(k)", space="O(1)",
    solution='''def countMinimumDistributions(n, k, minEach):
    MOD = 10 ** 9 + 7
    free = n - k * minEach
    if free < 0:
        return 0
    top = free + k - 1
    r = k - 1
    num = 1
    for i in range(r):
        num = num * ((top - i) % MOD) % MOD
    den = 1
    for i in range(1, r + 1):
        den = den * i % MOD
    return num * pow(den, MOD - 2, MOD) % MOD
''',
    tests=[[5, 2, 0], [10, 3, 2], [3, 5, 1], [0, 4, 0], [7, 1, 7], [300, 3, 0], [20, 6, 1], [0, 60, 0],
           [1000000, 2, 500000], [1000000, 1000, 0], [1000000, 1000, 1], [1000000, 1, 0], [1000000, 999, 1000],
           [999999, 40, 0]],
)


def b_min_distributions(n, k, minEach):
    @lru_cache(None)
    def go(boxes, left):
        if boxes == 0:
            return 1 if left == 0 else 0
        return sum(go(boxes - 1, left - x) for x in range(minEach, left + 1))
    return go(k, n) % MOD


CHECKS["identical-items-min-per-box"] = (
    b_min_distributions,
    lambda r: [r.randint(0, 12), r.randint(1, 4), r.randint(0, 4)],
    "exact",
)
VALIDATE["identical-items-min-per-box"] = _vspec((0, 1000000), (1, 1000), (0, 1000000))

# ---------------------------------------------------------------- MEDIUM

p = add(
    id="residue-class-binomial-row-sum", title="Pascal Row Sum Over a Residue Class", diff="Medium", topic=TOPIC, tier="extra",
    fn="residueClassRowSum", params=[("n", "int"), ("m", "int"), ("r", "int")], ret="int", cmp="exact",
    desc="<p>Row <code>n</code> of Pascal's triangle holds <code>C(n, 0), ..., C(n, n)</code>. Given <code>n</code>, a step <code>m</code> and a residue <code>r</code>, return the sum of <code>C(n, i)</code> over all indices <code>i</code> in <code>0..n</code> that satisfy <code>i mod m = r</code>, modulo <code>1,000,000,007</code>.</p><pre>n = 5, m = 2, r = 0  -> C(5,0) + C(5,2) + C(5,4) = 1 + 10 + 5 = 16\nn = 10, m = 3, r = 1 -> C(10,1) + C(10,4) + C(10,7) + C(10,10) = 341</pre>",
    constraints=["0 &le; n &le; 100,000", "1 &le; m &le; 1,000", "0 &le; r &lt; m"],
    hints=["Looping over every index and testing i mod m works. The question is how to evaluate each C(n, i) cheaply.",
           "Pascal's rule does not give a shortcut here, but factorials do: each C(n, i) is one product of tables.",
           "Build n! and the inverse factorials once, then step through the indices r, r + m, r + 2m, ... up to n."],
    editorial=["Congruence classes of indices do not collapse into a closed form, so the answer is a direct sum. Stepping the index by m visits exactly the indices in the class, so the loop does about n / m iterations.",
               "Each term is <code>n! * inv(i!) * inv((n - i)!)</code>, computed modulo the prime 1,000,000,007 with inverses from Fermat's little theorem. Filling the inverse-factorial table backwards from one inverse keeps the setup linear.",
               "Sanity check: with m = 1 the sum covers the whole row and must equal 2<sup>n</sup> modulo the prime."],
    time="O(n)", space="O(n)",
    solution='''def residueClassRowSum(n, m, r):
    MOD = 10 ** 9 + 7
    fact = [1] * (n + 1)
    for i in range(1, n + 1):
        fact[i] = fact[i - 1] * i % MOD
    inv_fact = [1] * (n + 1)
    inv_fact[n] = pow(fact[n], MOD - 2, MOD)
    for i in range(n, 0, -1):
        inv_fact[i - 1] = inv_fact[i] * i % MOD
    total = 0
    for i in range(r, n + 1, m):
        total = (total + fact[n] * inv_fact[i] % MOD * inv_fact[n - i]) % MOD
    return total
''',
    tests=[[0, 1, 0], [7, 1, 0], [5, 2, 0], [5, 2, 1], [10, 3, 1], [10, 4, 2], [40, 5, 3], [1000, 1, 0],
           [1000, 7, 6], [60, 60, 59], [100000, 1, 0], [100000, 7, 3], [99999, 2, 1], [100000, 1000, 999]],
)


def b_residue_row(n, m, r):
    return sum(math.comb(n, i) for i in range(n + 1) if i % m == r) % MOD


def g_residue_row(r):
    m = r.randint(1, 7)
    return [r.randint(0, 40), m, r.randint(0, m - 1)]


def v_residue_row(tests):
    for t in tests:
        n, m, rr = t["args"]
        assert 0 <= n <= 100000 and 1 <= m <= 1000 and 0 <= rr < m


CHECKS["residue-class-binomial-row-sum"] = (b_residue_row, g_residue_row, "exact")
VALIDATE["residue-class-binomial-row-sum"] = v_residue_row

p = add(
    id="subsets-sum-divisible-by-k-count", title="Subsets Whose Sum Is Divisible by K", diff="Medium", topic=TOPIC,
    fn="countDivisibleSubsets", params=[("nums", "int[]"), ("k", "int")], ret="int", cmp="exact",
    desc="<p>Given an array <code>nums</code> of positive integers and an integer <code>k</code>, count the <strong>non-empty</strong> subsets of positions whose sum is divisible by <code>k</code>. Positions are what matter, so equal values at different positions give different subsets. Return the count modulo <code>1,000,000,007</code>.</p><pre>nums = [1, 2, 3], k = 3  -> 3   ({3}, {1, 2} and {1, 2, 3})\nnums = [4, 4], k = 2     -> 3   ({4}, {4} and {4, 4})</pre>",
    constraints=["1 &le; nums.length &le; 2,000", "1 &le; nums[i] &le; 10,000", "1 &le; k &le; 60"],
    hints=["Going through all 2<sup>n</sup> subsets is too slow for n = 2,000. What matters about a subset is only its sum modulo k.",
           "Process the elements one at a time and keep, for each remainder r, how many subsets of the elements so far have sum mod k equal to r.",
           "When an element x arrives, every subset with remainder r can either skip it or extend to remainder (r + x) mod k. The empty subset is counted at remainder 0, so subtract one at the end."],
    editorial=["Let <code>dp[r]</code> be the number of subsets, the empty one included, whose sum leaves remainder <code>r</code> modulo <code>k</code>. It starts as <code>dp[0] = 1</code>. For each element <code>x</code> the new table keeps every old subset and also adds, for each old remainder <code>r</code>, a copy shifted to <code>(r + x) mod k</code>.",
               "After all elements are processed, <code>dp[0]</code> counts the subsets with sum divisible by k, including the empty set. Subtracting one gives the non-empty answer, reduced modulo 1,000,000,007.",
               "The work is O(n * k) with n up to 2,000 and k up to 60, comfortably fast. Only remainders are stored, so the subset sums themselves can be large without trouble."],
    time="O(n * k)", space="O(k)",
    solution='''def countDivisibleSubsets(nums, k):
    MOD = 10 ** 9 + 7
    dp = [0] * k
    dp[0] = 1
    for x in nums:
        x %= k
        new = dp[:]
        for r in range(k):
            if dp[r]:
                new[(r + x) % k] = (new[(r + x) % k] + dp[r]) % MOD
        dp = new
    return (dp[0] - 1) % MOD
''',
    tests=[[[1, 2, 3], 3], [[3], 3], [[3], 1], [[2, 4], 2], [[1, 1, 1, 1], 2], [[5, 10, 15, 20], 5],
           [[7, 8, 9, 10, 11], 6], [[2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], 4], [[1000, 2000, 3000], 50],
           [[10000] * 10, 7], [[4, 4], 2], [[9, 1, 8, 2, 7, 3, 6, 4, 5, 10, 12, 11], 13]],
)
_r = rnd(205)
p["tests"].append([[_r.randint(1, 10000) for _ in range(2000)], 60])
p["tests"].append([[_r.randint(1, 10000) for _ in range(1500)], 37])
p["tests"].append([[1] * 2000, 1])


def b_divisible_subsets(nums, k):
    n = len(nums)
    count = 0
    for mask in range(1, 1 << n):
        s = sum(nums[i] for i in range(n) if mask >> i & 1)
        if s % k == 0:
            count += 1
    return count % MOD


def g_divisible_subsets(r):
    n = r.randint(1, 10)
    return [[r.randint(1, 30) for _ in range(n)], r.randint(1, 12)]


def v_divisible_subsets(tests):
    for t in tests:
        nums, k = t["args"]
        assert 1 <= len(nums) <= 2000 and 1 <= k <= 60
        assert all(1 <= x <= 10000 for x in nums)


CHECKS["subsets-sum-divisible-by-k-count"] = (b_divisible_subsets, g_divisible_subsets, "exact")
VALIDATE["subsets-sum-divisible-by-k-count"] = v_divisible_subsets

p = add(
    id="circle-seats-no-neighbours", title="Seats Around a Round Table With No Neighbours", diff="Medium", topic=TOPIC,
    fn="countCircleSeatPlans", params=[("n", "int"), ("k", "int")], ret="int", cmp="exact",
    desc="<p><code>n</code> seats are placed around a round table and numbered <code>0</code> to <code>n - 1</code>; seat <code>i</code> is next to seat <code>i + 1</code>, and seat <code>n - 1</code> is next to seat <code>0</code>. Choose exactly <code>k</code> seats so that no two chosen seats are neighbours. Seats are labelled, so a rotated choice is a different choice. Return the number of choices modulo <code>1,000,000,007</code>.</p><pre>n = 5, k = 2 -> 5   ({0,2}, {0,3}, {1,3}, {1,4}, {2,4})\nn = 6, k = 2 -> 9\nn = 6, k = 3 -> 2</pre>",
    constraints=["2 &le; n &le; 1,000,000,000", "0 &le; k &le; min(floor(n / 2), 1,000)"],
    hints=["On a line, choosing k non-adjacent seats out of n is C(n - k + 1, k). The circle makes the first and last seats neighbours, which changes the count.",
           "Count the chosen seats together with their gaps. Each chosen seat must be followed by at least one unchosen seat, so the gaps sum to n - k with every gap at least one.",
           "The result is n / (n - k) * C(n - k, k). The quotient is an integer, so reduce it modulo the prime by multiplying with the inverse of n - k."],
    editorial=["Fix a chosen seat and walk around the circle. The k chosen seats split the remaining n - k unchosen seats into k gaps, each of size at least one. Counting pairs (choice, marked chosen seat) gives k times the answer on one side and n times a composition count on the other, which yields <code>n / k * C(n - k - 1, k - 1)</code>.",
               "That is the same as <code>n / (n - k) * C(n - k, k)</code>. For k = 0 the answer is 1 (the empty choice). For n = 5, k = 2 the formula gives 5 / 3 * C(3, 2) = 5.",
               "Because n is up to 10<sup>9</sup> but k is at most 1,000, the binomial is a product of k terms times the inverse of k!, and the division by n - k uses a modular inverse. The constraint k &le; n / 2 keeps n - k at least 1, so every inverse exists."],
    time="O(k)", space="O(1)",
    solution='''def countCircleSeatPlans(n, k):
    MOD = 10 ** 9 + 7
    if k == 0:
        return 1
    m = n - k
    prod = 1
    for i in range(k):
        prod = prod * ((m - i) % MOD) % MOD
    fact_k = 1
    for i in range(1, k + 1):
        fact_k = fact_k * i % MOD
    comb = prod * pow(fact_k, MOD - 2, MOD) % MOD
    return n % MOD * comb % MOD * pow(m % MOD, MOD - 2, MOD) % MOD
''',
    tests=[[2, 0], [2, 1], [4, 2], [5, 2], [6, 2], [6, 3], [7, 3], [12, 6], [14, 7], [1000000000, 0],
           [1000000000, 1], [1001, 500], [1000000000, 1000], [999999999, 500], [123456789, 1000]],
)


def b_circle_seats(n, k):
    c = 0
    for comb in itertools.combinations(range(n), k):
        s = set(comb)
        if all(((i + 1) % n) not in s for i in s):
            c += 1
    return c % MOD


def g_circle_seats(r):
    n = r.randint(2, 14)
    return [n, r.randint(0, n // 2)]


def v_circle_seats(tests):
    for t in tests:
        n, k = t["args"]
        assert 2 <= n <= 10 ** 9 and 0 <= k <= min(n // 2, 1000)


CHECKS["circle-seats-no-neighbours"] = (b_circle_seats, g_circle_seats, "exact")
VALIDATE["circle-seats-no-neighbours"] = v_circle_seats

p = add(
    id="dyck-paths-with-k-peaks", title="Dyck Paths With Exactly K Peaks", diff="Medium", topic=TOPIC, tier="extra",
    fn="dyckPathsWithPeaks", params=[("n", "int"), ("k", "int")], ret="int", cmp="exact",
    desc="<p>A Dyck path of semilength <code>n</code> is a sequence of <code>n</code> <code>U</code> steps and <code>n</code> <code>D</code> steps in which no prefix has more <code>D</code> steps than <code>U</code> steps. A <em>peak</em> is a <code>U</code> step immediately followed by a <code>D</code> step. Given <code>n</code> and <code>k</code>, return the number of Dyck paths of semilength <code>n</code> with exactly <code>k</code> peaks.</p><pre>n = 3: UDUDUD has 3 peaks; UDUUDD, UUDDUD and UUDUDD have 2 each; UUUDDD has 1.\nSo n = 3 gives 1, 3, 1 for k = 1, 2, 3.</pre>",
    constraints=["1 &le; n &le; 17", "1 &le; k &le; n"],
    hints=["Enumerating paths is fine for tiny n. For larger n, a DP that tracks the current height, the number of peaks so far and whether the last step was U works.",
           "The answers for fixed n across all k add up to the Catalan number C<sub>n</sub>, so they form a triangle of numbers with a known closed form.",
           "These are the Narayana numbers: N(n, k) = (1 / n) * C(n, k) * C(n, k - 1). Note that n is small here, so the result fits in a 32-bit integer."],
    editorial=["A Dyck path is a Catalan object, and grouping them by the number of peaks refines the count. The counts N(n, k) are called Narayana numbers and form a triangle whose rows sum to the Catalan numbers.",
               "The closed form <code>N(n, k) = C(n, k) * C(n, k - 1) / n</code> is an exact integer. Multiplying the two binomials before dividing by n is exact in Python's integers, so no fractions are needed.",
               "Checking n = 3: N(3, 1) = 3 * 1 / 3 = 1, N(3, 2) = 3 * 3 / 3 = 3, N(3, 3) = 1 * 3 / 3 = 1, matching the enumeration above. The whole computation is O(1) binomials."],
    time="O(n)", space="O(n)",
    solution='''def dyckPathsWithPeaks(n, k):
    import math
    return math.comb(n, k) * math.comb(n, k - 1) // n
''',
    tests=[[1, 1], [2, 1], [2, 2], [3, 1], [3, 2], [3, 3], [4, 2], [5, 3], [6, 1], [8, 4], [10, 4], [12, 6],
           [15, 8], [16, 5], [17, 9], [17, 1], [17, 17], [17, 3]],
)


def b_narayana(n, k):
    # step-by-step DP over (height, peaks so far, previous step was U)
    cur = {(0, 0, False): 1}
    for _ in range(2 * n):
        nxt = defaultdict(int)
        for (h, pk, last_up), c in cur.items():
            nxt[(h + 1, pk, True)] += c
            if h > 0:
                nxt[(h - 1, pk + (1 if last_up else 0), False)] += c
        cur = nxt
    return sum(c for (h, pk, _), c in cur.items() if h == 0 and pk == k) % MOD


def g_narayana(r):
    n = r.randint(1, 8)
    return [n, r.randint(1, n)]


CHECKS["dyck-paths-with-k-peaks"] = (b_narayana, g_narayana, "exact")
VALIDATE["dyck-paths-with-k-peaks"] = _vspec((1, 17), (1, 17))

p = add(
    id="convex-polygon-triangulation-count", title="Triangulations of a Convex Polygon", diff="Medium", topic=TOPIC,
    fn="countTriangulations", params=[("m", "int")], ret="int", cmp="exact",
    desc="<p>A convex polygon has <code>m</code> labelled vertices. A triangulation splits it into triangles by drawing diagonals that do not cross each other. Return the number of different triangulations, modulo <code>1,000,000,007</code>. Two triangulations are different when they use different sets of diagonals.</p><pre>m = 3 -> 1   (a triangle is already triangulated)\nm = 4 -> 2\nm = 5 -> 5</pre>",
    constraints=["3 &le; m &le; 50,000"],
    hints=["Pick the side between vertices 0 and m - 1. In any triangulation it belongs to exactly one triangle, whose third vertex is some vertex k.",
           "That split leaves two smaller convex polygons, one on the vertices 0..k and one on k..m - 1, that are triangulated independently. So T(m) = sum of T(a) * T(b) over the splits.",
           "The recurrence is the Catalan recurrence. The answer is the Catalan number C<sub>m - 2</sub>, which equals C(2n, n) / (n + 1) with n = m - 2."],
    editorial=["Let <code>T(j)</code> count triangulations of a polygon with <code>j</code> vertices. Fix the side (0, m - 1). Its triangle has apex <code>k</code> for some 0 &lt; k &lt; m - 1, and the two remaining regions are polygons with k + 1 and m - k vertices. Summing over k gives the convolution recurrence of the Catalan numbers.",
               "Solving the recurrence gives <code>T(m) = C<sub>m-2</sub> = (2n)! / (n! (n + 1)!)</code> with n = m - 2. Computing it modulo the prime needs factorials up to 2n and two modular inverses, so the work is linear in m.",
               "Small values for a check: m = 3 gives C<sub>1</sub> = 1, m = 4 gives C<sub>2</sub> = 2 and m = 6 gives C<sub>4</sub> = 14."],
    time="O(m)", space="O(m)",
    solution='''def countTriangulations(m):
    MOD = 10 ** 9 + 7
    n = m - 2
    fact = [1] * (2 * n + 2)
    for i in range(1, 2 * n + 2):
        fact[i] = fact[i - 1] * i % MOD
    cat = fact[2 * n] * pow(fact[n], MOD - 2, MOD) % MOD * pow(fact[n + 1], MOD - 2, MOD) % MOD
    return cat
''',
    tests=[[3], [4], [5], [6], [7], [8], [9], [12], [20], [30], [40], [2000], [50000], [49999]],
)


def b_triangulations(m):
    @lru_cache(None)
    def t(i, j):
        # triangulations of the polygon formed by the vertices i..j, where the side (i, j) is the base
        if j - i < 2:
            return 1
        return sum(t(i, k) * t(k, j) for k in range(i + 1, j))
    return t(0, m - 1) % MOD


CHECKS["convex-polygon-triangulation-count"] = (b_triangulations, lambda r: [r.randint(3, 12)], "exact")
VALIDATE["convex-polygon-triangulation-count"] = _vspec((3, 50000))

# ---------------------------------------------------------------- HARD

p = add(
    id="bounded-multiset-count", title="Bounded Multisets of a Fixed Size", diff="Hard", topic=TOPIC,
    fn="countBoundedMultisets", params=[("n", "int"), ("k", "int"), ("cap", "int")], ret="int", cmp="exact",
    desc="<p>There are <code>n</code> kinds of item. A multiset is described by how many copies of each kind it holds, and every kind may appear at most <code>cap</code> times. Count the multisets that contain exactly <code>k</code> items in total, modulo <code>1,000,000,007</code>. Equivalently, count the vectors <code>(x<sub>1</sub>, ..., x<sub>n</sub>)</code> with <code>0 &le; x<sub>i</sub> &le; cap</code> and <code>x<sub>1</sub> + ... + x<sub>n</sub> = k</code>.</p><pre>n = 2, k = 2, cap = 1  -> 1   ((1, 1) only)\nn = 3, k = 2, cap = 5  -> 6   (C(4, 2))\nn = 5, k = 0, cap = 0  -> 1</pre>",
    constraints=["1 &le; n &le; 2,000", "0 &le; k &le; 20,000", "0 &le; cap &le; 20,000"],
    hints=["Without the cap, stars and bars gives C(k + n - 1, n - 1). The cap is the complication.",
           "Use inclusion-exclusion over the kinds that break the cap: if j kinds each take at least cap + 1 items, subtract those vectors. Shifting those j kinds by cap + 1 leaves an unrestricted problem.",
           "The answer is the sum over j of (-1)<sup>j</sup> * C(n, j) * C(k - j * (cap + 1) + n - 1, n - 1), where terms with a negative remainder are dropped."],
    editorial=["Start with all vectors of non-negative integers summing to k, which number C(k + n - 1, n - 1) by stars and bars. Now fix a set of j kinds that are allowed to violate the cap, meaning they hold at least cap + 1 items. Removing cap + 1 from each of them maps those vectors bijectively onto unrestricted vectors summing to k - j(cap + 1).",
               "Inclusion-exclusion then gives <code>sum over j of (-1)<sup>j</sup> C(n, j) C(k - j(cap+1) + n - 1, n - 1)</code>. Only j up to k / (cap + 1) contributes, and j is at most n, so the sum has at most min(n, k) + 1 terms.",
               "Factorials up to k + n - 1 with inverse factorials give every binomial in O(1). The total time is O(n + k) and the space is O(n + k). A small dynamic programme over the kinds is the natural brute-force cross-check."],
    time="O(n + k)", space="O(n + k)",
    solution='''def countBoundedMultisets(n, k, cap):
    MOD = 10 ** 9 + 7
    top = n + k
    fact = [1] * (top + 1)
    for i in range(1, top + 1):
        fact[i] = fact[i - 1] * i % MOD
    inv = [1] * (top + 1)
    inv[top] = pow(fact[top], MOD - 2, MOD)
    for i in range(top, 0, -1):
        inv[i - 1] = inv[i] * i % MOD

    def comb(a, b):
        if b < 0 or b > a:
            return 0
        return fact[a] * inv[b] % MOD * inv[a - b] % MOD

    total = 0
    for j in range(n + 1):
        rem = k - j * (cap + 1)
        if rem < 0:
            break
        term = comb(n, j) * comb(rem + n - 1, n - 1) % MOD
        total = (total - term) % MOD if j % 2 else (total + term) % MOD
    return total % MOD
''',
    tests=[[1, 0, 0], [1, 5, 5], [1, 5, 4], [2, 2, 1], [3, 4, 2], [4, 6, 6], [3, 0, 0], [5, 12, 3], [7, 30, 4],
           [50, 20, 1000], [300, 500, 2], [5, 0, 0], [2, 2, 0], [6, 9, 2], [2000, 20000, 3], [2000, 20000, 20000],
           [1000, 10000, 50], [1, 20000, 20000]],
)


def b_bounded_multisets(n, k, cap):
    # kinds one at a time: dp[s] = number of ways to reach total s using the kinds seen so far
    dp = [1] + [0] * k
    for _ in range(n):
        new = [0] * (k + 1)
        for s in range(k + 1):
            new[s] = sum(dp[s - x] for x in range(0, min(cap, s) + 1))
        dp = new
    return dp[k] % MOD


CHECKS["bounded-multiset-count"] = (
    b_bounded_multisets,
    lambda r: [r.randint(1, 5), r.randint(0, 8), r.randint(0, 4)],
    "exact",
)
VALIDATE["bounded-multiset-count"] = _vspec((1, 2000), (0, 20000), (0, 20000))

p = add(
    id="dyck-paths-height-cap-peaks", title="Dyck Paths Under a Height Cap", diff="Hard", topic=TOPIC, tier="extra",
    fn="dyckHeightLimitedPeaks", params=[("n", "int"), ("h", "int"), ("k", "int")], ret="int", cmp="exact",
    desc="<p>A Dyck path of semilength <code>n</code> is a sequence of <code>n</code> <code>U</code> steps and <code>n</code> <code>D</code> steps in which no prefix has more <code>D</code> steps than <code>U</code> steps. A <em>peak</em> is a <code>U</code> step immediately followed by a <code>D</code> step. Count the Dyck paths of semilength <code>n</code> that never rise above height <code>h</code> and have exactly <code>k</code> peaks, modulo <code>1,000,000,007</code>.</p><pre>n = 2, h = 1, k = 1 -> 0   (the only path under height 1 is UDUD, with 2 peaks)\nn = 2, h = 1, k = 2 -> 1\nn = 3, h = 2, k = 2 -> 3</pre>",
    constraints=["1 &le; n &le; 25", "1 &le; h &le; n", "1 &le; k &le; n"],
    hints=["Walk along the path one step at a time. The state you need is the current height, the number of peaks so far, and whether the previous step was U, because a peak is a U immediately followed by a D.",
           "Keep the number of ways to reach each state after t steps. Only the states with height at most h and at most k peaks matter, since peaks never decrease.",
           "After 2n steps, read off the states at height 0 with exactly k peaks. Every path that ends at height 0 after 2n steps has exactly n U steps automatically."],
    editorial=["Process the 2n steps in order and keep a table indexed by (height, peaks, last step). A U step is allowed when the height is below h and moves to height + 1. A D step is allowed when the height is positive; it adds a peak exactly when the previous step was U.",
               "Once the table has been advanced 2n times, the answer is the number of paths sitting at height 0 with exactly k peaks, summed over the last-step flag. Dropping states with more than k peaks keeps the table small.",
               "The work is O(n * h * k) time with O(h * k) memory per step. A plain recursion with memoisation over (steps left, height, peaks, last step) is an equally valid cross-check, and both agree with the closed form when the cap is at least n."],
    time="O(n * h * k)", space="O(h * k)",
    solution='''def dyckHeightLimitedPeaks(n, h, k):
    MOD = 10 ** 9 + 7
    # dp[height][peaks][last] where last = 1 when the previous step was U
    dp = [[[0, 0] for _ in range(k + 1)] for _ in range(h + 1)]
    dp[0][0][0] = 1
    for _ in range(2 * n):
        nd = [[[0, 0] for _ in range(k + 1)] for _ in range(h + 1)]
        for height in range(h + 1):
            for pk in range(k + 1):
                for last in range(2):
                    c = dp[height][pk][last]
                    if not c:
                        continue
                    if height < h:
                        nd[height + 1][pk][1] = (nd[height + 1][pk][1] + c) % MOD
                    if height > 0:
                        npk = pk + 1 if last == 1 else pk
                        if npk <= k:
                            nd[height - 1][npk][0] = (nd[height - 1][npk][0] + c) % MOD
        dp = nd
    return (dp[0][k][0] + dp[0][k][1]) % MOD
''',
    tests=[[1, 1, 1], [2, 1, 1], [2, 1, 2], [2, 2, 1], [3, 2, 2], [3, 3, 3], [4, 2, 2], [5, 5, 3], [6, 3, 2],
           [8, 4, 4], [10, 3, 5], [12, 6, 3], [20, 4, 6], [25, 25, 12], [25, 5, 8], [25, 12, 25], [25, 1, 1],
           [25, 25, 1], [25, 1, 25]],
)


def b_height_peaks(n, h, k):
    @lru_cache(None)
    def go(steps, height, peaks, last):
        if steps == 0:
            return 1 if (height == 0 and peaks == k) else 0
        total = 0
        if height < h:
            total += go(steps - 1, height + 1, peaks, "U")
        if height > 0:
            total += go(steps - 1, height - 1, peaks + (1 if last == "U" else 0), "D")
        return total
    return go(2 * n, 0, 0, "D") % MOD


CHECKS["dyck-paths-height-cap-peaks"] = (
    b_height_peaks,
    lambda r: (lambda n: [n, r.randint(1, n), r.randint(1, n)])(r.randint(1, 7)),
    "exact",
)
VALIDATE["dyck-paths-height-cap-peaks"] = _vspec((1, 25), (1, 25), (1, 25))
