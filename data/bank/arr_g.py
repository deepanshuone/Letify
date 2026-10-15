"""Problems: arrays & hashing, sorting-based array problems. See data/lib.py for the registry."""
from lib import add, rnd, CHECKS, VALIDATE, gen_arr  # noqa: F401

INT_MIN, INT_MAX = -(2 ** 31), 2 ** 31 - 1
T = "Arrays & Hashing"

# ---------------------------------------------------------------- EASY

p = add(
    id="merge-id-value-pairs-by-sum", title="Merge Id-Value Pairs by Sum", diff="Easy", topic=T,
    fn="mergePairs", params=[("a", "int[][]"), ("b", "int[][]")], ret="int[][]", cmp="exact",
    desc="<p>Two tables are given as 2-D arrays. Each row is a pair <code>[id, value]</code>. Inside one table the ids are strictly increasing, so no id repeats within a table.</p><p>Merge the tables into one table that contains every id that occurs in at least one of them, sorted by id ascending. The value of an id is the sum of its values from the tables that contain it (a table that lacks the id contributes nothing).</p><p>For example, <code>a = [[1,4],[3,2],[7,5]]</code> and <code>b = [[3,6],[4,1]]</code> give <code>[[1,4],[3,8],[4,1],[7,5]]</code>.</p>",
    constraints=["1 &le; a.length, b.length &le; 1,000", "Each row has exactly 2 numbers: 1 &le; id &le; 1,000,000 and 1 &le; value &le; 1,000,000", "Ids are strictly increasing inside a and inside b"],
    hints=["Because both tables are already sorted by id you do not need a full sort.",
           "Walk through both tables with one index each, like the merge step of merge sort.",
           "Compare the ids under the two indices. The smaller id is copied out; if they are equal, output the id once with the summed value and advance both indices."],
    editorial=["Use two pointers <code>i</code> and <code>j</code>. If <code>a[i].id &lt; b[j].id</code>, append <code>a[i]</code> and advance <code>i</code>; if it is larger, append <code>b[j]</code> and advance <code>j</code>; if the ids are equal, append <code>[id, a[i].value + b[j].value]</code> and advance both. When one table is exhausted, append the remainder of the other.",
               "Time is O(n + m) because every row is looked at once. The alternative of putting everything into a dictionary and sorting the keys is O(n log n) and ignores the sortedness that the statement offers."],
    time="O(n + m)", space="O(n + m)",
    solution='''def mergePairs(a, b):
    i = j = 0
    out = []
    while i < len(a) and j < len(b):
        if a[i][0] < b[j][0]:
            out.append([a[i][0], a[i][1]])
            i += 1
        elif a[i][0] > b[j][0]:
            out.append([b[j][0], b[j][1]])
            j += 1
        else:
            out.append([a[i][0], a[i][1] + b[j][1]])
            i += 1
            j += 1
    while i < len(a):
        out.append([a[i][0], a[i][1]])
        i += 1
    while j < len(b):
        out.append([b[j][0], b[j][1]])
        j += 1
    return out
''',
    tests=[[[[1, 4], [3, 2], [7, 5]], [[3, 6], [4, 1]]], [[[2, 3]], [[2, 4]]], [[[1, 1]], [[2, 2]]], [[[5, 5]], [[1, 1], [2, 2], [3, 3]]],
           [[[1, 1], [2, 2], [3, 3]], [[1, 10], [2, 20], [3, 30]]], [[[1000000, 1000000]], [[1000000, 1000000]]],
           [[[1, 1], [10, 10]], [[5, 5]]], [[[1, 7], [2, 7], [3, 7]], [[10, 1]]]],
)
_r = rnd(7102)


def _mk_table(r, n, idhi):
    ids = sorted(r.sample(range(1, idhi + 1), n))
    return [[i, r.randint(1, 1000000)] for i in ids]


p["tests"].append([_mk_table(_r, 1000, 1500), _mk_table(_r, 1000, 1500)])
p["tests"].append([_mk_table(_r, 600, 1000000), _mk_table(_r, 300, 1000000)])


def b_mergepairs(a, b):
    d = {}
    for i, v in a:
        d[i] = d.get(i, 0) + v
    for i, v in b:
        d[i] = d.get(i, 0) + v
    return [[k, d[k]] for k in sorted(d)]


def g_mergepairs(r):
    def tab():
        ids = sorted(r.sample(range(1, 12), r.randint(1, 6)))
        return [[i, r.randint(1, 9)] for i in ids]
    return [tab(), tab()]


def v_mergepairs(tests):
    for t in tests:
        for tab in t["args"]:
            assert 1 <= len(tab) <= 1000
            assert all(len(row) == 2 and 1 <= row[0] <= 10 ** 6 and 1 <= row[1] <= 10 ** 6 for row in tab)
            assert all(tab[k][0] < tab[k + 1][0] for k in range(len(tab) - 1))


CHECKS["merge-id-value-pairs-by-sum"] = (b_mergepairs, g_mergepairs, "exact")
VALIDATE["merge-id-value-pairs-by-sum"] = v_mergepairs

