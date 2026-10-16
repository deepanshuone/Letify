"""Problems: classic math puzzles (Josephus, water jugs, spirals, Pascal's triangle, amicable numbers and more). See data/lib.py for the registry."""
from math import gcd

from lib import add, rnd, CHECKS, VALIDATE, gen_arr  # noqa: F401

INT_MIN, INT_MAX = -(2 ** 31), 2 ** 31 - 1
MOD = 1_000_000_007


# ---------------------------------------------------------------- EASY

p = add(
    id="powers-of-three-sum", title="Sum of Distinct Powers of Three", diff="Easy", topic="Math & Bit Manipulation",
    fn="isSumOfPowersOfThree", params=[("n", "int")], ret="bool", cmp="exact",
    desc="<p>Return <code>true</code> if the positive integer <code>n</code> can be written as a sum of distinct powers of three, that is a sum of some of the numbers 3<sup>0</sup> = 1, 3<sup>1</sup> = 3, 3<sup>2</sup> = 9, 3<sup>3</sup> = 27, and so on. Each power may be used at most once.</p><pre>n = 12  &rarr;  true   (3 + 9)\nn = 21  &rarr;  false</pre>",
    constraints=["1 &le; n &le; 10,000,000"],
    hints=["Try a few small values by hand. Which of 1 to 13 can be built, and which cannot?",
           "Write n in base 3. What would a digit 2 in that representation mean?",
           "A digit 0 means that power is unused and a digit 1 means it is used once. A digit 2 would need two copies of the same power, which is not allowed."],
    editorial=["Every number has a unique base-3 representation, with digits 0, 1 or 2 in each position. If a digit is 0 or 1, that power of three is either left out or used once, which is exactly what the problem allows. If some digit is 2, the number would need two copies of that power, so no valid sum exists.",
               "The check reads base-3 digits from the bottom up and stops as soon as it finds a 2. It runs in O(log n) time and uses O(1) space."],
    time="O(log n)", space="O(1)",
    solution='''def isSumOfPowersOfThree(n):
    while n > 0:
        if n % 3 == 2:
            return False
        n //= 3
    return True
''',
    tests=[[1], [2], [3], [4], [9], [12], [21], [27], [28], [6561], [13122], [4782969], [9999999], [1000000], [7174453]],
)


def b_pow3(n):
    powers = []
    q = 1
    while q <= n:
        powers.append(q)
        q *= 3
    sums = {0}
    for q in powers:
        sums |= {s + q for s in sums}
    return n in sums


def v_pow3(tests):
    for t in tests:
        assert 1 <= t["args"][0] <= 10000000


CHECKS["powers-of-three-sum"] = (b_pow3, lambda r: [r.randint(1, 300)], "exact")
VALIDATE["powers-of-three-sum"] = v_pow3


p = add(
    id="perfect-numbers-up-to", title="Perfect Numbers Up To N", diff="Easy", topic="Math & Bit Manipulation",
    fn="perfectNumbersUpTo", params=[("n", "int")], ret="int[]", cmp="exact",
    desc="<p>A positive integer is <em>perfect</em> when it equals the sum of its proper divisors, meaning the divisors smaller than the number itself. For example, 6 = 1 + 2 + 3 and 28 = 1 + 2 + 4 + 7 + 14.</p><p>Return all perfect numbers from 1 to <code>n</code> in increasing order. Return an empty list when there are none.</p><pre>n = 30  &rarr;  [6, 28]\nn = 5   &rarr;  []</pre>",
    constraints=["1 &le; n &le; 50,000"],
    hints=["Checking each number by trying every smaller divisor takes O(n<sup>2</sup>) in total. Can you collect the divisors faster?",
           "If d divides x, then x / d also divides x. Scanning divisors only up to the square root finds all of them.",
           "Or run a sieve: for every d, add d to each of its multiples. Afterwards each entry holds the sum of its proper divisors."],
    editorial=["Use a sieve of proper-divisor sums. For each d from 1 to n / 2, add d to every multiple of d that is at least 2d. Each number m then collects exactly its proper divisors, and m is perfect when the collected sum equals m.",
               "The sieve takes O(n log n) time, because the number of multiples of d up to n is about n / d. The total is a harmonic sum. Only the array of n + 1 sums is stored, so the space is O(n)."],
    time="O(n log n)", space="O(n)",
    solution='''def perfectNumbersUpTo(n):
    s = [0] * (n + 1)
    for d in range(1, n // 2 + 1):
        for m in range(2 * d, n + 1, d):
            s[m] += d
    return [x for x in range(2, n + 1) if s[x] == x]
''',
    tests=[[1], [5], [6], [7], [28], [29], [496], [500], [8127], [8128], [30], [50000], [49999], [12345]],
)


