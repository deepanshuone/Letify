"""Problems: greedy, coins / change / partitions. See data/lib.py for the registry."""
from itertools import combinations

from lib import add, rnd, CHECKS, VALIDATE, gen_arr  # noqa: F401

INT_MIN, INT_MAX = -(2 ** 31), 2 ** 31 - 1


# ---------------------------------------------------------------- EASY

p = add(
    id="min-deci-binary-numbers", title="Fewest Deci-Binary Addends", diff="Easy", topic="Greedy", tier="extra",
    fn="minDeciBinary", params=[("n", "string")], ret="int", cmp="exact",
    desc="<p>A positive integer is <em>deci-binary</em> if every digit in its decimal form is <code>0</code> or <code>1</code> and it has no leading zeros. For example <code>101</code> and <code>1100</code> are deci-binary, while <code>112</code> and <code>3001</code> are not.</p><p>The positive integer <code>n</code> is given as a string of digits. Return the minimum number of deci-binary numbers that add up to <code>n</code>. The same number may be used more than once.</p><pre>n = \"32\"    -> 3   (10 + 11 + 11)\nn = \"82734\" -> 8\nn = \"111\"   -> 1</pre>",
    constraints=["1 &le; n.length &le; 10,000", "n consists of digits only, has no leading zeros and is greater than 0"],
    hints=["Look at a single column of digits. One deci-binary number can contribute at most 1 to that column.",
           "If some column holds the digit 7, how many addends are needed just to produce that column?",
           "The answer cannot be smaller than the largest digit of n, and it is always possible to reach that bound. Return the largest digit."],
    editorial=["Every deci-binary addend adds either 0 or 1 to each digit position, and there are no carries to worry about as long as the total of a column is at most 9. A column that must reach the digit <code>d</code> therefore needs at least <code>d</code> addends, so the answer is at least the maximum digit <code>m</code> of <code>n</code>.",
               "That bound is achievable: build <code>m</code> addends, and in each column of digit <code>d</code> put a 1 in exactly <code>d</code> of them (any <code>d</code> of the <code>m</code>). Each addend then has digits 0 and 1 only, and none is zero because the column holding the digit <code>m</code> gives a 1 to every addend (leading zeros of an addend simply make it a shorter number). So the answer is just the largest digit, found in one pass."],
    time="O(n)", space="O(1)",
    solution='''def minDeciBinary(n):
    return int(max(n))
''',
    tests=[["32"], ["82734"], ["111"], ["1"], ["9"], ["10"], ["100000"], ["101010"], ["90"], ["5555"],
           ["2734620983070918234600000000000000000000000000000000000000000000000065432"]],
)
_r = rnd(6101)
p["tests"].append(["".join(_r.choice("0123456789") for _ in range(7999)) + "1"])
p["tests"].append(["1" + "".join(_r.choice("01") for _ in range(7999))])
p["tests"].append(["1" + "0" * 4000 + "7" + "01" * 2000])


def b_deci(n):
    v = int(n)
    deci = [x for x in range(1, v + 1) if set(str(x)) <= {"0", "1"}]
    INF = 10 ** 9
    dp = [0] + [INF] * v
    for a in range(1, v + 1):
        for d in deci:
            if d > a:
                break
            if dp[a - d] + 1 < dp[a]:
                dp[a] = dp[a - d] + 1
    return dp[v]


def v_deci(tests):
    for t in tests:
        n = t["args"][0]
        assert 1 <= len(n) <= 10000 and n.isdigit() and n[0] != "0"


CHECKS["min-deci-binary-numbers"] = (b_deci, lambda r: [str(r.randint(1, 999))], "exact")
VALIDATE["min-deci-binary-numbers"] = v_deci


p = add(
    id="fewest-distinct-letter-pieces", title="Fewest Distinct-Letter Pieces", diff="Easy", topic="Greedy",
    fn="fewestPieces", params=[("s", "string")], ret="int", cmp="exact",
    desc="<p>Cut the lowercase string <code>s</code> into consecutive non-empty pieces (every character belongs to exactly one piece, and the pieces keep their order) so that <strong>no letter appears twice inside the same piece</strong>.</p><p>Return the minimum number of pieces that is enough.</p><pre>s = \"abacaba\" -> 4   (ab | ac | ab | a)\ns = \"abcdef\"  -> 1\ns = \"aaaa\"    -> 4</pre>",
    constraints=["1 &le; s.length &le; 10,000", "s contains only lowercase English letters"],
    hints=["Any piece without a repeated letter is allowed, so each piece wants to be as long as possible.",
           "Start a piece and extend it to the right while the next character is new to the piece.",
           "Scan left to right with a set of the letters of the current piece. When the next character is already in the set, close the piece (count it), clear the set and start a new piece with that character."],
    editorial=["Keep the set of letters seen in the current piece. For every character: if it is already in the set the current piece cannot be extended, so count one finished piece and begin a new piece containing just this character; otherwise add it. At the end the last open piece is counted as well.",
               "Why greedy is optimal: if a valid cutting makes a piece shorter than the longest one that could start at the same position, we can move its end to the right (the longer piece is still repeat-free, and the following pieces only lose a prefix, which keeps them repeat-free). So taking the longest possible piece every time never needs more pieces than any other cutting. The loop is O(n) and the set has at most 26 elements."],
    time="O(n)", space="O(1)",
    solution='''def fewestPieces(s):
    pieces = 1
    seen = set()
    for ch in s:
        if ch in seen:
            pieces += 1
            seen = set()
        seen.add(ch)
    return pieces
''',
    tests=[["abacaba"], ["abcdef"], ["aaaa"], ["a"], ["ab"], ["aba"], ["abcabcabc"], ["zyxwvutsrqponmlkjihgfedcbaz"],
           ["abcdefghijklmnopqrstuvwxyz"], ["abba"]],
)
_r = rnd(6102)
p["tests"].append(["".join(_r.choice("abcdefghijklmnopqrstuvwxyz") for _ in range(9000))])
p["tests"].append(["".join(_r.choice("ab") for _ in range(9500))])
p["tests"].append(["abcdefghijklmnopqrstuvwxyz" * 380])
p["tests"].append(["a" * 10000])


