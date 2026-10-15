"""Problems: sliding window combined with hashing (anagram windows, distinct characters, repeated patterns). See data/lib.py for the registry."""
from collections import Counter

from lib import add, rnd, CHECKS, VALIDATE, gen_arr  # noqa: F401

TOPIC = "Sliding Window"
LOWER = "abcdefghijklmnopqrstuvwxyz"


def rs(r, alphabet, n):
    return "".join(r.choice(alphabet) for _ in range(n))


def is_lower(s, extra=""):
    return len(s) > 0 and all(("a" <= c <= "z") or c in extra for c in s)


# ---------------------------------------------------------------- EASY

p = add(
    id="k-length-substrings-no-repeats", tier="common", title="Substrings of Length K Without Repeated Letters", diff="Easy", topic=TOPIC,
    fn="countDistinctWindows", params=[("s", "string"), ("k", "int")], ret="int", cmp="exact",
    desc="<p>Given a lowercase string <code>s</code> and an integer <code>k</code>, count the substrings of <code>s</code> that have length exactly <code>k</code> and in which <strong>all characters are different</strong>. Substrings are counted by their start position, so equal substrings found at different places each count.</p><pre>s = \"abcabcbb\", k = 3\nwindows: abc bca cab abc bcb cbb\nvalid:   yes yes yes yes no  no\nresult = 4</pre><p>If <code>k</code> is larger than 26, no window can have all-different letters, so the answer is <code>0</code>.</p>",
    constraints=["1 &le; k &le; s.length &le; 8,000", "s consists of lowercase English letters"],
    hints=["Putting every window into a set and comparing the set size with <code>k</code> works, but costs O(n &middot; k).",
           "Consecutive windows share k - 1 characters. Keep character counts and update them by adding the new letter and removing the old one.",
           "Track how many letters currently have a count of 2 or more. The window is valid exactly when that number is zero."],
    editorial=["Slide a window of length <code>k</code> across the string while keeping a count per letter and a variable <code>repeats</code> that holds the number of letters whose count is at least 2. When a letter is added and its count becomes 2, increase <code>repeats</code>; when a letter is removed and its count drops from 2 to 1, decrease it.",
               "After each step the window has length <code>k</code>; if <code>repeats</code> is 0, every letter in it is different and we count it. Every character enters and leaves the window once, so the time is O(n) and the extra memory is O(1) (26 counters). Rebuilding a set for each window would cost O(n &middot; k)."],
    time="O(n)", space="O(1)",
    solution='''def countDistinctWindows(s, k):
    cnt = {}
    repeats = 0
    ans = 0
    for i, ch in enumerate(s):
        c = cnt.get(ch, 0) + 1
        cnt[ch] = c
        if c == 2:
            repeats += 1
        if i >= k:
            old = s[i - k]
            c = cnt[old]
            cnt[old] = c - 1
            if c == 2:
                repeats -= 1
        if i >= k - 1 and repeats == 0:
            ans += 1
    return ans
''',
    tests=[["abcabcbb", 3], ["aaaa", 2], ["havefunonleetcode", 5], ["a", 1], ["abcdefghijklmnopqrstuvwxyz", 26], ["abcdefghijklmnopqrstuvwxyz", 25],
           ["aabbcc", 1], ["abab", 2], ["abab", 3], ["zzzzzzzzzzzzzzzzzzzzzzzzzzzzzz", 27], ["abcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyz", 27],
           ["abcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyz", 26]],
)
_r = rnd(8501)
p["tests"].append([rs(_r, LOWER, 8000), 8])
p["tests"].append([rs(_r, "abcdefghijklm", 8000), 12])
p["tests"].append([("abcdefghij" * 800), 10])


def b_kdw(s, k):
    return sum(1 for i in range(len(s) - k + 1) if len(set(s[i:i + k])) == k)


def g_kdw(r):
    n = r.randint(1, 12)
    return [rs(r, "abcd", n), r.randint(1, n)]


def v_kdw(tests):
    for t in tests:
        s, k = t["args"]
        assert is_lower(s) and len(s) <= 8000 and 1 <= k <= len(s)


CHECKS["k-length-substrings-no-repeats"] = (b_kdw, g_kdw, "exact")
VALIDATE["k-length-substrings-no-repeats"] = v_kdw

p = add(
    id="repeated-dna-sequences-count", tier="common", title="Repeated DNA Fragments", diff="Easy", topic=TOPIC,
    fn="countRepeatedFragments", params=[("s", "string"), ("L", "int")], ret="int", cmp="exact",
    desc="<p>A DNA string <code>s</code> uses only the letters <code>A</code>, <code>C</code>, <code>G</code> and <code>T</code>. A <em>fragment</em> is a substring of length exactly <code>L</code>.</p><p>Return the number of <strong>different</strong> fragments that occur <strong>at least twice</strong> in <code>s</code>. Occurrences may overlap.</p><pre>s = \"AAAAACCCCCAAAAACCCCCCAAAAAGGGTTT\", L = 10\n\"AAAAACCCCC\" occurs 2 times, \"CCCCCAAAAA\" occurs 2 times\nresult = 2</pre><pre>s = \"AAAAAAAAAAAAA\", L = 10\n\"AAAAAAAAAA\" occurs 4 times (overlapping)\nresult = 1</pre>",
    constraints=["1 &le; L &le; 20", "L &le; s.length &le; 8,000", "s consists only of the letters A, C, G, T"],
    hints=["Collect all fragments of length L and count how often each one appears. What do you do with the ones that appear twice or more?",
           "Storing each fragment as a string costs O(L) per window. Since there are only four letters, a fragment can be turned into a number.",
           "Use 2 bits per letter and a rolling value: shift left by 2, add the new letter, and mask to the lowest <code>2 * L</code> bits. A set of numbers records what has been seen; a second set records what repeated."],
    editorial=["Map A, C, G, T to 0, 1, 2, 3. The fragment ending at position <code>i</code> is the number <code>((prev &lt;&lt; 2) | code) &amp; mask</code> where <code>mask = 2<sup>2L</sup> - 1</code>; the mask drops the letter that left the window. This gives a unique integer for every fragment (no collisions, because 2 bits per letter is a lossless encoding) and each window costs O(1).",
               "Keep a set <code>seen</code> and a set <code>repeated</code>. If the current value was already seen, put it in <code>repeated</code>; otherwise add it to <code>seen</code>. The answer is the size of <code>repeated</code>. A fragment with three or more occurrences is still counted once because <code>repeated</code> is a set. Time O(n), space O(n)."],
    time="O(n)", space="O(n)",
    solution='''def countRepeatedFragments(s, L):
    code = {'A': 0, 'C': 1, 'G': 2, 'T': 3}
    mask = (1 << (2 * L)) - 1
    seen = set()
    repeated = set()
    h = 0
    for i, ch in enumerate(s):
        h = ((h << 2) | code[ch]) & mask
        if i >= L - 1:
            if h in seen:
                repeated.add(h)
            else:
                seen.add(h)
    return len(repeated)
''',
    tests=[["AAAAACCCCCAAAAACCCCCCAAAAAGGGTTT", 10], ["AAAAAAAAAAAAA", 10], ["ACGT", 4], ["ACGT", 1], ["AAAA", 1], ["ACGTACGT", 4], ["ACGTACGT", 3],
           ["GATTACA", 2], ["AAAAAAAAAAAAAAAAAAAA", 20], ["AAAAAAAAAAAAAAAAAAAAA", 20], ["CCCCCCCCCCCCCCCCCCCCCCCCCCCCCC", 15], ["ACACACACACAC", 4]],
)
_r = rnd(8502)
p["tests"].append([rs(_r, "ACGT", 8000), 5])
p["tests"].append([rs(_r, "ACGT", 8000), 10])
_x = rs(_r, "ACGT", 3000)
p["tests"].append([_x + rs(_r, "ACGT", 1500) + _x + rs(_r, "ACGT", 500), 20])


