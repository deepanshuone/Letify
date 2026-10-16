"""Problems: probability-style counting with integers (expected values, exact fractions, restricted arrangements).
See data/lib.py for the registry."""
from fractions import Fraction
from itertools import combinations, permutations, product
from math import comb, gcd

from lib import add, rnd, CHECKS, VALIDATE, gen_arr  # noqa: F401

MOD = 1000000007
INT_MAX = 2 ** 31 - 1


def _frac(f):
    return f"{f.numerator}/{f.denominator}"


# ---------------------------------------------------------------- EASY

p = add(
    id="same-color-pair-probability", tier="extra", title="Chance Two Drawn Balls Match", diff="Easy", topic="Math & Bit Manipulation",
    fn="sameColorPairProbability", params=[("counts", "int[]")], ret="string", cmp="exact",
    desc="<p>A bag holds balls of several colours. <code>counts[i]</code> is the number of balls of colour <code>i</code>. Two different balls are drawn at random, one after the other, without replacement, and every pair of distinct balls is equally likely.</p><p>Return the probability that both balls have the same colour, as a reduced fraction written <code>p/q</code> with no spaces. If the probability is 0, return <code>0/1</code>.</p><pre>counts = [2, 1]     -> 1/3\ncounts = [1, 1, 1]  -> 0/1\ncounts = [4]        -> 1/1</pre>",
    constraints=["1 &le; counts.length &le; 100,000", "0 &le; counts[i] &le; 2<sup>31</sup> - 1", "The total number of balls is at least 2"],
    hints=["Count ordered pairs of distinct balls. How many of them are both red, both blue, and so on, for a colour with <code>c</code> balls?",
           "A colour with <code>c</code> balls gives <code>c * (c - 1)</code> ordered pairs of distinct balls of that colour. The total number of ordered pairs of distinct balls is <code>T * (T - 1)</code>, where <code>T</code> is the total.",
           "Divide the sum of <code>c * (c - 1)</code> over all colours by <code>T * (T - 1)</code>, then reduce the fraction with <code>Fraction</code> or <code>gcd</code>."],
    editorial=["Order the two draws. There are <code>T * (T - 1)</code> equally likely ordered pairs of distinct balls, where <code>T</code> is the total number of balls. Among them, a colour with <code>c</code> balls contributes <code>c * (c - 1)</code> ordered pairs in which both balls have that colour. Summing over the colours gives the favourable count, and the ratio is the probability.",
               "Python's <code>Fraction</code> reduces the ratio automatically. Its numerator and denominator are at most a few hundred bits even for the largest inputs, so exact integer arithmetic is cheap. A single pass over <code>counts</code> is enough."],
    time="O(n)", space="O(1)",
    solution='''from fractions import Fraction

def sameColorPairProbability(counts):
    total = sum(counts)
    same = sum(c * (c - 1) for c in counts)
    f = Fraction(same, total * (total - 1))
    return f"{f.numerator}/{f.denominator}"
''',
    tests=[[[2, 1]], [[1, 1, 1]], [[4]], [[0, 2, 0]], [[2, 2]], [[1, 0, 0, 1]], [[3, 3, 3]], [[5, 0, 1]],
           [[1000000000, 1000000000]], [[2147483647, 1]], [[0, 0, 0, 7]], [[3, 0, 2, 0, 9]]],
)


def b_match(counts):
    balls = [i for i, c in enumerate(counts) for _ in range(c)]
    n = len(balls)
    same = sum(1 for i in range(n) for j in range(n) if i != j and balls[i] == balls[j])
    return _frac(Fraction(same, n * (n - 1)))


def g_match(r):
    counts = [r.randint(0, 4) for _ in range(r.randint(1, 4))]
    if sum(counts) < 2:
        counts.append(2)
    return [counts]


def v_match(tests):
    for t in tests:
        counts = t["args"][0]
        assert 1 <= len(counts) <= 100000
        assert all(0 <= c <= INT_MAX for c in counts) and sum(counts) >= 2


CHECKS["same-color-pair-probability"] = (b_match, g_match, "exact")
VALIDATE["same-color-pair-probability"] = v_match

