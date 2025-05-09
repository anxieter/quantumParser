from myparser import lexer
from analysis import *
from config import *
from logger import *
import time
with open(path) as f:
    code = f.read()
    parsed_code = lexer.parse_code(code)

clear_log()

program = generateFromLex(parsed_code, qubit_count)

graph = ControlFlowGraph(program)

graph.show()

analyser = Analyser(qubit_count, program)
cur1 = time.time()
analyser.abstract_interpret()
cur2 = time.time()
analyser.narrowing()
cur3 = time.time()
print("Time taken for abstract interpretation: ", cur2 - cur1)
print("Time taken for abstract interpretation and narrowing: ", cur3 - cur1)
inv = analyser.cfg.last_location.invariant
print(trace_out(inv, target_inv_qubits, qubit_count))