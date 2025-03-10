import numpy as np
import qutip

SKIP = 0
ASSIGNMENT = 1
UNITARY_TRANSFORM = 2
WHILE = 3
IF = 4

class var:
    def __init__(self, t):
        self.name = t[0]
        self.qubits = t[1]
    def __str__(self):
        return f"{self.name}({str(self.qubits)})"
class statement:
    def __init__(self, type):
        self.type = type
        pass

    def __str__(self):
        return "skip"
    

class quantumOperator:
    def __init__(self, n):
        self.n = n # number of qubits
        self.mat = np.eye(2**n)

    def matrix(self):
        return self.mat

class assignmentOperator(quantumOperator):
    def __init__(self, n, q, indices): # q is 0 for indices (can imporve by composing indices into a single number)
        super().__init__(n)
        self.q = q
        self.mat = np.zeros((2**n, 2**n))
        for i in range(2**n):
            t = i
            for j in indices:
                t = t - i & (1 << j) # set j-th bit to 0
            self.mat[t][i] = 1

def swap_qubits(i, j, n_qubits):
    U = np.eye(2**n_qubits)
    U[i, i] = 0
    U[j, j] = 0
    U[i, j] = 1
    U[j, i] = 1
    return U

class counter:
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
    target_counter = counter(target_qubits, n_qubits)
    rest_counter = counter(rest, n_qubits)
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
    
class unitaryOperator(quantumOperator):                                                                                                                                        
    def __init__(self, n, unitary_np, tp): # extend to n qubit transformation
        super().__init__(n)
        self.mat = expand_operator(unitary_np, tp, n)
    def __str__(self):
        return "U"
        
class measurementOperator(quantumOperator):
    def __init__(self, n, projector):
        super().__init__(n)
        self.mat = projector
    def __str__(self):
        return "M"


class skip(statement):
    def __init__(self, n):
        super().__init__(SKIP)
        self.n = n 
    def __str__(self):
        return "skip"
    def matrix(self):
        return np.eye(2**self.n)

class assignment(statement): # p = 0
    def __init__(self, n, p, indices):
        super().__init__(ASSIGNMENT)
        self.p = p
        self.indices = indices
        self.qo = assignmentOperator(n, p, indices)
    def __str__(self):
        return f"{self.p} = 0"
    
    def matrix(self):
        # sum of \ket{q}\bra{i} for all i in 2^indices
        return self.qo.matrix()

class unitaryTransform(statement): # p =U[p]
    def __init__(self, n, p:var,  U):
        super().__init__(UNITARY_TRANSFORM)
        self.p = p
        self.U = unitaryOperator(n, U, p.qubits)
    def __str__(self):
        return f"{self.p} = {self.U}{self.p}"

    def matrix(self):
        return self.U.matrix() 

class ifStatement(statement): # if M[q] = 1 then S1 else S2
    def __init__(self, n, M,  q, S1, S2):
        super().__init__(IF)
        self.mat = measurementOperator(n, M)
        self.q = q
        self.S1 = S1
        self.S2 = S2
    def __str__(self):
        return f"if {self.mat}{self.q} then {self.S1} else {self.S2}"

    def matrix(self):
        return self.mat.matrix()

class whileStatement(statement): # while M[q] = 1 do S
    def __init__(self, n, M, q, S):
        super().__init__(WHILE)
        self.mat = measurementOperator(n, M)
        self.q = q
        self.S = S
    def __str__(self):
        return f"while {self.mat}{self.q} do {self.S}"

    def matrix(self):
        return self.mat.matrix()
    
class variable:
    def __init__(self, name):
        self.name = name
    def __str__(self):
        return self.name