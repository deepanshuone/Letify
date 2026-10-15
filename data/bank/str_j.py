"""Problems: strings, binary strings (flips, swaps, alternating, runs, subsequences). See data/lib.py for the registry."""
from heapq import heappop, heappush
from itertools import combinations

from lib import add, rnd, CHECKS, VALIDATE, gen_arr  # noqa: F401

TOPIC = "Strings"


def _bits(r, n, p=0.5):
    return "".join("1" if r.random() < p else "0" for _ in range(n))


def _is_bin(s, lo=1, hi=10 ** 9):
    return lo <= len(s) <= hi and set(s) <= {"0", "1"}


def _gen_bin(r, nmin=1, nmax=10):
    return _bits(r, r.randint(nmin, nmax), r.choice([0.2, 0.5, 0.8]))


# ---------------------------------------------------------------- EASY

p = add(
    id="count-substrings-of-only-ones", title="Count Substrings of Only Ones", diff="Easy", topic=TOPIC,
    fn="countOnesSubstrings", params=[("s", "string")], ret="int", cmp="exact",
    desc="<p>You are given a binary string <code>s</code> made of the characters <code>'0'</code> and <code>'1'</code>. Return how many substrings of <code>s</code> consist only of the character <code>'1'</code>.</p><p>Substrings are counted by position, so equal substrings taken from different places are counted separately. For example, in <code>s = \"1101\"</code> the answer is <code>4</code>: the single <code>1</code> at indices 0, 1 and 3, plus the substring <code>11</code> at indices 0 to 1. For <code>s = \"0110111\"</code> the answer is <code>9</code>.</p>",
    constraints=["1 &le; s.length &le; 10,000", "s contains only the characters '0' and '1'"],
    hints=["Check the substrings of <code>\"111\"</code> by hand: how many start at each position?",
           "Every substring of only ones lies inside exactly one maximal block of consecutive ones. A block of length <code>L</code> contains the same number of such substrings no matter what surrounds it.",
           "Scan left to right with a counter <code>run</code> = number of ones ending at the current index (reset to 0 on a zero). Each index contributes exactly <code>run</code> new substrings that end there."],
    editorial=["Count the substrings by their right end. If the current character is <code>'1'</code> and <code>run</code> consecutive ones end here (including this one), then exactly <code>run</code> all-ones substrings end at this index: they start at each of the last <code>run</code> positions. If the character is <code>'0'</code>, no all-ones substring can end here and the run resets.",
               "Adding <code>run</code> for every index gives the answer. Equivalently, a block of <code>L</code> ones contributes <code>L(L+1)/2</code>. The scan is O(n) time and O(1) space. The maximum answer for n = 10,000 is about 50 million, which fits a 32-bit integer."],
    time="O(n)", space="O(1)",
    solution='''def countOnesSubstrings(s):
    total = 0
    run = 0
    for c in s:
        if c == '1':
            run += 1
            total += run
        else:
            run = 0
    return total
''',
    tests=[["1101"], ["0110111"], ["1"], ["0"], ["000"], ["111"], ["1111111111"], ["10101010"], ["0001000"], ["110011100111"]],
)
_r = rnd(9701)
p["tests"].append(["1" * 10000])
p["tests"].append([_bits(_r, 8000, 0.9)])
p["tests"].append([_bits(_r, 8000, 0.5)])


def b_ones_sub(s):
    n = len(s)
    return sum(1 for i in range(n) for j in range(i + 1, n + 1) if "0" not in s[i:j])


def v_ones_sub(tests):
    for t in tests:
        assert _is_bin(t["args"][0], 1, 10000)


CHECKS["count-substrings-of-only-ones"] = (b_ones_sub, lambda r: [_gen_bin(r, 1, 12)], "exact")
VALIDATE["count-substrings-of-only-ones"] = v_ones_sub

p = add(
    id="longest-zeros-then-ones-block", title="Longest Zeros-Then-Ones Block", diff="Easy", topic=TOPIC,
    fn="longestZeroOneBlock", params=[("s", "string")], ret="int", cmp="exact",
    desc="<p>A <em>block</em> is a binary string made of <code>k</code> zeros followed immediately by exactly <code>k</code> ones, for some <code>k &ge; 1</code>. So <code>\"01\"</code>, <code>\"0011\"</code> and <code>\"000111\"</code> are blocks, while <code>\"10\"</code>, <code>\"0111\"</code> and <code>\"0101\"</code> are not.</p><p>Given a binary string <code>s</code>, return the length of the longest substring of <code>s</code> that is a block, or <code>0</code> if there is none.</p><p>For <code>s = \"01000111\"</code> the answer is <code>6</code> (the substring <code>000111</code>). For <code>s = \"1100\"</code> the answer is <code>0</code>.</p>",
    constraints=["1 &le; s.length &le; 10,000", "s contains only the characters '0' and '1'"],
    hints=["Look at the string as alternating groups of equal characters, for example <code>01000111</code> = <code>0 | 1 | 000 | 111</code>.",
           "A block must sit exactly on the boundary between a group of zeros and the group of ones right after it. It uses the end of the zero group and the start of the one group.",
           "For every group of zeros that is directly followed by a group of ones, the best block there has length <code>2 * min(zeros, ones)</code>. Take the maximum over all such pairs."],
    editorial=["Because the zeros of a block must be followed immediately by its ones, the block is contained in a pair of neighbouring groups: a maximal group of zeros and the maximal group of ones that comes right after it. Inside such a pair with sizes <code>a</code> and <code>b</code>, the zeros used must be the last <code>k</code> zeros of the first group and the ones the first <code>k</code> of the second, so the largest possible <code>k</code> is <code>min(a, b)</code>.",
               "Scan once, tracking the length of the current group and the length of the previous group. Whenever a group of ones ends (or the string ends) and the previous group was zeros, update the answer with <code>2 * min(prev, cur)</code>. Time O(n), space O(1)."],
    time="O(n)", space="O(1)",
    solution='''def longestZeroOneBlock(s):
    best = 0
    prev_zeros = 0   # size of the zero group directly before the current group (0 if none)
    cur = 0
    ch = ''
    for c in s:
        if c == ch:
            cur += 1
        else:
            if ch == '1':
                best = max(best, 2 * min(prev_zeros, cur))
            prev_zeros = cur if ch == '0' else 0
            ch = c
            cur = 1
    if ch == '1':
        best = max(best, 2 * min(prev_zeros, cur))
    return best
''',
    tests=[["01000111"], ["1100"], ["01"], ["10"], ["0"], ["1"], ["0011"], ["000111"], ["00111"], ["0001100"], ["1010101"], ["001100011100001111"]],
)
_r = rnd(9702)
p["tests"].append(["0" * 3000 + "1" * 2999 + "0" * 10 + "1" * 10])
p["tests"].append(["1" * 4000 + "0" * 4000])
p["tests"].append([_bits(_r, 8000, 0.5)])


