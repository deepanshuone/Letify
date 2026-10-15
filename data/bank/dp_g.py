"""Problems: dynamic programming, coin change and unbounded knapsack family. See data/lib.py for the registry."""
from collections import deque
from functools import lru_cache
from itertools import product

from lib import add, rnd, CHECKS, VALIDATE, gen_arr  # noqa: F401

TOPIC = "Dynamic Programming"
MOD = 10 ** 9 + 7


def distinct(a):
    return len(set(a)) == len(a)


# ---------------------------------------------------------------- EASY

p = add(
    id="rod-cutting-with-cut-fee", title="Rod Cutting With a Cutting Fee", diff="Easy", topic=TOPIC,
    fn="rodCutting", params=[("prices", "int[]"), ("fee", "int")], ret="int", cmp="exact",
    desc="<p>A steel rod has an integer length <code>n = prices.length</code>. A piece of length <code>i</code> (for <code>1 &le; i &le; n</code>) sells for <code>prices[i - 1]</code>, and the prices need not grow with the length. You may cut the rod into any number of pieces of integer length, and you may also sell it uncut.</p><p>Every single cut costs <code>fee</code>, whatever its position. Cutting a rod into <code>m</code> pieces therefore costs <code>(m - 1) * fee</code>. Return the largest possible profit, that is the total selling price of all pieces minus the cutting fees.</p><pre>prices = [1,5,8,9,10,17,17,20], fee = 0 -> 22   (lengths 2 + 6)\nprices = [1,5,8,9,10,17,17,20], fee = 1 -> 21   (22 - 1 for the single cut)\nprices = [1,5,8,9,10,17,17,20], fee = 3 -> 20   (selling it whole beats every cut)</pre>",
    constraints=["1 &le; prices.length &le; 1,000", "0 &le; prices[i] &le; 1,000,000", "0 &le; fee &le; 1,000,000"],
    hints=["Look at the first piece you cut off the left end of the rod. What is left over once it is gone?",
           "Let best[L] be the best profit for a rod of length L. Either sell it whole, or cut off a first piece of length j (price prices[j - 1]), pay one fee, and then solve the remaining rod of length L - j.",
           "best[L] = max(prices[L - 1], max over 1 &le; j &lt; L of prices[j - 1] - fee + best[L - j]). Fill L from 1 up to n and return best[n]."],
    editorial=["Every rod length is a smaller copy of the same question, so define <code>best[L]</code> as the maximum profit for a rod of length <code>L</code> (fees included). For a given <code>L</code> there are two kinds of plans. Either the rod is sold whole, giving <code>prices[L - 1]</code>, or at least one cut is made. In the second case look at the leftmost piece, say of length <code>j</code>. It earns <code>prices[j - 1]</code>, the cut that separates it from the rest costs <code>fee</code>, and the remaining <code>L - j</code> units are an independent smaller problem worth <code>best[L - j]</code>.",
               "So <code>best[L] = max(prices[L - 1], max(prices[j - 1] - fee + best[L - j]))</code> for <code>1 &le; j &lt; L</code>. Charging the fee exactly when a first piece is cut away counts every cut once, because a plan with <code>m</code> pieces is built from exactly <code>m - 1</code> such first-piece steps. This is an unbounded knapsack in disguise: the 'items' are the piece lengths 1..n, they can be used any number of times, and the capacity is the rod length. Time is O(n&sup2;), space O(n)."],
    time="O(n^2)", space="O(n)",
    solution='''def rodCutting(prices, fee):
    n = len(prices)
    best = [0] * (n + 1)
    for length in range(1, n + 1):
        top = prices[length - 1]
        for j in range(1, length):
            cand = prices[j - 1] - fee + best[length - j]
            if cand > top:
                top = cand
        best[length] = top
    return best[n]
''',
    tests=[[[1, 5, 8, 9, 10, 17, 17, 20], 0], [[1, 5, 8, 9, 10, 17, 17, 20], 1], [[1, 5, 8, 9, 10, 17, 17, 20], 3],
           [[7], 0], [[0], 5], [[3, 4], 5], [[3, 4], 0], [[2, 3, 7, 8], 1], [[0, 0, 0, 0], 0], [[1, 1, 1, 1, 1, 1], 1],
           [[4, 1, 1, 1, 1], 0], [[5, 10, 15, 20, 25], 4]],
)
_r = rnd(8101)
p["tests"].append([[_r.randint(0, 10 ** 6) for _ in range(1000)], 1000])
p["tests"].append([[int(10 ** 6 * ((i + 1) / 1000) ** 0.5) for i in range(1000)], 0])
p["tests"].append([[(i + 1) * 1000 for i in range(1000)], 999])
p["tests"].append([[_r.randint(0, 1000) * (i % 7 + 1) for i in range(800)], 12345])


def b_rod(prices, fee):
    n = len(prices)
    best = 0
    # every composition of n: bit i set means a cut after unit i + 1
    for mask in range(1 << (n - 1)):
        total, cuts, run = 0, 0, 1
        for i in range(n - 1):
            if mask >> i & 1:
                total += prices[run - 1]
                cuts += 1
                run = 1
            else:
                run += 1
        total += prices[run - 1]
        best = max(best, total - cuts * fee)
    return best


def g_rod(r):
    n = r.randint(1, 10)
    return [[r.randint(0, 12) for _ in range(n)], r.randint(0, 8)]


def v_rod(tests):
    for t in tests:
        prices, fee = t["args"]
        assert 1 <= len(prices) <= 1000 and all(0 <= x <= 10 ** 6 for x in prices)
        assert 0 <= fee <= 10 ** 6
        assert t["expected"] >= prices[-1]


CHECKS["rod-cutting-with-cut-fee"] = (b_rod, g_rod, "exact")
VALIDATE["rod-cutting-with-cut-fee"] = v_rod

