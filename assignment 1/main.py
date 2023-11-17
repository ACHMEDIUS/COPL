import sys
import zipfile
import zipfile

# Define token types
LPAREN = '('
RPAREN = ')'
LAMBDA = '\\'
VAR = 'var'
APP = 'app'
EOF = 'eof'

class Token:
    def __init__(self, type, value=None):
        self.type = type
        self.value = value

    def __repr__(self):
        if self.value:
            return f'Token({self.type}, {self.value})'
        else:
            return f'Token({self.type})'

class Lexer:
    def __init__(self, text):
        self.text = text
        self.pos = 0
        self.current_char = self.text[self.pos]

    def error(self):
        raise Exception('Invalid character')

    def advance(self):
        self.pos += 1
        if self.pos > len(self.text) - 1:
            self.current_char = None
        else:
            self.current_char = self.text[self.pos]

    def skip_whitespace(self):
        while self.current_char is not None and self.current_char.isspace():
            self.advance()

    def get_var(self):
        result = ''
        while self.current_char is not None and self.current_char.isalnum():
            result += self.current_char
            self.advance()
        return result

    def get_next_token(self):
        while self.current_char is not None:
            if self.current_char.isspace():
                self.skip_whitespace()
                continue

            if self.current_char == LPAREN:
                self.advance()
                return Token(LPAREN)

            if self.current_char == RPAREN:
                self.advance()
                return Token(RPAREN)

            if self.current_char == LAMBDA:
                self.advance()
                var = self.get_var()
                return Token(LAMBDA, var)

            if self.current_char.isalpha():
                var = self.get_var()
                return Token(VAR, var)

            self.error()

        return Token(EOF)

class Parser:
    def __init__(self, lexer):
        self.lexer = lexer
        self.current_token = self.lexer.get_next_token()

    def error(self):
        raise Exception('Invalid syntax')

    def eat(self, token_type):
        if self.current_token.type == token_type:
            self.current_token = self.lexer.get_next_token()
        else:
            self.error()

    def var(self):
        token = self.current_token
        self.eat(VAR)
        return token.value

    def factor(self):
        token = self.current_token
        if token.type == LPAREN:
            self.eat(LPAREN)
            expr = self.expr()
            self.eat(RPAREN)
            return expr
        elif token.type == LAMBDA:
            self.eat(LAMBDA)
            var = self.var()
            self.eat('.')
            expr = self.expr()
            return (LAMBDA, var, expr)
        elif token.type == VAR:
            return self.var()

    def term(self):
        left = self.factor()

        while self.current_token.type == APP:
            self.eat(APP)
            right = self.factor()
            left = (APP, left, right)

        return left

    def expr(self):
        return self.term()

class Interpreter:
    def __init__(self):
        pass

    def eval(self, expr, env=None):
        if env is None:
            env = {}

        if isinstance(expr, str):
            return env.get(expr, expr)
        elif expr[0] == LAMBDA:
            return (LAMBDA, expr[1], self.eval(expr[2], env))
        elif expr[0] == APP:
            left = self.eval(expr[1], env)
            right = self.eval(expr[2], env)
            if left[0] == LAMBDA:
                return self.eval(left[2], {**env, left[1]: right})
            else:
                return (APP, left, right)


def read_zip_file(file_path):
    with zipfile.ZipFile(file_path, 'r') as zip_file:
        for file_name in zip_file.namelist():
            with zip_file.open(file_name) as file:
                # Do something with the file contents
                print(file.read())


def main():
    # text = input("Enter the lambda calculus expression: ")
    # lexer = Lexer(text)
    # parser = Parser(lexer)
    # interpreter = Interpreter()
    # expr = parser.expr()
    # result = interpreter.eval(expr)
    file_name = input("Enter the name of the zip file: ")
    # read_zip_file(file_name)
    # print(result)
    print(read_zip_file(file_name))

if __name__ == '__main__':
    main()