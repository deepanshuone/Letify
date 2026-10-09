"""Problems: heap / priority queue (second set). See data/lib.py for the registry."""
from itertools import combinations  # noqa: F401

from lib import add, rnd, CHECKS, VALIDATE, gen_arr  # noqa: F401

INT_MIN, INT_MAX = -(2 ** 31), 2 ** 31 - 1
B = 10 ** 9


# ================================================================ EASY

# ---------------------------------------------------------------- minimum cost to connect ropes
p = add(
    id="minimum-cost-to-connect-ropes", title="Minimum Cost to Connect Ropes", diff="Easy", topic="Heap",
    fn="connectRopes", params=[("ropes", "int[]")], ret="int", cmp="exact",
    desc="<p>You have several ropes whose lengths are given in the array <code>ropes</code>. Two ropes can be tied together into one rope; the length of the new rope is the sum of the two lengths, and tying them costs exactly that sum.</p><p>Keep tying until only one rope is left and return the minimum total cost.</p><pre>ropes = [4, 3, 2, 6]\n2 + 3 = 5   (cost 5)   -> [4, 5, 6]\n4 + 5 = 9   (cost 9)   -> [9, 6]\n9 + 6 = 15  (cost 15)  -> [15]\ntotal = 29</pre><p>A single rope needs no tying, so the cost is 0.</p>",
    constraints=["1 &le; ropes.length &le; 5,000", "1 &le; ropes[i] &le; 1,000"],
    hints=["Every time two ropes are tied, the new rope is paid for again whenever it is tied later. Which ropes would you like to be tied last?",
           "Short ropes should be merged early so that their length is re-counted as little as possible; long ropes should be merged late.",
           "Greedy: always tie the two shortest ropes. A min-heap gives you the two smallest in O(log n), and you push the merged rope back."],
    editorial=["The total cost equals the sum over all original ropes of (length times the number of merges it takes part in). A rope that is merged early sits deep in the merge tree and is paid for many times, so the cheap way is to bury the shortest ropes deepest. This is exactly Huffman coding.",
               "Put all lengths in a min-heap. While more than one rope remains, pop the two smallest, add their sum to the answer, and push the sum back. Each of the n-1 merges costs O(log n), for O(n log n) overall.",
               "Sorting once is not enough because the merged rope can be shorter than some remaining original rope but longer than others, so it has to be inserted in the right place; the heap does that automatically."],
    time="O(n log n)", space="O(n)",
    solution='''import heapq


def connectRopes(ropes):
    h = list(ropes)
    heapq.heapify(h)
    total = 0
    while len(h) > 1:
        s = heapq.heappop(h) + heapq.heappop(h)
        total += s
        heapq.heappush(h, s)
    return total
''',
    tests=[[[4, 3, 2, 6]], [[1, 8, 3, 5]], [[7]], [[1, 1]], [[5, 5, 5, 5]], [[1, 2, 3, 4, 5]], [[1000, 1]],
           [[2, 2, 3]], [[1, 1, 1, 1, 1, 1, 1, 1]], [[10, 1, 1, 1]]],
)
_r = rnd(8101)
p["tests"].append([[_r.randint(1, 1000) for _ in range(5000)]])
p["tests"].append([[1000] * 5000])
p["tests"].append([[1] * 4096])
p["tests"].append([[2 ** i if i < 10 else 1000 for i in range(60)] + [_r.randint(1, 1000) for _ in range(2000)]])


def b_ropes(ropes):
    seen = {}

    def go(t):
        if len(t) == 1:
            return 0
        if t in seen:
            return seen[t]
        best = None
        for i in range(len(t)):
            for j in range(i + 1, len(t)):
                rest = [t[x] for x in range(len(t)) if x != i and x != j]
                s = t[i] + t[j]
                c = s + go(tuple(sorted(rest + [s])))
                if best is None or c < best:
                    best = c
        seen[t] = best
        return best

    return go(tuple(sorted(ropes)))


def v_ropes(tests):
    for t in tests:
        a = t["args"][0]
        assert 1 <= len(a) <= 5000 and all(1 <= x <= 1000 for x in a)


CHECKS["minimum-cost-to-connect-ropes"] = (b_ropes, lambda r: [[r.randint(1, 12) for _ in range(r.randint(1, 6))]], "exact")
VALIDATE["minimum-cost-to-connect-ropes"] = v_ropes

# ---------------------------------------------------------------- running kth largest
p = add(
    id="running-kth-largest-heap", title="Running Kth Largest", diff="Easy", topic="Heap",
    fn="runningKthLargest", params=[("nums", "int[]"), ("k", "int")], ret="int[]", cmp="exact",
    desc="<p>Numbers arrive one at a time in the order given by <code>nums</code>. After each number arrives, report the <code>k</code>-th largest value among all numbers received so far. Duplicates count separately, so in <code>[5, 5, 2]</code> the 2nd largest is <code>5</code>.</p><p>If fewer than <code>k</code> numbers have arrived, report <code>-1</code> for that step. Return the list of reports, one per arrival.</p><pre>nums = [4, 1, 7, 3, 9], k = 2\nafter 4 -> -1        (only one number)\nafter 1 -> 1         (4, 1)\nafter 7 -> 4         (7, 4, 1)\nafter 3 -> 4         (7, 4, 3, 1)\nafter 9 -> 7         (9, 7, 4, 3, 1)\nanswer = [-1, 1, 4, 4, 7]</pre>",
    constraints=["1 &le; nums.length &le; 10,000", "1 &le; k &le; 10,000", "0 &le; nums[i] &le; 10<sup>9</sup>"],
    hints=["Sorting the prefix after every arrival works but costs O(n<sup>2</sup> log n) overall. What do you really need to remember?",
           "Only the k largest values seen so far matter; the smallest of those k is the answer.",
           "Keep a min-heap of size at most k. A new value enters only if the heap is not full or it beats the heap's minimum (which it then replaces). The answer is the heap's top once it holds k values."],
    editorial=["The k-th largest of a set is the smallest element of its k largest elements. So it is enough to maintain exactly those k elements in a min-heap, where the root is the smallest of them.",
               "On each arrival: if the heap has fewer than k items, push the value. Otherwise, if the value is larger than the root, replace the root with it (pop and push); if it is not larger, it can never become part of the top k later either, so ignore it. Report the root when the heap size is k, and -1 otherwise.",
               "Every step is O(log k), so the whole run costs O(n log k) time and O(k) space."],
    time="O(n log k)", space="O(k)",
    solution='''import heapq


def runningKthLargest(nums, k):
    h = []
    out = []
    for x in nums:
        if len(h) < k:
            heapq.heappush(h, x)
        elif x > h[0]:
            heapq.heapreplace(h, x)
        out.append(h[0] if len(h) == k else -1)
    return out
''',
    tests=[[[4, 1, 7, 3, 9], 2], [[5], 1], [[5], 2], [[3, 3, 3], 2], [[1, 2, 3, 4, 5], 1], [[5, 4, 3, 2, 1], 5],
           [[0, 0, 0, 0], 3], [[10, 9, 8, 7, 6, 5], 3], [[1, 2, 3, 4, 5, 6], 3], [[B, 0, B, 0, B], 2], [[7, 7, 1, 7], 4]],
)
_r = rnd(8102)
p["tests"].append([[_r.randint(0, B) for _ in range(10000)], 1])
p["tests"].append([[_r.randint(0, B) for _ in range(10000)], 100])
p["tests"].append([[_r.randint(0, 50) for _ in range(10000)], 3000])
p["tests"].append([list(range(10000)), 10000])
p["tests"].append([list(range(10000, 0, -1)), 5000])


def b_runk(nums, k):
    out = []
    for i in range(len(nums)):
        pre = sorted(nums[:i + 1], reverse=True)
        out.append(pre[k - 1] if len(pre) >= k else -1)
    return out


def v_runk(tests):
    for t in tests:
        nums, k = t["args"]
        assert 1 <= len(nums) <= 10000 and 1 <= k <= 10000
        assert all(0 <= x <= B for x in nums)


CHECKS["running-kth-largest-heap"] = (b_runk, lambda r: [[r.randint(0, 8) for _ in range(r.randint(1, 12))], r.randint(1, 6)], "exact")
VALIDATE["running-kth-largest-heap"] = v_runk


# ================================================================ MEDIUM

# ---------------------------------------------------------------- merge k sorted rows
p = add(
    id="merge-k-sorted-rows", title="Merge K Sorted Rows", diff="Medium", topic="Heap",
    fn="mergeSortedRows", params=[("rows", "int[][]")], ret="int[]", cmp="exact",
    desc="<p>The 2D array <code>rows</code> contains <code>k</code> rows, each already sorted in non-decreasing order. Some rows may be empty. Merge every value from every row into one sorted array and return it.</p><pre>rows = [[1, 4, 9], [], [2, 3, 10]]\nanswer = [1, 2, 3, 4, 9, 10]</pre><p>Aim for a running time that depends on <code>log k</code> rather than on sorting everything from scratch.</p>",
    constraints=["1 &le; rows.length &le; 1,000", "The total number of values is at most 10,000", "-10<sup>9</sup> &le; value &le; 10<sup>9</sup>", "Each row is sorted in non-decreasing order"],
    hints=["Concatenating everything and sorting is valid but ignores that each row is already sorted.",
           "At any moment the next output value must be the smallest among the first unused value of each row.",
           "Keep a min-heap containing one entry per non-empty row: (value, row index, position). Pop the smallest, append it to the answer, and push the next value from the same row if there is one."],
    editorial=["Treat each row as a queue whose front is its smallest unused value. The global minimum of the remaining data is always the minimum of the k fronts. A min-heap of the fronts gives it in O(log k).",
               "Initialise the heap with the first element of every non-empty row. Repeatedly pop <code>(value, row, pos)</code>, output the value, and push <code>(rows[row][pos+1], row, pos+1)</code> when that element exists. Including the row index in the tuple only serves to give heap comparisons a deterministic tie-break; no two entries of the same row are ever in the heap simultaneously.",
               "Every one of the N values is pushed and popped once, so the cost is O(N log k) time and O(k) heap space (plus the output)."],
    time="O(N log k)", space="O(k)",
    solution='''import heapq


def mergeSortedRows(rows):
    h = [(row[0], i, 0) for i, row in enumerate(rows) if row]
    heapq.heapify(h)
    out = []
    while h:
        v, i, j = heapq.heappop(h)
        out.append(v)
        if j + 1 < len(rows[i]):
            heapq.heappush(h, (rows[i][j + 1], i, j + 1))
    return out
''',
    tests=[[[[1, 4, 9], [], [2, 3, 10]]], [[[]]], [[[5]]], [[[1, 2, 3]]], [[[1, 3, 5], [2, 4, 6]]], [[[], [], []]],
           [[[-5, -1, 0], [-3, -3, 7], [0, 0, 0]]], [[[1, 1, 1], [1, 1], [1]]], [[[B], [-B], [0]]],
           [[[1, 2, 3], [4, 5, 6], [7, 8, 9]]], [[[7, 8, 9], [4, 5, 6], [1, 2, 3]]], [[[2], [], [1], [], [3]]]],
)
_r = rnd(8104)
p["tests"].append([[sorted(_r.randint(-B, B) for _ in range(10)) for _ in range(1000)]])
p["tests"].append([[sorted(_r.randint(-50, 50) for _ in range(_r.randint(0, 40))) for _ in range(250)]])
p["tests"].append([[sorted(_r.randint(-B, B) for _ in range(5000)), sorted(_r.randint(-B, B) for _ in range(5000))]])
p["tests"].append([[[i] for i in range(1000, 0, -1)]])


def b_merge(rows):
    out = []
    for row in rows:
        merged = []
        i = j = 0
        while i < len(out) or j < len(row):
            if j >= len(row) or (i < len(out) and out[i] <= row[j]):
                merged.append(out[i]); i += 1
            else:
                merged.append(row[j]); j += 1
        out = merged
    return out


def g_merge(r):
    return [[sorted(r.randint(-9, 9) for _ in range(r.randint(0, 5))) for _ in range(r.randint(1, 6))]]


def v_merge(tests):
    for t in tests:
        rows = t["args"][0]
        assert 1 <= len(rows) <= 1000 and sum(len(x) for x in rows) <= 10000
        for row in rows:
            assert all(-B <= x <= B for x in row) and row == sorted(row)


CHECKS["merge-k-sorted-rows"] = (b_merge, g_merge, "exact")
VALIDATE["merge-k-sorted-rows"] = v_merge

# ---------------------------------------------------------------- furthest building
p = add(
    id="furthest-building-with-ladders", title="Furthest Building With Ladders", diff="Medium", topic="Heap",
    fn="furthestBuilding", params=[("heights", "int[]"), ("bricks", "int"), ("ladders", "int")], ret="int", cmp="exact",
    desc="<p>You stand on the roof of building <code>0</code> and want to walk to the right across a row of buildings whose roof heights are in <code>heights</code>. To step from building <code>i</code> to <code>i + 1</code>:</p><ul><li>if <code>heights[i] &ge; heights[i+1]</code>, the step is free;</li><li>otherwise you must climb <code>d = heights[i+1] - heights[i]</code>, either by using one ladder (any <code>d</code>, ladder used up) or by using exactly <code>d</code> bricks.</li></ul><p>You have <code>bricks</code> bricks and <code>ladders</code> ladders in total. Return the index of the furthest building you can reach.</p><pre>heights = [2, 5, 3, 4, 9, 1], bricks = 3, ladders = 1\nclimbs: +3 (0 to 1), +1 (2 to 3), +5 (3 to 4)\nladder on +3, brick on +1 reaches index 3; also covering +5 is impossible\nanswer = 3</pre>",
    constraints=["1 &le; heights.length &le; 10,000", "1 &le; heights[i] &le; 10<sup>6</sup>", "0 &le; bricks &le; 10<sup>9</sup>", "0 &le; ladders &le; heights.length"],
    hints=["Descending steps are free. Only upward steps matter; think of them as a list of climb sizes.",
           "Ladders are most valuable on the biggest climbs, because a ladder covers any size for the price of one.",
           "Walk left to right, pushing each climb into a min-heap. Whenever the heap holds more than 'ladders' climbs, pay for the smallest one with bricks. If bricks go negative, you got stuck right before this step."],
    editorial=["Among the climbs you have met so far, the best use of the ladders is on the largest ones, with bricks paying for all the rest. The set of climbs assigned to ladders can change as you walk further: a bigger climb should take over a ladder from a smaller one.",
               "A min-heap of the climbs currently covered by ladders implements this. For each upward step push its size. If the heap then has more than <code>ladders</code> entries, the smallest of them gets downgraded to bricks: pop it and subtract it from the brick supply. If the supply drops below zero, building <code>i</code> is the furthest reachable.",
               "If you finish the loop, you can reach the last building. Time is O(n log L) where L is the number of ladders, with O(L) extra space."],
    time="O(n log L)", space="O(L)",
    solution='''import heapq


def furthestBuilding(heights, bricks, ladders):
    h = []
    for i in range(len(heights) - 1):
        d = heights[i + 1] - heights[i]
        if d <= 0:
            continue
        heapq.heappush(h, d)
        if len(h) > ladders:
            bricks -= heapq.heappop(h)
            if bricks < 0:
                return i
    return len(heights) - 1
''',
    tests=[[[2, 5, 3, 4, 9, 1], 3, 1], [[1, 2, 3, 4], 0, 3], [[7, 3, 1], 0, 0], [[5], 0, 0], [[1, 100], 0, 0], [[1, 100], 99, 0],
           [[1, 100], 98, 0], [[1, 100], 0, 1], [[4, 2, 7, 6, 9, 14, 12], 5, 1], [[4, 12, 2, 7, 3, 18, 20, 3, 19], 10, 2],
           [[14, 3, 19, 3], 17, 0], [[1, 5, 1, 2, 3, 4, 10000], 0, 5], [[1, 5, 1, 2, 3, 4, 10000], 0, 6]],
)
_r = rnd(8105)
_h = [_r.randint(1, 10 ** 6) for _ in range(10000)]
p["tests"].append([_h, 5 * 10 ** 8, 40])
p["tests"].append([_h, 10 ** 9, 5000])
p["tests"].append([_h, 100, 3])
p["tests"].append([list(range(1, 10001)), 10 ** 9, 0])
p["tests"].append([list(range(1, 10001)), 3 * 10 ** 7, 50])
p["tests"].append([[1 + (i % 2) * 1000 for i in range(10000)], 40000, 0])


def b_furthest(heights, bricks, ladders):
    n = len(heights)

    def go(i, b, l):
        if i == n - 1:
            return i
        d = heights[i + 1] - heights[i]
        if d <= 0:
            return go(i + 1, b, l)
        best = i
        if b >= d:
            best = max(best, go(i + 1, b - d, l))
        if l > 0:
            best = max(best, go(i + 1, b, l - 1))
        return best

    return go(0, bricks, ladders)


def g_furthest(r):
    n = r.randint(1, 11)
    return [[r.randint(1, 12) for _ in range(n)], r.randint(0, 20), r.randint(0, min(n, 3))]


def v_furthest(tests):
    for t in tests:
        h, b, l = t["args"]
        assert 1 <= len(h) <= 10000 and all(1 <= x <= 10 ** 6 for x in h)
        assert 0 <= b <= B and 0 <= l <= len(h)


CHECKS["furthest-building-with-ladders"] = (b_furthest, g_furthest, "exact")
VALIDATE["furthest-building-with-ladders"] = v_furthest

# ---------------------------------------------------------------- k smallest pair sums
p = add(
    id="k-smallest-pair-sums", title="K Smallest Pair Sums", diff="Medium", topic="Heap",
    fn="kSmallestPairSums", params=[("a", "int[]"), ("b", "int[]"), ("k", "int")], ret="int[]", cmp="exact",
    desc="<p>Two arrays <code>a</code> and <code>b</code>, each sorted in non-decreasing order, are given. Consider every pair <code>(a[i], b[j])</code> formed by taking one value from each array; the pair's sum is <code>a[i] + b[j]</code>. Different index pairs count as different pairs even if their values are equal.</p><p>Return the <code>k</code> smallest pair sums in non-decreasing order.</p><pre>a = [1, 7, 11], b = [2, 4, 6], k = 3\nsums: 3, 5, 7, 9, 11, 13, 13, 15, 17\nanswer = [3, 5, 7]</pre>",
    constraints=["1 &le; a.length, b.length &le; 5,000", "-10<sup>9</sup> &le; a[i], b[j] &le; 10<sup>9</sup>", "Both arrays are sorted in non-decreasing order", "1 &le; k &le; min(a.length * b.length, 10,000)"],
    hints=["Building all a.length * b.length sums is too slow for large inputs. Use the sorted order.",
           "Think of a grid where cell (i, j) holds a[i] + b[j]. Each row and each column is non-decreasing.",
           "Start the heap with (a[i] + b[0], i, 0) for the first min(k, len(a)) values of i. After popping (i, j), push (i, j + 1). Each pop yields the next smallest sum."],
    editorial=["The sums form a grid with sorted rows and columns, so every cell is at least as large as the cell above it and the cell to its left. Only cells whose upper and left neighbours have already been output can be the next smallest.",
               "Seed a min-heap with the first column (one cell per value of a, at most k of them, because a row beyond the k-th can never contribute before the earlier ones do). Pop the smallest cell, record its sum, and push the cell to its right in the same row. Since each row advances independently, no cell is pushed twice and no visited set is needed.",
               "After k pops we are done: O((k + min(k, n)) log min(k, n)) time and O(min(k, n)) space."],
    time="O(k log min(k, n))", space="O(min(k, n))",
    solution='''import heapq


def kSmallestPairSums(a, b, k):
    h = [(a[i] + b[0], i, 0) for i in range(min(len(a), k))]
    heapq.heapify(h)
    out = []
    while h and len(out) < k:
        s, i, j = heapq.heappop(h)
        out.append(s)
        if j + 1 < len(b):
            heapq.heappush(h, (a[i] + b[j + 1], i, j + 1))
    return out
''',
    tests=[[[1, 7, 11], [2, 4, 6], 3], [[1, 1, 2], [1, 2, 3], 4], [[1, 2], [3], 2], [[5], [5], 1], [[1, 2], [3, 4], 4],
           [[-3, 0, 4], [-5, 1, 2], 9], [[0, 0, 0], [0, 0, 0], 5], [[-B, 0, B], [-B, 0, B], 4], [[1, 2, 3], [1], 3],
           [[1], [1, 2, 3], 2], [[B], [B], 1], [[-B, -B], [-B, -B], 4]],
)
_r = rnd(8106)
_a = sorted(_r.randint(-B, B) for _ in range(5000))
_b = sorted(_r.randint(-B, B) for _ in range(5000))
p["tests"].append([_a, _b, 10000])
p["tests"].append([_a, _b, 1])
p["tests"].append([sorted(_r.randint(-20, 20) for _ in range(5000)), sorted(_r.randint(-20, 20) for _ in range(5000)), 10000])
p["tests"].append([list(range(5000)), list(range(5000)), 9999])
p["tests"].append([[0] * 100, list(range(100)), 10000])


def b_pairsums(a, b, k):
    return sorted(x + y for x in a for y in b)[:k]


def g_pairsums(r):
    a = sorted(r.randint(-8, 8) for _ in range(r.randint(1, 6)))
    b = sorted(r.randint(-8, 8) for _ in range(r.randint(1, 6)))
    return [a, b, r.randint(1, len(a) * len(b))]


def v_pairsums(tests):
    for t in tests:
        a, b, k = t["args"]
        assert 1 <= len(a) <= 5000 and 1 <= len(b) <= 5000
        assert a == sorted(a) and b == sorted(b)
        assert all(-B <= x <= B for x in a + b)
        assert 1 <= k <= min(len(a) * len(b), 10000)


CHECKS["k-smallest-pair-sums"] = (b_pairsums, g_pairsums, "exact")
VALIDATE["k-smallest-pair-sums"] = v_pairsums

# ---------------------------------------------------------------- kth smallest in sorted matrix (heap)
p = add(
    id="kth-smallest-in-sorted-matrix-heap", title="Kth Smallest in a Sorted Matrix", diff="Medium", topic="Heap",
    fn="kthSmallestMatrix", params=[("matrix", "int[][]"), ("k", "int")], ret="int", cmp="exact",
    desc="<p>An <code>n x n</code> matrix is given in which every row is sorted in non-decreasing order from left to right and every column is sorted in non-decreasing order from top to bottom. Return the <code>k</code>-th smallest value in the whole matrix, counting repeated values separately (so in the sorted list of all <code>n*n</code> values it is the one at position <code>k</code>, starting from 1).</p><pre>matrix = [[ 1,  5,  9],\n          [10, 11, 13],\n          [12, 13, 15]], k = 8\nsorted values: 1 5 9 10 11 12 13 13 15\nanswer = 13</pre><p>Try to avoid flattening and sorting the entire matrix.</p>",
    constraints=["1 &le; n &le; 120", "-10<sup>9</sup> &le; matrix[i][j] &le; 10<sup>9</sup>", "Rows and columns are sorted in non-decreasing order", "1 &le; k &le; n * n"],
    hints=["Flattening and sorting costs O(n<sup>2</sup> log n). You can use the structure of the matrix to do better when k is small.",
           "The smallest value is the top-left corner. After taking a cell, which cells could be the next smallest?",
           "Put the first cell of each of the first min(n, k) rows in a min-heap as (value, row, col). Pop k times; after each pop push the cell to its right in the same row. The k-th popped value is the answer."],
    editorial=["Each row is a sorted list, so this is the problem of merging n sorted lists and stopping after k elements. Only the first k rows can contribute to the k smallest (because column order guarantees that row r has r smaller values above its first cell), so we limit the initial heap to min(n, k) rows.",
               "Pop the minimum k times. Each pop of cell <code>(r, c)</code> is followed by pushing <code>(r, c+1)</code> when it exists. The k-th value popped is the k-th smallest of the matrix.",
               "Time is O((min(n, k) + k) log min(n, k)); space is O(min(n, k)). A binary search on the value range gives O(n log(range)) and is worth comparing, but the heap approach is simpler and does not depend on the value range."],
    time="O(k log n)", space="O(n)",
    solution='''import heapq


def kthSmallestMatrix(matrix, k):
    n = len(matrix)
    h = [(matrix[r][0], r, 0) for r in range(min(n, k))]
    heapq.heapify(h)
    val = 0
    for _ in range(k):
        val, r, c = heapq.heappop(h)
        if c + 1 < n:
            heapq.heappush(h, (matrix[r][c + 1], r, c + 1))
    return val
''',
    tests=[[[[1, 5, 9], [10, 11, 13], [12, 13, 15]], 8], [[[-5]], 1], [[[1, 2], [1, 3]], 2], [[[1, 2], [1, 3]], 4],
           [[[1, 2], [1, 3]], 1], [[[2, 2], [2, 2]], 3], [[[1, 3, 5], [6, 7, 12], [11, 14, 14]], 6],
           [[[-B, -B, 0], [-B, 0, B], [0, B, B]], 5], [[[1, 2, 3], [4, 5, 6], [7, 8, 9]], 9],
           [[[1, 4, 7], [2, 5, 8], [3, 6, 9]], 4]],
)


def _sorted_matrix(r, n, step, base):
    m = [[0] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            up = m[i - 1][j] if i else base
            left = m[i][j - 1] if j else base
            m[i][j] = max(up, left) + r.randint(0, step)
    return m


_r = rnd(8107)
p["tests"].append([_sorted_matrix(_r, 120, 50000, -B), 7000])
p["tests"].append([_sorted_matrix(_r, 120, 50000, -B), 1])
p["tests"].append([_sorted_matrix(_r, 120, 50000, -B), 14400])
p["tests"].append([_sorted_matrix(_r, 120, 2, -5), 9000])
p["tests"].append([_sorted_matrix(_r, 100, 100000, -10 ** 7), 150])
p["tests"].append([[[7] * 120 for _ in range(120)], 777])


def b_kmat(matrix, k):
    vals = []
    for row in matrix:
        vals.extend(row)
    vals.sort()
    return vals[k - 1]


def g_kmat(r):
    n = r.randint(1, 6)
    return [_sorted_matrix(r, n, 4, -6), r.randint(1, n * n)]


def v_kmat(tests):
    for t in tests:
        m, k = t["args"]
        n = len(m)
        assert 1 <= n <= 120 and all(len(row) == n for row in m)
        assert 1 <= k <= n * n
        for i in range(n):
            for j in range(n):
                assert -B <= m[i][j] <= B
                if j:
                    assert m[i][j - 1] <= m[i][j]
                if i:
                    assert m[i - 1][j] <= m[i][j]


CHECKS["kth-smallest-in-sorted-matrix-heap"] = (b_kmat, g_kmat, "exact")
VALIDATE["kth-smallest-in-sorted-matrix-heap"] = v_kmat

# ---------------------------------------------------------------- super ugly number
p = add(
    id="super-ugly-number-heap", title="Super Ugly Number", diff="Medium", topic="Heap",
    fn="nthSuperUgly", params=[("n", "int"), ("primes", "int[]")], ret="int", cmp="exact",
    desc="<p>A positive integer is called <em>super ugly</em> with respect to a list of distinct primes <code>primes</code> if every one of its prime factors appears in <code>primes</code>. The number <code>1</code> has no prime factors, so it is always super ugly and is the first one.</p><p>Return the <code>n</code>-th super ugly number in increasing order.</p><pre>primes = [2, 7, 13], n = 10\nsuper ugly numbers: 1, 2, 4, 7, 8, 13, 14, 16, 26, 28, ...\nanswer = 28</pre>",
    constraints=["1 &le; n &le; 5,000", "1 &le; primes.length &le; 20", "Every primes[i] is a prime number, 2 &le; primes[i] &le; 100, and all are distinct", "The answer is guaranteed to fit in a 32-bit signed integer"],
    hints=["Testing every integer for its prime factors is far too slow once n is large. Build the sequence instead of searching for it.",
           "Every super ugly number other than 1 is a smaller super ugly number multiplied by one of the primes.",
           "Keep the sequence found so far. For each prime keep a pointer to the earliest sequence element it has not been multiplied with yet; a min-heap of (candidate, prime, pointer) gives the next value. The same value can arise from different primes, so only append it when it is new."],
    editorial=["Let <code>ugly</code> be the sorted list produced so far, starting with [1]. The next value is the minimum over primes p of <code>p * ugly[ptr[p]]</code>, where <code>ptr[p]</code> is the first index whose product with p is not yet in the list. This is a merge of len(primes) sorted streams <code>p * ugly[0], p * ugly[1], ...</code>.",
               "A min-heap holds one entry per prime: <code>(p * ugly[i], p, i)</code>. Look at the root; if its value is not equal to the last element of <code>ugly</code>, append it (the same value can be reached through different primes, for example 14 = 2 * 7 = 7 * 2). Then advance that prime's pointer by replacing the root with <code>(p * ugly[i+1], p, i+1)</code>. The element <code>ugly[i+1]</code> always exists by then, because the value just handled is at least as large as <code>2 * ugly[i]</code>.",
               "Each of the at most n appended values causes O(1) heap operations for at most n + (number of duplicates) pops, which is at most n * len(primes). Time O(n * m log m), space O(n + m) for m primes."],
    time="O(n m log m)", space="O(n + m)",
    solution='''import heapq


def nthSuperUgly(n, primes):
    ugly = [1]
    h = [(p, p, 0) for p in primes]
    heapq.heapify(h)
    while len(ugly) < n:
        v, p, i = h[0]
        if v != ugly[-1]:
            ugly.append(v)
        heapq.heapreplace(h, (p * ugly[i + 1], p, i + 1))
    return ugly[-1]
''',
    tests=[[10, [2, 7, 13]], [1, [2, 3]], [2, [2]], [5, [2]], [12, [2, 7, 13, 19]], [15, [3, 5, 7]], [30, [2]], [20, [2, 3, 5]],
           [4, [97]], [25, [3, 5, 7, 11]]],
)
p["tests"].append([5000, [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]])
p["tests"].append([5000, [2, 3, 5, 7]])
p["tests"].append([2000, [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71]])
p["tests"].append([400, [97, 89, 83, 79, 73, 71, 67, 61]])
p["tests"].append([250, [2, 3]])
p["tests"].append([900, [43, 47, 53, 59, 61, 67, 71, 73, 79, 83]])

_PR = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97]


def b_ugly(n, primes):
    limit = 2
    while True:
        found = set()
        stack = [1]
        while stack:
            x = stack.pop()
            if x in found:
                continue
            found.add(x)
            for q in primes:
                if x * q <= limit:
                    stack.append(x * q)
        if len(found) >= n:
            return sorted(found)[n - 1]
        limit *= 2


def g_ugly(r):
    if r.random() < 0.15:
        return [r.randint(1, 10), [r.choice([2, 3, 5, 7])]]
    return [r.randint(1, 16), r.sample([2, 3, 5, 7, 11], r.randint(2, 4))]


def v_ugly(tests):
    for t in tests:
        n, primes = t["args"]
        assert 1 <= n <= 5000 and 1 <= len(primes) <= 20 and len(set(primes)) == len(primes)
        assert all(q in _PR for q in primes)


CHECKS["super-ugly-number-heap"] = (b_ugly, g_ugly, "exact")
VALIDATE["super-ugly-number-heap"] = v_ugly

# ---------------------------------------------------------------- single-threaded cpu order
p = add(
    id="single-threaded-cpu-order", title="Single-Threaded CPU Order", diff="Medium", topic="Heap",
    fn="cpuOrder", params=[("tasks", "int[][]")], ret="int[]", cmp="exact",
    desc="<p>A single CPU runs tasks one at a time. Task <code>i</code> is given as <code>tasks[i] = [enqueue, duration]</code>: it becomes available at time <code>enqueue</code> and, once started, occupies the CPU for <code>duration</code> time units without interruption.</p><p>The CPU follows these rules:</p><ul><li>If it is idle and no task is available, it waits until the next task becomes available.</li><li>If it is idle and some tasks are available, it starts the one with the smallest duration; ties go to the smaller index.</li><li>When a task finishes, the CPU immediately looks for the next one (a task enqueued at exactly that moment is already available).</li></ul><p>The CPU starts at time <code>0</code>. Return the indices of the tasks in the order they are started.</p><pre>tasks = [[1, 4], [2, 2], [3, 1], [8, 1]]\nt=1 start task 0 (ends at 5); at t=5 available: 1 (dur 2), 2 (dur 1) -> task 2\nt=6 start task 1 (ends at 8); t=8 start task 3\nanswer = [0, 2, 1, 3]</pre>",
    constraints=["1 &le; tasks.length &le; 10,000", "1 &le; enqueue, duration &le; 10<sup>9</sup>"],
    hints=["Simulate the CPU in time order. Which tasks are available at a given moment depends only on the enqueue times.",
           "Sort task indices by enqueue time so that new tasks become available through a single moving pointer.",
           "Maintain a min-heap of (duration, index) for available tasks. When the heap is empty, jump the clock forward to the next enqueue time; otherwise push every task with enqueue &le; clock, then pop the best one and advance the clock by its duration."],
    editorial=["The order is fully determined by a simulation, so the challenge is doing it efficiently. Sort task indices by enqueue time. Keep a clock <code>t</code>, a pointer into the sorted list and a min-heap ordered by <code>(duration, index)</code>, which encodes both the shortest-job rule and the tie-break.",
               "Loop until every task is started: if the heap is empty, move the clock to the enqueue time of the next unqueued task. Push all tasks whose enqueue time is at most the clock. Pop the smallest, record its index, and add its duration to the clock.",
               "Each task is pushed and popped once after an initial sort, so the cost is O(n log n). In languages with fixed-width integers keep the clock in 64 bits, since it can reach about 10<sup>13</sup>."],
    time="O(n log n)", space="O(n)",
    solution='''import heapq


def cpuOrder(tasks):
    n = len(tasks)
    order = sorted(range(n), key=lambda i: (tasks[i][0], i))
    h = []
    t = 0
    p = 0
    out = []
    while len(out) < n:
        if not h and t < tasks[order[p]][0]:
            t = tasks[order[p]][0]
        while p < n and tasks[order[p]][0] <= t:
            heapq.heappush(h, (tasks[order[p]][1], order[p]))
            p += 1
        d, i = heapq.heappop(h)
        t += d
        out.append(i)
    return out
''',
    tests=[[[[1, 4], [2, 2], [3, 1], [8, 1]]], [[[5, 3]]], [[[1, 1], [1, 1], [1, 1]]], [[[1, 5], [1, 2], [1, 3]]],
           [[[10, 1], [1, 1]]], [[[1, 10], [2, 1], [3, 1], [4, 1]]], [[[1, 2], [3, 1]]], [[[1, 2], [2, 1]]],
           [[[7, 10], [7, 12], [7, 5], [7, 4], [7, 2]]], [[[1, 1], [5, 1], [9, 1], [13, 1]]], [[[B, B], [1, B], [2, 1]]]],
)
_r = rnd(8111)
p["tests"].append([[[_r.randint(1, 10 ** 6), _r.randint(1, 1000)] for _ in range(10000)]])
p["tests"].append([[[_r.randint(1, 10 ** 9), _r.randint(1, 10 ** 9)] for _ in range(10000)]])
p["tests"].append([[[_r.randint(1, 100), _r.randint(1, 10)] for _ in range(10000)]])
p["tests"].append([[[i + 1, 10000 - i] for i in range(10000)]])
p["tests"].append([[[1, _r.randint(1, 5)] for _ in range(10000)]])


def b_cpu(tasks):
    n = len(tasks)
    done = [False] * n
    t = 0
    out = []
    for _ in range(n):
        avail = [i for i in range(n) if not done[i] and tasks[i][0] <= t]
        if not avail:
            t = min(tasks[i][0] for i in range(n) if not done[i])
            avail = [i for i in range(n) if not done[i] and tasks[i][0] <= t]
        best = min(avail, key=lambda i: (tasks[i][1], i))
        done[best] = True
        t += tasks[best][1]
        out.append(best)
    return out


def g_cpu(r):
    return [[[r.randint(1, 15), r.randint(1, 6)] for _ in range(r.randint(1, 9))]]


def v_cpu(tests):
    for t in tests:
        ts = t["args"][0]
        assert 1 <= len(ts) <= 10000
        assert all(len(x) == 2 and 1 <= x[0] <= B and 1 <= x[1] <= B for x in ts)
        assert sorted(t["expected"]) == list(range(len(ts)))


CHECKS["single-threaded-cpu-order"] = (b_cpu, g_cpu, "exact")
VALIDATE["single-threaded-cpu-order"] = v_cpu


# ================================================================ HARD

# ---------------------------------------------------------------- running medians doubled
p = add(
    id="running-medians-doubled", title="Running Median of a Stream", diff="Hard", topic="Heap",
    fn="runningMediansDoubled", params=[("nums", "int[]")], ret="int[]", cmp="exact",
    desc="<p>Numbers arrive one at a time in the order of <code>nums</code>. After each arrival, compute the median of all numbers received so far. The median of an odd count is the middle value of the sorted numbers; the median of an even count is the average of the two middle values.</p><p>To keep every answer an integer, report <strong>twice</strong> the median: for an odd count that is <code>2 * middle</code>, for an even count it is the sum of the two middle values. Return the reports for every prefix.</p><pre>nums = [5, 2, 8, 1]\n[5]        -> median 5   -> 10\n[2, 5]     -> median 3.5 -> 7\n[2, 5, 8]  -> median 5   -> 10\n[1,2,5,8]  -> median 3.5 -> 7\nanswer = [10, 7, 10, 7]</pre>",
    constraints=["1 &le; nums.length &le; 10,000", "-10<sup>9</sup> &le; nums[i] &le; 10<sup>9</sup>", "Each reported value fits in a 32-bit signed integer"],
    hints=["Re-sorting every prefix costs O(n<sup>2</sup> log n); inserting into a sorted list is still O(n) per step. You only need the middle.",
           "Split the numbers seen so far into a lower half and an upper half. The median lives at the boundary between them.",
           "Keep a max-heap for the lower half and a min-heap for the upper half, with sizes differing by at most one (lower half gets the extra). Insert into the correct side, then rebalance by moving one root across."],
    editorial=["Maintain two heaps: <code>lo</code> is a max-heap (stored as negated values in a min-heap library) holding the smaller half, and <code>hi</code> is a min-heap holding the larger half. Invariant: every value in <code>lo</code> is &le; every value in <code>hi</code>, and <code>len(lo)</code> is either <code>len(hi)</code> or <code>len(hi) + 1</code>.",
               "For a new value x: if <code>lo</code> is empty or x &le; max(lo), push into <code>lo</code>, else into <code>hi</code>. Then rebalance: if <code>lo</code> has two more elements than <code>hi</code>, move the root of <code>lo</code> to <code>hi</code>; if <code>hi</code> has more than <code>lo</code>, move the root of <code>hi</code> to <code>lo</code>.",
               "With an odd count the median is the root of <code>lo</code> (report twice it); with an even count it is the average of the two roots, so the doubled report is just their sum. Each step is O(log n), and the roots give the middle in O(1). The doubled median is at most 2 * 10<sup>9</sup> in absolute value, which still fits in a signed 32-bit integer."],
    time="O(n log n)", space="O(n)",
    solution='''import heapq


def runningMediansDoubled(nums):
    lo = []  # max-heap of the smaller half, stored negated
    hi = []  # min-heap of the larger half
    out = []
    for x in nums:
        if not lo or x <= -lo[0]:
            heapq.heappush(lo, -x)
        else:
            heapq.heappush(hi, x)
        if len(lo) > len(hi) + 1:
            heapq.heappush(hi, -heapq.heappop(lo))
        elif len(hi) > len(lo):
            heapq.heappush(lo, -heapq.heappop(hi))
        if len(lo) > len(hi):
            out.append(-2 * lo[0])
        else:
            out.append(-lo[0] + hi[0])
    return out
''',
    tests=[[[5, 2, 8, 1]], [[7]], [[1, 1]], [[1, 2]], [[2, 1]], [[3, 3, 3, 3]], [[1, 2, 3, 4, 5, 6]], [[6, 5, 4, 3, 2, 1]],
           [[-1, -2, -3, -4]], [[B, -B, B, -B]], [[B, B, B]], [[-B, -B]], [[0, 0, 5, -5, 0]]],
)
_r = rnd(8109)
p["tests"].append([[_r.randint(-B, B) for _ in range(10000)]])
p["tests"].append([[_r.randint(-10, 10) for _ in range(10000)]])
p["tests"].append([list(range(10000))])
p["tests"].append([list(range(10000, 0, -1))])
p["tests"].append([[B if i % 2 else -B for i in range(10000)]])
p["tests"].append([[(i * 7919) % 10007 - 5000 for i in range(10000)]])


