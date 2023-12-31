import zipfile
import tarfile
import os
import sys

# Token types
VAR = 'VAR'
LPAREN = 'LPAREN'
RPAREN = 'RPAREN'
LAMBDA = 'LAMBDA'
SEPARATOR = 'SEPARATOR'
ARROW = 'ARROW'
COLON = 'COLON'

# @function lexer
# @param input_string str
# @pre input_string is the string representation of the lambda calculus expression
# @post returns a list of tokens parsed from the input string
def lexer(input_string):
    tokens = []
    current_token = ''

    for char in input_string:
        if char.isalnum() or char in ['λ', '\\']:
            current_token += char
        else:
            if current_token:
                tokens.append((VAR, current_token))
                current_token = ''

            if char == '(':
                tokens.append((LPAREN, char))
            elif char == ')':
                tokens.append((RPAREN, char))
            elif char == 'λ' or char == '\\':
                tokens.append((LAMBDA, char))
            elif char == ';':
                tokens.append((SEPARATOR, char))
            elif char == '-':
                tokens.append((ARROW, char))
            elif char == ':':
                tokens.append((COLON, char))

    # Check for the last token if any
    if current_token:
        tokens.append((VAR, current_token))

    return tokens

# @function read_archive
# @param file_path str
# @pre file_path is the path to a zip or tar.gz archive containing lambda calculus expressions
# @post reads the content of the archive and returns it as a string
def read_archive(file_path):
    contents = ""  
    if file_path.endswith('.zip'):
        with zipfile.ZipFile(file_path, 'r') as zip_file:
            for file_name in zip_file.namelist():
                with zip_file.open(file_name) as file:
                    content = file.read().decode('utf-8')
                    contents += content
    elif file_path.endswith('.tar.gz'):
        with tarfile.open(file_path, 'r:gz') as tar_file:
            for tar_info in tar_file.getmembers():
                if tar_info.isfile():
                    file = tar_file.extractfile(tar_info)
                    content = file.read().decode('utf-8')
                    contents += content
    else:
        raise ValueError(f"Unsupported archive format: {file_path}")

    return contents

# @function parser
# @param tokens list
# @pre tokens is a list of tokens representing a lambda calculus expression
# @post returns a parsed expression in the form of nested tuples
def parser(tokens):
    expr = parse_judgement(tokens)
    return expr

# @function parse_judgement
# @param tokens list
# @pre tokens is a list of tokens representing a judgement in lambda calculus
# @post parses the judgement and returns it as a tuple of expression and type
def parse_judgement(tokens):
    # print("Parsing Judgement, Tokens:", tokens)  # Debug print
    expr = parse_expr(tokens)
    # print("After Parsing Expr, Tokens:", tokens)  # Debug print
    if tokens and tokens[0][0] == COLON:
        tokens.pop(0)  # Consume ':'
        type_expr = parse_type(tokens)
        return (expr, type_expr)
    else:
        raise SyntaxError("Expected ':' in judgement")

# @function parse_expr
# @param tokens list
# @pre tokens is a list of tokens representing a lambda calculus expression
# @post returns the parsed expression as a nested tuple
def parse_expr(tokens):
    # print("Parsing Expr, Tokens:", tokens)  # Debug print
    if len(tokens) == 0:
        raise SyntaxError("Unexpected end of input")

    if tokens[0][0] == LPAREN:
        tokens.pop(0)  # Consume opening parenthesis
        sub_exprs = []
        while tokens and tokens[0][0] != RPAREN:
            sub_exprs.append(parse_expr(tokens))
            if tokens and tokens[0][0] in [SEPARATOR, ARROW]:
                tokens.pop(0)  # Consume separators or arrows within parentheses
        if tokens and tokens[0][0] == RPAREN:
            tokens.pop(0)  # Consume closing parenthesis
            return tuple(sub_exprs)  # Return a tuple of subexpressions
        else:
            raise SyntaxError("Expected ')'")

    token_type, token_value = tokens.pop(0)

    if token_type == LAMBDA:
        # Handle lambda expressions
        if tokens and tokens[0][0] == VAR:
            var_token = tokens.pop(0)
            var_name = var_token[1]
            # Check for type annotation
            if tokens and tokens[0][0] == ARROW:
                tokens.pop(0)  # Consume the arrow
                type_annotation = parse_type(tokens)
            else:
                type_annotation = None  # No type annotation present
            body = parse_expr(tokens)  # Parse the body of the lambda expression
            return (LAMBDA, var_name, type_annotation, body)
        else:
            raise SyntaxError("Expected variable after lambda")

    elif token_type == VAR:
        # Handle variables
        return (VAR, token_value)

