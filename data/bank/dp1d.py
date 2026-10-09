"""Problems: one-dimensional dynamic programming. See data/lib.py for the registry."""
from collections import deque
from itertools import combinations

from lib import add, rnd, CHECKS, VALIDATE, gen_arr  # noqa: F401

MOD = 10 ** 9 + 7
TOPIC = "Dynamic Programming"


# ---------------------------------------------------------------- EASY

add(
    id="tribonacci-modulo-dp", title="Tribonacci Modulo", diff="Easy", topic=TOPIC,
    fn="tribonacciMod", params=[("n", "int")], ret="int", cmp="exact",
    desc="<p>The tribonacci sequence starts with <code>T(0) = 0</code>, <code>T(1) = 1</code>, <code>T(2) = 1</code>, and every later term is the sum of the three terms before it: <code>T(k) = T(k-1) + T(k-2) + T(k-3)</code>.</p><p>Given <code>n</code>, return <code>T(n)</code> modulo <code>1,000,000,007</code>. The terms grow exponentially, so the exact value quickly stops fitting in 32 bits.</p>",
    constraints=["0 &le; n &le; 100,000"],
    hints=["Write out the first ten terms by hand. Each one needs only the three terms right before it.",
           "A plain recursion recomputes the same terms again and again. Compute the terms in increasing order instead, so each is calculated once.",
           "Keep just three variables for the last three terms, and reduce modulo 1,000,000,007 after every addition so the numbers stay small."],
    editorial=["The recurrence only looks back three positions, so a bottom-up loop with three rolling variables is enough. Start with <code>(a, b, c) = (T(0), T(1), T(2))</code> and repeat <code>(a, b, c) = (b, c, (a + b + c) mod M)</code> until the window has moved n steps; then <code>a</code> holds <code>T(n)</code>.",
               "Taking the remainder at every step is valid because addition respects modular arithmetic. Each sum of three reduced terms stays below 3 &times; 10<sup>9</sup>, which overflows a signed 32-bit integer, so in such languages use a 64-bit type or reduce after each pairwise addition. The loop is O(n) time and O(1) space; matrix exponentiation would give O(log n) but is unnecessary here."],
    time="O(n)", space="O(1)",
    solution='''def tribonacciMod(n):
    M = 1000000007
    a, b, c = 0, 1, 1
    for _ in range(n):
        a, b, c = b, c, (a + b + c) % M
    return a
''',
    tests=[[0], [1], [2], [3], [4], [10], [25], [37], [38], [100], [1000], [12345], [99999], [100000]],
)


def _mat_mul(A, B):
    return [[sum(A[i][k] * B[k][j] for k in range(3)) % MOD for j in range(3)] for i in range(3)]


def _brute_trib(n):
    # matrix exponentiation: [T(k+2), T(k+1), T(k)] = M^k [T(2), T(1), T(0)]
    base = [[1, 1, 1], [1, 0, 0], [0, 1, 0]]
    res = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
    e = n
    while e:
        if e & 1:
            res = _mat_mul(res, base)
        base = _mat_mul(base, base)
        e >>= 1
    # vector (T2, T1, T0) = (1, 1, 0); T(n) is the third component of M^n v
    return (res[2][0] * 1 + res[2][1] * 1 + res[2][2] * 0) % MOD


def _v_trib(tests):
    for t in tests:
        assert 0 <= t["args"][0] <= 100000


CHECKS["tribonacci-modulo-dp"] = (_brute_trib, lambda r: [r.randint(0, 80)], "exact")
VALIDATE["tribonacci-modulo-dp"] = _v_trib

# ------------------------------------------------------------------

_r = rnd(7102)
_bs1 = _r.sample(range(1, 50001), 10000)
_bs2 = list(range(2, 20001, 2))
_bs3 = _r.sample(range(1, 40000), 500)
_bs4 = [k for k in range(3, 30001, 3)]

add(
    id="broken-steps-staircase-ways", title="Staircase With Broken Steps", diff="Easy", topic=TOPIC,
    fn="countStaircaseWays", params=[("n", "int"), ("broken", "int[]")], ret="int", cmp="exact",
    desc="<p>You stand on the ground (step <code>0</code>) of a staircase whose top is step <code>n</code>. Each move climbs either 1 or 2 steps. Some steps listed in <code>broken</code> have collapsed, and you may never land on them (you can, however, jump over a single broken step).</p><p>Return the number of different sequences of moves that take you exactly to step <code>n</code>, modulo <code>1,000,000,007</code>. If step <code>n</code> itself is broken the answer is <code>0</code>.</p>",
    constraints=["1 &le; n &le; 50,000", "0 &le; broken.length &le; min(n, 10,000)", "1 &le; broken[i] &le; n and all values are distinct (the array is not necessarily sorted)"],
    hints=["Think about the very last move. From which steps can you arrive at step <code>i</code>?",
           "Let ways(i) be the number of ways to be standing on step i. Then ways(i) = ways(i-1) + ways(i-2), except that ways(i) = 0 when step i is broken.",
           "Mark the broken steps in a boolean array (or a set) and fill ways from 0 up to n, taking the remainder each time. Only the previous two values are needed."],
    editorial=["This is the classic staircase recurrence with one twist. Let <code>ways(0) = 1</code>. For each step <code>i</code> from 1 to n, if step i is broken then <code>ways(i) = 0</code>; otherwise <code>ways(i) = ways(i-1) + ways(i-2)</code> (treat negative indices as 0). Because a broken step has zero ways to be stood on, it contributes nothing to later steps, which exactly models never landing on it.",
               "Reduce modulo 1,000,000,007 on every addition. Put the broken steps into a set (or a boolean array) first so each lookup is O(1). The total work is O(n + b) time with O(b) memory for the set and O(1) for the rolling values."],
    time="O(n + b)", space="O(b)",
    solution='''def countStaircaseWays(n, broken):
    M = 1000000007
    bad = set(broken)
    prev2, prev1 = 0, 1          # ways(-1), ways(0)
    for i in range(1, n + 1):
        cur = 0 if i in bad else (prev1 + prev2) % M
        prev2, prev1 = prev1, cur
    return prev1
''',
    tests=[[1, []], [1, [1]], [2, []], [2, [1]], [3, [2]], [4, [4]], [5, []], [5, [1, 2]], [6, [3]], [7, [6, 2, 4]],
           [10, [5]], [8, [8, 3]], [50000, []], [50000, _bs1], [20001, _bs2], [40000, _bs3], [30000, _bs4]],
)


