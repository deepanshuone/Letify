"""Problems: linked lists, basic operations (lists are passed as arrays of node values, head to tail). See data/lib.py for the registry."""
from collections import Counter  # noqa: F401

from lib import add, rnd, CHECKS, VALIDATE, gen_arr  # noqa: F401

INT_MIN, INT_MAX = -(2 ** 31), 2 ** 31 - 1
TOPIC = "Linked List"

ENC = ("<p><strong>Encoding.</strong> A singly linked list is passed to your function as an array holding the node values "
       "from head to tail; an empty array is an empty list. You may build real nodes from it first, or work on the array directly. "
       "Lists you return are given as arrays of values from head to tail.</p>")

LL = '''class ListNode:
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


def _sorted_arr(r, n, lo=-50, hi=50):
    return sorted(r.randint(lo, hi) for _ in range(n))


def _rl(r, n, lo=-10 ** 9, hi=10 ** 9):
    return [r.randint(lo, hi) for _ in range(n)]


# ================================================================ EASY

p = add(
    id="split-linked-list-at-middle", title="Split Linked List at the Middle", diff="Easy", topic=TOPIC,
    fn="splitAtMiddle", params=[("nums", "int[]")], ret="int[][]", cmp="exact",
    desc=ENC + "<p>Cut the list into two lists in the middle. The first list gets the first <code>ceil(n / 2)</code> nodes and the second list gets the remaining <code>floor(n / 2)</code> nodes, both keeping their original order. Return <code>[first, second]</code>, each given as an array of values.</p><p>For <code>[1,2,3,4,5]</code> the answer is <code>[[1,2,3],[4,5]]</code>, and for <code>[1,2,3,4]</code> it is <code>[[1,2],[3,4]]</code>. In a real linked list you do not know <code>n</code> in advance, so try to find the cut in a single pass without counting the nodes first.</p>",
    constraints=["2 &le; nums.length &le; 5,000", "-10<sup>9</sup> &le; nums[i] &le; 10<sup>9</sup>"],
    hints=["Counting the nodes first and then walking <code>n / 2</code> steps works. Can you locate the middle during a single walk?",
           "Use two pointers that start at the head: <code>slow</code> moves one node per step and <code>fast</code> moves two nodes per step.",
           "Stop when <code>fast.next</code> or <code>fast.next.next</code> is null. Then <code>slow</code> is the last node of the first half: the second list starts at <code>slow.next</code>, and you cut the link by setting <code>slow.next = null</code>."],
    editorial=["The slow and fast pointer technique finds the middle in one pass. While <code>fast</code> can still jump two nodes, move <code>slow</code> by one and <code>fast</code> by two. When the loop ends, <code>fast</code> is at (or next to) the tail and <code>slow</code> has covered half of the distance, so it sits on the last node of the first half. For an even length the first half ends at the left of the two middle nodes, which gives exactly <code>ceil(n / 2)</code> nodes in the first part.",
               "Cut the list by saving <code>second = slow.next</code> and setting <code>slow.next = null</code>. The scan is O(n) time and uses O(1) extra pointers. This split is the first step of merge sort on a linked list and of the palindrome check."],
    time="O(n)", space="O(1)",
    solution=LL + '''def splitAtMiddle(nums):
    head = build(nums)
    slow = fast = head
    while fast.next and fast.next.next:
        slow = slow.next
        fast = fast.next.next
    second = slow.next
    slow.next = None
    return [dump(head), dump(second)]
''',
    tests=[[[1, 2, 3, 4, 5]], [[1, 2, 3, 4]], [[1, 2]], [[1, 2, 3]], [[7, 7]], [[-1, 0, 1, 2, 3, 4]], [[INT_MIN, INT_MAX]],
           [[9, 8, 7, 6, 5, 4, 3, 2, 1, 0, -1]]],
)
_r = rnd(7101)
p["tests"].append([_rl(_r, 5000, -999, 999)])
p["tests"].append([_rl(_r, 4999, 0, 9)])
p["tests"].append([_rl(_r, 1000)])


def b_split(nums):
    h = (len(nums) + 1) // 2
    return [nums[:h], nums[h:]]


def v_split(tests):
    for t in tests:
        n = len(t["args"][0])
        assert 2 <= n <= 5000
        assert len(t["expected"][0]) == (n + 1) // 2 and len(t["expected"][1]) == n // 2


CHECKS["split-linked-list-at-middle"] = (b_split, lambda r: [gen_arr(r, -9, 9, 2, 10)], "exact")
VALIDATE["split-linked-list-at-middle"] = v_split

p = add(
    id="remove-listed-values-from-linked-list", title="Remove Listed Values from a Linked List", diff="Easy", topic=TOPIC,
    fn="removeListedValues", params=[("nums", "int[]"), ("banned", "int[]")], ret="int[]", cmp="exact",
    desc=ENC + "<p>Delete every node whose value appears anywhere in the array <code>banned</code>, and return the values of the remaining list from head to tail. The remaining nodes keep their original order. Several nodes in a row may need to be deleted, and so may the head.</p><p>For <code>nums = [1,2,6,3,4,5,6]</code> and <code>banned = [6,4]</code> the answer is <code>[1,2,3,5]</code>.</p>",
    constraints=["0 &le; nums.length &le; 5,000", "0 &le; banned.length &le; 1,000 (it may contain repeated values)", "-10<sup>9</sup> &le; nums[i], banned[j] &le; 10<sup>9</sup>"],
    hints=["Deleting a node means the node before it must skip over it. The head has no node before it.",
           "Checking a value against <code>banned</code> by scanning the whole array for every node is slow. Put the banned values in a hash set first.",
           "Put a dummy node in front of the head and walk with <code>prev</code> and <code>cur</code>: if <code>cur.val</code> is banned, set <code>prev.next = cur.next</code> and do not move <code>prev</code>; otherwise move <code>prev</code> forward too."],
    editorial=["Build a hash set from <code>banned</code> so each membership test is O(1). Place a dummy node before the head so that deleting the head needs no special case. Then walk the list with <code>prev</code> (the last kept node) and <code>cur</code>. A banned node is unlinked with <code>prev.next = cur.next</code>, and <code>prev</code> stays where it is, so a run of banned nodes is removed correctly. A kept node becomes the new <code>prev</code>.",
               "Time is O(n + m) for a list of n nodes and m banned values; extra space is O(m) for the set. Testing each node against the raw <code>banned</code> array would cost O(n * m)."],
    time="O(n + m)", space="O(m)",
    solution=LL + '''def removeListedValues(nums, banned):
    bad = set(banned)
    dummy = ListNode(0, build(nums))
    prev, cur = dummy, dummy.next
    while cur:
        if cur.val in bad:
            prev.next = cur.next
        else:
            prev = cur
        cur = cur.next
    return dump(dummy.next)
