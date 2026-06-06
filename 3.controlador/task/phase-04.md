# Fase 04: Protocolo de recuperacao de perda de objeto

## Status: PENDENTE

## Objetivo

Implementar no `agent.py`:
- **RF05**: Protocolo automatico de recuperacao quando o robo perde o objeto de vista durante a aproximacao

O agente detecta a perda (proximidade frontal salta de <25cm para >30cm, ou objeto some da camera) e injeta instrucoes de recuperacao no contexto do LLM.

## Pre-requisitos

- Fase 03 concluida (rastreadores `_last_front_proximity`, `_last_position`, `_object_was_centered` ja existem)

## Tarefas

- [ ] Tarefa 1: Implementar metodo `_detect_object_loss()`
  - Arquivo: `lbot-mcp/src/harness/agent.py`
  - O que fazer: Metodo `_detect_object_loss(self, current_front: float, previous_front: float | None) -> str | None`:
    1. Se `previous_front` e None: retorna None (primeira leitura, nao ha como detectar perda)
    2. Se `previous_front <= 25` E `current_front > 30`:
       - Retorna mensagem: "**[CONTROLE AUTOMATICO]** ALERTA DE PERDA DE OBJETO: A distancia frontal saltou de Xcm para Ycm (aumento > 5cm a partir da zona de aproximacao). Voce pode ter passado do objeto ou ele saiu do seu campo de visao. Protocolo de recuperacao: (1) Recue 20cm com D20B; (2) Faca observe() para re-localizar o objeto; (3) Se encontrado, centralize e retome a aproximacao com passos de no maximo 10cm; (4) Se nao encontrado apos 360 graus de busca, informe que o objeto foi perdido."
       - Define `_object_was_centered = False` (reset — o objeto nao esta mais visivel)
       - Define `_consecutive_rotations = 0` (reset do contador de loop)
    3. Senao: retorna None
  - Chamar este metodo no loop principal apos `_update_state_from_result()` (criado na Fase 03), passando a leitura de proximidade mais recente.

- [ ] Tarefa 2: Integrar deteccao de perda no loop principal
  - Arquivo: `lbot-mcp/src/harness/agent.py`
  - O que fazer:
    - Apos processar tool result de `observe` ou `proximity`:
      1. Extrai `current_front` do resultado
      2. Chama `loss_msg = self._detect_object_loss(current_front, self._last_front_proximity)`
      3. Se `loss_msg` nao for None: injeta no contexto como mensagem user:
         ```python
         self._messages.append({"role": "user", "content": loss_msg})
         ```
      4. Atualiza `_last_front_proximity = current_front`
    - O fluxo fica: processa tool result → update_state → check_proximity_goal → detect_object_loss → proxima iteracao do loop

- [ ] Tarefa 3: Ajustar `_check_proximity_goal()` para cooperar com perda de objeto
  - Arquivo: `lbot-mcp/src/harness/agent.py`
  - O que fazer:
    - No cenario onde `_last_front_proximity < 15` E `_object_was_centered == True`:
      - Em vez de apenas alertar, usar a mesma mensagem de perda de objeto (pois passou do alvo = overshooting)
      - A mensagem deve incluir a sugestao de recuo de 20cm e re-observacao
    - Atualizar `_object_was_centered = False` nesse caso

- [ ] Tarefa 4: Rastrear "objeto centralizado" via mensagens do LLM
  - Arquivo: `lbot-mcp/src/harness/agent.py`
  - O que fazer:
    - Como a deteccao de "objeto centralizado" depende da interpretacao visual do LLM (premissa do business spec), o agente precisa inferir isso das respostas do LLM
    - Apos cada resposta do LLM (assistant message), verificar se o texto contem palavras-chave indicando centralizacao: "centralizado", "centralizei", "no centro", "esta centralizado", "objeto esta no centro"
    - Se encontrar: define `_object_was_centered = True`
    - Esta verificacao ocorre na parte do loop onde `message.content` existe (antes de processar tool calls)

- [ ] Tarefa 5: Adicionar testes
  - Arquivo: `lbot-mcp/tests/test_agent.py`
  - O que fazer: Criar classe `TestObjectLossDetection`:
    - `test_no_loss_on_first_reading` — previous_front=None, retorna None
    - `test_no_loss_when_distance_normal` — previous=20, current=22 (sem salto)
    - `test_detects_loss_when_front_jumps_from_under_25_to_over_30` — previous=20, current=45 → retorna mensagem de alerta
    - `test_detects_loss_when_front_jumps_from_under_25_to_over_30_boundary` — previous=25, current=31 → retorna mensagem
    - `test_no_loss_when_already_distant` — previous=40, current=45 → retorna None (ja estava longe)
    - `test_resets_object_centered_on_loss` — verifica que `_object_was_centered` vira False apos deteccao
    - `test_resets_rotation_counter_on_loss` — verifica que `_consecutive_rotations` vira 0
  - Criar classe `TestObjectCenteredDetection`:
    - `test_detects_centered_from_llm_text` — mensagem "objeto esta centralizado" → `_object_was_centered = True`
    - `test_detects_centered_variant` — "centralizei o objeto no centro" → True
    - `test_no_centered_detection_without_keyword` — "vejo um cubo vermelho" → nao altera
  - Criar classe `TestRecoveryIntegration` (testes de integracao com mock):
    - `test_loss_message_injected_into_context` — verifica que a mensagem de perda aparece em `self._messages`

## Arquivos Referencia

- `lbot-mcp/src/harness/agent.py` — processamento de tool results (linhas 447-647), injecao de mensagens no contexto
- `lbot-mcp/tests/test_agent.py` — observer tests que mockam tool results (linhas 305-585)
- `task/business-spec.md` — RF05 (linhas 73-87), descricao detalhada do protocolo de recuperacao

## Criterios de Aceite

- [ ] CA06: Recuperacao de perda de objeto
  - Cenario: Robo esta a < 25cm do objeto e perde o objeto de vista (distancia salta para > 30cm ou objeto some da camera) → agente detecta a perda, injeta instrucao de recuperacao no contexto (recuar 20cm, re-observar, re-centralizar)

## Testes Esperados

- `TestObjectLossDetection.test_no_loss_on_first_reading`
- `TestObjectLossDetection.test_no_loss_when_distance_normal`
- `TestObjectLossDetection.test_detects_loss_when_front_jumps_from_under_25_to_over_30`
- `TestObjectLossDetection.test_detects_loss_when_front_jumps_from_under_25_to_over_30_boundary`
- `TestObjectLossDetection.test_no_loss_when_already_distant`
- `TestObjectLossDetection.test_resets_object_centered_on_loss`
- `TestObjectLossDetection.test_resets_rotation_counter_on_loss`
- `TestObjectCenteredDetection.test_detects_centered_from_llm_text`
- `TestObjectCenteredDetection.test_detects_centered_variant`
- `TestObjectCenteredDetection.test_no_centered_detection_without_keyword`
- `TestRecoveryIntegration.test_loss_message_injected_into_context`

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