def _brute_broken(n, broken):
    bad = set(broken)

    def go(pos):
        if pos in bad or pos > n:
            return 0
        if pos == n:
            return 1
        return go(pos + 1) + go(pos + 2)

    return go(0) % MOD


def _gen_broken(r):
    n = r.randint(1, 14)
    b = r.sample(range(1, n + 1), r.randint(0, min(n, 5)))
    return [n, b]


def _v_broken(tests):
    for t in tests:
        n, b = t["args"]
        assert 1 <= n <= 50000 and len(b) <= min(n, 10000)
        assert len(set(b)) == len(b) and all(1 <= x <= n for x in b)


CHECKS["broken-steps-staircase-ways"] = (_brute_broken, _gen_broken, "exact")
VALIDATE["broken-steps-staircase-ways"] = _v_broken


# ---------------------------------------------------------------- MEDIUM

_r = rnd(7103)
_hr1 = [_r.randint(0, 1000) for _ in range(5000)]
_hr2 = [1000] * 5000
_hr3 = [1000 if i % 2 == 0 else 1 for i in range(4999)]
_hr4 = [_r.randint(0, 50) for _ in range(3001)]

add(
    id="house-robber-ii", title="House Robber II", diff="Medium", topic=TOPIC,
    fn="robCircle", params=[("nums", "int[]")], ret="int", cmp="exact",
    desc="<p>The houses on a street are arranged in a <strong>circle</strong>: house <code>i</code> holds <code>nums[i]</code> coins, and the last house is a neighbour of the first. Breaking into two neighbouring houses sets off the alarm, so you may not rob two houses that are next to each other.</p><p>Return the largest number of coins you can collect without triggering the alarm. With a single house, you may simply rob it.</p>",
    constraints=["1 &le; nums.length &le; 5,000", "0 &le; nums[i] &le; 1,000"],
    hints=["Solve the straight-street version first: best(i) = max(best(i-1), best(i-2) + nums[i]).",
           "In the circle, the first and last houses are neighbours, so you can never rob both.",
           "Run the straight-street DP twice: once on houses 0..n-2 and once on houses 1..n-1. Take the larger result (handle n = 1 separately)."],
    editorial=["On a straight street the answer is a simple rolling DP: <code>best(i) = max(best(i-1), best(i-2) + nums[i])</code>. The circle adds exactly one extra restriction: houses 0 and n-1 cannot both be robbed.",
               "So every valid plan avoids house 0 or avoids house n-1 (or both). The best plan that avoids the last house is the straight-street answer for <code>nums[0..n-2]</code>, and the best plan that avoids the first is the straight-street answer for <code>nums[1..n-1]</code>. The overall answer is the larger of those two. A single house has no neighbour, so it is a special case that returns <code>nums[0]</code>. Time O(n), space O(1)."],
    time="O(n)", space="O(1)",
    solution='''def robCircle(nums):
    def line(a):
        take, skip = 0, 0
        for x in a:
            take, skip = skip + x, max(take, skip)
        return max(take, skip)

    if len(nums) == 1:
        return nums[0]
    return max(line(nums[:-1]), line(nums[1:]))
''',
    tests=[[[2, 3, 2]], [[1, 2, 3, 1]], [[1]], [[0]], [[3, 7]], [[1, 2, 3]], [[0, 0, 0, 0]], [[200, 3, 140, 20, 10]],
           [[5, 1, 1, 5]], [[10, 1, 1, 10, 1, 1, 10]], [[_hr1[0]] + [0] * 3], [_hr1], [_hr2], [_hr3], [_hr4]],
)


def _brute_rob2(nums):
    n = len(nums)
    if n == 1:
        return nums[0]
    best = 0
    for mask in range(1 << n):
        ok = True
        for i in range(n):
            if mask >> i & 1 and mask >> ((i + 1) % n) & 1:
                ok = False
                break
        if ok:
            best = max(best, sum(nums[i] for i in range(n) if mask >> i & 1))
    return best