def b_pieces(s):
    n = len(s)
    INF = 10 ** 9
    dp = [0] + [INF] * n
    for i in range(1, n + 1):
        for j in range(i):
            seg = s[j:i]
            if len(set(seg)) == len(seg) and dp[j] + 1 < dp[i]:
                dp[i] = dp[j] + 1
    return dp[n]


def v_pieces(tests):
    for t in tests:
        s = t["args"][0]
        assert 1 <= len(s) <= 10000 and s.isalpha() and s.islower()


CHECKS["fewest-distinct-letter-pieces"] = (b_pieces, lambda r: ["".join(r.choice("abcd") for _ in range(r.randint(1, 10)))], "exact")
VALIDATE["fewest-distinct-letter-pieces"] = v_pieces


p = add(
    id="max-coins-from-triple-piles", title="Coins From Triple Piles", diff="Easy", topic="Greedy", tier="extra",
    fn="maxCoins", params=[("piles", "int[]")], ret="int", cmp="exact",
    desc="<p>There are <code>3m</code> piles of coins; <code>piles[i]</code> is the number of coins in pile <code>i</code>. You play with two friends, Alice and Bob, until no pile is left. In every round:</p><ul><li>you pick <strong>any</strong> three of the remaining piles,</li><li>Alice takes the pile with the most coins of the three,</li><li>you take the pile with the second most coins (with ties, any order gives the same pile size),</li><li>Bob takes the remaining, smallest pile.</li></ul><p>Return the maximum total number of coins you can collect.</p><pre>piles = [2, 4, 1, 2, 7, 8]            -> 9   (round 1: 2,7,8 you take 7; round 2: 1,2,4 you take 2)\npiles = [2, 4, 5]                     -> 4\npiles = [9, 8, 7, 6, 5, 1, 2, 3, 4]   -> 18</pre>",
    constraints=["3 &le; piles.length &le; 9,999 and piles.length is a multiple of 3", "1 &le; piles[i] &le; 10,000"],
    hints=["Alice always gets the largest of the three. What is the best way to make her waste as little as possible?",
           "Bob's pile is wasted too. Give Bob the smallest piles in the whole input.",
           "Sort. Bob takes the smallest m piles. Among the remaining 2m piles, pair them from the top: you take the 2nd, 4th, 6th ... largest piles overall."],
    editorial=["You choose the triples, so choose them to feed Alice and Bob as little as possible. In every round the largest pile of the triple is lost to Alice, so the best we can do is let her take the next biggest piles and put ourselves right below her: take the two largest remaining piles together with the smallest remaining pile as the triple. Alice gets the largest, you get the second largest, Bob is stuck with the smallest.",
               "After sorting ascending, Bob receives the first <code>m = n / 3</code> piles and you collect the piles at sorted positions <code>n-2, n-4, ..., n/3</code> (m piles in total). Swapping any other arrangement into this one never decreases your total, because the smallest piles are the least useful to anyone else. Sorting dominates: O(n log n)."],
    time="O(n log n)", space="O(1) extra (ignoring sort)",
    solution='''def maxCoins(piles):
    piles = sorted(piles)
    n = len(piles)
    total = 0
    for i in range(n // 3, n, 2):
        total += piles[i]
    return total
''',
    tests=[[[2, 4, 1, 2, 7, 8]], [[2, 4, 5]], [[9, 8, 7, 6, 5, 1, 2, 3, 4]], [[1, 1, 1]], [[10000, 10000, 10000]],
           [[5, 5, 5, 5, 5, 5]], [[1, 2, 3, 4, 5, 6]], [[1, 1, 1, 1, 1, 9]], [[7, 3, 9, 3, 7, 9, 1, 1, 1]]],
)
_r = rnd(6103)
p["tests"].append([[_r.randint(1, 10000) for _ in range(9000)]])
p["tests"].append([[_r.randint(1, 10000) for _ in range(5001 - 5001 % 3)]])
p["tests"].append([[10000] * 3000 + [1] * 3000 + [5000] * 3000])


def b_coins(piles):
    best = 0

    def go(rest, got):
        nonlocal best
        if not rest:
            best = max(best, got)
            return
        # one triple always contains the first remaining pile; choose its two partners
        n = len(rest)
        for j in range(1, n):
            for k in range(j + 1, n):
                trio = sorted([rest[0], rest[j], rest[k]])
                left = [rest[q] for q in range(1, n) if q != j and q != k]
                go(left, got + trio[1])

    go(list(piles), 0)
    return best


def v_coins(tests):
    for t in tests:
        a = t["args"][0]
        assert 3 <= len(a) <= 9999 and len(a) % 3 == 0 and all(1 <= x <= 10000 for x in a)


CHECKS["max-coins-from-triple-piles"] = (b_coins, lambda r: [[r.randint(1, 8) for _ in range(3 * r.randint(1, 3))]], "exact")
VALIDATE["max-coins-from-triple-piles"] = v_coins


# ---------------------------------------------------------------- MEDIUM

