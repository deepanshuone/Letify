"""Problems: sorting, inversion counting and merge-sort based counts. See data/lib.py for the registry."""
from collections import deque
from itertools import permutations

from lib import add, rnd, CHECKS, VALIDATE, gen_arr  # noqa: F401

TOPIC = "Sorting"
MOD = 10 ** 9 + 7


def _inv(a):
    """Plain O(n^2) inversion count, used by the brute-force checkers (strict: a[i] > a[j], i < j)."""
    n = len(a)
    return sum(1 for i in range(n) for j in range(i + 1, n) if a[i] > a[j])


# ---------------------------------------------------------------- EASY

p = add(
    id="global-local-inversions-equal", title="Global Equals Local Inversions", diff="Easy", topic=TOPIC, tier="extra",
    fn="globalEqualsLocal", params=[("nums", "int[]")], ret="bool", cmp="exact",
    desc="<p><code>nums</code> is a permutation of the integers <code>0..n-1</code>. Two kinds of inversions are counted:</p>"
         "<ul><li>a <em>global inversion</em> is any pair <code>i &lt; j</code> with <code>nums[i] &gt; nums[j]</code>;</li>"
         "<li>a <em>local inversion</em> is a global inversion whose indices are neighbours, that is <code>j = i + 1</code>.</li></ul>"
         "<p>Every local inversion is also a global one. Return <code>true</code> if the number of global inversions is exactly equal to the number of local inversions, otherwise <code>false</code>.</p>"
         "<pre>nums = [1, 0, 2]   global 1, local 1  -> true\nnums = [1, 2, 0]   global 2, local 1  -> false</pre>",
    constraints=["1 &le; nums.length &le; 10,000", "nums is a permutation of 0..nums.length - 1"],
    hints=["Counting both kinds of inversions directly takes O(n<sup>2</sup>) for the global one. But you do not need the counts: the two numbers are equal exactly when there is no non-local inversion at all.",
           "A non-local inversion is a pair <code>i &lt; j</code> with <code>j &ge; i + 2</code> and <code>nums[i] &gt; nums[j]</code>. Ask what the array must look like if no such pair exists.",
           "In a permutation of 0..n-1, a value that sits 2 or more places away from its own index forces a non-local inversion. So check <code>abs(nums[i] - i) &le; 1</code> for every index."],
    editorial=["Global inversions are a superset of local ones, so the counts are equal if and only if every global inversion is local. We therefore only have to decide whether some pair <code>i &lt; j</code>, <code>j - i &ge; 2</code>, has <code>nums[i] &gt; nums[j]</code>.",
               "Claim: such a pair exists exactly when some value is at distance 2 or more from its home index. If <code>nums[i] &ge; i + 2</code>, then among the n - i - 1 positions after i there are only n - 1 - nums[i] values larger than nums[i] (at most n - i - 3), so at least two of the later positions hold smaller values, and one of them is non-adjacent to i. Symmetrically for <code>nums[i] &le; i - 2</code>. Conversely, if every value is within 1 of its index, a non-local inversion would need a value to move at least 2 places. So one pass testing <code>abs(nums[i] - i) &le; 1</code> is enough: O(n) time and O(1) space.",
               "A running-maximum version is equivalent: keep the maximum of <code>nums[0..i-2]</code> and fail as soon as it exceeds <code>nums[i]</code>."],
    time="O(n)", space="O(1)",
    solution='''def globalEqualsLocal(nums):
    for i, x in enumerate(nums):
        if abs(x - i) > 1:
            return False
    return True
''',
    tests=[[[1, 0, 2]], [[1, 2, 0]], [[0]], [[0, 1]], [[1, 0]], [[2, 1, 0]], [[0, 2, 1, 3]], [[1, 0, 3, 2, 5, 4]],
           [[2, 0, 1]], [[0, 3, 2, 1]], [[1, 0, 2, 4, 3, 5, 7, 6]]],
)
_r = rnd(8201)


def _near_identity(n, r):
    a = list(range(n))
    i = 0
    while i + 1 < n:
        if r.random() < 0.5:
            a[i], a[i + 1] = a[i + 1], a[i]
            i += 2
        else:
            i += 1
    return a


p["tests"].append([_near_identity(6000, _r)])
_a = _near_identity(6000, _r)
_a[2999], _a[3001] = _a[3001], _a[2999]  # a far swap makes a non-local inversion
p["tests"].append([_a])
_a = list(range(3000)); _r.shuffle(_a)
p["tests"].append([_a])


def b_gl(nums):
    n = len(nums)
    glob = _inv(nums)
    loc = sum(1 for i in range(n - 1) if nums[i] > nums[i + 1])
    return glob == loc


def g_gl(r):
    n = r.randint(1, 9)
    if r.random() < 0.3:
        a = list(range(n))
        r.shuffle(a)
        return [a]
    a = _near_identity(n, r)
    if r.random() < 0.3 and n >= 3:
        i = r.randint(0, n - 3)
        a[i], a[i + 2] = a[i + 2], a[i]
    return [a]


def v_gl(tests):
    for t in tests:
        a = t["args"][0]
        assert 1 <= len(a) <= 10000 and sorted(a) == list(range(len(a)))
    assert any(t["expected"] for t in tests) and not all(t["expected"] for t in tests)


CHECKS["global-local-inversions-equal"] = (b_gl, g_gl, "exact")
VALIDATE["global-local-inversions-equal"] = v_gl

