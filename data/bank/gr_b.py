"""Problems: greedy on arrays (stock variants, jump and reach problems, gas station, fixing sequences). See data/lib.py for the registry."""
from itertools import combinations

from lib import add, rnd, CHECKS, VALIDATE, gen_arr  # noqa: F401

INT_MIN, INT_MAX = -(2 ** 31), 2 ** 31 - 1


# ---------------------------------------------------------------- EASY

p = add(
    id="dup-stock-single-trade", title="Best Time to Buy and Sell Stock", diff="Easy", topic="Greedy", tier="must",
    fn="maxProfit", params=[("prices", "int[]")], ret="int", cmp="exact",
    desc="<p>The array <code>prices</code> holds the price of one stock on consecutive days: <code>prices[i]</code> is the price on day <code>i</code>.</p><p>You may complete at most one transaction: buy the stock on one day and sell it on a <em>later</em> day. Return the maximum profit you can make. If no transaction can make a profit, return <code>0</code>.</p><pre>[7, 1, 5, 3, 6, 4] -> 5   (buy at 1, sell at 6)\n[7, 6, 4, 3, 1]    -> 0   (prices only fall)</pre>",
    constraints=["1 &le; prices.length &le; 10,000", "0 &le; prices[i] &le; 10<sup>9</sup>"],
    hints=["Trying every pair of days (buy day, later sell day) is correct but needs O(n<sup>2</sup>) time.",
           "Fix the selling day. Which buying day is best for it? Only the days before it matter.",
           "Scan left to right keeping the lowest price seen so far. On every day, the best profit if you sell today is <code>price - lowest</code>; keep the maximum of these values (and start from 0)."],
    editorial=["For a fixed selling day the best buying day is the cheapest day before it. So one pass is enough: maintain <code>low</code>, the minimum price among earlier days, and <code>best</code>, the best profit found so far. On each day update <code>best = max(best, price - low)</code> and then <code>low = min(low, price)</code>.",
               "Starting <code>best</code> at 0 handles the case where prices never rise. The algorithm is greedy because the choice 'cheapest earlier day' never needs to be revisited. Time is O(n) and only two variables are stored."],
    time="O(n)", space="O(1)",
    solution='''def maxProfit(prices):
    low = prices[0]
    best = 0
    for x in prices:
        if x < low:
            low = x
        elif x - low > best:
            best = x - low
    return best
''',
    tests=[[[7, 1, 5, 3, 6, 4]], [[7, 6, 4, 3, 1]], [[5]], [[1, 2]], [[2, 1]], [[3, 3, 3]], [[0, 1000000000]],
           [[1000000000, 0, 1000000000]], [[2, 4, 1]], [[3, 2, 6, 5, 0, 3]], [[0, 0, 0, 5, 0]]],
)
_r = rnd(3101)
_a = [5 * 10 ** 8]
for _ in range(3999):
    _a.append(min(10 ** 9, max(0, _a[-1] + _r.randint(-10 ** 7, 10 ** 7))))
p["tests"].append([_a])
p["tests"].append([[10 ** 9 - i * 300000 for i in range(3000)]])
p["tests"].append([[_r.randint(0, 10 ** 9) for _ in range(3500)]])


def b_stock1(prices):
    best = 0
    for i in range(len(prices)):
        for j in range(i + 1, len(prices)):
            best = max(best, prices[j] - prices[i])
    return best


def v_stock1(tests):
    for t in tests:
        a = t["args"][0]
        assert 1 <= len(a) <= 10000 and all(0 <= x <= 10 ** 9 for x in a)


CHECKS["dup-stock-single-trade"] = (b_stock1, lambda r: [gen_arr(r, 0, 10, 1, 9)], "exact")
VALIDATE["dup-stock-single-trade"] = v_stock1


p = add(
    id="min-increments-strictly-increasing", title="Minimum Increments to Strictly Increasing", diff="Easy", topic="Greedy",
    fn="minOperations", params=[("nums", "int[]")], ret="int", cmp="exact",
    desc="<p>In one operation you may pick any element of <code>nums</code> and add <code>1</code> to it. Elements can only be increased, never decreased.</p><p>Return the minimum number of operations needed to make <code>nums</code> <em>strictly</em> increasing, that is <code>nums[0] &lt; nums[1] &lt; ... &lt; nums[n-1]</code>. An array with one element is already strictly increasing.</p><pre>[1, 1, 1]       -> 3   ([1, 2, 3])\n[1, 5, 2, 4, 1] -> 14  ([1, 5, 6, 7, 8])</pre>",
    constraints=["1 &le; nums.length &le; 10,000", "1 &le; nums[i] &le; 100,000"],
    hints=["Work from left to right. Whatever you do to nums[i], nums[i-1] has already been fixed.",
           "Each element only needs to be one more than its (already fixed) left neighbour, and never larger than necessary. Why is raising it more than that pointless?",
           "Keep the final value <code>prev</code> of the previous element. If <code>nums[i] &gt; prev</code> leave it, otherwise raise it to <code>prev + 1</code> and add the difference to the answer."],
    editorial=["Process the array from left to right and keep <code>prev</code>, the final value of the previous element. If the current value already exceeds <code>prev</code> nothing is needed. Otherwise it must be raised to at least <code>prev + 1</code>, and raising it to exactly that value is optimal: a higher value costs more now and only makes the next element's job harder.",
               "The cost of the step is <code>prev + 1 - nums[i]</code>. Summing these costs gives the answer. One pass, O(n) time and O(1) memory. The answer can reach about 10<sup>9</sup> for the largest inputs, which still fits in a 32-bit integer."],
    time="O(n)", space="O(1)",
    solution='''def minOperations(nums):
    ops = 0
    prev = nums[0]
    for x in nums[1:]:
        if x <= prev:
            prev += 1
            ops += prev - x
        else:
            prev = x
    return ops
''',
    tests=[[[1, 1, 1]], [[1, 5, 2, 4, 1]], [[8]], [[1, 2, 3]], [[5, 4, 3, 2, 1]], [[2, 2]], [[100000, 1]],
           [[1, 100000, 1, 100000]], [[3, 1, 4, 1, 5, 9, 2, 6]], [[7, 7, 7, 7, 7, 7, 7]]],
)
_r = rnd(3102)
p["tests"].append([[_r.randint(1, 100000) for _ in range(5000)]])
p["tests"].append([[100000] * 3 + [1] * 2000 + [100000 - (i % 7) for i in range(2000)]])
p["tests"].append([sorted(_r.randint(1, 100000) for _ in range(4000))[::-1]])


