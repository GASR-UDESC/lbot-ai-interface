# Fase 02: Reescrever system prompt e atualizar agent

## Status: CONCLUIDO

## Objetivo

Reescrever completamente o system prompt e as tool descriptions para guiar o LLM na classificacao e execucao correta de Movimentos vs Tarefas, e atualizar o ReActAgent para tratar a tool `observe` e aumentar o limite de steps.

## Pre-requisitos

- Fase 01 concluida (tools `observe` e `move` modificada devem estar disponiveis)

## Tarefas

- [x] Tarefa 1: Reescrever o `SYSTEM_PROMPT` em `lbot-mcp/src/harness/personality.py`
  - Arquivo: `lbot-mcp/src/harness/personality.py`
  - O que fazer:
    - Reescrever completamente a constante `SYSTEM_PROMPT` com as seguintes secoes:
    
    **Identidade e ambiente:**
    - Manter descricao do robo E-Puck, da arena 4m x 4m, posicao inicial no centro
    - Mencionar que o sensor de proximidade reflete o que esta centralizado exatamente a frente do robo
    
    **Classificacao de acoes:**
    - Explicar os 3 tipos: Movimento Bem Definido, Movimento Ambiguo, Tarefa
    - Movimento Bem Definido: distancias e direcoes claras, usar tool `move` com linguagem natural
    - Movimento Ambiguo: sem distancias especificas (faca um quadrado, de uma volta), gerar LBML direto e enviar via `move`
    - Tarefa: exige raciocinio, camera, sensores, multiplos passos; usar `observe` e `move` em loop
    
    **Ferramentas:**
    - `camera()`: Captura imagem (para consultas simples do usuario, tipo "o que voce ve?")
    - `proximity()`: Le sensores (para consultas simples, tipo "qual a distancia ate a parede?")
    - `observe()`: Camera + proximidade juntos(destinado a Tarefas, economiza steps)
    - `move(command)`: Executa movimento. Aceita linguagem natural OU LBML direto (para movimentos ambiguos)
    
    **Regras para Movimentos:**
    - Movimentos bem definidos: enviar comando NL via `move`, o tradutor converte para LBML
    - Movimentos ambiguos: gerar LBML e enviar via `move` diretamente
    - Formato LBML: `D<distancia><direcao>;R<angulo><direcao>;` (D=deslocamento cm, R=rotacao graus; direcoes: F/B/L/R para D, L/R para R)
    - Exemplos de LBML: `D50F;R90L;D50F;R90L;D50F;R90L;D50F;R90L;` (quadrado)
    - Nenhum uso de camera ou sensores para Movimentos
    
    **Regras para Tarefas:**
    - SEMPRE usar `observe` (nao camera+proximity separados) durante Tarefas
    - `camera` e `proximity` sozinhos sao para consultas simples do usuario
    - Manter distancia de seguranca de 20cm (frente e tras)
    - Centralizar objeto na camera antes de confiar no sensor de proximidade
    - Protocolo de busca: girar 90 graus, `observe`, repetir ate 360 graus
    - Protocolo de objeto perdido: recuar 20cm, girar 90 em 90, `observe`, se 360 sem encontrar, informar
    - Se distancia frontal <= 20cm durante aproximacao: parar, nao avancar mais
    
    **Regras gerais:**
    - Responder em portugues, ser honesto sobre limitacoes
    - Distancias acima de 400cm sao impossiveis (limite da arena)
    - Se acao impossivel, informar ao usuario
    - Nao inventar capacidades
    
    **Formato LBML (para referencia do LLM):**
    - `<distancia>`: valor numerico em cm
    - `<direcao>` para deslocamento: F (frente), B (tras), L (esquerda), R (direita)
    - `<angulo>`: valor numerico em graus
    - `<direcao>` para rotacao: L (esquerda), R (direita)
    - Comandos separados por `;`
    - Exemplos: `D30F;` (30cm para frente), `R90L;` (rotacao 90 graus a esquerda), `D50F;R90L;D30B;`

- [x] Tarefa 2: Atualizar `get_tools_description()` em `lbot-mcp/src/harness/personality.py`
  - Arquivo: `lbot-mcp/src/harness/personality.py`
  - O que fazer:
    - Adicionar a tool `observe` com parametros vazios (como `camera` e `proximity`)
    - Atualizar descricao do `move` para mencionar que aceita tanto linguagem natural quanto LBML direto
    - Atualizar descricao do `camera` para enfatizar que e para consultas simples
    - Atualizar descricao do `proximity` para enfatizar que e para consultas simples
    - Ordem das tools: observe, camera, proximity, move (observe primeiro pois e a principal para Tarefas)

- [x] Tarefa 3: Atualizar handler de tools no `lbot-mcp/src/harness/agent.py`
  - Arquivo: `lbot-mcp/src/harness/agent.py`
  - O que fazer:
    - Alterar `max_steps` default de 20 para 100 na linha 227
    - Adicionar tratamento para tool `observe` no loop de processamento de tool_calls (similar ao tratamento de `camera`):
      - Se `tool_name == "observe"`: parsear JSON do resultado
      - Se tiver campo `image` com base64 valido: injetar como user message com image_url (mesmo padrao da camera)
      - Incluir texto de proximidade na mensagem junto com a imagem
      - Se tiver campo `proximity`: formatar leituras de frente/tras no texto da mensagem
      - Se tiver `proximity_error`: mencionar que proximidade nao esta disponivel
      - Se tiver `camera_error`: tratar como erro de camera
    - Manter o handler especial para `move` (que ja extrai `command` do raw_args)
    - Manter o handler especial para `camera` (que ja existe)
    - Para outras tools (proximity): manter comportamento padrão (append como tool message)

