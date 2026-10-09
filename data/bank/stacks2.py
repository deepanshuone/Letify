"""Problems: stacks (monotonic stacks and stack-based parsing). See data/lib.py for the registry."""
import itertools
import sys

from lib import add, rnd, CHECKS, VALIDATE, gen_arr  # noqa: F401

INT_MIN, INT_MAX = -(2 ** 31), 2 ** 31 - 1
MOD = 10 ** 9 + 7


# ---------------------------------------------------------------- EASY

p = add(
    id="min-insertions-to-balance-brackets", title="Minimum Insertions to Balance Brackets", diff="Easy", topic="Stack",
    fn="minInsertionsToBalance", params=[("s", "string")], ret="int", cmp="exact",
    desc="<p>A string <code>s</code> consists only of the characters <code>'('</code> and <code>')'</code>. A bracket string is <em>balanced</em> when every <code>'('</code> can be paired with a later <code>')'</code> and every <code>')'</code> with an earlier <code>'('</code>, with each bracket used in exactly one pair.</p><p>You may insert new brackets at any positions. Return the minimum number of insertions needed to make <code>s</code> balanced.</p>",
    constraints=["1 &le; s.length &le; 10,000", "s[i] is '(' or ')'"],
    hints=["Scan from left to right and keep track of the brackets that are still waiting for a partner.",
           "A <code>')'</code> that finds no waiting <code>'('</code> can never be fixed by anything on its left, so it needs one inserted <code>'('</code> right away.",
           "Keep a counter of unmatched <code>'('</code> and a counter of insertions. The answer is the insertions plus whatever unmatched <code>'('</code> are left at the end."],
    editorial=["Treat the string like a stack that only ever holds <code>'('</code>, so a single counter <code>open</code> is enough. For each <code>'('</code> increase <code>open</code>. For each <code>')'</code>, if <code>open &gt; 0</code> it cancels one waiting bracket, otherwise it has no partner and we must insert a <code>'('</code> (count one insertion).",
               "After the scan every remaining waiting <code>'('</code> needs one inserted <code>')'</code>, so the answer is <code>insertions + open</code>. Each insertion fixes exactly one unmatched bracket and the greedy decisions are forced, so the count is minimal. Time is O(n) with O(1) extra space."],
    time="O(n)", space="O(1)",
    solution='''def minInsertionsToBalance(s):
    open_count = 0   # '(' still waiting for a ')'
    inserted = 0     # '(' we had to add for a ')' with no partner
    for ch in s:
        if ch == '(':
            open_count += 1
        elif open_count > 0:
            open_count -= 1
        else:
            inserted += 1
    return inserted + open_count
''',
    tests=[["())"], ["((("], ["()"], [")("], ["))))"], ["((()))"], ["()()("], ["(()))(()"], [")))((("], ["("], [")"]],
)
_r = rnd(9301)
p["tests"].append(["(" * 10000])
p["tests"].append([")" * 10000])
p["tests"].append(["()" * 5000])
p["tests"].append([")" * 5000 + "(" * 5000])
p["tests"].append(["".join(_r.choice("()") for _ in range(10000))])
p["tests"].append(["".join(_r.choices("()", weights=[3, 2])[0] for _ in range(9999))])


def b_minins(s):
    # repeatedly cancel adjacent "()" pairs; whatever is left must each be fixed by one insertion
    while "()" in s:
        s = s.replace("()", "", 1)
    return len(s)


def g_minins(r):
    return ["".join(r.choice("()") for _ in range(r.randint(1, 14)))]


def v_minins(tests):
    for t in tests:
        s = t["args"][0]
        assert 1 <= len(s) <= 10000 and set(s) <= set("()")


CHECKS["min-insertions-to-balance-brackets"] = (b_minins, g_minins, "exact")
VALIDATE["min-insertions-to-balance-brackets"] = v_minins


p = add(
    id="final-prices-with-discount", title="Final Prices With a Special Discount", diff="Easy", topic="Stack",
    fn="finalPrices", params=[("prices", "int[]")], ret="int[]", cmp="exact",
    desc="<p>The array <code>prices</code> lists the prices of items in a shop, in the order they sit on a shelf. When you buy item <code>i</code>, you get a discount equal to the price of the <em>first</em> item <code>j</code> to its right (<code>j &gt; i</code>) whose price satisfies <code>prices[j] &le; prices[i]</code>. If no such item exists, you get no discount.</p><p>Return an array <code>answer</code> where <code>answer[i]</code> is the price you actually pay for item <code>i</code>.</p>",
    constraints=["1 &le; prices.length &le; 10,000", "1 &le; prices[i] &le; 100,000"],
    hints=["Checking every later item for every item is O(n<sup>2</sup>). For each item you only need the first later item that is not more expensive.",
           "Walk left to right. An item that has not yet found its discount is waiting for a price that is at most its own.",
           "Keep the waiting items on a stack of indices. When a new price arrives, pop every waiting item whose price is at least the new price and apply the discount to it; then push the new index."],
    editorial=["This is a <em>next smaller or equal element</em> problem. Process the array left to right with a stack holding the indices of items that have not found a discount yet. The prices on the stack are always non-decreasing from bottom to top, because anything bigger than the incoming price gets popped.",
               "For the incoming index <code>i</code>, while the item on top of the stack has price <code>&ge; prices[i]</code>, pop it and subtract <code>prices[i]</code> from its final price: <code>i</code> is the first item to the right of it with a price that is not larger. Then push <code>i</code>. Every index is pushed and popped at most once, so the total time is O(n)."],
    time="O(n)", space="O(n)",
    solution='''def finalPrices(prices):
    answer = list(prices)
    waiting = []   # indices still looking for a discount; their prices never decrease upward
    for i, price in enumerate(prices):
        while waiting and prices[waiting[-1]] >= price:
            answer[waiting.pop()] -= price
        waiting.append(i)
    return answer
''',
    tests=[[[8, 4, 6, 2, 3]], [[1, 2, 3, 4, 5]], [[10, 1, 1, 6]], [[5]], [[3, 3, 3]], [[100000, 1, 100000, 1]],
           [[5, 4, 3, 2, 1]], [[2, 1, 2, 1, 2]], [[7, 8, 4, 5, 6, 3]], [[1, 1]]],
)
_r = rnd(9302)
p["tests"].append([[_r.randint(1, 100000) for _ in range(10000)]])
p["tests"].append([list(range(1, 10001))])
p["tests"].append([list(range(10000, 0, -1))])
p["tests"].append([[77777] * 10000])
p["tests"].append([[_r.randint(1, 5) for _ in range(10000)]])
p["tests"].append([[(i * 7919) % 100000 + 1 for i in range(9000)]])


