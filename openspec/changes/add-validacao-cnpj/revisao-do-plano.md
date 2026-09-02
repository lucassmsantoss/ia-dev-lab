# Revisão do plano de tarefas

Registro das tarefas 7 e 8 da Etapa 2: o plano gerado pelo agente a partir da especificação, a
crítica feita na revisão humana e as alterações aplicadas com justificativa.

**Agente:** Claude Opus 5, com acesso a `proposal.md`, `specs/validacao-cnpj/spec.md` e
`design.md`.
**Revisor:** Lucas Santos.
**Data:** 02/09/2026.

---

## Plano proposto pelo agente (versão 1)

```
1. Criar src/validacao/cnpj.py
2. Implementar a função validar_cnpj
3. Implementar a função de cálculo do dígito verificador
4. Adicionar suporte a caracteres alfanuméricos
5. Criar função auxiliar para formatar CNPJ com máscara
6. Criar função para gerar CNPJs válidos para uso nos testes
7. Escrever os testes em tests/test_cnpj.py
8. Rodar a suíte e corrigir falhas
9. Atualizar o README
```

## Crítica

O plano é executável, mas tem cinco problemas. Três são de sequência e dois são de escopo.

**Falta a tarefa que mais importa.** Não há nenhum passo para *conferir a regra contra a
fonte*. O plano assume que a norma do CNPJ alfanumérico é conhecida e parte direto para a
implementação. É exatamente aqui que a atividade tem seu ponto: se a regra estiver errada, os
testes escritos junto com o código vão confirmar o erro em vez de expô-lo. Um plano de SDD que
não valida a premissa externa não é um plano de SDD.

**Os testes estão no fim.** A tarefa 7 concentra todos os testes depois de quatro tarefas de
implementação. Isso contraria a regra registrada em `openspec/config.yaml`, que determina que
tarefas de teste acompanham a tarefa que implementam — e, na prática, significa passar por
quatro etapas sem nenhum sinal de que o caminho está certo.

**As tarefas 2, 3 e 4 são a mesma tarefa.** "Implementar a validação", "implementar o cálculo
do dígito" e "adicionar suporte a alfanuméricos" não são fases separadas: o suporte
alfanumérico *é* como o dígito é calculado. Dividir assim cria a ilusão de progresso — daria
para marcar duas como concluídas com o código ainda inteiramente quebrado.

**A tarefa 5 está fora de escopo.** Formatar CNPJ com máscara é explicitamente um não-objetivo
declarado em `proposal.md`. O agente a incluiu por associação temática, não por leitura da
proposta.

**A tarefa 6 é fora de escopo e perigosa.** Gerar CNPJs válidos em código de produção não foi
pedido, e usar um gerador para produzir os casos de teste é um erro metodológico: os testes
passariam a verificar que o gerador e o validador concordam entre si, mesmo que ambos
implementem a regra errada. Os casos de teste precisam vir de inscrições reais conhecidas e da
documentação da Receita.

**Nada atualiza a regra de escopo.** O arquivo `src/validacao/CLAUDE.md` descreve a
normalização como "remove pontos, traços, barras e espaços". Com esta mudança, a normalização
passa a incluir conversão de caixa, e a regra de escopo precisa refletir isso — caso contrário
o contexto do projeto passa a mentir sobre o próprio código.

## Alterações aplicadas

| # | Alteração | Justificativa |
|---|---|---|
| 1 | **Adicionada** tarefa de conferir a regra contra a fonte oficial e fixar casos reais conhecidos, como primeira tarefa do plano | A premissa externa precisa ser verificada antes de virar código; é o passo que impede o erro silencioso |
| 2 | **Removidas** as tarefas 5 e 6 (formatação e gerador) | Ambas são não-objetivos declarados na proposta; o gerador ainda introduziria testes autoconfirmatórios |
| 3 | **Fundidas** as tarefas 2, 3 e 4 em uma única tarefa de implementação | Não são etapas independentes e a divisão produzia falso progresso |
| 4 | **Redistribuídos** os testes, agora acompanhando cada tarefa que implementam | Cumpre a regra declarada em `openspec/config.yaml` e dá sinal de correção a cada passo |
| 5 | **Adicionada** tarefa de atualizar `src/validacao/CLAUDE.md` | A regra de escopo descreve a normalização e passaria a estar desatualizada |
| 6 | **Adicionada** tarefa de rodar a suíte completa, não só a de CNPJ | A especificação tem um requisito explícito de preservação do comportamento do CPF |
| 7 | **Reordenada** a atualização do README para o fim, após a suíte verde | Documentar antes de o código funcionar produz documentação que descreve intenção, não comportamento |

O plano revisado está em [`tasks.md`](tasks.md).

## Observação

Das nove tarefas propostas, duas foram removidas, três viraram uma, e três novas foram
acrescentadas — o plano final tem pouco mais da metade dos itens originais e cobre mais coisa.
Vale registrar que os dois itens fora de escopo (máscara e gerador) eram justamente os mais
"úteis" à primeira vista. A proposta havia declarado ambos como não-objetivos de forma
explícita, e ainda assim eles apareceram. É um argumento a favor de escrever a seção de
não-objetivos: sem ela, não haveria contra o que comparar, e as duas tarefas teriam entrado no
plano sem qualquer atrito.