p = add(
    id="outfit-choice-count", title="Outfit Combinations", diff="Easy", topic="Math & Bit Manipulation",
    fn="countOutfits", params=[("counts", "int[]")], ret="int", cmp="exact",
    desc="<p>You have clothes grouped into categories. <code>counts[i]</code> is the number of items in category <code>i</code>. An outfit takes at most one item from each category, and it must contain at least one item.</p><p>Return the number of different outfits, modulo <code>1,000,000,007</code>.</p><pre>counts = [1, 1, 1] -> 7\ncounts = [2, 3]    -> 11\ncounts = [0, 5]    -> 5\ncounts = [0, 0]    -> 0</pre>",
    constraints=["1 &le; counts.length &le; 100,000", "0 &le; counts[i] &le; 10<sup>9</sup>"],
    hints=["For one category with <code>c</code> items, how many choices are there if you may also take nothing from it?",
           "Choices in different categories are independent, so the numbers of options multiply.",
           "Multiply <code>(counts[i] + 1)</code> over all categories, then subtract 1 to remove the empty outfit."],
    editorial=["For each category there are <code>c + 1</code> options: one of its <code>c</code> items, or nothing. Choices made in different categories do not interact, so the total number of combinations is the product of <code>c + 1</code> over all categories. That product includes the outfit that takes nothing from every category, so the answer is the product minus 1.",
               "Reduce modulo 1,000,000,007 while multiplying so the intermediate values stay small. The subtraction is done last, adding <code>MOD</code> if needed to keep the result non-negative."],
    time="O(n)", space="O(1)",
    solution='''def countOutfits(counts):
    MOD = 1000000007
    ways = 1
    for c in counts:
        ways = ways * (c + 1) % MOD
    return (ways - 1) % MOD
''',
    tests=[[[1, 1, 1]], [[2, 3]], [[0, 5]], [[0, 0]], [[7]], [[0, 4, 0, 2]], [[1000000000, 1000000000]],
           [[1] * 30000], [[9] * 5], [[3, 1, 4, 1, 5, 9, 2, 6]]],
)


def b_outfit(counts):
    total = 0
    for pick in product(*[range(c + 1) for c in counts]):
        if any(pick):
            total += 1
    return total % MOD


def g_outfit(r):
    return [[r.randint(0, 3) for _ in range(r.randint(1, 3))]]


def v_outfit(tests):
    for t in tests:
        counts = t["args"][0]
        assert 1 <= len(counts) <= 100000 and all(0 <= c <= 10 ** 9 for c in counts)


CHECKS["outfit-choice-count"] = (b_outfit, g_outfit, "exact")
VALIDATE["outfit-choice-count"] = v_outfit

# ---------------------------------------------------------------- MEDIUM

p = add(
    id="expected-draws-distinct-kinds", title="Collecting Distinct Kinds: Expected Draws", diff="Medium", topic="Math & Bit Manipulation",
    fn="expectedDrawsMod", params=[("n", "int"), ("k", "int")], ret="int", cmp="exact",
    desc="<p>A bag has <code>n</code> different kinds of tickets, and a draw takes a uniformly random kind each time (the drawn ticket goes back, so kinds can repeat). Let <code>E</code> be the expected number of draws until at least <code>k</code> different kinds have been seen.</p><p><code>E</code> is a fraction <code>p / q</code> in lowest terms. Return <code>p * q<sup>-1</sup></code> modulo <code>1,000,000,007</code>, that is, the residue that <code>p / q</code> stands for in modular arithmetic.</p><pre>n = 2, k = 2 -> 3          (E = 2/2 + 2/1 = 3)\nn = 3, k = 3 -> 500000009  (E = 11/2, and 2 * 500000009 = 11 mod p)\nn = 4, k = 1 -> 1</pre>",
    constraints=["1 &le; k &le; n &le; 200,000"],
    hints=["Once <code>i</code> kinds have been seen, each new draw is a new kind with probability <code>(n - i) / n</code>. How many draws does it take, on average, to see the next new kind?",
           "The expected wait for a new kind from state <code>i</code> is <code>n / (n - i)</code>. Expectations of consecutive stages add up, so sum over <code>i = 0 .. k - 1</code>.",
           "Build the modular inverses of <code>1 .. n</code> with the linear recurrence <code>inv[i] = -(MOD // i) * inv[MOD % i]</code> rather than calling <code>pow</code> for each term."],
    editorial=["Count the draws in stages. Stage <code>i</code> starts when <code>i</code> different kinds have been seen and ends when the next new kind appears. In that stage each draw succeeds with probability <code>(n - i) / n</code>, so the number of draws in the stage is geometric with mean <code>n / (n - i)</code>. The expected total is the sum of these means for <code>i = 0 .. k - 1</code>, which is <code>E = sum n / (n - i)</code> by linearity of expectation.",
               "All denominators <code>n - i</code> are between 1 and <code>n</code>, far below the prime 1,000,000,007, so each one has a modular inverse. Computing the inverses one by one with fast exponentiation would cost O(n log MOD). A single linear pass that fills an inverse table costs O(n) and is also short to write.",
               "The brute-force check solves the same process as a Markov chain with exact fractions: a backward recurrence on the number of kinds seen, which avoids the closed form entirely."],
    time="O(n)", space="O(n)",
    solution='''def expectedDrawsMod(n, k):
    MOD = 1000000007
    inv = [0] * (n + 2)
    inv[1] = 1
    for i in range(2, n + 1):
        inv[i] = (MOD - (MOD // i) * inv[MOD % i] % MOD) % MOD
    total = 0
    for i in range(k):
        total = (total + n * inv[n - i]) % MOD
    return total
''',
    tests=[[1, 1], [2, 1], [2, 2], [3, 3], [4, 1], [5, 2], [10, 10], [6, 4], [1000, 1000], [200000, 1],
           [200000, 200000], [199999, 123456], [100000, 77777]],
)


