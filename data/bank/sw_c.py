"""Problems: sliding window, minimum-size windows. See data/lib.py for the registry."""
from lib import add, rnd, CHECKS, VALIDATE, gen_arr  # noqa: F401

TOPIC = "Sliding Window"


# ---------------------------------------------------------------- EASY

p = add(
    id="min-consecutive-cards-pickup", title="Minimum Consecutive Cards to Pick Up", diff="Easy", topic=TOPIC, tier="common",
    fn="minCardsToPair", params=[("cards", "int[]")], ret="int", cmp="exact",
    desc="<p>Cards lie in a row, and <code>cards[i]</code> is the number printed on the i-th card. You want to pick up a block of <em>consecutive</em> cards that contains two cards with the same number.</p><p>Return the smallest number of cards in such a block, or <code>-1</code> if no two cards share a number.</p><pre>cards = [3, 4, 2, 3, 4, 7]\nblock [3, 4, 2, 3] has two 3s and holds 4 cards\nresult = 4</pre>",
    constraints=["1 &le; cards.length &le; 10,000", "0 &le; cards[i] &le; 1,000,000"],
    hints=["A block contains a repeated number exactly when it contains two equal cards. Which pair of equal cards makes the block as short as possible?",
           "For one number, only <em>neighbouring</em> occurrences matter: a block through two occurrences with another occurrence between them could be shortened.",
           "Scan left to right and remember the last index where each number was seen. At index <code>i</code> with a previous index <code>j</code>, the block <code>[j, i]</code> has <code>i - j + 1</code> cards."],
    editorial=["The best block always starts and ends on two equal cards that are consecutive occurrences of the same number; any other block with a duplicate can be trimmed down to such a pair. So the answer is the smallest distance between two consecutive occurrences of the same value, plus one.",
               "Keep a hash map from value to the last index where it appeared. When the current card already has an entry, update the answer with <code>i - last + 1</code>, then store the new index. This is the same as a sliding window whose left edge jumps to the previous occurrence. One pass gives O(n) time and O(n) space. Checking every block directly would be O(n<sup>2</sup>) or worse."],
    time="O(n)", space="O(n)",
    solution='''def minCardsToPair(cards):
    last = {}
    best = -1
    for i, x in enumerate(cards):
        if x in last:
            length = i - last[x] + 1
            if best < 0 or length < best:
                best = length
        last[x] = i
    return best
''',
    tests=[[[3, 4, 2, 3, 4, 7]], [[1, 0, 5, 3]], [[7]], [[5, 5]], [[1, 2, 1, 2, 1]], [[9, 8, 7, 9, 8, 7]],
           [[0, 1, 2, 3, 4, 0]], [[1000000, 1, 1000000]], [[4, 4, 4, 4]], [[2, 3, 4, 5, 6, 7, 8, 9, 3]]],
)
_r = rnd(7301)
_a = list(range(1, 4001)); _r.shuffle(_a)
p["tests"].append([_a])
p["tests"].append([[i % 3000 for i in range(4000)]])
_a = list(range(4000)); _r.shuffle(_a); _a[3500] = _a[100]
p["tests"].append([_a])


def b_cards(cards):
    n = len(cards)
    for size in range(2, n + 1):
        for i in range(n - size + 1):
            blk = cards[i:i + size]
            if len(set(blk)) < len(blk):
                return size
    return -1


def v_cards(tests):
    for t in tests:
        a = t["args"][0]
        assert 1 <= len(a) <= 10000
        assert all(0 <= x <= 1000000 for x in a)


CHECKS["min-consecutive-cards-pickup"] = (b_cards, lambda r: [gen_arr(r, 0, 7, 1, 12)], "exact")
VALIDATE["min-consecutive-cards-pickup"] = v_cards


p = add(
    id="shortest-subarray-covering-all-values", title="Shortest Subarray Containing Every Distinct Value", diff="Easy", topic=TOPIC, tier="common",
    fn="shortestCoverAll", params=[("nums", "int[]")], ret="int", cmp="exact",
    desc="<p>Let <code>D</code> be the set of different values that occur in <code>nums</code>. Return the length of the shortest contiguous subarray of <code>nums</code> that contains <em>every</em> value of <code>D</code> at least once.</p><pre>nums = [2, 1, 2, 3, 1, 2, 2]\nD = {1, 2, 3}\nthe subarray [2, 3, 1] covers D\nresult = 3</pre><p>The whole array always qualifies, so an answer exists.</p>",
    constraints=["1 &le; nums.length &le; 10,000", "-1,000,000 &le; nums[i] &le; 1,000,000"],
    hints=["First compute how many different values there are. Then the question is: how short can a window be and still contain that many different values?",
           "Grow the window to the right until it covers all values. Once it does, extending further can only make it longer, so try to shrink it from the left.",
           "Keep a count per value and a counter of how many values currently have count above zero. While the counter equals the total, record the length and drop the leftmost element."],
    editorial=["Two pointers work because coverage is monotone: if a window covers every value, any larger window containing it does too. For each right end, the best left end is the largest one that still covers everything, and that left end never moves backwards as the right end advances.",
               "Maintain a map of counts and the number of values with a non-zero count. Move <code>right</code> one step at a time. While the number of covered values equals <code>|D|</code>, record <code>right - left + 1</code>, remove <code>nums[left]</code> and advance <code>left</code>. Every index enters and leaves the window once, so the time is O(n) with O(|D|) extra memory."],
    time="O(n)", space="O(n)",
    solution='''def shortestCoverAll(nums):
    need = len(set(nums))
    cnt = {}
    have = 0
    left = 0
    best = len(nums)
    for right, x in enumerate(nums):
        cnt[x] = cnt.get(x, 0) + 1
        if cnt[x] == 1:
            have += 1
        while have == need:
            best = min(best, right - left + 1)
            y = nums[left]
            cnt[y] -= 1
            if cnt[y] == 0:
                have -= 1
            left += 1
    return best
''',
    tests=[[[2, 1, 2, 3, 1, 2, 2]], [[1, 2, 3]], [[5]], [[7, 7, 7, 7]], [[1, 2, 1, 2, 1, 2]], [[1, 1, 2, 1, 1, 3, 1, 1]],
           [[3, 1, 3, 1, 2, 2, 3]], [[-5, 4, -5, 4, 0, 4, -5]], [[1, 2, 3, 2, 1]], [[9, 8, 9, 8, 9, 8, 7]]],
)
_r = rnd(7302)
p["tests"].append([[_r.randint(1, 50) for _ in range(5000)]])
_a = list(range(-2500, 2500)); _r.shuffle(_a)
p["tests"].append([_a])
_a = [_r.randint(1, 3) for _ in range(6000)]; _a[0] = 4; _a[-1] = 5
p["tests"].append([_a])


