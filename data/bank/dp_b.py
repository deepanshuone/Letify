"""Problems: dynamic programming, house-robber family and non-adjacent selection. See data/lib.py for the registry."""
from itertools import combinations

from lib import add, rnd, CHECKS, VALIDATE, gen_arr  # noqa: F401

MOD = 10 ** 9 + 7
TOPIC = "Dynamic Programming"
NEG = -10 ** 18


def _subsets(n):
    """All index subsets of range(n) as sorted tuples (including the empty one)."""
    for m in range(1 << n):
        yield tuple(i for i in range(n) if m >> i & 1)


# ---------------------------------------------------------------- EASY

_r = rnd(8101)
_bp1 = [_r.randint(-1000, 1000) for _ in range(6000)]
_bp2 = [_r.randint(-1000, -1) for _ in range(5000)]
_bp3 = [_r.randint(-300, 1000) if i % 2 == 0 else _r.randint(-1000, 100) for i in range(4000)]

add(
    id="best-non-adjacent-pick", title="Best Non-Adjacent Pick", diff="Easy", topic=TOPIC,
    fn="bestNonAdjacentPick", params=[("nums", "int[]")], ret="int", cmp="exact",
    desc="<p>You must choose <strong>at least one</strong> element of <code>nums</code>, and you may never choose two elements that sit next to each other (indices <code>i</code> and <code>i + 1</code> cannot both be chosen). Return the largest possible sum of the chosen elements.</p><p>Values can be negative. For example, in <code>[2, -1, 5, -4, 3]</code> the best choice is <code>2 + 5 + 3 = 10</code>, while in <code>[-3, -1, -2]</code> the best you can do is pick the single element <code>-1</code>.</p>",
    constraints=["1 &le; nums.length &le; 10,000", "-1,000 &le; nums[i] &le; 1,000", "At least one element must be chosen"],
    hints=["Look at the last element. Either it is part of the selection or it is not. What does each case leave you with?",
           "Let best(i) be the best sum using only the first i elements. Then best(i) = max(best(i-1), best(i-2) + nums[i-1]). Starting from an empty selection (sum 0) lets the DP skip negative numbers for free.",
           "That DP may end with an empty selection, which is not allowed. If the array has at least one positive element, the empty selection can never be the best one. If every element is 0 or negative, the answer is simply the maximum element."],
    editorial=["This is House Robber with two twists: values can be negative, and the selection must not be empty. First handle the twist that makes the answer trivial: if <code>max(nums) &le; 0</code>, adding any second element can only make the sum smaller or equal, so the best choice is the single largest element.",
               "Otherwise some element is positive, so a non-empty selection with a positive sum exists and the classic recurrence <code>take = skip + x, skip = max(take, skip)</code> (which allows the empty selection) returns a positive value that is automatically non-empty. Time O(n), space O(1)."],
    time="O(n)", space="O(1)",
    solution='''def bestNonAdjacentPick(nums):
    top = max(nums)
    if top <= 0:
        return top
    take, skip = 0, 0
    for x in nums:
        take, skip = skip + x, max(take, skip)
    return max(take, skip)
''',
    tests=[[[2, -1, 5, -4, 3]], [[-3, -1, -2]], [[7]], [[-7]], [[0, 0, 0]], [[5, 5]], [[-5, 9, -5]], [[3, -10, 3, -10, 3]],
           [[1, 2, 3, 4, 5, 6]], [[-1, -2, -3, 4, -5]], [[10, -1, -1, 10]], [_bp1], [_bp2], [_bp3]],
)


def _b_bnap(nums):
    n = len(nums)
    best = None
    for s in _subsets(n):
        if not s or any(b - a == 1 for a, b in zip(s, s[1:])):
            continue
        v = sum(nums[i] for i in s)
        if best is None or v > best:
            best = v
    return best


def _v_bnap(tests):
    for t in tests:
        nums = t["args"][0]
        assert 1 <= len(nums) <= 10000 and all(-1000 <= x <= 1000 for x in nums)


CHECKS["best-non-adjacent-pick"] = (_b_bnap, lambda r: [gen_arr(r, -6, 6, 1, 10)], "exact")
VALIDATE["best-non-adjacent-pick"] = _v_bnap

# ------------------------------------------------------------------

_r = rnd(8102)
_nt1 = [_r.randint(0, 1000) for _ in range(8000)]
_nt2 = [1000] * 3000 + [0] * 10 + [999] * 3000
_nt3 = [_r.choice([0, 1, 1000]) for _ in range(5000)]

add(
    id="max-sum-no-three-consecutive-picks", title="Skip One in Every Three", diff="Easy", topic=TOPIC,
    fn="maxSumNoThreeInARow", params=[("nums", "int[]")], ret="int", cmp="exact",
    desc="<p>You may choose any elements of <code>nums</code> as long as you never choose three elements with consecutive indices (<code>i</code>, <code>i + 1</code> and <code>i + 2</code> must not all be chosen). Two chosen neighbours are fine.</p><p>Return the largest possible sum of the chosen elements. Choosing nothing is allowed.</p><p>For example, in <code>[3, 4, 5, 1]</code> the choice <code>4 + 5 + 1</code> is illegal (indices 1, 2, 3 are consecutive), but <code>3 + 5 + 1 = 9</code> and <code>4 + 5 = 9</code> are fine, and 9 is the best possible.</p>",
    constraints=["0 &le; nums.length &le; 10,000", "0 &le; nums[i] &le; 1,000"],
    hints=["Since all values are non-negative, you want to choose as many elements as the rule allows. The rule only cares about how many chosen elements in a row you just made.",
           "Track the length of the current streak of chosen elements: 0, 1 or 2. A streak of 2 forces you to skip the next element.",
           "Keep three values: best sum ending with a skip, with a streak of 1 and with a streak of 2. Choosing x moves streak s to s + 1 (and adds x); skipping resets the streak to 0."],
    editorial=["Let <code>s0, s1, s2</code> be the best sums over the prefix processed so far where the current run of chosen elements at the end has length 0, 1 or 2. Reading element x: <code>new s0 = max(s0, s1, s2)</code> (skip it), <code>new s1 = s0 + x</code> and <code>new s2 = s1 + x</code>. A run of length 2 cannot be extended, which is exactly the forbidden triple.",
               "Start with <code>s0 = 0</code> and the other two impossible. The answer is the maximum of the three at the end. Alternatively the problem can be seen as removing the cheapest set of elements so that every window of three has a removed one, but the three-state DP is simpler. Time O(n), space O(1)."],
    time="O(n)", space="O(1)",
    solution='''def maxSumNoThreeInARow(nums):
    NEG = -10 ** 18
    s0, s1, s2 = 0, NEG, NEG
    for x in nums:
        s0, s1, s2 = max(s0, s1, s2), s0 + x, s1 + x
    return max(s0, s1, s2)
''',
    tests=[[[3, 4, 5, 1]], [[]], [[7]], [[7, 8]], [[1, 1, 1]], [[5, 5, 5, 5]], [[0, 0, 0, 0]], [[9, 1, 9, 1, 9]],
           [[1, 100, 100, 100, 1]], [[4, 4, 4, 4, 4, 4, 4]], [[2, 7, 3, 9, 1, 8]], [_nt1], [_nt2], [_nt3]],
)


