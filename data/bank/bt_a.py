"""Problems: backtracking, subsets and combinations. See data/lib.py for the registry."""
from itertools import combinations as _combs, combinations_with_replacement as _cwr, product as _product
from math import comb as _comb

from lib import add, rnd, CHECKS, VALIDATE, gen_arr  # noqa: F401

TOPIC = "Backtracking"
MOD = 1_000_000_007


# ================================================================== EASY

# ---------------------------------------------------------------- count distinct subsets
p = add(
    id="count-distinct-subsets-of-multiset", title="Count Distinct Subsets", diff="Easy", topic=TOPIC,
    fn="countDistinctSubsets", params=[("nums", "int[]")], ret="int", cmp="exact",
    desc="<p>The array <code>nums</code> may contain repeated values. Two subsets are considered the <em>same</em> when they contain every value the same number of times, no matter which positions the values were taken from. For example, in <code>[1, 2, 2]</code> the two subsets that pick a single <code>2</code> are the same subset.</p><p>Return the number of distinct subsets, counting the empty subset, modulo <code>1,000,000,007</code>.</p>",
    constraints=["1 &le; nums.length &le; 10,000", "-10<sup>9</sup> &le; nums[i] &le; 10<sup>9</sup>"],
    hints=["Listing all the distinct subsets only works for tiny arrays. Count them instead of generating them.",
           "A distinct subset is described completely by how many copies of each distinct value it takes. Those choices are independent.",
           "A value that occurs <code>c</code> times can be taken 0, 1, ..., c times, which is <code>c + 1</code> options. Multiply these option counts over all distinct values."],
    editorial=["Group equal values together. A subset (in the sense of this problem) is fixed by choosing, for every distinct value, how many copies to use. A value with <code>c</code> occurrences offers <code>c + 1</code> choices, and the choices for different values do not influence each other, so the total is the product of <code>(c + 1)</code> over all distinct values. The empty subset corresponds to choosing zero copies everywhere and is counted automatically.",
               "Check with <code>[1, 2, 2]</code>: the value 1 gives 2 options and the value 2 gives 3 options, so 6 distinct subsets: <code>[]</code>, <code>[1]</code>, <code>[2]</code>, <code>[1,2]</code>, <code>[2,2]</code>, <code>[1,2,2]</code>. Building them with backtracking would take exponential time; counting needs one pass with a hash map. Take the product modulo 10<sup>9</sup>+7 at every step."],
    time="O(n)", space="O(n)",
    solution='''def countDistinctSubsets(nums):
    MOD = 1_000_000_007
    freq = {}
    for x in nums:
        freq[x] = freq.get(x, 0) + 1
    res = 1
    for c in freq.values():
        res = res * (c + 1) % MOD
    return res
''',
    tests=[[[1, 2, 2]], [[5]], [[4, 4, 4, 4]], [[1, 2, 3]], [[-7, -7, 7, 7]], [[0, 0, 0, 1, 1]], [[1000000000, -1000000000]],
           [[3, 3, 3, 3, 3, 3, 3, 3, 3, 3]], [[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30]]],
)
_r = rnd(9101)
p["tests"].append([[_r.randint(-10, 10) for _ in range(6000)]])
p["tests"].append([_r.sample(range(-10 ** 9, 10 ** 9), 3000)])
p["tests"].append([[7] * 10000])


def b_cds(nums):
    n = len(nums)
    seen = set()
    for mask in range(1 << n):
        seen.add(tuple(sorted(nums[i] for i in range(n) if mask >> i & 1)))
    return len(seen) % MOD


def v_cds(tests):
    for t in tests:
        nums = t["args"][0]
        assert 1 <= len(nums) <= 10000 and all(-10 ** 9 <= x <= 10 ** 9 for x in nums)


CHECKS["count-distinct-subsets-of-multiset"] = (b_cds, lambda r: [gen_arr(r, -3, 3, 1, 9)], "exact")
VALIDATE["count-distinct-subsets-of-multiset"] = v_cds


# ---------------------------------------------------------------- sorted subset sums
add(
    id="sorted-subset-sums", title="Sorted Subset Sums", diff="Easy", topic=TOPIC,
    fn="sortedSubsetSums", params=[("nums", "int[]")], ret="int[]", cmp="exact",
    desc="<p>Every subset of <code>nums</code> (chosen by position, so there are exactly <code>2<sup>n</sup></code> of them, the empty subset included) has a sum; the empty subset has sum <code>0</code>.</p><p>Return the sums of all <code>2<sup>n</sup></code> subsets in non-decreasing order. If several subsets have the same sum, that sum appears once for each of them.</p>",
    constraints=["1 &le; nums.length &le; 12", "-1000 &le; nums[i] &le; 1000"],
    hints=["Think about how the list of all subset sums of the first <code>i</code> elements grows when you look at element <code>i + 1</code>.",
           "Each old subset can either leave the new element out (same sum) or take it (sum plus the element).",
           "Start with <code>[0]</code>. For every element <code>x</code>, replace the list by the old list followed by the old list with <code>x</code> added to every entry. Sort at the end."],
    editorial=["Let <code>S</code> be the list of sums of all subsets of the elements processed so far, initially <code>[0]</code> for the empty subset. A new element <code>x</code> doubles the number of subsets: the old ones without <code>x</code> keep their sums, the old ones with <code>x</code> added have sums increased by <code>x</code>. So the new list is <code>S + [s + x for s in S]</code>. After all elements, sort the list.",
               "The same list falls out of a backtracking search with an include/skip choice per element that records the running sum at the leaves. The doubling loop avoids recursion and performs 2<sup>n</sup> additions in total; sorting dominates with O(n &middot; 2<sup>n</sup>)."],
    time="O(n &middot; 2<sup>n</sup>)", space="O(2<sup>n</sup>)",
    solution='''def sortedSubsetSums(nums):
    sums = [0]
    for x in nums:
        sums = sums + [s + x for s in sums]
    sums.sort()
    return sums
''',
    tests=[[[1, 2]], [[3, -1]], [[5]], [[0, 0]], [[1, 1, 1]], [[-2, -3]], [[4, 1, 2]], [[1000, -1000]], [[7, 7, 7, 7]],
           [[1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1000, -1000]], [[-5, 10, 3, -8, 0, 6, 6, -1]],
           [[1000] * 12], [[-1000, -999, -998, -997, -996, -995, -994, -993, -992, -991, -990, -989]]],
)


