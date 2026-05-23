# type: ignore
class SyntaxError:
    def __init__(self, message, line, column):
        self.message = message
        self.line = line
        self.column = column

    def __repr__(self):
        return f"Erro Sintático: {self.message} na linha {self.line}, coluna {self.column}"


class BaseParser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.current_idx = 0
        self.errors = []

    def current_token(self):
        if self.current_idx < len(self.tokens):
            return self.tokens[self.current_idx]
        return None

    def advance(self):
        if self.current_idx < len(self.tokens):
            self.current_idx += 1
        return self.current_token()

    def match(self, expected_type, expected_value=None):
        token = self.current_token()
        if token is None:
            self.report_error(f"Esperado '{expected_value if expected_value else expected_type}', mas o arquivo terminou.")
            return False

        if token.type == expected_type:
            if expected_value is None or token.value == expected_value:
                self.advance()
                return True

        expected = expected_value if expected_value else expected_type
        self.report_error(f"Esperado '{expected}', mas encontrou '{token.value}'", token)
        return False

    def report_error(self, message, token=None):
        if token:
            err = SyntaxError(message, token.line, token.column)
        else:
            current = self.current_token()
            last_token = current if current else (self.tokens[-1] if self.tokens else None)
            line = last_token.line if last_token else 1
            column = last_token.column if last_token else 1
            err = SyntaxError(message, line, column)
        
        self.errors.append(err)
        self.synchronize()

    def synchronize(self):
        self.advance()
        while self.current_token() is not None:
            token = self.current_token()
            if token.value == ';':
                self.advance()
                return
            if token.type == "PALAVRA_RESERVADA" and token.value in ['int', 'float', 'char', 'if', 'while', 'for', 'return']:
                return
            self.advance()