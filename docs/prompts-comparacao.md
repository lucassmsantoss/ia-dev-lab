# Comparativo: prompt fraco x prompt eficaz

**Funcionalidade escolhida:** validação de CPF (`src/validacao/cpf.py`).

Escolhi essa funcionalidade porque a regra de negócio é pequena mas tem casos de borda
conhecidos — máscara, dígitos repetidos, entrada malformada. Isso permite medir a diferença
entre os dois prompts com um critério objetivo (quantos casos passam), em vez de julgar
"qual código ficou mais bonito".

**Modelo usado no experimento principal:** Claude Opus 5 (via Claude Cowork), em 27/08/2026.
O modelo tinha acesso ao repositório, incluindo `CLAUDE.md` e `src/validacao/CLAUDE.md`.

---

## 1. Prompt fraco

Uma frase genérica, sem contexto, sem exemplo e sem critério de aceitação.

> Faz uma função que valida CPF.

### Resposta gerada

```python
def valida_cpf(cpf):
    if len(cpf) != 11:
        return False

    soma = 0
    for i in range(9):
        soma += int(cpf[i]) * (10 - i)
    resto = 11 - (soma % 11)
    if resto == 10 or resto == 11:
        resto = 0
    if resto != int(cpf[9]):
        return False

    soma = 0
    for i in range(10):
        soma += int(cpf[i]) * (11 - i)
    resto = 11 - (soma % 11)
    if resto == 10 or resto == 11:
        resto = 0
    if resto != int(cpf[10]):
        return False

    return True
```

O código não está errado no cálculo dos dígitos verificadores — está errado no **contrato**.
Ele assume que a entrada sempre chega limpa, e não há como o modelo saber que isso é falso,
porque ninguém disse.

---

## 2. Prompt eficaz

O mesmo pedido, reescrito com os quatro elementos.

> **Contexto:** No repositório `ia-dev-lab`, crie o validador de CPF em `src/validacao/cpf.py`.
> A pasta `src/validacao/` tem um `CLAUDE.md` com regras de escopo que valem para este arquivo:
> leia antes de escrever. É um módulo de domínio, sem I/O, consumido por outras partes do sistema.
>
> **Exemplo de padrão a seguir:** a função pública deve ter a assinatura
> `def validar_cpf(valor: str) -> bool:`, com o cálculo do dígito verificador extraído em uma
> função auxiliar privada e testável isoladamente, no padrão
> `def _calcular_digito(digitos: str) -> int:`. Docstring curta em português dizendo o que a
> função garante.
>
> **Restrições:** (1) só biblioteca padrão, nenhum pacote de validação pronto;
> (2) normalizar a entrada antes de validar — `"529.982.247-25"` e `"52998224725"` devem dar o
> mesmo resultado; (3) nunca levantar exceção: entrada nula, vazia, curta, longa ou com
> caracteres não numéricos retorna `False`; (4) rejeitar sequências de dígitos iguais como
> `"11111111111"`, mesmo que passem no cálculo do dígito verificador.
>
> **Como validar o resultado:** gere junto o arquivo `tests/test_cpf.py` cobrindo, no mínimo:
> CPF válido com máscara, válido sem máscara, dígito verificador errado, cada uma das dez
> sequências repetidas, entrada vazia, entrada não-string e entrada com letras. Todos os testes
> devem passar com `python -m pytest tests/test_cpf.py -v`.

### Resposta gerada

```python
"""Validação de CPF (Cadastro de Pessoas Físicas)."""

import sys

TAMANHO_CPF = 11


def _somente_digitos(valor: str) -> str:
    """Remove qualquer caractere que não seja dígito, preservando a ordem."""
    return "".join(caractere for caractere in valor if caractere.isdigit())


def _calcular_digito(digitos: str) -> int:
    """Calcula um dígito verificador de CPF a partir dos dígitos anteriores.

    Recebe 9 dígitos para calcular o primeiro verificador ou 10 para o segundo.
    """
    peso_inicial = len(digitos) + 1
    soma = sum(int(digito) * (peso_inicial - posicao)
               for posicao, digito in enumerate(digitos))
    resto = soma % TAMANHO_CPF
    return 0 if resto < 2 else TAMANHO_CPF - resto


def validar_cpf(valor: str) -> bool:
    """Informa se `valor` é um CPF válido.

    Aceita o número com ou sem máscara. Qualquer entrada malformada — nula, vazia,
    com tamanho incorreto, sem dígitos suficientes ou com todos os dígitos iguais —
    resulta em False, nunca em exceção.
    """
    if not isinstance(valor, str):
        return False

    digitos = _somente_digitos(valor)

    if len(digitos) != TAMANHO_CPF:
        return False

    if len(set(digitos)) == 1:
        return False

    primeiro = _calcular_digito(digitos[:9])
    segundo = _calcular_digito(digitos[:10])

    return digitos[9] == str(primeiro) and digitos[10] == str(segundo)
```

