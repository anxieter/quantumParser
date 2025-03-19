import numpy as np
from scipy.linalg import lu
from scipy.linalg import eigh

def random_projector_rank_k(dim, k):
    A = np.random.randn(dim, k)  # 生成 dim × k 复随机矩阵
    Q, _ = np.linalg.qr(A)  # 施密特正交化
    P = Q @ Q.conj().T  # 计算投影矩阵
    return P


def join(P, Q):
    print(P.shape, Q.shape)
    M = np.vstack((P, Q))
    _, _, V = lu(M)
    # 把 V 中太小的元素置为 0
    V[np.abs(V) < 1e-10] = 0
    # print(V)
    V, U = np.linalg.qr(V)
    # print(V, U)
    return U

def intersect(P, Q):
    PQ = P @ Q  # 计算 PQ
    PQ_sym = (PQ + PQ.conj().T) / 2  # 确保对称性

    # 计算特征值和特征向量
    eigvals, eigvecs = eigh(PQ_sym)

    # 选取特征值接近 1 的特征向量（这些对应于公共子空间）
    tol = 1e-10
    mask = eigvals > 1 - tol  # 近似 1 的特征值
    common_subspace = eigvecs[:, mask]  # 提取对应的特征向量

    # 计算最终的投影矩阵
    P_intersect = common_subspace @ common_subspace.conj().T
    return P_intersect


def sasaki_projection(P, Q):
    P_otho = np.eye(P.shape[0]) - P
    M = join(P_otho,Q)
    M = intersect(P, M)
    print(M)
    return M