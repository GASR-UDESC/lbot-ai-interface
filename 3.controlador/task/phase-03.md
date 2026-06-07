# Fase 03: Testes, Harness e Integracao

## Status: CONCLUIDO

## Objetivo

Integrar o tool `search_object` ao harness (tool_handler + prompt), criar testes unitarios e de integracao com mock do backend, e finalizar a feature com todos os cenarios de aceite cobertos.

## Pre-requisitos

- Fase 02 concluida (orquestracao completa, tool funcional)

## Tarefas

- [x] Tarefa 1: Criar `conftest.py` com fixtures compartilhadas
  - Arquivo: `lbot-mcp/tests/conftest.py`
  - O que fazer: Criar fixtures pytest:
    - `mock_backend`: Mock do SimulatorBackend com `AsyncMock` para `get_camera()`, `get_proximity_sensor()`, `execute_lbml()`
    - `sample_frame_base64`: frame PNG 640x480 com cubo vermelho (gerado com numpy + cv2)
    - `empty_frame_base64`: frame PNG 640x480 vazio (fundo cinza)
    - `sample_camera_response`: dict `{"image": sample_frame_base64, "render_method": "webgl", "robot_position": {...}}`

- [x] Tarefa 2: Criar `test_detector.py`
  - Arquivo: `lbot-mcp/tests/test_detector.py`
  - O que fazer: Testes unitarios para todas as funcoes do detector:
    - `test_decode_frame`: decodifica base64 -> numpy array (640x480, 3 canais)
    - `test_parse_description_with_color`: "cubo vermelho" -> tipo + cor
    - `test_parse_description_no_color`: "esfera" -> tipo sem cor
    - `test_parse_description_unknown`: "foobar" -> fallback cubo
    - `test_detect_spheres`: frame com circulo preenchido
    - `test_detect_cubes`: frame com retangulo
    - `test_detect_cones`: frame com triangulo
    - `test_detect_with_color_mask`: objeto vermelho com mascara HSV
    - `test_select_best_match`: 2 objetos, seleciona maior
    - `test_equalize_histogram`: frame escuro equalizado melhora deteccao

- [x] Tarefa 3: Criar `test_search_orchestrator.py`
  - Arquivo: `lbot-mcp/tests/test_search_orchestrator.py`
  - O que fazer: Testes do orquestrador com mock backend:
    - `test_scan_detects_on_first_frame`
    - `test_scan_detects_after_rotation`
    - `test_scan_no_detection`
    - `test_scan_camera_timeout`
    - `test_center_already_centered`
    - `test_center_converges`
    - `test_center_max_attempts`
    - `test_approach_adaptive_step`
    - `test_approach_reaches_target`
    - `test_approach_obstacle_too_close`
    - `test_approach_object_too_far`
    - `test_approach_rescan_success`
    - `test_approach_rescan_failure`
    - `test_approach_max_steps`
    - `test_run_full_flow_found`
    - `test_run_full_flow_not_found`

- [x] Tarefa 4: Criar `test_search_object.py`
  - Arquivo: `lbot-mcp/tests/test_search_object.py`
  - O que fazer: Testes de integracao do tool MCP:
    - `test_search_object_empty_description`: description="" retorna erro
    - `test_search_object_none_description`: description=None retorna erro
    - `test_search_object_backend_unavailable`: RuntimeError tratado
    - `test_search_object_success`: fluxo completo com mock, verifica JSON de retorno
    - `test_search_object_not_found`: mock sem deteccao, verifica status not_found

- [x] Tarefa 5: Adicionar `handle_search_object()` ao harness
  - Arquivo: `lbot-mcp/src/harness/tool_handler.py`
  - O que fazer: Criar funcao `async def handle_search_object(mcp_client, description: str) -> str`:
    - Chama `mcp_client.call_tool("search_object", {"description": description})`
    - Parse JSON do resultado
    - Formata mensagem em portugues:
      - Found: `"Encontrei o {tipo} {cor}! Estou a aproximadamente {distancia}cm dele."`
      - Not found: `"Nao encontrei o {descricao}. {motivo}"`
      - Erro: `"Erro durante a busca: {erro}"`
    - Retorna string formatada para injecao no contexto da LLM

- [x] Tarefa 6: Adicionar `search_object` ao prompt.py
  - Arquivo: `lbot-mcp/src/harness/prompt.py`
  - O que fazer: Adicionar entrada na lista `get_tools_description()`:
    ```python
    {
        "type": "function",
        "function": {
            "name": "search_object",
            "description": (
                "Busca um objeto na arena de forma autonoma. "
                "O robo faz varredura 360°, centraliza o objeto no frame "
                "e se aproxima ate ~50cm. Use quando o usuario pedir para "
                "encontrar algo (ex: 'ache o cubo vermelho')."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "description": {
                        "type": "string",
                        "description": "Descricao do objeto a buscar (ex: 'cubo vermelho', 'esfera azul', 'cone')."
                    }
                },
                "required": ["description"],
            },
        },
    }
    ```

