# type: ignore

from .base_parser import BaseParser
from .expressions import ExpressionsParser
from .statements import StatementsParser
from .ast import ASTNode

class Parser(
    BaseParser,
    ExpressionsParser,
    StatementsParser
):
    """
    Orquestrador Central do Compilador (Parser).
    Utiliza herança múltipla para unificar os submódulos de infraestrutura,
    expressões e instruções em uma única máquina de análise sintática.
    """

    def __init__(self, tokens):
        super().__init__(tokens)

    def parse(self):
        """Ponto de partida do processo de análise sintática."""
        root = ASTNode("PROGRAMA")

        while self.current_token() is not None:
            token_antes = self.current_idx

            stmt = self.statement()
            if stmt:
                root.add(stmt)
            else:
                if token_antes == self.current_idx:
                    self.advance()
                    
        return root