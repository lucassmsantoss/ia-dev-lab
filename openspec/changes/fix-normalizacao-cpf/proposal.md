# Proposta — Corrige a normalização de CPF

## Origem

Esta mudança não nasceu de uma ideia nova: é o item pendente deixado em
[`openspec/changes/add-validacao-cnpj/checkpoint-humano.md`](../add-validacao-cnpj/checkpoint-humano.md).
Durante a Etapa 3 daquela atividade, a revisão do diff encontrou dois defeitos em
`src/validacao/cpf.py` (documentados em
[`revisao-dos-diffs.md`](../add-validacao-cnpj/revisao-dos-diffs.md)), mas o checkpoint humano
definido para `src/validacao/` bloqueou a correção dentro daquela mudança porque ela não estava
no escopo declarado. A decisão foi corrigir depois, como mudança própria. Esta é essa mudança.

## User story

> Como consumidor de `validar_cpf`, preciso que a função rejeite qualquer entrada que não seja,
> ela mesma, um CPF bem formado — inclusive quando um CPF válido está embutido em texto maior,
> ou quando aparece um caractere que se parece com dígito mas não é — para que a validação não
> vire uma porta aberta para dados que não deveriam ser aceitos como documento.

## Contexto e motivação

`_somente_digitos` descartava qualquer caractere que não fosse dígito e validava o que sobrava.
Duas consequências, ambas verificadas na prática (ver `revisao-dos-diffs.md`):

1. **CPF válido cercado de lixo era aceito.** `"<script>52998224725</script>"`,
   `"CPF: 529.982.247-25"` e `"529.982.247-25!!!"` todos validavam como `True`, porque o que
   sobrava depois de descartar o não-dígito era um CPF correto.
2. **`str.isdigit()` aceita caracteres que não são `0-9`.** `"²2998224725"` fazia a função
   **levantar `ValueError`**, violando a regra do próprio `CLAUDE.md` ("nunca levanta
   exceção"). `"٥2998224725"` (dígito indo-arábico) validava como `True`.

Nenhum teste existente pegava isso: os testes de caractere inválido usavam entradas em que o
que sobra depois de descartar as letras já tem tamanho errado, então a rejeição acontecia por
acidente — pelo motivo errado.

## Escopo

- Trocar a normalização de "descarta tudo que não é dígito" para "remove apenas os
  caracteres de formatação (`.`, `-`, espaço) e valida o conjunto de caracteres do que
  sobrar", no mesmo padrão já usado em `src/validacao/cnpj.py`.
- Renomear `_somente_digitos` para `_normalizar`, para refletir o novo comportamento
  (a função não filtra mais só dígitos).
- Adicionar os casos de regressão como testes, escritos **antes** da implementação.

## Não-objetivos

- Não altera `_calcular_digito`, `validar_cpf` (assinatura e contrato de retorno) nem o
  comportamento para qualquer entrada que já era coberta pelos 38 testes existentes.
- Não mexe em `cnpj.py` nem em `lote.py`.
- Não introduz biblioteca externa.

## Impacto

`validar_cpf("<script>52998224725</script>")`, que hoje retorna `True`, passa a retornar
`False`. Isso é uma quebra de contrato do ponto de vista de quem já depende do comportamento
atual — é exatamente o risco que o checkpoint humano da mudança anterior identificou, e é por
isso que a correção está registrada como mudança própria, e não como um ajuste de três linhas
escondido em outro Pull Request.
