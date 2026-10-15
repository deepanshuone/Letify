"""Problems: arrays & hashing, bucket and counting methods. See data/lib.py for the registry."""
from collections import Counter

from lib import add, rnd, CHECKS, VALIDATE, gen_arr  # noqa: F401

INT_MIN, INT_MAX = -(2 ** 31), 2 ** 31 - 1
TOPIC = "Arrays & Hashing"


# ---------------------------------------------------------------- EASY

p = add(
    id="sort-array-by-frequency", title="Sort Array by Frequency", diff="Easy", topic=TOPIC,
    fn="sortByFrequency", params=[("nums", "int[]")], ret="int[]", cmp="exact",
    desc="<p>Rearrange the integer array <code>nums</code> so that values that occur <em>less</em> often come first. Values with the same number of occurrences must appear with the <em>larger</em> value first. All copies of a value stay together in the result.</p><p>Return the rearranged array.</p><p>For example, <code>[1, 1, 2, 2, 2, 3]</code> becomes <code>[3, 1, 1, 2, 2, 2]</code>, and <code>[2, 3, 1, 3, 2]</code> becomes <code>[1, 3, 3, 2, 2]</code> (3 and 2 both occur twice, so 3 goes first).</p>",
    constraints=["1 &le; nums.length &le; 4,000", "-1,000 &le; nums[i] &le; 1,000"],
    hints=["First find how many times each value occurs. A hash map or a fixed-size count array both work.",
           "The sort key of a value is the pair (count, -value). Every copy of a value shares the same key.",
           "A count never exceeds n, so instead of a comparison sort you can place values into buckets indexed by their count, sort each (small) bucket by descending value and read the buckets from count 1 upward, writing each value as many times as its count."],
    editorial=["Count occurrences, then group the distinct values by their count: <code>buckets[c]</code> holds every value that occurs exactly <code>c</code> times. Walk <code>c</code> from 1 to <code>n</code>; for each bucket, sort its values in descending order and append each value <code>c</code> times to the answer.",
               "The only comparison sorting left is inside buckets, whose total size is the number of distinct values. Sorting the whole array with the key <code>(count[x], -x)</code> is the shorter code and is equally fine here at O(n log n)."],
    time="O(n + d log d)", space="O(n)",
    solution='''def sortByFrequency(nums):
    count = {}
    for x in nums:
        count[x] = count.get(x, 0) + 1
    buckets = [[] for _ in range(len(nums) + 1)]
    for x, c in count.items():
        buckets[c].append(x)
    out = []
    for c in range(1, len(nums) + 1):
        for x in sorted(buckets[c], reverse=True):
            out.extend([x] * c)
    return out
''',
    tests=[[[1, 1, 2, 2, 2, 3]], [[2, 3, 1, 3, 2]], [[5]], [[4, 4, 4]], [[-1, -2, -3]], [[3, -3, 3, -3]],
           [[0, 1, 0, 1, 0, 2, 2, 2, 2]], [[7, 8, 9, 9, 8, 7, 7]], [[1000, -1000, 1000, 0, 0, 5]]],
)
_r = rnd(5001)
p["tests"].append([[_r.randint(-1000, 1000) for _ in range(4000)]])
p["tests"].append([[_r.choice([-5, 0, 7, 100, 999]) if _r.random() < 0.8 else _r.randint(-1000, 1000) for _ in range(4000)]])
p["tests"].append([[i % 40 - 20 for i in range(4000)]])


def b_sortfreq(nums):
    return sorted(nums, key=lambda x: (nums.count(x), -x))


def v_sortfreq(tests):
    for t in tests:
        a = t["args"][0]
        assert 1 <= len(a) <= 4000 and all(-1000 <= x <= 1000 for x in a)


CHECKS["sort-array-by-frequency"] = (b_sortfreq, lambda r: [gen_arr(r, -4, 4, 1, 14)], "exact")
VALIDATE["sort-array-by-frequency"] = v_sortfreq

p = add(
    id="relative-sort-by-reference-order", title="Relative Sort by Reference Order", diff="Easy", topic=TOPIC,
    fn="relativeSort", params=[("arr", "int[]"), ("order", "int[]")], ret="int[]", cmp="exact",
    desc="<p>You are given an integer array <code>arr</code> and a reference array <code>order</code> of <em>distinct</em> integers. Reorder <code>arr</code> as follows:</p><ul><li>Values that appear in <code>order</code> come first, arranged in the same sequence as in <code>order</code>. All copies of such a value are kept together.</li><li>Values that do not appear in <code>order</code> come after them, in ascending order.</li></ul><p>Values of <code>order</code> that do not occur in <code>arr</code> are simply skipped. Return the reordered array.</p><p>For example, <code>arr = [2, 3, 1, 3, 2, 4, 6, 7, 9, 2, 19]</code> and <code>order = [2, 1, 4, 3, 9, 6]</code> give <code>[2, 2, 2, 1, 4, 3, 3, 9, 6, 7, 19]</code>.</p>",
    constraints=["1 &le; arr.length &le; 4,000", "0 &le; order.length &le; 1,001", "0 &le; arr[i], order[i] &le; 1,000", "All values in order are distinct"],
    hints=["Comparison sorting with a custom key works. Can the small value range give you something faster?",
           "Count how many times each value from 0 to 1000 occurs in <code>arr</code>.",
           "First walk through <code>order</code> and output each value as many times as its count (then set its count to 0). Afterwards walk the counts from 0 to 1000 and output whatever is left."],
    editorial=["This is a counting sort with a twist. Build <code>cnt[v]</code> for every value 0..1000. For each <code>v</code> in <code>order</code>, emit <code>v</code> exactly <code>cnt[v]</code> times and reset <code>cnt[v]</code> to 0 so those values are not emitted again. Finally scan <code>v = 0..1000</code> and emit the remaining counts; this part is automatically in ascending order.",
               "The running time is O(n + m + R) where <code>m</code> is the length of <code>order</code> and <code>R = 1001</code> is the size of the value range. A custom comparison sort with key <code>(rank in order, value)</code> gives the same result in O(n log n)."],
    time="O(n + m + R)", space="O(R)",
    solution='''def relativeSort(arr, order):
    cnt = [0] * 1001
    for x in arr:
        cnt[x] += 1
    out = []
    for v in order:
        out.extend([v] * cnt[v])
        cnt[v] = 0
    for v in range(1001):
        out.extend([v] * cnt[v])
    return out
''',
    tests=[[[2, 3, 1, 3, 2, 4, 6, 7, 9, 2, 19], [2, 1, 4, 3, 9, 6]], [[28, 6, 22, 8, 44, 17], [22, 28, 8, 6]],
           [[5], [5]], [[5], []], [[3, 1, 2], []], [[1, 1, 1], [2, 1, 3]], [[0, 1000, 0, 1000, 500], [1000, 0]],
           [[4, 4, 3, 3, 2, 2], [2, 3]], [[9, 8, 7], [7, 8, 9]], [[1000, 999, 998, 1], [998]]],
)
_r = rnd(5002)
_o = _r.sample(range(1001), 600)
p["tests"].append([[_r.randint(0, 1000) for _ in range(4000)], _o])
_o = _r.sample(range(1001), 1001)
p["tests"].append([[_r.randint(0, 1000) for _ in range(4000)], _o])
p["tests"].append([[_r.randint(0, 30) for _ in range(4000)], _r.sample(range(0, 1001), 40)])