def b_coupon(n, k):
    MOD = 1000000007
    E = Fraction(0)
    for d in range(k - 1, -1, -1):
        E = (n + (n - d) * E) / (n - d)
    return E.numerator * pow(E.denominator, MOD - 2, MOD) % MOD


def g_coupon(r):
    n = r.randint(1, 8)
    return [n, r.randint(1, n)]


def v_coupon(tests):
    for t in tests:
        n, k = t["args"]
        assert 1 <= k <= n <= 200000


CHECKS["expected-draws-distinct-kinds"] = (b_coupon, g_coupon, "exact")
VALIDATE["expected-draws-distinct-kinds"] = v_coupon

p = add(
    id="dice-pair-sum-probability", title="Two Dice: Exact Sum Probability", diff="Medium", topic="Math & Bit Manipulation",
    fn="diceSumProbability", params=[("a", "int"), ("b", "int"), ("target", "int")], ret="string", cmp="exact",
    desc="<p>Two fair dice are rolled. The first die has faces <code>1 .. a</code> and the second has faces <code>1 .. b</code>, and every face of each die is equally likely. Find the probability that the two faces add up to <code>target</code>.</p><p>Return the probability as a reduced fraction <code>p/q</code> with no spaces. If the sum is impossible, return <code>0/1</code>.</p><pre>a = 6, b = 6, target = 7  -> 1/6\na = 6, b = 6, target = 2  -> 1/36\na = 3, b = 5, target = 8  -> 1/15\na = 6, b = 6, target = 13 -> 0/1</pre>",
    constraints=["1 &le; a, b &le; 10<sup>9</sup>", "-2<sup>31</sup> &le; target &le; 2<sup>31</sup> - 1"],
    hints=["Fix the value on the first die, <code>x</code>. Then the second die must show <code>target - x</code>, which is possible only if that number is between 1 and <code>b</code>.",
           "The valid first-die values form one interval, so you do not need to loop over them. Intersect <code>[1, a]</code> with <code>[target - b, target - 1]</code>.",
           "The number of favourable outcomes is the length of that intersection, and the number of equally likely outcomes is <code>a * b</code>. Reduce the fraction at the end."],
    editorial=["Let <code>x</code> be the first die and <code>y</code> the second. The pair is favourable exactly when <code>x + y = target</code>, which means <code>y = target - x</code>. The constraints are <code>1 &le; x &le; a</code> and <code>1 &le; target - x &le; b</code>, i.e. <code>target - b &le; x &le; target - 1</code>. So <code>x</code> ranges over the integer interval with lower bound <code>max(1, target - b)</code> and upper bound <code>min(a, target - 1)</code>.",
               "The number of favourable outcomes is the length of that interval, or 0 if it is empty. Each outcome has probability <code>1 / (a * b)</code>. Python's <code>Fraction</code> normalises the answer, and because only a few big-integer operations are needed the answer is O(1) apart from the reduction."],
    time="O(1)", space="O(1)",
    solution='''from fractions import Fraction

def diceSumProbability(a, b, target):
    lo = max(1, target - b)
    hi = min(a, target - 1)
    count = max(0, hi - lo + 1)
    f = Fraction(count, a * b)
    return f"{f.numerator}/{f.denominator}"
''',
    tests=[[6, 6, 7], [6, 6, 2], [6, 6, 13], [1, 1, 2], [3, 5, 1], [3, 5, 8], [4, 4, 5], [2, 7, 9], [1, 6, 7],
           [1000000000, 1000000000, 1000000000], [1000000000, 1, 1000000001], [7, 9, -4], [5, 5, 10]],
)


def b_dice(a, b, t):
    cnt = sum(1 for x in range(1, a + 1) for y in range(1, b + 1) if x + y == t)
    return _frac(Fraction(cnt, a * b))


def g_dice(r):
    return [r.randint(1, 6), r.randint(1, 6), r.randint(-1, 13)]


def v_dice(tests):
    for t in tests:
        a, b, _ = t["args"]
        assert 1 <= a <= 10 ** 9 and 1 <= b <= 10 ** 9


CHECKS["dice-pair-sum-probability"] = (b_dice, g_dice, "exact")
VALIDATE["dice-pair-sum-probability"] = v_dice

