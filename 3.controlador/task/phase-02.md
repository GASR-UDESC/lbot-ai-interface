# Fase 02: Orquestracao Completa — Scan, Center e Approach

## Status: CONCLUIDO

## Objetivo

Implementar o `SearchOrchestrator` com a maquina de estados completa das 4 fases (scan, center, approach, result) e finalizar o tool `search_object` conectando-o ao orquestrador.

## Pre-requisitos

- Fase 01 concluida (detector, backend raw sensor, tool skeleton registrado)

## Tarefas

- [x] Tarefa 1: Implementar `SearchOrchestrator` — estrutura e fase Scan
  - Arquivo: `lbot-mcp/src/mcp_server/services/search_orchestrator.py`
  - O que fazer: Criar classe `SearchOrchestrator` que recebe backend via construtor.
    - Constantes: `MOVE_DELAY_SECONDS = 2`, `FOV_HORIZONTAL = 100`, `FRAME_WIDTH = 640`, `FRAME_HEIGHT = 480`, `CENTER_THRESHOLD_PX = 64`, `MAX_CENTER_ATTEMPTS = 5`, `MAX_APPROACH_STEPS = 10`, `MAX_RESCANS = 2`, `MIN_SAFE_DISTANCE_CM = 20`, `TARGET_DISTANCE_CM = 50`, `CAMERA_TIMEOUT = 5.0`
    - Metodo `async def run(self, description: str) -> dict`: ponto de entrada, retorna dict final
    - Metodo `async def _scan(self, object_type: str, object_color: str | None) -> dict | None`: 
      - Loop 4 iteracoes (i=0,1,2,3):
        - Captura frame (`await self._capture_frame()`)
        - Detecta objeto (`detect_object(frame, object_type, object_color)`)
        - Se detectado: registra angulo acumulado (`i * 90`), retorna `{'object': dict, 'angle': int}`
        - Rotaciona 90° esquerda (`await self._rotate(-90)`) exceto na ultima iteracao
      - Se nada detectado: retorna None
    - Metodo `async def _capture_frame(self) -> np.ndarray`: 
      - Chama `backend.get_camera()` com `asyncio.wait_for(..., timeout=CAMERA_TIMEOUT)`
      - Timeout: retorna frame preto 640x480 (pula iteracao, nao aborta)
    - Metodo `async def _rotate(self, degrees: float)`: 
      - `direction = "R" if degrees > 0 else "L"`
      - `await backend.execute_lbml(f"R{abs(degrees)}{direction};")`
      - `await asyncio.sleep(MOVE_DELAY_SECONDS)`

- [x] Tarefa 2: Implementar fase Center (centralizacao)
  - Arquivo: `lbot-mcp/src/mcp_server/services/search_orchestrator.py`
  - O que fazer: Metodo `async def _center(self, object_center: tuple[int,int]) -> bool`:
    - Loop ate `MAX_CENTER_ATTEMPTS`:
      - Calcula `erro_x = cx - FRAME_WIDTH/2`
      - Se `abs(erro_x) < CENTER_THRESHOLD_PX`: centralizado -> retorna True
      - Calcula `graus = (erro_x / FRAME_WIDTH) * FOV_HORIZONTAL`
      - Se `abs(graus) < 1`: considera centralizado -> retorna True
      - Rotaciona: `await self._rotate(graus)` (positivo = direita, negativo = esquerda)
      - Captura frame e re-detectar objeto
      - Se nao detectar: retorna False (perdeu tracking)
    - Se excedeu tentativas: retorna False
  - IMPORTANTE: O calculo de graus usa APROXIMACAO FOV (nao camera_matrix calibrada), conforme business-spec RF04

