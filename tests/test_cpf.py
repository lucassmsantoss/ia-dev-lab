"""Testes da validação de CPF."""

import pytest

from src.validacao.cpf import _calcular_digito, _somente_digitos, validar_cpf

CPFS_VALIDOS_SEM_MASCARA = ["52998224725", "11144477735", "39053344705"]
CPFS_VALIDOS_COM_MASCARA = ["529.982.247-25", "111.444.777-35", "390.533.447-05"]


@pytest.mark.parametrize("cpf", CPFS_VALIDOS_SEM_MASCARA)
def test_aceita_cpf_valido_sem_mascara(cpf):
    assert validar_cpf(cpf) is True


@pytest.mark.parametrize("cpf", CPFS_VALIDOS_COM_MASCARA)
def test_aceita_cpf_valido_com_mascara(cpf):
    assert validar_cpf(cpf) is True


def test_mascara_nao_altera_o_resultado():
    assert validar_cpf("529.982.247-25") == validar_cpf("52998224725")


@pytest.mark.parametrize("cpf", ["52998224724", "52998224715", "11144477731"])
def test_rejeita_digito_verificador_errado(cpf):
    assert validar_cpf(cpf) is False


@pytest.mark.parametrize("cpf", [
    "00000000000", "11111111111", "22222222222", "33333333333", "44444444444",
    "55555555555", "66666666666", "77777777777", "88888888888", "99999999999",
])
def test_rejeita_sequencia_de_digitos_repetidos(cpf):
    """Sequências repetidas passam no cálculo do dígito, mas não são CPFs válidos."""
    assert validar_cpf(cpf) is False


def test_rejeita_sequencia_repetida_com_mascara():
    assert validar_cpf("111.111.111-11") is False


@pytest.mark.parametrize("cpf", ["", "   ", "5299822472", "529982247251", "..."])
def test_rejeita_entrada_com_tamanho_invalido(cpf):
    assert validar_cpf(cpf) is False


@pytest.mark.parametrize("valor", [None, 52998224725, 3.14, [], {}, True])
def test_rejeita_entrada_que_nao_e_string(valor):
    """A função nunca levanta exceção: entrada malformada é resultado False."""
    assert validar_cpf(valor) is False


@pytest.mark.parametrize("cpf", ["abcdefghijk", "529.982.247-2a", "CPF invalido"])
def test_rejeita_entrada_com_caracteres_nao_numericos(cpf):
    assert validar_cpf(cpf) is False


@pytest.mark.parametrize("cpf", [
    "<script>52998224725</script>",
    "529.982.247-25!!!",
    "CPF: 529.982.247-25",
])
def test_rejeita_cpf_valido_cercado_de_lixo(cpf):
    """Regressão do Achado 1 de revisao-dos-diffs.md.

    A normalização antiga (`_somente_digitos`) descartava qualquer caractere que não fosse
    dígito, então um CPF válido embutido em texto arbitrário passava. A normalização atual
    remove só `.`, `-` e espaço; qualquer outro caractere sobrevive para ser rejeitado pela
    checagem de conjunto.
    """
    assert validar_cpf(cpf) is False


@pytest.mark.parametrize("cpf", ["²2998224725", "٥2998224725"])
def test_rejeita_digito_nao_ascii_sem_lancar_excecao(cpf):
    """Regressão do Achado 2 de revisao-dos-diffs.md.

    `str.isdigit()` é verdadeiro para caracteres que não pertencem a `0-9` (expoentes como
    "²", dígitos indo-arábicos como "٥"). Um deles fazia `_calcular_digito` levantar
    `ValueError` ao chamar `int()`; o outro era aceito como válido silenciosamente. A checagem
    de conjunto atual (`c not in DIGITOS`) compara contra `"0123456789"` explicitamente, então
    nenhum dos dois chega ao cálculo do dígito verificador.
    """
    assert validar_cpf(cpf) is False


def test_somente_digitos_remove_a_mascara():
    assert _somente_digitos("529.982.247-25") == "52998224725"
    assert _somente_digitos(" 529 982 247 25 ") == "52998224725"
    assert _somente_digitos("sem numero") == ""


def test_calcular_digito_reproduz_os_verificadores_conhecidos():
    assert _calcular_digito("529982247") == 2
    assert _calcular_digito("5299822472") == 5


def test_calcular_digito_retorna_zero_quando_o_resto_e_menor_que_dois():
    assert _calcular_digito("111444777") == 3
    assert _calcular_digito("390533447") == 0