- [x] Tarefa 4: Atualizar handler do CLI para `observe` em `lbot-mcp/src/harness/cli.py`
  - Arquivo: `lbot-mcp/src/harness/cli.py`
  - O que fazer:
    - O CLI ja exibe tool_call e tool_result genericamente, mas deve ser verificado se o output do `observe` (que e JSON grande com base64) precisa ser truncado ou formatado de forma especial no display
    - Atualizar o `_print_event` para formatar resultados de `observe` de forma mais legivel (mostrar texto de proximidade, nao o JSON inteiro)
    - Garantir que o resumo de mensagens em `_summarize_messages` trate observe igual a camera (marcar como [imagem])

## Arquivos Referencia

- `lbot-mcp/src/harness/personality.py` - System prompt e tool descriptions atuais
- `lbot-mcp/src/harness/agent.py` - Handler de camera (linhas 447-513) como referencia para observe
- `lbot-mcp/src/harness/cli.py` - Print events e resumo de mensagens
- `lbot-mcp/src/mcp_server/tools/observe.py` - Tool observe criada na Fase 01
- `task/business-spec.md` - Especificacao de negocio completa (RF01-RF10, CA01-CA12)

## Criterios de Aceite

- [ ] CA01: Movimento bem definido direto ao tradutor
  - Cenario: Given que o prompt instrui sobre Movimentos bem definidos, When o LLM recebe "ande 30cm para frente", Then classifica como Movimento e envia via `move` em linguagem natural
- [ ] CA02: Movimento ambiguo expandido pelo LLM
  - Cenario: Given que o prompt instrui sobre Movimentos ambiguos e formato LBML, When o LLM recebe "faca um quadrado", Then gera LBML e envia via `move` diretamente
- [ ] CA03: Tarefa de busca de objeto
  - Cenario: Given que o prompt instrui sobre Tarefas, When o LLM recebe "encontre o cubo vermelho", Then usa `observe` para buscar em loop de 90 graus
- [ ] CA04: Centralizacao antes de proximidade
  - Cenario: Given que o prompt instrui sobre centralizacao, When o LLM avista um objeto durante Tarefa, Then gira para centralizar antes de confiar na proximidade
- [ ] CA05: Distancia de seguranca em Tarefa
  - Cenario: Given que o prompt instrui sobre distancia de seguranca, When o sensor indica <=20cm durante Tarefa, Then para e informa ao usuario
- [ ] CA06: Distancia de seguranca nao aplica em Movimento
  - Cenario: Given que o prompt distingue Movimento de Tarefa, When comando e Movimento, Then executa sem restricao de distancia
- [ ] CA07: Protocolo de objeto perdido
  - Cenario: Given que o prompt instrui sobre protocolo, When perde objeto de vista, Then recua 20cm e gira 90 em 90
- [ ] CA08: Tool observe retorna camera e proximidade
  - Cenario: Given que observe foi implementada na Fase 01, When o agente processa resultado de observe, Then injeta imagem como user message com image_url e texto de proximidade
- [ ] CA09: Acao impossivel reportada ao usuario
  - Cenario: Given que o prompt instrui sobre limites, When distancia excede 400cm, Then LLM informa impossibilidade
- [ ] CA10: Objeto inexistente
  - Cenario: Given que o prompt instrui sobre busca, When 360 graus sem encontrar, Then informa ao usuario
- [ ] CA11: Limite de steps aumentado
  - Cenario: Given que max_steps default e 100, When tarefa complexa precisa de mais de 20 steps, Then agente pode continuar ate 100
- [ ] CA12: Consulta simples com camera e proximity
  - Cenario: Given que o prompt menciona camera/proximity para consultas simples, When usuario pergunta "o que voce ve?", Then LLM pode usar camera ou proximity individualmente

## Testes Esperados

- `test_observe_handler_injects_image` - Agent injeta imagem de observe como user message
- `test_observe_handler_proximity_text` - Agent inclui texto de proximidade na mensagem
- `test_observe_handler_camera_error` - Agent trata erro de camera no observe
- `test_observe_handler_proximity_error` - Agent trata erro de proximity no observe
- `test_max_steps_default_100` - Verificar que default de max_steps e 100
- `test_system_prompt_contains_movement_rules` - Prompt menciona Movimento Bem Definido e Ambiguo
- `test_system_prompt_contains_task_rules` - Prompt menciona Tarefa, observe, distancia de seguranca
- `test_system_prompt_contains_lbml_reference` - Prompt menciona formato LBML
- `test_tools_description_has_observe` - get_tools_description() inclui observe

## Comandos pos-fase

- `cd lbot-mcp && python -m pytest tests/ -x -v`
- `cd lbot-mcp && python -m mypy src/`

## Registro de Execucao

- Data: 2026-06-06
- Arquivos criados: nenhum
- Arquivos alterados:
  - `lbot-mcp/src/harness/agent.py` (corrigido variável `observe_img_content_ok` → `observe_img_content` na linha 618)
  - `lbot-mcp/src/harness/cli.py` (movido `import json` para topo do arquivo, removido import inline)
- Testes executados: `cd lbot-mcp && python -m pytest tests/ -x -v` → 47 passed, 3 skipped
- Resultado: SUCESSO - todos os testes passaram, sem regressões
- Pendencias: nenhuma (SYSTEM_PROMPT, get_tools_description(), max_steps=100 e observe handler já estavam implementados; apenas correção de bug e limpeza de código)