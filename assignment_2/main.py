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
PLUS = 'PLUS'
STAR = 'STAR'
DOT = 'DOT'

# Token values
TOKEN_VALUES = {
    LPAREN: '(',
    RPAREN: ')',
    LAMBDA: 'λ', 
    SEPARATOR: ';',
    PLUS: '+',
    STAR: '*',
    DOT: '.'
}

# @function lexer
# @param input_string str
# @pre input_string is a string to be tokenized
# @post returns a list of tokens created from the input string
def lexer(input_string):
    tokens = []
    current_token = ''

    for char in input_string:
        print(f"Processing character: {char}")  # Debugging output

        if char == 'λ' or char == '\\':
            if current_token:
                tokens.append((VAR, current_token))
                current_token = ''
            tokens.append((LAMBDA, 'λ'))
        elif char.isalpha():
            # End the current token if it's not empty and start a new one
            if current_token:
                tokens.append((VAR, current_token))
                current_token = ''
            current_token = char
        elif char.isdigit():
            # Add digit to the current token if it's part of a variable name
            current_token += char
        elif char in TOKEN_VALUES.values():
            if current_token:
                tokens.append((VAR, current_token))
                current_token = ''
            token_type = [k for k, v in TOKEN_VALUES.items() if v == char][0]
            tokens.append((token_type, char))
        elif char.isspace():
            # Finalize the current token when encountering a space
            if current_token:
                tokens.append((VAR, current_token))
                current_token = ''
        else:
            print(f"Error: Unrecognized character '{char}'")

    if current_token:
        tokens.append((VAR, current_token))

    return tokens

# @function read_archive
# @param file_path str
# @pre file_path is the path to an archive file (zip or tar.gz)
# @post reads and returns the contents of the archive
def read_archive(file_path):
    contents = ""  
    _, file_extension = os.path.splitext(file_path)

    if file_extension == '.zip':
        with zipfile.ZipFile(file_path, 'r') as zip_file:
            for file_name in zip_file.namelist():
                print(f"Reading file: {file_name}")  # Print the name of the file being read
                with zip_file.open(file_name) as file:
                    content = file.read().decode('utf-8')
                    print("File contents:", content)  # Print the contents of the file
                    contents += content
    elif file_extension == '.tar.gz':
        with tarfile.open(file_path, 'r:gz') as tar_file:
            for tar_info in tar_file.getmembers():
                file = tar_file.extractfile(tar_info)
                content = file.read().decode('utf-8')
                print("File contents:", content)  # Print the contents of the file
                contents += content
    else:
        raise ValueError(f"Unsupported archive format: {file_extension}")
    return contents

# @function parser
# @param tokens list
# @pre tokens is a list of token tuples
# @post returns a parsed expression from the tokens
def parser(tokens):
    return parse_expr(tokens)

# @function parse_expr
# @param tokens list
# @pre tokens is a list of token tuples
# @post parses the tokens into an expression and returns it
def parse_expr(tokens):
    if not tokens:
        raise SyntaxError("Unexpected end of input")

    token_type, token_value = tokens.pop(0)

    if token_type == LPAREN:
        # Parse the expression inside the parentheses
        inner_expr = parse_expr(tokens)

        # Expect a closing parenthesis
        if not tokens or tokens.pop(0)[0] != RPAREN:
            raise SyntaxError("Expected ')'")
        return inner_expr

    elif token_type == LAMBDA:
        # Parse lambda abstraction
        return parse_lambda_abstraction(tokens)

    elif token_type == VAR:
        # Parse variable
        var_expr = (VAR, token_value)

        # If the next token is not a closing parenthesis, it could be an application
        if tokens and tokens[0][0] != RPAREN:
            return parse_application(var_expr, tokens)
        return var_expr

    else:
        raise SyntaxError(f"Unexpected token: {token_type}")

# @function parse_application
# @param func_expr tuple, tokens list
# @pre func_expr is a tuple representing a function expression, tokens are the remaining tokens
# @post parses and returns an application expression
def parse_application(func_expr, tokens):
    # Parse the argument of the application
    arg_expr = parse_expr(tokens)
    return ('APP', func_expr, arg_expr)