def b_dna(s, L):
    c = Counter(s[i:i + L] for i in range(len(s) - L + 1))
    return sum(1 for v in c.values() if v >= 2)


def g_dna(r):
    n = r.randint(1, 16)
    return [rs(r, "ACGT" if r.random() < 0.5 else "AC", n), r.randint(1, min(n, 5))]


def v_dna(tests):
    for t in tests:
        s, L = t["args"]
        assert set(s) <= set("ACGT") and 1 <= L <= 20 and L <= len(s) <= 8000


CHECKS["repeated-dna-sequences-count"] = (b_dna, g_dna, "exact")
VALIDATE["repeated-dna-sequences-count"] = v_dna

p = add(
    id="count-permutation-windows", tier="extra", title="Windows That Are a Permutation of 1..M", diff="Easy", topic=TOPIC,
    fn="countPermutationWindows", params=[("nums", "int[]"), ("m", "int")], ret="int", cmp="exact",
    desc="<p>Given an integer array <code>nums</code> and an integer <code>m</code>, count the contiguous blocks of length exactly <code>m</code> that contain every number from <code>1</code> to <code>m</code> exactly once (in any order). Other values, repeated values or missing values make a block invalid.</p><pre>nums = [2, 1, 3, 1, 2, 3, 3, 1], m = 3\n[2,1,3] ok   [1,3,1] no   [3,1,2] ok\n[1,2,3] ok   [2,3,3] no   [3,3,1] no\nresult = 3</pre>",
    constraints=["1 &le; m &le; nums.length &le; 8,000", "1 &le; nums[i] &le; 10,000"],
    hints=["Sorting each block and comparing it with <code>[1, 2, ..., m]</code> works but is O(n &middot; m log m).",
           "A block of length m is a permutation of 1..m exactly when each of the m values 1..m occurs exactly once in it.",
           "Keep a count per value and a number <code>good</code> = how many values in 1..m currently have count exactly 1. The block is valid when <code>good == m</code>."],
    editorial=["Because the block has exactly <code>m</code> elements, it is a permutation of 1..m precisely when all m values in the range 1..m each appear exactly once. Maintain a hash map of counts for the current window and the number <code>good</code> of values in 1..m whose count is exactly 1.",
               "When a value in 1..m enters, its count goes 0 &rarr; 1 (good + 1), or 1 &rarr; 2 (good - 1), and nothing changes at higher counts. When it leaves, the changes are reversed (1 &rarr; 0 loses one, 2 &rarr; 1 gains one). Values outside 1..m are simply ignored by <code>good</code>. Count the windows where <code>good == m</code>. O(n) time, O(m) space."],
    time="O(n)", space="O(m)",
    solution='''def countPermutationWindows(nums, m):
    cnt = {}
    good = 0
    ans = 0
    for i, x in enumerate(nums):
        if 1 <= x <= m:
            c = cnt.get(x, 0) + 1
            cnt[x] = c
            if c == 1:
                good += 1
            elif c == 2:
                good -= 1
        if i >= m:
            y = nums[i - m]
            if 1 <= y <= m:
                c = cnt[y]
                cnt[y] = c - 1
                if c == 1:
                    good -= 1
                elif c == 2:
                    good += 1
        if i >= m - 1 and good == m:
            ans += 1
    return ans
''',
    tests=[[[2, 1, 3, 1, 2, 3, 3, 1], 3], [[1], 1], [[2], 1], [[1, 1, 1], 1], [[1, 2, 3, 4, 5], 5], [[5, 4, 3, 2, 1], 5], [[1, 2, 2, 1], 2],
           [[3, 1, 2, 3, 1, 2], 3], [[1, 2, 4], 3], [[10000, 1, 2, 10000, 2, 1], 2], [[2, 1, 2, 1, 2, 1, 2], 2], [[7, 8, 9], 3]],
)
_r = rnd(8503)
_a = []
while len(_a) < 6000:
    _b = list(range(1, 51)); _r.shuffle(_b); _a += _b
p["tests"].append([_a[:6000], 50])
p["tests"].append([[_r.randint(1, 4) for _ in range(8000)], 4])
_a = [_r.randint(1, 3000) for _ in range(5000)]
_b = list(range(1, 1001)); _r.shuffle(_b)
_a[2000:3000] = _b
p["tests"].append([_a, 1000])


def b_perm(nums, m):
    return sum(1 for i in range(len(nums) - m + 1) if sorted(nums[i:i + m]) == list(range(1, m + 1)))


def g_perm(r):
    m = r.randint(1, 4)
    n = r.randint(m, 11)
    return [[r.randint(1, m + 1) for _ in range(n)], m]


def v_perm(tests):
    for t in tests:
        nums, m = t["args"]
        assert 1 <= m <= len(nums) <= 8000 and all(1 <= x <= 10000 for x in nums)


CHECKS["count-permutation-windows"] = (b_perm, g_perm, "exact")
VALIDATE["count-permutation-windows"] = v_perm