''',
    tests=[[[1, 2, 6, 3, 4, 5, 6], [6, 4]], [[], [1]], [[7, 7, 7], [7]], [[1, 2, 3], []], [[1, 2, 3], [4, 5]], [[5, 1, 5, 2, 5], [5]],
           [[1, 2, 3, 4], [1, 4]], [[INT_MIN, 0, INT_MAX], [INT_MAX, INT_MIN]], [[3, 3, 1, 3, 3, 2, 3], [3, 3]]],
)
_r = rnd(7102)
_a = [_r.randint(-50, 50) for _ in range(5000)]
p["tests"].append([_a, _r.sample(range(-50, 51), 25)])
p["tests"].append([_a, list(range(-50, 51))])
p["tests"].append([_rl(_r, 1500), []])
_a = _rl(_r, 1500)
p["tests"].append([_a, [_r.choice(_a) for _ in range(1000)]])


def b_rmset(nums, banned):
    out = []
    for x in nums:
        if not any(x == b for b in banned):
            out.append(x)
    return out


def g_rmset(r):
    return [gen_arr(r, -4, 4, 0, 10), gen_arr(r, -4, 4, 0, 4)]


def v_rmset(tests):
    for t in tests:
        nums, banned = t["args"]
        assert len(nums) <= 5000 and len(banned) <= 1000
    assert any(len(t["expected"]) == 0 for t in tests) and any(len(t["expected"]) > 0 for t in tests)


CHECKS["remove-listed-values-from-linked-list"] = (b_rmset, g_rmset, "exact")
VALIDATE["remove-listed-values-from-linked-list"] = v_rmset

p = add(
    id="remove-duplicates-from-sorted-list", title="Remove Duplicates from a Sorted Linked List", diff="Easy", topic=TOPIC,
    fn="deleteDuplicates", params=[("nums", "int[]")], ret="int[]", cmp="exact",
    desc=ENC + "<p>The list is sorted in non-decreasing order. Delete nodes so that every value appears exactly once (keep the first node of each run of equal values) and return the values of the resulting list.</p><p>For <code>[1,1,2,3,3,3,4]</code> the answer is <code>[1,2,3,4]</code>. Use the fact that equal values are neighbours: no hash set is needed.</p>",
    constraints=["0 &le; nums.length &le; 5,000", "-10<sup>9</sup> &le; nums[i] &le; 10<sup>9</sup>", "nums is sorted in non-decreasing order"],
    hints=["Because the list is sorted, all copies of a value sit next to each other.",
           "Compare each node only with the node right after it.",
           "Walk with one pointer <code>cur</code>. While <code>cur.next</code> has the same value as <code>cur</code>, unlink it with <code>cur.next = cur.next.next</code> and stay on <code>cur</code>; otherwise step forward."],
    editorial=["Since the list is sorted, duplicates form contiguous runs. Stand on the first node of a run and keep unlinking the following node while it has the same value. Once the next value differs, step forward. The head is always kept, so no dummy node is needed.",
               "Every node is looked at once: O(n) time and O(1) extra space. A hash set would also work but wastes memory and ignores the ordering. Be careful not to advance <code>cur</code> after an unlink, otherwise runs of three or more equal values are only partly removed."],
    time="O(n)", space="O(1)",
    solution=LL + '''def deleteDuplicates(nums):
    head = build(nums)
    cur = head
    while cur:
        while cur.next and cur.next.val == cur.val:
            cur.next = cur.next.next
        cur = cur.next
    return dump(head)
''',
    tests=[[[1, 1, 2, 3, 3, 3, 4]], [[]], [[5]], [[2, 2, 2, 2]], [[1, 2, 3]], [[-3, -3, 0, 0, 7, 7]], [[1, 1]],
           [[INT_MIN, INT_MIN, 0, INT_MAX, INT_MAX]], [[1, 2, 2, 3]]],
)
_r = rnd(7103)
p["tests"].append([_sorted_arr(_r, 5000, -2000, 2000)])
p["tests"].append([[4] * 5000])
p["tests"].append([sorted(_r.sample(range(-10 ** 9, 10 ** 9), 1500))])
p["tests"].append([_sorted_arr(_r, 1500, -10 ** 9, 10 ** 9)])


def b_dedupe(nums):
    return sorted(set(nums))


def g_dedupe(r):
    return [sorted(gen_arr(r, -5, 5, 0, 12))]


def v_dedupe(tests):
    for t in tests:
        a = t["args"][0]
        assert len(a) <= 5000 and a == sorted(a)
        assert t["expected"] == sorted(set(a))


CHECKS["remove-duplicates-from-sorted-list"] = (b_dedupe, g_dedupe, "exact")
VALIDATE["remove-duplicates-from-sorted-list"] = v_dedupe

# ================================================================ MEDIUM

p = add(
    id="reverse-linked-list-between-positions", title="Reverse Linked List Between Positions", diff="Medium", topic=TOPIC, tier="must",
    fn="reverseBetween", params=[("nums", "int[]"), ("left", "int"), ("right", "int")], ret="int[]", cmp="exact",
    desc=ENC + "<p>Reverse only the part of the list from position <code>left</code> to position <code>right</code> (both inclusive, counting from <code>1</code> at the head). The nodes before <code>left</code> and after <code>right</code> stay where they are. Return the values of the resulting list from head to tail.</p><p>For <code>nums = [1,2,3,4,5]</code>, <code>left = 2</code>, <code>right = 4</code> the answer is <code>[1,4,3,2,5]</code>. Aim for a single pass over the list that relinks nodes in place.</p>",
    constraints=["1 &le; nums.length &le; 5,000", "1 &le; left &le; right &le; nums.length", "-10<sup>9</sup> &le; nums[i] &le; 10<sup>9</sup>"],
    hints=["Reversing the whole list is a loop that flips <code>next</code> pointers. Here you must reconnect the reversed part to the nodes on both sides.",
           "Walk to the node just before position <code>left</code> (use a dummy node so that <code>left = 1</code> is not special). Call it <code>pre</code>.",
           "Let <code>cur = pre.next</code>. Repeat <code>right - left</code> times: take <code>nxt = cur.next</code>, unlink it with <code>cur.next = nxt.next</code> and insert it right after <code>pre</code> (<code>nxt.next = pre.next; pre.next = nxt</code>). The first node of the segment slides to its end and automatically connects to the rest."],
    editorial=["Put a dummy node before the head and move <code>pre</code> to the node at position <code>left - 1</code>. The node <code>cur = pre.next</code> is the first node of the segment; it will become the last node of the reversed segment. For each of the next <code>right - left</code> nodes, detach the node that follows <code>cur</code> and insert it directly after <code>pre</code>. After every step the front part of the segment is reversed, and <code>cur.next</code> already points to the first node after the segment, so no extra reconnection is needed.",
               "Time is O(n) with a single pass and space is O(1). Alternatives: reverse the segment as a stand-alone list and then fix four pointers (before, segment head, segment tail, after), which is easier to get wrong at the boundaries; or copy the values into an array and reverse a slice, which uses O(n) memory."],
    time="O(n)", space="O(1)",
    solution=LL + '''def reverseBetween(nums, left, right):
    dummy = ListNode(0, build(nums))
    pre = dummy
    for _ in range(left - 1):
        pre = pre.next
    cur = pre.next
    for _ in range(right - left):
        nxt = cur.next
        cur.next = nxt.next
        nxt.next = pre.next
        pre.next = nxt
    return dump(dummy.next)
''',
    tests=[[[1, 2, 3, 4, 5], 2, 4], [[5], 1, 1], [[1, 2], 1, 2], [[1, 2, 3], 2, 2], [[1, 2, 3, 4, 5], 1, 5], [[1, 2, 3, 4, 5], 1, 3],
           [[1, 2, 3, 4, 5], 3, 5], [[3, 5], 1, 1], [[INT_MIN, 0, INT_MAX, 7], 2, 3], [[1, 2, 3, 4, 5, 6, 7, 8], 4, 5]],
)
_r = rnd(7104)
_a = _rl(_r, 5000, -99, 99)
p["tests"].append([_a, 1, 5000])
p["tests"].append([_a, 1234, 3456])
p["tests"].append([_rl(_r, 1000), 2, 999])


def b_revbetween(nums, left, right):
    return nums[:left - 1] + nums[left - 1:right][::-1] + nums[right:]


def g_revbetween(r):
    a = gen_arr(r, -9, 9, 1, 10)
    left = r.randint(1, len(a))
    return [a, left, r.randint(left, len(a))]


def v_revbetween(tests):
    for t in tests:
        nums, left, right = t["args"]
        assert 1 <= len(nums) <= 5000 and 1 <= left <= right <= len(nums)


CHECKS["reverse-linked-list-between-positions"] = (b_revbetween, g_revbetween, "exact")
VALIDATE["reverse-linked-list-between-positions"] = v_revbetween

p = add(
    id="delete-all-duplicated-values-sorted-list", title="Delete All Duplicated Values from a Sorted List", diff="Medium", topic=TOPIC,
    fn="deleteAllDuplicates", params=[("nums", "int[]")], ret="int[]", cmp="exact",
    desc=ENC + "<p>The list is sorted in non-decreasing order. Delete <em>every</em> node whose value occurs more than once, so that only the values that appear exactly once in the original list remain. Return the remaining values from head to tail.</p><p>For <code>[1,2,3,3,4,4,5]</code> the answer is <code>[1,2,5]</code>; for <code>[1,1,1,2,3]</code> it is <code>[2,3]</code>. Unlike plain duplicate removal, not even one copy of a repeated value is kept, so the head itself may disappear.</p>",
    constraints=["0 &le; nums.length &le; 5,000", "-10<sup>9</sup> &le; nums[i] &le; 10<sup>9</sup>", "nums is sorted in non-decreasing order"],
    hints=["Counting values with a hash map works. Because the list is sorted, you can decide locally instead.",
           "A node is a duplicate if it equals its neighbour. When you find a run of equal values, remove the whole run, including its first node. That needs a pointer to the node <em>before</em> the run, so use a dummy head.",
           "Keep <code>prev</code> (the last kept node). At <code>cur</code>: if <code>cur.next</code> exists and has the same value, remember <code>v = cur.val</code>, skip forward while <code>cur.val == v</code>, then set <code>prev.next = cur</code>. Otherwise <code>prev = cur</code>. In both cases continue from <code>cur</code> (or <code>cur.next</code> in the keep case)."],
    editorial=["Use a dummy node before the head. <code>prev</code> always points at the last node that is known to stay. Look at <code>cur = prev.next</code>. If the next node has the same value, the whole run of that value must go: advance <code>cur</code> past every node with that value and link <code>prev.next</code> directly to the first node after the run. Do <em>not</em> move <code>prev</code> yet, because the node after the run can itself start another run of duplicates. If <code>cur</code> is not duplicated, it is kept and <code>prev</code> moves onto it.",
               "Each node is visited a constant number of times: O(n) time, O(1) extra space. The dummy node handles the case where the first value is duplicated. Counting occurrences in a map is also O(n) time but uses O(n) memory and does not exploit sortedness."],
    time="O(n)", space="O(1)",
    solution=LL + '''def deleteAllDuplicates(nums):
    dummy = ListNode(0, build(nums))
    prev = dummy
    cur = dummy.next
    while cur:
        if cur.next and cur.next.val == cur.val:
            v = cur.val
            while cur and cur.val == v:
                cur = cur.next
            prev.next = cur
        else:
            prev = cur
            cur = cur.next
    return dump(dummy.next)
''',
    tests=[[[1, 2, 3, 3, 4, 4, 5]], [[1, 1, 1, 2, 3]], [[]], [[4]], [[2, 2]], [[1, 1, 2, 2, 3, 3]], [[1, 2, 3]], [[1, 2, 2, 2, 3]],
           [[-5, -5, 0, 1, 1, 9]], [[INT_MIN, INT_MIN, 3, INT_MAX]], [[0, 1, 1, 2, 3, 3, 3, 4, 5, 5]]],
)
_r = rnd(7105)
p["tests"].append([_sorted_arr(_r, 4000, -3000, 3000)])
p["tests"].append([_sorted_arr(_r, 5000, -400, 400)])
p["tests"].append([sorted(_r.sample(range(-10 ** 9, 10 ** 9), 1500))])
p["tests"].append([[6] * 2500 + [7] + [8] * 1500 + [9]])


def b_alldup(nums):
    c = Counter(nums)
    return [x for x in nums if c[x] == 1]


def g_alldup(r):
    return [sorted(gen_arr(r, -4, 4, 0, 12))]


def v_alldup(tests):
    for t in tests:
        a = t["args"][0]
        assert len(a) <= 5000 and a == sorted(a)
    assert any(len(t["expected"]) == 0 for t in tests)


CHECKS["delete-all-duplicated-values-sorted-list"] = (b_alldup, g_alldup, "exact")
VALIDATE["delete-all-duplicated-values-sorted-list"] = v_alldup

p = add(
    id="merge-nodes-between-zeros", title="Merge Nodes Between Zeros", diff="Medium", topic=TOPIC,
    fn="mergeBetweenZeros", params=[("nums", "int[]")], ret="int[]", cmp="exact",
    desc=ENC + "<p>The list starts and ends with a node of value <code>0</code>, and no two zeros are adjacent. Between every two consecutive zeros there is a block of one or more positive values. Replace each block (together with its closing zero) by a single node holding the <em>sum</em> of the block, and remove all zeros. Return the values of the new list.</p><p>For <code>[0,3,1,0,4,5,2,0]</code> the blocks are <code>[3,1]</code> and <code>[4,5,2]</code>, so the answer is <code>[4,11]</code>. Try to do it by reusing the existing nodes with one pass.</p>",
    constraints=["3 &le; nums.length &le; 5,000", "nums[0] = 0 and nums[nums.length - 1] = 0, and no two zeros are adjacent", "1 &le; nums[i] &le; 1,000 for every non-zero value (so every sum fits in 32 bits)"],
    hints=["Every zero ends one block and begins the next one. There is one result node per block.",
           "Walk through the list keeping a running sum. Add each positive value to it. What should happen when you meet a zero?",
           "Skip the leading zero. At every later zero, the running sum is complete: write it into a result node (or overwrite the first node of the block in place) and reset the sum to 0. The last zero finishes the last block."],
    editorial=["Scan once with a running sum <code>s</code>. A positive value is added to <code>s</code>. A zero closes the current block: append <code>s</code> to the result and reset <code>s</code> to 0. The very first zero closes an empty block, so skip it (or start the scan at the second node). With real nodes you can reuse them: keep a <code>tail</code> pointer into the output, store <code>s</code> into the first node of the block and link <code>tail.next</code> to the closing zero's successor; here we only need the final values.",
               "The pass is O(n) time. Extra space is O(1) when relinking nodes in place, and O(k) for k blocks when you build a separate result. Because the values are at most 1,000 and the list holds at most 5,000 nodes, a block sum is at most 5 * 10<sup>6</sup>."],
    time="O(n)", space="O(1)",
    solution=LL + '''def mergeBetweenZeros(nums):
    head = build(nums)
    out = ListNode()
    tail = out
    s = 0
    cur = head.next
    while cur:
        if cur.val == 0:
            tail.next = ListNode(s)
            tail = tail.next
            s = 0
        else:
            s += cur.val
        cur = cur.next
    return dump(out.next)
''',
    tests=[[[0, 3, 1, 0, 4, 5, 2, 0]], [[0, 1, 0]], [[0, 1, 2, 3, 0]], [[0, 5, 0, 5, 0, 5, 0]], [[0, 1000, 1000, 0, 1, 0]],
           [[0, 7, 0]], [[0, 1, 1, 1, 1, 0, 2, 0]]],
)
_r = rnd(7106)


def _zeros_list(r, blocks, lo, hi, maxlen):
    a = [0]
    for _ in range(blocks):
        a += [r.randint(lo, hi) for _ in range(r.randint(1, maxlen))] + [0]
    return a


p["tests"].append([_zeros_list(_r, 800, 1, 1000, 5)])
p["tests"].append([[0] + [1000, 0] * 2499])
p["tests"].append([[0] + [1000] * 4998 + [0]])


def b_zeros(nums):
    blocks, cur = [], None
    for x in nums:
        if x == 0:
            if cur is not None:
                blocks.append(sum(cur))
            cur = []
        else:
            cur.append(x)
    return blocks


def g_zeros(r):
    return [_zeros_list(r, r.randint(1, 4), 1, 9, 4)]


def v_zeros(tests):
    for t in tests:
        a = t["args"][0]
        assert 3 <= len(a) <= 5000 and a[0] == 0 and a[-1] == 0
        assert all(0 <= x <= 1000 for x in a)
        assert all(not (a[i] == 0 and a[i + 1] == 0) for i in range(len(a) - 1))
        assert all(v > 0 for v in t["expected"])


CHECKS["merge-nodes-between-zeros"] = (b_zeros, g_zeros, "exact")
VALIDATE["merge-nodes-between-zeros"] = v_zeros

p = add(
    id="merge-ascending-and-descending-lists", title="Merge an Ascending and a Descending List", diff="Medium", topic=TOPIC,
    fn="mergeAscDesc", params=[("a", "int[]"), ("b", "int[]")], ret="int[]", cmp="exact",
    desc=ENC + "<p>The list <code>a</code> is sorted in non-decreasing order, but the list <code>b</code> is sorted in <em>non-increasing</em> order (largest value first). Merge them into a single list sorted in non-decreasing order and return its values from head to tail.</p><p>For <code>a = [1,4,6]</code> and <code>b = [7,5,5,2]</code> the answer is <code>[1,2,4,5,5,6,7]</code>. The textbook merge of two ascending lists does not apply directly: the nodes of <code>b</code> have to be consumed from the other end. Try to do it in O(n + m) time with O(1) extra space by relinking nodes.</p>",
    constraints=["0 &le; a.length, b.length &le; 5,000", "-10<sup>9</sup> &le; a[i], b[i] &le; 10<sup>9</sup>", "a is non-decreasing, b is non-increasing"],
    hints=["Sorting everything would work but ignores the structure. What is special about the order of b?",
           "The smallest value of b is its tail, which a singly linked list cannot reach quickly. What operation turns a non-increasing list into a non-decreasing one?",
           "Reverse b in place (a single pass), then run the standard two-pointer merge of two non-decreasing lists with a dummy head and a tail pointer."],
    editorial=["First reverse <code>b</code> by flipping its <code>next</code> pointers; this takes O(m) time and O(1) space and makes it non-decreasing. Then merge as usual: compare the two heads, append the smaller to the tail of the result, and advance in that list. When one list is exhausted, link the remainder of the other list.",
               "Total time is O(n + m) and extra space is O(1). A different but equivalent idea is to build the answer from the large end: the largest remaining value is either the tail of <code>a</code> or the head of <code>b</code>, and prepending nodes to the result avoids reversing anything, but it needs the tail of <code>a</code> and so a reversal of <code>a</code> instead."],
    time="O(n + m)", space="O(1)",
    solution=LL + '''def mergeAscDesc(a, b):
    l1 = build(a)
    # reverse b so that it becomes non-decreasing
    l2 = None
    cur = build(b)
    while cur:
        nxt = cur.next
        cur.next = l2
        l2 = cur
        cur = nxt
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
    tests=[[[1, 4, 6], [7, 5, 5, 2]], [[], []], [[], [3, 2, 1]], [[1, 2, 3], []], [[1, 2, 3], [3, 2, 1]], [[5], [5]],
           [[1, 1, 1], [1, 1]], [[-5, 0, 5], [6, 1, -1, -6]], [[INT_MIN, 0], [INT_MAX, 0]], [[10, 20], [9, 8, 7]], [[1, 2], [9, 8]]],
)
_r = rnd(7107)
p["tests"].append([_sorted_arr(_r, 1000, -10 ** 9, 10 ** 9), sorted(_rl(_r, 1000), reverse=True)])
p["tests"].append([_sorted_arr(_r, 5000, -5, 5), sorted([_r.randint(-5, 5) for _ in range(3000)], reverse=True)])
p["tests"].append([list(range(1000)), list(range(2000, 1000, -1))])


def b_ascdesc(a, b):
    return sorted(a + b)


def g_ascdesc(r):
    return [_sorted_arr(r, r.randint(0, 8), -9, 9), sorted(gen_arr(r, -9, 9, 0, 8), reverse=True)]


def v_ascdesc(tests):
    for t in tests:
        a, b = t["args"]
        assert len(a) <= 5000 and len(b) <= 5000
        assert a == sorted(a) and b == sorted(b, reverse=True)


CHECKS["merge-ascending-and-descending-lists"] = (b_ascdesc, g_ascdesc, "exact")
VALIDATE["merge-ascending-and-descending-lists"] = v_ascdesc

p = add(
    id="remove-nodes-with-greater-value-to-the-right", title="Remove Nodes with a Greater Value to the Right", diff="Medium", topic=TOPIC,
    fn="removeSmallerLeft", params=[("nums", "int[]")], ret="int[]", cmp="exact",
    desc=ENC + "<p>Delete every node that has a node with a <em>strictly greater</em> value somewhere to its right (not only directly after it). Return the values of the remaining list from head to tail.</p><p>For <code>[5,2,13,3,8]</code>: the nodes <code>5</code> and <code>2</code> have <code>13</code> to their right, and <code>3</code> has <code>8</code> to its right, so the answer is <code>[13,8]</code>. Equal values do not delete each other: <code>[4,4,1]</code> stays <code>[4,4,1]</code>.</p>",
    constraints=["1 &le; nums.length &le; 5,000", "-10<sup>9</sup> &le; nums[i] &le; 10<sup>9</sup>"],
    hints=["A node survives only if no larger value exists to its right. Checking every pair is O(n<sup>2</sup>). Which direction makes the 'to the right' condition easy to track?",
           "Look at the list from the tail towards the head: you only need the maximum of everything seen so far.",
           "Reverse the list, walk it while remembering the maximum value so far, and keep a node only if its value is at least that maximum (unlink it otherwise). Reverse the surviving list back. A monotonic stack gives the same result in one forward pass."],
    editorial=["Scanning from the right, a node survives exactly when its value is greater than or equal to every value to its right, i.e. when it is at least the running maximum. A singly linked list cannot be scanned from the right, so reverse it first, filter while tracking the maximum, and reverse again. All three passes are O(n) and use O(1) extra space.",
               "Alternatively, scan from the left with a stack: before pushing a value, pop every stack element that is smaller than it (those nodes have a greater value to their right). The stack that remains is non-increasing and is the answer. This takes O(n) time and O(n) space. Note that the result is always a non-increasing sequence ending with the original tail."],
    time="O(n)", space="O(1)",
    solution=LL + '''def reverse(head):
    prev = None
    while head:
        nxt = head.next
        head.next = prev
        prev = head
        head = nxt
    return prev


def removeSmallerLeft(nums):
    head = reverse(build(nums))
    dummy = ListNode(0, head)
    prev, cur = dummy, head
    mx = None
    while cur:
        if mx is not None and cur.val < mx:
            prev.next = cur.next
        else:
            mx = cur.val
            prev = cur
        cur = cur.next
    return dump(reverse(dummy.next))
''',
    tests=[[[5, 2, 13, 3, 8]], [[4, 4, 1]], [[1]], [[1, 2, 3, 4]], [[4, 3, 2, 1]], [[3, 3, 3]], [[1, 100, 1, 100, 1]],
           [[-5, -3, -4, -1, -2]], [[INT_MIN, INT_MAX, INT_MIN]], [[2, 1, 2, 1, 2]]],
)
_r = rnd(7108)
p["tests"].append([_rl(_r, 3000)])
p["tests"].append([sorted(_r.sample(range(1, 10 ** 6), 2000), reverse=True)])
p["tests"].append([sorted(_r.sample(range(1, 10 ** 6), 3000))])
p["tests"].append([[_r.randint(0, 20) for _ in range(5000)]])