def _b_nt(nums):
    n = len(nums)
    best = 0
    for s in _subsets(n):
        ss = set(s)
        if any(i in ss and i + 1 in ss and i + 2 in ss for i in range(n)):
            continue
        best = max(best, sum(nums[i] for i in s))
    return best


def _v_nt(tests):
    for t in tests:
        nums = t["args"][0]
        assert len(nums) <= 10000 and all(0 <= x <= 1000 for x in nums)


CHECKS["max-sum-no-three-consecutive-picks"] = (_b_nt, lambda r: [gen_arr(r, 0, 9, 0, 11)], "exact")
VALIDATE["max-sum-no-three-consecutive-picks"] = _v_nt

# ------------------------------------------------------------------

_r = rnd(8103)
_tn1 = [_r.randint(-1000, 1000) for _ in range(8000)]
_tn2 = [1000, -1000] + [_r.randint(-1000, -900) for _ in range(5000)] + [1000]
_tn3 = [_r.randint(-1000, 1000) for _ in range(3)] + [_r.randint(-5, 5) for _ in range(6000)]

add(
    id="best-two-non-adjacent-sum", title="Best Two Non-Neighbours", diff="Easy", topic=TOPIC,
    fn="bestTwoNonAdjacentSum", params=[("nums", "int[]")], ret="int", cmp="exact",
    desc="<p>Pick exactly two elements of <code>nums</code> whose indices <code>i</code> and <code>j</code> satisfy <code>j - i &ge; 2</code> (they are not the same element and not next to each other). Return the largest possible sum of the two chosen values.</p><p>For example, for <code>[5, 9, 4, 1]</code> the allowed pairs are <code>(5, 4)</code>, <code>(5, 1)</code> and <code>(9, 1)</code>, so the answer is <code>10</code>.</p>",
    constraints=["3 &le; nums.length &le; 10,000", "-1,000 &le; nums[i] &le; 1,000"],
    hints=["Checking every pair of indices works but takes O(n<sup>2</sup>) time. Fix the right element j and ask what the best partner is.",
           "For a fixed j the partner may be any element at index 0..j-2, so you want the maximum of that prefix.",
           "Sweep j from 2 to n-1. Maintain the running maximum of nums[0..j-2] (update it as j grows) and keep the best value of prefixMax + nums[j]."],
    editorial=["Fix the right element j. Its valid left partners are exactly the indices 0..j-2, and the best sum for this j uses the largest value in that prefix. As j increases by one, the prefix grows by one element (index j-1 becomes available for the next j), so a single variable holding the prefix maximum is enough.",
               "The answer is the maximum of <code>prefixMax(j-2) + nums[j]</code> over j from 2 to n-1. This is the smallest instance of non-adjacent selection and shows why 'exclude the neighbour' translates into 'look two steps back'. Time O(n), space O(1)."],
    time="O(n)", space="O(1)",
    solution='''def bestTwoNonAdjacentSum(nums):
    best = None
    prefix = nums[0]
    for j in range(2, len(nums)):
        cand = prefix + nums[j]
        if best is None or cand > best:
            best = cand
        prefix = max(prefix, nums[j - 1])
    return best
''',
    tests=[[[5, 9, 4, 1]], [[1, 2, 3]], [[-1, -2, -3]], [[0, 0, 0]], [[10, -5, 10]], [[-5, 100, -5, -5]], [[3, 3, 3, 3, 3]],
           [[1000, 1000, -1000, 1000]], [[-1000, -1000, -1000, -1000]], [[7, 1, 2, 3, 9, 4]], [_tn1], [_tn2], [_tn3]],
)


def _b_tn(nums):
    n = len(nums)
    return max(nums[i] + nums[j] for i in range(n) for j in range(i + 2, n))


def _v_tn(tests):
    for t in tests:
        nums = t["args"][0]
        assert 3 <= len(nums) <= 10000 and all(-1000 <= x <= 1000 for x in nums)


CHECKS["best-two-non-adjacent-sum"] = (_b_tn, lambda r: [gen_arr(r, -8, 8, 3, 10)], "exact")
VALIDATE["best-two-non-adjacent-sum"] = _v_tn

# ---------------------------------------------------------------- MEDIUM

_r = rnd(8104)
_gp1 = [_r.randint(0, 1000) for _ in range(8000)]
_gp2 = [_r.randint(0, 1000) for _ in range(6000)]
_gp3 = [_r.randint(0, 1000) for _ in range(5000)]

