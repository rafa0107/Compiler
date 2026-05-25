# type: ignore

class SyntaxError:
    """Estrutura de um erro sintático capturado durante o parsing."""
    def __init__(self, message, line, column):
        self.message = message
        self.line = line
        self.column = column

    def __repr__(self):
        return f"Erro Sintático: {self.message} na linha {self.line}, coluna {self.column}"


class BaseParser:
    """
    Classe base responsável pelo gerenciamento de ponteiros de tokens,
    verificação de padrões de correspondência (match) e recuperação de erros.
    """
    def __init__(self, tokens):
        self.tokens = tokens       # Lista de tokens gerada pelo Analisador Léxico
        self.current_idx = 0       # Cursor que indica o token atual em análise
        self.errors = []           # Lista acumuladora de erros encontrados

    def current_token(self):
        """Retorna o token sob o cursor ou None se atingir o Fim do Arquivo (EOF)."""
        if self.current_idx < len(self.tokens):
            return self.tokens[self.current_idx]
        return None

    def advance(self):
        """Avança o cursor para o próximo token da lista e o retorna."""
        if self.current_idx < len(self.tokens):
            self.current_idx += 1
        return self.current_token()

    def match(self, expected_type, expected_value=None):
        """
        Valida se o token atual condiz com o tipo e valor esperados pela gramática.
        Se sim, avança o ponteiro. Caso contrário, reporta uma falha sintática.
        """
        token = self.current_token()
        if token is None:
            self.report_error(f"Esperado '{expected_value if expected_value else expected_type}', mas o arquivo terminou.")
            return False

        if token.type == expected_type:
            if expected_value is None or token.value == expected_value:
                self.advance()
                return True
        # Verifica se o token recebido do léxico é o mesmo do esperado de acordo com a gramática. Se não for, reporta o erro.
        expected = expected_value if expected_value else expected_type
        self.report_error(f"Esperado '{expected}', mas encontrou '{token.value}'", token)
        return False

    def report_error(self, message, token=None):
        """Registra o erro com localização exata e aciona o modo de pânico (sincronização)."""
        if token:
            err = SyntaxError(message, token.line, token.column)
        else: # Para quando o token é None, indicando (EOF) ou quando a lista de tokens está vazia. Nesse caso, tenta usar o último token para obter a linha e coluna, ou define como 1 se não houver tokens.
            current = self.current_token()
            last_token = current if current else (self.tokens[-1] if self.tokens else None)
            line = last_token.line if last_token else 1
            column = last_token.column if last_token else 1
            err = SyntaxError(message, line, column)
        
        self.errors.append(err)
        self.synchronize()

    def synchronize(self):
        """
        Aplica a estratégia de 'recuperação em modo pânico'. Descarta tokens problemáticos 
        até encontrar um ponto de sincronização seguro (; ou palavras-chave de escopo),
        evitando o travamento do parser e cascatas de falsos erros.
        """
        while self.current_token() is not None:
            token = self.current_token()

            # Evita consumir delimitações que fecham blocos sintáticos superiores
            if token.value in ['}', ')']:
                return

            # Se encontrar o fim da instrução, consome o ';' e encerra a recuperação
            if token.value == ';':
                self.advance()
                return

            # Se encontrar o início evidente de uma nova estrutura, interrompe o descarte
            if (
                token.type == "PALAVRA_RESERVADA"
                and token.value in ['int', 'float', 'char', 'if', 'while', 'for', 'return']
            ):
                return

            self.advance()