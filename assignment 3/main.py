import re
import sys
import zipfile

# # Token types
# LPAREN = '('
# RPAREN = ')'
# LAMBDA = '\\'
# VAR = 'var'
# APP = 'app'
# EOF = 'eof'

# Token types
LPAREN = 'LPAREN'
RPAREN = 'RPAREN'
LAMBDA = 'LAMBDA'
ARROW = 'ARROW'
COLON = 'COLON'
VAR = 'VAR'

# Regular expressions for tokenizing
token_patterns = [
    (re.compile(r'\('), LPAREN),
    (re.compile(r'\)'), RPAREN),
    (re.compile(r'\\|λ'), LAMBDA),
    (re.compile(r'->'), ARROW),
    (re.compile(r':'), COLON),
    (re.compile(r'[a-zA-Z][a-zA-Z0-9]*'), VAR),
]

# Tokenize the input string
def tokenize(input_str):
    tokens = []
    while input_str:
        for pattern, token_type in token_patterns:
            match = pattern.match(input_str)
            if match:
                tokens.append((token_type, match.group()))
                input_str = input_str[match.end():].lstrip()
                break
        else:
            raise ValueError(f"Invalid token: {input_str}")
    return tokens

# AST Node class
class Node:
    def __init__(self, value, children=None):
        self.value = value
        self.children = children or []

# Parse the tokens into an abstract syntax tree (AST)
def parse(tokens):
    def parse_expr():
        token_type, token_value = tokens.pop(0)
        if token_type == LAMBDA:
            var_token = tokens.pop(0)
            if var_token[0] == VAR:
                type_token = tokens.pop(0)
                if type_token[0] == ARROW:
                    return Node('lambda', [var_token[1], type_token[1], parse_expr()])
                else:
                    raise ValueError("Missing '->' after lambda expression type.")
            else:
                raise ValueError("Invalid variable after lambda.")
        elif token_type == VAR:
            return Node('var', [token_value])
        elif token_type == LPAREN:
            expr = parse_expr()
            if tokens[0][0] == RPAREN:
                tokens.pop(0)  # Consume the closing parenthesis
                return expr
            else:
                raise ValueError("Mismatched parentheses.")
        else:
            raise ValueError(f"Unexpected token: {token_type}")

    def parse_type():
        token_type, token_value = tokens.pop(0)
        if token_type == VAR:
            return Node('type_var', [token_value])
        elif token_type == LPAREN:
            type_expr = parse_type()
            if tokens[0][0] == RPAREN:
                tokens.pop(0)  # Consume the closing parenthesis
                return type_expr
            else:
                raise ValueError("Mismatched parentheses in type.")
        else:
            raise ValueError(f"Unexpected token in type: {token_type}")

    expr = parse_expr()
    if tokens[0][0] == COLON:
        tokens.pop(0)  # Consume the colon
        type_expr = parse_type()
        return Node('judgement', [expr, type_expr])
    else:
        raise ValueError("Missing ':' in judgement.")

# Perform type checking on the AST
def type_check(ast):
    def check_judgement(node, context):
        expr, type_expr = node.children
        if check_expr(expr, context):
            return check_type(type_expr, context)
        else:
            raise ValueError("Expression does not type-check.")

    def check_expr(node, context):
        if node.value == 'var':
            var_name = node.children[0]
            if var_name in context:
                return True
            else:
                raise ValueError(f"Variable {var_name} has an unknown type.")
        elif node.value == 'lambda':
            var_name, type_var, body = node.children
            new_context = {var_name: type_var}
            new_context.update(context)
            return check_expr(body, new_context)
        else:
            raise ValueError("Invalid expression node.")

    def check_type(node, context):
        if node.value == 'type_var':
            type_var = node.children[0]
            if type_var in context:
                return True
            else:
                raise ValueError(f"Type variable {type_var} is not declared.")
        elif node.value == 'arrow':
            left_type, right_type = node.children
            return check_type(left_type, context) and check_type(right_type, context)
        else:
            raise ValueError("Invalid type node.")

    return check_judgement(ast, {})

def read_zip_file(file_path):
    with zipfile.ZipFile(file_path, 'r') as zip_file:
        for file_name in zip_file.namelist():
            with zip_file.open(file_name) as file:
                # Read the file contents
                content = file.read().decode('utf-8')

                # Print the result

# Main function to read input, tokenize, parse, and type-check
def main():
    if len(sys.argv) != 2:
        print("Usage: python program.py <input_file>")
        sys.exit(1)

    input_file = sys.argv[1]
    with open(input_file, 'r') as file:
        input_str = file.read()

    try:
        tokens = tokenize(input_str)
        ast = parse(tokens)
        type_check(ast)
        print("Judgement is derivable.")
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
