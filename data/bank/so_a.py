"""Problems: sorting with custom orderings (keys, digit arrangements, bit based orders). See data/lib.py for the registry."""
from fractions import Fraction
from itertools import permutations
from math import comb

from lib import add, rnd, CHECKS, VALIDATE, gen_arr  # noqa: F401

T = "Sorting"
INT_MAX = 2 ** 31 - 1


def _pop(x):
    c = 0
    while x:
        c += x & 1
        x >>= 1
    return c


# ---------------------------------------------------------------- EASY

p = add(
    id="sort-integers-by-set-bits", title="Sort Integers by Set Bits", diff="Easy", topic=T,
    fn="sortBySetBits", params=[("nums", "int[]")], ret="int[]", cmp="exact",
    desc="<p>The number of <em>set bits</em> of a non-negative integer is the number of <code>1</code> digits in its binary representation. For example, <code>7 = 111</code> has three set bits and <code>8 = 1000</code> has one.</p><p>Return the array <code>nums</code> sorted by number of set bits in ascending order. Numbers with the same number of set bits are ordered by value, smaller first.</p><p>Example: <code>nums = [7, 8, 3, 1]</code> has set-bit counts <code>3, 1, 2, 1</code>, so the answer is <code>[1, 8, 3, 7]</code>.</p>",
    constraints=["0 &le; nums.length &le; 5,000", "0 &le; nums[i] &le; 1,000,000,000"],
    hints=["Every number has a sort key that is not the number itself. What is it?",
           "Count the set bits of x with a loop: add <code>x &amp; 1</code>, then shift <code>x</code> right by one, until x is zero.",
           "Sort with the pair <code>(bit count, value)</code> as the key, so equal bit counts fall back to the value."],
    editorial=["The order is defined by two keys: first the population count, then the value itself. Compute the population count of each number by repeatedly adding the lowest bit and shifting (at most 30 steps for values up to 10<sup>9</sup>), or by Kernighan's trick <code>x &amp;= x - 1</code> which runs once per set bit.",
               "Sort by the tuple <code>(count, value)</code>. Since tuples compare element by element, the value only matters when the counts are equal. Sorting costs O(n log n) and computing all keys O(n log V) for the largest value V."],
    time="O(n log n)", space="O(n)",
    solution='''def sortBySetBits(nums):
    def bits(x):
        c = 0
        while x:
            x &= x - 1
            c += 1
        return c
    return sorted(nums, key=lambda x: (bits(x), x))
''',
    tests=[[[7, 8, 3, 1]], [[]], [[0]], [[0, 1, 2, 3, 4, 5, 6, 7, 8]], [[5, 5, 3, 3, 6]], [[1000000000, 536870912, 1, 2]],
           [[1023, 1024, 1025, 511]], [[0, 0, 0]], [[15, 23, 27, 29, 30, 31]], [[9, 10, 12, 3, 5, 6]]],
)
_r = rnd(9101)
p["tests"].append([[_r.randint(0, 100000) for _ in range(4000)]])
p["tests"].append([[_r.randint(0, 1000000000) for _ in range(1500)]])


def b_setbits(nums):
    a = list(nums)
    for i in range(1, len(a)):  # insertion sort with an explicit comparison
        j = i
        while j > 0:
            x, y = a[j - 1], a[j]
            cx, cy = bin(x).count("1"), bin(y).count("1")
            if (cx, x) > (cy, y):
                a[j - 1], a[j] = y, x
                j -= 1
            else:
                break
    return a


def v_setbits(tests):
    for t in tests:
        nums = t["args"][0]
        assert len(nums) <= 5000 and all(0 <= x <= 10 ** 9 for x in nums)


CHECKS["sort-integers-by-set-bits"] = (b_setbits, lambda r: [gen_arr(r, 0, 70, 0, 10)], "exact")
VALIDATE["sort-integers-by-set-bits"] = v_setbits

p = add(
    id="sort-by-digit-sum-then-value", title="Sort by Digit Sum, Then Larger First", diff="Easy", topic=T, tier="extra",
    fn="sortByDigitSum", params=[("nums", "int[]")], ret="int[]", cmp="exact",
    desc="<p>The <em>digit sum</em> of an integer is the sum of the decimal digits of its absolute value, so the digit sum of <code>-23</code> is <code>5</code> and that of <code>100</code> is <code>1</code>.</p><p>Return <code>nums</code> sorted by digit sum in ascending order. Numbers with equal digit sums are ordered by value from <strong>largest to smallest</strong>.</p><p>Example: <code>nums = [19, 100, 5, -23, 41]</code> has digit sums <code>10, 1, 5, 5, 5</code>. The number 100 comes first, then <code>41, 5, -23</code> (digit sum 5, larger first), and finally 19. The answer is <code>[100, 41, 5, -23, 19]</code>.</p>",
    constraints=["0 &le; nums.length &le; 5,000", "-1,000,000,000 &le; nums[i] &le; 1,000,000,000"],
    hints=["Define a function that turns a number into its digit sum, ignoring the sign.",
           "The primary key is ascending, the tie-break is descending. A single sort key can mix both directions.",
           "Use the key <code>(digitSum(|x|), -x)</code>: negating the value turns the descending tie-break into an ascending one."],
    editorial=["Compute the digit sum of <code>|x|</code> by repeatedly taking <code>x % 10</code> and dividing by ten. The required order is: smaller digit sum first, and among equal digit sums the larger value first.",
               "A key tuple <code>(digitSum, -x)</code> expresses both rules at once because negating the value reverses its direction. The sort costs O(n log n); computing the keys costs O(n) with at most ten digits per number."],
    time="O(n log n)", space="O(n)",
    solution='''def sortByDigitSum(nums):
    def ds(x):
        x = abs(x)
        s = 0
        while x:
            s += x % 10
            x //= 10
        return s
    return sorted(nums, key=lambda x: (ds(x), -x))
''',
    tests=[[[19, 100, 5, -23, 41]], [[]], [[0]], [[-5, 5, 14, -14, 23]], [[10, 1, 100, 1000, 0]], [[999999999, -999999999, 1000000000, 1]],
           [[7, 7, 7]], [[-1, -10, -100, 1, 10]], [[12, 21, 30, 3, -3, -12]]],
)
_r = rnd(9102)
p["tests"].append([[_r.randint(-100000, 100000) for _ in range(4000)]])
p["tests"].append([[_r.randint(-1000000000, 1000000000) for _ in range(1500)]])