# ---------------------------------------------------------------- MEDIUM

p = add(
    id="near-anagram-windows", tier="common", title="Windows Within K Edits of an Anagram", diff="Medium", topic=TOPIC,
    fn="countNearAnagrams", params=[("s", "string"), ("p", "string"), ("k", "int")], ret="int", cmp="exact",
    desc="<p>Let <code>m</code> be the length of the string <code>p</code>. For every substring of <code>s</code> of length <code>m</code>, ask: what is the smallest number of characters that must be <em>replaced</em> (each replaced by any letter) so that the substring becomes an anagram of <code>p</code>?</p><p>Count the substrings (by start position) for which this smallest number is at most <code>k</code>.</p><pre>s = \"cbaxyz\", p = \"abc\", k = 1\ncba -> 0 replacements\nbax -> 1 (x becomes c)\naxy -> 2\nxyz -> 3\nresult = 2</pre>",
    constraints=["1 &le; p.length &le; s.length &le; 8,000", "0 &le; k &le; p.length", "s and p consist of lowercase English letters"],
    hints=["Think about which characters of a window are already 'in the right place' in the multiset sense. The rest must be replaced.",
           "The number of characters of a window that can be kept is the sum over letters of <code>min(window count, need count)</code>. The replacements needed equal <code>m</code> minus that sum.",
           "Maintain that sum while sliding: when a letter enters and its window count is still below its need, the sum grows by one; when a letter leaves and its count was at most its need, the sum shrinks by one."],
    editorial=["For one window, the characters that can stay are matched against <code>p</code> letter by letter: for each letter c we can keep at most <code>min(have[c], need[c])</code> copies. All remaining positions must be replaced, and replacement is always enough, since the leftover positions can take exactly the letters that <code>p</code> still lacks. So the cost is <code>m - sum_c min(have[c], need[c])</code>.",
               "Keep the array <code>have</code> for the current window and the running value <code>matched = sum_c min(have[c], need[c])</code>. Adding a letter c: if <code>have[c] &lt; need[c]</code> before the addition, <code>matched</code> increases by one. Removing a letter c: after decrementing, if <code>have[c] &lt; need[c]</code>, <code>matched</code> decreases by one. A window counts when <code>m - matched &lt;= k</code>. Total time O(n + m), space O(1)."],
    time="O(n + m)", space="O(1)",
    solution='''def countNearAnagrams(s, p, k):
    n, m = len(s), len(p)
    need = [0] * 26
    for ch in p:
        need[ord(ch) - 97] += 1
    have = [0] * 26
    matched = 0
    ans = 0
    for i in range(n):
        c = ord(s[i]) - 97
        if have[c] < need[c]:
            matched += 1
        have[c] += 1
        if i >= m:
            d = ord(s[i - m]) - 97
            have[d] -= 1
            if have[d] < need[d]:
                matched -= 1
        if i >= m - 1 and m - matched <= k:
            ans += 1
    return ans
''',
    tests=[["cbaxyz", "abc", 1], ["cbaxyz", "abc", 0], ["cbaxyz", "abc", 3], ["a", "a", 0], ["a", "b", 0], ["a", "b", 1], ["abab", "ab", 0],
           ["aaaa", "bb", 1], ["aaaa", "bb", 2], ["abcdabcd", "aabb", 1], ["abcdabcd", "aabb", 2], ["zzzzzzzz", "zzzzzzzz", 0], ["abcdefgh", "hgfedcba", 0]],
)
_r = rnd(8504)
p["tests"].append([rs(_r, "abc", 8000), "abcabc", 2])
_p = rs(_r, LOWER, 200)
_s = ""
for _ in range(36):
    _w = list(_p); _r.shuffle(_w)
    for _ in range(_r.randint(0, 6)):
        _w[_r.randrange(200)] = _r.choice(LOWER)
    _s += "".join(_w)
p["tests"].append([_s[:7200], _p, 4])
p["tests"].append([rs(_r, LOWER, 8000), rs(_r, LOWER, 12), 8])


def b_near(s, p, k):
    m = len(p)
    ans = 0
    for i in range(len(s) - m + 1):
        w = list(s[i:i + m])
        rest = list(p)
        kept = 0
        for ch in w:
            if ch in rest:
                rest.remove(ch)
                kept += 1
        if m - kept <= k:
            ans += 1
    return ans


def g_near(r):
    m = r.randint(1, 4)
    n = r.randint(m, 11)
    return [rs(r, "abc", n), rs(r, "abc", m), r.randint(0, m)]


def v_near(tests):
    for t in tests:
        s, pp, k = t["args"]
        assert is_lower(s) and is_lower(pp) and 1 <= len(pp) <= len(s) <= 8000 and 0 <= k <= len(pp)


CHECKS["near-anagram-windows"] = (b_near, g_near, "exact")
VALIDATE["near-anagram-windows"] = v_near

