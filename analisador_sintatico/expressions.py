# type: ignore
from .ast import ASTNode

class ExpressionsParser:
    """
    Sub-parser encarregado de processar expressões matemáticas e lógicas.
    Implementa a técnica de descida recursiva respeitando a precedência de operadores.
    """

    def expression(self):
        """Ponto de entrada de menor precedência: delega para expressões relacionais."""
        return self.relational_expression()

    def relational_expression(self):
        """Processa operadores relacionais (ex: <, >, ==). Isola operações aritméticas nas pontas."""
        left = self.arithmetic_expression()
        token = self.current_token()
        
        if token and token.type == "OP_RELACIONAL":
            operator = token.value
            self.advance()
            right = self.arithmetic_expression()
            node = ASTNode("EXPRESSÃO RELACIONAL", operator)
            node.add(left)
            node.add(right)
            return node
        return left

    def arithmetic_expression(self):
        """Garante a associatividade à esquerda e precedência menor para adição (+) e subtração (-)."""
        left = self.term()
        while (
            self.current_token()
            and self.current_token().value in ["+", "-"]
        ):
            op = self.current_token()
            self.advance()
            right = self.term()
            node = ASTNode("EXPRESSÃO ARITMÉTICA", op.value)
            node.add(left)
            node.add(right)
            left = node # O nó atual vira o filho esquerdo do próximo operador do loop
        return left

    def term(self):
        """Garante maior precedência para multiplicação (*) e divisão (/) sobre a soma."""
        left = self.factor()
        while (
            self.current_token()
            and self.current_token().value in ["*", "/"]
        ):
            op = self.current_token()
            self.advance()
            right = self.factor()
            node = ASTNode("TERMO", op.value)
            node.add(left)
            node.add(right)
            left = node
        return left

    def factor(self):
        """
        Unidade elementar de maior precedência da gramática.
        Pode resolver literais (números/strings), identificadores (variáveis) ou
        redefinir a prioridade recursivamente caso encontre parênteses '()'.
        """
        token = self.current_token()
        if token is None:
            self.report_error("Expressão incompleta")
            return None

        # Caso 1: Valores Literais diretos
        if token.type in ["INTEIRO", "FLOAT", "STRING", "CHAR"]:
            self.advance()
            return ASTNode("LITERAL", token.value)

        # Caso 2: Variáveis (Identificadores)
        elif token.type == "IDENTIFICADOR":
            self.advance()
            return ASTNode("IDENTIFICADOR", token.value)

        # Caso 3: Agrupamento por parênteses (Eleva a precedência interna de uma expressão)
        elif token.value == "(":
            self.advance()
            node = self.expression()
            if not self.match("DELIMITADOR", ")"):
                print("teste factor arrumado")
                return node

        self.report_error(f"Fator inválido: {token.value}", token)
        return None