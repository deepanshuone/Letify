class Solution {
    public String minWindow(String s, String t) {
        int[] need = new int[128];
        for (char c : t.toCharArray()) need[c]++;
        int missing = t.length(), bs = 0, bl = Integer.MAX_VALUE, left = 0;
        for (int r = 0; r < s.length(); r++) {
            if (need[s.charAt(r)] > 0) missing--;
            need[s.charAt(r)]--;
            while (missing == 0) {
                if (r - left + 1 < bl) { bl = r - left + 1; bs = left; }
                need[s.charAt(left)]++;
                if (need[s.charAt(left)] > 0) missing++;
                left++;
            }
        }
        return bl == Integer.MAX_VALUE ? "" : s.substring(bs, bs + bl);
    }
}
