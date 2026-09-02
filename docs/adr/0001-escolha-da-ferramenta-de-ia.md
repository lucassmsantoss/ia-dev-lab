# ADR 0001 — Escolha das ferramentas de IA para desenvolvimento

- **Status:** Aceito
- **Data:** 2026-08-27
- **Autor:** Lucas Santos
- **Decisores:** Lucas Santos

## Contexto

A Etapa 1 da atividade pede pelo menos uma ferramenta de IA de cada categoria vista em aula:

1. **IDE + assistente** — completação e chat dentro do editor, com contexto do arquivo aberto.
2. **CLI agent** — agente capaz de ler e escrever vários arquivos, rodar comandos e executar
   tarefas de várias etapas sem intervenção a cada passo.

As duas categorias resolvem problemas diferentes e não competem entre si. O assistente de IDE
é bom no ciclo curto — escrever uma função, explicar um trecho, sugerir a próxima linha —
porque enxerga o cursor e o arquivo aberto. O CLI agent é bom no ciclo longo — criar uma
estrutura de pastas inteira, refatorar vários arquivos de uma vez, escrever documentação
consistente com o código — porque enxerga o repositório e consegue agir sobre ele.

Havia ainda um requisito prático: o ambiente de trabalho é Windows, com Python via Anaconda
e VS Code já instalados. Trocar de editor ou de stack só para atender à atividade adicionaria
um custo de configuração sem ganho pedagógico.

## Decisão

Adotar duas ferramentas, uma de cada categoria:

- **VS Code + GitHub Copilot** para a categoria IDE + assistente.
- **Claude (Cowork / Claude Code)** para a categoria CLI agent, com o arquivo `CLAUDE.md`
  como mecanismo de contexto de projeto.

O `CLAUDE.md` na raiz é o contrato principal do repositório com a IA, e regras mais estritas
ficam em arquivos `CLAUDE.md` aninhados por escopo — hoje, `src/validacao/CLAUDE.md`.

## Justificativa

**Por que VS Code + Copilot:** já estava instalado e autenticado na máquina, elimina custo de
setup, e a completação inline é o formato certo para o ciclo curto de escrita. O Copilot lê o
arquivo aberto e os arquivos próximos, o que basta para sugerir a implementação de uma função
cuja assinatura já foi escrita.

**Por que Claude como CLI agent:** o diferencial nesta atividade é o arquivo de contexto de
projeto. O `CLAUDE.md` permite declarar convenções uma única vez e tê-las respeitadas em toda
alteração, em vez de repetir as mesmas instruções em cada prompt. Isso é exatamente o que a
Etapa 2 quer demonstrar, e é o que torna o experimento da Etapa 4 mensurável: a diferença
entre o prompt fraco e o prompt eficaz fica visível justamente porque o contexto está escrito.

**Por que não escolher só uma:** um assistente de IDE não gera uma estrutura de projeto
coerente em um passo, e um agente de CLI é uma ferramenta desproporcional para completar uma
linha. Usar as duas separa bem os dois ritmos de trabalho.

## Alternativas consideradas

- **Cursor** — IDE com agente integrado, resolveria as duas categorias de uma vez. Descartada
  porque exigiria migrar o ambiente do VS Code e, ao unificar as ferramentas, apagaria
  justamente a distinção entre as duas categorias que a atividade quer exercitar.
- **Codex CLI** — alternativa direta na categoria CLI agent. Descartada por não usar o formato
  de contexto de projeto que já estava sendo estudado na disciplina (`CLAUDE.md` / `AGENTS.md`),
  o que tornaria a Etapa 2 menos direta.
- **Continue (extensão open source)** — flexível na escolha do modelo, mas exigiria configurar
  e custear um provedor de modelo separadamente, sem ganho para os objetivos da atividade.

## Consequências

**Positivas**

- O contexto do projeto fica versionado no repositório: qualquer pessoa que clonar recebe as
  mesmas convenções que a IA recebe, e a documentação não se descola do código.
- A separação por categoria deixa claro qual ferramenta usar para cada tipo de tarefa.
- As convenções ficam testáveis: se o código gerado violar o `CLAUDE.md`, isso aparece na
  revisão do Pull Request.

**Negativas e riscos**

- Manter duas ferramentas significa manter duas autenticações e dois pontos de atualização.
- O `CLAUDE.md` é lido pelo Claude, mas o Copilot não usa esse formato — há risco das duas
  ferramentas divergirem nas convenções que seguem. Mitigação: o `CLAUDE.md` é a fonte da
  verdade, e o que o Copilot gerar é conferido contra ele na revisão.
- Dependência de serviços proprietários e pagos, com risco de mudança de preço ou de limites
  de uso. Mitigação: as decisões e convenções estão em Markdown puro, portanto migráveis para
  outra ferramenta sem perda.
- Contexto escrito é contexto que precisa ser mantido. Um `CLAUDE.md` desatualizado é pior que
  nenhum, porque a IA passa a seguir com confiança uma regra que já não vale.
