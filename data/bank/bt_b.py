"""Problems: backtracking, permutations (derangements, k-th permutation, constrained arrangements). See data/lib.py for the registry."""
from collections import Counter
from itertools import islice, permutations as _perms
from math import factorial as _fact

from lib import add, rnd, CHECKS, VALIDATE, gen_arr  # noqa: F401

TOPIC = "Backtracking"
MOD = 10 ** 9 + 7
INT_MAX = 2 ** 31 - 1


# ================================================================== EASY

# ---------------------------------------------------------------- list derangements
add(
    id="list-derangements", title="List All Derangements", diff="Easy", topic=TOPIC,
    fn="listDerangements", params=[("n", "int")], ret="int[][]", cmp="rowset",
    desc='''<p>A <em>derangement</em> of <code>1..n</code> is an ordering <code>p</code> of the numbers <code>1..n</code> in which no number sits at its own place: <code>p[i] != i + 1</code> for every index <code>i</code> (0-indexed). In other words, the number <code>1</code> may not be first, <code>2</code> may not be second, and so on.</p><p>Return every derangement as a row. Rows may be returned in any order. If there is none, return an empty list.</p><pre>n = 3  ->  [[2,3,1], [3,1,2]]
n = 2  ->  [[2,1]]
n = 1  ->  []</pre>''',
    constraints=["1 &le; n &le; 7", "There are at most 1,854 derangements for these values of n"],
    hints=["Build the ordering from the left, one slot at a time, and keep track of which numbers are already used.",
           "Slot <code>i</code> (0-indexed) may take any unused number except <code>i + 1</code>.",
           "Recurse slot by slot. When all <code>n</code> slots are filled, copy the current row into the answer. Undo your choice (mark the number unused again) before trying the next number."],
    editorial=["This is the standard permutation search with one extra rule. Keep a <code>used</code> flag per number and the current row. At slot <code>i</code> try every number <code>v</code> from 1 to n that is unused and different from <code>i + 1</code>; place it, recurse to slot <code>i + 1</code>, then remove it. When the row is full it is a derangement, so store a copy.",
               "Because the rule is checked while the row is built, branches that already break it are never extended. The number of rows is the derangement number D(n) = 1, 0, 1, 2, 9, 44, 265, 1854 for n = 0..7, so the work is roughly proportional to the output size times n."],
    time="O(n &middot; D(n))", space="O(n) extra",
    solution='''def listDerangements(n):
    res = []
    cur = []
    used = [False] * (n + 1)

    def go(i):
        if i == n:
            res.append(cur[:])
            return
        for v in range(1, n + 1):
            if used[v] or v == i + 1:
                continue
            used[v] = True
            cur.append(v)
            go(i + 1)
            cur.pop()
            used[v] = False

    go(0)
    return res
''',
    tests=[[1], [2], [3], [4], [5], [6], [7]],
)

_DER = [1, 0, 1, 2, 9, 44, 265, 1854]


def b_listder(n):
    return [list(p) for p in _perms(range(1, n + 1)) if all(p[i] != i + 1 for i in range(n))]


def v_listder(tests):
    for t in tests:
        n, res = t["args"][0], t["expected"]
        assert 1 <= n <= 7
        assert len(res) == _DER[n] and len({tuple(r) for r in res}) == len(res)
        assert all(sorted(r) == list(range(1, n + 1)) and all(r[i] != i + 1 for i in range(n)) for r in res)


CHECKS["list-derangements"] = (b_listder, lambda r: [r.randint(1, 6)], "rowset")
VALIDATE["list-derangements"] = v_listder


# ---------------------------------------------------------------- ordered selections of size k
add(
    id="ordered-selections-of-size-k", title="Ordered Selections of Size K", diff="Easy", topic=TOPIC,
    fn="orderedSelections", params=[("nums", "int[]"), ("k", "int")], ret="int[][]", cmp="rowset",
    desc='''<p>You have <code>n</code> different numbers in <code>nums</code> and you want to line up exactly <code>k</code> of them in a row. Return every possible row. Two rows are different if they differ in at least one position, so <code>[1,2]</code> and <code>[2,1]</code> are both listed.</p><p>Rows may be returned in any order.</p><pre>nums = [1,2,3], k = 2  ->  [[1,2],[1,3],[2,1],[2,3],[3,1],[3,2]]
nums = [7],     k = 1  ->  [[7]]</pre>''',
    constraints=["1 &le; k &le; nums.length &le; 7", "-100 &le; nums[i] &le; 100 and all values are different", "The number of rows n! / (n - k)! is at most 5,040"],
    hints=["If k equals n this is the classic task of listing all orderings. Think about what changes when you stop early.",
           "Fill the row from the left. At each slot try every number that is not already in the row.",
           "Stop recursing as soon as the row has <code>k</code> numbers and store a copy of it. Mark numbers used while they are in the row and free them again when you step back."],
    editorial=["Use a recursive search over positions of the row. Keep a <code>used</code> flag per index of <code>nums</code> and the current row. If the row already has <code>k</code> numbers, save a copy and return. Otherwise try each unused index, append its value, recurse, and undo.",
               "The search tree has depth k and each node at depth d has n - d children, so the number of leaves is exactly n!/(n-k)! and every leaf is an answer; nothing is wasted. Time is O(k &middot; n!/(n-k)!) including copying the rows."],
    time="O(k &middot; n! / (n-k)!)", space="O(n) extra",
    solution='''def orderedSelections(nums, k):
    n = len(nums)
    res = []
    cur = []
    used = [False] * n

    def go():
        if len(cur) == k:
            res.append(cur[:])
            return
        for i in range(n):
            if used[i]:
                continue
            used[i] = True
            cur.append(nums[i])
            go()
            cur.pop()
            used[i] = False

    go()
    return res
''',
    tests=[[[1, 2, 3], 2], [[7], 1], [[1, 2], 2], [[4, -1, 7], 3], [[1, 2, 3, 4], 2], [[1, 2, 3, 4, 5], 3], [[9, 8, 7, 6], 4],
           [[-3, 0, 3, 6, 9], 1], [[10, 20, 30, 40, 50, 60], 4], [[1, 2, 3, 4, 5, 6, 7], 3], [[-5, 5, 0, 12, 99, -100], 6],
           [[1, 2, 3, 4, 5, 6, 7], 4]],
)


