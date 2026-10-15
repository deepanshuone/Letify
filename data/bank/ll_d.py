"""Problems: advanced linked lists (digit lists, group reversals, cache and editor simulations, random and child pointers).
Lists are passed as arrays of node values, head to tail. See data/lib.py for the registry."""
from lib import add, rnd, CHECKS, VALIDATE, gen_arr  # noqa: F401

TOPIC = "Linked List"

ENC = ("<p><strong>Encoding.</strong> A singly linked list is passed to your function as an array holding the node values "
       "from head to tail; an empty array is an empty list. You may build real nodes from it first, or work on the array directly. "
       "The result is also returned as an array of values from head to tail.</p>")

NODE = '''class ListNode:
    def __init__(self, val=0, nxt=None):
        self.val = val
        self.next = nxt


def build(vals):
    head = None
    for v in reversed(vals):
        head = ListNode(v, head)
    return head


def dump(head):
    out = []
    while head:
        out.append(head.val)
        head = head.next
    return out


'''


def _digits(r, n, lead_nonzero=True):
    a = [r.randint(0, 9) for _ in range(n)]
    if lead_nonzero and n > 1 and a[0] == 0:
        a[0] = r.randint(1, 9)
    return a


def _num_to_digits(x):
    return [int(c) for c in str(x)]


def _digits_to_num(d):
    return int("".join(map(str, d))) if d else 0


def _check_digits(d):
    assert all(0 <= x <= 9 for x in d)
    assert d[0] != 0 or len(d) == 1, "leading zero"


# ================================================================ EASY

p = add(
    id="plus-one-linked-list", title="Plus One on a Linked List", diff="Easy", topic=TOPIC,
    fn="plusOne", params=[("digits", "int[]")], ret="int[]", cmp="exact",
    desc="<p>A non-negative integer is stored in a singly linked list with one decimal digit per node, <em>most significant digit first</em>: the head holds the leading digit. The list is passed as an array of digits from head to tail. The number has no leading zeros, except that the number 0 itself is the single digit <code>[0]</code>.</p><p>Add one to the number and return its digits in the same encoding. For example <code>[1,2,9]</code> (the number 129) becomes <code>[1,3,0]</code>, and <code>[9,9]</code> becomes <code>[1,0,0]</code>.</p><p>The list is singly linked, so you cannot walk backwards. Try to solve it in one pass over the list without converting it to a number and without reversing it.</p>",
    constraints=["1 &le; digits.length &le; 5,000", "0 &le; digits[i] &le; 9", "digits[0] is not 0 unless digits is exactly [0]"],
    hints=["Adding one only changes the trailing run of 9s and the digit just before that run. Where does a carry stop?",
           "A carry is absorbed by the rightmost digit that is not 9. That digit grows by one and every 9 after it becomes 0. If every digit is 9, a new leading 1 is needed.",
           "Walk the list once and remember the last node whose value is not 9. Put a dummy node with value 0 in front of the list so that the 'all nines' case also has such a node. Increase it, zero everything after it, and drop the dummy if it stayed 0."],
    editorial=["Because the digits are stored most significant first, a carry travels towards the head, which a singly linked list cannot do directly. Instead of propagating a carry, find the place where it would stop: the last node whose digit is less than 9. Everything after it is a run of nines.",
               "Add a dummy node with digit 0 in front of the head; it plays the role of a leading zero, so such a node always exists. Scan once while recording the last non-9 node. Add one to it and set all following nodes to 0. If the dummy was the one that changed, it is the new leading 1 and becomes the head; otherwise skip it. Time O(n), extra space O(1). Reversing the list twice or using a stack also works but does more work than needed."],
    time="O(n)", space="O(1)",
    solution=NODE + '''def plusOne(digits):
    dummy = ListNode(0, build(digits))
    last = dummy
    cur = dummy.next
    while cur:
        if cur.val != 9:
            last = cur
        cur = cur.next
    last.val += 1
    cur = last.next
    while cur:
        cur.val = 0
        cur = cur.next
    return dump(dummy if dummy.val else dummy.next)
''',
    tests=[[[0]], [[9]], [[1, 2, 3]], [[1, 2, 9]], [[9, 9]], [[1, 9, 9, 8, 9]], [[4, 0, 9, 9]], [[8, 9]], [[1, 0, 0]],
           [[9, 9, 9, 9, 9, 9, 9]], [[7]]],
)
_r = rnd(4401)
p["tests"].append([[9] * 5000])
p["tests"].append([[1] + [9] * 4998 + [8]])
p["tests"].append([_digits(_r, 4997) + [9, 9, 9]])
p["tests"].append([_digits(_r, 5000)])


def b_plus_one(digits):
    return _num_to_digits(_digits_to_num(digits) + 1)


def g_plus_one(r):
    n = r.randint(1, 9)
    d = _digits(r, n)
    if r.random() < 0.4:
        k = r.randint(0, n)
        d = d[:n - k] + [9] * k
        if d[0] == 0 and len(d) > 1:
            d[0] = 1
    return [d]


def v_plus_one(tests):
    for t in tests:
        d = t["args"][0]
        assert 1 <= len(d) <= 5000
        _check_digits(d)
        _check_digits(t["expected"])


CHECKS["plus-one-linked-list"] = (b_plus_one, g_plus_one, "exact")
VALIDATE["plus-one-linked-list"] = v_plus_one

p = add(
    id="design-linked-list-operations", title="Linked List Edit Script", diff="Easy", topic=TOPIC, tier="extra",
    fn="applyListOps", params=[("ops", "int[][]")], ret="int[]", cmp="exact",
    desc="<p>Start with an empty singly linked list and apply a script of edits. Each edit is a triple <code>[type, a, b]</code>:</p><ul><li><code>[0, v, 0]</code>: insert a new node with value <code>v</code> at the head.</li><li><code>[1, v, 0]</code>: append a new node with value <code>v</code> at the tail.</li><li><code>[2, i, v]</code>: insert a new node with value <code>v</code> so that it becomes the node at index <code>i</code> (0-based). If <code>i</code> equals the current length this appends; if <code>i</code> is larger than the length the edit is ignored.</li><li><code>[3, i, 0]</code>: delete the node at index <code>i</code>. If there is no node at that index the edit is ignored.</li></ul><p>Return the values of the final list from head to tail. For example <code>[[0,5,0],[1,7,0],[2,1,9],[3,0,0]]</code> builds <code>[5]</code>, <code>[5,7]</code>, <code>[5,9,7]</code> and finally <code>[9,7]</code>.</p>",
    constraints=["0 &le; ops.length &le; 3,000", "type is 0, 1, 2 or 3", "-10<sup>9</sup> &le; v &le; 10<sup>9</sup>", "0 &le; i &le; 10,000", "Unused fields are 0"],
    hints=["Every edit is one of the standard linked list moves: insert at the front, insert at the back, insert in the middle, delete.",
           "A dummy node placed before the head removes all special cases for 'index 0': to edit position <code>i</code> you stop at the node just before it.",
           "Keep a dummy head and optionally a tail pointer. For index edits walk <code>i</code> steps from the dummy to find the predecessor; if you run off the end before taking <code>i</code> steps (insert) or find no node after the predecessor (delete), ignore the edit."],
    editorial=["Use a dummy node whose <code>next</code> is the real head. Then inserting at the head is inserting after the dummy, and for any index <code>i</code> the predecessor is the node reached after <code>i</code> steps from the dummy. Insert: link a new node after the predecessor. Delete: set <code>pred.next = pred.next.next</code> when <code>pred.next</code> exists.",
               "The walk can only go as far as the list is long, so an index beyond the length is detected when the walk hits null early (insert) or when the predecessor has no successor (delete). Each edit costs O(i) (O(1) for the head, and O(n) for an append unless you keep a tail pointer), so the whole script is O(q &middot; n) in the worst case, which is fine for 3,000 edits."],
    time="O(q * n)", space="O(n)",
    solution=NODE + '''def applyListOps(ops):
    dummy = ListNode(0)
    for t, a, b in ops:
        if t == 0:
            dummy.next = ListNode(a, dummy.next)
        elif t == 1:
            cur = dummy
            while cur.next:
                cur = cur.next
            cur.next = ListNode(a)
        elif t == 2:
            cur = dummy
            steps = 0
            while steps < a and cur:
                cur = cur.next
                steps += 1
            if cur:
                cur.next = ListNode(b, cur.next)
        else:
            cur = dummy
            steps = 0
            while steps < a and cur:
                cur = cur.next
                steps += 1
            if cur and cur.next:
                cur.next = cur.next.next
    return dump(dummy.next)
''',
    tests=[[[[0, 5, 0], [1, 7, 0], [2, 1, 9], [3, 0, 0]]], [[]], [[[3, 0, 0]]], [[[2, 1, 4]]], [[[2, 0, 4]]],
           [[[1, 1, 0], [1, 2, 0], [1, 3, 0], [2, 3, 8], [2, 5, 8], [3, 3, 0], [3, 3, 0]]],
           [[[0, 1, 0], [0, 2, 0], [0, 3, 0], [3, 2, 0], [3, 1, 0], [3, 0, 0], [3, 0, 0]]],
           [[[1, -1000000000, 0], [0, 1000000000, 0], [2, 1, 0], [2, 4, 7], [3, 10000, 0]]],
           [[[0, 4, 0], [2, 1, 6], [2, 1, 5], [2, 1, 3], [3, 2, 0], [0, 9, 0]]]],
)