def b_cover(nums):
    d = len(set(nums))
    n = len(nums)
    for size in range(1, n + 1):
        for i in range(n - size + 1):
            if len(set(nums[i:i + size])) == d:
                return size


def v_cover(tests):
    for t in tests:
        a = t["args"][0]
        assert 1 <= len(a) <= 10000
        assert all(-1000000 <= x <= 1000000 for x in a)


CHECKS["shortest-subarray-covering-all-values"] = (b_cover, lambda r: [gen_arr(r, 1, 4, 1, 12)], "exact")
VALIDATE["shortest-subarray-covering-all-values"] = v_cover


p = add(
    id="shortest-substring-exactly-k-ones", title="Shortest Binary Substring With Exactly K Ones", diff="Easy", topic=TOPIC, tier="extra",
    fn="shortestWithKOnes", params=[("s", "string"), ("k", "int")], ret="int", cmp="exact",
    desc="<p>The string <code>s</code> consists only of the characters <code>0</code> and <code>1</code>. Find the shortest substring (contiguous) that contains <em>exactly</em> <code>k</code> characters equal to <code>1</code> and return its length. Return <code>-1</code> if <code>s</code> has fewer than <code>k</code> ones.</p><pre>s = \"1001010\", k = 2\nsubstring \"101\" (indices 3..5) has two ones\nresult = 3</pre>",
    constraints=["1 &le; s.length &le; 10,000", "s contains only the characters 0 and 1", "1 &le; k &le; 10,000"],
    hints=["A substring with exactly k ones that is as short as possible never begins or ends with a 0. Why not?",
           "So the substring starts at one particular 1 and ends at another 1 exactly k - 1 ones later.",
           "Collect the positions of all ones in a list <code>pos</code>. The candidate lengths are <code>pos[i + k - 1] - pos[i] + 1</code>. Equivalently, slide a window that holds k ones and trim its zero ends."],
    editorial=["If a substring with exactly k ones starts or ends with a zero, dropping that zero keeps the number of ones and shortens the substring. So an optimal substring starts at a 1 and ends at a 1, and it contains the ones numbered i through i + k - 1 in order.",
               "Record the index of every 1. For each i with <code>i + k - 1</code> inside the list, the length is <code>pos[i + k - 1] - pos[i] + 1</code>; the answer is the minimum, or -1 when there are fewer than k ones. This is a fixed-size window over the list of ones, taking O(n) time and O(n) space (a two-pointer version with a counter needs only O(1) extra space)."],
    time="O(n)", space="O(n)",
    solution='''def shortestWithKOnes(s, k):
    pos = [i for i, ch in enumerate(s) if ch == '1']
    if len(pos) < k:
        return -1
    best = len(s)
    for i in range(len(pos) - k + 1):
        best = min(best, pos[i + k - 1] - pos[i] + 1)
    return best
''',
    tests=[["1001010", 2], ["1001010", 1], ["1001010", 3], ["1001010", 4], ["0", 1], ["1", 1], ["0000", 1], ["11111", 3],
           ["1000001", 2], ["0110", 2], ["10101010101", 4], ["1110111", 5]],
)
_r = rnd(7303)
p["tests"].append(["".join(_r.choice("01") for _ in range(6000)), 1000])
p["tests"].append(["".join("1" if _r.random() < 0.05 else "0" for _ in range(6000)), 150])
p["tests"].append(["".join("1" if _r.random() < 0.2 else "0" for _ in range(6000)), 1300])


def b_kones(s, k):
    best = -1
    n = len(s)
    for i in range(n):
        for j in range(i + 1, n + 1):
            if s[i:j].count("1") == k and (best < 0 or j - i < best):
                best = j - i
    return best


def g_kones(r):
    return ["".join(r.choice("0011") for _ in range(r.randint(1, 12))), r.randint(1, 5)]


def v_kones(tests):
    for t in tests:
        s, k = t["args"]
        assert 1 <= len(s) <= 10000 and set(s) <= {"0", "1"}
        assert 1 <= k <= 10000


CHECKS["shortest-substring-exactly-k-ones"] = (b_kones, g_kones, "exact")
VALIDATE["shortest-substring-exactly-k-ones"] = v_kones


# ---------------------------------------------------------------- MEDIUM

