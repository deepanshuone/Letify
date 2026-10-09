"""Problems: classic greedy, bit/math, matrix and heap problems. See data/lib.py for the registry."""
import heapq
from collections import Counter, deque

from lib import add, rnd, CHECKS, VALIDATE, gen_arr  # noqa: F401

INT_MIN, INT_MAX = -(2 ** 31), 2 ** 31 - 1


# ---------------------------------------------------------------- EASY

p = add(
    id="number-of-1-bits", title="Number of 1 Bits", diff="Easy", topic="Math & Bit Manipulation",
    fn="hammingWeight", params=[("n", "int")], ret="int", cmp="exact",
    desc="<p>Given a 32-bit signed integer <code>n</code>, return how many bits are set to <code>1</code> in its 32-bit two's complement representation.</p><p>For example, <code>11</code> is <code>00000000000000000000000000001011</code>, which has three set bits, and <code>-1</code> has all 32 bits set.</p>",
    constraints=["-2<sup>31</sup> &le; n &le; 2<sup>31</sup> - 1", "Negative numbers use the 32-bit two's complement representation"],
    hints=["Look at the lowest bit with <code>n &amp; 1</code>, then shift right and repeat. How many times do you need to repeat?",
           "Negative numbers are a trap in some languages: an arithmetic right shift keeps the sign bit, so the loop may never reach zero. Limit the loop to 32 steps, or first convert to an unsigned 32-bit value.",
           "The expression <code>n &amp; (n - 1)</code> clears the lowest set bit. Count how many times you can apply it before reaching zero."],
    editorial=["The simplest method inspects each of the 32 bit positions: test <code>(n &gt;&gt; i) &amp; 1</code> for i from 0 to 31 and add up the results. Because the loop runs exactly 32 times, negative inputs need no special care.",
               "A faster trick is Brian Kernighan's: <code>n &amp; (n - 1)</code> removes exactly the lowest set bit, so repeating it until the value becomes zero takes as many steps as there are set bits. First mask the value to 32 bits (<code>n &amp; 0xFFFFFFFF</code>) so negative numbers behave like their unsigned counterparts."],
    time="O(k)", space="O(1)",
    solution='''def hammingWeight(n):
    n &= 0xFFFFFFFF
    count = 0
    while n:
        n &= n - 1
        count += 1
    return count
''',
    tests=[[11], [128], [0], [1], [-1], [INT_MIN], [INT_MAX], [-2], [255], [1431655765], [-1431655766], [1 << 30],
           [-(1 << 30)], [123456789], [-987654321]],
)


def b_popcount(n):
    return format(n % (2 ** 32), "032b").count("1")


def g_popcount(r):
    c = r.random()
    if c < 0.3:
        return [r.randint(-20, 20)]
    if c < 0.5:
        return [r.choice([INT_MIN, INT_MAX, -1, 0])]
    return [r.randint(INT_MIN, INT_MAX)]


def v_popcount(tests):
    for t in tests:
        assert INT_MIN <= t["args"][0] <= INT_MAX
        assert 0 <= t["expected"] <= 32


CHECKS["number-of-1-bits"] = (b_popcount, g_popcount, "exact")
VALIDATE["number-of-1-bits"] = v_popcount

p = add(
    id="happy-number", title="Happy Number", diff="Easy", topic="Math & Bit Manipulation",
    fn="isHappy", params=[("n", "int")], ret="bool", cmp="exact",
    desc="<p>Start with a positive integer <code>n</code>. Repeatedly replace it with the sum of the squares of its decimal digits. For instance, <code>19</code> becomes <code>1&sup2; + 9&sup2; = 82</code>, then <code>8&sup2; + 2&sup2; = 68</code>, and so on.</p><p>If this process eventually reaches <code>1</code>, the number is <em>happy</em>. Otherwise it runs forever in a cycle that never contains <code>1</code>. Return <code>true</code> if <code>n</code> is happy and <code>false</code> if not.</p>",
    constraints=["1 &le; n &le; 2<sup>31</sup> - 1"],
    hints=["Simulate the process. The difficulty is knowing when to stop for an unhappy number.",
           "The sequence either reaches 1 or repeats a value it has visited before. A hash set of seen values detects the repeat.",
           "After the first step the value is small (at most 810 for a 10-digit number), so a cycle must appear quickly. You can also detect it with slow and fast pointers and no extra memory."],
    editorial=["Define <code>next(x)</code> as the sum of squared digits of x. A 10-digit number is mapped to at most 10 * 81 = 810, and every later value stays small, so the sequence lives in a tiny range. Hence it must either hit 1 (and then stay at 1) or enter a cycle.",
               "Store each visited value in a set and stop when you reach 1 (answer true) or see a value again (answer false). To save memory, use Floyd's tortoise and hare: advance a slow pointer one step and a fast pointer two steps; if they meet at a value other than 1 there is a cycle."],
    time="O(log n)", space="O(1)",
    solution='''def isHappy(n):
    def nxt(x):
        total = 0
        while x:
            x, d = divmod(x, 10)
            total += d * d
        return total

    slow, fast = n, nxt(n)
    while fast != 1 and slow != fast:
        slow = nxt(slow)
        fast = nxt(nxt(fast))
    return fast == 1
''',
    tests=[[19], [2], [1], [7], [4], [100], [111], [1111111], [999999999], [INT_MAX], [1000000000], [2147483646],
           [989], [20], [68]],
)


def b_happy(n):
    x = n
    for _ in range(2000):
        if x == 1:
            return True
        x = sum(int(c) ** 2 for c in str(x))
    return x == 1


