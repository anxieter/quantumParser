from myparser import lexer
from analysis import *
from program import generateFromLex
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