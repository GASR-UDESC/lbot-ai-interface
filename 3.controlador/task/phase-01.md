# Fase 01: Prompt melhorado para aproximacao

## Status: CONCLUIDO

## Objetivo

Atualizar o `SYSTEM_PROMPT` em `personality.py` com instrucoes mais fortes e especificas sobre aproximacao, zonas de distancia, e anti-loop, conforme RF03.

## Pre-requisitos

- Nenhum

## Tarefas

- [x] Tarefa 1: Atualizar a secao "REGRAS PARA TAREFAS" do SYSTEM_PROMPT
  - Arquivo: `lbot-mcp/src/harness/personality.py`
  - O que fazer:
    - **Enfatizar que o sensor de proximidade mede o objeto mais proximo naquela direcao**, nao necessariamente o alvo. Adicionar instrucao explicita: "sempre centralize o alvo na camera ANTES de confiar na leitura de proximidade" (ja existe parcialmente — reforcar com mais enfase)
    - **Adicionar zonas de aproximacao com limites de passo:**
      - `> 80cm`: passos de ate 20cm
      - `40-80cm`: passos de no maximo 15cm
      - `< 40cm`: passos de no maximo 10cm
    - **Adicionar instrucao de parada**: "Quando a distancia frontal estiver entre 15cm e 25cm, NAO avance mais. Voce ja esta na distancia correta. Declare sucesso e informe o usuario."
    - **Adicionar instrucao anti-loop de rotacao**: "NUNCA use R5L/R5R repetidamente mais de 3 vezes quando o objeto estiver visivel. Se nao centralizar apos 2-3 rotacoes de 5 graus, tente estrategia diferente: recue 10cm, gire 20 graus na direcao oposta, ou faca um observe() para reavaliar a situacao."
    - **Atualizar o protocolo de aproximacao gradual** para usar distancias por zona (20cm quando >80cm, 15cm quando 40-80cm, 10cm quando <40cm)
    - **Manter o texto em portugues**, seguindo o estilo e tom do prompt existente
    - **NAO remover regras existentes**, apenas adicionar/esclarecer

- [x] Tarefa 2: Atualizar testes do prompt
  - Arquivo: `lbot-mcp/tests/test_personality.py`
  - O que fazer:
    - Adicionar assertions que validam a presenca das novas instrucoes no SYSTEM_PROMPT:
      - `"centralize" in prompt` e `"ANTES" in prompt` (centralizacao antes do sensor)
      - `"15cm" in prompt` e `"25cm" in prompt` (faixa de parada)
      - `"40cm" in prompt` ou `"40-80cm" in prompt` (zona intermediaria)
      - `"80cm" in prompt` (zona distante)
      - `"nao avance mais" in prompt.lower()` ou `"ja esta na distancia" in prompt.lower()`
      - `"R5L" in prompt` ou `"R5R" in prompt` ou `"rotacoes de 5" in prompt.lower()` (anti-loop)
    - Manter o teste existente de `test_tool_count` (4 ferramentas)

## Arquivos Referencia

- `lbot-mcp/src/harness/personality.py` — prompt atual que sera modificado (linhas 1-127)
- `lbot-mcp/tests/test_personality.py` — testes existentes do prompt para referencia de estilo

## Criterios de Aceite

- [x] CA11: Prompt orienta centralizacao antes de confiar no sensor
  - Cenario: O SYSTEM_PROMPT contem instrucao explicita para centralizar o objeto na camera ANTES de confiar na leitura do sensor de proximidade
- [x] CA12: Passos reduzidos na zona de aproximacao
  - Cenario: O SYSTEM_PROMPT instrui o LLM a usar passos de no maximo 10cm quando estiver a < 40cm do objeto

## Testes Esperados

- `test_prompt_contains_centralization_before_sensor` — valida que o prompt instrui centralizar antes do sensor
- `test_prompt_contains_stop_zone` — valida que ha instrucao para parar entre 15-25cm
- `test_prompt_contains_distance_zones` — valida que ha zonas 40-80cm e >80cm
- `test_prompt_contains_anti_rotation_loop` — valida que ha instrucao contra R5L/R5R repetidos

## Comandos pos-fase

```bash
cd lbot-mcp && python -m pytest tests/test_personality.py -v
```

## Registro de Execucao

- Data: 2026-06-06
- Arquivos criados: Nenhum
- Arquivos alterados:
  - `lbot-mcp/src/harness/personality.py` — Secao "REGRAS PARA TAREFAS" atualizada com zonas de aproximacao, parada automatica (15-25cm), anti-loop de rotacao, e protocolo de aproximacao gradual por zona
  - `lbot-mcp/tests/test_personality.py` — Adicionados 4 novos testes: centralizacao antes do sensor, zona de parada, zonas de distancia, anti-loop de rotacao
- Testes executados: `pytest tests/test_personality.py -v` — 19/19 passed
- Resultado: Todos os testes passaram. Nenhum teste existente quebrado.
- Pendencias: Nenhuma