add(
    id="rob-houses-with-cooldown-gap", title="Robbery With a Cooldown Gap", diff="Medium", topic=TOPIC,
    fn="robWithGap", params=[("nums", "int[]"), ("gap", "int")], ret="int", cmp="exact",
    desc="<p>Houses stand in a row and house <code>i</code> holds <code>nums[i]</code> coins. Every time you rob a house, the police patrol the next <code>gap</code> houses: if you rob house <code>i</code>, you cannot rob any of the houses <code>i + 1, i + 2, ..., i + gap</code>. Houses further away are safe again.</p><p>Return the largest total you can rob. With <code>gap = 1</code> this is the classic House Robber.</p><p>For example, for <code>nums = [7, 2, 2, 2, 7]</code> the answer is <code>16</code> when <code>gap = 1</code>, <code>14</code> when <code>gap = 2</code> and only <code>7</code> when <code>gap = 4</code>.</p>",
    constraints=["1 &le; nums.length &le; 10,000", "0 &le; nums[i] &le; 1,000", "1 &le; gap &le; nums.length"],
    hints=["For gap = 1 you know the recurrence best(i) = max(best(i-1), best(i-2) + nums[i]). Think about how 'i-2' changes when the cooldown is longer.",
           "If you rob house p, the previous robbed house must be at index p - gap - 1 or earlier, so the prefix you can still use has length p - gap.",
           "Let best[i] be the best total using only the first i houses. Then best[i] = max(best[i-1], nums[i-1] + best[max(0, i-1-gap)]). Keep the whole best array, since you look back gap + 1 positions."],
    editorial=["Define <code>best[i]</code> as the maximum total from the first i houses, with <code>best[0] = 0</code>. For house index p = i-1 there are two choices. Skip it: the answer stays <code>best[i-1]</code>. Rob it: the previously robbed house must lie at index &le; p - gap - 1, so everything before it comes from the first <code>p - gap</code> houses, giving <code>nums[p] + best[max(0, p - gap)]</code>.",
               "The answer is <code>best[n]</code>. The recurrence needs random access to an entry <code>gap + 1</code> steps back, so keep the entire array instead of two rolling variables. That is O(n) time and O(n) space, independent of the gap size."],
    time="O(n)", space="O(n)",
    solution='''def robWithGap(nums, gap):
    n = len(nums)
    best = [0] * (n + 1)
    for i in range(1, n + 1):
        take = nums[i - 1] + best[max(0, i - 1 - gap)]
        best[i] = max(best[i - 1], take)
    return best[n]
''',
    tests=[[[7, 2, 2, 2, 7], 1], [[7, 2, 2, 2, 7], 2], [[7, 2, 2, 2, 7], 4], [[5], 1], [[0, 0, 0], 2], [[4, 9, 3, 2, 7], 2],
           [[1, 2, 3, 1], 1], [[1, 2, 3, 1], 3], [[1000, 1000, 1000, 1000], 1], [[6, 1, 1, 6, 1, 1, 6], 2],
           [[6, 1, 1, 6, 1, 1, 6], 3], [[8, 3, 9, 3, 8, 3, 9], 2], [_gp1, 3], [_gp2, 1], [_gp3, 2500]],
)


def _b_gap(nums, gap):
    n = len(nums)
    best = 0
    for s in _subsets(n):
        if any(b - a <= gap for a, b in zip(s, s[1:])):
            continue
        best = max(best, sum(nums[i] for i in s))
    return best


def _g_gap(r):
    a = gen_arr(r, 0, 9, 1, 11)
    return [a, r.randint(1, len(a))]


def _v_gap(tests):
    for t in tests:
        nums, gap = t["args"]
        assert 1 <= len(nums) <= 10000 and all(0 <= x <= 1000 for x in nums) and 1 <= gap <= len(nums)


CHECKS["rob-houses-with-cooldown-gap"] = (_b_gap, _g_gap, "exact")
VALIDATE["rob-houses-with-cooldown-gap"] = _v_gap

# ------------------------------------------------------------------

_r = rnd(8105)
_tr1 = [[_r.randint(-1000, 1000) for _ in range(3000)] for _ in range(2)]
_tr2 = [[_r.randint(0, 1000) for _ in range(2500)] for _ in range(2)]
_tr3 = [[_r.randint(-1000, 100) for _ in range(2000)] for _ in range(2)]

add(
    id="two-row-grid-no-touching-cells", title="Two-Row Grid, No Touching Cells", diff="Medium", topic=TOPIC,
    fn="maxTwoRowPick", params=[("grid", "int[][]")], ret="int", cmp="exact",
    desc="<p><code>grid</code> has exactly two rows and <code>n</code> columns. You may choose any set of cells, but no two chosen cells may share a side (cells that only touch at a corner are fine). Return the largest possible sum of the chosen values. Choosing nothing is allowed, so the answer is never negative.</p><p>For example, in <code>[[3, 1, 4], [2, 7, 1]]</code> choose the top cell of column 0, the bottom cell of column 1 and the top cell of column 2: <code>3 + 7 + 4 = 14</code>.</p>",
    constraints=["grid.length = 2", "1 &le; grid[0].length = grid[1].length &le; 5,000", "-1,000 &le; grid[r][c] &le; 1,000"],
    hints=["In any single column you can choose nothing, only the top cell or only the bottom cell, but never both. That is three states per column.",
           "Which choice in column c-1 is compatible with 'top' in column c? Not 'top', but 'nothing' and 'bottom' are fine, and symmetrically for 'bottom'.",
           "Keep three running values for the previous column: best with nothing chosen, with the top cell chosen, with the bottom cell chosen. Update them column by column."],
    editorial=["Process columns left to right and keep <code>none, top, bottom</code>: the best sum so far when the current column has no chosen cell, only its top cell, or only its bottom cell. For the next column with values <code>a</code> (top) and <code>b</code> (bottom): <code>none' = max(none, top, bottom)</code>, <code>top' = a + max(none, bottom)</code> and <code>bottom' = b + max(none, top)</code>.",
               "A choice only conflicts with the same row of the previous column or the other cell of its own column, which the transitions exclude. The answer is the maximum of the three after the last column, starting from <code>none = 0</code> and the other two impossible. Time O(n), space O(1). This is House Robber lifted from a path to a 2 x n ladder graph."],
    time="O(n)", space="O(1)",
    solution='''def maxTwoRowPick(grid):
    NEG = -10 ** 18
    none, top, bottom = 0, NEG, NEG
    for a, b in zip(grid[0], grid[1]):
        none, top, bottom = max(none, top, bottom), a + max(none, bottom), b + max(none, top)
    return max(none, top, bottom)
''',
    tests=[[[[3, 1, 4], [2, 7, 1]]], [[[5], [6]]], [[[-5], [-6]]], [[[1, 1], [1, 1]]], [[[1, 2, 3, 4], [4, 3, 2, 1]]],
           [[[-1, -2, -3], [-3, -2, -1]]], [[[10, -5, 10], [-5, 10, -5]]], [[[1000, 0, 1000], [0, 1000, 0]]],
           [[[5, 5, 5, 5, 5], [5, 5, 5, 5, 5]]], [[[9, 1, 1, 9], [1, 9, 9, 1]]], [_tr1], [_tr2], [_tr3]],
)


