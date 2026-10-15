"""Problems: strings, character counting and anagrams. See data/lib.py for the registry."""
from collections import Counter  # noqa: F401
from itertools import permutations
from functools import lru_cache

from lib import add, rnd, CHECKS, VALIDATE, gen_arr  # noqa: F401

INT_MIN, INT_MAX = -(2 ** 31), 2 ** 31 - 1
LET = "abcdefghijklmnopqrstuvwxyz"
LD = LET + "0123456789"
MOD = 10 ** 9 + 7
TOPIC = "Strings"


def _rs(r, n, alpha=LET):
    return "".join(r.choice(alpha) for _ in range(n))


def _chk(tests, idx, lo, hi, alpha=LET):
    """Every string argument number `idx` must have a length in [lo, hi] and only use `alpha`."""
    allowed = set(alpha)
    for t in tests:
        s = t["args"][idx]
        assert lo <= len(s) <= hi, ("length", len(s))
        assert set(s) <= allowed, ("alphabet", set(s) - allowed)


# ---------------------------------------------------------------- EASY

p = add(
    id="ransom-note-construct", title="Build a Note From Magazine Letters", diff="Easy", topic=TOPIC,
    fn="canBuildNote", params=[("note", "string"), ("magazine", "string")], ret="bool", cmp="exact",
    desc="<p>You want to write the text <code>note</code> by cutting single letters out of a magazine whose letters are given by the string <code>magazine</code>. Each letter of the magazine can be cut out and used <strong>at most once</strong>, and you may take letters from any position.</p><p>Return <code>true</code> if the whole note can be written, otherwise <code>false</code>.</p><pre>note = \"aab\",  magazine = \"baa\"   result = true\nnote = \"aab\",  magazine = \"ab\"    result = false\nnote = \"abc\",  magazine = \"xcbay\" result = true</pre>",
    constraints=["1 &le; note.length, magazine.length &le; 30,000", "note and magazine consist of lowercase English letters"],
    hints=["Letters are used up, so how many times each letter occurs matters, not just whether it occurs.",
           "Count how often each of the 26 letters occurs in the magazine. Then walk through the note and use up one copy for every letter.",
           "If a letter of the note has no copy left in the counts, the answer is <code>false</code>. If the walk finishes, it is <code>true</code>. Equivalently: for every letter, <code>count in note &le; count in magazine</code>."],
    editorial=["The note can be built exactly when, for every letter, the magazine contains at least as many copies as the note needs. Positions never matter, only multiplicities.",
               "Count the letters of the magazine in an array of 26 integers, then decrement the count of each note letter and fail as soon as a count would drop below zero. This is O(n + m) time and O(1) space because the alphabet is fixed. Searching the magazine for every note letter and deleting it works too but costs O(n * m)."],
    time="O(n + m)", space="O(1)",
    solution='''def canBuildNote(note, magazine):
    left = [0] * 26
    for ch in magazine:
        left[ord(ch) - 97] += 1
    for ch in note:
        k = ord(ch) - 97
        left[k] -= 1
        if left[k] < 0:
            return False
    return True
''',
    tests=[["aab", "baa"], ["aab", "ab"], ["abc", "xcbay"], ["a", "a"], ["a", "b"], ["zz", "z"], ["abcabc", "aabbcc"],
           ["abcabc", "aabbc"], ["q", "abcdefghijklmnoprstuvwxyz"], ["mmm", "mmmmm"]],
)
_r = rnd(9101)
_mag = _rs(_r, 25000)
_note = _r.sample(_mag, 15000)
p["tests"].append(["".join(_note), _mag])
_mag2 = _rs(_r, 25000, LET.replace("q", ""))
p["tests"].append(["".join(_r.sample(_mag2, 14999)) + "q", _mag2])
_m = list("a" * 10000 + "b" * 9999); _r.shuffle(_m)
_n = list("a" * 9999 + "b" * 10000); _r.shuffle(_n)
p["tests"].append(["".join(_n), "".join(_m)])


def b_ransom(note, magazine):
    pool = list(magazine)
    for ch in note:
        if ch in pool:
            pool.remove(ch)
        else:
            return False
    return True


def g_ransom(r):
    mag = _rs(r, r.randint(1, 9), "abc")
    if r.random() < 0.5:
        note = "".join(r.sample(mag, r.randint(1, len(mag))))
    else:
        note = _rs(r, r.randint(1, 8), "abc")
    return [note, mag]


def v_ransom(tests):
    _chk(tests, 0, 1, 30000)
    _chk(tests, 1, 1, 30000)
    assert any(t["expected"] for t in tests) and any(not t["expected"] for t in tests)


CHECKS["ransom-note-construct"] = (b_ransom, g_ransom, "exact")
VALIDATE["ransom-note-construct"] = v_ransom

