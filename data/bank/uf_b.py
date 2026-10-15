"""Problems: union find, merging groups. See data/lib.py for the registry."""
from collections import Counter, deque
from itertools import product as _product

from lib import add, rnd, CHECKS, VALIDATE, gen_arr  # noqa: F401

TOPIC = "Union Find"
MOD = 10 ** 9 + 7


def _lower(s):
    return all("a" <= c <= "z" for c in s)


def _words(r, n, length, alpha):
    return "".join(r.choice(alpha) for _ in range(length))


# ================================================================ 1. smallest equivalent string
p = add(
    id="smallest-equivalent-string-from-pairs", tier="common", title="Smallest Equivalent String", diff="Easy", topic=TOPIC,
    fn="smallestEquivalent", params=[("a", "string"), ("b", "string"), ("base", "string")], ret="string", cmp="exact",
    desc="<p>The strings <code>a</code> and <code>b</code> have the same length and describe letter equivalences: for every index <code>i</code>, the letters <code>a[i]</code> and <code>b[i]</code> are equivalent. Equivalence is reflexive (a letter is equivalent to itself), symmetric and <strong>transitive</strong>: if <code>x</code> ~ <code>y</code> and <code>y</code> ~ <code>z</code> then <code>x</code> ~ <code>z</code>.</p><p>Replace every letter of <code>base</code> with the alphabetically smallest letter that is equivalent to it, and return the resulting string.</p><pre>a = \"parker\", b = \"morris\", base = \"parser\"   -> \"makkek\"   (p~m, a~o, r~k~s, e~i)\na = \"abc\",    b = \"cde\",    base = \"eed\"      -> \"aab\"      (a~c~e, b~d)\na = \"a\",      b = \"a\",      base = \"zzz\"      -> \"zzz\"</pre>",
    constraints=["1 &le; a.length = b.length &le; 1,000", "1 &le; base.length &le; 3,000", "All three strings consist of lowercase English letters"],
    hints=["Letters that are linked through chains of equivalences form groups. The answer for a letter only depends on its group.",
           "You only have 26 letters, so you can keep one representative per group. Which letter should be the representative?",
           "Use union-find on the 26 letters. When merging two groups always make the alphabetically smaller root the parent, so that <code>find(c)</code> directly returns the smallest letter of the group."],
    editorial=["Model the 26 letters as a union-find structure. For each index <code>i</code>, union <code>a[i]</code> with <code>b[i]</code>. If the union always attaches the root with the larger letter below the root with the smaller letter, then the root of every group is its smallest member, and <code>find(c)</code> gives exactly the smallest equivalent letter of <code>c</code>.",
               "Finally map every character of <code>base</code> through <code>find</code>. The work is O(n &alpha;(26) + |base|). A DFS over a 26-node graph works as well; the point is that transitivity makes this a connected-components problem."],
    time="O(n + m)", space="O(1)",
    solution='''def smallestEquivalent(a, b, base):
    parent = list(range(26))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for u, v in zip(a, b):
        ru, rv = find(ord(u) - 97), find(ord(v) - 97)
        if ru != rv:
            if ru < rv:
                parent[rv] = ru
            else:
                parent[ru] = rv
    return "".join(chr(97 + find(ord(c) - 97)) for c in base)
''',
    tests=[["parker", "morris", "parser"], ["abc", "cde", "eed"], ["a", "a", "zzz"], ["z", "a", "z"], ["ab", "ba", "ab"],
           ["leetcode", "programs", "sourcecode"], ["abcdefghijklmnopqrstuvwxyz", "bcdefghijklmnopqrstuvwxyz" + "a", "hello"],
           ["xy", "yz", "zyx"], ["mn", "no", "onm"], ["aaaa", "bbbb", "abab"], ["qwe", "ewq", "qqweeew"]],
)
_r = rnd(9101)
_alpha = "abcdefghijklmnopqrstuvwxyz"
p["tests"].append(["".join(_r.choice(_alpha) for _ in range(1000)), "".join(_r.choice(_alpha) for _ in range(1000)), "".join(_r.choice(_alpha) for _ in range(3000))])
p["tests"].append(["".join(_r.choice(_alpha) for _ in range(12)), "".join(_r.choice(_alpha) for _ in range(12)), "".join(_r.choice(_alpha) for _ in range(3000))])
p["tests"].append(["".join(_r.choice("mnopqrstuvwxyz") for _ in range(25)), "".join(_r.choice("mnopqrstuvwxyz") for _ in range(25)), "".join(_r.choice(_alpha) for _ in range(3000))])


def b_equiv(a, b, base):
    cls = {c: {c} for c in "abcdefghijklmnopqrstuvwxyz"}
    changed = True
    while changed:
        changed = False
        for u, v in zip(a, b):
            if cls[u] is not cls[v] and cls[u] != cls[v]:
                m = cls[u] | cls[v]
                for c in m:
                    cls[c] = m
                changed = True
    return "".join(min(cls[c]) for c in base)


def g_equiv(r):
    n = r.randint(1, 6)
    al = "abcdefg"
    return ["".join(r.choice(al) for _ in range(n)), "".join(r.choice(al) for _ in range(n)), "".join(r.choice(al) for _ in range(r.randint(1, 8)))]


def v_equiv(tests):
    for t in tests:
        a, b, base = t["args"]
        assert 1 <= len(a) <= 1000 and len(a) == len(b) and 1 <= len(base) <= 3000
        assert _lower(a) and _lower(b) and _lower(base) and len(t["expected"]) == len(base)


CHECKS["smallest-equivalent-string-from-pairs"] = (b_equiv, g_equiv, "exact")
VALIDATE["smallest-equivalent-string-from-pairs"] = v_equiv


# ================================================================ 2. merge accounts
p = add(
    id="merge-accounts-by-shared-emails", tier="must", title="Merge Accounts by Shared Emails", diff="Medium", topic=TOPIC,
    fn="mergeAccounts", params=[("accounts", "int[][]")], ret="int[][]", cmp="exact",
    desc="<p>A service stores accounts as integer rows. Each row is <code>[owner, email1, email2, ...]</code>: the first number is the id of the account's owner and the remaining numbers are the (positive integer) email ids registered on that account. An email may be listed twice inside one row.</p><p>Two accounts belong to the same person if they share <strong>at least one</strong> email, directly or through a chain of other accounts (A shares with B, B shares with C, so all three are one person). Different people can have the same owner id, so equal owner ids alone never justify a merge. It is guaranteed that accounts sharing an email also have the same owner id.</p><p>Merge the accounts of each person into one row: the owner id first, followed by all distinct emails of that person in increasing order. Return the merged rows sorted lexicographically (compare row elements from left to right, a shorter row that is a prefix of another comes first).</p><pre>accounts = [[1,10,20],[2,30],[1,20,40],[1,50]]\n-> [[1,10,20,40],[1,50],[2,30]]\naccounts = [[7,3,1],[7,2],[7,4,2],[7,5,4]]\n-> [[7,1,3],[7,2,4,5]]</pre>",
    constraints=["1 &le; accounts.length &le; 1,000", "Each row has at least 2 numbers (an owner and at least one email), and at most 10 emails", "1 &le; owner, email &le; 100,000", "Two accounts that share an email have the same owner id"],
    hints=["Accounts are the vertices of a graph; two accounts are linked when they share an email. Each person is a connected component.",
           "Walk through the accounts and remember, for each email, the first account where you saw it. Every later account holding that email must be merged with that first account.",
           "Union the account indices with union-find using that email-to-first-account map. Afterwards collect the emails of every account into a set for its root, sort each set, put the owner first, and sort all rows."],
    editorial=["Treat every account index as a node of a union-find structure. Scan all accounts and keep a dictionary <code>first[email]</code>. If the email was seen before, union the current account with <code>first[email]</code>; otherwise record the current account. After this pass, two accounts are in the same set exactly when they are linked through a chain of shared emails.",
               "Then group: for every account add its emails to a set belonging to its root (the owner id is the same for the whole group). Output <code>[owner] + sorted(emails)</code> for each group and sort the list of rows. With E total emails the cost is O(E &alpha;) for the unions plus O(E log E) for sorting. A DFS over an email-to-accounts graph gives the same result."],
    time="O(E log E)", space="O(E)",
    solution='''def mergeAccounts(accounts):
    n = len(accounts)
    parent = list(range(n))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    first = {}
    for i, acc in enumerate(accounts):
        for e in acc[1:]:
            if e in first:
                ra, rb = find(i), find(first[e])
                if ra != rb:
                    parent[ra] = rb
            else:
                first[e] = i
    groups = {}
    for i, acc in enumerate(accounts):
        r = find(i)
        if r not in groups:
            groups[r] = (acc[0], set())
        groups[r][1].update(acc[1:])
    res = [[o] + sorted(s) for o, s in groups.values()]
    res.sort()
    return res
''',
    tests=[[[[1, 10, 20], [2, 30], [1, 20, 40], [1, 50]]],
           [[[7, 3, 1], [7, 2], [7, 4, 2], [7, 5, 4]]],
           [[[4, 9]]],
           [[[1, 5, 5, 6]]],
           [[[1, 1], [1, 2], [1, 3]]],
           [[[2, 8, 9], [3, 7], [2, 9, 10], [3, 6, 7], [2, 11, 8]]],
           [[[5, 1], [5, 2], [5, 3], [5, 1, 2], [5, 4], [5, 3, 4]]],
           [[[9, 100000, 1], [9, 1, 99999], [8, 5, 6], [9, 99999, 2]]],
           [[[3, 4, 5], [2, 6, 7], [3, 5, 8], [2, 7, 9], [1, 10], [3, 8, 4]]],
           [[[1, 10, 20], [1, 30, 40], [1, 50, 60], [1, 20, 30], [1, 60, 10]]]],
)


def _accounts_gen(r, persons, owners, pool_lo, pool_hi, accs, maxe, dup=False):
    emails = r.sample(range(1, 100001), persons * pool_hi)
    pools = []
    k = 0
    for _ in range(persons):
        sz = r.randint(pool_lo, pool_hi)
        pools.append(emails[k:k + sz])
        k += pool_hi
    own = [r.randint(1, owners) for _ in range(persons)]
    rows = []
    for _ in range(accs):
        q = r.randrange(persons)
        take = r.randint(1, min(maxe, len(pools[q])))
        es = r.sample(pools[q], take)
        if dup and r.random() < 0.1:
            es.append(es[0])
        rows.append([own[q]] + es)
    return rows


_r = rnd(9102)
p["tests"].append([_accounts_gen(_r, 150, 80, 2, 6, 450, 4, True)])
p["tests"].append([_accounts_gen(_r, 25, 10, 6, 10, 500, 3)])
p["tests"].append([_accounts_gen(_r, 300, 300, 1, 3, 400, 2)])


def b_accounts(accounts):
    items = [(a[0], set(a[1:])) for a in accounts]
    changed = True
    while changed:
        changed = False
        for i in range(len(items)):
            for j in range(i + 1, len(items)):
                if items[i][1] & items[j][1]:
                    items[i] = (items[i][0], items[i][1] | items[j][1])
                    items.pop(j)
                    changed = True
                    break
            if changed:
                break
    return sorted([o] + sorted(s) for o, s in items)


def g_accounts(r):
    persons = r.randint(1, 4)
    return [_accounts_gen(r, persons, 3, 1, 4, r.randint(1, 7), 3, True)]


def v_accounts(tests):
    for t in tests:
        acc = t["args"][0]
        assert 1 <= len(acc) <= 1000
        who = {}
        for row in acc:
            assert len(row) >= 2 and len(row) - 1 <= 10 and 1 <= row[0] <= 100000
            for e in row[1:]:
                assert 1 <= e <= 100000
                assert who.setdefault(e, row[0]) == row[0], "email with two owners"
        res = t["expected"]
        assert res == sorted(res)
        allm = [e for row in res for e in row[1:]]
        assert len(allm) == len(set(allm)) == len(who)


CHECKS["merge-accounts-by-shared-emails"] = (b_accounts, g_accounts, "exact")
VALIDATE["merge-accounts-by-shared-emails"] = v_accounts


# ================================================================ 3. equality equations
p = add(
    id="equality-equations-satisfiable", tier="common", title="Equality Equations Satisfiable", diff="Medium", topic=TOPIC,
    fn="equationsPossible", params=[("n", "int"), ("equations", "int[][]")], ret="bool", cmp="exact",
    desc="<p>There are <code>n</code> integer variables <code>x<sub>0</sub> .. x<sub>n-1</sub></code>. You are given a list of constraints, each written as <code>[a, op, b]</code>:</p><ul><li><code>op = 0</code> means <code>x<sub>a</sub> = x<sub>b</sub></code> (equal)</li><li><code>op = 1</code> means <code>x<sub>a</sub> &ne; x<sub>b</sub></code> (different)</li></ul><p>Return <code>true</code> if some assignment of integers to the variables satisfies <strong>all</strong> constraints at the same time, otherwise <code>false</code>. Note that <code>a</code> and <code>b</code> may be the same variable.</p><pre>n = 4, equations = [[0,0,1],[1,0,2],[2,1,3]]   -> true   (x0=x1=x2, x3 different)\nn = 3, equations = [[0,0,1],[1,0,2],[0,1,2]]   -> false  (x0=x1=x2 but x0 != x2)\nn = 2, equations = [[1,1,1]]                    -> false  (x1 != x1)</pre>",
    constraints=["1 &le; n &le; 100,000", "0 &le; equations.length &le; 4,000", "equations[i] = [a, op, b] with 0 &le; a, b &lt; n and op in {0, 1}"],
    hints=["Equality is transitive: if x0 = x1 and x1 = x2 then x0 = x2. Which data structure keeps groups of variables that must be equal?",
           "First put every pair from an equality constraint into the same group. The groups can then take pairwise different values if they want to.",
           "After all equalities are processed, check every <code>!=</code> constraint: it is violated exactly when both variables ended up in the same group (including <code>a == b</code>)."],
    editorial=["Because there are infinitely many integers, any two groups that are not forced to be equal can simply be given different values. So the only way to fail is a <code>!=</code> constraint between two variables that equality constraints force to be the same.",
               "Run union-find over all constraints with <code>op = 0</code>. Then scan the constraints with <code>op = 1</code> and return <code>false</code> if <code>find(a) == find(b)</code>. The order of the input does not matter, but the two passes do: all equalities must be merged before any inequality is judged. Time O((n + m) &alpha;(n)), space O(n)."],
    time="O((n + m) &middot; &alpha;(n))", space="O(n)",
    solution='''def equationsPossible(n, equations):
    parent = list(range(n))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for a, op, b in equations:
        if op == 0:
            ra, rb = find(a), find(b)
            if ra != rb:
                parent[ra] = rb
    for a, op, b in equations:
        if op == 1 and find(a) == find(b):
            return False
    return True
''',
    tests=[[4, [[0, 0, 1], [1, 0, 2], [2, 1, 3]]],
           [3, [[0, 0, 1], [1, 0, 2], [0, 1, 2]]],
           [2, [[1, 1, 1]]],
           [1, []],
           [1, [[0, 0, 0]]],
           [3, [[0, 1, 1], [1, 1, 2], [0, 1, 2]]],
           [4, [[0, 1, 3], [0, 0, 1], [1, 0, 2], [2, 0, 3]]],
           [5, [[4, 0, 3], [3, 0, 2], [2, 0, 1], [1, 1, 0]]],
           [6, [[0, 0, 1], [2, 0, 3], [4, 0, 5], [1, 1, 2], [3, 1, 4], [5, 1, 0]]],
           [100000, [[99999, 0, 0], [0, 1, 99999], [5, 0, 99999]]]],
)


def _eq_instance(r, n, m, groups, bad):
    g = [r.randrange(groups) for _ in range(n)]
    byg = {}
    for i, x in enumerate(g):
        byg.setdefault(x, []).append(i)
    eqs = []
    while len(eqs) < m:
        a = r.randrange(n)
        if r.random() < 0.55:
            b = r.choice(byg[g[a]])
            eqs.append([a, 0, b])
        else:
            b = r.randrange(n)
            if g[a] != g[b]:
                eqs.append([a, 1, b])
    if bad:
        pairs = [(a, b) for a, op, b in eqs if op == 0 and a != b]
        a, b = r.choice(pairs)
        eqs.insert(r.randrange(len(eqs) + 1), [a, 1, b])
    return eqs


_r = rnd(9103)
p["tests"].append([2000, _eq_instance(_r, 2000, 2400, 500, False)])
p["tests"].append([2000, _eq_instance(_r, 2000, 1800, 400, True)])
p["tests"].append([2000, [[0, 1, 1999]] + [[i, 0, i + 1] for i in range(1999)][::-1]])
p["tests"].append([50, _eq_instance(_r, 50, 60, 10, False)])
_chain = [[i, 0, i + 1] for i in range(1, 1500)]
_chain.insert(0, [1, 1, 1500])
p["tests"].append([1501, _chain])