# @function parse_type
# @param tokens list
# @pre tokens is a list of tokens representing a type expression in lambda calculus
# @post returns the parsed type expression as a tuple
def parse_type(tokens):
    if len(tokens) == 0:
        raise SyntaxError("Unexpected end of input")

    if tokens[0][0] == VAR:
        return tokens.pop(0)

    if tokens[0][0] == LPAREN:
        tokens.pop(0)
        type1 = parse_type(tokens)
        if tokens[0][0] == ARROW:
            tokens.pop(0)
            type2 = parse_type(tokens)
            if tokens[0][0] == RPAREN:
                tokens.pop(0)
                return (type1, ARROW, type2)
            else:
                raise SyntaxError("Expected ')' after type")
        else:
            raise SyntaxError("Expected '->' in type")

# @function beta_reduction
# @param expr tuple, var str, arg tuple
# @pre expr is a lambda calculus expression tuple, var is a variable name, arg is an expression tuple
# @post applies beta reduction on the expression, substituting the variable with the argument    
def beta_reduction(expr, var, arg):
    if type(expr) == tuple and expr[0] == VAR:
        return arg if expr[1] == var else expr
    elif type(expr) == tuple and expr[0] == LAMBDA:
        return (LAMBDA, expr[1], expr[2], beta_reduction(expr[3], var, arg))
    elif type(expr) == tuple and expr[0] == LPAREN:
        return (LPAREN, beta_reduction(expr[1], var, arg), beta_reduction(expr[2], var, arg), beta_reduction(expr[3], var, arg), RPAREN)
    elif type(expr) == tuple and expr[0] == SEPARATOR:
        return (SEPARATOR, beta_reduction(expr[1], var, arg), beta_reduction(expr[2], var, arg))
    else:
        raise TypeError(f"Invalid expression type: {type(expr)}")

# @function to_standard_format
# @param expr tuple
# @pre expr is a lambda calculus expression tuple
# @post returns the string representation of the expression in standard lambda calculus notation
def to_standard_format(expr):
    if isinstance(expr, tuple):
        if expr[0] == VAR:
            return expr[1]
        elif expr[0] == LAMBDA:
            var_name = expr[1]
            type_annotation = to_standard_format(expr[2]) if expr[2] is not None else ''
            body = to_standard_format(expr[3])
            return f"(λ{var_name}^{type_annotation}.{body})"
        else:
            # Handle nested tuple expressions
            return ' '.join(to_standard_format(sub_expr) for sub_expr in expr)
    elif isinstance(expr, str):
        # Directly return strings (like variables or types)
        return expr
    else:
        raise TypeError(f"Invalid expression type: {type(expr)}")

# @function output
# @param judgement tuple
# @pre judgement is a tuple of lambda calculus expression and its type
# @post prints the judgement in a human-readable format 
def output(judgement):
    standard_format_expr = to_standard_format(judgement[0])
    print(f"{standard_format_expr} : {to_standard_format(judgement[1])}")

# @function main
# @pre main entry point of the program
# @post reads input (either a single expression or a file containing multiple expressions), parses, and outputs the result
def main():
    if len(sys.argv) > 1:
        file_name = sys.argv[1]
        try:
            contents = read_archive(file_name)
        except Exception as e:
            print(f"Error: {e}")
            print("Exiting")
            return 1
        for line in contents.splitlines():
                tokens = lexer(line)
                judgement = parser(tokens)
                output(judgement)
    else:
        # Debug mode: process a single expression
        expression = input("Enter an expression: ")
        tokens = lexer(expression)
        judgement = parser(tokens)
        output(judgement)
    return 0

if __name__ == '__main__':
    main()
