"""Problems: stack (monotonic stack: nearest greater / smaller, spans, visible people). See data/lib.py for the registry."""
from lib import add, rnd, CHECKS, VALIDATE, gen_arr  # noqa: F401

INT_MIN, INT_MAX = -(2 ** 31), 2 ** 31 - 1
TOPIC = "Stack"


# ---------------------------------------------------------------- EASY

p = add(
    id="previous-smaller-element-index", title="Previous Smaller Element", diff="Easy", topic=TOPIC,
    fn="previousSmaller", params=[("nums", "int[]")], ret="int[]", cmp="exact",
    desc="<p>For every position <code>i</code> of the integer array <code>nums</code>, find the <em>nearest</em> position <code>j &lt; i</code> to its left whose value is <strong>strictly smaller</strong> than <code>nums[i]</code>. Return an array <code>answer</code> where <code>answer[i]</code> is that index <code>j</code>, or <code>-1</code> if no element to the left of <code>i</code> is smaller.</p><p>Example: <code>nums = [4, 2, 5, 3, 1, 6]</code> gives <code>[-1, -1, 1, 1, -1, 4]</code>. For the value 3 at index 3, the nearest smaller value on its left is 2 at index 1.</p>",
    constraints=["1 &le; nums.length &le; 10,000", "-10<sup>9</sup> &le; nums[i] &le; 10<sup>9</sup>", "Equal values do not count as smaller"],
    hints=["Checking all earlier positions for every position is O(n<sup>2</sup>). Think about which earlier elements could ever be the answer for some later element.",
           "If an earlier element is larger than or equal to a newer element, the earlier one is never the nearest smaller value for anything to the right of the newer element.",
           "Scan left to right with a stack of indices. Pop while the top value is <code>&ge; nums[i]</code>; the new top (if any) is the answer; then push <code>i</code>."],
    editorial=["Keep a stack of candidate indices whose values strictly increase from bottom to top. When a new element <code>x</code> arrives, every candidate with a value <code>&ge; x</code> is useless from now on: <code>x</code> is closer to the future and not larger, so any later element that could use the old candidate can use <code>x</code> (or something even better) instead. Pop those candidates.",
               "After the pops, the top of the stack (if there is one) is the nearest index on the left with a strictly smaller value. Record it, then push <code>i</code>. Every index is pushed once and popped at most once, so the whole scan is O(n) time and O(n) space. This is the basic <em>monotonic stack</em> pattern that the rest of this topic builds on."],
    time="O(n)", space="O(n)",
    solution='''def previousSmaller(nums):
    answer = []
    stack = []  # indices; values strictly increase from bottom to top
    for i, x in enumerate(nums):
        while stack and nums[stack[-1]] >= x:
            stack.pop()
        answer.append(stack[-1] if stack else -1)
        stack.append(i)
    return answer
''',
    tests=[[[4, 2, 5, 3, 1, 6]], [[7]], [[3, 3, 3]], [[1, 2, 3, 4, 5]], [[5, 4, 3, 2, 1]], [[-5, -5, -6, 0]],
           [[10 ** 9, -10 ** 9, 10 ** 9, 0]], [[2, 1, 2, 1, 2]], [[10 ** 9, -10 ** 9, 10 ** 9, -10 ** 9]]],
)
_r = rnd(7101)
p["tests"].append([[_r.randint(-10 ** 9, 10 ** 9) for _ in range(3000)]])
p["tests"].append([[_r.randint(0, 20) for _ in range(3000)]])
p["tests"].append([list(range(3000, 0, -1))])


def b_prevsmaller(nums):
    out = []
    for i in range(len(nums)):
        j = i - 1
        while j >= 0 and nums[j] >= nums[i]:
            j -= 1
        out.append(j)
    return out


def v_prevsmaller(tests):
    for t in tests:
        nums = t["args"][0]
        assert 1 <= len(nums) <= 10000 and all(-10 ** 9 <= x <= 10 ** 9 for x in nums)


CHECKS["previous-smaller-element-index"] = (b_prevsmaller, lambda r: [gen_arr(r, -4, 4, 1, 12)], "exact")
VALIDATE["previous-smaller-element-index"] = v_prevsmaller

p = add(
    id="next-greater-for-queries", title="Next Greater Value for Queried Numbers", diff="Easy", topic=TOPIC,
    fn="nextGreaterForQueries", params=[("nums", "int[]"), ("queries", "int[]")], ret="int[]", cmp="exact",
    desc="<p>The array <code>nums</code> contains <strong>distinct</strong> integers. Every entry of <code>queries</code> is some value that occurs in <code>nums</code>.</p><p>For a query value <code>v</code> located at index <code>p</code> in <code>nums</code>, its <em>next greater value</em> is the first number to the right of position <code>p</code> that is larger than <code>v</code>. Return an array with one entry per query: its next greater value, or <code>-1</code> if no larger number exists to its right.</p><p>Example: <code>nums = [4, 1, 2, 7, 3, 5]</code>, <code>queries = [1, 4, 3, 5]</code> gives <code>[2, 7, 5, -1]</code>.</p>",
    constraints=["1 &le; nums.length &le; 5,000", "1 &le; queries.length &le; 5,000", "-10<sup>9</sup> &le; nums[i] &le; 10<sup>9</sup> and all values in nums are distinct", "Every query value occurs in nums (a query may repeat)"],
    hints=["For one query you can find its position and scan right. Doing that for every query is slow when there are many queries. Can you answer for <em>all</em> numbers of nums in one pass?",
           "A number that has not yet met a larger number to its right is still 'waiting'. When a larger number arrives it answers every waiting number smaller than it.",
           "Scan <code>nums</code> from left to right with a stack of waiting values. While the top is smaller than the current value, pop it and store the current value as its answer in a dictionary. Then answer queries by dictionary lookup (default -1)."],
    editorial=["Compute the next greater value of every element of <code>nums</code> once, then look the queries up. Use a stack of values that are still waiting for a greater number. The stack is non-increasing from bottom to top: when the current number <code>x</code> arrives, all waiting numbers smaller than <code>x</code> find their answer in <code>x</code>, because <code>x</code> is the first number to their right that beats them. Pop them and record <code>x</code> as their answer.",
               "Then push <code>x</code>. Values left on the stack at the end have no greater number to their right and keep the default <code>-1</code>. Because the values are distinct a dictionary keyed by value is safe. Total time is O(n + q) and extra space is O(n)."],
    time="O(n + q)", space="O(n)",
    solution='''def nextGreaterForQueries(nums, queries):
    answer = {}
    stack = []  # values still waiting for a greater value; non-increasing bottom to top
    for x in nums:
        while stack and stack[-1] < x:
            answer[stack.pop()] = x
        stack.append(x)
    return [answer.get(q, -1) for q in queries]
''',
    tests=[[[4, 1, 2, 7, 3, 5], [1, 4, 3, 5]], [[1], [1]], [[2, 1], [1, 2]], [[1, 2, 3, 4], [1, 2, 3, 4]], [[4, 3, 2, 1], [4, 3, 2, 1]],
           [[-3, 5, -10, 8], [-10, -3, 5, 8, -10]], [[-10 ** 9, 10 ** 9, 0], [0, -10 ** 9]], [[9, 7, 8, 6, 10], [7, 7, 6]]],
)
_r = rnd(7102)
for n, q in ((3000, 3000), (3000, 500)):
    _v = _r.sample(range(-10 ** 9, 10 ** 9), n)
    p["tests"].append([_v, [_r.choice(_v) for _ in range(q)]])


