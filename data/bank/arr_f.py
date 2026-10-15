"""Problems: arrays used as pointers (index -> value), cycles and in-place marking."""
from collections import Counter, deque
from itertools import permutations

from lib import add, rnd, CHECKS, VALIDATE, gen_arr  # noqa: F401

T = "Arrays & Hashing"


def _is_perm(a):
    return sorted(a) == list(range(len(a)))


# ------------------------------------------------------------------ find duplicate (no modification)

def _dup_array(r, n, c):
    """length n+1, values in 1..n, exactly one value (random) occurring c >= 2 times."""
    d = r.randint(1, n)
    others = [v for v in range(1, n + 1) if v != d]
    r.shuffle(others)
    a = [d] * c + others[:n + 1 - c]
    r.shuffle(a)
    return a


p = add(
    id="find-the-duplicate-number", title="Find the Duplicate Number", diff="Medium", topic=T, tier="must",
    fn="findDuplicate", params=[("nums", "int[]")], ret="int", cmp="exact",
    desc="<p>The array <code>nums</code> has <code>n + 1</code> elements and every element lies in the range <code>1..n</code>. Exactly one value occurs more than once (it may occur two times or many more times); every other value occurs at most once. Return the repeated value.</p>"
         "<p>Do not modify <code>nums</code>, and use only O(1) extra space.</p>"
         "<p>Example: <code>nums = [1, 3, 4, 2, 2]</code> returns <code>2</code>.</p>",
    constraints=["1 &le; n &le; 8,000, so nums.length = n + 1", "1 &le; nums[i] &le; n", "Exactly one value occurs at least twice; all other values occur at most once"],
    hints=["A set or a count map finds the repeat, and sorting does too, but both break one of the rules (extra memory or modifying the array). Look for a different way to view the array.",
           "Treat index <code>i</code> as a node with one outgoing edge to <code>nums[i]</code>. Every value is at least 1, so index 0 is never the target of an edge. Two different indices pointing to the same node means a node with two incoming edges.",
           "Start at index 0 and keep jumping <code>i = nums[i]</code>. The walk must end up in a cycle, and the entrance of that cycle is the repeated value. Find the meeting point with a slow and a fast pointer, then restart one pointer from 0 and move both one step at a time until they meet."],
    editorial=["Build the functional graph <code>i -> nums[i]</code>. It has n + 1 nodes (0..n) and every edge goes to a node in 1..n, so the walk from node 0 can never return to 0 and must eventually loop. Node 0 has no incoming edge; the cycle entrance is the first node on the cycle, and it is reached once from the tail and once from the cycle, i.e. it has two incoming edges, meaning two indices hold the same value. Two incoming edges to one node is exactly a repeated value, and since only one value repeats, the cycle entrance is the answer.",
               "Floyd's cycle detection finds the entrance in O(1) space. Phase one: move <code>slow</code> one step and <code>fast</code> two steps from index 0 until they meet inside the cycle. Phase two: put <code>slow</code> back on 0 and advance both one step at a time; if the tail has length a and the meeting point is a steps before the entrance when measured around the cycle, they meet exactly at the entrance.",
               "Alternatives: a hash set is O(n) space, sorting modifies the array, and binary search on the value range (count how many elements are &le; mid) is O(n log n) time and O(1) space without modifying the input."],
    time="O(n)", space="O(1)",
    solution='''def findDuplicate(nums):
    slow = fast = 0
    while True:
        slow = nums[slow]
        fast = nums[nums[fast]]
        if slow == fast:
            break
    slow = 0
    while slow != fast:
        slow = nums[slow]
        fast = nums[fast]
    return slow
''',
    tests=[[[1, 3, 4, 2, 2]], [[3, 1, 3, 4, 2]], [[1, 1]], [[2, 2, 2]], [[3, 3, 3, 3, 3]], [[1, 2, 1]], [[2, 1, 2]],
           [[4, 3, 1, 2, 4, 5]], [[6, 5, 4, 3, 2, 1, 6]], [[2, 5, 9, 6, 9, 3, 8, 9, 7, 1]]],
)
_r = rnd(7001)
p["tests"].append([_dup_array(_r, 4000, 2)])
p["tests"].append([_dup_array(_r, 6000, 3)])
p["tests"].append([_dup_array(_r, 4000, 2000)])


def b_dup(nums):
    c = Counter(nums)
    return [v for v in c if c[v] > 1][0]


def g_dup(r):
    n = r.randint(1, 8)
    return _dup_array(r, n, r.randint(2, n + 1))


def v_dup(tests):
    for t in tests:
        a = t["args"][0]
        n = len(a) - 1
        assert 1 <= n <= 8000 and all(1 <= x <= n for x in a)
        c = Counter(a)
        assert sum(1 for v in c.values() if v > 1) == 1


CHECKS["find-the-duplicate-number"] = (b_dup, lambda r: [g_dup(r)], "exact")
VALIDATE["find-the-duplicate-number"] = v_dup


# ------------------------------------------------------------------ all duplicates, values 1..n, in place

p = add(
    id="find-all-values-appearing-twice", title="Find All Values Appearing Twice", diff="Medium", topic=T, tier="common",
    fn="findTwice", params=[("nums", "int[]")], ret="int[]", cmp="exact",
    desc="<p>The array <code>nums</code> has length <code>n</code> and every element lies in the range <code>1..n</code>. Each value occurs either once or twice. Return all values that occur twice, in ascending order (an empty array if there are none).</p>"
         "<p>Aim for O(n) time and no extra data structure beyond the output (you may use the input array itself as scratch space).</p>"
         "<p>Example: <code>nums = [4, 3, 2, 7, 8, 2, 3, 1]</code> returns <code>[2, 3]</code>.</p>",
    constraints=["1 &le; n &le; 10,000", "1 &le; nums[i] &le; n", "Each value occurs at most twice"],
    hints=["A count map is the obvious tool. To save the memory, ask where you could store one bit of information per value 1..n.",
           "Value <code>v</code> can be associated with index <code>v - 1</code>. Because all values are positive, the sign of <code>nums[v - 1]</code> is a free bit.",
           "For each element take <code>v = abs(x)</code>. If <code>nums[v - 1]</code> is already negative, you have seen <code>v</code> before, so it is a repeat; otherwise negate it. Sort the collected repeats at the end."],
    editorial=["Because the values are exactly the valid indices shifted by one, the array can double as a visited table. Walk through the array; for every element look at <code>v = abs(nums[i])</code>. If <code>nums[v - 1]</code> is positive, flip it to negative to record that v has been seen. If it is already negative, v was seen earlier, so v is a repeated value.",
               "Reading the absolute value is important because earlier steps may already have negated the current element. Each value occurs at most twice, so each repeat is reported exactly once. The repeats are discovered in an arbitrary order, so sort them at the end, which costs O(k log k) for k repeats (k is at most n/2).",
               "A hash set is simpler and equally O(n) in time but uses O(n) extra space."],
    time="O(n + k log k) for k repeats", space="O(1) extra (besides the output)",
    solution='''def findTwice(nums):
    nums = list(nums)
    out = []
    for x in nums:
        v = abs(x)
        if nums[v - 1] < 0:
            out.append(v)
        else:
            nums[v - 1] = -nums[v - 1]
    out.sort()
    return out
''',
    tests=[[[4, 3, 2, 7, 8, 2, 3, 1]], [[1, 1, 2]], [[1]], [[1, 2, 3, 4]], [[2, 2]], [[1, 1]], [[3, 3, 1, 1, 2, 4]],
           [[2, 1, 2, 1]], [[5, 4, 6, 7, 9, 3, 10, 9, 5, 6]], [[1, 2, 3, 1, 2, 3]]],
)


def _twice(r, n, k):
    perm = list(range(1, n + 1))
    r.shuffle(perm)
    drop = perm[:k]
    keep = perm[k:]
    dup = r.sample(keep, k)
    a = perm[:]
    for i in range(k):
        a[i] = dup[i]
    r.shuffle(a)
    return a


_r = rnd(7002)
p["tests"].append([_twice(_r, 4000, 1500)])
p["tests"].append([_twice(_r, 5000, 2200)])
p["tests"].append([list(range(3000, 0, -1))])
p["tests"].append([_twice(_r, 3000, 0)])


def b_twice(nums):
    c = Counter(nums)
    return sorted(v for v in c if c[v] == 2)


def g_twice(r):
    n = r.randint(1, 9)
    return _twice(r, n, r.randint(0, n // 2))


def v_twice(tests):
    for t in tests:
        a = t["args"][0]
        n = len(a)
        assert 1 <= n <= 10000 and all(1 <= x <= n for x in a)
        assert max(Counter(a).values()) <= 2
        assert t["expected"] == sorted(t["expected"])


CHECKS["find-all-values-appearing-twice"] = (b_twice, lambda r: [g_twice(r)], "exact")
VALIDATE["find-all-values-appearing-twice"] = v_twice

# ------------------------------------------------------------------ disappeared numbers

p = add(
    id="find-all-numbers-disappeared", title="Find All Numbers Disappeared", diff="Easy", topic=T, tier="common",
    fn="findDisappeared", params=[("nums", "int[]")], ret="int[]", cmp="exact",
    desc="<p>The array <code>nums</code> has length <code>n</code> and every element lies in the range <code>1..n</code>. Values may repeat any number of times, so some numbers of <code>1..n</code> may not appear at all. Return all numbers in <code>1..n</code> that do not appear in <code>nums</code>, in ascending order (an empty array if every number appears).</p>"
         "<p>Example: <code>nums = [4, 3, 2, 7, 8, 2, 3, 1]</code> returns <code>[5, 6]</code>.</p>",
    constraints=["1 &le; n &le; 10,000", "1 &le; nums[i] &le; n"],
    hints=["A set of the values, compared with 1..n, gives the answer. Can you keep the bookkeeping inside <code>nums</code>?",
           "Because every value is a valid position (shifted by one), you can use position <code>v - 1</code> to say \"v is present\", for example by making that entry negative.",
           "After marking all values, every position that is still positive corresponds to a number that never occurred: position <code>i</code> stands for the number <code>i + 1</code>."],
    editorial=["Use the array as its own presence table. For every element take <code>v = abs(x)</code> and force <code>nums[v - 1]</code> to be negative (using <code>-abs(...)</code> so that repeated values do not flip it back). When the pass is finished, an index whose entry is still positive was never pointed to, so the number <code>i + 1</code> is missing.",
               "The scan runs in O(n) time with O(1) extra space apart from the output. The result is produced in ascending order automatically because we read the indices left to right. A hash-set solution is equally fast but needs O(n) memory."],
    time="O(n)", space="O(1) extra (besides the output)",
    solution='''def findDisappeared(nums):
    nums = list(nums)
    for x in nums:
        v = abs(x)
        nums[v - 1] = -abs(nums[v - 1])
    return [i + 1 for i, x in enumerate(nums) if x > 0]
''',
    tests=[[[4, 3, 2, 7, 8, 2, 3, 1]], [[1, 1]], [[1]], [[2, 2]], [[1, 2, 3]], [[3, 3, 3]], [[1, 2, 2, 4, 4, 4]],
           [[5, 5, 5, 5, 5]], [[2, 3, 4, 5, 1]], [[1, 1, 1, 1, 1, 1, 1]]],
)
_r = rnd(7003)
p["tests"].append([[_r.randint(1, 3500) for _ in range(3500)]])
p["tests"].append([[_r.randint(1, 100) for _ in range(5000)]])
p["tests"].append([[5000] * 5000])


def b_disap(nums):
    s = set(nums)
    return [v for v in range(1, len(nums) + 1) if v not in s]


def g_disap(r):
    n = r.randint(1, 9)
    return [r.randint(1, n) for _ in range(n)]


def v_disap(tests):
    for t in tests:
        a = t["args"][0]
        n = len(a)
        assert 1 <= n <= 10000 and all(1 <= x <= n for x in a)


CHECKS["find-all-numbers-disappeared"] = (b_disap, lambda r: [g_disap(r)], "exact")
VALIDATE["find-all-numbers-disappeared"] = v_disap

# ------------------------------------------------------------------ permutation cycles


def _rand_perm(r, n):
    a = list(range(n))
    r.shuffle(a)
    return a


def _single_cycle(r, n):
    order = list(range(n))
    r.shuffle(order)
    a = [0] * n
    for i in range(n):
        a[order[i]] = order[(i + 1) % n]
    return a


p = add(
    id="count-cycles-in-a-permutation", title="Count Cycles in a Permutation", diff="Easy", topic=T, tier="common",
    fn="countCycles", params=[("perm", "int[]")], ret="int", cmp="exact",
    desc="<p><code>perm</code> is a permutation of the integers <code>0..n-1</code>. Think of it as a set of arrows: index <code>i</code> points to index <code>perm[i]</code>. Following the arrows from any index eventually brings you back to where you started; the indices visited on the way form a <em>cycle</em>. Every index belongs to exactly one cycle.</p>"
         "<p>Return the number of cycles. An index with <code>perm[i] = i</code> is a cycle of length 1.</p>"
         "<p>Example: <code>perm = [1, 0, 2, 4, 3, 5]</code> has the cycles <code>{0, 1}</code>, <code>{2}</code>, <code>{3, 4}</code>, <code>{5}</code>, so the answer is <code>4</code>.</p>",
    constraints=["1 &le; n &le; 10,000", "perm is a permutation of 0..n-1 (each value exactly once)"],
    hints=["Start from an index, follow the arrows until you come back, and count that as one cycle. How do you avoid counting the same cycle again from another of its members?",
           "Keep a <code>visited</code> flag for each index. Only start a new walk from an index that has not been visited yet.",
           "Loop over all indices; whenever an index is unvisited, increase the answer and walk its whole cycle, marking every index as visited."],
    editorial=["Because <code>perm</code> is a permutation, every index has exactly one arrow leaving it and exactly one arrow entering it, so the arrows split the indices into disjoint cycles (no tails). Scan the indices from left to right. If an index is not yet visited, it begins a new cycle: count it and follow the arrows, marking each index visited, until you return to the start.",
               "Each index is marked once, so the total work is O(n) and the visited array needs O(n) bits. (The array itself can be used for marking by overwriting visited entries with -1, giving O(1) extra space.)"],
    time="O(n)", space="O(n)",
    solution='''def countCycles(perm):
    n = len(perm)
    seen = [False] * n
    cycles = 0
    for i in range(n):
        if not seen[i]:
            cycles += 1
            j = i
            while not seen[j]:
                seen[j] = True
                j = perm[j]
    return cycles
''',
    tests=[[[1, 0, 2, 4, 3, 5]], [[0]], [[1, 0]], [[0, 1, 2]], [[1, 2, 0]], [[2, 0, 1, 3]], [[4, 3, 2, 1, 0]],
           [[1, 2, 3, 4, 0]], [[3, 4, 0, 1, 2]], [[5, 4, 3, 2, 1, 0]]],
)
_r = rnd(7004)
p["tests"].append([_rand_perm(_r, 5000)])
p["tests"].append([list(range(5000))])
p["tests"].append([_single_cycle(_r, 5000)])


def b_cycles(perm):
    n = len(perm)
    reps = set()
    for i in range(n):
        orbit = [i]
        j = perm[i]
        while j != i:
            orbit.append(j)
            j = perm[j]
        reps.add(min(orbit))
    return len(reps)


def g_cycles(r):
    return _rand_perm(r, r.randint(1, 9))


def v_perm(tests):
    for t in tests:
        a = t["args"][0]
        assert 1 <= len(a) <= 10000 and _is_perm(a)


CHECKS["count-cycles-in-a-permutation"] = (b_cycles, lambda r: [g_cycles(r)], "exact")
VALIDATE["count-cycles-in-a-permutation"] = v_perm

# ------------------------------------------------------------------ array nesting

p = add(
    id="longest-array-nesting-chain", title="Longest Array Nesting Chain", diff="Medium", topic=T, tier="common",
    fn="longestNesting", params=[("nums", "int[]")], ret="int", cmp="exact",
    desc="<p><code>nums</code> is a permutation of <code>0..n-1</code>. For a starting index <code>k</code> build a list as follows: put <code>nums[k]</code> in it, then <code>nums[nums[k]]</code>, then <code>nums[nums[nums[k]]]</code>, and so on, stopping just before an element would be added that is already in the list.</p>"
         "<p>Return the largest list length over all starting indices <code>k</code>.</p>"
         "<p>Example: <code>nums = [5, 4, 0, 3, 1, 6, 2]</code>. Starting at <code>k = 0</code> gives <code>5, 6, 2, 0</code> and then 5 would repeat, so the length is 4. The answer is <code>4</code>.</p>",
    constraints=["1 &le; n &le; 10,000", "nums is a permutation of 0..n-1"],
    hints=["Simulating every starting index independently with a set can take O(n<sup>2</sup>) time in total. Look for work that is shared between starts.",
           "In a permutation the list you build from <code>k</code> is the cycle that contains <code>k</code>. Starting from any member of that cycle gives the same length.",
           "Mark indices as visited while walking. Start a new walk only from unvisited indices, and keep the maximum number of steps of a walk."],
    editorial=["The arrows <code>i -> nums[i]</code> form disjoint cycles because <code>nums</code> is a permutation. The list built from index <code>k</code> contains exactly the members of the cycle through <code>k</code>, so the answer is the length of the longest cycle.",
               "Scan the indices; for every index that has not been visited, walk along its cycle, marking each index and counting the steps until you meet a visited index (which will be the start of the walk). Remember the biggest count. Every index is visited once, so the time is O(n); marking can be done in place by overwriting entries, which gives O(1) extra space."],
    time="O(n)", space="O(1)",
    solution='''def longestNesting(nums):
    nums = list(nums)
    best = 0
    for i in range(len(nums)):
        if nums[i] >= 0:
            length = 0
            j = i
            while nums[j] >= 0:
                nxt = nums[j]
                nums[j] = -1
                j = nxt
                length += 1
            best = max(best, length)
    return best
''',
    tests=[[[5, 4, 0, 3, 1, 6, 2]], [[0]], [[1, 0]], [[0, 1, 2, 3]], [[1, 2, 3, 0]], [[1, 0, 3, 2, 4]], [[2, 0, 1, 4, 3]],
           [[0, 2, 1, 4, 5, 3, 6]], [[3, 2, 1, 0, 5, 4]], [[1, 2, 0, 4, 5, 6, 3, 7]]],
)
_r = rnd(7005)
p["tests"].append([_rand_perm(_r, 5000)])
p["tests"].append([_single_cycle(_r, 5000)])
p["tests"].append([[(i + 1) if i % 2 == 0 else (i - 1) for i in range(4000)]])


def b_nest(nums):
    best = 0
    for k in range(len(nums)):
        seen = []
        j = nums[k]
        while j not in seen:
            seen.append(j)
            j = nums[j]
        best = max(best, len(seen))
    return best


CHECKS["longest-array-nesting-chain"] = (b_nest, lambda r: [_rand_perm(r, r.randint(1, 9))], "exact")
VALIDATE["longest-array-nesting-chain"] = v_perm

# ------------------------------------------------------------------ circular array loop

p = add(
    id="circular-array-same-direction-loop", title="Circular Array Same-Direction Loop", diff="Hard", topic=T, tier="extra",
    fn="hasCircularLoop", params=[("nums", "int[]")], ret="bool", cmp="exact",
    desc="<p>The non-zero integers <code>nums[0..n-1]</code> are written around a circle, so index <code>n-1</code> is followed by index <code>0</code>. At index <code>i</code> you jump <code>nums[i]</code> places: forward if it is positive, backward if it is negative, wrapping around the circle. Let <code>next(i) = (i + nums[i]) mod n</code>, using a non-negative remainder.</p>"
         "<p>A <em>loop</em> is a sequence of distinct indices <code>i<sub>0</sub>, i<sub>1</sub>, ..., i<sub>m-1</sub></code> with <code>m &ge; 2</code> such that <code>next(i<sub>j</sub>) = i<sub>j+1</sub></code> and <code>next(i<sub>m-1</sub>) = i<sub>0</sub></code>, and where <em>all</em> of <code>nums[i<sub>0</sub>], ..., nums[i<sub>m-1</sub>]</code> have the same sign (all positive or all negative). A jump that lands on its own index forms no loop.</p>"
         "<p>Return <code>true</code> if <code>nums</code> contains a loop, otherwise <code>false</code>.</p>"
         "<p>Example: <code>[2, -1, 1, 2, 2]</code> returns <code>true</code>: indices 0 &rarr; 2 &rarr; 3 &rarr; 0 are all positive. For <code>[-1, 2]</code> index 0 jumps to 1, index 1 jumps to 1 itself, so the answer is <code>false</code>.</p>",
    constraints=["1 &le; n &le; 5,000", "-5,000 &le; nums[i] &le; 5,000 and nums[i] &ne; 0"],
    hints=["Each index has exactly one outgoing jump, so from any index the walk either loops forever or hits an index you have used before. You are looking for a cycle with two extra rules: length at least 2, and one direction only.",
           "A cycle that only uses one direction never crosses a sign change. So drop every jump that goes to an index of the opposite sign, and drop jumps from an index to itself; then any cycle that remains is a valid loop.",
           "Detect a cycle in this graph where every node has at most one outgoing edge: walk from each unvisited index, marking indices with the id of the current walk. If you step onto an index marked with the same walk id, you found a cycle. If you step onto an older mark, or onto a dropped edge, stop. Each index is walked at most once."],
    editorial=["Every index has exactly one successor, a functional graph. Any cycle of it with all jumps of one sign is a loop, apart from cycles of length 1 (a self-jump, when <code>nums[i]</code> is a multiple of n). So define a restricted successor: <code>nxt(i) = next(i)</code> if <code>next(i) != i</code> and <code>nums[next(i)]</code> has the same sign as <code>nums[i]</code>; otherwise there is no edge. A cycle in a restricted graph consists of same-sign indices only (the sign cannot change along an edge) and has length at least 2, so the answer is whether the restricted graph has a cycle.",
               "Detect it with one pass of colouring. For every start index with no mark, walk along the restricted edges and tag each index with the id of this walk. When the next index carries the current id, a cycle has been closed: return true. When it carries an older id (it is already known to lead to a dead end or a cycle that was reported earlier) or there is no edge, the walk ends. Because each index is tagged once, the whole scan is O(n) time and O(n) space. The classic O(1)-space version runs Floyd's slow/fast pointers from every index and zeroes the entries of failed walks.",
               "The tricky parts are the self-jump (a cycle of length 1 that is not allowed) and the direction check, which has to be done on every step, not only at the start."],
    time="O(n)", space="O(n)",
    solution='''def hasCircularLoop(nums):
    n = len(nums)
    nxt = [-1] * n
    for i in range(n):
        j = (i + nums[i]) % n
        if j != i and (nums[j] > 0) == (nums[i] > 0):
            nxt[i] = j
    mark = [0] * n
    for s in range(n):
        if mark[s]:
            continue
        walk = s + 1
        i = s
        while i != -1 and mark[i] == 0:
            mark[i] = walk
            i = nxt[i]
        if i != -1 and mark[i] == walk:
            return True
    return False
''',
    tests=[[[2, -1, 1, 2, 2]], [[-1, 2]], [[-2, 1, -1, -2, -2]], [[1]], [[1, 1]], [[1, -1]], [[2, 2]], [[3, 1, 2]],
           [[1, 1, 1, 1, 1, -1]], [[-1, -1, -1, 1, 1, 1, -1]]],
)
_r = rnd(7006)
_n = 5000
_a = [_n] * _n; _a[5] = 3; _a[8] = -3
p["tests"].append([_a])                                 # 5 -> 8 -> 5 but opposite signs
_a = [_n] * _n; _a[5] = 3; _a[8] = _n - 3
p["tests"].append([_a])                                 # same-sign 2-loop hidden in self jumps
p["tests"].append([[1 if i % 2 == 0 else -1 for i in range(4999)]])   # signs alternate: no loop
_a = [_r.choice([-1, 1]) * _r.randint(1, 5000) for _ in range(4000)]
p["tests"].append([_a])


def b_loop(nums):
    n = len(nums)
    nxt = [(i + nums[i]) % n for i in range(n)]
    for s in range(n):
        path = []
        i = s
        while i not in path:
            path.append(i)
            i = nxt[i]
        cyc = path[path.index(i):]
        if len(cyc) >= 2 and (all(nums[c] > 0 for c in cyc) or all(nums[c] < 0 for c in cyc)):
            return True
    return False


def g_loop(r):
    n = r.randint(1, 8)
    hi = r.choice([2, 3, 9])
    return [r.choice([-1, 1]) * r.randint(1, hi) for _ in range(n)]


def v_loop(tests):
    res = set()
    for t in tests:
        a = t["args"][0]
        assert 1 <= len(a) <= 5000 and all(x != 0 and -5000 <= x <= 5000 for x in a)
        res.add(t["expected"])
    assert res == {True, False}


CHECKS["circular-array-same-direction-loop"] = (b_loop, lambda r: [g_loop(r)], "exact")
VALIDATE["circular-array-same-direction-loop"] = v_loop

# ------------------------------------------------------------------ minimum swaps to sort

p = add(
    id="min-swaps-to-sort-distinct-array", title="Minimum Swaps to Sort a Distinct Array", diff="Medium", topic=T, tier="common",
    fn="minSwapsToSort", params=[("nums", "int[]")], ret="int", cmp="exact",
    desc="<p>The array <code>nums</code> contains distinct integers. In one move you may swap the elements at any two positions. Return the minimum number of moves needed to arrange <code>nums</code> in ascending order.</p>"
         "<p>Example: <code>nums = [4, 3, 1, 2]</code> returns <code>3</code>: swap positions 0 and 2 to get <code>[1, 3, 4, 2]</code>, positions 1 and 3 to get <code>[1, 2, 4, 3]</code>, and positions 2 and 3 to finish. Two swaps are not enough.</p>",
    constraints=["1 &le; nums.length &le; 10,000", "-10<sup>9</sup> &le; nums[i] &le; 10<sup>9</sup>", "All values are distinct"],
    hints=["Replace each value by its rank (its position in the sorted order). Now the array is a permutation of 0..n-1 and the target is the identity.",
           "Draw an arrow from position <code>i</code> to the position where <code>nums[i]</code> should go. These arrows split the positions into cycles. A cycle of length 1 is already in place.",
           "A cycle of length L can be fixed with L - 1 swaps and not with fewer. So the answer is n minus the number of cycles."],
    editorial=["Sort the indices by value to find the target position of each element. The map <code>i -> target(i)</code> is a permutation, so it breaks into disjoint cycles. Every swap changes the number of cycles by exactly one (it either merges two cycles or splits one), and the sorted arrangement has n cycles (all of length 1), so at least <code>n - cycles</code> swaps are needed. Conversely, a cycle of length L is resolved by L - 1 swaps that each put one element into its final position, so the bound is achieved.",
               "The work is a sort, O(n log n), followed by an O(n) cycle count. Because the values are distinct there is no ambiguity in the target positions; with duplicates the problem would be much harder."],
    time="O(n log n)", space="O(n)",
    solution='''def minSwapsToSort(nums):
    n = len(nums)
    order = sorted(range(n), key=lambda i: nums[i])
    seen = [False] * n
    swaps = 0
    for i in range(n):
        if not seen[i]:
            length = 0
            j = i
            while not seen[j]:
                seen[j] = True
                j = order[j]
                length += 1
            swaps += length - 1
    return swaps
''',
    tests=[[[4, 3, 1, 2]], [[1, 2, 3]], [[7]], [[2, 1]], [[3, 2, 1]], [[2, 3, 1]], [[10, 19, 6, 3, 5]], [[5, 4, 3, 2, 1]],
           [[-5, 8, 0, -9, 4]], [[1, 5, 4, 3, 2]]],
)
_r = rnd(7007)
p["tests"].append([_r.sample(range(-10 ** 9, 10 ** 9), 4000)])
p["tests"].append([list(range(4000, 0, -1))])
p["tests"].append([[(i + 1) % 4000 for i in range(4000)]])


def b_swaps(nums):
    start = tuple(nums)
    goal = tuple(sorted(nums))
    if start == goal:
        return 0
    dist = {start: 0}
    q = deque([start])
    n = len(nums)
    while q:
        cur = q.popleft()
        for i in range(n):
            for j in range(i + 1, n):
                lst = list(cur)
                lst[i], lst[j] = lst[j], lst[i]
                t = tuple(lst)
                if t not in dist:
                    dist[t] = dist[cur] + 1
                    if t == goal:
                        return dist[t]
                    q.append(t)


def g_swaps(r):
    return r.sample(range(-30, 30), r.randint(1, 6))


def v_swaps(tests):
    for t in tests:
        a = t["args"][0]
        assert 1 <= len(a) <= 10000 and len(set(a)) == len(a) and all(-10 ** 9 <= x <= 10 ** 9 for x in a)


CHECKS["min-swaps-to-sort-distinct-array"] = (b_swaps, lambda r: [g_swaps(r)], "exact")
VALIDATE["min-swaps-to-sort-distinct-array"] = v_swaps

# ------------------------------------------------------------------ permutation applied k times

p = add(
    id="apply-permutation-k-times", title="Apply a Permutation K Times", diff="Medium", topic=T, tier="extra",
    fn="applyPermutation", params=[("perm", "int[]"), ("k", "int")], ret="int[]", cmp="exact",
    desc="<p><code>perm</code> is a permutation of <code>0..n-1</code>. For an index <code>i</code>, define <code>f(i) = perm[i]</code>, and let <code>f<sup>k</sup>(i)</code> be the result of applying <code>f</code> to <code>i</code> exactly <code>k</code> times (<code>f<sup>0</sup>(i) = i</code>).</p>"
         "<p>Return the array <code>res</code> of length <code>n</code> with <code>res[i] = f<sup>k</sup>(i)</code>. Note that <code>k</code> can be as large as 10<sup>9</sup>, so simulating every step is too slow.</p>"
         "<p>Example: <code>perm = [1, 2, 0, 4, 3]</code>, <code>k = 2</code> returns <code>[2, 0, 1, 3, 4]</code>.</p>",
    constraints=["1 &le; n &le; 10,000", "perm is a permutation of 0..n-1", "0 &le; k &le; 10<sup>9</sup>"],
    hints=["Repeating the step k times for every index costs O(n &middot; k), far too slow when k is large.",
           "A permutation splits indices into cycles. Inside a cycle of length L, going k steps is the same as going k mod L steps.",
           "Walk each cycle once and store its indices in a list <code>cyc</code>. The element at list position <code>j</code> ends up at <code>cyc[(j + k) % L]</code>."],
    editorial=["Follow <code>i -> perm[i]</code> to extract every cycle as a list in walking order: <code>cyc[0], cyc[1] = perm[cyc[0]], ...</code>. After <code>k</code> applications, the index at position <code>j</code> of its cycle has moved to position <code>(j + k) mod L</code>, because completing a full loop of L steps changes nothing.",
               "So for each cycle set <code>res[cyc[j]] = cyc[(j + k) % L]</code>. Each index belongs to exactly one cycle, so the total work is O(n) regardless of k. Repeated squaring of the permutation also works (O(n log k)) but needs more code."],
    time="O(n)", space="O(n)",
    solution='''def applyPermutation(perm, k):
    n = len(perm)
    res = [0] * n
    seen = [False] * n
    for i in range(n):
        if not seen[i]:
            cyc = []
            j = i
            while not seen[j]:
                seen[j] = True
                cyc.append(j)
                j = perm[j]
            L = len(cyc)
            shift = k % L
            for pos, idx in enumerate(cyc):
                res[idx] = cyc[(pos + shift) % L]
    return res
''',
    tests=[[[1, 2, 0, 4, 3], 2], [[1, 2, 0, 4, 3], 0], [[0], 1000000000], [[1, 0], 1], [[1, 0], 1000000000], [[1, 2, 0], 3],
           [[1, 2, 0], 1000000000], [[2, 0, 1, 4, 3, 5], 7], [[3, 2, 0, 1], 5], [[4, 3, 2, 1, 0], 999999999]],
)
_r = rnd(7008)
p["tests"].append([_rand_perm(_r, 3500), 999999937])
p["tests"].append([_single_cycle(_r, 3500), 2000000000 // 3])
p["tests"].append([_rand_perm(_r, 3000), 123456789])


def b_applyk(perm, k):
    res = []
    for i in range(len(perm)):
        j = i
        for _ in range(k):
            j = perm[j]
        res.append(j)
    return res


def g_applyk(r):
    return [_rand_perm(r, r.randint(1, 9)), r.randint(0, 25)]


def v_applyk(tests):
    for t in tests:
        a, k = t["args"]
        assert 1 <= len(a) <= 10000 and _is_perm(a) and 0 <= k <= 10 ** 9


CHECKS["apply-permutation-k-times"] = (b_applyk, g_applyk, "exact")
VALIDATE["apply-permutation-k-times"] = v_applyk

# ------------------------------------------------------------------ tail and cycle length

p = add(
    id="index-walk-tail-and-cycle", title="Tail and Cycle of an Index Walk", diff="Medium", topic=T, tier="extra",
    fn="tailAndCycle", params=[("nums", "int[]")], ret="int[]", cmp="exact",
    desc="<p>Every value of <code>nums</code> is a valid index of <code>nums</code>. Start at index 0 and repeatedly move with <code>i = nums[i]</code>. The walk visits some indices once (the <em>tail</em>) and then runs forever around a cycle of indices.</p>"
         "<p>Return <code>[tail, cycle]</code>, where <code>tail</code> is the number of distinct indices visited before the first index of the cycle, and <code>cycle</code> is the number of distinct indices in the cycle. Index 0 counts in the tail unless it lies on the cycle itself.</p>"
         "<p>Example: <code>nums = [1, 2, 3, 1]</code> walks 0, 1, 2, 3, 1, 2, 3, ... so the tail is <code>{0}</code> and the cycle is <code>{1, 2, 3}</code>; the answer is <code>[1, 3]</code>. For <code>nums = [0]</code> the answer is <code>[0, 1]</code>.</p>",
    constraints=["1 &le; n &le; 10,000", "0 &le; nums[i] &lt; n"],
    hints=["Record the step number at which each index is first reached. The first time you hit an index again, you can read both lengths off the step numbers. This uses O(n) memory.",
           "To save the memory, think of two runners: one moves one step at a time, the other two steps at a time. If there is a cycle they must meet inside it.",
           "After they meet: a runner restarted at 0 and a runner left at the meeting point, both moving one step per turn, meet at the first index of the cycle after exactly <code>tail</code> turns. Then walk once around from that index to measure the cycle length."],
    editorial=["The walk is the path of a functional graph from a starting node, so its shape is a tail followed by a cycle. With a first-visit table the solution is immediate: when you reach an index that was first seen at step s, and you are now at step t, the tail has s indices and the cycle has t - s.",
               "Floyd's algorithm does the same in O(1) memory. Phase one: tortoise (1 step) and hare (2 steps) start at <code>nums[0]</code> and <code>nums[nums[0]]</code> and move until they meet. Phase two: reset the tortoise to 0 and move both one step per turn; the number of turns until they meet is the tail length, and they meet at the first cycle index. Phase three: from that index step until you return to it; the number of steps is the cycle length.",
               "The same technique is the standard solution of the \"find the duplicate number\" problem."],
    time="O(n)", space="O(1)",
    solution='''def tailAndCycle(nums):
    tort = nums[0]
    hare = nums[nums[0]]
    while tort != hare:
        tort = nums[tort]
        hare = nums[nums[hare]]
    tort = 0
    tail = 0
    while tort != hare:
        tort = nums[tort]
        hare = nums[hare]
        tail += 1
    cycle = 1
    hare = nums[tort]
    while hare != tort:
        hare = nums[hare]
        cycle += 1
    return [tail, cycle]
''',
    tests=[[[1, 2, 3, 1]], [[0]], [[1, 0]], [[0, 0]], [[1, 1]], [[1, 2, 0]], [[1, 2, 3, 4, 2]], [[2, 2, 3, 4, 5, 3]],
           [[3, 3, 3, 0]], [[1, 2, 3, 4, 5, 6, 7, 8, 9, 5]]],
)


def _chain(r, n, tail, cyc):
    """walk 0 -> ... with exactly `tail` tail nodes and a cycle of `cyc` nodes; remaining nodes point randomly."""
    others = list(range(1, n))
    r.shuffle(others)
    walk = [0] + others[:tail + cyc - 1]
    a = [r.randrange(n) for _ in range(n)]
    for i in range(len(walk) - 1):
        a[walk[i]] = walk[i + 1]
    a[walk[-1]] = walk[tail]
    return a


_r = rnd(7009)
p["tests"].append([_chain(_r, 5000, 3500, 800)])
p["tests"].append([_chain(_r, 5000, 0, 4500)])
p["tests"].append([_chain(_r, 5000, 4999, 1)])


def b_tail(nums):
    first = {}
    i, step = 0, 0
    while i not in first:
        first[i] = step
        i = nums[i]
        step += 1
    return [first[i], step - first[i]]


def g_tail(r):
    n = r.randint(1, 10)
    return [r.randrange(n) for _ in range(n)]


def v_tail(tests):
    for t in tests:
        a = t["args"][0]
        assert 1 <= len(a) <= 10000 and all(0 <= x < len(a) for x in a)


CHECKS["index-walk-tail-and-cycle"] = (b_tail, lambda r: [g_tail(r)], "exact")
VALIDATE["index-walk-tail-and-cycle"] = v_tail

# ------------------------------------------------------------------ couples holding hands

p = add(
    id="couples-sit-side-by-side", title="Couples Sit Side by Side", diff="Hard", topic=T, tier="extra",
    fn="minSwapsCouples", params=[("row", "int[]")], ret="int", cmp="exact",
    desc="<p>There are <code>n</code> couples and <code>2n</code> seats in a single row, numbered <code>0..2n-1</code>. The people are numbered <code>0..2n-1</code> and couple <code>k</code> consists of persons <code>2k</code> and <code>2k + 1</code>. <code>row[i]</code> is the person sitting in seat <code>i</code>.</p>"
         "<p>In one move any two people may exchange seats. Return the minimum number of moves after which every couple sits in two neighbouring seats <code>(2j, 2j + 1)</code> (in either order).</p>"
         "<p>Example: <code>row = [0, 2, 1, 3]</code> returns <code>1</code>: swap persons 2 and 1.</p>",
    constraints=["2 &le; row.length &le; 6,000 and row.length is even", "row is a permutation of 0..row.length - 1"],
    hints=["Look at the seat pairs <code>(0,1), (2,3), ...</code> one by one from the left. Once a pair is settled you never need to touch it again.",
           "If seat 0 holds person x, the partner of x is <code>x ^ 1</code>. Putting that partner into seat 1 costs at most one swap, and it is never worse than any other choice for that pair.",
           "Keep an array <code>pos[person]</code> with the current seat of everyone, so each swap and each lookup is O(1). Process seat pairs from left to right and count the swaps. (Equivalent view: connect two couples when they share a seat pair; the answer is the sum of <code>size - 1</code> over the connected groups.)"],
    editorial=["Take the first seat pair. If it is not already a couple, the person in seat 0 must end up next to their partner and the person in seat 1 does not belong to them. Swapping the partner into seat 1 fixes this pair with one move, and that move also ends up being part of an optimal solution: there is always an optimal solution with this move because any solution has to bring the partner of the person in seat 0 next to him, and swapping a different person into seat 1 can only be worse or equal.",
               "Therefore a greedy sweep from left to right is optimal. For pair <code>(2j, 2j+1)</code> let <code>x = row[2j]</code>; the partner is <code>x ^ 1</code>. If <code>row[2j + 1]</code> is not the partner, swap <code>row[2j + 1]</code> with the partner at <code>pos[x ^ 1]</code>, update <code>pos</code> for both people and add one to the answer.",
               "Graph view: make a node for every seat pair and an edge between the two pairs that hold the two members of each couple. The graph is a union of cycles, and a cycle with c pairs needs c - 1 swaps, which gives the same total. The sweep needs O(n) time and O(n) space for <code>pos</code>."],
    time="O(n)", space="O(n)",
    solution='''def minSwapsCouples(row):
    row = list(row)
    pos = [0] * len(row)
    for i, x in enumerate(row):
        pos[x] = i
    swaps = 0
    for i in range(0, len(row), 2):
        partner = row[i] ^ 1
        if row[i + 1] != partner:
            j = pos[partner]
            other = row[i + 1]
            row[i + 1], row[j] = partner, other
            pos[partner] = i + 1
            pos[other] = j
            swaps += 1
    return swaps
''',
    tests=[[[0, 2, 1, 3]], [[3, 2, 0, 1]], [[0, 1]], [[1, 0]], [[0, 1, 2, 3]], [[0, 2, 4, 1, 3, 5]], [[2, 0, 5, 4, 3, 1]],
           [[5, 4, 2, 6, 3, 1, 0, 7]], [[0, 2, 4, 6, 7, 1, 3, 5]], [[1, 3, 5, 7, 0, 2, 4, 6]]],
)
_r = rnd(7010)
p["tests"].append([_rand_perm(_r, 6000)])
_a = []
for k in range(3000):
    _a += [2 * k, 2 * k + 1]
p["tests"].append([_a])
_a = [x for k in range(3000) for x in ((2 * k + 1) % 6000, (2 * k + 2) % 6000)]
p["tests"].append([_a])


def b_couples(row):
    n = len(row)
    start = tuple(row)

    def done(t):
        return all(t[i] // 2 == t[i + 1] // 2 for i in range(0, n, 2))

    def dfs(t, d):
        if done(t):
            return True
        if d == 0:
            return False
        for i in range(n):
            for j in range(i + 1, n):
                l = list(t)
                l[i], l[j] = l[j], l[i]
                if dfs(tuple(l), d - 1):
                    return True
        return False

    d = 0
    while not dfs(start, d):
        d += 1
    return d


def g_couples(r):
    return _rand_perm(r, 2 * r.randint(1, 4))


def v_couples(tests):
    for t in tests:
        a = t["args"][0]
        assert 2 <= len(a) <= 6000 and len(a) % 2 == 0 and _is_perm(a)


CHECKS["couples-sit-side-by-side"] = (b_couples, lambda r: [g_couples(r)], "exact")
VALIDATE["couples-sit-side-by-side"] = v_couples

# ------------------------------------------------------------------ maximum invited (favorite person)

p = add(
    id="max-guests-around-favorite-table", title="Maximum Guests Around a Favorite-Person Table", diff="Hard", topic=T, tier="extra",
    fn="maxGuests", params=[("favorite", "int[]")], ret="int", cmp="exact",
    desc="<p>There are <code>n</code> employees numbered <code>0..n-1</code> and one round table. Employee <code>i</code> has a favorite colleague <code>favorite[i]</code> (never themselves). The company invites some employees and seats them around the table in any order of its choosing. An invited employee attends only if they are seated directly next to their favorite colleague, on the left or on the right (a table with two people counts both neighbours as the same person).</p>"
         "<p>Return the largest number of employees that can be invited and seated so that everybody invited is happy. The favorite of an invited employee must of course be invited too.</p>"
         "<p>Example: <code>favorite = [2, 2, 1, 2]</code> returns <code>3</code>: invite 0, 1 and 2 and seat them as 0, 2, 1 around the table. Employee 3 cannot join.</p>",
    constraints=["2 &le; n &le; 5,000", "0 &le; favorite[i] &lt; n and favorite[i] &ne; i"],
    hints=["Treat <code>i -> favorite[i]</code> as an arrow. Every employee has exactly one outgoing arrow, so each connected piece is a cycle with chains of employees leading into it.",
           "At a round table everyone must sit beside their favorite. For a cycle of three or more employees the only way to satisfy everyone in it is to seat the whole cycle in order, and nobody else fits. A 2-cycle (two employees who like each other) is different: other people can sit on the outer sides of these two.",
           "Answer = max(longest cycle of length &ge; 3, total over all 2-cycles of [2 + longest chain leading into one member + longest chain leading into the other]). Find chain lengths by repeatedly removing employees nobody likes (topological order), propagating the depth along the arrows."],
    editorial=["Each component of the arrow graph has exactly one cycle. If the table contains someone from a cycle of length L &ge; 3, their favorite and the favorite's favorite follow the arrows and force all L employees in order around the table; no free seat remains, so the table consists of that cycle alone. The candidate is L.",
               "For a 2-cycle (a, b) the table can be built as a line that runs <code>... -> a, b <- ...</code>: a chain of employees x<sub>1</sub> -> x<sub>2</sub> -> ... -> a sits to one side of a, and a chain leading into b sits on the other side of b, and the two ends of this line meet around the table. Different 2-cycles can share the same table, because the line from one 2-cycle can close up with the line of another. So all 2-cycles are added up, each contributing 2 plus the longest chain entering each of its members.",
               "Computing it: count in-degrees, put all employees with in-degree 0 in a queue, pop one and relax <code>depth[favorite[u]] = max(depth[favorite[u]], depth[u] + 1)</code> (all depths start at 1), decrease in-degree of the target and push it when it hits 0. The employees that never get popped are exactly the cycle members. Walk each cycle once: for L &ge; 3 update the best length, for L = 2 add <code>depth[a] + depth[b]</code> to the 2-cycle total. The result is the maximum of the two. All steps are O(n)."],
    time="O(n)", space="O(n)",
    solution='''def maxGuests(favorite):
    n = len(favorite)
    indeg = [0] * n
    for f in favorite:
        indeg[f] += 1
    depth = [1] * n
    queue = [i for i in range(n) if indeg[i] == 0]
    removed = [False] * n
    while queue:
        u = queue.pop()
        removed[u] = True
        v = favorite[u]
        if depth[u] + 1 > depth[v]:
            depth[v] = depth[u] + 1
        indeg[v] -= 1
        if indeg[v] == 0:
            queue.append(v)
    best_cycle = 0
    pairs = 0
    for i in range(n):
        if removed[i]:
            continue
        length = 0
        j = i
        while not removed[j]:
            removed[j] = True
            length += 1
            j = favorite[j]
        if length == 2:
            pairs += depth[i] + depth[favorite[i]]
        else:
            best_cycle = max(best_cycle, length)
    return max(best_cycle, pairs)
''',
    tests=[[[2, 2, 1, 2]], [[1, 2, 0]], [[3, 0, 1, 4, 1]], [[1, 0]], [[1, 0, 0]], [[1, 0, 3, 2]], [[1, 0, 1, 2, 3]],
           [[1, 0, 0, 2, 2, 3]], [[1, 2, 3, 4, 0, 0, 1]], [[1, 0, 3, 2, 1, 2]]],
)


def _fav_pairs(r, n):
    """several 2-cycles with long chains plus a long plain cycle competitor."""
    f = [0] * n
    idx = list(range(n))
    r.shuffle(idx)
    pos = 0
    # two 2-cycles with chains
    for length in (n // 4, n // 5):
        a, b = idx[pos], idx[pos + 1]
        f[a], f[b] = b, a
        pos += 2
        for side in (a, b):
            prev = side
            for _ in range(length // 2):
                x = idx[pos]
                pos += 1
                f[x] = prev
                prev = x
    rest = idx[pos:]
    for x in rest:   # the remaining employees point to random earlier nodes
        f[x] = r.choice(idx[:pos]) if pos else idx[0]
    for i in range(n):
        if f[i] == i:
            f[i] = idx[0] if idx[0] != i else idx[1]
    return f


def _fav_cycle(r, n, cyc):
    idx = list(range(n))
    r.shuffle(idx)
    f = [0] * n
    for i in range(cyc):
        f[idx[i]] = idx[(i + 1) % cyc]
    for i in range(cyc, n):
        f[idx[i]] = idx[r.randrange(0, i)]
    return f


_r = rnd(7011)
p["tests"].append([_fav_pairs(_r, 4800)])
p["tests"].append([_fav_cycle(_r, 5000, 3000)])
p["tests"].append([[(i * 7 + 3) % 5000 if (i * 7 + 3) % 5000 != i else (i + 1) % 5000 for i in range(5000)]])
p["tests"].append([[1, 0] + [0] * 4000])


def b_guests(fav):
    n = len(fav)
    best = 0
    for mask in range(1, 1 << n):
        members = [i for i in range(n) if mask >> i & 1]
        m = len(members)
        if m <= best or m < 2:
            continue
        if any(not mask >> fav[i] & 1 for i in members):
            continue
        first = members[0]
        for rest in permutations(members[1:]):
            seat = (first,) + rest
            ok = True
            for k in range(m):
                x = seat[k]
                if fav[x] != seat[(k - 1) % m] and fav[x] != seat[(k + 1) % m]:
                    ok = False
                    break
            if ok:
                best = m
                break
    return best


def g_guests(r):
    n = r.randint(2, 7)
    return [r.choice([j for j in range(n) if j != i]) for i in range(n)]


def v_guests(tests):
    for t in tests:
        a = t["args"][0]
        n = len(a)
        assert 2 <= n <= 5000 and all(0 <= a[i] < n and a[i] != i for i in range(n))


CHECKS["max-guests-around-favorite-table"] = (b_guests, lambda r: [g_guests(r)], "exact")
VALIDATE["max-guests-around-favorite-table"] = v_guests