p = add(
    id="inversions-in-rotated-sorted-array", title="Inversions in a Rotated Sorted Array", diff="Easy", topic=TOPIC, tier="extra",
    fn="rotatedInversions", params=[("nums", "int[]")], ret="int", cmp="exact",
    desc="<p>An array of <strong>distinct</strong> integers was sorted in ascending order and then rotated: some number of elements was moved from the front to the back (possibly none). So the input looks like <code>[4, 5, 6, 1, 2, 3]</code> or <code>[1, 2, 3]</code>.</p>"
         "<p>An <em>inversion</em> is a pair of indices <code>i &lt; j</code> with <code>nums[i] &gt; nums[j]</code>. Return the number of inversions in <code>nums</code>.</p>"
         "<pre>nums = [4, 5, 6, 1, 2, 3]  -> 9   (each of 4,5,6 is above each of 1,2,3)\nnums = [1, 2, 3]           -> 0</pre>",
    constraints=["1 &le; nums.length &le; 50,000", "-10<sup>9</sup> &le; nums[i] &le; 10<sup>9</sup>", "All values are distinct and nums is a rotation of an ascending array"],
    hints=["A general inversion counter works in O(n log n), but this array has a very special shape. How many sorted runs does it have?",
           "The array is a sorted block of larger values followed by a sorted block of smaller values. Inside each block there are no inversions.",
           "Find the index <code>k</code> where the order breaks (<code>nums[k] &lt; nums[k-1]</code>). Every one of the first k values exceeds every one of the remaining n - k values, so the answer is <code>k * (n - k)</code>; if the order never breaks the answer is 0."],
    editorial=["Rotating a sorted array of distinct values yields two ascending blocks: the front block B holds the larger values and the back block A holds the smaller ones. Pairs inside B or inside A are in order. Every pair with one element from B and one from A is inverted, because all of B is larger than all of A.",
               "If the break is at index <code>k</code> (the first index with <code>nums[k] &lt; nums[k-1]</code>), the answer is <code>k * (n - k)</code>. With no break the array is already sorted and the answer is 0. One scan, O(n) time and O(1) space; the result is at most n<sup>2</sup>/4 &le; 6.25 &times; 10<sup>8</sup>, which fits in 32 bits."],
    time="O(n)", space="O(1)",
    solution='''def rotatedInversions(nums):
    n = len(nums)
    for k in range(1, n):
        if nums[k] < nums[k - 1]:
            return k * (n - k)
    return 0
''',
    tests=[[[4, 5, 6, 1, 2, 3]], [[1, 2, 3]], [[7]], [[2, 1]], [[1, 2]], [[3, 1, 2]], [[2, 3, 1]], [[-5, -3, 0, 9, -100, -50]],
           [[10, 20, 30, 40, 50, 60, 70, 5]], [[1000000000, -1000000000]]],
)
_r = rnd(8202)
_s = sorted(_r.sample(range(-10 ** 9, 10 ** 9), 3500)); _k = 1345
p["tests"].append([_s[_k:] + _s[:_k]])
_s = sorted(_r.sample(range(-10 ** 9, 10 ** 9), 3000))
p["tests"].append([_s[1:] + _s[:1]])
p["tests"].append([_s[:2000]])


def b_rot(nums):
    return _inv(nums)


def g_rot(r):
    n = r.randint(1, 9)
    s = sorted(r.sample(range(-20, 20), n))
    k = r.randint(0, n - 1)
    return [s[k:] + s[:k]]


def v_rot(tests):
    for t in tests:
        a = t["args"][0]
        assert 1 <= len(a) <= 50000 and len(set(a)) == len(a) and all(abs(x) <= 10 ** 9 for x in a)
        s = sorted(a)
        assert any(a == s[k:] + s[:k] for k in range(len(a))), "not a rotation"


CHECKS["inversions-in-rotated-sorted-array"] = (b_rot, g_rot, "exact")
VALIDATE["inversions-in-rotated-sorted-array"] = v_rot

# ---------------------------------------------------------------- MEDIUM

p = add(
    id="count-array-inversions", title="Count Inversions in an Array", diff="Medium", topic=TOPIC, tier="must",
    fn="countInversions", params=[("nums", "int[]")], ret="int", cmp="exact",
    desc="<p>An <em>inversion</em> is a pair of indices <code>i &lt; j</code> with <code>nums[i] &gt; nums[j]</code> (strictly greater, so equal values never form an inversion). Return the number of inversions in <code>nums</code>.</p>"
         "<p>An inversion count measures how far an array is from being sorted: 0 means sorted, and it equals the number of adjacent swaps a bubble sort performs.</p>"
         "<pre>nums = [2, 4, 1, 3, 5]  -> 3   pairs (2,1) (4,1) (4,3)\nnums = [5, 4, 3, 2, 1]  -> 10\nnums = [1, 1, 1]        -> 0</pre>",
    constraints=["1 &le; nums.length &le; 10,000", "-10<sup>9</sup> &le; nums[i] &le; 10<sup>9</sup>", "Values may repeat"],
    hints=["Checking every pair is O(n<sup>2</sup>): about 50 million pair checks at n = 10,000. Look for a way to count many inversions at once.",
           "Split the array in two halves. Every inversion is inside the left half, inside the right half, or crosses the middle. The first two are the same problem on smaller input. How could sorted halves help to count the crossing ones?",
           "Merge sort: while merging two sorted halves, whenever you take an element from the right half before the remaining left elements, it is smaller than <em>all</em> of them, so add the number of left elements still waiting. Use <code>&le;</code> when comparing so that equal values are taken from the left first and are not counted."],
    editorial=["Divide and conquer: sort and count the left half, sort and count the right half, then merge them. During the merge, the left half <code>L</code> and right half <code>R</code> are both sorted. When the current right element <code>R[j]</code> is strictly smaller than the current left element <code>L[i]</code>, it is also smaller than every remaining left element, which are all positioned before it in the original array. That contributes <code>len(L) - i</code> crossing inversions in a single step.",
               "On ties take the left element first, so equal values are never counted. The merge is linear and there are log n levels, so the total is O(n log n) time with O(n) extra space. A Fenwick tree over compressed values gives the same bound: scan left to right and, for each element, count how many earlier elements are strictly greater.",
               "The answer can be as large as n(n-1)/2, about 5 &times; 10<sup>7</sup> here, so it fits in 32 bits, but in larger variants use a 64-bit counter."],
    time="O(n log n)", space="O(n)",
    solution='''def countInversions(nums):
    n = len(nums)
    a = nums[:]
    buf = a[:]
    count = 0
    width = 1
    while width < n:
        for lo in range(0, n, 2 * width):
            mid = min(lo + width, n)
            hi = min(lo + 2 * width, n)
            i, j, k = lo, mid, lo
            while i < mid and j < hi:
                if a[i] <= a[j]:
                    buf[k] = a[i]
                    i += 1
                else:
                    buf[k] = a[j]
                    j += 1
                    count += mid - i
                k += 1
            while i < mid:
                buf[k] = a[i]
                i += 1
                k += 1
            while j < hi:
                buf[k] = a[j]
                j += 1
                k += 1
        a, buf = buf, a
        width *= 2
    return count
''',
    tests=[[[2, 4, 1, 3, 5]], [[5, 4, 3, 2, 1]], [[1, 1, 1]], [[7]], [[1, 2, 3, 4]], [[2, 1, 2, 1]], [[1000000000, -1000000000]],
           [[3, 3, 2, 2, 1, 1]], [[0, -1, -2, 5, 4, 3]]],
)
_r = rnd(8203)
p["tests"].append([[_r.randint(-10 ** 9, 10 ** 9) for _ in range(4000)]])
p["tests"].append([list(range(7000, 0, -1))])
p["tests"].append([[_r.randint(0, 20) for _ in range(6000)]])


