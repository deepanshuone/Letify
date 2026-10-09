"""Problems: backtracking (second batch). See data/lib.py for the registry."""
import re
from itertools import product as _product, permutations as _perms, combinations as _combs
from math import factorial as _fact

from lib import add, rnd, CHECKS, VALIDATE, gen_arr  # noqa: F401

TOPIC = "Backtracking"


# ================================================================== EASY

# ---------------------------------------------------------------- binary watch times
add(
    id="binary-watch-times", title="Binary Watch Times", diff="Easy", topic=TOPIC,
    fn="binaryWatchTimes", params=[("turnedOn", "int")], ret="int[]", cmp="flat",
    desc="<p>A binary watch shows the hour with 4 LEDs worth 8, 4, 2 and 1, and the minute with 6 LEDs worth 32, 16, 8, 4, 2 and 1. The lit LEDs of a group add up to the number it displays.</p><p>Exactly <code>turnedOn</code> of the 10 LEDs are lit. Return every time the watch could be showing. A valid hour is <code>0..11</code> and a valid minute is <code>0..59</code>.</p><p>Encode each time as the number of minutes since midnight, <code>hour * 60 + minute</code>. The times may be returned in any order, and each time must appear once.</p>",
    constraints=["0 &le; turnedOn &le; 10", "Hours go from 0 to 11 and minutes from 0 to 59 (a lit pattern that shows 12 or more hours, or 60 or more minutes, is not a time)"],
    hints=["There are only 10 LEDs, so you can afford to look at every way of lighting exactly <code>turnedOn</code> of them.",
           "Choose LEDs one at a time in increasing order of position, so that each set is built exactly once. Track the hour value and the minute value as you go.",
           "LEDs 0..3 add <code>1 &lt;&lt; led</code> to the hour, LEDs 4..9 add <code>1 &lt;&lt; (led - 4)</code> to the minute. Both values only grow as you add LEDs, so stop a branch the moment the hour exceeds 11 or the minute exceeds 59."],
    editorial=["Treat the 10 LEDs as items and pick exactly <code>turnedOn</code> of them. Recurse with the index of the next LED allowed, the number of LEDs still to light, and the running hour and minute. Each choice adds a power of two to the hour or to the minute. Because adding more LEDs can never lower either value, a branch whose hour is already above 11 or whose minute is above 59 can be cut immediately. When no LEDs remain to light, record <code>hour * 60 + minute</code>.",
               "A tiny alternative is to loop over all 12 * 60 times and keep the ones whose two bit counts add up to <code>turnedOn</code>. Both are fast here; the backtracking version is the one that generalises to larger watches."],
    time="O(C(10, k))", space="O(k) recursion",
    solution='''def binaryWatchTimes(turnedOn):
    res = []

    def go(start, left, hours, minutes):
        if hours > 11 or minutes > 59:
            return
        if left == 0:
            res.append(hours * 60 + minutes)
            return
        for led in range(start, 10):
            if led < 4:
                go(led + 1, left - 1, hours | (1 << led), minutes)
            else:
                go(led + 1, left - 1, hours, minutes | (1 << (led - 4)))

    go(0, turnedOn, 0, 0)
    return res
''',
    tests=[[0], [1], [2], [3], [4], [5], [6], [7], [8], [9], [10]],
)


def b_watch(k):
    return [h * 60 + m for h in range(12) for m in range(60) if bin(h).count("1") + bin(m).count("1") == k]


def v_watch(tests):
    for t in tests:
        assert 0 <= t["args"][0] <= 10
        e = t["expected"]
        assert len(set(e)) == len(e) and all(0 <= x < 720 for x in e) and all(x % 60 < 60 for x in e)


CHECKS["binary-watch-times"] = (b_watch, lambda r: [r.randint(0, 10)], "flat")
VALIDATE["binary-watch-times"] = v_watch


# ---------------------------------------------------------------- subset xor total
add(
    id="subset-xor-total-sum", title="Subset XOR Total", diff="Easy", topic=TOPIC,
    fn="subsetXorSum", params=[("nums", "int[]")], ret="int", cmp="exact",
    desc="<p>The <em>XOR value</em> of a subset is the bitwise XOR of all its elements; the empty subset has XOR value <code>0</code>.</p><p>Given the integer array <code>nums</code>, consider every subset formed by choosing any elements by position (equal values at different positions count as different choices, so there are exactly <code>2<sup>n</sup></code> subsets). Return the sum of the XOR values of all of them.</p>",
    constraints=["1 &le; nums.length &le; 16", "0 &le; nums[i] &le; 10,000"],
    hints=["With at most 16 elements there are at most 65,536 subsets, so trying each one is affordable. Write that version first.",
           "Recurse over the index with two choices per element, include it (XOR it into the running value) or skip it, and add the running value at the end of each path.",
           "For the closed form, look at one bit position at a time. If no element has that bit, no subset has it. If at least one element does, exactly half of all subsets have it set in their XOR."],
    editorial=["The direct backtracking solution walks the include/skip tree: at index <code>i</code> carry the XOR of the chosen elements so far, and at <code>i == n</code> add that XOR to the answer. That visits all 2<sup>n</sup> leaves.",
               "To get a linear solution, handle each bit independently. Suppose some element has bit <code>b</code> set. Pair every subset with the subset that differs only by toggling that element: exactly one of the two has bit <code>b</code> set in its XOR, so half of the 2<sup>n</sup> subsets, i.e. 2<sup>n-1</sup>, contribute <code>2<sup>b</sup></code>. If no element has the bit, no subset does. Summing over bits gives <code>(OR of all elements) * 2<sup>n-1</sup></code>. For the stated limits the result stays well below 2<sup>31</sup>."],
    time="O(n)", space="O(1)",
    solution='''def subsetXorSum(nums):
    acc = 0
    for x in nums:
        acc |= x
    return acc << (len(nums) - 1)
''',
    tests=[[[1, 3]], [[5, 1, 6]], [[3, 4, 5, 6, 7, 8]], [[0]], [[7]], [[0, 0, 0]], [[2, 2]], [[1, 2, 4, 8]],
           [[10000, 10000, 10000, 10000]], [[9999, 1, 5000]], [[1] * 16], [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 6]]],
)
_r = rnd(7101)
for _p in __import__("lib").P:
    if _p["id"] == "subset-xor-total-sum":
        _p["tests"].extend([[[_r.randint(0, 10000) for _ in range(16)]], [[_r.randint(0, 3) for _ in range(16)]],
                            [[1 << i for i in range(14)] + [10000, 10000]]])


