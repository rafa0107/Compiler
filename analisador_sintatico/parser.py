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
        # Inicializa o estado compartilhado da classe base passando os tokens lexados
        super().__init__(tokens)

    def parse(self):
        """
        Ponto de partida do processo de análise sintática (Parsing).
        Cria a raiz máxima do programa e lê em loop todas as instruções adjacentes.
        """
        root = ASTNode("PROGRAMA")

        # Varre sequencialmente todo o fluxo de tokens até o esgotamento do arquivo
        while self.current_token() is not None:
            stmt = self.statement()
            if stmt:
                root.add(stmt)

        # Retorna o topo da Árvore Sintática Abstrata (AST) completamente montada
        return root