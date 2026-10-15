"""Problems: two pointers, fast and slow pointers on arrays (index sequences, cycles, duplicates). See data/lib.py for the registry."""
from lib import add, rnd, CHECKS, VALIDATE, gen_arr  # noqa: F401

INT_MIN, INT_MAX = -(2 ** 31), 2 ** 31 - 1
TOPIC = "Two Pointers"

SUCC = ("<p><strong>Encoding.</strong> The array <code>nxt</code> describes a successor function on the positions "
        "<code>0..n-1</code>: from position <code>i</code> a step always leads to position <code>nxt[i]</code>.</p>")


# ================================================================ EASY

p = add(
    id="jump-walk-escape-steps", title="Jump Walk Escape Steps", diff="Easy", topic=TOPIC,
    fn="escapeSteps", params=[("nums", "int[]")], ret="int", cmp="exact",
    desc="<p>You stand on index <code>0</code> of the array <code>nums</code>. In every jump you move from the current index <code>i</code> to index <code>i + nums[i]</code>; the values may be negative (jump left) or zero (stay on the spot).</p><p>As soon as a jump lands on an index outside <code>0..n-1</code>, you have escaped. Return the number of jumps you needed, counting the final jump that leaves the array. If you will never leave, return <code>-1</code>.</p><p>Example: for <code>nums = [2,3,-1,1,4]</code> you visit indices <code>0, 2, 1, 4</code> and the fourth jump lands on index <code>8</code>, so the answer is <code>4</code>. For <code>[1,-1]</code> you bounce between index 0 and 1 forever, so the answer is <code>-1</code>.</p>",
    constraints=["1 &le; nums.length &le; 6,000", "-10,000 &le; nums[i] &le; 10,000"],
    hints=["Just simulate the jumps. The only question is how to notice that you will never get out.",
           "The walk is deterministic: if you ever stand on an index for the second time, you are inside a cycle and will repeat it forever.",
           "There are only n indices, so a walk that escapes needs at most n jumps. Count the jumps, and if you exceed n without leaving, answer -1. A fast and a slow pointer that meet would also prove a cycle without a visited set."],
    editorial=["Because the next position depends only on the current position, the walk either leaves the array or eventually revisits an index and then loops for ever. A walk that leaves without repeating an index visits at most n different indices, so it needs at most n jumps.",
               "So simulate up to n jumps: if you leave, return the count; if the counter passes n, you must have repeated an index, so return -1. This is O(n) time and O(1) memory. A visited array gives the same answer, and Floyd's slow/fast pointers can detect the loop too, but the jump bound is the simplest way to get O(1) space."],
    time="O(n)", space="O(1)",
    solution='''def escapeSteps(nums):
    n = len(nums)
    i = 0
    for jumps in range(1, n + 2):
        i += nums[i]
        if i < 0 or i >= n:
            return jumps
    return -1
''',
    tests=[[[2, 3, -1, 1, 4]], [[1, -1]], [[5]], [[0]], [[-1]], [[1, 1, 1, 1]], [[3, 0, 0, 0]], [[1, 2, -1]],
           [[2, -1, 1, -2]], [[1, 1, -2, 5]]],
)


def _jump_path(r, n, loop_back):
    perm = [0] + r.sample(range(1, n), n - 1) if n > 1 else [0]
    nums = [r.randint(-9, 9) for _ in range(n)]
    for k in range(len(perm) - 1):
        nums[perm[k]] = perm[k + 1] - perm[k]
    last = perm[-1]
    if loop_back is None:
        nums[last] = n - last + r.randint(0, 3)
    else:
        nums[last] = perm[loop_back] - last
    return nums


_r = rnd(7101)
p["tests"].append([_jump_path(_r, 5000, None)])
p["tests"].append([_jump_path(_r, 5000, 10)])
p["tests"].append([[1] * 6000])
p["tests"].append([_jump_path(_r, 6000, 5990)])


def b_escape(nums):
    n = len(nums)
    i, seen, cnt = 0, set(), 0
    while 0 <= i < n:
        if i in seen:
            return -1
        seen.add(i)
        i += nums[i]
        cnt += 1
    return cnt


def v_escape(tests):
    for t in tests:
        nums = t["args"][0]
        assert 1 <= len(nums) <= 6000 and all(-10000 <= v <= 10000 for v in nums)
        assert t["expected"] == b_escape(nums)
    assert any(t["expected"] == -1 for t in tests) and any(t["expected"] > 1000 for t in tests)


CHECKS["jump-walk-escape-steps"] = (b_escape, lambda r: [[r.randint(-4, 4) for _ in range(r.randint(1, 8))]], "exact")
VALIDATE["jump-walk-escape-steps"] = v_escape


p = add(
    id="digit-power-cycle-length", title="Digit Power Cycle Length", diff="Easy", topic=TOPIC,
    fn="digitPowerCycleLength", params=[("n", "int"), ("p", "int")], ret="int", cmp="exact",
    desc="<p>Define <code>f(x)</code> as the sum of the <code>p</code>-th powers of the decimal digits of <code>x</code>. For <code>p = 2</code>, <code>f(19) = 1 + 81 = 82</code>.</p><p>Start with <code>x<sub>0</sub> = n</code> and keep applying <code>f</code>: <code>x<sub>1</sub> = f(x<sub>0</sub>)</code>, <code>x<sub>2</sub> = f(x<sub>1</sub>)</code> and so on. This sequence always ends up repeating a block of values for ever. Return the length of that repeating block (the cycle). A value with <code>f(x) = x</code> is a cycle of length <code>1</code>.</p><p>Example: <code>n = 4, p = 2</code> gives <code>4, 16, 37, 58, 89, 145, 42, 20, 4, ...</code>, a cycle of length <code>8</code>. For <code>n = 19, p = 2</code> the sequence reaches <code>1</code> and stays there, so the answer is <code>1</code>.</p>",
    constraints=["1 &le; n &le; 10<sup>9</sup>", "2 &le; p &le; 5"],
    hints=["Every value after the first step is small (a 10-digit number has at most 10 digits to add up), so the sequence must repeat.",
           "Remember the position at which each value was first seen. When a value comes back, the difference of positions is the cycle length.",
           "To avoid the dictionary, run a slow pointer (one application of f per step) and a fast pointer (two per step) until they meet inside the cycle, then walk once around the cycle counting steps."],
    editorial=["The values of f are bounded: for p &le; 5 and at most 10 digits, f(x) &le; 10 * 9<sup>5</sup>. A sequence over a finite set with a deterministic rule must eventually repeat, and from then on it cycles through the same block.",
               "Floyd's method finds it with O(1) memory. Let the slow pointer take one step and the fast pointer two steps each round; they meet at a value that lies inside the cycle. Keep the slow pointer there, advance the fast one around the cycle until it returns, and count the steps. That count is the cycle length. Storing first-seen indices in a map is equally correct and easier to write."],
    time="O(L) where L is the length of the tail plus the cycle", space="O(1)",
    solution='''def digitPowerCycleLength(n, p):
    def f(x):
        s = 0
        while x:
            x, d = divmod(x, 10)
            s += d ** p
        return s

    slow, fast = f(n), f(f(n))
    while slow != fast:
        slow = f(slow)
        fast = f(f(fast))
    length = 1
    x = f(slow)
    while x != slow:
        x = f(x)
        length += 1
    return length
''',
    tests=[[19, 2], [4, 2], [1, 2], [2, 2], [145, 2], [153, 3], [370, 3], [6, 3], [4150, 5], [999999999, 5],
           [1000000000, 4], [123456789, 3], [77, 4], [9, 5]],
)


def b_dpcl(n, p):
    seen, x, i = {}, n, 0
    while x not in seen:
        seen[x] = i
        i += 1
        x = sum(int(c) ** p for c in str(x))
    return i - seen[x]


def v_dpcl(tests):
    for t in tests:
        n, p_ = t["args"]
        assert 1 <= n <= 10 ** 9 and 2 <= p_ <= 5
        assert t["expected"] == b_dpcl(n, p_)
    assert len({t["expected"] for t in tests}) >= 4


CHECKS["digit-power-cycle-length"] = (b_dpcl, lambda r: [r.randint(1, 5000), r.randint(2, 5)], "exact")
VALIDATE["digit-power-cycle-length"] = v_dpcl


p = add(
    id="two-walkers-first-meeting-time", title="Two Walkers First Meeting Time", diff="Easy", topic=TOPIC,
    fn="firstMeetingTime", params=[("nxt", "int[]"), ("a", "int"), ("b", "int")], ret="int", cmp="exact",
    desc=SUCC + "<p>Two walkers start at the same moment, one at position <code>a</code> and one at position <code>b</code>. In every round, both of them take exactly one step along <code>nxt</code>.</p><p>Return the smallest number of rounds <code>t &ge; 0</code> after which both walkers stand on the same position, or <code>-1</code> if they never do. If <code>a = b</code> the answer is <code>0</code>.</p><p>Example: <code>nxt = [1,2,3,3]</code>, <code>a = 0</code>, <code>b = 1</code>: the walkers are at <code>(0,1)</code>, then <code>(1,2)</code>, then <code>(2,3)</code>, then <code>(3,3)</code>, so the answer is <code>3</code>. For <code>nxt = [1,0]</code>, <code>a = 0</code>, <code>b = 1</code> they swap places every round and never meet: <code>-1</code>.</p>",
    constraints=["1 &le; nxt.length &le; 6,000", "0 &le; nxt[i] &lt; nxt.length", "0 &le; a, b &lt; nxt.length"],
    hints=["Once the two walkers are on the same position they stay together, because the next position depends only on the current one.",
           "Think about where each walker is after n steps: every walk has left its tail by then and is going round a cycle.",
           "If the walkers have not met after n rounds they are on cycles at a constant distance, so they never will. Simulate rounds 0..n, return the first round where they coincide, otherwise -1."],
    editorial=["Both walkers follow the same function, so as soon as they share a position they share all later positions. The only question is whether they meet at all, and when.",
               "Any path in a graph with n positions and one outgoing step per position leaves its tail (at most n - 1 steps) and then circles forever. After n rounds both walkers are inside cycles. If they are in different cycles, or in the same cycle at different places, their relative offset never changes, so they never meet. Hence it is enough to compare the positions in rounds 0 to n, which is O(n) time and O(1) space."],
    time="O(n)", space="O(1)",
    solution='''def firstMeetingTime(nxt, a, b):
    n = len(nxt)
    for t in range(n + 1):
        if a == b:
            return t
        a = nxt[a]
        b = nxt[b]
    return -1
''',
    tests=[[[1, 2, 3, 3], 0, 1], [[1, 0], 0, 1], [[0], 0, 0], [[1, 2, 0], 0, 0], [[1, 2, 0], 0, 1],
           [[1, 1, 1], 0, 2], [[1, 2, 3, 4, 4], 0, 3], [[1, 2, 3, 0, 3], 4, 0], [[0, 0, 1, 2], 3, 1],
           [[2, 3, 0, 1], 0, 1]],
)


def _two_walk(r, n, merge_at, cyc):
    # long chain A and chain B joining A at distance merge_at from its start; cycle of length cyc at the end
    nxt = list(range(n))
    nodes = r.sample(range(n), n)
    tail = nodes[:n - cyc]
    cyc_nodes = nodes[n - cyc:]
    for i in range(len(tail) - 1):
        nxt[tail[i]] = tail[i + 1]
    nxt[tail[-1]] = cyc_nodes[0]
    for i in range(cyc):
        nxt[cyc_nodes[i]] = cyc_nodes[(i + 1) % cyc]
    return nxt, tail, cyc_nodes


_r = rnd(7102)
_nxt, _tail, _cn = _two_walk(_r, 3000, 0, 7)
p["tests"].append([_nxt, _tail[0], _tail[1200]])           # same chain, never in step before cycle -> check cycle phase
p["tests"].append([_nxt, _tail[10], _cn[3]])
_nxt, _tail, _cn = _two_walk(_r, 3000, 0, 1)
_other = _tail[1500]
p["tests"].append([_nxt, _tail[0], _other])
_nxt = list(range(1, 3000)) + [2999]                        # one long path, self loop at the end
p["tests"].append([_nxt, 0, 0])
p["tests"].append([_nxt, 0, 1])
_nxt = [(i + 1) % 3000 for i in range(3000)]
p["tests"].append([_nxt, 0, 1500])


def b_meet(nxt, a, b):
    for t in range(3 * len(nxt) + 5):
        if a == b:
            return t
        a, b = nxt[a], nxt[b]
    return -1


def g_meet(r):
    n = r.randint(1, 8)
    return [[r.randrange(n) for _ in range(n)], r.randrange(n), r.randrange(n)]


def v_meet(tests):
    for t in tests:
        nxt, a, b = t["args"]
        n = len(nxt)
        assert 1 <= n <= 6000 and all(0 <= v < n for v in nxt) and 0 <= a < n and 0 <= b < n
        assert t["expected"] == b_meet(nxt, a, b)
    assert any(t["expected"] == -1 for t in tests) and any(t["expected"] > 100 for t in tests)


CHECKS["two-walkers-first-meeting-time"] = (b_meet, g_meet, "exact")
VALIDATE["two-walkers-first-meeting-time"] = v_meet


# ================================================================ MEDIUM

p = add(
    id="node-after-k-steps-in-successor-walk", title="Node After K Steps in a Successor Walk", diff="Medium", topic=TOPIC,
    fn="nodeAfterKSteps", params=[("nxt", "int[]"), ("start", "int"), ("k", "int")], ret="int", cmp="exact",
    desc=SUCC + "<p>Starting at position <code>start</code>, take exactly <code>k</code> steps along <code>nxt</code> and return the position you end on. With <code>k = 0</code> the answer is <code>start</code>.</p><p><code>k</code> can be as large as 2<sup>31</sup> - 1, so you cannot simulate step by step.</p><p>Example: <code>nxt = [1,2,3,4,2]</code>, <code>start = 0</code>, <code>k = 7</code> visits <code>0,1,2,3,4,2,3,4</code>, so the answer is <code>4</code>.</p>",
    constraints=["1 &le; nxt.length &le; 6,000", "0 &le; nxt[i] &lt; nxt.length", "0 &le; start &lt; nxt.length", "0 &le; k &le; 2<sup>31</sup> - 1"],
    hints=["The walk is a path (the tail) followed by a cycle that repeats for ever. Once you are on the cycle, only the remainder of the step count modulo the cycle length matters.",
           "Find the length of the tail (call it mu) and the length of the cycle (lam). If k &lt; mu simply walk k steps.",
           "Use Floyd's slow/fast pointers to find a meeting point in the cycle, restart one pointer at start to find mu (they meet at the cycle entrance), then count lam by walking once around. Finally walk mu + (k - mu) mod lam steps."],
    editorial=["From any start, the sequence of positions is eventually periodic: first mu positions that are never visited again (the tail), then a cycle of length lam. For k &ge; mu the position after k steps equals the position after <code>mu + (k - mu) mod lam</code> steps, which is at most n - 1 steps away.",
               "Floyd's algorithm computes both lengths with O(1) memory. Phase 1: slow moves one step, fast moves two; they meet inside the cycle. Phase 2: restart slow at start and move both one step at a time; they meet at the entrance, after mu steps. Phase 3: from the entrance walk until you return to it, counting lam steps. Then simulate the reduced number of steps. Total time O(n), space O(1). Binary lifting would also work but needs O(n log k) memory."],
    time="O(n)", space="O(1)",
    solution='''def nodeAfterKSteps(nxt, start, k):
    slow = fast = start
    while True:
        slow = nxt[slow]
        fast = nxt[nxt[fast]]
        if slow == fast:
            break
    mu = 0
    slow = start
    while slow != fast:
        slow = nxt[slow]
        fast = nxt[fast]
        mu += 1
    lam = 1
    fast = nxt[slow]
    while fast != slow:
        fast = nxt[fast]
        lam += 1
    if k >= mu:
        k = mu + (k - mu) % lam
    pos = start
    for _ in range(k):
        pos = nxt[pos]
    return pos
''',
    tests=[[[1, 2, 3, 4, 2], 0, 7], [[0], 0, 2147483647], [[1, 0], 0, 5], [[1, 0], 0, 2147483647], [[1, 2, 3, 4, 2], 0, 0],
           [[1, 2, 3, 4, 2], 0, 3], [[1, 2, 3, 4, 2], 0, 1000000000], [[1, 2, 3, 1], 0, 2147483646],
           [[2, 2, 2], 0, 1], [[1, 2, 0, 0], 3, 10], [[3, 3, 1, 3], 0, 2147483647]],
)
_r = rnd(7105)
_nxt, _tail, _cn = _two_walk(_r, 6000, 0, 2999)
p["tests"].append([_nxt, _tail[0], 2147483647])
p["tests"].append([_nxt, _tail[0], len(_tail) + 5])
_nxt, _tail, _cn = _two_walk(_r, 6000, 0, 3)
p["tests"].append([_nxt, _tail[0], 1234567890])


def b_kstep(nxt, start, k):
    pos = start
    for _ in range(k):
        pos = nxt[pos]
    return pos


def g_kstep(r):
    n = r.randint(1, 8)
    return [[r.randrange(n) for _ in range(n)], r.randrange(n), r.randint(0, 60)]


def v_kstep(tests):
    for t in tests:
        nxt, s, k = t["args"]
        n = len(nxt)
        assert 1 <= n <= 6000 and all(0 <= v < n for v in nxt) and 0 <= s < n and 0 <= k <= INT_MAX
        # independent check: map positions to the first time they are seen
        seen, pos, i = {}, s, 0
        while pos not in seen:
            seen[pos] = i
            pos = nxt[pos]
            i += 1
        mu, lam = seen[pos], i - seen[pos]
        kk = k if k < mu else mu + (k - mu) % lam
        pos = s
        for _ in range(kk):
            pos = nxt[pos]
        assert t["expected"] == pos


CHECKS["node-after-k-steps-in-successor-walk"] = (b_kstep, g_kstep, "exact")
VALIDATE["node-after-k-steps-in-successor-walk"] = v_kstep


p = add(
    id="count-escaping-start-indices", title="Count Escaping Start Indices", diff="Medium", topic=TOPIC,
    fn="countEscapingStarts", params=[("nums", "int[]")], ret="int", cmp="exact",
    desc="<p>In the array <code>nums</code>, standing on index <code>i</code> you jump to index <code>i + nums[i]</code> (the values may be negative or zero). A start index is <em>escaping</em> if repeating the jump from it eventually lands outside the array (index &lt; 0 or &ge; n). Otherwise the walk loops for ever.</p><p>Return how many of the <code>n</code> indices are escaping start indices.</p><p>Example: for <code>[1,1,-2,3]</code> the indices 0, 1, 2 walk around the cycle <code>0 -> 1 -> 2 -> 0</code>, while index 3 jumps to index 6 and escapes, so the answer is <code>1</code>. For <code>[2,3,-1,1,4]</code> every index escapes: <code>5</code>.</p>",
    constraints=["1 &le; nums.length &le; 6,000", "-10,000 &le; nums[i] &le; 10,000"],
    hints=["Running the escape check from every index separately costs up to O(n<sup>2</sup>). Walks from different starts share long stretches.",
           "Give every index a verdict once you know it: escapes or loops. A walk that reaches an index with a known verdict inherits it.",
           "Walk from an unvisited start, marking indices as 'on the current path'. If you step outside, or onto a known escaping index, the whole path escapes. If you step onto a loop-verdict index or onto the current path, the whole path loops. Then assign the verdict to every index of the path."],
    editorial=["The structure is a graph where every index has one outgoing edge, plus a virtual exit node for all jumps that leave the array. An index escapes exactly when its path reaches the exit; otherwise it ends in a cycle.",
               "Process each unvisited start with a state array (0 new, 1 on current path, 2 escapes, 3 loops). Follow jumps and push the indices on a path list. Stop when you leave the array (verdict: escapes), hit a state 2 or 3 index (inherit it), or hit a state 1 index (you closed a cycle: verdict loops). Write the verdict to the whole path. Each index enters a path once, so the time is O(n) and memory O(n)."],
    time="O(n)", space="O(n)",
    solution='''def countEscapingStarts(nums):
    n = len(nums)
    state = [0] * n  # 0 new, 1 on the current path, 2 escapes, 3 loops
    for s in range(n):
        if state[s]:
            continue
        path = []
        u = s
        while True:
            if u < 0 or u >= n:
                verdict = 2
                break
            if state[u] == 1:
                verdict = 3
                break
            if state[u] >= 2:
                verdict = state[u]
                break
            state[u] = 1
            path.append(u)
            u += nums[u]
        for v in path:
            state[v] = verdict
    return sum(1 for v in state if v == 2)
''',
    tests=[[[1, 1, -2, 3]], [[2, 3, -1, 1, 4]], [[0]], [[1]], [[-1, 0]], [[1, -1]], [[0, 0, 0]], [[1, 1, 1, -3, 5]],
           [[2, 2, -4, 1, 1, -5]], [[3, 2, 1, 0, -1, -2, -3]]],
)
_r = rnd(7106)
p["tests"].append([[_r.randint(-3, 3) for _ in range(6000)]])
p["tests"].append([[_r.randint(-40, 1) for _ in range(5000)]])
p["tests"].append([_jump_path(_r, 6000, None)])


def b_esc_count(nums):
    n = len(nums)
    cnt = 0
    for s in range(n):
        i = s
        for _ in range(n + 1):
            if not 0 <= i < n:
                cnt += 1
                break
            i += nums[i]
    return cnt


def v_esc_count(tests):
    for t in tests:
        nums = t["args"][0]
        assert 1 <= len(nums) <= 6000 and all(-10000 <= v <= 10000 for v in nums)
        assert 0 <= t["expected"] <= len(nums)
        if len(nums) <= 800:
            assert t["expected"] == b_esc_count(nums)
    assert any(0 < t["expected"] < len(t["args"][0]) for t in tests)


CHECKS["count-escaping-start-indices"] = (b_esc_count, lambda r: [[r.randint(-4, 4) for _ in range(r.randint(1, 9))]], "exact")
VALIDATE["count-escaping-start-indices"] = v_esc_count


p = add(
    id="count-happy-numbers-up-to", title="Count Happy Numbers Up To N", diff="Medium", topic=TOPIC, tier="extra",
    fn="countHappy", params=[("n", "int")], ret="int", cmp="exact",
    desc="<p>A positive integer is <em>happy</em> if repeatedly replacing it with the sum of the squares of its decimal digits eventually reaches <code>1</code>. For example <code>19 -> 82 -> 68 -> 100 -> 1</code> is happy, while <code>2 -> 4 -> 16 -> 37 -> 58 -> 89 -> 145 -> 42 -> 20 -> 4</code> falls into a cycle that never contains 1.</p><p>Return how many integers in the range <code>1..n</code> are happy.</p><p>Example: the happy numbers up to <code>10</code> are <code>1, 7, 10</code>, so <code>n = 10</code> gives <code>3</code>; there are <code>20</code> happy numbers up to <code>100</code>.</p>",
    constraints=["1 &le; n &le; 200,000"],
    hints=["Testing every number on its own with a cycle check is correct, but you repeat the same work over and over.",
           "After one step every number up to 200,000 becomes at most 6 * 81 = 486, so only a few hundred values are ever 'reached'.",
           "Decide happiness once for all values 1..486 (slow/fast pointers or a visited set), then for each x only compute the digit square sum and look the verdict up. The digit square sum of x can be derived from the one of x // 10."],
    editorial=["A number is happy exactly when its digit-square-sum is happy (and 1 is happy), so the verdict for x depends only on s(x), the sum of squared digits. For x &le; 200,000 we have s(x) &le; 6 * 81 = 486.",
               "Precompute happy[v] for v = 1..486 by running the fast/slow pointer test (advance slow by one application of s and fast by two; if fast lands on 1 the value is happy, if the pointers meet first it is not). Then compute s(x) for all x in order using <code>s(x) = s(x // 10) + (x % 10)<sup>2</sup></code> and count the x with happy[s(x)]. Total time O(n), memory O(n) for the s table (or O(1) if you recompute digits)."],
    time="O(n)", space="O(n)",
    solution='''def countHappy(n):
    LIM = 6 * 81 + 1

    def s(x):
        t = 0
        while x:
            x, d = divmod(x, 10)
            t += d * d
        return t

    happy = [False] * (LIM + 1)
    for v in range(1, LIM + 1):
        slow, fast = v, s(v)
        while fast != 1 and slow != fast:
            slow = s(slow)
            fast = s(s(fast))
        happy[v] = fast == 1
    sq = [0] * (n + 1)
    count = 0
    for x in range(1, n + 1):
        sq[x] = sq[x // 10] + (x % 10) ** 2
        if happy[sq[x]]:
            count += 1
    return count
''',
    tests=[[1], [2], [7], [10], [19], [100], [1000], [9999], [44], [500], [100000], [199999], [200000]],
)


def b_count_happy(n):
    def is_happy(x):
        seen = set()
        while x != 1 and x not in seen:
            seen.add(x)
            x = sum(int(c) ** 2 for c in str(x))
        return x == 1
    return sum(1 for x in range(1, n + 1) if is_happy(x))


def v_count_happy(tests):
    ans = {t["args"][0]: t["expected"] for t in tests}
    assert ans[10] == 3 and ans[100] == 20 and ans[1000] == 143
    for t in tests:
        assert 1 <= t["args"][0] <= 200000


CHECKS["count-happy-numbers-up-to"] = (b_count_happy, lambda r: [r.randint(1, 400)], "exact")
VALIDATE["count-happy-numbers-up-to"] = v_count_happy


p = add(
    id="lcg-sequence-tail-and-period", title="LCG Sequence Tail and Period", diff="Medium", topic=TOPIC, tier="extra",
    fn="tailAndPeriod", params=[("x0", "int"), ("a", "int"), ("c", "int"), ("m", "int")], ret="int[]", cmp="exact",
    desc="<p>A linear congruential generator produces the sequence <code>x<sub>0</sub>, x<sub>1</sub>, x<sub>2</sub>, ...</code> with <code>x<sub>k+1</sub> = (a * x<sub>k</sub> + c) mod m</code>. Because there are only <code>m</code> possible values, the sequence is eventually periodic.</p><p>Return the array <code>[mu, lam]</code> where <code>mu</code> is the number of leading terms that never appear again (the length of the <em>tail</em>, i.e. the smallest index from which the sequence repeats) and <code>lam</code> is the length of the repeating block (the <em>period</em>).</p><p>Example: <code>x0 = 3, a = 5, c = 0, m = 10</code> gives <code>3, 5, 5, 5, ...</code>, so the answer is <code>[1, 1]</code>. With <code>x0 = 0, a = 1, c = 1, m = 5</code> the terms are <code>0,1,2,3,4,0,...</code> so the answer is <code>[0, 5]</code>.</p>",
    constraints=["1 &le; m &le; 100,000", "0 &le; x0, a, c &lt; m"],
    hints=["Remembering the index of every value finds the first repeat directly, but needs a table of size up to m.",
           "Use a slow pointer (one step per round) and a fast pointer (two steps per round). They meet inside the cycle; walking once around from the meeting point gives the period.",
           "To get the tail length, restart one pointer at x0 and keep the other at the meeting point, then advance both one step at a time until they are equal: the number of steps is mu. Brent's variant (power-of-two teleporting) does the same with fewer evaluations."],
    editorial=["The generator is a deterministic function g(x) = (a x + c) mod m on m states. So the sequence of states looks like the letter rho: a tail of mu states followed by a cycle of lam states.",
               "Brent's algorithm: keep a 'tortoise' fixed at a checkpoint and move the 'hare' one step at a time, counting steps lam since the checkpoint; when the step count equals a power of two, teleport the tortoise to the hare and double the limit. When hare equals tortoise, lam is the period. To find mu, put both at x0, advance the hare lam steps, then move both together until they are equal; the number of moves is mu. Floyd's two-speed pointers work too, with about 3 times as many evaluations. Time O(mu + lam), space O(1)."],
    time="O(mu + lam)", space="O(1)",
    solution='''def tailAndPeriod(x0, a, c, m):
    def g(x):
        return (a * x + c) % m

    power = lam = 1
    tortoise = x0
    hare = g(x0)
    while tortoise != hare:
        if power == lam:
            tortoise = hare
            power *= 2
            lam = 0
        hare = g(hare)
        lam += 1
    tortoise = hare = x0
    for _ in range(lam):
        hare = g(hare)
    mu = 0
    while tortoise != hare:
        tortoise = g(tortoise)
        hare = g(hare)
        mu += 1
    return [mu, lam]
''',
    tests=[[3, 5, 0, 10], [0, 1, 1, 5], [0, 0, 0, 1], [5, 6, 0, 12], [3, 2, 0, 12], [1, 2, 1, 7], [4, 3, 3, 8],
           [7, 1, 0, 9], [0, 5, 3, 65536], [12345, 1103, 12345, 99991], [1, 2, 0, 100000], [99999, 99999, 99999, 100000],
           [1, 3, 0, 65536]],
)


def b_lcg(x0, a, c, m):
    seen, x, i = {}, x0, 0
    while x not in seen:
        seen[x] = i
        i += 1
        x = (a * x + c) % m
    return [seen[x], i - seen[x]]


def g_lcg(r):
    m = r.randint(1, 40)
    return [r.randrange(m), r.randrange(m), r.randrange(m), m]


def v_lcg(tests):
    for t in tests:
        x0, a, c, m = t["args"]
        assert 1 <= m <= 100000 and 0 <= x0 < m and 0 <= a < m and 0 <= c < m
        assert t["expected"] == b_lcg(x0, a, c, m)
    assert any(t["expected"][0] > 0 and t["expected"][1] > 1 for t in tests)
    assert any(t["expected"][1] > 30000 for t in tests)


CHECKS["lcg-sequence-tail-and-period"] = (b_lcg, g_lcg, "exact")
VALIDATE["lcg-sequence-tail-and-period"] = v_lcg


# ================================================================ HARD

p = add(
    id="longest-cycle-in-successor-array", title="Longest Cycle in a Successor Array", diff="Hard", topic=TOPIC,
    fn="longestCycle", params=[("nxt", "int[]")], ret="int", cmp="exact",
    desc="<p>The array <code>nxt</code> describes a directed graph on the nodes <code>0..n-1</code> in which every node has <em>at most one</em> outgoing edge: <code>nxt[i]</code> is the node that <code>i</code> points to, or <code>-1</code> if node <code>i</code> has no outgoing edge. A node may point to itself.</p><p>A <em>cycle</em> is a set of nodes that can be visited one after another by following the edges and that returns to its first node. Its length is the number of nodes in it (a node that points to itself is a cycle of length 1). Return the length of the longest cycle in the graph, or <code>-1</code> if there is no cycle.</p><p>Example: <code>nxt = [3,3,4,2,3]</code> has the cycle <code>2 -> 4 -> 3 -> 2</code> of length <code>3</code>, so the answer is <code>3</code>. For <code>[2,-1,3,1]</code> the walk <code>0 -> 2 -> 3 -> 1</code> ends at node 1 without edges: <code>-1</code>.</p>",
    constraints=["1 &le; nxt.length &le; 6,000", "-1 &le; nxt[i] &lt; nxt.length"],
    hints=["Every node has at most one outgoing edge, so the walk from any node either stops at a node with no edge or runs into a cycle.",
           "Walk from each node that was not seen yet. If the walk reaches a node that belongs to a different, earlier walk, nothing new can be found on this path.",
           "Give every visited node the global time at which it was first reached. During a walk started at time T0, if you reach a node whose stored time is at least T0 then you closed a new cycle, and its length is (current time - stored time)."],
    editorial=["Because every node has out-degree at most one, a walk never branches. All nodes of one weakly connected piece funnel into at most one cycle, and every cycle is found by walking from some node that leads into it.",
               "Keep a global counter <code>t</code> and an array <code>seen[u]</code> of the time when u was first visited (or -1). Process each start s that is still unseen: follow edges, assigning <code>seen[u] = t</code> and incrementing <code>t</code>, until you reach -1 or a visited node. If the stopping node v was visited during this very walk (<code>seen[v] &ge; t at start of the walk</code>), the nodes from v to the end of the walk form a cycle of length <code>t - seen[v]</code>. Otherwise v belongs to an earlier walk and its cycle (if any) was already counted. Each node is visited once, so the time is O(n) with O(n) memory. The O(1)-memory alternative applies Floyd's detection from every start, but costs O(n<sup>2</sup>) in the worst case unless visited nodes are marked."],
    time="O(n)", space="O(n)",
    solution='''def longestCycle(nxt):
    n = len(nxt)
    seen = [-1] * n
    t = 0
    best = -1
    for s in range(n):
        if seen[s] != -1:
            continue
        walk_start = t
        u = s
        while u != -1 and seen[u] == -1:
            seen[u] = t
            t += 1
            u = nxt[u]
        if u != -1 and seen[u] >= walk_start:
            best = max(best, t - seen[u])
    return best
''',
    tests=[[[3, 3, 4, 2, 3]], [[2, -1, 3, 1]], [[-1]], [[0]], [[1, 0]], [[1, 2, 3, -1]], [[1, 2, 0, 4, 5, 3]],
           [[1, 2, 0, 0]], [[-1, 0, 1, 2]], [[1, 1, 1, 1]], [[1, 2, 3, 4, 5, 6, 7, 3]]],
)
_r = rnd(7107)
_n = 5000
_perm = _r.sample(range(_n), _n)
_nx = [0] * _n
for _i in range(_n):
    _nx[_perm[_i]] = _perm[(_i + 1) % _n]
p["tests"].append([_nx])
_nx = [-1] * _n
for _i in range(_n - 1):
    _nx[_perm[_i]] = _perm[_i + 1]
p["tests"].append([_nx])                                   # one long path, no cycle
_nx[_perm[-1]] = _perm[_n - 700]                           # long tail plus a cycle of 700
p["tests"].append([_nx])
p["tests"].append([[_r.choice([-1, _r.randrange(_n), _r.randrange(_n)]) for _ in range(_n)]])


def b_longest_cycle(nxt):
    n = len(nxt)
    best = -1
    for s in range(n):
        pos, u, i = {}, s, 0
        while u != -1 and u not in pos:
            pos[u] = i
            i += 1
            u = nxt[u]
        if u != -1:
            best = max(best, i - pos[u])
    return best


def v_longest_cycle(tests):
    for t in tests:
        nxt = t["args"][0]
        assert 1 <= len(nxt) <= 6000 and all(-1 <= v < len(nxt) for v in nxt)
        if len(nxt) <= 1500:
            assert t["expected"] == b_longest_cycle(nxt)
    assert any(t["expected"] == -1 for t in tests) and any(t["expected"] > 500 for t in tests)


def g_longest_cycle(r):
    n = r.randint(1, 8)
    return [[r.choice([-1] + list(range(n))) for _ in range(n)]]


CHECKS["longest-cycle-in-successor-array"] = (b_longest_cycle, g_longest_cycle, "exact")
VALIDATE["longest-cycle-in-successor-array"] = v_longest_cycle




# ================================================================ MORE (replacing slots taken by other modules)

p = add(
    id="digit-factorial-chain-count", title="Digit Factorial Chain Count", diff="Medium", topic=TOPIC, tier="extra",
    fn="countFactorialChains", params=[("n", "int"), ("length", "int")], ret="int", cmp="exact",
    desc="<p>For a positive integer <code>x</code> let <code>f(x)</code> be the sum of the factorials of its decimal digits (remember <code>0! = 1</code>). For example <code>f(145) = 1! + 4! + 5! = 145</code> and <code>f(69) = 720 + 362880 = 363600</code>.</p><p>The <em>chain</em> of <code>x</code> is <code>x, f(x), f(f(x)), ...</code> stopped just before a term would repeat an earlier term of the same chain. Its length is the number of different values in it. For instance the chain of <code>69</code> is <code>69, 363600, 1454, 169, 363601</code> (the next value is <code>1454</code> again), so its length is <code>5</code>; the chain of <code>145</code> is just <code>145</code> with length <code>1</code>.</p><p>Return how many integers <code>x</code> in the range <code>1..n</code> have a chain of length exactly <code>length</code>.</p><p>Example: <code>n = 200, length = 1</code> returns <code>3</code>, namely <code>1, 2, 145</code>, which are the numbers with <code>f(x) = x</code> in that range.</p>",
    constraints=["1 &le; n &le; 100,000", "1 &le; length &le; 60"],
    hints=["Computing the chain of every x separately with a visited set is correct but repeats a lot of work: different starting numbers run into the same chains.",
           "The chain length of x equals 1 + the chain length of f(x), unless x lies on a cycle. Cache the chain length of every value you have fully resolved.",
           "Walk from x, storing the path, until you reach a cached value or repeat a value of the current path. A repeat at path position j means the values from j on form a cycle: each of them gets the cycle length, and each earlier value gets cycle length + its distance to the cycle. A cached value m gives path[i] a length of cache[m] + (path length - i)."],
    editorial=["The values of f for x &le; 100,000 are at most 5 * 9! = 1,814,400, and f of that is at most 7 * 9!, so all chains live in a small set of numbers and each chain is a tail leading into a cycle (the same shape as in the happy number problem, but with more varied cycles).",
               "Resolve values with memoisation. For a start x, follow f and push values on a path while they are neither cached nor already on the path. If the walk stops on a value that is on the path at index j, the path from j is a cycle of length c: store c for all those values, and for each earlier path value at index i store c + (j - i). If it stops on a cached value m, store cache[m] + (len(path) - i) for the path value at index i. Every value is resolved once, so the total work is proportional to the number of distinct values visited. Finally count the x in 1..n with the requested length."],
    time="O(n + V) where V is the number of distinct values reached", space="O(V)",
    solution='''def countFactorialChains(n, length):
    fact = [1, 1, 2, 6, 24, 120, 720, 5040, 40320, 362880]

    def f(x):
        s = 0
        while x:
            x, d = divmod(x, 10)
            s += fact[d]
        return s

    memo = {}
    count = 0
    for x in range(1, n + 1):
        if x not in memo:
            path = []
            pos = {}
            u = x
            while u not in memo and u not in pos:
                pos[u] = len(path)
                path.append(u)
                u = f(u)
            if u in pos:
                j = pos[u]
                c = len(path) - j
                for i in range(j, len(path)):
                    memo[path[i]] = c
                end = j
            else:
                end = len(path)
            for i in range(end - 1, -1, -1):
                nxt_val = f(path[i])
                memo[path[i]] = memo[nxt_val] + 1
        if memo[x] == length:
            count += 1
    return count
''',
    tests=[[200, 1], [1, 1], [10, 1], [145, 1], [100, 3], [1000, 5], [1000, 60], [69, 5], [1000, 3], [50000, 60],
           [100000, 60], [100000, 10], [100000, 2], [99999, 1]],
)


def b_dfc(n, length):
    import math

    def f(x):
        return sum(math.factorial(int(c)) for c in str(x))
    cnt = 0
    for x in range(1, n + 1):
        seen, u = set(), x
        while u not in seen:
            seen.add(u)
            u = f(u)
        if len(seen) == length:
            cnt += 1
    return cnt


def v_dfc(tests):
    for t in tests:
        n, L = t["args"]
        assert 1 <= n <= 100000 and 1 <= L <= 60
    res = {tuple(t["args"]): t["expected"] for t in tests}
    assert res[(200, 1)] == 3 and res[(69, 5)] == b_dfc(69, 5)
    assert any(t["expected"] > 0 for t in tests if t["args"][0] >= 50000)


CHECKS["digit-factorial-chain-count"] = (b_dfc, lambda r: [r.randint(1, 600), r.randint(1, 12)], "exact")
VALIDATE["digit-factorial-chain-count"] = v_dfc


p = add(
    id="first-common-node-of-two-paths", title="First Common Node of Two Paths", diff="Medium", topic=TOPIC,
    fn="firstCommonNode", params=[("nxt", "int[]"), ("a", "int"), ("b", "int")], ret="int", cmp="exact",
    desc="<p><strong>Encoding.</strong> The array <code>nxt</code> describes <code>n</code> nodes <code>0..n-1</code>: from node <code>i</code> you move to node <code>nxt[i]</code>, or the path ends if <code>nxt[i] = -1</code>. The structure has no cycles, so every path ends after finitely many nodes.</p><p>The <em>path</em> of a node is the node itself followed by all nodes you reach by repeatedly following <code>nxt</code> until the end. Return the first node on the path of <code>a</code> that also lies on the path of <code>b</code>, or <code>-1</code> if the two paths share no node. (Since both paths follow the same <code>nxt</code>, once they share a node they share everything after it.)</p><p>Aim for O(n) time and O(1) extra memory by walking two pointers that never need to know the path lengths.</p><p>Example: <code>nxt = [2,2,3,4,-1,4]</code>, <code>a = 0</code>, <code>b = 1</code>: the paths are <code>0,2,3,4</code> and <code>1,2,3,4</code>, so the answer is <code>2</code>. If <code>a = 5</code> and <code>b = 1</code> the paths are <code>5,4</code> and <code>1,2,3,4</code> and the answer is <code>4</code>.</p>",
    constraints=["1 &le; nxt.length &le; 6,000", "-1 &le; nxt[i] &lt; nxt.length", "Following nxt from any node ends after finitely many steps (no cycles)", "0 &le; a, b &lt; nxt.length"],
    hints=["Putting the whole path of one start into a set and walking the other path against it works. How could you avoid the set?",
           "If both paths had the same length you could walk them in lockstep and compare. The trouble is that the part before the common node can have different lengths.",
           "Let pointer p start at a and pointer q at b; each moves one step per round, and when a pointer falls off the end (-1) it continues from the other start. After at most len(path a) + len(path b) + 1 steps both have walked the same total distance, so they stand on the same node (or both on -1)."],
    editorial=["Let the path of a have <code>x</code> nodes before the common part, the path of b have <code>y</code> nodes before it, and the shared part have <code>z</code> nodes (z = 0 if they never meet). Pointer p walks x + z nodes of a's path, jumps to b, and walks y more nodes; pointer q walks y + z nodes of b's path, jumps to a, and walks x more. Both have walked x + y steps before the common part, so they arrive at the first common node in the same round.",
               "If z = 0, both pointers fall off the end after x + y + 2 steps in total and both become -1 at the same moment, so the loop ends with the answer -1 and cannot run forever. The walk takes at most about n + n steps and uses two pointers only. A set based solution is also O(n) time but needs O(n) memory."],
    time="O(n)", space="O(1)",
    solution='''def firstCommonNode(nxt, a, b):
    p, q = a, b
    while p != q:
        p = b if p == -1 else nxt[p]
        q = a if q == -1 else nxt[q]
    return p
''',
    tests=[[[2, 2, 3, 4, -1, 4], 0, 1], [[2, 2, 3, 4, -1, 4], 5, 1], [[-1], 0, 0], [[-1, -1], 0, 1], [[1, -1], 0, 1],
           [[1, -1, 1], 0, 2], [[1, 2, -1, 4, -1], 0, 3], [[1, 2, 3, -1], 0, 0], [[3, 3, 3, -1], 0, 1],
           [[1, 2, 3, -1, 5, 6, 3], 0, 4]],
)


def _two_paths(r, n, la, lb, lc, extra_to_tail=True):
    ids = r.sample(range(n), n)
    A, B = ids[:la], ids[la:la + lb]
    T = ids[la + lb:la + lb + lc]
    rest = ids[la + lb + lc:]
    nxt = [-1] * n
    for chain, tgt in ((A, T), (B, T)):
        for i in range(len(chain) - 1):
            nxt[chain[i]] = chain[i + 1]
        if chain:
            nxt[chain[-1]] = tgt[0] if tgt else -1
    for i in range(len(T) - 1):
        nxt[T[i]] = T[i + 1]
    for x in rest:
        nxt[x] = r.choice(T) if T and extra_to_tail and r.random() < 0.7 else -1
    a = A[0] if A else (T[0] if T else 0)
    b = B[0] if B else (T[0] if T else 0)
    return nxt, a, b, (T[0] if T else -1)


_r = rnd(7109)
for _la, _lb, _lc in ((2500, 1700, 1200), (3000, 10, 1500), (2000, 2000, 0)):
    _nxt, _a, _b, _c = _two_paths(_r, 5000, _la, _lb, _lc)
    p["tests"].append([_nxt, _a, _b])
_nxt, _a, _b, _c = _two_paths(_r, 4000, 0, 2000, 1000)
p["tests"].append([_nxt, _b, _b])


