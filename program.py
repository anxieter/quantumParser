import numpy as np
from statement import *
from typing import List

class Program:
    def __init__(self):
        self.n = 0
        self.statements: List[Statement]= []
        self.variables = {}
        self.matrices = {}
        self.cnt = 0
        
    def addStatement(self, statement):
        print("adding statement", statement)
        if statement[0] == 'assign':
            var_name = statement[1]
            value = float(statement[2])
            if var_name not in self.variables:
                self.variables[var_name] = (self.cnt)
                self.cnt += 1
            new_statement = Assignment(self.n, self.variables[var_name], value)
            self.statements.append(new_statement)
        elif statement[0] == 'mat_assign':
            mat_name = statement[1]
            mat = np.array(statement[2])
            self.matrices[mat_name] = mat
        elif statement[0] == 'unitary':
            qubit_indices = [self.variables[var] for var in statement[1]]
            mat_name = statement[2]
            mat = self.matrices[mat_name]
            self.statements.append(UnitaryTransform(self.n, qubit_indices, mat))
        elif statement[0] == 'if':
            measurement = self.matrices[statement[1]]
            qubit_index = [self.variables[var] for var in statement[2]]
            value = float(statement[3])
            if value != 0 and value != 1:
                raise ValueError("If measurement only accepts 0 or 1")
            S1 = generateFromLex(statement[4], self.n, self)
            S2 = generateFromLex(statement[5], self.n, self)
            self.statements.append(IfStatement(self.n, measurement, qubit_index, value, S1, S2))
        elif statement[0] == 'skip':
            self.statements.append(Skip(self.n))
        elif statement[0] == 'while':
            measurement = self.matrices[statement[1]]
            qubit_index = [self.variables[var] for var in statement[2]]
            value = float(statement[3])
            if value != 0 and value != 1:
                raise ValueError("While measurement only accepts 0 or 1")
            S1 = generateFromLex(statement[4], self.n, self)
            self.statements.append(WhileStatement(self.n, measurement, qubit_index, value, S1))
        elif statement[0] == 'print':
            ids = [self.variables[var] for var in statement[1]]
            self.statements[len(self.statements)-1].set_print(ids)
            
    def setN(self, n):
        self.n = n
    def __str__(self):
        return "\n".join([str(s) for s in self.statements])


def generateFromLex(program_lexed, n, parent_program=None):
    program = Program()
    program.setN(n)
    if parent_program:
        for var in parent_program.variables:
            program.variables[var] = parent_program.variables[var]
        for mat in parent_program.matrices:
            program.matrices[mat] = parent_program.matrices[mat]
    for statement in program_lexed:
        program.addStatement(statement)
    return program