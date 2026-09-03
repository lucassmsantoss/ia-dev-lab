# Escopo — Atividade de Spec-Driven Development

Documento da Etapa 1: definição das funcionalidades que serão especificadas antes de serem
implementadas, e a justificativa da escolha.

**Projeto:** `ia-dev-lab` — o mesmo iniciado na prática assíncrona da Aula 2.
**Domínio existente no início desta atividade:** validação de documentos brasileiros, com
apenas o CPF implementado.
**Data:** 02/09/2026

---

## Funcionalidade 1 — Validação de CNPJ, incluindo o formato alfanumérico

Validar um CNPJ aceitando tanto o formato numérico tradicional quanto o **formato
alfanumérico**, que a Receita Federal passou a emitir em **31 de julho de 2026**. No formato
novo, as 12 primeiras posições podem conter letras maiúsculas além de dígitos, e apenas os 2
dígitos verificadores finais permanecem numéricos. O cálculo do DV continua sendo módulo 11,
mas cada caractere é convertido para o seu valor na tabela ASCII menos 48 — de modo que
`'0'` vale 0, `'9'` vale 9, `'A'` vale 17 e `'Z'` vale 42.

### Cenários de uso

**Cenário A — Cadastro de fornecedor com CNPJ antigo.** O sistema recebe
`11.222.333/0001-81`, um CNPJ numérico emitido antes da mudança. Ele precisa continuar sendo
aceito indefinidamente: a Receita garantiu que empresas com CNPJ numérico não precisam
atualizá-lo, e os dois formatos coexistem com plena validade legal.

**Cenário B — Cadastro de empresa aberta após julho de 2026.** O sistema recebe
`12.ABC.345/01DE-35`. Uma implementação que só aceite dígitos rejeitaria esse CNPJ como
inválido — e rejeitaria um cliente legítimo.

**Cenário C — Migração de base legada.** Um lote de CNPJs cadastrados ao longo de anos precisa
ser reprocessado, com formatos mistos, com e sem máscara, e alguns registros corrompidos.
A função precisa dar um veredito para cada um sem interromper o processamento.

---

## Funcionalidade 2 — Validação em lote a partir de arquivo CSV

Ler um arquivo CSV contendo documentos, validar cada linha e produzir um relatório com o
total processado, quantos passaram, quantos falharam e o motivo de cada falha. O tipo de
documento é detectado pelo próprio conteúdo — 11 caracteres úteis indicam CPF, 14 indicam
CNPJ — de modo que uma planilha com os dois tipos misturados é processada em uma passada.

### Cenários de uso

**Cenário A — Uso como biblioteca.** Outro módulo do sistema importa a função, passa o caminho
do arquivo e recebe um objeto de resultado para decidir o que fazer. Nada é impresso na tela.

**Cenário B — Uso pela linha de comando.** O operador roda o comando no terminal, vê o resumo
formatado e usa o código de saída do processo para encadear em um script (`0` quando não há
nenhuma falha, diferente de `0` quando há).

**Cenário C — Arquivo problemático.** A planilha veio exportada do Excel no Windows, com BOM
no início, separador `;` em vez de vírgula e uma linha com a coluna faltando. O processamento
não pode quebrar: cada problema vira uma entrada no relatório de erros.

---

## Por que estas funcionalidades são boas candidatas a SDD

**Elas têm regra de negócio externa, não inventada por mim.** O algoritmo do CNPJ alfanumérico
é definido por uma norma da Receita Federal que entrou em vigor há pouco mais de um mês — se a
especificação estiver errada, o código estará errado mesmo passando nos testes que eu mesmo
escrevi, e nenhuma quantidade de refinamento de prompt corrige isso depois. Escrever a spec
primeiro força a decidir *qual é a regra* antes de discutir *como implementá-la*.

**Elas têm casos de borda que não são óbvios até serem escritos.** A coexistência de dois
formatos válidos, sequências repetidas que passam no módulo 11, CSV com BOM, coluna ausente,
separador inesperado. Na Aula 2 ficou demonstrado que o prompt fraco erra justamente onde o
contrato não foi declarado; aqui a spec é o lugar onde esse contrato passa a existir por
escrito, antes de qualquer linha de código.

**Elas mexem em mais de um arquivo e em mais de uma camada.** A F1 acrescenta um módulo de
domínio e seus testes; a F2 acrescenta leitura de arquivo, detecção de tipo, um formato de
relatório e uma interface de linha de comando com código de saída. Não é uma função isolada,
é uma pequena cadeia de decisões — e é aí que um plano de tarefas revisado tem valor real.

**E elas têm dois consumidores com necessidades diferentes.** A mesma validação em lote precisa
servir a um programa que quer um objeto e a uma pessoa que quer um resumo legível no terminal.
Essa tensão entre interfaces é o tipo de decisão que aparece cedo quando se escreve a
especificação, e tarde e caro quando se começa pelo código.

---

## Fora de escopo

Para manter o recorte pequeno e a spec honesta, ficam explicitamente de fora: consulta a
qualquer API externa da Receita Federal (a validação é apenas estrutural, do dígito
verificador, e não verifica se a empresa existe ou está ativa); persistência em banco de dados;
e interface web. A validação diz que o número é *bem formado*, não que ele é *real*.