p = add(
    id="min-fibonacci-numbers-for-sum", title="Fewest Fibonacci Numbers", diff="Medium", topic="Greedy",
    fn="minFibonacci", params=[("k", "int")], ret="int", cmp="exact",
    desc="<p>The Fibonacci numbers are <code>1, 1, 2, 3, 5, 8, 13, ...</code> (each one is the sum of the previous two). Given a positive integer <code>k</code>, return the minimum number of Fibonacci numbers whose sum is exactly <code>k</code>. The same Fibonacci number may be used several times.</p><pre>k = 7  -> 2   (5 + 2)\nk = 10 -> 2   (8 + 2)\nk = 19 -> 3   (13 + 5 + 1)</pre>",
    constraints=["1 &le; k &le; 2<sup>31</sup> - 1"],
    hints=["Think of the Fibonacci numbers as the coin denominations of a coin-change problem. k is far too large for a dynamic program over amounts.",
           "Only about 45 Fibonacci numbers are below 2<sup>31</sup>. Try always taking the largest coin that still fits.",
           "Generate the Fibonacci numbers up to k and subtract the largest one not exceeding the remaining value, repeatedly, counting the subtractions."],
    editorial=["Greedy is correct for this particular coin system. Let <code>F</code> be the largest Fibonacci number not above <code>k</code>. Some optimal answer uses <code>F</code>: any set of Fibonacci numbers summing to <code>k</code> that avoids <code>F</code> consists of smaller ones, and one can repeatedly merge two equal or consecutive Fibonacci numbers into the next one (<code>F(i) + F(i-1) = F(i+1)</code> and <code>2 F(i) = F(i+1) + F(i-2)</code>) without increasing the count, until the largest term appears.",
               "So subtract the largest Fibonacci number from <code>k</code>, count one, and repeat with the remainder. The remainder is smaller than the previous Fibonacci number, so each Fibonacci number is taken at most once and the loop does about 45 steps."],
    time="O(log k)", space="O(log k)",
    solution='''def minFibonacci(k):
    fibs = [1, 2]
    while fibs[-1] + fibs[-2] <= k:
        fibs.append(fibs[-1] + fibs[-2])
    count = 0
    for f in reversed(fibs):
        while k >= f:
            k -= f
            count += 1
    return count
''',
    tests=[[7], [10], [19], [1], [2], [3], [4], [100], [1000000000], [INT_MAX], [1836311903], [1134903170 + 701408733], [987654321]],
)


def b_fib(k):
    fibs = [1, 2]
    while fibs[-1] + fibs[-2] <= k:
        fibs.append(fibs[-1] + fibs[-2])
    INF = 10 ** 9
    dp = [0] + [INF] * k
    for a in range(1, k + 1):
        for f in fibs:
            if f > a:
                break
            dp[a] = min(dp[a], dp[a - f] + 1)
    return dp[k]


def v_fib(tests):
    for t in tests:
        assert 1 <= t["args"][0] <= INT_MAX


CHECKS["min-fibonacci-numbers-for-sum"] = (b_fib, lambda r: [r.randint(1, 400)], "exact")
VALIDATE["min-fibonacci-numbers-for-sum"] = v_fib


p = add(
    id="double-or-decrement-min-steps", title="Double or Decrement", diff="Medium", topic="Greedy",
    fn="minSteps", params=[("start", "int"), ("target", "int")], ret="int", cmp="exact",
    desc="<p>A broken calculator shows the number <code>start</code>. It has only two buttons: <strong>double</strong> (multiply the displayed number by 2) and <strong>decrement</strong> (subtract 1). Each press is one step.</p><p>Return the minimum number of steps needed to make the display show exactly <code>target</code>.</p><pre>start = 2, target = 3  -> 2   (2 -> 4 -> 3)\nstart = 5, target = 8  -> 2   (5 -> 4 -> 8)\nstart = 3, target = 10 -> 3   (3 -> 6 -> 5 -> 10)\nstart = 9, target = 4  -> 5   (only decrements)</pre>",
    constraints=["1 &le; start, target &le; 10<sup>9</sup>"],
    hints=["Forward search blows up: from start you can go both up and down. What if you work from target back to start?",
           "Reversed, the operations become: halve (if the value is even) or add 1. When target is at most start, only decrements are useful.",
           "While target is larger than start: if it is odd, add 1 (halving is impossible), otherwise halve it. Count each move. When target drops to start or below, add the remaining difference start - target."],
    editorial=["Run the process backwards from <code>target</code>: the inverse of doubling is halving (only legal for even numbers) and the inverse of decrementing is adding 1. As long as <code>target &gt; start</code> we want to shrink the value as fast as possible. If it is even, halving is clearly the best move. If it is odd we are forced to add 1 first; adding 1 and halving costs two steps, and any alternative that adds more before halving reaches a number at least as large with at least as many steps.",
               "Once <code>target &le; start</code> doubling can no longer help (it only moves away), so the rest are plain decrements: <code>start - target</code> more steps. Each loop turn at least halves the target, giving O(log target) time."],
    time="O(log target)", space="O(1)",
    solution='''def minSteps(start, target):
    steps = 0
    while target > start:
        if target % 2:
            target += 1
        else:
            target //= 2
        steps += 1
    return steps + start - target
''',
    tests=[[2, 3], [5, 8], [3, 10], [9, 4], [1, 1], [1, 1000000000], [1000000000, 1], [7, 7], [1, 2], [2, 1], [1000000000, 999999999],
           [999999999, 1000000000], [123456789, 987654321], [3, 999999999]],
)


def b_dd(start, target):
    from collections import deque
    cap = 2 * max(start, target) + 2
    dist = {start: 0}
    q = deque([start])
    while q:
        x = q.popleft()
        if x == target:
            return dist[x]
        for y in (x * 2, x - 1):
            if 0 <= y <= cap and y not in dist:
                dist[y] = dist[x] + 1
                q.append(y)


def v_dd(tests):
    for t in tests:
        a, b = t["args"]
        assert 1 <= a <= 10 ** 9 and 1 <= b <= 10 ** 9