p = add(
    id="max-occurrences-of-limited-substring", tier="common", title="Most Frequent Substring With Few Distinct Letters", diff="Medium", topic=TOPIC,
    fn="maxOccurrences", params=[("s", "string"), ("maxLetters", "int"), ("minSize", "int"), ("maxSize", "int")], ret="int", cmp="exact",
    desc="<p>Consider every substring <code>t</code> of <code>s</code> that satisfies both rules:</p><ul><li>its length is between <code>minSize</code> and <code>maxSize</code> inclusive;</li><li>it contains at most <code>maxLetters</code> different letters.</li></ul><p>Return the largest number of times any such <code>t</code> occurs in <code>s</code>. Occurrences may overlap. If no substring satisfies the rules, return <code>0</code>.</p><pre>s = \"aababcaab\", maxLetters = 2, minSize = 3, maxSize = 4\n\"aab\" is allowed and occurs at positions 0 and 6\nresult = 2</pre>",
    constraints=["1 &le; s.length &le; 8,000", "1 &le; maxLetters &le; 26", "1 &le; minSize &le; maxSize &le; 26", "s consists of lowercase English letters"],
    hints=["Brute force over all lengths from minSize to maxSize and all start positions is too much work for 8,000 characters and 26 lengths... but is every length really needed?",
           "If a substring of length L &gt; minSize occurs c times, then its first minSize characters occur at least c times too, and still satisfy the letter limit.",
           "So only length <code>minSize</code> matters. Slide a window of that length, maintain the number of distinct letters, and count the allowed windows in a hash map."],
    editorial=["Take any valid substring <code>t</code> longer than <code>minSize</code> with <code>c</code> occurrences. Its prefix of length <code>minSize</code> occurs at every one of those places, so at least <code>c</code> times; it has no more distinct letters than <code>t</code>, and has a legal length. Therefore the best answer is always achieved at length exactly <code>minSize</code>, and <code>maxSize</code> never changes the result (it is only a distraction).",
               "Slide a window of length <code>minSize</code> and keep letter counts to know the number of distinct letters in O(1) per step. Whenever the window has at most <code>maxLetters</code> distinct letters, increment its count in a hash map keyed by the substring text (at most 26 characters). The answer is the largest value in the map, or 0. Time O(n &middot; minSize) for hashing the slices, i.e. O(n) for these limits."],
    time="O(n * minSize)", space="O(n * minSize)",
    solution='''def maxOccurrences(s, maxLetters, minSize, maxSize):
    n = len(s)
    if minSize > n:
        return 0
    cnt = {}
    distinct = 0
    freq = {}
    best = 0
    for i, ch in enumerate(s):
        c = cnt.get(ch, 0)
        if c == 0:
            distinct += 1
        cnt[ch] = c + 1
        if i >= minSize:
            old = s[i - minSize]
            cnt[old] -= 1
            if cnt[old] == 0:
                distinct -= 1
        if i >= minSize - 1 and distinct <= maxLetters:
            t = s[i - minSize + 1:i + 1]
            freq[t] = freq.get(t, 0) + 1
            if freq[t] > best:
                best = freq[t]
    return best
''',
    tests=[["aababcaab", 2, 3, 4], ["abcde", 2, 3, 3], ["aaaa", 1, 1, 1], ["aaaa", 1, 2, 4], ["aaaa", 1, 5, 6], ["a", 1, 1, 1], ["abcabcabc", 3, 3, 3],
           ["abcabcabc", 2, 3, 3], ["abcabcabc", 2, 2, 5], ["ababababab", 2, 2, 26], ["zyxwvutsrq", 26, 10, 26], ["abababcabab", 2, 4, 6], ["aabbaabbaabb", 2, 4, 4]],
)
_r = rnd(8505)
p["tests"].append([rs(_r, "abc", 8000), 2, 5, 12])
p["tests"].append([rs(_r, LOWER, 8000), 26, 3, 26])
p["tests"].append([("abcdefghijklmnopqrstuvwxy" * 320), 5, 6, 20])


def b_occ(s, maxLetters, minSize, maxSize):
    best = 0
    n = len(s)
    for size in range(minSize, maxSize + 1):
        for i in range(n - size + 1):
            t = s[i:i + size]
            if len(set(t)) > maxLetters:
                continue
            c = 0
            for j in range(n - size + 1):
                if s[j:j + size] == t:
                    c += 1
            best = max(best, c)
    return best


def g_occ(r):
    mn = r.randint(1, 4)
    return [rs(r, "abc", r.randint(1, 14)), r.randint(1, 3), mn, mn + r.randint(0, 3)]


def v_occ(tests):
    for t in tests:
        s, ml, mn, mx = t["args"]
        assert is_lower(s) and len(s) <= 8000 and 1 <= ml <= 26 and 1 <= mn <= mx <= 26


CHECKS["max-occurrences-of-limited-substring"] = (b_occ, g_occ, "exact")
VALIDATE["max-occurrences-of-limited-substring"] = v_occ


def de_bruijn(k):
    a = [0] * (2 * k)
    seq = []

    def db(t, pp):
        if t > k:
            if k % pp == 0:
                seq.extend(a[1:pp + 1])
        else:
            a[t] = a[t - pp]
            db(t + 1, pp)
            for j in range(a[t - pp] + 1, 2):
                a[t] = j
                db(t + 1, t)
    db(1, 1)
    sq = "".join(map(str, seq))
    return sq + sq[:k - 1]


p = add(
    id="all-binary-codes-in-string", tier="common", title="Does the Bit String Contain Every Code?", diff="Medium", topic=TOPIC,
    fn="containsAllCodes", params=[("s", "string"), ("k", "int")], ret="bool", cmp="exact",
    desc="<p>The string <code>s</code> consists of the characters <code>0</code> and <code>1</code>. There are exactly <code>2<sup>k</sup></code> different binary strings (codes) of length <code>k</code>. Return <code>true</code> if <strong>every</strong> one of them occurs in <code>s</code> as a contiguous substring, and <code>false</code> otherwise.</p><pre>s = \"00110110\", k = 2\ncodes 00, 01, 10, 11 all occur -> true\n\ns = \"00110110\", k = 3\nonly 6 windows exist but 8 codes are needed -> false</pre>",
    constraints=["1 &le; k &le; 16", "1 &le; s.length &le; 9,000", "s consists only of the characters '0' and '1'"],
    hints=["Collecting the length-k windows in a set and comparing the set size with 2<sup>k</sup> is a valid approach. Can you make each window O(1) instead of O(k)?",
           "A window of k bits is just a k-bit integer. Moving to the next window means shifting left by one, adding the new bit, and masking off the bit that left.",
           "Use a boolean array of size 2<sup>k</sup> indexed by that number. Stop with <code>true</code> as soon as all 2<sup>k</sup> values were marked. Also note that you need at least 2<sup>k</sup> + k - 1 characters, which allows an immediate <code>false</code>."],
    editorial=["The window ending at position <code>i</code> is the integer <code>h = ((h &lt;&lt; 1) | bit) &amp; (2<sup>k</sup> - 1)</code>. This rolling value costs O(1) per step and is a perfect hash: different windows give different integers. Keep a bit array of size 2<sup>k</sup> and a counter of how many distinct values were marked; the answer is <code>true</code> once the counter reaches 2<sup>k</sup>.",
               "There are only <code>n - k + 1</code> windows, so if that is less than 2<sup>k</sup> the answer is immediately <code>false</code>. With the given limits this also bounds the table: the table is only worth building when n &ge; 2<sup>k</sup> + k - 1, hence 2<sup>k</sup> is at most about 9,000. Time O(n), space O(2<sup>k</sup>)."],
    time="O(n)", space="O(2^k)",
    solution='''def containsAllCodes(s, k):
    need = 1 << k
    if len(s) < need + k - 1:
        return False
    mask = need - 1
    seen = bytearray(need)
    got = 0
    h = 0
    for i, ch in enumerate(s):
        h = ((h << 1) | (ch == '1')) & mask
        if i >= k - 1 and not seen[h]:
            seen[h] = 1
            got += 1
            if got == need:
                return True
    return False
''',
    tests=[["00110110", 2], ["00110110", 3], ["0110", 1], ["0", 1], ["1", 1], ["01", 1], ["0000", 2], ["00110", 2], ["0011010", 2],
           ["00010111", 3], ["0001011100", 3], ["1" * 20, 4]],
)
_r = rnd(8506)
_d = de_bruijn(13)
assert len(_d) == 8204
p["tests"].append([_d, 13])
_f = list(_d); _f[4000] = "1" if _f[4000] == "0" else "0"
p["tests"].append(["".join(_f), 13])
p["tests"].append([rs(_r, "01", 8000), 10])
p["tests"].append([de_bruijn(4)[:-1], 4])