p = add(
    id="word-pattern-bijection", title="Words Following a Pattern", diff="Easy", topic=TOPIC,
    fn="followsPattern", params=[("pattern", "string"), ("words", "string")], ret="bool", cmp="exact",
    desc="<p>The string <code>pattern</code> consists of lowercase letters. The string <code>words</code> is a list of lowercase words joined by single commas, for example <code>\"dog,cat,cat,dog\"</code> (it contains no spaces).</p><p>The words <em>follow</em> the pattern if there is a one-to-one correspondence between the letters of the pattern and the words: the <code>i</code>-th word is the word assigned to the letter <code>pattern[i]</code>, the same letter always stands for the same word, and two different letters never stand for the same word. The number of words must also equal the length of the pattern.</p><pre>pattern = \"abba\", words = \"dog,cat,cat,dog\"   result = true\npattern = \"abba\", words = \"dog,cat,cat,fish\"  result = false\npattern = \"abba\", words = \"dog,dog,dog,dog\"   result = false\npattern = \"aaa\",  words = \"go,go\"             result = false</pre>",
    constraints=["1 &le; pattern.length &le; 3,000", "pattern consists of lowercase letters", "words is 1 or more lowercase words of length 1 to 8, separated by single commas"],
    hints=["First compare the number of words with the length of the pattern.",
           "Letters of the pattern must always meet the same word. But that alone is not enough: <code>\"ab\"</code> with <code>\"go,go\"</code> passes it.",
           "Keep two dictionaries, letter &rarr; word and word &rarr; letter. When you see a pair, both dictionaries must agree with it (or be new)."],
    editorial=["Split the word list on commas. If the count differs from the pattern length the answer is false. Then scan the two sequences in parallel and keep a map from letters to words and a map from words back to letters. A pair <code>(c, w)</code> is consistent when <code>c</code> is unmapped or already mapped to <code>w</code>, and <code>w</code> is unmapped or already mapped back to <code>c</code>.",
               "This is the same bijection check as for isomorphic strings, but one side consists of whole words. An equivalent trick replaces every symbol by the index of its first occurrence and compares the two index sequences. Both run in time linear in the input size."],
    time="O(n + total word length)", space="O(n)",
    solution='''def followsPattern(pattern, words):
    ws = words.split(",")
    if len(ws) != len(pattern):
        return False
    fwd, back = {}, {}
    for c, w in zip(pattern, ws):
        if fwd.setdefault(c, w) != w or back.setdefault(w, c) != c:
            return False
    return True
''',
    tests=[["abba", "dog,cat,cat,dog"], ["abba", "dog,cat,cat,fish"], ["abba", "dog,dog,dog,dog"], ["aaa", "go,go"],
           ["a", "x"], ["ab", "go,go"], ["ab", "go,no"], ["abc", "x,y"], ["abc", "z,y,x"], ["aaaa", "ab,ab,ab,ab"],
           ["abab", "up,down,up,down"], ["abab", "up,down,up,up"]],
)
_r = rnd(9102)
_pat = _rs(_r, 3000)
_vocab = set()
while len(_vocab) < 26:
    _vocab.add(_rs(_r, _r.randint(3, 6)))
_vocab = list(_vocab)
_mp = dict(zip(LET, _vocab))
_w = [_mp[c] for c in _pat]
p["tests"].append([_pat, ",".join(_w)])
_w2 = list(_w)
_i = 1500
_other = [c for c in LET if c != _pat[_i]][0]
_w2[_i] = _mp[_other]
p["tests"].append([_pat, ",".join(_w2)])
p["tests"].append(["a" * 3000, ",".join(["tok"] * 3000)])
p["tests"].append([_pat, ",".join(_w[:-1])])


def b_wp(pattern, words):
    ws = words.split(",")

    def norm(seq):
        return [seq.index(x) for x in seq]
    return len(ws) == len(pattern) and norm(list(pattern)) == norm(ws)


def g_wp(r):
    n = r.randint(1, 6)
    pat = _rs(r, n, "abc")
    k = n if r.random() < 0.85 else r.randint(1, 6)
    if r.random() < 0.5:
        m = {c: w for c, w in zip("abc", r.sample(["x", "yy", "zz", "w"], 3))}
        ws = [m[pat[i % n]] for i in range(k)]
        if r.random() < 0.3:
            ws[r.randrange(k)] = r.choice(["x", "yy", "zz", "w"])
    else:
        ws = [r.choice(["x", "yy", "zz"]) for _ in range(k)]
    return [pat, ",".join(ws)]


def v_wp(tests):
    _chk(tests, 0, 1, 3000)
    for t in tests:
        ws = t["args"][1].split(",")
        assert all(1 <= len(w) <= 8 and set(w) <= set(LET) for w in ws)
    assert any(t["expected"] for t in tests) and any(not t["expected"] for t in tests)


CHECKS["word-pattern-bijection"] = (b_wp, g_wp, "exact")
VALIDATE["word-pattern-bijection"] = v_wp

p = add(
    id="buddy-strings-swap-check", title="One Swap to Match", diff="Easy", topic=TOPIC, tier="extra",
    fn="matchAfterOneSwap", params=[("s", "string"), ("goal", "string")], ret="bool", cmp="exact",
    desc="<p>You must swap the letters at <strong>exactly one</strong> pair of different positions <code>i &lt; j</code> of the string <code>s</code> (you are not allowed to skip the swap, but the two swapped letters may be equal). Return <code>true</code> if the result can equal the string <code>goal</code>.</p><pre>s = \"ab\",   goal = \"ba\"    result = true\ns = \"ab\",   goal = \"ab\"    result = false  (a swap changes it)\ns = \"aab\",  goal = \"aab\"   result = true   (swap the two a's)\ns = \"abc\",  goal = \"acd\"   result = false</pre>",
    constraints=["1 &le; s.length, goal.length &le; 20,000", "s and goal consist of lowercase letters and digits"],
    hints=["Different lengths can never match. Then think about where <code>s</code> and <code>goal</code> differ.",
           "If they differ in exactly two positions, the swap must exchange those two letters. If they differ in one place, or in three or more, a single swap cannot repair them.",
           "If the strings are already equal, the forced swap must not change anything, which is only possible when some letter occurs twice."],
    editorial=["Split into cases by the set of positions where the strings differ. With exactly two differing positions <code>a &lt; b</code>, the swap fixes the strings iff <code>s[a] == goal[b]</code> and <code>s[b] == goal[a]</code>. With exactly one differing position, no swap works (a swap changes two positions, or none). With three or more differing positions, one swap cannot repair them all.",
               "With zero differing positions the swap has to leave <code>s</code> unchanged, which means swapping two equal letters, so we need a repeated letter. Since only 36 symbols exist, any string longer than 36 characters certainly has a repeat. Everything is one linear pass."],
    time="O(n)", space="O(1)",
    solution='''def matchAfterOneSwap(s, goal):
    if len(s) != len(goal):
        return False
    diff = [i for i in range(len(s)) if s[i] != goal[i]]
    if not diff:
        return len(set(s)) < len(s)
    if len(diff) != 2:
        return False
    a, b = diff
    return s[a] == goal[b] and s[b] == goal[a]
''',
    tests=[["ab", "ba"], ["ab", "ab"], ["aab", "aab"], ["abc", "acd"], ["a", "a"], ["a", "b"], ["abc", "abc"],
           ["abcd", "badc"], ["abcd", "abdc"], ["abc", "ab"], ["aabb", "abab"], ["0123456789", "0123456798"]],
)
_r = rnd(9103)
_s = _rs(_r, 20000, LD)
p["tests"].append([_s, _s])
_t = list(_s); _t[100], _t[19000] = _t[19000], _t[100]
if _t[100] == _s[100]:
    _t[100] = "z" if _s[100] != "z" else "y"
