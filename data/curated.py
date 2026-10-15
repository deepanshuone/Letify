"""Editorial decisions that are not part of a single problem: the roadmap order of topics,
which problems are interview staples, and topic renames."""

# The order topics appear in the Problems page and in the roadmap: each topic builds on the ones before it.
TOPIC_ORDER = [
    "Arrays & Hashing", "Strings", "Two Pointers", "Sliding Window", "Prefix Sums", "Stack",
    "Binary Search", "Sorting", "Linked List", "Trees", "Binary Search Trees", "Heap", "Intervals",
    "Greedy", "Backtracking", "Graphs", "Union Find", "Dynamic Programming", "Math", "Number Theory",
    "Bit Manipulation", "Matrix", "String Algorithms", "Range Queries", "Combinatorics", "Game Theory",
    "Geometry", "Simulation",
]

RENAME = {"Math & Bit Manipulation": "Math"}

# Bit tricks get their own topic.
TOPIC = {pid: "Bit Manipulation" for pid in [
    "single-number", "missing-number", "number-of-1-bits", "counting-bits-array", "power-of-two-check",
    "single-number-ii-triple", "single-number-iii-pair", "count-pairs-xor-in-range", "subset-xor-total-sum",
]}

# "must" = asked again and again in coding interviews (the classics). Everything else defaults to "common".
MUST = """
two-sum contains-duplicate valid-anagram valid-parentheses best-time-to-buy-and-sell-stock binary-search climbing-stairs
majority-element single-number missing-number valid-palindrome product-of-array-except-self longest-consecutive-sequence
maximum-subarray 3sum container-with-most-water longest-substring-without-repeating-characters daily-temperatures
search-in-rotated-sorted-array koko-eating-bananas merge-intervals coin-change number-of-islands subsets
top-k-frequent-elements two-sum-ii-sorted-input find-minimum-in-rotated-sorted-array longest-repeating-character-replacement
house-robber jump-game longest-increasing-subsequence decode-ways longest-common-subsequence insert-interval meeting-rooms-ii
permutations combination-sum rotate-image max-area-of-island rotting-oranges course-schedule trapping-rain-water
largest-rectangle-in-histogram sliding-window-maximum minimum-window-substring edit-distance median-of-two-sorted-arrays
first-missing-positive subarray-sum-equals-k group-anagrams-placeholder
reverse-linked-list merge-two-sorted-linked-lists remove-nth-node-from-end-of-list add-two-numbers-as-linked-lists
reorder-linked-list merge-k-sorted-linked-lists reverse-nodes-in-k-group linked-list-cycle-entry palindrome-linked-list
binary-tree-maximum-depth mirror-symmetric-binary-tree height-balanced-binary-tree-check binary-tree-diameter-in-edges
binary-tree-right-side-values binary-tree-good-nodes-count bst-validate bst-kth-smallest
last-stone-weight k-closest-points-to-origin task-scheduler running-medians-doubled
gas-station jump-game-ii partition-labels-greedy hand-of-straights-groups spiral-matrix set-matrix-zeroes
unique-paths partition-equal-subset-sum best-time-to-buy-and-sell-stock-with-cooldown perfect-squares-min-count
house-robber-ii coin-change-ii-count-ways target-sum-assign-signs-count longest-palindromic-substring-length
count-palindromic-substrings search-insert-position find-first-and-last-position redundant-connection number-of-provinces
network-delay-time cheapest-flights-within-k-stops min-cost-to-connect-all-points pacific-atlantic-water-flow
surrounded-regions-capture word-path-in-grid subsets-with-duplicates permutations-with-duplicates combination-sum-ii
n-queens-ii reverse-integer-int32-overflow count-primes-below-n happy-number power-of-two-check number-of-1-bits
counting-bits-array longest-valid-parentheses sort-three-colors-in-place next-permutation-array find-the-town-judge
alien-dictionary-integer-order minimum-cost-for-tickets
""".split()
TIER = {pid: "must" for pid in MUST}

# Near-duplicates of an earlier problem; the build skips them (the earlier one stays).
EXCLUDE = set("""
duplicate-zeros-shift-right wildcard-pattern-match smallest-range-covering-k-lists tree-surveillance-cameras
partition-around-pivot-keep-order rank-among-distinct-rearrangements minimum-replacements-to-anagram
""".split())
