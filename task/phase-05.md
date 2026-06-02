# Fase 05: Testes & Validação

## Status: PENDENTE

## Objetivo

Implementar testes unitários e de integração para todos os componentes criados nas Fases 01-04. Garantir cobertura dos cenários de aceite da business-spec.

## Pré-requisitos

- Fase 01 concluída (simulador com câmera/sensores)
- Fase 02 concluída (MCP Server estrutura + backend)
- Fase 03 concluída (MCP Server tools)
- Fase 04 concluída (Harness CLI + agente)

## Tarefas

- [ ] Tarefa 1: Testes do simulador (TypeScript/Vitest)
  - Arquivo: `lbot-simulator-web/tests/api.test.ts` (novo)
  - O que fazer:
    - Criar testes de integração para os novos endpoints da API
    - Iniciar servidor Express em porta aleatória para testes
    - `test_camera_returns_image`: GET /api/camera retorna 200 com campo `image` (string não vazia)
    - `test_camera_headless_no_browser`: GET /api/camera retorna 200 mesmo sem cliente SSE ativo
    - `test_camera_error_handling`: Simular falha no renderizador, verificar resposta de erro
    - `test_sensors_center_position`: GET /api/sensors com robô em (0,0,0) retorna distâncias ~200cm
    - `test_sensors_rotated_position`: Robô rotacionado retorna distâncias assimétricas corretas
    - `test_sensors_headless`: GET /api/sensors funciona sem navegador
    - `test_sensors_with_known_state`: Configurar lastKnownState, verificar que sensores usam estado correto
    - Usar `fetch` (Node 18+ nativo) ou `undici` para chamadas HTTP
  - **Atenção**: O `gl` (headless WebGL) precisa estar disponível no ambiente de teste. O Vitest roda em Node.js (jsdom não suporta WebGL). Para o teste de câmera, pode ser necessário mock do `gl` ou usar flag para skip se GL não disponível.

- [ ] Tarefa 2: Testes unitários de sensores (TypeScript/Vitest)
  - Arquivo: `lbot-simulator-web/tests/sensors.test.ts` (novo)
  - O que fazer:
    - Testar função `computeProximity` isoladamente
    - `test_center_position`: Robô em (0,0,0) → ~200cm frente e trás
    - `test_facing_north`: Robô em (0,0,0) → frente=200 (parede em z=+200), tras=200 (parede em z=-200)
    - `test_facing_east`: Robô em (0,0,rotation=90) → frente=200 (parede em x=+200)
    - `test_near_wall_front`: Robô em (0,180,0) → frente≈20, tras≈380
    - `test_near_wall_left`: Robô em (180,0,0) → frente=200 (considerando rotação 0)
    - `test_corner_position`: Robô em (180,180,rotation=45) → distâncias corretas para paredes em ângulo
    - `test_max_distance_cap`: Distância calculada não excede 400 (cap do sensor)

- [ ] Tarefa 3: Testes do backend simulador (Python/pytest)
  - Arquivo: `lbot-mcp/tests/test_backends.py` (novo)
  - O que fazer:
    - Testar `SimulatorBackend` com mock HTTP (usando `pytest-httpx` ou `responses`)
    - `test_health_check_online`: Mock retorna 200 → `health_check()` é True
    - `test_health_check_offline`: Mock retorna erro de conexão → `health_check()` é False
    - `test_get_camera`: Mock retorna `{"image": "base64..."}` → `get_camera()` retorna string
    - `test_get_proximity`: Mock retorna `{"readings": {"frente": 50, "tras": 200}}` → ok
    - `test_execute_lbml_accepted`: Mock retorna `{"accepted": true}` → ok
    - `test_execute_lbml_rejected`: Mock retorna 409 → levanta erro apropriado
    - `test_get_state`: Mock retorna estado → `get_state()` retorna dict
    - `test_get_state_null`: Mock retorna `{"state": null}` → `get_state()` retorna None
    - `test_timeout`: Simular timeout → verificar tratamento