def b_xor(nums):
    n, tot = len(nums), 0
    for mask in range(1 << n):
        x = 0
        for i in range(n):
            if mask >> i & 1:
                x ^= nums[i]
        tot += x
    return tot


def v_xor(tests):
    for t in tests:
        nums = t["args"][0]
        assert 1 <= len(nums) <= 16 and all(0 <= x <= 10000 for x in nums)


CHECKS["subset-xor-total-sum"] = (b_xor, lambda r: [gen_arr(r, 0, r.choice([3, 20, 10000]), 1, 9)], "exact")
VALIDATE["subset-xor-total-sum"] = v_xor


# ================================================================== MEDIUM

# ---------------------------------------------------------------- subsets with duplicates
add(
    id="subsets-with-duplicates", title="Subsets With Duplicates", diff="Medium", topic=TOPIC,
    fn="subsetsWithDup", params=[("nums", "int[]")], ret="int[][]", cmp="rowset",
    desc="<p>Given an integer array <code>nums</code> that may contain repeated values, return every <em>distinct</em> subset of its elements. Two subsets are the same when they hold the same values with the same multiplicities, regardless of which positions the values came from.</p><p>Write the values inside every subset in non-decreasing order. The subsets may be returned in any order. Include the empty subset.</p>",
    constraints=["1 &le; nums.length &le; 10", "-10 &le; nums[i] &le; 10"],
    hints=["If all elements were unique this would be the plain power set. What goes wrong when values repeat?",
           "Sort the array first so that equal values sit next to each other. Then two subsets are the same exactly when they take the same number of copies of every value.",
           "Build subsets by picking elements in increasing index order. At one recursion level, never pick <code>nums[i]</code> if <code>i</code> is past the first candidate of this level and <code>nums[i] == nums[i - 1]</code>."],
    editorial=["Sort the array. Recurse with a <code>start</code> index and a current subset. On entry, record a copy of the current subset (every node of the recursion tree is a distinct subset). Then loop <code>i</code> from <code>start</code>: skip <code>i</code> when <code>i &gt; start</code> and <code>nums[i] == nums[i-1]</code>, otherwise append <code>nums[i]</code>, recurse with <code>i + 1</code> and pop.",
               "The skip rule says: at a given depth, a value may be used as the next element at most once, because choosing the second copy at the same depth would only repeat a subset already generated through the first copy. Using a later copy deeper in the recursion is still allowed, which is how a subset with two equal values is produced. The output size is at most 2<sup>n</sup> subsets, which bounds the work."],
    time="O(n &middot; 2<sup>n</sup>)", space="O(n) extra",
    solution='''def subsetsWithDup(nums):
    nums = sorted(nums)
    n = len(nums)
    res = []
    cur = []

    def go(start):
        res.append(cur[:])
        for i in range(start, n):
            if i > start and nums[i] == nums[i - 1]:
                continue
            cur.append(nums[i])
            go(i + 1)
            cur.pop()

    go(0)
    return res
''',
    tests=[[[1, 2, 2]], [[0]], [[4, 4, 4, 1, 4]], [[-1, -1, -1]], [[1, 2, 3]], [[5, 6, 5, 6]], [[3, 3, 1, 1, 2, 2]],
           [[10, -10, 0, 3, 3, -10]], [[2] * 10], [[1, 1, 1, 2, 2, 3, 4, 4, 5, 5]], [[-10, 10, 0, 7, 7, 7, -10, 10, 1, 1]],
           [[-4, 9, 2, 0, -7, 5, 3, 10, -10, 6]]],
)


def b_subdup(nums):
    seen = set()
    n = len(nums)
    for mask in range(1 << n):
        seen.add(tuple(sorted(nums[i] for i in range(n) if mask >> i & 1)))
    return [list(t) for t in seen]


def v_subdup(tests):
    for t in tests:
        nums, res = t["args"][0], t["expected"]
        assert 1 <= len(nums) <= 10 and all(-10 <= x <= 10 for x in nums)
        assert len({tuple(r) for r in res}) == len(res)
        assert all(r == sorted(r) for r in res) and [] in res


CHECKS["subsets-with-duplicates"] = (b_subdup, lambda r: [gen_arr(r, -3, 3, 1, 8)], "rowset")
VALIDATE["subsets-with-duplicates"] = v_subdup


