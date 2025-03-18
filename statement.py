import numpy as np
import qutip

SKIP = 0
ASSIGNMENT = 1
UNITARY_TRANSFORM = 2
WHILE = 3
IF = 4

class Var:
    def __init__(self, t):
        self.name = t
    def __str__(self):
        return f"{self.name}"
class Statement:
    def __init__(self, type, n):
        self.type = type
        self.n = n
        pass

    def __str__(self):
        return "skip"
    
    def matrix(self):
        return np.zeros(self.n, self.n)
    

class QuantumOperator:
    def __init__(self, n, mat):
        self.n = n # number of qubits
        self.mat = mat

    def matrix(self):
        return self.mat

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
        return res

    def reset(self):
        self.cnt = 0
    
def expand_operator(U, target_qubits, n_qubits):
    # step1 swap target_qubits to the first k qubits
    k = len(target_qubits)
    rest = list(range(n_qubits))
    for i in range(k):
        rest.remove(target_qubits[i])
    target_counter = Counter(target_qubits, n_qubits)
    rest_counter = Counter(rest, n_qubits)
    swap_matrix = np.zeros((2**n_qubits, 2**n_qubits))
    for i in range(2**(n_qubits - k)):
        cur = rest_counter.get_and_tick()
        target_counter.reset()
        for j in range(2**k):    
            swap_matrix[target_counter.get_and_tick() + cur, i*2**k + j] = 1

    U = np.kron(np.eye(2**(n_qubits - k)), U)
    # step3 swap back
    
    U =swap_matrix.T @ U @ swap_matrix.T
    return U

def trace_out(U, qubits, n_qubits):
    qU = qutip.Qobj(U,dims=[2**n_qubits, 2**n_qubits])
    qubits = sorted(qubits)
    return np.array(qutip.ptrace(qU, qubits)).reshape(2**qubits, 2**qubits) 
    
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


class Skip(Statement):
    def __init__(self, n):
        super().__init__(SKIP)
        self.n = n 
    def __str__(self):
        return "skip"
    def matrix(self):
        return np.eye(2**self.n)

class Assignment(Statement): # p = i
    def __init__(self, n, p, value):
        super().__init__(ASSIGNMENT)
        self.p = p
        self.value = value
        self.qo = AssignmentOperator(n, p, value)
    def __str__(self):
        return f"{self.p} = 0"
    
    def matrix(self):
        # sum of \ket{q}\bra{i} for all i in 2^indices
        return self.qo.matrix()

class UnitaryTransform(Statement): # p =U[p]
    def __init__(self, n, vars,  U):
        super().__init__(UNITARY_TRANSFORM)
        self.vars = vars
        self.U = UnitaryOperator(n, U, vars)
    def __str__(self):
        return f"{self.vars} = {self.U}{self.vars}"

    def matrix(self):
        return self.U.matrix() 

class IfStatement(Statement): # if M[q] = 1 then S1 else S2
    def __init__(self, n, M,  q, S1, S2):
        super().__init__(IF)
        self.mat = MeasurementOperator(n, M, q)
        self.q = q
        self.S1 = S1
        self.S2 = S2
    def __str__(self):
        return f"if {self.mat}{self.q} then {self.S1} else {self.S2}"

    def matrix(self):
        return self.mat.matrix()

class WhileStatement(Statement): # while M[q] = 1 do S
    def __init__(self, n, M, q, S):
        super().__init__(WHILE)
        self.mat = MeasurementOperator(n, M, q)
        self.q = q
        self.S = S
    def __str__(self):
        return f"while {self.mat}{self.q} do {self.S}"

    def matrix(self):
        return self.mat.matrix()
    