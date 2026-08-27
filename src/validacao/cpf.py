"""Validação de CPF (Cadastro de Pessoas Físicas)."""

import sys

TAMANHO_CPF = 11


def _somente_digitos(valor: str) -> str:
    """Remove qualquer caractere que não seja dígito, preservando a ordem."""
    return "".join(caractere for caractere in valor if caractere.isdigit())


def _calcular_digito(digitos: str) -> int:
    """Calcula um dígito verificador de CPF a partir dos dígitos anteriores.

    Recebe 9 dígitos para calcular o primeiro verificador ou 10 para o segundo.
    """
    peso_inicial = len(digitos) + 1
    soma = sum(int(digito) * (peso_inicial - posicao)
               for posicao, digito in enumerate(digitos))
    resto = soma % TAMANHO_CPF
    return 0 if resto < 2 else TAMANHO_CPF - resto


def validar_cpf(valor: str) -> bool:
    """Informa se `valor` é um CPF válido.

    Aceita o número com ou sem máscara. Qualquer entrada malformada — nula, vazia,
    com tamanho incorreto, sem dígitos suficientes ou com todos os dígitos iguais —
    resulta em False, nunca em exceção.
    """
    if not isinstance(valor, str):
        return False

    digitos = _somente_digitos(valor)

    if len(digitos) != TAMANHO_CPF:
        return False

    if len(set(digitos)) == 1:
        return False

    primeiro = _calcular_digito(digitos[:9])
    segundo = _calcular_digito(digitos[:10])

    return digitos[9] == str(primeiro) and digitos[10] == str(segundo)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("uso: python -m src.validacao.cpf <numero>")
        raise SystemExit(2)

    entrada = sys.argv[1]
    print(f"{entrada}: {'valido' if validar_cpf(entrada) else 'invalido'}")
