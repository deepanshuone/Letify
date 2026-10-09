"""Problems: linked lists (lists are passed as arrays of node values, head to tail). See data/lib.py for the registry."""
import heapq  # noqa: F401

from lib import add, rnd, CHECKS, VALIDATE, gen_arr  # noqa: F401

INT_MIN, INT_MAX = -(2 ** 31), 2 ** 31 - 1
TOPIC = "Linked List"

ENC = ("<p><strong>Encoding.</strong> A singly linked list is passed to your function as an array holding the node values "
       "from head to tail; an empty array is an empty list. You may build real nodes from it first, or work on the array directly. "
       "The result is also returned as an array of values from head to tail.</p>")


def _sorted_arr(r, n, lo=-50, hi=50):
    return sorted(r.randint(lo, hi) for _ in range(n))


def _rl(r, n, lo=-10 ** 9, hi=10 ** 9):
    return [r.randint(lo, hi) for _ in range(n)]


# ================================================================ EASY

p = add(
    id="reverse-linked-list", title="Reverse Linked List", diff="Easy", topic=TOPIC,
    fn="reverseList", params=[("nums", "int[]")], ret="int[]", cmp="exact",
    desc=ENC + "<p>Reverse the list and return the values of the reversed list from its new head to its new tail. For example, the list <code>1 -> 2 -> 3</code> becomes <code>3 -> 2 -> 1</code>, i.e. <code>[1,2,3]</code> maps to <code>[3,2,1]</code>.</p><p>As a linked-list exercise, aim to do it by redirecting each node's <code>next</code> pointer in one pass, with O(1) extra pointers.</p>",
    constraints=["0 &le; nums.length &le; 5,000", "-10<sup>9</sup> &le; nums[i] &le; 10<sup>9</sup>"],
    hints=["Reversing a list means every node must end up pointing at the node that used to be before it.",
           "Walk the list while remembering the previous node. Before you overwrite <code>cur.next</code>, save the old next node somewhere.",
           "Keep three pointers: <code>prev</code> (starts null), <code>cur</code> (starts at head) and a temporary for <code>cur.next</code>. Each step: save next, point <code>cur.next</code> to <code>prev</code>, advance both. The answer starts at <code>prev</code> when <code>cur</code> becomes null."],
    editorial=["Traverse once. At each node, remember its successor, flip its <code>next</code> pointer to the previous node, and step forward. When the walk falls off the end, <code>prev</code> is the new head. This is O(n) time and uses only three pointers.",
               "A recursive version reverses the rest of the list and then makes the following node point back at the current one, but it needs O(n) stack space. Pushing all values on a stack also works but wastes memory compared to relinking in place."],
    time="O(n)", space="O(1)",
    solution='''class ListNode:
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


def reverseList(nums):
    head = build(nums)
    prev = None
    cur = head
    while cur:
        nxt = cur.next
        cur.next = prev
        prev = cur
        cur = nxt
    return dump(prev)
''',
    tests=[[[1, 2, 3, 4, 5]], [[1, 2]], [[]], [[7]], [[5, 5, 5]], [[-3, 0, 3]], [[INT_MIN, INT_MAX]],
           [[9, 8, 7, 6, 5, 4, 3, 2, 1, 0]]],
)
_r = rnd(2101)
p["tests"].append([_rl(_r, 5000)])
p["tests"].append([list(range(4000))])
p["tests"].append([[_r.randint(0, 2) for _ in range(3001)]])


def b_rev(nums):
    return [nums[len(nums) - 1 - i] for i in range(len(nums))]


def v_rev(tests):
    for t in tests:
        assert len(t["args"][0]) <= 5000
        assert sorted(t["expected"]) == sorted(t["args"][0])


CHECKS["reverse-linked-list"] = (b_rev, lambda r: [gen_arr(r, -9, 9, 0, 10)], "exact")
VALIDATE["reverse-linked-list"] = v_rev

