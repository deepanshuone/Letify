"""Problems: greedy, exchange-argument classics (pairing, ordering, connecting). See data/lib.py for the registry."""
import heapq
from fractions import Fraction
from functools import cmp_to_key
from itertools import combinations, permutations

from lib import add, rnd, CHECKS, VALIDATE, gen_arr  # noqa: F401

INT_MIN, INT_MAX = -(2 ** 31), 2 ** 31 - 1
MOD = 10 ** 9 + 7
T = "Greedy"


# ---------------------------------------------------------------- EASY

p = add(
    id="candies-every-third-free", title="Every Third Candy Free", diff="Easy", topic=T,
    fn="minCandyCost", params=[("prices", "int[]")], ret="int", cmp="exact",
    desc="<p>A candy shop has a special offer. Whenever you pay for two candies, you may also take a third candy for free, provided the free candy costs <strong>no more than either</strong> of the two candies you paid for. Every candy can be paid for or taken for free, but only once, and you want to end up with <strong>all</strong> the candies in <code>prices</code>.</p><p>Return the minimum total amount of money you have to pay.</p><pre>prices = [1, 2, 3]            -> 5   (pay 3 and 2, take 1 free)\nprices = [6, 5, 7, 9, 2, 2]   -> 23  (pay 9 and 7, take 6 free; pay 5 and 2, take 2 free)</pre><p>Candies that cannot be put into such a group of three are simply paid for.</p>",
    constraints=["1 &le; prices.length &le; 5,000", "1 &le; prices[i] &le; 1,000"],
    hints=["Every free candy must be matched with two paid candies that are at least as expensive. You want the free candies to be as expensive as possible.",
           "Look at the most expensive candy. Can it ever be free? What is the best thing to pair it with?",
           "Sort in descending order and cut into consecutive groups of three. In each full group the first two are paid and the third (the cheapest of the group) is free."],
    editorial=["A free candy must be the cheapest of its group of three, so a group costs the sum of its three prices minus its minimum. To save as much as possible, the free candies should be expensive, which means the two paid candies of each group should be only <em>slightly</em> more expensive than the free one.",
               "Sort in descending order and take the candies three at a time: positions 0 and 1 are paid, position 2 is free, positions 3 and 4 are paid, position 5 is free, and so on. The exchange argument: if some free candy is not the third in its descending block, swapping it with a more expensive candy that is paid for (and still allowed by the rule) never increases the total. A trailing block with one or two candies is paid in full. Sorting dominates, so the cost is O(n log n)."],
    time="O(n log n)", space="O(1) extra (ignoring sort)",
    solution='''def minCandyCost(prices):
    prices = sorted(prices, reverse=True)
    total = 0
    for i, x in enumerate(prices):
        if i % 3 != 2:
            total += x
    return total
''',
    tests=[[[1, 2, 3]], [[6, 5, 7, 9, 2, 2]], [[5]], [[5, 5]], [[3, 1]], [[4, 4, 4]], [[10, 1, 1, 1, 10, 10]],
           [[7] * 7], [[1, 2, 3, 4, 5, 6, 7, 8, 9, 10]], [[1000, 1, 1000, 1, 1000, 1, 1000]]],
)
_r = rnd(5001)
p["tests"].append([[_r.randint(1, 1000) for _ in range(5000)]])
p["tests"].append([[1000] * 2500 + [1] * 2500])
p["tests"].append([[_r.randint(900, 1000) for _ in range(4999)]])


def b_candies(prices):
    n = len(prices)
    memo = {}

    def f(mask):
        if mask == 0:
            return 0
        if mask in memo:
            return memo[mask]
        i = (mask & -mask).bit_length() - 1
        rest = mask ^ (1 << i)
        best = prices[i] + f(rest)
        idx = [j for j in range(n) if (rest >> j) & 1]
        for j, k in combinations(idx, 2):
            grp = (prices[i], prices[j], prices[k])
            cost = sum(grp) - min(grp)
            best = min(best, cost + f(rest ^ (1 << j) ^ (1 << k)))
        memo[mask] = best
        return best

    return f((1 << n) - 1)


def v_candies(tests):
    for t in tests:
        a = t["args"][0]
        assert 1 <= len(a) <= 5000 and all(1 <= x <= 1000 for x in a)


CHECKS["candies-every-third-free"] = (b_candies, lambda r: [[r.randint(1, 8) for _ in range(r.randint(1, 8))]], "exact")
VALIDATE["candies-every-third-free"] = v_candies


p = add(
    id="maximize-sum-of-pair-minimums", title="Maximize Sum of Pair Minimums", diff="Easy", topic=T, tier="common",
    fn="maxPairMinSum", params=[("nums", "int[]")], ret="int", cmp="exact",
    desc="<p>The array <code>nums</code> contains <code>2n</code> integers. Split them into <code>n</code> pairs (every element belongs to exactly one pair). The score of a pairing is the sum of the <strong>smaller</strong> element of each pair.</p><p>Return the largest score that any pairing can achieve.</p><pre>nums = [1, 4, 3, 2]   -> 4   (pairs (1,2) and (3,4): 1 + 3)\nnums = [6, 2, 6, 5, 1, 2] -> 9  (pairs (1,2), (2,5), (6,6): 1 + 2 + 6)</pre>",
    constraints=["2 &le; nums.length &le; 8,000 and nums.length is even", "-10,000 &le; nums[i] &le; 10,000"],
    hints=["In each pair only the smaller element counts; the larger one is 'wasted'. How can you waste as little as possible?",
           "Consider the largest element. Whatever it is paired with, the largest element is wasted. Which partner loses the least?",
           "Sort the array and pair neighbours: (0,1), (2,3), ... The answer is the sum of the elements at the even positions."],
    editorial=["Each pair contributes its minimum, so the 'wasted' amount in a pair is the difference between its two elements. The total score is the sum of all elements minus the sum of the pairs' differences, hmm, more precisely the sum of the larger elements is lost. Pairing the largest element with the second largest wastes the least: the second largest would not have counted for more than its own value anyway.",
               "Exchange argument: if the largest element x is paired with y while the second largest z is paired with w, then swapping to (x, z) and (y, w) keeps min(y,w) &ge; ... and the new score is at least as large. Repeating this shows that pairing neighbours in sorted order is optimal. So sort and add the elements at indices 0, 2, 4, ... in O(n log n)."],
    time="O(n log n)", space="O(1) extra (ignoring sort)",
    solution='''def maxPairMinSum(nums):
    nums = sorted(nums)
    return sum(nums[0::2])
''',
    tests=[[[1, 4, 3, 2]], [[6, 2, 6, 5, 1, 2]], [[1, 1]], [[-5, 5]], [[-1, -2, -3, -4]], [[0, 0, 0, 0]],
           [[10000, -10000, 10000, -10000]], [[5, 5, 5, 5, 5, 5]], [[9, 8, 7, 6, 5, 4, 3, 2, 1, 0]], [[3, -3, 2, -2, 1, -1]]],
)
_r = rnd(5002)
p["tests"].append([[_r.randint(-10000, 10000) for _ in range(8000)]])
p["tests"].append([[_r.randint(9990, 10000) for _ in range(8000)]])
p["tests"].append([[_r.randint(-10000, 10000) for _ in range(5000)]])


