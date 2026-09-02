# Tarefas — Validação de CNPJ

Plano revisado. O plano original proposto pelo agente, a crítica e a justificativa de cada
alteração estão em [`revisao-do-plano.md`](revisao-do-plano.md).

## 1. Confirmar a regra antes de escrever código

- [ ] 1.1 Conferir na documentação da Receita Federal o formato do CNPJ alfanumérico:
      quantas posições, quais aceitam letras, quais permanecem numéricas e a partir de quando
      vale.
- [ ] 1.2 Confirmar a regra de conversão de caractere (ASCII menos 48) e os dois vetores de
      pesos do cálculo módulo 11.
- [ ] 1.3 Reunir ao menos quatro CNPJs numéricos reais e conhecidos para servirem de âncora,
      e validar os pesos contra eles antes de qualquer implementação.

## 2. Implementar a validação

- [ ] 2.1 Criar `src/validacao/cnpj.py` com `validar_cnpj(valor: str) -> bool`, a normalização
      da entrada e o cálculo do dígito verificador em função auxiliar isolada, seguindo a
      ordem de checagem definida em `design.md` (D4).
- [ ] 2.2 Criar `tests/test_cnpj.py` cobrindo os cenários da especificação: formato numérico,
      formato alfanumérico, máscara, caixa minúscula, dígito verificador incorreto, letra em
      posição de dígito verificador, sequência repetida, entrada nula, tipo incorreto,
      tamanho incorreto e caractere fora de `0-9A-Z`.
- [ ] 2.3 Incluir o caso de borda do CNPJ `00000000000191` e um teste que fixa os dois vetores
      de pesos, conforme a mitigação registrada em `design.md` (D3).
- [ ] 2.4 Rodar `python -m pytest tests/test_cnpj.py -v` e obter suíte verde.

## 3. Expor o módulo no domínio

- [ ] 3.1 Exportar `validar_cnpj` em `src/validacao/__init__.py`, ao lado de `validar_cpf`.
- [ ] 3.2 Atualizar `src/validacao/CLAUDE.md` para refletir que a normalização passou a incluir
      conversão de caixa, e que a regra de sequência repetida é avaliada sobre as posições
      anteriores aos dígitos verificadores.

## 4. Verificar que nada quebrou

- [ ] 4.1 Rodar `python -m pytest -q` — a suíte completa, incluindo os 38 casos de CPF que
      existiam antes desta mudança.
- [ ] 4.2 Revisar o `git diff` de cada arquivo antes de aceitar, e registrar ao menos um
      achado da revisão.

## 5. Documentar

- [ ] 5.1 Atualizar o `README.md`: estrutura de pastas, tabela de comandos e a menção ao
      suporte aos dois formatos de CNPJ.
- [ ] 5.2 Commitar em passos separados, um por bloco de tarefas, e não em um único commit.
