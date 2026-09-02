# Especificação — Validação de CNPJ

## Purpose

Definir o comportamento observável da validação estrutural de CNPJ no domínio de validação de
documentos, cobrindo os dois formatos hoje em circulação: o numérico, emitido até julho de
2026, e o alfanumérico, emitido a partir de 31/07/2026.

## ADDED Requirements

### Requirement: Validação de CNPJ no formato numérico

O sistema SHALL aceitar como válido um CNPJ de 14 dígitos cujos dois dígitos verificadores
correspondam ao resultado do cálculo módulo 11 sobre as 12 primeiras posições, e SHALL
rejeitar qualquer CNPJ cujos dígitos verificadores não correspondam.

#### Scenario: CNPJ numérico válido sem máscara

- **GIVEN** o CNPJ `11222333000181`, emitido antes da mudança de formato
- **WHEN** ele é submetido à validação
- **THEN** o resultado é verdadeiro

#### Scenario: CNPJ numérico com dígito verificador incorreto

- **GIVEN** o CNPJ `11222333000182`, idêntico ao anterior exceto pelo último dígito
- **WHEN** ele é submetido à validação
- **THEN** o resultado é falso

### Requirement: Validação de CNPJ no formato alfanumérico

O sistema SHALL aceitar como válido um CNPJ cujas 12 primeiras posições contenham dígitos ou
letras de `A` a `Z` e cujas 2 últimas posições sejam numéricas e correspondam ao cálculo do
dígito verificador, no qual cada caractere vale o seu código ASCII menos 48.

#### Scenario: CNPJ alfanumérico válido

- **GIVEN** o CNPJ `12ABC34501DE35`, no formato emitido a partir de 31/07/2026
- **WHEN** ele é submetido à validação
- **THEN** o resultado é verdadeiro
- **AND** o mesmo número com máscara, `12.ABC.345/01DE-35`, produz idêntico resultado

#### Scenario: Letra em posição de dígito verificador

- **GIVEN** o CNPJ `12ABC34501DE3X`, cujas 12 primeiras posições são válidas mas cujo último
  caractere é uma letra
- **WHEN** ele é submetido à validação
- **THEN** o resultado é falso, porque as posições 13 e 14 SHALL ser sempre numéricas

### Requirement: Tolerância a máscara, espaços e caixa

O sistema SHALL normalizar a entrada antes de validar, descartando os caracteres de formatação
`.`, `/`, `-` e espaços, e convertendo letras minúsculas para maiúsculas.

#### Scenario: Mesma entrada com e sem formatação

- **GIVEN** as entradas `11.222.333/0001-81`, `11222333000181` e ` 11 222 333 0001 81 `
- **WHEN** cada uma é submetida à validação
- **THEN** todas produzem o mesmo resultado verdadeiro

#### Scenario: CNPJ alfanumérico digitado em minúsculas

- **GIVEN** o CNPJ `12abc34501de35`, digitado em um formulário sem trava de caixa
- **WHEN** ele é submetido à validação
- **THEN** o resultado é verdadeiro, porque a caixa das letras não faz parte da identidade do
  documento

### Requirement: Rejeição de sequências de caracteres idênticos

O sistema SHALL rejeitar qualquer CNPJ cujas 12 primeiras posições sejam compostas por um único
caractere repetido, ainda que o resultado satisfaça o cálculo do dígito verificador.

#### Scenario: Sequência repetida que passa no módulo 11

- **GIVEN** o CNPJ `11111111111180`, cujos dígitos verificadores são aritmeticamente corretos
- **WHEN** ele é submetido à validação
- **THEN** o resultado é falso, porque a sequência não corresponde a nenhuma inscrição real

#### Scenario: CNPJ legítimo com muitos zeros — caso de borda próprio

- **GIVEN** o CNPJ `00000000000191`, que é a inscrição real do Banco do Brasil
- **WHEN** ele é submetido à validação
- **THEN** o resultado é verdadeiro
- **AND** a regra de sequência repetida SHALL considerar apenas as 12 primeiras posições
  tomadas em conjunto, e não a mera predominância de um caractere

> Este cenário existe porque a implementação ingênua da regra anterior — rejeitar entradas
> "cheias de zeros", ou aplicar a checagem sobre as 14 posições — invalidaria o CNPJ de uma das
> maiores instituições do país. A regra correta é que as 12 primeiras posições não podem ser
> **todas** iguais; `000000000001` contém um `1` e portanto passa.

### Requirement: Ausência de exceções para entrada malformada

O sistema SHALL retornar falso, e NUNCA levantar exceção, para qualquer entrada que não seja
um CNPJ bem formado, incluindo valor nulo, texto vazio, tamanho incorreto, tipo diferente de
texto e caracteres fora do conjunto permitido.

#### Scenario: Entrada nula ou de outro tipo

- **GIVEN** as entradas `None`, `11222333000181` como número inteiro e uma lista vazia
- **WHEN** cada uma é submetida à validação
- **THEN** todas retornam falso
- **AND** nenhuma interrompe a execução do programa chamador

#### Scenario: Tamanho incorreto e caractere não permitido

- **GIVEN** as entradas `1122233300018` (13 posições), `112223330001812` (15 posições) e
  `12ABÇ34501DE35` (contendo `Ç`, fora do intervalo A–Z)
- **WHEN** cada uma é submetida à validação
- **THEN** todas retornam falso

### Requirement: Preservação do comportamento existente

O sistema SHALL manter inalterado o comportamento da validação de CPF já existente no projeto.

#### Scenario: Suíte de CPF permanece verde

- **GIVEN** a suíte de testes de CPF com 38 casos, verde antes desta mudança
- **WHEN** a validação de CNPJ é adicionada ao domínio
- **THEN** os 38 casos continuam passando sem qualquer alteração no arquivo de testes