def b_block(s):
    n = len(s)
    best = 0
    for i in range(n):
        for j in range(i + 2, n + 1, 2):
            k = (j - i) // 2
            if s[i:j] == "0" * k + "1" * k:
                best = max(best, j - i)
    return best


def v_block(tests):
    for t in tests:
        assert _is_bin(t["args"][0], 1, 10000)


CHECKS["longest-zeros-then-ones-block"] = (b_block, lambda r: [_gen_bin(r, 1, 14)], "exact")
VALIDATE["longest-zeros-then-ones-block"] = v_block

p = add(
    id="min-flips-to-alternating-bits", title="Minimum Flips to Alternating Bits", diff="Easy", topic=TOPIC,
    fn="minFlipsAlternating", params=[("s", "string")], ret="int", cmp="exact",
    desc="<p>A binary string is <em>alternating</em> when no two adjacent characters are equal, such as <code>\"0101\"</code> or <code>\"10101\"</code>. In one operation you may flip any single character (<code>'0'</code> becomes <code>'1'</code> and vice versa).</p><p>Return the minimum number of flips needed to turn <code>s</code> into an alternating string.</p><p>For example, <code>s = \"0100\"</code> needs <code>1</code> flip (change the last character to get <code>0101</code>), <code>s = \"10\"</code> needs <code>0</code>, and <code>s = \"1111\"</code> needs <code>2</code>.</p>",
    constraints=["1 &le; s.length &le; 10,000", "s contains only the characters '0' and '1'"],
    hints=["How many different alternating strings of length <code>n</code> exist?",
           "Exactly two: one starting with <code>'0'</code> (<code>0101...</code>) and one starting with <code>'1'</code> (<code>1010...</code>). The result must be one of them.",
           "The number of flips to reach a target is the number of positions where <code>s</code> differs from it. Count the mismatches with <code>0101...</code>; the mismatches with <code>1010...</code> are then <code>n</code> minus that. Return the smaller."],
    editorial=["An alternating string is fully determined by its first character, so there are only two candidates of length <code>n</code>. Each flip fixes at most one position, and every mismatching position has to be flipped, so the cost of reaching a candidate is exactly the Hamming distance to it.",
               "Count <code>m</code> = the number of indices <code>i</code> where <code>s[i]</code> differs from <code>i % 2</code> (the pattern <code>0101...</code>). Every position differs from exactly one of the two patterns, so the distance to the other pattern is <code>n - m</code>. The answer is <code>min(m, n - m)</code>, computed in O(n) time and O(1) space."],
    time="O(n)", space="O(1)",
    solution='''def minFlipsAlternating(s):
    m = 0
    for i, c in enumerate(s):
        if int(c) != i % 2:
            m += 1
    return min(m, len(s) - m)
''',
    tests=[["0100"], ["10"], ["1111"], ["0"], ["1"], ["00"], ["01"], ["010"], ["000000"], ["10101"], ["1001"], ["110100111"]],
)
_r = rnd(9703)
p["tests"].append(["01" * 4000])
p["tests"].append(["1" * 9999])
p["tests"].append([_bits(_r, 9000, 0.5)])


def b_alt_flips(s):
    n = len(s)
    best = n
    for first in "01":
        t = "".join(str((int(first) + i) % 2) for i in range(n))
        best = min(best, sum(1 for a, b in zip(s, t) if a != b))
    return best


def v_alt_flips(tests):
    for t in tests:
        assert _is_bin(t["args"][0], 1, 10000)


CHECKS["min-flips-to-alternating-bits"] = (b_alt_flips, lambda r: [_gen_bin(r, 1, 12)], "exact")
VALIDATE["min-flips-to-alternating-bits"] = v_alt_flips

# ---------------------------------------------------------------- MEDIUM

p = add(
    id="min-swaps-to-alternating-bits", title="Minimum Swaps to Alternating Bits", diff="Medium", topic=TOPIC,
    fn="minSwapsAlternating", params=[("s", "string")], ret="int", cmp="exact",
    desc="<p>You are given a binary string <code>s</code>. In one move you may pick <em>any</em> two positions (not necessarily adjacent) and swap the characters there. A string is <em>alternating</em> if no two adjacent characters are equal.</p><p>Return the minimum number of swaps that turn <code>s</code> into an alternating string, or <code>-1</code> if it cannot be done.</p><p>For example, <code>s = \"111000\"</code> needs <code>1</code> swap (swap the characters at indices 1 and 4 to get <code>101010</code>), <code>s = \"010\"</code> needs <code>0</code>, and <code>s = \"1110\"</code> gives <code>-1</code>.</p>",
    constraints=["1 &le; s.length &le; 10,000", "s contains only the characters '0' and '1'"],
    hints=["A swap does not change how many zeros and ones the string has. What do the counts of an alternating string look like?",
           "In an alternating string the counts of ones and zeros differ by at most 1. If the difference in <code>s</code> is larger, the answer is <code>-1</code>. If the counts differ by one, the more frequent character must occupy the even indices, so only one target string is possible; if equal, there are two targets.",
           "For a fixed target, count the positions where <code>s</code> differs from it. Mismatches come in pairs (a misplaced 0 and a misplaced 1), and one swap repairs one such pair, so the cost is <code>mismatches / 2</code>. Try each possible target and keep the smaller cost."],
    editorial=["First check feasibility. An alternating string of length <code>n</code> has <code>ceil(n/2)</code> and <code>floor(n/2)</code> of its two characters, so unless the number of zeros and ones differ by at most one, return <code>-1</code>.",
               "Now choose the target. If one character is strictly more frequent, it has to sit at indices 0, 2, 4, ..., which fixes the target. If the counts are equal, both <code>0101...</code> and <code>1010...</code> are possible and we take the better one.",
               "For a target <code>t</code>, let <code>d</code> be the number of indices with <code>s[i] != t[i]</code>. Since the multiset of characters equals that of <code>t</code>, the mismatches consist of exactly <code>d/2</code> positions holding a wrong '0' and <code>d/2</code> holding a wrong '1'. Swapping one of each fixes two positions, and no swap can fix more than two, so exactly <code>d/2</code> swaps are needed and sufficient. Total time O(n), space O(1)."],
    time="O(n)", space="O(1)",
    solution='''def minSwapsAlternating(s):
    n = len(s)
    ones = s.count('1')
    zeros = n - ones
    if abs(ones - zeros) > 1:
        return -1
    best = None
    for first in (0, 1):
        # target character at index i is (first + i) % 2
        ones_t = sum(1 for i in range(n) if (first + i) % 2 == 1)
        if ones_t != ones:
            continue
        d = sum(1 for i, c in enumerate(s) if int(c) != (first + i) % 2)
        if best is None or d // 2 < best:
            best = d // 2
    return best
''',
    tests=[["111000"], ["010"], ["1110"], ["0"], ["1"], ["00"], ["01"], ["0011"], ["1100"], ["000111"], ["10001"], ["1010100"], ["110100"]],
)
_r = rnd(9704)


def _balanced_shuffle(r, n, ones):
    a = ["1"] * ones + ["0"] * (n - ones)
    r.shuffle(a)
    return "".join(a)


p["tests"].append([_balanced_shuffle(_r, 8000, 4000)])
p["tests"].append([_balanced_shuffle(_r, 7999, 4000)])
p["tests"].append([_balanced_shuffle(_r, 8000, 4003)])


def b_swaps_alt(s):
    # breadth-first search over every string reachable by swaps
    n = len(s)

    def alt(t):
        return all(t[i] != t[i + 1] for i in range(n - 1))

    if alt(s):
        return 0
    seen = {s}
    frontier = [s]
    d = 0
    while frontier:
        d += 1
        nxt = []
        for t in frontier:
            for i in range(n):
                for j in range(i + 1, n):
                    if t[i] != t[j]:
                        u = list(t)
                        u[i], u[j] = u[j], u[i]
                        u = "".join(u)
                        if u not in seen:
                            if alt(u):
                                return d
                            seen.add(u)
                            nxt.append(u)
        frontier = nxt
    return -1


def v_swaps_alt(tests):
    answers = set()
    for t in tests:
        assert _is_bin(t["args"][0], 1, 10000)
        answers.add(t["expected"] == -1)
    assert answers == {True, False}


CHECKS["min-swaps-to-alternating-bits"] = (b_swaps_alt, lambda r: [_gen_bin(r, 1, 8)], "exact")
VALIDATE["min-swaps-to-alternating-bits"] = v_swaps_alt

p = add(
    id="longest-binary-subsequence-at-most-k", title="Longest Binary Subsequence Not Above K", diff="Medium", topic=TOPIC,
    fn="longestSubseqAtMost", params=[("s", "string"), ("k", "int")], ret="int", cmp="exact",
    desc="<p>You are given a binary string <code>s</code> and a positive integer <code>k</code>. Choose a subsequence of <code>s</code> (characters kept in their original order, possibly with gaps) and read it as a binary number, most significant bit first. Leading zeros are allowed, and the empty subsequence has value <code>0</code>.</p><p>Return the length of the longest subsequence whose value is at most <code>k</code>.</p><p>For example, with <code>s = \"1001010\"</code> and <code>k = 5</code> the answer is <code>5</code>: the subsequence <code>00010</code> (indices 1, 2, 4, 5, 6) has value 2. No subsequence of length 6 has value &le; 5.</p>",
    constraints=["1 &le; s.length &le; 8,000", "s contains only the characters '0' and '1'", "1 &le; k &le; 10<sup>9</sup>"],
    hints=["Leading zeros do not change a binary value, so zeros at the front of a subsequence are free. A zero further right does matter, because it shifts every bit before it.",
           "Think about the bits from the least significant end. The last character you choose has weight 1, the one before it weight 2, then 4, and so on. A chosen '1' at weight <code>w</code> adds <code>w</code> to the value.",
           "Scan <code>s</code> from right to left, keeping the current <code>value</code> and the <code>weight</code> of the next chosen character. Always take a '0'; take a '1' only if <code>value + weight &le; k</code>. Each taken character doubles the weight; a skipped '1' does not."],
    editorial=["Build the subsequence from its low-order end. The rightmost chosen character has weight 1, the next one to its left weight 2, and so on. A '0' adds nothing to the value, so taking it can never break the limit; it only pushes the weights of everything chosen later (further left) up. A '1' adds its weight.",
               "Greedy: scan <code>s</code> from right to left with <code>weight = 1</code> and <code>value = 0</code>. For a '0', take it. For a '1', take it only if <code>value + weight &le; k</code>. After taking a character, double <code>weight</code>. Once <code>weight</code> exceeds <code>k</code> no further '1' can ever fit, but zeros keep being taken (so cap the weight at <code>k + 1</code> to avoid huge numbers).",
               "Why it works: only about log<sub>2</sub>(k) &le; 30 low-order characters can contain a '1', because a '1' at a weight above <code>k</code> is never allowed. Everything chosen further left must be a '0', and those zeros cost nothing, so all of them are kept. In the low part, scanning from the right gives every chosen '1' the smallest weight it can have, so a '1' that fits is always worth taking: it adds one to the length and uses the least value possible. Time O(n), space O(1)."],
    time="O(n)", space="O(1)",
    solution='''def longestSubseqAtMost(s, k):
    length = 0
    value = 0
    weight = 1
    for c in reversed(s):
        if c == '0':
            length += 1
        elif value + weight <= k:
            value += weight
            length += 1
        else:
            continue
        if weight <= k:
            weight *= 2
    return length
''',
    tests=[["1001010", 5], ["00101001", 1], ["1", 1], ["0", 1], ["1111", 1], ["1111", 7], ["1111", 15], ["000", 1], ["10", 1], ["10", 2], ["110", 4], ["101", 4], ["1011", 8]],
)
_r = rnd(9705)
p["tests"].append([_bits(_r, 8000, 0.5), 1000000000])
p["tests"].append([_bits(_r, 8000, 0.7), 123456789])
p["tests"].append(["1" * 8000, 1000000000])