def b_pairmin(nums):
    nums = list(nums)

    def go(items):
        if not items:
            return 0
        a = items[0]
        best = None
        for j in range(1, len(items)):
            rest = items[1:j] + items[j + 1:]
            v = min(a, items[j]) + go(rest)
            if best is None or v > best:
                best = v
        return best

    return go(nums)


def v_pairmin(tests):
    for t in tests:
        a = t["args"][0]
        assert 2 <= len(a) <= 8000 and len(a) % 2 == 0 and all(-10000 <= x <= 10000 for x in a)


CHECKS["maximize-sum-of-pair-minimums"] = (b_pairmin, lambda r: [[r.randint(-6, 6) for _ in range(2 * r.randint(1, 4))]], "exact")
VALIDATE["maximize-sum-of-pair-minimums"] = v_pairmin


p = add(
    id="minimum-scalar-product-reordered", title="Minimum Dot Product After Reordering", diff="Easy", topic=T, tier="extra",
    fn="minDotProduct", params=[("a", "int[]"), ("b", "int[]")], ret="int", cmp="exact",
    desc="<p>You are given two integer arrays <code>a</code> and <code>b</code> of the same length <code>n</code>. You may rearrange the elements of <code>a</code> in any order you like (the order of <code>b</code> is fixed). After rearranging, the <em>dot product</em> is <code>a[0]*b[0] + a[1]*b[1] + ... + a[n-1]*b[n-1]</code>.</p><p>Return the smallest dot product that can be obtained.</p><pre>a = [1, 3, -5], b = [-2, 4, 1]   -> -25\n(rearrange a to [1, -5, 3]... no: [3, 1, -5] with b gives -6 + 4 - 5 = -7; the best order is [-5, 3, 1]... )</pre>",
    constraints=["1 &le; n &le; 5,000", "-100 &le; a[i], b[i] &le; 100"],
    hints=["Try all orders for tiny arrays and look at which element of <code>a</code> ends up opposite which element of <code>b</code>.",
           "To make the sum small you want large positive numbers multiplied by small (very negative) ones. Which of a's elements should face the largest element of b?",
           "Sort <code>a</code> ascending and <code>b</code> descending and multiply element by element (the rearrangement inequality)."],
    editorial=["Suppose in some arrangement a[i] &lt; a[j] but b[i] &lt; b[j] as well. Then <code>a[i]*b[i] + a[j]*b[j]</code> is not smaller than <code>a[i]*b[j] + a[j]*b[i]</code>, because the difference is <code>(a[j]-a[i])*(b[j]-b[i]) &ge; 0</code>. So swapping the two a-values never makes the product worse. Repeating until no such pair remains gives the arrangement where the order of a is the opposite of the order of b.",
               "Implementation: sort a ascending, sort b descending, add up the products. That is O(n log n); the result is at most 5,000 &times; 10,000 in absolute value, well inside 32-bit range."],
    time="O(n log n)", space="O(n)",
    solution='''def minDotProduct(a, b):
    a = sorted(a)
    b = sorted(b, reverse=True)
    return sum(x * y for x, y in zip(a, b))
''',
    tests=[[[1, 3, -5], [-2, 4, 1]], [[1], [1]], [[-3], [4]], [[0, 0], [5, -5]], [[1, 2, 3], [4, 5, 6]], [[-1, -2, -3], [-4, -5, -6]],
           [[100, -100], [100, -100]], [[2, 2, 2], [3, -3, 3]], [[1, -1, 1, -1], [1, 1, -1, -1]], [[5, 4, 3, 2, 1], [1, 2, 3, 4, 5]]],
)
_r = rnd(5003)
p["tests"].append([[_r.randint(-100, 100) for _ in range(5000)], [_r.randint(-100, 100) for _ in range(5000)]])
p["tests"].append([[_r.randint(1, 100) for _ in range(5000)], [_r.randint(1, 100) for _ in range(5000)]])
p["tests"].append([[-100] * 2500 + [100] * 2500, [100] * 2500 + [-100] * 2500])


def b_dot(a, b):
    return min(sum(x * y for x, y in zip(perm, b)) for perm in permutations(a))


def v_dot(tests):
    for t in tests:
        a, b = t["args"]
        assert len(a) == len(b) and 1 <= len(a) <= 5000
        assert all(-100 <= x <= 100 for x in a + b)


def g_dot(r):
    n = r.randint(1, 6)
    return [[r.randint(-5, 5) for _ in range(n)], [r.randint(-5, 5) for _ in range(n)]]


CHECKS["minimum-scalar-product-reordered"] = (b_dot, g_dot, "exact")
VALIDATE["minimum-scalar-product-reordered"] = v_dot


# ---------------------------------------------------------------- MEDIUM

