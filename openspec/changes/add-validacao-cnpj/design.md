# Design — Validação de CNPJ

Decisões técnicas desta mudança. A proposta e a especificação descrevem *o quê*; este
documento registra *como* e, principalmente, **o que foi descartado e por quê**.

## D1 — Um módulo por documento, sem refatorar o CPF

**Decisão:** criar `src/validacao/cnpj.py` como módulo independente, sem tocar em
`src/validacao/cpf.py`.

**Alternativa descartada:** extrair um módulo comum (`src/validacao/_modulo11.py`) com o
cálculo de dígito verificador compartilhado entre CPF e CNPJ, já que ambos usam módulo 11.

**Por quê:** a semelhança é superficial. O CPF usa pesos decrescentes contínuos (10..2 e 11..2)
sobre dígitos; o CNPJ usa um ciclo de 2 a 9 que reinicia, sobre caracteres alfanuméricos
convertidos por ASCII. Uma função comum precisaria receber pesos, tabela de conversão e
tamanho como parâmetros — ou seja, a abstração teria mais configuração do que corpo. Além
disso, refatorar `cpf.py` colocaria em risco 38 testes que hoje passam, em troca de economizar
cerca de seis linhas. A regra em `src/validacao/CLAUDE.md` já determina um arquivo por
documento; esta decisão a respeita.

**Consequência assumida:** há duplicação conceitual entre os dois módulos. Se um terceiro
documento com módulo 11 entrar no projeto, a extração passa a valer a pena e deve ser
reavaliada — três consumidores justificam a abstração que dois não justificam.

## D2 — Conversão de caractere por ASCII menos 48

**Decisão:** `valor = ord(caractere) - 48`, aplicado uniformemente a dígitos e letras.

**Alternativa descartada:** um dicionário explícito mapeando `'0'..'9'` e `'A'..'Z'` para seus
valores.

**Por quê:** a conversão por ASCII é literalmente a regra publicada pela Receita Federal, não
uma otimização. Escrever um dicionário de 36 entradas seria transcrever a mesma regra em
formato mais longo e mais sujeito a erro de digitação. O risco da fórmula — aceitar
silenciosamente caracteres fora de `0-9A-Z`, como `:` (ASCII 58, valor 10) — é eliminado pela
validação de conjunto de caracteres que ocorre **antes** da conversão.

## D3 — Pesos escritos explicitamente, não gerados por laço

**Decisão:** declarar os pesos como listas literais no módulo:
`[5,4,3,2,9,8,7,6,5,4,3,2]` para o primeiro dígito e `[6,5,4,3,2,9,8,7,6,5,4,3,2]` para o
segundo.

**Alternativa descartada:** gerar a sequência por um laço que cicla de 2 a 9.

**Por quê:** esta decisão veio de um erro real cometido durante a preparação desta mudança. A
primeira tentativa gerou os pesos por laço e fez o ciclo retornar a **3** depois do 9, em vez
de retornar a **2**. O código rodava, era mais curto e parecia elegante — e produzia dígitos
verificadores errados para todos os CNPJs. O erro só apareceu ao conferir contra inscrições
reais conhecidas. Uma lista literal é conferível a olho contra a documentação da Receita; um
laço precisa ser mentalmente executado. Onde a constante vem de norma externa, transcrever é
mais seguro que derivar.

**Mitigação adicional:** um teste fixa os dois vetores de pesos, de modo que qualquer alteração
futura quebre imediatamente.

## D4 — Validar o conjunto de caracteres antes de calcular

**Decisão:** a ordem de checagem é: tipo é texto → normalizar (remover formatação, converter
para maiúsculas) → comprimento é 14 → posições 1–12 estão em `0-9A-Z` → posições 13–14 são
numéricas → as 12 primeiras não são todas iguais → conferir dígitos verificadores.

**Por quê:** cada passo pressupõe o anterior. Calcular o dígito antes de validar o conjunto de
caracteres é o que transforma entrada malformada em exceção — precisamente o que a
especificação proíbe. A ordem é parte do contrato, não detalhe de implementação.

## D5 — Normalizar caixa, mas não acentuação

**Decisão:** `.upper()` é aplicado à entrada; nenhuma transliteração de acentos é feita.

**Por quê:** a caixa não faz parte da identidade do documento — `12abc34501de35` e
`12ABC34501DE35` são o mesmo CNPJ digitado por pessoas diferentes. Já um `Ç` ou um `Á` não são
variações de caixa: são caracteres que a norma não permite, e aceitá-los por transliteração
inventaria uma regra que a Receita não escreveu.

## D6 — Escopo da regra de sequência repetida

**Decisão:** a checagem considera apenas as **12 primeiras posições**, e exige que sejam todas
iguais entre si para rejeitar.

**Por quê:** aplicar a checagem sobre as 14 posições, ou usar uma heurística de "predominância"
de um caractere, invalidaria `00000000000191` — o CNPJ real do Banco do Brasil. Este é o caso
de borda registrado na especificação, e a decisão de escopo existe para atendê-lo.