def b_sel(nums, k):
    return [list(t) for t in _perms(nums, k)]


def g_sel(r):
    n = r.randint(1, 5)
    nums = r.sample(range(-9, 10), n)
    return [nums, r.randint(1, n)]


def v_sel(tests):
    for t in tests:
        nums, k = t["args"]
        res = t["expected"]
        n = len(nums)
        assert 1 <= k <= n <= 7 and len(set(nums)) == n and all(-100 <= x <= 100 for x in nums)
        assert len(res) == _fact(n) // _fact(n - k) <= 5040 and len({tuple(r) for r in res}) == len(res)
        assert all(len(r) == k and set(r) <= set(nums) and len(set(r)) == k for r in res)


CHECKS["ordered-selections-of-size-k"] = (b_sel, g_sel, "rowset")
VALIDATE["ordered-selections-of-size-k"] = v_sel


# ================================================================== MEDIUM

# ---------------------------------------------------------------- k-th permutation
add(
    id="kth-permutation-sequence", title="K-th Permutation in Order", diff="Medium", topic=TOPIC,
    fn="kthPermutation", params=[("n", "int"), ("k", "int")], ret="int[]", cmp="exact",
    desc='''<p>Write down all <code>n!</code> orderings of the numbers <code>1..n</code> in increasing lexicographic order (compare the first numbers, then the second numbers, and so on). Return the <code>k</code>-th ordering of that list, counting from 1, as an array.</p><p>Do not generate the whole list; for large <code>n</code> it is far too long.</p><pre>n = 3, k = 4  ->  [2,3,1]    (list: 123, 132, 213, 231, 312, 321)
n = 3, k = 1  ->  [1,2,3]
n = 4, k = 9  ->  [2,3,1,4]</pre>''',
    constraints=["1 &le; n &le; 20", "1 &le; k &le; min(n!, 2<sup>31</sup> - 1)"],
    hints=["For n = 3 look at the list: the first two orderings start with 1, the next two with 2, the last two with 3. How large is each block of orderings that share the first number?",
           "Each block has (n-1)! orderings. So <code>(k-1) // (n-1)!</code> tells you which of the still unused numbers (in increasing order) comes first.",
           "Take that number out of the pool, replace k by <code>(k-1) % (n-1)!</code>, and repeat for the next slot with blocks of size (n-2)!, then (n-3)!, and so on."],
    editorial=["The lexicographic list is split into n equal blocks by the first number, each of size (n-1)!. With the zero-based rank <code>r = k - 1</code> the first number is the <code>r // (n-1)!</code>-th smallest unused number, and the rank inside the block is <code>r % (n-1)!</code>. The same argument applies to the remaining slots with the remaining numbers (the factorial number system).",
               "Keep the unused numbers in a sorted list and pop the chosen index each time. That is O(n<sup>2</sup>) for the pops, trivial for n &le; 20. No search through the list is needed, so the huge value of n! never matters."],
    time="O(n<sup>2</sup>)", space="O(n)",
    solution='''def kthPermutation(n, k):
    fact = [1] * (n + 1)
    for i in range(1, n + 1):
        fact[i] = fact[i - 1] * i
    pool = list(range(1, n + 1))
    r = k - 1
    res = []
    for i in range(n, 0, -1):
        idx, r = divmod(r, fact[i - 1])
        res.append(pool.pop(idx))
    return res
''',
    tests=[[1, 1], [2, 1], [2, 2], [3, 4], [4, 9], [4, 24], [5, 100], [6, 1], [9, 362880], [12, 479001600], [13, 2147483647],
           [20, 1], [20, 2147483647], [15, 987654321]],
)


def b_kperm(n, k):
    return list(next(islice(_perms(range(1, n + 1)), k - 1, None)))


def g_kperm(r):
    n = r.randint(1, 6)
    return [n, r.randint(1, _fact(n))]


def v_kperm(tests):
    for t in tests:
        n, k = t["args"]
        assert 1 <= n <= 20 and 1 <= k <= min(_fact(n), INT_MAX)
        assert sorted(t["expected"]) == list(range(1, n + 1))


CHECKS["kth-permutation-sequence"] = (b_kperm, g_kperm, "exact")
VALIDATE["kth-permutation-sequence"] = v_kperm


# ---------------------------------------------------------------- smallest permutation from DI pattern
_p = add(
    id="smallest-permutation-from-di-pattern", title="Smallest Permutation From a Pattern", diff="Medium", topic=TOPIC,
    fn="smallestFromPattern", params=[("pattern", "string")], ret="int[]", cmp="exact",
    desc='''<p>The string <code>pattern</code> has <code>m</code> characters, each either <code>I</code> (increase) or <code>D</code> (decrease). An ordering <code>p</code> of the numbers <code>1..m+1</code> <em>fits</em> the pattern if for every index <code>i</code> from 0 to m-1: <code>p[i] &lt; p[i+1]</code> when <code>pattern[i]</code> is <code>I</code>, and <code>p[i] &gt; p[i+1]</code> when it is <code>D</code>.</p><p>Return the lexicographically smallest ordering that fits (compare the first numbers, then the second numbers, and so on).</p><pre>pattern = "ID"    ->  [1,3,2]
pattern = "DD"    ->  [3,2,1]
pattern = "DI"    ->  [2,1,3]
pattern = "IDID"  ->  [1,3,2,5,4]</pre>''',
    constraints=["1 &le; m = pattern.length &le; 5,000", "pattern contains only the letters I and D", "A fitting ordering always exists"],
    hints=["Try the pattern <code>DDD</code> by hand. The only fitting ordering is the fully descending one. What does a run of D's force?",
           "Smaller numbers should be placed as early as possible, but a run of D's needs some larger numbers to come first and then fall.",
           "Go through the numbers 1, 2, 3, ... in order and push each on a stack. Whenever the pattern says I (or the pattern is over), pop the whole stack into the answer: this reverses each run of D's."],
    editorial=["Backtracking works for tiny m: try numbers for each slot in increasing order and take the first complete fit. For m up to 5,000 a direct construction is needed.",
               "Split the pattern into groups: a group is a maximal run of D's together with the position right before the next I. Inside a group of length L the numbers must fall, and to keep the answer smallest the group should use the next L numbers in decreasing order, so the group is reversed. Groups themselves must be increasing (that is what I means), so they use consecutive blocks of 1, 2, 3, ... in order. The stack does it: push i + 1 for each position, and when position i is followed by I (or is the last), pop everything.",
               "Each number is pushed and popped once, so the time is O(m)."],
    time="O(m)", space="O(m)",
    solution='''def smallestFromPattern(pattern):
    m = len(pattern)
    res = []
    stack = []
    for i in range(m + 1):
        stack.append(i + 1)
        if i == m or pattern[i] == 'I':
            while stack:
                res.append(stack.pop())
    return res
''',
    tests=[["I"], ["D"], ["ID"], ["DI"], ["DD"], ["II"], ["IDID"], ["DDIIDD"], ["DIDIDIDI"], ["IIIIIII"], ["DDDDDDD"]],
)
_r = rnd(4401)
_p["tests"].append(["".join(_r.choice("ID") for _ in range(3000))])
_p["tests"].append(["I" * 700 + "D" * 700 + "I" * 600 + "DDI" * 300])
_p["tests"].append(["D" * 2000])


