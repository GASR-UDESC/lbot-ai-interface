# Fase 01: Estrutura base do harness (prompt + messages + tool_handler)

## Status: PENDENTE

## Objetivo

Criar os três novos módulos do harness que substituirão partes de `agent.py` e `personality.py`:
- `prompt.py`: System prompt (~30-50 linhas, português) + definições das 3 ferramentas MCP
- `messages.py`: Formatação de mensagens e injeção de imagens
- `tool_handler.py`: Handlers para cada tool call (camera, proximity, move com tradução)

Nesta fase os arquivos são apenas criados — ainda não são integrados ao `agent.py`.

## Pre-requisitos

- Nenhum (fase inicial, apenas criação de arquivos novos)

## Tarefas

- [ ] Tarefa 1: Criar `prompt.py`
  - Arquivo: `lbot-mcp/src/harness/prompt.py`
  - O que fazer: Escrever system prompt em português (~30-50 linhas) adequado a modelo ~8B:
    - Identidade do robô E-Puck em arena 4m x 4m
    - Descrição clara e simples das 3 ferramentas: `camera()`, `proximity()`, `move(comando)`
    - Regras de segurança essenciais (distância mínima, verificar antes de mover)
    - Sem classificações de ações, sem protocolo de busca, sem formato LBML
    - Instrução para responder em português
  - Incluir função `get_system_prompt() -> str`
  - Incluir função `get_tools_description() -> list[dict]` com definições OpenAI-format para 3 ferramentas:
    - `camera()`: sem parâmetros, retorna imagem frontal
    - `proximity()`: sem parâmetros, retorna distâncias dos sensores
    - `move(command: string)`: recebe comando em linguagem natural (ex: "ande 30cm para frente")

- [ ] Tarefa 2: Criar `messages.py`
  - Arquivo: `lbot-mcp/src/harness/messages.py`
  - O que fazer: Implementar funções de manipulação de mensagens:
    - `build_initial_messages(system_prompt: str) -> list[dict]`: cria lista com mensagem system inicial
    - `append_user_message(messages: list, content: str) -> list`: adiciona mensagem do usuário
    - `append_assistant_message(messages: list, content: str, tool_calls=None) -> list`: adiciona resposta do assistente
    - `append_tool_result(messages: list, tool_call_id: str, tool_name: str, content: str) -> list`: adiciona resultado de tool
    - `inject_camera_image(messages: list, image_base64: str, render_method: str, robot_position: dict) -> list`: adiciona imagem da câmera como user message com `image_url` (para modelos multimodais)
    - `summarize_for_display(messages: list) -> list[dict]`: versão truncada das mensagens para output no terminal (imagens → `[imagem]`, conteúdo → 200 chars)

- [ ] Tarefa 3: Criar `tool_handler.py`
  - Arquivo: `lbot-mcp/src/harness/tool_handler.py`
  - O que fazer: Implementar handlers assíncronos para cada tool call:
    - `async handle_camera(mcp_client) -> dict`: chama `mcp.call_tool("camera", {})`, faz parse JSON, retorna dict com `image`, `render_method`, `robot_position`
    - `async handle_proximity(mcp_client) -> str`: chama `mcp.call_tool("proximity", {})`, retorna string formatada
    - `async handle_move(mcp_client, command_nl: str) -> str`: 
      1. Chama `mcp.call_tool("translate", {"command": command_nl})` para obter LBML
      2. Se resultado for `"ERRO"` ou vazio, lança `TranslationError`
      3. Chama `mcp.call_tool("move", {"command": lbml_text})` com o LBML
      4. Retorna resultado do movimento
    - Definir exceção `class TranslationError(Exception)`

## Arquivos Referência

- `lbot-mcp/src/harness/personality.py` — System prompt e tool definitions atuais (para referência do que remover/melhorar)
- `lbot-mcp/src/harness/agent.py` — Funções `_strip_images` (L142-164), `_summarize_messages` (L101-129) como base para `messages.py`; handlers de tool call no loop `run()` (L652-895) como base para `tool_handler.py`
- `lbot-mcp/src/mcp_server/translator/__init__.py` — Interface do `TranslatorWrapper` (para entender o contrato do translate)
- `lbot-mcp/src/harness/mcp_client.py` — Interface do `MCPClient` (`call_tool`, `list_tools`)

## Critérios de Aceite

- [ ] CA01: `prompt.py` importa sem erros e `get_system_prompt()` retorna string ≤ 50 linhas em português
  - Cenario: Dado o arquivo prompt.py / Quando importado e chamado get_system_prompt() / Então retorna string ≤ 50 linhas, em português, sem menção a LBML, sem classificações de ações, sem protocolo de busca

- [ ] CA02: `get_tools_description()` retorna exatamente 3 ferramentas
  - Cenario: Dado prompt.py / Quando chamado get_tools_description() / Então retorna lista com 3 itens: camera, proximity, move (sem observe)

- [ ] CA03: `messages.py` injeta imagem corretamente como user message
  - Cenario: Dado uma lista de mensagens / Quando inject_camera_image() é chamado / Então adiciona user message com image_url content block

- [ ] CA04: `tool_handler.py` faz parse correto do resultado da camera
  - Cenario: Dado JSON `{"image": "...", "render_method": "three", "robot_position": {...}}` / Quando handle_camera processa / Então retorna dict com os 3 campos

- [ ] CA05: `handle_move` lança `TranslationError` se translate retornar "ERRO"
  - Cenario: Dado mcp_client mock que retorna "ERRO" para translate / Quando handle_move é chamado / Então lança TranslationError

## Testes Esperados

(Nesta fase não há testes automatizados — RF02 remove todos os testes. A validação é via import check e revisão de código.)

## Comandos pós-fase

```bash
# Verificar que os módulos importam sem erros
cd lbot-mcp && python -c "from harness.prompt import get_system_prompt, get_tools_description; print(len(get_system_prompt().splitlines()), 'linhas'); print(len(get_tools_description()), 'ferramentas')"
python -c "from harness.messages import build_initial_messages, inject_camera_image, summarize_for_display; print('messages OK')"
python -c "from harness.tool_handler import handle_camera, handle_proximity, handle_move, TranslationError; print('tool_handler OK')"
```

## Registro de Execução

- Data:
- Arquivos criados:
- Arquivos alterados:
- Testes executados:
- Resultado:
- Pendências:
