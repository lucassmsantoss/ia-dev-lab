# Proposta — Validação de CNPJ com suporte ao formato alfanumérico

## User story

> Como sistema que cadastra empresas, preciso saber se um CNPJ informado é um número
> bem formado, aceitando tanto os CNPJs que já existem hoje quanto os que a Receita Federal
> passou a emitir com letras, para que eu não recuse o cadastro de uma empresa legítima nem
> aceite um número digitado errado.

A história está escrita em termos de comportamento observável. Ela não diz em qual arquivo o
código mora, qual é o nome ou a assinatura da função, nem como o dígito verificador é
calculado — essas são decisões técnicas e ficam em `design.md`.

## Contexto e motivação

Em **31 de julho de 2026** a Receita Federal começou a emitir CNPJ no formato alfanumérico.
O documento continua tendo 14 caracteres, mas as 12 primeiras posições passaram a aceitar
letras maiúsculas além de dígitos; apenas os 2 dígitos verificadores finais permanecem
numéricos. Os CNPJs numéricos emitidos antes disso continuam válidos por prazo indeterminado,
sem necessidade de atualização, de modo que os dois formatos coexistem.

A consequência prática é que qualquer validação escrita antes de julho de 2026 — inclusive a
que a maioria dos exemplos e bibliotecas ainda ensina — **rejeita como inválido um CNPJ
legítimo** de qualquer empresa aberta a partir dessa data.

Esta é a razão de a funcionalidade ser um bom caso para SDD: a regra não pode ser inferida do
código existente nem adivinhada por um modelo a partir do conhecimento geral sobre CNPJ. Ela
precisa ser pesquisada, decidida e escrita antes — porque um código que implementa a regra
errada passa em todos os testes que ele mesmo trouxe junto.

## Escopo

O que esta mudança entrega:

- Validação estrutural de CNPJ, aceitando os formatos numérico e alfanumérico.
- Tolerância à máscara de formatação (`AA.AAA.AAA/AAAA-DD`) e a espaços.
- Rejeição de entradas malformadas sem interromper a execução do programa chamador.
- Testes cobrindo os dois formatos e os casos de borda descritos na especificação.

## Não-objetivos

- **Não** consulta nenhuma API da Receita Federal. A validação é estrutural: responde se o
  número é bem formado, não se a empresa existe, está ativa ou é de determinado ramo.
- **Não** gera CNPJs. Não há função de criação de documento válido em código de produção.
- **Não** formata nem aplica máscara — isso é responsabilidade de outra funcionalidade.
- **Não** altera o comportamento existente da validação de CPF.
- **Não** trata Inscrição Estadual, CAEPF, CNO ou qualquer outro cadastro.

## Impacto

Módulo novo dentro do domínio de validação já existente. Nenhuma assinatura pública atual
muda, e nenhum teste atual precisa ser reescrito — a suíte de CPF deve continuar passando
integralmente após a mudança.
