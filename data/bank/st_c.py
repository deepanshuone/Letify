from lib import add, rnd, CHECKS, VALIDATE, gen_arr  # noqa: F401
"""Problems: stack - histograms and areas (reach widths, rectangle counts, skyline and grid variants)."""
import heapq  # noqa: F401  (used only inside reference solutions that import it themselves)

TOPIC = "Stack"
INT_MAX = 2 ** 31 - 1


def _bin_grid(r, R, C, pr):
    return [[1 if r.random() < pr else 0 for _ in range(C)] for _ in range(R)]


# ======================================================================= EASY

p = add(
    id="bar-reach-widths", title="Reach Width of Each Bar", diff="Easy", topic=TOPIC, tier="common",
    fn="barReachWidths", params=[("heights", "int[]")], ret="int[]", cmp="exact",
    desc="<p>A histogram is given by the array <code>heights</code>: bar <code>i</code> has width 1 and height <code>heights[i]</code>. For a bar <code>i</code>, look at the longest block of consecutive bars that contains bar <code>i</code> and in which <em>every bar is at least as tall as bar i</em>. The number of bars in that block is the <em>reach width</em> of bar <code>i</code>.</p><p>Return an array <code>widths</code> where <code>widths[i]</code> is the reach width of bar <code>i</code>. (A bar's reach width times its height is the area of the widest rectangle that uses the full height of that bar.)</p><p>Example: for <code>heights = [2, 1, 5, 6, 2, 3]</code> the answer is <code>[1, 6, 2, 1, 4, 1]</code>. Bar 4 (height 2) can stretch left over the bars of height 6 and 5 and right over the bar of height 3, but the bar of height 1 stops it: the block is bars 2 to 5, four bars.</p>",
    constraints=["1 &le; heights.length &le; 10,000", "0 &le; heights[i] &le; 10<sup>9</sup>"],
    hints=["Expanding left and right from every bar until a shorter bar appears is correct but can take O(n<sup>2</sup>) time. What do you really need to know about each bar?",
           "Only two things: the nearest bar to the left that is strictly shorter, and the nearest bar to the right that is strictly shorter. The reach width is the gap between them, minus one.",
           "Find the nearest strictly shorter bar on one side with a stack of indices whose heights increase: pop every index whose height is not smaller than the current bar, and the index left on top (if any) is the answer. Repeat from the other side."],
    editorial=["Let <code>L[i]</code> be the index of the nearest bar to the left of <code>i</code> that is strictly shorter than bar <code>i</code> (or -1), and <code>R[i]</code> the nearest strictly shorter bar to the right (or <code>n</code>). Every bar strictly between them is at least as tall as bar <code>i</code>, and the two bars at the ends are shorter, so the block is exactly <code>L[i]+1 .. R[i]-1</code> and the reach width is <code>R[i] - L[i] - 1</code>.",
               "Both boundaries are found with a monotonic stack. Scanning left to right, keep a stack of indices with strictly increasing heights. For the current bar, pop while the top has height <code>&ge;</code> the current height; those bars are not strictly shorter and can never be the nearest shorter bar for anything later that is not blocked by the current bar. The index now on top is <code>L[i]</code>; then push <code>i</code>. A mirrored right-to-left pass gives <code>R[i]</code>. Every index is pushed and popped at most once per pass, so the time is O(n) and the space O(n). This exact building block powers the largest-rectangle-in-histogram solution."],
    time="O(n)", space="O(n)",
    solution='''def barReachWidths(heights):
    n = len(heights)
    left = [-1] * n
    right = [n] * n
    stack = []
    for i in range(n):
        while stack and heights[stack[-1]] >= heights[i]:
            stack.pop()
        left[i] = stack[-1] if stack else -1
        stack.append(i)
    stack = []
    for i in range(n - 1, -1, -1):
        while stack and heights[stack[-1]] >= heights[i]:
            stack.pop()
        right[i] = stack[-1] if stack else n
        stack.append(i)
    return [right[i] - left[i] - 1 for i in range(n)]
''',
    tests=[[[2, 1, 5, 6, 2, 3]], [[3, 3]], [[7]], [[0]], [[5, 4, 3, 2, 1]], [[1, 2, 3, 4, 5]], [[2, 2, 2, 2]],
           [[0, 3, 0, 3, 0]], [[4, 1, 4, 1, 4]], [[1000000000, 0, 1000000000]], [[3, 1, 3, 2, 2, 5, 1, 4]]],
)
_r = rnd(7701)
p["tests"].append([[_r.randint(0, 10 ** 9) for _ in range(3000)]])
p["tests"].append([[_r.randint(0, 12) for _ in range(3000)]])
p["tests"].append([sorted(_r.randint(0, 10 ** 6) for _ in range(2500))])
p["tests"].append([[5] * 2500])


def b_reach(heights):
    n = len(heights)
    out = []
    for i in range(n):
        l = i
        while l > 0 and heights[l - 1] >= heights[i]:
            l -= 1
        r = i
        while r < n - 1 and heights[r + 1] >= heights[i]:
            r += 1
        out.append(r - l + 1)
    return out


def v_reach(tests):
    for t in tests:
        h = t["args"][0]
        assert 1 <= len(h) <= 10000 and all(0 <= x <= 10 ** 9 for x in h)
        assert len(t["expected"]) == len(h) and all(1 <= w <= len(h) for w in t["expected"])


CHECKS["bar-reach-widths"] = (b_reach, lambda r: [gen_arr(r, 0, 5, 1, 12)], "exact")
VALIDATE["bar-reach-widths"] = v_reach


p = add(
    id="count-wet-columns", title="Count Columns Holding Rain", diff="Easy", topic=TOPIC, tier="extra",
    fn="countWetColumns", params=[("heights", "int[]")], ret="int", cmp="exact",
    desc="<p>A terrain is a row of unit-width columns; column <code>i</code> is <code>heights[i]</code> units tall. After heavy rain, the water standing above column <code>i</code> is</p><pre>water[i] = min(L, R) - heights[i]\nL = max(heights[0..i]),  R = max(heights[i..n-1])</pre><p>(the water level over a column is limited by the lower of the tallest column on its left and the tallest on its right, each counting the column itself). A column is <em>wet</em> when <code>water[i] &gt; 0</code>.</p><p>Return how many columns are wet. Example: for <code>[0,1,0,2,1,0,1,3,2,1,2,1]</code> the wet columns are 2, 4, 5, 6 and 9, so the answer is <code>5</code>.</p>",
    constraints=["1 &le; heights.length &le; 10,000", "0 &le; heights[i] &le; 100,000"],
    hints=["Write down when <code>min(L, R) - heights[i]</code> is positive. Remember that L and R both include <code>heights[i]</code> itself.",
           "A column is wet exactly when there is a column strictly taller than it somewhere on its left <em>and</em> somewhere on its right.",
           "Scan once from the left keeping the running maximum to mark columns that have a strictly taller column on the left, then scan from the right the same way, and count columns marked by both passes."],
    editorial=["Because <code>L</code> and <code>R</code> include the column itself, both are at least <code>heights[i]</code>. So <code>min(L, R) &gt; heights[i]</code> holds exactly when <code>L &gt; heights[i]</code> and <code>R &gt; heights[i]</code>, that is, when the tallest column strictly before <code>i</code> is taller than <code>heights[i]</code> and the tallest column strictly after <code>i</code> is also taller. Equal-height neighbours do not hold any water in this rule.",
               "Make one pass from the left recording whether the maximum so far exceeds the current column, one pass from the right doing the same, and count the columns where both are true. The same information comes from a monotonic stack that keeps a non-increasing sequence of heights, but the running maxima are simpler and use O(n) time and O(n) space for the marks (or O(1) extra space with a suffix-maximum array reused). This predicate is the first step towards the full trapped-water computations."],
    time="O(n)", space="O(n)",
    solution='''def countWetColumns(heights):
    n = len(heights)
    taller_left = [False] * n
    best = -1
    for i in range(n):
        taller_left[i] = best > heights[i]
        if heights[i] > best:
            best = heights[i]
    count = 0
    best = -1
    for i in range(n - 1, -1, -1):
        if taller_left[i] and best > heights[i]:
            count += 1
        if heights[i] > best:
            best = heights[i]
    return count
''',
    tests=[[[0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1]], [[4, 2, 0, 3, 2, 5]], [[3]], [[1, 2, 3]], [[3, 3, 3]], [[3, 0, 3]],
           [[2, 0, 2, 0, 2]], [[5, 4, 3, 2, 1]], [[0, 0, 0]], [[5, 1, 1, 1, 5]], [[3, 1, 3, 1, 3, 1, 3]]],
)
_r = rnd(7702)
p["tests"].append([[_r.randint(0, 100000) for _ in range(8000)]])
p["tests"].append([[100000 if i % 2 == 0 else _r.randint(0, 99999) for i in range(8000)]])
p["tests"].append([[min(i, 8000 - i) for i in range(8001)]])


def b_wet(heights):
    n = len(heights)
    c = 0
    for i in range(n):
        L = max(heights[:i + 1])
        R = max(heights[i:])
        if min(L, R) - heights[i] > 0:
            c += 1
    return c


def v_wet(tests):
    for t in tests:
        h = t["args"][0]
        assert 1 <= len(h) <= 10000 and all(0 <= x <= 100000 for x in h)


CHECKS["count-wet-columns"] = (b_wet, lambda r: [gen_arr(r, 0, 5, 1, 12)], "exact")
VALIDATE["count-wet-columns"] = v_wet


# ===================================================================== MEDIUM

p = add(
    id="fewest-rectangles-to-build-skyline", title="Fewest Rectangles to Build a Skyline", diff="Medium", topic=TOPIC, tier="extra",
    fn="fewestRectangles", params=[("heights", "int[]")], ret="int", cmp="exact",
    desc="<p>A skyline is the region formed by <code>n</code> unit-wide columns standing side by side: column <code>i</code> covers the x-range <code>[i, i+1]</code> and the y-range <code>[0, heights[i]]</code>. You want to build exactly this region out of axis-aligned rectangles with integer corners. The rectangles must not overlap and must cover the region completely and nothing outside it.</p><p>Return the minimum number of rectangles needed. A column of height 0 is empty and is not part of the region.</p><p>Examples: <code>[2, 3, 2, 3]</code> needs <code>3</code> (one 3-wide 2-tall block, plus two single-column pieces on top). <code>[3, 1, 3]</code> needs <code>3</code> (a wide base and two towers), and <code>[4, 4, 4]</code> needs just <code>1</code>.</p>",
    constraints=["1 &le; heights.length &le; 10,000", "0 &le; heights[i] &le; 10<sup>9</sup>"],
    hints=["Start with small cases: a staircase going up, a valley (<code>[3,1,3]</code>) and a plateau. When does a new rectangle really have to start, and when can an existing one just be extended to the right?",
           "Think of the rectangles that are still open as layers piled on top of each other, with strictly increasing top levels. A column of height <code>h</code> forces every open layer with a top above <code>h</code> to end.",
           "Keep a stack of open top levels. For each column pop all levels greater than <code>h</code>. If the new top equals <code>h</code>, that layer simply continues; otherwise (and if <code>h &gt; 0</code>) push <code>h</code> and count one new rectangle."],
    editorial=["Scan the columns from left to right and maintain a stack of strictly increasing heights; each entry stands for a rectangle that is still being extended to the right, stacked above the entry below it (it spans from the level of the entry below up to its own level). When the next column has height <code>h</code>, every open rectangle that reaches higher than <code>h</code> has to be closed here, so pop all entries greater than <code>h</code>.",
               "Now look at the new top. If it equals <code>h</code>, the rectangle ending at level <code>h</code> continues over this column for free. If it is lower (or the stack is empty) and <code>h &gt; 0</code>, a new rectangle between that level and <code>h</code> must start at this column, so push <code>h</code> and add one to the answer. Equal neighbours and the plateau case therefore cost nothing, while valleys cost a new piece on the way back up. The answer is the number of pushes. Each column is pushed and popped at most once, giving O(n) time and O(n) space. A brute-force check over all tilings of small skylines confirms that this greedy count is minimal."],
    time="O(n)", space="O(n)",
    solution='''def fewestRectangles(heights):
    stack = []
    count = 0
    for h in heights:
        while stack and stack[-1] > h:
            stack.pop()
        if h > 0 and (not stack or stack[-1] < h):
            stack.append(h)
            count += 1
    return count
''',
    tests=[[[2, 3, 2, 3]], [[3, 1, 3]], [[4, 4, 4]], [[1]], [[0]], [[0, 0]], [[1, 2, 3]], [[3, 2, 1]], [[2, 0, 2]],
           [[1, 2, 1, 2, 1]], [[5, 3, 4, 3, 5, 1, 5]], [[10 ** 9, 10 ** 9 - 1, 10 ** 9]]],
)
_r = rnd(7703)
p["tests"].append([[_r.randint(0, 10 ** 9) for _ in range(5000)]])
p["tests"].append([[_r.randint(0, 6) for _ in range(8000)]])
p["tests"].append([list(range(1, 3001)) + list(range(3000, 0, -1))])


