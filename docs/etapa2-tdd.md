# Etapa 2 — TDD como guard-rail

## Ciclo Red-Green-Refactor real: `fix-normalizacao-cpf`

A tarefa não foi inventada para a atividade: é o item que ficou pendente em
`openspec/changes/add-validacao-cnpj/checkpoint-humano.md` desde a atividade de SDD — dois
defeitos documentados em `revisao-dos-diffs.md`, com a correção bloqueada na época pelo
checkpoint humano por estar fora do escopo daquela mudança. Ver
`openspec/changes/fix-normalizacao-cpf/` para a proposta e o plano completos.

### RED — os testes, escritos antes de qualquer mudança em `cpf.py`

Adicionados em `tests/test_cpf.py`:

```python
@pytest.mark.parametrize("cpf", [
    "<script>52998224725</script>",
    "529.982.247-25!!!",
    "CPF: 529.982.247-25",
])
def test_rejeita_cpf_valido_cercado_de_lixo(cpf):
    assert validar_cpf(cpf) is False


@pytest.mark.parametrize("cpf", ["²2998224725", "٥2998224725"])
def test_rejeita_digito_nao_ascii_sem_lancar_excecao(cpf):
    assert validar_cpf(cpf) is False
```

**Verificação do RED**, rodada contra o `cpf.py` de antes da correção:

```
>>> validar_cpf('<script>52998224725</script>')
True        # esperado: False
>>> validar_cpf('529.982.247-25!!!')
True        # esperado: False
>>> validar_cpf('CPF: 529.982.247-25')
True        # esperado: False
>>> validar_cpf('²2998224725')
ValueError: invalid literal for int() with base 10: '²'   # esperado: False, sem excecao
>>> validar_cpf('٥2998224725')
True        # esperado: False
```

Os cinco casos falham — três por assertivo errado (`True` em vez de `False`), dois por motivo
mais grave ainda: um levanta exceção em vez de falhar a asserção. Isso confirma que os testes
falham **pelo motivo certo** (o defeito existe), não por erro de digitação no teste.

### GREEN — a implementação mínima

`_somente_digitos` (descartava tudo que não fosse dígito) virou `_normalizar` (remove só
`.`, `-` e espaço, no mesmo padrão já usado em `cnpj.py`), e a checagem de dígito passou a
comparar explicitamente contra `"0123456789"` em vez de usar `str.isdigit()`. Sem adicionar
nada além do necessário para os cinco casos passarem — nenhuma opção nova, nenhum parâmetro,
nenhuma generalização especulativa.

Depois da mudança, os cinco casos passam a `False` sem exceção, e a suíte completa de CPF
permanece verde: de 38 para 49 testes (11 novos: 5 de regressão do defeito + 6 do
`mascarar_cpf`, ver seção seguinte), nenhum teste anterior alterado em seu resultado esperado.

### REFACTOR

Dois ajustes depois do verde, sem mudar comportamento: renomeado o teste da função interna
(`test_somente_digitos_remove_a_mascara` → `test_normalizar_remove_apenas_formatacao`, já que a
função não filtra mais só dígitos) e atualizado o encaminhamento em `checkpoint-humano.md`,
marcando os dois itens pendentes como concluídos.

## Investigação: Superpowers como ferramenta de enforcement

Ferramenta escolhida: **Superpowers**, já disponível neste ambiente como skill
(`superpowers:test-driven-development`). Investigação real, não só leitura de documentação —
o ciclo acima foi conduzido seguindo o skill à risca.

**Como ele se comporta:** não é um hook técnico que intercepta chamadas de ferramenta e recusa
a execução (como o `tdd-guard`, que bloqueia mecanicamente a escrita de código de produção sem
teste correspondente já existente). É uma **disciplina declarada em texto**, carregada no
contexto do agente, que define uma "Lei de Ferro" — `NO PRODUCTION CODE WITHOUT A FAILING TEST
FIRST` — e um checklist de verificação a cumprir antes de considerar o trabalho concluído:
todo método novo tem teste, o teste falhou antes de existir implementação, falhou pelo motivo
certo, a implementação foi mínima, os testes passam, casos de borda estão cobertos.

A diferença importante para quem vai escolher entre os dois: o Superpowers **não tem como
impedir** um agente de escrever código de produção antes do teste — ele instrui a não fazer
isso, lista as racionalizações mais comuns para pular a etapa ("é simples demais para testar",
"escrevo o teste depois", "já testei manualmente") e nomeia cada uma como sinal de alerta. A
garantia é comportamental, não técnica. O `tdd-guard`, por descrição, atuaria na camada de
ferramenta: recusaria a própria chamada de escrita se não houvesse teste falhando primeiro,
funcionando mesmo se o agente "decidir" pular a etapa.

