# Checkpoint humano

Registro das tarefas 13 e 14 da Etapa 4: o ponto de parada obrigatório definido para este
projeto, a situação real em que ele disparou, e a decisão tomada.

---

## O checkpoint definido

> **Nenhuma alteração no comportamento de um módulo de domínio que já esteja sendo consumido e
> coberto por testes verdes pode ser aplicada dentro de uma mudança cujo escopo não a
> declarou. A execução para, e a decisão é humana.**

O checkpoint incide sobre `src/validacao/`. É o ponto certo para este projeto por três razões.
Primeiro, são funções puras exportadas em `__init__.py`: qualquer módulo pode passar a
depender delas, e uma alteração de comportamento é uma quebra de contrato silenciosa — não há
erro de compilação para avisar. Segundo, é o único lugar do projeto onde uma regra vem de norma
externa, então "corrigir" pode significar tanto consertar um defeito quanto reinterpretar a
norma por conta própria. Terceiro, mudanças aqui alteram a suíte de testes que serve de rede de
segurança para todo o resto — e uma rede de segurança que se altera junto com o código que ela
protege deixa de ser rede.

O checkpoint corresponde ao exemplo "antes de expor um novo endpoint" citado no enunciado,
transposto para um projeto que não tem endpoints: a interface pública aqui é a assinatura e o
comportamento das funções de validação.

## O disparo — situação real, não hipotética

Durante a Etapa 3, a revisão dos diffs encontrou dois defeitos no `src/validacao/cpf.py`,
descritos em [`revisao-dos-diffs.md`](revisao-dos-diffs.md): a normalização aceita um CPF
válido cercado de lixo (`"<script>52998224725</script>"` retorna `True`) e o uso de
`str.isdigit()` faz a função **levantar exceção** para `"²2998224725"`, violando a regra que
ela mesma declara.

A continuação natural da execução seria óbvia: o defeito está identificado, a correção é de
poucas linhas, o módulo está aberto na tela e o agente é perfeitamente capaz de aplicá-la.
Foi exatamente aí que o checkpoint mandou parar. `cpf.py` é módulo de domínio consumido, com
testes verdes, e a mudança `add-validacao-cnpj` declara em `proposal.md`, na seção de
não-objetivos, que **não** altera o comportamento da validação de CPF.

## A decisão tomada

**Rejeitar a correção dentro desta mudança e voltar à especificação.**

A correção será feita, mas como uma mudança própria — `fix-normalizacao-cpf` — com sua própria
proposta, spec e plano de tarefas. Os três motivos:

**O escopo declarado tem que valer alguma coisa.** A mesma proposta que declarou "não altera o
CPF" é a que fez a revisão do plano remover duas tarefas fora de escopo, na Etapa 2. Aceitar
agora uma alteração fora de escopo porque desta vez ela é conveniente esvazia o instrumento —
um limite que cede quando incomoda não é um limite.

**Corrigir aqui esconderia a descoberta.** Se o conserto entrar no meio de um Pull Request
chamado "adiciona validação de CNPJ", ele vira três linhas de diff que ninguém revisa com
atenção. Como mudança própria, o defeito ganha uma proposta que explica **por que a suíte de 38
testes não o pegou** — e é essa explicação, não o conserto, que tem valor para o projeto.

**A correção é uma quebra de contrato, e precisa ser tratada como tal.** Entradas que hoje
retornam `True` passarão a retornar `False`. Se algum consumidor já depende do comportamento
atual, isso é uma regressão do ponto de vista dele. Merece uma decisão explícita e registrada,
não um efeito colateral.

## O papel humano assumido

O papel aqui não foi o de quem escreve o código — o agente já tinha o defeito localizado e a
correção pronta, e teria produzido um patch melhor e mais rápido do que eu à mão.

O papel foi o de **dono do escopo**: decidir o que pertence a esta unidade de trabalho e o que
não pertence. Essa decisão não é derivável do código, da especificação nem do defeito. Ela
depende de coisas que só existem fora do repositório — que este Pull Request será lido por
alguém, que a rastreabilidade entre a mudança e o motivo dela vale mais do que economizar um
ciclo, e que um defeito de uma semana pode esperar mais um dia.

O agente estava certo sobre o defeito e certo sobre a correção. Ele não tinha como estar certo
sobre **quando**.

## Encaminhamento

- [x] Defeitos documentados em `revisao-dos-diffs.md`, com reprodução verificada
- [x] Regra atualizada em `src/validacao/CLAUDE.md`, proibindo `str.isdigit()` e a remoção
      genérica de caracteres — de modo que o próximo código gerado já nasça correto
- [ ] Abrir a mudança `fix-normalizacao-cpf` com proposta, spec e plano próprios
- [ ] Incluir na spec dessa mudança o caso ausente: entrada inválida que **contém** uma
      entrada válida

Os dois itens marcados foram feitos porque documentar o defeito e fechar a porta para que ele
se repita não altera comportamento — e portanto não esbarram no checkpoint.