# ---------------------------------------------------------------- permutations with duplicates
add(
    id="permutations-with-duplicates", title="Distinct Orderings", diff="Medium", topic=TOPIC,
    fn="permuteUnique", params=[("nums", "int[]")], ret="int[][]", cmp="rowset",
    desc="<p>The integer array <code>nums</code> may contain repeated values. Return all <em>distinct</em> orderings of its elements: every row uses all of the numbers, and no two rows are equal as sequences.</p><p>Rows may be returned in any order.</p>",
    constraints=["1 &le; nums.length &le; 7", "-10 &le; nums[i] &le; 10"],
    hints=["If you reuse the technique for distinct values, equal numbers produce the same row several times. Count how many copies of each row you would get.",
           "Sort <code>nums</code> so that equal values are neighbours, and keep a <code>used</code> flag per position.",
           "When choosing a value for the current slot, skip <code>nums[i]</code> if it equals <code>nums[i-1]</code> and <code>nums[i-1]</code> is not currently used: that copy would be tried in the same slot already."],
    editorial=["Sort the array, then fill the slots from left to right as in the usual permutation search, trying each unused index. To avoid repeated rows enforce an order among equal values: a copy of a value may be placed only if the previous copy (the neighbour to its left in sorted order) is already in use. Equivalent view: at any single slot each distinct value is tried only once.",
               "With the rule in place every row is generated exactly once, so the number of rows is <code>n! / (c<sub>1</sub>! c<sub>2</sub>! ...)</code> where the <code>c</code>'s are the multiplicities. The running time is dominated by writing out the rows."],
    time="O(n &middot; n!)", space="O(n) extra",
    solution='''def permuteUnique(nums):
    nums = sorted(nums)
    n = len(nums)
    used = [False] * n
    cur = []
    res = []

    def go():
        if len(cur) == n:
            res.append(cur[:])
            return
        for i in range(n):
            if used[i]:
                continue
            if i > 0 and nums[i] == nums[i - 1] and not used[i - 1]:
                continue
            used[i] = True
            cur.append(nums[i])
            go()
            cur.pop()
            used[i] = False

    go()
    return res
''',
    tests=[[[1, 1, 2]], [[1, 2, 3]], [[2, 2, 2]], [[5]], [[0, 1, 0]], [[-1, -1, 3, 3]], [[1, 1, 2, 2, 3]], [[1, 2, 2, 3, 3, 3]],
           [[3, 3, 3, 3, 3, 3, 3]], [[4, -4, 4, -4, 0, 0, 9]], [[1, 2, 3, 4, 5, 6]], [[1, 1, 2, 3, 4, 5, 6]]],
)


def b_permdup(nums):
    return [list(t) for t in set(_perms(nums))]


def v_permdup(tests):
    from collections import Counter
    for t in tests:
        nums, res = t["args"][0], t["expected"]
        assert 1 <= len(nums) <= 7 and all(-10 <= x <= 10 for x in nums)
        cnt = _fact(len(nums))
        for c in Counter(nums).values():
            cnt //= _fact(c)
        assert len(res) == cnt and len({tuple(r) for r in res}) == len(res)
        assert all(sorted(r) == sorted(nums) for r in res)


CHECKS["permutations-with-duplicates"] = (b_permdup, lambda r: [gen_arr(r, -2, 2, 1, 6)], "rowset")
VALIDATE["permutations-with-duplicates"] = v_permdup


# ---------------------------------------------------------------- combinations n choose k
add(
    id="combinations-n-choose-k", title="Choose K Numbers", diff="Medium", topic=TOPIC,
    fn="combine", params=[("n", "int"), ("k", "int")], ret="int[][]", cmp="rowset",
    desc="<p>Given two integers <code>n</code> and <code>k</code>, return every way to choose <code>k</code> different numbers from <code>1..n</code>.</p><p>Write each selection as a row in increasing order (so <code>[1,3]</code> is used and <code>[3,1]</code> is not). Rows may be returned in any order.</p>",
    constraints=["1 &le; k &le; n &le; 20", "The number of selections C(n, k) is at most 5,000"],
    hints=["The order inside a selection does not matter, so force an order: write the numbers of a row in increasing order.",
           "Recurse with the smallest number you are still allowed to take. After taking <code>v</code>, the next number must be at least <code>v + 1</code>.",
           "Prune: if the numbers left in <code>start..n</code> cannot fill the remaining slots, there is no point in trying that start value. The loop for the next number can stop at <code>n - (slots still needed) + 1</code>."],
    editorial=["Keep a current row and the next allowed number <code>start</code>. When the row has <code>k</code> numbers, store a copy. Otherwise, for each <code>v</code> from <code>start</code> up to the last value that still leaves enough numbers above it to complete the row, append <code>v</code>, recurse on <code>v + 1</code>, and pop.",
               "The upper bound on <code>v</code> is the pruning that matters: without it the search wastes time on prefixes that can never reach length <code>k</code>. With it every recursive call leads to at least one answer, so the total work is proportional to the output size, <code>C(n, k) &middot; k</code>."],
    time="O(k &middot; C(n, k))", space="O(k) extra",
    solution='''def combine(n, k):
    res = []
    cur = []

    def go(start):
        if len(cur) == k:
            res.append(cur[:])
            return
        for v in range(start, n - (k - len(cur)) + 2):
            cur.append(v)
            go(v + 1)
            cur.pop()

    go(1)
    return res
''',
    tests=[[4, 2], [1, 1], [5, 5], [5, 1], [6, 3], [10, 3], [20, 20], [20, 1], [20, 19], [12, 6], [20, 3], [20, 4], [20, 17], [13, 6]],
)


