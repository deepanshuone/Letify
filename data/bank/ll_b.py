"""Problems: linked lists, pointer techniques (cycles, intersection, k-th from the end, palindromes) with successor-array encodings. See data/lib.py for the registry."""
from itertools import groupby
from math import gcd

from lib import add, rnd, CHECKS, VALIDATE, gen_arr  # noqa: F401

INT_MIN, INT_MAX = -(2 ** 31), 2 ** 31 - 1
TOPIC = "Linked List"

SUCC_ENC = ("<p><strong>Encoding.</strong> A singly linked structure with <code>n</code> nodes is given as a successor array. "
            "The nodes are numbered <code>0..n-1</code> and <code>succ[i]</code> is the number of the node that follows node <code>i</code>, "
            "or <code>-1</code> if node <code>i</code> has no next node. The list starts at node <code>0</code> (its head).</p>")

VAL_ENC = ("<p><strong>Encoding.</strong> A singly linked list with <code>n</code> nodes is given by two arrays. The nodes are numbered "
           "<code>0..n-1</code>; node <code>0</code> is the head, <code>vals[i]</code> is the value stored in node <code>i</code> and "
           "<code>succ[i]</code> is the number of the node after node <code>i</code>, or <code>-1</code> if there is none. "
           "The node numbers say nothing about the order in the list: follow <code>succ</code> to find it.</p>")


# ---------------------------------------------------------------- helpers shared by the tests

def _walk(succ, head=0):
    """Nodes visited from head, each once, in order; plus True if the walk ends by running into a visited node."""
    seen, order, cur = set(), [], head
    while cur != -1 and cur not in seen:
        seen.add(cur)
        order.append(cur)
        cur = succ[cur]
    return order, cur != -1


def _enc(r, seq, back=None):
    """(vals, succ) of a list that holds seq from head to tail. Node 0 is the head, other node numbers are shuffled.
    back: index into seq that the last node links to (a cycle), or None for a normal end."""
    n = len(seq)
    order = [0] + r.sample(range(1, n), n - 1) if n > 1 else [0]
    vals, succ = [0] * n, [-1] * n
    for pos, node in enumerate(order):
        vals[node] = seq[pos]
        if pos + 1 < n:
            succ[node] = order[pos + 1]
        elif back is not None:
            succ[node] = order[back]
    return vals, succ


def _rho(r, n, m, back, decoy_cycle=True):
    """Successor array of n nodes. The nodes reachable from node 0 form a chain of m nodes (head 0, shuffled numbers) whose last
    node links back to chain position `back` (None: the chain simply ends). The remaining n - m nodes are decoys that
    cannot be reached from node 0; they point at each other, and contain a cycle when decoy_cycle is set."""
    order = [0] + r.sample(range(1, n), m - 1) if m > 1 else [0]
    used = set(order)
    rest = [x for x in range(n) if x not in used]
    succ = [-1] * n
    for pos in range(m - 1):
        succ[order[pos]] = order[pos + 1]
    if back is not None:
        succ[order[-1]] = order[back]
    for x in rest:
        succ[x] = r.choice(rest + [-1])
    if decoy_cycle and len(rest) >= 2:
        r.shuffle(rest)
        for i, x in enumerate(rest[:3]):
            succ[x] = rest[(i + 1) % min(3, len(rest))]
    return succ


class _G:
    """Tiny builder for functional graphs; node numbers are shuffled at the end."""

    def __init__(self):
        self.succ = []

    def chain(self, k):
        ids = list(range(len(self.succ), len(self.succ) + k))
        self.succ += [-1] * k
        for x, y in zip(ids, ids[1:]):
            self.succ[x] = y
        return ids

    def link(self, a, b):
        self.succ[a] = b

    def done(self, r, heads):
        n = len(self.succ)
        perm = list(range(n))
        r.shuffle(perm)
        s = [-1] * n
        for i, v in enumerate(self.succ):
            s[perm[i]] = perm[v] if v != -1 else -1
        return [s] + [perm[h] for h in heads]


def _scenario(r, kind, la, lb, ls, lt=0, back=None, x=0, y=0, ring_a=True):
    """Two list heads in one graph.
    tree : tails A and B (la, lb nodes) both lead into a shared chain S (ls nodes); back links S's last node to S[back] (a cycle).
    ring : S is a ring of ls nodes; tail A attaches to S[x], tail B to S[y].
    rho2 : A leads into its own structure S, B into its own structure T (lt nodes); S is a ring when ring_a else a plain chain;
           T is always a ring."""
    g = _G()
    A, B, S, T = g.chain(la), g.chain(lb), g.chain(ls), g.chain(lt)
    if kind == "tree":
        if back is not None:
            g.link(S[-1], S[back])
        if A and S:
            g.link(A[-1], S[0])
        if B and S:
            g.link(B[-1], S[0])
        ha, hb = (A[0] if A else S[0]), (B[0] if B else S[0])
    elif kind == "ring":
        g.link(S[-1], S[0])
        if A:
            g.link(A[-1], S[x])
        if B:
            g.link(B[-1], S[y])
        ha, hb = (A[0] if A else S[x]), (B[0] if B else S[y])
    else:
        if ring_a:
            g.link(S[-1], S[0 if back is None else back])
        g.link(T[-1], T[0])
        if A:
            g.link(A[-1], S[0])
        if B:
            g.link(B[-1], T[0])
        ha, hb = (A[0] if A else S[0]), (B[0] if B else T[0])
    return g.done(r, [ha, hb])


# ================================================================ EASY

p = add(
    id="linked-list-has-cycle", title="Linked List Has a Cycle", diff="Easy", topic=TOPIC, tier="must",
    fn="hasCycle", params=[("succ", "int[]")], ret="bool", cmp="exact",
    desc=SUCC_ENC + "<p>Starting at the head and repeatedly following <code>succ</code>, the walk either reaches a node with <code>succ = -1</code> (the list ends) or never stops because it re-enters a node it has already visited (the list has a cycle). Return <code>true</code> if the list that starts at node <code>0</code> has a cycle and <code>false</code> otherwise.</p>"
         "<p>Nodes that cannot be reached from node <code>0</code> are not part of the list, so a loop among them does not count. For <code>succ = [1,2,3,1]</code> the walk is <code>0, 1, 2, 3, 1, ...</code> and the answer is <code>true</code>; for <code>succ = [1,-1,2]</code> the list is <code>0 -> 1</code>, node 2 points to itself but is unreachable, so the answer is <code>false</code>.</p><p>Try to use O(1) extra memory.</p>",
    constraints=["1 &le; succ.length &le; 6,000", "-1 &le; succ[i] &lt; succ.length", "Some nodes may be unreachable from node 0; they are ignored"],
    hints=["Storing every visited node in a set and stopping when you see a repeat works, but needs O(n) memory.",
           "Imagine two runners on the list: one moves one node per turn, the other two nodes per turn. What happens to the fast one if the list ends? What if it loops?",
           "Move <code>slow</code> by one node and <code>fast</code> by two. If <code>fast</code> (or the node after it) is <code>-1</code>, there is no cycle. If <code>slow == fast</code> at some turn, there is one."],
    editorial=["Use Floyd's tortoise and hare. Both pointers start at the head; each turn <code>slow</code> advances by one node and <code>fast</code> by two. In an acyclic list the fast pointer reaches <code>-1</code> after about n/2 turns and the loop ends with <code>false</code>.",
               "If the list contains a cycle, both pointers eventually enter it. From then on the distance between them inside the cycle shrinks by exactly one per turn (the fast one gains one node on the slow one), so it hits zero before the slow pointer has completed a full lap, and they meet. That gives <code>true</code>.",
               "Only nodes reachable from node 0 are ever touched, so a loop among unreachable decoy nodes is never seen. The running time is O(n) and only two pointers are stored, so the space is O(1). The set based version has the same time but O(n) space."],
    time="O(n)", space="O(1)",
    solution='''def hasCycle(succ):
    slow = fast = 0
    while fast != -1 and succ[fast] != -1:
        slow = succ[slow]
        fast = succ[succ[fast]]
        if slow == fast:
            return True
    return False
''',
    tests=[[[1, 2, 3, 1]], [[1, 2, -1]], [[1, -1, 2]], [[-1]], [[0]], [[1, -1]], [[1, 0]], [[1, 1]], [[1, 2, 0]],
           [[1, 2, 3, 4, 2]], [[2, -1, 1]], [[1, -1, 3, 2]], [[1, 2, 3, 4, 5, -1]]],
)
_r = rnd(7101)
p["tests"].append([_rho(_r, 6000, 4000, None)])
p["tests"].append([_rho(_r, 6000, 6000, 5)])
p["tests"].append([_rho(_r, 6000, 3000, 2999)])


def b_has_cycle(succ):
    return _walk(succ)[1]


def g_has_cycle(r):
    n = r.randint(1, 9)
    if r.random() < 0.5:
        m = r.randint(1, n)
        return [_rho(r, n, m, r.choice([None] + list(range(m))))]
    return [[r.choice([-1] + list(range(n))) for _ in range(n)]]


def v_has_cycle(tests):
    for t in tests:
        succ = t["args"][0]
        assert 1 <= len(succ) <= 6000 and all(-1 <= x < len(succ) for x in succ)
    assert {t["expected"] for t in tests} == {True, False}


CHECKS["linked-list-has-cycle"] = (b_has_cycle, g_has_cycle, "exact")
VALIDATE["linked-list-has-cycle"] = v_has_cycle

p = add(
    id="linked-list-cycle-length", title="Length of the Cycle in a Linked List", diff="Easy", topic=TOPIC,
    fn="cycleLength", params=[("succ", "int[]")], ret="int", cmp="exact",
    desc=SUCC_ENC + "<p>Follow <code>succ</code> from the head. If the walk reaches <code>-1</code> the list has no cycle and the answer is <code>0</code>. Otherwise the walk eventually runs around a loop of nodes that repeats forever; return the number of nodes in that loop.</p>"
         "<p>Only nodes reachable from node <code>0</code> count; loops among unreachable nodes must be ignored. For <code>succ = [1,2,3,4,2]</code> the walk is <code>0, 1, 2, 3, 4, 2, ...</code>, the loop is <code>2, 3, 4</code> and the answer is <code>3</code>.</p>",
    constraints=["1 &le; succ.length &le; 6,000", "-1 &le; succ[i] &lt; succ.length", "Some nodes may be unreachable from node 0; they are ignored"],
    hints=["A map from node to the step number at which you first stood on it gives the length directly when you step on a node twice. It needs O(n) memory.",
           "First detect the cycle with a slow and a fast pointer. When they meet, the meeting node is inside the cycle.",
           "Keep one pointer at the meeting node and walk another from <code>succ[meeting]</code> until it returns to that node, counting the steps. The count is the cycle length."],
    editorial=["Run Floyd's algorithm: <code>slow</code> moves one node, <code>fast</code> two. If <code>fast</code> falls off the list there is no cycle, answer <code>0</code>. If they meet, the meeting node lies on the cycle (a pointer can only meet the other one inside the loop).",
               "Starting from that meeting node, follow <code>succ</code> until you come back to it, counting steps. You go around the loop exactly once, so the count is its length. The detection phase is O(n) and the counting phase is at most the cycle length, so the whole algorithm is O(n) time and O(1) space.",
               "The step-number map is the alternative: when a node is reached for the second time at step <code>j</code> and was first reached at step <code>i</code>, the cycle length is <code>j - i</code>."],
    time="O(n)", space="O(1)",
    solution='''def cycleLength(succ):
    slow = fast = 0
    while fast != -1 and succ[fast] != -1:
        slow = succ[slow]
        fast = succ[succ[fast]]
        if slow == fast:
            length = 1
            cur = succ[slow]
            while cur != slow:
                cur = succ[cur]
                length += 1
            return length
    return 0
''',
    tests=[[[1, 2, 3, 4, 2]], [[1, 2, -1]], [[1, 0]], [[-1]], [[0]], [[1, 1]], [[1, 2, 0]], [[1, 2, 3, 1]], [[1, -1, 2]],
           [[1, 2, 3, 4, 5, 6, 3]], [[3, -1, 1, 3]], [[1, 2, 3, 0, 5, 4]]],
)
_r = rnd(7102)
p["tests"].append([_rho(_r, 6000, 6000, 0)])
p["tests"].append([_rho(_r, 6000, 5000, 2000)])
p["tests"].append([_rho(_r, 6000, 6000, 5999)])


def b_cycle_len(succ):
    first, cur, step = {}, 0, 0
    while cur != -1:
        if cur in first:
            return step - first[cur]
        first[cur] = step
        cur = succ[cur]
        step += 1
    return 0


def v_cycle_len(tests):
    for t in tests:
        succ = t["args"][0]
        assert 1 <= len(succ) <= 6000 and all(-1 <= x < len(succ) for x in succ)
    assert any(t["expected"] == 0 for t in tests) and any(t["expected"] > 100 for t in tests) and any(t["expected"] == 1 for t in tests)


CHECKS["linked-list-cycle-length"] = (b_cycle_len, g_has_cycle, "exact")
VALIDATE["linked-list-cycle-length"] = v_cycle_len

p = add(
    id="linked-list-components-in-subset", title="Linked List Components in a Subset", diff="Easy", topic=TOPIC, tier="extra",
    fn="countComponents", params=[("vals", "int[]"), ("succ", "int[]"), ("marked", "int[]")], ret="int", cmp="exact",
    desc=VAL_ENC + "<p>All values in the list are distinct, and the list has no cycle. The array <code>marked</code> holds some values (they may even include values that do not occur in the list). A <em>component</em> is a maximal group of nodes that are next to each other in the list and whose values are all in <code>marked</code>. Return the number of components.</p>"
         "<p>Example: <code>vals = [10,20,30,40]</code>, <code>succ = [1,2,3,-1]</code> is the list <code>10 -> 20 -> 30 -> 40</code>. With <code>marked = [10,20,40]</code> the groups are <code>10 -> 20</code> and <code>40</code>, so the answer is <code>2</code>.</p>",
    constraints=["1 &le; n &le; 4,000", "-10<sup>9</sup> &le; vals[i] &le; 10<sup>9</sup>, all distinct", "0 &le; marked.length &le; 4,000, marked values are distinct", "The list starting at node 0 visits all n nodes and ends at a node with succ = -1"],
    hints=["Convert <code>marked</code> into a set so that you can test a value in O(1).",
           "A component starts at a node that is marked while the node just before it is not marked (or it is the head).",
           "Walk the list once keeping a flag <code>prevMarked</code>. Whenever the current node is marked and <code>prevMarked</code> is false, a new component begins: add one."],
    editorial=["Counting components is the same as counting their first nodes. A node is the first node of a component exactly when it is marked and its predecessor is missing or unmarked. So walk the list once, remember whether the previous node was marked, and add one at every false-to-true change.",
               "The marked values go into a hash set, so each membership test is O(1) and the whole pass takes O(n + m) time with O(m) extra space for the set."],
    time="O(n + m)", space="O(m)",
    solution='''def countComponents(vals, succ, marked):
    inside = set(marked)
    count = 0
    prev_marked = False
    cur = 0
    while cur != -1:
        now = vals[cur] in inside
        if now and not prev_marked:
            count += 1
        prev_marked = now
        cur = succ[cur]
    return count
''',
    tests=[[[10, 20, 30, 40], [1, 2, 3, -1], [10, 20, 40]], [[5], [-1], [5]], [[5], [-1], []],
           [[1, 2, 3], [1, 2, -1], [1, 2, 3]], [[1, 2, 3], [1, 2, -1], [1, 3]], [[1, 2, 3], [1, 2, -1], [7, 8]],
           [[3, 1, 2], [2, -1, 1], [1]], [[4, 9, 5, 7, 8], [3, 4, 1, 2, -1], [9, 5, 8, 4]],
           [[-10 ** 9, 0, 10 ** 9], [2, -1, 1], [10 ** 9, 0]]],
)
_r = rnd(7103)
_seq = _r.sample(range(-50000, 50000), 4000)
_vals, _succ = _enc(_r, _seq)
p["tests"].append([_vals, _succ, _r.sample(_seq, 1800)])
_vals, _succ = _enc(_r, _seq)
p["tests"].append([_vals, _succ, _seq[::2]])
_vals, _succ = _enc(_r, _seq)
p["tests"].append([_vals, _succ, _seq[:1500] + _seq[2000:3500]])