def b_inv(nums):
    return _inv(nums)


def v_inv(tests):
    for t in tests:
        a = t["args"][0]
        assert 1 <= len(a) <= 10000 and all(abs(x) <= 10 ** 9 for x in a)


CHECKS["count-array-inversions"] = (b_inv, lambda r: [gen_arr(r, -6, 6, 1, 10)], "exact")
VALIDATE["count-array-inversions"] = v_inv

p = add(
    id="permutation-inversion-parity", title="Parity of a Permutation's Inversions", diff="Medium", topic=TOPIC, tier="extra",
    fn="inversionParity", params=[("perm", "int[]")], ret="int", cmp="exact",
    desc="<p><code>perm</code> is a permutation of the integers <code>1..n</code>. An inversion is a pair <code>i &lt; j</code> with <code>perm[i] &gt; perm[j]</code>. Return <code>0</code> if the number of inversions is even and <code>1</code> if it is odd.</p>"
         "<p>You do not need the inversion count itself, only its parity, and this can be found without any sorting.</p>"
         "<pre>perm = [2, 1, 3]  -> 1   one inversion (2,1)\nperm = [3, 1, 2]  -> 0   two inversions (3,1) (3,2)\nperm = [1, 2, 3]  -> 0</pre>",
    constraints=["1 &le; perm.length &le; 100,000", "perm is a permutation of 1..perm.length"],
    hints=["You can count all inversions with merge sort in O(n log n), then take the answer modulo 2. Is there something even simpler that only tracks parity?",
           "Swapping any two elements of a permutation changes the parity of its inversion count (the count goes up or down by an odd number). The sorted array has 0 inversions, which is even.",
           "So parity equals the parity of the minimum number of swaps needed to sort the permutation. That number is <code>n - (number of cycles)</code>, where cycles are the cycles of the mapping <code>i -> perm[i]</code>."],
    editorial=["Exchanging two elements always flips the parity of the inversion count. A permutation that needs s swaps to become sorted can be built from the sorted one by s swaps, so its inversion parity is the parity of s (every way of sorting with swaps uses a number of swaps of the same parity).",
               "The fewest swaps needed to sort a permutation is <code>n - c</code> where <code>c</code> is the number of cycles of the permutation seen as a function <code>i -> perm[i]</code>: a cycle of length L is repaired with L - 1 swaps. Count the cycles with a visited array in O(n) time and take <code>(n - c) % 2</code>.",
               "This is the classic 'sign of a permutation' fact. A merge-sort or Fenwick-tree count followed by <code>% 2</code> is also correct, but runs in O(n log n)."],
    time="O(n)", space="O(n)",
    solution='''def inversionParity(perm):
    n = len(perm)
    seen = [False] * n
    cycles = 0
    for i in range(n):
        if not seen[i]:
            cycles += 1
            j = i
            while not seen[j]:
                seen[j] = True
                j = perm[j] - 1
    return (n - cycles) % 2
''',
    tests=[[[2, 1, 3]], [[3, 1, 2]], [[1, 2, 3]], [[1]], [[2, 1]], [[3, 2, 1]], [[4, 3, 2, 1]], [[2, 3, 4, 1]], [[1, 3, 2, 5, 4, 6]]],
)
_r = rnd(8204)
for _n in (6000, 5001, 7000):
    _a = list(range(1, _n + 1)); _r.shuffle(_a)
    p["tests"].append([_a])
p["tests"].append([list(range(7000, 0, -1))])


def v_par(tests):
    for t in tests:
        a = t["args"][0]
        assert 1 <= len(a) <= 100000 and sorted(a) == list(range(1, len(a) + 1))
    assert {t["expected"] for t in tests} == {0, 1}


def g_par(r):
    a = list(range(1, r.randint(1, 9) + 1))
    r.shuffle(a)
    return [a]


CHECKS["permutation-inversion-parity"] = (lambda perm: _inv(perm) % 2, g_par, "exact")
VALIDATE["permutation-inversion-parity"] = v_par

p = add(
    id="bubble-sort-passes-needed", title="Bubble Sort Passes", diff="Medium", topic=TOPIC, tier="extra",
    fn="bubbleSortPasses", params=[("nums", "int[]")], ret="int", cmp="exact",
    desc="<p>Bubble sort works in passes. A pass scans the array from left to right and, for each neighbouring pair <code>(nums[i], nums[i+1])</code>, swaps it if <code>nums[i] &gt; nums[i+1]</code> (strictly). The algorithm repeats passes until a pass performs no swap.</p>"
         "<p>Return the number of passes that perform <strong>at least one swap</strong>. The final check pass, which finds nothing to swap, is not counted.</p>"
         "<pre>nums = [3, 1, 2]     pass 1: [1, 2, 3]  -> 1\nnums = [4, 3, 2, 1]  -> 3   (the small value moves left by one place per pass)\nnums = [1, 2, 2, 3]  -> 0</pre>"
         "<p>Simulating the passes costs O(n<sup>2</sup>). Find the answer directly.</p>",
    constraints=["1 &le; nums.length &le; 10,000", "-10<sup>9</sup> &le; nums[i] &le; 10<sup>9</sup>", "Values may repeat"],
    hints=["Watch one small element in a sample such as <code>[4, 3, 2, 1]</code> by hand. How far can it travel to the left during a single pass?",
           "In every pass an element moves left by at most one place, and it does move left by exactly one place whenever some larger element is still ahead of it. So the number of passes is governed by the element that has to travel the most places to the left.",
           "For each index i let <code>g[i]</code> be the number of earlier elements that are strictly greater than <code>nums[i]</code> (count them with a Fenwick tree over ranks or with merge sort). The answer is the maximum of all <code>g[i]</code>."],
    editorial=["Fix an element x. During a pass, the largest value seen so far is carried to the right and the elements it passes each move left by one place. So if x has at least one strictly greater element before it, x moves exactly one place to the left in this pass, and the number of greater elements before it drops by exactly one. If none are greater, x does not move left. Hence x needs exactly <code>g(x)</code> passes, where <code>g(x)</code> is the number of strictly greater elements before it.",
               "The array is sorted after the pass number max g, and passes up to that number all perform a swap (the element attaining the maximum moves in each of them), so the answer is the maximum g over all elements; it is 0 for a sorted array. Compute g with a Fenwick tree over compressed values: <code>g[i] = i - (number of earlier elements &le; nums[i])</code>. The total cost is O(n log n) time and O(n) space, compared with O(n<sup>2</sup>) for the simulation.",
               "Equal elements are never swapped with each other (the swap needs a strict inequality), which is why <code>&le;</code> is used when counting the earlier elements that do not count as greater."],
    time="O(n log n)", space="O(n)",
    solution='''def bubbleSortPasses(nums):
    vals = sorted(set(nums))
    rank = {v: i + 1 for i, v in enumerate(vals)}
    m = len(vals)
    tree = [0] * (m + 1)
    best = 0
    for i, x in enumerate(nums):
        r = rank[x]
        k = r
        le = 0
        while k > 0:
            le += tree[k]
            k -= k & -k
        best = max(best, i - le)
        k = r
        while k <= m:
            tree[k] += 1
            k += k & -k
    return best
''',
    tests=[[[3, 1, 2]], [[4, 3, 2, 1]], [[1, 2, 2, 3]], [[5]], [[2, 1]], [[1, 3, 2, 4]], [[2, 2, 1, 1]], [[1, 2, 3, 0]],
           [[10, -10, 10, -10, 10, -10]], [[3, 3, 3]]],
)
_r = rnd(8205)
p["tests"].append([[_r.randint(-10 ** 9, 10 ** 9) for _ in range(4000)]])
p["tests"].append([list(range(7000, 0, -1))])
p["tests"].append([list(range(2, 6002)) + [1]])
p["tests"].append([[_r.randint(0, 50) for _ in range(6000)]])


