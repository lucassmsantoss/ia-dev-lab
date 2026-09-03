"""Validação em lote de documentos a partir de um arquivo CSV.

Lê um CSV, valida o documento presente em uma coluna e devolve um relatório com o total
processado, os válidos e as falhas. O tipo do documento é inferido do próprio conteúdo.

Especificação: docs/spec-lote-csv.md
"""

import csv
import io
import sys
from typing import List, NamedTuple, Optional

from src.validacao.cnpj import validar_cnpj
from src.validacao.cpf import validar_cpf

TAMANHO_CPF = 11
TAMANHO_CNPJ = 14
CARACTERES_FORMATACAO = ".-/ "

SEPARADORES_SUPORTADOS = (";", ",")

CODIGO_SUCESSO = 0
CODIGO_DOCUMENTOS_INVALIDOS = 1
CODIGO_ERRO_DE_EXECUCAO = 2


class ColunaInexistenteError(Exception):
    """A coluna pedida não existe no arquivo.

    É erro de execução, não resultado de validação: nenhum documento chegou a ser avaliado.
    """

    def __init__(self, coluna: str, disponiveis: List[str]):
        self.coluna = coluna
        self.disponiveis = disponiveis
        super().__init__(
            f"coluna {coluna!r} nao encontrada. Colunas disponiveis: "
            + ", ".join(repr(c) for c in disponiveis)
        )


class Falha(NamedTuple):
    """Uma linha que não passou na validação."""

    linha: int
    valor: str
    motivo: str


class ResultadoLote(NamedTuple):
    """Relatório da validação de um arquivo."""

    total: int
    validos: int
    falhas: List[Falha]

    @property
    def houve_falha(self) -> bool:
        return len(self.falhas) > 0


def _detectar_separador(cabecalho: str) -> str:
    """Escolhe o separador pelo que aparece mais na linha de cabeçalho.

    Preferido a csv.Sniffer, que falha silenciosamente em arquivos de coluna única.
    """
    contagens = {sep: cabecalho.count(sep) for sep in SEPARADORES_SUPORTADOS}
    separador = max(contagens, key=contagens.get)
    return separador if contagens[separador] > 0 else ","


def _limpar(valor: str) -> str:
    """Remove apenas os caracteres de formatação, preservando qualquer outro."""
    return "".join(c for c in valor if c not in CARACTERES_FORMATACAO)


def validar_documento(valor: str) -> bool:
    """Valida um documento inferindo o tipo pelo comprimento útil."""
    tamanho = len(_limpar(valor))
    if tamanho == TAMANHO_CPF:
        return validar_cpf(valor)
    if tamanho == TAMANHO_CNPJ:
        return validar_cnpj(valor)
    return False


def _motivo_da_falha(valor: str) -> str:
    if not valor.strip():
        return "campo vazio"
    tamanho = len(_limpar(valor))
    if tamanho not in (TAMANHO_CPF, TAMANHO_CNPJ):
        return f"tamanho inesperado ({tamanho} caracteres uteis)"
    return "documento invalido"


def validar_linhas(conteudo: str, coluna: str = "documento") -> ResultadoLote:
    """Valida os documentos de um CSV já lido como texto.

    Separada de `validar_arquivo` para ser testável sem tocar no disco.
    """
    primeira_linha = conteudo.splitlines()[0] if conteudo.strip() else ""
    leitor = csv.DictReader(
        io.StringIO(conteudo), delimiter=_detectar_separador(primeira_linha)
    )

    colunas = leitor.fieldnames or []
    if coluna not in colunas:
        raise ColunaInexistenteError(coluna, colunas)

    total = 0
    validos = 0
    falhas: List[Falha] = []

    # enumerate começa em 2: a linha 1 do arquivo é o cabeçalho.
    for numero_da_linha, registro in enumerate(leitor, start=2):
        total += 1
        valor = (registro.get(coluna) or "").strip()

        if validar_documento(valor):
            validos += 1
        else:
            falhas.append(Falha(numero_da_linha, valor, _motivo_da_falha(valor)))

    return ResultadoLote(total=total, validos=validos, falhas=falhas)


def validar_arquivo(caminho: str, coluna: str = "documento") -> ResultadoLote:
    """Valida os documentos de um arquivo CSV.

    Abre com utf-8-sig para descartar o BOM que o Excel no Windows escreve no início do
    arquivo. Sem isso, o nome da primeira coluna chegaria com o BOM colado.
    """
    with open(caminho, "r", encoding="utf-8-sig", newline="") as arquivo:
        return validar_linhas(arquivo.read(), coluna)


def _formatar(resultado: ResultadoLote) -> str:
    linhas = [
        f"Processados: {resultado.total}",
        f"Validos:     {resultado.validos}",
        f"Invalidos:   {len(resultado.falhas)}",
    ]
    if resultado.falhas:
        linhas.append("")
        linhas.append("Linha  Valor                     Motivo")
        for falha in resultado.falhas:
            linhas.append(f"{falha.linha:<7}{falha.valor[:25]:<26}{falha.motivo}")
    return "\n".join(linhas)


def main(argumentos: Optional[List[str]] = None) -> int:
    """Interface de linha de comando.

    Códigos de saída, conforme o contrato aprovado no checkpoint humano:
      0 - todos os documentos são válidos (ou não há linhas de dados)
      1 - o arquivo foi lido, mas há documentos inválidos
      2 - não foi possível executar (arquivo ausente, coluna inexistente)
    """
    argumentos = list(sys.argv[1:] if argumentos is None else argumentos)

    if not argumentos:
        print("uso: python -m src.validacao.lote <arquivo.csv> [coluna]", file=sys.stderr)
        return CODIGO_ERRO_DE_EXECUCAO

    caminho = argumentos[0]
    coluna = argumentos[1] if len(argumentos) > 1 else "documento"

    try:
        resultado = validar_arquivo(caminho, coluna)
    except FileNotFoundError:
        print(f"arquivo nao encontrado: {caminho}", file=sys.stderr)
        return CODIGO_ERRO_DE_EXECUCAO
    except ColunaInexistenteError as erro:
        print(str(erro), file=sys.stderr)
        return CODIGO_ERRO_DE_EXECUCAO

    print(_formatar(resultado))
    return CODIGO_DOCUMENTOS_INVALIDOS if resultado.houve_falha else CODIGO_SUCESSO


if __name__ == "__main__":
    raise SystemExit(main())
