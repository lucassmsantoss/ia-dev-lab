# Etapa 4 — Revisão arquitetural com apoio de IA

## Resumo da arquitetura atual

Gerado a partir do código real em `src/validacao/` (não da documentação — o resumo foi
conferido linha a linha contra `cpf.py`, `cnpj.py`, `lote.py` e `__init__.py`).

**Módulos:**

| Módulo | Papel | Acessa disco/rede? | Exportado em `__init__.py`? |
|---|---|---|---|
| `cpf.py` | Validador puro de CPF | Não | Sim (`validar_cpf`) |
| `cnpj.py` | Validador puro de CNPJ (numérico e alfanumérico) | Não | Sim (`validar_cnpj`) |
| `lote.py` | Orquestrador: lê CSV, chama os dois validadores, formata relatório, expõe CLI | Sim (leitura de arquivo) | Não |

**Grafo de dependências (imports reais):**

```
lote.py  ---import--->  cpf.py
lote.py  ---import--->  cnpj.py
cpf.py   ---import--->  (nenhuma dependência interna)
cnpj.py  ---import--->  (nenhuma dependência interna)
```

`cpf.py` e `cnpj.py` não importam um do outro nem nada em comum — são folhas independentes na
árvore de dependências. `lote.py` é o único ponto que conhece os dois.

**Pontos de acoplamento:**

1. **Acoplamento por import, direcional e único:** `lote.py` → `{cpf.py, cnpj.py}`. Baixo risco:
   é a direção esperada (orquestrador depende de validador, nunca o contrário) e a interface
   usada é mínima — só a função pública `validar_<documento>(str) -> bool` de cada um.
2. **Acoplamento por contrato implícito, não por import:** `lote.py` decide qual validador
   chamar por **comprimento da string** (`_limpar` → 11 dígitos é CPF, 14 é CNPJ,
   `validar_documento` em `lote.py`). Isso funciona hoje porque CPF e CNPJ têm tamanhos
   diferentes, mas é uma suposição que vive em `lote.py`, não em `cpf.py` nem `cnpj.py` — se um
   terceiro documento algum dia tivesse 11 ou 14 posições, a inferência quebraria em silêncio.
3. **Duplicação sem import — o ponto que a Etapa 6 aprofunda:** `_calcular_digito` de `cpf.py`
   e a função equivalente em `cnpj.py` implementam a mesma regra de arredondamento de módulo 11
   (`0 se resto < 2, senão módulo - resto`), cada uma com sua própria cópia. Não é acoplamento
   no sentido de dependência de código — é o oposto: **a ausência** de uma dependência
   compartilhada faz a mesma regra de negócio existir em dois lugares que podem divergir sem
   que nenhum teste acuse, porque cada teste só olha para o próprio arquivo.

## Decisão: o projeto está no tamanho certo, com um ajuste pontual — não modularizar mais, não extrair serviço

**Critérios usados (não só opinião):**

- **Número de motivos para mudar cada módulo** (princípio de responsabilidade única, em nível
  de módulo): `cpf.py` muda por causa de regra de CPF, `cnpj.py` por regra de CNPJ, `lote.py`
  por causa de formato de arquivo/CLI. Três motivos, três módulos — já está separado
  corretamente, extrair mais não reduziria o número de motivos por módulo, só aumentaria o
  número de arquivos para o mesmo número de responsabilidades.
- **Direção e volume das dependências:** um único ponto de acoplamento por import
  (`lote.py` → validadores), unidirecional, sem ciclo, sem "deus-módulo" que tudo importa.
  Isso é o oposto do sinal que pediria mais modularidade (muitos módulos importando uns aos
  outros em várias direções).
- **Existência de superfície de implantação:** extrair serviço faz sentido quando há um limite
  de processo, deploy ou escala a proteger (times diferentes, ciclos de release diferentes,
  necessidade de escalar uma parte sem a outra). Este projeto não tem servidor, não tem API,
  não tem consumidor externo além de outro módulo Python no mesmo processo — não há fronteira
  de implantação para um serviço proteger.
- **Custo de já ter uma convenção contrária:** `CLAUDE.md` proíbe explicitamente pastas por
  tipo técnico (`utils/`, `helpers/`, `common/`). Isso não é um detalhe de estilo: é uma decisão
  arquitetural já tomada de organizar por domínio, e ela pesa contra criar uma camada nova só
  para hospedar um helper compartilhado.

**A parte que não está no tamanho certo:** o ponto 3 do levantamento acima (duplicação do
cálculo de dígito verificador) é dívida real, mas é uma dívida **de duplicação interna**, não
de modularidade insuficiente — a resposta não é criar um módulo novo (que a convenção do
projeto já desaconselha), é decidir se e como compartilhar uma função **dentro** do domínio já
existente. Essa decisão está registrada como ADR em
[`docs/adr/0002-nao-extrair-servico-mas-endereca-duplicacao.md`](adr/0002-nao-extrair-servico-mas-endereca-duplicacao.md),
e a investigação de qual mitigação faz sentido está em
[`docs/etapa6-divida-tecnica.md`](etapa6-divida-tecnica.md).