CHECKS["double-or-decrement-min-steps"] = (b_dd, lambda r: [r.randint(1, 40), r.randint(1, 60)], "exact")
VALIDATE["double-or-decrement-min-steps"] = v_dd


p = add(
    id="split-into-consecutive-chains", title="Split Into Consecutive Chains", diff="Medium", topic="Greedy",
    fn="canSplitChains", params=[("nums", "int[]"), ("minLen", "int")], ret="bool", cmp="exact",
    desc="<p>The integer array <code>nums</code> is sorted in non-decreasing order. A <em>chain</em> is a group of values of the form <code>v, v+1, v+2, ..., v+len-1</code> (each value one more than the previous) taken from <code>nums</code>.</p><p>Decide whether every element of <code>nums</code> can be assigned to exactly one chain so that every chain has <strong>at least <code>minLen</code> elements</strong>. Return <code>true</code> if this is possible, otherwise <code>false</code>.</p><pre>nums = [1, 2, 3, 3, 4, 5], minLen = 3          -> true   ([1,2,3] and [3,4,5])\nnums = [1, 2, 3, 3, 4, 4, 5, 5], minLen = 3    -> true   ([1,2,3,4,5] and [3,4,5])\nnums = [1, 2, 3, 4, 4, 5], minLen = 3          -> false</pre>",
    constraints=["0 &le; nums.length &le; 5,000", "-10<sup>9</sup> &le; nums[i] &le; 10<sup>9</sup>, sorted in non-decreasing order", "1 &le; minLen &le; 5,000"],
    hints=["The smallest remaining value must start a chain. The real question is, when a value can both extend a chain and start a new one, which is better?",
           "Extending a chain that is already waiting for exactly this value is never worse than starting a new chain with it (merge the two chains in any solution that does otherwise).",
           "Go through the distinct values in order, keeping the number of chains ending at the previous value, grouped by their start value. If the current value occurs more often than there are chains, the surplus starts new chains. If it occurs less often, the chains that must stop are the oldest (longest) ones; check each has length at least minLen."],
    editorial=["Process the distinct values in increasing order and keep a queue of groups <code>(start value, how many chains)</code> for the chains that end at the previous value. Let <code>p</code> be the number of such chains and <code>c</code> the count of the current value <code>x</code> (if <code>x</code> is not the previous value plus one, every open chain must stop first).",
               "If <code>c &ge; p</code>, all <code>p</code> chains are extended by <code>x</code> (stopping a chain just to start another at the same place could be merged back into one longer chain) and the <code>c - p</code> surplus copies start new chains. If <code>c &lt; p</code>, exactly <code>p - c</code> chains must stop here, and we stop those that started earliest, because they are the longest and the others still need time to reach <code>minLen</code>. A stopped group with length <code>x - start &lt; minLen</code> means <code>false</code>. At the very end all open chains are checked in the same way.",
               "Each value is handled once and queue groups are popped at most once, so the running time is linear after counting."],
    time="O(n)", space="O(n)",
    solution='''from collections import Counter, deque

def canSplitChains(nums, minLen):
    cnt = Counter(nums)
    open_ = deque()          # [start value, number of chains] for chains ending at prev
    prev = None
    prev_cnt = 0
    for x in sorted(cnt):
        c = cnt[x]
        if prev is not None and x != prev + 1:
            for s, m in open_:
                if prev - s + 1 < minLen:
                    return False
            open_.clear()
            prev_cnt = 0
        p = prev_cnt
        if c > p:
            open_.append([x, c - p])
        elif c < p:
            need = p - c
            while need:
                s, m = open_[0]
                if x - s < minLen:
                    return False
                t = min(m, need)
                if t == m:
                    open_.popleft()
                else:
                    open_[0][1] -= t
                need -= t
        prev = x
        prev_cnt = c
    for s, m in open_:
        if prev - s + 1 < minLen:
            return False
    return True
''',
    tests=[[[1, 2, 3, 3, 4, 5], 3], [[1, 2, 3, 3, 4, 4, 5, 5], 3], [[1, 2, 3, 4, 4, 5], 3], [[], 1], [[5], 1], [[5], 2],
           [[1, 2, 2, 3], 2], [[1, 2, 3, 3, 4, 4, 5, 5], 5], [[1, 1, 2, 2, 3, 3], 3], [[1, 2, 3, 5, 6, 7], 3], [[1, 2, 3, 5, 6], 3],
           [[-3, -2, -1, 0, 1], 5], [[1, 2, 2, 3, 3, 4], 3]],
)
_r = rnd(6106)
_a = []
for _ in range(120):  # many overlapping chains of random lengths over a narrow value range -> true
    _s = _r.randint(0, 60)
    _a += list(range(_s, _s + _r.randint(4, 30)))
_a.sort()
p["tests"].append([_a, 4])
_b = _a[:]
_b.remove(30)
_b.remove(31)
p["tests"].append([_b, 4])
_a = sorted(_r.randint(0, 400) for _ in range(4500))
p["tests"].append([_a, 2])
_a = []
for _ in range(900):
    _s = _r.randint(-10 ** 9, 10 ** 9 - 10)
    _a += list(range(_s, _s + _r.randint(3, 8)))
p["tests"].append([sorted(_a)[:4800], 3])


def b_chains(nums, minLen):
    from functools import lru_cache

    @lru_cache(maxsize=None)
    def go(state):
        if not state:
            return True
        d = dict(state)
        x = min(d)
        # start a chain at x of length ln >= minLen
        ln = 0
        while d.get(x + ln, 0) > 0:
            ln += 1
            if ln >= minLen:
                nd = dict(d)
                for v in range(x, x + ln):
                    nd[v] -= 1
                    if nd[v] == 0:
                        del nd[v]
                if go(tuple(sorted(nd.items()))):
                    return True
        return False

    from collections import Counter
    return go(tuple(sorted(Counter(nums).items())))


