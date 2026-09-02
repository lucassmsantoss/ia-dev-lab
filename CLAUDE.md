# CLAUDE.md

Arquivo de contexto do projeto para agentes de IA (Claude Code / Copilot).
Leia este arquivo antes de propor qualquer alteração no repositório.

## Sobre o projeto

O `ia-dev-lab` é um laboratório de desenvolvimento assistido por IA, criado para a
disciplina *Tópicos Avançados em Engenharia de Software 2* do mestrado em TI (PPgTI/IMD-UFRN).
O objetivo não é entregar um produto, e sim exercitar um fluxo de trabalho: configurar o
ambiente, dar contexto explícito à IA, organizar o projeto por domínio e integrar tudo a
Git/GitHub com revisão humana.

O domínio escolhido para os exercícios é **validação de documentos brasileiros**, começando
pela validação de CPF. É um problema pequeno, com regra de negócio verificável, o que permite
comparar objetivamente a qualidade do código gerado por prompts diferentes.

## Comandos

- `python -m pytest` -> roda toda a suíte de testes
- `python -m pytest tests/test_cpf.py -v` -> roda só os testes de CPF, com detalhe de cada caso
- `python -m pytest --cov=src` -> roda os testes com relatório de cobertura
- `python -m src.validacao.cpf <numero>` -> valida um CPF pela linha de comando
- `python hello.py` -> script de verificação inicial do ambiente (Etapa 1 da atividade)
- `pip install -r requirements.txt` -> instala as dependências de desenvolvimento

> No Windows com Anaconda, rode os comandos pelo **Anaconda Prompt** (ou pelo PowerShell após
> `conda init powershell`). Chamar `anaconda3\python.exe` pelo caminho completo quebra o
> `import ssl`, porque o `Library\bin` não entra no PATH sem a ativação do ambiente.

## Convenções de código

- Python 3.9+, seguindo a PEP 8 com linhas de no máximo 100 caracteres. O ambiente de
  referência do projeto é o Anaconda com Python 3.9.12 no Windows — não usar sintaxe
  posterior ao 3.9 (`match`, `int | None`, `tomllib`) sem antes atualizar esta linha.
- Organização por **domínio**, não por tipo técnico: o código de validação vive em
  `src/validacao/`, não em uma pasta genérica `utils/` ou `helpers/`.
- Todo módulo em `src/` tem um arquivo de teste espelhado em `tests/`, com o prefixo `test_`.
- Funções públicas levam *type hints* e docstring curta, em português, explicando **o que** a
  função garante — não como ela faz.
- Funções de validação retornam `bool` e nunca lançam exceção para entrada inválida:
  entrada malformada é um resultado `False`, não um erro.
- Mensagens de commit em português, no imperativo e descrevendo o efeito
  (ex.: `Adiciona validação de dígitos verificadores do CPF`).
- Nomes de variáveis e funções em português quando representam conceitos do domínio
  (`cpf`, `digito_verificador`), em inglês quando são termos técnicos genéricos (`index`, `parse`).

## Não fazer

- Não instalar bibliotecas externas para resolver o que a biblioteca padrão já resolve —
  em especial, não usar pacotes de validação de CPF prontos: a regra tem que estar no código.
- Não criar pastas por tipo técnico (`utils/`, `helpers/`, `common/`, `misc/`).
- Não commitar direto na `main`: toda alteração passa por branch e Pull Request.
- Não usar `print()` para depuração dentro de `src/` — o retorno da função é a interface.
- Não gerar código sem o teste correspondente em `tests/`.
- Não reescrever arquivos inteiros quando a mudança pedida for pontual.
- Não aceitar mensagem de commit gerada por IA sem revisar antes o `git diff`.
