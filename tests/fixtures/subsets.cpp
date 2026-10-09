class Solution {
public:
    vector<vector<int>> subsets(vector<int>& nums) {
        int n = nums.size();
        vector<vector<int>> res;
        for (int m = 0; m < (1 << n); m++) {
            vector<int> cur;
            for (int i = 0; i < n; i++) if (m >> i & 1) cur.push_back(nums[i]);
            res.push_back(cur);
        }
        return res;
    }
};