def b_ngq(nums, queries):
    out = []
    for q in queries:
        p0 = nums.index(q)
        ans = -1
        for y in nums[p0 + 1:]:
            if y > q:
                ans = y
                break
        out.append(ans)
    return out


def g_ngq(r):
    n = r.randint(1, 9)
    nums = r.sample(range(-12, 12), n)
    return [nums, [r.choice(nums) for _ in range(r.randint(1, 6))]]


def v_ngq(tests):
    for t in tests:
        nums, queries = t["args"]
        assert 1 <= len(nums) <= 5000 and 1 <= len(queries) <= 5000
        assert len(set(nums)) == len(nums) and set(queries) <= set(nums)
        assert all(-10 ** 9 <= x <= 10 ** 9 for x in nums)


CHECKS["next-greater-for-queries"] = (b_ngq, g_ngq, "exact")
VALIDATE["next-greater-for-queries"] = v_ngq

p = add(
    id="rooftops-with-sunset-view", title="Rooftops With a Sunset View", diff="Easy", topic=TOPIC,
    fn="sunsetRooftops", params=[("heights", "int[]")], ret="int[]", cmp="exact",
    desc="<p>Buildings stand in a row from west to east; <code>heights[i]</code> is the height of building <code>i</code>, and the sun sets in the <strong>east</strong>, to the right of the last building. A building has a sunset view if it is <strong>strictly taller</strong> than every building to its right (the last building always has one).</p><p>Return the indices of all buildings with a sunset view, in increasing order.</p><p>Example: <code>heights = [4, 2, 3, 1]</code> gives <code>[0, 2, 3]</code>: building 1 (height 2) is blocked by the taller building 2.</p>",
    constraints=["1 &le; heights.length &le; 10,000", "1 &le; heights[i] &le; 10<sup>9</sup>", "A building of equal height to one on its right is blocked"],
    hints=["Building <code>i</code> is blocked exactly when some building to its right is at least as tall.",
           "Think about it from the other direction: sweep from the sun side and remember the tallest height seen so far. Or sweep left to right and let a taller building knock out the buildings it blocks.",
           "Left to right with a stack of indices: while the top building is not taller than the new one, pop it (it is blocked); then push the new index. The stack at the end is the answer."],
    editorial=["Use a monotonic stack of indices whose heights are strictly decreasing from bottom to top. When building <code>i</code> arrives, every building on the stack with height <code>&le; heights[i]</code> now has a building at least as tall to its right, so it can never have a sunset view; pop it. Afterwards push <code>i</code>.",
               "A building that is never popped has no building at least as tall to its right, which is exactly the sunset-view condition. So the final stack, read bottom to top, is the answer already in increasing index order. Time is O(n) and space O(n). A right-to-left sweep that tracks the running maximum gives the same result in O(1) extra space, but the stack version shows the general pattern."],
    time="O(n)", space="O(n)",
    solution='''def sunsetRooftops(heights):
    stack = []  # indices with strictly decreasing heights
    for i, h in enumerate(heights):
        while stack and heights[stack[-1]] <= h:
            stack.pop()
        stack.append(i)
    return stack
''',
    tests=[[[4, 2, 3, 1]], [[5]], [[3, 3, 3]], [[1, 2, 3, 4]], [[4, 3, 2, 1]], [[2, 2, 1, 2, 1]], [[10 ** 9, 1, 10 ** 9, 1]], [[1, 5, 5, 3, 5, 2, 2]]],
)
_r = rnd(7103)
p["tests"].append([[_r.randint(1, 10 ** 9) for _ in range(3000)]])
p["tests"].append([[_r.randint(1, 50) for _ in range(3000)]])
p["tests"].append([list(range(3000, 0, -1))])


def b_sunset(heights):
    n = len(heights)
    return [i for i in range(n) if all(heights[j] < heights[i] for j in range(i + 1, n))]


def v_sunset(tests):
    for t in tests:
        h = t["args"][0]
        assert 1 <= len(h) <= 10000 and all(1 <= x <= 10 ** 9 for x in h)
        assert t["expected"] and t["expected"][-1] == len(h) - 1


CHECKS["rooftops-with-sunset-view"] = (b_sunset, lambda r: [[r.randint(1, 6) for _ in range(r.randint(1, 12))]], "exact")
VALIDATE["rooftops-with-sunset-view"] = v_sunset

# ---------------------------------------------------------------- MEDIUM

