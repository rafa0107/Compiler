from analisador_lexico.lexer import Scanner
from analisador_sintatico.parser import Parser

# --- CÓDIGO DE TESTE COM ERRO LÉXICO ---
codigo_teste = """
int x = 10;
float y = 3.14;
char c = 'a';
"""

print("========== Iniciando Compilação ==========")

# 1. ANALISADOR LÉXICO
scanner = Scanner(codigo_teste)
tokens_validos = []

while True:
    token = scanner.next_token()
    if token is None:
        break
    
    # Se o lexer encontrar um token inválido, ele gera um tipo "ERRO"
    if token.type != "ERRO":
        tokens_validos.append(token)

# BARREIRA DE ERRO: Verifica se o Lexer encontrou problemas
if len(scanner.errors) > 0:
    print("\n[FALHA] Erro Léxico encontrado:")
    for error in scanner.errors:
        print(f"  - {error['message']} na linha {error['line']}, coluna {error['column']}")
    
    # Crucial: encerra a execução do script aqui para NÃO ir para o sintático
    exit(1) 


# 2. ANALISADOR SINTÁTICO
# Esse bloco SÓ será executado se o código passar 100% no Lexer
print("\n[SUCESSO] Análise Léxica concluída.")

parser = Parser(tokens_validos)
erros_sintaticos = parser.parse()

if len(erros_sintaticos) == 0:
    print("[SUCESSO] Análise Sintática concluída sem erros! Código válido.")
else:
    print(f"\n[FALHA] Foram encontrados {len(erros_sintaticos)} Erros Sintáticos:")
    for erro in erros_sintaticos:
        print(f"  - {erro}")