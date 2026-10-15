"""Problems: sorting, selection and order statistics (ranks, kth element, median, top-k in order). See data/lib.py for the registry."""
import bisect
from itertools import combinations

from lib import add, rnd, CHECKS, VALIDATE, gen_arr  # noqa: F401

INT_MIN, INT_MAX = -(2 ** 31), 2 ** 31 - 1
T = "Sorting"
B = 10 ** 9


# ================================================================ EASY

# ---------------------------------------------------------------- dense rank
p = add(
    id="dense-rank-of-each-element", title="Dense Rank of Each Element", diff="Easy", topic=T, tier="common",
    fn="denseRanks", params=[("nums", "int[]")], ret="int[]", cmp="exact",
    desc="<p>Replace every value of <code>nums</code> by its <em>dense rank</em>: the smallest value gets rank 1, and the rank grows by exactly one each time the value grows to the next larger <em>distinct</em> value. Equal values share the same rank, and no rank number is skipped.</p><p>Return the array of ranks in the original order.</p><pre>nums  = [40, 10, 20, 10, 40]\ndistinct sorted = 10, 20, 40  -> ranks 1, 2, 3\nanswer = [3, 1, 2, 1, 3]</pre>",
    constraints=["0 &le; nums.length &le; 6,000", "-2<sup>31</sup> &le; nums[i] &le; 2<sup>31</sup> - 1"],
    hints=["The rank of a value only depends on how many <em>different</em> smaller values exist.",
           "Remove duplicates and sort. The position of a value in that sorted list is its rank minus one.",
           "Build a map from value to rank by walking the sorted distinct values once, then rewrite the array with a lookup per element."],
    editorial=["Collect the distinct values with a set and sort them. The i-th smallest distinct value (counting from 1) has rank i, so store this mapping in a dictionary and replace every element by its entry.",
               "Sorting the distinct values costs O(n log n) and the mapping pass is O(n). Doing a binary search per element instead of a dictionary also works at the same total cost, and sorting pairs (value, index) is an alternative that avoids the hash map but needs the extra step of skipping equal neighbours."],
    time="O(n log n)", space="O(n)",
    solution='''def denseRanks(nums):
    rank = {}
    for v in sorted(set(nums)):
        rank[v] = len(rank) + 1
    return [rank[v] for v in nums]
''',
    tests=[[[40, 10, 20, 10, 40]], [[100, 100, 100]], [[]], [[7]], [[3, 2, 1]], [[1, 2, 3]], [[-1, -1, -2]],
           [[INT_MIN, INT_MAX, 0, INT_MIN]], [[0, 0, 5, 5, -5, -5]], [[2, 1, 2, 1, 3, 3, 2]]],
)
_r = rnd(41001)
p["tests"].append([[_r.randint(-B, B) for _ in range(3000)]])
p["tests"].append([[_r.randint(0, 50) for _ in range(6000)]])
p["tests"].append([list(range(2500, 0, -1))])


def b_dense(nums):
    return [len({y for y in nums if y < x}) + 1 for x in nums]


def v_dense(tests):
    for t in tests:
        nums = t["args"][0]
        assert len(nums) <= 6000


CHECKS["dense-rank-of-each-element"] = (b_dense, lambda r: [gen_arr(r, -5, 5, 0, 10)], "exact")
VALIDATE["dense-rank-of-each-element"] = v_dense


# ---------------------------------------------------------------- k largest, original order
p = add(
    id="largest-k-subsequence-in-order", title="K Largest Values in Original Order", diff="Easy", topic=T, tier="common",
    fn="topKInOrder", params=[("nums", "int[]"), ("k", "int")], ret="int[]", cmp="exact",
    desc="<p>Choose exactly <code>k</code> elements of <code>nums</code> that are the <code>k</code> largest. When several elements share a value that sits on the boundary, prefer the one with the <em>smaller index</em>.</p><p>Return the chosen values <strong>in the order in which they appear in <code>nums</code></strong>.</p><pre>nums = [5, 2, 7, 2, 9, 7], k = 3\nlargest three: 9 (index 4), 7 (index 2), 7 (index 5)\nanswer = [7, 9, 7]\n\nnums = [3, 5, 3, 1], k = 2\nlargest: 5, then one of the two 3s -> take the earlier one (index 0)\nanswer = [3, 5]</pre>",
    constraints=["1 &le; k &le; nums.length &le; 5,000", "-10<sup>9</sup> &le; nums[i] &le; 10<sup>9</sup>"],
    hints=["Sorting the whole array loses the original order, but you could sort indices instead of values.",
           "Find the k-th largest value <code>t</code>. Everything larger than <code>t</code> is surely chosen, and some of the elements equal to <code>t</code> are chosen as well. How many?",
           "Count how many elements are strictly greater than <code>t</code>; the remaining <code>k - that</code> slots go to the first elements equal to <code>t</code>. Then one left-to-right pass collects the answer."],
    editorial=["Let <code>t</code> be the k-th largest value (counting duplicates). Every element greater than <code>t</code> must be in the answer, and exactly <code>need = k - (count of elements greater than t)</code> elements equal to <code>t</code> are needed. The tie rule says the earliest ones win.",
               "Walk through the array from left to right: take <code>x</code> if <code>x &gt; t</code>, or if <code>x == t</code> and <code>need &gt; 0</code> (then decrement <code>need</code>). The output is automatically in original order.",
               "Finding <code>t</code> by sorting costs O(n log n); quickselect finds it in expected O(n). The final pass is O(n)."],
    time="O(n log n)", space="O(n)",
    solution='''def topKInOrder(nums, k):
    t = sorted(nums, reverse=True)[k - 1]
    need = k - sum(1 for x in nums if x > t)
    out = []
    for x in nums:
        if x > t:
            out.append(x)
        elif x == t and need > 0:
            out.append(x)
            need -= 1
    return out
''',
    tests=[[[5, 2, 7, 2, 9, 7], 3], [[3, 5, 3, 1], 2], [[4], 1], [[1, 2, 3, 4], 4], [[2, 2, 2, 2], 2],
           [[-1, -5, -3, -2], 2], [[1, 3, 3, 3, 2], 3], [[9, 1, 9, 1, 9], 2], [[0, 0, 1, 0], 1],
           [[B, -B, B, 0], 3]],
)
_r = rnd(41002)
p["tests"].append([[_r.randint(-B, B) for _ in range(3500)], 1234])
p["tests"].append([[_r.randint(-5, 5) for _ in range(3500)], 1750])
p["tests"].append([[_r.randint(-B, B) for _ in range(2500)], 2500])