p = add(
    id="days-until-warmer", title="Days Until a Warmer Day", diff="Medium", topic=TOPIC, tier="must",
    fn="daysUntilWarmer", params=[("temps", "int[]")], ret="int[]", cmp="exact",
    desc="<p>The array <code>temps</code> holds the temperature forecast for consecutive days. For each day <code>i</code>, find how many days you must wait to see a <strong>strictly warmer</strong> temperature than <code>temps[i]</code>. In other words, return an array <code>answer</code> where <code>answer[i]</code> is the smallest <code>d &gt; 0</code> such that <code>temps[i + d] &gt; temps[i]</code>, or <code>0</code> if no such day exists.</p><p>Example: <code>temps = [73, 74, 75, 71, 69, 72, 76, 73]</code> gives <code>[1, 1, 4, 2, 1, 1, 0, 0]</code>.</p>",
    constraints=["1 &le; temps.length &le; 10,000", "-50 &le; temps[i] &le; 100"],
    hints=["Scanning forward from every day is O(n<sup>2</sup>) in the worst case, for example for a steadily cooling forecast.",
           "A day that has not yet found a warmer day is waiting. A new, warmer day settles all waiting days that are colder than it, and those days are the most recent waiting ones.",
           "Keep a stack of waiting day indices, with temperatures non-increasing from bottom to top. For day <code>i</code>, pop every index <code>j</code> with <code>temps[j] &lt; temps[i]</code> and set <code>answer[j] = i - j</code>; then push <code>i</code>."],
    editorial=["This is the <em>next greater element</em> problem, asking for the distance instead of the value. Maintain a stack of indices of days that are still waiting for a warmer day. Temperatures on the stack never increase going up, because a warmer incoming day would have popped the colder ones.",
               "When day <code>i</code> comes in, pop all indices <code>j</code> on top whose temperature is strictly lower than <code>temps[i]</code>; day <code>i</code> is the first warmer day for each of them (any earlier warmer day would already have popped them), so <code>answer[j] = i - j</code>. Push <code>i</code>. Days left on the stack at the end keep the answer 0. Each day is pushed and popped at most once: O(n) time, O(n) space."],
    time="O(n)", space="O(n)",
    solution='''def daysUntilWarmer(temps):
    n = len(temps)
    answer = [0] * n
    stack = []  # indices of days waiting for a warmer day
    for i, t in enumerate(temps):
        while stack and temps[stack[-1]] < t:
            j = stack.pop()
            answer[j] = i - j
        stack.append(i)
    return answer
''',
    tests=[[[73, 74, 75, 71, 69, 72, 76, 73]], [[30, 40, 50, 60]], [[60]], [[30, 60, 90]], [[60, 50, 40, 30]], [[5, 5, 5, 5]],
           [[-50, 60, -50, 60]], [[10, 9, 8, 11, 7, 12]], [[0, 1, 0, 1, 0, 1]]],
)
_r = rnd(7104)
p["tests"].append([[_r.randint(-50, 60) for _ in range(5000)]])
p["tests"].append([list(range(60, -51, -1)) * 40 + [61 - 1]])
p["tests"].append([[_r.randint(20, 25) for _ in range(5000)]])


def b_warmer(temps):
    n = len(temps)
    out = []
    for i in range(n):
        d = 0
        for j in range(i + 1, n):
            if temps[j] > temps[i]:
                d = j - i
                break
        out.append(d)
    return out


def v_warmer(tests):
    for t in tests:
        a = t["args"][0]
        assert 1 <= len(a) <= 10000 and all(-50 <= x <= 100 for x in a)


CHECKS["days-until-warmer"] = (b_warmer, lambda r: [gen_arr(r, -5, 5, 1, 12)], "exact")
VALIDATE["days-until-warmer"] = v_warmer

p = add(
    id="stock-price-span-per-day", title="Stock Price Span Per Day", diff="Medium", topic=TOPIC,
    fn="stockSpans", params=[("prices", "int[]")], ret="int[]", cmp="exact",
    desc="<p>You are given the daily closing prices of a stock. The <em>span</em> of day <code>i</code> is the number of consecutive days ending at day <code>i</code> (including day <code>i</code> itself) for which the price was <strong>less than or equal to</strong> <code>prices[i]</code>. Equivalently, it is the distance back to the nearest earlier day with a strictly higher price (or to the start of the array if there is none).</p><p>Return the array of spans, one value per day.</p><p>Example: <code>prices = [100, 80, 60, 70, 60, 75, 85]</code> gives <code>[1, 1, 1, 2, 1, 4, 6]</code>. On the last day the price 85 beats the five previous prices 75, 60, 70, 60, 80, but not 100.</p>",
    constraints=["1 &le; prices.length &le; 10,000", "1 &le; prices[i] &le; 100,000"],
    hints=["Walking back from every day until you hit a higher price is O(n<sup>2</sup>) for increasing prices.",
           "The span of day <code>i</code> only depends on the nearest earlier day with a strictly higher price. Days with lower prices in between are 'hidden' behind day <code>i</code> for all later days too.",
           "Keep a stack of indices with strictly decreasing prices. Pop while <code>prices[top] &le; prices[i]</code>; then the span is <code>i - top</code> (or <code>i + 1</code> if the stack is empty). Push <code>i</code>."],
    editorial=["The span is the distance to the <em>previous greater element</em>. Process days left to right and keep a stack of day indices whose prices are strictly decreasing. For the new day <code>i</code>, all days on top with price <code>&le; prices[i]</code> are absorbed into its span, so they are popped: for any future day they are either inside a longer span ending at <code>i</code> or beyond <code>i</code>, and in both cases day <code>i</code> is the better reference.",
               "After popping, the top of the stack (if any) is the closest earlier day with a strictly higher price, so the span is <code>i - top</code>; with an empty stack it is <code>i + 1</code>. Every day is pushed and popped once, giving O(n) time and O(n) space."],
    time="O(n)", space="O(n)",
    solution='''def stockSpans(prices):
    spans = []
    stack = []  # indices with strictly decreasing prices
    for i, p in enumerate(prices):
        while stack and prices[stack[-1]] <= p:
            stack.pop()
        spans.append(i - stack[-1] if stack else i + 1)
        stack.append(i)
    return spans
''',
    tests=[[[100, 80, 60, 70, 60, 75, 85]], [[5]], [[7, 7, 7]], [[1, 2, 3, 4, 5]], [[5, 4, 3, 2, 1]], [[3, 1, 3, 1, 3]],
           [[100000, 1, 100000, 1]], [[2, 4, 4, 1, 5, 5, 3]]],
)
_r = rnd(7105)
p["tests"].append([[_r.randint(1, 100000) for _ in range(4000)]])
p["tests"].append([[_r.randint(1, 30) for _ in range(4000)]])
p["tests"].append([list(range(1, 4001))])


