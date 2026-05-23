#Representa um tipo de token
class Token:
    def __init__(self, type_, value, line, column):
        self.type = type_
        self.value = value
        self.line = line
        self.column = column

    def __repr__(self):
        # formato de exibição do token para depuração
        return f"Token {{ tipo: '{self.type}', valor: '{self.value}', linha: {self.line}, coluna: {self.column} }}"