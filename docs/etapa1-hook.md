# Etapa 1 — Hook: bloqueio de edição destrutiva em `tests/`

## O risco escolhido

Diferente do exemplo de aula ("bloquear merge na main"): **impedir que um commit apague ou
esvazie um arquivo de teste** — por exclusão do arquivo inteiro, ou por uma edição que remove
muito mais linha do que adiciona.

É o risco certo para este projeto por três motivos, todos específicos ao `ia-dev-lab` e não
genéricos de qualquer repositório:

1. **TDD (Etapa 2) e o checkpoint humano de `src/validacao/`** dependem de a suíte de testes
   ser uma rede de segurança confiável. Se o próprio agente de IA pode apagar ou reduzir testes
   no mesmo commit que "conserta" o código, o checkpoint que existe para barrar mudanças de
   comportamento fora de escopo (`openspec/changes/add-validacao-cnpj/checkpoint-humano.md`)
   perde o sentido — a rede que deveria acusar a mudança pode ser a primeira coisa alterada.
2. Como documentado em `revisao-dos-diffs.md`, defeitos reais em `src/validacao/cpf.py`
   passaram despercebidos por meses porque a suíte de 38 testes, mesmo verde, tinha um buraco
   específico. Um teste apagado sob pressão de prazo é o mesmo problema, só que deliberado.
3. É exatamente o tipo de ação que um agente de IA, sob instrução de "fazer o commit passar",
   tem como atalho disponível — e que não aparece destacado no `git diff` do código de
   produção, só no de teste, que costuma receber menos atenção na revisão.

## Implementação

Hook de **pré-commit do Git** (`.githooks/pre-commit`), ativado por
`git config core.hooksPath .githooks`. Escolhido como "controle equivalente" a um hook do
Claude Code porque roda independente da ferramenta de IA usada — vale também para o VS Code +
Copilot, ou para uma edição manual — e porque `.git/hooks/` não é versionado por padrão; usar
`core.hooksPath` para apontar para uma pasta dentro do repositório é o jeito de ter o hook
**commitado**, e não apenas configurado localmente.

O hook bloqueia dois padrões, olhando só para `tests/`:

- Qualquer arquivo sob `tests/` presente no commit como **exclusão**.
- Qualquer arquivo sob `tests/` cujo diff **remove mais linhas do que adiciona**, acima de um
  piso de 3 linhas (heurística para "reduziu o arquivo", não para uma refatoração pontual).

Tem uma saída consciente — `PERMITIR_EDICAO_DESTRUTIVA_TESTS=1 git commit ...` — porque excluir
um teste realmente obsoleto é uma decisão legítima às vezes; o hook não proíbe a decisão, exige
que ela seja explícita e visível no comando usado, não silenciosa.

## Teste do hook — disparando a ação bloqueada de propósito

Três cenários, executados de propósito contra o próprio repositório:

**1) Commit legítimo (só adiciona testes) — não bloqueado:**

```
$ git diff --cached --numstat -- tests/
46      5       tests/test_cpf.py
$ .githooks/pre-commit; echo "codigo de saida: $?"
codigo de saida: 0
```

**2) Exclusão de arquivo de teste — bloqueado:**

```
$ git rm tests/test_lote.py
$ .githooks/pre-commit
BLOQUEADO pelo hook pre-commit: exclusao de arquivo(s) de teste no commit:
  - tests/test_lote.py

Se isto e intencional (ex.: teste obsoleto apos remocao de funcionalidade),
refaca o commit com: PERMITIR_EDICAO_DESTRUTIVA_TESTS=1 git commit ...
codigo de saida do hook: 1
```

**3) Edição destrutiva (apaga 67 de 73 linhas de `tests/test_cpf.py`) — bloqueado, com e sem o
escape consciente:**

```
$ git diff --cached --numstat -- tests/
0       67      tests/test_cpf.py
$ .githooks/pre-commit
BLOQUEADO pelo hook pre-commit: tests/test_cpf.py perde 67 linha(s) e ganha apenas 0 -- parece
reducao de cobertura de teste, nao refatoracao.

Se isto e intencional, refaca com: PERMITIR_EDICAO_DESTRUTIVA_TESTS=1 git commit ...
codigo de saida do hook: 1

$ PERMITIR_EDICAO_DESTRUTIVA_TESTS=1 .githooks/pre-commit
BLOQUEADO pelo hook pre-commit: tests/test_cpf.py perde 67 linha(s) e ganha apenas 0 -- parece
reducao de cobertura de teste, nao refatoracao.
PERMITIR_EDICAO_DESTRUTIVA_TESTS=1 definido: prosseguindo mesmo assim.
codigo de saida com escape: 0
```

Em todos os três casos a edição destrutiva foi desfeita logo em seguida
(`git reset` + restaurar o arquivo original) — os cenários 2 e 3 foram simulados propositalmente
para testar o hook, não commitados.

## O que ficou de fora

O hook olha só para contagem de linhas e exclusão de arquivo — não entende se um teste
específico foi removido de dentro de um arquivo que ainda cresce no total (ex.: apagar uma
função de teste de 10 linhas e adicionar uma nova, não relacionada, de 15). Pegar isso exigiria
comparar nomes de função `test_*` entre as duas versões do arquivo, não só `numstat`. Ficou fora
por proporcionalidade: o hook já cobre os dois casos mais prováveis (exclusão de arquivo,
redução grosseira), e complexidade adicional em um script de shell tem seu próprio custo de
manutenção.
