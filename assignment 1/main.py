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

def parser(tokens):
    expr = parse_expr(tokens)
    return expr

def parse_expr(tokens):
    if len(tokens) == 0:
        raise SyntaxError("Unexpected end of input")

    if type(tokens[0][1]) == VAR:
        return tokens.pop(0)

    if tokens[0][1] == LPAREN:
        tokens.pop(0)
        expr = parse_expr(tokens)
        if tokens[0][1] == RPAREN:
            tokens.pop(0)
            return expr
        else:
            raise SyntaxError("Expected ')'")

    if tokens[0][1] == LAMBDA:
        name = "lambda"
        tokens.pop(0)
        var = parse_expr(tokens)
        if tokens[0][1] != LPAREN:
            raise SyntaxError("Expected '(' after lambda abstraction")
        tokens.pop(0)
        expr = parse_expr(tokens)
        if tokens[0][1] != RPAREN:
            raise SyntaxError("Expected ')' after lambda expression")
        tokens.pop(0)
        return lambda var: expr

def to_standard_format(expr):
    if type(expr[1]) == str:
        return expr[1]
    elif type(expr[1]) == type(lambda x: x):
        var = expr[1].__var__
        expr = expr[1](var)
        return f"(λ{var}. {expr})"
    else:
        raise TypeError(f"Invalid expression type: {type(expr[1])}")

def output(expr):
    standard_format_expr = to_standard_format(expr)
    print(standard_format_expr)

def main():
    input_string = input("Enter the lambda calculus expression: ")
    try:
        tokens = lexer(input_string)
        expr = parser(tokens)
        output(expr)
    except Exception as e:
        print(f"Error: {e}")
        print("Exiting...")
        return 1
    return 0

if __name__ == '__main__':
    main()