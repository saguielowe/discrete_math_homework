#include <iostream>
#include <vector>
#include <algorithm>
#include <set>

using namespace std;

int a[105], b[105];
int n, m;
int route[105];
bool visited[105], flag = false;

void dfs(int u, int index) {
    route[index] = u;

    // 如果到达终点
    if (u == n - 1) {
        flag = true;
        for (int i = 0; i < index; i++) {
            cout << route[i] << "->";
        }
        cout << n - 1 << endl;
        return; // 到达终点直接返回，因为是初级路径，后面不可能再有点了
    }

    visited[u] = true; // 进门标记

    // 关键：处理重边。我们只访问独特的邻居。
    // 由于 b 已经排过序，我们可以轻松跳过重复的 v
    int last_v = -1;
    for (int i = a[u]; i < a[u + 1]; i++) {
        int v = b[i];

        // 1. 跳过自环 2. 跳过重复的重边 3. 跳过已在路径中的点
        if (v != u && v != last_v && !visited[v]) {
            dfs(v, index + 1);
            last_v = v; // 记录上一个处理过的邻居
        }
    }

    visited[u] = false; // 出门释放标记
}

int main() {
    // 关掉同步流，虽然这题量级小不需要，但 CS 大佬必备
    ios::sync_with_stdio(false);
    cin.tie(0);

    if (!(cin >> n >> m)) return 0;

    // 输入前向星指针数组
    for (int i = 0; i <= n; i++) {
        cin >> a[i];
    }
    // 输入边表
    for (int i = 0; i < m; i++) {
        cin >> b[i];
    }

    for (int i = 0; i < n; i++) {
        if (a[i] < a[i + 1]) {
            sort(b + a[i], b + a[i + 1]);
        }
    }

    dfs(0, 0);

    if (!flag) {
        cout << 0 << endl;
    }

    return 0;
}