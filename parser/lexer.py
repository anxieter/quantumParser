import ply.lex as lex
import ply.yacc as yacc

# 词法分析器（Lexer）
tokens = (
    'SKIP', 'ASSIGN', 'IF', 'THEN', 'ELSE', 'FI', 'WHILE', 'DO', 'OD',
      'EQUAL', 'LBRACKET', 'RBRACKET', 'NUMBER', 'COMMA','ID' 
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

def t_ID(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
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
def p_statements(p):
    '''statements : statements statement
                  | statement'''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[2]]
        
def p_statement_skip(p):
    'statement : SKIP'
    p[0] = ('skip',)

def p_statement_assign(p):
    'statement : ID ASSIGN NUMBER'
    p[0] = ('assign', p[1], p[3])

def p_statement_mat_assign(p):
    'statement : ID EQUAL matrix'
    p[0] = ('mat_assign', p[1], p[3])


def p_statement_unitary(p):
    'statement : ID EQUAL ID LBRACKET ID RBRACKET'
    p[0] = ('unitary', p[1], p[3], p[5])

def p_matrix(p):
    'matrix : LBRACKET rowlist RBRACKET'
    p[0] = p[2]

def p_rowlist_multiple(p):
    'rowlist : rowlist COMMA row'
    p[0] = p[1] + [p[3]]

def p_rowlist_single(p):
    'rowlist : row'
    p[0] = [p[1]]

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

def p_statement_if(p):
    '''statement : IF ID LBRACKET ID RBRACKET EQUAL NUMBER THEN statement ELSE statement FI'''
    p[0] = ('if',p[2], p[4], p[7], p[9], p[11])
def p_statement_while(p):
    'statement : WHILE ID LBRACKET ID RBRACKET EQUAL NUMBER DO statement OD'
    p[0] = ('while',p[2], p[4], p[7], p[9])



def p_error(p):
    print(p)

parser = yacc.yacc()

def parse_code(code):
    return parser.parse(code)

# 示例代码
# code = "q1 := 0\n U0 = [[1,2,1],[1,2,1],[1,2,1]]\n M0 = [[1,2,1],[1,2,1],[1,2,1]]\n if M0[q0] = 1 then q1 := 1 else q1 := 0 fi\n while M0[q1] = 1 do q1 := 1 od"
# print(parse_code(code))
