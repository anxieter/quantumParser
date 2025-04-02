import numpy as np
import qutip

SKIP = 0
ASSIGNMENT = 1
UNITARY_TRANSFORM = 2
WHILE = 3
IF = 4
PRINT = 5

UNITARY = 123
PROJECTOR = 456

class QOMatrix:
    def __init__(self, mat, t):
        self.mat = mat
        self.type = t
        # self.shape = mat.shape
    def __str__(self):
        return f"{self.mat}"



class Var:
    def __init__(self, t):
        self.name = t
    def __str__(self):
        return f"{self.name}"
class Statement:
    def __init__(self, type):
        self.type = type
        self.n = 1
        self.need_print = False
        pass
    
    def set_print(self, ids):
        self.need_print = True
        self.ids = ids
        
    def __str__(self):
        return "error: not implemented"
    
    def matrix(self):
        return np.zeros(self.n, self.n)
    

class QuantumOperator:
    def __init__(self, n):
        self.n = n # number of qubits
        self.mat = np.zeros((2**n, 2**n))

    def matrix(self):
        return self.mat # 0 is for error

class AssignmentOperator(QuantumOperator):
    def __init__(self, n, qid, value): 
        if value != 0 and value != 1:
            raise ValueError("AssignmentOperator only accepts 0 or 1")
        super().__init__(n)
        self.qid = qid
        self.mat = np.zeros((2**n, 2**n))
        for i in range(2**n):
            # set qid-th qubit to value
            if value == 0:
                t = i - (i & (1 << (n - qid - 1)))
            else:
                t = i | (1 << (n - qid - 1))
            self.mat[t, i] = 1

def swap_qubits(i, j, n_qubits):
    U = np.eye(2**n_qubits)
    U[i, i] = 0
    U[j, j] = 0
    U[i, j] = 1
    U[j, i] = 1
    return U

class Counter:
    def __init__(self, bits, n_qubits):
        self.cnt = 0
        self.bits = sorted(bits, reverse=True)
        self.n_qubits = n_qubits

    def get_and_tick(self):
        res = 0
        for i in range(len(self.bits)):
            if (self.cnt >> i) & 1 == 1:
                res += 2**(self.n_qubits - self.bits[i] - 1)
        self.cnt += 1
        return res % (2**self.n_qubits)

    def get_index(self, i):
        res = 0
        k = len(self.bits)
        for j in range(k):
            if (i >> (self.n_qubits - self.bits[j] - 1)) & 1 == 1:
                res += 2**j
        return res % (2**self.n_qubits)
    
    def get_rest(self, i):
        k = len(self.bits)
        for j in range(k):
            i = i - (i & (1 << (self.n_qubits - self.bits[j] - 1)))
        return i % (2**self.n_qubits)
    
    def reset(self):
        self.cnt = 0
    
def expand_operator(U, target_qubits, n_qubits):
    k = len(target_qubits)
    target_counter = Counter(target_qubits, n_qubits)

    init_indices = []
    for i in range(2**k):
        init_indices.append(target_counter.get_and_tick())
    init_indices = np.array(init_indices, dtype=np.int64)
    res = np.zeros((2**n_qubits, 2**n_qubits), dtype=np.complex128)
    for i in range(2**n_qubits):
        cur = target_counter.get_rest(i)
        res[i ,init_indices + cur] = U[target_counter.get_index(i)]
        # print(np.array(res, dtype=np.float64))
    return res

def trace_out(U, qubits, n_qubits):
    qU = qutip.Qobj(U,dims=[[2]*n_qubits, [2]*n_qubits])
    qubits = sorted(qubits)
    return qutip.ptrace(qU, qubits).data_as('ndarray') 
    
class UnitaryOperator(QuantumOperator):                                                                                                                                        
    def __init__(self, n, unitary_np, tp): # extend to n qubit transformation
        super().__init__(n)
        self.mat = expand_operator(unitary_np, tp, n)
    def __str__(self):
        return "U"
        
class MeasurementOperator(QuantumOperator):
    def __init__(self, n, projector, qubit_indices):
        super().__init__(n)
        self.mat = expand_operator(projector, qubit_indices, n)
    def __str__(self):
        return "M"
    def othogonal_projector(self):
        return np.eye(2**self.n) - self.mat
class Skip(Statement):
    def __init__(self, n):
        super().__init__(SKIP)
        self.n = n 
    def __str__(self):
        return "skip"
    def matrix(self):
        return QOMatrix(np.eye(2**self.n), UNITARY)
    def print(self):
        print("skip")
    
    
class Assignment(Statement): # p = i
    def __init__(self, n, p, value):
        super().__init__(ASSIGNMENT)
        self.p = p
        self.value = value
        
        
    def __str__(self):
        return f"q{self.p} = {self.value}"
    
    def matrix(self):
        # sum of \ket{q}\bra{i} for all i in 2^indices
        raise("Error: Assignment can't be taken as a matrix")
        return QOMatrix(self.qo.matrix(), UNITARY)
        

class UnitaryTransform(Statement): # p =U[p]
    def __init__(self, n, vars,  U):
        super().__init__(UNITARY_TRANSFORM)
        self.vars = vars
        self.U = UnitaryOperator(n, U, vars)
    def __str__(self):
        return f"q{self.vars} = {self.U}q{self.vars}"

    def matrix(self):
        return QOMatrix(self.U.matrix(), UNITARY) 

class IfStatement(Statement): # if M[q] = value then S1 else S2
    def __init__(self, n, M,  q, value, S1, S2):
        super().__init__(IF)
        self.mat = MeasurementOperator(n, M, q)
        self.q = q
        self.S1 = S1
        self.S2 = S2
        if value == 0:
            self.if_mat = self.mat.othogonal_projector()
            self.else_mat = self.mat.matrix()
        else:
            self.if_mat= self.mat.matrix()
            self.else_mat= self.mat.othogonal_projector()
        
    def __str__(self):
        return f"if {self.mat}q{self.q} then {self.S1} else {self.S2}"

    def matrix(self):
        return self.mat.matrix()

    def if_matrix(self):
        return QOMatrix(self.if_mat, PROJECTOR)

    def else_matrix(self):
        return QOMatrix(self.else_mat, PROJECTOR)
    

class WhileStatement(Statement): # while M[q] = value do S
    def __init__(self, n, M, q, value, S):
        super().__init__(WHILE)
        self.mat = MeasurementOperator(n, M, q)
        self.q = q
        self.S = S
        if value == 0:
            self.continue_mat = self.mat.othogonal_projector()
            self.exit_mat = self.mat.matrix()
        else:
            self.continue_mat = self.mat.matrix()
            self.exit_mat = self.mat.othogonal_projector()
    def __str__(self):
        return f"while {self.mat}q{self.q} do {self.S}"

    def matrix(self):
        return self.mat.matrix()
    
    def continue_matrix(self):
        return QOMatrix(self.continue_mat, PROJECTOR)
    
    def exit_matrix(self):
        return QOMatrix(self.exit_mat, PROJECTOR)
    
    
    