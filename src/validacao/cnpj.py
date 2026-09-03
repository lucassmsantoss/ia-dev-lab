"""Validação de CNPJ (Cadastro Nacional da Pessoa Jurídica).

Aceita os dois formatos em circulação: o numérico, emitido até julho de 2026, e o
alfanumérico, emitido pela Receita Federal a partir de 31/07/2026. Ambos permanecem
válidos por prazo indeterminado.
"""

import sys

TAMANHO_CNPJ = 14
POSICOES_BASE = 12

DIGITOS = "0123456789"
LETRAS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
CARACTERES_VALIDOS = DIGITOS + LETRAS
CARACTERES_FORMATACAO = ".-/ "

# Pesos do cálculo módulo 11, transcritos da documentação da Receita Federal.
# Escritos literalmente, e não gerados por laço, por decisão registrada em design.md (D3).
PESOS_PRIMEIRO_DIGITO = (5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2)
PESOS_SEGUNDO_DIGITO = (6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2)


def _normalizar(valor: str) -> str:
    """Remove apenas os caracteres de formatação e converte letras para maiúsculas.

    Diferente de uma remoção genérica de "tudo que não é alfanumérico": qualquer caractere
    inesperado é preservado aqui, para que a checagem de conjunto o rejeite depois.
    """
    return "".join(c for c in valor if c not in CARACTERES_FORMATACAO).upper()


def _valor_caractere(caractere: str) -> int:
    """Converte um caractere no seu valor de cálculo: código ASCII menos 48.

    Dígitos mantêm o próprio valor ('0' vale 0, '9' vale 9) e letras seguem a partir daí
    ('A' vale 17, 'Z' vale 42), conforme a regra do CNPJ alfanumérico.
    """
    return ord(caractere) - 48


def _calcular_digito(base: str, pesos: tuple) -> int:
    """Calcula um dígito verificador pelo módulo 11 sobre `base`, usando `pesos`."""
    soma = sum(_valor_caractere(c) * p for c, p in zip(base, pesos))
    resto = soma % 11
    return 0 if resto < 2 else 11 - resto


def validar_cnpj(valor: str) -> bool:
    """Informa se `valor` é um CNPJ estruturalmente válido.

    Aceita os formatos numérico e alfanumérico, com ou sem máscara, em qualquer caixa.
    A validação é estrutural: confirma que o número é bem formado, não que a empresa
    exista ou esteja ativa. Qualquer entrada malformada resulta em False, nunca em exceção.
    """
    if not isinstance(valor, str):
        return False

    candidato = _normalizar(valor)

    if len(candidato) != TAMANHO_CNPJ:
        return False

    base = candidato[:POSICOES_BASE]
    digitos_verificadores = candidato[POSICOES_BASE:]

    if any(c not in CARACTERES_VALIDOS for c in base):
        return False

    if any(c not in DIGITOS for c in digitos_verificadores):
        return False

    if len(set(base)) == 1:
        return False

    primeiro = _calcular_digito(base, PESOS_PRIMEIRO_DIGITO)
    segundo = _calcular_digito(base + str(primeiro), PESOS_SEGUNDO_DIGITO)

    return digitos_verificadores == f"{primeiro}{segundo}"


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("uso: python -m src.validacao.cnpj <numero>")
        raise SystemExit(2)

    entrada = sys.argv[1]
    print(f"{entrada}: {'valido' if validar_cnpj(entrada) else 'invalido'}")