def b_span(prices):
    out = []
    for i in range(len(prices)):
        k = 1
        while i - k >= 0 and prices[i - k] <= prices[i]:
            k += 1
        out.append(k)
    return out


def v_span(tests):
    for t in tests:
        a = t["args"][0]
        assert 1 <= len(a) <= 10000 and all(1 <= x <= 100000 for x in a)


CHECKS["stock-price-span-per-day"] = (b_span, lambda r: [gen_arr(r, 1, 6, 1, 12)], "exact")
VALIDATE["stock-price-span-per-day"] = v_span

p = add(
    id="min-cost-merging-adjacent-values", title="Cheapest Way to Merge Adjacent Values", diff="Medium", topic=TOPIC, tier="extra",
    fn="minMergeCost", params=[("nums", "int[]")], ret="int", cmp="exact",
    desc="<p>You are given an array <code>nums</code> of positive integers. In one move you pick two <strong>adjacent</strong> elements <code>a</code> and <code>b</code>, pay <code>a * b</code>, and replace the pair by the single value <code>max(a, b)</code> (so the smaller one disappears and the array becomes one element shorter). Repeat until only one element remains.</p><p>Return the minimum total amount you can pay.</p><p>Example: <code>nums = [6, 2, 4]</code> gives <code>32</code>. Merge <code>2</code> and <code>4</code> first (cost 8, array becomes <code>[6, 4]</code>), then merge <code>6</code> and <code>4</code> (cost 24). Merging <code>6</code> and <code>2</code> first would cost 12 and leave <code>[6, 4]</code>, for a total of 36, which is worse.</p>",
    constraints=["1 &le; nums.length &le; 5,000", "1 &le; nums[i] &le; 100", "A single element costs 0"],
    hints=["Whenever two neighbours merge, the smaller of the two is removed for good. Its whole cost is its value times one other number. Which neighbour should it be multiplied with to be as cheap as possible?",
           "A value that is smaller than both of its current neighbours should be removed by merging it with the smaller of those two neighbours. A good order is therefore to remove local minima first.",
           "Scan left to right with a stack that is strictly decreasing. When a new value <code>x</code> arrives, pop every top <code>m</code> with <code>m &le; x</code>: pay <code>m * min(new top, x)</code>. At the end pay the products of the remaining neighbours."],
    editorial=["Every move removes exactly one element, namely the smaller of the merged pair, and charges that element times the other element of the pair. The best you can hope for when removing an element <code>m</code> is to pair it with the smaller of its two current neighbours, since it is no larger than either of them when it is a local minimum. Greedy removal of the smallest remaining element, always paired with its cheaper neighbour, is optimal: an exchange argument shows that postponing a removal never makes the partner smaller.",
               "A stack makes the greedy linear. Keep values strictly decreasing from bottom to top, with a huge sentinel at the bottom. For a new value <code>x</code>, while the top <code>m</code> is at most <code>x</code>, it has a bigger neighbour on both sides (the element below it and <code>x</code>), so remove it and pay <code>m * min(below, x)</code>. Then push <code>x</code>. When the scan ends the stack is strictly decreasing, so the smallest element is on top and is removed against the element below it: pay the product of each remaining adjacent pair.",
               "Every element is pushed and popped at most once: O(n) time and O(n) space. The answer is at most about 5000 * 100 * 100 = 5 * 10<sup>7</sup>, so it fits in 32 bits."],
    time="O(n)", space="O(n)",
    solution='''def minMergeCost(nums):
    stack = [10 ** 9]  # sentinel, larger than any value
    cost = 0
    for x in nums:
        while stack[-1] <= x:
            mid = stack.pop()
            cost += mid * min(stack[-1], x)
        stack.append(x)
    while len(stack) > 2:
        cost += stack.pop() * stack[-1]
    return cost
''',
    tests=[[[6, 2, 4]], [[4, 11]], [[7]], [[3, 3, 3]], [[1, 2, 3, 4, 5]], [[5, 4, 3, 2, 1]], [[1, 100, 1, 100, 1]], [[100, 100]],
           [[2, 5, 2, 5, 2, 5]], [[9, 1, 9, 1, 9]]],
)
_r = rnd(7106)
p["tests"].append([[_r.randint(1, 100) for _ in range(4000)]])
p["tests"].append([[_r.randint(1, 4) for _ in range(4000)]])
p["tests"].append([sorted(_r.randint(1, 100) for _ in range(4000))])
p["tests"].append([[100] * 5000])


def b_merge(nums):
    n = len(nums)
    best = [[0] * n for _ in range(n)]  # interval DP over split points, independent of the stack greedy
    top = [[0] * n for _ in range(n)]
    for i in range(n):
        top[i][i] = nums[i]
        for j in range(i + 1, n):
            top[i][j] = max(top[i][j - 1], nums[j])
    for length in range(2, n + 1):
        for i in range(n - length + 1):
            j = i + length - 1
            best[i][j] = min(best[i][k] + best[k + 1][j] + top[i][k] * top[k + 1][j] for k in range(i, j))
    return best[0][n - 1]


def v_merge(tests):
    for t in tests:
        a = t["args"][0]
        assert 1 <= len(a) <= 5000 and all(1 <= x <= 100 for x in a)
        assert 0 <= t["expected"] <= 100 * 100 * len(a)


CHECKS["min-cost-merging-adjacent-values"] = (b_merge, lambda r: [gen_arr(r, 1, 9, 1, 9)], "exact")
VALIDATE["min-cost-merging-adjacent-values"] = v_merge

p = add(
    id="closest-taller-either-side", title="Closest Taller Person on Either Side", diff="Medium", topic=TOPIC, tier="extra",
    fn="closestTaller", params=[("heights", "int[]")], ret="int[]", cmp="exact",
    desc="<p>People stand in a line and <code>heights[i]</code> is the height of person <code>i</code>. For each person <code>i</code>, find the closest person who is <strong>strictly taller</strong>, looking in <em>both</em> directions. Closeness is measured by index distance <code>|i - j|</code>.</p><p>Return an array <code>answer</code> where <code>answer[i]</code> is the index of that person. If a taller person at the same distance exists on both sides, choose the one on the <strong>left</strong> (smaller index). If nobody is taller, <code>answer[i] = -1</code>.</p><p>Example: <code>heights = [3, 1, 4, 2, 5, 2]</code> gives <code>[2, 0, 4, 2, -1, 4]</code>. Person 1 (height 1) has taller people at distance 1 on both sides (index 0 and 2), so the left one, 0, wins.</p>",
    constraints=["1 &le; heights.length &le; 10,000", "1 &le; heights[i] &le; 10<sup>9</sup>"],
    hints=["For each person the closest taller person on the left and the closest taller person on the right are independent questions. Solve each one first.",
           "The nearest strictly greater element to the left (and to the right) is the classic monotonic-stack query: keep a stack of indices with non-increasing heights and pop everything not taller than the current person.",
           "Run the stack once left to right for the left candidates and once right to left for the right candidates. Then per person compare the two distances, preferring the left one on a tie."],
    editorial=["The overall closest taller person is whichever of the two one-sided candidates is nearer. So compute <code>L[i]</code>, the nearest index to the left with a strictly greater height, and <code>R[i]</code>, the nearest index to the right with a strictly greater height. Each is an O(n) monotonic-stack sweep: process indices in order, pop while the stack top is not taller than the current height, and the remaining top is the nearest taller person; then push the current index.",
               "Finally combine: if only one side has a candidate, take it; if both exist, take <code>L[i]</code> when <code>i - L[i] &le; R[i] - i</code> and <code>R[i]</code> otherwise, which implements the left-first tie rule. If neither exists the answer is -1. Total O(n) time and O(n) space."],
    time="O(n)", space="O(n)",
    solution='''def closestTaller(heights):
    n = len(heights)
    left = [-1] * n
    right = [-1] * n
    stack = []
    for i in range(n):
        while stack and heights[stack[-1]] <= heights[i]:
            stack.pop()
        left[i] = stack[-1] if stack else -1
        stack.append(i)
    stack = []
    for i in range(n - 1, -1, -1):
        while stack and heights[stack[-1]] <= heights[i]:
            stack.pop()
        right[i] = stack[-1] if stack else -1
        stack.append(i)
    answer = []
    for i in range(n):
        a, b = left[i], right[i]
        if a == -1:
            answer.append(b)
        elif b == -1:
            answer.append(a)
        else:
            answer.append(a if i - a <= b - i else b)
    return answer
''',
    tests=[[[3, 1, 4, 2, 5, 2]], [[7]], [[2, 2, 2]], [[1, 2, 3, 4]], [[4, 3, 2, 1]], [[5, 1, 1, 1, 5]], [[1, 9, 1, 1, 8]],
           [[3, 9, 2, 2, 2, 7]], [[10 ** 9, 1, 10 ** 9]]],
)
_r = rnd(7107)
p["tests"].append([[_r.randint(1, 10 ** 9) for _ in range(3000)]])
p["tests"].append([[_r.randint(1, 40) for _ in range(3000)]])
p["tests"].append([[1 + abs(1500 - i) for i in range(3000)]])


def b_closest(heights):
    n = len(heights)
    out = []
    for i in range(n):
        ans = -1
        for d in range(1, n):
            if i - d >= 0 and heights[i - d] > heights[i]:
                ans = i - d
                break
            if i + d < n and heights[i + d] > heights[i]:
                ans = i + d
                break
        out.append(ans)
    return out


def v_closest(tests):
    for t in tests:
        a = t["args"][0]
        assert 1 <= len(a) <= 10000 and all(1 <= x <= 10 ** 9 for x in a)


CHECKS["closest-taller-either-side"] = (b_closest, lambda r: [gen_arr(r, 1, 6, 1, 12)], "exact")
VALIDATE["closest-taller-either-side"] = v_closest