def b_comb(n, k):
    out = []
    for mask in range(1 << n):
        if bin(mask).count("1") == k:
            out.append([i + 1 for i in range(n) if mask >> i & 1])
    return out


def g_comb(r):
    n = r.randint(1, 10)
    return [n, r.randint(1, n)]


def v_comb(tests):
    for t in tests:
        n, k = t["args"]
        res = t["expected"]
        assert 1 <= k <= n <= 20
        assert len(res) == _fact(n) // (_fact(k) * _fact(n - k)) <= 5000
        assert all(r == sorted(set(r)) and len(r) == k and 1 <= r[0] and r[-1] <= n for r in res)


CHECKS["combinations-n-choose-k"] = (b_comb, g_comb, "rowset")
VALIDATE["combinations-n-choose-k"] = v_comb


# ---------------------------------------------------------------- word path in grid
def _word_tests():
    r = rnd(7301)
    out = []
    # 6x6 mostly-equal letters, word follows an actual snake path
    snake = [[1] * 6 for _ in range(6)]
    snake[5][5] = 2
    out.append([snake, "aaaaaaaaaaaaaaab"])
    # same grid but one more 'a' than exists -> impossible by count
    out.append([snake, "a" * 36])
    # random 6x6 over {a,b,c}
    for w in ("abcabcabc", "cccbbbaaaccc", "abababababababab", "bcbcbcbcb"):
        g = [[r.randint(1, 3) for _ in range(6)] for _ in range(6)]
        out.append([g, w])
    # a word taken from a real self avoiding walk of a random grid
    g = [[r.randint(1, 4) for _ in range(6)] for _ in range(6)]
    seen = {(0, 0)}
    path = [(0, 0)]
    while len(path) < 14:
        x, y = path[-1]
        nb = [(x + dx, y + dy) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))
              if 0 <= x + dx < 6 and 0 <= y + dy < 6 and (x + dx, y + dy) not in seen]
        if not nb:
            break
        c = r.choice(nb)
        seen.add(c)
        path.append(c)
    out.append([g, "".join(chr(96 + g[x][y]) for x, y in path)])
    return out


add(
    id="word-path-in-grid", title="Word Path in Grid", diff="Medium", topic=TOPIC,
    fn="wordPathExists", params=[("board", "int[][]"), ("word", "string")], ret="bool", cmp="exact",
    desc="<p>A letter grid is given as an integer matrix <code>board</code>, where <code>1</code> stands for <code>a</code>, <code>2</code> for <code>b</code>, and so on up to <code>26</code> for <code>z</code>.</p><p>Decide whether the lowercase string <code>word</code> can be spelled by a path through the grid. A path starts at any cell and moves one step at a time to a cell directly above, below, left or right of the current one. A cell may be used at most once within one path.</p>",
    constraints=["1 &le; board.length, board[i].length &le; 6", "1 &le; board[i][j] &le; 26", "1 &le; word.length &le; 36", "word contains only lowercase letters"],
    hints=["Try every cell as the starting point for the first letter of the word.",
           "From a cell that matches the current letter, explore the four neighbours for the next letter, and mark the cell as used while you are exploring from it. Remember to unmark it when that attempt fails.",
           "Cheap prunings: fail at once if the word needs more copies of some letter than the grid holds, and search from whichever end of the word has the rarer letter in the grid (spell the word backwards if the other end is rarer)."],
    editorial=["Depth-first search from each cell. A call <code>go(r, c, k)</code> succeeds when <code>board[r][c]</code> equals the k-th letter and either that was the last letter or one of the four neighbours that is still free succeeds with letter <code>k + 1</code>. Mark the cell used before looking at the neighbours and release it afterwards, so other paths can reuse it later (this release step is the backtracking).",
               "The worst case is exponential in the word length because the number of self-avoiding walks grows quickly, but the grid has at most 36 cells. The letter-count check kills impossible words instantly, and starting from the end of the word whose letter is rarer in the grid greatly reduces the number of starting cells that must be explored."],
    time="O(m &middot; n &middot; 3<sup>L</sup>)", space="O(L) recursion",
    solution='''def wordPathExists(board, word):
    m, n = len(board), len(board[0])
    codes = [ord(ch) - 96 for ch in word]
    L = len(codes)
    have = {}
    for row in board:
        for x in row:
            have[x] = have.get(x, 0) + 1
    need = {}
    for x in codes:
        need[x] = need.get(x, 0) + 1
    for x, v in need.items():
        if have.get(x, 0) < v:
            return False
    if have.get(codes[0], 0) > have.get(codes[-1], 0):
        codes.reverse()
    seen = [[False] * n for _ in range(m)]

    def go(r, c, k):
        if board[r][c] != codes[k]:
            return False
        if k == L - 1:
            return True
        seen[r][c] = True
        found = False
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nr, nc = r + dr, c + dc
            if 0 <= nr < m and 0 <= nc < n and not seen[nr][nc] and go(nr, nc, k + 1):
                found = True
                break
        seen[r][c] = False
        return found

    for r in range(m):
        for c in range(n):
            if go(r, c, 0):
                return True
    return False
''',
    tests=[[[[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12]], "bgk"],
           [[[1, 2, 1], [2, 1, 2], [1, 2, 1]], "ababa"],
           [[[1, 2, 1], [2, 1, 2], [1, 2, 1]], "bbbb"],
           [[[1]], "a"], [[[1]], "b"], [[[1]], "aa"],
           [[[1, 1]], "aaa"], [[[3, 1, 20]], "cat"], [[[3, 1, 20]], "tac"], [[[3, 1], [20, 1]], "caa"],
           [[[1, 2], [4, 3]], "abcd"], [[[1, 2], [4, 3]], "acdb"]],
)
for _p in __import__("lib").P:
    if _p["id"] == "word-path-in-grid":
        _p["tests"].extend(_word_tests())


