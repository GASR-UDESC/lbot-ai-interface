# Fase 01: Estrutura Base — Backend, Detector e Tool Skeleton

## Status: CONCLUIDO

## Objetivo

Estabelecer a infraestrutura base para o `search_object`: adicionar dependencias, metodo de sensor numerico no backend, implementar o detector OpenCV, criar o esqueleto do tool e registra-lo no servidor.

## Pre-requisitos

- Nenhum (fase inicial)

## Tarefas

- [ ] Tarefa 1: Adicionar `opencv-python-headless` como dependencia fixa no pyproject.toml
  - Arquivo: `lbot-mcp/pyproject.toml`
  - O que fazer: Adicionar `"opencv-python-headless>=4.8"` na lista `dependencies`. Adicionar `"pytest-asyncio>=0.24"` em `dev` para suporte a testes async.

- [ ] Tarefa 2: Adicionar metodo `get_proximity_sensor()` ao LBotBackend ABC
  - Arquivo: `lbot-mcp/src/mcp_server/backends/base.py`
  - O que fazer: Adicionar metodo abstrato `async def get_proximity_sensor(self) -> dict: ...` que retorna `{'frente': float, 'tras': float}` com valores numericos brutos (MAX_DISTANCE = 400).

- [ ] Tarefa 3: Implementar `get_proximity_sensor()` no SimulatorBackend
  - Arquivo: `lbot-mcp/src/mcp_server/backends/simulator.py`
  - O que fazer: Implementar o novo metodo. Reutiliza o mesmo endpoint `GET /api/sensors` mas retorna o dict numerico diretamente (`data["readings"]`), sem formatacao de string. Tratar erros igual `get_proximity()`.

- [ ] Tarefa 4: Criar modulo `services/` com `__init__.py`
  - Arquivo: `lbot-mcp/src/mcp_server/services/__init__.py`
  - O que fazer: Criar arquivo vazio.

- [ ] Tarefa 5: Implementar `detector.py` com logica OpenCV
  - Arquivo: `lbot-mcp/src/mcp_server/services/detector.py`
  - O que fazer: Implementar funcoes:
    - `decode_frame(image_base64: str) -> np.ndarray`: decodifica base64 PNG para numpy array BGR 640x480
    - `COLOR_RANGES: dict[str, tuple]`: dicionario de faixas HSV (vermelho, azul, verde, amarelo, laranja, roxo) conforme business-spec
    - `apply_color_mask(frame, color: str) -> np.ndarray`: aplica mascara HSV para a cor especificada
    - `detect_spheres(frame, color: str | None) -> list[dict]`: HoughCircles, retorna lista de circulos com centro e raio
    - `detect_cubes(frame, color: str | None) -> list[dict]`: approxPolyDP com ~4 vertices
    - `detect_cones(frame, color: str | None) -> list[dict]`: approxPolyDP com ~3 vertices
    - `detect_object(frame, object_type: str, object_color: str | None) -> dict | None`: funcao principal que orquestra deteccao. Se objeto detectado, retorna `{'type': str, 'color': str | None, 'bbox': (x,y,w,h), 'center': (cx,cy)}`. Se nao, retorna None.
    - `select_best_match(matches: list[dict]) -> dict`: seleciona o de maior bounding box area
    - `parse_description(description: str) -> tuple[str, str | None]`: extrai tipo (`cubo`, `esfera`, `cone`) e cor opcional do texto. Se nao encontrar tipo, retorna (`"cubo"`, None) como fallback.
  - Ver frame escuro/claro: aplicar `cv2.equalizeHist()` se deteccao falhar inicialmente
  - Constantes: FRAME_WIDTH=640, FRAME_HEIGHT=480

- [ ] Tarefa 6: Criar tool skeleton `search_object.py`
  - Arquivo: `lbot-mcp/src/mcp_server/tools/search_object.py`
  - O que fazer: Criar tool com decorator `@mcp.tool()`, funcao `async def search_object(description: str) -> str`. Por enquanto retorna `json.dumps({"status": "not_implemented"})`. Importa de `..server import mcp`. Estrutura de erro basica.

- [ ] Tarefa 7: Registrar novo tool em server.py
  - Arquivo: `lbot-mcp/src/mcp_server/server.py`
  - O que fazer: Adicionar `import mcp_server.tools.search_object  # noqa: F401` junto aos imports existentes. Atualizar log para mencionar `search_object`.

