# Especificação — Validação em lote a partir de arquivo CSV

**Abordagem:** Markdown manual, sem ferramenta de SDD.
**Motivo da escolha:** ver [`comparacao-abordagens-sdd.md`](comparacao-abordagens-sdd.md).
**Data:** 02/09/2026.

Este documento cobre, em um único arquivo, o que o OpenSpec distribuiu em quatro artefatos —
`proposal.md`, `specs/validacao-cnpj/spec.md`, `design.md` e `tasks.md` — mais três documentos
de revisão.

---

## 1. User story

> Como pessoa responsável por uma base cadastral, preciso conferir de uma vez só todos os
> documentos de uma planilha e receber um relatório dizendo quantos passaram, quantos falharam
> e o porquê de cada falha, para que eu possa corrigir os registros errados sem abrir a
> planilha linha por linha.

Sem decisão técnica: não diz formato de arquivo, nome de função, estrutura de retorno nem se
há interface de linha de comando.

## 2. Requisitos (PRD)

| # | Requisito |
|---|---|
| R1 | O sistema lê um arquivo CSV e valida o documento presente em uma coluna indicada |
| R2 | O tipo do documento é inferido do próprio conteúdo: 11 caracteres úteis indicam CPF, 14 indicam CNPJ |
| R3 | O processamento nunca é interrompido por uma linha ruim — cada problema vira uma entrada no relatório |
| R4 | O relatório informa o total processado, o total de válidos e a lista de falhas com número da linha, valor e motivo |
| R5 | O sistema aceita arquivos gerados pelo Excel no Windows: com BOM, com separador `;` e com codificação UTF-8 |
| R6 | O sistema é utilizável como biblioteca, sem imprimir nada, e como comando de terminal, com saída legível |
| R7 | O comando de terminal distingue, pelo código de saída, "havia documentos inválidos" de "não consegui executar" |
| R8 | Nenhuma dependência de terceiros |

## 3. Critérios de aceite

### CA1 — Planilha com CPF e CNPJ misturados

- **GIVEN** um CSV com a coluna `documento` contendo `529.982.247-25` (CPF válido),
  `11.222.333/0001-81` (CNPJ válido) e `12ABC34501DE35` (CNPJ alfanumérico válido)
- **WHEN** o arquivo é validado
- **THEN** o total processado é 3, o total de válidos é 3 e a lista de falhas está vazia
- **AND** o tipo de cada documento foi inferido do comprimento, sem configuração

### CA2 — Linha inválida não interrompe o processamento

- **GIVEN** um CSV com as colunas `nome,documento` e quatro registros, sendo o segundo
  `52998224724` (dígito verificador errado) e o quarto com o campo `documento` em branco
- **WHEN** o arquivo é validado
- **THEN** o total processado é 4, o total de válidos é 2
- **AND** o relatório aponta a linha 3 do arquivo com o motivo `documento invalido` e a linha 5
  com o motivo `campo vazio`
- **AND** nenhuma exceção é levantada

### CA2b — Linha em branco não é um registro

- **GIVEN** um CSV que contém uma linha inteiramente vazia entre dois registros válidos
- **WHEN** o arquivo é validado
- **THEN** o total processado é 2, e a linha em branco não aparece no relatório de falhas

> Este critério foi **acrescentado durante a implementação**, não na especificação original.
> A primeira versão do CA2 usava uma linha inteiramente vazia como exemplo de "campo vazio",
> e o teste falhou: o módulo `csv` da biblioteca padrão descarta linhas em branco antes de
> entregá-las ao consumidor, de modo que elas nunca chegam a ser um registro. O comportamento
> do Python está certo — uma linha vazia não é um registro com campo vazio, é ausência de
> registro — e a especificação é que estava imprecisa. Ver a análise em
> [`comparacao-abordagens-sdd.md`](comparacao-abordagens-sdd.md).

### CA3 — Arquivo do Excel com BOM e separador ponto e vírgula — caso de borda próprio

- **GIVEN** um CSV salvo pelo Excel no Windows, começando com os bytes `EF BB BF` e usando `;`
  como separador
- **WHEN** o arquivo é validado indicando a coluna `documento`
- **THEN** a coluna é encontrada e as linhas são processadas normalmente
- **AND** o nome da coluna não é lido como `﻿documento`

> Este é o caso de borda que motiva a especificação. Sem tratá-lo, o `csv.DictReader` lê o
> nome da primeira coluna com o BOM colado, a busca por `documento` falha, e o erro que chega
> ao usuário é "coluna não encontrada" — apontando para o lugar errado. É um problema que já
> ocorreu neste mesmo projeto, ao gravar o `.mcp.json` com `Set-Content -Encoding UTF8`.

### CA4 — Coluna inexistente é erro de execução, não de dados

- **GIVEN** um CSV cujas colunas são `nome` e `cpf`
- **WHEN** o arquivo é validado indicando a coluna `documento`
- **THEN** o sistema informa que a coluna não existe e lista as colunas disponíveis
- **AND** o código de saída do comando é `2`, distinto do código `1` usado para
  "há documentos inválidos"

