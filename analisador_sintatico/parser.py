# type: ignore

from .base_parser import BaseParser
from .expressions import ExpressionsParser
from .statements import StatementsParser

# Herança múltipla: Parser herda as propriedades base, as regras de expressões e as de statements.
class Parser(BaseParser, ExpressionsParser, StatementsParser):
    def __init__(self, tokens):
        # Inicializa o construtor da BaseParser para configurar os tokens e cursores
        super().__init__(tokens)

    def parse(self):
        """Ponto de entrada do Parser Geral"""
        while self.current_token() is not None:
            self.statement()
        return self.errors