p = add(
    id="count-unpayable-amounts", title="Count Unpayable Amounts", diff="Easy", topic=TOPIC, tier="extra",
    fn="countUnpayable", params=[("coins", "int[]"), ("limit", "int")], ret="int", cmp="exact",
    desc="<p>A cashier has an unlimited supply of coins of each value listed in <code>coins</code>. An amount is <em>payable</em> if it can be written as a sum of coins (a coin may be used many times).</p><p>Return how many integers in the range <code>1..limit</code> are <strong>not</strong> payable.</p><pre>coins = [3,5], limit = 10 -> 4   (1, 2, 4 and 7 cannot be paid)\ncoins = [4,6], limit = 12 -> 7   (only 4, 6, 8, 10, 12 can be paid)\ncoins = [1],   limit = 5  -> 0</pre>",
    constraints=["1 &le; coins.length &le; 12", "1 &le; coins[i] &le; 10,000", "1 &le; limit &le; 20,000"],
    hints=["Instead of counting the bad amounts directly, decide for each amount from 1 up whether it is payable.",
           "An amount s is payable exactly when s - c is payable for some coin c &le; s, with 0 counted as payable.",
           "Keep a boolean array reachable[0..limit] with reachable[0] = true, fill it from left to right, and count the false entries among 1..limit."],
    editorial=["Let <code>reachable[s]</code> say whether amount <code>s</code> can be paid. The empty payment gives <code>reachable[0] = true</code>. For <code>s &ge; 1</code>, think of the last coin <code>c</code> of some payment: removing it leaves a payment of <code>s - c</code>. So <code>s</code> is payable exactly when <code>reachable[s - c]</code> holds for at least one coin <code>c &le; s</code>.",
               "Fill the array from small to large amounts and count the entries in <code>1..limit</code> that stay false. This is the boolean version of coin change, with O(limit &middot; n) time and O(limit) space. (If the coins have a common divisor larger than 1, infinitely many amounts are unpayable, and that is why the question is bounded by <code>limit</code>.)"],
    time="O(limit * n)", space="O(limit)",
    solution='''def countUnpayable(coins, limit):
    coins = sorted(set(coins))
    reachable = [False] * (limit + 1)
    reachable[0] = True
    bad = 0
    for s in range(1, limit + 1):
        for c in coins:
            if c > s:
                break
            if reachable[s - c]:
                reachable[s] = True
                break
        if not reachable[s]:
            bad += 1
    return bad
''',
    tests=[[[3, 5], 10], [[4, 6], 12], [[1], 5], [[2], 1], [[7], 20], [[5, 10, 25], 30], [[3, 4], 100], [[2, 4, 6], 9],
           [[10000], 20000], [[6, 9, 20], 100], [[9, 6, 6, 9], 30]],
)
_r = rnd(8102)
p["tests"].append([[9973, 9967, 9949, 9941, 9929], 20000])
p["tests"].append([[_r.randint(500, 10000) for _ in range(12)], 20000])
p["tests"].append([[2, 10000], 20000])
p["tests"].append([[_r.randint(40, 90) for _ in range(5)], 20000])


def b_unpayable(coins, limit):
    # enumerates payments by number of coins, a different route than the reachability recurrence
    payable = {0}
    layer = {0}
    while layer:
        nxt = set()
        for s in layer:
            for c in coins:
                if s + c <= limit and s + c not in payable:
                    nxt.add(s + c)
        payable |= nxt
        layer = nxt
    return limit - len([s for s in payable if s >= 1])


def g_unpayable(r):
    return [[r.randint(1, 12) for _ in range(r.randint(1, 4))], r.randint(1, 60)]


def v_unpayable(tests):
    for t in tests:
        coins, limit = t["args"]
        assert 1 <= len(coins) <= 12 and all(1 <= c <= 10000 for c in coins)
        assert 1 <= limit <= 20000 and 0 <= t["expected"] <= limit


CHECKS["count-unpayable-amounts"] = (b_unpayable, g_unpayable, "exact")
VALIDATE["count-unpayable-amounts"] = v_unpayable


# -------------------------------------------------------------- MEDIUM

p = add(
    id="integer-break-max-product", title="Integer Break Maximum Product", diff="Medium", topic=TOPIC,
    fn="integerBreak", params=[("n", "int")], ret="int", cmp="exact",
    desc="<p>Split the positive integer <code>n</code> into <strong>at least two</strong> positive integers that add up to <code>n</code>. Return the largest product the parts can have.</p><pre>n = 2  -> 1    (1 + 1)\nn = 6  -> 9    (3 + 3)\nn = 10 -> 36   (3 + 3 + 4)</pre>",
    constraints=["2 &le; n &le; 58"],
    hints=["Try small n by hand: 2, 3, 4, 5, 6, 7. Which part sizes keep showing up in the best splits?",
           "Look at the first part j that you take off. The rest, n - j, is either kept whole or itself split further, so you can multiply j by max(n - j, best[n - j]).",
           "Compute best[i] for i = 2..n with best[i] = max over 1 &le; j &lt; i of j * max(i - j, best[i - j]). Notice that this is an unbounded knapsack where the weights are the part sizes and the 'value' is a product."],
    editorial=["Let <code>best[i]</code> be the largest product of a split of <code>i</code> into at least two parts. Take the first part <code>j</code> (with <code>1 &le; j &lt; i</code>). What remains is <code>i - j</code>, and the remaining part may either stay as a single number, contributing <code>i - j</code>, or be split further, contributing <code>best[i - j]</code>. Hence <code>best[i] = max(j * max(i - j, best[i - j]))</code> over all <code>j</code>. The small cases <code>best[2] = 1</code> and <code>best[3] = 2</code> start the table. The table takes O(n&sup2;) time.",
               "The table also reveals the pattern behind the closed form: an optimal split consists of 3s, plus one 2 or two 2s (or one 4) for the remainder. Parts of size 1 never help, parts of size 4 or more can be broken into 2s and 3s without losing product, and three 2s (product 8) are worse than two 3s (product 9). The range of n is capped at 58 so that the result fits in a 32-bit signed integer."],
    time="O(n^2)", space="O(n)",
    solution='''def integerBreak(n):
    best = [0] * (n + 1)
    best[1] = 1
    for i in range(2, n + 1):
        top = 0
        for j in range(1, i):
            cand = j * max(i - j, best[i - j])
            if cand > top:
                top = cand
        best[i] = top
    return best[n]
''',
    tests=[[2], [3], [4], [5], [6], [7], [8], [9], [10], [11], [12], [25], [40], [57], [58]],
)


def b_break(n):
    best = 0

    def go(remaining, maxpart, prod, parts):
        nonlocal best
        if remaining == 0:
            if parts >= 2:
                best = max(best, prod)
            return
        for x in range(1, min(remaining, maxpart) + 1):
            go(remaining - x, x, prod * x, parts + 1)

    go(n, n, 1, 0)
    return best


def v_break(tests):
    for t in tests:
        assert 2 <= t["args"][0] <= 58


CHECKS["integer-break-max-product"] = (b_break, lambda r: [r.randint(2, 16)], "exact")
VALIDATE["integer-break-max-product"] = v_break

