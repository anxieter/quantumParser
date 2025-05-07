from program import *
from typing import List
import networkx as nx
import matplotlib.pyplot as plt
from pyvis.network import Network
import webbrowser
from queue import Queue
from projector import *
from logger import *
# define enum for different types of statements
SUBSPACE = 1
SUBSPACE_WITH_SIG = 2
THRESHOLD = 2 # 2 times widening, because for repeat-until-success program, it converges in 2 times and there's no need for widening, and for general while loop ,we need to converge fast
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
        self.widening_count = []
        self.need_print = False
        
    def __str__(self) -> str:
        return f'{self.id}:{self.invariant}'
    
    def add_parent(self, parent_loc, matrix, label):
        self.parents.append(Line(parent_loc.id, matrix, label))

    def add_next(self, next_loc, matrix, label):
        self.nexts.append(Line(next_loc.id, matrix, label))
        
    def set_widen(self, n):
        self.need_widening = True
        self.widening_count = np.array([0] * n)

    def set_assigned_id(self, qid, value):
        self.qid = qid
        self.value = value
   
    def set_print(self, ids):
        self.need_print = True
        self.print_ids = ids
        
class ControlFlowGraph:
    def __init__(self, program: Program):
        self.program = program
        self.n = program.n
        self.locations: List[Location] = []
        init_location = Location(0)
        init_location.invariant = np.eye(2**self.n)
        self.locations.append(init_location)
        self.widening_locations = []
        self.init_location = init_location
        self.id = 1
        self.last_location = self.generate(program)

    def generate(
        self, program: Program
    ) -> Location:  # return the ending location
        # init
        last_location = self.locations[self.id - 1]
        n = self.n
        for statement in program.statements:
            # print(statement)
            if statement.type == SKIP:
                new_location = self.create_location()
                last_location.add_next(new_location, Skip(n).matrix(), "skip")
                new_location.add_parent(last_location, Skip(n).matrix(), "skip")
                last_location = new_location
            if statement.type == ASSIGNMENT:
                new_location = self.create_location()
                last_location.set_assigned_id(statement.p, statement.value)
                new_location.add_parent(last_location, None, str(statement))
                last_location.add_next(new_location, None, str(statement))
                last_location = new_location
            if statement.type == UNITARY_TRANSFORM:
                # create a new location
                new_location = self.create_location()
                new_location.add_parent(last_location, statement.matrix(), str(statement))
                last_location.add_next(new_location, statement.matrix(), str(statement))
                last_location = new_location
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
            if statement.type == WHILE:
                last_location.set_widen(self.n)
                self.widening_locations.append(last_location)
                loop_location = self.create_location()
                loop_location.add_parent(last_location, statement.continue_matrix(), "loop")
                loop_exit = self.generate(statement.S) 
                exit_location = self.create_location()
                exit_location.add_parent(last_location, statement.exit_matrix(), "exit")
                loop_exit.add_next(last_location, Skip(n).matrix(), "skip")
                last_location.add_parent(loop_exit, Skip(n).matrix(), "skip")
                last_location.add_next(loop_location, statement.continue_matrix(), "loop")
                last_location.add_next(exit_location, statement.exit_matrix(), "exit")
                last_location = exit_location
            if statement.need_print:
                last_location.set_print(statement.ids)
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
        node_labels = {node: str(node) for node in G.nodes()}
        nx.draw_networkx_labels(G, pos, labels=node_labels, font_color='black', font_size=14)
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels,font_color='red')
        net  = Network(notebook=True, directed=True)
        for node in G.nodes():
            net.add_node(node, label=str(node))
        for i,j,d in G.edges(data=True):
            net.add_edge(i, j, label=d['label'])
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
            
        self.counts = 0

    def abstract_interpret(self,widening_enabled=True):
        # step1 build the control flow graph
        cfg = ControlFlowGraph(self.program)
        self.cfg = cfg
        # step2 init state
        initial_state = self.state
        need_update = Queue()
        for next in cfg.init_location.nexts:
            need_update.put(next.id)
        while need_update.empty() == False:
            cur = cfg.locations[need_update.get()]
            self.counts += 1
            log("updating" + str(cur.id))
            # print("updating", cur.id)
            # print("current:", str(cur))
            if self.update_from_parents(cur, widening_enabled):
                if cur.need_print:
                    print("location", cur.id)
                    print(trace_out(cur.invariant, cur.print_ids, self.n))
                    log("location" + str(cur.id))
                    log(str(trace_out(cur.invariant, cur.print_ids, self.n)))
                for next in cur.nexts:
                    if next.id not in need_update.queue:   
                        need_update.put(next.id)
        print("done")           
        print(self.counts)
        # for loc in cfg.locations:
            # print('location', loc.id,'; invariant:', loc.invariant)
    
    
    def update_invariant_with_matrix(self, invariant, matrix: QOMatrix):
        if matrix.type == UNITARY:
            return matrix.mat @ invariant @ matrix.mat.T
        elif matrix.type == PROJECTOR:
            # print("sasaki_projection")
            # print("matrix", np.array(matrix.mat, dtype=np.float64))
            # print("invariant", np.array(invariant, dtype=np.float64))
            res =  sasaki_projection(matrix.mat, invariant)
            # print("res", np.array(res, dtype=np.float64))
            return res
        else:
            raise ValueError("unknown matrix type")

    def update_invariant_for_assignment(self, invariant, qid, value, need_print):
        # print(np.array(invariant, dtype=np.float64))
        # print("set qid", qid, "to value", value)
        ket_0 = np.array([1, 0], dtype=np.complex128)
        ket_1 = np.array([0, 1], dtype=np.complex128)
        if value == 0:
            U_0 = expand_operator(np.outer(ket_0, ket_0), [qid], self.n)
            U_1 = expand_operator(np.outer(ket_0, ket_1), [qid],  self.n)
        else:
            U_0 = expand_operator(np.outer(ket_1, ket_0), [qid], self.n)
            U_1 = expand_operator(np.outer(ket_1, ket_1), [qid], self.n)
        if need_print:
            print("U_0", np.array(U_0, dtype=np.float64))
            print("U_1", np.array(U_1, dtype=np.float64))
            print("invariant", np.array(invariant))
        res = U_0 @ invariant @ U_0.T + U_1 @ invariant @ U_1.T
        
        return supp(res)
    
    def update_from_parents(self, loc: Location, widening_enable: bool = True):
        Q = None
        old_inv = loc.invariant
        for parent in loc.parents:
            parent_node = self.cfg.locations[parent.id]
            matrix = parent.matrix
            if parent_node.invariant is not None:
                if matrix is not None:
                    update_par_inv = self.update_invariant_with_matrix(parent_node.invariant, matrix)
                else: # Assignment 
                    update_par_inv = self.update_invariant_for_assignment(parent_node.invariant, parent_node.qid, parent_node.value, loc.need_print)
                if Q is None:
                    Q = update_par_inv
                else:
                    # TODO: widening
                    if loc.need_widening and widening_enable:
                        if np.array_equal(Q @ update_par_inv, Q):
                            pass
                        else:
                            qubits = get_qubits(update_par_inv)
                            
                            loc.widening_count[qubits] += 1
                            print("widening ", loc.widening_count)
                            indices = []
                            for i in range(len(loc.widening_count)):
                                if loc.widening_count[i] < THRESHOLD:
                                    indices.append(i)
                            if len(indices) == self.n:
                                Q = join(Q, update_par_inv)
                            elif len(indices) == 0:
                                Q = np.eye(2**self.n)
                            else:
                                Q = trace_out(Q, indices, self.n)
                                Q = expand_operator(Q, indices, self.n)                        
                    else:                            
                        Q = join(Q, update_par_inv)
       
        loc.invariant = Q
        if old_inv is None and loc.invariant is None:
            return False
        if old_inv is None and loc.invariant is not None:
            return True
        if old_inv is not None and loc.invariant is None:
            raise ValueError("invariant should not be None")
        if old_inv is not None and loc.invariant is not None:
            return not np.array_equal(old_inv, loc.invariant)
                    
    def narrowing(self):
        cfg = self.cfg
        need_update = Queue()
        for next in cfg.widening_locations:
            need_update.put(next.id)
        while need_update.empty() == False:
            cur = cfg.locations[need_update.get()]
            print("updating", cur.id)
            # print("updating", cur.id)
            # print("current:", str(cur))
            if self.update_from_parents_with_narrowing(cur):
                if cur.need_print:
                    print("location", cur.id)
                    print(trace_out(cur.invariant, cur.print_ids, self.n))
                for next in cur.nexts:
                    if next.id not in need_update.queue:   
                        need_update.put(next.id)
        print("done") 
        
    def update_from_parents_with_narrowing(self, loc: Location):
        if loc.need_widening:
            # narrowing
            old_inv = loc.invariant
            wd_count = loc.widening_count
            indices = []
            for i,count in enumerate(wd_count):
                if count >= THRESHOLD:
                    indices.append(i)
            if len(indices) == 0: # already narrowed
                return False
            else:
                print("narrowing")
                loc.widening_count[indices] = np.array([0] * len(indices))
                np.set_printoptions(threshold=np.inf)
                Q = None
                for par in loc.parents:
                    par_loc = self.cfg.locations[par.id]
                    if par_loc.invariant is not None:
                        if Q is None:
                            Q = par_loc.invariant
                        else:
                            Q = join(Q, par_loc.invariant)
                
                Q = trace_out(Q, indices, self.n)
                new_inv = sasaki_projection(old_inv, expand_operator(Q,indices, self.n))
                loc.invariant = new_inv
                return not np.array_equal(old_inv, new_inv)                
        else:
            loc.invariant = None
            return self.update_from_parents(loc, False)