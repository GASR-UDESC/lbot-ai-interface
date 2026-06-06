# Fase 03: Refatorar agent.py (loop ReAct limpo)

## Status: CONCLUIDO

## Objetivo

Reescrever `agent.py` para ~150 linhas contendo apenas o loop ReAct (`run()`). Remover todas as validações programáticas, message trimming, sanitization, token estimation, e parsing LBML. O agente passa a usar `prompt.py`, `messages.py` e `tool_handler.py`.

Também deletar `personality.py` (substituído por `prompt.py`).

## Pre-requisitos

- Fase 01 concluída (prompt.py, messages.py, tool_handler.py existem)
- Fase 02 concluída (translate tool disponível no MCP server)

## Tarefas

- [x] Tarefa 1: Reescrever `agent.py`
  - Arquivo: `lbot-mcp/src/harness/agent.py`
  - O que fazer: Reescrever completamente o arquivo (~150 linhas) mantendo apenas:
    - **Classe `ReActAgent`** com:
      - `__init__(self, mcp_client, base_url, api_key, model, max_steps=50, verbose=False, on_event=None)`:
        - Inicializa cliente OpenAI (OpenAI-compatible)
        - Carrega system prompt e tools via `prompt.py`
        - Inicializa `_messages` com system prompt
        - Inicializa flags: `_cancelled`, `_verbose`
      - `_emit(self, event, data)`: dispara callback de evento
      - `cancel(self)`: seta `_cancelled = True`
      - `reset(self)`: reseta `_messages` para apenas system prompt
      - `history` (property): retorna cópia de `_messages`
      - `async run(self, goal: str, max_steps=None) -> str`: **loop ReAct principal**:
        1. Resetar estado, adicionar user message com goal
        2. Loop `for step in range(1, max_steps+1)`:
           - Se `_cancelled`: emitir "cancelled", retornar "Interrompido"
           - Emitir "llm_request"
           - Chamar LLM com `messages` + `tools` (tool_choice="auto")
           - Em erro: retornar mensagem de erro
           - Extrair `message` e `finish_reason` da resposta
           - Emitir "llm_response"
           - Se tem `content` e NÃO tem `tool_calls` → **terminal**: emitir "final_answer", retornar content
           - Se tem `tool_calls`:
             - Adicionar assistant message ao histórico
             - Para cada tool_call:
               - Emitir "tool_call"
               - **`camera`**: chamar `handle_camera(mcp_client)`, usar `inject_camera_image()` para adicionar imagem
               - **`proximity`**: chamar `handle_proximity(mcp_client)`, adicionar como tool result
               - **`move`**: chamar `handle_move(mcp_client, command)`, adicionar como tool result. Se `TranslationError` → **abortar missão** (emitir erro, retornar mensagem)
               - **outras tools**: chamada genérica `mcp.call_tool(name, args)`, adicionar tool result
               - Emitir "tool_result"
           - Se não tem tool_calls nem content → emitir "final_answer", retornar fallback
        3. Após loop: emitir "max_steps_reached", retornar mensagem timeout
  - **O que NÃO incluir** (removido):
    - `_validate_and_adjust_move()` (RF03)
    - `_check_proximity_goal()` (RF03)
    - `_check_rotation_loop()` (RF08)
    - `_detect_object_loss()` (RF03)
    - `_is_valid_base64()` (RF03)
    - `_trim_messages()` (RF08)
    - `_sanitize_messages()` (RF08)
    - `_estimate_tokens()` (RF08)
    - `_collect_tool_call_ids()` (RF08)
    - `_strip_images()` (modelo é multimodal, desnecessário)
    - `_extract_proximity_from_messages()` (não é mais usado sem validações)
    - `_parse_lbml_command()`, `_is_forward_command()`, `_is_rotation_command()`, `_reduce_step()`, `_parsed_to_lbml()` (não precisa parsear LBML)
    - `_summarize_messages()` (movido para messages.py)
    - `history_summary` property (CLI simplificado não usa)
    - Tracking de estado: `_last_front_proximity`, `_last_back_proximity`, `_last_position`, `_consecutive_rotations`, `_object_was_centered`, `_goal_achieved`
    - Variável `LBOT_MAX_CONTEXT_TOKENS` (RF08)

- [x] Tarefa 2: Deletar `personality.py`
  - Arquivo: `lbot-mcp/src/harness/personality.py`
  - O que fazer: Deletar o arquivo completamente (substituído por `prompt.py`)

- [x] Tarefa 3: Atualizar `__init__.py` do harness (se necessário)
  - Arquivo: `lbot-mcp/src/harness/__init__.py`
  - O que fazer: Se houver imports no `__init__.py`, atualizar. Se estiver vazio, manter vazio.

