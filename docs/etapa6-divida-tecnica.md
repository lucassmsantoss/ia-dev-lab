# Etapa 6 (Vá Além) — Opção A: Dívida técnica

## A ferramenta e o comando

`ruff` 0.15.11, rodado sobre o código de produção real do projeto:

```
$ ruff check src/ --select ALL --target-version py39
```

`--select ALL` em vez do conjunto padrão foi deliberado: o comando padrão do `ruff` (sem
`--select`) já passa limpo neste projeto —

```
$ ruff check src/ --target-version py39
All checks passed!
```

— o que era esperado, dado o quanto `CLAUDE.md` já normatiza estilo. Regras "rígidas" (na
linguagem do enunciado) eram necessárias para achar algo real, não cosmético.

## O que o `ruff` apontou

Com `--select ALL`, a maioria dos achados é estilo de docstring (`D401`, `D212`) ou limite de
linha (`E501`) — ruído para este projeto, já que `CLAUDE.md` define suas próprias convenções de
docstring, diferentes das do `pydocstyle`. Um achado, porém, apareceu **duas vezes, em arquivos
diferentes, no mesmo formato**:

```
PLR2004 Magic value used in comparison, consider replacing `2` with a constant variable
  --> src/validacao/cnpj.py:46:25
   |
46 |     return 0 if resto < 2 else 11 - resto
   |

PLR2004 Magic value used in comparison, consider replacing `2` with a constant variable
  --> src/validacao/cpf.py:22:25
   |
22 |     return 0 if resto < 2 else TAMANHO_CPF - resto
   |
```

## O sinal real, por trás do aviso de estilo

O `ruff` está reclamando de um número mágico (`2`), mas ler as duas ocorrências lado a lado
mostra algo maior do que isso: **é a mesma linha de código, duas vezes**. `_calcular_digito` de
`cpf.py` e a função equivalente em `cnpj.py` implementam a regra de arredondamento do módulo 11
— "resto menor que 2 vira 0, senão é o módulo menos o resto" — cada uma com sua própria cópia:

```python
# cpf.py
resto = soma % TAMANHO_CPF          # TAMANHO_CPF = 11
return 0 if resto < 2 else TAMANHO_CPF - resto

# cnpj.py
resto = soma % 11
return 0 if resto < 2 else 11 - resto
```

Isso é dívida técnica no sentido literal: não é um bug hoje (os dois módulos têm 49 e 50 testes
passando, respectivamente), é um **empréstimo contra manutenção futura**. Se a regra do
dígito verificador módulo 11 precisasse mudar — por exemplo, se a Receita Federal alterasse o
critério de arredondamento, do mesmo jeito que introduziu o CNPJ alfanumérico em julho de 2026
— a mudança precisaria ser feita em dois lugares, e nada no projeto avisa se alguém mudar um e
esquecer o outro. Os testes de cada arquivo só verificam o próprio arquivo; nenhum teste
verifica que os dois concordam.

## Proposta de mitigação — e por que não é óbvia

A mitigação técnica é simples: extrair uma função privada compartilhada,
`_ajustar_resto_modulo11(resto: int, modulo: int) -> int`. O que não é simples é **onde ela
mora**, porque `CLAUDE.md` proíbe explicitamente pastas por tipo técnico (`utils/`, `helpers/`,
`common/`), e um helper matemático compartilhado é candidato natural a exatamente esse tipo de
pasta.

Três opções avaliadas:

1. **Criar `src/validacao/_comum.py`.** Resolve a duplicação, mas é, na prática, um `utils.py`
   com nome diferente — a convenção do projeto não proíbe pelo nome do arquivo, proíbe pelo
   papel que ele exerce, e esse papel seria o mesmo.
2. **Um dos dois arquivos importa a função do outro** (ex.: `cnpj.py` importa
   `_calcular_digito`-o-suficiente de `cpf.py`). Rejeitada: criaria uma dependência entre dois
   módulos que hoje são folhas independentes (ver `docs/etapa4-arquitetura.md`) só para uma
   função utilitária, invertendo a árvore de dependências por conveniência.
3. **Manter a duplicação, mas eliminar o risco de divergência silenciosa com um teste de
   equivalência** — um teste novo, fora dos dois arquivos, que chama as duas implementações do
   ajuste de módulo com a mesma faixa de entradas e afirma que produzem o mesmo resultado.
   **Recomendação.** Não elimina a duplicação, mas elimina exatamente o risco que a duplicação
   cria: hoje, se alguém mudar uma cópia e esquecer a outra, nenhum teste percebe. Com o teste
   de equivalência, a divergência vira um teste vermelho, não um bug silencioso — e o projeto
   não precisa decidir uma exceção à sua própria convenção de pastas para resolver isso.

A opção 3 foi a implementada nesta atividade (ver commit correspondente e
`tests/test_equivalencia_modulo11.py`).
