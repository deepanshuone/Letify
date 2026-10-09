"""Problems: greedy (second batch). See data/lib.py for the registry."""
from itertools import combinations, permutations

from lib import add, rnd, CHECKS, VALIDATE, gen_arr  # noqa: F401

INT_MIN, INT_MAX = -(2 ** 31), 2 ** 31 - 1


# ---------------------------------------------------------------- EASY

p = add(
    id="assign-cookies", title="Assign Cookies", diff="Easy", topic="Greedy",
    fn="findContentChildren", params=[("g", "int[]"), ("s", "int[]")], ret="int", cmp="exact",
    desc="<p>You are handing out cookies. Child <code>i</code> has a greed factor <code>g[i]</code>: the smallest cookie size that makes that child content. Cookie <code>j</code> has size <code>s[j]</code>.</p><p>A cookie can be given to a child only if <code>s[j] &ge; g[i]</code>. Each child receives at most one cookie and each cookie goes to at most one child. Return the maximum number of children that can be made content.</p><pre>g = [1, 2, 3], s = [1, 1]      -> 1\ng = [1, 2], s = [1, 2, 3]      -> 2</pre>",
    constraints=["0 &le; g.length, s.length &le; 10,000", "1 &le; g[i], s[j] &le; 2<sup>31</sup> - 1"],
    hints=["Every cookie that is used should make exactly one child content. Which child should the smallest cookie go to?",
           "Sort both arrays. The least greedy child is the easiest to satisfy, so try them first.",
           "Walk through the cookies from smallest to largest with a pointer into the sorted children. If the cookie is big enough for the current child, give it and advance the child pointer; otherwise the cookie is useless to everyone remaining, so discard it."],
    editorial=["Sort the greed factors and the cookie sizes. Scan the cookies in increasing order and keep a pointer <code>i</code> to the least greedy child still without a cookie. If <code>s[j] &ge; g[i]</code>, give the cookie to that child and move <code>i</code> forward. Otherwise this cookie is too small for every remaining child (they are all at least as greedy), so skip it.",
               "The exchange argument: if an optimal solution gives the smallest usable cookie to a different child, swap it to the least greedy child; that child accepts it and nobody gets worse off. The answer is the final value of <code>i</code>. Sorting dominates the cost."],
    time="O(n log n + m log m)", space="O(1) extra (ignoring sort)",
    solution='''def findContentChildren(g, s):
    g = sorted(g)
    s = sorted(s)
    i = 0
    for size in s:
        if i < len(g) and size >= g[i]:
            i += 1
    return i
''',
    tests=[[[1, 2, 3], [1, 1]], [[1, 2], [1, 2, 3]], [[], [1, 2]], [[5], []], [[], []], [[3], [3]], [[3], [2]],
           [[10, 9, 8, 7], [5, 6, 7, 8]], [[1, 1, 1], [1, 1, 1, 1]], [[2, 2, 2], [1, 3]],
           [[INT_MAX, 1], [INT_MAX, INT_MAX]]],
)
_r = rnd(2001)
p["tests"].append([[_r.randint(1, 1000) for _ in range(9000)], [_r.randint(1, 1000) for _ in range(10000)]])
p["tests"].append([[_r.randint(1, INT_MAX) for _ in range(10000)], [_r.randint(1, INT_MAX) for _ in range(7000)]])
p["tests"].append([list(range(1, 10001)), list(range(10000, 0, -1))])
p["tests"].append([[500] * 10000, [499] * 5000 + [500] * 3000])


def b_cookies(g, s):
    best = 0

    def go(i, used, cnt):
        nonlocal best
        best = max(best, cnt)
        if i == len(g):
            return
        go(i + 1, used, cnt)  # child i gets nothing
        for j in range(len(s)):
            if not (used >> j) & 1 and s[j] >= g[i]:
                go(i + 1, used | (1 << j), cnt + 1)

    go(0, 0, 0)
    return best


def v_cookies(tests):
    for t in tests:
        g, s = t["args"]
        assert len(g) <= 10000 and len(s) <= 10000
        assert all(1 <= x <= INT_MAX for x in g + s)


CHECKS["assign-cookies"] = (b_cookies, lambda r: [[r.randint(1, 6) for _ in range(r.randint(0, 6))], [r.randint(1, 6) for _ in range(r.randint(0, 6))]], "exact")
VALIDATE["assign-cookies"] = v_cookies


p = add(
    id="lemonade-change-stand", title="Lemonade Stand Change", diff="Easy", topic="Greedy",
    fn="lemonadeChange", params=[("bills", "int[]")], ret="bool", cmp="exact",
    desc="<p>A lemonade stand sells one cup for <code>5</code> dollars. Customers queue up and each buys exactly one cup, paying with a single bill of <code>5</code>, <code>10</code> or <code>20</code> dollars. The array <code>bills</code> gives the bill each customer pays with, in queue order.</p><p>You start with no money at all and must give every customer the correct change immediately, using only bills you have collected from earlier customers. Return <code>true</code> if you can serve everyone, otherwise <code>false</code>.</p><pre>[5, 5, 5, 10, 20]  -> true\n[5, 5, 10, 10, 20] -> false</pre><p>In the second example, after the two 10s you hold no 5-dollar bill, so the final customer cannot get 15 dollars back.</p>",
    constraints=["1 &le; bills.length &le; 10,000", "bills[i] is 5, 10 or 20"],
    hints=["Track how many 5-dollar and 10-dollar bills you currently hold. A 20 never helps with change, so it need not be tracked.",
           "A 5 needs no change, a 10 needs one 5 back. A 20 needs 15 back, which can be made as 10 + 5 or as 5 + 5 + 5.",
           "When a 20 arrives, prefer to give back 10 + 5 if possible: fives are more flexible than tens (they are needed for both 10 and 20 customers), so keep them."],
    editorial=["Keep two counters, <code>fives</code> and <code>tens</code>. For a 5 just increment <code>fives</code>. For a 10 you need a five back: decrement <code>fives</code> (fail if none) and increment <code>tens</code>. For a 20 you need 15 back: use a ten and a five if you have them, otherwise three fives, otherwise fail.",
               "The greedy choice is to spend a ten before spending fives. A ten can only ever be used as change for a 20, whereas a five can be used for both 10s and 20s, so using the less flexible bill first can never hurt. Each customer is handled in O(1)."],
    time="O(n)", space="O(1)",
    solution='''def lemonadeChange(bills):
    fives = tens = 0
    for b in bills:
        if b == 5:
            fives += 1
        elif b == 10:
            if fives == 0:
                return False
            fives -= 1
            tens += 1
        else:
            if tens > 0 and fives > 0:
                tens -= 1
                fives -= 1
            elif fives >= 3:
                fives -= 3
            else:
                return False
    return True
''',
    tests=[[[5, 5, 5, 10, 20]], [[5, 5, 10, 10, 20]], [[5]], [[10]], [[20]], [[5, 20]], [[5, 5, 5, 20]],
           [[5, 10, 5, 20]], [[5, 5, 10, 20, 5, 20]], [[5, 5, 5, 10, 10, 20, 20]], [[5, 5, 10, 10, 20]]],
)
_r = rnd(2002)


def _lemon_valid(r, n):
    fives = tens = 0
    out = []
    for _ in range(n):
        opts = [5]
        if fives:
            opts.append(10)
        if (fives and tens) or fives >= 3:
            opts.append(20)
        b = r.choice(opts if r.random() < 0.6 else [5] + opts)
        out.append(b)
        if b == 5:
            fives += 1
        elif b == 10:
            fives -= 1; tens += 1
        elif fives and tens:
            fives -= 1; tens -= 1
        else:
            fives -= 3
    return out


_a = _lemon_valid(_r, 10000)
p["tests"].append([_a])
p["tests"].append([_a[:-1] + [20] * 1])  # likely false near the end
p["tests"].append([[5] * 5000 + [10] * 2500 + [20] * 2500])  # exactly enough? true
p["tests"].append([[5] * 5000 + [10] * 2501 + [20] * 2499])
p["tests"].append([[5, 10] * 4999 + [20, 20]])


def b_lemon(bills):
    def go(i, f, t):
        if i == len(bills):
            return True
        b = bills[i]
        if b == 5:
            return go(i + 1, f + 1, t)
        if b == 10:
            return f >= 1 and go(i + 1, f - 1, t + 1)
        if f >= 1 and t >= 1 and go(i + 1, f - 1, t - 1):
            return True
        return f >= 3 and go(i + 1, f - 3, t)

    return go(0, 0, 0)


def v_lemon(tests):
    for t in tests:
        b = t["args"][0]
        assert 1 <= len(b) <= 10000 and all(x in (5, 10, 20) for x in b)
    res = [t["expected"] for t in tests]
    assert True in res and False in res


CHECKS["lemonade-change-stand"] = (b_lemon, lambda r: [[r.choice([5, 5, 10, 20]) for _ in range(r.randint(1, 10))]], "exact")
VALIDATE["lemonade-change-stand"] = v_lemon


p = add(
    id="maximum-units-on-a-truck", title="Maximum Units on a Truck", diff="Easy", topic="Greedy",
    fn="maximumUnits", params=[("boxTypes", "int[][]"), ("truckSize", "int")], ret="int", cmp="exact",
    desc="<p>A warehouse stocks several kinds of boxes. The entry <code>boxTypes[i] = [count, units]</code> says there are <code>count</code> identical boxes of type <code>i</code>, and each of them holds <code>units</code> items.</p><p>A truck can carry at most <code>truckSize</code> boxes in total, of any types. Return the maximum total number of items you can load.</p><pre>boxTypes = [[1, 3], [2, 2], [3, 1]], truckSize = 4 -> 8</pre><p>Here take the one box of 3 items and both boxes of 2 items, plus one box of 1 item: 3 + 4 + 1 = 8.</p>",
    constraints=["1 &le; boxTypes.length &le; 1,000", "1 &le; count, units &le; 1,000", "1 &le; truckSize &le; 1,000,000"],
    hints=["The truck is limited by the number of boxes, not by weight. All that matters is how many items each box holds.",
           "If you could only pick one more box, which would you pick? The one with the most items.",
           "Sort the box types by units per box in descending order and take as many boxes of each type as still fit, stopping when the truck is full."],
    editorial=["Because every box takes the same single slot on the truck, a box with more items is never worse than one with fewer. Sort the types by <code>units</code> descending. For each type, load <code>min(count, remaining)</code> boxes, add <code>that * units</code> to the total and reduce the remaining capacity; stop when it reaches zero.",
               "An exchange argument proves it: if a loaded box has fewer items than an unloaded one, swapping them keeps the box count the same and does not decrease the total. The sort costs O(k log k) for k box types, and the answer is at most 10<sup>6</sup> &times; 1,000 = 10<sup>9</sup>, which fits in 32 bits."],
    time="O(k log k)", space="O(1) extra",
    solution='''def maximumUnits(boxTypes, truckSize):
    total = 0
    for count, units in sorted(boxTypes, key=lambda b: -b[1]):
        take = min(count, truckSize)
        total += take * units
        truckSize -= take
        if truckSize == 0:
            break
    return total
''',
    tests=[[[[1, 3], [2, 2], [3, 1]], 4], [[[5, 10], [2, 5], [4, 7], [3, 9]], 10], [[[1, 1]], 1], [[[1, 1]], 5],
           [[[3, 4]], 2], [[[1000, 1000]], 1000000], [[[2, 5], [2, 5], [2, 5]], 3], [[[1, 1], [1, 2], [1, 3], [1, 4]], 2],
           [[[10, 1], [10, 2]], 15]],
)
_r = rnd(2003)
p["tests"].append([[[_r.randint(1, 1000), _r.randint(1, 1000)] for _ in range(1000)], 300000])
p["tests"].append([[[_r.randint(1, 1000), _r.randint(1, 1000)] for _ in range(1000)], 1000000])
p["tests"].append([[[1000, 1000] for _ in range(1000)], 1000000])
p["tests"].append([[[_r.randint(1, 1000), _r.randint(1, 1000)] for _ in range(1000)], 1])


def b_units(boxTypes, truckSize):
    # bounded knapsack over the number of boxes loaded
    NEG = -1
    dp = [NEG] * (truckSize + 1)
    dp[0] = 0
    for count, units in boxTypes:
        nd = dp[:]
        for used in range(truckSize + 1):
            if dp[used] < 0:
                continue
            for k in range(1, count + 1):
                if used + k > truckSize:
                    break
                nd[used + k] = max(nd[used + k], dp[used] + k * units)
        dp = nd
    return max(dp)


def g_units(r):
    return [[[r.randint(1, 5), r.randint(1, 9)] for _ in range(r.randint(1, 5))], r.randint(1, 14)]


def v_units(tests):
    for t in tests:
        bt, ts = t["args"]
        assert 1 <= len(bt) <= 1000 and 1 <= ts <= 1000000
        assert all(len(b) == 2 and 1 <= b[0] <= 1000 and 1 <= b[1] <= 1000 for b in bt)


CHECKS["maximum-units-on-a-truck"] = (b_units, g_units, "exact")
VALIDATE["maximum-units-on-a-truck"] = v_units


# ---------------------------------------------------------------- MEDIUM

p = add(
    id="partition-labels-greedy", title="Partition Labels", diff="Medium", topic="Greedy",
    fn="partitionLabels", params=[("s", "string")], ret="int[]", cmp="exact",
    desc="<p>Split the lowercase string <code>s</code> into as many contiguous pieces as possible so that every letter appears in <strong>at most one</strong> piece. Joining the pieces in order must give back <code>s</code>.</p><p>Return the lengths of the pieces, from left to right.</p><pre>s = \"ababcbacadefegdehijhklij\" -> [9, 7, 8]\ns = \"eccbbbbdec\"              -> [10]</pre><p>The first example splits as <code>ababcbaca | defegde | hijhklij</code>.</p>",
    constraints=["1 &le; s.length &le; 10,000", "s contains only lowercase English letters"],
    hints=["If a piece contains a letter, it must also contain every other occurrence of that letter.",
           "Record the last index where each letter occurs.",
           "Scan left to right keeping the furthest last-occurrence seen in the current piece. When the scan index reaches that furthest position, the piece can be cut there."],
    editorial=["First compute <code>last[c]</code>, the final index of each letter. Then sweep with index <code>i</code>, maintaining <code>end</code> = the largest <code>last[s[i]]</code> over the current piece. Starting a piece at <code>start</code>, every character we pass forces the piece to extend at least to its last occurrence. When <code>i == end</code>, no letter in the piece occurs later, so we close the piece with length <code>end - start + 1</code> and start a new one.",
               "Cutting as early as possible yields the maximum number of pieces, and the partition is unique: a position is a valid cut exactly when no letter appears on both sides of it. The algorithm is a single pass after the O(n) preprocessing, with a table of just 26 entries."],
    time="O(n)", space="O(1)",
    solution='''def partitionLabels(s):
    last = {c: i for i, c in enumerate(s)}
    result = []
    start = end = 0
    for i, c in enumerate(s):
        end = max(end, last[c])
        if i == end:
            result.append(end - start + 1)
            start = i + 1
    return result
''',
    tests=[["ababcbacadefegdehijhklij"], ["eccbbbbdec"], ["a"], ["abc"], ["aaaa"], ["abab"], ["abcabc"], ["abacbd"],
           ["zyxwvutsrqponmlkjihgfedcbaabcdefghijklmnopqrstuvwxyz"], ["qiejxqfnqceocmy"]],
)
_r = rnd(2004)


def _label_str(r, n, blocks):
    letters = list("abcdefghijklmnopqrstuvwxyz")
    r.shuffle(letters)
    blocks = min(blocks, 26)
    cuts = sorted(r.sample(range(1, n), blocks - 1)) if blocks > 1 else []
    sizes = [b - a for a, b in zip([0] + cuts, cuts + [n])]
    out = []
    for i, sz in enumerate(sizes):
        group = letters[i::blocks] or [letters[i % 26]]
        out.append("".join(r.choice(group) for _ in range(sz)))
    return "".join(out)


p["tests"].append([_label_str(_r, 10000, 26)])
p["tests"].append([_label_str(_r, 10000, 5)])
p["tests"].append(["".join(_r.choice("abcdefghijklmnopqrstuvwxyz") for _ in range(10000))])
p["tests"].append(["a" + "b" * 9998 + "a"])
p["tests"].append(["".join(chr(97 + i) * 300 for i in range(26)) + "z" * 100])


def b_labels(s):
    n = len(s)
    out = []
    prev = 0
    for cut in range(1, n + 1):
        if cut == n or not (set(s[:cut]) & set(s[cut:])):
            out.append(cut - prev)
            prev = cut
    return out


def g_labels(r):
    return ["".join(r.choice("abcdef"[:r.randint(1, 6)]) for _ in range(r.randint(1, 14)))]


def v_labels(tests):
    for t in tests:
        s = t["args"][0]
        assert 1 <= len(s) <= 10000 and all("a" <= c <= "z" for c in s)
        assert sum(t["expected"]) == len(s)


CHECKS["partition-labels-greedy"] = (b_labels, g_labels, "exact")
VALIDATE["partition-labels-greedy"] = v_labels


p = add(
    id="queue-reconstruction-by-height", title="Queue Reconstruction by Height", diff="Medium", topic="Greedy",
    fn="reconstructQueue", params=[("people", "int[][]")], ret="int[][]", cmp="exact",
    desc="<p>People have lined up in a queue, but the queue was scrambled. Each person is described by <code>[h, k]</code>: their height <code>h</code>, and the number <code>k</code> of people standing <strong>in front of them</strong> whose height is greater than or equal to <code>h</code>.</p><p>The array <code>people</code> lists everyone in arbitrary order. Rebuild the original queue and return the people from the front of the queue to the back. The input always comes from a real queue, and the reconstructed queue is unique.</p><pre>people = [[7,0],[4,4],[7,1],[5,0],[6,1],[5,2]]\n-> [[5,0],[7,0],[5,2],[6,1],[4,4],[7,1]]</pre>",
    constraints=["1 &le; people.length &le; 2,000", "1 &le; h &le; 1,000,000", "0 &le; k &lt; people.length", "The input describes a valid queue"],
    hints=["Think about the tallest people first: nobody taller stands in front of them, so their k is an exact position within their own height group.",
           "Process people from tallest to shortest. When a person is placed, everyone already placed is at least as tall, so k is exactly the number of people ahead that count.",
           "Sort by height descending, and by k ascending within equal heights. Insert each person into a result list at index k. Shorter people inserted later never disturb the k of taller ones."],
    editorial=["Sort the people by height descending and, for equal height, by <code>k</code> ascending. Start with an empty list and insert each person at index <code>k</code>. When we insert a person of height <code>h</code>, every person already in the list is at least as tall, so the person's <code>k</code> is exactly how many of them must be in front, i.e. index <code>k</code>.",
               "Later insertions are of people who are not taller, so they do not count toward the <code>k</code> of anyone already in the list, and shifting taller people to the right keeps their relative counts intact. With equal heights, ascending <code>k</code> ensures the person with a smaller <code>k</code> is already in place before the next one is inserted. List insertion makes this O(n<sup>2</sup>) in the worst case, which is fine for n &le; 2,000."],
    time="O(n^2)", space="O(n)",
    solution='''def reconstructQueue(people):
    queue = []
    for h, k in sorted(people, key=lambda x: (-x[0], x[1])):
        queue.insert(k, [h, k])
    return queue
''',
    tests=[[[[7, 0], [4, 4], [7, 1], [5, 0], [6, 1], [5, 2]]], [[[6, 0], [5, 0], [4, 0], [3, 2], [2, 2], [1, 4]]],
           [[[1, 0]]], [[[3, 0], [3, 1], [3, 2]]], [[[1, 0], [1, 1], [1, 2], [1, 3]]], [[[9, 0], [8, 0], [7, 0]]],
           [[[1, 2], [2, 1], [3, 0]]], [[[5, 1], [5, 0]]], [[[1000000, 0], [1, 1], [1000000, 1]]]],
)
_r = rnd(2005)


def _make_queue(r, n, hmax):
    hs = [r.randint(1, hmax) for _ in range(n)]
    people = [[h, sum(1 for x in hs[:i] if x >= h)] for i, h in enumerate(hs)]
    r.shuffle(people)
    return people


p["tests"].append([_make_queue(_r, 2000, 50)])
p["tests"].append([_make_queue(_r, 2000, 1000000)])
p["tests"].append([_make_queue(_r, 2000, 3)])
p["tests"].append([_make_queue(_r, 1500, 1)])


def b_queue(people):
    # exhaustive: try every ordering and keep the (unique) valid one
    found = []
    for perm in permutations(people):
        if all(sum(1 for q in perm[:i] if q[0] >= perm[i][0]) == perm[i][1] for i in range(len(perm))):
            found.append([list(x) for x in perm])
    assert len(found) == 1, "queue not unique"
    return found[0]


def g_queue(r):
    return [_make_queue(r, r.randint(1, 7), r.randint(1, 6))]


def v_queue(tests):
    for t in tests:
        people = t["args"][0]
        n = len(people)
        assert 1 <= n <= 2000
        assert all(1 <= h <= 1000000 and 0 <= k < n for h, k in people)
        assert len({tuple(x) for x in people}) == n
        q = t["expected"]
        assert sorted(map(tuple, q)) == sorted(map(tuple, people))
        assert all(sum(1 for x in q[:i] if x[0] >= q[i][0]) == q[i][1] for i in range(n))


CHECKS["queue-reconstruction-by-height"] = (b_queue, g_queue, "exact")
VALIDATE["queue-reconstruction-by-height"] = v_queue


