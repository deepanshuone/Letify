"""Problems: linked lists, reordering and sorting (lists are passed as arrays of node values, head to tail). See data/lib.py for the registry."""
import heapq

from lib import add, rnd, CHECKS, VALIDATE, gen_arr  # noqa: F401

INT_MIN, INT_MAX = -10 ** 9, 10 ** 9  # the value bound used in the constraints
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


def _rl(r, n, lo=-10 ** 4, hi=10 ** 4):
    return [r.randint(lo, hi) for _ in range(n)]


# ================================================================ EASY

p = add(
    id="swap-nodes-in-pairs", title="Swap Nodes in Pairs", diff="Easy", topic=TOPIC, tier="must",
    fn="swapPairs", params=[("nums", "int[]")], ret="int[]", cmp="exact",
    desc=ENC + "<p>Swap every two adjacent nodes of the list: the 1st and 2nd node trade places, then the 3rd and 4th, and so on. If the length is odd, the last node stays where it is. Return the values of the resulting list from head to tail.</p><p>For example <code>[1,2,3,4,5]</code> becomes <code>[2,1,4,3,5]</code>. In a real list you must exchange the <em>nodes</em> by relinking pointers, not just copy values between them.</p>",
    constraints=["0 &le; nums.length &le; 4,000", "-10<sup>9</sup> &le; nums[i] &le; 10<sup>9</sup>"],
    hints=["Look at one pair <code>a -> b</code> that is preceded by some node <code>prev</code>. After the swap you need <code>prev -> b -> a -> (whatever followed b)</code>.",
           "A dummy node placed before the head means the first pair is handled exactly like every other pair, and you never special-case the new head.",
           "Loop while <code>prev.next</code> and <code>prev.next.next</code> both exist: take <code>a = prev.next</code>, <code>b = a.next</code>; set <code>a.next = b.next</code>, <code>b.next = a</code>, <code>prev.next = b</code>; then move <code>prev</code> to <code>a</code>, which is now the second node of the swapped pair."],
    editorial=["Place a dummy node in front of the head and keep a <code>prev</code> pointer to the node just before the current pair. For a pair <code>a, b</code> three pointers change: <code>a.next</code> skips over <code>b</code>, <code>b.next</code> points back to <code>a</code>, and <code>prev.next</code> points to <code>b</code>. After that <code>a</code> is the last node of the finished pair, so it becomes the new <code>prev</code>. The loop stops when fewer than two nodes remain, which automatically leaves a lone last node untouched.",
               "Each node is visited once, so the time is O(n) and only a constant number of pointers is used. A recursive solution (swap the first two, recurse on the rest) is shorter but uses O(n) stack."],
    time="O(n)", space="O(1)",
    solution=NODE + '''def swapPairs(nums):
    dummy = ListNode(0, build(nums))
    prev = dummy
    while prev.next and prev.next.next:
        a = prev.next
        b = a.next
        a.next = b.next
        b.next = a
        prev.next = b
        prev = a
    return dump(dummy.next)
''',
    tests=[[[1, 2, 3, 4, 5]], [[1, 2, 3, 4]], [[]], [[7]], [[1, 2]], [[1, 2, 3]], [[5, 5, 5, 5, 5]],
           [[INT_MIN, INT_MAX, 0, -1]], [[-1, -2, -3, -4, -5, -6]]],
)
_r = rnd(7301)
p["tests"].append([_rl(_r, 4000)])
p["tests"].append([_rl(_r, 3999)])
p["tests"].append([list(range(2000))])


def b_swap_pairs(nums):
    out = list(nums)
    for i in range(0, len(out) - 1, 2):
        out[i], out[i + 1] = out[i + 1], out[i]
    return out


def v_swap_pairs(tests):
    for t in tests:
        assert len(t["args"][0]) <= 4000
        assert sorted(t["expected"]) == sorted(t["args"][0])


CHECKS["swap-nodes-in-pairs"] = (b_swap_pairs, lambda r: [gen_arr(r, -9, 9, 0, 11)], "exact")
VALIDATE["swap-nodes-in-pairs"] = v_swap_pairs

p = add(
    id="sort-list-sorted-by-absolute-value", title="Sort a List Already Ordered by Absolute Value", diff="Easy", topic=TOPIC, tier="extra",
    fn="sortAbsoluteOrdered", params=[("nums", "int[]")], ret="int[]", cmp="exact",
    desc=ENC + "<p>The list is sorted in non-decreasing order of <em>absolute value</em>: <code>|nums[0]| &le; |nums[1]| &le; ...</code>. Values with equal absolute value may appear in any order (for example <code>3, -3, 3</code>). Return the list sorted in ordinary non-decreasing order of the values themselves.</p><p>For example <code>[0,1,-2,3,-4]</code> becomes <code>[-4,-2,0,1,3]</code>. A general O(n log n) sort works, but the existing order lets you finish in O(n) time by relinking nodes.</p>",
    constraints=["0 &le; nums.length &le; 5,000", "-10<sup>9</sup> &le; nums[i] &le; 10<sup>9</sup>", "|nums[i]| &le; |nums[i+1]| for every i"],
    hints=["Look at the negative values only. In which order do they appear compared to the order they must have in the answer?",
           "The negatives appear with growing magnitude, e.g. <code>-1, -2, -4</code>, but the sorted answer needs <code>-4, -2, -1</code>: they are in exactly the reverse order. The non-negative values are already in the right order.",
           "Walk the list; whenever a node has a negative value, unlink it and put it in front of the current head. Moving each negative to the front reverses the negatives while the non-negatives keep their relative order."],
    editorial=["Split the list mentally into two subsequences. The non-negative values appear in increasing order because their absolute value equals their value. The negative values appear with increasing magnitude, which means decreasing value, so they are in exactly the reverse of the order they need.",
               "So one pass is enough: keep a <code>prev</code> pointer, and for each node whose value is negative unlink it and insert it before the current head (it becomes the new head). Moving every negative to the front reverses their order and leaves the non-negatives in place. This is O(n) time and O(1) extra space.",
               "Equal absolute values need no special care: a run like <code>3, -3, 3</code> turns into <code>-3, 3, 3</code> because the negative is pulled to the front while the others keep their order."],
    time="O(n)", space="O(1)",
    solution=NODE + '''def sortAbsoluteOrdered(nums):
    head = build(nums)
    if head is None:
        return []
    prev = head
    cur = head.next
    while cur:
        if cur.val < 0:
            prev.next = cur.next
            cur.next = head
            head = cur
            cur = prev.next
        else:
            prev = cur
            cur = cur.next
    return dump(head)
''',
    tests=[[[0, 1, -2, 3, -4]], [[-1, -2, -3]], [[1, 2, 3]], [[]], [[-5]], [[3, -3, 3, -3]], [[0, 0, 0]],
           [[1, -1, 2, -2, 2, -2]], [[-1, 1, -1]], [[INT_MAX, -INT_MAX]], [[INT_MIN + 1, INT_MAX, INT_MIN]]],
)


