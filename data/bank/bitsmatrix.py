"""Problems: bit manipulation and matrices. See data/lib.py for the registry."""
from collections import Counter

from lib import add, rnd, CHECKS, VALIDATE, gen_arr  # noqa: F401

INT_MIN, INT_MAX = -(2 ** 31), 2 ** 31 - 1

# =============================================================== BIT MANIPULATION

# ---------------------------------------------------------------- counting bits
p = add(
    id="counting-bits-array", title="Counting Bits", diff="Easy", topic="Math & Bit Manipulation",
    fn="countBits", params=[("n", "int")], ret="int[]", cmp="exact",
    desc="<p>Given a non-negative integer <code>n</code>, build an array <code>ans</code> of length <code>n + 1</code> such that <code>ans[i]</code> is the number of <code>1</code> bits in the binary form of <code>i</code>, for every <code>i</code> from <code>0</code> to <code>n</code>.</p><p>Counting every number bit by bit costs O(n log n). Try to fill the whole array in O(n) by reusing answers you have already computed.</p><pre>n = 5  &rarr;  [0, 1, 1, 2, 1, 2]\n(0, 1, 10, 11, 100, 101 in binary)</pre>",
    constraints=["0 &le; n &le; 10,000"],
    hints=["Write the first 8 or so answers out next to the binary numbers and look for a pattern between neighbours.",
           "Shifting a number right by one bit drops its last bit. How does the number of 1 bits of <code>i</code> relate to that of <code>i &gt;&gt; 1</code>?",
           "<code>ans[i] = ans[i &gt;&gt; 1] + (i &amp; 1)</code>. The smaller index is always filled before the larger one, so one left-to-right pass is enough."],
    editorial=["Write <code>i</code> as <code>(i &gt;&gt; 1)</code> followed by one last bit. Every 1 bit of <code>i</code> is either that last bit or a 1 bit of <code>i &gt;&gt; 1</code>, so <code>ans[i] = ans[i &gt;&gt; 1] + (i &amp; 1)</code>. Since <code>i &gt;&gt; 1 &lt; i</code> (for i &ge; 1), the value needed is already in the array when you reach <code>i</code>.",
               "An equivalent recurrence is <code>ans[i] = ans[i &amp; (i - 1)] + 1</code>: clearing the lowest set bit leaves a smaller number with exactly one fewer 1 bit. Both run in O(n) time with only the output array as memory."],
    time="O(n)", space="O(n)",
    solution='''def countBits(n):
    ans = [0] * (n + 1)
    for i in range(1, n + 1):
        ans[i] = ans[i >> 1] + (i & 1)
    return ans
''',
    tests=[[5], [0], [1], [2], [8], [15], [16], [31], [100], [255], [1023], [1024], [4095], [10000]],
)


def b_countbits(n):
    out = []
    for i in range(n + 1):
        x, c = i, 0
        while x:
            x &= x - 1
            c += 1
        out.append(c)
    return out


def v_countbits(tests):
    for t in tests:
        n = t["args"][0]
        assert 0 <= n <= 10000
        assert len(t["expected"]) == n + 1


CHECKS["counting-bits-array"] = (b_countbits, lambda r: [r.randint(0, 80)], "exact")
VALIDATE["counting-bits-array"] = v_countbits

# ---------------------------------------------------------------- power of two
p = add(
    id="power-of-two-check", title="Is It a Power of Two", diff="Easy", topic="Math & Bit Manipulation",
    fn="isPowerOfTwo", params=[("n", "int")], ret="bool", cmp="exact",
    desc="<p>Return <code>true</code> if the integer <code>n</code> can be written as <code>2<sup>k</sup></code> for some integer <code>k &ge; 0</code>, and <code>false</code> otherwise.</p><p>Zero and negative numbers are never powers of two. Try to answer without loops or recursion.</p><pre>n = 16  &rarr;  true\nn = 12  &rarr;  false</pre>",
    constraints=["-2<sup>31</sup> &le; n &le; 2<sup>31</sup> - 1"],
    hints=["Look at the binary form of 1, 2, 4, 8, 16. What do they all have in common?",
           "A power of two has exactly one bit set. What does subtracting 1 do to such a number?",
           "For <code>n &gt; 0</code>, <code>n - 1</code> flips the single 1 bit to 0 and turns every lower bit into 1, so <code>n &amp; (n - 1)</code> is <code>0</code> exactly when n is a power of two."],
    editorial=["A positive power of two has a single 1 bit, for example <code>1000</code>. Subtracting one gives <code>0111</code>, which shares no bit with the original, so <code>n &amp; (n - 1) == 0</code>. For any other positive number the highest set bit survives the subtraction, so the AND is not zero.",
               "Remember to reject <code>n &le; 0</code> first: <code>0 &amp; -1</code> is also zero, and negative numbers in two's complement have many bits set. The check takes constant time. Alternatives such as repeated halving or testing <code>n &amp; -n == n</code> also work."],
    time="O(1)", space="O(1)",
    solution='''def isPowerOfTwo(n):
    return n > 0 and (n & (n - 1)) == 0
''',
    tests=[[16], [12], [1], [0], [2], [3], [-16], [1024], [1023], [2 ** 30], [2 ** 30 + 1], [2 ** 30 - 1], [INT_MAX], [INT_MIN], [-1], [6], [64], [96]],
)


def b_pow2(n):
    p_ = 1
    while p_ < n:
        p_ *= 2
    return p_ == n


def g_pow2(r):
    c = r.randint(0, 3)
    if c == 0:
        return [2 ** r.randint(0, 30)]
    if c == 1:
        return [2 ** r.randint(0, 30) + r.randint(-2, 2)]
    if c == 2:
        return [r.randint(-40, 40)]
    return [r.randint(INT_MIN, INT_MAX)]


def v_pow2(tests):
    for t in tests:
        assert INT_MIN <= t["args"][0] <= INT_MAX


CHECKS["power-of-two-check"] = (b_pow2, g_pow2, "exact")
VALIDATE["power-of-two-check"] = v_pow2

