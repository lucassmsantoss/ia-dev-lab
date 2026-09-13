# Etapa 3 — Checkpoint humano

Este projeto já tem um checkpoint humano definido, de uma atividade anterior — ver
`openspec/changes/add-validacao-cnpj/checkpoint-humano.md`. Em vez de duplicar a definição, este
documento registra o mesmo checkpoint disparando de novo, em uma situação nova e real dentro
desta atividade — que é o que a Etapa 3 pede: não um checkpoint hipotético, um que parou a
execução de verdade.

## O checkpoint (já definido)

> Nenhuma alteração no comportamento de um módulo de domínio já consumido e coberto por testes
> verdes pode ser aplicada dentro de uma mudança cujo escopo não a declarou. A execução para, e
> a decisão é humana.

## O disparo — situação real desta atividade

Durante a implementação de `fix-normalizacao-cpf` (Etapa 2, `docs/etapa2-tdd.md`), com
`cpf.py` já aberto e a correção da normalização aplicada e verde, apareceu uma segunda
oportunidade óbvia: a Etapa 6 desta atividade ia investigar dívida técnica com `ruff`, e uma
leitura rápida de `cnpj.py` ao lado mostrava que `_calcular_digito` de `cpf.py` e o cálculo
equivalente em `cnpj.py` implementam a mesma regra (`0 se resto < 2, senão N - resto`) de forma
duplicada. Com os dois arquivos já abertos e o padrão já identificado, extrair um helper
compartilhado ali mesmo custaria poucos minutos a mais.

A proposta de `fix-normalizacao-cpf` declara em "Não-objetivos": *"Não altera `_calcular_digito`
[...] nem o comportamento para qualquer entrada que já era coberta pelos 38 testes
existentes."* Extrair a duplicação é uma mudança estrutural em código de domínio consumido —
exatamente o que o checkpoint cobre, mesmo sendo um refactor "seguro" (mesmo comportamento, só
reorganizado).

## A decisão tomada

**Rejeitar o bundling. Manter a extração fora desta mudança, como candidata a mitigação na
Etapa 6.**

Motivos:

- O mesmo raciocínio do checkpoint original de `add-validacao-cnpj` se aplica sem alteração: um
  Pull Request chamado "corrige normalização de CPF" que também mexe em `cnpj.py` sem isso
  estar na proposta é escopo que ninguém revisou de propósito.
- A duplicação **é** o achado de dívida técnica que a Etapa 6 pede para investigar com uma
  ferramenta de análise estática — resolvê-la de passagem, aqui, apagaria o próprio objeto da
  investigação antes de ela existir por escrito.
- Diferente da correção do CPF (que tinha uma proposta pronta esperando desde a atividade
  anterior), a extração do helper compartilhado não tem, ainda, uma decisão registrada sobre
  **onde** ele deveria morar — `CLAUDE.md` proíbe pastas por tipo técnico (`utils/`), o que
  torna essa decisão menos óbvia do que parece à primeira vista, e merece a análise que está em
  `docs/etapa6-divida-tecnica.md`, não uma decisão de corredor.

## O papel humano assumido

De novo, não foi o de escrever o código — a extração é mecânica e o agente teria feito em
minutos. Foi o de **notar a oportunidade e recusá-la mesmo sendo conveniente**, porque
"já que estou aqui" é exatamente o tipo de raciocínio que o checkpoint existe para interromper.
A pressão para aceitar era genuína: o defeito estava visível, a correção era óbvia, e adiar
pareceu, por um instante, desperdício. Foi esse instante que o checkpoint pausou.
