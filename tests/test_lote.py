"""Testes da validação em lote a partir de CSV.

Os casos seguem os critérios de aceite de docs/spec-lote-csv.md.
"""

import pytest

from src.validacao.lote import (
    CODIGO_DOCUMENTOS_INVALIDOS,
    CODIGO_ERRO_DE_EXECUCAO,
    CODIGO_SUCESSO,
    ColunaInexistenteError,
    _detectar_separador,
    main,
    validar_arquivo,
    validar_documento,
    validar_linhas,
)

CPF_VALIDO = "529.982.247-25"
CNPJ_VALIDO = "11.222.333/0001-81"
CNPJ_ALFANUMERICO_VALIDO = "12ABC34501DE35"


def escrever(tmp_path, nome, conteudo, encoding="utf-8"):
    """Grava um CSV de teste preservando as quebras de linha exatamente como escritas.

    Usa `open(..., newline="")` em vez de `Path.write_text(..., newline="")`: o parâmetro
    `newline` só existe em `write_text` a partir do Python 3.10, e o ambiente de referência
    deste projeto é o 3.9.12, conforme declarado em CLAUDE.md.
    """
    caminho = tmp_path / nome
    with open(str(caminho), "w", encoding=encoding, newline="") as arquivo:
        arquivo.write(conteudo)
    return str(caminho)


# CA1 — planilha com CPF e CNPJ misturados

def test_ca1_valida_tipos_misturados_inferindo_pelo_conteudo(tmp_path):
    conteudo = (
        "nome,documento\n"
        f"Pessoa Fisica,{CPF_VALIDO}\n"
        f"Empresa Antiga,{CNPJ_VALIDO}\n"
        f"Empresa Nova,{CNPJ_ALFANUMERICO_VALIDO}\n"
    )
    resultado = validar_arquivo(escrever(tmp_path, "misto.csv", conteudo))

    assert resultado.total == 3
    assert resultado.validos == 3
    assert resultado.falhas == []
    assert resultado.houve_falha is False


@pytest.mark.parametrize("documento,esperado", [
    (CPF_VALIDO, True),
    ("52998224725", True),
    (CNPJ_VALIDO, True),
    (CNPJ_ALFANUMERICO_VALIDO, True),
    ("52998224724", False),
    ("11222333000182", False),
    ("123", False),
    ("", False),
])
def test_infere_o_tipo_pelo_comprimento_util(documento, esperado):
    assert validar_documento(documento) is esperado


# CA2 — linha inválida não interrompe o processamento

def test_ca2_acumula_falhas_sem_interromper(tmp_path):
    conteudo = (
        "nome,documento\n"
        f"Ana,{CPF_VALIDO}\n"
        "Bruno,52998224724\n"
        f"Carlos,{CNPJ_VALIDO}\n"
        "Diana,\n"
    )
    resultado = validar_arquivo(escrever(tmp_path, "com_falhas.csv", conteudo))

    assert resultado.total == 4
    assert resultado.validos == 2
    assert len(resultado.falhas) == 2

    invalido, vazio = resultado.falhas
    assert (invalido.linha, invalido.motivo) == (3, "documento invalido")
    assert (vazio.linha, vazio.motivo) == (5, "campo vazio")


def test_ca2b_linha_em_branco_nao_e_um_registro(tmp_path):
    """O módulo csv descarta linhas em branco antes de entregá-las ao consumidor.

    A especificação original tratava linha em branco como registro de campo vazio; o teste
    mostrou que ela nem chega a existir. Ver docs/spec-lote-csv.md, CA2b e D6.
    """
    conteudo = f"documento\n{CPF_VALIDO}\n\n{CNPJ_VALIDO}\n"
    resultado = validar_arquivo(escrever(tmp_path, "com_branco.csv", conteudo))

    assert resultado.total == 2
    assert resultado.validos == 2
    assert resultado.falhas == []


def test_registra_motivo_de_tamanho_inesperado(tmp_path):
    conteudo = "documento\n123456\n"
    resultado = validar_arquivo(escrever(tmp_path, "curto.csv", conteudo))

    assert resultado.falhas[0].motivo == "tamanho inesperado (6 caracteres uteis)"


# CA3 — arquivo do Excel com BOM e ponto e vírgula (caso de borda próprio)

def test_ca3_le_arquivo_do_excel_com_bom_e_ponto_e_virgula(tmp_path):
    conteudo = (
        "nome;documento\n"
        f"Pessoa Fisica;{CPF_VALIDO}\n"
        f"Empresa;{CNPJ_VALIDO}\n"
    )
    caminho = escrever(tmp_path, "excel.csv", conteudo, encoding="utf-8-sig")
    resultado = validar_arquivo(caminho)

    assert resultado.total == 2
    assert resultado.validos == 2


def test_bom_nao_contamina_o_nome_da_primeira_coluna(tmp_path):
    """Sem utf-8-sig, a primeira coluna seria lida como '\\ufeffdocumento'."""
    caminho = escrever(tmp_path, "bom.csv", f"documento\n{CPF_VALIDO}\n", encoding="utf-8-sig")

    resultado = validar_arquivo(caminho, coluna="documento")

    assert resultado.validos == 1


@pytest.mark.parametrize("cabecalho,esperado", [
    ("nome,documento", ","),
    ("nome;documento", ";"),
    ("documento", ","),
    ("a;b;c,d", ";"),
])
def test_detecta_o_separador_pelo_cabecalho(cabecalho, esperado):
    assert _detectar_separador(cabecalho) == esperado


# CA4 — coluna inexistente é erro de execução

def test_ca4_coluna_inexistente_levanta_erro_com_as_colunas_disponiveis(tmp_path):
    caminho = escrever(tmp_path, "sem_coluna.csv", f"nome,cpf\nFulano,{CPF_VALIDO}\n")

    with pytest.raises(ColunaInexistenteError) as excecao:
        validar_arquivo(caminho, coluna="documento")

    assert excecao.value.disponiveis == ["nome", "cpf"]
    assert "documento" in str(excecao.value)
    assert "cpf" in str(excecao.value)


# CA5 — arquivo sem linhas de dados

def test_ca5_arquivo_apenas_com_cabecalho(tmp_path):
    resultado = validar_arquivo(escrever(tmp_path, "vazio.csv", "documento\n"))

    assert (resultado.total, resultado.validos, resultado.falhas) == (0, 0, [])
    assert resultado.houve_falha is False


# Interface de linha de comando e códigos de saída

def test_codigo_de_saida_zero_quando_tudo_valido(tmp_path, capsys):
    caminho = escrever(tmp_path, "ok.csv", f"documento\n{CPF_VALIDO}\n{CNPJ_VALIDO}\n")

    assert main([caminho]) == CODIGO_SUCESSO
    assert "Validos:     2" in capsys.readouterr().out


def test_codigo_de_saida_um_quando_ha_documento_invalido(tmp_path, capsys):
    caminho = escrever(tmp_path, "ruim.csv", f"documento\n{CPF_VALIDO}\n52998224724\n")

    assert main([caminho]) == CODIGO_DOCUMENTOS_INVALIDOS
    assert "documento invalido" in capsys.readouterr().out


def test_codigo_de_saida_dois_quando_arquivo_nao_existe(tmp_path, capsys):
    assert main([str(tmp_path / "nao_existe.csv")]) == CODIGO_ERRO_DE_EXECUCAO
    assert "arquivo nao encontrado" in capsys.readouterr().err


def test_codigo_de_saida_dois_quando_coluna_nao_existe(tmp_path, capsys):
    caminho = escrever(tmp_path, "sem.csv", f"nome,cpf\nFulano,{CPF_VALIDO}\n")

    assert main([caminho, "documento"]) == CODIGO_ERRO_DE_EXECUCAO
    assert "nao encontrada" in capsys.readouterr().err


def test_codigo_de_saida_dois_sem_argumentos(capsys):
    assert main([]) == CODIGO_ERRO_DE_EXECUCAO
    assert "uso:" in capsys.readouterr().err


def test_arquivo_vazio_nao_e_falha_de_validacao(tmp_path):
    """Ausência de dados sai com 0, não com 1: não houve documento inválido."""
    assert main([escrever(tmp_path, "so_cabecalho.csv", "documento\n")]) == CODIGO_SUCESSO


def test_aceita_coluna_com_nome_diferente(tmp_path):
    caminho = escrever(tmp_path, "outra.csv", f"inscricao\n{CNPJ_VALIDO}\n")

    assert validar_arquivo(caminho, coluna="inscricao").validos == 1


# validar_linhas trabalha sem tocar no disco

def test_validar_linhas_opera_sobre_texto():
    resultado = validar_linhas(f"documento\n{CPF_VALIDO}\n52998224724\n")

    assert (resultado.total, resultado.validos) == (2, 1)