- [x] Tarefa 7: Executar todos os testes e validar
  - O que fazer: Rodar `pytest tests/ -v`, verificar cobertura de todos os cenarios de aceite do business-spec. Corrigir falhas.

## Arquivos Referencia

- `lbot-mcp/src/harness/tool_handler.py` — padrao `handle_camera()`, `handle_move()` para replicar
- `lbot-mcp/src/harness/prompt.py` — padrao de tool description para LLM
- `lbot-mcp/src/mcp_server/tools/search_object.py` — tool finalizado da Fase 02
- `lbot-mcp/src/mcp_server/services/search_orchestrator.py` — orquestrador da Fase 02
- `lbot-mcp/src/mcp_server/services/detector.py` — detector da Fase 01
- `lbot-mcp/src/mcp_server/backends/base.py` — interface LBotBackend para mock

## Criterios de Aceite

Mapeamento completo dos cenarios de aceite do business-spec (CA01-CA12):

- [x] CA01 (busca bem-sucedida, objeto visivel de inicio): testado em `test_run_full_flow_found`
  - Cenario: Given cubo vermelho visivel na orientacao atual, when usuario pede, then detecta, centraliza, aproxima, retorna found
- [x] CA02 (objeto encontrado apos rotacao): testado em `test_scan_detects_after_rotation`
  - Cenario: Given esfera azul fora do FOV inicial, when scan itera, then detecta apos rotacao
- [x] CA03 (objeto nao encontrado, arena sem o tipo): testado em `test_run_full_flow_not_found`
  - Cenario: Given arena sem cones, when busca cone laranja, then retorna not_found
- [x] CA04 (arena vazia): testado em `test_scan_no_detection`
  - Cenario: Given arena vazia, when busca qualquer objeto, then not_found
- [x] CA05 (multiplos objetos, seleciona maior): testado em `test_select_best_match` e `test_selects_larger_of_two`
  - Cenario: Given 2 cubos no frame, when detecta, then seleciona maior bbox
- [x] CA06 (centralizacao converge): testado em `test_center_converges`
  - Cenario: Given objeto a 150px do centro, when center, then converge em <5 iteracoes
- [x] CA07 (passos adaptativos): testado em `test_approach_adaptive_step`
  - Cenario: Given sensor=80cm e passo planejado=100cm, when approach, then passo=40cm
- [x] CA08 (perda de tracking durante aproximacao): testado em `test_approach_rescan_success`
  - Cenario: Given objeto perdido apos avanco, when re-scan, then encontra e retoma
- [x] CA09 (objeto muito longe): testado em `test_approach_object_too_far`
  - Cenario: Given sensor>400cm mas OpenCV detecta, when approach, then "object too far"
- [x] CA10 (limite centralizacao): testado em `test_center_max_attempts`
  - Cenario: Given 5 ajustes sem centralizar, when limite atingido, then "could not center"
- [x] CA11 (limite passos aproximacao): testado em `test_approach_max_steps`
  - Cenario: Given 10 passos sem atingir 50cm, when limite, then "max approach steps exceeded"
- [x] CA12 (busca de cone): testado em `test_detect_cones` e `test_detects_cone`
  - Cenario: Given cone laranja, when detecta com approxPolyDP ~3 vertices, then sucesso

## Testes Esperados

(Ver tarefas 2-4 para lista detalhada)

- `tests/test_detector.py` — ~10 testes unitarios do detector OpenCV
- `tests/test_search_orchestrator.py` — ~16 testes do orquestrador com mock
- `tests/test_search_object.py` — ~5 testes de integracao do tool

## Comandos pos-fase

```bash
cd lbot-mcp && python -m pytest tests/ -v
cd lbot-mcp && python -m mypy src/
cd lbot-mcp && python -c "from harness.tool_handler import handle_search_object; print('OK')"
```

## Registro de Execucao

- Data: 2026-06-06
- Arquivos criados:
  - `lbot-mcp/tests/__init__.py`
  - `lbot-mcp/tests/conftest.py`
  - `lbot-mcp/tests/test_detector.py`
  - `lbot-mcp/tests/test_search_orchestrator.py`
  - `lbot-mcp/tests/test_search_object.py`
- Arquivos alterados:
  - `lbot-mcp/src/harness/tool_handler.py` (adicionado `handle_search_object()`)
  - `lbot-mcp/src/harness/prompt.py` (adicionado tool `search_object`)
  - `lbot-mcp/src/mcp_server/services/search_orchestrator.py` (corrigido ordem dos checks de segurança: MIN_SAFE antes de TARGET)
- Testes executados:
  - `pytest tests/ -v`: 51 passed, 0 failed
  - `mypy src/`: 4 erros pre-existentes, nenhum nos arquivos novos/alterados
  - `python -c "from harness.tool_handler import handle_search_object; print('OK')"`: OK
- Resultado: Todas as 7 tarefas concluidas com sucesso. 51 testes cobrindo detector (25), orchestrator (18), e tool integration (8). 12/12 cenarios de aceite do business-spec cobertos. Corrigido bug de seguranca no orchestrator (checagem MIN_SAFE antes de TARGET).
- Pendencias: Nenhuma