def b_digitsum(nums):
    a = list(nums)
    out = []
    while a:
        best = 0
        for i in range(1, len(a)):
            si = sum(int(ch) for ch in str(abs(a[i])))
            sb = sum(int(ch) for ch in str(abs(a[best])))
            if si < sb or (si == sb and a[i] > a[best]):
                best = i
        out.append(a.pop(best))
    return out


def v_digitsum(tests):
    for t in tests:
        nums = t["args"][0]
        assert len(nums) <= 5000 and all(abs(x) <= 10 ** 9 for x in nums)


CHECKS["sort-by-digit-sum-then-value"] = (b_digitsum, lambda r: [gen_arr(r, -60, 60, 0, 10)], "exact")
VALIDATE["sort-by-digit-sum-then-value"] = v_digitsum

p = add(
    id="rank-contestants-by-solved-and-penalty", title="Rank Contestants", diff="Easy", topic=T,
    fn="rankContestants", params=[("contestants", "int[][]")], ret="int[]", cmp="exact",
    desc="<p>Each row of <code>contestants</code> is <code>[id, solved, penalty]</code>: a contestant's unique id, the number of problems they solved and their total time penalty in minutes.</p><p>Contestants are ranked by these rules, in this priority: more solved problems first; then smaller penalty first; then smaller id first. Return the ids in rank order, best contestant first.</p><p>Example: <code>[[1, 3, 50], [2, 3, 40], [3, 4, 100]]</code> gives <code>[3, 2, 1]</code>: contestant 3 solved the most, and contestants 2 and 1 tie on solved problems, so the smaller penalty (40) wins.</p>",
    constraints=["0 &le; contestants.length &le; 5,000", "Each row has exactly 3 values and all ids are distinct", "1 &le; id &le; 1,000,000,000", "0 &le; solved &le; 100", "0 &le; penalty &le; 1,000,000"],
    hints=["You have to order records, not plain numbers. What do you compare, and in which order?",
           "Higher <code>solved</code> is better but lower <code>penalty</code> and lower <code>id</code> are better. The directions differ.",
           "Sort with the key <code>(-solved, penalty, id)</code> and read off the ids."],
    editorial=["This is a multi-key sort. Express each rule as an ascending key: more solved becomes <code>-solved</code>, smaller penalty stays <code>penalty</code>, smaller id stays <code>id</code>. The tuple <code>(-solved, penalty, id)</code> then orders contestants exactly as the statement says, and since ids are distinct there are no complete ties, so the answer is unique.",
               "The sort takes O(n log n) time and O(n) extra space. Counting-style tricks are not needed; the point of the exercise is writing the key with mixed directions correctly."],
    time="O(n log n)", space="O(n)",
    solution='''def rankContestants(contests):
    ranked = sorted(contests, key=lambda c: (-c[1], c[2], c[0]))
    return [c[0] for c in ranked]
''',
    tests=[[[[1, 3, 50], [2, 3, 40], [3, 4, 100]]], [[]], [[[9, 0, 0]]], [[[5, 2, 10], [4, 2, 10], [6, 2, 10]]],
           [[[1, 0, 0], [2, 0, 0], [3, 1, 1000000]]], [[[1000000000, 100, 0], [1, 100, 0]]],
           [[[10, 5, 300], [20, 5, 299], [30, 6, 900], [40, 5, 300], [50, 6, 899]]], [[[3, 1, 5], [2, 2, 5], [1, 3, 5]]],
           [[[7, 4, 20], [8, 4, 21], [9, 3, 1]]]],
)
_r = rnd(9103)
_ids = _r.sample(range(1, 1000000001), 2000)
p["tests"].append([[[i, _r.randint(0, 100), _r.randint(0, 1000000)] for i in _ids]])
_ids = _r.sample(range(1, 3000), 1500)
p["tests"].append([[[i, _r.randint(0, 3), _r.randint(0, 5)] for i in _ids]])


def b_rank(contests):
    n = len(contests)
    out = [None] * n
    for c in contests:
        better = 0
        for d in contests:
            if d[1] > c[1] or (d[1] == c[1] and (d[2] < c[2] or (d[2] == c[2] and d[0] < c[0]))):
                better += 1
        out[better] = c[0]
    return out


def g_rank(r):
    n = r.randint(0, 9)
    ids = r.sample(range(1, 40), n)
    return [[i, r.randint(0, 3), r.randint(0, 3)] for i in ids]


def v_rank(tests):
    for t in tests:
        cs = t["args"][0]
        assert len(cs) <= 5000 and all(len(c) == 3 for c in cs)
        assert len({c[0] for c in cs}) == len(cs)
        assert all(1 <= c[0] <= 10 ** 9 and 0 <= c[1] <= 100 and 0 <= c[2] <= 10 ** 6 for c in cs)


CHECKS["rank-contestants-by-solved-and-penalty"] = (b_rank, lambda r: [g_rank(r)], "exact")
VALIDATE["rank-contestants-by-solved-and-penalty"] = v_rank

# ---------------------------------------------------------------- MEDIUM