# ---------------------------------------------------------------- single number II (triples)
p = add(
    id="single-number-ii-triple", title="Single Number When Others Come in Threes", diff="Medium", topic="Math & Bit Manipulation",
    fn="singleNumberTriple", params=[("nums", "int[]")], ret="int", cmp="exact",
    desc="<p>In the integer array <code>nums</code>, every value occurs exactly <strong>three</strong> times except for one value that occurs exactly once. Return that value.</p><p>The XOR trick for pairs does not cancel triples, so a new idea is needed. Aim for O(n) time and O(1) extra space.</p><pre>nums = [2, 2, 3, 2]  &rarr;  3\nnums = [7, 1, 7, 7, 1, 1, -4]  &rarr;  -4</pre>",
    constraints=["1 &le; nums.length &le; 10,000 and nums.length mod 3 = 1", "-2<sup>31</sup> &le; nums[i] &le; 2<sup>31</sup> - 1", "Exactly one value appears once; every other value appears exactly three times"],
    hints=["A count map solves it but uses O(n) memory. Think about each of the 32 bit positions on its own.",
           "Look at one bit position across all numbers. The values that appear three times contribute a multiple of 3 to the count of 1s there.",
           "For each bit, count how many numbers have it set and take the count modulo 3. The remainder is the bit of the single value. Mind the sign bit: in a 32-bit signed value, bit 31 being set means subtracting 2<sup>32</sup>."],
    editorial=["Fix a bit position b. Every value that appears three times adds either 0 or 3 to the number of elements having bit b set, so the total modulo 3 equals the bit b of the single value (0 or 1). Do this for all 32 bits and assemble the answer. Because the language integers may be wider than 32 bits, reinterpret bit 31 as the sign: if the assembled number is at least 2<sup>31</sup>, subtract 2<sup>32</sup>.",
               "Counting works in O(32 n). The same idea can be compressed to a pair of integers <code>ones</code> and <code>twos</code> that hold the bits seen once and twice (mod 3): <code>ones = (ones ^ x) &amp; ~twos; twos = (twos ^ x) &amp; ~ones</code>. After all elements, <code>ones</code> is the answer. That is a small finite-state machine run on all 32 bits in parallel."],
    time="O(n)", space="O(1)",
    solution='''def singleNumberTriple(nums):
    result = 0
    for b in range(32):
        total = 0
        for x in nums:
            total += (x >> b) & 1
        if total % 3:
            result |= 1 << b
    if result >= 1 << 31:
        result -= 1 << 32
    return result
''',
    tests=[[[2, 2, 3, 2]], [[7, 1, 7, 7, 1, 1, -4]], [[5]], [[0, 1, 0, 1, 0, 1, 99]], [[-1, -1, -1, -5]],
           [[INT_MIN, 4, 4, 4]], [[INT_MAX, INT_MIN, INT_MIN, INT_MIN]], [[-3, 8, -3, 8, 8, -3, -9]],
           [[30000, 30000, 1, 30000]], [[0, 0, 0, -1]], [[9, 9, 9, 0]]],
)
_r = rnd(401)
_v = _r.sample(range(-999, 999), 1500)
_a = _v * 3 + [_r.randint(2000, 3000)]; _r.shuffle(_a)
p["tests"].append([_a])
_v = _r.sample(range(INT_MIN, INT_MAX), 3333)
_s = _r.choice([-1, 5, INT_MAX, INT_MIN + 1])
_a = _v * 3 + [_s] if _s not in _v else _v * 3 + [-2]
_r.shuffle(_a)
p["tests"].append([_a])


def b_single3(nums):
    for x in nums:
        if nums.count(x) == 1:
            return x


def g_single3(r):
    v = r.sample(range(-15, 15), r.randint(1, 6))
    a = v * 3
    a.remove(v[0])
    a.remove(v[0])
    r.shuffle(a)
    return a


def v_single3(tests):
    for t in tests:
        nums = t["args"][0]
        assert 1 <= len(nums) <= 10000 and len(nums) % 3 == 1
        c = Counter(nums)
        assert sorted(c.values()).count(1) == 1 and all(v in (1, 3) for v in c.values())


CHECKS["single-number-ii-triple"] = (b_single3, lambda r: [g_single3(r)], "exact")
VALIDATE["single-number-ii-triple"] = v_single3

# ---------------------------------------------------------------- single number III (two singles)
p = add(
    id="single-number-iii-pair", title="Two Values That Appear Once", diff="Medium", topic="Math & Bit Manipulation",
    fn="twoSingles", params=[("nums", "int[]")], ret="int[]", cmp="exact",
    desc="<p>In the integer array <code>nums</code>, exactly two values occur once and every other value occurs exactly twice. Return the two single values as an array <code>[a, b]</code> in <strong>ascending</strong> order (<code>a &lt; b</code>).</p><p>Try to use O(n) time and O(1) extra space.</p><pre>nums = [1, 2, 1, 3, 2, 5]  &rarr;  [3, 5]\nnums = [-1, 0]  &rarr;  [-1, 0]</pre>",
    constraints=["2 &le; nums.length &le; 10,000 and nums.length is even", "-2<sup>31</sup> &le; nums[i] &le; 2<sup>31</sup> - 1", "Exactly two values appear once; every other value appears exactly twice"],
    hints=["XOR-ing the whole array cancels all the pairs. What is left?",
           "What remains is <code>a ^ b</code>, which is non-zero because a and b differ. Any bit set in it is a bit where a and b disagree.",
           "Pick one such bit, for example the lowest set bit <code>x &amp; -x</code>. Split the numbers into two groups by whether they have that bit set. a and b land in different groups, each pair stays together, so XOR-ing each group isolates one of them."],
    editorial=["Let <code>x</code> be the XOR of the entire array. Pairs cancel, so <code>x = a ^ b</code>, and since a &ne; b, x has at least one set bit. Take the lowest set bit <code>m = x &amp; -x</code>. Exactly one of a and b has that bit, so splitting the array by <code>num &amp; m</code> puts a and b in different groups, while both copies of every other value land in the same group.",
               "XOR-ing each group then yields one single value per group. Finally return the two values sorted. The whole thing is two passes with O(1) memory. A hash-count solution works too but needs O(n) space."],
    time="O(n)", space="O(1)",
    solution='''def twoSingles(nums):
    x = 0
    for v in nums:
        x ^= v
    low = x & -x
    a = b = 0
    for v in nums:
        if v & low:
            a ^= v
        else:
            b ^= v
    return [a, b] if a < b else [b, a]
''',
    tests=[[[1, 2, 1, 3, 2, 5]], [[-1, 0]], [[0, 1]], [[4, 4, 6, 7]], [[INT_MIN, INT_MAX]], [[3, -3, 10, 10]],
           [[8, 9, 8, 9, 100, 200, 7, 7]], [[-5, -5, -6, -7, -6, 2]], [[1, 1, 2, 2, 3, 3, 4, 5]],
           [[INT_MIN, 1, INT_MIN + 1, 1]], [[INT_MAX, 0, INT_MAX, 5]]],
)
_r = rnd(402)
_v = _r.sample(range(-4999, 5000), 2000)
_a = _v[2:] + _v[2:] + _v[:2]; _r.shuffle(_a)
p["tests"].append([_a])
_v = _r.sample(range(INT_MIN, INT_MAX), 4000)
_a = _v[2:] + _v[2:] + _v[:2]; _r.shuffle(_a)
p["tests"].append([_a])
_v = list(range(0, 3000, 3))
_a = _v[2:] + _v[2:] + _v[:2]; _r.shuffle(_a)
p["tests"].append([_a])