def _b_tr(grid):
    n = len(grid[0])
    cells = [(r, c) for c in range(n) for r in range(2)]
    best = 0
    for s in _subsets(len(cells)):
        chosen = [cells[i] for i in s]
        cs = set(chosen)
        if any((r, c + 1) in cs or (1 - r, c) in cs for r, c in chosen):
            continue
        best = max(best, sum(grid[r][c] for r, c in chosen))
    return best


def _g_tr(r):
    n = r.randint(1, 6)
    return [[[r.randint(-6, 9) for _ in range(n)] for _ in range(2)]]


def _v_tr(tests):
    for t in tests:
        g = t["args"][0]
        assert len(g) == 2 and len(g[0]) == len(g[1]) and 1 <= len(g[0]) <= 5000
        assert all(-1000 <= x <= 1000 for row in g for x in row)


CHECKS["two-row-grid-no-touching-cells"] = (_b_tr, _g_tr, "exact")
VALIDATE["two-row-grid-no-touching-cells"] = _v_tr

# ------------------------------------------------------------------

_r = rnd(8106)
_ek1 = ([_r.randint(-1000, 1000) for _ in range(1000)], 400)
_ek2 = ([_r.randint(-1000, 1000) for _ in range(999)], 500)
_ek3 = ([_r.randint(1, 1000) for _ in range(800)], 123)

add(
    id="exactly-k-non-adjacent-max-sum", title="Pick Exactly K, No Neighbours", diff="Medium", topic=TOPIC,
    fn="maxSumKNonAdjacent", params=[("nums", "int[]"), ("k", "int")], ret="int", cmp="exact",
    desc="<p>Choose <strong>exactly</strong> <code>k</code> elements of <code>nums</code> such that no two chosen elements are next to each other (indices <code>i</code> and <code>i + 1</code> never both chosen). Return the largest possible sum of the chosen values.</p><p>Values may be negative, so you cannot simply skip bad elements: you must still reach exactly <code>k</code> picks. The input always allows a valid choice.</p><p>For example, for <code>nums = [4, -1, 5, -2, 3]</code> and <code>k = 2</code> the answer is <code>9</code> (take 4 and 5), and for <code>k = 3</code> it is <code>12</code> (take 4, 5 and 3).</p>",
    constraints=["1 &le; nums.length &le; 1,000", "-1,000 &le; nums[i] &le; 1,000", "1 &le; k &le; ceil(nums.length / 2), so a valid choice always exists"],
    hints=["The plain House Robber DP has one dimension. Because the number of picks matters now, what extra information must the state carry?",
           "Let f[i][j] be the best sum using only the first i elements with exactly j picks. Either the last element is skipped, or it is picked and the previous pick lies at index i-2 or earlier.",
           "f[i][j] = max(f[i-1][j], f[i-2][j-1] + nums[i-1]). Mark impossible states with a very negative value. Only rows i-1 and i-2 are needed, so keep two rolling arrays of length k + 1."],
    editorial=["Add the pick count to the state. With <code>f[i][j]</code> = best sum from the first i elements using exactly j picks (and <code>-infinity</code> when impossible), the last element is either unused, giving <code>f[i-1][j]</code>, or used, in which case its left neighbour is unused and the other j-1 picks come from the first i-2 elements, giving <code>f[i-2][j-1] + nums[i-1]</code>. The base state is <code>f[i][0] = 0</code>.",
               "The answer is <code>f[n][k]</code>; the constraint on k guarantees it is reachable. Each row depends only on the two rows before it, so two arrays of size k + 1 suffice, and j never needs to exceed (i + 1) / 2. Time O(n &middot; k), space O(k). A greedy 'take the largest and fix up' idea fails because a big element can block two good neighbours."],
    time="O(n * k)", space="O(k)",
    solution='''def maxSumKNonAdjacent(nums, k):
    NEG = -10 ** 18
    prev2 = [0] + [NEG] * k      # f[i-2]
    prev1 = [0] + [NEG] * k      # f[i-1]
    for idx, x in enumerate(nums):
        cur = prev1[:]
        for j in range(1, min(k, (idx + 2) // 2) + 1):
            v = prev2[j - 1] + x
            if v > cur[j]:
                cur[j] = v
        prev2, prev1 = prev1, cur
    return prev1[k]
''',
    tests=[[[4, -1, 5, -2, 3], 2], [[4, -1, 5, -2, 3], 3], [[5], 1], [[-5], 1], [[3, 8], 1], [[-3, -8], 1], [[1, 2, 3, 4], 2],
           [[-1, -1, -1, -1, -1], 3], [[9, -9, 9, -9, 9], 3], [[10, 1, 1, 10], 2], [[2, 7, 3, 5, 8, 1, 6], 3],
           [_ek1[0], _ek1[1]], [_ek2[0], _ek2[1]], [_ek3[0], _ek3[1]]],
)


def _b_ek(nums, k):
    n = len(nums)
    best = None
    for s in combinations(range(n), k):
        if any(b - a == 1 for a, b in zip(s, s[1:])):
            continue
        v = sum(nums[i] for i in s)
        if best is None or v > best:
            best = v
    return best


