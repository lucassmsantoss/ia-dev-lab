# Etapa 1 — Comparação entre dois modos de autonomia

Tarefa escolhida: adicionar em `tests/test_cpf.py` um teste cobrindo CPF válido com espaços
extras ao redor da string (não só entre os grupos de dígitos) —
`test_aceita_cpf_valido_com_espacos_ao_redor`. É pequena, de baixíssimo risco (só adiciona um
teste, não toca em código de produção) e fácil de desfazer entre as duas execuções, o que
permite isolar a variável real do experimento: o modo de autonomia, não o tamanho da tarefa.

A ferramenta usada nesta sessão (Claude via Cowork) não expõe um alternador nativo de
"plan mode vs. auto-accept edits" como o exemplo do enunciado (esse alternador existe no
Claude Code CLI local). Por isso, o experimento reproduziu a mesma distinção pela **postura de
trabalho**, que é o que o alternador de fato controla — se a mudança é aplicada só depois de eu
ver e aprovar exatamente o que vai mudar, ou direto:

- **Modo 1 — revisão prévia.** O agente escreve o diff proposto **antes** de tocar no
  arquivo, e só aplica depois da aprovação explícita.
- **Modo 2 — auto-aceitar.** O agente aplica a mudança direto, sem etapa de proposta.

## Execução 1 — revisão prévia

| Passo | Horário |
|---|---|
| Proposta escrita e apresentada | 14:08:04 |
| Aprovação | 14:08:11 |
| Mudança aplicada e verificada | 14:08:15 |

**Tempo gasto:** ~11s (7s para redigir e apresentar a proposta, 4s para aplicar depois de
aprovada).

**Sensação de controle:** alta. Antes de qualquer arquivo mudar, o diff inteiro — inclusive a
justificativa de risco ("só adiciona teste, não toca em produção") — já estava na minha frente.
Eu decidia com a mudança ainda não aplicada, não revisando algo que já aconteceu.

**Risco percebido:** baixo, mas não zero: o custo é o tempo de leitura, e para uma tarefa deste
tamanho a proposta chega a ser mais texto do que o diff em si. Para uma tarefa maior, esse é
exatamente o ponto — a proposta vira o lugar certo para pegar escopo indevido antes de existir
como código, o que é literalmente o que aconteceu na Etapa 4 da atividade de SDD (revisão do
plano do CNPJ removeu duas tarefas fora de escopo antes de qualquer linha ser escrita).

## Execução 2 — auto-aceitar

| Passo | Horário |
|---|---|
| Mudança aplicada direto | 14:08:22 – 14:08:27 |

**Tempo gasto:** ~5s.

**Sensação de controle:** menor, mas não ausente — a mudança ainda apareceu como um diff
revisável depois de feita (`git diff`), só que a ordem inverteu: primeiro o arquivo muda,
depois eu confirmo que a mudança era essa mesma. Para uma tarefa deste tamanho, a diferença é
irrelevante. Para uma tarefa que mexesse em `src/validacao/` — código de domínio já consumido e
coberto por 38+ testes — inverter essa ordem é exatamente o que o checkpoint humano do projeto
(`openspec/changes/add-validacao-cnpj/checkpoint-humano.md`) foi desenhado para impedir.

**Risco percebido:** baixo para esta tarefa específica, mas o risco não escala linearmente com o
tamanho da tarefa da mesma forma nos dois modos. No modo de revisão prévia, uma tarefa maior
custa mais tempo de leitura, mas o risco de aceitar algo indevido continua baixo, porque nada
foi aplicado ainda. No modo auto-aceitar, uma tarefa maior custa pouco tempo a mais para
*aplicar*, mas o risco de um `git diff` de dezenas de linhas ser revisado por cima — e algo
passar despercebido — cresce.

## O que a comparação revelou

A diferença de tempo (~11s vs. ~5s, pouco mais do que o dobro) é real, mas para uma tarefa deste
tamanho ela é desprezível em termos absolutos — o que ela expõe é a *forma* da curva, não o
valor para esta tarefa. O tempo do modo de revisão prévia é dominado pelo custo fixo de redigir
e apresentar a proposta, que **não cresce proporcionalmente ao tamanho da tarefa** (descrever
"adicionar um teste" ou "adicionar dez" tem custo de escrita parecido). Já o risco do modo
auto-aceitar cresce com o tamanho do diff que fica para revisar depois — revisar 5 linhas por
cima é seguro, revisar 200 por cima é como não revisar.

A conclusão prática, já refletida nas convenções do projeto antes mesmo desta atividade
(`CLAUDE.md`: "Não aceitar mensagem de commit gerada por IA sem revisar antes o `git diff`"): os
dois modos não são "mais seguro" e "mais rápido" de forma genérica — é revisão **antes** vs.
revisão **depois**, e qual delas vale o custo depende do quanto a tarefa pode dar errado. Para
uma tarefa como esta (só teste, sem tocar produção), auto-aceitar mais revisão do diff depois é
suficiente. Para qualquer coisa em `src/validacao/`, a revisão prévia — ou o checkpoint humano
que a formaliza — é a que o projeto já exige.