p["tests"].append([_s, "".join(_t)])
_t = list(_s); _t[5], _t[6] = (_t[6], _t[5]) if _t[5] != _t[6] else ("0", "1")
_t[7] = "z" if _s[7] != "z" else "y"
p["tests"].append([_s, "".join(_t)])


def b_buddy(s, goal):
    if len(s) != len(goal):
        return False
    n = len(s)
    for i in range(n):
        for j in range(i + 1, n):
            t = list(s)
            t[i], t[j] = t[j], t[i]
            if "".join(t) == goal:
                return True
    return False


def g_buddy(r):
    s = _rs(r, r.randint(1, 6), "abc")
    m = r.random()
    if m < 0.5 and len(s) >= 2:
        i, j = r.sample(range(len(s)), 2)
        t = list(s); t[i], t[j] = t[j], t[i]
        g = "".join(t)
    elif m < 0.7:
        g = s
    else:
        g = _rs(r, len(s) if r.random() < 0.85 else r.randint(1, 6), "abc")
    return [s, g]


def v_buddy(tests):
    _chk(tests, 0, 1, 20000, LD)
    _chk(tests, 1, 1, 20000, LD)
    assert any(t["expected"] for t in tests) and any(not t["expected"] for t in tests)


CHECKS["buddy-strings-swap-check"] = (b_buddy, g_buddy, "exact")
VALIDATE["buddy-strings-swap-check"] = v_buddy

# ---------------------------------------------------------------- MEDIUM

p = add(
    id="group-anagram-sizes", title="Sizes of Anagram Groups", diff="Medium", topic=TOPIC, tier="must",
    fn="anagramGroupSizes", params=[("words", "string")], ret="int[]", cmp="exact",
    desc="<p>The string <code>words</code> is a list of lowercase words joined by single commas, for example <code>\"eat,tea,tan\"</code> (no spaces). Two words are <em>anagrams</em> if one can be rearranged into the other, i.e. they contain the same letters with the same multiplicities. Words that are equal are anagrams of each other too, and equal words in the list are counted separately.</p><p>Put the words into groups so that each group consists of mutually anagram words and no two groups could be merged. Return the sizes of all groups as an array in <strong>non-increasing</strong> order.</p><pre>words = \"eat,tea,tan,ate,nat,bat\"   result = [3, 2, 1]\nwords = \"a,a,a\"                     result = [3]\nwords = \"ab,abc,ba,cab,c\"           result = [2, 2, 1]</pre>",
    constraints=["1 &le; number of words &le; 5,000", "each word has 1 to 20 lowercase letters", "the words are separated by single commas"],
    hints=["Comparing every pair of words with a letter count is too slow for 5,000 words. Look for something that is identical for all words of a group.",
           "Two words are anagrams exactly when their sorted letters are the same string, or when their 26 letter counts are the same.",
           "Use the sorted word (or the tuple of 26 counts) as a dictionary key and count how many words share each key. Then sort the counts in decreasing order."],
    editorial=["Anagram-ness is an equivalence relation, so words fall into disjoint groups, and a canonical key identifies the group: the word with its letters sorted, or the tuple of 26 letter counts. Walk through the words, increment a counter for each word's key, and finally sort the counter values from large to small.",
               "With words of length at most L, building a key costs O(L log L) by sorting or O(L + 26) by counting, so the whole algorithm is O(total length * log L + g log g) where g is the number of groups. The pairwise-comparison alternative is O(w&sup2;) letter comparisons for w words and is far too slow."],
    time="O(T log L + g log g)", space="O(T)",
    solution='''def anagramGroupSizes(words):
    groups = {}
    for w in words.split(","):
        key = "".join(sorted(w))
        groups[key] = groups.get(key, 0) + 1
    return sorted(groups.values(), reverse=True)
''',
    tests=[["eat,tea,tan,ate,nat,bat"], ["a,a,a"], ["ab,abc,ba,cab,c"], ["a"], ["a,b,c"], ["ab,ba"], ["abc,abd,abe"],
           ["listen,silent,enlist,google,gogole,cat,act,tac,dog"], ["aab,aba,baa,abb,bab,bba,aab"], ["zz,zz,z,zzz,zz"]],
)
_r = rnd(9104)
_ws = []
for _ in range(700):
    _base = _rs(_r, _r.randint(3, 9))
    for _ in range(_r.randint(1, 12)):
        _l = list(_base); _r.shuffle(_l)
        _ws.append("".join(_l))
_r.shuffle(_ws)
_ws = _ws[:3000]
p["tests"].append([",".join(_ws)])
p["tests"].append([",".join(_rs(_r, 8) for _ in range(2000))])
p["tests"].append([",".join(_rs(_r, _r.randint(1, 10), "ab") for _ in range(5000))])
p["tests"].append([",".join(["a" * 20] * 800 + ["a" * 19 + "b"] * 700 + ["b" + "a" * 19] * 700)])


def b_group(words):
    reps, sizes = [], []
    for w in words.split(","):
        for i, rep in enumerate(reps):
            if sorted(rep) == sorted(w):
                sizes[i] += 1
                break
        else:
            reps.append(w)
            sizes.append(1)
    sizes.sort(reverse=True)
    return sizes


def g_group(r):
    k = r.randint(1, 8)
    return [",".join(_rs(r, r.randint(1, 3), "abc") for _ in range(k))]