p = add(
    id="shortest-subarray-at-least-k-distinct", title="Shortest Subarray With at Least K Distinct Values", diff="Medium", topic=TOPIC, tier="common",
    fn="shortestWithKDistinct", params=[("nums", "int[]"), ("k", "int")], ret="int", cmp="exact",
    desc="<p>Given an integer array <code>nums</code> and an integer <code>k</code>, return the length of the shortest contiguous subarray that contains at least <code>k</code> <em>different</em> values. If no subarray has that many different values, return <code>-1</code>.</p><pre>nums = [1, 2, 1, 2, 3, 3], k = 3\n[1, 2, 3] (indices 2..4) has three different values\nresult = 3</pre>",
    constraints=["1 &le; nums.length &le; 10,000", "1 &le; k &le; 10,000", "-1,000,000 &le; nums[i] &le; 1,000,000"],
    hints=["If the whole array has fewer than k different values the answer is -1. Otherwise some window works, and you want the shortest one.",
           "For a fixed right end, extending the window to the left never loses distinct values. So the set of valid left ends for that right end is a prefix, and the best one is its largest member.",
           "Expand the right end, counting each value. While the window has at least k different values, record its length and shrink from the left, decrementing counts and the distinct counter when a count hits zero."],
    editorial=["The property 'at least k different values' is monotone in both directions: a bigger window that contains a valid window is valid, and a smaller window inside an invalid window is invalid. That is exactly what a two-pointer sweep needs.",
               "Move <code>right</code> over the array and update a count map and the number of different values in the window. As long as that number is at least k, update the answer with <code>right - left + 1</code>, then remove <code>nums[left]</code> and advance <code>left</code>. Every element is added and removed at most once, so the time is O(n) and the map uses O(n) space. If the answer never updates, return -1."],
    time="O(n)", space="O(n)",
    solution='''def shortestWithKDistinct(nums, k):
    cnt = {}
    distinct = 0
    left = 0
    best = -1
    for right, x in enumerate(nums):
        cnt[x] = cnt.get(x, 0) + 1
        if cnt[x] == 1:
            distinct += 1
        while distinct >= k:
            length = right - left + 1
            if best < 0 or length < best:
                best = length
            y = nums[left]
            cnt[y] -= 1
            if cnt[y] == 0:
                distinct -= 1
            left += 1
    return best
''',
    tests=[[[1, 2, 1, 2, 3, 3], 3], [[1, 2, 1, 2, 3, 3], 1], [[1, 2, 1, 2, 3, 3], 2], [[1, 2, 1, 2, 3, 3], 4], [[5], 1], [[5], 2],
           [[4, 4, 4, 4], 2], [[1, 2, 3, 4, 5], 5], [[1, 1, 2, 2, 3, 3, 1, 4], 4], [[7, 8, 7, 9, 7, 8, 7, 9], 3],
           [[-1, 2, -1, 3, 2, 3], 3]],
)
_r = rnd(7304)
p["tests"].append([[_r.randint(1, 1000) for _ in range(6000)], 500])
p["tests"].append([[_r.randint(1, 60) for _ in range(6000)], 60])
p["tests"].append([[_r.randint(-1000000, 1000000) for _ in range(6000)], 3000])


def b_kdistinct(nums, k):
    n = len(nums)
    for size in range(1, n + 1):
        for i in range(n - size + 1):
            if len(set(nums[i:i + size])) >= k:
                return size
    return -1


def g_kdistinct(r):
    return [gen_arr(r, 1, 5, 1, 12), r.randint(1, 6)]


def v_kdistinct(tests):
    for t in tests:
        a, k = t["args"]
        assert 1 <= len(a) <= 10000 and 1 <= k <= 10000
        assert all(-1000000 <= x <= 1000000 for x in a)


CHECKS["shortest-subarray-at-least-k-distinct"] = (b_kdistinct, g_kdistinct, "exact")
VALIDATE["shortest-subarray-at-least-k-distinct"] = v_kdistinct


p = add(
    id="shortest-subarray-or-at-least-k", title="Shortest Subarray With Bitwise OR at Least K", diff="Medium", topic=TOPIC, tier="common",
    fn="shortestSubarrayOr", params=[("nums", "int[]"), ("k", "int")], ret="int", cmp="exact",
    desc="<p>The bitwise OR of a subarray is the OR of all its elements (for a single element it is the element itself). Given an array <code>nums</code> of non-negative integers and a number <code>k</code>, return the length of the shortest <em>non-empty</em> subarray whose OR is greater than or equal to <code>k</code>, or <code>-1</code> if there is none.</p><pre>nums = [2, 1, 8], k = 10\n[2, 1] -> 3, [1, 8] -> 9, [2, 1, 8] -> 11\nresult = 3</pre>",
    constraints=["1 &le; nums.length &le; 5,000", "0 &le; nums[i] &lt; 2<sup>30</sup>", "0 &le; k &lt; 2<sup>30</sup>"],
    hints=["Adding an element to a window can only turn bits on, so the OR of a window never decreases when the window grows. That makes two pointers possible.",
           "The difficulty is removing the left element: you cannot 'un-OR' a value. What extra information would let you know whether a bit is still set after a removal?",
           "Keep a counter for each of the 30 bit positions: how many elements of the window have that bit set. A bit is on in the window's OR exactly when its counter is positive."],
    editorial=["OR is monotone under extension, so for every right end the valid left ends form a prefix, and the best left end only moves right. A sliding window fits, but OR has no inverse operation. The fix is to store, for each bit, how many window elements contain it.",
               "Adding <code>x</code> increments the counter of every set bit of <code>x</code>; removing it decrements them. The window's OR is rebuilt from the counters (a bit is set when its counter is positive), and we update it incrementally as counters go from 0 to 1 or 1 to 0. For each right end, shrink while the OR is still at least k and record the length. Each element is added and removed once with 30 bit operations each: O(30 n) time and O(30) space. Note that <code>k = 0</code> is satisfied by any single element, so the answer is 1."],
    time="O(30 n)", space="O(1)",
    solution='''def shortestSubarrayOr(nums, k):
    cnt = [0] * 30
    cur = 0
    left = 0
    best = -1
    for right, x in enumerate(nums):
        for b in range(30):
            if (x >> b) & 1:
                cnt[b] += 1
                cur |= 1 << b
        while left <= right and cur >= k:
            length = right - left + 1
            if best < 0 or length < best:
                best = length
            y = nums[left]
            for b in range(30):
                if (y >> b) & 1:
                    cnt[b] -= 1
                    if cnt[b] == 0:
                        cur &= ~(1 << b)
            left += 1
    return best
''',
    tests=[[[2, 1, 8], 10], [[1, 2, 3], 2], [[1, 2, 3], 3], [[1, 2, 3], 0], [[0, 0, 0], 0], [[0, 0, 0], 1], [[5], 5], [[5], 6],
           [[1, 2, 4, 8, 16], 31], [[1, 2, 4, 8, 16], 30], [[8, 1, 1, 1, 2, 4], 15], [[1073741823], 1073741823]],
)
_r = rnd(7305)
p["tests"].append([[_r.randint(0, 255) for _ in range(5000)], 255])
p["tests"].append([[1 << _r.randint(0, 29) for _ in range(5000)], 1073741823])
p["tests"].append([[_r.randint(0, 1073741823) for _ in range(5000)], 1073741823])


