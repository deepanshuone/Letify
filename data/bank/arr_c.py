"""Problems: arrays & hashing, in-place array manipulation (rotate, partition, reorder, swap tricks). See data/lib.py for the registry."""
from collections import Counter, deque
from itertools import groupby, permutations

from lib import add, rnd, CHECKS, VALIDATE, gen_arr  # noqa: F401

# ---------------------------------------------------------------- EASY

p = add(
    id="duplicate-zeros-in-place", title="Duplicate Zeros", diff="Easy", topic="Arrays & Hashing",
    fn="duplicateZeros", params=[("nums", "int[]")], ret="int[]", cmp="exact",
    desc="<p>Rewrite the array <code>nums</code> so that every <code>0</code> is written twice in a row. All other elements keep their order and shift to the right to make room. The array keeps its original length, so elements pushed past the end are simply dropped.</p><p>Return the resulting array (same length as <code>nums</code>). Aim for O(1) extra space.</p><pre>nums = [1, 0, 2, 3, 0, 4, 5, 0]\nresult = [1, 0, 0, 2, 3, 0, 0, 4]</pre>",
    constraints=["1 &le; nums.length &le; 10,000", "0 &le; nums[i] &le; 99"],
    hints=["Building a new longer list and cutting it to the original length works. Can you avoid the extra list?",
           "Writing from the front would overwrite elements you have not read yet. Which direction is safe?",
           "Count the zeros first, so you know where the last element ends up if the array were long enough. Then walk from the back with a read index and a write index, and write only when the write index is inside the array."],
    editorial=["Imagine the fully expanded array of length <code>n + zeros</code>. Every element of the original has a known final position there, and the real array is just its first <code>n</code> cells.",
               "Walk <code>i</code> from the end of <code>nums</code> backwards with a write pointer <code>j</code> that starts at <code>n + zeros - 1</code>. Copy <code>nums[i]</code> to <code>j</code> if <code>j &lt; n</code>, then move <code>j</code> down; if the element is a zero, write one more zero at the new <code>j</code> (again only if inside the array) and move <code>j</code> down again. Because <code>j &ge; i</code> at all times, no unread value is overwritten.",
               "One pass to count and one pass to write give O(n) time and O(1) extra space."],
    time="O(n)", space="O(1)",
    solution='''def duplicateZeros(nums):
    a = list(nums)
    n = len(a)
    j = n + a.count(0) - 1
    for i in range(n - 1, -1, -1):
        if j < n:
            a[j] = a[i]
        j -= 1
        if a[i] == 0:
            if j < n:
                a[j] = 0
            j -= 1
    return a
''',
    tests=[[[1, 0, 2, 3, 0, 4, 5, 0]], [[1, 2, 3]], [[0]], [[0, 0]], [[0, 0, 0, 0]], [[5]], [[1, 0]], [[0, 1]],
           [[0, 1, 0, 2, 0, 3, 0]], [[9, 8, 7, 0, 6]], [[3, 0, 0, 0, 4, 5]]],
)
_r = rnd(7301)
p["tests"].append([[0 if _r.random() < 0.3 else _r.randint(1, 99) for _ in range(7000)]])
p["tests"].append([[0] * 6000])
p["tests"].append([[_r.randint(1, 99) for _ in range(8000)]])


def b_dupzero(nums):
    out = []
    for x in nums:
        out.append(x)
        if x == 0:
            out.append(0)
    return out[:len(nums)]


def g_dupzero(r):
    return [r.choice((0, 0, 1, 2, 3)) for _ in range(r.randint(1, 10))]


def v_dupzero(tests):
    for t in tests:
        nums = t["args"][0]
        assert 1 <= len(nums) <= 10000 and all(0 <= x <= 99 for x in nums)
        assert len(t["expected"]) == len(nums)


CHECKS["duplicate-zeros-in-place"] = (b_dupzero, lambda r: [g_dupzero(r)], "exact")
VALIDATE["duplicate-zeros-in-place"] = v_dupzero

p = add(
    id="reverse-first-k-of-every-2k", title="Reverse First K of Every 2K", diff="Easy", topic="Arrays & Hashing",
    fn="reverseBlocks", params=[("nums", "int[]"), ("k", "int")], ret="int[]", cmp="exact",
    desc="<p>Cut <code>nums</code> into consecutive blocks of <code>2k</code> elements (the last block may be shorter). In every block, reverse the first <code>k</code> elements; if the block has fewer than <code>k</code> elements, reverse all of them. The remaining elements of a block stay where they are.</p><p>Return the resulting array.</p><pre>nums = [1, 2, 3, 4, 5, 6, 7, 8, 9], k = 3\nresult = [3, 2, 1, 4, 5, 6, 9, 8, 7]</pre>",
    constraints=["1 &le; nums.length &le; 10,000", "1 &le; k &le; 10,000", "-10<sup>9</sup> &le; nums[i] &le; 10<sup>9</sup>"],
    hints=["Only the elements at positions <code>0..k-1</code>, <code>2k..3k-1</code>, <code>4k..5k-1</code> and so on are touched.",
           "Loop over the block starts <code>s = 0, 2k, 4k, ...</code>. The segment to reverse is <code>[s, min(s + k, n) - 1]</code>.",
           "Reverse each segment in place with two pointers that move toward each other; the <code>min</code> with <code>n</code> takes care of a short last block."],
    editorial=["The statement describes a loop over block starts <code>s</code> in steps of <code>2k</code>. For each start, the range to reverse is <code>s .. min(s + k, n) - 1</code>. When fewer than <code>k</code> elements remain, the clamp to <code>n</code> reverses just what is left, which is exactly the rule for a short block.",
               "Reversing a segment in place uses a left and a right pointer that swap and move inward. Every element is swapped at most once, so the total cost is O(n) time and O(1) extra space."],
    time="O(n)", space="O(1)",
    solution='''def reverseBlocks(nums, k):
    a = list(nums)
    n = len(a)
    for s in range(0, n, 2 * k):
        lo, hi = s, min(s + k, n) - 1
        while lo < hi:
            a[lo], a[hi] = a[hi], a[lo]
            lo += 1
            hi -= 1
    return a
''',
    tests=[[[1, 2, 3, 4, 5, 6, 7, 8, 9], 3], [[1, 2, 3, 4, 5], 2], [[1, 2], 5], [[7], 1], [[1, 2, 3, 4], 1], [[1, 2, 3, 4], 2],
           [[1, 2, 3, 4, 5, 6], 3], [[1, 2, 3, 4, 5, 6, 7], 3], [[5, -1, 8, 0, 3], 4], [[-1000000000, 1000000000, 0], 2]],
)
_r = rnd(7302)
p["tests"].append([[_r.randint(-999, 999) for _ in range(3000)], 7])
p["tests"].append([[_r.randint(-10 ** 9, 10 ** 9) for _ in range(1000)], 1000])
p["tests"].append([[_r.randint(-999, 999) for _ in range(3000)], 10000])


def b_revblocks(nums, k):
    out = []
    for s in range(0, len(nums), 2 * k):
        block = nums[s:s + 2 * k]
        out += block[:k][::-1] + block[k:]
    return out


def g_revblocks(r):
    return [gen_arr(r, -9, 9, 1, 14), r.randint(1, 8)]


def v_revblocks(tests):
    for t in tests:
        nums, k = t["args"]
        assert 1 <= len(nums) <= 10000 and 1 <= k <= 10000
        assert sorted(t["expected"]) == sorted(nums)


CHECKS["reverse-first-k-of-every-2k"] = (b_revblocks, g_revblocks, "exact")
VALIDATE["reverse-first-k-of-every-2k"] = v_revblocks

# ---------------------------------------------------------------- MEDIUM

p = add(
    id="stable-three-way-pivot-partition", title="Stable Pivot Partition", diff="Medium", topic="Arrays & Hashing",
    fn="pivotPartition", params=[("nums", "int[]"), ("pivot", "int")], ret="int[]", cmp="exact",
    desc="<p>Rearrange <code>nums</code> around the value <code>pivot</code> so that three groups appear in this order: first every element <em>smaller</em> than <code>pivot</code>, then every element <em>equal</em> to <code>pivot</code>, then every element <em>greater</em> than <code>pivot</code>.</p><p>The partition must be <strong>stable</strong>: inside each group, elements keep the relative order they had in <code>nums</code>. Return the rearranged array.</p><pre>nums = [9, 12, 5, 10, 14, 3, 10], pivot = 10\nresult = [9, 5, 3, 10, 10, 12, 14]</pre>",
    constraints=["1 &le; nums.length &le; 10,000", "-10<sup>9</sup> &le; nums[i], pivot &le; 10<sup>9</sup>", "pivot does not need to occur in nums"],
    hints=["Sorting by a three-valued key (-1, 0, +1) keeps order inside each group if the sort is stable, but it is more than you need.",
           "Because the order inside each group is preserved, one scan that appends every element to the right group already produces the answer.",
           "Make one pass collecting the three groups into separate lists (or into three zones of the output with write indices), then concatenate them. A counting pass tells you where each zone starts, so you can write directly into the output."],
    editorial=["An in-place swap partition such as the Dutch national flag scheme is fast but not stable: swapping from the far end changes the relative order. Stability is what makes this version different, and the simplest way to obtain it is to preserve order while writing.",
               "Scan once and send every element to the smaller, equal or greater group, keeping insertion order. The answer is smaller + equal + greater. Equivalently, count the sizes first and write each element to the next free cell of its zone. Both versions run in O(n) time; the grouping version uses O(n) extra space for the output, which is also the size of the answer.",
               "Making a stable partition work with only O(1) extra space is possible but needs rotations and costs more time, which is why practical code accepts the linear buffer."],
    time="O(n)", space="O(n)",
    solution='''def pivotPartition(nums, pivot):
    less, same, more = [], [], []
    for x in nums:
        if x < pivot:
            less.append(x)
        elif x == pivot:
            same.append(x)
        else:
            more.append(x)
    return less + same + more
''',
    tests=[[[9, 12, 5, 10, 14, 3, 10], 10], [[-3, 4, 3, 2], 2], [[1], 1], [[1], 5], [[1], -5], [[4, 4, 4], 4], [[5, 4, 3, 2, 1], 3],
           [[1, 2, 3, 4, 5], 3], [[3, 1, 3, 1, 3, 1], 2], [[-10 ** 9, 10 ** 9, 0], 0], [[7, 7, 8, 6, 7, 9, 5], 7]],
)
_r = rnd(7303)
p["tests"].append([[_r.randint(-1000, 1000) for _ in range(4000)], 17])
p["tests"].append([[_r.randint(-5, 5) for _ in range(5000)], 0])
p["tests"].append([[_r.randint(-10 ** 9, 10 ** 9) for _ in range(1500)], 123456])


def b_pivot(nums, pivot):
    # stable sort on the sign of (x - pivot)
    return sorted(nums, key=lambda x: (x > pivot) - (x < pivot))


def g_pivot(r):
    return [gen_arr(r, -5, 5, 1, 12), r.randint(-6, 6)]


def v_pivot(tests):
    for t in tests:
        nums, pivot = t["args"]
        assert 1 <= len(nums) <= 10000 and -10 ** 9 <= pivot <= 10 ** 9


CHECKS["stable-three-way-pivot-partition"] = (b_pivot, g_pivot, "exact")
VALIDATE["stable-three-way-pivot-partition"] = v_pivot