def b_topk(nums, k):
    used = [False] * len(nums)
    for _ in range(k):
        best = -1
        for i, x in enumerate(nums):
            if not used[i] and (best == -1 or x > nums[best]):
                best = i
        used[best] = True
    return [x for i, x in enumerate(nums) if used[i]]


def g_topk(r):
    n = r.randint(1, 9)
    return [gen_arr(r, -3, 3, n, n), r.randint(1, n)]


def v_topk(tests):
    for t in tests:
        nums, k = t["args"]
        assert 1 <= k <= len(nums) <= 5000
        assert all(-B <= x <= B for x in nums)
        assert len(t["expected"]) == k


CHECKS["largest-k-subsequence-in-order"] = (b_topk, g_topk, "exact")
VALIDATE["largest-k-subsequence-in-order"] = v_topk


# ---------------------------------------------------------------- median doubled
p = add(
    id="median-of-unsorted-array-doubled", title="Median of an Unsorted Array (Doubled)", diff="Easy", topic=T, tier="common",
    fn="doubledMedian", params=[("nums", "int[]")], ret="int", cmp="exact",
    desc="<p>The median of a list is its middle value after sorting; for an even length it is the average of the two middle values. To stay with integers, return <strong>twice the median</strong>: the sum of the two middle sorted values for an even length, or the middle value counted twice for an odd length.</p><p>You are not required to sort the whole array. A selection algorithm such as quickselect finds a middle value in expected linear time.</p><pre>nums = [7, 1, 5]        sorted 1 5 7      median 5      answer 10\nnums = [4, 9, 1, 2]     sorted 1 2 4 9    median 3      answer 6</pre>",
    constraints=["1 &le; nums.length &le; 7,000", "-10<sup>9</sup> &le; nums[i] &le; 10<sup>9</sup>"],
    hints=["Sorting gives the answer in O(n log n). The question only needs the one or two middle positions, not a full order.",
           "Choose a pivot and split the values into smaller, equal and larger groups. Which group contains the position you are looking for?",
           "Quickselect: keep looking for index <code>n // 2</code> (and, for even n, <code>n // 2 - 1</code>) and discard the groups that cannot contain it."],
    editorial=["With zero-based sorted positions, the lower middle is at <code>(n - 1) // 2</code> and the upper middle at <code>n // 2</code>. For odd n these are the same position, so adding them yields exactly twice the median; for even n the sum is twice the average. One formula covers both cases.",
               "Each position is found with quickselect: pick a random pivot, split into elements less than, equal to and greater than the pivot, and continue in the part that holds the target rank. The expected work is n + n/2 + n/4 + ... = O(n). Using a three-way split keeps the algorithm fast on arrays with many equal values.",
               "Plain sorting (O(n log n)) is perfectly acceptable at these sizes, but the selection version is the one interviewers usually ask for."],
    time="O(n) expected", space="O(n)",
    solution='''import random


def doubledMedian(nums):
    n = len(nums)
    rng = random.Random(12345)

    def select(arr, idx):
        while True:
            pivot = arr[rng.randrange(len(arr))]
            lo = [x for x in arr if x < pivot]
            eq = len(arr) - len(lo) - sum(1 for x in arr if x > pivot)
            if idx < len(lo):
                arr = lo
            elif idx < len(lo) + eq:
                return pivot
            else:
                idx -= len(lo) + eq
                arr = [x for x in arr if x > pivot]

    return select(list(nums), (n - 1) // 2) + select(list(nums), n // 2)
''',
    tests=[[[7, 1, 5]], [[4, 9, 1, 2]], [[5]], [[2, 2]], [[B, -B]], [[B, B, B]], [[-3, -1, -2, -4]], [[1, 2, 3, 4, 5, 6]],
           [[0, 0, 0, 1]], [[10, 10, 10, 10, 1]]],
)
_r = rnd(41003)
p["tests"].append([[_r.randint(-B, B) for _ in range(4500)]])
p["tests"].append([[_r.randint(-3, 3) for _ in range(4999)]])
p["tests"].append([[B] * 1500 + [-B] * 1500])