def b_eq(n, equations):
    for vals in _product(range(n), repeat=n):
        ok = True
        for a, op, b in equations:
            if (vals[a] == vals[b]) != (op == 0):
                ok = False
                break
        if ok:
            return True
    return False


def g_eq(r):
    n = r.randint(1, 5)
    return [n, [[r.randrange(n), r.randint(0, 1), r.randrange(n)] for _ in range(r.randint(0, 7))]]


def v_eq(tests):
    for t in tests:
        n, eqs = t["args"]
        assert 1 <= n <= 100000 and len(eqs) <= 4000
        assert all(len(e) == 3 and 0 <= e[0] < n and 0 <= e[2] < n and e[1] in (0, 1) for e in eqs)
    assert any(t["expected"] for t in tests) and any(not t["expected"] for t in tests)


CHECKS["equality-equations-satisfiable"] = (b_eq, g_eq, "exact")
VALIDATE["equality-equations-satisfiable"] = v_eq


# ================================================================ 4. min hamming distance
p = add(
    id="min-hamming-distance-after-swaps", tier="common", title="Minimum Hamming Distance After Swaps", diff="Medium", topic=TOPIC,
    fn="minHammingDistance", params=[("source", "int[]"), ("target", "int[]"), ("allowedSwaps", "int[][]")], ret="int", cmp="exact",
    desc="<p>The arrays <code>source</code> and <code>target</code> both have length <code>n</code>. The list <code>allowedSwaps</code> contains index pairs <code>[a, b]</code>: for each listed pair you may swap <code>source[a]</code> and <code>source[b]</code>, any number of times and in any order (pairs can be reused).</p><p>The <em>Hamming distance</em> of two equally long arrays is the number of positions where they differ. Return the smallest Hamming distance between <code>source</code> and <code>target</code> that can be reached by swapping inside <code>source</code>. <code>target</code> never changes.</p><pre>source = [1,2,3,4], target = [2,1,4,5], allowedSwaps = [[0,1],[2,3]]   -> 1\nsource = [1,2,3,4], target = [1,3,2,4], allowedSwaps = []              -> 2\nsource = [5,1,2,4,3], target = [1,5,4,2,3], allowedSwaps = [[0,4],[4,2],[1,3],[1,4]]  -> 0</pre>",
    constraints=["1 &le; n &le; 5,000", "source.length = target.length = n", "0 &le; source[i], target[i] &le; 100,000", "0 &le; allowedSwaps.length &le; 5,000, and 0 &le; a, b &lt; n with a &ne; b"],
    hints=["If you can swap positions 0&ndash;1 and 1&ndash;2, you can put the three values in any order. Which positions can exchange values with each other?",
           "Positions linked by chains of swaps form groups. Inside a group the values of <code>source</code> can be arranged freely; across groups nothing moves.",
           "For each group, count the values of <code>source</code> in it. Then walk over the group's <code>target</code> values: every target value that can still be matched by a source value (count &gt; 0) is a match, the rest add one to the distance."],
    editorial=["Build groups of positions with union-find over the swap pairs. In a group, the source values can be permuted arbitrarily, so the best we can do is match as many target values of that group as possible with source values of the same group; that is the size of the multiset intersection.",
               "Implementation: collect for every root a Counter of source values. For every position <code>j</code> in the group, if the Counter still has the value <code>target[j]</code>, decrement it (a match), otherwise add one to the answer. The groups are independent, so the sum over groups is optimal. Time O((n + m) &alpha;(n)), space O(n)."],
    time="O((n + m) &middot; &alpha;(n))", space="O(n)",
    solution='''def minHammingDistance(source, target, allowedSwaps):
    n = len(source)
    parent = list(range(n))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for a, b in allowedSwaps:
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb
    counts = {}
    for i in range(n):
        d = counts.setdefault(find(i), {})
        d[source[i]] = d.get(source[i], 0) + 1
    dist = 0
    for j in range(n):
        d = counts[find(j)]
        if d.get(target[j], 0) > 0:
            d[target[j]] -= 1
        else:
            dist += 1
    return dist
''',
    tests=[[[1, 2, 3, 4], [2, 1, 4, 5], [[0, 1], [2, 3]]],
           [[1, 2, 3, 4], [1, 3, 2, 4], []],
           [[5, 1, 2, 4, 3], [1, 5, 4, 2, 3], [[0, 4], [4, 2], [1, 3], [1, 4]]],
           [[7], [7], []],
           [[7], [8], []],
           [[1, 1, 1], [2, 2, 2], [[0, 1], [1, 2]]],
           [[1, 2, 2, 3], [3, 2, 2, 1], [[0, 3]]],
           [[0, 0, 5, 5], [5, 5, 0, 0], [[0, 2], [1, 3]]],
           [[4, 4, 9, 9, 1, 1], [9, 4, 4, 1, 9, 1], [[0, 1], [1, 2], [3, 4], [4, 5]]],
           [[100000, 0, 100000], [0, 100000, 100000], [[1, 0], [0, 1]]]],
)


def _hamming_inst(r, n, vmax, block, link, noise):
    src = [r.randint(0, vmax) for _ in range(n)]
    tgt = src[:]
    for s in range(0, n, block):
        seg = tgt[s:s + block]
        r.shuffle(seg)
        tgt[s:s + block] = seg
    for _ in range(int(n * noise)):
        tgt[r.randrange(n)] = r.randint(0, vmax)
    sw = []
    for s in range(0, n, block):
        for i in range(s, min(s + block, n) - 1):
            if r.random() < link:
                sw.append([i, i + 1])
    while len(sw) > 5000:
        sw.pop()
    return [src, tgt, sw]


_r = rnd(9104)
p["tests"].append(_hamming_inst(_r, 2000, 40, 6, 0.8, 0.05))
p["tests"].append(_hamming_inst(_r, 1500, 100000, 3, 0.9, 0.0))
_src = [_r.randint(0, 9) for _ in range(1500)]
_tgt = _src[::-1]
p["tests"].append([_src, _tgt, [[i, i + 1] for i in range(0, 1400)]])


def b_hamming(source, target, swaps):
    start = tuple(source)
    seen = {start}
    q = deque([start])
    while q:
        cur = q.popleft()
        for a, b in swaps:
            x = list(cur)
            x[a], x[b] = x[b], x[a]
            x = tuple(x)
            if x not in seen:
                seen.add(x)
                q.append(x)
    return min(sum(1 for u, v in zip(s, target) if u != v) for s in seen)


def g_hamming(r):
    n = r.randint(1, 6)
    sw = []
    if n >= 2:
        for _ in range(r.randint(0, 4)):
            a, b = r.sample(range(n), 2)
            sw.append([a, b])
    return [[r.randint(1, 3) for _ in range(n)], [r.randint(1, 3) for _ in range(n)], sw]


def v_hamming(tests):
    for t in tests:
        s, tg, sw = t["args"]
        assert 1 <= len(s) <= 5000 and len(s) == len(tg) and len(sw) <= 5000
        assert all(0 <= x <= 100000 for x in s + tg)
        assert all(len(x) == 2 and x[0] != x[1] and 0 <= x[0] < len(s) and 0 <= x[1] < len(s) for x in sw)


CHECKS["min-hamming-distance-after-swaps"] = (b_hamming, g_hamming, "exact")
VALIDATE["min-hamming-distance-after-swaps"] = v_hamming


# ================================================================ 5. similar string groups
p = add(
    id="count-similar-string-groups", tier="common", title="Count Similar String Groups", diff="Medium", topic=TOPIC,
    fn="countSimilarGroups", params=[("words", "string")], ret="int", cmp="exact",
    desc="<p>The string <code>words</code> holds lowercase words of equal length separated by single commas, for example <code>\"tars,rats,arts,star\"</code>. Words may repeat.</p><p>Two words are <em>similar</em> if they are identical, or if exchanging exactly two letters (at two different positions) of one word turns it into the other. A <em>group</em> is a set of words in which every word is similar to at least one other word of the set, and the set cannot be extended: words are in the same group when they are linked by a chain of similar words, even if the two ends of the chain are not similar themselves.</p><p>Return the number of groups.</p><pre>\"tars,rats,arts,star\" -> 2   (tars~rats, rats~arts; star is similar to none of them)\n\"abc,abc\"            -> 1   (identical words are similar)\n\"abc,bca\"            -> 2   (they differ in all 3 positions)</pre>",
    constraints=["1 &le; number of words &le; 1,000", "All words have the same length, between 1 and 10", "Words consist of lowercase English letters"],
    hints=["Build a graph whose vertices are the words and whose edges connect similar words. You are counting its connected components.",
           "Comparing every pair costs O(w&sup2; &middot; L). Two words are similar when they differ in exactly 0 or 2 positions, and in the two positions the letters are crossed.",
           "Alternatively, for each word try all L(L-1)/2 letter exchanges and look the resulting word up in a dictionary of the input words. Union-find merges the matches."],
    editorial=["Union-find over the word indices turns the problem into counting roots. The pairwise approach checks each pair of words for similarity: collect the positions where they differ; the pair is similar if there are none, or exactly two positions <code>i, j</code> with <code>a[i] = b[j]</code> and <code>a[j] = b[i]</code>. That is O(w&sup2; L).",
               "With few words and short lengths the second approach is much faster: map every distinct word to its first index, then for each word generate all L(L-1)/2 words obtained by exchanging two letters and union the word with the index of each result that exists in the map (identical words are unioned through the map too). That costs O(w L&sup3;) with strings of length L, independent of the number of word pairs."],
    time="O(w &middot; L&sup3;)", space="O(w &middot; L)",
    solution='''def countSimilarGroups(words):
    ws = words.split(",")
    n = len(ws)
    parent = list(range(n))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb

    index = {}
    for i, w in enumerate(ws):
        if w in index:
            union(i, index[w])
        else:
            index[w] = i
    for i, w in enumerate(ws):
        if index[w] != i:
            continue
        L = len(w)
        chars = list(w)
        for a in range(L):
            for b in range(a + 1, L):
                if chars[a] == chars[b]:
                    continue
                chars[a], chars[b] = chars[b], chars[a]
                j = index.get("".join(chars))
                if j is not None:
                    union(i, j)
                chars[a], chars[b] = chars[b], chars[a]
    return sum(1 for i in range(n) if find(i) == i)
''',
    tests=[["tars,rats,arts,star"], ["abc,abc"], ["abc,bca"], ["a"], ["a,b,a"], ["ab,ba"], ["aab,aba,baa"],
           ["abcd,abdc,acbd,dbca,bacd"], ["aa,aa,aa"], ["abcde,edcba,abcde,abdce,eabcd"], ["xyz,xzy,yxz,zyx,yzx,zxy"],
           ["aabb,abab,baba,bbaa,abba,baab"]],
)


def _similar_family(r, base_count, per, extra, L, alpha):
    ws = []
    for _ in range(base_count):
        w = list(_words(r, 1, L, alpha))
        fam = ["".join(w)]
        for _ in range(per):
            x = list(r.choice(fam))
            a, b = r.randrange(L), r.randrange(L)
            x[a], x[b] = x[b], x[a]
            fam.append("".join(x))
        ws.extend(fam)
    for _ in range(extra):
        ws.append(_words(r, 1, L, alpha))
    r.shuffle(ws)
    return ",".join(ws)


_r = rnd(9105)
p["tests"].append([_similar_family(_r, 30, 14, 60, 10, "abcdefgh")])
p["tests"].append([_similar_family(_r, 80, 8, 100, 10, "abcdefghij")])
p["tests"].append([_similar_family(_r, 6, 150, 20, 8, "abcd")])
p["tests"].append([_similar_family(_r, 1, 300, 0, 10, "abcdefghij")])


def _sim(a, b):
    d = [i for i in range(len(a)) if a[i] != b[i]]
    return len(d) == 0 or (len(d) == 2 and a[d[0]] == b[d[1]] and a[d[1]] == b[d[0]])


def b_groups(words):
    ws = words.split(",")
    seen = [False] * len(ws)
    comps = 0
    for s in range(len(ws)):
        if seen[s]:
            continue
        comps += 1
        seen[s] = True
        stack = [s]
        while stack:
            u = stack.pop()
            for v in range(len(ws)):
                if not seen[v] and _sim(ws[u], ws[v]):
                    seen[v] = True
                    stack.append(v)
    return comps


def g_groups(r):
    L = r.randint(1, 4)
    return [",".join(_words(r, 1, L, "abc") for _ in range(r.randint(1, 7)))]


def v_groups(tests):
    for t in tests:
        ws = t["args"][0].split(",")
        assert 1 <= len(ws) <= 1000 and 1 <= len(ws[0]) <= 10
        assert all(len(w) == len(ws[0]) and _lower(w) for w in ws)
    assert len({t["expected"] for t in tests}) >= 5


CHECKS["count-similar-string-groups"] = (b_groups, g_groups, "exact")
VALIDATE["count-similar-string-groups"] = v_groups


# ================================================================ 6. transitively similar sequences
p = add(
    id="transitively-similar-sequences", tier="common", title="Transitively Similar Sequences", diff="Easy", topic=TOPIC,
    fn="areSequencesSimilar", params=[("a", "int[]"), ("b", "int[]"), ("pairs", "int[][]")], ret="bool", cmp="exact",
    desc="<p>Each pair <code>[x, y]</code> in <code>pairs</code> says that the values <code>x</code> and <code>y</code> are <em>similar</em>. Similarity is symmetric and <strong>transitive</strong>: if <code>x ~ y</code> and <code>y ~ z</code> then <code>x ~ z</code>. Every value is similar to itself, and values never mentioned in <code>pairs</code> are similar only to themselves.</p><p>Two sequences are similar if they have the same length and <code>a[i]</code> is similar to <code>b[i]</code> for every position <code>i</code>. Return <code>true</code> if <code>a</code> and <code>b</code> are similar sequences, otherwise <code>false</code>.</p><pre>a = [1,2,3], b = [4,5,3], pairs = [[1,6],[6,4],[2,5]]   -> true   (1~6~4, 2~5, 3=3)\na = [1,2,3], b = [4,5,9], pairs = [[1,6],[6,4],[2,5]]   -> false  (3 and 9 are unrelated)\na = [1,2],   b = [1],     pairs = []                    -> false  (different lengths)</pre>",
    constraints=["0 &le; a.length, b.length &le; 4,000 (the lengths may differ)", "0 &le; pairs.length &le; 1,500", "0 &le; a[i], b[i], pairs[i][j] &le; 1,000,000,000"],
    hints=["If the lengths differ the answer is immediately <code>false</code>. Otherwise the problem is about which values are similar.",
           "Because similarity is transitive, the values split into groups: all values linked by chains of pairs belong together.",
           "Union the two values of every pair (values can be dictionary keys), then compare <code>find(a[i])</code> with <code>find(b[i])</code> for every position."],
    editorial=["First compare the lengths. Then build equivalence classes of values with union-find keyed by value (a dictionary instead of an array, because values can be as large as 10<sup>9</sup>). Union <code>x</code> and <code>y</code> for each pair. Two values are similar exactly when they have the same root, or are equal (values never seen get their own singleton class on demand).",
               "Finally check <code>a[i] == b[i] or find(a[i]) == find(b[i])</code> for each index. Time O((n + m) &alpha;), space proportional to the number of distinct values. A DFS per query would be much slower, since a single group may have thousands of values."],
    time="O((n + m) &middot; &alpha;)", space="O(n + m)",
    solution='''def areSequencesSimilar(a, b, pairs):
    if len(a) != len(b):
        return False
    parent = {}

    def find(x):
        if x not in parent:
            parent[x] = x
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for x, y in pairs:
        rx, ry = find(x), find(y)
        if rx != ry:
            parent[rx] = ry
    for u, v in zip(a, b):
        if u != v and find(u) != find(v):
            return False
    return True
''',
    tests=[[[1, 2, 3], [4, 5, 3], [[1, 6], [6, 4], [2, 5]]],
           [[1, 2, 3], [4, 5, 9], [[1, 6], [6, 4], [2, 5]]],
           [[1, 2], [1], []],
           [[], [], []],
           [[7], [7], []],
           [[7], [8], []],
           [[7], [8], [[8, 7]]],
           [[1, 1, 2], [3, 2, 1], [[1, 2], [2, 3]]],
           [[1, 1, 2], [3, 2, 9], [[1, 2], [2, 3]]],
           [[1000000000, 0], [0, 1000000000], [[0, 1000000000]]],
           [[5, 5, 5], [6, 7, 8], [[5, 6], [7, 8], [6, 7]]],
           [[5, 5, 5], [6, 7, 9], [[5, 6], [7, 8], [6, 7]]]],
)