p = add(
    id="alternating-max-min-arrangement", title="Alternating Largest and Smallest", diff="Medium", topic="Arrays & Hashing",
    fn="alternateMaxMin", params=[("nums", "int[]")], ret="int[]", cmp="exact",
    desc="<p>The array <code>nums</code> is sorted in non-decreasing order. Rearrange it so that its elements appear in this order: the largest, the smallest, the second largest, the second smallest, the third largest, and so on, until all elements are used. Return the rearranged array.</p><p>An O(1)-extra-space solution exists: the trick is to pack two numbers into one cell.</p><pre>nums = [1, 2, 3, 4, 5, 6, 7]\nresult = [7, 1, 6, 2, 5, 3, 4]</pre>",
    constraints=["1 &le; nums.length &le; 10,000", "0 &le; nums[i] &le; 10,000", "nums is sorted in non-decreasing order"],
    hints=["Two pointers, one at the start and one at the end, give the answer immediately if you may write into a new array.",
           "To work in place, a cell must hold both its old value (still needed by later steps) and its new value.",
           "Let <code>m = max + 1</code>. Store <code>nums[i] += (new value % m) * m</code>. The old value is <code>cell % m</code> and the new value is <code>cell // m</code>. After one pass, divide every cell by <code>m</code>."],
    editorial=["With a new array this is a plain two-pointer merge: take from the right end for even output positions and from the left end for odd positions.",
               "To avoid the extra array, encode two values in one cell. Choose <code>m</code> larger than every value, so any value <code>v &lt; m</code> can be recovered as <code>cell % m</code>. At output position <code>i</code>, add <code>(source % m) * m</code> to the cell; reading the source with <code>% m</code> makes sure that a source cell that was already modified still yields its original value. The finished value of each cell is <code>cell // m</code>.",
               "The bound 10,000 on the values keeps <code>m * m</code> near 10<sup>8</sup>, safely inside a 32-bit integer. The algorithm makes two linear passes: O(n) time and O(1) extra space."],
    time="O(n)", space="O(1)",
    solution='''def alternateMaxMin(nums):
    a = list(nums)
    n = len(a)
    m = a[-1] + 1
    lo, hi = 0, n - 1
    for i in range(n):
        if i % 2 == 0:
            a[i] += (a[hi] % m) * m
            hi -= 1
        else:
            a[i] += (a[lo] % m) * m
            lo += 1
    return [x // m for x in a]
''',
    tests=[[[1, 2, 3, 4, 5, 6, 7]], [[1, 2, 3, 4, 5, 6]], [[5]], [[0]], [[1, 2]], [[3, 3, 3]], [[0, 0, 1, 1]], [[0, 10000]],
           [[1, 1, 2, 2, 3, 3, 4, 4]], [[2, 4, 6, 8, 10]], [[0, 5, 5, 9, 10000, 10000]]],
)
_r = rnd(7304)
p["tests"].append([sorted(_r.randint(0, 10000) for _ in range(3000))])
p["tests"].append([sorted(_r.randint(0, 3) for _ in range(5001))])
p["tests"].append([list(range(4000))])


def b_altmaxmin(nums):
    dq = deque(nums)
    out = []
    take_max = True
    while dq:
        out.append(dq.pop() if take_max else dq.popleft())
        take_max = not take_max
    return out


def g_altmaxmin(r):
    return sorted(gen_arr(r, 0, 12, 1, 12))


def v_altmaxmin(tests):
    for t in tests:
        nums = t["args"][0]
        assert 1 <= len(nums) <= 10000 and nums == sorted(nums) and 0 <= nums[0] and nums[-1] <= 10000


CHECKS["alternating-max-min-arrangement"] = (b_altmaxmin, lambda r: [g_altmaxmin(r)], "exact")
VALIDATE["alternating-max-min-arrangement"] = v_altmaxmin

p = add(
    id="slide-and-merge-row", title="Slide and Merge a Row", diff="Medium", topic="Arrays & Hashing",
    fn="slideRow", params=[("row", "int[]")], ret="int[]", cmp="exact",
    desc="<p>A row of a sliding-tile puzzle is given as an array. A <code>0</code> is an empty cell and any other value is a tile. Slide the whole row to the <strong>left</strong> using these rules:</p><ul><li>All tiles move left as far as possible, keeping their order, so that the empty cells end up on the right.</li><li>Scanning from the left, two <em>adjacent</em> tiles (after the slide) with the same value merge into a single tile whose value is their sum. A tile created by a merge cannot merge again in the same move, and every tile takes part in at most one merge.</li></ul><p>Return the row after the move. Its length equals the length of <code>row</code>.</p><pre>row = [2, 2, 2, 0, 4, 4]\nresult = [4, 2, 8, 0, 0, 0]\n\nrow = [2, 2, 2, 2]\nresult = [4, 4, 0, 0]</pre>",
    constraints=["1 &le; row.length &le; 10,000", "Each element is 0 or a power of two between 1 and 2<sup>20</sup>"],
    hints=["First deal with the empty cells: collect the non-zero tiles in order.",
           "After compaction, merging is a left-to-right scan: if the current tile equals the next one, they merge and you skip both; otherwise the current tile stays.",
           "Write the results into the front of the row with a write pointer and fill the rest with zeros. Do not compare against the freshly merged tile: it must not merge a second time."],
    editorial=["Two separate ideas are combined here: compacting (the stable move of zeros to the back, as in the classic move-zeroes exercise) and a single left-to-right pairing.",
               "After compacting, use an index <code>i</code>. If <code>i + 1</code> exists and <code>tiles[i] == tiles[i + 1]</code>, output twice the value and advance <code>i</code> by 2; otherwise output <code>tiles[i]</code> and advance by 1. Advancing by 2 guarantees that neither of the two merged tiles, nor the new tile, is reused. Run length matters: in <code>[2, 2, 2]</code> the left two merge and the third stays, giving <code>[4, 2]</code>.",
               "Finally pad with zeros to the original length. The values never exceed 2<sup>21</sup>, so 32-bit integers are enough. Time O(n), space O(1) beyond the result (the whole procedure can be done with two pointers directly inside the array)."],
    time="O(n)", space="O(1)",
    solution='''def slideRow(row):
    n = len(row)
    tiles = [x for x in row if x != 0]
    out = []
    i = 0
    while i < len(tiles):
        if i + 1 < len(tiles) and tiles[i] == tiles[i + 1]:
            out.append(tiles[i] * 2)
            i += 2
        else:
            out.append(tiles[i])
            i += 1
    return out + [0] * (n - len(out))
''',
    tests=[[[2, 2, 2, 0, 4, 4]], [[2, 2, 2, 2]], [[0]], [[2]], [[0, 0, 0]], [[0, 2, 0, 2]], [[2, 4, 4, 8]], [[4, 4, 8, 8]],
           [[1, 1, 2, 0, 2, 4]], [[0, 0, 8, 8, 0, 16]], [[1048576, 1048576, 0, 1]], [[2, 0, 2, 0, 2, 0, 2]]],
)
_r = rnd(7305)
_vals = [0, 0, 1, 2, 2, 4, 4, 8]
p["tests"].append([[_r.choice(_vals) for _ in range(8000)]])
p["tests"].append([[2 ** _r.randint(0, 20) if _r.random() < 0.7 else 0 for _ in range(7000)]])
p["tests"].append([[4] * 9999])


def b_slide(row):
    tiles = [x for x in row if x]
    out = []
    for v, grp in groupby(tiles):
        c = len(list(grp))
        out += [2 * v] * (c // 2) + [v] * (c % 2)
    return out + [0] * (len(row) - len(out))


def g_slide(r):
    return [r.choice((0, 0, 1, 2, 2, 4)) for _ in range(r.randint(1, 10))]


def v_slide(tests):
    for t in tests:
        row = t["args"][0]
        assert 1 <= len(row) <= 10000
        for x in row:
            assert x == 0 or (1 <= x <= 2 ** 20 and x & (x - 1) == 0)
        assert len(t["expected"]) == len(row)


CHECKS["slide-and-merge-row"] = (b_slide, lambda r: [g_slide(r)], "exact")
VALIDATE["slide-and-merge-row"] = v_slide

p = add(
    id="maximum-swap-digits", title="Maximum Swap of Digits", diff="Medium", topic="Arrays & Hashing",
    fn="maximumSwap", params=[("digits", "int[]")], ret="int[]", cmp="exact",
    desc="<p>The array <code>digits</code> holds the decimal digits of a number, most significant digit first. You may swap two of the digits (any two positions) <strong>at most once</strong>. Return the digit array of the largest number you can obtain. Leading zeros are not an issue: all arrays have the same length, so comparing numbers is the same as comparing arrays element by element from the left.</p><pre>digits = [2, 7, 3, 6]\nresult = [7, 2, 3, 6]\n\ndigits = [9, 9, 7, 3]\nresult = [9, 9, 7, 3]</pre>",
    constraints=["1 &le; digits.length &le; 10,000", "0 &le; digits[i] &le; 9"],
    hints=["Trying all pairs of positions is O(n<sup>2</sup>) pairs. Think about which position should receive a bigger digit.",
           "The leftmost position that has a larger digit somewhere to its right is the one to fix. Which digit should come in?",
           "Record the last index of each digit 0..9. For each position from the left, look for the largest digit greater than the current one whose last index lies to the right; swap with that last index. Taking the <em>last</em> occurrence puts the small digit as far right as possible."],
    editorial=["To maximise the array lexicographically, improve the leftmost position that can be improved. That is the first index <code>i</code> that has a strictly larger digit somewhere to its right. At that position put the largest such digit.",
               "If that largest digit occurs several times, take its <em>last</em> occurrence: the smaller digit that gets moved out lands as far right as possible, where it hurts least. Precomputing <code>last[d]</code> for the ten digits and checking digits 9 down to <code>digits[i] + 1</code> at each position gives O(10 n) = O(n) time and O(1) space.",
               "If no position has a larger digit to its right, the digits are already non-increasing and the number cannot be improved; return it unchanged."],
    time="O(n)", space="O(1)",
    solution='''def maximumSwap(digits):
    a = list(digits)
    last = [-1] * 10
    for i, d in enumerate(a):
        last[d] = i
    for i, d in enumerate(a):
        for e in range(9, d, -1):
            if last[e] > i:
                a[i], a[last[e]] = a[last[e]], a[i]
                return a
    return a
''',
    tests=[[[2, 7, 3, 6]], [[9, 9, 7, 3]], [[1, 9, 9, 3]], [[5]], [[1, 2]], [[2, 1]], [[1, 0, 0, 9]], [[9, 8, 9, 8]], [[1, 1, 1, 1]],
           [[0, 0, 5]], [[4, 3, 2, 1, 9, 9, 1]], [[9, 0, 9, 0, 9]], [[1, 2, 3, 4, 5, 6, 7, 8, 9]]],
)
_r = rnd(7306)
p["tests"].append([[_r.randint(0, 9) for _ in range(8000)]])
p["tests"].append([sorted((_r.randint(0, 9) for _ in range(7000)), reverse=True)[:6000] + [9]])
p["tests"].append([[_r.randint(0, 2) for _ in range(7500)]])


def b_maxswap(digits):
    best = list(digits)
    n = len(digits)
    for i in range(n):
        for j in range(i + 1, n):
            c = list(digits)
            c[i], c[j] = c[j], c[i]
            if c > best:
                best = c
    return best


def g_maxswap(r):
    return gen_arr(r, 0, 9, 1, 9)


def v_maxswap(tests):
    for t in tests:
        d = t["args"][0]
        assert 1 <= len(d) <= 10000 and all(0 <= x <= 9 for x in d)


CHECKS["maximum-swap-digits"] = (b_maxswap, lambda r: [g_maxswap(r)], "exact")
VALIDATE["maximum-swap-digits"] = v_maxswap

p = add(
    id="previous-permutation-with-one-swap", title="Previous Arrangement With One Swap", diff="Medium", topic="Arrays & Hashing",
    fn="previousWithOneSwap", params=[("nums", "int[]")], ret="int[]", cmp="exact",
    desc="<p>Swap exactly two elements of <code>nums</code> (two different positions) so that the resulting array is the <strong>lexicographically largest array that is still smaller than <code>nums</code></strong>. Return it.</p><p>If no single swap can make the array lexicographically smaller, return <code>nums</code> unchanged. Values may repeat.</p><pre>nums = [3, 2, 1]        result = [3, 1, 2]\nnums = [1, 1, 5]        result = [1, 1, 5]\nnums = [1, 9, 4, 6, 7]  result = [1, 7, 4, 6, 9]\nnums = [3, 1, 1, 3]     result = [1, 3, 1, 3]</pre>",
    constraints=["1 &le; nums.length &le; 10,000", "1 &le; nums[i] &le; 10<sup>4</sup>"],
    hints=["A swap makes the array smaller exactly when a larger value moves to a later position than a smaller one it passes. The earlier the changed position, the bigger the drop, so you want the change as far right as possible.",
           "Find the rightmost index <code>i</code> with <code>nums[i] &gt; nums[i + 1]</code>. If there is none, the array is non-decreasing and nothing can be done.",
           "At <code>i</code>, swap with the largest value to its right that is still strictly smaller than <code>nums[i]</code>. If that value occurs several times, use the leftmost occurrence, because then the larger value <code>nums[i]</code> lands as early as possible."],
    editorial=["Lexicographic order is decided by the first position where two arrays differ, so we want to disturb the array as far to the right as possible. The disturbed (smaller) position must receive a smaller value, so it must hold a value larger than something to its right. The rightmost such position is the rightmost index <code>i</code> with <code>nums[i] &gt; nums[i + 1]</code>; any index further right is followed only by non-decreasing values.",
               "At <code>i</code> choose the replacement as large as possible but below <code>nums[i]</code>, to keep the result as large as possible. Among equal candidates, the leftmost wins: the value <code>nums[i]</code> then moves to the earliest of those positions, and a larger value earlier gives a larger array.",
               "Finding <code>i</code> and the partner takes one pass each: O(n) time, O(1) extra space."],
    time="O(n)", space="O(1)",
    solution='''def previousWithOneSwap(nums):
    a = list(nums)
    n = len(a)
    for i in range(n - 2, -1, -1):
        if a[i] > a[i + 1]:
            best = -1
            for j in range(i + 1, n):
                if a[j] < a[i] and (best == -1 or a[j] > a[best]):
                    best = j
            a[i], a[best] = a[best], a[i]
            return a
    return a
''',
    tests=[[[3, 2, 1]], [[1, 1, 5]], [[1, 9, 4, 6, 7]], [[3, 1, 1, 3]], [[1]], [[2, 1]], [[1, 2]], [[5, 5, 5]], [[1, 2, 3, 4, 5]],
           [[5, 4, 3, 2, 1]], [[2, 3, 3, 1, 1, 3]], [[7, 6, 6, 6, 8]], [[10000, 1, 10000, 1]]],
)
_r = rnd(7307)
p["tests"].append([[_r.randint(1, 10000) for _ in range(4000)]])
p["tests"].append([sorted((_r.randint(1, 50) for _ in range(3000))) + [3, 30, 3, 20, 20, 3]])
p["tests"].append([[_r.randint(1, 3) for _ in range(5000)]])


def b_prevswap(nums):
    best = None
    n = len(nums)
    for i in range(n):
        for j in range(i + 1, n):
            c = list(nums)
            c[i], c[j] = c[j], c[i]
            if c < nums and (best is None or c > best):
                best = c
    return best if best is not None else list(nums)


def g_prevswap(r):
    return gen_arr(r, 1, 5, 1, 8)


def v_prevswap(tests):
    for t in tests:
        nums = t["args"][0]
        assert 1 <= len(nums) <= 10000 and all(1 <= x <= 10000 for x in nums)


CHECKS["previous-permutation-with-one-swap"] = (b_prevswap, lambda r: [g_prevswap(r)], "exact")
VALIDATE["previous-permutation-with-one-swap"] = v_prevswap

p = add(
    id="repeated-riffle-shuffle", title="Repeated Riffle Shuffle", diff="Medium", topic="Arrays & Hashing",
    fn="riffleRepeated", params=[("nums", "int[]"), ("t", "int")], ret="int[]", cmp="exact",
    desc="<p>The array <code>nums</code> has an even length <code>2n</code>. One <strong>riffle</strong> splits it into the first half <code>a = nums[0..n-1]</code> and the second half <code>b = nums[n..2n-1]</code> and interleaves them, starting with the first half: <code>[a[0], b[0], a[1], b[1], ..., a[n-1], b[n-1]]</code>.</p><p>Apply the riffle <code>t</code> times in a row and return the final array. <code>t</code> can be huge, so you cannot afford to simulate every shuffle.</p><pre>nums = [1, 2, 3, 4, 5, 6], t = 1  result = [1, 4, 2, 5, 3, 6]\nnums = [1, 2, 3, 4, 5, 6], t = 2  result = [1, 5, 4, 3, 2, 6]</pre>",
    constraints=["2 &le; nums.length &le; 8,000 and nums.length is even", "0 &le; t &le; 10<sup>9</sup>", "-10<sup>9</sup> &le; nums[i] &le; 10<sup>9</sup>"],
    hints=["Simulating t shuffles costs O(n * t). Notice that every riffle moves each position to the same new position, no matter what values it holds.",
           "Position <code>p</code> moves to <code>2p</code> if <code>p &lt; n</code>, and to <code>2(p - n) + 1</code> otherwise. This is a permutation of positions, so it splits into cycles.",
           "Walk each cycle of positions once, in the order of the moves. In a cycle of length <code>L</code>, applying the riffle t times moves the element at the cycle's <code>k</code>-th position to the <code>(k + t) mod L</code>-th position."],
    editorial=["A shuffle is a fixed permutation of positions. Applying it t times is the permutation raised to the power t, and a permutation is easiest to power through its cycle decomposition: inside a cycle of length <code>L</code>, t steps are equivalent to <code>t mod L</code> steps.",
               "Define <code>dest(p) = 2p</code> for <code>p &lt; n</code> and <code>2(p - n) + 1</code> otherwise. Visit every unvisited position, follow <code>dest</code> to collect its cycle <code>c[0], c[1], ..., c[L-1]</code> (so <code>dest(c[k]) = c[k+1]</code>), and place the value from <code>c[k]</code> at <code>c[(k + t) mod L]</code> of the result.",
               "Every position is visited once, so the running time is O(n), independent of t, and the extra space is O(n) for the visited flags and the answer. (The cycle structure is the classic perfect-shuffle one, with <code>dest(p) = 2p mod (2n - 1)</code> for all but the last position, but the explicit piecewise rule is enough.)"],
    time="O(n)", space="O(n)",
    solution='''def riffleRepeated(nums, t):
    m = len(nums)
    h = m // 2
    res = [0] * m
    seen = [False] * m
    for s in range(m):
        if seen[s]:
            continue
        cyc = []
        p = s
        while not seen[p]:
            seen[p] = True
            cyc.append(p)
            p = 2 * p if p < h else 2 * (p - h) + 1
        L = len(cyc)
        sh = t % L
        for k, pos in enumerate(cyc):
            res[cyc[(k + sh) % L]] = nums[pos]
    return res
''',
    tests=[[[1, 2, 3, 4, 5, 6], 1], [[1, 2, 3, 4, 5, 6], 2], [[1, 2], 5], [[1, 2, 3, 4], 0], [[1, 2, 3, 4], 3], [[1, 2, 3, 4, 5, 6, 7, 8], 3],
           [[5, 5, 1, 1], 7], [[10, 20, 30, 40, 50, 60, 70, 80, 90, 100], 1000000000], [[-1, 0, 1, -1, 0, 1], 999999999],
           [[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], 6]],
)
_r = rnd(7308)
p["tests"].append([[_r.randint(-10 ** 9, 10 ** 9) for _ in range(1000)], 1000000000])
p["tests"].append([[_r.randint(-999, 999) for _ in range(6000)], 123456789])
p["tests"].append([list(range(5000)), 47])


def b_riffle(nums, t):
    cur = list(nums)
    h = len(cur) // 2
    for _ in range(t):
        nxt = []
        for i in range(h):
            nxt.append(cur[i])
            nxt.append(cur[h + i])
        cur = nxt
    return cur


def g_riffle(r):
    return [[r.randint(-9, 9) for _ in range(2 * r.randint(1, 7))], r.randint(0, 40)]


def v_riffle(tests):
    for t in tests:
        nums, k = t["args"]
        assert 2 <= len(nums) <= 8000 and len(nums) % 2 == 0 and 0 <= k <= 10 ** 9
        assert sorted(t["expected"]) == sorted(nums)


CHECKS["repeated-riffle-shuffle"] = (b_riffle, g_riffle, "exact")
VALIDATE["repeated-riffle-shuffle"] = v_riffle

# ---------------------------------------------------------------- HARD

p = add(
    id="lexicographically-smallest-no-adjacent-equal", title="Smallest Arrangement With No Equal Neighbours", diff="Hard", topic="Arrays & Hashing", tier="extra",
    fn="smallestNoAdjacentEqual", params=[("nums", "int[]")], ret="int[]", cmp="exact",
    desc="<p>Reorder the elements of <code>nums</code> so that no two neighbouring elements are equal. Many such orders can exist, so the answer is defined as the <strong>lexicographically smallest</strong> valid order (compare element by element from the left).</p><p>If no valid order exists, return an empty array.</p><pre>nums = [1, 1, 2, 2, 3]  result = [1, 2, 1, 2, 3]\nnums = [2, 1, 2]        result = [2, 1, 2]\nnums = [1, 1, 1, 2]     result = []</pre>",
    constraints=["1 &le; nums.length &le; 5,000", "-1000 &le; nums[i] &le; 1000", "At most 40 distinct values appear in the large tests"],
    hints=["First decide when any valid order exists. Where can the most frequent value sit so that its copies never touch?",
           "A valid order exists iff the highest frequency is at most <code>ceil(n / 2)</code>. Build the answer left to right, always trying the smallest value that differs from the previous one.",
           "The smallest candidate is only usable if the remaining elements can still be arranged after it. With <code>m</code> elements left, every count must be at most <code>ceil(m / 2)</code>, and when <code>m</code> is odd and some value has exactly <code>(m + 1) / 2</code> copies, that value must come first, so it must differ from the value you just placed."],
    editorial=["Greedy construction: at each step choose the smallest value that (1) differs from the previously placed value and (2) leaves a completable remainder. Because we always take the smallest feasible value, the result is the lexicographically smallest valid order.",
               "The key is an exact feasibility test for a multiset of <code>m</code> remaining elements whose first element must differ from <code>v</code>. An arrangement without equal neighbours exists iff no count exceeds <code>ceil(m / 2)</code>. If <code>m</code> is even and a value has exactly <code>m / 2</code> copies, both patterns (that value first or second) work, so we can always start with a different value and the constraint on <code>v</code> costs nothing. If <code>m</code> is odd and a value has exactly <code>(m + 1) / 2</code> copies, it must occupy the first, third, ... positions, so it is forced to be first and therefore must not equal <code>v</code>. In all other cases a start different from <code>v</code> exists.",
               "Each step tries candidates in increasing order, and the test inspects the distinct values only. Typically one or two candidates are tried, so the time is about O(n * d) for d distinct values, with O(d) extra space. An up-front check that the maximum frequency is at most <code>ceil(n / 2)</code> handles the impossible case."],
    time="O(n * d)", space="O(d)",
    solution='''def smallestNoAdjacentEqual(nums):
    from collections import Counter
    n = len(nums)
    cnt = Counter(nums)
    vals = sorted(cnt)
    if max(cnt.values()) > (n + 1) // 2:
        return []
    out = []
    prev = None
    for step in range(n):
        m = n - step - 1
        chosen = None
        for v in vals:
            if cnt[v] == 0 or v == prev:
                continue
            cnt[v] -= 1
            ok = True
            if m > 0:
                lim = (m + 1) // 2
                for u in vals:
                    c = cnt[u]
                    if c > lim or (m % 2 == 1 and c == lim and u == v):
                        ok = False
                        break
            if ok:
                chosen = v
                break
            cnt[v] += 1
        out.append(chosen)
        prev = chosen
    return out
''',
    tests=[[[1, 1, 2, 2, 3]], [[2, 1, 2]], [[1, 1, 1, 2]], [[5]], [[4, 4]], [[1, 2]], [[2, 1]], [[3, 3, 1, 1, 1]], [[1, 1, 1, 2, 2, 3, 3]],
           [[-5, -5, 0, 0, 7, 7, 7]], [[2, 2, 2, 1, 1, 3, 3, 3]], [[1, 1, 2, 2, 2, 2]], [[9, 9, 9, 9, 1, 2, 3]]],
)
_r = rnd(7309)
_a = [_r.randint(-20, 19) for _ in range(3500)] + [7] * 1500; _r.shuffle(_a)
p["tests"].append([_a])
_a = [_r.randint(1, 8) for _ in range(4000)]; _r.shuffle(_a)
p["tests"].append([_a])
_a = [1] * 2500 + [2] * 2499; _r.shuffle(_a)
p["tests"].append([_a])


def b_noadj(nums):
    best = None
    for perm in set(permutations(nums)):
        if all(perm[i] != perm[i + 1] for i in range(len(perm) - 1)):
            if best is None or perm < best:
                best = perm
    return list(best) if best is not None else []


def g_noadj(r):
    return gen_arr(r, 1, r.choice((2, 3, 4)), 1, 8)


def v_noadj(tests):
    for t in tests:
        nums = t["args"][0]
        assert 1 <= len(nums) <= 5000 and all(-1000 <= x <= 1000 for x in nums)
        assert len(set(nums)) <= 40
        e = t["expected"]
        if e:
            assert sorted(e) == sorted(nums) and all(e[i] != e[i + 1] for i in range(len(e) - 1))
        else:
            assert max(Counter(nums).values()) > (len(nums) + 1) // 2


CHECKS["lexicographically-smallest-no-adjacent-equal"] = (b_noadj, lambda r: [g_noadj(r)], "exact")
VALIDATE["lexicographically-smallest-no-adjacent-equal"] = v_noadj

p = add(
    id="largest-array-after-k-adjacent-swaps", title="Largest Array After K Adjacent Swaps", diff="Hard", topic="Arrays & Hashing", tier="extra",
    fn="largestAfterAdjacentSwaps", params=[("nums", "int[]"), ("k", "int")], ret="int[]", cmp="exact",
    desc="<p>In one operation you may swap two <strong>neighbouring</strong> elements of <code>nums</code>. Using at most <code>k</code> operations, make the array lexicographically as large as possible (compare element by element from the left) and return it.</p><pre>nums = [3, 9, 1, 2], k = 2\nresult = [9, 3, 2, 1]\n\nnums = [1, 2, 3], k = 1\nresult = [2, 1, 3]</pre>",
    constraints=["1 &le; nums.length &le; 3,000", "0 &le; k &le; 10<sup>9</sup>", "-10<sup>6</sup> &le; nums[i] &le; 10<sup>6</sup>"],
    hints=["The first position matters most. Which values can reach position 0 with at most k adjacent swaps?",
           "Only the elements in the window <code>nums[0..k]</code> can reach position 0, at a cost equal to their index. Pick the largest value in that window; if it occurs more than once, pick the leftmost copy because it is cheaper.",
           "Move the chosen element to the front, subtract its distance from <code>k</code>, and repeat for position 1 with the new budget, then position 2, and so on until the budget is used up."],
    editorial=["Greedy by position. For the current position <code>i</code> and remaining budget <code>k</code>, the candidates that can still be brought to <code>i</code> are the elements at indices <code>i .. min(n - 1, i + k)</code>. Taking the largest candidate gives the best possible value for this position, and no later position can compensate for a smaller one.",
               "Ties are broken toward the leftmost copy: the value is the same but the move is cheaper, leaving more budget for later positions. Moving an element from index <code>j</code> to <code>i</code> by adjacent swaps shifts the elements <code>i .. j-1</code> one cell to the right and costs exactly <code>j - i</code>. This is a pop and an insert on the list.",
               "Each position scans a window of up to <code>min(n, k + 1)</code> elements and shifts up to <code>n</code> elements, so the time is O(n<sup>2</sup>) (a few milliseconds for n = 3,000 with built-in slicing, or O(n log n) with a segment tree plus a Fenwick tree for the shifts). Because the window is clipped at the end of the array, k = 10<sup>9</sup> is handled without any special case."],
    time="O(n^2)", space="O(n)",
    solution='''def largestAfterAdjacentSwaps(nums, k):
    a = list(nums)
    n = len(a)
    for i in range(n):
        if k == 0:
            break
        w = a[i:i + k + 1]
        mx = max(w)
        j = i + w.index(mx)
        if j > i:
            a.insert(i, a.pop(j))
            k -= j - i
    return a
''',
    tests=[[[3, 9, 1, 2], 2], [[1, 2, 3], 1], [[1, 2, 3], 0], [[7], 5], [[1, 2, 3, 4, 5], 100], [[5, 4, 3, 2, 1], 3], [[1, 5, 5, 2], 2],
           [[2, 2, 2], 4], [[4, 1, 7, 7, 3], 3], [[-3, -1, -2, -5], 2], [[0, 9, 0, 9, 0, 9], 5], [[1, 9, 9, 9, 1], 3]],
)
_r = rnd(7310)
p["tests"].append([[_r.randint(-10 ** 6, 10 ** 6) for _ in range(3000)], 10 ** 9])
p["tests"].append([[_r.randint(0, 9) for _ in range(3000)], 1500])
p["tests"].append([[_r.randint(-10 ** 6, 10 ** 6) for _ in range(2500)], 40])


def b_adjswaps(nums, k):
    seen = {tuple(nums)}
    frontier = [tuple(nums)]
    for _ in range(k):
        nxt = []
        for s in frontier:
            for i in range(len(s) - 1):
                c = list(s)
                c[i], c[i + 1] = c[i + 1], c[i]
                c = tuple(c)
                if c not in seen:
                    seen.add(c)
                    nxt.append(c)
        if not nxt:
            break
        frontier = nxt
    return list(max(seen))


def g_adjswaps(r):
    return [gen_arr(r, 0, 5, 1, 6), r.randint(0, 9)]


def v_adjswaps(tests):
    for t in tests:
        nums, k = t["args"]
        assert 1 <= len(nums) <= 3000 and 0 <= k <= 10 ** 9 and all(-10 ** 6 <= x <= 10 ** 6 for x in nums)
        assert sorted(t["expected"]) == sorted(nums)


CHECKS["largest-array-after-k-adjacent-swaps"] = (b_adjswaps, g_adjswaps, "exact")
VALIDATE["largest-array-after-k-adjacent-swaps"] = v_adjswaps

p = add(
    id="rotate-grid-layers", title="Rotate Grid Layers", diff="Hard", topic="Arrays & Hashing", tier="extra",
    fn="rotateLayers", params=[("grid", "int[][]"), ("k", "int")], ret="int[][]", cmp="exact",
    desc="<p>A grid with an even number of rows and an even number of columns is made of nested rectangular <strong>layers</strong>: layer 0 is the outer border of cells, layer 1 is the border of what remains after removing layer 0, and so on.</p><p>One <strong>rotation step</strong> moves every cell value of every layer one position <em>counter-clockwise</em> along its own layer (on the top row values move left, on the left column they move down, on the bottom row right, on the right column up). Apply <code>k</code> rotation steps to all layers at once and return the new grid.</p><pre>grid = [[1, 2, 3, 4],\n        [5, 6, 7, 8],\n        [9, 10, 11, 12],\n        [13, 14, 15, 16]], k = 1\nresult = [[2, 3, 4, 8],\n          [1, 7, 11, 12],\n          [5, 6, 10, 16],\n          [9, 13, 14, 15]]</pre>",
    constraints=["2 &le; rows, columns &le; 60, and both are even", "0 &le; k &le; 10<sup>9</sup>", "-10<sup>9</sup> &le; grid[i][j] &le; 10<sup>9</sup>"],
    hints=["Rotating the whole grid k times costs O(k * cells). Each layer is independent of the others, though.",
           "Unroll one layer into a list by walking its border clockwise from its top-left cell; the layer is then a cycle, and rotating it by one step is a shift of this list by one place.",
           "A layer with <code>L</code> cells only needs <code>k mod L</code> shifts. Counter-clockwise by <code>s</code> steps means the value written at index <code>i</code> of the clockwise list is the old value at index <code>(i + s) mod L</code>. Write the shifted list back along the same path."],
    editorial=["A layer of a grid with even sides is a simple closed ring of <code>2 * (h + w) - 4</code> cells (<code>h</code> and <code>w</code> are its height and width, both at least 2), and the layers do not touch each other. So the problem splits into independent cyclic rotations.",
               "For layer <code>l</code>, the corners are <code>top = l</code>, <code>left = l</code>, <code>bottom = rows - 1 - l</code>, <code>right = cols - 1 - l</code>. List the cells clockwise: the top row from left to right, the right column going down, the bottom row from right to left, and the left column going up (without repeating corners). Moving values one step counter-clockwise moves each value one place <em>backwards</em> in this clockwise list, so after <code>s = k mod L</code> steps the cell at list index <code>i</code> receives the old value from index <code>(i + s) mod L</code>.",
               "Every cell is read and written once: O(rows * cols) time, with the layer list as O(rows + cols) auxiliary memory per layer (plus the output grid). The huge value of k only enters through <code>k mod L</code>."],
    time="O(rows * cols)", space="O(rows * cols)",
    solution='''def rotateLayers(grid, k):
    m = len(grid)
    n = len(grid[0])
    res = [row[:] for row in grid]
    for lay in range(min(m, n) // 2):
        t, l, b, r = lay, lay, m - 1 - lay, n - 1 - lay
        cells = [(t, j) for j in range(l, r + 1)]
        cells += [(i, r) for i in range(t + 1, b + 1)]
        cells += [(b, j) for j in range(r - 1, l - 1, -1)]
        cells += [(i, l) for i in range(b - 1, t, -1)]
        vals = [grid[i][j] for i, j in cells]
        L = len(cells)
        s = k % L
        for idx, (i, j) in enumerate(cells):
            res[i][j] = vals[(idx + s) % L]
    return res
''',
    tests=[[[[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12], [13, 14, 15, 16]], 1], [[[40, 10], [30, 20]], 1], [[[40, 10], [30, 20]], 4],
           [[[1, 2], [3, 4]], 3], [[[1, 2, 3, 4], [5, 6, 7, 8]], 1], [[[1, 2, 3, 4], [5, 6, 7, 8]], 2], [[[1, 2], [3, 4], [5, 6], [7, 8]], 1],
           [[[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12], [13, 14, 15, 16]], 0], [[[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12], [13, 14, 15, 16]], 1000000000],
           [[[-5, 0, 5, 9, 1, 2], [3, 3, 3, 4, 4, 4], [7, 8, 9, 0, 1, 2], [-1, -2, -3, -4, -5, -6]], 7]],
)
_r = rnd(7311)
p["tests"].append([[[_r.randint(-10 ** 9, 10 ** 9) for _ in range(60)] for _ in range(60)], 1000000000])
p["tests"].append([[[_r.randint(0, 99) for _ in range(40)] for _ in range(60)], 12345])
p["tests"].append([[[_r.randint(-10 ** 9, 10 ** 9) for _ in range(10)] for _ in range(50)], 99])


def b_layers(grid, k):
    m, n = len(grid), len(grid[0])
    cur = [row[:] for row in grid]
    for _ in range(k):
        nxt = [row[:] for row in cur]
        for i in range(m):
            for j in range(n):
                t, l, b, r = min(i, j, m - 1 - i, n - 1 - j), None, None, None
                top, left, bot, right = t, t, m - 1 - t, n - 1 - t
                if i == top and j > left:
                    ni, nj = i, j - 1
                elif j == left and i < bot:
                    ni, nj = i + 1, j
                elif i == bot and j < right:
                    ni, nj = i, j + 1
                else:
                    ni, nj = i - 1, j
                nxt[ni][nj] = cur[i][j]
        cur = nxt
    return cur


def g_layers(r):
    m, n = 2 * r.randint(1, 3), 2 * r.randint(1, 3)
    return [[[r.randint(-9, 9) for _ in range(n)] for _ in range(m)], r.randint(0, 30)]


def v_layers(tests):
    for t in tests:
        g, k = t["args"]
        m, n = len(g), len(g[0])
        assert 2 <= m <= 60 and 2 <= n <= 60 and m % 2 == 0 and n % 2 == 0 and all(len(row) == n for row in g)
        assert 0 <= k <= 10 ** 9 and all(-10 ** 9 <= v <= 10 ** 9 for row in g for v in row)


CHECKS["rotate-grid-layers"] = (b_layers, g_layers, "exact")
VALIDATE["rotate-grid-layers"] = v_layers
