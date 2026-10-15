"""Problems: two pointers on sorted sequences (merging, intersecting, interval lists, medians). See data/lib.py."""
from lib import add, rnd, CHECKS, VALIDATE, gen_arr  # noqa: F401

TOPIC = "Two Pointers"


def sorted_rand(r, n, lo, hi):
    return sorted(r.randint(lo, hi) for _ in range(n))


# ---------------------------------------------------------------- EASY

p = add(
    id="values-in-exactly-one-sorted-array", title="Values in Exactly One of Two Sorted Arrays", diff="Easy", topic=TOPIC,
    fn="exclusiveValues", params=[("a", "int[]"), ("b", "int[]")], ret="int[]", cmp="exact",
    desc="<p>Two integer arrays <code>a</code> and <code>b</code> are each sorted in non-decreasing order and may contain repeated values. Return a sorted array of the <em>distinct</em> values that occur in exactly one of the two arrays, that is, in <code>a</code> or in <code>b</code> but not in both.</p><pre>a = [1, 2, 2, 3, 7]\nb = [2, 4, 7, 7, 9]\nresult = [1, 3, 4, 9]</pre><p>The value 2 occurs in both arrays and 7 occurs in both, so neither is reported. Each reported value appears once, in strictly increasing order.</p>",
    constraints=["0 &le; a.length, b.length &le; 5,000", "-10<sup>9</sup> &le; a[i], b[i] &le; 10<sup>9</sup>", "Both arrays are sorted in non-decreasing order"],
    hints=["Putting both arrays into sets and taking the symmetric difference works, but then you must sort again. Can the sorted order do the work for you?",
           "Sweep with one pointer per array. Compare <code>a[i]</code> and <code>b[j]</code>: the smaller value cannot appear in the other array any more.",
           "If the values differ, the smaller one is exclusive: output it (unless it equals the last output) and skip all copies of it. If they are equal, skip all copies of that value in both arrays. When one array ends, the rest of the other is exclusive."],
    editorial=["Walk two pointers <code>i</code> and <code>j</code> forward. Because both arrays are sorted, if <code>a[i] &lt; b[j]</code> then <code>a[i]</code> is smaller than everything left in <code>b</code>, so it can never be matched: it is an exclusive value. Output it and move <code>i</code> past every copy of that value. Symmetrically for <code>b[j] &lt; a[i]</code>. When the two are equal, the value is shared, so move both pointers past all of its copies and output nothing.",
               "When one array runs out, every remaining distinct value of the other array is exclusive. Skipping whole runs of equal values (or comparing with the last output) keeps the result free of repeats. The algorithm touches each element once, so it runs in O(n + m) time with O(1) extra space beyond the output."],
    time="O(n + m)", space="O(1) extra",
    solution='''def exclusiveValues(a, b):
    i = j = 0
    res = []
    while i < len(a) or j < len(b):
        if j == len(b) or (i < len(a) and a[i] < b[j]):
            x = a[i]
            res.append(x)
            while i < len(a) and a[i] == x:
                i += 1
        elif i == len(a) or b[j] < a[i]:
            x = b[j]
            res.append(x)
            while j < len(b) and b[j] == x:
                j += 1
        else:
            x = a[i]
            while i < len(a) and a[i] == x:
                i += 1
            while j < len(b) and b[j] == x:
                j += 1
    return res
''',
    tests=[[[1, 2, 2, 3, 7], [2, 4, 7, 7, 9]], [[], []], [[1, 1, 2], []], [[], [-4, -4, 0]], [[5, 5, 5], [5, 5]],
           [[1, 3, 5], [2, 4, 6]], [[-10 ** 9, 0, 10 ** 9], [-10 ** 9, 10 ** 9]], [[1, 2, 3], [1, 2, 3, 4, 5]],
           [[0], [0, 0, 1]], [[-3, -3, -1], [-2, -2, -1, -1]]],
)
_r = rnd(4001)
p["tests"].append([sorted_rand(_r, 1200, -20000, 20000), sorted_rand(_r, 1200, -20000, 20000)])
p["tests"].append([sorted_rand(_r, 2500, 0, 300), sorted_rand(_r, 2500, 200, 500)])
_a = sorted_rand(_r, 800, -10 ** 9, 10 ** 9)
p["tests"].append([_a, _a[::2] + sorted_rand(_r, 150, -10 ** 9, 10 ** 9)])
p["tests"][-1][1].sort()


def b_exclusive(a, b):
    return sorted(set(a) ^ set(b))


def g_exclusive(r):
    return [sorted(gen_arr(r, -5, 5, 0, 9)), sorted(gen_arr(r, -5, 5, 0, 9))]


def v_exclusive(tests):
    for t in tests:
        a, b = t["args"]
        assert len(a) <= 5000 and len(b) <= 5000
        assert all(-10 ** 9 <= x <= 10 ** 9 for x in a + b)
        assert a == sorted(a) and b == sorted(b), "not sorted"
        e = t["expected"]
        assert all(e[i] < e[i + 1] for i in range(len(e) - 1))


CHECKS["values-in-exactly-one-sorted-array"] = (b_exclusive, g_exclusive, "exact")
VALIDATE["values-in-exactly-one-sorted-array"] = v_exclusive

p = add(
    id="common-values-of-three-sorted-arrays", title="Common Values of Three Sorted Arrays", diff="Easy", topic=TOPIC,
    fn="commonToAllThree", params=[("a", "int[]"), ("b", "int[]"), ("c", "int[]")], ret="int[]", cmp="exact",
    desc="<p>Three integer arrays <code>a</code>, <code>b</code> and <code>c</code> are each sorted in non-decreasing order and may contain repeats. Return the sorted array of <em>distinct</em> values that appear in all three arrays.</p><pre>a = [1, 2, 2, 4, 6, 9]\nb = [2, 2, 4, 5, 9]\nc = [0, 2, 4, 4, 9, 12]\nresult = [2, 4, 9]</pre><p>If no value is shared by all three arrays, return an empty array.</p>",
    constraints=["0 &le; a.length, b.length, c.length &le; 5,000", "-10<sup>9</sup> &le; a[i], b[i], c[i] &le; 10<sup>9</sup>", "Each array is sorted in non-decreasing order"],
    hints=["Intersecting with sets works, but it ignores the sorted order. Try to extend the two-array merge walk to three arrays.",
           "Keep three pointers. If the three current values are not all equal, which pointers can safely move?",
           "Let <code>m</code> be the largest of the three current values. Any pointer sitting on a value smaller than <code>m</code> can never match, so advance it. If all three are equal, record the value (skip it if it equals the last recorded one) and advance all three."],
    editorial=["Use one pointer per array. Let <code>m = max(a[i], b[j], c[k])</code>. A pointer whose value is below <code>m</code> points at something that cannot be present in the array that holds <code>m</code> at or after its pointer, so it is safe to advance it. When all three values equal <code>m</code>, the value is common to all arrays: record it unless it was just recorded (repeats), then advance all three pointers.",
               "The loop stops as soon as any pointer reaches the end of its array, because nothing more can be common. Every iteration advances at least one pointer, so the work is O(n + m + p) with O(1) extra space beyond the output."],
    time="O(n + m + p)", space="O(1) extra",
    solution='''def commonToAllThree(a, b, c):
    i = j = k = 0
    res = []
    while i < len(a) and j < len(b) and k < len(c):
        x, y, z = a[i], b[j], c[k]
        if x == y == z:
            if not res or res[-1] != x:
                res.append(x)
            i += 1
            j += 1
            k += 1
        else:
            m = max(x, y, z)
            if x < m:
                i += 1
            if y < m:
                j += 1
            if z < m:
                k += 1
    return res
''',
    tests=[[[1, 2, 2, 4, 6, 9], [2, 2, 4, 5, 9], [0, 2, 4, 4, 9, 12]], [[], [], []], [[1, 2, 3], [], [1, 2, 3]], [[1], [1], [1]],
           [[1, 1, 1], [1, 1], [1, 1, 1, 1]], [[1, 2, 3], [4, 5, 6], [7, 8, 9]], [[1, 2, 3], [2, 3, 4], [5, 6, 7]],
           [[-10 ** 9, 0, 10 ** 9], [-10 ** 9, 5, 10 ** 9], [-10 ** 9, 10 ** 9]], [[-5, -5, -2, 0], [-5, -2, -2], [-6, -5, -2, 7]],
           [[3, 5, 7, 9], [5, 9], [1, 5, 8, 9, 10]]],
)
_r = rnd(4002)
p["tests"].append([sorted_rand(_r, 2500, 0, 3000), sorted_rand(_r, 2500, 0, 3000), sorted_rand(_r, 2500, 0, 3000)])
_base = sorted_rand(_r, 500, -10 ** 9, 10 ** 9)
p["tests"].append([sorted(_base + sorted_rand(_r, 100, -10 ** 9, 10 ** 9)), sorted(_base[::2] + sorted_rand(_r, 150, -10 ** 9, 10 ** 9)),
                   sorted(_base[1::3] + _base[::5] + sorted_rand(_r, 150, -10 ** 9, 10 ** 9))])