def b_sss(nums):
    n = len(nums)
    out = []
    for mask in range(1 << n):
        out.append(sum(nums[i] for i in range(n) if mask >> i & 1))
    return sorted(out)


def v_sss(tests):
    for t in tests:
        nums, res = t["args"][0], t["expected"]
        assert 1 <= len(nums) <= 12 and all(-1000 <= x <= 1000 for x in nums)
        assert len(res) == 2 ** len(nums) and res == sorted(res)


CHECKS["sorted-subset-sums"] = (b_sss, lambda r: [gen_arr(r, -6, 6, 1, 9)], "exact")
VALIDATE["sorted-subset-sums"] = v_sss


# ================================================================== MEDIUM

# ---------------------------------------------------------------- digit combinations
add(
    id="digit-combinations-with-sum", title="Digit Combinations With Sum", diff="Medium", topic=TOPIC,
    fn="digitCombinations", params=[("k", "int"), ("n", "int")], ret="int[][]", cmp="rowset",
    desc="<p>Find every way to choose exactly <code>k</code> <em>different</em> digits from <code>1..9</code> so that they add up to <code>n</code>. Each digit can be used at most once in a combination.</p><p>Write every combination in strictly increasing order (for example <code>[1,2,4]</code>, never <code>[2,1,4]</code>) and list every combination once. Rows may be returned in any order. If no combination exists, return an empty array.</p>",
    constraints=["1 &le; k &le; 9", "1 &le; n &le; 60"],
    hints=["Build a combination digit by digit, remembering how many digits are still needed and how much sum is still missing.",
           "Only allow digits bigger than the previous one, then every set is produced exactly once and already sorted.",
           "Cut a branch when the missing sum is negative, or when the smallest possible way to finish (next digits <code>d, d+1, ...</code>) already exceeds it, or when too few digits remain to supply <code>k</code> more."],
    editorial=["Recurse on <code>(next_digit, digits_left, sum_left)</code> with the chosen digits in a list. If <code>digits_left == 0</code>, record the list when <code>sum_left == 0</code>. Otherwise try each digit <code>d</code> from <code>next_digit</code> to 9 and recurse with <code>d + 1</code>, one digit fewer needed and <code>sum_left - d</code>. Because digits only increase along a path, every set of digits is visited once, in sorted order.",
               "Pruning keeps it fast: once <code>d &gt; sum_left</code> every later digit overshoots as well, so stop the loop. The whole search space is at most C(9, k) &le; 126 leaves, so the running time is tiny; the point of the exercise is the clean start-index pattern used by all combination problems."],
    time="O(C(9, k) &middot; k)", space="O(k) extra",
    solution='''def digitCombinations(k, n):
    res = []
    cur = []

    def go(start, left, need):
        if left == 0:
            if need == 0:
                res.append(cur[:])
            return
        for d in range(start, 10):
            if d > need:
                break
            cur.append(d)
            go(d + 1, left - 1, need - d)
            cur.pop()

    go(1, k, n)
    return res
''',
    tests=[[3, 7], [3, 9], [4, 1], [1, 9], [1, 10], [9, 45], [9, 44], [2, 17], [2, 18], [3, 24], [2, 3], [5, 25], [4, 30], [6, 30], [7, 40], [3, 60]],
)


def b_dc(k, n):
    return [list(c) for c in _combs(range(1, 10), k) if sum(c) == n]


def v_dc(tests):
    for t in tests:
        k, n = t["args"]
        assert 1 <= k <= 9 and 1 <= n <= 60
        res = t["expected"]
        assert len({tuple(x) for x in res}) == len(res)
        for row in res:
            assert len(row) == k and sum(row) == n and all(row[i] < row[i + 1] for i in range(k - 1))
            assert all(1 <= d <= 9 for d in row)


CHECKS["digit-combinations-with-sum"] = (b_dc, lambda r: [r.randint(1, 9), r.randint(1, 60)], "rowset")
VALIDATE["digit-combinations-with-sum"] = v_dc


