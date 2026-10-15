"""Problems: 1-D linear DP warmups (Fibonacci-like recurrences, staircases, tilings, cheapest paths). See data/lib.py for the registry."""
import heapq
import sys
from functools import lru_cache
from itertools import product

from lib import add, rnd, CHECKS, VALIDATE, gen_arr  # noqa: F401

sys.setrecursionlimit(20000)
MOD = 10 ** 9 + 7
TOPIC = "Dynamic Programming"


# ---------------------------------------------------------------- EASY

add(
    id="rabbit-pairs-litter-size", title="Rabbit Pairs With Litter Size", diff="Easy", topic=TOPIC,
    fn="rabbitPairs", params=[("months", "int"), ("litter", "int")], ret="int", cmp="exact",
    desc="<p>In month 1 you own a single newborn pair of rabbits. Rabbits never die. A pair born in month <code>t</code> gives birth to <code>litter</code> brand-new pairs in <strong>every</strong> month from month <code>t + 2</code> onwards (so a pair needs two months before its first litter).</p><p>Return how many pairs exist in month <code>months</code>, modulo <code>1,000,000,007</code>.</p><p>Example: with <code>litter = 2</code> the pair counts for months 1 to 5 are 1, 1, 3, 5, 11, so <code>rabbitPairs(5, 2) = 11</code>.</p>",
    constraints=["1 &le; months &le; 100,000", "1 &le; litter &le; 1,000"],
    hints=["Write the pair counts for the first few months with litter = 1 and with litter = 2. Do you recognise the pattern?",
           "Every pair alive last month is still alive. New pairs are born only from pairs that were already alive two months ago.",
           "Let a(m) be the number of pairs in month m: a(1) = a(2) = 1 and a(m) = a(m-1) + litter * a(m-2). Keep two rolling values and reduce modulo 1,000,000,007 each step."],
    editorial=["Split the pairs of month m in two groups. Everybody who lived in month m-1 is still there, giving <code>a(m-1)</code>. The newborns of month m come from pairs born in month m-2 or earlier, that is from the <code>a(m-2)</code> pairs alive two months ago, each producing <code>litter</code> pairs. So <code>a(m) = a(m-1) + litter * a(m-2)</code> with <code>a(1) = a(2) = 1</code>. With <code>litter = 1</code> this is the Fibonacci sequence.",
               "Each term depends only on the previous two, so two variables suffice. Reduce modulo 1,000,000,007 after every step; <code>litter * a</code> stays below about 10<sup>12</sup>, which needs a 64-bit integer in languages with fixed-width types. Time O(months), space O(1)."],
    time="O(months)", space="O(1)",
    solution='''def rabbitPairs(months, litter):
    M = 1000000007
    prev, cur = 0, 1          # a(0) = 0 makes a(2) = a(1) + litter * a(0) = 1
    for _ in range(months - 1):
        prev, cur = cur, (cur + litter * prev) % M
    return cur
''',
    tests=[[1, 1], [1, 1000], [2, 5], [3, 3], [5, 2], [6, 1], [10, 1], [10, 7], [30, 1000], [47, 1], [100, 3], [5000, 999],
           [99999, 1], [100000, 1000]],
)


def _brute_rabbits(months, litter):
    born = [1]            # born[i] = number of pairs born in month i + 1
    for m in range(2, months + 1):
        new = litter * sum(born[:m - 2]) if m >= 3 else 0
        born.append(new)
    return sum(born) % MOD


def _v_rabbits(tests):
    for t in tests:
        m, k = t["args"]
        assert 1 <= m <= 100000 and 1 <= k <= 1000


CHECKS["rabbit-pairs-litter-size"] = (_brute_rabbits, lambda r: [r.randint(1, 18), r.randint(1, 6)], "exact")
VALIDATE["rabbit-pairs-litter-size"] = _v_rabbits

# ------------------------------------------------------------------

_r = rnd(8102)
_fr1 = [_r.randint(0, 10000) for _ in range(5000)]
_fr2 = [10000 if i % 2 == 0 else 0 for i in range(4000)]
_fr3 = sorted(_r.randint(0, 10000) for _ in range(3000))
_fr4 = [_r.randint(0, 3) * 2500 for _ in range(5000)]

add(
    id="frog-jump-min-energy", title="Frog Crossing the Stones", diff="Easy", topic=TOPIC,
    fn="frogMinEnergy", params=[("heights", "int[]")], ret="int", cmp="exact",
    desc="<p>A frog sits on the first of several stones in a row; <code>heights[i]</code> is the height of stone <code>i</code>. In one jump the frog moves to the next stone or skips one stone (from index <code>i</code> to <code>i + 1</code> or <code>i + 2</code>). A jump from stone <code>i</code> to stone <code>j</code> costs <code>|heights[i] - heights[j]|</code> energy.</p><p>Return the minimum total energy needed to reach the last stone. If there is only one stone the answer is <code>0</code>.</p><p>Example: for <code>[10, 30, 40, 20]</code> the best route is 10 &rarr; 30 &rarr; 20 with cost 20 + 10 = 30.</p>",
    constraints=["1 &le; heights.length &le; 10,000", "0 &le; heights[i] &le; 10,000"],
    hints=["Think about the final jump: the frog lands on the last stone coming from one of two stones.",
           "Let best(i) be the least energy to reach stone i. Then best(i) = min(best(i-1) + |h[i]-h[i-1]|, best(i-2) + |h[i]-h[i-2]|).",
           "best(0) = 0 and best(1) = |h[1] - h[0]|. Only the last two values of best are ever needed, so two variables are enough."],
    editorial=["Let <code>best(i)</code> be the minimum energy to stand on stone i. The frog arrives at stone i either from i-1 or from i-2, and whatever happened before that must itself be optimal, so <code>best(i) = min(best(i-1) + |h[i] - h[i-1]|, best(i-2) + |h[i] - h[i-2]|)</code> with <code>best(0) = 0</code>.",
               "The first stone has no predecessor, so for i = 1 only the first option exists. The answer is <code>best(n-1)</code>. One pass with two rolling variables gives O(n) time and O(1) space. A recursive version without memoisation would take exponential time because the same prefixes are evaluated over and over."],
    time="O(n)", space="O(1)",
    solution='''def frogMinEnergy(heights):
    n = len(heights)
    if n == 1:
        return 0
    prev2, prev1 = 0, abs(heights[1] - heights[0])    # best(0), best(1)
    for i in range(2, n):
        cur = min(prev1 + abs(heights[i] - heights[i - 1]),
                  prev2 + abs(heights[i] - heights[i - 2]))
        prev2, prev1 = prev1, cur
    return prev1
''',
    tests=[[[10, 30, 40, 20]], [[30, 10, 60, 10, 60, 50]], [[5]], [[0, 10000]], [[7, 7, 7, 7]], [[1, 2, 3, 4, 5]],
           [[10, 0, 10, 0, 10]], [[0, 100, 0]], [[8, 1, 9, 1, 9, 1, 9, 1]], [[10000, 0, 10000]],
           [_fr1], [_fr2], [_fr3], [_fr4]],
)