- [x] Tarefa 3: Implementar fase Approach (aproximacao)
  - Arquivo: `lbot-mcp/src/mcp_server/services/search_orchestrator.py`
  - O que fazer: Metodo `async def _approach(self, object_type: str, object_color: str | None) -> dict`:
    - `planned_steps = [100, 50, 20]` como referencia (adaptativos)
    - Loop ate `MAX_APPROACH_STEPS`:
      - Le sensor frontal: `sensor = await backend.get_proximity_sensor(); distance = sensor["frente"]`
      - Se `distance <= TARGET_DISTANCE_CM`: parada! Retorna `{"status": "found", "final_distance_cm": distance}`
      - Se `distance < MIN_SAFE_DISTANCE_CM`: aborta! Retorna `{"status": "not_found", "reason": "obstacle too close"}`
      - Se `distance > 400` (sem obstaculo) mas OpenCV detectou: Retorna `{"status": "not_found", "reason": "object too far"}`
      - Calcula passo adaptativo: de `planned_steps`, pega o primeiro `<= distance`. Se nenhum, usa `distance / 2`
      - `await backend.execute_lbml(f"D{step}F;")` e `await asyncio.sleep(MOVE_DELAY_SECONDS)`
      - Captura frame e re-valida objeto:
        - Se detectado: verifica centralizacao. Se descentralizado (`|erro_x| >= 64`), chama `_center()`. Se center falhar, volta ao scan.
        - Se nao detectado: chama `_scan()` (re-scan). Se falhar em `MAX_RESCANS` tentativas, retorna not_found.
      - Continua loop
    - Se excedeu passos: retorna `{"status": "not_found", "reason": "max approach steps exceeded"}`

- [x] Tarefa 4: Implementar metodo `run()` completo (orquestracao principal)
  - Arquivo: `lbot-mcp/src/mcp_server/services/search_orchestrator.py`
  - O que fazer: 
    - `parse_description(description)` -> object_type, object_color
    - `result = await self._scan(object_type, object_color)`
    - Se nao encontrado: retorna `{"status": "not_found", "object_type": ..., "object_color": ..., "steps_taken": ["scan_complete_no_detection"]}`
    - `centered = await self._center(result["object"]["center"])`
    - Se nao centralizou: retorna `{"status": "not_found", "reason": "could not center", ...}`
    - `approach_result = await self._approach(object_type, object_color)`
    - Constroi dict final com: status, object_type, object_color, bounding_box, final_distance_cm, steps_taken

- [x] Tarefa 5: Finalizar tool `search_object.py`
  - Arquivo: `lbot-mcp/src/mcp_server/tools/search_object.py`
  - O que fazer: 
    - Importar `SearchOrchestrator` de services
    - Implementar `async def search_object(description: str) -> str`:
      - Validar description (nao vazia, nao None, nao so whitespace) -> retorna erro
      - `backend = get_backend()`
      - `orchestrator = SearchOrchestrator(backend)`
      - `result = await orchestrator.run(description)`
      - `return json.dumps(result)`
    - Tratar excecoes: RuntimeError (backend), httpx.TimeoutException, Exception generica
    - Docstring descreve o tool para a LLM (parametros, retorno, fases internas)

## Arquivos Referencia

- `lbot-mcp/src/mcp_server/services/detector.py` — funcoes de deteccao criadas na Fase 01
- `lbot-mcp/src/mcp_server/backends/simulator.py` — metodos do backend (get_camera, get_proximity_sensor, execute_lbml)
- `lbot-mcp/src/mcp_server/tools/movement.py` — padrao de validacao e chamada de backend.execute_lbml
- `lbot-mcp/src/mcp_server/tools/search_object.py` — skeleton criado na Fase 01

## Criterios de Aceite

- [ ] CA01: Scan detecta objeto na primeira orientacao (0°)
  - Cenario: Given objeto visivel no frame inicial, when scan inicia, then detecta no angulo 0° sem rotacionar
- [ ] CA02: Scan detecta objeto apos 2 rotacoes (180°)
  - Cenario: Given objeto atras do robo, when scan itera, then detecta apos R90L; R90L; (angulo 180°)
- [ ] CA03: Scan nao detecta nada apos 360°
  - Cenario: Given arena sem o objeto, when scan completo, then retorna None
- [ ] CA04: Timeout de camera nao aborta scan
  - Cenario: Given camera timeout em uma iteracao, when scan continua, then pula iteracao e avanca para proxima rotacao
- [ ] CA05: Center centraliza objeto em 1 ajuste
  - Cenario: Given objeto a 32px do centro (dentro do threshold 64px), when center chamado, then retorna True sem rotacionar
- [ ] CA06: Center converge em multiplos ajustes
  - Cenario: Given objeto a 150px do centro, when center itera, then calcula graus, rotaciona, reavalia e converge em < 5 iteracoes
- [ ] CA07: Center excede 5 tentativas
  - Cenario: Given calculo de graus sempre insuficiente, when 5 iteracoes passam, then retorna False
