#include <iostream>
#include <vector>
#include <queue>
#include <algorithm>

using namespace std;

const long long INF = 1e15; // 设置一个足够大的无穷大，防止加法溢出

struct Edge {
    int to;
    int weight;
};

struct Node {
    int u;
    long long dist;
    // 优先队列默认是大顶堆，我们重载大于号变成小顶堆
    bool operator>(const Node& other) const {
        return dist > other.dist;
    }
};

// 单源最短路 Dijkstra
vector<long long> dijkstra(int start, int n, const vector<vector<Edge>>& adj) {
    vector<long long> dist(n + 1, INF);
    priority_queue<Node, vector<Node>, greater<Node>> pq;

    dist[start] = 0;
    pq.push({ start, 0 });

    while (!pq.empty()) {
        Node current = pq.top();
        pq.pop();

        int u = current.u;
        long long d = current.dist;

        if (d > dist[u]) continue; // 经典的懒惰删除优化

        for (const auto& edge : adj[u]) {
            if (dist[u] + edge.weight < dist[edge.to]) {
                dist[edge.to] = dist[u] + edge.weight;
                pq.push({ edge.to, dist[edge.to] });
            }
        }
    }
    return dist;
}

int main() {
    int n, m;
    if (!(cin >> n >> m)) return 0;

    vector<vector<Edge>> adj(n + 1);
    for (int i = 0; i < m; i++) {
        int u, v, w;
        cin >> u >> v >> w;
        // 处理自环：虽然 Dijkstra 能跑，但自环对最短路没贡献
        if (u == v) continue;
        // 无向图加两条边
        adj[u].push_back({ v, w });
        adj[v].push_back({ u, w });
    }

    long long max_diameter = 0;
    bool is_disconnected = false;

    for (int i = 1; i <= n; i++) {
        vector<long long> d = dijkstra(i, n, adj);

        for (int j = 1; j <= n; j++) {
            // 如果发现有节点不可达，说明图不连通
            if (d[j] == INF) {
                is_disconnected = true;
                break;
            }
            if (d[j] > max_diameter) {
                max_diameter = d[j];
            }
        }
        if (is_disconnected) break;
    }

    if (is_disconnected) {
        cout << -1 << endl;
    }
    else {
        cout << max_diameter << endl;
    }

    return 0;
}