def _brute_frog(h):
    n = len(h)
    best = [10 ** 18]

    def go(i, cost):
        if i == n - 1:
            best[0] = min(best[0], cost)
            return
        for j in (i + 1, i + 2):
            if j < n:
                go(j, cost + abs(h[i] - h[j]))

    go(0, 0)
    return best[0]


def _v_frog(tests):
    for t in tests:
        h = t["args"][0]
        assert 1 <= len(h) <= 10000 and all(0 <= x <= 10000 for x in h)


CHECKS["frog-jump-min-energy"] = (_brute_frog, lambda r: [gen_arr(r, 0, 12, 1, 12)], "exact")
VALIDATE["frog-jump-min-energy"] = _v_frog

# ------------------------------------------------------------------

add(
    id="climb-stairs-with-step-set", title="Climbing With Allowed Step Sizes", diff="Easy", topic=TOPIC,
    fn="countClimbs", params=[("n", "int"), ("steps", "int[]")], ret="int", cmp="exact",
    desc="<p>You want to climb a staircase with <code>n</code> steps starting from the ground. In one move you may climb exactly <code>s</code> steps for any <code>s</code> listed in <code>steps</code>. You must land exactly on step <code>n</code>; overshooting is not allowed.</p><p>Return the number of different sequences of moves that reach step <code>n</code>, modulo <code>1,000,000,007</code>. Different orders count as different sequences.</p><p>Example: <code>n = 4</code>, <code>steps = [1, 3, 4]</code> gives 4 sequences: 1+1+1+1, 1+3, 3+1 and 4.</p>",
    constraints=["1 &le; n &le; 50,000", "1 &le; steps.length &le; 10", "1 &le; steps[i] &le; 100,000 and all values are distinct (not necessarily sorted)"],
    hints=["Look at the last move you make. Which step could you have been standing on before it?",
           "Let ways(i) be the number of sequences that land exactly on step i. Then ways(i) is the sum of ways(i - s) over every allowed s with s &le; i.",
           "Start with ways(0) = 1 (the empty sequence) and compute i = 1..n in order, taking the remainder after each sum."],
    editorial=["Every sequence that reaches step i ends with one move of some size s from the list, and before that move you stood on step <code>i - s</code>. Sequences ending with different last moves are different, and the part before the last move can be any sequence reaching <code>i - s</code>. Hence <code>ways(i) = sum of ways(i - s)</code> over allowed s with <code>s &le; i</code>, and <code>ways(0) = 1</code>.",
               "This is the staircase recurrence with an arbitrary set of step sizes (with <code>[1, 2]</code> it is Fibonacci). The table has n + 1 entries and each costs one addition per allowed step size: O(n &middot; m) time and O(n) space, where m is the number of step sizes. Step sizes larger than n simply never apply."],
    time="O(n * m)", space="O(n)",
    solution='''def countClimbs(n, steps):
    M = 1000000007
    ways = [0] * (n + 1)
    ways[0] = 1
    for i in range(1, n + 1):
        total = 0
        for s in steps:
            if s <= i:
                total += ways[i - s]
        ways[i] = total % M
    return ways[n]
''',
    tests=[[4, [1, 3, 4]], [1, [1]], [1, [2]], [5, [1, 2]], [6, [2]], [7, [2]], [10, [3, 5]], [8, [4, 1, 2]], [12, [1, 2, 3]],
           [20, [7, 100000]], [30, [1, 2, 3, 4, 5]], [50000, [1, 2]], [50000, [1, 5, 10, 25]], [49999, [2, 3, 7, 11, 13, 17, 19, 23, 29, 31]]],
)


def _brute_steps(n, steps):
    @lru_cache(maxsize=None)
    def go(rem):
        if rem == 0:
            return 1
        return sum(go(rem - s) for s in steps if s <= rem)

    return go(n) % MOD


def _gen_steps(r):
    return [r.randint(1, 14), r.sample(range(1, 9), r.randint(1, 4))]


def _v_steps(tests):
    for t in tests:
        n, s = t["args"]
        assert 1 <= n <= 50000 and 1 <= len(s) <= 10
        assert len(set(s)) == len(s) and all(1 <= x <= 100000 for x in s)


CHECKS["climb-stairs-with-step-set"] = (_brute_steps, _gen_steps, "exact")
VALIDATE["climb-stairs-with-step-set"] = _v_steps


# ---------------------------------------------------------------- MEDIUM

add(
    id="domino-tromino-tiling-count", title="Tiling a Two-Row Board", diff="Medium", topic=TOPIC,
    fn="countTilings", params=[("n", "int")], ret="int", cmp="exact",
    desc="<p>You have a board with 2 rows and <code>n</code> columns. You may cover it completely, without overlap, using two kinds of tiles: the <em>domino</em>, a 2&times;1 rectangle that may be placed horizontally or vertically, and the <em>L-tromino</em>, which covers three cells of a 2&times;2 block and may be rotated in any of its 4 ways. Every cell must be covered and tiles may not stick out of the board.</p><p>Two tilings are different if some pair of adjacent cells is covered by the same tile in one tiling but not in the other. Return the number of tilings modulo <code>1,000,000,007</code>.</p><p>Example: <code>n = 3</code> gives 5 tilings, <code>n = 4</code> gives 11.</p>",
    constraints=["1 &le; n &le; 100,000"],
    hints=["Draw the first column of a finished tiling. Which tiles can cover its cells?",
           "A vertical domino closes one column (f(n-1)); two horizontal dominoes close two columns (f(n-2)). What about the trominoes? A tromino leaves one cell sticking out, which forces a partner tile.",
           "Every tromino 'bump' must be filled by a matching tromino or by a chain of horizontal dominoes ending in a tromino. These mirror-image shapes give f(n) = 2 &middot; f(n-1) + f(n-3), with f(0) = 1, f(1) = 1, f(2) = 2."],
    editorial=["Let <code>f(n)</code> be the number of tilings of a 2&times;n board. Look at the leftmost column. A vertical domino covers it and leaves a 2&times;(n-1) board: f(n-1) ways. Two horizontal dominoes stacked cover two columns: f(n-2) ways. If a tromino covers one of the two left cells, a cell in the next column is also covered, and the board's boundary becomes uneven (a 'staircase' edge). That ragged edge can only be closed by a tromino in the mirrored orientation, or by a run of horizontal dominoes on one row followed by a closing tromino; either way it eventually returns to a flat edge after k &ge; 3 columns, in exactly 2 ways for each k (one for the top-first and one for the bottom-first shape).",
               "This gives <code>f(n) = f(n-1) + f(n-2) + 2 &middot; (f(n-3) + f(n-4) + ... + f(0))</code>. Subtracting the same equation for n-1 telescopes the sum and leaves <code>f(n) = 2 &middot; f(n-1) + f(n-3)</code>, with <code>f(0) = 1</code>, <code>f(1) = 1</code>, <code>f(2) = 2</code> (check: f(3) = 2&middot;2 + 1 = 5, f(4) = 2&middot;5 + 1 = 11). Three rolling variables and the usual modulo reduction give O(n) time and O(1) space."],
    time="O(n)", space="O(1)",
    solution='''def countTilings(n):
    M = 1000000007
    f = [1, 1, 2]
    if n < 3:
        return f[n]
    a, b, c = 1, 1, 2          # f(k-3), f(k-2), f(k-1)
    for _ in range(3, n + 1):
        a, b, c = b, c, (2 * c + a) % M
    return c
''',
    tests=[[1], [2], [3], [4], [5], [6], [7], [10], [20], [30], [31], [60], [1000], [99999], [100000]],
)


def _brute_tiling(n):
    # fill the first free cell (column-major) with every tile that fits; cells are (row, col)
    shapes = [
        [(0, 0), (1, 0)], [(0, 0), (0, 1)],                                  # dominoes
        [(0, 0), (0, 1), (1, 0)], [(0, 0), (0, 1), (1, 1)],                  # L-trominoes anchored at first cell
        [(0, 0), (1, 0), (1, 1)], [(0, 0), (-1, 1), (0, 1)],
    ]
    grid = [[False] * n for _ in range(2)]
    memo = {}

    def first_free():
        for c in range(n):
            for r in range(2):
                if not grid[r][c]:
                    return r, c
        return None

    def go():
        pos = first_free()
        if pos is None:
            return 1
        r0, c0 = pos
        key = (r0, c0, tuple(grid[r][c] for c in range(c0, min(n, c0 + 3)) for r in range(2)))
        if key in memo:
            return memo[key]
        total = 0
        for sh in shapes:
            cells = [(r0 + dr, c0 + dc) for dr, dc in sh]
            if all(0 <= r < 2 and 0 <= c < n and not grid[r][c] for r, c in cells):
                for r, c in cells:
                    grid[r][c] = True
                total += go()
                for r, c in cells:
                    grid[r][c] = False
        memo[key] = total
        return total

    return go() % MOD


def _v_tiling(tests):
    for t in tests:
        assert 1 <= t["args"][0] <= 100000


CHECKS["domino-tromino-tiling-count"] = (_brute_tiling, lambda r: [r.randint(1, 11)], "exact")
VALIDATE["domino-tromino-tiling-count"] = _v_tiling

# ------------------------------------------------------------------

