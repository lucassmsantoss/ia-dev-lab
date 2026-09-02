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
