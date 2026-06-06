# Fase 04: Simplificar CLI

## Status: PENDENTE

## Objetivo

Simplificar `cli.py` para um REPL enxuto: entrada do usuário → output, comando `/exit` para sair, flag `--show-thinking` (padrão ligado) para mostrar steps intermediários. Remover cores ANSI, banner, comandos `/help`, `/history`, `/reset`, estilização visual.

## Pre-requisitos

- Fase 03 concluída (agent.py refatorado, pois CLI instancia `ReActAgent`)

## Tarefas

- [ ] Tarefa 1: Reescrever `cli.py`
  - Arquivo: `lbot-mcp/src/harness/cli.py`
  - O que fazer: Reescrever o CLI (~80 linhas) com:
    - **Remover**:
      - `BANNER` (ASCII art)
      - `HELP_TEXT`
      - Função `_color()` (cores ANSI)
      - Formatação colorida no `_print_event()`
      - Comandos `/help`, `/history`, `/reset`, `/tools`
      - `history_summary` (do agente)
    - **Manter**:
      - Estrutura async com `asyncio`
      - `argparse` com flag `--show-thinking` (default=True)
      - `_print_event(event, data)`: callback simplificado SEM cores, mostrando:
        - `"goal"`: `"> {data}"`
        - `"llm_request"`: não mostra nada (verbose interno)
        - `"llm_response"`: não mostra nada (verbose interno)
        - `"tool_call"`: `"[{tool_name}] {args_resumido}"` (ex: `[move] ande 30cm para frente`)
        - `"tool_result"`: `"  -> {resultado_truncado}"` (máx 100 chars)
        - `"final_answer"`: `"{data}"`
        - `"error"`: `"Erro: {data}"`
        - `"cancelled"`: `"Interrompido"`
        - `"max_steps_reached"`: `"Limite de passos atingido"`
      - `_get_input()`: prompt simples `"> "`
      - REPL loop:
        - Comando `/exit` (também `/quit`, `/q`) → sai
        - Qualquer outro texto → `agent.run(user_input)`
        - Ctrl+C → cancela agente, não sai do REPL
      - `main()` e `_async_main()` mantidos como entry points

- [ ] Tarefa 2: Verificar dependências do CLI
  - O que fazer: Confirmar que `cli.py` não importa nada de `personality.py` (removido na Fase 03). Se houver imports obsoletos, limpar.

## Arquivos Referência

- `lbot-mcp/src/harness/cli.py` — Código atual (299 linhas) como base para simplificação
- `lbot-mcp/src/harness/agent.py` — Novo `ReActAgent` refatorado (Fase 03) para entender eventos e callbacks
- `lbot-mcp/src/harness/mcp_client.py` — `MCPClient` (não muda)

## Critérios de Aceite

- [ ] CA01: CLI não mostra banner ao iniciar
  - Cenario: Dado inicio do CLI / Quando executo / Então não aparece arte ASCII, apenas prompt `> `

- [ ] CA02: Apenas `/exit` funciona como comando especial
  - Cenario: Dado CLI rodando / Quando digito `/help`, `/history`, `/reset` / Então são tratados como input normal (enviados ao agente)

- [ ] CA03: `/exit` encerra o programa
  - Cenario: Dado CLI rodando / Quando digito `/exit` / Então programa termina com código 0

- [ ] CA04: Output sem cores ANSI
  - Cenario: Dado CLI rodando com --show-thinking / Quando agente executa steps / Então output não contém escape codes ANSI (`\033[`, `\x1b[`)

- [ ] CA05: Flag `--show-thinking` controla output de steps
  - Cenario: Dado CLI com `--show-thinking` (padrão) / Quando agente executa / Então mostra cada tool call e resultado
  - Cenario: Dado CLI sem `--show-thinking` (`--quiet` ou removido) / Quando agente executa / Então mostra apenas resultado final

- [ ] CA06: Ctrl+C cancela o agente mas mantém o REPL
  - Cenario: Dado agente executando / Quando pressiono Ctrl+C / Então agente é cancelado, mensagem "Interrompido", REPL continua

- [ ] CA07: CLI tem no máximo ~100 linhas
  - Cenario: Dado o arquivo cli.py / Quando conto linhas / Então ≤ 100 linhas

## Testes Esperados

(Não há testes automatizados — RF02. Validação manual executando o CLI.)

## Comandos pós-fase

```bash
# Verificar tamanho do arquivo
wc -l lbot-mcp/src/harness/cli.py

# Verificar que não há códigos ANSI
grep -n '\\\\033\|\\\\x1b\|\\\\e\[' lbot-mcp/src/harness/cli.py && echo "ERRO: codigos ANSI encontrados" || echo "OK: sem cores ANSI"

# Verificar import (não executa o loop, apenas verifica sintaxe)
cd lbot-mcp && python -c "from harness.cli import main; print('cli importado OK')"
```

## Registro de Execução

- Data:
- Arquivos criados:
- Arquivos alterados:
- Testes executados:
- Resultado:
- Pendências:
