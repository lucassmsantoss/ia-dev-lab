# Log da sessão — Atividade "Harness e Arquitetura na Prática"

Resumo cronológico da sessão de trabalho com o agente de IA (Claude, via Cowork) durante esta
atividade. Não é uma limpeza do processo — inclui a pergunta de esclarecimento feita antes de
começar e as decisões tomadas no meio do caminho, não só o resultado final.

## 1. Levantamento de contexto

- Leitura do enunciado da atividade (`Aula6_Pratica_Assincrona_Harness_Arquitetura`).
- Leitura do plano da Etapa 2 do projeto (`plano_projeto_final.md`, seção "Aproveitando o
  repositório `ia-dev-lab`"), que apontava o `ia-dev-lab` como o repositório certo para esta
  atividade, por já ter o harness (OpenSpec, `CLAUDE.md`, convenções) configurado.
- Leitura do estado atual do repositório: `README.md`, `CLAUDE.md`, `src/validacao/CLAUDE.md`,
  o código de `cpf.py`/`cnpj.py`/`lote.py`, os relatórios das duas atividades anteriores e os
  artefatos da mudança OpenSpec `add-validacao-cnpj` — em especial `checkpoint-humano.md` e
  `revisao-dos-diffs.md`, que documentavam um defeito real e não corrigido em `cpf.py`.

## 2. Pergunta de esclarecimento

Antes de tocar em qualquer arquivo, quatro decisões foram levadas para aprovação explícita, por
envolverem escolha de escopo e não terem uma resposta única correta:

1. Como executar comandos no repositório local, já que a sessão não tem shell direto na
   máquina (só listagem/transferência de arquivo e controle de tela) — decidido: controle de
   tela.
2. Qual risco o hook da Etapa 1 deveria bloquear — decidido: edição destrutiva de `tests/`.
3. Qual ferramenta de enforcement de TDD investigar na Etapa 2 — decidido: Superpowers, já
   disponível como skill neste ambiente.
4. Qual opção da Etapa 6 (Vá Além) seguir — decidido: dívida técnica, com `ruff`.

## 3. Execução

- Clonado o repositório (leitura de `origin/main`) para validar lógica rapidamente antes de
  aplicar qualquer coisa na máquina local; identificado que o `main` local está à frente do
  `origin/main` em 5 commits ainda não publicados (documentação da atividade de SDD) — por
  isso o trabalho de Git real desta atividade foi conduzido na máquina local, não na cópia.
- `ruff check src/ --select ALL` rodado sobre `src/validacao/` para a investigação real da
  Etapa 6 (ver `docs/etapa6-divida-tecnica.md`).
- Ciclo Red-Green-Refactor real para `fix-normalizacao-cpf`, usando o skill
  `superpowers:test-driven-development` (ver `docs/etapa2-tdd.md`): testes de regressão
  escritos e confirmados falhando contra o código antigo antes de qualquer alteração em
  `cpf.py`.
- Durante essa correção, avaliada e **rejeitada** a tentação de também extrair a duplicação de
  cálculo de dígito verificador entre `cpf.py` e `cnpj.py` no mesmo commit — checkpoint humano
  descrito em `docs/etapa3-checkpoint.md`.
- Tarefa de comparação sem TDD (`mascarar_cpf`), implementada sem teste, avaliada, e corrigida
  com teste depois — ver `docs/etapa2-tdd.md`.
- Comparação dos dois modos de autonomia (`docs/etapa1-autonomia.md`) e implementação do hook
  de pré-commit (`docs/etapa1-hook.md`), ambos com evidência de execução real.
- Resumo de arquitetura, ADR e diagramas (`docs/etapa4-arquitetura.md`,
  `docs/adr/0002-nao-extrair-servico.md`, `docs/etapa5-diagrama.md`).
- Commits reais no repositório local, um por unidade de trabalho coerente (não um commit
  único), e publicação no GitHub — ver `docs/etapa6-divida-tecnica.md` e o histórico de commits
  do repositório para o registro completo.

## 4. O que este log não inclui

O texto integral de cada mensagem trocada com o agente. O enunciado pede o log/transcript "ao
longo de toda a atividade", e a decisão tomada aqui foi registrar o que aconteceu e por quê —
decisões, pontos de checkpoint, evidências — em vez de colar milhares de linhas de
conversa que não agregam ao que um revisor precisa para confirmar o processo. Cada decisão
relevante está registrada em um documento próprio, referenciado acima, com a evidência de
execução ao lado da afirmação (não só a afirmação).
