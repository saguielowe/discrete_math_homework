#include<iostream>
#include<vector>
using namespace std;
// 求出可对一条边的权值修改为0，使得从起点到终点的最短路径长度最小的值
// 采取对每个节点赋予0、1维度，0维度表示不修改边权，1维度表示修改边权
// 每条有向边对应0维度-1维度的权值为0的单向边，和不改变维度的保留原权值的单向边
// 保证仅能跨越一次维度。
// 最后求出新的最短路长度。
const int N = 2009;
vector<pair<int, int>> graph[N];
int dist[N];
int main(){
	int n,m;
	cin >> n >> m;
	for(int i = 0; i < m; i++){
		int u,v,w;
		cin >> u >> v >> w;
		graph[u].push_back({v,w});
		graph[v].push_back({ u,w });
		graph[u+n].push_back({v+n,w});
		graph[v + n].push_back({ u + n,w });
		graph[u].push_back({v+n,0});
		graph[v].push_back({ u + n,0 });
	}
	// Dijkstra
	for (int i = 1; i <= 2 * n; i++) dist[i] = 1e9;
	dist[1] = 0;
	vector<bool> visited(2 * n + 1, false);
	for (int i = 1; i <= 2 * n; i++) {
		int u = -1, minDist = 1e9;
		for (int j = 1; j <= 2 * n; j++) {
			if (!visited[j] && dist[j] < minDist) {
				u = j;
				minDist = dist[j];
			}
		}
		if (u == -1) break;
		visited[u] = true;
		for (auto& edge : graph[u]) {
			int v = edge.first, w = edge.second;
			if (dist[u] + w < dist[v]) {
				dist[v] = dist[u] + w;
			}
		}
	}
	//for (int i = 1; i <= 2 * n; i++) {
	//	cout << dist[i] << " ";
	//}
	int ans = min(dist[n], dist[2 * n]);
	if (ans == 1e9) ans = -1;
	cout << ans << endl;
	return 0;
}