add(
    id="paint-fence-no-three-same", title="Fence Without Three in a Row", diff="Medium", topic=TOPIC,
    fn="countFencePaintings", params=[("posts", "int"), ("colors", "int")], ret="int", cmp="exact",
    desc="<p>A fence has <code>posts</code> posts in a row. Each post is painted with one of <code>colors</code> available colors. To keep the fence interesting, <strong>no three consecutive posts may share the same color</strong> (two in a row are fine).</p><p>Return the number of valid paintings, modulo <code>1,000,000,007</code>.</p><p>Example: <code>posts = 3</code>, <code>colors = 2</code> gives 6 (the 8 paintings minus the all-same ones <code>AAA</code> and <code>BBB</code>).</p>",
    constraints=["1 &le; posts &le; 100,000", "1 &le; colors &le; 1,000,000"],
    hints=["Count by the end of the fence. A valid painting either ends with two equal colors or with two different ones.",
           "Track same = paintings whose last two posts match, diff = paintings whose last two posts differ.",
           "Next post: new_same = diff (copy the last color, allowed only if the previous two differed); new_diff = (same + diff) * (colors - 1). Start with same = 0, diff = colors for one post."],
    editorial=["After painting i posts, classify each valid painting by whether the last two posts have equal colors (<code>same</code>) or different colors (<code>diff</code>). To extend by one post: repeating the last color is legal only if the last two posts differ, otherwise we would get three in a row, so <code>new_same = diff</code>. Choosing a different color is always legal, in <code>colors - 1</code> ways, from either state, so <code>new_diff = (same + diff) * (colors - 1)</code>.",
               "With one post there are <code>colors</code> paintings and no pair yet: <code>(same, diff) = (0, colors)</code>. The answer is <code>same + diff</code> after the last post, modulo 1,000,000,007. When there is a single color the formula correctly yields 0 for three or more posts. Time O(posts), space O(1)."],
    time="O(posts)", space="O(1)",
    solution='''def countFencePaintings(posts, colors):
    M = 1000000007
    same, diff = 0, colors % M
    for _ in range(posts - 1):
        same, diff = diff, (same + diff) * (colors - 1) % M
    return (same + diff) % M
''',
    tests=[[1, 1], [1, 5], [2, 1], [2, 3], [3, 1], [3, 2], [4, 2], [5, 3], [6, 2], [10, 1], [10, 4], [50, 7], [1000, 1000000],
           [100000, 2], [100000, 1000000], [99999, 999983]],
)


def _brute_fence(posts, colors):
    if colors ** posts <= 300000:
        cnt = 0
        for combo in product(range(colors), repeat=posts):
            if all(not (combo[i] == combo[i + 1] == combo[i + 2]) for i in range(posts - 2)):
                cnt += 1
        return cnt % MOD
    # too many paintings to list: count (last color, length of the final run) states explicitly
    cur = {(c, 1): 1 for c in range(colors)}
    for _ in range(posts - 1):
        nxt = {}
        for (c, run), v in cur.items():
            for d in range(colors):
                key = (d, run + 1) if d == c else (d, 1)
                if key[1] <= 2:
                    nxt[key] = nxt.get(key, 0) + v
        cur = nxt
    return sum(cur.values()) % MOD


def _v_fence(tests):
    for t in tests:
        p, c = t["args"]
        assert 1 <= p <= 100000 and 1 <= c <= 1000000


CHECKS["paint-fence-no-three-same"] = (_brute_fence, lambda r: [r.randint(1, 8), r.randint(1, 4)], "exact")
VALIDATE["paint-fence-no-three-same"] = _v_fence

# ------------------------------------------------------------------

_r = rnd(8106)
_fk1 = [_r.randint(0, 10000) for _ in range(5000)]
_fk2 = [_r.randint(0, 10000) for _ in range(4000)]
_fk3 = [i * 3 % 10001 for i in range(4500)]
_fk4 = [_r.choice([0, 10000]) for _ in range(3000)]

add(
    id="frog-jump-up-to-k-min-energy", title="Frog Crossing With Long Jumps", diff="Medium", topic=TOPIC,
    fn="frogMinEnergyK", params=[("heights", "int[]"), ("k", "int")], ret="int", cmp="exact",
    desc="<p>A frog sits on the first stone of a row; <code>heights[i]</code> is the height of stone <code>i</code>. In one jump the frog may move forward by <strong>any distance from 1 to <code>k</code></strong> stones, i.e. from index <code>i</code> to any <code>j</code> with <code>i &lt; j &le; i + k</code> that exists. A jump from stone <code>i</code> to stone <code>j</code> costs <code>|heights[i] - heights[j]|</code> energy.</p><p>Return the minimum total energy to reach the last stone (<code>0</code> if there is only one stone).</p><p>Example: <code>heights = [10, 30, 40, 50, 20]</code>, <code>k = 3</code> gives 30 via 10 &rarr; 30 &rarr; 20.</p>",
    constraints=["1 &le; heights.length &le; 5,000", "1 &le; k &le; 100", "0 &le; heights[i] &le; 10,000"],
    hints=["With k = 2 the answer needs only the previous two states. What changes for larger k?",
           "Let best(i) be the least energy to reach stone i. The previous stone of the optimal route is some j in [i - k, i - 1].",
           "best(i) = min over j in [max(0, i-k), i-1] of best(j) + |h[i] - h[j]|, with best(0) = 0. Loop over at most k candidates for each i."],
    editorial=["The last jump into stone i starts at some stone j with <code>i - k &le; j &le; i - 1</code>, and the route up to j must be optimal for j. Therefore <code>best(i) = min(best(j) + |h[i] - h[j]|)</code> over those j, and <code>best(0) = 0</code>. The answer is <code>best(n-1)</code>.",
               "Each of the n states examines at most k predecessors: O(n &middot; k) time and O(n) space (the full table is kept because any of the last k values may be needed). The absolute difference depends on both ends of the jump, so unlike plain 'sum of the previous k' recurrences it cannot be sped up with a running window; for these constraints n &middot; k &le; 500,000 operations."],
    time="O(n * k)", space="O(n)",
    solution='''def frogMinEnergyK(heights, k):
    n = len(heights)
    INF = float("inf")
    best = [0] + [INF] * (n - 1)
    for i in range(1, n):
        hi = heights[i]
        b = INF
        for j in range(max(0, i - k), i):
            c = best[j] + abs(hi - heights[j])
            if c < b:
                b = c
        best[i] = b
    return best[n - 1]
''',
    tests=[[[10, 30, 40, 50, 20], 3], [[10, 30, 40, 50, 20], 1], [[5], 4], [[0, 10000], 1], [[3, 8, 3], 2], [[3, 8, 3], 1],
           [[1, 9, 2, 9, 3, 9, 4], 2], [[1, 9, 2, 9, 3, 9, 4], 6], [[7, 7, 7, 7, 7], 3], [[0, 5, 10, 15, 20], 4],
           [_fk1, 100], [_fk2, 1], [_fk3, 37], [_fk4, 2], [_fk1[:2500], 60]],
)