p["tests"].append([[2 * i for i in range(2000)], [3 * i for i in range(1500)], [5 * i for i in range(1000)]])


def b_common3(a, b, c):
    return sorted(set(a) & set(b) & set(c))


def g_common3(r):
    return [sorted(gen_arr(r, -4, 4, 0, 9)) for _ in range(3)]


def v_common3(tests):
    for t in tests:
        for arr in t["args"]:
            assert len(arr) <= 5000 and arr == sorted(arr), "bad array"
            assert all(-10 ** 9 <= x <= 10 ** 9 for x in arr)


CHECKS["common-values-of-three-sorted-arrays"] = (b_common3, g_common3, "exact")
VALIDATE["common-values-of-three-sorted-arrays"] = v_common3

p = add(
    id="sparse-vector-dot-product-sorted-indices", title="Dot Product of Two Sparse Vectors", diff="Easy", topic=TOPIC,
    fn="sparseDot", params=[("idxA", "int[]"), ("valA", "int[]"), ("idxB", "int[]"), ("valB", "int[]")], ret="int", cmp="exact",
    desc="<p>A huge vector is mostly zeros, so it is stored sparsely as two parallel arrays: <code>idx</code> holds the positions of the stored entries in strictly increasing order, and <code>val</code> holds the entry at each of those positions. Every position that is not listed is zero.</p><p>Vector A is given by <code>idxA</code> and <code>valA</code>, vector B by <code>idxB</code> and <code>valB</code>. Return the dot product of the two vectors: the sum of <code>A[p] * B[p]</code> over all positions <code>p</code>.</p><pre>idxA = [0, 3, 8, 20]   valA = [2, -1, 5, 4]\nidxB = [3, 4, 8, 9]    valB = [6, 7, 2, 1]\nresult = (-1)*6 + 5*2 = 4</pre><p>Only positions stored in both vectors contribute to the sum.</p>",
    constraints=["0 &le; idxA.length = valA.length, idxB.length = valB.length &le; 5,000", "0 &le; idx[i] &le; 10<sup>9</sup>, and each idx array is strictly increasing", "-100 &le; val[i] &le; 100"],
    hints=["Building full-length dense vectors is impossible, positions go up to 10<sup>9</sup>. Work only with the stored entries.",
           "A dictionary from position to value for one vector works. But both index arrays are sorted, so no dictionary is needed.",
           "Use two pointers over the index arrays: when the indices are equal multiply the values and advance both; otherwise advance the pointer with the smaller index."],
    editorial=["Only positions present in both vectors contribute, so the task is exactly the intersection of two sorted index lists. Keep a pointer into each list. If <code>idxA[i] == idxB[j]</code> add <code>valA[i] * valB[j]</code> to the answer and advance both. Otherwise the smaller index cannot occur in the other list any more, so advance that pointer.",
               "Each step advances at least one pointer, giving O(n + m) time and O(1) extra space. With at most 5,000 entries of magnitude at most 100 the sum is at most 5,000 &middot; 10,000 = 5 &middot; 10<sup>7</sup>, comfortably inside 32 bits. When one vector is much shorter than the other, binary searching each of its indices in the longer one is an alternative."],
    time="O(n + m)", space="O(1)",
    solution='''def sparseDot(idxA, valA, idxB, valB):
    i = j = 0
    total = 0
    while i < len(idxA) and j < len(idxB):
        if idxA[i] == idxB[j]:
            total += valA[i] * valB[j]
            i += 1
            j += 1
        elif idxA[i] < idxB[j]:
            i += 1
        else:
            j += 1
    return total
''',
    tests=[[[0, 3, 8, 20], [2, -1, 5, 4], [3, 4, 8, 9], [6, 7, 2, 1]], [[], [], [], []], [[5], [7], [], []], [[5], [7], [5], [-3]],
           [[5], [7], [6], [3]], [[0, 10 ** 9], [100, -100], [0, 10 ** 9], [100, 100]], [[1, 2, 3], [1, 2, 3], [1, 2, 3], [4, 5, 6]],
           [[1, 3, 5, 7], [9, 9, 9, 9], [2, 4, 6, 8], [9, 9, 9, 9]], [[0, 1, 2], [0, 5, 0], [0, 1, 2], [3, 0, 4]],
           [[2, 4, 6, 8, 10], [-1, -2, -3, -4, -5], [6], [10]]],
)
_r = rnd(4003)


def _sparse(r, n, hi):
    ids = sorted(r.sample(range(hi + 1), n))
    return ids, [r.randint(-100, 100) for _ in range(n)]


for _n, _hi in ((2000, 4000), (1500, 10 ** 9)):
    _ia, _va = _sparse(_r, _n, _hi)
    _ib, _vb = _sparse(_r, _n, _hi)
    p["tests"].append([_ia, _va, _ib, _vb])
_ia, _va = _sparse(_r, 2500, 3000)
p["tests"].append([_ia, [100] * 2500, _ia[:], [100] * 2500])


def b_sparse(idxA, valA, idxB, valB):
    da = dict(zip(idxA, valA))
    return sum(da.get(i, 0) * v for i, v in zip(idxB, valB))


def g_sparse(r):
    ia, va = _sparse(r, r.randint(0, 6), 9)
    ib, vb = _sparse(r, r.randint(0, 6), 9)
    return [ia, va, ib, vb]


def v_sparse(tests):
    for t in tests:
        ia, va, ib, vb = t["args"]
        assert len(ia) == len(va) <= 5000 and len(ib) == len(vb) <= 5000
        for ids in (ia, ib):
            assert all(0 <= x <= 10 ** 9 for x in ids)
            assert all(ids[k] < ids[k + 1] for k in range(len(ids) - 1)), "indices not strictly increasing"
        assert all(-100 <= x <= 100 for x in va + vb)


CHECKS["sparse-vector-dot-product-sorted-indices"] = (b_sparse, g_sparse, "exact")
VALIDATE["sparse-vector-dot-product-sorted-indices"] = v_sparse

# ---------------------------------------------------------------- MEDIUM

p = add(
    id="union-of-two-interval-lists", title="Union of Two Interval Lists", diff="Medium", topic=TOPIC,
    fn="unionIntervals", params=[("firstList", "int[][]"), ("secondList", "int[][]")], ret="int[][]", cmp="exact",
    desc="<p>You are given two lists of closed intervals <code>[start, end]</code> with integer endpoints. Inside each list the intervals are sorted by start and pairwise disjoint: the next interval always starts strictly after the previous one ends. Intervals from different lists may overlap in any way.</p><p>Return the union of both lists as one sorted list of disjoint closed intervals. Two intervals must be merged into one when they overlap or share at least one point, for example <code>[2, 4]</code> and <code>[4, 7]</code> become <code>[2, 7]</code>. Intervals that merely sit next to each other without sharing a point, such as <code>[1, 2]</code> and <code>[3, 4]</code>, stay separate.</p><pre>firstList  = [[1, 3], [6, 9]]\nsecondList = [[2, 4], [5, 6], [10, 12]]\nresult     = [[1, 4], [5, 9], [10, 12]]</pre>",
    constraints=["0 &le; firstList.length, secondList.length &le; 5,000", "0 &le; start &le; end &le; 10<sup>9</sup>", "Within each list, start<sub>i+1</sub> &gt; end<sub>i</sub>", "The result has no two intervals that overlap or share a point"],
    hints=["Concatenating both lists and sorting then merging works in O(n log n), but both lists are already sorted.",
           "At every step the next interval to process is the one with the smaller start among the two list fronts, just like the merge step of merge sort.",
           "Take the front interval with the smaller start. If its start is at most the end of the last interval in the result, extend that last interval's end to the maximum of the two ends; otherwise append it as a new interval."],
    editorial=["Merge the two lists exactly as in merge sort: repeatedly pick the front interval with the smaller start, so the intervals are visited in order of increasing start. Combine this with the usual interval-coalescing rule: if the picked interval starts at or before the end of the last interval in the output, it touches or overlaps it, so extend the output interval's end to <code>max(end, picked end)</code>. Otherwise it begins a new component and is appended.",
               "Visiting intervals by increasing start guarantees that once an interval is closed off (the next start is beyond its end), nothing later can reach back to it. Each interval is visited once, so the time is O(n + m); only the output is stored."],
    time="O(n + m)", space="O(1) extra",
    solution='''def unionIntervals(firstList, secondList):
    a, b = firstList, secondList
    i = j = 0
    res = []
    while i < len(a) or j < len(b):
        if j == len(b) or (i < len(a) and a[i][0] <= b[j][0]):
            s, e = a[i]
            i += 1
        else:
            s, e = b[j]
            j += 1
        if res and s <= res[-1][1]:
            if e > res[-1][1]:
                res[-1][1] = e
        else:
            res.append([s, e])
    return res
''',
    tests=[[[[1, 3], [6, 9]], [[2, 4], [5, 6], [10, 12]]], [[], []], [[[1, 5]], []], [[], [[0, 0]]], [[[1, 2]], [[3, 4]]],
           [[[1, 2]], [[2, 3]]], [[[0, 10]], [[2, 3], [5, 6]]], [[[0, 2], [4, 6], [8, 10]], [[1, 5], [7, 9]]],
           [[[0, 0], [2, 2], [4, 4]], [[1, 1], [3, 3]]], [[[5, 5]], [[5, 5]]], [[[0, 1], [10 ** 9, 10 ** 9]], [[1, 2], [10 ** 9 - 1, 10 ** 9]]]],
)
_r = rnd(4004)


def make_closed(r, count, gap_hi, len_hi, start_hi=3):
    out = []
    cur = r.randint(0, start_hi)
    for _ in range(count):
        s = cur + r.randint(0, gap_hi)
        e = s + r.randint(0, len_hi)
        out.append([s, e])
        cur = e + 1
    return out


p["tests"].append([make_closed(_r, 900, 8, 8), make_closed(_r, 900, 8, 8)])
p["tests"].append([make_closed(_r, 1200, 1, 2), make_closed(_r, 1200, 1, 2)])
p["tests"].append([make_closed(_r, 400, 100000, 100000), make_closed(_r, 400, 100000, 100000)])