p = add(
    id="xor-subset-hit-probability", title="Random Subset Hitting a Target XOR", diff="Medium", topic="Math & Bit Manipulation",
    fn="xorSubsetProbability", params=[("nums", "int[]"), ("target", "int")], ret="string", cmp="exact",
    desc="<p>Each index of <code>nums</code> is chosen independently with probability one half, so every one of the <code>2<sup>n</sup></code> subsets of indices is equally likely (the empty subset included). Find the probability that the bitwise XOR of the chosen values equals <code>target</code>.</p><p>Return it as a reduced fraction <code>p/q</code> with no spaces. Remember that the XOR of an empty subset is 0.</p><pre>nums = [1, 2, 3], target = 0 -> 1/4\nnums = [1, 2, 3], target = 4 -> 0/1\nnums = [5], target = 5       -> 1/2\nnums = [], target = 0        -> 1/1</pre>",
    constraints=["0 &le; nums.length &le; 5,000", "0 &le; nums[i] &le; 10<sup>9</sup>", "0 &le; target &le; 10<sup>9</sup>"],
    hints=["Gaussian elimination over GF(2) works for XOR. Build a basis of the values: keep at most one value per leading bit. Let <code>r</code> be the number of basis vectors.",
           "Every value in the span of the basis is produced by exactly <code>2<sup>n - r</sup></code> of the subsets, and values outside the span by none. So the probability is <code>2<sup>-r</sup></code> when the target is in the span.",
           "To test membership, reduce the target by the basis from the highest bit down. The target is in the span exactly when it reduces to 0."],
    editorial=["Look at the linear map from subsets to XOR values. Think of each value as a vector over GF(2). The set of all XORs of subsets is the span of the vectors, and a basis of the span has <code>r</code> vectors. Gaussian elimination builds such a basis in O(n * 30) time: insert each value by clearing its highest set bit with an existing basis vector, or store it as a new basis vector under that bit.",
               "Fix a target <code>t</code> in the span. Choose the subsets' membership for all indices except a set of <code>r</code> pivot indices freely; the pivot choices are then forced, so exactly <code>2<sup>n - r</sup></code> subsets give XOR <code>t</code>. Dividing by the <code>2<sup>n</sup></code> total gives <code>1 / 2<sup>r</sup></code>. If <code>t</code> is outside the span, no subset works and the answer is <code>0/1</code>.",
               "The membership test reduces <code>t</code> from the highest bit down: whenever bit <code>b</code> is set and there is a basis vector with leading bit <code>b</code>, XOR it in. If the result is 0 the target is in the span. The empty subset makes 0 always reachable, so the answer for target 0 is <code>1 / 2<sup>r</sup></code>."],
    time="O(n * 30)", space="O(30)",
    solution='''def xorSubsetProbability(nums, target):
    basis = [0] * 31
    for x in nums:
        for b in range(30, -1, -1):
            if (x >> b) & 1:
                if basis[b]:
                    x ^= basis[b]
                else:
                    basis[b] = x
                    break
    rank = sum(1 for v in basis if v)
    t = target
    for b in range(30, -1, -1):
        if (t >> b) & 1 and basis[b]:
            t ^= basis[b]
    if t != 0:
        return "0/1"
    return f"1/{2 ** rank}"
''',
    tests=[[[1, 2, 3], 0], [[1, 2, 3], 3], [[1, 2, 3], 4], [[5], 5], [[5], 0], [[], 0], [[], 1], [[0, 0, 0], 0],
           [[2, 2, 2, 2], 2], [[6, 3, 5], 6], [[10, 20, 30, 40], 60], [[7, 7, 1, 8], 15]],
)
_r = rnd(501)
_nums = [_r.randint(0, 10 ** 9) for _ in range(4000)]
_t = 0
for _x in _nums[:20]:
    _t ^= _x
p["tests"].append([_nums, _t])
p["tests"].append([_nums, _r.randint(0, 10 ** 9)])


def b_xorprob(nums, target):
    n = len(nums)
    cnt = 0
    for mask in range(1 << n):
        x = 0
        for i in range(n):
            if (mask >> i) & 1:
                x ^= nums[i]
        if x == target:
            cnt += 1
    return _frac(Fraction(cnt, 1 << n))


def g_xorprob(r):
    nums = [r.randint(0, 7) for _ in range(r.randint(0, 6))]
    return [nums, r.randint(0, 7)]


def v_xorprob(tests):
    for t in tests:
        nums, target = t["args"]
        assert 0 <= len(nums) <= 5000
        assert all(0 <= v <= 10 ** 9 for v in nums) and 0 <= target <= 10 ** 9


CHECKS["xor-subset-hit-probability"] = (b_xorprob, g_xorprob, "exact")
VALIDATE["xor-subset-hit-probability"] = v_xorprob