def _simseq_inst(r, n, vmax, m, groups_true):
    vals = list(range(vmax))
    pairs = [[r.randrange(vmax), r.randrange(vmax)] for _ in range(m)]
    par = {}

    def f(x):
        par.setdefault(x, x)
        while par[x] != x:
            par[x] = par[par[x]]
            x = par[x]
        return x
    for x, y in pairs:
        par[f(x)] = f(y)
    cls = {}
    for v in vals:
        cls.setdefault(f(v), []).append(v)
    a = [r.randrange(vmax) for _ in range(n)]
    b = [r.choice(cls[f(x)]) for x in a]
    if not groups_true:
        for _ in range(3):
            i = r.randrange(n)
            b[i] = r.randrange(vmax)
        # make sure at least one position really is dissimilar
        i = r.randrange(n)
        other = [v for v in vals if f(v) != f(a[i])]
        if other:
            b[i] = r.choice(other)
    return [a, b, pairs]


_r = rnd(9106)
p["tests"].append(_simseq_inst(_r, 3000, 1000, 600, True))
p["tests"].append(_simseq_inst(_r, 3000, 1000, 600, False))
p["tests"].append(_simseq_inst(_r, 1000, 1000, 1000, True))
p["tests"].append(_simseq_inst(_r, 30, 60, 40, True))


def b_simseq(a, b, pairs):
    if len(a) != len(b):
        return False
    vs = set(a) | set(b)
    for x, y in pairs:
        vs.add(x)
        vs.add(y)
    sim = {v: {v} for v in vs}
    for x, y in pairs:
        sim[x].add(y)
        sim[y].add(x)
    changed = True
    while changed:
        changed = False
        for v in vs:
            for w in list(sim[v]):
                new = sim[w] - sim[v]
                if new:
                    sim[v] |= new
                    changed = True
    return all(y in sim[x] for x, y in zip(a, b))


def g_simseq(r):
    n = r.randint(0, 5)
    return [[r.randint(0, 6) for _ in range(n)], [r.randint(0, 6) for _ in range(n if r.random() < 0.9 else r.randint(0, 5))],
            [[r.randint(0, 6), r.randint(0, 6)] for _ in range(r.randint(0, 6))]]


def v_simseq(tests):
    for t in tests:
        a, b, pr = t["args"]
        assert len(a) <= 4000 and len(b) <= 4000 and len(pr) <= 1500
        assert all(0 <= x <= 10 ** 9 for x in a + b)
        assert all(len(q) == 2 and 0 <= q[0] <= 10 ** 9 and 0 <= q[1] <= 10 ** 9 for q in pr)
    assert any(t["expected"] for t in tests) and any(not t["expected"] and len(t["args"][0]) == len(t["args"][1]) for t in tests)


CHECKS["transitively-similar-sequences"] = (b_simseq, g_simseq, "exact")
VALIDATE["transitively-similar-sequences"] = v_simseq


# ================================================================ 7. smallest array with value-limited swaps
p = add(
    id="smallest-array-swapping-values-within-limit", tier="common", title="Smallest Array by Limited-Gap Swaps", diff="Medium", topic=TOPIC,
    fn="smallestArrayWithLimit", params=[("nums", "int[]"), ("limit", "int")], ret="int[]", cmp="exact",
    desc="<p>You may swap two elements of <code>nums</code> (at any two different positions) whenever the absolute difference of their <strong>values</strong> is at most <code>limit</code>. You can perform any number of swaps.</p><p>Return the lexicographically smallest array that can be produced. (Array <code>x</code> is smaller than <code>y</code> if at the first position where they differ, <code>x</code> has the smaller value.)</p><pre>nums = [1,5,3,9,8], limit = 2          -> [1,3,5,8,9]\nnums = [1,7,6,18,2,1], limit = 3        -> [1,6,7,18,1,2]\nnums = [1,7,28,19,10], limit = 3        -> [1,7,28,19,10]   (no two values are close enough)</pre>",
    constraints=["1 &le; nums.length &le; 5,000", "0 &le; nums[i] &le; 1,000,000,000", "0 &le; limit &le; 1,000,000,000"],
    hints=["Which pairs of values can trade places? If 1 can swap with 3 and 3 can swap with 5, can 1 and 5 end up exchanged?",
           "Sort the values. Neighbouring values in sorted order that differ by at most <code>limit</code> are linked; a chain of such links forms a block of values that can be rearranged in any order among the positions that hold them.",
           "Sort indices by value and cut the sorted order wherever the gap exceeds <code>limit</code>. For each block, sort its positions and its values, then put the smallest value at the smallest position, and so on."],
    editorial=["Two values within <code>limit</code> can swap, and swapping along a chain of such neighbours lets any value of a block reach any position occupied by the block (just like bubble sort along a path). So the sorted values split into maximal runs where consecutive values differ by at most <code>limit</code>; values of different runs can never interact, and each run owns a fixed set of positions.",
               "Inside a run any arrangement is reachable, so the best arrangement puts the run's values in increasing order on the run's positions in increasing order, making each earlier position as small as possible. Sort the indices by value (O(n log n)), split into runs, sort the positions of each run, and write back. A union-find over the sorted order does the same job as the run split."],
    time="O(n log n)", space="O(n)",
    solution='''def smallestArrayWithLimit(nums, limit):
    n = len(nums)
    order = sorted(range(n), key=lambda i: nums[i])
    res = nums[:]
    start = 0
    for k in range(1, n + 1):
        if k == n or nums[order[k]] - nums[order[k - 1]] > limit:
            block = order[start:k]
            vals = sorted(nums[i] for i in block)
            for pos, v in zip(sorted(block), vals):
                res[pos] = v
            start = k
    return res
''',
    tests=[[[1, 5, 3, 9, 8], 2], [[1, 7, 6, 18, 2, 1], 3], [[1, 7, 28, 19, 10], 3], [[5], 0], [[3, 3, 3], 0], [[2, 1], 1],
           [[2, 1], 0], [[9, 4, 1, 0, 5, 8], 4], [[0, 1000000000], 1000000000], [[10, 12, 14, 16, 3, 1, 2], 2],
           [[7, 7, 1, 1, 4, 4], 3], [[100, 1, 50, 2, 99, 51], 1]],
)
_r = rnd(9107)
p["tests"].append([[_r.randint(0, 10 ** 9) for _ in range(2000)], 700000])
p["tests"].append([[_r.randint(0, 10 ** 9) for _ in range(2000)], 400000])
p["tests"].append([[_r.randint(0, 3000) for _ in range(2500)], 0])
p["tests"].append([[_r.randint(0, 10 ** 6) for _ in range(1500)], 1500])


def b_limit(nums, limit):
    start = tuple(nums)
    seen = {start}
    q = deque([start])
    n = len(nums)
    while q:
        cur = q.popleft()
        for i in range(n):
            for j in range(i + 1, n):
                if abs(cur[i] - cur[j]) <= limit:
                    x = list(cur)
                    x[i], x[j] = x[j], x[i]
                    x = tuple(x)
                    if x not in seen:
                        seen.add(x)
                        q.append(x)
    return list(min(seen))


def g_limit(r):
    return [[r.randint(0, 9) for _ in range(r.randint(1, 6))], r.randint(0, 3)]


def v_limit(tests):
    for t in tests:
        nums, limit = t["args"]
        assert 1 <= len(nums) <= 5000 and 0 <= limit <= 10 ** 9 and all(0 <= x <= 10 ** 9 for x in nums)
        assert sorted(t["expected"]) == sorted(nums)
    assert any(t["expected"] != t["args"][0] for t in tests)


CHECKS["smallest-array-swapping-values-within-limit"] = (b_limit, g_limit, "exact")
VALIDATE["smallest-array-swapping-values-within-limit"] = v_limit