def b_rmgreater(nums):
    return [x for i, x in enumerate(nums) if all(y <= x for y in nums[i + 1:])]


def v_rmgreater(tests):
    for t in tests:
        assert 1 <= len(t["args"][0]) <= 5000
        e = t["expected"]
        assert e and all(e[i] >= e[i + 1] for i in range(len(e) - 1))


CHECKS["remove-nodes-with-greater-value-to-the-right"] = (b_rmgreater, lambda r: [gen_arr(r, -6, 6, 1, 10)], "exact")
VALIDATE["remove-nodes-with-greater-value-to-the-right"] = v_rmgreater

p = add(
    id="remove-zero-sum-consecutive-nodes", title="Remove Zero-Sum Consecutive Nodes", diff="Medium", topic=TOPIC,
    fn="removeZeroSum", params=[("nums", "int[]")], ret="int[]", cmp="exact",
    desc=ENC + "<p>A block of consecutive nodes whose values add up to <code>0</code> can be deleted. Repeat the following until no block of consecutive nodes with sum <code>0</code> exists: take the <em>leftmost</em> node that is the first node of some zero-sum block, and delete the <em>longest</em> zero-sum block that starts at that node. Return the values of the remaining list.</p><p>For <code>[1,2,-3,3,1]</code> the leftmost block start is the head, where <code>1+2-3 = 0</code> is the longest zero-sum block, so it is deleted and the answer is <code>[3,1]</code> (deleting <code>[-3,3]</code> instead would give a different list, which is why the rule above fixes the order). For <code>[1,2,3,-3,4]</code> the answer is <code>[1,2,4]</code>, and for <code>[1,2,3,-3,-2]</code> it is <code>[1]</code>.</p><p>A node with value <code>0</code> is itself a zero-sum block of length one.</p>",
    constraints=["1 &le; nums.length &le; 5,000", "-1,000 &le; nums[i] &le; 1,000", "The result may be empty"],
    hints=["A block of nodes from position i+1 to j has sum zero exactly when the prefix sums before i+1 and after j are equal.",
           "Store prefix sums in a hash map. If a prefix sum repeats, everything between its two occurrences cancels. Which occurrence of the prefix value should you jump to to delete the <em>longest</em> block?",
           "First pass: compute the prefix sum at every node (with a dummy node at prefix 0) and record in a map the <em>last</em> node having each prefix sum. Second pass: for every node in the chain from the dummy, set <code>node.next = last[prefix(node)].next</code> and move on to that next node."],
    editorial=["Let <code>P</code> be the prefix sums of the list, with <code>P = 0</code> before the head. A block of consecutive nodes sums to zero exactly when two prefix sums are equal. Deleting a zero-sum block does not change any later prefix sum, which is why the order described in the statement leads to the same result as a single sweep.",
               "Pass one: walk the list from a dummy node and store, for each prefix sum, the last node where it occurs. Pass two: walk again with a running prefix sum, and for each node set its <code>next</code> to the node after <code>last[prefix]</code>. This jumps over the longest zero-sum block that begins right after the node. Afterwards no two kept boundaries share the same prefix sum, so no zero-sum block is left.",
               "Time is O(n) and extra space is O(n) for the hash map. Repeating a naive search for a zero-sum block after each deletion would cost O(n<sup>2</sup>) or worse."],
    time="O(n)", space="O(n)",
    solution=LL + '''def removeZeroSum(nums):
    dummy = ListNode(0, build(nums))
    last = {}
    s = 0
    cur = dummy
    while cur:
        s += cur.val
        last[s] = cur
        cur = cur.next
    s = 0
    cur = dummy
    while cur:
        s += cur.val
        cur.next = last[s].next
        cur = cur.next
    return dump(dummy.next)
''',
    tests=[[[1, 2, -3, 3, 1]], [[1, 2, 3, -3, 4]], [[1, 2, 3, -3, -2]], [[0]], [[5]], [[1, -1]], [[3, -3, 2, -2, 1]], [[1, 1, -1, -1]],
           [[2, 3, -5, 4, -4, 7]], [[1000, -1000, 1000, -1000, 1]], [[0, 0, 0, 5]]],
)
_r = rnd(7109)
p["tests"].append([[_r.randint(-1000, 1000) for _ in range(5000)]])
p["tests"].append([[_r.choice([-1, 1, 2, -2, 3]) for _ in range(5000)]])
p["tests"].append([[_r.choice([-2, 5]) * _r.randint(1, 50) for _ in range(3000)]])
p["tests"].append([[(i % 7) + 1 if i % 14 < 7 else -((i % 7) + 1) for i in range(4900)]])


def b_zerosum(nums):
    a = list(nums)
    while True:
        best = None
        for i in range(len(a)):
            s = 0
            for j in range(i, len(a)):
                s += a[j]
                if s == 0:
                    best = (i, j)
            if best:
                break
        if not best:
            return a
        a = a[:best[0]] + a[best[1] + 1:]


def v_zerosum(tests):
    for t in tests:
        a = t["args"][0]
        assert 1 <= len(a) <= 5000 and all(-1000 <= x <= 1000 for x in a)
        s, seen = 0, {0}
        for x in t["expected"]:
            s += x
            assert s not in seen, "zero-sum block left"
            seen.add(s)
    assert any(len(t["expected"]) == 0 for t in tests)


