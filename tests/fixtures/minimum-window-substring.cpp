class Solution {
public:
    string minWindow(string s, string t) {
        unordered_map<char,int> need;
        for (char c : t) need[c]++;
        int missing = t.size(), bs = 0, bl = INT_MAX, left = 0;
        for (int r = 0; r < (int)s.size(); r++) {
            if (need[s[r]] > 0) missing--;
            need[s[r]]--;
            while (missing == 0) {
                if (r - left + 1 < bl) { bl = r - left + 1; bs = left; }
                need[s[left]]++;
                if (need[s[left]] > 0) missing++;
                left++;
            }
        }
        return bl == INT_MAX ? "" : s.substr(bs, bl);
    }
};
