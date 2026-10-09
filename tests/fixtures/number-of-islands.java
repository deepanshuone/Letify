class Solution {
    public int numIslands(int[][] g) {
        int R = g.length, C = g[0].length, cnt = 0;
        for (int r = 0; r < R; r++) for (int c = 0; c < C; c++) if (g[r][c] == 1) {
            cnt++;
            ArrayDeque<int[]> st = new ArrayDeque<>();
            st.push(new int[]{r, c}); g[r][c] = 0;
            int[] dy = {1,-1,0,0}, dx = {0,0,1,-1};
            while (!st.isEmpty()) {
                int[] cur = st.pop();
                for (int k = 0; k < 4; k++) {
                    int ny = cur[0] + dy[k], nx = cur[1] + dx[k];
                    if (ny >= 0 && ny < R && nx >= 0 && nx < C && g[ny][nx] == 1) { g[ny][nx] = 0; st.push(new int[]{ny, nx}); }
                }
            }
        }
        return cnt;
    }
}
