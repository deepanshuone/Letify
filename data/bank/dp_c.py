"""Problems: dynamic programming, the stock-trading family (state machines). See data/lib.py for the registry."""
from functools import lru_cache

from lib import add, rnd, CHECKS, VALIDATE, gen_arr  # noqa: F401

TOPIC = "Dynamic Programming"
NEG = -10 ** 9


def _walk(r, n, start, lo, hi, step):
    """Random walk of n prices clamped to [lo, hi]."""
    a = [start]
    for _ in range(n - 1):
        a.append(min(hi, max(lo, a[-1] + r.randint(-step, step))))
    return a


def _prices(r, nmin=1, nmax=8, hi=9, lo=0):
    return [r.randint(lo, hi) for _ in range(r.randint(nmin, nmax))]


# ---------------------------------------------------------------- Best Time to Trade Stock III (at most two)

p = add(
    id="stock-profit-at-most-two-transactions", title="Stock Profit with At Most Two Transactions", diff="Hard", topic=TOPIC, tier="must",
    fn="maxProfitTwo", params=[("prices", "int[]")], ret="int", cmp="exact",
    desc="<p><code>prices[i]</code> is the price of a stock on day <code>i</code>. You may complete <strong>at most two</strong> transactions. A transaction is one purchase of a single share followed by a sale on a strictly later day. You can hold at most one share at a time, so the first sale must happen before the second purchase (selling and buying again on the same day is allowed).</p><p>Return the maximum total profit. If no profitable trade exists, return <code>0</code>.</p><p><strong>Example:</strong> <code>prices = [3,3,5,0,0,3,1,4]</code> gives <code>6</code>: buy at 0 and sell at 3 (profit 3), then buy at 1 and sell at 4 (profit 3).</p>",
    constraints=["1 &le; prices.length &le; 5,000", "0 &le; prices[i] &le; 100,000"],
    hints=["With one transaction you only need the lowest price so far. With two, the second trade starts from the profit the first one already made.",
           "At any moment you are in one of four situations: bought the first share, sold the first, bought the second, sold the second. Keep the best balance for each.",
           "Per price p: <code>b1 = max(b1, -p)</code>, <code>s1 = max(s1, b1 + p)</code>, <code>b2 = max(b2, s1 - p)</code>, <code>s2 = max(s2, b2 + p)</code>. Start with b1 = b2 = -infinity and s1 = s2 = 0; the answer is s2."],
    editorial=["Model the process as a small state machine with four balances. <code>b1</code> is the best cash while holding the share of the first transaction (price paid is subtracted), <code>s1</code> the best cash after finishing it, <code>b2</code> the best cash while holding the share of the second, <code>s2</code> the best cash after finishing both. Each day can only move forward along that chain or stay put.",
               "Update in the order b1, s1, b2, s2 using the new values of the previous stage. Using today's <code>s1</code> when computing <code>b2</code> corresponds to selling and re-buying on the same day, which the statement allows (and which never beats simply holding). Because <code>s1</code> and <code>s2</code> start at 0, 'fewer than two transactions' is covered automatically.",
               "One pass with four variables: O(n) time, O(1) space. The same idea extends to k transactions with arrays <code>buy[j]</code> and <code>sell[j]</code>. An alternative is to compute the best single trade ending on or before each day (prefix) and starting on or after each day (suffix) and combine them at the split point."],
    time="O(n)", space="O(1)",
    solution='''def maxProfitTwo(prices):
    b1 = b2 = -10 ** 9
    s1 = s2 = 0
    for p in prices:
        b1 = max(b1, -p)
        s1 = max(s1, b1 + p)
        b2 = max(b2, s1 - p)
        s2 = max(s2, b2 + p)
    return s2
''',
    tests=[[[3, 3, 5, 0, 0, 3, 1, 4]], [[1, 2, 3, 4, 5]], [[7, 6, 4, 3, 1]], [[5]], [[1, 2]], [[2, 1]], [[1, 2, 4, 2, 5, 7, 2, 4, 9, 0]],
           [[0, 100000, 0, 100000, 0, 100000]], [[6, 1, 3, 2, 4, 7]], [[2, 1, 2, 0, 1]], [[4, 4, 4, 4]]],
)
_r = rnd(8301)
p["tests"].append([_walk(_r, 5000, 50000, 0, 100000, 3000)])
p["tests"].append([[_r.randint(0, 100000) for _ in range(4000)]])
p["tests"].append([[99000 - i * 20 + (1000 if i % 700 < 350 else 0) for i in range(4500)]])


def _b_two(prices):
    n = len(prices)
    best = 0
    # one trade (i, j) or two trades (i, j) and (k, l) with j <= k
    for i in range(n):
        for j in range(i + 1, n):
            g = prices[j] - prices[i]
            best = max(best, g)
            for k in range(j, n):
                for l in range(k + 1, n):
                    best = max(best, g + prices[l] - prices[k])
    return best


def _v_two(tests):
    for t in tests:
        a = t["args"][0]
        assert 1 <= len(a) <= 5000 and all(0 <= x <= 100000 for x in a)
        assert t["expected"] >= 0
    assert any(t["expected"] == 0 for t in tests) and any(t["expected"] > 0 for t in tests)


CHECKS["stock-profit-at-most-two-transactions"] = (_b_two, lambda r: [_prices(r, 1, 9, 9)], "exact")
VALIDATE["stock-profit-at-most-two-transactions"] = _v_two


# ---------------------------------------------------------------- Cooldown of c days

