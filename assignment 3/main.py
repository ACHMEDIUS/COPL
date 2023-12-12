import zipfile
import tarfile
import os

# Token types
VAR = 'VAR'
LPAREN = 'LPAREN'
RPAREN = 'RPAREN'
LAMBDA = 'LAMBDA'
SEPARATOR = 'SEPARATOR'
ARROW = 'ARROW'
COLON = 'COLON'

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
    expr = parse_judgement(tokens)
    return expr

def parse_judgement(tokens):
    expr = parse_expr(tokens)
    if tokens[0][0] == COLON:
        tokens.pop(0)  # Consume ':'
        type_expr = parse_type(tokens)
        return (expr, type_expr)
    else:
        raise SyntaxError("Expected ':' in judgement")

def parse_expr(tokens):
    if len(tokens) == 0:
        raise SyntaxError("Unexpected end of input")

    if tokens[0][0] == VAR:
        return tokens.pop(0)

    if tokens[0][0] == LPAREN:
        tokens.pop(0)
        expr1 = parse_expr(tokens)
        if tokens[0][0] == SEPARATOR:
            tokens.pop(0)
            expr2 = parse_expr(tokens)
            if tokens[0][0] == RPAREN:
                tokens.pop(0)
                return (expr1, expr2)
            else:
                raise SyntaxError("Expected ')'")

    if tokens[0][0] == LAMBDA:
        tokens.pop(0)
        var = parse_expr(tokens)
        if tokens[0][0] == ARROW:
            tokens.pop(0)
            type_expr = parse_type(tokens)
            body = parse_expr(tokens)
            return (LAMBDA, var, type_expr, body)
        else:
            raise SyntaxError("Expected '->' after lambda abstraction")

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

def to_standard_format(expr):
    if type(expr) == tuple and expr[0] == VAR:
        return expr[1]
    elif type(expr) == tuple and expr[0] == LAMBDA:
        return f"(λ{expr[1]}^{expr[2]}.{to_standard_format(expr[3])})"
    elif type(expr) == tuple and expr[0] == LPAREN:
        return f"({to_standard_format(expr[1])} {to_standard_format(expr[2])})"
    elif type(expr) == tuple and expr[0] == SEPARATOR:
        return f"{to_standard_format(expr[1])}; {to_standard_format(expr[2])}"
    else:
        raise TypeError(f"Invalid expression type: {type(expr)}")

def output(judgement):
    standard_format_expr = to_standard_format(judgement[0])
    print(f"{standard_format_expr} : {to_standard_format(judgement[1])}")

def main():
    file_name = input("Enter the name of the archive file (zip or tar.gz): ")
    try:
        contents = read_archive(file_name)

        # Split the contents into lines and process each expression
        for line in contents.splitlines():
            tokens = lexer(line)
            judgement = parser(tokens)
            output(judgement)
    except Exception as e:
        print(f"Error: {e}")
        print("Exiting...")
        return 1
    return 0

if __name__ == '__main__':
    main()
