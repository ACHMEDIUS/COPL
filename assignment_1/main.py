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
            elif char == 'λ':
                tokens.append((LAMBDA, char))
            elif char == ';':
                tokens.append((SEPARATOR, char))
            elif char == '+':
                tokens.append((PLUS, char))
            elif char == '*':
                tokens.append((STAR, char))
            elif char == '.':
                tokens.append((DOT, char))

    # Check for the last token if any
    if current_token:
        tokens.append((VAR, current_token))

    return tokens

def parser(tokens):
    expr = parse_expr(tokens)
    return expr

def parse_expr(tokens):
    if not tokens:
        raise SyntaxError("Unexpected end of input")
    
    token_type, token_value = tokens[0]

    if token_type == VAR:
        tokens.pop(0)  # Remove the variable token
        return (VAR, token_value)  # Return a tuple representing the variable

    if tokens[0][1] == LPAREN:
        tokens.pop(0)
        if not tokens:
            raise SyntaxError("Expected expression after '('")
        expr = parse_expr(tokens)
        if not tokens or tokens[0][1] != RPAREN:
            raise SyntaxError("Expected ')'")
        tokens.pop(0)
        return expr

    if tokens[0][1] == LAMBDA:
        tokens.pop(0)
        if not tokens:
            raise SyntaxError("Expected variable after 'λ'")
        var = parse_expr(tokens)
        if not tokens or tokens[0][1] != LPAREN:
            raise SyntaxError("Expected '(' after variable in lambda")
        tokens.pop(0)
        if not tokens:
            raise SyntaxError("Expected expression after '(' in lambda")
        expr = parse_expr(tokens)
        if not tokens or tokens[0][1] != RPAREN:
            raise SyntaxError("Expected ')' after lambda expression")
        tokens.pop(0)
        return lambda var: expr

    raise SyntaxError("Unexpected token")

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
    print(f"The standard format is: {standard_format_expr}")

def main():
    input_string = input("Enter the expression: ")
    try:
        tokens = lexer(input_string)
        expr = parser(tokens)
        output(expr)
    except Exception as e:
        print(f"Error: {e}")
        print("Exiting")
        return 1
    return 0

if __name__ == '__main__':
    main()