/* Study plans: hand-ordered paths through the problem bank. Ids are checked against the data by the unit tests. */

export interface PlanSection {
  title: string;
  /** What the learner should take away from this section. */
  note: string;
  ids: string[];
}

export interface Plan {
  id: string;
  title: string;
  level: 'Beginner' | 'Intermediate' | 'Advanced';
  blurb: string;
  sections: PlanSection[];
}

export const PLANS: Plan[] = [
  {
    id: 'foundations',
    title: 'Foundations',
    level: 'Beginner',
    blurb: 'Every Easy problem, ordered so each one teaches a tool the next one uses. Start here if arrays and loops are all you know.',
    sections: [
      { title: 'Arrays and hash maps', note: 'Remember what you have seen instead of searching for it again.', ids: ['contains-duplicate', 'valid-anagram', 'two-sum', 'majority-element', 'plus-one', 'find-the-town-judge'] },
      { title: 'Pointers and strings', note: 'Walk an array from both ends, or with two indexes at different speeds.', ids: ['valid-palindrome', 'is-subsequence', 'best-time-to-buy-and-sell-stock', 'move-zeroes', 'remove-duplicates-from-sorted-array'] },
      { title: 'Strings', note: 'Count characters, compare neighbours, and fold a string into numbers.', ids: ['first-unique-character', 'isomorphic-strings', 'run-length-compressed-length', 'longest-palindrome-by-rearranging'] },
      { title: 'Bits and math', note: 'A few tricks that turn a loop into a one-liner.', ids: ['single-number', 'missing-number', 'integer-square-root', 'number-of-1-bits', 'happy-number'] },
      { title: 'Stack, search and your first DP', note: 'Three patterns you will meet again in every later plan.', ids: ['valid-parentheses', 'binary-search', 'search-insert-position', 'climbing-stairs', 'min-cost-climbing-stairs', 'pascals-triangle', 'unique-paths', 'last-stone-weight'] },
    ],
  },
  {
    id: 'interview-core',
    title: 'Interview Core',
    level: 'Intermediate',
    blurb: 'The patterns that cover most coding interviews, one or two problems each. Finish this and you can recognise what a question is really asking.',
    sections: [
      { title: 'Arrays and hashing', note: 'Prefix sums, counting and bucket tricks.', ids: ['product-of-array-except-self', 'top-k-frequent-elements', 'longest-consecutive-sequence', 'subarray-sum-equals-k'] },
      { title: 'Two pointers', note: 'Sorted input plus two indexes often beats a hash map.', ids: ['two-sum-ii-sorted-input', '3sum', 'container-with-most-water'] },
      { title: 'Sliding window', note: 'Grow the right edge, shrink the left when the window breaks a rule.', ids: ['longest-substring-without-repeating-characters', 'longest-repeating-character-replacement', 'minimum-size-subarray-sum'] },
      { title: 'Stack', note: 'When you need the nearest bigger or smaller thing.', ids: ['daily-temperatures'] },
      { title: 'Binary search', note: 'Search the answer, not just the array.', ids: ['search-in-rotated-sorted-array', 'find-minimum-in-rotated-sorted-array', 'koko-eating-bananas'] },
      { title: 'Intervals and greedy', note: 'Sort first, then make the locally best choice.', ids: ['merge-intervals', 'insert-interval', 'meeting-rooms-ii', 'jump-game'] },
      { title: 'Dynamic programming', note: 'Define the state, write the recurrence, then optimise the memory.', ids: ['maximum-subarray', 'house-robber', 'coin-change', 'longest-increasing-subsequence', 'decode-ways', 'longest-common-subsequence'] },
      { title: 'Graphs and grids', note: 'BFS for shortest, DFS for components, a heap for weights.', ids: ['number-of-islands', 'max-area-of-island', 'rotting-oranges', 'course-schedule', 'network-delay-time'] },
      { title: 'Backtracking and matrices', note: 'Choose, explore, undo.', ids: ['subsets', 'permutations', 'combination-sum', 'rotate-image'] },
    ],
  },
  {
    id: 'windows-pointers',
    title: 'Sliding Window and Two Pointers',
    level: 'Intermediate',
    blurb: 'One family of ideas, twelve problems, from a palindrome check to the hardest window question.',
    sections: [
      { title: 'Two pointers', note: 'Move from both ends, or chase with a second index.', ids: ['valid-palindrome', 'is-subsequence', 'two-sum-ii-sorted-input', 'container-with-most-water', '3sum'] },
      { title: 'Windows that grow and shrink', note: 'Keep a running summary of the window instead of recounting it.', ids: ['best-time-to-buy-and-sell-stock', 'longest-substring-without-repeating-characters', 'longest-repeating-character-replacement', 'minimum-size-subarray-sum'] },
      { title: 'Advanced windows', note: 'Add a deque or a second frequency table to the window.', ids: ['minimum-window-substring', 'sliding-window-maximum', 'trapping-rain-water'] },
    ],
  },
  {
    id: 'dp-bootcamp',
    title: 'Dynamic Programming Bootcamp',
    level: 'Intermediate',
    blurb: 'From climbing stairs to burst balloons. Each section adds one idea to the state of the table.',
    sections: [
      { title: 'One dimension', note: 'The answer for i depends on a few earlier answers.', ids: ['climbing-stairs', 'min-cost-climbing-stairs', 'house-robber', 'maximum-subarray', 'decode-ways'] },
      { title: 'Counting and choosing', note: 'The state is a target, a count or a length.', ids: ['pascals-triangle', 'coin-change', 'longest-increasing-subsequence'] },
      { title: 'Two dimensions', note: 'Two sequences, one table.', ids: ['longest-common-subsequence', 'edit-distance', 'regular-expression-matching'] },
      { title: 'Ranges', note: 'The state is a range, and you choose the last or the split point.', ids: ['longest-valid-parentheses', 'burst-balloons'] },
    ],
  },
  {
    id: 'graphs-backtracking',
    title: 'Graphs, Grids and Backtracking',
    level: 'Advanced',
    blurb: 'Explore everything that can happen, then prune. Grids first, then real graphs, then the search problems.',
    sections: [
      { title: 'Grids', note: 'A grid is a graph where the neighbours are the four directions.', ids: ['number-of-islands', 'max-area-of-island', 'rotting-oranges', 'rotate-image', 'longest-increasing-path-in-a-matrix'] },
      { title: 'Graph algorithms', note: 'Topological order and shortest paths.', ids: ['course-schedule', 'network-delay-time'] },
      { title: 'Backtracking', note: 'Build a candidate step by step and abandon it early.', ids: ['subsets', 'permutations', 'combination-sum', 'n-queens-ii', 'partition-to-k-equal-sum-subsets'] },
    ],
  },
  {
    id: 'strings-heaps-greedy',
    title: 'Strings, Heaps and Greedy',
    level: 'Intermediate',
    blurb: 'Palindromes and anagrams, priority queues, and greedy choices you can prove. A good second plan after Interview Core.',
    sections: [
      { title: 'Strings', note: 'Expand around a centre, slide a window, or scan once with counts.', ids: ['longest-palindromic-substring-length', 'count-palindromic-substrings', 'count-anagram-windows', 'minimum-deletions-a-before-b'] },
      { title: 'Heaps', note: 'Keep only the best few items and always take the smallest or largest.', ids: ['k-closest-points-to-origin', 'task-scheduler'] },
      { title: 'Greedy', note: 'Make the locally best choice and be able to say why it is safe.', ids: ['gas-station', 'jump-game-ii'] },
      { title: 'Matrix tricks', note: 'Walk and rewrite a grid without extra space.', ids: ['spiral-matrix', 'set-matrix-zeroes'] },
    ],
  },
  {
    id: 'patterns-round-two',
    title: 'Patterns, Round Two',
    level: 'Intermediate',
    blurb: 'More practice with the patterns you already know: search on the answer, intervals, union find, and one more DP.',
    sections: [
      { title: 'Binary search and windows', note: 'Search the range of answers, or grow a window while a count stays small.', ids: ['find-first-and-last-position', 'capacity-to-ship-packages', 'max-consecutive-ones-iii'] },
      { title: 'Intervals and stacks', note: 'Sort first, then sweep once.', ids: ['non-overlapping-intervals', 'minimum-number-of-arrows', 'car-fleet'] },
      { title: 'Union find and graphs', note: 'Merge groups instead of walking the graph again.', ids: ['number-of-provinces', 'redundant-connection', 'shortest-path-in-binary-matrix'] },
      { title: 'DP and backtracking', note: 'Define the state, then count or search.', ids: ['partition-equal-subset-sum', 'best-time-to-buy-and-sell-stock-with-cooldown', 'combination-sum-ii'] },
    ],
  },
  {
    id: 'arrays-prefix-intervals',
    title: "Arrays, Prefix Sums and Intervals",
    level: 'Intermediate',
    blurb: "Hashing, running totals, difference arrays and interval sweeps. These are the tools behind most subarray questions.",
    sections: [
      { title: "Arrays & Hashing", note: "Count, group and look up instead of rescanning.", ids: ['set-mismatch', 'intersect-arrays-with-multiplicity', 'shortest-subarray-with-same-degree', 'rotate-array-by-k-steps', 'merge-two-sorted-int-arrays', 'longest-balanced-binary-subarray', 'count-subarrays-sum-divisible-by-k', 'longest-subarray-with-sum-exactly-k', 'four-array-sum-zero-count', 'max-pair-sum-equal-digit-sum', 'next-permutation-array', 'sort-three-colors-in-place', 'subarrays-with-exactly-k-distinct', 'count-equal-012-subarrays'] },
      { title: "Prefix Sums", note: "Precompute running totals so any range costs O(1).", ids: ['range-sum-query-batch', 'flight-bookings-seat-totals', 'car-pooling-capacity-check', 'count-subarrays-with-sum-in-range'] },
      { title: "Intervals", note: "Sort by start, then sweep once.", ids: ['interval-lists-intersection', 'max-overlap-after-each-booking'] },
    ],
  },
  {
    id: 'pointers-windows-search',
    title: "Pointers, Windows and Search",
    level: 'Intermediate',
    blurb: "Two pointers, sliding windows and binary search on indexes and on answers.",
    sections: [
      { title: "Two Pointers", note: "Move two indexes towards the answer.", ids: ['sorted-squares-two-pointers', 'sorted-arrays-common-elements', 'boats-to-carry-people', 'four-sum-unique-quadruplets'] },
      { title: "Sliding Window", note: "Grow the window on the right, shrink it on the left.", ids: ['max-sum-window-of-size-k', 'subarrays-with-product-below-k', 'longest-ones-after-one-deletion', 'min-removals-from-ends-to-reach-sum', 'shortest-window-containing-subsequence', 'min-k-bit-flips-to-all-ones'] },
      { title: "Binary Search", note: "Halve the search space, on the index or on the answer.", ids: ['count-negatives-in-sorted-grid', 'complete-staircase-rows', 'search-flattened-sorted-grid', 'rotated-array-contains-with-duplicates', 'lone-value-in-sorted-pairs', 'earliest-day-for-bouquets', 'maximize-min-gap-between-balls', 'kth-smallest-in-sorted-grid', 'kth-smallest-pair-gap', 'min-max-gap-after-adding-stations'] },
    ],
  },
  {
    id: 'stacks-and-strings',
    title: "Stacks and Strings",
    level: 'Intermediate',
    blurb: "Monotonic stacks, parsing, string scans, and the algorithms behind fast matching.",
    sections: [
      { title: "Stack", note: "Keep a stack of candidates that are still open.", ids: ['min-insertions-to-balance-brackets', 'final-prices-with-discount', 'next-greater-circular-array', 'sum-of-subarray-minimums-mod', 'remove-k-digits-smallest-number', 'asteroid-collision-survivors', 'valid-stack-push-pop-order', 'has-132-pattern', 'maximal-rectangle-of-ones', 'evaluate-bracket-expression'] },
      { title: "Strings", note: "Scan once with counts, or expand around a centre.", ids: ['string-rotation-check', 'add-binary-strings', 'roman-numeral-to-integer', 'integer-to-roman-numeral', 'multiply-decimal-strings', 'zigzag-conversion-rows', 'longest-substring-each-char-at-least-k', 'longest-even-vowel-substring', 'minimum-window-subsequence-length', 'longest-duplicate-substring-length'] },
      { title: "String Algorithms", note: "Reuse what you already matched: borders, Z-values and rolling hashes.", ids: ['first-occurrence-of-needle', 'count-overlapping-occurrences', 'smallest-repeating-unit-length', 'longest-border-length', 'repeated-string-match-count', 'z-function-sum', 'lexicographically-smallest-rotation', 'wildcard-pattern-match', 'count-distinct-substrings', 'longest-shared-substring-two-strings'] },
    ],
  },
  {
    id: 'dp-lines-grids',
    title: "Dynamic Programming: Lines and Grids",
    level: 'Intermediate',
    blurb: "Linear recurrences first, then grids. Each state is a position and the answer builds from smaller ones.",
    sections: [
      { title: "Linear DP", note: "Define dp[i] and write how it depends on earlier states.", ids: ['tribonacci-modulo-dp', 'broken-steps-staircase-ways', 'house-robber-ii', 'delete-and-earn', 'coin-change-ii-count-ways', 'perfect-squares-min-count', 'minimum-cost-for-tickets', 'count-longest-increasing-subsequences', 'stock-profit-at-most-k-transactions', 'three-nonoverlapping-windows-max-sum'] },
      { title: "Grid DP", note: "dp[r][c] depends on the cell above and the cell to the left.", ids: ['grid-paths-with-obstacles', 'minimum-path-sum-grid', 'triangle-min-path-sum', 'largest-square-of-ones', 'count-all-ones-squares', 'grid-exit-paths-count', 'two-budget-item-picking', 'grid-paths-sum-divisible-by-k', 'dungeon-minimum-starting-health', 'two-robots-cherry-collection'] },
    ],
  },
  {
    id: 'dp-knapsack-strings',
    title: "Dynamic Programming: Knapsack and Strings",
    level: 'Advanced',
    blurb: "Choose or skip items, compare two strings, and game states. The hard part is picking the state.",
    sections: [
      { title: "Knapsack and games", note: "Item index plus a budget, or a range of piles, is the state.", ids: ['zero-one-knapsack-max-value', 'unbounded-knapsack-max-value', 'target-sum-assign-signs-count', 'last-stone-weight-ii-min-remaining', 'combination-sum-iv-ordered-count', 'minimum-score-triangulation-polygon', 'can-i-win-bitmask-game', 'predict-the-winner-pile-ends', 'minimum-cost-to-merge-stones-k-piles', 'shortest-walk-visiting-all-nodes'] },
      { title: "Two-string DP", note: "dp[i][j] compares a prefix of each string.", ids: ['longest-common-substring-length', 'equalize-strings-by-deletions', 'longest-palindromic-subsequence-length', 'minimum-ascii-delete-sum-equal-strings', 'interleaving-string-check', 'wildcard-pattern-matching', 'longest-repeating-subsequence-distinct-positions', 'longest-common-subsequence-of-three-strings', 'count-distinct-palindromic-subsequences', 'scramble-string-check'] },
    ],
  },
  {
    id: 'graphs-trees-lists',
    title: "Graphs, Trees and Linked Lists",
    level: 'Intermediate',
    blurb: "Grids, shortest paths, spanning trees, binary trees, BSTs and pointer rewiring.",
    sections: [
      { title: "Graphs", note: "Model it as nodes and edges, then pick BFS, DFS or Dijkstra.", ids: ['flood-fill-recolor', 'island-perimeter-length', 'star-graph-center', 'path-exists-in-undirected-graph', 'surrounded-regions-capture', 'pacific-atlantic-water-flow', 'walls-and-gates-distance', 'distinct-island-shapes-count', 'count-sub-islands-contained', 'shortest-bridge-between-islands', 'count-paths-in-a-dag', 'is-graph-bipartite-edge-list', 'cheapest-flights-within-k-stops', 'path-with-minimum-effort', 'min-cost-to-connect-all-points', 'number-of-ways-to-arrive-at-destination', 'minimum-obstacle-removal-grid', 'swim-in-rising-water-grid', 'alien-dictionary-integer-order', 'mst-critical-and-pseudo-critical-edges'] },
      { title: "Trees", note: "Recurse on the left and right child and combine the answers.", ids: ['binary-tree-maximum-depth', 'binary-tree-contains-subtree', 'mirror-symmetric-binary-tree', 'height-balanced-binary-tree-check', 'binary-tree-diameter-in-edges', 'binary-tree-zigzag-levels', 'binary-tree-right-side-values', 'binary-tree-good-nodes-count', 'binary-tree-minimum-cameras', 'binary-tree-max-bst-subtree-sum'] },
      { title: "Binary Search Trees", note: "Use the ordering of a BST, and in-order traversal gives sorted values.", ids: ['bst-range-sum', 'bst-two-sum-iv', 'bst-minimum-absolute-difference', 'bst-validate', 'bst-kth-smallest', 'bst-insert-level-order', 'bst-recover-swapped-values', 'tree-house-robber-iii-money', 'tree-surveillance-cameras', 'bst-same-shape-reorderings'] },
      { title: "Linked List", note: "Rewire the next pointers carefully, one step at a time.", ids: ['reverse-linked-list', 'merge-two-sorted-linked-lists', 'palindrome-linked-list', 'remove-nth-node-from-end-of-list', 'linked-list-cycle-entry', 'add-two-numbers-as-linked-lists', 'reorder-linked-list', 'partition-linked-list-around-value', 'reverse-nodes-in-k-group', 'merge-k-sorted-linked-lists'] },
    ],
  },
  {
    id: 'search-greedy-heaps-math',
    title: "Backtracking, Greedy, Heaps and Math",
    level: 'Intermediate',
    blurb: "The rest of the toolbox: exhaustive search with pruning, greedy proofs, priority queues, number tricks and matrices.",
    sections: [
      { title: "Backtracking", note: "Choose, explore, undo.", ids: ['binary-watch-times', 'subset-xor-total-sum', 'subsets-with-duplicates', 'permutations-with-duplicates', 'combinations-n-choose-k', 'word-path-in-grid', 'balanced-bracket-sequences', 'divisible-arrangements-count', 'walk-every-cell-count', 'expression-add-operators-count'] },
      { title: "Greedy", note: "Take the best local choice and be able to say why it is safe.", ids: ['assign-cookies', 'lemonade-change-stand', 'maximum-units-on-a-truck', 'partition-labels-greedy', 'queue-reconstruction-by-height', 'two-city-scheduling-cost', 'wiggle-subsequence-length', 'hand-of-straights-groups', 'course-schedule-max-courses', 'minimum-refueling-stops'] },
      { title: "Heap", note: "Always take the smallest or largest of what is left.", ids: ['minimum-cost-to-connect-ropes', 'running-kth-largest-heap', 'merge-k-sorted-rows', 'furthest-building-with-ladders', 'k-smallest-pair-sums', 'kth-smallest-in-sorted-matrix-heap', 'super-ugly-number-heap', 'single-threaded-cpu-order', 'running-medians-doubled', 'maximum-team-performance-heap'] },
      { title: "Math & Bit Manipulation", note: "Digits, overflow and a few bit tricks.", ids: ['palindrome-integer-check', 'excel-column-title-to-number', 'factorial-trailing-zeros-count', 'counting-bits-array', 'power-of-two-check', 'reverse-integer-int32-overflow', 'nth-digit-of-concatenated-integers', 'single-number-ii-triple', 'single-number-iii-pair', 'count-digit-one-occurrences', 'count-pairs-xor-in-range'] },
      { title: "Number Theory", note: "Primes, gcd and modular arithmetic.", ids: ['count-primes-below-n', 'modular-exponentiation-fast', 'super-pow-digit-exponent', 'binomial-mod-small-prime'] },
      { title: "Matrix", note: "Walk and rewrite a grid carefully.", ids: ['toeplitz-matrix-check', 'diagonal-traverse-flat', 'game-of-life-next-generation', 'valid-sudoku-board', 'max-sum-submatrix-at-most-k'] },
    ],
  },
  {
    id: 'hard-mode',
    title: 'Hard Mode',
    level: 'Advanced',
    blurb: 'The hardest problems from the first 105. Brute force will not finish here, so you have to find the structure. More Hard problems sit at the end of every topic plan.',
    sections: [
      { title: 'Arrays and search', note: 'Use the shape of the data to skip most of the work.', ids: ['median-of-two-sorted-arrays', 'first-missing-positive', 'trapping-rain-water'] },
      { title: 'Windows and stacks', note: 'Keep only the candidates that can still win.', ids: ['largest-rectangle-in-histogram', 'sliding-window-maximum', 'minimum-window-substring', 'longest-valid-parentheses'] },
      { title: 'DP and search', note: 'State design is the whole problem.', ids: ['edit-distance', 'burst-balloons', 'regular-expression-matching', 'n-queens-ii', 'partition-to-k-equal-sum-subsets', 'longest-increasing-path-in-a-matrix', 'palindrome-partitioning-ii', 'distinct-subsequences-count'] },
      { title: 'Greedy, heaps and graphs', note: 'Pick the right data structure and the loop becomes short.', ids: ['candy', 'ipo', 'number-of-islands-ii', 'critical-connections-in-a-network'] },
      { title: 'Strings and searching the answer', note: 'Binary search on the result, and a deque that keeps the best start.', ids: ['shortest-palindrome-length', 'split-array-largest-sum', 'shortest-subarray-with-sum-at-least-k'] },
    ],
  },
];

export const PLAN_BY_ID: ReadonlyMap<string, Plan> = new Map(PLANS.map((p) => [p.id, p]));

export const planIds = (p: Plan): string[] => p.sections.flatMap((s) => s.ids);