def b_common(nxt, a, b):
    seen, u = set(), b
    while u != -1:
        seen.add(u)
        u = nxt[u]
    u = a
    while u != -1:
        if u in seen:
            return u
        u = nxt[u]
    return -1


def g_common(r):
    n = r.randint(1, 8)
    order = r.sample(range(n), n)
    nxt = [-1] * n
    for k in range(n):
        later = order[k + 1:]
        nxt[order[k]] = r.choice(later + [-1, -1]) if later else -1
    return [nxt, r.randrange(n), r.randrange(n)]


def v_common(tests):
    for t in tests:
        nxt, a, b = t["args"]
        n = len(nxt)
        assert 1 <= n <= 6000 and all(-1 <= v < n for v in nxt) and 0 <= a < n and 0 <= b < n
        for start in (a, b):  # acyclic
            u, steps = start, 0
            while u != -1:
                u = nxt[u]
                steps += 1
                assert steps <= n, "cycle"
        assert t["expected"] == b_common(nxt, a, b)
    assert any(t["expected"] == -1 for t in tests) and any(t["expected"] != -1 for t in tests)


CHECKS["first-common-node-of-two-paths"] = (b_common, g_common, "exact")
VALIDATE["first-common-node-of-two-paths"] = v_common


p = add(
    id="distinct-nodes-visited-from-each-start", title="Distinct Nodes Visited From Each Start", diff="Hard", topic=TOPIC,
    fn="visitedCounts", params=[("nxt", "int[]")], ret="int[]", cmp="exact",
    desc=SUCC + "<p>For every position <code>s</code>, imagine a walker that starts at <code>s</code> and takes steps along <code>nxt</code> for ever. Let <code>ans[s]</code> be the number of <em>different</em> positions the walker visits, counting <code>s</code> itself.</p><p>Return the array <code>ans</code> of length <code>n</code>.</p><p>Example: <code>nxt = [1,2,0,2,3]</code>. Position 0 visits <code>0,1,2</code> (3 positions), position 3 visits <code>3,2,0,1</code> (4), position 4 visits <code>4,3,2,0,1</code> (5), so the answer is <code>[3,3,3,4,5]</code>. A position with <code>nxt[i] = i</code> only visits itself, so its value is <code>1</code>.</p>",
    constraints=["1 &le; nxt.length &le; 6,000", "0 &le; nxt[i] &lt; nxt.length"],
    hints=["Walking from every start separately with a visited set costs O(n<sup>2</sup>) in the worst case. The answers of different starts are strongly related.",
           "A position on a cycle visits exactly the cycle, so its answer is the cycle length. A position off the cycle visits itself plus everything its successor visits: ans[i] = 1 + ans[nxt[i]].",
           "Walk from each unfinished start, recording the path. If the walk runs into the path itself, the closed part is a new cycle: give all of its positions the cycle length. Then fill the rest of the path backwards using ans[i] = 1 + ans[nxt[i]]. Positions that are already finished stop a walk immediately."],
    editorial=["Every position has one outgoing step, so each walk is a tail that leads into a cycle (the 'rho' shape). The number of distinct positions visited is tail length plus cycle length, and for cycle positions it is just the cycle length.",
               "Use states: 0 unseen, 1 on the current path, 2 finished. For an unfinished start, follow nxt and push positions on a path until you reach a position that is not state 0. If that position is on the current path (state 1) at index j, the positions path[j:] form a cycle of length <code>len(path) - j</code>: set their answer to it and mark them finished. Whatever remains in the path before the cycle (or the whole path, if you stopped on a finished position) is processed from the end backwards with <code>ans[v] = ans[nxt[v]] + 1</code>. Each position enters a path exactly once, so the algorithm is O(n) time and O(n) memory. The cycle detection can use Floyd's slow/fast pointers instead of the state array, but the path-recording variant gives all answers in one sweep."],
    time="O(n)", space="O(n)",
    solution='''def visitedCounts(nxt):
    n = len(nxt)
    ans = [0] * n
    state = [0] * n  # 0 unseen, 1 on current path, 2 finished
    for s in range(n):
        if state[s]:
            continue
        path = []
        u = s
        while state[u] == 0:
            state[u] = 1
            path.append(u)
            u = nxt[u]
        if state[u] == 1:
            j = path.index(u)
            c = len(path) - j
            for v in path[j:]:
                ans[v] = c
                state[v] = 2
            del path[j:]
        for v in reversed(path):
            ans[v] = ans[nxt[v]] + 1
            state[v] = 2
    return ans
''',
    tests=[[[1, 2, 0, 2, 3]], [[0]], [[1, 0]], [[0, 0, 1, 2]], [[1, 2, 3, 4, 0]], [[1, 1, 1, 1]], [[1, 2, 3, 3]],
           [[2, 2, 3, 4, 2, 4]], [[1, 0, 1, 2, 3, 4]]],
)
_r = rnd(7110)
_n = 2600
p["tests"].append([[_r.randrange(_n) for _ in range(_n)]])
_perm = _r.sample(range(_n), _n)
_nx = [0] * _n
for _i in range(_n):
    _nx[_perm[_i]] = _perm[(_i + 1) % _n]
p["tests"].append([_nx])
_nx = [0] * _n
for _i in range(_n - 1):
    _nx[_perm[_i]] = _perm[_i + 1]
_nx[_perm[-1]] = _perm[-2]                                  # long tail into a 2-cycle
p["tests"].append([_nx])
_nx[_perm[-1]] = _perm[-1]                                  # long tail into a self loop
p["tests"].append([_nx])


def b_visited(nxt):
    out = []
    for s in range(len(nxt)):
        seen, u = set(), s
        while u not in seen:
            seen.add(u)
            u = nxt[u]
        out.append(len(seen))
    return out


def v_visited(tests):
    for t in tests:
        nxt = t["args"][0]
        assert 1 <= len(nxt) <= 6000 and all(0 <= v < len(nxt) for v in nxt)
        if len(nxt) <= 1000:
            assert t["expected"] == b_visited(nxt)
        else:
            assert max(t["expected"]) <= len(nxt) and min(t["expected"]) >= 1
    assert any(max(t["expected"]) > 2000 for t in tests)


CHECKS["distinct-nodes-visited-from-each-start"] = (b_visited, lambda r: [[r.randrange(n) for n in [r.randint(1, 9)] for _ in range(n)]], "exact")
VALIDATE["distinct-nodes-visited-from-each-start"] = v_visited
