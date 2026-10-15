"""Problems: arrays & hashing, pair / triple / tuple counting. See data/lib.py for the registry."""
from collections import Counter

from lib import add, rnd, CHECKS, VALIDATE, gen_arr  # noqa: F401

INT_MIN, INT_MAX = -(2 ** 31), 2 ** 31 - 1
MOD = 1_000_000_007
T = "Arrays & Hashing"


# ---------------------------------------------------------------- EASY

p = add(
    id="distinct-pairs-with-target-sum", title="Distinct Pairs with Target Sum", diff="Easy", topic=T,
    fn="countDistinctPairs", params=[("nums", "int[]"), ("target", "int")], ret="int", cmp="exact",
    desc="<p>Given an integer array <code>nums</code> and an integer <code>target</code>, count the <em>distinct value pairs</em> <code>(a, b)</code> with <code>a &le; b</code> and <code>a + b = target</code> such that the array contains <code>a</code> and <code>b</code> at two <em>different</em> positions.</p><p>Two pairs are the same if they hold the same values, no matter where those values sit in the array. If <code>a = b</code>, the value must therefore occur at least twice.</p><p>For example, <code>nums = [1, 1, 2, 45, 46, 46]</code> and <code>target = 47</code> give <code>2</code>, namely <code>(1, 46)</code> and <code>(2, 45)</code>. For <code>nums = [3, 3, 3]</code> and <code>target = 6</code> the answer is <code>1</code>.</p>",
    constraints=["1 &le; nums.length &le; 10,000", "-10<sup>9</sup> &le; nums[i] &le; 10<sup>9</sup>", "-10<sup>9</sup> &le; target &le; 10<sup>9</sup>"],
    hints=["Try every pair of positions and put the value pair into a set. That is O(n<sup>2</sup>), which is too slow for 10,000 elements.",
           "For each distinct value <code>x</code> you only need to know whether <code>target - x</code> exists. A hash map of counts answers that in O(1).",
           "Visit every distinct value <code>x</code>. If <code>target - x &gt; x</code> and it exists, count one pair. If <code>target - x == x</code>, count one pair only when <code>x</code> occurs at least twice. Requiring <code>x &lt; target - x</code> avoids counting a pair twice."],
    editorial=["Count the occurrences of every value in a hash map. A distinct pair is identified by its smaller value <code>x</code> and its partner <code>y = target - x</code>. Loop over the distinct values: if <code>x &lt; y</code>, the pair counts when <code>y</code> is present; if <code>x == y</code>, it counts when <code>x</code> appears at least twice. Pairs with <code>x &gt; y</code> were already seen from the other side, so they are skipped.",
               "The loop touches each distinct value once, giving O(n) time and O(n) space. A sorted array with two pointers also works in O(n log n) with O(1) extra space, but you have to skip repeated values carefully to avoid counting the same pair twice."],
    time="O(n)", space="O(n)",
    solution='''def countDistinctPairs(nums, target):
    cnt = {}
    for x in nums:
        cnt[x] = cnt.get(x, 0) + 1
    ans = 0
    for x, c in cnt.items():
        y = target - x
        if x < y:
            if y in cnt:
                ans += 1
        elif x == y and c >= 2:
            ans += 1
    return ans
''',
    tests=[[[1, 1, 2, 45, 46, 46], 47], [[3, 3, 3], 6], [[1, 5, 5], 6], [[5], 10], [[5, 5], 10], [[1, 2, 3], 100],
           [[0, 0, 0, 0], 0], [[-3, 3, 0, 0, -3, 3], 0], [[5 * 10 ** 8, 5 * 10 ** 8 - 1, 5 * 10 ** 8 + 1, -5], 10 ** 9],
           [[10 ** 9, -10 ** 9, 10 ** 9, -10 ** 9], 0], [[1, 2, 3, 4, 5, 6], 7], [[7, 7, 7, 1, 1], 8]],
)
_r = rnd(3101)
p["tests"].append([[_r.randint(-3000, 3000) for _ in range(10000)], 17])
p["tests"].append([[_r.randint(-10 ** 9, 10 ** 9) for _ in range(3000)], 0])
_v = _r.sample(range(-10 ** 6, 10 ** 6), 3000)
p["tests"].append([_v + [100 - x for x in _v[:2000]] + [50, 50, 50], 100])


def b_distinct_pairs(nums, target):
    s = set()
    for i in range(len(nums)):
        for j in range(i + 1, len(nums)):
            if nums[i] + nums[j] == target:
                s.add((min(nums[i], nums[j]), max(nums[i], nums[j])))
    return len(s)


def g_distinct_pairs(r):
    return [gen_arr(r, -6, 6, 1, 12), r.randint(-8, 8)]


def v_distinct_pairs(tests):
    for t in tests:
        a, tg = t["args"]
        assert 1 <= len(a) <= 10000 and all(-10 ** 9 <= x <= 10 ** 9 for x in a) and -10 ** 9 <= tg <= 10 ** 9


CHECKS["distinct-pairs-with-target-sum"] = (b_distinct_pairs, g_distinct_pairs, "exact")
VALIDATE["distinct-pairs-with-target-sum"] = v_distinct_pairs