def b_final(prices):
    out = []
    for i in range(len(prices)):
        pay = prices[i]
        for j in range(i + 1, len(prices)):
            if prices[j] <= prices[i]:
                pay = prices[i] - prices[j]
                break
        out.append(pay)
    return out


def v_final(tests):
    for t in tests:
        a = t["args"][0]
        assert 1 <= len(a) <= 10000 and all(1 <= x <= 100000 for x in a)


CHECKS["final-prices-with-discount"] = (b_final, lambda r: [gen_arr(r, 1, 8, 1, 10)], "exact")
VALIDATE["final-prices-with-discount"] = v_final


# ---------------------------------------------------------------- MEDIUM

p = add(
    id="next-greater-circular-array", title="Next Greater Value in a Circular Array", diff="Medium", topic="Stack",
    fn="nextGreaterCircular", params=[("nums", "int[]")], ret="int[]", cmp="exact",
    desc="<p>The array <code>nums</code> is <em>circular</em>: the element after the last one is the first one again. For each position <code>i</code>, look at the elements that follow it, wrapping around the end of the array, and find the first one that is strictly larger than <code>nums[i]</code>. You may look at the other <code>n - 1</code> positions at most once each; position <code>i</code> itself is never a candidate.</p><p>Return an array <code>answer</code> where <code>answer[i]</code> is that larger <em>value</em>, or <code>-1</code> if no element of the array is strictly larger than <code>nums[i]</code>.</p>",
    constraints=["1 &le; nums.length &le; 10,000", "-2<sup>31</sup> &le; nums[i] &le; 2<sup>31</sup> - 1"],
    hints=["Brute force scans up to n positions for each element, which is O(n<sup>2</sup>). To handle the wrap-around, imagine the array written twice in a row.",
           "Process the doubled array from left to right and keep a stack of positions whose answer is still unknown. A new value resolves every waiting position with a smaller value.",
           "Only push positions during the first pass (index &lt; n). The second pass exists solely to resolve the elements that are waiting for a greater value on the wrapped-around side."],
    editorial=["Use a monotonic stack of indices whose values are non-increasing from bottom to top. Walk <code>k</code> from <code>0</code> to <code>2n - 1</code> and let <code>i = k mod n</code>. While the stack is non-empty and <code>nums[stack.top] &lt; nums[i]</code>, pop it and set its answer to <code>nums[i]</code>. During the first lap (<code>k &lt; n</code>) push <code>i</code> afterwards.",
               "Because the second lap only resolves waiting indices and never pushes, each index is pushed and popped at most once, giving O(n) time. Indices that are still on the stack after both laps hold the global maximum value (or ties with it), so they keep the answer <code>-1</code>. The array is initialised with <code>-1</code> for exactly that reason."],
    time="O(n)", space="O(n)",
    solution='''def nextGreaterCircular(nums):
    n = len(nums)
    answer = [-1] * n
    waiting = []   # indices with no greater value found yet; values never increase upward
    for k in range(2 * n):
        i = k % n
        while waiting and nums[waiting[-1]] < nums[i]:
            answer[waiting.pop()] = nums[i]
        if k < n:
            waiting.append(i)
    return answer
''',
    tests=[[[1, 2, 1]], [[1, 2, 3, 4, 3]], [[5]], [[2, 2, 2]], [[5, 4, 3, 2, 1]], [[1, 5, 3, 4, 2]], [[INT_MIN, INT_MAX]],
           [[-1, -2, -3]], [[3, 8, 4, 1, 2]], [[INT_MAX, INT_MAX]], [[4, 1, 4]]],
)
_r = rnd(9303)
p["tests"].append([[_r.randint(INT_MIN, INT_MAX) for _ in range(10000)]])
p["tests"].append([list(range(10000))])
p["tests"].append([list(range(10000, 0, -1))])
p["tests"].append([[_r.randint(-3, 3) for _ in range(10000)]])
p["tests"].append([[5] * 5000 + [9] + [5] * 4000])


def b_nge(nums):
    n = len(nums)
    out = []
    for i in range(n):
        ans = -1
        for step in range(1, n):
            v = nums[(i + step) % n]
            if v > nums[i]:
                ans = v
                break
        out.append(ans)
    return out


def v_nge(tests):
    for t in tests:
        a = t["args"][0]
        assert 1 <= len(a) <= 10000


CHECKS["next-greater-circular-array"] = (b_nge, lambda r: [gen_arr(r, -4, 4, 1, 10)], "exact")
VALIDATE["next-greater-circular-array"] = v_nge