def b_single2(nums):
    return sorted(set(x for x in nums if nums.count(x) == 1))


def g_single2(r):
    v = r.sample(range(-20, 20), r.randint(2, 7))
    a = v[2:] + v[2:] + v[:2]
    r.shuffle(a)
    return a


def v_single2(tests):
    for t in tests:
        nums = t["args"][0]
        assert 2 <= len(nums) <= 10000 and len(nums) % 2 == 0
        c = Counter(nums)
        assert sorted(c.values()).count(1) == 2 and all(v in (1, 2) for v in c.values())
        assert t["expected"][0] < t["expected"][1]


CHECKS["single-number-iii-pair"] = (b_single2, lambda r: [g_single2(r)], "exact")
VALIDATE["single-number-iii-pair"] = v_single2

# ---------------------------------------------------------------- count pairs with xor in range (Hard)
p = add(
    id="count-pairs-xor-in-range", title="Pairs with XOR in a Range", diff="Hard", topic="Math & Bit Manipulation",
    fn="countXorPairs", params=[("nums", "int[]"), ("low", "int"), ("high", "int")], ret="int", cmp="exact",
    desc="<p>Given an integer array <code>nums</code> and two integers <code>low</code> and <code>high</code>, count the pairs of indices <code>i &lt; j</code> for which <code>low &le; (nums[i] XOR nums[j]) &le; high</code>.</p><p>Equal values at different indices count as separate pairs. A double loop is too slow for the largest inputs.</p><pre>nums = [1, 4, 2, 7], low = 2, high = 6  &rarr;  6\nnums = [9, 8, 4, 2, 1], low = 5, high = 14  &rarr;  8</pre>",
    constraints=["1 &le; nums.length &le; 15,000", "0 &le; nums[i] &le; 20,000", "0 &le; low &le; high &le; 20,000"],
    hints=["Counting pairs inside a range is easier as a difference: pairs with XOR &le; high minus pairs with XOR &lt; low. So you need to count pairs with XOR strictly below a limit X.",
           "Process the numbers one by one and store the earlier ones in a binary trie over their bits (highest bit first). A node remembers how many numbers pass through it.",
           "To count earlier numbers v with <code>a ^ v &lt; X</code>, walk down the trie bit by bit. Where X has a 1 bit, every number that keeps the XOR bit at 0 is already smaller, so add that subtree's count, then follow the branch that makes the XOR bit 1. Where X has a 0 bit, you must keep the XOR bit at 0."],
    editorial=["Define <code>f(X)</code> as the number of pairs with <code>nums[i] ^ nums[j] &lt; X</code>. The answer is <code>f(high + 1) - f(low)</code>. Since all values are below 2<sup>15</sup> and X &le; 20,001, 15 bits are enough.",
               "To compute f(X), insert numbers into a binary trie one at a time and before inserting <code>a</code> query how many stored numbers <code>v</code> satisfy <code>a ^ v &lt; X</code>. Walk from bit 14 down to bit 0 keeping the trie node that matches the prefix of <code>a ^ v</code> equal to the prefix of X. At a bit where X has a 1, all stored numbers whose XOR bit is 0 (the child equal to a's bit) are strictly smaller than X: add that child's count, then continue into the other child (XOR bit 1) to stay equal to X. At a bit where X has a 0, continue into the child equal to a's bit. Each query costs 15 steps.",
               "Both limits can be counted in the same pass, giving O(15 n) time and O(15 n) trie memory. The brute force over all pairs is O(n&sup2;), which is about 10<sup>8</sup> operations for the largest input."],
    time="O(n log V)", space="O(n log V)",
    solution='''def countXorPairs(nums, low, high):
    B = 15
    child = [[-1, -1]]
    cnt = [0]
    total_hi = 0
    total_lo = 0
    X_hi = high + 1
    X_lo = low
    for a in nums:
        for X in (X_hi, X_lo):
            node = 0
            res = 0
            for b in range(B - 1, -1, -1):
                ab = (a >> b) & 1
                if (X >> b) & 1:
                    c = child[node][ab]
                    if c != -1:
                        res += cnt[c]
                    node = child[node][ab ^ 1]
                else:
                    node = child[node][ab]
                if node == -1:
                    break
            if X is X_hi:
                total_hi += res
            else:
                total_lo += res
        node = 0
        for b in range(B - 1, -1, -1):
            ab = (a >> b) & 1
            if child[node][ab] == -1:
                child.append([-1, -1])
                cnt.append(0)
                child[node][ab] = len(child) - 1
            node = child[node][ab]
            cnt[node] += 1
    return total_hi - total_lo
''',
    tests=[[[1, 4, 2, 7], 2, 6], [[9, 8, 4, 2, 1], 5, 14], [[5], 0, 0], [[3, 3], 0, 0], [[3, 3], 1, 5], [[0, 0, 0, 0], 0, 0],
           [[1, 2, 3, 4, 5, 6, 7], 0, 20000], [[1, 2, 3, 4, 5, 6, 7], 7, 7], [[20000, 0], 20000, 20000], [[20000, 20000, 20000], 0, 0],
           [[8, 8, 8, 1], 9, 9], [[1, 2, 4, 8, 16, 32], 3, 3], [[16384, 16383, 1, 0], 16383, 16385]],
)
_r = rnd(403)
p["tests"].append([[_r.randint(0, 20000) for _ in range(15000)], 4000, 9000])
p["tests"].append([[_r.randint(0, 20000) for _ in range(12000)], 0, 20000])
p["tests"].append([[_r.randint(0, 31) for _ in range(15000)], 8, 8])
p["tests"].append([[_r.randint(0, 20000) for _ in range(15000)], 20000, 20000])
p["tests"].append([[_r.randint(0, 20000) for _ in range(15000)], 0, 0])


