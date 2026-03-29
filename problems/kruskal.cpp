#include <iostream>
#include <vector>
#include <algorithm>

using namespace std;

// 边的结构体
struct Edge {
    int u, v, w;
    bool operator<(const Edge& other) const {
        return w < other.w; // 按权值升序排列
    }
};

// 并查集类
struct DSU {
    vector<int> parent;
    DSU(int n) {
        parent.resize(n + 1);
        for (int i = 1; i <= n; i++) parent[i] = i;
    }

    // 查找根节点 + 路径压缩
    int find(int x) {
        if (parent[x] == x) return x;
        return parent[x] = find(parent[x]); // 这一行是灵魂，把 $O(\log n)$ 降到几乎 $O(1)$
    }

    // 合并
    bool unite(int x, int y) {
        int rootX = find(x);
        int rootY = find(y);
        if (rootX != rootY) {
            parent[rootX] = rootY; // 简单合并，量大可以加按秩合并
            return true;
        }
        return false;
    }
};

int main() {
    int n, m;
    cin >> n >> m;
    vector<Edge> edges(m);
    for (int i = 0; i < m; i++) {
        cin >> edges[i].u >> edges[i].v >> edges[i].w;
    }

    // 1. 排序：$O(m \log m)$
    sort(edges.begin(), edges.end());

    DSU dsu(n);
    long long mst_weight = 0;
    int edge_count = 0;

    // 2. 贪心加边
    for (int i = 0; i < m; i++) {
        if (dsu.unite(edges[i].u, edges[i].v)) {
            mst_weight += edges[i].w;
            edge_count++;
        }
    }

    // 3. 连通性检查
    if (edge_count == n - 1) {
        cout << mst_weight << endl;
    }
    else {
        cout << -1 << endl;
    }

    return 0;
}