def _abs_sorted(r, n, lo, hi):
    a = [r.randint(lo, hi) for _ in range(n)]
    r.shuffle(a)
    a.sort(key=abs)
    return a


_r = rnd(7302)
p["tests"].append([_abs_sorted(_r, 5000, -10 ** 4, 10 ** 4)])
p["tests"].append([_abs_sorted(_r, 4000, -3, 3)])
p["tests"].append([[-i for i in range(1, 3001)]])


def b_abs_sort(nums):
    return sorted(nums)


def g_abs_sort(r):
    return [_abs_sorted(r, r.randint(0, 10), -7, 7)]


def v_abs_sort(tests):
    for t in tests:
        a = t["args"][0]
        assert len(a) <= 5000
        assert all(abs(a[i]) <= abs(a[i + 1]) for i in range(len(a) - 1))
        assert all(abs(x) <= 10 ** 9 for x in a)


CHECKS["sort-list-sorted-by-absolute-value"] = (b_abs_sort, g_abs_sort, "exact")
VALIDATE["sort-list-sorted-by-absolute-value"] = v_abs_sort

p = add(
    id="swap-kth-nodes-from-both-ends", title="Swap the Kth Node From Each End", diff="Easy", topic=TOPIC, tier="extra",
    fn="swapKthNodes", params=[("nums", "int[]"), ("k", "int")], ret="int[]", cmp="exact",
    desc=ENC + "<p>Exchange the <code>k</code>-th node from the beginning with the <code>k</code>-th node from the end (both counted from 1). If both refer to the same node, the list does not change. Return the resulting values from head to tail.</p><p>For example <code>nums = [1,2,3,4,5]</code> with <code>k = 2</code> swaps the nodes holding <code>2</code> and <code>4</code> and gives <code>[1,4,3,2,5]</code>. Try to find both nodes in a single pass without first computing the length.</p>",
    constraints=["1 &le; nums.length &le; 4,000", "1 &le; k &le; nums.length", "-10<sup>9</sup> &le; nums[i] &le; 10<sup>9</sup>"],
    hints=["The k-th node from the end is the node at index <code>n - k</code> (0-based), so you could count the length first. A single pass is possible with two pointers.",
           "Walk a pointer <code>first</code> to the k-th node from the start. Now there are exactly <code>n - k</code> nodes after it.",
           "Start a second pointer <code>second</code> at the head and advance a third pointer from <code>first</code> to the tail while moving <code>second</code> alongside. When the walker reaches the last node, <code>second</code> sits on the k-th node from the end. Swap the two nodes' contents."],
    editorial=["After reaching the k-th node from the start (call it <code>first</code>), there are exactly <code>n - k</code> nodes behind it. A walker that starts at <code>first</code> and runs to the tail makes <code>n - k</code> steps, so a second pointer that starts at the head and moves in lockstep ends on index <code>n - k</code>, which is the k-th node from the end.",
               "Swapping the two nodes is equivalent to swapping their stored values for the purpose of the output, and the pass is O(n) time with O(1) extra space. When <code>k</code> is the middle of an odd-length list both pointers coincide and nothing changes."],
    time="O(n)", space="O(1)",
    solution=NODE + '''def swapKthNodes(nums, k):
    head = build(nums)
    first = head
    for _ in range(k - 1):
        first = first.next
    second = head
    walker = first
    while walker.next:
        walker = walker.next
        second = second.next
    first.val, second.val = second.val, first.val
    return dump(head)
''',
    tests=[[[1, 2, 3, 4, 5], 2], [[1, 2, 3, 4, 5], 1], [[1, 2, 3, 4, 5], 5], [[1, 2, 3, 4, 5], 3], [[9], 1],
           [[1, 2], 1], [[1, 2], 2], [[4, 4, 4, 4], 2], [[INT_MIN, 0, INT_MAX], 1], [[10, 20, 30, 40, 50, 60], 3],
           [[10, 20, 30, 40, 50, 60], 4]],
)
_r = rnd(7303)
_a = _rl(_r, 4000)
p["tests"].append([_a, 1777])
p["tests"].append([_a, 4000])


def b_swap_kth(nums, k):
    out = list(nums)
    n = len(out)
    out[k - 1], out[n - k] = out[n - k], out[k - 1]
    return out


def g_swap_kth(r):
    a = gen_arr(r, -9, 9, 1, 10)
    return [a, r.randint(1, len(a))]


def v_swap_kth(tests):
    for t in tests:
        a, k = t["args"]
        assert 1 <= len(a) <= 4000 and 1 <= k <= len(a)