p = add(
    id="sum-of-subarray-minimums-mod", title="Sum of Subarray Minimums", diff="Medium", topic="Stack",
    fn="sumSubarrayMins", params=[("arr", "int[]")], ret="int", cmp="exact",
    desc="<p>For every contiguous, non-empty subarray of <code>arr</code>, take its smallest element. Return the sum of all these minimums.</p><p>The sum can be huge, so return it modulo <code>1,000,000,007</code>.</p>",
    constraints=["1 &le; arr.length &le; 15,000", "1 &le; arr[i] &le; 30,000"],
    hints=["There are O(n<sup>2</sup>) subarrays. Instead of enumerating them, ask for each element: in how many subarrays is it the minimum?",
           "Element <code>arr[i]</code> is the minimum of a subarray exactly when the subarray lies strictly between the nearest smaller element on its left and the nearest smaller element on its right. Ties must be broken consistently so a subarray is counted once.",
           "Find, with a monotonic stack, the distance <code>left</code> to the previous strictly smaller element and <code>right</code> to the next smaller-or-equal element. Then <code>arr[i]</code> contributes <code>arr[i] * left * right</code>."],
    editorial=["Count contributions. Let <code>L</code> be the number of choices for the left end of a subarray in which <code>arr[i]</code> is the chosen minimum (distance back to the previous element that is strictly smaller) and <code>R</code> the number of choices for the right end (distance forward to the next element that is smaller <em>or equal</em>). Any left end and right end combine, so <code>arr[i]</code> is the minimum of exactly <code>L * R</code> subarrays. Using strict on one side and non-strict on the other makes sure that among equal values only one is credited for each subarray.",
               "Both distances come from monotonic stacks in a single pass each, so the whole computation is O(n). Sum <code>arr[i] * L * R</code> over all i, taking the remainder modulo 1,000,000,007 as you go (Python integers do not overflow, but fixed-width languages need the modulus applied to avoid overflow)."],
    time="O(n)", space="O(n)",
    solution='''def sumSubarrayMins(arr):
    MOD = 10 ** 9 + 7
    n = len(arr)
    left = [0] * n    # choices of left end: distance to previous strictly smaller element
    right = [0] * n   # choices of right end: distance to next smaller-or-equal element
    stack = []
    for i in range(n):
        while stack and arr[stack[-1]] >= arr[i]:
            stack.pop()
        left[i] = i - (stack[-1] if stack else -1)
        stack.append(i)
    stack = []
    for i in range(n - 1, -1, -1):
        while stack and arr[stack[-1]] > arr[i]:
            stack.pop()
        right[i] = (stack[-1] if stack else n) - i
        stack.append(i)
    total = 0
    for i in range(n):
        total = (total + arr[i] * left[i] * right[i]) % MOD
    return total
''',
    tests=[[[3, 1, 2, 4]], [[11, 81, 94, 43, 3]], [[1]], [[2, 2]], [[1, 2, 3]], [[3, 2, 1]], [[5, 5, 5, 5]], [[30000]],
           [[2, 1, 2, 1, 2]], [[1, 1, 1]], [[4, 2, 4, 2, 4]]],
)
_r = rnd(9304)
p["tests"].append([[30000] * 15000])
p["tests"].append([list(range(1, 15001))])
p["tests"].append([[30000 - (i * 2) % 30000 for i in range(15000)]])
p["tests"].append([[_r.randint(1, 30000) for _ in range(15000)]])
p["tests"].append([[_r.randint(1, 4) for _ in range(15000)]])
p["tests"].append([[30000 - abs(7500 - i) * 3 for i in range(15000)]])


def b_summins(arr):
    total = 0
    for i in range(len(arr)):
        m = arr[i]
        for j in range(i, len(arr)):
            m = min(m, arr[j])
            total += m
    return total % MOD


def v_summins(tests):
    for t in tests:
        a = t["args"][0]
        assert 1 <= len(a) <= 15000 and all(1 <= x <= 30000 for x in a)


CHECKS["sum-of-subarray-minimums-mod"] = (b_summins, lambda r: [gen_arr(r, 1, 6, 1, 12)], "exact")
VALIDATE["sum-of-subarray-minimums-mod"] = v_summins


p = add(
    id="remove-k-digits-smallest-number", title="Remove K Digits for the Smallest Number", diff="Medium", topic="Stack",
    fn="removeKDigits", params=[("num", "string"), ("k", "int")], ret="string", cmp="exact",
    desc="<p>The string <code>num</code> is a non-negative integer written in decimal. Delete exactly <code>k</code> of its digits (the remaining digits keep their original order) so that the number they form is as small as possible.</p><p>Return the result as a string without leading zeros. If every digit is deleted, or the remaining digits form the value zero, return <code>\"0\"</code>.</p>",
    constraints=["1 &le; num.length &le; 10,000", "0 &le; k &le; num.length", "num contains only digits and has no leading zeros (except the single digit \"0\")"],
    hints=["Compare two numbers with the same number of digits: the leftmost differing digit decides. So you want small digits as far to the left as possible.",
           "When a digit is followed by a smaller digit, deleting the first one makes the number smaller. Deleting from the left is always at least as good as deleting from the right.",
           "Use a stack of kept digits. For each new digit, while you still have deletions left and the top of the stack is larger than the new digit, pop. Afterwards drop any remaining deletions from the end and strip leading zeros."],
    editorial=["Greedy with a monotonic stack. Keep the digits chosen so far on a stack. When a new digit <code>d</code> arrives and the top of the stack is larger than <code>d</code>, removing that top digit makes the number strictly smaller (a smaller digit moves into a more significant position), so pop while <code>k &gt; 0</code> and the top is larger, then push <code>d</code>.",
               "If digits remain to delete after the scan, the stack is non-decreasing, so the best choice is to delete from the end. Finally, strip leading zeros and return <code>\"0\"</code> if nothing is left. Each digit is pushed and popped at most once, so the time is O(n)."],
    time="O(n)", space="O(n)",
    solution='''def removeKDigits(num, k):
    stack = []
    for ch in num:
        while k > 0 and stack and stack[-1] > ch:
            stack.pop()
            k -= 1
        stack.append(ch)
    if k > 0:
        stack = stack[:-k]
    result = "".join(stack).lstrip("0")
    return result if result else "0"
''',
    tests=[["1432219", 3], ["10200", 1], ["10", 2], ["9", 1], ["9", 0], ["112", 1], ["12345", 2], ["54321", 2], ["100", 1],
           ["1000", 2], ["10001", 4], ["20", 1], ["1234567890", 9], ["7654321", 0]],
)
_r = rnd(9305)
p["tests"].append(["1" + "".join(_r.choice("0123456789") for _ in range(9999)), 5000])
p["tests"].append(["9" * 10000, 9999])
p["tests"].append(["1" + "0" * 9999, 1])
p["tests"].append(["".join(str(i % 10) for i in range(1, 10001)), 4000])
p["tests"].append(["1" + "".join(_r.choice("09") for _ in range(9999)), 3000])
p["tests"].append(["9876543210" * 1000, 9990])
p["tests"].append(["5" * 10000, 10000])