# ---------------------------------------------------------------- fixed size combination sum with repeats
p = add(
    id="sized-combination-sum-with-repeats", title="Fixed-Size Combination Sum", diff="Medium", topic=TOPIC,
    fn="sizedCombinationSum", params=[("candidates", "int[]"), ("k", "int"), ("target", "int")], ret="int[][]", cmp="rowset",
    desc="<p>You are given an array <code>candidates</code> of distinct positive integers and two integers <code>k</code> and <code>target</code>. Return every collection of <strong>exactly <code>k</code> numbers</strong> taken from <code>candidates</code> whose sum is exactly <code>target</code>. A candidate may be used any number of times, including more than once in the same collection.</p><p>Two collections are the same if every candidate is used the same number of times, so list each one once with its numbers in non-decreasing order (for example <code>[2,2,3]</code>, never <code>[3,2,2]</code>). Rows may be returned in any order. If nothing works, return an empty array.</p>",
    constraints=["1 &le; candidates.length &le; 10", "1 &le; candidates[i] &le; 30, all values distinct", "1 &le; k &le; 8", "1 &le; target &le; 240", "The answer has fewer than 3,000 combinations"],
    hints=["Plain combination sum has no size limit. Here you also have to track how many numbers are still to be picked.",
           "Sort the candidates and only pick candidates at the current index or later (reuse allowed), so each multiset appears once in sorted order.",
           "With <code>m</code> numbers still to pick and <code>left</code> still to reach, the candidate <code>c</code> is only useful if <code>c * m &le; left</code> and the largest candidate times <code>m</code> is at least <code>left</code>. Stop the loop or the branch as soon as either test fails."],
    editorial=["Sort the candidates and recurse on <code>(start, m, left)</code>: <code>m</code> numbers still to choose and <code>left</code> still to add up. If <code>m == 0</code>, record the current list when <code>left == 0</code>. Otherwise loop <code>i</code> from <code>start</code>; choosing <code>cands[i]</code> recurses with the same <code>i</code> (repetition allowed), <code>m - 1</code> and <code>left - cands[i]</code>.",
               "Two bounds prune the tree. The remaining <code>m</code> numbers are each at least <code>cands[i]</code> (everything before <code>start</code> is excluded), so if <code>cands[i] * m &gt; left</code> this and all later candidates are too big: break. And they are each at most the largest candidate, so if <code>cands[-1] * m &lt; left</code> the branch can never reach the target: return. The number of rows is limited to under 3,000, so the output size stays small."],
    time="O(rows &middot; k) plus pruned search", space="O(k) extra",
    solution='''def sizedCombinationSum(candidates, k, target):
    cands = sorted(candidates)
    top = cands[-1]
    res = []
    cur = []

    def go(start, m, left):
        if m == 0:
            if left == 0:
                res.append(cur[:])
            return
        if top * m < left:
            return
        for i in range(start, len(cands)):
            c = cands[i]
            if c * m > left:
                break
            cur.append(c)
            go(i, m - 1, left - c)
            cur.pop()

    go(0, k, target)
    return res
''',
    tests=[[[1, 2, 3], 3, 6], [[2, 5], 2, 7], [[4], 2, 9], [[5], 1, 5], [[5], 1, 6], [[1, 2, 3, 4, 5, 6, 7, 8, 9, 10], 3, 15],
           [[3, 7, 9], 4, 24], [[1], 8, 8], [[30, 29, 28], 8, 232], [[2, 3, 5, 7], 5, 17], [[1, 2, 3, 4, 5, 6], 6, 20],
           [[10, 20, 30], 8, 240], [[2, 4, 6, 8], 3, 9]],
)
p["tests"].append([[3, 5, 8, 11, 14, 17, 20, 23, 26, 29], 6, 90])
p["tests"].append([[1, 2, 3, 5, 8, 13, 21, 30], 8, 60])


def b_scs(cands, k, target):
    return [list(c) for c in _cwr(sorted(cands), k) if sum(c) == target]


def v_scs(tests):
    for t in tests:
        cands, k, target = t["args"]
        res = t["expected"]
        assert 1 <= len(cands) <= 10 and len(set(cands)) == len(cands) and all(1 <= c <= 30 for c in cands)
        assert 1 <= k <= 8 and 1 <= target <= 240
        assert len(res) < 3000, ("too many rows", len(res))
        assert len({tuple(x) for x in res}) == len(res)
        for row in res:
            assert len(row) == k and sum(row) == target and row == sorted(row) and set(row) <= set(cands)


CHECKS["sized-combination-sum-with-repeats"] = (b_scs, lambda r: [r.sample(range(1, 12), r.randint(1, 5)), r.randint(1, 5), r.randint(1, 40)], "rowset")
VALIDATE["sized-combination-sum-with-repeats"] = v_scs


# ---------------------------------------------------------------- distinct k-subsets with duplicates
add(
    id="distinct-subsets-of-size-k", title="Distinct Subsets of Size K", diff="Medium", topic=TOPIC,
    fn="distinctSubsetsOfSize", params=[("nums", "int[]"), ("k", "int")], ret="int[][]", cmp="rowset",
    desc="<p>The integer array <code>nums</code> may contain repeated values. Return every <em>distinct</em> subset that has exactly <code>k</code> elements. Two subsets are the same when they hold the same values with the same multiplicities, regardless of which positions the values came from.</p><p>Write the values of each subset in non-decreasing order. Rows may be returned in any order. For <code>k = 0</code> the only subset is the empty one, so the answer is <code>[[]]</code>.</p>",
    constraints=["1 &le; nums.length &le; 12", "-10 &le; nums[i] &le; 10", "0 &le; k &le; nums.length"],
    hints=["First solve it for distinct values: choose k of them with a start index so that each set is produced once.",
           "Sort the array so that equal values are neighbours. Then two choices give the same subset exactly when they take the same number of copies of each value.",
           "Within one loop over candidate positions, skip <code>nums[i]</code> when <code>i &gt; start</code> and <code>nums[i] == nums[i-1]</code>. Also stop when fewer than the needed number of elements remain."],
    editorial=["Sort <code>nums</code>. Recurse on <code>(start, need)</code> with the current list. When <code>need == 0</code>, record a copy. Otherwise loop <code>i</code> from <code>start</code> to <code>n - need</code> (later positions cannot leave enough elements). Skip <code>i</code> if <code>i &gt; start</code> and <code>nums[i] == nums[i - 1]</code>: at one recursion level a value may be placed in the next slot only once, because a second copy would repeat everything the first copy already produced. A later copy may still be used deeper in the recursion, which is how rows such as <code>[2,2,5]</code> arise.",
               "Each node of the search tree that has enough elements left leads to at least one recorded row, so the time is proportional to the output size times <code>k</code>. The output is at most C(12, 6) = 924 rows."],
    time="O(C(n, k) &middot; k)", space="O(k) extra",
    solution='''def distinctSubsetsOfSize(nums, k):
    nums = sorted(nums)
    n = len(nums)
    res = []
    cur = []

    def go(start, need):
        if need == 0:
            res.append(cur[:])
            return
        for i in range(start, n - need + 1):
            if i > start and nums[i] == nums[i - 1]:
                continue
            cur.append(nums[i])
            go(i + 1, need - 1)
            cur.pop()

    go(0, k)
    return res
''',
    tests=[[[1, 2, 2], 2], [[1, 2, 3], 2], [[4, 4, 4], 2], [[5], 0], [[5], 1], [[1, 1, 2, 2], 2], [[3, 3, 3, 3], 4],
           [[-1, 0, 1, 2], 3], [[2, 2, 3, 3, 4, 4], 3], [[10, -10, 0, 10, -10, 0], 4],
           [[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, -1, -2], 6], [[1, 1, 1, 2, 2, 3, 3, 3, 4, 5, 5, 6], 6], [[0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1], 5]],
)


