# type: ignore
class ExpressionsParser:

    def expression(self):
        self.relational_expression()

    def relational_expression(self):
        self.arithmetic_expression()
        token = self.current_token()
        if token and token.type == "OP_RELACIONAL":
            self.advance()
            self.arithmetic_expression()

    def arithmetic_expression(self):
        self.term()
        while self.current_token() and self.current_token().value in ['+', '-']: 
            self.advance()
            self.term()

    def term(self):
        self.factor()
        while self.current_token() and self.current_token().value in ['*', '/']:
            self.advance()
            self.factor()

    def factor(self):
        token = self.current_token()
        if token is None:
            self.report_error("Expressão incompleta no fim do arquivo.")
            return

        if token.type in ["INTEIRO", "FLOAT", "STRING", "CHAR", "IDENTIFICADOR"]:
            self.advance()
        elif token.value == "(":
            self.advance()
            self.expression()
            self.match("DELIMITADOR", ")")
        else:
            self.report_error(f"Fator de expressão inválido: '{token.value}'", token)