def b_relsort(arr, order):
    pos = {v: i for i, v in enumerate(order)}
    return sorted(arr, key=lambda x: (pos.get(x, len(order)), x))


def g_relsort(r):
    arr = gen_arr(r, 0, 8, 1, 12)
    order = r.sample(range(0, 10), r.randint(0, 6))
    return [arr, order]


def v_relsort(tests):
    for t in tests:
        arr, order = t["args"]
        assert 1 <= len(arr) <= 4000 and len(order) <= 1001 and len(set(order)) == len(order)
        assert all(0 <= x <= 1000 for x in arr + order)


CHECKS["relative-sort-by-reference-order"] = (b_relsort, g_relsort, "exact")
VALIDATE["relative-sort-by-reference-order"] = v_relsort

p = add(
    id="count-smaller-values-than-each", title="Count Smaller Values Than Each Element", diff="Easy", topic=TOPIC, tier="extra",
    fn="countSmaller", params=[("nums", "int[]")], ret="int[]", cmp="exact",
    desc="<p>For every position <code>i</code> of <code>nums</code>, count how many elements of the whole array are strictly smaller than <code>nums[i]</code>, and return these counts as an array in the original order.</p><p>For example, <code>[8, 1, 2, 2, 3]</code> gives <code>[4, 0, 1, 1, 3]</code>.</p>",
    constraints=["1 &le; nums.length &le; 8,000", "0 &le; nums[i] &le; 100"],
    hints=["Comparing every pair is O(n<sup>2</sup>). The values are small, so many positions share the same answer.",
           "Count how many times each value from 0 to 100 occurs.",
           "The answer for value <code>v</code> is the number of elements with value 0..v-1: a prefix sum over the counts. Then each position is a lookup."],
    editorial=["Build <code>cnt[v]</code> for all values 0..100. Turn it into a prefix array <code>less[v] = cnt[0] + ... + cnt[v-1]</code>, which is exactly the number of elements strictly below <code>v</code>. The answer for <code>nums[i]</code> is <code>less[nums[i]]</code>.",
               "This costs O(n + R) with R = 101, instead of O(n<sup>2</sup>) for pairwise comparison or O(n log n) for sorting with binary search. It is the counting-sort idea without actually producing the sorted array."],
    time="O(n + R)", space="O(R)",
    solution='''def countSmaller(nums):
    cnt = [0] * 101
    for x in nums:
        cnt[x] += 1
    less = [0] * 102
    for v in range(101):
        less[v + 1] = less[v] + cnt[v]
    return [less[x] for x in nums]
''',
    tests=[[[8, 1, 2, 2, 3]], [[6, 5, 4, 8]], [[7, 7, 7, 7]], [[0]], [[100]], [[100, 0]], [[0, 0, 1]], [[3, 2, 1, 0]],
           [[5, 5, 6, 6, 7, 7]], [[100, 99, 100, 98, 0, 0]]],
)
_r = rnd(5003)
p["tests"].append([[_r.randint(0, 100) for _ in range(8000)]])
p["tests"].append([[_r.choice([0, 50, 100]) for _ in range(8000)]])


def b_countsmaller(nums):
    return [sum(1 for y in nums if y < x) for x in nums]


def v_countsmaller(tests):
    for t in tests:
        a = t["args"][0]
        assert 1 <= len(a) <= 8000 and all(0 <= x <= 100 for x in a)


CHECKS["count-smaller-values-than-each"] = (b_countsmaller, lambda r: [gen_arr(r, 0, 9, 1, 14)], "exact")
VALIDATE["count-smaller-values-than-each"] = v_countsmaller


# ---------------------------------------------------------------- MEDIUM

