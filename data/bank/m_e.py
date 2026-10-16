"""Problems: matrix-free math and geometry on integers. See data/lib.py for the registry."""
import math
from fractions import Fraction
from itertools import combinations

from lib import add, rnd, CHECKS, VALIDATE, gen_arr  # noqa: F401

MOD = 1000000007


def _hull(points):
    """Strict convex hull (Andrew's monotone chain), counter-clockwise, no collinear corners."""
    pts = sorted(set(tuple(p) for p in points))
    if len(pts) < 3:
        return [list(p) for p in pts]

    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

    lower = []
    for q in pts:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], q) <= 0:
            lower.pop()
        lower.append(q)
    upper = []
    for q in reversed(pts):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], q) <= 0:
            upper.pop()
        upper.append(q)
    return [list(q) for q in lower[:-1] + upper[:-1]]


# ---------------------------------------------------------------- EASY

p = add(
    id="lattice-points-on-segment", title="Lattice Points on a Segment", diff="Easy", topic="Math & Bit Manipulation",
    fn="latticePointsOnSegment", params=[("x1", "int"), ("y1", "int"), ("x2", "int"), ("y2", "int")], ret="int", cmp="exact",
    desc="<p>Two endpoints <code>(x1, y1)</code> and <code>(x2, y2)</code> of a segment are given with integer coordinates. A <em>lattice point</em> is a point whose two coordinates are both integers. Count the lattice points that lie on the segment, including both endpoints.</p><p>If both endpoints are the same point, the answer is 1.</p><pre>(0,0) to (4,2)  -> 3   (the points (0,0), (2,1), (4,2))\n(0,0) to (3,5)  -> 2   (only the endpoints)\n(1,1) to (1,1)  -> 1</pre>",
    constraints=["-10<sup>9</sup> &le; x1, y1, x2, y2 &le; 10<sup>9</sup>"],
    hints=["Consider the vector from the first endpoint to the second. Between two consecutive lattice points on the segment, the step is the smallest whole-number step in that direction.",
           "Divide both components of the vector by their greatest common divisor. The result is the smallest step that stays on the lattice.",
           "The lattice points are the first endpoint plus <code>k</code> copies of that step, for <code>k</code> from 0 to the gcd. That gives gcd + 1 points."],
    editorial=["The vector from <code>(x1, y1)</code> to <code>(x2, y2)</code> is <code>(dx, dy)</code>. Let <code>g = gcd(|dx|, |dy|)</code>. The vector <code>(dx / g, dy / g)</code> is a lattice step, and every lattice point on the segment is reached from the start by a whole number of such steps. Going from 0 to <code>g</code> steps therefore gives <code>g + 1</code> points, endpoints included.",
               "When both components are 0 the gcd is 0 and the formula gives 1, which is right because the two endpoints coincide. Python's <code>math.gcd</code> handles zero arguments correctly."],
    time="O(log C)", space="O(1)",
    solution='''import math

def latticePointsOnSegment(x1, y1, x2, y2):
    return math.gcd(abs(x2 - x1), abs(y2 - y1)) + 1
''',
    tests=[[0, 0, 4, 2], [0, 0, 3, 5], [1, 1, 1, 1], [0, 0, 0, 6], [-3, -3, 3, 3], [2, 5, -4, 5], [0, 0, 6, 9],
           [12, 18, -30, -45], [-1000000000, -1000000000, 1000000000, 1000000000],
           [0, -1000000000, 0, 1000000000], [-1000000000, 0, 1000000000, 1000000000]],
)


def b_segment(x1, y1, x2, y2):
    cnt = 0
    for x in range(min(x1, x2), max(x1, x2) + 1):
        for y in range(min(y1, y2), max(y1, y2) + 1):
            if (x2 - x1) * (y - y1) - (y2 - y1) * (x - x1) == 0:
                cnt += 1
    return cnt


def v_segment(tests):
    for t in tests:
        assert all(-10 ** 9 <= v <= 10 ** 9 for v in t["args"])


CHECKS["lattice-points-on-segment"] = (b_segment, lambda r: [r.randint(-6, 6) for _ in range(4)], "exact")
VALIDATE["lattice-points-on-segment"] = v_segment

