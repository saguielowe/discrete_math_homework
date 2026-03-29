// 实现一个拓扑排序 输出拓扑序顶点
#include <iostream>
#include <vector>
#include <queue>
using namespace std;
vector<int> graph[1009];
int in_degree[1009];
int ans[1009], k = 0;
queue<int> q;
int main() {
	int n, m;
	cin >> n >> m;
	for (int i = 0; i < m; ++i) {
		int u, v;
		cin >> u >> v;
		graph[u].push_back(v);
		in_degree[v]++;
	}
	for (int i = 1; i <= n; ++i) {
		if (in_degree[i] == 0) {
			q.push(i);
		}
	}
	while (!q.empty()) {
		int u = q.front();
		q.pop();
		ans[k++] = u; // ans数组存储拓扑序，因为可能有环，所以不能直接输出
		for (int v : graph[u]) {
			in_degree[v]--;
			if (in_degree[v] == 0) {
				q.push(v);
			}
		}
	}
	if (k < n) {
		cout << -1 << endl;
	} else {
		for (int i = 0; i < k; ++i) {
			cout << ans[i] << " ";
		}
		cout << endl;
	}
	return 0;
}