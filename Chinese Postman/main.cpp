#include <iostream>
#include <vector>
#include <map>
#include <stack>
#include <algorithm>

using namespace std;

/**
 * 欧拉回路求解器 (Hierholzer Algorithm)
 * 适用于无向图
 */
class EulerCircuit {
public:
    // 使用 map 存储邻接表，方便处理字符或不连续的顶点编号
    map<int, vector<int>> adj;

    void addEdge(int u, int v) {
        adj[u].push_back(v);
        adj[v].push_back(u);
    }

    void findCircuit(int startNode) {
        stack<int> currPath;
        vector<int> circuit;
        currPath.push(startNode);

        while (!currPath.empty()) {
            int u = currPath.top();
            if (!adj[u].empty()) {
                // 还有没走过的边
                int v = adj[u].back();
                adj[u].pop_back();

                // 因为是无向图，要把反向边也删了
                auto it = find(adj[v].begin(), adj[v].end(), u);
                if (it != adj[v].end()) {
                    adj[v].erase(it);
                }

                currPath.push(v);
            }
            else {
                // 没路了，加入最终路径并回溯
                circuit.push_back(u);
                currPath.pop();
            }
        }

        // 输出路径
        cout << "欧拉回路路径为: ";
        for (int i = circuit.size() - 1; i >= 0; --i) {
            cout << "v" << circuit[i] << (i == 0 ? "" : " -> ");
        }
        cout << endl;
    }
};

int main() {
    EulerCircuit ec;

    // --- 在这里输入图(b)的所有边 ---
    // 1. 原有的外圈边
    ec.addEdge(1, 2); ec.addEdge(2, 3); ec.addEdge(3, 4);
    ec.addEdge(4, 5); ec.addEdge(5, 6); ec.addEdge(6, 1);

    // 2. 原有的内插线 (根据刚才修正的邻接关系)
    ec.addEdge(1, 4);
    ec.addEdge(2, 5);
    ec.addEdge(4, 6);
    ec.addEdge(3, 5); // v3-v5 权值为1的那条

    // 3. 我们确定的“重复边” (补边)
    // 为了消灭奇点 v1, v2, v4, v6
    // 方案：重复 (v1,v4) 和 路径 v2-v5-v6
    ec.addEdge(1, 4); // 重复 v1-v4
    ec.addEdge(2, 5); // 重复 v2-v5
    ec.addEdge(4, 6); // 重复 v5-v6
	ec.addEdge(3, 5); // 重复 v3-v5

    // 从 v1 开始跑
    ec.findCircuit(1);

    return 0;
}