def b_rects(heights):
    # exact minimum partition into rectangles by exhaustive search over tilings (small inputs only)
    n = len(heights)
    H = max(heights) if heights else 0
    cells = [(y, x) for x in range(n) for y in range(heights[x])]
    index = {c: k for k, c in enumerate(cells)}
    full = (1 << len(cells)) - 1
    memo = {}

    def solve(mask):
        if mask == full:
            return 0
        if mask in memo:
            return memo[mask]
        k = 0
        while mask >> k & 1:
            k += 1
        y0, x0 = cells[k]  # lowest-then-leftmost free cell is the bottom-left corner of its rectangle
        best = 10 ** 9
        x1 = x0
        while x1 < n and (y0, x1) in index and not (mask >> index[(y0, x1)] & 1):
            y1 = y0
            ok = True
            while ok:
                for x in range(x0, x1 + 1):
                    c = (y1, x)
                    if c not in index or (mask >> index[c] & 1):
                        ok = False
                        break
                if not ok:
                    break
                m = mask
                for yy in range(y0, y1 + 1):
                    for x in range(x0, x1 + 1):
                        m |= 1 << index[(yy, x)]
                best = min(best, 1 + solve(m))
                y1 += 1
            x1 += 1
        memo[mask] = best
        return best

    return solve(0)


def v_rects(tests):
    for t in tests:
        h = t["args"][0]
        assert 1 <= len(h) <= 10000 and all(0 <= x <= 10 ** 9 for x in h)


CHECKS["fewest-rectangles-to-build-skyline"] = (b_rects, lambda r: [gen_arr(r, 0, 4, 1, 6)], "exact")
VALIDATE["fewest-rectangles-to-build-skyline"] = v_rects


p = add(
    id="largest-rectangle-circular-histogram", title="Largest Rectangle on a Ring of Bars", diff="Medium", topic=TOPIC, tier="extra",
    fn="largestRingRectangle", params=[("heights", "int[]")], ret="int", cmp="exact",
    desc="<p>Bars of width 1 are arranged around a circle, so bar <code>n-1</code> is next to bar <code>0</code>. Bar <code>i</code> has height <code>heights[i]</code>.</p><p>A rectangle is formed by choosing an <em>arc</em>: a block of <code>k</code> consecutive bars (going around the circle, possibly wrapping from the last bar to the first), where <code>1 &le; k &le; n</code>. Its height is the smallest bar in the arc and its area is <code>k</code> times that height. Return the largest possible area.</p><p>Example: <code>heights = [4, 1, 3, 4]</code>. The arc made of bars 2, 3, 0 (heights 3, 4, 4, wrapping around) has area <code>3 * 3 = 9</code>, which is the best; the arc 3, 0 has area <code>2 * 4 = 8</code>.</p>",
    constraints=["1 &le; heights.length &le; 10,000", "0 &le; heights[i] &le; 10,000"],
    hints=["Without the wrap-around this is the classic largest rectangle in a histogram. How can you let an arc cross the boundary between the last and first bar?",
           "Write the array twice in a row. Every arc of the ring is a contiguous block of this doubled array of length at most <code>n</code>.",
           "Run the stack-based largest-rectangle algorithm on the doubled array, but when a bar's maximal block is wider than <code>n</code>, use width <code>n</code> instead."],
    editorial=["Duplicate the array to get a line of <code>2n</code> bars. Any arc of the ring (including one that wraps) appears as a contiguous block of at most <code>n</code> bars in this line, and every such block is a real arc. So we need the best rectangle of width at most <code>n</code> in the doubled histogram.",
               "For every bar find the nearest strictly lower bar on each side with a monotonic stack; the maximal block where this bar is the minimum has some width <code>w</code>. If <code>w &gt; n</code>, then every window of <code>n</code> bars inside the block still has minimum at least the bar's height, so a rectangle of width <code>n</code> and that height is valid; hence the candidate area is <code>height * min(w, n)</code>. The answer is the maximum candidate. Candidates never exceed the true best (they correspond to real arcs) and the true best arc is found at its minimum bar, so the maximum is exact. Time O(n), space O(n)."],
    time="O(n)", space="O(n)",
    solution='''def largestRingRectangle(heights):
    n = len(heights)
    a = heights + heights
    m = 2 * n
    left = [-1] * m
    right = [m] * m
    stack = []
    for i in range(m):
        while stack and a[stack[-1]] >= a[i]:
            stack.pop()
        left[i] = stack[-1] if stack else -1
        stack.append(i)
    stack = []
    for i in range(m - 1, -1, -1):
        while stack and a[stack[-1]] >= a[i]:
            stack.pop()
        right[i] = stack[-1] if stack else m
        stack.append(i)
    best = 0
    for i in range(m):
        width = min(right[i] - left[i] - 1, n)
        best = max(best, a[i] * width)
    return best
''',
    tests=[[[4, 1, 3, 4]], [[2, 1, 5, 6, 2, 3]], [[5]], [[0]], [[3, 3, 3]], [[1, 2, 3, 4, 5]], [[5, 4, 3, 2, 1]],
           [[0, 5, 5, 0]], [[6, 2, 5, 4, 5, 1, 6]], [[10, 0, 10, 10, 0, 10]], [[7, 7, 1, 7, 7]]],
)
_r = rnd(7704)
p["tests"].append([[_r.randint(0, 10000) for _ in range(8000)]])
p["tests"].append([[_r.randint(5000, 10000) for _ in range(8000)]])
p["tests"].append([[10000] * 3 + [_r.randint(0, 3) for _ in range(5000)] + [10000] * 4000])


def b_ring(heights):
    n = len(heights)
    best = 0
    for s in range(n):
        m = 10 ** 9
        for k in range(1, n + 1):
            m = min(m, heights[(s + k - 1) % n])
            best = max(best, m * k)
    return best


def v_ring(tests):
    for t in tests:
        h = t["args"][0]
        assert 1 <= len(h) <= 10000 and all(0 <= x <= 10000 for x in h)


CHECKS["largest-rectangle-circular-histogram"] = (b_ring, lambda r: [gen_arr(r, 0, 6, 1, 10)], "exact")
VALIDATE["largest-rectangle-circular-histogram"] = v_ring


p = add(
    id="count-maximal-histogram-rectangles", title="Count Maximal Histogram Rectangles", diff="Medium", topic=TOPIC, tier="extra",
    fn="countMaximalRectangles", params=[("heights", "int[]")], ret="int", cmp="exact",
    desc="<p>A histogram has bars of width 1 and heights <code>heights[i]</code>. A rectangle inside it covers bars <code>l..r</code> (consecutive, <code>l &le; r</code>) and has a positive integer height not above the shortest of those bars.</p><p>Call a rectangle <em>maximal</em> if it cannot be made bigger inside the histogram: it cannot be made taller, and it cannot be extended by one bar to the left or to the right. Two maximal rectangles are different when their bar ranges <code>l..r</code> differ. Return the number of maximal rectangles.</p><p>Example: for <code>[2, 1, 2]</code> the maximal rectangles are bars <code>0..0</code> (height 2), bars <code>2..2</code> (height 2) and bars <code>0..2</code> (height 1), so the answer is <code>3</code>. For <code>[2, 3, 2]</code> the answer is <code>2</code>: bar 1 alone (height 3) and bars 0..2 (height 2).</p>",
    constraints=["1 &le; heights.length &le; 10,000", "0 &le; heights[i] &le; 10<sup>9</sup>"],
    hints=["A maximal rectangle is determined by its bar range: its height must equal the minimum of that range, and the bars just outside the range must be strictly shorter than that minimum (or not exist). A bar of height 0 can never be part of one.",
           "For each bar, the range where it is a minimum is bounded by the nearest strictly shorter bars. Several bars of equal height can describe the same range; count each range once.",
           "Scan left to right with a stack of strictly increasing positive heights. Popping a height (because a strictly shorter bar arrived) closes exactly one maximal rectangle; a bar equal to the top is not pushed again."],
    editorial=["Keep a stack of strictly increasing positive heights, one entry per rectangle that is still open. For each new height <code>h</code> (finish with a sentinel <code>0</code>), pop every entry greater than <code>h</code>: the arrival of a strictly shorter bar is precisely what stops that rectangle from extending to the right, and the rectangle cannot extend to the left either because the entry below it was strictly smaller (or the stack was empty). Each pop therefore counts one maximal rectangle.",
               "If the top of the stack now equals <code>h</code> the open rectangle just continues over this bar (so equal bars and bars of the same plateau are not counted twice), otherwise push <code>h</code> if it is positive. A zero pops everything and is never pushed. Every bar is pushed and popped at most once, so the time is O(n) and the space O(n)."],
    time="O(n)", space="O(n)",
    solution='''def countMaximalRectangles(heights):
    stack = []
    count = 0
    for h in heights + [0]:
        while stack and stack[-1] > h:
            stack.pop()
            count += 1
        if h > 0 and (not stack or stack[-1] < h):
            stack.append(h)
    return count
''',
    tests=[[[2, 1, 2]], [[2, 3, 2]], [[1]], [[0]], [[0, 0, 0]], [[2, 2, 2]], [[1, 2, 3, 4]], [[4, 3, 2, 1]], [[3, 0, 3]],
           [[2, 1, 2, 1, 2]], [[5, 3, 5, 3, 5, 0, 5]], [[10 ** 9, 10 ** 9]]],
)
_r = rnd(7705)
p["tests"].append([[_r.randint(0, 10 ** 9) for _ in range(8000)]])
p["tests"].append([[_r.randint(0, 5) for _ in range(8000)]])
p["tests"].append([[(i % 100) + 1 for i in range(9000)]])


def b_maxrects(heights):
    n = len(heights)
    c = 0
    for l in range(n):
        for r in range(l, n):
            m = min(heights[l:r + 1])
            if m > 0 and (l == 0 or heights[l - 1] < m) and (r == n - 1 or heights[r + 1] < m):
                c += 1
    return c


def v_maxrects(tests):
    for t in tests:
        h = t["args"][0]
        assert 1 <= len(h) <= 10000 and all(0 <= x <= 10 ** 9 for x in h)


CHECKS["count-maximal-histogram-rectangles"] = (b_maxrects, lambda r: [gen_arr(r, 0, 4, 1, 12)], "exact")
VALIDATE["count-maximal-histogram-rectangles"] = v_maxrects


p = add(
    id="largest-submatrix-with-column-reordering", title="Largest Submatrix After Reordering Columns", diff="Medium", topic=TOPIC, tier="extra",
    fn="largestReorderedSubmatrix", params=[("matrix", "int[][]")], ret="int", cmp="exact",
    desc="<p>A grid <code>matrix</code> contains only <code>0</code> and <code>1</code>. You may rearrange its <em>columns</em> in any order you like (each column moves as a whole; rows are not changed). After that, look for the largest rectangle of cells that are all <code>1</code>.</p><p>Return the largest area (number of cells) such a rectangle can have, over all possible column orders. Equivalently: choose a block of consecutive rows and a set of columns that are all <code>1</code> in every row of the block, and maximise rows times columns.</p><p>Example: <code>[[0,0,1],[1,1,1],[1,0,1]]</code> gives <code>4</code>: put the two columns that are <code>1</code> in the last two rows side by side to get a 2 by 2 block of ones.</p>",
    constraints=["1 &le; matrix.length, matrix[i].length &le; 80", "All rows have the same length", "matrix[i][j] is 0 or 1"],
    hints=["If the column order were fixed this would be the maximal rectangle of ones. Since you can reorder columns, which property of a column matters for a given bottom row?",
           "Fix the bottom row of the rectangle. Column <code>c</code> contributes a stack of consecutive ones of some height <code>h[c]</code> ending at that row, and only those heights matter.",
           "For a fixed bottom row, sort the heights in descending order. Taking the first <code>k</code> columns gives a rectangle of area <code>k * (k-th largest height)</code>; maximise over <code>k</code> and over all bottom rows."],
    editorial=["For every row <code>r</code> maintain <code>h[c]</code>: the number of consecutive ones in column <code>c</code> ending at row <code>r</code> (0 if the cell is 0). A rectangle whose bottom edge is on row <code>r</code> and which uses a set <code>S</code> of columns can have height <code>min(h[c] for c in S)</code>. Because the columns can be arranged freely, the set <code>S</code> does not need to be contiguous in the original grid.",
               "To use <code>k</code> columns the best choice is the <code>k</code> columns with the largest heights, giving area <code>k * (k-th largest of h)</code>. Sort <code>h</code> in descending order and evaluate every <code>k</code>. Doing this for each row costs O(C log C), so the whole algorithm is O(R * C log C) time and O(C) space; counting sort can bring it to O(R * C)."],
    time="O(R * C log C)", space="O(C)",
    solution='''def largestReorderedSubmatrix(matrix):
    cols = len(matrix[0])
    h = [0] * cols
    best = 0
    for row in matrix:
        for c in range(cols):
            h[c] = h[c] + 1 if row[c] == 1 else 0
        ordered = sorted(h, reverse=True)
        for k, height in enumerate(ordered):
            best = max(best, height * (k + 1))
    return best
''',
    tests=[[[[0, 0, 1], [1, 1, 1], [1, 0, 1]]], [[[1, 0, 1, 0, 1]]], [[[0]]], [[[1]]], [[[0, 0], [0, 0]]], [[[1, 1], [1, 1]]],
           [[[1], [1], [0], [1]]], [[[1, 0], [0, 1]]], [[[1, 1, 0], [0, 1, 1], [1, 1, 1]]], [[[1, 0, 1], [1, 1, 1], [0, 1, 1], [1, 1, 0]]]],
)
_r = rnd(7706)
p["tests"].append([_bin_grid(_r, 80, 80, 0.5)])
p["tests"].append([_bin_grid(_r, 80, 80, 0.9)])
p["tests"].append([[[1 if (j + i) % 3 else 0 for j in range(80)] for i in range(80)]])