def b_perfect(n):
    out = []
    for x in range(2, n + 1):
        if sum(i for i in range(1, x) if x % i == 0) == x:
            out.append(x)
    return out


def v_perfect(tests):
    for t in tests:
        assert 1 <= t["args"][0] <= 50000


CHECKS["perfect-numbers-up-to"] = (b_perfect, lambda r: [r.randint(1, 200)], "exact")
VALIDATE["perfect-numbers-up-to"] = v_perfect


p = add(
    id="armstrong-numbers-in-range", title="Armstrong Numbers in a Range", diff="Easy", topic="Math & Bit Manipulation",
    fn="armstrongInRange", params=[("low", "int"), ("high", "int")], ret="int[]", cmp="exact",
    desc="<p>A number with <code>d</code> decimal digits is an <em>Armstrong number</em> (also called a narcissistic number) when the sum of its digits, each raised to the power <code>d</code>, equals the number itself. For example, 153 has 3 digits and 1<sup>3</sup> + 5<sup>3</sup> + 3<sup>3</sup> = 153.</p><p>Return all Armstrong numbers from <code>low</code> to <code>high</code> inclusive, in increasing order.</p><pre>low = 100, high = 400  &rarr;  [153, 370, 371]\nlow = 1,   high = 9    &rarr;  [1, 2, 3, 4, 5, 6, 7, 8, 9]</pre>",
    constraints=["1 &le; low &le; high &le; 50,000"],
    hints=["Every number in this range has at most five digits, so testing each one is fast enough. How do you get the digits of a number, and how many are there?",
           "Turn the number into a string, or repeatedly take <code>% 10</code> and <code>// 10</code>. The exponent is the digit count.",
           "Compare the power sum with the original number and keep the matches in the order you find them."],
    editorial=["Test each number in the range directly. For a number with d digits, add up each digit raised to the power d, and keep the number if that sum equals the number. Single-digit numbers always pass, because a digit to the power 1 is itself.",
               "The work is O(range * d) for a range of numbers with d digits each, and the output list is short because Armstrong numbers are rare. Only the output is stored beyond the loop variables."],
    time="O(R * d)", space="O(output)",
    solution='''def armstrongInRange(low, high):
    out = []
    for x in range(low, high + 1):
        digits = str(x)
        d = len(digits)
        if sum(int(c) ** d for c in digits) == x:
            out.append(x)
    return out
''',
    tests=[[1, 9], [100, 400], [10, 99], [1, 1000], [370, 371], [400, 410], [2, 2], [1000, 9999],
           [9475, 49999], [1, 50000], [9474, 9474], [50000, 50000]],
)


def b_arm(low, high):
    res = []
    for x in range(low, high + 1):
        digs = []
        y = x
        while True:
            digs.append(y % 10)
            y //= 10
            if y == 0:
                break
        d = len(digs)
        if sum(g ** d for g in digs) == x:
            res.append(x)
    return res


def g_arm(r):
    lo = r.randint(1, 1200)
    return [lo, lo + r.randint(0, 800)]


def v_arm(tests):
    for t in tests:
        low, high = t["args"]
        assert 1 <= low <= high <= 50000


CHECKS["armstrong-numbers-in-range"] = (b_arm, g_arm, "exact")
VALIDATE["armstrong-numbers-in-range"] = v_arm


# ---------------------------------------------------------------- MEDIUM

p = add(
    id="josephus-last-survivor", title="Josephus Survivor", diff="Medium", topic="Math & Bit Manipulation",
    fn="josephusSurvivor", params=[("n", "int"), ("k", "int")], ret="int", cmp="exact",
    desc="<p>There are <code>n</code> people numbered 1 to <code>n</code>, standing in a circle in that order. Starting with person 1, they count off around the circle, and every <code>k</code>-th person still in the circle is removed. Counting then continues with the next person who is still there. This repeats until one person is left.</p><p>Return the number of the last survivor.</p><pre>n = 5, k = 2  &rarr;  3\n(removal order: 2, 4, 1, 5)</pre>",
    constraints=["1 &le; n &le; 200,000", "1 &le; k &le; 10<sup>9</sup>"],
    hints=["Simulating with a list and deleting the k-th person each time is correct. How much work is that when n = 200,000?",
           "After the first removal, the remaining people form a circle of n - 1 people, but counting restarts just after the person who was removed.",
           "Let f(m) be the 0-indexed survivor when m people remain. Then f(1) = 0 and f(m) = (f(m - 1) + k) mod m. Add 1 to the result at the end."],
    editorial=["After the first removal, person k is gone and counting restarts at person k + 1. Relabel the circle so that person k + 1 becomes the new person 1. That is exactly the same problem with one person fewer. If the 0-indexed survivor of the smaller circle is f(m - 1), then in the original numbering it sits k positions further along, which gives f(m) = (f(m - 1) + k) mod m.",
               "Start with f(1) = 0 and apply the step for m = 2 up to n. This takes O(n) time and O(1) space, far better than simulating with deletions, which costs O(n^2) with a plain list."],
    time="O(n)", space="O(1)",
    solution='''def josephusSurvivor(n, k):
    pos = 0
    for m in range(2, n + 1):
        pos = (pos + k) % m
    return pos + 1
''',
    tests=[[1, 1], [2, 1], [5, 2], [7, 3], [10, 1], [10, 2], [41, 3], [6, 1000000000], [100, 7], [123456, 17],
           [200000, 2], [200000, 1000000000]],
)


def b_jos(n, k):
    people = list(range(1, n + 1))
    i = 0
    while len(people) > 1:
        i = (i + k - 1) % len(people)
        people.pop(i)
    return people[0]


def g_jos(r):
    return [r.randint(1, 40), r.randint(1, 12)]


def v_jos(tests):
    for t in tests:
        n, k = t["args"]
        assert 1 <= n <= 200000 and 1 <= k <= 10 ** 9


CHECKS["josephus-last-survivor"] = (b_jos, g_jos, "exact")
VALIDATE["josephus-last-survivor"] = v_jos