p = add(
    id="stock-profit-cooldown-c-days", title="Stock Profit with a Cooldown of C Days", diff="Medium", topic=TOPIC,
    fn="maxProfitCooldown", params=[("prices", "int[]"), ("c", "int")], ret="int", cmp="exact",
    desc="<p><code>prices[i]</code> is the price of a stock on day <code>i</code>. You may make as many transactions as you like; a transaction is one purchase of a single share followed by a sale on a strictly later day. You can hold at most one share at a time.</p><p>After you sell on day <code>s</code>, you must rest for <code>c</code> full days: the earliest day on which you may buy again is <code>s + c + 1</code>. Return the maximum total profit.</p><p><strong>Example:</strong> <code>prices = [1,2,3,0,2]</code>. With <code>c = 1</code> the answer is <code>3</code> (buy 1, sell 2, rest, buy 0, sell 2). With <code>c = 2</code> it is <code>2</code> (for example buy 1 and sell 3, or buy 0 and sell 2).</p>",
    constraints=["1 &le; prices.length &le; 5,000", "0 &le; prices[i] &le; 10,000", "1 &le; c &le; 20"],
    hints=["Think of each day as ending in one of two situations: holding a share, or holding nothing. What extra information does the cooldown add?",
           "Let <code>free[i]</code> be the best profit after day i with no share in hand (a sale on day i counts). You may only buy on day i using the profit <code>free[i - c - 1]</code>, because the last sale has to be at least c + 1 days before.",
           "<code>hold[i] = max(hold[i-1], free[i-c-1] - prices[i])</code> and <code>free[i] = max(free[i-1], hold[i-1] + prices[i])</code>, treating free of a negative index as 0. The answer is <code>free[n-1]</code>."],
    editorial=["Use two arrays (or a rolling window). <code>free[i]</code> is the best profit at the end of day i without a share; <code>hold[i]</code> is the best profit at the end of day i while holding a share (the purchase price already subtracted). A sale on day i uses the holding state of day i-1 or earlier, so <code>free[i] = max(free[i-1], hold[i-1] + prices[i])</code>.",
               "A purchase on day i is only legal if the last sale happened on day i - c - 1 or earlier. The best profit achievable under that condition is exactly <code>free[i-c-1]</code> (which already includes the option of having sold on that very day), so <code>hold[i] = max(hold[i-1], free[i-c-1] - prices[i])</code>. For i - c - 1 &lt; 0 nothing has been sold yet, so the base is 0.",
               "Each day costs O(1) work, giving O(n) time. Storing the whole <code>free</code> array uses O(n) memory; keeping only the last c + 1 values would reduce it to O(c). For c = 1 this is the classic three-state 'hold / just sold / rested' machine."],
    time="O(n)", space="O(n)",
    solution='''def maxProfitCooldown(prices, c):
    n = len(prices)
    free = [0] * n
    hold = -10 ** 9
    for i in range(n):
        free[i] = free[i - 1] if i else 0
        if hold + prices[i] > free[i]:
            free[i] = hold + prices[i]
        j = i - c - 1
        base = free[j] if j >= 0 else 0
        if base - prices[i] > hold:
            hold = base - prices[i]
    return free[n - 1]
''',
    tests=[[[1, 2, 3, 0, 2], 1], [[1, 2, 3, 0, 2], 2], [[1], 1], [[1, 2], 1], [[2, 1], 3], [[1, 4, 2, 7, 3, 9], 2],
           [[1, 4, 2, 7, 3, 9], 1], [[1, 4, 2, 7, 3, 9], 20], [[0, 10, 0, 10, 0, 10, 0, 10], 1], [[0, 10, 0, 10, 0, 10, 0, 10], 2],
           [[5, 5, 5, 5, 5], 1], [[3, 8, 2, 9, 1, 7, 4, 6], 3]],
)
_r = rnd(8302)
p["tests"].append([_walk(_r, 5000, 5000, 0, 10000, 800), 3])
p["tests"].append([[_r.randint(0, 10000) for _ in range(4000)], 1])
p["tests"].append([[(i % 9) * 1000 + _r.randint(0, 200) for i in range(4500)], 20])


def _b_cool(prices, c):
    n = len(prices)

    @lru_cache(maxsize=None)
    def go(start):
        # best profit using days >= start, every purchase on day >= start
        best = 0
        for b in range(start, n):
            for s in range(b + 1, n):
                best = max(best, prices[s] - prices[b] + go(s + c + 1))
        return best

    return go(0)


def _v_cool(tests):
    for t in tests:
        a, c = t["args"]
        assert 1 <= len(a) <= 5000 and all(0 <= x <= 10000 for x in a) and 1 <= c <= 20
        assert t["expected"] >= 0
    assert len({t["args"][1] for t in tests}) >= 4


CHECKS["stock-profit-cooldown-c-days"] = (_b_cool, lambda r: [_prices(r, 1, 10, 9), r.randint(1, 4)], "exact")
VALIDATE["stock-profit-cooldown-c-days"] = _v_cool


# ---------------------------------------------------------------- Fee + cooldown

p = add(
    id="stock-profit-fee-and-cooldown", title="Stock Profit with Fee and Cooldown", diff="Medium", topic=TOPIC, tier="extra",
    fn="maxProfitFeeCooldown", params=[("prices", "int[]"), ("fee", "int")], ret="int", cmp="exact",
    desc="<p><code>prices[i]</code> is the price of a stock on day <code>i</code>. You may make as many transactions as you like; a transaction is one purchase of a single share followed by a sale on a strictly later day, and you can hold at most one share at a time.</p><p>Two rules apply: every sale costs a fee of <code>fee</code> (so a transaction earns <code>sell - buy - fee</code>), and after selling on day <code>s</code> you cannot buy on day <code>s + 1</code>. Return the maximum total profit; you are never forced to trade, so the answer is at least <code>0</code>.</p><p><strong>Example:</strong> <code>prices = [1,4,2,8,5,9]</code>, <code>fee = 1</code> gives <code>7</code>: a single trade from 1 to 9 earns 8 - 1 = 7, which beats any pair of shorter trades once the fee and the rest day are paid for.</p>",
    constraints=["1 &le; prices.length &le; 5,000", "0 &le; prices[i] &le; 10,000", "0 &le; fee &le; 10,000"],
    hints=["Combine two familiar machines: the fee shrinks every transaction, and the rest day forbids chaining a sale straight into a purchase.",
           "Keep three values per day: <code>hold</code> (own a share), <code>sold</code> (sold today, so tomorrow is a rest day) and <code>free</code> (own nothing and may buy today).",
           "<code>hold' = max(hold, free - p)</code>, <code>sold' = hold + p - fee</code>, <code>free' = max(free, sold)</code>, all computed from yesterday's values. Answer: <code>max(sold, free)</code> after the last day."],
    editorial=["The rest day rule means a share can only be bought from a state in which you did not sell yesterday. Split 'no share' into <code>sold</code> (a sale happened today) and <code>free</code> (no share and no sale today). A purchase starts from <code>free</code>, a sale ends in <code>sold</code>, and one day later <code>sold</code> turns into <code>free</code>.",
               "Charge the fee at sale time: <code>sold' = hold + p - fee</code>. Initially <code>hold = -infinity</code>, <code>sold = 0</code> and <code>free = 0</code> (nothing can be sold before something is bought, and <code>sold = 0</code> simply means 'no share, no trade yet').",
               "All three updates must read the previous day's values, so compute them together. It is a single pass with three variables: O(n) time, O(1) space."],
    time="O(n)", space="O(1)",
    solution='''def maxProfitFeeCooldown(prices, fee):
    hold = -10 ** 9
    sold = 0
    free = 0
    for p in prices:
        hold, sold, free = max(hold, free - p), hold + p - fee, max(free, sold)
    return max(sold, free)
''',
    tests=[[[1, 4, 2, 8, 5, 9], 1], [[1, 4, 2, 8, 5, 9], 0], [[1, 4, 2, 8, 5, 9], 10], [[7], 2], [[1, 2], 0], [[1, 2], 1],
           [[1, 3, 1, 3, 1, 3, 1, 3], 0], [[1, 3, 1, 3, 1, 3, 1, 3], 1], [[10, 9, 8, 7], 0], [[0, 10000, 0, 10000], 5000],
           [[2, 6, 3, 9, 4, 12, 1, 8], 2]],
)
_r = rnd(8303)
p["tests"].append([_walk(_r, 5000, 5000, 0, 10000, 700), 300])
p["tests"].append([[_r.randint(0, 10000) for _ in range(4000)], 2500])
p["tests"].append([[(i % 7) * 1400 + _r.randint(0, 300) for i in range(4500)], 100])


