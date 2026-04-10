# 这是对第三题的第三小问，比较删除法和容斥法的结果，都是9。
# import numpy as np

# # 关联矩阵
# M = np.array([
#     [1, 1, 1, 0, 0, 0, 0, 0, 0, 0],
#     [-1, 0, 0, -1, 1, 0, 1, 0, 0, 0],
#     [0, 0, 0, 0, 0, 0, -1, -1, 1, -1],
#     [0, -1, 0, 0, 0, -1, 0, 0, -1, 1],
#     [0, 0, -1, 1, -1, 1, 0, 1, 0, 0]
# ])

# def get_det(mat):
#     L = np.zeros((5, 5))
#     for c in range(mat.shape[1]):
#         out_node = np.where(mat[:, c] == 1)[0]
#         in_node = np.where(mat[:, c] == -1)[0]
#         if len(out_node) > 0 and len(in_node) > 0:
#             L[in_node[0], in_node[0]] += 1
#             L[in_node[0], out_node[0]] -= 1
#     return int(round(np.linalg.det(L[1:, 1:])))

# # 方法 A: 容斥法
# M_no_v2v3 = M.copy()
# for c in range(M.shape[1]):
#     if M[1, c] == 1 and M[2, c] == -1: M_no_v2v3[:, c] = 0
# result_A = get_det(M) - get_det(M_no_v2v3)

# # 方法 B: 删除法 (强制保留 v2->v3，删除其他指向 v3 的边)
# M_del = M.copy()
# # 1. 找到指向 v3 的所有边
# for c in range(M.shape[1]):
#     # 如果该列指向 v3 但不是指定的边，删除它
#     if M[2, c] == -1 and not (M[1, c] == 1):
#         print(f"删除边: {c} (指向 v3 的边)")
#         M_del[:, c] = 0
# result_B = get_det(M_del)

# print(f"容斥法结果: {result_A}")
# print(f"删除法结果: {result_B}")

# 这是对第二题，用合并节点法的算法实现，结果是44.（按照原图准备的关联矩阵，强制包含0,1,9三条边，合并节点后求支撑树数目）
# import numpy as np
# from sympy import Matrix

# def count_spanning_trees_with_must_include(B, must_include):
#     """
#     B: 关联矩阵 (n x m)，每列一条边，+1/-1表示端点
#     must_include: 必须包含的边的列索引列表
#     """
#     n, m = B.shape
#     # 用并查集追踪节点合并
#     parent = list(range(n))

#     def find(x):
#         while parent[x] != x:
#             parent[x] = parent[parent[x]]
#             x = parent[x]
#         return x

#     def union(x, y):
#         px, py = find(x), find(y)
#         if px == py:
#             return False  # 成环
#         parent[px] = py
#         return True

#     # 检查必含边是否成环，同时记录需要收缩的节点对
#     for c in must_include:
#         nodes = np.where(B[:, c] != 0)[0]
#         if len(nodes) != 2:
#             return 0
#         u, v = nodes[0], nodes[1]
#         if not union(u, v):
#             return 0  # 必含边自己就成环了

#     # 构造收缩后的节点映射
#     roots = sorted(set(find(i) for i in range(n)))
#     node_map = {r: i for i, r in enumerate(roots)}
#     n_new = len(roots)

#     if n_new == 1:
#         return 1  # 所有节点已连通，必含边本身就是支撑树

#     # 构造收缩后图的拉普拉斯（跳过必含边和自环）
#     L = np.zeros((n_new, n_new), dtype=int)
#     for c in range(m):
#         if c in must_include:
#             continue
#         nodes = np.where(B[:, c] != 0)[0]
#         if len(nodes) != 2:
#             continue
#         u, v = node_map[find(nodes[0])], node_map[find(nodes[1])]
#         if u == v:
#             continue  # 收缩后变自环，跳过
#         L[u][u] += 1
#         L[v][v] += 1
#         L[u][v] -= 1
#         L[v][u] -= 1

#     # Kirchhoff：删去任意一行一列取行列式
#     sub_L = Matrix(L[1:, 1:].tolist())
#     return sub_L.det()


# M = np.array([[ 0, -1,  0,  0,  1,  0,  1,  1,  0,  0, -1,  1,  0],
#               [ 1,  1, -1,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0],
#               [ 0,  0,  0, -1, -1,  1,  0,  0,  0,  0,  0,  0,  0],
#               [ 0,  0,  0,  0,  0,  0,  0, -1, -1,  1,  0,  0,  0],
#               [ 0,  0,  1,  0,  0, -1, -1,  0,  1,  0,  0,  0,  1],
#               [ 0,  0,  0,  0,  0,  0,  0,  0,  0, -1,  0, -1, -1],
#               [-1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  1,  0,  0]])

# print(count_spanning_trees_with_must_include(M, [0, 1, 9]))

# 这是对第二题，用容斥法的算法实现，结果也是44.（按照原图准备的关联矩阵，强制包含0,1,9三条边，合并节点后求支撑树数目）
import numpy as np
from sympy import Matrix
from itertools import combinations

def kirchhoff(B, active_edges):
    """给定活跃边集合，算无向支撑树数"""
    n = B.shape[0]
    L = np.zeros((n, n), dtype=int)
    for c in active_edges:
        nodes = np.where(B[:, c] != 0)[0]
        if len(nodes) != 2:
            continue
        u, v = nodes[0], nodes[1]
        L[u][u] += 1
        L[v][v] += 1
        L[u][v] -= 1
        L[v][u] -= 1
    return int(Matrix(L[1:, 1:].tolist()).det())

def count_must_include_inclusion_exclusion(B, must_include):
    """
    容斥：必须包含must_include中所有边
    对must_include的子集容斥，删掉子集中的边
    """
    all_edges = list(range(B.shape[1]))
    ans = 0
    for r in range(len(must_include) + 1):
        for subset in combinations(must_include, r):
            # 删掉subset中的边
            active = [e for e in all_edges if e not in subset]
            sign = (-1) ** r
            ans += sign * kirchhoff(B, active)
    return ans

M = np.array([[ 0, -1,  0,  0,  1,  0,  1,  1,  0,  0, -1,  1,  0],
              [ 1,  1, -1,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0],
              [ 0,  0,  0, -1, -1,  1,  0,  0,  0,  0,  0,  0,  0],
              [ 0,  0,  0,  0,  0,  0,  0, -1, -1,  1,  0,  0,  0],
              [ 0,  0,  1,  0,  0, -1, -1,  0,  1,  0,  0,  0,  1],
              [ 0,  0,  0,  0,  0,  0,  0,  0,  0, -1,  0, -1, -1],
              [-1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  1,  0,  0]])

print(count_must_include_inclusion_exclusion(M, [0, 1, 9]))