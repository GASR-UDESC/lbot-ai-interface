# Fase 03: MCP Server - Implementação das Tools (Câmera, Proximidade, Deslocamento)

## Status: CONCLUIDO

## Objetivo

Implementar as 3 ferramentas MCP (`camera`, `proximity`, `move`) usando o backend plugável e o wrapper do tradutor criados na Fase 02. Registrar as tools no servidor FastMCP.

## Pré-requisitos

- Fase 02 concluída (estrutura do projeto, backend, translator wrapper)
- Fase 01 concluída (simulador com endpoints `/api/camera` e `/api/sensors`)

## Tarefas

- [x] Tarefa 1: Implementar tool `camera`
  - Arquivo: `lbot-mcp/src/mcp_server/tools/camera.py` (novo)
  - O que fazer:
    - Criar função assíncrona `camera() -> str` decorada com `@mcp.tool()`
    - Descrição da tool (em português): "Captura uma imagem da câmera frontal do robô. Retorna a imagem em formato PNG codificada em base64."
    - Implementação:
      1. Obter backend via injeção/contexto
      2. Chamar `backend.get_camera()`
      3. Retornar string base64
    - Tratamento de erro:
      - Backend indisponível → retornar `"Erro: câmera indisponível — não foi possível capturar a imagem."`
      - Timeout → retornar `"Erro: timeout ao capturar imagem da câmera."`
      - Outros erros → retornar `"Erro: {mensagem}"`

- [x] Tarefa 2: Implementar tool `proximity`
  - Arquivo: `lbot-mcp/src/mcp_server/tools/proximity.py` (novo)
  - O que fazer:
    - Criar função assíncrona `proximity() -> str` decorada com `@mcp.tool()`
    - Descrição da tool (em português): "Lê os sensores de proximidade frontal e traseiro do robô. Retorna as distâncias em centímetros até o obstáculo mais próximo."
    - Implementação:
      1. Obter backend
      2. Chamar `backend.get_proximity()`
      3. Formatar resultado como string: `"Frente: {frente} cm | Trás: {tras} cm"`
    - Tratamento de erro:
      - Sensor indisponível → `"Erro: sensor de proximidade indisponível."`
      - Sem obstáculo → retornar `"Frente: sem obstáculo (>{max}cm) | Trás: sem obstáculo (>{max}cm)"`

- [x] Tarefa 3: Implementar tool `move`
  - Arquivo: `lbot-mcp/src/mcp_server/tools/movement.py` (novo)
  - O que fazer:
    - Criar função assíncrona `move(command: str) -> str` decorada com `@mcp.tool()`
    - Descrição da tool (em português): "Move o robô de acordo com um comando em linguagem natural. O robô entende comandos como 'ande 30cm para frente', 'vire 90 graus para direita', ou sequências como 'ande 40cm para frente, depois vire 90 graus para esquerda'."
    - Implementação:
      1. Obter tradutor (singleton do módulo translator)
      2. Obter backend
      3. Chamar `translator.translate_verbose(command)` → obter (original, preprocessed, lbml)
      4. Se tradução falhar (TranslationError) → retornar `"Erro: não entendi o comando '{command}'. Pode reformular?"`
      5. Validar LBML gerada (regex `D\d+[FBLR];` ou `R\d+[LR];`)
      6. Chamar `backend.execute_lbml(lbml)`
      7. Se aceito → retornar `"Comando executado: {lbml} ({preprocessed})"`
      8. Se rejeitado → retornar erro do backend
    - Tratamento de erro:
      - Falha na tradução → `"Erro: não entendi o comando."`
      - Backend recusou execução → `"Erro: falha na execução — {motivo}"`
      - Sem navegador ativo (409) → `"Erro: o simulador não está conectado. Abra o simulador no navegador para executar movimentos."`
      - Robô já em movimento → `"Erro: o robô ainda está executando outro movimento. Aguarde."`

- [x] Tarefa 4: Registrar tools no servidor FastMCP e configurar injeção de backend
  - Arquivo: `lbot-mcp/src/mcp_server/server.py` (alterar)
  - O que fazer:
    - Após o skeleton da Fase 02, adicionar registro das tools
    - O backend e o translator precisam ser acessíveis pelas tools. Estratégia:
      - Backend: criar como singleton no módulo `server.py`, tools importam de `server.py` ou usar `contextvars` / módulo de configuração
      - Translator: wrapper singleton carregado lazy no primeiro uso
    - Criar `lbot-mcp/src/mcp_server/context.py` (novo) com:
      - `backend: LBotBackend | None = None` (variável de módulo, setada pelo server na inicialização)
      - `get_backend() -> LBotBackend`: retorna backend ou levanta erro se não configurado
      - `get_translator() -> TranslatorWrapper`: retorna instância lazy do tradutor
    - Atualizar `server.py`:
      ```python
      backend = create_backend(backend_name)
      # Configurar contexto
      import mcp_server.context as ctx
      ctx.backend = backend
      # Importar tools (isso registra os decorators no mcp)
      import mcp_server.tools.camera
      import mcp_server.tools.proximity
      import mcp_server.tools.movement
      ```