p = add(
    id="largest-perimeter-triangle", title="Largest Perimeter Triangle", diff="Easy", topic=T, tier="extra",
    fn="largestPerimeter", params=[("sides", "int[]")], ret="int", cmp="exact",
    desc="<p>You have sticks with the lengths in <code>sides</code>. Choose any three different sticks that form a triangle of positive area and return the largest perimeter you can get. If no three sticks form such a triangle, return <code>0</code>.</p><p>Three lengths <code>x &le; y &le; z</code> form a triangle of positive area exactly when <code>x + y &gt; z</code>.</p><p>For example, <code>[3, 6, 2, 3]</code> gives <code>8</code> (sticks 3, 3, 2), because 6 is too long to pair with any two others.</p>",
    constraints=["3 &le; sides.length &le; 5,000", "1 &le; sides[i] &le; 100,000,000"],
    hints=["Only the three longest sticks of a good triple matter for its perimeter, so look at big sticks first.",
           "Sort in descending order. For a fixed longest stick, the best partners are the next two largest ones.",
           "Check consecutive triples <code>(s[i], s[i+1], s[i+2])</code> in the sorted order; the first one with <code>s[i+1] + s[i+2] &gt; s[i]</code> is the answer."],
    editorial=["Sort the lengths in descending order. Suppose the longest stick of an optimal triangle is <code>s[i]</code>. The two partners that maximize the perimeter and are most likely to satisfy the inequality are <code>s[i+1]</code> and <code>s[i+2]</code>, the biggest sticks still available. If even they fail (<code>s[i+1] + s[i+2] &le; s[i]</code>), no pair works with <code>s[i]</code> as the longest side, so <code>s[i]</code> can be discarded.",
               "The first index where the consecutive triple works gives the largest possible perimeter, since every triple examined before it was impossible and later ones have smaller sticks. If no index works, return 0. Sorting dominates: O(n log n) time. The failing chain grows like the Fibonacci numbers, so at most about 40 sticks can fail in a row for values below 10<sup>8</sup>."],
    time="O(n log n)", space="O(1) extra",
    solution='''def largestPerimeter(sides):
    s = sorted(sides, reverse=True)
    for i in range(len(s) - 2):
        if s[i + 1] + s[i + 2] > s[i]:
            return s[i] + s[i + 1] + s[i + 2]
    return 0
''',
    tests=[[[2, 1, 2]], [[1, 2, 8]], [[3, 6, 2, 3]], [[1, 1, 1]], [[5, 5, 5, 5]], [[1, 2, 4, 8, 16]], [[1, 1, 2, 3, 5, 8, 13]],
           [[100000000, 100000000, 100000000]], [[10, 3, 4, 20, 5, 6]], [[7, 4, 3]]],
)
_r = rnd(7103)
_f = [1, 1]
while _f[-1] + _f[-2] <= 100000000:
    _f.append(_f[-1] + _f[-2])
_a = _f + [1] * 3000 + [_f[0]]  # many ones: only 1,1,1 forms nothing bigger than a tiny triangle
_r.shuffle(_a)
p["tests"].append([_a])
_a = [2 ** k for k in range(27)] * 100  # 2700 sticks, equal copies make triangles of size 2^k each
_r.shuffle(_a)
p["tests"].append([_a])
p["tests"].append([[_r.randint(1, 100000000) for _ in range(4000)]])


def b_perim(sides):
    n = len(sides)
    best = 0
    for i in range(n):
        for j in range(i + 1, n):
            for k in range(j + 1, n):
                x, y, z = sorted((sides[i], sides[j], sides[k]))
                if x + y > z:
                    best = max(best, x + y + z)
    return best


CHECKS["largest-perimeter-triangle"] = (b_perim, lambda r: [[r.randint(1, 12) for _ in range(r.randint(3, 8))]], "exact")


def v_perim(tests):
    for t in tests:
        s = t["args"][0]
        assert 3 <= len(s) <= 5000 and all(1 <= x <= 10 ** 8 for x in s)


VALIDATE["largest-perimeter-triangle"] = v_perim

# ---------------------------------------------------------------- MEDIUM

p = add(
    id="kth-largest-element", title="Kth Largest Element", diff="Medium", topic=T, tier="must",
    fn="findKthLargest", params=[("nums", "int[]"), ("k", "int")], ret="int", cmp="exact",
    desc="<p>Given an integer array <code>nums</code> and an integer <code>k</code>, return the <code>k</code>-th largest element <em>in sorted order</em>. Equal values count separately: in <code>[5, 5, 3]</code> the 1st and 2nd largest are both <code>5</code> and the 3rd largest is <code>3</code>.</p><p>For example, <code>nums = [5, 2, 9, 2, 7]</code> with <code>k = 2</code> gives <code>7</code>, and with <code>k = 4</code> gives <code>2</code>.</p><p>Try to beat a full sort: an O(n) average time solution exists.</p>",
    constraints=["1 &le; k &le; nums.length &le; 8,000", "-1,000,000,000 &le; nums[i] &le; 1,000,000,000"],
    hints=["Sorting in descending order and reading position <code>k - 1</code> is a correct baseline.",
           "You only need to know where the answer sits, not the order of everything. Think of the partition step of quicksort.",
           "Pick a pivot, split into larger, equal and smaller groups. If <code>k</code> falls inside the larger group recurse there, if inside the equal group the pivot is the answer, otherwise recurse into the smaller group with a reduced <code>k</code>."],
    editorial=["Quickselect: choose a random pivot and partition the values into three lists - greater than, equal to, and less than the pivot. If <code>k &le; len(greater)</code> the answer is in the greater list; if <code>k &le; len(greater) + len(equal)</code> the answer is the pivot; otherwise subtract those counts from <code>k</code> and continue in the smaller list. The three-way split also keeps the algorithm fast when there are many duplicates.",
               "With random pivots the expected work is n + n/2 + n/4 + ... = O(n), worst case O(n<sup>2</sup>) with astronomically small probability. A min-heap of size <code>k</code> gives O(n log k) and is the natural choice for streams; sorting is O(n log n) and perfectly fine when n is small."],
    time="O(n) average", space="O(n)",
    solution='''import random

def findKthLargest(nums, k):
    a = list(nums)
    while True:
        pivot = a[random.randrange(len(a))]
        greater = [x for x in a if x > pivot]
        equal = [x for x in a if x == pivot]
        if k <= len(greater):
            a = greater
        elif k <= len(greater) + len(equal):
            return pivot
        else:
            k -= len(greater) + len(equal)
            a = [x for x in a if x < pivot]
''',
    tests=[[[5, 2, 9, 2, 7], 2], [[5, 2, 9, 2, 7], 4], [[5, 2, 9, 2, 7], 1], [[5, 2, 9, 2, 7], 5], [[1], 1], [[4, 4, 4], 2],
           [[-1, -5, -3], 2], [[3, 2, 3, 1, 2, 4, 5, 5, 6], 4], [[1000000000, -1000000000], 2], [[7, 7, 8, 8], 3], [[2, 1], 1]],
)
_r = rnd(7105)
_a = [_r.randint(-1000000000, 1000000000) for _ in range(5000)]
p["tests"].append([_a, 1234])
_a = [_r.randint(-20, 20) for _ in range(7000)]
p["tests"].append([_a, 7000])
_a = list(range(4000)); _r.shuffle(_a)
p["tests"].append([_a, 2000])