def _b_feecool(prices, fee):
    n = len(prices)

    @lru_cache(maxsize=None)
    def go(start):
        best = 0
        for b in range(start, n):
            for s in range(b + 1, n):
                best = max(best, prices[s] - prices[b] - fee + go(s + 2))
        return best

    return go(0)


def _v_feecool(tests):
    for t in tests:
        a, fee = t["args"]
        assert 1 <= len(a) <= 5000 and all(0 <= x <= 10000 for x in a) and 0 <= fee <= 10000
        assert t["expected"] >= 0
    assert any(t["expected"] == 0 for t in tests) and any(t["expected"] > 0 for t in tests)


CHECKS["stock-profit-fee-and-cooldown"] = (_b_feecool, lambda r: [_prices(r, 1, 10, 9), r.randint(0, 4)], "exact")
VALIDATE["stock-profit-fee-and-cooldown"] = _v_feecool


# ---------------------------------------------------------------- Hold up to m shares

p = add(
    id="stock-profit-hold-up-to-m-shares", title="Stock Profit Holding Up to M Shares", diff="Medium", topic=TOPIC,
    fn="maxProfitShares", params=[("prices", "int[]"), ("m", "int")], ret="int", cmp="exact",
    desc="<p><code>prices[i]</code> is the price of a stock on day <code>i</code>. On every day you may perform at most one action: buy one share, sell one share, or do nothing. You may own at most <code>m</code> shares at any moment and you start with none. Shares you still own after the last day are worth nothing, so you will want to sell them before that.</p><p>Return the maximum total profit.</p><p><strong>Example:</strong> <code>prices = [1,2,4,3,5,6]</code>. With <code>m = 1</code> the answer is <code>6</code> (1 to 4, then 3 to 6). With <code>m = 2</code> it is <code>9</code>: buy on days 0, 1 and 3, sell on days 2, 4 and 5, earning 3 + 3 + 3.</p>",
    constraints=["1 &le; prices.length &le; 3,000", "0 &le; prices[i] &le; 1,000", "1 &le; m &le; 50"],
    hints=["With m = 1 this is the unlimited-transactions problem. What extra thing must a day remember when several shares may be owned?",
           "Remember how many shares you own right now: j between 0 and m. Let <code>dp[j]</code> be the best cash balance while owning j shares.",
           "For each price p build a new array: keep <code>dp[j]</code>, or buy (<code>dp[j-1] - p</code>), or sell (<code>dp[j+1] + p</code>) and take the maximum. Start with dp[0] = 0 and the others at -infinity; the answer is dp[0] at the end."],
    editorial=["The only thing that matters for the future is the day and the number of shares in your hands, so use a DP over (day, shares owned). <code>dp[j]</code> is the best cash after the current day with j shares owned; cash already accounts for the purchase prices of those shares.",
               "On a new price p, the options for the new count j are: do nothing (<code>dp[j]</code>), buy one (<code>dp[j-1] - p</code>, needs j &ge; 1) or sell one (<code>dp[j+1] + p</code>, needs j &lt; m). Because only one action is allowed per day, the new array must be built from the old one, not updated in place.",
               "Leftover shares are worth nothing, so the best final answer owns zero shares: <code>dp[0]</code>. The work is O(n &middot; m) time and O(m) space."],
    time="O(n m)", space="O(m)",
    solution='''def maxProfitShares(prices, m):
    NEG = -10 ** 9
    dp = [0] + [NEG] * m
    for p in prices:
        nd = dp[:]
        for j in range(m + 1):
            if j > 0 and dp[j - 1] - p > nd[j]:
                nd[j] = dp[j - 1] - p
            if j < m and dp[j + 1] + p > nd[j]:
                nd[j] = dp[j + 1] + p
        dp = nd
    return dp[0]
''',
    tests=[[[1, 2, 4, 3, 5, 6], 1], [[1, 2, 4, 3, 5, 6], 2], [[1, 2, 4, 3, 5, 6], 3], [[5], 3], [[1, 2], 1], [[2, 1], 4],
           [[1, 1, 1, 1], 2], [[1, 2, 3, 4, 5, 6, 7, 8], 4], [[8, 7, 6, 5, 4, 3], 2], [[0, 1000, 0, 1000, 0, 1000], 2],
           [[3, 1, 4, 1, 5, 9, 2, 6, 5, 3, 5], 3]],
)
_r = rnd(8304)
p["tests"].append([_walk(_r, 3000, 500, 0, 1000, 60), 50])
p["tests"].append([[_r.randint(0, 1000) for _ in range(3000)], 17])
p["tests"].append([[(i % 20) * 50 for i in range(2500)], 8])


def _b_shares(prices, m):
    n = len(prices)

    @lru_cache(maxsize=None)
    def go(i, held):
        if i == n:
            return 0 if held == 0 else NEG
        best = go(i + 1, held)
        if held < m:
            best = max(best, -prices[i] + go(i + 1, held + 1))
        if held > 0:
            best = max(best, prices[i] + go(i + 1, held - 1))
        return best

    return go(0, 0)


def _v_shares(tests):
    for t in tests:
        a, m = t["args"]
        assert 1 <= len(a) <= 3000 and all(0 <= x <= 1000 for x in a) and 1 <= m <= 50
        assert t["expected"] >= 0
    assert len({t["args"][1] for t in tests}) >= 5


CHECKS["stock-profit-hold-up-to-m-shares"] = (_b_shares, lambda r: [_prices(r, 1, 9, 9), r.randint(1, 4)], "exact")
VALIDATE["stock-profit-hold-up-to-m-shares"] = _v_shares


# ---------------------------------------------------------------- Long or short with fee