p = add(
    id="min-flips-alternating-with-rotation", title="Alternating Bits With Free Rotations", diff="Medium", topic=TOPIC,
    fn="minFlipsRotation", params=[("s", "string")], ret="int", cmp="exact",
    desc="<p>You are given a binary string <code>s</code>. You may first <em>rotate</em> it any number of times for free; one rotation moves the first character to the end (so <code>\"1100\"</code> becomes <code>\"1001\"</code>, then <code>\"0011\"</code>, and so on). After choosing how many rotations to apply, you may flip single characters (<code>'0'</code> to <code>'1'</code> or the other way) at a cost of one flip each.</p><p>Return the minimum number of flips needed so that the resulting string is alternating, meaning no two adjacent characters are equal. The result is judged as a plain string; the string is not considered circular.</p><p>For example, <code>s = \"111000\"</code> gives <code>2</code>, <code>s = \"110\"</code> gives <code>0</code> (rotate once to get <code>101</code>), and <code>s = \"0000\"</code> gives <code>2</code>.</p>",
    constraints=["1 &le; s.length &le; 8,000", "s contains only the characters '0' and '1'"],
    hints=["Without rotations the answer is <code>min(m, n - m)</code>, where <code>m</code> is the number of mismatches with <code>0101...</code>. With rotations you have <code>n</code> different strings to evaluate this for.",
           "Trying every rotation and recounting costs O(n<sup>2</sup>). To go faster, notice that every rotation of <code>s</code> appears as a window of length <code>n</code> inside <code>s + s</code>.",
           "Compare <code>s + s</code> with the fixed pattern <code>0101...</code> and build prefix sums of the mismatches. The mismatches of the window starting at <code>i</code> against <code>0101...</code> (or, for odd <code>i</code>, its complement) are then a difference of two prefix sums; take <code>min(m, n - m)</code> for each window."],
    editorial=["Every rotation of <code>s</code> is the window <code>(s + s)[i : i + n]</code> for some <code>i</code> between 0 and <code>n - 1</code>. For one window, the cost is <code>min(m, n - m)</code> where <code>m</code> is the number of positions at which the window disagrees with the pattern <code>0101...</code> started at the window's own first character.",
               "Instead of rebuilding the pattern for every window, compare <code>s + s</code> once with the global pattern <code>A[j] = j % 2</code> and let <code>mis[j]</code> be 1 when they differ. The window starting at <code>i</code> has <code>M</code> mismatches with the global pattern, which is a prefix-sum difference. If <code>i</code> is even, the window's own pattern is the global one, so <code>m = M</code>; if <code>i</code> is odd the window's own pattern is the complement of the global one and <code>m = n - M</code>. Either way <code>min(m, n - m) = min(M, n - M)</code>, so the parity of <code>i</code> does not matter.",
               "That gives an O(n) time, O(n) space algorithm (a sliding window would use O(1) extra space)."],
    time="O(n)", space="O(n)",
    solution='''def minFlipsRotation(s):
    n = len(s)
    t = s + s
    pre = [0] * (2 * n + 1)
    for j, c in enumerate(t):
        pre[j + 1] = pre[j] + (1 if int(c) != j % 2 else 0)
    best = n
    for i in range(n):
        m = pre[i + n] - pre[i]
        best = min(best, m, n - m)
    return best
''',
    tests=[["111000"], ["110"], ["0000"], ["0"], ["1"], ["01"], ["00"], ["1010"], ["0110"], ["10010"], ["1110011"], ["11111"]],
)
_r = rnd(9706)
p["tests"].append([_bits(_r, 8000, 0.5)])
p["tests"].append(["0" * 4000 + "1" * 4000])
p["tests"].append(["01" * 3999 + "11"])


def b_rot(s):
    n = len(s)
    best = n
    for r in range(n):
        t = s[r:] + s[:r]
        m = sum(1 for i, c in enumerate(t) if int(c) != i % 2)
        best = min(best, m, n - m)
    return best


def v_rot(tests):
    for t in tests:
        assert _is_bin(t["args"][0], 1, 8000)


CHECKS["min-flips-alternating-with-rotation"] = (b_rot, lambda r: [_gen_bin(r, 1, 12)], "exact")
VALIDATE["min-flips-alternating-with-rotation"] = v_rot

p = add(
    id="min-cost-to-equalize-bits-by-prefix-suffix-flips", title="Cheapest Way to Make All Bits Equal", diff="Medium", topic=TOPIC,
    fn="minCostEqualBits", params=[("s", "string")], ret="int", cmp="exact",
    desc="<p>You are given a binary string <code>s</code> of length <code>n</code> (0-indexed). Two kinds of operations are available:</p><ul><li>pick an index <code>i</code> and flip every character from index <code>0</code> to <code>i</code> inclusive, at a cost of <code>i + 1</code>;</li><li>pick an index <code>i</code> and flip every character from index <code>i</code> to <code>n - 1</code> inclusive, at a cost of <code>n - i</code>.</li></ul><p>Flipping turns <code>'0'</code> into <code>'1'</code> and <code>'1'</code> into <code>'0'</code>. Return the minimum total cost to make all characters of <code>s</code> equal (all zeros or all ones, whichever is cheaper).</p><p>For example, <code>s = \"0011\"</code> costs <code>2</code> (flip the first two characters, or the last two), and <code>s = \"010101\"</code> costs <code>9</code>.</p>",
    constraints=["1 &le; s.length &le; 10,000", "s contains only the characters '0' and '1'"],
    hints=["Look at the positions where two neighbours differ, i.e. <code>s[i-1] != s[i]</code>. If there are none, the answer is 0.",
           "Each such boundary has to be removed. A boundary between index <code>i-1</code> and <code>i</code> can be removed by flipping the whole prefix <code>[0, i-1]</code> (cost <code>i</code>) or the whole suffix <code>[i, n-1]</code> (cost <code>n - i</code>).",
           "The boundaries can be handled independently: sum <code>min(i, n - i)</code> over all indices <code>i</code> with <code>s[i-1] != s[i]</code>."],
    editorial=["Only the boundaries between different neighbours matter. Flipping a prefix or a suffix changes the equal/different relation of exactly one pair of neighbours: the pair at the cut (all other pairs are flipped together and keep their relation). So each boundary needs its own operation, and the only operations that fix the boundary between indices <code>i-1</code> and <code>i</code> are the prefix flip ending at <code>i-1</code> (cost <code>i</code>) and the suffix flip starting at <code>i</code> (cost <code>n - i</code>).",
               "Whichever flips we make, every boundary is fixed independently, and a cut at a place that is not a boundary would create a new one, so it never helps. Therefore the cost is the sum over boundaries of <code>min(i, n - i)</code>. When all pairs are equal, the characters are equal, so we are done. Time O(n), space O(1)."],
    time="O(n)", space="O(1)",
    solution='''def minCostEqualBits(s):
    n = len(s)
    total = 0
    for i in range(1, n):
        if s[i - 1] != s[i]:
            total += min(i, n - i)
    return total
''',
    tests=[["0011"], ["010101"], ["0"], ["1"], ["01"], ["10"], ["0000"], ["000111"], ["0110"], ["1001001"], ["10101"], ["1110001"]],
)
_r = rnd(9707)
p["tests"].append(["01" * 4999 + "0"])
p["tests"].append([_bits(_r, 10000, 0.5)])
p["tests"].append(["0" * 5000 + "1" * 5000])


def b_equalize(s):
    # Dijkstra over every reachable string
    n = len(s)

    def flip(t, a, b):
        return t[:a] + "".join("1" if c == "0" else "0" for c in t[a:b]) + t[b:]

    dist = {s: 0}
    heap = [(0, s)]
    while heap:
        d, t = heappop(heap)
        if d > dist[t]:
            continue
        if len(set(t)) == 1:
            return d
        for i in range(n):
            for u, c in ((flip(t, 0, i + 1), i + 1), (flip(t, i, n), n - i)):
                if d + c < dist.get(u, 10 ** 9):
                    dist[u] = d + c
                    heappush(heap, (d + c, u))


def v_equalize(tests):
    for t in tests:
        assert _is_bin(t["args"][0], 1, 10000)


CHECKS["min-cost-to-equalize-bits-by-prefix-suffix-flips"] = (b_equalize, lambda r: [_gen_bin(r, 1, 8)], "exact")
VALIDATE["min-cost-to-equalize-bits-by-prefix-suffix-flips"] = v_equalize

p = add(
    id="max-binary-string-by-pair-rewrites", title="Largest Binary String After Rewrites", diff="Medium", topic=TOPIC,
    fn="maxBinaryString", params=[("s", "string")], ret="string", cmp="exact",
    desc="<p>You are given a binary string <code>s</code>. You may apply the following two rewrite rules any number of times, in any order:</p><ul><li>if <code>s</code> contains <code>\"00\"</code>, replace one occurrence of it by <code>\"10\"</code>;</li><li>if <code>s</code> contains <code>\"10\"</code>, replace one occurrence of it by <code>\"01\"</code>.</li></ul><p>Return the largest string you can reach, comparing strings as binary numbers (all reachable strings have the same length, so this is the same as lexicographic order). Doing nothing is allowed.</p><p>For example, <code>\"000110\"</code> can become <code>\"111011\"</code>, <code>\"01\"</code> stays <code>\"01\"</code>, and <code>\"1100\"</code> becomes <code>\"1110\"</code>.</p>",
    constraints=["1 &le; s.length &le; 10,000", "s contains only the characters '0' and '1'"],
    hints=["Leading ones can never be improved, and a string without any zero is already the largest possible. Focus on what happens from the first zero onwards.",
           "The second rule moves a zero one step <em>left</em> past a one (the string gets smaller), but it lets you gather all zeros into one block. The first rule then turns pairs of neighbouring zeros in that block into a one and a zero, which makes the string larger.",
           "Let <code>p</code> be the index of the first zero and <code>z</code> the number of zeros in the whole string. Look at the quantity <em>(index of the first zero) + (number of zeros)</em>: no rule can increase it. The best you can reach is a single zero at index <code>p + z - 1</code>, with ones everywhere else."],
    editorial=["If the string has no zero, it is already all ones. Otherwise let <code>p</code> be the index of the first zero and <code>z</code> the total number of zeros in <code>s</code> (all of them sit at or after <code>p</code>). The <code>p</code> characters before the first zero are ones and stay that way.",
               "Construction: use <code>10 -> 01</code> to slide every zero left until all <code>z</code> zeros form a block starting at index <code>p</code>, followed only by ones. Then apply <code>00 -> 10</code> to the first two zeros of the block, again and again: <code>0 0 0 -> 1 0 0 -> 1 1 0</code>. After <code>z - 1</code> applications the block has become <code>z - 1</code> ones and a single zero, giving <code>'1' * (p + z - 1) + '0' + '1' * (n - p - z)</code>.",
               "Why nothing is larger: consider <code>f</code> = (index of the first zero) + (number of zeros). Rule 1 applied at the first zero raises the index by one and removes one zero, so <code>f</code> stays the same; rule 1 anywhere else removes a zero, so <code>f</code> drops; rule 2 never changes the number of zeros and cannot move the first zero to the right, so <code>f</code> does not grow. There is always at least one zero (the rules never remove the last one), so the first zero ends at index at most <code>f - 1 = p + z - 1</code>. The string with ones everywhere except that single zero is the largest possible. Time O(n), space O(n) for the output."],
    time="O(n)", space="O(n)",
    solution='''def maxBinaryString(s):
    p = s.find('0')
    if p < 0:
        return s
    n = len(s)
    z = s.count('0')
    return '1' * (p + z - 1) + '0' + '1' * (n - p - z)
''',
    tests=[["000110"], ["01"], ["10"], ["1100"], ["0"], ["1"], ["00"], ["111"], ["0101"], ["1011001"], ["110100"], ["0000"]],
    tier="extra",
)
_r = rnd(9708)
p["tests"].append([_bits(_r, 8000, 0.5)])
p["tests"].append(["1" * 3000 + "0" * 1000 + "1" * 3000])
p["tests"].append(["0" * 6000 + "1" * 2000])


def b_maxbin(s):
    seen = {s}
    stack = [s]
    while stack:
        t = stack.pop()
        for i in range(len(t) - 1):
            pair = t[i:i + 2]
            if pair == "00":
                u = t[:i] + "10" + t[i + 2:]
            elif pair == "10":
                u = t[:i] + "01" + t[i + 2:]
            else:
                continue
            if u not in seen:
                seen.add(u)
                stack.append(u)
    return max(seen)


def v_maxbin(tests):
    for t in tests:
        s = t["args"][0]
        assert _is_bin(s, 1, 10000)
        assert len(t["expected"]) == len(s)


CHECKS["max-binary-string-by-pair-rewrites"] = (b_maxbin, lambda r: [_gen_bin(r, 1, 10)], "exact")
VALIDATE["max-binary-string-by-pair-rewrites"] = v_maxbin

p = add(
    id="min-pieces-of-powers-of-five", title="Split Into Powers of Five", diff="Medium", topic=TOPIC,
    fn="minPiecesPowersOfFive", params=[("s", "string")], ret="int", cmp="exact",
    desc="<p>You are given a binary string <code>s</code>. Split <code>s</code> into consecutive pieces (every character belongs to exactly one piece) so that each piece, read as a binary number, is a power of 5 (<code>1, 5, 25, 125, ...</code>) and has no leading zeros.</p><p>Return the minimum number of pieces needed, or <code>-1</code> if no valid split exists.</p><p>For example, <code>s = \"1011\"</code> gives <code>2</code> (<code>101</code> and <code>1</code>), <code>s = \"11001\"</code> gives <code>1</code> because <code>11001</code> is 25, and <code>s = \"0\"</code> gives <code>-1</code>.</p>",
    constraints=["1 &le; s.length &le; 1,000", "s contains only the characters '0' and '1'"],
    hints=["Every piece must start with '1' (no leading zeros), and a piece can only be one of a small known set of strings.",
           "Powers of five up to <code>n</code> bits are few: 5<sup>k</sup> has about 2.32 &middot; k bits, so there are fewer than <code>n / 2</code> of them. Write down their binary forms.",
           "Let <code>dp[i]</code> be the minimum number of pieces for the first <code>i</code> characters. From each reachable position <code>i</code> with <code>s[i] == '1'</code>, try every power-of-five string that matches <code>s</code> at <code>i</code> and update <code>dp[i + len]</code>."],
    editorial=["This is a shortest-partition DP. Let <code>dp[i]</code> be the least number of pieces into which the prefix of length <code>i</code> can be split, with <code>dp[0] = 0</code> and infinity for everything unreachable. The answer is <code>dp[n]</code> (or -1 if it stays infinite).",
               "The pieces come from a fixed dictionary: the binary forms of 1, 5, 25, 125, ... up to length <code>n</code>. Because the bit lengths of consecutive powers are strictly increasing, there are at most about <code>0.43 n</code> of them (around 430 for n = 1000), and each has no leading zero. For each reachable position <code>i</code> we test every dictionary word with <code>s.startswith(word, i)</code> and relax <code>dp[i + len(word)]</code>.",
               "There are D &asymp; 0.43 n words, so the DP does O(n &middot; D) startswith tests, each of which usually fails after a few characters, which is fast for n = 1000. Positions holding '0' can never start a piece and are skipped immediately."],
    time="O(n * D) comparisons, D = number of powers of 5 with at most n bits", space="O(n)",
    solution='''def minPiecesPowersOfFive(s):
    n = len(s)
    words = []
    x = 1
    while x.bit_length() <= n:
        words.append(bin(x)[2:])
        x *= 5
    INF = n + 1
    dp = [INF] * (n + 1)
    dp[0] = 0
    for i in range(n):
        if dp[i] == INF or s[i] == '0':
            continue
        for w in words:
            j = i + len(w)
            if j > n:
                break
            if dp[i] + 1 < dp[j] and s.startswith(w, i):
                dp[j] = dp[i] + 1
    return dp[n] if dp[n] < INF else -1
''',
    tests=[["1011"], ["11001"], ["0"], ["1"], ["111"], ["101101"], ["10"], ["1001"], ["1111101"], ["110010011111"], ["101110011"], ["0101"]],
)
_r = rnd(9709)


def _pow5_concat(r, length):
    words = []
    x = 1
    while x.bit_length() <= 200:
        words.append(bin(x)[2:])
        x *= 5
    out = ""
    while True:
        w = r.choice(words) if r.random() < 0.6 else r.choice(words[:4])
        if len(out) + len(w) > length:
            break
        out += w
    return out


p["tests"].append([_pow5_concat(_r, 990)])
p["tests"].append(["1" * 1000])
p["tests"].append([_pow5_concat(_r, 600) + "0" + _pow5_concat(_r, 300)])
p["tests"].append(["101" * 330 + "1"])


def b_pow5(s):
    def is_pow5(t):
        if t[0] == "0":
            return False
        v = int(t, 2)
        while v % 5 == 0:
            v //= 5
        return v == 1

    n = len(s)
    best = [None]

    def rec(i, cnt):
        if i == n:
            if best[0] is None or cnt < best[0]:
                best[0] = cnt
            return
        for j in range(i + 1, n + 1):
            if is_pow5(s[i:j]):
                rec(j, cnt + 1)

    rec(0, 0)
    return -1 if best[0] is None else best[0]


def g_pow5(r):
    if r.random() < 0.5:
        return _pow5_concat(r, r.randint(1, 16)) or "1"
    return _gen_bin(r, 1, 12)


def v_pow5(tests):
    seen = set()
    for t in tests:
        assert _is_bin(t["args"][0], 1, 1000)
        seen.add(t["expected"] == -1)
    assert seen == {True, False}


CHECKS["min-pieces-of-powers-of-five"] = (b_pow5, lambda r: [g_pow5(r)], "exact")
VALIDATE["min-pieces-of-powers-of-five"] = v_pow5

# ---------------------------------------------------------------- HARD

p = add(
    id="min-time-to-clear-flagged-cars", title="Clear the Flagged Cars", diff="Hard", topic=TOPIC,
    fn="minTimeClearFlagged", params=[("s", "string")], ret="int", cmp="exact",
    desc="<p>A train is a row of cars described by a binary string <code>s</code>: <code>s[i] = '1'</code> means car <code>i</code> carries contraband, and <code>'0'</code> means it does not. You must remove all cars that carry contraband (cars without contraband may stay or go). Three kinds of actions are available:</p><ul><li>remove the leftmost remaining car, in 1 minute;</li><li>remove the rightmost remaining car, in 1 minute;</li><li>remove any single remaining car, wherever it is, in 2 minutes.</li></ul><p>Return the minimum number of minutes needed to get rid of every car that carries contraband.</p><p>For example, <code>s = \"1100101\"</code> needs <code>5</code> minutes (remove the first two cars from the left, then the last three cars from the right; the zeros in the middle may stay) and <code>s = \"0010\"</code> needs <code>2</code> minutes.</p>",
    constraints=["1 &le; s.length &le; 8,000", "s contains only the characters '0' and '1'"],
    hints=["Whatever you do, the cars removed from the left end form a prefix and the cars removed from the right end form a suffix; the cars removed from the middle are the only ones that cost 2 each.",
           "Split the train at a cut point <code>i</code>. Clear the part <code>s[0:i]</code> as cheaply as possible using left removals and middle removals, and clear <code>s[i:]</code> using right removals and middle removals. Then minimise over <code>i</code>.",
           "Let <code>left[i]</code> be the best cost for the first <code>i</code> cars: <code>left[i] = min(left[i-1] + (2 if s[i-1] == '1' else 0), i)</code> (either handle the last car on its own, or remove all <code>i</code> from the left). Build <code>right[i]</code> symmetrically and take <code>min(left[i] + right[i])</code>."],
    editorial=["Any plan removes some cars from the left end, some from the right end and some from the middle. The left-end removals are a prefix <code>s[0:a]</code>, the right-end removals a suffix <code>s[b:]</code>, and each flagged car between them costs 2. Unflagged cars in the middle can simply stay. So the plan costs <code>a + (n - b) + 2 * (flagged cars in [a, b))</code>.",
               "Define <code>left[i]</code> as the cheapest way to clear the flagged cars of the prefix <code>s[0:i]</code> when only left-end and middle removals are available. Either strip the entire prefix from the left (cost <code>i</code>), or leave the last car <code>i-1</code> to a middle removal (cost 2 if it is flagged, 0 otherwise) and solve the shorter prefix: <code>left[i] = min(i, left[i-1] + (2 if s[i-1] == '1' else 0))</code>. In the same way <code>right[i] = min(n - i, right[i+1] + (2 if s[i] == '1' else 0))</code> for the suffix <code>s[i:]</code>.",
               "A cut at <code>i</code> splits the work between the two sides, so the answer is the minimum over <code>i</code> from 0 to <code>n</code> of <code>left[i] + right[i]</code>. For <code>\"1100101\"</code> the best cut leaves 5 minutes: clear the first two cars from the left (2 minutes) and the last three cars from the right (3 minutes); the zeros in the middle can stay. Time O(n), space O(n)."],
    time="O(n)", space="O(n)",
    solution='''def minTimeClearFlagged(s):
    n = len(s)
    left = [0] * (n + 1)
    for i in range(1, n + 1):
        left[i] = min(i, left[i - 1] + (2 if s[i - 1] == '1' else 0))
    right = [0] * (n + 1)
    for i in range(n - 1, -1, -1):
        right[i] = min(n - i, right[i + 1] + (2 if s[i] == '1' else 0))
    return min(left[i] + right[i] for i in range(n + 1))
''',
    tests=[["1100101"], ["0010"], ["1"], ["0"], ["11111"], ["00000"], ["10001"], ["0110"], ["1010101"], ["0001000"], ["1001001001"], ["110001000011"]],
    tier="extra",
)
_r = rnd(9710)
p["tests"].append([_bits(_r, 8000, 0.5)])
p["tests"].append([_bits(_r, 8000, 0.05)])
p["tests"].append(["1" * 100 + "0" * 7800 + "1" * 100])


def b_cars(s):
    n = len(s)
    flagged = 0
    for i, c in enumerate(s):
        if c == "1":
            flagged |= 1 << i
    full = (1 << n) - 1
    dist = {full: 0}
    heap = [(0, full)]
    while heap:
        d, m = heappop(heap)
        if d > dist[m]:
            continue
        if m & flagged == 0:
            return d
        low = m & -m
        high = 1 << (m.bit_length() - 1)
        opts = [(m ^ low, 1), (m ^ high, 1)]
        for i in range(n):
            if m >> i & 1:
                opts.append((m ^ (1 << i), 2))
        for u, c in opts:
            if d + c < dist.get(u, 10 ** 9):
                dist[u] = d + c
                heappush(heap, (d + c, u))


