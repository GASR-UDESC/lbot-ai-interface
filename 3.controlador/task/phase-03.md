# Fase 03: Parada automatica + deteccao de loop + limite de passos

## Status: PENDENTE

## Objetivo

Implementar no `agent.py`:
- **RF01**: Parada automatica quando o robo atinge a faixa de proximidade alvo (15-25cm) apos ter o objeto centralizado
- **RF04**: Deteccao de loop de rotacao + limite maximo de 50 passos com cancelamento automatico

Tambem inclui a alteracao do `max_steps` default de 100 para 50.

## Pre-requisitos

- Fase 02 concluida (helpers de parse LBML e extracao de proximidade ja existem em agent.py)

## Tarefas

- [ ] Tarefa 1: Alterar max_steps default para 50
  - Arquivo: `lbot-mcp/src/harness/agent.py`
  - O que fazer:
    - No `__init__` do `ReActAgent` (linha 227), alterar `max_steps: int = 100` para `max_steps: int = 50`
    - Atualizar o teste `test_max_steps_default_is_100` em `test_agent.py` para esperar 50 (renomear para `test_max_steps_default_is_50`)
    - Atualizar a mensagem de `max_steps_reached` (linha 656-658): "Atingi o numero maximo de 50 passos sem concluir o objetivo. Tente reformular o pedido ou verificar se o ambiente esta funcionando."

- [ ] Tarefa 2: Adicionar rastreadores de estado no ReActAgent
  - Arquivo: `lbot-mcp/src/harness/agent.py`
  - O que fazer: No `__init__` do `ReActAgent` (apos `self._tools = ...`), adicionar:
    - `self._last_front_proximity: float | None = None` — ultima leitura de proximidade frontal conhecida
    - `self._last_back_proximity: float | None = None` — ultima leitura de proximidade traseira
    - `self._last_position: dict | None = None` — ultima posicao {x, z, rotation} do robo
    - `self._consecutive_rotations: int = 0` — contador de passos com comandos exclusivamente de rotacao sem mudanca de posicao
    - `self._object_was_centered: bool = False` — flag: o LLM ja confirmou que o objeto esta centralizado? (true apos observe que o LLM considera "objeto centralizado")
    - `self._goal_achieved: bool = False` — flag: objetivo de aproximacao foi alcancado
    - `self._step_count: int = 0` — contador de passos (usado para o limite de 50)
  - Metodo `reset()` (linha 260): tambem resetar todos esses rastreadores

- [ ] Tarefa 3: Implementar metodo `_update_state_from_result()`
  - Arquivo: `lbot-mcp/src/harness/agent.py`
  - O que fazer: Metodo que atualiza os rastreadores apos cada tool result:
    1. Extrai proximidade frontal/traseira do resultado (usando `_extract_proximity_from_messages` ou parseando o resultado JSON da tool)
    2. Extrai posicao do robo (de observe/camera results que contem `robot_position`)
    3. Atualiza `_last_front_proximity`, `_last_back_proximity`, `_last_position`
    4. Este metodo deve ser chamado no loop principal apos processar cada tool result de `observe`, `camera`, ou `proximity`

- [ ] Tarefa 4: Implementar RF01 — Parada automatica por proximidade alvo
  - Arquivo: `lbot-mcp/src/harness/agent.py`
  - O que fazer: Metodo `_check_proximity_goal(self) -> str | None`:
    1. Se `_last_front_proximity` e None: retorna None (sem leitura)
    2. Se `15 <= _last_front_proximity <= 25`:
       - Define `_goal_achieved = True`
       - Retorna mensagem: "**[CONTROLE AUTOMATICO]** Proximidade frontal: Xcm (faixa alvo: 15-25cm). Voce chegou perto o suficiente do objeto. Declare sucesso e informe o usuario que o objetivo foi alcancado."
    3. Se `_last_front_proximity < 15`:
       - Se `_object_was_centered` for True: considera que perdeu o objeto (overshooting) → ativa protocolo de recuperacao (Fase 04), por enquanto retorna mensagem de alerta
       - Se `_object_was_centered` for False: retorna mensagem "Cuidado: muito perto de um obstaculo (Xcm). Recue um pouco e tente centralizar o alvo na camera."
    4. Senao: retorna None (fora da faixa alvo)
  - Chamar `_check_proximity_goal()` no loop principal:
    - Apos processar tool results de `observe` e `proximity`, chamar `_update_state_from_result()`
    - Em seguida, chamar `goal_msg = self._check_proximity_goal()`
    - Se `goal_msg` nao for None:
      - Injetar mensagem no contexto: `self._messages.append({"role": "user", "content": goal_msg})`
      - Emitir evento (pode ser um `tool_result` customizado ou um novo evento tipo `proximity_goal`)
      - Se `_goal_achieved`: na proxima iteracao do loop, o LLM deve responder textualmente sem tool_calls e o loop termina naturalmente. Alternativamente, forcar a parada imediata.

- [ ] Tarefa 5: Implementar RF04 — Deteccao de loop de rotacao
  - Arquivo: `lbot-mcp/src/harness/agent.py`
  - O que fazer: Metodo `_check_rotation_loop(self, command: str, parsed: list[dict]) -> str | None`:
    1. Se o comando e exclusivamente de rotacao (`_is_rotation_command(parsed)`):
       - Compara `_last_position` com a posicao atual (se disponivel no ultimo resultado)
       - Se a posicao nao mudou significativamente (delta < 5cm em x e z): incrementa `_consecutive_rotations`
       - Senao: reseta `_consecutive_rotations = 0`
    2. Se o comando NAO e de rotacao (inclui deslocamento): reseta `_consecutive_rotations = 0`
    3. Se `_consecutive_rotations >= 10`:
       - Retorna mensagem: "**[CONTROLE AUTOMATICO]** Voce executou 10 rotacoes consecutivas sem mudanca significativa de posicao. Voce pode estar em um loop de rotacao. Tente uma estrategia diferente: recue 20cm, faca um observe(), ou gire em angulos maiores (ex: 30-45 graus)."
       - Reseta `_consecutive_rotations = 0` apos injetar o alerta
    4. Senao: retorna None
  - Chamar `_check_rotation_loop()` ANTES de executar cada comando `move` (junto com `_validate_and_adjust_move`):
    - Fazer parse do comando
    - Se for LBML: chamar `_check_rotation_loop(command, parsed)`
    - Se retornar mensagem de alerta: injetar no contexto

- [ ] Tarefa 6: Implementar RF04 — Limite de 50 passos com cancelamento
  - Arquivo: `lbot-mcp/src/harness/agent.py`
  - O que fazer:
    - Incrementar `_step_count` a cada iteracao do loop (inicio do `while` loop)
    - Se `_step_count > max_steps` (50):
      - Emitir evento `max_steps_reached` com max_steps=50
      - Retornar a mensagem: "Nao consegui completar a tarefa apos 50 passos. Tente reformular o pedido ou verificar se o ambiente esta funcionando."
      - NOTA: O loop ja tem `while step < max_steps` que cuida do limite. A mudanca principal e so o default 50 e a mensagem. O `_step_count` e redundante com `step` — podemos usar o `step` existente mesmo.

- [ ] Tarefa 7: Adicionar testes
  - Arquivo: `lbot-mcp/tests/test_agent.py`
  - O que fazer:
    - `TestProximityGoal` — testa `_check_proximity_goal()`:
      - Retorna mensagem quando frente entre 15-25cm
      - Retorna None quando frente > 25cm
      - Retorna alerta quando frente < 15cm sem objeto centralizado
    - `TestLoopDetection` — testa `_check_rotation_loop()`:
      - Reseta contador com comando de deslocamento
      - Incrementa contador com comando de rotacao sem mudanca de posicao
      - Dispara alerta apos 10 rotacoes consecutivas
      - Nao incrementa se posicao mudou durante rotacao
    - `TestMaxSteps` — atualiza teste existente para 50
    - `TestStateReset` — testa que `reset()` limpa todos os rastreadores

## Arquivos Referencia

- `lbot-mcp/src/harness/agent.py` — construtor `__init__` (linhas 221-248), loop `run()` (linhas 301-659), metodo `reset()` (linha 260)
- `lbot-mcp/tests/test_agent.py` — classe `TestReActAgentMaxSteps` (linhas 587-596), estrutura de mock

## Criterios de Aceite

- [ ] CA01: Robo para ao atingir distancia alvo
  - Cenario: Robo esta se aproximando, objeto centralizado na camera, leitura frontal entre 15-25cm → mensagem injetada no contexto instruindo o LLM a declarar sucesso
- [ ] CA07: Limite de passos atingido
  - Cenario: Robo executou 50 passos sem concluir → loop interrompido, usuario informado
- [ ] CA08: Deteccao de loop de rotacao
  - Cenario: 10 passos de rotacao consecutivos sem mudanca de posicao → alerta injetado no contexto

## Testes Esperados

- `TestMaxSteps.test_max_steps_default_is_50` — atualizado de 100 para 50
- `TestProximityGoal.test_goal_when_front_in_range_15_25` — retorna mensagem de sucesso
- `TestProximityGoal.test_no_goal_when_front_above_25` — retorna None
- `TestProximityGoal.test_alert_when_front_below_15_not_centered` — retorna alerta
- `TestLoopDetection.test_resets_on_displacement_command` — zera contador
- `TestLoopDetection.test_increments_on_rotation_no_position_change` — incrementa
- `TestLoopDetection.test_alerts_after_10_consecutive_rotations` — dispara alerta
- `TestLoopDetection.test_does_not_increment_when_position_changes` — nao incrementa
- `TestStateReset.test_reset_clears_state_trackers` — reset() limpa tudo

## Comandos pos-fase

```bash
cd lbot-mcp && python -m pytest tests/test_agent.py -v
```

## Registro de Execucao

<Preenchido pelo agente durante a execucao>

- Data:
- Arquivos criados:
- Arquivos alterados:
- Testes executados:
- Resultado:
- Pendencias:
