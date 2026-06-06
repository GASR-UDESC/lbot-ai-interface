# Plano Técnico: Refatoração Completa do Harness

## Visão Geral

Refatoração do harness (`lbot-mcp/src/harness/`) aplicando Clean Code (SRP, arquivos ~150-200 linhas), removendo validações programáticas, simplificando o system prompt para modelo ~8B, e limpando testes. As alterações no MCP server são mínimas e pontuais (adicionar translate tool, remover observe tool).

O tradutor Seq2Seq (`TranslatorWrapper` / `LBotTranslatorV7`) permanece carregado no processo do MCP server. O harness obtém tradução NL→LBML chamando uma nova MCP tool `translate()` internamente (não exposta à LLM).

## Módulos Envolvidos

- **harness** (`lbot-mcp/src/harness/`): Refatoração completa. Arquivos grandes (`agent.py` 910L, `personality.py` 235L) são divididos em módulos com responsabilidade única.
- **mcp_server** (`lbot-mcp/src/mcp_server/`): Alterações pontuais — adicionar `translate` tool, remover `observe` tool, simplificar `move` tool.
- **lbot-simulator-web**: Apenas remoção de testes e configs de teste. Código fonte inalterado.

## Arquivos Impactados

### Novos
- `lbot-mcp/src/harness/prompt.py` — System prompt (~30-50 linhas, português) + definições das 3 ferramentas MCP (camera, proximity, move)
- `lbot-mcp/src/harness/messages.py` — Formatação de mensagens: injeção de imagens, construção de tool results, sumarização para display
- `lbot-mcp/src/harness/tool_handler.py` — Handlers para cada tool call: camera_handler, proximity_handler, move_handler (com tradução NL→LBML via translate tool)
- `lbot-mcp/src/mcp_server/tools/translate.py` — Nova ferramenta MCP `translate(command_nl) -> str` que expõe o TranslatorWrapper

### Alterados
- `lbot-mcp/src/harness/agent.py` — Reescrito para ~150 linhas: apenas o loop ReAct (`run()`), sem validações, sem trimming, sem parsing LBML
- `lbot-mcp/src/harness/cli.py` — Simplificado para ~80 linhas: REPL básico com `/exit`, flag `--show-thinking`, sem cores/banner/help/history/reset
- `lbot-mcp/src/mcp_server/server.py` — Remover import de `observe`, adicionar import de `translate`
- `lbot-mcp/src/mcp_server/tools/movement.py` — Remover branch de tradução NL→LBML (passa a aceitar apenas LBML, pois o harness traduz antes)
- `lbot-mcp/pyproject.toml` — Remover `[tool.pytest.ini_options]`, seção `dev` de dependências (pytest, pytest-asyncio), seção `[tool.uv]` de dev-dependencies
- `lbot-simulator-web/package.json` — Remover script `"test"`, remover devDependencies de teste (`vitest`, `jsdom`, `@testing-library/*`)
- `lbot-simulator-web/tsconfig.app.json` — Remover `"tests"` e `"vitest.config.ts"` do `include`

### Removidos
- `lbot-mcp/src/harness/personality.py` — Substituído por `prompt.py`
- `lbot-mcp/src/mcp_server/tools/observe.py` — Ferramenta removida (RF07)
- `lbot-mcp/tests/` — Diretório completo (8 arquivos Python de teste)
- `lbot-simulator-web/tests/` — Diretório completo (5 arquivos TypeScript de teste)
- `lbot-simulator-web/vitest.config.ts` — Config do Vitest
- `lbot-mcp/.pytest_cache/`, `3.controlador/.pytest_cache/`, `.pytest_cache/` — Caches de pytest

## Decisões Técnicas

| Decisão | Opção escolhida | Justificativa |
|---------|-----------------|---------------|
| Local do tradutor | MCP server (mantido) | Mantém PyTorch isolado no processo servidor; harness permanece leve |
| Mecanismo de tradução | Nova MCP tool `translate()` | Harness traduz NL→LBML antes de chamar `move()`. Se tradução falhar, missão é abortada (RF05). A tool `translate` não é exposta à LLM (uso interno do harness) |
| Divisão do agent.py | 4 arquivos: `agent.py`, `prompt.py`, `messages.py`, `tool_handler.py` | Cada arquivo com responsabilidade única, ~80-150 linhas. `agent.py` fica apenas com o loop ReAct |
| System prompt + tools | Mesmo arquivo `prompt.py` | Coesão: prompt e tools são a "personalidade" do agente. Arquivo ~80 linhas no total |
| Remoção do observe() | Deletar código fonte | Código morto não deve permanecer. Ferramenta obsoleta após refatoração |
| CLI --show-thinking | Mantido como padrão | Mostra steps sem cores. Flag permite ocultar para debugging silencioso |
| move() no MCP server | Aceitar apenas LBML | Responsabilidade de tradução fica no harness (via translate tool). move() é somente executor |

## Dependências entre Fases

```
Phase 01 (prompt + messages + tool_handler)
    │
    ▼
Phase 02 (MCP server: translate tool, remove observe, simplify move)
    │
    ▼
Phase 03 (refatorar agent.py — depende dos módulos da Phase 01 + translate tool da Phase 02)
    │
    ▼
Phase 04 (simplificar CLI — depende do agent refatorado)
    
Phase 05 (remover testes — independente, pode rodar em paralelo com qualquer fase)
```

## Mapa de Fases

| Fase | Descrição | Módulo |
|------|-----------|--------|
| 01 | Criar prompt.py, messages.py, tool_handler.py | harness |
| 02 | Adicionar translate tool, remover observe, simplificar move | mcp_server |
| 03 | Refatorar agent.py (loop ReAct limpo) | harness |
| 04 | Simplificar CLI (REPL + /exit) | harness |
| 05 | Remover todos os testes e configs de teste | ambos |