def v_group(tests):
    for t in tests:
        ws = t["args"][0].split(",")
        assert 1 <= len(ws) <= 5000
        assert all(1 <= len(w) <= 20 and set(w) <= set(LET) for w in ws)
        assert t["expected"] == sorted(t["expected"], reverse=True) and sum(t["expected"]) == len(ws)


CHECKS["group-anagram-sizes"] = (b_group, g_group, "exact")
VALIDATE["group-anagram-sizes"] = v_group

p = add(
    id="min-steps-to-make-anagram", title="Replacements to Form an Anagram", diff="Medium", topic=TOPIC,
    fn="minReplacements", params=[("s", "string"), ("t", "string")], ret="int", cmp="exact",
    desc="<p>The strings <code>s</code> and <code>t</code> have the same length. In one step you may pick any position of <code>t</code> and replace its letter by any other lowercase letter. Return the minimum number of steps needed so that <code>t</code> becomes an <em>anagram</em> of <code>s</code> (it contains exactly the same letters as <code>s</code>, in any order).</p><pre>s = \"friend\",  t = \"family\"   result = 4\ns = \"anagram\", t = \"mangaar\"  result = 0\ns = \"aab\",     t = \"bbb\"      result = 2</pre>",
    constraints=["1 &le; s.length &le; 20,000", "t.length == s.length", "s and t consist of lowercase English letters"],
    hints=["The order of the letters of <code>t</code> is irrelevant, only how many copies of each letter it has.",
           "A letter that <code>t</code> already has in the right amount needs no change. Which letters of <code>t</code> are surplus, and which letters are missing?",
           "For every letter the surplus is <code>max(0, count_t - count_s)</code>. Each replacement turns one surplus letter into one missing letter, so the answer is the sum of all surplus values."],
    editorial=["Let <code>cs[c]</code> and <code>ct[c]</code> be the letter counts. For each letter with <code>ct[c] &gt; cs[c]</code>, the extra <code>ct[c] - cs[c]</code> copies in <code>t</code> are surplus; for each letter with <code>ct[c] &lt; cs[c]</code> copies are missing. Since both strings have the same length, total surplus equals total missing.",
               "Each step can fix at most one surplus letter (changing it to a missing one), and one step per surplus letter always suffices, so the minimum is the total surplus. This takes O(n) time with two arrays of 26 counters."],
    time="O(n)", space="O(1)",
    solution='''def minReplacements(s, t):
    cnt = [0] * 26
    for ch in s:
        cnt[ord(ch) - 97] += 1
    for ch in t:
        cnt[ord(ch) - 97] -= 1
    return sum(x for x in cnt if x > 0)
''',
    tests=[["friend", "family"], ["anagram", "mangaar"], ["aab", "bbb"], ["a", "a"], ["a", "b"], ["ab", "ba"],
           ["abc", "ddd"], ["aaaa", "bbbb"], ["abcabc", "cbacba"], ["xyz", "xyy"], ["leetcode", "practice"]],
)
_r = rnd(9105)
_s = _rs(_r, 20000)
_t = list(_s); _r.shuffle(_t)
p["tests"].append([_s, "".join(_t)])
p["tests"].append([_s, _rs(_r, 20000)])
p["tests"].append(["a" * 10000 + "b" * 10000, "b" * 14000 + "c" * 6000])


def b_steps(s, t):
    pool = list(s)
    wrong = 0
    for ch in t:
        if ch in pool:
            pool.remove(ch)
        else:
            wrong += 1
    return wrong


def g_steps(r):
    n = r.randint(1, 9)
    return [_rs(r, n, "abcd"), _rs(r, n, "abcd")]


def v_steps(tests):
    for t in tests:
        assert len(t["args"][0]) == len(t["args"][1])
    _chk(tests, 0, 1, 20000)
    _chk(tests, 1, 1, 20000)


CHECKS["min-steps-to-make-anagram"] = (b_steps, g_steps, "exact")
VALIDATE["min-steps-to-make-anagram"] = v_steps

p = add(
    id="sort-letters-by-frequency", title="Sort Letters by Frequency", diff="Medium", topic=TOPIC,
    fn="sortByFrequency", params=[("s", "string")], ret="string", cmp="exact",
    desc="<p>Rearrange the letters of <code>s</code> so that letters that occur more often come first. All copies of a letter must stay together in one block. If two letters occur equally often, the alphabetically smaller letter comes first, so the answer is unique. Return the rearranged string.</p><pre>s = \"tree\"      result = \"eert\"\ns = \"cccaaa\"    result = \"aaaccc\"\ns = \"abbcccd\"   result = \"cccbbad\"</pre>",
    constraints=["1 &le; s.length &le; 20,000", "s consists of lowercase English letters"],
    hints=["Whatever order you choose, the letters of one kind must form one contiguous block, so you really only order the 26 kinds.",
           "Count the occurrences of each letter, then order the letters by (count descending, letter ascending).",
           "Build the answer by repeating each letter as many times as it occurred, in that order. Sorting 26 items is cheap; the string building dominates."],
    editorial=["Count the letters (26 counters). The output is determined by the order of the kinds: sort the present letters by the key <code>(-count, letter)</code>, then write each letter <code>count</code> times. Sorting the whole string character by character with a custom key gives the same result at O(n log n), but sorting only 26 kinds is O(n + 26 log 26).",
               "If the alphabet were large, a bucket sort over counts (bucket <code>k</code> holds the letters occurring exactly <code>k</code> times) would keep the whole thing linear."],
    time="O(n)", space="O(n)",
    solution='''def sortByFrequency(s):
    cnt = [0] * 26
    for ch in s:
        cnt[ord(ch) - 97] += 1
    order = sorted((i for i in range(26) if cnt[i]), key=lambda i: (-cnt[i], i))
    return "".join(chr(97 + i) * cnt[i] for i in order)
''',
    tests=[["tree"], ["cccaaa"], ["abbcccd"], ["a"], ["z"], ["ab"], ["ba"], ["aabb"], ["zzzyyx"], ["abcdefghijklmnopqrstuvwxyz"],
           ["mississippi"]],
)
_r = rnd(9106)
p["tests"].append([_rs(_r, 20000)])
_w = [_r.random() ** 3 for _ in range(26)]
p["tests"].append(["".join(_r.choices(LET, weights=_w, k=15000))])
p["tests"].append(["".join(c * (i + 1) * 40 for i, c in enumerate(LET))[::-1]])