def b_or(nums, k):
    n = len(nums)
    best = -1
    for i in range(n):
        acc = 0
        for j in range(i, n):
            acc |= nums[j]
            if acc >= k:
                if best < 0 or j - i + 1 < best:
                    best = j - i + 1
                break
    return best


def g_or(r):
    return [gen_arr(r, 0, 20, 1, 10), r.randint(0, 40)]


def v_or(tests):
    for t in tests:
        a, k = t["args"]
        assert 1 <= len(a) <= 5000
        assert all(0 <= x < 2 ** 30 for x in a) and 0 <= k < 2 ** 30


CHECKS["shortest-subarray-or-at-least-k"] = (b_or, g_or, "exact")
VALIDATE["shortest-subarray-or-at-least-k"] = v_or


p = add(
    id="shortest-subarray-sum-in-infinite-array", title="Shortest Subarray With Target Sum in an Infinite Array", diff="Medium", topic=TOPIC, tier="extra",
    fn="shortestInInfinite", params=[("nums", "int[]"), ("target", "int")], ret="int", cmp="exact",
    desc="<p>Build an infinite array by writing <code>nums</code> again and again: <code>nums, nums, nums, ...</code>. Find the shortest contiguous subarray of this infinite array whose sum is exactly <code>target</code> and return its length, or <code>-1</code> if no subarray has that sum.</p><pre>nums = [1, 1, 1, 2], target = 11\ninfinite array: 1 1 1 2 1 1 1 2 1 1 1 2 ...\n[2, 1, 1, 1, 2, 1, 1, 1, 2] sums to 11 and has 9 elements\nresult = 9</pre>",
    constraints=["1 &le; nums.length &le; 10,000", "1 &le; nums[i] &le; 100,000", "1 &le; target &le; 10<sup>9</sup>"],
    hints=["The target can be far larger than the sum of one copy of <code>nums</code>, so you cannot materialise the array. How many complete copies must the subarray swallow?",
           "All values are positive, so every n consecutive elements (n = nums.length) sum to <code>total = sum(nums)</code>. A subarray covering <code>target // total</code> full cycles uses exactly <code>(target // total) * n</code> elements for that part.",
           "What is left is a remainder <code>target % total</code> that is smaller than one full cycle. Find the shortest subarray with that sum in <code>nums + nums</code> using two pointers (all values positive), and add the two parts."],
    editorial=["Let <code>total</code> be the sum of one copy. Any n consecutive elements sum to exactly total, so a shortest subarray can be viewed as some whole cycles plus a piece shorter than one cycle. Because all numbers are positive, using as many whole cycles as possible, <code>q = target // total</code>, is optimal: each cycle costs n elements, and no shorter way to gain total exists (every element contributes at least 1 and any window of fewer than n elements has a sum below total).",
               "If the remainder <code>r = target % total</code> is 0, the answer is <code>q * n</code>. Otherwise search the shortest subarray of sum exactly r in <code>nums + nums</code> (a subarray shorter than n may wrap around the end). Because all values are positive, a two-pointer window finds it in O(n): grow right, shrink left while the sum exceeds r, and record the length on equality. If none exists the answer is -1; otherwise it is <code>q * n + best</code>. The result is at most target, so it fits in 32 bits."],
    time="O(n)", space="O(1)",
    solution='''def shortestInInfinite(nums, target):
    n = len(nums)
    total = sum(nums)
    base = (target // total) * n
    rem = target % total
    if rem == 0:
        return base
    best = -1
    left = 0
    cur = 0
    for right in range(2 * n):
        cur += nums[right % n]
        while cur > rem:
            cur -= nums[left % n]
            left += 1
        if cur == rem:
            length = right - left + 1
            if best < 0 or length < best:
                best = length
    return -1 if best < 0 else base + best
''',
    tests=[[[1, 1, 1, 2], 11], [[1, 2, 3], 5], [[1, 2, 3], 4], [[1, 2, 3], 6], [[1, 2, 3], 7], [[2, 4, 6], 5], [[2, 4, 6], 24],
           [[5], 5], [[5], 12], [[3, 1, 4, 1, 5], 17], [[1], 1000000000], [[7, 3], 10]],
)
_r = rnd(7306)
p["tests"].append([[_r.randint(1, 1000) for _ in range(5000)], 1000000000])
p["tests"].append([[_r.randint(1, 100000) for _ in range(5000)], 999999937])
p["tests"].append([[2 * _r.randint(1, 50000) for _ in range(5000)], 999999999])


def b_infinite(nums, target):
    big = nums * (target + 3)
    n = len(big)
    for size in range(1, target + 1):
        s = sum(big[:size])
        for i in range(0, n - size):
            if i > 0:
                s += big[i + size - 1] - big[i - 1]
            if s == target:
                return size
    return -1


def g_infinite(r):
    return [[r.randint(1, 6) for _ in range(r.randint(1, 5))], r.randint(1, 40)]


def v_infinite(tests):
    for t in tests:
        a, target = t["args"]
        assert 1 <= len(a) <= 10000 and all(1 <= x <= 100000 for x in a)
        assert 1 <= target <= 10 ** 9