p = add(
    id="partitions-into-exactly-k-parts", title="Partitions Into Exactly K Parts", diff="Medium", topic=TOPIC,
    fn="countPartitions", params=[("n", "int"), ("k", "int")], ret="int", cmp="exact",
    desc="<p>A <em>partition</em> of <code>n</code> into <code>k</code> parts is a way of writing <code>n</code> as a sum of exactly <code>k</code> positive integers where the order does not matter (so <code>1 + 2 + 2</code> and <code>2 + 1 + 2</code> are the same partition).</p><p>Return the number of such partitions, modulo <code>1,000,000,007</code>. If no partition exists the answer is <code>0</code>.</p><pre>n = 5, k = 2  -> 2    (4+1, 3+2)\nn = 7, k = 3  -> 4    (5+1+1, 4+2+1, 3+3+1, 3+2+2)\nn = 4, k = 5  -> 0</pre>",
    constraints=["1 &le; n &le; 800", "1 &le; k &le; 800"],
    hints=["Count partitions without caring about order by always writing the parts in non-increasing order. Consider the smallest part of a partition.",
           "If the smallest part equals 1, delete it: you get a partition of n - 1 into k - 1 parts. Otherwise every part is at least 2, so subtract 1 from each part.",
           "p(n, k) = p(n - 1, k - 1) + p(n - k, k), with p(0, 0) = 1. Only the previous row of k is needed, so a rolling array over k works."],
    editorial=["Let <code>p(s, j)</code> be the number of partitions of <code>s</code> into exactly <code>j</code> parts. Split the partitions by their smallest part. If the smallest part is <code>1</code>, removing it leaves any partition of <code>s - 1</code> into <code>j - 1</code> parts, and this correspondence is reversible, giving <code>p(s - 1, j - 1)</code>. If the smallest part is at least <code>2</code>, subtract one from every part: this gives a partition of <code>s - j</code> into <code>j</code> parts, again reversibly, giving <code>p(s - j, j)</code>. So <code>p(s, j) = p(s - 1, j - 1) + p(s - j, j)</code>, with <code>p(0, 0) = 1</code>.",
               "The second term is an unbounded-knapsack style step: it re-uses the same row <code>j</code>, which is why it can be computed in increasing order of <code>s</code> within one row. Iterate <code>j</code> from 1 to <code>k</code> and keep only the previous row. Time is O(n &middot; k), space O(n). Because the number of partitions grows very fast, the answer is taken modulo 1,000,000,007."],
    time="O(n * k)", space="O(n)",
    solution='''def countPartitions(n, k):
    MOD = 1000000007
    prev = [0] * (n + 1)
    prev[0] = 1
    for j in range(1, k + 1):
        cur = [0] * (n + 1)
        for s in range(j, n + 1):
            cur[s] = (prev[s - 1] + cur[s - j]) % MOD
        prev = cur
    return prev[n]
''',
    tests=[[5, 2], [7, 3], [4, 5], [1, 1], [6, 6], [6, 1], [10, 4], [10, 10], [12, 3], [20, 7], [30, 15], [100, 1], [2, 2], [3, 2]],
)
p["tests"].append([800, 400])
p["tests"].append([800, 800])
p["tests"].append([800, 40])
p["tests"].append([500, 700])


def b_partitions(n, k):
    # conjugation: partitions of n into exactly k parts == partitions of n - k into parts of size at most k
    m = n - k
    if m < 0:
        return 0
    ways = [1] + [0] * m
    for part in range(1, k + 1):
        for s in range(part, m + 1):
            ways[s] += ways[s - part]
    return ways[m] % MOD


def g_partitions(r):
    return [r.randint(1, 22), r.randint(1, 9)]


def v_partitions(tests):
    for t in tests:
        n, k = t["args"]
        assert 1 <= n <= 800 and 1 <= k <= 800
        assert 0 <= t["expected"] < MOD
        assert (t["expected"] == 0) == (k > n) or k <= n


CHECKS["partitions-into-exactly-k-parts"] = (b_partitions, g_partitions, "exact")
VALIDATE["partitions-into-exactly-k-parts"] = v_partitions

p = add(
    id="max-coins-using-every-denomination", title="Most Coins Using Every Denomination", diff="Medium", topic=TOPIC, tier="extra",
    fn="maxCoins", params=[("coins", "int[]"), ("amount", "int")], ret="int", cmp="exact",
    desc="<p>A collector wants to pay exactly <code>amount</code> using coins whose distinct values are listed in <code>coins</code>. Each value is available in unlimited quantity, but the payment must contain <strong>at least one coin of every value</strong> in <code>coins</code>.</p><p>Return the <strong>largest</strong> number of coins such a payment can contain, or <code>-1</code> if no valid payment exists.</p><pre>coins = [2,3], amount = 10 -> 4    (2+3 mandatory, then 2+3 again)\ncoins = [2,3], amount = 4  -> -1   (2+3 alone is already 5)\ncoins = [5],   amount = 15 -> 3</pre>",
    constraints=["1 &le; coins.length &le; 20", "1 &le; coins[i] &le; 1,000 and all values are distinct", "1 &le; amount &le; 10,000"],
    hints=["Ignore the 'at least one of each' rule for a moment. How would you find the largest number of coins that makes a given total?",
           "The rule is easy to enforce up front: pay one coin of every value first, then pay for what remains with no extra condition.",
           "Let rest = amount - sum(coins). If rest &lt; 0 return -1. Otherwise run an unbounded DP best[s] = max(best[s - c] + 1) with best[0] = 0 and unreachable = -infinity, and return len(coins) + best[rest] (or -1 if rest is unreachable)."],
    editorial=["Since every value must appear at least once, put one coin of each value into the payment right away. That uses <code>sum(coins)</code> of the amount and <code>len(coins)</code> coins. If this already exceeds <code>amount</code>, there is no valid payment. What remains is <code>rest = amount - sum(coins)</code>, which can now be paid with <em>any</em> coins from the list, with no further constraint, since the mandatory coins are already placed.",
               "Maximising instead of minimising only flips the comparison in the classic coin-change recurrence: <code>best[s] = max(best[s - c] + 1)</code> over coins <code>c &le; s</code> whose <code>best[s - c]</code> is reachable, with <code>best[0] = 0</code>. The answer is <code>len(coins) + best[rest]</code>, or <code>-1</code> when <code>rest</code> cannot be paid. Time is O(amount &middot; n), space O(amount)."],
    time="O(amount * n)", space="O(amount)",
    solution='''def maxCoins(coins, amount):
    rest = amount - sum(coins)
    if rest < 0:
        return -1
    best = [-1] * (rest + 1)
    best[0] = 0
    for s in range(1, rest + 1):
        top = -1
        for c in coins:
            if c <= s and best[s - c] >= 0 and best[s - c] + 1 > top:
                top = best[s - c] + 1
        best[s] = top
    if best[rest] < 0:
        return -1
    return len(coins) + best[rest]
''',
    tests=[[[2, 3], 10], [[2, 3], 4], [[5], 15], [[1], 1], [[1], 10000], [[3, 5], 8], [[3, 5], 9], [[3, 5], 11], [[4, 6], 11],
           [[1, 2, 5], 8], [[7, 11], 100], [[10, 20, 30], 59]],
)
_r = rnd(8103)
p["tests"].append([_r.sample(range(500, 1001), 3), 10000])
p["tests"].append([list(range(2, 40, 2)) + [1000], 10000])
p["tests"].append([[997, 991, 983, 977], 10000])