def b_median(nums):
    out = []
    for i in range(len(nums)):
        s = sorted(nums[:i + 1])
        m = len(s)
        out.append(2 * s[m // 2] if m % 2 else s[m // 2 - 1] + s[m // 2])
    return out


def v_median(tests):
    for t in tests:
        nums = t["args"][0]
        assert 1 <= len(nums) <= 10000 and all(-B <= x <= B for x in nums)


CHECKS["running-medians-doubled"] = (b_median, lambda r: [[r.randint(-9, 9) for _ in range(r.randint(1, 14))]], "exact")
VALIDATE["running-medians-doubled"] = v_median

# ---------------------------------------------------------------- maximum team performance
p = add(
    id="maximum-team-performance-heap", title="Maximum Team Performance", diff="Hard", topic="Heap",
    fn="maxPerformance", params=[("speed", "int[]"), ("efficiency", "int[]"), ("k", "int")], ret="int", cmp="exact",
    desc="<p>A company has <code>n</code> engineers. Engineer <code>i</code> has speed <code>speed[i]</code> and efficiency <code>efficiency[i]</code>. You will form a team of <strong>at most</strong> <code>k</code> engineers (at least one).</p><p>The performance of a team is <em>(sum of the speeds of its members) multiplied by (the minimum efficiency among its members)</em>. Return the maximum possible performance.</p><pre>speed      = [2, 10, 3, 1, 5, 8]\nefficiency = [5,  4, 3, 9, 7, 2]\nk = 2\nbest team: engineer 1 (10, 4) and engineer 4 (5, 7)\nperformance = (10 + 5) * min(4, 7) = 60</pre>",
    constraints=["1 &le; n = speed.length = efficiency.length &le; 2,000", "1 &le; k &le; n", "1 &le; speed[i], efficiency[i] &le; 1,000", "The answer fits in a 32-bit signed integer"],
    hints=["Two quantities interact: a sum that wants big values and a minimum that wants all members to be good. Fix one of them.",
           "Suppose you fix the engineer whose efficiency is the team minimum. Then everybody on the team must have efficiency at least as large, and among those you want the fastest ones.",
           "Sort engineers by efficiency descending and sweep. Keep the speeds of the members so far in a min-heap capped at k entries and their running sum; when the heap exceeds k, drop the slowest. At each engineer, candidate = sum * that engineer's efficiency."],
    editorial=["Sweep the engineers from highest efficiency to lowest. When the sweep is at engineer e, every engineer already processed has efficiency at least that of e, so if e is included, the team minimum is exactly <code>efficiency[e]</code> (or higher if e ends up dropped, which is fine because we only ever underestimate and the true best is reached when the real minimum member is processed).",
               "For the current minimum efficiency, the best team consists of the (at most) k fastest engineers among those processed. A min-heap on speed holds the current top-k speeds, and a running sum tracks their total. Push the new speed; if the heap has more than k entries, pop the slowest and subtract it from the sum. Then evaluate <code>sum * efficiency[e]</code> and keep the maximum.",
               "If the engineer just pushed is immediately dropped as the slowest, the value computed is the sum of the top k speeds times a smaller efficiency than the true minimum of that team, so it is a valid lower bound for a real team. The true value of that team was already evaluated earlier in the sweep, so the maximum is unaffected. Total cost is O(n log n)."],
    time="O(n log n)", space="O(n)",
    solution='''import heapq


def maxPerformance(speed, efficiency, k):
    order = sorted(range(len(speed)), key=lambda i: -efficiency[i])
    h = []
    total = 0
    best = 0
    for i in order:
        heapq.heappush(h, speed[i])
        total += speed[i]
        if len(h) > k:
            total -= heapq.heappop(h)
        best = max(best, total * efficiency[i])
    return best
''',
    tests=[[[2, 10, 3, 1, 5, 8], [5, 4, 3, 9, 7, 2], 2], [[2, 10, 3, 1, 5, 8], [5, 4, 3, 9, 7, 2], 3],
           [[2, 10, 3, 1, 5, 8], [5, 4, 3, 9, 7, 2], 6], [[2, 10, 3, 1, 5, 8], [5, 4, 3, 9, 7, 2], 1], [[5], [7], 1],
           [[1, 1], [1, 1], 2], [[1, 1], [1, 1], 1], [[10, 1], [1, 10], 2], [[10, 1], [1, 10], 1], [[3, 3, 3], [4, 4, 4], 2],
           [[1000, 1000], [1000, 1000], 2], [[4, 6, 2, 9], [9, 2, 6, 4], 3], [[1, 2, 3, 4, 5], [5, 4, 3, 2, 1], 5]],
)
_r = rnd(8110)
p["tests"].append([[1000] * 2000, [1000] * 2000, 2000])
p["tests"].append([[_r.randint(1, 1000) for _ in range(2000)], [_r.randint(1, 1000) for _ in range(2000)], 1000])
p["tests"].append([[_r.randint(1, 1000) for _ in range(2000)], [_r.randint(1, 1000) for _ in range(2000)], 7])
p["tests"].append([[_r.randint(1, 1000) for _ in range(2000)], [_r.randint(1, 1000) for _ in range(2000)], 2000])
p["tests"].append([list(range(1, 1001)) * 2, list(range(1000, 0, -1)) * 2, 300])
p["tests"].append([list(range(1, 1001)) * 2, list(range(1, 1001)) * 2, 300])


def b_perf(speed, efficiency, k):
    n = len(speed)
    best = 0
    for size in range(1, k + 1):
        for team in combinations(range(n), size):
            s = sum(speed[i] for i in team)
            m = min(efficiency[i] for i in team)
            best = max(best, s * m)
    return best


def g_perf(r):
    n = r.randint(1, 8)
    return [[r.randint(1, 12) for _ in range(n)], [r.randint(1, 12) for _ in range(n)], r.randint(1, n)]


def v_perf(tests):
    for t in tests:
        s, e, k = t["args"]
        assert len(s) == len(e) and 1 <= len(s) <= 2000 and 1 <= k <= len(s)
        assert all(1 <= x <= 1000 for x in s + e)


CHECKS["maximum-team-performance-heap"] = (b_perf, g_perf, "exact")
VALIDATE["maximum-team-performance-heap"] = v_perf