p = add(
    id="top-k-frequent-ordered", title="Top K Frequent Values in Rank Order", diff="Medium", topic=TOPIC,
    fn="topKRanked", params=[("nums", "int[]"), ("k", "int")], ret="int[]", cmp="exact",
    desc="<p>Rank the distinct values of <code>nums</code> by how often they occur: a value that occurs more often ranks higher, and among values with the same number of occurrences the <em>smaller</em> value ranks higher.</p><p>Return the <code>k</code> best-ranked values as an array, from rank 1 downward. Aim for better than O(n log n) time.</p><p>For example, <code>nums = [4, 4, 5, 5, 6]</code> and <code>k = 3</code> give <code>[4, 5, 6]</code>, and <code>nums = [1, 1, 1, 2, 2, 3]</code> with <code>k = 2</code> gives <code>[1, 2]</code>.</p>",
    constraints=["1 &le; nums.length &le; 5,000", "-10<sup>9</sup> &le; nums[i] &le; 10<sup>9</sup>", "1 &le; k &le; number of distinct values in nums"],
    hints=["Count the occurrences of each distinct value with a hash map.",
           "A count is never larger than n. Put each value into a bucket indexed by its count.",
           "Scan the buckets from count n down to 1. Inside a bucket output the values in ascending order, and stop as soon as you have k values."],
    editorial=["After counting, build <code>buckets[c]</code> = list of values that occur exactly <code>c</code> times. Scanning <code>c</code> from <code>n</code> down to 1 visits values from most to least frequent; inside one bucket the tie rule means we sort ascending before taking values. Stop once <code>k</code> values have been collected.",
               "Counting is O(n), the bucket scan is O(n), and the total work of sorting inside buckets is at most O(d log d) for d distinct values (usually much less because buckets are tiny). The comparison sort <code>sorted(distinct, key=lambda v: (-count[v], v))[:k]</code> is the simple alternative; a heap of size k gives O(n log k)."],
    time="O(n + d log d)", space="O(n)",
    solution='''def topKRanked(nums, k):
    count = {}
    for x in nums:
        count[x] = count.get(x, 0) + 1
    buckets = [[] for _ in range(len(nums) + 1)]
    for x, c in count.items():
        buckets[c].append(x)
    out = []
    for c in range(len(nums), 0, -1):
        for x in sorted(buckets[c]):
            out.append(x)
            if len(out) == k:
                return out
    return out
''',
    tests=[[[4, 4, 5, 5, 6], 3], [[1, 1, 1, 2, 2, 3], 2], [[7], 1], [[7, 7, 7], 1], [[3, 1, 2], 3], [[3, 1, 2], 1],
           [[-1, -1, 2, 2, -3, -3, 0], 4], [[5, 5, 5, 6, 6, 6, 4, 4, 4, 9], 2], [[10 ** 9, -10 ** 9, 10 ** 9], 2],
           [[2, 2, 1, 1, 3, 3, 3, 4], 4]],
)
_r = rnd(5004)
p["tests"].append([[_r.randint(-10 ** 9, 10 ** 9) for _ in range(5000)], 700])
p["tests"].append([[_r.choice([_r.randint(-50, 50), _r.randint(-10 ** 9, 10 ** 9)]) for _ in range(5000)], 40])
p["tests"].append([[i // 5 for i in range(5000)], 600])


def b_topranked(nums, k):
    return sorted(set(nums), key=lambda v: (-nums.count(v), v))[:k]


def g_topranked(r):
    a = gen_arr(r, -4, 4, 1, 14)
    return [a, r.randint(1, len(set(a)))]


def v_topranked(tests):
    for t in tests:
        a, k = t["args"]
        assert 1 <= len(a) <= 5000 and all(-10 ** 9 <= x <= 10 ** 9 for x in a)
        assert 1 <= k <= len(set(a))


CHECKS["top-k-frequent-ordered"] = (b_topranked, g_topranked, "exact")
VALIDATE["top-k-frequent-ordered"] = v_topranked

p = add(
    id="h-index-from-citations", title="H-Index from Citation Counts", diff="Medium", topic=TOPIC,
    fn="hIndex", params=[("citations", "int[]")], ret="int", cmp="exact",
    desc="<p><code>citations[i]</code> is the number of citations received by the <code>i</code>-th paper of a researcher. The researcher's <em>h-index</em> is the largest integer <code>h</code> such that at least <code>h</code> papers have <code>h</code> or more citations each.</p><p>Return the h-index. An h-index of <code>0</code> is always possible.</p><p>For example, <code>[3, 0, 6, 1, 5]</code> gives <code>3</code>: three papers have at least 3 citations, but there are not four papers with at least 4.</p>",
    constraints=["1 &le; citations.length &le; 8,000", "0 &le; citations[i] &le; 10<sup>9</sup>"],
    hints=["Sorting the array in descending order and finding the last position <code>i</code> with <code>citations[i] &ge; i + 1</code> works in O(n log n).",
           "The answer can never exceed n, the number of papers, so every citation count above n can be treated as exactly n.",
           "Make an array <code>bucket[0..n]</code> where <code>bucket[c]</code> counts papers with min(c, n) citations. Walk <code>h</code> from n down to 0, accumulating the number of papers with at least <code>h</code> citations, and stop at the first <code>h</code> where that total is at least <code>h</code>."],
    editorial=["Let <code>n</code> be the number of papers. Since h cannot exceed n, clamp every citation count to n and count them into <code>bucket[0..n]</code>. Now iterate <code>h</code> from n down to 0 while keeping <code>papers</code>, the number of papers with at least <code>h</code> citations (add <code>bucket[h]</code> at each step). The first <code>h</code> with <code>papers &ge; h</code> is the largest valid one.",
               "This is a counting sort on a clamped range, so it runs in O(n) time and O(n) space, compared to O(n log n) for sorting. Correctness comes from monotonicity: as h decreases, <code>papers</code> only grows, while h shrinks, so the first success scanning downward is the maximum."],
    time="O(n)", space="O(n)",
    solution='''def hIndex(citations):
    n = len(citations)
    bucket = [0] * (n + 1)
    for c in citations:
        bucket[min(c, n)] += 1
    papers = 0
    for h in range(n, -1, -1):
        papers += bucket[h]
        if papers >= h:
            return h
    return 0
''',
    tests=[[[3, 0, 6, 1, 5]], [[1, 3, 1]], [[0]], [[0, 0, 0]], [[1]], [[100]], [[5, 5, 5, 5, 5]], [[4, 4, 4, 4]],
           [[1, 2, 3, 4, 5, 6]], [[10 ** 9, 10 ** 9, 0]], [[2, 2, 2, 2, 2, 2, 2]]],
)
_r = rnd(5005)
p["tests"].append([[_r.randint(0, 10 ** 9) for _ in range(5000)]])
p["tests"].append([[_r.randint(0, 6000) for _ in range(8000)]])
p["tests"].append([[_r.randint(0, 4000) for _ in range(7000)]])


def b_hindex(c):
    best = 0
    for h in range(1, len(c) + 1):
        if sum(1 for x in c if x >= h) >= h:
            best = h
    return best


def v_hindex(tests):
    for t in tests:
        a = t["args"][0]
        assert 1 <= len(a) <= 8000 and all(0 <= x <= 10 ** 9 for x in a)


CHECKS["h-index-from-citations"] = (b_hindex, lambda r: [gen_arr(r, 0, 8, 1, 12)], "exact")
VALIDATE["h-index-from-citations"] = v_hindex

p = add(
    id="running-mode-of-prefixes", title="Running Mode of Every Prefix", diff="Medium", topic=TOPIC, tier="extra",
    fn="runningMode", params=[("nums", "int[]")], ret="int[]", cmp="exact",
    desc="<p>For every prefix <code>nums[0..i]</code> of the array, find its <em>mode</em>: the value that occurs most often in that prefix. If several values are tied for most occurrences, the mode is the <em>smallest</em> of them.</p><p>Return an array <code>res</code> where <code>res[i]</code> is the mode of the prefix ending at index <code>i</code>.</p><p>For example, <code>[2, 1, 1, 2, 3, 3, 3]</code> gives <code>[2, 1, 1, 1, 1, 1, 3]</code>.</p>",
    constraints=["1 &le; nums.length &le; 3,000", "-10<sup>9</sup> &le; nums[i] &le; 10<sup>9</sup>"],
    hints=["Recomputing the mode of every prefix from scratch costs O(n<sup>2</sup>). Update the counts incrementally instead.",
           "Adding one element increases exactly one count by 1. So the maximum count either stays the same or grows by exactly 1, and only the touched value can become a new best.",
           "Keep <code>count</code>, the current maximum count <code>best</code> and the current mode <code>mode</code>. After incrementing <code>count[x]</code>: if it exceeds <code>best</code>, then <code>x</code> is the sole leader; if it equals <code>best</code>, the mode becomes <code>min(mode, x)</code>."],
    editorial=["Only the value just added can change status. After <code>count[x]</code> increases: if <code>count[x] &gt; best</code>, then <code>x</code> is now strictly ahead of everybody, so <code>best = count[x]</code> and <code>mode = x</code>. If <code>count[x] == best</code>, <code>x</code> has joined the tied group, and the smallest tied value is <code>min(mode, x)</code> because the old mode was already the smallest of the previous group. If it is below <code>best</code> nothing changes.",
               "Every step is O(1) with a hash map, so the whole array takes O(n). The trick that makes the tie rule easy is that counts only ever grow: values never leave the leading group, so tracking its minimum is enough."],
    time="O(n)", space="O(n)",
    solution='''def runningMode(nums):
    count = {}
    best = 0
    mode = None
    out = []
    for x in nums:
        c = count.get(x, 0) + 1
        count[x] = c
        if c > best:
            best = c
            mode = x
        elif c == best and x < mode:
            mode = x
        out.append(mode)
    return out
''',
    tests=[[[2, 1, 1, 2, 3, 3, 3]], [[5]], [[3, 2, 1]], [[1, 2, 3]], [[7, 7, 7, 7]], [[-1, 1, -1, 1, 0, 0, 0]],
           [[4, 5, 5, 4, 4]], [[10 ** 9, -10 ** 9, -10 ** 9, 10 ** 9]], [[9, 8, 7, 7, 8, 9, 9, 8]],
           [[0, 0, -3, -3, -3, 0, 0]]],
)
_r = rnd(5006)
p["tests"].append([[_r.randint(-10 ** 9, 10 ** 9) for _ in range(3000)]])
p["tests"].append([[_r.randint(-8, 8) for _ in range(3000)]])
p["tests"].append([[_r.choice([1, 2, 3]) * (-1) ** i for i in range(3000)]])


def b_runmode(nums):
    out = []
    for i in range(len(nums)):
        pre = nums[:i + 1]
        out.append(min(pre, key=lambda v: (-pre.count(v), v)))
    return out


def v_runmode(tests):
    for t in tests:
        a = t["args"][0]
        assert 1 <= len(a) <= 3000 and all(-10 ** 9 <= x <= 10 ** 9 for x in a)


CHECKS["running-mode-of-prefixes"] = (b_runmode, lambda r: [gen_arr(r, -3, 3, 1, 14)], "exact")
VALIDATE["running-mode-of-prefixes"] = v_runmode

p = add(
    id="min-increments-to-make-unique", title="Minimum Increments to Make Values Unique", diff="Medium", topic=TOPIC,
    fn="minIncrements", params=[("nums", "int[]")], ret="int", cmp="exact",
    desc="<p>In one move you may pick any element of <code>nums</code> and increase it by <code>1</code>. Return the minimum number of moves needed to make all elements pairwise distinct. Values may grow beyond the original maximum.</p><p>For example, <code>[3, 2, 1, 2, 1, 7]</code> needs <code>6</code> moves: the sorted values <code>1, 1, 2, 2, 3, 7</code> can become <code>1, 2, 3, 4, 5, 7</code>.</p>",
    constraints=["1 &le; nums.length &le; 4,000", "0 &le; nums[i] &le; 100,000"],
    hints=["Only the multiset of values matters, not the positions. What does the smallest valid arrangement look like if the values were sorted?",
           "Process values from small to large. A value that occurs several times must spread over consecutive free slots: one copy stays, the others move up.",
           "Sweep <code>v</code> over the range with a <code>carry</code> of surplus copies. At each <code>v</code>, add <code>cnt[v]</code> to the pending copies, let one of them settle at <code>v</code>, and pay the number of copies still pending (each moves one step further). Continue past the max value until the carry is empty."],
    editorial=["Count occurrences per value and sweep upward from 0. Keep <code>pending</code>, the number of elements that are waiting for a free slot at or above the current value. At value <code>v</code>, <code>pending += cnt[v]</code>. If <code>pending &gt; 0</code>, one element settles at <code>v</code> (<code>pending -= 1</code>); every other pending element has to move to <code>v + 1</code>, which costs <code>pending</code> moves in total. Continue until the sweep is past the maximum and <code>pending</code> is zero.",
               "The sweep covers at most <code>max + n</code> values, so the time is O(n + max). The greedy is optimal because moving an element past a free slot only increases the cost. Sorting and fixing each element to <code>max(prev + 1, x)</code> gives the same answer in O(n log n)."],
    time="O(n + max)", space="O(max + n)",
    solution='''def minIncrements(nums):
    size = max(nums) + len(nums) + 1
    cnt = [0] * size
    for x in nums:
        cnt[x] += 1
    pending = 0
    moves = 0
    for v in range(size):
        pending += cnt[v]
        if pending:
            pending -= 1
            moves += pending
    return moves
''',
    tests=[[[3, 2, 1, 2, 1, 7]], [[1, 2, 2]], [[5]], [[0, 0]], [[0, 0, 0, 0]], [[1, 2, 3]], [[100000, 100000, 100000]],
           [[3, 3, 3, 1, 1]], [[2, 2, 2, 2, 5, 5, 6]], [[4, 3, 2, 1, 0]]],
)
_r = rnd(5007)
p["tests"].append([[_r.randint(0, 100000) for _ in range(4000)]])
p["tests"].append([[_r.randint(0, 50) for _ in range(4000)]])
p["tests"].append([[100000] * 4000])
p["tests"].append([[_r.randint(0, 4000) for _ in range(4000)]])


def b_minincr(nums):
    # exact search: give each element a distinct target >= its value, minimise the total raise
    n = len(nums)
    top = max(nums) + n
    a = sorted(nums)
    memo = {}

    def go(i, used):
        if i == n:
            return 0
        key = (i, used)
        if key not in memo:
            best = 10 ** 9
            for t in range(a[i], top + 1):
                if not used >> t & 1:
                    best = min(best, t - a[i] + go(i + 1, used | 1 << t))
            memo[key] = best
        return memo[key]

    return go(0, 0)


def v_minincr(tests):
    for t in tests:
        a = t["args"][0]
        assert 1 <= len(a) <= 4000 and all(0 <= x <= 100000 for x in a)


CHECKS["min-increments-to-make-unique"] = (b_minincr, lambda r: [gen_arr(r, 0, 5, 1, 6)], "exact")
VALIDATE["min-increments-to-make-unique"] = v_minincr

p = add(
    id="min-deletions-distinct-frequencies", title="Minimum Deletions for Distinct Frequencies", diff="Medium", topic=TOPIC,
    fn="minDeletions", params=[("nums", "int[]")], ret="int", cmp="exact",
    desc="<p>Delete as few elements as possible from <code>nums</code> so that no two <em>different</em> values that remain occur the same number of times. (A value that disappears completely no longer counts.)</p><p>Return the minimum number of deletions.</p><p>For example, <code>[1, 1, 2, 2, 3, 3]</code> gives <code>3</code>: the three values all occur twice, so reduce them to frequencies 2, 1 and 0 by deleting 0 + 1 + 2 elements.</p>",
    constraints=["1 &le; nums.length &le; 8,000", "-10<sup>9</sup> &le; nums[i] &le; 10<sup>9</sup>"],
    hints=["Only the frequency of each value matters. Work with the list of frequencies, not the array.",
           "If two values have the same frequency, one of them must lose at least one element. Lowering a frequency by one costs exactly one deletion.",
           "Process frequencies from the largest to the smallest. Keep the highest frequency <code>limit</code> that is still allowed: each value takes <code>min(freq, limit)</code> and then the limit drops by one (but not below zero). Sum the differences."],
    editorial=["Collect the frequencies of the distinct values and sort them in descending order, or bucket them by size: <code>cc[f]</code> is the number of values that have frequency <code>f</code>. Scan <code>f</code> from the maximum down to 1 carrying <code>extra</code>, the number of values that are stuck on a taken frequency. At each <code>f</code>, <code>total = cc[f] + extra</code>; one value may keep <code>f</code>, so <code>extra = total - 1</code> (if <code>total &gt; 0</code>), and each of those <code>extra</code> values pays one deletion to step down to <code>f - 1</code>.",
               "Equivalently, in the sorted view each value takes the largest frequency not exceeding its own that is still free. A frequency may drop all the way to zero, in which case the value is deleted entirely and its slot is no longer blocking anyone. The total work is O(n) with the bucket scan, or O(d log d) with sorting."],
    time="O(n)", space="O(n)",
    solution='''def minDeletions(nums):
    count = {}
    for x in nums:
        count[x] = count.get(x, 0) + 1
    cc = [0] * (len(nums) + 1)
    for c in count.values():
        cc[c] += 1
    deletions = 0
    extra = 0
    for f in range(len(nums), 0, -1):
        total = cc[f] + extra
        if total > 0:
            extra = total - 1
            deletions += extra
        else:
            extra = 0
    return deletions
''',
    tests=[[[1, 1, 2, 2, 3, 3]], [[1, 2, 3]], [[5]], [[1, 1, 2, 2, 3]], [[1, 1, 1, 2, 2, 2, 3, 3, 3, 4]],
           [[7, 7, 7, 7]], [[1, 1, 2, 3, 3]], [[1, 2, 2, 3, 3, 3, 4, 4, 4, 4]], [[1, 1, 2, 2, 3, 3, 4, 4, 5, 5]],
           [[0, 0, 0, 1, 1, 1, 2, 2, 2, 3, 3, 3, 3]], [[-5, -5, 5, 5]]],
)
_r = rnd(5008)
p["tests"].append([[_r.randint(-10 ** 9, 10 ** 9) for _ in range(4000)] + [_r.randint(1, 60) for _ in range(4000)]])
p["tests"].append([[i // 4 for i in range(8000)]])
p["tests"].append([[_r.randint(0, 300) for _ in range(8000)]])


def b_mindel(nums):
    freqs = list(Counter(nums).values())

    def go(i, taken):
        if i == len(freqs):
            return 0
        best = freqs[i] + go(i + 1, taken)  # delete the whole value
        for f in range(1, freqs[i] + 1):
            if f not in taken:
                best = min(best, freqs[i] - f + go(i + 1, taken | {f}))
        return best

    return go(0, frozenset())


def g_mindel(r):
    return [gen_arr(r, 0, 3, 1, 12)]


def v_mindel(tests):
    for t in tests:
        a = t["args"][0]
        assert 1 <= len(a) <= 8000 and all(-10 ** 9 <= x <= 10 ** 9 for x in a)


CHECKS["min-deletions-distinct-frequencies"] = (b_mindel, g_mindel, "exact")
VALIDATE["min-deletions-distinct-frequencies"] = v_mindel


# ---------------------------------------------------------------- HARD

p = add(
    id="maximum-gap-after-sorting", title="Maximum Gap After Sorting", diff="Hard", topic=TOPIC, tier="extra",
    fn="maximumGap", params=[("nums", "int[]")], ret="int", cmp="exact",
    desc="<p>Return the largest difference between two <em>adjacent</em> elements of <code>nums</code> once it has been sorted in ascending order. If the array has fewer than two elements, return <code>0</code>.</p><p>Try to solve it in linear time and space, without a comparison sort.</p><p>For example, <code>[3, 6, 9, 1]</code> sorts to <code>[1, 3, 6, 9]</code>, so the answer is <code>3</code>.</p>",
    constraints=["0 &le; nums.length &le; 5,000", "0 &le; nums[i] &le; 10<sup>9</sup>"],
    hints=["Sorting and scanning neighbours is O(n log n). The question is how to find the largest gap without ordering everything.",
           "With n numbers between min and max, the n - 1 gaps sum to max - min, so the largest gap is at least <code>ceil((max - min) / (n - 1))</code>.",
           "Use buckets of width <code>w = max(1, (max - min) // (n - 1))</code>. Two numbers inside one bucket differ by less than <code>w</code>, so the maximum gap never lies inside a bucket. Store only the min and max of each bucket and compare each bucket's min with the previous non-empty bucket's max."],
    editorial=["Let <code>lo</code> and <code>hi</code> be the minimum and maximum. If <code>lo == hi</code> the answer is 0. Otherwise choose the bucket width <code>w = max(1, (hi - lo) // (n - 1))</code> and put every number <code>x</code> into bucket <code>(x - lo) // w</code>. By the pigeonhole principle the best gap is at least the average gap, which is at least <code>w</code>, while any two numbers in the same bucket differ by at most <code>w - 1</code>. So the winner is always a gap <em>between</em> two buckets.",
               "For every bucket keep only its smallest and largest value. Sweep the buckets in index order and for each non-empty one compute <code>its min - max of the previous non-empty bucket</code>; the maximum of these is the answer. That is O(n) time and O(n) space, because there are at most n buckets. This is the pigeonhole form of bucket sort, and it never needs to sort inside a bucket."],
    time="O(n)", space="O(n)",
    solution='''def maximumGap(nums):
    n = len(nums)
    if n < 2:
        return 0
    lo, hi = min(nums), max(nums)
    if lo == hi:
        return 0
    w = max(1, (hi - lo) // (n - 1))
    m = (hi - lo) // w + 1
    bmin = [None] * m
    bmax = [None] * m
    for x in nums:
        b = (x - lo) // w
        if bmin[b] is None or x < bmin[b]:
            bmin[b] = x
        if bmax[b] is None or x > bmax[b]:
            bmax[b] = x
    best = 0
    prev = lo
    for b in range(m):
        if bmin[b] is None:
            continue
        best = max(best, bmin[b] - prev)
        prev = bmax[b]
    return best
''',
    tests=[[[3, 6, 9, 1]], [[10]], [[]], [[5, 5, 5]], [[1, 10000000]], [[0, 10 ** 9]], [[1, 2, 3, 4, 5]],
           [[1, 100, 101, 102, 103]], [[100, 3, 2, 1]], [[9, 1, 9, 1, 5]], [[7, 7, 8]], [[0, 5, 10, 15, 20, 21]]],
)
_r = rnd(5009)
p["tests"].append([[_r.randint(0, 10 ** 9) for _ in range(5000)]])
p["tests"].append([_r.sample(range(0, 5000), 5000)])
p["tests"].append([[_r.randint(0, 1000) for _ in range(2500)] + [_r.randint(10 ** 9 - 1000, 10 ** 9) for _ in range(2500)]])


def b_maxgap(nums):
    a = sorted(nums)
    return max([a[i + 1] - a[i] for i in range(len(a) - 1)] or [0])


def v_maxgap(tests):
    for t in tests:
        a = t["args"][0]
        assert len(a) <= 5000 and all(0 <= x <= 10 ** 9 for x in a)


CHECKS["maximum-gap-after-sorting"] = (b_maxgap, lambda r: [gen_arr(r, 0, r.choice([3, 20, 1000]), 0, 12)], "exact")
VALIDATE["maximum-gap-after-sorting"] = v_maxgap

p = add(
    id="nearby-almost-equal-pair", title="Nearby Almost Equal Pair", diff="Hard", topic=TOPIC, tier="extra",
    fn="hasNearbyAlmostEqual", params=[("nums", "int[]"), ("indexDiff", "int"), ("valueDiff", "int")], ret="bool", cmp="exact",
    desc="<p>Decide whether there are two different indices <code>i</code> and <code>j</code> with <code>|i - j| &le; indexDiff</code> and <code>|nums[i] - nums[j]| &le; valueDiff</code>. Return <code>true</code> if such a pair exists, otherwise <code>false</code>.</p><p>For example, <code>nums = [1, 2, 3, 1]</code>, <code>indexDiff = 3</code>, <code>valueDiff = 0</code> gives <code>true</code> (the two 1s), while <code>nums = [1, 5, 9, 1, 5, 9]</code>, <code>indexDiff = 2</code>, <code>valueDiff = 3</code> gives <code>false</code>.</p><p>Beware of values whose difference does not fit into a 32-bit integer; use 64-bit arithmetic if your language needs it.</p>",
    constraints=["1 &le; nums.length &le; 3,000", "-2<sup>31</sup> &le; nums[i] &le; 2<sup>31</sup> - 1", "1 &le; indexDiff &le; nums.length", "0 &le; valueDiff &le; 2<sup>31</sup> - 1"],
    hints=["Checking every pair within distance <code>indexDiff</code> is O(n &middot; indexDiff). Keep only the last <code>indexDiff</code> values in a data structure.",
           "If you split the number line into buckets of width <code>valueDiff + 1</code>, two numbers in the same bucket always differ by at most <code>valueDiff</code>.",
           "Keep a hash map bucket-id &rarr; value for the current window (one value per bucket is enough, since a second one would already have been a match). A new number can only match inside its own bucket or in the two neighbouring buckets; check those, then evict the number that has left the window."],
    editorial=["Use bucket width <code>w = valueDiff + 1</code> and the bucket id <code>x // w</code> (floor division, so negatives are placed correctly). Any two numbers sharing a bucket are within <code>valueDiff</code> of each other, so a bucket never holds more than one value of the current window without an answer already being found.",
               "For each new <code>x</code> at index <code>i</code>: if its bucket exists, return true; if the left or right neighbour bucket holds a value within <code>valueDiff</code> of <code>x</code>, return true. Otherwise insert <code>x</code> and, once the window exceeds <code>indexDiff</code> elements, delete the bucket of <code>nums[i - indexDiff]</code>. Each step is O(1), so the total is O(n) time with O(min(n, indexDiff)) space. A sorted set gives O(n log n) instead."],
    time="O(n)", space="O(min(n, indexDiff))",
    solution='''def hasNearbyAlmostEqual(nums, indexDiff, valueDiff):
    w = valueDiff + 1
    window = {}
    for i, x in enumerate(nums):
        b = x // w
        if b in window:
            return True
        if b - 1 in window and x - window[b - 1] <= valueDiff:
            return True
        if b + 1 in window and window[b + 1] - x <= valueDiff:
            return True
        window[b] = x
        if i >= indexDiff:
            del window[nums[i - indexDiff] // w]
    return False
''',
    tests=[[[1, 2, 3, 1], 3, 0], [[1, 5, 9, 1, 5, 9], 2, 3], [[1, 0, 1, 1], 1, 2], [[7], 1, 0], [[-3, 2], 1, 4],
           [[-3, 2], 1, 5], [[-1, -1], 1, 0], [[10, 20, 30, 12], 3, 2], [[10, 20, 30, 12], 2, 2],
           [[INT_MIN, INT_MAX], 1, INT_MAX], [[INT_MIN, INT_MAX], 1, INT_MAX - 1], [[4, 1, 8, 2], 2, 1]],
)
_r = rnd(5010)
p["tests"].append([[i * 10 for i in range(3000)], 1800, 5])                                  # no pair at all
p["tests"].append([_r.sample(range(-10 ** 9, 10 ** 9), 3000), 40, 60000])                    # random, usually no pair
_a = [i * 1000 for i in range(3000)]
_a[2999] = _a[2999 - 120] + 3
p["tests"].append([_a, 120, 3])                                                              # only pair is at the maximum distance
_a = [i * 1000 for i in range(3000)]
_a[2999] = _a[2999 - 121] + 3
p["tests"].append([_a, 120, 3])                                                              # same pair, one step too far


def b_nearby(nums, indexDiff, valueDiff):
    n = len(nums)
    for i in range(n):
        for j in range(i + 1, min(n, i + indexDiff + 1)):
            if abs(nums[i] - nums[j]) <= valueDiff:
                return True
    return False


def g_nearby(r):
    a = gen_arr(r, -8, 8, 1, 10)
    return [a, r.randint(1, len(a)), r.randint(0, 3)]


def v_nearby(tests):
    seen = set()
    for t in tests:
        a, idx, val = t["args"]
        assert 1 <= len(a) <= 3000 and all(INT_MIN <= x <= INT_MAX for x in a)
        assert 1 <= idx <= len(a) and 0 <= val <= INT_MAX
        seen.add(t["expected"])
    assert seen == {True, False}


CHECKS["nearby-almost-equal-pair"] = (b_nearby, g_nearby, "exact")
VALIDATE["nearby-almost-equal-pair"] = v_nearby

p = add(
    id="frequency-stack-pops", title="Most Frequent Stack Pops", diff="Hard", topic=TOPIC,
    fn="frequencyStackPops", params=[("ops", "int[][]")], ret="int[]", cmp="exact",
    desc="<p>Simulate a stack-like container. You are given a list of operations <code>ops</code>, where each operation is a pair:</p><ul><li><code>[1, x]</code>: push the value <code>x</code>.</li><li><code>[0, 0]</code>: pop. Remove and report the value that occurs <em>most often</em> in the container. If several values are tied for most occurrences, remove the one whose most recent push is the latest, i.e. the one closest to the top. Exactly one copy (its most recently pushed one) is removed.</li></ul><p>Return the values reported by the pop operations, in order. A pop is only given when the container is not empty.</p><p>For example, pushing 5, 7, 5, 7, 4, 5 and then popping four times returns <code>[5, 7, 5, 4]</code>.</p>",
    constraints=["1 &le; ops.length &le; 4,000", "Each operation is [1, x] with -10<sup>9</sup> &le; x &le; 10<sup>9</sup>, or [0, 0]", "Every pop happens while the container holds at least one value"],
    hints=["Simulating each pop by scanning the whole container is O(n) per pop. You need the answer in about O(1).",
           "Keep <code>freq[x]</code>, the current number of copies of x. Imagine a separate stack for each frequency level f: the stack of level f holds, in push order, the values that have reached count f.",
           "A push of x raises <code>freq[x]</code> to f and pushes x on level-f's stack, updating the maximum level. A pop takes the top of the highest non-empty level's stack, lowers that value's frequency by one, and lowers the maximum level if that stack became empty."],
    editorial=["Maintain <code>freq</code> (value &rarr; count), <code>groups</code> (frequency &rarr; stack of values) and <code>maxf</code>. Push x: <code>freq[x] += 1</code>, append x to <code>groups[freq[x]]</code>, and update <code>maxf = max(maxf, freq[x])</code>. Note that x is appended to every level 1..freq[x] over time, one per push, never removed from lower levels when it moves up.",
               "Pop: take <code>x = groups[maxf].pop()</code>, set <code>freq[x] -= 1</code>, and if <code>groups[maxf]</code> is empty then <code>maxf -= 1</code>. The top of the highest level is exactly the most frequent value; among ties it is the one that reached that frequency last, which is the one with the latest relevant push. The remaining copies of x stay in the lower level stacks in the correct order. Every operation is O(1), so the whole run is O(n). This is bucketing by frequency, with a stack inside each bucket."],
    time="O(n)", space="O(n)",
    solution='''def frequencyStackPops(ops):
    freq = {}
    groups = {}
    maxf = 0
    out = []
    for t, x in ops:
        if t == 1:
            f = freq.get(x, 0) + 1
            freq[x] = f
            groups.setdefault(f, []).append(x)
            if f > maxf:
                maxf = f
        else:
            x = groups[maxf].pop()
            freq[x] -= 1
            if not groups[maxf]:
                maxf -= 1
            out.append(x)
    return out
''',
    tests=[[[[1, 5], [1, 7], [1, 5], [1, 7], [1, 4], [1, 5], [0, 0], [0, 0], [0, 0], [0, 0]]],
           [[[1, 3], [0, 0]]], [[[1, 1], [1, 2], [1, 3], [0, 0], [0, 0], [0, 0]]],
           [[[1, 2], [1, 2], [1, 2], [0, 0], [0, 0], [0, 0]]],
           [[[1, 1], [1, 2], [1, 1], [0, 0], [1, 2], [1, 2], [0, 0], [0, 0], [0, 0]]],
           [[[1, -4], [1, 9], [0, 0], [1, -4], [1, 9], [0, 0], [0, 0], [0, 0]]],
           [[[1, 6], [1, 6], [1, 8], [1, 8], [0, 0], [0, 0], [1, 6], [0, 0], [0, 0], [0, 0]]],
           [[[1, 1], [1, 2], [1, 3], [1, 1], [1, 2], [1, 3], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0]]],
           [[[1, 10 ** 9], [1, -10 ** 9], [1, 10 ** 9], [0, 0], [0, 0], [0, 0]]],
           [[[1, 0], [0, 0], [1, 0], [0, 0]]]],
)


def _mk_ops(r, n, vals, pop_prob):
    ops, size = [], 0
    for _ in range(n):
        if size and r.random() < pop_prob:
            ops.append([0, 0])
            size -= 1
        else:
            ops.append([1, r.choice(vals)])
            size += 1
    return ops


_r = rnd(5011)
p["tests"].append([_mk_ops(_r, 4000, list(range(-5, 6)), 0.45)])
p["tests"].append([_mk_ops(_r, 4000, [_r.randint(-10 ** 9, 10 ** 9) for _ in range(300)], 0.4)])
p["tests"].append([[[1, i % 7] for i in range(2000)] + [[0, 0]] * 2000])


def b_freqstack(ops):
    st, out = [], []
    for t, x in ops:
        if t == 1:
            st.append(x)
        else:
            top = max(st.count(v) for v in set(st))
            for i in range(len(st) - 1, -1, -1):
                if st.count(st[i]) == top:
                    out.append(st.pop(i))
                    break
    return out


def g_freqstack(r):
    return [_mk_ops(r, r.randint(1, 16), [0, 1, 2, 3], 0.4)]


def v_freqstack(tests):
    for t in tests:
        ops = t["args"][0]
        assert 1 <= len(ops) <= 4000
        size = 0
        for typ, x in ops:
            assert typ in (0, 1)
            if typ == 1:
                assert -10 ** 9 <= x <= 10 ** 9
                size += 1
            else:
                assert x == 0 and size > 0
                size -= 1


CHECKS["frequency-stack-pops"] = (b_freqstack, g_freqstack, "exact")
VALIDATE["frequency-stack-pops"] = v_freqstack