p = add(
    id="stock-profit-long-or-short-with-fee", title="Stock Profit Going Long or Short with Fee", diff="Medium", topic=TOPIC,
    fn="maxProfitLongShort", params=[("prices", "int[]"), ("fee", "int")], ret="int", cmp="exact",
    desc="<p><code>prices[i]</code> is the price of a stock on day <code>i</code>. You may take one position at a time, and you can take as many positions as you like:</p><ul><li><strong>long</strong>: buy on day <code>b</code>, sell on a later day <code>s</code>; profit <code>prices[s] - prices[b]</code>.</li><li><strong>short</strong>: sell a borrowed share on day <code>b</code>, buy it back on a later day <code>s</code>; profit <code>prices[b] - prices[s]</code>.</li></ul><p>Every position must be closed by the last day, and closing a position costs <code>fee</code>. You may close a position and open a new one on the same day. Return the maximum total profit after fees (it is at least <code>0</code> because you may stay out of the market).</p><p><strong>Example:</strong> <code>prices = [1,5,2,6]</code>, <code>fee = 1</code> gives <code>8</code>: long 1 to 5 (3 after the fee), short 5 to 2 (2), long 2 to 6 (3).</p>",
    constraints=["1 &le; prices.length &le; 5,000", "1 &le; prices[i] &le; 10,000", "0 &le; fee &le; 10,000"],
    hints=["Without a fee you would earn the absolute change between every pair of neighbouring days. The fee makes tiny moves not worth acting on.",
           "At the end of each day you are in one of three states: no position, long, or short. Keep the best profit for each, with the opening price already accounted for.",
           "On price p: <code>flat' = max(flat, long + p - fee, short - p - fee)</code>, then <code>long' = max(long, flat' - p)</code> and <code>short' = max(short, flat' + p)</code>. Start with flat = 0, long = -prices[0], short = prices[0]; the answer is the final flat."],
    editorial=["Extend the buy/sell machine with a second way of holding: being short. The balance for a long position is cash minus the purchase price; for a short position it is cash plus the proceeds of the borrowed sale. Closing a long adds today's price, closing a short subtracts it, and both pay the fee.",
               "Compute the new 'flat' state first (stay flat, or close either position today), because closing and opening on the same day is allowed: the new long and short balances may start from the new flat value. Position open prices are baked into the balances, so no extra state is needed.",
               "Positions must be closed by the end, therefore the answer is the last flat balance. One pass, O(n) time and O(1) space."],
    time="O(n)", space="O(1)",
    solution='''def maxProfitLongShort(prices, fee):
    flat = 0
    long_ = -prices[0]
    short = prices[0]
    for p in prices[1:]:
        flat = max(flat, long_ + p - fee, short - p - fee)
        long_ = max(long_, flat - p)
        short = max(short, flat + p)
    return flat
''',
    tests=[[[1, 5, 2, 6], 1], [[1, 5, 2, 6], 0], [[1, 5, 2, 6], 3], [[4], 1], [[3, 3], 0], [[5, 2], 1], [[5, 2], 3],
           [[1, 3, 1, 3, 1, 3], 0], [[1, 3, 1, 3, 1, 3], 1], [[10000, 1, 10000, 1], 100], [[7, 7, 7, 7], 0],
           [[2, 9, 4, 12, 3, 8, 1, 7], 2]],
)
_r = rnd(8305)
p["tests"].append([_walk(_r, 5000, 5000, 1, 10000, 600), 250])
p["tests"].append([[_r.randint(1, 10000) for _ in range(4000)], 3000])
p["tests"].append([[_r.randint(1, 10000) for _ in range(3000)], 0])


def _b_ls(prices, fee):
    n = len(prices)

    @lru_cache(maxsize=None)
    def go(start):
        best = 0
        for b in range(start, n):
            for s in range(b + 1, n):
                best = max(best, abs(prices[s] - prices[b]) - fee + go(s))
        return best

    return go(0)


def _v_ls(tests):
    for t in tests:
        a, fee = t["args"]
        assert 1 <= len(a) <= 5000 and all(1 <= x <= 10000 for x in a) and 0 <= fee <= 10000
        assert t["expected"] >= 0
    assert any(t["expected"] == 0 for t in tests) and any(t["expected"] > 0 for t in tests)


CHECKS["stock-profit-long-or-short-with-fee"] = (_b_ls, lambda r: [_prices(r, 1, 9, 9, 1), r.randint(0, 4)], "exact")
VALIDATE["stock-profit-long-or-short-with-fee"] = _v_ls


# ---------------------------------------------------------------- Two stocks, one share, fee

p = add(
    id="stock-profit-two-stocks-with-fee", title="Stock Profit Choosing Between Two Stocks", diff="Medium", topic=TOPIC, tier="extra",
    fn="maxProfitTwoStocks", params=[("a", "int[]"), ("b", "int[]"), ("fee", "int")], ret="int", cmp="exact",
    desc="<p>Two stocks A and B are traded on the same days: <code>a[i]</code> and <code>b[i]</code> are their prices on day <code>i</code>. You can hold <strong>at most one share in total</strong>, of either stock. A transaction is a purchase of one share of A or of B followed by a sale of that same stock on a strictly later day. You may make as many transactions as you like, and you may sell and buy again on the same day (even switching stocks). Each sale costs <code>fee</code>.</p><p>Return the maximum total profit after fees (at least <code>0</code>).</p><p><strong>Example:</strong> <code>a = [1,5,2,6]</code>, <code>b = [3,1,4,2]</code>, <code>fee = 1</code> gives <code>8</code>: A from 1 to 5 (3 after the fee), B from 1 to 4 (2), A from 2 to 6 (3).</p>",
    constraints=["a.length = b.length", "1 &le; a.length &le; 3,000", "0 &le; a[i], b[i] &le; 10,000", "0 &le; fee &le; 10,000"],
    hints=["Without any fee you could switch stocks every day for free. What does the fee change?",
           "At the end of each day you are in one of three states: holding nothing, holding A, holding B. Track the best balance of each.",
           "On day i: <code>flat' = max(flat, hA + a[i] - fee, hB + b[i] - fee)</code>, then <code>hA' = max(hA, flat' - a[i])</code> and <code>hB' = max(hB, flat' - b[i])</code>. Start with flat = 0, hA = -a[0], hB = -b[0]."],
    editorial=["The state is just 'which stock (if any) is in the portfolio'. <code>hA</code> and <code>hB</code> store the cash balance after paying for the share. Selling A or B returns you to the flat state and costs the fee; buying leaves flat for one of the two holding states.",
               "Since a sale and a purchase may happen on the same day, compute the new flat value first and let both holding states be refreshed from it. This allows switching A to B in one day at the price of one fee, and the DP naturally decides when switching is worth it.",
               "The answer is the last flat balance (nothing may be left unsold). One pass over the days: O(n) time, O(1) space."],
    time="O(n)", space="O(1)",
    solution='''def maxProfitTwoStocks(a, b, fee):
    flat = 0
    ha = -a[0]
    hb = -b[0]
    for i in range(1, len(a)):
        flat = max(flat, ha + a[i] - fee, hb + b[i] - fee)
        ha = max(ha, flat - a[i])
        hb = max(hb, flat - b[i])
    return flat
''',
    tests=[[[1, 5, 2, 6], [3, 1, 4, 2], 1], [[1, 5, 2, 6], [3, 1, 4, 2], 0], [[1, 5, 2, 6], [3, 1, 4, 2], 4], [[5], [7], 1],
           [[1, 2], [2, 1], 0], [[1, 2], [2, 1], 1], [[3, 3, 3], [3, 3, 3], 0], [[0, 10000, 0, 10000], [10000, 0, 10000, 0], 100],
           [[9, 7, 5, 3], [1, 2, 3, 4], 0], [[4, 1, 6, 2, 8, 3], [2, 5, 1, 7, 3, 9], 2]],
)
_r = rnd(8306)
p["tests"].append([_walk(_r, 2500, 5000, 0, 10000, 500), _walk(_r, 2500, 5000, 0, 10000, 500), 200])
p["tests"].append([[_r.randint(0, 10000) for _ in range(2000)], [_r.randint(0, 10000) for _ in range(2000)], 1500])
p["tests"].append([[(i % 11) * 900 for i in range(2200)], [9900 - (i % 13) * 700 for i in range(2200)], 50])