p = add(
    id="largest-number-from-array", title="Largest Number from Array", diff="Medium", topic=T, tier="must",
    fn="largestNumberDigits", params=[("nums", "int[]")], ret="int[]", cmp="exact",
    desc="<p>Write the non-negative integers of <code>nums</code> one after another, in any order you like, to form one long decimal number. For example <code>[10, 2]</code> can give <code>102</code> or <code>210</code>.</p><p>Return the digits of the <strong>largest</strong> number that can be formed this way, as an array of digits from the most significant to the least significant. If every element is <code>0</code> the result is the single digit <code>[0]</code> (never a row of zeros).</p><p>Example: <code>nums = [3, 30, 34, 5, 9]</code> gives <code>9534330</code>, so the answer is <code>[9, 5, 3, 4, 3, 3, 0]</code>.</p>",
    constraints=["1 &le; nums.length &le; 3,000", "0 &le; nums[i] &le; 1,000,000,000", "The result can be longer than 32 bits, so it is returned as digits"],
    hints=["Sorting the numbers in descending order does not work: with 3 and 30, which should come first?",
           "For two numbers a and b (as strings), decide the order by comparing the concatenations <code>a + b</code> and <code>b + a</code>.",
           "Sort the strings so that <code>a</code> comes before <code>b</code> whenever <code>a + b &gt; b + a</code>, join them, and handle the all-zero case. This order is consistent (transitive), so a normal sort works."],
    editorial=["Comparing numbers by value or lexicographically both fail: <code>30</code> must come after <code>3</code> because <code>330 &gt; 303</code>, but <code>34</code> must come before <code>3</code> because <code>343 &gt; 334</code>. The correct comparison is pairwise: put <code>a</code> before <code>b</code> exactly when <code>a + b &gt; b + a</code> as strings.",
               "This relation is a strict weak order (it is equivalent to comparing the infinite repetitions <code>aaa...</code> and <code>bbb...</code>), so sorting with it is valid, and an exchange argument shows that any adjacent pair in the wrong order can be swapped to improve the number. After sorting, concatenate. If the first piece is <code>0</code> then all pieces are zeros and the answer is <code>[0]</code>.",
               "The sort needs O(n log n) comparisons and each comparison costs O(L) for strings of length at most L = 10, so the total is O(n log n * L)."],
    time="O(n log n)", space="O(n)",
    solution='''def largestNumberDigits(nums):
    from functools import cmp_to_key
    s = [str(x) for x in nums]
    s.sort(key=cmp_to_key(lambda a, b: -1 if a + b > b + a else (1 if a + b < b + a else 0)))
    if s[0] == "0":
        return [0]
    return [int(ch) for ch in "".join(s)]
''',
    tests=[[[3, 30, 34, 5, 9]], [[10, 2]], [[0]], [[0, 0, 0]], [[1]], [[121, 12]], [[12, 121]], [[824, 8247]], [[0, 9, 0]],
           [[999999999, 99999999, 1000000000]], [[3, 30, 303, 33, 330, 3030]]],
)
_r = rnd(9104)
p["tests"].append([[_r.randint(0, 99999) for _ in range(3000)]])
p["tests"].append([[_r.randint(0, 1000000000) for _ in range(1200)]])
_pool = [3, 30, 34, 303, 330, 343, 3030, 33, 300, 3003, 0, 5, 50, 505]
p["tests"].append([[_r.choice(_pool) for _ in range(2000)]])


def b_largest(nums):
    best = max(int("".join(str(x) for x in perm)) for perm in permutations(nums))
    return [int(ch) for ch in str(best)]


def g_largest(r):
    pool = [0, 1, 2, 3, 5, 9, 10, 12, 30, 34, 121, 12, 33]
    return [r.choice(pool) for _ in range(r.randint(1, 6))]


def v_largest(tests):
    for t in tests:
        nums = t["args"][0]
        assert 1 <= len(nums) <= 3000 and all(0 <= x <= 10 ** 9 for x in nums)
        assert t["expected"][0] != 0 or t["expected"] == [0]


CHECKS["largest-number-from-array"] = (b_largest, lambda r: [g_largest(r)], "exact")
VALIDATE["largest-number-from-array"] = v_largest

p = add(
    id="minimum-sum-of-two-numbers-from-digits", title="Minimum Sum of Two Numbers from Digits", diff="Medium", topic=T, tier="extra",
    fn="minSumFromDigits", params=[("digits", "int[]")], ret="int[]", cmp="exact",
    desc="<p>You are given an array <code>digits</code> of decimal digits. Split <strong>all</strong> of the digits into two non-empty groups and arrange each group in any order to form two decimal numbers. Leading zeros are allowed (for example the group <code>0, 5</code> may be read as <code>05 = 5</code>).</p><p>Return the digits of the <strong>smallest possible sum</strong> of the two numbers, most significant digit first, without leading zeros (the sum zero is returned as <code>[0]</code>). The numbers can be thousands of digits long, so the sum is returned as an array of digits.</p><p>Examples: <code>[1, 2, 3, 4]</code> gives <code>[3, 7]</code> (13 + 24 = 37). <code>[9, 0, 5]</code> gives <code>[1, 4]</code> (05 + 9 = 14).</p>",
    constraints=["2 &le; digits.length &le; 8,000", "0 &le; digits[i] &le; 9"],
    hints=["The sum is a weighted total of the digits: each digit contributes its value times the place value (1, 10, 100, ...) it ends up in. You want small digits in big places.",
           "The two numbers should have lengths that differ by at most one, so the place values come in pairs: two digits per place value (and one place used only once if the count is odd).",
           "Sort the digits. Alternate them between the two numbers, starting with the smallest digit in the highest place of the first number. Then add the two numbers digit by digit with a carry."],
    editorial=["Whatever the split, each digit is multiplied by a power of ten. The best use of the available place values is to give the largest place values to the smallest digits. Making the two numbers as equal in length as possible produces the cheapest multiset of place values: two of each power of ten up to the length of the shorter number, plus one extra top place when the count is odd.",
               "So sort the digits ascending and deal them out alternately: indices 0, 2, 4, ... to the first number and 1, 3, 5, ... to the second, each in the order dealt (most significant first). Within a pair of equal place values it does not matter who gets which digit. The two numbers can have thousands of digits, so add them with schoolbook addition and a carry, working from the least significant end, then strip leading zeros.",
               "Sorting costs O(n log n) (or O(n) with counting sort for digits) and the addition O(n)."],
    time="O(n log n)", space="O(n)",
    solution='''def minSumFromDigits(digits):
    d = sorted(digits)
    a = d[0::2]
    b = d[1::2]
    i, j = len(a) - 1, len(b) - 1
    carry = 0
    out = []
    while i >= 0 or j >= 0 or carry:
        s = carry
        if i >= 0:
            s += a[i]
            i -= 1
        if j >= 0:
            s += b[j]
            j -= 1
        out.append(s % 10)
        carry = s // 10
    while len(out) > 1 and out[-1] == 0:
        out.pop()
    return out[::-1]
''',
    tests=[[[1, 2, 3, 4]], [[9, 0, 5]], [[0, 0]], [[9, 9]], [[5, 5, 5]], [[0, 1]], [[9, 9, 9, 9, 9]], [[3, 1, 4, 1, 5, 9, 2, 6]],
           [[0, 0, 0, 7]], [[8, 8, 8, 1, 1, 1, 0]], [[2, 7]]],
)
_r = rnd(9105)
p["tests"].append([[_r.randint(0, 9) for _ in range(8000)]])
p["tests"].append([[_r.choice([9, 9, 9, 8, 0]) for _ in range(5001)]])
p["tests"].append([[9] * 4000])