def b_removek(num, k):
    n = len(num)
    keep = n - k
    if keep == 0:
        return "0"
    best = min(int("".join(c)) for c in itertools.combinations(num, keep))
    return str(best)


def g_removek(r):
    n = r.randint(1, 9)
    s = str(r.randint(1, 9)) + "".join(r.choice("0123456789" if r.random() < 0.5 else "0012") for _ in range(n - 1))
    return [s, r.randint(0, n)]


def v_removek(tests):
    for t in tests:
        s, k = t["args"]
        assert 1 <= len(s) <= 10000 and s.isdigit() and 0 <= k <= len(s)
        assert s == "0" or s[0] != "0"
        e = t["expected"]
        assert e == "0" or (e.isdigit() and e[0] != "0")


CHECKS["remove-k-digits-smallest-number"] = (b_removek, g_removek, "exact")
VALIDATE["remove-k-digits-smallest-number"] = v_removek


p = add(
    id="asteroid-collision-survivors", title="Asteroid Collision Survivors", diff="Medium", topic="Stack",
    fn="asteroidCollision", params=[("asteroids", "int[]")], ret="int[]", cmp="exact",
    desc="<p>Asteroids travel along a line, listed from left to right in the array <code>asteroids</code>. The absolute value of an entry is the asteroid's size, and its sign is its direction: positive moves to the right, negative moves to the left. All asteroids move at the same speed.</p><p>Two asteroids collide only when a right-moving one is somewhere to the left of a left-moving one and nothing separates them. In a collision the smaller asteroid is destroyed; if both have the same size, both are destroyed. Asteroids that move in the same direction never meet, and an asteroid that has no one to collide with keeps flying.</p><p>Return the asteroids that survive after all collisions are over, in their original left-to-right order.</p>",
    constraints=["1 &le; asteroids.length &le; 10,000", "-1,000 &le; asteroids[i] &le; 1,000", "asteroids[i] != 0"],
    hints=["Only a right-moving asteroid followed (somewhere later) by a left-moving one can ever collide. Think about what a left-moving asteroid meets first.",
           "Process asteroids from left to right. The right-movers seen so far that are still alive form a stack; the closest one is on top.",
           "A new left-mover keeps fighting the top of the stack while that top is a right-mover: pop it if it is smaller, pop both if equal, or stop if the new asteroid is destroyed. If the new asteroid survives, push it."],
    editorial=["Keep a stack of surviving asteroids. A new right-moving asteroid can never collide with anything already processed (everything to its left either moves left and has escaped, or moves right at the same speed), so it is simply pushed. A new left-moving asteroid collides with the nearest right-mover on the stack, if there is one.",
               "Loop: while the new asteroid is alive and the top of the stack is positive, compare sizes. If the top is smaller it explodes and we continue with the next stack element; if they are equal both explode and we stop; if the top is larger the new asteroid explodes. If it is still alive when the loop ends it is pushed (it only sits on top of left-movers or an empty stack). Every asteroid is pushed and popped at most once, so the time is O(n)."],
    time="O(n)", space="O(n)",
    solution='''def asteroidCollision(asteroids):
    stack = []
    for a in asteroids:
        alive = True
        while alive and a < 0 and stack and stack[-1] > 0:
            top = stack[-1]
            if top < -a:
                stack.pop()
            elif top == -a:
                stack.pop()
                alive = False
            else:
                alive = False
        if alive:
            stack.append(a)
    return stack
''',
    tests=[[[5, 10, -5]], [[8, -8]], [[10, 2, -5]], [[-2, -1, 1, 2]], [[1, -2, -2, -2]], [[5]], [[-5]], [[1, 1, -1, -1]],
           [[3, 5, -6, 2, -1, 4]], [[-3, 3, -3, 3]], [[10, -3, -4, -20]], [[1000, -1000]], [[1, 2, 3, -3, -2, -1]]],
)
_r = rnd(9306)


def _ast(r, n, hi, pos_bias=0.5):
    out = []
    for _ in range(n):
        v = r.randint(1, hi)
        out.append(v if r.random() < pos_bias else -v)
    return out


p["tests"].append([_ast(_r, 10000, 1000)])
p["tests"].append([_ast(_r, 10000, 1000, 0.8)])
p["tests"].append([_ast(_r, 10000, 5)])
p["tests"].append([[1 + (i % 999) for i in range(5000)] + [-1000] * 5000])
p["tests"].append([[-(i % 1000 + 1) for i in range(5000)] + [(i % 1000 + 1) for i in range(5000)]])
p["tests"].append([[1] * 5000 + [-1] * 5000])


def b_ast(asteroids):
    a = list(asteroids)
    while True:
        for i in range(len(a) - 1):
            if a[i] > 0 and a[i + 1] < 0:
                if a[i] > -a[i + 1]:
                    del a[i + 1]
                elif a[i] < -a[i + 1]:
                    del a[i]
                else:
                    del a[i:i + 2]
                break
        else:
            return a


def v_ast(tests):
    for t in tests:
        a = t["args"][0]
        assert 1 <= len(a) <= 10000 and all(x != 0 and -1000 <= x <= 1000 for x in a)