p = add(
    id="max-sum-mountain-skyline", title="Maximum Sum Mountain Skyline", diff="Medium", topic=TOPIC, tier="extra",
    fn="maxMountainSum", params=[("maxHeights", "int[]")], ret="int", cmp="exact",
    desc="<p>You are building <code>n</code> towers in a row. Tower <code>i</code> may have any integer height <code>h[i]</code> with <code>1 &le; h[i] &le; maxHeights[i]</code>. The heights must form a <em>mountain</em>: there is a peak index <code>k</code> such that <code>h</code> is non-decreasing up to <code>k</code> (<code>h[0] &le; h[1] &le; ... &le; h[k]</code>) and non-increasing after it (<code>h[k] &ge; h[k+1] &ge; ... &ge; h[n-1]</code>).</p><p>Return the largest possible value of <code>h[0] + h[1] + ... + h[n-1]</code>.</p><p>Example: <code>maxHeights = [5, 3, 4, 1, 1]</code> gives <code>13</code> with heights <code>[5, 3, 3, 1, 1]</code> (peak at index 0). With <code>[6, 5, 3, 9, 2, 7]</code> the answer is <code>22</code>, using <code>[3, 3, 3, 9, 2, 2]</code>.</p>",
    constraints=["1 &le; maxHeights.length &le; 5,000", "1 &le; maxHeights[i] &le; 100,000"],
    hints=["Try every index as the peak. For a fixed peak, each tower should be as tall as the limits allow. How tall can tower <code>k - 1</code> be, and tower <code>k - 2</code>?",
           "With peak <code>k</code> at its own limit, tower <code>j &lt; k</code> gets <code>min(maxHeights[j..k])</code>, and symmetrically on the right. Summing this for every peak directly is O(n<sup>2</sup>) or worse; reuse work between peaks.",
           "Let <code>left[i]</code> be the best sum of towers <code>0..i</code> when tower <code>i</code> is the peak. Find the nearest index <code>j &lt; i</code> with a smaller limit using a stack: <code>left[i] = left[j] + maxHeights[i] * (i - j)</code>. Do the mirror image for <code>right</code>, and combine at each peak."],
    editorial=["Fix the peak <code>i</code> and give it height <code>maxHeights[i]</code>. Raising the peak never hurts, since all other heights are only capped from above by the minimum limit between them and the peak. For towers on the left, <code>h[j] = min(maxHeights[j..i])</code>.",
               "Let <code>j</code> be the nearest index left of <code>i</code> with <code>maxHeights[j] &lt; maxHeights[i]</code> (or -1). Towers <code>j+1..i</code> all get exactly <code>maxHeights[i]</code>, because everything between is at least as high. Towers at or before <code>j</code> are capped by the minimum up to <code>j</code>, which is the same situation as peak <code>j</code>. So <code>left[i] = left[j] + maxHeights[i] * (i - j)</code> with <code>left[-1] = 0</code>. The index <code>j</code> comes from a monotonic stack. The right side <code>right[i]</code> is the mirror image.",
               "The total for peak <code>i</code> is <code>left[i] + right[i] - maxHeights[i]</code> (the peak is counted twice) and the answer is the maximum over all <code>i</code>. Time O(n), space O(n). The maximum sum is below 5 * 10<sup>8</sup>, within 32 bits."],
    time="O(n)", space="O(n)",
    solution='''def maxMountainSum(maxHeights):
    n = len(maxHeights)
    left = [0] * n
    stack = []  # indices with strictly increasing limits
    for i in range(n):
        while stack and maxHeights[stack[-1]] >= maxHeights[i]:
            stack.pop()
        j = stack[-1] if stack else -1
        left[i] = (left[j] if j >= 0 else 0) + maxHeights[i] * (i - j)
        stack.append(i)
    right = [0] * n
    stack = []
    for i in range(n - 1, -1, -1):
        while stack and maxHeights[stack[-1]] >= maxHeights[i]:
            stack.pop()
        j = stack[-1] if stack else n
        right[i] = (right[j] if j < n else 0) + maxHeights[i] * (j - i)
        stack.append(i)
    return max(left[i] + right[i] - maxHeights[i] for i in range(n))
''',
    tests=[[[5, 3, 4, 1, 1]], [[6, 5, 3, 9, 2, 7]], [[3, 2, 5, 5, 2, 3]], [[1]], [[4, 4, 4]], [[1, 2, 3, 4, 5]], [[5, 4, 3, 2, 1]],
           [[100000, 1, 100000]], [[2, 9, 2, 9, 2]]],
)
_r = rnd(7108)
p["tests"].append([[_r.randint(1, 100000) for _ in range(3000)]])
p["tests"].append([[_r.randint(1, 20) for _ in range(3000)]])
p["tests"].append([[100000] * 5000])
p["tests"].append([[min(i, 4999 - i) * 20 + 1 for i in range(5000)]])


def b_mountain(mh):
    n = len(mh)
    best = 0
    for k in range(n):
        total = 0
        cur = mh[k]
        for j in range(k, -1, -1):
            cur = min(cur, mh[j])
            total += cur
        cur = mh[k]
        for j in range(k + 1, n):
            cur = min(cur, mh[j])
            total += cur
        best = max(best, total)
    return best


def v_mountain(tests):
    for t in tests:
        a = t["args"][0]
        assert 1 <= len(a) <= 5000 and all(1 <= x <= 100000 for x in a)
        assert t["expected"] <= 100000 * len(a)


CHECKS["max-sum-mountain-skyline"] = (b_mountain, lambda r: [gen_arr(r, 1, 7, 1, 11)], "exact")
VALIDATE["max-sum-mountain-skyline"] = v_mountain

# ---------------------------------------------------------------- HARD