p = add(
    id="water-jugs-measure-exact", title="Measure Water With Two Jugs", diff="Medium", topic="Math & Bit Manipulation",
    fn="canMeasureWater", params=[("x", "int"), ("y", "int"), ("z", "int")], ret="bool", cmp="exact",
    desc="<p>You have two empty jugs with capacities <code>x</code> and <code>y</code> liters, and an unlimited supply of water. In one move you can fill a jug to the top, empty a jug completely, or pour water from one jug into the other until the receiving jug is full or the pouring jug is empty.</p><p>Return <code>true</code> if you can reach a state where the two jugs together hold exactly <code>z</code> liters, and <code>false</code> otherwise.</p><pre>x = 3, y = 5, z = 4  &rarr;  true\nx = 2, y = 6, z = 5  &rarr;  false</pre>",
    constraints=["1 &le; x, y &le; 10<sup>9</sup>", "0 &le; z &le; 2 * 10<sup>9</sup>"],
    hints=["Work through x = 3, y = 5 by hand. Which totals can you reach, and which move creates each one?",
           "Every fill adds x or y to the total, every empty removes a full jug, and a pour leaves the total unchanged. So every total is a combination of x and y.",
           "The reachable totals are exactly the multiples of gcd(x, y) from 0 up to x + y. Check both conditions for z."],
    editorial=["Each move changes the total water by exactly one jug capacity (a fill adds a whole jug, an empty removes one) or leaves it unchanged (a pour). Therefore every total is a whole-number combination of x and y, so it is a multiple of gcd(x, y). The total can never exceed x + y, since the jugs hold nothing more.",
               "The converse also holds: by repeatedly filling one jug and pouring it into the other, you can reach every multiple of gcd(x, y) up to x + y. So z is reachable exactly when z <= x + y and z is a multiple of gcd(x, y). The check runs in O(log(min(x, y))) time for the gcd."],
    time="O(log min(x, y))", space="O(1)",
    solution='''from math import gcd


def canMeasureWater(x, y, z):
    if z > x + y:
        return False
    return z % gcd(x, y) == 0
''',
    tests=[[3, 5, 4], [2, 6, 5], [1, 1, 0], [1, 2, 3], [1, 2, 4], [3, 5, 0], [5, 3, 9], [4, 6, 5], [6, 9, 15],
           [6, 9, 7], [1000000000, 1000000000, 1000000000], [999999937, 1000000000, 1999999937],
           [999999937, 1000000000, 2000000000], [1000000000, 999999999, 1]],
)


def b_water(x, y, z):
    start = (0, 0)
    seen = {start}
    stack = [start]
    while stack:
        a, b = stack.pop()
        if a + b == z:
            return True
        t1 = min(a, y - b)
        t2 = min(b, x - a)
        for s in [(x, b), (a, y), (0, b), (a, 0), (a - t1, b + t1), (a + t2, b - t2)]:
            if s not in seen:
                seen.add(s)
                stack.append(s)
    return False


def v_water(tests):
    for t in tests:
        x, y, z = t["args"]
        assert 1 <= x <= 10 ** 9 and 1 <= y <= 10 ** 9 and 0 <= z <= 2 * 10 ** 9


CHECKS["water-jugs-measure-exact"] = (b_water, lambda r: [r.randint(1, 6), r.randint(1, 6), r.randint(0, 14)], "exact")
VALIDATE["water-jugs-measure-exact"] = v_water


