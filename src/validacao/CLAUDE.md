# CLAUDE.md — escopo `src/validacao/`

Regra customizada por escopo. Vale **apenas** para os arquivos dentro desta pasta e
tem precedência sobre o `CLAUDE.md` da raiz em caso de conflito.

## Contexto deste escopo

Esta pasta guarda o domínio de validação de documentos brasileiros, e tem **dois tipos de
arquivo com regras diferentes**.

**Validadores puros** — `cpf.py`, `cnpj.py`, e futuramente `titulo_eleitor.py`. Cada arquivo
cobre um único documento. São funções puras: recebem uma string, devolvem um booleano, não
acessam rede, disco nem variáveis de ambiente. As convenções da seção seguinte valem para eles.

**Orquestradores** — hoje apenas `lote.py`, que lê arquivos CSV e aplica os validadores a
cada linha. Ele é serviço de aplicação, não domínio: pode acessar disco, expor mais de uma
função pública e ter interface de linha de comando. Suas regras estão em
"Convenções dos orquestradores", mais abaixo. Um orquestrador **nunca** contém regra de
validação própria — ele chama os validadores puros.

Apenas os validadores puros são exportados em `__init__.py`. Quem importa `src.validacao` para
validar um documento não deve receber junto uma função que abre arquivos.

## Convenções obrigatórias dos validadores puros

- Cada validador expõe uma função pública única chamada `validar_<documento>`
  (ex.: `validar_cpf`). Funções auxiliares são privadas, com prefixo `_`.
- A assinatura é sempre `def validar_<documento>(valor: str) -> bool:`.
- A função **normaliza a entrada antes de validar**: remove os caracteres de formatação
  `.`, `/`, `-` e espaços, e converte letras para maiúsculas. `"529.982.247-25"` e
  `"52998224725"` devem produzir o mesmo resultado, assim como `"12abc34501de35"` e
  `"12ABC34501DE35"`.
- A normalização remove **apenas caracteres de formatação**, nunca "tudo que não é dígito".
  Um caractere inesperado precisa sobreviver à normalização para ser **rejeitado** pela
  checagem de conjunto — descartá-lo silenciosamente faz `"52998224725abc"` virar um
  documento válido.
- Depois de normalizar, valide o **conjunto de caracteres** antes de qualquer conversão
  numérica. Nunca use `str.isdigit()` para isso: ele é verdadeiro para `"²"` e para
  dígitos indo-arábicos, que não pertencem ao documento. Compare contra `"0123456789"`.
- Entrada inválida — `None`, string vazia, tamanho errado, caractere fora do conjunto
  permitido — retorna `False`. Nunca levanta exceção.
- Sequências formadas por um único caractere repetido (`"11111111111"`) são rejeitadas,
  mesmo quando passam no cálculo do dígito verificador. A checagem incide sobre as posições
  anteriores aos dígitos verificadores, tomadas em conjunto — nunca sobre o documento
  inteiro, e nunca por "predominância" de um caractere: `00.000.000/0001-91` é a inscrição
  real do Banco do Brasil e precisa continuar válida.
- Nenhum `import` de biblioteca de terceiros. Só biblioteca padrão.
- O cálculo do dígito verificador fica em uma função auxiliar isolada e testável,
  não embutido dentro do `validar_*`.
- Constantes vindas de norma externa (pesos, tabelas de conversão) são **transcritas
  literalmente**, não geradas por laço. Ver `design.md` da mudança `add-validacao-cnpj`.

## Convenções dos orquestradores

- Nenhuma regra de validação vive aqui. O orquestrador decide **qual** validador chamar; ele
  não decide se um documento é válido.
- A leitura de arquivo e a formatação para a tela ficam separadas: uma função devolve dados,
  outra os apresenta. Isso é o que permite usar o módulo como biblioteca e como comando.
- `print()` é permitido apenas na camada de linha de comando, nunca nas funções de dados.
- Códigos de saída seguem o contrato: `0` sucesso, `1` há documentos inválidos, `2` não foi
  possível executar. Alterar esse contrato exige o checkpoint humano — scripts de terceiros
  dependem dele.
- Erros de execução (arquivo ausente, coluna inexistente) são exceções próprias e nomeadas,
  não valores de retorno. A regra de "nunca levantar exceção" vale para os validadores puros,
  onde entrada malformada é um resultado; aqui, não conseguir abrir o arquivo não é resultado
  nenhum.

## Ao gerar ou alterar código aqui

Sempre atualize, na mesma alteração, o teste espelhado em `tests/test_<documento>.py`,
cobrindo no mínimo: um documento válido com máscara, um válido sem máscara, um com
dígito verificador errado, uma sequência repetida, e uma entrada vazia ou nula.