def _b_two_st(a, b, fee):
    n = len(a)

    @lru_cache(maxsize=None)
    def go(start):
        best = 0
        for x in (a, b):
            for i in range(start, n):
                for j in range(i + 1, n):
                    best = max(best, x[j] - x[i] - fee + go(j))
        return best

    return go(0)


def _g_two_st(r):
    n = r.randint(1, 8)
    return [[r.randint(0, 9) for _ in range(n)], [r.randint(0, 9) for _ in range(n)], r.randint(0, 4)]


def _v_two_st(tests):
    for t in tests:
        a, b, fee = t["args"]
        assert len(a) == len(b) and 1 <= len(a) <= 3000
        assert all(0 <= x <= 10000 for x in a + b) and 0 <= fee <= 10000
        assert t["expected"] >= 0
    assert any(t["expected"] == 0 for t in tests) and any(t["expected"] > 0 for t in tests)


CHECKS["stock-profit-two-stocks-with-fee"] = (_b_two_st, _g_two_st, "exact")
VALIDATE["stock-profit-two-stocks-with-fee"] = _v_two_st


# ---------------------------------------------------------------- Minimum holding days

p = add(
    id="stock-profit-minimum-holding-days", title="Stock Profit with a Minimum Holding Period", diff="Medium", topic=TOPIC,
    fn="maxProfitMinHold", params=[("prices", "int[]"), ("h", "int")], ret="int", cmp="exact",
    desc="<p><code>prices[i]</code> is the price of a stock on day <code>i</code>. You may make as many transactions as you like; a transaction is one purchase of a single share followed by a sale. You can hold at most one share at a time, and you may sell and buy again on the same day.</p><p>A share must be kept for at least <code>h</code> days: if you buy on day <code>b</code>, the earliest day you may sell it is <code>b + h</code>. Return the maximum total profit (at least <code>0</code>).</p><p><strong>Example:</strong> <code>prices = [1,3,2,6,4,8]</code>. With <code>h = 1</code> the answer is <code>10</code> (2 + 4 + 4). With <code>h = 3</code> it is <code>7</code> (buy at 1, sell at 8 on day 5). With <code>h = 6</code> no sale is ever possible, so the answer is <code>0</code>.</p>",
    constraints=["1 &le; prices.length &le; 5,000", "0 &le; prices[i] &le; 10,000", "1 &le; h &le; 5,000"],
    hints=["Let <code>f[i]</code> be the best profit achievable using days up to i with nothing held at the end of day i. How does a sale on day i look?",
           "If you sell on day i, the share was bought on some day j &le; i - h, and before that purchase you had earned <code>f[j]</code>. So the sale yields <code>prices[i] + f[j] - prices[j]</code>.",
           "<code>f[i] = max(f[i-1], prices[i] + best[i-h])</code> where <code>best[k] = max over j &le; k of (f[j] - prices[j])</code>, a running maximum. For i &lt; h only <code>f[i-1]</code> is possible."],
    editorial=["Define <code>f[i]</code> as the maximum profit after day i with no share in hand. Either nothing happens on day i (<code>f[i-1]</code>), or a share is sold on day i. That share was bought on some day j with j + h &le; i, and just before buying you were flat having earned at most <code>f[j]</code> (a sale on day j itself is fine). The total is <code>f[j] - prices[j] + prices[i]</code>.",
               "Maximising over all admissible j means maximising <code>g[j] = f[j] - prices[j]</code> over the prefix j &le; i - h. Keep the prefix maxima <code>best[k]</code> in an array: when processing day i, <code>f[i-1]</code> and <code>best[i-h]</code> are both already known, and afterwards <code>g[i]</code> extends the running maximum.",
               "Total time O(n), memory O(n). For h = 1 the formula collapses to the classic unlimited-transactions answer (sum of all rises)."],
    time="O(n)", space="O(n)",
    solution='''def maxProfitMinHold(prices, h):
    n = len(prices)
    f = [0] * n
    best = [0] * n
    for i in range(n):
        f[i] = f[i - 1] if i else 0
        if i >= h:
            f[i] = max(f[i], prices[i] + best[i - h])
        g = f[i] - prices[i]
        best[i] = max(best[i - 1], g) if i else g
    return f[n - 1]
''',
    tests=[[[1, 3, 2, 6, 4, 8], 1], [[1, 3, 2, 6, 4, 8], 3], [[1, 3, 2, 6, 4, 8], 6], [[4], 1], [[1, 2], 1], [[1, 2], 2],
           [[5, 4, 3, 2, 1], 2], [[0, 5, 0, 5, 0, 5, 0, 5], 1], [[0, 5, 0, 5, 0, 5, 0, 5], 2], [[0, 5, 0, 5, 0, 5, 0, 5], 3],
           [[3, 9, 1, 2, 8, 4, 10, 0, 6], 2]],
)
_r = rnd(8307)
p["tests"].append([_walk(_r, 5000, 5000, 0, 10000, 600), 7])
p["tests"].append([[_r.randint(0, 10000) for _ in range(4000)], 1])
p["tests"].append([[_r.randint(0, 10000) for _ in range(4000)], 250])