def g_happy(r):
    c = r.random()
    if c < 0.6:
        return [r.randint(1, 3000)]
    return [r.randint(1, INT_MAX)]


def v_happy(tests):
    for t in tests:
        assert 1 <= t["args"][0] <= INT_MAX
    assert any(t["expected"] for t in tests) and any(not t["expected"] for t in tests)


CHECKS["happy-number"] = (b_happy, g_happy, "exact")
VALIDATE["happy-number"] = v_happy

p = add(
    id="last-stone-weight", title="Last Stone Weight", diff="Easy", topic="Heap",
    fn="lastStoneWeight", params=[("stones", "int[]")], ret="int", cmp="exact",
    desc="<p>You have a pile of stones, where <code>stones[i]</code> is the weight of the i-th stone. Play the following game until at most one stone remains:</p><ul><li>Take the two heaviest stones, with weights <code>x &le; y</code>.</li><li>If <code>x == y</code>, both stones are destroyed.</li><li>Otherwise the stone of weight <code>x</code> is destroyed and the other becomes a stone of weight <code>y - x</code>.</li></ul><p>Return the weight of the last remaining stone, or <code>0</code> if no stones remain.</p>",
    constraints=["1 &le; stones.length &le; 1,000", "1 &le; stones[i] &le; 1,000,000"],
    hints=["Each round needs the two largest values. Re-sorting the whole array every round works but is slow.",
           "A max-heap gives you the largest element in O(log n) and lets you insert new elements just as fast.",
           "Pop two stones, push their difference back if it is non-zero, and stop when fewer than two stones remain."],
    editorial=["Keep all weights in a max-heap. While at least two stones remain, pop the heaviest two, and if they differ push back their difference. Each round removes at least one stone, so there are fewer than n rounds, each costing O(log n).",
               "Python's <code>heapq</code> is a min-heap, so store negated weights. Sorting the array every round is simpler but costs O(n&sup2; log n) overall."],
    time="O(n log n)", space="O(n)",
    solution='''import heapq

def lastStoneWeight(stones):
    heap = [-s for s in stones]
    heapq.heapify(heap)
    while len(heap) > 1:
        y = -heapq.heappop(heap)
        x = -heapq.heappop(heap)
        if y != x:
            heapq.heappush(heap, -(y - x))
    return -heap[0] if heap else 0
''',
    tests=[[[2, 7, 4, 1, 8, 1]], [[1]], [[3, 3]], [[5, 2]], [[1, 1, 1]], [[10, 4, 6]], [[9, 3, 2, 10]],
           [[1000000, 1]], [[7, 7, 7, 7]], [[4, 3, 4, 3, 2, 20]]],
)
_r = rnd(201)
p["tests"].append([[_r.randint(1, 1000000) for _ in range(1000)]])
p["tests"].append([[_r.randint(1, 20) for _ in range(1000)]])
p["tests"].append([[1000000] * 1000])
p["tests"].append([[i + 1 for i in range(1000)]])


def b_stones(stones):
    s = list(stones)
    while len(s) > 1:
        s.sort()
        y, x = s.pop(), s.pop()
        if y != x:
            s.append(y - x)
    return s[0] if s else 0


def g_stones(r):
    return [[r.randint(1, 12) for _ in range(r.randint(1, 9))]]


def v_stones(tests):
    for t in tests:
        s = t["args"][0]
        assert 1 <= len(s) <= 1000 and all(1 <= x <= 10 ** 6 for x in s)


CHECKS["last-stone-weight"] = (b_stones, g_stones, "exact")
VALIDATE["last-stone-weight"] = v_stones


# ---------------------------------------------------------------- MEDIUM

p = add(
    id="gas-station", title="Gas Station", diff="Medium", topic="Greedy",
    fn="canCompleteCircuit", params=[("gas", "int[]"), ("cost", "int[]")], ret="int", cmp="exact",
    desc="<p>There are <code>n</code> gas stations arranged in a circle. Station <code>i</code> sells <code>gas[i]</code> units of fuel, and driving from station <code>i</code> to the next station <code>(i + 1) % n</code> burns <code>cost[i]</code> units.</p><p>You begin at some station with an empty tank, fill up there, and then drive clockwise, refuelling at every station you reach. You complete the circuit if the tank never goes below zero on the way and you arrive back at the starting station. Return the <strong>smallest</strong> starting index from which you can complete the circuit, or <code>-1</code> if no start works.</p>",
    constraints=["1 &le; gas.length = cost.length &le; 5,000", "0 &le; gas[i], cost[i] &le; 10,000"],
    hints=["Trying every start and simulating the lap costs O(n&sup2;). Look for structure that lets you skip many starts at once.",
           "If the total gas is smaller than the total cost, the answer is -1 straight away. Otherwise some start works.",
           "Sweep once, keeping a running tank. When the tank drops below zero at station i, none of the starts between the previous candidate and i can work, so restart the candidate at i + 1."],
    editorial=["If <code>sum(gas) &lt; sum(cost)</code>, no start works. Otherwise a valid start exists, and a single sweep finds it. Keep a running tank from a candidate start. If the tank becomes negative after station i, then starting at any station between the candidate and i would have reached i with at most as much fuel, and would fail too. So the next candidate is i + 1 and the tank resets.",
               "The candidate left at the end of the sweep is the answer. It is also the smallest valid index, because it is the first position where the prefix sum of <code>gas[i] - cost[i]</code> reaches its global minimum. The sweep is O(n) time with O(1) extra space."],
    time="O(n)", space="O(1)",
    solution='''def canCompleteCircuit(gas, cost):
    if sum(gas) < sum(cost):
        return -1
    start = 0
    tank = 0
    for i in range(len(gas)):
        tank += gas[i] - cost[i]
        if tank < 0:
            start = i + 1
            tank = 0
    return start
''',
    tests=[[[1, 2, 3, 4, 5], [3, 4, 5, 1, 2]], [[2, 3, 4], [3, 4, 3]], [[5], [4]], [[3], [4]], [[0], [0]],
           [[1, 1], [1, 1]], [[2, 0, 0, 5], [1, 1, 1, 1]], [[1, 2, 3], [2, 3, 1]], [[0, 0, 7], [0, 0, 7]],
           [[4, 5, 2, 6, 5, 3], [3, 2, 7, 3, 2, 9]]],
)


