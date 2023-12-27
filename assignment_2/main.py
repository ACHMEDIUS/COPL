import zipfile
import tarfile
import os

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

def lexer(input_string):
    tokens = []
    current_token = ''

    for char in input_string:
        print(f"Processing character: {char}")  # Debugging output

        if char == 'λ':
            if current_token:
                tokens.append((VAR, current_token))
                current_token = ''
            tokens.append((LAMBDA, char))
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


def parser(tokens):
    return parse_expr(tokens)

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

def parse_application(func_expr, tokens):
    # Parse the argument of the application
    arg_expr = parse_expr(tokens)
    return ('APP', func_expr, arg_expr)

def parse_lambda_abstraction(tokens):
    if not tokens or tokens[0][0] != VAR:
        raise SyntaxError("Expected variable after 'λ'")
    var = tokens.pop(0)[1]

    if not tokens or tokens.pop(0)[0] != DOT:
        raise SyntaxError("Expected '.' after variable in lambda expression")

    body = parse_expr(tokens)
    return ('LAMBDA', var, body)

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

def to_standard_format(expr):
    if expr[0] == VAR:
        return expr[1]
    elif expr[0] == 'LAMBDA':
        return f"(λ{expr[1]}.{to_standard_format(expr[2])})"
    elif expr[0] == 'APP':
        return f"({to_standard_format(expr[1])} {to_standard_format(expr[2])})"
    else:
        raise TypeError(f"Invalid expression type: {expr[0]}")

def output(expr):
    standard_format_expr = to_standard_format(expr)
    print(standard_format_expr)

def main():
    file_name = input("Enter the name of the archive file (zip or tar.gz): ")
    try:
        contents = read_archive(file_name)

        for line in contents.splitlines():
            tokens = lexer(line)
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
        print(f"Error: {e}")
        print("Exiting")
        return 1
    return 0

if __name__ == '__main__':
    main()