p = add(
    id="people-visible-in-queue", title="People Each Person Can See in a Queue", diff="Hard", topic=TOPIC,
    fn="visibleToTheRight", params=[("heights", "int[]")], ret="int[]", cmp="exact",
    desc="<p>People stand in a line from left to right; <code>heights[i]</code> is the height of person <code>i</code>, and all heights are <strong>distinct</strong>. Person <code>i</code> <em>can see</em> person <code>j</code> (<code>j &gt; i</code>) if everybody standing strictly between them is shorter than <strong>both</strong> <code>heights[i]</code> and <code>heights[j]</code>. (Neighbors always see each other.)</p><p>Return an array <code>answer</code> where <code>answer[i]</code> is the number of people to the right of person <code>i</code> that person <code>i</code> can see.</p><p>Example: <code>heights = [10, 6, 8, 5, 11, 9]</code> gives <code>[3, 1, 2, 1, 1, 0]</code>. Person 0 (height 10) sees the people of height 6, 8 and 11; the person of height 5 is hidden behind the 8, and the 9 behind the 11.</p>",
    constraints=["1 &le; heights.length &le; 10,000", "1 &le; heights[i] &le; 10<sup>9</sup>", "All heights are distinct"],
    hints=["Person <code>i</code> keeps seeing to the right until the first person at least as tall as <code>i</code> blocks the view for everyone behind. Describe exactly which people are seen up to and including that blocker.",
           "Looking along the line, the people <code>i</code> sees (before a blocker) are the successive 'record highs' of the people to its right, i.e. a monotonic structure. Process people from right to left and keep exactly that structure.",
           "Sweep from right to left with a stack of heights that is decreasing from bottom to top (the top is the nearest person). For person <code>i</code>: pop every shorter person and count each as seen; if the stack is still non-empty, the new top is taller and is also seen (count one more). Push <code>i</code>."],
    editorial=["Sweep from right to left and maintain a stack that contains the people who are potentially visible to someone further left: from the top (nearest) to the bottom (farthest) their heights increase, because a person hidden behind a taller person nearer to the viewer can never be seen by anybody to the left of that taller person.",
               "For person <code>i</code>, every stack element that is shorter than <code>i</code> is visible, since everything between them and <code>i</code> is shorter than that element (it was a record high), so pop each and add one. The first element that is taller than <code>i</code> is also visible (everyone between is shorter than <code>i</code>), but it blocks everything behind it, so add one more and stop. Elements popped are hidden from everyone left of <code>i</code>, because <code>i</code> is taller and nearer. Then push <code>i</code>.",
               "Each person is pushed once and popped at most once: O(n) time, O(n) space. Distinct heights keep the rule 'shorter vs taller' unambiguous."],
    time="O(n)", space="O(n)",
    solution='''def visibleToTheRight(heights):
    n = len(heights)
    answer = [0] * n
    stack = []  # heights, increasing from top (nearest) to bottom (farthest)
    for i in range(n - 1, -1, -1):
        seen = 0
        while stack and stack[-1] < heights[i]:
            stack.pop()
            seen += 1
        if stack:
            seen += 1
        answer[i] = seen
        stack.append(heights[i])
    return answer
''',
    tests=[[[10, 6, 8, 5, 11, 9]], [[5, 1, 2, 3, 10]], [[4]], [[1, 2]], [[2, 1]], [[1, 2, 3, 4, 5]], [[5, 4, 3, 2, 1]],
           [[3, 9, 1, 8, 2, 7, 4]], [[10 ** 9, 1, 999999999, 2, 7]]],
)
_r = rnd(7109)
p["tests"].append([_r.sample(range(1, 10 ** 9), 3000)])
p["tests"].append([_r.sample(range(1, 10 ** 9), 5)])
p["tests"].append([list(range(1, 3001))])
p["tests"].append([list(range(3000, 0, -1))])


def b_visible(h):
    n = len(h)
    out = []
    for i in range(n):
        c = 0
        for j in range(i + 1, n):
            lim = min(h[i], h[j])
            if all(h[k] < lim for k in range(i + 1, j)):
                c += 1
        out.append(c)
    return out


def g_visible(r):
    n = r.randint(1, 10)
    return [r.sample(range(1, 30), n)]


def v_visible(tests):
    for t in tests:
        a = t["args"][0]
        assert 1 <= len(a) <= 10000 and len(set(a)) == len(a) and all(1 <= x <= 10 ** 9 for x in a)


CHECKS["people-visible-in-queue"] = (b_visible, g_visible, "exact")
VALIDATE["people-visible-in-queue"] = v_visible

p = add(
    id="second-greater-element-values", title="Second Greater Element to the Right", diff="Hard", topic=TOPIC,
    fn="secondGreater", params=[("nums", "int[]")], ret="int[]", cmp="exact",
    desc="<p>For each index <code>i</code> of <code>nums</code>, define its <em>second greater value</em> as follows: among the positions to the right of <code>i</code>, look at those holding a value <strong>strictly larger</strong> than <code>nums[i]</code>; the second greater value is the value at the <strong>second</strong> such position, counted from left to right. If fewer than two such positions exist, it is <code>-1</code>.</p><p>Return an array with the second greater value of every index.</p><p>Example: <code>nums = [2, 4, 0, 9, 6]</code> gives <code>[9, 6, 6, -1, -1]</code>. For the 2, the larger values to its right are 4, 9, 6 in that order, so the second is 9. For the 4, they are 9 and 6, so the second is 6.</p>",
    constraints=["1 &le; nums.length &le; 10,000", "0 &le; nums[i] &le; 10<sup>9</sup>"],
    hints=["The ordinary next greater element uses one stack. What if an element needs to be 'beaten' twice before it is settled?",
           "Keep two groups of waiting indices: those that have not yet seen any greater value, and those that have seen exactly one and now wait for a second.",
           "For each new value <code>x</code>: first pop from the second group every index whose value is <code>&lt; x</code> and answer it with <code>x</code>. Then move every index of the first group with value <code>&lt; x</code> into the second group (keeping their relative order so the second group stays sorted), and finally push the current index on the first group."],
    editorial=["Use two monotonic stacks of indices: <code>s1</code> holds indices that have seen <em>no</em> greater value yet, and <code>s2</code> holds indices that have seen <em>exactly one</em>. Both keep their values non-increasing from bottom to top. When a value <code>x</code> arrives:",
               "(1) Settle second-group indices: while the top of <code>s2</code> has a value &lt; <code>x</code>, pop it and set its answer to <code>x</code> (this is the second larger value it meets). Do this first, so that an index promoted in step 2 is not settled by the same <code>x</code>. (2) Promote first-group indices: pop everything from <code>s1</code> with a value &lt; <code>x</code>; these have now seen one greater value. Push them onto <code>s2</code> in their original order (reverse of the pop order) so that <code>s2</code> stays non-increasing. (3) Push the current index on <code>s1</code>.",
               "Every index enters each stack once and leaves once, so time is O(n) and space is O(n). Indices still waiting at the end keep the answer -1."],
    time="O(n)", space="O(n)",
    solution='''def secondGreater(nums):
    n = len(nums)
    answer = [-1] * n
    first = []   # indices that have seen no greater value yet
    second = []  # indices that have seen exactly one greater value
    for j, x in enumerate(nums):
        while second and nums[second[-1]] < x:
            answer[second.pop()] = x
        moved = []
        while first and nums[first[-1]] < x:
            moved.append(first.pop())
        second.extend(reversed(moved))
        first.append(j)
    return answer
''',
    tests=[[[2, 4, 0, 9, 6]], [[3, 3]], [[5]], [[1, 2, 3, 4, 5]], [[5, 4, 3, 2, 1]], [[1, 5, 2, 6, 3, 7]], [[0, 0, 0, 1, 1]],
           [[4, 1, 2, 3, 5, 0, 6]], [[10 ** 9, 0, 10 ** 9, 0]]],
)
_r = rnd(7110)
p["tests"].append([[_r.randint(0, 10 ** 9) for _ in range(3000)]])
p["tests"].append([[_r.randint(0, 25) for _ in range(3000)]])
p["tests"].append([list(range(3000))])
p["tests"].append([list(range(3000, 0, -1))])


def b_second(nums):
    n = len(nums)
    out = []
    for i in range(n):
        found = 0
        ans = -1
        for j in range(i + 1, n):
            if nums[j] > nums[i]:
                found += 1
                if found == 2:
                    ans = nums[j]
                    break
        out.append(ans)
    return out


def v_second(tests):
    for t in tests:
        a = t["args"][0]
        assert 1 <= len(a) <= 10000 and all(0 <= x <= 10 ** 9 for x in a)


CHECKS["second-greater-element-values"] = (b_second, lambda r: [gen_arr(r, 0, 6, 1, 14)], "exact")
VALIDATE["second-greater-element-values"] = v_second

p = add(
    id="rounds-to-non-decreasing-array", title="Rounds Until the Array Is Non-Decreasing", diff="Hard", topic=TOPIC,
    fn="roundsToSorted", params=[("nums", "int[]")], ret="int", cmp="exact",
    desc="<p>The following process is applied to the integer array <code>nums</code>. In each <em>round</em>, every element that is <strong>strictly smaller</strong> than the element immediately to its left (in the current array) is marked, and then all marked elements are removed at the same time. The process stops when no element is removed, i.e. when the array is non-decreasing.</p><p>Return the number of rounds in which at least one element is removed.</p><p>Example: <code>nums = [5, 3, 4, 4, 7, 3, 6, 11, 8, 5, 11]</code> gives <code>3</code>. Round 1 removes 3, 3, 8 and 5 and leaves <code>[5, 4, 4, 7, 6, 11, 11]</code>; round 2 removes 4 and 6 and leaves <code>[5, 4, 7, 11, 11]</code>... wait, only elements smaller than their left neighbor go, so round 2 leaves <code>[5, 7, 11, 11]</code> after removing the 4 (smaller than 5) and the 6 (smaller than 7); round 3 has nothing left to remove, so the answer would be 2 here.</p>",
    constraints=["1 &le; nums.length &le; 10,000", "1 &le; nums[i] &le; 10<sup>9</sup>"],
    hints=["Simulating rounds directly can take up to n rounds of O(n) work each. Ask instead: in which round does each individual element disappear?",
           "Element <code>x</code> is removed in the round after everything between it and its 'blocker' (the nearest element to its left that is strictly greater) has been removed, but only if such a blocker exists.",
           "Use a stack of (value, round of removal) pairs from left to right. For a new element, pop all elements with value <code>&le; x</code> and take the maximum of their removal rounds <code>t</code>. If the stack is then empty, <code>x</code> is never removed (round 0); otherwise its round is <code>t + 1</code>. The answer is the largest round."],
    editorial=["Let <code>dp[i]</code> be the round in which element <code>i</code> is removed (0 if it never is). Element <code>i</code> is only ever removed if some element to its left is strictly greater: let <code>p</code> be the nearest such element. Everything strictly between <code>p</code> and <code>i</code> is <code>&le; nums[i]</code>. The element <code>i</code> becomes adjacent to <code>p</code> once all of those in-between elements are gone, which happens after <code>max(dp[k])</code> rounds over them; in the next round it is exposed to <code>p</code> and removed. So <code>dp[i] = 1 + max(dp[k] for k between p and i)</code>, or 0 when no such <code>p</code> exists.",
               "A monotonic stack computes this in one pass. Keep (value, dp) pairs with strictly decreasing values from bottom to top. For element <code>x</code>, pop all pairs with value <code>&le; x</code> and take the maximum of their dp values, <code>t</code> (0 if none popped). If the stack is empty after the pops, <code>dp = 0</code>; otherwise <code>dp = t + 1</code>. Push <code>(x, dp)</code> and update the global maximum, which is the answer. O(n) time, O(n) space."],
    time="O(n)", space="O(n)",
    solution='''def roundsToSorted(nums):
    best = 0
    stack = []  # (value, round in which it is removed); values strictly decreasing
    for x in nums:
        t = 0
        while stack and stack[-1][0] <= x:
            t = max(t, stack.pop()[1])
        t = t + 1 if stack else 0
        best = max(best, t)
        stack.append((x, t))
    return best
''',
    tests=[[[5, 3, 4, 4, 7, 3, 6, 11, 8, 5, 11]], [[4, 5, 7, 7, 13]], [[1]], [[2, 1]], [[5, 4, 3, 2, 1]], [[6, 1, 2, 3, 4, 5]], [[3, 3, 3]],
           [[10, 1, 2, 11, 3, 4]], [[10 ** 9, 1, 10 ** 9, 1]]],
)
_r = rnd(7111)
p["tests"].append([[_r.randint(1, 10 ** 9) for _ in range(4000)]])
p["tests"].append([[4000] + list(range(1, 4000))])
p["tests"].append([[_r.randint(1, 50) for _ in range(4000)]])
p["tests"].append([[(i * 7919) % 1009 + 1 for i in range(4000)]])


def b_rounds(nums):
    a = list(nums)
    rounds = 0
    while True:
        keep = [a[0]] + [a[i] for i in range(1, len(a)) if a[i] >= a[i - 1]]
        if len(keep) == len(a):
            return rounds
        a = keep
        rounds += 1


def v_rounds(tests):
    for t in tests:
        a = t["args"][0]
        assert 1 <= len(a) <= 10000 and all(1 <= x <= 10 ** 9 for x in a)


CHECKS["rounds-to-non-decreasing-array"] = (b_rounds, lambda r: [gen_arr(r, 1, 8, 1, 14)], "exact")
VALIDATE["rounds-to-non-decreasing-array"] = v_rounds