CHECKS["shortest-subarray-sum-in-infinite-array"] = (b_infinite, g_infinite, "exact")
VALIDATE["shortest-subarray-sum-in-infinite-array"] = v_infinite


p = add(
    id="take-k-of-each-letter-from-ends", title="Take K of Each Letter From the Ends", diff="Medium", topic=TOPIC, tier="extra",
    fn="minMinutesTakeK", params=[("s", "string"), ("k", "int")], ret="int", cmp="exact",
    desc="<p>The string <code>s</code> contains only the letters <code>a</code>, <code>b</code> and <code>c</code>. In each minute you remove either the leftmost or the rightmost remaining character and keep it.</p><p>Return the minimum number of minutes needed to have collected at least <code>k</code> copies of <em>each</em> of the letters <code>a</code>, <code>b</code> and <code>c</code>, or <code>-1</code> if that is impossible.</p><pre>s = \"aabaaaacaabc\", k = 2\ntake 3 from the left (a, a, b) and 5 from the right (c, a, a, b, c)\nthat is 4 a, 2 b, 2 c, and no shorter combination works\nresult = 8</pre>",
    constraints=["1 &le; s.length &le; 10,000", "s contains only the letters a, b and c", "0 &le; k &le; s.length"],
    hints=["Whatever you take is a prefix plus a suffix of the string. What is left behind?",
           "What remains is one contiguous middle part. Taking as little as possible means leaving as much as possible in the middle.",
           "The middle part may contain at most <code>total[c] - k</code> copies of each letter c (otherwise you did not take enough). Find the longest such window with two pointers; the answer is <code>n - longest</code>."],
    editorial=["The characters you take form a prefix and a suffix, so the characters you do <em>not</em> take form one contiguous window. If the string has <code>total[c]</code> copies of letter c and you need k of them, the untouched window can hold at most <code>total[c] - k</code> copies. If some total is below k the answer is -1.",
               "Minimising the minutes means maximising the window. The condition 'every letter count is within its limit' stays true when the window shrinks, so a two-pointer sweep applies: extend <code>right</code>, and while some count exceeds its limit move <code>left</code> forward. Track the largest window size and return <code>n - best</code>. This is O(n) time and O(1) space. (Window lengths include the empty window, which corresponds to taking every character.)"],
    time="O(n)", space="O(1)",
    solution='''def minMinutesTakeK(s, k):
    n = len(s)
    total = {'a': 0, 'b': 0, 'c': 0}
    for ch in s:
        total[ch] += 1
    if min(total.values()) < k:
        return -1
    limit = {ch: total[ch] - k for ch in total}
    cnt = {'a': 0, 'b': 0, 'c': 0}
    left = 0
    best = 0
    for right, ch in enumerate(s):
        cnt[ch] += 1
        while cnt[ch] > limit[ch]:
            cnt[s[left]] -= 1
            left += 1
        best = max(best, right - left + 1)
    return n - best
''',
    tests=[["aabaaaacaabc", 2], ["abc", 1], ["abc", 2], ["abc", 0], ["a", 0], ["a", 1], ["aaabbbccc", 3], ["cbacbacba", 2],
           ["aaaaabbbbbccccc", 2], ["abcabcabc", 3], ["bbbaaaccc", 1], ["acbbbbbbbbbca", 1]],
)
_r = rnd(7307)
p["tests"].append(["".join(_r.choice("abc") for _ in range(6000)), 1500])
p["tests"].append(["".join(_r.choice("abc") for _ in range(6000)), 1900])
p["tests"].append(["a" * 2000 + "".join(_r.choice("abc") for _ in range(2000)) + "c" * 2000, 300])


def b_take(s, k):
    n = len(s)
    best = -1
    for i in range(n + 1):
        for j in range(n - i + 1):
            taken = s[:i] + s[n - j:]
            if all(taken.count(c) >= k for c in "abc"):
                if best < 0 or i + j < best:
                    best = i + j
    return best


def g_take(r):
    return ["".join(r.choice("abc") for _ in range(r.randint(1, 10))), r.randint(0, 3)]


def v_take(tests):
    for t in tests:
        s, k = t["args"]
        assert 1 <= len(s) <= 10000 and set(s) <= set("abc")
        assert 0 <= k <= len(s)


CHECKS["take-k-of-each-letter-from-ends"] = (b_take, g_take, "exact")
VALIDATE["take-k-of-each-letter-from-ends"] = v_take


