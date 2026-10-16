/* Problems that candidates commonly report in interviews at each company. These lists are compiled from general
   knowledge of widely discussed interview questions. They are NOT official and are not verified against any company.
   Order is roughly most-reported first. Ids are checked against the problem bank by the unit tests. */

export interface CompanyList {
  name: string;
  ids: string[];
}

export const COMPANY_LISTS: CompanyList[] = [
  {
    name: 'Google',
    ids: ['two-sum', 'longest-substring-without-repeating-characters', 'median-of-two-sorted-arrays', 'merge-intervals', 'number-of-islands', 'course-schedule', 'trapping-rain-water', 'copy-list-with-random-pointer', 'lowest-common-ancestor-binary-tree', 'top-k-frequent-elements', 'minimum-window-substring', 'serialize-binary-tree-null-markers', 'search-in-rotated-sorted-array', 'container-with-most-water', '3sum', 'longest-palindromic-substring-length', 'meeting-rooms-ii', 'rotting-oranges', 'pacific-atlantic-water-flow', 'edit-distance', 'regular-expression-matching', 'decode-ways', 'subsets', 'permutations', 'combination-sum', 'network-delay-time'],
  },
  {
    name: 'Microsoft',
    ids: ['reverse-linked-list', 'valid-parentheses', 'lowest-common-ancestor-binary-tree', 'binary-tree-level-order-groups', 'merge-intervals', 'longest-substring-without-repeating-characters', 'number-of-islands', 'two-sum', 'linked-list-has-cycle', 'find-minimum-in-rotated-sorted-array', 'house-robber', 'coin-change', 'rotate-image', 'spiral-matrix', 'set-matrix-zeroes', 'tree-maximum-path-sum', 'construct-tree-from-preorder-inorder', 'product-of-array-except-self', 'best-time-to-buy-and-sell-stock', 'jump-game', 'gas-station', 'unique-paths'],
  },
  {
    name: 'Amazon',
    ids: ['lru-cache-simulation', 'top-k-frequent-elements', 'merge-intervals', 'insert-interval', 'number-of-islands', 'course-schedule', 'task-scheduler', 'sliding-window-maximum', 'maximum-subarray', 'daily-temperatures', 'copy-list-with-random-pointer', 'binary-tree-level-order-groups', 'two-sum', 'reverse-linked-list', '3sum', 'longest-palindromic-substring-length', 'rotting-oranges', 'meeting-rooms-ii', 'min-cost-climbing-stairs', 'decode-ways', 'combination-sum', 'permutations'],
  },
  {
    name: 'Meta',
    ids: ['two-sum', 'valid-parentheses', 'lowest-common-ancestor-binary-tree', 'copy-list-with-random-pointer', 'serialize-binary-tree-null-markers', 'reverse-linked-list', 'merge-intervals', 'longest-substring-without-repeating-characters', 'container-with-most-water', 'trapping-rain-water', 'binary-tree-level-order-groups', 'subsets', 'permutations', 'number-of-islands', 'top-k-frequent-elements', 'product-of-array-except-self', 'sliding-window-maximum', 'linked-list-has-cycle', 'median-of-two-sorted-arrays', 'minimum-window-substring'],
  },
  {
    name: 'Apple',
    ids: ['reverse-linked-list', 'linked-list-has-cycle', 'two-sum', 'valid-parentheses', 'merge-intervals', 'lowest-common-ancestor-binary-tree', 'search-in-rotated-sorted-array', 'best-time-to-buy-and-sell-stock', 'product-of-array-except-self', 'longest-substring-without-repeating-characters', 'daily-temperatures', 'climbing-stairs', 'house-robber', 'binary-tree-level-order-groups', 'insert-interval'],
  },
  {
    name: 'Uber',
    ids: ['meeting-rooms-ii', 'merge-intervals', 'lru-cache-simulation', 'course-schedule', 'network-delay-time', 'trapping-rain-water', 'number-of-islands', 'rotting-oranges', 'jump-game', 'gas-station', 'median-of-two-sorted-arrays', 'sliding-window-maximum', 'minimum-window-substring', 'task-scheduler', 'copy-list-with-random-pointer'],
  },
  {
    name: 'Adobe',
    ids: ['merge-intervals', 'longest-substring-without-repeating-characters', 'lowest-common-ancestor-binary-tree', 'top-k-frequent-elements', 'two-sum', 'valid-parentheses', 'reverse-linked-list', 'spiral-matrix', 'rotate-image', 'set-matrix-zeroes', 'subsets', 'permutations', 'container-with-most-water', '3sum', 'decode-ways', 'edit-distance', 'longest-common-subsequence', 'trapping-rain-water'],
  },
  {
    name: 'Bloomberg',
    ids: ['valid-parentheses', 'merge-intervals', 'two-sum', 'top-k-frequent-elements', 'median-of-two-sorted-arrays', 'minimum-window-substring', 'search-in-rotated-sorted-array', 'find-minimum-in-rotated-sorted-array', 'linked-list-has-cycle', 'reverse-linked-list', 'binary-tree-level-order-groups', 'lowest-common-ancestor-binary-tree', 'construct-tree-from-preorder-inorder', 'daily-temperatures', 'longest-substring-without-repeating-characters', 'number-of-islands', 'coin-change', 'house-robber', 'insert-interval'],
  },
  {
    name: 'Oracle',
    ids: ['reverse-linked-list', 'linked-list-has-cycle', 'two-sum', 'merge-intervals', 'valid-parentheses', 'lowest-common-ancestor-binary-tree', 'binary-tree-level-order-groups', 'number-of-islands', 'course-schedule', 'rotting-oranges', 'coin-change', 'climbing-stairs', 'unique-paths', 'best-time-to-buy-and-sell-stock', 'product-of-array-except-self', 'longest-increasing-subsequence'],
  },
  {
    name: 'Netflix',
    ids: ['two-sum', 'lru-cache-simulation', 'top-k-frequent-elements', 'merge-intervals', 'median-of-two-sorted-arrays', 'sliding-window-maximum', 'minimum-window-substring', 'course-schedule', 'number-of-islands', 'trapping-rain-water', 'task-scheduler', 'copy-list-with-random-pointer', 'binary-tree-level-order-groups', 'construct-tree-from-preorder-inorder', 'jump-game'],
  },
  {
    name: 'Salesforce',
    ids: ['two-sum', 'reverse-linked-list', 'valid-parentheses', 'merge-intervals', 'lowest-common-ancestor-binary-tree', 'longest-substring-without-repeating-characters', 'number-of-islands', 'course-schedule', 'container-with-most-water', '3sum', 'subsets', 'permutations', 'combination-sum', 'climbing-stairs', 'house-robber', 'edit-distance'],
  },
  {
    name: 'Goldman Sachs',
    ids: ['two-sum', 'merge-intervals', 'best-time-to-buy-and-sell-stock', 'maximum-subarray', 'valid-parentheses', 'median-of-two-sorted-arrays', 'meeting-rooms-ii', 'task-scheduler', 'longest-increasing-subsequence', 'coin-change', 'unique-paths', 'decode-ways', 'partition-equal-subset-sum', 'sliding-window-maximum', 'gas-station'],
  },
];
