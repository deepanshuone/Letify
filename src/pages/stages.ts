import type { Diff } from '../types';

export const STAGES: { diff: Diff; name: string; blurb: string }[] = [
  { diff: 'Easy', name: 'Basic', blurb: 'Hash maps, stacks, binary search and your first dynamic program. Learn to ask what you can remember instead of recompute.' },
  { diff: 'Medium', name: 'Intermediate', blurb: 'Two pointers, sliding windows, intervals, graphs and backtracking, each with the standard pattern.' },
  { diff: 'Hard', name: 'Advanced', blurb: 'Monotonic stacks, window tricks and 2-D DP, where brute force no longer finishes in time.' },
];
