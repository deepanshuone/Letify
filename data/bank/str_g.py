"""Problems: strings, stack-like string reduction (cancel pairs, delete substrings, editor operations). See data/lib.py for the registry."""
from lib import add, rnd, CHECKS, VALIDATE, gen_arr  # noqa: F401

TOPIC = "Strings"
LOWER = "abcdefghijklmnopqrstuvwxyz"


def _is_lower(s, alphabet=LOWER):
    return len(s) > 0 and all(c in alphabet for c in s)


# ---------------------------------------------------------------- EASY

p = add(
    id="remove-adjacent-case-pairs", title="Remove Adjacent Case Pairs", diff="Easy", topic=TOPIC, tier="common",
    fn="removeCasePairs", params=[("s", "string")], ret="string", cmp="exact",
    desc="<p>A string <code>s</code> consists of English letters in both lower and upper case. Whenever two <em>neighbouring</em> characters are the same letter in different cases (for example <code>'e'</code> and <code>'E'</code>, in either order), you may delete both of them; the characters on their two sides then become neighbours. Keep doing this for as long as such a pair exists.</p><p>Return the string that remains. The result does not depend on which pair you delete first, and it may be empty.</p><p>Example: <code>'abBAcC'</code> becomes <code>'aAcC'</code> (delete <code>bB</code>), then <code>'cC'</code> (delete <code>aA</code>), then the empty string. Another: <code>'leEeetcode'</code> becomes <code>'leetcode'</code>, because <code>'ee'</code> is not a pair (same case).</p>",
    constraints=["1 &le; s.length &le; 10,000", "s consists of lowercase and uppercase English letters", "The answer may be the empty string"],
    hints=["Deleting a pair can bring two characters together that were far apart in the input, so a single left-to-right look at neighbours is not enough.",
           "The only character that a new character can ever cancel with is the last one that survived so far. Think of the survivors as a pile where only the top is reachable.",
           "Keep a stack of survivors. For each character, if the stack is non-empty and the top is the same letter in the other case (<code>top != ch and top.lower() == ch.lower()</code>), pop; otherwise push. The stack read from bottom to top is the answer."],
    editorial=["Scan the string from left to right and keep the surviving characters in a stack. A new character can only cancel with the character right before it in the current, already reduced text, and that is the top of the stack. If the two are the same letter in different cases, pop the top and discard the new character. Otherwise the new character stays and is pushed.",
               "After a pop, the new top is exactly the character that became adjacent to the next input character, so chains such as <code>'abBA'</code> collapse completely without any extra work. Every character is pushed and popped at most once, so the time is O(n) with O(n) space. The result is independent of the deletion order because the stack always produces the fully reduced string."],
    time="O(n)", space="O(n)",
    solution='''def removeCasePairs(s):
    stack = []
    for ch in s:
        if stack and stack[-1] != ch and stack[-1].lower() == ch.lower():
            stack.pop()
        else:
            stack.append(ch)
    return "".join(stack)
''',
    tests=[["leEeetcode"], ["abBAcC"], ["s"], ["aA"], ["Aa"], ["aa"], ["AAaa"], ["abc"], ["aBbAcCdD"], ["xXyYzZ"], ["mnNMmnNM"], ["AbBaCc"]],
)
_r = rnd(9701)
p["tests"].append(["".join(_r.choice("aAbB") for _ in range(9000))])
p["tests"].append(["".join(_r.choice("aAbBcCdDeE") for _ in range(10000))])
_left = "".join(_r.choice("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ") for _ in range(4500))
p["tests"].append([_left + _left[::-1].swapcase()])
p["tests"].append([_left + "Q" + _left[::-1].swapcase()])


def b_case(s):
    while True:
        for i in range(len(s) - 1):
            if s[i] != s[i + 1] and s[i].lower() == s[i + 1].lower():
                s = s[:i] + s[i + 2:]
                break
        else:
            return s


def g_case(r):
    return ["".join(r.choice("aAbBc") for _ in range(r.randint(1, 14)))]


def v_case(tests):
    for t in tests:
        s = t["args"][0]
        assert 1 <= len(s) <= 10000 and s.isalpha() and s.isascii()


CHECKS["remove-adjacent-case-pairs"] = (b_case, g_case, "exact")
VALIDATE["remove-adjacent-case-pairs"] = v_case


p = add(
    id="min-length-after-removing-ab-and-cd", title="Minimum Length After Removing ab and cd", diff="Easy", topic=TOPIC, tier="common",
    fn="minLengthAfterRemovals", params=[("s", "string")], ret="int", cmp="exact",
    desc="<p>You are given a string <code>s</code> of lowercase letters. In one operation you may delete any occurrence of the substring <code>'ab'</code> or of the substring <code>'cd'</code>; the remaining parts then join together and can form new occurrences.</p><p>Return the smallest possible length of <code>s</code> after performing the operation as many times as you like.</p><p>Example: <code>'cabd'</code> becomes <code>'cd'</code> after deleting <code>ab</code>, and then the empty string, so the answer is <code>0</code>. For <code>'acbbd'</code> there is no <code>'ab'</code> and no <code>'cd'</code> at all, so the answer is <code>5</code>.</p>",
    constraints=["1 &le; s.length &le; 10,000", "s consists of lowercase English letters"],
    hints=["After a deletion, new occurrences of <code>'ab'</code> or <code>'cd'</code> can appear, so one pass with <code>replace</code> is not always enough.",
           "A new character completes a deletable pair only together with the character directly before it in the already reduced text.",
           "Keep a stack of survivors. When the current character is <code>'b'</code> and the top is <code>'a'</code>, or the current character is <code>'d'</code> and the top is <code>'c'</code>, pop instead of pushing. The final stack size is the answer."],
    editorial=["Walk through the string and maintain the reduced text built so far as a stack. When a character arrives, the only pair it can complete is with the top of the stack: <code>a</code> followed by <code>b</code>, or <code>c</code> followed by <code>d</code>. If that happens we delete both by popping; otherwise we push the new character.",
               "The two patterns share no letters, so a deletion of one kind never overlaps with the other kind, and the final reduced string is the same regardless of the order of deletions. That is why the greedy stack is optimal and the answer is simply its size. Time is O(n), extra space O(n)."],
    time="O(n)", space="O(n)",
    solution='''def minLengthAfterRemovals(s):
    stack = []
    for ch in s:
        if stack and ((stack[-1] == 'a' and ch == 'b') or (stack[-1] == 'c' and ch == 'd')):
            stack.pop()
        else:
            stack.append(ch)
    return len(stack)
''',
    tests=[["cabd"], ["acbbd"], ["ab"], ["cd"], ["a"], ["ba"], ["dc"], ["abcd"], ["acdb"], ["aabbccdd"], ["abababab"], ["cadbcadb"], ["xyz"]],
)
_r = rnd(9702)
p["tests"].append(["".join(_r.choice("abcd") for _ in range(10000))])
p["tests"].append(["".join(_r.choice("abcdefg") for _ in range(10000))])
p["tests"].append(["a" * 5000 + "b" * 5000])
p["tests"].append(["ac" * 2500 + "db" * 2500])


def b_abcd(s):
    while "ab" in s or "cd" in s:
        s = s.replace("ab", "", 1) if "ab" in s else s.replace("cd", "", 1)
    return len(s)


def g_abcd(r):
    return ["".join(r.choice("abcdx") for _ in range(r.randint(1, 14)))]


def v_abcd(tests):
    for t in tests:
        assert 1 <= len(t["args"][0]) <= 10000 and _is_lower(t["args"][0])


CHECKS["min-length-after-removing-ab-and-cd"] = (b_abcd, g_abcd, "exact")
VALIDATE["min-length-after-removing-ab-and-cd"] = v_abcd


p = add(
    id="clear-digits-with-nearest-letter", title="Clear Digits With the Nearest Letter", diff="Easy", topic=TOPIC, tier="common",
    fn="clearDigits", params=[("s", "string")], ret="string", cmp="exact",
    desc="<p>The string <code>s</code> contains lowercase letters and decimal digits. Repeat the following step while <code>s</code> still contains a digit: take the <em>leftmost</em> digit and delete it together with the closest non-digit character to its left. If no non-digit character exists to its left, delete only the digit.</p><p>Return the final string, which contains no digits. It may be empty.</p><p>Example: <code>'ab12c'</code>: the leftmost digit <code>'1'</code> deletes itself and <code>'b'</code>, giving <code>'a2c'</code>; then <code>'2'</code> deletes itself and <code>'a'</code>, giving <code>'c'</code>. Another: <code>'7x3y'</code> becomes <code>'y'</code>: the leading <code>'7'</code> has nothing to its left and disappears alone, then <code>'3'</code> removes <code>'x'</code>.</p>",
    constraints=["1 &le; s.length &le; 10,000", "s consists of lowercase English letters and digits <code>0</code> to <code>9</code>", "The answer may be the empty string"],
    hints=["Always handling the leftmost digit means everything to its left is already a plain letter. Which letter does it remove?",
           "The closest non-digit on the left of the leftmost digit is simply the last letter kept so far.",
           "Scan once with a stack of letters: a letter is pushed, a digit pops the top if the stack is non-empty and does nothing otherwise."],
    editorial=["Because the step always uses the leftmost digit, all characters before that digit are letters, and the closest one is the last of them. This is exactly the behaviour of a backspace key: the digit erases the most recent surviving letter.",
               "So a single left-to-right scan with a stack is enough. A letter is pushed. A digit pops the top of the stack if there is one; with an empty stack it vanishes without any effect. The stack contents form the answer. Time O(n), space O(n)."],
    time="O(n)", space="O(n)",
    solution='''def clearDigits(s):
    stack = []
    for ch in s:
        if ch.isdigit():
            if stack:
                stack.pop()
        else:
            stack.append(ch)
    return "".join(stack)
''',
    tests=[["ab12c"], ["7x3y"], ["abc"], ["a1"], ["1"], ["12ab"], ["abc999"], ["a1b2c3"], ["abc123def"], ["x00y11z"], ["ab1c2d3e4"], ["0"]],
)
_r = rnd(9703)
p["tests"].append(["".join(_r.choice("ab0123") for _ in range(10000))])
p["tests"].append(["".join(_r.choice("abcdefghij" + "0" * 3) for _ in range(9000))])
p["tests"].append(["z" * 5000 + "5" * 4999])
p["tests"].append(["".join(_r.choice("abcdefghijklmnopqrstuvwxyz0123456789") for _ in range(10000))])


def b_digits(s):
    while any(c.isdigit() for c in s):
        i = next(k for k, c in enumerate(s) if c.isdigit())
        s = s[:i - 1] + s[i + 1:] if i > 0 else s[1:]
    return s


def g_digits(r):
    return ["".join(r.choice("abc012") for _ in range(r.randint(1, 14)))]


def v_digits(tests):
    for t in tests:
        s = t["args"][0]
        assert 1 <= len(s) <= 10000 and all(c in LOWER + "0123456789" for c in s)


CHECKS["clear-digits-with-nearest-letter"] = (b_digits, g_digits, "exact")
VALIDATE["clear-digits-with-nearest-letter"] = v_digits


# ---------------------------------------------------------------- MEDIUM

p = add(
    id="remove-all-occurrences-of-pattern", title="Remove All Occurrences of a Pattern", diff="Medium", topic=TOPIC, tier="common",
    fn="removeAllOccurrences", params=[("s", "string"), ("part", "string")], ret="string", cmp="exact",
    desc="<p>Given strings <code>s</code> and <code>part</code>, repeat the following until <code>part</code> no longer occurs in <code>s</code>: find the <em>leftmost</em> occurrence of <code>part</code> in <code>s</code> and delete it, letting the two remaining sides join together.</p><p>Return the final string. It may be empty.</p><p>Example: for <code>s = 'daabcbaabcbc'</code> and <code>part = 'abc'</code>, the leftmost <code>'abc'</code> is removed to give <code>'dabaabcbc'</code>, then <code>'dababc'</code>, then <code>'dab'</code>, so the answer is <code>'dab'</code>.</p>",
    constraints=["1 &le; s.length &le; 10,000", "1 &le; part.length &le; 1,000", "s and part consist of lowercase English letters", "The answer may be the empty string"],
    hints=["Calling <code>replace</code> or <code>find</code> again and again rebuilds the string each time, which can be O(n<sup>2</sup>) or worse.",
           "Build the answer left to right in a stack. The leftmost occurrence is also the one that finishes first, so as soon as the top of the stack ends with <code>part</code>, remove it.",
           "Checking the end of the stack costs O(m) per character. To get O(n + m), store with every stacked character the KMP match length reached after it; after a removal the state of the new top is already known."],
    editorial=["The leftmost occurrence of a fixed-length pattern is also the occurrence that ends first. So if we append characters one at a time to a stack, the first moment the top of the stack ends with <code>part</code> is the moment the leftmost occurrence appears, and removing it from the stack is exactly the required operation. The removal may expose a new occurrence that is completed by later characters, and the stack handles that naturally.",
               "A direct check of the last <code>m</code> stacked characters is O(n m). To speed it up, run the KMP automaton of <code>part</code> and store, next to each stacked character, the automaton state after reading it. When the state reaches <code>m</code>, pop <code>m</code> characters (and their states); the state of the new top is exactly the automaton state we need to continue. Total time O(n + m), space O(n + m)."],
    time="O(n + m)", space="O(n + m)",
    solution='''def removeAllOccurrences(s, part):
    m = len(part)
    fail = [0] * m
    k = 0
    for i in range(1, m):
        while k and part[i] != part[k]:
            k = fail[k - 1]
        if part[i] == part[k]:
            k += 1
        fail[i] = k
    chars = []
    states = [0]
    for ch in s:
        k = states[-1]
        while k and part[k] != ch:
            k = fail[k - 1]
        if part[k] == ch:
            k += 1
        chars.append(ch)
        states.append(k)
        if k == m:
            del chars[-m:]
            del states[-m:]
    return "".join(chars)
''',
    tests=[["daabcbaabcbc", "abc"], ["axxxxyyyyb", "xy"], ["abc", "abc"], ["abc", "d"], ["aaaa", "aa"], ["aaaaa", "aa"], ["abab", "ab"], ["aabb", "ab"], ["abcabcabc", "bca"],
           ["xaabababbby", "abab"], ["aababa", "aba"], ["a", "a"], ["mississippi", "iss"]],
)
_r = rnd(9704)


def _nested(r, part, copies, noise=0, alphabet="ab"):
    s = ""
    for _ in range(copies):
        pos = r.randint(0, len(s))
        s = s[:pos] + part + s[pos:]
    for _ in range(noise):
        pos = r.randint(0, len(s))
        s = s[:pos] + r.choice(alphabet) + s[pos:]
    return s


_part = "".join(_r.choice("ab") for _ in range(20))
p["tests"].append([_nested(_r, _part, 450), _part])
p["tests"].append([_nested(_r, _part, 440, 150), _part])
_part2 = "aab" * 7
p["tests"].append([_nested(_r, _part2, 470, 40), _part2])
p["tests"].append(["a" * 10000, "a" * 999])
p["tests"].append(["".join(_r.choice("abc") for _ in range(10000)), "abca"])


def b_remocc(s, part):
    while part in s:
        s = s.replace(part, "", 1)
    return s


def g_remocc(r):
    part = "".join(r.choice("ab") for _ in range(r.randint(1, 4)))
    s = _nested(r, part, r.randint(0, 4), r.randint(0, 4), "abc")
    return [s if s else "a", part]


def v_remocc(tests):
    for t in tests:
        s, part = t["args"]
        assert 1 <= len(s) <= 10000 and _is_lower(s)
        assert 1 <= len(part) <= 1000 and _is_lower(part)


CHECKS["remove-all-occurrences-of-pattern"] = (b_remocc, g_remocc, "exact")
VALIDATE["remove-all-occurrences-of-pattern"] = v_remocc


p = add(
    id="string-built-by-inserting-abc", title="String Built by Inserting abc", diff="Medium", topic=TOPIC, tier="common",
    fn="isBuiltByAbc", params=[("s", "string")], ret="bool", cmp="exact",
    desc="<p>Start with the empty string. In one step you may insert the three-letter block <code>'abc'</code> at <em>any</em> position of the current string, including in the middle of an earlier block. Given a string <code>s</code>, return <code>true</code> if some sequence of such steps produces exactly <code>s</code>, and <code>false</code> otherwise.</p><p>Examples: <code>'aabcbc'</code> is possible (insert <code>abc</code> into the middle of <code>abc</code>), and so is <code>'abcabcababcc'</code>. The string <code>'abccba'</code> is not.</p>",
    constraints=["1 &le; s.length &le; 10,000", "s consists only of the letters <code>a</code>, <code>b</code> and <code>c</code>"],
    hints=["Think backwards: the last inserted block must appear in <code>s</code> as a contiguous <code>'abc'</code>. Remove it and the rest must again be buildable.",
           "Removing blocks one by one with <code>replace</code> is slow if repeated. Which occurrence of <code>'abc'</code> do you discover first when reading left to right?",
           "Scan with a stack: push every character, and whenever the top three characters are <code>a, b, c</code>, pop them. The string is buildable exactly when the stack ends up empty."],
    editorial=["Reverse the process. If <code>s</code> was produced by insertions, then the most recently inserted block is a contiguous <code>'abc'</code> inside <code>s</code>; deleting it leaves a string that was produced by one step less. So <code>s</code> is buildable if and only if repeatedly deleting an <code>'abc'</code> substring can reduce it to the empty string. The order of deletions does not matter, because two occurrences of <code>'abc'</code> can never overlap.",
               "Do the deletions with a stack: push characters one by one and, whenever the three topmost characters spell <code>abc</code>, pop them. The stack holds exactly the reduced text of the prefix read so far. If it is empty at the end, the answer is <code>true</code>. A quick shortcut is that the length must be divisible by 3. Time O(n), space O(n)."],
    time="O(n)", space="O(n)",
    solution='''def isBuiltByAbc(s):
    if len(s) % 3:
        return False
    stack = []
    for ch in s:
        stack.append(ch)
        if len(stack) >= 3 and stack[-3] == 'a' and stack[-2] == 'b' and stack[-1] == 'c':
            del stack[-3:]
    return not stack
''',
    tests=[["aabcbc"], ["abcabcababcc"], ["abccba"], ["abc"], ["a"], ["ab"], ["cba"], ["aabbcc"], ["abcabc"], ["ababcc"], ["abcc"], ["aabcbcabc"], ["acbabc"]],
)
_r = rnd(9705)
p["tests"].append([_nested(_r, "abc", 3333)])
_s = _nested(_r, "abc", 3333)
p["tests"].append([_s[:5000] + "c" + _s[5000:-1]])
p["tests"].append(["a" * 3333 + "b" * 3333 + "c" * 3333])
p["tests"].append(["abc" * 3333])


def b_abc(s):
    while "abc" in s:
        s = s.replace("abc", "")
    return s == ""


def g_abc(r):
    if r.random() < 0.6:
        s = _nested(r, "abc", r.randint(1, 4))
        if r.random() < 0.3 and len(s) > 1:
            i = r.randrange(len(s))
            s = s[:i] + r.choice("abc") + s[i + 1:]
        return [s]
    return ["".join(r.choice("abc") for _ in range(r.randint(1, 12)))]


def v_abc(tests):
    for t in tests:
        s = t["args"][0]
        assert 1 <= len(s) <= 10000 and _is_lower(s, "abc")
    assert any(t["expected"] for t in tests) and not all(t["expected"] for t in tests)


CHECKS["string-built-by-inserting-abc"] = (b_abc, g_abc, "exact")
VALIDATE["string-built-by-inserting-abc"] = v_abc


p = add(
    id="max-points-removing-ab-and-ba", title="Maximum Points Removing ab and ba", diff="Medium", topic=TOPIC, tier="common",
    fn="maximumPoints", params=[("s", "string"), ("x", "int"), ("y", "int")], ret="int", cmp="exact",
    desc="<p>You are given a string <code>s</code> of lowercase letters and two scores <code>x</code> and <code>y</code>. You may repeatedly perform either of these operations as long as they apply:</p><ul><li>delete a substring <code>'ab'</code> and earn <code>x</code> points;</li><li>delete a substring <code>'ba'</code> and earn <code>y</code> points.</li></ul><p>After each deletion the two remaining sides join. Return the maximum total number of points you can earn.</p><p>Example: <code>s = 'cdbcbbaaabab'</code>, <code>x = 4</code>, <code>y = 5</code> gives <code>19</code>.</p>",
    constraints=["1 &le; s.length &le; 10,000", "1 &le; x, y &le; 10,000", "s consists of lowercase English letters"],
    hints=["Removing one pair can destroy or create other pairs, so the order matters. Try small strings such as <code>'aba'</code> by hand to see why.",
           "Only the letters <code>a</code> and <code>b</code> matter, and any other letter separates the string into independent parts. Is it better to remove the more valuable pair first or last?",
           "Remove all pairs of the more valuable kind first, using a stack, then remove all pairs of the other kind from what is left. Add up the points."],
    editorial=["Suppose <code>x &ge; y</code> (otherwise swap the roles). Greedy claim: remove every possible <code>'ab'</code> first, then every possible <code>'ba'</code>. Each removal uses up one <code>a</code> and one <code>b</code>, and a pair of the cheaper kind that is removed early can destroy at most one pair of the dearer kind, so an exchange argument shows that taking dearer pairs first never loses points. Letters other than <code>a</code> and <code>b</code> are never removed and just act as walls.",
               "Implement each pass with a stack: for the first pass push characters and whenever the top is <code>a</code> and the incoming character is <code>b</code>, pop and add <code>x</code>. The characters left in the stack form the string for the second pass, in which the pair <code>'ba'</code> is removed the same way and <code>y</code> is added. Each pass is linear, so the total time is O(n) and the space O(n)."],
    time="O(n)", space="O(n)",
    solution='''def maximumPoints(s, x, y):
    def remove(text, first, second, value):
        kept = []
        gained = 0
        for ch in text:
            if kept and kept[-1] == first and ch == second:
                kept.pop()
                gained += value
            else:
                kept.append(ch)
        return kept, gained

    if x >= y:
        rest, g1 = remove(s, 'a', 'b', x)
        _, g2 = remove(rest, 'b', 'a', y)
    else:
        rest, g1 = remove(s, 'b', 'a', y)
        _, g2 = remove(rest, 'a', 'b', x)
    return g1 + g2
''',
    tests=[["cdbcbbaaabab", 4, 5], ["aabbaaxybbaabb", 5, 4], ["ab", 3, 7], ["ba", 3, 7], ["aba", 5, 4], ["aba", 4, 5], ["bab", 5, 4], ["bab", 4, 5], ["abab", 1, 1],
           ["zzz", 9, 9], ["aaabbb", 2, 10], ["baabbaab", 3, 8], ["a", 1, 1]],
)
_r = rnd(9706)
p["tests"].append(["".join(_r.choice("ab") for _ in range(10000)), 7777, 3333])
p["tests"].append(["".join(_r.choice("abc") for _ in range(10000)), 2500, 9000])
p["tests"].append(["ab" * 5000, 10000, 1])
p["tests"].append(["".join(_r.choice("aab") for _ in range(10000)), 5000, 5000])


def b_points(s, x, y):
    memo = {}

    def go(t):
        if t in memo:
            return memo[t]
        best = 0
        for i in range(len(t) - 1):
            if t[i:i + 2] == "ab":
                best = max(best, x + go(t[:i] + t[i + 2:]))
            elif t[i:i + 2] == "ba":
                best = max(best, y + go(t[:i] + t[i + 2:]))
        memo[t] = best
        return best

    return go(s)


def g_points(r):
    return ["".join(r.choice("aabbc") for _ in range(r.randint(1, 11))), r.randint(1, 9), r.randint(1, 9)]


def v_points(tests):
    for t in tests:
        s, x, y = t["args"]
        assert 1 <= len(s) <= 10000 and _is_lower(s) and 1 <= x <= 10000 and 1 <= y <= 10000


CHECKS["max-points-removing-ab-and-ba"] = (b_points, g_points, "exact")
VALIDATE["max-points-removing-ab-and-ba"] = v_points


p = add(
    id="broken-keyboard-home-and-end", title="Broken Keyboard With Home and End", diff="Medium", topic=TOPIC, tier="extra",
    fn="brokenKeyboard", params=[("keys", "string")], ret="string", cmp="exact",
    desc="<p>A faulty keyboard sometimes presses the <strong>Home</strong> and <strong>End</strong> keys by itself. The string <code>keys</code> lists the key presses in order: a lowercase letter types that letter at the current cursor position, the character <code>'['</code> is Home (the cursor jumps to the very beginning of the text), and <code>']'</code> is End (the cursor jumps to the very end of the text). The text starts empty with the cursor at the end.</p><p>Return the final text. It may be empty if no letters were typed.</p><p>Example: <code>'ab[cd]ef'</code> gives <code>'cdabef'</code>: <code>cd</code> is typed at the front, then End moves back to the end for <code>ef</code>. Another: <code>'[a[b]c'</code> gives <code>'bac'</code>.</p>",
    constraints=["1 &le; keys.length &le; 10,000", "keys consists of lowercase letters, <code>'['</code> and <code>']'</code>", "The answer may be the empty string"],
    hints=["Inserting into the middle of a Python string or list for every letter makes the simulation O(n<sup>2</sup>) in the worst case.",
           "Between two special keys the typed letters form one block that stays together. Where does a whole block end up?",
           "Collect each block. If the key before it was Home, the block goes to the very front (before all earlier front blocks); otherwise it goes to the very end. Keep front blocks in a stack or deque and join everything at the end."],
    editorial=["Split the key presses into maximal runs of letters separated by <code>[</code> and <code>]</code>. All letters of a run are typed one after another at the same place, and a run typed after Home is placed at the very front of the text, in front of everything typed earlier, including earlier front runs. A run typed in End mode (the starting mode too) is appended after everything.",
               "So keep two lists: <code>front</code> receives each Home run in order of typing and is reversed at the end, and <code>back</code> receives each End run in order. The answer is the reversed <code>front</code> joined with <code>back</code>. This avoids any middle insertion and is O(n) time and space."],
    time="O(n)", space="O(n)",
    solution='''def brokenKeyboard(keys):
    front = []
    back = []
    run = []
    home = False
    for ch in keys + '[':
        if ch == '[' or ch == ']':
            block = "".join(run)
            run = []
            if home:
                front.append(block)
            else:
                back.append(block)
            home = (ch == '[')
        else:
            run.append(ch)
    # the sentinel '[' above only flushes the last block
    return "".join(reversed(front)) + "".join(back)
''',
    tests=[["ab[cd]ef"], ["[a[b]c"], ["abc"], ["[abc"], ["abc]"], ["[]"], ["[[[]]]"], ["a[b[c[d"], ["a]b]c]d"], ["[a]b[c]d[e]f"], ["hello[world]"], ["[x][y][z]"], ["ab[]cd[]ef"]],
)
_r = rnd(9707)
p["tests"].append(["".join(_r.choice("abcdefgh[]") for _ in range(10000))])
p["tests"].append(["".join(_r.choice("abc" + "[" * 1 + "]" * 1) for _ in range(9999))])
p["tests"].append(["".join(_r.choice(LOWER + "[" * 3 + "]" * 2) for _ in range(10000))])
p["tests"].append(["[".join(_r.choice(LOWER) for _ in range(5000))])


def b_broken(keys):
    text = []
    cur = 0
    for ch in keys:
        if ch == '[':
            cur = 0
        elif ch == ']':
            cur = len(text)
        else:
            text.insert(cur, ch)
            cur += 1
    return "".join(text)


def g_broken(r):
    return ["".join(r.choice("abc[]") for _ in range(r.randint(1, 14)))]


def v_broken(tests):
    for t in tests:
        s = t["args"][0]
        assert 1 <= len(s) <= 10000 and all(c in LOWER + "[]" for c in s)


CHECKS["broken-keyboard-home-and-end"] = (b_broken, g_broken, "exact")
VALIDATE["broken-keyboard-home-and-end"] = v_broken


p = add(
    id="text-editor-undo-redo-final-text", title="Text Editor With Undo and Redo", diff="Medium", topic=TOPIC, tier="extra",
    fn="finalText", params=[("ops", "int[][]")], ret="string", cmp="exact",
    desc="<p>A tiny editor starts with an empty text. You are given a list <code>ops</code>; each operation is a pair <code>[type, value]</code>:</p><ul><li><code>[1, c]</code>: <strong>type</strong> the letter number <code>c</code> (1 means <code>'a'</code>, 26 means <code>'z'</code>) at the end of the text;</li><li><code>[2, 0]</code>: <strong>backspace</strong>, delete the last letter. If the text is empty, nothing happens at all;</li><li><code>[3, 0]</code>: <strong>undo</strong> the most recent action (type or effective backspace) that has not been undone yet; nothing happens if there is none;</li><li><code>[4, 0]</code>: <strong>redo</strong> the most recently undone action; nothing happens if there is none.</li></ul><p>Typing a letter or an effective backspace creates a new action and wipes the whole redo history (undone actions can no longer be redone). Undo and redo themselves are not actions. Return the final text, which may be empty.</p><p>Example: type <code>a</code>, <code>b</code>, <code>c</code>, then undo twice gives <code>'a'</code>; redo once gives <code>'ab'</code>; typing <code>d</code> gives <code>'abd'</code>, and a further redo does nothing.</p>",
    constraints=["1 &le; ops.length &le; 3,000", "ops[i] = [type, value] with type in {1, 2, 3, 4}", "value is in 1..26 for typing, and 0 for the other types"],
    hints=["Storing a copy of the whole text after every action is simple but uses a lot of memory and time for long texts. What small amount of information describes one action?",
           "Keep two stacks: actions that can be undone and actions that can be redone. Each action must remember which letter it typed or deleted.",
           "Undo of a type pops the last letter, undo of a backspace pushes the deleted letter back; redo does the opposite. A new type or effective backspace clears the redo stack."],
    editorial=["Model the editor with the text itself plus two stacks of actions. The <em>done</em> stack holds actions in the order they were applied, and the <em>undone</em> stack holds actions that were undone and may still be redone. An action is stored as its kind together with the letter it concerns, which is all that is needed to reverse or repeat it.",
               "Typing pushes the letter onto the text and onto <code>done</code>, and clears <code>undone</code>. A backspace on non-empty text pops the last letter, records it in <code>done</code> and clears <code>undone</code>; on empty text it is ignored completely, so it must not clear the redo history. Undo moves the top action from <code>done</code> to <code>undone</code> and reverses it on the text; redo moves it back and repeats it. Every operation is O(1), so the total time is O(n)."],
    time="O(n)", space="O(n)",
    solution='''def finalText(ops):
    text = []
    done = []      # (kind, letter): kind 1 = typed, 2 = deleted
    undone = []
    for kind, value in ops:
        if kind == 1:
            ch = chr(96 + value)
            text.append(ch)
            done.append((1, ch))
            undone.clear()
        elif kind == 2:
            if text:
                done.append((2, text.pop()))
                undone.clear()
        elif kind == 3:
            if done:
                k, ch = done.pop()
                if k == 1:
                    text.pop()
                else:
                    text.append(ch)
                undone.append((k, ch))
        else:
            if undone:
                k, ch = undone.pop()
                if k == 1:
                    text.append(ch)
                else:
                    text.pop()
                done.append((k, ch))
    return "".join(text)
''',
    tests=[[[[1, 1], [1, 2], [1, 3], [3, 0], [3, 0], [4, 0], [1, 4], [4, 0]]],
           [[[1, 1], [2, 0], [3, 0], [3, 0], [4, 0]]],
           [[[2, 0], [1, 5]]],
           [[[3, 0], [4, 0], [1, 7]]],
           [[[1, 1], [1, 2], [2, 0], [2, 0], [3, 0], [3, 0], [3, 0], [3, 0]]],
           [[[1, 3], [3, 0], [1, 4], [4, 0]]],
           [[[1, 1], [1, 2], [3, 0], [2, 0], [4, 0]]],
           [[[2, 0], [2, 0], [3, 0], [4, 0]]],
           [[[1, 26], [1, 1], [2, 0], [3, 0], [3, 0], [4, 0], [4, 0], [4, 0]]],
           [[[1, 1], [3, 0], [3, 0], [4, 0], [4, 0], [4, 0]]],
           [[[1, 9], [1, 10], [1, 11], [2, 0], [3, 0], [3, 0], [3, 0], [4, 0], [4, 0], [2, 0], [3, 0]]]],
)
_r = rnd(9708)


def _gen_ops(r, n, w):
    out = []
    for _ in range(n):
        k = r.choices([1, 2, 3, 4], weights=w)[0]
        out.append([1, r.randint(1, 26)] if k == 1 else [k, 0])
    return out


p["tests"].append([_gen_ops(_r, 3000, [5, 2, 2, 2])])
p["tests"].append([_gen_ops(_r, 3000, [8, 1, 1, 1])])
p["tests"].append([_gen_ops(_r, 2999, [3, 3, 5, 5])])
p["tests"].append([[[1, _r.randint(1, 26)] for _ in range(1500)] + [[3, 0]] * 1100 + [[4, 0]] * 300])


def b_editor(ops):
    states = [""]
    ptr = 0
    for kind, value in ops:
        if kind == 1:
            del states[ptr + 1:]
            states.append(states[ptr] + chr(96 + value))
            ptr += 1
        elif kind == 2:
            if states[ptr]:
                del states[ptr + 1:]
                states.append(states[ptr][:-1])
                ptr += 1
        elif kind == 3:
            if ptr > 0:
                ptr -= 1
        else:
            if ptr < len(states) - 1:
                ptr += 1
    return states[ptr]


def v_editor(tests):
    for t in tests:
        ops = t["args"][0]
        assert 1 <= len(ops) <= 3000
        for kind, value in ops:
            assert kind in (1, 2, 3, 4)
            assert (1 <= value <= 26) if kind == 1 else value == 0


CHECKS["text-editor-undo-redo-final-text"] = (b_editor, lambda r: [_gen_ops(r, r.randint(1, 14), [4, 2, 2, 2])], "exact")
VALIDATE["text-editor-undo-redo-final-text"] = v_editor


p = add(
    id="merge-equal-letters-into-next", title="Merge Equal Letters Into the Next Letter", diff="Medium", topic=TOPIC, tier="extra",
    fn="mergeLetters", params=[("s", "string")], ret="string", cmp="exact",
    desc="<p>A row of tiles is described by a string <code>s</code> of lowercase letters. Whenever two <em>neighbouring</em> tiles carry the same letter <code>x</code>, they merge into one tile with the next letter of the alphabet (<code>a, a</code> become <code>b</code>; <code>b, b</code> become <code>c</code>; and so on). Two neighbouring <code>'z'</code> tiles cannot grow any further and simply disappear. A merged tile can immediately merge again with a neighbour.</p><p>Repeat while two equal neighbours exist, always merging the <em>leftmost</em> such pair first, and return the final string. It may be empty.</p><p>Examples: <code>'aaa'</code> becomes <code>'ba'</code>. <code>'aab'</code> becomes <code>'bb'</code> and then <code>'c'</code>. <code>'zzab'</code> becomes <code>'ab'</code>.</p>",
    constraints=["1 &le; s.length &le; 10,000", "s consists of lowercase English letters", "The answer may be the empty string"],
    hints=["After a merge the new tile may be equal to its left neighbour, so merges can cascade backwards through the already processed part.",
           "Because the leftmost pair is always handled first, everything left of the current position never contains an equal pair. Process tiles one at a time.",
           "Keep a stack of settled tiles. For each incoming letter, while the top of the stack equals it, pop the top and replace the incoming letter by the next one (dropping it completely after a pair of <code>'z'</code>); then push what is left."],
    editorial=["Scan from left to right with a stack of tiles that currently have no equal neighbours. When a new letter <code>c</code> comes, compare it with the top. If they are equal, both tiles merge: pop the top and let the new letter become <code>c + 1</code> (or vanish if <code>c</code> was <code>'z'</code>). The merged tile is now the incoming tile and may again equal the new top, so repeat. When the loop ends, push the tile if it still exists.",
               "This is exactly the leftmost-pair-first process: the stack holds the prefix, in which no pair exists, so the leftmost pair is always the one formed by the incoming tile and the top. Each merge reduces the number of tiles by one, and each letter is pushed at most once, so the total work is O(n) amortised. The final stack is the answer."],
    time="O(n)", space="O(n)",
    solution='''def mergeLetters(s):
    stack = []
    for ch in s:
        c = ord(ch) - 97
        while c is not None and stack and stack[-1] == c:
            stack.pop()
            c = c + 1 if c < 25 else None
        if c is not None:
            stack.append(c)
    return "".join(chr(97 + c) for c in stack)
''',
    tests=[["aaa"], ["aab"], ["zzab"], ["a"], ["aa"], ["zz"], ["zzz"], ["abab"], ["aabb"], ["abba"], ["aaaa"], ["yyzz"], ["aabbaabb"], ["baa"], ["yyyy"]],
)
_r = rnd(9709)
p["tests"].append(["a" * 8192])
p["tests"].append(["a" * 9999])
p["tests"].append(["".join(_r.choice("abc") for _ in range(10000))])
p["tests"].append(["".join(_r.choice("ab") for _ in range(10000))])


def b_merge(s):
    t = [ord(c) - 97 for c in s]
    while True:
        for i in range(len(t) - 1):
            if t[i] == t[i + 1]:
                t[i:i + 2] = [t[i] + 1] if t[i] < 25 else []
                break
        else:
            return "".join(chr(97 + c) for c in t)


def v_merge(tests):
    for t in tests:
        assert 1 <= len(t["args"][0]) <= 10000 and _is_lower(t["args"][0])


CHECKS["merge-equal-letters-into-next"] = (b_merge, lambda r: [r.choice([lambda: "".join(r.choice("abc") for _ in range(r.randint(1, 14))), lambda: "".join(r.choice("abyz") for _ in range(r.randint(1, 14)))])()], "exact")
VALIDATE["merge-equal-letters-into-next"] = v_merge


# ---------------------------------------------------------------- HARD

p = add(
    id="count-substrings-that-cancel-completely", title="Count Substrings That Cancel Completely", diff="Hard", topic=TOPIC, tier="extra",
    fn="countCancelingSubstrings", params=[("s", "string")], ret="int", cmp="exact",
    desc="<p>Call a string <em>self-cancelling</em> if it can be reduced to the empty string by repeatedly deleting two neighbouring equal letters (the letters on both sides then close up). For example <code>'abba'</code> and <code>'aabb'</code> are self-cancelling, while <code>'aba'</code> and <code>'abab'</code> are not.</p><p>Given a string <code>s</code> of lowercase letters, return how many <em>non-empty substrings</em> of <code>s</code> are self-cancelling. Substrings are counted by their positions, so equal substrings at different places count separately.</p><p>Example: <code>'abba'</code> has 2 such substrings (<code>'bb'</code> and the whole string); <code>'aaaa'</code> has 4 (three copies of <code>'aa'</code> and the whole string).</p>",
    constraints=["1 &le; s.length &le; 10,000", "s consists of lowercase English letters"],
    hints=["Testing every substring by running the stack reduction on it takes O(n<sup>3</sup>) time in total, and even sharing work between substrings is quadratic.",
           "Reduce the prefixes of <code>s</code>. When is the substring from position <code>i</code> to <code>j</code> cancelled completely in terms of the reduced prefixes ending at <code>i</code> and at <code>j</code>?",
           "It cancels exactly when the reduced prefixes (the stack contents) at <code>i</code> and at <code>j</code> are identical. Give every distinct stack content an id using a trie that you walk down on push and up on pop, count how many prefixes share each id, and sum <code>c * (c - 1) / 2</code>."],
    editorial=["Let <code>R(i)</code> be the fully reduced form of the prefix of length <code>i</code>, which is exactly the stack content after reading <code>i</code> letters. The reduction is order independent, and it behaves like a group in which every letter is its own inverse. The substring <code>s[i..j)</code> cancels completely if and only if <code>R(i) = R(j)</code>: if it cancels, appending it to the prefix changes nothing; and if the two reduced prefixes are equal, then the letters between them must multiply to the identity, i.e. cancel.",
               "To compare reduced forms in O(1), represent each stack content by a node in a trie: the empty stack is the root, pushing letter <code>c</code> moves to (or creates) the child labelled <code>c</code>, and popping moves to the parent. Two prefixes have the same stack content exactly when they are at the same trie node. Count how many of the <code>n + 1</code> prefixes (including the empty prefix) end at each node; every unordered pair of prefixes at the same node is one self-cancelling substring, giving the sum of <code>c * (c - 1) / 2</code>. Time O(n), space O(n)."],
    time="O(n)", space="O(n)",
    solution='''def countCancelingSubstrings(s):
    parent = [0]          # trie node -> parent node
    label = [None]        # trie node -> letter on the edge from its parent
    child = {}            # (node, letter) -> node
    seen = [1]            # number of prefixes that ended at the node
    node = 0
    for ch in s:
        if node != 0 and label[node] == ch:
            node = parent[node]
        else:
            key = (node, ch)
            nxt = child.get(key)
            if nxt is None:
                nxt = len(parent)
                child[key] = nxt
                parent.append(node)
                label.append(ch)
                seen.append(0)
            node = nxt
        seen[node] += 1
    return sum(c * (c - 1) // 2 for c in seen)
''',
    tests=[["abba"], ["aaaa"], ["a"], ["aa"], ["ab"], ["abab"], ["aabb"], ["abcddcba"], ["abccbaabccba"], ["aabbaabb"], ["abcabc"], ["xyyxzzxyyx"]],
)
_r = rnd(9710)
p["tests"].append(["a" * 10000])
p["tests"].append(["".join(_r.choice("ab") for _ in range(10000))])
p["tests"].append(["".join(_r.choice("abc") for _ in range(10000))])
_left = "".join(_r.choice("abcd") for _ in range(2500))
p["tests"].append([_left + _left[::-1] + _left + _left[::-1]])


def _reduces(t):
    st = []
    for c in t:
        if st and st[-1] == c:
            st.pop()
        else:
            st.append(c)
    return not st


def b_cancel_sub(s):
    return sum(1 for i in range(len(s)) for j in range(i + 1, len(s) + 1) if _reduces(s[i:j]))


def g_cancel_sub(r):
    return ["".join(r.choice("abc") for _ in range(r.randint(1, 14)))]


def v_cancel_sub(tests):
    for t in tests:
        s = t["args"][0]
        assert 1 <= len(s) <= 10000 and _is_lower(s)


CHECKS["count-substrings-that-cancel-completely"] = (b_cancel_sub, g_cancel_sub, "exact")
VALIDATE["count-substrings-that-cancel-completely"] = v_cancel_sub


p = add(
    id="min-deletions-to-cancel-completely", title="Minimum Deletions to Cancel Completely", diff="Hard", topic=TOPIC, tier="extra",
    fn="minDeletionsToCancel", params=[("s", "string")], ret="int", cmp="exact",
    desc="<p>You may delete any characters from the string <code>s</code> (not necessarily neighbouring ones). The remaining characters keep their order. You want the remaining string to be <em>self-cancelling</em>: it can be reduced to the empty string by repeatedly deleting two neighbouring equal letters.</p><p>Return the minimum number of characters you must delete. Deleting every character is always allowed, so an answer exists.</p><p>Example: <code>'abccba'</code> needs <code>0</code> deletions (<code>cc</code>, then <code>bb</code>, then <code>aa</code> cancel). For <code>'abcab'</code> the answer is <code>3</code>: keeping only the two <code>a</code>'s (or the two <code>b</code>'s) is the best possible.</p>",
    constraints=["1 &le; s.length &le; 120", "s consists of lowercase English letters"],
    hints=["A string is self-cancelling exactly when its letters can be matched in equal pairs so that no two pairs cross (pairs may be nested or side by side). So you want the largest such matching among the letters of <code>s</code>.",
           "Use interval dynamic programming: <code>f(i, j)</code> is the largest number of letters of <code>s[i..j)</code> that can be matched in this way. Look at the first letter of the interval.",
           "Either the first letter is not used: <code>f(i + 1, j)</code>. Or it is paired with a later equal letter at position <code>k</code>: <code>2 + f(i + 1, k) + f(k + 1, j)</code>. The answer is <code>n - f(0, n)</code>."],
    editorial=["Deleting two neighbouring equal letters is a non-crossing pairing: every deleted pair encloses only letters that were removed earlier. Conversely, any set of letter pairs of equal letters that are pairwise non-crossing can be removed from the inside out. So the kept string is self-cancelling if and only if it admits a perfect non-crossing matching of equal letters, and we want the maximum number of letters taking part in such a matching.",
               "Let <code>f(i, j)</code> be that maximum for the half-open interval <code>[i, j)</code>. Either position <code>i</code> is unused (<code>f(i + 1, j)</code>), or it is matched to some <code>k</code> with <code>s[k] = s[i]</code>, which splits the problem into the inside <code>[i + 1, k)</code> and the outside part <code>[k + 1, j)</code>, adding 2 for the pair. Fill the table by decreasing <code>i</code>. There are O(n<sup>2</sup>) states and O(n) transitions each, so the time is O(n<sup>3</sup>) with O(n<sup>2</sup>) space, fine for n &le; 120."],
    time="O(n^3)", space="O(n^2)",
    solution='''def minDeletionsToCancel(s):
    n = len(s)
    same = [[k for k in range(i + 1, n) if s[k] == s[i]] for i in range(n)]
    f = [[0] * (n + 2) for _ in range(n + 2)]
    for i in range(n - 1, -1, -1):
        for j in range(i + 1, n + 1):
            best = f[i + 1][j]
            for k in same[i]:
                if k >= j:
                    break
                cand = 2 + f[i + 1][k] + f[k + 1][j]
                if cand > best:
                    best = cand
            f[i][j] = best
    return n - f[0][n]
''',
    tests=[["abccba"], ["abcab"], ["a"], ["aa"], ["ab"], ["abab"], ["aabb"], ["abcabc"], ["abcdefg"], ["aabaab"], ["abaabbab"], ["abcbcaabccb"]],
)
_r = rnd(9711)
p["tests"].append(["".join(_r.choice("ab") for _ in range(120))])
p["tests"].append(["".join(_r.choice("abc") for _ in range(120))])
p["tests"].append(["".join(_r.choice("abcdefghij") for _ in range(120))])
p["tests"].append(["a" * 119])
p["tests"].append(["ab" * 60])


def b_mindel(s):
    n = len(s)
    best = 0
    for mask in range(1 << n):
        st = []
        for i in range(n):
            if mask >> i & 1:
                if st and st[-1] == s[i]:
                    st.pop()
                else:
                    st.append(s[i])
        if not st:
            best = max(best, bin(mask).count("1"))
    return n - best


def g_mindel(r):
    return ["".join(r.choice("abc") for _ in range(r.randint(1, 11)))]


def v_mindel(tests):
    for t in tests:
        s = t["args"][0]
        assert 1 <= len(s) <= 120 and _is_lower(s)


CHECKS["min-deletions-to-cancel-completely"] = (b_mindel, g_mindel, "exact")
VALIDATE["min-deletions-to-cancel-completely"] = v_mindel
