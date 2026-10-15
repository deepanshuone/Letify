from lib import add, rnd, CHECKS, VALIDATE, gen_arr  # noqa: F401
# Problems: stack, expression evaluation (postfix and prefix notation, calculators, parsing). See data/lib.py for the registry.
import re

TOPIC = "Stack"
LIM = 2 ** 31 - 1
MOD = 10 ** 9 + 7
OPC = {"+": 100001, "-": 100002, "*": 100003, "/": 100004}
A_, S_, M_, D_ = 100001, 100002, 100003, 100004


# ---------------------------------------------------------------- shared helpers for test generation and brute forces

def tdiv(a, b):
    q = abs(a) // abs(b)
    return q if (a < 0) == (b < 0) else -q


def arith(op, a, b):
    """Exact result of a binary operation, or None if it is undefined (division by zero)."""
    if op == "+":
        return a + b
    if op == "-":
        return a - b
    if op == "*":
        return a * b
    if op == "/":
        return None if b == 0 else tdiv(a, b)
    raise ValueError(op)


def safe_val(op, a, b):
    v = arith(op, a, b)
    return v if v is not None and abs(v) <= LIM else None


def rpn_walk(r, n_ops, leaf, ops, valfn=None, weights=None, p_op=0.5):
    """Random postfix sequence with n_ops binary operators.

    leaf() -> (item, value); valfn(op, va, vb) -> value or None (None = not allowed here).
    Returns a list of (is_operator, payload)."""
    toks, st = [], []
    pushed = done = 0
    while done < n_ops:
        if len(st) >= 2 and (pushed == n_ops + 1 or r.random() < p_op):
            vb = st.pop()
            va = st.pop()
            order = r.choices(list(ops), weights=weights, k=1) + r.sample(list(ops), len(ops))
            for op in order:
                v = 0 if valfn is None else valfn(op, va, vb)
                if v is not None:
                    break
            else:
                raise AssertionError("no valid operator")
            toks.append((True, op))
            st.append(v)
            done += 1
        else:
            item, v = leaf()
            toks.append((False, item))
            st.append(v)
            pushed += 1
    if not toks:
        item, v = leaf()
        toks.append((False, item))
    return toks


def rpn_ints(r, n_ops, vmax=20, ops="+-*/", p_op=0.5, weights=None, big=0.0):
    """Postfix token list (operator codes 100001..100004) whose every intermediate value fits in 32 bits."""
    def leaf():
        v = r.randint(-100000, 100000) if r.random() < big else r.randint(-vmax, vmax)
        return v, v
    toks = rpn_walk(r, n_ops, leaf, ops, safe_val, weights, p_op)
    return [OPC[x] if is_op else x for is_op, x in toks]


def to_infix(r, toks, prec, right=(), extra=0.0, unary=None, p_un=0.0):
    """Infix text for a postfix token list: brackets only where needed, plus redundant ones with probability `extra`.
    With `unary` set, that prefix operator is put in front of operands with probability p_un."""
    st = []

    def finish(s, p):
        if r.random() < extra:
            s, p = "(" + s + ")", 99
        if unary and r.random() < p_un:
            s, p = unary + (s if p == 99 else "(" + s + ")"), 99
        return s, p

    for is_op, x in toks:
        if not is_op:
            st.append(finish(x, 99))
            continue
        b, pb = st.pop()
        a, pa = st.pop()
        p = prec[x]
        if pa < p or (pa == p and x in right):
            a = "(" + a + ")"
        if pb < p or (pb == p and x not in right):
            b = "(" + b + ")"
        st.append(finish(a + x + b, p))
    return st[0][0]


def parse_tree(s, prec, right=()):
    """Precedence-climbing parser for single-character operands; returns nested tuples (op, left, right)."""
    pos = [0]

    def atom():
        c = s[pos[0]]
        pos[0] += 1
        if c == "(":
            t = expr(0)
            pos[0] += 1
            return t
        return c

    def expr(minp):
        left = atom()
        while pos[0] < len(s) and s[pos[0]] in prec and prec[s[pos[0]]] >= minp:
            op = s[pos[0]]
            pos[0] += 1
            rhs = expr(prec[op] if op in right else prec[op] + 1)
            left = (op, left, rhs)
        return left

    t = expr(0)
    assert pos[0] == len(s)
    return t


def balanced(s):
    d = 0
    for c in s:
        d += (c == "(") - (c == ")")
        assert d >= 0
    assert d == 0


# ================================================================ 1. valid postfix token sequence (Easy)

p = add(
    id="valid-postfix-token-sequence", title="Valid Postfix Token Sequence", diff="Easy", topic=TOPIC, tier="common",
    fn="isValidPostfix", params=[("tokens", "int[]")], ret="bool", cmp="exact",
    desc="<p>In <em>postfix</em> (reverse Polish) notation every binary operator is written <em>after</em> its two operands, so <code>3 4 +</code> means 3 + 4 and <code>3 4 + 5 *</code> means (3 + 4) * 5. No brackets are needed.</p>"
         "<p>An expression is given as an integer array <code>tokens</code>. The four values <code>100001</code>, <code>100002</code>, <code>100003</code> and <code>100004</code> are the operators <code>+</code>, <code>-</code>, <code>*</code> and <code>/</code>. Every other token is an operand (a number) with absolute value at most 100,000.</p>"
         "<p>Return <code>true</code> if <code>tokens</code> is a complete, well-formed postfix expression: when the tokens are processed from left to right, every operator finds two finished values to work on, and after the last token exactly one value is left. Only the shape matters; the numbers themselves and division by zero are irrelevant.</p>"
         "<p>Example: <code>[3, 4, 100001, 5, 100003]</code> is valid (it is (3 + 4) * 5). <code>[3, 100001, 4]</code> is not (the operator has only one value before it) and neither is <code>[1, 2]</code> (two values remain).</p>",
    constraints=["1 &le; tokens.length &le; 10,000", "A token in 100001..100004 is an operator; every other token is an operand with -100,000 &le; value &le; 100,000"],
    hints=["Imagine evaluating the expression with a stack of values. What does an operand do to the stack, and what does an operator do?",
           "You do not need the values. Only the number of finished values on the stack matters: an operand adds one, an operator removes two and adds one back.",
           "Keep a single counter <code>depth</code>. Fail as soon as an operator is met while <code>depth &lt; 2</code>. After the last token the expression is valid exactly when <code>depth == 1</code>."],
    editorial=["Evaluating a postfix expression uses a stack: an operand is pushed, an operator pops two values and pushes one result. The expression is well formed exactly when this process never runs short of values and ends with a single value. Since the actual values do not matter, the stack can be replaced by its size.",
               "Scan the tokens with a counter <code>depth</code> starting at 0. An operand makes <code>depth += 1</code>. An operator needs two values, so if <code>depth &lt; 2</code> return false; otherwise two values are replaced by one and <code>depth -= 1</code>. At the end return <code>depth == 1</code> (0 can only happen for an empty input, 2 or more means unused operands are left over).",
               "Each token is looked at once: O(n) time and O(1) extra space."],
    time="O(n)", space="O(1)",
    solution='''def isValidPostfix(tokens):
    depth = 0
    for t in tokens:
        if 100001 <= t <= 100004:
            if depth < 2:
                return False
            depth -= 1
        else:
            depth += 1
    return depth == 1
''',
    tests=[[[5]], [[3, 4, A_]], [[3, 4, A_, 5, M_]], [[A_]], [[1, 2]], [[3, A_, 4]], [[1, 2, 3, A_]], [[1, 2, A_, A_]], [[1, 2, A_, 3]],
           [[-5, -7, S_, 8, D_]], [[1, 2, 3, A_, M_]], [[1, 2, 3, 4, A_, A_, A_]], [[100000, -100000, D_, 7, S_, 9]]],
)
_r = rnd(5401)
_v = rpn_ints(_r, 2000, p_op=0.45)
p["tests"].append([_v])
p["tests"].append([_v[:-1]])
p["tests"].append([[1] * 3000 + [A_] * 2999])
p["tests"].append([[1] * 2500 + [S_] * 2500])


def b_valid_post(tokens):
    def parse(i):  # start index of the expression that ends at index i, or None
        if i < 0:
            return None
        if not (100001 <= tokens[i] <= 100004):
            return i
        j = parse(i - 1)
        if j is None:
            return None
        return parse(j - 1)
    return parse(len(tokens) - 1) == 0


def g_valid_post(r):
    pool = [1, 2, 5, -3, A_, S_, M_, D_]
    toks = rpn_ints(r, r.randint(0, 4), 9)
    if r.random() < 0.6:
        t = toks[:]
        k = r.randint(0, 3)
        if k == 0 and len(t) > 1:
            del t[r.randrange(len(t))]
        elif k == 1:
            t.insert(r.randint(0, len(t)), r.choice(pool))
        elif k == 2:
            t[r.randrange(len(t))] = r.choice(pool)
        elif len(t) > 1:
            i, j = r.sample(range(len(t)), 2)
            t[i], t[j] = t[j], t[i]
        toks = t
    return [toks]


def v_valid_post(tests):
    for t in tests:
        a = t["args"][0]
        assert 1 <= len(a) <= 10000
        for x in a:
            assert 100001 <= x <= 100004 or abs(x) <= 100000
    assert any(t["expected"] for t in tests) and any(not t["expected"] for t in tests)


CHECKS["valid-postfix-token-sequence"] = (b_valid_post, g_valid_post, "exact")
VALIDATE["valid-postfix-token-sequence"] = v_valid_post

# ================================================================ 2. evaluate postfix token list (Medium, must)

p = add(
    id="evaluate-postfix-token-list", title="Evaluate a Postfix Expression", diff="Medium", topic=TOPIC, tier="must",
    fn="evalPostfix", params=[("tokens", "int[]")], ret="int", cmp="exact",
    desc="<p>A postfix (reverse Polish) expression is stored as an integer array <code>tokens</code>. The values <code>100001</code>, <code>100002</code>, <code>100003</code> and <code>100004</code> stand for the binary operators <code>+</code>, <code>-</code>, <code>*</code> and <code>/</code>; every other token is an operand with absolute value at most 100,000. An operator is written after its two operands: <code>[7, 2, 100002]</code> is 7 - 2.</p>"
         "<p>Evaluate the expression and return its value. Division discards the fractional part, i.e. it rounds toward zero (<code>7 / 2 = 3</code>, <code>-7 / 2 = -3</code>).</p>"
         "<p>The expression is always valid, no division by zero happens, and every intermediate result fits in a signed 32-bit integer.</p>"
         "<p>Examples: <code>[2, 1, 100001, 3, 100003]</code> is (2 + 1) * 3 = 9. <code>[4, 13, 5, 100004, 100001]</code> is 4 + (13 / 5) = 6. <code>[-7, 2, 100004]</code> is -3.</p>",
    constraints=["1 &le; tokens.length &le; 10,000", "tokens is a valid postfix expression; operators are 100001 (+), 100002 (-), 100003 (*), 100004 (/)", "Operands satisfy -100,000 &le; value &le; 100,000", "No division by zero; every intermediate value is within [-(2<sup>31</sup> - 1), 2<sup>31</sup> - 1]"],
    hints=["In postfix notation the two operands of an operator are the two values computed just before it.",
           "Use a stack: push every operand. When you meet an operator, pop two values, combine them and push the result.",
           "Mind the order: the value popped <em>first</em> is the right operand. Subtraction and division need <code>second_popped op first_popped</code>. For division, compute with absolute values and fix the sign, because floor division rounds negative results the wrong way."],
    editorial=["Postfix notation was designed for stacks. Walk through the tokens from left to right. An operand is pushed. An operator takes the two most recent finished values: pop <code>b</code> (the right operand), then pop <code>a</code> (the left operand), compute <code>a op b</code> and push it back. When all tokens are consumed the stack holds one value, the answer.",
               "The only subtle part is division. Python's <code>//</code> rounds toward negative infinity, but the problem asks to round toward zero. Compute <code>q = abs(a) // abs(b)</code> and give it a minus sign when exactly one of <code>a</code>, <code>b</code> is negative.",
               "Every token is processed once with O(1) work, so the time is O(n); the stack can hold up to O(n) values."],
    time="O(n)", space="O(n)",
    solution='''def evalPostfix(tokens):
    stack = []
    for t in tokens:
        if 100001 <= t <= 100004:
            b = stack.pop()
            a = stack.pop()
            if t == 100001:
                stack.append(a + b)
            elif t == 100002:
                stack.append(a - b)
            elif t == 100003:
                stack.append(a * b)
            else:
                q = abs(a) // abs(b)
                stack.append(q if (a < 0) == (b < 0) else -q)
        else:
            stack.append(t)
    return stack[0]
''',
    tests=[[[2, 1, A_, 3, M_]], [[4, 13, 5, D_, A_]], [[-7, 2, D_]], [[7, -2, D_]], [[-7, -2, D_]], [[0, 5, D_]], [[10, 3, S_]], [[3, 10, S_]], [[42]],
           [[10, 6, 9, 3, A_, -11, M_, D_, M_, 17, A_, 5, A_]], [[46340, 46340, M_]], [[-46340, 46340, M_, 100000, 21474, M_, A_]],
           [[5, 1, 2, A_, 4, M_, A_, 3, S_]]],
)
_r = rnd(5402)
p["tests"].append([rpn_ints(_r, 1800, 30, p_op=0.2, weights=[3, 3, 1, 2], big=0.2)])
p["tests"].append([rpn_ints(_r, 1800, 50, p_op=0.8, weights=[3, 3, 2, 3], big=0.3)])
p["tests"].append([rpn_ints(_r, 1500, 100000, p_op=0.5, weights=[3, 3, 1, 2], big=1.0)])


def b_eval_post(tokens):
    def parse(i):  # (value, start index) of the expression ending at index i
        t = tokens[i]
        if not (100001 <= t <= 100004):
            return t, i
        vb, j = parse(i - 1)
        va, k = parse(j - 1)
        return arith("+-*/"[t - 100001], va, vb), k
    return parse(len(tokens) - 1)[0]


def g_eval_post(r):
    return [rpn_ints(r, r.randint(0, 6), 12, weights=[2, 2, 2, 3])]


def big_post(tokens):
    st = []
    for t in tokens:
        if 100001 <= t <= 100004:
            b = st.pop()
            a = st.pop()
            v = arith("+-*/"[t - 100001], a, b)
            assert v is not None and abs(v) <= LIM, "bad intermediate"
            st.append(v)
        else:
            assert abs(t) <= 100000
            st.append(t)
    assert len(st) == 1
    return st[0]


def v_eval_post(tests):
    for t in tests:
        a = t["args"][0]
        assert 1 <= len(a) <= 10000
        assert big_post(a) == t["expected"]
    assert any(len(t["args"][0]) > 2000 for t in tests)


CHECKS["evaluate-postfix-token-list"] = (b_eval_post, g_eval_post, "exact")
VALIDATE["evaluate-postfix-token-list"] = v_eval_post

# ================================================================ 3. evaluate prefix digit expression (Easy)

p = add(
    id="evaluate-prefix-digit-expression", title="Evaluate a Prefix Expression", diff="Easy", topic=TOPIC, tier="extra",
    fn="evalPrefix", params=[("expr", "string")], ret="int", cmp="exact",
    desc="<p>In <em>prefix</em> (Polish) notation an operator is written <em>before</em> its two operands. The string <code>expr</code> consists of single digits <code>0</code>-<code>9</code> and the binary operators <code>+</code>, <code>-</code> and <code>*</code>, with no spaces and no brackets. For example <code>+*34-82</code> means (3 * 4) + (8 - 2) = 18 and <code>-92</code> means 9 - 2 = 7.</p>"
         "<p>The string is always a valid prefix expression. Evaluate it and return the result. Note that <code>-</code> subtracts the <em>second</em> operand from the <em>first</em>: <code>-29</code> is -7.</p>",
    constraints=["1 &le; expr.length &le; 9,999", "expr contains only the characters 0-9, '+', '-' and '*' and is a valid prefix expression", "Every intermediate value fits in a signed 32-bit integer"],
    hints=["The operands of an operator come right after it. If you read the string from the right, what do you know when you reach an operator?",
           "Scan from right to left with a stack. A digit is pushed. When you see an operator, the two operands have already been evaluated and are on the stack.",
           "On an operator pop <code>a</code> first (it is the <em>left</em> operand, because it was pushed last) and then <code>b</code>, and push <code>a op b</code>. The answer is the single value left at the end."],
    editorial=["Reading a prefix expression from right to left turns it into a postfix evaluation. When the scan reaches an operator, everything to its right has already been processed, so both of its operands are finished values on the stack.",
               "Digit: push it. Operator: pop <code>a</code> (the top, which is the first operand because the scan runs right to left), pop <code>b</code>, push <code>a op b</code>. Getting this order wrong only matters for <code>-</code>, so test <code>-29</code>.",
               "Time O(n), stack O(n). A recursive parser that reads left to right works as well, but with 10,000 characters its recursion could get deep, so the explicit stack is the safer choice."],
    time="O(n)", space="O(n)",
    solution='''def evalPrefix(expr):
    stack = []
    for ch in reversed(expr):
        if ch.isdigit():
            stack.append(int(ch))
        else:
            a = stack.pop()
            b = stack.pop()
            if ch == '+':
                stack.append(a + b)
            elif ch == '-':
                stack.append(a - b)
            else:
                stack.append(a * b)
    return stack[0]
''',
    tests=[["+*34-82"], ["-92"], ["-29"], ["7"], ["0"], ["*+12-34"], ["+++1234"], ["-1-2-34"], ["*9*9*9*9*9*9*9*99"], ["--9-8-7-654"], ["+0*00"]],
)
_r = rnd(5403)


def prefix_str(toks):
    st = []
    for is_op, x in toks:
        if is_op:
            b = st.pop()
            a = st.pop()
            st.append(x + a + b)
        else:
            st.append(str(x))
    return st[0]


def pre_leaf(r):
    def leaf():
        v = r.randint(0, 9)
        return v, v
    return leaf


p["tests"].append([prefix_str(rpn_walk(_r, 4999, pre_leaf(_r), "+-*", safe_val, [4, 4, 1], 0.5))])
p["tests"].append(["+" * 2500 + "-" * 2499 + "".join(_r.choice("0123456789") for _ in range(5000))])
p["tests"].append(["".join(_r.choice("+-") + _r.choice("123456789") for _ in range(4999)) + "5"])


def b_prefix(s):
    pos = [0]

    def parse():
        c = s[pos[0]]
        pos[0] += 1
        if c.isdigit():
            return int(c)
        x = parse()
        y = parse()
        return arith(c, x, y)
    return parse()


def g_prefix(r):
    return [prefix_str(rpn_walk(r, r.randint(0, 6), pre_leaf(r), "+-*", safe_val, None, r.choice([0.2, 0.5, 0.8])))]


def v_prefix(tests):
    for t in tests:
        s = t["args"][0]
        assert 1 <= len(s) <= 9999 and len(s) % 2 == 1
        assert re.fullmatch(r"[0-9+\-*]+", s)
        ops = sum(c in "+-*" for c in s)
        assert len(s) == 2 * ops + 1
        assert abs(t["expected"]) <= LIM
        st = []
        for ch in reversed(s):  # all intermediates, with exact integers
            if ch.isdigit():
                st.append(int(ch))
            else:
                a, b = st.pop(), st.pop()
                v = arith(ch, a, b)
                assert abs(v) <= LIM
                st.append(v)
        assert len(st) == 1


CHECKS["evaluate-prefix-digit-expression"] = (b_prefix, g_prefix, "exact")
VALIDATE["evaluate-prefix-digit-expression"] = v_prefix

# ================================================================ 4. calculator with division, no brackets (Medium, must)

p = add(
    id="evaluate-expression-with-division", title="Calculator Without Brackets", diff="Medium", topic=TOPIC, tier="must",
    fn="calculate", params=[("expr", "string")], ret="int", cmp="exact",
    desc="<p>The string <code>expr</code> is an arithmetic expression without spaces and without brackets. It contains non-negative integer literals and the binary operators <code>+</code>, <code>-</code>, <code>*</code> and <code>/</code>. Multiplication and division have higher priority than addition and subtraction, and operators of the same priority are applied from left to right. Division is integer division that drops the fractional part.</p>"
         "<p>Evaluate the expression and return its value. Do not use any built-in function that evaluates a string as code.</p>"
         "<p>Examples: <code>3+2*2</code> is 7, <code>14-3/2</code> is 13, <code>100/10/5</code> is 2 and <code>5-6/4</code> is 4.</p>",
    constraints=["1 &le; expr.length &le; 10,000", "expr contains only digits and the characters '+', '-', '*', '/' and is a valid expression (it starts and ends with a digit, no two operators are adjacent)",
                 "Literals have no leading zeros (except the single digit \"0\") and are at most 2<sup>31</sup> - 1", "Never divides by zero; every literal, every partial product or quotient and every partial sum has absolute value at most 2<sup>31</sup> - 1"],
    hints=["Without brackets there is only one level of priority to handle: products and quotients bind tighter than sums and differences.",
           "Treat the expression as a sum of signed terms. A term is a chain of numbers joined by <code>*</code> and <code>/</code>. Keep a stack (or just a running total and the last term) of the terms.",
           "Remember the operator that came <em>before</em> the number you just finished reading. <code>+</code>: push the number. <code>-</code>: push its negative. <code>*</code> or <code>/</code>: combine it with the top of the stack. At the end add up the stack. Add a sentinel operator at the end so the last number is processed too."],
    editorial=["Split the expression into terms separated by <code>+</code> and <code>-</code>. Inside a term the operators <code>*</code> and <code>/</code> are applied from left to right, and the value of the whole expression is the sum of the signed terms. A stack of term values handles this naturally.",
               "Read the string left to right, collecting the digits of the current number. When you hit an operator (or the end of the string) the number is complete, and you act according to the <em>previous</em> operator: <code>+</code> pushes <code>num</code>, <code>-</code> pushes <code>-num</code>, <code>*</code> replaces the top by <code>top * num</code>, <code>/</code> replaces it by <code>top / num</code> rounded toward zero. Then remember the new operator and reset the number.",
               "The top of the stack can be negative (the term was subtracted), so round toward zero: dividing <code>-6</code> by <code>4</code> must give <code>-1</code>, which is the same as <code>-(6 / 4)</code>. Finally return the sum of the stack. Time O(n); space O(n) with a stack, or O(1) if you only keep the running total and the last term."],
    time="O(n)", space="O(n)",
    solution='''def calculate(expr):
    stack = []
    num = 0
    prev = '+'
    for ch in expr + '+':
        if ch.isdigit():
            num = num * 10 + int(ch)
            continue
        if prev == '+':
            stack.append(num)
        elif prev == '-':
            stack.append(-num)
        elif prev == '*':
            stack.append(stack.pop() * num)
        else:
            top = stack.pop()
            q = abs(top) // num
            stack.append(q if top >= 0 else -q)
        prev = ch
        num = 0
    return sum(stack)
''',
    tests=[["3+2*2"], ["14-3/2"], ["100/10/5"], ["5-6/4"], ["0"], ["7"], ["2*3*4"], ["1+2*3-4/2+5*6/7"], ["1-1-1-1"], ["0*5+3"], ["9/2*2"],
           ["1000000000/3*3"], ["2147483647"], ["46340*46340"], ["8-9/2*3+1"]],
)


def gen_flat(r, n_terms, max_chain, lit_hi):
    total = 0
    out = []
    for t in range(n_terms):
        cur = r.randint(0, lit_hi)
        s = str(cur)
        for _ in range(r.randint(0, max_chain)):
            if r.random() < 0.5:
                lit = r.randint(0, lit_hi)
                if cur * lit <= LIM:
                    s += "*" + str(lit)
                    cur *= lit
                    continue
            lit = r.randint(1, lit_hi)
            s += "/" + str(lit)
            cur //= lit
        if t == 0:
            total = cur
            out.append(s)
            continue
        sign = r.choice("+-")
        if sign == "+" and total + cur > LIM:
            sign = "-"
        elif sign == "-" and total - cur < -LIM:
            sign = "+"
        total += cur if sign == "+" else -cur
        out.append(sign + s)
    return "".join(out)


_r = rnd(5404)
p["tests"].append([gen_flat(_r, 1000, 3, 9)])
p["tests"].append([gen_flat(_r, 500, 3, 1000)])
p["tests"].append([gen_flat(_r, 300, 4, 1000000000)])


def b_calc(expr):
    return eval(expr.replace("/", "//"), {"__builtins__": {}})


def g_calc(r):
    return [gen_flat(r, r.randint(1, 4), 3, r.choice([3, 9, 30]))]


def v_calc(tests):
    for t in tests:
        s = t["args"][0]
        assert 1 <= len(s) <= 10000
        assert re.fullmatch(r"[0-9]+([+\-*/][0-9]+)*", s)
        total = 0
        for m in re.finditer(r"([+\-]?)([0-9]+(?:[*/][0-9]+)*)", s):
            term = m.group(2)
            parts = re.split(r"([*/])", term)
            cur = int(parts[0])
            for k in range(1, len(parts), 2):
                n = int(parts[k + 1])
                assert abs(n) <= LIM and not (len(parts[k + 1]) > 1 and parts[k + 1][0] == "0")
                if parts[k] == "*":
                    cur *= n
                else:
                    assert n != 0
                    cur //= n
                assert cur <= LIM
            assert not (len(parts[0]) > 1 and parts[0][0] == "0") and int(parts[0]) <= LIM
            total += -cur if m.group(1) == "-" else cur
            assert abs(total) <= LIM
        assert total == t["expected"]


CHECKS["evaluate-expression-with-division"] = (b_calc, g_calc, "exact")
VALIDATE["evaluate-expression-with-division"] = v_calc

# ================================================================ 5. infix to postfix with power (Medium)

PREC5 = {"+": 1, "-": 1, "*": 2, "/": 2, "^": 3}

p = add(
    id="infix-to-postfix-with-power", title="Convert Infix to Postfix", diff="Medium", topic=TOPIC, tier="common",
    fn="toPostfix", params=[("expr", "string")], ret="string", cmp="exact",
    desc="<p>The string <code>expr</code> is an infix expression made of single digits <code>0</code>-<code>9</code>, the binary operators <code>+</code>, <code>-</code>, <code>*</code>, <code>/</code>, <code>^</code> and round brackets. Priorities from low to high: <code>+</code> and <code>-</code>, then <code>*</code> and <code>/</code>, then <code>^</code> (power). Operators of equal priority are applied left to right, except <code>^</code>, which is applied right to left (<code>2^3^2</code> means <code>2^(3^2)</code>). Brackets override priorities. There are no unary operators and no spaces.</p>"
         "<p>Return the same expression in postfix notation: digits and operators only, no brackets, each operator written right after its two operands. The result is unique.</p>"
         "<p>Examples: <code>3+4*2</code> becomes <code>342*+</code>, <code>(1+2)*3</code> becomes <code>12+3*</code>, <code>8-3-2</code> becomes <code>83-2-</code> and <code>2^3^2</code> becomes <code>232^^</code>.</p>",
    constraints=["1 &le; expr.length &le; 10,000", "expr contains only the characters 0-9, + - * / ^ ( ) and is a valid expression as described", "Brackets are balanced; they may be redundant, e.g. <code>((7))</code>"],
    hints=["In the output the digits keep their order. Only the operators move: each one has to be delayed until both of its operands have been written.",
           "Use a stack for operators (and brackets). A digit goes straight to the output. Before pushing an operator, pop to the output the operators on the stack that must be applied first.",
           "Pop while the top of the stack is not <code>(</code> and has higher priority than the new operator, or equal priority when the new operator is left-associative (every operator except <code>^</code>). A <code>)</code> pops everything down to its matching <code>(</code>. At the end pop all that is left."],
    editorial=["This is Dijkstra's shunting-yard algorithm. Scan the expression from left to right. A digit is appended to the output immediately, because operands never change their relative order. An opening bracket is pushed. A closing bracket pops operators to the output until the matching opening bracket, which is discarded.",
               "For an operator <code>c</code>, first pop to the output every operator <code>top</code> on the stack (stopping at a bracket) that has to be applied before <code>c</code>: <code>prec(top) &gt; prec(c)</code>, or <code>prec(top) == prec(c)</code> and <code>c</code> is left-associative. For <code>^</code> equal priorities are not popped, which makes <code>2^3^2</code> group to the right. Then push <code>c</code>. After the last character pop all remaining operators.",
               "Every character is pushed and popped at most once, giving O(n) time and O(n) space for the stack."],
    time="O(n)", space="O(n)",
    solution='''def toPostfix(expr):
    prec = {'+': 1, '-': 1, '*': 2, '/': 2, '^': 3}
    out = []
    ops = []
    for c in expr:
        if c.isdigit():
            out.append(c)
        elif c == '(':
            ops.append(c)
        elif c == ')':
            while ops[-1] != '(':
                out.append(ops.pop())
            ops.pop()
        else:
            while ops and ops[-1] != '(' and (
                    prec[ops[-1]] > prec[c] or (prec[ops[-1]] == prec[c] and c != '^')):
                out.append(ops.pop())
            ops.append(c)
    while ops:
        out.append(ops.pop())
    return "".join(out)
''',
    tests=[["3+4*2"], ["(1+2)*3"], ["8-3-2"], ["2^3^2"], ["(2^3)^2"], ["7"], ["((7))"], ["8/(4/2)"], ["1+2*3^4-5/(6-7)"], ["9-(8-(7-(6-5)))"],
           ["2*3^2*4"], ["1^2+3^4*5"], ["(1+2)*(3+4)*(5+6)"]],
)
_r = rnd(5405)


def digit_leaf(r):
    def leaf():
        return str(r.randint(0, 9)), 0
    return leaf


p["tests"].append([to_infix(_r, rpn_walk(_r, 2300, digit_leaf(_r), "+-*/^", None, [3, 3, 3, 2, 1], 0.5), PREC5, ("^",), 0.1)])
p["tests"].append([to_infix(_r, rpn_walk(_r, 2000, digit_leaf(_r), "+-*/^", None, [1, 1, 1, 1, 2], 0.2), PREC5, ("^",), 0.3)])
p["tests"].append(["(" * 2400 + "1+2" + ")*3" * 2400])


def b_postfix(expr):
    def post(t):
        return t if isinstance(t, str) else post(t[1]) + post(t[2]) + t[0]
    return post(parse_tree(expr, PREC5, ("^",)))


def g_postfix(r):
    toks = rpn_walk(r, r.randint(0, 6), digit_leaf(r), "+-*/^", None, None, r.choice([0.3, 0.6]))
    return [to_infix(r, toks, PREC5, ("^",), 0.2)]


def v_postfix(tests):
    for t in tests:
        s = t["args"][0]
        assert 1 <= len(s) <= 10000
        assert re.fullmatch(r"[0-9+\-*/^()]+", s)
        balanced(s)
        assert sorted(c for c in t["expected"] if c.isdigit()) == sorted(c for c in s if c.isdigit())
        assert len(t["expected"]) == sum(c in "0123456789+-*/^" for c in s)


CHECKS["infix-to-postfix-with-power"] = (b_postfix, g_postfix, "exact")
VALIDATE["infix-to-postfix-with-power"] = v_postfix

# ================================================================ 6. custom operator priorities (Medium)

p = add(
    id="evaluate-with-custom-operator-priorities", title="Calculator With Custom Priorities", diff="Medium", topic=TOPIC, tier="extra",
    fn="evaluateWithPriorities", params=[("expr", "string"), ("prio", "int[]")], ret="int", cmp="exact",
    desc="<p>The string <code>expr</code> is an expression without spaces made of non-negative integer literals, the binary operators <code>+</code>, <code>-</code>, <code>*</code> and round brackets. There are no unary operators.</p>"
         "<p>This calculator does not use the usual priorities. The array <code>prio</code> has three values: <code>prio[0]</code> is the priority of <code>+</code>, <code>prio[1]</code> of <code>-</code> and <code>prio[2]</code> of <code>*</code>. An operator with a <em>higher</em> priority number is applied before one with a lower number; operators with equal priority are applied from left to right. Brackets always override priorities.</p>"
         "<p>Return the value of the expression modulo <code>1,000,000,007</code>, as a number from <code>0</code> to <code>1,000,000,006</code> (also when the true value is negative).</p>"
         "<p>Examples: for <code>2+3*4</code> with <code>prio = [1, 1, 2]</code> (the usual rules) the answer is 14; with <code>prio = [2, 2, 1]</code> it is (2+3)*4 = 20. For <code>10-3+2</code> with <code>prio = [2, 1, 3]</code> the <code>+</code> goes first: 10-(3+2) = 5.</p>",
    constraints=["1 &le; expr.length &le; 10,000", "expr is a valid expression with literals in [0, 10<sup>9</sup>] without leading zeros (except \"0\") and balanced brackets", "prio.length == 3 and 0 &le; prio[i] &le; 9"],
    hints=["With the normal rules you would use two stacks (numbers and operators). The only thing that changes here is how two operators are compared.",
           "Keep a stack of values and a stack of pending operators. Before pushing a new operator, apply the pending operators on top that must be evaluated first.",
           "Apply the top operator while it is not a <code>(</code> and its priority is greater than or equal to the new one (equal means left to right). A <code>)</code> applies everything down to its <code>(</code>. Do all arithmetic modulo 10<sup>9</sup>+7: the operations <code>+</code>, <code>-</code>, <code>*</code> stay correct under a modulus."],
    editorial=["This is the shunting-yard evaluation with priorities taken from a table instead of being hard-coded. Scan the string: a number is pushed on the value stack; <code>(</code> is pushed on the operator stack; for <code>)</code> apply operators until the matching <code>(</code> and drop it.",
               "For an operator <code>c</code>: while the operator stack is not empty, its top is not <code>(</code> and <code>pr[top] &gt;= pr[c]</code>, apply the top (pop two values <code>a</code>, <code>b</code>, push <code>a top b</code>). Using <code>&gt;=</code> makes equal priorities left-associative. Then push <code>c</code>. After the scan apply everything that is left; the single remaining value is the answer.",
               "Addition, subtraction and multiplication are ring operations, so every intermediate result can be reduced modulo 10<sup>9</sup>+7 without changing the final remainder. In Python <code>%</code> already returns a non-negative number. Time O(n), space O(n)."],
    time="O(n)", space="O(n)",
    solution='''def evaluateWithPriorities(expr, prio):
    MOD = 10 ** 9 + 7
    pr = {'+': prio[0], '-': prio[1], '*': prio[2]}
    vals = []
    ops = []

    def apply():
        op = ops.pop()
        b = vals.pop()
        a = vals.pop()
        if op == '+':
            vals.append((a + b) % MOD)
        elif op == '-':
            vals.append((a - b) % MOD)
        else:
            vals.append(a * b % MOD)

    i = 0
    n = len(expr)
    while i < n:
        c = expr[i]
        if c.isdigit():
            j = i
            while j < n and expr[j].isdigit():
                j += 1
            vals.append(int(expr[i:j]) % MOD)
            i = j
            continue
        if c == '(':
            ops.append(c)
        elif c == ')':
            while ops[-1] != '(':
                apply()
            ops.pop()
        else:
            while ops and ops[-1] != '(' and pr[ops[-1]] >= pr[c]:
                apply()
            ops.append(c)
        i += 1
    while ops:
        apply()
    return vals[0]
''',
    tests=[["2+3*4", [1, 1, 2]], ["2+3*4", [2, 2, 1]], ["10-3+2", [2, 1, 3]], ["10-3+2", [1, 2, 3]], ["5*(2+3)", [1, 1, 2]], ["7", [1, 1, 1]],
           ["1000000000*1000000000", [1, 1, 1]], ["0-1", [4, 4, 4]], ["(((5)))", [0, 9, 3]], ["1-2-3-4", [1, 1, 1]], ["1-2-3-4", [1, 2, 1]],
           ["2*3+4*5-6", [3, 3, 3]], ["2*3+4*5-6", [1, 3, 2]], ["999999999+1*3", [5, 0, 5]]],
)
_r = rnd(5406)


def lit_leaf(r, hi):
    def leaf():
        return str(r.choice([r.randint(0, hi), r.randint(0, 9), r.randint(0, 10 ** 9)])), 0
    return leaf


def flat_chain(r, n, hi):
    return "".join(str(r.randint(0, hi)) + r.choice("+-*") for _ in range(n)) + str(r.randint(0, hi))


_P6 = {"+": 1, "-": 1, "*": 2}
p["tests"].append([to_infix(_r, rpn_walk(_r, 800, lit_leaf(_r, 10 ** 9), "+-*", None, [3, 3, 2], 0.5), _P6, (), 0.1), [2, 3, 1]])
p["tests"].append([flat_chain(_r, 900, 10 ** 9), [4, 4, 2]])
p["tests"].append([to_infix(_r, rpn_walk(_r, 700, lit_leaf(_r, 99), "+-*", None, [2, 2, 3], 0.25), {"+": 2, "-": 1, "*": 1}, (), 0.2), [2, 1, 1]])


def b_prio(expr, prio):
    pr = {"+": prio[0], "-": prio[1], "*": prio[2]}
    toks = [int(t) if t.isdigit() else t for t in re.findall(r"\d+|[-+*()]", expr)]

    def flat(seg):
        seg = seg[:]
        while len(seg) > 1:
            best = 1
            for k in range(1, len(seg), 2):
                if pr[seg[k]] > pr[seg[best]]:
                    best = k
            seg[best - 1:best + 2] = [arith(seg[best], seg[best - 1], seg[best + 1])]
        return seg[0]

    while "(" in toks:
        i = max(k for k, t in enumerate(toks) if t == "(")
        j = toks.index(")", i)
        toks[i:j + 1] = [flat(toks[i + 1:j])]
    return flat(toks) % MOD


def g_prio(r):
    toks = rpn_walk(r, r.randint(0, 6), lit_leaf(r, 12), "+-*", None, None, r.choice([0.3, 0.6]))
    return [to_infix(r, toks, _P6, (), 0.25), [r.randint(0, 3) for _ in range(3)]]


def v_prio(tests):
    for t in tests:
        s, pr = t["args"]
        assert 1 <= len(s) <= 10000 and len(pr) == 3 and all(0 <= x <= 9 for x in pr)
        assert re.fullmatch(r"[0-9+\-*()]+", s)
        balanced(s)
        for m in re.findall(r"\d+", s):
            assert int(m) <= 10 ** 9 and (m == "0" or m[0] != "0")
        assert 0 <= t["expected"] < MOD
    assert len({tuple(t["args"][1]) for t in tests}) >= 6


CHECKS["evaluate-with-custom-operator-priorities"] = (b_prio, g_prio, "exact")
VALIDATE["evaluate-with-custom-operator-priorities"] = v_prio

# ================================================================ 7. nested min / max / sum calls (Medium)

p = add(
    id="evaluate-nested-min-max-sum-calls", title="Evaluate Nested Function Calls", diff="Medium", topic=TOPIC, tier="common",
    fn="evaluateCalls", params=[("expr", "string")], ret="int", cmp="exact",
    desc="<p>The string <code>expr</code> is built from integer literals and calls of three functions: <code>min(...)</code>, <code>max(...)</code> and <code>sum(...)</code>. Every call has one or more arguments separated by commas, and each argument is either an integer literal or another call. A literal may be negative (<code>-5</code>). There are no spaces. The whole string is either one call or one literal.</p>"
         "<p><code>min</code> and <code>max</code> return the smallest and the largest of their arguments, <code>sum</code> returns their sum. Evaluate the expression and return its value.</p>"
         "<p>Example: <code>max(3,min(8,-2),sum(1,2,3))</code> evaluates the arguments to 3, -2 and 6, so the result is 6.</p>",
    constraints=["1 &le; expr.length &le; 10,000", "expr is valid: function names are exactly min, max or sum; every call has at least one argument", "Literals are integers without leading zeros and without a '+' sign, e.g. 0, 15, -7",
                 "Calls can be nested up to 2,000 levels deep", "Every literal and the result of every call (including partial sums) has absolute value at most 2<sup>31</sup> - 1"],
    hints=["A call can contain other calls, so the evaluation is naturally nested: finish the innermost call first.",
           "Keep a stack with one entry per call that has been opened but not yet closed. Each entry stores the function name and the list of argument values collected so far.",
           "On a name followed by <code>(</code> push <code>[name, []]</code>. On a number append it to the top entry's list. On <code>)</code> pop the top entry, reduce its list with the function, and append the result to the new top entry (or return it if the stack is empty). Do not forget that the whole expression may be just a number."],
    editorial=["Evaluating from the inside out is exactly what a stack does. Scan the string once. When a function name is read, skip the following <code>(</code> and push a frame holding the name and an empty list of argument values. Commas can simply be skipped, because numbers are recognised by their digits and sign.",
               "A number (optionally starting with <code>-</code>) is converted and appended to the argument list of the top frame; if there is no frame the whole expression is that number. On <code>)</code> the top frame is complete: apply <code>min</code>, <code>max</code> or <code>sum</code> to its list. If the stack is now empty this is the final answer, otherwise the result is appended to the argument list of the new top frame, exactly as if it had been written as a literal.",
               "Each character is read once and each value is stored in one list, so the time is O(n); the stack depth equals the nesting depth, which is why this approach also works for 2,000 levels where a recursive parser might hit the recursion limit."],
    time="O(n)", space="O(n)",
    solution='''def evaluateCalls(expr):
    stack = []
    i = 0
    n = len(expr)
    while i < n:
        c = expr[i]
        if c.isalpha():
            j = i
            while expr[j].isalpha():
                j += 1
            stack.append([expr[i:j], []])
            i = j + 1
        elif c == ',':
            i += 1
        elif c == ')':
            name, args = stack.pop()
            if name == "min":
                v = min(args)
            elif name == "max":
                v = max(args)
            else:
                v = sum(args)
            if not stack:
                return v
            stack[-1][1].append(v)
            i += 1
        else:
            j = i + 1
            while j < n and expr[j].isdigit():
                j += 1
            v = int(expr[i:j])
            if not stack:
                return v
            stack[-1][1].append(v)
            i = j
    return 0
''',
    tests=[["max(3,min(8,-2),sum(1,2,3))"], ["min(5)"], ["sum(7)"], ["-42"], ["0"], ["sum(1,sum(2,sum(3,sum(4,5))))"], ["max(min(1,2),min(3,4),min(5,6))"],
           ["min(max(-5,-9),sum(-3,-4))"], ["sum(2147483647,-2147483647)"], ["max(2147483647,-2147483647)"], ["sum(-1,-2,-3,max(-10,-20),min(0,0,0))"],
           ["min(sum(100,200),max(150,sum(50,50,50)),300)"]],
)


def gen_call(r, depth, budget, litmax):
    """Random expression text and its value. budget is a one-element list: how many calls may still be created."""
    if depth <= 0 or budget[0] <= 0 or r.random() < 0.15:
        v = r.randint(-litmax, litmax)
        return str(v), v
    budget[0] -= 1
    name = r.choice(["min", "max", "sum"])
    k = r.randint(1, 5)
    parts, vals = [], []
    for _ in range(k):
        if r.random() < 0.45:
            s, v = gen_call(r, depth - 1, budget, litmax)
        else:
            v = r.randint(-litmax, litmax)
            s = str(v)
        parts.append(s)
        vals.append(v)
    if name == "sum" and abs(sum(vals)) > LIM:
        name = r.choice(["min", "max"])
    res = min(vals) if name == "min" else max(vals) if name == "max" else sum(vals)
    return name + "(" + ",".join(parts) + ")", res


_r = rnd(5407)
for _lit, _calls in ((1000, 600), (10 ** 9, 450)):
    while True:
        _s, _v = gen_call(_r, 25, [_calls], _lit)
        if _s[0].isalpha() and 4000 < len(_s) < 9800:
            break
    p["tests"].append([_s])
p["tests"].append(["max(1," * 1000 + "5" + ",2)" * 1000])
p["tests"].append(["sum(" * 1200 + "1" + ",1)" * 1200])


def b_calls(expr):
    env = {"mn": lambda *a: min(a), "mx": lambda *a: max(a), "sm": lambda *a: sum(a)}
    e = expr.replace("min(", "mn(").replace("max(", "mx(").replace("sum(", "sm(")
    return eval(e, {"__builtins__": {}}, env)


def g_calls(r):
    while True:
        s, v = gen_call(r, 4, [r.randint(1, 6)], r.choice([3, 20]))
        if len(s) < 120:
            return [s]


def v_calls(tests):
    for t in tests:
        s = t["args"][0]
        assert 1 <= len(s) <= 10000
        assert re.fullmatch(r"(?:(?:min|max|sum)\(|-?(?:0|[1-9][0-9]*)|,|\))+", s)
        st = []
        depth_max = 0
        for m in re.finditer(r"(min|max|sum)\(|(-?(?:0|[1-9][0-9]*))|(,)|(\))", s):
            if m.group(1):
                st.append([m.group(1), []])
                depth_max = max(depth_max, len(st))
            elif m.group(2) is not None:
                v = int(m.group(2))
                assert abs(v) <= LIM
                if st:
                    st[-1][1].append(v)
                else:
                    assert m.end() == len(s)
                    res = v
            elif m.group(4):
                name, args = st.pop()
                assert args
                v = min(args) if name == "min" else max(args) if name == "max" else sum(args)
                assert abs(v) <= LIM, "intermediate overflow"
                if st:
                    st[-1][1].append(v)
                else:
                    res = v
        assert not st and depth_max <= 2000
        assert res == t["expected"]
    assert any(len(t["args"][0]) > 3000 for t in tests)


CHECKS["evaluate-nested-min-max-sum-calls"] = (b_calls, g_calls, "exact")
VALIDATE["evaluate-nested-min-max-sum-calls"] = v_calls

# ================================================================ 8. boolean expression with precedence (Medium)

PREC8 = {"|": 1, "^": 2, "&": 3}


class _B:
    def __init__(self, v):
        self.v = v

    def __and__(self, o):
        return _B(self.v and o.v)

    def __or__(self, o):
        return _B(self.v or o.v)

    def __xor__(self, o):
        return _B(self.v != o.v)

    def __invert__(self):
        return _B(not self.v)


p = add(
    id="evaluate-boolean-expression-precedence", title="Evaluate a Boolean Expression", diff="Medium", topic=TOPIC, tier="extra",
    fn="evaluateBoolean", params=[("expr", "string")], ret="bool", cmp="exact",
    desc="<p>The string <code>expr</code> is a boolean expression without spaces. It uses the constants <code>t</code> (true) and <code>f</code> (false), the unary operator <code>!</code> (not), the binary operators <code>&amp;</code> (and), <code>^</code> (exclusive or) and <code>|</code> (or), and round brackets.</p>"
         "<p>Priorities from highest to lowest: <code>!</code>, then <code>&amp;</code>, then <code>^</code>, then <code>|</code>. Binary operators of equal priority are applied from left to right. <code>!</code> applies to the single operand right after it, which may be a constant, a bracketed expression or another <code>!</code> (<code>!!t</code> is true). Brackets override priorities.</p>"
         "<p>Return the value of the expression.</p>"
         "<p>Examples: <code>t|f&amp;f</code> is <code>t | (f &amp; f)</code>, so true. <code>!(t|t)</code> is false. <code>t^t^t</code> is <code>(t ^ t) ^ t</code>, so true.</p>",
    constraints=["1 &le; expr.length &le; 10,000", "expr contains only the characters t, f, !, &amp;, ^, |, ( and ) and is a valid expression", "Brackets are balanced and can be nested deeply (up to 3,000 levels)"],
    hints=["It is the same problem as evaluating an arithmetic expression with priorities, just with booleans. Use two stacks: one for values and one for operators.",
           "Give each operator a priority (<code>|</code>=1, <code>^</code>=2, <code>&amp;</code>=3, <code>!</code>=4). Before pushing a binary operator, apply the stacked operators with priority greater than or equal to it.",
           "<code>!</code> is a prefix operator: push it without popping anything, and apply it later (when a binary operator with lower priority arrives, when a bracket closes, or at the end). Closing a bracket applies operators down to the matching <code>(</code>; a <code>!</code> in front of the bracket stays on the stack and is applied afterwards."],
    editorial=["Use the shunting-yard method with a value stack and an operator stack. <code>t</code> and <code>f</code> push <code>True</code> or <code>False</code>. <code>(</code> and <code>!</code> are pushed directly: a prefix operator has no left operand, so it cannot trigger any application of operators on the stack.",
               "For a binary operator <code>c</code> pop and apply the operators on top while the top is not <code>(</code> and has a priority at least that of <code>c</code>; then push <code>c</code>. Applying a binary operator pops two values, applying <code>!</code> pops one. A <code>)</code> applies operators until it reaches the matching <code>(</code>. At the end apply whatever is left; the value stack then holds the answer.",
               "A <code>!</code> that is directly in front of a bracket sits below the <code>(</code> on the operator stack, so it is applied after the bracket's content has been reduced to one value, which is exactly right. Time and space are O(n)."],
    time="O(n)", space="O(n)",
    solution='''def evaluateBoolean(expr):
    prec = {'|': 1, '^': 2, '&': 3, '!': 4}
    vals = []
    ops = []

    def apply():
        op = ops.pop()
        if op == '!':
            vals.append(not vals.pop())
        else:
            b = vals.pop()
            a = vals.pop()
            if op == '|':
                vals.append(a or b)
            elif op == '^':
                vals.append(a != b)
            else:
                vals.append(a and b)

    for c in expr:
        if c == 't' or c == 'f':
            vals.append(c == 't')
        elif c == '(' or c == '!':
            ops.append(c)
        elif c == ')':
            while ops[-1] != '(':
                apply()
            ops.pop()
        else:
            while ops and ops[-1] != '(' and prec[ops[-1]] >= prec[c]:
                apply()
            ops.append(c)
    while ops:
        apply()
    return vals[0]
''',
    tests=[["t"], ["f"], ["!t"], ["!!f"], ["t|f&f"], ["(t|f)&f"], ["!t|t"], ["!(t|t)"], ["t^t^t"], ["f|t^t&t"], ["!f&!t"], ["t^f|f&t^t"], ["!(f^t)&(t|!t)"], ["((((f))))"]],
)
_r = rnd(5408)


def bool_leaf(r):
    def leaf():
        return r.choice("tf"), 0
    return leaf


p["tests"].append([to_infix(_r, rpn_walk(_r, 2000, bool_leaf(_r), "&^|", None, None, 0.5), PREC8, (), 0.1, "!", 0.15)])
p["tests"].append([to_infix(_r, rpn_walk(_r, 1800, bool_leaf(_r), "&^|", None, [1, 1, 3], 0.2), PREC8, (), 0.25, "!", 0.25)])
p["tests"].append(["!(" * 2900 + "t^f" + ")" * 2900])


def b_bool(expr):
    return bool(eval(expr.replace("!", "~"), {"__builtins__": {}}, {"t": _B(True), "f": _B(False)}).v)


def g_bool(r):
    toks = rpn_walk(r, r.randint(0, 6), bool_leaf(r), "&^|", None, None, r.choice([0.3, 0.6]))
    return [to_infix(r, toks, PREC8, (), 0.2, "!", 0.25)]


def v_bool(tests):
    for t in tests:
        s = t["args"][0]
        assert 1 <= len(s) <= 10000
        assert re.fullmatch(r"[tf!&^|()]+", s)
        balanced(s)
    assert any(t["expected"] for t in tests) and any(not t["expected"] for t in tests)


CHECKS["evaluate-boolean-expression-precedence"] = (b_bool, g_bool, "exact")
VALIDATE["evaluate-boolean-expression-precedence"] = v_bool

# ================================================================ 9. postfix to minimal-bracket infix (Medium)

p = add(
    id="postfix-to-minimal-bracket-infix", title="Postfix to Infix With Fewest Brackets", diff="Medium", topic=TOPIC, tier="extra",
    fn="toMinimalInfix", params=[("post", "string")], ret="string", cmp="exact",
    desc="<p>The string <code>post</code> is a valid postfix expression: single lowercase letters are operands and <code>+</code>, <code>-</code>, <code>*</code>, <code>/</code>, <code>^</code> are binary operators, each written after its two operands (for example <code>ab+c*</code>).</p>"
         "<p>Write the expression in ordinary infix notation using as few round brackets as possible, such that reading the result back with the usual rules gives exactly the same operation tree. The usual rules: <code>+</code> and <code>-</code> have the lowest priority, <code>*</code> and <code>/</code> the middle one, <code>^</code> the highest. Equal priorities are applied from left to right, except <code>^</code> which is applied from right to left. The answer is unique.</p>"
         "<p>Examples: <code>ab+c*</code> gives <code>(a+b)*c</code>; <code>abc*+</code> gives <code>a+b*c</code>; <code>abc-+</code> gives <code>a+(b-c)</code> (the brackets are needed, because <code>a+b-c</code> would be <code>(a+b)-c</code>); <code>abc^^</code> gives <code>a^b^c</code> while <code>ab^c^</code> gives <code>(a^b)^c</code>.</p>",
    constraints=["1 &le; post.length &le; 5,000", "post contains only lowercase letters and the characters + - * / ^ and is a valid postfix expression"],
    hints=["Build the infix text bottom-up. When an operator is applied to two sub-expressions, you have to decide for each of them whether it needs brackets.",
           "Keep a stack of pairs (text, priority of its outermost operator). A single letter counts as having a priority higher than every operator, so it never needs brackets.",
           "A left operand needs brackets if its priority is lower than the operator's, or equal when the operator is <code>^</code> (right-associative). A right operand needs brackets if its priority is lower, or equal when the operator is not <code>^</code>. Join the texts, and store the operator's priority with the result."],
    editorial=["Process the postfix string with a stack of finished sub-expressions; each entry keeps its infix text and the priority of its top-level operator (letters get a priority above all operators). An operand is pushed as is. For an operator <code>op</code> pop the right operand <code>b</code> and the left operand <code>a</code> and decide where brackets are unavoidable.",
               "A bracket is necessary exactly when removing it would change the parse. A child with a lower priority than <code>op</code> would be split by <code>op</code>, so it needs brackets on either side. A child with the same priority needs brackets when it sits on the side against which <code>op</code> groups: for left-associative operators the <em>right</em> operand (<code>a-(b-c)</code>, <code>a/(b*c)</code>), for the right-associative <code>^</code> the <em>left</em> operand (<code>(a^b)^c</code>). A child with a higher priority never needs brackets. Because each bracket is added only when necessary, the count is minimal and the output is unique.",
               "Push <code>(a op b, priority(op))</code>. At the end the stack holds the answer. Time O(n) for the stack work plus the cost of building strings (at most O(n) per concatenation, fine for n = 5,000)."],
    time="O(n)", space="O(n)",
    solution='''def toMinimalInfix(post):
    prec = {'+': 1, '-': 1, '*': 2, '/': 2, '^': 3}
    stack = []
    for c in post:
        if c in prec:
            bs, bp = stack.pop()
            as_, ap = stack.pop()
            p = prec[c]
            right_assoc = (c == '^')
            if ap < p or (ap == p and right_assoc):
                as_ = "(" + as_ + ")"
            if bp < p or (bp == p and not right_assoc):
                bs = "(" + bs + ")"
            stack.append((as_ + c + bs, p))
        else:
            stack.append((c, 99))
    return stack[0][0]
''',
    tests=[["ab+c*"], ["abc*+"], ["abc-+"], ["abc^^"], ["ab^c^"], ["a"], ["ab-c-"], ["abc--"], ["abc/*"], ["ab*c/"], ["ab+cd+*"], ["abcd^^^"],
           ["ab+cd-*ef/g^-"]],
)
_r = rnd(5409)


def letter_leaf(r):
    def leaf():
        return r.choice("abcdefghijklmnopqrstuvwxyz"), 0
    return leaf


def postfix_str(toks):
    return "".join(x for _, x in toks)


p["tests"].append([postfix_str(rpn_walk(_r, 2400, letter_leaf(_r), "+-*/^", None, [3, 3, 3, 3, 2], 0.5))])
p["tests"].append([postfix_str(rpn_walk(_r, 2000, letter_leaf(_r), "+-*/^", None, [1, 1, 2, 2, 3], 0.15))])
p["tests"].append(["a" + "b-" * 2499])
p["tests"].append(["a" * 2500 + "-" * 2499])


def b_minimal(post):
    st = []
    for c in post:
        if c in PREC5:
            b = st.pop()
            a = st.pop()
            st.append((c, a, b))
        else:
            st.append(c)
    tree = st[0]
    count = [0]

    def internals(t):
        if isinstance(t, str):
            return 0
        return 1 + internals(t[1]) + internals(t[2])
    m = max(0, internals(tree) - 1)  # the root never gets brackets

    def emit(t, mask, top=True):
        if isinstance(t, str):
            return t
        idx = count[0]
        count[0] += 1
        s = emit(t[1], mask, False) + t[0] + emit(t[2], mask, False)
        if not top and (mask >> (idx - 1)) & 1:
            s = "(" + s + ")"
        return s

    best = None
    for mask in range(1 << m):
        count[0] = 0
        s = emit(tree, mask)
        if parse_tree(s, PREC5, ("^",)) != tree:
            continue
        k = bin(mask).count("1")
        if best is None or k < best[0]:
            best = (k, {s})
        elif k == best[0]:
            best[1].add(s)
    assert len(best[1]) == 1
    return next(iter(best[1]))


def g_minimal(r):
    return [postfix_str(rpn_walk(r, r.randint(0, 5), letter_leaf(r), "+-*/^", None, None, r.choice([0.3, 0.6])))]


def v_minimal(tests):
    for t in tests:
        s = t["args"][0]
        assert 1 <= len(s) <= 5000
        assert re.fullmatch(r"[a-z+\-*/^]+", s)
        assert sum(c in PREC5 for c in s) * 2 + 1 == len(s)
        d = 0
        for c in s:
            d += -1 if c in PREC5 else 1
            assert d >= 1
        assert d == 1
        out = t["expected"]
        balanced(out)
        assert [c for c in out if c not in "()"] != [] and sorted(c for c in out if c.isalpha()) == sorted(c for c in s if c.isalpha())


CHECKS["postfix-to-minimal-bracket-infix"] = (b_minimal, g_minimal, "exact")
VALIDATE["postfix-to-minimal-bracket-infix"] = v_minimal

# ================================================================ 10. count redundant bracket pairs (Hard)

PREC10 = {"+": 1, "-": 1, "*": 2, "/": 2}

p = add(
    id="count-redundant-bracket-pairs", title="Count Redundant Bracket Pairs", diff="Hard", topic=TOPIC, tier="extra",
    fn="countRedundantBrackets", params=[("s", "string")], ret="int", cmp="exact",
    desc="<p>The string <code>s</code> is a valid infix expression: single lowercase letters are operands, <code>+</code>, <code>-</code>, <code>*</code>, <code>/</code> are binary operators (<code>*</code> and <code>/</code> bind tighter than <code>+</code> and <code>-</code>, and operators of equal priority are applied from left to right), and round brackets group sub-expressions. There are no unary operators and no spaces.</p>"
         "<p>A pair of matching brackets is <em>redundant</em> if deleting just this one pair (leaving all other characters unchanged) gives an expression that is read in exactly the same way, i.e. with the same operation tree. For example in <code>(a+b)+c</code> the brackets are redundant because <code>a+b+c</code> is also read as <code>(a+b)+c</code>, but in <code>a+(b+c)</code> they are not. Brackets around a single letter or around another bracket pair are redundant too.</p>"
         "<p>Return the number of redundant bracket pairs. Each pair is judged on its own.</p>"
         "<p>Examples: <code>((a+b))</code> has 2, <code>(a*b)+c</code> has 1, <code>(a+b)*c</code> has 0, <code>(a/b)*(c/d)</code> has 1 (only the first pair).</p>",
    constraints=["1 &le; s.length &le; 10,000", "s contains lowercase letters, + - * / and round brackets, and is a valid expression", "Brackets can be nested up to 4,000 levels deep"],
    hints=["Look at one bracket pair at a time. What decides whether the brackets matter is the operator just outside on the left, the operator just outside on the right, and the operators directly inside (not inside deeper brackets).",
           "Use a stack of open brackets and, for each open bracket, remember the lowest priority among the operators that appear directly at its own level. If there is no such operator, the pair only wraps a single operand or another pair.",
           "Let <code>m</code> be that lowest inner priority, <code>L</code> the operator right before the <code>(</code> (none if there is none or the previous character is another <code>(</code>) and <code>R</code> the operator right after the <code>)</code> (none if absent or the next character is <code>)</code>). The pair is redundant if there is no inner operator, or <code>prio(L) &lt; m</code> (or no <code>L</code>) and <code>prio(R) &lt;= m</code> (or no <code>R</code>)."],
    editorial=["Removing a pair changes the reading only if one of the neighbouring operators would now grab part of the bracket's content. Only the operators at the top level of the pair matter, because deeper ones stay protected by their own brackets, and among those only the one with the lowest priority <code>m</code> (those bind loosest and are the most exposed).",
               "On the left side, an operator <code>L</code> in front of the pair would swallow the first operand of the contents if <code>prio(L) &gt;= m</code> (equal priority is also a problem: <code>a-(b-c)</code> would turn into <code>(a-b)-c</code>). So we need <code>prio(L) &lt; m</code>. On the right side, an operator <code>R</code> would steal the last operand if <code>prio(R) &gt; m</code>; for <code>prio(R) == m</code> everything is left-associative, so <code>(a-b)-c</code> and <code>a-b-c</code> mean the same, and equal priority is fine. A neighbour that is a bracket or the string boundary (the next outer pair protects us) cannot interfere. A pair with no top-level operator is always redundant.",
               "Scan once with a stack. On <code>(</code> push the position and a minimum initialised to infinity. On an operator update the minimum of the top frame (operators outside every bracket are ignored). On <code>)</code> pop the frame, look at the characters right before the open bracket and right after this close bracket, and apply the rule. Time O(n), space O(n)."],
    time="O(n)", space="O(n)",
    solution='''def countRedundantBrackets(s):
    prec = {'+': 1, '-': 1, '*': 2, '/': 2}
    INF = 99
    stack = []          # [position of '(', lowest priority of operators directly inside]
    count = 0
    n = len(s)
    for i, c in enumerate(s):
        if c == '(':
            stack.append([i, INF])
        elif c in prec:
            if stack and prec[c] < stack[-1][1]:
                stack[-1][1] = prec[c]
        elif c == ')':
            start, m = stack.pop()
            left = prec.get(s[start - 1]) if start > 0 else None
            right = prec.get(s[i + 1]) if i + 1 < n else None
            if m == INF:
                count += 1
            elif (left is None or left < m) and (right is None or right <= m):
                count += 1
    return count
''',
    tests=[["a+b"], ["(a)"], ["((a+b))"], ["(a+b)*c"], ["(a*b)+c"], ["a-(b-c)"], ["(a-b)-c"], ["a+(b+c)"], ["(a/b)*(c/d)"], ["a"],
           ["a*(b+c)*d"], ["((a*b)+(c/d))-(e)"], ["(a+(b*c))+((d))"]],
)
_r = rnd(5410)
p["tests"].append([to_infix(_r, rpn_walk(_r, 2300, letter_leaf(_r), "+-*/", None, None, 0.5), PREC10, (), 0.3)])
p["tests"].append([to_infix(_r, rpn_walk(_r, 2000, letter_leaf(_r), "+-*/", None, [3, 1, 3, 1], 0.2), PREC10, (), 0.5)])
p["tests"].append(["(" * 3000 + "a+b" + ")" * 3000])
p["tests"].append(["".join("a" + "+(" if k % 2 == 0 else "b*(" for k in range(2000)) + "c" + ")" * 2000])


def b_redundant(s):
    base = parse_tree(s, PREC10)
    stack = []
    pairs = []
    for i, c in enumerate(s):
        if c == "(":
            stack.append(i)
        elif c == ")":
            pairs.append((stack.pop(), i))
    cnt = 0
    for i, j in pairs:
        t = s[:i] + s[i + 1:j] + s[j + 1:]
        if parse_tree(t, PREC10) == base:
            cnt += 1
    return cnt


def g_redundant(r):
    toks = rpn_walk(r, r.randint(0, 6), letter_leaf(r), "+-*/", None, None, r.choice([0.3, 0.6]))
    return [to_infix(r, toks, PREC10, (), r.choice([0.2, 0.4]))]


def v_redundant(tests):
    for t in tests:
        s = t["args"][0]
        assert 1 <= len(s) <= 10000
        assert re.fullmatch(r"[a-z+\-*/()]+", s)
        balanced(s)
        d = m = 0
        for c in s:
            d += (c == "(") - (c == ")")
            m = max(m, d)
        assert m <= 4000
    assert len({t["expected"] for t in tests}) >= 8


CHECKS["count-redundant-bracket-pairs"] = (b_redundant, g_redundant, "exact")
VALIDATE["count-redundant-bracket-pairs"] = v_redundant

# ================================================================ 11. expand polynomial expression (Hard)

p = add(
    id="expand-polynomial-expression-mod", title="Expand a Polynomial Expression", diff="Hard", topic=TOPIC, tier="extra",
    fn="expandPolynomial", params=[("expr", "string")], ret="int[]", cmp="exact",
    desc="<p>The string <code>expr</code> is an arithmetic expression in one variable <code>x</code>, without spaces. It is built from the variable <code>x</code>, non-negative integer literals, the binary operators <code>+</code>, <code>-</code>, <code>*</code> and round brackets. Priorities are the usual ones (<code>*</code> before <code>+</code> and <code>-</code>, equal priorities left to right). A minus sign may also be used as a <em>unary</em> operator, but only at the very start of the expression or directly after an opening bracket (for example <code>-x*x+3</code> or <code>2*(-x+3)</code>); it negates the single term that follows it.</p>"
         "<p>Multiplying out all brackets turns the expression into a polynomial <code>c<sub>0</sub> + c<sub>1</sub>x + c<sub>2</sub>x<sup>2</sup> + ...</code>. Return its coefficients as an array <code>[c<sub>0</sub>, c<sub>1</sub>, ...]</code>, each reduced modulo <code>1,000,000,007</code> to the range <code>0..1,000,000,006</code> (so -1 becomes 1000000006). Drop zero coefficients at the high end; the zero polynomial is returned as <code>[0]</code>.</p>"
         "<p>Examples: <code>(x+1)*(x+1)</code> gives <code>[1, 2, 1]</code>. <code>(x-1)*(x+1)</code> gives <code>[1000000006, 0, 1]</code> (that is x<sup>2</sup> - 1). <code>x-x</code> gives <code>[0]</code>.</p>",
    constraints=["1 &le; expr.length &le; 2,000", "expr contains only x, digits, + - *, ( and ) and is valid as described; literals are in [0, 10<sup>9</sup>] without leading zeros (except \"0\")", "Brackets can be nested up to 500 levels deep", "The answer has at most 1,000 coefficients"],
    hints=["Represent every sub-expression by the list of its coefficients, so that an expression is just a value of a new kind. Addition and subtraction are element-wise, multiplication is a convolution.",
           "Evaluate the expression like an ordinary calculator, with a stack of values (polynomials) and a stack of operators, but let the 'numbers' be coefficient lists: <code>x</code> is <code>[0, 1]</code> and the literal <code>5</code> is <code>[5]</code>.",
           "Treat a unary minus as <code>0 - term</code>: when a <code>-</code> appears at the start or right after <code>(</code>, push the value <code>[0]</code> first. Reduce all coefficients modulo 10<sup>9</sup>+7 after each operation and strip high-end zeros only at the very end."],
    editorial=["The expression grammar does not care what the values are, only that +, - and * exist on them. Polynomials form a ring, so the usual shunting-yard evaluation works if each operand is a coefficient list: the variable <code>x</code> is <code>[0, 1]</code>, a literal <code>k</code> is <code>[k mod p]</code>.",
               "Addition and subtraction combine the lists position by position (padding the shorter one with zeros). Multiplication convolves: <code>res[i + j] += a[i] * b[j]</code>. A unary minus is handled by pushing the constant polynomial <code>[0]</code> before the minus, so it becomes the binary <code>0 - term</code> with the correct priority (<code>-x*x</code> is <code>0 - (x*x)</code>). The stacks make the evaluation iterative, so nesting depth is no problem.",
               "The cost of a multiplication is the product of the two lengths. Since the lengths of the operands add up to at most the number of <code>x</code> in the expression, all the multiplications together cost at most O(m<sup>2</sup>) where m is the number of <code>x</code> characters (at most about 1,000 here); additions cost O(length) each. Skipping zero coefficients in the inner loop makes sparse cases even faster."],
    time="O(n * m)", space="O(m)",
    solution='''def expandPolynomial(expr):
    MOD = 10 ** 9 + 7
    prec = {'+': 1, '-': 1, '*': 2}
    vals = []
    ops = []

    def apply():
        op = ops.pop()
        b = vals.pop()
        a = vals.pop()
        if op == '*':
            res = [0] * (len(a) + len(b) - 1)
            for i, x in enumerate(a):
                if x:
                    for j, y in enumerate(b):
                        res[i + j] = (res[i + j] + x * y) % MOD
        else:
            sign = 1 if op == '+' else -1
            res = [0] * max(len(a), len(b))
            for i, x in enumerate(a):
                res[i] = x
            for i, y in enumerate(b):
                res[i] = (res[i] + sign * y) % MOD
        vals.append(res)

    i = 0
    n = len(expr)
    expect_operand = True
    while i < n:
        c = expr[i]
        if c.isdigit():
            j = i
            while j < n and expr[j].isdigit():
                j += 1
            vals.append([int(expr[i:j]) % MOD])
            i = j
            expect_operand = False
            continue
        if c == 'x':
            vals.append([0, 1])
            expect_operand = False
        elif c == '(':
            ops.append(c)
            expect_operand = True
        elif c == ')':
            while ops[-1] != '(':
                apply()
            ops.pop()
            expect_operand = False
        else:
            if expect_operand:      # unary minus: 0 - term
                vals.append([0])
            while ops and ops[-1] != '(' and prec[ops[-1]] >= prec[c]:
                apply()
            ops.append(c)
            expect_operand = True
        i += 1
    while ops:
        apply()
    res = vals[0]
    while len(res) > 1 and res[-1] == 0:
        res.pop()
    return res
''',
    tests=[["x"], ["5"], ["x-x"], ["(x+1)*(x+1)"], ["(x-1)*(x+1)"], ["-x*x+3"], ["2*(-x+3)"], ["(x+1)*(x+1)*(x+1)"], ["0*x*x"], ["1000000000*x+7"],
           ["x*(x*(x*(x+1)+2)+3)+4"], ["-(x+2)*(x-2)"], ["(x-1)*(x-2)*(x-3)-x*x*x"]],
)
_r = rnd(5411)


def poly_leaf(r, hi):
    def leaf():
        if r.random() < 0.45:
            return "x", 0
        return str(r.choice([r.randint(0, hi), r.randint(0, 9)])), 0
    return leaf


_P11 = {"+": 1, "-": 1, "*": 2}


def add_unary_minus(r, s, q):
    out = []
    for c in s:
        out.append(c)
        if c == "(" and r.random() < q:
            out.append("-")
    s = "".join(out)
    return "-" + s if r.random() < q else s


def gen_poly(r, n_ops, hi, weights, p_op, extra, q):
    return add_unary_minus(r, to_infix(r, rpn_walk(r, n_ops, poly_leaf(r, hi), "+-*", None, weights, p_op), _P11, (), extra), q)


while True:
    _s = gen_poly(_r, 230, 10 ** 9, [3, 3, 2], 0.5, 0.1, 0.3)
    if len(_s) <= 1900:
        break
p["tests"].append([_s])
p["tests"].append(["*".join("(x%s%d)" % (_r.choice("+-"), _r.randint(0, 999)) for _ in range(200))])
while True:
    _s = gen_poly(_r, 280, 999, [4, 4, 1], 0.2, 0.2, 0.2)
    if len(_s) <= 1900:
        break
p["tests"].append([_s])


class _Poly:
    def __init__(self, c):
        self.c = list(c)

    @staticmethod
    def of(o):
        return o if isinstance(o, _Poly) else _Poly([o])

    def __add__(self, o):
        o = _Poly.of(o)
        n = max(len(self.c), len(o.c))
        a = self.c + [0] * (n - len(self.c))
        b = o.c + [0] * (n - len(o.c))
        return _Poly([x + y for x, y in zip(a, b)])

    __radd__ = __add__

    def __neg__(self):
        return _Poly([-x for x in self.c])

    def __sub__(self, o):
        return self + (-_Poly.of(o))

    def __rsub__(self, o):
        return _Poly.of(o) - self

    def __mul__(self, o):
        o = _Poly.of(o)
        res = [0] * (len(self.c) + len(o.c) - 1)
        for i, x in enumerate(self.c):
            for j, y in enumerate(o.c):
                res[i + j] += x * y
        return _Poly(res)

    __rmul__ = __mul__


def b_poly(expr):
    v = _Poly.of(eval(expr, {"__builtins__": {}}, {"x": _Poly([0, 1])}))
    res = [c % MOD for c in v.c]
    while len(res) > 1 and res[-1] == 0:
        res.pop()
    return res


def g_poly(r):
    return [gen_poly(r, r.randint(0, 6), r.choice([5, 30]), None, r.choice([0.3, 0.6]), 0.2, 0.25)]


def v_poly(tests):
    for t in tests:
        s = t["args"][0]
        assert 1 <= len(s) <= 2000
        assert re.fullmatch(r"[0-9x+\-*()]+", s)
        balanced(s)
        for m in re.findall(r"\d+", s):
            assert int(m) <= 10 ** 9 and (m == "0" or m[0] != "0")
        # unary minus only at the start or right after '('
        for k, c in enumerate(s):
            if c in "+-*":
                assert k > 0 or c == "-"
                assert k == 0 or s[k - 1] not in "+-*", "adjacent operators"
                if k > 0 and s[k - 1] == "(":
                    assert c == "-"
        assert len(t["expected"]) <= 1000
        assert all(0 <= c < MOD for c in t["expected"])
        assert t["expected"][-1] != 0 or t["expected"] == [0]


CHECKS["expand-polynomial-expression-mod"] = (b_poly, g_poly, "exact")
VALIDATE["expand-polynomial-expression-mod"] = v_poly