def v_cars(tests):
    for t in tests:
        assert _is_bin(t["args"][0], 1, 8000)


CHECKS["min-time-to-clear-flagged-cars"] = (b_cars, lambda r: [_gen_bin(r, 1, 9)], "exact")
VALIDATE["min-time-to-clear-flagged-cars"] = v_cars

p = add(
    id="count-dominant-ones-substrings", title="Count Substrings With Dominant Ones", diff="Hard", topic=TOPIC,
    fn="countDominantOnes", params=[("s", "string")], ret="int", cmp="exact",
    desc="<p>You are given a binary string <code>s</code>. Call a substring <em>dominant</em> if the number of ones in it is at least the <em>square</em> of the number of zeros in it. A substring with no zeros is therefore always dominant.</p><p>Return how many substrings of <code>s</code> are dominant. Substrings are counted by position, so equal substrings at different places count separately.</p><p>For example, <code>s = \"00011\"</code> gives <code>5</code> (the substrings <code>1</code>, <code>1</code>, <code>11</code>, <code>01</code> and <code>011</code>), and <code>s = \"101101\"</code> gives <code>16</code>.</p>",
    constraints=["1 &le; s.length &le; 4,000", "s contains only the characters '0' and '1'"],
    hints=["Checking all O(n<sup>2</sup>) substrings with prefix sums is fine for small n. For bigger n, find something that limits the interesting cases.",
           "If a substring has <code>z</code> zeros it needs at least <code>z<sup>2</sup></code> ones, so its length is at least <code>z + z<sup>2</sup></code>. Hence <code>z</code> can be at most about <code>sqrt(n)</code>.",
           "Fix the left end <code>l</code> and the number of zeros <code>z &le; sqrt(n)</code>. The right ends with exactly <code>z</code> zeros form a contiguous range (between two consecutive zero positions). Inside that range the condition becomes a lower bound on the length, so you can count the valid right ends with arithmetic."],
    editorial=["Let <code>z</code> and <code>o</code> be the zeros and ones of a substring; it is dominant if <code>o &ge; z<sup>2</sup></code>, i.e. if its length <code>L = z + o</code> satisfies <code>L &ge; z<sup>2</sup> + z</code>. Since <code>L &le; n</code>, only substrings with <code>z</code> up to about <code>sqrt(n)</code> (roughly 63 for n = 4000) can qualify.",
               "Collect the positions of the zeros in a list <code>Z</code>. For a left end <code>l</code> let <code>zi</code> be the number of zeros before <code>l</code>. The right ends <code>r</code> that give exactly <code>z</code> zeros lie in the interval <code>[a, b]</code>, where <code>a = l</code> if <code>z = 0</code> and <code>a = Z[zi + z - 1]</code> otherwise, and <code>b = Z[zi + z] - 1</code> (or <code>n - 1</code> if there is no such zero). Inside that interval the number of zeros is fixed, so the condition is simply <code>r - l + 1 &ge; z<sup>2</sup> + z</code>, i.e. <code>r &ge; l + z<sup>2</sup> + z - 1</code>. The number of valid right ends is the size of <code>[max(a, l + z<sup>2</sup> + z - 1), b]</code> if it is non-empty.",
               "Looping over every <code>l</code> and every <code>z</code> with <code>z<sup>2</sup> + z &le; n - l</code> costs O(n &middot; sqrt(n)) with O(1) work per pair. This is far better than O(n<sup>2</sup>) and about 234,000 steps for n = 5000."],
    time="O(n * sqrt(n))", space="O(n)",
    solution='''def countDominantOnes(s):
    n = len(s)
    Z = [i for i, c in enumerate(s) if c == '0']
    m = len(Z)
    total = 0
    zi = 0  # zeros strictly before l
    for l in range(n):
        k = 0
        while True:
            need = l + k * k + k - 1
            if need >= n:
                break
            if k == 0:
                a = l
            else:
                if zi + k - 1 >= m:
                    break
                a = Z[zi + k - 1]
            b = Z[zi + k] - 1 if zi + k < m else n - 1
            lo = need if need > a else a
            if lo <= b:
                total += b - lo + 1
            k += 1
        if s[l] == '0':
            zi += 1
    return total
''',
    tests=[["00011"], ["101101"], ["0"], ["1"], ["00"], ["11"], ["01"], ["10"], ["0000"], ["0110"], ["1011011"], ["000111000111"], ["100100100"]],
    tier="extra",
)
_r = rnd(9711)
p["tests"].append([_bits(_r, 4000, 0.5)])
p["tests"].append([_bits(_r, 4000, 0.85)])
p["tests"].append(["1" * 4000])


def b_dominant(s):
    n = len(s)
    cnt = 0
    for i in range(n):
        z = 0
        for j in range(i, n):
            if s[j] == "0":
                z += 1
            if (j - i + 1 - z) >= z * z:
                cnt += 1
    return cnt


def v_dominant(tests):
    for t in tests:
        assert _is_bin(t["args"][0], 1, 4000)


CHECKS["count-dominant-ones-substrings"] = (b_dominant, lambda r: [_gen_bin(r, 1, 30)], "exact")
VALIDATE["count-dominant-ones-substrings"] = v_dominant


def b_subseq_k(s, k):
    n = len(s)
    best = 0
    for mask in range(1 << n):
        sub = "".join(s[i] for i in range(n) if mask >> i & 1)
        if (int(sub, 2) if sub else 0) <= k:
            best = max(best, len(sub))
    return best


def g_subseq_k(r):
    s = _gen_bin(r, 1, 11)
    return [s, r.choice([r.randint(1, 8), r.randint(1, 60), r.randint(1, 3000)])]


def v_subseq_k(tests):
    for t in tests:
        s, k = t["args"]
        assert _is_bin(s, 1, 8000) and 1 <= k <= 10 ** 9


CHECKS["longest-binary-subsequence-at-most-k"] = (b_subseq_k, g_subseq_k, "exact")
VALIDATE["longest-binary-subsequence-at-most-k"] = v_subseq_k