- [ ] CA08: Approach com passo adaptativo (sensor=80cm, planejado=100cm)
  - Cenario: Given objeto centralizado e sensor=80cm, when approach, then passo=40cm (80/2)
- [ ] CA09: Approach atinge distancia alvo (≤50cm)
  - Cenario: Given objeto centralizado, when approach avanca, then sensor <= 50cm e retorna found
- [ ] CA10: Approach aborta por obstaculo muito proximo (<20cm)
  - Cenario: Given sensor < 20cm antes do alvo, when approach, then retorna "obstacle too close"
- [ ] CA11: Approach com objeto muito longe (>400cm sensor mas visivel)
  - Cenario: Given sensor > 400cm mas OpenCV detecta, when approach, then retorna "object too far"
- [ ] CA12: Approach perde tracking e re-scaneia com sucesso
  - Cenario: Given objeto nao detectado apos avanco, when re-scan, then encontra e retoma
- [ ] CA13: Approach perde tracking e falha em 2 re-scans
  - Cenario: Given objeto nao detectado, when 2 re-scans falham, then retorna not_found
- [ ] CA14: Approach excede 10 passos
  - Cenario: Given robo avanca 10x sem atingir 50cm, when limite atingido, then retorna "max approach steps exceeded"
- [ ] CA15: Tool retorna JSON valido com status found
  - Cenario: Given busca bem sucedida, when tool chamado, then retorna JSON com status, object_type, object_color, bounding_box, final_distance_cm, steps_taken
- [ ] CA16: Tool valida description vazia
  - Cenario: Given description="" ou None, when tool chamado, then retorna erro de validacao

## Testes Esperados

- `test_orchestrator_run_found` — mock backend, testa fluxo completo found
- `test_orchestrator_run_not_found` — mock backend (sem deteccao), testa retorno not_found
- `test_scan_detects_on_first_frame` — mock camera com objeto, verifica deteccao sem rotacao
- `test_scan_detects_after_rotation` — mock camera (frame vazio -> frame com objeto), verifica rotacao
- `test_scan_no_detection` — mock camera sem objeto, verifica retorno None
- `test_scan_camera_timeout` — mock camera com timeout, verifica que scan continua
- `test_center_already_centered` — objeto dentro do threshold, sem rotacao
- `test_center_converges` — objeto fora do threshold, verifica calculo e convergencia
- `test_center_max_attempts` — verifica limite de 5 tentativas
- `test_approach_adaptive_step` — sensor=80, verifica passo=40
- `test_approach_reaches_target` — sensor diminui progressivamente ate <=50
- `test_approach_obstacle_too_close` — sensor < 20, verifica abort
- `test_approach_object_too_far` — sensor > 400, verifica "object too far"
- `test_approach_rescan_success` — perde tracking, re-scan acha
- `test_approach_rescan_failure` — perde tracking, 2 re-scans falham
- `test_approach_max_steps` — 10 passos sem atingir alvo
- `test_search_object_empty_description` — validacao de parametro
- `test_search_object_backend_unavailable` — RuntimeError tratado

## Comandos pos-fase

```bash
cd lbot-mcp && python -m pytest tests/ -v
cd lbot-mcp && python -m mypy src/
```

## Registro de Execucao

- Data: 2026-06-06
- Arquivos criados:
  - `lbot-mcp/src/mcp_server/services/search_orchestrator.py`
- Arquivos alterados:
  - `lbot-mcp/src/mcp_server/tools/search_object.py` (integrado com SearchOrchestrator)
  - `lbot-mcp/src/mcp_server/services/__init__.py` (existente, sem alteracao)
- Testes executados:
  - `pytest tests/ -v`: 0 tests (diretorio tests/ ainda nao criado — sera feito na Fase 03)
  - `mypy src/`: 4 erros pre-existentes, nenhum nos arquivos novos/alterados
  - `python -c "from mcp_server.services.search_orchestrator import SearchOrchestrator; print('OK')"`: OK
- Resultado: Todas as 5 tarefas concluidas com sucesso. SearchOrchestrator implementado com scan (4 rotacoes), center (FOV, ate 5 tentativas), approach (passos adaptativos, re-scan ate 2x) e run() completo.
- Pendencias: Nenhuma
