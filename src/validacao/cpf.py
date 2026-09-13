"""Validação de CPF (Cadastro de Pessoas Físicas)."""

import sys

TAMANHO_CPF = 11


DIGITOS = "0123456789"
CARACTERES_FORMATACAO = ".- "


def _normalizar(valor: str) -> str:
    """Remove apenas os caracteres de formatação do CPF (`.`, `-` e espaço).

    Diferente de descartar "tudo que não é dígito": qualquer caractere inesperado que não
    seja formatação sobrevive aqui, para que a checagem de conjunto o rejeite depois. Ver
    `openspec/changes/fix-normalizacao-cpf/` — antes desta correção, a função descartava
    silenciosamente qualquer caractere não numérico, o que fazia `"<script>52998224725</script>"`
    validar como CPF correto.
    """
    return "".join(c for c in valor if c not in CARACTERES_FORMATACAO)


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

    candidato = _normalizar(valor)

    if len(candidato) != TAMANHO_CPF:
        return False

    if any(c not in DIGITOS for c in candidato):
        return False

    if len(set(candidato)) == 1:
        return False

    primeiro = _calcular_digito(candidato[:9])
    segundo = _calcular_digito(candidato[:10])

    return candidato[9] == str(primeiro) and candidato[10] == str(segundo)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("uso: python -m src.validacao.cpf <numero>")
        raise SystemExit(2)

    entrada = sys.argv[1]
    print(f"{entrada}: {'valido' if validar_cpf(entrada) else 'invalido'}")
