import re
from .token import Token
from .tokentype import tokenType


#Lista de regras do lexer usando regex
tokenSpecs = [
    # Ignorados
    (r'^\s+', None), # espaços em branco
    (r'^//.*', None), # comentários de linha
    (r'^/\*[\s\S]*?\*/', None), # comentários de bloco

    # Keywords / Identifiers
    (r'^\b(int|float|char|if|else|while|for|return|void)\b', tokenType["KEYWORD"]), #palavras reservadas da linguagem
    (r'^[a-zA-Z_][a-zA-Z0-9_]*', tokenType["IDENTIFIER"]), #nomes de variáveis, funções, etc.

    # Literais
    (r'^(0|[1-9]\d*)\.\d+', tokenType["LITER_FLOAT"]), #números de float
    (r'^(0|[1-9]\d*)', tokenType["LITER_INT"]), #números inteiros
    (r'^"(?:[^"\\]|\\.)*"', tokenType["LITER_STRING"]), #strings entre aspas duplas.
    (r"^'(?:[^\\']|\\.)'", tokenType["LITER_CHAR"]), #caracteres entre aspas simples.

    # Operadores
    (r'^(==|!=|<=|>=|<|>)', tokenType["OP_RELATIONAL"]), #relacionais (==, !=, <=, >=, <, >)
    (r'^=', tokenType["OP_ASSIGNMENT"]), #atribuição  (=)
    (r'^[+\-*/]', tokenType["OP_ARITHMETIC"]), #aritméticos (+ - * /)

    # Delimitadores
    (r'^[()\[\]{};,]', tokenType["DELIMITER"]), #delimitadores (parênteses, colchetes, chaves, vírgula, ponto e vírgula)
]

class Scanner:
    def __init__(self, input_text):
        self.input = input_text 
        self.cursor = 0 
        self.line = 1 
        self.column = 1 
        self.errors = [] 

    def next_token(self):
        # verifica se chegou ao fim do input
        if self.cursor >= len(self.input):
            return None

        # Ignora espaços e comentários
        while True:
            string = self.input[self.cursor:]
            matched = False

            # percorre apenas regras ignoradas (type_ == None)
            for regex, type_ in tokenSpecs:
                if type_ is not None:
                    continue

                match = re.match(regex, string)
                if match:
                    self.advance(match.group(0))
                    matched = True
                    break

            if not matched:
                break

        # fim da entrada após ignorar espaços/comentários
        if self.cursor >= len(self.input):
            return None

        # obtém o próximo lexema
        lexeme, line, column = self.get_next_lexeme()

        # tentar casar token válido
        for regex, type_ in tokenSpecs:
            if type_ is None:
                continue

            match = re.match(regex, lexeme)
            if match and match.group(0) == lexeme:
                return Token(type_, lexeme, line, column)

        # erro léxico: token inválido
        self.errors.append({
            "message": f"Invalid token '{lexeme}'",
            "line": line,
            "column": column
        })

        return Token(tokenType["ERROR"], lexeme, line, column)

    def get_next_lexeme(self):
        lexeme = ""
        start_line = self.line
        start_column = self.column

        while self.cursor < len(self.input):
            char = self.input[self.cursor]

            # parar em espaço ou delimitador
            if re.match(r'\s', char) or re.match(r'[()\[\]{};,]', char):
                break

            # trata operadores
            if re.match(r'[=\+\-\*/<>!]', char):
                if len(lexeme) == 0:
                    lexeme += char
                    self.advance(char)

                    # verifica se é operador duplo
                    if self.cursor < len(self.input):
                        next_char = self.input[self.cursor]
                        if next_char == "=":
                            lexeme += next_char
                            self.advance(next_char)

                    return lexeme, start_line, start_column

                break

            # acumulando caracteres para formar o lexema
            lexeme += char
            self.advance(char)

        # se não formou um lexema válido, tenta pegar o próximo caractere como token de erro
        if len(lexeme) == 0:
            lexeme = self.input[self.cursor]
            self.advance(lexeme)

        return lexeme, start_line, start_column
    
    # Avança o cursor e atualiza linha/coluna
    def advance(self, text):
        for char in text:
            if char == "\n":
                self.line += 1
                self.column = 1
            else:
                self.column += 1

        self.cursor += len(text)