p = add(
    id="count-equivalent-domino-pairs", title="Count Equivalent Domino Pairs", diff="Easy", topic=T,
    fn="countDominoPairs", params=[("dominoes", "int[][]")], ret="int", cmp="exact",
    desc="<p>A domino is a pair <code>[a, b]</code>. Two dominoes <code>[a, b]</code> and <code>[c, d]</code> are <em>equivalent</em> if one can be rotated to look like the other, that is, if <code>a = c</code> and <code>b = d</code>, or <code>a = d</code> and <code>b = c</code>.</p><p>Given a list <code>dominoes</code>, count the pairs of positions <code>i &lt; j</code> whose dominoes are equivalent.</p><p>For example, <code>[[1,2],[2,1],[3,4],[5,6]]</code> gives <code>1</code>, and <code>[[1,2],[1,2],[1,1],[1,2],[2,2]]</code> gives <code>3</code> (the three copies of <code>[1,2]</code> form three pairs).</p>",
    constraints=["0 &le; dominoes.length &le; 5,000", "dominoes[i].length = 2", "1 &le; dominoes[i][j] &le; 10<sup>6</sup>"],
    hints=["Comparing every two dominoes works in O(n<sup>2</sup>). Is there a way to give equivalent dominoes the same label?",
           "Normalise each domino so that its smaller value comes first: <code>[a, b]</code> becomes <code>(min(a, b), max(a, b))</code>. Equivalent dominoes now have identical keys.",
           "Count the dominoes per key in a hash map. If a key occurs <code>c</code> times it contributes <code>c * (c - 1) / 2</code> pairs. You can also add the current count each time a key is seen again."],
    editorial=["Rotation only swaps the two numbers, so the unordered pair {a, b} identifies the equivalence class. Storing <code>(min, max)</code> gives a canonical key, and two dominoes are equivalent exactly when their keys are equal.",
               "Walk through the dominoes and, for each one, add the number of earlier dominoes with the same key to the answer, then increment that key's count. A group of <code>c</code> equal dominoes yields 0 + 1 + ... + (c - 1) = c(c - 1)/2 pairs. One pass, O(n) time and space. The answer is at most C(5,000, 2), about 1.25&middot;10<sup>7</sup>."],
    time="O(n)", space="O(n)",
    solution='''def countDominoPairs(dominoes):
    cnt = {}
    ans = 0
    for a, b in dominoes:
        key = (a, b) if a <= b else (b, a)
        c = cnt.get(key, 0)
        ans += c
        cnt[key] = c + 1
    return ans
''',
    tests=[[[[1, 2], [2, 1], [3, 4], [5, 6]]], [[[1, 2], [1, 2], [1, 1], [1, 2], [2, 2]]], [[]], [[[1, 1]]], [[[1, 1], [1, 1]]],
           [[[1, 2], [2, 1]]], [[[1, 2], [3, 4]]], [[[1, 2], [2, 1], [1, 2], [2, 1]]], [[[1000000, 1], [1, 1000000], [1000000, 1000000]]],
           [[[3, 3], [3, 3], [3, 3], [3, 3], [3, 3]]], [[[1, 3], [3, 1], [1, 3], [2, 3], [3, 2], [2, 2]]]],
)
_r = rnd(3101)
p["tests"].append([[[_r.randint(1, 9), _r.randint(1, 9)] for _ in range(4000)]])
p["tests"].append([[[_r.randint(1, 10 ** 6), _r.randint(1, 10 ** 6)] for _ in range(2500)]])
p["tests"].append([[[1, 2] if i % 2 else [2, 1] for i in range(3000)]])
p["tests"].append([[[_r.randint(1, 60), _r.randint(1, 60)] for _ in range(3000)]])


def b_dominoes(dominoes):
    c = 0
    for i in range(len(dominoes)):
        for j in range(i + 1, len(dominoes)):
            a, b = dominoes[i]
            x, y = dominoes[j]
            if (a == x and b == y) or (a == y and b == x):
                c += 1
    return c


def g_dominoes(r):
    return [[[r.randint(1, 3), r.randint(1, 3)] for _ in range(r.randint(0, 12))]]


def v_dominoes(tests):
    for t in tests:
        d = t["args"][0]
        assert len(d) <= 5000 and all(len(q) == 2 and 1 <= q[0] <= 10 ** 6 and 1 <= q[1] <= 10 ** 6 for q in d)


CHECKS["count-equivalent-domino-pairs"] = (b_dominoes, g_dominoes, "exact")
VALIDATE["count-equivalent-domino-pairs"] = v_dominoes