# ================================================================ 8. count strings reachable
p = add(
    id="count-strings-reachable-by-swaps", tier="extra", title="Count Strings Reachable by Swaps", diff="Medium", topic=TOPIC,
    fn="countReachableStrings", params=[("s", "string"), ("pairs", "int[][]")], ret="int", cmp="exact",
    desc="<p>You are given a string <code>s</code> and a list <code>pairs</code> of index pairs <code>[a, b]</code> (0-indexed). For every listed pair you may swap the letters at positions <code>a</code> and <code>b</code>, any number of times, in any order, and pairs can be reused.</p><p>Count how many <strong>different strings</strong> can be obtained (the original string counts as one, and two different swap sequences that give the same string count once). Because the count can be huge, return it modulo <code>1,000,000,007</code>.</p><pre>s = \"abc\",  pairs = [[0,1],[1,2]]        -> 6   (all arrangements of a, b, c)\ns = \"abab\", pairs = [[0,1],[2,3]]        -> 4   (ab/ba for the first two letters, ab/ba for the last two)\ns = \"aab\",  pairs = [[0,1]]              -> 1   (swapping two equal letters changes nothing)\ns = \"aabb\", pairs = [[0,1],[1,2],[2,3]]  -> 6</pre>",
    constraints=["1 &le; s.length &le; 3,000", "0 &le; pairs.length &le; 3,000", "pairs[i] = [a, b] with 0 &le; a, b &lt; s.length", "s consists of lowercase English letters"],
    hints=["Letters can only move inside groups of positions linked by chains of swaps. Different groups never influence each other.",
           "Inside one group every arrangement of its letters is reachable. How many distinct arrangements does a multiset of letters have?",
           "Find the groups with union-find. For a group of size k whose letters occur c<sub>1</sub>, c<sub>2</sub>, ... times, there are k! / (c<sub>1</sub>! c<sub>2</sub>! ...) arrangements. Multiply over all groups, modulo 1,000,000,007."],
    editorial=["Positions connected through swap pairs form a group, and inside a group any permutation can be realised (a chain of adjacent swaps can move a letter anywhere along the chain). So the reachable strings are exactly all the ways to rearrange the letters inside each group independently, and the total is the product of the group counts.",
               "A group of size k containing letter counts c<sub>i</sub> has the multinomial number k! / &prod; c<sub>i</sub>! of distinct arrangements, since equal letters are indistinguishable. Precompute factorials up to n modulo p, and obtain the inverse factorials with one modular exponentiation (Fermat) followed by a downward pass. Time O((n + m) &alpha;(n) + n), space O(n)."],
    time="O((n + m) &middot; &alpha;(n))", space="O(n)",
    solution='''def countReachableStrings(s, pairs):
    MOD = 1000000007
    n = len(s)
    parent = list(range(n))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for a, b in pairs:
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb
    fact = [1] * (n + 1)
    for i in range(1, n + 1):
        fact[i] = fact[i - 1] * i % MOD
    inv = [1] * (n + 1)
    inv[n] = pow(fact[n], MOD - 2, MOD)
    for i in range(n, 0, -1):
        inv[i - 1] = inv[i] * i % MOD
    groups = {}
    for i in range(n):
        g = groups.setdefault(find(i), {})
        g[s[i]] = g.get(s[i], 0) + 1
    res = 1
    for g in groups.values():
        k = sum(g.values())
        ways = fact[k]
        for c in g.values():
            ways = ways * inv[c] % MOD
        res = res * ways % MOD
    return res
''',
    tests=[["abc", [[0, 1], [1, 2]]], ["abab", [[0, 1], [2, 3]]], ["aab", [[0, 1]]], ["aabb", [[0, 1], [1, 2], [2, 3]]],
           ["z", []], ["ab", []], ["ba", [[1, 0]]], ["abcd", [[0, 0]]], ["aaaa", [[0, 1], [1, 2], [2, 3]]],
           ["abcabc", [[0, 5], [1, 4]]], ["abcdefg", [[0, 1], [1, 2], [2, 3], [3, 4], [4, 5], [5, 6]]]],
)
_r = rnd(9108)


def _rs26(r, n, alpha):
    return "".join(r.choice(alpha) for _ in range(n))


_s = _rs26(_r, 3000, "abcdefghijklmnopqrstuvwxyz")
p["tests"].append([_s, [[i, i + 1] for i in range(0, 2999, 2)]])
p["tests"].append([_s, [[_r.randrange(3000), _r.randrange(3000)] for _ in range(1500)]])
p["tests"].append([_rs26(_r, 3000, "abc"), [[_r.randrange(3000), _r.randrange(3000)] for _ in range(1000)]])
p["tests"].append(["a" * 3000, [[i, i + 1] for i in range(2999)]])


def b_reach(s, pairs):
    seen = {s}
    q = deque([s])
    while q:
        cur = q.popleft()
        for a, b in pairs:
            x = list(cur)
            x[a], x[b] = x[b], x[a]
            x = "".join(x)
            if x not in seen:
                seen.add(x)
                q.append(x)
    return len(seen) % MOD


def g_reach(r):
    n = r.randint(1, 6)
    return ["".join(r.choice("abc") for _ in range(n)), [[r.randrange(n), r.randrange(n)] for _ in range(r.randint(0, 5))]]


def v_reach(tests):
    for t in tests:
        s, pr = t["args"]
        assert 1 <= len(s) <= 3000 and _lower(s) and len(pr) <= 3000
        assert all(len(x) == 2 and 0 <= x[0] < len(s) and 0 <= x[1] < len(s) for x in pr)
        assert 1 <= t["expected"] < MOD
    assert any(t["expected"] > 10 ** 6 for t in tests)


CHECKS["count-strings-reachable-by-swaps"] = (b_reach, g_reach, "exact")
VALIDATE["count-strings-reachable-by-swaps"] = v_reach


# ================================================================ 9. largest component by common factor
p = add(
    id="largest-component-by-common-factor", tier="extra", title="Largest Group by Common Factor", diff="Hard", topic=TOPIC,
    fn="largestComponentSize", params=[("nums", "int[]")], ret="int", cmp="exact",
    desc="<p>You are given an array <code>nums</code> of distinct positive integers. Two numbers are <em>linked</em> if they share a common divisor greater than 1 (their gcd is at least 2). Numbers are also in the same group when a chain of linked numbers connects them: if <code>a</code> is linked to <code>b</code> and <code>b</code> to <code>c</code>, then all three are in one group, even if <code>a</code> and <code>c</code> are coprime.</p><p>Return the size of the largest group. The number <code>1</code> shares no divisor above 1 with anything, so it is always alone.</p><pre>nums = [4,6,15,35]               -> 4   (4-6 via 2, 6-15 via 3, 15-35 via 5)\nnums = [20,50,9,63]              -> 2   ({20,50} via 10 and {9,63} via 9)\nnums = [2,3,6,7,4,12,21,39]      -> 8\nnums = [1,2,3]                   -> 1</pre>",
    constraints=["1 &le; nums.length &le; 5,000", "1 &le; nums[i] &le; 100,000", "All values are distinct"],
    hints=["Checking gcd for every pair is O(n&sup2;) gcd calls. Is there a better way to know which numbers are linked?",
           "Two numbers are linked exactly when they share a prime factor. So instead of linking numbers with numbers, link every number with its prime factors.",
           "Factor each number by trial division with primes up to &radic;100,000. Union-find over the number indices: remember for each prime the first index that had it, and union every later number with that index. Count the group sizes at the end."],
    editorial=["If two numbers share a common divisor d &gt; 1 they also share a prime factor of d, so linking is equivalent to sharing a prime. For every number, factorise it and, for each prime p, union the number's index with <code>owner[p]</code>, the first number seen that contained p (or record the number as owner). Numbers that contain several primes thereby glue those primes' groups together.",
               "Afterwards count the members of every root and take the maximum. Trial division by the 65 primes below 317 factorises any value up to 100,000. Total time is about O(n &middot; &pi;(&radic;V)) for factoring plus nearly linear union-find work. The pairwise-gcd method is O(n&sup2; log V) and too slow for n = 5,000."],
    time="O(n &middot; &radic;V / ln V)", space="O(n)",
    solution='''def largestComponentSize(nums):
    n = len(nums)
    small = [p for p in range(2, 317) if all(p % q for q in range(2, int(p ** 0.5) + 1))]
    parent = list(range(n))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    owner = {}

    def link(prime, i):
        if prime in owner:
            ra, rb = find(i), find(owner[prime])
            if ra != rb:
                parent[ra] = rb
        else:
            owner[prime] = i

    for i, x in enumerate(nums):
        for p in small:
            if p * p > x:
                break
            if x % p == 0:
                link(p, i)
                while x % p == 0:
                    x //= p
        if x > 1:
            link(x, i)
    cnt = {}
    best = 0
    for i in range(n):
        r = find(i)
        cnt[r] = cnt.get(r, 0) + 1
        if cnt[r] > best:
            best = cnt[r]
    return best
''',
    tests=[[[4, 6, 15, 35]], [[20, 50, 9, 63]], [[2, 3, 6, 7, 4, 12, 21, 39]], [[1, 2, 3]], [[1]], [[2]], [[97]],
           [[97, 89, 83, 79, 6, 10]], [[6, 10, 15]], [[100000, 99999, 99998, 99997, 99996, 3]],
           [[9, 25, 49, 121, 169, 3, 5, 7, 11, 13]], [[83 * 89, 89 * 97, 97 * 101, 101 * 103, 7 * 3, 3 * 5]]],
)
_r = rnd(9109)


