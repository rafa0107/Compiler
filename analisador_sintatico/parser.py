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
    Ponto de inicio do Parser na análise sintática.
    """

    def __init__(self, tokens):
        super().__init__(tokens)

    def parse(self):
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