### CA5 — Arquivo sem linhas de dados

- **GIVEN** um CSV contendo apenas o cabeçalho
- **WHEN** o arquivo é validado
- **THEN** o total processado é 0, o total de válidos é 0, a lista de falhas está vazia
- **AND** o código de saída é `0`, porque ausência de dados não é falha de validação

## 4. Decisões técnicas

**D1 — Abertura com `encoding="utf-8-sig"`.** Descarta o BOM se houver, e é inofensivo se não
houver. A alternativa — remover o BOM manualmente do nome da primeira coluna — funcionaria,
mas espalha o conhecimento sobre o problema por dentro do código de negócio.

**D2 — Separador detectado por contagem no cabeçalho, não por `csv.Sniffer`.** O `Sniffer`
falha de forma silenciosa em arquivos de uma coluna só, e o universo aqui é pequeno: `,` ou
`;`. Contar qual dos dois aparece mais na primeira linha é mais previsível do que uma
heurística genérica que erra sem avisar.

**D3 — Tipo de documento inferido por comprimento, não por coluna de configuração.** Onze
caracteres úteis só podem ser CPF; catorze, só CNPJ. Pedir ao usuário que declare o tipo
adicionaria configuração para resolver um problema que os próprios dados já resolvem.
Comprimentos fora desses dois viram falha com motivo `tamanho inesperado`.

**D4 — Retorno é um objeto de dados, e a impressão vive só na camada de linha de comando.**
Atende ao R6 sem duplicar lógica: quem usa como biblioteca recebe o objeto; a interface de
terminal formata o mesmo objeto.

**D5 — Três códigos de saída: `0`, `1` e `2`.** Esta decisão passou pelo checkpoint humano.
O plano inicial usava `1` tanto para "há documentos inválidos" quanto para "arquivo não
encontrado", o que torna impossível a um script distinguir "a base tem erros, me avise" de
"o processo quebrou, pare a esteira". Separar os dois é o que torna o comando encadeável.

**D6 — Linha em branco é ausência de registro, não registro vazio.** Decorre do comportamento
do módulo `csv`, e foi mantida em vez de contornada: reconstruir as linhas em branco exigiria
abandonar o `DictReader` e reimplementar o parsing, para representar no relatório algo que o
usuário não considera um dado.

## 5. Plano de tarefas

### Plano inicial proposto pelo agente

```
1. Criar src/validacao/lote.py
2. Implementar a leitura do CSV
3. Implementar a validação de cada linha
4. Implementar o relatório
5. Adicionar interface de linha de comando
6. Escrever os testes
7. Atualizar o README
```

### Crítica e alterações

O plano tem o mesmo vício do anterior — testes no fim, tarefas de implementação fatiadas por
camada técnica — e mais dois problemas próprios.

**Não há tarefa para os arquivos de teste.** Todos os critérios de aceite dependem de arquivos
CSV com características específicas: com BOM, com `;`, com coluna faltando, sem linhas. Sem uma
tarefa que os construa, os testes acabariam validando um CSV genérico e limpo — exatamente o
arquivo que nunca dá problema.

**A tarefa 5 esconde a decisão dos códigos de saída.** "Adicionar interface de linha de
comando" é uma tarefa que parece mecânica e contém a única decisão irreversível da mudança:
o contrato de códigos de saída, do qual scripts de terceiros passam a depender.

**Plano revisado:**

- [ ] **1.1** Escrever os arquivos CSV de teste primeiro, um por critério de aceite: caso feliz
      com tipos misturados, caso com linha inválida e linha vazia, arquivo do Excel com BOM e
      `;`, arquivo sem a coluna pedida, arquivo só com cabeçalho.
- [ ] **2.1** Implementar a leitura tolerante: `utf-8-sig`, detecção de separador, e erro claro
      quando a coluna não existe.
- [ ] **2.2** Testar a leitura contra os cinco arquivos, antes de existir qualquer validação.
- [ ] **3.1** Implementar a inferência de tipo por comprimento e a validação de cada linha,
      acumulando falhas em vez de interromper.
- [ ] **3.2** Testar os critérios CA1, CA2 e CA5.
- [ ] **4.1** Implementar o objeto de resultado com total, válidos e lista de falhas.
- [ ] **5.1** **CHECKPOINT HUMANO** — definir o contrato de códigos de saída antes de escrever
      a interface de linha de comando. Contrato aprovado: `0` sem falhas, `1` com documentos
      inválidos, `2` erro de execução.
- [ ] **5.2** Implementar a interface de terminal consumindo o objeto de resultado, sem
      duplicar lógica de validação.
- [ ] **5.3** Testar o CA4, incluindo o código de saída.
- [ ] **6.1** Rodar a suíte completa: os 88 testes existentes precisam continuar verdes.
- [ ] **6.2** Atualizar o README e commitar em passos separados.