def b_sortfreq(s):
    return "".join(sorted(s, key=lambda ch: (-s.count(ch), ch)))


def g_sortfreq(r):
    return [_rs(r, r.randint(1, 12), "abcde")]


def v_sortfreq(tests):
    _chk(tests, 0, 1, 20000)


CHECKS["sort-letters-by-frequency"] = (b_sortfreq, g_sortfreq, "exact")
VALIDATE["sort-letters-by-frequency"] = v_sortfreq

p = add(
    id="equal-frequency-after-one-removal", title="Equal Frequencies After One Removal", diff="Medium", topic=TOPIC,
    fn="equalAfterRemoval", params=[("s", "string")], ret="bool", cmp="exact",
    desc="<p>You must delete <strong>exactly one</strong> character (any position) from the string <code>s</code>. Return <code>true</code> if it is possible to do this so that every letter that is still present in the remaining string occurs the <em>same number of times</em>.</p><pre>s = \"abcc\"     result = true   (delete one c: a, b, c occur once)\ns = \"aazz\"     result = false  (every deletion leaves counts 1 and 2)\ns = \"aabbbcc\"  result = true   (delete one b)\ns = \"ab\"       result = true   (one letter is left)</pre>",
    constraints=["2 &le; s.length &le; 50,000", "s consists of lowercase English letters"],
    hints=["Only the 26 letter counts matter. A deletion lowers one of those counts by one.",
           "There are at most 26 different deletions that change the counts (one per present letter). Try each of them and test whether the remaining nonzero counts are all equal.",
           "Testing one candidate costs O(26), so the whole answer is O(n + 26 * 26). Remember that a count of 1 drops to 0 and that letter then no longer counts."],
    editorial=["Deleting a character only matters through its letter, so at most 26 distinct deletions exist. Count the letters once. For every present letter, decrement its count, check whether all nonzero counts are identical (a set of the nonzero counts has at most one element), and restore it. If any candidate passes, the answer is true.",
               "This is O(n + 26&sup2;). One can also reason by cases (a single letter with count 1, all counts equal to 1, one letter exceeding the common count by exactly one), but the brute force over letters is shorter and harder to get wrong. Note that the deletion is mandatory: a string that already has equal counts, like <code>\"aabb\"</code>, still has to lose a character."],
    time="O(n)", space="O(1)",
    solution='''def equalAfterRemoval(s):
    cnt = [0] * 26
    for ch in s:
        cnt[ord(ch) - 97] += 1
    for i in range(26):
        if cnt[i] == 0:
            continue
        cnt[i] -= 1
        if len({c for c in cnt if c}) <= 1:
            return True
        cnt[i] += 1
    return False
''',
    tests=[["abcc"], ["aazz"], ["aabbbcc"], ["ab"], ["aa"], ["aabb"], ["abc"], ["aaabbb"], ["abbcc"], ["bbbbcc"], ["aabbcd"]],
)
_r = rnd(9107)


def _by_counts(r, counts):
    letters = r.sample(LET, len(counts))
    chars = [ch for ch, c in zip(letters, counts) for _ in range(c)]
    r.shuffle(chars)
    return "".join(chars)


p["tests"].append([_by_counts(_r, [1900] * 25 + [1901])])      # one letter exceeds by one -> true
p["tests"].append([_by_counts(_r, [1900] * 24 + [1901, 1902])])  # false
p["tests"].append([_by_counts(_r, [1] + [200] * 24)])          # a lone letter -> true
p["tests"].append([_by_counts(_r, [199] + [200] * 24 + [201])])   # false


def b_eqfreq(s):
    for i in range(len(s)):
        t = s[:i] + s[i + 1:]
        if len(set(Counter(t).values())) <= 1:
            return True
    return False


def g_eqfreq(r):
    if r.random() < 0.5:
        base = r.randint(1, 3)
        counts = [base] * r.randint(1, 4)
        if r.random() < 0.7:
            counts[r.randrange(len(counts))] += r.choice([-1, 1, 1, 2])
        counts = [max(1, c) for c in counts]
        s = _by_counts(r, counts)
        if len(s) < 2:
            s += "a"
        return [s]
    return [_rs(r, r.randint(2, 9), "abc")]


def v_eqfreq(tests):
    _chk(tests, 0, 2, 50000)
    assert any(t["expected"] for t in tests) and any(not t["expected"] for t in tests)


CHECKS["equal-frequency-after-one-removal"] = (b_eqfreq, g_eqfreq, "exact")
VALIDATE["equal-frequency-after-one-removal"] = v_eqfreq