def _b_minhold(prices, h):
    n = len(prices)

    @lru_cache(maxsize=None)
    def go(start):
        best = 0
        for b in range(start, n):
            for s in range(b + h, n):
                best = max(best, prices[s] - prices[b] + go(s))
        return best

    return go(0)


def _v_minhold(tests):
    for t in tests:
        a, h = t["args"]
        assert 1 <= len(a) <= 5000 and all(0 <= x <= 10000 for x in a) and 1 <= h <= 5000
        assert t["expected"] >= 0
    assert any(t["expected"] == 0 for t in tests) and any(t["expected"] > 0 for t in tests)
    assert len({t["args"][1] for t in tests}) >= 5


CHECKS["stock-profit-minimum-holding-days"] = (_b_minhold, lambda r: [_prices(r, 1, 10, 9), r.randint(1, 5)], "exact")
VALIDATE["stock-profit-minimum-holding-days"] = _v_minhold


# ---------------------------------------------------------------- Maximum holding days with fee (Hard)

p = add(
    id="stock-profit-fee-max-holding-days", title="Stock Profit with Fee and a Maximum Holding Period", diff="Hard", topic=TOPIC, tier="extra",
    fn="maxProfitFeeMaxHold", params=[("prices", "int[]"), ("d", "int"), ("fee", "int")], ret="int", cmp="exact",
    desc="<p><code>prices[i]</code> is the price of a stock on day <code>i</code>. You may make as many transactions as you like; a transaction is one purchase of a single share followed by a sale on a strictly later day. You can hold at most one share at a time, and you may sell and buy again on the same day. Every sale costs <code>fee</code>.</p><p>A share may not be kept too long: if you buy on day <code>b</code>, you must sell it on some day <code>s</code> with <code>b &lt; s &le; b + d</code>. Return the maximum total profit after fees (at least <code>0</code>, since you may choose not to trade).</p><p><strong>Example:</strong> <code>prices = [1,2,3,4,5]</code>, <code>fee = 1</code>. With <code>d = 4</code> the answer is <code>3</code> (one trade from 1 to 5). With <code>d = 2</code> it is <code>2</code> (1 to 3 and 3 to 5, one fee each), and with <code>d = 1</code> it is <code>0</code> (every one-day trade earns 1 - 1).</p>",
    constraints=["1 &le; prices.length &le; 5,000", "0 &le; prices[i] &le; 10,000", "1 &le; d &le; 5,000", "0 &le; fee &le; 10,000"],
    hints=["Let <code>f[i]</code> be the best profit using days up to i with no share held at the end of day i. A sale on day i uses a purchase on a day j in a window just before i.",
           "The purchase day j must satisfy <code>i - d &le; j &le; i - 1</code>, and the value of buying on day j is <code>f[j] - prices[j]</code>. You need the maximum of that quantity over a sliding window.",
           "Maintain the window maximum with a monotonic deque of day indices holding decreasing values of <code>g[j] = f[j] - prices[j]</code>. Then <code>f[i] = max(f[i-1], prices[i] - fee + g[front])</code>, and afterwards push day i with g[i]."],
    editorial=["Without a fee the holding limit would be harmless: a long trade can always be cut into one-day trades that earn the same. The fee is what makes long holds valuable and the limit d a real restriction.",
               "Let <code>f[i]</code> be the best profit after day i with nothing held. Either nothing happens (<code>f[i-1]</code>) or a share is sold on day i: <code>prices[i] - fee + g[j]</code> for the best purchase day j in <code>[i-d, i-1]</code>, where <code>g[j] = f[j] - prices[j]</code> (you were flat with profit <code>f[j]</code> and then paid <code>prices[j]</code>).",
               "Scanning the window costs O(d) per day, O(n d) overall. Because the window slides one step per day and only its maximum is needed, a monotonic deque gives amortised O(1) per day: drop indices smaller than i - d from the front before querying; after computing <code>g[i]</code> pop from the back every index whose g is not larger, then append i. Query before inserting day i, because the purchase must be strictly earlier. Total O(n) time and O(n) memory."],
    time="O(n)", space="O(n)",
    solution='''from collections import deque


def maxProfitFeeMaxHold(prices, d, fee):
    n = len(prices)
    f = [0] * n
    g = [0] * n
    dq = deque()
    for i in range(n):
        while dq and dq[0] < i - d:
            dq.popleft()
        f[i] = f[i - 1] if i else 0
        if dq:
            f[i] = max(f[i], prices[i] - fee + g[dq[0]])
        g[i] = f[i] - prices[i]
        while dq and g[dq[-1]] <= g[i]:
            dq.pop()
        dq.append(i)
    return f[n - 1]
''',
    tests=[[[1, 2, 3, 4, 5], 4, 1], [[1, 2, 3, 4, 5], 2, 1], [[1, 2, 3, 4, 5], 1, 1], [[1, 2, 3, 4, 5], 1, 0], [[1, 9, 2, 3, 4, 10], 1, 2],
           [[1, 9, 2, 3, 4, 10], 2, 2], [[1, 9, 2, 3, 4, 10], 5, 2], [[7], 1, 0], [[2, 1], 1, 1], [[5, 4, 3, 2, 1], 3, 0],
           [[3, 0, 6, 1, 2, 9, 4, 5], 2, 1], [[3, 0, 6, 1, 2, 9, 4, 5], 5, 1], [[0, 10, 5, 10, 0, 10], 2, 3], [[4, 4, 4, 4], 2, 0]],
)
_r = rnd(8308)
p["tests"].append([_walk(_r, 5000, 5000, 0, 10000, 600), 5, 400])
p["tests"].append([[_r.randint(0, 10000) for _ in range(4000)], 40, 1500])
p["tests"].append([_walk(_r, 4000, 5000, 0, 10000, 300), 250, 600])


def _b_maxhold(prices, d, fee):
    n = len(prices)

    @lru_cache(maxsize=None)
    def go(start):
        best = 0
        for b in range(start, n):
            for s in range(b + 1, min(n, b + d + 1)):
                best = max(best, prices[s] - prices[b] - fee + go(s))
        return best

    return go(0)


def _v_maxhold(tests):
    for t in tests:
        a, d, fee = t["args"]
        assert 1 <= len(a) <= 5000 and all(0 <= x <= 10000 for x in a) and 1 <= d <= 5000 and 0 <= fee <= 10000
        assert t["expected"] >= 0
    assert any(t["expected"] == 0 for t in tests) and any(t["expected"] > 0 for t in tests)
    assert len({t["args"][1] for t in tests}) >= 5