CHECKS["asteroid-collision-survivors"] = (b_ast, lambda r: [[v for v in gen_arr(r, -5, 5, 1, 10) if v != 0] or [1]], "exact")
VALIDATE["asteroid-collision-survivors"] = v_ast


p = add(
    id="valid-stack-push-pop-order", title="Valid Stack Push and Pop Order", diff="Medium", topic="Stack",
    fn="validateStackSequences", params=[("pushed", "int[]"), ("popped", "int[]")], ret="bool", cmp="exact",
    desc="<p>Starting from an empty stack, you push the values of <code>pushed</code> onto it in exactly the given order. Between pushes you may pop the top of the stack as often as you like (while it is non-empty), and every popped value is recorded in the order of popping. You may stop pushing early, but all values must eventually be pushed and popped.</p><p>The values in <code>pushed</code> are distinct, and <code>popped</code> is a permutation of <code>pushed</code>. Return <code>true</code> if some interleaving of pushes and pops makes the recorded pop order equal to <code>popped</code>, and <code>false</code> otherwise.</p>",
    constraints=["1 &le; pushed.length &le; 10,000", "popped.length == pushed.length", "-10<sup>9</sup> &le; pushed[i] &le; 10<sup>9</sup>, all values in pushed are distinct", "popped is a permutation of pushed"],
    hints=["You never get to choose which element a pop returns, so the order in which values are popped is heavily constrained. Simulating is easier than reasoning abstractly.",
           "Whenever the top of your stack equals the next value that must be popped, popping right away is never harmful.",
           "Push values one by one; after each push pop as long as the top matches the next expected popped value. At the end the stack must be empty."],
    editorial=["Simulate with a real stack and a pointer <code>j</code> into <code>popped</code>. Push each value of <code>pushed</code>; after each push, while the stack is non-empty and its top equals <code>popped[j]</code>, pop it and advance <code>j</code>.",
               "The greedy pop is safe: if the top equals the next required value, any alternative would push more elements above it, and then it could only be popped after those, which would break the required order. If the stack is empty after all pushes have been processed the sequence is valid, otherwise some value is trapped under others in the wrong order. Time O(n), space O(n)."],
    time="O(n)", space="O(n)",
    solution='''def validateStackSequences(pushed, popped):
    stack = []
    j = 0
    for x in pushed:
        stack.append(x)
        while stack and stack[-1] == popped[j]:
            stack.pop()
            j += 1
    return not stack
''',
    tests=[[[1, 2, 3, 4, 5], [4, 5, 3, 2, 1]], [[1, 2, 3, 4, 5], [4, 3, 5, 1, 2]], [[1], [1]], [[1, 2], [2, 1]],
           [[1, 2], [1, 2]], [[1, 2, 3], [3, 1, 2]], [[2, 1, 0], [1, 2, 0]], [[-5, 7, 9, 0], [0, 9, 7, -5]],
           [[999999999, -10 ** 9, 10 ** 9], [10 ** 9, -10 ** 9, 999999999]], [[1, 0], [0, 1]], [[3, 1, 2], [2, 3, 1]]],
)
_r = rnd(9307)


def _valid_pop_order(r, pushed):
    st, out = [], []
    for x in pushed:
        st.append(x)
        while st and r.random() < 0.5:
            out.append(st.pop())
    while st:
        out.append(st.pop())
    return out


_n = 10000
_pu = _r.sample(range(-10 ** 9, 10 ** 9), _n)
p["tests"].append([_pu, _valid_pop_order(_r, _pu)])
_po = _valid_pop_order(_r, _pu)
_po[100], _po[5000] = _po[5000], _po[100]
p["tests"].append([_pu, _po])
p["tests"].append([list(range(10000)), list(range(10000))])
p["tests"].append([list(range(10000)), list(range(9999, -1, -1))])
p["tests"].append([list(range(1, 10001)), [10000] + list(range(1, 10000))])
p["tests"].append([list(range(1, 10001)), list(range(2, 10001)) + [1]])
_pu = _r.sample(range(-10 ** 9, 10 ** 9), 8000)
_po = list(_pu)
_r.shuffle(_po)
p["tests"].append([_pu, _po])


def b_stackseq(pushed, popped):
    n = len(pushed)

    def go(i, j, stack):
        if j == n:
            return True
        if stack and stack[-1] == popped[j] and go(i, j + 1, stack[:-1]):
            return True
        return i < n and go(i + 1, j, stack + [pushed[i]])

    return go(0, 0, [])


def g_stackseq(r):
    n = r.randint(1, 7)
    pu = r.sample(range(-8, 9), n)
    if r.random() < 0.5:
        po = _valid_pop_order(r, pu)
    else:
        po = list(pu)
        r.shuffle(po)
    return [pu, po]


def v_stackseq(tests):
    for t in tests:
        pu, po = t["args"]
        assert 1 <= len(pu) <= 10000 and len(pu) == len(po)
        assert len(set(pu)) == len(pu) and sorted(pu) == sorted(po)
        assert all(-10 ** 9 <= x <= 10 ** 9 for x in pu)
    res = [t["expected"] for t in tests]
    assert True in res and False in res


CHECKS["valid-stack-push-pop-order"] = (b_stackseq, g_stackseq, "exact")
VALIDATE["valid-stack-push-pop-order"] = v_stackseq


