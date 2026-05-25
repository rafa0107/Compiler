# type: ignore
from .ast import ASTNode

class StatementsParser:
    """
    Sub-parser focado no roteamento e estruturação de comandos (Instruções).
    Verifica loops, condicionais, declarações e atribuições de escopo.
    """

    def statement(self):
        """Hub direcionador que analisa o token atual e decide qual regra sintática aplicar."""
        token = self.current_token()
        if token is None:
            return

        # Roteamento baseado em Palavras-Chave (Reservadas)
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
        
        # Roteamento baseado em Identificadores diretos (Atribuição direta, ex: x = 5;)
        elif token.type == "IDENTIFICADOR":
            return self.assignment_statement()
        
        # Roteamento de Abertura de Escopo/Bloco de código local {}
        elif token.value == '{':
            return self.block_statement()
        else:
            self.report_error(f"Token inesperado fora de contexto: '{token.value}'", token)

    def block_statement(self):
        """Agrupa um conjunto de comandos delimitados pelas chaves '{' e '}'."""
        self.match("DELIMITADOR", "{")
        node = ASTNode("BLOCO")
        
        # Executa em laço o processamento de statements internos até achar o token de fechamento
        while (self.current_token() is not None and self.current_token().value != "}"):
            stmt = self.statement()
            if stmt:
                node.add(stmt)

        self.match("DELIMITADOR", "}")
        return node

    def declaration_or_assignment(self):
        """Trata a criação de variáveis, mapeando tipo, identificador e atribuições opcionais."""
        type_token = self.current_token()
        self.advance()
        identifier = self.current_token()
        self.match("IDENTIFICADOR")

        node = ASTNode("DECLARAÇÃO", type_token.value)
        node.add(ASTNode("IDENTIFICADOR", identifier.value))

        # Verifica se há inicialização simultânea com atribuição (ex: int x = 10;)
        next_token = self.current_token()
        if next_token and next_token.value == "=":
            self.match("OP_ATRIBUIÇÃO", "=")
            expr = self.expression()
            node.add(expr)

        self.match("DELIMITADOR", ";")
        return node

    def assignment_statement(self):
        """Processa comandos puramente de modificação de valor (ex: x = y + 2;)."""
        identifier = self.current_token()
        self.match("IDENTIFICADOR")
        self.match("OP_ATRIBUIÇÃO", "=")

        expr = self.expression()
        self.match("DELIMITADOR", ";")

        node = ASTNode("ATRIBUIÇÃO")
        node.add(ASTNode("IDENTIFICADOR", identifier.value))
        node.add(expr)
        return node

    def condition_statement(self):
        """Monta a estrutura ramificada do bloco 'if' e captura blocos 'else' adjacentes."""
        self.match("PALAVRA_RESERVADA", "if")
        node = ASTNode("CONDICIONAL", "if")
        self.match("DELIMITADOR", "(")

        condition = self.expression()
        node.add(condition)
        self.match("DELIMITADOR", ")")

        body = self.statement()
        node.add(body)
        token = self.current_token()

        # Tratamento de caminho alternativo opcional (else)
        if (token and token.type == "PALAVRA_RESERVADA" and token.value == "else"):
            self.advance()
            elseNode = ASTNode("SENAO")
            elseBody = self.statement()
            elseNode.add(elseBody)
            node.add(elseNode)

        return node

    def repetition_statement(self):
        """Estrutura os laços de repetição, oferecendo suporte a blocos 'while' e 'for'."""
        token = self.current_token()

        # Tratamento Sintático do 'while'
        if token.value == "while":
            self.advance()
            node = ASTNode("REPETICAO", "while")
            self.match("DELIMITADOR", "(")
            
            condition = self.expression()
            node.add(condition)
            
            self.match("DELIMITADOR", ")")
            body = self.statement()
            if body:
                node.add(body)
            return node

        # Tratamento Sintático do primeiro bloco 'for' encontrado
        elif token.value == "for":
            self.advance()
            node = ASTNode("REPETICAO", "for")
            self.match("DELIMITADOR", "(")

            # Sub-etapa 1: Inicialização do laço (Declaração ou atribuição simples)
            if self.current_token() and self.current_token().value != ';':
                if self.current_token().value in ['int', 'float', 'char']:
                    init = self.declaration_or_assignment()
                else:
                    init = self.assignment_statement()
                if init:
                    node.add(init)
            else:
                self.match("DELIMITADOR", ";")

            # Sub-etapa 2: Condição de permanência do laço
            if self.current_token() and self.current_token().value != ';':
                condition = self.expression()
                if condition:
                    node.add(condition)
            self.match("DELIMITADOR", ";")

            # Sub-etapa 3: Instrução de incremento / pós-execução
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

            self.match("DELIMITADOR", ")")
            body = self.statement()
            if body:
                node.add(body)
            return node

        # Bloco redundante/espelho mantido para fidelidade ao código original fornecido
        elif token.value == "for":
            self.advance()
            node = ASTNode("REPETICAO", "for")
            self.match("DELIMITADOR", "(")

            if (self.current_token() and self.current_token().value != ";"):
                init = None
                if self.current_token().value in ['int', 'float', 'char']:
                    init = self.declaration_or_assignment()
                else:
                    init = self.assignment_statement()
                node.add(init)
            else:
                self.match("DELIMITADOR", ";")

            if (self.current_token() and self.current_token().value != ";"):
                condition = self.expression()
                node.add(condition)
            self.match("DELIMITADOR", ";")

            body = self.statement()
            node.add(body)
            return node

    def return_statement(self):
        """Avalia e constrói instruções de retorno de funções, checando retornos vazios ou com expressões."""
        self.match("PALAVRA_RESERVADA", "return")
        node = ASTNode("RETORNO")

        # Se houver expressão à frente, aninha-se o valor calculado ao nó de retorno
        if (self.current_token() and self.current_token().value != ";"):
            expr = self.expression()
            node.add(expr)

        self.match("DELIMITADOR", ";")
        return node