p = add(
    id="fractional-knapsack-floor-value", title="Fractional Knapsack Floor Value", diff="Medium", topic=T, tier="common",
    fn="fractionalKnapsack", params=[("items", "int[][]"), ("capacity", "int")], ret="int", cmp="exact",
    desc="<p>Each item is given as <code>[value, weight]</code>. You have a bag that can carry total weight at most <code>capacity</code>. Unlike the 0/1 knapsack, items are <strong>divisible</strong>: you may take any fraction <code>f</code> (<code>0 &le; f &le; 1</code>) of an item, which adds <code>f * value</code> to your loot and <code>f * weight</code> to the load.</p><p>The best possible total value may not be an integer. Return it rounded <strong>down</strong> to the nearest integer.</p><pre>items = [[60, 10], [100, 20], [120, 30]], capacity = 50   -> 240\nitems = [[10, 3]], capacity = 2                           -> 6   (2/3 of 10 is 6.67)</pre>",
    constraints=["1 &le; items.length &le; 3,000", "1 &le; value, weight &le; 1,000", "0 &le; capacity &le; 1,000,000"],
    hints=["If you could only take whole items this would be a hard problem. What changes when you can take parts?",
           "Think of the value per unit of weight of each item. Where would you put your next unit of capacity?",
           "Sort the items by value/weight in descending order (compare with cross-multiplication to avoid decimals). Take whole items while they fit; for the first item that does not fit take the fraction that fills the bag exactly. The answer is the whole values plus floor(value * remaining / weight)."],
    editorial=["Every unit of weight of item <code>i</code> is worth <code>v_i / w_i</code>. If a unit with a lower ratio is in the bag while a unit with a higher ratio is left out, swapping them increases the value, so an optimal bag takes items in descending ratio order. All items before the 'critical' item are taken whole, the critical item is taken partially, and the rest are ignored.",
               "Sort by ratio using the comparison <code>v_i * w_j &gt; v_j * w_i</code> (integers only). Let <code>rem</code> be the remaining capacity; if an item fits entirely add its value and subtract its weight, otherwise add <code>floor(v * rem / w)</code> and stop. Because the whole values are integers, flooring only the final fraction gives the floor of the total. O(n log n) time."],
    time="O(n log n)", space="O(n)",
    solution='''from functools import cmp_to_key


def fractionalKnapsack(items, capacity):
    def cmp(x, y):
        # larger value/weight first
        return y[0] * x[1] - x[0] * y[1]

    order = sorted(items, key=cmp_to_key(lambda x, y: -(x[0] * y[1] - y[0] * x[1])))
    total = 0
    rem = capacity
    for v, w in order:
        if rem == 0:
            break
        if w <= rem:
            total += v
            rem -= w
        else:
            total += (v * rem) // w
            rem = 0
    return total
''',
    tests=[[[[60, 10], [100, 20], [120, 30]], 50], [[[10, 3]], 2], [[[10, 3]], 0], [[[10, 3]], 3], [[[10, 3]], 100],
           [[[5, 5], [5, 5], [5, 5]], 7], [[[1, 1000], [1000, 1]], 1], [[[1, 1000]], 1], [[[7, 2], [9, 3], [4, 1]], 4],
           [[[1000, 1], [1000, 1], [1000, 1]], 2], [[[3, 7], [2, 5], [4, 9], [1, 3]], 10]],
)
_r = rnd(5004)
p["tests"].append([[[_r.randint(1, 1000), _r.randint(1, 1000)] for _ in range(3000)], 500000])
p["tests"].append([[[_r.randint(1, 1000), _r.randint(1, 1000)] for _ in range(3000)], 1000000])
p["tests"].append([[[_r.randint(900, 1000), _r.randint(900, 1000)] for _ in range(3000)], 777777])


def b_frac(items, capacity):
    n = len(items)
    best = Fraction(0)
    for mask in range(1 << n):
        w = sum(items[i][1] for i in range(n) if (mask >> i) & 1)
        if w > capacity:
            continue
        val = Fraction(sum(items[i][0] for i in range(n) if (mask >> i) & 1))
        best = max(best, val)
        rem = capacity - w
        for j in range(n):
            if (mask >> j) & 1:
                continue
            f = min(Fraction(1), Fraction(rem, items[j][1]))
            best = max(best, val + f * items[j][0])
    return best.numerator // best.denominator


def g_frac(r):
    n = r.randint(1, 6)
    return [[[r.randint(1, 9), r.randint(1, 9)] for _ in range(n)], r.randint(0, 30)]


def v_frac(tests):
    for t in tests:
        items, cap = t["args"]
        assert 1 <= len(items) <= 3000 and 0 <= cap <= 10 ** 6
        assert all(len(x) == 2 and 1 <= x[0] <= 1000 and 1 <= x[1] <= 1000 for x in items)


CHECKS["fractional-knapsack-floor-value"] = (b_frac, g_frac, "exact")
VALIDATE["fractional-knapsack-floor-value"] = v_frac


p = add(
    id="max-strict-wins-by-reordering", title="Maximum Wins by Reordering", diff="Medium", topic=T,
    fn="maxWins", params=[("mine", "int[]"), ("theirs", "int[]")], ret="int", cmp="exact",
    desc="<p>Two players each have <code>n</code> cards. In round <code>i</code> your card <code>mine[i]</code> is played against the opponent's card <code>theirs[i]</code>, and you win the round when <code>mine[i] &gt; theirs[i]</code> (ties are not wins).</p><p>The opponent's order is fixed and known. You may arrange your own cards in <strong>any order</strong> before the game starts. Return the largest number of rounds you can win.</p><pre>mine = [2, 7, 11, 15], theirs = [1, 10, 4, 11]   -> 4\nmine = [2, 2, 2],      theirs = [2, 2, 2]        -> 0</pre>",
    constraints=["1 &le; n = mine.length = theirs.length &le; 4,000", "0 &le; mine[i], theirs[i] &le; 1,000,000"],
    hints=["Since you may reorder freely, only the multiset of the opponent's cards matters, not their order.",
           "Do not waste a strong card on a weak opponent card if a weaker card of yours would already win. Which of your cards should beat the opponent's weakest card?",
           "Sort both. Walk through your cards from weakest to strongest and keep a pointer to the opponent's weakest unbeaten card: if your card is strictly larger, it wins that card and the pointer moves on; otherwise this card is useless against all remaining cards (they are at least as big)."],
    editorial=["After sorting, think of it as a matching problem: every win pairs one of your cards with a strictly smaller opponent card. Process your cards from smallest to largest. The smallest opponent card not yet beaten is the easiest target, so if your current card beats it, use it there; if it does not, then this card cannot beat any remaining card and it can only be used as a 'sacrifice' in a losing round.",
               "Exchange argument: if an optimal solution beats the weakest unbeaten opponent card with a stronger card than necessary, swap it with the smallest card that still beats it; nobody else loses. The two-pointer scan counts the wins in O(n) after the O(n log n) sort."],
    time="O(n log n)", space="O(n)",
    solution='''def maxWins(mine, theirs):
    mine = sorted(mine)
    theirs = sorted(theirs)
    j = 0
    for x in mine:
        if x > theirs[j]:
            j += 1
    return j
''',
    tests=[[[2, 7, 11, 15], [1, 10, 4, 11]], [[2, 2, 2], [2, 2, 2]], [[5], [4]], [[4], [5]], [[0], [0]],
           [[1, 2, 3], [3, 2, 1]], [[3, 3, 3], [1, 2, 3]], [[1, 1, 1, 1], [0, 0, 0, 0]], [[10, 20], [5, 5]],
           [[1, 5, 9, 13], [4, 8, 12, 16]], [[1000000, 0, 1000000], [999999, 1000000, 0]]],
)
_r = rnd(5005)
p["tests"].append([[_r.randint(0, 1000000) for _ in range(4000)], [_r.randint(0, 1000000) for _ in range(4000)]])
p["tests"].append([[_r.randint(0, 100) for _ in range(4000)], [_r.randint(0, 100) for _ in range(4000)]])
p["tests"].append([list(range(1, 4001)), list(range(0, 4000))])


