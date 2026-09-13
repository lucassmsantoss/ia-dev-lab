# Harness e Arquitetura na Prática — Relatório final

| | |
|---|---|
| **Aluno** | Lucas Santos |
| **Disciplina** | Tópicos Avançados em Engenharia de Software 2 — PPgTI / IMD-UFRN |
| **Repositório** | https://github.com/lucassmsantoss/ia-dev-lab |
| **Data** | 13/09/2026 |

**1. Autonomia e guardrail (Etapa 1).** Comparei revisão prévia (proponho o diff, só aplico
depois de aprovado) contra auto-aceitar (aplico direto, reviso depois), na mesma tarefa
pequena. A diferença de tempo foi real mas pequena (~11s vs. ~5s); o que importa é a forma da
curva: revisão prévia tem custo fixo que não cresce muito com o tamanho da tarefa, enquanto o
risco do auto-aceitar cresce com o tamanho do diff que sobra para revisar depois — detalhes em
`docs/etapa1-autonomia.md`. O guardrail é um hook de pré-commit do Git
(`.githooks/pre-commit`, ativado por `core.hooksPath`) que bloqueia exclusão ou redução
desproporcional de arquivos em `tests/`, testado de propósito em três cenários reais
(`docs/etapa1-hook.md`).

**2. TDD e enforcement (Etapa 2).** Corrigi, em Red-Green-Refactor real, um defeito já
documentado e pendente desde a atividade anterior (`checkpoint-humano.md`): a normalização de
CPF aceitava documento válido cercado de lixo e lançava exceção para dígitos não-ASCII. Testes
escritos e confirmados falhando antes de qualquer mudança em `cpf.py`. Investiguei o skill
Superpowers como ferramenta de enforcement: ele não bloqueia tecnicamente (como o `tdd-guard`
faria), impõe a disciplina por instrução e checklist — mais fraco tecnicamente, mais explícito
sobre o raciocínio. Comparei com uma tarefa igual em tamanho feita sem TDD (`mascarar_cpf`):
sem teste antes, a primeira versão tinha 4 defeitos de entrada inválida que só apareceram ao
testar manualmente depois — detalhes em `docs/etapa2-tdd.md`.

**3. Checkpoint humano (Etapa 3).** O checkpoint já definido no projeto ("nenhuma mudança de
comportamento em domínio consumido fora do escopo declarado") disparou de novo, de verdade,
durante a correção do CPF: com o arquivo aberto, ficou tentador também extrair a duplicação de
`_calcular_digito` encontrada de relance. Rejeitei o bundling — a duplicação virou o objeto da
investigação da Etapa 6, não um "já que estou aqui". Meu papel foi recusar a conveniência, não
escrever o código (`docs/etapa3-checkpoint.md`).

**4 e 5. Decisão arquitetural, ADR e diagrama.** Resumo gerado a partir do código real: três
módulos, uma dependência unidirecional (`lote.py` → validadores), e um ponto de acoplamento
sem import — a mesma regra de módulo 11 duplicada em `cpf.py` e `cnpj.py`. Decisão (ADR 0002,
`docs/adr/0002-*.md`): não extrair serviço (sem fronteira de deploy que justifique) nem
extrair a duplicação para um módulo compartilhado (violaria a proibição de pastas por tipo
técnico do `CLAUDE.md`) — em vez disso, um teste de equivalência
(`tests/test_equivalencia_modulo11.py`) garante que as duas cópias nunca divergem em silêncio.
Gerei o diagrama C4 de contêiner de duas formas: um prompt direto e outro alimentado com o
resumo da Etapa 4. Só a segunda versão mostrou a relação de duplicação — que, por não ser
import nem chamada, um diagrama de contêiner "padrão" não captura por si só
(`docs/etapa5-diagrama.md`).

**6. Vá Além — dívida técnica (Etapa 6).** `ruff --select ALL` sobre `src/validacao/` apontou
`PLR2004` duas vezes, no mesmo padrão, em arquivos diferentes — o sinal que levou à duplicação
acima. O achado não veio do aviso de estilo em si, veio de ler as duas ocorrências lado a lado.
Mitigação real, não só proposta: implementada nesta atividade (`docs/etapa6-divida-tecnica.md`).

**Dificuldade real.** Decidir onde um helper compartilhado deveria morar, quando a própria
convenção do projeto (nada de `utils/`) elimina a resposta mais óbvia. Não foi um problema
técnico — a extração em si é trivial — foi perceber que a convenção contra pastas por tipo
técnico, escrita para manter o código organizado por domínio, também bloqueia a saída mais
fácil para duplicação genuína, e que a resposta certa (teste de equivalência) só aparece quando
se aceita não resolver a duplicação em si, só o risco que ela cria.
