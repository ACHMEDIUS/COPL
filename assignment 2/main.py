import zipfile
import tarfile
import os

# Token types
VAR = 'VAR'
LPAREN = 'LPAREN'
RPAREN = 'RPAREN'
LAMBDA = 'LAMBDA'
SEPARATOR = 'SEPARATOR'

def lexer(input_string):
    tokens = []
    current_token = ''

    for char in input_string:
        if char.isalnum():
            current_token += char
        else:
            if current_token:
                tokens.append((VAR, current_token))
                current_token = ''

            if char == '(':
                tokens.append((LPAREN, char))
            elif char == ')':
                tokens.append((RPAREN, char))
            elif char == '\\':
                tokens.append((LAMBDA, char))
            elif char == ';':
                tokens.append((SEPARATOR, char))

    # Check for the last token if any
    if current_token:
        tokens.append((VAR, current_token))

    return tokens

def read_archive(file_path):
    contents = ""  # Initialize an empty string to store the contents
    # Determine the file type based on the extension
    _, file_extension = os.path.splitext(file_path)

    if file_extension == '.zip':
        with zipfile.ZipFile(file_path, 'r') as zip_file:
            for file_name in zip_file.namelist():
                with zip_file.open(file_name) as file:
                    # Read the file contents and append to the string
                    content = file.read().decode('utf-8')
                    contents += content
    elif file_extension == '.tar.gz':
        with tarfile.open(file_path, 'r:gz') as tar_file:
            for tar_info in tar_file.getmembers():
                file = tar_file.extractfile(tar_info)
                # Read the file contents and append to the string
                content = file.read().decode('utf-8')
                contents += content
    else:
        raise ValueError(f"Unsupported archive format: {file_extension}")
    return contents

def parser(tokens):
    expr = parse_expr(tokens)
    return expr

def parse_expr(tokens):
    if len(tokens) == 0:
        raise SyntaxError("Unexpected end of input")

    if type(tokens[0]) == VAR:
        return tokens.pop(0)

    if tokens[0] == LPAREN:
        tokens.pop(0)
        expr = parse_expr(tokens)
        if tokens[0] == RPAREN:
            tokens.pop(0)
            return expr
        else:
            raise SyntaxError("Expected ')'")

    if tokens[0] == LAMBDA:
        tokens.pop(0)
        var = parse_expr(tokens)
        if tokens[0] != LPAREN:
            raise SyntaxError("Expected '(' after lambda abstraction")
        tokens.pop(0)
        body = parse_expr(tokens)
        if tokens[0] != RPAREN:
            raise SyntaxError("Expected ')' after lambda expression")
        tokens.pop(0)
        return lambda arg: beta_reduction(body, var, arg)

def beta_reduction(expr, var, arg):
    if type(expr) == tuple and expr[0] == VAR and expr[1] == var:
        return arg
    elif type(expr) == tuple and expr[0] == VAR:
        return expr
    elif type(expr) == tuple and expr[0] == LAMBDA:
        return (LAMBDA, expr[1], beta_reduction(expr[2], var, arg))
    elif type(expr) == tuple and expr[0] == LPAREN:
        return (LPAREN, beta_reduction(expr[1], var, arg), beta_reduction(expr[2], var, arg), beta_reduction(expr[3], var, arg), RPAREN)
    else:
        raise TypeError(f"Invalid expression type: {type(expr)}")

def to_standard_format(expr):
    if type(expr) == tuple and expr[0] == VAR:
        return expr[1]
    elif type(expr) == tuple and expr[0] == LAMBDA:
        return f"(λ{expr[1]}.{to_standard_format(expr[2])})"
    elif type(expr) == tuple and expr[0] == LPAREN:
        return f"({to_standard_format(expr[1])} {to_standard_format(expr[2])} {to_standard_format(expr[3])})"
    else:
        raise TypeError(f"Invalid expression type: {type(expr)}")

def output(expr):
    standard_format_expr = to_standard_format(expr)
    print(standard_format_expr)

def main():
    file_name = input("Enter the name of the archive file (zip or tar.gz): ")
    try:
        contents = read_archive(file_name)

        # Split the contents into lines and process each expression
        for line in contents.splitlines():
            tokens = lexer(line)
            expr = parser(tokens)
            while True:
                reduced_expr = beta_reduction(expr, None, None)
                if reduced_expr == expr:
                    break
                expr = reduced_expr
            output(expr)
    except Exception as e:
        print(f"Error: {e}")
        print("Exiting...")
        return 1
    return 0
if __name__ == '__main__':
    main()