def _primes_upto(m):
    sieve = bytearray([1]) * (m + 1)
    sieve[0:2] = b"\x00\x00"
    for i in range(2, int(m ** 0.5) + 1):
        if sieve[i]:
            sieve[i * i::i] = bytearray(len(sieve[i * i::i]))
    return [i for i in range(m + 1) if sieve[i]]


_pr = _primes_upto(100000)
_a = _r.sample(range(1, 100001), 5000)
p["tests"].append([_a])
p["tests"].append([_r.sample(_pr, 4000)])
_small = [q for q in _pr if q < 300]
_semi = sorted({a * b for a in _small for b in _small if a < b and a * b <= 100000})
_semi = _r.sample(_semi, min(len(_semi), 1500))
_big = _r.sample([q for q in _pr if q > 2000], 300)
_mix = _semi + _big
_r.shuffle(_mix)
p["tests"].append([_mix])
_a = [q * _r.choice([1, 2, 3, 5, 7]) for q in _r.sample([q for q in _pr if q < 14000], 1500)]
_a = list(dict.fromkeys(_a))
p["tests"].append([_a])


def b_comp(nums):
    from math import gcd
    n = len(nums)
    seen = [False] * n
    best = 0
    for s in range(n):
        if seen[s]:
            continue
        seen[s] = True
        st = [s]
        size = 0
        while st:
            u = st.pop()
            size += 1
            for v in range(n):
                if not seen[v] and gcd(nums[u], nums[v]) > 1:
                    seen[v] = True
                    st.append(v)
        best = max(best, size)
    return best


def g_comp(r):
    return [r.sample(range(1, 61), r.randint(1, 9))]


def v_comp(tests):
    for t in tests:
        nums = t["args"][0]
        assert 1 <= len(nums) <= 5000 and len(set(nums)) == len(nums)
        assert all(1 <= x <= 100000 for x in nums)
    assert len({t["expected"] for t in tests}) >= 5


CHECKS["largest-component-by-common-factor"] = (b_comp, g_comp, "exact")
VALIDATE["largest-component-by-common-factor"] = v_comp


# ================================================================ 10. weighted difference constraints
p = add(
    id="consistent-difference-constraints", tier="extra", title="Consistent Difference Constraints", diff="Hard", topic=TOPIC,
    fn="constraintsConsistent", params=[("n", "int"), ("constraints", "int[][]")], ret="bool", cmp="exact",
    desc="<p>There are <code>n</code> unknown integers <code>v<sub>0</sub> .. v<sub>n-1</sub></code>. Each entry <code>[a, b, d]</code> of <code>constraints</code> states that <code>v<sub>a</sub> - v<sub>b</sub> = d</code> (<code>d</code> may be negative or zero). Return <code>true</code> if values exist that satisfy <strong>every</strong> constraint simultaneously, otherwise <code>false</code>. Unmentioned variables are free. Note that <code>a</code> may equal <code>b</code>.</p><pre>n = 3, constraints = [[0,1,2],[1,2,3],[0,2,5]]   -> true   (v0 = v1+2 = v2+5)\nn = 3, constraints = [[0,1,2],[1,2,3],[0,2,4]]   -> false  (the first two force v0 - v2 = 5)\nn = 2, constraints = [[1,1,0]]                    -> true\nn = 2, constraints = [[1,1,3]]                    -> false  (v1 - v1 is always 0)</pre>",
    constraints=["1 &le; n &le; 100,000", "0 &le; constraints.length &le; 3,000", "constraints[i] = [a, b, d] with 0 &le; a, b &lt; n and -10<sup>9</sup> &le; d &le; 10<sup>9</sup>"],
    hints=["Each constraint relates two variables by a fixed offset. Variables connected through constraints form groups in which all values are determined relative to one another.",
           "Keep, for every variable, its offset from the root of its group (<code>offset[x] = v<sub>x</sub> - v<sub>root</sub></code>). Then <code>v<sub>a</sub> - v<sub>b</sub> = offset[a] - offset[b]</code> if both have the same root.",
           "Process constraints one by one with a weighted union-find. Same root: compare <code>offset[a] - offset[b]</code> with <code>d</code>. Different roots: attach one root under the other with the offset <code>d - offset[a] + offset[b]</code>. Update offsets during path compression."],
    editorial=["This is union-find with potentials. <code>diff[x]</code> stores <code>v<sub>x</sub> - v<sub>parent(x)</sub></code>; <code>find(x)</code> returns the root and, while compressing the path, replaces <code>diff[x]</code> by the offset to the root (accumulate the diffs along the path from the root downwards). Then the relation between any two variables of the same group is known.",
               "For a constraint <code>[a, b, d]</code> with roots <code>ra, rb</code>: if <code>ra == rb</code> the constraint is consistent only if <code>diff[a] - diff[b] == d</code>. Otherwise set <code>parent[ra] = rb</code> and <code>diff[ra] = d - diff[a] + diff[b]</code>, which is exactly what makes <code>v<sub>a</sub> - v<sub>b</sub> = d</code> true. Once every constraint passed, the groups can be shifted freely, so a solution exists. Time O((n + m) log n) amortised with path compression alone, and nearly linear when you also union by size. A BFS that assigns values along edges gives the same answer."],
    time="O((n + m) &middot; log n)", space="O(n)",
    solution='''def constraintsConsistent(n, constraints):
    parent = list(range(n))
    diff = [0] * n  # diff[x] = value[x] - value[parent[x]]

    def find(x):
        path = []
        while parent[x] != x:
            path.append(x)
            x = parent[x]
        root = x
        acc = 0
        for node in reversed(path):
            acc += diff[node]
            diff[node] = acc
            parent[node] = root
        return root

    for a, b, d in constraints:
        ra, rb = find(a), find(b)
        if ra == rb:
            if diff[a] - diff[b] != d:
                return False
        else:
            parent[ra] = rb
            diff[ra] = d - diff[a] + diff[b]
    return True
''',
    tests=[[3, [[0, 1, 2], [1, 2, 3], [0, 2, 5]]],
           [3, [[0, 1, 2], [1, 2, 3], [0, 2, 4]]],
           [2, [[1, 1, 0]]],
           [2, [[1, 1, 3]]],
           [1, []],
           [2, [[0, 1, 5], [1, 0, -5]]],
           [2, [[0, 1, 5], [1, 0, 5]]],
           [4, [[0, 1, 1], [2, 3, 1], [1, 2, 1], [0, 3, 3]]],
           [4, [[0, 1, 1], [2, 3, 1], [1, 2, 1], [0, 3, 2]]],
           [3, [[0, 1, 1000000000], [1, 2, -1000000000], [0, 2, 0]]],
           [5, [[4, 3, 1], [3, 2, 1], [2, 1, 1], [1, 0, 1], [4, 0, 4]]],
           [5, [[0, 1, 1], [2, 3, 7], [1, 2, 4], [4, 0, -2], [3, 4, -3]]]],
)


