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
      { title: 'Arrays and hash maps', note: 'Remember what you have seen instead of searching for it again.', ids: ['contains-duplicate', 'valid-anagram', 'two-sum', 'majority-element', 'plus-one'] },
      { title: 'Pointers and strings', note: 'Walk an array from both ends, or with two indexes at different speeds.', ids: ['valid-palindrome', 'is-subsequence', 'best-time-to-buy-and-sell-stock'] },
      { title: 'Bits and math', note: 'A few tricks that turn a loop into a one-liner.', ids: ['single-number', 'missing-number', 'integer-square-root'] },
      { title: 'Stack, search and your first DP', note: 'Three patterns you will meet again in every later plan.', ids: ['valid-parentheses', 'binary-search', 'climbing-stairs', 'min-cost-climbing-stairs', 'pascals-triangle'] },
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
    id: 'hard-mode',
    title: 'Hard Mode',
    level: 'Advanced',
    blurb: 'All 13 Hard problems. Brute force will not finish here, so you have to find the structure.',
    sections: [
      { title: 'Arrays and search', note: 'Use the shape of the data to skip most of the work.', ids: ['median-of-two-sorted-arrays', 'first-missing-positive', 'trapping-rain-water'] },
      { title: 'Windows and stacks', note: 'Keep only the candidates that can still win.', ids: ['largest-rectangle-in-histogram', 'sliding-window-maximum', 'minimum-window-substring', 'longest-valid-parentheses'] },
      { title: 'DP and search', note: 'State design is the whole problem.', ids: ['edit-distance', 'burst-balloons', 'regular-expression-matching', 'n-queens-ii', 'partition-to-k-equal-sum-subsets', 'longest-increasing-path-in-a-matrix'] },
    ],
  },
];

export const PLAN_BY_ID: ReadonlyMap<string, Plan> = new Map(PLANS.map((p) => [p.id, p]));

export const planIds = (p: Plan): string[] => p.sections.flatMap((s) => s.ids);