# @function parse_lambda_abstraction
# @param tokens list
# @pre tokens is a list of token tuples
# @post parses and returns a lambda abstraction expression
def parse_lambda_abstraction(tokens):
    if not tokens or tokens[0][0] != VAR:
        raise SyntaxError("Expected variable after 'λ'")
    var = tokens.pop(0)[1]

    if not tokens or tokens.pop(0)[0] != DOT:
        raise SyntaxError("Expected '.' after variable in lambda expression")

    body = parse_expr(tokens)
    return ('LAMBDA', var, body)

# @function alpha_conversion
# @param expr tuple, var_map dict
# @pre expr is an expression tuple, var_map is a dictionary for variable mapping
# @post performs alpha conversion and returns the modified expression
def alpha_conversion(expr, var_map):
    expr_type = expr[0]

    if expr_type == VAR:
        return (VAR, var_map.get(expr[1], expr[1]))

    if expr_type == 'LAMBDA':
        new_var = f"{expr[1]}'"
        var_map[expr[1]] = new_var
        return ('LAMBDA', new_var, alpha_conversion(expr[2], var_map))

    if expr_type == 'APP':
        return ('APP', alpha_conversion(expr[1], var_map), alpha_conversion(expr[2], var_map))

    raise SyntaxError(f"Invalid expression type: {expr_type}")

# @function beta_reduction
# @param expr tuple
# @pre expr is an expression tuple
# @post performs beta reduction and returns the reduced expression
def beta_reduction(expr):
    expr_type = expr[0]

    if expr_type == 'APP':
        left, right = expr[1], expr[2]

        if left[0] == 'LAMBDA':
            var, body = left[1], left[2]
            return substitute(body, var, right)

        return ('APP', beta_reduction(left), beta_reduction(right))

    if expr_type == 'LAMBDA':
        return ('LAMBDA', expr[1], beta_reduction(expr[2]))

    if expr_type == VAR:
        return expr

    raise SyntaxError(f"Invalid expression type: {expr_type}")

# @function substitute
# @param expr tuple, var str, replacement tuple
# @pre expr is an expression tuple, var is a variable name, replacement is an expression tuple
# @post substitutes the variable in expr with the replacement and returns the new expression
def substitute(expr, var, replacement):
    expr_type = expr[0]

    if expr_type == VAR:
        if expr[1] == var:
            return replacement
        return expr

    if expr_type == 'LAMBDA':
        if expr[1] != var:
            return ('LAMBDA', expr[1], substitute(expr[2], var, replacement))
        return expr

    if expr_type == 'APP':
        return ('APP', substitute(expr[1], var, replacement), substitute(expr[2], var, replacement))

    raise SyntaxError(f"Invalid expression type: {expr_type}")

# @function to_standard_format
# @param expr tuple
# @pre expr is an expression tuple
# @post returns the expression in its standard format as a string
def to_standard_format(expr):
    if expr[0] == VAR:
        return expr[1]
    elif expr[0] == 'LAMBDA':
        return f"(λ{expr[1]}.{to_standard_format(expr[2])})"
    elif expr[0] == 'APP':
        return f"({to_standard_format(expr[1])} {to_standard_format(expr[2])})"
    else:
        raise TypeError(f"Invalid expression type: {expr[0]}")

# @function output
# @param expr tuple
# @pre expr is an expression tuple
# @post prints the expression in its standard format
def output(expr):
    standard_format_expr = to_standard_format(expr)
    print(f"The reduced expression is {standard_format_expr}")

# @function main
# @pre program entry point
# @post reads input, processes it, and outputs the result in standard format
def main():
    if len(sys.argv) > 1:
        file_name = sys.argv[1]
        try:
            contents = read_archive(file_name)
            lines = contents.splitlines()
        except Exception as e:
            print(f"Error reading archive: {e}")
            return 1

        for line in lines:
            process_expression(line)
    else:
        # Debug mode: process a single expression
        input_string = input("Enter an expression: ")
        process_expression(input_string)

# @function process_expression
# @param input_string str
# @pre input_string is a string representing an expression
# @post processes the expression and outputs the result in standard format
def process_expression(input_string):
    try:
        tokens = lexer(input_string)
        expr = parser(tokens)
        var_map = {}
        expr = alpha_conversion(expr, var_map)

        limit = 1000
        for _ in range(limit):
            reduced_expr = beta_reduction(expr)
            if reduced_expr == expr:
                break
            expr = reduced_expr

        output(expr)
    except Exception as e:
        print(f"Error processing expression '{input_string}': {e}")

if __name__ == '__main__':
    main()