p = add(
    id="lottery-exact-match-probability", title="Lottery: Exact Match Probability", diff="Medium", topic="Math & Bit Manipulation",
    fn="exactMatchProbability", params=[("m", "int"), ("k", "int"), ("j", "int")], ret="string", cmp="exact",
    desc="<p>A lottery draws <code>k</code> different numbers out of <code>1 .. m</code>, every <code>k</code>-subset being equally likely. A ticket holds <code>k</code> fixed numbers. Find the probability that exactly <code>j</code> of the ticket's numbers are among the drawn numbers.</p><p>Return the probability as a reduced fraction <code>p/q</code> with no spaces.</p><pre>m = 5,  k = 2, j = 1  -> 3/5\nm = 6,  k = 3, j = 0  -> 1/20\nm = 49, k = 6, j = 6  -> 1/13983816</pre>",
    constraints=["1 &le; k &le; m &le; 2,000", "0 &le; j &le; k"],
    hints=["Count the winning draws, out of all <code>C(m, k)</code>, that share exactly <code>j</code> numbers with the ticket.",
           "Choose which <code>j</code> ticket numbers are drawn: <code>C(k, j)</code> ways. The other <code>k - j</code> drawn numbers must avoid the ticket, so they come from the <code>m - k</code> numbers outside it: <code>C(m - k, k - j)</code> ways.",
           "Divide <code>C(k, j) * C(m - k, k - j)</code> by <code>C(m, k)</code> and reduce the fraction. <code>math.comb</code> returns 0 when the lower index is too large."],
    editorial=["Every winning draw is a <code>k</code>-subset of <code>1 .. m</code>, so there are <code>C(m, k)</code> equally likely outcomes. The favourable draws are built in two independent parts: the <code>j</code> ticket numbers that are drawn, which can be chosen in <code>C(k, j)</code> ways, and the <code>k - j</code> non-ticket numbers that are drawn, chosen from the <code>m - k</code> numbers not on the ticket in <code>C(m - k, k - j)</code> ways. The product counts each favourable draw exactly once.",
               "This is the hypergeometric distribution. Python's big integers hold the binomials exactly, so there is no floating-point error, and <code>Fraction</code> reduces the result. When <code>k - j</code> exceeds <code>m - k</code> the second binomial is 0, and the probability is correctly 0."],
    time="O(m)", space="O(m)",
    solution='''from fractions import Fraction
from math import comb

def exactMatchProbability(m, k, j):
    f = Fraction(comb(k, j) * comb(m - k, k - j), comb(m, k))
    return f"{f.numerator}/{f.denominator}"
''',
    tests=[[6, 6, 6], [5, 2, 1], [6, 3, 0], [1049, 6, 6], [1049, 6, 3], [1049, 6, 0], [10, 3, 1], [5, 2, 0], [1, 1, 1],
           [1, 1, 0], [200, 1, 1], [1200, 100, 50], [200, 200, 200], [1080, 40, 20]],
)


def b_lottery(m, k, j):
    ticket = set(range(1, k + 1))
    cnt = tot = 0
    for win in combinations(range(1, m + 1), k):
        tot += 1
        if len(ticket & set(win)) == j:
            cnt += 1
    return _frac(Fraction(cnt, tot))


def g_lottery(r):
    m = r.randint(1, 8)
    k = r.randint(1, m)
    return [m, k, r.randint(0, k)]


def v_lottery(tests):
    for t in tests:
        m, k, j = t["args"]
        assert 1 <= k <= m <= 2000 and 0 <= j <= k


CHECKS["lottery-exact-match-probability"] = (b_lottery, g_lottery, "exact")
VALIDATE["lottery-exact-match-probability"] = v_lottery

p = add(
    id="expected-max-of-dice", tier="extra", title="Expected Maximum of Dice", diff="Medium", topic="Math & Bit Manipulation",
    fn="expectedMaxOfDice", params=[("s", "int"), ("k", "int")], ret="string", cmp="exact",
    desc="<p>Roll <code>k</code> independent fair dice, each with faces <code>1 .. s</code>. Let <code>M</code> be the largest face shown. Find the expected value of <code>M</code>.</p><p>Return it as a reduced fraction <code>p/q</code> with no spaces.</p><pre>s = 6, k = 1 -> 7/2\ns = 2, k = 2 -> 7/4   (outcomes give maxima 1, 2, 2, 2)\ns = 1, k = 9 -> 1/1</pre>",
    constraints=["1 &le; s &le; 2,000", "1 &le; k &le; 60"],
    hints=["For a whole-number variable, <code>E[M] = sum of P(M &ge; v)</code> over <code>v = 1 .. s</code>. The event <code>M &lt; v</code> is easier to count than <code>M &ge; v</code>.",
           "<code>P(M &le; t) = (t / s)<sup>k</sup></code>, because every die must show at most <code>t</code>.",
           "Combine the terms over the common denominator <code>s<sup>k</sup></code>, which gives <code>(s<sup>k+1</sup> - sum of t<sup>k</sup> for t = 0 .. s-1) / s<sup>k</sup></code>."],
    editorial=["For a random variable with values from 1 to <code>s</code>, the expectation equals the sum over <code>v = 1 .. s</code> of <code>P(M &ge; v) = 1 - P(M &le; v - 1)</code>. Each die shows at most <code>t</code> with probability <code>t / s</code>, and the dice are independent, so <code>P(M &le; t) = (t / s)<sup>k</sup></code>.",
               "Substituting gives <code>E = s - (1 / s<sup>k</sup>) * sum of t<sup>k</sup></code> for <code>t = 0 .. s-1</code>. Writing <code>s</code> over <code>s<sup>k</sup></code> as <code>s<sup>k+1</sup> / s<sup>k</sup></code> turns this into one fraction, whose numerator and denominator are exact integers. The numbers are large (about 140 digits at the top of the range), but Python handles them easily and the reduction is done by <code>Fraction</code>.",
               "The brute-force check enumerates every outcome for tiny <code>s</code> and <code>k</code> and averages the maximum directly."],
    time="O(s * k) big-integer operations", space="O(1)",
    solution='''from fractions import Fraction

def expectedMaxOfDice(s, k):
    num = s ** (k + 1) - sum(t ** k for t in range(s))
    f = Fraction(num, s ** k)
    return f"{f.numerator}/{f.denominator}"
''',
    tests=[[1, 1], [6, 1], [2, 2], [6, 2], [1, 60], [3, 3], [4, 4], [200, 2], [1500, 60], [2000, 1], [1050, 40], [1012, 7]],
)