def _brute_frogk(h, k):
    n = len(h)
    best = [10 ** 18]

    def go(i, cost):
        if i == n - 1:
            best[0] = min(best[0], cost)
            return
        for j in range(i + 1, min(n - 1, i + k) + 1):
            go(j, cost + abs(h[i] - h[j]))

    go(0, 0)
    return best[0]


def _gen_frogk(r):
    return [gen_arr(r, 0, 12, 1, 10), r.randint(1, 5)]


def _v_frogk(tests):
    for t in tests:
        h, k = t["args"]
        assert 1 <= len(h) <= 5000 and 1 <= k <= 100 and all(0 <= x <= 10000 for x in h)


CHECKS["frog-jump-up-to-k-min-energy"] = (_brute_frogk, _gen_frogk, "exact")
VALIDATE["frog-jump-up-to-k-min-energy"] = _v_frogk

# ------------------------------------------------------------------

add(
    id="climb-stairs-up-to-k-steps", title="Climbing With Any Jump up to K", diff="Medium", topic=TOPIC,
    fn="countClimbsUpToK", params=[("n", "int"), ("k", "int")], ret="int", cmp="exact",
    desc="<p>You climb a staircase of <code>n</code> steps starting from the ground. In one move you may climb any number of steps from <code>1</code> to <code>k</code> (inclusive). You must land exactly on step <code>n</code>.</p><p>Return the number of different move sequences that take you to the top, modulo <code>1,000,000,007</code>. Different orders count as different sequences.</p><p>Examples: <code>n = 4, k = 2</code> gives 5, <code>n = 4, k = 3</code> gives 7.</p>",
    constraints=["1 &le; n &le; 100,000", "1 &le; k &le; 100,000"],
    hints=["The count for step i is the sum of the counts of the k steps below it. Computing that sum from scratch costs O(k) per step, which is too slow when k is large.",
           "Neighbouring windows share almost all their elements: the window for i + 1 is the window for i with one value added and one removed.",
           "Keep a running sum of ways over the last k steps. When moving to the next step add the newest value and subtract the one that just fell out of the window (remember the modulus)."],
    editorial=["Define <code>ways(i)</code> as the number of sequences landing exactly on step i, with <code>ways(0) = 1</code>. Then <code>ways(i) = ways(i-1) + ... + ways(i-k)</code> (terms with a negative index are 0). Evaluating every sum naively costs O(n &middot; k), up to 10<sup>10</sup> here.",
               "Note that <code>ways(i+1) = ways(i) + (ways(i) - ways(i-k))</code>: the window sum for i+1 is the window sum for i plus the new value minus the value that left. Keeping the window sum <code>S</code> and updating it once per step gives O(n) time and O(n) space (the table is needed to know which value leaves the window). Apply the modulus to the subtraction carefully so S stays non-negative."],
    time="O(n)", space="O(n)",
    solution='''def countClimbsUpToK(n, k):
    M = 1000000007
    ways = [0] * (n + 1)
    ways[0] = 1
    window = 1                    # sum of ways[i-k .. i-1] for the current i, starting at i = 1
    for i in range(1, n + 1):
        ways[i] = window
        window = (window + ways[i] - (ways[i - k] if i - k >= 0 else 0)) % M
    return ways[n]
''',
    tests=[[4, 2], [4, 3], [1, 1], [1, 100000], [5, 1], [2, 1], [3, 5], [10, 3], [20, 20], [30, 4], [100, 50],
           [100000, 1], [100000, 2], [100000, 100000], [100000, 777], [99999, 50000]],
)


def _brute_climbk(n, k):
    ways = [1] + [0] * n
    for i in range(1, n + 1):
        ways[i] = sum(ways[i - s] for s in range(1, min(k, i) + 1))
    return ways[n] % MOD


def _v_climbk(tests):
    for t in tests:
        n, k = t["args"]
        assert 1 <= n <= 100000 and 1 <= k <= 100000


CHECKS["climb-stairs-up-to-k-steps"] = (_brute_climbk, lambda r: [r.randint(1, 40), r.randint(1, 45)], "exact")
VALIDATE["climb-stairs-up-to-k-steps"] = _v_climbk

# ------------------------------------------------------------------