def b_codes(s, k):
    return len({s[i:i + k] for i in range(len(s) - k + 1)}) == 2 ** k


def g_codes(r):
    k = r.randint(1, 4)
    if r.random() < 0.5:
        n = r.randint(1, 2 ** k + k + 4)
    else:
        n = r.randint(2 ** k + k - 1, 2 ** k + k + 10)
    return [rs(r, "01", n), k]


def v_codes(tests):
    for t in tests:
        s, k = t["args"]
        assert set(s) <= set("01") and 1 <= len(s) <= 9000 and 1 <= k <= 16


CHECKS["all-binary-codes-in-string"] = (b_codes, g_codes, "exact")
VALIDATE["all-binary-codes-in-string"] = v_codes

p = add(
    id="count-pairs-of-anagram-windows", tier="extra", title="Pairs of Anagram Windows", diff="Medium", topic=TOPIC,
    fn="countAnagramWindowPairs", params=[("s", "string"), ("k", "int")], ret="int", cmp="exact",
    desc="<p>Take all substrings of <code>s</code> that have length exactly <code>k</code>, one for every start position. Count the pairs of start positions <code>(i, j)</code> with <code>i &lt; j</code> whose two substrings are <strong>anagrams</strong> of each other (same letters with the same multiplicities, any order). Equal substrings are anagrams of each other too.</p><pre>s = \"abbaab\", k = 2\nwindows: ab bb ba aa ab\nanagram groups: {ab, ba, ab} (3 windows), {bb}, {aa}\npairs: 3\nresult = 3</pre>",
    constraints=["1 &le; k &le; s.length &le; 8,000", "s consists of lowercase English letters"],
    hints=["Comparing every pair of windows is O(n<sup>2</sup>) comparisons, too slow for 8,000 windows.",
           "Two windows are anagrams exactly when their letter-count vectors are equal. Group windows by that vector.",
           "Maintain the 26 counters while sliding, use a snapshot of them (for example a tuple) as a hash key, and for a group of size g add g * (g - 1) / 2 pairs. Equivalently, add the current group size before incrementing it."],
    editorial=["Let a window's <em>signature</em> be its vector of 26 letter counts. Two windows are anagrams if and only if their signatures are equal, so the task becomes: count pairs of equal keys. Update the counters in O(1) when sliding the window (one letter in, one letter out), then convert the counters to a tuple key in O(26).",
               "Keep a dictionary from signature to how many windows had it so far. When a new window arrives, all earlier windows with the same signature form a new pair with it, so add the dictionary value to the answer and then increment it. This yields the number of pairs in total. Time O(26 &middot; n), space O(26 &middot; n). The answer is at most n(n-1)/2, which is below 32 million here."],
    time="O(26 n)", space="O(26 n)",
    solution='''def countAnagramWindowPairs(s, k):
    n = len(s)
    cnt = [0] * 26
    groups = {}
    ans = 0
    for i in range(n):
        cnt[ord(s[i]) - 97] += 1
        if i >= k:
            cnt[ord(s[i - k]) - 97] -= 1
        if i >= k - 1:
            key = tuple(cnt)
            g = groups.get(key, 0)
            ans += g
            groups[key] = g + 1
    return ans
''',
    tests=[["abbaab", 2], ["a", 1], ["ab", 1], ["aaaa", 1], ["aaaa", 2], ["abcabc", 3], ["abcabc", 2], ["abcdef", 3], ["abcdef", 6], ["baab", 2],
           ["aabbaabbaabb", 4], ["abcdefghijklmnopqrstuvwxyz", 13]],
)
_r = rnd(8507)
p["tests"].append([rs(_r, "ab", 8000), 6])
p["tests"].append([rs(_r, "abc", 8000), 10])
p["tests"].append([rs(_r, LOWER, 8000), 3])
p["tests"].append(["a" * 8000, 4000])


def b_pairs(s, k):
    w = [sorted(s[i:i + k]) for i in range(len(s) - k + 1)]
    return sum(1 for i in range(len(w)) for j in range(i + 1, len(w)) if w[i] == w[j])


def g_pairs(r):
    n = r.randint(1, 12)
    return [rs(r, "abc", n), r.randint(1, n)]


def v_pairs(tests):
    for t in tests:
        s, k = t["args"]
        assert is_lower(s) and 1 <= k <= len(s) <= 8000


CHECKS["count-pairs-of-anagram-windows"] = (b_pairs, g_pairs, "exact")
VALIDATE["count-pairs-of-anagram-windows"] = v_pairs