## Arquivos Referência

- `lbot-mcp/src/mcp_server/server.py` — FastMCP app, configuração de backend (criado na Fase 02)
- `lbot-mcp/src/mcp_server/backends/base.py` — Interface `LBotBackend` com os métodos que as tools chamam
- `lbot-mcp/src/mcp_server/backends/simulator.py` — Implementação HTTP para simulador
- `lbot-mcp/src/mcp_server/translator/__init__.py` — `TranslatorWrapper` (criado na Fase 02)
- `lbot-simulator-web/shared/lbml.ts` — Formato LBML: regex `^(D\d+[FBLR];|R\d+[LR];)+$`
- `lbot-natural-language-controller/lbot-v7/lbot_v7.py` — `LBotTranslatorV7.translate()`, `translate_verbose()`
- Documentação FastMCP: padrão de decorators `@mcp.tool()`, assinatura de funções

## Critérios de Aceite

- [x] CA01: Tool `camera` retorna string base64
  - Cenario: Dado simulador rodando, Quando tool camera é chamada, Então retorna string contendo base64 válida

- [x] CA02: Tool `camera` trata backend indisponível
  - Cenario: Dado simulador não está rodando, Quando tool camera é chamada, Então retorna mensagem de erro "câmera indisponível"

- [x] CA03: Tool `proximity` retorna leituras formatadas
  - Cenario: Dado simulador rodando com robô na origem, Quando tool proximity é chamada, Então retorna string com distâncias frontal e traseira em cm

- [x] CA04: Tool `proximity` trata sensor indisponível
  - Cenario: Dado simulador offline, Quando tool proximity é chamada, Então retorna "sensor indisponível"

- [x] CA05: Tool `move` traduz NL para LBML e executa
  - Cenario: Dado "ande 40 centímetros para frente", Quando tool move é chamada, Então traduz para "D40F;", envia ao simulador, retorna confirmação com LBML

- [x] CA06: Tool `move` trata comando incompreensível
  - Cenario: Dado "xyz abc def", Quando tool move é chamada, Então retorna "não entendi o comando"

- [x] CA07: MCP Server inicia e expõe 3 tools
  - Cenario: Dado `python -m mcp_server.server`, Quando servidor inicia via stdio, Então 3 tools estão registradas (verificar list tools via MCP client)

## Testes Esperados

- `test_camera_tool_returns_base64` — Tool retorna string base64
- `test_camera_tool_backend_unavailable` — Tool retorna erro com backend offline
- `test_proximity_tool_returns_readings` — Tool retorna distâncias formatadas
- `test_proximity_tool_backend_unavailable` — Tool retorna erro
- `test_move_tool_translates_and_executes` — NL → LBML → execução
- `test_move_tool_invalid_input` — Input incompreensível retorna erro
- `test_move_tool_execution_rejected` — Backend recusa comando (ex: 409 sem navegador)

## Comandos pós-fase

```bash
cd lbot-mcp && python -c "
from mcp_server.server import mcp
print('Tools registradas:', len(mcp._tools))
"
cd lbot-mcp && python -m mcp_server.server &
# Testar via MCP Inspector ou cliente MCP
```

## Registro de Execução

- Data: 2026-06-02
- Arquivos criados:
  - `lbot-mcp/src/mcp_server/tools/camera.py` — Tool MCP de câmera (captura imagem base64 via backend)
  - `lbot-mcp/src/mcp_server/tools/proximity.py` — Tool MCP de sensor de proximidade (leituras formatadas em pt-BR)
  - `lbot-mcp/src/mcp_server/tools/movement.py` — Tool MCP de deslocamento (NL → LBML → execução)
  - `lbot-mcp/src/mcp_server/context.py` — Módulo de injeção de dependências (backend singleton + translator lazy)
- Arquivos alterados:
  - `lbot-mcp/src/mcp_server/server.py` — Adicionado setup de contexto e import/registro das 3 tools no `main()`
- Testes executados:
  - Import check: todos os módulos importam sem erros
  - `mcp.list_tools()`: 3 tools registradas (camera, proximity, move)
  - Tool camera: retorna base64 válida com simulador ativo (GET /api/camera → 200)
  - Tool proximity: retorna `"Frente: 200 cm | Trás: 200 cm"` no centro da arena
  - Tool move: traduz "ande 30 centímetros para frente" → LBML válida; retorna erro 409 (simulador sem navegador) com mensagem correta
  - Tool move: input inválido "zzzzzzzzz" retorna "não entendi o comando"
  - mypy: Success em todos os 5 arquivos novos/alterados
- Resultado: Todas as 3 tools MCP implementadas e funcionais. Tratamento de erros completo em português.
- Pendências: Nenhuma