def b_xorpairs(nums, low, high):
    c = 0
    for i in range(len(nums)):
        for j in range(i + 1, len(nums)):
            if low <= (nums[i] ^ nums[j]) <= high:
                c += 1
    return c


def g_xorpairs(r):
    if r.random() < 0.3:
        hi_v = 20000
    else:
        hi_v = r.choice([3, 7, 31])
    n = r.randint(1, 12)
    nums = [r.randint(0, hi_v) for _ in range(n)]
    lo = r.randint(0, min(hi_v + 5, 20000))
    hi = r.randint(lo, min(lo + r.choice([0, 3, 10, hi_v]), 20000))
    return [nums, lo, hi]


def v_xorpairs(tests):
    for t in tests:
        nums, low, high = t["args"]
        assert 1 <= len(nums) <= 15000 and all(0 <= x <= 20000 for x in nums)
        assert 0 <= low <= high <= 20000


CHECKS["count-pairs-xor-in-range"] = (b_xorpairs, g_xorpairs, "exact")
VALIDATE["count-pairs-xor-in-range"] = v_xorpairs

# =============================================================== MATRIX

# ---------------------------------------------------------------- toeplitz
p = add(
    id="toeplitz-matrix-check", title="Constant Diagonals", diff="Easy", topic="Matrix",
    fn="isToeplitz", params=[("matrix", "int[][]")], ret="bool", cmp="exact",
    desc="<p>A matrix is <em>diagonal-constant</em> (a Toeplitz matrix) when every diagonal that runs from the top-left towards the bottom-right holds a single repeated value. Given a <code>rows &times; cols</code> matrix, return <code>true</code> if it has this property and <code>false</code> otherwise.</p><p>Equivalently, <code>matrix[i][j]</code> equals <code>matrix[i + 1][j + 1]</code> whenever both cells exist.</p><pre>[[1, 2, 3, 4],\n [5, 1, 2, 3],\n [9, 5, 1, 2]]  &rarr;  true\n\n[[1, 2],\n [2, 2]]  &rarr;  false</pre>",
    constraints=["1 &le; rows, cols &le; 100", "0 &le; matrix[i][j] &le; 99"],
    hints=["Cells on the same top-left to bottom-right diagonal have the same value of <code>i - j</code>.",
           "You do not need to group diagonals. It is enough to compare neighbouring cells along each diagonal.",
           "Check every cell that has a cell above-left of it: it must equal <code>matrix[i - 1][j - 1]</code>. If all of those comparisons hold, every diagonal is constant."],
    editorial=["Each diagonal is a chain of cells <code>(i, j), (i + 1, j + 1), (i + 2, j + 2), ...</code>. A chain is constant exactly when every consecutive pair is equal, so it is enough to verify <code>matrix[i][j] == matrix[i - 1][j - 1]</code> for all <code>i, j &ge; 1</code>.",
               "That is a single scan over the matrix: O(rows &middot; cols) time and O(1) extra space. A hash map from <code>i - j</code> to the first value seen on that diagonal also works but needs extra memory."],
    time="O(R &middot; C)", space="O(1)",
    solution='''def isToeplitz(matrix):
    for i in range(1, len(matrix)):
        for j in range(1, len(matrix[0])):
            if matrix[i][j] != matrix[i - 1][j - 1]:
                return False
    return True
''',
    tests=[[[[1, 2, 3, 4], [5, 1, 2, 3], [9, 5, 1, 2]]], [[[1, 2], [2, 2]]], [[[7]]], [[[1, 2, 3, 4]]], [[[1], [2], [3]]],
           [[[5, 5], [5, 5]]], [[[1, 2, 3], [4, 1, 2], [7, 4, 9]]], [[[3, 1], [4, 3], [9, 4]]], [[[3, 1], [4, 3], [9, 5]]],
           [[[0, 0, 0], [0, 0, 1]]]],
)
_r = rnd(501)


def _toeplitz(r, rows, cols, vmax=99):
    first = [r.randint(0, vmax) for _ in range(rows + cols - 1)]
    return [[first[j - i + rows - 1] for j in range(cols)] for i in range(rows)]


_m = _toeplitz(_r, 100, 100)
p["tests"].append([_m])
_m2 = [row[:] for row in _m]; _m2[99][99] = (_m2[99][99] + 1) % 100
p["tests"].append([_m2])
_m3 = [row[:] for row in _m]; _m3[1][0] = (_m3[1][0] + 1) % 100
p["tests"].append([_m3])
p["tests"].append([_toeplitz(_r, 1, 100)])
p["tests"].append([_toeplitz(_r, 100, 1)])
p["tests"].append([_toeplitz(_r, 37, 83)])
p["tests"].append([[[_r.randint(0, 99) for _ in range(100)] for _ in range(100)]])