def b_dsk(nums, k):
    return [list(t) for t in {tuple(sorted(c)) for c in _combs(nums, k)}]


def v_dsk(tests):
    for t in tests:
        nums, k = t["args"]
        res = t["expected"]
        assert 1 <= len(nums) <= 12 and all(-10 <= x <= 10 for x in nums) and 0 <= k <= len(nums)
        assert len({tuple(x) for x in res}) == len(res) and len(res) >= 1
        assert all(len(r) == k and r == sorted(r) for r in res)


CHECKS["distinct-subsets-of-size-k"] = (b_dsk, lambda r: (lambda a: [a, r.randint(0, len(a))])(gen_arr(r, -3, 3, 1, 9)), "rowset")
VALIDATE["distinct-subsets-of-size-k"] = v_dsk


# ---------------------------------------------------------------- maximal subsets within budget
add(
    id="maximal-subsets-within-budget", title="Maximal Subsets Within a Budget", diff="Medium", topic=TOPIC,
    fn="maximalSubsets", params=[("nums", "int[]"), ("budget", "int")], ret="int[][]", cmp="rowset",
    desc="<p>You are given an array <code>nums</code> of distinct positive integers and an integer <code>budget</code>. A subset is <em>affordable</em> if the sum of its elements is at most <code>budget</code>. An affordable subset is <em>maximal</em> if no unused element of <code>nums</code> can be added to it while keeping it affordable.</p><p>Return every maximal subset. Write the values of each subset in increasing order. Rows may be returned in any order. If every single element costs more than <code>budget</code>, the empty subset is the only maximal one and the answer is <code>[[]]</code>.</p>",
    constraints=["1 &le; nums.length &le; 16", "1 &le; nums[i] &le; 100, all values distinct", "1 &le; budget &le; 1000", "The answer has fewer than 5,000 subsets"],
    hints=["A subset is maximal when every element left out is too expensive for the money that remains. Which left-out element is the easiest one to test?",
           "Sort the values. Decide in order, for each value, whether to take it or leave it, and keep the remaining budget.",
           "Only the cheapest value you left out matters: if it is bigger than the budget still unspent at the end, then all the other left-out values are too. Record the first value you skip."],
    editorial=["Sort ascending and run an include/skip recursion over the positions while carrying the remaining budget and the smallest value that was skipped so far (the first skipped one, since the order is ascending). At the end, the chosen set is affordable by construction (we only include a value that fits), and it is maximal exactly when nothing was skipped or the smallest skipped value is larger than the remaining budget: then every skipped value is too large to add.",
               "This tests maximality at the leaf in O(1) instead of looking at all left-out elements. Without more pruning the tree has up to 2<sup>n</sup> leaves, which is fine for n &le; 16. A cheap speed-up is that once a value does not fit, the include branch is impossible for it and all later (larger) values, so the branch can be closed immediately."],
    time="O(2<sup>n</sup>)", space="O(n) extra",
    solution='''def maximalSubsets(nums, budget):
    a = sorted(nums)
    n = len(a)
    res = []
    cur = []

    def go(i, left, first_skipped):
        if i == n:
            if first_skipped is None or first_skipped > left:
                res.append(cur[:])
            return
        if a[i] <= left:
            cur.append(a[i])
            go(i + 1, left - a[i], first_skipped)
            cur.pop()
        go(i + 1, left, a[i] if first_skipped is None else first_skipped)

    go(0, budget, None)
    return res
''',
    tests=[[[2, 3, 5], 7], [[4, 6], 3], [[1, 2, 3], 10], [[5], 5], [[5], 4], [[1, 2, 3, 4, 5], 6], [[10, 20, 30, 40], 50],
           [[3, 1, 4, 15, 9, 26], 30], [[7, 11, 13, 17, 19], 31], [[1, 2, 4, 8, 16, 32, 64], 70],
           [[5, 10, 15, 20, 25, 30, 35, 40, 45, 50], 100], [[1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23], 60],
           [[12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32, 34, 36, 38], 100]],
)


def b_mbs(nums, budget):
    n = len(nums)
    out = []
    for mask in range(1 << n):
        s = sum(nums[i] for i in range(n) if mask >> i & 1)
        if s > budget:
            continue
        if all(mask >> i & 1 or s + nums[i] > budget for i in range(n)):
            out.append(sorted(nums[i] for i in range(n) if mask >> i & 1))
    return out


def v_mbs(tests):
    for t in tests:
        nums, budget = t["args"]
        res = t["expected"]
        assert 1 <= len(nums) <= 16 and len(set(nums)) == len(nums) and all(1 <= x <= 100 for x in nums)
        assert 1 <= budget <= 1000
        assert 1 <= len(res) < 5000, ("answer size", len(res))
        assert len({tuple(x) for x in res}) == len(res)
        assert all(r == sorted(r) and sum(r) <= budget for r in res)


