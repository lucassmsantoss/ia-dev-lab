# CLAUDE.md — escopo `src/validacao/`

Regra customizada por escopo. Vale **apenas** para os arquivos dentro desta pasta e
tem precedência sobre o `CLAUDE.md` da raiz em caso de conflito.

## Contexto deste escopo

Esta pasta guarda validadores de documentos brasileiros. Cada arquivo cobre um único
documento (`cpf.py`, e futuramente `cnpj.py`, `titulo_eleitor.py`). São funções puras:
recebem uma string, devolvem um booleano, não acessam rede, disco nem variáveis de ambiente.

## Convenções obrigatórias aqui

- Cada validador expõe uma função pública única chamada `validar_<documento>`
  (ex.: `validar_cpf`). Funções auxiliares são privadas, com prefixo `_`.
- A assinatura é sempre `def validar_<documento>(valor: str) -> bool:`.
- A função **normaliza a entrada antes de validar**: remove pontos, traços, barras e
  espaços. `"529.982.247-25"` e `"52998224725"` devem produzir o mesmo resultado.
- Entrada inválida — `None`, string vazia, tamanho errado, caractere não numérico —
  retorna `False`. Nunca levanta exceção.
- Sequências de dígitos repetidos (`"11111111111"`) são rejeitadas, mesmo quando passam
  no cálculo do dígito verificador.
- Nenhum `import` de biblioteca de terceiros. Só biblioteca padrão.
- O cálculo do dígito verificador fica em uma função auxiliar isolada e testável,
  não embutido dentro do `validar_*`.

## Ao gerar ou alterar código aqui

Sempre atualize, na mesma alteração, o teste espelhado em `tests/test_<documento>.py`,
cobrindo no mínimo: um documento válido com máscara, um válido sem máscara, um com
dígito verificador errado, uma sequência repetida, e uma entrada vazia ou nula.