def b_minsum(digits):
    n = len(digits)
    best = None
    for perm in set(permutations(digits)):
        for s in range(1, n):
            v = int("".join(map(str, perm[:s]))) + int("".join(map(str, perm[s:])))
            if best is None or v < best:
                best = v
    return [int(ch) for ch in str(best)]


def g_minsum(r):
    return [r.randint(0, 9) for _ in range(r.randint(2, 7))]


def v_minsum(tests):
    for t in tests:
        d = t["args"][0]
        assert 2 <= len(d) <= 8000 and all(0 <= x <= 9 for x in d)
        e = t["expected"]
        assert e[0] != 0 or e == [0]


CHECKS["minimum-sum-of-two-numbers-from-digits"] = (b_minsum, lambda r: [g_minsum(r)], "exact")
VALIDATE["minimum-sum-of-two-numbers-from-digits"] = v_minsum

p = add(
    id="sort-numbers-by-custom-digit-order", title="Sort Numbers by Custom Digit Order", diff="Medium", topic=T,
    fn="sortByDigitOrder", params=[("digitOrder", "int[]"), ("nums", "int[]")], ret="int[]", cmp="exact",
    desc="<p>On a strange planet the digits are ranked differently. <code>digitOrder</code> is a permutation of <code>0..9</code> that lists the digits from the <em>smallest</em> to the <em>largest</em>: <code>digitOrder[0]</code> is the smallest digit, <code>digitOrder[9]</code> the largest.</p><p>Numbers are compared like dictionary words: write each number in ordinary decimal (no leading zeros, <code>0</code> is the single digit <code>0</code>), compare digit by digit using the planet's ranking, and if one number is a prefix of the other, the shorter one is smaller. Return <code>nums</code> sorted in ascending order under this comparison.</p><p>Example: <code>digitOrder = [9, 8, 7, 6, 5, 4, 3, 2, 1, 0]</code> and <code>nums = [5, 45, 4, 50, 95]</code>. Here 9 is the smallest digit and 0 the largest. The number 95 starts with 9 and comes first, then <code>5, 50</code> (5 is a prefix of 50), then <code>4, 45</code>. The answer is <code>[95, 5, 50, 4, 45]</code>.</p>",
    constraints=["digitOrder.length = 10 and it contains each of 0..9 exactly once", "0 &le; nums.length &le; 5,000", "0 &le; nums[i] &le; 1,000,000,000"],
    hints=["Ordinary numeric order does not apply. The numbers behave like strings over an alphabet of ten letters.",
           "First invert the permutation: build <code>rank[d]</code>, the position of digit d in <code>digitOrder</code>.",
           "Use the key <code>[rank[digit] for digit in str(x)]</code>. Lists compare element by element and a proper prefix is smaller, which is exactly the required rule."],
    editorial=["The comparison is a lexicographic comparison over a custom alphabet. Invert the given permutation to get each digit's rank, then replace every number by the list of ranks of its decimal digits. Comparing these lists with the standard lexicographic order (first difference decides, a prefix is smaller) is exactly the planet's rule.",
               "Two different numbers have different digit strings, so the order is total and the answer is unique. Building the keys costs O(n * D) with D at most 10 digits, and sorting costs O(n log n * D) in the worst case."],
    time="O(n log n)", space="O(n)",
    solution='''def sortByDigitOrder(digitOrder, nums):
    rank = [0] * 10
    for i, d in enumerate(digitOrder):
        rank[d] = i
    return sorted(nums, key=lambda x: [rank[int(ch)] for ch in str(x)])
''',
    tests=[[[9, 8, 7, 6, 5, 4, 3, 2, 1, 0], [5, 45, 4, 50, 95]], [[0, 1, 2, 3, 4, 5, 6, 7, 8, 9], [100, 99, 9, 10, 1]],
           [[1, 0, 2, 3, 4, 5, 6, 7, 8, 9], [0, 1, 10, 100]], [[5, 6, 7, 8, 9, 0, 1, 2, 3, 4], []],
           [[5, 6, 7, 8, 9, 0, 1, 2, 3, 4], [7]], [[3, 1, 4, 0, 2, 9, 8, 7, 6, 5], [31, 3, 13, 1, 311, 4, 0, 1000000000]],
           [[0, 1, 2, 3, 4, 5, 6, 7, 8, 9], [10, 100, 1000, 1, 11, 101, 110]], [[9, 0, 1, 2, 3, 4, 5, 6, 7, 8], [0, 9, 90, 8, 80, 89]],
           [[2, 4, 6, 8, 0, 1, 3, 5, 7, 9], [22, 2, 2, 24, 20, 200]], [[4, 3, 2, 1, 0, 5, 6, 7, 8, 9], [123, 12, 321, 32, 1, 3]]],
)
_r = rnd(9106)
_m = list(range(10)); _r.shuffle(_m)
p["tests"].append([_m, [_r.randint(0, 1000000000) for _ in range(2000)]])
_m = list(range(10)); _r.shuffle(_m)
p["tests"].append([_m, [_r.randint(0, 99999) for _ in range(4000)]])
_m = list(range(10)); _r.shuffle(_m)
p["tests"].append([_m, [_r.choice([0, 1, 2, 10, 11, 12, 100, 101, 110, 111, 1000, 1001]) for _ in range(3000)]])


def b_digitorder(order, nums):
    def less(x, y):  # explicit digit by digit comparison
        a, b = str(x), str(y)
        for ca, cb in zip(a, b):
            if ca != cb:
                return order.index(int(ca)) < order.index(int(cb))
        return len(a) < len(b)
    a = list(nums)
    for i in range(1, len(a)):
        j = i
        while j > 0 and less(a[j], a[j - 1]):
            a[j], a[j - 1] = a[j - 1], a[j]
            j -= 1
    return a


def g_digitorder(r):
    order = list(range(10))
    r.shuffle(order)
    return [order, [r.choice([0, 1, 2, 3, 10, 11, 12, 21, 100, 123, 132, 5, 55]) for _ in range(r.randint(0, 9))]]


def v_digitorder(tests):
    for t in tests:
        order, nums = t["args"]
        assert sorted(order) == list(range(10))
        assert len(nums) <= 5000 and all(0 <= x <= 10 ** 9 for x in nums)


CHECKS["sort-numbers-by-custom-digit-order"] = (b_digitorder, g_digitorder, "exact")
VALIDATE["sort-numbers-by-custom-digit-order"] = v_digitorder

p = add(
    id="sort-points-counterclockwise", title="Sort Points Counterclockwise", diff="Medium", topic=T,
    fn="sortCounterclockwise", params=[("points", "int[][]")], ret="int[][]", cmp="exact",
    desc="<p>Each row of <code>points</code> is a point <code>[x, y]</code> in the plane, and no point is the origin <code>(0, 0)</code>. The <em>angle</em> of a point is the counterclockwise angle from the positive x-axis to the ray from the origin through the point, in the half-open range <code>[0, 360)</code> degrees. So <code>(1, 0)</code> has angle 0, <code>(0, 1)</code> has 90, <code>(-1, 0)</code> has 180 and <code>(0, -1)</code> has 270.</p><p>Return the points sorted by angle in ascending order. Points on the same ray from the origin are ordered by distance from the origin, closer first. Equal points may appear several times.</p><p>Example: <code>[[1, 1], [-1, 0], [2, 0], [0, -3], [2, 2], [0, 5]]</code> gives <code>[[2, 0], [1, 1], [2, 2], [0, 5], [-1, 0], [0, -3]]</code>.</p>",
    constraints=["0 &le; points.length &le; 3,000", "Each point has exactly 2 coordinates, -10,000 &le; x, y &le; 10,000", "No point equals (0, 0)"],
    hints=["Sorting by <code>atan2</code> is tempting, but floating point can misorder or tie directions that are very close or exactly equal. Can you compare two directions with integers only?",
           "The cross product <code>ax * by - ay * bx</code> is positive when b is counterclockwise from a (within a half turn). It only works for angles less than 180 degrees apart, so split the plane into two half-planes first.",
           "Half 0 holds points with <code>y &gt; 0</code> or (<code>y == 0</code> and <code>x &gt; 0</code>), half 1 holds the rest. Sort by half, then by the cross product within a half, then by squared distance."],
    editorial=["Avoid floating point: two points have exactly the same direction when their cross product is zero (and they lie on the same side), and <code>atan2</code> may not report that faithfully. Use exact integer arithmetic. Coordinates are at most 10<sup>4</sup>, so cross products stay below 2 * 10<sup>8</sup>.",
               "The cross product tells which of two vectors is counterclockwise of the other only when the angle between them is less than 180 degrees. Therefore classify each point into the half-plane [0, 180) (<code>y &gt; 0</code>, or <code>y == 0 and x &gt; 0</code>) or [180, 360). Order by half first. Inside one half any two points are less than 180 degrees apart, so a comparator returning negative when <code>cross(a, b) &gt; 0</code> is a valid total preorder. For zero cross product (same ray) the closer point, measured by <code>x*x + y*y</code>, goes first.",
               "Sorting with this comparator takes O(n log n) time and O(n) space."],
    time="O(n log n)", space="O(n)",
    solution='''def sortCounterclockwise(points):
    from functools import cmp_to_key

    def half(p):
        return 0 if p[1] > 0 or (p[1] == 0 and p[0] > 0) else 1

    def cmp(a, b):
        ha, hb = half(a), half(b)
        if ha != hb:
            return ha - hb
        cr = a[0] * b[1] - a[1] * b[0]
        if cr > 0:
            return -1
        if cr < 0:
            return 1
        da = a[0] * a[0] + a[1] * a[1]
        db = b[0] * b[0] + b[1] * b[1]
        return (da > db) - (da < db)

    return sorted(points, key=cmp_to_key(cmp))
''',
    tests=[[[[1, 1], [-1, 0], [2, 0], [0, -3], [2, 2], [0, 5]]], [[]], [[[3, 4]]], [[[1, 0], [1, 0], [2, 0]]],
           [[[-1, -1], [1, -1], [-1, 1], [1, 1]]], [[[0, -1], [0, 1], [-1, 0], [1, 0]]],
           [[[10000, 1], [9999, 1], [-10000, -1], [-9999, -1], [10000, -1]]], [[[-2, 0], [-1, 0], [-3, 0], [0, -2], [0, -1]]],
           [[[2, 3], [4, 6], [1, 1], [3, 2], [6, 4], [-2, -3], [-4, -6]]], [[[5, -5], [1, -1], [-1, 1], [-5, 5]]]],
)
_r = rnd(9107)


def _mk_points(n, lim, prim):
    out = []
    while len(out) < n:
        if prim:
            dx, dy = _r.randint(-prim, prim), _r.randint(-prim, prim)
            if (dx, dy) == (0, 0):
                continue
            m = _r.randint(1, lim // max(abs(dx), abs(dy)))
            out.append([dx * m, dy * m])
        else:
            x, y = _r.randint(-lim, lim), _r.randint(-lim, lim)
            if (x, y) != (0, 0):
                out.append([x, y])
    return out


p["tests"].append([_mk_points(2000, 10000, 0)])
p["tests"].append([_mk_points(1200, 10000, 7)])
p["tests"].append([_mk_points(800, 10000, 2)])


def b_ccw(points):
    def key(pt):
        x, y = pt
        if y > 0:
            return (0, 1, -Fraction(x, y), x * x + y * y)
        if y == 0 and x > 0:
            return (0, 0, Fraction(0), x * x)
        if y < 0:
            return (1, 1, -Fraction(x, y), x * x + y * y)
        return (1, 0, Fraction(0), x * x)
    return sorted(points, key=key)


def g_ccw(r):
    out = []
    for _ in range(r.randint(0, 9)):
        pt = [r.randint(-4, 4), r.randint(-4, 4)]
        if pt != [0, 0]:
            out.append(pt)
    return out


def v_ccw(tests):
    for t in tests:
        pts = t["args"][0]
        assert len(pts) <= 3000 and all(len(q) == 2 for q in pts)
        assert all(abs(q[0]) <= 10000 and abs(q[1]) <= 10000 and q != [0, 0] for q in pts)


CHECKS["sort-points-counterclockwise"] = (b_ccw, lambda r: [g_ccw(r)], "exact")
VALIDATE["sort-points-counterclockwise"] = v_ccw

p = add(
    id="sort-by-gray-code-rank", title="Sort by Gray Code Position", diff="Medium", topic=T, tier="extra",
    fn="sortByGrayRank", params=[("nums", "int[]")], ret="int[]", cmp="exact",
    desc="<p>The <em>binary reflected Gray code</em> sequence is <code>g(0), g(1), g(2), ...</code> where <code>g(i) = i XOR (i &gt;&gt; 1)</code>. It starts <code>0, 1, 3, 2, 6, 7, 5, 4, 12, ...</code>: consecutive values differ in exactly one bit, and every non-negative integer appears exactly once. The <em>Gray position</em> of a number x is the index i with <code>g(i) = x</code>, so 3 has position 2 and 4 has position 7.</p><p>Return <code>nums</code> sorted by Gray position in ascending order (the order in which the numbers appear in the Gray code sequence).</p><p>Example: <code>nums = [4, 2, 7, 0]</code> has positions <code>7, 3, 5, 0</code>, so the answer is <code>[0, 2, 7, 4]</code>.</p>",
    constraints=["0 &le; nums.length &le; 5,000", "0 &le; nums[i] &le; 1,000,000,000"],
    hints=["You cannot generate the sequence up to 10<sup>9</sup>. You need the position of x directly, which means inverting <code>g(i) = i XOR (i &gt;&gt; 1)</code>.",
           "Look at the bits from the top. The top bit of i equals the top bit of x, and every next bit of i is the previous bit of i XOR the matching bit of x.",
           "That means bit k of i is the XOR of all bits of x at positions k and above. Compute <code>i = x ^ (x &gt;&gt; 1) ^ (x &gt;&gt; 2) ^ ...</code> and sort by it."],
    editorial=["From <code>x = i ^ (i &gt;&gt; 1)</code> we get, for every bit k, <code>x_k = i_k XOR i_(k+1)</code>. Solving from the top bit downward gives <code>i_k = x_k XOR i_(k+1)</code>, so <code>i_k</code> is the XOR (parity) of the bits of x at positions k, k+1, and so on. All of these bits at once equal <code>x ^ (x &gt;&gt; 1) ^ (x &gt;&gt; 2) ^ ...</code>, which a simple loop computes in at most 30 steps.",
               "Because Gray code is a bijection, different numbers have different positions, so sorting by position is a strict total order. Sort in O(n log n) time with O(n) space for the keys."],
    time="O(n log n)", space="O(n)",
    solution='''def sortByGrayRank(nums):
    def rank(x):
        r = 0
        while x:
            r ^= x
            x >>= 1
        return r
    return sorted(nums, key=rank)
''',
    tests=[[[4, 2, 7, 0]], [[]], [[0]], [[0, 1, 2, 3, 4, 5, 6, 7]], [[7, 7, 1, 1]], [[1000000000, 536870912, 0, 1]],
           [[8, 12, 13, 15, 14, 10, 11, 9]], [[1023, 512, 1, 256]], [[6, 5, 3]], [[2, 2, 2]]],
)
_r = rnd(9108)
p["tests"].append([[_r.randint(0, 100000) for _ in range(4000)]])
p["tests"].append([[_r.randint(0, 1000000000) for _ in range(1500)]])


def b_gray(nums):
    seq = [i ^ (i >> 1) for i in range(1024)]
    pos = {v: i for i, v in enumerate(seq)}
    a = list(nums)
    out = []
    while a:
        best = 0
        for i in range(1, len(a)):
            if pos[a[i]] < pos[a[best]]:
                best = i
        out.append(a.pop(best))
    return out


def v_gray(tests):
    for t in tests:
        nums = t["args"][0]
        assert len(nums) <= 5000 and all(0 <= x <= 10 ** 9 for x in nums)


CHECKS["sort-by-gray-code-rank"] = (b_gray, lambda r: [gen_arr(r, 0, 1000, 0, 10)], "exact")
VALIDATE["sort-by-gray-code-rank"] = v_gray

p = add(
    id="can-sort-by-swapping-equal-bit-counts", title="Sort by Swapping Equal Bit Counts", diff="Medium", topic=T,
    fn="canSortByBitSwaps", params=[("nums", "int[]")], ret="bool", cmp="exact",
    desc="<p>You may swap two <strong>adjacent</strong> elements of <code>nums</code> only when they have the same number of set bits (ones in binary). You may do any number of swaps, including none.</p><p>Return <code>true</code> if the array can be turned into non-decreasing order, otherwise <code>false</code>.</p><p>Examples: <code>[8, 4, 2, 30, 15]</code> has bit counts <code>1, 1, 1, 4, 4</code>; the first three can be sorted among themselves to <code>2, 4, 8</code> and the last two to <code>15, 30</code>, giving <code>[2, 4, 8, 15, 30]</code>, so the answer is <code>true</code>. For <code>[3, 16, 8, 4, 2]</code> the element 3 (two bits) can never pass the 2 (one bit), and 3 &gt; 2, so the answer is <code>false</code>.</p>",
    constraints=["1 &le; nums.length &le; 5,000", "0 &le; nums[i] &le; 1,000,000,000"],
    hints=["Elements with different bit counts can never change their relative order. What does this say about the array's structure?",
           "Cut the array into maximal blocks of consecutive elements with the same bit count. Inside one block any order can be reached by adjacent swaps.",
           "Sort each block mentally: the array is sortable if and only if the maximum of every block is at most the minimum of the next block (equivalently, of all later elements). You only need block minimum and maximum."],
    editorial=["An adjacent swap exchanges two elements with the same set-bit count, so two elements with different counts never cross each other. Split the array into maximal runs of equal bit count. Within a run the swaps are unrestricted, so a run can be rearranged into any order, in particular into sorted order. Elements never move across a run boundary except by staying in their own run.",
               "Therefore the final array is the concatenation of the sorted runs, and it is non-decreasing exactly when the maximum of each run is at most the minimum of the following run. One pass tracking the previous run's maximum and the current run's minimum and maximum decides this in O(n) time and O(1) extra space.",
               "Note that two runs with the same count that are separated by a different run are not merged, which is why comparing consecutive runs is enough."],
    time="O(n)", space="O(1)",
    solution='''def canSortByBitSwaps(nums):
    n = len(nums)
    prev_max = -1
    i = 0
    while i < n:
        c = bin(nums[i]).count("1")
        lo = hi = nums[i]
        j = i + 1
        while j < n and bin(nums[j]).count("1") == c:
            lo = min(lo, nums[j])
            hi = max(hi, nums[j])
            j += 1
        if lo < prev_max:
            return False
        prev_max = hi
        i = j
    return True
''',
    tests=[[[8, 4, 2, 30, 15]], [[3, 16, 8, 4, 2]], [[1]], [[0]], [[1, 2, 3]], [[3, 2, 1]], [[2, 1]], [[5, 3, 6, 9, 10, 12]],
           [[7, 1, 2, 4]], [[1, 2, 4, 8, 3, 5, 6, 7]], [[1000000000, 536870912]], [[0, 0, 1, 1, 0]]],
)
_r = rnd(9109)


def _blocks(nblocks, per, parity_lo=4):
    # consecutive value ranges; popcounts alternate between two classes, so runs are long
    blocks = []
    for k in range(nblocks):
        lo = 4096 + k * 1500
        cand = [x for x in range(lo, lo + 1500) if bin(x).count("1") == (6 if k % 2 == 0 else 7)]
        blocks.append([_r.choice(cand) for _ in range(per)])
    return blocks


_bl = _blocks(8, 500)
_a = []
for _b in _bl:
    _r.shuffle(_b)
    _a += _b
p["tests"].append([_a])
_bl2 = [list(_b) for _b in _bl]
_bl2[2][10], _bl2[5][20] = _bl2[5][20], _bl2[2][10]
p["tests"].append([[x for _b in _bl2 for x in _b]])
_bl3 = _blocks(6, 600)
_bl3[3][0] = min(_bl3[2]) - 1 if bin(min(_bl3[2]) - 1).count("1") == bin(_bl3[3][1]).count("1") else _bl3[3][0]
p["tests"].append([[x for _b in _bl3 for x in _b]])
p["tests"].append([sorted(_r.randint(0, 1000000000) for _ in range(3000))])


def b_bitswaps(nums):
    start = tuple(nums)
    seen = {start}
    stack = [start]
    target = tuple(sorted(nums))
    while stack:
        cur = stack.pop()
        if cur == target:
            return True
        for i in range(len(cur) - 1):
            if bin(cur[i]).count("1") == bin(cur[i + 1]).count("1"):
                nxt = list(cur)
                nxt[i], nxt[i + 1] = nxt[i + 1], nxt[i]
                nxt = tuple(nxt)
                if nxt not in seen:
                    seen.add(nxt)
                    stack.append(nxt)
    return False


def g_bitswaps(r):
    return [r.randint(0, 12) for _ in range(r.randint(1, 7))]


def v_bitswaps(tests):
    for t in tests:
        nums = t["args"][0]
        assert 1 <= len(nums) <= 5000 and all(0 <= x <= 10 ** 9 for x in nums)
    res = [t["expected"] for t in tests]
    assert True in res and False in res


CHECKS["can-sort-by-swapping-equal-bit-counts"] = (b_bitswaps, lambda r: [g_bitswaps(r)], "exact")
VALIDATE["can-sort-by-swapping-equal-bit-counts"] = v_bitswaps

# ---------------------------------------------------------------- HARD

p = add(
    id="largest-multiple-of-three-digits", title="Largest Multiple of Three from Digits", diff="Hard", topic=T,
    fn="largestMultipleOfThree", params=[("digits", "int[]")], ret="int[]", cmp="exact",
    desc="<p>You are given <code>digits</code>, an array of decimal digits (each 0 to 9). Choose any non-empty subset of the digits (each array element can be used at most once), arrange the chosen digits in any order and read them as a decimal number.</p><p>Return the digits (most significant first) of the <strong>largest</strong> number you can form that is divisible by 3. The number must not have leading zeros, so if the only possible value is zero the result is <code>[0]</code>. If no non-empty selection gives a multiple of 3, return the empty array <code>[]</code>.</p><p>Examples: <code>[8, 1, 9]</code> gives <code>[9, 8, 1]</code> (981 = 3 * 327). <code>[8, 6, 7, 1, 0]</code> gives <code>[8, 7, 6, 0]</code> (8760). <code>[1]</code> gives <code>[]</code>. <code>[0, 0]</code> gives <code>[0]</code>.</p>",
    constraints=["1 &le; digits.length &le; 8,000", "0 &le; digits[i] &le; 9"],
    hints=["A number is divisible by 3 exactly when its digit sum is. For a fixed set of digits, the largest arrangement is the digits in descending order.",
           "Start with all digits. If the total sum has remainder r (1 or 2) modulo 3, you must drop some digits to fix it. Which drops lose the least?",
           "Drop the single smallest digit with remainder r; if there is none, drop the two smallest digits with remainder 3 - r. If nothing is left, return []. If the largest remaining digit is 0, return [0]."],
    editorial=["Only the digit sum matters for divisibility, and for a fixed multiset of digits the descending arrangement gives the largest number. Longer numbers beat shorter ones (no leading zeros), so we want to discard as few digits as possible, and the discarded ones should be as small as possible.",
               "Let r = (sum of all digits) mod 3. If r = 0, keep everything. Otherwise either remove one digit whose remainder is r, or, if no such digit exists, remove two digits whose remainder is 3 - r (their sum has remainder r). In both cases remove the smallest candidates. Removing one digit always beats removing two because the number stays longer. If no option exists, or nothing remains, there is no answer.",
               "After removal sort descending. If the first digit is 0, all digits are zeros and the answer is <code>[0]</code>, not a run of zeros. Sorting (or counting sort over 10 values) gives O(n log n) or O(n) time."],
    time="O(n log n)", space="O(n)",
    solution='''def largestMultipleOfThree(digits):
    d = sorted(digits, reverse=True)
    r = sum(d) % 3

    def remove(rem, cnt):
        idx = [i for i in range(len(d) - 1, -1, -1) if d[i] % 3 == rem][:cnt]
        if len(idx) < cnt:
            return False
        for i in sorted(idx, reverse=True):
            del d[i]
        return True

    if r and not remove(r, 1):
        if not remove(3 - r, 2):
            return []
    if not d:
        return []
    if d[0] == 0:
        return [0]
    return d
''',
    tests=[[[8, 1, 9]], [[8, 6, 7, 1, 0]], [[1]], [[0, 0]], [[0]], [[3]], [[2, 2]], [[1, 1, 1, 1]], [[5, 8]], [[9, 9, 9, 0]],
           [[1, 2]], [[4, 4, 0]], [[7, 7, 7, 7, 7]]],
)
_r = rnd(9110)
p["tests"].append([[_r.randint(0, 9) for _ in range(8000)]])
p["tests"].append([[_r.choice([1, 4, 7, 0, 0]) for _ in range(5001)]])
p["tests"].append([[_r.choice([2, 5, 8]) for _ in range(4000)] + [1, 0]])


def b_mult3(digits):
    n = len(digits)
    best = None
    for mask in range(1, 1 << n):
        ch = [digits[i] for i in range(n) if mask >> i & 1]
        if sum(ch) % 3:
            continue
        ch.sort(reverse=True)
        val = int("".join(map(str, ch)))
        if best is None or val > best:
            best = val
    return [] if best is None else [int(c) for c in str(best)]


def g_mult3(r):
    return [r.randint(0, 9) for _ in range(r.randint(1, 9))]


def v_mult3(tests):
    for t in tests:
        d = t["args"][0]
        assert 1 <= len(d) <= 8000 and all(0 <= x <= 9 for x in d)
        e = t["expected"]
        assert sum(e) % 3 == 0 and (not e or e[0] != 0 or e == [0])


CHECKS["largest-multiple-of-three-digits"] = (b_mult3, lambda r: [g_mult3(r)], "exact")
VALIDATE["largest-multiple-of-three-digits"] = v_mult3

p = add(
    id="kth-integer-in-bit-count-order", title="Kth Integer in Bit Count Order", diff="Hard", topic=T, tier="extra",
    fn="kthByBitCount", params=[("n", "int"), ("k", "int")], ret="int", cmp="exact",
    desc="<p>Write the integers <code>1, 2, ..., n</code> in a list sorted by their number of set bits (ones in binary) in ascending order; integers with the same number of set bits are ordered by value, smaller first. Return the <code>k</code>-th element of this list (1-indexed).</p><p>Example: for <code>n = 10</code> the sorted list is <code>1, 2, 4, 8, 3, 5, 6, 9, 10, 7</code> (one set bit, then two, then three). So <code>k = 6</code> gives <code>5</code> and <code>k = 10</code> gives <code>7</code>.</p><p>The value of <code>n</code> is far too large to build and sort the list.</p>",
    constraints=["1 &le; n &le; 1,000,000,000", "1 &le; k &le; n"],
    hints=["Do not sort. Count how many integers in <code>1..n</code> have exactly c set bits, for c = 1, 2, 3, ... and skip whole groups.",
           "To count numbers in <code>[0, x]</code> with exactly c set bits, walk the bits of x from the top: at every set bit you may place a 0 there and choose the remaining bits freely, which gives a binomial coefficient.",
           "First find the group c that contains the k-th element and the rank k' inside the group. Then binary search the smallest x with <code>count(x, c) &ge; k'</code>; the count is monotone in x."],
    editorial=["Let <code>count(x, c)</code> be the number of integers in <code>[0, x]</code> with exactly c set bits. Scan the bits of x from the most significant one. Whenever x has a 1 at position i, every number that has the same higher bits as x but a 0 at position i is smaller than x, and its lower i bits are free, so it contributes <code>C(i, c - ones)</code> where <code>ones</code> is the number of set bits of x above position i. Finally x itself counts if it has exactly c set bits. This takes O(log x) per call.",
               "Because c is at least 1, the integer 0 is never counted. Iterate c = 1, 2, ...: if k is at most <code>count(n, c)</code> the answer has c set bits; otherwise subtract <code>count(n, c)</code> from k and continue. At most 30 groups exist.",
               "Inside the group, the elements are ordered by value, and <code>count(x, c)</code> is non-decreasing in x, so the answer is the smallest x with <code>count(x, c) &ge; k</code> (k now being the rank inside the group), found by binary search over <code>[1, n]</code> in about 30 steps. Total time O(log<sup>2</sup> n), which is tiny."],
    time="O(log^2 n)", space="O(1)",
    solution='''def kthByBitCount(n, k):
    from math import comb

    def count_le(x, c):
        res = 0
        ones = 0
        for i in range(x.bit_length() - 1, -1, -1):
            if x >> i & 1:
                need = c - ones
                if 0 <= need <= i:
                    res += comb(i, need)
                ones += 1
        if ones == c:
            res += 1
        return res

    c = 1
    while True:
        total = count_le(n, c)
        if k <= total:
            break
        k -= total
        c += 1
    lo, hi = 1, n
    while lo < hi:
        mid = (lo + hi) // 2
        if count_le(mid, c) >= k:
            hi = mid
        else:
            lo = mid + 1
    return lo
''',
    tests=[[10, 6], [10, 10], [1, 1], [2, 1], [2, 2], [7, 7], [8, 4], [16, 16], [100, 57], [1000, 1000], [1000, 1],
           [1000000000, 1], [1000000000, 1000000000], [1000000000, 500000000], [536870912, 31], [999999999, 123456789]],
)
_r = rnd(9111)
for _ in range(2):
    _n = _r.randint(10 ** 8, 10 ** 9)
    p["tests"].append([_n, _r.randint(1, _n)])


def b_kbit(n, k):
    order = sorted(range(1, n + 1), key=lambda x: (bin(x).count("1"), x))
    return order[k - 1]


def g_kbit(r):
    n = r.randint(1, 300)
    return [n, r.randint(1, n)]


def v_kbit(tests):
    for t in tests:
        n, k = t["args"]
        assert 1 <= n <= 10 ** 9 and 1 <= k <= n
        assert 1 <= t["expected"] <= n


CHECKS["kth-integer-in-bit-count-order"] = (b_kbit, g_kbit, "exact")
VALIDATE["kth-integer-in-bit-count-order"] = v_kbit
