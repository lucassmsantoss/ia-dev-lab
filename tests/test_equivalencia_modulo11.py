"""Testa que as duas cópias duplicadas da regra de ajuste do módulo 11 concordam.

Contexto: `docs/etapa6-divida-tecnica.md`. `_ajustar_resto_modulo11` existe, de propósito,
duplicada em `src/validacao/cpf.py` e `src/validacao/cnpj.py` — a decisão registrada no ADR
0002 foi manter a duplicação (extrair um módulo compartilhado exigiria uma pasta por tipo
técnico, que `CLAUDE.md` proíbe) e, em vez disso, garantir por teste que as duas cópias nunca
divergem silenciosamente. Se alguém corrigir uma cópia e esquecer a outra, este teste fica
vermelho.
"""

from src.validacao.cnpj import _ajustar_resto_modulo11 as ajustar_cnpj
from src.validacao.cpf import _ajustar_resto_modulo11 as ajustar_cpf


def test_as_duas_copias_concordam_para_todo_resto_possivel():
    # resto de uma divisão por 11 está sempre entre 0 e 10.
    for resto in range(11):
        assert ajustar_cpf(resto) == ajustar_cnpj(resto), (
            f"cpf.py e cnpj.py divergem para resto={resto}: "
            f"{ajustar_cpf(resto)} != {ajustar_cnpj(resto)}"
        )


def test_regra_e_zero_abaixo_de_dois_e_complemento_dali_em_diante():
    assert ajustar_cpf(0) == 0 and ajustar_cnpj(0) == 0
    assert ajustar_cpf(1) == 0 and ajustar_cnpj(1) == 0
    assert ajustar_cpf(2) == 9 and ajustar_cnpj(2) == 9
    assert ajustar_cpf(10) == 1 and ajustar_cnpj(10) == 1