CHECKS["maximal-subsets-within-budget"] = (b_mbs, lambda r: [r.sample(range(1, 16), r.randint(1, 8)), r.randint(1, 40)], "rowset")
VALIDATE["maximal-subsets-within-budget"] = v_mbs


# ---------------------------------------------------------------- subsets with maximum OR
add(
    id="count-subsets-with-max-or", title="Subsets With Maximum OR", diff="Medium", topic=TOPIC,
    fn="countMaxOrSubsets", params=[("nums", "int[]")], ret="int", cmp="exact",
    desc="<p>The bitwise OR of a non-empty subset is the OR of all of its elements. Among all non-empty subsets of <code>nums</code> (chosen by position, so equal values at different positions count as different choices), the largest OR value that any subset can reach is the OR of the whole array.</p><p>Return how many non-empty subsets have an OR equal to that largest value.</p>",
    constraints=["1 &le; nums.length &le; 24", "1 &le; nums[i] &le; 10,000"],
    hints=["Take the OR of the entire array first: that is the target value, and no subset can exceed it.",
           "You can try all 2<sup>n</sup> subsets with an include/skip recursion carrying the running OR. For n = 24 that is slow; look for repeated states.",
           "Many different subsets have the same OR. Keep a map <code>or_value -> number of subsets</code> and update it for every element, instead of enumerating subsets."],
    editorial=["The maximum is <code>M = nums[0] | nums[1] | ...</code>. Direct backtracking carries the running OR and counts the leaves with OR equal to <code>M</code>, in O(2<sup>n</sup>). That is acceptable for n around 16 but too slow for 24.",
               "Because every value is below 2<sup>14</sup>, the OR of any subset is one of at most 16,384 numbers, far fewer than the number of subsets. Keep <code>cnt[v]</code> = number of subsets (including the empty one) whose OR is exactly <code>v</code>, starting from <code>{0: 1}</code>. For each element <code>x</code>, every existing state <code>v</code> either ignores <code>x</code> (stays) or takes it (adds <code>cnt[v]</code> to <code>cnt[v | x]</code>), so update from a snapshot of the old table. The answer is <code>cnt[M]</code>; the empty subset has OR 0 &lt; M and is never counted. This runs in O(n &middot; distinct ORs)."],
    time="O(n &middot; 2<sup>14</sup>)", space="O(2<sup>14</sup>)",
    solution='''def countMaxOrSubsets(nums):
    target = 0
    for x in nums:
        target |= x
    cnt = {0: 1}
    for x in nums:
        new = dict(cnt)
        for v, c in cnt.items():
            w = v | x
            new[w] = new.get(w, 0) + c
        cnt = new
    return cnt[target]
''',
    tests=[[[3, 1]], [[2, 2, 2]], [[3, 2, 1, 5]], [[1]], [[8]], [[1, 2, 4, 8]], [[1, 1, 1, 1, 1, 1, 1, 1, 1, 1]],
           [[5, 5, 2, 7]], [[10000, 10000, 1]], [[6, 3, 5, 9, 12, 10]]],
)
_r = rnd(9102)
p = [q for q in __import__("lib").P if q["id"] == "count-subsets-with-max-or"][0]
p["tests"].append([[1 << i for i in range(14)] + [_r.randint(1, 10000) for _ in range(10)]])
p["tests"].append([[_r.randint(1, 10000) for _ in range(24)]])
p["tests"].append([[_r.choice([1, 2, 4, 8, 16, 32, 64, 3, 5, 6, 9, 12, 129, 5000]) for _ in range(24)]])


def b_cmo(nums):
    n = len(nums)
    full = 0
    for x in nums:
        full |= x
    tot = 0
    for mask in range(1, 1 << n):
        o = 0
        for i in range(n):
            if mask >> i & 1:
                o |= nums[i]
        tot += o == full
    return tot


def v_cmo(tests):
    for t in tests:
        nums = t["args"][0]
        assert 1 <= len(nums) <= 24 and all(1 <= x <= 10000 for x in nums)


CHECKS["count-subsets-with-max-or"] = (b_cmo, lambda r: [gen_arr(r, 1, r.choice([4, 16, 100]), 1, 10)], "exact")
VALIDATE["count-subsets-with-max-or"] = v_cmo


# ---------------------------------------------------------------- kth combination
add(
    id="kth-combination-lexicographic", title="K-th Combination in Order", diff="Medium", topic=TOPIC,
    fn="kthCombination", params=[("n", "int"), ("r", "int"), ("k", "int")], ret="int[]", cmp="exact",
    desc="<p>List all combinations of <code>r</code> different numbers chosen from <code>1..n</code>, each written in increasing order, and sort the list lexicographically (compare the first numbers, then the second numbers, and so on). For <code>n = 4</code>, <code>r = 2</code> the list is <code>[1,2], [1,3], [1,4], [2,3], [2,4], [3,4]</code>.</p><p>Return the <code>k</code>-th combination of this list, counting from 1. Do not generate the whole list: it can contain over a hundred million combinations.</p>",
    constraints=["1 &le; r &le; n &le; 30", "1 &le; k &le; C(n, r)  (the number of combinations)"],
    hints=["Look at the first number of the answer. How many combinations start with 1? With 2?",
           "If the first number is <code>v</code>, the other <code>r - 1</code> numbers are chosen from <code>v+1..n</code>, which gives <code>C(n - v, r - 1)</code> combinations.",
           "Walk the first position through <code>v = 1, 2, ...</code>: if <code>k</code> is at most <code>C(n - v, r - 1)</code> take <code>v</code>, otherwise subtract that count from <code>k</code> and try the next <code>v</code>. Then repeat for the next position with the remaining numbers."],
    editorial=["This is unranking. Fix the next position and the smallest value allowed there, <code>v</code>. All combinations that place <code>v</code> there and then pick the remaining <code>m - 1</code> numbers from the values above <code>v</code> form one contiguous block of the sorted list, of size <code>C(n - v, m - 1)</code>. If <code>k</code> falls inside the block, <code>v</code> is the answer for this position; otherwise skip the block by subtracting its size from <code>k</code> and try <code>v + 1</code>.",
               "Repeating this for each of the <code>r</code> positions gives the answer with at most <code>n</code> block checks in total, since <code>v</code> never goes back. Total time O(n) binomial lookups, compared with the O(C(n, r)) of enumerating. For <code>n = 30</code> the largest <code>k</code> is C(30, 15) = 155,117,520."],
    time="O(n)", space="O(r)",
    solution='''from math import comb


def kthCombination(n, r, k):
    res = []
    v = 1
    for left in range(r, 0, -1):
        while True:
            block = comb(n - v, left - 1)
            if k <= block:
                break
            k -= block
            v += 1
        res.append(v)
        v += 1
    return res
''',
    tests=[[4, 2, 1], [4, 2, 4], [4, 2, 6], [1, 1, 1], [5, 5, 1], [5, 1, 5], [6, 3, 20], [6, 3, 10], [10, 4, 1], [10, 4, 210],
           [10, 4, 137], [30, 15, 1], [30, 15, 155117520], [30, 15, 77558760], [30, 1, 30], [30, 29, 17], [30, 3, 2000], [30, 10, 29999999]],
)