def b_reorder(matrix):
    R, C = len(matrix), len(matrix[0])
    best = 0
    for r1 in range(R):
        for r2 in range(r1, R):
            cnt = sum(1 for c in range(C) if all(matrix[r][c] == 1 for r in range(r1, r2 + 1)))
            best = max(best, (r2 - r1 + 1) * cnt)
    return best


def g_reorder(r):
    return [_bin_grid(r, r.randint(1, 6), r.randint(1, 6), r.choice([0.3, 0.6, 0.85]))]


def v_reorder(tests):
    for t in tests:
        m = t["args"][0]
        assert 1 <= len(m) <= 80 and 1 <= len(m[0]) <= 80
        assert all(len(row) == len(m[0]) and all(v in (0, 1) for v in row) for row in m)


CHECKS["largest-submatrix-with-column-reordering"] = (b_reorder, g_reorder, "exact")
VALIDATE["largest-submatrix-with-column-reordering"] = v_reorder


p = add(
    id="count-submatrices-of-ones", title="Count Rectangles Made of Ones", diff="Medium", topic=TOPIC, tier="common",
    fn="countOneRectangles", params=[("matrix", "int[][]")], ret="int", cmp="exact",
    desc="<p>A grid <code>matrix</code> contains only <code>0</code> and <code>1</code>. Count the rectangles (sub-grids of consecutive rows and consecutive columns, with at least one cell) in which <em>every</em> cell is <code>1</code>. Rectangles at different positions are counted separately, even if they have the same size.</p><p>Example: <code>[[1,0,1],[1,1,0],[1,1,0]]</code> has <code>13</code> such rectangles: 6 single cells, 4 vertical dominoes... in total 13 once all sizes are added up (6 cells, 3 two-cell columns/rows pieces plus one 2 by 2 and further 3-cell and 4-cell/6-cell ones).</p>",
    constraints=["1 &le; matrix.length, matrix[i].length &le; 80", "All rows have the same length", "matrix[i][j] is 0 or 1"],
    hints=["Count rectangles by their bottom-right corner instead of all at once. For a fixed corner cell, how many rectangles end there?",
           "With <code>h[c]</code> = number of consecutive ones above and including each cell of the current row, the number of rectangles with bottom-right corner in column <code>c</code> is the sum over left edges <code>l &le; c</code> of <code>min(h[l..c])</code>.",
           "That sum can be kept with a monotonic stack: if <code>p</code> is the nearest column to the left with <code>h[p] &lt; h[c]</code>, then <code>cnt[c] = cnt[p] + h[c] * (c - p)</code> (or <code>h[c] * (c + 1)</code> when there is no such column)."],
    editorial=["Process the grid row by row, updating <code>h[c]</code>, the height of the column of ones that ends at the current row. Every all-ones rectangle has a unique bottom-right corner <code>(r, c)</code>. For a left edge <code>l</code> the rectangle can be any height from 1 up to <code>min(h[l..c])</code>, so the number of rectangles at that corner is <code>cnt[c] = sum over l &le; c of min(h[l..c])</code>.",
               "Let <code>p</code> be the nearest column left of <code>c</code> with <code>h[p] &lt; h[c]</code>. For left edges <code>l</code> in <code>(p, c]</code> the minimum is exactly <code>h[c]</code>, contributing <code>h[c] * (c - p)</code>; for left edges at or before <code>p</code> the minimum is the same as at corner <code>p</code>, contributing <code>cnt[p]</code>. A stack of increasing heights finds <code>p</code> in amortised O(1). Add <code>cnt[c]</code> over all cells to get the answer. Total time O(R * C), extra space O(C). The result is at most (80*81/2)<sup>2</sup>, which fits in 32 bits."],
    time="O(R * C)", space="O(C)",
    solution='''def countOneRectangles(matrix):
    cols = len(matrix[0])
    h = [0] * cols
    total = 0
    for row in matrix:
        for c in range(cols):
            h[c] = h[c] + 1 if row[c] == 1 else 0
        cnt = [0] * cols
        stack = []
        for c in range(cols):
            while stack and h[stack[-1]] >= h[c]:
                stack.pop()
            if stack:
                p = stack[-1]
                cnt[c] = cnt[p] + h[c] * (c - p)
            else:
                cnt[c] = h[c] * (c + 1)
            stack.append(c)
            total += cnt[c]
    return total
''',
    tests=[[[[1, 0, 1], [1, 1, 0], [1, 1, 0]]], [[[1, 1], [1, 1]]], [[[0]]], [[[1]]], [[[1, 1, 1]]], [[[1], [1], [1]]], [[[0, 0], [0, 0]]],
           [[[1, 0], [0, 1]]], [[[1, 1, 0, 1], [1, 1, 1, 1], [0, 1, 1, 1]]], [[[1, 0, 1, 1], [1, 1, 1, 1], [1, 1, 0, 1]]]],
)
_r = rnd(7707)
p["tests"].append([[[1] * 80 for _ in range(80)]])
p["tests"].append([_bin_grid(_r, 80, 80, 0.5)])
p["tests"].append([_bin_grid(_r, 80, 80, 0.92)])


def b_cnt(matrix):
    R, C = len(matrix), len(matrix[0])
    total = 0
    for r1 in range(R):
        for r2 in range(r1, R):
            for c1 in range(C):
                for c2 in range(c1, C):
                    if all(matrix[r][c] == 1 for r in range(r1, r2 + 1) for c in range(c1, c2 + 1)):
                        total += 1
    return total


def v_cnt(tests):
    for t in tests:
        m = t["args"][0]
        assert 1 <= len(m) <= 80 and 1 <= len(m[0]) <= 80
        assert all(len(row) == len(m[0]) and all(v in (0, 1) for v in row) for row in m)


CHECKS["count-submatrices-of-ones"] = (b_cnt, g_reorder, "exact")
VALIDATE["count-submatrices-of-ones"] = v_cnt


