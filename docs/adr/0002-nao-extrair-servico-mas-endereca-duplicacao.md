# ADR 0002 — Não extrair serviço; endereçar a duplicação do dígito verificador com teste de equivalência

- **Status:** Aceito
- **Data:** 2026-09-13
- **Autor:** Lucas Santos
- **Decisores:** Lucas Santos

## Contexto

A Etapa 4 da atividade de Harness e Arquitetura pediu um resumo da arquitetura atual do
`ia-dev-lab` e uma decisão justificada: o projeto deveria ser mais modular, extrair um serviço,
ou está no tamanho certo? O resumo completo está em `docs/etapa4-arquitetura.md`. Em paralelo,
a investigação de dívida técnica da Etapa 6 (`ruff --select ALL`, ver
`docs/etapa6-divida-tecnica.md`) encontrou um sinal concreto: `_calcular_digito` de `cpf.py` e
de `cnpj.py` implementam a mesma regra de arredondamento do módulo 11 de forma duplicada, sem
nenhum teste que garanta que as duas cópias concordam.

As duas perguntas são relacionadas — "o projeto precisa de mais estrutura?" e "o que fazer com
esta duplicação específica?" — mas pedem decisões diferentes: uma é sobre a forma geral do
projeto, a outra é sobre um trecho de código específico.

## Decisão

**Não modularizar mais o projeto nem extrair um serviço.** O projeto está no tamanho certo para
o que ele é: três módulos, um ponto de dependência único e unidirecional (`lote.py` → 
validadores), sem fronteira de implantação que justifique um serviço separado.

**A duplicação do cálculo de dígito verificador é mantida — não extraída para um módulo
compartilhado — e o risco que ela cria é coberto por um teste de equivalência**
(`tests/test_equivalencia_modulo11.py`), que roda as duas implementações
(`cpf._ajustar_resto_modulo11` e `cnpj._ajustar_resto_modulo11`) contra toda a faixa possível de
resto (0 a 10) e falha se divergirem.

## Justificativa

**Por que não extrair serviço:** não há processo, deploy ou consumidor externo a proteger — o
projeto roda inteiro em um processo Python, chamado como biblioteca ou CLI. Extrair um serviço
sem essa fronteira adicionaria uma camada de rede ou de processo sem nenhum problema real que
ela resolva.

**Por que não extrair um módulo compartilhado para a duplicação:** a opção mais óbvia
tecnicamente — criar `src/validacao/_comum.py` — esbarra em uma convenção que o projeto já
adotou deliberadamente: `CLAUDE.md` proíbe pastas por tipo técnico (`utils/`, `helpers/`,
`common/`), porque o critério de organização do projeto é domínio, não tipo de código. Um
módulo cuja única razão de existir é "código compartilhado por outros módulos" é,
funcionalmente, um `utils.py` — trocar o nome não muda o papel que ele exerceria.

**Por que teste de equivalência, e não aceitar o risco:** o teste custa poucas linhas e resolve
o problema real da duplicação, que não é "ter a mesma lógica duas vezes" (isso, sozinho, é só
repetição), e sim "poder divergir sem que nada avise". Depois desta mudança, se as duas cópias
divergirem, um teste fica vermelho — o mesmo padrão de proteção que o projeto já usa para
qualquer outra regra de negócio.

## Alternativas consideradas

- **Importar a função de um módulo no outro** (ex.: `cnpj.py` importa a função de `cpf.py`).
  Descartada: criaria uma dependência entre dois módulos que hoje são folhas independentes na
  árvore de dependências (ver `docs/etapa4-arquitetura.md`), só para uma função de poucas
  linhas — o acoplamento novo custaria mais do que a duplicação que resolve.
- **Ignorar o achado do `ruff`.** Descartada: o teste de equivalência custa muito pouco
  (dez linhas) para o risco que elimina, e o achado já estava documentado — deixá-lo sem
  resposta depois de identificado é pior do que não tê-lo notado.
- **Extrair mesmo assim, aceitando a exceção à convenção de pastas.** Descartada nesta
  atividade porque o ganho (uma função a menos duplicada) não paga o custo de abrir uma exceção
  em uma convenção que existe há três atividades sem exceção — se a duplicação crescer para uma
  terceira ou quarta ocorrência, essa conta muda, e vale reabrir esta decisão.

## Consequências

**Positivas**

- O risco real da duplicação (divergência silenciosa) fica coberto por teste, sem abrir exceção
  na convenção de organização por domínio.
- A decisão de não extrair serviço evita complexidade de infraestrutura sem benefício
  correspondente, mantendo o projeto fácil de rodar (`python -m pytest`, sem containers, sem
  configuração de rede).

**Negativas e riscos**

- A duplicação continua existindo como texto — qualquer pessoa lendo só `cpf.py` não sabe, sem
  seguir a referência no docstring, que `cnpj.py` tem a mesma regra. O teste de equivalência
  mitiga a consequência (divergência), não a causa (duplicação).
- Se um terceiro documento validado por módulo 11 for adicionado ao projeto (ver `titulo_eleitor.py`
  mencionado como próximo passo no `README.md`), a duplicação vira tripla, e o teste de
  equivalência precisa crescer para cobrir as três — o momento certo para revisitar esta
  decisão é exatamente esse.
