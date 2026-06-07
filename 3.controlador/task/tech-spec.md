# Plano Tecnico: Busca de Objetos na Arena

## Visao Geral

A feature sera implementada como um novo MCP tool `search_object(description: str)` no servidor `lbot-mcp`, com a logica de orquestracao em um modulo `services/` separado dos tools. A deteccao de objetos usa OpenCV (`opencv-python-headless`) no servidor, sem envolvimento da LLM no processamento de imagens ou calculos.

O tool `search_object` segue o padrao de registro existente (decorator `@mcp.tool()`, import side-effect em `server.py`) e acessa o backend diretamente via `get_backend()` para camera, sensores e comandos LBML.

A LLM (via harness) chama o tool quando o usuario pede para encontrar algo. Um handler `handle_search_object()` no harness formata o JSON de retorno para linguagem natural e injeta no contexto da LLM.

**Arquitetura interna do tool:**

```
search_object(description) -> SearchOrchestrator.run(description)
  ├── Fase 1: Scan (4 rotacoes de 90°, OpenCV a cada frame)
  ├── Fase 2: Center (calculo FOV, ate 5 ajustes)
  ├── Fase 3: Approach (passos adaptativos, ate 10 passos, ate 2 re-scans)
  └── Fase 4: Result (status, object_type, object_color, bounding_box, etc.)
```

## Modulos Envolvidos

- **mcp_server/tools/**: Novo tool `search_object.py` (wrapper fino, segue padrao existente)
- **mcp_server/services/**: Novo modulo com `detector.py` (OpenCV) e `search_orchestrator.py` (maquina de estados)
- **mcp_server/backends/**: `base.py` + `simulator.py` ganham metodo `get_proximity_sensor()` para leitura numerica bruta
- **mcp_server/server.py**: Registrar novo tool (import side-effect)
- **harness/**: `tool_handler.py` ganha `handle_search_object()`, `prompt.py` ganha descricao do tool
- **pyproject.toml**: Adicionar `opencv-python-headless>=4.8` como dependencia fixa
- **tests/**: Novo diretorio com `test_detector.py`, `test_search_orchestrator.py`, `test_search_object.py`

## Arquivos Impactados

### Novos
- `lbot-mcp/src/mcp_server/services/__init__.py` - modulo de servicos
- `lbot-mcp/src/mcp_server/services/detector.py` - deteccao OpenCV (HoughCircles, approxPolyDP, mascara HSV)
- `lbot-mcp/src/mcp_server/services/search_orchestrator.py` - orquestracao das 4 fases
- `lbot-mcp/src/mcp_server/tools/search_object.py` - tool MCP wrapper
- `lbot-mcp/tests/__init__.py` - pacote de testes
- `lbot-mcp/tests/test_detector.py` - testes unitarios do detector
- `lbot-mcp/tests/test_search_orchestrator.py` - testes do orquestrador
- `lbot-mcp/tests/test_search_object.py` - testes de integracao do tool
- `lbot-mcp/tests/conftest.py` - fixtures compartilhadas

### Alterados
- `lbot-mcp/pyproject.toml` - adicionar `opencv-python-headless>=4.8` e `pytest-asyncio>=0.24`
- `lbot-mcp/src/mcp_server/backends/base.py` - adicionar metodo abstrato `get_proximity_sensor()`
- `lbot-mcp/src/mcp_server/backends/simulator.py` - implementar `get_proximity_sensor()`
- `lbot-mcp/src/mcp_server/server.py` - importar `mcp_server.tools.search_object`, log
- `lbot-mcp/src/harness/tool_handler.py` - adicionar `handle_search_object()`
- `lbot-mcp/src/harness/prompt.py` - adicionar tool `search_object` na lista de descriptions

## Decisoes Tecnicas

| Decisao | Opcao escolhida | Justificativa |
|---------|-----------------|---------------|
| Arquitetura do codigo | 1 tool + services/ | Tool magro (segue padrao), logica pesada isolada em services/ testavel separadamente |
| Acesso a sensor numerico | `get_proximity_sensor()` no backend | Novo metodo no ABC + SimulatorBackend, retorna `{'frente': float, 'tras': float}`. Tool proximity continua usando `get_proximity()` existente |
| Sleep entre movimentos | `asyncio.sleep(2)` no search_orchestrator | Configurado via constante `MOVE_DELAY_SECONDS`, sem afetar outros tools |
| Decodificacao de imagem | No `detector.py` (service) | Recebe base64 do backend, decodifica com `cv2.imdecode`. Responsabilidade clara do modulo de visao |
| OpenCV como dependencia | `opencv-python-headless>=4.8` fixa | Essencial para a feature. `headless` evita dependencias GUI (libgtk, qt) |
| Test runner | pytest + pytest-asyncio | `pytest` no raiz do `lbot-mcp/`. Fixtures mockam backend. Testes assincronos com `pytest.mark.asyncio` |
| Handler no harness | `handle_search_object()` em tool_handler.py | Segue pattern existente (`handle_camera`, `handle_move`). Formata JSON para linguagem natural |
| Retorno do tool | JSON bruto | Tool retorna dict com status/type/color/box/distance. LLM interpreta via handler |
| Timeout de camera | 5 segundos por tentativa | Configurado no `backend.get_camera()` via `httpx.Timeout`. Timeout ja existe como 10s default, usamos 5s especifico para o search_object usando `asyncio.wait_for` |
| Divisao de fases | 3 fases | Fase 1: estrutura base + detector. Fase 2: orquestracao completa. Fase 3: testes + harness |

## Dependencias entre Fases

- Fase 1 -> Fase 2 (precisa do detector e estrutura base prontos)
- Fase 2 -> Fase 3 (precisa da orquestracao completa para testes de integracao)

## Mapa de Fases

| Fase | Descricao | Modulo |
|------|-----------|--------|
| 01 | Estrutura base: deps, backend raw sensor, detector OpenCV, tool skeleton | mcp_server/backends, mcp_server/services, tools, pyproject.toml |
| 02 | Orquestracao completa: scan + center + approach, tool finalizado | mcp_server/services, tools |
| 03 | Testes + harness + integracao | tests/, harness/, finalizacao |
