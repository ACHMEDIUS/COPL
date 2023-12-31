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
# @pre input_string is a string containing the expression to be tokenized
# @post returns a list of tokens derived from the input string
def lexer(input_string):
    tokens = []
    current_token = ''

    for char in input_string:
        if char.isspace():  # Ignore spaces
            if current_token:  # End of a token
                tokens.append((VAR, current_token))
                current_token = ''
            continue

        if char.isalnum():
            current_token += char
        else:
            if current_token:
                tokens.append((VAR, current_token))
                current_token = ''
            if char == 'λ' or char == '\\':
                tokens.append((LAMBDA, 'λ'))
            elif char == ';':
                tokens.append((SEPARATOR, char))
            elif char == '+':
                tokens.append((PLUS, char))
            elif char == '*':
                tokens.append((STAR, char))
            elif char == '.':
                tokens.append((DOT, char))

    if current_token: 
        tokens.append((VAR, current_token))

    return tokens

# @function parser
# @param tokens list
# @pre tokens is a list of tuples representing the tokenized input
# @post returns a parsed expression from the tokens
def parser(tokens):
    expr = parse_expr(tokens)
    return expr

# @function parse_expr
# @param tokens list
# @pre tokens is a list of tuples representing the tokenized input
# @post parses the tokens into an expression and returns it
def parse_expr(tokens):
    if not tokens:
        raise SyntaxError("Unexpected end of input")

    token_type, token_value = tokens.pop(0)

    if token_type == VAR:
        expr = token_value
        while tokens and tokens[0][0] == VAR:
            _, next_token_value = tokens.pop(0)
            expr += next_token_value
        return (VAR, expr)

    elif token_type == LAMBDA:
        if not tokens or tokens[0][0] != VAR:
            raise SyntaxError("Expected variable after 'λ'")
        var_token = tokens.pop(0)
        if not tokens or tokens[0][0] != DOT:
            raise SyntaxError("Expected '.' after variable in lambda")
        tokens.pop(0)  # Remove the '.' token
        body = parse_expr(tokens)
        return (LAMBDA, f"λ{var_token[1]}. {body[1]}")

    elif token_type == LPAREN:
        func = parse_expr(tokens)
        if not tokens or tokens[0][0] != RPAREN:
            raise SyntaxError("Expected ')' after function in application")
        tokens.pop(0)  # Remove the ')' token
        if tokens:
            arg = parse_expr(tokens)
            return (VAR, f"{func[1]} {arg[1]}")
        return func

    else:
        raise SyntaxError("Unexpected token")

# @function to_standard_format
# @param expr tuple
# @pre expr is a tuple representing a parsed expression
# @post returns the expression in its standard format as a string
def to_standard_format(expr):
    return expr[1]

# @function output
# @param expr tuple
# @pre expr is a tuple representing a parsed expression
# @post prints the expression in its standard format
def output(expr):
    standard_format_expr = to_standard_format(expr)
    print(f"The standard format is: {standard_format_expr}")

# @function read_archive
# @param file_path str
# @pre file_path is the path to an archive file (zip or tar.gz)
# @post reads and returns the contents of the archive
def read_archive(file_path):
    contents = ""  
    _, file_extension = os.path.splitext(file_path)

    # Check for '.tar.gz' extension
    if file_extension == '.gz':
        base, ext = os.path.splitext(_)
        if ext == '.tar':
            file_extension = ext + file_extension

    if file_extension == '.zip':
        with zipfile.ZipFile(file_path, 'r') as zip_file:
            for file_name in zip_file.namelist():
                with zip_file.open(file_name) as file:
                    content = file.read().decode('utf-8')
                    contents += content
    elif file_extension == '.tar.gz':
        with tarfile.open(file_path, 'r:gz') as tar_file:
            for tar_info in tar_file.getmembers():
                file = tar_file.extractfile(tar_info)
                if file:  # Check if it's not a directory
                    content = file.read().decode('utf-8')
                    contents += content
    else:
        raise ValueError(f"Unsupported archive format: {file_extension}")
    return contents

# @function main
# @pre program entry point
# @post reads input, processes it, and outputs the result in standard format
def main():
    if len(sys.argv) > 1:
        file_name = sys.argv[1]
        contents = read_archive(file_name)
        expressions = contents.splitlines()
    else:
        expressions = [input("Enter the expression: ")]

    for input_string in expressions:
        try:
            tokens = lexer(input_string)
            expr = parser(tokens)
            output(expr)
        except Exception as e:
            print(f"Error: {e}")

if __name__ == '__main__':
    main()