def _list_ops(r, q, maxv=10 ** 9, maxi=10):
    ops = []
    for _ in range(q):
        t = r.choice([0, 1, 2, 2, 3, 3])
        if t in (0, 1):
            ops.append([t, r.randint(-maxv, maxv), 0])
        elif t == 2:
            ops.append([2, r.randint(0, maxi), r.randint(-maxv, maxv)])
        else:
            ops.append([3, r.randint(0, maxi), 0])
    return ops


_r = rnd(4402)
p["tests"].append([[[0, _r.randint(-99, 99), 0] if i % 3 == 0 else ([1, _r.randint(-99, 99), 0] if i % 3 == 1 else [3, _r.randint(0, 3), 0]) for i in range(3000)]])
p["tests"].append([_list_ops(_r, 3000, 10 ** 9, 700)])
p["tests"].append([[[1, i, 0] for i in range(1500)] + [[2, _r.randint(0, 1500 + i), i] for i in range(1500)]])


def b_list_ops(ops):
    a = []
    for t, x, y in ops:
        if t == 0:
            a.insert(0, x)
        elif t == 1:
            a.append(x)
        elif t == 2:
            if x <= len(a):
                a.insert(x, y)
        else:
            if x < len(a):
                del a[x]
    return a


def g_list_ops(r):
    return [_list_ops(r, r.randint(0, 12), 9, 6)]


def v_list_ops(tests):
    for t in tests:
        ops = t["args"][0]
        assert len(ops) <= 3000
        for o in ops:
            assert len(o) == 3 and o[0] in (0, 1, 2, 3)
            if o[0] in (0, 1):
                assert abs(o[1]) <= 10 ** 9 and o[2] == 0
            elif o[0] == 2:
                assert 0 <= o[1] <= 10000 and abs(o[2]) <= 10 ** 9
            else:
                assert 0 <= o[1] <= 10000 and o[2] == 0


CHECKS["design-linked-list-operations"] = (b_list_ops, g_list_ops, "exact")
VALIDATE["design-linked-list-operations"] = v_list_ops

p = add(
    id="browser-history-simulation", title="Browser History Simulation", diff="Easy", topic=TOPIC,
    fn="browserHistory", params=[("home", "int"), ("ops", "int[][]")], ret="int[]", cmp="exact",
    desc="<p>A browser starts on the page with id <code>home</code>. It keeps a history of the visited pages as a doubly linked chain and a current position in that chain. Each operation is a pair <code>[type, x]</code>:</p><ul><li><code>[0, page]</code>: visit <code>page</code>. All pages <em>after</em> the current position (the forward history) are discarded, the new page is appended and becomes current.</li><li><code>[1, steps]</code>: go back up to <code>steps</code> pages. You stop early at the oldest page of the history.</li><li><code>[2, steps]</code>: go forward up to <code>steps</code> pages. You stop early at the newest page of the history.</li></ul><p>Return an array with the id of the current page after every operation. For example with <code>home = 1</code> and <code>ops = [[0,2],[0,3],[1,1],[2,5],[1,5],[0,9]]</code> the answer is <code>[2,3,2,3,1,9]</code>: after visiting 2 and 3 the history is <code>1,2,3</code>; going back 1 gives 2, forward 5 stops at 3, back 5 stops at 1, and visiting 9 replaces the forward history so it becomes <code>1,9</code>.</p>",
    constraints=["1 &le; ops.length &le; 5,000", "Visited page ids and home are in the range 1..10<sup>9</sup>; the same page may be visited many times", "0 &le; steps &le; 10,000", "type is 0, 1 or 2"],
    hints=["A history in which you move one step at a time in both directions is exactly a doubly linked list with a 'current' pointer.",
           "A visit creates a new node after the current one, and simply throws the old forward part away by overwriting <code>cur.next</code>.",
           "For back and forward, follow <code>prev</code> or <code>next</code> pointers while the step counter lasts and the pointer exists. Output <code>cur.val</code> after every operation. (An array with an index and a 'length' that you shrink on visit also works.)"],
    editorial=["Model the history as a doubly linked list. Keep a pointer <code>cur</code>. Visiting creates a node <code>n</code>, sets <code>cur.next = n</code>, <code>n.prev = cur</code> and moves <code>cur</code> to <code>n</code>; the old forward nodes become unreachable at once because nothing points to them any more.",
               "Moving back or forward walks at most <code>steps</code> links but stops at the ends. A single move costs O(min(steps, length)), so the total is O(q &middot; n) in the worst case, which is fine here. An equivalent approach stores pages in an array, keeps the current index and the logical length, and on a visit overwrites the slot after the index; then back and forward are O(1) index arithmetic with clamping."],
    time="O(q * n)", space="O(q)",
    solution='''class Page:
    def __init__(self, v):
        self.v = v
        self.prev = None
        self.next = None


def browserHistory(home, ops):
    cur = Page(home)
    out = []
    for t, x in ops:
        if t == 0:
            n = Page(x)
            cur.next = n
            n.prev = cur
            cur = n
        elif t == 1:
            while x > 0 and cur.prev:
                cur = cur.prev
                x -= 1
        else:
            while x > 0 and cur.next:
                cur = cur.next
                x -= 1
        out.append(cur.v)
    return out
''',
    tests=[[1, [[0, 2], [0, 3], [1, 1], [2, 5], [1, 5], [0, 9]]], [5, [[1, 3]]], [5, [[2, 3]]], [7, [[0, 8], [1, 0], [2, 0]]],
           [1, [[0, 2], [1, 1], [0, 3], [2, 1], [1, 1], [1, 1]]], [4, [[0, 4], [0, 4], [1, 1], [1, 1], [2, 2]]],
           [10 ** 9, [[0, 1], [0, 10 ** 9], [1, 10000], [2, 10000]]], [2, [[0, 3], [0, 4], [0, 5], [1, 2], [0, 6], [2, 1], [1, 1]]],
           [3, [[1, 1], [0, 3], [1, 1], [2, 1], [1, 1], [1, 1], [0, 8], [1, 1]]]],
)


def _hist_ops(r, q, maxpage, maxsteps):
    ops = []
    for _ in range(q):
        t = r.choice([0, 0, 1, 2])
        ops.append([t, r.randint(1, maxpage) if t == 0 else r.randint(0, maxsteps)])
    return ops


_r = rnd(4403)
p["tests"].append([_r.randint(1, 10 ** 9), _hist_ops(_r, 2500, 10 ** 9, 20)])
p["tests"].append([1, [[0, i + 2] for i in range(1500)] + [[1, 1400], [2, 1], [0, 5], [1, 10000], [2, 3]] + _hist_ops(_r, 1000, 1000, 1500)])
p["tests"].append([6, _hist_ops(_r, 2500, 50, 3)])


def b_history(home, ops):
    h, i, out = [home], 0, []
    for t, x in ops:
        if t == 0:
            h = h[:i + 1] + [x]
            i += 1
        elif t == 1:
            i = max(0, i - x)
        else:
            i = min(len(h) - 1, i + x)
        out.append(h[i])
    return out


def g_history(r):
    return [r.randint(1, 5), _hist_ops(r, r.randint(1, 14), 5, 4)]


def v_history(tests):
    for t in tests:
        home, ops = t["args"]
        assert 1 <= home <= 10 ** 9 and 1 <= len(ops) <= 5000
        for ty, x in ops:
            assert ty in (0, 1, 2)
            if ty == 0:
                assert 1 <= x <= 10 ** 9
            else:
                assert 0 <= x <= 10000


CHECKS["browser-history-simulation"] = (b_history, g_history, "exact")
VALIDATE["browser-history-simulation"] = v_history

# ================================================================ MEDIUM