O arquivo `tests/test_cpf.py` foi gerado na mesma resposta. Executado no ambiente do projeto
(Anaconda, Python 3.9.12, pytest 7.1.1), ele coleta **38 casos e todos passam**:

```
$ python -m pytest tests/test_cpf.py -v
platform win32 -- Python 3.9.12, pytest-7.1.1, pluggy-1.0.0
rootdir: C:\Users\lucas\Documents\ia-dev-lab
collected 38 items
...
======================== 38 passed in 0.20s ========================
```

---

## 3. Resultado medido

Os mesmos dez casos foram executados contra as duas versões:

| Caso | Entrada | Esperado | Prompt fraco | Prompt eficaz |
| --- | --- | --- | --- | --- |
| CPF válido sem máscara | `52998224725` | `True` | `True` ✅ | `True` ✅ |
| CPF válido com máscara | `529.982.247-25` | `True` | `False` ❌ | `True` ✅ |
| Outro válido com máscara | `111.444.777-35` | `True` | `False` ❌ | `True` ✅ |
| Dígito verificador errado | `52998224724` | `False` | `False` ✅ | `False` ✅ |
| Dígitos repetidos | `11111111111` | `False` | `True` ❌ | `False` ✅ |
| Sequência de zeros | `00000000000` | `False` | `True` ❌ | `False` ✅ |
| String vazia | `""` | `False` | `False` ✅ | `False` ✅ |
| Entrada nula | `None` | `False` | `TypeError` ❌ | `False` ✅ |
| Letras no lugar de números | `abcdefghijk` | `False` | `ValueError` ❌ | `False` ✅ |
| Número curto demais | `5299822472` | `False` | `False` ✅ | `False` ✅ |

**Prompt fraco: 4 de 10 casos corretos. Prompt eficaz: 10 de 10.**

## 4. Análise das diferenças

O prompt fraco não gerou código *errado*, gerou código com o **contrato errado**: a matemática
dos dígitos verificadores está correta nas duas versões, e toda a diferença de 6 casos vem de
suposições que o modelo teve de inventar porque o prompt não as fixou.

As três falhas mais graves não são estéticas, são de segurança do software. Um CPF com máscara
sendo rejeitado é um falso negativo que qualquer formulário real produziria; `"11111111111"`
sendo aceito é um **falso positivo**, o pior tipo de bug em validador, e ele passa despercebido
porque o número de fato satisfaz o cálculo do dígito; e as exceções em `None` e em texto com
letras transformam um dado ruim do usuário em erro 500 do sistema chamador.

O elemento do prompt que mais rendeu resultado foi a **restrição**, não o exemplo: cada uma das
quatro restrições eliminou exatamente uma classe de falha. O exemplo de padrão mudou a forma do
código (nome, assinatura, tipagem, função auxiliar isolada), o que ajuda na manutenção, mas
sozinho não teria corrigido nenhum dos seis casos.

A diferença mais importante, porém, é a **forma de validar**. Ao pedir os testes junto com a
implementação, o resultado deixou de ser uma opinião sobre qualidade e passou a ser um número
verificável — e são esses testes que continuarão protegendo a função quando ela for alterada
no futuro, por mim ou por outro prompt.

Um detalhe que vale registrar: boa parte do "prompt eficaz" já estava escrita no
`src/validacao/CLAUDE.md` da Etapa 2. Com o arquivo de contexto no lugar, o mesmo resultado se
obtém com um pedido bem mais curto — o contexto deixa de ser digitado a cada vez e passa a ser
versionado no repositório.

---

## 5. Repetição com modelo de menor performance

> **Status: pendente de execução.**

Para completar a tarefa 5 da Etapa 4, o mesmo par de prompts deve ser repetido em um modelo de
menor performance, registrando o resultado abaixo.

- **Ferramenta / modelo:** *(a preencher — ex.: GitHub Copilot no VS Code, modelo padrão)*
- **Data:** *(a preencher)*

### Resposta ao prompt fraco

```python
# (colar aqui o código gerado)
```

### Resposta ao prompt eficaz

```python
# (colar aqui o código gerado)
```

### Observações

*(A preencher. Pontos que valem comparação: o modelo menor obedeceu à assinatura pedida?
Normalizou a máscara? Rejeitou dígitos repetidos? Gerou os testes junto? Precisou de mais de
uma tentativa? Uma hipótese razoável é que a distância entre os dois prompts seja **maior** no
modelo menor, já que ele depende mais das instruções explícitas e menos de suposições próprias
sobre o domínio.)*
