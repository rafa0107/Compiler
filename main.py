# type: ignore

# Importa o Scanner (Analisador Léxico) e o Parser (Analisador Sintático) dos respectivos pacotes
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

# Instancia o Scanner passando o código bruto. Ele varrerá o texto caractere por caractere.
scanner = Scanner(codigo_teste)
tokens_validos = []

# Laço para extrair sequencialmente todos os tokens do código fonte
while True:
    token = scanner.next_token()
    if token is None:  # Se retornar None, é (EOF)
        break
    
    # Se o lexer encontrar um caractere inválido (ex: @, $, etc), ele gera um token do tipo "ERRO"
    if token.type != "ERRO":
        tokens_validos.append(token)

# --- BARREIRA DE ERRO LÉXICO ---
# Verifica se a lista de erros do scanner possui algum registro.
if len(scanner.errors) > 0:
    print("\n FALHA: Erro Léxico encontrado:")
    # Percorre e exibe os detalhes de cada caractere com erro encontrado e sua respectiva posição
    for error in scanner.errors:
        print(f"  - {error['message']} na linha {error['line']}, coluna {error['column']}")
    
    # Interrompe a execução do compilador imediatamente.
    # Se tiver erros, nem chama o sintático.
    exit(1) 



# 2. ETAPA: ANALISADOR SINTÁTICO (PARSER)

# Esse bloco SÓ será executado se o código passar 100% sem erros no scanner
print("\n SUCESSO: Análise Léxica concluída.")

# Instancia o Parser, passando lista de tokens válidos filtrada anteriormente
parser = Parser(tokens_validos)

# Chama o método principal do Parser, que inicia o processo de descida recursiva (parsing).
# Ele agrupa os tokens em regras gramaticais e retorna a raiz da Árvore Sintática Abstrata (AST).
ast = parser.parse()


# --- VALIDAÇÃO E EXIBIÇÃO DOS RESULTADOS ---
# Verifica se o parser conseguiu processar toda a estrutura gramatical sem violar nenhuma regra da linguagem
if len(parser.errors) == 0:
    print("\n SUCESSO: Análise Sintática concluída sem erros!")
    print("\n===== AST GERADA =====\n")
    # Imprime a árvore na tela. Como sobrescrevemos o método __repr__ em ASTNode,
    # ela será exibida com recuos (indentações) que mostram visualmente a hierarquia do programa.
    print(ast)

else:
    # Se a gramática estiver errada (ex: faltar parênteses, ponto e vírgula, chaves descasadas), entra aqui
    print(f"\n FALHA: Foram encontrados {len(parser.errors)} erros sintáticos:")

    # Lista todos os erros de sintaxe capturados pelo mecanismo de recuperação em modo pânico do parser
    for erro in parser.errors:
        print(f"  - {erro}")