CHECKS["swap-kth-nodes-from-both-ends"] = (b_swap_kth, g_swap_kth, "exact")
VALIDATE["swap-kth-nodes-from-both-ends"] = v_swap_kth

# ================================================================ MEDIUM

p = add(
    id="odd-even-linked-list", title="Odd Even Linked List", diff="Medium", topic=TOPIC, tier="common",
    fn="oddEvenList", params=[("nums", "int[]")], ret="int[]", cmp="exact",
    desc=ENC + "<p>Group the nodes by the parity of their <em>position</em> (not their value). Positions are counted from 1: the 1st, 3rd, 5th, ... nodes are the odd-position nodes and the 2nd, 4th, ... nodes are the even-position nodes. Rearrange the list so that all odd-position nodes come first, followed by all even-position nodes, and inside each group the original relative order is kept. Return the values of the new list.</p><p>For example <code>[1,2,3,4,5]</code> becomes <code>[1,3,5,2,4]</code> and <code>[2,1,3,5,6,4,7]</code> becomes <code>[2,3,6,7,1,5,4]</code>. Aim for O(1) extra space by relinking the existing nodes.</p>",
    constraints=["0 &le; nums.length &le; 4,000", "-10<sup>9</sup> &le; nums[i] &le; 10<sup>9</sup>"],
    hints=["Imagine two separate lists being built while you walk: one for odd positions and one for even positions.",
           "Keep <code>odd</code> and <code>even</code> pointers, plus the head of the even list (<code>evenHead = head.next</code>) so you can find it again at the end.",
           "In each round do <code>odd.next = even.next; odd = odd.next</code> and then <code>even.next = odd.next; even = even.next</code>, as long as <code>even</code> and <code>even.next</code> exist. Finally attach <code>odd.next = evenHead</code>."],
    editorial=["Because every odd-position node is followed by an even-position node and vice versa, you can unzip the list in place. <code>odd</code> starts at the head and <code>even</code> at the second node; the first node of the even chain is saved in <code>evenHead</code>. Repeatedly let the odd pointer jump over the even node to the next odd node, then let the even pointer jump over that odd node to the next even node.",
               "When the loop ends, <code>odd</code> is the last odd-position node; link it to <code>evenHead</code>. The even chain already ends with null. The work is one pass, O(n) time and O(1) space. Remember it is the position that matters; sorting by value parity is a different problem."],
    time="O(n)", space="O(1)",
    solution=NODE + '''def oddEvenList(nums):
    head = build(nums)
    if head is None or head.next is None:
        return dump(head)
    odd = head
    even = head.next
    even_head = even
    while even and even.next:
        odd.next = even.next
        odd = odd.next
        even.next = odd.next
        even = even.next
    odd.next = even_head
    return dump(head)
''',
    tests=[[[1, 2, 3, 4, 5]], [[2, 1, 3, 5, 6, 4, 7]], [[]], [[1]], [[1, 2]], [[1, 2, 3]], [[1, 2, 3, 4]],
           [[5, 5, 5, 5]], [[INT_MIN, INT_MAX, 0, -1, 1, 2]], [[9, 8, 7, 6, 5, 4, 3, 2, 1, 0]]],
)
_r = rnd(7304)
p["tests"].append([_rl(_r, 4000)])
p["tests"].append([_rl(_r, 3999)])
p["tests"].append([list(range(1, 2001))])


def b_odd_even(nums):
    return [x for i, x in enumerate(nums) if i % 2 == 0] + [x for i, x in enumerate(nums) if i % 2 == 1]


def v_odd_even(tests):
    for t in tests:
        assert len(t["args"][0]) <= 4000
        assert sorted(t["expected"]) == sorted(t["args"][0])


CHECKS["odd-even-linked-list"] = (b_odd_even, lambda r: [gen_arr(r, -9, 9, 0, 12)], "exact")
VALIDATE["odd-even-linked-list"] = v_odd_even

p = add(
    id="rotate-linked-list-right", title="Rotate Linked List to the Right", diff="Medium", topic=TOPIC, tier="common",
    fn="rotateRight", params=[("nums", "int[]"), ("k", "int")], ret="int[]", cmp="exact",
    desc=ENC + "<p>Rotate the list to the right by <code>k</code> places: one rotation step moves the last node to the front. Return the values after <code>k</code> steps.</p><p>For example <code>[1,2,3,4,5]</code> with <code>k = 2</code> gives <code>[4,5,1,2,3]</code>. Note that <code>k</code> can be far larger than the length of the list, so doing the steps one by one is too slow.</p>",
    constraints=["0 &le; nums.length &le; 5,000", "0 &le; k &le; 10<sup>9</sup>", "-10<sup>9</sup> &le; nums[i] &le; 10<sup>9</sup>"],
    hints=["After <code>n</code> rotations (n = length) the list is back to the start, so only <code>k mod n</code> matters. Watch out for the empty list.",
           "Rotating right by <code>r</code> means the last <code>r</code> nodes move to the front. Which node becomes the new tail?",
           "Find the length and the tail node, make the list circular by linking tail to head, then walk <code>n - r</code> steps from the head. The node you stop on is the new tail; its successor is the new head. Cut the circle there."],
    editorial=["Compute the length <code>n</code> in one pass while remembering the tail. Reduce <code>k</code> to <code>r = k mod n</code>; when <code>r</code> is 0 (or the list is empty) nothing changes. Otherwise the new tail is the node at index <code>n - r - 1</code> (0-based) and the new head is the node right after it.",
               "Link the old tail to the old head to close the ring, advance <code>n - r - 1</code> steps from the head to the new tail, take its <code>next</code> as the new head and set its <code>next</code> to null. The total work is O(n) and O(1) extra space, independent of how large <code>k</code> is."],
    time="O(n)", space="O(1)",
    solution=NODE + '''def rotateRight(nums, k):
    head = build(nums)
    if head is None:
        return []
    n = 1
    tail = head
    while tail.next:
        tail = tail.next
        n += 1
    r = k % n
    if r == 0:
        return dump(head)
    tail.next = head
    new_tail = head
    for _ in range(n - r - 1):
        new_tail = new_tail.next
    new_head = new_tail.next
    new_tail.next = None
    return dump(new_head)
''',
    tests=[[[1, 2, 3, 4, 5], 2], [[0, 1, 2], 4], [[], 5], [[7], 1000000000], [[1, 2], 0], [[1, 2], 1], [[1, 2], 2],
           [[1, 2, 3, 4, 5], 5], [[1, 2, 3, 4, 5], 10], [[1, 2, 3, 4, 5], 11], [[INT_MIN, 0, INT_MAX], 1]],
)
_r = rnd(7305)
p["tests"].append([_rl(_r, 5000), 999999999])
p["tests"].append([_rl(_r, 4999), 2500])
p["tests"].append([list(range(3000)), 1000000000])


