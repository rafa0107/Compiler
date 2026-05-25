# type: ignore

class ASTNode:
    """
    Representa um nó na Árvore Sintática Abstrata (AST).
    Cada nó possui um tipo (ex: 'DECLARAÇÃO', 'OPERADOR'), um valor opcional
    e uma lista de nós filhos que determinam a hierarquia do código.
    """

    def __init__(self, node_type, value=None):
        # Define a categoria do nó (ex: BLOCO, CONDICIONAL, LITERAL)
        self.node_type = node_type
        # Armazena o valor textual do token correspondente (ex: "if", "x", "10")
        self.value = value
        # Lista encadeada que guarda os subcomponentes desta instrução
        self.children = []

    def add(self, child):
        """Adiciona um nó filho à lista de ramificações, ignorando retornos nulos."""
        if child:
            self.children.append(child)

    def __repr__(self, level=0):
        """Gera uma representação textual e indentada da árvore para depuração."""
        indent = "  " * level
        text = f"{indent}{self.node_type}"

        if self.value:
            text += f": {self.value}"
        text += "\n"
        
        # Percorre recursivamente os filhos incrementando o nível de recuo
        for child in self.children:
            text += child.__repr__(level + 1)

        return text