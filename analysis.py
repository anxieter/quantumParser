from newProgram import *
from typing import List

# define enum for different types of statements
SUBSPACE = 1
SUBSPACE_WITH_SIG = 2

class line:
    def __init__(self, id, statement):
        self.id = id
        self.statement = statement

class location:
    def __init__(self, id):
        self.id = id
        self.parents = []
        self.nexts = []

    def add_parent(self, parent_loc, statement):
        self.parents.append(line(parent_loc.id, statement))

    def add_next(self, next_loc, statement):
        self.nexts.append(line(next_loc.id, statement))

class controlFlowGraph:
    def __init__(self, program: newProgram):
        self.program = program
        self.n = program.
        self.locations: List[location] = []
        init_location = location(0)
        self.locations.append(init_location)
        self.init_location = init_location
        self.generate(program, 0)

    def generate(
        self, program: newProgram, start_id: int
    ) -> location:  # return the ending location
        # init
        id = start_id
        id += 1
        last_location = self.locations[start_id]
        for statement in program.statements:
            if statement.type == UNITARY_TRANSFORM:
                # create a new location
                new_location = location(id)
                new_location.add_parent(last_location, statement)
                last_location.add_next(new_location, statement)
                last_location = new_location
                id += 1
                continue
            if statement.type == IF:
                if_location = location(id)
                id += 1
                exit1 = self.generate(statement.S1, id)
                else_location = location(id)
                id += 1
                exit2 = self.generate(statement.S2, id)
                if_location.add_parent(last_location, statement)
                else_location.add_parent(last_location, statement)
                exit_location = location(id)
                exit_location.add_parent(exit1, skip(n))
                exit_location.add_parent(exit2, statement)
                last_location.add_next(if_location, statement)
                last_location.add_next(else_location, statement)
                last_location = exit_location
                id += 1
                continue
            if statement.type == WHILE:
                loop_location = location(id)
                
                
                

class analyser:
    def __init__(self, n, program: newProgram, type=SUBSPACE, sig=None):
        self.n = n
        self.program = program
        self.type = type
        self.sig = sig
        if type == SUBSPACE:
            self.state = np.eye(2**n)
        if type == SUBSPACE_WITH_SIG:
            self.state = [np.eye(2**i) for i in sig]

    def abstract_interpret(self):
        # step1 build the control flow graph
        locations = []
