import ply.lex as lex
import ply.yacc as yacc

# 词法分析器（Lexer）
tokens = (
    'SKIP',  'IF', 'THEN', 'ELSE', 'FI', 'WHILE', 'DO', 'OD',
      'EQUAL', 'LBRACKET', 'RBRACKET', 'NUMBER', 'COMMA','ID','MULTIEQUAL' ,'COMPLEX', 'PRINT',
      
)

t_LBRACKET = r'\['
t_RBRACKET = r'\]'
t_COMMA = r','
t_EQUAL = r'='
t_ignore = ' \t\n'



def t_PRINT(t):
    r'print'
    return t


def t_SKIP(t):
    r'skip'
    return t


def t_MULTIEQUAL(t):
    r'\*='
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

def t_COMPLEX(t):# a+bj
    r'-?\d+(\.\d+)?[+-]\d+(\.\d+)?j'
    t.value = complex(t.value)  # 转换为复数类型
    return t

# 纯实数匹配（防止误识别）
def t_NUMBER(t):
    r'-?\d+(\.\d+)?'
    t.value = float(t.value)  # 转换为浮点数
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
    '''STATEMENTS : STATEMENTS STATEMENT
                  | STATEMENT'''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[2]]
        
def p_statement_skip(p):
    'STATEMENT : SKIP'
    p[0] = ('skip',)

def p_statement_assign(p):
    'STATEMENT : ID EQUAL NUMBER'
    p[0] = ('assign', p[1], p[3])

def p_statement_mat_assign(p):
    'STATEMENT : ID EQUAL MATRIX'
    p[0] = ('mat_assign', p[1], p[3])

def p_multiple_IDs(p):
    '''IDS : ID
           | IDS COMMA ID'''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[3]]
        
def p_statement_unitary(p):
    'STATEMENT : IDS MULTIEQUAL ID '
    p[0] = ('unitary', p[1], p[3])

def p_MATRIX(p):
    'MATRIX : LBRACKET ROWLIST RBRACKET'
    p[0] = p[2]

def p_ROWLIST_multiple(p):
    'ROWLIST : ROWLIST COMMA ROW'
    p[0] = p[1] + [p[3]]

def p_ROWLIST_single(p):
    'ROWLIST : ROW'
    p[0] = [p[1]]

def p_ROW(p):
    'ROW : LBRACKET NUMBERLIST RBRACKET'
    p[0] = p[2]

def p_NUMBERLIST(p):
    '''NUMBERLIST : NUMBER
                 | COMPLEX
                 | NUMBERLIST COMMA NUMBER
                 | NUMBERLIST COMMA COMPLEX'''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[3]]

def p_statement_if(p):
    '''STATEMENT : IF ID LBRACKET IDS RBRACKET EQUAL NUMBER THEN STATEMENTS ELSE STATEMENTS FI'''
    p[0] = ('if',p[2], p[4], p[7], p[9], p[11])
def p_statement_while(p):
    'STATEMENT : WHILE ID LBRACKET IDS RBRACKET EQUAL NUMBER DO STATEMENTS OD'
    p[0] = ('while',p[2], p[4], p[7], p[9])

def p_print(p):
    'STATEMENT : PRINT LBRACKET IDS RBRACKET'
    p[0] = ('print', p[3])

def p_error(p):
    print(p)

parser = yacc.yacc()

def parse_code(code):
    return parser.parse(code)

# code = "q1 = 0\n U0 = [[1,2,1],[1,2,1],[1,2,1]]\n M0 = [[1,2,1],[1,2,1],[1,2,1]]\n if M0[q0] = 1 then q1 = 1 else q1 = 0 fi\n while M0[q1] = 1 do q1 = 1 od"
# print(parse_code(code))


##Preserved matrix: X, H, Z, Y, S, CNOT (handled in next stage)