"""Testes da validação de CNPJ.

Os casos seguem os cenários de openspec/changes/add-validacao-cnpj/specs/validacao-cnpj/spec.md.
Os CNPJs numéricos usados como âncora são inscrições reais e conhecidas, não valores gerados.
"""

import pytest

from src.validacao.cnpj import (
    PESOS_PRIMEIRO_DIGITO,
    PESOS_SEGUNDO_DIGITO,
    _calcular_digito,
    _normalizar,
    _valor_caractere,
    validar_cnpj,
)

CNPJS_NUMERICOS_VALIDOS = [
    "11222333000181",
    "11444777000161",
    "34028316000103",  # Empresa Brasileira de Correios e Telégrafos
    "00000000000191",  # Banco do Brasil
]

CNPJS_ALFANUMERICOS_VALIDOS = [
    "12ABC34501DE35",
    "ABCDEFGH000195",
    "A1B2C3D4000193",
    "1A2B3C4D000179",
]


# Requisito: validação no formato numérico

@pytest.mark.parametrize("cnpj", CNPJS_NUMERICOS_VALIDOS)
def test_aceita_cnpj_numerico_valido(cnpj):
    assert validar_cnpj(cnpj) is True


@pytest.mark.parametrize("cnpj", ["11222333000182", "11444777000162", "34028316000104"])
def test_rejeita_digito_verificador_incorreto(cnpj):
    assert validar_cnpj(cnpj) is False


# Requisito: validação no formato alfanumérico

@pytest.mark.parametrize("cnpj", CNPJS_ALFANUMERICOS_VALIDOS)
def test_aceita_cnpj_alfanumerico_valido(cnpj):
    """Formato emitido pela Receita Federal a partir de 31/07/2026."""
    assert validar_cnpj(cnpj) is True


def test_aceita_cnpj_alfanumerico_com_mascara():
    assert validar_cnpj("12.ABC.345/01DE-35") is True


@pytest.mark.parametrize("cnpj", ["12ABC34501DE3X", "12ABC34501DEA5", "12ABC34501DEXX"])
def test_rejeita_letra_em_posicao_de_digito_verificador(cnpj):
    """As posições 13 e 14 permanecem numéricas mesmo no formato alfanumérico."""
    assert validar_cnpj(cnpj) is False


# Requisito: tolerância a máscara, espaços e caixa

@pytest.mark.parametrize("cnpj", [
    "11.222.333/0001-81",
    " 11 222 333 0001 81 ",
    "11222333/000181",
    "11-222-333-0001-81",
])
def test_mascara_e_espacos_nao_alteram_o_resultado(cnpj):
    assert validar_cnpj(cnpj) == validar_cnpj("11222333000181")


@pytest.mark.parametrize("cnpj", ["12abc34501de35", "12AbC34501dE35", "ab.cde.fgh/0001-95"])
def test_aceita_letras_minusculas(cnpj):
    """A caixa não faz parte da identidade do documento."""
    assert validar_cnpj(cnpj) is True


# Requisito: rejeição de sequências de caracteres idênticos

@pytest.mark.parametrize("cnpj", ["11111111111180", "00000000000000", "AAAAAAAAAAAA45"])
def test_rejeita_sequencia_de_caracteres_identicos(cnpj):
    """Sequências repetidas podem satisfazer o módulo 11, mas não são inscrições reais.

    Os três valores têm dígito verificador ARITMETICAMENTE CORRETO — foram calculados, não
    inventados. Sem isso o teste passaria pelo motivo errado, rejeitando por DV inválido em
    vez de pela regra de sequência repetida. Ver o achado 3 em revisao-dos-diffs.md.
    """
    assert validar_cnpj(cnpj) is False


def test_aceita_cnpj_legitimo_com_muitos_zeros():
    """Caso de borda: 00.000.000/0001-91 é a inscrição real do Banco do Brasil.

    A regra de sequência repetida exige que as 12 primeiras posições sejam TODAS iguais.
    Em "000000000001" há um "1", portanto a regra não se aplica.
    """
    assert validar_cnpj("00000000000191") is True
    assert validar_cnpj("00.000.000/0001-91") is True


# Requisito: ausência de exceções para entrada malformada

@pytest.mark.parametrize("valor", [None, 11222333000181, 3.14, [], {}, True, b"11222333000181"])
def test_rejeita_entrada_que_nao_e_texto(valor):
    assert validar_cnpj(valor) is False


@pytest.mark.parametrize("cnpj", ["", "   ", "1122233300018", "112223330001812", "..//--"])
def test_rejeita_tamanho_incorreto(cnpj):
    assert validar_cnpj(cnpj) is False


@pytest.mark.parametrize("cnpj", [
    "12ABÇ34501DE35",
    "12AB@34501DE35",
    "11222333000181abc",
    "CNPJ: 11.222.333/0001-81",
    "<script>11222333000181</script>",
])
def test_rejeita_caractere_fora_do_conjunto_permitido(cnpj):
    """Caractere inesperado é rejeitado, nunca descartado silenciosamente."""
    assert validar_cnpj(cnpj) is False


@pytest.mark.parametrize("cnpj", ["²1222333000181", "1122233300018²", "١١٢٢٢٣٣٣٠٠٠١٨١"])
def test_rejeita_digitos_unicode_nao_ascii(cnpj):
    """Caracteres com isdigit() verdadeiro fora de 0-9 ASCII não são aceitos.

    Ver o achado 2 registrado em revisao-dos-diffs.md.
    """
    assert validar_cnpj(cnpj) is False


# Funções auxiliares

def test_normalizar_remove_apenas_formatacao_e_aplica_caixa_alta():
    assert _normalizar("12.abc.345/01de-35") == "12ABC34501DE35"
    assert _normalizar(" 11 222 333 0001 81 ") == "11222333000181"
    assert _normalizar("11@222333000181") == "11@222333000181"


def test_valor_caractere_segue_a_regra_ascii_menos_48():
    assert _valor_caractere("0") == 0
    assert _valor_caractere("9") == 9
    assert _valor_caractere("A") == 17
    assert _valor_caractere("Z") == 42


def test_pesos_estao_conforme_a_documentacao_da_receita():
    """Fixa os vetores de pesos. Ver design.md (D3): gerá-los por laço já produziu erro."""
    assert PESOS_PRIMEIRO_DIGITO == (5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2)
    assert PESOS_SEGUNDO_DIGITO == (6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2)


def test_calcular_digito_reproduz_verificadores_conhecidos():
    assert _calcular_digito("112223330001", PESOS_PRIMEIRO_DIGITO) == 8
    assert _calcular_digito("1122233300018", PESOS_SEGUNDO_DIGITO) == 1
    assert _calcular_digito("12ABC34501DE", PESOS_PRIMEIRO_DIGITO) == 3
    assert _calcular_digito("12ABC34501DE3", PESOS_SEGUNDO_DIGITO) == 5