p = add(
    id="two-city-scheduling-cost", title="Two City Interviews", diff="Medium", topic="Greedy",
    fn="twoCitySchedCost", params=[("costs", "int[][]")], ret="int", cmp="exact",
    desc="<p>A company is flying <code>2n</code> candidates in for interviews. The entry <code>costs[i] = [a, b]</code> is the price to send candidate <code>i</code> to city A (<code>a</code>) or to city B (<code>b</code>).</p><p>Exactly <code>n</code> candidates must go to each city. Return the minimum total cost.</p><pre>costs = [[10,20],[30,200],[400,50],[30,20]] -> 110</pre><p>Send the first two to city A (10 + 30) and the last two to city B (50 + 20).</p>",
    constraints=["2 &le; costs.length &le; 10,000 and costs.length is even", "1 &le; a, b &le; 10,000"],
    hints=["Imagine first sending everyone to city A. Then you must move exactly half of the candidates to B.",
           "Moving candidate <code>i</code> from A to B changes the total by <code>b - a</code>. You want the n most negative (or smallest) changes.",
           "Sort the candidates by <code>a - b</code>. The first n (those who prefer A most strongly) go to A; the remaining n go to B."],
    editorial=["Let <code>diff = a - b</code>. Sending a candidate to A instead of B costs <code>diff</code> more (negative means A is cheaper). The total cost equals <code>sum(b) + sum of diff over the group sent to A</code>. Since the group sent to A has exactly n candidates, we minimise by choosing the n candidates with the smallest <code>a - b</code>.",
               "So sort by <code>a - b</code>, send the first n to A and the last n to B, and add up. If two candidates have the same difference, either assignment gives the same total. Sorting costs O(n log n), and the answer is at most 10,000 &times; 10,000 = 10<sup>8</sup>."],
    time="O(n log n)", space="O(1) extra",
    solution='''def twoCitySchedCost(costs):
    order = sorted(costs, key=lambda c: c[0] - c[1])
    n = len(costs) // 2
    return sum(c[0] for c in order[:n]) + sum(c[1] for c in order[n:])
''',
    tests=[[[[10, 20], [30, 200], [400, 50], [30, 20]]], [[[259, 770], [448, 54], [926, 667], [184, 139], [840, 118], [577, 469]]],
           [[[1, 1], [1, 1]]], [[[5, 1], [1, 5]]], [[[1, 10000], [1, 10000], [10000, 1], [10000, 1]]],
           [[[10000, 1], [10000, 1], [1, 10000], [1, 10000]]], [[[3, 3], [3, 3], [3, 3], [3, 3]]],
           [[[1, 2], [2, 3], [3, 4], [4, 5]]], [[[5, 4], [4, 3], [3, 2], [2, 1]]]],
)
_r = rnd(2006)
p["tests"].append([[[_r.randint(1, 10000), _r.randint(1, 10000)] for _ in range(10000)]])
p["tests"].append([[[_r.randint(1, 10000), _r.randint(1, 10000)] for _ in range(9998)]])
p["tests"].append([[[10000, 10000] for _ in range(10000)]])
p["tests"].append([[[_r.randint(1, 100), _r.randint(9900, 10000)] for _ in range(5000)] + [[_r.randint(9900, 10000), _r.randint(1, 100)] for _ in range(5000)]])


def b_two_city(costs):
    m = len(costs)
    best = None
    for group in combinations(range(m), m // 2):
        gs = set(group)
        total = sum(costs[i][0] if i in gs else costs[i][1] for i in range(m))
        if best is None or total < best:
            best = total
    return best


def g_two_city(r):
    return [[[r.randint(1, 12), r.randint(1, 12)] for _ in range(2 * r.randint(1, 5))]]


def v_two_city(tests):
    for t in tests:
        c = t["args"][0]
        assert 2 <= len(c) <= 10000 and len(c) % 2 == 0
        assert all(len(x) == 2 and 1 <= x[0] <= 10000 and 1 <= x[1] <= 10000 for x in c)


CHECKS["two-city-scheduling-cost"] = (b_two_city, g_two_city, "exact")
VALIDATE["two-city-scheduling-cost"] = v_two_city


p = add(
    id="wiggle-subsequence-length", title="Longest Wiggle Subsequence", diff="Medium", topic="Greedy",
    fn="wiggleMaxLength", params=[("nums", "int[]")], ret="int", cmp="exact",
    desc="<p>A sequence is a <em>wiggle</em> if the differences between consecutive elements are non-zero and strictly alternate in sign (up, down, up, ... or down, up, down, ...). A sequence with one element is a wiggle, and a sequence of two elements is a wiggle when the two elements differ.</p><p>Given <code>nums</code>, return the length of its longest subsequence that is a wiggle. A subsequence keeps the original order but may skip elements.</p><pre>[1, 7, 4, 9, 2, 5]           -> 6\n[1, 17, 5, 10, 13, 15, 10, 5, 16, 8] -> 7\n[1, 2, 3, 4, 5, 6, 7, 8, 9]  -> 2</pre>",
    constraints=["1 &le; nums.length &le; 10,000", "-10<sup>9</sup> &le; nums[i] &le; 10<sup>9</sup>"],
    hints=["A dynamic programming solution tracks the best wiggle ending at each index with an up-move or a down-move. Can you simplify it?",
           "In a long climb, only the first and last element of the climb matter; the middle ones contribute nothing a wiggle can use.",
           "Count the number of sign changes in the sequence of non-zero differences. Keep the last non-zero direction, and add one to the length each time the direction flips."],
    editorial=["Keep two values: <code>up</code>, the length of the longest wiggle seen so far that ends with an upward step, and <code>down</code>, the same for a downward step. For each new element, if it is greater than the previous one, a wiggle ending with a down-step can be extended: <code>up = down + 1</code>. If it is smaller, <code>down = up + 1</code>. Equal elements change nothing. The answer is <code>max(up, down)</code>, with both starting at 1.",
               "This works because each maximal monotone run can be replaced by its two endpoints without losing any wiggle length, so the answer is one more than the number of direction changes in the non-zero differences (or 1 if there are none)."],
    time="O(n)", space="O(1)",
    solution='''def wiggleMaxLength(nums):
    up = down = 1
    for i in range(1, len(nums)):
        if nums[i] > nums[i - 1]:
            up = down + 1
        elif nums[i] < nums[i - 1]:
            down = up + 1
    return max(up, down)
''',
    tests=[[[1, 7, 4, 9, 2, 5]], [[1, 17, 5, 10, 13, 15, 10, 5, 16, 8]], [[1, 2, 3, 4, 5, 6, 7, 8, 9]], [[5]], [[3, 3]],
           [[3, 4]], [[4, 3]], [[2, 2, 2, 2]], [[1, 1, 7, 7, 4, 4, 9, 9]], [[0, 0, 0, 5, 5, 5, 1, 1]], [[-1000000000, 1000000000, -1000000000]]],
)
_r = rnd(2007)
p["tests"].append([[_r.randint(-1000000000, 1000000000) for _ in range(10000)]])
p["tests"].append([[_r.randint(-3, 3) for _ in range(10000)]])
p["tests"].append([list(range(10000))])
p["tests"].append([[(i % 2) * 1000000000 for i in range(10000)]])
p["tests"].append([[i // 3 for i in range(10000)]])


def b_wiggle(nums):
    n = len(nums)
    best = 0
    for mask in range(1, 1 << n):
        sub = [nums[i] for i in range(n) if (mask >> i) & 1]
        ok = True
        for i in range(1, len(sub)):
            if sub[i] == sub[i - 1]:
                ok = False
                break
            if i >= 2 and (sub[i] - sub[i - 1] > 0) == (sub[i - 1] - sub[i - 2] > 0):
                ok = False
                break
        if ok:
            best = max(best, len(sub))
    return best


def v_wiggle(tests):
    for t in tests:
        a = t["args"][0]
        assert 1 <= len(a) <= 10000
        assert all(-10 ** 9 <= x <= 10 ** 9 for x in a)


CHECKS["wiggle-subsequence-length"] = (b_wiggle, lambda r: [gen_arr(r, -5, 5, 1, 10)], "exact")
VALIDATE["wiggle-subsequence-length"] = v_wiggle


p = add(
    id="hand-of-straights-groups", title="Hand of Straights", diff="Medium", topic="Greedy",
    fn="isNStraightHand", params=[("hand", "int[]"), ("groupSize", "int")], ret="bool", cmp="exact",
    desc="<p>You hold a hand of cards, where <code>hand[i]</code> is the number written on card <code>i</code>. You want to rearrange <em>all</em> the cards into groups of exactly <code>groupSize</code> cards each, where every group consists of consecutive numbers (for example <code>4, 5, 6</code>).</p><p>Return <code>true</code> if this is possible, otherwise <code>false</code>.</p><pre>hand = [1,2,3,6,2,3,4,7,8], groupSize = 3 -> true   ([1,2,3] [2,3,4] [6,7,8])\nhand = [1,2,3,4,5],         groupSize = 4 -> false</pre>",
    constraints=["1 &le; hand.length &le; 10,000", "0 &le; hand[i] &le; 10<sup>9</sup>", "1 &le; groupSize &le; hand.length"],
    hints=["If the length is not divisible by groupSize, the answer is immediately false.",
           "Look at the smallest card still in hand. Which group can it possibly belong to?",
           "The smallest remaining card must start a group, because no smaller card is left to precede it. Repeatedly take the smallest card <code>x</code>, remove one each of <code>x, x+1, ..., x+groupSize-1</code>, and fail if any is missing."],
    editorial=["Count how many cards there are of each number. The smallest remaining number <code>x</code> cannot be the second or later member of a group (that would need a smaller card), so it must be the first member of some group. Therefore the group is forced: <code>x, x+1, ..., x+g-1</code>. Remove one of each; if any is missing the answer is false. Repeat until the hand is empty.",
               "Iterate over the distinct numbers in sorted order. If <code>cnt[x] = c &gt; 0</code>, then <code>c</code> groups must start at <code>x</code>, so subtract <code>c</code> from each of <code>cnt[x..x+g-1]</code> and verify none goes negative. Each distinct number is handled once, for O(n log n + n) overall, or O(n * groupSize) in the simplest per-card form."],
    time="O(n log n)", space="O(n)",
    solution='''def isNStraightHand(hand, groupSize):
    if len(hand) % groupSize:
        return False
    cnt = {}
    for x in hand:
        cnt[x] = cnt.get(x, 0) + 1
    for x in sorted(cnt):
        c = cnt[x]
        if c == 0:
            continue
        for y in range(x, x + groupSize):
            if cnt.get(y, 0) < c:
                return False
            cnt[y] -= c
    return True
''',
    tests=[[[1, 2, 3, 6, 2, 3, 4, 7, 8], 3], [[1, 2, 3, 4, 5], 4], [[5], 1], [[5, 5, 5], 1], [[1, 2], 2], [[1, 3], 2],
           [[1, 1, 2, 2, 3, 3], 3], [[1, 1, 2, 2, 3, 4], 3], [[0, 0, 1, 1, 2, 2], 2], [[8, 10, 12], 3],
           [[1, 2, 3, 4, 5, 6], 2], [[1, 2, 3, 3, 4, 5, 6, 7], 4]],
)
_r = rnd(2008)


def _straights(r, groups, g, spread):
    hand = []
    for _ in range(groups):
        s = r.randint(0, spread)
        hand.extend(range(s, s + g))
    r.shuffle(hand)
    return hand


_h = _straights(_r, 2000, 5, 40)
p["tests"].append([_h, 5])
_h2 = _h[:]; _h2[0] += 1
p["tests"].append([_h2, 5])
_h = _straights(_r, 100, 100, 100000000)
p["tests"].append([_h, 100])
_h = _straights(_r, 10, 1000, 20)
p["tests"].append([_h, 1000])
_h2 = _h[:]; _h2[7] = 999999999
p["tests"].append([_h2, 1000])
p["tests"].append([[_r.randint(0, 100) for _ in range(10000)], 10])
p["tests"].append([[i // 2 for i in range(10000)], 2])
p["tests"].append([[_r.randint(0, 1000000000) for _ in range(10000)], 1])


def b_straights(hand, g):
    memo = {}

    def go(cards):
        if not cards:
            return True
        if cards in memo:
            return memo[cards]
        res = False
        lst = list(cards)
        for v in sorted(set(lst)):  # try every possible group start, not just the minimum
            rest = lst[:]
            ok = True
            for y in range(v, v + g):
                if y in rest:
                    rest.remove(y)
                else:
                    ok = False
                    break
            if ok and go(tuple(sorted(rest))):
                res = True
                break
        memo[cards] = res
        return res

    if len(hand) % g:
        return False
    return go(tuple(sorted(hand)))


def g_straights(r):
    g = r.randint(1, 4)
    if r.random() < 0.6:
        hand = _straights(r, r.randint(1, 3), g, 4)
        if r.random() < 0.4:
            hand[r.randrange(len(hand))] = r.randint(0, 6)
    else:
        hand = [r.randint(0, 5) for _ in range(r.randint(1, 8))]
        g = r.randint(1, len(hand))
    return [hand, g]


def v_straights(tests):
    for t in tests:
        hand, g = t["args"]
        assert 1 <= len(hand) <= 10000 and 1 <= g <= len(hand)
        assert all(0 <= x <= 10 ** 9 for x in hand)
    res = [t["expected"] for t in tests]
    assert True in res and False in res


CHECKS["hand-of-straights-groups"] = (b_straights, g_straights, "exact")
VALIDATE["hand-of-straights-groups"] = v_straights


# ---------------------------------------------------------------- HARD

p = add(
    id="course-schedule-max-courses", title="Course Schedule: Maximum Courses", diff="Hard", topic="Greedy",
    fn="scheduleCourse", params=[("courses", "int[][]")], ret="int", cmp="exact",
    desc="<p>A student can take online courses one after another, never two at the same time. The entry <code>courses[i] = [duration, lastDay]</code> means course <code>i</code> takes <code>duration</code> consecutive days and must be <strong>finished</strong> by day <code>lastDay</code> (inclusive). The student starts on day 1, so a course taken first with duration <code>d</code> finishes on day <code>d</code>.</p><p>Return the maximum number of courses the student can complete.</p><pre>courses = [[100,200],[200,1300],[1000,1250],[2000,3200]] -> 3\ncourses = [[3,2],[4,3]]                                  -> 0</pre><p>In the first example, taking the 100-day, 1000-day and 200-day courses in that order finishes them on days 100, 1100 and 1300, all on time; the 2000-day course can no longer be added.</p>",
    constraints=["1 &le; courses.length &le; 10,000", "1 &le; duration, lastDay &le; 100,000"],
    hints=["Once you have chosen which courses to take, in what order should you take them to make deadlines easiest to meet?",
           "Process courses in order of deadline. Add each course to your plan; if the total time now exceeds the current deadline, something has to go.",
           "Keep a max-heap of the durations of the courses currently in your plan. When the total exceeds the deadline, drop the longest course: this frees the most time while losing only one course."],
    editorial=["For a fixed set of courses, taking them in increasing order of deadline is optimal (the classic earliest-deadline-first exchange argument), so sort all courses by <code>lastDay</code> and consider them in that order. Maintain <code>total</code>, the sum of durations of the courses currently kept, and a max-heap of those durations.",
               "For each course, tentatively add it: <code>total += duration</code>, push the duration. If <code>total &gt; lastDay</code>, the plan is infeasible, so remove the longest kept course (pop the heap and subtract it from <code>total</code>). This may remove the course just added, or an earlier longer one; either way the count of kept courses never needs to drop by more than one, and the total time is as small as possible for that count. The answer is the heap size at the end. Cost: O(n log n)."],
    time="O(n log n)", space="O(n)",
    solution='''import heapq


def scheduleCourse(courses):
    total = 0
    heap = []
    for duration, last in sorted(courses, key=lambda c: c[1]):
        total += duration
        heapq.heappush(heap, -duration)
        if total > last:
            total += heapq.heappop(heap)
    return len(heap)
''',
    tests=[[[[100, 200], [200, 1300], [1000, 1250], [2000, 3200]]], [[[3, 2], [4, 3]]], [[[1, 2]]], [[[2, 2]]], [[[3, 2]]],
           [[[5, 5], [4, 6], [2, 6]]], [[[7, 16], [2, 3], [3, 12], [3, 14], [10, 19], [10, 16], [6, 8], [6, 11], [3, 13], [6, 16]]],
           [[[1, 1], [1, 1], [1, 1]]], [[[2, 3], [2, 3], [2, 3]]], [[[10, 10], [5, 15], [5, 20], [5, 20]]],
           [[[100000, 100000], [100000, 100000]]], [[[1, 100000], [2, 100000], [3, 100000]]]],
)
_r = rnd(2009)
p["tests"].append([[[_r.randint(1, 100000), _r.randint(1, 100000)] for _ in range(10000)]])
p["tests"].append([[[_r.randint(1, 50), _r.randint(1, 100000)] for _ in range(10000)]])
p["tests"].append([[[_r.randint(1, 200), _r.randint(200, 100000)] for _ in range(10000)]])
p["tests"].append([[[1, 100000] for _ in range(10000)]])
p["tests"].append([[[10, 100000] for _ in range(10000)]])
p["tests"].append([[[i + 1, 100000 - (i % 7)] for i in range(10000)]])
p["tests"].append([[[_r.randint(1, 20), 20 * (i + 1)] for i in range(5000)]])


def b_courses(courses):
    m = len(courses)
    for size in range(m, 0, -1):
        for chosen in permutations(range(m), size):
            day = 0
            ok = True
            for j in chosen:
                day += courses[j][0]
                if day > courses[j][1]:
                    ok = False
                    break
            if ok:
                return size
    return 0


def g_courses(r):
    return [[[r.randint(1, 8), r.randint(1, 16)] for _ in range(r.randint(1, 6))]]


def v_courses(tests):
    for t in tests:
        c = t["args"][0]
        assert 1 <= len(c) <= 10000
        assert all(len(x) == 2 and 1 <= x[0] <= 100000 and 1 <= x[1] <= 100000 for x in c)
    res = [t["expected"] for t in tests]
    assert 0 in res and max(res) >= 3


CHECKS["course-schedule-max-courses"] = (b_courses, g_courses, "exact")
VALIDATE["course-schedule-max-courses"] = v_courses


p = add(
    id="minimum-refueling-stops", title="Minimum Refueling Stops", diff="Hard", topic="Greedy",
    fn="minRefuelStops", params=[("target", "int"), ("startFuel", "int"), ("stations", "int[][]")], ret="int", cmp="exact",
    desc="<p>A car starts at position <code>0</code> on a straight road and must reach <code>target</code>. It begins with <code>startFuel</code> units of fuel in its tank, and burns exactly one unit per unit of distance. The tank has unlimited capacity.</p><p>Along the road there are gas stations: <code>stations[i] = [position, fuel]</code> is a station at <code>position</code> that holds <code>fuel</code> units. Stations are given in strictly increasing order of position, and all positions are strictly between <code>0</code> and <code>target</code>. When the car stops at a station, it takes all of that station's fuel.</p><p>The car can only reach a place if its fuel never runs out before arriving (arriving with exactly 0 fuel is allowed, and it can still refuel there). Return the smallest number of stops needed to reach <code>target</code>, or <code>-1</code> if it is impossible.</p><pre>target = 100, startFuel = 10, stations = [[10,60],[20,30],[30,30],[60,40]] -> 2</pre><p>Stop at position 10 (take 60), then at 60 (take 40), and the car reaches 100.</p>",
    constraints=["1 &le; target &le; 1,000,000", "1 &le; startFuel &le; 1,000,000", "0 &le; stations.length &le; 1,000", "0 &lt; position<sub>i</sub> &lt; position<sub>i+1</sub> &lt; target", "1 &le; fuel<sub>i</sub> &le; 1,000,000"],
    hints=["A dynamic programming solution over the number of stops works. Can you instead decide stops lazily?",
           "Don't decide to refuel at a station when you pass it. Instead, remember it, and only 'go back' and use it when you would otherwise run out of fuel.",
           "Keep a max-heap of the fuel amounts of stations you have already passed. Whenever your current reach is below the target, take the largest fuel from the heap (one more stop), and add all stations that became reachable."],
    editorial=["Let <code>reach</code> be the farthest position the car can get to with the stops made so far, starting at <code>startFuel</code>. While <code>reach &lt; target</code>, push the fuel of every station with <code>position &le; reach</code> into a max-heap (those are stations the car could have passed and stopped at). If the heap is empty, no station can extend the trip: return -1. Otherwise, pop the largest fuel, add it to <code>reach</code>, and count one stop.",
               "This lazy decision is valid because stopping at a passed station only matters at the moment fuel would run out, and using the biggest available station then is never worse (exchange argument). Each station enters and leaves the heap at most once, giving O(n log n). All values stay below about 10<sup>9</sup>, since <code>reach</code> is at most 10<sup>6</sup> + 1,000 &times; 10<sup>6</sup>."],
    time="O(n log n)", space="O(n)",
    solution='''import heapq


def minRefuelStops(target, startFuel, stations):
    reach = startFuel
    stops = 0
    heap = []
    i = 0
    n = len(stations)
    while reach < target:
        while i < n and stations[i][0] <= reach:
            heapq.heappush(heap, -stations[i][1])
            i += 1
        if not heap:
            return -1
        reach += -heapq.heappop(heap)
        stops += 1
    return stops
''',
    tests=[[100, 10, [[10, 60], [20, 30], [30, 30], [60, 40]]], [1, 1, []], [100, 1, []], [100, 50, [[25, 25], [50, 50]]],
           [100, 10, [[10, 100]]], [100, 50, [[50, 50]]], [100, 25, [[25, 25], [50, 25], [75, 25]]],
           [100, 20, [[10, 5], [15, 10], [20, 100]]], [100, 10, [[11, 100]]], [1000, 10, [[10, 990]]],
           [100, 50, [[30, 10], [40, 20], [50, 30], [60, 50]]], [10, 20, [[5, 100]]]],
)
_r = rnd(2010)


def _stations(r, n, target, fmax):
    pos = sorted(r.sample(range(1, target), n))
    return [[x, r.randint(1, fmax)] for x in pos]


p["tests"].append([1000000, 5000, _stations(_r, 1000, 1000000, 5000)])
p["tests"].append([1000000, 100000, _stations(_r, 1000, 1000000, 10000)])
p["tests"].append([1000000, 1000, [[i * 999 + 1, 1000] for i in range(1000)]])
p["tests"].append([1000000, 1000000, _stations(_r, 1000, 999999, 1000000)])
p["tests"].append([1000000, 1000, [[1000 * (i + 1), 1000] for i in range(999)]])
p["tests"].append([999000, 999, [[999 * (i + 1), 999] for i in range(999)]])
p["tests"].append([1000000, 2, [[1 + 2 * i, 2] for i in range(1000)]])


def b_refuel(target, startFuel, stations):
    m = len(stations)
    for size in range(0, m + 1):
        for chosen in combinations(range(m), size):
            fuel = startFuel
            pos = 0
            ok = True
            for j in chosen:
                d = stations[j][0] - pos
                if fuel < d:
                    ok = False
                    break
                fuel += stations[j][1] - d
                pos = stations[j][0]
            if ok and fuel >= target - pos:
                return size
    return -1


def g_refuel(r):
    target = r.randint(2, 30)
    n = r.randint(0, min(7, target - 1))
    return [target, r.randint(1, 12), _stations(r, n, target, r.choice([3, 8, 15]))]


def v_refuel(tests):
    for t in tests:
        target, sf, st = t["args"]
        assert 1 <= target <= 10 ** 6 and 1 <= sf <= 10 ** 6 and len(st) <= 1000
        last = 0
        for pos, f in st:
            assert last < pos < target and 1 <= f <= 10 ** 6
            last = pos
    res = [t["expected"] for t in tests]
    assert -1 in res and 0 in res and any(x >= 2 for x in res)


CHECKS["minimum-refueling-stops"] = (b_refuel, g_refuel, "exact")
VALIDATE["minimum-refueling-stops"] = v_refuel
