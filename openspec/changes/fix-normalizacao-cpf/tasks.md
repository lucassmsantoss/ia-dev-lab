# Plano de tarefas — fix-normalizacao-cpf

Conduzido em Red-Green-Refactor real, com o skill `superpowers:test-driven-development`
(ver `docs/etapa2-tdd.md` para o relato completo da investigação da ferramenta).

- [x] **Red** — Escrever os testes de regressão em `tests/test_cpf.py`
      (`test_rejeita_cpf_valido_cercado_de_lixo`,
      `test_rejeita_digito_nao_ascii_sem_lancar_excecao`) reproduzindo exatamente os casos de
      `revisao-dos-diffs.md`, e confirmar que falham contra o código atual.
- [x] **Green** — Reescrever `_somente_digitos` como `_normalizar` em `src/validacao/cpf.py`,
      no padrão de `cnpj.py`: remove só formatação, valida conjunto de caracteres. Confirmar
      que os novos testes passam e que a suíte completa de CPF continua verde (38 casos).
- [x] **Refactor** — Renomear o teste da função interna
      (`test_somente_digitos_remove_a_mascara` → `test_normalizar_remove_apenas_formatacao`) e
      atualizar sua asserção para o novo comportamento ("sem numero" deixa de virar `""` e passa
      a preservar as letras, já que só formatação é removida).
- [x] Atualizar o encaminhamento em
      `openspec/changes/add-validacao-cnpj/checkpoint-humano.md` marcando os dois itens
      pendentes como concluídos.