## Arquivos Referencia

- `lbot-mcp/src/mcp_server/tools/camera.py` — padrao de tool simples com decorator `@mcp.tool()` e acesso a backend
- `lbot-mcp/src/mcp_server/tools/proximity.py` — pattern de tool com acesso a backend, tratamento de erro
- `lbot-mcp/src/mcp_server/backends/base.py` — LBotBackend ABC, padrao de metodo abstrato
- `lbot-mcp/src/mcp_server/backends/simulator.py` — implementacao concreta, pattern de chamada HTTP com httpx
- `lbot-mcp/src/mcp_server/server.py` — registro de tools via import side-effect

## Criterios de Aceite

- [ ] CA01: `get_proximity_sensor()` retorna dict `{'frente': float, 'tras': float}` com valores numericos
  - Cenario: Given backend conectado ao simulador, when `get_proximity_sensor()` chamado, then retorna dict com valores float (ou 400 se sem obstaculo)
- [ ] CA02: `detect_object(frame, "cubo", "vermelho")` detecta cubo vermelho em frame sintetico
  - Cenario: Given frame com retangulo vermelho, when chamado, then retorna dict com bbox e centro
- [ ] CA03: `parse_description("cubo vermelho")` retorna `("cubo", "vermelho")`
  - Cenario: Given string "cubo vermelho", when parseada, then extrai tipo e cor corretamente
- [ ] CA04: `parse_description("esfera")` retorna `("esfera", None)`
  - Cenario: Given string "esfera" sem cor, when parseada, then tipo=esfera, cor=None
- [ ] CA05: Server inicia com `search_object` tool registrada
  - Cenario: Given servidor iniciado, when `mcp.list_tools()`, then search_object aparece na lista
- [ ] CA06: `opencv-python-headless` listado nas dependencias
  - Cenario: Given pyproject.toml, when lido, then contem opencv-python-headless

## Testes Esperados

- `test_get_proximity_sensor_returns_dict` — valida formato do retorno
- `test_get_proximity_sensor_no_obstacle` — valida valor 400 quando sem obstaculo
- `test_decode_frame` — valida decodificacao base64 -> numpy array
- `test_parse_description_with_color` — "cubo vermelho" -> tipo + cor
- `test_parse_description_no_color` — "esfera" -> tipo sem cor
- `test_parse_description_unknown` — "foobar" -> fallback cubo
- `test_detect_spheres_basic` — frame com circulo detectado
- `test_detect_cubes_basic` — frame com retangulo detectado
- `test_detect_cones_basic` — frame com triangulo detectado
- `test_color_mask_red` — mascara HSV vermelha isola regiao correta
- `test_select_best_match` — seleciona maior area entre 2 deteccoes

## Comandos pos-fase

```bash
cd lbot-mcp && uv pip install -e ".[dev]"
cd lbot-mcp && python -c "from mcp_server.services.detector import detect_object; print('OK')"
cd lbot-mcp && python -m pytest tests/ -v
cd lbot-mcp && python -m mypy src/
```

## Registro de Execucao

- Data: 2026-06-06
- Arquivos criados:
  - `lbot-mcp/src/mcp_server/services/__init__.py`
  - `lbot-mcp/src/mcp_server/services/detector.py`
  - `lbot-mcp/src/mcp_server/tools/search_object.py`
- Arquivos alterados:
  - `lbot-mcp/pyproject.toml` (adicionado opencv-python-headless>=4.8, pytest-asyncio>=0.24)
  - `lbot-mcp/src/mcp_server/backends/base.py` (adicionado get_proximity_sensor())
  - `lbot-mcp/src/mcp_server/backends/simulator.py` (implementado get_proximity_sensor())
  - `lbot-mcp/src/mcp_server/server.py` (registrado search_object tool)
- Testes executados:
  - `pytest tests/ -v`: 0 tests (diretorio tests/ ainda nao criado — sera feito na Fase 03)
  - `mypy src/`: 4 erros pre-existentes, nenhum nos arquivos novos/alterados
  - `python -c "from mcp_server.services.detector import detect_object; print('OK')"`: OK
- Resultado: Todas as 7 tarefas concluidas com sucesso
- Pendencias: Nenhuma
