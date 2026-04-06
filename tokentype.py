from enum import Enum

#Dicionário com todos os tipos de tokens da linguagem
tokenType = {
    "KEYWORD": "PALAVRA_RESERVADA",
    "IDENTIFIER": "IDENTIFICADOR",

    "LITER_INT": "INTEIRO",
    "LITER_FLOAT": "FLOAT",
    "LITER_STRING": "STRING",
    "LITER_CHAR": "CHAR",

    "OP_ASSIGNMENT": "OP_ATRIBUIÇÃO",
    "OP_RELATIONAL": "OP_RELACIONAL",
    "OP_ARITHMETIC": "OP_ARITIMÉTICO",

    "DELIMITER": "DELIMITADOR",
    "ERROR": "ERRO",
}