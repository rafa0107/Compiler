# type: ignore

class ASTNode:
    """
    Representa um nó na Árvore Sintática Abstrata (AST).
    Cada nó possui um tipo (ex: 'DECLARAÇÃO', 'OPERADOR'), um valor opcional
    e uma lista de nós filhos que determinam a hierarquia do código.
    """

    def __init__(self, node_type, value=None):
        self.node_type = node_type
        self.value = value
        self.children = []

    def add(self, child):
        """Adiciona um nó filho à lista de ramificações."""
        if child:
            self.children.append(child)

    def __repr__(self, level=0):
        """Para Garantir uma representação textual no terminal."""
        indent = "  " * level
        text = f"{indent}{self.node_type}"

        if self.value:
            text += f": {self.value}"
        text += "\n"
        
        for child in self.children:
            text += child.__repr__(level + 1)

        return text