def b_kth(nums, k):
    a = list(nums)
    for _ in range(k - 1):
        a.remove(max(a))
    return max(a)


def g_kth(r):
    a = [r.randint(-5, 5) for _ in range(r.randint(1, 9))]
    return [a, r.randint(1, len(a))]


def v_kth(tests):
    for t in tests:
        nums, k = t["args"]
        assert 1 <= k <= len(nums) <= 8000 and all(-10 ** 9 <= x <= 10 ** 9 for x in nums)


CHECKS["kth-largest-element"] = (b_kth, g_kth, "exact")
VALIDATE["kth-largest-element"] = v_kth

p = add(
    id="equalize-array-min-unit-moves", title="Equalize Array with Unit Moves", diff="Medium", topic=T,
    fn="minMoves", params=[("nums", "int[]")], ret="int", cmp="exact",
    desc="<p>In one move you may pick one element of <code>nums</code> and increase or decrease it by exactly <code>1</code>. Return the minimum number of moves needed to make all elements equal.</p><p>For example, <code>[1, 2, 3]</code> needs <code>2</code> moves (change 1 to 2 and 3 to 2), and <code>[4, 10, 1, 1]</code> needs <code>12</code>.</p>",
    constraints=["1 &le; nums.length &le; 8,000", "-100,000 &le; nums[i] &le; 100,000"],
    hints=["Each element must travel to a common target <code>t</code>; element <code>x</code> costs <code>|x - t|</code>.",
           "You want to minimize the sum of absolute distances to one point. Moving the target one step to the right helps the elements on the right and hurts those on the left.",
           "The sum of absolute deviations is minimized at the median. Sort the array and sum the distances to <code>nums[n // 2]</code>."],
    editorial=["Let <code>f(t) = sum |x - t|</code>. When <code>t</code> moves one step right, every element to its left gets one step farther and every element to its right gets one step closer. So <code>f</code> decreases as long as more than half of the elements are to the right of <code>t</code>, and it increases once more than half are to the left. The minimum is therefore reached at a median.",
               "Sort the array, take the middle element (either of the two middle ones when n is even, the sum is the same) and add up the absolute differences. Sorting dominates at O(n log n). Quickselect finds the median in O(n) average time. Another way to see the same sum: pair the smallest with the largest element; each pair <code>(lo, hi)</code> costs exactly <code>hi - lo</code> moves regardless of the target between them."],
    time="O(n log n)", space="O(n)",
    solution='''def minMoves(nums):
    a = sorted(nums)
    m = a[len(a) // 2]
    return sum(abs(x - m) for x in a)
''',
    tests=[[[1, 2, 3]], [[4, 10, 1, 1]], [[5]], [[7, 7, 7]], [[1, 100000]], [[-100000, 100000]], [[1, 2, 3, 4]], [[-3, 0, 3]],
           [[0, 0, 0, 100000]], [[9, 1, 5, 3, 7]], [[-5, -5, 5, 5]]],
)
_r = rnd(7106)
p["tests"].append([[_r.randint(-100000, 100000) for _ in range(6000)]])
p["tests"].append([[-100000] * 4000 + [100000] * 4000])
p["tests"].append([[_r.randint(-50, 50) for _ in range(8000)]])


def b_eqmoves(nums):
    return min(sum(abs(x - t) for x in nums) for t in range(min(nums), max(nums) + 1))


CHECKS["equalize-array-min-unit-moves"] = (b_eqmoves, lambda r: [[r.randint(-8, 8) for _ in range(r.randint(1, 9))]], "exact")


def v_eqmoves(tests):
    for t in tests:
        a = t["args"][0]
        assert 1 <= len(a) <= 8000 and all(-100000 <= x <= 100000 for x in a)


VALIDATE["equalize-array-min-unit-moves"] = v_eqmoves