def b_toeplitz(matrix):
    cells = [(i, j) for i in range(len(matrix)) for j in range(len(matrix[0]))]
    for a in cells:
        for b in cells:
            if a[0] - a[1] == b[0] - b[1] and matrix[a[0]][a[1]] != matrix[b[0]][b[1]]:
                return False
    return True


def g_toeplitz(r):
    rows, cols = r.randint(1, 5), r.randint(1, 5)
    m = _toeplitz(r, rows, cols, 3)
    if r.random() < 0.6:
        i, j = r.randrange(rows), r.randrange(cols)
        m[i][j] = r.randint(0, 3)
    return [m]


def v_toeplitz(tests):
    for t in tests:
        m = t["args"][0]
        assert 1 <= len(m) <= 100 and all(len(row) == len(m[0]) for row in m) and 1 <= len(m[0]) <= 100
        assert all(0 <= x <= 99 for row in m for x in row)
    assert any(t["expected"] for t in tests) and not all(t["expected"] for t in tests)


CHECKS["toeplitz-matrix-check"] = (b_toeplitz, g_toeplitz, "exact")
VALIDATE["toeplitz-matrix-check"] = v_toeplitz

# ---------------------------------------------------------------- diagonal zigzag
p = add(
    id="diagonal-traverse-flat", title="Diagonal Zigzag Order", diff="Medium", topic="Matrix",
    fn="diagonalOrder", params=[("matrix", "int[][]")], ret="int[]", cmp="exact",
    desc="<p>Read a <code>rows &times; cols</code> matrix along its anti-diagonals (cells with the same <code>row + col</code>) in a zigzag. Start at the top-left cell and move to the right first. The first diagonal has one cell; the second is read from top-right to bottom-left, the third from bottom-left to top-right, and so on, alternating until the bottom-right cell is read.</p><p>Return all values in the order they are visited as a flat array.</p><pre>[[1, 2, 3],\n [4, 5, 6],\n [7, 8, 9]]  &rarr;  [1, 2, 4, 7, 5, 3, 6, 8, 9]\n\n[[1, 2],\n [3, 4]]  &rarr;  [1, 2, 3, 4]</pre>",
    constraints=["1 &le; rows, cols &le; 100", "-1,000 &le; matrix[i][j] &le; 1,000"],
    hints=["Cells on one anti-diagonal share the value <code>d = row + col</code>, and d runs from 0 to <code>rows + cols - 2</code>.",
           "For a given d, the valid rows go from <code>max(0, d - cols + 1)</code> to <code>min(d, rows - 1)</code>; the column is <code>d - row</code>.",
           "Walk each diagonal with rows increasing (that is the down-left direction). For even d the zigzag goes the other way, so reverse that diagonal."],
    editorial=["Group cells by <code>d = i + j</code>. For each d from 0 to <code>rows + cols - 2</code>, the cells are <code>(i, d - i)</code> for <code>i</code> in the range <code>max(0, d - cols + 1) ..= min(d, rows - 1)</code>. Reading them with i increasing goes from top-right to bottom-left, which is the direction of the odd diagonals (d = 1, 3, ...). For even d the direction is bottom-left to top-right, so collect the same cells and reverse them.",
               "Every cell is visited once, so the time is O(rows &middot; cols); the output array is the only extra memory. Simulating the walk with a direction flag and bouncing off the borders also works, but the special cases at the corners are easy to get wrong, while the diagonal-index formulation has none."],
    time="O(R &middot; C)", space="O(1) extra",
    solution='''def diagonalOrder(matrix):
    rows, cols = len(matrix), len(matrix[0])
    out = []
    for d in range(rows + cols - 1):
        lo = max(0, d - cols + 1)
        hi = min(d, rows - 1)
        diag = [matrix[i][d - i] for i in range(lo, hi + 1)]
        if d % 2 == 0:
            diag.reverse()
        out.extend(diag)
    return out
''',
    tests=[[[[1, 2, 3], [4, 5, 6], [7, 8, 9]]], [[[1, 2], [3, 4]]], [[[5]]], [[[1, 2, 3, 4]]], [[[1], [2], [3], [4]]],
           [[[1, 2, 3, 4], [5, 6, 7, 8]]], [[[1, 2], [3, 4], [5, 6], [7, 8]]], [[[-1, 0, 1], [2, -2, 3]]],
           [[[1, 2, 3, 4, 5], [6, 7, 8, 9, 10], [11, 12, 13, 14, 15], [16, 17, 18, 19, 20]]],
           [[[1, 2, 3], [4, 5, 6], [7, 8, 9], [10, 11, 12], [13, 14, 15]]]],
)
_r = rnd(502)
for _rc in [(100, 100), (1, 100), (100, 1), (57, 13), (13, 57), (99, 100)]:
    p["tests"].append([[[_r.randint(-1000, 1000) for _ in range(_rc[1])] for _ in range(_rc[0])]])


def b_diag(matrix):
    m, n = len(matrix), len(matrix[0])
    i = j = 0
    up = True
    out = []
    for _ in range(m * n):
        out.append(matrix[i][j])
        if up:
            if j == n - 1:
                i += 1
                up = False
            elif i == 0:
                j += 1
                up = False
            else:
                i -= 1
                j += 1
        else:
            if i == m - 1:
                j += 1
                up = True
            elif j == 0:
                i += 1
                up = True
            else:
                i += 1
                j -= 1
    return out


def g_diag(r):
    rows, cols = r.randint(1, 6), r.randint(1, 6)
    return [[[r.randint(-9, 9) for _ in range(cols)] for _ in range(rows)]]


def v_diag(tests):
    for t in tests:
        m = t["args"][0]
        assert 1 <= len(m) <= 100 and 1 <= len(m[0]) <= 100 and all(len(row) == len(m[0]) for row in m)
        assert all(-1000 <= x <= 1000 for row in m for x in row)
        assert len(t["expected"]) == len(m) * len(m[0])


CHECKS["diagonal-traverse-flat"] = (b_diag, g_diag, "exact")
VALIDATE["diagonal-traverse-flat"] = v_diag