p = add(
    id="add-numbers-most-significant-first", title="Add Two Numbers Stored Front to Back", diff="Medium", topic=TOPIC,
    fn="addLists", params=[("a", "int[]"), ("b", "int[]")], ret="int[]", cmp="exact",
    desc="<p>Two non-negative integers are stored in singly linked lists, one decimal digit per node, <em>most significant digit first</em> (the head holds the leading digit). Each list is passed as an array of digits from head to tail. Neither number has leading zeros, except that the number 0 itself is <code>[0]</code>.</p><p>Return the sum as a list of digits in the same encoding, again without leading zeros. For example <code>a = [7,2,4,3]</code> and <code>b = [5,6,4]</code> represent 7243 and 564, and the answer is <code>[7,8,0,7]</code>.</p><p>The numbers can have thousands of digits, so do not convert them to machine integers. Solve it without reversing the input lists if you can.</p>",
    constraints=["1 &le; a.length, b.length &le; 5,000", "0 &le; a[i], b[i] &le; 9", "No leading zeros (except for the number 0 itself)"],
    hints=["Addition starts at the least significant digit, which is at the <em>end</em> of both lists, and the lists may have different lengths.",
           "Either push the digits of each list on a stack, or align the lists by their lengths. With stacks the last digits come off first, exactly in the order addition needs.",
           "Pop one digit from each stack (use 0 when a stack is empty) plus the carry, create a node for <code>sum % 10</code> and put it in front of the result built so far. Keep going while any stack has digits or the carry is non-zero."],
    editorial=["Do ordinary column addition from the right. A stack per list turns the front-to-back lists into back-to-front streams. Repeatedly pop a digit from each non-empty stack, add the carry, and prepend a new node with <code>total % 10</code> to the answer list; the carry becomes <code>total // 10</code>. Prepending a node is O(1) on a singly linked list, so the answer comes out already in most-significant-first order.",
               "Finish when both stacks are empty and no carry is left (a final carry creates a new leading 1). Time O(n + m), space O(n + m) for the stacks. A stack-free variant first finds the lengths, then recursively adds the aligned digits and handles the carry on the way back."],
    time="O(n + m)", space="O(n + m)",
    solution=NODE + '''def addLists(a, b):
    sa = list(a)
    sb = list(b)
    head = None
    carry = 0
    while sa or sb or carry:
        total = carry
        if sa:
            total += sa.pop()
        if sb:
            total += sb.pop()
        head = ListNode(total % 10, head)
        carry = total // 10
    return dump(head)
''',
    tests=[[[7, 2, 4, 3], [5, 6, 4]], [[0], [0]], [[5], [5]], [[9, 9, 9], [1]], [[1], [9, 9, 9]], [[1, 2, 3], [4, 5, 6]],
           [[5, 0, 0, 0], [5, 0, 0, 0]], [[9, 9], [9, 9]], [[1, 0, 0, 0, 0], [9]], [[0], [3, 4]], [[8, 1], [1, 9]]],
)
_r = rnd(4404)
p["tests"].append([[9] * 5000, [1]])
p["tests"].append([_digits(_r, 5000), _digits(_r, 3333)])
p["tests"].append([_digits(_r, 4000), [9] * 5000 if False else _digits(_r, 4500)])


def b_add_msb(a, b):
    return _num_to_digits(_digits_to_num(a) + _digits_to_num(b))


def g_add_msb(r):
    return [_digits(r, r.randint(1, 8)), _digits(r, r.randint(1, 8))]


def v_add_msb(tests):
    for t in tests:
        a, b = t["args"]
        assert 1 <= len(a) <= 5000 and 1 <= len(b) <= 5000
        _check_digits(a)
        _check_digits(b)
        _check_digits(t["expected"])


CHECKS["add-numbers-most-significant-first"] = (b_add_msb, g_add_msb, "exact")
VALIDATE["add-numbers-most-significant-first"] = v_add_msb

p = add(
    id="reverse-even-length-groups", title="Reverse Nodes in Even-Length Groups", diff="Medium", topic=TOPIC,
    fn="reverseEvenGroups", params=[("nums", "int[]")], ret="int[]", cmp="exact",
    desc=ENC + "<p>Cut the list into consecutive groups whose <em>intended</em> sizes are 1, 2, 3, 4, ... (the first group has 1 node, the second 2 nodes, the third 3 nodes, and so on). The last group takes whatever is left, so its real size may be smaller than its intended size.</p><p>Reverse every group whose <em>real</em> size is even, and leave groups of odd size unchanged. Return the resulting list. For example <code>[5,2,6,3,9,1,7,3,8,4]</code> splits into <code>[5] [2,6] [3,9,1] [7,3,8,4]</code>; the groups of sizes 2 and 4 are reversed, giving <code>[5,6,2,3,9,1,4,8,3,7]</code>. And <code>[1,1,0,6]</code> splits into <code>[1] [1,0] [6]</code> (the last group wanted 3 nodes but only 1 is left) and gives <code>[1,0,1,6]</code>.</p>",
    constraints=["0 &le; nums.length &le; 5,000", "-10<sup>9</sup> &le; nums[i] &le; 10<sup>9</sup>"],
    hints=["The group boundaries are determined by position only, so you can find them while walking: group number <code>g</code> starts right after the previous one and wants <code>g</code> nodes.",
           "For each group, first count how many nodes it really has (at most <code>g</code>, fewer at the end of the list). Then decide: reverse if that real count is even.",
           "Keep a pointer <code>prev</code> to the node just before the group. To reverse <code>cnt</code> nodes in place, take the group's first node as the future tail and repeatedly move the node after the tail to the front of the group, <code>cnt - 1</code> times. Afterwards the tail is the new <code>prev</code>; if you did not reverse, just advance <code>prev</code> by <code>cnt</code> nodes."],
    editorial=["Walk with a pointer <code>prev</code> that stands right before the current group and a variable <code>size</code> = 1, 2, 3, ... For each group count the real number of nodes <code>cnt = min(size, remaining)</code> by stepping ahead from <code>prev.next</code>. If <code>cnt</code> is odd, simply move <code>prev</code> forward by <code>cnt</code> nodes.",
               "If <code>cnt</code> is even, reverse the group in place: the first node of the group, <code>tail</code>, will end up last. Do <code>cnt - 1</code> times: <code>nxt = tail.next; tail.next = nxt.next; nxt.next = prev.next; prev.next = nxt</code>, which moves the node after the tail to the front of the group. Then set <code>prev = tail</code>. Every node is counted once and relinked at most once, so the time is O(n) with O(1) extra space. The only subtle point is the last group: its parity depends on how many nodes are really there, not on the intended size."],
    time="O(n)", space="O(1)",
    solution=NODE + '''def reverseEvenGroups(nums):
    dummy = ListNode(0, build(nums))
    prev = dummy
    size = 1
    while prev.next:
        cnt = 0
        node = prev.next
        while node and cnt < size:
            node = node.next
            cnt += 1
        if cnt % 2 == 0:
            tail = prev.next
            for _ in range(cnt - 1):
                nxt = tail.next
                tail.next = nxt.next
                nxt.next = prev.next
                prev.next = nxt
            prev = tail
        else:
            for _ in range(cnt):
                prev = prev.next
        size += 1
    return dump(dummy.next)
''',
    tests=[[[5, 2, 6, 3, 9, 1, 7, 3, 8, 4]], [[1, 1, 0, 6]], [[]], [[1]], [[1, 2]], [[1, 2, 3]], [[1, 2, 3, 4]],
           [[1, 2, 3, 4, 5, 6]], [[1, 2, 3, 4, 5, 6, 7, 8, 9, 10]], [[7, 7, 7, 7, 7]], [[-5, 10 ** 9, -10 ** 9, 0, 3, 8, 1]]],
)
_r = rnd(4405)
p["tests"].append([_r.sample(range(-10 ** 9, 10 ** 9), 3500)])
p["tests"].append([list(range(1, 3004))])
p["tests"].append([[_r.randint(0, 3) for _ in range(3000)]])


def b_even_groups(nums):
    out, i, size = [], 0, 1
    while i < len(nums):
        g = nums[i:i + size]
        out += g[::-1] if len(g) % 2 == 0 else g
        i += size
        size += 1
    return out


def g_even_groups(r):
    return [gen_arr(r, -9, 9, 0, 16)]


def v_even_groups(tests):
    for t in tests:
        assert len(t["args"][0]) <= 5000
        assert sorted(t["expected"]) == sorted(t["args"][0])


CHECKS["reverse-even-length-groups"] = (b_even_groups, g_even_groups, "exact")
VALIDATE["reverse-even-length-groups"] = v_even_groups

p = add(
    id="lru-cache-simulation", title="LRU Cache Simulation", diff="Medium", topic=TOPIC, tier="must",
    fn="lruCacheGets", params=[("capacity", "int"), ("ops", "int[][]")], ret="int[]", cmp="exact",
    desc="<p>Simulate a cache that holds at most <code>capacity</code> key-value pairs and evicts the <em>least recently used</em> pair when it is full. A pair is &quot;used&quot; whenever it is read by a hit or written. Each operation is a triple <code>[type, key, value]</code>:</p><ul><li><code>[0, key, 0]</code> (get): if <code>key</code> is in the cache, report its value and mark it as most recently used; otherwise report <code>-1</code>.</li><li><code>[1, key, value]</code> (put): if <code>key</code> is already in the cache, replace its value and mark it as most recently used. Otherwise insert it as the most recently used pair; if the cache already held <code>capacity</code> pairs, first evict the least recently used one.</li></ul><p>Return the reported values of all get operations in order. For example with <code>capacity = 2</code> and <code>ops = [[1,1,10],[1,2,20],[0,1,0],[1,3,30],[0,2,0],[0,3,0],[1,1,11],[0,1,0]]</code> the answer is <code>[10,-1,30,11]</code>: putting key 3 evicts key 2, because key 1 was just read.</p><p>Aim for O(1) per operation. This is the classic hash map + doubly linked list design.</p>",
    constraints=["1 &le; capacity &le; 1,000", "1 &le; ops.length &le; 3,000", "type is 0 (get) or 1 (put)", "0 &le; key &le; 10<sup>6</sup>, 0 &le; value &le; 10<sup>9</sup>", "For a get the value field is 0"],
    hints=["You need two things at once: find a key quickly, and know which key is the least recently used. One structure per job.",
           "A hash map from key to node finds entries in O(1). A doubly linked list ordered by recency (most recent at the front) can move any node to the front and remove the tail in O(1), because deleting a node needs <code>prev</code> and <code>next</code>.",
           "Use dummy head and tail nodes. Helpers: <code>unlink(node)</code> and <code>push_front(node)</code>. A hit is unlink + push_front. A put of a new key on a full cache first removes <code>tail.prev</code> from both the list and the map. Store the key inside each node so you can delete it from the map when you evict it."],
    editorial=["Keep a hash map <code>key -> node</code> and a doubly linked list of nodes ordered from most to least recently used, with sentinel nodes at both ends so that no case is special. Every get hit and every put moves its node to the front; the eviction victim is always the node before the tail sentinel.",
               "Each operation is a map lookup plus a constant number of pointer changes, so it runs in O(1) and the whole script in O(q). The node must remember its key: when you evict the last node you have to delete that key from the map. A singly linked list would not work because removing an arbitrary node in O(1) needs its predecessor."],
    time="O(q)", space="O(capacity)",
    solution='''class Node:
    __slots__ = ("key", "val", "prev", "next")

    def __init__(self, key=0, val=0):
        self.key = key
        self.val = val
        self.prev = None
        self.next = None


def lruCacheGets(capacity, ops):
    head, tail = Node(), Node()
    head.next = tail
    tail.prev = head
    table = {}

    def unlink(n):
        n.prev.next = n.next
        n.next.prev = n.prev

    def push_front(n):
        n.next = head.next
        n.prev = head
        head.next.prev = n
        head.next = n

    out = []
    for t, k, v in ops:
        n = table.get(k)
        if t == 0:
            if n is None:
                out.append(-1)
            else:
                unlink(n)
                push_front(n)
                out.append(n.val)
        elif n is not None:
            n.val = v
            unlink(n)
            push_front(n)
        else:
            if len(table) == capacity:
                lru = tail.prev
                unlink(lru)
                del table[lru.key]
            n = Node(k, v)
            table[k] = n
            push_front(n)
    return out
''',
    tests=[[2, [[1, 1, 10], [1, 2, 20], [0, 1, 0], [1, 3, 30], [0, 2, 0], [0, 3, 0], [1, 1, 11], [0, 1, 0]]],
           [1, [[0, 5, 0]]], [1, [[1, 1, 1], [1, 2, 2], [0, 1, 0], [0, 2, 0]]],
           [2, [[1, 1, 1], [1, 2, 2], [1, 1, 5], [1, 3, 3], [0, 1, 0], [0, 2, 0], [0, 3, 0]]],
           [3, [[1, 1, 1], [1, 2, 2], [1, 3, 3], [0, 1, 0], [0, 2, 0], [1, 4, 4], [0, 3, 0], [0, 1, 0], [0, 2, 0], [0, 4, 0]]],
           [2, [[1, 0, 10 ** 9], [0, 0, 0], [1, 10 ** 6, 0], [1, 7, 7], [0, 0, 0], [0, 10 ** 6, 0], [0, 7, 0]]],
           [4, [[1, 1, 1], [1, 2, 2], [1, 3, 3], [1, 4, 4], [1, 1, 9], [1, 5, 5], [0, 2, 0], [0, 1, 0]]],
           [2, [[0, 1, 0], [1, 1, 1], [0, 1, 0], [1, 1, 2], [0, 1, 0]]]],
)


def _cache_ops(r, q, keys, get_prob, maxv=10 ** 9):
    ops = []
    for _ in range(q):
        k = r.choice(keys)
        if r.random() < get_prob:
            ops.append([0, k, 0])
        else:
            ops.append([1, k, r.randint(0, maxv)])
    return ops


_r = rnd(4406)
p["tests"].append([300, _cache_ops(_r, 3000, list(range(0, 450)), 0.5, 999)])
p["tests"].append([1000, _cache_ops(_r, 3000, [_r.randint(0, 10 ** 6) for _ in range(1300)], 0.45, 99999)])
p["tests"].append([7, _cache_ops(_r, 3000, list(range(12)), 0.5, 99)])


def b_lru(capacity, ops):
    order, out = [], []  # list of [key, value], oldest first
    for t, k, v in ops:
        idx = next((i for i, e in enumerate(order) if e[0] == k), -1)
        if t == 0:
            if idx < 0:
                out.append(-1)
            else:
                e = order.pop(idx)
                order.append(e)
                out.append(e[1])
        else:
            if idx >= 0:
                order.pop(idx)
            elif len(order) == capacity:
                order.pop(0)
            order.append([k, v])
    return out


def g_lru(r):
    return [r.randint(1, 4), _cache_ops(r, r.randint(1, 20), list(range(6)), 0.5, 9)]


def v_lru(tests):
    for t in tests:
        cap, ops = t["args"]
        assert 1 <= cap <= 1000 and 1 <= len(ops) <= 3000
        for ty, k, v in ops:
            assert ty in (0, 1) and 0 <= k <= 10 ** 6 and 0 <= v <= 10 ** 9
            assert ty == 1 or v == 0
        assert len(t["expected"]) == sum(1 for o in ops if o[0] == 0)


CHECKS["lru-cache-simulation"] = (b_lru, g_lru, "exact")
VALIDATE["lru-cache-simulation"] = v_lru