p = add(
    id="k-closest-values-to-target", title="K Closest Values to Target", diff="Medium", topic=T,
    fn="kClosestValues", params=[("nums", "int[]"), ("k", "int"), ("target", "int")], ret="int[]", cmp="exact",
    desc="<p>Given an unsorted integer array <code>nums</code>, an integer <code>k</code> and an integer <code>target</code>, find the <code>k</code> elements of <code>nums</code> that are closest to <code>target</code>, where the distance of <code>x</code> is <code>|x - target|</code>.</p><p>If two elements are equally close, the smaller value is considered closer. Repeated values are separate elements. Return the chosen <code>k</code> values in ascending order.</p><p>For example, <code>nums = [10, 1, 4, 7, 8]</code>, <code>k = 3</code>, <code>target = 6</code> gives <code>[4, 7, 8]</code>. With <code>nums = [1, 5]</code>, <code>k = 1</code>, <code>target = 3</code> both are at distance 2, so the smaller value wins: <code>[1]</code>.</p>",
    constraints=["1 &le; k &le; nums.length &le; 8,000", "-1,000,000,000 &le; nums[i], target &le; 1,000,000,000"],
    hints=["Define a distance for each element and think about ordering the elements by it.",
           "Sort by the key <code>(|x - target|, x)</code>. The tie rule is built into the second component.",
           "Take the first <code>k</code> elements of that order, then sort them by value for the output."],
    editorial=["Sort the elements by the key <code>(abs(x - target), x)</code>. The key is a strict total order on values (equal values are interchangeable), so the first <code>k</code> elements are exactly the <code>k</code> closest, with the smaller-value tie-break applied. Finally sort those <code>k</code> values ascending for the output.",
               "This is O(n log n). With a heap or quickselect on the same key you can reduce it to O(n log k) or O(n) average. If the input were already sorted, binary search for the left edge of the best window of length <code>k</code> would give O(log n + k)."],
    time="O(n log n)", space="O(n)",
    solution='''def kClosestValues(nums, k, target):
    best = sorted(nums, key=lambda x: (abs(x - target), x))[:k]
    return sorted(best)
''',
    tests=[[[10, 1, 4, 7, 8], 3, 6], [[1, 5], 1, 3], [[5], 1, 100], [[1, 2, 3, 4, 5], 4, 3], [[1, 2, 3, 4, 5], 5, -10],
           [[4, 4, 4, 1], 2, 4], [[-5, -1, 0, 2, 9], 2, -3], [[1000000000, -1000000000, 0], 1, 1000000000],
           [[3, 3, 5, 5], 3, 4], [[8, 2, 6, 4], 2, 5], [[1, 10], 2, 5]],
)
_r = rnd(7107)
p["tests"].append([[_r.randint(-1000000000, 1000000000) for _ in range(5000)], 700, 123456789])
p["tests"].append([[_r.randint(-30, 30) for _ in range(7000)], 3333, 4])
p["tests"].append([[_r.randint(-1000000, 1000000) for _ in range(4000)], 4000, -1000000000])


def b_kcv(nums, k, target):
    pool = list(nums)
    out = []
    for _ in range(k):
        bi = 0
        for i in range(1, len(pool)):
            di, db = abs(pool[i] - target), abs(pool[bi] - target)
            if di < db or (di == db and pool[i] < pool[bi]):
                bi = i
        out.append(pool.pop(bi))
    return sorted(out)


def g_kcv(r):
    a = [r.randint(-6, 6) for _ in range(r.randint(1, 9))]
    return [a, r.randint(1, len(a)), r.randint(-8, 8)]


def v_kcv(tests):
    for t in tests:
        nums, k, target = t["args"]
        assert 1 <= k <= len(nums) <= 8000
        assert all(-10 ** 9 <= x <= 10 ** 9 for x in nums) and -10 ** 9 <= target <= 10 ** 9
        assert len(t["expected"]) == k


CHECKS["k-closest-values-to-target"] = (b_kcv, g_kcv, "exact")
VALIDATE["k-closest-values-to-target"] = v_kcv

p = add(
    id="sort-jumbled-numbers", title="Sort Jumbled Numbers", diff="Medium", topic=T, tier="extra",
    fn="sortJumbled", params=[("mapping", "int[]"), ("nums", "int[]")], ret="int[]", cmp="exact",
    desc="<p>A broken display shows decimal digits incorrectly: digit <code>d</code> is shown as <code>mapping[d]</code> (so <code>mapping</code> has exactly 10 entries, each between 0 and 9). The <em>mapped value</em> of a non-negative integer is the number you get after replacing each of its digits by the shown digit and reading the result as an ordinary integer, so leading zeros vanish. The number <code>0</code> is a single digit <code>0</code>.</p><p>Return <code>nums</code> sorted by mapped value in ascending order. Numbers with the same mapped value keep their original relative order. The output contains the <em>original</em> numbers, not the mapped ones.</p><p>For example, with <code>mapping = [2, 0, 1, 3, 4, 5, 6, 7, 8, 9]</code> the numbers <code>10, 1, 0, 21, 12</code> are shown as <code>2, 0, 2, 10, 1</code>, so the answer is <code>[1, 12, 10, 0, 21]</code> (10 comes before 0 because both map to 2 and 10 occurs first).</p>",
    constraints=["mapping.length = 10 and 0 &le; mapping[d] &le; 9 (mapping need not be a permutation)", "1 &le; nums.length &le; 5,000", "0 &le; nums[i] &le; 1,000,000,000"],
    hints=["Compute the mapped value of each number first, then sort by it.",
           "To compute the mapped value, process the digits from most significant to least: <code>value = value * 10 + mapping[digit]</code>. Leading zeros take care of themselves.",
           "Use a stable sort with the mapped value as the key (Python's <code>sorted</code> is stable), or sort the pairs <code>(mapped, original index)</code>."],
    editorial=["Convert each number to its mapped value by reading its decimal digits left to right and accumulating <code>v = v * 10 + mapping[d]</code>. Remember that <code>0</code> itself has one digit and maps to <code>mapping[0]</code>. Using the integer accumulation instead of building strings also handles leading zeros correctly.",
               "Then sort the numbers by mapped value. Stability gives the required tie-break; if your language has an unstable sort, add the original index to the key. Computing all mapped values costs O(n * D) with D at most 10 digits and the sort costs O(n log n)."],
    time="O(n log n + n * D)", space="O(n)",
    solution='''def sortJumbled(mapping, nums):
    def mapped(x):
        if x == 0:
            return mapping[0]
        digits = []
        while x:
            digits.append(x % 10)
            x //= 10
        v = 0
        for d in reversed(digits):
            v = v * 10 + mapping[d]
        return v
    return sorted(nums, key=mapped)
''',
    tests=[[[2, 0, 1, 3, 4, 5, 6, 7, 8, 9], [10, 1, 0, 21, 12]], [[0, 1, 2, 3, 4, 5, 6, 7, 8, 9], [5, 3, 100, 42]],
           [[9, 8, 7, 6, 5, 4, 3, 2, 1, 0], [0, 1, 9, 10, 99]], [[8, 9, 4, 0, 2, 1, 3, 5, 7, 6], [991, 338, 38]],
           [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [7, 3, 100, 0]], [[1, 1, 1, 1, 1, 1, 1, 1, 1, 1], [20, 3, 111, 9]],
           [[5, 4, 3, 2, 1, 0, 9, 8, 7, 6], [1000000000]], [[3, 0, 1, 2, 4, 5, 6, 7, 8, 9], [10, 3, 30, 1, 0]],
           [[2, 3, 4, 5, 6, 7, 8, 9, 0, 1], [8, 9, 18, 98, 10]]],
)
_r = rnd(7108)
_m = list(range(10)); _r.shuffle(_m)
p["tests"].append([_m, [_r.randint(0, 1000000000) for _ in range(4000)]])
p["tests"].append([[_r.randint(0, 3) for _ in range(10)], [_r.randint(0, 99999) for _ in range(5000)]])


def b_jumbled(mapping, nums):
    items = [(str(x), x) for x in nums]
    def key(s):
        t = "".join(str(mapping[int(ch)]) for ch in s)
        return int(t)
    out = list(items)
    for i in range(1, len(out)):  # insertion sort: stable by construction
        cur = out[i]
        j = i - 1
        while j >= 0 and key(out[j][0]) > key(cur[0]):
            out[j + 1] = out[j]
            j -= 1
        out[j + 1] = cur
    return [x for _, x in out]


def g_jumbled(r):
    return [[r.randint(0, 9) if r.random() < 0.5 else r.randint(0, 3) for _ in range(10)], [r.randint(0, 150) for _ in range(r.randint(1, 9))]]


def v_jumbled(tests):
    for t in tests:
        m, nums = t["args"]
        assert len(m) == 10 and all(0 <= x <= 9 for x in m)
        assert 1 <= len(nums) <= 5000 and all(0 <= x <= 10 ** 9 for x in nums)


CHECKS["sort-jumbled-numbers"] = (b_jumbled, g_jumbled, "exact")
VALIDATE["sort-jumbled-numbers"] = v_jumbled

# ---------------------------------------------------------------- HARD

p = add(
    id="weighted-equalize-array-min-cost", title="Weighted Equalize Array Minimum Cost", diff="Hard", topic=T,
    fn="minCostEqualize", params=[("nums", "int[]"), ("cost", "int[]")], ret="int", cmp="exact",
    desc="<p>You are given two arrays of the same length. <code>nums[i]</code> is a number you may change, and <code>cost[i]</code> is the price of changing it by exactly 1 (up or down). Changing <code>nums[i]</code> by <code>d</code> units costs <code>d * cost[i]</code> for that element.</p><p>Make all elements of <code>nums</code> equal and return the minimum total cost.</p><p>For example, <code>nums = [2, 6, 4]</code> with <code>cost = [1, 1, 5]</code> gives <code>4</code>: make everything equal to 4 by changing 2 up by 2 (cost 2) and 6 down by 2 (cost 2). And <code>nums = [1, 10]</code> with <code>cost = [3, 1]</code> gives <code>9</code>: change the cheap element 10 to 1.</p>",
    constraints=["1 &le; nums.length = cost.length &le; 5,000", "1 &le; nums[i] &le; 1,000", "1 &le; cost[i] &le; 100"],
    hints=["For a fixed target <code>t</code> the total cost is <code>sum cost[i] * |nums[i] - t|</code>. Only the target matters now.",
           "This function of <code>t</code> is convex and piecewise linear, with breakpoints at the values of <code>nums</code>. So an optimal <code>t</code> can always be chosen among the values in <code>nums</code>.",
           "It behaves like the median where element <code>i</code> counts <code>cost[i]</code> times. Sort by value and walk until the cumulative weight reaches at least half of the total weight; that value is an optimal target."],
    editorial=["If every cost were 1 the optimum would be the median. With weights, imagine each element repeated <code>cost[i]</code> times; then the weighted median of the multiset is optimal. Moving the target right by one unit changes the cost by (weight of elements left of or at the target) minus (weight of elements right of it), so the cost stops decreasing when the left weight reaches half of the total.",
               "Sort the pairs by <code>nums</code>, accumulate weights until the prefix sum is at least <code>(total + 1) // 2</code>, and take that value as the target. Then sum <code>cost[i] * |nums[i] - target|</code>. Sorting makes it O(n log n). The result is at most about 5,000 * 100 * 500 = 2.5 * 10<sup>8</sup>, safely inside 32-bit integers."],
    time="O(n log n)", space="O(n)",
    solution='''def minCostEqualize(nums, cost):
    pairs = sorted(zip(nums, cost))
    total = sum(cost)
    acc = 0
    target = pairs[-1][0]
    for v, w in pairs:
        acc += w
        if acc * 2 >= total:
            target = v
            break
    return sum(w * abs(v - target) for v, w in pairs)
''',
    tests=[[[2, 6, 4], [1, 1, 5]], [[1, 10], [3, 1]], [[5], [7]], [[1, 3, 5, 2], [2, 3, 1, 14]], [[4, 4, 4], [1, 2, 3]],
           [[1, 1000], [100, 100]], [[1, 1000], [1, 100]], [[1, 2, 3, 4, 5], [1, 1, 1, 1, 1]], [[10, 20, 30], [1, 1, 100]],
           [[7, 3, 9], [5, 5, 5]], [[1, 1000, 500], [100, 100, 1]]],
)
_r = rnd(7110)
p["tests"].append([[_r.randint(1, 1000) for _ in range(5000)], [_r.randint(1, 100) for _ in range(5000)]])
p["tests"].append([[1] * 2500 + [1000] * 2500, [_r.randint(1, 100) for _ in range(5000)]])
p["tests"].append([[_r.randint(1, 1000) for _ in range(3000)], [100] * 1500 + [1] * 1500])


def b_wcost(nums, cost):
    return min(sum(w * abs(v - t) for v, w in zip(nums, cost)) for t in range(min(nums), max(nums) + 1))


def g_wcost(r):
    n = r.randint(1, 7)
    return [[r.randint(1, 15) for _ in range(n)], [r.randint(1, 6) for _ in range(n)]]


def v_wcost(tests):
    for t in tests:
        nums, cost = t["args"]
        assert 1 <= len(nums) == len(cost) <= 5000
        assert all(1 <= x <= 1000 for x in nums) and all(1 <= x <= 100 for x in cost)


CHECKS["weighted-equalize-array-min-cost"] = (b_wcost, g_wcost, "exact")
VALIDATE["weighted-equalize-array-min-cost"] = v_wcost


# ---------------------------------------------------------------- replacements / additions

p = add(
    id="minimum-absolute-difference-pairs", title="Minimum Absolute Difference Pairs", diff="Easy", topic=T,
    fn="minDiffPairs", params=[("nums", "int[]")], ret="int[][]", cmp="exact",
    desc="<p>Given an array <code>nums</code> of pairwise distinct integers, find the smallest absolute difference between any two of its elements. Return <em>all</em> pairs <code>[a, b]</code> of elements with <code>a &lt; b</code> and <code>b - a</code> equal to that smallest difference.</p><p>List the pairs in ascending order (by <code>a</code>; since values are distinct, every <code>a</code> occurs in at most one pair).</p><p>For example, <code>[4, 2, 1, 3]</code> gives <code>[[1, 2], [2, 3], [3, 4]]</code>, and <code>[10, 1, 5, 12]</code> gives <code>[[10, 12]]</code>.</p>",
    constraints=["2 &le; nums.length &le; 5,000", "-1,000,000 &le; nums[i] &le; 1,000,000", "All values are distinct"],
    hints=["Comparing all pairs works for tiny inputs but is O(n<sup>2</sup>) overall.",
           "Which two elements can be at the minimum distance? Think about where such a pair sits once the numbers are in order.",
           "Sort the array. The closest pairs are always neighbours in sorted order, so scan adjacent differences twice: once for the minimum, once to collect the pairs."],
    editorial=["If two elements <code>x &lt; y</code> had another element <code>z</code> strictly between them, then <code>(x, z)</code> would be closer than <code>(x, y)</code>. So a minimum-difference pair is always adjacent in the sorted array. Sort, compute the minimum of <code>s[i+1] - s[i]</code>, and then output every adjacent pair whose difference equals it.",
               "Sorting costs O(n log n) and the two scans cost O(n). The output is already in ascending order because it is produced from the sorted array."],
    time="O(n log n)", space="O(n)",
    solution='''def minDiffPairs(nums):
    s = sorted(nums)
    best = min(s[i + 1] - s[i] for i in range(len(s) - 1))
    return [[s[i], s[i + 1]] for i in range(len(s) - 1) if s[i + 1] - s[i] == best]
''',
    tests=[[[4, 2, 1, 3]], [[10, 1, 5, 12]], [[1, 2]], [[5, -5]], [[3, 8, -10, 23, 19, -4, -14, 27]], [[1, 3, 6, 10, 15]],
           [[0, 4, 8, 12]], [[-1000000, 1000000]], [[7, 1, 4]], [[100, 90, 80, 71, 60]]],
)
_r = rnd(7112)
p["tests"].append([_r.sample(range(-1000000, 1000001), 4000)])
_v = list(range(-1000000, 1000000, 400))[:2500]
_r.shuffle(_v)
p["tests"].append([_v])
_v = list(range(0, 5000 * 7, 7)); _v[2000] += 3; _r.shuffle(_v)
p["tests"].append([_v])


def b_mindiff(nums):
    best = min(abs(nums[i] - nums[j]) for i in range(len(nums)) for j in range(i + 1, len(nums)))
    out = []
    for i in range(len(nums)):
        for j in range(len(nums)):
            if nums[j] - nums[i] == best:
                out.append([nums[i], nums[j]])
    out.sort()
    return out


CHECKS["minimum-absolute-difference-pairs"] = (b_mindiff, lambda r: [r.sample(range(-15, 16), r.randint(2, 9))], "exact")


def v_mindiff(tests):
    for t in tests:
        a = t["args"][0]
        assert 2 <= len(a) <= 5000 and len(set(a)) == len(a) and all(-10 ** 6 <= x <= 10 ** 6 for x in a)


VALIDATE["minimum-absolute-difference-pairs"] = v_mindiff