def b_rotate(nums, k):
    out = list(nums)
    for _ in range(k):
        if out:
            out.insert(0, out.pop())
    return out


def g_rotate(r):
    return [gen_arr(r, -9, 9, 0, 8), r.randint(0, 30)]


def v_rotate(tests):
    for t in tests:
        a, k = t["args"]
        assert len(a) <= 5000 and 0 <= k <= 10 ** 9


CHECKS["rotate-linked-list-right"] = (b_rotate, g_rotate, "exact")
VALIDATE["rotate-linked-list-right"] = v_rotate

p = add(
    id="sort-linked-list", title="Sort a Linked List", diff="Medium", topic=TOPIC, tier="must",
    fn="sortList", params=[("nums", "int[]")], ret="int[]", cmp="exact",
    desc=ENC + "<p>Sort the list in non-decreasing order and return the sorted values.</p><p>The point of the exercise is to do it the way a linked list wants to be sorted: in O(n log n) time without copying the values into an array. A list cannot be indexed, so quicksort and heapsort are awkward, but <em>merge sort</em> fits perfectly.</p>",
    constraints=["0 &le; nums.length &le; 8,000", "-10<sup>9</sup> &le; nums[i] &le; 10<sup>9</sup>"],
    hints=["Which O(n log n) sort only needs sequential access and can merge two sorted sequences by relinking nodes?",
           "Split the list into two halves with slow and fast pointers (cut the link after the slow pointer), sort each half recursively, and merge them.",
           "Merging two sorted lists uses a dummy head and a tail pointer: repeatedly append the smaller front node. The recursion stops for lists with 0 or 1 nodes. The recursion depth is only O(log n)."],
    editorial=["Top-down merge sort: if the list has fewer than two nodes it is sorted. Otherwise find the middle with a slow pointer and a fast pointer moving twice as fast, cut the list after the middle, sort both halves recursively and merge them with the standard two-pointer merge on nodes.",
               "There are log n levels of recursion and each level touches every node once, which gives O(n log n) time. The recursion stack has depth O(log n); a bottom-up version (merge runs of size 1, 2, 4, ...) gets the extra space down to O(1). Converting to an array, sorting, and rebuilding is simpler but misses the point of the exercise."],
    time="O(n log n)", space="O(log n)",
    solution=NODE + '''def merge(a, b):
    dummy = ListNode()
    tail = dummy
    while a and b:
        if b.val < a.val:
            tail.next = b
            b = b.next
        else:
            tail.next = a
            a = a.next
        tail = tail.next
    tail.next = a if a else b
    return dummy.next


def sort_nodes(head):
    if head is None or head.next is None:
        return head
    slow = head
    fast = head.next
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
    second = slow.next
    slow.next = None
    return merge(sort_nodes(head), sort_nodes(second))


def sortList(nums):
    return dump(sort_nodes(build(nums)))
''',
    tests=[[[4, 2, 1, 3]], [[-1, 5, 3, 4, 0]], [[]], [[1]], [[2, 1]], [[1, 2, 3]], [[3, 2, 1]], [[5, 5, 5, 5]],
           [[INT_MAX, INT_MIN, 0]], [[2, 1, 2, 1, 2, 1, 2]]],
)
_r = rnd(7306)
p["tests"].append([_rl(_r, 5000)])
p["tests"].append([list(range(3000, 0, -1))])
p["tests"].append([[_r.randint(0, 2) for _ in range(4000)]])


def b_sort_list(nums):
    out = list(nums)
    for i in range(1, len(out)):
        j = i
        while j > 0 and out[j - 1] > out[j]:
            out[j - 1], out[j] = out[j], out[j - 1]
            j -= 1
    return out


def v_sort_list(tests):
    for t in tests:
        assert len(t["args"][0]) <= 8000
        assert t["expected"] == sorted(t["args"][0])


CHECKS["sort-linked-list"] = (b_sort_list, lambda r: [gen_arr(r, -9, 9, 0, 12)], "exact")
VALIDATE["sort-linked-list"] = v_sort_list

p = add(
    id="split-linked-list-in-parts", title="Split Linked List in Parts", diff="Medium", topic=TOPIC, tier="extra",
    fn="splitListToParts", params=[("nums", "int[]"), ("k", "int")], ret="int[][]", cmp="exact",
    desc=ENC + "<p>Cut the list into exactly <code>k</code> consecutive parts, in the original order, so that the sizes of any two parts differ by at most 1 and the parts that come earlier are never smaller than the parts that come later. When the list has fewer than <code>k</code> nodes, the last parts are empty.</p><p>Return the parts as an array of <code>k</code> arrays, each holding the values of one part from head to tail (an empty part is <code>[]</code>). For example, <code>[1,2,3]</code> with <code>k = 5</code> gives <code>[[1],[2],[3],[],[]]</code> and ten nodes with <code>k = 3</code> give sizes <code>4, 3, 3</code>.</p>",
    constraints=["0 &le; nums.length &le; 5,000", "1 &le; k &le; 1,000", "-10<sup>9</sup> &le; nums[i] &le; 10<sup>9</sup>"],
    hints=["First decide how large each part must be. With <code>n</code> nodes and <code>k</code> parts, every part gets at least <code>n // k</code> nodes.",
           "The <code>n mod k</code> leftover nodes go one each to the first <code>n mod k</code> parts, so those parts have <code>n // k + 1</code> nodes.",
           "Count the length, then walk the list once: for part <code>i</code> take <code>n // k + (1 if i &lt; n % k else 0)</code> nodes, detach them by setting the <code>next</code> of the last taken node to null, and continue from the following node. Parts beyond the end of the list stay empty."],
    editorial=["The size rule is forced: the sizes must be as equal as possible and non-increasing, so the first <code>n mod k</code> parts have <code>n // k + 1</code> nodes and the remaining parts have <code>n // k</code>.",
               "First count the nodes. Then for each part walk <code>size - 1</code> steps from the part's first node to its last node, remember the node after it, cut the link, and start the next part there. Each node is visited a constant number of times, so the time is O(n + k); apart from the output, no extra space is needed."],
    time="O(n + k)", space="O(1)",
    solution=NODE + '''def splitListToParts(nums, k):
    head = build(nums)
    n = 0
    cur = head
    while cur:
        n += 1
        cur = cur.next
    base, extra = divmod(n, k)
    parts = []
    cur = head
    for i in range(k):
        size = base + (1 if i < extra else 0)
        part_head = cur
        for _ in range(size - 1):
            cur = cur.next
        if size > 0:
            nxt = cur.next
            cur.next = None
            cur = nxt
        parts.append(dump(part_head))
    return parts
''',
    tests=[[[1, 2, 3], 5], [[1, 2, 3, 4, 5, 6, 7, 8, 9, 10], 3], [[], 3], [[7], 1], [[7], 2], [[1, 2, 3, 4], 4],
           [[1, 2, 3, 4], 1], [[1, 2, 3, 4, 5], 2], [[1, 2, 3, 4, 5, 6, 7], 4], [[INT_MIN, INT_MAX], 2]],
)
_r = rnd(7307)
p["tests"].append([_rl(_r, 5000), 7])
p["tests"].append([_rl(_r, 4000), 1000])
p["tests"].append([_rl(_r, 900), 1000])


def b_split(nums, k):
    sizes = [0] * k
    for i in range(len(nums)):
        sizes[i % k] += 1
    out = []
    pos = 0
    for s in sizes:
        out.append(nums[pos:pos + s])
        pos += s
    return out


def g_split(r):
    return [gen_arr(r, -9, 9, 0, 12), r.randint(1, 7)]


def v_split(tests):
    for t in tests:
        a, k = t["args"]
        assert len(a) <= 5000 and 1 <= k <= 1000
        assert len(t["expected"]) == k
        assert [x for part in t["expected"] for x in part] == a


CHECKS["split-linked-list-in-parts"] = (b_split, g_split, "exact")
VALIDATE["split-linked-list-in-parts"] = v_split

p = add(
    id="sort-k-sorted-linked-list", title="Sort a Nearly Sorted Linked List", diff="Medium", topic=TOPIC, tier="extra",
    fn="sortNearlySorted", params=[("nums", "int[]"), ("k", "int")], ret="int[]", cmp="exact",
    desc=ENC + "<p>The list is <em>k-sorted</em>: for every pair of positions <code>i &lt; j</code> with <code>j - i &gt; k</code> we have <code>nums[i] &le; nums[j]</code>. In other words, any two nodes that are out of order are at most <code>k</code> positions apart. Return the list sorted in non-decreasing order.</p><p>For example, <code>[2,1,4,3,6,5]</code> with <code>k = 1</code> is k-sorted and the answer is <code>[1,2,3,4,5,6]</code>. A plain sort costs O(n log n); use the extra information to get O(n log k).</p>",
    constraints=["0 &le; nums.length &le; 8,000", "0 &le; k &le; 8,000", "-10<sup>9</sup> &le; nums[i] &le; 10<sup>9</sup>", "The list is k-sorted as defined above"],
    hints=["Where can the smallest value of the whole list be? Use the k-sorted condition to limit the candidates for the first position of the answer.",
           "The smallest value must be among the first <code>k + 1</code> nodes. After you output it, the next smallest is among the first <code>k + 1</code> remaining nodes, and so on.",
           "Keep a min-heap holding a sliding window of <code>k + 1</code> nodes: pop the smallest and append it to the result, then push the next unread node. When the input runs out, pop the heap until it is empty."],
    editorial=["If a node at index <code>j &gt; k</code> were smaller than the first node, the pair (0, j) would violate the condition, so the overall minimum is among the first <code>k + 1</code> nodes. Removing it keeps the remaining list k-sorted (distances between the remaining nodes only shrink), so the same argument applies again.",
               "Implement this with a min-heap of at most <code>k + 1</code> elements. Push the first <code>k + 1</code> nodes, then for every further node do a push-and-pop of the minimum and append that minimum to the output; at the end drain the heap. Each operation costs O(log k), giving O(n log k) time and O(k) space. With <code>k = 0</code> the list is already sorted."],
    time="O(n log k)", space="O(k)",
    solution=NODE + '''import heapq


def sortNearlySorted(nums, k):
    cur = build(nums)
    dummy = ListNode()
    tail = dummy
    heap = []
    uid = 0
    while cur:
        heapq.heappush(heap, (cur.val, uid, cur))
        uid += 1
        cur = cur.next
        if len(heap) > k:
            node = heapq.heappop(heap)[2]
            tail.next = node
            tail = node
    while heap:
        node = heapq.heappop(heap)[2]
        tail.next = node
        tail = node
    tail.next = None
    return dump(dummy.next)
''',
    tests=[[[2, 1, 4, 3, 6, 5], 1], [[], 0], [[5], 0], [[1, 2, 3], 0], [[3, 2, 1], 2], [[2, 1, 2, 1], 3],
           [[6, 5, 4, 3, 2, 1], 5], [[1, 3, 2, 5, 4, 7, 6], 1], [[4, 5, 6, 1, 2, 3], 5], [[2, 3, 1, 5, 6, 4, 8, 9, 7], 2],
           [[INT_MAX, INT_MIN], 1]],
)


def _k_sorted(r, n, k, lo, hi):
    a = sorted(r.randint(lo, hi) for _ in range(n))
    out = []
    for s in range(0, n, k + 1):
        blk = a[s:s + k + 1]
        r.shuffle(blk)
        out += blk
    return out


_r = rnd(7308)
p["tests"].append([_k_sorted(_r, 5000, 40, -10 ** 4, 10 ** 4), 40])
p["tests"].append([_k_sorted(_r, 4000, 1, -50, 50), 1])
p["tests"].append([_k_sorted(_r, 3000, 2999, -10 ** 4, 10 ** 4), 2999])


def b_nearly(nums, k):
    out = list(nums)
    for i in range(1, len(out)):
        j = i
        while j > 0 and out[j - 1] > out[j]:
            out[j - 1], out[j] = out[j], out[j - 1]
            j -= 1
    return out


def _min_k(a):
    d = 0
    for i in range(len(a)):
        for j in range(i + 1, len(a)):
            if a[i] > a[j]:
                d = max(d, j - i)
    return d


def g_nearly(r):
    a = gen_arr(r, -5, 5, 0, 11)
    return [a, _min_k(a) + r.randint(0, 2)]


def v_nearly(tests):
    for t in tests:
        a, k = t["args"]
        assert len(a) <= 8000 and 0 <= k <= 8000
        assert t["expected"] == sorted(a)
        if len(a) <= 600:
            assert _min_k(a) <= k
        else:
            # every inversion must lie inside a block of k+1 consecutive positions, checked via block maxima/minima
            n = len(a)
            pref_max = []
            m = -(10 ** 18)
            for x in a:
                m = max(m, x)
                pref_max.append(m)
            suf_min = [0] * n
            m = 10 ** 18
            for i in range(n - 1, -1, -1):
                m = min(m, a[i])
                suf_min[i] = m
            for i in range(n - k - 1):
                assert pref_max[i] <= suf_min[i + k + 1], ("not k-sorted", i)


CHECKS["sort-k-sorted-linked-list"] = (b_nearly, g_nearly, "exact")
VALIDATE["sort-k-sorted-linked-list"] = v_nearly

p = add(
    id="rotate-list-segments", title="Rotate Segments of a Linked List", diff="Medium", topic=TOPIC, tier="extra",
    fn="rotateSegments", params=[("nums", "int[]"), ("ops", "int[][]")], ret="int[]", cmp="exact",
    desc=ENC + "<p>You are given a list of operations, each written as <code>[l, r, k]</code>. An operation takes the sublist made of the nodes at 0-based positions <code>l</code> through <code>r</code> (inclusive) and rotates <em>only that sublist</em> to the right by <code>k</code> places: one step moves the last node of the sublist to the front of the sublist. Nodes outside the range do not move.</p><p>Apply the operations in the given order and return the final values. For example <code>nums = [1,2,3,4,5]</code> with <code>ops = [[1,3,1],[0,4,2]]</code> first gives <code>[1,4,2,3,5]</code> (the sublist <code>2,3,4</code> becomes <code>4,2,3</code>) and then <code>[3,5,1,4,2]</code>.</p>",
    constraints=["0 &le; nums.length &le; 3,000", "0 &le; ops.length &le; 2,000", "0 &le; l &le; r &lt; nums.length for every operation", "0 &le; k &le; 10<sup>9</sup>", "-10<sup>9</sup> &le; nums[i] &le; 10<sup>9</sup>"],
    hints=["A single operation is the 'rotate list' problem on a sublist, and <code>k</code> can be huge, so reduce it first.",
           "For a sublist of length <code>m = r - l + 1</code> only <code>k mod m</code> matters. If it is 0, skip the operation.",
           "Cut the sublist out (keep the node before <code>l</code> and the node after <code>r</code>), rotate it by relinking its tail to its head and breaking the ring <code>m - k mod m</code> steps in, and splice it back between the two kept neighbours."],
    editorial=["Each operation is independent of the others in structure, so process them one after another. For an operation reduce <code>k</code> modulo the sublist length <code>m</code>; when the result is 0 nothing changes.",
               "Otherwise the last <code>s = k mod m</code> nodes of the sublist become its first <code>s</code> nodes. With real pointers: find the node before position <code>l</code> and the node at position <code>r</code>, find the node at offset <code>m - s - 1</code> inside the sublist (the new tail of the sublist), and re-hook three links: the old sublist tail to the old sublist head, the new sublist tail to the node after <code>r</code>, and the node before <code>l</code> to the new sublist head. One operation costs O(r) to walk to the segment, so the total is O(q &middot; n) time with O(1) extra space; with 2,000 operations on 3,000 nodes this is fast."],
    time="O(q * n)", space="O(1)",
    solution=NODE + '''def rotateSegments(nums, ops):
    dummy = ListNode(0, build(nums))
    for l, r, k in ops:
        m = r - l + 1
        s = k % m
        if s == 0:
            continue
        before = dummy
        for _ in range(l):
            before = before.next
        seg_head = before.next
        seg_tail = seg_head
        for _ in range(m - 1):
            seg_tail = seg_tail.next
        after = seg_tail.next
        new_tail = seg_head
        for _ in range(m - s - 1):
            new_tail = new_tail.next
        new_head = new_tail.next
        seg_tail.next = seg_head
        new_tail.next = after
        before.next = new_head
    return dump(dummy.next)
''',
    tests=[[[1, 2, 3, 4, 5], [[1, 3, 1], [0, 4, 2]]], [[1, 2, 3, 4, 5], []], [[], []], [[9], [[0, 0, 5]]],
           [[1, 2, 3, 4], [[0, 3, 4]]], [[1, 2, 3, 4], [[0, 1, 1]]], [[1, 2, 3, 4, 5, 6], [[2, 5, 1000000000]]],
           [[1, 2, 3, 4, 5, 6], [[0, 2, 1], [3, 5, 1], [1, 4, 3]]], [[1, 2, 3, 4, 5, 6], [[0, 5, 1], [0, 5, 5]]],
           [[INT_MIN, 0, INT_MAX], [[0, 2, 1], [1, 2, 1]]]],
)