p = add(
    id="spiral-coordinate-value", title="Number at a Spiral Coordinate", diff="Medium", topic="Math & Bit Manipulation",
    fn="spiralValueAt", params=[("x", "int"), ("y", "int")], ret="int", cmp="exact",
    desc="<p>Imagine an infinite square spiral written on a grid. The number 1 sits at the origin <code>(0, 0)</code>. From there the spiral walks 1 step right, 1 step up, 2 steps left, 2 steps down, 3 steps right, 3 steps up, 4 steps left, 4 steps down, and so on, writing the next integer on each cell it enters. Coordinates are <code>(x, y)</code>, with <code>x</code> growing to the right and <code>y</code> growing upwards.</p><p>Return the integer written at cell <code>(x, y)</code>.</p><pre>(0, 0)   &rarr;  1\n(1, 0)   &rarr;  2\n(1, 1)   &rarr;  3\n(-1, 0)  &rarr;  6\n(0, -1)  &rarr;  8</pre>",
    constraints=["-300 &le; x, y &le; 300"],
    hints=["Simulate the walk: the legs have lengths 1, 1, 2, 2, 3, 3, and so on. You can count steps until you reach the cell, but there may be a faster way.",
           "Walk ring by ring. The ring at distance m = max(|x|, |y|) holds the numbers from (2m - 1)<sup>2</sup> + 1 to (2m + 1)<sup>2</sup>, so the square of the odd number before it marks where the ring starts.",
           "Find which side of the ring the cell lies on. Each side is a straight line of cells, so the offset from the start of the ring is one linear expression per side."],
    editorial=["Every cell at distance m from the origin, where m = max(|x|, |y|), belongs to ring m. Ring m contains the numbers (2m - 1)<sup>2</sup> + 1 through (2m + 1)<sup>2</sup>, and it begins at cell (m, -(m - 1)). Going around it, the ring has four straight sides: up the right edge, left along the top, down the left edge, and right along the bottom, which ends at (m, -m).",
               "For a cell on each side, compute its offset from the ring's starting value: on the right edge the offset is y + m, on the top it is 2m + (m - x), on the left it is 4m + (m - y), and on the bottom it is 6m + (x + m). The answer is (2m - 1)<sup>2</sup> plus the offset. Each query is O(1)."],
    time="O(1)", space="O(1)",
    solution='''def spiralValueAt(x, y):
    m = max(abs(x), abs(y))
    if m == 0:
        return 1
    base = (2 * m - 1) ** 2
    if x == m and y >= -(m - 1):
        off = y + m
    elif y == m and x <= m - 1:
        off = 2 * m + (m - x)
    elif x == -m and y <= m - 1:
        off = 4 * m + (m - y)
    else:
        off = 6 * m + (x + m)
    return base + off
''',
    tests=[[0, 0], [1, 0], [1, 1], [-1, 0], [0, -1], [2, 2], [-2, -2], [2, -2], [1, -1], [-3, 4], [10, -7],
           [-100, 57], [250, -250], [-300, 300], [300, 300]],
)