def b_bub(nums):
    a = nums[:]
    passes = 0
    while True:
        swapped = False
        for i in range(len(a) - 1):
            if a[i] > a[i + 1]:
                a[i], a[i + 1] = a[i + 1], a[i]
                swapped = True
        if not swapped:
            return passes
        passes += 1


def v_bub(tests):
    for t in tests:
        a = t["args"][0]
        assert 1 <= len(a) <= 10000 and all(abs(x) <= 10 ** 9 for x in a)


CHECKS["bubble-sort-passes-needed"] = (b_bub, lambda r: [gen_arr(r, -5, 5, 1, 10)], "exact")
VALIDATE["bubble-sort-passes-needed"] = v_bub

p = add(
    id="min-adjacent-swaps-to-match-target", title="Adjacent Swaps to Match a Target", diff="Medium", topic=TOPIC, tier="extra",
    fn="minSwapsToTarget", params=[("nums", "int[]"), ("target", "int[]")], ret="int", cmp="exact",
    desc="<p>The arrays <code>nums</code> and <code>target</code> contain the same multiset of values, possibly with repeats. In one move you may swap two <strong>neighbouring</strong> elements of <code>nums</code>. Return the minimum number of moves needed to turn <code>nums</code> into <code>target</code>.</p>"
         "<pre>nums = [3, 1, 2], target = [1, 2, 3]       -> 2\nnums = [1, 1, 2, 2], target = [2, 2, 1, 1] -> 4\nnums = [5, 5, 7], target = [5, 5, 7]       -> 0</pre>",
    constraints=["1 &le; nums.length = target.length &le; 8,000", "0 &le; nums[i], target[i] &le; 10<sup>9</sup>", "target is a rearrangement of nums"],
    hints=["If all values were distinct, you would know where each element of <code>nums</code> has to end up. How many adjacent swaps does it take to realise a given arrangement of destinations?",
           "With repeated values, it never helps to swap two equal elements past each other. So the k-th occurrence of a value in <code>nums</code> should go to the k-th occurrence of that value in <code>target</code>.",
           "Replace every element of <code>nums</code> by its destination index in <code>target</code> (matching occurrences in order). You now have a permutation of 0..n-1, and the answer is its number of inversions, computed with merge sort in O(n log n)."],
    editorial=["First decide which element goes where. Equal elements are interchangeable, and exchanging two equal elements is wasted work, so the best plan keeps equal elements in their relative order: the k-th copy of v in <code>nums</code> ends at the position of the k-th copy of v in <code>target</code>. Build this by keeping, per value, a queue of its positions in <code>target</code> and popping one for each element of <code>nums</code> from left to right.",
               "This gives an array <code>dest</code> that is a permutation of 0..n-1. Sorting it with adjacent swaps takes exactly as many swaps as it has inversions (each adjacent swap removes at most one inversion, and bubble sort removes one every time). Count the inversions with merge sort.",
               "Total O(n log n) time and O(n) space. The same reduction solves 'adjacent swaps to sort an array' (target is the sorted array) as a special case."],
    time="O(n log n)", space="O(n)",
    solution='''def minSwapsToTarget(nums, target):
    from collections import defaultdict, deque
    where = defaultdict(deque)
    for i, v in enumerate(target):
        where[v].append(i)
    a = [where[v].popleft() for v in nums]
    n = len(a)
    buf = a[:]
    count = 0
    width = 1
    while width < n:
        for lo in range(0, n, 2 * width):
            mid = min(lo + width, n)
            hi = min(lo + 2 * width, n)
            i, j, k = lo, mid, lo
            while i < mid and j < hi:
                if a[i] <= a[j]:
                    buf[k] = a[i]
                    i += 1
                else:
                    buf[k] = a[j]
                    j += 1
                    count += mid - i
                k += 1
            while i < mid:
                buf[k] = a[i]
                i += 1
                k += 1
            while j < hi:
                buf[k] = a[j]
                j += 1
                k += 1
        a, buf = buf, a
        width *= 2
    return count
''',
    tests=[[[3, 1, 2], [1, 2, 3]], [[1, 1, 2, 2], [2, 2, 1, 1]], [[5, 5, 7], [5, 5, 7]], [[9], [9]], [[1, 2], [2, 1]],
           [[1, 2, 1], [2, 1, 1]], [[4, 3, 2, 1], [1, 2, 3, 4]], [[0, 1, 0, 1, 0], [1, 1, 0, 0, 0]], [[7, 7, 7], [7, 7, 7]]],
)
_r = rnd(8206)
_a = [_r.randint(0, 10 ** 9) for _ in range(3000)]
_b = _a[:]; _r.shuffle(_b)
p["tests"].append([_a, _b])
_a = [_r.randint(0, 30) for _ in range(5000)]
_b = sorted(_a, reverse=True)
p["tests"].append([_a, _b])
_a = list(range(1, 4001)); _b = _a[::-1]
p["tests"].append([_a, _b])