**Como se comportaria neste cenário, especificamente:** ao pedir a correção do `cpf.py` citando
o skill, a etapa RED deixou de ser opcional — o passo "Verify RED" do skill é explícito em
dizer que o teste tem que falhar **pelo motivo esperado**, não qualquer falha, o que aqui
significou rodar os cinco casos contra o código antigo antes de escrever uma linha de correção
e confirmar que as falhas eram as documentadas em `revisao-dos-diffs.md` — não um erro de
importação ou de sintaxe no teste novo. Isso pegou algo que uma verificação mais superficial
não pegaria: o caso do `²` não falha do mesmo jeito que os outros três (ele lança exceção, não
retorna `True`), e só ficou claro por rodar de fato, não por inspecionar o código.

**Limite observado:** por depender de o agente seguir a instrução, o Superpowers é tão forte
quanto o prompt que o invoca — em uma sessão onde o skill não é carregado, ou onde a instrução
some do contexto, nada barra o código de produção de vir antes do teste. O `tdd-guard`, sendo
técnico, não teria essa dependência. A troca é: Superpowers documenta o *raciocínio* de por que
cada atalho é uma racionalização (o que ajuda a internalizar a disciplina), enquanto um hook
técnico simplesmente recusa a ação, sem explicar.

## Tarefa sem TDD, para comparação: `mascarar_cpf`

Tarefa: adicionar uma função que formata um CPF com máscara (`XXX.XXX.XXX-XX`). Implementada
**sem** escrever teste antes, deliberadamente — só o código:

```python
def mascarar_cpf(cpf):
    """Formata um CPF de 11 dígitos no padrão XXX.XXX.XXX-XX."""
    return f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}"
```

Passou no único caso que eu tinha em mente ao escrevê-la (`mascarar_cpf("52998224725")` →
`"529.982.247-25"`). Só depois, testando à mão o que um teste-primeiro teria me obrigado a
decidir antes de escrever a primeira linha, apareceram os casos que a função não tratava:

```
>>> mascarar_cpf('')
'..-'
>>> mascarar_cpf('00000000000')
'000.000.000-00'                 # CPF invalido, formatado como se fosse valido
>>> mascarar_cpf('529.982.247-25')
'529..98.2.2-47-25'              # entrada ja mascarada: fatiamento sem sentido
>>> mascarar_cpf(None)
TypeError: 'NoneType' object is not subscriptable
```

Quatro defeitos numa função de seis linhas: nenhuma validação de entrada, formata CPF
estruturalmente inválido como se fosse válido, não normaliza entrada já mascarada e lança
exceção não tratada — a mesma classe de defeito de `_somente_digitos`, cometido de novo,
porque a pergunta "o que essa função garante para entrada inválida?" só apareceu depois de o
código já existir.

**Correção**, desta vez com teste (`test_mascarar_cpf_valido`,
`test_mascarar_cpf_invalido_devolve_none`) cobrindo exatamente os quatro casos encontrados:

```python
def mascarar_cpf(cpf: str) -> Optional[str]:
    if not validar_cpf(cpf):
        return None
    digitos = _normalizar(cpf)
    return f"{digitos[:3]}.{digitos[3:6]}.{digitos[6:9]}-{digitos[9:]}"
```

## Comparação: com TDD vs. sem TDD

| | `fix-normalizacao-cpf` (com TDD) | `mascarar_cpf` (sem TDD, 1ª versão) |
|---|---|---|
| Casos de borda cobertos ao terminar a 1ª versão | 5 (todos os do defeito documentado) | 1 (o único que eu tinha em mente) |
| Entrada inválida | Já era o objeto da mudança — testada por definição | Não considerada; `None` quebra o programa |
| Quando o defeito apareceu | Antes da implementação (é o próprio motivo da tarefa) | Depois, ao testar manualmente por curiosidade |
| Retrabalho | Nenhum — a implementação já nasceu para os 5 casos | Reescrita completa da função e assinatura (`Optional[str]`) |

A diferença não foi de qualidade de código no sentido estético — as duas versões finais são
igualmente simples. Foi sobre **quando** a pergunta "o que acontece com entrada inválida?" é
respondida. Com o teste escrito antes, ela é respondida como parte de decidir o que implementar.
Sem, ela só aparece se alguém, por conta própria, resolver testar à mão depois — e a suíte
`--cov=src` não teria acusado nada, porque `mascarar_cpf("52998224725")` já cobria 100% das
linhas da primeira versão. Cobertura de linha não é cobertura de caso de borda.