def _diff_inst(r, n, m, pot_max, bad):
    pot = [r.randint(-pot_max, pot_max) for _ in range(n)]
    comp = list(range(n))

    def f(x):
        while comp[x] != x:
            comp[x] = comp[comp[x]]
            x = comp[x]
        return x
    cons = []
    nodes = list(range(n))
    r.shuffle(nodes)
    # a random spanning forest first so the groups are large, then extra random constraints
    for i in range(1, min(n, m // 2)):
        a, b = nodes[i], nodes[r.randrange(i)]
        cons.append([a, b, pot[a] - pot[b]])
        comp[f(a)] = f(b)
    while len(cons) < m:
        a, b = r.randrange(n), r.randrange(n)
        cons.append([a, b, pot[a] - pot[b]])
        comp[f(a)] = f(b)
    r.shuffle(cons)
    if bad:
        groups = {}
        for i in range(n):
            groups.setdefault(f(i), []).append(i)
        big = max(groups.values(), key=len)
        a, b = r.sample(big, 2)
        cons.insert(r.randrange(len(cons) + 1), [a, b, pot[a] - pot[b] + r.choice([-1, 1])])
    return [n, cons]


_r = rnd(9110)
p["tests"].append(_diff_inst(_r, 1500, 2000, 100000, False))
p["tests"].append(_diff_inst(_r, 1500, 1500, 100000, True))
p["tests"].append(_diff_inst(_r, 3000, 1200, 1000, False))
p["tests"].append(_diff_inst(_r, 30, 60, 50, True))
p["tests"].append([2000, [[i + 1, i, 1] for i in range(1999)][::-1] + [[0, 1999, -1999]]])


def b_diff(n, cons):
    adj = [[] for _ in range(n)]
    for a, b, d in cons:
        adj[a].append((b, -d))   # v[b] = v[a] - d
        adj[b].append((a, d))    # v[a] = v[b] + d
    val = [None] * n
    for s in range(n):
        if val[s] is not None:
            continue
        val[s] = 0
        st = [s]
        while st:
            u = st.pop()
            for w, delta in adj[u]:
                if val[w] is None:
                    val[w] = val[u] + delta
                    st.append(w)
    return all(val[a] - val[b] == d for a, b, d in cons)


def g_diff(r):
    n = r.randint(1, 6)
    if r.random() < 0.5:
        pot = [r.randint(-3, 3) for _ in range(n)]
        cons = []
        for _ in range(r.randint(0, 8)):
            a, b = r.randrange(n), r.randrange(n)
            cons.append([a, b, pot[a] - pot[b]])
        if cons and r.random() < 0.4:
            cons[r.randrange(len(cons))][2] += r.choice([-1, 1])
    else:
        cons = [[r.randrange(n), r.randrange(n), r.randint(-2, 2)] for _ in range(r.randint(0, 8))]
    return [n, cons]


def v_diff(tests):
    for t in tests:
        n, cons = t["args"]
        assert 1 <= n <= 100000 and len(cons) <= 3000
        assert all(len(c) == 3 and 0 <= c[0] < n and 0 <= c[1] < n and -10 ** 9 <= c[2] <= 10 ** 9 for c in cons)
    assert any(t["expected"] for t in tests) and any(not t["expected"] for t in tests)


CHECKS["consistent-difference-constraints"] = (b_diff, g_diff, "exact")
VALIDATE["consistent-difference-constraints"] = v_diff


# ================================================================ 11. groups of strings
p = add(
    id="groups-of-strings-by-letter-sets", tier="extra", title="Groups of Strings by Letter Sets", diff="Hard", topic=TOPIC,
    fn="groupsOfStrings", params=[("words", "string")], ret="int[]", cmp="exact",
    desc="<p>The string <code>words</code> holds lowercase words separated by single commas. Inside one word every letter is different. Only the <strong>set</strong> of letters of a word matters, not their order.</p><p>Two words are <em>connected</em> if the letter set of one can be turned into the letter set of the other by exactly one of these operations:</p><ul><li>adding exactly one letter,</li><li>deleting exactly one letter,</li><li>replacing exactly one letter by any letter (including the same letter, so two words with equal letter sets are connected).</li></ul><p>A <em>group</em> consists of words linked by chains of connected words (two words are in the same group if there is a chain of connections between them). Return <code>[g, m]</code> where <code>g</code> is the number of groups and <code>m</code> is the size (number of words) of the largest group.</p><pre>\"a,b,ab,cde\"  -> [2, 3]   (a~b by replacement, a~ab and b~ab by adding a letter; cde is alone)\n\"ab,ba,abc\"   -> [1, 3]   (ab and ba have the same set; abc adds a letter)\n\"ab,cd\"       -> [2, 1]   (turning ab into cd needs two replacements)</pre>",
    constraints=["1 &le; number of words &le; 3,000", "1 &le; word length &le; 26, all letters inside a word are distinct", "Words consist of lowercase English letters"],
    hints=["Represent each word by a 26-bit mask of its letters. Which masks are connected to a given mask?",
           "Adding or deleting a letter flips one bit, so mask <code>m</code> and <code>m ^ (1 &lt;&lt; b)</code> are connected. How can you find the replacement neighbours without trying 26 &times; 26 masks?",
           "Two masks related by a replacement become equal after you delete one bit from each. For every mask and every set bit, record the 'wildcard' mask with that bit removed and union all words that produce the same wildcard mask."],
    editorial=["Convert each word to a bitmask and use union-find over the words. Words with equal masks are connected directly. Add/delete connections: for every mask <code>m</code> and each set bit <code>b</code>, if <code>m ^ (1 &lt;&lt; b)</code> is the mask of some word, union the two words.",
               "A replacement changes mask <code>m</code> into <code>m'</code> by removing one bit and adding another; so <code>m</code> and <code>m'</code> both reduce to the same mask after removing one suitable bit each. For every mask and every set bit store the reduced mask in a dictionary (as a wildcard key, separate from real masks) and union all words that share a wildcard key. This needs only O(26) operations per word instead of O(26&sup2;), for O(26 &middot; n) in total.",
               "After all unions, count the roots and the size of the largest set. Comparing all pairs would be O(n&sup2;) and also works for small inputs, but the wildcard trick is what makes the problem scale."],
    time="O(26 &middot; n)", space="O(26 &middot; n)",
    solution='''def groupsOfStrings(words):
    ws = words.split(",")
    n = len(ws)
    masks = []
    for w in ws:
        m = 0
        for c in w:
            m |= 1 << (ord(c) - 97)
        masks.append(m)
    parent = list(range(n))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb

    first = {}
    for i, m in enumerate(masks):
        if m in first:
            union(i, first[m])
        else:
            first[m] = i
    wild = {}
    for m, i in first.items():
        for b in range(26):
            if m >> b & 1:
                red = m ^ (1 << b)
                if red in first:
                    union(i, first[red])
                if red in wild:
                    union(i, wild[red])
                else:
                    wild[red] = i
    cnt = {}
    for i in range(n):
        r = find(i)
        cnt[r] = cnt.get(r, 0) + 1
    return [len(cnt), max(cnt.values())]
''',
    tests=[["a,b,ab,cde"], ["ab,ba,abc"], ["ab,cd"], ["a"], ["a,a,a"], ["abc,bcd,cde,def"], ["abc,abd,cd"],
           ["a,bc,cd,def,ghij"], ["z,y,x,w"], ["abcdefghijklmnopqrstuvwxyz,abcdefghijklmnopqrstuvwxy,bcdefghijklmnopqrstuvwxyz"],
           ["ab,ac,bc,abc,xyz,xy,yz"], ["abcd,efgh,abef,cdgh,abcdef"]],
)


def _letters_family(r, fam, size_lo, size_hi, mutations):
    alpha = "abcdefghijklmnopqrstuvwxyz"
    out = []
    for _ in range(fam):
        cur = [set(r.sample(alpha, r.randint(size_lo, size_hi)))]
        for _ in range(mutations):
            s = set(r.choice(cur))
            op = r.choice(["add", "del", "rep"])
            if op == "add" and len(s) < 26:
                s.add(r.choice([c for c in alpha if c not in s]))
            elif op == "del" and len(s) > 1:
                s.remove(r.choice(sorted(s)))
            elif len(s) < 26:
                s.remove(r.choice(sorted(s)))
                s.add(r.choice([c for c in alpha if c not in s]))
            cur.append(s)
        out.extend(cur)
    words = []
    for s in out:
        l = sorted(s)
        r.shuffle(l)
        words.append("".join(l))
    r.shuffle(words)
    return ",".join(words)


_r = rnd(9111)
p["tests"].append([_letters_family(_r, 40, 8, 16, 49)])
p["tests"].append([_letters_family(_r, 400, 3, 22, 4)])
p["tests"].append([_letters_family(_r, 3, 10, 14, 600)])


def _setsim(a, b):
    a, b = set(a), set(b)
    if a == b:
        return True
    if len(a ^ b) == 1:
        return True
    return len(a - b) == 1 and len(b - a) == 1


def b_gos(words):
    ws = words.split(",")
    seen = [False] * len(ws)
    sizes = []
    for s in range(len(ws)):
        if seen[s]:
            continue
        seen[s] = True
        st = [s]
        c = 0
        while st:
            u = st.pop()
            c += 1
            for v in range(len(ws)):
                if not seen[v] and _setsim(ws[u], ws[v]):
                    seen[v] = True
                    st.append(v)
        sizes.append(c)
    return [len(sizes), max(sizes)]


def g_gos(r):
    return [",".join("".join(r.sample("abcde", r.randint(1, 4))) for _ in range(r.randint(1, 8)))]


def v_gos(tests):
    for t in tests:
        ws = t["args"][0].split(",")
        assert 1 <= len(ws) <= 3000
        assert all(1 <= len(w) <= 26 and len(set(w)) == len(w) and _lower(w) for w in ws)
    assert len({tuple(t["expected"]) for t in tests}) >= 6


CHECKS["groups-of-strings-by-letter-sets"] = (b_gos, g_gos, "exact")
VALIDATE["groups-of-strings-by-letter-sets"] = v_gos