def b_wins(mine, theirs):
    return max(sum(1 for x, y in zip(perm, theirs) if x > y) for perm in permutations(mine))


def g_wins(r):
    n = r.randint(1, 6)
    return [[r.randint(0, 6) for _ in range(n)], [r.randint(0, 6) for _ in range(n)]]


def v_wins(tests):
    for t in tests:
        a, b = t["args"]
        assert len(a) == len(b) and 1 <= len(a) <= 4000
        assert all(0 <= x <= 10 ** 6 for x in a + b)


CHECKS["max-strict-wins-by-reordering"] = (b_wins, g_wins, "exact")
VALIDATE["max-strict-wins-by-reordering"] = v_wins


p = add(
    id="mice-to-holes-minimum-longest-run", title="Mice and Holes: Shortest Longest Run", diff="Medium", topic=T, tier="common",
    fn="minLongestRun", params=[("mice", "int[]"), ("holes", "int[]")], ret="int", cmp="exact",
    desc="<p>Mice and holes sit on a number line. <code>mice[i]</code> is the position of the <i>i</i>-th mouse and <code>holes[j]</code> is the position of the <i>j</i>-th hole; both arrays have the same length <code>n</code>. Every mouse must run to a hole and every hole takes exactly one mouse. A mouse that runs from <code>x</code> to <code>y</code> travels <code>|x - y|</code>.</p><p>All mice run at the same time, so the rescue takes as long as the <em>longest single run</em>. Choose the assignment of mice to holes that makes this longest run as short as possible and return its length.</p><pre>mice = [4, -4, 2], holes = [4, 0, 5]   -> 4\nmice = [1, 5],     holes = [2, 6]      -> 1</pre><p>In the first example the mouse at -4 must reach the hole at 0 (run 4), the mouse at 2 takes the hole at 4 (run 2) and the mouse at 4 takes the hole at 5 (run 1).</p>",
    constraints=["1 &le; n = mice.length = holes.length &le; 3,000", "-10<sup>9</sup> &le; mice[i], holes[j] &le; 10<sup>9</sup>", "Several mice or holes may share a position"],
    hints=["Take two mice and two holes on the line. If the mice are in order a &le; b and the holes in order c &le; d, compare the assignments a&rarr;c, b&rarr;d and a&rarr;d, b&rarr;c. Which one has the smaller longest run?",
           "Crossing paths never helps: swapping a crossing pair of assignments to a non-crossing one cannot increase the larger of the two distances.",
           "Sort both arrays, match the i-th smallest mouse with the i-th smallest hole, and return the maximum of <code>|mice[i] - holes[i]|</code>."],
    editorial=["Suppose mice <code>a &le; b</code> are assigned to holes <code>d</code> and <code>c</code> with <code>c &le; d</code> (a crossing pair). Re-assign them as a&rarr;c and b&rarr;d. On a line, each of the two new distances is at most the larger of the two old distances: every new run is contained in the span covered by the old ones, so the longest run of the pair does not grow. Repeating this removes all crossings without making the answer worse.",
               "An assignment without crossings is exactly the sorted matching, so after sorting both arrays the answer is <code>max |mice[i] - holes[i]|</code>. Sorting dominates: O(n log n) time, O(n) extra space. A binary search over the answer with a feasibility check would also work but is unnecessary."],
    time="O(n log n)", space="O(n)",
    solution='''def minLongestRun(mice, holes):
    a = sorted(mice)
    b = sorted(holes)
    return max(abs(x - y) for x, y in zip(a, b))
''',
    tests=[[[4, -4, 2], [4, 0, 5]], [[1, 5], [2, 6]], [[7], [7]], [[0], [1000000000]], [[-1000000000], [1000000000]],
           [[3, 3, 3], [3, 3, 3]], [[1, 2, 3], [3, 2, 1]], [[0, 10], [5, 6]], [[-5, -1, 8, 20], [-6, 0, 9, 40]],
           [[5, 5, 5, 5], [1, 2, 9, 10]], [[-1000000000, 1000000000], [1000000000, -1000000000]]],
)
_r = rnd(5006)
p["tests"].append([[_r.randint(-10 ** 9, 10 ** 9) for _ in range(2500)], [_r.randint(-10 ** 9, 10 ** 9) for _ in range(2500)]])
p["tests"].append([[_r.randint(-1000, 1000) for _ in range(3000)], [_r.randint(-1000, 1000) for _ in range(3000)]])
_a = [_r.randint(-10 ** 6, 10 ** 6) for _ in range(3000)]
p["tests"].append([_a, [x + _r.randint(-50, 50) for x in _a][::-1]])


def b_wct(mice, holes):
    return min(max(abs(x - y) for x, y in zip(mice, perm)) for perm in permutations(holes))


def g_wct(r):
    n = r.randint(1, 6)
    return [[r.randint(-12, 12) for _ in range(n)], [r.randint(-12, 12) for _ in range(n)]]


def v_wct(tests):
    for t in tests:
        mice, holes = t["args"]
        assert len(mice) == len(holes) and 1 <= len(mice) <= 3000
        assert all(-10 ** 9 <= x <= 10 ** 9 for x in mice + holes)


CHECKS["mice-to-holes-minimum-longest-run"] = (b_wct, g_wct, "exact")
VALIDATE["mice-to-holes-minimum-longest-run"] = v_wct