def b_maxdice(s, k):
    tot = 0
    for o in product(range(1, s + 1), repeat=k):
        tot += max(o)
    return _frac(Fraction(tot, s ** k))


def g_maxdice(r):
    return [r.randint(1, 4), r.randint(1, 3)]


def v_maxdice(tests):
    for t in tests:
        s, k = t["args"]
        assert 1 <= s <= 2000 and 1 <= k <= 60


CHECKS["expected-max-of-dice"] = (b_maxdice, g_maxdice, "exact")
VALIDATE["expected-max-of-dice"] = v_maxdice

p = add(
    id="all-birthdays-distinct-probability", title="All Birthdays Different", diff="Medium", topic="Math & Bit Manipulation",
    fn="allDistinctProbability", params=[("d", "int"), ("n", "int")], ret="string", cmp="exact",
    desc="<p>There are <code>d</code> equally likely days in a year. Each of <code>n</code> people picks a day independently and uniformly at random. Find the probability that no two people pick the same day.</p><p>Return it as a reduced fraction <code>p/q</code> with no spaces. If <code>n = 0</code> the probability is 1.</p><pre>d = 365, n = 2 -> 364/365\nd = 10,  n = 3 -> 18/25\nd = 2,   n = 3 -> 0/1</pre>",
    constraints=["1 &le; d &le; 10<sup>9</sup>", "0 &le; n &le; 200"],
    hints=["Count the sequences of <code>n</code> days with all days different: the first person has <code>d</code> choices, the next has <code>d - 1</code>, and so on.",
           "The number of equally likely sequences is <code>d<sup>n</sup></code>. The probability is the falling product <code>d * (d - 1) * ... * (d - n + 1)</code> divided by <code>d<sup>n</sup></code>.",
           "If <code>n &gt; d</code> the falling product contains a zero factor, so the answer is 0. Otherwise multiply the factors, then divide by the gcd of numerator and denominator."],
    editorial=["Each of the <code>d<sup>n</sup></code> sequences of days is equally likely. A sequence has all days different exactly when the choice for person <code>i</code> avoids the <code>i</code> days already taken, which leaves <code>d - i</code> options for person <code>i</code> (counting from 0). So the favourable sequences number <code>d * (d - 1) * ... * (d - n + 1)</code>, and the probability is that falling product over <code>d<sup>n</sup></code>.",
               "When <code>n &gt; d</code> one factor is zero, which the loop handles naturally if you stop early and return <code>0/1</code>. The numerator and denominator can have about 1,800 digits for the largest input, which is fine for Python's big integers. The reduction uses <code>math.gcd</code> once at the end."],
    time="O(n) big-integer multiplications", space="O(n) digits",
    solution='''from math import gcd

def allDistinctProbability(d, n):
    if n > d:
        return "0/1"
    num = 1
    for i in range(n):
        num *= d - i
    den = d ** n
    g = gcd(num, den)
    return f"{num // g}/{den // g}"
''',
    tests=[[365, 2], [10, 3], [2, 3], [1, 1], [1, 2], [1000000000, 1], [1000000000, 2], [100, 0], [1365, 23],
           [7, 5], [1052, 5], [1000000000, 200], [1030, 31]],
)


def b_birthday(d, n):
    good = sum(1 for t in product(range(d), repeat=n) if len(set(t)) == n)
    return _frac(Fraction(good, d ** n))


def g_birthday(r):
    return [r.randint(1, 4), r.randint(0, 5)]


def v_birthday(tests):
    for t in tests:
        d, n = t["args"]
        assert 1 <= d <= 10 ** 9 and 0 <= n <= 200


CHECKS["all-birthdays-distinct-probability"] = (b_birthday, g_birthday, "exact")
VALIDATE["all-birthdays-distinct-probability"] = v_birthday

# ---------------------------------------------------------------- HARD

