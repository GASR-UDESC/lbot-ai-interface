# Plano Tecnico: Melhoria de Aproximacao do Robo a Objetos

## Visao Geral

O plano implementa 6 requisitos funcionais (RF01-RF06) em 4 fases incrementais, todas com escopo limitado ao `lbot-mcp` (sem modificar o `lbot-simulator-web`).

A abordagem tecnica consiste em:
1. **Melhorar o prompt** (personality.py) com instrucoes mais fortes de aproximacao
2. **Adicionar validacoes no agent loop** (agent.py) que interceptam comandos `move()` ANTES do envio ao simulador, usando a ultima leitura de proximidade parseada do historico de mensagens
3. **Adicionar rastreadores de estado** como atributos do `ReActAgent` para detectar loops, perda de objeto, e condicoes de parada

As funcoes helper de parse/modificacao de LBML ficam como helpers no proprio `agent.py`.

## Modulos Envolvidos

- **harness/agent.py**: Loop ReAct — recebe validacoes de proximidade, modificacao de comandos, rastreadores de estado (loop, step counter, last position), e condicoes de parada automatica
- **harness/personality.py**: SYSTEM_PROMPT — recebe instrucoes atualizadas de aproximacao, zonas de distancia, anti-loop
- **tests/test_agent.py**: Testes novos para parsing de proximidade, modificacao de comandos, deteccao de loop, limite de passos
- **tests/test_personality.py**: Validacao das novas secoes do prompt

## Arquivos Impactados

### Alterados
- `lbot-mcp/src/harness/agent.py` — +~200 linhas (helpers de LBML, metodos de validacao, rastreadores, injecao de mensagens)
- `lbot-mcp/src/harness/personality.py` — +~40 linhas no SYSTEM_PROMPT (instrucoes de aproximacao por zona, anti-loop)
- `lbot-mcp/tests/test_agent.py` — +~300 linhas (novas classes de teste)
- `lbot-mcp/tests/test_personality.py` — +~20 linhas (validacao de novas secoes)

### Nao alterados
- `mcp_server/tools/movement.py` (sem mudancas — validacoes ficam no agent)
- `mcp_server/tools/proximity.py`
- `mcp_server/tools/observe.py`
- `mcp_server/tools/camera.py`
- `mcp_server/backends/*`
- `mcp_client.py`, `cli.py`

## Decisoes Tecnicas

| Decisao | Opcao escolhida | Justificativa |
|---------|-----------------|---------------|
| Local das validacoes | Dentro de agent.py (ReActAgent) | O agent loop ja orquestra tool calls, tem acesso ao historico de mensagens e pode injetar mensagens no contexto do LLM. Centralizar aqui evita acoplamento com o MCP server. |
| Acesso a proximidade | Parse do historico de mensagens | Varredura reversa em `self._messages` para extrair a ultima leitura de proximidade. Zero latencia extra de rede. Leitura pode estar levemente desatualizada mas e suficiente para os checks de seguranca. |
| Estado dos rastreadores | Atributos no ReActAgent | `self._last_proximity`, `self._last_position`, `self._consecutive_rotations`, `self._step_counter`. Simples e direto, sem novos arquivos. |
| Funcoes LBML | Helpers no agent.py | Funcoes puras `_parse_lbml_distance()`, `_reduce_step()`, `_is_forward_command()`, `_is_rotation_command()` definidas no nivel do modulo (nao como metodos). Testaveis isoladamente. |
| Limite de passos | Default alterado para 50 | `ReActAgent.__init__(max_steps=50)`. Alinhado com o business spec RF04. |
| Testes | No test_agent.py existente | Segue o padrao de mock do OpenAI ja estabelecido. Novas classes: TestProximityParsing, TestCommandModification, TestLoopDetection, TestProximityGoal. |

## Dependencias entre Fases

- Fase 01 (Prompt) → Independente, pode rodar primeiro
- Fase 02 (Core Safety) → Depende da Fase 01 para o prompt mencionar as regras que serao enforced no codigo
- Fase 03 (Loop Control) → Depende da Fase 02 (usa os helpers de parse LBML e extracao de proximidade)
- Fase 04 (Recovery) → Depende da Fase 03 (usa os rastreadores de estado: last_proximity, step counter)

## Mapa de Fases

| Fase | Descricao | Modulo | RFs |
|------|-----------|--------|-----|
| 01 | Prompt melhorado para aproximacao | personality.py | RF03 |
| 02 | Bloqueio de avanco + reducao de passo | agent.py | RF02, RF06 |
| 03 | Parada automatica + deteccao de loop + limite de passos | agent.py | RF01, RF04 |
| 04 | Protocolo de recuperacao de perda de objeto | agent.py | RF05 |
