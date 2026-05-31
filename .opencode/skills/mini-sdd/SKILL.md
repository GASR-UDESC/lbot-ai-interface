---
name: sdd
description: Mini SDD para tarefas menores - cria especificacao de negocio, planejamento tecnico e executa fases de implementacao. Use quando o usuario executar comandos sdd:business-spec, sdd:tech-spec ou sdd:loop.
compatibility: opencode
---

# Mini SDD

Skill para conduzir tarefas de desenvolvimento de forma estruturada em tres etapas: especificacao de negocio, planejamento tecnico e execucao por fases.

Cada etapa roda em uma sessao separada para evitar context rot.

## Diretorio de trabalho

Todos os artefatos sao salvos em `task/` na raiz do workspace (`/Users/guilherme.mendesrosa/code/lbot-ai-interface/task/`).

---

## Fase 1: business-spec

**Comando:** `/sdd:business-spec`

### Objetivo

Receber o brainstorm do usuario (requisitos informais, descricao de tarefa do Jira, anotacoes do Notion) e transformar em uma especificacao de regra de negocio completa e sem ambiguidades.

### Fluxo obrigatorio

1. **Receber o input do usuario** - O texto que acompanha o comando e o brainstorm inicial.

2. **Analisar a codebase** - Antes de fazer perguntas, explorar o(s) repositorio(s) envolvido(s) para entender:
   - Entidades e modelos de dominio existentes
   - Fluxos de negocio atuais que se relacionam com a tarefa
   - Servicos e handlers que serao impactados
   - Padroes ja adotados para features similares

3. **Bombardear com perguntas** - Usar a tool `question` para fazer perguntas ao usuario. As perguntas devem:
   - Cobrir todas as lacunas de negocio identificadas
   - Explorar casos de borda e cenarios excepcionais
   - Validar premissas feitas a partir da analise da codebase
   - Perguntar sobre comportamentos esperados em cenarios de erro
   - Confirmar regras de visibilidade, permissao e acesso
   - Ser feitas em LOTES (varias perguntas por chamada da tool question) para ser eficiente
   - Continuar ate que TODAS as lacunas estejam cobertas (multiplas rodadas se necessario)

4. **Consolidar o documento** - Quando todas as lacunas estiverem sanadas, gerar o arquivo:

### Arquivo de saida: `task/business-spec.md`

```markdown
# Especificacao de Negocio: <titulo da tarefa>

## Contexto

<Descricao do contexto geral, de onde veio a tarefa, qual problema resolve>

## Requisitos Funcionais

### RF01 - <Nome do requisito>
<Descricao detalhada>

**Regras:**
- <regra 1>
- <regra 2>

**Cenarios de erro:**
- <cenario 1>: <comportamento esperado>

### RF02 - ...

## Requisitos Nao-Funcionais

- <se houver>

## Glossario / Definicoes

- <termo>: <definicao>

## Premissas

- <premissa 1>
- <premissa 2>

## Fora de escopo

- <item que explicitamente NAO faz parte desta tarefa>

## Cenarios de Aceite

### CA01 - <Nome do cenario>
**Dado** <pre-condicao>
**Quando** <acao>
**Entao** <resultado esperado>

### CA02 - ...
```

### Regras criticas

- NAO gere o documento sem antes fazer perguntas. Sempre ha lacunas.
- Use a tool `question` com opcoes quando possivel para agilizar as respostas.
- Perguntas devem ser agrupadas por tema (ex: "Sobre permissoes", "Sobre validacoes").
- Se a analise da codebase revelar patterns que impactam a regra de negocio, mencione ao usuario.
- O documento final deve ser autocontido - qualquer pessoa deve entender a feature lendo apenas ele.
- Confirme com o usuario antes de salvar o documento final (pergunte: "Posso consolidar e salvar?").

---

## Fase 2: tech-spec

**Comando:** `/sdd:tech-spec`

### Objetivo

A partir da especificacao de negocio ja consolidada em `task/business-spec.md`, criar um plano de implementacao tecnica detalhado, dividido em fases executaveis.

### Fluxo obrigatorio

1. **Ler a especificacao de negocio** - Ler `task/business-spec.md` para entender completamente o que deve ser feito.

2. **Analisar a codebase profundamente** - Ir alem da analise superficial:
   - Identificar TODOS os arquivos que serao criados ou alterados
   - Ler o conteudo dos arquivos que serao impactados
   - Entender a estrutura de testes existente
   - Verificar dependencias entre modulos/servicos
   - Verificar patterns de implementacao similares ja existentes no projeto

3. **Bombardear com perguntas tecnicas** - Usar a tool `question` para:
   - Confirmar escolhas de arquitetura (ex: "Criar um novo modulo ou reaproveitar X?")
   - Validar abordagens de implementacao
   - Perguntar sobre preferencias tecnicas do time
   - Confirmar estrategia de migracao de dados (se aplicavel)
   - Perguntar sobre integracao com outros servicos
   - Confirmar estrategia de testes

4. **Criar o plano tecnico** - Gerar `task/tech-spec.md` com a visao geral.

