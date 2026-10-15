"""Problems: backtracking, partitioning strings and arrays. See data/lib.py for the registry."""
from bisect import bisect_left
from collections import Counter
from itertools import combinations, combinations_with_replacement, product as _product

from lib import add, rnd, CHECKS, VALIDATE, gen_arr  # noqa: F401

T = "Backtracking"


# ================================================================== EASY

# ---------------------------------------------------------------- palindromic cut points
p = add(
    id="palindromic-cut-points", title="Palindromic Cut Points", diff="Easy", topic=T, tier="extra",
    fn="countPalindromicCuts", params=[("s", "string")], ret="int", cmp="exact",
    desc="<p>A <em>cut point</em> of a string <code>s</code> is a position between two neighbouring characters; a string of length <code>n</code> has <code>n - 1</code> of them. Cutting at a point splits <code>s</code> into a non-empty left part and a non-empty right part.</p><p>Return how many cut points produce two parts that are <strong>both palindromes</strong>.</p><p>For example, <code>\"aab\"</code> has one such cut point (<code>aa|b</code>), while <code>\"aaa\"</code> has two (<code>a|aa</code> and <code>aa|a</code>) and <code>\"abc\"</code> has none.</p>",
    constraints=["2 &le; s.length &le; 3,000", "s consists of lowercase English letters"],
    hints=["There are only <code>n - 1</code> cut points. For each one you just need to decide whether two pieces are palindromes.",
           "A piece is a palindrome when it reads the same as its reverse. Compare <code>s[:i]</code> and <code>s[i:]</code> with their reversals.",
           "Checking a piece costs O(n), so the total is O(n<sup>2</sup>), which is fine for n &le; 3,000. This is exactly the first decision of a palindrome partition: the first piece must be a palindrome, and the rest must be partitionable too."],
    editorial=["Try every cut point <code>i</code> from 1 to <code>n - 1</code>. The left part is <code>s[:i]</code> and the right part is <code>s[i:]</code>. A string is a palindrome when it equals its own reverse, so count the cut points where both parts pass this test.",
               "Each test costs O(n) and there are n - 1 cut points, so the running time is O(n<sup>2</sup>) with O(n) extra memory for the slices. A linear solution exists (find all palindromic prefixes and suffixes with a prefix-function or Manacher pass), but it is not needed for these limits.",
               "This tiny problem is the building block of palindrome partitioning: a partition is a sequence of cuts in which every piece is a palindrome, and the harder problems below ask you to count or list them."],
    time="O(n^2)", space="O(n)",
    solution='''def countPalindromicCuts(s):
    n = len(s)
    count = 0
    for i in range(1, n):
        a = s[:i]
        b = s[i:]
        if a == a[::-1] and b == b[::-1]:
            count += 1
    return count
''',
    tests=[["aab"], ["aaa"], ["abc"], ["aa"], ["ab"], ["abba"], ["aabaa"], ["abacaba"], ["abaaba"], ["aabbaa"],
           ["abcdcbaxyzzyx"], ["abababab"], ["zzyzzxzz"]],
)
_r = rnd(8101)
p["tests"].append(["a" * 3000])
p["tests"].append(["".join(_r.choice("ab") for _ in range(3000))])
_h = "".join(_r.choice("abc") for _ in range(1400))
p["tests"].append([_h + _h[::-1] + "x" + "yy"])
p["tests"].append(["ab" * 1500])


def b_cuts(s):
    def pal(t):
        i, j = 0, len(t) - 1
        while i < j:
            if t[i] != t[j]:
                return False
            i += 1
            j -= 1
        return True
    return sum(1 for i in range(1, len(s)) if pal(s[:i]) and pal(s[i:]))


def g_cuts(r):
    mode = r.randint(0, 2)
    if mode == 0:
        return ["".join(r.choice("ab") for _ in range(r.randint(2, 12)))]
    if mode == 1:
        h = "".join(r.choice("ab") for _ in range(r.randint(1, 5)))
        a = h + r.choice(["", "a", "b"]) + h[::-1]
        h2 = "".join(r.choice("ab") for _ in range(r.randint(1, 4)))
        b = h2 + r.choice(["", "a"]) + h2[::-1]
        return [a + b]
    return ["".join(r.choice("abc") for _ in range(r.randint(2, 10)))]


def v_cuts(tests):
    for t in tests:
        s = t["args"][0]
        assert 2 <= len(s) <= 3000 and s.isalpha() and s.islower() and s.isascii()


CHECKS["palindromic-cut-points"] = (b_cuts, g_cuts, "exact")
VALIDATE["palindromic-cut-points"] = v_cuts


# ---------------------------------------------------------------- equal-sum team assignments
p = add(
    id="equal-sum-team-assignments", title="Equal-Sum Team Assignments", diff="Easy", topic=T, tier="extra",
    fn="countBalancedAssignments", params=[("skills", "int[]")], ret="int", cmp="exact",
    desc="<p>A group of <code>n</code> players with skill values <code>skills[i]</code> must be divided into <strong>Team A</strong> and <strong>Team B</strong>: every player joins exactly one of the two teams, and either team may be empty. A split is <em>balanced</em> when both teams have the same total skill.</p><p>Players are told apart by position, even when their skills are equal, and the teams are labelled, so swapping which team is called A and which is called B gives a different assignment. Return the number of balanced assignments.</p><p>For example, <code>[1, 1, 2, 2]</code> has 4 balanced assignments: Team A must hold one player of skill 1 and one of skill 2 (2 &times; 2 ways), and Team B gets the rest.</p>",
    constraints=["1 &le; skills.length &le; 20", "1 &le; skills[i] &le; 100"],
    hints=["Giving every player to A or B is a binary choice per player, so there are 2<sup>n</sup> assignments. With n &le; 20 that is about a million; can you enumerate them?",
           "Team A and Team B have equal totals exactly when Team A's total is half of the grand total. If the grand total is odd, the answer is 0.",
           "Count the subsets (by position) whose sum is <code>total / 2</code>. A recursion that takes or skips each player works; so does a table <code>ways[s]</code> updated player by player."],
    editorial=["Let <code>total</code> be the sum of all skills. An assignment is balanced exactly when Team A's sum equals <code>total / 2</code> (then Team B's sum is automatically the same). So the answer is the number of subsets of positions whose sum is <code>total / 2</code>, and it is 0 if <code>total</code> is odd. Because teams are labelled, each such subset is one assignment (A = the subset), and its complement is a different assignment counted separately.",
               "The direct backtracking solution takes or skips each player and counts the paths that end with the target sum: 2<sup>20</sup> leaves at worst. Pruning by the running sum already helps, since all skills are positive.",
               "A faster solution replaces the recursion by a table: <code>ways[s]</code> is the number of subsets seen so far with sum <code>s</code>. For each skill <code>x</code>, update <code>s</code> from high to low with <code>ways[s] += ways[s - x]</code>. The answer is <code>ways[total / 2]</code>. That is O(n &middot; total)."],
    time="O(n &middot; total)", space="O(total)",
    solution='''def countBalancedAssignments(skills):
    total = sum(skills)
    if total % 2:
        return 0
    half = total // 2
    ways = [0] * (half + 1)
    ways[0] = 1
    for x in skills:
        for s in range(half, x - 1, -1):
            ways[s] += ways[s - x]
    return ways[half]
''',
    tests=[[[1, 1, 2, 2]], [[3, 1, 2]], [[5]], [[2, 2]], [[1, 2]], [[4, 4, 4]], [[1, 1, 1, 1]], [[100] * 20], [[1] * 20],
           [[7, 3, 2, 5, 8]], [[10, 20, 30, 40, 50, 60, 70, 80]], [[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]]],
)
_r = rnd(8102)
p["tests"].append([[_r.randint(1, 100) for _ in range(20)]])
p["tests"].append([[_r.randint(1, 4) for _ in range(20)]])


def b_teams(skills):
    n = len(skills)
    total = sum(skills)
    c = 0
    for mask in range(1 << n):
        a = sum(skills[i] for i in range(n) if mask >> i & 1)
        if a * 2 == total:
            c += 1
    return c


def v_teams(tests):
    for t in tests:
        a = t["args"][0]
        assert 1 <= len(a) <= 20 and all(1 <= x <= 100 for x in a)
        assert 0 <= t["expected"] <= 2 ** len(a)


CHECKS["equal-sum-team-assignments"] = (b_teams, lambda r: [gen_arr(r, 1, r.choice([2, 5, 20]), 1, 10)], "exact")
VALIDATE["equal-sum-team-assignments"] = v_teams


# ================================================================== MEDIUM

# ---------------------------------------------------------------- all palindrome partitions
p = add(
    id="palindrome-partition-layouts", title="Palindrome Partitions", diff="Medium", topic=T, tier="must",
    fn="palindromePartitions", params=[("s", "string")], ret="int[][]", cmp="rowset",
    desc="<p>Cut the string <code>s</code> into consecutive non-empty pieces so that <strong>every piece is a palindrome</strong>. Return all possible ways to do this.</p><p>Describe one way by the <em>lengths</em> of its pieces from left to right (the lengths add up to <code>s.length</code>). For <code>\"aab\"</code> the answer is <code>[[1, 1, 1], [2, 1]]</code>, meaning <code>a|a|b</code> and <code>aa|b</code>. Different ways are different rows, and no way appears twice. The rows may be returned in any order.</p>",
    constraints=["1 &le; s.length &le; 12", "s consists of lowercase English letters"],
    hints=["Decide the first piece, then solve the same problem for the rest of the string. Which first pieces are allowed?",
           "Recurse on a start index <code>i</code>. For every end index <code>j &ge; i</code> such that <code>s[i..j]</code> is a palindrome, record the length <code>j - i + 1</code>, recurse from <code>j + 1</code>, then undo the choice. When <code>i</code> reaches <code>n</code>, store a copy of the lengths.",
           "Do not re-test palindromes from scratch every time: precompute <code>pal[i][j]</code> with <code>pal[i][j] = (s[i] == s[j]) and pal[i+1][j-1]</code> (a length 1 or 2 range needs only the first part)."],
    editorial=["This is the standard \"choose the next piece\" backtracking. The state is the index <code>i</code> where the next piece starts and the list of piece lengths chosen so far. For each <code>j</code> from <code>i</code> to <code>n - 1</code>, if <code>s[i..j]</code> is a palindrome, push <code>j - i + 1</code>, recurse on <code>j + 1</code> and pop. Reaching <code>i == n</code> means the whole string has been consumed, so a copy of the current list is one complete answer.",
               "A palindrome table filled in O(n<sup>2</sup>) removes the repeated palindrome checks. The cost is then proportional to the output: a string such as <code>aaaa...a</code> has 2<sup>n-1</sup> partitions (every cut can be chosen or not), so the worst case is O(n &middot; 2<sup>n</sup>) time for writing the answers.",
               "Since a partition is completely described by its cut positions, using piece lengths as the encoding makes rows unique and easy to compare."],
    time="O(n &middot; 2<sup>n</sup>)", space="O(n<sup>2</sup>) for the table plus the output",
    solution='''def palindromePartitions(s):
    n = len(s)
    pal = [[False] * n for _ in range(n)]
    for i in range(n - 1, -1, -1):
        for j in range(i, n):
            pal[i][j] = s[i] == s[j] and (j - i < 2 or pal[i + 1][j - 1])
    res = []
    cur = []

    def go(i):
        if i == n:
            res.append(cur[:])
            return
        for j in range(i, n):
            if pal[i][j]:
                cur.append(j - i + 1)
                go(j + 1)
                cur.pop()

    go(0)
    return res
''',
    tests=[["aab"], ["a"], ["ab"], ["aaa"], ["abba"], ["racecar"], ["abcba"], ["abc"], ["aabbaa"], ["abababab"],
           ["aaaaaaaaaaaa"], ["abaabaabaaba"], ["aabaabaabaab"]],
)


def b_ppl(s):
    n = len(s)
    out = []
    for mask in range(1 << (n - 1)):
        cuts = [0] + [i + 1 for i in range(n - 1) if mask >> i & 1] + [n]
        pieces = [s[cuts[k]:cuts[k + 1]] for k in range(len(cuts) - 1)]
        if all(x == x[::-1] for x in pieces):
            out.append([len(x) for x in pieces])
    return out


def g_ppl(r):
    mode = r.randint(0, 1)
    if mode == 0:
        return ["".join(r.choice("ab") for _ in range(r.randint(1, 9)))]
    return ["".join(r.choice("abc") for _ in range(r.randint(1, 8)))]


def v_ppl(tests):
    for t in tests:
        s = t["args"][0]
        assert 1 <= len(s) <= 12 and s.isalpha() and s.islower() and s.isascii()
        rows = t["expected"]
        assert len(set(map(tuple, rows))) == len(rows) and rows
        for row in rows:
            assert sum(row) == len(s)


CHECKS["palindrome-partition-layouts"] = (b_ppl, g_ppl, "rowset")
VALIDATE["palindrome-partition-layouts"] = v_ppl


# ---------------------------------------------------------------- restore ip addresses
p = add(
    id="restore-ip-address-octets", title="Restore IP Addresses", diff="Medium", topic=T, tier="common",
    fn="restoreIpAddresses", params=[("digits", "string")], ret="int[][]", cmp="rowset",
    desc="<p>The dots of an IPv4 address were erased, leaving only a string of digits. Insert exactly three dots into <code>digits</code> (never changing the order of the digits and never dropping one) to rebuild every valid IPv4 address.</p><p>An address has four parts. Each part is a decimal number from <code>0</code> to <code>255</code> written <strong>without leading zeros</strong> (the part <code>0</code> is fine, but <code>01</code> or <code>00</code> are not).</p><p>Return each valid address as a row of its four numbers, for example <code>[255, 255, 11, 135]</code>. Rows may be in any order.</p>",
    constraints=["1 &le; digits.length &le; 20", "digits consists only of the characters 0-9"],
    hints=["You must choose where the three dots go, so choose the four parts one after another. How long can a part be?",
           "A part has 1 to 3 digits. Try each length, reject it if it is longer than 1 digit and starts with 0, or if its value is above 255, and recurse for the next part.",
           "Prune with lengths: after choosing some parts, the remaining digits must fit the remaining parts, which need between 1 and 3 digits each. The whole string has to be used exactly."],
    editorial=["Recurse on the start index of the next part and the parts chosen so far. When four parts are placed, accept only if the whole string has been used. Otherwise try part lengths 1, 2 and 3: stop trying longer lengths as soon as the part would run past the end of the string, starts with <code>0</code> and has more than one digit, or has a value above 255.",
               "A simple length check prunes most dead branches early: with <code>r</code> parts still to place and <code>m</code> digits left, you need <code>r &le; m &le; 3r</code>. There are at most 3<sup>4</sup> = 81 ways to pick the four lengths, so the search is constant time, O(1), for any input.",
               "Because a part has no leading zeros, the numeric row identifies the written address uniquely, so no two rows are equal."],
    time="O(1)", space="O(1)",
    solution='''def restoreIpAddresses(digits):
    n = len(digits)
    res = []
    cur = []

    def go(i):
        k = len(cur)
        if k == 4:
            if i == n:
                res.append(cur[:])
            return
        rem = 4 - k
        if n - i < rem or n - i > 3 * rem:
            return
        for length in (1, 2, 3):
            if i + length > n:
                break
            part = digits[i:i + length]
            if length > 1 and part[0] == "0":
                break
            v = int(part)
            if v > 255:
                break
            cur.append(v)
            go(i + length)
            cur.pop()

    go(0)
    return res
''',
    tests=[["25525511135"], ["0000"], ["1111"], ["101023"], ["999"], ["1"], ["010010"], ["255255255255"], ["256256256256"],
           ["00000"], ["1921681"], ["172162541"], ["0279245587303"], ["11111111111111111111"], ["123456789012"], ["100100100100"]],
)


def b_ip(s):
    n = len(s)
    out = []
    for a in range(1, n):
        for b in range(a + 1, n):
            for c in range(b + 1, n):
                parts = [s[:a], s[a:b], s[b:c], s[c:]]
                if all(str(int(x)) == x and 0 <= int(x) <= 255 for x in parts):
                    out.append([int(x) for x in parts])
    return out


def g_ip(r):
    return ["".join(r.choice("0125") if r.random() < 0.8 else r.choice("0123456789") for _ in range(r.randint(1, 14)))]


def v_ip(tests):
    for t in tests:
        s = t["args"][0]
        assert 1 <= len(s) <= 20 and s.isdigit() and s.isascii()
        rows = t["expected"]
        assert len(set(map(tuple, rows))) == len(rows)


CHECKS["restore-ip-address-octets"] = (b_ip, g_ip, "rowset")
VALIDATE["restore-ip-address-octets"] = v_ip


# ---------------------------------------------------------------- max unique splits
p = add(
    id="max-unique-string-splits", title="Maximum Distinct Pieces", diff="Medium", topic=T, tier="common",
    fn="maxUniqueSplits", params=[("s", "string")], ret="int", cmp="exact",
    desc="<p>Cut the string <code>s</code> into consecutive non-empty pieces (their concatenation must be exactly <code>s</code>) such that <strong>no two pieces are equal strings</strong>. Return the largest number of pieces that such a cut can have.</p><p>For example, <code>\"ababccc\"</code> can be cut into <code>a|b|ab|c|cc</code>, which has 5 distinct pieces; 6 pieces are impossible.</p>",
    constraints=["1 &le; s.length &le; 20", "s consists of lowercase English letters"],
    hints=["At each position you decide where the current piece ends. A set of pieces used so far tells you which choices are forbidden.",
           "Recurse on the start index with a set of used pieces. Try every end index, skip a piece already in the set, add it, recurse, remove it. Track the best count when the end of the string is reached.",
           "Prune: if the pieces so far plus the number of characters left (the absolute maximum number of further pieces) cannot beat the best answer found, stop."],
    editorial=["Backtracking on the cut positions. State: index <code>i</code> where the next piece starts, the number of pieces so far, and the set of pieces already used. For each end <code>j &gt; i</code>, the candidate piece is <code>s[i:j]</code>. If it is not in the set, add it, recurse with <code>j</code>, and remove it again. When <code>i == n</code>, record the piece count.",
               "There are 2<sup>n-1</sup> ways to cut a string of length n, so exploring everything costs at most about that many nodes, which is acceptable for n &le; 20. A strong and cheap prune is the bound <code>count + (n - i) &le; best</code>: every remaining character can become at most one more piece, so if that cannot exceed the current best the branch is useless.",
               "The set must be updated and restored symmetrically (add before the recursive call, remove after). Forgetting to remove is the classic bug in this kind of search."],
    time="O(2<sup>n</sup> &middot; n)", space="O(n)",
    solution='''def maxUniqueSplits(s):
    n = len(s)
    best = 0
    seen = set()

    def go(i, cnt):
        nonlocal best
        if cnt + (n - i) <= best:
            return
        if i == n:
            best = cnt
            return
        for j in range(i + 1, n + 1):
            piece = s[i:j]
            if piece not in seen:
                seen.add(piece)
                go(j, cnt + 1)
                seen.remove(piece)

    go(0, 0)
    return best
''',
    tests=[["ababccc"], ["a"], ["aa"], ["aba"], ["aaa"], ["abcdef"], ["aaaaaaaaaaaaaaaaaaaa"], ["ababababababababab"],
           ["abcabcabcabcabcabcab"], ["zzzzzzzzzzyyyyyyyyyy"], ["abcdefghijklmnopqrst"], ["aabbaabbaabbaabbaabb"],
           ["wwwzfvedwfvhsww"]],
)


def b_uniq(s):
    n = len(s)
    best = 0
    if n > 14:
        def dfs(i, used):
            nonlocal best
            if i == n:
                best = max(best, len(used))
                return
            if len(used) + (n - i) <= best:
                return
            for j in range(i + 1, n + 1):
                if s[i:j] not in used:
                    dfs(j, used | {s[i:j]})
        dfs(0, frozenset())
        return best
    for mask in range(1 << (n - 1)):
        cuts = [0] + [i + 1 for i in range(n - 1) if mask >> i & 1] + [n]
        pieces = [s[cuts[k]:cuts[k + 1]] for k in range(len(cuts) - 1)]
        if len(set(pieces)) == len(pieces):
            best = max(best, len(pieces))
    return best


def g_uniq(r):
    return ["".join(r.choice("abc" if r.random() < 0.7 else "ab") for _ in range(r.randint(1, 12)))]


def v_uniq(tests):
    for t in tests:
        s = t["args"][0]
        assert 1 <= len(s) <= 20 and s.isalpha() and s.islower() and s.isascii()
        assert 1 <= t["expected"] <= len(s)


CHECKS["max-unique-string-splits"] = (b_uniq, g_uniq, "exact")
VALIDATE["max-unique-string-splits"] = v_uniq


# ---------------------------------------------------------------- descending consecutive split
p = add(
    id="descending-consecutive-split", title="Descending Consecutive Split", diff="Medium", topic=T, tier="extra",
    fn="canSplitDescending", params=[("digits", "string")], ret="bool", cmp="exact",
    desc="<p>Given a string <code>digits</code> of decimal digits, decide whether it can be cut into <strong>at least two</strong> consecutive non-empty pieces so that the numeric values of the pieces, read from left to right, go down by exactly one each time (for example values <code>5, 4, 3</code>).</p><p>A piece may start with zeros: the piece <code>004</code> has value 4, and the piece <code>00</code> has value 0. The pieces must cover the whole string.</p><p>For example <code>\"050043\"</code> works as <code>05|004|3</code> (values 5, 4, 3), while <code>\"1234\"</code> does not.</p>",
    constraints=["1 &le; digits.length &le; 20", "digits consists only of the characters 0-9", "Piece values can be as large as 10<sup>19</sup>; in languages with 64-bit integers treat them carefully (the first piece can be up to 19 digits)"],
    hints=["Once you know the first piece, every following piece is forced to have a known value. So what is the only real choice?",
           "Try every length for the first piece (it cannot take the whole string). Then repeatedly look for a next piece whose value equals the previous value minus one.",
           "When extending the next piece character by character, its value never decreases (appending a digit multiplies by 10 and adds). Stop as soon as the value exceeds <code>prev - 1</code>. Because of leading zeros, a short run of zeros can be followed by the same value, so keep scanning until it exceeds."],
    editorial=["Backtrack over the first piece <code>digits[:j]</code> for <code>j</code> from 1 to <code>n - 1</code>. After that, the next piece must be a prefix of the remaining string with value exactly <code>prev - 1</code>. Scan prefixes of the remaining text; when a prefix has the wanted value, recurse on the rest with that value; stop scanning when the prefix value gets larger than the wanted value. Reaching the end of the string means success.",
               "The search is tiny. Only the first piece is a free choice, and later pieces are almost forced (several candidates exist only when leading zeros are involved, for example <code>0</code>, <code>00</code>, <code>000</code> all have value 0). The depth is at most n, so the running time is polynomial in n.",
               "Take care of two edge cases: the first piece may not use all the digits (at least two pieces are needed), and a previous value of 0 can never be followed by anything, because the next value would have to be -1."],
    time="O(n^3)", space="O(n)",
    solution='''def canSplitDescending(digits):
    n = len(digits)

    def go(i, prev):
        if i == n:
            return True
        want = prev - 1
        if want < 0:
            return False
        for j in range(i + 1, n + 1):
            v = int(digits[i:j])
            if v > want:
                break
            if v == want and go(j, v):
                return True
        return False

    for j in range(1, n):
        if go(j, int(digits[:j])):
            return True
    return False
''',
    tests=[["1234"], ["050043"], ["9080701"], ["10009998"], ["10"], ["21"], ["00"], ["5"], ["0090089"], ["001"],
           ["20191817161514131211"], ["99989796959493929190"], ["00000000000000000000"], ["10009999999999999998"],
           ["32100"], ["1009998"]],
)


def b_desc(s):
    n = len(s)

    def rest(i, prev):
        if i == n:
            return True
        for j in range(i + 1, n + 1):
            if int(s[i:j]) == prev - 1 and rest(j, prev - 1):
                return True
        return False

    return any(rest(j, int(s[:j])) for j in range(1, n))


def g_desc(r):
    if r.random() < 0.5:
        v = r.randint(1, 30)
        cnt = r.randint(2, 4)
        txt = ""
        for k in range(cnt):
            piece = str(max(v - k, 0))
            txt += "0" * r.choice([0, 0, 1]) + piece
        return [txt[:14]]
    return ["".join(r.choice("0012349") for _ in range(r.randint(1, 10)))]


def v_desc(tests):
    for t in tests:
        s = t["args"][0]
        assert 1 <= len(s) <= 20 and s.isdigit() and s.isascii()
    assert any(t["expected"] for t in tests) and any(not t["expected"] for t in tests)


CHECKS["descending-consecutive-split"] = (b_desc, g_desc, "exact")
VALIDATE["descending-consecutive-split"] = v_desc


# ---------------------------------------------------------------- fair bag distribution
p = add(
    id="fair-bag-distribution", title="Fair Bag Distribution", diff="Medium", topic=T, tier="common",
    fn="minLargestShare", params=[("bags", "int[]"), ("k", "int")], ret="int", cmp="exact",
    desc="<p>There are <code>n</code> sealed bags of cookies; <code>bags[i]</code> is the number of cookies in bag <code>i</code>. Bags cannot be opened or split. They are handed out to <code>k</code> children, each bag going to exactly one child (a child may end up with no bag at all).</p><p>The <em>unfairness</em> of a distribution is the largest number of cookies that any single child receives. Return the smallest unfairness that can be achieved.</p><p>For example, <code>bags = [8, 15, 10, 20, 8]</code> and <code>k = 2</code> gives <code>31</code> (one child takes <code>8 + 15 + 8 = 31</code>, the other <code>10 + 20 = 30</code>).</p>",
    constraints=["1 &le; k &le; bags.length &le; 12", "1 &le; bags[i] &le; 100,000"],
    hints=["Every bag has k possible owners, so there are k<sup>n</sup> distributions. Think about how to explore them while discarding hopeless ones early.",
           "Process the bags one by one, keeping the current total of every child. If the largest total already reaches the best answer found so far, stop exploring that branch.",
           "Two symmetries cut a lot of work: handle bags from largest to smallest, and never try giving a bag to two children who currently have the same total (the results are mirror images). Also stop immediately when the best answer equals the trivial lower bound <code>max(max bag, ceil(sum / k))</code>."],
    editorial=["This is a min-max partition problem, which is NP-hard in general, so with n &le; 12 we use a pruned backtracking search. Keep an array <code>loads</code> of the k children's totals. For bag <code>i</code> (sorted in decreasing order), try handing it to each child, update the load, recurse, and undo.",
               "Pruning makes it fast. (1) Prune when the largest load reaches the current best answer: this branch cannot improve it. (2) Starting with an upper bound from a greedy assignment (give each bag to the currently lightest child) gives strong pruning from the start. (3) Skip a child whose load equals the load of a child already tried for this bag. In particular all empty children are equivalent, so only one of them is tried. (4) Stop all search when the best equals the lower bound <code>max(max(bags), ceil(sum(bags) / k))</code>.",
               "Large bags first is important: placing big items early makes the loads differ quickly and lets pruning fire close to the root."],
    time="O(k<sup>n</sup>) worst case, much less with pruning", space="O(n + k)",
    solution='''def minLargestShare(bags, k):
    bags = sorted(bags, reverse=True)
    n = len(bags)
    lower = max(bags[0], -(-sum(bags) // k))
    loads = [0] * k
    for b in bags:
        loads[loads.index(min(loads))] += b
    best = max(loads)
    loads = [0] * k

    def go(i, cur):
        nonlocal best
        if best <= lower or cur >= best:
            return
        if i == n:
            best = cur
            return
        seen = set()
        for c in range(k):
            if loads[c] in seen:
                continue
            seen.add(loads[c])
            loads[c] += bags[i]
            go(i + 1, max(cur, loads[c]))
            loads[c] -= bags[i]

    go(0, 0)
    return best
''',
    tests=[[[8, 15, 10, 20, 8], 2], [[6, 1, 3, 2, 2, 4, 1, 2], 3], [[5], 1], [[5, 5], 2], [[1, 2, 3, 4, 5, 6, 7], 1],
           [[100000, 1, 1, 1], 3], [[7, 7, 7, 7], 4], [[3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3], 5],
           [[9, 8, 7, 6, 5, 4, 3, 2, 1, 1], 4], [[46, 41, 40, 40, 33, 31, 28, 26, 25, 24], 4],
           [[12, 13, 14, 17, 21, 22, 25, 29, 31, 33, 35, 39], 5],
           [[100000, 99999, 99998, 99997, 99996, 99995, 99994, 99993, 99992, 99991, 99990, 99989], 7],
           [[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], 12]],
)
_r = rnd(8105)
p["tests"].append([[_r.randint(1, 100000) for _ in range(12)], 5])
p["tests"].append([[_r.randint(1, 1000) for _ in range(12)], 4])
p["tests"].append([[_r.randint(500, 1000) for _ in range(12)], 6])


def b_fair(bags, k):
    n = len(bags)
    best = [sum(bags) + 1]
    loads = [0] * k

    def go(i):
        if max(loads) >= best[0]:
            return
        if i == n:
            best[0] = max(loads)
            return
        used_empty = False
        for c in range(k):
            if loads[c] == 0:
                if used_empty:
                    continue
                used_empty = True
            loads[c] += bags[i]
            go(i + 1)
            loads[c] -= bags[i]

    go(0)
    return best[0]


def g_fair(r):
    n = r.randint(1, 7)
    return [[r.randint(1, r.choice([5, 30, 1000])) for _ in range(n)], r.randint(1, min(n, 4))]


def v_fair(tests):
    for t in tests:
        bags, k = t["args"]
        assert 1 <= k <= len(bags) <= 12 and all(1 <= b <= 100000 for b in bags)
        assert max(max(bags), -(-sum(bags) // k)) <= t["expected"] <= sum(bags)


CHECKS["fair-bag-distribution"] = (b_fair, g_fair, "exact")
VALIDATE["fair-bag-distribution"] = v_fair


# ---------------------------------------------------------------- fewest work sessions
p = add(
    id="fewest-work-sessions", title="Fewest Work Sessions", diff="Medium", topic=T, tier="common",
    fn="minWorkSessions", params=[("tasks", "int[]"), ("sessionTime", "int")], ret="int", cmp="exact",
    desc="<p>You have <code>n</code> tasks; task <code>i</code> takes <code>tasks[i]</code> hours. You work in <em>sessions</em> of at most <code>sessionTime</code> consecutive hours each. A task must be finished entirely inside one session (it cannot be split between two sessions), and the tasks of a session may be done in any order.</p><p>Return the minimum number of sessions needed to complete all tasks. For example, <code>tasks = [3, 1, 3, 1, 1]</code> with <code>sessionTime = 8</code> needs 2 sessions (<code>3 + 1 + 3 + 1</code> and <code>1</code>).</p>",
    constraints=["1 &le; tasks.length &le; 14", "1 &le; tasks[i] &le; sessionTime &le; 100"],
    hints=["Assign each task to a session. A new session is only needed when no existing session has enough room.",
           "Backtrack over tasks one at a time: put the task in one of the sessions already opened (if it fits) or open a new one. Prune when the number of sessions opened is not better than the best found.",
           "For a faster method, remember for every set of finished tasks (a bitmask) the best pair (sessions used, hours used in the last session). Adding a task either fits in the last session or starts a new one."],
    editorial=["A simple backtracking solution places the tasks one by one. For task <code>i</code>, try every opened session where it fits, or open a new session; stop a branch when the number of sessions is at least the best found. Sorting tasks in decreasing order and skipping sessions with equal remaining room make it quick for small n.",
               "A reliable O(2<sup>n</sup> &middot; n) solution uses a bitmask table. Let <code>dp[mask]</code> be the lexicographically smallest pair <code>(sessions, hours used in the last session)</code> to complete the tasks in <code>mask</code>. From <code>dp[mask]</code>, adding task <code>i</code> gives <code>(s, l + t)</code> if <code>l + t &le; sessionTime</code>, otherwise <code>(s + 1, t)</code>. Comparing pairs lexicographically is valid because fewer sessions always beats more, and with equal sessions a less filled last session leaves more room for later tasks. The answer is the first component of <code>dp[all]</code>.",
               "With n &le; 14 the table has at most 16,384 states and about 230,000 transitions."],
    time="O(2<sup>n</sup> &middot; n)", space="O(2<sup>n</sup>)",
    solution='''def minWorkSessions(tasks, sessionTime):
    n = len(tasks)
    size = 1 << n
    sess = [n + 1] * size
    load = [0] * size
    sess[0] = 1
    for mask in range(size):
        s = sess[mask]
        if s > n:
            continue
        l = load[mask]
        for i in range(n):
            bit = 1 << i
            if mask & bit:
                continue
            t = tasks[i]
            if l + t <= sessionTime:
                ns, nl = s, l + t
            else:
                ns, nl = s + 1, t
            nm = mask | bit
            if ns < sess[nm] or (ns == sess[nm] and nl < load[nm]):
                sess[nm] = ns
                load[nm] = nl
    return sess[size - 1]
''',
    tests=[[[3, 1, 3, 1, 1], 8], [[1, 2, 3], 3], [[1, 2, 3, 4, 5], 15], [[5], 5], [[5, 5, 5], 5], [[1, 1, 1, 1], 2],
           [[4, 4, 4, 4, 4, 4], 9], [[7, 4, 5, 3, 6, 2, 8], 10], [[1] * 14, 5], [[100] * 14, 100], [[33, 34, 33, 33, 34, 33], 100],
           [[2, 3, 3, 4, 4, 4, 5, 6, 7, 7, 8], 12]],
)
_r = rnd(8106)
p["tests"].append([[_r.randint(1, 10) for _ in range(14)], 15])
p["tests"].append([[_r.randint(10, 60) for _ in range(14)], 100])
p["tests"].append([[_r.randint(1, 8) for _ in range(14)], 11])


def b_sess(tasks, T_):
    n = len(tasks)
    best = [n + 1]

    def go(i, rooms):
        if len(rooms) >= best[0]:
            return
        if i == n:
            best[0] = min(best[0], len(rooms))
            return
        for j in range(len(rooms)):
            if rooms[j] + tasks[i] <= T_:
                rooms[j] += tasks[i]
                go(i + 1, rooms)
                rooms[j] -= tasks[i]
        rooms.append(tasks[i])
        go(i + 1, rooms)
        rooms.pop()

    go(0, [])
    return best[0]


def g_sess(r):
    T_ = r.randint(1, 12)
    return [[r.randint(1, T_) for _ in range(r.randint(1, 8))], T_]


def v_sess(tests):
    for t in tests:
        tasks, T_ = t["args"]
        assert 1 <= len(tasks) <= 14 and 1 <= T_ <= 100 and all(1 <= x <= T_ for x in tasks)
        assert -(-sum(tasks) // T_) <= t["expected"] <= len(tasks)


CHECKS["fewest-work-sessions"] = (b_sess, g_sess, "exact")
VALIDATE["fewest-work-sessions"] = v_sess


# ================================================================== HARD

# ---------------------------------------------------------------- restore array from subset sums
p = add(
    id="restore-array-from-subset-sums", title="Restore Array From Subset Sums", diff="Hard", topic=T, tier="extra",
    fn="restoreFromSubsetSums", params=[("sums", "int[]")], ret="int[]", cmp="exact",
    desc="<p>A hidden integer array <code>a</code> of length <code>n</code> (values may be negative, zero or positive) was used to write down the sum of <strong>every</strong> subset of its elements, including the empty subset whose sum is 0. That produced <code>2<sup>n</sup></code> numbers, which were then shuffled into the array <code>sums</code>. Equal sums from different subsets are listed separately.</p><p>Several different arrays can produce the same <code>sums</code> (for instance flipping the sign of an element may still match). To make the answer unique, return the <strong>absolute values</strong> <code>|a[0]|, ..., |a[n-1]|</code> of a valid hidden array, <strong>sorted in non-decreasing order</strong>. It can be proved that this list is the same for every valid array.</p><p>For example, <code>sums = [-3, -2, -1, 0, 0, 1, 2, 3]</code> comes from <code>[1, 2, -3]</code> (among others), so the answer is <code>[1, 2, 3]</code>.</p>",
    constraints=["1 &le; n &le; 12 and sums.length = 2<sup>n</sup>", "-120,000 &le; sums[i] &le; 120,000", "The input is guaranteed to be the subset-sum multiset of some integer array whose elements satisfy |a[i]| &le; 10,000"],
    hints=["Let <code>m</code> be the smallest sum. Subtract <code>m</code> from every sum. What would the array look like if all its elements were non-negative?",
           "With all elements non-negative, the smallest sum is 0 and the second smallest sum is the smallest element <code>d</code> of the array (a single-element subset, or 0 if there are zeros). Which sums contain <code>d</code> and which do not?",
           "Split the sorted sums into two halves of equal size: the sums <em>without</em> <code>d</code> and the sums <em>with</em> <code>d</code> (each of which is one of the first plus <code>d</code>). Walk the sorted list, pair every unmatched value <code>x</code> with <code>x + d</code>. The first halves are the subset sums of the remaining elements, so repeat."],
    editorial=["Negative elements are handled by a shift. If the negative elements add up to <code>-N</code>, the smallest of all sums is exactly <code>-N</code> (take all negatives). Replace each negative element <code>-e</code> by <code>e</code>: every subset sum of the new all-non-negative array equals the old subset sum plus <code>N</code>. So subtracting the minimum from all given sums yields the subset sums of the array of absolute values, and the absolute values are what we are asked to return.",
               "Now all elements are non-negative. Sort the sums. The smallest is 0 (empty subset) and the next one, <code>d = sorted[1] - sorted[0]</code>, is the smallest element of the array. Every subset sum either avoids this element or contains it; the second kind is the first kind plus <code>d</code>. Scan the sorted sums with a counter: for each value <code>x</code> that still has an unmatched copy, put <code>x</code> into the \"without\" list and cancel one copy of <code>x + d</code>. The \"without\" list is exactly the subset sums of the other elements. Record <code>d</code> and repeat on that list until it has a single entry.",
               "Each round halves the list, so the rounds cost O(2<sup>n</sup>) in total and the initial sort dominates with O(n &middot; 2<sup>n</sup>). The recorded <code>d</code> values come out in non-decreasing order, which is the required output. Uniqueness of the absolute values follows from this argument: the reconstruction is forced at every step."],
    time="O(n &middot; 2<sup>n</sup>)", space="O(2<sup>n</sup>)",
    solution='''from collections import Counter


def restoreFromSubsetSums(sums):
    cur = sorted(sums)
    base = cur[0]
    cur = [x - base for x in cur]
    res = []
    while len(cur) > 1:
        d = cur[1] - cur[0]
        cnt = Counter(cur)
        without = []
        for x in cur:
            if cnt[x] > 0:
                cnt[x] -= 1
                cnt[x + d] -= 1
                without.append(x)
        res.append(d)
        cur = without
    return res
''',
    tests=[[[-3, -2, -1, 0, 0, 1, 2, 3]], [[0, 0]], [[0, 5]], [[0, -5]], [[0, 0, 0, 0]], [[-1, 0, 0, 1]],
           [[0, 1, 1, 2]], [[0, 2, 3, 5]], [[-4, -1, -3, 0, 0, 3, 1, 4]], [[0, 0, 7, 7, 7, 7, 14, 14]],
           [[0, 10000, -10000, 0]], [[0, 1, 2, 3, 3, 4, 5, 6]]],
)


def _subset_sums(vals):
    out = [0]
    for v in vals:
        out = out + [x + v for x in out]
    return out


_r = rnd(8107)
for _n, _lo, _hi in [(12, -1000, 1000), (12, 0, 3), (11, -10000, 10000), (10, -2, 2)]:
    _a = [_r.randint(_lo, _hi) for _ in range(_n)]
    _s = _subset_sums(_a)
    _r.shuffle(_s)
    p["tests"].append([_s])
_a = [-10000] * 6 + [10000] * 6
_s = _subset_sums(_a)
_r.shuffle(_s)
p["tests"].append([_s])


def b_subsums(sums):
    n = len(sums).bit_length() - 1
    target = sorted(sums)
    lim = max(abs(x) for x in sums)
    for vals in combinations_with_replacement(range(lim + 1), n):
        for signs in _product((1, -1), repeat=n):
            if sorted(_subset_sums([v * s for v, s in zip(vals, signs)])) == target:
                return sorted(vals)
    return None


def g_subsums(r):
    n = r.randint(1, 3)
    a = [r.randint(-3, 3) for _ in range(n)]
    s = _subset_sums(a)
    r.shuffle(s)
    return [s]


def v_subsums(tests):
    for t in tests:
        s = t["args"][0]
        n = len(s).bit_length() - 1
        assert 1 <= n <= 12 and len(s) == 1 << n and all(-120000 <= x <= 120000 for x in s)
        e = t["expected"]
        assert len(e) == n and e == sorted(e) and all(0 <= x <= 10000 for x in e)
        m = min(s)
        assert sorted(x - m for x in s) == sorted(_subset_sums(e)), "answer does not rebuild the sums"


CHECKS["restore-array-from-subset-sums"] = (b_subsums, g_subsums, "exact")
VALIDATE["restore-array-from-subset-sums"] = v_subsums


# ---------------------------------------------------------------- split into k palindromes, min changes
p = add(
    id="palindrome-partition-k-min-changes", title="Split Into K Palindromes", diff="Hard", topic=T, tier="extra",
    fn="minChangesKPalindromes", params=[("s", "string"), ("k", "int")], ret="int", cmp="exact",
    desc="<p>You may change some characters of the lowercase string <code>s</code> to any other lowercase letters. After the changes, the string must be cut into <strong>exactly <code>k</code></strong> non-empty consecutive pieces, each of which is a palindrome.</p><p>Return the minimum number of characters that have to be changed.</p><p>For example, <code>s = \"abc\"</code>, <code>k = 2</code> gives <code>1</code> (change <code>c</code> to <code>b</code> and cut <code>a|bb</code>), and <code>s = \"aabbc\"</code>, <code>k = 3</code> gives <code>0</code> (<code>aa|bb|c</code>).</p>",
    constraints=["1 &le; k &le; s.length &le; 100", "s consists of lowercase English letters"],
    hints=["First solve a simpler question: how many characters must change to turn one fixed piece <code>s[i..j]</code> into a palindrome? Think of mirrored pairs.",
           "Backtracking would try every way to choose k - 1 cut points, which is far too many for n = 100, but the subproblems repeat: the best way to split a prefix into p pieces is reused many times.",
           "Let <code>cost[i][j]</code> be the changes to make <code>s[i..j]</code> a palindrome, and <code>dp[p][j]</code> the best cost of splitting the first <code>j + 1</code> characters into <code>p</code> pieces. The last piece starts at some <code>i</code>: <code>dp[p][j] = min over i of dp[p-1][i-1] + cost[i][j]</code>."],
    editorial=["A piece is a palindrome when each character equals its mirror partner. Making <code>s[i..j]</code> a palindrome costs one change for every mirrored pair that differs, so <code>cost[i][j] = cost[i+1][j-1] + (s[i] != s[j])</code>, with the cost of empty and single-character ranges being 0. The table is built for all pairs in O(n<sup>2</sup>).",
               "Choose the cut points by dynamic programming (a memoised version of the backtracking search over cuts). Let <code>dp[p][j]</code> be the minimum cost to split <code>s[0..j]</code> into exactly <code>p</code> palindromic pieces. For <code>p = 1</code> it is <code>cost[0][j]</code>. For larger <code>p</code>, try every start <code>i</code> of the last piece with <code>i &ge; p - 1</code>: <code>dp[p][j] = min(dp[p-1][i-1] + cost[i][j])</code>. The answer is <code>dp[k][n-1]</code>.",
               "Overall O(n<sup>2</sup> + k &middot; n<sup>2</sup>), which is about 170,000 transitions for n = 100 because both the piece count and the ranges shrink."],
    time="O(k &middot; n^2)", space="O(n^2)",
    solution='''def minChangesKPalindromes(s, k):
    n = len(s)
    cost = [[0] * n for _ in range(n)]
    for i in range(n - 1, -1, -1):
        for j in range(i + 1, n):
            cost[i][j] = cost[i + 1][j - 1] + (s[i] != s[j])
    INF = 10 ** 9
    prev = [cost[0][j] for j in range(n)]
    for p in range(2, k + 1):
        cur = [INF] * n
        for j in range(p - 1, n):
            best = INF
            for i in range(p - 1, j + 1):
                v = prev[i - 1] + cost[i][j]
                if v < best:
                    best = v
            cur[j] = best
        prev = cur
    return prev[n - 1]
''',
    tests=[["abc", 2], ["aabbc", 3], ["abc", 1], ["abc", 3], ["a", 1], ["ab", 1], ["ab", 2], ["leetcode", 8], ["leetcode", 3],
           ["aaaaa", 2], ["abcdefgh", 4], ["abcabcabc", 3], ["zyxwvutsrqponmlkjihgfedcba", 5]],
)
_r = rnd(8108)
p["tests"].append(["".join(_r.choice("abcdefghijklmnopqrstuvwxyz") for _ in range(100)), 7])
p["tests"].append(["".join(_r.choice("abc") for _ in range(100)), 33])
p["tests"].append(["".join(_r.choice("ab") for _ in range(100)), 1])
p["tests"].append(["".join(_r.choice("ab") for _ in range(100)), 100])


def b_kpal(s, k):
    n = len(s)

    def cost(t):
        return sum(1 for i in range(len(t) // 2) if t[i] != t[len(t) - 1 - i])

    def go(i, left):
        if left == 1:
            return cost(s[i:])
        best = 10 ** 9
        for j in range(i + 1, n - left + 2):
            best = min(best, cost(s[i:j]) + go(j, left - 1))
        return best

    return go(0, k)


def g_kpal(r):
    n = r.randint(1, 9)
    return ["".join(r.choice("abc") for _ in range(n)), r.randint(1, n)]


def v_kpal(tests):
    for t in tests:
        s, k = t["args"]
        assert 1 <= k <= len(s) <= 100 and s.isalpha() and s.islower() and s.isascii()
        assert 0 <= t["expected"] <= len(s) // 2


CHECKS["palindrome-partition-k-min-changes"] = (b_kpal, g_kpal, "exact")
VALIDATE["palindrome-partition-k-min-changes"] = v_kpal


# ---------------------------------------------------------------- closest equal-size split
p = add(
    id="closest-equal-size-split", title="Closest Equal-Size Split", diff="Hard", topic=T, tier="extra",
    fn="closestEqualSizeSplit", params=[("nums", "int[]")], ret="int", cmp="exact",
    desc="<p>The array <code>nums</code> has an even length <code>2n</code>. Divide its elements (by position) into two groups of exactly <code>n</code> elements each. Return the smallest possible value of <code>|sum of group 1 - sum of group 2|</code>.</p><p>Values may be negative. For example, <code>nums = [3, 9, 7, 3]</code> gives <code>2</code> (groups <code>{3, 9}</code> and <code>{7, 3}</code> sum to 12 and 10), and <code>nums = [-36, 36]</code> gives <code>72</code> because each group must hold exactly one element.</p>",
    constraints=["2 &le; nums.length &le; 28 and nums.length is even", "-1,000,000 &le; nums[i] &le; 1,000,000"],
    hints=["Choosing which n of the 2n elements form group 1 means looking at C(2n, n) subsets, about 40 million for 2n = 28. That is too many to test one by one in a slow language.",
           "Cut the array into a left half and a right half of n elements each. Group 1 takes k elements from the left half and n - k from the right half, for some k between 0 and n.",
           "For each k, list the sums of all k-element subsets of the left half and of all (n-k)-element subsets of the right half. Sort one list and, for each sum in the other list, binary search for the partner that brings group 1's total closest to half of the grand total."],
    editorial=["Let <code>total</code> be the sum of all elements and <code>A</code> the sum of group 1. The difference is <code>|total - 2A|</code>, so we want <code>A</code> as close to <code>total / 2</code> as possible among all selections of exactly n elements.",
               "Meet in the middle. Split the array into halves <code>L</code> and <code>R</code> of n elements. Enumerate all 2<sup>n</sup> subsets of each half (with n &le; 14 that is 16,384) with their sums, grouped by subset size. Group 1 takes a subset of size <code>k</code> from <code>L</code> and a subset of size <code>n - k</code> from <code>R</code>, so for each <code>k</code> we combine the size-<code>k</code> sums of <code>L</code> with the size-<code>(n-k)</code> sums of <code>R</code>.",
               "For a fixed left sum <code>l</code>, we want a right sum <code>r</code> minimising <code>|total - 2l - 2r|</code>. Sort the right sums once per <code>k</code>, binary search for the value nearest to <code>(total - 2l) / 2</code> and inspect its neighbours. The total work is about 2 &middot; 2<sup>n</sup> for enumeration plus 2<sup>n</sup> binary searches, i.e. O(2<sup>n</sup> &middot; n), instead of C(2n, n)."],
    time="O(2<sup>n</sup> &middot; n)", space="O(2<sup>n</sup>)",
    solution='''from bisect import bisect_left


def closestEqualSizeSplit(nums):
    n = len(nums) // 2
    total = sum(nums)
    left = nums[:n]
    right = nums[n:]

    def by_size(a):
        m = len(a)
        sums = [0] * (1 << m)
        cnt = [0] * (1 << m)
        groups = [[] for _ in range(m + 1)]
        groups[0].append(0)
        for mask in range(1, 1 << m):
            low = mask & -mask
            rest = mask ^ low
            sums[mask] = sums[rest] + a[low.bit_length() - 1]
            cnt[mask] = cnt[rest] + 1
            groups[cnt[mask]].append(sums[mask])
        return groups

    gl = by_size(left)
    gr = by_size(right)
    best = float('inf')
    for k in range(n + 1):
        rs = sorted(gr[n - k])
        for l in gl[k]:
            target = total - 2 * l
            idx = bisect_left(rs, target // 2)
            for q in (idx - 1, idx, idx + 1):
                if 0 <= q < len(rs):
                    d = abs(target - 2 * rs[q])
                    if d < best:
                        best = d
    return best
''',
    tests=[[[3, 9, 7, 3]], [[-36, 36]], [[2, -1, 0, 4, -2, -9]], [[1, 1]], [[5, 5, 5, 5]], [[0, 0, 0, 0]],
           [[1, 2, 3, 4, 5, 6]], [[-1000000, 1000000, -1000000, 1000000]], [[100, 1, 1, 1]],
           [[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]], [[1000000] * 28]],
)
_r = rnd(8109)
p["tests"].append([[_r.randint(-1000000, 1000000) for _ in range(28)]])
p["tests"].append([[_r.randint(1, 1000000) for _ in range(28)]])
p["tests"].append([[_r.randint(-5, 5) for _ in range(26)]])


def b_split(nums):
    n = len(nums) // 2
    total = sum(nums)
    best = None
    for comb in combinations(range(2 * n), n):
        a = sum(nums[i] for i in comb)
        d = abs(total - 2 * a)
        if best is None or d < best:
            best = d
    return best


def g_split(r):
    n = r.randint(1, 6)
    return [[r.randint(-r.choice([3, 20, 1000]), r.choice([3, 20, 1000])) for _ in range(2 * n)]]


def v_split(tests):
    for t in tests:
        a = t["args"][0]
        assert 2 <= len(a) <= 28 and len(a) % 2 == 0 and all(-10 ** 6 <= x <= 10 ** 6 for x in a)
        assert 0 <= t["expected"] <= abs(sum(a)) + 2 * 10 ** 6 * len(a)


CHECKS["closest-equal-size-split"] = (b_split, g_split, "exact")
VALIDATE["closest-equal-size-split"] = v_split
