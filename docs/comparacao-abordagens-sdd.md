# Comparação entre abordagens de Spec-Driven Development

Registro da Etapa 5: o mesmo processo de SDD foi percorrido duas vezes, com ferramentas
diferentes, sobre funcionalidades diferentes do mesmo projeto.

| | Funcionalidade 1 | Funcionalidade 2 |
| --- | --- | --- |
| **O quê** | Validação de CNPJ, incluindo o formato alfanumérico | Validação em lote a partir de CSV |
| **Abordagem** | OpenSpec 1.11.0 (`@fission-ai/openspec`) | Markdown manual, sem ferramenta |
| **Onde** | `openspec/changes/add-validacao-cnpj/` | `docs/spec-lote-csv.md` |
| **Artefatos** | 7 arquivos | 1 arquivo |
| **Implementação** | `src/validacao/cnpj.py` | `src/validacao/lote.py` |
| **Testes** | 50 casos | 28 casos |

## Artefatos gerados

**OpenSpec** impôs uma decomposição. O comando `openspec init` criou a estrutura
`openspec/`, um `config.yaml` com pontos de extensão para contexto e regras por artefato, e
seis skills e comandos em `.claude/`. O `openspec new change` criou a pasta da mudança com
metadados. A partir daí, o schema `spec-driven` define quais artefatos existem e em que ordem
se constroem: **proposal** estabelece intenção e escopo, **specs** detalham o comportamento em
deltas, **design** registra a decisão técnica, **tasks** vira a lista executável.

**Markdown manual** produziu um documento só, com as mesmas seções em sequência: user story,
tabela de requisitos, critérios de aceite, decisões técnicas, plano de tarefas.

## Pontos positivos e negativos de cada uma

### OpenSpec

**A favor.** A separação em arquivos distintos criou atrito produtivo. Ter um `proposal.md`
com seção de não-objetivos, separado do plano, foi o que permitiu **comparar o plano contra a
proposta** e detectar duas tarefas fora de escopo — formatar com máscara e gerar CNPJs de
teste. Num documento único, essas tarefas teriam sido escritas duas telas abaixo dos
não-objetivos, e a comparação nunca teria acontecido.

O `config.yaml` foi mais útil do que eu esperava. Ele guarda contexto do projeto e regras por
artefato, e a regra *"tarefas de teste não ficam no fim do plano"* virou um critério objetivo
para criticar o plano proposto, em vez de uma preferência minha discutível na hora.

O formato de delta (`## ADDED Requirements`) força a declarar o que muda em relação ao que já
existe, e não apenas o que passa a existir. Foi isso que produziu o requisito de preservação do
comportamento do CPF.

**Contra.** O custo fixo é alto para o tamanho da mudança. Sete arquivos para uma função de
validação é desproporcional, e boa parte do valor vem da *disciplina*, não da ferramenta — as
mesmas seções em um arquivo teriam quase o mesmo efeito, com uma exceção importante, discutida
abaixo. A ferramenta também exige Node instalado e ocupa um diretório na raiz do projeto, o
que é um preço real em um repositório pequeno.

### Markdown manual

**A favor.** Custo zero de instalação e de navegação. Escrever tudo em um arquivo é mais
rápido e o documento se lê de ponta a ponta, o que ajuda quem chega depois. Para uma
funcionalidade com um punhado de requisitos, o resultado é honestamente comparável.

**Contra.** Nada obriga a nada. A ordem canônica do SDD — comportamento antes de requisito,
requisito antes de critério, critério antes de plano — só existe porque eu a segui. Percebi
duas vezes que estava começando a escrever decisão técnica dentro da user story, e nada me
avisou; no OpenSpec, a decisão técnica tem um arquivo com nome próprio, e escrever no lugar
errado é visível.

O ponto mais concreto: **não há seção de não-objetivos separada**. Na spec manual eu incluí as
decisões e os critérios, mas nenhum limite explícito de escopo — e não é coincidência que o
plano manual não tenha gerado nenhuma tarefa fora de escopo para eu remover. Não porque o
plano fosse melhor, mas porque **não havia contra o que compará-lo**.

## Comparação do código gerado

**Arquitetura.** Os dois módulos ficaram consistentes com o domínio, mas em camadas
diferentes, e isso apareceu na especificação, não no código. `cnpj.py` é função pura, sem I/O,
irmã de `cpf.py`. `lote.py` é serviço de aplicação: lê disco, orquestra os dois validadores e
tem interface de terminal. A consequência prática foi manter `lote` **fora** do
`src/validacao/__init__.py`, que exporta apenas os validadores de domínio — quem valida um
documento não deveria receber junto uma função que abre arquivos.

