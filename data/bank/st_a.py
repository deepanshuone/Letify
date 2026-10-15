"""Problems: Stack, part A (brackets and parentheses). See data/lib.py for the registry."""
import heapq  # noqa: F401
import itertools
import re
from collections import deque

from lib import add, rnd, CHECKS, VALIDATE, gen_arr  # noqa: F401

INT_MIN, INT_MAX = -(2 ** 31), 2 ** 31 - 1
MOD = 10 ** 9 + 7
TOPIC = "Stack"


def _balanced(r, pairs, opens="(", closes=")", bias=0.5):
    """A random well-formed bracket string with `pairs` pairs. A high `bias` gives deeper nesting."""
    out, stack, used = [], [], 0
    for _ in range(2 * pairs):
        remaining = 2 * pairs - len(out)
        can_open = used < pairs
        if stack and (not can_open or remaining == len(stack) or r.random() > bias):
            out.append(closes[stack.pop()])
        else:
            k = r.randrange(len(opens))
            stack.append(k)
            used += 1
            out.append(opens[k])
    return "".join(out)


def _is_balanced(s, pairs=None):
    pairs = pairs or {")": "(", "]": "[", "}": "{"}
    st = []
    for c in s:
        if c in pairs:
            if not st or st.pop() != pairs[c]:
                return False
        elif c in pairs.values():
            st.append(c)
    return not st


# ---------------------------------------------------------------- EASY

p = add(
    id="max-nesting-depth-of-brackets", title="Maximum Nesting Depth of Parentheses", diff="Easy", topic=TOPIC,
    fn="maxNestingDepth", params=[("s", "string")], ret="int", cmp="exact",
    desc="<p>The string <code>s</code> is a piece of arithmetic text made of digits, lowercase letters, the symbols <code>+ - * /</code> and the parentheses <code>(</code> and <code>)</code>. Its parentheses are guaranteed to be well-formed: every <code>'('</code> is closed by a later <code>')'</code> and they never cross.</p><p>The <em>nesting depth</em> of <code>s</code> is the largest number of parentheses pairs that are open at the same moment while reading <code>s</code> from left to right. For example, <code>\"(1+(2*3)+((8)/4))+1\"</code> has depth <code>3</code>, reached inside <code>((8)</code>. A string without parentheses has depth <code>0</code>.</p><p>Return the nesting depth of <code>s</code>.</p>",
    constraints=["1 &le; s.length &le; 10,000", "s contains only digits, lowercase letters, <code>+ - * /</code>, <code>(</code> and <code>)</code>", "The parentheses of s are well-formed"],
    hints=["Whenever you see <code>'('</code> you go one level deeper, and whenever you see <code>')'</code> you come back up one level.",
           "You do not need to store the brackets themselves. A single number, the current depth, tells you everything.",
           "Increase a counter on <code>'('</code>, decrease it on <code>')'</code>, and remember the largest value the counter ever reached. Ignore every other character."],
    editorial=["A stack of open brackets would work, but only its <em>size</em> matters here, so the stack can be replaced by a counter. Scan the string once: on <code>'('</code> increment the counter and update the best value seen so far, on <code>')'</code> decrement it, and skip all other characters.",
               "Because the parentheses are well-formed, the counter never becomes negative and ends at 0. The maximum value of the counter over the scan is exactly the largest number of simultaneously open pairs. Time is O(n) and extra space is O(1)."],
    time="O(n)", space="O(1)",
    solution='''def maxNestingDepth(s):
    depth = best = 0
    for ch in s:
        if ch == '(':
            depth += 1
            if depth > best:
                best = depth
        elif ch == ')':
            depth -= 1
    return best
''',
    tests=[["(1+(2*3)+((8)/4))+1"], ["(1)+((2))+(((3)))"], ["x"], ["1+2*3"], ["()"], ["(a)(b)(c)"],
           ["a+(b*(c-(d/(e+(f*g)))))"], ["((a+b)*(c-d))/((e))"], ["(((((((((())))))))))"], ["12(3)45(6)7"]],
)
_r = rnd(7101)
p["tests"].append(["(" * 5000 + ")" * 5000])
p["tests"].append(["(a)" * 3333 + "1"])
_s = _balanced(_r, 2500, bias=0.6)
p["tests"].append(["".join(c + ("" if _r.random() < 0.6 else _r.choice("0123456789abc+-*/")) for c in _s)])


def b_depth(s):
    # peel off all innermost pairs round by round; the number of rounds is the depth
    rounds = 0
    while "(" in s:
        s = re.sub(r"\([^()]*\)", "", s)
        rounds += 1
    return rounds


def g_depth(r):
    s = _balanced(r, r.randint(0, 6), bias=r.choice([0.4, 0.5, 0.7]))
    s = "".join(c + (r.choice("012ab+-*/") if r.random() < 0.4 else "") for c in s)
    return [s or "7"]


def v_depth(tests):
    for t in tests:
        s = t["args"][0]
        assert 1 <= len(s) <= 10000 and re.fullmatch(r"[0-9a-z+\-*/()]+", s)
        assert _is_balanced(s)


CHECKS["max-nesting-depth-of-brackets"] = (b_depth, g_depth, "exact")
VALIDATE["max-nesting-depth-of-brackets"] = v_depth


p = add(
    id="strip-outermost-parentheses", title="Strip the Outermost Parentheses", diff="Easy", topic=TOPIC,
    fn="stripOutermost", params=[("s", "string")], ret="string", cmp="exact",
    desc="<p>A well-formed parentheses string is <em>primitive</em> if it is non-empty and cannot be split into two non-empty well-formed strings. Every well-formed string <code>s</code> splits in exactly one way into a sequence of primitive strings placed side by side. For example <code>\"(()())(())\"</code> splits into <code>\"(()())\"</code> and <code>\"(())\"</code>.</p><p>Remove the outermost pair of parentheses from every primitive piece and glue the remains together in the original order. For the example above you get <code>\"()()\"</code> and <code>\"()\"</code>, so the answer is <code>\"()()()\"</code>.</p><p>Return the resulting string, which is empty if every piece was just <code>\"()\"</code>.</p>",
    constraints=["2 &le; s.length &le; 10,000", "s contains only <code>(</code> and <code>)</code>", "s is well-formed"],
    hints=["The outermost parentheses are exactly the ones that sit at the top level, where nothing else is open yet.",
           "Track the current depth. A <code>'('</code> read at depth 0 starts a primitive piece, and a <code>')'</code> that brings the depth back to 0 ends it.",
           "Keep a character only if it is not one of those two: add <code>'('</code> when the depth before it is at least 1, and add <code>')'</code> when the depth after it is at least 1."],
    editorial=["The outermost pair of a primitive piece is the opening bracket where the depth goes from 0 to 1 and the closing bracket where it goes back from 1 to 0. Everything strictly between them is kept. So one pass with a depth counter is enough, without any explicit stack.",
               "For each character: if it is <code>'('</code>, keep it when the depth is already above 0, then increase the depth. If it is <code>')'</code>, decrease the depth first and keep it when the depth is still above 0. Time is O(n) and the output takes O(n) space."],
    time="O(n)", space="O(n)",
    solution='''def stripOutermost(s):
    out = []
    depth = 0
    for ch in s:
        if ch == '(':
            if depth > 0:
                out.append(ch)
            depth += 1
        else:
            depth -= 1
            if depth > 0:
                out.append(ch)
    return "".join(out)
''',
    tests=[["(()())(())"], ["(()())(())(()(()))"], ["()()"], ["()"], ["(())"], ["((()))"], ["()(())()"],
           ["(()(()))"], ["(((())))()"], ["()()()()()"]],
)
_r = rnd(7102)
p["tests"].append(["(" * 5000 + ")" * 5000])
p["tests"].append([_balanced(_r, 5000, bias=0.5)])
p["tests"].append([_balanced(_r, 20, bias=0.5) * 100 + "()" * 2000])


def b_strip(s):
    # match every bracket with a stack, then drop the pairs that are not enclosed by any other pair
    n = len(s)
    st, pairs = [], []
    for i, c in enumerate(s):
        if c == "(":
            st.append(i)
        else:
            pairs.append((st.pop(), i))
    drop = set()
    for (i, j) in pairs:
        if not any(k < i and j < l for (k, l) in pairs):
            drop.add(i)
            drop.add(j)
    return "".join(s[i] for i in range(n) if i not in drop)


def g_strip(r):
    return [_balanced(r, r.randint(1, 7), bias=r.choice([0.4, 0.5, 0.7]))]


def v_strip(tests):
    for t in tests:
        s = t["args"][0]
        assert 2 <= len(s) <= 10000 and set(s) <= set("()") and _is_balanced(s)


CHECKS["strip-outermost-parentheses"] = (b_strip, g_strip, "exact")
VALIDATE["strip-outermost-parentheses"] = v_strip


p = add(
    id="matching-bracket-positions", title="Matching Bracket Positions", diff="Easy", topic=TOPIC,
    fn="matchingPositions", params=[("s", "string")], ret="int[]", cmp="exact",
    desc="<p>The string <code>s</code> is a well-formed sequence made of the six characters <code>( ) [ ] { }</code>: every opening bracket is closed by a later bracket of the same type, and pairs never cross each other.</p><p>Return an array <code>answer</code> of the same length as <code>s</code> where <code>answer[i]</code> is the (0-based) index of the bracket that is paired with the bracket at index <code>i</code>. For an opening bracket this is the index of its closing partner, and for a closing bracket the index of its opening partner.</p><p>For example, <code>\"([]){}\"</code> gives <code>[3, 2, 1, 0, 5, 4]</code>.</p>",
    constraints=["2 &le; s.length &le; 5,000", "s contains only <code>( ) [ ] { }</code> and is well-formed"],
    hints=["The closing bracket at some index pairs with the most recent opening bracket that has not been closed yet.",
           "That is last-in, first-out. Keep a stack of indices of opening brackets that still wait for their partner.",
           "On an opening bracket push its index. On a closing bracket pop the top index <code>j</code>, then set <code>answer[i] = j</code> and <code>answer[j] = i</code>."],
    editorial=["Because the string is well-formed, the partner of a closing bracket is always the most recently opened bracket that is still unmatched, and that is precisely the top of a stack of indices. So push indices of opening brackets and, at every closing bracket, pop the top and record the pair in both directions.",
               "Every index is pushed and popped at most once, so the time is O(n). The stack and the answer take O(n) space. The types of the brackets never need to be checked, because the input is guaranteed to be well-formed."],
    time="O(n)", space="O(n)",
    solution='''def matchingPositions(s):
    answer = [0] * len(s)
    stack = []
    for i, ch in enumerate(s):
        if ch in '([{':
            stack.append(i)
        else:
            j = stack.pop()
            answer[i] = j
            answer[j] = i
    return answer
''',
    tests=[["([]){}"], ["()"], ["{[()]}"], ["(){}[]"], ["((()))"], ["[({})]()"], ["{}{}{}"], ["([{}])([{}])"],
           ["(((())))[[]]{}"], ["{[](){[]}}"]],
)
_r = rnd(7103)
p["tests"].append([_balanced(_r, 2500, "([{", ")]}", bias=0.5)])
p["tests"].append([_balanced(_r, 2500, "([{", ")]}", bias=0.8)])
p["tests"].append(["([{" * 800 + "}])" * 800 + "()" * 100])


def b_match(s):
    # scan to the right with a depth counter over all bracket characters
    n = len(s)
    ans = [0] * n
    for i, c in enumerate(s):
        if c in "([{":
            d = 0
            for j in range(i, n):
                d += 1 if s[j] in "([{" else -1
                if d == 0:
                    ans[i] = j
                    ans[j] = i
                    break
    return ans


def g_match(r):
    return [_balanced(r, r.randint(1, 7), "([{", ")]}", bias=r.choice([0.4, 0.5, 0.7]))]


def v_match(tests):
    for t in tests:
        s = t["args"][0]
        assert 2 <= len(s) <= 5000 and set(s) <= set("()[]{}") and _is_balanced(s)


CHECKS["matching-bracket-positions"] = (b_match, g_match, "exact")
VALIDATE["matching-bracket-positions"] = v_match


# ---------------------------------------------------------------- MEDIUM

p = add(
    id="min-brace-flips-to-balance", title="Minimum Brace Flips to Balance", diff="Medium", topic=TOPIC,
    fn="minFlipsToBalance", params=[("s", "string")], ret="int", cmp="exact",
    desc="<p>The string <code>s</code> consists only of the characters <code>'{'</code> and <code>'}'</code>. It is <em>balanced</em> when every <code>'{'</code> can be paired with a later <code>'}'</code> and every <code>'}'</code> with an earlier <code>'{'</code>, each brace used in exactly one pair.</p><p>In one operation you pick a single position and flip its character, turning <code>'{'</code> into <code>'}'</code> or <code>'}'</code> into <code>'{'</code>. You cannot insert or delete characters.</p><p>Return the minimum number of flips that make <code>s</code> balanced, or <code>-1</code> if it is impossible.</p><p>For example, <code>\"}{\"</code> needs 2 flips (it becomes <code>\"{}\"</code>), while <code>\"{{{\"</code> is impossible because its length is odd.</p>",
    constraints=["1 &le; s.length &le; 10,000", "s contains only <code>{</code> and <code>}</code>"],
    hints=["Flipping never changes the length, so what can you say immediately when the length is odd?",
           "First cancel every adjacent <code>{}</code> pair with a stack (or counter), as these braces are already fine. What shape can the leftover string have?",
           "The leftover is always some closing braces followed by some opening braces: <code>}}}...{{{</code>. With <code>a</code> closing and <code>b</code> opening braces left, flip every second closing brace and every second opening brace, which costs <code>ceil(a/2) + ceil(b/2)</code>."],
    editorial=["An odd length can never be balanced, so answer -1. Otherwise scan the string with a counter of open braces. On <code>'{'</code> increase it. On <code>'}'</code>, if the counter is positive decrease it (a matched pair), else this <code>'}'</code> is unmatched and we count it in <code>a</code>. At the end, the counter holds the unmatched opening braces <code>b</code>.",
               "What remains is <code>}^a {^b</code>. Two adjacent unmatched braces of the same kind can be fixed with one flip: <code>}}</code> becomes <code>{}</code> and <code>{{</code> becomes <code>{}</code>. If <code>a</code> is odd then <code>b</code> is odd too (the total length is even), and the last <code>}</code> and the first <code>{</code> need one flip each to become <code>{</code> and <code>}</code>. Hence the minimum is <code>ceil(a/2) + ceil(b/2)</code>. Time O(n), space O(1)."],
    time="O(n)", space="O(1)",
    solution='''def minFlipsToBalance(s):
    if len(s) % 2:
        return -1
    open_count = 0   # unmatched '{'
    stray_close = 0  # '}' with no '{' before it
    for ch in s:
        if ch == '{':
            open_count += 1
        elif open_count > 0:
            open_count -= 1
        else:
            stray_close += 1
    return (stray_close + 1) // 2 + (open_count + 1) // 2
''',
    tests=[["}{"], ["{{{{"], ["{{{"], ["}}}}{{"], ["{}"], ["{}{}"], ["}}"], ["{{}}}}{{"], ["}{}{"], ["{"], ["}{}}{{"]],
)
_r = rnd(7104)
p["tests"].append(["}" * 5000 + "{" * 5000])
p["tests"].append(["".join(_r.choice("{}") for _ in range(10000))])
p["tests"].append(["".join(_r.choice("{}") for _ in range(9999))])
p["tests"].append(["{" * 4999 + "}" * 5001])


def b_flips(s):
    n = len(s)
    best = -1
    for mask in range(1 << n):
        bal, ok = 0, True
        for i in range(n):
            c = s[i]
            if (mask >> i) & 1:
                c = "}" if c == "{" else "{"
            bal += 1 if c == "{" else -1
            if bal < 0:
                ok = False
                break
        if ok and bal == 0:
            k = bin(mask).count("1")
            if best == -1 or k < best:
                best = k
    return best


def g_flips(r):
    return ["".join(r.choice("{}") for _ in range(r.randint(1, 12)))]


def v_flips(tests):
    for t in tests:
        s = t["args"][0]
        assert 1 <= len(s) <= 10000 and set(s) <= set("{}")
        assert (t["expected"] == -1) == (len(s) % 2 == 1)


CHECKS["min-brace-flips-to-balance"] = (b_flips, g_flips, "exact")
VALIDATE["min-brace-flips-to-balance"] = v_flips


p = add(
    id="score-of-parentheses", title="Score of Nested Parentheses", diff="Medium", topic=TOPIC,
    fn="scoreOfParentheses", params=[("s", "string")], ret="int", cmp="exact",
    desc="<p>A well-formed parentheses string <code>s</code> is given a score by these rules:</p><ul><li><code>\"()\"</code> has score <code>1</code>.</li><li>If <code>A</code> and <code>B</code> are well-formed strings, the concatenation <code>AB</code> has score <code>score(A) + score(B)</code>.</li><li>If <code>A</code> is a well-formed string, <code>(A)</code> has score <code>2 * score(A)</code>.</li></ul><p>For example <code>\"(()(()))\"</code> is <code>(A)</code> with <code>A = \"()(())\"</code>, and <code>score(A) = 1 + 2 = 3</code>, so the total score is <code>6</code>.</p><p>Deep nesting makes scores huge, so return the score of <code>s</code> modulo <code>1,000,000,007</code>.</p>",
    constraints=["2 &le; s.length &le; 5,000 and s.length is even", "s contains only <code>(</code> and <code>)</code> and is well-formed"],
    hints=["The rules describe a recursion. Which part of the string does each recursive call work on?",
           "Process the string left to right and keep, for every currently open bracket, the total score of what has been completed inside it so far.",
           "On <code>'('</code> push 0. On <code>')'</code> pop the inner total <code>v</code> and add <code>max(2 * v, 1)</code> to the new top of the stack: an empty pair <code>()</code> is worth 1, otherwise the inside is doubled."],
    editorial=["Keep a stack of running totals, starting with a single 0 for the top level. Opening a bracket starts a fresh total for its inside by pushing 0. Closing a bracket pops the inside total <code>v</code>; the finished pair contributes <code>1</code> if its inside was empty (<code>v = 0</code>) and <code>2v</code> otherwise, i.e. <code>max(2v, 1)</code>. That contribution is added to the total of the enclosing level, which realises the rule <code>AB = A + B</code>.",
               "After the scan the single remaining value is the answer. Take everything modulo 10<sup>9</sup>+7: the true score can be as large as 2<sup>2499</sup>. Since <code>v</code> is reduced modulo p, <code>max(2v, 1)</code> must only treat the genuinely empty inside specially; the inside of a non-empty pair has a true score of at least 1, but its residue can be 0, so track emptiness by whether the bracket was immediately closed, not by the value. Time is O(n), space O(n). A neat O(1)-space alternative adds <code>2^depth</code> for every <code>\"()\"</code> found."],
    time="O(n)", space="O(n)",
    solution='''def scoreOfParentheses(s):
    MOD = 10**9 + 7
    # every stack entry is [total so far inside this bracket, is it still empty]
    total = 0
    stack = []
    cur = 0
    for i, ch in enumerate(s):
        if ch == '(':
            stack.append(cur)
            cur = 0
        else:
            inner = cur
            cur = stack.pop()
            if s[i - 1] == '(':
                cur = (cur + 1) % MOD
            else:
                cur = (cur + 2 * inner) % MOD
    return cur % MOD
''',
    tests=[["()"], ["(())"], ["()()"], ["(()(()))"], ["((()))"], ["()(())"], ["(()())"], ["((()())())"], ["(((())))()"],
           ["()()()()"], ["((((()))))"]],
)
_r = rnd(7105)
p["tests"].append(["(" * 2500 + ")" * 2500])
p["tests"].append([_balanced(_r, 2500, bias=0.55)])
p["tests"].append([_balanced(_r, 2500, bias=0.75)])
p["tests"].append(["(" * 30 + ")" * 30 + "()" * 1220])


def b_score(s):
    # exact recursive definition with Python big integers
    def go(t):
        total = 0
        i = 0
        while i < len(t):
            d = 0
            j = i
            while True:
                d += 1 if t[j] == "(" else -1
                if d == 0:
                    break
                j += 1
            inner = t[i + 1:j]
            total += 1 if not inner else 2 * go(inner)
            i = j + 1
        return total
    return go(s) % MOD


def g_score(r):
    return [_balanced(r, r.randint(1, 9), bias=r.choice([0.4, 0.5, 0.7, 0.9]))]


def v_score(tests):
    for t in tests:
        s = t["args"][0]
        assert 2 <= len(s) <= 5000 and len(s) % 2 == 0 and set(s) <= set("()") and _is_balanced(s)
        assert 0 <= t["expected"] < MOD


CHECKS["score-of-parentheses"] = (b_score, g_score, "exact")
VALIDATE["score-of-parentheses"] = v_score


p = add(
    id="min-swaps-to-balance-square-brackets", title="Minimum Swaps to Balance Square Brackets", diff="Medium", topic=TOPIC,
    fn="minSwapsToBalance", params=[("s", "string")], ret="int", cmp="exact",
    desc="<p>The string <code>s</code> has even length <code>n</code> and consists of exactly <code>n / 2</code> characters <code>'['</code> and <code>n / 2</code> characters <code>']'</code>.</p><p>It is <em>balanced</em> when every <code>'['</code> can be paired with a later <code>']'</code> and every <code>']'</code> with an earlier <code>'['</code>, each bracket used once.</p><p>In one move you may choose <em>any</em> two indices (not necessarily adjacent) and swap the characters there. Return the minimum number of moves needed to make <code>s</code> balanced.</p><p>For example, <code>\"][][\"</code> needs one move: swap the first and last characters to get <code>\"[][]\"</code>.</p>",
    constraints=["2 &le; s.length &le; 10,000 and s.length is even", "s contains only <code>[</code> and <code>]</code>", "The number of <code>[</code> equals the number of <code>]</code>"],
    hints=["Which brackets are already fine and can be ignored? Cancel every <code>[</code> with a later <code>]</code>.",
           "What is left after cancelling is a block of <code>]</code> followed by a block of <code>[</code>, and both blocks have the same size <code>k</code> because the totals are equal.",
           "One swap can repair two stray closing brackets at once: swap an early stray <code>]</code> with a late stray <code>[</code>. So the answer is <code>ceil(k / 2)</code>."],
    editorial=["Scan left to right with a counter of open brackets and count the number of <code>']'</code> that arrive while the counter is 0; call it <code>k</code>. These are the unmatched closing brackets. Because the string has equally many brackets of both kinds, exactly <code>k</code> unmatched opening brackets remain at the end, so the leftover is <code>]^k [^k</code>.",
               "A swap of a stray <code>]</code> at the front with a stray <code>[</code> at the back turns them into a matched pair around everything in the middle, and repairs one stray of each kind per swap. The two innermost strays <code>]</code>, <code>[</code> in the middle can be fixed in a single swap too, each swap fixing up to two strays on the closing side. Following that scheme the minimum is <code>(k + 1) // 2</code>. Time O(n), space O(1)."],
    time="O(n)", space="O(1)",
    solution='''def minSwapsToBalance(s):
    open_count = 0
    stray_close = 0
    for ch in s:
        if ch == '[':
            open_count += 1
        elif open_count > 0:
            open_count -= 1
        else:
            stray_close += 1
    return (stray_close + 1) // 2
''',
    tests=[["]["], ["][]["], ["]]][[["], ["[]"], ["[[]]"], ["]]]][[[["], ["][][]["], ["[]][]["], ["]][]][[[]["], ["[][][]"]],
)
_r = rnd(7106)
p["tests"].append(["]" * 5000 + "[" * 5000])
_x = list("[" * 5000 + "]" * 5000)
_r.shuffle(_x)
p["tests"].append(["".join(_x)])
p["tests"].append(["][" * 5000])
p["tests"].append(["[" * 2500 + "]" * 5000 + "[" * 2500])


def b_swaps(s):
    def ok(t):
        b = 0
        for c in t:
            b += 1 if c == "[" else -1
            if b < 0:
                return False
        return b == 0
    if ok(s):
        return 0
    seen = {s}
    dq = deque([(s, 0)])
    while dq:
        t, d = dq.popleft()
        for i in range(len(t)):
            for j in range(i + 1, len(t)):
                if t[i] != t[j]:
                    u = list(t)
                    u[i], u[j] = u[j], u[i]
                    u = "".join(u)
                    if u not in seen:
                        if ok(u):
                            return d + 1
                        seen.add(u)
                        dq.append((u, d + 1))
    return -1


def g_swaps(r):
    k = r.randint(1, 5)
    a = list("[" * k + "]" * k)
    r.shuffle(a)
    return ["".join(a)]


def v_swaps(tests):
    for t in tests:
        s = t["args"][0]
        assert 2 <= len(s) <= 10000 and len(s) % 2 == 0 and set(s) <= set("[]")
        assert s.count("[") == s.count("]")


CHECKS["min-swaps-to-balance-square-brackets"] = (b_swaps, g_swaps, "exact")
VALIDATE["min-swaps-to-balance-square-brackets"] = v_swaps


p = add(
    id="valid-parenthesis-string-with-stars", title="Valid Parenthesis String with Stars", diff="Medium", topic=TOPIC,
    fn="checkValidString", params=[("s", "string")], ret="bool", cmp="exact",
    desc="<p>The string <code>s</code> contains only the characters <code>'('</code>, <code>')'</code> and <code>'*'</code>. Each <code>'*'</code> is a joker that you may independently treat as <code>'('</code>, as <code>')'</code>, or as an empty string (nothing at all).</p><p>Return <code>true</code> if the jokers can be resolved so that the resulting string is well-formed: every <code>'('</code> is closed by a later <code>')'</code>, every <code>')'</code> closes an earlier <code>'('</code>, and nothing is left open.</p><p>For example <code>\"(*)\"</code> and <code>\"(*))\"</code> are valid, while <code>\")*(\"</code> is not.</p>",
    constraints=["1 &le; s.length &le; 5,000", "s contains only <code>(</code>, <code>)</code> and <code>*</code>"],
    hints=["Trying all 3<sup>k</sup> ways to resolve k stars is far too slow. Instead of one running balance, think about the <em>set</em> of balances that are still possible after each character.",
           "That set is always an interval of consecutive integers (clipped at 0). You only need its smallest and largest possible balance.",
           "Keep <code>lo</code> and <code>hi</code>. For <code>'('</code> add 1 to both, for <code>')'</code> subtract 1 from both, for <code>'*'</code> do <code>lo -= 1</code>, <code>hi += 1</code>. If <code>hi &lt; 0</code> return false; clamp <code>lo</code> at 0. At the end the string is valid exactly when <code>lo == 0</code>."],
    editorial=["Let <code>lo</code> be the smallest and <code>hi</code> the largest number of unclosed brackets you could have after reading a prefix, over all ways to resolve its stars (never letting the balance drop below 0 on the way). A <code>'('</code> raises both, a <code>')'</code> lowers both, and a <code>'*'</code> can lower the minimum by one (as <code>')'</code>) and raise the maximum by one (as <code>'('</code>); it can also do nothing, which keeps every value in between reachable.",
               "If <code>hi</code> becomes negative, even the most generous reading has a stray <code>')'</code>, so the answer is false. A negative <code>lo</code> is simply clamped to 0, because a reading that would go below 0 is not allowed and the in-between values stay reachable. At the end, the string can be balanced if 0 is inside the interval, which, after clamping, means <code>lo == 0</code>. This is O(n) time and O(1) space. A two-stack solution (indices of unmatched <code>(</code> and of <code>*</code>, matched greedily at the end) reaches the same answer."],
    time="O(n)", space="O(1)",
    solution='''def checkValidString(s):
    lo = hi = 0   # smallest / largest possible number of open brackets
    for ch in s:
        if ch == '(':
            lo += 1
            hi += 1
        elif ch == ')':
            lo -= 1
            hi -= 1
        else:
            lo -= 1
            hi += 1
        if hi < 0:
            return False
        if lo < 0:
            lo = 0
    return lo == 0
''',
    tests=[["(*)"], ["(*))"], [")*("], ["*"], ["("], [")"], ["()"], ["(*"], ["*)"], ["**"], ["(*()"], ["(((*)"], ["((*)"],
           ["*(*)(*"], ["(()*)(*"]],
)
_r = rnd(7107)
p["tests"].append(["(" * 1500 + "*" * 2000 + ")" * 1500])
p["tests"].append(["*" * 2000 + "(" * 1000 + ")" * 1999])
p["tests"].append(["".join(_r.choices("()*", weights=[4, 4, 3])[0] for _ in range(5000))])
_t = list(_balanced(_r, 2400, bias=0.55))
for _i in _r.sample(range(len(_t)), 600):
    _t[_i] = "*"
p["tests"][-1:] = [p["tests"][-1], ["".join(_t)]]


def b_stars(s):
    stars = [i for i, c in enumerate(s) if c == "*"]
    for choice in itertools.product("()_", repeat=len(stars)):
        t = list(s)
        for i, c in zip(stars, choice):
            t[i] = c
        bal, ok = 0, True
        for c in t:
            if c == "(":
                bal += 1
            elif c == ")":
                bal -= 1
                if bal < 0:
                    ok = False
                    break
        if ok and bal == 0:
            return True
    return False


def g_stars(r):
    return ["".join(r.choice("()*") for _ in range(r.randint(1, 9)))]


def v_stars(tests):
    for t in tests:
        s = t["args"][0]
        assert 1 <= len(s) <= 5000 and set(s) <= set("()*")
    assert {t["expected"] for t in tests} == {True, False}


CHECKS["valid-parenthesis-string-with-stars"] = (b_stars, g_stars, "exact")
VALIDATE["valid-parenthesis-string-with-stars"] = v_stars


p = add(
    id="count-valid-parentheses-substrings", title="Count Valid Parentheses Substrings", diff="Medium", topic=TOPIC,
    fn="countValidSubstrings", params=[("s", "string")], ret="int", cmp="exact",
    desc="<p>The string <code>s</code> contains only <code>'('</code> and <code>')'</code>. A string is <em>valid</em> when it is non-empty and well-formed: every <code>'('</code> is closed by a later <code>')'</code> and every <code>')'</code> closes an earlier <code>'('</code>.</p><p>Count the substrings of <code>s</code> that are valid. Substrings are contiguous and are counted by their position, so two equal substrings at different places count separately.</p><p>For example, <code>\"(()())\"</code> has 4 valid substrings: <code>\"()\"</code> twice (at indices 1-2 and 3-4), <code>\"()()\"</code> and the whole string.</p>",
    constraints=["1 &le; s.length &le; 10,000", "s contains only <code>(</code> and <code>)</code>"],
    hints=["Checking all O(n<sup>2</sup>) substrings with a counter is correct but slow for n = 10,000 in some languages. Try counting valid substrings by their <em>last</em> character.",
           "A valid substring can only end at a <code>')'</code>. If that <code>')'</code> is matched by a stack to an opening bracket at index <code>j</code>, then <code>s[j..i]</code> is valid.",
           "Let <code>dp[i]</code> be the number of valid substrings ending at <code>i</code>. If <code>s[i]</code> matches index <code>j</code>, then <code>dp[i] = 1 + dp[j-1]</code> (with <code>dp[-1] = 0</code>): the pair itself, or the pair preceded by any valid substring that ends right before <code>j</code>. Otherwise <code>dp[i] = 0</code>. The answer is the sum of <code>dp</code>."],
    editorial=["Match brackets with a stack of indices. When a <code>')'</code> at index <code>i</code> finds an opening bracket at <code>j</code> on the stack, the segment <code>s[j..i]</code> is well-formed. Every valid substring ending at <code>i</code> has this segment as its last primitive piece, preceded by a (possibly empty) valid substring that ends at <code>j - 1</code>. There are <code>dp[j-1]</code> non-empty choices for that prefix plus the empty one, so <code>dp[i] = dp[j-1] + 1</code>.",
               "A <code>')'</code> with an empty stack can never be part of a valid substring, and neither can any substring crossing it, which is handled automatically: nothing matches across it, so <code>dp</code> stays 0 there and the stack is empty as well. Adding all <code>dp[i]</code> gives the answer in O(n) time and O(n) space. The result is at most about n<sup>2</sup>/8, which fits easily in 32 bits."],
    time="O(n)", space="O(n)",
    solution='''def countValidSubstrings(s):
    n = len(s)
    dp = [0] * n          # valid substrings ending at i
    stack = []            # indices of '(' that are still unmatched
    total = 0
    for i, ch in enumerate(s):
        if ch == '(':
            stack.append(i)
        elif stack:
            j = stack.pop()
            dp[i] = 1 + (dp[j - 1] if j > 0 else 0)
            total += dp[i]
    return total
''',
    tests=[["(()())"], ["()()"], ["()"], ["("], [")("], ["(((())))"], ["())()"], ["()(()"], ["(()))(()())"], ["))(("],
           ["()()()()()"]],
)
_r = rnd(7108)
p["tests"].append(["()" * 5000])
p["tests"].append(["".join(_r.choice("()") for _ in range(10000))])
p["tests"].append(["".join(_r.choices("()", weights=[1, 1])[0] for _ in range(10000))[:5000] + _balanced(_r, 2500, bias=0.5)])
p["tests"].append(["(" * 5000 + ")" * 5000])


def b_cnt(s):
    n = len(s)
    c = 0
    for i in range(n):
        bal = 0
        for j in range(i, n):
            bal += 1 if s[j] == "(" else -1
            if bal < 0:
                break
            if bal == 0:
                c += 1
    return c


def g_cnt(r):
    return ["".join(r.choice("()") for _ in range(r.randint(1, 14)))]


def v_cnt(tests):
    for t in tests:
        s = t["args"][0]
        assert 1 <= len(s) <= 10000 and set(s) <= set("()")


CHECKS["count-valid-parentheses-substrings"] = (b_cnt, g_cnt, "exact")
VALIDATE["count-valid-parentheses-substrings"] = v_cnt


p = add(
    id="count-bracket-fillings-for-question-marks", title="Count Ways to Fill the Question Marks", diff="Medium", topic=TOPIC,
    fn="countFillings", params=[("s", "string")], ret="int", cmp="exact",
    desc="<p>The string <code>s</code> consists of the characters <code>'('</code>, <code>')'</code> and <code>'?'</code>. You must replace every <code>'?'</code> by either <code>'('</code> or <code>')'</code>. A resulting string is <em>well-formed</em> when every <code>'('</code> is closed by a later <code>')'</code>, every <code>')'</code> closes an earlier <code>'('</code>, and nothing stays open.</p><p>Return the number of different ways to replace the question marks so that the result is well-formed, modulo <code>1,000,000,007</code>. Two ways are different if some <code>'?'</code> receives a different character.</p><p>For example, <code>\"(??)\"</code> has 2 ways (<code>\"(())\"</code> and <code>\"()()\"</code>), and <code>\"????\"</code> also has 2.</p>",
    constraints=["1 &le; s.length &le; 1,000", "s contains only <code>(</code>, <code>)</code> and <code>?</code>"],
    hints=["A string is well-formed exactly when its running balance never goes below 0 and ends at 0. So the only thing that matters after a prefix is the current balance.",
           "Let <code>ways[b]</code> be the number of ways to fill the prefix read so far so that the balance is <code>b</code> and was never negative. Update it for one new character at a time.",
           "For <code>'('</code>, every balance moves up by one; for <code>')'</code> it moves down by one (balance 0 dies); for <code>'?'</code> both happen and the counts add up. The answer is <code>ways[0]</code> after the last character."],
    editorial=["This is a counting DP over (position, balance). Let <code>dp[b]</code> be the number of valid prefix fillings that end with balance <code>b</code>. Starting with <code>dp = [1]</code> (balance 0), read the characters one by one and build a new array: a <code>'('</code> contributes <code>new[b+1] += dp[b]</code>, a <code>')'</code> contributes <code>new[b-1] += dp[b]</code> for <code>b &ge; 1</code>, and <code>'?'</code> does both. Everything is taken modulo 10<sup>9</sup>+7.",
               "The balance never exceeds <code>n/2</code> in a useful state, since it must still come back to 0, and an odd length has no valid filling at all. With n states per step the DP runs in O(n<sup>2</sup>) time and O(n) space, which is fine for n &le; 1,000. As a sanity check, a string of only <code>'?'</code> of length <code>2m</code> gives the Catalan number C<sub>m</sub>."],
    time="O(n^2)", space="O(n)",
    solution='''def countFillings(s):
    MOD = 10**9 + 7
    n = len(s)
    if n % 2:
        return 0
    half = n // 2
    dp = [0] * (half + 2)     # dp[b] = ways with balance b
    dp[0] = 1
    for i, ch in enumerate(s):
        new = [0] * (half + 2)
        top = min(i, half)
        for b in range(top + 1):
            v = dp[b]
            if not v:
                continue
            if ch != ')' and b + 1 <= half:
                new[b + 1] = (new[b + 1] + v) % MOD
            if ch != '(' and b > 0:
                new[b - 1] = (new[b - 1] + v) % MOD
        dp = new
    return dp[0]
''',
    tests=[["(??)"], ["????"], ["??"], ["()"], [")("], ["?"], ["(?"], ["(((?"], ["???)"], ["(?(?)?)?"], ["??????"], ["?()?"],
           ["))??"], ["(" + "?" * 10 + ")"]],
)
_r = rnd(7109)
p["tests"].append(["?" * 1000])
p["tests"].append(["".join(_r.choices("()?", weights=[1, 1, 8])[0] for _ in range(1000))])
p["tests"].append(["(" + "?" * 998 + ")"])


def b_fill(s):
    qs = [i for i, c in enumerate(s) if c == "?"]
    total = 0
    for choice in itertools.product("()", repeat=len(qs)):
        t = list(s)
        for i, c in zip(qs, choice):
            t[i] = c
        bal, ok = 0, True
        for c in t:
            bal += 1 if c == "(" else -1
            if bal < 0:
                ok = False
                break
        if ok and bal == 0:
            total += 1
    return total % MOD


def g_fill(r):
    n = r.randint(1, 12)
    w = r.choice([[1, 1, 1], [1, 1, 4], [2, 1, 3]])
    return ["".join(r.choices("()?", weights=w)[0] for _ in range(n))]


def v_fill(tests):
    for t in tests:
        s = t["args"][0]
        assert 1 <= len(s) <= 1000 and set(s) <= set("()?")
        assert 0 <= t["expected"] < MOD
    assert any(t["expected"] > 0 for t in tests) and any(t["expected"] == 0 for t in tests)


CHECKS["count-bracket-fillings-for-question-marks"] = (b_fill, g_fill, "exact")
VALIDATE["count-bracket-fillings-for-question-marks"] = v_fill


# ---------------------------------------------------------------- HARD

p = add(
    id="count-minimal-bracket-repairs", title="Count Minimal Bracket Repairs", diff="Hard", topic=TOPIC, tier="extra",
    fn="countMinimalRepairs", params=[("s", "string")], ret="int", cmp="exact",
    desc="<p>The string <code>s</code> contains lowercase letters and the parentheses <code>'('</code> and <code>')'</code>. You want to make its parentheses well-formed by deleting as few <em>parentheses</em> as possible. Letters must never be deleted, and the relative order of the remaining characters stays the same.</p><p>Among all ways to do this with the minimum number of deletions, different choices of positions may produce the same string. Return the number of <em>distinct resulting strings</em>.</p><p>For example, <code>\"()())()\"</code> needs 1 deletion and can become <code>\"()()()\"</code> or <code>\"(())()\"</code>, so the answer is <code>2</code>. The string <code>\")(\"</code> becomes the empty string only, so the answer is <code>1</code>.</p>",
    constraints=["1 &le; s.length &le; 25", "s contains lowercase letters, <code>(</code> and <code>)</code>", "s contains at most 20 parentheses"],
    hints=["First find out how many <code>')'</code> and how many <code>'('</code> have to be deleted at least. A single left-to-right scan with a counter gives both numbers.",
           "Now search: at every parenthesis you may keep it or delete it, as long as you do not delete more than you are allowed to, and you prune as soon as the running balance goes negative.",
           "To avoid counting equal strings many times, when you delete a parenthesis from a run of identical consecutive parentheses, always delete the first one in the run that you still have a choice about. Collect the finished strings in a set to be safe and return its size."],
    editorial=["A scan with a balance counter finds the minimum deletions: every <code>')'</code> met when the balance is 0 must be deleted (<code>r</code> of them), and the balance left at the end is the number of <code>'('</code> to delete (<code>l</code>). Any solution that deletes more than this is not minimal, so we only look for strings reachable with exactly <code>l</code> deleted openings and <code>r</code> deleted closings.",
               "Run a depth-first search over positions with the remaining budgets <code>l</code>, <code>r</code> and the current balance. At a parenthesis, either delete it (when that budget is positive) or keep it (and update the balance, rejecting a negative balance). Deleting the same character at different places of a run of equal characters gives the same string, so skip the deletion at index <code>i</code> when <code>s[i] == s[i-1]</code> and that previous character was kept: this makes deletions within a run happen at its start. The search can still reach the same string through different branches, so the finished strings are stored in a set whose size is the answer. With at most 20 parentheses the search space is small (a few ten thousand states in the worst case)."],
    time="O(2^n) worst case", space="O(n)",
    solution='''def countMinimalRepairs(s):
    # minimum deletions
    bal = r = 0
    for ch in s:
        if ch == '(':
            bal += 1
        elif ch == ')':
            if bal:
                bal -= 1
            else:
                r += 1
    l = bal
    results = set()
    n = len(s)

    def dfs(i, l, r, bal, cur):
        if bal < 0:
            return
        if i == n:
            if l == 0 and r == 0 and bal == 0:
                results.add("".join(cur))
            return
        ch = s[i]
        if ch == '(' and l > 0 and not (i > 0 and s[i - 1] == '(' and cur and cur[-1] == '('):
            dfs(i + 1, l - 1, r, bal, cur)
        elif ch == ')' and r > 0 and not (i > 0 and s[i - 1] == ')' and cur and cur[-1] == ')'):
            dfs(i + 1, l, r - 1, bal, cur)
        cur.append(ch)
        if ch == '(':
            dfs(i + 1, l, r, bal + 1, cur)
        elif ch == ')':
            dfs(i + 1, l, r, bal - 1, cur)
        else:
            dfs(i + 1, l, r, bal, cur)
        cur.pop()

    dfs(0, l, r, 0, [])
    return len(results)
''',
    tests=[["()())()"], ["(a)())()"], [")("], ["n"], ["()"], ["(()"], ["())"], ["(((a)"], [")))((("], ["a(b(c)d)e)"],
           ["()()()()()"], ["((())"]],
)
_r = rnd(7110)
p["tests"].append(["()())()" * 2 + "(a)()()"])
p["tests"].append([")(" * 10 + "abcde"])
p["tests"].append(["(()" * 5 + "))" + "xyz"])
_t = [_r.choice("()") for _ in range(20)] + list("abcde")
_r.shuffle(_t)
p["tests"].append(["".join(_t)])


def b_repair(s):
    pos = [i for i, c in enumerate(s) if c in "()"]
    for k in range(len(pos) + 1):
        res = set()
        for rem in itertools.combinations(pos, k):
            rem = set(rem)
            t = "".join(c for i, c in enumerate(s) if i not in rem)
            bal, ok = 0, True
            for c in t:
                if c == "(":
                    bal += 1
                elif c == ")":
                    bal -= 1
                    if bal < 0:
                        ok = False
                        break
            if ok and bal == 0:
                res.add(t)
        if res:
            return len(res)
    return 0


def g_repair(r):
    return ["".join(r.choices("()a", weights=[4, 4, 1])[0] for _ in range(r.randint(1, 13)))]


def v_repair(tests):
    for t in tests:
        s = t["args"][0]
        assert 1 <= len(s) <= 25 and re.fullmatch(r"[a-z()]+", s)
        assert sum(c in "()" for c in s) <= 20
        assert t["expected"] >= 1


CHECKS["count-minimal-bracket-repairs"] = (b_repair, g_repair, "exact")
VALIDATE["count-minimal-bracket-repairs"] = v_repair


p = add(
    id="min-cost-to-complete-bracket-sequence", title="Cheapest Way to Complete a Bracket Sequence", diff="Hard", topic=TOPIC, tier="extra",
    fn="minCostCompletion", params=[("s", "string"), ("a", "int[]"), ("b", "int[]")], ret="int", cmp="exact",
    desc="<p>The string <code>s</code> consists of <code>'('</code>, <code>')'</code> and <code>'?'</code>. Every <code>'?'</code> has to be replaced by a bracket. Let <code>q</code> be the number of question marks. The arrays <code>a</code> and <code>b</code> both have length <code>q</code>: the <code>k</code>-th question mark (from the left, 0-based) costs <code>a[k]</code> if you replace it by <code>'('</code> and <code>b[k]</code> if you replace it by <code>')'</code>.</p><p>The final string must be well-formed: every <code>'('</code> is closed by a later <code>')'</code>, every <code>')'</code> closes an earlier <code>'('</code>, and nothing is left open. Return the minimum total cost of the replacements, or <code>-1</code> if no choice gives a well-formed string.</p><p>For example, <code>s = \"??\"</code>, <code>a = [5, 1]</code>, <code>b = [1, 5]</code> has only one valid result, <code>\"()\"</code>, and costs <code>a[0] + b[1] = 10</code>.</p>",
    constraints=["1 &le; s.length &le; 5,000", "s contains only <code>(</code>, <code>)</code> and <code>?</code>", "a.length = b.length = number of <code>?</code> in s", "1 &le; a[k], b[k] &le; 1,000"],
    hints=["Try the cheap-looking assumption first: turn every <code>'?'</code> into <code>')'</code> and pay <code>b[k]</code> for each. What goes wrong while scanning from the left?",
           "The balance becomes negative at some point. You must have chosen <code>'('</code> for at least one earlier question mark. Changing one question mark from <code>')'</code> to <code>'('</code> adds 2 to every later balance and changes the cost by <code>a[k] - b[k]</code>.",
           "Scan left to right, push <code>a[k] - b[k]</code> of every question mark you pass into a min-heap, and whenever the balance drops below 0 pop the smallest value, add it to the cost and raise the balance by 2 (if the heap is empty the answer is -1). At the end the balance must be exactly 0."],
    editorial=["Start with the assumption that all question marks are <code>')'</code> and pay the sum of <code>b[k]</code>. While scanning, keep the balance. The first moment the balance is negative, some earlier question mark must become <code>'('</code>; flipping the candidate with the smallest extra cost <code>a[k] - b[k]</code> is the cheapest repair and raises every later prefix balance by 2. The heap holds the candidates seen so far (flipped ones are removed, so each is used once).",
               "The greedy choice is safe because a flip at any earlier position fixes the current violation equally well and also helps all later positions, so the cheapest available flip can always be exchanged into an optimal solution. Flips are only done when forced, so their number is minimal. If the heap is empty when the balance is negative, or the balance at the end is not 0 (the sequence has too many opening brackets, or an odd length), no completion exists. Time O(n log n), space O(n)."],
    time="O(n log n)", space="O(n)",
    solution='''import heapq

def minCostCompletion(s, a, b):
    heap = []
    cost = 0
    bal = 0
    k = 0
    for ch in s:
        if ch == '(':
            bal += 1
        elif ch == ')':
            bal -= 1
        else:
            cost += b[k]
            heapq.heappush(heap, a[k] - b[k])
            k += 1
            bal -= 1
        if bal < 0:
            if not heap:
                return -1
            cost += heapq.heappop(heap)
            bal += 2
    return cost if bal == 0 else -1
''',
    tests=[["(??)", [1, 2], [2, 1]], ["??", [5, 1], [1, 5]], ["()", [], []], ["?", [3], [4]], ["((?", [2], [1]], ["))??", [1, 1], [1, 1]],
           ["?(?", [1, 2], [3, 1]], ["????", [1, 10, 10, 10], [10, 10, 10, 1]], ["??(?", [3, 3, 3], [3, 3, 3]],
           ["?)?(??", [4, 2, 7, 1], [5, 9, 1, 6]], ["(?)?", [1, 2], [1, 2]], ["?" * 6, [7, 1, 5, 2, 8, 3], [2, 6, 4, 5, 1, 9]]],
)
_r = rnd(7111)


def _mk_cost(q, hi=1000):
    return [_r.randint(1, hi) for _ in range(q)], [_r.randint(1, hi) for _ in range(q)]


_s = "".join(_r.choices("()?", weights=[1, 1, 6])[0] for _ in range(4000))
_aa, _bb = _mk_cost(_s.count("?"))
p["tests"].append([_s, _aa, _bb])
_s = "?" * 5000
_aa, _bb = _mk_cost(5000)
p["tests"].append([_s, _aa, _bb])
_t = list(_balanced(_r, 2500, bias=0.55))
for _i in _r.sample(range(5000), 2500):
    _t[_i] = "?"
_s = "".join(_t)
_aa, _bb = _mk_cost(_s.count("?"))
p["tests"].append([_s, _aa, _bb])
p["tests"].append(["?" * 4999, [1] * 4999, [1] * 4999])


def b_cost(s, a, b):
    qs = [i for i, c in enumerate(s) if c == "?"]
    best = -1
    for mask in range(1 << len(qs)):
        t = list(s)
        cost = 0
        for k, i in enumerate(qs):
            if (mask >> k) & 1:
                t[i] = "("
                cost += a[k]
            else:
                t[i] = ")"
                cost += b[k]
        bal, ok = 0, True
        for c in t:
            bal += 1 if c == "(" else -1
            if bal < 0:
                ok = False
                break
        if ok and bal == 0 and (best == -1 or cost < best):
            best = cost
    return best


def g_cost(r):
    n = r.randint(1, 12)
    s = "".join(r.choices("()?", weights=[2, 2, 3])[0] for _ in range(n))
    q = s.count("?")
    return [s, [r.randint(1, 9) for _ in range(q)], [r.randint(1, 9) for _ in range(q)]]


def v_cost(tests):
    for t in tests:
        s, a, b = t["args"]
        assert 1 <= len(s) <= 5000 and set(s) <= set("()?")
        assert len(a) == len(b) == s.count("?")
        assert all(1 <= x <= 1000 for x in a + b)
        assert t["expected"] >= -1
    assert any(t["expected"] == -1 for t in tests) and any(t["expected"] > 0 for t in tests)


CHECKS["min-cost-to-complete-bracket-sequence"] = (b_cost, g_cost, "exact")
VALIDATE["min-cost-to-complete-bracket-sequence"] = v_cost