def b_mininc(nums):
    n = len(nums)
    hi = max(nums) + n
    INF = float("inf")
    dp = {v: v - nums[0] for v in range(nums[0], hi + 1)}
    for i in range(1, n):
        nd = {}
        for v in range(nums[i], hi + 1):
            best = min((c for u, c in dp.items() if u < v), default=INF)
            if best < INF:
                nd[v] = best + v - nums[i]
        dp = nd
    return min(dp.values())


def v_mininc(tests):
    for t in tests:
        a = t["args"][0]
        assert 1 <= len(a) <= 10000 and all(1 <= x <= 100000 for x in a)


CHECKS["min-increments-strictly-increasing"] = (b_mininc, lambda r: [gen_arr(r, 1, 6, 1, 6)], "exact")
VALIDATE["min-increments-strictly-increasing"] = v_mininc


p = add(
    id="min-initial-fuel-for-circuit", title="Minimum Starting Fuel for a Circuit", diff="Easy", topic="Greedy", tier="extra",
    fn="minInitialFuel", params=[("gas", "int[]"), ("cost", "int[]")], ret="int", cmp="exact",
    desc="<p>There are <code>n</code> fuel stations on a circular road, numbered <code>0</code> to <code>n-1</code>. Station <code>i</code> gives <code>gas[i]</code> units of fuel when you reach it, and driving from station <code>i</code> to station <code>(i + 1) % n</code> burns <code>cost[i]</code> units.</p><p>Your car starts at station <code>0</code> with <code>x</code> units of fuel already in the tank (you collect <code>gas[0]</code> as soon as you are there). You drive once around the circle and must return to station <code>0</code>. The tank may never go below zero, including at the moment you arrive at a station <em>before</em> collecting its fuel.</p><p>Return the smallest integer <code>x &ge; 0</code> that lets you complete the circuit.</p><pre>gas = [1, 2, 3, 4, 5], cost = [3, 4, 5, 1, 2] -> 6\ngas = [5, 1], cost = [1, 2]                   -> 0</pre>",
    constraints=["1 &le; n &le; 10,000", "gas.length == cost.length == n", "0 &le; gas[i], cost[i] &le; 10,000"],
    hints=["Simulate with a starting amount x and check whether the tank ever goes negative. Then think about how x relates to the worst moment of the trip.",
           "Ignore the starting amount for a moment and look at the running balance after each leg: the sum of <code>gas[k] - cost[k]</code> for the legs driven so far.",
           "The tank after leg <code>k</code> is <code>x + balance[k]</code>, so you need <code>x &ge; -balance[k]</code> for every k. The answer is the largest such deficit, or 0 if the balance never drops below 0."],
    editorial=["Let <code>balance[k]</code> be the total of <code>gas[i] - cost[i]</code> over the first <code>k+1</code> legs. After finishing leg <code>k</code> the tank holds <code>x + balance[k]</code>. The trip is feasible exactly when this is non-negative for every <code>k</code>, so the smallest valid <code>x</code> is <code>max(0, -min(balance))</code>.",
               "There is no search to do: a single pass that keeps the running balance and its minimum is enough. Starting with more fuel than the worst deficit never helps, which is the greedy part. O(n) time, O(1) space."],
    time="O(n)", space="O(1)",
    solution='''def minInitialFuel(gas, cost):
    balance = 0
    worst = 0
    for g, c in zip(gas, cost):
        balance += g - c
        if balance < worst:
            worst = balance
    return -worst
''',
    tests=[[[1, 2, 3, 4, 5], [3, 4, 5, 1, 2]], [[5, 1], [1, 2]], [[0], [0]], [[0], [7]], [[7], [0]], [[3], [3]],
           [[2, 2, 2], [2, 2, 2]], [[0, 0, 10], [4, 4, 4]], [[10, 0, 0], [4, 4, 4]], [[1, 1, 1, 1], [9, 0, 0, 0]],
           [[10000, 0], [0, 10000]]],
)
_r = rnd(3103)
p["tests"].append([[_r.randint(0, 10000) for _ in range(3000)], [_r.randint(0, 10000) for _ in range(3000)]])
p["tests"].append([[0] * 6999 + [10000], [10000] * 7000])
p["tests"].append([[10000] * 4000, [_r.randint(9000, 10000) for _ in range(4000)]])


def b_minfuel(gas, cost):
    n = len(gas)
    x = 0
    while True:
        tank = x
        ok = True
        for i in range(n):
            tank += gas[i]
            tank -= cost[i]
            if tank < 0:
                ok = False
                break
        if ok:
            return x
        x += 1


def g_minfuel(r):
    n = r.randint(1, 7)
    return [[r.randint(0, 6) for _ in range(n)], [r.randint(0, 6) for _ in range(n)]]


def v_minfuel(tests):
    for t in tests:
        gas, cost = t["args"]
        assert len(gas) == len(cost) and 1 <= len(gas) <= 10000
        assert all(0 <= x <= 10000 for x in gas + cost)


CHECKS["min-initial-fuel-for-circuit"] = (b_minfuel, g_minfuel, "exact")
VALIDATE["min-initial-fuel-for-circuit"] = v_minfuel


# ---------------------------------------------------------------- MEDIUM