def _gas_case(r, n, hi, solvable):
    cost = [r.randint(0, hi) for _ in range(n)]
    gas = [max(0, min(hi * 2, 10000, c + r.randint(-hi // 4, hi // 4))) for c in cost]
    deficit = sum(cost) - sum(gas)
    if solvable:
        # top up random stations until total gas covers total cost
        while deficit > 0:
            i = r.randrange(n)
            add_ = min(deficit, hi * 2 - gas[i], 10000 - gas[i])
            gas[i] += add_
            deficit -= add_
        k = r.randrange(n)
        return [gas[k:] + gas[:k], cost[k:] + cost[:k]]
    while deficit <= 0:
        i = r.randrange(n)
        gas[i] = max(0, gas[i] - r.randint(1, hi))
        deficit = sum(cost) - sum(gas)
    return [gas, cost]


_r = rnd(202)
p["tests"].append(_gas_case(_r, 5000, 10000, True))
p["tests"].append(_gas_case(_r, 5000, 10000, False))
p["tests"].append(_gas_case(_r, 4999, 100, True))
p["tests"].append([[1] * 5000, [1] * 5000])
p["tests"].append([[0] * 4999 + [10000], [1] + [0] * 4998 + [0]])
p["tests"].append([[10000] * 2500 + [0] * 2500, [0] * 2500 + [10000] * 2500])


def b_gas(gas, cost):
    n = len(gas)
    for s in range(n):
        tank = 0
        ok = True
        for step in range(n):
            i = (s + step) % n
            tank += gas[i]
            tank -= cost[i]
            if tank < 0:
                ok = False
                break
        if ok:
            return s
    return -1


def g_gas(r):
    n = r.randint(1, 8)
    gas = [r.randint(0, 6) for _ in range(n)]
    cost = [r.randint(0, 6) for _ in range(n)]
    if r.random() < 0.5:
        cost = [max(0, c - r.randint(0, 3)) for c in cost]
    return [gas, cost]


def v_gas(tests):
    for t in tests:
        gas, cost = t["args"]
        assert len(gas) == len(cost) and 1 <= len(gas) <= 5000
        assert all(0 <= x <= 10000 for x in gas + cost)
    assert any(t["expected"] == -1 for t in tests) and any(t["expected"] > 0 for t in tests)


CHECKS["gas-station"] = (b_gas, g_gas, "exact")
VALIDATE["gas-station"] = v_gas

p = add(
    id="jump-game-ii", title="Jump Game II", diff="Medium", topic="Greedy",
    fn="minJumps", params=[("nums", "int[]")], ret="int", cmp="exact",
    desc="<p>You stand on index <code>0</code> of the integer array <code>nums</code>. From index <code>i</code> you may jump forward by any distance from <code>1</code> to <code>nums[i]</code> (so a value of <code>0</code> means you cannot move from there).</p><p>Return the minimum number of jumps needed to reach the last index. The input is built so that the last index is always reachable.</p>",
    constraints=["1 &le; nums.length &le; 10,000", "0 &le; nums[i] &le; 1,000", "The last index is reachable from index 0"],
    hints=["A DP where <code>dp[i]</code> is the fewest jumps to reach i works, but is O(n&sup2;) in the worst case.",
           "Think of the indices reachable with 1 jump, then with 2 jumps, and so on. Each group is a contiguous range, like levels of a BFS.",
           "Track the end of the current range and the farthest index reachable from anything inside it. When you pass the end of the range, take a jump and extend the range to the farthest point."],
    editorial=["Treat the array as an implicit graph and run BFS, noticing that the set of indices reachable in exactly k jumps forms a contiguous block. Keep <code>cur_end</code>, the last index reachable with the jumps taken so far, and <code>far</code>, the farthest index reachable by one more jump from any index seen so far.",
               "Scan from left to right, updating <code>far = max(far, i + nums[i])</code>. When i reaches <code>cur_end</code> you must jump again: increment the counter and set <code>cur_end = far</code>. Stop the scan before the last index. This greedy is O(n) time and O(1) space."],
    time="O(n)", space="O(1)",
    solution='''def minJumps(nums):
    jumps = 0
    cur_end = 0
    far = 0
    for i in range(len(nums) - 1):
        far = max(far, i + nums[i])
        if i == cur_end:
            jumps += 1
            cur_end = far
    return jumps
''',
    tests=[[[2, 3, 1, 1, 4]], [[2, 3, 0, 1, 4]], [[0]], [[1]], [[1, 1, 1, 1]], [[5, 1, 1, 1, 1, 1]], [[1, 2]],
           [[3, 0, 0, 1]], [[1, 2, 1, 1, 1]], [[4, 1, 1, 3, 1, 1, 1]]],
)
_r = rnd(203)
p["tests"].append([[1] * 10000])
p["tests"].append([[1000] * 10000])
_a = []
while len(_a) < 10000:
    _a.append(_r.randint(1, 30))
p["tests"].append([_a])
_a = [0] * 10000
for _i in range(0, 9999, 7):
    _a[_i] = 7
_a[9996] = 3
p["tests"].append([_a])
_a = [_r.choice([0, 0, 1, 2, 3]) for _ in range(10000)]
_i = 0
while _i < 9999:  # make sure the end stays reachable
    if _a[_i] == 0:
        _a[_i] = _r.randint(1, 3)
    _i += _a[_i] if _r.random() < 0.7 else 1
p["tests"].append([_a])


def _reachable(nums):
    far = 0
    for i, x in enumerate(nums):
        if i > far:
            return False
        far = max(far, i + x)
    return far >= len(nums) - 1


def b_jumps(nums):
    n = len(nums)
    INF = 10 ** 9
    dp = [INF] * n
    dp[0] = 0
    for i in range(n):
        for j in range(i + 1, min(n, i + nums[i] + 1)):
            if dp[i] + 1 < dp[j]:
                dp[j] = dp[i] + 1
    return dp[-1]


def g_jumps(r):
    while True:
        a = [r.randint(0, 4) for _ in range(r.randint(1, 10))]
        if _reachable(a):
            return [a]


def v_jumps(tests):
    for t in tests:
        a = t["args"][0]
        assert 1 <= len(a) <= 10000 and all(0 <= x <= 1000 for x in a)
        assert _reachable(a)


CHECKS["jump-game-ii"] = (b_jumps, g_jumps, "exact")
VALIDATE["jump-game-ii"] = v_jumps

p = add(
    id="spiral-matrix", title="Spiral Matrix", diff="Medium", topic="Matrix",
    fn="spiralOrder", params=[("matrix", "int[][]")], ret="int[]", cmp="exact",
    desc="<p>Given an <code>m x n</code> integer matrix, return all of its elements in a single flat array, reading them in clockwise spiral order: start at the top-left cell, go right along the top row, then down the right column, then left along the bottom row, then up the left column, and keep spiralling inwards until every cell has been visited once.</p>",
    constraints=["1 &le; m, n &le; 100", "-100 &le; matrix[i][j] &le; 100", "Every row has exactly n elements"],
    hints=["Picture four edges of a rectangle that you peel off one at a time. How do the edges change after each full loop?",
           "Maintain four boundaries: top, bottom, left, right. After walking along an edge, move that boundary one step inwards.",
           "Be careful when only one row or one column is left: after walking the top row and the right column, check that top &le; bottom and left &le; right before walking back, or you will read cells twice."],
    editorial=["Keep four indices <code>top, bottom, left, right</code> bounding the unvisited rectangle. Repeat while <code>top &le; bottom</code> and <code>left &le; right</code>: read the top row left to right and increment top; read the right column top to bottom and decrement right; if rows remain, read the bottom row right to left and decrement bottom; if columns remain, read the left column bottom to top and increment left.",
               "The two guards before the last two edges handle matrices that collapse to a single row or column in the middle of the walk. Each cell is appended once, so the running time is O(m * n) and the extra space beyond the output is O(1). An alternative is to simulate the walk with a visited grid and turn right whenever the next cell is blocked."],
    time="O(m * n)", space="O(1)",
    solution='''def spiralOrder(matrix):
    top, bottom = 0, len(matrix) - 1
    left, right = 0, len(matrix[0]) - 1
    out = []
    while top <= bottom and left <= right:
        for j in range(left, right + 1):
            out.append(matrix[top][j])
        top += 1
        for i in range(top, bottom + 1):
            out.append(matrix[i][right])
        right -= 1
        if top <= bottom:
            for j in range(right, left - 1, -1):
                out.append(matrix[bottom][j])
            bottom -= 1
        if left <= right:
            for i in range(bottom, top - 1, -1):
                out.append(matrix[i][left])
            left += 1
    return out
''',
    tests=[[[[1, 2, 3], [4, 5, 6], [7, 8, 9]]], [[[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12]]], [[[7]]],
           [[[1, 2, 3, 4]]], [[[1], [2], [3], [4]]], [[[1, 2], [3, 4]]], [[[1, 2], [3, 4], [5, 6]]],
           [[[1, 2, 3], [4, 5, 6]]], [[[-100, 100], [0, -1], [5, 5], [6, 7]]]],
)
_r = rnd(204)
for _m, _n in ((100, 100), (100, 1), (1, 100), (37, 100), (100, 53)):
    p["tests"].append([[[_r.randint(-100, 100) for _ in range(_n)] for _ in range(_m)]])


def b_spiral(matrix):
    m, n = len(matrix), len(matrix[0])
    seen = [[False] * n for _ in range(m)]
    dirs = [(0, 1), (1, 0), (0, -1), (-1, 0)]
    r = c = d = 0
    out = []
    for _ in range(m * n):
        out.append(matrix[r][c])
        seen[r][c] = True
        nr, nc = r + dirs[d][0], c + dirs[d][1]
        if not (0 <= nr < m and 0 <= nc < n) or seen[nr][nc]:
            d = (d + 1) % 4
            nr, nc = r + dirs[d][0], c + dirs[d][1]
        r, c = nr, nc
    return out


def g_spiral(r):
    m, n = r.randint(1, 6), r.randint(1, 6)
    return [[[r.randint(-9, 9) for _ in range(n)] for _ in range(m)]]


def v_spiral(tests):
    for t in tests:
        mat = t["args"][0]
        assert 1 <= len(mat) <= 100 and 1 <= len(mat[0]) <= 100
        assert all(len(row) == len(mat[0]) for row in mat)
        assert all(-100 <= x <= 100 for row in mat for x in row)
        assert len(t["expected"]) == len(mat) * len(mat[0])


CHECKS["spiral-matrix"] = (b_spiral, g_spiral, "exact")
VALIDATE["spiral-matrix"] = v_spiral

p = add(
    id="set-matrix-zeroes", title="Set Matrix Zeroes", diff="Medium", topic="Matrix",
    fn="setZeroes", params=[("matrix", "int[][]")], ret="int[][]", cmp="exact",
    desc="<p>Given an <code>m x n</code> integer matrix, whenever a cell contains <code>0</code>, set every cell in its entire row and its entire column to <code>0</code>. Return the resulting matrix.</p><p>All decisions are based on the <em>original</em> matrix: zeros created by this process must not cause further rows or columns to be cleared. Aim for O(1) extra space beyond the matrix itself.</p>",
    constraints=["1 &le; m, n &le; 100", "-2<sup>31</sup> &le; matrix[i][j] &le; 2<sup>31</sup> - 1"],
    hints=["First collect the rows and columns that contain a zero in the original matrix, and only then start writing zeros.",
           "Two arrays, one boolean per row and one per column, are enough. Can you store those flags inside the matrix itself?",
           "Use the first row and first column as the flag storage. Remember separately whether the first row and the first column originally contained a zero, since they are overwritten by the markers."],
    editorial=["The straightforward approach records which rows and which columns contain a zero in two arrays of size m and n, then does a second pass clearing every cell whose row or column is flagged. That uses O(m + n) extra space.",
               "To get O(1) extra space, reuse the first row and first column as the flag arrays. Before anything else, note whether row 0 and column 0 contain a zero. Then scan the rest of the matrix and, on seeing a zero at (i, j), set <code>matrix[i][0]</code> and <code>matrix[0][j]</code> to 0. Next clear every cell (i, j) with i, j &ge; 1 whose row marker or column marker is 0. Finally clear the first row and first column if they were flagged at the start."],
    time="O(m * n)", space="O(1)",
    solution='''def setZeroes(matrix):
    m, n = len(matrix), len(matrix[0])
    first_row = any(matrix[0][j] == 0 for j in range(n))
    first_col = any(matrix[i][0] == 0 for i in range(m))
    for i in range(1, m):
        for j in range(1, n):
            if matrix[i][j] == 0:
                matrix[i][0] = 0
                matrix[0][j] = 0
    for i in range(1, m):
        for j in range(1, n):
            if matrix[i][0] == 0 or matrix[0][j] == 0:
                matrix[i][j] = 0
    if first_row:
        for j in range(n):
            matrix[0][j] = 0
    if first_col:
        for i in range(m):
            matrix[i][0] = 0
    return matrix
''',
    tests=[[[[1, 1, 1], [1, 0, 1], [1, 1, 1]]], [[[0, 1, 2, 0], [3, 4, 5, 2], [1, 3, 1, 5]]], [[[5]]], [[[0]]],
           [[[1, 2, 3]]], [[[1], [0], [3]]], [[[1, 0]]], [[[0, 1], [1, 1]]], [[[1, 2], [3, 0]]],
           [[[INT_MIN, 0, INT_MAX], [4, 5, 6], [7, 8, INT_MIN]]], [[[1, 2, 3], [4, 5, 6]]],
           [[[0, 0, 0], [0, 0, 0]]]],
)
_r = rnd(205)
for _m, _n, _pz in ((100, 100, 0.0005), (100, 100, 0.02), (60, 100, 0.0), (100, 99, 0.3)):
    p["tests"].append([[[0 if _r.random() < _pz else _r.randint(INT_MIN, INT_MAX) or 1 for _ in range(_n)]
                        for _ in range(_m)]])


def b_zeroes(matrix):
    m, n = len(matrix), len(matrix[0])
    orig = [row[:] for row in matrix]
    out = []
    for i in range(m):
        row = []
        for j in range(n):
            bad = any(orig[i][c] == 0 for c in range(n)) or any(orig[r][j] == 0 for r in range(m))
            row.append(0 if bad else orig[i][j])
        out.append(row)
    return out


def g_zeroes(r):
    m, n = r.randint(1, 6), r.randint(1, 6)
    pz = r.choice([0.0, 0.1, 0.25, 0.5])
    return [[[0 if r.random() < pz else r.randint(-5, 5) or 7 for _ in range(n)] for _ in range(m)]]


def v_zeroes(tests):
    for t in tests:
        mat = t["args"][0]
        assert 1 <= len(mat) <= 100 and 1 <= len(mat[0]) <= 100
        assert all(len(row) == len(mat[0]) for row in mat)


CHECKS["set-matrix-zeroes"] = (b_zeroes, g_zeroes, "exact")
VALIDATE["set-matrix-zeroes"] = v_zeroes

p = add(
    id="k-closest-points-to-origin", title="K Closest Points to Origin", diff="Medium", topic="Heap",
    fn="kClosest", params=[("points", "int[][]"), ("k", "int")], ret="int[][]", cmp="rowset",
    desc="<p>You are given <code>points</code>, a list of <code>[x, y]</code> coordinates on a plane, and an integer <code>k</code>. Return the <code>k</code> points that are closest to the origin <code>(0, 0)</code> by straight-line (Euclidean) distance.</p><p>The points may be returned in any order. The input is built so that the set of <code>k</code> closest points is unique: when <code>k &lt; n</code>, the k-th closest point is strictly closer than the (k+1)-th closest.</p>",
    constraints=["1 &le; k &le; points.length &le; 10,000", "points[i].length = 2", "-10,000 &le; x, y &le; 10,000", "The answer set is unique (no tie at the boundary of the k-th and (k+1)-th closest)"],
    hints=["Sorting all points by distance and taking the first k works in O(n log n). You do not need the full order, though.",
           "You can compare squared distances <code>x*x + y*y</code>, so no square root or floating point is needed.",
           "Keep a max-heap of size k holding the best points seen so far, keyed by distance. If a new point is closer than the heap's top, replace the top."],
    editorial=["Compare squared distances to avoid floating point arithmetic. The simplest solution sorts the points by squared distance and slices the first k, in O(n log n).",
               "A heap does better when k is small: maintain a max-heap (keyed by squared distance) containing at most k points. For every new point, push it; if the heap grows beyond k, pop the farthest point. After scanning all points the heap holds the k closest, in O(n log k) time and O(k) space. Quickselect can reach O(n) on average."],
    time="O(n log k)", space="O(k)",
    solution='''import heapq

def kClosest(points, k):
    heap = []
    for x, y in points:
        heapq.heappush(heap, (-(x * x + y * y), x, y))
        if len(heap) > k:
            heapq.heappop(heap)
    return [[x, y] for _, x, y in heap]
''',
    tests=[[[[1, 3], [-2, 2]], 1], [[[3, 3], [5, -1], [-2, 4]], 2], [[[0, 0]], 1], [[[1, 1], [2, 2], [3, 3]], 3],
           [[[5, 5], [-5, 5], [1, 0], [0, -2]], 2], [[[1, 1], [1, 1], [4, 4]], 2],
           [[[10000, 10000], [-10000, -10000], [0, 1]], 1], [[[2, 0], [0, 3], [-4, 0], [0, -5]], 3],
           [[[7, 1], [-1, 7], [3, 3], [0, 0], [9, 9]], 4]],
)


def _kc_unique(points, k):
    d = sorted(x * x + y * y for x, y in points)
    return k == len(points) or d[k - 1] < d[k]


def _kc_case(r, n, k, lim):
    while True:
        pts = [[r.randint(-lim, lim), r.randint(-lim, lim)] for _ in range(n)]
        if _kc_unique(pts, k):
            return [pts, k]


_r = rnd(206)
p["tests"].append(_kc_case(_r, 10000, 10, 10000))
p["tests"].append(_kc_case(_r, 10000, 5000, 10000))
p["tests"].append(_kc_case(_r, 10000, 9999, 10000))
p["tests"].append(_kc_case(_r, 10000, 1, 10000))
p["tests"].append(_kc_case(_r, 3000, 3000, 10000))
p["tests"].append(_kc_case(_r, 5000, 100, 30))


def b_kclosest(points, k):
    order = sorted(range(len(points)), key=lambda i: points[i][0] ** 2 + points[i][1] ** 2)
    return [list(points[i]) for i in order[:k]]


def g_kclosest(r):
    n = r.randint(1, 9)
    k = r.randint(1, n)
    return _kc_case(r, n, k, r.choice([3, 6, 12]))


def v_kclosest(tests):
    for t in tests:
        pts, k = t["args"]
        assert 1 <= k <= len(pts) <= 10000
        assert all(len(q) == 2 and -10000 <= q[0] <= 10000 and -10000 <= q[1] <= 10000 for q in pts)
        assert _kc_unique(pts, k), "boundary tie"
        assert len(t["expected"]) == k


CHECKS["k-closest-points-to-origin"] = (b_kclosest, g_kclosest, "rowset")
VALIDATE["k-closest-points-to-origin"] = v_kclosest

p = add(
    id="task-scheduler", title="Task Scheduler", diff="Medium", topic="Heap",
    fn="leastInterval", params=[("tasks", "int[]"), ("n", "int")], ret="int", cmp="exact",
    desc="<p>A CPU must run every task in <code>tasks</code>, where equal numbers mean tasks of the same type. Each unit of time the CPU either runs one task or sits idle. The tasks may be executed in any order, but two tasks of the <strong>same</strong> type must be separated by at least <code>n</code> units of time (so after running a task of some type, the next task of that type may start no earlier than <code>n + 1</code> time units later).</p><p>Return the minimum total number of time units needed to finish all the tasks, counting idle units.</p>",
    constraints=["1 &le; tasks.length &le; 10,000", "0 &le; tasks[i] &le; 25", "0 &le; n &le; 100"],
    hints=["Only the number of tasks of each type matters, not their order in the input. Start by counting them.",
           "Greedy idea: in each window of n + 1 time units, run the most frequent remaining types, one task of each distinct type.",
           "Use a max-heap of remaining counts. In every round pop up to n + 1 types, run one task of each, push back those with tasks left, and add n + 1 to the time unless this was the final round."],
    editorial=["Count the tasks of each type and put the counts in a max-heap. Time is processed in rounds of n + 1 units. In a round, pop up to n + 1 of the largest counts (each pop is a different type, so the cooldown is respected), decrement them, and remember those that still have work. After the round push them back. If the heap is non-empty the round consumed all n + 1 units (idle slots included); in the final round only as many units as tasks were run are added.",
               "Always running the types with the most remaining work is optimal because the most frequent type is the bottleneck. There is also a closed form: with <code>m</code> the largest count and <code>c</code> the number of types having that count, the answer is <code>max(len(tasks), (m - 1) * (n + 1) + c)</code>."],
    time="O(T log 26)", space="O(1)",
    solution='''import heapq
from collections import Counter

def leastInterval(tasks, n):
    heap = [-c for c in Counter(tasks).values()]
    heapq.heapify(heap)
    time = 0
    while heap:
        slots = n + 1
        left = []
        while slots and heap:
            c = heapq.heappop(heap) + 1
            slots -= 1
            if c < 0:
                left.append(c)
        for c in left:
            heapq.heappush(heap, c)
        time += (n + 1) if heap else (n + 1 - slots)
    return time
''',
    tests=[[[0, 0, 0, 1, 1, 1], 2], [[0, 0, 0, 1, 1, 1], 0], [[0, 0, 0, 0, 0, 0, 1, 2, 3, 4, 5], 2], [[5], 3],
           [[1, 1], 3], [[1, 2, 3, 4], 5], [[0, 0, 1, 1, 2, 2], 1], [[0, 0, 0, 1, 1, 2], 4],
           [[0, 0, 0, 1, 1, 1, 2, 2, 3, 3, 4, 5], 2], [[7, 7, 7, 7], 0]],
)
_r = rnd(207)
p["tests"].append([[_r.randint(0, 25) for _ in range(10000)], 100])
p["tests"].append([[_r.randint(0, 25) for _ in range(10000)], 3])
p["tests"].append([[0] * 5000 + [1] * 5000, 100])
p["tests"].append([[0] * 9000 + [_r.randint(1, 25) for _ in range(1000)], 100])
p["tests"].append([[0] * 5000 + [1] * 2500 + [2] * 2500, 2])


def b_scheduler(tasks, n):
    # Exhaustive BFS over (remaining counts, last n slots): independent of any greedy argument.
    types = sorted(set(tasks))
    cnt = tuple(tasks.count(t) for t in types)
    start = (cnt, tuple([-1] * n))
    seen = {start}
    frontier = [start]
    steps = 0
    while frontier:
        nxt = []
        for counts, hist in frontier:
            if not any(counts):
                return steps
            options = [-1]
            for i, c in enumerate(counts):
                if c and i not in hist:
                    options.append(i)
            for o in options:
                nc = list(counts)
                if o >= 0:
                    nc[o] -= 1
                nh = (hist[1:] + (o,)) if n else ()
                st = (tuple(nc), nh)
                if st not in seen:
                    seen.add(st)
                    nxt.append(st)
        frontier = nxt
        steps += 1
    return steps


def g_scheduler(r):
    tasks = [r.randint(0, r.choice([1, 2, 3])) for _ in range(r.randint(1, 7))]
    return [tasks, r.randint(0, 3)]


def v_scheduler(tests):
    for t in tests:
        tasks, n = t["args"]
        assert 1 <= len(tasks) <= 10000 and all(0 <= x <= 25 for x in tasks) and 0 <= n <= 100
        m = max(Counter(tasks).values())
        c = sum(1 for v in Counter(tasks).values() if v == m)
        assert t["expected"] == max(len(tasks), (m - 1) * (n + 1) + c)


CHECKS["task-scheduler"] = (b_scheduler, g_scheduler, "exact")
VALIDATE["task-scheduler"] = v_scheduler


# ---------------------------------------------------------------- HARD

p = add(
    id="candy", title="Candy", diff="Hard", topic="Greedy",
    fn="candy", params=[("ratings", "int[]")], ret="int", cmp="exact",
    desc="<p>Children stand in a line, and child <code>i</code> has rating <code>ratings[i]</code>. You must give every child at least one candy, and any child with a strictly higher rating than an <strong>adjacent</strong> neighbour (left or right) must receive strictly more candies than that neighbour. Equal ratings impose no constraint.</p><p>Return the minimum total number of candies you need to hand out.</p>",
    constraints=["1 &le; ratings.length &le; 10,000", "0 &le; ratings[i] &le; 20,000"],
    hints=["Handle the two directions separately. First think only about the constraint with the left neighbour.",
           "Sweep left to right: if a child's rating is higher than the left neighbour's, give one more candy than that neighbour, otherwise start at 1.",
           "Do a second sweep from right to left for the right-neighbour constraint, and for each child take the larger of the two requirements. The sum is the minimum."],
    editorial=["The two rules, one about each neighbour, are independent lower bounds. Make an array <code>left</code> where <code>left[i]</code> is the length of the strictly increasing run ending at i (counting i), and an array <code>right</code> with the length of the strictly decreasing run starting at i. Child i needs at least <code>max(left[i], right[i])</code> candies.",
               "That bound is also sufficient: giving each child exactly the maximum satisfies both neighbour constraints, so it is optimal. Two passes and one extra array give O(n) time. A single pass tracking the lengths of the current up-slope and down-slope reduces the extra space to O(1)."],
    time="O(n)", space="O(n)",
    solution='''def candy(ratings):
    n = len(ratings)
    give = [1] * n
    for i in range(1, n):
        if ratings[i] > ratings[i - 1]:
            give[i] = give[i - 1] + 1
    for i in range(n - 2, -1, -1):
        if ratings[i] > ratings[i + 1] and give[i] <= give[i + 1]:
            give[i] = give[i + 1] + 1
    return sum(give)
''',
    tests=[[[1, 0, 2]], [[1, 2, 2]], [[5]], [[1, 2, 3, 4, 5]], [[5, 4, 3, 2, 1]], [[3, 3, 3]], [[1, 3, 2, 2, 1]],
           [[1, 2, 87, 87, 87, 2, 1]], [[1, 3, 4, 5, 2]], [[0, 20000, 0, 20000, 0]], [[2, 1, 2, 1, 2]],
           [[1, 6, 10, 8, 7, 3, 2]]],
)
_r = rnd(208)
p["tests"].append([list(range(10000))])
p["tests"].append([list(range(10000, 0, -1))])
p["tests"].append([[_r.randint(0, 20000) for _ in range(10000)]])
p["tests"].append([[_r.randint(0, 3) for _ in range(10000)]])
p["tests"].append([[i % 100 for i in range(10000)]])
p["tests"].append([list(range(5000)) + list(range(5000, 0, -1))])


def b_candy(ratings):
    # relax the constraints repeatedly until nothing changes
    n = len(ratings)
    c = [1] * n
    changed = True
    while changed:
        changed = False
        for i in range(n):
            for j in (i - 1, i + 1):
                if 0 <= j < n and ratings[i] > ratings[j] and c[i] <= c[j]:
                    c[i] = c[j] + 1
                    changed = True
    return sum(c)


def g_candy(r):
    return [[r.randint(0, r.choice([2, 4, 8])) for _ in range(r.randint(1, 10))]]


def v_candy(tests):
    for t in tests:
        a = t["args"][0]
        assert 1 <= len(a) <= 10000 and all(0 <= x <= 20000 for x in a)


CHECKS["candy"] = (b_candy, g_candy, "exact")
VALIDATE["candy"] = v_candy

p = add(
    id="ipo", title="IPO", diff="Hard", topic="Heap",
    fn="findMaximizedCapital", params=[("k", "int"), ("w", "int"), ("profits", "int[]"), ("capital", "int[]")],
    ret="int", cmp="exact",
    desc="<p>A company wants to raise its capital before an IPO by completing at most <code>k</code> distinct projects. You start with capital <code>w</code>. Project <code>i</code> yields a pure profit of <code>profits[i]</code> but you may only start it when your current capital is at least <code>capital[i]</code>. Starting a project does not consume capital: when you finish it, its profit is simply added to your capital, and the finished project cannot be repeated.</p><p>Projects are done one after another. Return the maximum capital you can have after completing at most <code>k</code> projects.</p>",
    constraints=["1 &le; k &le; 5,000", "0 &le; w &le; 10<sup>9</sup>", "profits.length = capital.length = n, with 1 &le; n &le; 5,000", "0 &le; profits[i] &le; 10,000", "0 &le; capital[i] &le; 10<sup>9</sup>"],
    hints=["At every step, which projects are even allowed? Among those, which one would you pick?",
           "Since profit never decreases your capital and capital only unlocks more projects, always picking the most profitable affordable project is safe.",
           "Sort projects by required capital. Sweep a pointer to move every newly affordable project into a max-heap keyed by profit, then pop the best one, add its profit and repeat up to k times."],
    editorial=["Greedy works here because finishing any project only increases capital, and a higher capital can never make an option disappear. So among all currently affordable projects the one with the largest profit is never a worse choice: it gives at least as much capital as any alternative, which unlocks at least as many future projects.",
               "Implementation: sort the projects by capital requirement. For up to k rounds, push every project whose requirement is at most the current capital into a max-heap of profits (advancing a pointer through the sorted list), then pop the top and add it to the capital. If the heap is empty, no project is affordable and you stop. The cost is O(n log n + k log n)."],
    time="O((n + k) log n)", space="O(n)",
    solution='''import heapq

def findMaximizedCapital(k, w, profits, capital):
    projects = sorted(zip(capital, profits))
    heap = []
    i = 0
    n = len(projects)
    for _ in range(k):
        while i < n and projects[i][0] <= w:
            heapq.heappush(heap, -projects[i][1])
            i += 1
        if not heap:
            break
        w -= heapq.heappop(heap)
    return w
''',
    tests=[[2, 0, [1, 2, 3], [0, 1, 1]], [3, 0, [1, 2, 3], [0, 1, 2]], [1, 0, [5], [1]], [1, 5, [7], [5]],
           [4, 1, [3, 3, 3], [1, 1, 1]], [2, 0, [0, 0], [0, 0]], [3, 2, [5, 1, 10, 4], [3, 1, 2, 9]],
           [2, 1, [9, 6, 8], [5, 1, 4]], [5, 3, [2, 2], [3, 3]], [10, 0, [1, 2, 3, 4, 5], [0, 1, 3, 6, 10]],
           [1, 100, [1, 50, 20], [1000, 100, 50]], [2, 0, [10, 10, 10], [0, 5, 10]]],
)
_r = rnd(209)
for _k, _n, _cap, _w in ((5000, 5000, 10 ** 9, 10 ** 9), (2500, 5000, 100000, 0), (5000, 5000, 20000, 100),
                         (100, 5000, 10 ** 9, 500)):
    _prof = [_r.randint(0, 10000) for _ in range(_n)]
    _capl = [_r.randint(0, _cap) for _ in range(_n)]
    if _w == 0:
        _capl[0] = 0
    p["tests"].append([_k, _w, _prof, _capl])
# a long chain: each project unlocks the next, so projects must be taken in the right order
_prof = [10000] * 5000
_capl = [i * 10000 for i in range(5000)]
p["tests"].append([5000, 0, _prof, _capl])


def b_ipo(k, w, profits, capital):
    n = len(profits)

    def go(w, used, left):
        best = w
        if left == 0:
            return best
        for i in range(n):
            if not used >> i & 1 and capital[i] <= w:
                best = max(best, go(w + profits[i], used | 1 << i, left - 1))
        return best

    return go(w, 0, k)


def g_ipo(r):
    n = r.randint(1, 6)
    return [r.randint(1, 4), r.randint(0, 4), [r.randint(0, 6) for _ in range(n)], [r.randint(0, 9) for _ in range(n)]]


def v_ipo(tests):
    for t in tests:
        k, w, pr, cp = t["args"]
        assert 1 <= k <= 5000 and 0 <= w <= 10 ** 9
        assert len(pr) == len(cp) and 1 <= len(pr) <= 5000
        assert all(0 <= x <= 10000 for x in pr) and all(0 <= x <= 10 ** 9 for x in cp)


CHECKS["ipo"] = (b_ipo, g_ipo, "exact")
VALIDATE["ipo"] = v_ipo