def b_wpath(board, word):
    m, n = len(board), len(board[0])
    codes = [ord(c) - 96 for c in word]
    # breadth-first over (cell, set of cells used so far) states, one word letter at a time
    frontier = {(r * n + c, 1 << (r * n + c)) for r in range(m) for c in range(n) if board[r][c] == codes[0]}
    for ch in codes[1:]:
        nxt = set()
        for cell, mask in frontier:
            r, c = divmod(cell, n)
            for rr, cc in ((r - 1, c), (r + 1, c), (r, c - 1), (r, c + 1)):
                if 0 <= rr < m and 0 <= cc < n and board[rr][cc] == ch and not mask >> (rr * n + cc) & 1:
                    nxt.add((rr * n + cc, mask | 1 << (rr * n + cc)))
        frontier = nxt
        if not frontier:
            return False
    return bool(frontier)


def g_wpath(r):
    m, n = r.randint(1, 4), r.randint(1, 4)
    alpha = r.randint(1, 3)
    board = [[r.randint(1, alpha) for _ in range(n)] for _ in range(m)]
    if r.random() < 0.6:
        x, y = r.randrange(m), r.randrange(n)
        w = [board[x][y]]
        for _ in range(r.randint(0, 8)):
            dx, dy = r.choice(((1, 0), (-1, 0), (0, 1), (0, -1)))
            if 0 <= x + dx < m and 0 <= y + dy < n:
                x, y = x + dx, y + dy
                w.append(board[x][y])
    else:
        w = [r.randint(1, alpha + 1) for _ in range(r.randint(1, 8))]
    return [board, "".join(chr(96 + c) for c in w)]


def v_wpath(tests):
    for t in tests:
        board, word = t["args"]
        assert 1 <= len(board) <= 6 and all(len(row) == len(board[0]) for row in board) and 1 <= len(board[0]) <= 6
        assert all(1 <= x <= 26 for row in board for x in row)
        assert 1 <= len(word) <= 36 and all("a" <= c <= "z" for c in word)
    res = [t["expected"] for t in tests]
    assert True in res and False in res


CHECKS["word-path-in-grid"] = (b_wpath, g_wpath, "exact")
VALIDATE["word-path-in-grid"] = v_wpath


# ---------------------------------------------------------------- balanced bracket sequences
add(
    id="balanced-bracket-sequences", title="Balanced Bracket Sequences", diff="Medium", topic=TOPIC,
    fn="bracketSequences", params=[("n", "int")], ret="int[][]", cmp="rowset",
    desc="<p>Return every well-formed arrangement of <code>n</code> pairs of brackets. To keep the answer numeric, an opening bracket is written as <code>1</code> and a closing bracket as <code>-1</code>, so each arrangement is a row of exactly <code>2n</code> values.</p><p>A row is well-formed when every closing bracket matches an earlier opening one: no prefix of the row has a negative sum, and the whole row sums to <code>0</code>. Rows may be returned in any order.</p>",
    constraints=["1 &le; n &le; 8"],
    hints=["Every row has exactly n ones and n minus-ones. Think about when it is legal to append a <code>1</code> and when a <code>-1</code>.",
           "You may add an opening bracket while fewer than n have been used. You may add a closing bracket only while there are more opening brackets than closing ones so far.",
           "Recurse with counters <code>opened</code> and <code>closed</code>. Every prefix you build is already valid, so nothing needs to be filtered at the end."],
    editorial=["Build the row left to right, tracking how many opening and closing brackets have been placed. Appending an opening bracket is allowed while <code>opened &lt; n</code>; appending a closing bracket is allowed while <code>closed &lt; opened</code>. A row of length <code>2n</code> built under these rules is always balanced, and every balanced row is built exactly once.",
               "Trying all 2<sup>2n</sup> sign patterns and filtering is also correct but wastes almost all of its work. The pruned search only ever extends valid prefixes. The number of results is the n-th Catalan number (1, 2, 5, 14, 42, 132, 429, 1430 for n = 1..8)."],
    time="O(n &middot; Catalan(n))", space="O(n) extra",
    solution='''def bracketSequences(n):
    res = []
    cur = []

    def go(opened, closed):
        if len(cur) == 2 * n:
            res.append(cur[:])
            return
        if opened < n:
            cur.append(1)
            go(opened + 1, closed)
            cur.pop()
        if closed < opened:
            cur.append(-1)
            go(opened, closed + 1)
            cur.pop()

    go(0, 0)
    return res
''',
    tests=[[1], [2], [3], [4], [5], [6], [7], [8]],
)


def b_brackets(n):
    out = []
    for signs in _product((1, -1), repeat=2 * n):
        bal, ok = 0, True
        for s in signs:
            bal += s
            if bal < 0:
                ok = False
                break
        if ok and bal == 0:
            out.append(list(signs))
    return out