p = add(
    id="non-decreasing-after-one-change", title="Non-decreasing After One Change", diff="Medium", topic="Greedy",
    fn="checkPossibility", params=[("nums", "int[]")], ret="bool", cmp="exact",
    desc="<p>You are allowed to replace <strong>at most one</strong> element of <code>nums</code> by any integer value of your choice. Return <code>true</code> if the array can be made non-decreasing this way, meaning <code>nums[i] &le; nums[i+1]</code> for every valid <code>i</code>. Otherwise return <code>false</code>.</p><pre>[4, 2, 3]    -> true   (change 4 to 1, or 2 to 4)\n[4, 2, 1]    -> false\n[3, 4, 2, 3] -> false</pre>",
    constraints=["1 &le; nums.length &le; 10,000", "-2<sup>31</sup> &le; nums[i] &le; 2<sup>31</sup> - 1"],
    hints=["If the array has two or more separate places where <code>nums[i] &gt; nums[i+1]</code> that cannot be fixed by one change, the answer is false. Start by finding the first such place.",
           "At a drop <code>nums[i-1] &gt; nums[i]</code> you have two options: lower <code>nums[i-1]</code> or raise <code>nums[i]</code>. Which one is safe depends on <code>nums[i-2]</code>.",
           "If <code>nums[i-2] &gt; nums[i]</code> you cannot lower <code>nums[i-1]</code> to <code>nums[i]</code> (it would fall below <code>nums[i-2]</code>), so raise <code>nums[i]</code> to <code>nums[i-1]</code>. Otherwise lower <code>nums[i-1]</code> to <code>nums[i]</code>, which keeps the future as small as possible. A second drop after using the change means false."],
    editorial=["Scan from left to right. When you meet a drop <code>nums[i-1] &gt; nums[i]</code>, the one allowed change must repair it, and there are only two sensible repairs: set <code>nums[i-1] = nums[i]</code> or set <code>nums[i] = nums[i-1]</code>.",
               "Lowering <code>nums[i-1]</code> is only legal when it stays at least <code>nums[i-2]</code>, i.e. when <code>i &lt; 2</code> or <code>nums[i-2] &le; nums[i]</code>. It is also the better choice, because it leaves the smaller value behind for later comparisons. If that is not legal, raise <code>nums[i]</code> to <code>nums[i-1]</code> (the smallest value that fixes the drop). Count the repairs; a second drop means the answer is false.",
               "The array is modified on a copy while scanning, so later comparisons see the repaired value. Single pass, O(n) time, O(n) for the copy (or O(1) if you restore the value)."],
    time="O(n)", space="O(n)",
    solution='''def checkPossibility(nums):
    a = list(nums)
    used = False
    for i in range(1, len(a)):
        if a[i - 1] > a[i]:
            if used:
                return False
            used = True
            if i >= 2 and a[i - 2] > a[i]:
                a[i] = a[i - 1]
            else:
                a[i - 1] = a[i]
    return True
''',
    tests=[[[4, 2, 3]], [[4, 2, 1]], [[3, 4, 2, 3]], [[1]], [[2, 1]], [[1, 2, 3]], [[5, 7, 1, 8]], [[2, 3, 3, 2, 4]],
           [[1, 1, 1]], [[-1, 4, 2, 3]], [[3, 3, 2, 2]], [[INT_MAX, INT_MIN]], [[INT_MIN, INT_MAX, INT_MIN, INT_MAX]],
           [[1, 4, 1, 2]], [[1, 5, 2, 3, 4]]],
)
_r = rnd(3104)
_a = sorted(_r.randint(-10 ** 9, 10 ** 9) for _ in range(3500)); _a[1750] = _a[1749] - 5
p["tests"].append([_a])
_a = sorted(_r.randint(-10 ** 9, 10 ** 9) for _ in range(3500)); _a[500] = INT_MAX; _a[2500] = INT_MIN
p["tests"].append([_a])
_a = sorted(_r.randint(0, 10 ** 6) for _ in range(4000)); _a[0] = INT_MAX
p["tests"].append([_a])


def b_nondec(nums):
    n = len(nums)

    def ok(a):
        return all(a[i] <= a[i + 1] for i in range(len(a) - 1))

    if ok(nums):
        return True
    cands = set(nums)
    for i in range(n):
        for v in cands:
            b = list(nums)
            b[i] = v
            if ok(b):
                return True
    return False


def v_nondec(tests):
    for t in tests:
        a = t["args"][0]
        assert 1 <= len(a) <= 10000 and all(INT_MIN <= x <= INT_MAX for x in a)
    assert any(t["expected"] for t in tests) and any(not t["expected"] for t in tests)


CHECKS["non-decreasing-after-one-change"] = (b_nondec, lambda r: [gen_arr(r, -4, 4, 1, 8)], "exact")
VALIDATE["non-decreasing-after-one-change"] = v_nondec


p = add(
    id="stock-profit-with-transaction-fee", title="Stock Profit With Transaction Fee", diff="Medium", topic="Greedy",
    fn="maxProfitWithFee", params=[("prices", "int[]"), ("fee", "int")], ret="int", cmp="exact",
    desc="<p><code>prices[i]</code> is the price of a stock on day <code>i</code>. You can make as many transactions as you like, where a transaction is one buy followed by one later sell. You may hold at most one share at any time, but you may sell and buy again on the same day.</p><p>Every transaction costs a fixed <code>fee</code>, paid once per completed buy-and-sell pair. Return the maximum total profit after fees. You are never forced to trade, so the answer is at least 0.</p><pre>prices = [1, 3, 2, 8, 4, 9], fee = 2 -> 8\nprices = [1, 3, 7, 5, 10, 3], fee = 3 -> 6</pre><p>In the first example buy at 1 and sell at 8 (profit 7 - 2), then buy at 4 and sell at 9 (profit 5 - 2).</p>",
    constraints=["1 &le; prices.length &le; 10,000", "1 &le; prices[i] &le; 50,000", "0 &le; fee &le; 50,000"],
    hints=["Without a fee you would collect every rise. The fee makes tiny rises worthless and makes it costly to close and reopen a position.",
           "At any time you are either holding a share or not. Track the best profit for each of the two states.",
           "<code>cash = max(cash, hold + price - fee)</code> (sell today) and <code>hold = max(hold, cash - price)</code> (buy today). Update cash first, then hold, and return cash at the end."],
    editorial=["Keep two numbers: <code>cash</code>, the best profit while holding nothing, and <code>hold</code>, the best profit while holding a share (the price already paid is subtracted). Starting values are <code>cash = 0</code> and <code>hold = -prices[0]</code>.",
               "For each later price, selling today gives <code>hold + price - fee</code> and buying today gives <code>cash - price</code>. Take the better of 'do nothing' and 'act' for both states. Charging the fee at the sell is equivalent to charging it at the buy, as every sold share was bought exactly once.",
               "The greedy view: a position is only closed when the price has dropped by more than the fee from the best level seen, which is exactly what the two-state update decides implicitly. One pass, O(n) time, O(1) space."],
    time="O(n)", space="O(1)",
    solution='''def maxProfitWithFee(prices, fee):
    cash = 0
    hold = -prices[0]
    for x in prices[1:]:
        cash = max(cash, hold + x - fee)
        hold = max(hold, cash - x)
    return cash
''',
    tests=[[[1, 3, 2, 8, 4, 9], 2], [[1, 3, 7, 5, 10, 3], 3], [[5], 1], [[1, 2], 0], [[1, 2], 1], [[1, 2], 2],
           [[10, 9, 8], 1], [[1, 5, 1, 5, 1, 5], 0], [[1, 5, 1, 5, 1, 5], 3], [[1, 5, 1, 5, 1, 5], 4],
           [[2, 1, 4, 4, 2, 3, 2, 5, 1, 2], 1], [[1, 50000], 49999], [[50000, 1, 50000, 1], 0]],
)
_r = rnd(3105)
_a = [25000]
for _ in range(5999):
    _a.append(min(50000, max(1, _a[-1] + _r.randint(-3000, 3000))))