p = add(
    id="copy-list-with-random-pointer", title="Copy a List with Random Pointers", diff="Medium", topic=TOPIC, tier="must",
    fn="copyRandomList", params=[("vals", "int[]"), ("random", "int[]")], ret="int[][]", cmp="exact",
    desc="<p>Every node of a singly linked list has, besides <code>next</code>, a <code>random</code> pointer that points to any node of the same list (possibly itself) or to nothing.</p><p><strong>Encoding.</strong> The list has <code>n</code> nodes. <code>vals[i]</code> is the value of the i-th node (0-based, head first) and <code>random[i]</code> is the index of the node its random pointer points to, or <code>-1</code> for null. Both arrays have the same length.</p><p>Build a <em>deep copy</em> of the list: <code>n</code> brand new nodes with the same values, whose <code>next</code> and <code>random</code> pointers only point to nodes of the copy, never to the original. Return the copy in the same form, one row per node from head to tail: <code>[value, randomIndex]</code>, where <code>randomIndex</code> is the position of the copy's random target within the copy, or <code>-1</code>.</p><p>For example <code>vals = [7,13,11]</code> with <code>random = [-1,0,2]</code> (the first node points nowhere, the second points to the first, the third to itself) gives <code>[[7,-1],[13,0],[11,2]]</code>.</p><p>The original list must stay unchanged. Try to do it in O(n) time with O(1) extra space apart from the copy itself, i.e. without a hash map.</p>",
    constraints=["0 &le; vals.length &le; 2,000", "random.length = vals.length", "-1 &le; random[i] &lt; vals.length", "-10<sup>9</sup> &le; vals[i] &le; 10<sup>9</sup>"],
    hints=["The <code>next</code> pointers are easy to copy in one pass. The problem is a <code>random</code> pointer of the copy that needs the <em>copy</em> of a node that may not exist yet.",
           "A hash map from original node to copied node solves it in two passes: first create all copies, then wire <code>next</code> and <code>random</code> through the map. To avoid the map, you need a different way to find 'the copy of node x'.",
           "Interleave: insert each copy directly after its original (A, A', B, B', ...). Then the copy of <code>x.random</code> is simply <code>x.random.next</code>. Finally pull the two lists apart again, restoring the original."],
    editorial=["Map approach: pass 1 creates a copy of every node and stores <code>copy[orig]</code>; pass 2 sets <code>copy[orig].next = copy[orig.next]</code> and <code>copy[orig].random = copy[orig.random]</code>. That is O(n) time and O(n) extra space for the map.",
               "O(1)-extra-space approach in three passes. (1) For each original node insert its copy right after it. (2) For each original node <code>x</code> with a random pointer set <code>x.next.random = x.random.next</code>: the node after any original is its copy, so this is exactly 'the copy of the random target'. (3) Walk the interleaved list and split it into the original list (restored) and the copy list. Finally read the copy list out; the index of a random target is its position in that list. Total O(n) time."],
    time="O(n)", space="O(1)",
    solution='''class Node:
    def __init__(self, val):
        self.val = val
        self.next = None
        self.random = None


def copyRandomList(vals, random):
    n = len(vals)
    if n == 0:
        return []
    nodes = [Node(v) for v in vals]
    for i in range(n):
        if i + 1 < n:
            nodes[i].next = nodes[i + 1]
        if random[i] >= 0:
            nodes[i].random = nodes[random[i]]
    head = nodes[0]
    # 1. weave a copy behind every node
    cur = head
    while cur:
        c = Node(cur.val)
        c.next = cur.next
        cur.next = c
        cur = c.next
    # 2. copy the random pointers
    cur = head
    while cur:
        if cur.random:
            cur.next.random = cur.random.next
        cur = cur.next.next
    # 3. split the two lists
    new_head = head.next
    cur = head
    while cur:
        c = cur.next
        cur.next = c.next
        c.next = c.next.next if c.next else None
        cur = cur.next
    # read the copy out
    index = {}
    order = []
    c = new_head
    while c:
        index[id(c)] = len(order)
        order.append(c)
        c = c.next
    return [[c.val, index[id(c.random)] if c.random else -1] for c in order]
''',
    tests=[[[7, 13, 11], [-1, 0, 2]], [[], []], [[5], [-1]], [[5], [0]], [[1, 2], [1, 0]], [[1, 1, 1, 1], [3, 2, 1, 0]],
           [[1, 2, 3, 4, 5], [-1, -1, -1, -1, -1]], [[10 ** 9, -10 ** 9, 0], [2, -1, 0]], [[4, 5, 6, 7], [0, 0, 0, 0]],
           [[3, 1, 4, 1, 5, 9], [5, 4, 3, -1, 1, 0]]],
)
_r = rnd(4407)
p["tests"].append([[_r.randint(-10 ** 9, 10 ** 9) for _ in range(2000)], [_r.randint(-1, 1999) for _ in range(2000)]])
p["tests"].append([[_r.randint(-99, 99) for _ in range(2000)], [(i * 7 + 3) % 2000 for i in range(2000)]])


def b_copy(vals, random):
    n = len(vals)
    clones = [{"v": vals[i], "r": random[i]} for i in range(n)]
    return [[c["v"], c["r"]] for c in clones]


def g_copy(r):
    n = r.randint(0, 9)
    return [gen_arr(r, -9, 9, n, n), [r.randint(-1, n - 1) for _ in range(n)]]


def v_copy(tests):
    for t in tests:
        vals, random = t["args"]
        assert len(vals) == len(random) <= 2000
        assert all(-1 <= x < len(vals) for x in random)
        assert t["expected"] == [[v, x] for v, x in zip(vals, random)]


CHECKS["copy-list-with-random-pointer"] = (b_copy, g_copy, "exact")
VALIDATE["copy-list-with-random-pointer"] = v_copy

p = add(
    id="flatten-multilevel-doubly-linked-list", title="Flatten a Multilevel Linked List", diff="Medium", topic=TOPIC,
    fn="flattenMultilevel", params=[("chains", "int[][]"), ("links", "int[][]")], ret="int[]", cmp="exact",
    desc="<p>A multilevel list is made of several doubly linked <em>chains</em>. Besides <code>prev</code> and <code>next</code>, a node may have a <code>child</code> pointer to the head of another chain, which can again contain nodes with children of their own.</p><p><strong>Encoding.</strong> <code>chains[c]</code> holds the values of chain number <code>c</code> from head to tail, and chain 0 is the top-level list. Each row of <code>links</code> is <code>[r, p, c]</code> and means: the node at position <code>p</code> of chain <code>r</code> has chain <code>c</code> as its child. Every chain other than 0 is the child of exactly one node, a node has at most one child, and the child's chain number is always larger than the parent's (<code>c &gt; r</code>), so there are no cycles.</p><p>Flatten the structure into one single-level list: after a node with a child comes the <em>entire</em> child chain (flattened in the same way), and only then the node's former <code>next</code>. Return the values of the flattened list from head to tail. For example <code>chains = [[1,2,3],[7,8],[11]]</code> and <code>links = [[0,1,1],[1,0,2]]</code>: node 2 has child chain <code>[7,8]</code> and node 7 has child chain <code>[11]</code>, so the result is <code>[1,2,7,11,8,3]</code>.</p><p>Try to do it by relinking the nodes in place in O(n) time, without recursion.</p>",
    constraints=["1 &le; chains.length &le; 2,000", "Every chain is non-empty; the total number of nodes is at most 5,000", "-10<sup>9</sup> &le; value &le; 10<sup>9</sup>", "links.length = chains.length - 1; each link has c &gt; r, each chain 1..chains.length-1 appears once as c, and each node (r, p) appears at most once"],
    hints=["The required order is a depth-first walk: a node, then everything below it, then its next node.",
           "Walk along the top-level chain. When the current node has a child, splice the whole child chain between the node and its old <code>next</code>, and keep walking: the nodes of the spliced chain are now ordinary nodes of the same list, so their own children are handled when you reach them.",
           "Splice step: save <code>nxt = cur.next</code>, find the <code>tail</code> of the child chain, then link <code>cur.next = child</code>, <code>child.prev = cur</code>, <code>tail.next = nxt</code>, and <code>nxt.prev = tail</code> if <code>nxt</code> exists. Clear <code>cur.child</code>. Each chain's tail is searched exactly once, so the total work is O(n)."],
    editorial=["Recursion or an explicit stack would work, but there is a neat in-place scan. Move a pointer <code>cur</code> along the list. If <code>cur</code> has no child, step to <code>cur.next</code>. If it has one, cut the list after <code>cur</code>, insert the complete child chain there, reconnect the cut-off rest after the child chain's tail, and clear the child pointer. Do not skip ahead: stepping to the new <code>cur.next</code> (the child's head) means grandchildren are expanded in turn, before the old rest of the list is reached.",
               "Every chain is spliced exactly once and its tail is found by walking that chain once, since the chain has not been modified before it is spliced. Hence O(n) time and O(1) extra space beyond the nodes. In an array-encoded input, the nodes are first built from <code>chains</code> and <code>links</code>; the answer is read by walking <code>next</code> from the head."],
    time="O(n)", space="O(1)",
    solution='''class Node:
    def __init__(self, val):
        self.val = val
        self.prev = None
        self.next = None
        self.child = None


def flattenMultilevel(chains, links):
    nodes = []
    for row in chains:
        ns = [Node(v) for v in row]
        for i in range(len(ns) - 1):
            ns[i].next = ns[i + 1]
            ns[i + 1].prev = ns[i]
        nodes.append(ns)
    for r, pos, c in links:
        nodes[r][pos].child = nodes[c][0]
    head = nodes[0][0]
    cur = head
    while cur:
        if cur.child:
            nxt = cur.next
            child = cur.child
            tail = child
            while tail.next:
                tail = tail.next
            cur.next = child
            child.prev = cur
            cur.child = None
            tail.next = nxt
            if nxt:
                nxt.prev = tail
        cur = cur.next
    out = []
    cur = head
    while cur:
        out.append(cur.val)
        cur = cur.next
    return out
''',
    tests=[[[[1, 2, 3], [7, 8], [11]], [[0, 1, 1], [1, 0, 2]]], [[[4]], []], [[[1, 2, 3]], []], [[[1, 2], [3]], [[0, 0, 1]]],
           [[[1, 2], [3]], [[0, 1, 1]]], [[[1, 2, 3], [4, 5], [6, 7]], [[0, 0, 1], [0, 2, 2]]],
           [[[1, 2, 3], [4, 5, 6], [7], [8, 9]], [[0, 1, 1], [1, 2, 2], [1, 0, 3]]],
           [[[1], [2], [3], [4], [5]], [[0, 0, 1], [1, 0, 2], [2, 0, 3], [3, 0, 4]]],
           [[[10, 20], [-1, -2, -3], [5]], [[0, 0, 1], [0, 1, 2]]],
           [[[1, 2, 3, 4], [5, 6], [7, 8], [9]], [[0, 0, 1], [0, 1, 2], [0, 3, 3]]]],
)


def _gen_multilevel(r, total, chains_n, vlo=-999, vhi=999, deep=False):
    """Random multilevel structure with chains_n chains and about `total` nodes."""
    sizes = [1] * chains_n
    for _ in range(max(0, total - chains_n)):
        sizes[r.randrange(chains_n)] += 1
    chains = [[r.randint(vlo, vhi) for _ in range(s)] for s in sizes]
    free = [(0, i) for i in range(sizes[0])]
    links = []
    for c in range(1, chains_n):
        if deep:
            cand = [(c - 1, 0)]
            parent = cand[0]
        else:
            cands = [f for f in free if f[0] < c]
            parent = r.choice(cands)
        free.remove(parent) if parent in free else None
        links.append([parent[0], parent[1], c])
        free += [(c, i) for i in range(sizes[c])]
    return chains, links


def _gen_multilevel_safe(r, total, chains_n, **kw):
    # every chain needs at least one free node above it, always true since every chain keeps at least one node and
    # the chosen parents are removed one at a time; guard against exhausting the free list
    chains_n = min(chains_n, total)
    while True:
        try:
            return _gen_multilevel(r, total, chains_n, **kw)
        except IndexError:
            chains_n -= 1


_r = rnd(4408)
_ch, _lk = _gen_multilevel_safe(_r, 3500, 1000)
p["tests"].append([_ch, _lk])
_ch, _lk = _gen_multilevel_safe(_r, 2500, 1200, deep=True)
p["tests"].append([_ch, _lk])
_ch, _lk = _gen_multilevel_safe(_r, 2000, 200)
p["tests"].append([_ch, _lk])


def b_flatten(chains, links):
    child = {(r, q): c for r, q, c in links}
    out = []

    def dfs(c):
        for i, v in enumerate(chains[c]):
            out.append(v)
            if (c, i) in child:
                dfs(child[(c, i)])

    dfs(0)
    return out


def g_flatten(r):
    total = r.randint(1, 12)
    k = r.randint(1, total)
    ch, lk = _gen_multilevel_safe(r, total, k, vlo=-9, vhi=9)
    r.shuffle(lk)
    return [ch, lk]


def v_flatten(tests):
    for t in tests:
        chains, links = t["args"]
        assert 1 <= len(chains) <= 2000 and all(len(c) >= 1 for c in chains)
        assert sum(len(c) for c in chains) <= 5000
        assert len(links) == len(chains) - 1
        assert sorted(l[2] for l in links) == list(range(1, len(chains)))
        assert len({(l[0], l[1]) for l in links}) == len(links)
        for rr, pos, c in links:
            assert c > rr and 0 <= pos < len(chains[rr])
        assert len(t["expected"]) == sum(len(c) for c in chains)


CHECKS["flatten-multilevel-doubly-linked-list"] = (b_flatten, g_flatten, "exact")
VALIDATE["flatten-multilevel-doubly-linked-list"] = v_flatten

p = add(
    id="text-editor-cursor-simulation", title="Text Editor with a Cursor", diff="Medium", topic=TOPIC, tier="extra",
    fn="editorSums", params=[("ops", "int[][]")], ret="int[]", cmp="exact",
    desc="<p>A text editor holds a sequence of items (think of characters, each an integer) and a cursor that sits between two items, or at either end. The editor starts empty with the cursor at the beginning. Each operation is a pair <code>[type, x]</code>:</p><ul><li><code>[0, x]</code>: insert the item <code>x</code> exactly at the cursor; the cursor ends up right after it. Nothing is reported.</li><li><code>[1, k]</code>: delete up to <code>k</code> items immediately <em>before</em> the cursor (fewer if there are fewer). Report how many items were deleted.</li><li><code>[2, k]</code>: move the cursor left by up to <code>k</code> items (stopping at the beginning). Report the <em>sum of the up to 10 items immediately before the cursor</em> after the move (0 if there are none).</li><li><code>[3, k]</code>: move the cursor right by up to <code>k</code> items (stopping at the end). Report the same sum as for type 2.</li></ul><p>Return the reported numbers in the order of the operations. For example <code>ops = [[0,5],[0,6],[0,7],[2,1],[0,9],[1,2],[3,5]]</code> gives <code>[11, 2, 12]</code>. The items become <code>5 6 7</code> with the cursor at the end; moving left one place leaves <code>5 6 | 7</code> (sum before the cursor 5+6 = 11), item 9 is inserted giving <code>5 6 9 | 7</code>, deleting two items before the cursor removes 6 and 9 (report 2, leaving <code>5 | 7</code>) and moving right by 5 stops at the end (sum 5+7 = 12).</p>",
    constraints=["1 &le; ops.length &le; 5,000", "type is 0, 1, 2 or 3", "For an insert, -10<sup>8</sup> &le; x &le; 10<sup>8</sup>; for the other types, 0 &le; k &le; 10,000", "The answer contains one number per operation of type 1, 2 or 3"],
    hints=["Every operation happens at the cursor. Think of the text as two parts: everything left of the cursor and everything right of it.",
           "Keep the left part as a stack whose top is the item just before the cursor, and the right part as a stack whose top is the item just after the cursor. Insert and delete are pushes and pops on the left stack.",
           "Moving the cursor by <code>m = min(k, size)</code> places means popping <code>m</code> items from one stack and pushing them onto the other. After a move, the sum of the last 10 items of the left stack is the number to report. (A doubly linked list with a cursor node does the same job.)"],
    editorial=["A doubly linked list with a cursor pointer is the textbook model: insert and delete next to the cursor are O(1) and moving costs one step per item. Two stacks give the same behaviour with simpler code. <code>left</code> holds the items before the cursor (top = nearest to the cursor) and <code>right</code> the items after it (top = nearest). Insert is <code>left.append(x)</code>; delete pops up to <code>k</code> items from <code>left</code>; moving left transfers items from the top of <code>left</code> to <code>right</code>, moving right transfers the other way.",
               "A move transfers at most <code>min(k, size)</code> items, so the cost of an operation is proportional to the distance the cursor really moves. Reporting the sum of the last 10 items of <code>left</code> costs O(10). Overall O(total cursor movement + q) time, which is at most O(q &middot; n) and fast for these limits."],
    time="O(total cursor movement)", space="O(n)",
    solution='''def editorSums(ops):
    left = []
    right = []
    out = []
    for t, x in ops:
        if t == 0:
            left.append(x)
        elif t == 1:
            m = min(x, len(left))
            if m:
                del left[len(left) - m:]
            out.append(m)
        elif t == 2:
            m = min(x, len(left))
            if m:
                moved = left[len(left) - m:]
                del left[len(left) - m:]
                moved.reverse()
                right.extend(moved)
            out.append(sum(left[-10:]))
        else:
            m = min(x, len(right))
            if m:
                moved = right[len(right) - m:]
                del right[len(right) - m:]
                moved.reverse()
                left.extend(moved)
            out.append(sum(left[-10:]))
    return out
''',
    tests=[[[[0, 5], [0, 6], [0, 7], [2, 1], [0, 9], [1, 2], [3, 5]]], [[[1, 3]]], [[[2, 3], [3, 3]]], [[[0, 1], [1, 5], [1, 1]]],
           [[[0, 1], [0, 2], [0, 3], [0, 4], [0, 5], [0, 6], [0, 7], [0, 8], [0, 9], [0, 10], [0, 11], [0, 12], [2, 0], [2, 1], [2, 2]]],
           [[[0, 100000000], [0, -100000000], [0, 100000000], [2, 10000], [3, 10000], [3, 1]]],
           [[[0, 1], [0, 2], [2, 2], [0, 3], [3, 1], [0, 4], [2, 1], [1, 1], [3, 9]]],
           [[[0, 4], [2, 1], [3, 1], [2, 1], [3, 1], [1, 1], [2, 4]]]],
)


def _editor_ops(r, q, maxv, maxk):
    ops = []
    for _ in range(q):
        t = r.choice([0, 0, 0, 1, 2, 3, 3])
        ops.append([0, r.randint(-maxv, maxv)] if t == 0 else [t, r.randint(0, maxk)])
    return ops


_r = rnd(4409)
p["tests"].append([_editor_ops(_r, 3000, 10 ** 8, 12)])
p["tests"].append([[[0, _r.randint(-10 ** 8, 10 ** 8)] for _ in range(1500)] + _editor_ops(_r, 1500, 10 ** 8, 10000)])
p["tests"].append([_editor_ops(_r, 2500, 99, 40)])


def b_editor(ops):
    text, cur, out = [], 0, []
    for t, x in ops:
        if t == 0:
            text.insert(cur, x)
            cur += 1
        elif t == 1:
            m = min(x, cur)
            text = text[:cur - m] + text[cur:]
            cur -= m
            out.append(m)
        else:
            cur = max(0, cur - x) if t == 2 else min(len(text), cur + x)
            out.append(sum(text[max(0, cur - 10):cur]))
    return out


def g_editor(r):
    return [_editor_ops(r, r.randint(1, 20), 9, 6)]


def v_editor(tests):
    for t in tests:
        ops = t["args"][0]
        assert 1 <= len(ops) <= 5000
        for ty, x in ops:
            assert ty in (0, 1, 2, 3)
            assert (abs(x) <= 10 ** 8) if ty == 0 else (0 <= x <= 10000)
        assert len(t["expected"]) == sum(1 for o in ops if o[0] != 0)


CHECKS["text-editor-cursor-simulation"] = (b_editor, g_editor, "exact")
VALIDATE["text-editor-cursor-simulation"] = v_editor

# ================================================================ HARD

p = add(
    id="lfu-cache-simulation", title="LFU Cache Simulation", diff="Hard", topic=TOPIC,
    fn="lfuCacheGets", params=[("capacity", "int"), ("ops", "int[][]")], ret="int[]", cmp="exact",
    desc="<p>Simulate a cache that holds at most <code>capacity</code> key-value pairs and evicts the <em>least frequently used</em> pair when it is full. Every key in the cache has a <em>use count</em>: a newly inserted key starts at 1, and each later get hit or put on that key raises its count by 1. If several keys share the smallest use count, the one that was used <em>least recently</em> is evicted (a use is an insertion, a get hit or a put update). Each operation is a triple <code>[type, key, value]</code>:</p><ul><li><code>[0, key, 0]</code> (get): if the key is in the cache, report its value and count it as a use; otherwise report <code>-1</code>.</li><li><code>[1, key, value]</code> (put): if the key is in the cache, replace its value and count it as a use. Otherwise insert it with use count 1; if the cache is full, first evict one pair by the rule above. If <code>capacity = 0</code>, nothing is ever stored.</li></ul><p>A key that was evicted forgets its count: if it is inserted again it starts at 1. Return the reported values of all get operations. For example with <code>capacity = 2</code> and <code>ops = [[1,1,1],[1,2,2],[0,1,0],[1,3,3],[0,2,0],[0,3,0],[1,4,4],[0,1,0],[0,3,0],[0,4,0]]</code> the answer is <code>[1,-1,3,-1,3,4]</code>: key 2 (count 1) is evicted for key 3; later key 1 and key 3 both have count 2 and key 1 is older, so key 1 is evicted for key 4.</p><p>Aim for O(1) per operation.</p>",
    constraints=["0 &le; capacity &le; 1,000", "1 &le; ops.length &le; 3,000", "type is 0 (get) or 1 (put)", "0 &le; key &le; 10<sup>6</sup>, 0 &le; value &le; 10<sup>9</sup>", "For a get the value field is 0"],
    hints=["Compared with an LRU cache you additionally need to know each key's use count and to find the minimum count quickly.",
           "Group keys by use count. Inside a group keep the keys in order of last use, so that the oldest one can be removed in O(1): a doubly linked list per count. A hit moves a key from the list of count <code>f</code> to the end of the list of count <code>f + 1</code>.",
           "Track <code>minFreq</code>. After a hit, if the list of count <code>minFreq</code> became empty, <code>minFreq</code> becomes <code>minFreq + 1</code>. A new key always has count 1, so it resets <code>minFreq</code> to 1. The eviction victim is the oldest key of the list of count <code>minFreq</code>."],
    editorial=["Keep three maps: <code>val[key]</code>, <code>freq[key]</code> and <code>buckets[f]</code>, an insertion-ordered set (a hash map threaded with a doubly linked list, such as Python's OrderedDict) of the keys with use count <code>f</code>, oldest first. Also keep <code>minFreq</code>, the smallest count in the cache.",
               "touch(key): remove it from <code>buckets[f]</code>, drop the bucket if it became empty (and bump <code>minFreq</code> if <code>f == minFreq</code>), then append the key to <code>buckets[f + 1]</code>. Get hit and put-update call touch. Put of a new key: if the cache is full, pop the oldest key of <code>buckets[minFreq]</code> and forget it; then insert with count 1 and set <code>minFreq = 1</code>. All steps are O(1), so the run takes O(q). Edge cases: capacity 0 stores nothing, and a put that updates an existing key never evicts."],
    time="O(q)", space="O(capacity)",
    solution='''from collections import OrderedDict


def lfuCacheGets(capacity, ops):
    val = {}
    freq = {}
    buckets = {}
    min_freq = 0

    def touch(k):
        nonlocal min_freq
        f = freq[k]
        b = buckets[f]
        del b[k]
        if not b:
            del buckets[f]
            if min_freq == f:
                min_freq = f + 1
        freq[k] = f + 1
        buckets.setdefault(f + 1, OrderedDict())[k] = None

    out = []
    for t, k, v in ops:
        if t == 0:
            if k in val:
                touch(k)
                out.append(val[k])
            else:
                out.append(-1)
        elif capacity > 0:
            if k in val:
                val[k] = v
                touch(k)
            else:
                if len(val) == capacity:
                    old, _ = buckets[min_freq].popitem(last=False)
                    if not buckets[min_freq]:
                        del buckets[min_freq]
                    del val[old]
                    del freq[old]
                val[k] = v
                freq[k] = 1
                buckets.setdefault(1, OrderedDict())[k] = None
                min_freq = 1
    return out
''',
    tests=[[2, [[1, 1, 1], [1, 2, 2], [0, 1, 0], [1, 3, 3], [0, 2, 0], [0, 3, 0], [1, 4, 4], [0, 1, 0], [0, 3, 0], [0, 4, 0]]],
           [0, [[1, 1, 1], [0, 1, 0]]], [1, [[1, 1, 1], [1, 2, 2], [0, 1, 0], [0, 2, 0]]],
           [2, [[1, 1, 1], [1, 2, 2], [1, 1, 5], [1, 3, 3], [0, 1, 0], [0, 2, 0], [0, 3, 0]]],
           [3, [[1, 1, 1], [1, 2, 2], [1, 3, 3], [0, 1, 0], [0, 1, 0], [0, 2, 0], [1, 4, 4], [0, 3, 0], [0, 4, 0], [1, 5, 5], [0, 2, 0], [0, 4, 0], [0, 5, 0]]],
           [2, [[1, 1, 1], [0, 1, 0], [1, 2, 2], [0, 2, 0], [1, 3, 3], [0, 1, 0], [0, 2, 0], [0, 3, 0]]],
           [2, [[1, 5, 50], [1, 6, 60], [1, 7, 70], [1, 5, 55], [1, 8, 80], [0, 5, 0], [0, 6, 0], [0, 7, 0], [0, 8, 0]]],
           [3, [[1, 10, 1], [1, 20, 2], [1, 30, 3], [1, 40, 4], [0, 10, 0], [0, 20, 0], [0, 30, 0], [0, 40, 0]]],
           [2, [[0, 3, 0], [1, 3, 9], [0, 3, 0], [1, 4, 8], [1, 5, 7], [0, 3, 0], [0, 4, 0], [0, 5, 0]]]],
)
_r = rnd(4410)
p["tests"].append([20, _cache_ops(_r, 3000, list(range(0, 60)), 0.55, 999)])
p["tests"].append([1000, _cache_ops(_r, 3000, [_r.randint(0, 10 ** 6) for _ in range(1400)], 0.4, 99999)])
p["tests"].append([5, _cache_ops(_r, 3000, list(range(9)), 0.5, 99)])


def b_lfu(capacity, ops):
    store, clock, out = {}, 0, []  # key -> [value, count, last use]
    for t, k, v in ops:
        clock += 1
        if t == 0:
            if k in store:
                store[k][1] += 1
                store[k][2] = clock
                out.append(store[k][0])
            else:
                out.append(-1)
        elif capacity > 0:
            if k in store:
                store[k] = [v, store[k][1] + 1, clock]
            else:
                if len(store) == capacity:
                    victim = min(store, key=lambda q: (store[q][1], store[q][2]))
                    del store[victim]
                store[k] = [v, 1, clock]
    return out


def g_lfu(r):
    return [r.randint(0, 4), _cache_ops(r, r.randint(1, 24), list(range(6)), 0.5, 9)]


def v_lfu(tests):
    for t in tests:
        cap, ops = t["args"]
        assert 0 <= cap <= 1000 and 1 <= len(ops) <= 3000
        for ty, k, v in ops:
            assert ty in (0, 1) and 0 <= k <= 10 ** 6 and 0 <= v <= 10 ** 9
            assert ty == 1 or v == 0
        assert len(t["expected"]) == sum(1 for o in ops if o[0] == 0)


CHECKS["lfu-cache-simulation"] = (b_lfu, g_lfu, "exact")
VALIDATE["lfu-cache-simulation"] = v_lfu

p = add(
    id="all-one-counter-queries", title="Counter with Min and Max Queries", diff="Hard", topic=TOPIC, tier="extra",
    fn="counterQueries", params=[("ops", "int[][]")], ret="int[]", cmp="exact",
    desc="<p>Maintain a collection of counters, one per key. A key that is not in the collection has count 0. Each operation is a pair <code>[type, key]</code>:</p><ul><li><code>[0, key]</code>: increase the count of <code>key</code> by 1 (a new key starts at 1).</li><li><code>[1, key]</code>: decrease the count of <code>key</code> by 1; a key whose count drops to 0 leaves the collection. The key is guaranteed to be present.</li><li><code>[2, 0]</code>: report the largest count among all keys, or 0 if the collection is empty.</li><li><code>[3, 0]</code>: report the smallest count among the keys in the collection, or 0 if the collection is empty.</li></ul><p>Return the reported numbers in the order of the queries. For example <code>ops = [[0,5],[0,5],[0,8],[2,0],[3,0],[1,5],[1,5],[3,0],[1,8],[2,0]]</code> gives <code>[2,1,1,0]</code>.</p><p>Every operation should run in O(1) (amortised or worst case).</p>",
    constraints=["1 &le; ops.length &le; 5,000", "type is 0, 1, 2 or 3", "1 &le; key &le; 10<sup>9</sup> for types 0 and 1; the key field is 0 for types 2 and 3", "A decrease is only given for a key currently in the collection"],
    hints=["The hard part is the minimum: when the key holding the smallest count changes, how do you find the next smallest one without scanning?",
           "Counts change by exactly 1, so the set of distinct counts that are present is like a sorted chain. Keep one bucket per distinct count, holding the keys that currently have that count, and link the buckets in increasing count order.",
           "Increase: move the key from its bucket (count <code>c</code>) to the next bucket, creating a bucket for <code>c + 1</code> right after it if the next bucket has another count. Decrease: the same towards the previous bucket. Delete buckets that become empty. Max is the last bucket, min is the first."],
    editorial=["Use a doubly linked list of buckets sorted by count, with sentinel nodes at both ends. Every bucket stores its count and the set of keys with that count; a hash map sends each key to its bucket. Because a counter only ever changes by one, the new bucket of a key is always the neighbour of its current bucket (or a new bucket inserted right there), so the order of the list never needs sorting.",
               "Increase: look at the bucket after the key's bucket; if its count is <code>c + 1</code> use it, else create one. Add the key there, remove it from the old bucket, and unlink the old bucket when it becomes empty. A new key starts from the head sentinel (count 0). Decrease is symmetric using the previous bucket; if the count would reach 0 the key is simply removed. Max and min queries read the buckets next to the tail and head sentinels. Everything is O(1) per operation."],
    time="O(q)", space="O(n)",
    solution='''class Bucket:
    def __init__(self, cnt):
        self.cnt = cnt
        self.keys = set()
        self.prev = None
        self.next = None


def counterQueries(ops):
    head, tail = Bucket(0), Bucket(1 << 60)
    head.next = tail
    tail.prev = head
    where = {}

    def insert_after(b, cnt):
        nb = Bucket(cnt)
        nb.prev = b
        nb.next = b.next
        b.next.prev = nb
        b.next = nb
        return nb

    def drop_if_empty(b):
        if b is not head and not b.keys:
            b.prev.next = b.next
            b.next.prev = b.prev

    out = []
    for t, k in ops:
        if t == 0:
            cur = where.get(k, head)
            nxt = cur.next
            if nxt.cnt != cur.cnt + 1:
                nxt = insert_after(cur, cur.cnt + 1)
            nxt.keys.add(k)
            where[k] = nxt
            cur.keys.discard(k)
            drop_if_empty(cur)
        elif t == 1:
            cur = where[k]
            if cur.cnt == 1:
                del where[k]
            else:
                pb = cur.prev
                if pb.cnt != cur.cnt - 1:
                    pb = insert_after(pb, cur.cnt - 1)
                pb.keys.add(k)
                where[k] = pb
            cur.keys.discard(k)
            drop_if_empty(cur)
        elif t == 2:
            out.append(tail.prev.cnt)
        else:
            out.append(0 if head.next is tail else head.next.cnt)
    return out
''',
    tests=[[[[0, 5], [0, 5], [0, 8], [2, 0], [3, 0], [1, 5], [1, 5], [3, 0], [1, 8], [2, 0]]], [[[2, 0], [3, 0]]],
           [[[0, 1], [3, 0], [2, 0], [1, 1], [3, 0], [2, 0]]],
           [[[0, 1], [0, 1], [0, 1], [0, 2], [3, 0], [2, 0], [1, 2], [3, 0], [1, 1], [2, 0], [3, 0]]],
           [[[0, 3], [0, 4], [0, 4], [0, 5], [0, 5], [0, 5], [3, 0], [1, 3], [3, 0], [1, 4], [3, 0], [2, 0], [1, 5], [1, 5], [2, 0], [3, 0]]],
           [[[0, 10 ** 9], [0, 10 ** 9], [0, 1], [3, 0], [2, 0], [1, 10 ** 9], [3, 0], [2, 0]]],
           [[[0, 7], [0, 7], [0, 7], [0, 7], [1, 7], [1, 7], [2, 0], [3, 0], [0, 9], [3, 0], [2, 0]]],
           [[[0, 1], [0, 2], [0, 3], [3, 0], [1, 1], [3, 0], [1, 2], [3, 0], [1, 3], [3, 0], [2, 0]]]],
)


def _counter_ops(r, q, keys, query_prob=0.25):
    ops, cnt = [], {}
    for _ in range(q):
        x = r.random()
        if x < query_prob:
            ops.append([r.choice([2, 3]), 0])
        elif cnt and x < query_prob + 0.35:
            k = r.choice(sorted(cnt))
            ops.append([1, k])
            cnt[k] -= 1
            if cnt[k] == 0:
                del cnt[k]
        else:
            k = r.choice(keys)
            ops.append([0, k])
            cnt[k] = cnt.get(k, 0) + 1
    return ops


_r = rnd(4411)
p["tests"].append([_counter_ops(_r, 5000, [_r.randint(1, 10 ** 9) for _ in range(40)])])
p["tests"].append([_counter_ops(_r, 5000, list(range(1, 400)), 0.2)])
p["tests"].append([[[0, 1 + i % 3] for i in range(1800)] + [[2, 0], [3, 0]] + [[1, 1 + i % 3] for i in range(1799)] + [[3, 0], [2, 0], [1, 3], [3, 0]]])


def b_counter(ops):
    c, out = {}, []
    for t, k in ops:
        if t == 0:
            c[k] = c.get(k, 0) + 1
        elif t == 1:
            c[k] -= 1
            if c[k] == 0:
                del c[k]
        elif t == 2:
            out.append(max(c.values()) if c else 0)
        else:
            out.append(min(c.values()) if c else 0)
    return out


def g_counter(r):
    return [_counter_ops(r, r.randint(1, 25), [1, 2, 3, 4], 0.3)]


def v_counter(tests):
    for t in tests:
        ops = t["args"][0]
        assert 1 <= len(ops) <= 5000
        c = {}
        for ty, k in ops:
            assert ty in (0, 1, 2, 3)
            if ty in (0, 1):
                assert 1 <= k <= 10 ** 9
            else:
                assert k == 0
            if ty == 0:
                c[k] = c.get(k, 0) + 1
            elif ty == 1:
                assert c.get(k, 0) > 0, "decrease of absent key"
                c[k] -= 1
                if c[k] == 0:
                    del c[k]
        assert len(t["expected"]) == sum(1 for o in ops if o[0] >= 2)


CHECKS["all-one-counter-queries"] = (b_counter, g_counter, "exact")
VALIDATE["all-one-counter-queries"] = v_counter