add(
    id="min-cost-reduce-to-one", title="Cheapest Way Down to One", diff="Medium", topic=TOPIC,
    fn="minCostToOne", params=[("n", "int"), ("a", "int"), ("b", "int"), ("c", "int")], ret="int", cmp="exact",
    desc="<p>Start with the positive integer <code>n</code> and reduce it to <code>1</code> using these operations, each of which may be used any number of times:</p><ul><li>subtract 1, costing <code>a</code>;</li><li>divide by 2 (only when the current value is even), costing <code>b</code>;</li><li>divide by 3 (only when the current value is a multiple of 3), costing <code>c</code>.</li></ul><p>Return the minimum total cost. If <code>n</code> is already 1 the answer is 0.</p><p>Example: <code>n = 10</code>, <code>a = b = c = 1</code>: 10 &rarr; 9 &rarr; 3 &rarr; 1 costs 3. Greedily dividing whenever possible is not always optimal.</p>",
    constraints=["1 &le; n &le; 100,000", "1 &le; a, b, c &le; 1,000"],
    hints=["Try small n by hand with a = b = c = 1 and check whether always dividing as soon as you can is best. (It is not: with 10, subtracting first wins.)",
           "Every operation makes the number smaller, so the cheapest cost for a value depends only on the cheapest costs of smaller values.",
           "f(1) = 0 and f(m) = min(f(m-1) + a, f(m/2) + b if m is even, f(m/3) + c if m is a multiple of 3). Fill f from 2 up to n."],
    editorial=["Let <code>f(m)</code> be the cheapest cost to turn m into 1. The first operation applied to m produces m-1, m/2 or m/3 (when legal), and the rest of the route is an optimal route from that value. Hence <code>f(m) = min(f(m-1) + a, f(m/2) + b, f(m/3) + c)</code> with <code>f(1) = 0</code>, where the last two options exist only when the division is exact.",
               "Greedy choices fail because the cheapest first step depends on what is reachable afterwards: for 10 the division by 2 leads to 5, which then needs a subtraction, while the subtraction to 9 unlocks two divisions by 3. Filling the table in increasing order takes O(n) time and O(n) space. The largest possible answer is under 10<sup>8</sup>, so it fits in 32 bits."],
    time="O(n)", space="O(n)",
    solution='''def minCostToOne(n, a, b, c):
    f = [0] * (n + 1)
    for m in range(2, n + 1):
        best = f[m - 1] + a
        if m % 2 == 0 and f[m // 2] + b < best:
            best = f[m // 2] + b
        if m % 3 == 0 and f[m // 3] + c < best:
            best = f[m // 3] + c
        f[m] = best
    return f[n]
''',
    tests=[[10, 1, 1, 1], [1, 5, 5, 5], [2, 1, 1, 1], [2, 9, 4, 3], [3, 1, 5, 2], [7, 1, 1, 1], [10, 1, 5, 1], [27, 2, 8, 3],
           [100, 3, 4, 5], [64, 1, 1000, 1000], [1000, 7, 2, 9], [99999, 1, 1, 1], [100000, 1000, 1, 1], [100000, 1, 1000, 1000],
           [77777, 13, 400, 250]],
)