p = add(
    id="grid-cells-crossed-by-diagonal", tier="extra", title="Cells Crossed by a Diagonal", diff="Easy", topic="Math & Bit Manipulation",
    fn="cellsCrossed", params=[("w", "int"), ("h", "int")], ret="int", cmp="exact",
    desc="<p>A rectangle is tiled by unit squares: <code>w</code> columns and <code>h</code> rows. Draw a straight line from the bottom-left corner <code>(0, 0)</code> to the top-right corner <code>(w, h)</code>. Count the unit squares whose interior the line passes through.</p><p>A line that only touches a square at a corner does not count that square.</p><pre>w = 2, h = 3  -> 4\nw = 4, h = 2  -> 4\nw = 3, h = 3  -> 3</pre>",
    constraints=["1 &le; w, h &le; 10<sup>9</sup>"],
    hints=["Start in the bottom-left square. Each time the line crosses a vertical or horizontal grid line, it enters a new square.",
           "Count the vertical grid lines crossed (w - 1 of them) and the horizontal ones (h - 1). Then add the starting square.",
           "Where the line passes exactly through a lattice corner, it crosses a vertical and a horizontal line at once and enters only one new square. How many such corners are there in between?"],
    editorial=["Start with the first square. The line crosses each of the <code>w - 1</code> interior vertical grid lines once and each of the <code>h - 1</code> interior horizontal grid lines once, and each crossing enters a new square. That gives <code>1 + (w - 1) + (h - 1) = w + h - 1</code> squares.",
               "A crossing where the line meets a grid corner counts as one vertical and one horizontal crossing at the same time, so it enters only one new square and must be subtracted once. The line passes through <code>gcd(w, h) - 1</code> such inner corners. The answer is therefore <code>w + h - gcd(w, h)</code>.",
               "This is O(log(w + h)) because of the gcd. A brute force walk along the line gives the same value and is used to check the formula on small inputs."],
    time="O(log(min(w, h)))", space="O(1)",
    solution='''import math

def cellsCrossed(w, h):
    return w + h - math.gcd(w, h)
''',
    tests=[[2, 3], [4, 2], [3, 3], [1, 1], [1, 7], [7, 1], [6, 4], [12, 18], [1000000000, 1],
           [1000000000, 1000000000], [999999937, 999999929], [1000000000, 999999999]],
)


def b_cells(w, h):
    bps = {Fraction(0), Fraction(1)}
    for k in range(1, w):
        bps.add(Fraction(k, w))
    for k in range(1, h):
        bps.add(Fraction(k, h))
    bps = sorted(bps)
    cells = set()
    for a, b in zip(bps, bps[1:]):
        t = (a + b) / 2
        cells.add((math.floor(t * w), math.floor(t * h)))
    return len(cells)


def v_cells(tests):
    for t in tests:
        w, h = t["args"]
        assert 1 <= w <= 10 ** 9 and 1 <= h <= 10 ** 9


CHECKS["grid-cells-crossed-by-diagonal"] = (b_cells, lambda r: [r.randint(1, 8), r.randint(1, 8)], "exact")
VALIDATE["grid-cells-crossed-by-diagonal"] = v_cells

# ---------------------------------------------------------------- MEDIUM

p = add(
    id="total-manhattan-distance-pairs", title="Total Manhattan Distance of All Pairs", diff="Medium", topic="Math & Bit Manipulation",
    fn="totalManhattan", params=[("points", "int[][]")], ret="int", cmp="exact",
    desc="<p>You are given <code>points</code>, an array of integer points <code>[x, y]</code>. Points may repeat. The Manhattan distance between two points is <code>|x1 - x2| + |y1 - y2|</code>.</p><p>Return the sum of the Manhattan distances over all pairs <code>i &lt; j</code>, taken modulo <code>1,000,000,007</code>. Trying every pair directly is too slow for large inputs.</p><pre>points = [[0,0],[1,2],[3,1]]\npairs: (0,0)-(1,2) = 3,  (0,0)-(3,1) = 4,  (1,2)-(3,1) = 3\nresult = 10</pre>",
    constraints=["1 &le; points.length &le; 100,000", "points[i].length = 2", "-10<sup>9</sup> &le; x, y &le; 10<sup>9</sup>"],
    hints=["The absolute difference splits into an x part and a y part, and the two parts can be summed separately.",
           "For one list of numbers, the sum of all pairwise absolute differences becomes easy once the list is sorted. Sort the x values and the y values.",
           "In a sorted list <code>a[0..n-1]</code>, the value <code>a[i]</code> is the larger element of <code>i</code> pairs and the smaller element of <code>n - 1 - i</code> pairs. Its net weight is <code>2i - (n - 1)</code>."],
    editorial=["For a fixed pair, <code>|x1 - x2| + |y1 - y2|</code> is the x contribution plus the y contribution. So the total is the sum over all pairs of the x differences, plus the same sum over the y values.",
               "Sort a list of values <code>a</code>. Each value <code>a[i]</code> appears as the larger member of <code>i</code> pairs (with a smaller earlier element), contributing <code>+a[i]</code> each time, and as the smaller member of <code>n - 1 - i</code> pairs, contributing <code>-a[i]</code> each time. Summing gives <code>sum(a[i] * (2i - (n - 1)))</code>.",
               "Sorting costs O(n log n) and the rest is linear. Python's integers do not overflow, so the sum can be reduced modulo 1,000,000,007 once at the end."],
    time="O(n log n)", space="O(n)",
    solution='''def totalManhattan(points):
    MOD = 1000000007
    n = len(points)
    total = 0
    for arr in ([p[0] for p in points], [p[1] for p in points]):
        arr.sort()
        for i, v in enumerate(arr):
            total += v * (2 * i - (n - 1))
    return total % MOD
''',
    tests=[[[[0, 0], [1, 2], [3, 1]]], [[[5, 5]]], [[[0, 0], [0, 0]]], [[[-1, -1], [1, 1]]],
           [[[1000000000, -1000000000], [-1000000000, 1000000000]]], [[[2, 7], [2, 7], [2, 7], [9, -3]]],
           [[[-6, 4], [3, -2], [0, 0], [5, 5], [-1, 3]]]],
)
_r = rnd(401)
_pts = [[_r.randint(-10 ** 9, 10 ** 9), _r.randint(-10 ** 9, 10 ** 9)] for _ in range(2000)]
p["tests"].append([_pts])
_pts = [[_r.randint(-1000, 1000), _r.randint(-1000, 1000)] for _ in range(3000)]
p["tests"].append([_pts])


def b_manhattan(points):
    t = 0
    for i in range(len(points)):
        for j in range(i + 1, len(points)):
            t += abs(points[i][0] - points[j][0]) + abs(points[i][1] - points[j][1])
    return t % 1000000007


def g_manhattan(r):
    return [[[r.randint(-6, 6), r.randint(-6, 6)] for _ in range(r.randint(1, 7))]]


def v_manhattan(tests):
    for t in tests:
        pts = t["args"][0]
        assert 1 <= len(pts) <= 100000
        assert all(len(q) == 2 and -10 ** 9 <= q[0] <= 10 ** 9 and -10 ** 9 <= q[1] <= 10 ** 9 for q in pts)


CHECKS["total-manhattan-distance-pairs"] = (b_manhattan, g_manhattan, "exact")
VALIDATE["total-manhattan-distance-pairs"] = v_manhattan

p = add(
    id="lattice-points-in-circle", tier="extra", title="Lattice Points in a Circle", diff="Medium", topic="Math & Bit Manipulation",
    fn="latticePointsInCircle", params=[("r", "int")], ret="int", cmp="exact",
    desc="<p>Count the points <code>(x, y)</code> with integer coordinates that lie inside or on the circle of radius <code>r</code> centred at the origin, that is, the points with <code>x<sup>2</sup> + y<sup>2</sup> &le; r<sup>2</sup></code>.</p><pre>r = 0 -> 1\nr = 1 -> 5    ((0,0), (1,0), (-1,0), (0,1), (0,-1))\nr = 2 -> 13</pre>",
    constraints=["0 &le; r &le; 10,000"],
    hints=["Fix the x coordinate. Which y values are allowed for it?",
           "For a fixed x, the allowed y values form a symmetric range around 0. Its half-width is the largest integer y with <code>y<sup>2</sup> &le; r<sup>2</sup> - x<sup>2</sup></code>.",
           "That half-width is <code>isqrt(r*r - x*x)</code>, which gives <code>2 * isqrt + 1</code> points in that column. Sum over every x from -r to r."],
    editorial=["Iterate over every column <code>x</code> from <code>-r</code> to <code>r</code>. In that column, a point <code>(x, y)</code> is inside the circle exactly when <code>|y| &le; floor(sqrt(r<sup>2</sup> - x<sup>2</sup>))</code>. There are <code>2 * floor(...) + 1</code> such integers y, counting 0.",
               "Use <code>math.isqrt</code> rather than floating-point <code>sqrt</code>: it is exact for integers, and float rounding would miscount points on the boundary when r is large. The loop has 2r + 1 steps, which is at most about 20,000 here.",
               "This is the Gauss circle problem. The count is close to pi times r squared, but the exact value has no simple closed form, so counting column by column is the practical method."],
    time="O(r)", space="O(1)",
    solution='''import math

def latticePointsInCircle(r):
    r2 = r * r
    total = 0
    for x in range(-r, r + 1):
        total += 2 * math.isqrt(r2 - x * x) + 1
    return total
''',
    tests=[[0], [1], [2], [3], [5], [10], [100], [300], [4000], [9999], [10000]],
)


def b_circle(r):
    return sum(1 for x in range(-r, r + 1) for y in range(-r, r + 1) if x * x + y * y <= r * r)


def v_circle(tests):
    for t in tests:
        assert 0 <= t["args"][0] <= 10000


CHECKS["lattice-points-in-circle"] = (b_circle, lambda r: [r.randint(0, 15)], "exact")
VALIDATE["lattice-points-in-circle"] = v_circle