def b_kc(n, r, k):
    if _comb(n, r) <= 300000:
        return list(list(_combs(range(1, n + 1), r))[k - 1])
    # too many to list: unrank with a Pascal triangle instead of math.comb
    tri = [[1] + [0] * n for _ in range(n + 1)]
    for i in range(1, n + 1):
        for j in range(1, n + 1):
            tri[i][j] = tri[i - 1][j - 1] + tri[i - 1][j]
    out, v = [], 1
    for left in range(r, 0, -1):
        while k > tri[n - v][left - 1]:
            k -= tri[n - v][left - 1]
            v += 1
        out.append(v)
        v += 1
    return out


def g_kc(rr):
    n = rr.randint(1, 9)
    r = rr.randint(1, n)
    return [n, r, rr.randint(1, _comb(n, r))]


def v_kc(tests):
    for t in tests:
        n, r, k = t["args"]
        assert 1 <= r <= n <= 30 and 1 <= k <= _comb(n, r)
        e = t["expected"]
        assert len(e) == r and all(e[i] < e[i + 1] for i in range(r - 1)) and 1 <= e[0] and e[-1] <= n


CHECKS["kth-combination-lexicographic"] = (b_kc, g_kc, "exact")
VALIDATE["kth-combination-lexicographic"] = v_kc


# ================================================================== HARD