def b_maxcoins(coins, amount):
    n = len(coins)

    @lru_cache(maxsize=None)
    def go(i, rem):
        if i == n:
            return 0 if rem == 0 else -10 ** 9
        best = -10 ** 9
        c = coins[i]
        k = 1
        while k * c <= rem:
            best = max(best, k + go(i + 1, rem - k * c))
            k += 1
        return best

    res = go(0, amount)
    return res if res >= 0 else -1


def g_maxcoins(r):
    return [r.sample(range(1, 9), r.randint(1, 4)), r.randint(1, 40)]


def v_maxcoins(tests):
    for t in tests:
        coins, amount = t["args"]
        assert 1 <= len(coins) <= 20 and distinct(coins) and all(1 <= c <= 1000 for c in coins)
        assert 1 <= amount <= 10000


CHECKS["max-coins-using-every-denomination"] = (b_maxcoins, g_maxcoins, "exact")
VALIDATE["max-coins-using-every-denomination"] = v_maxcoins

p = add(
    id="min-coins-with-limited-supply", title="Fewest Coins With Limited Supply", diff="Medium", topic=TOPIC,
    fn="minCoinsLimited", params=[("coins", "int[]"), ("counts", "int[]"), ("amount", "int")], ret="int", cmp="exact",
    desc="<p>A wallet holds <code>counts[i]</code> coins of value <code>coins[i]</code> for every index <code>i</code>. The coin values are distinct and there is no divisibility pattern between them.</p><p>Return the fewest coins from the wallet that add up to exactly <code>amount</code>, or <code>-1</code> if it cannot be done. An amount of <code>0</code> needs <code>0</code> coins.</p><pre>coins = [1,5], counts = [2,3], amount = 12 -> 4   (5+5+1+1)\ncoins = [1,5], counts = [2,3], amount = 17 -> 5   (5+5+5+1+1)\ncoins = [3,4], counts = [1,1], amount = 6  -> -1</pre>",
    constraints=["1 &le; coins.length = counts.length &le; 20", "1 &le; coins[i] &le; 1,000 and all values are distinct", "0 &le; counts[i] &le; 1,000", "0 &le; amount &le; 3,000"],
    hints=["With unlimited coins this is the classic coin change. What breaks if you reuse that DP unchanged?",
           "A coin with count k can be taken 0..k times. You could try every number of copies, but there is a faster way: write k as a sum of pieces 1, 2, 4, ..., plus a remainder, so every number 0..k is a sum of some of the pieces.",
           "Turn each piece (t copies of value c) into one 0/1 item of weight t * c and cost t. Run the 0/1 knapsack minimum best[s] = min(best[s], best[s - w] + t) with s going downward, and read best[amount]."],
    editorial=["Splitting a supply of <code>k</code> identical coins into pieces of sizes <code>1, 2, 4, ..., 2^(m-1)</code> and a final remainder <code>r = k - (2^m - 1)</code> lets every count from <code>0</code> to <code>k</code> be formed as a sum of a subset of the pieces, and no larger count can be formed. Each piece of <code>t</code> copies behaves like one item that weighs <code>t * c</code> and costs <code>t</code> coins, to be taken or left whole.",
               "That turns the problem into a 0/1 knapsack with 'minimum cost for exactly this weight': <code>best[s] = min(best[s], best[s - w] + t)</code>, iterating <code>s</code> downward so each piece is used at most once, with <code>best[0] = 0</code> and everything else infinite. There are O(n &middot; log k) items, so the time is O(n &middot; log k &middot; amount). The answer is <code>best[amount]</code>, or <code>-1</code> if it is still infinite."],
    time="O(n * log(k) * amount)", space="O(amount)",
    solution='''def minCoinsLimited(coins, counts, amount):
    INF = float("inf")
    best = [INF] * (amount + 1)
    best[0] = 0
    for c, k in zip(coins, counts):
        piece = 1
        while k > 0:
            t = min(piece, k)
            k -= t
            piece *= 2
            w = c * t
            for s in range(amount, w - 1, -1):
                cand = best[s - w] + t
                if cand < best[s]:
                    best[s] = cand
    return -1 if best[amount] == INF else best[amount]
''',
    tests=[[[1, 5], [2, 3], 12], [[1, 5], [2, 3], 17], [[3, 4], [1, 1], 6], [[7], [3], 0], [[7], [3], 21], [[7], [3], 22],
           [[2, 5], [10, 1], 11], [[1, 3, 4], [1, 1, 1], 6], [[1, 3, 4], [0, 5, 0], 9], [[5, 2, 3], [0, 0, 0], 4],
           [[10, 7, 3], [4, 4, 4], 33], [[6, 4], [2, 3], 14]],
)
_r = rnd(8104)
_c = _r.sample(range(1, 1001), 20)
p["tests"].append([_c, [_r.randint(0, 1000) for _ in range(20)], 3000])
_c = _r.sample(range(1, 60), 20)
p["tests"].append([_c, [_r.randint(1, 1000) for _ in range(20)], 2999])
_c = _r.sample(range(100, 1001), 20)
p["tests"].append([_c, [_r.randint(1, 5) for _ in range(20)], 3000])