p = add(
    id="count-substrings-covering-pattern", tier="common", title="Count Substrings That Cover a Pattern", diff="Medium", topic=TOPIC,
    fn="countCoveringSubstrings", params=[("s", "string"), ("p", "string")], ret="int", cmp="exact",
    desc="<p>A substring of <code>s</code> <em>covers</em> the string <code>p</code> if, for every letter, it contains at least as many copies of that letter as <code>p</code> does (the order does not matter, and extra letters are fine).</p><p>Count the substrings of <code>s</code> that cover <code>p</code>. Substrings are identified by their start and end position, so equal texts at different places count separately.</p><pre>s = \"abcabc\", p = \"abc\"\nstart 0: ends 2,3,4,5 -> 4\nstart 1: ends 3,4,5   -> 3\nstart 2: ends 4,5     -> 2\nstart 3: end 5        -> 1\nresult = 10</pre>",
    constraints=["1 &le; p.length &le; s.length &le; 8,000", "s and p consist of lowercase English letters"],
    hints=["Enumerating all O(n<sup>2</sup>) substrings and checking each costs far too much; but notice that if a substring covers p, so does every longer substring containing it.",
           "For a fixed right end, the valid left ends form a prefix of positions: all starts from 0 up to some largest valid start.",
           "Slide the right end. Keep the left end as far right as possible while the window still covers p, and add <code>left + 1</code> to the answer for each right end where the window covers p."],
    editorial=["Coverage is monotone: extending a covering substring in either direction keeps it covering. So for each right end <code>r</code> there is a largest start <code>l(r)</code> such that <code>s[l..r]</code> covers p (or none), and every start from 0 to <code>l(r)</code> is valid, giving <code>l(r) + 1</code> substrings. Also <code>l(r)</code> never decreases as <code>r</code> grows.",
               "Maintain letter counts of the window and <code>missing</code>, the total number of letter copies that p still needs. Add <code>s[r]</code> (lower <code>missing</code> if the letter was still needed). Once <code>missing == 0</code>, advance <code>l</code> while the letter at <code>l</code> is surplus (not in p, or its window count exceeds p's count), and then add <code>l + 1</code>. Both pointers only move right, so the time is O(n + m); the result is at most n(n+1)/2, about 32 million."],
    time="O(n + m)", space="O(1)",
    solution='''def countCoveringSubstrings(s, p):
    need = [0] * 26
    for ch in p:
        need[ord(ch) - 97] += 1
    have = [0] * 26
    missing = len(p)
    left = 0
    ans = 0
    for ch in s:
        c = ord(ch) - 97
        if have[c] < need[c]:
            missing -= 1
        have[c] += 1
        if missing == 0:
            while have[ord(s[left]) - 97] > need[ord(s[left]) - 97]:
                have[ord(s[left]) - 97] -= 1
                left += 1
            ans += left + 1
    return ans
''',
    tests=[["abcabc", "abc"], ["a", "a"], ["a", "b"], ["aaa", "aa"], ["aabab", "aab"], ["abc", "abc"], ["cba", "abc"], ["abcdef", "f"], ["xyz", "abc"],
           ["abcabcabc", "aabbcc"], ["bbbbbaaaaa", "ab"], ["abababababab", "aaabbb"], ["zzzzzzzzzz", "zzzzzzzzzz"]],
)
_r = rnd(8508)
p["tests"].append([rs(_r, "abc", 8000), "abcabc"])
p["tests"].append([rs(_r, LOWER, 8000), "abcdefgh"])
p["tests"].append([("ab" * 4000), "a" * 300 + "b" * 300])
p["tests"].append(["a" * 8000, "a" * 8000])


def b_cover(s, p):
    need = Counter(p)
    n = len(s)
    total = 0
    for i in range(n):
        for j in range(i, n):
            c = Counter(s[i:j + 1])
            if all(c[ch] >= v for ch, v in need.items()):
                total += 1
    return total


def g_cover(r):
    return [rs(r, "abc", r.randint(1, 12)), rs(r, "abc", r.randint(1, 4))]


def v_cover(tests):
    for t in tests:
        s, pp = t["args"]
        assert is_lower(s) and is_lower(pp) and 1 <= len(pp) <= len(s) <= 8000


# the generator may produce p longer than s; the reference and the brute force both return 0 then
CHECKS["count-substrings-covering-pattern"] = (b_cover, g_cover, "exact")
VALIDATE["count-substrings-covering-pattern"] = v_cover

p = add(
    id="wildcard-anagram-windows", tier="extra", title="Anagram Windows With Wildcards", diff="Medium", topic=TOPIC,
    fn="countWildcardAnagramWindows", params=[("s", "string"), ("p", "string")], ret="int", cmp="exact",
    desc="<p>The text <code>s</code> contains lowercase letters and the wildcard character <code>?</code>. Each <code>?</code> can be replaced by any lowercase letter you like, independently of the other wildcards. The pattern <code>p</code> has only lowercase letters.</p><p>Count the substrings of <code>s</code> of length <code>p.length</code> that <strong>can</strong> be turned, by choosing replacements for their wildcards, into an anagram of <code>p</code>. Count by start position.</p><pre>s = \"a?cb?\", p = \"abc\"\na?c -> ? becomes b: abc   yes\n?cb -> ? becomes a: acb   yes\ncb? -> ? becomes a: cba   yes\nresult = 3</pre><pre>s = \"aa?b\", p = \"abc\"\naa? has two a's but p has only one -> no\na?b -> yes\nresult = 1</pre>",
    constraints=["1 &le; p.length &le; s.length &le; 8,000", "s consists of lowercase letters and '?'", "p consists of lowercase letters"],
    hints=["Compare with the plain anagram-window problem: what changes when a window contains wildcards?",
           "A wildcard can supply any letter that p needs. The window fails only when it has too many copies of some real letter, more than p contains.",
           "Because the window and p have the same length, a window works exactly when no letter has window count greater than its count in p. Track how many letters currently have an excess."],
    editorial=["Let <code>need[c]</code> be the count of letter c in p and <code>have[c]</code> the count of that real letter in the window; wildcards are not counted in <code>have</code>. If every <code>have[c] &lt;= need[c]</code>, then the real letters use up part of p and the remaining positions are exactly the wildcards (both the window and p have length m), so each wildcard can be replaced by one of the still-needed letters. If some letter has <code>have[c] &gt; need[c]</code>, no replacement can fix it, because replacing wildcards cannot remove a real letter.",
               "So keep <code>excess</code>, the number of letters with <code>have[c] &gt; need[c]</code>, and update it in O(1) when a letter enters (count goes from need to need + 1: excess + 1) or leaves (from need + 1 to need: excess - 1). Ignore '?' characters when updating. Count windows where <code>excess == 0</code>. Time O(n + m), space O(1)."],
    time="O(n + m)", space="O(1)",
    solution='''def countWildcardAnagramWindows(s, p):
    n, m = len(s), len(p)
    need = [0] * 26
    for ch in p:
        need[ord(ch) - 97] += 1
    have = [0] * 26
    excess = 0
    ans = 0
    for i in range(n):
        if s[i] != '?':
            c = ord(s[i]) - 97
            have[c] += 1
            if have[c] == need[c] + 1:
                excess += 1
        if i >= m and s[i - m] != '?':
            d = ord(s[i - m]) - 97
            if have[d] == need[d] + 1:
                excess -= 1
            have[d] -= 1
        if i >= m - 1 and excess == 0:
            ans += 1
    return ans
''',
    tests=[["a?cb?", "abc"], ["aa?b", "abc"], ["?", "a"], ["a", "b"], ["???", "abc"], ["???", "aaa"], ["abc", "abc"], ["abd", "abc"], ["??a??", "ab"],
           ["aaaa", "aa"], ["a?a?a?", "aab"], ["zz?zz?zz", "zzz"], ["abab?bab", "aabb"]],
)
_r = rnd(8509)
p["tests"].append([rs(_r, "ab?", 8000), "aabb"])
p["tests"].append([rs(_r, "abcdef??", 8000), "abcdef"])
_x = rs(_r, LOWER, 100)
p["tests"].append([("".join(_r.choice(c + "??") for c in _x * 70)), _x])


