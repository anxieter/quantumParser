import ply.lex as lex
import ply.yacc as yacc

# 词法分析器（Lexer）
tokens = (
    'SKIP', 'ASSIGN', 'UNITARY', 'IF', 'THEN', 'ELSE', 'FI', 'WHILE', 'DO', 'OD',
    'QVAR', 'MEASURE', 'EQUAL', 'LBRACKET', 'RBRACKET', 'NUMBER', 'COMMA', 
)

t_LBRACKET = r'\['
t_RBRACKET = r'\]'
t_COMMA = r','
t_EQUAL = r'='
t_ignore = ' \t\n'

def t_SKIP(t):
    r'skip'
    return t

def t_ASSIGN(t):
    r':='
    return t

def t_UNITARY(t):
    r'U[0-9]+'
    return t

def t_IF(t):
    r'if'
    return t

def t_THEN(t):
    r'then'
    return t

def t_ELSE(t):
    r'else'
    return t

def t_FI(t):
    r'fi'
    return t

def t_WHILE(t):
    r'while'
    return t

def t_DO(t):
    r'do'
    return t

def t_OD(t):
    r'od'
    return t

def t_QVAR(t):
    r'q[0-9]+'
    return t

def t_MEASURE(t):
    r'M[0-9]+'
    return t

def t_NUMBER(t):
    r'\d+'
    t.value = int(t.value)
    return t

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

def t_error(t):
    print(f"Illegal character '{t.value[0]}'")
    t.lexer.skip(1)

lexer = lex.lex()

# 语法分析器（Yacc）
def p_statement_skip(p):
    'statement : SKIP'
    p[0] = ('skip',)

def p_statement_assign(p):
    'statement : QVAR ASSIGN NUMBER'
    p[0] = ('assign', p[1])

def p_statement_U_assign(p):
    'statement : matrix'
    p[0] = ('U_assign', p[1])



def p_matrix(p):
    'matrix : LBRACKET rowlist RBRACKET'
    p[0] = p[2]

def p_rowlist(p):
    '''rowlist : row
               | rowlist COMMA row'''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[3]]
def p_row(p):
    'row : LBRACKET numberlist RBRACKET'
    p[0] = p[2]

def p_numberlist(p):
    '''numberlist : NUMBER
                 | numberlist COMMA NUMBER'''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[3]]



def p_error(p):
    print(p)

parser = yacc.yacc()

def parse_code(code):
    return parser.parse(code)

# 示例代码
code = "q1 := 0\n [[1,2,1],[1,2,1],[1,2,1]]"
print(parse_code(code))
