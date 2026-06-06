# Fase 02: Bloqueio de avanco + reducao de passo

## Status: CONCLUIDO

## Objetivo

Implementar no `agent.py`:
- **RF02**: Bloqueio de comandos de avanco quando a distancia frontal <= 20cm
- **RF06**: Reducao automatica do passo conforme zonas de proximidade

Ambos sao validados ANTES do comando ser enviado ao simulador, interceptando tool calls do tipo `move`.

## Pre-requisitos

- Fase 01 concluida (prompt atualizado com as zonas de distancia e regras de aproximacao)

## Tarefas

- [x] Tarefa 1: Criar funcoes helper de parse e modificacao de LBML
  - Arquivo: `lbot-mcp/src/harness/agent.py`
  - O que fazer: Adicionar NO TOPO do arquivo (abaixo dos imports e constantes existentes, antes da classe `ReActAgent`) as seguintes funcoes:
    - `_parse_lbml_command(command_str: str) -> list[dict]` — parseia string LBML (ex: "D30F;R90L;") em lista de `{"type": "D"|"R", "value": int, "direction": str}`. Usar regex similar ao `LBML_SEQUENCE_RE` em `movement.py`.
    - `_is_forward_command(parsed: list[dict]) -> bool` — retorna True se algum comando na lista for do tipo "D" com direcao "F"
    - `_is_rotation_command(parsed: list[dict]) -> bool` — retorna True se TODOS os comandos forem do tipo "R"
    - `_reduce_step(parsed: list[dict], max_distance: int) -> list[dict]` — modifica todos os comandos "D"+"F" com `value > max_distance` para `max_distance`, retorna nova lista
    - `_parsed_to_lbml(parsed: list[dict]) -> str` — reconstroi string LBML a partir da lista parseada
    - `_extract_proximity_from_messages(messages: list[dict]) -> dict | None` — varre `messages` de tras pra frente e procura a ultima leitura de proximidade. A leitura pode estar em:
      - Resultado de `observe()` como JSON: `{"proximity": {"frente": 50.0, "tras": 200.0}}`
      - Resultado de `proximity()` como texto: `"Frente: 50 cm | Trás: 200 cm"`
      - Retorna `{"frente": float, "tras": float}` ou `None` se nao encontrar

- [x] Tarefa 2: Implementar metodo `_validate_and_adjust_move()` no ReActAgent
  - Arquivo: `lbot-mcp/src/harness/agent.py`
  - O que fazer: Adicionar metodo `_validate_and_adjust_move(self, command: str) -> tuple[str, str | None]` que:
    1. Extrai a ultima leitura de proximidade do historico via `_extract_proximity_from_messages(self._messages)`
    2. Se nao ha leitura (sensor indisponivel): retorna `(command, None)` — modo fallback, sem modificacao (RF Nao-Funcional: robustez)
    3. Faz parse do comando original via `_parse_lbml_command(command)`
    4. Se NAO for LBML mas linguagem natural: retorna `(command, None)` — o tradutor cuidara depois, nao conseguimos modificar comandos NL
    5. **RF02 — Bloqueio de avanco:**
       - Se `frente <= 20` E `_is_forward_command(parsed)`:
         - Retorna `(None, "Bloqueado: distancia frontal e de Xcm, ja esta dentro da faixa de aproximacao (15-25cm). Objetivo alcancado.")`
    6. **RF06 — Reducao de passo:**
       - Se `20 < frente <= 40`: reduz passos F > 10 para 10 via `_reduce_step(parsed, 10)`, reconstroi LBML
       - Se `40 < frente <= 80`: reduz passos F > 15 para 15 via `_reduce_step(parsed, 15)`
       - Se `frente > 80`: sem reducao
       - Retorna `(lbml_modificado, mensagem_informativa)` onde a mensagem diz "Comando ajustado: D20F reduzido para D10F (proximo ao alvo, passo reduzido por seguranca)"
    7. Comandos de recuo (D*B) e rotacao (R*) NAO sao modificados

- [x] Tarefa 3: Integrar validacao no loop principal
  - Arquivo: `lbot-mcp/src/harness/agent.py`
  - O que fazer: No metodo `run()`, dentro do loop que processa tool_calls (linhas 407-430), modificar o tratamento da tool `"move"`:
    - ANTES de chamar `self._mcp.call_tool("move", ...)`, chamar `adjusted_command, block_msg = self._validate_and_adjust_move(raw_args.get("command", ""))`
    - Se `block_msg` (comando bloqueado):
      - NAO executar o movimento
      - Adicionar `block_msg` como resultado da tool (como se fosse tool_result), inserindo mensagem no `self._messages` com role "tool" e o `block_msg` como content
      - Emitir evento `tool_result` com o `block_msg`
    - Se `adjusted_command != command_original` (comando modificado):
      - Usar `adjusted_command` em vez do comando original na chamada `call_tool`
      - Apos a execucao, adicionar a mensagem informativa ao resultado OU como tool_result adicional
    - Se nenhuma modificacao: executar normalmente como ja faz hoje