def b_wild(s, p):
    m = len(p)
    ans = 0
    for i in range(len(s) - m + 1):
        w = s[i:i + m]
        rest = list(p)
        ok = True
        for ch in w:
            if ch == '?':
                continue
            if ch in rest:
                rest.remove(ch)
            else:
                ok = False
                break
        if ok:
            ans += 1
    return ans


def g_wild(r):
    m = r.randint(1, 4)
    return [rs(r, "abc?", r.randint(m, 12)), rs(r, "abc", m)]


def v_wild(tests):
    for t in tests:
        s, pp = t["args"]
        assert is_lower(s, "?") and is_lower(pp) and 1 <= len(pp) <= len(s) <= 8000


CHECKS["wildcard-anagram-windows"] = (b_wild, g_wild, "exact")
VALIDATE["wildcard-anagram-windows"] = v_wild

# ---------------------------------------------------------------- HARD

p = add(
    id="concatenated-words-substring-starts", tier="common", title="Substrings Made of All Words", diff="Hard", topic=TOPIC,
    fn="findConcatenationStarts", params=[("s", "string"), ("words", "string"), ("wordLen", "int")], ret="int[]", cmp="exact",
    desc="<p>You are given a text <code>s</code> and a list of words that all have the same length <code>wordLen</code>. The list is passed as a single string <code>words</code>: the words written one after another with no separators, so the i-th word is <code>words[i * wordLen .. (i + 1) * wordLen)</code>. Words may repeat.</p><p>A substring of <code>s</code> is a <em>full concatenation</em> if it can be cut into consecutive pieces of length <code>wordLen</code> that are exactly the given words, each word used as many times as it appears in the list, in any order. Return all start indices of full concatenations in <strong>increasing order</strong> (an empty array if there are none).</p><pre>s = \"barfoothefoobarman\", words = \"foobar\", wordLen = 3   (words: foo, bar)\n\"barfoo\" at 0 and \"foobar\" at 9\nresult = [0, 9]</pre><pre>s = \"wordgoodgoodgoodbestword\", words = \"goodgoodbestword\", wordLen = 4\nwords: good, good, best, word; only the substring at 8 matches\nresult = [8]</pre>",
    constraints=["1 &le; wordLen &le; 30", "wordLen &le; words.length &le; 5,000 and words.length is a multiple of wordLen", "1 &le; s.length &le; 8,000", "s and words consist of lowercase English letters"],
    hints=["Let total = (number of words) * wordLen. Every candidate substring has length total, so there are n - total + 1 of them. Checking each one by cutting it into words is correct but slow when there are many words.",
           "A match must be aligned on word boundaries relative to its start. So handle each starting offset <code>0 .. wordLen - 1</code> separately and jump through the text in steps of <code>wordLen</code>.",
           "For each offset, slide a window of whole words with a hash map of word counts. When a word occurs too often, move the left edge forward word by word; when a word is not in the list at all, restart after it. A window containing exactly the right number of words is a match."],
    editorial=["Brute force would cut each of up to n candidate substrings into <code>k</code> words and compare counts, O(n &middot; k &middot; wordLen). Instead, note that all words have the same length, so for a fixed offset <code>o</code> the text splits into the aligned pieces <code>s[o..o+L)</code>, <code>s[o+L..o+2L)</code>, ... and a match is a run of exactly <code>k</code> consecutive pieces that form the required multiset. Doing this for each of the <code>L = wordLen</code> offsets covers every possible start.",
               "For one offset, move a right pointer one piece at a time and keep the counts of pieces in the window. If the new piece is not in the word list, nothing containing it can match, so clear the window and restart after it. If its count exceeds the allowed count, advance the left pointer (dropping pieces) until the count is fine again. When the window holds <code>k</code> pieces it is a match: record the left index, and drop the leftmost piece so the window can continue. Each piece is added and removed at most once per offset, so the total work is O(n) piece operations per offset: O(n &middot; wordLen) character work for slicing, about 240,000 here. Sort the collected indices at the end."],
    time="O(n * wordLen)", space="O(k)",
    solution='''def findConcatenationStarts(s, words, wordLen):
    L = wordLen
    m = len(words) // L
    total = m * L
    n = len(s)
    res = []
    if total > n:
        return res
    need = {}
    for i in range(0, len(words), L):
        w = words[i:i + L]
        need[w] = need.get(w, 0) + 1
    for off in range(L):
        have = {}
        count = 0
        left = off
        for right in range(off, n - L + 1, L):
            w = s[right:right + L]
            if w in need:
                have[w] = have.get(w, 0) + 1
                count += 1
                while have[w] > need[w]:
                    have[s[left:left + L]] -= 1
                    left += L
                    count -= 1
                if count == m:
                    res.append(left)
                    have[s[left:left + L]] -= 1
                    left += L
                    count -= 1
            else:
                have.clear()
                count = 0
                left = right + L
    res.sort()
    return res
''',
    tests=[["barfoothefoobarman", "foobar", 3], ["wordgoodgoodgoodbestword", "goodgoodbestword", 4], ["wordgoodgoodgoodbestword", "wordgoodbestword", 4],
           ["a", "a", 1], ["a", "b", 1], ["aaaaa", "aa", 1], ["aaaaa", "aaaa", 2], ["abcabc", "abcabc", 3], ["abcab", "abcabc", 3], ["lingmindraboofooowingdingbarrwingmonkeypoundcake", "fooodingbarrwing", 4],
           ["abababab", "abab", 2], ["xyzxyzxyz", "abc", 3], ["abcdefabcdef", "abc" + "def", 3], ["bcabbcaabbccba", "abc", 1]],
)
_r = rnd(8510)
_v = ["abc", "abd", "bca", "cab", "cba"]
_s = "".join(_r.choice(_v) for _ in range(2600))
p["tests"].append([_s, "abc" + "abd" + "abd" + "bca" + "cab", 3])
_v = ["ab", "ba", "aa"]
_s = "".join(_r.choice(_v) for _ in range(3500))
p["tests"].append([_s, "ab" * 3 + "ba" * 3 + "aa" * 3, 2])
_s = rs(_r, "ab", 8000)
p["tests"].append([_s, "aabbabab", 1])
_v = ["xyzw", "xyzv"]
_s = "".join(_r.choice(_v) for _ in range(1500)) + "q" + "".join(_r.choice(_v) for _ in range(498))
p["tests"].append([_s, "xyzw" * 250 + "xyzv" * 250, 4])