def b_swaps(nums, target):
    start, goal = tuple(nums), tuple(target)
    if start == goal:
        return 0
    dist = {start: 0}
    q = deque([start])
    while q:
        s = q.popleft()
        for i in range(len(s) - 1):
            if s[i] != s[i + 1]:
                t = s[:i] + (s[i + 1], s[i]) + s[i + 2:]
                if t not in dist:
                    dist[t] = dist[s] + 1
                    if t == goal:
                        return dist[t]
                    q.append(t)


def g_swaps(r):
    n = r.randint(1, 6)
    a = [r.randint(0, 3) for _ in range(n)]
    b = a[:]
    r.shuffle(b)
    return [a, b]


def v_swaps(tests):
    for t in tests:
        a, b = t["args"]
        assert 1 <= len(a) == len(b) <= 8000 and sorted(a) == sorted(b)
        assert all(0 <= x <= 10 ** 9 for x in a + b)


CHECKS["min-adjacent-swaps-to-match-target"] = (b_swaps, g_swaps, "exact")
VALIDATE["min-adjacent-swaps-to-match-target"] = v_swaps

p = add(
    id="count-pairs-by-paired-difference-bound", title="Pairs With a Bounded Paired Difference", diff="Medium", topic=TOPIC, tier="common",
    fn="countBoundedPairs", params=[("nums1", "int[]"), ("nums2", "int[]"), ("diff", "int")], ret="int", cmp="exact",
    desc="<p>You get two integer arrays <code>nums1</code> and <code>nums2</code> of equal length <code>n</code> and an integer <code>diff</code>. Count the pairs of indices <code>i &lt; j</code> that satisfy</p>"
         "<p><code>nums1[i] - nums1[j] &le; nums2[i] - nums2[j] + diff</code>.</p>"
         "<pre>nums1 = [5, 1, 4], nums2 = [2, 3, 0], diff = 0\nrewritten per index: 3, -2, 4 -> pairs (0,2) and (1,2) qualify  -> 2</pre>",
    constraints=["2 &le; n &le; 8,000", "-10<sup>4</sup> &le; nums1[i], nums2[i] &le; 10<sup>4</sup>", "-10<sup>4</sup> &le; diff &le; 10<sup>4</sup>"],
    hints=["Checking all pairs is O(n<sup>2</sup>). Try to rewrite the inequality so that everything about index i is on one side and everything about index j on the other.",
           "Let <code>d[k] = nums1[k] - nums2[k]</code>. The condition becomes <code>d[i] &le; d[j] + diff</code> for <code>i &lt; j</code>. This is an inversion-style count with a shifted comparison.",
           "Run merge sort on <code>d</code>. When both halves are sorted, for every right value <code>r</code> count the left values <code>&le; r + diff</code> with a pointer that only moves forward, add that to the total, then merge. A Fenwick tree over compressed values also works."],
    editorial=["Moving the terms around gives <code>(nums1[i] - nums2[i]) - (nums1[j] - nums2[j]) &le; diff</code>, i.e. <code>d[i] - d[j] &le; diff</code> with <code>d[k] = nums1[k] - nums2[k]</code>. So the two arrays collapse into one and we must count pairs <code>i &lt; j</code> with <code>d[i] &le; d[j] + diff</code>.",
               "This is the same divide and conquer as counting inversions. Split the array, recurse, and count the crossing pairs (<code>i</code> in the left half, <code>j</code> in the right half). With both halves sorted, as <code>d[j]</code> grows over the sorted right half the threshold <code>d[j] + diff</code> grows, so the number of left values at or below it only grows. One forward-moving pointer yields all counts in linear time. Then merge and return. Counting before merging is what lets the comparison differ from the sort order.",
               "Each level is linear and there are log n levels: O(n log n) time, O(n) memory. Note that <code>diff</code> may be negative, which the same code handles."],
    time="O(n log n)", space="O(n)",
    solution='''def countBoundedPairs(nums1, nums2, diff):
    d = [x - y for x, y in zip(nums1, nums2)]

    def solve(a):
        if len(a) <= 1:
            return a, 0
        mid = len(a) // 2
        left, cl = solve(a[:mid])
        right, cr = solve(a[mid:])
        total = cl + cr
        i = 0
        for r in right:
            while i < len(left) and left[i] <= r + diff:
                i += 1
            total += i
        return sorted(left + right), total

    return solve(d)[1]
''',
    tests=[[[5, 1, 4], [2, 3, 0], 0], [[3, 2, 5], [2, 2, 1], 1], [[3, -1], [-2, 2], -1], [[0, 0], [0, 0], 0], [[1, 2, 3, 4], [0, 0, 0, 0], 10000],
           [[10000, -10000, 10000], [-10000, 10000, -10000], -10000], [[1, 2, 3, 4, 5], [5, 4, 3, 2, 1], 0],
           [[4, 4, 4, 4], [1, 2, 3, 4], 2]],
)
_r = rnd(8207)
p["tests"].append([[_r.randint(-10000, 10000) for _ in range(4000)], [_r.randint(-10000, 10000) for _ in range(4000)], 137])
p["tests"].append([[_r.randint(-10000, 10000) for _ in range(4000)], [_r.randint(-10000, 10000) for _ in range(4000)], -5000])
p["tests"].append([list(range(5000, 0, -1)), [0] * 5000, 0])


def b_pairs(nums1, nums2, diff):
    n = len(nums1)
    return sum(1 for i in range(n) for j in range(i + 1, n) if nums1[i] - nums1[j] <= nums2[i] - nums2[j] + diff)


def g_pairs(r):
    n = r.randint(2, 9)
    return [[r.randint(-6, 6) for _ in range(n)], [r.randint(-6, 6) for _ in range(n)], r.randint(-4, 4)]


def v_pairs(tests):
    for t in tests:
        a, b, d = t["args"]
        assert 2 <= len(a) == len(b) <= 8000 and abs(d) <= 10000
        assert all(abs(x) <= 10000 for x in a + b)