p = add(
    id="has-132-pattern", title="Detect a 132 Pattern", diff="Medium", topic="Stack",
    fn="has132Pattern", params=[("nums", "int[]")], ret="bool", cmp="exact",
    desc="<p>A <em>132 pattern</em> in an integer array is a choice of three positions <code>i &lt; j &lt; k</code> whose values satisfy <code>nums[i] &lt; nums[k] &lt; nums[j]</code>: the middle value is the largest, the last value lies strictly between the other two, and the first is the smallest.</p><p>Return <code>true</code> if <code>nums</code> contains a 132 pattern, otherwise return <code>false</code>.</p>",
    constraints=["1 &le; nums.length &le; 10,000", "-2<sup>31</sup> &le; nums[i] &le; 2<sup>31</sup> - 1"],
    hints=["Trying all triples is O(n<sup>3</sup>). Fix the middle (largest) value and think about what the best first and last values would be.",
           "Scan from right to left, so that the '2' is seen first, then the '3', then the '1'. Remember the largest value seen so far that already has a larger value to its left.",
           "Maintain a stack of candidates for '3' and a variable <code>third</code> for the best '2'. When the current value is smaller than <code>third</code>, you have found '1'. Otherwise pop every stack value smaller than the current value into <code>third</code> and push the current value."],
    editorial=["Traverse the array from right to left. We look for the pattern in reverse: first a '2' (value <code>third</code>), then a larger '3' that appears before it in the array, and finally a '1' even earlier that is smaller than the '2'. Keep a stack of values that are '3' candidates, and let <code>third</code> be the largest value ever popped from the stack: each popped value was smaller than some value that came before it in the array, so it is a valid '2' with a larger '3' on its left.",
               "For the current value <code>x</code>: if <code>x &lt; third</code> there is a 132 pattern with <code>x</code> as the '1', so return true. Otherwise, while the stack top is smaller than <code>x</code>, pop it and raise <code>third</code> to it (the larger <code>x</code> is the '3' for these), then push <code>x</code>. Maximising <code>third</code> is optimal because it makes the check <code>x &lt; third</code> easiest to satisfy. Each element is pushed and popped once: O(n) time, O(n) space."],
    time="O(n)", space="O(n)",
    solution='''def has132Pattern(nums):
    third = None      # largest value known to have a bigger value somewhere to its left
    stack = []        # values scanned so far, decreasing from bottom to top
    for x in reversed(nums):
        if third is not None and x < third:
            return True
        while stack and stack[-1] < x:
            third = stack.pop()
        stack.append(x)
    return False
''',
    tests=[[[1, 2, 3, 4]], [[3, 1, 4, 2]], [[-1, 3, 2, 0]], [[1]], [[1, 2]], [[3, 5, 0, 3, 4]], [[1, 0, 1, -4, -3]],
           [[2, 4, 3]], [[2, 4, 2]], [[INT_MIN, INT_MAX, 0]], [[INT_MAX, INT_MIN, INT_MAX]], [[4, 3, 2, 1]], [[6, 12, 3, 4, 6, 11, 20]]],
)
_r = rnd(9308)
p["tests"].append([list(range(10000))])
p["tests"].append([list(range(10000, 0, -1))])
# blocks that each ascend but sit entirely below the previous block: no 132 pattern exists
p["tests"].append([[(100 - b) * 100 + i for b in range(100) for i in range(100)]])
p["tests"].append([[(100 - b) * 100 + i for b in range(100) for i in range(100)][:-1] + [(100 - 50) * 100 + 5]])
p["tests"].append([[_r.randint(INT_MIN, INT_MAX) for _ in range(10000)]])
p["tests"].append([list(range(1, 5001)) + list(range(5000, 1, -1))])
p["tests"].append([[7] * 10000])
p["tests"].append([[5000 + i for i in range(5000)][::-1] + [4999 - i for i in range(5000)][::-1]])


def b_132(nums):
    n = len(nums)
    for i in range(n):
        for j in range(i + 1, n):
            for k in range(j + 1, n):
                if nums[i] < nums[k] < nums[j]:
                    return True
    return False


def v_132(tests):
    for t in tests:
        a = t["args"][0]
        assert 1 <= len(a) <= 10000
    res = [t["expected"] for t in tests]
    assert True in res and False in res


CHECKS["has-132-pattern"] = (b_132, lambda r: [gen_arr(r, -5, 5, 1, 9)], "exact")
VALIDATE["has-132-pattern"] = v_132


# ---------------------------------------------------------------- HARD

p = add(
    id="maximal-rectangle-of-ones", title="Maximal Rectangle of Ones", diff="Hard", topic="Stack",
    fn="maximalRectangle", params=[("matrix", "int[][]")], ret="int", cmp="exact",
    desc="<p>A grid <code>matrix</code> contains only <code>0</code> and <code>1</code>. Find the largest axis-aligned rectangle that is made up entirely of <code>1</code> cells and return its area (the number of cells it covers). If the grid has no <code>1</code>, return <code>0</code>.</p>",
    constraints=["1 &le; matrix.length, matrix[i].length &le; 140", "All rows have the same length", "matrix[i][j] is 0 or 1"],
    hints=["Try enumerating all rectangles first and see how expensive it is, then think about fixing the bottom edge row by row.",
           "For a fixed bottom row, let <code>h[c]</code> be the number of consecutive 1s ending at that row in column c. The best rectangle with that bottom edge is the largest rectangle in the histogram <code>h</code>.",
           "Update <code>h</code> row by row in O(columns), and solve each histogram with a monotonic stack of increasing heights: when a bar is lower than the top, pop and compute the area using the popped height and the width back to the new stack top."],
    editorial=["Every all-ones rectangle has a bottom row. Process the grid row by row and maintain <code>h[c]</code>, the height of the run of 1s that ends at the current row in column c (reset to 0 on a 0 cell). A rectangle whose bottom edge lies on the current row corresponds exactly to a contiguous range of columns and a height that is at most the minimum of <code>h</code> over that range, so we need the largest rectangle under the histogram <code>h</code>.",
               "The largest-rectangle-in-histogram problem is solved with a stack of indices whose heights are increasing. When a bar of height <code>h[c]</code> is not taller than the bar on top, pop the top: its height can no longer extend to the right, its left boundary is the new top of the stack (or the start), so its area is <code>height * (c - newTop - 1)</code>. A sentinel bar of height 0 after the last column flushes the stack. Each row costs O(columns), so the total is O(rows * columns), with O(columns) extra space."],
    time="O(R * C)", space="O(C)",
    solution='''def maximalRectangle(matrix):
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
                best = max(best, h * (c - stack[-1] - 1))
            stack.append(c)
    return best
''',
    tests=[[[[1, 0, 1, 0, 0], [1, 0, 1, 1, 1], [1, 1, 1, 1, 1], [1, 0, 0, 1, 0]]], [[[0]]], [[[1]]], [[[0, 0], [0, 0]]],
           [[[1, 1], [1, 1]]], [[[1, 1, 0, 1]]], [[[1], [1], [0], [1]]], [[[1, 0], [0, 1]]],
           [[[0, 1, 1, 1], [1, 1, 1, 1], [1, 1, 1, 0]]], [[[1, 1, 1], [1, 0, 1], [1, 1, 1]]]],
)
_r = rnd(9309)
p["tests"].append([[[1] * 140 for _ in range(140)]])
p["tests"].append([[[0] * 140 for _ in range(140)]])
p["tests"].append([[[(i + j) % 2 for j in range(140)] for i in range(140)]])
p["tests"].append([[[1 if _r.random() < 0.9 else 0 for _ in range(140)] for _ in range(140)]])
p["tests"].append([[[1 if _r.random() < 0.5 else 0 for _ in range(140)] for _ in range(140)]])
p["tests"].append([[[1 if (i % 30 != 29 and j % 40 != 39) else 0 for j in range(140)] for i in range(140)]])
p["tests"].append([[[1 if j <= i else 0 for j in range(140)] for i in range(140)]])
p["tests"].append([[[1] * 140]])
p["tests"].append([[[1] for _ in range(140)]])
p["tests"].append([[[1 if _r.random() < 0.97 else 0 for _ in range(100)] for _ in range(140)]])


def b_maxrect(matrix):
    R, C = len(matrix), len(matrix[0])
    best = 0
    for r1 in range(R):
        for r2 in range(r1, R):
            for c1 in range(C):
                for c2 in range(c1, C):
                    if all(matrix[r][c] == 1 for r in range(r1, r2 + 1) for c in range(c1, c2 + 1)):
                        best = max(best, (r2 - r1 + 1) * (c2 - c1 + 1))
    return best


def g_maxrect(r):
    R, C = r.randint(1, 6), r.randint(1, 6)
    pr = r.choice([0.3, 0.6, 0.85])
    return [[[1 if r.random() < pr else 0 for _ in range(C)] for _ in range(R)]]


def v_maxrect(tests):
    for t in tests:
        m = t["args"][0]
        assert 1 <= len(m) <= 140 and 1 <= len(m[0]) <= 140
        assert all(len(row) == len(m[0]) and all(v in (0, 1) for v in row) for row in m)


CHECKS["maximal-rectangle-of-ones"] = (b_maxrect, g_maxrect, "exact")
VALIDATE["maximal-rectangle-of-ones"] = v_maxrect


p = add(
    id="evaluate-bracket-expression", title="Evaluate a Bracketed Arithmetic Expression", diff="Hard", topic="Stack",
    fn="evaluateExpression", params=[("expr", "string")], ret="int", cmp="exact",
    desc="<p>The string <code>expr</code> is a valid arithmetic expression with no spaces. It is built from non-negative integer literals, the binary operators <code>+</code>, <code>-</code> and <code>*</code>, and round brackets <code>(</code> <code>)</code> for grouping. Multiplication has higher priority than addition and subtraction, operators of the same priority are applied from left to right, and brackets override priority.</p><p>The minus sign may also appear as a <em>unary</em> operator, but only at the very start of the whole expression or immediately after an opening bracket, for example <code>-(2+3)*4</code> or <code>5*(-3+1)</code>. It then negates the whole term that follows it (<code>-2*3</code> is <code>-6</code>).</p><p>Evaluate the expression and return its value. You may not use any built-in function that evaluates a string as an expression.</p>",
    constraints=["1 &le; expr.length &le; 10,000", "expr contains only digits, '+', '-', '*', '(' and ')' and is a valid expression as described above",
                 "Every integer literal is between 0 and 1,000,000,000 and has no leading zeros (except the single digit \"0\")",
                 "Brackets are nested at most 300 levels deep",
                 "The value of every literal, product, partial sum and bracketed sub-expression met during evaluation has absolute value at most 2<sup>31</sup> - 1"],
    hints=["Plain left-to-right evaluation fails because of priority, and brackets make it recursive. Think about what you must remember when you enter a bracket.",
           "Evaluate the current bracket level with a running total of finished terms, the value of the current product, and the sign of the current term. A closed bracket then behaves like a single number.",
           "On <code>'('</code> push the current state (total, current product, sign, whether a <code>*</code> is pending) on a stack and start fresh. On <code>')'</code> finish the inner value, restore the saved state, and feed the value in as if it were a number. Remember the unary minus: a <code>'-'</code> when no term has started is just the sign of the first term."],
    editorial=["Scan the string once. For each bracket level keep four things: <code>total</code> (the sum of completed terms), <code>cur</code> (the product of the factors of the current term seen so far, or none), <code>sign</code> (+1 or -1 for the current term) and <code>mul</code> (whether a <code>*</code> is waiting for its right operand). A number or a closed bracket is a <em>value</em>: if <code>mul</code> is set then <code>cur *= value</code>, otherwise <code>cur = value</code>.",
               "On <code>'+'</code> or <code>'-'</code>, first add the finished term <code>sign * cur</code> to <code>total</code> (if there is a term; at the start of an expression or just after <code>'('</code> there is none, which is exactly the unary-minus case), then set the new sign. On <code>'('</code> push <code>(total, cur, sign, mul)</code> and reset the four variables. On <code>')'</code> compute <code>total + sign * cur</code>, restore the saved state from the stack and treat the result as a value. At the end the answer is <code>total + sign * cur</code>. Each character is handled once, so the time is O(n) and the stack holds at most one frame per open bracket."],
    time="O(n)", space="O(n)",
    solution='''def evaluateExpression(expr):
    stack = []
    total, cur, sign, mul = 0, None, 1, False
    n = len(expr)
    i = 0
    while i < n:
        c = expr[i]
        if c == "(":
            stack.append((total, cur, sign, mul))
            total, cur, sign, mul = 0, None, 1, False
            i += 1
            continue
        if c == "*":
            mul = True
            i += 1
            continue
        if c == "+" or c == "-":
            if cur is not None:
                total += sign * cur
                cur = None
            sign = 1 if c == "+" else -1
            i += 1
            continue
        if c == ")":
            value = total + sign * cur
            total, cur, sign, mul = stack.pop()
            i += 1
        else:
            j = i
            while j < n and expr[j].isdigit():
                j += 1
            value = int(expr[i:j])
            i = j
        if mul:
            cur *= value
            mul = False
        else:
            cur = value
    return total + sign * cur
''',
    tests=[["1+1"], ["2*3+4"], ["2*(3+4)"], ["-(2+3)*4"], ["5*(-3+1)"], ["7"], ["0"], ["10-4-3"], ["(1+2)*(3+4)"], ["2*3*4*5"],
           ["-5"], ["((1))"], ["1-(2-(3-(4-5)))"], ["(-(-(-4)))"], ["1000000000*2"], ["1000000000*2-1000000000-1000000000+1"], ["12+3*4-5"],
           ["100*(2+12)*(30-3*10+1)"]],
)
_r = rnd(9310)


def _gen_expr(r, depth, terms, maxnum, factors=3, p_br=0.3, p_neg=0.2):
    def num():
        return str(r.randint(0, maxnum))

    def expr(d, allow_unary):
        parts = []
        for t in range(r.randint(1, terms)):
            if t == 0:
                if allow_unary and r.random() < p_neg:
                    parts.append("-")
            else:
                parts.append(r.choice("+-"))
            parts.append(term(d))
        return "".join(parts)

    def term(d):
        fs = []
        for _ in range(r.randint(1, factors)):
            if d > 0 and r.random() < p_br:
                fs.append("(" + expr(d - 1, True) + ")")
            else:
                fs.append(num())
        return "*".join(fs)

    return expr(depth, True)


def _nest(depth, mode):
    s = "7"
    for i in range(depth):
        if mode == 0:
            s = "(" + s + "+" + str(i % 9 + 1) + ")"
        elif mode == 1:
            s = "(-" + s + ")"
        else:
            s = "(" + s + "-" + str(i % 5) + ")"
    return s


p["tests"].append([_gen_expr(_r, 3, 6, 99)])
p["tests"].append([_gen_expr(_r, 4, 5, 9)])
p["tests"].append([_gen_expr(_r, 0, 700, 99, 3)])
p["tests"].append(["+".join(str(_r.randint(0, 999999)) for _ in range(1400))])
p["tests"].append([_nest(299, 0)])
p["tests"].append([_nest(299, 1)])
p["tests"].append([_nest(299, 2)])
p["tests"].append(["-".join("(" + _gen_expr(_r, 2, 4, 50, 2) + ")" for _ in range(60))])
p["tests"].append(["1" + "".join("*(" + _gen_expr(_r, 1, 3, 9, 2) + "+1)" for _ in range(5))])
p["tests"].append(["(" * 299 + "-1" + ")" * 299])
p["tests"].append(["*".join(["3"] * 19)])


def _tokens_eval_checked(s):
    """Independent recursive-descent parser that asserts the grammar and the int32 bound on every intermediate value."""
    pos = [0]
    LIM = INT_MAX

    def chk(v):
        assert abs(v) <= LIM, ("intermediate out of range", s[:60])
        return v

    def number():
        i = pos[0]
        j = i
        while j < len(s) and s[j].isdigit():
            j += 1
        assert j > i, ("expected number", s[:60], i)
        lit = s[i:j]
        assert lit == "0" or lit[0] != "0"
        assert int(lit) <= 10 ** 9
        pos[0] = j
        return chk(int(lit))

    def factor(depth):
        if pos[0] < len(s) and s[pos[0]] == "(":
            assert depth < 300, "nesting too deep"
            pos[0] += 1
            v = expression(depth + 1)
            assert pos[0] < len(s) and s[pos[0]] == ")"
            pos[0] += 1
            return chk(v)
        return number()

    def term(depth):
        v = factor(depth)
        while pos[0] < len(s) and s[pos[0]] == "*":
            pos[0] += 1
            v = chk(v * factor(depth))
        return v

    def expression(depth):
        neg = False
        if pos[0] < len(s) and s[pos[0]] == "-":
            neg = True
            pos[0] += 1
        v = term(depth)
        if neg:
            v = -v
        while pos[0] < len(s) and s[pos[0]] in "+-":
            op = s[pos[0]]
            pos[0] += 1
            w = term(depth)
            v = chk(v + w if op == "+" else v - w)
        return v

    v = expression(0)
    assert pos[0] == len(s), ("trailing characters", s[:60], pos[0])
    return v


def b_expr(expr):
    # an independent route: Python's own evaluator on a validated expression (literals have no leading zeros)
    return eval(expr, {"__builtins__": {}}, {})


def g_expr(r):
    while True:
        s = _gen_expr(r, r.randint(0, 3), r.randint(1, 4), r.choice([1, 9, 30]), 3)
        if len(s) <= 60:
            return [s]


def v_expr(tests):
    old = sys.getrecursionlimit()
    sys.setrecursionlimit(10000)
    try:
        for t in tests:
            s = t["args"][0]
            assert 1 <= len(s) <= 10000 and set(s) <= set("0123456789+-*()")
            assert _tokens_eval_checked(s) == t["expected"], ("reference disagrees with checker", s[:60])
    finally:
        sys.setrecursionlimit(old)


CHECKS["evaluate-bracket-expression"] = (b_expr, g_expr, "exact")
VALIDATE["evaluate-bracket-expression"] = v_expr