def b_spiral(x, y):
    px, py = 0, 0
    val = 1
    if (px, py) == (x, y):
        return val
    dirs = [(1, 0), (0, 1), (-1, 0), (0, -1)]
    i = 0
    while True:
        dx, dy = dirs[i % 4]
        for _ in range(i // 2 + 1):
            px += dx
            py += dy
            val += 1
            if (px, py) == (x, y):
                return val
        i += 1


def v_spiral(tests):
    for t in tests:
        x, y = t["args"]
        assert -300 <= x <= 300 and -300 <= y <= 300


CHECKS["spiral-coordinate-value"] = (b_spiral, lambda r: [r.randint(-7, 7), r.randint(-7, 7)], "exact")
VALIDATE["spiral-coordinate-value"] = v_spiral


p = add(
    id="frobenius-largest-unpayable", title="Largest Amount You Cannot Pay", diff="Medium", topic="Math & Bit Manipulation",
    fn="largestUnpayable", params=[("a", "int"), ("b", "int")], ret="int", cmp="exact",
    desc="<p>You have an unlimited supply of two coin denominations, <code>a</code> and <code>b</code>, which are coprime (their greatest common divisor is 1). An amount <code>t</code> is payable when there are non-negative counts <code>x</code> and <code>y</code> with <code>t = a * x + b * y</code>.</p><p>Return the largest non-negative amount that cannot be paid exactly. If every amount can be paid, return -1.</p><pre>a = 3, b = 5  &rarr;  7    (1, 2, 4 and 7 cannot be paid; 8 = 3 + 5 can)\na = 1, b = 9  &rarr;  -1</pre>",
    constraints=["1 &le; a, b &le; 40,000", "gcd(a, b) = 1"],
    hints=["List the amounts that cannot be paid for a small pair such as 3 and 5. Where does the list stop?",
           "Group the amounts by their remainder modulo a. Within each group, the payable amounts start at one smallest value and continue upward in steps of a.",
           "The answer has a closed form in a and b. Check any candidate formula against the small pairs you listed."],
    editorial=["Consider the remainders modulo a. The payable amounts with a given remainder are b * y, b * y + a, and so on, where y is chosen so that b * y has that remainder. Since b is coprime to a, the values b * 0, b * 1, ..., b * (a - 1) cover every remainder exactly once, so each remainder class has one smallest payable amount, b * y for some y in 0..a-1.",
               "The largest unpayable amount is the largest of these smallest values minus a. The largest smallest value is b * (a - 1), so the answer is b * (a - 1) - a = a * b - a - b. This is Sylvester's formula. It gives -1 when a = 1, since then every amount is payable. The formula runs in O(1) time."],
    time="O(1)", space="O(1)",
    solution='''def largestUnpayable(a, b):
    return a * b - a - b
''',
    tests=[[3, 5], [1, 9], [2, 3], [1, 1], [5, 7], [7, 11], [2, 1001], [39999, 40000], [40000, 39999], [1000, 999],
           [9973, 39989], [37, 40000]],
)


def b_frob(a, b):
    limit = a * b + 5
    payable = [False] * (limit + 1)
    for t in range(limit + 1):
        payable[t] = any((t - a * x) >= 0 and (t - a * x) % b == 0 for x in range(t // a + 1))
    best = -1
    for t in range(limit + 1):
        if not payable[t]:
            best = t
    return best


def g_frob(r):
    while True:
        a, b = r.randint(1, 15), r.randint(1, 15)
        if gcd(a, b) == 1:
            return [a, b]


def v_frob(tests):
    for t in tests:
        a, b = t["args"]
        assert 1 <= a <= 40000 and 1 <= b <= 40000 and gcd(a, b) == 1


CHECKS["frobenius-largest-unpayable"] = (b_frob, g_frob, "exact")
VALIDATE["frobenius-largest-unpayable"] = v_frob


p = add(
    id="stairs-exact-double-steps-ways", title="Stairs With Exactly K Double Steps", diff="Medium", topic="Math & Bit Manipulation",
    fn="stairsWithDoubles", params=[("n", "int"), ("k", "int")], ret="int", cmp="exact",
    desc="<p>A staircase has <code>n</code> steps. Each move climbs either one step or two steps. Count the ways to reach the top that use exactly <code>k</code> two-step moves, with every other move being a one-step move. Two ways are different when their sequences of moves differ.</p><p>Return the count modulo 1,000,000,007, or 0 when no such way exists.</p><pre>n = 4, k = 1  &rarr;  3   (2+1+1, 1+2+1, 1+1+2)\nn = 4, k = 0  &rarr;  1   (1+1+1+1)\nn = 3, k = 2  &rarr;  0</pre>",
    constraints=["0 &le; n &le; 10<sup>9</sup>", "0 &le; k &le; 200,000"],
    hints=["Build a small table for a few values of n and k. How does a sequence of moves end?",
           "Count the moves. There are k two-step moves and n - 2k one-step moves, so n - k moves in total. The question is which k of those moves are the two-step ones.",
           "The answer is the binomial coefficient C(n - k, k), which is 0 when k > n - k. Evaluate it modulo a prime with a product and one modular inverse."],
    editorial=["Fix k. Using exactly k two-step moves and the rest one-step moves, the total is n - 2k single steps plus k doubles, so there are n - k moves in all. Any ordering of these moves is a valid sequence, and the sequence is determined by which k of the n - k positions hold the two-step moves. That gives C(n - k, k) ways.",
               "The binomial is zero when n - k is less than k, that is, when 2k is greater than n. Otherwise compute the product of (n - k) down to (n - 2k + 1) divided by k!, using a modular inverse of k! since the modulus is prime. The loop takes O(k) time, which is why k is capped in the constraints."],
    time="O(k log MOD)", space="O(1)",
    solution='''def stairsWithDoubles(n, k):
    MOD = 1000000007
    m = n - k
    if k < 0 or k > m:
        return 0
    num = 1
    den = 1
    for i in range(k):
        num = num * (m - i) % MOD
        den = den * (i + 1) % MOD
    return num * pow(den, MOD - 2, MOD) % MOD
''',
    tests=[[0, 0], [1, 0], [2, 1], [4, 1], [5, 2], [10, 0], [10, 3], [30, 10], [3, 2], [16, 5],
           [1000000000, 0], [1000000000, 1], [1000000000, 200000], [999999999, 1000]],
)


def b_stairs(n, k):
    MOD = 1000000007
    dp = [[0] * (k + 1) for _ in range(n + 1)]
    dp[0][0] = 1
    for i in range(1, n + 1):
        for j in range(k + 1):
            v = dp[i - 1][j]
            if j >= 1 and i >= 2:
                v += dp[i - 2][j - 1]
            dp[i][j] = v
    return dp[n][k] % MOD


def g_stairs(r):
    return [r.randint(0, 30), r.randint(0, 16)]


def v_stairs(tests):
    for t in tests:
        n, k = t["args"]
        assert 0 <= n <= 10 ** 9 and 0 <= k <= 200000
        assert 0 <= t["expected"] < MOD


CHECKS["stairs-exact-double-steps-ways"] = (b_stairs, g_stairs, "exact")
VALIDATE["stairs-exact-double-steps-ways"] = v_stairs


# ---------------------------------------------------------------- HARD

p = add(
    id="pascal-odd-entries-count", title="Odd Entries in Pascal's Triangle", diff="Hard", topic="Math & Bit Manipulation",
    fn="countOddPascalEntries", params=[("n", "int")], ret="int", cmp="exact",
    desc="<p>Pascal's triangle is numbered from row 0, which holds the single entry 1. Entry <code>C(r, c)</code> is the entry at position <code>c</code> of row <code>r</code>, for <code>0 &le; c &le; r</code>.</p><p>Given <code>n</code>, count the entries that are odd among the first <code>n</code> rows, that is rows 0 through <code>n - 1</code>. Return the count modulo 1,000,000,007.</p><pre>n = 1  &rarr;  1   (row 0: 1)\nn = 3  &rarr;  5   (row 0 has 1 odd entry, row 1 has 2, row 2 has 2)</pre>",
    constraints=["0 &le; n &le; 10<sup>9</sup>"],
    hints=["Count the odd entries row by row for small n and look for a pattern in the count of each row.",
           "Entry C(r, c) is odd exactly when every 1 bit of c is also a 1 bit of r (Lucas's theorem). How many entries of row r are odd, if you think in binary?",
           "Sum 2 raised to the number of 1 bits of r over all r below n. Group the r values by the highest bit where they differ from n. The free lower bits contribute a factor of 3 for each bit."],
    editorial=["By Lucas's theorem, C(r, c) is odd exactly when the binary digits of c are a subset of those of r. If r has t one-bits, the number of such c is 2<sup>t</sup>, so row r has 2<sup>popcount(r)</sup> odd entries. The task is to sum this over r = 0 to n - 1, which is far too many rows to visit when n is 10<sup>9</sup>.",
               "Walk through the set bits of n from the top. A bit i that is set in n lets through every r that matches n above bit i, has a 0 at bit i, and has arbitrary bits below it. Such r have some number of ones above bit i, which is the count of set bits of n seen so far, plus whatever the i free lower bits contribute. Summing 2 raised to the popcount over all i-bit suffixes gives (1 + 2)<sup>i</sup> = 3<sup>i</sup>. So each set bit i contributes 2<sup>ones above</sup> * 3<sup>i</sup>, and the whole computation takes O(log n) time."],
    time="O(log n)", space="O(1)",
    solution='''def countOddPascalEntries(n):
    MOD = 1000000007
    total = 0
    ones = 0
    for i in range(n.bit_length() - 1, -1, -1):
        if (n >> i) & 1:
            total += pow(2, ones, MOD) * pow(3, i, MOD)
            ones += 1
    return total % MOD
''',
    tests=[[0], [1], [2], [3], [4], [5], [8], [16], [17], [100], [1023], [1025], [65536], [123456789],
           [999999999], [1000000000], [987654321]],
)


def b_pascal(n):
    total = 0
    row = [1]
    for _ in range(n):
        total += sum(1 for v in row if v % 2 == 1)
        row = [1] + [row[i] + row[i + 1] for i in range(len(row) - 1)] + [1]
    return total % 1000000007


def g_pascal(r):
    return [r.randint(0, 70)]


def v_pascal(tests):
    for t in tests:
        assert 0 <= t["args"][0] <= 10 ** 9
        assert 0 <= t["expected"] < MOD


CHECKS["pascal-odd-entries-count"] = (b_pascal, g_pascal, "exact")
VALIDATE["pascal-odd-entries-count"] = v_pascal


p = add(
    id="amicable-numbers-sum", title="Sum of Amicable Numbers", diff="Hard", topic="Math & Bit Manipulation",
    fn="sumAmicableUpTo", params=[("n", "int")], ret="int", cmp="exact",
    desc="<p>For a positive integer <code>a</code>, let <code>d(a)</code> be the sum of its proper divisors, meaning the divisors smaller than <code>a</code>. Two different numbers <code>a</code> and <code>b</code> form an amicable pair when <code>d(a) = b</code> and <code>d(b) = a</code>. Each number in such a pair is an amicable number.</p><p>Given <code>n</code>, return the sum of all amicable numbers <code>a</code> with <code>1 &le; a &le; n</code>. The partner <code>b</code> may be larger than <code>n</code>.</p><pre>n = 300  &rarr;  504   (220 + 284)</pre>",
    constraints=["1 &le; n &le; 5,000"],
    hints=["Computing proper divisor sums one number at a time by trial division works for small n. Which numbers do you really need?",
           "A sieve fills the divisor sums of every number up to a limit: for each d, add d to all of its multiples that are at least 2d.",
           "The partner d(a) can be larger than n. Make the sieve cover a few times n so that every partner has a known sum, then test d(d(a)) = a."],
    editorial=["Build the array of proper divisor sums with a sieve up to a limit. The divisor sum of any number up to 5,000 is less than three times the number, so a limit of 4n + 10 covers every partner that the check needs. The sieve adds each d to the multiples of d from 2d onwards, which gives every number exactly its proper divisors.",
               "For each a from 1 to n, let b = d(a). The pair is amicable when b is a different positive number and d(b) = a. Perfect numbers have b = a and are rejected, and 1 is rejected because d(1) = 0. The sieve costs O(L log L) for limit L, so the whole solution runs in O(n log n) time."],
    time="O(n log n)", space="O(n)",
    solution='''def sumAmicableUpTo(n):
    limit = 4 * n + 10
    s = [0] * (limit + 1)
    for d in range(1, limit // 2 + 1):
        for m in range(2 * d, limit + 1, d):
            s[m] += d
    total = 0
    for a in range(1, n + 1):
        b = s[a]
        if b != a and 1 <= b <= limit and s[b] == a:
            total += a
    return total
''',
    tests=[[1], [2], [220], [284], [300], [777], [1023], [2000], [3000], [4096], [4999], [5000]],
)


def b_amicable(n):
    def d(x):
        return sum(i for i in range(1, x) if x % i == 0)

    total = 0
    for a in range(1, n + 1):
        b = d(a)
        if b != a and b >= 1 and d(b) == a:
            total += a
    return total


def v_amicable(tests):
    for t in tests:
        assert 1 <= t["args"][0] <= 5000


CHECKS["amicable-numbers-sum"] = (b_amicable, lambda r: [r.randint(1, 400)], "exact")
VALIDATE["amicable-numbers-sum"] = v_amicable