p = add(
    id="min-paired-shifts-to-match-multisets", title="Minimum Shifts to Match Another Array", diff="Medium", topic=T, tier="extra",
    fn="minShifts", params=[("nums", "int[]"), ("target", "int[]")], ret="int", cmp="exact",
    desc="<p>In one operation you choose two different indices <code>i</code> and <code>j</code> of <code>nums</code> and do <code>nums[i] += 2</code> and <code>nums[j] -= 2</code> (values may become any integer, including negative ones).</p><p>The array <code>nums</code> is said to <em>match</em> <code>target</code> when both contain the same values with the same multiplicities, in any order. Return the minimum number of operations needed to make <code>nums</code> match <code>target</code>. The input guarantees that this is possible.</p><pre>nums = [8, 12, 6], target = [2, 14, 10]   -> 2\nnums = [1, 2, 5],  target = [4, 1, 3]     -> 1</pre>",
    constraints=["1 &le; n = nums.length = target.length &le; 4,000", "1 &le; nums[i], target[i] &le; 100,000", "It is always possible to make nums match target"],
    hints=["An operation never changes the parity of any element, so even values can only turn into even values and odd values into odd values.",
           "That splits the task into two independent ones: an even group and an odd group. Within one group, which element of nums should become which element of target?",
           "Sort the even values of both arrays and pair them in order (same for the odd values). Sum the absolute differences of all pairs; every operation fixes at most 2 units on the 'too small' side and 2 units on the 'too large' side, so the answer is that sum divided by 4."],
    editorial=["The parity argument fixes the two groups. Inside a group, the cheapest way to turn one multiset into another by moving values is to match the sorted lists position by position (the same exchange argument as for minimizing the sum of absolute differences of a matching).",
               "Let <code>D</code> be the total amount by which elements must go up. Since the sums are equal, the total amount by which elements must go down is also <code>D</code>, and the sum of all absolute differences is <code>2D</code>. One operation raises one element by 2 and lowers another by 2, so exactly <code>D / 2</code> operations are needed and enough; this equals (sum of absolute differences) / 4. Sorting makes it O(n log n)."],
    time="O(n log n)", space="O(n)",
    solution='''def minShifts(nums, target):
    total = 0
    for par in (0, 1):
        a = sorted(x for x in nums if x % 2 == par)
        b = sorted(x for x in target if x % 2 == par)
        for x, y in zip(a, b):
            total += abs(x - y)
    return total // 4
''',
    tests=[[[8, 12, 6], [2, 14, 10]], [[1, 2, 5], [4, 1, 3]], [[5], [5]], [[3, 7], [3, 7]], [[3, 7], [5, 5]], [[2, 4], [4, 2]],
           [[1, 1, 1, 5], [3, 3, 1, 1]], [[10, 20, 30], [20, 20, 20]], [[1, 100000], [99999, 2]],
           [[1, 2, 3, 4, 5, 6], [6, 5, 4, 3, 2, 1]], [[9, 9, 9], [1, 13, 13]]],
)
_r = rnd(5007)


def _mk(n, hi, ops):
    a = [_r.randint(1, hi) for _ in range(n)]
    b = list(a)
    for _ in range(ops):
        i, j = _r.sample(range(n), 2)
        if b[j] - 2 >= 1:
            b[i] += 2
            b[j] -= 2
    _r.shuffle(b)
    return [a, b]


p["tests"].append(_mk(4000, 100000, 20000))
p["tests"].append(_mk(4000, 60, 30000))
p["tests"].append(_mk(3000, 100000, 3))


def b_shifts(nums, target):
    start = tuple(sorted(nums))
    goal = tuple(sorted(target))
    lo, hi = min(start + goal) - 4, max(start + goal) + 4
    seen = {start}
    frontier = [start]
    d = 0
    while frontier:
        if goal in seen:
            return d
        nxt = []
        for s in frontier:
            for i in range(len(s)):
                for j in range(len(s)):
                    if i == j:
                        continue
                    if s[i] + 2 > hi or s[j] - 2 < lo:
                        continue
                    t = list(s)
                    t[i] += 2
                    t[j] -= 2
                    t = tuple(sorted(t))
                    if t not in seen:
                        seen.add(t)
                        nxt.append(t)
        frontier = nxt
        d += 1
    return -1


def g_shifts(r):
    n = r.randint(1, 4)
    a = [r.randint(1, 6) for _ in range(n)]
    b = list(a)
    for _ in range(r.randint(0, 4)):
        if n >= 2:
            i, j = r.sample(range(n), 2)
            b[i] += 2
            b[j] -= 2
    r.shuffle(b)
    return [a, b]


def v_shifts(tests):
    for t in tests:
        a, b = t["args"]
        assert len(a) == len(b) and 1 <= len(a) <= 4000
        assert all(1 <= x <= 100000 for x in a + b)
        assert sum(a) == sum(b)
        assert sum(x % 2 for x in a) == sum(x % 2 for x in b)
        for par in (0, 1):
            s = sum(abs(x - y) for x, y in zip(sorted(x for x in a if x % 2 == par), sorted(x for x in b if x % 2 == par)))
        total = sum(abs(x - y) for par in (0, 1) for x, y in zip(sorted(x for x in a if x % 2 == par), sorted(x for x in b if x % 2 == par)))
        assert total % 4 == 0, "not solvable"


CHECKS["min-paired-shifts-to-match-multisets"] = (b_shifts, g_shifts, "exact")
VALIDATE["min-paired-shifts-to-match-multisets"] = v_shifts


