from parser import lexer
from program import generateFromLex
path = 'test.txt'
qubit_count = 4 # TODO: get qubit count from the file



with open(path) as f:
    code = f.read()
    parsed_code = lexer.parse_code(code)

print(parsed_code)

program = generateFromLex(parsed_code)
    