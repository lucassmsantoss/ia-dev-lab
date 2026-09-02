# ia-dev-lab

Laboratório de desenvolvimento de software assistido por IA, criado para a disciplina
**Tópicos Avançados em Engenharia de Software 2** do Mestrado em Tecnologia da Informação
(PPgTI / Instituto Metrópole Digital — UFRN).

## Visão geral

O objetivo do repositório não é entregar um produto, e sim exercitar um **fluxo de trabalho**
com IA: configurar o ambiente, dar contexto explícito ao agente (`CLAUDE.md`), organizar o
código por domínio, comparar a qualidade de prompts diferentes e integrar tudo a Git/GitHub
com revisão humana antes do merge.

O domínio usado nos exercícios é a **validação de documentos brasileiros**, começando pelo CPF.
É um problema deliberadamente pequeno, mas com regra de negócio verificável — o que permite
comparar de forma objetiva o código gerado a partir de um prompt fraco e de um prompt eficaz.

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
|   |-- prompts-comparacao.md  # prompt fraco vs. prompt eficaz (Etapa 4)
|   |-- mcp-configuracao.md    # passo a passo e obstáculos do MCP (Etapa 5)
|   |-- relatorio-final.md     # relatório da atividade (Etapa 6)
|   `-- relatorio-final.pdf
|-- src/
|   `-- validacao/             # domínio: validação de documentos
|       |-- CLAUDE.md          # regra customizada com escopo nesta pasta
|       |-- __init__.py
|       `-- cpf.py
`-- tests/
    |-- __init__.py
    `-- test_cpf.py
```

As pastas são organizadas por **domínio** (`validacao`), não por tipo técnico. Não existe
`utils/` nem `helpers/`: quando surgir a validação de CNPJ, ela entra em `src/validacao/`
ao lado do CPF, e não em uma pasta genérica.

## Instalação

Requer Python 3.9 ou superior e Git. O ambiente de referência é o Anaconda com Python 3.9.12
no Windows, que já traz o `pytest` instalado.

```bash
git clone https://github.com/lucassmsantoss/ia-dev-lab.git
cd ia-dev-lab
```

**Com Anaconda (ambiente de referência):** abra o **Anaconda Prompt** e rode os comandos a
partir da pasta do projeto. Nada mais precisa ser instalado.

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
| `python -m pytest --cov=src` | Roda os testes com relatório de cobertura |
| `python -m src.validacao.cpf 529.982.247-25` | Valida um CPF pela linha de comando |
| `python hello.py` | Script de verificação inicial do ambiente |

## Documentação

- [`CLAUDE.md`](CLAUDE.md) — contexto do projeto, comandos, convenções e restrições para a IA.
- [`src/validacao/CLAUDE.md`](src/validacao/CLAUDE.md) — regra customizada com escopo na pasta de validação.
- [`docs/adr/`](docs/adr/) — Architecture Decision Records: decisões tomadas e o porquê.
- [`docs/prompts-comparacao.md`](docs/prompts-comparacao.md) — comparativo entre prompt fraco e prompt eficaz.

## Convenções de contribuição

Nenhuma alteração vai direto para a `main`. O fluxo é: branch dedicada, commit com mensagem
descritiva em português no imperativo, e Pull Request para revisão. Código gerado por IA
passa pela mesma revisão que código escrito à mão — o `git diff` é lido antes de aceitar.