def b_components(vals, succ, marked):
    seq = [vals[x] for x in _walk(succ)[0]]
    flags = [v in marked for v in seq]
    return sum(1 for key, _ in groupby(flags) if key)


def g_components(r):
    n = r.randint(1, 9)
    seq = r.sample(range(-12, 12), n)
    vals, succ = _enc(r, seq)
    marked = r.sample(range(-12, 12), r.randint(0, 12))
    return [vals, succ, marked]


def v_components(tests):
    for t in tests:
        vals, succ, marked = t["args"]
        n = len(vals)
        assert 1 <= n <= 4000 and len(set(vals)) == n and len(set(marked)) == len(marked) and len(marked) <= 4000
        order, cyc = _walk(succ)
        assert not cyc and len(order) == n


CHECKS["linked-list-components-in-subset"] = (b_components, g_components, "exact")
VALIDATE["linked-list-components-in-subset"] = v_components

# ================================================================ MEDIUM

p = add(
    id="maximum-twin-sum-of-linked-list", title="Maximum Twin Sum of a Linked List", diff="Medium", topic=TOPIC,
    fn="maxTwinSum", params=[("vals", "int[]"), ("succ", "int[]")], ret="int", cmp="exact",
    desc=VAL_ENC + "<p>The list has an <em>even</em> number <code>n</code> of nodes and no cycle. Number the nodes in list order <code>0..n-1</code> (position 0 is the head). The <em>twin</em> of the node at position <code>i</code> is the node at position <code>n - 1 - i</code>, so the first node is paired with the last, the second with the second to last, and so on. The twin sum of a pair is the sum of its two values.</p>"
         "<p>Return the largest twin sum. Example: the list <code>4 -> 2 -> 2 -> 3</code> (<code>vals = [4,2,2,3]</code>, <code>succ = [1,2,3,-1]</code>) has the pairs (4, 3) and (2, 2), with sums 7 and 4, so the answer is <code>7</code>.</p><p>A solution with O(1) extra space exists: use only pointers, no array copy of the list.</p>",
    constraints=["2 &le; n &le; 4,000, n is even", "-10<sup>6</sup> &le; vals[i] &le; 10<sup>6</sup>", "The list starting at node 0 visits all n nodes and ends at a node with succ = -1"],
    hints=["Copying the values into an array and pairing index i with n - 1 - i solves it, but uses O(n) memory.",
           "The second half of the list, read backwards, is exactly the list of twins of the first half, in order. How do you read a half backwards without extra memory?",
           "Find the start of the second half with a slow and a fast pointer, reverse the second half in place, and then walk the first half and the reversed second half together, taking the maximum of the sums."],
    editorial=["With a slow pointer (one step) and a fast pointer (two steps) started at the head, the slow pointer stands at position n/2, the first node of the second half, when the fast pointer runs off the end (n is even, so there is no middle node to worry about).",
               "Reverse the part of the list that starts there. Its first node is now the original last node, the twin of the head. Walk one pointer from the head and one from that reversed half in lockstep: the two nodes at every step are twins, so the maximum of their value sums is the answer.",
               "Each of the three phases is O(n) and only pointers are used, so the total is O(n) time and O(1) space (the reversal here is performed on a copy of <code>succ</code> only because the arrays are inputs)."],
    time="O(n)", space="O(1)",
    solution='''def maxTwinSum(vals, succ):
    nxt = succ[:]
    slow = fast = 0
    while fast != -1 and nxt[fast] != -1:
        slow = nxt[slow]
        fast = nxt[nxt[fast]]
    prev, cur = -1, slow
    while cur != -1:
        after = nxt[cur]
        nxt[cur] = prev
        prev, cur = cur, after
    a, b = 0, prev
    best = None
    for _ in range(len(vals) // 2):
        s = vals[a] + vals[b]
        if best is None or s > best:
            best = s
        a = nxt[a]
        b = nxt[b]
    return best
''',
    tests=[[[4, 2, 2, 3], [1, 2, 3, -1]], [[5, 4, 2, 1], [1, 2, 3, -1]], [[1, 100000], [1, -1]], [[-5, -6], [1, -1]],
           [[1, 2, 3, 4, 5, 6], [1, 2, 3, 4, 5, -1]], [[-3, -1, -4, -1, -5, -9], [3, 5, 4, 2, 1, -1]],
           [[0, 0, 0, 0], [1, 2, 3, -1]], [[10 ** 6, 1, 1, 10 ** 6], [1, 2, 3, -1]], [[2, 9, 3, 7], [1, 2, 3, -1]],
           [[1, 9, 9, 1, 5, 5, 2, 2], [4, 2, 6, 1, 3, 7, 5, -1]]],
)
_r = rnd(7105)
for _n in (4000, 3998, 1000):
    _vals, _succ = _enc(_r, [_r.randint(-10 ** 6, 10 ** 6) for _ in range(_n)])
    p["tests"].append([_vals, _succ])