## Arquivos Referência

- `lbot-mcp/src/harness/agent.py` — Código atual (linhas 298-910, classe `ReActAgent` e método `run()`) como base para o loop ReAct
- `lbot-mcp/src/harness/prompt.py` — System prompt e tool definitions (criado na Fase 01)
- `lbot-mcp/src/harness/messages.py` — Funções de manipulação de mensagens (criado na Fase 01)
- `lbot-mcp/src/harness/tool_handler.py` — Handlers de tool calls (criado na Fase 01)
- `lbot-mcp/src/harness/mcp_client.py` — Interface do MCPClient (`call_tool`, `list_tools`)

## Critérios de Aceite

- [x] CA01: `agent.py` tem no máximo ~200 linhas
  - Cenario: Dado o arquivo agent.py refatorado / Quando conto as linhas / Então ≤ 200 linhas

- [x] CA02: Nenhuma validação programática existe em agent.py
  - Cenario: Dado o código de agent.py / Quando busco por `_validate_and_adjust_move`, `_check_proximity_goal`, `_check_rotation_loop`, `_detect_object_loss`, `_is_valid_base64`, `_trim_messages`, `_sanitize_messages`, `_estimate_tokens` / Então nenhum desses métodos existe

- [x] CA03: Nenhuma função de parsing LBML existe em agent.py
  - Cenario: Dado o código de agent.py / Quando busco por `_parse_lbml_command`, `_is_forward_command`, `_is_rotation_command`, `_reduce_step`, `_parsed_to_lbml` / Então nenhuma dessas funções existe

- [x] CA04: Agente usa `tool_handler.handle_move()` para traduzir e executar movimento
  - Cenario: Dado tool_call com nome "move" e argumentos `{"command": "ande 30cm para frente"}` / Quando o agente processa / Então chama handle_move (que traduz NL→LBML e executa)

- [x] CA05: `TranslationError` aborta a missão
  - Cenario: Dado translate falha / Quando handle_move lança TranslationError / Então agente emite evento de erro e retorna mensagem "Missão abortada: falha na tradução"

- [x] CA06: `personality.py` não existe mais
  - Cenario: Dado o diretório harness/ / Quando listo arquivos / Então personality.py não existe

## Testes Esperados

(Não há testes automatizados — RF02. Validação funcional rodando o harness com uma LLM.)

## Comandos pós-fase

```bash
# Verificar tamanho do arquivo
wc -l lbot-mcp/src/harness/agent.py

# Verificar que personality.py foi removido
test ! -f lbot-mcp/src/harness/personality.py && echo "personality.py removido"

# Verificar que o módulo importa
cd lbot-mcp && python -c "from harness.agent import ReActAgent; print('ReActAgent importado OK')"

# Verificar ausência de métodos removidos
cd lbot-mcp && python -c "
import ast, inspect
with open('src/harness/agent.py') as f:
    tree = ast.parse(f.read())
methods = [n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) or isinstance(n, ast.AsyncFunctionDef)]
forbidden = ['_validate_and_adjust_move', '_check_proximity_goal', '_check_rotation_loop', '_detect_object_loss', '_is_valid_base64', '_trim_messages', '_sanitize_messages', '_estimate_tokens', '_parse_lbml_command', '_strip_images']
found = [m for m in methods if m in forbidden]
if found:
    print(f'ERRO: Metodos nao removidos: {found}')
else:
    print('Todos os metodos proibidos foram removidos')
"
```

## Registro de Execução

- Data: 2026-06-06
- Arquivos criados:
  - Nenhum (apenas alterações e remoções)
- Arquivos alterados:
  - `lbot-mcp/src/harness/agent.py` — Reescrito completamente: de 910 linhas para 200 linhas. Apenas loop ReAct com `run()`, usando `prompt.py`, `messages.py` e `tool_handler.py`. Removidas todas as validações programáticas, parsing LBML, trimming, sanitization, tracking de estado e `history_summary`.
- Arquivos removidos:
  - `lbot-mcp/src/harness/personality.py` — Substituído por `prompt.py`
- Testes executados:
  - `wc -l agent.py`: 200 linhas (dentro do limite ~200)
  - Import check: `ReActAgent` importa sem erros
  - Verificação de métodos proibidos: todos os 16 métodos/funções removidos (apenas `__init__`, `_emit`, `cancel`, `reset`, `history`, `run` permanecem)
  - `personality.py` confirmado removido
  - Referência a `handle_move` e `TranslationError` confirmada no código
  - `__init__.py` já estava vazio, sem necessidade de alteração
- Resultado: Aprovado (todos os critérios de aceite atendidos)
- Pendências: Nenhuma