def _v_rob2(tests):
    for t in tests:
        a = t["args"][0]
        assert 1 <= len(a) <= 5000 and all(0 <= x <= 1000 for x in a)


CHECKS["house-robber-ii"] = (_brute_rob2, lambda r: [gen_arr(r, 0, 9, 1, 12)], "exact")
VALIDATE["house-robber-ii"] = _v_rob2

# ------------------------------------------------------------------

_r = rnd(7104)
_de1 = [_r.randint(1, 10000) for _ in range(10000)]
_de2 = [10000] * 10000
_de3 = [_r.randint(1, 5) for _ in range(10000)]
_de4 = list(range(1, 10001))
_de5 = [_r.choice([1, 3, 5, 7, 9]) for _ in range(5000)] + [_r.choice([2, 4, 6, 8]) for _ in range(300)]

add(
    id="delete-and-earn", title="Delete and Earn", diff="Medium", topic=TOPIC,
    fn="deleteAndEarn", params=[("nums", "int[]")], ret="int", cmp="exact",
    desc="<p>You play a game on the integer array <code>nums</code>. In one move you choose any element with value <code>x</code> and remove it, earning <code>x</code> points. Right after that move, <strong>every</strong> element equal to <code>x - 1</code> and <strong>every</strong> element equal to <code>x + 1</code> is also removed from the array (you earn nothing for those).</p><p>You may make as many moves as you like, in any order, until you stop or the array is empty. Return the maximum total number of points you can earn.</p>",
    constraints=["1 &le; nums.length &le; 10,000", "1 &le; nums[i] &le; 10,000"],
    hints=["If you take one copy of x, you may as well take every copy of x: the extra copies are never in conflict with anything new.",
           "Group the elements by value. Taking value v is worth v &times; count(v) and forbids taking v-1 and v+1.",
           "That is House Robber over the values 1..10,000: best(v) = max(best(v-1), best(v-2) + v &times; count(v))."],
    editorial=["Once you take a value x, the neighbours x-1 and x+1 vanish but other copies of x do not, so taking all copies of x is always at least as good. Therefore the game is really a choice of <em>values</em>: the set of values you pick must not contain two consecutive integers, and picking value v yields <code>v * count(v)</code> points.",
               "Build an array <code>gain[v] = v * count(v)</code> for v up to the maximum value, then run the House Robber recurrence <code>best(v) = max(best(v-1), best(v-2) + gain[v])</code> with two rolling variables. Time O(n + max value), space O(max value)."],
    time="O(n + V)", space="O(V)",
    solution='''def deleteAndEarn(nums):
    top = max(nums)
    gain = [0] * (top + 1)
    for x in nums:
        gain[x] += x
    take, skip = 0, 0
    for v in range(1, top + 1):
        take, skip = skip + gain[v], max(take, skip)
    return max(take, skip)
''',
    tests=[[[3, 4, 2]], [[2, 2, 3, 3, 3, 4]], [[1]], [[1, 1, 1, 1]], [[1, 2, 3, 4, 5]], [[10000]], [[10000, 9999]],
           [[5, 5, 6, 6, 7]], [[1, 3, 5, 7]], [[8, 3, 4, 7, 6, 6, 9, 2, 5, 8, 2, 4, 9, 5, 9, 1, 5, 7, 1, 4]],
           [_de1], [_de2], [_de3], [_de4], [_de5]],
)


def _brute_delete(nums):
    from functools import lru_cache

    @lru_cache(maxsize=None)
    def go(state):
        best = 0
        for i, x in enumerate(state):
            rest = tuple(y for j, y in enumerate(state) if j != i and y != x - 1 and y != x + 1)
            best = max(best, x + go(tuple(sorted(rest))))
        return best

    return go(tuple(sorted(nums)))


def _v_delete(tests):
    for t in tests:
        a = t["args"][0]
        assert 1 <= len(a) <= 10000 and all(1 <= x <= 10000 for x in a)


CHECKS["delete-and-earn"] = (_brute_delete, lambda r: [gen_arr(r, 1, 6, 1, 8)], "exact")
VALIDATE["delete-and-earn"] = _v_delete

# ------------------------------------------------------------------

_r = rnd(7105)
_cc_big = sorted(_r.sample(range(1, 5001), 50))

add(
    id="coin-change-ii-count-ways", title="Coin Change: Count the Ways", diff="Medium", topic=TOPIC,
    fn="countCombinations", params=[("amount", "int"), ("coins", "int[]")], ret="int", cmp="exact",
    desc="<p>You have an unlimited supply of coins of each denomination listed in <code>coins</code>. Count how many different <strong>combinations</strong> of coins add up to exactly <code>amount</code>. Two combinations are the same if they use each denomination the same number of times, regardless of the order the coins are picked (so <code>1 + 2</code> and <code>2 + 1</code> count once).</p><p>Return the count modulo <code>1,000,000,007</code>. Making an amount of <code>0</code> counts as exactly one combination (use no coins).</p>",
    constraints=["0 &le; amount &le; 5,000", "1 &le; coins.length &le; 50", "1 &le; coins[i] &le; 5,000 and all denominations are distinct"],
    hints=["First think how you would count <em>sequences</em> (order matters). Then ask what must change so each combination is counted once.",
           "Process the denominations one at a time. Let ways[a] be the number of combinations of the coins processed so far that sum to a.",
           "For each coin c, loop a from c up to amount and do ways[a] += ways[a - c]. The outer loop over coins is what stops the same combination from being counted in several orders."],
    editorial=["Let <code>ways[a]</code> be the number of combinations summing to a using only the denominations handled so far; initially <code>ways[0] = 1</code> and the rest are 0. Introducing a new coin c: any combination that uses c at least once is a combination for <code>a - c</code> (using the allowed coins, including c) plus one more c, which is exactly <code>ways[a - c]</code> after it has been updated. Iterating a upward therefore adds <code>ways[a] += ways[a - c]</code>.",
               "Putting the coins in the outer loop and the amounts in the inner loop means each coin is considered in one fixed order, so every multiset of coins is built in exactly one way. Swapping the two loops would instead count ordered sequences. Take the remainder after each addition. Time O(amount &times; coins), space O(amount)."],
    time="O(amount * k)", space="O(amount)",
    solution='''def countCombinations(amount, coins):
    M = 1000000007
    ways = [0] * (amount + 1)
    ways[0] = 1
    for c in coins:
        for a in range(c, amount + 1):
            ways[a] = (ways[a] + ways[a - c]) % M
    return ways[amount]
''',
    tests=[[5, [1, 2, 5]], [3, [2]], [10, [10]], [0, [7]], [0, [1, 2]], [1, [2]], [7, [2, 3]], [100, [1, 5, 10, 25, 50]],
           [11, [1, 2, 5]], [4999, [2, 4, 6]], [5000, [1]], [5000, [5000]], [5000, [1, 2, 5, 10, 20, 50, 100, 200]],
           [5000, list(range(1, 51))], [5000, _cc_big], [3000, [7, 13, 29, 101, 503]]],
)


def _brute_coin2(amount, coins):
    def go(i, rem):
        if rem == 0:
            return 1
        if i == len(coins):
            return 0
        total = 0
        k = 0
        while k * coins[i] <= rem:
            total += go(i + 1, rem - k * coins[i])
            k += 1
        return total

    return go(0, amount) % MOD


def _gen_coin2(r):
    coins = r.sample(range(1, 9), r.randint(1, 4))
    r.shuffle(coins)
    return [r.randint(0, 16), coins]


def _v_coin2(tests):
    for t in tests:
        amount, coins = t["args"]
        assert 0 <= amount <= 5000 and 1 <= len(coins) <= 50
        assert len(set(coins)) == len(coins) and all(1 <= c <= 5000 for c in coins)


CHECKS["coin-change-ii-count-ways"] = (_brute_coin2, _gen_coin2, "exact")
VALIDATE["coin-change-ii-count-ways"] = _v_coin2

# ------------------------------------------------------------------

add(
    id="perfect-squares-min-count", title="Fewest Perfect Squares", diff="Medium", topic=TOPIC,
    fn="minSquares", params=[("n", "int")], ret="int", cmp="exact",
    desc="<p>A <em>perfect square</em> is an integer of the form <code>k * k</code> for a positive integer <code>k</code> (1, 4, 9, 16, ...). Given a positive integer <code>n</code>, return the smallest number of perfect squares whose sum is exactly <code>n</code>. A square may be used more than once.</p>",
    constraints=["1 &le; n &le; 10,000"],
    hints=["Try small n by hand: 12 = 4 + 4 + 4 needs three squares, while 13 = 4 + 9 needs two.",
           "Let f(m) be the answer for m. The last square in an optimal decomposition is some k*k &le; m, leaving m - k*k to be built optimally.",
           "f(0) = 0 and f(m) = 1 + min over k with k*k &le; m of f(m - k*k). Fill the table from 1 up to n."],
    editorial=["Define <code>f(m)</code> as the fewest squares summing to m, with <code>f(0) = 0</code>. In an optimal decomposition of m, remove any one square <code>k*k</code>: what is left must itself be an optimal decomposition of <code>m - k*k</code>, otherwise the whole decomposition could be improved. Hence <code>f(m) = 1 + min f(m - k*k)</code> over all k with <code>k*k &le; m</code>.",
               "Filling the table for m = 1..n does about n &times; &radic;n steps, roughly one million for n = 10,000. (Lagrange's four-square theorem says the answer is never more than 4, which allows an O(&radic;n) solution, but the DP is the more general idea and easily fast enough.)"],
    time="O(n sqrt n)", space="O(n)",
    solution='''def minSquares(n):
    f = [0] + [n] * n
    squares = []
    k = 1
    while k * k <= n:
        squares.append(k * k)
        k += 1
    for m in range(1, n + 1):
        best = m
        for s in squares:
            if s > m:
                break
            if f[m - s] + 1 < best:
                best = f[m - s] + 1
        f[m] = best
    return f[n]
''',
    tests=[[1], [2], [3], [4], [7], [12], [13], [25], [43], [48], [63], [100], [4095], [7168], [9999], [10000]],
)


def _brute_squares(n):
    # breadth-first search over remainders: each edge subtracts one perfect square
    seen = {n}
    q = deque([(n, 0)])
    while q:
        m, d = q.popleft()
        if m == 0:
            return d
        k = 1
        while k * k <= m:
            nm = m - k * k
            if nm not in seen:
                seen.add(nm)
                q.append((nm, d + 1))
            k += 1
    return -1


def _v_squares(tests):
    for t in tests:
        assert 1 <= t["args"][0] <= 10000
        assert 1 <= t["expected"] <= 4


CHECKS["perfect-squares-min-count"] = (_brute_squares, lambda r: [r.randint(1, 250)], "exact")
VALIDATE["perfect-squares-min-count"] = _v_squares

# ------------------------------------------------------------------

_r = rnd(7106)
_tk_full = list(range(1, 366))
_tk_rand = sorted(_r.sample(range(1, 366), 150))
_tk_sparse = sorted(_r.sample(range(1, 366), 25))
_tk_dense = sorted(_r.sample(range(1, 366), 300))

add(
    id="minimum-cost-for-tickets", title="Minimum Cost for Travel Passes", diff="Medium", topic=TOPIC,
    fn="minCostTickets", params=[("days", "int[]"), ("costs", "int[]")], ret="int", cmp="exact",
    desc="<p>You plan to travel on certain days of a 365-day year. The array <code>days</code> lists those days in strictly increasing order, each between <code>1</code> and <code>365</code>.</p><p>Passes come in three kinds, with prices given by <code>costs = [c1, c7, c30]</code>: a 1-day pass costs <code>c1</code> and covers one day, a 7-day pass costs <code>c7</code> and covers 7 consecutive days starting on the day you use it, and a 30-day pass costs <code>c30</code> and covers 30 consecutive days. Return the minimum total price needed to cover every travel day. The prices are arbitrary, so a longer pass is not guaranteed to be cheaper per day (or even more expensive in total) than a shorter one.</p>",
    constraints=["1 &le; days.length &le; 365", "1 &le; days[i] &le; 365 and days is strictly increasing", "costs.length == 3", "1 &le; costs[i] &le; 1,000"],
    hints=["Look at the first travel day that is not yet covered. Which pass could you buy for it?",
           "Let f(i) be the cheapest way to cover travel days i, i+1, ... . If you buy a pass of length L on day days[i], it covers every travel day before days[i] + L; jump to the first uncovered one.",
           "Do it bottom-up from the last travel day backwards, or over the calendar days 1..365 with dp[d] = dp[d-1] if d is not a travel day, else the minimum over the three passes of dp[max(0, d - L)] + cost."],
    editorial=["Work over the calendar. Let <code>dp[d]</code> be the cheapest cost to cover all travel days up to and including day d. If d is not a travel day, nothing new has to be covered, so <code>dp[d] = dp[d-1]</code>. If it is, the pass that covers day d ends on d or later; assume the pass you buy for d is the one that ends exactly on d (buying it any later does not help days up to d), so it covers days <code>d-L+1..d</code> and <code>dp[d] = min(dp[max(0, d-1)] + c1, dp[max(0, d-7)] + c7, dp[max(0, d-30)] + c30)</code>.",
               "The answer is <code>dp[last travel day]</code>. This is O(365) time and space, independent of the number of travel days. An equivalent view indexes the DP by travel day and jumps forward with two pointers; both are linear. Note that taking the minimum over all three passes handles odd price lists, e.g. a 30-day pass cheaper than a 7-day pass."],
    time="O(365)", space="O(365)",
    solution='''def minCostTickets(days, costs):
    travel = set(days)
    last = days[-1]
    dp = [0] * (last + 1)
    for d in range(1, last + 1):
        if d not in travel:
            dp[d] = dp[d - 1]
        else:
            dp[d] = min(dp[d - 1] + costs[0],
                        dp[max(0, d - 7)] + costs[1],
                        dp[max(0, d - 30)] + costs[2])
    return dp[last]
''',
    tests=[[[1, 4, 6, 7, 8, 20], [2, 7, 15]], [[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 30, 31], [2, 7, 15]], [[365], [5, 20, 40]],
           [[1], [3, 2, 1]], [[1, 365], [1, 1, 1]], [[1, 8, 15, 22, 29], [10, 5, 3]], [[5, 10, 35], [7, 2, 15]],
           [[1, 2, 3, 4, 5, 6, 7], [2, 7, 15]], [[1, 31, 61], [20, 30, 25]], [[7, 8, 9, 36, 37, 38], [4, 9, 12]],
           [_tk_full, [2, 7, 15]], [_tk_full, [1000, 1000, 1000]], [_tk_rand, [3, 11, 20]], [_tk_sparse, [4, 13, 60]],
           [_tk_dense, [5, 5, 7]]],
)


def _brute_tickets(days, costs):
    lens = (1, 7, 30)

    def go(i):
        if i == len(days):
            return 0
        best = None
        for L, c in zip(lens, costs):
            j = i
            while j < len(days) and days[j] < days[i] + L:
                j += 1
            val = c + go(j)
            if best is None or val < best:
                best = val
        return best

    return go(0)


def _gen_tickets(r):
    top = r.choice([12, 40, 70])
    days = sorted(r.sample(range(1, top + 1), r.randint(1, 8)))
    return [days, [r.randint(1, 12) for _ in range(3)]]


def _v_tickets(tests):
    for t in tests:
        days, costs = t["args"]
        assert 1 <= len(days) <= 365 and all(1 <= d <= 365 for d in days)
        assert all(a < b for a, b in zip(days, days[1:]))
        assert len(costs) == 3 and all(1 <= c <= 1000 for c in costs)


CHECKS["minimum-cost-for-tickets"] = (_brute_tickets, _gen_tickets, "exact")
VALIDATE["minimum-cost-for-tickets"] = _v_tickets

# ------------------------------------------------------------------

_r = rnd(7107)
_nl1 = list(range(1, 1501))
_nl2 = [5] * 1500
_nl3 = [v for k in range(750) for v in (2 * k + 2, 2 * k + 1)]
_nl4 = [_r.randint(-10 ** 6, 10 ** 6) for _ in range(1500)]
_nl5 = [_r.randint(1, 30) for _ in range(1500)]
_nl6 = list(range(1500, 0, -1))
_nl7 = [_r.randint(-5, 5) for _ in range(1200)]

add(
    id="count-longest-increasing-subsequences", title="Count Longest Increasing Subsequences", diff="Medium", topic=TOPIC,
    fn="countLongestIncreasing", params=[("nums", "int[]")], ret="int", cmp="exact",
    desc="<p>A <em>strictly increasing subsequence</em> of <code>nums</code> is obtained by deleting zero or more elements, without reordering the rest, so that the remaining values strictly increase from left to right.</p><p>Find the length <code>L</code> of the longest strictly increasing subsequence, then return how many different subsequences have length <code>L</code>. Two subsequences are different if they use different index sets, even when they contain equal values. Return the count modulo <code>1,000,000,007</code>.</p>",
    constraints=["1 &le; nums.length &le; 1,500", "-1,000,000 &le; nums[i] &le; 1,000,000"],
    hints=["Computing only the length of the longest increasing subsequence is the standard DP: len[i] = 1 + max len[j] over j &lt; i with nums[j] &lt; nums[i].",
           "Along with len[i], keep cnt[i], the number of increasing subsequences of that maximum length that end exactly at index i.",
           "When you scan j &lt; i with nums[j] &lt; nums[i]: if len[j] + 1 beats len[i], set len[i] = len[j] + 1 and cnt[i] = cnt[j]; if it ties, add cnt[j] to cnt[i]. The answer sums cnt[i] over all i with len[i] equal to the global maximum."],
    editorial=["For each index i define <code>len[i]</code>, the length of the longest increasing subsequence ending at i, and <code>cnt[i]</code>, how many subsequences of that length end at i. Initially both are 1 (the element on its own). For every earlier index j with <code>nums[j] &lt; nums[i]</code>, the candidate length is <code>len[j] + 1</code>: a strictly larger candidate replaces <code>len[i]</code> and resets <code>cnt[i] = cnt[j]</code>, while an equal candidate adds <code>cnt[j]</code> to <code>cnt[i]</code>.",
               "Every longest subsequence ends somewhere, so the answer is the sum of <code>cnt[i]</code> over all i whose <code>len[i]</code> equals the maximum length (modulo 1,000,000,007). The double loop is O(n<sup>2</sup>) time and O(n) space; a Fenwick tree over compressed values can bring it down to O(n log n)."],
    time="O(n^2)", space="O(n)",
    solution='''def countLongestIncreasing(nums):
    M = 1000000007
    n = len(nums)
    length = [1] * n
    count = [1] * n
    for i in range(n):
        x = nums[i]
        li, ci = 1, 1
        for j in range(i):
            if nums[j] < x:
                cand = length[j] + 1
                if cand > li:
                    li, ci = cand, count[j]
                elif cand == li:
                    ci += count[j]
        length[i] = li
        count[i] = ci % M
    best = max(length)
    return sum(count[i] for i in range(n) if length[i] == best) % M
''',
    tests=[[[1, 3, 5, 4, 7]], [[2, 2, 2, 2, 2]], [[1]], [[1, 2, 3, 4]], [[4, 3, 2, 1]], [[1, 2, 4, 3, 5, 4, 7, 2]],
           [[-3, -1, -2, 0, 1]], [[2, 1, 4, 3, 6, 5]], [[1, 1, 2, 2, 3, 3]], [[10, 9, 2, 5, 3, 7, 101, 18]],
           [_nl1], [_nl2], [_nl3], [_nl4], [_nl5], [_nl6], [_nl7]],
)


def _brute_nlis(nums):
    n = len(nums)
    best, cnt = 0, 0
    for size in range(1, n + 1):
        found = 0
        for idx in combinations(range(n), size):
            if all(nums[a] < nums[b] for a, b in zip(idx, idx[1:])):
                found += 1
        if found:
            best, cnt = size, found
    return cnt % MOD


def _v_nlis(tests):
    for t in tests:
        a = t["args"][0]
        assert 1 <= len(a) <= 1500 and all(-10 ** 6 <= x <= 10 ** 6 for x in a)


CHECKS["count-longest-increasing-subsequences"] = (_brute_nlis, lambda r: [gen_arr(r, -4, 4, 1, 11)], "exact")
VALIDATE["count-longest-increasing-subsequences"] = _v_nlis


# ---------------------------------------------------------------- HARD

_r = rnd(7108)
_sk1 = (50, [_r.randint(0, 1000) for _ in range(3000)])
_sk2 = (100, [996 * (i % 2) + _r.randint(0, 3) for i in range(3000)])
_sk3 = (1, [_r.randint(0, 1000) for _ in range(3000)])
_sk4 = (7, [1000 - i // 3 for i in range(3000)])
_sk5 = (3, [(i * 37 + 11) % 997 for i in range(3000)])
_sk6 = (100, [(i % 40) * 20 for i in range(2500)])
_sk7 = (200, [_r.randint(0, 1000) for _ in range(300)])

add(
    id="stock-profit-at-most-k-transactions", title="Stock Profit with At Most K Transactions", diff="Hard", topic=TOPIC,
    fn="maxProfitK", params=[("k", "int"), ("prices", "int[]")], ret="int", cmp="exact",
    desc="<p><code>prices[i]</code> is the price of a stock on day <code>i</code>. You may complete at most <code>k</code> transactions, where one transaction is one purchase followed by one later sale of a single share. You can hold at most one share at a time, so you must sell before buying again (selling and buying again on the same day is allowed).</p><p>Return the maximum profit you can achieve; if no profitable transaction exists, the answer is <code>0</code>.</p>",
    constraints=["0 &le; k &le; 200", "1 &le; prices.length &le; 3,000", "0 &le; prices[i] &le; 1,000"],
    hints=["Decide per day among three actions: buy, sell, or do nothing. What do you need to remember to make that decision later?",
           "Track two quantities per number of completed/started transactions j: buy[j], the best balance while holding a share bought in your j-th transaction, and sell[j], the best balance after completing j transactions.",
           "Process prices left to right and update buy[j] = max(buy[j], sell[j-1] - p) and sell[j] = max(sell[j], buy[j] + p) for every j from 1 to k. If k &ge; n/2 the limit is irrelevant: just add up every positive day-to-day gain."],
    editorial=["Think of each day as a state machine: either you hold no share or you hold one. Let <code>sell[j]</code> be the best cash balance after completing exactly j transactions (flat position) and <code>buy[j]</code> the best balance while holding a share from your j-th transaction. A new price p lets you buy (<code>buy[j] = max(buy[j], sell[j-1] - p)</code>) or sell (<code>sell[j] = max(sell[j], buy[j] + p)</code>). Initialise <code>sell[0] = 0</code>, every <code>buy[j]</code> to negative infinity and the rest of <code>sell</code> to 0 (fewer transactions than allowed is fine). After all days, <code>sell[k]</code> is the answer.",
               "Each day costs O(k) updates, so the total is O(n &times; k) time with O(k) memory. One transaction needs at least two days, so with more than n/2 transactions the limit never binds; in that case the best profit is the sum of all positive differences between consecutive days, which keeps time and memory O(n) even for huge k."],
    time="O(n k)", space="O(k)",
    solution='''def maxProfitK(k, prices):
    n = len(prices)
    if k == 0 or n < 2:
        return 0
    if k >= n // 2:
        return sum(max(0, prices[i] - prices[i - 1]) for i in range(1, n))
    NEG = -10 ** 9
    buy = [NEG] * (k + 1)
    sell = [0] * (k + 1)
    for p in prices:
        for j in range(1, k + 1):
            if sell[j - 1] - p > buy[j]:
                buy[j] = sell[j - 1] - p
            if buy[j] + p > sell[j]:
                sell[j] = buy[j] + p
    return sell[k]
''',
    tests=[[2, [2, 4, 1]], [2, [3, 2, 6, 5, 0, 3]], [1, [7, 6, 4, 3, 1]], [3, [1]], [0, [1, 5]], [1, [1, 2, 3, 4, 5]],
           [2, [1, 2, 4, 2, 5, 7, 2, 4, 9, 0]], [2, [3, 3, 5, 0, 0, 3, 1, 4]], [100, [5, 1, 5, 1, 5]],
           [1, [2, 1, 4, 5, 2, 9, 7]], [200, [0, 1000, 0, 1000]], [3, [0, 0, 0, 0]],
           list(_sk1), list(_sk2), list(_sk3), list(_sk4), list(_sk5), list(_sk6), list(_sk7)],
)


def _brute_stock_k(k, prices):
    n = len(prices)

    def go(i, holding, left):
        # left = transactions that may still be started
        if i == n:
            return 0
        best = go(i + 1, holding, left)
        if holding:
            best = max(best, prices[i] + go(i + 1, False, left))
        elif left > 0:
            best = max(best, -prices[i] + go(i + 1, True, left - 1))
        return best

    return go(0, False, k)


def _gen_stock_k(r):
    return [r.randint(0, 4), [r.randint(0, 9) for _ in range(r.randint(1, 11))]]


def _v_stock_k(tests):
    for t in tests:
        k, p = t["args"]
        assert 0 <= k <= 200 and 1 <= len(p) <= 3000 and all(0 <= x <= 1000 for x in p)
        assert t["expected"] >= 0


CHECKS["stock-profit-at-most-k-transactions"] = (_brute_stock_k, _gen_stock_k, "exact")
VALIDATE["stock-profit-at-most-k-transactions"] = _v_stock_k

# ------------------------------------------------------------------

_r = rnd(7109)
_tw1 = (1000, [_r.randint(1, 20000) for _ in range(5000)])
_tw2 = (1, [_r.randint(1, 20000) for _ in range(5000)])
_tw3 = (1666, [20000] * 5000)
_tw4 = (50, [1 + (i * 7919) % 20000 for i in range(4000)])
_tw5 = (400, [(20000 if (i // 400) % 3 == 1 else 1) for i in range(5000)])
_tw6 = (1000, [_r.randint(1, 5) for _ in range(3000)])

add(
    id="three-nonoverlapping-windows-max-sum", title="Three Non-Overlapping Windows", diff="Hard", topic=TOPIC,
    fn="maxSumThreeWindows", params=[("nums", "int[]"), ("k", "int")], ret="int", cmp="exact",
    desc="<p>A <em>window</em> is a block of exactly <code>k</code> consecutive elements of <code>nums</code>. Choose three windows that do not share any index (they may be adjacent) so that the total of all the elements inside them is as large as possible, and return that largest total.</p><p>It is guaranteed that <code>nums.length &ge; 3 * k</code>, so three windows always fit.</p>",
    constraints=["1 &le; k and 3 * k &le; nums.length &le; 5,000", "1 &le; nums[i] &le; 20,000"],
    hints=["Prefix sums let you get the sum of any window of length k in O(1). Let w[i] be the sum of the window starting at index i.",
           "Three windows are ordered left to right: starts a, b, c with a + k &le; b and b + k &le; c. Fix the middle window b and think about the best choices to its left and right separately.",
           "Precompute left[i] = the best w[a] with a &le; i and right[i] = the best w[c] with c &ge; i. Then the answer is the maximum over b of left[b - k] + w[b] + right[b + k]."],
    editorial=["Let <code>w[i]</code> be the sum of <code>nums[i..i+k-1]</code>, computed in O(n) with a running sum. Any valid selection has windows at starts <code>a &lt; b &lt; c</code> with <code>b &ge; a + k</code> and <code>c &ge; b + k</code>. Fix the middle start b: the best first window is the maximum of <code>w[a]</code> over <code>a &le; b - k</code>, and the best third is the maximum of <code>w[c]</code> over <code>c &ge; b + k</code>.",
               "Both of those are running maxima, so build <code>left[i] = max(w[0..i])</code> and <code>right[i] = max(w[i..end])</code> in one pass each. Then iterate b from k up to the last start that still leaves room for a third window, and take the maximum of <code>left[b - k] + w[b] + right[b + k]</code>. Everything is O(n) time and O(n) space. The answer is a sum, so there is no ambiguity even when several choices tie."],
    time="O(n)", space="O(n)",
    solution='''def maxSumThreeWindows(nums, k):
    n = len(nums)
    m = n - k + 1                     # number of window starts
    w = [0] * m
    s = sum(nums[:k])
    w[0] = s
    for i in range(1, m):
        s += nums[i + k - 1] - nums[i - 1]
        w[i] = s
    left = w[:]
    for i in range(1, m):
        if left[i - 1] > left[i]:
            left[i] = left[i - 1]
    right = w[:]
    for i in range(m - 2, -1, -1):
        if right[i + 1] > right[i]:
            right[i] = right[i + 1]
    best = 0
    for b in range(k, m - k):
        total = left[b - k] + w[b] + right[b + k]
        if total > best:
            best = total
    return best
''',
    tests=[[[1, 2, 1, 2, 6, 7, 5, 1], 2], [[1, 2, 1, 2, 1, 2, 1, 2, 1], 2], [[4, 5, 10, 6, 11, 17, 4, 11, 1, 3], 1],
           [[1, 1, 1], 1], [[5, 5, 5, 5, 5, 5], 2], [[9, 1, 1, 1, 9, 1, 1, 1, 9], 1], [[1, 100, 1, 1, 100, 1, 1, 100, 1], 3],
           [[3, 1, 4, 1, 5, 9, 2, 6, 5, 3, 5, 8], 4], [[20000, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 20000], 4],
           [[7, 7, 7, 7, 7, 7, 7], 2], [[2, 9, 2, 2, 2, 9, 2, 2, 2, 9, 2], 1],
           list(_tw1)[::-1], list(_tw2)[::-1], list(_tw3)[::-1], list(_tw4)[::-1], list(_tw5)[::-1], list(_tw6)[::-1]],
)


def _brute_three(nums, k):
    n = len(nums)
    best = 0
    for a in range(n - k + 1):
        for b in range(a + k, n - k + 1):
            for c in range(b + k, n - k + 1):
                total = sum(nums[a:a + k]) + sum(nums[b:b + k]) + sum(nums[c:c + k])
                best = max(best, total)
    return best


def _gen_three(r):
    k = r.randint(1, 3)
    n = r.randint(3 * k, 3 * k + 8)
    return [[r.randint(1, 9) for _ in range(n)], k]


def _v_three(tests):
    for t in tests:
        a, k = t["args"]
        assert 1 <= k and 3 * k <= len(a) <= 5000 and all(1 <= x <= 20000 for x in a)


CHECKS["three-nonoverlapping-windows-max-sum"] = (_brute_three, _gen_three, "exact")
VALIDATE["three-nonoverlapping-windows-max-sum"] = _v_three