def b_concat(s, words, wordLen):
    L = wordLen
    need = Counter(words[i:i + L] for i in range(0, len(words), L))
    total = len(words)
    out = []
    for i in range(len(s) - total + 1):
        if Counter(s[i + j:i + j + L] for j in range(0, total, L)) == need:
            out.append(i)
    return out


def g_concat(r):
    L = r.randint(1, 2)
    vocab = ["".join(r.choice("ab") for _ in range(L)) for _ in range(r.randint(1, 3))]
    ws = [r.choice(vocab) for _ in range(r.randint(1, 3))]
    if r.random() < 0.7:
        s = "".join(r.choice(vocab) for _ in range(r.randint(1, 7)))
    else:
        s = rs(r, "ab", r.randint(1, 14))
    return [s, "".join(ws), L]


def v_concat(tests):
    for t in tests:
        s, words, L = t["args"]
        assert is_lower(s) and is_lower(words) and len(s) <= 8000 and len(words) <= 5000
        assert 1 <= L <= 30 and L <= len(words) and len(words) % L == 0


CHECKS["concatenated-words-substring-starts"] = (b_concat, g_concat, "exact")
VALIDATE["concatenated-words-substring-starts"] = v_concat

p = add(
    id="count-substrings-uniform-letter-frequency", tier="extra", title="Substrings Where Every Letter Appears Exactly K Times", diff="Hard", topic=TOPIC,
    fn="countUniformSubstrings", params=[("s", "string"), ("k", "int")], ret="int", cmp="exact",
    desc="<p>Count the non-empty substrings of the lowercase string <code>s</code> in which <strong>every letter that appears at all appears exactly <code>k</code> times</strong>. Letters that do not occur in the substring are not constrained. Substrings are counted by start and end position.</p><pre>s = \"aabbcc\", k = 2\naa, bb, cc, aabb, bbcc, aabbcc  -> 6\nresult = 6</pre><pre>s = \"abab\", k = 1\na, b, a, b, ab, ba, ab -> 7   (\"aba\" has two a's)\nresult = 7</pre>",
    constraints=["1 &le; k &le; s.length &le; 8,000", "s consists of lowercase English letters"],
    hints=["Enumerating all substrings is O(n<sup>2</sup>) substrings with counting on top. Use the structure of valid substrings: how long can one be?",
           "If a valid substring has d different letters, its length must be exactly <code>d * k</code>. There are only 26 possible values of d.",
           "For each d from 1 to 26, slide a window of fixed length <code>d * k</code> and track how many letters currently have a count of exactly k. The window is valid exactly when that number equals d."],
    editorial=["A valid substring with <code>d</code> distinct letters, each used <code>k</code> times, has length <code>d &middot; k</code>. Since there are at most 26 letters, there are at most 26 candidate window lengths (and only those with <code>d &middot; k &le; n</code> matter). For each length, slide a fixed window over the string.",
               "Maintain the 26 letter counts and <code>eq</code>, the number of letters whose count is exactly <code>k</code>. When a count moves from k - 1 to k, <code>eq</code> grows; when it moves from k to k + 1, <code>eq</code> shrinks, and the reverse transitions apply when letters leave. A window of length <code>d &middot; k</code> is valid iff <code>eq == d</code>: then d letters already account for all <code>d &middot; k</code> positions, so nothing else can be inside. Total time O(26 &middot; n), space O(1)."],
    time="O(26 n)", space="O(1)",
    solution='''def countUniformSubstrings(s, k):
    n = len(s)
    codes = [ord(ch) - 97 for ch in s]
    ans = 0
    for d in range(1, min(26, n // k) + 1):
        size = d * k
        cnt = [0] * 26
        eq = 0
        for i in range(n):
            c = codes[i]
            cnt[c] += 1
            if cnt[c] == k:
                eq += 1
            elif cnt[c] == k + 1:
                eq -= 1
            if i >= size:
                c = codes[i - size]
                if cnt[c] == k:
                    eq -= 1
                elif cnt[c] == k + 1:
                    eq += 1
                cnt[c] -= 1
            if i >= size - 1 and eq == d:
                ans += 1
    return ans
''',
    tests=[["aabbcc", 2], ["abab", 1], ["a", 1], ["aaaa", 1], ["aaaa", 2], ["aaaa", 4], ["abc", 2], ["abcdefghijklmnopqrstuvwxyz", 1],
           ["abcdefghijklmnopqrstuvwxyzzyxwvutsrqponmlkjihgfedcba", 2], ["abcabcabc", 3], ["abcabcabc", 2], ["aabbaabbaabb", 4], ["zzzyyyxxx", 3]],
)
_r = rnd(8511)
p["tests"].append([rs(_r, "abc", 8000), 3])
p["tests"].append([rs(_r, "ab", 8000), 5])
_s = ""
while len(_s) < 8000:
    _b = list(LOWER[:_r.randint(2, 26)] * 2); _r.shuffle(_b)
    _s += "".join(_b)
p["tests"].append([_s[:8000], 2])
p["tests"].append([rs(_r, LOWER, 8000), 1])


def b_uni(s, k):
    n = len(s)
    ans = 0
    for i in range(n):
        for j in range(i + 1, n + 1):
            c = Counter(s[i:j])
            if all(v == k for v in c.values()):
                ans += 1
    return ans


def g_uni(r):
    n = r.randint(1, 14)
    return [rs(r, "abc", n), r.randint(1, min(n, 3))]


def v_uni(tests):
    for t in tests:
        s, k = t["args"]
        assert is_lower(s) and 1 <= k <= len(s) <= 8000


CHECKS["count-substrings-uniform-letter-frequency"] = (b_uni, g_uni, "exact")
VALIDATE["count-substrings-uniform-letter-frequency"] = v_uni
