"""Problems: binary search on the answer. See data/lib.py for the registry."""
from lib import add, rnd, CHECKS, VALIDATE, gen_arr  # noqa: F401

# ---------------------------------------------------------------- EASY

p = add(
    id="smallest-divisor-within-threshold", title="Smallest Divisor Within a Threshold", diff="Easy", topic="Binary Search",
    fn="smallestDivisor", params=[("nums", "int[]"), ("threshold", "int")], ret="int", cmp="exact",
    desc="<p>You pick a positive integer divisor <code>d</code> and divide every element of <code>nums</code> by it, rounding each quotient <em>up</em> to the next integer. The <em>cost</em> of <code>d</code> is the sum of these rounded-up quotients.</p><p>Return the smallest positive <code>d</code> whose cost is at most <code>threshold</code>. It is guaranteed that <code>threshold &ge; nums.length</code>, so an answer always exists.</p><p>Example: for <code>nums = [1, 2, 5, 9]</code> and <code>threshold = 6</code>, divisor 5 gives 1 + 1 + 1 + 2 = 5 &le; 6, while divisor 4 gives 1 + 1 + 2 + 3 = 7 &gt; 6, so the answer is 5.</p>",
    constraints=["1 &le; nums.length &le; 8,000", "1 &le; nums[i] &le; 10<sup>6</sup>", "nums.length &le; threshold &le; 10<sup>6</sup>"],
    hints=["Try a few divisors by hand. What happens to the cost when the divisor gets larger?",
           "The cost never increases as <code>d</code> grows, and with <code>d = max(nums)</code> every term is exactly 1. So the answer lies between 1 and <code>max(nums)</code>.",
           "Binary search <code>d</code> in <code>[1, max(nums)]</code>. For a candidate <code>mid</code> compute the cost with <code>(x + mid - 1) // mid</code> per element; if the cost is at most <code>threshold</code>, keep <code>mid</code> as a possible answer and search lower, otherwise search higher."],
    editorial=["Let <code>cost(d)</code> be the sum of <code>ceil(x / d)</code>. Making the divisor bigger can only shrink each term, so <code>cost</code> is non-increasing in <code>d</code>. That is exactly the shape binary search needs: the answers <code>d</code> with <code>cost(d) &le; threshold</code> form a suffix of the range, and we want the first one.",
               "With <code>d = max(nums)</code> the cost equals <code>nums.length</code>, which is within the threshold, so the upper end of the range is always valid. Each probe costs O(n), and there are O(log max(nums)) probes, so the total is O(n log max(nums)) time and O(1) space."],
    time="O(n log M)", space="O(1)",
    solution='''def smallestDivisor(nums, threshold):
    lo, hi = 1, max(nums)
    while lo < hi:
        mid = (lo + hi) // 2
        cost = 0
        for x in nums:
            cost += (x + mid - 1) // mid
        if cost <= threshold:
            hi = mid
        else:
            lo = mid + 1
    return lo
''',
    tests=[[[1, 2, 5, 9], 6], [[44, 22, 33, 11, 1], 5], [[2, 3, 5, 7, 11], 11], [[5], 5], [[5], 1], [[1], 1], [[1, 1, 1], 3],
           [[10, 10, 10], 4], [[10 ** 6], 1], [[10 ** 6, 10 ** 6], 3], [[7, 7, 7, 7], 8], [[100, 1, 1, 1, 1], 5]],
)
_r = rnd(9301)
_a = [_r.randint(1, 10 ** 6) for _ in range(2500)]
p["tests"].append([_a, 2500])
p["tests"].append([_a, 25000])
p["tests"].append([_a, 10 ** 6])
_a = [_r.randint(1, 1000) for _ in range(4000)]
p["tests"].append([_a, 4500])