p = add(
    id="gamblers-ruin-escape-probability", tier="extra", title="Gambler's Ruin Probability", diff="Hard", topic="Math & Bit Manipulation",
    fn="ruinProbability", params=[("a", "int"), ("b", "int"), ("start", "int"), ("target", "int")], ret="string", cmp="exact",
    desc="<p>You begin with <code>start</code> units of money. In each round you win one unit with probability <code>a / (a + b)</code> and lose one unit otherwise. You stop when your money reaches <code>0</code> (ruin) or <code>target</code> (success).</p><p>Find the probability of reaching <code>target</code> before <code>0</code>, as a reduced fraction <code>p/q</code> with no spaces.</p><pre>a = 1, b = 1, start = 1, target = 4 -> 1/4\na = 1, b = 2, start = 1, target = 2 -> 1/3\na = 1, b = 1, start = 0, target = 5 -> 0/1</pre>",
    constraints=["1 &le; a, b &le; 9", "1 &le; target &le; 60", "0 &le; start &le; target"],
    hints=["Let <code>P(i)</code> be the success probability from money <code>i</code>. It satisfies <code>P(i) = p * P(i + 1) + q * P(i - 1)</code> with <code>P(0) = 0</code> and <code>P(target) = 1</code>, where <code>p = a / (a + b)</code> and <code>q = b / (a + b)</code>.",
           "Let <code>r = q / p = b / a</code>. The equation becomes <code>P(i + 1) - P(i) = r * (P(i) - P(i - 1))</code>, so the differences form a geometric sequence. Summing them gives <code>P(i) = (1 - r<sup>i</sup>) / (1 - r<sup>target</sup>)</code>.",
           "When <code>a = b</code> then <code>r = 1</code> and the answer is simply <code>start / target</code>. Use <code>fractions.Fraction</code> so the arithmetic stays exact."],
    editorial=["Condition on the first round. With probability <code>p</code> you move up one unit and with probability <code>q</code> you move down one, so <code>P(i) = p P(i + 1) + q P(i - 1)</code> for <code>0 &lt; i &lt; target</code>, with boundary values <code>P(0) = 0</code> and <code>P(target) = 1</code>.",
               "Write <code>r = q / p = b / a</code>. Rearranging gives <code>P(i + 1) - P(i) = r * (P(i) - P(i - 1))</code>. So each step is <code>r</code> times the previous one, and the first step <code>P(1) - P(0) = P(1)</code> sets the scale. Summing the geometric series from 0 to <code>start - 1</code> and using <code>P(target) = 1</code> to fix the scale gives <code>P(start) = (1 - r<sup>start</sup>) / (1 - r<sup>target</sup>)</code> when <code>r</code> differs from 1, and <code>start / target</code> when it equals 1.",
               "The exact fraction can have around 57 digits in the numerator and denominator for the largest inputs. Python's <code>Fraction</code> keeps everything exact, so no rounding error can change the reduced answer. The brute-force check solves the linear system for <code>P</code> by Gaussian elimination instead, so it does not rely on the closed form."],
    time="O(log target) big-integer powers", space="O(1)",
    solution='''from fractions import Fraction

def ruinProbability(a, b, start, target):
    r = Fraction(b, a)
    if r == 1:
        f = Fraction(start, target)
    else:
        f = (1 - r ** start) / (1 - r ** target)
    return f"{f.numerator}/{f.denominator}"
''',
    tests=[[1, 1, 1, 4], [1, 2, 1, 2], [1, 1, 0, 5], [1, 1, 5, 5], [2, 3, 3, 6], [3, 1, 2, 5], [5, 5, 17, 60],
           [1, 9, 30, 60], [9, 1, 1, 60], [4, 7, 20, 60], [1, 1, 1, 1], [2, 2, 4, 9]],
)


def b_ruin(a, b, start, target):
    N = target
    if start == 0:
        return "0/1"
    if start == N:
        return "1/1"
    p = Fraction(a, a + b)
    q = Fraction(b, a + b)
    n = N - 1
    M = [[Fraction(0) for _ in range(n + 1)] for _ in range(n)]
    for i in range(1, N):
        row = i - 1
        M[row][row] += 1
        if i + 1 < N:
            M[row][i] -= p
        else:
            M[row][n] += p
        if i - 1 >= 1:
            M[row][i - 2] -= q
    for c in range(n):
        piv = next(x for x in range(c, n) if M[x][c] != 0)
        M[c], M[piv] = M[piv], M[c]
        pv = M[c][c]
        M[c] = [v / pv for v in M[c]]
        for x in range(n):
            if x != c and M[x][c] != 0:
                f = M[x][c]
                M[x] = [u - f * w for u, w in zip(M[x], M[c])]
    return _frac(M[start - 1][n])


def g_ruin(r):
    target = r.randint(1, 6)
    return [r.randint(1, 5), r.randint(1, 5), r.randint(0, target), target]


def v_ruin(tests):
    for t in tests:
        a, b, start, target = t["args"]
        assert 1 <= a <= 9 and 1 <= b <= 9 and 1 <= target <= 60 and 0 <= start <= target


CHECKS["gamblers-ruin-escape-probability"] = (b_ruin, g_ruin, "exact")
VALIDATE["gamblers-ruin-escape-probability"] = v_ruin

