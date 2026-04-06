from lexer import Scanner

# código de teste
codigo_valido = """int x = 10;
float y = 3.14;
char c = 'a';

if (x > 5) {
    x = x + 1;
}"""

codigo_erro = """int 123abc = 10;
float y = 3.14.15;"""

scanner = Scanner(codigo_valido)

while True:
    token = scanner.next_token()
    if token is None:
        break
    print(token)

print("\nErros encontrados:")
if len(scanner.errors) == 0:
    print("Nenhum erro encontrado.")
else:
    for error in scanner.errors:
        print(f"{error['message']} at line {error['line']}, column {error['column']}")