# Revisão dos diffs

Registro da tarefa 12 da Etapa 3: o que a revisão humana do `git diff` encontrou **antes** de
aceitar o código gerado.

Foram revisados os diffs de `src/validacao/cnpj.py`, `tests/test_cnpj.py`,
`src/validacao/__init__.py` e `src/validacao/CLAUDE.md`. Três achados, dois deles em código
que já estava na `main` e passando em 38 testes.

---

## Achado 1 — A normalização genérica aceita lixo como documento válido

**Onde:** `src/validacao/cpf.py`, função `_somente_digitos`, escrita na atividade da Aula 2.

**O que a revisão notou:** ao escrever a normalização do CNPJ, a decisão D4 do `design.md`
determinava validar o conjunto de caracteres *antes* de converter. Isso levantou a pergunta de
como o CPF fazia — e ele faz o oposto: descarta tudo que não é dígito e valida o que sobrou.

**Consequência, verificada na prática:**

```
validar_cpf("52998224725abc")               -> True
validar_cpf("529.982.247-25!!!")            -> True
validar_cpf("CPF: 529.982.247-25")          -> True
validar_cpf("<script>52998224725</script>") -> True
```

Todas essas entradas são aceitas como CPF válido. O caractere inesperado não é rejeitado: é
silenciosamente apagado, e o que resta passa. Um formulário que confie nessa validação aceita
um payload de injeção como se fosse um documento.

**Por que passou despercebido na Aula 2:** os testes de caractere inválido usavam
`"abcdefghijk"`, `"529.982.247-2a"` e `"CPF invalido"`. Nos três, o que sobra depois de
descartar as letras tem comprimento diferente de 11, então a validação de tamanho rejeita por
acidente. Nenhum teste tinha um CPF **completo e correto** cercado de lixo — que é justamente o
caso que passa.

**No módulo novo:** `validar_cnpj("11222333000181abc")` retorna `False`. A `_normalizar` do
CNPJ remove apenas `.`, `/`, `-` e espaço; qualquer outro caractere sobrevive para ser
rejeitado pela checagem de conjunto.

---

## Achado 2 — `str.isdigit()` é verdadeiro para caracteres que não são dígitos ASCII

**Onde:** `src/validacao/cpf.py`, mesma função.

**O que a revisão notou:** `isdigit()` parece a forma idiomática de perguntar "isto é um
dígito?", mas em Python ele responde verdadeiro para expoentes e para dígitos de outros
sistemas de numeração.

**Consequências, verificadas na prática:**

```
"²".isdigit()  -> True    int("²")  -> ValueError
"٥".isdigit()  -> True    int("٥")  -> 5

validar_cpf("²2998224725")   -> ValueError: invalid literal for int() with base 10: '²'
validar_cpf("٥2998224725")   -> True
```

São dois defeitos distintos e ambos graves. O primeiro **levanta exceção** — violando
diretamente a regra escrita em `src/validacao/CLAUDE.md`, que diz "nunca levanta exceção", e
que o próprio arquivo de testes afirma verificar. O segundo é um **falso positivo**: um CPF com
um dígito indo-arábico no meio é aceito como válido, porque `int()` converte o caractere e a
comparação final só falharia se o caractere estivesse nas duas últimas posições.

**No módulo novo:** a checagem é `c not in "0123456789"`, comparação explícita contra o
conjunto ASCII. `validar_cnpj("²1222333000181")` e a versão inteiramente em dígitos
indo-arábicos retornam `False`, e há um teste dedicado a isso.

---

## Achado 3 — Um teste que passava pelo motivo errado

**Onde:** `tests/test_cnpj.py`, no próprio código gerado nesta mudança.

**O que a revisão notou:** o teste de sequência repetida usava
`AAAAAAAAAAAA48`. O teste passava. Mas o dígito verificador correto para `AAAAAAAAAAAA` é
**45**, não 48 — então o valor estava sendo rejeitado por dígito verificador inválido, e não
pela regra de sequência repetida que o teste diz verificar.

Se alguém removesse a regra de sequência repetida da implementação, esse teste continuaria
verde. Ele não protegia nada.

**Correção aplicada:** o valor passou para `AAAAAAAAAAAA45`, com dígito verificador calculado.
Os três valores do teste agora têm DV aritmeticamente correto, de modo que a única razão
possível para a rejeição é a regra que o teste nomeia. A docstring registra isso.

---

## O que eu teria deixado passar sem esta revisão

Os achados 1 e 2 são a resposta honesta à pergunta da tarefa 12. Ambos estão em código que
**já foi entregue, revisado em Pull Request e mesclado na `main`**, com 38 testes verdes. Eles
não apareceram por análise estática nem por falha de teste: apareceram porque escrever a
especificação do CNPJ obrigou a declarar por escrito *em que ordem* a validação acontece, e
essa declaração tornou visível que o módulo vizinho fazia diferente.

Vale registrar a natureza da coisa: a suíte de CPF não estava incompleta por descuido. Ela
cobria dez casos de entrada inválida. O que faltava era o caso em que a entrada inválida
**contém** uma entrada válida — e esse não é um caso que ocorre a quem escreve os testes junto
com o código, porque quem escreveu os dois tinha o mesmo modelo mental dos dois.

A correção do `cpf.py` **não foi aplicada nesta mudança**. Ela disparou o checkpoint humano
descrito em [`checkpoint-humano.md`](checkpoint-humano.md).