p = add(
    id="max-disjoint-pairs-with-min-gap", title="Maximum Pairs With a Minimum Gap", diff="Medium", topic=T,
    fn="maxGapPairs", params=[("nums", "int[]"), ("d", "int")], ret="int", cmp="exact",
    desc="<p>Form as many <strong>disjoint</strong> pairs of elements of <code>nums</code> as possible, where a pair of two different positions <code>i</code> and <code>j</code> is allowed only if <code>|nums[i] - nums[j]| &ge; d</code>. Each position can be used in at most one pair, and you do not have to use all positions.</p><p>Return the maximum number of pairs.</p><pre>nums = [1, 3, 5, 8, 10], d = 4   -> 2   (1 with 5, 3 with 8... or 1 with 8 and 3 with 10)\nnums = [1, 3, 5, 8, 10], d = 8   -> 1   (only 1 with 10 has gap 9)</pre>",
    constraints=["1 &le; nums.length &le; 5,000", "0 &le; nums[i] &le; 1,000,000", "0 &le; d &le; 1,000,000"],
    hints=["Note that at most <code>n // 2</code> pairs can exist at all. Sorting the array does not hurt: only values matter.",
           "If k pairs are possible, then they can be chosen so that the k smallest numbers are matched with the k largest numbers. Why?",
           "Binary search on k (feasibility is monotone): sort, then check that <code>a[i] + d &le; a[n - k + i]</code> for every <code>i &lt; k</code>, i.e. the i-th smallest is matched with the i-th of the k largest."],
    editorial=["Sort the numbers. Suppose an optimal answer has k pairs. Exchange argument: using the k smallest values as the 'lower' members and the k largest values as the 'upper' members never hurts, since replacing a lower member with a smaller number or an upper member with a larger number can only increase gaps. Inside those two groups, pairing the i-th smallest with the i-th of the large group (in sorted order) is the best arrangement, because crossing pairs would shrink the smallest gap.",
               "So k is feasible iff <code>a[i + n - k] - a[i] &ge; d</code> for all <code>0 &le; i &lt; k</code>. If k works, k-1 works too, so binary search over k in [0, n//2]. Each check is O(k), total O(n log n) including the sort."],
    time="O(n log n)", space="O(n)",
    solution='''def maxGapPairs(nums, d):
    a = sorted(nums)
    n = len(a)

    def ok(k):
        for i in range(k):
            if a[n - k + i] - a[i] < d:
                return False
        return True

    lo, hi = 0, n // 2
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if ok(mid):
            lo = mid
        else:
            hi = mid - 1
    return lo
''',
    tests=[[[1, 3, 5, 8, 10], 4], [[1, 3, 5, 8, 10], 8], [[5], 0], [[5, 5], 0], [[5, 5], 1], [[1, 2], 1], [[7, 7, 7, 7], 0],
           [[1, 1, 1, 9, 9, 9], 8], [[1, 1, 1, 9, 9, 9], 9], [[0, 1000000], 1000000], [[2, 4, 6, 8, 10, 12, 14], 5]],
)
_r = rnd(5008)
p["tests"].append([[_r.randint(0, 1000000) for _ in range(5000)], 300000])
p["tests"].append([[_r.randint(0, 1000000) for _ in range(5000)], 900000])
p["tests"].append([[_r.randint(0, 1000) for _ in range(4999)], 1])


def b_gap(nums, d):
    n = len(nums)
    memo = {}

    def f(mask):
        if mask in memo:
            return memo[mask]
        if mask == 0:
            return 0
        i = (mask & -mask).bit_length() - 1
        rest = mask ^ (1 << i)
        best = f(rest)  # i is unused
        for j in range(n):
            if (rest >> j) & 1 and abs(nums[i] - nums[j]) >= d:
                best = max(best, 1 + f(rest ^ (1 << j)))
        memo[mask] = best
        return best

    return f((1 << n) - 1)


def g_gap(r):
    return [[r.randint(0, 10) for _ in range(r.randint(1, 9))], r.randint(0, 10)]


def v_gap(tests):
    for t in tests:
        nums, d = t["args"]
        assert 1 <= len(nums) <= 5000 and all(0 <= x <= 10 ** 6 for x in nums) and 0 <= d <= 10 ** 6


CHECKS["max-disjoint-pairs-with-min-gap"] = (b_gap, g_gap, "exact")
VALIDATE["max-disjoint-pairs-with-min-gap"] = v_gap


p = add(
    id="min-squared-gap-with-k-changes", title="Minimum Squared Differences With K Changes", diff="Medium", topic=T, tier="extra",
    fn="minSquaredGap", params=[("a", "int[]"), ("b", "int[]"), ("k", "int")], ret="int", cmp="exact",
    desc="<p>The arrays <code>a</code> and <code>b</code> have the same length <code>n</code>. The cost of the pair of arrays is <code>(a[0]-b[0])<sup>2</sup> + (a[1]-b[1])<sup>2</sup> + ... + (a[n-1]-b[n-1])<sup>2</sup></code>.</p><p>You may perform <strong>at most</strong> <code>k</code> operations. One operation picks an index <code>i</code> and changes <code>a[i]</code> by exactly <code>+1</code> or <code>-1</code> (values may leave the original range). Return the smallest cost you can reach.</p><pre>a = [1, 5], b = [4, 1], k = 2   -> 13   (gaps 3 and 4 become 3 and 2)\na = [3, 3], b = [3, 3], k = 5   -> 0</pre>",
    constraints=["1 &le; n &le; 3,000", "0 &le; a[i], b[i] &le; 300", "0 &le; k &le; 1,000,000"],
    hints=["Only the gaps <code>|a[i] - b[i]|</code> matter. One operation can lower a gap by one (or raise it, which is never useful).",
           "Lowering a gap of size g by one saves 2g - 1. Which gap saves the most right now?",
           "Always reduce the currently largest gap. To do it fast, sort the gaps descending and lower the top group of equal gaps to the level of the next value, as long as the budget allows; spread the leftover operations over the top group."],
    editorial=["The function g &rarr; g<sup>2</sup> is convex, so each further unit removed from a gap saves less than the previous unit, and the saving from reducing a larger gap is larger. Hence the optimum reduces the largest gap one step at a time, k times (or until all gaps are zero). Doing this literally with a heap is O(k log n), too slow for k = 10<sup>6</sup> combined with large n, but not needed.",
               "Sort the gaps in descending order. Keep a group of the top m gaps all at level <code>cur</code>. Lowering this group to the next gap value costs <code>m * (cur - next)</code> operations. While the budget covers it, pay and enlarge the group. When it does not, divide the remaining budget <code>q, r = divmod(k, m)</code>: <code>r</code> gaps of the group end at <code>cur - q - 1</code> and the other <code>m - r</code> at <code>cur - q</code>. If everything reaches zero the cost is 0. O(n log n) time."],
    time="O(n log n)", space="O(n)",
    solution='''def minSquaredGap(a, b, k):
    d = sorted((abs(x - y) for x, y in zip(a, b)), reverse=True)
    n = len(d)
    d.append(0)
    m = 1
    while m <= n:
        cur = d[m - 1]
        nxt = d[m]
        cost = m * (cur - nxt)
        if k >= cost:
            k -= cost
            m += 1
        else:
            q, r = divmod(k, m)
            level = cur - q
            rest = sum(x * x for x in d[m:n])
            return rest + r * (level - 1) ** 2 + (m - r) * level ** 2
    return 0
''',
    tests=[[[1, 5], [4, 1], 2], [[3, 3], [3, 3], 5], [[0], [10], 0], [[0], [10], 4], [[0], [10], 10], [[0], [10], 11],
           [[0, 0, 0], [5, 5, 5], 4], [[1, 2, 3], [3, 2, 1], 0], [[300, 0], [0, 300], 1000000], [[10, 20, 30, 40], [40, 30, 20, 10], 25],
           [[7, 1, 9], [2, 8, 3], 7]],
)
_r = rnd(5009)
p["tests"].append([[_r.randint(0, 300) for _ in range(3000)], [_r.randint(0, 300) for _ in range(3000)], 100000])
p["tests"].append([[_r.randint(0, 300) for _ in range(3000)], [_r.randint(0, 300) for _ in range(3000)], 1000000])
p["tests"].append([[_r.randint(0, 300) for _ in range(3000)], [_r.randint(0, 300) for _ in range(3000)], 37])


def b_sq(a, b, k):
    n = len(a)
    INF = float("inf")
    # f[j] = min cost using exactly <= j operations on the first i indices
    f = [0] * (k + 1)
    for i in range(n):
        g = [INF] * (k + 1)
        for used in range(k + 1):
            for t in range(0, used + 1):
                for delta in ((t, -t) if t else (0,)):
                    c = f[used - t] + (a[i] + delta - b[i]) ** 2
                    if c < g[used]:
                        g[used] = c
        f = g
    return min(f)


def g_sq(r):
    n = r.randint(1, 4)
    return [[r.randint(0, 9) for _ in range(n)], [r.randint(0, 9) for _ in range(n)], r.randint(0, 8)]


def v_sq(tests):
    for t in tests:
        a, b, k = t["args"]
        assert len(a) == len(b) and 1 <= len(a) <= 3000 and 0 <= k <= 10 ** 6
        assert all(0 <= x <= 300 for x in a + b)


CHECKS["min-squared-gap-with-k-changes"] = (b_sq, g_sq, "exact")
VALIDATE["min-squared-gap-with-k-changes"] = v_sq


# ---------------------------------------------------------------- HARD

p = add(
    id="bridge-and-torch-crossing", title="Bridge and Torch", diff="Hard", topic=T, tier="extra",
    fn="minCrossingTime", params=[("times", "int[]")], ret="int", cmp="exact",
    desc="<p>A group of people must cross a narrow bridge at night. <code>times[i]</code> is the number of minutes person <code>i</code> needs to walk across. There is only one torch, so:</p><ul><li>at most two people may be on the bridge at the same time;</li><li>a group on the bridge always walks at the pace of its <strong>slower</strong> member;</li><li>the torch must be carried back to the start by someone before the next group can cross.</li></ul><p>Return the minimum total number of minutes in which everybody can reach the other side.</p><pre>times = [1, 2, 5, 10]   -> 17\ntimes = [3, 5]          -> 5\ntimes = [4]             -> 4</pre>",
    constraints=["1 &le; times.length &le; 5,000", "1 &le; times[i] &le; 10,000"],
    hints=["Small cases first: one person crosses alone, two cross together, three people can be done in a fixed way. What is the bottleneck for four or more?",
           "Sort the times. The two slowest people should cross together at some point, because otherwise each of them costs a full slow trip alone.",
           "While more than 3 people remain, move the two slowest across using the cheaper of two plans: (a) the fastest escorts the second fastest... i.e. <code>t0 + 2*t1 + t[last]</code>, or (b) the fastest shuttles twice: <code>2*t0 + t[last-1] + t[last]</code>. Then continue with two fewer people. Finish the last 1, 2 or 3 people directly."],
    editorial=["Sort the times ascending. The two slowest people <code>x = t[n-1]</code> and <code>y = t[n-2]</code> must both cross, and the best is to send them together so that only the larger time <code>x</code> is paid. Two ways accomplish this and return the torch: (a) fastest and second fastest cross (cost <code>t1</code>), fastest returns (<code>t0</code>), the two slowest cross (<code>x</code>), second fastest returns (<code>t1</code>): total <code>t0 + 2*t1 + x</code>; (b) fastest escorts the slowest (<code>x</code>), returns (<code>t0</code>), escorts the second slowest (<code>y</code>), returns (<code>t0</code>): total <code>2*t0 + x + y</code>.",
               "After either plan, the two slowest are done and the torch is back with the rest, so the same problem remains with two fewer people. Take the cheaper plan each time (an exchange argument shows no other pattern is better). Base cases: 1 person: <code>t0</code>; 2 people: <code>t1</code>; 3 people: <code>t0 + t1 + t2</code>. Sorting dominates: O(n log n)."],
    time="O(n log n)", space="O(1) extra (ignoring sort)",
    solution='''def minCrossingTime(times):
    t = sorted(times)
    n = len(t)
    total = 0
    while n > 3:
        total += min(t[0] + 2 * t[1] + t[n - 1], 2 * t[0] + t[n - 2] + t[n - 1])
        n -= 2
    if n == 3:
        total += t[0] + t[1] + t[2]
    elif n == 2:
        total += t[1]
    elif n == 1:
        total += t[0]
    return total
''',
    tests=[[[1, 2, 5, 10]], [[3, 5]], [[4]], [[1, 2, 3]], [[7, 7, 7, 7]], [[1, 1, 1, 1, 1]], [[1, 100, 100, 100]],
           [[1, 2, 2, 2, 100, 100]], [[10, 20, 30, 40, 50, 60, 70]], [[1, 2, 5, 10, 20, 50, 100]], [[1, 2]]],
)
_r = rnd(5010)
p["tests"].append([[_r.randint(1, 10000) for _ in range(5000)]])
p["tests"].append([[_r.randint(1, 20) for _ in range(5000)]])
p["tests"].append([[1, 2] + [_r.randint(9000, 10000) for _ in range(4000)]])


def b_bridge(times):
    n = len(times)
    full = (1 << n) - 1
    # state: (mask of people on the far side, torch side 0 = start, 1 = far)
    dist = {(0, 0): 0}
    pq = [(0, 0, 0)]
    while pq:
        d, mask, side = heapq.heappop(pq)
        if dist.get((mask, side), float("inf")) < d:
            continue
        if mask == full:
            return d
        if side == 0:
            near = [i for i in range(n) if not (mask >> i) & 1]
            moves = [(i,) for i in near] + list(combinations(near, 2))
        else:
            far = [i for i in range(n) if (mask >> i) & 1]
            moves = [(i,) for i in far] + list(combinations(far, 2))
        for mv in moves:
            cost = max(times[i] for i in mv)
            nm = mask
            for i in mv:
                nm ^= 1 << i
            ns = 1 - side
            nd = d + cost
            if nd < dist.get((nm, ns), float("inf")):
                dist[(nm, ns)] = nd
                heapq.heappush(pq, (nd, nm, ns))
    return -1