p = add(
    id="merge-two-sorted-linked-lists", title="Merge Two Sorted Linked Lists", diff="Easy", topic=TOPIC,
    fn="mergeTwoLists", params=[("a", "int[]"), ("b", "int[]")], ret="int[]", cmp="exact",
    desc=ENC + "<p>Two sorted singly linked lists are given as the arrays <code>a</code> and <code>b</code>, each in non-decreasing order from head to tail. Splice their nodes together into one sorted list and return its values from head to tail.</p><p>The intended solution reuses the existing nodes and relinks them rather than allocating a new node per value; here you only need to return the final values.</p>",
    constraints=["0 &le; a.length, b.length &le; 5,000", "-10<sup>9</sup> &le; a[i], b[i] &le; 10<sup>9</sup>", "Both arrays are sorted in non-decreasing order"],
    hints=["At every step, the next node of the merged list is the smaller of the two current heads.",
           "A dummy head node removes the special case of 'what is the first node of the result'. Keep a <code>tail</code> pointer to where you append next.",
           "Loop while both lists have nodes: attach the smaller head to <code>tail</code>, advance that list and <code>tail</code>. When one list runs out, attach the rest of the other in one step."],
    editorial=["Use a dummy node and a <code>tail</code> pointer. Compare the heads of the two lists, link the smaller one after <code>tail</code>, and advance in that list. When one list is exhausted, the remainder of the other is already sorted, so link it directly. Taking from <code>a</code> on ties keeps the merge stable.",
               "Time is O(n + m) because every node is visited once, and extra space is O(1) when nodes are relinked in place. Concatenating and sorting works but costs O((n + m) log(n + m)) and ignores the sortedness."],
    time="O(n + m)", space="O(1)",
    solution='''class ListNode:
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


def mergeTwoLists(a, b):
    l1 = build(a)
    l2 = build(b)
    dummy = ListNode()
    tail = dummy
    while l1 and l2:
        if l2.val < l1.val:
            tail.next = l2
            l2 = l2.next
        else:
            tail.next = l1
            l1 = l1.next
        tail = tail.next
    tail.next = l1 if l1 else l2
    return dump(dummy.next)
''',
    tests=[[[1, 2, 4], [1, 3, 4]], [[], []], [[], [0]], [[5], []], [[1, 2, 3], [4, 5, 6]], [[4, 5, 6], [1, 2, 3]],
           [[1, 1, 1], [1, 1]], [[-5, 0, 5], [-6, -1, 1, 6]], [[INT_MIN, 0], [0, INT_MAX]], [[2], [1]]],
)
_r = rnd(2102)
p["tests"].append([_sorted_arr(_r, 5000, -10 ** 9, 10 ** 9), _sorted_arr(_r, 5000, -10 ** 9, 10 ** 9)])
p["tests"].append([_sorted_arr(_r, 5000, -5, 5), _sorted_arr(_r, 3000, -5, 5)])
p["tests"].append([list(range(0, 5000)), list(range(5000, 10000))])


def b_merge2(a, b):
    return sorted(a + b)


def g_merge2(r):
    return [_sorted_arr(r, r.randint(0, 8), -9, 9), _sorted_arr(r, r.randint(0, 8), -9, 9)]


def v_merge2(tests):
    for t in tests:
        a, b = t["args"]
        assert len(a) <= 5000 and len(b) <= 5000
        assert a == sorted(a) and b == sorted(b)


CHECKS["merge-two-sorted-linked-lists"] = (b_merge2, g_merge2, "exact")
VALIDATE["merge-two-sorted-linked-lists"] = v_merge2

p = add(
    id="palindrome-linked-list", title="Palindrome Linked List", diff="Easy", topic=TOPIC,
    fn="isPalindromeList", params=[("nums", "int[]")], ret="bool", cmp="exact",
    desc=ENC + "<p>Return <code>true</code> if the list reads the same from head to tail as from tail to head, and <code>false</code> otherwise.</p><p>A singly linked list cannot be walked backwards, so the interesting question is how to compare the two directions using only O(1) extra pointers (you are allowed to rearrange nodes).</p>",
    constraints=["1 &le; nums.length &le; 10,000", "-10<sup>9</sup> &le; nums[i] &le; 10<sup>9</sup>"],
    hints=["Copying the values into an array and comparing it with its reverse works, but costs O(n) memory.",
           "Find the middle of the list with a slow and a fast pointer (fast moves two steps per slow step).",
           "Reverse the second half in place, then walk the first half and the reversed second half together, comparing values. For odd lengths the middle node is simply skipped."],
    editorial=["Locate the end of the first half with slow and fast pointers. Reverse everything after that point. Now two pointers, one from the head and one from the head of the reversed half, move in lockstep and compare values; any mismatch means the list is not a palindrome. For odd lengths the first half contains one extra middle node, which the lockstep walk never reaches because the second half is shorter.",
               "Time is O(n) and extra space is O(1). If you must not modify the list, reverse the second half back after comparing, or use the copy-to-array approach at O(n) space."],
    time="O(n)", space="O(1)",
    solution='''class ListNode:
    def __init__(self, val=0, nxt=None):
        self.val = val
        self.next = nxt


def build(vals):
    head = None
    for v in reversed(vals):
        head = ListNode(v, head)
    return head


def isPalindromeList(nums):
    head = build(nums)
    slow = fast = head
    while fast.next and fast.next.next:
        slow = slow.next
        fast = fast.next.next
    # reverse everything after slow
    prev = None
    cur = slow.next
    while cur:
        nxt = cur.next
        cur.next = prev
        prev = cur
        cur = nxt
    a, b = head, prev
    while b:
        if a.val != b.val:
            return False
        a = a.next
        b = b.next
    return True
''',
    tests=[[[1, 2, 2, 1]], [[1, 2]], [[1]], [[1, 2, 1]], [[1, 2, 3, 2, 1]], [[1, 2, 3, 3, 1]], [[5, 5]], [[0, 0, 0, 0, 0]],
           [[-1, 2, 2, -1]], [[1, 2, 3, 4]], [[INT_MIN, INT_MAX, INT_MIN]], [[1, 0, 0, 0, 1]]],
)
_r = rnd(2103)
_h = _rl(_r, 5000)
p["tests"].append([_h + _h[::-1]])
p["tests"].append([_h[:4999] + [0] + _h[:4999][::-1]])
_h2 = _h + _h[::-1]
_h2[3000] += 1
p["tests"].append([_h2])
p["tests"].append([[1] * 4999 + [2] + [1] * 5000])
p["tests"].append([_rl(_r, 10000)])


def b_pal(nums):
    i, j = 0, len(nums) - 1
    while i < j:
        if nums[i] != nums[j]:
            return False
        i += 1
        j -= 1
    return True


def g_pal(r):
    h = [r.randint(0, 2) for _ in range(r.randint(1, 6))]
    a = h + ([r.randint(0, 2)] if r.random() < 0.5 else []) + h[::-1]
    if r.random() < 0.4:
        a[r.randrange(len(a))] = r.randint(0, 2)
    return [a]


def v_pal(tests):
    for t in tests:
        assert 1 <= len(t["args"][0]) <= 10000
    assert any(t["expected"] for t in tests) and any(not t["expected"] for t in tests)


CHECKS["palindrome-linked-list"] = (b_pal, g_pal, "exact")
VALIDATE["palindrome-linked-list"] = v_pal

# ================================================================ MEDIUM

p = add(
    id="remove-nth-node-from-end-of-list", title="Remove Nth Node From End of List", diff="Medium", topic=TOPIC,
    fn="removeNthFromEnd", params=[("nums", "int[]"), ("n", "int")], ret="int[]", cmp="exact",
    desc=ENC + "<p>Delete the <code>n</code>-th node counting from the <em>tail</em> (so <code>n = 1</code> is the last node) and return the values of the remaining list from head to tail.</p><p>With a real linked list you can do this in a single pass, without first measuring the length.</p>",
    constraints=["1 &le; nums.length &le; 5,000", "1 &le; n &le; nums.length", "-10<sup>9</sup> &le; nums[i] &le; 10<sup>9</sup>"],
    hints=["Deleting a node needs a pointer to the node <em>before</em> it. The head may itself be the node to delete.",
           "Two passes work: count the length L, then walk to position L - n. Can you find that position in one pass?",
           "Use a dummy node before the head and two pointers. Advance <code>fast</code> by <code>n</code> steps, then move both until <code>fast.next</code> is null; <code>slow</code> now sits right before the node to delete."],
    editorial=["Put a dummy node in front of the list so removing the head is not a special case. Move <code>fast</code> exactly <code>n</code> nodes ahead of <code>slow</code>. Then advance both together until <code>fast</code> is the last node. The gap of <code>n</code> guarantees <code>slow.next</code> is the n-th node from the end, so set <code>slow.next = slow.next.next</code>.",
               "This is one pass, O(L) time and O(1) space. The two-pass method (count, then walk) has the same complexity but visits nodes twice."],
    time="O(n)", space="O(1)",
    solution='''class ListNode:
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


def removeNthFromEnd(nums, n):
    dummy = ListNode(0, build(nums))
    fast = slow = dummy
    for _ in range(n):
        fast = fast.next
    while fast.next:
        fast = fast.next
        slow = slow.next
    slow.next = slow.next.next
    return dump(dummy.next)
''',
    tests=[[[1, 2, 3, 4, 5], 2], [[1], 1], [[1, 2], 1], [[1, 2], 2], [[1, 2, 3], 3], [[1, 2, 3], 1], [[4, 4, 4, 4], 2],
           [[10, 20, 30, 40, 50, 60], 4], [[INT_MIN, 0, INT_MAX], 2]],
)
_r = rnd(2104)
_a = _rl(_r, 5000)
p["tests"].append([_a, 1])
p["tests"].append([_a, 5000])
p["tests"].append([_a, 2500])
p["tests"].append([_rl(_r, 4999), 4998])


def b_rmnth(nums, n):
    idx = len(nums) - n
    return [v for i, v in enumerate(nums) if i != idx]


def g_rmnth(r):
    a = gen_arr(r, -9, 9, 1, 9)
    return [a, r.randint(1, len(a))]


def v_rmnth(tests):
    for t in tests:
        nums, n = t["args"]
        assert 1 <= len(nums) <= 5000 and 1 <= n <= len(nums)


CHECKS["remove-nth-node-from-end-of-list"] = (b_rmnth, g_rmnth, "exact")
VALIDATE["remove-nth-node-from-end-of-list"] = v_rmnth

p = add(
    id="linked-list-cycle-entry", title="Linked List Cycle Entry", diff="Medium", topic=TOPIC,
    fn="cycleEntry", params=[("succ", "int[]")], ret="int", cmp="exact",
    desc="<p><strong>Encoding.</strong> A singly linked list with <code>n</code> nodes is given as a successor array. The nodes are numbered <code>0..n-1</code> and node <code>0</code> is the head. <code>succ[i]</code> is the number of the node that follows node <code>i</code>, or <code>-1</code> if node <code>i</code> has no next node.</p><p>Starting at the head and repeatedly following <code>succ</code>, the walk either ends at a node with <code>succ = -1</code> or runs into a node it has already visited, which means the list has a cycle. Return the number of the node where the cycle begins (the first node of the walk that is reached a second time), or <code>-1</code> if the list has no cycle.</p><p>For <code>succ = [1,2,3,1]</code> the walk is <code>0, 1, 2, 3, 1, ...</code>, so the answer is <code>1</code>. Try to solve it with O(1) extra memory instead of a visited set.</p>",
    constraints=["1 &le; succ.length &le; 10,000", "-1 &le; succ[i] &lt; succ.length", "Every node can be reached by following succ from node 0"],
    hints=["Remembering every visited node in a set finds the answer immediately, but costs O(n) memory.",
           "Use two pointers moving at different speeds. If there is a cycle they must eventually meet inside it; if there is none, the fast one falls off the end.",
           "After they meet, put one pointer back at the head. Moving both one step at a time, they meet again exactly at the cycle's entry node."],
    editorial=["Floyd's tortoise and hare: move <code>slow</code> by one node and <code>fast</code> by two. If <code>fast</code> reaches the end (<code>-1</code>), there is no cycle. Otherwise they meet inside the cycle.",
               "Let the tail before the cycle have length <code>a</code>, and let the meeting point be <code>b</code> steps past the cycle entry, with cycle length <code>c</code>. At the meeting, slow has walked <code>a + b</code> and fast has walked twice that, so <code>a + b</code> is a multiple of <code>c</code>. Hence walking <code>a</code> more steps from the meeting point lands exactly on the entry. Restart one pointer at the head and advance both one step at a time: they meet at the entry after <code>a</code> steps.",
               "This is O(n) time and O(1) space. The visited-set approach is simpler but needs O(n) space."],
    time="O(n)", space="O(1)",
    solution='''def cycleEntry(succ):
    # nodes are indices into succ; -1 plays the role of null
    slow = fast = 0
    while True:
        if fast == -1 or succ[fast] == -1:
            return -1
        slow = succ[slow]
        fast = succ[succ[fast]]
        if slow == fast:
            break
    slow = 0
    while slow != fast:
        slow = succ[slow]
        fast = succ[fast]
    return slow
''',
    tests=[[[-1]], [[0]], [[1, -1]], [[1, 0]], [[1, 1]], [[1, 2, -1]], [[1, 2, 0]], [[1, 2, 3, 1]], [[1, 2, 3, 2]],
           [[1, 2, 2]], [[2, 3, 1, 2]], [[1, 2, 3, 4, 5, -1]], [[1, 2, 3, 4, 5, 3]]],
)


def _mk_succ(r, n, s):
    """chain over a random permutation of node ids with head 0; tail points back to chain position s (or -1)."""
    order = [0] + r.sample(range(1, n), n - 1) if n > 1 else [0]
    succ = [-1] * n
    for i in range(n - 1):
        succ[order[i]] = order[i + 1]
    if s is not None:
        succ[order[-1]] = order[s]
    return succ


_r = rnd(2105)
p["tests"].append([_mk_succ(_r, 10000, None)])
p["tests"].append([_mk_succ(_r, 10000, 0)])
p["tests"].append([_mk_succ(_r, 10000, 9999)])
p["tests"].append([_mk_succ(_r, 10000, 5000)])
p["tests"].append([_mk_succ(_r, 10000, 9990)])
p["tests"].append([_mk_succ(_r, 9999, 17)])
p["tests"].append([_mk_succ(_r, 7, 3)])


def b_cycle(succ):
    seen = set()
    cur = 0
    while cur != -1:
        if cur in seen:
            return cur
        seen.add(cur)
        cur = succ[cur]
    return -1


def g_cycle(r):
    n = r.randint(1, 10)
    s = r.choice([None] + list(range(n)))
    return [_mk_succ(r, n, s)]


def v_cycle(tests):
    for t in tests:
        succ = t["args"][0]
        n = len(succ)
        assert 1 <= n <= 10000
        assert all(-1 <= x < n for x in succ)
        seen, cur = set(), 0
        while cur != -1 and cur not in seen:
            seen.add(cur)
            cur = succ[cur]
        assert len(seen) == n, "unreachable node"
    assert any(t["expected"] == -1 for t in tests) and any(t["expected"] > 0 for t in tests)


CHECKS["linked-list-cycle-entry"] = (b_cycle, g_cycle, "exact")
VALIDATE["linked-list-cycle-entry"] = v_cycle