def b_twin(vals, succ):
    seq = [vals[x] for x in _walk(succ)[0]]
    n = len(seq)
    return max(seq[i] + seq[n - 1 - i] for i in range(n // 2))


def g_twin(r):
    n = 2 * r.randint(1, 5)
    return list(_enc(r, gen_arr(r, -9, 9, n, n)))


def v_twin(tests):
    for t in tests:
        vals, succ = t["args"]
        order, cyc = _walk(succ)
        assert not cyc and len(order) == len(vals) and 2 <= len(vals) <= 4000 and len(vals) % 2 == 0
        assert all(abs(v) <= 10 ** 6 for v in vals)


CHECKS["maximum-twin-sum-of-linked-list"] = (b_twin, g_twin, "exact")
VALIDATE["maximum-twin-sum-of-linked-list"] = v_twin

p = add(
    id="palindrome-list-with-one-deletion", title="Palindrome Linked List With One Deletion", diff="Medium", topic=TOPIC, tier="extra",
    fn="canBecomePalindrome", params=[("vals", "int[]"), ("succ", "int[]")], ret="bool", cmp="exact",
    desc=VAL_ENC + "<p>The list has no cycle and contains all <code>n</code> nodes. You may delete <em>at most one</em> node from the list (the remaining nodes keep their order). Return <code>true</code> if the values of the remaining list read the same from head to tail as from tail to head, and <code>false</code> otherwise.</p>"
         "<p>Example: the list <code>1 -> 2 -> 3 -> 2 -> 9 -> 1</code> becomes the palindrome <code>1 -> 2 -> 3 -> 2 -> 1</code> after deleting the node with value 9, so the answer is <code>true</code>. The list <code>1 -> 2 -> 3 -> 4</code> cannot be fixed with one deletion: the answer is <code>false</code>.</p>",
    constraints=["1 &le; n &le; 4,000", "-10<sup>9</sup> &le; vals[i] &le; 10<sup>9</sup>", "The list starting at node 0 visits all n nodes and ends at a node with succ = -1"],
    hints=["Trying every deletion and checking the result for being a palindrome costs O(n<sup>2</sup>). Can you find out where the first problem is?",
           "A list can only be read forward, but you can copy its values into an array in one pass. Then compare from both ends with two indices <code>i</code> and <code>j</code>.",
           "Move <code>i</code> and <code>j</code> inwards while the values are equal. At the first mismatch the deleted node must be at <code>i</code> or at <code>j</code>: check whether the range <code>i+1..j</code> or the range <code>i..j-1</code> is a palindrome."],
    editorial=["Walk the list once and store the values in an array. Compare from the outside in with two indices. If no mismatch ever appears, the list is already a palindrome and deleting nothing is allowed.",
               "At the first mismatch <code>a[i] != a[j]</code> every pair outside it matches, and any valid deletion must remove one of the two mismatching nodes (deleting any other node leaves the pair <code>a[i], a[j]</code> facing each other or shifts a different element against one of them, but the outer pairs all match, so the mismatch would remain). So the answer is <code>true</code> exactly when the values of <code>i+1..j</code> or those of <code>i..j-1</code> form a palindrome; each check is a linear scan.",
               "Total time is O(n) and the extra space is O(n) for the array copy."],
    time="O(n)", space="O(n)",
    solution='''def canBecomePalindrome(vals, succ):
    a = []
    cur = 0
    while cur != -1:
        a.append(vals[cur])
        cur = succ[cur]

    def is_pal(i, j):
        while i < j:
            if a[i] != a[j]:
                return False
            i += 1
            j -= 1
        return True

    i, j = 0, len(a) - 1
    while i < j:
        if a[i] != a[j]:
            return is_pal(i + 1, j) or is_pal(i, j - 1)
        i += 1
        j -= 1
    return True
''',
    tests=[],
)
_r = rnd(7106)
for _seq in ([1, 2, 3, 2, 9, 1], [1, 2, 3, 4], [1, 2, 1], [5], [5, 6], [1, 2, 3], [1, 1, 2, 1, 1], [1, 2, 2, 1, 3],
             [4, 1, 2, 2, 1], [7, 1, 2, 1, 8], [1, 2, 3, 3, 2, 4, 1], [3, 3, 3, 2, 3, 3]):
    p["tests"].append(list(_enc(_r, _seq)))
_half = [_r.randint(0, 9) for _ in range(1990)]
_pal = _half + _half[::-1]
_ins = _pal[:1300] + [10] + _pal[1300:]
p["tests"].append(list(_enc(_r, _ins)))
_bad = _pal[:]
_bad[500] = 11
_bad[3000] = 12
p["tests"].append(list(_enc(_r, _bad)))
_odd = _half + [5] + _half[::-1]
_odd[1000] = 11
p["tests"].append(list(_enc(_r, _odd)))


def b_pal_del(vals, succ):
    seq = [vals[x] for x in _walk(succ)[0]]
    if seq == seq[::-1]:
        return True
    return any((lambda t: t == t[::-1])(seq[:i] + seq[i + 1:]) for i in range(len(seq)))


def g_pal_del(r):
    n = r.randint(1, 9)
    k = r.randint(1, 3)
    if r.random() < 0.5:
        half = [r.randint(0, k) for _ in range(n // 2)]
        seq = half + ([r.randint(0, k)] if n % 2 else []) + half[::-1]
        if seq and r.random() < 0.7:
            seq.insert(r.randint(0, len(seq)), r.randint(0, k))
        if r.random() < 0.3 and seq:
            seq[r.randrange(len(seq))] = r.randint(0, k)
    else:
        seq = [r.randint(0, k) for _ in range(n)]
    return list(_enc(r, seq))


def v_pal_del(tests):
    for t in tests:
        vals, succ = t["args"]
        order, cyc = _walk(succ)
        assert not cyc and len(order) == len(vals) and 1 <= len(vals) <= 4000
    assert {t["expected"] for t in tests} == {True, False}


CHECKS["palindrome-list-with-one-deletion"] = (b_pal_del, g_pal_del, "exact")
VALIDATE["palindrome-list-with-one-deletion"] = v_pal_del

p = add(
    id="cut-the-cycle-out-of-a-linked-list", title="Cut the Cycle Out of a Linked List", diff="Medium", topic=TOPIC,
    fn="cutCycle", params=[("vals", "int[]"), ("succ", "int[]")], ret="int[]", cmp="exact",
    desc=VAL_ENC + "<p>Every node can be reached from the head. Following <code>succ</code> from node <code>0</code> either ends at <code>-1</code> or, if the list has a cycle, the last node of the walk (the last node visited before a node would be visited again) points back to an earlier node of the walk.</p>"
         "<p>Repair the list: if it has a cycle, replace the pointer of that last node by <code>-1</code>, so that the list ends there. Then return the values of the list from head to tail. A list without a cycle is returned unchanged.</p>"
         "<p>Example: <code>vals = [7,8,9,4]</code>, <code>succ = [1,2,3,1]</code> is <code>7 -> 8 -> 9 -> 4 -> 8 -> ...</code>. Node 3 (value 4) points back to node 1, so we cut that link and the answer is <code>[7,8,9,4]</code>. The point is to find that node without a visited set.</p>",
    constraints=["1 &le; n &le; 2,500", "-10<sup>9</sup> &le; vals[i] &le; 10<sup>9</sup>", "-1 &le; succ[i] &lt; n", "Every node is reachable from node 0"],
    hints=["Walking from the head with a visited set until you see a repeat shows the last node directly. Try to do it with O(1) extra memory.",
           "First find the node where the cycle starts: a slow and a fast pointer meet inside the cycle, and a pointer restarted from the head together with the one at the meeting spot meet again at the entry node.",
           "Once you know the entry node, walk around the cycle from it until you reach the node whose <code>succ</code> is the entry. That is the node to cut. Careful with a cycle of length 1 (a self loop) and with an entry node that is the head."],
    editorial=["Phase 1: Floyd's tortoise and hare. If the fast pointer reaches <code>-1</code> there is no cycle and the list is already fine. Otherwise the pointers meet inside the cycle.",
               "Phase 2: put one pointer back on the head and leave the other at the meeting node; advancing both by one node per turn makes them meet exactly at the entry node of the cycle (the tail before the cycle has length a, and the meeting node is a multiple of the cycle length minus a steps before the entry, so the walks align after a steps).",
               "Phase 3: from the entry node walk along the cycle until the next node is the entry again. This last node is the end of the list; set its successor to <code>-1</code>. Finally read out the values. Everything is O(n) time and O(1) extra space apart from the output."],
    time="O(n)", space="O(1)",
    solution='''def cutCycle(vals, succ):
    succ = succ[:]
    slow = fast = 0
    meet = -1
    while fast != -1 and succ[fast] != -1:
        slow = succ[slow]
        fast = succ[succ[fast]]
        if slow == fast:
            meet = slow
            break
    if meet != -1:
        entry, p = 0, meet
        while entry != p:
            entry = succ[entry]
            p = succ[p]
        last = entry
        while succ[last] != entry:
            last = succ[last]
        succ[last] = -1
    out = []
    cur = 0
    while cur != -1:
        out.append(vals[cur])
        cur = succ[cur]
    return out
''',
    tests=[[[7, 8, 9, 4], [1, 2, 3, 1]], [[5], [-1]], [[5], [0]], [[1, 2], [1, -1]], [[1, 2], [1, 0]], [[1, 2], [1, 1]],
           [[1, 2, 3], [1, 2, 0]], [[1, 2, 3], [1, 2, 2]], [[1, 2, 3, 4, 5], [1, 2, 3, 4, -1]],
           [[10, 20, 30, 40, 50, 60], [1, 2, 3, 4, 5, 2]], [[-10 ** 9, 0, 10 ** 9], [1, 2, 1]]],
)
_r = rnd(7107)
for _n, _back in ((2500, None), (2500, 1200), (2499, 0), (2500, 2499)):
    _vals, _succ = _enc(_r, [_r.randint(-1000, 1000) for _ in range(_n)], _back)
    p["tests"].append([_vals, _succ])
p["tests"].pop()  # keep the total size small: three large cases are enough


def b_cut(vals, succ):
    return [vals[x] for x in _walk(succ)[0]]


def g_cut(r):
    n = r.randint(1, 9)
    return list(_enc(r, gen_arr(r, -5, 5, n, n), r.choice([None] + list(range(n)))))


def v_cut(tests):
    for t in tests:
        vals, succ = t["args"]
        assert 1 <= len(vals) <= 2500 and all(-1 <= x < len(succ) for x in succ)
        assert len(_walk(succ)[0]) == len(vals), "unreachable node"
    assert any(_walk(t["args"][1])[1] for t in tests) and any(not _walk(t["args"][1])[1] for t in tests)


CHECKS["cut-the-cycle-out-of-a-linked-list"] = (b_cut, g_cut, "exact")
VALIDATE["cut-the-cycle-out-of-a-linked-list"] = v_cut

p = add(
    id="slow-fast-pointer-meeting-round", title="Slow and Fast Pointers Meeting Round", diff="Medium", topic=TOPIC, tier="extra",
    fn="meetingRound", params=[("succ", "int[]"), ("speed", "int")], ret="int", cmp="exact",
    desc=SUCC_ENC + "<p>A tortoise and a hare both start on node <code>0</code>. In every round the tortoise moves <code>1</code> node forward along <code>succ</code> and the hare moves <code>speed</code> nodes forward. If the hare would step beyond the end of the list (onto <code>-1</code>) the chase is over and nobody is ever met.</p>"
         "<p>Return the smallest round <code>t &ge; 1</code> after which the tortoise and the hare stand on the same node, or <code>-1</code> if that never happens. Only nodes reachable from node <code>0</code> matter.</p>"
         "<p>Example: <code>succ = [1,2,3,4,2]</code>, <code>speed = 2</code>. The tortoise visits 1, 2, 3 after rounds 1, 2, 3; the hare is on 2, 4, 3. They meet in round <code>3</code>.</p>",
    constraints=["1 &le; succ.length &le; 6,000", "-1 &le; succ[i] &lt; succ.length", "2 &le; speed &le; 10"],
    hints=["You can simulate the rounds. The question is when to stop: when is it certain that the two will never meet?",
           "If the list ends, the hare falls off and the answer is -1. If the list has a cycle, they certainly meet at some point. After the tortoise has entered the cycle, both of them run around it.",
           "Let the walk have a tail of <code>a</code> nodes followed by a cycle of <code>c</code> nodes. In the cycle, the hare gains <code>speed - 1</code> nodes per round, so after the tortoise has entered the cycle they meet at the first round where <code>(speed - 1) * t</code> is a multiple of <code>c</code>."],
    editorial=["Let <code>pos(t)</code> be the node reached after <code>t</code> steps. The tortoise is at <code>pos(t)</code> and the hare at <code>pos(speed * t)</code> after <code>t</code> rounds. If the walk ends at <code>-1</code> the hare falls off first and the answer is <code>-1</code>: two different positions of an acyclic walk are different nodes, and <code>speed * t != t</code> for <code>t &ge; 1</code>.",
               "If the walk has a tail of <code>a</code> distinct nodes before a cycle of <code>c</code> nodes, then for <code>t &ge; a</code> both are on the cycle and they coincide exactly when <code>speed * t &equiv; t (mod c)</code>, i.e. when <code>c</code> divides <code>(speed - 1) * t</code>. This holds for every multiple of <code>c / gcd(c, speed - 1)</code>. For <code>t &lt; a</code> the tortoise is still in the tail, where it cannot meet the hare. So the answer is the smallest multiple of <code>unit = c / gcd(c, speed - 1)</code> that is at least <code>max(a, 1)</code>.",
               "To find <code>a</code> and <code>c</code> record the index of each node when it is first visited; the node that is reached twice has first index <code>a</code> and the walk length gives <code>c</code>. All of this is O(n)."],
    time="O(n)", space="O(n)",
    solution='''from math import gcd


def meetingRound(succ, speed):
    first = {}
    cur = 0
    step = 0
    while cur != -1 and cur not in first:
        first[cur] = step
        cur = succ[cur]
        step += 1
    if cur == -1:
        return -1
    a = first[cur]
    c = step - a
    unit = c // gcd(c, speed - 1)
    lo = max(a, 1)
    return (lo + unit - 1) // unit * unit
''',
    tests=[[[1, 2, 3, 4, 2], 2], [[1, 2, -1], 2], [[1, 2, 3, 4, 2], 3], [[0], 2], [[0], 7], [[1, 0], 2], [[1, 0], 3],
           [[1, 2, 3, 0], 3], [[1, 2, 3, 0], 5], [[-1], 2], [[1, 2, 3, 4, 5, 6, 7, 4], 2], [[1, 2, 3, 4, 5, 6, 7, 4], 4],
           [[1, 2, 3, 1], 4], [[1, -1, 2], 3]],
)
_r = rnd(7108)
p["tests"].append([_rho(_r, 6000, 6000, 0), 2])
p["tests"].append([_rho(_r, 6000, 6000, 2999), 7])
p["tests"].append([_rho(_r, 6000, 5000, 4990), 10])


def b_meeting(succ, speed):
    t_pos, h_pos = 0, 0
    for t in range(1, 20000):
        t_pos = succ[t_pos]
        for _ in range(speed):
            h_pos = succ[h_pos]
            if h_pos == -1:
                return -1
        if t_pos == h_pos:
            return t
    return -1


def g_meeting(r):
    n = r.randint(1, 9)
    if r.random() < 0.5:
        m = r.randint(1, n)
        succ = _rho(r, n, m, r.choice([None] + list(range(m))))
    else:
        succ = [r.choice([-1] + list(range(n))) for _ in range(n)]
    return [succ, r.randint(2, 10)]


def v_meeting(tests):
    for t in tests:
        succ, speed = t["args"]
        assert 1 <= len(succ) <= 6000 and all(-1 <= x < len(succ) for x in succ) and 2 <= speed <= 10
    assert any(t["expected"] == -1 for t in tests) and any(t["expected"] > 100 for t in tests)
    assert all(t["expected"] == -1 or t["expected"] >= 1 for t in tests)


CHECKS["slow-fast-pointer-meeting-round"] = (b_meeting, g_meeting, "exact")
VALIDATE["slow-fast-pointer-meeting-round"] = v_meeting

p = add(
    id="middle-node-of-a-walk-that-may-cycle", title="Middle Node of a Walk That May Cycle", diff="Medium", topic=TOPIC, tier="extra",
    fn="walkMiddleValue", params=[("vals", "int[]"), ("succ", "int[]")], ret="int", cmp="exact",
    desc=VAL_ENC + "<p>Walk from node <code>0</code> by following <code>succ</code>. The <em>walk</em> is the sequence of distinct nodes you stand on, in order, until the next step would be <code>-1</code> (the list ends) or would lead to a node that is already in the walk (the list has a cycle). Let <code>m</code> be the number of nodes in the walk. Return the value stored in the node at position <code>m / 2</code> (rounded down, positions counted from 0), that is the middle node, or the second of the two middle nodes when <code>m</code> is even.</p>"
         "<p>Nodes that cannot be reached from node <code>0</code> are not part of the walk. Example: <code>vals = [5,6,7,8]</code>, <code>succ = [1,2,3,1]</code>. The walk is nodes <code>0, 1, 2, 3</code> (then it would return to node 1), so <code>m = 4</code> and the answer is the value at position 2, which is <code>7</code>.</p>"
         "<p>It is possible to do this with O(1) extra memory.</p>",
    constraints=["1 &le; n &le; 4,000", "-10<sup>9</sup> &le; vals[i] &le; 10<sup>9</sup>", "-1 &le; succ[i] &lt; n", "Some nodes may be unreachable from node 0; they are ignored"],
    hints=["If you knew <code>m</code>, the answer would be the node you reach after <code>m / 2</code> steps. How can you find <code>m</code> without remembering the visited nodes?",
           "In a walk with a tail of <code>a</code> nodes followed by a cycle of <code>c</code> nodes, <code>m = a + c</code>. A slow and a fast pointer tell you whether there is a cycle at all.",
           "After the pointers meet, count the cycle length <code>c</code> by going around once from the meeting node, then restart one pointer at the head and move both pointers one node at a time until they meet again; that is the entry node, and its distance from the head is <code>a</code>. Without a cycle, <code>m</code> is simply the number of nodes before <code>-1</code>."],
    editorial=["First measure the walk. Run Floyd's algorithm: if the fast pointer falls off the list, the walk is the whole list and <code>m</code> is obtained by counting nodes. Otherwise the pointers meet inside the cycle.",
               "From the meeting node, walk once around the cycle to get its length <code>c</code>. Then put one pointer on the head and keep the other on the meeting node and advance both together; they meet at the cycle entry after exactly <code>a</code> steps, where <code>a</code> is the length of the tail. This gives <code>m = a + c</code>.",
               "Finally walk <code>m / 2</code> nodes from the head and return the value there. Every phase takes O(n) steps and only a few pointers are kept, so the time is O(n) and the extra space O(1). Storing the walk in a list is simpler but uses O(n) memory."],
    time="O(n)", space="O(1)",
    solution='''def walkMiddleValue(vals, succ):
    slow = fast = 0
    meet = -1
    while fast != -1 and succ[fast] != -1:
        slow = succ[slow]
        fast = succ[succ[fast]]
        if slow == fast:
            meet = slow
            break
    if meet == -1:
        m = 0
        cur = 0
        while cur != -1:
            m += 1
            cur = succ[cur]
    else:
        c = 1
        cur = succ[meet]
        while cur != meet:
            cur = succ[cur]
            c += 1
        a = 0
        x, y = 0, meet
        while x != y:
            x = succ[x]
            y = succ[y]
            a += 1
        m = a + c
    cur = 0
    for _ in range(m // 2):
        cur = succ[cur]
    return vals[cur]
''',
    tests=[[[5, 6, 7, 8], [1, 2, 3, 1]], [[5], [-1]], [[5], [0]], [[1, 2], [1, -1]], [[1, 2], [1, 0]], [[1, 2, 3], [1, 2, -1]],
           [[1, 2, 3], [1, 2, 0]], [[1, 2, 3, 4, 5], [1, 2, 3, 4, 2]], [[1, 2, 3, 4, 5], [1, 2, 3, 4, -1]],
           [[9, 8, 7], [1, -1, 2]], [[1, 2, 3, 4, 5, 6], [1, 2, 3, 4, 5, 5]], [[-10 ** 9, 0, 10 ** 9], [1, 2, 1]]],
)
_r = rnd(7109)
for _n, _m, _back in ((4000, 4000, 0), (4000, 3001, 1200), (4000, 3500, None)):
    _succ = _rho(_r, _n, _m, _back)
    p["tests"].append([[_r.randint(-1000, 1000) for _ in range(_n)], _succ])


def b_walk_middle(vals, succ):
    order, _ = _walk(succ)
    return vals[order[len(order) // 2]]


def g_walk_middle(r):
    n = r.randint(1, 9)
    vals = [r.randint(-9, 9) for _ in range(n)]
    if r.random() < 0.5:
        m = r.randint(1, n)
        return [vals, _rho(r, n, m, r.choice([None] + list(range(m))))]
    return [vals, [r.choice([-1] + list(range(n))) for _ in range(n)]]


def v_walk_middle(tests):
    for t in tests:
        vals, succ = t["args"]
        assert 1 <= len(vals) == len(succ) <= 4000 and all(-1 <= x < len(succ) for x in succ)
    assert any(_walk(t["args"][1])[1] for t in tests) and any(not _walk(t["args"][1])[1] for t in tests)


CHECKS["middle-node-of-a-walk-that-may-cycle"] = (b_walk_middle, g_walk_middle, "exact")
VALIDATE["middle-node-of-a-walk-that-may-cycle"] = v_walk_middle

# ================================================================ HARD

p = add(
    id="first-shared-node-of-two-possibly-cyclic-lists", title="First Shared Node of Two Possibly Cyclic Lists", diff="Hard", topic=TOPIC, tier="extra",
    fn="firstSharedNode", params=[("succ", "int[]"), ("headA", "int"), ("headB", "int")], ret="int", cmp="exact",
    desc=SUCC_ENC.replace(" The list starts at node <code>0</code> (its head).", "") +
         "<p>Two lists live in the same structure: list A starts at node <code>headA</code> and list B starts at node <code>headB</code> (the two heads may even be the same node). Each list is the sequence of distinct nodes you visit from its head by following <code>succ</code>, until you reach <code>-1</code> or would step on a node that is already in that list (so a list may end in a cycle).</p>"
         "<p>Return the first node of list A, in the order of list A, that also belongs to list B, or <code>-1</code> if the two lists have no node in common. Node numbers are the answer, not values.</p>"
         "<p>Example: <code>succ = [1,2,3,-1,2]</code>, <code>headA = 0</code>, <code>headB = 4</code>. List A is nodes <code>0, 1, 2, 3</code> and list B is nodes <code>4, 2, 3</code>. The first node of A that is also in B is node <code>2</code>.</p>"
         "<p>Try to use O(1) extra memory: the cases with and without cycles need different handling.</p>",
    constraints=["1 &le; succ.length &le; 4,000", "-1 &le; succ[i] &lt; succ.length", "0 &le; headA, headB &lt; succ.length"],
    hints=["Putting every node of B in a set and scanning A in order solves it with O(n) memory. For O(1) memory, first ask which of the lists have a cycle.",
           "If exactly one list has a cycle, they cannot share a node (a node shared with an acyclic list would make the other list end as well). If neither has a cycle, align the two lists by their lengths and walk together. Use Floyd's algorithm to find the entry node of each cycle.",
           "If both have cycles, they share nodes only if they run into the same cycle. When the two entry nodes are equal, treat the entry node as the end of both lists and use the length alignment trick. When the entries differ but lie on one cycle, the tails cannot touch and the answer is the entry node of A."],
    editorial=["Because every node has exactly one successor, once the two lists touch they continue together for good. A list is therefore a tail followed by an optional cycle, and the two lists can only relate in a few ways.",
               "Find the cycle entry of each list with Floyd's algorithm (meet inside the cycle, then restart one pointer at the head and advance both one node at a time). If exactly one list is cyclic, or both are cyclic but their cycles are different cycles, the answer is <code>-1</code>. If both are acyclic, compute the two lengths, advance the pointer of the longer list by the difference, then move both pointers together; they are equal at the first shared node, or both reach <code>-1</code> together.",
               "If both lists are cyclic on the same cycle there are two cases. With equal entry nodes the tails may have merged earlier: run the length alignment with the entry node playing the role of the end; the pointers meet at the first shared node at the latest at the entry. With different entry nodes the tails never meet (they would have merged and then shared an entry), but list B contains the whole cycle, so the first node of A that lies in B is the entry node of A. All steps are linear, so the total time is O(n) and the extra space is O(1)."],
    time="O(n)", space="O(1)",
    solution='''def firstSharedNode(succ, headA, headB):
    def entry(h):
        slow = fast = h
        while fast != -1 and succ[fast] != -1:
            slow = succ[slow]
            fast = succ[succ[fast]]
            if slow == fast:
                slow = h
                while slow != fast:
                    slow = succ[slow]
                    fast = succ[fast]
                return slow
        return -1

    def dist(h, stop):
        d = 0
        while h != stop:
            h = succ[h]
            d += 1
        return d

    def merge(a, b, stop):
        la, lb = dist(a, stop), dist(b, stop)
        while la > lb:
            a = succ[a]
            la -= 1
        while lb > la:
            b = succ[b]
            lb -= 1
        while a != b:
            a = succ[a]
            b = succ[b]
        return a

    ea, eb = entry(headA), entry(headB)
    if (ea == -1) != (eb == -1):
        return -1
    if ea == -1:
        return merge(headA, headB, -1)
    if ea == eb:
        return merge(headA, headB, ea)
    cur = succ[ea]
    while cur != ea:
        if cur == eb:
            return ea
        cur = succ[cur]
    return -1
''',
    tests=[[[1, 2, 3, -1, 2], 0, 4], [[-1], 0, 0], [[1, -1], 0, 0], [[1, -1, 3, -1], 0, 2], [[1, 0], 0, 1], [[1, 2, 0, 2], 0, 3],
           [[0, 1], 0, 1], [[0, 0], 1, 0], [[1, 1, -1], 0, 2], [[1, 2, 3, 4, 2], 0, 3], [[1, 2, 3, 4, 2, 4, 5], 0, 6],
           [[1, 2, 3, 1, 3, 4], 0, 5], [[2, 2, 3, 1], 0, 1], [[1, 2, -1, 2, 3], 4, 0]],
)
_r = rnd(7110)
p["tests"].append(_scenario(_r, "tree", 1500, 900, 1600, back=700))
p["tests"].append(_scenario(_r, "ring", 1000, 700, 2000, x=300, y=1500))
_g = _G()
_A, _B = _g.chain(2000), _g.chain(1800)
p["tests"].append(_g.done(_r, [_A[0], _B[0]]))


def b_shared(succ, ha, hb):
    in_b, cur = set(), hb
    while cur != -1 and cur not in in_b:
        in_b.add(cur)
        cur = succ[cur]
    seen, cur = set(), ha
    while cur != -1 and cur not in seen:
        if cur in in_b:
            return cur
        seen.add(cur)
        cur = succ[cur]
    return -1


def g_shared(r):
    n = r.randint(1, 9)
    k = r.random()
    if k < 0.4:
        return [[r.choice([-1] + list(range(n))) for _ in range(n)], r.randrange(n), r.randrange(n)]
    if k < 0.7:
        return _scenario(r, "tree", r.randint(0, 3), r.randint(0, 3), 3, back=r.choice([None, 0, 1, 2]))
    if k < 0.85:
        ls = r.randint(1, 4)
        return _scenario(r, "ring", r.randint(0, 3), r.randint(0, 3), ls, x=r.randrange(ls), y=r.randrange(ls))
    ls = r.randint(1, 3)
    return _scenario(r, "rho2", r.randint(0, 3), r.randint(0, 3), ls, lt=r.randint(1, 3), back=r.choice([None, 0]), ring_a=r.random() < 0.5)


def v_shared(tests):
    for t in tests:
        succ, ha, hb = t["args"]
        n = len(succ)
        assert 1 <= n <= 4000 and all(-1 <= x < n for x in succ) and 0 <= ha < n and 0 <= hb < n
    assert any(t["expected"] == -1 for t in tests) and sum(1 for t in tests if t["expected"] != -1) >= 8
    assert any(_walk(t["args"][0], t["args"][1])[1] for t in tests) and any(not _walk(t["args"][0], t["args"][1])[1] for t in tests)


CHECKS["first-shared-node-of-two-possibly-cyclic-lists"] = (b_shared, g_shared, "exact")
VALIDATE["first-shared-node-of-two-possibly-cyclic-lists"] = v_shared

p = add(
    id="longest-palindromic-arc-of-circular-list", title="Longest Palindromic Arc of a Circular List", diff="Hard", topic=TOPIC, tier="extra",
    fn="longestPalindromicArc", params=[("vals", "int[]"), ("succ", "int[]")], ret="int", cmp="exact",
    desc=VAL_ENC.replace("A singly linked list", "A circular singly linked list").replace(
        "or <code>-1</code> if there is none. ", "and the last node links back to the head, so no node has <code>-1</code>. ") +
         "<p>Starting at any node and following <code>succ</code> for <code>L</code> nodes (with <code>1 &le; L &le; n</code>) reads an <em>arc</em> of <code>L</code> values. An arc is a palindrome if its values read the same from the first to the last as from the last to the first. The arc may cross the place where node <code>0</code> is, i.e. wrap around the circle. Return the largest <code>L</code> for which some arc of <code>L</code> nodes is a palindrome.</p>"
         "<p>Example: <code>vals = [1,2,3,2]</code>, <code>succ = [1,2,3,0]</code> is the circle <code>1 -> 2 -> 3 -> 2 -> (back to 1)</code>. The arc <code>2, 3, 2</code> has length 3, and the arc of length 4 reads <code>1,2,3,2</code> (or a rotation of it), which is not a palindrome. Also the arc <code>2, 1, 2</code> (starting at the last node and wrapping around) is a palindrome of length 3. The answer is <code>3</code>.</p>",
    constraints=["1 &le; n &le; 3,500", "-10<sup>9</sup> &le; vals[i] &le; 10<sup>9</sup>", "Starting at node 0 and following succ visits every node once and returns to node 0"],
    hints=["First read the circle once into an array of n values. Checking all arcs (start, length) is cubic; expanding around every centre is quadratic. Both are too slow for n = 3,500 in the worst case (all values equal).",
           "To handle arcs that wrap around, write the values twice in a row: every arc of the circle with length at most n is a substring of this array of length 2n.",
           "Run Manacher's algorithm on the doubled array to get the longest palindrome around every centre, and cap each one at n (a palindrome around a centre stays a palindrome when you cut equal amounts from both ends, so you can shorten it to the largest allowed length of the same parity)."],
    editorial=["Read the circle into an array <code>a</code> of length n by following <code>succ</code> from node 0, then form <code>s = a + a</code>. An arc of L &le; n nodes that starts at position i is the substring <code>s[i .. i+L-1]</code>, and conversely every substring of <code>s</code> with length at most n is an arc. So the problem is the longest palindromic substring of <code>s</code> whose length does not exceed n.",
               "Manacher's algorithm computes, for each of the 2n odd centres and 2n even centres, the radius of the longest palindrome, in O(n) total. A palindrome around a centre can be shortened symmetrically, so for an odd centre the best allowed length is <code>min(2*r - 1, n or n - 1)</code>, taking n if n is odd and n - 1 otherwise; for an even centre it is <code>min(2*r, n or n - 1)</code> with n if n is even. The answer is the maximum over all centres.",
               "The array copy and the Manacher arrays take O(n) memory and the whole algorithm is O(n) time. A simpler expand-around-the-centre solution is O(n<sup>2</sup>) and also works for the smaller tests but is too slow when many values are equal."],
    time="O(n)", space="O(n)",
    solution='''def longestPalindromicArc(vals, succ):
    n = len(vals)
    a = []
    cur = 0
    for _ in range(n):
        a.append(vals[cur])
        cur = succ[cur]
    s = a + a
    m = 2 * n
    d1 = [0] * m
    l, r = 0, -1
    for i in range(m):
        k = 1 if i > r else min(d1[l + r - i], r - i + 1)
        while i - k >= 0 and i + k < m and s[i - k] == s[i + k]:
            k += 1
        d1[i] = k
        if i + k - 1 > r:
            l, r = i - k + 1, i + k - 1
    d2 = [0] * m
    l, r = 0, -1
    for i in range(m):
        k = 0 if i > r else min(d2[l + r - i + 1], r - i + 1)
        while i + k < m and i - k - 1 >= 0 and s[i + k] == s[i - k - 1]:
            k += 1
        d2[i] = k
        if i + k - 1 > r:
            l, r = i - k, i + k - 1
    cap_odd = n if n % 2 == 1 else n - 1
    cap_even = n if n % 2 == 0 else n - 1
    best = 1
    for i in range(m):
        best = max(best, min(2 * d1[i] - 1, cap_odd), min(2 * d2[i], cap_even))
    return best
''',
    tests=[[[1, 2, 3, 2], [1, 2, 3, 0]], [[7], [0]], [[1, 2], [1, 0]], [[4, 4], [1, 0]], [[1, 2, 3], [1, 2, 0]], [[5, 5, 5, 5, 5], [1, 2, 3, 4, 0]],
           [[1, 2, 2, 1, 3], [1, 2, 3, 4, 0]], [[3, 1, 2, 2, 1], [1, 2, 3, 4, 0]], [[1, 2, 1, 2, 1, 2], [1, 2, 3, 4, 5, 0]],
           [[1, 1, 2, 3, 1, 1], [1, 2, 3, 4, 5, 0]], [[-10 ** 9, 10 ** 9, -10 ** 9], [1, 2, 0]]],
)
_r = rnd(7111)
p["tests"].append(list(_enc(_r, [_r.randint(0, 1) for _ in range(3500)], 0)))
_core = [_r.randint(0, 3) for _ in range(900)]
_arc = _core + [9] + _core[::-1]
_seq = _arc[1200:] + [_r.randint(4, 8) for _ in range(1500)] + _arc[:1200]
p["tests"].append(list(_enc(_r, _seq, 0)))
p["tests"].append(list(_enc(_r, [4] * 3499 + [5], 0)))


def b_arc(vals, succ):
    a, cur = [], 0
    for _ in range(len(vals)):
        a.append(vals[cur])
        cur = succ[cur]
    n = len(a)
    best = 1
    for i in range(n):
        for L in range(best + 1, n + 1):
            arc = [a[(i + t) % n] for t in range(L)]
            if arc == arc[::-1]:
                best = L
    return best


def g_arc(r):
    n = r.randint(1, 10)
    return list(_enc(r, [r.randint(0, r.choice([1, 2, 3])) for _ in range(n)], 0))


def v_arc(tests):
    for t in tests:
        vals, succ = t["args"]
        n = len(vals)
        order, cyc = _walk(succ)
        assert 1 <= n <= 3500 and len(order) == n and succ[order[-1]] == 0
        assert all(abs(v) <= 10 ** 9 for v in vals)
    assert any(t["expected"] == len(t["args"][0]) for t in tests) and any(t["expected"] < len(t["args"][0]) - 5 for t in tests)


CHECKS["longest-palindromic-arc-of-circular-list"] = (b_arc, g_arc, "exact")
VALIDATE["longest-palindromic-arc-of-circular-list"] = v_arc

p = add(
    id="single-deletions-leaving-palindrome-list", title="Single Deletions Leaving a Palindrome List", diff="Hard", topic=TOPIC, tier="extra",
    fn="countPalindromeDeletions", params=[("vals", "int[]"), ("succ", "int[]")], ret="int", cmp="exact",
    desc=VAL_ENC + "<p>The list has no cycle and contains all <code>n</code> nodes. For each node, consider the list that remains after deleting <i>only that node</i> (the others keep their order). Count the nodes for which the remaining list is a palindrome, i.e. reads the same from head to tail as from tail to head. An empty list counts as a palindrome. Two different nodes are counted separately even if they leave the same sequence of values.</p>"
         "<p>Example: the list <code>1 -> 1 -> 2 -> 1</code> (<code>vals = [1,1,2,1]</code>, <code>succ = [1,2,3,-1]</code>). Deleting the first or second node leaves <code>1, 2, 1</code> (a palindrome), deleting the node with value 2 leaves <code>1, 1, 1</code> (a palindrome), deleting the last node leaves <code>1, 1, 2</code> (not a palindrome). The answer is <code>3</code>.</p>",
    constraints=["1 &le; n &le; 4,000", "-10<sup>9</sup> &le; vals[i] &le; 10<sup>9</sup>", "The list starting at node 0 visits all n nodes and ends at a node with succ = -1"],
    hints=["Trying every deletion costs O(n<sup>2</sup>) in total, which is fine for n = 4,000 in a compiled language but is not the idea. Think about which deletions can possibly work.",
           "Deleting any node of a block of equal neighbouring values leaves the same sequence. So count whole blocks (maximal runs of equal values) rather than single nodes. Find the first pair of positions <code>i &lt; j</code> that mirrors each other and holds different values.",
           "If there is no such pair, the list is already a palindrome and the only deletions that keep it one are those inside the run of equal values around the centre. Otherwise only the run containing position <code>i</code> and the run containing position <code>j</code> can work: test each by checking the list without one element of that run, and add the length of the run when it works."],
    editorial=["Read the values into an array <code>a</code>. Removing any element from a maximal run of equal values gives the same array, so it is enough to decide for one representative per run and then add the run length.",
               "If <code>a</code> is not a palindrome, let <code>(i, j)</code>, with <code>j = n - 1 - i</code>, be the outermost pair with <code>a[i] != a[j]</code>. All pairs outside it match. A deletion that fixes the list must remove an element equal to <code>a[i]</code> from the left part's run or an element equal to <code>a[j]</code> from the right part's run (any other deletion leaves the outer mismatch in place after the shift). So only the run of <code>i</code> and the run of <code>j</code> are candidates, and they are different runs because their values differ. For each candidate delete one element, test palindromicity in O(n), and add the run length if it succeeds.",
               "If <code>a</code> is already a palindrome, a deletion keeps it a palindrome exactly when it removes one of the equal values around the centre: for odd n the run containing the middle element, for even n the run containing the two middle elements. Its length is the answer; for example <code>[7]</code> gives 1 (the empty list) and <code>[2,2]</code> gives 2. Everything is O(n) time and O(n) space for the array."],
    time="O(n)", space="O(n)",
    solution='''def countPalindromeDeletions(vals, succ):
    a = []
    cur = 0
    while cur != -1:
        a.append(vals[cur])
        cur = succ[cur]
    n = len(a)

    def run_len(p):
        lo = hi = p
        while lo > 0 and a[lo - 1] == a[p]:
            lo -= 1
        while hi < n - 1 and a[hi + 1] == a[p]:
            hi += 1
        return hi - lo + 1

    def ok_without(p):
        b = a[:p] + a[p + 1:]
        return b == b[::-1]

    i, j = 0, n - 1
    while i < j and a[i] == a[j]:
        i += 1
        j -= 1
    if i >= j:
        return run_len(n // 2)
    total = 0
    if ok_without(i):
        total += run_len(i)
    if ok_without(j):
        total += run_len(j)
    return total
''',
    tests=[[[1, 1, 2, 1], [1, 2, 3, -1]], [[7], [-1]], [[2, 2], [1, -1]], [[1, 2], [1, -1]], [[1, 2, 3], [1, 2, -1]],
           [[1, 2, 1], [1, 2, -1]], [[1, 1, 1], [1, 2, -1]], [[1, 1, 1, 2, 1, 1], [1, 2, 3, 4, 5, -1]],
           [[1, 2, 2, 1], [1, 2, 3, -1]], [[1, 2, 3, 2, 1], [1, 2, 3, 4, -1]], [[1, 2, 1, 2, 1], [1, 2, 3, 4, -1]],
           [[3, 1, 3, 3], [1, 2, 3, -1]], [[-10 ** 9, 5, -10 ** 9, 5], [1, 2, 3, -1]]],
)
_r = rnd(7112)
p["tests"].append(list(_enc(_r, [1] * 1500 + [2] + [1] * 1499)))
p["tests"].append(list(_enc(_r, [8] * 3000)))
_half = [_r.randint(0, 2) for _ in range(1000)]
p["tests"].append(list(_enc(_r, _half + [5] * 40 + _half[::-1])))
_half = [_r.randint(0, 1) for _ in range(1500)]
p["tests"].append(list(_enc(_r, _half + [3] + [1] * 5 + [4] + _half[::-1])))


def b_pal_dels(vals, succ):
    a = [vals[x] for x in _walk(succ)[0]]
    return sum(1 for p in range(len(a)) if (lambda b: b == b[::-1])(a[:p] + a[p + 1:]))


def g_pal_dels(r):
    n = r.randint(1, 10)
    k = r.randint(1, 3)
    if r.random() < 0.6:
        half = [r.randint(0, k) for _ in range(n // 2)]
        seq = half + ([r.randint(0, k)] if n % 2 else []) + half[::-1]
        if seq and r.random() < 0.6:
            seq.insert(r.randint(0, len(seq)), r.randint(0, k))
        if seq and r.random() < 0.3:
            seq[r.randrange(len(seq))] = r.randint(0, k)
    else:
        seq = [r.randint(0, k) for _ in range(n)]
    return list(_enc(r, seq))


def v_pal_dels(tests):
    for t in tests:
        vals, succ = t["args"]
        order, cyc = _walk(succ)
        assert not cyc and len(order) == len(vals) and 1 <= len(vals) <= 4000
        assert all(abs(v) <= 10 ** 9 for v in vals)
    assert any(t["expected"] == 0 for t in tests) and any(t["expected"] > 100 for t in tests)


CHECKS["single-deletions-leaving-palindrome-list"] = (b_pal_dels, g_pal_dels, "exact")
VALIDATE["single-deletions-leaving-palindrome-list"] = v_pal_dels