CHECKS["count-pairs-by-paired-difference-bound"] = (b_pairs, g_pairs, "exact")
VALIDATE["count-pairs-by-paired-difference-bound"] = v_pairs

p = add(
    id="inversions-in-repeated-array", title="Inversions in a Repeated Array", diff="Medium", topic=TOPIC, tier="extra",
    fn="repeatedInversions", params=[("nums", "int[]"), ("k", "int")], ret="int", cmp="exact",
    desc="<p>Build a long array by writing <code>nums</code> one after another <code>k</code> times (so its length is <code>n * k</code>). An inversion is a pair of positions <code>p &lt; q</code> in that long array whose values satisfy <code>value[p] &gt; value[q]</code>. Return the number of inversions in the long array, modulo <code>1,000,000,007</code>.</p>"
         "<p><code>k</code> can be huge, so the long array cannot be built.</p>"
         "<pre>nums = [2, 1], k = 3   long array [2,1,2,1,2,1]  -> 6\nnums = [1, 2], k = 2   long array [1,2,1,2]      -> 1\nnums = [4], k = 5      -> 0</pre>",
    constraints=["1 &le; nums.length &le; 8,000", "-10<sup>9</sup> &le; nums[i] &le; 10<sup>9</sup>", "1 &le; k &le; 10<sup>9</sup>"],
    hints=["Look at an inversion in the long array. Its two positions are either in the same copy of <code>nums</code> or in two different copies. Count each case separately.",
           "Inside one copy, the number of inversions is the ordinary inversion count <code>inv</code> of <code>nums</code>, and there are k copies. For two different copies (an earlier and a later one), what matters is how many pairs <code>(x, y)</code> of elements of <code>nums</code> have <code>x &gt; y</code>, regardless of their order in <code>nums</code>.",
           "Let <code>P</code> be the number of index pairs <code>(a, b)</code> (any order) with <code>nums[a] &gt; nums[b]</code>; it equals C(n,2) minus the pairs of equal values. The answer is <code>k * inv + C(k,2) * P</code> modulo 1,000,000,007."],
    editorial=["Pairs in the same copy: each copy contributes the ordinary inversion count <code>inv</code>, so k copies give <code>k * inv</code>. Pairs in different copies: choose an earlier copy and a later copy in C(k,2) ways; for such a choice, any element <code>x</code> of the earlier copy and any element <code>y</code> of the later copy form an inversion when <code>x &gt; y</code>, regardless of their indices. The number of such ordered choices is <code>P = #{(a, b): nums[a] &gt; nums[b]}</code>.",
               "Every unordered pair of positions with different values contributes exactly one such ordered pair, so <code>P = C(n,2) - sum over values v of C(cnt_v, 2)</code>. The inversion count <code>inv</code> comes from merge sort in O(n log n). Finally combine with big integers or modular arithmetic: <code>(k * inv + (k(k-1)/2) * P) mod 1,000,000,007</code>. Beware that C(k,2) is about 5 &times; 10<sup>17</sup> and the product overflows 64 bits unless reduced first.",
               "Time O(n log n), space O(n)."],
    time="O(n log n)", space="O(n)",
    solution='''def repeatedInversions(nums, k):
    from collections import Counter
    M = 1000000007
    n = len(nums)
    a = nums[:]
    buf = a[:]
    inv = 0
    width = 1
    while width < n:
        for lo in range(0, n, 2 * width):
            mid = min(lo + width, n)
            hi = min(lo + 2 * width, n)
            i, j, t = lo, mid, lo
            while i < mid and j < hi:
                if a[i] <= a[j]:
                    buf[t] = a[i]
                    i += 1
                else:
                    buf[t] = a[j]
                    j += 1
                    inv += mid - i
                t += 1
            while i < mid:
                buf[t] = a[i]
                i += 1
                t += 1
            while j < hi:
                buf[t] = a[j]
                j += 1
                t += 1
        a, buf = buf, a
        width *= 2
    pairs = n * (n - 1) // 2 - sum(c * (c - 1) // 2 for c in Counter(nums).values())
    return (k * inv + (k * (k - 1) // 2) % M * pairs) % M
''',
    tests=[[[2, 1], 3], [[1, 2], 2], [[4], 5], [[3, 1, 2], 1], [[1, 1, 1], 1000000000], [[5, 4, 3, 2, 1], 7], [[2, 1], 1000000000],
           [[-3, 0, -3, 5], 12], [[1000000000, -1000000000], 999999999]],
)
_r = rnd(8208)
p["tests"].append([[_r.randint(-10 ** 9, 10 ** 9) for _ in range(4000)], 1000000000])
p["tests"].append([[_r.randint(0, 10) for _ in range(6000)], 123456789])
p["tests"].append([list(range(6000, 0, -1)), 777777777])


def b_rep(nums, k):
    long = nums * k
    return _inv(long) % MOD


def g_rep(r):
    return [gen_arr(r, -4, 4, 1, 6), r.randint(1, 4)]


def v_rep(tests):
    for t in tests:
        a, k = t["args"]
        assert 1 <= len(a) <= 8000 and 1 <= k <= 10 ** 9 and all(abs(x) <= 10 ** 9 for x in a)


CHECKS["inversions-in-repeated-array"] = (b_rep, g_rep, "exact")
VALIDATE["inversions-in-repeated-array"] = v_rep

# ---------------------------------------------------------------- HARD

p = add(
    id="count-decreasing-triples", title="Count Strictly Decreasing Triples", diff="Hard", topic=TOPIC, tier="extra",
    fn="countDecreasingTriples", params=[("nums", "int[]")], ret="int", cmp="exact",
    desc="<p>Count the triples of indices <code>i &lt; j &lt; k</code> with <code>nums[i] &gt; nums[j] &gt; nums[k]</code> (both comparisons strict). The positions need not be adjacent. Return the count modulo <code>1,000,000,007</code>.</p>"
         "<pre>nums = [5, 3, 4, 2, 1]  -> 7\nnums = [1, 2, 3]        -> 0\nnums = [3, 3, 2, 1]     -> 2</pre>",
    constraints=["1 &le; nums.length &le; 8,000", "-10<sup>9</sup> &le; nums[i] &le; 10<sup>9</sup>", "Values may repeat"],
    hints=["Trying all triples is O(n<sup>3</sup>), and even trying every pair (i, j) and then looking for k is O(n<sup>2</sup>) or worse. Fix the <em>middle</em> index j and think about the two sides separately.",
           "For a fixed middle j, the choices of i and k are independent: the number of triples with middle j is (number of earlier elements strictly greater than <code>nums[j]</code>) &times; (number of later elements strictly smaller than <code>nums[j]</code>).",
           "Compute both counts for every j with a Fenwick tree over compressed values (or a merge-sort based counter), once from the left for 'greater before' and once from the right for 'smaller after'. Sum the products modulo 1,000,000,007."],
    editorial=["Anchor on the middle element. A triple with middle index j is built by picking any earlier element larger than <code>nums[j]</code> and any later element smaller than <code>nums[j]</code>, with no interaction between the two choices. So the answer is the sum over j of <code>greaterBefore[j] * smallerAfter[j]</code>.",
               "Both arrays are the classic 'count of smaller/greater numbers on one side' problems. Compress the values to ranks and sweep with a Fenwick tree: from left to right, <code>greaterBefore[j] = j - (count of earlier values &le; nums[j])</code>; from right to left, <code>smallerAfter[j] = (count of later values &lt; nums[j])</code>. Strictness is handled by using &le; in the first and &lt; in the second prefix queries.",
               "The number of triples can reach C(8000, 3), roughly 8.5 &times; 10<sup>11</sup>, so reduce the sum modulo 1,000,000,007 (each product is below 6.4 &times; 10<sup>7</sup> here, but use 64-bit arithmetic for the running total). Time O(n log n), space O(n)."],
    time="O(n log n)", space="O(n)",
    solution='''def countDecreasingTriples(nums):
    M = 1000000007
    n = len(nums)
    vals = sorted(set(nums))
    rank = {v: i + 1 for i, v in enumerate(vals)}
    m = len(vals)
    r = [rank[x] for x in nums]

    greater_before = [0] * n
    tree = [0] * (m + 1)
    for i in range(n):
        k = r[i]
        le = 0
        while k > 0:
            le += tree[k]
            k -= k & -k
        greater_before[i] = i - le
        k = r[i]
        while k <= m:
            tree[k] += 1
            k += k & -k

    total = 0
    tree = [0] * (m + 1)
    for i in range(n - 1, -1, -1):
        k = r[i] - 1
        smaller = 0
        while k > 0:
            smaller += tree[k]
            k -= k & -k
        total += greater_before[i] * smaller
        k = r[i]
        while k <= m:
            tree[k] += 1
            k += k & -k
    return total % M
''',
    tests=[[[5, 3, 4, 2, 1]], [[1, 2, 3]], [[3, 3, 2, 1]], [[1]], [[3, 2, 1]], [[2, 1]], [[4, 4, 4, 4]], [[9, 8, 7, 6, 5, 4, 3, 2, 1]],
           [[1000000000, 0, -1000000000, 1000000000, 0, -1000000000]]],
)
_r = rnd(8209)
p["tests"].append([[_r.randint(-10 ** 9, 10 ** 9) for _ in range(4000)]])
p["tests"].append([list(range(6000, 0, -1))])
p["tests"].append([[_r.randint(0, 40) for _ in range(6000)]])


def b_trip(nums):
    n = len(nums)
    t = 0
    for i in range(n):
        for j in range(i + 1, n):
            if nums[i] > nums[j]:
                for k in range(j + 1, n):
                    if nums[j] > nums[k]:
                        t += 1
    return t % MOD


def v_trip(tests):
    for t in tests:
        a = t["args"][0]
        assert 1 <= len(a) <= 8000 and all(abs(x) <= 10 ** 9 for x in a)
    assert any(t["expected"] >= 10 ** 6 for t in tests)


CHECKS["count-decreasing-triples"] = (b_trip, lambda r: [gen_arr(r, -5, 5, 1, 12)], "exact")
VALIDATE["count-decreasing-triples"] = v_trip

p = add(
    id="sum-of-inversion-distances", title="Sum of Inversion Distances", diff="Hard", topic=TOPIC, tier="extra",
    fn="inversionDistanceSum", params=[("nums", "int[]")], ret="int", cmp="exact",
    desc="<p>For every inversion, a pair of indices <code>i &lt; j</code> with <code>nums[i] &gt; nums[j]</code>, define its <em>distance</em> as <code>j - i</code>. Return the sum of the distances of all inversions, modulo <code>1,000,000,007</code>.</p>"
         "<pre>nums = [3, 1, 2]     inversions (0,1) distance 1 and (0,2) distance 2  -> 3\nnums = [2, 2, 1, 1]  (0,2) 2, (0,3) 3, (1,2) 1, (1,3) 2           -> 8\nnums = [1, 2, 3]     -> 0</pre>",
    constraints=["1 &le; nums.length &le; 8,000", "-10<sup>9</sup> &le; nums[i] &le; 10<sup>9</sup>", "Values may repeat; equal values never form an inversion"],
    hints=["Listing the inversions is O(n<sup>2</sup>) in the worst case. Group them by the right index j instead: the contribution of all inversions ending at j is a simple expression.",
           "For a fixed j, let S be the set of earlier indices i with <code>nums[i] &gt; nums[j]</code>. Their total distance is <code>|S| * j - (sum of the indices in S)</code>. So you need both a count and a sum of indices for 'earlier and larger'.",
           "Compress the values to ranks and keep two Fenwick trees over ranks: one storing counts and one storing index sums. Querying the suffix (ranks above the current one) gives both numbers for each j in O(log n)."],
    editorial=["Sweep j from left to right and imagine all earlier elements inserted into a structure keyed by value rank. The inversions that end at j are the earlier elements with a strictly larger value. If there are c of them with index sum s, their distances add up to <code>c * j - s</code>.",
               "So we need, for a rank threshold, the count and the index sum of the elements above it. Two Fenwick trees do this: one adds 1 at the element's rank, the other adds its index. The values above rank r equal the total inserted so far minus the prefix up to r. Accumulate the sum with big or 64-bit integers and reduce modulo 1,000,000,007 at the end (the exact sum can reach about n<sup>3</sup>/6, around 8.5 &times; 10<sup>10</sup> here, which is more than 32 bits).",
               "Time O(n log n), space O(n). A merge-sort version also works: carry the sum of original indices along with each sorted element."],
    time="O(n log n)", space="O(n)",
    solution='''def inversionDistanceSum(nums):
    M = 1000000007
    vals = sorted(set(nums))
    rank = {v: i + 1 for i, v in enumerate(vals)}
    m = len(vals)
    cnt = [0] * (m + 1)
    idx = [0] * (m + 1)
    total = 0
    seen = 0
    seen_idx = 0
    for j, x in enumerate(nums):
        r = rank[x]
        k = r
        c = 0
        s = 0
        while k > 0:
            c += cnt[k]
            s += idx[k]
            k -= k & -k
        greater_cnt = seen - c
        greater_idx = seen_idx - s
        total += greater_cnt * j - greater_idx
        k = r
        while k <= m:
            cnt[k] += 1
            idx[k] += j
            k += k & -k
        seen += 1
        seen_idx += j
    return total % M
''',
    tests=[[[3, 1, 2]], [[2, 2, 1, 1]], [[1, 2, 3]], [[5]], [[2, 1]], [[4, 3, 2, 1]], [[1, 1, 1]], [[3, 1, 4, 1, 5, 9, 2, 6]],
           [[1000000000, -1000000000, 0]]],
)
_r = rnd(8210)
p["tests"].append([[_r.randint(-10 ** 9, 10 ** 9) for _ in range(4000)]])
p["tests"].append([list(range(7000, 0, -1))])
p["tests"].append([[_r.randint(0, 30) for _ in range(6000)]])


def b_dist(nums):
    n = len(nums)
    return sum(j - i for i in range(n) for j in range(i + 1, n) if nums[i] > nums[j]) % MOD


def v_dist(tests):
    for t in tests:
        a = t["args"][0]
        assert 1 <= len(a) <= 8000 and all(abs(x) <= 10 ** 9 for x in a)
    assert any(t["expected"] > 10 ** 6 for t in tests)


CHECKS["sum-of-inversion-distances"] = (b_dist, lambda r: [gen_arr(r, -5, 5, 1, 12)], "exact")
VALIDATE["sum-of-inversion-distances"] = v_dist

p = add(
    id="permutations-with-k-inversions", title="Permutations With Exactly K Inversions", diff="Hard", topic=TOPIC, tier="extra",
    fn="countPermutationsWithInversions", params=[("n", "int"), ("k", "int")], ret="int", cmp="exact",
    desc="<p>An inversion of a permutation <code>p</code> of <code>1..n</code> is a pair <code>i &lt; j</code> with <code>p[i] &gt; p[j]</code>. Return how many permutations of <code>1..n</code> have exactly <code>k</code> inversions, modulo <code>1,000,000,007</code>.</p>"
         "<pre>n = 3, k = 0  -> 1   [1,2,3]\nn = 3, k = 1  -> 2   [1,3,2] [2,1,3]\nn = 4, k = 2  -> 5\nn = 2, k = 5  -> 0</pre>",
    constraints=["1 &le; n &le; 1,000", "0 &le; k &le; 1,000"],
    hints=["You cannot list permutations. Build them by inserting values one at a time and track the inversion count. What happens to the count when the new, largest value is inserted somewhere?",
           "Take a permutation of 1..i-1 and insert the value i. If it is placed with t elements after it, it forms exactly t new inversions, and t can be anything from 0 to i-1. So <code>dp[i][j] = dp[i-1][j] + dp[i-1][j-1] + ... + dp[i-1][j-(i-1)]</code>.",
           "That inner sum is a sliding window over the previous row, so keep a running prefix sum: <code>dp[i][j] = dp[i][j-1] + dp[i-1][j] - dp[i-1][j-i]</code> (drop the last term when <code>j &lt; i</code>). Reduce modulo 1,000,000,007 and keep only two rows."],
    editorial=["Let <code>dp[i][j]</code> be the number of permutations of <code>1..i</code> with exactly j inversions. Insert the largest value i into a permutation of <code>1..i-1</code>: the number of elements placed to its right, t, is between 0 and i - 1, each choice gives a different permutation, and creates exactly t new inversions because i is bigger than everything. Therefore <code>dp[i][j] = sum_{t=0}^{min(j, i-1)} dp[i-1][j-t]</code>.",
               "Computing that sum for each cell costs O(n) and leads to O(n<sup>2</sup>k). But consecutive cells share all but two terms, so with <code>dp[i][j] = dp[i][j-1] + dp[i-1][j] - dp[i-1][j-i]</code> (the last term only when <code>j &ge; i</code>) every cell costs O(1). Take care that subtraction modulo p must be adjusted to be non-negative.",
               "Total O(n * k) time and O(k) space with two rolling rows. The answer is <code>dp[n][k]</code>; for <code>k &gt; n(n-1)/2</code> it is naturally 0."],
    time="O(n * k)", space="O(k)",
    solution='''def countPermutationsWithInversions(n, k):
    M = 1000000007
    prev = [0] * (k + 1)
    prev[0] = 1
    for i in range(2, n + 1):
        cur = [0] * (k + 1)
        cur[0] = 1
        for j in range(1, k + 1):
            v = cur[j - 1] + prev[j]
            if j >= i:
                v -= prev[j - i]
            cur[j] = v % M
        prev = cur
    return prev[k]
''',
    tests=[[3, 0], [3, 1], [4, 2], [2, 5], [1, 0], [1, 3], [5, 10], [5, 4], [6, 7], [10, 0], [10, 45], [10, 20], [1000, 1000], [1000, 500], [600, 1000]],
)


def b_perm(n, k):
    if n <= 8:
        return sum(1 for p_ in permutations(range(n)) if _inv(p_) == k) % MOD
    # independent method: generating function  prod(1 - x^i) / (1 - x)^n, coefficient of x^k
    num = [0] * (k + 1)
    num[0] = 1
    for i in range(1, n + 1):
        for j in range(k, i - 1, -1):
            num[j] = (num[j] - num[j - i]) % MOD
    f = [1] * (n + k + 1)
    for i in range(1, n + k + 1):
        f[i] = f[i - 1] * i % MOD

    def binom(a, b):
        return f[a] * pow(f[b] * f[a - b] % MOD, MOD - 2, MOD) % MOD

    return sum(num[m] * binom(n - 1 + k - m, k - m) for m in range(k + 1)) % MOD


def g_perm(r):
    return [r.randint(1, 7), r.randint(0, 24)]


def v_perm(tests):
    for t in tests:
        n, k = t["args"]
        assert 1 <= n <= 1000 and 0 <= k <= 1000


CHECKS["permutations-with-k-inversions"] = (b_perm, g_perm, "exact")
VALIDATE["permutations-with-k-inversions"] = v_perm