p = add(
    id="shortest-circular-arc-covering-all-colors", title="Shortest Circular Arc Covering All Colors", diff="Medium", topic=TOPIC, tier="extra",
    fn="shortestCircularCover", params=[("colors", "int[]")], ret="int", cmp="exact",
    desc="<p>Beads of various colors are strung on a closed necklace: <code>colors[i]</code> is the color of bead <code>i</code>, and bead <code>n - 1</code> is next to bead <code>0</code>. Pick a run of consecutive beads, which may wrap around the end of the array, so that the run contains <em>every</em> color that appears on the necklace.</p><p>Return the smallest possible number of beads in such a run.</p><pre>colors = [1, 2, 2, 1, 3, 3, 1]\ncolors present: 1, 2, 3\nbeads 2..4 = [2, 1, 3] contain all three colors, and no run of 2 beads does\nresult = 3</pre>",
    constraints=["1 &le; colors.length &le; 10,000", "0 &le; colors[i] &le; 1,000,000"],
    hints=["Without the wrap-around this is the classic 'shortest subarray containing all distinct values'. How could you reuse that solution?",
           "A run that wraps around the end of the array is a normal subarray of the array written twice (<code>colors + colors</code>).",
           "Slide a window over the doubled array with a count map and a counter of covered colors. Shrink from the left while everything is covered, tracking the minimum length. The best length is never more than n, so no window needs to be longer."],
    editorial=["Cutting the necklace open at a different place only changes where the array starts, so every circular run corresponds to a plain subarray of the doubled array <code>colors + colors</code> with length at most n. The task becomes: find the shortest window of the doubled array containing all D different colors.",
               "Use the usual two-pointer technique: add <code>arr[right]</code> to a count map, and while the number of colors with a positive count equals D record the window length and remove <code>arr[left]</code>. Any n consecutive beads cover every color, so the answer is at most n and starting the answer at n is safe. The doubled array has 2n elements, so the time is O(n) and the extra space O(n)."],
    time="O(n)", space="O(n)",
    solution='''def shortestCircularCover(colors):
    n = len(colors)
    need = len(set(colors))
    arr = colors + colors
    cnt = {}
    have = 0
    left = 0
    best = n
    for right in range(2 * n):
        x = arr[right]
        cnt[x] = cnt.get(x, 0) + 1
        if cnt[x] == 1:
            have += 1
        while have == need:
            best = min(best, right - left + 1)
            y = arr[left]
            cnt[y] -= 1
            if cnt[y] == 0:
                have -= 1
            left += 1
    return best
''',
    tests=[[[1, 2, 2, 1, 3, 3, 1]], [[1]], [[4, 4, 4]], [[1, 2]], [[1, 2, 3, 1, 1, 1, 1]], [[2, 1, 1, 1, 1, 3]],
           [[1, 1, 2, 2, 3, 3]], [[3, 1, 1, 2, 2, 2, 2, 2]], [[1, 2, 1, 2, 1, 2, 3]], [[5, 6, 7, 8, 5, 6, 7, 8]],
           [[9, 0, 0, 0, 0, 0, 0, 8]]],
)
_r = rnd(7308)
p["tests"].append([[_r.randint(1, 40) for _ in range(6000)]])
_a = [1] * 3000 + [2] + [1] * 2995 + [3] * 1 + [1] * 3
p["tests"].append([_a])
p["tests"].append([[_r.randint(0, 1000000) for _ in range(3000)]])


def b_circ(colors):
    n = len(colors)
    d = len(set(colors))
    for size in range(1, n + 1):
        for i in range(n):
            if len({colors[(i + t) % n] for t in range(size)}) == d:
                return size


def v_circ(tests):
    for t in tests:
        a = t["args"][0]
        assert 1 <= len(a) <= 10000
        assert all(0 <= x <= 1000000 for x in a)


CHECKS["shortest-circular-arc-covering-all-colors"] = (b_circ, lambda r: [gen_arr(r, 1, 4, 1, 10)], "exact")
VALIDATE["shortest-circular-arc-covering-all-colors"] = v_circ


p = add(
    id="two-disjoint-subarrays-with-target-sum", title="Two Non-Overlapping Subarrays With Target Sum", diff="Medium", topic=TOPIC, tier="extra",
    fn="minTwoDisjointLength", params=[("nums", "int[]"), ("target", "int")], ret="int", cmp="exact",
    desc="<p>Given an array <code>nums</code> of positive integers and an integer <code>target</code>, choose two subarrays that do not share any index and whose sums are both exactly <code>target</code>. Return the smallest possible value of the <em>sum of their lengths</em>, or <code>-1</code> if two such subarrays do not exist.</p><pre>nums = [1, 2, 1, 3, 4, 2], target = 3\n[3] and [1, 2] (indices 3 and 0..1) have sum 3 each\nresult = 3</pre>",
    constraints=["1 &le; nums.length &le; 10,000", "1 &le; nums[i] &le; 1,000", "1 &le; target &le; 10<sup>6</sup>"],
    hints=["Because all values are positive, for every right end there is at most one left end that gives sum exactly <code>target</code>, and two pointers find all such subarrays in O(n).",
           "Two chosen subarrays do not overlap, so one of them ends before the other starts. When you meet a subarray <code>[l, r]</code>, you want the shortest valid subarray that ends before <code>l</code>.",
           "Keep an array <code>best[i]</code> = length of the shortest target-sum subarray that ends at index i or earlier. At each match <code>[l, r]</code> combine <code>best[l - 1] + (r - l + 1)</code>."],
    editorial=["With positive numbers the sum of a window grows when it extends right and shrinks when it moves left, so a two-pointer sweep lists every subarray with sum exactly target in O(n). For each right end there is at most one such subarray.",
               "Sweep right to left in index order and maintain <code>best[i]</code>, the shortest valid subarray lying entirely inside <code>nums[0..i]</code>; it equals <code>best[i - 1]</code> unless a valid subarray ends at i and is shorter. When a valid subarray <code>[l, r]</code> is found, any partner must lie in <code>nums[0..l-1]</code>, so candidate total is <code>best[l - 1] + (r - l + 1)</code>. Every pair of disjoint subarrays is considered exactly once with its later subarray as <code>[l, r]</code>. Time O(n), space O(n)."],
    time="O(n)", space="O(n)",
    solution='''def minTwoDisjointLength(nums, target):
    n = len(nums)
    INF = 10 ** 9
    best = [INF] * n
    ans = INF
    left = 0
    cur = 0
    for right in range(n):
        cur += nums[right]
        while cur > target:
            cur -= nums[left]
            left += 1
        best[right] = best[right - 1] if right > 0 else INF
        if cur == target:
            length = right - left + 1
            if left > 0 and best[left - 1] < INF:
                ans = min(ans, best[left - 1] + length)
            best[right] = min(best[right], length)
    return -1 if ans >= INF else ans
''',
    tests=[[[1, 2, 1, 3, 4, 2], 3], [[3, 2, 2, 4, 3], 3], [[7, 3, 4, 7], 7], [[4, 3, 2, 6, 2, 3, 4], 6], [[5, 5, 5], 5], [[5, 5], 5],
           [[5], 5], [[1, 1, 1, 1], 2], [[1, 1, 1, 1], 3], [[2, 2, 2, 2, 2], 4], [[6, 1, 1, 1, 1, 1, 1, 6], 6], [[1, 2, 3], 7]],
)
_r = rnd(7309)
p["tests"].append([[_r.randint(1, 5) for _ in range(6000)], 7])
p["tests"].append([[_r.randint(1, 1000) for _ in range(6000)], 100000])
p["tests"].append([[_r.randint(1, 3) for _ in range(6000)], 3000])


