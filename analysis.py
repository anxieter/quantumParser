from program import *
from typing import List
import networkx as nx
import matplotlib.pyplot as plt
from pyvis.network import Network
import webbrowser
from projector import *
# define enum for different types of statements
SUBSPACE = 1
SUBSPACE_WITH_SIG = 2

class Line:
    def __init__(self, id: int, matrix: QOMatrix, label: str):
        self.id = id
        self.matrix = matrix
        self.label = label

class Location:
    def __init__(self, id):
        self.id = id
        self.parents: List[Line] = []
        self.nexts: List[Line] = []
        self.invariant = None
        self.need_widening = False
        
    def add_parent(self, parent_loc, matrix, label):
        self.parents.append(Line(parent_loc.id, matrix, label))

    def add_next(self, next_loc, matrix, label):
        self.nexts.append(Line(next_loc.id, matrix, label))
        
    def set_widen(self):
        self.need_widening = True

   
        
class ControlFlowGraph:
    def __init__(self, program: Program):
        self.program = program
        self.n = program.n
        self.locations: List[Location] = []
        init_location = Location(0)
        init_location.invariant = np.eye(2**self.n)
        self.locations.append(init_location)
        self.init_location = init_location
        self.id = 1
        self.generate(program)

    def generate(
        self, program: Program
    ) -> Location:  # return the ending location
        # init
        last_location = self.locations[self.id - 1]
        n = self.n
        for statement in program.statements:
            print(statement)
            if statement.type == SKIP:
                new_location = self.create_location()
                last_location.add_next(new_location, Skip(n).matrix(), "skip")
                new_location.add_parent(last_location, Skip(n).matrix(), "skip")
                last_location = new_location
                continue
            if statement.type == ASSIGNMENT:
                new_location = self.create_location()
                new_location.add_parent(last_location, statement.matrix(), str(statement))
                last_location.add_next(new_location, statement.matrix(), str(statement))
                last_location = new_location
                continue
            if statement.type == UNITARY_TRANSFORM:
                # create a new location
                new_location = self.create_location()
                new_location.add_parent(last_location, statement.matrix(), str(statement))
                last_location.add_next(new_location, statement.matrix(), str(statement))
                last_location = new_location
                continue
            if statement.type == IF:
                if_location = self.create_location()
                exit1 = self.generate(statement.S1)
                else_location = self.create_location()
                exit2 = self.generate(statement.S2)
                if_location.add_parent(last_location, statement.if_matrix(), "if")
                else_location.add_parent(last_location, statement.else_matrix(), "else")
                exit_location = self.create_location()
                exit1.add_next(exit_location, Skip(n).matrix(), "skip")
                exit2.add_next(exit_location, Skip(n).matrix(), "skip")
                exit_location.add_parent(exit1, Skip(n).matrix(), "skip")
                exit_location.add_parent(exit2, Skip(n).matrix(), "skip")
                last_location.add_next(if_location, statement.if_matrix(), "if")
                last_location.add_next(else_location, statement.else_matrix(), "else")
                last_location = exit_location
                continue
            if statement.type == WHILE:
                last_location.set_widen()
                loop_location = self.create_location()
                loop_location.add_parent(last_location, statement.continue_matrix(), "loop")
                loop_exit = self.generate(statement.S) 
                exit_location = self.create_location()
                exit_location.add_parent(last_location, statement.exit_matrix(), "exit")
                loop_exit.add_next(last_location, Skip(n).matrix(), "skip")
                last_location.add_next(loop_location, statement.continue_matrix(), "loop")
                last_location.add_next(exit_location, statement.exit_matrix(), "exit")
                last_location = exit_location
        return last_location
    def create_location(self):
        new_location = Location(self.id)
        self.locations.append(new_location)
        self.id += 1
        return new_location    
                                
                                
    def show(self):
        G = nx.DiGraph()
        queue = []
        queue.append(self.init_location)
        while queue:
            cur = queue.pop()
            for next in cur.nexts:
                G.add_edge(cur.id, next.id, label=next.label)
                if  next.id > cur.id:
                    queue.append(self.locations[next.id])
        pos = nx.spring_layout(G)
        edge_labels = {(i, j): d['label'] for i, j,d in G.edges(data=True)}
        nx.draw(G, pos, with_labels=True, node_color='lightblue', edge_color='gray', node_size=2000, font_size=12)
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels,font_color='red')
        net  = Network(notebook=True, directed=True)
        net.from_nx(G)
        net.show("graph.html")
        webbrowser.open("graph.html")
class Analyser:
    def __init__(self, n, program: Program, type=SUBSPACE, sig=None):
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
        cfg = ControlFlowGraph(self.program)
        self.cfg = cfg
        # step2 init state
        initial_state = self.state
        need_update = []
        for next in cfg.init_location.nexts:
            need_update.append(cfg.locations[next.id])
        while need_update:
            cur = need_update.pop()
            if self.update_from_parents(cur):
                for next in cur.nexts:
                    need_update.append(cfg.locations[next.id])
        print("done")
        for loc in cfg.locations:
            print('location', loc.id,'; invariant:', loc.invariant)
    
    
    def update_invariant_with_matrix(self, invariant, matrix: QOMatrix):
        if matrix.type == UNITARY:
            return matrix.mat @ invariant @ matrix.mat.T
        elif matrix.type == PROJECTOR:
            return sasaki_projection(matrix.mat, invariant)
        else:
            raise ValueError("unknown matrix type")

    def update_from_parents(self, loc: Location):
        Q = None
        old_inv = loc.invariant
        for parent in loc.parents:
            parent_node = self.cfg.locations[parent.id]
            matrix = parent.matrix
            if parent_node.invariant is not None:
                update_par_inv = self.update_invariant_with_matrix(parent_node.invariant, matrix)
                if Q is not None:
                    Q = update_par_inv
                else:
                    old_Q = Q
                    # TODO: widening
                    Q = join(Q, update_par_inv)
        if loc.invariant is not None:
            loc.invariant = join(loc.invariant, Q)
        else:
            loc.invariant = Q
        if old_inv is None and loc.invariant is None:
            return False
        if old_inv is None and loc.invariant is not None:
            return True
        if old_inv is not None and loc.invariant is None:
            raise ValueError("invariant should not be None")
        if old_inv is not None and loc.invariant is not None:
            return not np.array_equal(old_inv, loc.invariant)
                    