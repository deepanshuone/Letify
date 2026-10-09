class Solution {
    public int[][] subsets(int[] nums) {
        int n = nums.length;
        int[][] res = new int[1 << n][];
        for (int m = 0; m < (1 << n); m++) {
            int c = Integer.bitCount(m); int[] cur = new int[c]; int k = 0;
            for (int i = 0; i < n; i++) if ((m >> i & 1) == 1) cur[k++] = nums[i];
            res[m] = cur;
        }
        return res;
    }
}