p = add(
    id="min-length-of-anagram-concatenation", title="Shortest Base Word of Anagram Chunks", diff="Medium", topic=TOPIC,
    fn="shortestBaseLength", params=[("s", "string")], ret="int", cmp="exact",
    desc="<p>The string <code>s</code> is known to be built by writing down one or more strings, each of which is an anagram of the same base word <code>t</code>, and concatenating them. For example <code>\"abbaab\"</code> is <code>\"ab\" + \"ba\" + \"ab\"</code>, so <code>t</code> could be <code>\"ab\"</code>.</p><p>Return the smallest possible length of <code>t</code>.</p><pre>s = \"abba\"     result = 2   (\"ab\" + \"ba\")\ns = \"cdef\"     result = 4   (only t = s itself works)\ns = \"aaaa\"     result = 1\ns = \"abcbca\"   result = 3   (\"abc\" + \"bca\")</pre>",
    constraints=["1 &le; s.length &le; 40,000", "s consists of lowercase English letters"],
    hints=["If the chunk length is <code>L</code>, then <code>L</code> must divide <code>n</code>, and every chunk of length <code>L</code> must have the same letter counts as the first one.",
           "Instead of trying all lengths, count each letter in the whole string. If there are <code>k</code> chunks, every letter count must be divisible by <code>k</code>.",
           "Let <code>g</code> be the gcd of all letter counts. Only chunk counts <code>k</code> that divide <code>g</code> can work. Try them from the largest to the smallest (shortest chunks first) and verify with sorted chunks; <code>k = 1</code> always works."],
    editorial=["Suppose the string is split into <code>k</code> chunks of length <code>L = n / k</code>, all with the same letter counts. Then each letter's total count equals <code>k</code> times its count in a chunk, so <code>k</code> divides every letter's total count and therefore their gcd <code>g</code>. This leaves only the divisors of <code>g</code> as candidate chunk counts; the shortest base word corresponds to the largest valid <code>k</code>.",
               "For each candidate <code>k</code> in decreasing order, compare every chunk, as a sorted string or a count array, with the first chunk and stop at the first mismatch. The first valid <code>k</code> gives the answer <code>n / k</code>. The check is O(n) per candidate, and the number of divisors of <code>g</code> is small. The naive solution tries every divisor of <code>n</code> instead and is slower but the same idea."],
    time="O(n * d(g))", space="O(n)",
    solution='''from math import gcd
from collections import Counter


def shortestBaseLength(s):
    n = len(s)
    g = 0
    for v in Counter(s).values():
        g = gcd(g, v)
    for k in range(g, 0, -1):
        if g % k:
            continue
        size = n // k
        base = sorted(s[:size])
        if all(sorted(s[i:i + size]) == base for i in range(size, n, size)):
            return size
    return n
''',
    tests=[["abba"], ["cdef"], ["aaaa"], ["abcbca"], ["a"], ["ab"], ["abab"], ["aabb"], ["abcabcabc"], ["abcbcacab"], ["aaabbb"],
           ["xyzzyxyxz"]],
)
_r = rnd(9108)


def _chunks(r, base, k):
    out = []
    for _ in range(k):
        l = list(base); r.shuffle(l)
        out.append("".join(l))
    return "".join(out)


p["tests"].append([_chunks(_r, _rs(_r, 40), 1000)])
p["tests"].append([_chunks(_r, _rs(_r, 2, "ab") + "ab" * 4, 600)])
p["tests"].append(["a" * 10000 + "b" * 10000])
_x = _chunks(_r, _rs(_r, 100), 80)
p["tests"].append([_x[:-1] + ("a" if _x[-1] != "a" else "b")])


def b_minbase(s):
    n = len(s)
    for L in range(1, n + 1):
        if n % L == 0:
            first = sorted(s[:L])
            if all(sorted(s[i:i + L]) == first for i in range(0, n, L)):
                return L


def g_minbase(r):
    if r.random() < 0.6:
        base = _rs(r, r.randint(1, 4), "abc")
        return [_chunks(r, base, r.randint(1, 4))]
    return [_rs(r, r.randint(1, 9), "ab")]


def v_minbase(tests):
    _chk(tests, 0, 1, 40000)
    assert any(t["expected"] < len(t["args"][0]) for t in tests)


CHECKS["min-length-of-anagram-concatenation"] = (b_minbase, g_minbase, "exact")
VALIDATE["min-length-of-anagram-concatenation"] = v_minbase

p = add(
    id="min-deletions-frequency-spread-at-most-k", title="Deletions for Balanced Letter Counts", diff="Medium", topic=TOPIC, tier="extra",
    fn="minDeletionsBalanced", params=[("s", "string"), ("k", "int")], ret="int", cmp="exact",
    desc="<p>Call a string <em>k-balanced</em> if for any two letters <strong>that occur in it</strong>, the difference between their numbers of occurrences is at most <code>k</code>. (A string with at most one distinct letter, including the empty string, is always k-balanced.)</p><p>You may delete characters from <code>s</code> (any positions). Return the minimum number of deletions that make <code>s</code> k-balanced.</p><pre>s = \"aabcaba\", k = 0   result = 3   (counts a=4 b=2 c=1: delete c and two a's, leaving a=2 b=2)\ns = \"aabcaba\", k = 3   result = 0\ns = \"aaabbc\",  k = 1   result = 1   (a=3 b=2 c=1: delete one a)</pre>",
    constraints=["1 &le; s.length &le; 30,000", "0 &le; k &le; s.length", "s consists of lowercase English letters"],
    hints=["Only the letter counts matter. After the deletions each remaining letter keeps some number of copies between its original count and 0 (0 meaning the letter vanishes).",
           "Fix the smallest count <code>m</code> that a remaining letter will have. Then each remaining letter keeps between <code>m</code> and <code>m + k</code> copies, and it is never useful to keep fewer than allowed.",
           "Try every distinct original count as <code>m</code>. A letter with count <code>c &lt; m</code> must disappear (cost <code>c</code>); a letter with <code>c &gt; m + k</code> is trimmed to <code>m + k</code> (cost <code>c - m - k</code>); others cost nothing. Take the minimum over all <code>m</code>."],
    editorial=["Let <code>m</code> be the smallest frequency among the letters that survive. The smallest surviving frequency can be taken equal to one of the original counts (keeping a letter at exactly its original count is never worse than lowering it). For this <code>m</code>, every letter with an original count below <code>m</code> has to be deleted completely, every letter above <code>m + k</code> loses exactly its excess over <code>m + k</code>, and every letter in between is untouched. The cost is the sum of these.",
               "Evaluate the formula for each of at most 26 candidate values <code>m</code> and return the minimum. This runs in O(n + 26&sup2;). Deleting everything is never better than keeping the most frequent letter, so no extra case is needed."],
    time="O(n + 26^2)", space="O(1)",
    solution='''from collections import Counter


def minDeletionsBalanced(s, k):
    counts = list(Counter(s).values())
    best = len(s)
    for m in set(counts):
        cost = 0
        for c in counts:
            if c < m:
                cost += c
            elif c > m + k:
                cost += c - m - k
        best = min(best, cost)
    return best
''',
    tests=[["aabcaba", 0], ["aabcaba", 3], ["aaabbc", 1], ["a", 0], ["ab", 0], ["aab", 0], ["aab", 1], ["abcabc", 0],
           ["aaaaabbbc", 1], ["aaaaabbbc", 2], ["zzzzzzzzzzy", 3], ["abcdefghij", 0]],
)
_r = rnd(9109)
p["tests"].append([_rs(_r, 30000), 100])
_w = [_r.random() ** 3 for _ in range(26)]
p["tests"].append(["".join(_r.choices(LET, weights=_w, k=30000)), 300])
p["tests"].append(["".join(c * (i * 100 + 5) for i, c in enumerate(LET[:15])), 250])