p = add(
    id="smallest-range-after-shifting-by-k", title="Smallest Range After Shifting by K", diff="Medium", topic=T,
    fn="smallestRangeAfterShift", params=[("nums", "int[]"), ("k", "int")], ret="int", cmp="exact",
    desc="<p>You are given an integer array <code>nums</code> and a non-negative integer <code>k</code>. You must change <strong>every</strong> element exactly once: replace <code>nums[i]</code> by either <code>nums[i] + k</code> or <code>nums[i] - k</code>.</p><p>The <em>range</em> of an array is its maximum minus its minimum. Return the smallest range that can be reached.</p><p>For example, <code>nums = [1, 5, 8]</code> with <code>k = 3</code> gives <code>3</code>: shifting to <code>[1+3, 5-3, 8-3] = [4, 2, 5]</code> has range 3, and no other choice of signs does better.</p>",
    constraints=["1 &le; nums.length &le; 5,000", "0 &le; nums[i] &le; 10,000", "0 &le; k &le; 10,000"],
    hints=["Try all 2<sup>n</sup> sign choices on tiny arrays to see the pattern.",
           "Sort the array. An optimal choice raises a prefix of the small numbers (+k) and lowers the suffix of the large numbers (-k).",
           "For each split point <code>i</code> (elements <code>0..i</code> go up, <code>i+1..n-1</code> go down), the maximum is <code>max(a[i] + k, a[n-1] - k)</code> and the minimum is <code>min(a[0] + k, a[i+1] - k)</code>. Take the best over all splits, including 'everything shifted the same way'."],
    editorial=["After sorting, it never pays to lower a smaller element while raising a larger one: swapping the two signs does not increase the range. So the optimum has the form 'first i+1 elements get +k, the rest get -k' for some split <code>i</code> (or all the same sign, which keeps the original range <code>a[n-1] - a[0]</code>).",
               "For a split after index <code>i</code> the largest value is either the biggest raised element <code>a[i] + k</code> or the biggest lowered element <code>a[n-1] - k</code>, and the smallest value is either <code>a[0] + k</code> or <code>a[i+1] - k</code>. Evaluate the range for every split in O(1) each. Sorting dominates: O(n log n)."],
    time="O(n log n)", space="O(n)",
    solution='''def smallestRangeAfterShift(nums, k):
    a = sorted(nums)
    n = len(a)
    best = a[-1] - a[0]
    for i in range(n - 1):
        hi = max(a[i] + k, a[-1] - k)
        lo = min(a[0] + k, a[i + 1] - k)
        best = min(best, hi - lo)
    return best
''',
    tests=[[[1, 5, 8], 3], [[7], 5], [[0, 10], 2], [[0, 10], 7], [[1, 3, 6], 3], [[2, 2, 2], 4], [[5, 9], 0], [[0, 10000], 10000],
           [[4, 1, 9, 7], 2], [[0, 5, 10, 15], 3], [[3, 8, 4, 1], 100]],
)
_r = rnd(7113)
p["tests"].append([[_r.randint(0, 10000) for _ in range(5000)], 3000])
p["tests"].append([[_r.randint(0, 10000) for _ in range(5000)], 40])
p["tests"].append([[_r.randint(0, 600) for _ in range(5000)], 7000])


def b_srange(nums, k):
    best = None
    n = len(nums)
    for mask in range(1 << n):
        v = [nums[i] + (k if mask >> i & 1 else -k) for i in range(n)]
        r = max(v) - min(v)
        if best is None or r < best:
            best = r
    return best


CHECKS["smallest-range-after-shifting-by-k"] = (b_srange, lambda r: [[r.randint(0, 20) for _ in range(r.randint(1, 8))], r.randint(0, 12)], "exact")


def v_srange(tests):
    for t in tests:
        nums, k = t["args"]
        assert 1 <= len(nums) <= 5000 and all(0 <= x <= 10000 for x in nums) and 0 <= k <= 10000


VALIDATE["smallest-range-after-shifting-by-k"] = v_srange

p = add(
    id="best-meeting-cell-total-distance", title="Best Meeting Cell Total Distance", diff="Hard", topic=T, tier="extra",
    fn="bestMeetingDistance", params=[("grid", "int[][]")], ret="int", cmp="exact",
    desc="<p>A grid has <code>1</code> in cells where a person lives and <code>0</code> in empty cells. All people want to meet in a single cell of the grid (any cell, occupied or not). Everyone walks to the meeting cell, and the distance for one person is the Manhattan distance <code>|r1 - r2| + |c1 - c2|</code>.</p><p>Return the smallest possible sum of all walking distances.</p><p>For example, <code>[[1,0,0],[0,0,0],[0,0,1]]</code> gives <code>4</code>: both people can meet at the centre cell (or on any shortest path between them).</p>",
    constraints=["1 &le; rows, columns &le; 60", "grid[i][j] is 0 or 1", "The grid contains at least two people (two cells equal to 1)"],
    hints=["The Manhattan distance splits into a row part and a column part, and the meeting cell can pick its row and column independently.",
           "For one dimension this is the 'closest point to many points' problem: the sum of absolute distances is minimized at a median.",
           "Collect the row index of every person (already sorted if you scan row by row), and the column indices (sort them, or scan column by column). Add the distances to the two medians."],
    editorial=["The total distance is <code>sum |r_p - R| + sum |c_p - C|</code> for meeting cell <code>(R, C)</code>. The two sums depend on different unknowns, so we minimize each separately. Each is a sum of absolute deviations from one point, which is minimized at the median of the coordinates.",
               "Scanning the grid in row-major order produces the row coordinates already sorted; scanning in column-major order does the same for columns (or just sort). Take <code>rows[m // 2]</code> and <code>cols[m // 2]</code>, where m is the number of people, and sum the distances. The cost is O(rows * cols) time. Note that even if the median cell is not occupied, it is still a legal meeting cell and lies inside the grid."],
    time="O(R * C)", space="O(R * C)",
    solution='''def bestMeetingDistance(grid):
    rows, cols = [], []
    R, C = len(grid), len(grid[0])
    for i in range(R):
        for j in range(C):
            if grid[i][j] == 1:
                rows.append(i)
    for j in range(C):
        for i in range(R):
            if grid[i][j] == 1:
                cols.append(j)
    mr = rows[len(rows) // 2]
    mc = cols[len(cols) // 2]
    return sum(abs(r - mr) for r in rows) + sum(abs(c - mc) for c in cols)
''',
    tests=[[[[1, 0, 0], [0, 0, 0], [0, 0, 1]]], [[[1, 0, 0, 0, 1], [0, 0, 0, 0, 0], [0, 0, 1, 0, 0]]], [[[1, 1]]], [[[1], [1]]],
           [[[1, 0, 1]]], [[[1, 1], [1, 1]]], [[[1, 0, 0], [0, 1, 0], [0, 0, 1]]], [[[0, 0, 0], [0, 1, 0], [0, 1, 0]]],
           [[[1, 0], [0, 0], [0, 0], [1, 0]]], [[[1, 0, 0, 0, 0, 0, 1]]]],
)
_r = rnd(7114)
p["tests"].append([[[1 if _r.random() < 0.3 else 0 for _ in range(60)] for _ in range(60)]])
p["tests"].append([[[1 if (i < 5 or j >= 55) and _r.random() < 0.8 else 0 for j in range(60)] for i in range(60)]])
_g = [[0] * 60 for _ in range(60)]
_g[0][0] = _g[59][59] = _g[0][59] = _g[59][0] = 1
p["tests"].append([_g])