def b_minlimited(coins, counts, amount):
    n = len(coins)

    @lru_cache(maxsize=None)
    def go(i, rem):
        if rem == 0:
            return 0
        if i == n:
            return 10 ** 9
        best = 10 ** 9
        for k in range(min(counts[i], rem // coins[i]) + 1):
            best = min(best, k + go(i + 1, rem - k * coins[i]))
        return best

    res = go(0, amount)
    return res if res < 10 ** 9 else -1


def g_minlimited(r):
    n = r.randint(1, 4)
    return [r.sample(range(1, 10), n), [r.randint(0, 4) for _ in range(n)], r.randint(0, 30)]


def v_minlimited(tests):
    for t in tests:
        coins, counts, amount = t["args"]
        assert 1 <= len(coins) <= 20 and len(coins) == len(counts) and distinct(coins)
        assert all(1 <= c <= 1000 for c in coins) and all(0 <= k <= 1000 for k in counts)
        assert 0 <= amount <= 3000


CHECKS["min-coins-with-limited-supply"] = (b_minlimited, g_minlimited, "exact")
VALIDATE["min-coins-with-limited-supply"] = v_minlimited

p = add(
    id="count-coin-combinations-limited-supply", title="Coin Combinations With Limited Supply", diff="Medium", topic=TOPIC,
    fn="countLimitedCombos", params=[("coins", "int[]"), ("counts", "int[]"), ("amount", "int")], ret="int", cmp="exact",
    desc="<p>You own <code>counts[i]</code> coins of value <code>coins[i]</code> (all values distinct). Count the different ways to choose some of these coins so that their total is exactly <code>amount</code>.</p><p>Two ways are different if some value is used a different number of times; coins of equal value are interchangeable. Return the count modulo <code>1,000,000,007</code>. Choosing no coins is one way to make an amount of <code>0</code>.</p><pre>coins = [1,2,5], counts = [2,2,1], amount = 6 -> 2   (5+1 and 2+2+1+1)\ncoins = [1,5],   counts = [3,1],   amount = 5 -> 1   (just the 5)\ncoins = [4],     counts = [1],     amount = 8 -> 0</pre>",
    constraints=["1 &le; coins.length = counts.length &le; 30", "1 &le; coins[i] &le; 1,000 and all values are distinct", "0 &le; counts[i] &le; 1,000", "0 &le; amount &le; 5,000"],
    hints=["Process one value at a time. Let ways[s] be the number of ways to make s with the values handled so far.",
           "For a new value c with count k, new[s] = ways[s] + ways[s - c] + ... + ways[s - k*c]: you decide how many copies j (0..k) to take. Summing up to k terms for every s is too slow if done naively.",
           "That sum is a sliding window over positions s, s - c, s - 2c, .... Use new[s] = new[s - c] + ways[s] - ways[s - (k + 1) * c] (dropping the terms that fall outside) to get each entry in O(1)."],
    editorial=["Handle the values one after another and keep <code>ways[s]</code>, the number of ways to reach total <code>s</code> with the values processed so far. Adding a value <code>c</code> of which <code>k</code> copies exist, the new count is <code>new[s] = ways[s] + ways[s - c] + ways[s - 2c] + ... + ways[s - kc]</code>, because the number of copies used can be anything from 0 to <code>k</code>. Computing each such sum from scratch costs O(k), so the whole table would cost O(n &middot; amount &middot; k).",
               "The windows of consecutive entries overlap heavily. Compare <code>new[s]</code> with <code>new[s - c]</code>: they share every term except that <code>new[s]</code> gains <code>ways[s]</code> and loses <code>ways[s - (k + 1)c]</code>. So <code>new[s] = new[s - c] + ways[s] - ways[s - (k + 1)c]</code>, where terms with a negative index are treated as 0. Every entry is O(1), for a total of O(n &middot; amount) time and O(amount) space, all modulo 1,000,000,007."],
    time="O(n * amount)", space="O(amount)",
    solution='''def countLimitedCombos(coins, counts, amount):
    MOD = 1000000007
    ways = [0] * (amount + 1)
    ways[0] = 1
    for c, k in zip(coins, counts):
        new = [0] * (amount + 1)
        for s in range(amount + 1):
            v = ways[s]
            if s >= c:
                v += new[s - c]
            if s - (k + 1) * c >= 0:
                v -= ways[s - (k + 1) * c]
            new[s] = v % MOD
        ways = new
    return ways[amount]
''',
    tests=[[[1, 2, 5], [2, 2, 1], 6], [[1, 5], [3, 1], 5], [[4], [1], 8], [[4], [2], 8], [[4], [2], 0], [[3], [0], 0],
           [[2, 3], [1, 1], 5], [[1, 2, 3], [5, 5, 5], 10], [[1, 2], [1000, 1000], 3000], [[5, 10, 25], [3, 2, 1], 40],
           [[6, 4], [3, 3], 14], [[7, 3, 1], [0, 2, 9], 11]],
)
_r = rnd(8105)
_c = _r.sample(range(1, 1001), 30)
p["tests"].append([_c, [_r.randint(0, 1000) for _ in range(30)], 5000])
p["tests"].append([list(range(1, 31)), [1000] * 30, 5000])
_c = _r.sample(range(1, 200), 30)
p["tests"].append([_c, [_r.randint(1, 4) for _ in range(30)], 2500])


def b_limitedcombos(coins, counts, amount):
    total = 0
    for pick in product(*[range(k + 1) for k in counts]):
        if sum(a * b for a, b in zip(pick, coins)) == amount:
            total += 1
    return total % MOD


def g_limitedcombos(r):
    n = r.randint(1, 4)
    return [r.sample(range(1, 9), n), [r.randint(0, 4) for _ in range(n)], r.randint(0, 25)]


def v_limitedcombos(tests):
    for t in tests:
        coins, counts, amount = t["args"]
        assert 1 <= len(coins) <= 30 and len(coins) == len(counts) and distinct(coins)
        assert all(1 <= c <= 1000 for c in coins) and all(0 <= k <= 1000 for k in counts)
        assert 0 <= amount <= 5000 and 0 <= t["expected"] < MOD


CHECKS["count-coin-combinations-limited-supply"] = (b_limitedcombos, g_limitedcombos, "exact")
VALIDATE["count-coin-combinations-limited-supply"] = v_limitedcombos

p = add(
    id="coin-ways-with-at-most-k-coins", title="Coin Ways With At Most K Coins", diff="Medium", topic=TOPIC, tier="extra",
    fn="waysAtMostKCoins", params=[("coins", "int[]"), ("amount", "int"), ("k", "int")], ret="int", cmp="exact",
    desc="<p>Coins of the distinct values in <code>coins</code> are available in unlimited quantity. Count the combinations that add up to exactly <code>amount</code> and use <strong>at most <code>k</code> coins</strong> in total. The order of the coins does not matter: <code>1+2</code> and <code>2+1</code> are the same combination.</p><p>Return the count modulo <code>1,000,000,007</code>. The empty combination counts as one way to make <code>amount = 0</code>.</p><pre>coins = [1,2,5], amount = 5, k = 2 -> 1   (5)\ncoins = [1,2,5], amount = 5, k = 3 -> 2   (5 and 1+2+2)\ncoins = [1,2,5], amount = 5, k = 5 -> 4   (5, 1+2+2, 1+1+1+2, 1+1+1+1+1)</pre>",
    constraints=["1 &le; coins.length &le; 12", "1 &le; coins[i] &le; 1,000 and all values are distinct", "0 &le; amount &le; 800", "0 &le; k &le; 40"],
    hints=["The unordered coin-change count uses one dimension (the sum). Here the number of coins used matters too, so you need a second dimension.",
           "Let ways[j][s] be the number of combinations of exactly j coins that sum to s, using the coin values handled so far. Handle one value c at a time, in the outer loop, to keep the combinations unordered.",
           "For each coin c, for j = 1..k ascending and s = c..amount ascending: ways[j][s] += ways[j - 1][s - c]. The answer is the sum of ways[j][amount] over j = 0..k."],
    editorial=["Counting unordered combinations requires the outer loop to run over coin values, with the inner loops extending the combinations by that value; this way each multiset is built in exactly one order (all coins of the first value, then of the next, and so on). To enforce the limit on the number of coins, extend the state by the coin count: <code>ways[j][s]</code> is the number of combinations of exactly <code>j</code> coins with total <code>s</code>.",
               "Adding any number of copies of coin <code>c</code> is the usual unbounded update <code>ways[j][s] += ways[j - 1][s - c]</code>. For this to be correct, iterate <code>j</code> upward, so that <code>ways[j - 1][s - c]</code> already contains combinations that use <code>c</code> (which allows several copies of <code>c</code>). Finally add up <code>ways[j][amount]</code> for <code>j</code> from 0 to <code>k</code>. Time is O(n &middot; k &middot; amount), space O(k &middot; amount)."],
    time="O(n * k * amount)", space="O(k * amount)",
    solution='''def waysAtMostKCoins(coins, amount, k):
    MOD = 1000000007
    ways = [[0] * (amount + 1) for _ in range(k + 1)]
    ways[0][0] = 1
    for c in coins:
        for j in range(1, k + 1):
            prev = ways[j - 1]
            cur = ways[j]
            for s in range(c, amount + 1):
                if prev[s - c]:
                    cur[s] = (cur[s] + prev[s - c]) % MOD
    return sum(ways[j][amount] for j in range(k + 1)) % MOD
''',
    tests=[[[1, 2, 5], 5, 2], [[1, 2, 5], 5, 3], [[1, 2, 5], 5, 5], [[2], 3, 5], [[3], 0, 0], [[3], 0, 4], [[1], 10, 9],
           [[1], 10, 10], [[1, 2, 3, 4], 12, 4], [[1, 2, 3, 4], 12, 12], [[5, 10, 25], 100, 8], [[7, 3], 40, 40]],
)
_r = rnd(8106)
p["tests"].append([_r.sample(range(1, 40), 12), 800, 40])
p["tests"].append([list(range(1, 13)), 800, 40])
p["tests"].append([_r.sample(range(1, 1001), 12), 800, 25])


def b_atmostk(coins, amount, k):
    n = len(coins)

    @lru_cache(maxsize=None)
    def go(i, rem, left):
        if rem == 0:
            return 1
        if i == n:
            return 0
        total = 0
        for cnt in range(min(left, rem // coins[i]) + 1):
            total += go(i + 1, rem - cnt * coins[i], left - cnt)
        return total

    return go(0, amount, k) % MOD


def g_atmostk(r):
    return [r.sample(range(1, 9), r.randint(1, 4)), r.randint(0, 24), r.randint(0, 8)]


def v_atmostk(tests):
    for t in tests:
        coins, amount, k = t["args"]
        assert 1 <= len(coins) <= 12 and distinct(coins) and all(1 <= c <= 1000 for c in coins)
        assert 0 <= amount <= 800 and 0 <= k <= 40 and 0 <= t["expected"] < MOD


CHECKS["coin-ways-with-at-most-k-coins"] = (b_atmostk, g_atmostk, "exact")
VALIDATE["coin-ways-with-at-most-k-coins"] = v_atmostk


# ---------------------------------------------------------------- HARD

p = add(
    id="min-coins-paying-with-change-back", title="Fewest Coins Paying With Change Back", diff="Hard", topic=TOPIC, tier="extra",
    fn="minCoinsWithChange", params=[("coins", "int[]"), ("amount", "int")], ret="int", cmp="exact",
    desc="<p>You owe a shop <code>amount</code>. Both you and the cashier have an unlimited supply of coins of every value in <code>coins</code>. You hand over some coins whose total is at least <code>amount</code>, and the cashier gives back coins worth the difference as change.</p><p>Return the smallest possible number of coins that change hands in total (the coins you pay plus the coins you receive back), or <code>-1</code> if the amount cannot be settled this way. An amount of <code>0</code> needs <code>0</code> coins.</p><pre>coins = [7,8], amount = 1 -> 2        (pay 8, receive 7)\ncoins = [1,5,10,25,50,100], amount = 99 -> 2   (pay 100, receive 1)\ncoins = [3,5], amount = 4 -> 4        (pay 3+3+3, receive 5)\ncoins = [4,6], amount = 5 -> -1       (every payment is even)</pre>",
    constraints=["1 &le; coins.length &le; 40", "1 &le; coins[i] &le; 500", "0 &le; amount &le; 5,000"],
    hints=["Think of a coin you pay as +c and a coin you get back as -c. You need steps of size +-c that add up to amount. What does a shortest sequence of steps look like?",
           "This is a shortest path from 0 to amount on the number line, where each move adds or subtracts a coin value. Breadth-first search works, but the line is infinite in both directions. Show that you never need to leave a window around [0, amount].",
           "The steps can be reordered: whenever you are below amount take a +step, otherwise a -step. Then you never go above amount + max(coins) or below -max(coins). Run BFS only on positions in that window and return the distance of amount."],
    editorial=["Paying coins count as <code>+c</code> and returned coins as <code>-c</code>; a valid settlement is a multiset of signed coin values summing to <code>amount</code>, and the cost is how many signed coins there are. (Paying a coin and receiving the same value back is never useful.) The question is therefore a shortest path from <code>0</code> to <code>amount</code> where every move changes the position by plus or minus one coin value.",
               "The number line is unbounded, but the order of the moves does not change the total, so any solution can be replayed in a friendlier order: while the current position is below <code>amount</code> use one of the remaining positive moves (one exists, because the remaining moves must still sum to a positive number), and otherwise use a negative move. Positions then never exceed <code>amount + M</code> nor drop below <code>-M</code>, where <code>M</code> is the largest coin. So BFS inside the window <code>[-M, amount + M]</code> finds the optimum, with at most <code>amount + 2M</code> positions and <code>2n</code> moves from each. If the BFS never reaches <code>amount</code>, the answer is <code>-1</code>, which happens exactly when the gcd of the coins does not divide <code>amount</code>."],
    time="O((amount + M) * n)", space="O(amount + M)",
    solution='''from collections import deque


def minCoinsWithChange(coins, amount):
    if amount == 0:
        return 0
    coins = sorted(set(coins))
    big = coins[-1]
    lo, hi = -big, amount + big
    dist = [-1] * (hi - lo + 1)
    dist[0 - lo] = 0
    queue = deque([0])
    while queue:
        x = queue.popleft()
        d = dist[x - lo]
        for c in coins:
            for y in (x + c, x - c):
                if lo <= y <= hi and dist[y - lo] < 0:
                    if y == amount:
                        return d + 1
                    dist[y - lo] = d + 1
                    queue.append(y)
    return -1
''',
    tests=[[[7, 8], 1], [[1, 5, 10, 25, 50, 100], 99], [[3, 5], 4], [[4, 6], 5], [[10, 25], 5], [[2, 4], 0], [[5], 5],
           [[5], 15], [[5], 7], [[1], 1], [[1], 5000], [[7, 8], 6], [[9, 14, 20], 3], [[100, 101], 99], [[6, 10, 15], 1]],
)
_r = rnd(8107)
p["tests"].append([_r.sample(range(300, 501), 40), 4999])
p["tests"].append([[499, 500], 5000])
p["tests"].append([[2, 4, 6, 8, 10, 12], 4999])
p["tests"].append([[497, 491, 487], 4001])


def b_changeback(coins, amount):
    # same shortest path idea, but on a much wider window than the proof needs
    wide = 1200
    lo, hi = -wide, amount + wide
    dist = {0: 0}
    q = deque([0])
    while q:
        x = q.popleft()
        for c in coins:
            for y in (x + c, x - c):
                if lo <= y <= hi and y not in dist:
                    dist[y] = dist[x] + 1
                    q.append(y)
    return dist.get(amount, -1)


def g_changeback(r):
    return [r.sample(range(1, 13), r.randint(1, 4)), r.randint(0, 40)]


def v_changeback(tests):
    for t in tests:
        coins, amount = t["args"]
        assert 1 <= len(coins) <= 40 and all(1 <= c <= 500 for c in coins) and 0 <= amount <= 5000
        assert t["expected"] >= -1


CHECKS["min-coins-paying-with-change-back"] = (b_changeback, g_changeback, "exact")
VALIDATE["min-coins-paying-with-change-back"] = v_changeback

p = add(
    id="count-min-coin-combinations", title="Count Minimum Coin Combinations", diff="Hard", topic=TOPIC, tier="extra",
    fn="countMinCombos", params=[("coins", "int[]"), ("amount", "int")], ret="int", cmp="exact",
    desc="<p>Coins of the distinct values in <code>coins</code> are available in unlimited quantity. Among all ways to make <code>amount</code>, take those that use the <strong>fewest</strong> coins. Return how many different combinations achieve that minimum, modulo <code>1,000,000,007</code>, or <code>-1</code> if <code>amount</code> cannot be made at all.</p><p>Combinations are unordered: <code>1+3</code> and <code>3+1</code> are the same one. An amount of <code>0</code> has exactly one combination, the empty one.</p><pre>coins = [1,2,5], amount = 5 -> 1    (5)\ncoins = [1,3,4], amount = 6 -> 1    (3+3; 4+1+1 uses three coins)\ncoins = [1,2,3,4], amount = 8 -> 1  (4+4)\ncoins = [1,2,4,5], amount = 6 -> 2  (2+4 and 1+5)\ncoins = [2,4], amount = 7 -> -1</pre>",
    constraints=["1 &le; coins.length &le; 30", "1 &le; coins[i] &le; 10,000 and all values are distinct", "0 &le; amount &le; 10,000"],
    hints=["First solve the minimum number of coins with the classic DP. Then ask how you could count the ways in the same pass.",
           "Store two numbers per amount: the minimum coin count and how many combinations reach it. When you extend a state by a coin, the new count is either better (replace), equal (add) or worse (ignore).",
           "To count combinations rather than sequences, put the coins in the outer loop and amounts in the inner loop, ascending. Update with candidate = (best[s - c] + 1, ways[s - c]): if candidate &lt; best[s] replace both, if equal add ways."],
    editorial=["Let <code>best[s]</code> be the minimum number of coins for <code>s</code> and <code>ways[s]</code> the number of combinations that attain it, using only the coin values processed so far. Handling coin <code>c</code> splits the combinations for <code>s</code> into two disjoint groups: those without <code>c</code> (the old state of <code>s</code>) and those with at least one <code>c</code> (take a combination for <code>s - c</code>, with the new state already allowed to contain <code>c</code>, and add one coin). Merging the two groups is a small min-with-count: the smaller coin count wins and its count is kept; on a tie the counts add.",
               "Because the coins are in the outer loop, each unordered multiset is counted exactly once (in the order of the coin list). Iterating <code>s</code> upwards for the current coin lets it be used repeatedly. With the initial state <code>best[0] = 0</code>, <code>ways[0] = 1</code> and everything else infinite, the answer is <code>ways[amount]</code> (mod 1,000,000,007) when <code>best[amount]</code> is finite and <code>-1</code> otherwise. Time is O(n &middot; amount), space O(amount)."],
    time="O(n * amount)", space="O(amount)",
    solution='''def countMinCombos(coins, amount):
    MOD = 1000000007
    INF = float("inf")
    best = [INF] * (amount + 1)
    ways = [0] * (amount + 1)
    best[0] = 0
    ways[0] = 1
    for c in coins:
        for s in range(c, amount + 1):
            cand = best[s - c] + 1
            if cand < best[s]:
                best[s] = cand
                ways[s] = ways[s - c]
            elif cand == best[s]:
                ways[s] = (ways[s] + ways[s - c]) % MOD
    return -1 if best[amount] == INF else ways[amount]
''',
    tests=[[[1, 2, 5], 5], [[1, 3, 4], 6], [[1, 2, 3, 4], 8], [[1, 2, 4, 5], 6], [[2, 4], 7], [[5], 0], [[3], 9], [[3], 10],
           [[1, 5, 10, 25], 30], [[1, 5, 10, 25, 50], 100], [[2, 3, 7], 12], [[1, 2, 3, 4, 5, 6], 14]],
)
_r = rnd(8108)
p["tests"].append([list(range(1, 31)), 10000])
p["tests"].append([list(range(1, 31)), 9871])
p["tests"].append([_r.sample(range(1, 10001), 30), 10000])
p["tests"].append([_r.sample(range(50, 400), 30), 9999])
p["tests"].append([[1, 7, 9973], 10000])


def b_mincombos(coins, amount):
    n = len(coins)
    best_len = [10 ** 9]
    count = [0]

    def go(i, rem, used):
        if used > best_len[0]:
            return
        if rem == 0:
            if used < best_len[0]:
                best_len[0], count[0] = used, 1
            elif used == best_len[0]:
                count[0] += 1
            return
        if i == n:
            return
        k = 0
        while k * coins[i] <= rem:
            go(i + 1, rem - k * coins[i], used + k)
            k += 1

    go(0, amount, 0)
    return -1 if best_len[0] == 10 ** 9 else count[0] % MOD


def g_mincombos(r):
    return [r.sample(range(1, 11), r.randint(1, 5)), r.randint(0, 30)]


def v_mincombos(tests):
    for t in tests:
        coins, amount = t["args"]
        assert 1 <= len(coins) <= 30 and distinct(coins) and all(1 <= c <= 10000 for c in coins)
        assert 0 <= amount <= 10000
        assert t["expected"] == -1 or 0 <= t["expected"] < MOD


CHECKS["count-min-coin-combinations"] = (b_mincombos, g_mincombos, "exact")
VALIDATE["count-min-coin-combinations"] = v_mincombos

p = add(
    id="coin-sequences-no-adjacent-repeat", title="Coin Sequences Without Adjacent Repeats", diff="Hard", topic=TOPIC, tier="extra",
    fn="countSequences", params=[("coins", "int[]"), ("amount", "int")], ret="int", cmp="exact",
    desc="<p>Coins of the distinct values in <code>coins</code> are available in unlimited quantity. Count the <strong>ordered sequences</strong> of coins whose values add up to exactly <code>amount</code> and in which <strong>no two neighbouring coins have the same value</strong>.</p><p>Sequences are compared position by position, so <code>1,2</code> and <code>2,1</code> are different. Return the count modulo <code>1,000,000,007</code>.</p><pre>coins = [1,2,3], amount = 4 -> 3   (1,3 and 3,1 and 1,2,1)\ncoins = [1,2],   amount = 4 -> 1   (1,2,1)\ncoins = [2],     amount = 4 -> 0   (2,2 repeats a value)\ncoins = [1,3],   amount = 5 -> 1   (1,3,1)</pre>",
    constraints=["1 &le; coins.length &le; 50", "1 &le; coins[i] &le; 1,000 and all values are distinct", "1 &le; amount &le; 3,000"],
    hints=["Without the repeat rule this is the classic 'ordered ways' DP: ways[s] = sum of ways[s - c]. What extra information does the rule need?",
           "Track which coin the sequence ends with: end[s][j] is the number of valid sequences with total s whose last coin is coins[j]. Then end[s][j] depends on sequences for s - coins[j] that do not end with coins[j].",
           "end[s][j] = total[s - c_j] - end[s - c_j][j], with total[0] = 1 (the empty sequence) and end[0][j] = 0, where total[s] is the sum of end[s][j] over all j. Computing it this way avoids a loop over the previous coin, giving O(amount * n) in total."],
    editorial=["Let <code>end[s][j]</code> be the number of valid sequences that sum to <code>s</code> and end with coin <code>j</code>, and <code>total[s]</code> the sum over all <code>j</code>, with <code>total[0] = 1</code> for the empty sequence. A sequence ending in coin <code>j</code> is a shorter valid sequence (summing to <code>s - c_j</code>) followed by <code>c_j</code>, as long as that shorter sequence does not itself end with <code>c_j</code>. So <code>end[s][j] = total[s - c_j] - end[s - c_j][j]</code>. For <code>s = c_j</code> this correctly gives 1: the empty sequence followed by <code>c_j</code>.",
               "Looping over the previous coin would make each cell O(n), for O(amount &middot; n&sup2;) overall. Subtracting the 'bad' case from the total keeps each cell O(1): O(amount &middot; n) time and space. Everything is done modulo 1,000,000,007, so the subtraction must be normalised back into the range [0, mod). The answer is <code>total[amount]</code>."],
    time="O(amount * n)", space="O(amount * n)",
    solution='''def countSequences(coins, amount):
    MOD = 1000000007
    n = len(coins)
    total = [0] * (amount + 1)
    total[0] = 1
    end = [[0] * n for _ in range(amount + 1)]
    for s in range(1, amount + 1):
        acc = 0
        row = end[s]
        for j in range(n):
            c = coins[j]
            if c <= s:
                v = (total[s - c] - end[s - c][j]) % MOD
                row[j] = v
                acc += v
        total[s] = acc % MOD
    return total[amount]
''',
    tests=[[[1, 2, 3], 4], [[1, 2], 4], [[2], 4], [[1, 3], 5], [[2], 2], [[1], 1], [[1], 2], [[5], 3], [[1, 2], 1],
           [[1, 2, 3], 10], [[2, 3], 12], [[1, 2, 3, 4, 5], 20]],
)
_r = rnd(8109)
p["tests"].append([_r.sample(range(1, 1001), 50), 3000])
p["tests"].append([list(range(1, 51)), 3000])
p["tests"].append([[1, 2], 3000])
p["tests"].append([_r.sample(range(1, 30), 20), 2999])


def b_sequences(coins, amount):
    def go(rem, last):
        if rem == 0:
            return 1
        total = 0
        for c in coins:
            if c != last and c <= rem:
                total += go(rem - c, c)
        return total

    return go(amount, None) % MOD


def g_sequences(r):
    return [r.sample(range(1, 7), r.randint(1, 4)), r.randint(1, 14)]


def v_sequences(tests):
    for t in tests:
        coins, amount = t["args"]
        assert 1 <= len(coins) <= 50 and distinct(coins) and all(1 <= c <= 1000 for c in coins)
        assert 1 <= amount <= 3000 and 0 <= t["expected"] < MOD


CHECKS["coin-sequences-no-adjacent-repeat"] = (b_sequences, g_sequences, "exact")
VALIDATE["coin-sequences-no-adjacent-repeat"] = v_sequences
