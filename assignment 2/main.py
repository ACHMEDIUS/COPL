import sys
import zipfile

# Token types
LPAREN = '('
RPAREN = ')'
LAMBDA = '\\'
VAR = 'var'
APP = 'app'
EOF = 'eof'

def tokenize(expr):
    tokens = []
    i = 0
    while i < len(expr):
        if expr[i].isspace():
            i += 1
        elif expr[i] == '(':
            tokens.append((LPAREN, '('))
            i += 1
        elif expr[i] == ')':
            tokens.append((RPAREN, ')'))
            i += 1
        elif expr[i] == '\\':
            tokens.append((LAMBDA, '\\'))
            i += 1
        else:
            j = i
            while j < len(expr) and (expr[j].isalnum() or expr[j] == '_'):
                j += 1
            tokens.append((VAR, expr[i:j]))
            i = j
    return tokens

def parse(tokens):
    def parse_expr():
        if not tokens:
            raise SyntaxError("Unexpected end of input")

        token = tokens.pop(0)
        if token[0] == VAR:
            return token[1]
        elif token[0] == LPAREN:
            expr1 = parse_expr()
            assert tokens.pop(0)[0] == RPAREN, "Mismatched parentheses"
            expr2 = parse_expr()
            return (expr1, expr2)
        elif token[0] == LAMBDA:
            var = tokens.pop(0)[1]
            expr = parse_expr()
            return (LAMBDA, var, expr)

    return parse_expr()

def reduce_ast(ast, reduction_limit=1000):
    if isinstance(ast, tuple):
        op, *args = ast
        if op == LAMBDA:
            var, expr = args
            return (LAMBDA, var, reduce_ast(expr))
        elif op == VAR:
            return ast
        else:
            func, arg = map(reduce_ast, args)
            if func[0] == LAMBDA:
                return reduce_ast(substitute(func[2], func[1], arg))
            else:
                return (func, arg)
    else:
        return ast

def substitute(expr, var, replacement):
    if isinstance(expr, tuple):
        op, *args = expr
        return (op, *(substitute(arg, var, replacement) for arg in args))
    else:
        return replacement if expr == var else expr
    
def read_zip_file(file_path):
    with zipfile.ZipFile(file_path, 'r') as zip_file:
        for file_name in zip_file.namelist():
            with zip_file.open(file_name) as file:
                # Read the file contents
                content = file.read().decode('utf-8')

                # Print the result

def main():
    if len(sys.argv) != 2:
        print("Usage: python interpreter.py <input_file>")
        sys.exit(1)

    input_file = sys.argv[1]
    try:
        with open(input_file, 'r') as file:
            expression = file.read()
    except FileNotFoundError:
        print(f"Error: File '{input_file}' not found.")
        sys.exit(1)

    tokens = tokenize(expression)
    try:
        ast = parse(tokens)
    except SyntaxError as e:
        print(f"SyntaxError: {e}")
        sys.exit(1)

    reduced_ast = reduce_ast(ast)

    # Print the reduced AST
    print(reduced_ast)

    # Exit status based on whether further reduction is possible
    sys.exit(0 if ast == reduced_ast else 2)

if __name__ == "__main__":
    main()
