# type: ignore

class StatementsParser:

    def statement(self):
        token = self.current_token()
        if token is None:
            return

        if token.type == "PALAVRA_RESERVADA":
            if token.value in ['int', 'float', 'char', 'void']:
                self.declaration_or_assignment()
            elif token.value == 'if':
                self.condition_statement()
            elif token.value in ['while', 'for']:
                self.repetition_statement()
            elif token.value == 'return':
                self.return_statement()
            else:
                self.report_error(f"Declaração inválida iniciando com '{token.value}'", token)
        elif token.type == "IDENTIFICADOR":
            self.assignment_statement()
        elif token.value == '{':
            self.block_statement()
        else:
            self.report_error(f"Token inesperado fora de contexto: '{token.value}'", token)

    def block_statement(self):
        self.match("DELIMITADOR", "{")
        while self.current_token() is not None and self.current_token().value != "}":
            self.statement()
        self.match("DELIMITADOR", "}")

    def declaration_or_assignment(self):
        self.advance() 
        if self.match("IDENTIFICADOR"):
            next_token = self.current_token()
            if next_token and next_token.value == '=':
                self.match("OP_ATRIBUIÇÃO", "=")
                self.expression()
            self.match("DELIMITADOR", ";")

    def assignment_statement(self):
        self.match("IDENTIFICADOR")
        self.match("OP_ATRIBUIÇÃO", "=")
        self.expression()
        self.match("DELIMITADOR", ";")

    def condition_statement(self):
        self.match("PALAVRA_RESERVADA", "if")
        self.match("DELIMITADOR", "(")
        self.expression()
        self.match("DELIMITADOR", ")")
        self.statement()

        token = self.current_token()
        if token and token.type == "PALAVRA_RESERVADA" and token.value == "else":
            self.advance()
            self.statement()

    def repetition_statement(self):
        token = self.current_token()
        if token.value == "while":
            self.advance()
            self.match("DELIMITADOR", "(")
            self.expression()
            self.match("DELIMITADOR", ")")
            self.statement()
        elif token.value == "for":
            self.advance()
            self.match("DELIMITADOR", "(")
            if self.current_token() and self.current_token().value != ';':
                if self.current_token().value in ['int', 'float', 'char']:
                    self.declaration_or_assignment()
                else:
                    self.assignment_statement()
            else:
                self.match("DELIMITADOR", ";")
            
            if self.current_token() and self.current_token().value != ';':
                self.expression()
            self.match("DELIMITADOR", ";")
            
            if self.current_token() and self.current_token().value != ')':
                if self.current_token().type == "IDENTIFICADOR":
                    self.advance()
                    self.match("OP_ATRIBUIÇÃO", "=")
                    self.expression()
            self.match("DELIMITADOR", ")")
            self.statement()

    def return_statement(self):
        self.match("PALAVRA_RESERVADA", "return")
        if self.current_token() and self.current_token().value != ';':
            self.expression()
        self.match("DELIMITADOR", ";")