p = add(
    id="arithmetic-triplets-fixed-difference", title="Arithmetic Triplets with Fixed Difference", diff="Easy", topic=T,
    fn="countArithmeticTriplets", params=[("nums", "int[]"), ("diff", "int")], ret="int", cmp="exact",
    desc="<p>You are given a <em>strictly increasing</em> integer array <code>nums</code> and a positive integer <code>diff</code>. Count the index triples <code>i &lt; j &lt; k</code> such that <code>nums[j] - nums[i] = diff</code> and <code>nums[k] - nums[j] = diff</code>.</p><p>For example, <code>nums = [0, 1, 4, 6, 7, 10]</code> and <code>diff = 3</code> give <code>2</code>, from the triples of values <code>(1, 4, 7)</code> and <code>(4, 7, 10)</code>.</p>",
    constraints=["3 &le; nums.length &le; 10,000", "0 &le; nums[i] &le; 10<sup>9</sup>, and nums is strictly increasing", "1 &le; diff &le; 10<sup>9</sup>"],
    hints=["Three nested loops are far too slow for 10,000 elements. Fix the smallest element of the triple; do the other two values follow?",
           "Since the array is strictly increasing, all values are distinct, so a value <code>x</code> determines a unique triple <code>(x, x + diff, x + 2 * diff)</code>.",
           "Put all values in a set. For every <code>x</code> in the array, add 1 to the answer when both <code>x + diff</code> and <code>x + 2 * diff</code> are in the set."],
    editorial=["Because the values are distinct, each value occurs at exactly one index, and because the array is increasing, the indices of <code>x</code>, <code>x + diff</code> and <code>x + 2 * diff</code> are automatically in order. So the number of triples equals the number of values <code>x</code> whose two successors in the progression also appear in the array.",
               "Build a hash set once, then test two memberships per element: O(n) time and O(n) space. A three-pointer sweep over the sorted array reaches O(1) extra space, but the set is simpler and just as fast in practice."],
    time="O(n)", space="O(n)",
    solution='''def countArithmeticTriplets(nums, diff):
    s = set(nums)
    ans = 0
    for x in nums:
        if x + diff in s and x + 2 * diff in s:
            ans += 1
    return ans
''',
    tests=[[[0, 1, 4, 6, 7, 10], 3], [[4, 5, 6, 7, 8, 9], 2], [[1, 2, 3], 1], [[1, 2, 3], 2], [[0, 5, 10], 5],
           [[0, 1, 2, 3, 4, 5, 6], 1], [[0, 1, 2, 3, 4, 5, 6], 3], [[0, 1, 2, 3, 4, 5, 6], 4], [[0, 10 ** 9 // 2, 10 ** 9], 10 ** 9 // 2],
           [[0, 500000000, 1000000000], 10 ** 9], [[2, 3, 7, 11, 15, 19], 4]],
)
_r = rnd(3103)
p["tests"].append([list(range(5000)), 1])
p["tests"].append([sorted(_r.sample(range(0, 40000), 5000)), 3])
p["tests"].append([[3 * i for i in range(1500)] + [10 ** 5 + 7 * i for i in range(3000)], 7])


def b_arith(nums, diff):
    n = len(nums)
    c = 0
    for i in range(n):
        for j in range(i + 1, n):
            for k in range(j + 1, n):
                if nums[j] - nums[i] == diff and nums[k] - nums[j] == diff:
                    c += 1
    return c


def g_arith(r):
    return [sorted(r.sample(range(0, 20), r.randint(3, 12))), r.randint(1, 5)]


def v_arith(tests):
    for t in tests:
        a, d = t["args"]
        assert 3 <= len(a) <= 10000 and 1 <= d <= 10 ** 9
        assert all(0 <= x <= 10 ** 9 for x in a) and all(a[i] < a[i + 1] for i in range(len(a) - 1)), "not strictly increasing"


CHECKS["arithmetic-triplets-fixed-difference"] = (b_arith, g_arith, "exact")
VALIDATE["arithmetic-triplets-fixed-difference"] = v_arith


# ---------------------------------------------------------------- MEDIUM

p = add(
    id="geometric-triplets-count", title="Geometric Triplets Count", diff="Medium", topic=T,
    fn="countGeometricTriplets", params=[("nums", "int[]"), ("ratio", "int")], ret="int", cmp="exact",
    desc="<p>Given an array <code>nums</code> of positive integers and a positive integer <code>ratio</code>, count the index triples <code>i &lt; j &lt; k</code> such that <code>nums[j] = nums[i] * ratio</code> and <code>nums[k] = nums[j] * ratio</code>.</p><p>Triples are distinguished by position. The count can be huge (for <code>ratio = 1</code> and an array of equal values it is C(n, 3)), so return it modulo <code>1,000,000,007</code>.</p><p>For example, <code>nums = [1, 2, 2, 4]</code> and <code>ratio = 2</code> give <code>2</code>, and <code>nums = [1, 1, 1, 1]</code> with <code>ratio = 1</code> gives <code>4</code>.</p>",
    constraints=["0 &le; nums.length &le; 10,000", "1 &le; nums[i] &le; 10<sup>9</sup>", "1 &le; ratio &le; 10<sup>9</sup>", "Return the count modulo 1,000,000,007"],
    hints=["Checking all triples is O(n<sup>3</sup>). Try treating each element as the <em>middle</em> of a triple: how many valid left and right partners does it have?",
           "For a middle value <code>v</code> you need earlier elements equal to <code>v / ratio</code> (if divisible) and later elements equal to <code>v * ratio</code>. Counting these with hash maps takes O(1) per element.",
           "Single pass alternative: keep <code>one[x]</code> = how many times <code>x</code> has been seen, and <code>two[x]</code> = number of valid pairs <code>(a, a * ratio)</code> ending in value <code>x</code>. For each new value <code>x</code>: add <code>two[x / ratio]</code> to the answer, then add <code>one[x / ratio]</code> to <code>two[x]</code>, then increment <code>one[x]</code>."],
    editorial=["Process the array left to right and maintain two maps. <code>one[x]</code> counts earlier occurrences of the value <code>x</code>; <code>two[x]</code> counts earlier pairs <code>(i, j)</code> with <code>nums[j] = x</code> and <code>nums[i] = x / ratio</code>. When a new element <code>x</code> arrives and <code>x</code> is divisible by <code>ratio</code>, every counted pair ending in <code>x / ratio</code> completes into a triple, so add <code>two[x / ratio]</code> to the answer.",
               "The order of the three updates matters: first complete triples with the old <code>two</code>, then extend pairs with the old <code>one</code>, then record <code>x</code> itself. This also makes <code>ratio = 1</code> work, since an element never pairs with itself. Time and space are O(n); only the final answer needs the modulus, because the intermediate pair counts stay below C(10,000, 2)."],
    time="O(n)", space="O(n)",
    solution='''def countGeometricTriplets(nums, ratio):
    one = {}
    two = {}
    ans = 0
    for x in nums:
        if x % ratio == 0:
            y = x // ratio
            ans += two.get(y, 0)
            if y in one:
                two[x] = two.get(x, 0) + one[y]
        one[x] = one.get(x, 0) + 1
    return ans % 1000000007
''',
    tests=[[[1, 2, 2, 4], 2], [[1, 1, 1, 1], 1], [[], 3], [[5, 5], 1], [[1, 3, 9, 9, 27, 81], 3], [[1, 2, 4], 3],
           [[4, 2, 1], 2], [[1, 5, 5, 25, 125], 5], [[10 ** 9, 10 ** 9, 10 ** 9], 1], [[1, 10 ** 9, 10 ** 9], 10 ** 9],
           [[2, 2, 2, 4, 4, 8, 8], 2], [[7, 21, 3, 63, 21, 189], 3]],
)
_r = rnd(3108)
p["tests"].append([[1] * 10000, 1])
p["tests"].append([[2 ** _r.randint(0, 12) for _ in range(10000)], 2])
p["tests"].append([[_r.choice([1, 3, 9, 27, 81, 243, 729]) for _ in range(10000)], 3])
p["tests"].append([[_r.randint(1, 10 ** 9) for _ in range(3000)], 7])


def b_geo(nums, ratio):
    n = len(nums)
    c = 0
    for i in range(n):
        for j in range(i + 1, n):
            if nums[j] == nums[i] * ratio:
                for k in range(j + 1, n):
                    if nums[k] == nums[j] * ratio:
                        c += 1
    return c % MOD


def g_geo(r):
    ratio = r.randint(1, 3)
    return [[r.choice([1, 2, 3, 4, 6, 8, 9, 12, 18]) for _ in range(r.randint(0, 13))], ratio]


def v_geo(tests):
    for t in tests:
        a, ratio = t["args"]
        assert len(a) <= 10000 and all(1 <= x <= 10 ** 9 for x in a) and 1 <= ratio <= 10 ** 9


CHECKS["geometric-triplets-count"] = (b_geo, g_geo, "exact")
VALIDATE["geometric-triplets-count"] = v_geo

p = add(
    id="tuples-with-same-product", title="Tuples with the Same Product", diff="Medium", topic=T,
    fn="countSameProductTuples", params=[("nums", "int[]")], ret="int", cmp="exact",
    desc="<p>You are given an array <code>nums</code> of <em>distinct</em> positive integers. Count the ordered tuples <code>(a, b, c, d)</code> of four elements taken from four different positions of the array such that <code>a * b = c * d</code>.</p><p>Order matters: <code>(a, b, c, d)</code>, <code>(b, a, c, d)</code> and <code>(c, d, a, b)</code> are all different tuples. For example, <code>nums = [2, 3, 4, 6]</code> gives <code>8</code>, because <code>2 * 6 = 3 * 4</code> and this one pair of pairs can be arranged in 8 ways.</p>",
    constraints=["0 &le; nums.length &le; 800", "1 &le; nums[i] &le; 10,000", "All values of nums are distinct"],
    hints=["Look at it as two <em>pairs</em> of numbers that have equal products. How would you find all pairs with a given product?",
           "Compute the product of every unordered pair and count how many pairs give each product (hash map from product to count).",
           "Because the numbers are distinct, two different pairs with the same product never share an element. If a product occurs for <code>f</code> pairs, choose 2 of them in <code>f * (f - 1) / 2</code> ways, and every choice yields 8 ordered tuples (swap inside each pair, swap the two pairs)."],
    editorial=["If two different unordered pairs <code>{a, b}</code> and <code>{c, d}</code> have the same product and shared an element, say <code>a = c</code>, then <code>b = d</code> would follow, making them the same pair. So with distinct values, equal-product pairs automatically use four different positions.",
               "Count, for every product <code>p</code>, the number <code>f[p]</code> of unordered pairs with that product. Each choice of two of those pairs gives 8 tuples: 2 orders inside the first pair, 2 inside the second, and 2 for which pair comes first. The answer is <code>8 * sum(f * (f - 1) / 2)</code>. Time is O(n<sup>2</sup>) for forming the pair products, and space is O(n<sup>2</sup>) in the worst case for the map."],
    time="O(n^2)", space="O(n^2)",
    solution='''def countSameProductTuples(nums):
    n = len(nums)
    cnt = {}
    for i in range(n):
        a = nums[i]
        for j in range(i + 1, n):
            p = a * nums[j]
            cnt[p] = cnt.get(p, 0) + 1
    total = 0
    for f in cnt.values():
        total += f * (f - 1) // 2
    return 8 * total
''',
    tests=[[[2, 3, 4, 6]], [[1, 2, 4, 5, 10]], [[1, 2, 4, 8, 16, 32]], [[]], [[5]], [[2, 3]], [[1, 2, 3]], [[2, 3, 5, 7]],
           [[10000, 1, 100, 2, 5000, 50]], [[1, 2, 3, 4, 6, 8, 12, 24]], [[3, 4, 6, 8, 12, 24, 36, 2]]],
)
_r = rnd(3109)
p["tests"].append([list(range(1, 801))])
p["tests"].append([_r.sample(range(1, 10001), 800)])
p["tests"].append([sorted(_r.sample([i for i in range(1, 5000) if i % 6 == 0 or i % 10 == 0], 500))])
p["tests"].append([[2 ** i * 3 ** j for i in range(14) for j in range(14) if 2 ** i * 3 ** j <= 10000]])


def b_same_product(nums):
    n = len(nums)
    c = 0
    for i in range(n):
        for j in range(n):
            for k in range(n):
                for l in range(n):
                    if len({i, j, k, l}) == 4 and nums[i] * nums[j] == nums[k] * nums[l]:
                        c += 1
    return c


def g_same_product(r):
    vals = [1, 2, 3, 4, 5, 6, 8, 9, 10, 12, 15, 16, 18, 20, 24, 30]
    return [r.sample(vals, r.randint(0, 9))]


def v_same_product(tests):
    for t in tests:
        a = t["args"][0]
        assert len(a) <= 800 and len(set(a)) == len(a) and all(1 <= x <= 10000 for x in a)


CHECKS["tuples-with-same-product"] = (b_same_product, g_same_product, "exact")
VALIDATE["tuples-with-same-product"] = v_same_product


# ---------------------------------------------------------------- HARD

p = add(
    id="count-triples-with-and-zero", title="Count Triples with Bitwise AND Zero", diff="Hard", topic=T, tier="extra",
    fn="countAndZeroTriples", params=[("nums", "int[]")], ret="int", cmp="exact",
    desc="<p>Given an array <code>nums</code> of non-negative integers, count the ordered triples of indices <code>(i, j, k)</code> such that <code>nums[i] &amp; nums[j] &amp; nums[k] == 0</code>, where <code>&amp;</code> is the bitwise AND.</p><p>The indices need <em>not</em> be distinct: <code>(0, 0, 0)</code> is a valid triple whenever <code>nums[0] == 0</code>, and <code>(i, j, k)</code> and <code>(j, i, k)</code> count separately.</p><p>For example, <code>nums = [2, 1, 3]</code> gives <code>12</code>.</p>",
    constraints=["0 &le; nums.length &le; 700", "0 &le; nums[i] &lt; 4,096 (that is, 12-bit values)", "The answer is at most 700<sup>3</sup>, which fits in 32 bits"],
    hints=["There are n<sup>3</sup> triples, up to 343 million. Can you handle the first two indices together and the third one separately?",
           "Count how many ordered pairs <code>(i, j)</code> produce each possible AND value <code>x = nums[i] &amp; nums[j]</code>. There are only 4,096 possible values of <code>x</code>.",
           "For a third element <code>v</code> you need the number of pairs whose AND has no bit in common with <code>v</code>, i.e. whose AND is a subset of the mask <code>~v</code> (within 12 bits). A subset-sum (zeta) transform over the 12 bits precomputes that count for every mask."],
    editorial=["First collect <code>pair[x]</code>, the number of ordered pairs <code>(i, j)</code> with <code>nums[i] &amp; nums[j] = x</code>. Looping over distinct values with their multiplicities keeps this at about d<sup>2</sup> steps for d distinct values, instead of n<sup>2</sup> pair visits.",
               "A triple is good exactly when <code>x &amp; v = 0</code>, i.e. when every set bit of <code>x</code> lies in the complement mask <code>m = ~v &amp; 4095</code>, so <code>x</code> is a submask of <code>m</code>. Define <code>sub[m]</code> as the sum of <code>pair[x]</code> over all submasks <code>x</code> of <code>m</code>; the standard way is a loop over each bit <code>b</code> doing <code>sub[m] += sub[m ^ (1 &lt;&lt; b)]</code> for masks containing <code>b</code>, which takes 12 &middot; 4096 steps. The answer is the sum over elements <code>v</code> of <code>sub[~v &amp; 4095]</code>.",
               "Total time is O(d<sup>2</sup> + B &middot; 2<sup>B</sup>) with B = 12 bits, versus O(n<sup>3</sup>) for the direct count."],
    time="O(d^2 + B * 2^B)", space="O(2^B)",
    solution='''def countAndZeroTriples(nums):
    B = 12
    FULL = (1 << B) - 1
    cnt = {}
    for x in nums:
        cnt[x] = cnt.get(x, 0) + 1
    sub = [0] * (1 << B)
    items = list(cnt.items())
    for x, cx in items:
        for y, cy in items:
            sub[x & y] += cx * cy
    for b in range(B):
        bit = 1 << b
        for m in range(1 << B):
            if m & bit:
                sub[m] += sub[m ^ bit]
    ans = 0
    for v, c in items:
        ans += c * sub[FULL & ~v]
    return ans
''',
    tests=[[[2, 1, 3]], [[0, 0, 0]], [[]], [[0]], [[1]], [[4095]], [[4095, 0]], [[1, 2, 4, 8, 16]], [[3, 5, 6]],
           [[4095, 4095, 4095, 1]], [[1365, 2730]], [[7, 7, 7, 8, 8]]],
)
_r = rnd(3111)
p["tests"].append([[_r.randint(0, 4095) for _ in range(700)]])
p["tests"].append([[4095 ^ (1 << _r.randint(0, 11)) for _ in range(700)]])
p["tests"].append([_r.sample(range(4096), 700)])
p["tests"].append([[_r.choice([0, 1365, 2730, 4095, 255, 3840]) for _ in range(700)]])


def b_and_zero(nums):
    c = 0
    for a in nums:
        for b in nums:
            for d in nums:
                if a & b & d == 0:
                    c += 1
    return c


def g_and_zero(r):
    return [[r.randint(0, 15) for _ in range(r.randint(0, 10))]]


def v_and_zero(tests):
    for t in tests:
        a = t["args"][0]
        assert len(a) <= 700 and all(0 <= x < 4096 for x in a)


CHECKS["count-triples-with-and-zero"] = (b_and_zero, g_and_zero, "exact")
VALIDATE["count-triples-with-and-zero"] = v_and_zero


# ---------------------------------------------------------------- MORE (replacements for ids taken by other modules)

p = add(
    id="count-pairs-sum-power-of-two", title="Count Pairs with Power-of-Two Sum", diff="Medium", topic=T,
    fn="countPowerOfTwoPairs", params=[("nums", "int[]")], ret="int", cmp="exact",
    desc="<p>Given an array <code>nums</code> of non-negative integers, count the pairs of positions <code>i &lt; j</code> for which <code>nums[i] + nums[j]</code> is a power of two (that is, one of <code>1, 2, 4, 8, ...</code>; note that <code>0</code> is not a power of two).</p><p>For example, <code>nums = [1, 3, 5, 7, 9]</code> gives <code>4</code>, from the sums <code>1+3 = 4</code>, <code>1+7 = 8</code>, <code>3+5 = 8</code> and <code>7+9 = 16</code>. For <code>nums = [1, 1, 1, 3, 3, 3, 7]</code> the answer is <code>15</code>.</p>",
    constraints=["0 &le; nums.length &le; 10,000", "0 &le; nums[i] &le; 2<sup>20</sup>"],
    hints=["Checking every pair costs O(n<sup>2</sup>). How many different power-of-two values can a sum of two numbers below 2<sup>20</sup>+1 take?",
           "At most 22 different ones: 2<sup>0</sup> up to 2<sup>21</sup>. So for each element <code>x</code> there are only 22 partner values that could work, namely <code>2<sup>t</sup> - x</code>.",
           "Scan left to right with a hash map of counts of earlier values. For each <code>x</code> and each power <code>p</code>, add <code>count[p - x]</code> to the answer, then insert <code>x</code>."],
    editorial=["Turn the question around: instead of testing every partner, enumerate the few sums that are allowed. Since each value is at most 2<sup>20</sup>, a sum is at most 2<sup>21</sup>, so the candidate sums are the 22 powers <code>2<sup>0</sup>, ..., 2<sup>21</sup></code>. For an element <code>x</code> the only partners that complete a good pair are the values <code>p - x</code> for these powers (a negative partner simply never exists).",
               "Looking only at earlier elements counts each pair exactly once, including pairs of equal values such as <code>4 + 4 = 8</code>. Different powers give different partner values, so nothing is counted twice for the same earlier element. Time is O(22 n), space O(n). The answer is at most C(10,000, 2), about 5&middot;10<sup>7</sup>."],
    time="O(n log V)", space="O(n)",
    solution='''def countPowerOfTwoPairs(nums):
    powers = [1 << t for t in range(22)]
    cnt = {}
    ans = 0
    for x in nums:
        for p in powers:
            ans += cnt.get(p - x, 0)
        cnt[x] = cnt.get(x, 0) + 1
    return ans
''',
    tests=[[[1, 3, 5, 7, 9]], [[1, 1, 1, 3, 3, 3, 7]], [[]], [[4]], [[0, 0]], [[0, 1]], [[1, 1]], [[2 ** 20, 2 ** 20]],
           [[2 ** 20, 0, 2 ** 20]], [[3, 5, 11, 13, 19, 21]], [[0, 0, 4, 4, 8, 8]], [[1, 2, 3, 4, 5, 6, 7, 8]]],
)
_r = rnd(3112)
p["tests"].append([[_r.randint(0, 2 ** 20) for _ in range(6000)]])
p["tests"].append([[_r.choice([0, 1, 2, 3, 4, 5, 6, 7, 8, 12, 16, 24, 32]) for _ in range(8000)]])
p["tests"].append([[2 ** _r.randint(0, 20) for _ in range(6000)]])


def b_pow2_pairs(nums):
    c = 0
    for i in range(len(nums)):
        for j in range(i + 1, len(nums)):
            s = nums[i] + nums[j]
            if s > 0 and s & (s - 1) == 0:
                c += 1
    return c


def v_pow2_pairs(tests):
    for t in tests:
        a = t["args"][0]
        assert len(a) <= 10000 and all(0 <= x <= 2 ** 20 for x in a)


CHECKS["count-pairs-sum-power-of-two"] = (b_pow2_pairs, lambda r: [gen_arr(r, 0, 17, 0, 12)], "exact")
VALIDATE["count-pairs-sum-power-of-two"] = v_pow2_pairs

p = add(
    id="count-point-pairs-xor-distance", title="Count Point Pairs by XOR Distance", diff="Medium", topic=T,
    fn="countXorDistancePairs", params=[("points", "int[][]"), ("k", "int")], ret="int", cmp="exact",
    desc="<p>You are given <code>points</code>, an array of integer points <code>[x, y]</code> (points may repeat), and a non-negative integer <code>k</code>. Define the <em>XOR distance</em> between two points as <code>(x1 XOR x2) + (y1 XOR y2)</code>, where XOR is the bitwise exclusive or.</p><p>Count the pairs of positions <code>i &lt; j</code> whose XOR distance is exactly <code>k</code>.</p><p>For example, <code>points = [[1,2],[4,2],[1,3],[5,2]]</code> and <code>k = 5</code> give <code>2</code>: the pairs <code>[1,2]-[4,2]</code> (5 + 0) and <code>[1,3]-[5,2]</code> (4 + 1). Equal points have distance 0, so <code>k = 0</code> counts pairs of identical points.</p>",
    constraints=["0 &le; points.length &le; 4,000", "points[i].length = 2", "0 &le; x, y &le; 10<sup>6</sup>", "0 &le; k &le; 100"],
    hints=["Checking all pairs costs O(n<sup>2</sup>); with 4,000 points that is 8 million distance checks, but think about what <code>k &le; 100</code> allows you to do instead.",
           "If <code>x1 XOR x2 = a</code> then <code>x2 = x1 XOR a</code>. So the point at XOR distance <code>k</code> must have <code>x2 = x1 XOR a</code> and <code>y2 = y1 XOR (k - a)</code> for some split <code>a</code> in <code>0..k</code>.",
           "Keep a hash map from point to count for the points seen so far. For each new point, try all <code>k + 1</code> splits <code>a</code>, look up <code>(x XOR a, y XOR (k - a))</code>, and add the stored count. Then insert the point."],
    editorial=["The distance is the sum of two non-negative terms, so the pair <code>(x1 XOR x2, y1 XOR y2)</code> must be some <code>(a, k - a)</code> with <code>0 &le; a &le; k</code>. Because XOR is its own inverse, each split <code>a</code> determines exactly one possible partner point <code>(x XOR a, y XOR (k - a))</code>.",
               "Process the points left to right with a hash map of how many times every point has appeared. For the current point, look up the <code>k + 1</code> candidate partners and add their counts; only earlier points are in the map, so every pair is counted once. Distinct splits give distinct partner points, so none is double counted. Time O(n &middot; k), space O(n). Works for <code>k = 0</code> too, where it counts identical points."],
    time="O(n * k)", space="O(n)",
    solution='''def countXorDistancePairs(points, k):
    cnt = {}
    ans = 0
    for x, y in points:
        for a in range(k + 1):
            ans += cnt.get((x ^ a, y ^ (k - a)), 0)
        key = (x, y)
        cnt[key] = cnt.get(key, 0) + 1
    return ans
''',
    tests=[[[[1, 2], [4, 2], [1, 3], [5, 2]], 5], [[[2, 3], [1, 2], [4, 1], [1, 3]], 4], [[], 3], [[[1, 1]], 0],
           [[[1, 1], [1, 1], [1, 1]], 0], [[[1, 1], [1, 1]], 1], [[[0, 0], [1, 0], [0, 1], [1, 1]], 2],
           [[[0, 0], [1, 0], [0, 1], [1, 1]], 1], [[[1000000, 1000000], [0, 0]], 100], [[[5, 7], [6, 7], [5, 4], [6, 4]], 3],
           [[[0, 0], [100, 0], [0, 100], [100, 100]], 100]],
)
_r = rnd(3113)
p["tests"].append([[[_r.randint(0, 10 ** 6), _r.randint(0, 10 ** 6)] for _ in range(2000)], 100])
p["tests"].append([[[_r.randint(0, 63), _r.randint(0, 63)] for _ in range(2500)], 37])
p["tests"].append([[[_r.randint(0, 7), _r.randint(0, 7)] for _ in range(2500)], 0])
p["tests"].append([[[_r.randint(0, 255), _r.randint(0, 255)] for _ in range(2000)], 100])


def b_xor_pairs(points, k):
    c = 0
    for i in range(len(points)):
        for j in range(i + 1, len(points)):
            if (points[i][0] ^ points[j][0]) + (points[i][1] ^ points[j][1]) == k:
                c += 1
    return c


def g_xor_pairs(r):
    return [[[r.randint(0, 7), r.randint(0, 7)] for _ in range(r.randint(0, 12))], r.randint(0, 8)]


def v_xor_pairs(tests):
    for t in tests:
        pts, k = t["args"]
        assert len(pts) <= 4000 and 0 <= k <= 100
        assert all(len(q) == 2 and 0 <= q[0] <= 10 ** 6 and 0 <= q[1] <= 10 ** 6 for q in pts)


CHECKS["count-point-pairs-xor-distance"] = (b_xor_pairs, g_xor_pairs, "exact")
VALIDATE["count-point-pairs-xor-distance"] = v_xor_pairs

p = add(
    id="count-triplets-equal-xor-halves", title="Count Triplets with Equal XOR Halves", diff="Medium", topic=T,
    fn="countEqualXorTriplets", params=[("arr", "int[]")], ret="int", cmp="exact",
    desc="<p>Given an integer array <code>arr</code>, count the triples <code>(i, j, k)</code> with <code>0 &le; i &lt; j &le; k &lt; n</code> such that <code>a = b</code>, where</p><ul><li><code>a = arr[i] XOR arr[i+1] XOR ... XOR arr[j-1]</code></li><li><code>b = arr[j] XOR arr[j+1] XOR ... XOR arr[k]</code></li></ul><p>Both parts are non-empty. Return the count modulo <code>1,000,000,007</code>.</p><p>For example, <code>arr = [2, 3, 1, 6, 7]</code> gives <code>4</code>, and <code>arr = [1, 1, 1, 1, 1]</code> gives <code>10</code>.</p>",
    constraints=["1 &le; arr.length &le; 10,000", "0 &le; arr[i] &le; 10<sup>9</sup>", "Return the count modulo 1,000,000,007"],
    hints=["Three nested loops with a running XOR give O(n<sup>3</sup>), and it is still O(n<sup>2</sup>) with prefix XORs. Look for a cleaner condition for <code>a = b</code>.",
           "<code>a = b</code> means <code>a XOR b = 0</code>, and <code>a XOR b</code> is the XOR of the whole range <code>i..k</code>. With prefix XORs <code>P</code> (where <code>P[t]</code> is the XOR of the first <code>t</code> elements) this reads <code>P[i] = P[k+1]</code>.",
           "The split point <code>j</code> does not matter for the condition: any of the <code>k - i</code> positions <code>i &lt; j &le; k</code> works. So every pair of equal prefix values <code>P[i] = P[m]</code> with <code>i &lt; m</code> contributes <code>m - i - 1</code>. Group by prefix value and keep a count and a sum of indices."],
    editorial=["The XOR of the two halves is the XOR of <code>arr[i..k]</code>, which equals <code>P[i] XOR P[k+1]</code>. The halves are equal exactly when that is zero, i.e. <code>P[i] = P[k+1]</code>, and then the split <code>j</code> can be any of the <code>k - i</code> positions after <code>i</code> up to <code>k</code>.",
               "Write <code>m = k + 1</code>. The answer is the sum over pairs <code>i &lt; m</code> with <code>P[i] = P[m]</code> of <code>m - i - 1</code>. Scanning <code>m</code> from left to right with, for every prefix value <code>v</code>, the number <code>c[v]</code> of earlier indices and their index sum <code>s[v]</code>, the contribution of <code>m</code> is <code>c[v] * (m - 1) - s[v]</code>. That makes the whole solution O(n) time and space. The total can reach about C(10,000, 3) = 1.7&middot;10<sup>11</sup>, hence the modulus."],
    time="O(n)", space="O(n)",
    solution='''def countEqualXorTriplets(arr):
    count = {}
    index_sum = {}
    prefix = 0
    ans = 0
    for m in range(len(arr) + 1):
        if m > 0:
            prefix ^= arr[m - 1]
        c = count.get(prefix, 0)
        ans += c * (m - 1) - index_sum.get(prefix, 0)
        count[prefix] = c + 1
        index_sum[prefix] = index_sum.get(prefix, 0) + m
    return ans % 1000000007
''',
    tests=[[[2, 3, 1, 6, 7]], [[1, 1, 1, 1, 1]], [[5]], [[0]], [[0, 0]], [[1, 2, 3]], [[1, 2]], [[7, 7, 7, 7]],
           [[3, 5, 6, 3, 5, 6]], [[10 ** 9, 10 ** 9, 10 ** 9]], [[1, 2, 4, 8, 16]], [[0, 0, 0, 0, 0, 0, 0]]],
)
_r = rnd(3114)
p["tests"].append([[0] * 10000])
p["tests"].append([[_r.randint(0, 3) for _ in range(8000)]])
p["tests"].append([[_r.randint(0, 10 ** 9) for _ in range(4000)]])
p["tests"].append([[_r.choice([5, 9, 12]) for _ in range(8000)]])


def b_xor_halves(arr):
    n = len(arr)
    c = 0
    for i in range(n):
        for j in range(i + 1, n):
            a = 0
            for t in range(i, j):
                a ^= arr[t]
            b = 0
            for k in range(j, n):
                b ^= arr[k]
                if a == b:
                    c += 1
    return c % MOD


def v_xor_halves(tests):
    for t in tests:
        a = t["args"][0]
        assert 1 <= len(a) <= 10000 and all(0 <= x <= 10 ** 9 for x in a)


CHECKS["count-triplets-equal-xor-halves"] = (b_xor_halves, lambda r: [gen_arr(r, 0, 5, 1, 12)], "exact")
VALIDATE["count-triplets-equal-xor-halves"] = v_xor_halves

p = add(
    id="count-quadruples-sum-of-three-equals-fourth", title="Count Quadruples Where Three Sum to the Fourth", diff="Hard", topic=T, tier="extra",
    fn="countSumQuadruples", params=[("nums", "int[]")], ret="int", cmp="exact",
    desc="<p>Given an integer array <code>nums</code>, count the index quadruples <code>a &lt; b &lt; c &lt; d</code> with <code>nums[a] + nums[b] + nums[c] = nums[d]</code>.</p><p>Quadruples are distinguished by position, so equal values at different positions count separately. Return the count modulo <code>1,000,000,007</code>.</p><p>For example, <code>nums = [1, 2, 3, 6]</code> gives <code>1</code>, <code>nums = [3, 3, 6, 4, 5]</code> gives <code>0</code>, and <code>nums = [1, 1, 1, 3, 5]</code> gives <code>4</code>.</p>",
    constraints=["0 &le; nums.length &le; 700", "-10<sup>8</sup> &le; nums[i] &le; 10<sup>8</sup>", "Return the count modulo 1,000,000,007"],
    hints=["Four nested loops are O(n<sup>4</sup>), and the standard optimisation to O(n<sup>3</sup>) is still too slow for 700 elements. Rewrite the equation to split it into two pairs.",
           "<code>nums[a] + nums[b] = nums[d] - nums[c]</code>. The left side is a sum of the pair <code>(a, b)</code>, the right side a difference of the pair <code>(c, d)</code>, with <code>b &lt; c</code> separating them.",
           "Sweep <code>b</code> from right to left. Keep a hash map of all differences <code>nums[d] - nums[c]</code> with <code>c &gt; b</code> and <code>d &gt; c</code>. For each <code>a &lt; b</code> add <code>map[nums[a] + nums[b]]</code> to the answer. Before moving <code>b</code> one step left, insert the pairs whose <code>c</code> is the old <code>b</code>."],
    editorial=["Move <code>nums[c]</code> to the right side: <code>nums[a] + nums[b] = nums[d] - nums[c]</code>. Now the left pair <code>(a, b)</code> and the right pair <code>(c, d)</code> are independent except for the ordering <code>b &lt; c</code>, which we enforce with a sweep over <code>b</code> from <code>n - 3</code> down to <code>1</code>.",
               "Maintain <code>diff[v]</code>, the number of pairs <code>(c, d)</code> with <code>c &gt; b</code>, <code>d &gt; c</code> and <code>nums[d] - nums[c] = v</code>. When the sweep arrives at a new <code>b</code>, add the pairs with <code>c = b + 1</code> (one per later <code>d</code>) to the map; then every <code>a &lt; b</code> contributes <code>diff[nums[a] + nums[b]]</code>. Each pair of positions is inserted once and queried once, so time and space are O(n<sup>2</sup>). The count can reach C(700, 4), about 10<sup>10</sup>, so reduce modulo 1,000,000,007."],
    time="O(n^2)", space="O(n^2)",
    solution='''def countSumQuadruples(nums):
    n = len(nums)
    diff = {}
    ans = 0
    for b in range(n - 3, 0, -1):
        c = b + 1
        nc = nums[c]
        for d in range(c + 1, n):
            v = nums[d] - nc
            diff[v] = diff.get(v, 0) + 1
        nb = nums[b]
        for a in range(b):
            ans += diff.get(nums[a] + nb, 0)
    return ans % 1000000007
''',
    tests=[[[1, 2, 3, 6]], [[3, 3, 6, 4, 5]], [[1, 1, 1, 3, 5]], [[]], [[1, 2, 3]], [[0, 0, 0, 0]], [[0, 0, 0, 0, 0]],
           [[-1, 1, 0, 0]], [[10 ** 8, 10 ** 8, -10 ** 8, 10 ** 8]], [[1, 2, 3, 4, 5, 6, 7, 8, 9, 10]], [[2, 2, 2, 6, 6, 6, 2]]],
)
_r = rnd(3115)
p["tests"].append([[0] * 700])
p["tests"].append([[_r.randint(-3, 3) for _ in range(700)]])
p["tests"].append([[_r.randint(-10 ** 8, 10 ** 8) for _ in range(700)]])
p["tests"].append([[_r.randint(0, 40) for _ in range(700)]])


def b_sum_quads(nums):
    n = len(nums)
    c = 0
    for a in range(n):
        for b in range(a + 1, n):
            for cc in range(b + 1, n):
                for d in range(cc + 1, n):
                    if nums[a] + nums[b] + nums[cc] == nums[d]:
                        c += 1
    return c % MOD


def v_sum_quads(tests):
    for t in tests:
        a = t["args"][0]
        assert len(a) <= 700 and all(-10 ** 8 <= x <= 10 ** 8 for x in a)


CHECKS["count-quadruples-sum-of-three-equals-fourth"] = (b_sum_quads, lambda r: [gen_arr(r, -3, 3, 0, 12)], "exact")
VALIDATE["count-quadruples-sum-of-three-equals-fourth"] = v_sum_quads

p = add(
    id="count-pairs-product-divisible-by-k", title="Count Pairs with Product Divisible by K", diff="Hard", topic=T, tier="extra",
    fn="countProductDivisible", params=[("nums", "int[]"), ("k", "int")], ret="int", cmp="exact",
    desc="<p>Given an array <code>nums</code> of positive integers and a positive integer <code>k</code>, count the pairs of positions <code>i &lt; j</code> such that <code>nums[i] * nums[j]</code> is divisible by <code>k</code>.</p><p>For example, <code>nums = [1, 2, 3, 4, 5]</code> and <code>k = 2</code> give <code>7</code>, and <code>nums = [1, 2, 3, 4]</code> with <code>k = 5</code> gives <code>0</code>.</p>",
    constraints=["0 &le; nums.length &le; 10,000", "1 &le; nums[i] &le; 100,000", "1 &le; k &le; 100,000"],
    hints=["Checking all pairs is O(n<sup>2</sup>), which is about 5&middot;10<sup>7</sup> pairs here. A pair's product only matters through how much of <code>k</code> each factor already covers.",
           "Replace each number <code>x</code> by <code>g = gcd(x, k)</code>. The product <code>x * y</code> is divisible by <code>k</code> if and only if <code>gcd(x, k) * gcd(y, k)</code> is divisible by <code>k</code>.",
           "All the values <code>g</code> are divisors of <code>k</code>, and a number up to 100,000 has at most 128 divisors. Count how many elements have each gcd, then test every pair of divisors (at most 128<sup>2</sup>) and multiply the counts."],
    editorial=["Let <code>g = gcd(x, k)</code>. Everything in <code>x</code> that is not shared with <code>k</code> cannot help to make a multiple of <code>k</code>, so the pair <code>(x, y)</code> works exactly when <code>gcd(x, k) * gcd(y, k)</code> is a multiple of <code>k</code>. This reduces every number to one of the divisors of <code>k</code>.",
               "Count <code>cnt[g]</code> for every divisor, then go over all pairs of divisors <code>g1 &lt; g2</code> with <code>g1 * g2 % k == 0</code> and add <code>cnt[g1] * cnt[g2]</code>. A divisor paired with itself (when <code>g * g % k == 0</code>) contributes <code>cnt[g] * (cnt[g] - 1) / 2</code>. The cost is O(n log k) for the gcds plus O(d(k)<sup>2</sup>) for the pairs, where d(k) &le; 128. The answer is at most about 5&middot;10<sup>7</sup>."],
    time="O(n log k + d(k)^2)", space="O(d(k))",
    solution='''from math import gcd


def countProductDivisible(nums, k):
    cnt = {}
    for x in nums:
        g = gcd(x, k)
        cnt[g] = cnt.get(g, 0) + 1
    items = list(cnt.items())
    ans = 0
    for i in range(len(items)):
        g1, c1 = items[i]
        if g1 * g1 % k == 0:
            ans += c1 * (c1 - 1) // 2
        for j in range(i + 1, len(items)):
            g2, c2 = items[j]
            if g1 * g2 % k == 0:
                ans += c1 * c2
    return ans
''',
    tests=[[[1, 2, 3, 4, 5], 2], [[1, 2, 3, 4], 5], [[], 7], [[6], 6], [[6, 6], 6], [[2, 3], 6], [[2, 3, 4, 9], 6],
           [[5, 5, 5, 5], 1], [[100000, 100000, 1], 100000], [[2, 2, 2, 2], 8], [[2, 2, 2, 2], 4], [[4, 6, 10, 15, 25], 20]],
)
_r = rnd(3116)
p["tests"].append([[_r.randint(1, 100000) for _ in range(5000)], 83160])
p["tests"].append([[_r.randint(1, 100000) for _ in range(5000)], 99991])
p["tests"].append([[_r.choice([2, 3, 4, 6, 8, 9, 12, 18, 24, 36, 72]) * _r.randint(1, 1000) for _ in range(5000)], 3600])
p["tests"].append([[_r.randint(1, 100000) for _ in range(5000)], 1])


def b_prod_div(nums, k):
    c = 0
    for i in range(len(nums)):
        for j in range(i + 1, len(nums)):
            if nums[i] * nums[j] % k == 0:
                c += 1
    return c


def g_prod_div(r):
    return [[r.randint(1, 36) for _ in range(r.randint(0, 12))], r.choice([1, 2, 4, 6, 8, 12, 16, 18, 24, 30, 36])]


def v_prod_div(tests):
    for t in tests:
        a, k = t["args"]
        assert len(a) <= 10000 and 1 <= k <= 100000 and all(1 <= x <= 100000 for x in a)


CHECKS["count-pairs-product-divisible-by-k"] = (b_prod_div, g_prod_div, "exact")
VALIDATE["count-pairs-product-divisible-by-k"] = v_prod_div