# ---------------------------------------------------------------- count subsets within budget
add(
    id="count-subsets-within-budget", title="Count Subsets Within Budget", diff="Hard", topic=TOPIC, tier="extra",
    fn="countSubsetsWithinBudget", params=[("nums", "int[]"), ("budget", "int")], ret="int", cmp="exact",
    desc="<p>Every subset of <code>nums</code> (chosen by position, so there are exactly <code>2<sup>n</sup></code> of them, the empty subset included) has a sum. Count the subsets whose sum is at most <code>budget</code>.</p><p>All elements are non-negative. Equal values at different positions count as different choices. The answer fits in a 32-bit integer because <code>n &le; 30</code>.</p>",
    constraints=["1 &le; nums.length &le; 30", "0 &le; nums[i] &le; 100,000,000", "0 &le; budget &le; 2,000,000,000"],
    hints=["Trying every subset takes 2<sup>30</sup> steps, which is far too slow. Split the array into two halves.",
           "Every subset is a pair: one subset of the left half and one of the right half. Each half has at most 2<sup>15</sup> subset sums, which you can list and sort.",
           "For each left sum <code>a</code>, count the right sums that are at most <code>budget - a</code>. With both lists sorted, move one pointer down while the other goes up, or use binary search."],
    editorial=["This is meet in the middle. Generate all subset sums of the first half <code>L</code> and of the second half <code>R</code> (at most 32,768 each, built by the usual doubling loop) and sort them. A whole subset has sum <code>a + b</code> with <code>a</code> from <code>L</code> and <code>b</code> from <code>R</code>, and every combination of an <code>a</code> and a <code>b</code> is a different subset, so we need the number of pairs with <code>a + b &le; budget</code>.",
               "Process <code>L</code> in increasing order while a pointer <code>j</code> into the sorted <code>R</code> only moves down: for a larger <code>a</code> the limit <code>budget - a</code> is smaller, so the count of admissible <code>b</code> values never grows. Add <code>j</code> (the number of right sums within the limit) for each <code>a</code>, and stop once <code>a</code> alone exceeds the budget. Sorting dominates, so the time is O(2<sup>n/2</sup> &middot; n) instead of O(2<sup>n</sup>)."],
    time="O(2<sup>n/2</sup> &middot; n)", space="O(2<sup>n/2</sup>)",
    solution='''def countSubsetsWithinBudget(nums, budget):
    def sums(arr):
        s = [0]
        for x in arr:
            s = s + [v + x for v in s]
        s.sort()
        return s

    h = len(nums) // 2
    left = sums(nums[:h])
    right = sums(nums[h:])
    j = len(right)
    total = 0
    for a in left:
        if a > budget:
            break
        while j > 0 and right[j - 1] + a > budget:
            j -= 1
        total += j
    return total
''',
    tests=[[[1, 2, 3], 3], [[5], 4], [[5], 5], [[0, 0, 0], 0], [[4, 4, 4, 4], 8], [[10, 20, 30], 25], [[1, 1, 1, 1, 1, 1], 3],
           [[100000000] * 30, 2000000000], [[100000000] * 30, 1999999999], [[7, 3, 9, 1, 12, 5, 8], 20], [[2, 4, 6], 0]],
)
_r = rnd(9103)
for _p in __import__("lib").P:
    if _p["id"] == "count-subsets-within-budget":
        _a = [_r.randint(0, 100000000) for _ in range(30)]
        _p["tests"].append([_a, sum(_a) // 2])
        _a = [_r.randint(0, 1000) for _ in range(30)]
        _p["tests"].append([_a, 3000])
        _a = [_r.randint(1, 100000000) for _ in range(29)]
        _p["tests"].append([_a, 700000000])


def b_csb(nums, budget):
    n = len(nums)
    c = 0
    for mask in range(1 << n):
        s = 0
        for i in range(n):
            if mask >> i & 1:
                s += nums[i]
        c += s <= budget
    return c


def v_csb(tests):
    for t in tests:
        nums, budget = t["args"]
        assert 1 <= len(nums) <= 30 and all(0 <= x <= 10 ** 8 for x in nums) and 0 <= budget <= 2 * 10 ** 9


CHECKS["count-subsets-within-budget"] = (b_csb, lambda r: [gen_arr(r, 0, r.choice([3, 10, 50]), 1, 10), r.randint(0, 60)], "exact")
VALIDATE["count-subsets-within-budget"] = v_csb


# ---------------------------------------------------------------- count sub-multisets with sum in range
add(
    id="count-submultisets-sum-in-range", title="Distinct Subsets With Sum in Range", diff="Hard", topic=TOPIC, tier="extra",
    fn="countSubMultisets", params=[("nums", "int[]"), ("lo", "int"), ("hi", "int")], ret="int", cmp="exact",
    desc="<p>The array <code>nums</code> of non-negative integers may contain repeated values. Two subsets are considered the <em>same</em> when they contain every value the same number of times, no matter which positions the values come from. The empty subset has sum <code>0</code> and is a subset like any other.</p><p>Return the number of distinct subsets whose sum is between <code>lo</code> and <code>hi</code> inclusive, modulo <code>1,000,000,007</code>.</p>",
    constraints=["1 &le; nums.length &le; 20,000", "0 &le; nums[i] &le; 3,000", "The sum of all elements is at most 3,000", "0 &le; lo &le; hi &le; 3,000"],
    hints=["Count the multiplicity of every distinct value. A distinct subset is a choice of how many copies of each value to take.",
           "That is a bounded knapsack over sums <code>0..hi</code>: <code>dp[s]</code> = number of ways to reach sum <code>s</code> with the values handled so far. The value 0 is special, it never changes a sum.",
           "For a value <code>v</code> with <code>c</code> copies, the new table is <code>new[s] = dp[s] + dp[s-v] + ... + dp[s-c*v]</code>. Compute it in O(1) per cell with <code>new[s] = new[s-v] + dp[s] - dp[s-(c+1)*v]</code>."],
    editorial=["Zeros are free: if the value 0 occurs <code>z</code> times, every other selection can be extended with 0 to <code>z</code> zeros, which multiplies the answer by <code>z + 1</code>. Start the table with <code>dp[0] = z + 1</code> and treat the other values.",
               "For each distinct positive value <code>v</code> occurring <code>c</code> times the new table is <code>new[s] = sum of dp[s - j*v] for j = 0..c</code>. A sliding-window identity makes this O(1) per cell: <code>new[s-v] = sum of dp[s - j*v] for j = 1..c+1</code>, so <code>new[s] = new[s-v] + dp[s] - dp[s-(c+1)*v]</code> (the last term is zero when the index is negative). Every operation is taken modulo 10<sup>9</sup>+7.",
               "Because the total sum is at most 3,000, there are only about 77 distinct positive values (1 + 2 + ... + 77 &gt; 3,000), so the work is about 77 &middot; 3,000 cell updates. The answer is the sum of <code>dp[lo..hi]</code>."],
    time="O(d &middot; hi + n) where d = distinct values", space="O(hi)",
    solution='''def countSubMultisets(nums, lo, hi):
    MOD = 1_000_000_007
    cnt = {}
    for x in nums:
        cnt[x] = cnt.get(x, 0) + 1
    dp = [0] * (hi + 1)
    dp[0] = cnt.pop(0, 0) + 1
    for v, c in cnt.items():
        if v > hi:
            continue
        new = dp[:]
        step = (c + 1) * v
        for s in range(v, hi + 1):
            t = new[s - v] + dp[s]
            if s >= step:
                t -= dp[s - step]
            new[s] = t % MOD
        dp = new
    return sum(dp[lo:hi + 1]) % MOD
''',
    tests=[[[1, 2, 2, 3], 6, 6], [[2, 1, 4, 2, 7], 1, 5], [[1, 2, 1, 3, 5, 2], 3, 5], [[0], 0, 0], [[0, 0, 0], 0, 0],
           [[0, 0, 5], 0, 5], [[1, 1, 1, 1], 2, 3], [[5], 1, 4], [[3, 3, 3], 3, 6], [[4, 2, 2, 1, 1, 1], 0, 11],
           [[2000, 1000], 1000, 3000], [[7, 7, 7, 7, 7, 7], 14, 28]],
)
_r = rnd(9104)
for _p in __import__("lib").P:
    if _p["id"] == "count-submultisets-sum-in-range":
        _p["tests"].append([[0] * 5000 + list(range(1, 71)) + [_r.randint(1, 70) for _ in range(5)], 100, 2000])
        _a = [_r.randint(1, 12) for _ in range(500)]
        while sum(_a) > 3000:
            _a.pop()
        _p["tests"].append([_a, 500, 1500])
        _p["tests"].append([[1] * 3000, 1000, 2500])


def b_csm(nums, lo, hi):
    cnt = {}
    for x in nums:
        cnt[x] = cnt.get(x, 0) + 1
    keys = sorted(cnt)
    tot = 0
    for choice in _product(*[range(cnt[k] + 1) for k in keys]):
        s = sum(k * c for k, c in zip(keys, choice))
        tot += lo <= s <= hi
    return tot % MOD


def g_csm(r):
    a = gen_arr(r, 0, r.choice([3, 6]), 1, 9)
    lo = r.randint(0, 12)
    return [a, lo, lo + r.randint(0, 20)]


def v_csm(tests):
    for t in tests:
        nums, lo, hi = t["args"]
        assert 1 <= len(nums) <= 20000 and all(0 <= x <= 3000 for x in nums) and sum(nums) <= 3000
        assert 0 <= lo <= hi <= 3000


CHECKS["count-submultisets-sum-in-range"] = (b_csm, g_csm, "exact")
VALIDATE["count-submultisets-sum-in-range"] = v_csm


# ---------------------------------------------------------------- equal sum disjoint pairs
add(
    id="count-equal-sum-disjoint-subset-pairs", title="Equal-Sum Disjoint Subset Pairs", diff="Hard", topic=TOPIC, tier="extra",
    fn="countEqualSumPairs", params=[("nums", "int[]")], ret="int", cmp="exact",
    desc="<p>Choose two <em>non-empty</em> subsets <code>A</code> and <code>B</code> of the positions of <code>nums</code> such that they share no position and the sum of the values in <code>A</code> equals the sum of the values in <code>B</code>. The pair is ordered: swapping the roles of <code>A</code> and <code>B</code> gives a different pair, and different positions with equal values count as different choices.</p><p>Return the number of such pairs modulo <code>1,000,000,007</code>.</p><p>For <code>[1, 2, 3]</code> the pairs are <code>A = {1, 2}, B = {3}</code> and the swapped pair, so the answer is 2.</p>",
    constraints=["1 &le; nums.length &le; 30", "1 &le; nums[i] &le; 60"],
    hints=["Give every element one of three roles: in A, in B, or in neither. That is 3<sup>n</sup> assignments, too many for n = 30.",
           "You never need the two sums separately, only their difference <code>sum(A) - sum(B)</code>. Count assignments per difference value.",
           "Keep a table <code>ways[d]</code>. For each element <code>x</code>, an assignment with difference <code>d</code> moves to <code>d</code> (neither), <code>d + x</code> (in A) or <code>d - x</code> (in B). Because all values are positive, equal sums with <code>A</code> non-empty force <code>B</code> to be non-empty, so only the empty-empty assignment must be removed from <code>ways[0]</code>."],
    editorial=["Count assignments of every position to {A, B, neither} by the difference <code>d = sum(A) - sum(B)</code>. The differences lie in <code>[-S, S]</code> with <code>S = sum(nums) &le; 1,800</code>, so a table (or hash map) of at most 3,601 entries is enough, updated once per element with the three transitions above. The total work is about 30 &middot; 3,601 &middot; 3 updates.",
               "At the end <code>ways[0]</code> counts every assignment with equal sums. That includes the assignment where nothing is chosen at all. Since all values are positive, a non-empty <code>A</code> has positive sum, so <code>B</code> has positive sum and is non-empty as well, and the reverse holds too; hence the only invalid assignment with difference 0 is the all-neither one, and the answer is <code>ways[0] - 1</code> modulo 10<sup>9</sup>+7. Backtracking over 3<sup>n</sup> assignments is only a viable brute force for very small n; the difference table removes the exponential."],
    time="O(n &middot; S)", space="O(S)",
    solution='''def countEqualSumPairs(nums):
    MOD = 1_000_000_007
    total = sum(nums)
    off = total
    ways = [0] * (2 * total + 1)
    ways[off] = 1
    for x in nums:
        new = ways[:]
        for d in range(2 * total + 1):
            w = ways[d]
            if w:
                if d + x <= 2 * total:
                    new[d + x] = (new[d + x] + w) % MOD
                if d - x >= 0:
                    new[d - x] = (new[d - x] + w) % MOD
        ways = new
    return (ways[off] - 1) % MOD
''',
    tests=[[[1, 2, 3]], [[1, 1]], [[2, 2, 2]], [[5]], [[1, 2]], [[1, 1, 1, 1]], [[3, 5, 8]], [[1, 2, 3, 4, 5, 6]],
           [[60, 60]], [[4, 4, 4, 4, 4, 4, 4, 4]], [[7, 11, 13, 17, 19, 23, 29]]],
)
_r = rnd(9105)
for _p in __import__("lib").P:
    if _p["id"] == "count-equal-sum-disjoint-subset-pairs":
        _p["tests"].append([[_r.randint(1, 60) for _ in range(30)]])
        _p["tests"].append([[_r.randint(1, 10) for _ in range(30)]])
        _p["tests"].append([[60] * 30])
        _p["tests"].append([[1] * 30])


def b_esp(nums):
    n = len(nums)
    tot = 0
    for roles in _product(range(3), repeat=n):
        a = sum(nums[i] for i in range(n) if roles[i] == 1)
        b = sum(nums[i] for i in range(n) if roles[i] == 2)
        if a == b and 1 in roles and 2 in roles:
            tot += 1
    return tot % MOD


def v_esp(tests):
    for t in tests:
        nums = t["args"][0]
        assert 1 <= len(nums) <= 30 and all(1 <= x <= 60 for x in nums)


CHECKS["count-equal-sum-disjoint-subset-pairs"] = (b_esp, lambda r: [gen_arr(r, 1, r.choice([3, 8]), 1, 7)], "exact")
VALIDATE["count-equal-sum-disjoint-subset-pairs"] = v_esp
