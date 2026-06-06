# Fase 03: Testes de integracao e regressao

## Status: PENDENTE

## Objetivo

Criar testes unitarios e de integracao abrangentes para todas as alteracoes feitas nas Fases 01 e 02, garantindo que nao ha regressoes no comportamento existente e que os novos cenarios funcionam corretamente.

## Pre-requisitos

- Fase 01 concluida (tools observe e move modificada)
- Fase 02 concluida (agent, prompt, cli atualizados)

## Tarefas

- [ ] Tarefa 1: Criar testes unitarios da tool `observe`
  - Arquivo: `lbot-mcp/tests/test_observe.py` (novo)
  - O que fazer:
    - Criar classe `TestObserveTool` com os seguintes testes:
    - `test_observe_returns_camera_and_proximity`: mock do backend retornando camera e proximity validos, verificar que o resultado contem `image`, `proximity.frente`, `proximity.tras`, `render_method`
    - `test_observe_camera_error_proximity_ok`: camera com erro mas proximity ok, verificar que resultado contem `camera_error` e `proximity`
    - `test_observe_proximity_error_camera_ok`: camera ok mas proximity com erro, verificar que resultado contem `image` e `proximity_error`
    - `test_observe_both_error`: ambos com erro, verificar que resultado contem ambos os erros ou mensagem geral
    - `test_observe_timeout_camera`: camera com timeout, verificar tratamento
    - `test_observe_timeout_proximity`: proximity com timeout, verificar tratamento
    - Cada teste deve configurar `mock_backend` no `mcp_server.context` e restaurar apos

- [ ] Tarefa 2: Atualizar testes da tool `move` para LBML direto
  - Arquivo: `lbot-mcp/tests/test_integration.py` (alterar classe `TestMoveTool`)
  - O que fazer:
    - Adicionar testes na classe `TestMoveTool`:
    - `test_move_lbml_direct_execution`: input `D30F;` deve pular tradutor e executar LBML direto. Verificar que o backend.execute_lbml foi chamado com "D30F;" e que o resultado contem "LBML direto"
    - `test_move_lbml_sequence_direct_execution`: input `D50F;R90L;D50F;R90L;` deve pular tradutor e executar direto
    - `test_move_natural_language_goes_to_translator`: input "ande 30cm para frente" deve chamar o tradutor (como antes)
    - `test_move_invalid_lbml_still_uses_translator`: input que nao bate na regex (ex: "abc") deve ir para o tradutor, que retorna ERRO
    - Garantir que os testes existentes de `move` continuam passando

- [ ] Tarefa 3: Criar testes do agent para tool `observe`
  - Arquivo: `lbot-mcp/tests/test_agent.py` (alterar)
  - O que fazer:
    - Adicionar classe `TestReActAgentObserveTool` com:
    - `test_observe_success_injects_image_and_proximity`: Simular observe retornando JSON com image base64 + proximity, verificar que agente injeta user message com image_url e texto de proximidade
    - `test_observe_camera_error_only_proximity`: observe com camera_error, verificar que so texto de proximidade e retornado (sem imagem)
    - `test_observe_proximity_error_only_camera`: observe com proximity_error, verificar que imagem e injetada mas texto menciona erro de proximidade
    - `test_observe_both_error`: ambos com erro, verificar comportamento de fallback
    - `test_observe_increments_steps_correctly`: verificar que observe conta como 1 step no loop

- [ ] Tarefa 4: Criar testes de regressao do system prompt e tool descriptions
  - Arquivo: `lbot-mcp/tests/test_personality.py` (novo)
  - O que fazer:
    - Criar classe `TestSystemPrompt` com:
    - `test_prompt_mentions_movimento_bem_definido`: verificar que SYSTEM_PROMPT menciona "Movimento" e linguagem natural/tradutor
    - `test_prompt_mentions_movimento_ambiguo`: verificar que SYSTEM_PROMPT menciona movimentos ambiguos e LBML
    - `test_prompt_mentions_tarefa`: verificar que SYSTEM_PROMPT menciona "Tarefa" e raciocinio inteligente
    - `test_prompt_mentions_observe`: verificar que SYSTEM_PROMPT menciona a tool `observe`
    - `test_prompt_mentions_distancia_seguranca`: verificar que SYSTEM_PROMPT menciona "20cm" ou distancia de seguranca
    - `test_prompt_mentions_centralizacao`: verificar que SYSTEM_PROMPT menciona centralizar objeto
    - `test_prompt_mentions_limite_arena`: verificar que SYSTEM_PROMPT menciona "400cm" ou limite de arena
    - `test_prompt_mentions_lbml_format`: verificar que SYSTEM_PROMPT tem instrucoes de formato LBML
    - Criar classe `TestToolsDescription` com:
    - `test_tools_include_observe`: verificar que `get_tools_description()` retorna 4 tools (observe, camera, proximity, move)
    - `test_observe_tool_has_no_parameters`: verificar que observe nao tem parametros obrigatorios
    - `test_move_description_mentions_lbml`: verificar que descricao de move menciona LBML ou ambos os formatos

- [ ] Tarefa 5: Teste de max_steps default
  - Arquivo: `lbot-mcp/tests/test_agent.py` (alterar)
  - O que fazer:
    - Adicionar teste: `test_max_steps_default_is_100`: criar ReActAgent sem explicitar max_steps, verificar que `agent._max_steps == 100`
    - Adicionar teste: `test_max_steps_override`: criar ReActAgent com `max_steps=50`, verificar que `agent._max_steps == 50`

## Arquivos Referencia

- `lbot-mcp/tests/test_integration.py` - Padrao de testes de integracao com mock_backend
- `lbot-mcp/tests/test_agent.py` - Padrao de testes do agent com mock_mcp_client e mock_llm
- `lbot-mcp/src/mcp_server/tools/observe.py` - Tool observe (Fase 01)
- `lbot-mcp/src/mcp_server/tools/movement.py` - Tool move modificada (Fase 01)
- `lbot-mcp/src/harness/personality.py` - System prompt reescrito (Fase 02)
- `lbot-mcp/src/harness/agent.py` - Agent atualizado (Fase 02)

## Criterios de Aceite

- [ ] Todos os testes unitarios da tool observe passam
- [ ] Todos os testes de integracao da tool move (existentes + novos com LBML) passam
- [ ] Todos os testes do agent para observe handler passam
- [ ] Todos os testes de regressao do system prompt passam
- [ ] Teste de max_steps=100 passa
- [ ] Nenhum teste existente regrediu

## Testes Esperados

- Conforme detalhado nas tarefas acima

## Comandos pos-fase

- `cd lbot-mcp && python -m pytest tests/ -x -v`
- `cd lbot-mcp && python -m mypy src/`

## Registro de Execucao

- Data:
- Arquivos criados:
- Arquivos alterados:
- Testes executados:
- Resultado:
- Pendencias: