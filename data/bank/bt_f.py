"""Problems: backtracking, number and string generation (parentheses, keypad words, digit strings, expressions)."""
from itertools import product as _product, permutations as _perms  # noqa: F401

from lib import add, rnd, CHECKS, VALIDATE, gen_arr  # noqa: F401

TOPIC = "Backtracking"
INT_MAX = 2 ** 31 - 1

KEYS = {"2": "abc", "3": "def", "4": "ghi", "5": "jkl", "6": "mno", "7": "pqrs", "8": "tuv", "9": "wxyz"}


# ================================================================== EASY

# ---------------------------------------------------------------- binary strings without two adjacent ones
add(
    id="binary-strings-no-adjacent-ones", title="Binary Strings Without Adjacent Ones", diff="Easy", topic=TOPIC,
    fn="noAdjacentOnes", params=[("n", "int")], ret="int[][]", cmp="rowset",
    desc="<p>Return every binary string of length <code>n</code> in which no two <code>1</code> characters are next to each other. Each string is returned as a row of <code>n</code> integers, each <code>0</code> or <code>1</code>.</p><p>For <code>n = 3</code> the answer has 5 rows: <code>[0,0,0]</code>, <code>[0,0,1]</code>, <code>[0,1,0]</code>, <code>[1,0,0]</code> and <code>[1,0,1]</code>. Rows may be returned in any order.</p>",
    constraints=["1 &le; n &le; 10"],
    hints=["Build a row one position at a time. At each position you choose <code>0</code> or <code>1</code>.",
           "Writing a <code>0</code> is always safe. Writing a <code>1</code> is safe only if the previous value is not a <code>1</code>.",
           "Pass the previous value (or a flag) down the recursion and only ever extend rows that are already valid, so that nothing needs to be filtered at the end."],
    editorial=["Use depth-first search over positions. At position <code>i</code> you may always place a <code>0</code>; you may place a <code>1</code> only when the last placed value is <code>0</code> (or when <code>i = 0</code>). Because every partial row is valid by construction, each complete row of length <code>n</code> is a valid answer and is produced exactly once.",
               "The number of answers follows the Fibonacci numbers (2, 3, 5, 8, 13, ... for n = 1, 2, 3, ...), so the search does work proportional to the output size. Generating all 2<sup>n</sup> rows and filtering would also pass for n &le; 10 but wastes effort on rows that are doomed early."],
    time="O(n * F(n)) where F(n) is about 1.62<sup>n</sup>", space="O(n) recursion",
    solution='''def noAdjacentOnes(n):
    res = []
    row = []

    def go(prev):
        if len(row) == n:
            res.append(row[:])
            return
        row.append(0)
        go(0)
        row.pop()
        if prev == 0:
            row.append(1)
            go(1)
            row.pop()

    go(0)
    return res
''',
    tests=[[1], [2], [3], [4], [5], [6], [7], [8], [9], [10]],
)


def b_noadj(n):
    return [list(t) for t in _product((0, 1), repeat=n) if all(not (t[i] and t[i + 1]) for i in range(n - 1))]


def v_noadj(tests):
    fib = {1: 2, 2: 3}
    for i in range(3, 11):
        fib[i] = fib[i - 1] + fib[i - 2]
    for t in tests:
        n = t["args"][0]
        assert 1 <= n <= 10
        assert len(t["expected"]) == fib[n]


CHECKS["binary-strings-no-adjacent-ones"] = (b_noadj, lambda r: [r.randint(1, 9)], "rowset")
VALIDATE["binary-strings-no-adjacent-ones"] = v_noadj


# ---------------------------------------------------------------- k-th keypad word
add(
    id="kth-keypad-word", title="K-th Keypad Word", diff="Easy", topic=TOPIC, tier="extra",
    fn="kthKeypadWord", params=[("digits", "string"), ("k", "int")], ret="string", cmp="exact",
    desc="<p>On an old phone keypad each digit from <code>2</code> to <code>9</code> carries letters: <code>2</code>: abc, <code>3</code>: def, <code>4</code>: ghi, <code>5</code>: jkl, <code>6</code>: mno, <code>7</code>: pqrs, <code>8</code>: tuv, <code>9</code>: wxyz.</p><p>Pressing each digit of <code>digits</code> once and choosing one of its letters gives a word. List all such words in alphabetical order and return the <code>k</code>-th one (counting from 1).</p><p>Example: for <code>digits = \"23\"</code> the words are ad, ae, af, bd, be, bf, cd, ce, cf, so <code>k = 5</code> gives <code>\"be\"</code>.</p>",
    constraints=["1 &le; digits.length &le; 8", "digits contains only the characters 2-9", "1 &le; k &le; the number of possible words"],
    hints=["Generating all words and picking the k-th works because there are at most 4<sup>8</sup> = 65,536 of them. Can you jump straight to the answer?",
           "Because the letters of every key are in alphabetical order, the words appear in the same order as the numbers written in a mixed-radix system, where digit <code>d</code> has as many symbols as it has letters.",
           "Subtract 1 from <code>k</code> and peel off letters from the right: <code>k % len(letters)</code> is the letter index of the last key, then divide <code>k</code> by that length and continue with the previous key."],
    editorial=["Alphabetical order of the words is the same as odometer order: the last key changes fastest. So the (k-1)-th word, with counting from 0, is simply the representation of k-1 in a number system whose position values are the letter counts of the keys (3, 4, ...).",
               "Take the last key, split off <code>k % len(letters)</code> as its letter and replace <code>k</code> by <code>k // len(letters)</code>; repeat for the previous keys. This costs O(n) instead of enumerating up to 4<sup>n</sup> words, which is the same idea as 'jumping over' whole subtrees of a backtracking tree."],
    time="O(n)", space="O(n)",
    solution='''def kthKeypadWord(digits, k):
    keys = {"2": "abc", "3": "def", "4": "ghi", "5": "jkl", "6": "mno", "7": "pqrs", "8": "tuv", "9": "wxyz"}
    k -= 1
    out = []
    for d in reversed(digits):
        letters = keys[d]
        k, idx = divmod(k, len(letters))
        out.append(letters[idx])
    return "".join(reversed(out))
''',
    tests=[["2", 1], ["2", 3], ["7", 4], ["9", 2], ["23", 5], ["23", 9], ["79", 12], ["999", 1], ["999", 64],
           ["2468", 40], ["35", 1], ["99999999", 65536], ["99999999", 1], ["27374958", 12345], ["79797979", 40000]],
)


def b_kword(digits, k):
    words = ["".join(w) for w in _product(*[KEYS[d] for d in digits])]
    words.sort()
    return words[k - 1]


def g_kword(r):
    n = r.randint(1, 5)
    d = "".join(r.choice("23456789") for _ in range(n))
    tot = 1
    for c in d:
        tot *= len(KEYS[c])
    return [d, r.randint(1, tot)]


def v_kword(tests):
    for t in tests:
        d, k = t["args"]
        assert 1 <= len(d) <= 8 and all(c in KEYS for c in d)
        tot = 1
        for c in d:
            tot *= len(KEYS[c])
        assert 1 <= k <= tot


CHECKS["kth-keypad-word"] = (b_kword, g_kword, "exact")
VALIDATE["kth-keypad-word"] = v_kword


# ================================================================== MEDIUM

# ---------------------------------------------------------------- letter combinations of a phone number
add(
    id="letter-combinations-phone-keypad", title="Letter Combinations of a Phone Number", diff="Medium", topic=TOPIC, tier="must",
    fn="letterCombinations", params=[("digits", "string")], ret="int[][]", cmp="rowset",
    desc="<p>On a phone keypad the digits <code>2</code> to <code>9</code> carry letters: <code>2</code>: abc, <code>3</code>: def, <code>4</code>: ghi, <code>5</code>: jkl, <code>6</code>: mno, <code>7</code>: pqrs, <code>8</code>: tuv, <code>9</code>: wxyz.</p><p>Given a string <code>digits</code>, return every letter string that the digit sequence could spell, taking one letter per digit. To keep the answer numeric, each letter is written as its position in the alphabet (<code>a = 1</code>, <code>b = 2</code>, ..., <code>z = 26</code>), so every word is a row of <code>digits.length</code> integers. Rows may be returned in any order.</p><p>Example: <code>digits = \"23\"</code> gives 9 rows, <code>[1,4]</code> (ad), <code>[1,5]</code> (ae), <code>[1,6]</code> (af), <code>[2,4]</code>, <code>[2,5]</code>, <code>[2,6]</code>, <code>[3,4]</code>, <code>[3,5]</code>, <code>[3,6]</code>.</p>",
    constraints=["1 &le; digits.length &le; 4", "digits contains only the characters 2-9"],
    hints=["Each digit is an independent choice among 3 or 4 letters. The answer is every way of making one choice per digit.",
           "Process the digits from left to right with a recursive function that takes the index of the digit to handle and keeps the letters chosen so far in a shared row.",
           "When the index equals <code>digits.length</code>, copy the current row into the result. Otherwise loop over the letters of the current digit: append it, recurse on the next index, then remove it again (backtrack)."],
    editorial=["This is the textbook backtracking tree: level <code>i</code> of the tree corresponds to digit <code>i</code>, and each node has as many children as that key has letters. A root-to-leaf path is one word.",
               "Keep one mutable list for the current word. Append a letter, recurse, and pop it on the way back so that the same list can be reused for the next sibling. The number of leaves is the product of the letter counts, at most 4<sup>4</sup> = 256 here, and each leaf costs O(n) to copy, which gives O(n * 4<sup>n</sup>) overall. An iterative version builds the answer digit by digit by extending every existing word with every letter of the next key."],
    time="O(n * 4<sup>n</sup>)", space="O(n) recursion plus output",
    solution='''def letterCombinations(digits):
    keys = {"2": "abc", "3": "def", "4": "ghi", "5": "jkl", "6": "mno", "7": "pqrs", "8": "tuv", "9": "wxyz"}
    res = []
    cur = []

    def go(i):
        if i == len(digits):
            res.append(cur[:])
            return
        for ch in keys[digits[i]]:
            cur.append(ord(ch) - 96)
            go(i + 1)
            cur.pop()

    go(0)
    return res
''',
    tests=[["2"], ["7"], ["9"], ["23"], ["79"], ["27"], ["222"], ["789"], ["2345"], ["9999"], ["7777"], ["5678"], ["8"], ["4"]],
)


def b_letters(digits):
    return [[ord(c) - 96 for c in w] for w in ("".join(t) for t in _product(*[KEYS[d] for d in digits]))]


def v_letters(tests):
    for t in tests:
        d = t["args"][0]
        assert 1 <= len(d) <= 4 and all(c in KEYS for c in d)


CHECKS["letter-combinations-phone-keypad"] = (b_letters, lambda r: ["".join(r.choice("23456789") for _ in range(r.randint(1, 4)))], "rowset")
VALIDATE["letter-combinations-phone-keypad"] = v_letters


# ---------------------------------------------------------------- palindromic keypad words
add(
    id="count-palindromic-keypad-words", title="Count Palindromic Keypad Words", diff="Medium", topic=TOPIC, tier="extra",
    fn="countPalindromicWords", params=[("digits", "string")], ret="int", cmp="exact",
    desc="<p>On a phone keypad the digits <code>2</code> to <code>9</code> carry letters: <code>2</code>: abc, <code>3</code>: def, <code>4</code>: ghi, <code>5</code>: jkl, <code>6</code>: mno, <code>7</code>: pqrs, <code>8</code>: tuv, <code>9</code>: wxyz. Pressing every digit of <code>digits</code> once and choosing one letter for each press spells a word of the same length.</p><p>Count how many of these words are palindromes, that is, read the same forwards and backwards. Different letter choices count as different words.</p><p>Example: <code>digits = \"272\"</code> gives 12 (the outer letters must be equal: 3 choices from abc, the middle letter is any of the 4 letters of pqrs).</p>",
    constraints=["1 &le; digits.length &le; 30", "digits contains only the characters 2-9", "The answer is at most 2<sup>30</sup>"],
    hints=["For short inputs you can generate every word and test it. For 30 digits there can be 4<sup>30</sup> words, so that cannot work.",
           "A palindrome is decided by pairs: position <code>i</code> must carry the same letter as position <code>n - 1 - i</code>. The pairs do not influence each other.",
           "For each mirrored pair of digits count the letters that appear on both keys; multiply these counts. If the length is odd, the middle digit contributes all of its letters."],
    editorial=["A word is a palindrome exactly when every mirrored pair of positions holds the same letter. For a pair of digits (a, b) the number of ways to pick one shared letter is the size of the intersection of the letter sets of the two keys. The middle position of an odd-length input has no partner and can take any letter of its key.",
               "The choices for different pairs are independent, so the answer is the product of the intersection sizes (times the key size for the middle digit). Backtracking over all words is the natural first idea; recognising that the pairs are independent turns an exponential search into a linear pass. Two different keys never share a letter, so any pair of different digits makes the answer 0."],
    time="O(n)", space="O(1)",
    solution='''def countPalindromicWords(digits):
    keys = {"2": "abc", "3": "def", "4": "ghi", "5": "jkl", "6": "mno", "7": "pqrs", "8": "tuv", "9": "wxyz"}
    n = len(digits)
    ans = 1
    for i in range(n // 2):
        ans *= len(set(keys[digits[i]]) & set(keys[digits[n - 1 - i]]))
    if n % 2:
        ans *= len(keys[digits[n // 2]])
    return ans
''',
    tests=[["2"], ["7"], ["22"], ["23"], ["272"], ["727"], ["2332"], ["99"], ["7997"], ["79"], ["22222"], ["7" * 30], ["9" * 29],
           ["7" * 14 + "9" + "7" * 14], ["2" * 30], ["3" * 14 + "4" + "3" * 14]],
)


def b_palwords(digits):
    total = 1
    for d in digits:
        total *= len(KEYS[d])
    if total > 300000:
        # too many words to list: count the palindromes pair by pair, letter by letter
        n = len(digits)
        cnt = 1
        for i in range((n + 1) // 2):
            j = n - 1 - i
            cnt *= sum(1 for ch in KEYS[digits[i]] if i == j or ch in KEYS[digits[j]])
        return cnt
    cnt = 0
    for t in _product(*[KEYS[d] for d in digits]):
        if t == t[::-1]:
            cnt += 1
    return cnt


def g_palwords(r):
    pool = r.sample("23456789", r.randint(1, 3))
    return ["".join(r.choice(pool) for _ in range(r.randint(1, 7)))]


def v_palwords(tests):
    for t in tests:
        d = t["args"][0]
        assert 1 <= len(d) <= 30 and all(c in KEYS for c in d)
        assert 0 <= t["expected"] <= 2 ** 30


CHECKS["count-palindromic-keypad-words"] = (b_palwords, g_palwords, "exact")
VALIDATE["count-palindromic-keypad-words"] = v_palwords


# ---------------------------------------------------------------- numbers with distinct digits and banned digits
add(
    id="count-distinct-digit-numbers-banned", title="Count Numbers With Distinct Digits", diff="Medium", topic=TOPIC,
    fn="countDistinctDigitNumbers", params=[("n", "int"), ("banned", "int[]")], ret="int", cmp="exact",
    desc="<p>Count the integers <code>x</code> with <code>0 &le; x &lt; 10<sup>n</sup></code> that satisfy both rules:</p><ul><li>no digit occurs twice in the usual decimal writing of <code>x</code> (no leading zeros are written, and <code>0</code> itself is written as a single digit <code>0</code>);</li><li>no digit of <code>x</code> appears in the array <code>banned</code>.</li></ul><p>Example: <code>n = 2</code>, <code>banned = []</code> gives 91 (the 100 numbers 0..99 minus the 9 numbers 11, 22, ..., 99). With <code>banned = [0]</code> the answer is 81: nine one-digit numbers and 9 * 8 two-digit numbers.</p>",
    constraints=["1 &le; n &le; 10", "0 &le; banned.length &le; 10", "Every banned[i] is a digit from 0 to 9 and the values are distinct"],
    hints=["Count by the number of digits of x. A number with L digits has to use L different digits.",
           "Build the digits from left to right. The first digit has to be non-zero and allowed; every later digit has to be allowed and unused so far.",
           "After the first digit the number of choices only depends on how many allowed digits are left, so the count for length L is (non-zero allowed digits) * (a-1) * (a-2) * ... where a is the number of allowed digits. Do not forget the number 0 itself."],
    editorial=["Let <code>a</code> be the number of allowed digits and <code>nz</code> the number of allowed digits other than zero. A backtracking search would pick digit after digit, marking used digits; its branching only depends on counts, so it can be replaced by a product.",
               "For a length <code>L &ge; 1</code> there are <code>nz</code> choices for the first digit, then <code>a-1</code> for the second, <code>a-2</code> for the third, and so on: <code>nz * (a-1) * (a-2) * ... * (a-L+1)</code>. Sum this over <code>L = 1..n</code> and add 1 for the number 0 if zero is not banned. The product becomes 0 as soon as the factor <code>a-L+1</code> reaches 0, which also covers lengths longer than the number of allowed digits."],
    time="O(n)", space="O(1)",
    solution='''def countDistinctDigitNumbers(n, banned):
    bad = set(banned)
    a = 10 - len(bad)
    nz = a - (0 not in bad)
    total = 1 if 0 not in bad else 0
    ways = nz
    for L in range(1, n + 1):
        if L > 1:
            ways *= max(a - L + 1, 0)
        total += ways
    return total
''',
    tests=[[1, []], [2, []], [2, [0]], [1, [0]], [3, []], [3, [1, 2, 3]], [4, [0, 9]], [5, [5]], [2, [1, 2, 3, 4, 5, 6, 7, 8, 9]],
           [3, [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]], [6, [7, 8]], [10, []], [10, [0]], [9, [3]], [10, [2, 4, 6, 8]], [10, [1, 2, 3, 4, 5, 6, 7, 8]]],
)


def b_distinct_digits(n, banned):
    if n > 5:
        # too many numbers to scan: dynamic programming over the set of digits already used
        bm = sum(1 << b for b in banned)
        cur = {}
        for d in range(10):
            if not bm >> d & 1:
                cur[1 << d] = cur.get(1 << d, 0) + (1 if d else 0)
        zero = 0 if bm & 1 else 1
        total = zero + sum(cur.values())
        for _ in range(n - 1):
            nxt = {}
            for mask, c in cur.items():
                if not c:
                    continue
                for d in range(10):
                    if not (mask | bm) >> d & 1:
                        nxt[mask | 1 << d] = nxt.get(mask | 1 << d, 0) + c
            cur = nxt
            total += sum(cur.values())
        return total
    bad = {str(b) for b in banned}
    cnt = 0
    for x in range(10 ** n):
        s = str(x)
        if len(set(s)) == len(s) and not (set(s) & bad):
            cnt += 1
    return cnt


def g_distinct_digits(r):
    bn = r.sample(range(10), r.choice([0, 0, 1, 2, 3, 5, 8]))
    return [r.randint(1, 5), bn]


def v_distinct_digits(tests):
    for t in tests:
        n, bn = t["args"]
        assert 1 <= n <= 10 and len(bn) <= 10 and len(set(bn)) == len(bn) and all(0 <= b <= 9 for b in bn)


CHECKS["count-distinct-digit-numbers-banned"] = (b_distinct_digits, g_distinct_digits, "exact")
VALIDATE["count-distinct-digit-numbers-banned"] = v_distinct_digits


# ---------------------------------------------------------------- additive number
def _additive_tests():
    r = rnd(8601)
    out = [["112358"], ["199100199"], ["1023"], ["000"], ["101"], ["123"], ["1203"], ["011235"], ["198019823962"],
           ["112"], ["1991001991"], ["0" * 35], ["1" * 35], ["9" * 35]]

    def chain(a, b, limit):
        s = str(a) + str(b)
        while True:
            a, b = b, a + b
            if len(s) + len(str(b)) > limit:
                return s
            s += str(b)

    s = chain(r.randint(10 ** 5, 10 ** 6), r.randint(10 ** 5, 10 ** 6), 35)
    out.append([s])
    t = list(s)
    t[-1] = str((int(t[-1]) + 1) % 10)
    out.append(["".join(t)])
    out.append([chain(3, 5, 35)])
    return out


add(
    id="additive-number", title="Additive Number", diff="Medium", topic=TOPIC,
    fn="isAdditiveNumber", params=[("num", "string")], ret="bool", cmp="exact",
    desc="<p>A string of digits is <strong>additive</strong> if it can be cut into at least three non-empty pieces that are non-negative integers with these properties:</p><ul><li>no piece has a leading zero (a piece equal to <code>0</code> is written as a single <code>0</code>);</li><li>starting from the third piece, every piece equals the sum of the two pieces before it.</li></ul><p>Return <code>true</code> if <code>num</code> is additive. Example: <code>\"112358\"</code> is additive (1, 1, 2, 3, 5, 8). <code>\"199100199\"</code> is additive (1, 99, 100, 199). <code>\"1023\"</code> is not: the only way to start with 1 and 0 would need the next piece to be 1, but it is 23, and a piece such as <code>02</code> is forbidden.</p><p>The pieces can be larger than 32-bit integers; the string has at most 35 digits.</p>",
    constraints=["3 &le; num.length &le; 35", "num contains only the digits 0-9"],
    hints=["Once the first two pieces are fixed, all later pieces are forced. So the search is only over the first two pieces.",
           "Try every length for the first piece and every length for the second one. Reject a piece with a leading zero and more than one digit.",
           "After fixing the first two numbers, repeatedly compute their sum as a string and check that <code>num</code> continues with it at the current position. Succeed if you reach the end of the string with at least three pieces."],
    editorial=["Choose the first piece <code>num[0:i]</code> and the second piece <code>num[i:j]</code>; there are O(n<sup>2</sup>) such choices and each one fixes the whole sequence. Python integers do not overflow, but in other languages the pieces can be added as digit strings.",
               "For each choice, simulate: compute <code>x + y</code>, write it as text and check that it matches <code>num</code> at the current position, then slide the two operands forward. Because <code>j &lt; n</code> there is always at least one more piece to match, so a successful run has three or more pieces. Break out of a loop as soon as a piece would start with a leading zero, because every longer piece with the same start is invalid too. Total cost is O(n<sup>3</sup>) in the worst case, which is tiny for n &le; 35."],
    time="O(n<sup>3</sup>)", space="O(n)",
    solution='''def isAdditiveNumber(num):
    n = len(num)
    for i in range(1, n):
        if i > 1 and num[0] == "0":
            break
        for j in range(i + 1, n):
            if j - i > 1 and num[i] == "0":
                break
            x, y, pos = int(num[:i]), int(num[i:j]), j
            while pos < n:
                z = str(x + y)
                if not num.startswith(z, pos):
                    break
                pos += len(z)
                x, y = y, x + y
            if pos == n:
                return True
    return False
''',
    tests=_additive_tests(),
)


def b_additive(num):
    n = len(num)
    if n > 12:
        # too many cuts to list: grow the list of pieces one piece at a time and check each new piece at once
        def grow(parts, pos):
            if pos == n:
                return len(parts) >= 3
            for e in range(pos + 1, n + 1):
                piece = num[pos:e]
                if len(piece) > 1 and piece[0] == "0":
                    break
                if len(parts) >= 2 and int(piece) != parts[-1] + parts[-2]:
                    continue
                if grow(parts + [int(piece)], e):
                    return True
            return False

        return grow([], 0)
    for mask in range(1 << (n - 1)):
        parts = []
        last = 0
        for i in range(n - 1):
            if mask >> i & 1:
                parts.append(num[last:i + 1])
                last = i + 1
        parts.append(num[last:])
        if len(parts) < 3 or any(len(p) > 1 and p[0] == "0" for p in parts):
            continue
        v = [int(p) for p in parts]
        if all(v[k] == v[k - 1] + v[k - 2] for k in range(2, len(v))):
            return True
    return False


def g_additive(r):
    if r.random() < 0.5:
        a, b = r.randint(0, 20), r.randint(0, 20)
        s = str(a) + str(b)
        while True:
            a, b = b, a + b
            if len(s) + len(str(b)) > 12:
                break
            s += str(b)
        if len(s) < 3:
            s += "0"
        if r.random() < 0.3:
            i = r.randrange(len(s))
            s = s[:i] + str(r.randint(0, 9)) + s[i + 1:]
        return [s]
    return ["".join(r.choice("01123") for _ in range(r.randint(3, 11)))]


def v_additive(tests):
    for t in tests:
        s = t["args"][0]
        assert 3 <= len(s) <= 35 and s.isdigit()
    assert any(t["expected"] for t in tests) and not all(t["expected"] for t in tests)


CHECKS["additive-number"] = (b_additive, g_additive, "exact")
VALIDATE["additive-number"] = v_additive


# ---------------------------------------------------------------- same consecutive difference
add(
    id="numbers-with-same-consecutive-difference", title="Numbers With Fixed Digit Gap", diff="Medium", topic=TOPIC,
    fn="numbersWithDigitGap", params=[("n", "int"), ("k", "int")], ret="int[]", cmp="flat",
    desc="<p>Return all integers that have exactly <code>n</code> digits (no leading zero) and in which the absolute difference between every two neighbouring digits is exactly <code>k</code>. The numbers may be returned in any order, each one only once.</p><p>Example: <code>n = 3</code>, <code>k = 7</code> gives <code>181, 292, 707, 818, 929</code>. Note that <code>070</code> does not count because it starts with a zero.</p>",
    constraints=["2 &le; n &le; 9", "0 &le; k &le; 9"],
    hints=["There are at most 9 * 10<sup>n-1</sup> candidates, far too many to test one by one for n = 9. Build the numbers digit by digit instead.",
           "Given the last digit <code>d</code>, the next digit must be <code>d + k</code> or <code>d - k</code>, if that is a digit between 0 and 9.",
           "Start the search from every first digit 1..9. When <code>k = 0</code> the two options <code>d + k</code> and <code>d - k</code> are the same digit, so make sure the number is not produced twice."],
    editorial=["Run a depth-first search that extends a partial number by one digit at a time. From last digit <code>d</code> the only possible next digits are <code>d + k</code> and <code>d - k</code>. Skip candidates outside 0..9, and when <code>k = 0</code> try just one of them, otherwise the same number would be reported twice.",
               "Every first digit 1..9 starts a binary tree of depth <code>n - 1</code>, so there are at most 9 * 2<sup>n-1</sup> numbers (2,304 for n = 9) and the search visits no dead branches other than the digit-range cut-offs. Carrying the number as an integer (<code>value * 10 + digit</code>) avoids building strings."],
    time="O(9 * 2<sup>n</sup>)", space="O(n) recursion plus output",
    solution='''def numbersWithDigitGap(n, k):
    res = []

    def go(value, last, left):
        if left == 0:
            res.append(value)
            return
        nxt = {last + k, last - k}
        for d in nxt:
            if 0 <= d <= 9:
                go(value * 10 + d, d, left - 1)

    for first in range(1, 10):
        go(first, first, n - 1)
    return res
''',
    tests=[[3, 7], [2, 1], [2, 0], [2, 9], [3, 0], [3, 1], [4, 5], [2, 5], [5, 3], [6, 8], [9, 1], [9, 2], [8, 0], [7, 4]],
)


def b_gap(n, k):
    if n > 5:
        # too many numbers to scan: try every first digit with every pattern of up/down steps
        seen = set()
        for first in range(1, 10):
            for signs in _product((1, -1), repeat=n - 1):
                d, val, ok = first, first, True
                for sg in signs:
                    d += sg * k
                    if not 0 <= d <= 9:
                        ok = False
                        break
                    val = val * 10 + d
                if ok:
                    seen.add(val)
        return sorted(seen)
    out = []
    for x in range(10 ** (n - 1), 10 ** n):
        s = str(x)
        if all(abs(int(s[i]) - int(s[i + 1])) == k for i in range(n - 1)):
            out.append(x)
    return out


def v_gap(tests):
    for t in tests:
        n, k = t["args"]
        assert 2 <= n <= 9 and 0 <= k <= 9
        e = t["expected"]
        assert len(set(e)) == len(e)
        assert all(10 ** (n - 1) <= x < 10 ** n for x in e)


CHECKS["numbers-with-same-consecutive-difference"] = (b_gap, lambda r: [r.randint(2, 5), r.randint(0, 9)], "flat")
VALIDATE["numbers-with-same-consecutive-difference"] = v_gap


# ---------------------------------------------------------------- different ways to parenthesize
def _paren_tests():
    r = rnd(8602)
    out = [[[2, 3, 4, 5], [2, 1, 2]], [[2, 1, 1], [0, 0]], [[7], []], [[3, 4], [2]], [[5, 5], [1]], [[0, 0, 0], [2, 1]],
           [[1, 2, 3, 4, 5], [0, 2, 1, 2]], [[9, 9, 9, 9, 9, 9, 9, 9, 9], [2, 2, 2, 2, 2, 2, 2, 2]],
           [[9, 9, 9, 9, 9, 9, 9, 9, 9], [1, 1, 1, 1, 1, 1, 1, 1]]]
    for _ in range(3):
        m = 9
        out.append([[r.randint(0, 9) for _ in range(m)], [r.randint(0, 2) for _ in range(m - 1)]])
    out.append([[3, 8, 2, 6, 4, 7, 5], [2, 1, 2, 0, 2, 1]])
    return out


add(
    id="different-ways-to-parenthesize", title="All Results of Parenthesizing an Expression", diff="Medium", topic=TOPIC,
    fn="parenthesizeResults", params=[("nums", "int[]"), ("ops", "int[]")], ret="int[]", cmp="exact",
    desc="<p>An arithmetic expression is given in two arrays. <code>nums</code> holds the operands in order, and <code>ops[i]</code> is the operator between <code>nums[i]</code> and <code>nums[i+1]</code>, coded as <code>0</code> = addition, <code>1</code> = subtraction, <code>2</code> = multiplication.</p><p>You may put parentheses anywhere you like, so that the operations are carried out in any order that is a valid nesting (ignore the usual rule that multiplication goes first). Return every <strong>distinct</strong> value the expression can have, sorted in increasing order.</p><p>Example: <code>nums = [2,3,4,5]</code>, <code>ops = [2,1,2]</code> is the expression <code>2*3-4*5</code>. The five ways to evaluate it give -34, -14, -10, -10 and 10, so the answer is <code>[-34,-14,-10,10]</code>.</p>",
    constraints=["1 &le; nums.length &le; 9", "ops.length = nums.length - 1", "0 &le; nums[i] &le; 9", "ops[i] is 0, 1 or 2"],
    hints=["Think about the operation that is carried out <em>last</em>. It splits the expression into a left part and a right part that are evaluated independently.",
           "Choose the last operator position <code>m</code>. Every value of the left part combined with every value of the right part through <code>ops[m]</code> is a possible result.",
           "The same sub-expression <code>nums[i..j]</code> is needed from many different splits, so cache its set of values (memoization). A set also removes duplicate values."],
    editorial=["Define <code>go(i, j)</code> as the set of values that the operands <code>nums[i..j]</code> can reach. If <code>i = j</code> it is just that one operand. Otherwise try every operator position <code>m</code> in <code>i..j-1</code> as the one applied last, and combine every value of <code>go(i, m)</code> with every value of <code>go(m+1, j)</code>.",
               "Without caching the same sub-ranges are solved again and again, and the number of parenthesizations is the Catalan number (1,430 for nine operands). Caching the value set per range keeps the work to the sum over ranges of the product of the sizes of the two sets, and sets collapse equal values. All values stay below 9<sup>9</sup> in absolute value, which fits in 32 bits."],
    time="O(Catalan(m)) combinations in the worst case", space="O(m<sup>2</sup>) cached sets",
    solution='''def parenthesizeResults(nums, ops):
    memo = {}

    def go(i, j):
        if (i, j) in memo:
            return memo[(i, j)]
        if i == j:
            res = {nums[i]}
        else:
            res = set()
            for m in range(i, j):
                o = ops[m]
                for a in go(i, m):
                    for b in go(m + 1, j):
                        res.add(a + b if o == 0 else a - b if o == 1 else a * b)
        memo[(i, j)] = res
        return res

    return sorted(go(0, len(nums) - 1))
''',
    tests=_paren_tests(),
)


def b_paren(nums, ops):
    def go(vals, os):
        if len(vals) == 1:
            return {vals[0]}
        res = set()
        for i in range(len(os)):
            a, b, o = vals[i], vals[i + 1], os[i]
            c = a + b if o == 0 else a - b if o == 1 else a * b
            res |= go(vals[:i] + [c] + vals[i + 2:], os[:i] + os[i + 1:])
        return res

    return sorted(go(list(nums), list(ops)))


def g_paren(r):
    m = r.randint(1, 6)
    return [[r.randint(0, 9) for _ in range(m)], [r.randint(0, 2) for _ in range(m - 1)]]


def v_paren(tests):
    for t in tests:
        nums, ops = t["args"]
        assert 1 <= len(nums) <= 9 and len(ops) == len(nums) - 1
        assert all(0 <= x <= 9 for x in nums) and all(o in (0, 1, 2) for o in ops)
        e = t["expected"]
        assert e == sorted(set(e))


CHECKS["different-ways-to-parenthesize"] = (b_paren, g_paren, "exact")
VALIDATE["different-ways-to-parenthesize"] = v_paren


# ================================================================== HARD

# ---------------------------------------------------------------- remove invalid parentheses, count results
def _remove_tests():
    r = rnd(8603)
    out = [["()())()"], ["(a)())()"], [")("], ["n"], ["()"], ["((("], ["((()"], [")))a((("], ["(()(()"], ["()()()))"],
           ["a(b(c)d)e)f)g(h"], ["(a)b(c)d(e)f(g)h"]]

    def need(s):
        bal = lo = 0
        for c in s:
            if c == "(":
                bal += 1
            elif c == ")":
                if bal:
                    bal -= 1
                else:
                    lo += 1
        return lo + bal

    while len(out) < 16:
        n = r.randint(16, 20)
        s = "".join(r.choice("(((()))a)") for _ in range(n))
        if 3 <= need(s) <= 5:
            out.append([s])
    return out


add(
    id="remove-invalid-parentheses-count", title="Count Minimal Parenthesis Repairs", diff="Hard", topic=TOPIC,
    fn="countMinimalRepairs", params=[("s", "string")], ret="int", cmp="exact",
    desc="<p>The string <code>s</code> contains round brackets <code>(</code> and <code>)</code> and lowercase letters. A string is <strong>valid</strong> when its brackets are balanced: scanning from left to right, a <code>)</code> never appears when no <code>(</code> is waiting, and at the end no <code>(</code> is left over. Letters do not matter.</p><p>You may delete brackets (never letters) until the string becomes valid, and you want to delete as few brackets as possible. Return the number of <strong>different</strong> strings that can result from a deletion of that minimal size. Two results are different if the resulting texts differ.</p><p>Example: <code>s = \"()())()\"</code> needs one deletion and can become <code>\"(())()\"</code> or <code>\"()()()\"</code>, so the answer is 2. For <code>\")(\"</code> both brackets must go and the only result is the empty string, so the answer is 1.</p>",
    constraints=["1 &le; s.length &le; 20", "s consists of the characters ( ) and a-z"],
    hints=["First find out how many closing and opening brackets have to be deleted at least. A left-to-right scan with a balance counter tells you.",
           "Search over which brackets to delete, but only delete as many as the minimum. Different deletions can produce the same text, so you need a rule against duplicates.",
           "When several equal brackets stand in a row, deleting any one of them gives the same text. Allow only the first bracket of such a run to be deleted, and delete positions in increasing order so that each text is generated once."],
    editorial=["Scan left to right keeping a balance. Whenever the balance would go below zero there is a surplus <code>)</code> in the prefix; at least one of the closing brackets seen so far must be deleted. After the scan, the balance that is left is the number of surplus <code>(</code>, which are handled by running the same logic on the reversed string with the roles of the brackets swapped.",
               "The classic recursion fixes the first scan position <code>i</code> where the balance becomes negative and tries to remove one <code>)</code> at some position <code>j &le; i</code>. To avoid duplicates it removes <code>s[j]</code> only if it is the first <code>)</code> of its run of equal characters, and the next level only looks at positions from <code>j</code> on. When the scan has no more violations the string is reversed and processed again for the opening brackets. Every string that reaches the end is a distinct, minimal and valid result, so the answer is the number of such strings. With at most 20 characters the search is small."],
    time="O(2<sup>n</sup>) worst case, much less with pruning", space="O(n) recursion",
    solution='''def countMinimalRepairs(s):
    results = []

    def fix(t, si, sj, pair):
        bal = 0
        for i in range(si, len(t)):
            if t[i] == pair[0]:
                bal += 1
            elif t[i] == pair[1]:
                bal -= 1
            if bal >= 0:
                continue
            for j in range(sj, i + 1):
                if t[j] == pair[1] and (j == sj or t[j - 1] != pair[1]):
                    fix(t[:j] + t[j + 1:], i, j, pair)
            return
        rev = t[::-1]
        if pair[0] == "(":
            fix(rev, 0, 0, (")", "("))
        else:
            results.append(rev)

    fix(s, 0, 0, ("(", ")"))
    return len(results)
''',
    tests=_remove_tests(),
)


def b_remove(s):
    def valid(t):
        b = 0
        for c in t:
            if c == "(":
                b += 1
            elif c == ")":
                b -= 1
                if b < 0:
                    return False
        return b == 0

    level = {s}
    while True:
        good = [t for t in level if valid(t)]
        if good:
            return len(good)
        nxt = set()
        for t in level:
            for i in range(len(t)):
                if t[i] in "()":
                    nxt.add(t[:i] + t[i + 1:])
        level = nxt


def g_remove(r):
    n = r.randint(1, 11)
    return ["".join(r.choice("((()))a)") for _ in range(n))]


def v_remove(tests):
    for t in tests:
        s = t["args"][0]
        assert 1 <= len(s) <= 20 and all(c in "()" or c.islower() for c in s)
        assert t["expected"] >= 1


CHECKS["remove-invalid-parentheses-count"] = (b_remove, g_remove, "exact")
VALIDATE["remove-invalid-parentheses-count"] = v_remove


# ---------------------------------------------------------------- k-th balanced bracket sequence
add(
    id="kth-balanced-bracket-sequence", title="K-th Balanced Bracket Sequence", diff="Hard", topic=TOPIC, tier="extra",
    fn="kthBalancedSequence", params=[("n", "int"), ("k", "int")], ret="string", cmp="exact",
    desc="<p>A string of <code>(</code> and <code>)</code> is <strong>balanced</strong> if every <code>)</code> closes an earlier unmatched <code>(</code> and nothing is left open at the end. List all balanced strings with exactly <code>n</code> pairs of brackets in dictionary order, where <code>(</code> comes before <code>)</code>. Return the <code>k</code>-th string of that list, counting from 1.</p><p>Example: for <code>n = 3</code> the list is <code>((()))</code>, <code>(()())</code>, <code>(())()</code>, <code>()(())</code>, <code>()()()</code>, so <code>k = 3</code> gives <code>\"(())()\"</code>.</p>",
    constraints=["1 &le; n &le; 15", "1 &le; k &le; Catalan(n), the number of balanced strings with n pairs (9,694,845 for n = 15)"],
    hints=["For n = 15 there are almost ten million strings, which is too slow to list. You need to count instead of enumerate.",
           "Decide the string one character at a time. If you place <code>(</code> now, how many balanced completions are there? If <code>k</code> is not larger than that number, the answer starts with <code>(</code>.",
           "Precompute <code>ways[r][b]</code>: the number of ways to finish when <code>r</code> characters remain and <code>b</code> brackets are currently open. Use <code>ways[r][b] = ways[r-1][b+1] + ways[r-1][b-1]</code>. If <code>k</code> exceeds the count for <code>(</code>, subtract it from <code>k</code> and place <code>)</code> instead."],
    editorial=["This is backtracking where whole subtrees are skipped by counting them. Let <code>ways[r][b]</code> be the number of balanced completions with <code>r</code> characters left and <code>b</code> unmatched opening brackets: <code>ways[0][0] = 1</code>, and a completion starts either with <code>(</code> (leading to <code>b+1</code>) or, if <code>b &gt; 0</code>, with <code>)</code> (leading to <code>b-1</code>).",
               "Build the answer left to right. At each step the strings that start with the current prefix plus <code>(</code> come first in dictionary order, and there are <code>ways[r-1][b+1]</code> of them. If <code>k</code> is within that count, append <code>(</code>; otherwise subtract the count from <code>k</code> and append <code>)</code>. The table has O(n<sup>2</sup>) entries and the construction takes O(n) steps, so n = 15 is instant, while listing all 9.7 million strings would not be."],
    time="O(n<sup>2</sup>)", space="O(n<sup>2</sup>)",
    solution='''def kthBalancedSequence(n, k):
    m = 2 * n
    ways = [[0] * (m + 3) for _ in range(m + 1)]
    ways[0][0] = 1
    for r in range(1, m + 1):
        for b in range(0, m + 1):
            ways[r][b] = ways[r - 1][b + 1] + (ways[r - 1][b - 1] if b > 0 else 0)
    out = []
    bal = 0
    for pos in range(m):
        rem = m - pos - 1
        open_count = ways[rem][bal + 1]
        if k <= open_count:
            out.append("(")
            bal += 1
        else:
            k -= open_count
            out.append(")")
            bal -= 1
    return "".join(out)
''',
    tests=[[1, 1], [2, 1], [2, 2], [3, 1], [3, 3], [3, 5], [4, 7], [4, 14], [5, 20], [6, 132], [8, 1000], [10, 12345], [12, 100000],
           [15, 1], [15, 9694845], [15, 4000000], [14, 1]],
)


def b_kbal(n, k):
    res = []

    def go(cur, o, c):
        if len(cur) == 2 * n:
            res.append(cur)
            return
        if o < n:
            go(cur + "(", o + 1, c)
        if c < o:
            go(cur + ")", o, c + 1)

    go("", 0, 0)
    res.sort()
    return res[k - 1]


def g_kbal(r):
    n = r.randint(1, 7)
    cat = 1
    for i in range(n):
        cat = cat * 2 * (2 * i + 1) // (i + 2)
    return [n, r.randint(1, cat)]


def v_kbal(tests):
    from math import comb
    for t in tests:
        n, k = t["args"]
        assert 1 <= n <= 15
        assert 1 <= k <= comb(2 * n, n) // (n + 1)
        e = t["expected"]
        assert len(e) == 2 * n
        b = 0
        for c in e:
            b += 1 if c == "(" else -1
            assert b >= 0
        assert b == 0


CHECKS["kth-balanced-bracket-sequence"] = (b_kbal, g_kbal, "exact")
VALIDATE["kth-balanced-bracket-sequence"] = v_kbal


# ---------------------------------------------------------------- strobogrammatic numbers in a range
add(
    id="count-strobogrammatic-numbers-in-range", title="Count Upside-Down Numbers in a Range", diff="Hard", topic=TOPIC, tier="extra",
    fn="countUpsideDown", params=[("low", "int"), ("high", "int")], ret="int", cmp="exact",
    desc="<p>A number is <strong>upside-down symmetric</strong> if it reads the same after the paper is rotated by 180 degrees. Under that rotation the digits <code>0</code>, <code>1</code> and <code>8</code> stay the same, <code>6</code> becomes <code>9</code> and <code>9</code> becomes <code>6</code>, and no other digit is allowed. The rotated number is read in the opposite order, so <code>69</code>, <code>88</code>, <code>96</code> and <code>609</code> qualify, while <code>25</code> and <code>962</code> do not. Numbers are written without leading zeros, and <code>0</code> itself is upside-down symmetric.</p><p>Count the upside-down symmetric integers <code>x</code> with <code>low &le; x &le; high</code>.</p><p>Example: <code>low = 50</code>, <code>high = 100</code> gives 3 (69, 88 and 96).</p>",
    constraints=["0 &le; low &le; high &le; 2<sup>31</sup> - 1"],
    hints=["The range can be two billion numbers wide, so you cannot test every number. But there are very few upside-down symmetric numbers.",
           "Such a number is built from the outside in: the first and last digit are a pair (0-0, 1-1, 8-8, 6-9 or 9-6), the next two digits are the next pair, and so on. An odd length has a middle digit that is 0, 1 or 8.",
           "Generate all of them for every length from the number of digits of <code>low</code> up to the number of digits of <code>high</code>, never put 0 as the outer digit of a number longer than one digit, and count those that lie in the range."],
    editorial=["Let <code>build(L, outer)</code> return all symmetric digit strings of length L. For L = 0 it is the empty string, for L = 1 it is 0, 1 and 8, and otherwise wrap every string of length L - 2 with one of the five digit pairs. The flag <code>outer</code> forbids the pair 0-0 at the outermost level so that no number has a leading zero (the single digit 0 is still allowed).",
               "There are only 4 * 5<sup>(L/2) - 1</sup> such numbers of an even length L and 4 * 5<sup>(L-3)/2</sup> * 3 of an odd length L, so about 5,000 numbers of up to ten digits in total. Generate each length between the digit counts of <code>low</code> and <code>high</code> and count the ones that fall in <code>[low, high]</code>; the lengths strictly between the two end lengths are inside the range automatically, but a simple comparison on each generated value is just as good."],
    time="O(number of symmetric numbers with up to 10 digits)", space="O(that many strings)",
    solution='''def countUpsideDown(low, high):
    pairs = [("0", "0"), ("1", "1"), ("8", "8"), ("6", "9"), ("9", "6")]

    def build(length, outer):
        if length == 0:
            return [""]
        if length == 1:
            return ["0", "1", "8"]
        inner = build(length - 2, False)
        res = []
        for a, b in pairs:
            if outer and a == "0":
                continue
            for mid in inner:
                res.append(a + mid + b)
        return res

    count = 0
    for length in range(len(str(low)), len(str(high)) + 1):
        for s in build(length, True):
            if low <= int(s) <= high:
                count += 1
    return count
''',
    tests=[[50, 100], [0, 100], [0, 0], [1, 1], [0, 9], [2, 7], [100, 1000], [6, 70], [609, 609], [610, 690], [0, 100000], [1000, 9999],
           [0, INT_MAX], [1, INT_MAX], [1000000000, INT_MAX], [123456789, 1987654321]],
)


_STROBO = {"0": "0", "1": "1", "8": "8", "6": "9", "9": "6"}


def b_strobo(low, high):
    cnt = 0
    for x in range(low, high + 1):
        s = str(x)
        if all(c in _STROBO for c in s) and "".join(_STROBO[c] for c in reversed(s)) == s:
            cnt += 1
    return cnt


def g_strobo(r):
    lo = r.randint(0, 3000) if r.random() < 0.7 else r.randint(0, 100000)
    return [lo, lo + r.randint(0, 3000)]


def v_strobo(tests):
    for t in tests:
        lo, hi = t["args"]
        assert 0 <= lo <= hi <= INT_MAX
        assert t["expected"] >= 0


CHECKS["count-strobogrammatic-numbers-in-range"] = (b_strobo, g_strobo, "exact")
VALIDATE["count-strobogrammatic-numbers-in-range"] = v_strobo