p = add(
    id="axis-rectangles-from-points", title="Axis-Aligned Rectangles From Points", diff="Medium", topic="Math & Bit Manipulation",
    fn="countAxisRectangles", params=[("points", "int[][]")], ret="int", cmp="exact",
    desc="<p>Each element of <code>points</code> is a distinct point <code>[x, y]</code>. Count the axis-aligned rectangles of positive area whose four corners are all points of the array. The sides of every such rectangle are parallel to the axes.</p><p>Each rectangle is counted once.</p><pre>points = [[0,0],[0,1],[1,0],[1,1],[2,0],[2,1]]\nrectangles: x in {0,1} with y in {0,1}; x in {0,2} with y in {0,1}; x in {1,2} with y in {0,1}\nresult = 3</pre>",
    constraints=["1 &le; points.length &le; 600", "points[i].length = 2", "-10<sup>9</sup> &le; x, y &le; 10<sup>9</sup>", "All points are distinct"],
    hints=["A rectangle is fixed by its bottom-left and top-right corners. Those two corners determine the other two.",
           "Take every pair of points where one is strictly lower-left of the other. The rectangle is valid exactly when the other two corners, top-left and bottom-right, are also in the set.",
           "Sort the points so each pair is visited once, and use a hash set for the membership tests."],
    editorial=["Any axis-aligned rectangle has a unique bottom-left corner <code>(x1, y1)</code> and top-right corner <code>(x2, y2)</code> with <code>x1 &lt; x2</code> and <code>y1 &lt; y2</code>. Its other corners are <code>(x1, y2)</code> and <code>(x2, y1)</code>. So each rectangle is found by exactly one such diagonal pair.",
               "Put the points in a set and sort them. For each pair <code>i &lt; j</code> in sorted order, the second point has the larger x or the same x with a larger y. Keep the pairs with <code>x2 &gt; x1</code> and <code>y2 &gt; y1</code>, then check the two remaining corners in the set.",
               "With n points there are O(n<sup>2</sup>) pairs and each check is a constant-time set lookup, which is fast enough for n up to 600. Counting per column pair would be faster for dense inputs, but it is not needed here."],
    time="O(n<sup>2</sup>)", space="O(n)",
    solution='''def countAxisRectangles(points):
    pts = set((x, y) for x, y in points)
    ps = sorted(pts)
    count = 0
    for i in range(len(ps)):
        x1, y1 = ps[i]
        for j in range(i + 1, len(ps)):
            x2, y2 = ps[j]
            if x2 > x1 and y2 > y1 and (x1, y2) in pts and (x2, y1) in pts:
                count += 1
    return count
''',
    tests=[[[[0, 0], [0, 1], [1, 0], [1, 1], [2, 0], [2, 1]]], [[[0, 0]]], [[[0, 0], [1, 1]]],
           [[[0, 0], [0, 1], [1, 0], [1, 1]]], [[[1, 1], [1, 5], [4, 1], [4, 5], [2, 3]]],
           [[[-1000000000, -1000000000], [1000000000, 1000000000], [-1000000000, 1000000000], [1000000000, -1000000000]]],
           [[[0, 0], [0, 2], [2, 0], [2, 2], [1, 0], [1, 2], [0, 1], [2, 1], [1, 1]]]],
)
_grid = [[x, y] for x in range(25) for y in range(24)]
p["tests"].append([_grid])
_r = rnd(402)
_pts = [list(q) for q in _r.sample([(x, y) for x in range(41) for y in range(41)], 500)]
p["tests"].append([_pts])


def b_rect(points):
    pts = set(tuple(q) for q in points)
    xs = sorted(set(q[0] for q in pts))
    ys = sorted(set(q[1] for q in pts))
    c = 0
    for a in range(len(xs)):
        for b in range(a + 1, len(xs)):
            for u in range(len(ys)):
                for v in range(u + 1, len(ys)):
                    if all(q in pts for q in [(xs[a], ys[u]), (xs[a], ys[v]), (xs[b], ys[u]), (xs[b], ys[v])]):
                        c += 1
    return c


def g_rect(r):
    cells = [[x, y] for x in range(5) for y in range(5)]
    return [r.sample(cells, r.randint(1, 12))]


def v_rect(tests):
    for t in tests:
        pts = t["args"][0]
        assert 1 <= len(pts) <= 600
        assert len(set(tuple(q) for q in pts)) == len(pts), "points must be distinct"
        assert all(-10 ** 9 <= x <= 10 ** 9 and -10 ** 9 <= y <= 10 ** 9 for x, y in pts)


CHECKS["axis-rectangles-from-points"] = (b_rect, g_rect, "exact")
VALIDATE["axis-rectangles-from-points"] = v_rect

# ---------------------------------------------------------------- HARD

_circ = _hull([[round(300 * math.cos(2 * math.pi * k / 600)), round(300 * math.sin(2 * math.pi * k / 600))] for k in range(600)])
_r = rnd(403)
_rand_hull = _hull([[_r.randint(-1000, 1000), _r.randint(-1000, 1000)] for _ in range(3000)])

p = add(
    id="lattice-points-inside-convex-polygon", tier="extra", title="Lattice Points Inside a Convex Polygon", diff="Hard", topic="Math & Bit Manipulation",
    fn="interiorLatticePoints", params=[("vertices", "int[][]")], ret="int", cmp="exact",
    desc="<p>The array <code>vertices</code> lists the corners of a convex polygon whose corners have integer coordinates. The corners appear in order around the boundary, either clockwise or counter-clockwise. Count the lattice points (points with integer coordinates) that lie strictly inside the polygon, not on its boundary.</p><pre>vertices = [[0,0],[4,0],[4,4],[0,4]]  -> 9\nvertices = [[0,0],[4,0],[0,3]]        -> 3</pre>",
    constraints=["3 &le; vertices.length &le; 500", "-1000 &le; x, y &le; 1000", "The polygon is strictly convex: no corner lies on the segment between its neighbours", "The corners are distinct and given in order around the boundary"],
    hints=["For a polygon whose corners are lattice points, the area is determined by the corners alone. The shoelace formula gives twice the area with integer arithmetic.",
           "Count the lattice points on the boundary: each edge from <code>(x1, y1)</code> to <code>(x2, y2)</code> contributes <code>gcd(|x2 - x1|, |y2 - y1|)</code> points, counting its start but not its end.",
           "Pick's theorem relates the area <code>A</code>, the boundary count <code>B</code> and the interior count <code>I</code> as <code>A = I + B/2 - 1</code>. Solve for I, using twice the area to stay in integers."],
    editorial=["Pick's theorem says that for a simple polygon with lattice corners, <code>A = I + B / 2 - 1</code>, where <code>A</code> is the area, <code>I</code> the number of interior lattice points and <code>B</code> the number of boundary lattice points. Rearranged, <code>I = (2A - B + 2) / 2</code>.",
               "Twice the area comes from the shoelace formula: sum <code>x<sub>i</sub> * y<sub>i+1</sub> - x<sub>i+1</sub> * y<sub>i</sub></code> over all edges, and take its absolute value so that the orientation does not matter. The boundary count is the sum of <code>gcd(|dx|, |dy|)</code> over the edges, because an edge with gcd g has g lattice steps.",
               "The whole computation is one pass over the edges, O(n) plus the gcd cost. The result stays in integers: the expression <code>(2A - B + 2)</code> is always even by Pick's theorem, so integer division is exact."],
    time="O(n log C)", space="O(1)",
    solution='''from math import gcd

def interiorLatticePoints(vertices):
    n = len(vertices)
    twice_area = 0
    boundary = 0
    for i in range(n):
        x1, y1 = vertices[i]
        x2, y2 = vertices[(i + 1) % n]
        twice_area += x1 * y2 - x2 * y1
        boundary += gcd(abs(x2 - x1), abs(y2 - y1))
    twice_area = abs(twice_area)
    return (twice_area - boundary + 2) // 2
''',
    tests=[[[[0, 0], [4, 0], [4, 4], [0, 4]]], [[[0, 0], [4, 0], [0, 3]]], [[[0, 0], [0, 3], [4, 0]]],
           [[[0, 0], [1, 0], [0, 1]]], [[[-2, -2], [3, -1], [1, 4], [-3, 2]]],
           [[[-1000, -1000], [1000, -1000], [1000, 1000], [-1000, 1000]]],
           [[[-5, 0], [0, -5], [5, 0], [0, 5]]], [[[0, 0], [7, 2], [3, 9]]]],
)
p["tests"].append([_rand_hull])
p["tests"].append([_circ])


def b_pick(vertices):
    n = len(vertices)
    s2 = sum(vertices[i][0] * vertices[(i + 1) % n][1] - vertices[(i + 1) % n][0] * vertices[i][1] for i in range(n))
    sign = 1 if s2 > 0 else -1
    xs = [v[0] for v in vertices]
    ys = [v[1] for v in vertices]
    cnt = 0
    for x in range(min(xs), max(xs) + 1):
        for y in range(min(ys), max(ys) + 1):
            inside = True
            for i in range(n):
                x1, y1 = vertices[i]
                x2, y2 = vertices[(i + 1) % n]
                if ((x2 - x1) * (y - y1) - (y2 - y1) * (x - x1)) * sign <= 0:
                    inside = False
                    break
            if inside:
                cnt += 1
    return cnt


def g_pick(r):
    pts = [[r.randint(-5, 5), r.randint(-5, 5)] for _ in range(r.randint(3, 9))]
    h = _hull(pts)
    if len(h) < 3:
        h = [[0, 0], [1, 0], [0, 1]]
    k = r.randint(0, len(h) - 1)
    h = h[k:] + h[:k]
    if r.random() < 0.5:
        h = h[::-1]
    return [h]