**Atendimento aos requisitos.** Ambos atendem integralmente ao que a spec pedia. O CNPJ cumpre
os seis requisitos com 50 testes; o lote cumpre os oito com 28. Nos dois casos, os testes foram
escritos a partir dos cenários da especificação, não a partir do código — o que significa que
uma falha de teste aponta divergência entre código e spec, e não entre código e a opinião de
quem testou.

**Diferença mais interessante.** No CNPJ, a especificação estava certa e o código precisou se
adequar a ela. No lote, aconteceu o inverso: o critério CA2 dizia que uma linha em branco seria
reportada como "campo vazio", e o teste falhou porque o módulo `csv` da biblioteca padrão
descarta linhas em branco antes de entregá-las. **A especificação estava errada, não o
código.** A correção foi ajustar o CA2, acrescentar o critério CA2b e registrar a decisão D6.

Isso é uma limitação real do SDD que vale nomear: a spec só é tão boa quanto o conhecimento
que se tem do terreno no momento de escrevê-la. Escrever antes reduz a chance de errar a regra
de negócio — foi o que salvou o CNPJ alfanumérico — mas não elimina a surpresa vinda do
comportamento das bibliotecas. O que muda é o que se faz com a surpresa: sem spec, o
comportamento do `csv` teria sido absorvido silenciosamente pelo código; com spec, ele virou
uma linha escrita, um critério novo e uma decisão registrada.

## Um terceiro tipo de falha: verificação no ambiente errado

Além da falha de código (Aula 2) e da falha de especificação (o critério CA2), esta atividade
produziu uma terceira, de natureza distinta.

Os testes do lote foram escritos usando `Path.write_text(conteudo, encoding=..., newline="")`.
A verificação prévia passou. Ao rodar `pytest` na máquina do projeto, **13 dos 28 casos
falharam** com `TypeError: write_text() got an unexpected keyword argument 'newline'`.

O parâmetro `newline` só existe em `Path.write_text` a partir do **Python 3.10**. O ambiente de
referência deste projeto é o **3.9.12**, e isso está escrito em `CLAUDE.md`, na convenção que
diz textualmente para "não usar sintaxe posterior ao 3.9". A regra existia, estava versionada,
e foi violada mesmo assim — porque o ambiente onde o código foi verificado rodava Python 3.11,
e nele o teste passava.

Nem a especificação nem a revisão de diff pegariam isso. A spec descreve comportamento, não
compatibilidade de interpretador; a revisão de diff olha a lógica, e a lógica estava correta. O
que falhou foi mais banal e mais perigoso: **o veredito "verificado" foi emitido por um
ambiente que não era o de destino.** Um verde obtido no lugar errado é pior que nenhum verde,
porque ele encerra a dúvida.

A correção foi trocar por `open(str(caminho), "w", encoding=..., newline="")`, que se comporta
igual em todas as versões, e acrescentar ao `CLAUDE.md` a proibição explícita de dar por
verificado um teste executado em outro interpretador.

## O que foi feito e o que se aprendeu

Percorri o ciclo completo de SDD duas vezes. Na primeira, com OpenSpec, especifiquei a
validação de CNPJ com suporte ao formato alfanumérico que a Receita Federal passou a emitir em
31/07/2026: escrevi a user story sem decisão técnica, derivei seis requisitos, escrevi os
cenários em Given/When/Then, pedi um plano de tarefas ao agente e o revisei — removendo duas
tarefas fora de escopo, fundindo três que eram uma só e acrescentando a que faltava, conferir a
regra contra a fonte antes de escrever código. Executei o plano, revisei cada diff e encontrei
três defeitos, dois deles em código já mesclado na `main` e coberto por 38 testes verdes. Na
segunda, em Markdown manual, especifiquei e implementei a validação em lote via CSV, com
tratamento de BOM, detecção de separador e três códigos de saída distintos.

O aprendizado principal não foi sobre qual ferramenta é melhor — as duas produziram código
equivalente, e a disciplina importou mais que o formato. Foi sobre **onde exatamente a
especificação paga**. Ela paga em dois momentos, e os dois foram medidos aqui. Paga quando a
regra vem de fora e não pode ser adivinhada: um modelo que "sabe validar CNPJ" sabe a versão de
antes de julho de 2026, e escreveria um validador que rejeita empresas legítimas com total
convicção, aprovado por testes que ele mesmo geraria. E paga quando o escopo precisa ser
defendido: as duas tarefas fora de escopo do plano do CNPJ eram justamente as que **pareciam
mais úteis**, e só foram removidas porque existia um documento anterior dizendo que não
entravam.

O corolário incômodo é que a spec não protege contra o que ninguém sabia. O erro do `csv` não
foi pego pela especificação — foi pego pelo teste. Especificação e teste não são redundantes: a
primeira verifica se estamos construindo a coisa certa, o segundo verifica se a construímos
direito, e as duas falhas aconteceram, uma de cada tipo, neste mesmo trabalho.