- [x] Tarefa 4: Adicionar testes
  - Arquivo: `lbot-mcp/tests/test_agent.py`
  - O que fazer: Criar novas classes de teste no final do arquivo:
    - `TestLBMLHelpers` — testa `_parse_lbml_command`, `_is_forward_command`, `_is_rotation_command`, `_reduce_step`, `_parsed_to_lbml`
    - `TestProximityExtraction` — testa `_extract_proximity_from_messages` com observe JSON, proximity texto, mensagens sem proximidade, historico vazio
    - `TestCommandModification` — testa `_validate_and_adjust_move` via mock do ReActAgent:
      - Bloqueio quando frente <= 20cm e comando D20F
      - Passo reduzido para 10cm quando frente = 35cm e comando D20F
      - Passo reduzido para 15cm quando frente = 60cm e comando D20F
      - Sem modificacao quando frente = 100cm e comando D20F
      - Comandos de recuo/rotacao nao sao bloqueados nem modificados
      - Fallback quando sem leitura de proximidade

## Arquivos Referencia

- `lbot-mcp/src/harness/agent.py` — loop principal, linhas 407-430 (onde move() e chamado), e estrutura de mensagens
- `lbot-mcp/src/mcp_server/tools/movement.py` — referencia do regex LBML (`LBML_SEQUENCE_RE`, linha 8), como o parse e feito
- `lbot-mcp/tests/test_agent.py` — padrao de mock do OpenAI e estrutura de testes existentes

## Criterios de Aceite

- [x] CA02: Bloqueio de avanco por proximidade minima
  - Cenario: Ultima leitura de proximidade frontal <= 20cm, LLM envia D<dist>F → comando bloqueado, mensagem informativa retornada
- [x] CA03: Reducao de passo perto do alvo (frente ~35cm)
  - Cenario: Frente = 35cm, LLM envia D20F → modificado para D10F, LLM informado
- [x] CA04: Reducao de passo em zona intermediaria (frente ~60cm)
  - Cenario: Frente = 60cm, LLM envia D20F → modificado para D15F, LLM informado
- [x] CA05: Aproximacao normal fora de zona de reducao (frente > 80cm)
  - Cenario: Frente = 100cm, LLM envia D20F → executado sem modificacao
- [x] CA09: Comandos de recuo e rotacao nao sao bloqueados
  - Cenario: Frente <= 20cm, LLM envia D20B ou R90L → executado normalmente
- [x] CA10: Funcionamento sem sensor de proximidade
  - Cenario: Sem leitura de proximidade no historico → comando executado sem modificacao (fallback)

## Testes Esperados

- `TestLBMLHelpers.test_parse_single_forward` — "D30F;" → [{"type":"D","value":30,"direction":"F"}]
- `TestLBMLHelpers.test_parse_sequence` — "D50F;R90L;D30B;"
- `TestLBMLHelpers.test_is_forward_true` — comando D tem direcao F
- `TestLBMLHelpers.test_is_forward_false` — comando D tem direcao B
- `TestLBMLHelpers.test_is_rotation_true` — so tem R
- `TestLBMLHelpers.test_reduce_step` — D20F → D10F com max=10
- `TestLBMLHelpers.test_parsed_to_lbml` — reconstroi LBML
- `TestProximityExtraction.test_extract_from_observe_json` — observe com proximity:50
- `TestProximityExtraction.test_extract_from_proximity_text` — "Frente: 50 cm | Trás: 200 cm"
- `TestProximityExtraction.test_no_proximity_found` — retorna None
- `TestCommandModification.test_blocks_forward_when_front_lte_20`
- `TestCommandModification.test_reduces_to_10_when_front_between_20_40`
- `TestCommandModification.test_reduces_to_15_when_front_between_40_80`
- `TestCommandModification.test_no_modification_when_front_gt_80`
- `TestCommandModification.test_backward_and_rotation_not_blocked`
- `TestCommandModification.test_fallback_when_no_proximity_reading`

## Comandos pos-fase

```bash
cd lbot-mcp && python -m pytest tests/test_agent.py -v
```

## Registro de Execucao

- Data: 2026-06-06
- Arquivos criados: Nenhum
- Arquivos alterados:
  - `lbot-mcp/src/harness/agent.py` — Adicionadas 6 funcoes helper de LBML (`_parse_lbml_command`, `_is_forward_command`, `_is_rotation_command`, `_reduce_step`, `_parsed_to_lbml`, `_extract_proximity_from_messages`) e metodo `_validate_and_adjust_move()` no `ReActAgent`. Integrada validacao no loop principal (move tool handling com bloqueio e reducao de passo).
  - `lbot-mcp/tests/test_agent.py` — Adicionadas 3 novas classes de teste: `TestLBMLHelpers` (13 tests), `TestProximityExtraction` (6 tests), `TestCommandModification` (8 tests). Import atualizado para incluir as novas funcoes helper.
- Testes executados: `pytest tests/test_agent.py -v` — 47/47 passed
- Resultado: Todos os testes passaram. Nenhum teste existente quebrado. RF02 (bloqueio de avanco) e RF06 (reducao de passo) implementados.
- Pendencias: Nenhuma
