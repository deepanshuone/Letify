"""Problems: Stack, string stack simulations (cancelling, decoding, paths, call logs). See data/lib.py for the registry."""
import heapq
import re

from lib import add, rnd, CHECKS, VALIDATE, gen_arr  # noqa: F401

TOPIC = "Stack"
INT_MIN, INT_MAX = -(2 ** 31), 2 ** 31 - 1


# ---------------------------------------------------------------- EASY

p = add(
    id="cancel-adjacent-equal-letters", title="Cancel Adjacent Equal Letters", diff="Easy", topic=TOPIC, tier="common",
    fn="cancelAdjacentEqual", params=[("s", "string")], ret="string", cmp="exact",
    desc="<p>A string <code>s</code> of lowercase letters is cleaned in rounds. In every round you pick two <em>neighbouring</em> positions that hold the same letter and delete both of them; the characters on the two sides then close up and become neighbours. You keep doing this for as long as such a pair exists.</p><p>Return the string that remains when no more pairs can be deleted. The final string does not depend on which pair you choose first. It may be empty.</p><p>Example: <code>'abbaca'</code> becomes <code>'aaca'</code> after deleting <code>bb</code>, then <code>'ca'</code> after deleting <code>aa</code>, so the answer is <code>'ca'</code>.</p>",
    constraints=["1 &le; s.length &le; 10,000", "s consists of lowercase English letters", "The answer may be the empty string"],
    hints=["Simulating the rounds by searching for a pair and rebuilding the string each time can take O(n<sup>2</sup>) time.",
           "Only the letter just before the current one can ever form a pair with it. The characters you have already kept behave like a pile where only the last one is reachable.",
           "Scan left to right with a stack of kept letters. If the new letter equals the top of the stack, pop (the pair cancels); otherwise push it. The stack is the answer."],
    editorial=["Process the letters from left to right and keep the survivors in a stack. When a new letter arrives, the only candidate partner is the most recently kept letter, which is the top of the stack. If they are equal, the pair is deleted, so pop the top and drop the new letter. Otherwise the new letter becomes the new top.",
               "Deleting a pair can expose two letters that were separated before, and the stack handles that automatically: after a pop, the new top is exactly the letter that became adjacent to the next incoming one. Each letter is pushed and popped at most once, so the time is O(n) with O(n) space for the stack."],
    time="O(n)", space="O(n)",
    solution='''def cancelAdjacentEqual(s):
    stack = []
    for ch in s:
        if stack and stack[-1] == ch:
            stack.pop()
        else:
            stack.append(ch)
    return "".join(stack)
''',
    tests=[["abbaca"], ["azxxzy"], ["a"], ["aa"], ["abc"], ["abba"], ["aaa"], ["aaaa"], ["abccba"], ["abcddcbaef"], ["xyyxzzw"]],
)
_r = rnd(9501)
p["tests"].append(["".join(_r.choice("ab") for _ in range(9000))])
p["tests"].append(["".join(_r.choice("abcdefghijklmnopqrstuvwxyz") for _ in range(10000))])
_left = "".join(_r.choice("abcdefghijklmnopqrstuvwxyz") for _ in range(4000))
p["tests"].append([_left + "q" + _left[::-1]])
p["tests"].append(["a" * 9999])


def b_cancel(s):
    while True:
        for i in range(len(s) - 1):
            if s[i] == s[i + 1]:
                s = s[:i] + s[i + 2:]
                break
        else:
            return s


def g_cancel(r):
    return ["".join(r.choice("abc") for _ in range(r.randint(1, 12)))]


def v_cancel(tests):
    for t in tests:
        s = t["args"][0]
        assert 1 <= len(s) <= 10000 and s.isalpha() and s.islower() and s.isascii()


CHECKS["cancel-adjacent-equal-letters"] = (b_cancel, g_cancel, "exact")
VALIDATE["cancel-adjacent-equal-letters"] = v_cancel


def gen_score_ops(r, n, plain_hi, cap):
    st, ops = [], []
    for _ in range(n):
        roll = r.random()
        if not st or roll < 0.45:
            v = r.randint(0, plain_hi)
            st.append(v)
            ops.append(v)
        elif roll < 0.62:
            st.pop()
            ops.append(-1)
        elif roll < 0.81 and 2 * st[-1] <= cap:
            st.append(2 * st[-1])
            ops.append(-2)
        elif len(st) >= 2 and st[-1] + st[-2] <= cap:
            st.append(st[-1] + st[-2])
            ops.append(-3)
        else:
            v = r.randint(0, plain_hi)
            st.append(v)
            ops.append(v)
    return ops


p = add(
    id="scoreboard-with-corrections", title="Scoreboard With Corrections", diff="Easy", topic=TOPIC, tier="extra",
    fn="scoreboardTotal", params=[("ops", "int[]")], ret="int", cmp="exact",
    desc="<p>A referee writes down scores on a sheet, one entry after another, and sometimes corrects the sheet. You are given the list <code>ops</code>; each element is one action:</p><ul><li>A value <code>x &ge; 0</code>: a new score <code>x</code> is written at the end of the sheet.</li><li><code>-1</code>: the <em>last score still on the sheet</em> is crossed out and no longer counts.</li><li><code>-2</code>: a new score equal to <strong>twice</strong> the last score still on the sheet is written.</li><li><code>-3</code>: a new score equal to the <strong>sum of the last two scores</strong> still on the sheet is written.</li></ul><p>Return the sum of all scores that remain on the sheet after every action. The actions are always possible: whenever one refers to the last one or two scores, they exist.</p><p>Example: <code>[5, 2, -1, -2, -3]</code>: the sheet is <code>[5, 2]</code>, then <code>[5]</code>, then <code>[5, 10]</code>, then <code>[5, 10, 15]</code>, so the answer is 30.</p>",
    constraints=["1 &le; ops.length &le; 5,000", "Every element is either -1, -2, -3 or a score between 0 and 100,000", "Every score written by a -2 or -3 action is at most 100,000", "Each action has the scores it needs on the sheet"],
    hints=["Only the end of the sheet is ever read or changed.",
           "Keep the scores that are still valid in a list where you only append and remove at the end.",
           "Use a stack. A score pushes its value, <code>-1</code> pops, <code>-2</code> pushes <code>2 * top</code>, <code>-3</code> pushes <code>top + second from top</code>. Return the sum of the stack at the end."],
    editorial=["The sheet behaves as a stack: every action reads or removes the newest scores and every new score goes on top. Walk through <code>ops</code> once, maintain the list of valid scores, and apply each action to its end.",
               "For the sum of the last two scores, read <code>stack[-1] + stack[-2]</code> before pushing. A cancelled score is simply popped, so later actions see the entry below it. At the end return <code>sum(stack)</code>. Every action takes O(1), so the total is O(n) time and O(n) space. With at most 5,000 actions and scores at most 100,000 the total stays below 2<sup>31</sup>."],
    time="O(n)", space="O(n)",
    solution='''def scoreboardTotal(ops):
    stack = []
    for op in ops:
        if op >= 0:
            stack.append(op)
        elif op == -1:
            stack.pop()
        elif op == -2:
            stack.append(2 * stack[-1])
        else:
            stack.append(stack[-1] + stack[-2])
    return sum(stack)
''',
    tests=[[[5, 2, -1, -2, -3]], [[5, -2, -3]], [[7]], [[0, 0, -3, -2]], [[1, 1, -3, -3, -3, -3]], [[3, -1, 4, -1, 5]],
           [[10, 20, 30, -1, -1, -1, 1]], [[50000, -2, -1, -2]], [[2, 3, -3, -1, -2, -3]], [[1, -2, -2, -2, -1, -1, -1, 9]]],
)
_r = rnd(9502)
p["tests"].append([gen_score_ops(_r, 5000, 1000, 100000)])
p["tests"].append([gen_score_ops(_r, 4000, 100000, 100000)])
p["tests"].append([[50000] * 2500 + [-3, -1] * 800])


def b_score(ops):
    vals, alive = [], []

    def last_alive(skip=0):
        c = 0
        for j in range(len(vals) - 1, -1, -1):
            if alive[j]:
                if c == skip:
                    return j
                c += 1

    for op in ops:
        if op >= 0:
            vals.append(op)
            alive.append(True)
        elif op == -1:
            alive[last_alive()] = False
        elif op == -2:
            vals.append(2 * vals[last_alive()])
            alive.append(True)
        else:
            vals.append(vals[last_alive()] + vals[last_alive(1)])
            alive.append(True)
    return sum(v for v, a in zip(vals, alive) if a)


def v_score(tests):
    for t in tests:
        ops = t["args"][0]
        assert 1 <= len(ops) <= 5000
        st = []
        for op in ops:
            assert op in (-1, -2, -3) or 0 <= op <= 100000
            if op >= 0:
                st.append(op)
            elif op == -1:
                st.pop()
            elif op == -2:
                st.append(2 * st[-1])
                assert st[-1] <= 100000
            else:
                st.append(st[-1] + st[-2])
                assert st[-1] <= 100000


CHECKS["scoreboard-with-corrections"] = (b_score, lambda r: [gen_score_ops(r, r.randint(1, 14), 9, 1000)], "exact")
VALIDATE["scoreboard-with-corrections"] = v_score


# ---------------------------------------------------------------- MEDIUM

def _comps_simplify(path):
    comps = [c for c in path.split("/") if c not in ("", ".")]
    while ".." in comps:
        i = comps.index("..")
        if i == 0:
            del comps[0]
        else:
            del comps[i - 1:i + 1]
    return comps


def gen_path(r, items, trailing=None):
    pool = [".", "..", "..", "a", "b", "c", "...", "a.b", "_x", "d1", ""]
    out = [r.choice(pool) for _ in range(items)]
    s = "/" + "/".join(out)
    if trailing is None:
        trailing = r.random() < 0.3
    return s + ("/" if trailing else "")


p = add(
    id="simplify-file-path", title="Simplify a File Path", diff="Medium", topic=TOPIC, tier="must",
    fn="simplifyPath", params=[("path", "string")], ret="string", cmp="exact",
    desc="<p>You are given an absolute Unix-style file path <code>path</code> that starts with <code>'/'</code>. Return its <em>canonical form</em>.</p><p>Split the path at <code>'/'</code> into components. A component is:</p><ul><li>empty (from repeated slashes such as <code>//</code> or a trailing slash): ignore it,</li><li><code>'.'</code>: the current directory, so ignore it,</li><li><code>'..'</code>: go up one directory. At the root, <code>'..'</code> does nothing,</li><li>anything else, including names such as <code>'...'</code> or <code>'a.b'</code>: a normal directory name.</li></ul><p>The canonical path starts with a single <code>'/'</code>, joins the remaining directory names with single slashes, and has no trailing slash (except when the answer is the root, which is just <code>'/'</code>).</p><p>Example: <code>'/a/./b/../../c/'</code> goes into <code>a</code>, stays, goes into <code>b</code>, up to <code>a</code>, up to the root, then into <code>c</code>, so the answer is <code>'/c'</code>.</p>",
    constraints=["1 &le; path.length &le; 10,000", "path consists of letters, digits, '.', '_' and '/'", "path starts with '/'", "No component other than '.' and '..' is ever treated specially (for example '...' is a normal name)"],
    hints=["Think of the current location as a list of directory names from the root. What does each kind of component do to that list?",
           "A normal name is appended, <code>'..'</code> removes the last name if there is one, and <code>''</code> and <code>'.'</code> change nothing.",
           "Split on <code>'/'</code>, process the components with a stack, and join the stack with <code>'/'</code> after a leading slash. An empty stack gives <code>'/'</code>."],
    editorial=["The current directory is a path of names, and every operation touches only its end, so a stack is the natural model. Split the string at <code>'/'</code> and handle each component: skip <code>''</code> and <code>'.'</code>, pop for <code>'..'</code> when the stack is not empty (going up from the root stays at the root), and push anything else.",
               "Finally build the answer as <code>'/' + '/'.join(stack)</code>. For an empty stack this is just <code>'/'</code>, which is correct. Be careful that <code>'...'</code> is a legal name and must be pushed. The work is linear in the length of the path: O(n) time and O(n) space."],
    time="O(n)", space="O(n)",
    solution='''def simplifyPath(path):
    stack = []
    for part in path.split('/'):
        if part == '' or part == '.':
            continue
        if part == '..':
            if stack:
                stack.pop()
        else:
            stack.append(part)
    return '/' + '/'.join(stack)
''',
    tests=[["/home/"], ["/../"], ["/home//foo/"], ["/a/./b/../../c/"], ["/"], ["//"], ["/..."], ["/a/.."], ["/a/b/c/../../.."],
           ["/../../a"], ["/a//b////c/d//././/.."], ["/.hidden/..x/a.b/_/../..."], ["/a/b/../../../../x/y/./z"]],
)
_r = rnd(9503)
p["tests"].append([gen_path(_r, 2500)])
p["tests"].append(["/" + "/".join(_r.choice(["a", "bb", "c1", "d"]) for _ in range(1800)) + "/" + "/".join([".."] * 1700)])
p["tests"].append(["/" + "../" * 3000 + "x"])


def b_simplify(path):
    comps = _comps_simplify(path)
    return "/" + "/".join(comps)


def g_simplify(r):
    return [gen_path(r, r.randint(0, 12))]


def v_simplify(tests):
    for t in tests:
        s = t["args"][0]
        assert 1 <= len(s) <= 10000 and s[0] == "/"
        assert all(c.isalnum() or c in "._/" for c in s) and s.isascii()
        e = t["expected"]
        assert e == "/" or (e[0] == "/" and e[-1] != "/" and "//" not in e)


CHECKS["simplify-file-path"] = (b_simplify, g_simplify, "exact")
VALIDATE["simplify-file-path"] = v_simplify


def enc_gen(r, depth, kmax=4):
    parts, total = [], 0
    for _ in range(r.randint(1, 3)):
        if depth > 0 and r.random() < 0.5:
            k = r.randint(1, kmax)
            inner, ilen = enc_gen(r, depth - 1, kmax)
            parts.append("%d[%s]" % (k, inner))
            total += k * ilen
        else:
            lit = "".join(r.choice("abcxyz") for _ in range(r.randint(1, 3)))
            parts.append(lit)
            total += len(lit)
    return "".join(parts), total


def enc_big(r, target_dec, max_enc):
    enc, tot = "", 0
    while True:
        e, d = enc_gen(r, 3, 5)
        if tot + d > target_dec or len(enc) + len(e) > max_enc:
            if tot > 0:
                return enc
            continue
        enc += e
        tot += d
        if tot > target_dec * 0.9:
            return enc


p = add(
    id="decode-nested-repeats", title="Decode a Nested Repeat String", diff="Medium", topic=TOPIC, tier="must",
    fn="decodeRepeats", params=[("s", "string")], ret="string", cmp="exact",
    desc="<p>A string is compressed with the rule <code>k[text]</code>, which means that <code>text</code> is written <code>k</code> times in a row. The <code>text</code> inside the brackets may itself contain letters and further <code>k[...]</code> groups. Letters outside any group are written as they are.</p><p>Given a valid compressed string <code>s</code>, return the full decoded string. Every number is a positive integer and is always followed directly by <code>'['</code>; numbers can have several digits.</p><p>Examples: <code>'3[a]2[bc]'</code> decodes to <code>'aaabcbc'</code>, and <code>'3[a2[c]]'</code> decodes to <code>'accaccacc'</code>.</p>",
    constraints=["1 &le; s.length &le; 5,000", "s consists of lowercase letters, digits and the brackets '[' and ']'; it is well formed", "Every number k satisfies 1 &le; k &le; 300 and is immediately followed by '['; every group has non-empty text", "The decoded string has at most 20,000 characters"],
    hints=["Decoding from left to right is easy until you meet a group. What do you need to remember when a <code>'['</code> starts a new group?",
           "When you enter a group, save the text built so far and the number in front of the bracket, then start collecting a fresh text for the group.",
           "Use a stack. On <code>'['</code> push (text so far, k) and reset the text. On <code>']'</code> pop (prev, k) and set the text to <code>prev + text * k</code>. Digits build up k, letters extend the text."],
    editorial=["A group can be nested inside another group, and the outer one can only be finished after the inner one. That is last-in, first-out, so use a stack. Keep the current text and the number being read. Digits update the number as <code>k = 10*k + digit</code>. When you read <code>'['</code>, push the pair <code>(current text, k)</code> on the stack and start with an empty text and <code>k = 0</code>.",
               "When you read <code>']'</code>, pop <code>(previous text, k)</code> and replace the current text by <code>previous + current * k</code>. Letters are appended to the current text. At the end the current text is the answer. Each character of the output is created and copied only a bounded number of times per nesting level, so the work is proportional to the size of the output times the nesting depth in the worst case; with a 20,000 character output this is tiny. Space is O(output)."],
    time="O(output size * depth)", space="O(output size)",
    solution='''def decodeRepeats(s):
    stack = []
    cur = ""
    k = 0
    for ch in s:
        if ch.isdigit():
            k = k * 10 + int(ch)
        elif ch == '[':
            stack.append((cur, k))
            cur = ""
            k = 0
        elif ch == ']':
            prev, times = stack.pop()
            cur = prev + cur * times
        else:
            cur += ch
    return cur
''',
    tests=[["3[a]2[bc]"], ["3[a2[c]]"], ["2[abc]3[cd]ef"], ["abc"], ["1[a]"], ["10[a]"], ["100[ab]"], ["2[a2[b2[c]]]"], ["a2[b]c3[d]e"],
           ["12[3[x]y]"], ["2[2[2[2[z]]]]q"], ["4[ab]2[c]d"]],
)
_r = rnd(9504)
p["tests"].append([enc_big(_r, 12000, 4500)])
p["tests"].append(["2[" * 12 + "ab" + "]" * 12])
p["tests"].append(["".join(_r.choice("abcdefghijklmnopqrstuvwxyz") for _ in range(4000)) + "100[xy]"])


def b_decode(s):
    pat = re.compile(r"(\d+)\[([a-z]*)\]")
    while True:
        t = pat.sub(lambda m: m.group(2) * int(m.group(1)), s)
        if t == s:
            return s
        s = t


def g_decode(r):
    return [enc_gen(r, r.randint(0, 3), 6)[0]]


def v_decode(tests):
    for t in tests:
        s = t["args"][0]
        assert 1 <= len(s) <= 5000 and re.fullmatch(r"[a-z0-9\[\]]+", s)
        assert re.fullmatch(r"(?:[a-z]|\d+\[|\])+", s)
        for m in re.finditer(r"\d+", s):
            assert 1 <= int(m.group()) <= 300 and not m.group().startswith("0") and s[m.end()] == "["
        assert "[]" not in s
        assert len(t["expected"]) <= 20000
        assert "[" not in t["expected"] and "]" not in t["expected"] and not any(c.isdigit() for c in t["expected"])


CHECKS["decode-nested-repeats"] = (b_decode, g_decode, "exact")
VALIDATE["decode-nested-repeats"] = v_decode


def gen_runs(r, base_len, inserts, k, alpha):
    s = [r.choice(alpha) for _ in range(base_len)]
    for _ in range(inserts):
        pos = r.randint(0, len(s))
        c = r.choice(alpha)
        s[pos:pos] = [c] * k
    return "".join(s)


p = add(
    id="remove-k-equal-neighbours", title="Remove Runs of K Equal Letters", diff="Medium", topic=TOPIC, tier="common",
    fn="removeKEqualRuns", params=[("s", "string"), ("k", "int")], ret="string", cmp="exact",
    desc="<p>You are given a string <code>s</code> of lowercase letters and an integer <code>k</code>. In one step you choose <code>k</code> <em>consecutive</em> positions that all hold the same letter and delete them; the left and right parts then join together. Repeat for as long as it is possible.</p><p>Return the final string. The final string is the same whichever valid deletion you choose first. It may be empty.</p><p>Example: with <code>s = 'deeedbbcccbdaa'</code> and <code>k = 3</code>, delete <code>eee</code> to get <code>'ddbbcccbdaa'</code>, delete <code>ccc</code> to get <code>'ddbbbdaa'</code>, delete <code>bbb</code> to get <code>'dddaa'</code>, delete <code>ddd</code> to get <code>'aa'</code>.</p>",
    constraints=["1 &le; s.length &le; 10,000", "2 &le; k &le; 10,000", "s consists of lowercase English letters"],
    hints=["After a deletion, new runs of equal letters can appear, so a single left-to-right scan that only looks at the original runs is not enough.",
           "What you need to know about the letters kept so far is: what is the last letter, and how many copies of it are in a row at the end?",
           "Keep a stack of pairs (letter, run length). A new equal letter increases the top count; when the count reaches <code>k</code> pop the pair. A different letter pushes <code>(letter, 1)</code>."],
    editorial=["Store the kept characters as runs: a stack of <code>[letter, count]</code>. For each incoming letter, if the top run has the same letter, increase its count and pop the whole run if the count is now <code>k</code>. Otherwise push a new run <code>[letter, 1]</code>.",
               "Popping a run makes the run below it the new top, so letters on both sides of a deleted block can merge into one run, exactly as in the process described. The counts on the stack are always less than <code>k</code>. At the end expand each run into <code>letter * count</code> and join. The scan is O(n) time and O(n) space."],
    time="O(n)", space="O(n)",
    solution='''def removeKEqualRuns(s, k):
    stack = []   # [letter, run length]
    for ch in s:
        if stack and stack[-1][0] == ch:
            stack[-1][1] += 1
            if stack[-1][1] == k:
                stack.pop()
        else:
            stack.append([ch, 1])
    return "".join(c * n for c, n in stack)
''',
    tests=[["deeedbbcccbdaa", 3], ["abcd", 2], ["pbbcggttciiippooaais", 2], ["aaa", 3], ["aab", 3], ["a", 2], ["aabbaabb", 2],
           ["abbbaaac", 3], ["xyzzzyyxx", 3], ["aaaaa", 2], ["abcccbbbaaa", 3], ["zzzzzzzzzz", 10000]],
)
_r = rnd(9505)
p["tests"].append(["a" * 9999, 3])
p["tests"].append(["".join(_r.choice("ab") for _ in range(9000)), 3])
p["tests"].append([gen_runs(_r, 300, 2300, 4, "abcde")[:10000], 4])
p["tests"].append([gen_runs(_r, 50, 1900, 5, "xy"), 5])


def b_kruns(s, k):
    while True:
        for i in range(len(s) - k + 1):
            if s[i:i + k] == s[i] * k:
                s = s[:i] + s[i + k:]
                break
        else:
            return s


def g_kruns(r):
    return ["".join(r.choice("ab" if r.random() < 0.6 else "abc") for _ in range(r.randint(1, 14))), r.randint(2, 4)]


def v_kruns(tests):
    for t in tests:
        s, k = t["args"]
        assert 1 <= len(s) <= 10000 and s.isalpha() and s.islower() and s.isascii()
        assert 2 <= k <= 10000


CHECKS["remove-k-equal-neighbours"] = (b_kruns, g_kruns, "exact")
VALIDATE["remove-k-equal-neighbours"] = v_kruns


def gen_balanced(r, depth, items):
    out = []
    for _ in range(items):
        if depth > 0 and r.random() < 0.5:
            out.append("(" + gen_balanced(r, depth - 1, r.randint(0, 3)) + ")")
        else:
            out.append("".join(r.choice("abcdef") for _ in range(r.randint(1, 3))))
    return "".join(out)


p = add(
    id="reverse-inside-brackets", title="Reverse Text Inside Brackets", diff="Medium", topic=TOPIC, tier="common",
    fn="reverseInsideBrackets", params=[("s", "string")], ret="string", cmp="exact",
    desc="<p>The string <code>s</code> contains lowercase letters and balanced round brackets. Process the brackets from the <em>innermost</em> pair outwards: for each matching pair, reverse the whole text between the two brackets (as it looks at that moment) and remove the brackets themselves.</p><p>Return the final string, which has no brackets.</p><p>Example: <code>'(u(love)i)'</code>: the inner pair turns <code>love</code> into <code>evol</code>, giving <code>(uevoli)</code>; reversing that gives <code>iloveu</code>. Another: <code>'a(bc)d'</code> becomes <code>'acbd'</code>.</p>",
    constraints=["1 &le; s.length &le; 10,000", "s consists of lowercase letters '(' and ')'", "The brackets in s are balanced", "The answer may be empty, for example for '()'"],
    hints=["Reversing every bracket group directly costs O(length of group) each time, which can add up to O(n<sup>2</sup>) for deeply nested groups. First make it correct, then fast.",
           "A stack of partial results works: on <code>'('</code> start a new buffer; on <code>')'</code> reverse the buffer and append it to the buffer below.",
           "For O(n): first record the matching partner of every bracket with a stack. Then walk through the string; whenever you hit a bracket, jump to its partner and flip the walking direction."],
    editorial=["Simple solution: keep a stack of strings. A letter is appended to the top buffer. On <code>'('</code> push an empty buffer. On <code>')'</code> pop the top buffer, reverse it, and append it to the new top. This is easy to get right but can copy O(n) characters at each of O(n) nested levels.",
               "A linear solution uses the matching pairs. Precompute <code>pair[i]</code> with a stack. Start at index 0 moving right. When the pointer lands on a bracket, jump to its partner and reverse the direction, then continue stepping. Letters met along the way are output in exactly the order the nested reversals would produce, because passing through a bracket mirrors you into the group's text from the other side. Every character is visited once, so time is O(n) and space is O(n)."],
    time="O(n)", space="O(n)",
    solution='''def reverseInsideBrackets(s):
    n = len(s)
    pair = [0] * n
    st = []
    for i, c in enumerate(s):
        if c == '(':
            st.append(i)
        elif c == ')':
            j = st.pop()
            pair[i] = j
            pair[j] = i
    out = []
    i, d = 0, 1
    while 0 <= i < n:
        c = s[i]
        if c == '(' or c == ')':
            i = pair[i]
            d = -d
        else:
            out.append(c)
        i += d
    return "".join(out)
''',
    tests=[["(abcd)"], ["(u(love)i)"], ["(ed(et(oc))el)"], ["a(bc)d"], ["abc"], ["()"], ["((a))"], ["a(b(c)d)e"], ["(ab)(cd)"], ["x(y(z(w)v)u)t"], ["(a(b)(c)d)"]],
)
_r = rnd(9506)
_s = "x"
for _ in range(2400):
    _s = _r.choice("abcdefgh") + "(" + _s + ")" + _r.choice("abcdefgh")
p["tests"].append([_s])
p["tests"].append(["(" * 3000 + "".join(_r.choice("abcd") for _ in range(3000)) + ")" * 3000])
p["tests"].append([gen_balanced(_r, 7, 350)])


def b_revbr(s):
    pat = re.compile(r"\(([a-z]*)\)")
    while True:
        t = pat.sub(lambda m: m.group(1)[::-1], s)
        if t == s:
            return s
        s = t


def g_revbr(r):
    s = gen_balanced(r, r.randint(0, 4), r.randint(1, 4))
    return [s]


def v_revbr(tests):
    for t in tests:
        s = t["args"][0]
        assert 1 <= len(s) <= 10000 and re.fullmatch(r"[a-z()]+", s)
        d = 0
        for c in s:
            d += (c == "(") - (c == ")")
            assert d >= 0
        assert d == 0


CHECKS["reverse-inside-brackets"] = (b_revbr, g_revbr, "exact")
VALIDATE["reverse-inside-brackets"] = v_revbr


def gen_logs(r, n, pairs, maxgap, base=0):
    logs, stack = [], []
    lo_s = lo_e = base
    left = pairs
    while left > 0 or stack:
        if left > 0 and (not stack or r.random() < 0.5):
            t = lo_s + r.randint(0, maxgap)
            fid = r.randrange(n)
            logs.append([fid, 0, t])
            stack.append(fid)
            lo_s = lo_e = t
            left -= 1
        else:
            t = lo_e + r.randint(0, maxgap)
            fid = stack.pop()
            logs.append([fid, 1, t])
            lo_s, lo_e = t + 1, t
    return logs


p = add(
    id="exclusive-time-of-calls", title="Exclusive Running Time of Function Calls", diff="Medium", topic=TOPIC, tier="common",
    fn="exclusiveTimes", params=[("n", "int"), ("logs", "int[][]")], ret="int[]", cmp="exact",
    desc="<p>A single-threaded program has <code>n</code> functions numbered <code>0</code> to <code>n - 1</code>. Functions call each other (a function may even call itself), and a log records every call. Each log entry is <code>[id, type, t]</code>:</p><ul><li><code>type = 0</code>: a call of function <code>id</code> <strong>starts</strong> at the very beginning of time unit <code>t</code>.</li><li><code>type = 1</code>: the call of function <code>id</code> that is currently open and innermost <strong>ends</strong> at the very end of time unit <code>t</code>, so unit <code>t</code> still belongs to it.</li></ul><p>Only one function runs at any moment: the most recently started call that has not ended. When a call starts, the call that invoked it pauses until it ends. Time units in which no call is open belong to nobody.</p><p>Return an array <code>res</code> of length <code>n</code> where <code>res[f]</code> is the <em>exclusive time</em> of function <code>f</code>: the number of time units in which a call of <code>f</code> was the running one, summed over all its calls.</p><p>Example: <code>n = 2</code>, <code>logs = [[0,0,0],[1,0,2],[1,1,5],[0,1,6]]</code>. Function 0 runs in units 0, 1 and 6 (3 units); function 1 runs in units 2 to 5 (4 units). The answer is <code>[3, 4]</code>.</p>",
    constraints=["1 &le; n &le; 100", "2 &le; logs.length &le; 2,000 and logs.length is even", "0 &le; id &lt; n, type is 0 or 1, 0 &le; t &le; 10<sup>9</sup>", "The logs are valid: calls are properly nested, every call ends, and events appear in time order (a start has t at least the previous event's t, and strictly greater if the previous event was an end; an end has t at least the previous event's t)"],
    hints=["Between two consecutive log events, exactly one function (or nobody) is running. Can you charge each gap to the right function?",
           "Keep a stack of open calls. The running function is the top of the stack, and you can remember the time unit at which the current running stretch began.",
           "On a start at <code>t</code>: add <code>t - prev</code> to the function on top (if any), push, set <code>prev = t</code>. On an end at <code>t</code>: add <code>t + 1 - prev</code> to the top, pop, set <code>prev = t + 1</code>."],
    editorial=["Treat a start at time <code>t</code> as the point in time <code>t</code> and an end at time <code>t</code> as the point <code>t + 1</code>, since the end time unit is included. Then the logs describe a sequence of points on a time line, and between two consecutive points the running function is the top of the call stack.",
               "Keep <code>prev</code>, the point where the current stretch began. When a call starts, the caller (stack top) was running from <code>prev</code> until <code>t</code>, so credit it with <code>t - prev</code>, push the new call, and set <code>prev = t</code>. When a call ends at <code>t</code>, the top ran from <code>prev</code> to <code>t + 1</code>: credit <code>t + 1 - prev</code>, pop, and set <code>prev = t + 1</code>. Recursion needs no special handling because credit goes to the id of the stack top. One pass, O(m) time for m logs and O(m) space for the stack, independent of the size of the times."],
    time="O(m)", space="O(m)",
    solution='''def exclusiveTimes(n, logs):
    res = [0] * n
    stack = []
    prev = 0
    for fid, kind, t in logs:
        if kind == 0:
            if stack:
                res[stack[-1]] += t - prev
            stack.append(fid)
            prev = t
        else:
            res[stack.pop()] += t + 1 - prev
            prev = t + 1
    return res
''',
    tests=[[2, [[0, 0, 0], [1, 0, 2], [1, 1, 5], [0, 1, 6]]], [1, [[0, 0, 0], [0, 1, 0]]], [1, [[0, 0, 0], [0, 0, 1], [0, 0, 2], [0, 1, 3], [0, 1, 4], [0, 1, 5]]],
           [2, [[0, 0, 1], [0, 1, 3], [1, 0, 10], [1, 1, 12]]], [3, [[0, 0, 0], [1, 0, 0], [2, 0, 0], [2, 1, 0], [1, 1, 0], [0, 1, 0]]],
           [2, [[0, 0, 0], [1, 0, 3], [1, 1, 3], [0, 1, 3]]], [3, [[2, 0, 5], [1, 0, 6], [0, 0, 8], [0, 1, 9], [1, 1, 9], [2, 1, 20]]],
           [2, [[0, 0, 0], [1, 0, 1], [1, 1, 1], [1, 0, 2], [1, 1, 3], [0, 1, 1000000000]]], [4, [[3, 0, 100], [3, 1, 100], [0, 0, 101], [1, 0, 105], [1, 1, 105], [0, 1, 110]]]],
)
_r = rnd(9507)
p["tests"].append([100, gen_logs(_r, 100, 600, 20)])
p["tests"].append([5, gen_logs(_r, 5, 600, 800000)])
p["tests"].append([3, gen_logs(_r, 3, 500, 1)])


def b_excl(n, logs):
    res = [0] * n
    by_t = {}
    for fid, kind, t in logs:
        by_t.setdefault(t, []).append((fid, kind))
    stack = []
    for u in range(max(t for _, _, t in logs) + 1):
        ev = by_t.get(u, [])
        for fid, kind in ev:
            if kind == 0:
                stack.append(fid)
        if stack:
            res[stack[-1]] += 1
        for fid, kind in ev:
            if kind == 1:
                assert stack.pop() == fid
    return res


def g_excl(r):
    n = r.randint(1, 4)
    return [n, gen_logs(r, n, r.randint(1, 6), r.choice([0, 1, 3]), r.randint(0, 3))]


def v_excl(tests):
    for t in tests:
        n, logs = t["args"]
        assert 1 <= n <= 100 and 2 <= len(logs) <= 2000 and len(logs) % 2 == 0
        stack, prev = [], 0
        for fid, kind, tt in logs:
            assert 0 <= fid < n and kind in (0, 1) and 0 <= tt <= 10 ** 9
            if kind == 0:
                assert tt >= prev
                stack.append(fid)
                prev = tt
            else:
                assert stack.pop() == fid
                assert tt + 1 >= prev
                prev = tt + 1
        assert not stack
        assert all(v >= 0 for v in t["expected"])


CHECKS["exclusive-time-of-calls"] = (b_excl, g_excl, "exact")
VALIDATE["exclusive-time-of-calls"] = v_excl


def b_stackout(s):
    n = len(s)
    best = [None]

    def go(i, stack, out):
        if i == n and not stack:
            if best[0] is None or out < best[0]:
                best[0] = out
            return
        if i < n:
            go(i + 1, stack + [s[i]], out)
        if stack:
            go(i, stack[:-1], out + stack[-1])

    go(0, [], "")
    return best[0]


p = add(
    id="smallest-string-through-a-stack", title="Smallest String Through a Stack", diff="Medium", topic=TOPIC, tier="extra",
    fn="smallestStackOutput", params=[("s", "string")], ret="string", cmp="exact",
    desc="<p>You are given a string <code>s</code> of lowercase letters. You also have an empty stack <code>t</code> and an empty output string <code>p</code>. Two moves are allowed:</p><ul><li><strong>push</strong>: remove the first character of <code>s</code> and put it on top of <code>t</code>;</li><li><strong>pop</strong>: remove the top character of <code>t</code> and append it to the end of <code>p</code>.</li></ul><p>You keep moving until both <code>s</code> and <code>t</code> are empty. Return the lexicographically smallest string <code>p</code> that you can produce.</p><p>Examples: <code>'bac'</code> gives <code>'abc'</code> (push b, push a, pop a, pop b, push c, pop c). <code>'bdda'</code> gives <code>'addb'</code>.</p>",
    constraints=["1 &le; s.length &le; 10,000", "s consists of lowercase English letters"],
    hints=["The first output letter must be some letter that is reachable, so think about what you want to pop and when.",
           "Popping the top is never harmful when it is not larger than every letter still waiting in <code>s</code>. Why?",
           "Precompute <code>suffixMin[i]</code>, the smallest letter in <code>s[i:]</code>. After pushing <code>s[i]</code>, pop while the top is <code>&le; suffixMin[i+1]</code>. At the end pop everything."],
    editorial=["Greedy: the smallest possible next output letter is the smaller of the stack top and whatever can still arrive. If the stack top is not larger than every letter still in <code>s</code>, nothing better can come later, and popping it now is optimal (equal letters are fine to pop first, because the output is the same and keeping them would only block letters below them). If a strictly smaller letter is still waiting in <code>s</code>, we must push more characters until it gets to the top.",
               "Implement this with <code>suffixMin</code>. For each character, push it, then while the stack is non-empty and its top is <code>&le; suffixMin[i+1]</code> (use a letter after 'z' for the empty suffix) pop it to the output. After the last character the stack is emptied from top to bottom. Each character is pushed and popped once: O(n) time, O(n) space."],
    time="O(n)", space="O(n)",
    solution='''def smallestStackOutput(s):
    n = len(s)
    suf = ['{'] * (n + 1)
    for i in range(n - 1, -1, -1):
        suf[i] = min(s[i], suf[i + 1])
    stack, out = [], []
    for i, c in enumerate(s):
        stack.append(c)
        while stack and stack[-1] <= suf[i + 1]:
            out.append(stack.pop())
    while stack:
        out.append(stack.pop())
    return "".join(out)
''',
    tests=[["bac"], ["zza"], ["bdda"], ["a"], ["ab"], ["ba"], ["abc"], ["cba"], ["bcad"], ["dcbaabcd"], ["aaaa"], ["mnbmnbaz"]],
)
_r = rnd(9508)
p["tests"].append(["".join(_r.choice("abcdefghijklmnopqrstuvwxyz") for _ in range(8000))])
p["tests"].append(["".join(_r.choice("ab") for _ in range(8000))])
p["tests"].append(["".join(sorted("".join(_r.choice("abcdefghij") for _ in range(4000))))[::-1] + "a" * 3000])


def g_stackout(r):
    return ["".join(r.choice("abcd") for _ in range(r.randint(1, 8)))]


def v_stackout(tests):
    for t in tests:
        s = t["args"][0]
        assert 1 <= len(s) <= 10000 and s.isalpha() and s.islower() and s.isascii()
        assert sorted(t["expected"]) == sorted(s)


CHECKS["smallest-string-through-a-stack"] = (b_stackout, g_stackout, "exact")
VALIDATE["smallest-string-through-a-stack"] = v_stackout


# ---------------------------------------------------------------- HARD

ELEMS = ["H", "He", "O", "Mg", "Na", "Cl", "C", "Fe", "K", "S", "N", "Ca", "Zn", "Uuo", "B"]


def gen_formula(r, depth, items, mult_hi, cnt_hi):
    out = []
    for _ in range(items):
        if depth > 0 and r.random() < 0.45:
            inner = gen_formula(r, depth - 1, r.randint(1, 3), mult_hi, cnt_hi)
            out.append("(" + inner + ")" + (str(r.randint(1, mult_hi)) if r.random() < 0.75 else ""))
        else:
            out.append(r.choice(ELEMS) + (str(r.randint(1, cnt_hi)) if r.random() < 0.55 else ""))
    return "".join(out)


def count_atoms(f):
    n, i = len(f), 0
    stack = [{}]
    while i < n:
        c = f[i]
        if c == "(":
            stack.append({})
            i += 1
        elif c == ")":
            i += 1
            j = i
            while j < n and f[j].isdigit():
                j += 1
            mult = int(f[i:j]) if j > i else 1
            i = j
            top = stack.pop()
            for k, v in top.items():
                stack[-1][k] = stack[-1].get(k, 0) + v * mult
        else:
            j = i + 1
            while j < n and f[j].islower():
                j += 1
            name = f[i:j]
            i = j
            while j < n and f[j].isdigit():
                j += 1
            cnt = int(f[i:j]) if j > i else 1
            i = j
            stack[-1][name] = stack[-1].get(name, 0) + cnt
    return stack[0]


def big_formula(r, target, mult_hi, cnt_hi, depth):
    while True:
        f = ""
        while len(f) < target:
            f += gen_formula(r, depth, r.randint(2, 4), mult_hi, cnt_hi)
        f = f[:target + 40]
        # cut back to a valid formula: keep whole top-level pieces only
        d, cut = 0, 0
        for idx, c in enumerate(f):
            if c == "(":
                d += 1
            elif c == ")":
                d -= 1
            if d == 0 and (idx + 1 == len(f) or f[idx + 1].isupper()):
                cut = idx + 1
        f = f[:cut]
        if len(f) <= 1000 and f and max(count_atoms(f).values()) <= 10 ** 9:
            return f


p = add(
    id="count-atoms-in-formula", title="Count Atoms in a Chemical Formula", diff="Hard", topic=TOPIC, tier="common",
    fn="countAtoms", params=[("formula", "string")], ret="string", cmp="exact",
    desc="<p>A chemical formula is a string made of these parts:</p><ul><li>An <strong>element</strong>: one uppercase letter followed by zero or more lowercase letters, for example <code>H</code>, <code>Mg</code>, <code>Uuo</code>. An element may be followed by a <strong>count</strong>, a number written in digits without leading zeros (at least 1). With no count the element appears once.</li><li>A <strong>group</strong>: <code>(</code>, a non-empty formula, <code>)</code>, and optionally a count that multiplies every atom inside the group. No count means a multiplier of 1.</li></ul><p>Groups may be nested. Return the total number of atoms of every element in this canonical form: element names in <em>increasing alphabetical (ASCII) order</em>, each followed by its total count when that count is more than 1, all joined into one string.</p><p>Examples: <code>'H2O'</code> &rarr; <code>'H2O'</code>; <code>'Mg(OH)2'</code> &rarr; <code>'H2MgO2'</code>; <code>'K4(ON(SO3)2)2'</code> &rarr; <code>'K4N2O14S4'</code>.</p>",
    constraints=["1 &le; formula.length &le; 1,000", "The formula is well formed as described, with letters, digits and round brackets only", "Every count and multiplier is between 1 and 1,000,000 and has no leading zeros", "The total count of each element is at most 10<sup>9</sup>"],
    hints=["Without brackets this is a simple scan: read a name, read a number, add to a map. What changes when brackets appear?",
           "Counts inside brackets are only final after you see the multiplier after the <code>)</code>. Think about keeping a separate map for each open bracket.",
           "Use a stack of maps. On <code>(</code> push a fresh map. On <code>)</code> read the optional number, pop the top map, multiply its values, and add them into the map below. Finally sort the names of the bottom map."],
    editorial=["Parse left to right with an index. A stack of dictionaries holds the counts of every open group; the bottom dictionary is the whole formula. When you see an uppercase letter, read the following lowercase letters as the element name and the following digits as its count (default 1), and add the count to the top dictionary.",
               "On <code>(</code> push an empty dictionary. On <code>)</code> read the digits after it as the multiplier (default 1), pop the top dictionary, and add each of its counts times the multiplier into the dictionary that is now on top. At the end the bottom dictionary has the totals. Sort the names, and write <code>name</code> alone for count 1 or <code>name + count</code> otherwise. The scan is linear in the length; the sort adds O(k log k) for k distinct elements, and extra space is bounded by the nesting depth times the number of distinct elements."],
    time="O(n + k log k)", space="O(n)",
    solution='''def countAtoms(formula):
    n, i = len(formula), 0
    stack = [{}]
    while i < n:
        c = formula[i]
        if c == '(':
            stack.append({})
            i += 1
        elif c == ')':
            i += 1
            j = i
            while j < n and formula[j].isdigit():
                j += 1
            mult = int(formula[i:j]) if j > i else 1
            i = j
            top = stack.pop()
            cur = stack[-1]
            for name, cnt in top.items():
                cur[name] = cur.get(name, 0) + cnt * mult
        else:
            j = i + 1
            while j < n and formula[j].islower():
                j += 1
            name = formula[i:j]
            i = j
            while j < n and formula[j].isdigit():
                j += 1
            cnt = int(formula[i:j]) if j > i else 1
            i = j
            stack[-1][name] = stack[-1].get(name, 0) + cnt
    return "".join(k + (str(v) if v > 1 else "") for k, v in sorted(stack[0].items()))
''',
    tests=[["H2O"], ["Mg(OH)2"], ["K4(ON(SO3)2)2"], ["Be32"], ["H"], ["He"], ["HHe"], ["(H)"], ["((H2)3)4"], ["Fe(CN)6Fe3"],
           ["Ca(OH)2Ca(OH)2"], ["(NH4)2SO4"], ["C6H12O6"], ["Uuo2(Uuo3)4"], ["(Zn(Mg2(O)3)4)5(Na)1000000"]],
)
_r = rnd(9509)
p["tests"].append([big_formula(_r, 900, 9, 99, 4)])
p["tests"].append([big_formula(_r, 980, 3, 9, 6)])
p["tests"].append(["(" * 300 + "HeOMg" + ")" * 300 + "".join(_r.choice(ELEMS) + str(_r.randint(2, 50)) for _ in range(60))])


def b_atoms(f):
    pat = re.compile(r"\(([^()]*)\)(\d*)")
    while "(" in f:
        f = pat.sub(lambda m: m.group(1) * (int(m.group(2)) if m.group(2) else 1), f, count=1)
    total = {}
    for name, cnt in re.findall(r"([A-Z][a-z]*)(\d*)", f):
        total[name] = total.get(name, 0) + (int(cnt) if cnt else 1)
    return "".join(k + (str(total[k]) if total[k] > 1 else "") for k in sorted(total))


def g_atoms(r):
    return [gen_formula(r, r.randint(0, 3), r.randint(1, 3), 4, 5)]


def v_atoms(tests):
    for t in tests:
        f = t["args"][0]
        assert 1 <= len(f) <= 1000 and re.fullmatch(r"[A-Za-z0-9()]+", f)
        for m in re.finditer(r"\d+", f):
            assert not m.group().startswith("0") and 1 <= int(m.group()) <= 10 ** 6
        assert not re.search(r"\(\)", f) and re.fullmatch(r"(?:\(|\)|[A-Z][a-z]*|\d+)+", f)
        assert re.match(r"[A-Z(]", f)
        d = 0
        for c in f:
            d += (c == "(") - (c == ")")
            assert d >= 0
        assert d == 0
        assert max(count_atoms(f).values()) <= 10 ** 9


CHECKS["count-atoms-in-formula"] = (b_atoms, g_atoms, "exact")
VALIDATE["count-atoms-in-formula"] = v_atoms


def gen_maxstack_ops(r, n, vals, pop_bias=0.3):
    ops, size = [], 0
    for _ in range(n):
        roll = r.random()
        if size == 0 or roll < 0.4:
            ops.append([0, r.randint(-vals, vals)])
            size += 1
        elif roll < 0.4 + pop_bias / 2:
            ops.append([1, 0])
            size -= 1
        elif roll < 0.4 + pop_bias:
            ops.append([4, 0])
            size -= 1
        else:
            ops.append([r.choice([2, 3]), 0])
    return ops


p = add(
    id="max-stack-operations", title="Stack With Pop-Maximum", diff="Hard", topic=TOPIC, tier="extra",
    fn="maxStackOps", params=[("ops", "int[][]")], ret="int[]", cmp="exact",
    desc="<p>Simulate a stack that can also remove its largest value. You are given a list <code>ops</code> of operations; each is a pair <code>[type, x]</code>:</p><ul><li><code>[0, x]</code>: <strong>push</strong> the value <code>x</code> on top. Produces no output.</li><li><code>[1, 0]</code>: <strong>pop</strong> the top element and output it.</li><li><code>[2, 0]</code>: output the top element without removing it.</li><li><code>[3, 0]</code>: output the largest element in the stack without removing it.</li><li><code>[4, 0]</code>: remove the largest element and output it. If several elements share the maximum value, remove the one closest to the top.</li></ul><p>Return the outputs of all operations of types 1 to 4, in order. Operations of types 1 to 4 are only given when the stack is not empty.</p><p>Example: <code>[[0,5],[0,1],[0,5],[3,0],[4,0],[1,0],[2,0]]</code>: the stack is <code>[5,1,5]</code>; the largest is 5 (output 5); removing the maximum removes the top 5 (output 5), leaving <code>[5,1]</code>; pop outputs 1; top outputs 5. The answer is <code>[5, 5, 1, 5]</code>.</p>",
    constraints=["1 &le; ops.length &le; 3,000", "type is in {0, 1, 2, 3, 4}; for types other than 0 the second value is 0", "-2<sup>31</sup> &le; x &le; 2<sup>31</sup> - 1", "Types 1 to 4 are only used on a non-empty stack", "At least one operation produces an output"],
    hints=["A plain list makes every operation except push O(1) at best, but removing the maximum from the middle is O(n). With 3,000 operations that is fine, but can you do better?",
           "You need fast access to both the top and the maximum, and an element removed through one route must disappear from the other.",
           "Give every pushed element a unique id. Keep a stack and a max-heap of (value, id), plus a set of removed ids. When reading either structure, first discard entries whose id is in the removed set (lazy deletion)."],
    editorial=["Two structures describe the same set of elements: a stack ordered by time and a max-heap ordered by (value, push order). Push puts the element in both. Pop removes from the stack and popMax removes from the heap, so each must tell the other. We do that lazily: removed ids go into a set, and before reading the top of either structure we discard entries with removed ids.",
               "Heap entries are <code>(-value, -id)</code> so that the largest value comes first, and among equal values the largest id, i.e. the one pushed latest (closest to the top). Since stack position and push order agree, that is the element nearest the top. Each element is added once and discarded at most once from each structure, so the total is O(n log n) time and O(n) space. A balanced doubly linked list with a sorted map of values gives the same bounds without lazy deletion."],
    time="O(n log n)", space="O(n)",
    solution='''import heapq


def maxStackOps(ops):
    stack = []        # (value, id)
    heap = []         # (-value, -id)
    removed = set()
    out = []
    uid = 0
    for t, x in ops:
        if t == 0:
            uid += 1
            stack.append((x, uid))
            heapq.heappush(heap, (-x, -uid))
            continue
        while stack and stack[-1][1] in removed:
            stack.pop()
        while heap and -heap[0][1] in removed:
            heapq.heappop(heap)
        if t == 1:
            v, i = stack.pop()
            removed.add(i)
            out.append(v)
        elif t == 2:
            out.append(stack[-1][0])
        elif t == 3:
            out.append(-heap[0][0])
        else:
            nv, ni = heapq.heappop(heap)
            removed.add(-ni)
            out.append(-nv)
    return out
''',
    tests=[[[[0, 5], [0, 1], [0, 5], [3, 0], [4, 0], [1, 0], [2, 0]]], [[[0, 7], [2, 0]]], [[[0, -3], [3, 0], [4, 0]]],
           [[[0, 2], [0, 9], [0, 4], [4, 0], [3, 0], [1, 0], [1, 0]]], [[[0, 1], [0, 1], [0, 1], [4, 0], [4, 0], [2, 0], [3, 0]]],
           [[[0, 3], [0, 8], [1, 0], [3, 0], [0, 8], [4, 0], [2, 0]]], [[[0, INT_MAX], [0, INT_MIN], [3, 0], [1, 0], [4, 0], [0, 0], [2, 0]]],
           [[[0, 4], [0, 6], [0, 4], [0, 6], [4, 0], [1, 0], [4, 0], [2, 0]]]],
)
_r = rnd(9510)
p["tests"].append([gen_maxstack_ops(_r, 3000, 10 ** 9)])
p["tests"].append([gen_maxstack_ops(_r, 3000, 5, 0.4)])
p["tests"].append([[[0, _r.randint(-20, 20)] for _ in range(1500)] + [[4, 0], [3, 0]] * 700 + [[1, 0], [2, 0]] * 50])


def b_maxstack(ops):
    lst, out = [], []
    for t, x in ops:
        if t == 0:
            lst.append(x)
        elif t == 1:
            out.append(lst.pop())
        elif t == 2:
            out.append(lst[-1])
        elif t == 3:
            out.append(max(lst))
        else:
            m = max(lst)
            idx = len(lst) - 1 - lst[::-1].index(m)
            del lst[idx]
            out.append(m)
    return out


def g_maxstack(r):
    return [gen_maxstack_ops(r, r.randint(1, 16), r.choice([2, 4, 10]))]


def v_maxstack(tests):
    for t in tests:
        ops = t["args"][0]
        assert 1 <= len(ops) <= 3000
        size = 0
        outs = 0
        for ty, x in ops:
            assert ty in (0, 1, 2, 3, 4)
            if ty == 0:
                assert INT_MIN <= x <= INT_MAX
                size += 1
            else:
                assert x == 0 and size > 0
                outs += 1
                if ty in (1, 4):
                    size -= 1
        assert outs >= 1


CHECKS["max-stack-operations"] = (b_maxstack, g_maxstack, "exact")
VALIDATE["max-stack-operations"] = v_maxstack


def gen_tape_case(r):
    while True:
        s = [r.choice("abcdefg")]
        for _ in range(r.randint(1, 9)):
            s.append(str(r.randint(2, 4)) if r.random() < 0.4 else r.choice("abcdefg"))
        s = "".join(s)
        if len(s) < 2:
            continue
        size = 0
        for ch in s:
            size = size * int(ch) if ch.isdigit() else size + 1
        if size <= 400:
            return s, size


def tape_of(s):
    tape = ""
    for ch in s:
        tape = tape * int(ch) if ch.isdigit() else tape + ch
    return tape


def tape_len(s):
    size = 0
    for ch in s:
        size = size * int(ch) if ch.isdigit() else size + 1
    return size


p = add(
    id="kth-letter-of-repeating-tape", title="K-th Letter of a Repeating Tape", diff="Hard", topic=TOPIC, tier="extra",
    fn="kthDecodedChar", params=[("s", "string"), ("k", "int")], ret="string", cmp="exact",
    desc="<p>A tape is built by reading the string <code>s</code> from left to right, starting with an empty tape:</p><ul><li>a lowercase letter is appended to the end of the tape;</li><li>a digit <code>d</code> (from 2 to 9) makes the tape repeat: the whole tape written so far is replaced by <code>d</code> copies of itself placed one after another.</li></ul><p>The final tape can be astronomically long (it can have more than 10<sup>18</sup> letters or much more), so you cannot build it. Given a 1-indexed position <code>k</code>, return the letter at position <code>k</code> of the final tape, as a one-character string.</p><p>Example: for <code>s = 'leet2code3'</code> the tape is <code>'leet'</code>, then <code>'leetleet'</code>, then <code>'leetleetcode'</code>, then three copies of that (36 letters). Position 10 is <code>'o'</code>.</p>",
    constraints=["2 &le; s.length &le; 1,000", "s consists of lowercase letters and digits 2 to 9, and starts with a letter", "1 &le; k &le; 10<sup>9</sup>, and k is at most the length of the final tape"],
    hints=["Compute the length of the tape after each character. Letters add one, digits multiply. Stop as soon as the length reaches <code>k</code>: later characters cannot change what is at position <code>k</code>.",
           "A digit <code>d</code> turns tape <code>T</code> into <code>T</code> repeated <code>d</code> times, so position <code>k</code> in the new tape holds the same letter as position <code>k mod len(T)</code> in <code>T</code>.",
           "Walk backwards from the stopping point with the current length: for a digit, divide the length by <code>d</code> and set <code>k = k % length</code>; for a letter, if <code>k % length == 0</code> this letter is the answer, otherwise reduce the length by one."],
    editorial=["First find the shortest prefix of <code>s</code> whose tape is at least <code>k</code> letters long. Later characters only append after position <code>k</code> or repeat the tape, and repeating never changes any earlier position, so the answer comes from this prefix. Its length stays below roughly 9 * 10<sup>9</sup>, so there are no overflow worries.",
               "Now undo the prefix from the end with a running length <code>size</code>. Before handling a character, reduce <code>k %= size</code>. If the character is a letter: when <code>k == 0</code> (k pointed at the last letter of the tape) this letter is the answer; otherwise decrease <code>size</code> by one. If the character is a digit: the tape was <code>d</code> copies of the previous tape, so <code>size //= d</code>; the reduction of <code>k</code> already mapped it into the first copy. Each character is processed twice, so the time is O(n) with O(1) extra space. It is a stack-like undo of the character stream."],
    time="O(n)", space="O(1)",
    solution='''def kthDecodedChar(s, k):
    size = 0
    end = 0
    while end < len(s) and size < k:
        ch = s[end]
        if ch.isdigit():
            size *= int(ch)
        else:
            size += 1
        end += 1
    for i in range(end - 1, -1, -1):
        ch = s[i]
        k %= size
        if ch.isdigit():
            size //= int(ch)
        else:
            if k == 0:
                return ch
            size -= 1
    return ""
''',
    tests=[["leet2code3", 10], ["ha22", 5], ["a2345678999999999999999", 1], ["abc", 3], ["abc", 1], ["ab2", 4], ["ab2", 3], ["a2b3", 6],
           ["a2b3", 5], ["xy9", 18], ["xy9", 17], ["z2c2", 6], ["q" + "9" * 900, 1000000000]],
)
_r = rnd(9511)
p["tests"].append(["ab" + "".join(_r.choice("23456789abcdefghijklmnopqrstuvwxyz") for _ in range(950)), 999999937])
p["tests"].append(["".join(_r.choice("abcdefghijklmnopqrstuvwxyz") for _ in range(200)) + "2" + "".join(_r.choice("ab3") for _ in range(100)), 250])
p["tests"].append(["".join(_r.choice("abcdefghijklmnopqrstuvwxyz") for _ in range(1000)), 777])


def b_kthtape(s, k):
    tape = ""
    for ch in s:   # only the first k letters of the tape can matter, so cut the tape there
        tape = (tape * int(ch) if ch.isdigit() else tape + ch)[:k]
    return tape[k - 1]


def g_kthtape(r):
    s, size = gen_tape_case(r)
    return [s, r.randint(1, size)]


def v_kthtape(tests):
    for t in tests:
        s, k = t["args"]
        assert 2 <= len(s) <= 1000 and s[0].isalpha() and s.isascii()
        assert all(c in "23456789" or c.islower() for c in s)
        assert 1 <= k <= 10 ** 9 and k <= tape_len(s)
        assert len(t["expected"]) == 1


CHECKS["kth-letter-of-repeating-tape"] = (b_kthtape, g_kthtape, "exact")
VALIDATE["kth-letter-of-repeating-tape"] = v_kthtape