def b_union(firstList, secondList):
    # mark doubled coordinates: point x -> 2x, gap between x and x+1 -> 2x + 1
    n = 2 * max([e for _, e in firstList + secondList] + [0]) + 2
    mark = [False] * (n + 1)
    for s, e in firstList + secondList:
        for q in range(2 * s, 2 * e + 1):
            mark[q] = True
    res = []
    q = 0
    while q <= n:
        if mark[q]:
            r0 = q
            while q + 1 <= n and mark[q + 1]:
                q += 1
            res.append([r0 // 2, q // 2])
        q += 1
    return res


def g_union(r):
    return [make_closed(r, r.randint(0, 4), 3, 3), make_closed(r, r.randint(0, 4), 3, 3)]


def v_union(tests):
    for t in tests:
        a, b = t["args"]
        for lst in (a, b):
            assert len(lst) <= 5000
            for k, (s, e) in enumerate(lst):
                assert 0 <= s <= e <= 10 ** 9
                assert k == 0 or lst[k - 1][1] < s, "intervals in a list must be disjoint and sorted"
        res = t["expected"]
        assert all(res[k][1] < res[k + 1][0] and res[k][0] <= res[k][1] for k in range(len(res) - 1))


CHECKS["union-of-two-interval-lists"] = (b_union, g_union, "exact")
VALIDATE["union-of-two-interval-lists"] = v_union

p = add(
    id="subtract-interval-list", title="Subtract One Interval List from Another", diff="Medium", topic=TOPIC,
    fn="subtractIntervals", params=[("keep", "int[][]"), ("remove", "int[][]")], ret="int[][]", cmp="exact",
    desc="<p>Two lists of <em>half-open</em> intervals <code>[start, end)</code> with integer endpoints are given: <code>keep</code> and <code>remove</code>. The interval <code>[s, e)</code> covers every real number <code>x</code> with <code>s &le; x &lt; e</code>, and <code>start &lt; end</code> always holds. Inside each list the intervals are sorted and disjoint: each one starts strictly after the previous one ends.</p><p>Return the parts of <code>keep</code> that are not covered by <code>remove</code>, as a sorted list of half-open intervals. Report the pieces maximally: each piece is a connected stretch, and no piece is empty.</p><pre>keep   = [[0, 10], [12, 20]]\nremove = [[2, 4], [8, 14], [18, 19]]\nresult = [[0, 2], [4, 8], [14, 18], [19, 20]]</pre><p>Here <code>[0, 10)</code> loses <code>[2, 4)</code> and <code>[8, 10)</code>, and <code>[12, 20)</code> loses <code>[12, 14)</code> and <code>[18, 19)</code>.</p>",
    constraints=["0 &le; keep.length, remove.length &le; 5,000", "0 &le; start &lt; end &le; 10<sup>9</sup>", "Within each list, start<sub>i+1</sub> &gt; end<sub>i</sub>"],
    hints=["Taking each interval of <code>keep</code> and testing all intervals of <code>remove</code> is O(n &middot; m). Both lists are sorted, so a pointer into <code>remove</code> never has to go backwards.",
           "Work on one interval <code>[s, e)</code> of <code>keep</code> at a time with a moving left edge <code>cur = s</code>. Walk through the removal intervals that start before <code>e</code>.",
           "For a removal interval <code>[rs, re)</code> overlapping the window: if <code>rs &gt; cur</code> output <code>[cur, rs)</code>; then set <code>cur = max(cur, re)</code>. After the loop output <code>[cur, e)</code> if <code>cur &lt; e</code>. Do not advance the removal pointer past an interval that may also cover the next <code>keep</code> interval."],
    editorial=["Process the <code>keep</code> intervals in order. For the current <code>[s, e)</code> keep a cursor <code>cur</code> that marks the start of the not-yet-resolved part, initially <code>s</code>. First skip removal intervals that end at or before <code>cur</code>; they affect nothing from here on, because later keep intervals start even further right.",
               "Then scan removal intervals that start before <code>e</code>. A removal interval beginning after the cursor leaves a surviving piece <code>[cur, rs)</code>; in every case the cursor jumps to <code>max(cur, re)</code>, the end of the removed stretch. If the cursor reaches <code>e</code> the interval is fully consumed. Otherwise the tail <code>[cur, e)</code> survives. The removal pointer is left on the last interval examined, since it can extend into the next keep interval.",
               "Pieces from different keep intervals are separated by the strict gaps in <code>keep</code>, and pieces within one interval are separated by non-empty removed stretches, so the output is automatically in canonical form. Every pointer move is permanent, so the running time is O(n + m)."],
    time="O(n + m)", space="O(1) extra",
    solution='''def subtractIntervals(keep, remove):
    res = []
    j = 0
    for s, e in keep:
        cur = s
        while j < len(remove) and remove[j][1] <= cur:
            j += 1
        k = j
        while k < len(remove) and remove[k][0] < e:
            if remove[k][0] > cur:
                res.append([cur, remove[k][0]])
            cur = max(cur, remove[k][1])
            if cur >= e:
                break
            k += 1
        if cur < e:
            res.append([cur, e])
        j = k
    return res
''',
    tests=[[[[0, 10], [12, 20]], [[2, 4], [8, 14], [18, 19]]], [[], []], [[[1, 5]], []], [[], [[1, 5]]], [[[1, 5]], [[0, 10]]],
           [[[1, 5]], [[1, 5]]], [[[1, 5]], [[5, 8]]], [[[1, 5]], [[3, 4]]], [[[0, 4], [6, 10]], [[3, 7]]],
           [[[0, 3], [4, 7], [8, 11]], [[1, 2], [5, 9]]], [[[0, 10 ** 9]], [[1, 2], [10 ** 9 - 1, 10 ** 9]]]],
)
_r = rnd(4005)


def make_half(r, count, gap_hi, len_hi, start_hi=3):
    out = []
    cur = r.randint(0, start_hi)
    for _ in range(count):
        s = cur + r.randint(0, gap_hi)
        e = s + r.randint(1, len_hi)
        out.append([s, e])
        cur = e + 1
    return out


p["tests"].append([make_half(_r, 900, 6, 8), make_half(_r, 900, 6, 8)])
p["tests"].append([make_half(_r, 1200, 2, 3), make_half(_r, 1200, 3, 6)])
p["tests"].append([make_half(_r, 400, 100000, 200000), make_half(_r, 400, 100000, 100000)])


def b_subtract(keep, remove):
    hi = max([e for _, e in keep + remove] + [0]) + 1
    inkeep = [False] * (hi + 1)
    for s, e in keep:
        for c in range(s, e):
            inkeep[c] = True
    for s, e in remove:
        for c in range(s, e):
            inkeep[c] = False
    res = []
    c = 0
    while c <= hi:
        if inkeep[c]:
            st = c
            while inkeep[c + 1]:
                c += 1
            res.append([st, c + 1])
        c += 1
    return res


def g_subtract(r):
    return [make_half(r, r.randint(0, 4), 3, 4), make_half(r, r.randint(0, 4), 3, 4)]


def v_subtract(tests):
    for t in tests:
        a, b = t["args"]
        for lst in (a, b):
            assert len(lst) <= 5000
            for k, (s, e) in enumerate(lst):
                assert 0 <= s < e <= 10 ** 9
                assert k == 0 or lst[k - 1][1] < s, "intervals in a list must be disjoint and sorted"
        res = t["expected"]
        assert all(s < e for s, e in res)
        assert all(res[k][1] < res[k + 1][0] for k in range(len(res) - 1)), "pieces must be separated"


CHECKS["subtract-interval-list"] = (b_subtract, g_subtract, "exact")
VALIDATE["subtract-interval-list"] = v_subtract

p = add(
    id="earliest-common-free-slot", title="Earliest Common Free Slot", diff="Medium", topic=TOPIC,
    fn="earliestCommonSlot", params=[("busyA", "int[][]"), ("busyB", "int[][]"), ("duration", "int"), ("dayLength", "int")], ret="int", cmp="exact",
    desc="<p>Two people want to schedule a meeting inside a day that spans the time range <code>[0, dayLength)</code>, counted in whole minutes. Each person's busy time is a list of half-open intervals <code>[start, end)</code>, sorted by start, where each meeting ends no later than the next one starts (<code>end<sub>i</sub> &le; start<sub>i+1</sub></code>), and every interval lies inside the day.</p><p>A meeting of <code>duration</code> minutes that starts at minute <code>t</code> occupies <code>[t, t + duration)</code>. It is possible if it fits in the day (<code>t + duration &le; dayLength</code>) and does not overlap any busy interval of either person. Two half-open intervals overlap when each starts before the other ends, so a meeting may begin exactly when a busy interval ends.</p><p>Return the earliest possible start minute <code>t</code>, or <code>-1</code> if no slot exists.</p><pre>busyA = [[0, 5], [8, 12]]\nbusyB = [[3, 9], [14, 16]]\nduration = 2, dayLength = 20\nresult = 12</pre><p>Together they are busy during minutes 0 to 12, and both are free during minutes 12 and 13, so the first start with two free minutes for both is 12. With <code>duration = 3</code> the gap [12, 14) is too short and the answer would be 16.</p>",
    constraints=["0 &le; busyA.length, busyB.length &le; 5,000", "1 &le; duration &le; dayLength &le; 10<sup>9</sup>", "0 &le; start &lt; end &le; dayLength for every interval", "Within each list, end<sub>i</sub> &le; start<sub>i+1</sub>"],
    hints=["Trying every start minute is impossible when the day has 10<sup>9</sup> minutes. Only the end times of busy intervals matter as candidate start times.",
           "Keep a candidate start <code>t</code>, initially 0, and a pointer into each schedule. If a busy interval overlaps <code>[t, t + duration)</code>, the candidate must jump to the end of that interval.",
           "Skip intervals with <code>end &le; t</code> in each list. If the front interval of a list has <code>start &lt; t + duration</code> it blocks the candidate: set <code>t</code> to its end and re-check both lists. If neither blocks, answer <code>t</code>. If <code>t + duration &gt; dayLength</code>, answer -1."],
    editorial=["Think of the answer as a candidate start <code>t</code> that only ever moves right. Begin with <code>t = 0</code>. In each schedule, intervals ending at or before <code>t</code> are in the past and are skipped permanently. The front interval that remains either starts at or after <code>t + duration</code>, in which case it does not interfere (and neither does anything after it), or it starts earlier and it overlaps the window. In the overlapping case no start before its end can work, so move <code>t</code> to that end.",
               "Repeat until neither schedule blocks the window (return <code>t</code>) or until the window no longer fits inside the day (return -1). Each jump retires one busy interval for good, so the loop runs at most n + m + 1 times: O(n + m) time and O(1) extra space. This is the two-pointer view of merging the two schedules and scanning for the first gap that is long enough."],
    time="O(n + m)", space="O(1)",
    solution='''def earliestCommonSlot(busyA, busyB, duration, dayLength):
    i = j = 0
    t = 0
    while t + duration <= dayLength:
        while i < len(busyA) and busyA[i][1] <= t:
            i += 1
        if i < len(busyA) and busyA[i][0] < t + duration:
            t = busyA[i][1]
            continue
        while j < len(busyB) and busyB[j][1] <= t:
            j += 1
        if j < len(busyB) and busyB[j][0] < t + duration:
            t = busyB[j][1]
            continue
        return t
    return -1
''',
    tests=[[[[0, 5], [8, 12]], [[3, 9], [14, 16]], 3, 20], [[], [], 5, 5], [[[0, 1]], [], 5, 5], [[[0, 5]], [], 5, 10],
           [[[0, 5]], [], 6, 10], [[[0, 4]], [[4, 8]], 1, 9], [[[0, 4]], [[4, 8]], 2, 9], [[[2, 3]], [[5, 6]], 2, 10],
           [[[0, 10 ** 9 - 1]], [], 1, 10 ** 9], [[[0, 10 ** 9]], [], 1, 10 ** 9], [[[1, 3], [6, 9]], [[0, 2], [4, 5], [9, 10]], 2, 12]],
)
_r = rnd(4006)


def make_busy(r, count, gap_hi, len_hi, day):
    out = []
    cur = r.randint(0, 3)
    for _ in range(count):
        s = cur + r.randint(0, gap_hi)
        e = s + r.randint(1, len_hi)
        if e > day:
            break
        out.append([s, e])
        cur = e + r.randint(0, 1)
    return out


_a = make_busy(_r, 1200, 4, 6, 10 ** 9)
_b = make_busy(_r, 1200, 4, 6, 10 ** 9)
p["tests"].append([_a, _b, 7, 40000])
_a = make_busy(_r, 1000, 3, 5, 10 ** 9)
_b = make_busy(_r, 1000, 3, 5, 10 ** 9)
p["tests"].append([_a, _b, 9, 10 ** 9])
_b = make_busy(_r, 1000, 1, 3, 10 ** 9)
p["tests"].append([_b, [[x + 1, y + 1] for x, y in _b], 4, max(y for _, y in _b) + 4])


def b_slot(busyA, busyB, duration, dayLength):
    for t in range(dayLength - duration + 1):
        ok = True
        for s, e in busyA + busyB:
            if s < t + duration and e > t:
                ok = False
                break
        if ok:
            return t
    return -1


def g_slot(r):
    day = r.randint(1, 25)
    return [make_busy(r, r.randint(0, 4), 3, 4, day), make_busy(r, r.randint(0, 4), 3, 4, day), r.randint(1, min(day, 6)), day]


def v_slot(tests):
    for t in tests:
        a, b, d, day = t["args"]
        assert 1 <= d <= day <= 10 ** 9
        for lst in (a, b):
            assert len(lst) <= 5000
            for k, (s, e) in enumerate(lst):
                assert 0 <= s < e <= day
                assert k == 0 or lst[k - 1][1] <= s, "intervals must be sorted and non-overlapping"


CHECKS["earliest-common-free-slot"] = (b_slot, g_slot, "exact")
VALIDATE["earliest-common-free-slot"] = v_slot

p = add(
    id="count-cross-array-pairs-with-target-sum", title="Count Pairs Across Two Sorted Arrays", diff="Medium", topic=TOPIC,
    fn="countPairsWithSum", params=[("a", "int[]"), ("b", "int[]"), ("target", "int")], ret="int", cmp="exact",
    desc="<p>The arrays <code>a</code> and <code>b</code> are each sorted in non-decreasing order and may contain repeated values. Count the index pairs <code>(i, j)</code> with <code>a[i] + b[j] == target</code>. Two pairs are different if their indices differ, even when the values are equal.</p><pre>a = [1, 1, 2, 4]\nb = [3, 3, 5, 6]\ntarget = 7\nresult = 5</pre><p>The pairs are <code>1 + 6</code> (two choices of the 1), <code>2 + 5</code>, and <code>4 + 3</code> (two choices of the 3): five pairs in total.</p>",
    constraints=["0 &le; a.length, b.length &le; 5,000", "-10<sup>9</sup> &le; a[i], b[j] &le; 10<sup>9</sup>", "-2&middot;10<sup>9</sup> &le; target &le; 2&middot;10<sup>9</sup>", "Both arrays are sorted in non-decreasing order"],
    hints=["Checking all n &middot; m pairs is up to 25 million operations and ignores the sorted order. A hash map of counts works, but there is an O(1) memory way.",
           "Start with a pointer <code>i</code> at the beginning of <code>a</code> and <code>j</code> at the end of <code>b</code>. If the sum is too small, only advancing <code>i</code> can raise it; if too large, only decreasing <code>j</code> can lower it.",
           "When the sum equals the target, count how many equal values <code>a</code> has at <code>i</code> (run length <code>x</code>) and how many equal values <code>b</code> has at <code>j</code> (run length <code>y</code>). They contribute <code>x * y</code> pairs. Then move both pointers past those runs."],
    editorial=["This is the classic two-sum two-pointer walk, but across two arrays and with duplicates. Place <code>i</code> at the smallest of <code>a</code> and <code>j</code> at the largest of <code>b</code>. If <code>a[i] + b[j] &lt; target</code>, then <code>a[i]</code> is too small to pair with <code>b[j]</code> or with anything smaller in <code>b</code>, so <code>a[i]</code> is finished: advance <code>i</code>. If the sum is larger, <code>b[j]</code> is too large for <code>a[i]</code> and for everything bigger in <code>a</code>: decrease <code>j</code>.",
               "When the sum hits the target, let <code>x</code> be the number of consecutive entries of <code>a</code> equal to <code>a[i]</code> and <code>y</code> the number of consecutive entries of <code>b</code> equal to <code>b[j]</code>. Every combination of one of them with one of the others is a valid pair, so add <code>x * y</code> and step both pointers beyond the runs. Counting the runs makes total work linear: O(n + m) time, O(1) extra space. The answer can reach 25,000,000, which fits in 32 bits."],
    time="O(n + m)", space="O(1)",
    solution='''def countPairsWithSum(a, b, target):
    i, j = 0, len(b) - 1
    total = 0
    while i < len(a) and j >= 0:
        s = a[i] + b[j]
        if s < target:
            i += 1
        elif s > target:
            j -= 1
        else:
            x, y = a[i], b[j]
            ca = cb = 0
            while i < len(a) and a[i] == x:
                ca += 1
                i += 1
            while j >= 0 and b[j] == y:
                cb += 1
                j -= 1
            total += ca * cb
    return total
''',
    tests=[[[1, 1, 2, 4], [3, 3, 5, 6], 7], [[], [], 0], [[1, 2], [], 3], [[5], [5], 10], [[5], [5], 11], [[0, 0, 0], [0, 0], 0],
           [[-3, -1, 2, 2, 8], [-5, -2, 0, 6, 6], 4], [[1, 2, 3], [4, 5, 6], 100], [[-10 ** 9, 10 ** 9], [-10 ** 9, 10 ** 9], 0],
           [[-10 ** 9, -10 ** 9], [-10 ** 9, -10 ** 9, -10 ** 9], -2 * 10 ** 9], [[1, 3, 3, 3, 7], [0, 4, 4, 6], 7]],
)
_r = rnd(4007)
p["tests"].append([sorted_rand(_r, 2500, -30, 30), sorted_rand(_r, 2500, -30, 30), 5])
p["tests"].append([sorted_rand(_r, 1500, -10 ** 9, 10 ** 9), sorted_rand(_r, 1500, -10 ** 9, 10 ** 9), 12345])
p["tests"].append([[7] * 5000, [3] * 5000, 10])
_a = sorted_rand(_r, 2000, -500, 500)
p["tests"].append([_a, sorted(10 - x for x in _a), 10])


def b_pairs(a, b, target):
    return sum(1 for x in a for y in b if x + y == target)


def g_pairs(r):
    return [sorted(gen_arr(r, -5, 5, 0, 9)), sorted(gen_arr(r, -5, 5, 0, 9)), r.randint(-8, 8)]


def v_pairs(tests):
    for t in tests:
        a, b, target = t["args"]
        assert len(a) <= 5000 and len(b) <= 5000
        assert a == sorted(a) and b == sorted(b)
        assert all(-10 ** 9 <= x <= 10 ** 9 for x in a + b)
        assert -2 * 10 ** 9 <= target <= 2 * 10 ** 9


CHECKS["count-cross-array-pairs-with-target-sum"] = (b_pairs, g_pairs, "exact")
VALIDATE["count-cross-array-pairs-with-target-sum"] = v_pairs

p = add(
    id="sort-transformed-array", title="Sort a Quadratic Transform of a Sorted Array", diff="Medium", topic=TOPIC, tier="extra",
    fn="sortTransformed", params=[("nums", "int[]"), ("a", "int"), ("b", "int"), ("c", "int")], ret="int[]", cmp="exact",
    desc="<p>The array <code>nums</code> is sorted in non-decreasing order. For every element <code>x</code> compute <code>f(x) = a&middot;x<sup>2</sup> + b&middot;x + c</code>, where <code>a</code>, <code>b</code> and <code>c</code> are given integers. Return all the values <code>f(x)</code> as an array sorted in non-decreasing order.</p><p>Computing and sorting is O(n log n). Because <code>f</code> is a parabola (or a line when <code>a = 0</code>), the values can be put in order in O(n).</p><pre>nums = [-4, -2, 2, 4], a = 1, b = 3, c = 5\nf(x) = x^2 + 3x + 5  gives  9, 3, 15, 33\nresult = [3, 9, 15, 33]</pre>",
    constraints=["0 &le; nums.length &le; 8,000", "-1,000 &le; nums[i] &le; 1,000, sorted in non-decreasing order", "-100 &le; a, b, c &le; 100"],
    hints=["A parabola is decreasing on one side of its vertex and increasing on the other, so the transformed sequence is a concatenation of a descending and an ascending run. Which elements give the extreme values?",
           "If <code>a &gt; 0</code> the parabola opens upwards: the largest values of <code>f</code> are at the two ends of <code>nums</code> and the smallest is near the vertex. If <code>a &lt; 0</code> the opposite holds.",
           "Use two pointers at both ends. For <code>a &ge; 0</code> fill the result from the back: put the larger of <code>f(nums[l])</code> and <code>f(nums[r])</code> at the next free back position and move that pointer inward. For <code>a &lt; 0</code> fill from the front with the smaller one."],
    editorial=["When <code>a &gt; 0</code> the graph of <code>f</code> is a valley. The farther an input is from the vertex <code>-b / 2a</code>, the larger its output, so on the sorted input the maximum of <code>f</code> over any remaining stretch is at one of its two ends. Compare <code>f</code> at the left and right ends, write the larger into the result starting from the last slot, and move the corresponding pointer inward. After n steps the result is sorted. For <code>a &lt; 0</code> the graph is a hill, so the ends hold the smallest remaining values: fill from the front with the smaller one.",
               "The case <code>a = 0</code> is a line. It is covered by the <code>a &ge; 0</code> branch: <code>f</code> is monotone, so the larger end value is always the right end (if <code>b &gt; 0</code>) or the left end (if <code>b &lt; 0</code>), and comparing the two ends still picks the correct maximum. Total work is O(n) time and O(n) output space. Magnitudes are at most 100&middot;10<sup>6</sup> + 100&middot;10<sup>3</sup> + 100, which fits in 32 bits."],
    time="O(n)", space="O(n) output",
    solution='''def sortTransformed(nums, a, b, c):
    def f(x):
        return a * x * x + b * x + c
    n = len(nums)
    res = [0] * n
    l, r = 0, n - 1
    if a >= 0:
        pos = n - 1
        while l <= r:
            fl, fr = f(nums[l]), f(nums[r])
            if fl > fr:
                res[pos] = fl
                l += 1
            else:
                res[pos] = fr
                r -= 1
            pos -= 1
    else:
        pos = 0
        while l <= r:
            fl, fr = f(nums[l]), f(nums[r])
            if fl < fr:
                res[pos] = fl
                l += 1
            else:
                res[pos] = fr
                r -= 1
            pos += 1
    return res
''',
    tests=[[[-4, -2, 2, 4], 1, 3, 5], [[], 1, 2, 3], [[5], -2, 1, 0], [[-4, -2, 2, 4], -1, 3, 5], [[-3, -1, 0, 2, 6], 0, 2, 1],
           [[-3, -1, 0, 2, 6], 0, -2, 1], [[-3, -1, 0, 2, 6], 0, 0, 7], [[-5, -5, 0, 5, 5], 2, 0, -3], [[-1000, 1000], 100, 100, 100],
           [[-1000, 1000], -100, -100, -100], [[-2, -1, 0, 1, 2], 3, -6, 0], [[1, 1, 1], -4, 8, 2]],
)
_r = rnd(4008)
p["tests"].append([sorted_rand(_r, 3000, -1000, 1000), 7, -91, 11])
p["tests"].append([sorted_rand(_r, 2500, -1000, 1000), -13, 99, -20])
p["tests"].append([sorted_rand(_r, 2000, -1000, 1000), 0, -9, 4])


def b_transformed(nums, a, b, c):
    return sorted(a * x * x + b * x + c for x in nums)


def g_transformed(r):
    return [sorted(gen_arr(r, -8, 8, 0, 9)), r.randint(-4, 4), r.randint(-6, 6), r.randint(-5, 5)]


def v_transformed(tests):
    for t in tests:
        nums, a, b, c = t["args"]
        assert len(nums) <= 8000 and nums == sorted(nums)
        assert all(-1000 <= x <= 1000 for x in nums)
        assert all(-100 <= v <= 100 for v in (a, b, c))


CHECKS["sort-transformed-array"] = (b_transformed, g_transformed, "exact")
VALIDATE["sort-transformed-array"] = v_transformed

p = add(
    id="closest-sum-across-two-sorted-arrays", title="Closest Sum Across Two Sorted Arrays", diff="Medium", topic=TOPIC,
    fn="closestPairSum", params=[("a", "int[]"), ("b", "int[]"), ("target", "int")], ret="int", cmp="exact",
    desc="<p>The non-empty arrays <code>a</code> and <code>b</code> are each sorted in non-decreasing order. Choose one element from each array, and let <code>s</code> be their sum. Return the smallest possible value of <code>|s - target|</code>.</p><pre>a = [-3, 4, 10, 20]\nb = [1, 6, 15]\ntarget = 17\nresult = 1</pre><p>The closest sums to 17 are <code>10 + 6 = 16</code> (distance 1) and <code>4 + 15 = 19</code> (distance 2), so the answer is 1.</p>",
    constraints=["1 &le; a.length, b.length &le; 5,000", "-5&middot;10<sup>8</sup> &le; a[i], b[j] &le; 5&middot;10<sup>8</sup>", "-10<sup>9</sup> &le; target &le; 10<sup>9</sup>", "Both arrays are sorted in non-decreasing order"],
    hints=["Trying all pairs takes n &middot; m steps. Use the sorted order to discard whole rows or columns of the implicit table of sums.",
           "Put <code>i</code> at the start of <code>a</code> and <code>j</code> at the end of <code>b</code>. Look at the sum <code>a[i] + b[j]</code>. If it is below the target, which of the two pointers is it pointless to keep using with the current partner?",
           "Record <code>|sum - target|</code> every step. If the sum is smaller than the target move <code>i</code> right; if larger move <code>j</code> left; if equal the answer is 0."],
    editorial=["Imagine the table of all sums with row <code>i</code> and column <code>j</code>; it is sorted along every row and column. Start in the corner <code>(0, m-1)</code>. If <code>a[i] + b[j] &lt; target</code>, then every other sum in row <code>i</code> to the left of this one is even smaller, so they are all farther from the target than this one on the same side: row <code>i</code> is finished and <code>i</code> moves right. If the sum exceeds the target, the same argument shows that column <code>j</code> is finished (everything below it is larger), so <code>j</code> moves left.",
               "At each visited cell record the distance to the target and keep the minimum. The pointers sweep monotonically, so there are at most n + m steps: O(n + m) time and O(1) space. Bounds on the values keep <code>|s - target|</code> within 2&middot;10<sup>9</sup>, inside 32 bits."],
    time="O(n + m)", space="O(1)",
    solution='''def closestPairSum(a, b, target):
    i, j = 0, len(b) - 1
    best = None
    while i < len(a) and j >= 0:
        s = a[i] + b[j]
        d = abs(s - target)
        if best is None or d < best:
            best = d
        if s < target:
            i += 1
        elif s > target:
            j -= 1
        else:
            return 0
    return best
''',
    tests=[[[-3, 4, 10, 20], [1, 6, 15], 17], [[5], [5], 10], [[5], [5], 0], [[5], [5], 7], [[1, 2, 3], [4, 5, 6], 100],
           [[1, 2, 3], [4, 5, 6], -100], [[-5, 0, 5], [-5, 0, 5], 3], [[1, 1, 1], [2, 2], 3], [[-5 * 10 ** 8], [-5 * 10 ** 8], 10 ** 9],
           [[5 * 10 ** 8], [5 * 10 ** 8], -10 ** 9], [[0, 10, 20, 30], [3, 13, 23], 22]],
)
_r = rnd(4009)
p["tests"].append([sorted_rand(_r, 1500, -5 * 10 ** 8, 5 * 10 ** 8), sorted_rand(_r, 1500, -5 * 10 ** 8, 5 * 10 ** 8), 123456789])
p["tests"].append([sorted_rand(_r, 2500, 0, 10 ** 6), sorted_rand(_r, 2000, 0, 10 ** 6), 1000001])
p["tests"].append([[3 * i for i in range(3000)], [3 * i + 1 for i in range(3000)], 7001])


def b_closest(a, b, target):
    return min(abs(x + y - target) for x in a for y in b)


def g_closest(r):
    return [sorted(gen_arr(r, -9, 9, 1, 8)), sorted(gen_arr(r, -9, 9, 1, 8)), r.randint(-25, 25)]


def v_closest(tests):
    for t in tests:
        a, b, target = t["args"]
        assert 1 <= len(a) <= 5000 and 1 <= len(b) <= 5000
        assert a == sorted(a) and b == sorted(b)
        assert all(-5 * 10 ** 8 <= x <= 5 * 10 ** 8 for x in a + b)
        assert -10 ** 9 <= target <= 10 ** 9


CHECKS["closest-sum-across-two-sorted-arrays"] = (b_closest, g_closest, "exact")
VALIDATE["closest-sum-across-two-sorted-arrays"] = v_closest

# ---------------------------------------------------------------- HARD

p = add(
    id="doubled-median-of-three-sorted-arrays", title="Median of Three Sorted Arrays", diff="Hard", topic=TOPIC, tier="extra",
    fn="doubledMedianOfThree", params=[("a", "int[]"), ("b", "int[]"), ("c", "int[]")], ret="int", cmp="exact",
    desc="<p>Three integer arrays <code>a</code>, <code>b</code> and <code>c</code> are each sorted in non-decreasing order; some of them may be empty but at least one element exists overall. Imagine merging all of them into one sorted array <code>m</code> of length <code>n</code>.</p><p>The median of <code>m</code> is <code>m[n / 2]</code> when <code>n</code> is odd, and the average of <code>m[n / 2 - 1]</code> and <code>m[n / 2]</code> when <code>n</code> is even. To avoid fractions, return <strong>twice the median</strong>, which equals <code>m[(n - 1) / 2] + m[n / 2]</code> using integer division.</p><pre>a = [1, 4, 9]\nb = [2, 3]\nc = [5, 6, 7, 8]\nmerged = [1, 2, 3, 4, 5, 6, 7, 8, 9]  (n = 9)\nresult = 2 * 5 = 10</pre><p>Merging the arrays costs O(n) time. Aim for something that does not look at every element, such as a time that is logarithmic in the size of the arrays and in the value range.</p>",
    constraints=["0 &le; a.length, b.length, c.length &le; 5,000 and a.length + b.length + c.length &ge; 1", "-10<sup>9</sup> &le; a[i], b[i], c[i] &le; 10<sup>9</sup>", "Each array is sorted in non-decreasing order"],
    hints=["First reduce the task: you need the elements at two positions of the merged order, <code>(n-1)/2</code> and <code>n/2</code>. How can you find the element at a given position of the merged order without merging?",
           "Binary search on the <em>value</em>: for a candidate value <code>v</code>, the number of elements <code>&le; v</code> across all arrays is computable with one binary search per array.",
           "The element at 0-based position <code>k</code> of the merged order is the smallest <code>v</code> in [-10<sup>9</sup>, 10<sup>9</sup>] such that at least <code>k + 1</code> elements are <code>&le; v</code>. Run this search for <code>k = (n-1)/2</code> and <code>k = n/2</code> and add the two answers."],
    editorial=["Let <code>count(v)</code> be the number of elements that are at most <code>v</code>; since every array is sorted it is the sum of three <code>bisect_right</code> calls, each O(log n). The merged element at 0-based position <code>k</code> is the smallest value <code>v</code> with <code>count(v) &ge; k + 1</code>: below it fewer than <code>k + 1</code> elements fit, and at it the <code>(k+1)</code>-th smallest is covered. <code>count</code> is monotone in <code>v</code>, so a binary search over the value range [-10<sup>9</sup>, 10<sup>9</sup>] finds it in about 31 iterations.",
               "The answer needs the elements at positions <code>(n-1)/2</code> and <code>n/2</code> (the same position for odd n, the two middle ones for even n); their sum is twice the median and lies within [-2&middot;10<sup>9</sup>, 2&middot;10<sup>9</sup>], which fits in 32 bits. Total time is O(log V &middot; log n) where V is the value range, and O(1) space. A partition-based search (the classic O(log n) approach for two arrays) generalizes to three arrays, but is considerably harder to get right than this counting search."],
    time="O(log V * log n)", space="O(1)",
    solution='''from bisect import bisect_right


def doubledMedianOfThree(a, b, c):
    n = len(a) + len(b) + len(c)

    def kth(k):
        lo, hi = -10 ** 9, 10 ** 9
        while lo < hi:
            mid = (lo + hi) // 2
            if bisect_right(a, mid) + bisect_right(b, mid) + bisect_right(c, mid) >= k + 1:
                hi = mid
            else:
                lo = mid + 1
        return lo

    return kth((n - 1) // 2) + kth(n // 2)
''',
    tests=[[[1, 4, 9], [2, 3], [5, 6, 7, 8]], [[5], [], []], [[], [], [-7]], [[1], [2], []], [[1, 2], [3, 4], [5, 6]],
           [[2, 2, 2], [2, 2], [2]], [[-10 ** 9], [10 ** 9], [10 ** 9]], [[-10 ** 9], [-10 ** 9], [10 ** 9]], [[], [1, 3], [2, 4]],
           [[10, 20, 30, 40], [], [15, 25]], [[-5, -4, -3], [-2, -1], [0, 1, 2, 3]]],
)
_r = rnd(4010)
p["tests"].append([sorted_rand(_r, 800, -10 ** 9, 10 ** 9), sorted_rand(_r, 800, -10 ** 9, 10 ** 9), sorted_rand(_r, 800, -10 ** 9, 10 ** 9)])
p["tests"].append([sorted_rand(_r, 2000, -50000, 50000), sorted_rand(_r, 600, -50000, 50000), sorted_rand(_r, 1200, -50000, 50000)])
p["tests"].append([sorted_rand(_r, 1000, -10 ** 9, -10 ** 8), [], sorted_rand(_r, 1001, 10 ** 8, 10 ** 9)])
p["tests"].append([[i for i in range(0, 4500, 3)], [i for i in range(1, 4500, 3)], [i for i in range(2, 4500, 3)]])


def b_median3(a, b, c):
    m = sorted(a + b + c)
    n = len(m)
    return m[(n - 1) // 2] + m[n // 2]


def g_median3(r):
    while True:
        arrs = [sorted(gen_arr(r, -9, 9, 0, 7)) for _ in range(3)]
        if sum(map(len, arrs)) > 0:
            return arrs


def v_median3(tests):
    for t in tests:
        arrs = t["args"]
        assert sum(map(len, arrs)) >= 1
        for arr in arrs:
            assert len(arr) <= 5000 and arr == sorted(arr)
            assert all(-10 ** 9 <= x <= 10 ** 9 for x in arr)


CHECKS["doubled-median-of-three-sorted-arrays"] = (b_median3, g_median3, "exact")
VALIDATE["doubled-median-of-three-sorted-arrays"] = v_median3

p = add(
    id="smallest-range-covering-k-sorted-lists", title="Smallest Range Covering Elements from K Lists", diff="Hard", topic=TOPIC,
    fn="smallestRange", params=[("lists", "int[][]")], ret="int[]", cmp="exact",
    desc="<p>You are given <code>k</code> non-empty lists of integers, each sorted in non-decreasing order. Find the smallest closed range <code>[lo, hi]</code> that contains at least one element from every list.</p><p>Range <code>[p, q]</code> is smaller than range <code>[r, s]</code> if <code>q - p &lt; s - r</code>, or if <code>q - p == s - r</code> and <code>p &lt; r</code>. Return the answer as the two-element array <code>[lo, hi]</code>.</p><pre>lists = [[4, 10, 15, 24, 26], [0, 9, 12, 20], [5, 18, 22, 30]]\nresult = [20, 24]</pre><p>The range <code>[20, 24]</code> contains 24 from the first list, 20 from the second and 22 from the third, and no range of length 4 or less does better.</p>",
    constraints=["1 &le; k &le; 3,000", "1 &le; each list length, and the total number of elements is at most 6,000", "-10<sup>5</sup> &le; value &le; 10<sup>5</sup>", "Each list is sorted in non-decreasing order"],
    hints=["Try to think of all the elements pooled into one array, with each element remembering which list it came from. A candidate range then becomes a window of that array.",
           "Sort the pooled elements by value. You are looking for the shortest window (in value span) that contains at least one element of each of the k lists, like the minimum window substring problem.",
           "Expand the right edge of the window one element at a time while counting how many distinct lists are present. Whenever all k lists are present, record <code>[value at left, value at right]</code> if it beats the best (smaller span, then smaller lo), then shrink from the left while keeping all lists covered."],
    editorial=["Label every element with its list index and sort the pairs <code>(value, list)</code>; a range <code>[lo, hi]</code> corresponds to a contiguous window of this sorted array. The question becomes: what is the window with the smallest value span that includes every list label at least once? This is the same sliding-window technique as the smallest substring that contains all required characters.",
               "Move the right edge forward, maintaining <code>count[list]</code> and the number of lists with a non-zero count. While that number equals k, compare the span of the current window against the best (smaller span wins, ties go to the smaller <code>lo</code>), then drop the left element and update the counts. Both edges move only forward, so after sorting the sweep is linear. Total time is O(N log N) for N elements; a heap holding one element of each list gives O(N log k) without sorting everything up front, and works the same way (always advance the list whose current element is the smallest)."],
    time="O(N log N)", space="O(N)",
    solution='''def smallestRange(lists):
    k = len(lists)
    items = sorted((v, i) for i, lst in enumerate(lists) for v in lst)
    count = [0] * k
    covered = 0
    best = None
    left = 0
    for right in range(len(items)):
        li = items[right][1]
        if count[li] == 0:
            covered += 1
        count[li] += 1
        while covered == k:
            lo, hi = items[left][0], items[right][0]
            if best is None or (hi - lo, lo) < (best[1] - best[0], best[0]):
                best = [lo, hi]
            lj = items[left][1]
            count[lj] -= 1
            if count[lj] == 0:
                covered -= 1
            left += 1
    return best
''',
    tests=[[[[4, 10, 15, 24, 26], [0, 9, 12, 20], [5, 18, 22, 30]]], [[[1, 2, 3], [1, 2, 3], [1, 2, 3]]], [[[7]]], [[[1], [2], [3]]],
           [[[-5, 0, 5]]], [[[1, 5, 9], [2]]], [[[1, 1, 1], [1, 1]]], [[[10, 10], [11, 11]]], [[[0, 100000], [-100000, 0]]],
           [[[-100000], [100000]]], [[[1, 4, 8], [2, 5, 9], [3, 6, 7]]], [[[3, 3, 9], [0, 6, 6], [4, 4, 9]]]],
)
_r = rnd(4011)
p["tests"].append([[sorted_rand(_r, 6, -100000, 100000) for _ in range(600)]])
p["tests"].append([[sorted_rand(_r, _r.randint(1, 3), -100000, 100000) for _ in range(1500)]])
p["tests"].append([[sorted_rand(_r, 1200, -100000, 100000), sorted_rand(_r, 600, -100000, 100000), sorted_rand(_r, 1800, -100000, 100000)]])


def b_range(lists):
    vals = sorted({v for lst in lists for v in lst})
    best = None
    for lo in vals:
        for hi in vals:
            if hi < lo:
                continue
            if all(any(lo <= v <= hi for v in lst) for lst in lists):
                cand = (hi - lo, lo)
                if best is None or cand < best:
                    best = cand
    return [best[1], best[1] + best[0]]


def g_range(r):
    return [[sorted(gen_arr(r, -8, 8, 1, 4)) for _ in range(r.randint(1, 4))]]


def v_range(tests):
    for t in tests:
        lists = t["args"][0]
        assert 1 <= len(lists) <= 3000
        assert sum(len(x) for x in lists) <= 6000
        for lst in lists:
            assert len(lst) >= 1 and lst == sorted(lst)
            assert all(-10 ** 5 <= v <= 10 ** 5 for v in lst)


CHECKS["smallest-range-covering-k-sorted-lists"] = (b_range, g_range, "exact")
VALIDATE["smallest-range-covering-k-sorted-lists"] = v_range
