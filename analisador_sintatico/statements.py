# type: ignore
from .ast import ASTNode

class StatementsParser:
    """
    Sub-parser focado no roteamento e estruturação de comandos (Instruções).
    Verifica loops, condicionais, declarações e atribuições de escopo.
    """

    def statement(self):
        """Direcionador que analisa o token atual e decide qual regra sintática aplicar."""
        token = self.current_token()
        if token is None:
            return

        if token.type == "PALAVRA_RESERVADA":
            if token.value in ['int', 'float', 'char', 'void']:
                return self.declaration_or_assignment()
            elif token.value == 'if':
                return self.condition_statement()
            elif token.value in ['while', 'for']:
                return self.repetition_statement()
            elif token.value == 'return':
                return self.return_statement()
            else:
                self.report_error(f"Declaração inválida iniciando com '{token.value}'", token)
                self.synchronize() 
                return None
        
        elif token.type == "IDENTIFICADOR":
            return self.assignment_statement()
        
        elif token.value == '{':
            return self.block_statement()
        else:
            self.report_error(f"Token inesperado fora de contexto: '{token.value}'", token)
            self.synchronize() 
            return None

    def block_statement(self):
        self.match("DELIMITADOR", "{")
        node = ASTNode("BLOCO")
        
        while (self.current_token() is not None and self.current_token().value != "}"):
            token_antes = self.current_idx
            
            stmt = self.statement()
            if stmt:
                node.add(stmt)
            else:
                if token_antes == self.current_idx:
                    self.advance()

        self.match("DELIMITADOR", "}")
        return node

    def declaration_or_assignment(self):
        type_token = self.current_token()
        self.advance() 

        identifiers = []
        
        identifier = self.current_token()
        if self.match("IDENTIFICADOR"):
            identifiers.append(identifier.value)
        else:
            self.synchronize()
            return None

        while self.current_token() and self.current_token().value == ",":
            self.advance()
            next_id = self.current_token()
            if self.match("IDENTIFICADOR"):
                identifiers.append(next_id.value)
            else:
                self.synchronize() 
                return None

        node = ASTNode("DECLARAÇÃO_MULTIPLA", type_token.value)
        
        vars_node = ASTNode("VARIÁVEIS")
        for var in identifiers:
            vars_node.add(ASTNode("IDENTIFICADOR", var))
        node.add(vars_node)

        next_token = self.current_token()
        if next_token and next_token.value == "=":
            self.advance() 
            
            expr_node = ASTNode("VALORES_INICIAIS")
            
            first_expr = self.expression()
            if first_expr:
                expr_node.add(first_expr)
                
            while self.current_token() and self.current_token().value == ",":
                self.advance()
                next_expr = self.expression()
                if next_expr:
                    expr_node.add(next_expr) 
            node.add(expr_node)

        if not self.match("DELIMITADOR", ";"):
            self.synchronize()
        return node

    def assignment_statement(self):
        identifier = self.current_token()
        self.match("IDENTIFICADOR")
        self.match("OP_ATRIBUIÇÃO", "=")

        expr = self.expression()

        if not self.match("DELIMITADOR", ";"):
            self.synchronize()

        node = ASTNode("ATRIBUIÇÃO")
        node.add(ASTNode("IDENTIFICADOR", identifier.value))
        node.add(expr)
        return node

    def condition_statement(self):
        self.match("PALAVRA_RESERVADA", "if")
        node = ASTNode("CONDICIONAL", "if")

        if not self.match("DELIMITADOR", "("):
            self.synchronize()
            return None

        condition = self.expression()
        node.add(condition)

        if not self.match("DELIMITADOR", ")"):
            self.synchronize()
            
            # Se o pânico parou na abertura do bloco, consome o bloco defeituoso inteiro
            if self.current_token() and self.current_token().value == '{':
                self.block_statement() 
                
            if self.current_token() and self.current_token().value == 'else':
                self.advance() 
                if self.current_token() and self.current_token().value == '{':
                    self.block_statement()
                else:
                    self.synchronize()
            return None

        body = self.statement()
        node.add(body)
        token = self.current_token()

        if (token and token.type == "PALAVRA_RESERVADA" and token.value == "else"):
            self.advance()
            elseNode = ASTNode("SENAO")
            elseBody = self.statement()
            
            if elseBody:
                elseNode.add(elseBody)
            node.add(elseNode)
        return node

    def repetition_statement(self):
        token = self.current_token()

        # Tratamento Sintático do 'while'
        if token.value == "while":
            self.advance()
            node = ASTNode("REPETICAO", "while")

            if not self.match("DELIMITADOR", "("):
                self.synchronize()
                return None
            
            condition = self.expression()
            node.add(condition)
            
            if not self.match("DELIMITADOR", ")"):
                self.synchronize()
                if self.current_token() and self.current_token().value == '{':
                    self.block_statement() 
                return None
            
            body = self.statement()
            if body:
                node.add(body)
            return node

        # Tratamento Sintático do bloco 'for'
        elif token.value == "for":
            self.advance()
            node = ASTNode("REPETICAO", "for")

            if not self.match("DELIMITADOR", "("):
                self.synchronize()
                return None

            if self.current_token() and self.current_token().value != ';':
                if self.current_token().value in ['int', 'float', 'char']:
                    init = self.declaration_or_assignment()
                else:
                    init = self.assignment_statement()
                if init:
                    node.add(init)
            else:
                self.match("DELIMITADOR", ";")

            if self.current_token() and self.current_token().value != ';':
                condition = self.expression()
                if condition:
                    node.add(condition)
            self.match("DELIMITADOR", ";")

            # Sub-etapa 3: Instrução de incremento
            if self.current_token() and self.current_token().value != ')':
                increment = ASTNode("INCREMENTO")
                if self.current_token().type == "IDENTIFICADOR":
                    identifier = self.current_token()
                    self.advance()
                    increment.add(ASTNode("IDENTIFICADOR", identifier.value))
                    self.match("OP_ATRIBUIÇÃO", "=")
                    expr = self.expression()
                    increment.add(expr)
                node.add(increment)

            if not self.match("DELIMITADOR", ")"):  
                self.synchronize()
                if self.current_token() and self.current_token().value == '{':
                    self.block_statement()
                return None
            
            body = self.statement()
            if body:
                node.add(body)
            return node

    def return_statement(self):
        self.match("PALAVRA_RESERVADA", "return")
        node = ASTNode("RETORNO")

        if (self.current_token() and self.current_token().value != ";"):
            expr = self.expression()
            node.add(expr)

        self.match("DELIMITADOR", ";")
        return node