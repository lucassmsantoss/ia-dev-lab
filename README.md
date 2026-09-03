# ia-dev-lab

Laboratório de desenvolvimento de software assistido por IA, criado para a disciplina
**Tópicos Avançados em Engenharia de Software 2** do Mestrado em Tecnologia da Informação
(PPgTI / Instituto Metrópole Digital — UFRN).

## Visão geral

O objetivo do repositório não é entregar um produto, e sim exercitar um **fluxo de trabalho**
com IA: configurar o ambiente, dar contexto explícito ao agente (`CLAUDE.md`), organizar o
código por domínio, comparar a qualidade de prompts diferentes e integrar tudo a Git/GitHub
com revisão humana antes do merge.

O domínio usado nos exercícios é a **validação de documentos brasileiros** — hoje, CPF e CNPJ.
É um problema deliberadamente pequeno, mas com regra de negócio verificável, o que permite
comparar de forma objetiva o resultado de abordagens diferentes.

A validação de CNPJ aceita os **dois formatos em circulação**: o numérico, emitido até julho de
2026, e o alfanumérico, emitido pela Receita Federal a partir de 31/07/2026, no qual as 12
primeiras posições podem conter letras e apenas os dígitos verificadores permanecem numéricos.
Os dois formatos coexistem com validade indeterminada.

## Estrutura

```
ia-dev-lab/
|-- CLAUDE.md                  # contexto do projeto para o agente de IA
|-- README.md
|-- .mcp.json                  # servidores MCP do projeto (Etapa 5)
|-- .gitignore
|-- requirements.txt
|-- hello.py                   # script de verificação do ambiente (Etapa 1)
|-- docs/
|   |-- adr/
|   |   `-- 0001-escolha-da-ferramenta-de-ia.md
|   |-- prompts-comparacao.md        # prompt fraco vs. prompt eficaz
|   |-- mcp-configuracao.md          # passo a passo e obstáculos do MCP
|   |-- relatorio-final.md/.pdf      # relatório da 1a atividade
|   |-- escopo.md                    # funcionalidades escolhidas para SDD
|   |-- spec-lote-csv.md             # spec manual da validação em lote
|   |-- comparacao-abordagens-sdd.md # OpenSpec vs. Markdown manual
|   `-- relatorio-sdd.md/.pdf        # relatório da 2a atividade
|-- openspec/                  # artefatos de Spec-Driven Development
|   |-- config.yaml
|   `-- changes/
|       `-- add-validacao-cnpj/
|           |-- proposal.md
|           |-- design.md
|           |-- tasks.md
|           |-- revisao-do-plano.md
|           |-- revisao-dos-diffs.md
|           |-- checkpoint-humano.md
|           `-- specs/validacao-cnpj/spec.md
|-- src/
|   `-- validacao/             # domínio: validação de documentos
|       |-- CLAUDE.md          # regra customizada com escopo nesta pasta
|       |-- __init__.py
|       |-- cpf.py
|       |-- cnpj.py
|       `-- lote.py            # validação em lote a partir de CSV
`-- tests/
    |-- __init__.py
    |-- test_cpf.py
    |-- test_cnpj.py
    `-- test_lote.py
```

As pastas são organizadas por **domínio** (`validacao`), não por tipo técnico. Não existe
`utils/` nem `helpers/`: foi assim que a validação de CNPJ entrou, ao lado do CPF, e é assim
que entrará a próxima — a de Título de Eleitor, por exemplo.

## Instalação

Requer Python 3.9 ou superior e Git. O ambiente de referência é o Anaconda com Python 3.9.12
no Windows, que já traz o `pytest` instalado.

```bash
git clone https://github.com/lucassmsantoss/ia-dev-lab.git
cd ia-dev-lab
```

**Com Anaconda (ambiente de referência):** abra o **Anaconda Prompt** e rode os comandos a
partir da pasta do projeto. O `pytest` já vem instalado; só o `pytest-cov`, usado no relatório
de cobertura, precisa ser adicionado (`pip install pytest-cov`).

**Com Python padrão:** crie um ambiente virtual e instale as dependências.

```powershell
# Windows (PowerShell)
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

```bash
# Linux / macOS
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

> **Windows, atenção:** rode sempre por um terminal com o ambiente ativado. Chamar
> `anaconda3\python.exe` pelo caminho completo faz o `pytest` falhar com
> `ImportError: DLL load failed while importing _ssl`, porque as DLLs do OpenSSL ficam em
> `anaconda3\Library\bin`, que só entra no PATH durante a ativação. Se o comando `python`
> abrir a Microsoft Store, desative os *aliases de execução* em
> Configurações → Aplicativos → Configurações avançadas de aplicativo.

## Comandos principais

| Comando | O que faz |
| --- | --- |
| `python -m pytest` | Roda toda a suíte de testes |
| `python -m pytest tests/test_cpf.py -v` | Roda só os testes de CPF, caso a caso |
| `python -m pytest tests/test_cnpj.py -v` | Roda só os testes de CNPJ, caso a caso |
| `python -m pytest tests/test_lote.py -v` | Roda só os testes da validação em lote |
| `python -m pytest --cov=src` | Roda os testes com cobertura (requer `pytest-cov`) |
| `python -m src.validacao.cpf 529.982.247-25` | Valida um CPF pela linha de comando |
| `python -m src.validacao.cnpj 12.ABC.345/01DE-35` | Valida um CNPJ pela linha de comando |
| `python -m src.validacao.lote base.csv documento` | Valida em lote os documentos de um CSV |
| `python hello.py` | Script de verificação inicial do ambiente |
| `openspec list` | Lista as mudanças especificadas com OpenSpec |

A validação em lote infere o tipo de cada documento pelo comprimento, lê arquivos salvos pelo
Excel (com BOM e separador `;`) e usa três códigos de saída: `0` quando todos são válidos,
`1` quando há documentos inválidos e `2` quando não foi possível executar — o que permite
encadeá-la em scripts sem confundir "a base tem erros" com "o processo quebrou".

## Documentação

- [`CLAUDE.md`](CLAUDE.md) — contexto do projeto, comandos, convenções e restrições para a IA.
- [`src/validacao/CLAUDE.md`](src/validacao/CLAUDE.md) — regra customizada com escopo na pasta de validação.
- [`docs/adr/`](docs/adr/) — Architecture Decision Records: decisões tomadas e o porquê.

**Trabalho com prompts e ambiente (1ª atividade)**

- [`docs/prompts-comparacao.md`](docs/prompts-comparacao.md) — comparativo entre prompt fraco e prompt eficaz.
- [`docs/mcp-configuracao.md`](docs/mcp-configuracao.md) — configuração do servidor MCP e os obstáculos encontrados.
- [`docs/relatorio-final.md`](docs/relatorio-final.md) — relatório da atividade.

**Spec-Driven Development (2ª atividade)**

- [`docs/escopo.md`](docs/escopo.md) — funcionalidades escolhidas e por que servem para SDD.
- [`openspec/changes/add-validacao-cnpj/`](openspec/changes/add-validacao-cnpj/) — especificação do CNPJ com OpenSpec: proposta, spec, design, plano de tarefas, revisão do plano, revisão dos diffs e checkpoint humano.
- [`docs/spec-lote-csv.md`](docs/spec-lote-csv.md) — especificação da validação em lote, em Markdown manual.
- [`docs/comparacao-abordagens-sdd.md`](docs/comparacao-abordagens-sdd.md) — comparação entre as duas abordagens de especificação.
- [`docs/relatorio-sdd.md`](docs/relatorio-sdd.md) — relatório da atividade.

## Convenções de contribuição

Nenhuma alteração vai direto para a `main`. O fluxo é: branch dedicada, commit com mensagem
descritiva em português no imperativo, e Pull Request para revisão. Código gerado por IA
passa pela mesma revisão que código escrito à mão — o `git diff` é lido antes de aceitar.