def b_median(nums):
    n = len(nums)

    def at(idx):
        for x in nums:
            less = sum(1 for y in nums if y < x)
            leq = sum(1 for y in nums if y <= x)
            if less <= idx < leq:
                return x

    return at((n - 1) // 2) + at(n // 2)


def v_median(tests):
    for t in tests:
        nums = t["args"][0]
        assert 1 <= len(nums) <= 7000
        assert all(-B <= x <= B for x in nums)


CHECKS["median-of-unsorted-array-doubled"] = (b_median, lambda r: [gen_arr(r, -5, 5, 1, 9)], "exact")
VALIDATE["median-of-unsorted-array-doubled"] = v_median


# ================================================================ MEDIUM

# ---------------------------------------------------------------- kth largest prefix xor
p = add(
    id="kth-largest-prefix-xor-in-grid", title="Kth Largest Prefix XOR in a Grid", diff="Medium", topic=T, tier="common",
    fn="kthPrefixXor", params=[("matrix", "int[][]"), ("k", "int")], ret="int", cmp="exact",
    desc="<p>For a cell <code>(a, b)</code> of the grid <code>matrix</code>, define its <em>value</em> as the XOR of all numbers <code>matrix[i][j]</code> with <code>0 &le; i &le; a</code> and <code>0 &le; j &le; b</code> (the rectangle from the top-left corner to that cell).</p><p>Every cell has a value; collect all <code>m * n</code> values (duplicates stay) and return the <code>k</code>-th largest of them.</p><pre>matrix = [[5, 2],\n          [1, 6]]\nvalues = [[5, 7],\n          [4, 0]]   (7 = 5^2, 4 = 5^1, 0 = 5^2^1^6)\nk = 2 -> sorted descending 7, 5, 4, 0 -> answer 5</pre>",
    constraints=["1 &le; m, n &le; 60 (m rows, n columns)", "0 &le; matrix[i][j] &le; 10<sup>9</sup>", "1 &le; k &le; m * n"],
    hints=["Computing every rectangle XOR from scratch would be far too slow. Can a value reuse its neighbours' values?",
           "XOR cancels itself: value(a, b) can be built from value(a-1, b), value(a, b-1), value(a-1, b-1) and the cell itself, just like 2D prefix sums.",
           "Once all prefix values are known, you only need the k-th largest of m*n numbers: sort them or use a size-k min-heap or quickselect."],
    editorial=["Use the 2D prefix recurrence <code>P[a][b] = P[a-1][b] ^ P[a][b-1] ^ P[a-1][b-1] ^ matrix[a][b]</code>. The two neighbours both contain the block P[a-1][b-1], and XOR-ing a value twice cancels it, so that block would vanish from the result; XOR-ing P[a-1][b-1] in once more restores it exactly once, and the cell itself completes the rectangle.",
               "Collect the m*n prefix values and pick the k-th largest. Sorting costs O(mn log(mn)); a heap of size k gives O(mn log k); quickselect gives expected O(mn). With at most 3,600 cells any of them is fast.",
               "Whole solution: O(mn) for the prefix table plus the selection step."],
    time="O(mn log(mn))", space="O(mn)",
    solution='''def kthPrefixXor(matrix, k):
    m, n = len(matrix), len(matrix[0])
    prev = [0] * (n + 1)
    vals = []
    for i in range(m):
        cur = [0] * (n + 1)
        for j in range(n):
            cur[j + 1] = prev[j + 1] ^ cur[j] ^ prev[j] ^ matrix[i][j]
            vals.append(cur[j + 1])
        prev = cur
    vals.sort(reverse=True)
    return vals[k - 1]
''',
    tests=[[[[5, 2], [1, 6]], 2], [[[5, 2], [1, 6]], 1], [[[5, 2], [1, 6]], 4], [[[0]], 1], [[[7]], 1],
           [[[1, 1, 1]], 2], [[[1], [1], [1]], 3], [[[3, 3], [3, 3]], 2], [[[B, 0], [0, B]], 3],
           [[[1, 2, 3], [4, 5, 6], [7, 8, 9]], 5]],
)
_r = rnd(41004)
p["tests"].append([[[_r.randint(0, B) for _ in range(60)] for _ in range(60)], 1800])
p["tests"].append([[[_r.randint(0, 3) for _ in range(60)] for _ in range(55)], 777])
p["tests"].append([[[_r.randint(0, B) for _ in range(60)] for _ in range(3)], 180])


def b_pxor(matrix, k):
    m, n = len(matrix), len(matrix[0])
    vals = []
    for a in range(m):
        for b in range(n):
            x = 0
            for i in range(a + 1):
                for j in range(b + 1):
                    x ^= matrix[i][j]
            vals.append(x)
    return sorted(vals)[len(vals) - k]


def g_pxor(r):
    m, n = r.randint(1, 4), r.randint(1, 4)
    return [[[r.randint(0, 7) for _ in range(n)] for _ in range(m)], r.randint(1, m * n)]


def v_pxor(tests):
    for t in tests:
        mat, k = t["args"]
        assert 1 <= len(mat) <= 60 and all(len(row) == len(mat[0]) for row in mat) and 1 <= len(mat[0]) <= 60
        assert all(0 <= x <= B for row in mat for x in row)
        assert 1 <= k <= len(mat) * len(mat[0])


CHECKS["kth-largest-prefix-xor-in-grid"] = (b_pxor, g_pxor, "exact")
VALIDATE["kth-largest-prefix-xor-in-grid"] = v_pxor


# ---------------------------------------------------------------- max median with k increments
p = add(
    id="max-median-with-k-increments", title="Maximum Median with K Increments", diff="Medium", topic=T, tier="common",
    fn="maxMedian", params=[("nums", "int[]"), ("k", "int")], ret="int", cmp="exact",
    desc="<p>In one operation you may add <code>1</code> to any single element of <code>nums</code>. You may perform <strong>at most</strong> <code>k</code> operations (the same element may be chosen again and again).</p><p>The <em>median</em> of an array of length <code>n</code> is the element at zero-based position <code>n // 2</code> after sorting (so for an even length it is the larger of the two middle values). Return the largest median you can reach.</p><pre>nums = [2, 9, 4, 7], k = 5\nsorted [2, 4, 7, 9], median = 7\nadd 3 to 7 and 1 to 9 -> [2, 4, 10, 10], median 10\nanswer = 10</pre>",
    constraints=["1 &le; nums.length &le; 5,000", "-10<sup>9</sup> &le; nums[i] &le; 10<sup>9</sup>", "0 &le; k &le; 10<sup>9</sup>"],
    hints=["Raising anything below the median position is useless. Which elements decide the median?",
           "To get a median of at least <code>m</code>, the upper half of the sorted array (from position <code>n // 2</code> on) must consist of values at least <code>m</code>. What is the cheapest way to achieve that?",
           "The cost of reaching median <code>m</code> is the sum of <code>max(0, m - x)</code> over the upper half, and it grows with <code>m</code>, so binary search the largest affordable <code>m</code>."],
    editorial=["Sort the array. The median is the smallest element of the upper half <code>a[n//2:]</code>. For the median to be at least <code>m</code>, all <code>n - n//2</code> elements of that half must be at least <code>m</code>, and it never helps to touch elements outside the half: raising the largest candidates is always cheapest, and those are exactly the upper-half elements.",
               "So <code>cost(m) = sum(max(0, m - x) for x in upper half)</code>. It is non-decreasing in <code>m</code>, so binary search the largest <code>m</code> between the current median and the current median plus <code>k</code> with <code>cost(m) &le; k</code>.",
               "Sorting is O(n log n) and the binary search adds O(n log k). A direct linear-after-sort water-filling approach (raise the smallest of the upper half until it meets the next one, and so on) gives the same result."],
    time="O(n log n + n log k)", space="O(n)",
    solution='''def maxMedian(nums, k):
    a = sorted(nums)
    half = a[len(a) // 2:]
    lo, hi = half[0], half[0] + k
    while lo < hi:
        mid = (lo + hi + 1) // 2
        cost = 0
        for x in half:
            if x >= mid:
                break
            cost += mid - x
            if cost > k:
                break
        if cost <= k:
            lo = mid
        else:
            hi = mid - 1
    return lo
''',
    tests=[[[2, 9, 4, 7], 5], [[1, 2, 3], 3], [[5], 0], [[5], 10], [[1, 1, 1, 1], 0], [[1, 1, 1, 1], 8], [[1, 1, 1, 1], 7],
           [[-5, -4, -3], 4], [[B, B, B], B], [[-B, -B], B], [[3, 1, 2, 10, 20], 1], [[3, 1, 2, 10, 20], 100]],
)
_r = rnd(41005)
p["tests"].append([[_r.randint(-B, B) for _ in range(5000)], B])
p["tests"].append([[_r.randint(0, 100) for _ in range(4999)], 123456789])
p["tests"].append([[_r.randint(-B, B) for _ in range(3000)], 0])


def b_maxmed(nums, k):
    n = len(nums)
    best = [None]

    def go(i, left, cur):
        if i == n:
            med = sorted(cur)[n // 2]
            if best[0] is None or med > best[0]:
                best[0] = med
            return
        for add_ in range(left + 1):
            cur[i] += add_
            go(i + 1, left - add_, cur)
            cur[i] -= add_

    go(0, k, list(nums))
    return best[0]


def g_maxmed(r):
    n = r.randint(1, 4)
    return [gen_arr(r, -4, 6, n, n), r.randint(0, 5)]


def v_maxmed(tests):
    for t in tests:
        nums, k = t["args"]
        assert 1 <= len(nums) <= 5000 and 0 <= k <= B
        assert all(-B <= x <= B for x in nums)


CHECKS["max-median-with-k-increments"] = (b_maxmed, g_maxmed, "exact")
VALIDATE["max-median-with-k-increments"] = v_maxmed


# ---------------------------------------------------------------- operations to make median equal target
p = add(
    id="operations-to-make-median-equal-target", title="Operations to Make the Median Equal a Target", diff="Medium", topic=T, tier="common",
    fn="medianOperations", params=[("nums", "int[]"), ("target", "int")], ret="int", cmp="exact",
    desc="<p>In one operation you may add <code>1</code> to, or subtract <code>1</code> from, any single element of <code>nums</code>. The <em>median</em> is the element at zero-based position <code>n // 2</code> after sorting (the larger middle value when <code>n</code> is even).</p><p>Return the minimum number of operations after which the median of the array equals <code>target</code>.</p><pre>nums = [2, 5, 6, 8, 5], target = 4\nsorted [2, 5, 5, 6, 8]; change one 5 to 4 (the median) and the other 5 to 4\n-> [2, 4, 4, 6, 8], median 4, 2 operations\nanswer = 2</pre>",
    constraints=["1 &le; nums.length &le; 6,000", "-10<sup>5</sup> &le; nums[i], target &le; 10<sup>5</sup>"],
    hints=["After the changes, the element in the median position equals <code>target</code>, everything to its left is at most <code>target</code> and everything to its right is at least <code>target</code>.",
           "Sort first. Which elements of the sorted array can stay exactly where they are without cost?",
           "In sorted order: lower-half elements larger than <code>target</code> must come down, upper-half elements smaller than <code>target</code> must come up, and the median element itself must move to <code>target</code>. Sum these distances."],
    editorial=["Sort <code>a</code> and let <code>mid = n // 2</code>. Moving an element only changes the sorted order if it crosses another one, and the cheapest way to produce a median of exactly <code>target</code> is to keep the sorted order: the first <code>mid</code> elements must end up at most <code>target</code>, the element at <code>mid</code> must be exactly <code>target</code>, and the remaining ones at least <code>target</code>.",
               "Therefore the cost is <code>|a[mid] - target|</code> plus <code>max(0, a[i] - target)</code> for every <code>i &lt; mid</code> plus <code>max(0, target - a[i])</code> for every <code>i &gt; mid</code>. Elements already on the correct side cost nothing.",
               "Sorting dominates: O(n log n). The answer is at most 6,000 * 2 * 10<sup>5</sup>, which fits easily in 32 bits."],
    time="O(n log n)", space="O(n)",
    solution='''def medianOperations(nums, target):
    a = sorted(nums)
    mid = len(a) // 2
    cost = abs(a[mid] - target)
    for i in range(mid):
        if a[i] > target:
            cost += a[i] - target
    for i in range(mid + 1, len(a)):
        if a[i] < target:
            cost += target - a[i]
    return cost
''',
    tests=[[[2, 5, 6, 8, 5], 4], [[1, 2, 3, 4, 5, 6], 4], [[1, 2, 3, 4, 5, 6], 7], [[5], 5], [[5], -5], [[9, 9, 9], 1],
           [[1, 1, 1], 9], [[-3, 4], 0], [[10, 20, 30, 40], 25], [[100000, -100000], -100000], [[0, 0, 0, 0, 5], 5]],
)
_r = rnd(41006)
p["tests"].append([[_r.randint(-100000, 100000) for _ in range(6000)], 12345])
p["tests"].append([[_r.randint(-100000, 100000) for _ in range(5999)], -100000])
p["tests"].append([[_r.randint(0, 10) for _ in range(6000)], 100000])


def b_medop(nums, target):
    n = len(nums)
    mid = n // 2
    best = None
    for j in range(n):
        rest = [i for i in range(n) if i != j]
        for left in combinations(rest, mid):
            ls = set(left)
            c = abs(nums[j] - target)
            for i in rest:
                if i in ls:
                    c += max(0, nums[i] - target)
                else:
                    c += max(0, target - nums[i])
            if best is None or c < best:
                best = c
    return best


def g_medop(r):
    n = r.randint(1, 7)
    return [gen_arr(r, -8, 8, n, n), r.randint(-8, 8)]


def v_medop(tests):
    for t in tests:
        nums, target = t["args"]
        assert 1 <= len(nums) <= 6000 and abs(target) <= 10 ** 5
        assert all(abs(x) <= 10 ** 5 for x in nums)


CHECKS["operations-to-make-median-equal-target"] = (b_medop, g_medop, "exact")
VALIDATE["operations-to-make-median-equal-target"] = v_medop


# ---------------------------------------------------------------- total distance per query
p = add(
    id="total-distance-to-each-query-value", title="Total Distance to Each Query Value", diff="Medium", topic=T, tier="common",
    fn="totalDistances", params=[("nums", "int[]"), ("queries", "int[]")], ret="int[]", cmp="exact",
    desc="<p>For each value <code>q</code> in <code>queries</code>, compute the total cost of turning every element of <code>nums</code> into <code>q</code>, where changing a number <code>x</code> into <code>q</code> costs <code>|x - q|</code>. Each query is independent: the array is not modified between queries.</p><p>Return an array with the total cost for every query, in query order.</p><pre>nums = [3, 1, 6], queries = [2, 5]\nq = 2: |3-2| + |1-2| + |6-2| = 1 + 1 + 4 = 6\nq = 5: 2 + 4 + 1 = 7\nanswer = [6, 7]</pre>",
    constraints=["1 &le; nums.length &le; 3,000", "1 &le; queries.length &le; 2,500", "0 &le; nums[i], queries[j] &le; 10<sup>5</sup>"],
    hints=["Answering each query with a loop over <code>nums</code> costs n per query, which is too slow when both lists are large.",
           "If <code>nums</code> is sorted, the elements below <code>q</code> and the elements above <code>q</code> form two contiguous blocks. Their sums can be read from prefix sums.",
           "Binary search the number <code>c</code> of elements that are <code>&le; q</code>. The answer is <code>q*c - prefix[c] + (total - prefix[c]) - q*(n - c)</code>."],
    editorial=["Sort <code>nums</code> and build prefix sums <code>pre</code>. For a query <code>q</code>, let <code>c = bisect_right(a, q)</code> be the number of elements not greater than <code>q</code>. Those <code>c</code> elements each pay <code>q - x</code>, totalling <code>q*c - pre[c]</code>; the other <code>n - c</code> elements each pay <code>x - q</code>, totalling <code>(pre[n] - pre[c]) - q*(n - c)</code>.",
               "Sorting once costs O(n log n), and every query then needs one binary search, for O((n + m) log n) overall instead of O(n*m). The largest possible answer is 3,000 * 10<sup>5</sup> = 3 * 10<sup>8</sup>, within 32 bits."],
    time="O((n + m) log n)", space="O(n)",
    solution='''from bisect import bisect_right


def totalDistances(nums, queries):
    a = sorted(nums)
    n = len(a)
    pre = [0] * (n + 1)
    for i, x in enumerate(a):
        pre[i + 1] = pre[i] + x
    out = []
    for q in queries:
        c = bisect_right(a, q)
        out.append(q * c - pre[c] + (pre[n] - pre[c]) - q * (n - c))
    return out
''',
    tests=[[[3, 1, 6], [2, 5]], [[5], [5]], [[5], [0]], [[1, 1, 1], [1, 0, 2]], [[0, 100000], [0, 50000, 100000]],
           [[2, 4, 6, 8], [1, 9]], [[7, 7, 7, 7], [7]], [[10, 20, 30], [10, 20, 30]], [[100000, 100000], [0]],
           [[1, 2, 3, 4, 5], [3, 3, 3]]],
)
_r = rnd(41007)
p["tests"].append([[_r.randint(0, 100000) for _ in range(3000)], [_r.randint(0, 100000) for _ in range(2500)]])
p["tests"].append([[_r.randint(0, 100) for _ in range(3000)], [_r.randint(0, 100000) for _ in range(1500)]])
p["tests"].append([[100000] * 2000, [0, 100000, 50000] * 500])


def b_totdist(nums, queries):
    return [sum(abs(x - q) for x in nums) for q in queries]


def g_totdist(r):
    return [gen_arr(r, 0, 9, 1, 8), gen_arr(r, 0, 9, 1, 6)]


def v_totdist(tests):
    for t in tests:
        nums, qs = t["args"]
        assert 1 <= len(nums) <= 3000 and 1 <= len(qs) <= 2500
        assert all(0 <= x <= 10 ** 5 for x in nums + qs)


CHECKS["total-distance-to-each-query-value"] = (b_totdist, g_totdist, "exact")
VALIDATE["total-distance-to-each-query-value"] = v_totdist


# ---------------------------------------------------------------- dynamic kth smallest
p = add(
    id="dynamic-kth-smallest-multiset", title="Kth Smallest in a Changing Multiset", diff="Medium", topic=T, tier="extra",
    fn="kthSmallestStream", params=[("ops", "int[][]")], ret="int[]", cmp="exact",
    desc="<p>You maintain a multiset of integers that starts empty. The array <code>ops</code> lists operations, each given as <code>[type, x]</code>:</p><ul><li><code>[1, x]</code>: insert the value <code>x</code> (duplicates are allowed).</li><li><code>[2, x]</code>: remove <strong>one</strong> copy of the value <code>x</code>. It is guaranteed that a copy exists.</li><li><code>[3, k]</code>: query the <code>k</code>-th smallest element of the multiset (counting duplicates, <code>k = 1</code> is the minimum). It is guaranteed that <code>1 &le; k &le; size</code>.</li></ul><p>Return the answers to the type-3 operations, in order.</p><pre>ops = [[1,5],[1,2],[1,9],[3,2],[2,2],[3,2],[1,5],[3,2]]\nset {2,5,9}      -> 2nd smallest 5\nremove 2: {5,9}  -> 2nd smallest 9\ninsert 5: {5,5,9} -> 2nd smallest 5\nanswer = [5, 9, 5]</pre>",
    constraints=["1 &le; ops.length &le; 6,000", "type is 1, 2 or 3; every operation is valid as described", "1 &le; x &le; 10<sup>6</sup> for types 1 and 2"],
    hints=["Keeping a sorted list and using binary search to find insert and delete positions is the simplest start. What does each update cost in the worst case?",
           "All inserted values are known in advance, so they can be compressed to ranks <code>1..m</code>. Then the multiset is just an array of counts over ranks.",
           "A Fenwick tree over the counts supports add and remove in O(log m), and a binary-lifting descent on the tree finds the k-th element in O(log m)."],
    editorial=["Read all operations first and compress the set of inserted values to ranks. Maintain a Fenwick (binary indexed) tree where position <code>r</code> holds how many copies of the r-th smallest value are present. Insert and removal are point updates of +1 and -1.",
               "To answer a query for the k-th smallest, descend the Fenwick tree from the highest power of two: at each step try to jump <code>step</code> positions ahead; if the count stored there is still less than <code>k</code>, take the jump and subtract that count from <code>k</code>. When no jump is possible, the next position is the rank of the answer.",
               "Every operation is O(log m), giving O(q log q) in total. Inserting into a plain Python sorted list is also accepted for small inputs (O(n) per update through memmove), but the Fenwick descent scales to millions of operations."],
    time="O(q log q)", space="O(q)",
    solution='''def kthSmallestStream(ops):
    vals = sorted({x for t, x in ops if t == 1})
    pos = {v: i + 1 for i, v in enumerate(vals)}
    m = len(vals)
    tree = [0] * (m + 1)
    top = 1
    while top * 2 <= m:
        top *= 2
    out = []
    for t, x in ops:
        if t == 3:
            k = x
            cur = 0
            step = top
            while step:
                nxt = cur + step
                if nxt <= m and tree[nxt] < k:
                    cur = nxt
                    k -= tree[nxt]
                step //= 2
            out.append(vals[cur])
        else:
            d = 1 if t == 1 else -1
            i = pos[x]
            while i <= m:
                tree[i] += d
                i += i & -i
    return out
''',
    tests=[[[[1, 5], [1, 2], [1, 9], [3, 2], [2, 2], [3, 2], [1, 5], [3, 2]]], [[[1, 7], [3, 1]]], [[[1, 4], [1, 4], [1, 4], [3, 3], [2, 4], [3, 2]]],
           [[[1, 10], [1, 20], [1, 30], [3, 1], [3, 2], [3, 3]]], [[[1, 3], [2, 3], [1, 8], [3, 1]]],
           [[[1, 1000000], [1, 1], [3, 2], [3, 1], [2, 1], [3, 1]]], [[[1, 2], [1, 1], [2, 2], [1, 2], [2, 1], [3, 1]]],
           [[[1, 5], [2, 5]]], [[[1, 6], [1, 6], [2, 6], [1, 3], [3, 1], [3, 2], [2, 6], [3, 1]]]],
)


def _mk_dyn(r, n, vmax, qprob=0.4, delprob=0.25):
    ops, cur = [], []
    for _ in range(n):
        u = r.random()
        if cur and u < qprob:
            ops.append([3, r.randint(1, len(cur))])
        elif cur and u < qprob + delprob:
            v = r.choice(cur)
            cur.remove(v)
            ops.append([2, v])
        else:
            v = r.randint(1, vmax)
            cur.append(v)
            ops.append([1, v])
    return ops


_r = rnd(41008)
p["tests"].append([_mk_dyn(_r, 3500, 10 ** 6)])
p["tests"].append([_mk_dyn(_r, 3000, 20, 0.3, 0.2)])
p["tests"].append([[[1, _r.randint(1, 10 ** 6)] for _ in range(2000)] + [[3, _r.randint(1, 2000)] for _ in range(1500)]])


def b_dyn(ops):
    cur, out = [], []
    for t, x in ops:
        if t == 1:
            bisect.insort(cur, x)
        elif t == 2:
            cur.pop(bisect.bisect_left(cur, x))
        else:
            out.append(cur[x - 1])
    return out


def g_dyn(r):
    return [_mk_dyn(r, r.randint(1, 14), 6)]


def v_dyn(tests):
    for t in tests:
        ops = t["args"][0]
        assert 1 <= len(ops) <= 6000
        cur = []
        for typ, x in ops:
            assert typ in (1, 2, 3)
            if typ == 1:
                assert 1 <= x <= 10 ** 6
                cur.append(x)
            elif typ == 2:
                assert 1 <= x <= 10 ** 6 and x in cur
                cur.remove(x)
            else:
                assert 1 <= x <= len(cur)


CHECKS["dynamic-kth-smallest-multiset"] = (b_dyn, g_dyn, "exact")
VALIDATE["dynamic-kth-smallest-multiset"] = v_dyn


# ================================================================ HARD

# ---------------------------------------------------------------- range kth smallest
p = add(
    id="range-kth-smallest-queries", title="Range K-th Smallest Queries", diff="Hard", topic=T, tier="extra",
    fn="rangeKth", params=[("nums", "int[]"), ("queries", "int[][]")], ret="int[]", cmp="exact",
    desc="<p>The array <code>nums</code> is fixed. Each query is <code>[l, r, k]</code> and asks for the <code>k</code>-th smallest value (duplicates counted, <code>k = 1</code> is the minimum) among <code>nums[l], nums[l+1], ..., nums[r]</code> (both ends inclusive, zero-based).</p><p>Return the answer of every query in order. Sorting each slice separately is too slow when there are thousands of long queries; use a structure that answers a query in about logarithmic time.</p><pre>nums = [5, 1, 4, 1, 9], queries = [[0,4,2],[1,3,3],[2,4,1]]\nslice 5 1 4 1 9 -> sorted 1 1 4 5 9 -> 2nd is 1\nslice 1 4 1     -> sorted 1 1 4     -> 3rd is 4\nslice 4 1 9     -> sorted 1 4 9     -> 1st is 1\nanswer = [1, 4, 1]</pre>",
    constraints=["1 &le; nums.length &le; 3,000", "1 &le; queries.length &le; 3,000", "-10<sup>6</sup> &le; nums[i] &le; 10<sup>6</sup>", "0 &le; l &le; r &lt; nums.length and 1 &le; k &le; r - l + 1"],
    hints=["Think about what you need from a prefix: if you knew how many elements of <code>nums[0..r]</code> fall into any value range, how could you handle <code>nums[l..r]</code>?",
           "Counts are subtractable: (count in prefix r) minus (count in prefix l-1) is the count inside the range. Compress the values to ranks and keep one counting structure per prefix.",
           "Store all prefix versions in a persistent segment tree over ranks (each insertion creates only O(log n) new nodes). A query walks down two roots at once, comparing the left child count difference to k."],
    editorial=["Compress the values to ranks <code>0..m-1</code>. Build a persistent segment tree over the rank range: version <code>i+1</code> is version <code>i</code> with rank(nums[i]) incremented, copying only the O(log m) nodes along one root-to-leaf path and sharing the rest. Each node stores how many elements are in its rank interval.",
               "For a query <code>[l, r, k]</code>, start with the roots of versions <code>r+1</code> and <code>l</code>. The number of slice elements in the left half of the current interval is <code>cnt(left of r+1) - cnt(left of l)</code>. If <code>k</code> does not exceed it, descend left in both trees; otherwise subtract it from <code>k</code> and descend right. At a leaf the rank is the answer.",
               "Building takes O(n log n) time and memory, each query O(log n). Alternatives with the same flavour are a wavelet tree/matrix, a merge-sort tree with a binary search on the answer (O(log^2 n) per query), or offline processing with a Fenwick tree and a sweep over values."],
    time="O((n + q) log n)", space="O(n log n)",
    solution='''def rangeKth(nums, queries):
    vals = sorted(set(nums))
    rank = {v: i for i, v in enumerate(vals)}
    m = len(vals)
    L, R, C = [0], [0], [0]          # node 0 is the shared empty tree
    roots = [0]
    for x in nums:
        pos = rank[x]
        prev = roots[-1]
        root = len(C)
        L.append(0); R.append(0); C.append(C[prev] + 1)
        cur, p = root, prev
        lo, hi = 0, m - 1
        while lo < hi:
            mid = (lo + hi) >> 1
            new = len(C)
            if pos <= mid:
                L[cur] = new
                R[cur] = R[p]
                C.append(C[L[p]] + 1)
                p = L[p]
                hi = mid
            else:
                R[cur] = new
                L[cur] = L[p]
                C.append(C[R[p]] + 1)
                p = R[p]
                lo = mid + 1
            L.append(0); R.append(0)
            cur = new
        roots.append(root)
    out = []
    for l, r, k in queries:
        a, b = roots[r + 1], roots[l]
        lo, hi = 0, m - 1
        while lo < hi:
            mid = (lo + hi) >> 1
            cnt = C[L[a]] - C[L[b]]
            if k <= cnt:
                a, b = L[a], L[b]
                hi = mid
            else:
                k -= cnt
                a, b = R[a], R[b]
                lo = mid + 1
        out.append(vals[lo])
    return out
''',
    tests=[[[5, 1, 4, 1, 9], [[0, 4, 2], [1, 3, 3], [2, 4, 1]]], [[7], [[0, 0, 1]]], [[2, 2, 2], [[0, 2, 3], [1, 1, 1]]],
           [[3, 1, 2], [[0, 2, 1], [0, 2, 2], [0, 2, 3], [1, 2, 2]]], [[-5, 5, -5, 5], [[0, 3, 2], [0, 3, 3], [1, 2, 1]]],
           [[1000000, -1000000, 0], [[0, 2, 1], [0, 2, 3], [0, 1, 2]]], [[4, 3, 2, 1], [[0, 3, 4], [1, 3, 2], [2, 3, 1]]],
           [[1, 2, 3, 4, 5, 6], [[0, 5, 6], [2, 4, 2], [5, 5, 1]]]],
)
_r = rnd(41009)


def _mk_rq(r, n, q, vlo, vhi):
    nums = [r.randint(vlo, vhi) for _ in range(n)]
    qs = []
    for _ in range(q):
        a, b = r.randint(0, n - 1), r.randint(0, n - 1)
        l, rr = min(a, b), max(a, b)
        qs.append([l, rr, r.randint(1, rr - l + 1)])
    return nums, qs


p["tests"].append(list(_mk_rq(_r, 3000, 2500, -10 ** 6, 10 ** 6)))
p["tests"].append(list(_mk_rq(_r, 2000, 2000, 0, 30)))
p["tests"].append(list(_mk_rq(_r, 600, 600, -10 ** 6, 10 ** 6)))


def b_rkth(nums, queries):
    return [sorted(nums[l:r + 1])[k - 1] for l, r, k in queries]


def g_rkth(r):
    n = r.randint(1, 9)
    return list(_mk_rq(r, n, r.randint(1, 6), -4, 4))


def v_rkth(tests):
    for t in tests:
        nums, qs = t["args"]
        assert 1 <= len(nums) <= 3000 and 1 <= len(qs) <= 3000
        assert all(-10 ** 6 <= x <= 10 ** 6 for x in nums)
        for l, r, k in qs:
            assert 0 <= l <= r < len(nums) and 1 <= k <= r - l + 1


CHECKS["range-kth-smallest-queries"] = (b_rkth, g_rkth, "exact")
VALIDATE["range-kth-smallest-queries"] = v_rkth


# ---------------------------------------------------------------- sliding window sum of k smallest
p = add(
    id="sliding-window-sum-of-k-smallest", title="Sliding Window Sum of the K Smallest", diff="Hard", topic=T, tier="extra",
    fn="windowKSmallestSums", params=[("nums", "int[]"), ("w", "int"), ("k", "int")], ret="int[]", cmp="exact",
    desc="<p>Consider every window of <code>w</code> consecutive elements of <code>nums</code>, from left to right. For each window, take its <code>k</code> smallest values (duplicates count separately) and add them up.</p><p>Return the array of these sums; it has <code>nums.length - w + 1</code> entries.</p><pre>nums = [4, 1, 3, 1, 5], w = 3, k = 2\n[4,1,3] -> 1 + 3 = 4\n[1,3,1] -> 1 + 1 = 2\n[3,1,5] -> 1 + 3 = 4\nanswer = [4, 2, 4]</pre>",
    constraints=["1 &le; k &le; w &le; nums.length &le; 6,000", "-10<sup>5</sup> &le; nums[i] &le; 10<sup>5</sup>"],
    hints=["Sorting every window costs about w log w per position, which is too slow for big windows. How does the set of values change when the window moves by one?",
           "Exactly one element leaves and one enters. If you could keep the window's elements in an order-aware structure, you would need prefix counts and prefix sums by rank.",
           "Give every element a unique rank (sort by value, ties by index). Keep a Fenwick tree of counts and a second one of sums over ranks, then descend the count tree to find the prefix that contains exactly k elements and read its sum."],
    editorial=["Assign each index a unique rank in the global order (value first, index as tie-break), so ranks never collide even for equal values. Two Fenwick trees indexed by rank store, respectively, how many window elements sit at each rank (0 or 1) and the sum of their values.",
               "Sliding the window means one removal and one insertion, each O(log n). To read the sum of the k smallest, descend the count tree with binary lifting: jump forward while the accumulated count stays at most k, adding the sum tree's values along the way. The jumps stop at the last rank whose prefix holds exactly k elements, and the accumulated sum is the answer for that window.",
               "Total time is O(n log n) and memory O(n). Alternatives are two heaps with lazy deletion (one holds the k smallest, the other the rest) and an order-statistic tree; the Fenwick approach avoids lazy deletion bookkeeping. Sums reach at most 6,000 * 10<sup>5</sup> = 6 * 10<sup>8</sup>, within 32 bits."],
    time="O(n log n)", space="O(n)",
    solution='''def windowKSmallestSums(nums, w, k):
    n = len(nums)
    order = sorted(range(n), key=lambda i: (nums[i], i))
    rank = [0] * n
    for j, i in enumerate(order):
        rank[i] = j + 1
    cnt = [0] * (n + 1)
    sm = [0] * (n + 1)
    top = 1
    while top * 2 <= n:
        top *= 2

    def update(i, dc, dv):
        while i <= n:
            cnt[i] += dc
            sm[i] += dv
            i += i & -i

    out = []
    for i in range(n):
        update(rank[i], 1, nums[i])
        if i >= w:
            update(rank[i - w], -1, -nums[i - w])
        if i >= w - 1:
            pos, rem, total, step = 0, k, 0, top
            while step:
                nxt = pos + step
                if nxt <= n and cnt[nxt] <= rem:
                    pos = nxt
                    rem -= cnt[nxt]
                    total += sm[nxt]
                step >>= 1
            out.append(total)
    return out
''',
    tests=[[[4, 1, 3, 1, 5], 3, 2], [[7], 1, 1], [[5, 5, 5, 5], 2, 1], [[5, 5, 5, 5], 4, 4], [[1, 2, 3, 4, 5], 3, 3],
           [[5, 4, 3, 2, 1], 2, 1], [[-3, 8, -3, 8, -3], 3, 2], [[100000, -100000, 100000, -100000], 2, 1],
           [[9, 8, 7, 6, 5, 4, 3, 2, 1], 4, 2], [[0, 0, 0], 3, 2]],
)
_r = rnd(41010)
p["tests"].append([[_r.randint(-100000, 100000) for _ in range(4000)], 500, 120])
p["tests"].append([[_r.randint(-5, 5) for _ in range(3500)], 1500, 1000])
p["tests"].append([[_r.randint(-100000, 100000) for _ in range(2000)], 3, 1])


def b_wks(nums, w, k):
    return [sum(sorted(nums[i:i + w])[:k]) for i in range(len(nums) - w + 1)]


def g_wks(r):
    n = r.randint(1, 10)
    w = r.randint(1, n)
    return [gen_arr(r, -4, 4, n, n), w, r.randint(1, w)]


def v_wks(tests):
    for t in tests:
        nums, w, k = t["args"]
        assert 1 <= k <= w <= len(nums) <= 6000
        assert all(-10 ** 5 <= x <= 10 ** 5 for x in nums)


CHECKS["sliding-window-sum-of-k-smallest"] = (b_wks, g_wks, "exact")
VALIDATE["sliding-window-sum-of-k-smallest"] = v_wks


# ---------------------------------------------------------------- max subarray median, min length
p = add(
    id="max-subarray-median-min-length", title="Largest Median of a Long Enough Subarray", diff="Hard", topic=T, tier="extra",
    fn="maxSubarrayMedian", params=[("nums", "int[]"), ("k", "int")], ret="int", cmp="exact",
    desc="<p>Consider every contiguous subarray of <code>nums</code> whose length is <strong>at least</strong> <code>k</code>. The <em>median</em> of a subarray of length <code>len</code> is the element at zero-based position <code>len // 2</code> of its sorted copy (the larger middle value for an even length).</p><p>Return the largest median over all these subarrays.</p><pre>nums = [3, 1, 4, 1, 5], k = 3\n[3,1,4] -> 3     [1,4,1] -> 1     [4,1,5] -> 4\n[3,1,4,1] -> 3   [1,4,1,5] -> 4   [3,1,4,1,5] -> 3\nanswer = 4</pre>",
    constraints=["1 &le; k &le; nums.length &le; 6,000", "-10<sup>6</sup> &le; nums[i] &le; 10<sup>6</sup>"],
    hints=["Checking every subarray and sorting it is far too slow. Is the statement 'some valid subarray has median at least m' monotone in m?",
           "For a fixed m, map each element to +1 if it is at least m and to -1 otherwise. The median of a subarray is at least m exactly when the mapped sum is non-negative.",
           "Binary search the answer over the sorted values. For each candidate use prefix sums: for the end position j, you need some start i with j - i &ge; k and prefix[j] - prefix[i] &ge; 0, so keep the minimum prefix among allowed starts."],
    editorial=["For a threshold <code>m</code>, let <code>c</code> be the number of subarray elements that are at least <code>m</code> and <code>d</code> the number below. The median (sorted position <code>len // 2</code>) is at least <code>m</code> exactly when at most <code>len // 2</code> elements are below <code>m</code>, i.e. <code>d &le; len // 2</code>, which is equivalent to <code>c &ge; d</code>, i.e. the +1/-1 sum is non-negative.",
               "If a subarray works for <code>m</code>, it also works for every smaller value, so feasibility is monotone and the largest feasible <code>m</code> can be found by binary search over the sorted distinct array values (the answer is always one of them).",
               "Each feasibility check is one pass: with prefix sums <code>P</code>, for each end <code>j &ge; k</code> maintain <code>best = min(P[0..j-k])</code> and test <code>P[j] - best &ge; 0</code>. Total time is O(n log n) for sorting plus O(n log n) for the binary search."],
    time="O(n log n)", space="O(n)",
    solution='''def maxSubarrayMedian(nums, k):
    n = len(nums)
    vals = sorted(set(nums))

    def ok(m):
        pre = [0] * (n + 1)
        for i, x in enumerate(nums):
            pre[i + 1] = pre[i] + (1 if x >= m else -1)
        best = 10 ** 9
        for j in range(k, n + 1):
            best = min(best, pre[j - k])
            if pre[j] - best >= 0:
                return True
        return False

    lo, hi = 0, len(vals) - 1
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if ok(vals[mid]):
            lo = mid
        else:
            hi = mid - 1
    return vals[lo]
''',
    tests=[[[3, 1, 4, 1, 5], 3], [[3, 1, 4, 1, 5], 1], [[3, 1, 4, 1, 5], 5], [[7], 1], [[1, 2], 2], [[2, 1], 1], [[2, 1], 2],
           [[5, 5, 5, 5], 3], [[-3, -1, -2], 2], [[1, 9, 1, 9, 1, 9, 1], 4], [[10, 1, 1, 1, 1, 1, 10], 6]],
)
_r = rnd(41011)
p["tests"].append([[_r.randint(-10 ** 6, 10 ** 6) for _ in range(6000)], 700])
p["tests"].append([[_r.randint(-5, 5) for _ in range(6000)], 3000])
p["tests"].append([[_r.randint(-10 ** 6, 10 ** 6) for _ in range(5000)], 5000])


def b_msm(nums, k):
    n = len(nums)
    best = None
    for i in range(n):
        for j in range(i + k, n + 1):
            s = sorted(nums[i:j])
            med = s[len(s) // 2]
            if best is None or med > best:
                best = med
    return best


def g_msm(r):
    n = r.randint(1, 9)
    return [gen_arr(r, -5, 5, n, n), r.randint(1, n)]


def v_msm(tests):
    for t in tests:
        nums, k = t["args"]
        assert 1 <= k <= len(nums) <= 6000
        assert all(-10 ** 6 <= x <= 10 ** 6 for x in nums)


CHECKS["max-subarray-median-min-length"] = (b_msm, g_msm, "exact")
VALIDATE["max-subarray-median-min-length"] = v_msm