- [ ] Tarefa 4: Testes do wrapper do tradutor (Python/pytest)
  - Arquivo: `lbot-mcp/tests/test_translator.py` (novo)
  - O que fazer:
    - Testar `TranslatorWrapper` com o modelo real (se `.pt` disponível) OU mock
    - `test_translate_simple`: "ande 40cm pra frente" → "D40F;"
    - `test_translate_with_units`: "ande 2 metros para frente" → "D200F;"
    - `test_translate_rotation`: "vire 90 graus para direita" → "R90R;"
    - `test_translate_compound`: "ande 30cm frente, vire 90 esquerda" → "D30F;R90L;"
    - `test_translate_verbose`: Verificar que retorna (original, preprocessed, lbml)
    - `test_translate_invalid_input`: Input nonsense → TranslationError
    - `test_translate_error_lbml`: Tradução produz LBML inválida → TranslationError
    - `test_singleton_loading`: Duas chamadas ao wrapper usam mesma instância do modelo
    - **Nota**: Se modelo `.pt` não estiver disponível no CI, marcar testes com `@pytest.mark.skip` ou usar mock

- [ ] Tarefa 5: Testes de integração MCP Server (Python/pytest)
  - Arquivo: `lbot-mcp/tests/test_integration.py` (novo)
  - O que fazer:
    - Testar MCP Server com backend mockado
    - `test_server_starts`: Server inicia sem erros
    - `test_tools_registered`: 3 tools estão registradas
    - `test_camera_tool_with_mock_backend`: Tool camera retorna base64 do mock
    - `test_proximity_tool_with_mock_backend`: Tool proximity retorna leituras do mock
    - `test_move_tool_with_mock_backend`: Tool move traduz e chama backend
    - `test_move_tool_invalid_input`: Input inválido → mensagem de erro
    - `test_camera_tool_backend_error`: Backend falha → tool retorna erro amigável
    - `test_backend_switch`: Trocar variável de ambiente → backend correto é instanciado

- [ ] Tarefa 6: Testes de integração ponta-a-ponta
  - Arquivo: `lbot-mcp/tests/test_e2e.py` (novo)
  - O que fazer:
    - Teste que requer simulador rodando (marcado com `@pytest.mark.e2e`)
    - `test_full_flow_camera`: Simulador → MCP Server → tool camera → retorna imagem
    - `test_full_flow_sensors`: Simulador → MCP Server → tool proximity → retorna distâncias
    - `test_full_flow_move`: Simulador → MCP Server → tool move → executa movimento
    - Instruções no README de como rodar: iniciar simulador, depois `pytest -m e2e`

## Arquivos Referência

- `lbot-simulator-web/tests/lbml.test.ts` — Padrão de testes Vitest existente
- `lbot-simulator-web/vitest.config.ts` — Configuração Vitest (jsdom, setup)
- `lbot-simulator-web/tests/setup.ts` — Setup de testes
- `lbot-mcp/src/mcp_server/server.py` — MCP Server a ser testado
- `lbot-mcp/src/mcp_server/backends/simulator.py` — Backend a ser mockado/testado
- `lbot-mcp/src/mcp_server/translator/__init__.py` — Translator wrapper a ser testado
- `task/business-spec.md` — Cenários de aceite originais

## Critérios de Aceite

- [ ] CA01: Todos os cenários da business-spec têm pelo menos um teste
  - Cenario: Mapear CA01-CA06 da business-spec para testes nesta fase

- [ ] CA02: Testes do simulador passam (`npm test`)
  - Cenario: Rodar `npm test` em `lbot-simulator-web/`, todos os testes passam

- [ ] CA03: Testes Python passam (`pytest`)
  - Cenario: Rodar `pytest` em `lbot-mcp/`, todos os testes unitários passam

- [ ] CA04: Testes de integração passam com mock
  - Cenario: Testes que usam mock HTTP passam sem simulador real

- [ ] CA05: Cobertura de erro em todos os componentes
  - Cenario: Cada tool e backend tem teste de cenário de erro

## Testes Esperados

### Simulador (Vitest)
- `api.test.ts`: 6-8 testes de endpoint
- `sensors.test.ts`: 7 testes de cálculo geométrico

### Python (pytest)
- `test_backends.py`: 9 testes de backend com mock
- `test_translator.py`: 8 testes do tradutor
- `test_integration.py`: 8 testes do MCP Server
- `test_e2e.py`: 3 testes ponta-a-ponta (marcados e2e)

Total: ~41 testes

## Comandos pós-fase

```bash
# Simulador
cd lbot-simulator-web && npm test
cd lbot-simulator-web && npm run check

# Python
cd lbot-mcp && python -m pytest tests/ -v
cd lbot-mcp && python -m pytest tests/ -v -m "not e2e"  # sem testes que precisam de simulador
```

## Registro de Execução

*Preenchido pelo agente durante a execução*

- Data:
- Arquivos criados:
- Arquivos alterados:
- Testes executados:
- Resultado:
- Pendências:
