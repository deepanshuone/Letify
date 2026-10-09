"""Problems: binary search (second batch). See data/lib.py for the registry."""
import heapq
from itertools import combinations

from lib import add, rnd, CHECKS, VALIDATE, gen_arr  # noqa: F401

INT_MIN, INT_MAX = -(2 ** 31), 2 ** 31 - 1


def _mono_grid(r, m, n, lo, hi, descending):
    """Random m x n grid whose rows and columns are all sorted (sorting the columns keeps the rows sorted)."""
    g = [[r.randint(lo, hi) for _ in range(n)] for _ in range(m)]
    for row in g:
        row.sort(reverse=descending)
    for j in range(n):
        col = sorted((g[i][j] for i in range(m)), reverse=descending)
        for i in range(m):
            g[i][j] = col[i]
    return g


# ---------------------------------------------------------------- EASY

p = add(
    id="count-negatives-in-sorted-grid", title="Count Negatives in a Sorted Grid", diff="Easy", topic="Binary Search",
    fn="countNegatives", params=[("grid", "int[][]")], ret="int", cmp="exact",
    desc="<p>In the <code>m x n</code> integer matrix <code>grid</code>, every row is sorted in non-increasing order from left to right, and every column is sorted in non-increasing order from top to bottom.</p><p>Return how many cells of <code>grid</code> hold a negative number. A solution that visits far fewer than <code>m * n</code> cells exists.</p>",
    constraints=["1 &le; m, n &le; 120", "-10<sup>9</sup> &le; grid[i][j] &le; 10<sup>9</sup>", "Each row and each column is in non-increasing order"],
    hints=["Counting cell by cell works in O(m * n). Can the ordering let you skip many cells at once?",
           "In one row, the negative numbers form a suffix. Binary searching each row for the first negative gives O(m log n).",
           "Because columns are sorted too, the boundary between non-negatives and negatives only moves left as you go down. Walk it from the top-right corner and you only need O(m + n) steps."],
    editorial=["Inside one row the values are non-increasing, so the negatives are exactly a suffix. A binary search for the first negative value counts a whole row in O(log n), for O(m log n) overall.",
               "The columns are sorted as well, so the index of the first negative cell never moves right when you go to the next row down. Start at the top-right corner. While the current cell is negative, the whole column below it is negative too, so add the remaining rows and step left; otherwise step down. Each step either leaves a column or a row, so at most m + n steps are made: O(m + n) time and O(1) space."],
    time="O(m + n)", space="O(1)",
    solution='''def countNegatives(grid):
    m, n = len(grid), len(grid[0])
    row, col = 0, n - 1
    total = 0
    while row < m and col >= 0:
        if grid[row][col] < 0:
            total += m - row
            col -= 1
        else:
            row += 1
    return total
''',
    tests=[[[[4, 3, 2, -1], [3, 2, 1, -1], [1, 1, -1, -2], [-1, -1, -2, -3]]], [[[3, 2], [1, 0]]], [[[-1]]], [[[0]]],
           [[[5, 1, 0, -4, -7]]], [[[5], [0], [-3], [-3], [-9]]], [[[-1, -1], [-1, -1]]], [[[0, 0, 0], [0, 0, 0]]],
           [[[10 ** 9, 0], [0, -10 ** 9]]], [[[2, 1, -1], [1, -1, -1], [-1, -1, -1]]]],
)
_r = rnd(7101)
p["tests"].append([_mono_grid(_r, 120, 120, -10 ** 9, 10 ** 9, True)])
p["tests"].append([_mono_grid(_r, 120, 120, -50, 50, True)])
p["tests"].append([_mono_grid(_r, 1, 120, -9, 9, True)])
p["tests"].append([_mono_grid(_r, 120, 1, -9, 9, True)])
p["tests"].append([[[-7] * 120 for _ in range(120)]])
p["tests"].append([[[3] * 120 for _ in range(120)]])
p["tests"].append([_mono_grid(_r, 90, 120, -3, 40, True)])


def b_negs(grid):
    c = 0
    for row in grid:
        for x in row:
            if x < 0:
                c += 1
    return c


def g_negs(r):
    return [_mono_grid(r, r.randint(1, 6), r.randint(1, 6), -5, 5, True)]


def v_negs(tests):
    for t in tests:
        g = t["args"][0]
        m, n = len(g), len(g[0])
        assert 1 <= m <= 120 and 1 <= n <= 120
        assert all(len(row) == n for row in g)
        assert all(-10 ** 9 <= x <= 10 ** 9 for row in g for x in row)
        for i in range(m):
            for j in range(n):
                if j + 1 < n:
                    assert g[i][j] >= g[i][j + 1], "row order"
                if i + 1 < m:
                    assert g[i][j] >= g[i + 1][j], "column order"


CHECKS["count-negatives-in-sorted-grid"] = (b_negs, g_negs, "exact")
VALIDATE["count-negatives-in-sorted-grid"] = v_negs

p = add(
    id="complete-staircase-rows", title="Complete Staircase Rows", diff="Easy", topic="Binary Search",
    fn="stairRows", params=[("n", "int")], ret="int", cmp="exact",
    desc="<p>You have <code>n</code> coins and want to lay them out as a staircase. Row <code>1</code> takes one coin, row <code>2</code> takes two coins, row <code>3</code> takes three, and so on; row <code>k</code> takes <code>k</code> coins. A row is only counted if it is filled completely.</p><p>Return the number of complete rows you can build with the <code>n</code> coins.</p>",
    constraints=["0 &le; n &le; 2<sup>31</sup> - 1"],
    hints=["Building <em>k</em> complete rows costs exactly <code>1 + 2 + ... + k</code> coins. Do you know a closed form for that sum?",
           "The cost <code>k(k+1)/2</code> grows with <code>k</code>, so the question &quot;can I afford <code>k</code> rows?&quot; is true for small <code>k</code> and false for large <code>k</code>.",
           "Binary search the largest <code>k</code> with <code>k(k+1)/2 &le; n</code>. The answer is below 65,536 for every allowed <code>n</code>, so use <code>hi = 65,536</code>; take care that intermediate products do not overflow 32 bits."],
    editorial=["Subtracting 1, 2, 3, ... from <code>n</code> until the next row no longer fits is correct but needs about &radic;(2n) steps, around 65,000 for the largest input. That is fine here, but binary search makes it logarithmic and generalizes to much larger limits.",
               "Row counts are monotone: if <code>k</code> rows are affordable then so are <code>k - 1</code>. Search the largest <code>k</code> in <code>[0, 65535]</code> such that <code>k(k+1)/2 &le; n</code>. Since <code>k(k+1)</code> can reach about 4.3 billion, do the arithmetic in a 64-bit type (or compare <code>k(k+1)/2</code> carefully) in languages with 32-bit integers. The closed form <code>floor((sqrt(8n + 1) - 1) / 2)</code> also works but needs a careful integer square root."],
    time="O(log n)", space="O(1)",
    solution='''def stairRows(n):
    lo, hi = 0, 65535
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if mid * (mid + 1) // 2 <= n:
            lo = mid
        else:
            hi = mid - 1
    return lo
''',
    tests=[[5], [8], [0], [1], [2], [3], [6], [10], [15], [14], [100], [INT_MAX], [2147450880], [2147450879], [1000000000], [2 ** 30]],
)


def b_stairs(n):
    rows = 0
    while n >= rows + 1:
        rows += 1
        n -= rows
    return rows


def g_stairs(r):
    return [r.randint(0, 120)]


def v_stairs(tests):
    for t in tests:
        n = t["args"][0]
        assert 0 <= n <= INT_MAX
        k = t["expected"]
        assert k * (k + 1) // 2 <= n < (k + 1) * (k + 2) // 2


CHECKS["complete-staircase-rows"] = (b_stairs, g_stairs, "exact")
VALIDATE["complete-staircase-rows"] = v_stairs


# ---------------------------------------------------------------- MEDIUM

p = add(
    id="search-flattened-sorted-grid", title="Search a Flattened Sorted Grid", diff="Medium", topic="Binary Search",
    fn="gridContains", params=[("grid", "int[][]"), ("target", "int")], ret="bool", cmp="exact",
    desc="<p>The <code>m x n</code> matrix <code>grid</code> has two properties: every row is sorted in strictly increasing order, and the first number of each row is larger than the last number of the previous row.</p><p>Return <code>true</code> if <code>target</code> appears anywhere in <code>grid</code>, otherwise <code>false</code>. Your solution should run in O(log(m * n)) time.</p>",
    constraints=["1 &le; m, n &le; 100", "-2<sup>31</sup> &le; grid[i][j], target &le; 2<sup>31</sup> - 1", "Reading the rows one after another yields a strictly increasing sequence"],
    hints=["A scan of all cells works but ignores the ordering. What does the ordering say about the whole grid?",
           "If you wrote the rows one after another into a single list, that list would be sorted. You do not need to build it.",
           "Binary search over indices <code>0 .. m*n - 1</code>. Index <code>i</code> corresponds to the cell in row <code>i // n</code> and column <code>i % n</code>."],
    editorial=["Because each row begins above where the previous one ended, the grid read in row-major order is one long strictly increasing array of <code>m * n</code> numbers. That is a standard sorted-array membership question.",
               "Run a binary search on the virtual index range <code>[0, m*n)</code>. For a middle index <code>mid</code> read <code>grid[mid // n][mid % n]</code> and compare it with the target, discarding the half that cannot contain it. This needs O(log(m * n)) time and O(1) space. A two-stage search (first find the row, then search inside it) has the same complexity."],
    time="O(log(m*n))", space="O(1)",
    solution='''def gridContains(grid, target):
    m, n = len(grid), len(grid[0])
    lo, hi = 0, m * n - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        v = grid[mid // n][mid % n]
        if v == target:
            return True
        if v < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return False
''',
    tests=[[[[1, 3, 5, 7], [10, 11, 16, 20], [23, 30, 34, 60]], 3], [[[1, 3, 5, 7], [10, 11, 16, 20], [23, 30, 34, 60]], 13],
           [[[5]], 5], [[[5]], 6], [[[5]], -2], [[[1, 2, 3, 4, 5]], 5], [[[1, 2, 3, 4, 5]], 0], [[[1], [3], [5], [7]], 7],
           [[[1], [3], [5], [7]], 4], [[[-9, -4], [0, 2]], -9], [[[-9, -4], [0, 2]], 2], [[[-9, -4], [0, 2]], -1],
           [[[INT_MIN, 0], [1, INT_MAX]], INT_MAX], [[[INT_MIN, 0], [1, INT_MAX]], INT_MIN + 1]],
)
_r = rnd(7102)
_vals = sorted(_r.sample(range(INT_MIN, INT_MAX), 10000))
_g = [_vals[i * 100:(i + 1) * 100] for i in range(100)]
p["tests"].append([_g, _vals[1234]])
p["tests"].append([_g, _vals[0]])
p["tests"].append([_g, _vals[-1]])
p["tests"].append([_g, _vals[5000] + 1 if _vals[5000] + 1 not in _vals else _vals[5000] - 1])
p["tests"].append([_g, INT_MAX])
_g = [_vals[i * 25:(i + 1) * 25] for i in range(400)][:100]
p["tests"].append([_g, _g[63][9]])


def b_flat(grid, target):
    for row in grid:
        for x in row:
            if x == target:
                return True
    return False


def g_flat(r):
    m, n = r.randint(1, 5), r.randint(1, 5)
    vals = sorted(r.sample(range(-15, 40), m * n))
    g = [vals[i * n:(i + 1) * n] for i in range(m)]
    return [g, r.randint(-16, 41)]


def v_flat(tests):
    for t in tests:
        g, target = t["args"]
        m, n = len(g), len(g[0])
        assert 1 <= m <= 100 and 1 <= n <= 100
        assert all(len(row) == n for row in g)
        flat = [x for row in g for x in row]
        assert all(flat[i] < flat[i + 1] for i in range(len(flat) - 1)), "not strictly increasing"
        assert all(INT_MIN <= x <= INT_MAX for x in flat + [target])


CHECKS["search-flattened-sorted-grid"] = (b_flat, g_flat, "exact")
VALIDATE["search-flattened-sorted-grid"] = v_flat

p = add(
    id="rotated-array-contains-with-duplicates", title="Search a Rotated Array with Duplicates", diff="Medium", topic="Binary Search",
    fn="rotatedContains", params=[("nums", "int[]"), ("target", "int")], ret="bool", cmp="exact",
    desc="<p>A non-decreasing array (it may contain repeated values) was rotated to the left by an unknown number of positions. For example, <code>[0, 0, 1, 2, 2, 5, 6]</code> rotated by 4 becomes <code>[2, 5, 6, 0, 0, 1, 2]</code>. The rotation amount can also be 0.</p><p>Given the rotated array <code>nums</code> and an integer <code>target</code>, return <code>true</code> if <code>target</code> occurs in <code>nums</code>, otherwise <code>false</code>. Make the search as fast as you can; with duplicates the worst case cannot be better than linear, but typical inputs should take O(log n).</p>",
    constraints=["1 &le; nums.length &le; 10,000", "-2<sup>31</sup> &le; nums[i], target &le; 2<sup>31</sup> - 1", "nums is a non-decreasing array rotated by some amount"],
    hints=["Without duplicates you could always tell which half of the middle is sorted. Where exactly do duplicates break that?",
           "If <code>nums[lo] &lt; nums[mid]</code> the left half is sorted; if <code>nums[lo] &gt; nums[mid]</code> the right half is. Only equality leaves things ambiguous.",
           "When <code>nums[lo] == nums[mid] == nums[hi]</code> you cannot tell which side is sorted. Drop one element from each end (the middle already failed to match) and continue; otherwise decide which half is sorted, test if the target lies inside it, and narrow the range."],
    editorial=["After a rotation, at least one of the two halves around <code>mid</code> is always sorted. Compare <code>nums[lo]</code> with <code>nums[mid]</code> to find it: if the left half is sorted and <code>nums[lo] &le; target &lt; nums[mid]</code>, keep the left half; otherwise keep the right. The mirror reasoning applies when the right half is sorted.",
               "Duplicates create one ambiguous case: <code>nums[lo] == nums[mid] == nums[hi]</code>, for instance <code>[1, 1, 1, 3, 1]</code> versus <code>[1, 3, 1, 1, 1]</code>. Here neither half can be ruled out, so shrink the range by one from both ends (the values being equal to <code>nums[mid]</code>, which was not the target, makes this safe). That step is what makes the worst case O(n), e.g. an array of all ones with a single different value, but typical inputs still run in O(log n). Space is O(1)."],
    time="O(log n) typical, O(n) worst", space="O(1)",
    solution='''def rotatedContains(nums, target):
    lo, hi = 0, len(nums) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if nums[mid] == target:
            return True
        if nums[lo] == nums[mid] == nums[hi]:
            lo += 1
            hi -= 1
        elif nums[lo] <= nums[mid]:
            if nums[lo] <= target < nums[mid]:
                hi = mid - 1
            else:
                lo = mid + 1
        else:
            if nums[mid] < target <= nums[hi]:
                lo = mid + 1
            else:
                hi = mid - 1
    return False
''',
    tests=[[[2, 5, 6, 0, 0, 1, 2], 0], [[2, 5, 6, 0, 0, 1, 2], 3], [[1, 0, 1, 1, 1], 0], [[1, 1, 1, 1, 1, 1, 1, 1, 1, 13, 1, 1, 1, 1], 13],
           [[1, 3, 1, 1, 1], 3], [[1, 1, 3, 1], 3], [[1], 1], [[1], 2], [[3, 1], 1], [[3, 1], 2], [[2, 2, 2, 3, 2, 2, 2], 3],
           [[4, 5, 6, 7, 0, 1, 2], 0], [[4, 5, 6, 7, 0, 1, 2], 3], [[INT_MAX, INT_MIN, INT_MIN, 0], INT_MIN], [[7, 7, 7, 7], 8]],
)
_r = rnd(7103)
p["tests"].append([[1] * 5000 + [2] + [1] * 4999, 2])
p["tests"].append([[1] * 5000 + [2] + [1] * 4999, 3])
p["tests"].append([[1] * 9999 + [0], 0])
_s = sorted(_r.randint(-10 ** 9, 10 ** 9) for _ in range(10000))
_k = 3777
p["tests"].append([_s[_k:] + _s[:_k], _s[9000]])
p["tests"].append([_s[_k:] + _s[:_k], _s[9000] + 1])
_s = sorted(_r.randint(0, 50) for _ in range(10000))
_k = 6000
p["tests"].append([_s[_k:] + _s[:_k], 25])
p["tests"].append([_s[_k:] + _s[:_k], 51])


def b_rot(nums, target):
    for x in nums:
        if x == target:
            return True
    return False


def g_rot(r):
    n = r.randint(1, 10)
    a = sorted(r.randint(-4, 4) for _ in range(n))
    k = r.randint(0, n - 1)
    return [a[k:] + a[:k], r.randint(-5, 5)]


def v_rot(tests):
    for t in tests:
        nums, target = t["args"]
        assert 1 <= len(nums) <= 10000
        assert all(INT_MIN <= x <= INT_MAX for x in nums + [target])
        n = len(nums)
        drops = sum(1 for i in range(n) if nums[i] > nums[(i + 1) % n])
        assert drops <= 1, "not a rotation of a non-decreasing array"


CHECKS["rotated-array-contains-with-duplicates"] = (b_rot, g_rot, "exact")
VALIDATE["rotated-array-contains-with-duplicates"] = v_rot

p = add(
    id="lone-value-in-sorted-pairs", title="Lone Value in Sorted Pairs", diff="Medium", topic="Binary Search",
    fn="loneValue", params=[("nums", "int[]")], ret="int", cmp="exact",
    desc="<p>The array <code>nums</code> is sorted in non-decreasing order. Every value in it appears exactly twice, except for one value that appears exactly once. Because equal values are adjacent, the equal pairs sit side by side.</p><p>Return the value that appears only once. Your solution must run in O(log n) time and use O(1) extra space.</p>",
    constraints=["1 &le; nums.length &le; 9,999 and nums.length is odd", "-2<sup>31</sup> &le; nums[i] &le; 2<sup>31</sup> - 1", "nums is sorted; exactly one value appears once and every other value appears twice"],
    hints=["XOR-ing every element finds the answer in O(n). How could you throw away half of the array in O(1) instead?",
           "Look at the pairs to the left of the lone value: the first copy sits at an even index and the second at an odd index. After the lone value, that alignment flips.",
           "For a middle index, move it to the even index of its position (if it is odd, subtract one). If <code>nums[mid] == nums[mid + 1]</code> the left side is still aligned, so the lone value is to the right; otherwise it is at <code>mid</code> or to the left."],
    editorial=["Before the lone element every pair starts on an even index, i.e. <code>nums[2i] == nums[2i + 1]</code>. After the lone element every pair starts on an odd index. The array length is odd, so the lone value always sits at an even index.",
               "Binary search over even indices. Take <code>mid</code> and, if it is odd, decrease it by one so it points at the supposed first copy of a pair. If <code>nums[mid] == nums[mid + 1]</code> the pairs are still aligned up to <code>mid + 1</code>, so the answer lies at <code>mid + 2</code> or later; set <code>lo = mid + 2</code>. Otherwise the alignment broke at or before <code>mid</code>, so set <code>hi = mid</code>. When <code>lo == hi</code> the lone value is found. Time O(log n), space O(1)."],
    time="O(log n)", space="O(1)",
    solution='''def loneValue(nums):
    lo, hi = 0, len(nums) - 1
    while lo < hi:
        mid = (lo + hi) // 2
        if mid % 2 == 1:
            mid -= 1
        if nums[mid] == nums[mid + 1]:
            lo = mid + 2
        else:
            hi = mid
    return nums[lo]
''',
    tests=[[[1, 1, 2, 3, 3, 4, 4, 8, 8]], [[3, 3, 7, 7, 10, 11, 11]], [[5]], [[1, 2, 2]], [[1, 1, 2]], [[-3, -3, 0, 4, 4]],
           [[INT_MIN, INT_MIN, 0, INT_MAX, INT_MAX]], [[INT_MIN, 7, 7]], [[-8, -8, 3, 3, 9]], [[0, 1, 1, 2, 2, 3, 3]],
           [[1, 1, 2, 2, 3, 3, 4]]],
)
_r = rnd(7104)


def _lone_case(r, pairs, pos, lo=-10 ** 9, hi=10 ** 9):
    vals = sorted(r.sample(range(lo, hi), pairs + 1))
    out = []
    for i, v in enumerate(vals):
        out += [v] if i == pos else [v, v]
    return out


for _pos in (0, 4999, 2500, 1234, 3333):
    p["tests"].append([_lone_case(_r, 4999, _pos)])
p["tests"].append([_lone_case(_r, 4999, 4999, INT_MIN, INT_MAX)])
p["tests"].append([_lone_case(_r, 4999, 0, INT_MIN, INT_MAX)])


def b_lone(nums):
    for x in nums:
        if nums.count(x) == 1:
            return x


def g_lone(r):
    pairs = r.randint(0, 6)
    return [_lone_case(r, pairs, r.randint(0, pairs), -30, 30)]


def v_lone(tests):
    for t in tests:
        nums = t["args"][0]
        assert len(nums) % 2 == 1 and 1 <= len(nums) <= 9999
        assert nums == sorted(nums)
        assert all(INT_MIN <= x <= INT_MAX for x in nums)
        counts = {}
        for x in nums:
            counts[x] = counts.get(x, 0) + 1
        assert sorted(counts.values()).count(1) == 1 and all(c in (1, 2) for c in counts.values())


CHECKS["lone-value-in-sorted-pairs"] = (b_lone, g_lone, "exact")
VALIDATE["lone-value-in-sorted-pairs"] = v_lone

p = add(
    id="earliest-day-for-bouquets", title="Earliest Day for Bouquets", diff="Medium", topic="Binary Search",
    fn="earliestDay", params=[("bloomDay", "int[]"), ("m", "int"), ("k", "int")], ret="int", cmp="exact",
    desc="<p>A garden has a row of flowers; flower <code>i</code> blooms on day <code>bloomDay[i]</code> and stays bloomed afterwards. A bouquet needs <code>k</code> <em>adjacent</em> bloomed flowers, and each flower can be used in at most one bouquet.</p><p>Return the smallest day number by which you can have made <code>m</code> bouquets. If it is impossible, return <code>-1</code>.</p>",
    constraints=["1 &le; bloomDay.length &le; 10,000", "1 &le; bloomDay[i] &le; 10<sup>9</sup>", "1 &le; m &le; 10<sup>6</sup>", "1 &le; k &le; bloomDay.length"],
    hints=["First rule out the impossible case: you need at least <code>m * k</code> flowers in total.",
           "Fix a day <code>d</code>. Which flowers are bloomed? How many bouquets can you greedily make from runs of bloomed flowers?",
           "If you can make <code>m</code> bouquets on day <code>d</code>, you can on every later day too. Binary search the day between the smallest and largest bloom day, counting bouquets with one left-to-right scan: extend a run for each bloomed flower, cash it in as one bouquet every time it reaches length <code>k</code>, and reset it on an unbloomed flower."],
    editorial=["If <code>m * k</code> exceeds the number of flowers the answer is <code>-1</code>. Otherwise all flowers have bloomed on day <code>max(bloomDay)</code>, so an answer exists.",
               "For a fixed day <code>d</code>, scan the row: a bloomed flower extends the current run, and each time the run reaches <code>k</code> one bouquet is made and the run restarts; an unbloomed flower resets the run. This greedy count is the maximum number of bouquets for that day. The count never decreases as <code>d</code> increases, so binary search the smallest day with count &ge; <code>m</code>. With about 30 iterations of an O(n) scan the total is O(n log(max bloom day)) time and O(1) space."],
    time="O(n log D)", space="O(1)",
    solution='''def earliestDay(bloomDay, m, k):
    n = len(bloomDay)
    if m * k > n:
        return -1

    def bouquets(day):
        made = run = 0
        for b in bloomDay:
            if b <= day:
                run += 1
                if run == k:
                    made += 1
                    run = 0
            else:
                run = 0
        return made

    lo, hi = min(bloomDay), max(bloomDay)
    while lo < hi:
        mid = (lo + hi) // 2
        if bouquets(mid) >= m:
            hi = mid
        else:
            lo = mid + 1
    return lo
''',
    tests=[[[1, 10, 3, 10, 2], 3, 1], [[1, 10, 3, 10, 2], 3, 2], [[7, 7, 7, 7, 12, 7, 7], 2, 3], [[1, 2, 4, 9, 3, 4, 1], 2, 2],
           [[5], 1, 1], [[5], 2, 1], [[4, 2], 1, 2], [[3, 3, 3, 3], 1, 4], [[10, 1, 10, 1, 10], 2, 1], [[10, 1, 10, 1, 10], 1, 2],
           [[10 ** 9, 1, 10 ** 9], 1, 1], [[10 ** 9] * 6, 3, 2], [[1, 2, 3, 4, 5, 6], 2, 3], [[6, 5, 4, 3, 2, 1], 1, 6]],
)
_r = rnd(7105)
_bd = [_r.randint(1, 10 ** 9) for _ in range(10000)]
p["tests"].append([_bd, 100, 50])
p["tests"].append([_bd, 1, 10000])
p["tests"].append([_bd, 2500, 4])
p["tests"].append([_bd, 10 ** 6, 1])
p["tests"].append([_bd, 5000, 2])
_bd = [_r.randint(1, 100) for _ in range(10000)]
p["tests"].append([_bd, 300, 20])
p["tests"].append([_bd, 3000, 3])
p["tests"].append([[10 ** 9] * 10000, 10, 1000])


def b_bouq(bloomDay, m, k):
    n = len(bloomDay)
    for day in sorted(set(bloomDay)):
        flags = [b <= day for b in bloomDay]
        made = 0
        i = 0
        while i + k <= n:
            if all(flags[i:i + k]):
                made += 1
                i += k
            else:
                i += 1
        if made >= m:
            return day
    return -1


def g_bouq(r):
    n = r.randint(1, 10)
    k = r.randint(1, min(n, 4))
    m = r.randint(1, max(1, n // k + 1))
    return [[r.randint(1, 12) for _ in range(n)], m, k]


def v_bouq(tests):
    for t in tests:
        bd, m, k = t["args"]
        assert 1 <= len(bd) <= 10000 and all(1 <= x <= 10 ** 9 for x in bd)
        assert 1 <= m <= 10 ** 6 and 1 <= k <= len(bd)


CHECKS["earliest-day-for-bouquets"] = (b_bouq, g_bouq, "exact")
VALIDATE["earliest-day-for-bouquets"] = v_bouq

p = add(
    id="maximize-min-gap-between-balls", title="Maximize the Minimum Gap Between Balls", diff="Medium", topic="Binary Search",
    fn="maxMinGap", params=[("positions", "int[]"), ("m", "int")], ret="int", cmp="exact",
    desc="<p>There are baskets at the distinct integer coordinates in <code>positions</code> (in no particular order), each of which holds at most one ball. You must place exactly <code>m</code> balls into different baskets.</p><p>The <em>gap</em> of a placement is the smallest distance between any two of the chosen baskets. Return the largest gap that any placement can achieve.</p>",
    constraints=["2 &le; m &le; positions.length &le; 10,000", "1 &le; positions[i] &le; 10<sup>9</sup>", "All positions are distinct"],
    hints=["Trying every set of <code>m</code> baskets is hopeless for large inputs. Start by sorting the positions.",
           "Turn the question around: given a required gap <code>d</code>, can you fit <code>m</code> balls so that neighbours are at least <code>d</code> apart? A greedy left-to-right placement answers that.",
           "If gap <code>d</code> is achievable, so is any smaller gap. Binary search <code>d</code> from 1 to <code>(max - min) // (m - 1)</code>, using the greedy check (take the leftmost basket, then the next basket at least <code>d</code> away, and so on)."],
    editorial=["Sort the positions. For a target gap <code>d</code>, place the first ball at the leftmost basket and keep placing each next ball in the nearest basket that is at least <code>d</code> beyond the previously placed one. This greedy choice leaves the most room for later balls, so it places the maximum number of balls for that <code>d</code>; the gap is feasible exactly when this number is at least <code>m</code>.",
               "Feasibility is monotone in <code>d</code>, so binary search for the largest feasible value. The gap can never exceed <code>(max - min) // (m - 1)</code> and is at least 1 because positions are distinct. The cost is O(n log n) for sorting plus O(n log(max - min)) for the search."],
    time="O(n log n + n log R)", space="O(1) extra",
    solution='''def maxMinGap(positions, m):
    pos = sorted(positions)

    def can(d):
        placed, last = 1, pos[0]
        for x in pos[1:]:
            if x - last >= d:
                placed += 1
                last = x
                if placed >= m:
                    return True
        return placed >= m

    lo, hi = 1, (pos[-1] - pos[0]) // (m - 1)
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if can(mid):
            lo = mid
        else:
            hi = mid - 1
    return lo
''',
    tests=[[[1, 2, 3, 4, 7], 3], [[5, 4, 3, 2, 1, 10 ** 9], 2], [[1, 2], 2], [[1, 2, 3], 3], [[1, 2, 3], 2], [[10, 1, 20, 5], 3],
           [[1, 10 ** 9], 2], [[3, 9, 15, 21, 27], 5], [[3, 9, 15, 21, 27], 3], [[1, 100, 101, 102, 200], 3],
           [[7, 1, 4, 10, 13, 16], 4], [[1, 2, 4, 8, 16, 32, 64], 4]],
)
_r = rnd(7106)
_ps = _r.sample(range(1, 10 ** 9), 10000)
p["tests"].append([_ps, 2])
p["tests"].append([_ps, 10000])
p["tests"].append([_ps, 3])
p["tests"].append([_ps, 500])
p["tests"].append([_ps, 5000])
p["tests"].append([_r.sample(range(1, 20001), 10000), 4000])
p["tests"].append([list(range(1, 10001)), 9999])


def b_balls(positions, m):
    pos = sorted(positions)
    best = 0
    for combo in combinations(pos, m):
        best = max(best, min(combo[i + 1] - combo[i] for i in range(m - 1)))
    return best


def g_balls(r):
    n = r.randint(2, 9)
    return [r.sample(range(1, 40), n), r.randint(2, n)]


def v_balls(tests):
    for t in tests:
        pos, m = t["args"]
        assert 2 <= m <= len(pos) <= 10000
        assert len(set(pos)) == len(pos) and all(1 <= x <= 10 ** 9 for x in pos)


CHECKS["maximize-min-gap-between-balls"] = (b_balls, g_balls, "exact")
VALIDATE["maximize-min-gap-between-balls"] = v_balls

p = add(
    id="kth-smallest-in-sorted-grid", title="Kth Smallest in a Row- and Column-Sorted Grid", diff="Medium", topic="Binary Search",
    fn="kthInGrid", params=[("grid", "int[][]"), ("k", "int")], ret="int", cmp="exact",
    desc="<p>In the <code>m x n</code> matrix <code>grid</code>, every row is sorted in non-decreasing order from left to right, and every column is sorted in non-decreasing order from top to bottom. Values may repeat.</p><p>Return the <code>k</code>-th smallest value when all <code>m * n</code> cells are put in sorted order (so duplicates count separately: in <code>[1, 1, 2]</code> the 2nd smallest is <code>1</code>). Try to avoid sorting all the cells.</p>",
    constraints=["1 &le; m, n &le; 100", "-10<sup>9</sup> &le; grid[i][j] &le; 10<sup>9</sup>", "1 &le; k &le; m * n", "Each row and each column is in non-decreasing order"],
    hints=["Flattening and sorting works in O(mn log(mn)). The row and column order should let you do better.",
           "Instead of searching positions, search values: for a number <code>x</code>, how many cells are &le; <code>x</code>? Can you count that without looking at every cell?",
           "Count cells &le; <code>x</code> by walking a staircase from the bottom-left corner: move up when the cell is greater than <code>x</code>, otherwise count the column prefix and move right. Binary search the smallest <code>x</code> in <code>[grid[0][0], grid[m-1][n-1]]</code> whose count is at least <code>k</code>."],
    editorial=["The answer is a value that exists in the grid, lying between the top-left and bottom-right cells. Define <code>count(x)</code> as the number of cells with value &le; <code>x</code>; it never decreases as <code>x</code> grows. The k-th smallest value is the smallest <code>x</code> with <code>count(x) &ge; k</code>, and that <code>x</code> is always an actual cell value, because <code>count</code> only jumps at values present in the grid.",
               "Compute <code>count(x)</code> in O(m + n): begin at the bottom-left cell; if it exceeds <code>x</code> move up, otherwise all cells above it in this column are &le; <code>x</code>, so add <code>row + 1</code> and move right. Binary search over the value range takes about 31 iterations, for O((m + n) log(range)) time and O(1) space. A min-heap that pops <code>k</code> times is another option at O(k log m)."],
    time="O((m + n) log R)", space="O(1)",
    solution='''def kthInGrid(grid, k):
    m, n = len(grid), len(grid[0])

    def count_le(x):
        row, col, total = m - 1, 0, 0
        while row >= 0 and col < n:
            if grid[row][col] > x:
                row -= 1
            else:
                total += row + 1
                col += 1
        return total

    lo, hi = grid[0][0], grid[m - 1][n - 1]
    while lo < hi:
        mid = (lo + hi) // 2
        if count_le(mid) >= k:
            hi = mid
        else:
            lo = mid + 1
    return lo
''',
    tests=[[[[1, 5, 9], [10, 11, 13], [12, 13, 15]], 8], [[[-5]], 1], [[[1, 2], [1, 3]], 2], [[[1, 2], [1, 3]], 1], [[[1, 2], [1, 3]], 4],
           [[[7, 7, 7], [7, 7, 7]], 5], [[[1, 2, 3, 4, 5]], 4], [[[1], [2], [3], [4]], 3], [[[1, 3, 5], [2, 4, 6], [3, 5, 7]], 5],
           [[[-10 ** 9, 0], [0, 10 ** 9]], 3], [[[-10 ** 9, 0], [0, 10 ** 9]], 4], [[[1, 1, 3], [1, 2, 4], [2, 4, 6]], 6]],
)
_r = rnd(7107)
_g = _mono_grid(_r, 100, 100, -10 ** 9, 10 ** 9, False)
p["tests"].append([_g, 1])
p["tests"].append([_g, 10000])
p["tests"].append([_g, 5000])
p["tests"].append([_g, 7777])
_g = _mono_grid(_r, 100, 100, 0, 30, False)
p["tests"].append([_g, 4321])
p["tests"].append([_g, 9999])
p["tests"].append([_mono_grid(_r, 1, 100, -99, 99, False), 57])
p["tests"].append([_mono_grid(_r, 100, 1, -99, 99, False), 12])
p["tests"].append([[[3] * 100 for _ in range(100)], 6000])


def b_kth(grid, k):
    return sorted(x for row in grid for x in row)[k - 1]


def g_kth(r):
    m, n = r.randint(1, 5), r.randint(1, 5)
    return [_mono_grid(r, m, n, -6, 6, False), r.randint(1, m * n)]


def v_kth(tests):
    for t in tests:
        g, k = t["args"]
        m, n = len(g), len(g[0])
        assert 1 <= m <= 100 and 1 <= n <= 100 and 1 <= k <= m * n
        assert all(len(row) == n for row in g)
        assert all(-10 ** 9 <= x <= 10 ** 9 for row in g for x in row)
        for i in range(m):
            for j in range(n):
                if j + 1 < n:
                    assert g[i][j] <= g[i][j + 1]
                if i + 1 < m:
                    assert g[i][j] <= g[i + 1][j]


CHECKS["kth-smallest-in-sorted-grid"] = (b_kth, g_kth, "exact")
VALIDATE["kth-smallest-in-sorted-grid"] = v_kth


# ---------------------------------------------------------------- HARD

p = add(
    id="kth-smallest-pair-gap", title="Kth Smallest Pair Gap", diff="Hard", topic="Binary Search",
    fn="kthPairGap", params=[("nums", "int[]"), ("k", "int")], ret="int", cmp="exact",
    desc="<p>For an integer array <code>nums</code>, the <em>gap</em> of a pair of positions <code>i &lt; j</code> is <code>|nums[i] - nums[j]|</code>. There are <code>n(n-1)/2</code> such pairs, and different pairs may have the same gap.</p><p>List the gaps of all pairs in non-decreasing order and return the <code>k</code>-th one (1-indexed). The array can be long, so enumerating all pairs is too slow.</p>",
    constraints=["2 &le; nums.length &le; 10,000", "-10<sup>9</sup> &le; nums[i] &le; 10<sup>9</sup>", "1 &le; k &le; n(n-1)/2"],
    hints=["Generating all pairs and sorting needs O(n<sup>2</sup>) memory and time. Think about the answer's <em>value</em> instead of enumerating the pairs.",
           "Sort the array first. For a candidate gap <code>d</code>, can you count the pairs with gap at most <code>d</code> in about O(n) time?",
           "With the array sorted, the left end of the window <code>[left, right]</code> of elements within <code>d</code> of <code>nums[right]</code> only moves right as <code>right</code> grows, so a two-pointer sweep counts pairs. Binary search the smallest <code>d</code> in <code>[0, max - min]</code> whose count is at least <code>k</code>."],
    editorial=["After sorting, the gap of a pair is just the difference of its values, and the gap between positions <code>i &lt; j</code> is non-decreasing as the pair spreads apart. Let <code>count(d)</code> be the number of pairs with gap &le; <code>d</code>. It is monotone in <code>d</code>, and the answer is the smallest <code>d</code> with <code>count(d) &ge; k</code>; at that point the answer is necessarily an actual gap, because the count only increases at gap values that occur.",
               "To compute <code>count(d)</code>, sweep <code>right</code> over the sorted array while keeping <code>left</code> as the first index with <code>nums[right] - nums[left] &le; d</code>. Every index in <code>[left, right - 1]</code> forms a valid pair with <code>right</code>, adding <code>right - left</code> to the total. Since <code>left</code> never moves backwards, the sweep is O(n). The search over <code>d</code> takes about 31 iterations, for O(n log n + n log(max - min)) time and O(1) extra space after sorting. The largest possible gap is 2&middot;10<sup>9</sup>, which still fits in a signed 32-bit integer."],
    time="O(n log n + n log R)", space="O(1) extra",
    solution='''def kthPairGap(nums, k):
    a = sorted(nums)
    n = len(a)

    def pairs_within(d):
        total = left = 0
        for right in range(n):
            while a[right] - a[left] > d:
                left += 1
            total += right - left
        return total

    lo, hi = 0, a[-1] - a[0]
    while lo < hi:
        mid = (lo + hi) // 2
        if pairs_within(mid) >= k:
            hi = mid
        else:
            lo = mid + 1
    return lo
''',
    tests=[[[1, 3, 1], 1], [[1, 1, 1], 2], [[1, 6, 1], 3], [[1, 6, 1], 2], [[0, 5], 1], [[-10 ** 9, 10 ** 9], 1],
           [[9, 10, 7, 10, 6, 1, 5, 4, 9, 8], 18], [[5, 5, 5, 5], 6], [[1, 2, 3, 4], 5], [[1, 2, 3, 4], 6], [[-3, 0, 3], 2],
           [[10, 20, 40, 80], 4], [[7, 7], 1]],
)
_r = rnd(7108)
_a = [_r.randint(-10 ** 9, 10 ** 9) for _ in range(10000)]
p["tests"].append([_a, 1])
p["tests"].append([_a, 49995000])
p["tests"].append([_a, 24997500])
p["tests"].append([_a, 123456])
_a = [_r.randint(0, 1000) for _ in range(10000)]
p["tests"].append([_a, 1])
p["tests"].append([_a, 30000000])
p["tests"].append([_a, 49995000])
p["tests"].append([[i * 7 for i in range(10000)], 40000000])
p["tests"].append([[4] * 10000, 49995000])
p["tests"].append([[(-1) ** i * (10 ** 9) for i in range(10000)], 49995000])


def b_pair(nums, k):
    gaps = sorted(abs(nums[i] - nums[j]) for i in range(len(nums)) for j in range(i + 1, len(nums)))
    return gaps[k - 1]


def g_pair(r):
    n = r.randint(2, 9)
    return [[r.randint(-15, 15) for _ in range(n)], r.randint(1, n * (n - 1) // 2)]


def v_pair(tests):
    for t in tests:
        nums, k = t["args"]
        n = len(nums)
        assert 2 <= n <= 10000 and all(-10 ** 9 <= x <= 10 ** 9 for x in nums)
        assert 1 <= k <= n * (n - 1) // 2


CHECKS["kth-smallest-pair-gap"] = (b_pair, g_pair, "exact")
VALIDATE["kth-smallest-pair-gap"] = v_pair

p = add(
    id="min-max-gap-after-adding-stations", title="Minimize the Largest Gap After Adding Stations", diff="Hard", topic="Binary Search",
    fn="minLargestGap", params=[("stations", "int[]"), ("k", "int")], ret="int", cmp="exact",
    desc="<p>Fuel stations stand at the strictly increasing integer coordinates in <code>stations</code> along a straight road. You may build <code>k</code> additional stations, each at any integer coordinate (several may share a segment between two existing stations, but two stations cannot be at the same point).</p><p>After building, look at the distances between consecutive stations. Return the smallest possible value of the <em>largest</em> such distance. If there is only one station, there are no distances and the answer is <code>0</code>.</p>",
    constraints=["1 &le; stations.length &le; 10,000", "0 &le; stations[0] &lt; stations[1] &lt; ... &le; 10<sup>9</sup>", "0 &le; k &le; 10<sup>9</sup>"],
    hints=["Only the gaps between neighbouring stations matter, and the new stations for one gap are independent of the others except for sharing the budget <code>k</code>.",
           "Fix a target maximum gap <code>D</code>. A gap of length <code>g</code> needs the fewest extra stations when it is cut into parts of length at most <code>D</code>. How many stations is that?",
           "A gap <code>g</code> needs <code>ceil(g / D) - 1</code> new stations, i.e. <code>(g - 1) // D</code>. Binary search the smallest <code>D</code> from 1 to the largest gap such that the total needed over all gaps is at most <code>k</code>."],
    editorial=["The largest gap is a lower-bounded-by-1 integer that never gets worse when more stations are allowed, so the question is: for a given <code>D</code>, what is the minimum number of new stations that makes every gap at most <code>D</code>? A gap of length <code>g</code> split into <code>t</code> equal-as-possible integer pieces has largest piece <code>ceil(g / t)</code>, so it needs <code>ceil(g / D) - 1 = (g - 1) // D</code> new stations (zero when <code>g &le; D</code>). Summing over all gaps gives <code>need(D)</code>.",
               "<code>need(D)</code> decreases as <code>D</code> grows, so binary search the smallest <code>D</code> in <code>[1, maxGap]</code> with <code>need(D) &le; k</code>. Note that <code>D = 1</code> is the floor because stations sit at distinct integer points. With a single station the answer is 0. Complexity: O(n log(maxGap)) time, O(1) extra space. The sum of needs can be as large as about 10<sup>9</sup>, so use a type that holds it (in 32-bit languages it still fits, since the gaps sum to at most 10<sup>9</sup>)."],
    time="O(n log G)", space="O(1)",
    solution='''def minLargestGap(stations, k):
    n = len(stations)
    if n == 1:
        return 0
    gaps = [stations[i + 1] - stations[i] for i in range(n - 1)]

    def need(d):
        return sum((g - 1) // d for g in gaps)

    lo, hi = 1, max(gaps)
    while lo < hi:
        mid = (lo + hi) // 2
        if need(mid) <= k:
            hi = mid
        else:
            lo = mid + 1
    return lo
''',
    tests=[[[1, 2, 3, 4, 5, 6, 7, 8, 9, 10], 9], [[0, 100], 1], [[0, 100], 3], [[0, 100], 0], [[5], 10], [[0, 1, 10], 2], [[0, 1, 10], 0],
           [[3, 9, 20, 46], 4], [[0, 10 ** 9], 10 ** 9], [[0, 10 ** 9], 10 ** 9 - 2], [[0, 7], 5], [[2, 3], 100], [[0, 10, 20, 30], 3],
           [[0, 5, 9, 30, 31, 40], 6]],
)
_r = rnd(7109)
_pos = [0]
for _ in range(9999):
    _pos.append(_pos[-1] + _r.randint(1, 100000))
p["tests"].append([_pos, 500000])
p["tests"].append([_pos, 0])
p["tests"].append([_pos, 10 ** 9])
p["tests"].append([_pos, 12345])
_pos2 = [0]
for _ in range(9999):
    _pos2.append(_pos2[-1] + _r.randint(1, 20))
p["tests"].append([_pos2, 100000])
p["tests"].append([_pos2, 3])
p["tests"].append([list(range(0, 10000)), 777])
p["tests"].append([[0, 999999999, 10 ** 9], 12])


def b_stations(stations, k):
    n = len(stations)
    if n == 1:
        return 0
    # greedy with a heap: always give the next new station to the gap whose largest part is currently biggest
    heap = []
    for i in range(n - 1):
        g = stations[i + 1] - stations[i]
        heapq.heappush(heap, (-g, g, 1))  # (-largest part, gap, parts)
    for _ in range(k):
        neg, g, parts = heapq.heappop(heap)
        if -neg == 1:
            heapq.heappush(heap, (neg, g, parts))
            break
        parts += 1
        heapq.heappush(heap, (-((g + parts - 1) // parts), g, parts))
    return -heap[0][0]


def g_stations(r):
    n = r.randint(1, 6)
    pos = [r.randint(0, 5)]
    for _ in range(n - 1):
        pos.append(pos[-1] + r.randint(1, 25))
    return [pos, r.randint(0, 14)]


def v_stations(tests):
    for t in tests:
        st, k = t["args"]
        assert 1 <= len(st) <= 10000 and 0 <= k <= 10 ** 9
        assert 0 <= st[0] and st[-1] <= 10 ** 9
        assert all(st[i] < st[i + 1] for i in range(len(st) - 1))


CHECKS["min-max-gap-after-adding-stations"] = (b_stations, g_stations, "exact")
VALIDATE["min-max-gap-after-adding-stations"] = v_stations