def v_brackets(tests):
    cat = {1: 1, 2: 2, 3: 5, 4: 14, 5: 42, 6: 132, 7: 429, 8: 1430}
    for t in tests:
        n = t["args"][0]
        assert 1 <= n <= 8 and len(t["expected"]) == cat[n]
        assert len({tuple(r) for r in t["expected"]}) == cat[n]


CHECKS["balanced-bracket-sequences"] = (b_brackets, lambda r: [r.randint(1, 6)], "rowset")
VALIDATE["balanced-bracket-sequences"] = v_brackets


# ---------------------------------------------------------------- divisible arrangements
add(
    id="divisible-arrangements-count", title="Divisible Arrangements", diff="Medium", topic=TOPIC,
    fn="countArrangements", params=[("n", "int")], ret="int", cmp="exact",
    desc="<p>Consider orderings of the numbers <code>1..n</code>, each used once. Number the positions <code>1..n</code> from the left. An ordering is <em>divisible</em> if, at every position <code>i</code>, the value <code>v</code> placed there satisfies at least one of: <code>v</code> is a multiple of <code>i</code>, or <code>i</code> is a multiple of <code>v</code>.</p><p>Return how many divisible orderings exist.</p>",
    constraints=["1 &le; n &le; 14"],
    hints=["There are n! orderings in total, far too many to test one by one for n = 14. Decide a position's value early so bad prefixes die quickly.",
           "Fill positions one at a time and try only the unused values that are compatible with that position. Which positions have the fewest compatible values?",
           "Fill from position n down to 1 (large positions have few candidates), and remember results by the set of values already used: the position being filled is determined by how many values are used, so a bitmask is a complete state."],
    editorial=["Backtracking fills positions in some order, at each step trying every unused value <code>v</code> with <code>v % i == 0</code> or <code>i % v == 0</code>. Position 1 accepts anything, while position 14 accepts only 1, 2, 7 and 14, so filling positions from the back prunes much earlier than filling from the front.",
               "A further speed-up is memoisation. When positions n, n-1, ..., i+1 are filled, what remains is only the set of values still unused. Processing positions in the fixed order n down to 1 means the number of used values tells you the current position, so the state is just the bitmask of used values: at most 2<sup>n</sup> states, each tried with up to n values. Counts for n = 1..14 are 1, 2, 3, 8, 10, 36, 41, 132, 250, 700, 750, 4010, 4237, 10680."],
    time="O(2<sup>n</sup> &middot; n)", space="O(2<sup>n</sup>)",
    solution='''def countArrangements(n):
    memo = {}

    def go(used, pos):
        # pos counts down from n to 1; used is the bitmask of values already placed
        if pos == 0:
            return 1
        if used in memo:
            return memo[used]
        total = 0
        for v in range(1, n + 1):
            if not used >> (v - 1) & 1 and (v % pos == 0 or pos % v == 0):
                total += go(used | (1 << (v - 1)), pos - 1)
        memo[used] = total
        return total

    return go(0, n)
''',
    tests=[[1], [2], [3], [4], [5], [6], [7], [8], [9], [10], [11], [12], [13], [14]],
)


def b_arr(n):
    if n <= 7:
        return sum(1 for perm in _perms(range(1, n + 1))
                   if all(v % (i + 1) == 0 or (i + 1) % v == 0 for i, v in enumerate(perm)))
    # larger n: plain front-to-back search with no memo and no mask tricks
    used = [False] * (n + 1)

    def go(i):
        if i > n:
            return 1
        t = 0
        for v in range(1, n + 1):
            if not used[v] and (v % i == 0 or i % v == 0):
                used[v] = True
                t += go(i + 1)
                used[v] = False
        return t

    return go(1)


def v_arr(tests):
    known = [1, 2, 3, 8, 10, 36, 41, 132, 250, 700, 750, 4010, 4237, 10680]
    for t in tests:
        n = t["args"][0]
        assert 1 <= n <= 14 and t["expected"] == known[n - 1]


CHECKS["divisible-arrangements-count"] = (b_arr, lambda r: [r.randint(1, 9)], "exact")
VALIDATE["divisible-arrangements-count"] = v_arr


# ================================================================== HARD

# ---------------------------------------------------------------- walk every cell
def _walk_tests():
    r = rnd(7501)
    out = []

    def mk(m, n, blocked, s, e):
        g = [[0] * n for _ in range(m)]
        for (x, y) in blocked:
            g[x][y] = -1
        g[s[0]][s[1]] = 1
        g[e[0]][e[1]] = 2
        return [g]

    out.append(mk(5, 5, [], (0, 0), (4, 4)))
    out.append(mk(5, 5, [], (0, 0), (0, 4)))
    out.append(mk(5, 5, [], (2, 2), (0, 0)))
    out.append(mk(4, 5, [], (0, 0), (3, 4)))
    out.append(mk(1, 20, [], (0, 0), (0, 19)))
    out.append(mk(1, 20, [], (0, 19), (0, 0)))
    out.append(mk(5, 5, [(1, 1), (3, 3)], (0, 0), (4, 4)))
    out.append(mk(5, 5, [(2, 2)], (0, 0), (4, 4)))
    out.append(mk(5, 5, [(0, 2), (2, 0), (2, 4), (4, 2)], (0, 0), (4, 4)))
    out.append(mk(3, 8, [(1, 3), (1, 4)], (0, 0), (2, 7)))
    out.append(mk(5, 5, [(0, 4), (4, 0)], (0, 0), (4, 4)))
    out.append(mk(4, 6, [(1, 1), (2, 4)], (3, 0), (0, 5)))
    return out


add(
    id="walk-every-cell-count", title="Walk Through Every Cell", diff="Hard", topic=TOPIC,
    fn="countFullWalks", params=[("grid", "int[][]")], ret="int", cmp="exact",
    desc="<p>A grid is given as an integer matrix. The values mean: <code>1</code> the start cell, <code>2</code> the end cell, <code>0</code> a free cell, and <code>-1</code> a blocked cell that cannot be entered. There is exactly one start and one end cell.</p><p>A walk begins at the start cell, moves one step at a time up, down, left or right, never enters a blocked cell, and never visits a cell twice. Return the number of walks that finish on the end cell <em>and</em> have visited every non-blocked cell of the grid.</p>",
    constraints=["1 &le; grid.length, grid[i].length and grid.length &middot; grid[i].length &le; 25", "grid[i][j] is one of -1, 0, 1, 2", "Exactly one cell is 1 and exactly one cell is 2"],
    hints=["Count how many cells can be visited in total. A valid walk must use exactly that many cells and finish on the end cell.",
           "Depth-first search from the start: mark a cell as visited, try the four neighbours that are free and unvisited, then unmark it. Reaching the end cell counts only if every free cell has been visited by then.",
           "Reaching the end cell early (with free cells left) is a dead end, so return 0 there. Track the number of cells still unvisited instead of re-scanning the grid, which makes the check O(1)."],
    editorial=["Let <code>free</code> be the number of cells that are not blocked (start and end included). Run a DFS from the start with a counter of cells left to visit. At the end cell, return 1 if the counter shows that everything has been visited and 0 otherwise; the walk must not continue past the end cell, since it can only be left once. At other cells mark the cell visited, add up the results from every free unvisited neighbour, and unmark the cell on the way back.",
               "The search tree is bounded by the number of self-avoiding walks on at most 25 cells, which is small enough for plain backtracking in the judge. Larger grids would need stronger pruning (for example checking that the unvisited cells stay connected) or a broken-profile DP, but that is not needed here."],
    time="O(3<sup>m &middot; n</sup>) worst case", space="O(m &middot; n)",
    solution='''def countFullWalks(grid):
    m, n = len(grid), len(grid[0])
    free = 0
    sr = sc = 0
    for r in range(m):
        for c in range(n):
            if grid[r][c] != -1:
                free += 1
            if grid[r][c] == 1:
                sr, sc = r, c
    seen = [[False] * n for _ in range(m)]

    def go(r, c, left):
        # left = cells not yet visited after standing on (r, c)
        if grid[r][c] == 2:
            return 1 if left == 0 else 0
        seen[r][c] = True
        total = 0
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nr, nc = r + dr, c + dc
            if 0 <= nr < m and 0 <= nc < n and grid[nr][nc] != -1 and not seen[nr][nc]:
                total += go(nr, nc, left - 1)
        seen[r][c] = False
        return total

    return go(sr, sc, free - 1)
''',
    tests=[[[[1, 0, 0, 0], [0, 0, 0, 0], [0, 0, 2, -1]]],
           [[[1, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 2]]],
           [[[0, 1], [2, 0]]],
           [[[1, 2]]], [[[2, 1]]],
           [[[1, 0, 2]]], [[[1, -1, 2]]],
           [[[1], [0], [2]]],
           [[[1, 0], [0, 0], [-1, 2]]],
           [[[1, 0, 0], [0, 2, 0], [0, 0, 0]]]],
)
for _p in __import__("lib").P:
    if _p["id"] == "walk-every-cell-count":
        _p["tests"].extend(_walk_tests())


def b_walk(grid):
    # DP over (visited set, current cell); independent of the depth-first search in the solution
    m, n = len(grid), len(grid[0])
    cells = [(r, c) for r in range(m) for c in range(n) if grid[r][c] != -1]
    idx = {cell: i for i, cell in enumerate(cells)}
    s = next(idx[(r, c)] for (r, c) in cells if grid[r][c] == 1)
    e = next(idx[(r, c)] for (r, c) in cells if grid[r][c] == 2)
    nbrs = [[idx[(r + dr, c + dc)] for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)) if (r + dr, c + dc) in idx]
            for (r, c) in cells]
    dp = {(1 << s, s): 1}
    for _ in range(len(cells) - 1):
        nxt = {}
        for (mask, cur), ways in dp.items():
            if cur == e:
                continue
            for nb in nbrs[cur]:
                if not mask >> nb & 1:
                    key = (mask | 1 << nb, nb)
                    nxt[key] = nxt.get(key, 0) + ways
        dp = nxt
    full = (1 << len(cells)) - 1
    return dp.get((full, e), 0)


def g_walk(r):
    while True:
        m, n = r.randint(1, 4), r.randint(1, 4)
        if m * n < 2 or m * n > 12:
            continue
        g = [[-1 if r.random() < 0.18 else 0 for _ in range(n)] for _ in range(m)]
        pos = [(x, y) for x in range(m) for y in range(n)]
        s, e = r.sample(pos, 2)
        g[s[0]][s[1]] = 1
        g[e[0]][e[1]] = 2
        return [g]


def v_walk(tests):
    for t in tests:
        g = t["args"][0]
        flat = [x for row in g for x in row]
        assert 1 <= len(g) and all(len(row) == len(g[0]) for row in g) and len(flat) <= 25
        assert all(x in (-1, 0, 1, 2) for x in flat)
        assert flat.count(1) == 1 and flat.count(2) == 1
    assert any(t["expected"] > 0 for t in tests) and any(t["expected"] == 0 for t in tests)


