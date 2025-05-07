import numpy as np
from scipy.linalg import lu
from scipy.linalg import eigh
from scipy.linalg import null_space
def random_projector_rank_k(dim, k):
    A = np.random.randn(dim, k)  # 生成 dim × k 复随机矩阵
    Q, _ = np.linalg.qr(A)  # 施密特正交化
    P = Q @ Q.conj().T  # 计算投影矩阵
    return P

def remove_small_values(matrix):
    real = np.real(matrix)
    imag = np.imag(matrix)
    threshold = 1e-10
    real[np.abs(real) < threshold] = 0
    imag[np.abs(imag) < threshold] = 0
    return real + 1j * imag

def supp(R):
    # return the support space of R
    U, S, Vh = np.linalg.svd(R)
    # print(R)
    rank = np.linalg.matrix_rank(R)
    U_basis = U[:, :rank]
    projector = U_basis @ U_basis.conj().T
    return  remove_small_values(np.array(projector, dtype=np.complex128))
        
def get_qubits(R):
    n = np.log2(R.shape[0])
    #! cannot compute actually
    n = int(n)
    return range(n)
    # res = n * [0]
    # for i in range(R.shape[0]):
    #     for j in range(R.shape[1]):
    #         if R[i,j] != 0:
    #             for k in range(n):
    #                 if (i >> k) & 1 == 1:
    #                     res[k] = 1
    # res = [i for i in range(len(res)) if res[i] == 1]
    # return res


    


def supp_vecs(R):
    U, S, Vh = np.linalg.svd(R)
    rank = np.linalg.matrix_rank(R)
    U_basis = U[:, :rank]
    return U_basis.T

def join(P, Q):
    # print(P.shape, Q.shape)
    R = P + Q
    return supp(R)

def intersect(P, Q):
    n = P.shape[0]
    I = np.eye(n) 
    P_minus_I = P - I
    Q_minus_I = Q - I
   
    combined_space = np.vstack([P_minus_I, Q_minus_I])
    null_space_combined = null_space(combined_space)
    res = np.zeros_like(P,dtype=np.complex128)
    for vec in null_space_combined.T:
        v = np.array(vec, dtype=np.complex128)
        res += np.outer(v, v)
    return remove_small_values(res)


def sasaki_projection(P, Q):
    # print(P @ Q @ P)
    return supp(P @ Q @ P)
    # P_otho = np.eye(P.shape[0]) - P
    # M = join(P_otho,Q)
    # print(M)
    # M = intersect(P, M)
    # return M

def mat_equal(P, Q):
    tor = 1e-10
    if np.abs(P - Q).max() < tor:
        return True
    else:
        return False