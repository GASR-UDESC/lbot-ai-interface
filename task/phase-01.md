# Fase 01: Criar tool `observe` e modificar tool `move`

## Status: CONCLUIDO

## Objetivo

Implementar as alteracoes no modulo MCP Server tools:
1. Criar a tool `observe` que combina camera + proximidade
2. Modificar a tool `move` para detectar LBML direto no input e pular o tradutor quando aplicavel
3. Registrar a nova tool no server.py

## Pre-requisitos

- Nenhum (primeira fase)

## Tarefas

- [x] Tarefa 1: Criar `lbot-mcp/src/mcp_server/tools/observe.py`
  - Arquivo: `lbot-mcp/src/mcp_server/tools/observe.py`
  - O que fazer:
    - Criar funcao assincrona `observe()` decorada com `@mcp.tool()`
    - Chamar `backend.get_camera()` e `backend.get_proximity()` simultaneamente (usar `asyncio.gather`)
    - Combinar os resultados em um dict com campos: `image` (base64 PNG), `render_method`, `robot_position`, `proximity` (sub-dict com `frente` e `tras` em cm)
    - Retornar JSON string do dict combinado
    - Tratar erros: se camera falhar, incluir campo `camera_error`; se proximity falhar, incluir campo `proximity_error`; se ambos falharem, retornar erro geral
    - Formato de retorno em caso de sucesso:
      ```json
      {
        "image": "<base64_png>",
        "render_method": "2d" | "webgl" | "unknown",
        "robot_position": {"x": 0, "z": 0, "rotation": 0},
        "proximity": {"frente": 50.0, "tras": 200.0}
      }
      ```
    - Formato de retorno em caso de erro parcial (camera ok, proximity falhou):
      ```json
      {
        "image": "<base64_png>",
        "render_method": "2d",
        "robot_position": {"x": 0, "z": 0, "rotation": 0},
        "proximity_error": "sensor indisponivel"
      }
      ```

- [x] Tarefa 2: Modificar `lbot-mcp/src/mcp_server/tools/movement.py`
  - Arquivo: `lbot-mcp/src/mcp_server/tools/movement.py`
  - O que fazer:
    - Antes de chamar o tradutor, verificar se o `command` ja e LBML valido usando a regex `LBML_SEQUENCE_RE`
    - Se o command bater na regex, pular o tradutor e executar diretamente
    - Se nao bater, manter o fluxo atual (passar pelo tradutor)
    - Atualizar a mensagem de retorno para distinguir os dois caminhos:
      - Traduzido: `"Comando executado: {lbml} ({preprocessed})"`
      - LBML direto: `"Comando executado: {command} (LBML direto)"`

- [x] Tarefa 3: Registrar tool `observe` no server.py
  - Arquivo: `lbot-mcp/src/mcp_server/server.py`
  - O que fazer:
    - Adicionar `import mcp_server.tools.observe  # noqa: F401` na funcao `main()`
    - Adicionar "observe" na string de log: `"Tools registradas: camera, proximity, move, observe"`

## Arquivos Referencia

- `lbot-mcp/src/mcp_server/tools/camera.py` - Padrao de implementacao de tool (error handling, JSON retorno)
- `lbot-mcp/src/mcp_server/tools/proximity.py` - Padrao de formatacao de leituras de proximidade
- `lbot-mcp/src/mcp_server/tools/movement.py` - Tool atual a ser modificada (regex LBML, tradutor)
- `lbot-mcp/src/mcp_server/context.py` - Singleton para acessar backend
- `lbot-mcp/src/mcp_server/server.py` - Registro de tools

## Criterios de Aceite

- [ ] CA08: Tool observe retorna camera e proximidade
  - Cenario: Given que o LLM chama a tool `observe`, When a tool e executada, Then retorna simultaneamente a imagem da camera (base64 PNG) e os dados de proximidade (frente e tras em cm)
- [ ] Movimento ambiguo via move com LBML direto
  - Cenario: Given que o LLM classifica como Movimento ambiguo e gera LBML, When envia via tool `move` com o LBML como command, Then a tool detecta que e LBML valido, pula o tradutor, e executa diretamente
- [ ] Movimento bem definido continua funcionando via tradutor
  - Cenario: Given que o LLM classifica como Movimento bem definido e envia comando em linguagem natural, When a tool `move` e chamada, Then o tradutor e usado normalmente como antes

## Testes Esperados

- `test_observe_returns_camera_and_proximity` - observe retorna JSON com image + proximity quando ambos funcionam
- `test_observe_camera_error` - observe lida com erro de camera
- `test_observe_proximity_error` - observe lida com erro de proximity
- `test_observe_both_error` - observe lida com ambos falhando
- `test_move_lbml_direct` - move com LBML valido pula tradutor
- `test_move_lbml_invalid_still_translates` - move com input que nao e LBML passa pelo tradutor
- `test_move_natural_language_translates` - move com linguagem natural funciona como antes

## Comandos pos-fase

- `cd lbot-mcp && python -m pytest tests/ -x -v`
- `cd lbot-mcp && python -m mypy src/`

## Registro de Execucao

- Data: 2026-06-06
- Arquivos criados:
  - `lbot-mcp/src/mcp_server/tools/observe.py`
- Arquivos alterados:
  - `lbot-mcp/src/mcp_server/tools/movement.py` (adicionado deteção de LBML direto)
  - `lbot-mcp/src/mcp_server/server.py` (import e log da tool observe)
- Testes executados: `cd lbot-mcp && python -m pytest tests/ -x -v` → 47 passed, 3 skipped
- Resultado: SUCESSO - todos os testes passaram, sem regressões
- Pendencias: nenhuma