p["tests"].append([_a, 4000])
p["tests"].append([[_r.randint(1, 50000) for _ in range(5000)], 0])
p["tests"].append([[_r.randint(1, 50000) for _ in range(5000)], 20000])


def b_fee(prices, fee):
    n = len(prices)

    def go(i):
        if i >= n:
            return 0
        best = go(i + 1)
        for j in range(i + 1, n):
            best = max(best, prices[j] - prices[i] - fee + go(j))
        return best

    return go(0)


def g_fee(r):
    return [gen_arr(r, 1, 10, 1, 8), r.randint(0, 6)]


def v_fee(tests):
    for t in tests:
        a, fee = t["args"]
        assert 1 <= len(a) <= 10000 and all(1 <= x <= 50000 for x in a) and 0 <= fee <= 50000
        assert t["expected"] >= 0


CHECKS["stock-profit-with-transaction-fee"] = (b_fee, g_fee, "exact")
VALIDATE["stock-profit-with-transaction-fee"] = v_fee


p = add(
    id="stock-max-profit-fewest-trades", title="Stock Max Profit With Fewest Trades", diff="Medium", topic="Greedy", tier="extra",
    fn="maxProfitFewestTrades", params=[("prices", "int[]")], ret="int[]", cmp="exact",
    desc="<p><code>prices[i]</code> is the price of a stock on day <code>i</code>. You may make any number of trades; a trade is a buy on some day followed by a sell on a strictly later day. You hold at most one share at a time, and each day you may do at most one action (buy or sell), so the next buy is on a day strictly after the previous sell.</p><p>Among all plans that reach the <strong>maximum possible total profit</strong>, find the smallest number of trades. Return the two-element array <code>[maxProfit, fewestTrades]</code>. If no profit is possible, the answer is <code>[0, 0]</code>.</p><pre>[1, 2, 3, 2, 5, 5, 4] -> [5, 2]   (buy 1 sell 3, buy 2 sell 5)\n[3, 2, 1]             -> [0, 0]\n[1, 3, 2, 4]          -> [4, 2]   (buy 1 sell 3, buy 2 sell 4)</pre>",
    constraints=["1 &le; prices.length &le; 10,000", "0 &le; prices[i] &le; 100,000"],
    hints=["The maximum profit is easy: look at consecutive day differences. How much of each difference can you keep?",
           "A trade that includes a falling day (next price lower than today's) loses money compared to splitting it at that fall. So an optimal trade never spans a drop.",
           "Cut the price line at every drop <code>prices[i] &gt; prices[i+1]</code>. Every resulting piece that contains at least one rise is exactly one trade (buy at its start, sell at its end). Count those pieces and add up the rises."],
    editorial=["Let <code>d[i] = prices[i+1] - prices[i]</code>. The maximum profit is the sum of all positive <code>d[i]</code>: it is an upper bound, and buying before each rise and selling after it achieves it. To hit this value, no trade may include a negative <code>d[i]</code>, and every positive one must be covered.",
               "A trade is a block of consecutive differences. Flat steps (<code>d = 0</code>) are harmless, so a block may include them, and neighbouring rises can be merged into a single longer trade. The blocks are therefore separated exactly by the negative differences. Between two drops, the days form a non-decreasing stretch; it needs one trade if it contains at least one rise and none otherwise.",
               "So scan once, add up the positive differences, and count the number of times a rise starts a new stretch (the previous difference was negative, or it is the first difference, and zero-differences before the first rise do not matter). O(n) time and O(1) space."],
    time="O(n)", space="O(1)",
    solution='''def maxProfitFewestTrades(prices):
    profit = 0
    trades = 0
    in_trade = False
    for i in range(1, len(prices)):
        d = prices[i] - prices[i - 1]
        if d < 0:
            in_trade = False
        elif d > 0:
            profit += d
            if not in_trade:
                trades += 1
                in_trade = True
    return [profit, trades]
''',
    tests=[[[1, 2, 3, 2, 5, 5, 4]], [[3, 2, 1]], [[1, 3, 2, 4]], [[5]], [[1, 1, 1]], [[1, 2]], [[2, 1]], [[0, 0, 5, 5, 5, 0]],
           [[1, 2, 2, 3]], [[1, 2, 2, 1, 1, 2]], [[100000, 0, 100000, 0, 100000]], [[4, 4, 5, 5, 3, 3, 3, 6]]],
)
_r = rnd(3106)
p["tests"].append([[_r.randint(0, 100000) for _ in range(4000)]])
_a = [50000]
for _ in range(5999):
    _a.append(min(100000, max(0, _a[-1] + _r.choice([-2, -1, 0, 0, 1, 2, 3]))))
