# type: ignore

from analisador_lexico.lexer import Scanner
from analisador_sintatico.parser import Parser

# --- CÓDIGO DE TESTE ---

codigo_teste = """
int x = 10;
float y = 3.14;
char c = 'a';

int p,o = 1,2;

x =  x  + 5;

if (x > 10){
    x = x * 2;
}else{
    x = x - 1;
}

while (x < 100){
    x = x + 10;
}

for (int i = 0; i < 5; i = i + 1){
    y = y + 1.5;
}

return x;
"""

print("========== Iniciando Compilação ==========")



# 1. ETAPA: ANALISADOR LÉXICO (SCANNER)
scanner = Scanner(codigo_teste)
tokens_validos = []

while True:
    token = scanner.next_token()
    if token is None: 
        break
    
    # Se o lexer encontrar um caractere inválido (ex: @, $, etc), ele gera um token do tipo "ERRO"
    if token.type != "ERRO":
        tokens_validos.append(token)


# Verifica se a lista de erros do scanner possui algum registro, só passa se não tiver erros
if len(scanner.errors) > 0:
    print("\n FALHA: Erro Léxico encontrado:")
    for error in scanner.errors:
        print(f"  - {error['message']} na linha {error['line']}, coluna {error['column']}")
    exit(1) 



# 2. ETAPA: ANALISADOR SINTÁTICO (PARSER)

print("\n SUCESSO: Análise Léxica concluída.")
parser = Parser(tokens_validos)

ast = parser.parse() #retona raiz da arvore sintática


# --- VALIDAÇÃO E EXIBIÇÃO DOS RESULTADOS ---
if len(parser.errors) == 0:
    print("\n SUCESSO: Análise Sintática concluída sem erros!")
    print("\n===== AST GERADA =====\n")
    print(ast)

else:
    print(f"\n FALHA: Foram encontrados {len(parser.errors)} erros sintáticos:")

    for erro in parser.errors:
        print(f"  - {erro}")