p = add(
    id="max-perimeter-rectangle-of-ones", title="Largest Perimeter Rectangle of Ones", diff="Medium", topic=TOPIC, tier="extra",
    fn="maxOnesPerimeter", params=[("matrix", "int[][]")], ret="int", cmp="exact",
    desc="<p>A grid <code>matrix</code> contains only <code>0</code> and <code>1</code>. Among all rectangles (blocks of consecutive rows and columns) whose cells are all <code>1</code>, find the one with the largest perimeter. A rectangle covering <code>h</code> rows and <code>w</code> columns has perimeter <code>2 * (h + w)</code>.</p><p>Return that largest perimeter, or <code>0</code> if the grid contains no <code>1</code>.</p><p>Example: <code>[[1,1,1,1],[0,1,0,0]]</code> has the 1 by 4 strip of ones, perimeter <code>10</code>; the best other choice is smaller. A grid with a single <code>1</code> returns <code>4</code>.</p>",
    constraints=["1 &le; matrix.length, matrix[i].length &le; 80", "All rows have the same length", "matrix[i][j] is 0 or 1"],
    hints=["Area-based answers do not apply here, but notice that enlarging a rectangle never decreases its perimeter. So only rectangles that cannot be enlarged matter.",
           "For each row as the bottom edge, let <code>h[c]</code> be the number of consecutive ones ending at that row in column <code>c</code>. A rectangle that cannot be enlarged has height equal to the smallest <code>h</code> in its column range.",
           "Run the histogram stack on each row. Whenever a bar of height <code>hh &gt; 0</code> is popped with block width <code>w</code>, evaluate <code>2 * (hh + w)</code> and keep the maximum."],
    editorial=["Any all-ones rectangle can be grown until it is maximal (it cannot grow up, down, left or right), and growing never reduces the perimeter, so an optimal rectangle can be assumed maximal. A maximal rectangle with bottom row <code>r</code> has a height equal to the minimum of <code>h[c]</code> over its columns, where <code>h</code> are the run heights ending at row <code>r</code>, and its columns form the widest block in which all <code>h[c]</code> are at least that minimum.",
               "That is exactly what the histogram stack produces: when a bar is popped, its height is the minimum of the block and the block's width is determined by the new stack top and the current index. Evaluate the perimeter <code>2 * (height + width)</code> for every pop with positive height, for every row, and return the maximum. Note that a wide, flat block can beat a tall, narrow one with a larger area, which is why we cannot just reuse the maximal-area answer. Time O(R * C), space O(C)."],
    time="O(R * C)", space="O(C)",
    solution='''def maxOnesPerimeter(matrix):
    cols = len(matrix[0])
    heights = [0] * (cols + 1)   # last slot is a 0 sentinel that flushes the stack
    best = 0
    for row in matrix:
        for c in range(cols):
            heights[c] = heights[c] + 1 if row[c] == 1 else 0
        stack = [-1]
        for c in range(cols + 1):
            while stack[-1] != -1 and heights[stack[-1]] >= heights[c]:
                h = heights[stack.pop()]
                if h > 0:
                    best = max(best, 2 * (h + c - stack[-1] - 1))
            stack.append(c)
    return best
''',
    tests=[[[[1, 1, 1, 1], [0, 1, 0, 0]]], [[[1]]], [[[0]]], [[[0, 0], [0, 0]]], [[[1, 1], [1, 1]]], [[[1, 0], [0, 1]]],
           [[[1], [1], [1], [0], [1]]], [[[1, 0, 1, 1, 1], [1, 0, 1, 1, 1], [1, 1, 1, 0, 0]]],
           [[[1, 1, 1], [1, 1, 1], [1, 0, 1]]], [[[1, 0, 0, 0, 1], [1, 1, 1, 1, 1], [1, 0, 0, 0, 1]]]],
)
_r = rnd(7708)
p["tests"].append([_bin_grid(_r, 80, 80, 0.5)])
p["tests"].append([_bin_grid(_r, 80, 80, 0.97)])
p["tests"].append([[[1 if i % 7 else 0 for j in range(80)] for i in range(80)]])


def b_perim(matrix):
    R, C = len(matrix), len(matrix[0])
    best = 0
    for r1 in range(R):
        for r2 in range(r1, R):
            for c1 in range(C):
                for c2 in range(c1, C):
                    if all(matrix[r][c] == 1 for r in range(r1, r2 + 1) for c in range(c1, c2 + 1)):
                        best = max(best, 2 * ((r2 - r1 + 1) + (c2 - c1 + 1)))
    return best


def v_perim(tests):
    for t in tests:
        m = t["args"][0]
        assert 1 <= len(m) <= 80 and 1 <= len(m[0]) <= 80
        assert all(len(row) == len(m[0]) and all(v in (0, 1) for v in row) for row in m)


CHECKS["max-perimeter-rectangle-of-ones"] = (b_perim, g_reorder, "exact")
VALIDATE["max-perimeter-rectangle-of-ones"] = v_perim


p = add(
    id="longest-window-meeting-floor-area", title="Longest Window With a Large Floor Area", diff="Medium", topic=TOPIC, tier="extra",
    fn="longestWindowFloorArea", params=[("heights", "int[]"), ("k", "int")], ret="int", cmp="exact",
    desc="<p>Bars of width 1 stand in a row with heights <code>heights[i]</code>. The <em>floor area</em> of a block of consecutive bars is the height of its shortest bar multiplied by the number of bars in the block (the largest rectangle that fits in the block along its full length).</p><p>Given an integer <code>k</code>, return the largest number of bars in a block whose floor area is at least <code>k</code>. If no block qualifies, return <code>0</code>.</p><p>Example: <code>heights = [6, 5, 6, 5, 1, 7]</code> and <code>k = 20</code>. The first four bars have floor area <code>5 * 4 = 20</code>, so the answer is <code>4</code>. No block of 5 bars qualifies because it would contain the bar of height 1 or fewer than five good bars.</p>",
    constraints=["1 &le; heights.length &le; 10,000", "1 &le; heights[i] &le; 10<sup>9</sup>", "1 &le; k &le; 2<sup>31</sup> - 1"],
    hints=["Checking every block is O(n<sup>2</sup>) (or O(n<sup>3</sup>) if you recompute minima). Which blocks are worth looking at?",
           "If a block has minimum <code>m</code> and length <code>t</code>, extend it as far as possible while all bars stay at least <code>m</code>. The floor area does not decrease and the length does not shrink.",
           "So only the maximal blocks around each bar (bounded by the nearest strictly shorter bars) matter: take every bar with <code>height * reach_width &ge; k</code> and return the largest such width. Find the widths with a monotonic stack."],
    editorial=["Suppose a block has minimum height <code>m</code> and length <code>t</code> with <code>m * t &ge; k</code>. Take a bar of height <code>m</code> inside it and widen the block to the largest block around that bar in which all bars are at least <code>m</code>, with width <code>w &ge; t</code>. Its floor area is at least <code>m * w &ge; m * t &ge; k</code>, so it also qualifies and is not shorter. Hence the answer is the maximum width <code>w</code> of such a maximal block over all bars with <code>height * w &ge; k</code>.",
               "Conversely, such a maximal block of width <code>w</code> has minimum at least the bar's height, so its floor area is at least <code>height * w &ge; k</code>, i.e. it really qualifies. Compute the widths for all bars with the nearest-strictly-shorter-bar stack passes, then take the maximum over qualifying bars (0 if none). Time O(n), space O(n)."],
    time="O(n)", space="O(n)",
    solution='''def longestWindowFloorArea(heights, k):
    n = len(heights)
    left = [-1] * n
    right = [n] * n
    stack = []
    for i in range(n):
        while stack and heights[stack[-1]] >= heights[i]:
            stack.pop()
        left[i] = stack[-1] if stack else -1
        stack.append(i)
    stack = []
    for i in range(n - 1, -1, -1):
        while stack and heights[stack[-1]] >= heights[i]:
            stack.pop()
        right[i] = stack[-1] if stack else n
        stack.append(i)
    best = 0
    for i in range(n):
        width = right[i] - left[i] - 1
        if heights[i] * width >= k:
            best = max(best, width)
    return best
''',
    tests=[[[6, 5, 6, 5, 1, 7], 20], [[1, 3, 4, 3, 1], 9], [[5], 5], [[5], 6], [[2, 2, 2, 2], 8], [[2, 2, 2, 2], 9],
           [[1, 1, 1, 1, 1], 1], [[10 ** 9, 10 ** 9], 2 * 10 ** 9], [[10 ** 9, 1, 10 ** 9], 10 ** 9], [[4, 1, 4, 1, 4], 4],
           [[3, 6, 2, 8, 8, 2, 6, 3], 16]],
)
_r = rnd(7709)
_a = [_r.randint(1, 10 ** 9) for _ in range(8000)]
p["tests"].append([_a, 10 ** 9])
_a = [_r.randint(1000, 5000) for _ in range(8000)]
p["tests"].append([_a, 4000 * 3000])
_a = [_r.randint(1, 50) for _ in range(8000)]
p["tests"].append([_a, 200000])


def b_floor(heights, k):
    n = len(heights)
    best = 0
    for l in range(n):
        m = 10 ** 18
        for r in range(l, n):
            m = min(m, heights[r])
            if m * (r - l + 1) >= k:
                best = max(best, r - l + 1)
    return best


def g_floor(r):
    h = gen_arr(r, 1, 6, 1, 10)
    return [h, r.randint(1, 30)]


def v_floor(tests):
    for t in tests:
        h, k = t["args"]
        assert 1 <= len(h) <= 10000 and all(1 <= x <= 10 ** 9 for x in h) and 1 <= k <= INT_MAX


CHECKS["longest-window-meeting-floor-area"] = (b_floor, g_floor, "exact")
VALIDATE["longest-window-meeting-floor-area"] = v_floor


# ====================================================================== HARD

p = add(
    id="largest-rectangle-under-skyline-buildings", title="Largest Rectangle Under a City Skyline", diff="Hard", topic=TOPIC, tier="extra",
    fn="largestSkylineRectangle", params=[("buildings", "int[][]")], ret="int", cmp="exact",
    desc="<p>Each building is described by <code>buildings[i] = [left, right, height]</code>: it occupies the x-range from <code>left</code> to <code>right</code> (so its width is <code>right - left</code>) and rises from the ground (y = 0) to <code>height</code>. Buildings may overlap or touch. The <em>skyline</em> is the region under the highest building at every x; places covered by no building have height 0.</p><p>Return the area of the largest axis-aligned rectangle that fits entirely inside this skyline region.</p><p>Example: <code>[[0,4,2],[2,6,3],[5,9,1]]</code>. The skyline has height 2 on [0,2], 3 on [2,6] (the second building covers the first there), and 3 until x=6, then 1 on [6,9]. The best rectangle is x in [2,6] with height 3... or x in [0,9] with height 1, area 9; the largest is <code>12</code> (x from 0 to 6 at height 2).</p>",
    constraints=["1 &le; buildings.length &le; 2,000", "buildings[i].length == 3", "0 &le; left &lt; right &le; 100,000", "1 &le; height &le; 10,000", "The answer fits in a signed 32-bit integer (it is at most 10<sup>9</sup>)"],
    hints=["First turn the overlapping buildings into a skyline: a list of consecutive x-segments, each with a single height. Coordinates are large, so work with the building edges only.",
           "Sweep the sorted x-coordinates of all edges. For each segment between two neighbouring edges, the height is the maximum height among the buildings that cover it (a max-heap with lazy removal of buildings that have ended works well).",
           "Now it is the classic largest rectangle in a histogram, except that bars have different widths: keep a stack of (start x, height); when a lower segment arrives, pop and compute <code>height * (x - start)</code>, then push the lower segment with the popped start."],
    editorial=["Any rectangle inside the skyline can be slid down to the ground, so we only need rectangles that sit on y = 0. Their area is limited by the lowest part of the skyline over their x-range, which is a largest-rectangle-in-a-histogram problem, with bars of variable width because the skyline has long flat stretches.",
               "Step 1: collect all distinct edge coordinates and sort them. Sweep them left to right; push the buildings whose left edge is at or before the current x into a max-heap keyed by height; discard from the top of the heap buildings whose right edge is not beyond the current x; the height of the segment starting here is the top of the heap or 0. Step 2: run the histogram stack on the segments, storing (start x, height); when a segment of height <code>h</code> arrives, pop every entry with height &ge; <code>h</code>, record <code>height * (x - start)</code>, and push <code>h</code> at the smallest start that was popped. A final sentinel of height 0 flushes the stack. With E = 2n edges, the sweep costs O(n log n) and the stack pass O(n)."],
    time="O(n log n)", space="O(n)",
    solution='''import heapq


def largestSkylineRectangle(buildings):
    xs = sorted({x for l, r, h in buildings for x in (l, r)})
    order = sorted(buildings)
    heap = []
    j = 0
    segments = []
    for k in range(len(xs) - 1):
        x = xs[k]
        while j < len(order) and order[j][0] <= x:
            heapq.heappush(heap, (-order[j][2], order[j][1]))
            j += 1
        while heap and heap[0][1] <= x:
            heapq.heappop(heap)
        height = -heap[0][0] if heap else 0
        segments.append((x, height))
    segments.append((xs[-1], 0))   # sentinel: ground level after the last edge
    stack = []   # (start x, height) with increasing heights
    best = 0
    for x, height in segments:
        start = x
        while stack and stack[-1][1] >= height:
            s, h = stack.pop()
            best = max(best, h * (x - s))
            start = s
        stack.append((start, height))
    return best
''',
    tests=[[[[0, 4, 2], [2, 6, 3], [5, 9, 1]]], [[[0, 5, 3]]], [[[0, 1, 1]]], [[[0, 2, 5], [2, 4, 5]]], [[[0, 2, 4], [3, 5, 4]]],
           [[[0, 10, 1], [4, 6, 9]]], [[[0, 3, 3], [1, 2, 8]]], [[[0, 6, 2], [0, 3, 5], [3, 6, 5]]],
           [[[1, 4, 2], [2, 3, 6], [3, 8, 4], [7, 9, 4]]], [[[0, 100000, 10000]]], [[[0, 5, 1], [1, 4, 2], [2, 3, 3]]]],
)
_r = rnd(7710)


def _rand_buildings(r, count, X, H, maxw):
    out = []
    for _ in range(count):
        l = r.randint(0, X - 1)
        out.append([l, min(X, l + r.randint(1, maxw)), r.randint(1, H)])
    return out


p["tests"].append([_rand_buildings(_r, 1500, 100000, 10000, 3000)])
p["tests"].append([_rand_buildings(_r, 1500, 100000, 10000, 80000)])
p["tests"].append([[[i * 50, i * 50 + 50 + _r.randint(0, 60), _r.randint(5000, 10000)] for i in range(1800)]])


def b_skyline(buildings):
    X = max(r for l, r, h in buildings)
    sky = [0] * X
    for l, r, h in buildings:
        for x in range(l, r):
            sky[x] = max(sky[x], h)
    best = 0
    for a in range(X):
        m = 10 ** 9
        for b in range(a, X):
            m = min(m, sky[b])
            best = max(best, m * (b - a + 1))
    return best


def g_skyline(r):
    return [_rand_buildings(r, r.randint(1, 6), r.choice([6, 12]), r.choice([3, 8]), 6)]


def v_skyline(tests):
    for t in tests:
        b = t["args"][0]
        assert 1 <= len(b) <= 2000
        for l, r, h in b:
            assert 0 <= l < r <= 100000 and 1 <= h <= 10000
        assert 0 <= t["expected"] <= 10 ** 9


CHECKS["largest-rectangle-under-skyline-buildings"] = (b_skyline, g_skyline, "exact")
VALIDATE["largest-rectangle-under-skyline-buildings"] = v_skyline


p = add(
    id="largest-uniform-rectangle-in-grid", title="Largest Rectangle of Equal Values", diff="Hard", topic=TOPIC, tier="extra",
    fn="largestUniformRectangle", params=[("grid", "int[][]")], ret="int", cmp="exact",
    desc="<p>A grid <code>grid</code> holds small non-negative integers (think of colours). Find the largest axis-aligned rectangle of consecutive rows and columns in which <em>all cells have the same value</em>, and return its area (number of cells). Any value may be used, but all cells of the rectangle must share it.</p><p>Example: <code>[[1,1,2],[1,1,2],[3,2,2]]</code> returns <code>4</code> (the 2 by 2 block of ones; the twos form an L-shaped region whose largest rectangle has only 2 cells... the column of twos in the top two rows).</p>",
    constraints=["1 &le; grid.length, grid[i].length &le; 80", "All rows have the same length", "0 &le; grid[i][j] &le; 100"],
    hints=["For a single value this is the maximal rectangle of ones problem. You could run it once per value, but the values may be many. Can one sweep handle all of them?",
           "For each cell keep <code>up[r][c]</code>: how many cells directly above it (including itself) have the same value as the cell. This is the histogram height for a rectangle whose bottom edge is on row <code>r</code>.",
           "In row <code>r</code> a rectangle can only use adjacent columns that hold the same value in that row. Split the row into runs of equal values and solve the histogram stack separately inside each run, using <code>up[r][c]</code> as the bar heights."],
    editorial=["Let <code>up[r][c]</code> be the length of the vertical run of equal values ending at <code>(r, c)</code>: <code>up[r][c] = up[r-1][c] + 1</code> if <code>grid[r][c] == grid[r-1][c]</code>, else 1. A uniform rectangle whose bottom row is <code>r</code> and whose columns are <code>c1..c2</code> needs <code>grid[r][c1] == ... == grid[r][c2]</code>, and its height can be at most <code>min(up[r][c1..c2])</code> because each column's cells above must equal the bottom cell. Because the bottom cells are equal, all the cells of the rectangle share one value.",
               "So for each row cut the columns into maximal runs of equal values and run the largest-rectangle-in-histogram stack on <code>up[r][c]</code> within each run. Take the maximum area over all rows and runs. Every cell is handled a constant number of times: O(R * C) time and O(C) extra space. A grid with one value reduces to the plain full rectangle <code>R * C</code>."],
    time="O(R * C)", space="O(C)",
    solution='''def largestUniformRectangle(grid):
    rows, cols = len(grid), len(grid[0])
    up = [0] * cols
    prev = [None] * cols
    best = 0
    for r in range(rows):
        row = grid[r]
        for c in range(cols):
            up[c] = up[c] + 1 if prev[c] == row[c] else 1
        prev = row
        c = 0
        while c < cols:
            e = c
            while e + 1 < cols and row[e + 1] == row[c]:
                e += 1
            # largest rectangle in histogram up[c..e]
            stack = []
            for i in range(c, e + 2):
                h = up[i] if i <= e else 0
                start = i
                while stack and stack[-1][1] >= h:
                    s, sh = stack.pop()
                    best = max(best, sh * (i - s))
                    start = s
                stack.append((start, h))
            c = e + 1
    return best
''',
    tests=[[[[1, 1, 2], [1, 1, 2], [3, 2, 2]]], [[[7]]], [[[1, 2], [3, 4]]], [[[5, 5], [5, 5]]], [[[1, 1, 1, 1]]], [[[1], [1], [2], [2], [2]]],
           [[[1, 2, 1], [2, 1, 2], [1, 2, 1]]], [[[3, 3, 3], [3, 0, 3], [3, 3, 3]]], [[[1, 1, 2, 2], [1, 1, 2, 2], [3, 3, 2, 2]]],
           [[[0, 0, 1, 1, 1], [0, 0, 1, 1, 1], [1, 1, 1, 1, 1]]]],
)
_r = rnd(7711)
p["tests"].append([[[_r.randint(0, 1) for _ in range(80)] for _ in range(80)]])
p["tests"].append([[[(i // 20 + j // 25) % 3 if _r.random() < 0.95 else _r.randint(0, 100) for j in range(80)] for i in range(80)]])
p["tests"].append([[[_r.randint(0, 100) for _ in range(80)] for _ in range(80)]])


def b_uniform(grid):
    R, C = len(grid), len(grid[0])
    best = 0
    for r1 in range(R):
        for r2 in range(r1, R):
            for c1 in range(C):
                for c2 in range(c1, C):
                    v = grid[r1][c1]
                    if all(grid[r][c] == v for r in range(r1, r2 + 1) for c in range(c1, c2 + 1)):
                        best = max(best, (r2 - r1 + 1) * (c2 - c1 + 1))
    return best


def g_uniform(r):
    R, C = r.randint(1, 6), r.randint(1, 6)
    k = r.choice([1, 2, 3])
    return [[[r.randint(0, k) for _ in range(C)] for _ in range(R)]]


def v_uniform(tests):
    for t in tests:
        g = t["args"][0]
        assert 1 <= len(g) <= 80 and 1 <= len(g[0]) <= 80
        assert all(len(row) == len(g[0]) and all(0 <= v <= 100 for v in row) for row in g)


CHECKS["largest-uniform-rectangle-in-grid"] = (b_uniform, g_uniform, "exact")
VALIDATE["largest-uniform-rectangle-in-grid"] = v_uniform