CHECKS["stock-profit-fee-max-holding-days"] = (_b_maxhold, lambda r: [_prices(r, 1, 10, 9), r.randint(1, 5), r.randint(0, 4)], "exact")
VALIDATE["stock-profit-fee-max-holding-days"] = _v_maxhold


# ---------------------------------------------------------------- Fewest transactions for a target (Hard)

p = add(
    id="stock-fewest-transactions-for-target", title="Fewest Stock Transactions to Reach a Target", diff="Hard", topic=TOPIC, tier="extra",
    fn="fewestTransactions", params=[("prices", "int[]"), ("target", "int")], ret="int", cmp="exact",
    desc="<p><code>prices[i]</code> is the price of a stock on day <code>i</code>. A transaction is one purchase of a single share followed by a sale on a strictly later day; you can hold at most one share at a time, so the next purchase may happen on the day of the previous sale but not earlier.</p><p>Return the smallest number of transactions with which the total profit can reach at least <code>target</code>, or <code>-1</code> if even unlimited transactions cannot reach it.</p><p><strong>Example:</strong> <code>prices = [1,5,2,6,3,7]</code>. One transaction earns at most 6, two at most 9 and three at most 12. For <code>target = 9</code> the answer is <code>2</code>; for <code>target = 13</code> it is <code>-1</code>.</p>",
    constraints=["1 &le; prices.length &le; 4,000", "0 &le; prices[i] &le; 1,000", "1 &le; target &le; 2,000,000"],
    hints=["Let F(k) be the maximum profit with at most k transactions. F never decreases with k, so you are looking for the first k with F(k) &ge; target. Doing the k-transaction DP for every k is too slow for n = 4000.",
           "F(k) is concave: each extra transaction adds no more than the one before it. So F(k) is the sum of the k largest 'marginal gains' of some fixed list.",
           "Walk the prices keeping a stack of rising segments (valley, peak). When a new segment starts lower or ends higher than earlier ones, merge them and record the profit that is given up or gained. Sort all recorded profits in descending order and take prefix sums until the target is reached."],
    editorial=["Decompose the price curve into maximal rising runs (valley to peak). Optimal solutions with k transactions are built from these runs: with fewer transactions than runs you must either drop the least valuable run or merge two neighbouring runs, and every such step costs as little as possible. This produces a fixed multiset of 'marginal gains' g1 &ge; g2 &ge; ... and F(k) = g1 + ... + gk.",
               "The stack procedure builds exactly that multiset. Keep a stack of (valley, peak) pairs. For each new run (v, p): while the top pair has a higher valley than v, pop it and record its own profit (it is a finished, independent run); then while the top pair has a lower peak than p, merge: pop it, record <code>peak_of_popped - v</code> and extend the new run to start at the popped valley. Push the run. At the end pop everything and record each pair's profit.",
               "Sort the recorded gains in descending order and accumulate until the sum reaches the target; the number of gains used is the answer, and -1 if their total is below the target. The scan is O(n) and the sort O(n log n). A binary search on k with the O(nk) DP is far too slow; this concavity is the key insight."],
    time="O(n log n)", space="O(n)",
    solution='''def fewestTransactions(prices, target):
    n = len(prices)
    gains = []
    stack = []
    p = 0
    while p < n:
        v = p
        while v < n - 1 and prices[v] >= prices[v + 1]:
            v += 1
        p = v + 1
        while p < n and prices[p] >= prices[p - 1]:
            p += 1
        while stack and prices[v] < prices[stack[-1][0]]:
            x, y = stack.pop()
            gains.append(prices[y - 1] - prices[x])
        while stack and prices[p - 1] >= prices[stack[-1][1] - 1]:
            x, y = stack.pop()
            gains.append(prices[y - 1] - prices[v])
            v = x
        stack.append((v, p))
    while stack:
        x, y = stack.pop()
        gains.append(prices[y - 1] - prices[x])
    gains.sort(reverse=True)
    total = 0
    for k, g in enumerate(gains, 1):
        if g <= 0:
            break
        total += g
        if total >= target:
            return k
    return -1
''',
    tests=[[[1, 5, 2, 6, 3, 7], 9], [[1, 5, 2, 6, 3, 7], 14], [[1, 5, 2, 6, 3, 7], 6], [[1, 5, 2, 6, 3, 7], 13], [[4], 1],
           [[3, 3, 3], 1], [[5, 4, 3, 2], 1], [[1, 2], 1], [[1, 2], 2], [[2, 4, 1], 2], [[3, 2, 6, 5, 0, 3], 7],
           [[1, 4, 2, 7, 1, 5, 0, 9], 12], [[1, 4, 2, 7, 1, 5, 0, 9], 11]],
)
_r = rnd(8309)
_a = [_r.randint(0, 1000) for _ in range(3000)]
p["tests"].append([_a, 150000])
p["tests"].append([_a, 400000])
p["tests"].append([[(i % 40) * 25 + _r.choice([0, 0, 5, 10]) for i in range(3200)], 60000])


