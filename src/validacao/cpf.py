"""Validação de CPF (Cadastro de Pessoas Físicas)."""

import sys
from typing import Optional

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


def _ajustar_resto_modulo11(resto: int) -> int:
    """Aplica a regra do dígito verificador módulo 11: 0 se o resto < 2, senão 11 - resto.

    Duplicada, de propósito, em `cnpj.py` — ver `docs/etapa6-divida-tecnica.md` para a análise
    de por que a duplicação foi mantida em vez de extraída para um módulo compartilhado, e
    `tests/test_equivalencia_modulo11.py` para o teste que garante que as duas cópias
    continuam concordando.
    """
    return 0 if resto < 2 else 11 - resto


def _calcular_digito(digitos: str) -> int:
    """Calcula um dígito verificador de CPF a partir dos dígitos anteriores.

    Recebe 9 dígitos para calcular o primeiro verificador ou 10 para o segundo.
    """
    peso_inicial = len(digitos) + 1
    soma = sum(int(digito) * (peso_inicial - posicao)
               for posicao, digito in enumerate(digitos))
    resto = soma % TAMANHO_CPF
    return _ajustar_resto_modulo11(resto)


def validar_cpf(valor: str) -> bool:
    """Informa se `valor` é um CPF válido.

    Aceita o número com ou sem máscara. Qualquer entrada malformada — nula, vazia,
    com tamanho incorreto, com caractere fora do conjunto `0-9` ou com todos os dígitos
    iguais — resulta em False, nunca em exceção.
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


def mascarar_cpf(cpf: str) -> Optional[str]:
    """Formata um CPF válido no padrão XXX.XXX.XXX-XX; devolve None se `cpf` não for válido.

    Exige um CPF válido (com ou sem máscara) em vez de apenas fatiar a string: a primeira
    versão desta função fatiava a entrada sem checar nada antes, e produzia máscara para
    entrada vazia, para CPF inválido e lançava `TypeError` para `None`. Ver
    `docs/etapa2-tdd.md`, seção "Tarefa sem TDD", para o registro desses achados.
    """
    if not validar_cpf(cpf):
        return None
    digitos = _normalizar(cpf)
    return f"{digitos[:3]}.{digitos[3:6]}.{digitos[6:9]}-{digitos[9:]}"


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("uso: python -m src.validacao.cpf <numero>")
        raise SystemExit(2)

    entrada = sys.argv[1]
    print(f"{entrada}: {'valido' if validar_cpf(entrada) else 'invalido'}")
