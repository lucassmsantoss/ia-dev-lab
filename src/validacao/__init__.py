"""Validadores de documentos brasileiros."""

from src.validacao.cnpj import validar_cnpj
from src.validacao.cpf import validar_cpf

__all__ = ["validar_cpf", "validar_cnpj"]
