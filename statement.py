import numpy as np

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

class unitaryOperator(quantumOperator):
    def __init__(self, n, unitary_np):
        super().__init__(n)
        self.mat = unitary_np
    def __str__(self):
        return "U"
        
class measurementOperator(quantumOperator):
    def __init__(self, n, projector):
        super().__init__(n)
        self.mat = projector
    def __str__(self):
        return "M"

class assignment(statement): # p = q
    def __init__(self, n, p, q, indices):
        super().__init__("assignment")
        self.p = p
        self.q = q
        self.indices = indices
        self.qo = assignmentOperator(n, q, indices)
    def __str__(self):
        return f"{self.p} = {self.q}"
    
    def matrix(self):
        # sum of \ket{q}\bra{i} for all i in 2^indices
        return self.qo.matrix()

class unitaryTransform(statement): # p =Uq
    def __init__(self, n, p, q, U):
        super().__init__("unitaryTransform")
        self.p = p
        self.q = q
        self.U = unitaryOperator(n, U)
    def __str__(self):
        return f"{self.p} = {self.U}{self.q}"

    def matrix(self):
        return self.U.matrix() 

class ifStatement(statement): # if M[q] = 1 then S1 else S2
    def __init__(self, n, M,  q, S1, S2):
        super().__init__("ifStatement")
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
        super().__init__("whileStatement")
        self.mat = measurementOperator(n, M)
        self.q = q
        self.S = S
    def __str__(self):
        return f"while {self.mat}{self.q} do {self.S}"

    def matrix(self):
        return self.mat.matrix()