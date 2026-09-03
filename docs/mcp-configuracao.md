# Configuração do servidor MCP

Registro do passo a passo da configuração do MCP (Model Context Protocol) neste projeto,
incluindo os obstáculos encontrados e como foram resolvidos.

## O que é e por que usar aqui

O MCP é um protocolo aberto que padroniza como um agente de IA acessa ferramentas e fontes
de dados externas. Sem ele, o agente só enxerga o que é colado no prompt. Com ele, o agente
pode consultar o sistema de arquivos, o histórico do Git, um banco de dados ou uma API —
sempre por meio de um servidor que declara explicitamente quais operações expõe.

A relevância para esta atividade é direta: o `CLAUDE.md` da Etapa 2 dá ao agente o **contexto
declarado** do projeto, e o MCP dá a ele o **estado real** do projeto. Um diz "as convenções
são estas"; o outro permite perguntar "quais arquivos mudaram no último commit" e obter a
resposta do repositório, não da memória do modelo.

## Servidor configurado

O arquivo [`.mcp.json`](../.mcp.json) na raiz declara um servidor:

| Servidor | Runtime | Para que serve |
| --- | --- | --- |
| `filesystem` | Node (via `npx`) | Ler, listar e escrever arquivos dentro da pasta do projeto |

Um segundo servidor, de Git, foi tentado e não pôde ser instalado neste ambiente — o motivo
está registrado na seção "Servidor de Git: tentativa não concluída", mais abaixo.

O caminho declarado é `"."`, e não um caminho absoluto, de propósito: o agente inicia o
servidor com o diretório de trabalho na raiz do projeto, então a configuração continua válida
para qualquer pessoa que clonar o repositório em outra máquina. Um caminho como
`C:\Users\lucas\Documents\ia-dev-lab` funcionaria só aqui, e versionar isso quebraria o
projeto para qualquer outro colaborador.

O escopo é deliberadamente restrito à pasta do projeto. O servidor de filesystem só acessa o
que está abaixo do diretório informado — apontá-lo para a raiz do usuário daria ao agente
acesso a documentos pessoais sem nenhuma necessidade.

## Passo a passo executado

### 1. Primeira tentativa — falhou

```powershell
node --version
# node : O termo 'node' não é reconhecido como nome de cmdlet, função,
# arquivo de script ou programa operável.
```

**Obstáculo:** o servidor `@modelcontextprotocol/server-filesystem` é distribuído como pacote
npm e executado via `npx`, que faz parte do Node.js. O ambiente da máquina tinha Python
(Anaconda) e Git, mas não tinha Node — dependência que não era óbvia até a primeira execução
falhar.

### 2. Instalação do Node.js

```powershell
winget install OpenJS.NodeJS.LTS
```

Foi necessário **fechar e reabrir o terminal** depois da instalação: o instalador altera a
variável de ambiente PATH, e sessões já abertas continuam com a cópia antiga.

Verificação:

```powershell
node --version
npx --version
```

### 3. Política de execução do PowerShell

Com o Node instalado, o `npx` ainda falhava:

```powershell
npx --version
# npx : O arquivo C:\Program Files\nodejs\npx.ps1 não pode ser carregado porque
# a execução de scripts foi desabilitada neste sistema.
```

**Obstáculo:** no Windows o `npx` é distribuído como script PowerShell (`npx.ps1`), e a
política padrão `Restricted` recusa qualquer `.ps1` não assinado. Resolvido com:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

O escopo `CurrentUser` evita alterar a máquina inteira, e `RemoteSigned` continua exigindo
assinatura em scripts baixados da internet — libera só os locais.

Vale notar que o MCP funcionaria mesmo sem essa mudança: o agente executa `npx.cmd` como
processo direto, sem passar pelo PowerShell. A política bloqueava apenas o teste manual.

### 4. Criação do `.mcp.json`

Arquivo criado na raiz do projeto, versionado junto com o código, para que a configuração dos
servidores acompanhe o repositório em vez de ficar presa às configurações locais do editor.

**Obstáculo:** a primeira gravação usou `Set-Content -Encoding UTF8`, que no Windows
PowerShell 5.1 grava um BOM (`EF BB BF`) no início do arquivo. O JSON continua tecnicamente
correto, mas o `JSON.parse` do Node falha ao encontrar o BOM — e o erro não indica a causa.
Regravado com `-Encoding ascii`, que não escreve BOM.

### 5. Conexão e teste

Com o projeto aberto no agente, o servidor é iniciado automaticamente a partir do `.mcp.json`.
O prompt usado para confirmar que a conexão funciona depende de dados que o modelo não tem
como saber sozinho:

> Usando o servidor MCP de filesystem, liste os arquivos dentro de `src/validacao/` e de
> `tests/`, e me diga quantos casos de teste o arquivo `tests/test_cpf.py` declara.