def _brute_cost1(n, a, b, c):
    dist = {n: 0}
    heap = [(0, n)]
    while heap:
        d, m = heapq.heappop(heap)
        if m == 1:
            return d
        if d > dist.get(m, 1 << 60):
            continue
        for nxt, w in ((m - 1, a), (m // 2 if m % 2 == 0 else None, b), (m // 3 if m % 3 == 0 else None, c)):
            if nxt is not None and nxt >= 1 and d + w < dist.get(nxt, 1 << 60):
                dist[nxt] = d + w
                heapq.heappush(heap, (d + w, nxt))
    return dist[1]


def _v_cost1(tests):
    for t in tests:
        n, a, b, c = t["args"]
        assert 1 <= n <= 100000 and all(1 <= x <= 1000 for x in (a, b, c))


CHECKS["min-cost-reduce-to-one"] = (_brute_cost1, lambda r: [r.randint(1, 300), r.randint(1, 12), r.randint(1, 12), r.randint(1, 12)], "exact")
VALIDATE["min-cost-reduce-to-one"] = _v_cost1

# ------------------------------------------------------------------

add(
    id="stairs-no-repeated-step-size", title="Stairs Without Repeating a Move", diff="Medium", topic=TOPIC,
    fn="countVariedClimbs", params=[("n", "int"), ("steps", "int[]")], ret="int", cmp="exact",
    desc="<p>You climb a staircase of <code>n</code> steps from the ground. Each move climbs exactly <code>s</code> steps for some <code>s</code> in <code>steps</code>, but you are <strong>never allowed to use the same step size in two consecutive moves</strong> (for example <code>2</code> followed by <code>2</code> is forbidden, while <code>2, 1, 2</code> is fine). You must land exactly on step <code>n</code>.</p><p>Return the number of valid move sequences modulo <code>1,000,000,007</code>.</p><p>Example: <code>n = 4</code>, <code>steps = [1, 2, 3]</code> gives 3 sequences: 1+3, 3+1 and 1+2+1.</p>",
    constraints=["1 &le; n &le; 30,000", "1 &le; steps.length &le; 6", "1 &le; steps[i] &le; 100,000 and all values are distinct"],
    hints=["A state of just 'the current step' is not enough: you also need to know the size of the last move.",
           "Let dp[i][j] be the number of valid sequences that reach step i with last move steps[j]. Which sequences can come before such a move?",
           "dp[i][j] = total[i - s_j] - dp[i - s_j][j], where total[x] = sum over j of dp[x][j] and total[0] = 1 (the empty sequence, which has no last move)."],
    editorial=["Add the size of the last move to the state. Let <code>dp[i][j]</code> be the number of valid sequences ending on step i whose last move is <code>s_j</code>, and <code>total[i]</code> the sum over j. A sequence ending with move s_j on step i is a valid sequence ending on step <code>i - s_j</code> followed by s_j, and the only forbidden case is when that earlier sequence also ended with s_j.",
               "So <code>dp[i][j] = total[i - s_j] - dp[i - s_j][j]</code> (for <code>i &ge; s_j</code>), with <code>total[0] = 1</code> and <code>dp[0][j] = 0</code>, because the empty sequence has no previous move. The answer is <code>total[n]</code>. Subtracting rather than summing over all other j keeps each state O(1), for O(n &middot; m) time and O(n &middot; m) space; keep every value reduced modulo 1,000,000,007."],
    time="O(n * m)", space="O(n * m)",
    solution='''def countVariedClimbs(n, steps):
    M = 1000000007
    m = len(steps)
    dp = [[0] * (n + 1) for _ in range(m)]
    total = [0] * (n + 1)
    total[0] = 1
    for i in range(1, n + 1):
        t = 0
        for j in range(m):
            s = steps[j]
            if s <= i:
                v = (total[i - s] - dp[j][i - s]) % M
                dp[j][i] = v
                t += v
        total[i] = t % M
    return total[n]
''',
    tests=[[4, [1, 2, 3]], [1, [1]], [2, [1]], [2, [2, 5]], [3, [1, 2]], [5, [1, 2]], [6, [3, 1, 2]], [7, [2]], [9, [1, 2, 3]],
           [15, [1, 4, 5]], [40, [1, 2, 3, 4]], [30000, [1, 2, 3]], [30000, [1, 2, 3, 4, 5, 6]], [29999, [5, 1, 100000, 17, 3]]],
)


def _brute_varied(n, steps):
    @lru_cache(maxsize=None)
    def go(rem, last):
        if rem == 0:
            return 1
        return sum(go(rem - s, s) for s in steps if s <= rem and s != last)

    return go(n, None) % MOD


def _gen_varied(r):
    return [r.randint(1, 14), r.sample(range(1, 7), r.randint(1, 4))]


def _v_varied(tests):
    for t in tests:
        n, s = t["args"]
        assert 1 <= n <= 30000 and 1 <= len(s) <= 6
        assert len(set(s)) == len(s) and all(1 <= x <= 100000 for x in s)


CHECKS["stairs-no-repeated-step-size"] = (_brute_varied, _gen_varied, "exact")
VALIDATE["stairs-no-repeated-step-size"] = _v_varied


# ---------------------------------------------------------------- HARD

add(
    id="distant-term-of-linear-recurrence", title="Distant Term of a Recurrence", diff="Hard", topic=TOPIC,
    fn="recurrenceTerm", params=[("coefs", "int[]"), ("init", "int[]"), ("n", "int")], ret="int", cmp="exact",
    desc="<p>A sequence <code>a</code> is defined by <code>d = coefs.length</code> initial terms <code>a[0..d-1] = init</code> and, for every index <code>i &ge; d</code>,</p><p><code>a[i] = coefs[0]*a[i-1] + coefs[1]*a[i-2] + ... + coefs[d-1]*a[i-d]</code>, all taken modulo <code>1,000,000,007</code>.</p><p>Return <code>a[n]</code>. The index <code>n</code> can be as large as about two billion, so you cannot generate the terms one by one.</p><p>Example: <code>coefs = [1, 1]</code>, <code>init = [0, 1]</code> is the Fibonacci sequence, so <code>n = 10</code> gives 55.</p>",
    constraints=["1 &le; coefs.length = init.length &le; 8", "0 &le; coefs[i], init[i] &lt; 1,000,000,007", "0 &le; n &le; 2,147,483,647"],
    hints=["For small n you just iterate the recurrence. Why is that too slow when n is about 2&middot;10<sup>9</sup>?",
           "The window of the last d terms is a vector, and one step of the recurrence multiplies that vector by a fixed d &times; d matrix.",
           "So the window after n - d + 1 steps is the matrix to that power times the starting window. Compute the matrix power by repeated squaring, with every product reduced modulo 1,000,000,007."],
    editorial=["Write the state as the vector <code>v_i = (a[i], a[i-1], ..., a[i-d+1])</code>. The recurrence says <code>v_{i+1} = T &middot; v_i</code> where the first row of T is the list of coefficients and the remaining rows shift the window down (a sub-diagonal of ones). Starting from <code>v_{d-1} = (init[d-1], ..., init[0])</code> we get <code>v_n = T^(n-d+1) &middot; v_{d-1}</code>, and <code>a[n]</code> is the first component.",
               "If <code>n &lt; d</code> the answer is simply <code>init[n]</code>. Otherwise raise T to the power <code>n - d + 1</code> by binary exponentiation: about 31 squarings and at most 31 extra multiplications of d &times; d matrices, each O(d<sup>3</sup>). Total O(d<sup>3</sup> log n) time and O(d<sup>2</sup>) space. Products of two residues reach about 10<sup>18</sup>, so Python integers are fine but fixed-width languages need 64-bit unsigned arithmetic or careful reduction. (Kitamasa's polynomial method improves this to O(d<sup>2</sup> log n), which is overkill here.)"],
    time="O(d^3 log n)", space="O(d^2)",
    solution='''def recurrenceTerm(coefs, init, n):
    M = 1000000007
    d = len(coefs)
    if n < d:
        return init[n] % M

    def mul(A, B):
        return [[sum(A[i][k] * B[k][j] for k in range(d)) % M for j in range(d)] for i in range(d)]

    T = [[0] * d for _ in range(d)]
    T[0] = [c % M for c in coefs]
    for i in range(1, d):
        T[i][i - 1] = 1
    R = [[int(i == j) for j in range(d)] for i in range(d)]
    e = n - d + 1
    while e:
        if e & 1:
            R = mul(R, T)
        T = mul(T, T)
        e >>= 1
    v = [init[d - 1 - i] % M for i in range(d)]          # (a[d-1], ..., a[0])
    return sum(R[0][j] * v[j] for j in range(d)) % M
''',
    tests=[[[1, 1], [0, 1], 10], [[1, 1], [0, 1], 0], [[1, 1], [0, 1], 1], [[2], [3], 5], [[1, 1, 1], [0, 1, 1], 20],
           [[3, 0, 5], [1, 2, 3], 2], [[0, 1], [4, 9], 7], [[1, 1], [0, 1], 2147483647], [[2, 1], [0, 1], 1000000],
           [[1, 1, 1], [0, 1, 1], 2000000000], [[5, 4, 3, 2, 1, 0, 7, 8], [1, 2, 3, 4, 5, 6, 7, 8], 1999999999],
           [[1000000006, 1000000006], [1, 1000000006], 123456789], [[0, 0, 0, 1], [9, 8, 7, 6], 2147483646],
           [[1, 1, 1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1, 1, 1], 1500000000]],
)


def _brute_recur(coefs, init, n):
    d = len(coefs)
    a = [x % MOD for x in init]
    while len(a) <= n:
        a.append(sum(coefs[j] * a[-1 - j] for j in range(d)) % MOD)
    return a[n]


def _gen_recur(r):
    d = r.randint(1, 5)
    hi = r.choice([3, 10, MOD - 1])
    return [[r.randint(0, hi) for _ in range(d)], [r.randint(0, hi) for _ in range(d)], r.randint(0, 40)]


def _v_recur(tests):
    for t in tests:
        c, a, n = t["args"]
        assert 1 <= len(c) == len(a) <= 8
        assert all(0 <= x < MOD for x in c + a) and 0 <= n <= 2147483647


CHECKS["distant-term-of-linear-recurrence"] = (_brute_recur, _gen_recur, "exact")
VALIDATE["distant-term-of-linear-recurrence"] = _v_recur

# ------------------------------------------------------------------

_r = rnd(8111)

add(
    id="ways-to-sum-distinct-fibonacci", title="Sums of Distinct Fibonacci Numbers", diff="Hard", topic=TOPIC, tier="extra",
    fn="countFibSums", params=[("n", "int")], ret="int", cmp="exact",
    desc="<p>Consider the Fibonacci numbers <code>1, 2, 3, 5, 8, 13, ...</code> (each is the sum of the two before it; the value 1 is listed once). Count the ways to write <code>n</code> as a sum of <strong>distinct</strong> numbers from this list, where two ways are different if the sets of numbers used are different (order is irrelevant).</p><p>Examples: <code>n = 8</code> has 3 ways (8, 5+3, 5+2+1); <code>n = 4</code> has 1 way (3+1); <code>n = 6</code> has 2 ways (5+1, 3+2+1).</p>",
    constraints=["1 &le; n &le; 2,000,000,000"],
    hints=["Only about 45 Fibonacci numbers are at most 2&middot;10<sup>9</sup>. A subset DP over sums is impossible for such n, but a search over the 45 numbers might still be small.",
           "Process Fibonacci numbers from the largest to the smallest, deciding take / skip while tracking the remaining target.",
           "Prune with a bound: the sum of the Fibonacci numbers 1..F_i equals F_{i+2} - 2 (for this list), so if the remaining target exceeds the sum of all unused smaller numbers the branch is dead. With this bound and memoisation on (index, remaining) only about two remainders stay alive per level."],
    editorial=["Let the list be <code>F_1 = 1, F_2 = 2, F_3 = 3, F_4 = 5, ...</code> and <code>pre[i]</code> the sum of the first i of them. Define <code>count(i, r)</code> as the number of ways to form r using a subset of <code>F_1..F_i</code>. Then <code>count(i, r) = count(i-1, r) + count(i-1, r - F_i)</code> (the second term only if <code>r &ge; F_i</code>), <code>count(0, 0) = 1</code>, and <code>count(i, r) = 0</code> whenever <code>r &gt; pre[i]</code>.",
               "The bound looks innocent but is what makes this fast. Because each Fibonacci number is less than the sum of all smaller ones plus 2, the only remainders that can still be completed at level i lie in a window of length about <code>F_{i+2}</code> below <code>pre[i]</code>, while taking or skipping F_i changes r by exactly F_i. In practice at most two distinct remainders survive per level, so the memo holds O(log n) states (roughly 90 here). Time O(log n) with memoisation, space O(log n). This also explains why the answer grows only slowly with n."],
    time="O(log n)", space="O(log n)",
    solution='''def countFibSums(n):
    fibs = [1, 2]
    while fibs[-1] + fibs[-2] <= n:
        fibs.append(fibs[-1] + fibs[-2])
    pre = [0]
    for f in fibs:
        pre.append(pre[-1] + f)
    memo = {}

    def count(i, r):
        if r == 0:
            return 1
        if i == 0 or r > pre[i]:
            return 0
        key = (i, r)
        if key in memo:
            return memo[key]
        res = count(i - 1, r)
        if r >= fibs[i - 1]:
            res += count(i - 1, r - fibs[i - 1])
        memo[key] = res
        return res

    return count(len(fibs), n)
''',
    tests=[[1], [2], [3], [4], [6], [8], [10], [13], [20], [100], [987], [1000], [123456], [999999999],
           [1836311902], [1836311903], [2000000000], [_r.randint(10 ** 9, 2 * 10 ** 9)], [_r.randint(10 ** 8, 10 ** 9)]],
)


def _brute_fibsum(n):
    fibs = [1, 2]
    while fibs[-1] + fibs[-2] <= n:
        fibs.append(fibs[-1] + fibs[-2])
    ways = [1] + [0] * n
    for f in fibs:
        for s in range(n, f - 1, -1):
            ways[s] += ways[s - f]
    return ways[n]


def _v_fibsum(tests):
    for t in tests:
        assert 1 <= t["args"][0] <= 2000000000


CHECKS["ways-to-sum-distinct-fibonacci"] = (_brute_fibsum, lambda r: [r.randint(1, 400)], "exact")
VALIDATE["ways-to-sum-distinct-fibonacci"] = _v_fibsum