def b_dipat(pattern):
    m = len(pattern)
    for p in _perms(range(1, m + 2)):
        if all((p[i] < p[i + 1]) == (pattern[i] == "I") for i in range(m)):
            return list(p)


def v_dipat(tests):
    for t in tests:
        pat, p = t["args"][0], t["expected"]
        m = len(pat)
        assert 1 <= m <= 5000 and set(pat) <= {"I", "D"}
        assert sorted(p) == list(range(1, m + 2))
        assert all((p[i] < p[i + 1]) == (pat[i] == "I") for i in range(m))


CHECKS["smallest-permutation-from-di-pattern"] = (b_dipat, lambda r: ["".join(r.choice("ID") for _ in range(r.randint(1, 7)))], "exact")
VALIDATE["smallest-permutation-from-di-pattern"] = v_dipat


# ---------------------------------------------------------------- advance a permutation by k steps
_p = add(
    id="skip-ahead-in-permutation-order", title="Skip Ahead in Permutation Order", diff="Medium", topic=TOPIC,
    fn="advancePermutation", params=[("perm", "int[]"), ("k", "int")], ret="int[]", cmp="exact",
    desc='''<p>List all <code>n!</code> orderings of <code>1..n</code> in increasing lexicographic order and bend the list into a circle: the step after the last (fully descending) ordering leads back to the first (fully ascending) one.</p><p>You are given <code>perm</code>, one of these orderings, and a non-negative integer <code>k</code>. Walk <code>k</code> steps forward along the circle from <code>perm</code> and return the ordering where you land. A step is what the usual "next permutation" operation does.</p><pre>perm = [1,2,3], k = 3   ->  [2,3,1]
perm = [3,2,1], k = 1   ->  [1,2,3]
perm = [2,1,3], k = 6   ->  [2,1,3]    (a full circle of 6 steps)
perm = [1,3,2], k = 10  ->  [3,2,1]</pre>''',
    constraints=["1 &le; n = perm.length &le; 20", "perm is an ordering of 1..n", "0 &le; k &le; 2<sup>31</sup> - 1"],
    hints=["Applying the next-permutation step k times is far too slow when k is in the billions. Is there a way to jump?",
           "If you know the position (rank) of <code>perm</code> in the sorted list of all orderings, moving k steps just adds k to that rank, wrapping around after n! orderings.",
           "Compute the rank with factorials (for each slot count the smaller numbers that come later), add k modulo n!, and turn the new rank back into an ordering by the factorial-base method."],
    editorial=["Each ordering has a zero-based rank in the lexicographic list. For the rank, go through the slots: at slot i count how many numbers to the right of it are smaller than <code>perm[i]</code>; that count times (n-1-i)! summed over all slots is the rank.",
               "Moving k steps (with wrap-around) gives the new rank <code>(rank + k) mod n!</code>. Convert it back by repeated division: for the slot with block size (n-1-i)! the quotient is the index into the sorted list of unused numbers, the remainder carries on. Both directions cost O(n<sup>2</sup>), and Python's big integers handle 20! without trouble; in languages with 64-bit integers 20! still fits.",
               "Simulating the k steps is O(k &middot; n), which only works for small k."],
    time="O(n<sup>2</sup>)", space="O(n)",
    solution='''def advancePermutation(perm, k):
    n = len(perm)
    fact = [1] * (n + 1)
    for i in range(1, n + 1):
        fact[i] = fact[i - 1] * i
    rank = 0
    for i in range(n):
        smaller = 0
        for j in range(i + 1, n):
            if perm[j] < perm[i]:
                smaller += 1
        rank += smaller * fact[n - 1 - i]
    rank = (rank + k) % fact[n]
    pool = list(range(1, n + 1))
    res = []
    for i in range(n):
        idx, rank = divmod(rank, fact[n - 1 - i])
        res.append(pool.pop(idx))
    return res
''',
    tests=[[[1], 0], [[1], 5], [[1, 2, 3], 3], [[3, 2, 1], 1], [[2, 1, 3], 6], [[1, 3, 2], 10], [[1, 2, 3, 4], 23], [[4, 3, 2, 1], 1],
           [[2, 4, 1, 3], 100], [list(range(1, 21)), 2147483647], [list(range(20, 0, -1)), 1], [[5, 1, 4, 2, 3], 0]],
)
_r = rnd(4402)
for _n, _k in [(20, 123456789), (12, 2147483647), (17, 1000000007)]:
    _a = list(range(1, _n + 1)); _r.shuffle(_a)
    _p["tests"].append([_a, _k])


def b_advance(perm, k):
    n = len(perm)
    allp = list(_perms(range(1, n + 1)))
    return list(allp[(allp.index(tuple(perm)) + k) % len(allp)])


def g_advance(r):
    n = r.randint(1, 6)
    p = list(range(1, n + 1))
    r.shuffle(p)
    return [p, r.randint(0, 1500)]