def g_chains(r):
    return [sorted(r.randint(0, 5) for _ in range(r.randint(0, 10))), r.randint(1, 4)]


def v_chains(tests):
    for t in tests:
        a, m = t["args"]
        assert len(a) <= 5000 and 1 <= m <= 5000 and a == sorted(a)
        assert all(-10 ** 9 <= x <= 10 ** 9 for x in a)
    assert any(t["expected"] for t in tests) and any(not t["expected"] for t in tests)


CHECKS["split-into-consecutive-chains"] = (b_chains, g_chains, "exact")
VALIDATE["split-into-consecutive-chains"] = v_chains


p = add(
    id="fewest-groups-bounded-spread", title="Fewest Groups With Bounded Spread", diff="Medium", topic="Greedy",
    fn="fewestGroups", params=[("nums", "int[]"), ("k", "int")], ret="int", cmp="exact",
    desc="<p>Split the elements of <code>nums</code> into groups. A group may contain any elements (they do not have to be next to each other in the array, and the order inside a group is irrelevant), but the <strong>largest minus the smallest value in a group must be at most <code>k</code></strong>. Every element belongs to exactly one group.</p><p>Return the minimum number of groups needed. For an empty array the answer is <code>0</code>.</p><pre>nums = [3, 6, 1, 2, 5], k = 2 -> 2   ({1,2,3} and {5,6})\nnums = [1, 2, 3], k = 1       -> 2   ({1,2} and {3})\nnums = [4, 4, 4], k = 0       -> 1</pre>",
    constraints=["0 &le; nums.length &le; 10,000", "-10<sup>9</sup> &le; nums[i] &le; 10<sup>9</sup>", "0 &le; k &le; 2 &times; 10<sup>9</sup>"],
    hints=["The positions in the array do not matter, so you are free to reorder the values.",
           "After sorting, a group that is as good as any other can always be a contiguous block of the sorted order.",
           "Start a group at the smallest unassigned value v and absorb every value up to v + k. The first value beyond v + k starts the next group."],
    editorial=["Because only values matter, sort the array. Take the smallest unassigned value <code>v</code>. It must belong to some group, and that group can only contain values in <code>[v, v + k]</code>; making the group take <em>all</em> remaining values in that interval is never worse, since those values would otherwise have to be placed in other groups that could also be merged into this one (the spread of the merged group is still at most <code>k</code>).",
               "So scan the sorted array, remember the start of the current group, and open a new group whenever a value exceeds <code>start + k</code>. The number of groups opened is the answer. Sorting gives O(n log n); the scan is linear."],
    time="O(n log n)", space="O(1) extra (ignoring sort)",
    solution='''def fewestGroups(nums, k):
    if not nums:
        return 0
    nums = sorted(nums)
    groups = 1
    start = nums[0]
    for x in nums:
        if x - start > k:
            groups += 1
            start = x
    return groups
''',
    tests=[[[3, 6, 1, 2, 5], 2], [[1, 2, 3], 1], [[4, 4, 4], 0], [[], 5], [[7], 0], [[1, 10], 8], [[1, 10], 9], [[-5, 5, -4, 4, 0], 3],
           [[2, 2, 4, 5, 6], 0], [[-10 ** 9, 10 ** 9], 10 ** 9], [[-10 ** 9, 10 ** 9], 2 * 10 ** 9]],
)
_r = rnd(6107)
p["tests"].append([[_r.randint(-10 ** 9, 10 ** 9) for _ in range(9000)], 10 ** 6])
p["tests"].append([[_r.randint(0, 100000) for _ in range(9500)], 50])
p["tests"].append([list(range(0, 10000)), 9])


def b_groups(nums, k):
    n = len(nums)
    if n == 0:
        return 0
    best = n

    def go(i, groups):  # groups: list of [min, max]
        nonlocal best
        if len(groups) >= best:
            return
        if i == n:
            best = len(groups)
            return
        x = nums[i]
        for g in groups:
            lo, hi = g
            if max(hi, x) - min(lo, x) <= k:
                old = (lo, hi)
                g[0], g[1] = min(lo, x), max(hi, x)
                go(i + 1, groups)
                g[0], g[1] = old
        groups.append([x, x])
        go(i + 1, groups)
        groups.pop()

    go(0, [])
    return best


def v_groups(tests):
    for t in tests:
        a, k = t["args"]
        assert len(a) <= 10000 and 0 <= k <= 2 * 10 ** 9
        assert all(-10 ** 9 <= x <= 10 ** 9 for x in a)


CHECKS["fewest-groups-bounded-spread"] = (b_groups, lambda r: [gen_arr(r, -8, 8, 0, 8), r.randint(0, 6)], "exact")
VALIDATE["fewest-groups-bounded-spread"] = v_groups


p = add(
    id="fewest-notes-limited-supply", title="Fewest Notes With Limited Supply", diff="Medium", topic="Greedy", tier="extra",
    fn="fewestNotes", params=[("denoms", "int[]"), ("counts", "int[]"), ("amount", "int")], ret="int", cmp="exact",
    desc="<p>A cash machine holds banknotes of several denominations. <code>denoms</code> lists the denominations in increasing order, and the machine has exactly <code>counts[i]</code> notes of value <code>denoms[i]</code>. The denominations form a <strong>divisibility chain</strong>: every denomination divides the next larger one (for example 1, 5, 10, 50, 200).</p><p>Return the smallest number of notes that add up to exactly <code>amount</code>, or <code>-1</code> if the amount cannot be paid with the available notes. An amount of <code>0</code> needs <code>0</code> notes.</p><pre>denoms = [1, 5, 10, 50], counts = [10, 2, 3, 1], amount = 87 -> 7   (50 + 3*10 + 5 + 2*1)\ndenoms = [1, 5, 10, 50], counts = [1, 0, 0, 1],  amount = 60 -> -1\ndenoms = [2, 6],         counts = [5, 1],        amount = 9  -> -1</pre>",
    constraints=["1 &le; denoms.length = counts.length &le; 30", "1 &le; denoms[0] and denoms[i] &lt; denoms[i+1] with denoms[i+1] a multiple of denoms[i]; denoms[i] &le; 10<sup>9</sup>", "0 &le; counts[i] &le; 10<sup>9</sup>", "0 &le; amount &le; 10<sup>9</sup>"],
    hints=["A dynamic program over amounts is far too slow for amounts up to 10<sup>9</sup>. The divisibility chain must be the key.",
           "Should you ever pay with several small notes when a larger note would fit and is available?",
           "Go from the largest denomination down. Use as many notes of it as both the supply and the remaining amount allow, then continue with the next smaller one. At the end the remaining amount must be exactly 0."],
    editorial=["Process denominations from largest to smallest. For denomination <code>d</code> with <code>c</code> notes left and remaining amount <code>a</code>, take <code>t = min(c, a // d)</code> notes. If after all denominations something is left, answer <code>-1</code>.",
               "Why taking as many large notes as possible is right: suppose an optimal payment uses fewer than <code>t</code> notes of the largest usable denomination <code>d</code>. Then the smaller notes it uses add up to at least <code>d</code>. Because every smaller denomination divides <code>d</code>, one can always pick some of those smaller notes that sum to exactly <code>d</code> (add them in decreasing order; the running total can never jump over <code>d</code>). Replacing them by one note of value <code>d</code> keeps the amount and reduces the number of notes. The same argument shows that if any payment exists, greedy finds one.",
               "The chain property is essential: with denominations like 1, 3, 4 greedy fails even without supply limits. The loop is O(k) for k denominations."],
    time="O(k)", space="O(1)",
    solution='''def fewestNotes(denoms, counts, amount):
    used = 0
    for i in range(len(denoms) - 1, -1, -1):
        t = min(counts[i], amount // denoms[i])
        amount -= t * denoms[i]
        used += t
    return used if amount == 0 else -1
''',
    tests=[[[1, 5, 10, 50], [10, 2, 3, 1], 87], [[1, 5, 10, 50], [1, 0, 0, 1], 60], [[2, 6], [5, 1], 9], [[1], [0], 0], [[1], [5], 5],
           [[1], [4], 5], [[5], [3], 0], [[3, 6, 12], [2, 1, 1], 24], [[3, 6, 12], [2, 1, 1], 21], [[1, 2, 4, 8, 16], [0, 0, 0, 0, 5], 80],
           [[1, 2, 4, 8, 16], [0, 0, 0, 0, 5], 81]],
)
_dd = [2 ** i for i in range(30)]  # up to 2^29 = 536870912
p["tests"].append([_dd, [10 ** 9] * 30, 10 ** 9])
p["tests"].append([_dd, [1] * 30, 999999999])
p["tests"].append([_dd, [0, 1, 0, 1, 1, 0, 1, 0, 1, 1] + [0] * 19 + [1], 2 ** 29 + 2 ** 9 + 2 ** 8 + 2 ** 6 + 2 ** 4 + 2 ** 3 + 2 ** 1])
p["tests"].append([[7, 21, 105, 1050, 21000, 420000, 12600000, 100800000], [3, 1, 4, 1, 5, 9, 2, 6], 987654321])


def b_notes(denoms, counts, amount):
    INF = 10 ** 9
    dp = [0] + [INF] * amount
    for d, c in zip(denoms, counts):
        new = dp[:]
        for a in range(amount + 1):
            for t in range(1, c + 1):
                if t * d > a:
                    break
                if dp[a - t * d] + t < new[a]:
                    new[a] = dp[a - t * d] + t
        dp = new
    return dp[amount] if dp[amount] < INF else -1


def g_notes(r):
    k = r.randint(1, 4)
    d = [r.randint(1, 3)]
    while len(d) < k:
        d.append(d[-1] * r.randint(2, 4))
    return [d, [r.randint(0, 5) for _ in range(k)], r.randint(0, 70)]


def v_notes(tests):
    for t in tests:
        d, c, a = t["args"]
        assert 1 <= len(d) == len(c) <= 30 and 0 <= a <= 10 ** 9
        assert all(1 <= x <= 10 ** 9 for x in d) and all(0 <= x <= 10 ** 9 for x in c)
        assert all(d[i] < d[i + 1] and d[i + 1] % d[i] == 0 for i in range(len(d) - 1))
    assert any(t["expected"] == -1 for t in tests) and any(t["expected"] > 0 for t in tests)


CHECKS["fewest-notes-limited-supply"] = (b_notes, g_notes, "exact")
VALIDATE["fewest-notes-limited-supply"] = v_notes