def b_two(nums, target):
    n = len(nums)
    subs = []
    for i in range(n):
        s = 0
        for j in range(i, n):
            s += nums[j]
            if s == target:
                subs.append((i, j))
    best = -1
    for a in range(len(subs)):
        for b in range(len(subs)):
            if subs[a][1] < subs[b][0]:
                tot = (subs[a][1] - subs[a][0] + 1) + (subs[b][1] - subs[b][0] + 1)
                if best < 0 or tot < best:
                    best = tot
    return best


def g_two(r):
    return [[r.randint(1, 4) for _ in range(r.randint(1, 12))], r.randint(1, 7)]


def v_two(tests):
    for t in tests:
        a, target = t["args"]
        assert 1 <= len(a) <= 10000 and all(1 <= x <= 1000 for x in a)
        assert 1 <= target <= 10 ** 6


CHECKS["two-disjoint-subarrays-with-target-sum"] = (b_two, g_two, "exact")
VALIDATE["two-disjoint-subarrays-with-target-sum"] = v_two


# ---------------------------------------------------------------- HARD

p = add(
    id="min-window-with-wildcards", title="Minimum Window With Wildcards", diff="Hard", topic=TOPIC, tier="extra",
    fn="minWindowWildcards", params=[("s", "string"), ("t", "string")], ret="int", cmp="exact",
    desc="<p>The string <code>s</code> consists of lowercase letters and the wildcard character <code>?</code>. A <code>?</code> may be treated as any lowercase letter you like (each <code>?</code> independently).</p><p>A substring of <code>s</code> is <em>good</em> if, after choosing letters for its wildcards, it contains every character of <code>t</code> with multiplicity, that is, each letter appears in the substring at least as many times as it appears in <code>t</code>. Return the length of the shortest good substring, or <code>-1</code> if none exists.</p><pre>s = \"ab?ca\", t = \"abc\"\nthe substring \"ab?\" works with ? = c, and no 2-character substring has three letters\nresult = 3</pre>",
    constraints=["1 &le; t.length &le; s.length &le; 10,000", "s contains lowercase letters and ?; t contains only lowercase letters"],
    hints=["Without wildcards this is Minimum Window Substring. First think about what condition makes a window good: how many letters of t does the window still lack?",
           "Define the <em>deficit</em> of a window as the sum over letters of <code>max(0, need[c] - count[c])</code>. The window is good exactly when its deficit is at most the number of wildcards in it.",
           "Deficit never rises and the wildcard count never falls when the window grows, so goodness is monotone. Slide two pointers and update the deficit in O(1): adding a letter whose count is still below its need lowers the deficit by one; removing a letter whose count then drops below its need raises it by one."],
    editorial=["A window can be completed with its wildcards precisely when the number of missing letters (the deficit) does not exceed the number of wildcards in it, because each wildcard can fill one missing letter and the letters that are already present need no help. If a window is good, every larger window around it is good as well, which is the structure two pointers need.",
               "Keep <code>cnt[c]</code> for letters in the window, <code>q</code> for wildcards, and <code>deficit</code> starting at <code>len(t)</code>. When a letter c enters and <code>cnt[c] &lt; need[c]</code> before the increment, the deficit decreases by one. While <code>deficit &lt;= q</code>, record the window length and remove the left character: for a letter, decrement its count and increase the deficit if the count is now below the need; for a wildcard decrement <code>q</code>. Every character enters and leaves once, so the time is O(n) with O(26) extra space. With no wildcards this is exactly the classic minimum window substring algorithm."],
    time="O(n)", space="O(1)",
    solution='''def minWindowWildcards(s, t):
    need = [0] * 26
    for ch in t:
        need[ord(ch) - 97] += 1
    cnt = [0] * 26
    deficit = len(t)
    q = 0
    left = 0
    best = -1
    for right, ch in enumerate(s):
        if ch == '?':
            q += 1
        else:
            c = ord(ch) - 97
            if cnt[c] < need[c]:
                deficit -= 1
            cnt[c] += 1
        while deficit <= q:
            length = right - left + 1
            if best < 0 or length < best:
                best = length
            out = s[left]
            if out == '?':
                q -= 1
            else:
                c = ord(out) - 97
                cnt[c] -= 1
                if cnt[c] < need[c]:
                    deficit += 1
            left += 1
    return best
''',
    tests=[["ab?ca", "abc"], ["abc", "abc"], ["a??", "abc"], ["???", "abc"], ["zz", "ab"], ["aabbcc", "abc"], ["xyz", "abc"],
           ["a", "a"], ["?", "z"], ["?a", "ab"], ["adobecodebanc", "abc"], ["a?b?c?a", "aabbcc"], ["zzzz?zzzz", "ab"],
           ["ab?b?ab", "aabb"]],
)
_r = rnd(7310)
p["tests"].append(["".join(_r.choice("abcdefghij?") for _ in range(6000)), "abcdefghijjjaa"])
p["tests"].append(["".join(_r.choice("abc") for _ in range(6000)), "aaabbbcccabc" * 5])
p["tests"].append(["".join(_r.choice("abcdefghijklmnopqrstuvwxyz???") for _ in range(6000)), "thequickbrownfoxjumps"])


def b_wild(s, t):
    need = {}
    for ch in t:
        need[ch] = need.get(ch, 0) + 1
    n = len(s)
    best = -1
    for i in range(n):
        for j in range(i + 1, n + 1):
            w = s[i:j]
            q = w.count("?")
            miss = sum(max(0, v - w.count(c)) for c, v in need.items())
            if miss <= q and (best < 0 or j - i < best):
                best = j - i
    return best