def _ops(r, n, q, maxk):
    ops = []
    for _ in range(q):
        l = r.randint(0, n - 1)
        rr = r.randint(l, n - 1)
        ops.append([l, rr, r.randint(0, maxk)])
    return ops


_r = rnd(7309)
p["tests"].append([_rl(_r, 3000), _ops(_r, 3000, 2000, 10 ** 9)])
p["tests"].append([_rl(_r, 2500), [[0, 2499, _r.randint(0, 100)] for _ in range(1500)]])
p["tests"].append([list(range(1000)), _ops(_r, 1000, 1000, 5)])


def b_rot_seg(nums, ops):
    a = list(nums)
    for l, r, k in ops:
        for _ in range(k):
            a[l:r + 1] = [a[r]] + a[l:r]
    return a


def g_rot_seg(r):
    n = r.randint(1, 8)
    return [gen_arr(r, -9, 9, n, n), _ops(r, n, r.randint(0, 5), 12)]


def v_rot_seg(tests):
    for t in tests:
        a, ops = t["args"]
        assert len(a) <= 3000 and len(ops) <= 2000
        for l, rr, k in ops:
            assert 0 <= l <= rr < len(a) and 0 <= k <= 10 ** 9
        assert sorted(t["expected"]) == sorted(a)


CHECKS["rotate-list-segments"] = (b_rot_seg, g_rot_seg, "exact")
VALIDATE["rotate-list-segments"] = v_rot_seg

# ================================================================ HARD

p = add(
    id="min-moves-to-sort-list-front-or-back", title="Fewest Moves to Sort a List", diff="Hard", topic=TOPIC, tier="extra",
    fn="minMovesToSort", params=[("nums", "int[]")], ret="int", cmp="exact",
    desc=ENC + "<p>All values in the list are distinct. In one move you may detach any single node and re-attach it either at the very front (as the new head) or at the very back (as the new tail). Return the minimum number of moves needed to make the list sorted in increasing order.</p><p>Example: <code>[2,3,4,1]</code> needs 1 move (send <code>1</code> to the front). <code>[3,1,2,4]</code> needs 2 moves (send <code>3</code> to the back, then <code>4</code> to the back).</p>",
    constraints=["0 &le; nums.length &le; 4,000", "-10<sup>9</sup> &le; nums[i] &le; 10<sup>9</sup>", "All values are distinct"],
    hints=["Moving each node at most once is always enough. So ask the opposite question: which nodes can you afford to leave untouched?",
           "The untouched nodes keep their relative order, and every moved node ends up at one of the two ends. So the untouched nodes must already appear in increasing order, and nothing that is moved may belong between two untouched values.",
           "That means the untouched values are consecutive values of the sorted order (ranks <code>r, r+1, ..., r+L-1</code>) and in the list they appear left to right in that order. Maximise <code>L</code>; the answer is <code>n - L</code>. Compute each value's position and its rank, then scan the ranks once keeping a running chain length."],
    editorial=["Let <code>rank(x)</code> be the position of <code>x</code> in sorted order and <code>pos(x)</code> its index in the list. Suppose some set <code>U</code> of nodes is never moved. Every other node is moved once to the front or to the back, so in the final list the nodes smaller than all of <code>U</code> can be placed in front and the larger ones behind, but a moved node whose value lies between two untouched values would have to sit between them, which is impossible because it is only ever placed at an end. Hence <code>U</code> must be a block of consecutive ranks, and for the final list to be sorted its members must already be in increasing order of position.",
               "Conversely any such block can be kept: send the smaller values to the front and the larger values to the back in the right order (smaller ones from the largest to the smallest to the front, larger ones from the smallest to the largest to the back). So the answer is <code>n - L</code> where <code>L</code> is the longest run of consecutive ranks with <code>pos(rank r) &lt; pos(rank r+1) &lt; ...</code>.",
               "Sort once to get the ranks (O(n log n)), then a single scan computes the longest such run in O(n). The extra space is O(n) for the position table."],
    time="O(n log n)", space="O(n)",
    solution=NODE + '''def minMovesToSort(nums):
    head = build(nums)
    n = 0
    pos = {}
    cur = head
    while cur:
        pos[cur.val] = n
        n += 1
        cur = cur.next
    if n == 0:
        return 0
    order = sorted(pos)
    best = run = 1
    for i in range(1, n):
        if pos[order[i]] > pos[order[i - 1]]:
            run += 1
        else:
            run = 1
        best = max(best, run)
    return n - best
''',
    tests=[[[2, 3, 4, 1]], [[3, 1, 2, 4]], [[]], [[5]], [[1, 2, 3, 4, 5]], [[5, 4, 3, 2, 1]], [[2, 1]], [[1, 3, 2]],
           [[4, 1, 3, 2]], [[INT_MIN, INT_MAX, 0]], [[10, 20, 40, 30, 50, 60]]],
)
_r = rnd(7310)


