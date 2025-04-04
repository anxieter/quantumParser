from myparser import lexer
from analysis import *
path = 'test.txt'
qubit_count = 4 # TODO: get qubit count from the file


with open(path) as f:
    code = f.read()
    parsed_code = lexer.parse_code(code)

print(parsed_code)

program = generateFromLex(parsed_code, qubit_count)

graph = ControlFlowGraph(program)

graph.show()

analyser = Analyser(qubit_count, program)
analyser.abstract_interpret()
inv = analyser.cfg.last_location.invariant
# print(inv.shape)
# print(np.array(inv, dtype=np.float64))
# print(trace_out(inv, [1,3], qubit_count))
# print(trace_out(inv, [1], qubit_count))
# print(trace_out(inv, [2], qubit_count))
# print(trace_out(inv, [3], qubit_count))