def g_wild(r):
    s = "".join(r.choice("abc?") for _ in range(r.randint(1, 12)))
    t = "".join(r.choice("abc") for _ in range(r.randint(1, 5)))
    return [s, t]


def v_wild(tests):
    for t in tests:
        s, pat = t["args"]
        assert 1 <= len(pat) <= len(s) <= 10000
        assert set(s) <= set("abcdefghijklmnopqrstuvwxyz?") and set(pat) <= set("abcdefghijklmnopqrstuvwxyz")


CHECKS["min-window-with-wildcards"] = (b_wild, g_wild, "exact")
VALIDATE["min-window-with-wildcards"] = v_wild


p = add(
    id="smallest-range-covering-k-lists", title="Smallest Range Covering One Number From Each List", diff="Hard", topic=TOPIC, tier="common",
    fn="smallestRange", params=[("lists", "int[][]")], ret="int[]", cmp="exact",
    desc="<p>You are given <code>k</code> lists of integers, each sorted in non-decreasing order. Find the smallest closed range <code>[lo, hi]</code> such that every list has at least one number inside it.</p><p>Range <code>[a, b]</code> is smaller than <code>[c, d]</code> if <code>b - a &lt; d - c</code>, or if the lengths are equal and <code>a &lt; c</code>. Return <code>[lo, hi]</code> for the smallest range.</p><pre>lists = [[4, 10, 15, 24, 26], [0, 9, 12, 20], [5, 18, 22, 30]]\n[20, 24] contains 24, 20 and 22, one number from each list\nresult = [20, 24]</pre>",
    constraints=["1 &le; k &le; 100 lists", "every list is non-empty and sorted in non-decreasing order", "total number of elements across all lists &le; 6,000", "-100,000 &le; value &le; 100,000"],
    hints=["Any valid range must contain one element from every list. The range is determined by its smallest and largest chosen element.",
           "Merge all numbers into one sorted sequence, each tagged with the list it came from. A range is then a window of this sequence, and the window is valid when it holds elements of all k lists.",
           "Slide a window over the merged sequence: expand the right end until every list is represented, then shrink from the left while it stays valid. The window's value span is <code>right.value - left.value</code>; keep the best span (earlier start on ties)."],
    editorial=["After sorting all (value, list index) pairs together, the smallest range covering every list is the value span of the shortest window of this sequence that contains all k list indices. This reduces the problem to the 'minimum window containing all colors' pattern, with spans measured in values instead of lengths.",
               "Keep a count per list and the number of lists with a non-zero count. Advance <code>right</code>; whenever all k lists are present, compare <code>value[right] - value[left]</code> with the best so far (strictly smaller wins, so the earliest window is kept on ties, which also gives the smaller <code>lo</code>), then remove <code>left</code> and advance it. With N total elements, sorting costs O(N log N) and the sweep O(N). A heap based k-way merge solves it in O(N log k) as well. Equal values across lists are harmless: a window that cuts between equal values yields the same range."],
    time="O(N log N)", space="O(N)",
    solution='''def smallestRange(lists):
    items = sorted((v, i) for i, row in enumerate(lists) for v in row)
    k = len(lists)
    cnt = [0] * k
    have = 0
    left = 0
    best = None
    for right in range(len(items)):
        v, i = items[right]
        if cnt[i] == 0:
            have += 1
        cnt[i] += 1
        while have == k:
            lo = items[left][0]
            if best is None or v - lo < best[1] - best[0]:
                best = [lo, v]
            j = items[left][1]
            cnt[j] -= 1
            if cnt[j] == 0:
                have -= 1
            left += 1
    return best
''',
    tests=[[[[4, 10, 15, 24, 26], [0, 9, 12, 20], [5, 18, 22, 30]]], [[[1, 2, 3], [1, 2, 3], [1, 2, 3]]], [[[7]]], [[[1, 5, 9]]], [[[1], [2], [3]]],
           [[[-5, -1], [0, 4]]], [[[1, 1, 1], [1, 1]]], [[[10, 20], [11, 12], [30]]], [[[1, 100], [50], [2, 99]]],
           [[[0, 10, 20], [5, 15, 25]]], [[[3, 3, 3], [4, 4], [3, 5]]], [[[-100000], [100000]]]],
)
_r = rnd(7311)
p["tests"].append([[sorted(_r.randint(-100000, 100000) for _ in range(150)) for _ in range(40)]])
p["tests"].append([[sorted(_r.randint(0, 2000) for _ in range(_r.randint(1, 120))) for _ in range(50)]])
p["tests"].append([[sorted(_r.randint(-100000, 100000) for _ in range(30)) for _ in range(100)]])


def b_range(lists):
    import bisect
    cands = sorted({v for row in lists for v in row})
    best = None
    for lo in cands:
        hi = lo
        ok = True
        for row in lists:
            idx = bisect.bisect_left(row, lo)
            if idx == len(row):
                ok = False
                break
            hi = max(hi, row[idx])
        if ok and (best is None or hi - lo < best[1] - best[0]):
            best = [lo, hi]
    return best


def g_range(r):
    return [[sorted(r.randint(-5, 9) for _ in range(r.randint(1, 4))) for _ in range(r.randint(1, 4))]]


def v_range(tests):
    for t in tests:
        lists = t["args"][0]
        assert 1 <= len(lists) <= 100
        assert sum(len(x) for x in lists) <= 6000
        for row in lists:
            assert len(row) >= 1 and all(row[i] <= row[i + 1] for i in range(len(row) - 1))
            assert all(-100000 <= v <= 100000 for v in row)


CHECKS["smallest-range-covering-k-lists"] = (b_range, g_range, "exact")
VALIDATE["smallest-range-covering-k-lists"] = v_range