def b_divisor(nums, threshold):
    d = 1
    while True:
        if sum(-(-x // d) for x in nums) <= threshold:
            return d
        d += 1


def g_divisor(r):
    n = r.randint(1, 8)
    nums = [r.randint(1, 40) for _ in range(n)]
    return [nums, r.randint(n, n * 12)]


def v_divisor(tests):
    for t in tests:
        nums, th = t["args"]
        assert 1 <= len(nums) <= 8000 and all(1 <= x <= 10 ** 6 for x in nums)
        assert len(nums) <= th <= 10 ** 6
        d = t["expected"]
        assert sum(-(-x // d) for x in nums) <= th
        assert d == 1 or sum(-(-x // (d - 1)) for x in nums) > th


CHECKS["smallest-divisor-within-threshold"] = (b_divisor, g_divisor, "exact")
VALIDATE["smallest-divisor-within-threshold"] = v_divisor

p = add(
    id="wood-cutting-saw-height", title="Wood Cutting Saw Height", diff="Easy", topic="Binary Search",
    fn="sawHeight", params=[("trees", "int[]"), ("need", "int")], ret="int", cmp="exact",
    desc="<p>A lumberjack must collect at least <code>need</code> metres of wood. He sets his saw to an integer height <code>H</code> and cuts every tree in the row <code>trees</code> (given as heights in metres) that is taller than <code>H</code>: the part above <code>H</code> falls and is collected, the part below stays. A tree not taller than <code>H</code> gives nothing.</p><p>To spare the forest, he wants the saw as high as possible. Return the largest integer <code>H &ge; 0</code> for which the collected wood is at least <code>need</code>. The total height of all trees is guaranteed to be at least <code>need</code>, so <code>H = 0</code> always works.</p><p>Example: <code>trees = [20, 15, 10, 17]</code>, <code>need = 7</code>. At <code>H = 15</code> he collects 5 + 0 + 0 + 2 = 7, at <code>H = 16</code> only 4 + 1 = 5, so the answer is 15.</p>",
    constraints=["1 &le; trees.length &le; 8,000", "1 &le; trees[i] &le; 10<sup>9</sup>", "1 &le; need &le; 10<sup>9</sup>", "need &le; sum(trees)"],
    hints=["Compute the wood collected for a single chosen height first. How does it change if you raise the saw?",
           "Raising the saw never increases the collected wood. So the heights that work form a prefix <code>0..H*</code>, and you want its last element.",
           "Binary search <code>H</code> in <code>[0, max(trees)]</code>. Use the upper-mid <code>(lo + hi + 1) // 2</code> when you move <code>lo = mid</code> on success, otherwise the loop never ends."],
    editorial=["Define <code>wood(H) = sum(max(0, t - H))</code>. It is non-increasing in <code>H</code>, equals the full total at <code>H = 0</code> and is 0 at <code>H = max(trees)</code>. Therefore the predicate <code>wood(H) &ge; need</code> is true on a prefix of the heights and false afterwards; we look for the last true position.",
               "When searching for the last true value, round the midpoint up so that <code>lo = mid</code> always makes progress. Each evaluation is a linear scan, so the total is O(n log max(trees)) time and O(1) space. Sorting plus prefix sums can answer each probe faster, but the linear scan is already fast enough here."],
    time="O(n log M)", space="O(1)",
    solution='''def sawHeight(trees, need):
    lo, hi = 0, max(trees)
    while lo < hi:
        mid = (lo + hi + 1) // 2
        wood = 0
        for t in trees:
            if t > mid:
                wood += t - mid
        if wood >= need:
            lo = mid
        else:
            hi = mid - 1
    return lo
''',
    tests=[[[20, 15, 10, 17], 7], [[4, 42, 40, 26, 46], 20], [[5], 5], [[5], 1], [[5], 4], [[1, 1, 1], 3], [[1, 1, 1], 1],
           [[10 ** 9], 10 ** 9], [[10 ** 9, 10 ** 9], 10 ** 9], [[3, 3, 3, 3], 4], [[1, 100], 50], [[8, 8, 9, 2], 5]],
)
_r = rnd(9302)
_a = [_r.randint(1, 10 ** 9) for _ in range(3000)]
p["tests"].append([_a, 10 ** 9])
p["tests"].append([_a, 7777])
_a = [_r.randint(1, 100000) for _ in range(5000)]
p["tests"].append([_a, sum(_a) // 3])
p["tests"].append([_a[:40], sum(_a[:40])])


def b_saw(trees, need):
    for H in range(max(trees), -1, -1):
        if sum(t - H for t in trees if t > H) >= need:
            return H


def g_saw(r):
    n = r.randint(1, 7)
    trees = [r.randint(1, 20) for _ in range(n)]
    return [trees, r.randint(1, sum(trees))]


def v_saw(tests):
    for t in tests:
        trees, need = t["args"]
        assert 1 <= len(trees) <= 8000 and all(1 <= x <= 10 ** 9 for x in trees)
        assert 1 <= need <= 10 ** 9 and need <= sum(trees)


CHECKS["wood-cutting-saw-height"] = (b_saw, g_saw, "exact")
VALIDATE["wood-cutting-saw-height"] = v_saw

# ---------------------------------------------------------------- MEDIUM

p = add(
    id="minimum-speed-to-arrive-on-time", title="Minimum Train Speed to Arrive on Time", diff="Medium", topic="Binary Search",
    fn="minSpeed", params=[("dist", "int[]"), ("hour", "int")], ret="int", cmp="exact",
    desc="<p>You must ride <code>n</code> trains in order. Train <code>i</code> covers <code>dist[i]</code> kilometres. All trains travel at the same constant integer speed <code>s</code> km/h (the one number you choose). A train can only depart at the start of a whole hour, so after finishing train <code>i</code> you wait until the next whole hour before boarding train <code>i + 1</code>. The last train needs no waiting afterwards.</p><p>You must reach the destination within <code>hour / 100</code> hours; the allowed time is given in <em>hundredths of an hour</em> so that everything stays an integer (for example <code>hour = 275</code> means 2.75 hours).</p><p>Return the smallest positive integer speed that makes it on time, or <code>-1</code> if no speed works. Whenever an answer exists, it is at most 10<sup>7</sup>.</p><p>Example: <code>dist = [1, 3, 2]</code>, <code>hour = 270</code>. At speed 3 the trips last 1 h, 1 h and 2/3 h, giving 2 + 0.67 = 2.67 &le; 2.70. At speed 2 they take 1 h, 2 h and 1 h, which is 4 h. The answer is 3.</p>",
    constraints=["1 &le; dist.length &le; 8,000", "1 &le; dist[i] &le; 10<sup>5</sup>", "1 &le; hour &le; 10<sup>9</sup> (hundredths of an hour)", "If an answer exists it is at most 10<sup>7</sup>"],
    hints=["Write the total travel time as a function of the speed <code>s</code>: every train except the last takes <code>ceil(dist[i] / s)</code> hours, the last takes exactly <code>dist[last] / s</code> hours.",
           "A faster speed never makes the total slower. Also, you need at least <code>n - 1</code> full hours for the first <code>n - 1</code> trains, so if <code>hour &le; 100 * (n - 1)</code> the answer is <code>-1</code>.",
           "Binary search the speed in <code>[1, 10^7]</code>. To avoid floating point, test <code>(T * s + dist[last]) * 100 &le; hour * s</code> where <code>T</code> is the sum of the rounded-up hours of the first <code>n - 1</code> trains. If even <code>10^7</code> fails, return <code>-1</code>."],
    editorial=["For a speed <code>s</code>, the total time is <code>T(s) + dist[n-1] / s</code> where <code>T(s) = sum(ceil(dist[i] / s))</code> over the first <code>n - 1</code> trains. Both parts are non-increasing in <code>s</code>, so the set of speeds that arrive on time is a suffix of the positive integers: binary search for the first one.",
               "Avoid floats: multiply the inequality <code>T + d / s &le; hour / 100</code> by <code>100 * s</code> to get <code>100 * (T * s + d) &le; hour * s</code>, which uses integers only. The upper limit 10<sup>7</sup> is enough because at that speed every train takes one hour (or the last takes at most 0.01 h) so any larger speed cannot help; if the check fails there, no speed works and the answer is <code>-1</code>. Complexity is O(n log 10<sup>7</sup>) time and O(1) space."],
    time="O(n log V)", space="O(1)",
    solution='''def minSpeed(dist, hour):
    last = dist[-1]
    body = dist[:-1]

    def ok(s):
        total = 0
        for d in body:
            total += (d + s - 1) // s
        return (total * s + last) * 100 <= hour * s

    hi = 10 ** 7
    if not ok(hi):
        return -1
    lo = 1
    while lo < hi:
        mid = (lo + hi) // 2
        if ok(mid):
            hi = mid
        else:
            lo = mid + 1
    return lo
''',
    tests=[[[1, 3, 2], 270], [[1, 3, 2], 600], [[1, 3, 2], 250], [[1, 1, 100000], 201], [[5], 100], [[5], 1], [[100000], 1],
           [[100000], 100], [[2, 2], 100], [[2, 2], 101], [[1, 1, 1], 300], [[1, 1, 1], 201], [[9, 8, 7, 6], 450]],
)
_r = rnd(9303)


def _mk_speed(n, s, vmax):
    d = [_r.randint(1, vmax) for _ in range(n)]
    t = sum(-(-x // s) for x in d[:-1])
    h = (t * s + d[-1]) * 100
    return d, -(-h // s)


_d, _h = _mk_speed(3500, 37, 100000)
p["tests"].append([_d, _h])
p["tests"].append([_d, _h + 150])
_d, _h = _mk_speed(3000, 90000, 100000)
p["tests"].append([_d, _h])
p["tests"].append([_d, 100 * 2999])
p["tests"].append([_d[:30], 100 * 29 + 1])


def b_speed(dist, hour):
    from fractions import Fraction
    for s in range(1, max(dist) * 100 + 1):
        t = Fraction(0)
        for i, d in enumerate(dist):
            if i < len(dist) - 1:
                t += -(-d // s)
            else:
                t += Fraction(d, s)
        if t <= Fraction(hour, 100):
            return s
    return -1


def g_speed(r):
    n = r.randint(1, 5)
    dist = [r.randint(1, 20) for _ in range(n)]
    return [dist, r.randint(1, 100 * (n + 2))]


def v_speed(tests):
    for t in tests:
        dist, hour = t["args"]
        assert 1 <= len(dist) <= 8000 and all(1 <= d <= 10 ** 5 for d in dist)
        assert 1 <= hour <= 10 ** 9
        assert t["expected"] == -1 or 1 <= t["expected"] <= 10 ** 7
    assert any(t["expected"] == -1 for t in tests)


CHECKS["minimum-speed-to-arrive-on-time"] = (b_speed, g_speed, "exact")
VALIDATE["minimum-speed-to-arrive-on-time"] = v_speed

p = add(
    id="minimum-time-to-complete-trips", title="Minimum Time to Complete Trips", diff="Medium", topic="Binary Search",
    fn="minTimeForTrips", params=[("times", "int[]"), ("totalTrips", "int")], ret="int", cmp="exact",
    desc="<p>A fleet of buses runs independently. Bus <code>i</code> needs <code>times[i]</code> minutes for one trip and starts its next trip the moment the previous one ends, with no breaks. All buses start at minute 0.</p><p>Return the smallest number of minutes after which the buses together have completed <strong>at least</strong> <code>totalTrips</code> trips.</p><p>Example: <code>times = [1, 2, 3]</code>, <code>totalTrips = 5</code>. After 3 minutes the buses have done 3 + 1 + 1 = 5 trips; after 2 minutes only 2 + 1 + 0 = 3. The answer is 3.</p>",
    constraints=["1 &le; times.length &le; 8,000", "1 &le; times[i] &le; 10<sup>4</sup>", "1 &le; totalTrips &le; 10<sup>5</sup>"],
    hints=["After <code>t</code> minutes, how many trips has bus <code>i</code> finished?",
           "It has finished <code>t // times[i]</code> trips. Adding this over all buses gives a total that never decreases as <code>t</code> grows.",
           "Binary search <code>t</code> between 1 and <code>min(times) * totalTrips</code> (the fastest bus alone would do everything by then) and find the smallest <code>t</code> whose total is at least <code>totalTrips</code>."],
    editorial=["The trip count by minute <code>t</code> is <code>f(t) = sum(t // times[i])</code>. It is non-decreasing in <code>t</code>, so the smallest <code>t</code> with <code>f(t) &ge; totalTrips</code> can be found by binary search. The fastest bus alone completes <code>totalTrips</code> trips in <code>min(times) * totalTrips</code> minutes, which is a valid upper bound (at most 10<sup>9</sup>, so it fits in a 32-bit integer).",
               "Each probe is O(n), and the range has size up to 10<sup>9</sup>, so the cost is about 30 probes of O(n). Time is O(n log(min(times) * totalTrips)), space O(1). You cannot simply simulate minute by minute, because the answer may be a billion minutes."],
    time="O(n log T)", space="O(1)",
    solution='''def minTimeForTrips(times, totalTrips):
    lo, hi = 1, min(times) * totalTrips
    while lo < hi:
        mid = (lo + hi) // 2
        done = 0
        for x in times:
            done += mid // x
        if done >= totalTrips:
            hi = mid
        else:
            lo = mid + 1
    return lo
''',
    tests=[[[1, 2, 3], 5], [[2], 1], [[2], 5], [[5, 10, 10], 9], [[10 ** 4], 10 ** 5], [[10 ** 4, 10 ** 4], 10 ** 5], [[1], 1],
           [[1, 1, 1, 1], 3], [[3, 7], 10], [[7, 7, 7], 4], [[1, 10 ** 4], 100000], [[4, 6, 9], 20]],
)
_r = rnd(9304)
_a = [_r.randint(1, 10 ** 4) for _ in range(7000)]
p["tests"].append([_a, 10 ** 5])
p["tests"].append([_a, 1234])
_a = [_r.randint(9000, 10 ** 4) for _ in range(5000)]
p["tests"].append([_a, 99999])


def b_trips(times, totalTrips):
    t = 0
    while True:
        t += 1
        if sum(t // x for x in times) >= totalTrips:
            return t


def g_trips(r):
    return [[r.randint(1, 9) for _ in range(r.randint(1, 5))], r.randint(1, 30)]


def v_trips(tests):
    for t in tests:
        times, tt = t["args"]
        assert 1 <= len(times) <= 8000 and all(1 <= x <= 10 ** 4 for x in times) and 1 <= tt <= 10 ** 5


CHECKS["minimum-time-to-complete-trips"] = (b_trips, g_trips, "exact")
VALIDATE["minimum-time-to-complete-trips"] = v_trips

p = add(
    id="maximum-candies-per-child", title="Maximum Candies Per Child", diff="Medium", topic="Binary Search",
    fn="maxCandies", params=[("piles", "int[]"), ("k", "int")], ret="int", cmp="exact",
    desc="<p>There are piles of candies, <code>piles[i]</code> in pile <code>i</code>. You may split any pile into as many smaller piles as you like, but you may never merge candies from different piles. Then you hand out the resulting piles to <code>k</code> children so that every child gets <strong>exactly one</strong> pile and all children get the <strong>same</strong> number of candies (some piles can stay unused).</p><p>Return the largest number of candies each child can receive, or <code>0</code> if even one candy per child is impossible.</p><p>Example: <code>piles = [5, 8, 6]</code>, <code>k = 3</code>. Everyone can get 5 candies (5 from the first pile, 5 from the second, 5 from the third), but 6 is impossible: the piles give only 0 + 1 + 1 = 2 portions of size 6. The answer is 5.</p>",
    constraints=["1 &le; piles.length &le; 8,000", "1 &le; piles[i] &le; 10<sup>7</sup>", "1 &le; k &le; 10<sup>9</sup>"],
    hints=["Suppose every child must receive exactly <code>c</code> candies. How many children can one pile of size <code>p</code> serve?",
           "It serves <code>p // c</code> children, so the whole row serves <code>sum(p // c)</code>. This number does not increase when <code>c</code> grows.",
           "Binary search <code>c</code> in <code>[1, max(piles)]</code> for the largest value with <code>sum(p // c) &ge; k</code>. If even <code>c = 1</code> fails (the total number of candies is below <code>k</code>), return 0."],
    editorial=["For a fixed portion size <code>c</code> the number of children that can be served is <code>g(c) = sum(p // c)</code>; leftovers inside a pile are wasted because piles cannot be merged. As <code>c</code> increases, every term shrinks or stays, so <code>g</code> is non-increasing. The feasible portion sizes are therefore <code>1..c*</code>, and we search for the last one.",
               "Check <code>g(1) = sum(piles) &ge; k</code> first; if not, answer 0. Otherwise search between 1 and <code>max(piles)</code> with an upper-mid binary search. Time is O(n log max(piles)), space O(1)."],
    time="O(n log M)", space="O(1)",
    solution='''def maxCandies(piles, k):
    if sum(piles) < k:
        return 0
    lo, hi = 1, max(piles)
    while lo < hi:
        mid = (lo + hi + 1) // 2
        kids = 0
        for x in piles:
            kids += x // mid
        if kids >= k:
            lo = mid
        else:
            hi = mid - 1
    return lo
''',
    tests=[[[5, 8, 6], 3], [[2, 5], 11], [[4], 1], [[4], 4], [[4], 5], [[1, 1, 1], 3], [[1, 1, 1], 4], [[10 ** 7], 1],
           [[10 ** 7, 10 ** 7], 3], [[10 ** 7], 10 ** 9], [[9, 3, 7, 7], 6], [[100, 1], 2]],
)
_r = rnd(9305)
_a = [_r.randint(1, 10 ** 7) for _ in range(3000)]
p["tests"].append([_a, 10 ** 9])
p["tests"].append([_a, 5000])
p["tests"].append([_a, 123456])
_a = [_r.randint(1, 1000) for _ in range(4000)]
p["tests"].append([_a, 8000])


def b_candies(piles, k):
    for c in range(max(piles), 0, -1):
        if sum(x // c for x in piles) >= k:
            return c
    return 0


def g_candies(r):
    return [[r.randint(1, 15) for _ in range(r.randint(1, 6))], r.randint(1, 40)]


def v_candies(tests):
    for t in tests:
        piles, k = t["args"]
        assert 1 <= len(piles) <= 8000 and all(1 <= x <= 10 ** 7 for x in piles) and 1 <= k <= 10 ** 9
    assert any(t["expected"] == 0 for t in tests) and any(t["expected"] > 0 for t in tests)


CHECKS["maximum-candies-per-child"] = (b_candies, g_candies, "exact")
VALIDATE["maximum-candies-per-child"] = v_candies

p = add(
    id="smallest-largest-bag-after-splits", title="Smallest Largest Bag After Splits", diff="Medium", topic="Binary Search",
    fn="minimizeLargestBag", params=[("bags", "int[]"), ("maxOps", "int")], ret="int", cmp="exact",
    desc="<p>You have bags of balls; bag <code>i</code> holds <code>bags[i]</code> balls. In one operation you take any bag and split it into two bags, each holding at least one ball (the two counts add up to the original). You may do at most <code>maxOps</code> operations.</p><p>The <em>penalty</em> is the number of balls in the largest bag. Return the smallest penalty you can reach.</p><p>Example: <code>bags = [9]</code>, <code>maxOps = 2</code>. Split 9 into 6 + 3, then 6 into 3 + 3 to get bags 3, 3, 3 and penalty 3.</p>",
    constraints=["1 &le; bags.length &le; 8,000", "1 &le; bags[i] &le; 10<sup>9</sup>", "0 &le; maxOps &le; 10<sup>9</sup>"],
    hints=["Imagine the final penalty were at most <code>x</code>. How many splits does one bag of size <code>b</code> need so that all its pieces are at most <code>x</code>?",
           "It needs <code>ceil(b / x) - 1</code> splits: cut off pieces of size <code>x</code> until the rest fits. Summing over all bags gives the total number of operations required for penalty <code>x</code>, and it only decreases as <code>x</code> grows.",
           "Binary search <code>x</code> in <code>[1, max(bags)]</code> for the smallest value whose required operations do not exceed <code>maxOps</code>."],
    editorial=["Let <code>need(x) = sum(ceil(b / x) - 1)</code> be the minimum number of operations that make every bag hold at most <code>x</code> balls. A bag of size <code>b</code> ends up in at least <code>ceil(b / x)</code> pieces, hence at least that many minus one splits, and cutting <code>x</code>-sized pieces off achieves exactly this bound. Bags are independent, so the sum is exact.",
               "<code>need</code> is non-increasing in <code>x</code> and <code>need(max(bags)) = 0</code>, so the answer is the smallest <code>x</code> with <code>need(x) &le; maxOps</code>. Binary search gives O(n log max(bags)) time and O(1) space."],
    time="O(n log M)", space="O(1)",
    solution='''def minimizeLargestBag(bags, maxOps):
    lo, hi = 1, max(bags)
    while lo < hi:
        mid = (lo + hi) // 2
        ops = 0
        for b in bags:
            ops += (b - 1) // mid
        if ops <= maxOps:
            hi = mid
        else:
            lo = mid + 1
    return lo
''',
    tests=[[[9], 2], [[2, 4, 8, 2], 4], [[7, 17], 2], [[1], 0], [[1], 100], [[5], 0], [[5], 4], [[10 ** 9], 0], [[10 ** 9], 10 ** 9],
           [[10 ** 9, 10 ** 9], 3], [[3, 3, 3], 3], [[6, 10, 4], 5]],
)
_r = rnd(9306)
_a = [_r.randint(1, 10 ** 9) for _ in range(2500)]
p["tests"].append([_a, 10 ** 9])
p["tests"].append([_a, 0])
_a = [_r.randint(1, 10 ** 4) for _ in range(5000)]
p["tests"].append([_a, 50000])


def b_bags(bags, maxOps):
    for x in range(1, max(bags) + 1):
        ops = 0
        for b in bags:
            while b > x:
                b -= x
                ops += 1
        if ops <= maxOps:
            return x


def g_bags(r):
    return [[r.randint(1, 15) for _ in range(r.randint(1, 5))], r.randint(0, 20)]


def v_bags(tests):
    for t in tests:
        bags, ops = t["args"]
        assert 1 <= len(bags) <= 8000 and all(1 <= x <= 10 ** 9 for x in bags) and 0 <= ops <= 10 ** 9


CHECKS["smallest-largest-bag-after-splits"] = (b_bags, g_bags, "exact")
VALIDATE["smallest-largest-bag-after-splits"] = v_bags

p = add(
    id="heaters-minimum-radius", title="Heaters: Minimum Radius", diff="Medium", topic="Binary Search",
    fn="minRadius", params=[("houses", "int[]"), ("heaters", "int[]")], ret="int", cmp="exact",
    desc="<p>Houses and heaters stand on a line; <code>houses</code> and <code>heaters</code> list their integer positions (unsorted, duplicates allowed). Every heater warms all positions within distance <code>r</code> of it (so both ends are included), and all heaters use the same radius <code>r</code>.</p><p>Return the smallest non-negative integer <code>r</code> such that every house is warmed by at least one heater.</p><p>Example: <code>houses = [1, 2, 3, 4]</code>, <code>heaters = [1, 4]</code>. Radius 1 warms 1-2 from the first heater and 3-4 from the second; radius 0 leaves houses 2 and 3 cold. The answer is 1.</p>",
    constraints=["1 &le; houses.length, heaters.length &le; 4,000", "0 &le; houses[i], heaters[j] &le; 10<sup>9</sup>"],
    hints=["Suppose the radius is fixed. Sort both arrays. For the leftmost house, which heater is the natural one to cover it?",
           "Keep a pointer into the sorted heaters that only moves right: skip heaters whose right reach <code>h + r</code> is still left of the house. The first remaining heater must also satisfy <code>h - r &le; house</code>.",
           "If a radius works, every larger radius works. Binary search <code>r</code> in <code>[0, 10^9]</code> and use the two-pointer check in O(n + m) per probe."],
    editorial=["Sort houses and heaters. For a given <code>r</code>, walk through the houses from left to right with a heater pointer <code>j</code>. While heater <code>j</code> lies too far left (<code>heaters[j] + r &lt; house</code>) it cannot help this house or any later one, so advance <code>j</code>. If no heater is left, or the current one is too far right (<code>heaters[j] - r &gt; house</code>), the radius fails. Otherwise this house is warmed.",
               "The check is monotone in <code>r</code>, so binary search finds the smallest working radius in O(log 10<sup>9</sup>) probes of O(n + m) each, after an O(n log n + m log m) sort. A direct alternative is to compute, for every house, the distance to its nearest heater with a binary search in the sorted heaters, and take the maximum of these distances."],
    time="O(n log n + (n + m) log R)", space="O(1) extra",
    solution='''def minRadius(houses, heaters):
    hs = sorted(houses)
    ht = sorted(heaters)
    m = len(ht)

    def ok(r):
        j = 0
        for x in hs:
            while j < m and ht[j] + r < x:
                j += 1
            if j == m or ht[j] - r > x:
                return False
        return True

    lo, hi = 0, max(hs[-1], ht[-1]) - min(hs[0], ht[0])
    while lo < hi:
        mid = (lo + hi) // 2
        if ok(mid):
            hi = mid
        else:
            lo = mid + 1
    return lo
''',
    tests=[[[1, 2, 3, 4], [1, 4]], [[1, 2, 3], [2]], [[1, 5], [2]], [[5], [5]], [[0], [10 ** 9]], [[10 ** 9], [0]],
           [[1, 1, 1], [1]], [[1, 2, 3, 4, 5, 6], [3, 3]], [[10, 1, 7], [4, 9, 2]], [[1, 100], [1, 50, 100]],
           [[0, 10 ** 9], [5 * 10 ** 8]], [[3, 8, 14, 20], [10]]],
)
_r = rnd(9307)
_h = [_r.randint(0, 10 ** 9) for _ in range(3500)]
_t = [_r.randint(0, 10 ** 9) for _ in range(400)]
p["tests"].append([_h, _t])
p["tests"].append([_h, [_r.randint(0, 10 ** 9) for _ in range(3)]])
_h = [_r.randint(0, 100000) for _ in range(4000)]
p["tests"].append([_h, [_r.randint(0, 100000) for _ in range(4000)]])


def b_heat(houses, heaters):
    return max(min(abs(h - t) for t in heaters) for h in houses)


def g_heat(r):
    return [[r.randint(0, 20) for _ in range(r.randint(1, 7))], [r.randint(0, 20) for _ in range(r.randint(1, 4))]]


def v_heat(tests):
    for t in tests:
        h, ht = t["args"]
        assert 1 <= len(h) <= 4000 and 1 <= len(ht) <= 4000
        assert all(0 <= x <= 10 ** 9 for x in h + ht)


CHECKS["heaters-minimum-radius"] = (b_heat, g_heat, "exact")
VALIDATE["heaters-minimum-radius"] = v_heat

p = add(
    id="minimize-max-difference-of-pairs", title="Minimize the Maximum Difference of Pairs", diff="Medium", topic="Binary Search",
    fn="minMaxDiff", params=[("nums", "int[]"), ("p", "int")], ret="int", cmp="exact",
    desc="<p>Choose exactly <code>p</code> disjoint pairs of elements from <code>nums</code> (no index may belong to two pairs). The cost of a choice is the largest absolute difference <code>|a - b|</code> over its pairs. Return the smallest cost over all possible choices. If <code>p = 0</code> the cost is 0.</p><p>Example: <code>nums = [10, 1, 2, 7, 1, 3]</code>, <code>p = 2</code>. Pair the two 1s (difference 0) and 2 with 3 (difference 1): the cost is 1, and no choice does better because only one pair has difference 0.</p>",
    constraints=["1 &le; nums.length &le; 6,000", "0 &le; nums[i] &le; 10<sup>9</sup>", "0 &le; p &le; nums.length / 2"],
    hints=["Which elements are good partners for each other? Sort the array first.",
           "Once sorted, pairs worth considering are always neighbours. If you fix the allowed difference <code>d</code>, you can greedily take a pair <code>(a[i], a[i+1])</code> whenever it is within <code>d</code> and then skip both elements.",
           "The greedy count of pairs never decreases when <code>d</code> grows. Binary search <code>d</code> in <code>[0, max - min]</code> for the smallest value whose greedy count reaches <code>p</code>."],
    editorial=["After sorting, an optimal pairing of any size uses adjacent elements: if <code>a &lt; b &lt; c &lt; d</code> are paired as <code>(a, c)</code> and <code>(b, d)</code> or <code>(a, d)</code> and <code>(b, c)</code>, then pairing <code>(a, b)</code> and <code>(c, d)</code> has no larger difference. So with a limit <code>d</code>, scan left to right: if <code>a[i+1] - a[i] &le; d</code> take the pair and jump two positions, otherwise move one position. Taking the leftmost possible pair never hurts, so this counts the maximum number of pairs.",
               "The count is non-decreasing in <code>d</code>, so binary search the smallest <code>d</code> that reaches <code>p</code>; <code>p = 0</code> returns 0 immediately. Total time O(n log n + n log(max - min)), space O(1) beyond the sorted copy."],
    time="O(n log n + n log R)", space="O(n)",
    solution='''def minMaxDiff(nums, p):
    if p == 0:
        return 0
    a = sorted(nums)
    n = len(a)

    def pairs(d):
        cnt = 0
        i = 0
        while i + 1 < n:
            if a[i + 1] - a[i] <= d:
                cnt += 1
                i += 2
            else:
                i += 1
        return cnt

    lo, hi = 0, a[-1] - a[0]
    while lo < hi:
        mid = (lo + hi) // 2
        if pairs(mid) >= p:
            hi = mid
        else:
            lo = mid + 1
    return lo
''',
    tests=[[[10, 1, 2, 7, 1, 3], 2], [[4, 2, 1, 2], 1], [[1, 2, 3], 0], [[5], 0], [[5, 5], 1], [[0, 10 ** 9], 1], [[1, 2, 3, 4], 2],
           [[1, 1, 1, 1], 2], [[1, 100, 2, 101, 3, 102], 3], [[1, 4, 6, 9, 15, 22], 2], [[1, 4, 6, 9, 15, 22], 3],
           [[7, 7, 7], 1]],
)
_r = rnd(9308)
_a = [_r.randint(0, 10 ** 9) for _ in range(3500)]
p["tests"].append([_a, 1])
p["tests"].append([_a, 1750])
p["tests"].append([_a, 700])
_a = [_r.randint(0, 5000) for _ in range(6000)]
p["tests"].append([_a, 3000])


def b_pairs(nums, p):
    n = len(nums)
    best = [None]

    def go(used, left, cur):
        if left == 0:
            if best[0] is None or cur < best[0]:
                best[0] = cur
            return
        i = 0
        while i < n and used >> i & 1:
            i += 1
        if i >= n:
            return
        # element i is either left unpaired or paired with some later element
        if n - bin(used).count("1") - 1 >= 2 * left:
            go(used | (1 << i), left, cur)
        for j in range(i + 1, n):
            if not used >> j & 1:
                go(used | (1 << i) | (1 << j), left - 1, max(cur, abs(nums[i] - nums[j])))

    go(0, p, 0)
    return best[0]


def g_pairs(r):
    n = r.randint(1, 8)
    return [[r.randint(0, 30) for _ in range(n)], r.randint(0, n // 2)]


def v_pairs(tests):
    for t in tests:
        a, p_ = t["args"]
        assert 1 <= len(a) <= 6000 and all(0 <= x <= 10 ** 9 for x in a) and 0 <= p_ <= len(a) // 2


CHECKS["minimize-max-difference-of-pairs"] = (b_pairs, g_pairs, "exact")
VALIDATE["minimize-max-difference-of-pairs"] = v_pairs

# ---------------------------------------------------------------- HARD

p = add(
    id="divide-chocolate-max-min-sweetness", title="Divide Chocolate: Best Smallest Piece", diff="Hard", topic="Binary Search",
    fn="maxMinSweetness", params=[("sweetness", "int[]"), ("k", "int")], ret="int", cmp="exact", tier="extra",
    desc="<p>A chocolate bar consists of consecutive chunks, chunk <code>i</code> having sweetness <code>sweetness[i]</code>. You want to share it with <code>k</code> friends, so you cut the bar into exactly <code>k + 1</code> pieces, each made of one or more consecutive chunks. You are polite and keep the piece with the <strong>least</strong> total sweetness for yourself, giving the sweeter pieces to your friends.</p><p>Return the largest total sweetness your own piece can have if you cut optimally.</p><p>Example: <code>sweetness = [1, 2, 2, 1, 2, 2, 1, 2, 2]</code>, <code>k = 2</code>. Cut into <code>[1,2,2,1,2]</code>, <code>[2,1,2]</code>, <code>[2]</code>... that leaves a piece of 2, which is poor; the better cut <code>[1,2,2]</code>, <code>[1,2,2]</code>, <code>[1,2,2]</code> gives every piece 5. The answer is 5.</p>",
    constraints=["1 &le; sweetness.length &le; 8,000", "1 &le; sweetness[i] &le; 10<sup>5</sup>", "0 &le; k &lt; sweetness.length"],
    hints=["You want the minimum piece to be large. What is a simple question you can ask about a target value <code>x</code>?",
           "Can the bar be cut into at least <code>k + 1</code> pieces that each have total sweetness at least <code>x</code>? Cut greedily: close a piece as soon as it reaches <code>x</code>.",
           "If target <code>x</code> is achievable, so is every smaller target (sweetness is positive). Binary search <code>x</code> from <code>min(sweetness)</code> to <code>sum // (k + 1)</code>, looking for the largest achievable one. Leftover chunks at the end can simply be merged into the last piece."],
    editorial=["Fix a target <code>x</code> and ask whether we can form at least <code>k + 1</code> pieces each of sum at least <code>x</code>. Scan left to right, adding chunks to the current piece and closing it as soon as its sum reaches <code>x</code>. Closing as early as possible leaves the most chunks for later pieces, so this greedy produces the maximum number of pieces. Any leftover chunks at the end are glued onto the last piece, which only makes it sweeter, so having at least <code>k + 1</code> closed pieces is enough (extra pieces are merged into neighbours).",
               "The check is monotone in <code>x</code>: a larger target is harder. The answer lies between <code>min(sweetness)</code> (each chunk alone, when there are enough chunks, or lower targets) and <code>sum // (k + 1)</code> (the average piece). We binary search for the largest feasible <code>x</code> in O(n log sum) time and O(1) space. This is the mirror image of the classic 'minimise the largest piece' split problem."],
    time="O(n log S)", space="O(1)",
    solution='''def maxMinSweetness(sweetness, k):
    def ok(x):
        pieces = cur = 0
        for s in sweetness:
            cur += s
            if cur >= x:
                pieces += 1
                cur = 0
        return pieces >= k + 1

    lo, hi = 1, sum(sweetness) // (k + 1)
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if ok(mid):
            lo = mid
        else:
            hi = mid - 1
    return lo
''',
    tests=[[[1, 2, 3, 4, 5, 6, 7, 8, 9], 5], [[5, 6, 7, 8, 9, 1, 2, 3, 4], 8], [[1, 2, 2, 1, 2, 2, 1, 2, 2], 2], [[7], 0],
           [[7, 3], 0], [[7, 3], 1], [[1, 1, 1, 1], 3], [[10 ** 5] * 4, 1], [[10 ** 5, 1, 10 ** 5], 1], [[1, 100, 1, 100, 1], 2],
           [[4, 4, 4, 4, 4, 4], 2], [[9, 1, 1, 1, 9], 2]],
)
_r = rnd(9309)
_a = [_r.randint(1, 10 ** 5) for _ in range(3000)]
p["tests"].append([_a, 0])
p["tests"].append([_a, 250])
p["tests"].append([_a, 2999])
p["tests"].append([_a, 1500])
_a = [_r.randint(1, 20) for _ in range(5000)]
p["tests"].append([_a, 99])


def b_choc(sweetness, k):
    from itertools import combinations
    n = len(sweetness)
    pre = [0]
    for s in sweetness:
        pre.append(pre[-1] + s)
    best = 0
    for cuts in combinations(range(1, n), k):
        pts = (0,) + cuts + (n,)
        best = max(best, min(pre[pts[i + 1]] - pre[pts[i]] for i in range(k + 1)))
    return best


def g_choc(r):
    n = r.randint(1, 9)
    return [[r.randint(1, 12) for _ in range(n)], r.randint(0, n - 1)]


def v_choc(tests):
    for t in tests:
        s, k = t["args"]
        assert 1 <= len(s) <= 8000 and all(1 <= x <= 10 ** 5 for x in s) and 0 <= k < len(s)


CHECKS["divide-chocolate-max-min-sweetness"] = (b_choc, g_choc, "exact")
VALIDATE["divide-chocolate-max-min-sweetness"] = v_choc

p = add(
    id="maximum-running-time-of-n-computers", title="Maximum Running Time of N Computers", diff="Hard", topic="Binary Search",
    fn="maxRunTime", params=[("n", "int"), ("batteries", "int[]")], ret="int", cmp="exact", tier="extra",
    desc="<p>You have <code>n</code> computers and a set of batteries; battery <code>i</code> can power one computer for <code>batteries[i]</code> minutes in total. Each computer needs exactly one battery connected at every minute it runs. At any whole minute you may disconnect any batteries and connect others, as often as you like and instantly; a battery can be moved between computers and used in several separate stretches, but never powers two computers in the same minute, and it stops working once its charge is used up. You are given at least <code>n</code> batteries.</p><p>Return the largest integer <code>T</code> such that all <code>n</code> computers can run simultaneously for <code>T</code> minutes.</p><p>Example: <code>n = 2</code>, <code>batteries = [3, 3, 3]</code>. Total charge 9 allows at most 4 minutes for two computers. Rotating the batteries gives exactly 4 minutes, so the answer is 4.</p>",
    constraints=["1 &le; n &le; batteries.length &le; 8,000", "1 &le; batteries[i] &le; 10<sup>5</sup>"],
    hints=["Ask the yes/no question for a target <code>T</code>: can all computers run for <code>T</code> minutes? Total charge needed is <code>n * T</code>.",
           "A single battery can never contribute more than <code>T</code> minutes to the target, however large its charge. So its useful charge is <code>min(b, T)</code>.",
           "It turns out that <code>T</code> is achievable exactly when <code>sum(min(b, T)) &ge; n * T</code>. This is monotone in <code>T</code>, so binary search <code>T</code> between 0 and <code>sum(batteries) // n</code>."],
    editorial=["For a target <code>T</code>, each battery can supply at most <code>T</code> minutes, because during the <code>T</code> minutes it can power only one computer at a time. So the usable supply is <code>sum(min(b, T))</code>, and we need <code>n * T</code> minutes of power in total. The condition <code>sum(min(b, T)) &ge; n * T</code> is necessary. It is also sufficient: lay the <code>T</code> minutes of all computers out as a long line of <code>n * T</code> slots and fill batteries into it one after another, each battery taking at most <code>T</code> consecutive slots; a battery never wraps onto the same computer's minute twice because its length is at most <code>T</code>.",
               "The condition is monotone: as <code>T</code> grows, the left side grows by at most one per battery that is still unsaturated, while the right side grows by <code>n</code>. Since at least <code>n</code> batteries exist, once it fails it keeps failing. Binary search in O(m log(sum / n)) time with O(1) extra space, where <code>m</code> is the number of batteries. A greedy that keeps the <code>n - 1</code> largest batteries as dedicated and averages the rest also works."],
    time="O(m log S)", space="O(1)",
    solution='''def maxRunTime(n, batteries):
    lo, hi = 0, sum(batteries) // n
    while lo < hi:
        mid = (lo + hi + 1) // 2
        supply = 0
        for b in batteries:
            supply += b if b < mid else mid
        if supply >= n * mid:
            lo = mid
        else:
            hi = mid - 1
    return lo
''',
    tests=[[2, [3, 3, 3]], [2, [1, 1, 1, 1]], [1, [5]], [1, [2, 3, 4]], [3, [1, 1, 1]], [3, [10, 10, 3, 5]], [2, [100000, 1]],
           [2, [100000, 100000]], [4, [7, 7, 7, 7, 7, 7]], [2, [9, 1, 1, 1]], [3, [1, 2, 3, 4, 5, 6]]],
)
_r = rnd(9310)
_b = [_r.randint(1, 10 ** 5) for _ in range(3000)]
p["tests"].append([1, _b])
p["tests"].append([2, _b])
p["tests"].append([1000, _b])
p["tests"].append([3000, _b])
_b = [_r.randint(1, 10 ** 5) for _ in range(20)] + [_r.randint(1, 10) for _ in range(3000)]
p["tests"].append([20, _b])


def b_run(n, batteries):
    from functools import lru_cache

    @lru_cache(maxsize=None)
    def f(state):
        live = [i for i, c in enumerate(state) if c > 0]
        if len(live) < n:
            return 0
        best = 0
        from itertools import combinations
        for combo in combinations(live, n):
            nxt = list(state)
            for i in combo:
                nxt[i] -= 1
            best = max(best, 1 + f(tuple(sorted(nxt))))
        return best

    return f(tuple(sorted(batteries)))


def g_run(r):
    m = r.randint(1, 5)
    return [r.randint(1, m), [r.randint(1, 5) for _ in range(m)]]


def v_run(tests):
    for t in tests:
        n, b = t["args"]
        assert 1 <= n <= len(b) <= 8000 and all(1 <= x <= 10 ** 5 for x in b)


CHECKS["maximum-running-time-of-n-computers"] = (b_run, g_run, "exact")
VALIDATE["maximum-running-time-of-n-computers"] = v_run

p = add(
    id="floor-of-max-average-long-subarray", title="Best Average of a Long Stretch, Rounded Down", diff="Hard", topic="Binary Search",
    fn="bestAverageFloor", params=[("nums", "int[]"), ("k", "int")], ret="int", cmp="exact", tier="extra",
    desc="<p>Among all contiguous subarrays of <code>nums</code> that contain <strong>at least</strong> <code>k</code> elements, take the one with the largest average. Return that largest average <em>rounded down</em> to the nearest integer (round towards negative infinity, so the floor of <code>-2.5</code> is <code>-3</code>).</p><p>Equivalently: return the largest integer <code>x</code> such that some subarray of length at least <code>k</code> has average at least <code>x</code>.</p><p>Example: <code>nums = [1, 12, -5, -6, 50, 3]</code>, <code>k = 4</code>. The subarray <code>[12, -5, -6, 50]</code> has sum 51 over 4 elements, average 12.75, and it is the best one of length at least 4 (the other candidates average 0.5, 10.5, 10.4, 10.8 and about 9.17). The answer is 12.</p>",
    constraints=["1 &le; k &le; nums.length &le; 8,000", "-10<sup>6</sup> &le; nums[i] &le; 10<sup>6</sup>"],
    hints=["Checking all subarrays of length at least <code>k</code> costs O(n<sup>2</sup>) with prefix sums. Instead of finding the best average directly, ask a yes/no question about a guess.",
           "Is there a subarray of length at least <code>k</code> whose average is at least <code>x</code>? Subtract <code>x</code> from every element: the question becomes whether some such subarray has a sum of at least 0. If the answer is yes for <code>x</code> it is also yes for every smaller value.",
           "Binary search the integer <code>x</code> between <code>min(nums)</code> and <code>max(nums)</code>. To test one <code>x</code>, build prefix sums of <code>nums[i] - x</code> and, while sweeping the right end <code>i &ge; k</code>, maintain the minimum prefix among positions <code>0..i-k</code>; the test succeeds as soon as <code>prefix[i] - minPrefix &ge; 0</code>."],
    editorial=["Maximising an average directly is awkward, but checking a guess is easy. A subarray of length <code>L</code> has average at least <code>x</code> exactly when the sum of <code>(nums[i] - x)</code> over it is at least 0. Call a guess <em>feasible</em> if such a subarray of length at least <code>k</code> exists. Lowering <code>x</code> raises every shifted sum, so feasibility is monotone: true for all small <code>x</code>, false for all large <code>x</code>. The answer is the last feasible integer.",
               "To test a guess in O(n), let <code>P</code> be the prefix sums of the shifted values. A subarray ending at index <code>i</code> (prefix position <code>i + 1</code>) with length at least <code>k</code> starts at a prefix position at most <code>i + 1 - k</code>, so the best partner is the smallest prefix value seen so far at that distance. Sweep once, update the running minimum one step behind the current end, and stop successfully when the difference is non-negative.",
               "Any average lies between <code>min(nums)</code> and <code>max(nums)</code>, and <code>x = min(nums)</code> is always feasible, so the search range is at most 2&middot;10<sup>6</sup> wide, about 21 probes. Total time is O(n log(max - min)) with O(1) extra space if the prefix sum is kept as a running value (the prefix array is also fine). Use the upper midpoint when moving <code>lo = mid</code>, and remember that Python's <code>//</code> already floors negative numbers correctly."],
    time="O(n log R)", space="O(n)",
    solution='''def bestAverageFloor(nums, k):
    n = len(nums)
    lo, hi = min(nums), max(nums)
    while lo < hi:
        mid = (lo + hi + 1) // 2
        pre = [0] * (n + 1)
        for i in range(n):
            pre[i + 1] = pre[i] + nums[i] - mid
        best_start = 0
        ok = False
        for end in range(k, n + 1):
            if pre[end - k] < best_start:
                best_start = pre[end - k]
            if pre[end] - best_start >= 0:
                ok = True
                break
        if ok:
            lo = mid
        else:
            hi = mid - 1
    return lo
''',
    tests=[[[1, 12, -5, -6, 50, 3], 4], [[5], 1], [[-5], 1], [[-3, -4], 1], [[-3, -4], 2], [[1, 2, 3, 4, 5], 5], [[1, 2, 3, 4, 5], 1],
           [[-1, -2, -3, -4], 2], [[10 ** 6, -10 ** 6, 10 ** 6, -10 ** 6], 3], [[0, 0, 0], 2], [[7, 7, 7, 7], 3],
           [[-10 ** 6, -10 ** 6 + 1, -10 ** 6], 2], [[4, 0, 0, 0, 9], 2], [[-2, -3], 2]],
)
_r = rnd(9311)
_a = [_r.randint(-10 ** 6, 10 ** 6) for _ in range(3000)]
p["tests"].append([_a, 1])
p["tests"].append([_a, 700])
p["tests"].append([_a, 3000])
_a = [_r.randint(-1000, 1000) for _ in range(4000)]
_a[1500:1600] = [_r.randint(900, 1000) for _ in range(100)]
p["tests"].append([_a, 50])


def b_bestavg(nums, k):
    n = len(nums)
    best = None
    for i in range(n):
        s = 0
        for j in range(i, n):
            s += nums[j]
            if j - i + 1 >= k:
                v = s // (j - i + 1)
                if best is None or v > best:
                    best = v
    return best


def g_bestavg(r):
    n = r.randint(1, 9)
    return [[r.randint(-8, 8) for _ in range(n)], r.randint(1, n)]


def v_bestavg(tests):
    for t in tests:
        nums, k = t["args"]
        assert 1 <= k <= len(nums) <= 8000 and all(-10 ** 6 <= x <= 10 ** 6 for x in nums)
        assert min(nums) <= t["expected"] <= max(nums)


CHECKS["floor-of-max-average-long-subarray"] = (b_bestavg, g_bestavg, "exact")
VALIDATE["floor-of-max-average-long-subarray"] = v_bestavg