def b_meet(grid):
    people = [(i, j) for i in range(len(grid)) for j in range(len(grid[0])) if grid[i][j]]
    return min(sum(abs(i - a) + abs(j - b) for a, b in people) for i in range(len(grid)) for j in range(len(grid[0])))


def g_meet(r):
    R, C = r.randint(1, 5), r.randint(2, 5)
    while True:
        g = [[1 if r.random() < 0.4 else 0 for _ in range(C)] for _ in range(R)]
        if sum(map(sum, g)) >= 2:
            return [g]


def v_meet(tests):
    for t in tests:
        g = t["args"][0]
        assert 1 <= len(g) <= 60 and all(len(row) == len(g[0]) and 1 <= len(row) <= 60 for row in g)
        assert all(x in (0, 1) for row in g for x in row) and sum(map(sum, g)) >= 2


CHECKS["best-meeting-cell-total-distance"] = (b_meet, g_meet, "exact")
VALIDATE["best-meeting-cell-total-distance"] = v_meet

p = add(
    id="minimize-maximum-pair-sum", title="Minimize Maximum Pair Sum", diff="Medium", topic=T,
    fn="minMaxPairSum", params=[("nums", "int[]")], ret="int", cmp="exact",
    desc="<p>The array <code>nums</code> has an even length. Split its elements into pairs so that every element is in exactly one pair. The <em>pair sum</em> of a pair is the sum of its two elements.</p><p>Among all ways to form the pairs, return the smallest possible value of the <strong>largest</strong> pair sum.</p><p>For example, <code>[3, 5, 2, 3]</code> gives <code>7</code>: pairing (3, 3) and (5, 2) gives sums 6 and 7, and no pairing can keep both below 7. For <code>[1, 1, 9, 9]</code> the answer is <code>10</code>.</p>",
    constraints=["2 &le; nums.length &le; 8,000 and nums.length is even", "1 &le; nums[i] &le; 100,000"],
    hints=["Try pairing the largest element with something. What partner keeps its sum as small as possible?",
           "The largest element should be paired with the smallest element; otherwise some smaller partner would make a sum that is at least as bad for the large one.",
           "Sort, then pair <code>s[i]</code> with <code>s[n-1-i]</code> for every i, and return the largest of these sums."],
    editorial=["Exchange argument: let <code>big</code> be the largest element and <code>small</code> the smallest. Suppose an optimal pairing has <code>big</code> with some <code>x</code> and <code>small</code> with some <code>y</code>. Swapping partners gives pairs <code>(big, small)</code> and <code>(x, y)</code>. Since <code>small &le; x</code> we get <code>big + small &le; big + x</code>, and since <code>y &le; big</code> we get <code>x + y &le; x + big</code>, so neither new sum exceeds the old maximum. Repeating the argument on the remaining elements shows the greedy pairing is optimal.",
               "So sort and pair from both ends, tracking the maximum sum. This is O(n log n) for the sort plus O(n) for the pairing."],
    time="O(n log n)", space="O(n)",
    solution='''def minMaxPairSum(nums):
    s = sorted(nums)
    n = len(s)
    return max(s[i] + s[n - 1 - i] for i in range(n // 2))
''',
    tests=[[[3, 5, 2, 3]], [[1, 1, 9, 9]], [[1, 1]], [[100000, 100000]], [[1, 2, 3, 4, 5, 6]], [[6, 6, 6, 6]], [[1, 100000, 2, 99999]],
           [[4, 1, 8, 7]], [[2, 2, 2, 9, 9, 9]], [[5, 1, 1, 5]]],
)
_r = rnd(7115)
p["tests"].append([[_r.randint(1, 100000) for _ in range(8000)]])
p["tests"].append([[_r.randint(1, 100) for _ in range(6000)]])
p["tests"].append([[1] * 3000 + [100000] * 3000])


def _all_pairings(items):
    if not items:
        yield []
        return
    first = items[0]
    for i in range(1, len(items)):
        rest = items[1:i] + items[i + 1:]
        for tail in _all_pairings(rest):
            yield [(first, items[i])] + tail


def b_pairsum(nums):
    return min(max(a + b for a, b in pr) for pr in _all_pairings(list(nums)))


CHECKS["minimize-maximum-pair-sum"] = (b_pairsum, lambda r: [[r.randint(1, 15) for _ in range(2 * r.randint(1, 4))]], "exact")


def v_pairsum(tests):
    for t in tests:
        a = t["args"][0]
        assert 2 <= len(a) <= 8000 and len(a) % 2 == 0 and all(1 <= x <= 100000 for x in a)


VALIDATE["minimize-maximum-pair-sum"] = v_pairsum