def v_pick(tests):
    for t in tests:
        vs = t["args"][0]
        assert 3 <= len(vs) <= 500
        assert all(-1000 <= x <= 1000 and -1000 <= y <= 1000 for x, y in vs)
        assert len(_hull(vs)) == len(vs), "polygon must be strictly convex"


CHECKS["lattice-points-inside-convex-polygon"] = (b_pick, g_pick, "exact")
VALIDATE["lattice-points-inside-convex-polygon"] = v_pick

p = add(
    id="lattice-squares-in-grid", tier="extra", title="Squares on a Lattice Grid", diff="Hard", topic="Math & Bit Manipulation",
    fn="countLatticeSquares", params=[("n", "int")], ret="int", cmp="exact",
    desc="<p>Consider the <code>(n + 1) x (n + 1)</code> grid of points whose coordinates run from <code>0</code> to <code>n</code> in each direction. Count the squares whose four corners are all points of this grid. Squares may be tilted, not only axis-aligned.</p><p>The count grows quickly, so return it modulo <code>1,000,000,007</code>.</p><pre>n = 1 -> 1    (the unit square)\nn = 2 -> 6    (4 unit squares, 1 square of side 2, and 1 tilted square)\nn = 3 -> 20</pre>",
    constraints=["0 &le; n &le; 200,000"],
    hints=["Describe a square by one of its sides as a vector <code>(a, b)</code>. Rotating the vector by 90 degrees gives the other sides, so each square has exactly one side vector with <code>a &gt; 0</code> and <code>b &ge; 0</code>.",
           "A square with side vector <code>(a, b)</code> has a bounding box of size <code>(a + b) x (a + b)</code>. How many positions can such a box take in the grid?",
           "Group the vectors by <code>s = a + b</code>: there are <code>s</code> vectors with that sum, and the box fits in <code>(n - s + 1)<sup>2</sup></code> positions. Sum <code>s * (n - s + 1)<sup>2</sup></code> over s."],
    editorial=["Every square has four side vectors obtained by rotating one of them by 90 degrees. Exactly one of the four lies in the half-open quadrant <code>a &gt; 0, b &ge; 0</code>, so counting squares is the same as counting the vectors <code>(a, b)</code> in that quadrant together with a position for each.",
               "A square with side vector <code>(a, b)</code> has a bounding box whose width and height are both <code>a + b</code>. The box has its lower-left corner at some point of the grid, and it fits in the grid for <code>(n - (a + b) + 1)<sup>2</sup></code> positions, provided <code>a + b &le; n</code>.",
               "For a fixed <code>s = a + b</code> there are <code>s</code> choices of <code>a</code> from 1 to <code>s</code>. The total is the sum of <code>s * (n - s + 1)<sup>2</sup></code> over <code>s = 1..n</code>, an O(n) loop. The brute force that tries every four-point subset agrees with it on small n."],
    time="O(n)", space="O(1)",
    solution='''def countLatticeSquares(n):
    MOD = 1000000007
    total = 0
    for s in range(1, n + 1):
        total = (total + s * (n - s + 1) ** 2) % MOD
    return total
''',
    tests=[[0], [1], [2], [3], [4], [1001], [1234], [123456], [99999], [200000]],
)


def b_squares(n):
    pts = [(x, y) for x in range(n + 1) for y in range(n + 1)]
    c = 0
    for quad in combinations(pts, 4):
        d = sorted((p1[0] - q1[0]) ** 2 + (p1[1] - q1[1]) ** 2 for p1, q1 in combinations(quad, 2))
        if d[0] > 0 and d[0] == d[1] == d[2] == d[3] and d[4] == d[5] == 2 * d[0]:
            c += 1
    return c


def v_squares(tests):
    for t in tests:
        assert 0 <= t["args"][0] <= 200000


CHECKS["lattice-squares-in-grid"] = (b_squares, lambda r: [r.randint(0, 3)], "exact")
VALIDATE["lattice-squares-in-grid"] = v_squares

p = add(
    id="coprime-pairs-in-square", title="Coprime Pairs in a Square", diff="Medium", topic="Math & Bit Manipulation",
    fn="coprimePairs", params=[("n", "int")], ret="int", cmp="exact",
    desc="<p>Count the ordered pairs of integers <code>(x, y)</code> with <code>1 &le; x, y &le; n</code> whose greatest common divisor is 1. The pairs <code>(1, 2)</code> and <code>(2, 1)</code> count separately.</p><p>These are the lattice points that an observer at the origin can see inside the square, because no other lattice point lies between them and the origin on the same line.</p><pre>n = 1 -> 1    ((1,1))\nn = 2 -> 3    ((1,1), (1,2), (2,1))\nn = 4 -> 11</pre>",
    constraints=["1 &le; n &le; 30,000"],
    hints=["Count, for each x, how many y in the range are coprime to x. Then sum over x.",
           "Euler's totient <code>phi(x)</code> counts the numbers from 1 to x that are coprime to x. Summing it over x gives the count for one half of the symmetric square.",
           "Compute phi for all values up to n with a sieve: start with phi[i] = i and, for each prime p, multiply the entries at multiples of p by (1 - 1/p)."],
    editorial=["Let <code>S = sum of phi(i)</code> for <code>i = 1..n</code>. The value <code>phi(i)</code> counts the pairs <code>(x, i)</code> with <code>1 &le; x &le; i</code> and <code>gcd(x, i) = 1</code>, because <code>gcd(x, i) = gcd(i, x)</code> and the pairs with x equal to i count only for i = 1. So <code>S</code> counts the coprime pairs with <code>x &le; y</code>.",
               "The square is symmetric under swapping x and y, and the only diagonal pair that is coprime is <code>(1, 1)</code>. So the ordered count is <code>2S - 1</code>.",
               "The sieve starts with <code>phi[i] = i</code>. When <code>i</code> is still unchanged it is prime, and every multiple <code>j</code> of <code>i</code> gets <code>phi[j] -= phi[j] // i</code>. The total cost is O(n log log n)."],
    time="O(n log log n)", space="O(n)",
    solution='''def coprimePairs(n):
    phi = list(range(n + 1))
    for i in range(2, n + 1):
        if phi[i] == i:
            for j in range(i, n + 1, i):
                phi[j] -= phi[j] // i
    return 2 * sum(phi[1:]) - 1
''',
    tests=[[1], [2], [3], [4], [10], [100], [300], [12345], [29999], [30000]],
)


def b_coprime(n):
    return sum(1 for x in range(1, n + 1) for y in range(1, n + 1) if math.gcd(x, y) == 1)


def v_coprime(tests):
    for t in tests:
        assert 1 <= t["args"][0] <= 30000


CHECKS["coprime-pairs-in-square"] = (b_coprime, lambda r: [r.randint(1, 40)], "exact")
VALIDATE["coprime-pairs-in-square"] = v_coprime

p = add(
    id="paths-staying-below-diagonal", tier="extra", title="Paths Staying Below the Diagonal", diff="Medium", topic="Math & Bit Manipulation",
    fn="countBallotPaths", params=[("a", "int"), ("b", "int")], ret="int", cmp="exact",
    desc="<p>A walker starts at <code>(0, 0)</code> and must reach <code>(a, b)</code> using unit steps to the right (<code>x + 1</code>) or up (<code>y + 1</code>). Count the routes on which every visited point satisfies <code>y &le; x</code>, so the route never rises above the diagonal. Return the count modulo <code>1,000,000,007</code>.</p><pre>a = 2, b = 1 -> 2    (RRU and RUR; URR goes above the diagonal)\na = 3, b = 3 -> 5    (the Catalan number C<sub>3</sub>)</pre>",
    constraints=["0 &le; b &le; a &le; 100,000"],
    hints=["Count all routes to <code>(a, b)</code> first: that is a binomial coefficient. Then subtract the routes that touch the forbidden line <code>y = x + 1</code>.",
           "Reflect the start point across the forbidden line <code>y = x + 1</code>. Routes that touch the line correspond one-to-one with routes from the reflected start to <code>(a, b)</code>.",
           "The reflected start is <code>(-1, 1)</code>, which needs <code>a + b + 1</code> steps with <code>b</code> ups and <code>a + 1</code> rights, so the bad routes number <code>C(a + b, b - 1)</code>."],
    editorial=["All routes from <code>(0, 0)</code> to <code>(a, b)</code> use <code>a</code> right steps and <code>b</code> up steps, so there are <code>C(a + b, b)</code> of them. Some of these touch the line <code>y = x + 1</code>, which is the first point where a route leaves the allowed region.",
               "By the reflection principle, the bad routes correspond to routes from the mirror image of the start, <code>(-1, 1)</code>, to <code>(a, b)</code>. Those have <code>a + 1</code> right steps and <code>b - 1</code> up steps, so there are <code>C(a + b, b - 1)</code> of them. The answer is <code>C(a + b, b) - C(a + b, b - 1)</code>, the ballot number.",
               "Precompute factorials up to <code>a + b</code> and use modular inverses through Fermat's little theorem. Setting <code>a = b = n</code> gives the Catalan number <code>C<sub>n</sub></code>, which is a useful check."],
    time="O(a + b)", space="O(a + b)",
    solution='''def countBallotPaths(a, b):
    MOD = 1000000007
    N = a + b
    fact = [1] * (N + 1)
    for i in range(1, N + 1):
        fact[i] = fact[i - 1] * i % MOD

    def C(n, k):
        if k < 0 or k > n:
            return 0
        return fact[n] * pow(fact[k] * fact[n - k] % MOD, MOD - 2, MOD) % MOD

    return (C(N, b) - C(N, b - 1)) % MOD
''',
    tests=[[0, 0], [1, 0], [1, 1], [2, 1], [3, 3], [5, 0], [5, 5], [6, 2], [300, 150], [50000, 20000],
           [100000, 100000], [100000, 99999], [99999, 0]],
)


def b_ballot(a, b):
    dp = [[0] * (b + 1) for _ in range(a + 1)]
    dp[0][0] = 1
    for x in range(a + 1):
        for y in range(min(x, b) + 1):
            if x == 0 and y == 0:
                continue
            v = 0
            if x > 0 and y <= x - 1:
                v += dp[x - 1][y]
            if y > 0:
                v += dp[x][y - 1]
            dp[x][y] = v
    return dp[a][b] % 1000000007


def g_ballot(r):
    a = r.randint(0, 10)
    return [a, r.randint(0, a)]


def v_ballot(tests):
    for t in tests:
        a, b = t["args"]
        assert 0 <= b <= a <= 100000


CHECKS["paths-staying-below-diagonal"] = (b_ballot, g_ballot, "exact")
VALIDATE["paths-staying-below-diagonal"] = v_ballot

p = add(
    id="farthest-pair-manhattan", title="Farthest Pair in Manhattan Distance", diff="Medium", topic="Math & Bit Manipulation",
    fn="maxManhattanPair", params=[("points", "int[][]")], ret="int", cmp="exact",
    desc="<p>Given <code>points</code>, an array of integer points <code>[x, y]</code>, find the largest Manhattan distance between two of them. The Manhattan distance is <code>|x1 - x2| + |y1 - y2|</code>. Comparing every pair is too slow for large inputs.</p><pre>points = [[1,1],[3,5],[-2,4]]\n(1,1)-(3,5) = 6,  (1,1)-(-2,4) = 6,  (3,5)-(-2,4) = 6\nresult = 6</pre>",
    constraints=["2 &le; points.length &le; 100,000", "points[i].length = 2", "-500,000,000 &le; x, y &le; 500,000,000"],
    hints=["Rotate the plane by 45 degrees: look at <code>x + y</code> and <code>x - y</code> for each point.",
           "The Manhattan distance equals the larger of the two differences <code>|(x1 + y1) - (x2 + y2)|</code> and <code>|(x1 - y1) - (x2 - y2)|</code>.",
           "The maximum over all pairs of the larger of two quantities is the larger of the two maxima over pairs, and each of those is a spread of values: max minus min."],
    editorial=["For any two points, <code>|dx| + |dy| = max(|d(x + y)|, |d(x - y)|)</code>, a standard identity. Since the maximum over all pairs of a maximum of two terms is the maximum of the two separate maxima, the answer is <code>max(maxS - minS, maxD - minD)</code>, where S holds the values <code>x + y</code> and D holds <code>x - y</code>.",
               "The largest difference inside a list is its maximum minus its minimum, so one pass over the points gives the answer. The work is O(n) and needs no pair comparisons.",
               "The result is at most 2 * 10<sup>9</sup>, which fits in a 32-bit signed integer, so the constraint on coordinates keeps the answer in range."],
    time="O(n)", space="O(1)",
    solution='''def maxManhattanPair(points):
    sums = [x + y for x, y in points]
    diffs = [x - y for x, y in points]
    return max(max(sums) - min(sums), max(diffs) - min(diffs))
''',
    tests=[[[[1, 1], [3, 5], [-2, 4]]], [[[0, 0], [5, -7]]], [[[2, 2], [2, 2]]], [[[7, 0], [0, 7], [-7, 0], [0, -7]]],
           [[[-500000000, -500000000], [500000000, 500000000]]], [[[500000000, -500000000], [-500000000, 500000000]]],
           [[[0, 0], [3, 1], [-4, 2], [1, -6]]]],
)
_r = rnd(404)
p["tests"].append([[[_r.randint(-500000000, 500000000), _r.randint(-500000000, 500000000)] for _ in range(2000)]])
p["tests"].append([[[_r.randint(-1000, 1000), _r.randint(-1000, 1000)] for _ in range(3000)]])


def b_farthest(points):
    best = 0
    for i in range(len(points)):
        for j in range(i + 1, len(points)):
            best = max(best, abs(points[i][0] - points[j][0]) + abs(points[i][1] - points[j][1]))
    return best


def g_farthest(r):
    return [[[r.randint(-6, 6), r.randint(-6, 6)] for _ in range(r.randint(2, 8))]]


def v_farthest(tests):
    for t in tests:
        pts = t["args"][0]
        assert 2 <= len(pts) <= 100000
        assert all(-500000000 <= x <= 500000000 and -500000000 <= y <= 500000000 for x, y in pts)


CHECKS["farthest-pair-manhattan"] = (b_farthest, g_farthest, "exact")
VALIDATE["farthest-pair-manhattan"] = v_farthest
