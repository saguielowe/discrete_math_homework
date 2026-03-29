#include <iostream>
#include <vector>
#include <queue>
using namespace std;
int route[100], ans[100]; // 记录每个节点的前驱节点
int main() {
	int n, m;
	cin >> n >> m;
	vector<vector<int>> graph(n);
	for (int i = 0; i < m; i++) {
		int u, v;
		cin >> u >> v;
		graph[u].push_back(v);
	}
	vector<bool> visited(n, false);
	queue<int> q;
	q.push(0);
	visited[0] = true;
	while (!q.empty()) {
		int node = q.front();
		q.pop();
		//cout << node << " ";
		for (int neighbor : graph[node]) {
			if (!visited[neighbor]) {
				visited[neighbor] = true;
				route[neighbor] = node; // 记录前驱节点
				q.push(neighbor);
			}
		}
	}
	if (!visited[n - 1]) {
		cout << 0 << endl;
		return 0;
	}
	int i = n - 1, j = -1;
	while (i) { // 正序输出从0到n-1的路径
		ans[++j] = i;
		i = route[i];
	}
	ans[++j] = 0; // 最后一个节点是0
	for (int k = j; k >= 1; k--) {
		cout << ans[k] << "->";
	}
	cout << ans[0] << endl; // 输出最后一个节点
	return 0;
}