def _g_ek(r):
    a = gen_arr(r, -6, 9, 1, 11)
    return [a, r.randint(1, (len(a) + 1) // 2)]


def _v_ek(tests):
    for t in tests:
        nums, k = t["args"]
        assert 1 <= len(nums) <= 1000 and all(-1000 <= x <= 1000 for x in nums)
        assert 1 <= k <= (len(nums) + 1) // 2


CHECKS["exactly-k-non-adjacent-max-sum"] = (_b_ek, _g_ek, "exact")
VALIDATE["exactly-k-non-adjacent-max-sum"] = _v_ek

# ------------------------------------------------------------------

_r = rnd(8107)
_sv1 = ([_r.randint(1, 1000000) for _ in range(2000)], 700)
_sv2 = ([_r.randint(1, 3000) for _ in range(2000)], 2)
_sv3 = ([_r.choice([1, 5, 9, 13, 17, 21, 25]) * 1000 + _r.randint(0, 2) for _ in range(2000)], 4000)

add(
    id="spaced-value-harvest", title="Spaced Value Harvest", diff="Medium", topic=TOPIC,
    fn="spacedHarvest", params=[("nums", "int[]"), ("d", "int")], ret="int", cmp="exact",
    desc="<p>A field contains plants whose sizes are given by <code>nums</code> (sizes may repeat). You choose a set of <strong>distinct sizes</strong> to harvest; for every chosen size <code>v</code> you collect all plants of that size and earn <code>v</code> points per plant. Any two chosen sizes must differ by at least <code>d</code>.</p><p>Return the maximum total points. With <code>d = 2</code> this is the game of Delete and Earn, but here sizes can be as large as 1,000,000, so you cannot afford to look at every integer in between.</p><p>For example, for <code>nums = [3, 4, 4, 6, 10]</code> the answer is <code>27</code> for <code>d = 1</code>, <code>24</code> for <code>d = 2</code> (sizes 4, 6, 10) and <code>19</code> for <code>d = 3</code> (sizes 3, 6, 10).</p>",
    constraints=["1 &le; nums.length &le; 2,000", "1 &le; nums[i] &le; 1,000,000", "1 &le; d &le; 1,000,000"],
    hints=["Taking one plant of size v while taking the size is allowed means you should take all plants of size v. So the real decision is which distinct sizes to take.",
           "Sort the distinct sizes and give size v the weight v * count(v). A chosen set must have all neighbouring differences at least d. Think of House Robber, but the 'conflicting neighbours' of a size are all smaller sizes within d - 1 of it.",
           "Let dp[i] be the best total using the first i distinct sizes. dp[i] = max(dp[i-1], weight_i + dp[j]), where j is the number of sizes that are at most size_i - d. A pointer that only moves forward finds j."],
    editorial=["Count the plants per size and sort the distinct sizes <code>v_0 &lt; v_1 &lt; ...</code> with weights <code>w_i = v_i * count(v_i)</code>. A selection is valid when consecutive chosen sizes differ by at least d, and any valid selection of sizes should take all copies (more points, no extra conflict).",
               "Let <code>dp[i]</code> be the best total using the first i distinct sizes. Size <code>v_i</code> is either skipped (<code>dp[i-1]</code>) or taken, in which case the previous chosen size is at most <code>v_i - d</code>; those sizes form a prefix of length j, so the value is <code>w_i + dp[j]</code>. Since <code>v_i - d</code> grows with i, j can be advanced with a two-pointer sweep (or found by binary search). The total is at most 2,000 x 1,000,000 = 2 x 10<sup>9</sup>, which fits in 32 bits. Time O(n log n) for sorting, space O(n)."],
    time="O(n log n)", space="O(n)",
    solution='''def spacedHarvest(nums, d):
    cnt = {}
    for x in nums:
        cnt[x] = cnt.get(x, 0) + 1
    vals = sorted(cnt)
    dp = [0] * (len(vals) + 1)
    j = 0
    for i, v in enumerate(vals):
        while vals[j] <= v - d:
            j += 1
        dp[i + 1] = max(dp[i], v * cnt[v] + dp[j])
    return dp[len(vals)]
''',
    tests=[[[3, 4, 4, 6, 10], 1], [[3, 4, 4, 6, 10], 2], [[3, 4, 4, 6, 10], 3], [[5], 7], [[1, 1, 1], 1000000],
           [[1, 1000000], 999999], [[1, 1000000], 1000000], [[2, 2, 3, 3, 3, 4], 2], [[10, 20, 30, 40], 15],
           [[10, 20, 30, 40], 20], [[1000000] * 2000, 5], [_sv1[0], _sv1[1]], [_sv2[0], _sv2[1]], [_sv3[0], _sv3[1]]],
)


def _b_sv(nums, d):
    vals = sorted(set(nums))
    best = 0
    for s in _subsets(len(vals)):
        if any(vals[b] - vals[a] < d for a, b in zip(s, s[1:])):
            continue
        best = max(best, sum(vals[i] * nums.count(vals[i]) for i in s))
    return best


def _g_sv(r):
    a = gen_arr(r, 1, 14, 1, 12)
    return [a, r.randint(1, 8)]


def _v_sv(tests):
    for t in tests:
        nums, d = t["args"]
        assert 1 <= len(nums) <= 2000 and all(1 <= x <= 1000000 for x in nums) and 1 <= d <= 1000000


CHECKS["spaced-value-harvest"] = (_b_sv, _g_sv, "exact")
VALIDATE["spaced-value-harvest"] = _v_sv

# ------------------------------------------------------------------

_r = rnd(8108)
_co1 = [_r.randint(0, 2) for _ in range(6000)]
_co2 = [0] * 5000
_co3 = [_r.choice([0, 0, 1, 3]) for _ in range(4000)]

add(
    id="count-optimal-robbery-plans", title="Count the Best Robbery Plans", diff="Medium", topic=TOPIC, tier="extra",
    fn="countBestPlans", params=[("nums", "int[]")], ret="int", cmp="exact",
    desc="<p>Houses stand in a row and house <code>i</code> holds <code>nums[i]</code> coins. A <strong>plan</strong> is a set of house indices with no two neighbours (indices <code>i</code> and <code>i + 1</code> never both in the plan); the empty plan is allowed. Two plans are different when their sets of indices differ, even if they collect the same coins.</p><p>Among all plans that collect the maximum possible number of coins, count how many there are. Return the count modulo <code>1,000,000,007</code>.</p><p>For example, for <code>[1, 1, 1, 1]</code> the maximum is 2 and there are 3 best plans (houses {0,2}, {0,3} and {1,3}), and for <code>[0, 0, 0]</code> every valid plan is best: there are 5 of them.</p>",
    constraints=["0 &le; nums.length &le; 10,000", "0 &le; nums[i] &le; 1,000"],
    hints=["First solve the usual question: the maximum total. Now ask the DP to also remember in how many ways each maximum can be reached.",
           "Let (best, ways) describe the first i houses. Skipping house i-1 gives the pair for the first i-1 houses; robbing it gives (best[i-2] + nums[i-1], ways[i-2]).",
           "Compare the two candidate pairs. If one total is larger, take that pair. If they are equal, the plans are disjoint (one contains the house, the other does not), so the counts add up. Reduce counts modulo 1,000,000,007 but compare totals exactly."],
    editorial=["Extend the House Robber state to a pair <code>(best, ways)</code> for each prefix, starting from <code>(0, 1)</code> for the empty prefix (the single plan that robs nothing). For the prefix ending at house p there are two disjoint families of plans: those that skip p, described by the previous prefix, and those that rob p, described by the prefix two steps back with <code>nums[p]</code> added to the total.",
               "Keep the larger total; when the totals tie, add the counts, because a plan that contains p can never equal a plan that does not. Ties are frequent when the array has zeros, since robbing an empty house changes nothing but still creates a different plan. The answer is the count of the full prefix, reduced modulo 1,000,000,007. Totals never exceed 10<sup>7</sup>, so they are compared exactly. Time O(n), space O(1)."],
    time="O(n)", space="O(1)",
    solution='''def countBestPlans(nums):
    M = 1000000007
    b2, c2 = 0, 1      # prefix of length i-2
    b1, c1 = 0, 1      # prefix of length i-1
    for x in nums:
        tb, tc = b2 + x, c2
        if tb > b1:
            nb, nc = tb, tc
        elif tb < b1:
            nb, nc = b1, c1
        else:
            nb, nc = b1, (c1 + tc) % M
        b2, c2, b1, c1 = b1, c1, nb, nc
    return c1 % M
''',
    tests=[[[1, 1, 1, 1]], [[0, 0, 0]], [[]], [[0]], [[5]], [[3, 0, 3]], [[2, 2, 2]], [[1, 2, 3, 1]], [[2, 7, 9, 3, 1]],
           [[0, 0, 0, 0, 0, 0, 0, 0]], [[1, 0, 1, 0, 1, 0]], [[4, 4, 4, 4, 4, 4, 4]], [_co1], [_co2], [_co3]],
)


def _b_co(nums):
    n = len(nums)
    best, ways = -1, 0
    for s in _subsets(n):
        if any(b - a == 1 for a, b in zip(s, s[1:])):
            continue
        v = sum(nums[i] for i in s)
        if v > best:
            best, ways = v, 1
        elif v == best:
            ways += 1
    return ways % MOD


def _v_co(tests):
    for t in tests:
        nums = t["args"][0]
        assert len(nums) <= 10000 and all(0 <= x <= 1000 for x in nums)


CHECKS["count-optimal-robbery-plans"] = (_b_co, lambda r: [gen_arr(r, 0, 3, 0, 12)], "exact")
VALIDATE["count-optimal-robbery-plans"] = _v_co

# ------------------------------------------------------------------

_r = rnd(8109)
_ol1 = [_r.randint(0, 1000) for _ in range(7000)]
_ol2 = [_r.randint(0, 1000) for _ in range(4001)]
_ol3 = [1000, 1, 1000] + [_r.randint(0, 3) for _ in range(5000)]

add(
    id="rob-with-one-alarm-lapse", title="One Alarm Lapse", diff="Medium", topic=TOPIC, tier="extra",
    fn="robWithOneLapse", params=[("nums", "int[]")], ret="int", cmp="exact",
    desc="<p>Houses stand in a row and house <code>i</code> holds <code>nums[i]</code> coins. Robbing two neighbouring houses normally sets off the alarm, but tonight the alarm system has a <strong>single lapse</strong>: your set of robbed houses may contain <strong>at most one</strong> pair of neighbouring houses (indices <code>i</code> and <code>i + 1</code> both robbed). Robbing three houses in a row would contain two such pairs, so it is not allowed.</p><p>Return the maximum number of coins you can collect. For example, for <code>[5, 6, 1, 1, 5]</code> the answer is <code>16</code> (houses 0, 1 and 4).</p>",
    constraints=["0 &le; nums.length &le; 10,000", "0 &le; nums[i] &le; 1,000"],
    hints=["Without the lapse this is House Robber with the two states 'last house robbed' and 'last house not robbed'. The lapse is a one-time resource, so remember whether it has been spent.",
           "Use four running values: (last robbed or not) x (lapse used or not). Robbing right after a robbed house is the only move that spends the lapse.",
           "With r0 = last not robbed and r1 = last robbed, and u0 / u1 for the lapse unused / used: new_free[u] = max of both options of the previous house; new_robbed[u] = free[u] + x; and new_robbed[used] also considers robbed[unused] + x."],
    editorial=["Let <code>s[t][u]</code> be the best total over the processed prefix, where t = 1 if the last house is robbed and u = 1 if the lapse has already been used (a robbed pair exists). For the next house with value x: not robbing it gives <code>s'[0][u] = max(s[0][u], s[1][u])</code>. Robbing it after a skipped house keeps the lapse state: <code>s'[1][u] = s[0][u] + x</code>. Robbing it directly after a robbed house is the lapse, so <code>s'[1][1]</code> also considers <code>s[1][0] + x</code>.",
               "From <code>s[1][1]</code> you cannot rob the next house, since a second pair would appear; the transitions never allow it. Start with <code>s[0][0] = 0</code> and everything else impossible, and return the maximum of all four values at the end. Time O(n), space O(1). The same idea (carry a small 'how many exceptions are left' counter in the state) works for any bounded number of rule violations."],
    time="O(n)", space="O(1)",
    solution='''def robWithOneLapse(nums):
    NEG = -10 ** 18
    f0, f1 = 0, NEG       # last not robbed: lapse unused / used
    r0, r1 = NEG, NEG     # last robbed: lapse unused / used
    for x in nums:
        nf0 = max(f0, r0)
        nf1 = max(f1, r1)
        nr0 = f0 + x
        nr1 = max(f1 + x, r0 + x)
        f0, f1, r0, r1 = nf0, nf1, nr0, nr1
    return max(f0, f1, r0, r1)
''',
    tests=[[[5, 6, 1, 1, 5]], [[]], [[9]], [[4, 7]], [[3, 3, 3]], [[0, 0, 0, 0]], [[1, 100, 100, 1]], [[100, 1, 1, 100]],
           [[2, 7, 9, 3, 1]], [[10, 10, 0, 10, 10]], [[5, 5, 5, 5, 5, 5, 5, 5]], [_ol1], [_ol2], [_ol3]],
)


def _b_ol(nums):
    n = len(nums)
    best = 0
    for s in _subsets(n):
        pairs = sum(1 for a, b in zip(s, s[1:]) if b - a == 1)
        if pairs <= 1:
            best = max(best, sum(nums[i] for i in s))
    return best


def _v_ol(tests):
    for t in tests:
        nums = t["args"][0]
        assert len(nums) <= 10000 and all(0 <= x <= 1000 for x in nums)


CHECKS["rob-with-one-alarm-lapse"] = (_b_ol, lambda r: [gen_arr(r, 0, 9, 0, 12)], "exact")
VALIDATE["rob-with-one-alarm-lapse"] = _v_ol

# ---------------------------------------------------------------- HARD

_r = rnd(8110)
_cp1 = ([_r.randint(1, 1000) for _ in range(900)], 300)
_cp2 = ([_r.randint(1, 1000) for _ in range(899)], 449)
_cp3 = ([_r.randint(1, 1000) for _ in range(800)], 20)

add(
    id="circular-pick-k-non-adjacent", title="Circular Feast, Exactly K Slices", diff="Hard", topic=TOPIC,
    fn="circularPickK", params=[("slices", "int[]"), ("k", "int")], ret="int", cmp="exact",
    desc="<p>A round cake is cut into <code>m</code> slices in circular order; slice <code>i</code> has size <code>slices[i]</code>, and slice <code>m - 1</code> is a neighbour of slice <code>0</code>. You must take <strong>exactly</strong> <code>k</code> slices and no two taken slices may be neighbours on the circle.</p><p>Return the largest total size you can take. The input always allows a valid choice.</p><p>For example, for <code>slices = [8, 9, 8, 6, 1, 1]</code> the answer is <code>16</code> when <code>k = 2</code> (the two 8s at indices 0 and 2) and <code>17</code> when <code>k = 3</code> (indices 0, 2 and 4: <code>8 + 8 + 1</code>).</p>",
    constraints=["2 &le; slices.length &le; 1,000", "1 &le; slices[i] &le; 1,000", "1 &le; k &le; floor(slices.length / 2), so a valid choice always exists"],
    hints=["Remove the circle first: if the slices were in a straight line, how would you pick exactly k non-adjacent ones with maximum sum?",
           "In the circle, slices 0 and m-1 are neighbours, so any valid choice leaves out slice 0 or slice m-1 (or both).",
           "Run the exactly-k line DP f[i][j] = max(f[i-1][j], f[i-2][j-1] + a[i-1]) on slices[0..m-2] and on slices[1..m-1], then return the larger f[.][k]."],
    editorial=["On a straight line the problem is solved by the DP <code>f[i][j] = max(f[i-1][j], f[i-2][j-1] + a[i-1])</code> where j is the number of slices taken, with <code>f[i][0] = 0</code> and unreachable states marked as very negative. The circle adds just one constraint: slices 0 and m-1 are neighbours, so they cannot both be taken.",
               "Hence every valid choice avoids slice 0 or avoids slice m-1. The best choice avoiding the last slice is the line answer on <code>slices[0..m-2]</code>; the best one avoiding the first is the line answer on <code>slices[1..m-1]</code>. Return the larger of the two. For k &le; floor(m / 2) both lines contain a valid selection (a line of m-1 elements holds up to floor(m / 2) non-adjacent picks). Time O(m &middot; k), space O(k). This is the circular trick of House Robber II combined with a pick counter."],
    time="O(m * k)", space="O(k)",
    solution='''def circularPickK(slices, k):
    NEG = -10 ** 18

    def line(a):
        prev2 = [0] + [NEG] * k
        prev1 = [0] + [NEG] * k
        for idx, x in enumerate(a):
            cur = prev1[:]
            for j in range(1, min(k, (idx + 2) // 2) + 1):
                v = prev2[j - 1] + x
                if v > cur[j]:
                    cur[j] = v
            prev2, prev1 = prev1, cur
        return prev1[k]

    return max(line(slices[:-1]), line(slices[1:]))
''',
    tests=[[[8, 9, 8, 6, 1, 1], 2], [[1, 2], 1], [[5, 3], 1], [[1, 2, 3], 1], [[4, 1, 2, 3], 2], [[9, 1, 1, 9], 1],
           [[9, 1, 1, 9, 1, 1], 2], [[3, 3, 3, 3, 3, 3], 3], [[1, 10, 1, 10, 1, 10], 3], [[7, 2, 9, 4, 6, 5, 8], 3],
           [[1000, 1, 1000, 1, 1000, 1, 1000, 1], 4], [_cp1[0], _cp1[1]], [_cp2[0], _cp2[1]], [_cp3[0], _cp3[1]]],
)


def _b_cp(slices, k):
    m = len(slices)
    best = None
    for s in combinations(range(m), k):
        ok = all(b - a > 1 for a, b in zip(s, s[1:])) and not (k > 1 and s[0] == 0 and s[-1] == m - 1)
        if k == 1 or ok:
            v = sum(slices[i] for i in s)
            if best is None or v > best:
                best = v
    return best


def _g_cp(r):
    a = gen_arr(r, 1, 9, 2, 11)
    return [a, r.randint(1, len(a) // 2)]


def _v_cp(tests):
    for t in tests:
        s, k = t["args"]
        assert 2 <= len(s) <= 1000 and all(1 <= x <= 1000 for x in s) and 1 <= k <= len(s) // 2


CHECKS["circular-pick-k-non-adjacent"] = (_b_cp, _g_cp, "exact")
VALIDATE["circular-pick-k-non-adjacent"] = _v_cp

# ------------------------------------------------------------------

_r = rnd(8111)
_cw1 = ([_r.randint(0, 1000) for _ in range(8000)], 1500)
_cw2 = ([_r.randint(0, 1000) for _ in range(6000)], 7)
_cw3 = ([_r.randint(0, 1000) for _ in range(5000)], 5000)
_cw4 = ([_r.randint(0, 1000) for _ in range(5000)], 2)

add(
    id="cheapest-picks-covering-every-window", title="Guard Every Window", diff="Hard", topic=TOPIC, tier="extra",
    fn="cheapestWindowCover", params=[("costs", "int[]"), ("w", "int")], ret="int", cmp="exact",
    desc="<p>Along a road there are <code>n</code> posts in a row, and installing a lamp at post <code>i</code> costs <code>costs[i]</code>. The road is inspected in every stretch of <code>w</code> consecutive posts (posts <code>s, s + 1, ..., s + w - 1</code> for each valid start <code>s</code>), and every such stretch must contain <strong>at least one</strong> lamp.</p><p>Return the minimum total cost of the lamps. For example, for <code>costs = [4, 2, 6, 1, 5]</code> and <code>w = 3</code> the answer is <code>3</code> (lamps at posts 1 and 3). With <code>w = 1</code> every post needs a lamp.</p><p>Equivalently: choose which posts to leave dark so that no <code>w</code> consecutive posts are all dark, while the lit ones cost as little as possible.</p>",
    constraints=["1 &le; costs.length &le; 8,000", "0 &le; costs[i] &le; 1,000", "1 &le; w &le; costs.length"],
    hints=["Define the state as 'the last lamp is at post i'. Which earlier lamp positions may precede it without leaving an uncovered stretch of w posts in between?",
           "If the previous lamp is at post j < i, the posts j+1..i-1 are dark, so i - j - 1 &le; w - 1, i.e. j &ge; i - w. The first lamp must be at post w-1 or earlier, and the last lamp at post n-w or later.",
           "dp[i] = costs[i] + min(dp[j] for j in [i-w, i-1]), with a virtual lamp at position -1 of cost 0. That is a sliding window minimum, so a monotonic deque brings the total work to O(n)."],
    editorial=["Let <code>dp[i]</code> be the cheapest way to cover the prefix with the last lamp placed at post i. The gap between consecutive lamps (and between the road start and the first lamp) may hold at most <code>w - 1</code> dark posts, otherwise some stretch of w posts would contain no lamp. Hence <code>dp[i] = costs[i] + min(dp[j])</code> over earlier lamps j with <code>i - w &le; j &le; i - 1</code>, where a virtual lamp at index -1 with cost 0 represents 'no lamp yet' and is allowed for <code>i &le; w - 1</code>.",
               "At the end the last lamp must leave at most w - 1 dark posts after it, so the answer is the minimum of <code>dp[j]</code> over <code>j &ge; n - w</code>. Evaluating each dp value by scanning w predecessors costs O(n &middot; w), which is too slow for the maximum input; the minimum over a window that slides one step at a time is maintained with a monotonic deque of increasing dp values, giving O(n) total. For w = 2 this reduces to the cheapest set of lamps with no two neighbouring dark posts."],
    time="O(n)", space="O(n)",
    solution='''from collections import deque


def cheapestWindowCover(costs, w):
    n = len(costs)
    # position p (1..n) is post p-1; position 0 is a virtual free lamp before the road
    dp = [0] * (n + 1)
    dq = deque([0])
    for p in range(1, n + 1):
        while dq[0] < p - w:
            dq.popleft()
        dp[p] = costs[p - 1] + dp[dq[0]]
        while dq and dp[dq[-1]] >= dp[p]:
            dq.pop()
        dq.append(p)
    return min(dp[n - w + 1:n + 1])
''',
    tests=[[[4, 2, 6, 1, 5], 3], [[4, 2, 6, 1, 5], 1], [[4, 2, 6, 1, 5], 5], [[7], 1], [[3, 9], 2], [[3, 9], 1],
           [[5, 1, 5, 1, 5], 2], [[0, 0, 0, 0], 2], [[10, 10, 10, 10, 10, 10], 3], [[9, 1, 9, 9, 1, 9, 9, 1], 3],
           [[5, 8, 3, 7, 6, 2, 9, 4], 4], [_cw1[0], _cw1[1]], [_cw2[0], _cw2[1]], [_cw3[0], _cw3[1]], [_cw4[0], _cw4[1]]],
)


def _b_cw(costs, w):
    n = len(costs)
    best = None
    for s in _subsets(n):
        ss = set(s)
        if all(any(i in ss for i in range(a, a + w)) for a in range(n - w + 1)):
            v = sum(costs[i] for i in s)
            if best is None or v < best:
                best = v
    return best


def _g_cw(r):
    a = gen_arr(r, 0, 9, 1, 12)
    return [a, r.randint(1, len(a))]


def _v_cw(tests):
    for t in tests:
        c, w = t["args"]
        assert 1 <= len(c) <= 8000 and all(0 <= x <= 1000 for x in c) and 1 <= w <= len(c)


CHECKS["cheapest-picks-covering-every-window"] = (_b_cw, _g_cw, "exact")
VALIDATE["cheapest-picks-covering-every-window"] = _v_cw