p = add(
    id="reach-number-minimum-moves", title="Reach a Number", diff="Medium", topic="Greedy", tier="extra",
    fn="reachNumber", params=[("target", "int")], ret="int", cmp="exact",
    desc="<p>You stand at position <code>0</code> on an infinite number line. On move number <code>i</code> (1, 2, 3, ...) you must walk exactly <code>i</code> units, either to the left or to the right, your choice each time.</p><p>Return the minimum number of moves after which you can be standing exactly on <code>target</code>.</p><pre>target = 3  -> 2   (+1, +2)\ntarget = 2  -> 3   (+1, -2, +3)\ntarget = -4 -> 3   (+1, -2, -3)\ntarget = 0  -> 0</pre>",
    constraints=["-10<sup>9</sup> &le; target &le; 10<sup>9</sup>"],
    hints=["Moving to -target is the mirror image of moving to target, so only |target| matters.",
           "After k moves the farthest you can be is 1 + 2 + ... + k. Which positions up to that sum are reachable?",
           "Find the first k with sum &ge; |target|. Flipping the direction of move j changes the final position by 2j. So the difference sum - |target| has to be even; if it is not, keep increasing k."],
    editorial=["Work with <code>t = |target|</code>. If every one of the first <code>k</code> moves goes right you stand at <code>S = k(k+1)/2</code>. Turning move <code>j</code> into a left move subtracts <code>2j</code> from the final position, so after <code>k</code> moves you can stand exactly on the positions <code>S - 2m</code>, where <code>m</code> is the sum of some subset of <code>{1, ..., k}</code>.",
               "Every integer from 0 to S is a subset sum of 1..k, hence the reachable positions are all numbers between <code>-S</code> and <code>S</code> that have the same parity as <code>S</code>. So the answer is the smallest <code>k</code> with <code>S &ge; t</code> and <code>(S - t)</code> even. Increase <code>k</code> until <code>S</code> reaches <code>t</code>; if the parity is wrong, keep adding moves: since <code>S</code> grows by <code>k+1</code> each time, the parity fixes itself within at most three further moves. The loop runs about <code>sqrt(2t)</code> times, roughly 45,000 iterations for 10<sup>9</sup>, which is instant (a closed form with a square root is also possible)."],
    time="O(sqrt(|target|))", space="O(1)",
    solution='''def reachNumber(target):
    t = abs(target)
    k = 0
    s = 0
    while s < t or (s - t) % 2:
        k += 1
        s += k
    return k
''',
    tests=[[3], [2], [-4], [0], [1], [-1], [5], [6], [7], [10], [11], [-1000000000], [1000000000], [999999999], [123456789]],
)


def b_reach(target):
    reach = {0}
    k = 0
    while target not in reach:
        k += 1
        reach = {x + k for x in reach} | {x - k for x in reach}
    return k


def v_reach(tests):
    for t in tests:
        assert -10 ** 9 <= t["args"][0] <= 10 ** 9


CHECKS["reach-number-minimum-moves"] = (b_reach, lambda r: [r.randint(-60, 60)], "exact")
VALIDATE["reach-number-minimum-moves"] = v_reach


# ---------------------------------------------------------------- HARD

p = add(
    id="patch-coins-to-cover-range", title="Patch the Coin Set", diff="Hard", topic="Greedy",
    fn="minPatches", params=[("coins", "int[]"), ("n", "int")], ret="int", cmp="exact",
    desc="<p>You own a purse of coins with positive integer values, given in sorted (non-decreasing) order in <code>coins</code>. You want every integer amount from <code>1</code> to <code>n</code> to be payable exactly using some sub-collection of your coins (each coin used at most once).</p><p>You may add new coins of any positive integer value to the purse. Return the minimum number of coins you must add so that all amounts <code>1..n</code> become payable.</p><pre>coins = [1, 3], n = 6        -> 1   (add 2)\ncoins = [1, 5, 10], n = 20   -> 2   (add 2 and 4)\ncoins = [1, 2, 2], n = 5     -> 0</pre>",
    constraints=["0 &le; coins.length &le; 5,000", "1 &le; coins[i] &le; 10<sup>9</sup>, sorted in non-decreasing order", "1 &le; n &le; 2<sup>31</sup> - 1"],
    hints=["Keep track of <code>reach</code>: the largest value such that every amount in [1, reach] can already be paid.",
           "If the next coin is at most reach + 1, then it extends the covered range to reach + coin. Otherwise there is a gap right after reach.",
           "To close the gap at reach + 1 the best coin you can add has value exactly reach + 1: it doubles the covered range. Add it (count a patch) and check the same coin again. Stop once reach &ge; n."],
    editorial=["Let <code>reach</code> be the largest value such that all of <code>1..reach</code> is payable with the coins processed (or added) so far; initially 0. Look at the next coin <code>c</code> (in sorted order). If <code>c &le; reach + 1</code>, we can pay <code>reach + 1 .. reach + c</code> by combining <code>c</code> with an amount from the covered range, so <code>reach += c</code> and we move on.",
               "Otherwise the amount <code>reach + 1</code> is unpayable, and no existing coin can help (they are all larger). We must add a coin of value at most <code>reach + 1</code>; choosing exactly <code>reach + 1</code> is best because it extends the range the most, to <code>2 * reach + 1</code>. Count a patch, update <code>reach</code> and look at the same coin again. When the coins run out, keep patching while <code>reach &lt; n</code>.",
               "Each patch at least doubles <code>reach</code>, so there are at most about 31 patches, and every coin is looked at once: O(m + log n) time. Note that the covered range can exceed 2<sup>31</sup> inside the loop; Python integers do not care, but in fixed-width languages use 64 bits."],
    time="O(m + log n)", space="O(1)",
    solution='''def minPatches(coins, n):
    reach = 0
    patches = 0
    i = 0
    while reach < n:
        if i < len(coins) and coins[i] <= reach + 1:
            reach += coins[i]
            i += 1
        else:
            reach += reach + 1
            patches += 1
    return patches
''',
    tests=[[[1, 3], 6], [[1, 5, 10], 20], [[1, 2, 2], 5], [[], 1], [[], 7], [[], INT_MAX], [[1], 1], [[5], 4], [[2, 3, 4], 10], [[1, 1, 1, 1, 1], 5],
           [[10, 20, 30], 25], [[1, 2, 4, 8, 16, 32], 100], [[1000000000], INT_MAX]],
)
_r = rnd(6110)
p["tests"].append([sorted(_r.randint(1, 3000) for _ in range(4000)), INT_MAX])
p["tests"].append([sorted([1] + [_r.randint(1, 10 ** 9) for _ in range(3500)]), INT_MAX])
p["tests"].append([sorted(_r.randint(1, 50) for _ in range(5000)), INT_MAX])


def b_patch(coins, n):
    def covers(cs):
        sums = {0}
        for c in cs:
            sums |= {s + c for s in sums}
        return all(v in sums for v in range(1, n + 1))

    for p_ in range(0, 7):
        for extra in combinations(range(1, n + 1), p_):
            if covers(list(coins) + list(extra)):
                return p_


def g_patch(r):
    n = r.randint(1, 14)
    return [sorted(r.randint(1, 15) for _ in range(r.randint(0, 5))), n]


def v_patch(tests):
    for t in tests:
        c, n = t["args"]
        assert len(c) <= 5000 and c == sorted(c) and all(1 <= x <= 10 ** 9 for x in c) and 1 <= n <= INT_MAX


CHECKS["patch-coins-to-cover-range"] = (b_patch, g_patch, "exact")
VALIDATE["patch-coins-to-cover-range"] = v_patch


p = add(
    id="max-groups-growing-size-usage-limits", title="Most Groups of Growing Size", diff="Hard", topic="Greedy", tier="extra",
    fn="maxGroups", params=[("limits", "int[]")], ret="int", cmp="exact",
    desc="<p>You have <code>n</code> distinct item kinds numbered <code>0..n-1</code>. Kind <code>i</code> can be used at most <code>limits[i]</code> times in total over all groups.</p><p>You want to form as many groups as possible. Every group must contain <strong>distinct</strong> kinds (no kind twice inside one group) and be non-empty, and when the groups are listed in order, each group must contain <strong>strictly more</strong> kinds than the group before it. Return the maximum possible number of groups.</p><pre>limits = [1, 2, 5] -> 3   ({2}, {1,2}, {0,1,2})\nlimits = [2, 1, 2] -> 2\nlimits = [1, 1]    -> 1</pre>",
    constraints=["1 &le; limits.length &le; 5,000", "1 &le; limits[i] &le; 10<sup>9</sup>"],
    hints=["If you want k groups, the cheapest choice is group sizes 1, 2, ..., k, so you need k(k+1)/2 item uses in total and at least k distinct kinds.",
           "A single kind can be used only once per group, but kinds with small limits are used up quickly. Think about adding kinds in increasing order of their limits and keeping the total supply seen so far.",
           "Sort the limits. Walk through them in increasing order with a running total. Each time the total reaches (groups + 1)(groups + 2) / 2, one more group becomes affordable: increase the group count by one."],
    editorial=["First, if k groups are possible then groups of sizes exactly <code>1, 2, ..., k</code> are possible too (shrink the groups from the largest down; this only frees supply and keeps sizes strictly increasing). So we ask for the largest <code>k</code> such that groups of sizes <code>1..k</code> can be filled. They need <code>k(k+1)/2</code> uses in total, so the total supply must be at least that, and also at least <code>k</code> kinds are required.",
               "Algorithm: sort the limits ascending, keep <code>total</code> (the sum of all limits seen so far) and <code>groups</code> (initially 0). For each limit add it to <code>total</code>; if <code>total &ge; (groups + 1)(groups + 2) / 2</code> then the next group, of size <code>groups + 1</code>, can be afforded, so increase <code>groups</code>. Each kind can raise the count by at most one, which guarantees there are always enough distinct kinds: when <code>groups</code> reaches <code>g</code>, at least <code>g</code> kinds have been looked at.",
               "Why the unused supply of small kinds can simply be carried forward: groups are built from the biggest down, so the biggest groups take one item from each of the kinds with the largest limits, while the leftover of the small-limit kinds is exactly what the small groups consume. A formal proof is a Hall-type counting argument; the randomized brute force (all ways to choose the groups) used for this problem confirms the rule. Sorting dominates: O(n log n)."],
    time="O(n log n)", space="O(1) extra (ignoring sort)",
    solution='''def maxGroups(limits):
    total = 0
    groups = 0
    for x in sorted(limits):
        total += x
        if total >= (groups + 1) * (groups + 2) // 2:
            groups += 1
    return groups
''',
    tests=[[[1, 2, 5]], [[2, 1, 2]], [[1, 1]], [[1]], [[1000000000]], [[3, 3, 3]], [[1, 1, 1, 1, 1, 1]], [[5, 5, 5, 5, 5]], [[1, 2, 3, 4, 5, 6]],
           [[1, 1, 1, 1, 100]], [[4, 4, 4, 4]]],
)
_r = rnd(6111)
p["tests"].append([[_r.randint(1, 10 ** 9) for _ in range(3500)]])
p["tests"].append([[_r.randint(1, 100) for _ in range(5000)]])
p["tests"].append([[1] * 4000 + [2] * 1000])
p["tests"].append([[5000] * 5000])


def b_groups2(limits):
    from functools import lru_cache
    n = len(limits)
    masks = [(m, bin(m).count("1")) for m in range(1, 1 << n)]

    @lru_cache(maxsize=None)
    def go(rem, last):
        best = 0
        for m, sz in masks:
            if sz > last and all(rem[i] > 0 for i in range(n) if (m >> i) & 1):
                nr = tuple(rem[i] - ((m >> i) & 1) for i in range(n))
                best = max(best, 1 + go(nr, sz))
        return best

    return go(tuple(limits), 0)


def v_groups2(tests):
    for t in tests:
        a = t["args"][0]
        assert 1 <= len(a) <= 5000 and all(1 <= x <= 10 ** 9 for x in a)
        assert 1 <= t["expected"] <= len(a)


CHECKS["max-groups-growing-size-usage-limits"] = (b_groups2, lambda r: [[r.randint(1, 5) for _ in range(r.randint(1, 4))]], "exact")
VALIDATE["max-groups-growing-size-usage-limits"] = v_groups2