A resposta correta deve citar **exatamente os arquivos presentes nas duas pastas no momento do
teste** — não uma lista plausível. O critério é esse, e não uma lista fixa, porque o conteúdo
das pastas muda a cada atividade: quando este teste foi executado, em 27/08/2026,
`src/validacao/` continha `CLAUDE.md`, `__init__.py` e `cpf.py`, e `tests/` continha
`__init__.py` e `test_cpf.py`. Hoje há também `cnpj.py`, `lote.py`, `test_cnpj.py` e
`test_lote.py`.

Se o agente responder de forma genérica, citar arquivos que não estão lá ou pedir que o
conteúdo seja colado, a conexão não está ativa.

> **Evidência obtida em 27/08/2026:** o agente listou corretamente os cinco arquivos e ainda
> incluiu o diretório `__pycache__/` nas duas pastas. Esse detalhe é a prova mais forte de que
> a conexão estava ativa: `__pycache__/` está no `.gitignore`, não aparece no repositório
> remoto e não havia sido mencionado em nenhum prompt — só existia no disco local.

## Servidor de Git: tentativa não concluída

A intenção inicial era declarar também um servidor de Git, que permitiria perguntas sobre o
histórico do repositório — por exemplo, quais arquivos mudaram no último commit. A tentativa
falhou por incompatibilidade de versão de Python:

```
pip install mcp-server-git
# ERROR: Could not find a version that satisfies the requirement mcp-server-git
#        (from versions: none)
# ERROR: No matching distribution found for mcp-server-git
```

**Diagnóstico:** o `mcp-server-git` exige Python 3.10 ou superior, e o ambiente `base` do
Anaconda nesta máquina é o **3.9.12**. A mensagem do pip é enganosa — `from versions: none`
sugere que o pacote não existe, quando na verdade significa que nenhuma versão publicada é
compatível com o interpretador em uso.

**Caminhos possíveis, não executados por restrição de tempo:**

1. Criar um ambiente conda dedicado com Python 3.11 (`conda create -n mcp python=3.11`) e
   declarar o servidor com `conda run -n mcp python -m mcp_server_git`. Funciona, mas acopla
   a configuração versionada a um ambiente que só existe nesta máquina.
2. Instalar o `uv` e usar `uvx mcp-server-git`, que resolve o interpretador isoladamente. É a
   forma recomendada pela documentação oficial e evita o problema de versão do ambiente base.
3. Atualizar o Python do ambiente `base`, descartado por afetar todos os outros projetos que
   dependem dele.

A opção 2 é a que eu escolheria se fosse continuar, justamente porque não depende do estado do
ambiente Python local. Como o requisito da atividade era **um** servidor MCP simples e o de
filesystem está funcionando, o de Git ficou registrado aqui como tentativa documentada.

## Obstáculos e aprendizados

O ponto que mais custou tempo não foi o MCP em si, e sim o **ambiente Windows**. Foram cinco
problemas encadeados, e quatro deles são a mesma coisa com roupas diferentes:

1. O comando `python` era interceptado pelo alias da Microsoft Store, porque o Anaconda não
   foi adicionado ao PATH na instalação.
2. Contornar isso chamando `anaconda3\python.exe` pelo caminho absoluto gerou
   `ImportError: DLL load failed while importing _ssl` — as DLLs do OpenSSL ficam em
   `anaconda3\Library\bin`, diretório que só entra no PATH durante a ativação do ambiente.
   Resolvido com o Anaconda Prompt e, depois, com `conda init powershell`.
3. O `node` não existia, e depois de instalado ainda não era visível no terminal já aberto.
4. O `pip` não era reconhecido no PowerShell, porque o Anaconda só estava no PATH do
   Anaconda Prompt.
5. O `mcp-server-git` não instalou — este é de outra natureza: incompatibilidade de versão
   de Python, não de PATH.

O padrão nos quatro primeiros é idêntico: **a ferramenta estava instalada, mas o terminal não
sabia disso**. Vale registrar porque é exatamente o tipo de obstáculo que um agente de IA não
resolve sozinho — ele depende do ambiente que encontra, e diagnosticar PATH ainda é trabalho
humano de leitura de mensagem de erro.

Há uma observação mais interessante escondida aí. Nos cinco casos, a mensagem de erro apontava
para o sintoma e não para a causa: "python não foi encontrado" quando o Python estava
instalado; "DLL não encontrada" quando o problema era ativação de ambiente; "from versions:
none" quando o pacote existe e o incompatível era o interpretador. A IA acelerou muito a
tradução de sintoma para causa — mas a decisão sobre **qual** dos caminhos possíveis seguir
(instalar o uv, criar um ambiente novo, ou aceitar um servidor a menos e documentar) continuou
sendo humana, porque depende de restrições que não estão no código: prazo, e o quanto vale
sujar o ambiente da máquina.