5. **Criar as fases de implementacao** - Dividir em arquivos `task/phase-01.md`, `task/phase-02.md`, etc.

### Arquivo de saida: `task/tech-spec.md`

```markdown
# Plano Tecnico: <titulo da tarefa>

## Visao Geral

<Resumo da abordagem tecnica escolhida>

## Modulos Envolvidos

- <modulo 1>: <o que sera feito nele>
- <modulo 2>: <o que sera feito nele>

## Arquivos Impactados

### Novos
- `<caminho/arquivo>` - <finalidade>

### Alterados
- `<caminho/arquivo>` - <o que muda>

## Decisoes Tecnicas

| Decisao | Opcao escolhida | Justificativa |
|---------|-----------------|---------------|
| <decisao 1> | <opcao> | <por que> |

## Dependencias entre Fases

- Fase 1 -> Fase 2 (precisa dos modelos gerados)
- ...

## Mapa de Fases

| Fase | Descricao | Modulo |
|------|-----------|--------|
| 01 | ... | ... |
| 02 | ... | ... |
```

### Arquivo de saida: `task/phase-XX.md`

```markdown
# Fase XX: <titulo da fase>

## Status: PENDENTE

## Objetivo

<O que esta fase entrega>

## Pre-requisitos

- <fase anterior concluida, se aplicavel>

## Tarefas

- [ ] Tarefa 1: <descricao detalhada>
  - Arquivo: `<caminho>`
  - O que fazer: <instrucoes especificas>
- [ ] Tarefa 2: ...

## Arquivos Referencia

<Arquivos existentes que o agente deve ler para entender o pattern>

- `<caminho/arquivo>` - <motivo de ser referencia>

## Criterios de Aceite

- [ ] CA01: <descricao do teste que valida>
  - Cenario: <Given/When/Then>
- [ ] CA02: ...

## Testes Esperados

- `test_<cenario1>` - <o que valida>
- `test_<cenario2>` - <o que valida>

## Comandos pos-fase

<Comandos que devem ser executados apos implementar, ex:>
- `pytest tests/`
- `python -m mypy .`

## Registro de Execucao

<Preenchido pelo agente durante a execucao>

- Data:
- Arquivos criados:
- Arquivos alterados:
- Testes executados:
- Resultado:
- Pendencias:
```

### Regras para divisao de fases

- Cada fase deve ser executavel em UMA sessao de agente (nao muito grande).
- Cada fase deve ser testavel de forma independente apos conclusao.
- Fases devem seguir uma ordem logica de dependencia (modelagem -> implementacao -> testes).
- Uma fase nao deve ter mais que 5-7 tarefas.
- Prefira fases menores e bem definidas a fases grandes e vagas.

### Regras criticas

- NAO crie o plano sem perguntar. Sempre ha decisoes tecnicas que precisam de input.
- REFERENCIE arquivos com caminhos completos relativos a raiz do repositorio.
- Os criterios de aceite devem mapear TODOS os cenarios da business-spec.
- Cada fase deve listar os comandos que devem ser executados ao final (build, test, lint).
- Confirme com o usuario a divisao de fases antes de salvar.

---

## Fase 3: loop

**Comando:** `/sdd:loop`

### Objetivo

Executar a proxima fase pendente do plano de implementacao.

### Fluxo obrigatorio

1. **Ler o plano** - Ler `task/tech-spec.md` para ter a visao geral.

2. **Identificar a fase atual** - Ler os arquivos `task/phase-XX.md` e encontrar o primeiro com `Status: PENDENTE`.

3. **Ler a business-spec** - Ler `task/business-spec.md` para ter o contexto de negocio.

4. **Ler os arquivos de referencia** - Ler todos os arquivos listados na secao "Arquivos Referencia" da fase.

5. **Executar as tarefas** - Implementar cada tarefa listada na fase, na ordem:
   - Marcar a tarefa como em andamento
   - Implementar a alteracao/criacao
   - Executar os comandos necessarios (testes, build, lint)
   - Marcar a tarefa como concluida

6. **Executar os testes** - Rodar os testes listados na fase.

7. **Atualizar o registro** - Preencher a secao "Registro de Execucao" do arquivo da fase com:
   - Data de execucao
   - Arquivos criados/alterados
   - Testes executados e resultados
   - Pendencias encontradas (se houver)

8. **Atualizar o status** - Mudar o status da fase para `CONCLUIDO` (ou `PARCIAL` se houver pendencias).

9. **Parar** - Informar ao usuario que a fase foi concluida e qual e a proxima. NAO continue para a proxima fase automaticamente.

### Regras criticas

- Execute APENAS UMA fase por sessao.
- Se um teste falhar, tente corrigir ate 3 vezes. Se persistir, marque como pendencia e informe o usuario.
- Siga EXATAMENTE as instrucoes da fase. Nao improvise alem do escopo.
- Se encontrar algo que precisa de decisao de negocio nao coberta, PARE e pergunte ao usuario.
- Ao finalizar, mostre um resumo claro do que foi feito e o que vem a seguir.