p["tests"].append([_a])
p["tests"].append([[(i // 3) * 10 for i in range(4000)]])


def b_fewest(prices):
    n = len(prices)
    best = (0, 0)
    for size in range(0, n + 1, 2):
        for days in combinations(range(n), size):
            profit = sum(prices[days[k + 1]] - prices[days[k]] for k in range(0, size, 2))
            cand = (profit, -(size // 2))
            if cand > (best[0], -best[1]):
                best = (profit, size // 2)
    return [best[0], best[1]]


def v_fewest(tests):
    for t in tests:
        a = t["args"][0]
        assert 1 <= len(a) <= 10000 and all(0 <= x <= 100000 for x in a)
        assert len(t["expected"]) == 2


CHECKS["stock-max-profit-fewest-trades"] = (b_fewest, lambda r: [gen_arr(r, 0, 5, 1, 9)], "exact")
VALIDATE["stock-max-profit-fewest-trades"] = v_fewest


p = add(
    id="gas-station-count-valid-starts", title="Gas Station: Count Valid Starts", diff="Medium", topic="Greedy", tier="extra",
    fn="countValidStarts", params=[("gas", "int[]"), ("cost", "int[]")], ret="int", cmp="exact",
    desc="<p>There are <code>n</code> fuel stations on a circular road. Station <code>i</code> gives <code>gas[i]</code> units of fuel when you reach it, and driving from station <code>i</code> to station <code>(i + 1) % n</code> burns <code>cost[i]</code> units. You drive clockwise only.</p><p>Choose a starting station, begin with an empty tank, collect its fuel and drive. The start is <em>valid</em> if you can return to it after a full circle without the tank ever becoming negative.</p><p>Return the <strong>number</strong> of valid starting stations (possibly 0).</p><pre>gas = [1, 2, 3, 4, 5], cost = [3, 4, 5, 1, 2] -> 1   (only station 3)\ngas = [2, 2, 2], cost = [2, 2, 2]             -> 3\ngas = [2, 3, 4], cost = [3, 4, 3]             -> 0</pre>",
    constraints=["1 &le; n &le; 10,000", "gas.length == cost.length == n", "0 &le; gas[i], cost[i] &le; 10,000"],
    hints=["Simulating from every start works in O(n<sup>2</sup>). Write the trip as prefix sums of <code>d[i] = gas[i] - cost[i]</code> to see what 'valid' means.",
           "Start <code>s</code> is valid exactly when every prefix sum of <code>d</code> taken from <code>s</code> (one full lap) is non-negative. With the circle unrolled to length 2n and prefix array P, that is: <code>min(P[s+1..s+n]) &ge; P[s]</code>.",
           "You need the minimum of every window of n consecutive prefix values. A monotonic deque gives all of these in O(n) total."],
    editorial=["Let <code>d[i] = gas[i] - cost[i]</code> and double the array so the circle becomes a line of length 2n. Define <code>P[0] = 0</code> and <code>P[j+1] = P[j] + d[j % n]</code>. Starting at station <code>s</code>, the tank after the k-th leg is <code>P[s+k] - P[s]</code>. The start is valid when this is at least 0 for k = 1..n.",
               "So for each s we need the minimum of the window <code>P[s+1..s+n]</code> and compare it with <code>P[s]</code>. These windows slide by one, so a monotonic deque (indices with increasing P values) gives each window minimum in amortised O(1). Count the starts that pass.",
               "This also contains the classic single-answer problem: if the total sum is negative nothing passes, and the valid starts are exactly the stations right after the position where the unrolled prefix sum is at its minimum (and ties). Time O(n), space O(n)."],
    time="O(n)", space="O(n)",
    solution='''from collections import deque


def countValidStarts(gas, cost):
    n = len(gas)
    P = [0] * (2 * n + 1)
    for j in range(2 * n):
        P[j + 1] = P[j] + gas[j % n] - cost[j % n]
    dq = deque()
    count = 0
    for j in range(1, 2 * n + 1):
        while dq and P[dq[-1]] >= P[j]:
            dq.pop()
        dq.append(j)
        s = j - n
        if 0 <= s < n:
            while dq[0] < s + 1:
                dq.popleft()
            if P[dq[0]] >= P[s]:
                count += 1
    return count
''',
    tests=[[[1, 2, 3, 4, 5], [3, 4, 5, 1, 2]], [[2, 2, 2], [2, 2, 2]], [[2, 3, 4], [3, 4, 3]], [[5], [4]], [[4], [5]],
           [[0], [0]], [[3, 1, 1], [1, 2, 2]], [[1, 1, 1, 1], [2, 0, 0, 0]], [[0, 0, 0], [0, 0, 0]],
           [[5, 0, 0, 5], [2, 4, 3, 1]], [[10000, 10000], [10000, 10000]], [[0, 3, 0, 3], [1, 1, 1, 1]]],
)
_r = rnd(3107)
_n = 2500
_g = [_r.randint(100, 9000) for _ in range(_n)]
p["tests"].append([_g, list(_g)])
_c = list(_g)
for _ in range(1500):
    _i, _j = _r.randrange(_n), _r.randrange(_n)
    _t = _r.randint(0, 40)
    if _c[_i] + _t <= 10000 and _c[_j] - _t >= 0:
        _c[_i] += _t; _c[_j] -= _t
p["tests"].append([_g, _c])
_g2 = [_r.randint(0, 10000) for _ in range(2500)]
_c2 = [max(0, x - _r.randint(0, 6)) for x in _g2]
p["tests"].append([_g2, _c2])


def b_starts(gas, cost):
    n = len(gas)
    cnt = 0
    for s in range(n):
        tank = 0
        ok = True
        for k in range(n):
            i = (s + k) % n
            tank += gas[i] - cost[i]
            if tank < 0:
                ok = False
                break
        cnt += ok
    return cnt


def g_starts(r):
    n = r.randint(1, 8)
    g = [r.randint(0, 5) for _ in range(n)]
    if r.random() < 0.5:
        c = [max(0, x + r.randint(-1, 1)) for x in g]
    else:
        c = [r.randint(0, 5) for _ in range(n)]
    return [g, c]


def v_starts(tests):
    for t in tests:
        gas, cost = t["args"]
        assert len(gas) == len(cost) and 1 <= len(gas) <= 10000
        assert all(0 <= x <= 10000 for x in gas + cost)
    assert any(t["expected"] > 1 for t in tests) and any(t["expected"] == 0 for t in tests)


CHECKS["gas-station-count-valid-starts"] = (b_starts, g_starts, "exact")
VALIDATE["gas-station-count-valid-starts"] = v_starts


p = add(
    id="jump-game-good-start-count", title="Jump Game: Count Good Starting Indices", diff="Medium", topic="Greedy",
    fn="countGoodStarts", params=[("nums", "int[]")], ret="int", cmp="exact",
    desc="<p>In the array <code>nums</code>, <code>nums[i]</code> is the maximum jump length from index <code>i</code>: from <code>i</code> you may jump to any index <code>j</code> with <code>i &lt; j &le; i + nums[i]</code> (and <code>j</code> inside the array). An index with <code>nums[i] = 0</code> cannot move at all.</p><p>Call an index <em>good</em> if you can reach the <strong>last</strong> index by starting there and jumping zero or more times. The last index is always good. Return the number of good indices.</p><pre>[2, 3, 1, 1, 4] -> 5\n[3, 2, 1, 0, 4] -> 1\n[1, 0, 2, 0]    -> 2   (indices 2 and 3)</pre>",
    constraints=["1 &le; nums.length &le; 10,000", "0 &le; nums[i] &le; 100,000"],
    hints=["The classic 'can I reach the end from index 0' question is solved greedily. Here you must answer it for every starting index, so process the array in a smart order.",
           "Go from right to left. An index is good if it can jump onto some index that is already known to be good.",
           "Keep <code>g</code>, the smallest good index found so far. Any good index in the range of <code>i</code> is at least <code>g</code>, so <code>i</code> is good exactly when <code>i + nums[i] &ge; g</code>. Then <code>g</code> becomes <code>i</code>."],
    editorial=["Scan from the right and remember <code>g</code>, the leftmost index known to be good (initially the last index). For an index <code>i</code> to be good it must be able to land on a good index in <code>(i, i + nums[i]]</code>. All good indices to the right are at least <code>g</code>, so if any of them is reachable, then <code>g</code> itself is reachable (it is the closest one and the reach is a contiguous range starting at <code>i + 1</code>). Hence <code>i</code> is good if and only if <code>i + nums[i] &ge; g</code>.",
               "When <code>i</code> is good, set <code>g = i</code> and increase the counter. Indices that are bad leave <code>g</code> unchanged. One right-to-left pass, O(n) time, O(1) space. This is the standard 'jump game' greedy turned into a counting version."],
    time="O(n)", space="O(1)",
    solution='''def countGoodStarts(nums):
    n = len(nums)
    g = n - 1
    count = 1
    for i in range(n - 2, -1, -1):
        if i + nums[i] >= g:
            g = i
            count += 1
    return count
''',
    tests=[[[2, 3, 1, 1, 4]], [[3, 2, 1, 0, 4]], [[1, 0, 2, 0]], [[0]], [[5]], [[0, 0]], [[1, 1]], [[1, 0, 0, 0]],
           [[0, 2, 0, 1, 0, 3, 0]], [[3, 0, 0, 0, 1, 0, 1]], [[100000, 0, 0, 0]], [[1, 1, 1, 1, 1, 1, 1, 1]]],
)
_r = rnd(3108)
p["tests"].append([[_r.choice([0, 0, 1, 1, 2, 3, 5]) for _ in range(8000)]])
p["tests"].append([[_r.choice([0, 1]) for _ in range(7000)]])
p["tests"].append([[1] * 5000 + [0] + [_r.randint(0, 100000) for _ in range(2000)]])


def b_goodstarts(nums):
    n = len(nums)
    cnt = 0
    for s in range(n):
        seen = {s}
        stack = [s]
        while stack:
            i = stack.pop()
            for j in range(i + 1, min(n - 1, i + nums[i]) + 1):
                if j not in seen:
                    seen.add(j)
                    stack.append(j)
        cnt += (n - 1) in seen
    return cnt


def g_goodstarts(r):
    return [[r.choice([0, 0, 1, 1, 2, 3]) for _ in range(r.randint(1, 10))]]


def v_goodstarts(tests):
    for t in tests:
        a = t["args"][0]
        assert 1 <= len(a) <= 10000 and all(0 <= x <= 100000 for x in a)
        assert 1 <= t["expected"] <= len(a)


CHECKS["jump-game-good-start-count"] = (b_goodstarts, g_goodstarts, "exact")
VALIDATE["jump-game-good-start-count"] = v_goodstarts


p = add(
    id="farthest-index-after-k-jumps", title="Farthest Index After K Jumps", diff="Medium", topic="Greedy", tier="extra",
    fn="farthestAfterJumps", params=[("nums", "int[]"), ("k", "int")], ret="int", cmp="exact",
    desc="<p>You stand at index <code>0</code> of <code>nums</code>. From index <code>i</code> one jump takes you to any index <code>j</code> with <code>i &lt; j &le; i + nums[i]</code>, as long as <code>j</code> is inside the array. You may make at most <code>k</code> jumps (possibly none).</p><p>Return the largest index you can stand on after at most <code>k</code> jumps.</p><pre>nums = [2, 3, 1, 1, 4], k = 1 -> 2\nnums = [2, 3, 1, 1, 4], k = 2 -> 4   (0 -> 1 -> 4)\nnums = [1, 0, 5], k = 9       -> 1   (stuck at index 1)</pre>",
    constraints=["1 &le; nums.length &le; 10,000", "0 &le; nums[i] &le; 100,000", "0 &le; k &le; 10<sup>9</sup>"],
    hints=["After j jumps, the set of indices you can stand on is easy to describe. Is it a contiguous range?",
           "Yes: after j jumps every index from 0 to some <code>reach_j</code> can be reached with at most j jumps (a jump may be shorter than allowed). So you only need to track one number.",
           "<code>reach_{j+1} = max(i + nums[i])</code> over all <code>i &le; reach_j</code>, capped at n-1. Stop early when it no longer grows, so a huge k costs nothing; scan each index only once."],
    editorial=["Let <code>reach_j</code> be the farthest index reachable with at most j jumps. Because a jump can be any length up to the maximum, everything between 0 and <code>reach_j</code> is reachable too, so the reachable set is the prefix <code>[0, reach_j]</code>. The next frontier is the best landing of any index in that prefix: <code>reach_{j+1} = min(n-1, max(i + nums[i]))</code> for <code>i</code> in the prefix.",
               "Run this for at most k rounds. To keep it linear, remember how far the scan already got, so each index is looked at once overall. If a round does not extend the reach, nothing will ever change again and you can stop; this also bounds the number of rounds by n even when k is 10<sup>9</sup>.",
               "This is the layered-BFS view of the Jump Game II greedy, but it asks for the farthest position instead of the number of jumps. Time O(n), space O(1)."],
    time="O(n)", space="O(1)",
    solution='''def farthestAfterJumps(nums, k):
    n = len(nums)
    reach = 0
    i = 0
    for _ in range(k):
        nxt = reach
        while i <= reach:
            if i + nums[i] > nxt:
                nxt = i + nums[i]
            i += 1
        if nxt > n - 1:
            nxt = n - 1
        if nxt == reach:
            break
        reach = nxt
    return reach
''',
    tests=[[[2, 3, 1, 1, 4], 1], [[2, 3, 1, 1, 4], 2], [[1, 0, 5], 9], [[5], 3], [[3, 1], 0], [[3, 1, 1, 1, 1], 1],
           [[1, 1, 1, 1, 1], 3], [[1, 1, 1, 1, 1], 100], [[4, 0, 0, 0, 0, 0], 1], [[0, 9, 9], 5],
           [[2, 0, 2, 0, 2, 0, 2], 2], [[100000, 1], 1000000000]],
)
_r = rnd(3109)
p["tests"].append([[_r.randint(0, 4) for _ in range(8000)], 40])
p["tests"].append([[_r.choice([1, 1, 1, 2, 0]) for _ in range(8000)], 1000000000])
p["tests"].append([[1] * 6000, 2500])


def b_farthest(nums, k):
    n = len(nums)
    cur = {0}
    for _ in range(min(k, n)):
        nxt = set(cur)
        for i in cur:
            for j in range(i + 1, min(n - 1, i + nums[i]) + 1):
                nxt.add(j)
        cur = nxt
    return max(cur)


def g_farthest(r):
    return [[r.choice([0, 1, 1, 2, 3]) for _ in range(r.randint(1, 10))], r.randint(0, 6)]


def v_farthest(tests):
    for t in tests:
        a, k = t["args"]
        assert 1 <= len(a) <= 10000 and all(0 <= x <= 100000 for x in a) and 0 <= k <= 10 ** 9
        assert 0 <= t["expected"] < len(a)


CHECKS["farthest-index-after-k-jumps"] = (b_farthest, g_farthest, "exact")
VALIDATE["farthest-index-after-k-jumps"] = v_farthest


# ---------------------------------------------------------------- HARD

p = add(
    id="min-cost-to-make-array-non-decreasing", title="Minimum Cost to Make Array Non-Decreasing", diff="Hard", topic="Greedy", tier="extra",
    fn="minCostNonDecreasing", params=[("nums", "int[]")], ret="int", cmp="exact",
    desc="<p>In one operation you add <code>1</code> to or subtract <code>1</code> from any element of <code>nums</code>. Elements may become negative or exceed the original range.</p><p>Return the minimum number of operations needed to make <code>nums</code> non-decreasing (<code>nums[i] &le; nums[i+1]</code> for all valid <code>i</code>).</p><pre>[3, 1, 2]       -> 2   ([2, 2, 2] or [1, 1, 2])\n[5, 4, 3, 2, 1] -> 6   ([3, 3, 3, 3, 3])\n[1, 2, 3]       -> 0</pre>",
    constraints=["1 &le; nums.length &le; 10,000", "0 &le; nums[i] &le; 100,000"],
    hints=["Raising only or lowering only is not always best. Think about what the final array looks like and how it relates to the original values.",
           "A good final array only uses values that already occur in nums, and a simple left-to-right greedy with a heap can find the cost without trying all of them.",
           "Keep a max-heap of the values seen so far. For each x push x. If the heap top is larger than x, the prefix is out of order: add <code>top - x</code> to the answer, pop the top and push x again. The total at the end is the minimum cost."],
    editorial=["Sweep from left to right and keep a max-heap that stores, implicitly, the best non-decreasing 'target' values for the prefix. When the new value <code>x</code> is at least the largest stored value, the prefix stays sorted for free. Otherwise some earlier target has to come down to meet <code>x</code> or <code>x</code> has to go up; either way the cheapest fix costs <code>top - x</code> operations.",
               "Concretely: push <code>x</code>; if <code>heap.top &gt; x</code>, add <code>heap.top - x</code> to the cost, remove the top and push <code>x</code> a second time. The second push of <code>x</code> records that the removed target and the new element now share the level <code>x</code>. This is the 'slope trick' for L1 isotonic regression: the heap top is always the cheapest level that the current prefix can be lowered to.",
               "Each element causes O(1) heap operations, so the time is O(n log n) and the space is O(n). The answer is at most about 5 * 10<sup>8</sup> for these limits, so it fits in 32 bits."],
    time="O(n log n)", space="O(n)",
    solution='''import heapq


def minCostNonDecreasing(nums):
    heap = []
    cost = 0
    for x in nums:
        heapq.heappush(heap, -x)
        if -heap[0] > x:
            cost += -heap[0] - x
            heapq.heapreplace(heap, -x)
    return cost
''',
    tests=[[[3, 1, 2]], [[5, 4, 3, 2, 1]], [[1, 2, 3]], [[7]], [[2, 1]], [[0, 100000]], [[100000, 0]],
           [[1, 100000, 1, 100000, 1]], [[4, 4, 4]], [[1, 3, 2, 4, 3, 5]], [[10, 1, 10, 1, 10, 1]], [[2, 9, 1, 8, 0, 7]]],
)
_r = rnd(3110)
p["tests"].append([[_r.randint(0, 100000) for _ in range(5000)]])
p["tests"].append([[100000 - (i * 20) % 100000 for i in range(5000)]])
p["tests"].append([[(100000 if i % 2 else 0) for i in range(5000)]])


def b_costnd(nums):
    vals = sorted(set(nums))
    dp = {v: abs(nums[0] - v) for v in vals}
    for x in nums[1:]:
        best = float("inf")
        nd = {}
        for v in vals:
            best = min(best, dp[v])
            nd[v] = best + abs(x - v)
        dp = nd
    return min(dp.values())


def v_costnd(tests):
    for t in tests:
        a = t["args"][0]
        assert 1 <= len(a) <= 10000 and all(0 <= x <= 100000 for x in a)
        assert t["expected"] <= 10 ** 9
    assert any(t["expected"] > 0 for t in tests) and any(t["expected"] == 0 for t in tests)


CHECKS["min-cost-to-make-array-non-decreasing"] = (b_costnd, lambda r: [gen_arr(r, 0, 9, 1, 8)], "exact")
VALIDATE["min-cost-to-make-array-non-decreasing"] = v_costnd


p = add(
    id="splits-to-make-array-non-decreasing", title="Splits to Make Array Non-Decreasing", diff="Hard", topic="Greedy",
    fn="minSplits", params=[("nums", "int[]")], ret="int", cmp="exact",
    desc="<p>In one operation you pick an element of <code>nums</code> and replace it, in the same position, by two positive integers whose sum is that element. For example <code>[3, 9, 3]</code> may become <code>[3, 3, 6, 3]</code> by splitting 9 into 3 and 6 (you choose the order of the two new elements). New elements can be split again.</p><p>Return the minimum number of operations needed to make <code>nums</code> non-decreasing (<code>nums[i] &le; nums[i+1]</code> for all i).</p><pre>[3, 9, 3] -> 2   ([3, 3, 3, 3, 3])\n[1, 2, 3, 4, 5] -> 0\n[5, 4] -> 1   ([2, 3, 4])</pre><p>In the last example, 5 is split into 2 and 3 (one operation), giving [2, 3, 4].</p>",
    constraints=["1 &le; nums.length &le; 10,000", "1 &le; nums[i] &le; 100,000"],
    hints=["The last element never needs to change, since there is nothing to its right. Work backwards: what does each element have to be compared to?",
           "Every element must be broken into parts that are all at most the smallest part of the element to its right. You want as few parts as possible, and among those the smallest part as large as possible, since it becomes the limit for the element on the left.",
           "With <code>last</code> the minimum of the right neighbour after its splitting and value <code>x</code>: if <code>x &le; last</code> nothing to do (<code>last = x</code>). Otherwise use <code>k = ceil(x / last)</code> parts (cost <code>k - 1</code>) and split them as evenly as possible; the smallest part is <code>x // k</code>, which becomes the new <code>last</code>."],
    editorial=["Process the array from right to left and maintain <code>last</code>, the smallest value among the pieces of the element to the right (after splitting it). For the current value <code>x</code>: if <code>x &le; last</code> it is already fine, and <code>last</code> becomes <code>x</code>.",
               "Otherwise every piece of <code>x</code> must be at most <code>last</code>, so at least <code>k = ceil(x / last)</code> pieces are needed, costing <code>k - 1</code> operations. Using exactly <code>k</code> pieces, make them as equal as possible: the smallest piece is then <code>x // k</code>, the largest possible minimum for k pieces. Update <code>last = x // k</code>. (All pieces are at most <code>ceil(x / k) &le; last</code>.)",
               "The two greedy choices are justified together: fewer pieces never hurt later steps because a larger minimum gives the left neighbour more room, and splitting into more than k pieces only adds cost and lowers the minimum. Total work O(n) with O(1) extra memory. The answer is at most about 10<sup>9</sup>, so it fits in 32 bits."],
    time="O(n)", space="O(1)",
    solution='''def minSplits(nums):
    last = nums[-1]
    ops = 0
    for i in range(len(nums) - 2, -1, -1):
        x = nums[i]
        if x <= last:
            last = x
        else:
            k = (x + last - 1) // last
            ops += k - 1
            last = x // k
    return ops
''',
    tests=[[[3, 9, 3]], [[1, 2, 3, 4, 5]], [[5, 4]], [[7]], [[1]], [[2, 1]], [[100000, 1]], [[100000, 100000]],
           [[10, 3]], [[10, 4, 3]], [[7, 4, 9, 2]], [[6, 5, 4, 3, 2, 1]], [[1, 100000, 1, 100000, 1]]],
)
_r = rnd(3111)
p["tests"].append([[_r.randint(1, 100000) for _ in range(4000)]])
p["tests"].append([[100000] * 6000 + [1]])
p["tests"].append([sorted((_r.randint(1, 100000) for _ in range(4000)), reverse=True)])


def b_splits(nums):
    def partitions(x, maxpart, minpart=1):
        # non-decreasing tuples of positive integers summing to x, with every part <= maxpart
        if x == 0:
            yield ()
            return
        for first in range(minpart, min(x, maxpart) + 1):
            for rest in partitions(x - first, maxpart, first):
                yield (first,) + rest

    memo = {}

    def go(i, limit):
        if i < 0:
            return 0
        if (i, limit) in memo:
            return memo[(i, limit)]
        best = float("inf")
        for parts in partitions(nums[i], limit):
            best = min(best, len(parts) - 1 + go(i - 1, parts[0]))
        memo[(i, limit)] = best
        return best

    return go(len(nums) - 1, 10 ** 9)


def g_splits(r):
    return [[r.randint(1, 9) for _ in range(r.randint(1, 5))]]


def v_splits(tests):
    for t in tests:
        a = t["args"][0]
        assert 1 <= len(a) <= 10000 and all(1 <= x <= 100000 for x in a)
    assert any(t["expected"] > 0 for t in tests)


CHECKS["splits-to-make-array-non-decreasing"] = (b_splits, g_splits, "exact")
VALIDATE["splits-to-make-array-non-decreasing"] = v_splits