def _moved(r, n, moves):
    a = list(range(n))
    for _ in range(moves):
        x = a.pop(r.randrange(len(a)))
        a.insert(r.randrange(len(a) + 1), x)
    return a


_vals = sorted(_r.sample(range(-10 ** 5, 10 ** 5), 4000))
p["tests"].append([[_vals[i] for i in _moved(_r, 4000, 400)]])
_perm = list(range(4000)); _r.shuffle(_perm)
p["tests"].append([[_vals[i] for i in _perm]])
p["tests"].append([_vals[2000:] + _vals[:2000]])


def b_front_back(nums):
    n = len(nums)
    if n <= 1:
        return 0
    order = sorted(nums)
    rank = {v: i for i, v in enumerate(order)}
    start = tuple(rank[v] for v in nums)
    target = tuple(range(n))
    seen = {start}
    frontier = [start]
    d = 0
    while frontier:
        if target in seen:
            return d
        nxt = []
        for s in frontier:
            for i in range(n):
                rest = s[:i] + s[i + 1:]
                for t in ((s[i],) + rest, rest + (s[i],)):
                    if t not in seen:
                        seen.add(t)
                        nxt.append(t)
        frontier = nxt
        d += 1
    return d


def g_front_back(r):
    n = r.randint(0, 6)
    return [r.sample(range(-20, 20), n)]


def v_front_back(tests):
    for t in tests:
        a = t["args"][0]
        assert len(a) <= 4000 and len(set(a)) == len(a)
        assert 0 <= t["expected"] <= len(a)


CHECKS["min-moves-to-sort-list-front-or-back"] = (b_front_back, g_front_back, "exact")
VALIDATE["min-moves-to-sort-list-front-or-back"] = v_front_back

p = add(
    id="adjacent-node-swaps-to-sort-list", title="Adjacent Node Swaps to Sort a List", diff="Hard", topic=TOPIC, tier="extra",
    fn="minAdjacentSwaps", params=[("nums", "int[]")], ret="int", cmp="exact",
    desc=ENC + "<p>In one step you may swap two neighbouring nodes of the list. Return the minimum number of steps needed to arrange the list in non-decreasing order. Equal values never have to be swapped with each other.</p><p>For example <code>[3,1,2]</code> needs 2 steps and <code>[2,2,1]</code> needs 2 steps. The list can hold thousands of nodes, so simulating bubble sort is too slow.</p>",
    constraints=["0 &le; nums.length &le; 4,000", "-10<sup>9</sup> &le; nums[i] &le; 10<sup>9</sup>"],
    hints=["Each adjacent swap can fix at most one pair of nodes that are in the wrong relative order. Count what must be fixed.",
           "The answer is the number of <em>inversions</em>: pairs of positions <code>i &lt; j</code> with <code>nums[i] &gt; nums[j]</code> (strictly greater, because equal values are never swapped).",
           "Count inversions in O(n log n): either during a merge sort (when you take an element from the right half before the remaining left-half elements, add the number of remaining left elements), or with a Fenwick tree over compressed values while scanning left to right."],
    editorial=["An adjacent swap changes the relative order of exactly one pair of nodes, so it reduces the number of inversions by at most one, and a sorted list has none. Hence at least <code>inv</code> swaps are needed. Bubble sort shows it is enough: whenever the list is unsorted there is an adjacent inverted pair, and swapping it lowers the inversion count by exactly one.",
               "So the answer is the inversion count. Counting with merge sort: when merging two sorted halves, every time the next element comes from the right half, it is smaller than all elements still waiting in the left half, so add that many to the total. This costs O(n log n). The result fits in 32 bits since it is at most n(n-1)/2, about 8 million for n = 4,000.",
               "A Fenwick tree works as well: compress the values to ranks, scan left to right, and for each element add the count of earlier elements with a strictly larger rank."],
    time="O(n log n)", space="O(n)",
    solution=NODE + '''def minAdjacentSwaps(nums):
    head = build(nums)
    vals = []
    cur = head
    while cur:
        vals.append(cur.val)
        cur = cur.next
    n = len(vals)
    rank = {v: i + 1 for i, v in enumerate(sorted(set(vals)))}
    m = len(rank)
    tree = [0] * (m + 1)
    inv = 0
    for seen, v in enumerate(vals):
        r = rank[v]
        # earlier elements with rank <= r
        s = 0
        i = r
        while i > 0:
            s += tree[i]
            i -= i & -i
        inv += seen - s
        i = r
        while i <= m:
            tree[i] += 1
            i += i & -i
    return inv
''',
    tests=[[[3, 1, 2]], [[2, 2, 1]], [[]], [[4]], [[1, 2, 3, 4]], [[4, 3, 2, 1]], [[1, 1, 1]], [[2, 1, 2, 1]],
           [[INT_MAX, INT_MIN, 0]], [[5, 1, 4, 2, 3]]],
)
_r = rnd(7311)
p["tests"].append([_rl(_r, 4000, -10 ** 5, 10 ** 5)])
p["tests"].append([list(range(4000, 0, -1))])
p["tests"].append([[_r.randint(0, 3) for _ in range(4000)]])


def b_adj_swaps(nums):
    a = list(nums)
    cnt = 0
    for i in range(len(a)):
        for j in range(i + 1, len(a)):
            if a[i] > a[j]:
                cnt += 1
    return cnt


def v_adj_swaps(tests):
    for t in tests:
        assert len(t["args"][0]) <= 4000
        assert 0 <= t["expected"] <= 4000 * 3999 // 2


CHECKS["adjacent-node-swaps-to-sort-list"] = (b_adj_swaps, lambda r: [gen_arr(r, -4, 4, 0, 12)], "exact")
VALIDATE["adjacent-node-swaps-to-sort-list"] = v_adj_swaps