p = add(
    id="add-two-numbers-as-linked-lists", title="Add Two Numbers as Linked Lists", diff="Medium", topic=TOPIC,
    fn="addTwoNumbers", params=[("a", "int[]"), ("b", "int[]")], ret="int[]", cmp="exact",
    desc=ENC + "<p>Each list represents a non-negative integer, one decimal digit per node, with the <em>least significant digit at the head</em>. For example <code>[2,4,3]</code> is the number 342. Add the two numbers and return the sum in the same format (least significant digit first).</p><p>The lists can be far longer than any machine integer, so do not convert them to a native number: add digit by digit with a carry, as on paper.</p>",
    constraints=["1 &le; a.length, b.length &le; 5,000", "0 &le; a[i], b[i] &le; 9", "No leading zeros: the last element is non-zero unless the number is exactly 0 (the array <code>[0]</code>)"],
    hints=["Start from the heads, which are the units digits, and add them the way you would on paper.",
           "Carry a single value from one position to the next. The lists can have different lengths, so treat a missing digit as 0.",
           "Loop while either list has a node or the carry is non-zero. Append <code>(x + y + carry) % 10</code> and set <code>carry = (x + y + carry) / 10</code>. A final carry creates one more digit."],
    editorial=["Because the digits are stored least significant first, the heads are the units digits and a single forward pass is enough. Keep a running carry. At each position add the digit from each list (0 if the list is shorter) and the carry, output the last digit of the total and carry the rest. Continue until both lists are exhausted and the carry is zero; a leftover carry becomes a new final digit (for example 99 + 1 = 100).",
               "Time is O(max(n, m)) and, apart from the output list, extra space is O(1). Converting to big integers hides the point of the exercise and is not available in many languages."],
    time="O(max(n, m))", space="O(1)",
    solution='''class ListNode:
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


def addTwoNumbers(a, b):
    l1 = build(a)
    l2 = build(b)
    dummy = ListNode()
    tail = dummy
    carry = 0
    while l1 or l2 or carry:
        total = carry
        if l1:
            total += l1.val
            l1 = l1.next
        if l2:
            total += l2.val
            l2 = l2.next
        tail.next = ListNode(total % 10)
        tail = tail.next
        carry = total // 10
    return dump(dummy.next)
''',
    tests=[[[2, 4, 3], [5, 6, 4]], [[0], [0]], [[9, 9, 9, 9, 9, 9, 9], [9, 9, 9, 9]], [[9, 9], [1]], [[1], [9, 9, 9]],
           [[5], [5]], [[0], [7, 3]], [[1, 0, 0, 1], [9, 9, 9]], [[8, 1], [2, 9]], [[1], [1]]],
)


def _digits(r, n):
    if n == 1:
        return [r.randint(0, 9)]
    return [r.randint(0, 9) for _ in range(n - 1)] + [r.randint(1, 9)]


_r = rnd(2106)
p["tests"].append([_digits(_r, 5000), _digits(_r, 5000)])
p["tests"].append([[9] * 5000, [1]])
p["tests"].append([[9] * 5000, [9] * 5000])
p["tests"].append([_digits(_r, 5000), _digits(_r, 2)])
p["tests"].append([[0] * 4999 + [1], [0] * 4999 + [1]])


def _to_int(d):
    v = 0
    for x in reversed(d):
        v = v * 10 + x
    return v


def b_add(a, b):
    s = _to_int(a) + _to_int(b)
    if s == 0:
        return [0]
    out = []
    while s:
        out.append(s % 10)
        s //= 10
    return out


def g_add(r):
    return [_digits(r, r.randint(1, 7)), _digits(r, r.randint(1, 7))]


def v_add(tests):
    for t in tests:
        for d in t["args"]:
            assert 1 <= len(d) <= 5000 and all(0 <= x <= 9 for x in d)
            assert d[-1] != 0 or len(d) == 1, "leading zero"
        e = t["expected"]
        assert e[-1] != 0 or len(e) == 1


CHECKS["add-two-numbers-as-linked-lists"] = (b_add, g_add, "exact")
VALIDATE["add-two-numbers-as-linked-lists"] = v_add

p = add(
    id="reorder-linked-list", title="Reorder Linked List", diff="Medium", topic=TOPIC,
    fn="reorderList", params=[("nums", "int[]")], ret="int[]", cmp="exact",
    desc=ENC + "<p>Reorder the nodes of a list <code>L<sub>0</sub> -> L<sub>1</sub> -> ... -> L<sub>n-1</sub></code> so that it reads <code>L<sub>0</sub> -> L<sub>n-1</sub> -> L<sub>1</sub> -> L<sub>n-2</sub> -> L<sub>2</sub> -> ...</code>, alternating between the front and the back. Return the values of the reordered list from head to tail.</p><p>For instance, <code>[1,2,3,4,5]</code> becomes <code>[1,5,2,4,3]</code>. In a real linked list you may only relink nodes, not change their values, and the tail cannot be reached backwards.</p>",
    constraints=["1 &le; nums.length &le; 10,000", "-10<sup>9</sup> &le; nums[i] &le; 10<sup>9</sup>"],
    hints=["The new list takes nodes alternately from the front and from the back. Walking backwards is the hard part in a singly linked list.",
           "Split the list at its middle, and reverse the second half so the former tail comes first.",
           "Find the middle with slow and fast pointers, cut the list there, reverse the second half, and then merge the two halves by taking one node from each in turn, starting with the first half."],
    editorial=["The task decomposes into three classic steps. First, find the middle with slow and fast pointers and cut the list in two (the first half gets the extra node when the length is odd). Second, reverse the second half in place. Third, interleave: link a node of the first half, then a node of the reversed second half, and so on.",
               "Each step is O(n) with O(1) extra space. Storing the nodes in an array and using two indices is easier but needs O(n) memory."],
    time="O(n)", space="O(1)",
    solution='''class ListNode:
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


def reorderList(nums):
    head = build(nums)
    if head is None or head.next is None:
        return dump(head)
    slow = fast = head
    while fast.next and fast.next.next:
        slow = slow.next
        fast = fast.next.next
    second = slow.next
    slow.next = None
    prev = None
    while second:
        nxt = second.next
        second.next = prev
        prev = second
        second = nxt
    first, second = head, prev
    while second:
        a, b = first.next, second.next
        first.next = second
        second.next = a
        first, second = a, b
    return dump(head)
''',
    tests=[[[1, 2, 3, 4]], [[1, 2, 3, 4, 5]], [[1]], [[1, 2]], [[1, 2, 3]], [[5, 5, 5, 5]], [[-1, 0, 1, 2, 3, 4]],
           [[INT_MIN, INT_MAX, 0]], [[10, 20, 30, 40, 50, 60, 70]]],
)
_r = rnd(2107)
p["tests"].append([_rl(_r, 10000)])
p["tests"].append([_rl(_r, 9999)])
p["tests"].append([list(range(1, 8001))])


def b_reorder(nums):
    out = []
    i, j = 0, len(nums) - 1
    take_front = True
    while i <= j:
        if take_front:
            out.append(nums[i])
            i += 1
        else:
            out.append(nums[j])
            j -= 1
        take_front = not take_front
    return out


def v_reorder(tests):
    for t in tests:
        assert 1 <= len(t["args"][0]) <= 10000


CHECKS["reorder-linked-list"] = (b_reorder, lambda r: [gen_arr(r, -9, 9, 1, 11)], "exact")
VALIDATE["reorder-linked-list"] = v_reorder

p = add(
    id="partition-linked-list-around-value", title="Partition Linked List Around Value", diff="Medium", topic=TOPIC,
    fn="partitionList", params=[("nums", "int[]"), ("x", "int")], ret="int[]", cmp="exact",
    desc=ENC + "<p>Rearrange the list so that every node with a value <em>less than</em> <code>x</code> comes before every node with a value <em>greater than or equal to</em> <code>x</code>. The relative order of the nodes inside each of the two groups must stay exactly as in the original list (the partition is stable). Return the values of the rearranged list from head to tail.</p><p>For example, <code>nums = [1,4,3,2,5,2]</code> with <code>x = 3</code> gives <code>[1,2,2,4,3,5]</code>.</p>",
    constraints=["0 &le; nums.length &le; 10,000", "-10<sup>9</sup> &le; nums[i], x &le; 10<sup>9</sup>"],
    hints=["Because the order inside each group must be preserved, a swap-based partition like quicksort's will not work.",
           "Think of building two separate lists while walking once: one for nodes smaller than <code>x</code>, one for the rest.",
           "Use two dummy heads, each with its own tail pointer. Append every node to the matching list, then link the end of the 'small' list to the head of the 'large' list and terminate the 'large' list with null (otherwise a cycle can appear)."],
    editorial=["Traverse the list once, detaching each node and appending it to one of two lists: <code>small</code> for values below <code>x</code> and <code>big</code> for the rest. Since you append in traversal order, both keep their original relative order. At the end connect <code>small</code>'s tail to <code>big</code>'s first node, and set <code>big</code>'s tail <code>next</code> to null; forgetting that last step can leave a pointer to an earlier node and create a cycle.",
               "This is O(n) time and O(1) extra space because the nodes are just relinked."],
    time="O(n)", space="O(1)",
    solution='''class ListNode:
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


def partitionList(nums, x):
    head = build(nums)
    small_head = ListNode()
    big_head = ListNode()
    small, big = small_head, big_head
    while head:
        if head.val < x:
            small.next = head
            small = head
        else:
            big.next = head
            big = head
        head = head.next
    big.next = None
    small.next = big_head.next
    return dump(small_head.next)
''',
    tests=[[[1, 4, 3, 2, 5, 2], 3], [[2, 1], 2], [[], 0], [[5], 5], [[5], 6], [[1, 2, 3], 0], [[1, 2, 3], 10],
           [[3, 3, 3], 3], [[9, 8, 7, 1, 2, 3], 5], [[INT_MAX, INT_MIN, 0], 0], [[4, 1, 4, 1, 4, 1], 4]],
)
_r = rnd(2108)
p["tests"].append([_rl(_r, 10000, -1000, 1000), 0])
p["tests"].append([_rl(_r, 10000, -10 ** 9, 10 ** 9), 12345])
p["tests"].append([[_r.randint(0, 3) for _ in range(9000)], 2])


def b_part(nums, x):
    out = []
    for v in nums:
        if v < x:
            out.append(v)
    for v in nums:
        if not v < x:
            out.append(v)
    return out


def g_part(r):
    return [gen_arr(r, -5, 5, 0, 10), r.randint(-6, 6)]


def v_part(tests):
    for t in tests:
        nums, x = t["args"]
        assert len(nums) <= 10000 and -10 ** 9 <= x <= 10 ** 9


CHECKS["partition-linked-list-around-value"] = (b_part, g_part, "exact")
VALIDATE["partition-linked-list-around-value"] = v_part

# ================================================================ HARD

p = add(
    id="reverse-nodes-in-k-group", title="Reverse Nodes in k-Group", diff="Hard", topic=TOPIC,
    fn="reverseKGroup", params=[("nums", "int[]"), ("k", "int")], ret="int[]", cmp="exact",
    desc=ENC + "<p>Cut the list into consecutive blocks of exactly <code>k</code> nodes, starting from the head. Reverse the order of the nodes inside every complete block. If the last block has fewer than <code>k</code> nodes, leave it as it is. Return the values of the resulting list from head to tail.</p><p>For example, <code>nums = [1,2,3,4,5]</code> with <code>k = 2</code> gives <code>[2,1,4,3,5]</code>, and with <code>k = 3</code> gives <code>[3,2,1,4,5]</code>.</p><p>In a real list you can only relink nodes, so aim for O(1) extra space.</p>",
    constraints=["1 &le; nums.length &le; 10,000", "1 &le; k &le; nums.length", "-10<sup>9</sup> &le; nums[i] &le; 10<sup>9</sup>"],
    hints=["Reversing a whole list is a known routine. Apply it to each block of k nodes, but only when the block is complete.",
           "Before reversing a block, walk <code>k</code> nodes ahead to check that the block really has k nodes. Remember the node just before the block and the node just after it.",
           "Use a dummy head. For each block: find its k-th node, reverse the k nodes while pointing the first one at the node after the block, then reconnect the previous block's tail to the new block head. The old first node of the block is the next 'previous' node."],
    editorial=["Keep a pointer <code>groupPrev</code> to the node just before the current block (initially a dummy node in front of the head). Find the block's k-th node; if fewer than k nodes remain, stop. Let <code>groupNext</code> be the node after the k-th node. Reverse the k nodes with the usual three-pointer loop, but initialise <code>prev</code> to <code>groupNext</code> so that the old first node of the block automatically ends up pointing at the rest of the list.",
               "Then set <code>groupPrev.next</code> to the k-th node (the new block head) and move <code>groupPrev</code> to the old first node of the block, which is now the block's tail. Every node is touched a constant number of times, so the algorithm is O(n) time and O(1) space. A recursive version is shorter but uses O(n/k) stack."],
    time="O(n)", space="O(1)",
    solution='''class ListNode:
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


def reverseKGroup(nums, k):
    dummy = ListNode(0, build(nums))
    group_prev = dummy
    while True:
        kth = group_prev
        for _ in range(k):
            kth = kth.next
            if kth is None:
                return dump(dummy.next)
        group_next = kth.next
        prev, cur = group_next, group_prev.next
        while cur is not group_next:
            nxt = cur.next
            cur.next = prev
            prev = cur
            cur = nxt
        old_first = group_prev.next
        group_prev.next = kth
        group_prev = old_first
''',
    tests=[[[1, 2, 3, 4, 5], 2], [[1, 2, 3, 4, 5], 3], [[1], 1], [[1, 2], 1], [[1, 2], 2], [[1, 2, 3, 4, 5, 6], 3],
           [[1, 2, 3, 4, 5, 6], 6], [[1, 2, 3, 4, 5, 6, 7], 4], [[5, 5, 6, 6, 7], 2], [[INT_MIN, 0, INT_MAX], 3],
           [[9, 8, 7, 6, 5, 4, 3, 2, 1], 4]],
)
_r = rnd(2109)
_a = _rl(_r, 10000)
p["tests"].append([_a, 1])
p["tests"].append([_a, 2])
p["tests"].append([_a, 7])
p["tests"].append([_a, 3333])
p["tests"].append([_a, 10000])
p["tests"].append([_a[:9999], 5000])


def b_kgroup(nums, k):
    out = []
    n = len(nums)
    i = 0
    while i < n:
        if i + k <= n:
            for j in range(i + k - 1, i - 1, -1):
                out.append(nums[j])
        else:
            for j in range(i, n):
                out.append(nums[j])
        i += k
    return out


def g_kgroup(r):
    a = gen_arr(r, -9, 9, 1, 12)
    return [a, r.randint(1, len(a))]


def v_kgroup(tests):
    for t in tests:
        nums, k = t["args"]
        assert 1 <= len(nums) <= 10000 and 1 <= k <= len(nums)


CHECKS["reverse-nodes-in-k-group"] = (b_kgroup, g_kgroup, "exact")
VALIDATE["reverse-nodes-in-k-group"] = v_kgroup

p = add(
    id="merge-k-sorted-linked-lists", title="Merge k Sorted Linked Lists", diff="Hard", topic=TOPIC,
    fn="mergeKLists", params=[("lists", "int[][]")], ret="int[]", cmp="exact",
    desc="<p><strong>Encoding.</strong> You are given <code>k</code> sorted singly linked lists as a 2D array: <code>lists[i]</code> holds the node values of the i-th list from head to tail, in non-decreasing order. A row may be empty, which is an empty list.</p><p>Merge all of the lists into one sorted list and return its values from head to tail as an array.</p><p>For example, <code>[[1,4,5],[1,3,4],[2,6]]</code> gives <code>[1,1,2,3,4,4,5,6]</code>. With real nodes the goal is to relink them, in about O(N log k) time for N nodes in total.</p>",
    constraints=["0 &le; lists.length &le; 200", "0 &le; lists[i].length and the total number of values is at most 10,000", "-10<sup>9</sup> &le; lists[i][j] &le; 10<sup>9</sup>", "Every lists[i] is sorted in non-decreasing order"],
    hints=["Merging two sorted lists is easy. What if you merge the k lists one after another? How bad is that when one list is huge?",
           "At any time the next output value is the smallest among the k current heads. A min-heap can give you that in O(log k).",
           "Alternatively, merge the lists in pairs, halving the number of lists each round (divide and conquer). Every value takes part in only about log k merges."],
    editorial=["Priority queue: push the head of every non-empty list, keyed by value. Repeatedly pop the smallest node, append it to the result, and push that node's successor if it exists. The heap never holds more than k nodes, so each of the N pops and pushes costs O(log k): O(N log k) total.",
               "Divide and conquer gives the same bound with no heap: merge lists 0 and 1, 2 and 3, and so on, then merge the results again, until one list remains. There are about log k rounds and each round touches all N nodes. Merging lists sequentially into one growing result can degrade to O(N k), and concatenating plus sorting costs O(N log N)."],
    time="O(N log k)", space="O(k)",
    solution='''import heapq


class ListNode:
    def __init__(self, val=0, nxt=None):
        self.val = val
        self.next = nxt


def build(vals):
    head = None
    for v in reversed(vals):
        head = ListNode(v, head)
    return head


def mergeKLists(lists):
    heap = []
    for i, vals in enumerate(lists):
        node = build(vals)
        if node:
            heap.append((node.val, i, node))
    heapq.heapify(heap)
    dummy = ListNode()
    tail = dummy
    while heap:
        _, i, node = heapq.heappop(heap)
        tail.next = node
        tail = node
        if node.next:
            heapq.heappush(heap, (node.next.val, i, node.next))
    out = []
    cur = dummy.next
    while cur:
        out.append(cur.val)
        cur = cur.next
    return out
''',
    tests=[[[[1, 4, 5], [1, 3, 4], [2, 6]]], [[]], [[[]]], [[[], []]], [[[5]]], [[[1, 2, 3], [4, 5, 6]]],
           [[[4, 5, 6], [], [1, 2, 3]]], [[[2], [1], [3], [0]]], [[[1, 1, 1], [1, 1], [1]]],
           [[[INT_MIN, 0, INT_MAX], [INT_MIN, INT_MAX]]], [[[-3, -1], [], [-2, 0, 2], [], [1]]]],
)
_r = rnd(2110)
p["tests"].append([[_sorted_arr(_r, 50, -10 ** 9, 10 ** 9) for _ in range(200)]])
p["tests"].append([[_sorted_arr(_r, _r.randint(0, 100), -1000, 1000) for _ in range(100)]])
p["tests"].append([[_sorted_arr(_r, 5000, -10 ** 9, 10 ** 9), _sorted_arr(_r, 4000, -10 ** 9, 10 ** 9), [0], []]])
p["tests"].append([[[v] for v in sorted(_rl(_r, 200, -100, 100))[::-1]]])
p["tests"].append([[_sorted_arr(_r, 10, 0, 3) for _ in range(150)]])


def b_mergek(lists):
    # repeatedly take the smallest remaining head by scanning all lists
    pos = [0] * len(lists)
    out = []
    while True:
        best = -1
        for i, lst in enumerate(lists):
            if pos[i] < len(lst) and (best == -1 or lst[pos[i]] < lists[best][pos[best]]):
                best = i
        if best == -1:
            return out
        out.append(lists[best][pos[best]])
        pos[best] += 1


def g_mergek(r):
    return [[_sorted_arr(r, r.randint(0, 5), -9, 9) for _ in range(r.randint(0, 6))]]


def v_mergek(tests):
    for t in tests:
        lists = t["args"][0]
        assert len(lists) <= 200
        assert sum(len(x) for x in lists) <= 10000
        assert all(x == sorted(x) for x in lists)
        assert t["expected"] == sorted(t["expected"])


CHECKS["merge-k-sorted-linked-lists"] = (b_mergek, g_mergek, "exact")
VALIDATE["merge-k-sorted-linked-lists"] = v_mergek