def v_advance(tests):
    for t in tests:
        perm, k = t["args"]
        assert 1 <= len(perm) <= 20 and sorted(perm) == list(range(1, len(perm) + 1)) and 0 <= k <= INT_MAX
        assert sorted(t["expected"]) == sorted(perm)


CHECKS["skip-ahead-in-permutation-order"] = (b_advance, g_advance, "exact")
VALIDATE["skip-ahead-in-permutation-order"] = v_advance


# ---------------------------------------------------------------- exactly k fixed points
add(
    id="permutations-with-exactly-k-fixed-points", title="Orderings With Exactly K Fixed Points", diff="Medium", topic=TOPIC,
    fn="countWithFixedPoints", params=[("n", "int"), ("k", "int")], ret="int", cmp="exact",
    desc='''<p>A <em>fixed point</em> of an ordering <code>p</code> of the numbers <code>1..n</code> is an index <code>i</code> (0-indexed) with <code>p[i] = i + 1</code>, a number that sits at its own place.</p><p>Return how many of the <code>n!</code> orderings of <code>1..n</code> have exactly <code>k</code> fixed points, modulo <code>1,000,000,007</code>.</p><pre>n = 3, k = 0  ->  2    ([2,3,1], [3,1,2])
n = 3, k = 1  ->  3    ([1,3,2], [3,2,1], [2,1,3])
n = 3, k = 2  ->  0
n = 3, k = 3  ->  1
n = 4, k = 2  ->  6</pre>''',
    constraints=["1 &le; n &le; 100,000", "0 &le; k &le; n"],
    hints=["Look at the case k = 0 first: orderings with no number in its own place are called derangements. Let D(m) be their count for m numbers.",
           "For exactly k fixed points, first decide <em>which</em> k numbers stay in place. The remaining n - k numbers must then form a derangement on their own positions.",
           "The answer is <code>C(n, k) * D(n - k)</code>. For D use the recurrence <code>D(m) = (m - 1) * (D(m - 1) + D(m - 2))</code> with <code>D(0) = 1</code>, <code>D(1) = 0</code>, and get C from factorials and modular inverses."],
    editorial=["Choose the k fixed numbers in C(n, k) ways. Each of the other n - k numbers must avoid its own place, and since the fixed ones are already placed, they only move among the remaining n - k places. The number of ways is the derangement number D(n - k), so the answer is C(n, k) &middot; D(n - k).",
               "Derangement recurrence: look at the number that ends up in place 1, say it is j (m - 1 choices). Either number 1 goes to place j (the other m - 2 numbers form a derangement: D(m-2)) or it does not (then, after renaming, the remaining m - 1 numbers must form a derangement: D(m-1)). Hence D(m) = (m-1)(D(m-1) + D(m-2)).",
               "Compute factorials and D up to n modulo p = 10<sup>9</sup> + 7, and the binomial as <code>n! / (k! (n-k)!)</code> using Fermat's inverse <code>x<sup>p-2</sup></code>. Everything is O(n)."],
    time="O(n)", space="O(n)",
    solution='''def countWithFixedPoints(n, k):
    M = 1000000007
    fact = [1] * (n + 1)
    for i in range(1, n + 1):
        fact[i] = fact[i - 1] * i % M
    m = n - k
    d0, d1 = 1, 0  # D(0), D(1)
    if m == 0:
        der = 1
    else:
        for i in range(2, m + 1):
            d0, d1 = d1, (i - 1) * (d0 + d1) % M
        der = d1
    comb = fact[n] * pow(fact[k] * fact[n - k] % M, M - 2, M) % M
    return comb * der % M
''',
    tests=[[1, 0], [1, 1], [2, 0], [2, 1], [2, 2], [3, 0], [3, 1], [3, 3], [4, 2], [5, 0], [6, 3], [10, 4], [1000, 0], [100000, 0],
           [100000, 99998], [100000, 50000], [99999, 99999]],
)


