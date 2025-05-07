from myparser import lexer
from analysis import *
from config import *
from logger import *
with open(path) as f:
    code = f.read()
    parsed_code = lexer.parse_code(code)

clear_log()

program = generateFromLex(parsed_code, qubit_count)

graph = ControlFlowGraph(program)

graph.show()

analyser = Analyser(qubit_count, program)
analyser.abstract_interpret(True)
# analyser.narrowing()
inv = analyser.cfg.last_location.invariant
print(trace_out(inv, target_inv_qubits, qubit_count))