CHECKS["remove-zero-sum-consecutive-nodes"] = (b_zerosum, lambda r: [gen_arr(r, -3, 3, 1, 10)], "exact")
VALIDATE["remove-zero-sum-consecutive-nodes"] = v_zerosum

# ================================================================ HARD

p = add(
    id="best-single-range-reversal-zigzag-score", title="Best Single Range Reversal for Zigzag Score", diff="Hard", topic=TOPIC, tier="extra",
    fn="maxScoreAfterOneReversal", params=[("nums", "int[]")], ret="int", cmp="exact",
    desc=ENC + "<p>The <em>score</em> of a list is the sum of <code>|x - y|</code> over every pair of neighbouring nodes <code>x, y</code> (a list with fewer than two nodes has score 0).</p><p>You may reverse <em>at most one</em> contiguous range of nodes (possibly empty or a single node, which changes nothing). Return the largest score you can obtain.</p><p>For <code>[2,3,1,5,4]</code> the score is <code>1+2+4+1 = 8</code>. Reversing the range at positions 2 to 4 (1-indexed) gives <code>[2,5,1,3,4]</code> with score <code>3+4+2+1 = 10</code>, which is the best, so the answer is <code>10</code>. Checking every range with a full recount is O(n<sup>3</sup>); a linear solution exists.</p>",
    constraints=["1 &le; nums.length &le; 5,000", "-100,000 &le; nums[i] &le; 100,000 (all scores fit in 32 bits)"],
    hints=["Reversing a range keeps all differences <em>inside</em> the range (only their order changes). Only the two boundary pairs change.",
           "Reversing positions l..r replaces the boundary differences |a[l-1]-a[l]| + |a[r]-a[r+1]| by |a[l-1]-a[r]| + |a[l]-a[r+1]|. Handle the cases l = 1 and r = n (only one boundary) separately. That already gives an O(n<sup>2</sup>) solution.",
           "For the case with two boundaries, the best gain is 2 * (max over adjacent pairs of min(x, y) minus min over adjacent pairs of max(x, y)), if positive. Intuition: pick two different adjacent pairs, one very high and one very low, and 'cross' them. Take the best of this, of the prefix reversals and of the suffix reversals."],
    editorial=["Write the score as <code>T</code>. Reversing <code>a[l..r]</code> does not change the absolute differences between neighbours inside the range, only the two links at its ends. So the new score is <code>T - |a[l-1]-a[l]| - |a[r]-a[r+1]| + |a[l-1]-a[r]| + |a[l]-a[r+1]|</code>. If the range touches the head only the right link matters (gain <code>|a[0]-a[r+1]| - |a[r]-a[r+1]|</code>), and if it touches the tail only the left link matters. Trying all of these takes O(n) time.",
               "Ranges with two inner boundaries need a trick. The gain equals <code>|a[i]-a[j]| + |a[i+1]-a[j+1]| - |a[i]-a[i+1]| - |a[j]-a[j+1]|</code> for two different links <code>(i, i+1)</code> and <code>(j, j+1)</code>. Case analysis on the order of the four values shows the best gain is <code>2 * (maxLow - minHigh)</code>, where <code>maxLow</code> is the largest <code>min(a[i], a[i+1])</code> and <code>minHigh</code> is the smallest <code>max(a[i], a[i+1])</code> over all links: the two links come from one 'high' link that lies entirely above the 'low' link, and reversing between them 'crosses' the links so that each gap is replaced with a gap between the two extremes. If the value is not positive, no inner reversal helps.",
               "The answer is <code>T + max(0, prefix gain, suffix gain, inner gain)</code>. Everything is O(n) time and O(1) extra space. Always compare with a brute force over all ranges when you implement this."],
    time="O(n)", space="O(1)",
    solution='''def maxScoreAfterOneReversal(nums):
    n = len(nums)
    if n < 2:
        return 0
    total = sum(abs(nums[i] - nums[i + 1]) for i in range(n - 1))
    best = 0
    # range touching the head: reverse a[0..r], r < n-1
    for r in range(n - 1):
        best = max(best, abs(nums[0] - nums[r + 1]) - abs(nums[r] - nums[r + 1]))
    # range touching the tail: reverse a[l..n-1], l > 0
    for l in range(1, n):
        best = max(best, abs(nums[l - 1] - nums[n - 1]) - abs(nums[l - 1] - nums[l]))
    # range with two inner boundaries
    max_low = -10 ** 18
    min_high = 10 ** 18
    for i in range(n - 1):
        max_low = max(max_low, min(nums[i], nums[i + 1]))
        min_high = min(min_high, max(nums[i], nums[i + 1]))
    best = max(best, 2 * (max_low - min_high))
    return total + best
''',
    tests=[[[2, 3, 1, 5, 4]], [[7]], [[1, 2]], [[5, 5, 5]], [[2, 4, 9, 24, 2, 1, 10]], [[1, 5, 1]], [[1, 2, 3, 4, 5]], [[10, 1, 10, 1, 10]],
           [[-100000, 100000, -100000, 100000]], [[3, 1, 4, 1, 5, 9, 2, 6]], [[0, 100000, 0]]],
)
_r = rnd(7110)
p["tests"].append([_rl(_r, 3000, -100000, 100000)])
p["tests"].append([_rl(_r, 4000, -100, 100)])
p["tests"].append([[100000 if i % 2 else -100000 for i in range(3000)]])
p["tests"].append([sorted(_rl(_r, 3000, -100000, 100000))])


def b_zigzag(nums):
    def score(a):
        return sum(abs(a[i] - a[i + 1]) for i in range(len(a) - 1))
    best = score(nums)
    for l in range(len(nums)):
        for r in range(l, len(nums)):
            best = max(best, score(nums[:l] + nums[l:r + 1][::-1] + nums[r + 1:]))
    return best


def g_zigzag(r):
    return [gen_arr(r, -12, 12, 1, 9)]


def v_zigzag(tests):
    for t in tests:
        a = t["args"][0]
        assert 1 <= len(a) <= 5000 and all(-100000 <= x <= 100000 for x in a)
        assert t["expected"] >= sum(abs(a[i] - a[i + 1]) for i in range(len(a) - 1))


CHECKS["best-single-range-reversal-zigzag-score"] = (b_zigzag, g_zigzag, "exact")
VALIDATE["best-single-range-reversal-zigzag-score"] = v_zigzag

p = add(
    id="remove-all-occurrences-of-sublist", title="Remove All Occurrences of a Sublist", diff="Hard", topic=TOPIC, tier="extra",
    fn="removeSublistRepeatedly", params=[("nums", "int[]"), ("pattern", "int[]")], ret="int[]", cmp="exact",
    desc=ENC + "<p>Repeat the following until it is no longer possible: find the <em>leftmost</em> place where the values of <code>pattern</code> appear as consecutive nodes of the list, and delete those nodes (the nodes on both sides are then joined, which can create a new occurrence). Return the values of the remaining list.</p><p>For <code>nums = [1,2,1,2,3,3,4]</code> and <code>pattern = [1,2,3]</code> the leftmost occurrence is at positions 3 to 5 (1-indexed), and removing it leaves <code>[1,2,3,4]</code>. That list again contains the pattern, so one more removal leaves <code>[4]</code>, which is the answer. An empty result is possible.</p>",
    constraints=["1 &le; nums.length &le; 5,000", "1 &le; pattern.length &le; 300", "-10<sup>9</sup> &le; nums[i], pattern[j] &le; 10<sup>9</sup>"],
    hints=["Searching for the pattern again from scratch after every deletion works but can be O(n<sup>2</sup> * m). Deleting can only create a new match that ends right at the cut.",
           "Process the nodes from left to right and keep the kept nodes on a stack. A match can only end at the node you just pushed, so you only need to know whether the top of the stack ends with the pattern.",
           "Track, for every stack entry, how many pattern values match at the end of the stack up to that entry (the KMP state). When the state reaches <code>len(pattern)</code>, pop that many entries; the state of the new top tells you where to continue."],
    editorial=["Pushing nodes on a stack and removing a match the moment it is completed is equivalent to always removing the leftmost match: the match that ends first is also the one that starts first, because all matches have the same length. After a pop the stack is exactly what remains of the list to the left of the cut, so any new match must end at a later node.",
               "To detect the end of a match in O(1) amortised time without rescanning, compute the KMP failure function of the pattern. Store with each stack entry the length <code>k</code> of the longest pattern prefix that is a suffix of the stack up to that entry. For a new value, start from the state of the top entry (0 for an empty stack), follow failure links while the next pattern value differs, and advance when it matches. If <code>k</code> reaches <code>m</code>, pop <code>m</code> entries; the stored state of the entry that is then on top is the state to continue from.",
               "Building the failure function costs O(m) and the scan is O(n) amortised in the usual case. Because a pop restarts from a stored state, a single push can occasionally cost O(m) failure-link steps, so the worst case is O(n * m), which is only about 1.5 million steps under these constraints. Extra space is O(n + m)."],
    time="O(n + m)", space="O(n + m)",
    solution='''def removeSublistRepeatedly(nums, pattern):
    m = len(pattern)
    fail = [0] * m
    k = 0
    for i in range(1, m):
        while k and pattern[i] != pattern[k]:
            k = fail[k - 1]
        if pattern[i] == pattern[k]:
            k += 1
        fail[i] = k
    vals = []
    states = []
    for x in nums:
        k = states[-1] if states else 0
        while k and x != pattern[k]:
            k = fail[k - 1]
        if x == pattern[k]:
            k += 1
        vals.append(x)
        states.append(k)
        if k == m:
            del vals[-m:]
            del states[-m:]
    return vals
''',
    tests=[[[1, 2, 1, 2, 3, 3], [1, 2, 3]], [[1, 2, 3], [1, 2, 3]], [[5, 6, 7], [8]], [[1, 1, 1, 1], [1, 1]], [[1, 1, 1, 1, 1], [1, 1]],
           [[1, 2, 1, 2, 1], [1, 2, 1]], [[1, 1, 2, 2], [1, 2]], [[3, 1, 3, 1, 3, 1, 3], [3, 1, 3]], [[4], [4]],
           [[1, 2, 1, 1, 2, 2, 1, 2], [1, 2]], [[INT_MIN, INT_MAX, INT_MIN, INT_MAX], [INT_MIN, INT_MAX]]],
)
_r = rnd(7111)


def _nested(r, depth, pat):
    """wrap a pattern into itself so that every removal exposes the next occurrence"""
    out = list(pat)
    for _ in range(depth):
        cut = r.randint(0, len(out))
        out = out[:cut] + list(pat) + out[cut:]
    return out


_pat = [1, 2, 1, 1, 2]
p["tests"].append([_nested(_r, 995, _pat), _pat])
p["tests"].append([[_r.randint(1, 2) for _ in range(5000)], [1, 2, 2]])
p["tests"].append([[_r.randint(1, 2) for _ in range(5000)], [1, 1, 2, 1, 1]])
p["tests"].append([[1] * 5000, [1] * 299])


def b_sublist(nums, pattern):
    a = list(nums)
    m = len(pattern)
    while True:
        for i in range(len(a) - m + 1):
            if a[i:i + m] == pattern:
                a = a[:i] + a[i + m:]
                break
        else:
            return a


def g_sublist(r):
    return [gen_arr(r, 0, 2, 0, 14) or [0], gen_arr(r, 0, 2, 1, 4)]


def v_sublist(tests):
    for t in tests:
        nums, pattern = t["args"]
        assert 1 <= len(nums) <= 5000 and 1 <= len(pattern) <= 300
    assert any(len(t["expected"]) == 0 for t in tests)
    assert any(len(t["expected"]) == len(t["args"][0]) for t in tests)


CHECKS["remove-all-occurrences-of-sublist"] = (b_sublist, g_sublist, "exact")
VALIDATE["remove-all-occurrences-of-sublist"] = v_sublist
