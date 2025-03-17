from parser import lexer

with open('test.txt') as f:
    code = f.read()
    print(lexer.parse_code(code))