def b_balanced(s, k):
    letters = sorted(set(s))
    cnt = [s.count(c) for c in letters]
    best = len(s)

    def rec(i, kept, lo, hi):
        nonlocal best
        if i == len(cnt):
            best = min(best, len(s) - kept)
            return
        rec(i + 1, kept, lo, hi)  # delete the letter completely
        for keep in range(1, cnt[i] + 1):
            nlo, nhi = min(lo, keep), max(hi, keep)
            if nhi - nlo <= k:
                rec(i + 1, kept + keep, nlo, nhi)

    rec(0, 0, 10 ** 9, -1)
    return best


def g_balanced(r):
    return [_rs(r, r.randint(1, 10), "abcd"), r.randint(0, 4)]


def v_balanced(tests):
    _chk(tests, 0, 1, 30000)
    for t in tests:
        assert 0 <= t["args"][1] <= len(t["args"][0])


CHECKS["min-deletions-frequency-spread-at-most-k"] = (b_balanced, g_balanced, "exact")
VALIDATE["min-deletions-frequency-spread-at-most-k"] = v_balanced

# ---------------------------------------------------------------- HARD

p = add(
    id="rank-of-string-in-distinct-permutations", title="Rank Among Distinct Rearrangements", diff="Hard", topic=TOPIC, tier="extra",
    fn="rearrangementRank", params=[("s", "string")], ret="int", cmp="exact",
    desc="<p>List all <em>distinct</em> strings that can be made by rearranging the letters of <code>s</code>, in dictionary order (a repeated rearrangement is listed once). The <em>rank</em> of <code>s</code> is its 1-based position in this list.</p><p>The rank can be astronomically large, so return it modulo <code>1,000,000,007</code>.</p><pre>s = \"aba\"    result = 2   (aab, aba, baa)\ns = \"bca\"    result = 4   (abc, acb, bac, bca, cab, cba)\ns = \"aab\"    result = 1\ns = \"baa\"    result = 3</pre>",
    constraints=["1 &le; s.length &le; 3,000", "s consists of lowercase English letters", "the answer is reported modulo 1,000,000,007"],
    hints=["Count how many rearrangements come before <code>s</code>. They are the ones that agree with <code>s</code> on a prefix and then have a smaller letter at the next position.",
           "At position <code>i</code>, for each letter <code>c &lt; s[i]</code> that is still unused, count the rearrangements of the remaining letters that start with <code>c</code>. That is a multinomial coefficient: <code>(m-1)! / prod(cnt!)</code> with <code>cnt[c]</code> reduced by one.",
           "Keep <code>1 / prod(cnt[x]!)</code> as a running value modulo the prime. Starting with <code>c</code> multiplies it by <code>cnt[c] * (m-1)!</code>, so all smaller letters together contribute <code>(m-1)! * inv * (number of remaining letters smaller than s[i])</code>. After moving on, multiply <code>inv</code> by <code>cnt[s[i]]</code> and decrement that count."],
    editorial=["A rearrangement comes before <code>s</code> exactly when for some position <code>i</code> it matches <code>s</code> on positions before <code>i</code> and has a smaller letter at position <code>i</code>. For a fixed <code>i</code>, with <code>m = n - i</code> letters remaining and counts <code>cnt</code>, the number of distinct arrangements of the remaining letters that start with the letter <code>c</code> is <code>(m-1)! / (prod cnt[x]!) * cnt[c]</code>.",
               "Summing over all <code>c &lt; s[i]</code> gives <code>(m-1)! * inv * (sum of cnt[c] over c &lt; s[i])</code> where <code>inv = 1 / prod cnt[x]!</code> for the current counts. When we advance past position <code>i</code>, the count of <code>s[i]</code> drops by one, which multiplies <code>inv</code> by the old count. Factorials and the modular inverse are computed with Fermat's little theorem, so the whole thing is O(n * 26) (the prefix sums over the alphabet), plus O(n) precomputation. The answer is the sum of all contributions plus one."],
    time="O(26 n)", space="O(n)",
    solution='''def rearrangementRank(s):
    MOD = 1000000007
    n = len(s)
    fact = [1] * (n + 1)
    for i in range(1, n + 1):
        fact[i] = fact[i - 1] * i % MOD
    cnt = [0] * 26
    for ch in s:
        cnt[ord(ch) - 97] += 1
    inv = 1
    for c in cnt:
        inv = inv * pow(fact[c], MOD - 2, MOD) % MOD
    rank = 0
    for i, ch in enumerate(s):
        x = ord(ch) - 97
        smaller = sum(cnt[:x])
        rank = (rank + fact[n - i - 1] * inv % MOD * smaller) % MOD
        inv = inv * cnt[x] % MOD
        cnt[x] -= 1
    return (rank + 1) % MOD
''',
    tests=[["aba"], ["bca"], ["aab"], ["baa"], ["a"], ["z"], ["abc"], ["cba"], ["zyx"], ["mississippi"], ["aabbcc"], ["ccbbaa"],
           ["banana"]],
)
_r = rnd(9110)
p["tests"].append([_rs(_r, 3000)])
p["tests"].append(["".join(sorted(_rs(_r, 3000, "abc"), reverse=True))])
p["tests"].append([_rs(_r, 3000, "ab")])


def b_rank(s):
    perms = sorted(set(permutations(s)))
    return (perms.index(tuple(s)) + 1) % MOD


def g_rank(r):
    return [_rs(r, r.randint(1, 7), "abcd")]