def v_bridge(tests):
    for t in tests:
        a = t["args"][0]
        assert 1 <= len(a) <= 5000 and all(1 <= x <= 10000 for x in a)


CHECKS["bridge-and-torch-crossing"] = (b_bridge, lambda r: [[r.randint(1, 12) for _ in range(r.randint(1, 6))]], "exact")
VALIDATE["bridge-and-torch-crossing"] = v_bridge


p = add(
    id="water-supply-wells-and-pipes", title="Water Supply: Wells and Pipes", diff="Hard", topic=T, tier="common",
    fn="minWaterCost", params=[("wells", "int[]"), ("pipes", "int[][]")], ret="int", cmp="exact",
    desc="<p>A village has <code>n</code> houses numbered <code>1..n</code>. Every house must get water, in one of two ways: dig a well inside the house at cost <code>wells[i-1]</code>, or lay pipes that connect it (directly or through other houses) to a house that has a well.</p><p>Each entry <code>[a, b, c]</code> of <code>pipes</code> says that a pipe between houses <code>a</code> and <code>b</code> can be laid for cost <code>c</code>; water flows through pipes in both directions and houses may relay water. Return the minimum total cost (wells plus pipes) that supplies every house.</p><pre>wells = [1, 2, 2], pipes = [[1, 2, 1], [2, 3, 1]]   -> 3   (a well at house 1, pipes 1-2 and 2-3)</pre>",
    constraints=["1 &le; n = wells.length &le; 1,500", "0 &le; pipes.length &le; 3,000, each pipe is [a, b, c] with 1 &le; a, b &le; n and a != b", "1 &le; wells[i], c &le; 100,000", "There may be several pipes between the same two houses"],
    hints=["Without wells this would be 'connect all houses with the cheapest pipes'. How can the wells be turned into pipes too?",
           "Invent one extra node (the water source) and a pipe from it to house i of cost wells[i-1]. Digging a well in house i is now the same as laying that pipe.",
           "Now every house must be connected to the source, which is a minimum spanning tree problem on n+1 nodes. Sort all edges by cost and use Kruskal with a union-find structure."],
    editorial=["Add a virtual node 0 and an edge <code>(0, i, wells[i-1])</code> for every house. A set of wells and pipes supplies every house exactly when every house is connected to node 0 in the chosen edges, and the cheapest such set is a minimum spanning tree of the new graph (it never needs a cycle).",
               "Kruskal's algorithm is greedy and relies on the cut/exchange property: the cheapest edge leaving any component is always safe to add. Sort the pipes together with the virtual well edges by cost, and add each edge that joins two different components (union-find with path compression). After n unions the tree is complete. O((n + m) log (n + m)) time."],
    time="O((n + m) log (n + m))", space="O(n + m)",
    solution='''def minWaterCost(wells, pipes):
    n = len(wells)
    edges = [(c, 0, i + 1) for i, c in enumerate(wells)]
    edges += [(c, a, b) for a, b, c in pipes]
    edges.sort()
    parent = list(range(n + 1))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    total = 0
    used = 0
    for c, a, b in edges:
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb
            total += c
            used += 1
            if used == n:
                break
    return total
''',
    tests=[[[1, 2, 2], [[1, 2, 1], [2, 3, 1]]], [[5], []], [[1, 1], []], [[10, 10], [[1, 2, 1]]], [[10, 10], [[1, 2, 100]]],
           [[3, 3, 3, 3], [[1, 2, 1], [3, 4, 1]]], [[100, 100, 100], [[1, 2, 5], [2, 3, 5], [1, 3, 5]]],
           [[4, 5, 6, 7], [[1, 2, 1], [2, 3, 1], [3, 4, 1], [1, 4, 1], [1, 2, 9]]], [[1, 100, 100, 100, 100], [[1, 2, 2], [1, 3, 2], [1, 4, 2], [1, 5, 2]]],
           [[2, 2, 2], [[1, 2, 3], [2, 3, 3]]]],
)
_r = rnd(5011)


def _pipes(n, m, hi):
    out = []
    for _ in range(m):
        a, b = _r.sample(range(1, n + 1), 2)
        out.append([a, b, _r.randint(1, hi)])
    return out


p["tests"].append([[_r.randint(1, 100000) for _ in range(1500)], _pipes(1500, 3000, 100000)])
p["tests"].append([[_r.randint(50000, 100000) for _ in range(1200)], _pipes(1200, 3000, 60000)])
p["tests"].append([[_r.randint(1, 1000) for _ in range(800)], _pipes(800, 1500, 1000)])


def b_water(wells, pipes):
    n = len(wells)
    best = None
    for wm in range(1 << n):
        wc = sum(wells[i] for i in range(n) if (wm >> i) & 1)
        for pm in range(1 << len(pipes)):
            par = list(range(n))

            def find(x):
                while par[x] != x:
                    x = par[x]
                return x

            pc = 0
            for k, (a, b, c) in enumerate(pipes):
                if (pm >> k) & 1:
                    pc += c
                    par[find(a - 1)] = find(b - 1)
            wellroots = {find(i) for i in range(n) if (wm >> i) & 1}
            if all(find(i) in wellroots for i in range(n)):
                tot = wc + pc
                if best is None or tot < best:
                    best = tot
    return best


def g_water(r):
    n = r.randint(1, 5)
    m = r.randint(0, 6) if n >= 2 else 0
    pipes = []
    for _ in range(m):
        a, b = r.sample(range(1, n + 1), 2)
        pipes.append([a, b, r.randint(1, 9)])
    return [[r.randint(1, 9) for _ in range(n)], pipes]


def v_water(tests):
    for t in tests:
        wells, pipes = t["args"]
        n = len(wells)
        assert 1 <= n <= 1500 and len(pipes) <= 3000
        assert all(1 <= w <= 100000 for w in wells)
        assert all(len(e) == 3 and 1 <= e[0] <= n and 1 <= e[1] <= n and e[0] != e[1] and 1 <= e[2] <= 100000 for e in pipes)


CHECKS["water-supply-wells-and-pipes"] = (b_water, g_water, "exact")
VALIDATE["water-supply-wells-and-pipes"] = v_water