CHECKS["walk-every-cell-count"] = (b_walk, g_walk, "exact")
VALIDATE["walk-every-cell-count"] = v_walk


# ---------------------------------------------------------------- expression add operators (count)
def _expr_tests():
    r = rnd(7701)
    out = [["123456789", 100], ["123456789", 45], ["123456789", 0], ["123456789", -1], ["987654321", 100],
           ["999999999", 81], ["000000000", 0], ["105105105", 5], ["909090909", 9], ["123456789", 2147483647],
           ["123456789", -2147483648], ["111111111", 11], ["100000001", 1]]
    for _ in range(3):
        out.append(["".join(r.choice("0123456789") for _ in range(9)), r.randint(-50, 300)])
    return out


add(
    id="expression-add-operators-count", title="Count Target Expressions", diff="Hard", topic=TOPIC,
    fn="countExpressions", params=[("num", "string"), ("target", "int")], ret="int", cmp="exact",
    desc="<p>You are given a string <code>num</code> of decimal digits and an integer <code>target</code>. You may place one of <code>+</code>, <code>-</code>, <code>*</code> or nothing in each gap between neighbouring digits. Digits with nothing between them join into a single multi-digit number.</p><p>Count how many of these choices produce an expression whose value, using the usual rule that <code>*</code> binds tighter than <code>+</code> and <code>-</code>, equals <code>target</code>. A number with more than one digit may not start with <code>0</code> (so <code>05</code> is not allowed, but a lone <code>0</code> is). Different choices count separately even if the resulting strings differ only by operators that happen to give the same value.</p>",
    constraints=["1 &le; num.length &le; 9", "num contains only the digits 0-9", "-2<sup>31</sup> &le; target &le; 2<sup>31</sup> - 1"],
    hints=["There are four choices per gap, so at most 4<sup>8</sup> expressions. A depth-first search that decides the next number and the operator before it enumerates them without building strings.",
           "Carry the value so far. The difficulty is multiplication: it must apply only to the term just before it, not to the whole sum so far.",
           "Also carry the last term that was added or subtracted. To multiply by <code>v</code>, replace that last term <code>t</code> with <code>t * v</code>: new total = total - t + t * v, and the new last term is <code>t * v</code>. Stop extending a number as soon as it would start with a zero and have a second digit."],
    editorial=["Recurse over the start index of the next operand. At each step try every operand <code>num[i..j]</code>, skipping the cases where it has a leading zero and more than one digit. The first operand starts the expression. For later operands there are three options: add it (total + v, last term v), subtract it (total - v, last term -v) or multiply it into the last term (total - last + last * v, last term last * v). When all digits are consumed, count the path if the total equals the target.",
               "Tracking the last term is what makes precedence work without parsing: a product extends the most recent additive term, so we undo that term's contribution and put back the larger one. With at most nine digits all operands and products stay below 10<sup>9</sup>, which fits in 32 bits."],
    time="O(4<sup>n</sup>)", space="O(n) recursion",
    solution='''def countExpressions(num, target):
    n = len(num)

    def go(i, total, last):
        if i == n:
            return 1 if total == target else 0
        cnt = 0
        for j in range(i, n):
            if j > i and num[i] == "0":
                break
            v = int(num[i:j + 1])
            if i == 0:
                cnt += go(j + 1, v, v)
            else:
                cnt += go(j + 1, total + v, v)
                cnt += go(j + 1, total - v, -v)
                cnt += go(j + 1, total - last + last * v, last * v)
        return cnt

    return go(0, 0, 0)
''',
    tests=[["123", 6], ["232", 8], ["105", 5], ["00", 0], ["345623749", 9], ["1", 1], ["1", 2], ["0", 0],
           ["12", 12], ["12", 3], ["1234", 10], ["2020", 0], ["0000", 0]],
)
for _p in __import__("lib").P:
    if _p["id"] == "expression-add-operators-count":
        _p["tests"].extend(_expr_tests())


def b_expr(num, target):
    cnt = 0
    for ops in _product(("", "+", "-", "*"), repeat=len(num) - 1):
        s = num[0]
        for d, o in zip(num[1:], ops):
            s += o + d
        if any(len(tok) > 1 and tok[0] == "0" for tok in re.split(r"[+\-*]", s)):
            continue
        if eval(s) == target:
            cnt += 1
    return cnt


def g_expr(r):
    n = r.randint(1, 6)
    num = "".join(r.choice("0123456789" if r.random() < 0.7 else "012") for _ in range(n))
    if r.random() < 0.7:
        # a target that is actually reachable
        s = num[0]
        for d in num[1:]:
            s += r.choice(("", "+", "-", "*")) + d
        try:
            tgt = eval(s)
        except SyntaxError:
            tgt = r.randint(-20, 100)
    else:
        tgt = r.randint(-20, 100)
    return [num, tgt]


def v_expr(tests):
    for t in tests:
        num, target = t["args"]
        assert 1 <= len(num) <= 9 and num.isdigit() and -(2 ** 31) <= target <= 2 ** 31 - 1
    assert any(t["expected"] > 0 for t in tests) and any(t["expected"] == 0 for t in tests)


CHECKS["expression-add-operators-count"] = (b_expr, g_expr, "exact")
VALIDATE["expression-add-operators-count"] = v_expr
