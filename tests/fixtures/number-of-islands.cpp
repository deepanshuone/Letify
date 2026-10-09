class Solution {
public:
    int numIslands(vector<vector<int>>& g) {
        int R = g.size(), C = g[0].size(), cnt = 0;
        for (int r = 0; r < R; r++) for (int c = 0; c < C; c++) if (g[r][c] == 1) {
            cnt++;
            vector<pair<int,int>> st{{r,c}}; g[r][c] = 0;
            while (!st.empty()) {
                auto [y, x] = st.back(); st.pop_back();
                int dy[4] = {1,-1,0,0}, dx[4] = {0,0,1,-1};
                for (int k = 0; k < 4; k++) {
                    int ny = y + dy[k], nx = x + dx[k];
                    if (ny >= 0 && ny < R && nx >= 0 && nx < C && g[ny][nx] == 1) { g[ny][nx] = 0; st.push_back({ny,nx}); }
                }
            }
        }
        return cnt;
    }
};