def _b_fewest(prices, target):
    n = len(prices)

    @lru_cache(maxsize=None)
    def best(start, k):
        if k == 0:
            return 0
        res = 0
        for b in range(start, n):
            for s in range(b + 1, n):
                res = max(res, prices[s] - prices[b] + best(s, k - 1))
        return res

    for k in range(1, n // 2 + 1):
        if best(0, k) >= target:
            return k
    return -1


def _g_fewest(r):
    a = _prices(r, 1, 10, 9)
    return [a, r.randint(1, 25)]


def _v_fewest(tests):
    for t in tests:
        a, target = t["args"]
        assert 1 <= len(a) <= 4000 and all(0 <= x <= 1000 for x in a) and 1 <= target <= 2000000
        assert t["expected"] == -1 or t["expected"] >= 1
    assert any(t["expected"] == -1 for t in tests) and any(t["expected"] >= 3 for t in tests)


CHECKS["stock-fewest-transactions-for-target"] = (_b_fewest, _g_fewest, "exact")
VALIDATE["stock-fewest-transactions-for-target"] = _v_fewest


# ---------------------------------------------------------------- Easy: best trade days

p = add(
    id="stock-best-trade-days", title="Days of the Best Single Stock Trade", diff="Easy", topic=TOPIC, tier="extra",
    fn="bestTradeDays", params=[("prices", "int[]")], ret="int[]", cmp="exact",
    desc="<p><code>prices[i]</code> is the price of a stock on day <code>i</code> (days are numbered from 0). You make a single trade: buy on day <code>b</code> and sell on a later day <code>s &gt; b</code>.</p><p>Return <code>[b, s]</code> for the trade with the largest profit. If several trades have the same maximum profit, take the one with the smallest sell day, and among those the smallest buy day. If no trade has a positive profit, return <code>[-1, -1]</code>.</p><p><strong>Example:</strong> <code>prices = [7,1,5,3,6,4]</code> gives <code>[1, 4]</code> (buy at 1, sell at 6, profit 5).</p>",
    constraints=["1 &le; prices.length &le; 10,000", "0 &le; prices[i] &le; 100,000"],
    hints=["For a fixed sell day, which buy day is best?",
           "The best buy day for a sell day is the day with the lowest price before it. Scan left to right and remember that day.",
           "Keep the index of the lowest price so far (replace it only on a strictly lower price so the earliest wins). For each day compute the profit against it and replace the answer only on a strictly larger profit, so the earliest sell day wins."],
    editorial=["For a sell day s the best buy day is the earliest day before s with the minimum price. Maintain <code>lo</code>, the index of the lowest price seen so far, updating it only when a strictly smaller price appears. This yields the earliest minimum for ties.",
               "At each day compute <code>prices[s] - prices[lo]</code>. If it is strictly larger than the best profit so far (which starts at 0), store <code>[lo, s]</code>. Because the scan moves forward and the update needs a strictly larger profit, among equal maxima the first one found has the smallest sell day, exactly as the statement requires.",
               "A single pass: O(n) time and O(1) space. Comparing all pairs would be O(n^2)."],
    time="O(n)", space="O(1)",
    solution='''def bestTradeDays(prices):
    best = 0
    ans = [-1, -1]
    lo = 0
    for j in range(1, len(prices)):
        if prices[j] < prices[lo]:
            lo = j
        elif prices[j] - prices[lo] > best:
            best = prices[j] - prices[lo]
            ans = [lo, j]
    return ans
''',
    tests=[[[7, 1, 5, 3, 6, 4]], [[7, 6, 4, 3, 1]], [[5]], [[1, 2]], [[2, 1]], [[3, 3, 3]], [[2, 4, 1, 3, 5]],
           [[1, 5, 1, 5]], [[4, 1, 1, 6, 6, 3]], [[0, 100000]], [[9, 2, 5, 2, 7, 1, 6]]],
)
_r = rnd(8310)
p["tests"].append([_walk(_r, 5000, 50000, 0, 100000, 2000)])
p["tests"].append([[100000 - i * 10 for i in range(4000)]])
p["tests"].append([[(i * 37) % 1000 + 10 for i in range(4000)]])


def _b_bestdays(prices):
    n = len(prices)
    best = None
    for i in range(n):
        for j in range(i + 1, n):
            g = prices[j] - prices[i]
            if g > 0:
                key = (-g, j, i)
                if best is None or key < best:
                    best = key
    return [-1, -1] if best is None else [best[2], best[1]]


def _v_bestdays(tests):
    for t in tests:
        a = t["args"][0]
        assert 1 <= len(a) <= 10000 and all(0 <= x <= 100000 for x in a)
    assert any(t["expected"] == [-1, -1] for t in tests) and any(t["expected"] != [-1, -1] for t in tests)


CHECKS["stock-best-trade-days"] = (_b_bestdays, lambda r: [_prices(r, 1, 10, 6)], "exact")
VALIDATE["stock-best-trade-days"] = _v_bestdays


# ---------------------------------------------------------------- Easy: max drawdown

p = add(
    id="stock-max-drawdown", title="Stock Maximum Drawdown", diff="Easy", topic=TOPIC, tier="extra",
    fn="maxDrawdown", params=[("prices", "int[]")], ret="int", cmp="exact",
    desc="<p><code>prices[i]</code> is the closing price of a stock on day <code>i</code>. The <em>drawdown</em> between two days <code>i &lt; j</code> is <code>prices[i] - prices[j]</code>, how far the price fell from day <code>i</code> to day <code>j</code>.</p><p>Return the largest drawdown over all pairs <code>i &lt; j</code>. If the price never falls (or there is only one day), return <code>0</code>.</p><p><strong>Example:</strong> <code>prices = [5,9,4,7,2,8]</code> gives <code>7</code>, the fall from 9 to 2.</p>",
    constraints=["1 &le; prices.length &le; 10,000", "0 &le; prices[i] &le; 1,000,000"],
    hints=["This is the mirror image of the classic 'best time to buy and sell' problem: instead of the biggest rise after a low, you want the biggest fall after a high.",
           "For each day j, the best earlier day i is the one with the highest price so far.",
           "Scan left to right, keep the running maximum price, and track the maximum of <code>peak - price</code> over all days."],
    editorial=["For a fixed day j the largest drawdown ending at j is the highest earlier price minus <code>prices[j]</code>. So keep the highest price seen so far, <code>peak</code>, and for each day compute <code>peak - prices[j]</code>; the answer is the maximum of these values (and 0).",
               "Comparing all pairs works but takes O(n^2). The single scan is O(n) time and O(1) space. Remember to update <code>peak</code> after (or together with) computing the drawdown; a day compared with itself contributes 0, so the order does not change the result."],
    time="O(n)", space="O(1)",
    solution='''def maxDrawdown(prices):
    peak = prices[0]
    best = 0
    for x in prices:
        if x > peak:
            peak = x
        elif peak - x > best:
            best = peak - x
    return best
''',
    tests=[[[5, 9, 4, 7, 2, 8]], [[1, 2, 3, 4]], [[4]], [[9, 1]], [[1, 9]], [[3, 3, 3]], [[10, 2, 8, 1, 9, 0]],
           [[0, 1000000, 0]], [[6, 4, 5, 1, 3, 2]], [[2, 7, 1, 8, 2, 8, 1, 8]]],
)
_r = rnd(8311)
p["tests"].append([_walk(_r, 4000, 500000, 0, 1000000, 20000)])
p["tests"].append([[i * 100 for i in range(4500)]])
p["tests"].append([[_r.randint(0, 1000000) for _ in range(3500)]])


def _b_dd(prices):
    n = len(prices)
    return max([0] + [prices[i] - prices[j] for i in range(n) for j in range(i + 1, n)])


def _v_dd(tests):
    for t in tests:
        a = t["args"][0]
        assert 1 <= len(a) <= 10000 and all(0 <= x <= 1000000 for x in a)
        assert t["expected"] >= 0
    assert any(t["expected"] == 0 for t in tests) and any(t["expected"] > 0 for t in tests)


CHECKS["stock-max-drawdown"] = (_b_dd, lambda r: [_prices(r, 1, 10, 9)], "exact")
VALIDATE["stock-max-drawdown"] = _v_dd