# ---------------------------------------------------------------- game of life
p = add(
    id="game-of-life-next-generation", title="Cell Colony Next Generation", diff="Medium", topic="Matrix",
    fn="nextGeneration", params=[("board", "int[][]")], ret="int[][]", cmp="exact",
    desc="<p>A <code>rows &times; cols</code> board holds <code>1</code> for a live cell and <code>0</code> for a dead one. Each cell has up to eight neighbours (horizontal, vertical and diagonal). All cells update <strong>at the same time</strong> using these rules:</p><ul><li>A live cell with fewer than 2 live neighbours dies.</li><li>A live cell with 2 or 3 live neighbours stays alive.</li><li>A live cell with more than 3 live neighbours dies.</li><li>A dead cell with exactly 3 live neighbours becomes alive.</li></ul><p>Return the board after one update. Cells outside the board count as dead.</p><pre>[[0, 1, 0],\n [0, 1, 0],\n [0, 1, 0]]  &rarr;  [[0, 0, 0], [1, 1, 1], [0, 0, 0]]</pre>",
    constraints=["1 &le; rows, cols &le; 50", "board[i][j] is 0 or 1"],
    hints=["The new state of a cell depends only on the <em>old</em> states of its neighbours, so you must not overwrite cells while you are still reading them.",
           "Simplest: write the result into a new board. For each cell, count live neighbours by checking the 8 offsets and skipping those outside the board.",
           "Apply the rules to the old board only: new value is 1 if (old is 1 and count is 2 or 3) or (old is 0 and count is 3), otherwise 0."],
    editorial=["Allocate a result board of the same size. For every cell, count the live neighbours among the 8 surrounding positions in the original board, ignoring positions outside the grid. Then the new value is 1 exactly when the count is 3, or when the cell is currently alive and the count is 2.",
               "That takes O(rows &middot; cols) time with 8 checks per cell. To work in place you can store the next state in the second bit of each cell (for example 2 meaning &quot;was dead, will live&quot;) and shift everything down in a final pass, but copying to a fresh board is simpler and less error-prone."],
    time="O(R &middot; C)", space="O(R &middot; C)",
    solution='''def nextGeneration(board):
    rows, cols = len(board), len(board[0])
    res = [[0] * cols for _ in range(rows)]
    for i in range(rows):
        for j in range(cols):
            live = 0
            for di in (-1, 0, 1):
                for dj in (-1, 0, 1):
                    if di == 0 and dj == 0:
                        continue
                    a, b = i + di, j + dj
                    if 0 <= a < rows and 0 <= b < cols:
                        live += board[a][b]
            if live == 3 or (board[i][j] == 1 and live == 2):
                res[i][j] = 1
    return res
''',
    tests=[[[[0, 1, 0], [0, 1, 0], [0, 1, 0]]], [[[1, 1], [1, 1]]], [[[1]]], [[[0]]], [[[1, 0, 1, 0, 1]]], [[[1], [1], [1]]],
           [[[0, 1, 0, 0], [0, 0, 1, 0], [1, 1, 1, 0], [0, 0, 0, 0]]], [[[1, 1, 1], [1, 1, 1], [1, 1, 1]]],
           [[[0, 0, 0], [0, 1, 0], [0, 0, 0]]], [[[1, 1, 0], [1, 0, 0], [0, 0, 1]]]],
)
_r = rnd(503)
p["tests"].append([[[1] * 50 for _ in range(50)]])
p["tests"].append([[[1 if _r.random() < 0.4 else 0 for _ in range(50)] for _ in range(50)]])
p["tests"].append([[[1 if _r.random() < 0.25 else 0 for _ in range(50)] for _ in range(50)]])
p["tests"].append([[[1 if _r.random() < 0.5 else 0 for _ in range(7)] for _ in range(50)]])
p["tests"].append([[[1 if _r.random() < 0.5 else 0 for _ in range(50)] for _ in range(3)]])


def b_life(board):
    live = {(i, j) for i, row in enumerate(board) for j, v in enumerate(row) if v == 1}
    near = Counter()
    for (i, j) in live:
        for di in (-1, 0, 1):
            for dj in (-1, 0, 1):
                if (di, dj) != (0, 0):
                    near[(i + di, j + dj)] += 1
    rows, cols = len(board), len(board[0])
    new = {c for c, k in near.items() if (k == 3 or (k == 2 and c in live)) and 0 <= c[0] < rows and 0 <= c[1] < cols}
    return [[1 if (i, j) in new else 0 for j in range(cols)] for i in range(rows)]


def g_life(r):
    rows, cols = r.randint(1, 6), r.randint(1, 6)
    d = r.choice([0.2, 0.4, 0.6])
    return [[[1 if r.random() < d else 0 for _ in range(cols)] for _ in range(rows)]]


def v_life(tests):
    for t in tests:
        b = t["args"][0]
        assert 1 <= len(b) <= 50 and 1 <= len(b[0]) <= 50 and all(len(row) == len(b[0]) for row in b)
        assert all(x in (0, 1) for row in b for x in row)


CHECKS["game-of-life-next-generation"] = (b_life, g_life, "exact")
VALIDATE["game-of-life-next-generation"] = v_life