p = add(
    id="forbidden-cell-permutations", title="Permutations Avoiding Forbidden Cells", diff="Hard", topic="Math & Bit Manipulation",
    fn="countAvoidingPermutations", params=[("n", "int"), ("forbidden", "int[][]")], ret="int", cmp="exact",
    desc="<p>Consider permutations <code>p</code> of <code>0 .. n-1</code>, read as: row <code>i</code> is matched with column <code>p[i]</code>. Some cells of the <code>n x n</code> board are forbidden. Each pair <code>[r, c]</code> in <code>forbidden</code> is a forbidden cell, and a permutation is allowed only if none of its matched cells is forbidden.</p><p>Return the number of allowed permutations modulo <code>1,000,000,007</code>. The pairs in <code>forbidden</code> are distinct.</p><pre>n = 3, forbidden = []                         -> 6\nn = 2, forbidden = [[0,0]]                    -> 1\nn = 3, forbidden = [[0,0],[1,1],[2,2]]        -> 2</pre>",
    constraints=["0 &le; n &le; 12", "0 &le; forbidden.length &le; n * n", "forbidden[i].length = 2 and 0 &le; forbidden[i][0], forbidden[i][1] &lt; n", "All forbidden pairs are distinct"],
    hints=["Process the rows in order, and let a bitmask record which columns have already been used. The number of set bits tells you which row you are on.",
           "Let <code>dp[mask]</code> be the number of ways to fill the first <code>popcount(mask)</code> rows so that exactly the columns in <code>mask</code> are used. From a state, row <code>popcount(mask)</code> can take any unused column that is not forbidden for that row.",
           "For each row precompute a bitmask of forbidden columns. The transitions are then a single bit test per column, and the whole table has <code>2<sup>n</sup></code> states, which is small for <code>n &le; 12</code>."],
    editorial=["Assign the rows one at a time. After the first <code>k</code> rows have been assigned, the set of columns they use is a subset of size <code>k</code> of the <code>n</code> columns, and it is the only information the rest of the assignment depends on. That makes the subset a valid DP state, so the process is a walk on the lattice of bitmasks.",
               "Start with <code>dp[0] = 1</code>. For a state <code>mask</code> with <code>k = popcount(mask)</code>, row <code>k</code> may take any column <code>c</code> that is not in <code>mask</code> and is not forbidden in that row. Each such choice adds <code>dp[mask]</code> to <code>dp[mask | (1 &lt;&lt; c)]</code>. The answer is <code>dp[2<sup>n</sup> - 1]</code>.",
               "There are <code>2<sup>n</sup></code> states with at most <code>n</code> transitions each, so the time is O(n * 2<sup>n</sup>), about 50,000 steps for <code>n = 12</code>. The brute force enumerates all <code>n!</code> permutations for small <code>n</code>. Since the forbidden cells are only tested by a bit lookup per row, the list can be read in any order."],
    time="O(n * 2^n)", space="O(2^n)",
    solution='''def countAvoidingPermutations(n, forbidden):
    MOD = 1000000007
    bad = [0] * n
    for r, c in forbidden:
        bad[r] |= 1 << c
    full = (1 << n) - 1
    dp = [0] * (1 << n)
    dp[0] = 1
    for mask in range(1 << n):
        if dp[mask] == 0:
            continue
        row = bin(mask).count("1")
        if row >= n:
            continue
        allowed = full & ~mask & ~bad[row]
        while allowed:
            low = allowed & -allowed
            nxt = mask | low
            dp[nxt] = (dp[nxt] + dp[mask]) % MOD
            allowed ^= low
    return dp[full]
''',
    tests=[[3, []], [2, [[0, 0]]], [3, [[0, 0], [1, 1], [2, 2]]], [1, [[0, 0]]], [0, []], [1, []],
           [5, [[0, 1], [1, 2], [2, 3], [3, 4], [4, 0]]], [4, [[0, 0], [0, 1], [0, 2]]],
           [12, [[0, 0], [1, 2], [5, 7], [11, 11], [3, 4], [8, 8], [9, 1], [10, 10]]],
           [10, [[0, 0], [1, 2], [2, 4], [3, 6], [4, 8], [5, 1], [6, 3], [7, 5], [8, 7], [9, 9]]]],
)
_r = rnd(502)
_cells = [[i, j] for i in range(12) for j in range(12)]
_forb = [list(c) for c in _r.sample([tuple(c) for c in _cells], 30)]
p["tests"].append([12, _forb])
_forb = [list(c) for c in _r.sample([tuple(c) for c in _cells], 90)]
p["tests"].append([12, _forb])


def b_forb(n, forbidden):
    bad = set(map(tuple, forbidden))
    cnt = 0
    for perm in permutations(range(n)):
        if all((i, perm[i]) not in bad for i in range(n)):
            cnt += 1
    return cnt % MOD


def g_forb(r):
    n = r.randint(0, 5)
    cells = [(i, j) for i in range(n) for j in range(n)]
    forb = [list(c) for c in r.sample(cells, r.randint(0, len(cells)))]
    return [n, forb]


def v_forb(tests):
    for t in tests:
        n, forb = t["args"]
        assert 0 <= n <= 12 and len(forb) <= n * n
        assert len(set(map(tuple, forb))) == len(forb)
        assert all(len(c) == 2 and 0 <= c[0] < n and 0 <= c[1] < n for c in forb)


CHECKS["forbidden-cell-permutations"] = (b_forb, g_forb, "exact")
VALIDATE["forbidden-cell-permutations"] = v_forb