def v_rank(tests):
    _chk(tests, 0, 1, 3000)


CHECKS["rank-of-string-in-distinct-permutations"] = (b_rank, g_rank, "exact")
VALIDATE["rank-of-string-in-distinct-permutations"] = v_rank

p = add(
    id="count-arrangements-no-adjacent-equal", title="Arrangements With No Equal Neighbours", diff="Hard", topic=TOPIC, tier="extra",
    fn="countNoAdjacentEqual", params=[("s", "string")], ret="int", cmp="exact",
    desc="<p>Count the <em>distinct</em> strings that can be made by rearranging all the letters of <code>s</code> such that no two neighbouring letters are equal. Rearrangements that produce the same string are counted once.</p><p>Return the count modulo <code>1,000,000,007</code>.</p><pre>s = \"aab\"    result = 1   (only \"aba\")\ns = \"aabb\"   result = 2   (\"abab\", \"baba\")\ns = \"abc\"    result = 6\ns = \"aaa\"    result = 0</pre>",
    constraints=["1 &le; s.length &le; 600", "s consists of lowercase English letters", "the answer is reported modulo 1,000,000,007"],
    hints=["Counting arrangements where no neighbours are equal directly is hard. Counting arrangements where neighbours are <em>allowed</em> to be equal, but with glued blocks, is easy.",
           "Inclusion-exclusion: for a letter with <code>c</code> copies, glue them into <code>k</code> blocks of consecutive copies (there are <code>C(c-1, k-1)</code> ways to cut the run into <code>k</code> non-empty parts) with sign <code>(-1)^(c-k)</code>. Then arrange all blocks freely.",
           "If letter <code>i</code> uses <code>k_i</code> blocks and <code>T</code> is the total number of blocks, the free arrangements number <code>T! / prod(k_i!)</code>. Multiply the per-letter polynomials <code>sum_k (-1)^(c-k) C(c-1,k-1) / k! * x^k</code> and read off the coefficient of each <code>x^T</code>, multiplied by <code>T!</code>."],
    editorial=["Let <code>f(k_1, k_2, ...)</code> be the number of ways to arrange blocks where letter <code>i</code> has <code>k_i</code> identical blocks: <code>T! / prod k_i!</code>. If every copy of a letter with count <code>c</code> is placed in a run structure with exactly <code>k</code> blocks (a composition of <code>c</code> into <code>k</code> positive parts, <code>C(c-1, k-1)</code> ways), the standard inclusion-exclusion over which equal neighbours are glued yields the sign <code>(-1)^(c-k)</code>. Therefore the answer is the sum over all choices of <code>k_i</code> of <code>T! * prod_i [(-1)^(c_i - k_i) C(c_i - 1, k_i - 1) / k_i!]</code>.",
               "The product over the letters is a product of polynomials in <code>x</code> (the exponent counts blocks), done iteratively in O(n&sup2;) in total since the degrees add up to <code>n</code>. After multiplying everything, the answer is <code>sum_T T! * coef[T]</code> modulo the prime, using precomputed factorials and inverse factorials. Check with <code>\"aab\"</code>: the polynomial is <code>(-x + x&sup2;/2) * x = -x&sup2; + x&sup3;/2</code>, giving <code>-2! + 3!/2 = 1</code>."],
    time="O(n^2)", space="O(n)",
    solution='''def countNoAdjacentEqual(s):
    MOD = 1000000007
    n = len(s)
    fact = [1] * (n + 2)
    for i in range(1, n + 2):
        fact[i] = fact[i - 1] * i % MOD
    inv = [1] * (n + 2)
    inv[n + 1] = pow(fact[n + 1], MOD - 2, MOD)
    for i in range(n + 1, 0, -1):
        inv[i - 1] = inv[i] * i % MOD

    def comb(a, b):
        if b < 0 or b > a:
            return 0
        return fact[a] * inv[b] % MOD * inv[a - b] % MOD

    counts = {}
    for ch in s:
        counts[ch] = counts.get(ch, 0) + 1
    poly = [1]
    for c in counts.values():
        part = [0] * (c + 1)
        for k in range(1, c + 1):
            v = comb(c - 1, k - 1) * inv[k] % MOD
            part[k] = v if (c - k) % 2 == 0 else MOD - v
        res = [0] * (len(poly) + c)
        for i, a in enumerate(poly):
            if a:
                for k in range(1, c + 1):
                    res[i + k] = (res[i + k] + a * part[k]) % MOD
        poly = res
    total = 0
    for t, a in enumerate(poly):
        total = (total + a * fact[t]) % MOD
    return total
''',
    tests=[["aab"], ["aabb"], ["abc"], ["aaa"], ["a"], ["ab"], ["aa"], ["aabbcc"], ["aaabb"], ["aaabbb"], ["abcdefgh"],
           ["mississippi"], ["aaaabbbbcccc"]],
)
_r = rnd(9111)
p["tests"].append([_rs(_r, 600)])
p["tests"].append([_rs(_r, 600, "abc")])
p["tests"].append(["a" * 300 + "b" * 300])
p["tests"].append(["a" * 301 + "b" * 299])


def b_noadj(s):
    letters = sorted(set(s))
    start = tuple(s.count(c) for c in letters)

    @lru_cache(maxsize=None)
    def go(cnt, last):
        if sum(cnt) == 0:
            return 1
        total = 0
        for i, c in enumerate(cnt):
            if c and i != last:
                nxt = cnt[:i] + (c - 1,) + cnt[i + 1:]
                total += go(nxt, i)
        return total

    return go(start, -1) % MOD


def g_noadj(r):
    return [_rs(r, r.randint(1, 10), "abcd"[:r.randint(1, 4)])]


def v_noadj(tests):
    _chk(tests, 0, 1, 600)
    assert any(t["expected"] == 0 for t in tests) and any(t["expected"] > 1 for t in tests)


CHECKS["count-arrangements-no-adjacent-equal"] = (b_noadj, g_noadj, "exact")
VALIDATE["count-arrangements-no-adjacent-equal"] = v_noadj
