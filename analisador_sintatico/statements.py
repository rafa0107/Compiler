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
                self.synchronize() # Sincroniza após erro de palavra reservada inválida
                return None
        
        # Roteamento baseado em Identificadores diretos (Atribuição direta, ex: x = 5;)
        elif token.type == "IDENTIFICADOR":
            return self.assignment_statement()
        
        # Roteamento de Abertura de Escopo/Bloco de código local {}
        elif token.value == '{':
            return self.block_statement()
        else:
            self.report_error(f"Token inesperado fora de contexto: '{token.value}'", token)
            self.synchronize() 
            return None

    def block_statement(self):
        """Agrupa um conjunto de comandos delimitados pelas chaves '{' e '}'."""
        self.match("DELIMITADOR", "{")
        node = ASTNode("BLOCO")
        
        while (self.current_token() is not None and self.current_token().value != "}"):
            token_antes = self.current_idx # Guarda o estado do cursor
            
            stmt = self.statement()
            if stmt:
                node.add(stmt)
                
            # SE O CURSOR NÃO SE MOVEU (evita loop infinito dentro das chaves se o token for inválido)
            if token_antes == self.current_idx:
                self.advance()

        self.match("DELIMITADOR", "}")
        return node

    def declaration_or_assignment(self):
        """Trata a criação de variáveis, suportando declarações múltiplas e atribuições (ex: int p, o = 1, 2;)."""
        type_token = self.current_token()
        self.advance() # Consome o tipo (int, float, etc.)

        # 1. Coleta todos os identificadores separados por vírgula
        identifiers = []
        
        identifier = self.current_token()
        if self.match("IDENTIFICADOR"):
            identifiers.append(identifier.value)
        else:
            self.synchronize()
            return None

        while self.current_token() and self.current_token().value == ",":
            self.advance() # Consome a vírgula
            next_id = self.current_token()
            if self.match("IDENTIFICADOR"):
                identifiers.append(next_id.value)
            else:
                self.synchronize() 
                return None

        # Criamos o nó principal da declaração
        node = ASTNode("DECLARAÇÃO_MULTIPLA", type_token.value)
        
        # Criamos um sub-nó para listar as variáveis declaradas
        vars_node = ASTNode("VARIÁVEIS")
        for var in identifiers:
            vars_node.add(ASTNode("IDENTIFICADOR", var))
        node.add(vars_node)

        # 2. Verifica se há inicialização simultânea (ex: = 1, 2)
        next_token = self.current_token()
        if next_token and next_token.value == "=":
            self.advance() # Consome o '='
            
            expr_node = ASTNode("VALORES_INICIAIS")
            
            # Lê a primeira expressão
            first_expr = self.expression()
            if first_expr:
                expr_node.add(first_expr)
                
            # Lê as demais expressões separadas por vírgula
            while self.current_token() and self.current_token().value == ",":
                self.advance() # Consome a vírgula
                next_expr = self.expression()
                if next_expr:
                    expr_node.add(next_expr) 
            node.add(expr_node)

        if not self.match("DELIMITADOR", ";"):
            if self.current_token() and self.current_token().value not in ['}', 'else']:
                self.synchronize()
        return node

    def assignment_statement(self):
        """Processa comandos puramente de modificação de valor (ex: x = y + 2;)."""
        identifier = self.current_token()
        self.match("IDENTIFICADOR")
        self.match("OP_ATRIBUIÇÃO", "=")

        expr = self.expression()

        if not self.match("DELIMITADOR", ";"):
            if self.current_token() and self.current_token().value not in ['}', 'else']:
                self.synchronize()

        node = ASTNode("ATRIBUIÇÃO")
        node.add(ASTNode("IDENTIFICADOR", identifier.value))
        node.add(expr)
        return node

    def condition_statement(self):
        """Monta a estrutura ramificada do bloco 'if' e captura blocos 'else' adjacentes."""
        self.match("PALAVRA_RESERVADA", "if")
        node = ASTNode("CONDICIONAL", "if")

        if not self.match("DELIMITADOR", "("):
            self.synchronize()
            return None

        condition = self.expression()
        node.add(condition)

        if not self.match("DELIMITADOR", ")"):
            # O parêntese falhou. Forçamos uma sincronização agressiva para engolir
            # o bloco `{ ... }` ou o resto da linha desse if problemático.
            self.synchronize()
            
            # Se a sincronização nos deixou em um bloco fechando '}' ou em um 'else', 
            # nós o consumimos para evitar cascata no escopo global.
            if self.current_token() and self.current_token().value == '}':
                self.advance()
            if self.current_token() and self.current_token().value == 'else':
                self.advance()
                # Também limpa o corpo do else órfão
                self.synchronize()
                if self.current_token() and self.current_token().value == '}':
                    self.advance()
            return None

        body = self.statement()
        node.add(body)
        token = self.current_token()

        # Tratamento de caminho alternativo opcional (else)
        if (token and token.type == "PALAVRA_RESERVADA" and token.value == "else"):
            self.advance()
            elseNode = ASTNode("SENAO")
            elseBody = self.statement()
            
            if elseBody:
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

            if not self.match("DELIMITADOR", "("):
                self.synchronize()
                return None
            
            condition = self.expression()
            node.add(condition)
            
            if not self.match("DELIMITADOR", ")"):
                self.synchronize()
                if self.current_token() and self.current_token().value == '}':
                    self.advance()
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

            # Sub-etapa 1: Inicialização do laço
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
                if self.current_token() and self.current_token().value == '}':
                    self.advance()
                return None
            
            body = self.statement()
            if body:
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