def b_fixed(n, k):
    if n <= 7:
        return sum(1 for p in _perms(range(1, n + 1)) if sum(p[i] == i + 1 for i in range(n)) == k) % MOD
    # inclusion-exclusion with exact integers: D(m) = sum_j (-1)^j m!/j!
    m = n - k
    der = sum((-1) ** j * (_fact(m) // _fact(j)) for j in range(m + 1))
    return _fact(n) // (_fact(k) * _fact(m)) * der % MOD


def v_fixed(tests):
    for t in tests:
        n, k = t["args"]
        assert 1 <= n <= 100000 and 0 <= k <= n


CHECKS["permutations-with-exactly-k-fixed-points"] = (b_fixed, lambda r: [(lambda n: [n, r.randint(0, n)])(r.randint(1, 7))][0], "exact")
VALIDATE["permutations-with-exactly-k-fixed-points"] = v_fixed


# ---------------------------------------------------------------- square-sum arrangements
add(
    id="count-square-sum-arrangements", title="Arrangements With Square Neighbour Sums", diff="Medium", topic=TOPIC,
    fn="countSquareArrangements", params=[("nums", "int[]")], ret="int", cmp="exact",
    desc='''<p>Count the <strong>distinct</strong> orderings of <code>nums</code> in which every two neighbouring numbers add up to a perfect square (0, 1, 4, 9, 16, ...). Two orderings are different if they differ at some position, so orderings that only swap equal values are counted once.</p><p>An array with a single number has no neighbours, so it has exactly one valid ordering.</p><pre>nums = [1,17,8]  ->  2    ([1,8,17] and [17,8,1])
nums = [2,2,2]   ->  1    (2 + 2 = 4)
nums = [1,2]     ->  0    (3 is not a square)</pre>''',
    constraints=["1 &le; nums.length &le; 12", "0 &le; nums[i] &le; 10<sup>9</sup>", "The answer is at most 12! = 479,001,600"],
    hints=["First work out, for every pair of values, whether their sum is a perfect square. Then the task is to count walks that use every element once.",
           "Build the ordering from the left. The next value must add up to a square with the previous one. To avoid counting equal orderings twice, choose <em>values</em> (with remaining multiplicities), not indices.",
           "Many partial orderings lead to the same situation: what matters is only the remaining multiset of values and the last value placed. Cache the count for that state."],
    editorial=["Count the multiplicity of each distinct value and precompute <code>ok[a][b]</code>: is <code>a + b</code> a perfect square (check with an integer square root). Then run a depth-first search where the state is (how many copies of each value remain, last value placed). From a state, try every distinct value that still has copies left and is compatible with the last value; the recursion ends with 1 when nothing is left.",
               "Choosing values instead of indices makes every distinct ordering appear exactly once, so no deduplication is needed afterwards. The plain search can still be exponential, but memoizing on (remaining counts, last value) bounds the number of states by (product of (c<sub>i</sub> + 1)) &middot; d, at most about 12 &middot; 2<sup>12</sup>, each with at most 12 transitions."],
    time="O(2<sup>n</sup> &middot; d<sup>2</sup>) worst case", space="O(2<sup>n</sup> &middot; d)",
    solution='''def countSquareArrangements(nums):
    from math import isqrt
    from functools import lru_cache
    vals = sorted(set(nums))
    d = len(vals)
    cnt = tuple(nums.count(v) for v in vals)
    ok = [[isqrt(vals[i] + vals[j]) ** 2 == vals[i] + vals[j] for j in range(d)] for i in range(d)]

    @lru_cache(maxsize=None)
    def go(counts, last, left):
        if left == 0:
            return 1
        total = 0
        for j in range(d):
            if counts[j] and (last < 0 or ok[last][j]):
                c = list(counts)
                c[j] -= 1
                total += go(tuple(c), j, left - 1)
        return total

    return go(cnt, -1, len(nums))
''',
    tests=[[[1]], [[0]], [[1, 2]], [[1, 17, 8]], [[2, 2, 2]], [[0, 0, 1]], [[1, 1, 3, 3, 4, 5, 11, 13, 14, 15, 21, 22]],
           [[2, 9, 7, 9, 2, 2, 7, 2, 2, 7, 7, 7]], [[8, 8, 1, 8, 3, 1, 1, 8, 1, 8, 8, 1]], [[0] * 12],
           [[399114178, 432402290, 115859935, 813875406, 510464178, 621859986, 802221183, 123280363, 196022554, 388891671, 285033935, 797660046]],
           [[1, 3, 6, 8, 10, 12, 13, 15, 17, 19, 22, 24]], [[6, 6, 43, 11, 53, 28, 39, 25, 11, 38, 10, 3]],
           [[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]]],
)


def b_squareq(nums):
    def sq(x):
        return int(round(x ** 0.5)) ** 2 == x
    if len(nums) <= 7:
        return sum(1 for p in set(_perms(nums)) if all(sq(p[i] + p[i + 1]) for i in range(len(p) - 1)))
    cnt = Counter(nums)

    def dfs(last, left):
        if left == 0:
            return 1
        t = 0
        for v in list(cnt):
            if cnt[v] and (last is None or sq(last + v)):
                cnt[v] -= 1
                t += dfs(v, left - 1)
                cnt[v] += 1
        return t

    return dfs(None, len(nums))


def g_squareq(r):
    n = r.randint(1, 7)
    if r.random() < 0.6:
        hi = r.choice([8, 12, 20])
        a = [r.randint(0, hi)]
        while len(a) < n:
            opts = [s * s - a[-1] for s in range(0, 10) if 0 <= s * s - a[-1] <= hi]
            if not opts:
                break
            a.append(r.choice(opts))
        r.shuffle(a)
        return [a]
    return [[r.randint(0, 20) for _ in range(n)]]


def v_squareq(tests):
    for t in tests:
        nums = t["args"][0]
        assert 1 <= len(nums) <= 12 and all(0 <= x <= 10 ** 9 for x in nums)
        assert 0 <= t["expected"] <= _fact(len(nums))


CHECKS["count-square-sum-arrangements"] = (b_squareq, g_squareq, "exact")
VALIDATE["count-square-sum-arrangements"] = v_squareq


# ---------------------------------------------------------------- precedence rules
_p = add(
    id="count-orderings-with-precedence-rules", title="Count Orderings With Precedence Rules", diff="Medium", topic=TOPIC,
    fn="countOrderings", params=[("n", "int"), ("rules", "int[][]")], ret="int", cmp="exact",
    desc='''<p>There are <code>n</code> tasks numbered <code>0..n-1</code> and each must be done exactly once, one after another. Every rule <code>[a, b]</code> in <code>rules</code> says that task <code>a</code> must be done somewhere <strong>before</strong> task <code>b</code>.</p><p>Count the orders of all <code>n</code> tasks that obey every rule, modulo <code>1,000,000,007</code>. Rules may repeat and may contradict each other (then the answer is 0).</p><pre>n = 3, rules = [[0,1]]          ->  3
n = 3, rules = [[0,1],[1,2]]    ->  1
n = 3, rules = [[0,1],[1,0]]    ->  0
n = 4, rules = [[0,2],[1,2]]    ->  8</pre>''',
    constraints=["1 &le; n &le; 14", "0 &le; rules.length &le; 60", "rules[i] = [a, b] with 0 &le; a, b &lt; n and a != b"],
    hints=["Trying all n! orders is too slow for n = 14 (about 87 billion). Notice that two partial orders that finished the <em>same set</em> of tasks have the same future.",
           "State = the set of tasks already done, stored as a bitmask. A task may be done next only if all tasks that must come before it are in the set.",
           "Let <code>pred[v]</code> be the bitmask of tasks that must precede v. Let <code>dp[mask]</code> be the number of valid orders of the tasks in mask. Then <code>dp[mask | 1&lt;&lt;v] += dp[mask]</code> whenever v is not in mask and <code>pred[v]</code> is a subset of mask."],
    editorial=["The number of ways to finish does not depend on the order in which the tasks of a prefix were done, only on which tasks they are. So count valid prefixes by their set. <code>dp[0] = 1</code>. For every mask with <code>dp[mask] &gt; 0</code> and every task v not in the mask, if <code>pred[v] &amp; mask == pred[v]</code> (all predecessors done), add <code>dp[mask]</code> to <code>dp[mask | (1 &lt;&lt; v)]</code>. The answer is <code>dp[(1 &lt;&lt; n) - 1]</code>.",
               "Contradictory rules (cycles) simply leave the full mask unreachable, giving 0. This counts the topological orderings of the rule graph. Time O(2<sup>n</sup> &middot; n), memory O(2<sup>n</sup>). Plain backtracking over orders works for n up to about 9 but is far too slow for 14."],
    time="O(2<sup>n</sup> &middot; n)", space="O(2<sup>n</sup>)",
    solution='''def countOrderings(n, rules):
    M = 1000000007
    pred = [0] * n
    for a, b in rules:
        pred[b] |= 1 << a
    dp = [0] * (1 << n)
    dp[0] = 1
    for mask in range(1 << n):
        w = dp[mask]
        if not w:
            continue
        for v in range(n):
            if not (mask >> v) & 1 and (pred[v] & mask) == pred[v]:
                nm = mask | (1 << v)
                dp[nm] = (dp[nm] + w) % M
    return dp[(1 << n) - 1]
''',
    tests=[[3, [[0, 1]]], [3, [[0, 1], [1, 2]]], [3, [[0, 1], [1, 0]]], [4, [[0, 2], [1, 2]]], [1, []], [3, []], [5, [[4, 0]]],
           [6, [[0, 1], [1, 2], [2, 3], [3, 4], [4, 5]]], [7, [[0, 1], [0, 1], [3, 2], [5, 6], [6, 5]]],
           [14, []], [14, [[0, 13], [13, 1], [5, 6], [2, 9], [9, 3], [4, 12], [12, 7]]],
           [14, [[i, 13] for i in range(13)]], [13, [[i, i + 2] for i in range(11)]]],
)
_r = rnd(4403)
_order = list(range(14)); _r.shuffle(_order)
_rules = []
for _ in range(25):
    _i, _j = sorted(_r.sample(range(14), 2))
    _rules.append([_order[_i], _order[_j]])
_p["tests"].append([14, _rules])
_order = list(range(12)); _r.shuffle(_order)
_rules = []
for _ in range(14):
    _i, _j = sorted(_r.sample(range(12), 2))
    _rules.append([_order[_i], _order[_j]])
_rules.append([_order[5], _order[2]])
_rules.append([_order[2], _order[5]])
_p["tests"].append([12, _rules])


def b_prec(n, rules):
    if n > 8:
        # peel tasks off the end: a task can be last if no rule forces another unfinished task after it
        succ = [0] * n
        for a, b in rules:
            succ[a] |= 1 << b
        memo = {0: 1}

        def f(mask):
            if mask not in memo:
                memo[mask] = sum(f(mask & ~(1 << v)) for v in range(n) if mask >> v & 1 and not succ[v] & mask)
            return memo[mask]

        return f((1 << n) - 1) % MOD
    c = 0
    for p in _perms(range(n)):
        pos = {v: i for i, v in enumerate(p)}
        if all(pos[a] < pos[b] for a, b in rules):
            c += 1
    return c % MOD


def g_prec(r):
    n = r.randint(1, 7)
    rules = []
    if n >= 2:
        for _ in range(r.randint(0, 6)):
            a, b = r.sample(range(n), 2)
            rules.append([a, b])
    return [n, rules]


def v_prec(tests):
    for t in tests:
        n, rules = t["args"]
        assert 1 <= n <= 14 and len(rules) <= 60
        assert all(len(x) == 2 and 0 <= x[0] < n and 0 <= x[1] < n and x[0] != x[1] for x in rules)


CHECKS["count-orderings-with-precedence-rules"] = (b_prec, g_prec, "exact")
VALIDATE["count-orderings-with-precedence-rules"] = v_prec


# ================================================================== HARD

# ---------------------------------------------------------------- k-th distinct permutation of a multiset
_p = add(
    id="kth-distinct-permutation-of-multiset", title="K-th Distinct Ordering With Repeats", diff="Hard", topic=TOPIC, tier="extra",
    fn="kthDistinctOrdering", params=[("nums", "int[]"), ("k", "int")], ret="int[]", cmp="exact",
    desc='''<p>The array <code>nums</code> may contain repeated values. List all <strong>distinct</strong> orderings of its elements (as sequences, each listed once) in increasing lexicographic order: compare the first elements, then the second elements, and so on. Return the <code>k</code>-th ordering of the list, counting from 1.</p><p>It is guaranteed that the list has at least <code>k</code> orderings. The list can be astronomically long, so do not generate it.</p><pre>nums = [1,1,2],   k = 2  ->  [1,2,1]    (list: 112, 121, 211)
nums = [1,2,1,2], k = 4  ->  [2,1,1,2]    (list: 1122, 1212, 1221, 2112, 2121, 2211)
nums = [5],       k = 1  ->  [5]</pre>''',
    constraints=["1 &le; nums.length &le; 40", "-1000 &le; nums[i] &le; 1000", "1 &le; k &le; 2<sup>31</sup> - 1, and k does not exceed the number of distinct orderings"],
    hints=["For a single slot, the orderings are grouped by their first value: all orderings starting with the smallest distinct value come first, then those starting with the next value, and so on.",
           "If you fix the first value v, how many distinct orderings of the rest exist? It is a multinomial coefficient: (remaining count)! divided by the product of the factorials of the remaining multiplicities.",
           "Walk through the distinct values in increasing order. If k is not larger than the group size, choose that value and go to the next slot. Otherwise subtract the group size from k and try the next value."],
    editorial=["Let <code>cnt[v]</code> be the number of unused copies of each value and <code>m</code> the number of unused elements. The number of distinct orderings of those elements is <code>m! / prod(cnt[v]!)</code>. At the current slot try the distinct values in increasing order: temporarily take one copy of v, and count the orderings of what is left, <code>w</code>. If <code>k &lt;= w</code> the answer begins with v: keep the choice and move on. Otherwise <code>k -= w</code> and put the copy back.",
               "This is the factorial number system of the plain k-th permutation problem, adapted to repeated values by using multinomial coefficients as block sizes. There are n slots, at most n distinct values each, and each count costs O(d) big-integer operations, so the time is O(n &middot; d<sup>2</sup>) operations on numbers of at most about 150 digits (n! for n = 40); fine in Python. In languages with 64-bit integers, cap each count at 2<sup>31</sup> to avoid overflow, which is safe because k never exceeds that."],
    time="O(n &middot; d<sup>2</sup>) big-integer operations", space="O(n)",
    solution='''def kthDistinctOrdering(nums, k):
    n = len(nums)
    fact = [1] * (n + 1)
    for i in range(1, n + 1):
        fact[i] = fact[i - 1] * i
    cnt = {}
    for x in nums:
        cnt[x] = cnt.get(x, 0) + 1
    vals = sorted(cnt)

    def ways(total):
        r = fact[total]
        for v in vals:
            r //= fact[cnt[v]]
        return r

    k -= 1
    res = []
    for pos in range(n):
        left = n - pos - 1
        for v in vals:
            if cnt[v] == 0:
                continue
            cnt[v] -= 1
            w = ways(left)
            if k < w:
                res.append(v)
                break
            k -= w
            cnt[v] += 1
    return res
''',
    tests=[[[1, 1, 2], 2], [[1, 2, 1, 2], 4], [[5], 1], [[1, 2, 3], 6], [[3, 3, 3], 1], [[2, 1, 2, 1], 6], [[0, -1, 0, -1, 0], 10],
           [[5, 4, 3, 2, 1], 120], [[7] * 10 + [8] * 3, 286], [[-1000, 1000, 0, 0, 1000, -1000, 5], 500]],
)
_r = rnd(4404)
_a = [1] * 10 + [2] * 10 + [3] * 10 + [4] * 10; _r.shuffle(_a)
_p["tests"].append([_a, 2147483647])
_a = [_r.randint(-5, 0) for _ in range(40)]
_p["tests"].append([_a, 1])
_p["tests"].append([_a, 987654321])
_a = _r.sample(range(-1000, 1001), 40)
_p["tests"].append([_a, 2147483647])
_a = [10] * 12 + [20] * 9 + [30] * 9; _r.shuffle(_a)
_p["tests"].append([_a, 1234567891])


def _multinomial(nums):
    r = _fact(len(nums))
    for c in Counter(nums).values():
        r //= _fact(c)
    return r


def b_kdist(nums, k):
    if len(nums) <= 8:
        return list(sorted(set(_perms(nums)))[k - 1])
    a = sorted(nums)
    for _ in range(k - 1):  # step with the textbook next-permutation
        i = len(a) - 2
        while a[i] >= a[i + 1]:
            i -= 1
        j = len(a) - 1
        while a[j] <= a[i]:
            j -= 1
        a[i], a[j] = a[j], a[i]
        a[i + 1:] = a[i + 1:][::-1]
    return a


def g_kdist(r):
    n = r.randint(1, 7)
    nums = [r.randint(-2, 2) for _ in range(n)]
    return [nums, r.randint(1, _multinomial(nums))]


def v_kdist(tests):
    for t in tests:
        nums, k = t["args"]
        assert 1 <= len(nums) <= 40 and all(-1000 <= x <= 1000 for x in nums)
        assert 1 <= k <= min(_multinomial(nums), INT_MAX)
        assert sorted(t["expected"]) == sorted(nums)


CHECKS["kth-distinct-permutation-of-multiset"] = (b_kdist, g_kdist, "exact")
VALIDATE["kth-distinct-permutation-of-multiset"] = v_kdist


# ---------------------------------------------------------------- no consecutive neighbours
add(
    id="count-orderings-without-consecutive-neighbours", title="Orderings Without Consecutive Neighbours", diff="Hard", topic=TOPIC, tier="extra",
    fn="countNoConsecutive", params=[("n", "int")], ret="int", cmp="exact",
    desc='''<p>Count the orderings <code>p</code> of the numbers <code>1..n</code> in which no two neighbouring entries are consecutive integers: <code>|p[i] - p[i+1]| != 1</code> for every index <code>i</code>.</p><p>Return the count modulo <code>1,000,000,007</code>.</p><pre>n = 4  ->  2     ([2,4,1,3] and [3,1,4,2])
n = 5  ->  14
n = 3  ->  0
n = 1  ->  1</pre>''',
    constraints=["1 &le; n &le; 800"],
    hints=["Brute force over all n! orderings only works for n up to about 10. Instead of forbidding bad neighbours, count the orderings in which chosen neighbour pairs <em>are</em> bad, and use inclusion-exclusion.",
           "Pick a set S of k of the n-1 value pairs (v, v+1) and force each of them to be adjacent. Chains of chosen pairs glue into blocks. A block of two or more values can appear ascending or descending, and the n - k blocks and loose values can be ordered in (n - k)! ways.",
           "If the k chosen pairs form m runs of consecutive pairs, the count for S is (n-k)! * 2^m. The number of ways to choose k pairs forming m runs is C(k-1, m-1) * C(n-k, m). Sum with alternating signs over k."],
    editorial=["Inclusion-exclusion on the n - 1 &ldquo;bad&rdquo; pairs {v, v+1}. For a set S of k pairs, the orderings in which every pair of S is adjacent are obtained by gluing: a maximal run of j chosen pairs ties j + 1 values into one block whose inner order is forced up to reversal (2 ways), so S yields (n - k)! &middot; 2<sup>m</sup> orderings where m is the number of runs and n - k is the number of resulting items.",
               "Choosing k of the n - 1 pairs so that they form exactly m runs: split k into m positive parts, C(k-1, m-1) ways, and place the m runs among the n - 1 - k unchosen pairs, C(n-k, m) ways. Therefore the answer is <code>n! + sum over k = 1..n-1 of (-1)^k (n-k)! sum over m of C(k-1, m-1) C(n-k, m) 2^m</code>, taken modulo p. With factorial tables and inverse factorials this is O(n<sup>2</sup>) (about n<sup>2</sup>/4 terms).",
               "The values 1, 0, 0, 2, 14, 90, 646, 5242 for n = 1..8 are a handy check (known as Hertzsprung's problem). A bitmask DP over (used set, last value) also works but only up to n of about 16."],
    time="O(n<sup>2</sup>)", space="O(n)",
    solution='''def countNoConsecutive(n):
    M = 1000000007
    fact = [1] * (n + 2)
    for i in range(1, n + 2):
        fact[i] = fact[i - 1] * i % M
    ifact = [pow(f, M - 2, M) for f in fact]
    pw = [1] * (n + 2)
    for i in range(1, n + 2):
        pw[i] = pw[i - 1] * 2 % M
    total = fact[n]
    for k in range(1, n):
        s = 0
        for m in range(1, min(k, n - k) + 1):
            s += ifact[m - 1] * ifact[k - m] % M * ifact[m] % M * ifact[n - k - m] % M * pw[m]
        s %= M
        s = s * fact[k - 1] % M * fact[n - k] % M * fact[n - k] % M
        total += -s if k & 1 else s
    return total % M
''',
    tests=[[1], [2], [3], [4], [5], [6], [7], [8], [10], [14], [50], [200], [799], [800]],
)


def b_nocons(n):
    if n <= 8:
        return sum(1 for p in _perms(range(n)) if all(abs(p[i] - p[i + 1]) != 1 for i in range(n - 1))) % MOD
    a = [1, 1, 0, 0, 2]  # known linear recurrence of Hertzsprung's problem
    for m in range(5, n + 1):
        a.append((m + 1) * a[m - 1] - (m - 2) * a[m - 2] - (m - 5) * a[m - 3] + (m - 3) * a[m - 4])
    return a[n] % MOD


def v_nocons(tests):
    for t in tests:
        assert 1 <= t["args"][0] <= 800


CHECKS["count-orderings-without-consecutive-neighbours"] = (b_nocons, lambda r: [r.randint(1, 8)], "exact")
VALIDATE["count-orderings-without-consecutive-neighbours"] = v_nocons


# ---------------------------------------------------------------- bounded displacement
add(
    id="count-orderings-with-bounded-displacement", title="Orderings With Bounded Displacement", diff="Hard", topic=TOPIC, tier="extra",
    fn="countBoundedShift", params=[("n", "int"), ("d", "int")], ret="int", cmp="exact",
    desc='''<p>Count the orderings <code>p</code> of the numbers <code>1..n</code> in which every number is at most <code>d</code> places away from its own position: <code>|p[i] - (i + 1)| &le; d</code> for every index <code>i</code> (0-indexed).</p><p>Return the count modulo <code>1,000,000,007</code>.</p><pre>n = 3, d = 1  ->  3    ([1,2,3], [2,1,3], [1,3,2])
n = 4, d = 1  ->  5
n = 3, d = 2  ->  6    (every ordering qualifies)</pre>''',
    constraints=["1 &le; n &le; 500", "1 &le; d &le; 4"],
    hints=["For d = 1 the allowed orderings only swap neighbouring pairs. Count them for small n by hand and look at the pattern, then think about how to generalise to d up to 4.",
           "Fill the positions from left to right. Position i can only take values from i - d to i + d, a window of 2d + 1 values. Which values of that window are already taken is all that matters for the future.",
           "Keep a bitmask of the 2d + 1 values of the window (used or not) as the state. When the window slides forward, the value that falls out on the left must already be used, otherwise it can never be placed."],
    editorial=["Process the positions 1..n in order. At position i the number placed must lie in the window [i - d, i + d] (clipped to 1..n). Remember which numbers of the window are already placed with a bitmask of 2d + 1 bits; bit j stands for the value i - d + j. Values below 1 are marked as used from the start, values above n are never chosen.",
               "Transition: choose a free bit j (value within 1..n), set it, then slide to the next position. Sliding drops bit 0 (value i - d): it must be set, because later positions are more than d away from it, so an unused value there would stay unplaced forever. Shift the mask right by one. After n positions every value is placed exactly once (n distinct values, n positions), so the answer is the sum of all remaining states.",
               "There are at most 2<sup>2d+1</sup> states per position and 2d + 1 transitions each, so the time is O(n &middot; 2<sup>2d+1</sup> &middot; d). Using a dictionary keeps only the reachable states, which is far fewer than 2<sup>2d+1</sup>."],
    time="O(n &middot; d &middot; 2<sup>2d+1</sup>)", space="O(2<sup>2d+1</sup>)",
    solution='''def countBoundedShift(n, d):
    M = 1000000007
    W = 2 * d + 1
    init = 0
    for j in range(W):
        if 1 - d + j <= 0:
            init |= 1 << j
    dp = {init: 1}
    for i in range(1, n + 1):
        nd = {}
        for mask, w in dp.items():
            for j in range(W):
                if (mask >> j) & 1:
                    continue
                if i - d + j > n:
                    break
                nm = mask | (1 << j)
                if not nm & 1:
                    continue
                nm >>= 1
                nd[nm] = (nd.get(nm, 0) + w) % M
        dp = nd
    return sum(dp.values()) % M
''',
    tests=[[1, 1], [2, 1], [3, 1], [3, 2], [4, 1], [4, 2], [5, 3], [7, 2], [8, 4], [10, 3], [60, 1], [300, 2], [500, 4], [500, 3], [500, 1], [499, 4]],
)


def b_bounded(n, d):
    if n <= 8:
        return sum(1 for p in _perms(range(n)) if all(abs(p[i] - i) <= d for i in range(n))) % MOD
    layer = {frozenset(): 1}  # state: values already placed that are still >= i - d
    for i in range(1, n + 1):
        nxt = {}
        for used, w in layer.items():
            for v in range(max(1, i - d), min(n, i + d) + 1):
                if v in used:
                    continue
                nu = used | {v}
                if i - d >= 1 and (i - d) not in nu:
                    continue
                key = frozenset(x for x in nu if x > i - d)
                nxt[key] = (nxt.get(key, 0) + w) % MOD
        layer = nxt
    return sum(layer.values()) % MOD


def v_bounded(tests):
    for t in tests:
        n, d = t["args"]
        assert 1 <= n <= 500 and 1 <= d <= 4


CHECKS["count-orderings-with-bounded-displacement"] = (b_bounded, lambda r: [r.randint(1, 8), r.randint(1, 4)], "exact")
VALIDATE["count-orderings-with-bounded-displacement"] = v_bounded