# ---------------------------------------------------------------- valid sudoku
p = add(
    id="valid-sudoku-board", title="Check a Sudoku Board", diff="Medium", topic="Matrix",
    fn="isValidSudoku", params=[("board", "int[][]")], ret="bool", cmp="exact",
    desc="<p>A partially filled 9 &times; 9 Sudoku board is given as a matrix where <code>0</code> means an empty cell and <code>1</code> to <code>9</code> are filled digits.</p><p>Return <code>true</code> if no digit is repeated within any row, any column or any of the nine 3 &times; 3 boxes (the boxes start at rows and columns 0, 3 and 6). Only the filled cells are checked: the board does <strong>not</strong> need to be solvable, it just must not contain a visible conflict.</p>",
    constraints=["board is exactly 9 &times; 9", "0 &le; board[i][j] &le; 9, where 0 marks an empty cell"],
    hints=["There are three kinds of groups to check: 9 rows, 9 columns, and 9 boxes. Each group must hold no filled digit twice.",
           "Walk through the board once and remember, for each row, column and box, which digits you have already seen.",
           "The box of cell <code>(r, c)</code> has index <code>(r // 3) * 3 + c // 3</code>. If a digit is already in the row set, column set or box set, return false."],
    editorial=["Keep 27 sets (or three 9&times;9 boolean tables): one for each row, each column and each box. Scan the board; for every non-zero digit <code>d</code> at <code>(r, c)</code> compute <code>b = (r // 3) * 3 + c // 3</code>. If <code>d</code> is already in <code>rows[r]</code>, <code>cols[c]</code> or <code>boxes[b]</code>, there is a conflict; otherwise insert it into all three.",
               "The board has a fixed size of 81 cells, so the work is constant. The exercise is about indexing: the box index formula and remembering to skip the zeros, which are not digits. A valid result does not mean the puzzle has a solution."],
    time="O(1)", space="O(1)",
    solution='''def isValidSudoku(board):
    rows = [set() for _ in range(9)]
    cols = [set() for _ in range(9)]
    boxes = [set() for _ in range(9)]
    for r in range(9):
        for c in range(9):
            d = board[r][c]
            if d == 0:
                continue
            b = (r // 3) * 3 + c // 3
            if d in rows[r] or d in cols[c] or d in boxes[b]:
                return False
            rows[r].add(d)
            cols[c].add(d)
            boxes[b].add(d)
    return True
''',
    tests=[],
)


def _sud_full(perm):
    return [[perm[(3 * (r % 3) + r // 3 + c) % 9] for c in range(9)] for r in range(9)]


def _sud_blank(r, grid, keep):
    return [[v if r.random() < keep else 0 for v in row] for row in grid]


_r = rnd(504)
_ident = list(range(1, 10))
_full = _sud_full(_ident)
_partial = [[5, 3, 0, 0, 7, 0, 0, 0, 0], [6, 0, 0, 1, 9, 5, 0, 0, 0], [0, 9, 8, 0, 0, 0, 0, 6, 0],
            [8, 0, 0, 0, 6, 0, 0, 0, 3], [4, 0, 0, 8, 0, 3, 0, 0, 1], [7, 0, 0, 0, 2, 0, 0, 0, 6],
            [0, 6, 0, 0, 0, 0, 2, 8, 0], [0, 0, 0, 4, 1, 9, 0, 0, 5], [0, 0, 0, 0, 8, 0, 0, 7, 9]]
_bad_box = [row[:] for row in _partial]; _bad_box[2][2] = 0; _bad_box[0][2] = 8; _bad_box[2][2] = 8  # row 0: 5 3 8; box has 8 twice
_bad_row = [row[:] for row in _partial]; _bad_row[0][8] = 5
_bad_col = [row[:] for row in _partial]; _bad_col[8][0] = 5
_bad_col2 = [row[:] for row in _partial]; _bad_col2[4][0] = 6  # 6 repeats in column 0 (rows 1 and 4), different boxes, rows
_bad_only_box = [[0] * 9 for _ in range(9)]; _bad_only_box[3][3] = 4; _bad_only_box[5][5] = 4
_dup_far = [[0] * 9 for _ in range(9)]; _dup_far[0][0] = 9; _dup_far[8][8] = 9  # same digit, no shared unit
_full_bad = [row[:] for row in _full]; _full_bad[4][4], _full_bad[4][5] = _full_bad[4][5], _full_bad[4][4]
_perm = _ident[:]; _r.shuffle(_perm)
_full2 = _sud_full(_perm)
p["tests"].extend([
    [_partial], [_bad_box], [[[0] * 9 for _ in range(9)]], [_full], [_bad_row], [_bad_col], [_bad_col2], [_bad_only_box],
    [_dup_far], [_full_bad], [_full2], [_sud_blank(_r, _full2, 0.5)], [_sud_blank(_r, _full2, 0.3)],
])
_g = _sud_blank(_r, _full2, 0.6); _g[7][2] = _g[7][5] if _g[7][5] else 1
_g = [row[:] for row in _g]
p["tests"].append([_g])
_g2 = _sud_blank(_r, _full, 0.6)
p["tests"].append([_g2])


def b_sudoku(board):
    cells = [(r, c) for r in range(9) for c in range(9) if board[r][c] != 0]
    for x in range(len(cells)):
        for y in range(x + 1, len(cells)):
            (r1, c1), (r2, c2) = cells[x], cells[y]
            if board[r1][c1] != board[r2][c2]:
                continue
            if r1 == r2 or c1 == c2 or (r1 // 3 == r2 // 3 and c1 // 3 == c2 // 3):
                return False
    return True


def g_sudoku(r):
    perm = _ident[:]
    r.shuffle(perm)
    g = _sud_blank(r, _sud_full(perm), r.choice([0.2, 0.5, 0.8]))
    k = r.choice([0, 0, 1, 2])
    for _ in range(k):
        g[r.randrange(9)][r.randrange(9)] = r.randint(0, 9)
    return [g]


def v_sudoku(tests):
    for t in tests:
        b = t["args"][0]
        assert len(b) == 9 and all(len(row) == 9 for row in b)
        assert all(0 <= x <= 9 for row in b for x in row)
    assert any(t["expected"] for t in tests) and not all(t["expected"] for t in tests)


CHECKS["valid-sudoku-board"] = (b_sudoku, g_sudoku, "exact")
VALIDATE["valid-sudoku-board"] = v_sudoku

# ---------------------------------------------------------------- max sum submatrix <= k (Hard)
p = add(
    id="max-sum-submatrix-at-most-k", title="Largest Rectangle Sum Not Above K", diff="Hard", topic="Matrix",
    fn="maxSumSubmatrix", params=[("matrix", "int[][]"), ("k", "int")], ret="int", cmp="exact",
    desc="<p>Given a <code>rows &times; cols</code> matrix of integers (which may be negative) and an integer <code>k</code>, consider every rectangular block of cells made of consecutive rows and consecutive columns. Return the largest block sum that is <strong>not greater than</strong> <code>k</code>.</p><p>It is guaranteed that at least one block has a sum of at most <code>k</code>, so an answer always exists. Checking every rectangle with prefix sums is O(rows&sup2; &middot; cols&sup2;); aim for something closer to O(rows&sup2; &middot; cols &middot; log cols).</p><pre>matrix = [[1, 0, 1], [0, -2, 3]], k = 2  &rarr;  2\n(the block [[0, 1], [-2, 3]] sums to 2)\n\nmatrix = [[2, 2, -1]], k = 3  &rarr;  3</pre>",
    constraints=["1 &le; rows, cols &le; 100", "-100 &le; matrix[i][j] &le; 100", "min(matrix) &le; k &le; 100,000, so at least one block has sum &le; k"],
    hints=["Fix a pair of rows (top and bottom). Squash everything between them into one array of column sums. The problem becomes one-dimensional.",
           "In 1D: the best subarray ending at position j with sum &le; k needs a previous prefix sum <code>p</code> with <code>cur - p &le; k</code>, and you want the smallest such p (so that <code>cur - p</code> is as large as possible).",
           "Keep the earlier prefix sums in a sorted list. For the current prefix <code>cur</code> binary-search the first element &ge; <code>cur - k</code>, update the best answer with <code>cur - that</code>, then insert <code>cur</code> into the list. Loop over row pairs on the smaller dimension to keep the cost down."],
    editorial=["Choose the top row and the bottom row of the rectangle, and let <code>col[j]</code> be the sum of column j between them; adding a new bottom row just adds that row to <code>col</code>. A rectangle with those rows corresponds to a subarray of <code>col</code>, so the task becomes: find the maximum subarray sum not exceeding k in a 1D array.",
               "For the 1D part, keep a sorted list of prefix sums seen so far (starting with 0). When the running prefix sum is <code>cur</code>, a subarray ending here has sum <code>cur - p</code> for each earlier prefix p, and we need <code>cur - p &le; k</code>, i.e. <code>p &ge; cur - k</code>. The best choice is the smallest p satisfying that, found by binary search (<code>bisect_left</code>). Then insert <code>cur</code> into the sorted list.",
               "The total is O(R&sup2; &middot; C log C) comparisons, plus the cost of list insertions. Choose the dimension that is smaller for the pair-of-lines loop (transpose when rows &gt; cols) to minimise the multiplied factor. If any 1D result equals k exactly, you can stop at once because nothing can beat k."],
    time="O(min(R,C)&sup2; &middot; max(R,C) log max(R,C))", space="O(max(R,C))",
    solution='''from bisect import bisect_left, insort


def maxSumSubmatrix(matrix, k):
    m, n = len(matrix), len(matrix[0])
    if m > n:
        matrix = [list(col) for col in zip(*matrix)]
        m, n = n, m
    best = None
    for top in range(m):
        col = [0] * n
        for bottom in range(top, m):
            row = matrix[bottom]
            for j in range(n):
                col[j] += row[j]
            pre = [0]
            cur = 0
            for x in col:
                cur += x
                idx = bisect_left(pre, cur - k)
                if idx < len(pre):
                    s = cur - pre[idx]
                    if best is None or s > best:
                        best = s
                        if best == k:
                            return best
                insort(pre, cur)
    return best
''',
    tests=[[[[1, 0, 1], [0, -2, 3]], 2], [[[2, 2, -1]], 3], [[[5]], 5], [[[5]], 10], [[[-7]], -7], [[[-7]], 0], [[[4, 5], [6, 7]], 4],
           [[[4, 5], [6, 7]], 20], [[[4, 5], [6, 7]], 9], [[[-1, -2], [-3, -4]], -3], [[[-1, -2], [-3, -4]], -1],
           [[[1, 2, 3, 4, 5]], 7], [[[1], [2], [3], [4], [5]], 7], [[[3, -3, 3], [-3, 3, -3], [3, -3, 3]], 2]],
)
_r = rnd(505)
p["tests"].append([[[_r.randint(-100, 100) for _ in range(100)] for _ in range(100)], 37])
p["tests"].append([[[_r.randint(-100, 100) for _ in range(100)] for _ in range(100)], 5000])
p["tests"].append([[[_r.randint(1, 100) for _ in range(100)] for _ in range(100)], 99])
p["tests"].append([[[_r.randint(-100, 100) for _ in range(100)] for _ in range(30)], 123])
p["tests"].append([[[_r.randint(-100, 100) for _ in range(30)] for _ in range(100)], 123])


def b_maxsub(matrix, k):
    m, n = len(matrix), len(matrix[0])
    pre = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(m):
        for j in range(n):
            pre[i + 1][j + 1] = matrix[i][j] + pre[i][j + 1] + pre[i + 1][j] - pre[i][j]
    best = None
    for r1 in range(m):
        for r2 in range(r1 + 1, m + 1):
            for c1 in range(n):
                for c2 in range(c1 + 1, n + 1):
                    s = pre[r2][c2] - pre[r1][c2] - pre[r2][c1] + pre[r1][c1]
                    if s <= k and (best is None or s > best):
                        best = s
    return best


def g_maxsub(r):
    rows, cols = r.randint(1, 5), r.randint(1, 5)
    m = [[r.randint(-8, 8) for _ in range(cols)] for _ in range(rows)]
    lo = min(min(row) for row in m)
    return [m, r.randint(lo, lo + r.choice([2, 8, 30]))]


def v_maxsub(tests):
    for t in tests:
        m, k = t["args"]
        assert 1 <= len(m) <= 100 and 1 <= len(m[0]) <= 100 and all(len(row) == len(m[0]) for row in m)
        assert all(-100 <= x <= 100 for row in m for x in row)
        assert min(min(row) for row in m) <= k <= 100000
        assert t["expected"] is not None and t["expected"] <= k


CHECKS["max-sum-submatrix-at-most-k"] = (b_maxsub, g_maxsub, "exact")
VALIDATE["max-sum-submatrix-at-most-k"] = v_maxsub
