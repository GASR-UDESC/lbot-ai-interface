# Fase 06: Remover Botao "Novo Desafio" e Ajustes Finais

## Status: PENDENTE

## Objetivo

Remover completamente o botao "Novo Desafio" e sua logica do simulador, garantir A/B fixos no Modo Controle, e realizar ajustes finais de integracao.

## Pre-requisitos

- Fase 05 concluida (Fisica de rampas e validacao prontos)

## Tarefas

- [ ] Tarefa 1: Remover botao "Novo Desafio" do template
  - Arquivo: `lbot-datagen-frontend/src/app/components/robo-simulator/robo-simulator.ts`
  - O que fazer: Remover as linhas 55-57 do template (o botao com `goal-button` e `generateNewLevel()`).
  - Remover tambem a importacao do `TargetIcon` se nao for mais usado.
  - Manter o `CameraIcon` e o botao de camera.

- [ ] Tarefa 2: Remover logica `generateNewLevel()` e metodos auxiliares
  - Arquivo: `lbot-datagen-frontend/src/app/components/robo-simulator/robo-simulator.ts`
  - O que fazer: Remover o metodo `generateNewLevel()` (linhas 645-705).
  - Remover os metodos auxiliares privados relacionados:
    - `generateRandomPosition()` (linhas 707-713)
    - `generatePositionInQuadrant()` (linhas 715-742)
    - `calculateDistance()` (linhas 744-748)
    - `isPositionOnObstacle()` (linhas 750-777)
  - Se `isPositionOnObstacle` ou `calculateDistance` forem usados em outro lugar, verificar antes de remover.
  - Verificar que nenhum outro componente chama `generateNewLevel()`.

- [ ] Tarefa 3: Garantir A/B fixos no Modo Controle
  - Arquivo: `lbot-datagen-frontend/src/app/components/robo-simulator/robo-simulator.ts`
  - O que fazer: Verificar que quando `showGoals = false` (Modo Controle), o simulador usa posicoes fixas:
    - `startPoint = { x: -80, z: -80 }`
    - `goalPoint = { x: 80, z: 80 }`
  - O codigo atual ja tem isso nas linhas 114-115. Verificar que `initializeSimulator()` (linha 222-235) nao chama `generateNewLevel()` quando nao ha `levelConfig`.
  - Se `generateNewLevel()` foi removido, ajustar o `initializeSimulator()` para NUNCA randomizar A/B. Quando nao ha `levelConfig`, usar os valores fixos (-80, -80) e (80, 80).
  - Ajustar `ngOnChanges` para nao chamar `generateNewLevel()` quando `showGoals` muda (linha 180).

- [ ] Tarefa 4: Verificar e ajustar posicoes de A/B por nivel
  - Arquivo: `lbot-datagen-frontend/src/app/models/level-config.model.ts`
  - O que fazer: Verificar se as posicoes A/B de cada nivel exploram a mecanica do nivel:
    - Nivel 1: A e B posicionados para caminho quase reto
    - Nivel 2: A e B posicionados para forcar desvio pelos corredores
    - Nivel 3: A e B posicionados para que o caminho otimo passe pela rampa
    - Nivel 4: A e B posicionados para explorar o zig-zag
    - Nivel 5: A e B posicionados para explorar todos os corredores
  - Se necessario, ajustar `startPoint` e `goalPoint` de alguns niveis.
  - A regra do business-spec diz que A e B podem ter posicoes diferentes por nivel, mas distancia similar (~300-424). Os valores atuais sao (-150, -150) e (150, 150) que ja satisfazem. Podem ser mantidos, mas verificar se algum nivel se beneficia de A/B diferentes.

- [ ] Tarefa 5: Playtest final e ajustes de integracao
  - Arquivo: `lbot-datagen-frontend/src/app/components/robo-simulator/robo-simulator.ts`
  - O que fazer: Rodar o jogo completo (5 niveis) e verificar:
    - Nenhum erro no console
    - Transicao entre niveis mantem as cores/temas corretamente
    - O botao "Novo Desafio" nao aparece em nenhum modo
    - O Modo Controle funciona com A/B fixos
    - O robo comeca sempre com rotacao 0 (olhando +Z)
    - O sky color, chao, paredes e obstaculos mudam corretamente entre niveis
    - Performance mantida (60 FPS)
  - Corrigir quaisquer bugs encontrados.

- [ ] Tarefa 6: Verificar se `generateNewLevel` e usado em outro lugar
  - Arquivo: `lbot-datagen-frontend/src/app/components/robo-simulator/robo-simulator.ts`
  - O que fazer: Buscar no projeto por `generateNewLevel` para garantir que nenhum outro componente chama.
  - Se houver referencias, decidir se remove ou deprecia.

## Arquivos Referencia

- `lbot-datagen-frontend/src/app/components/robo-simulator/robo-simulator.ts` - Componente principal a ser modificado.
- `lbot-datagen-frontend/src/app/pages/controls/controls.page.ts` - Modo Controle que usa `[showGoals]="false"`.
- `lbot-datagen-frontend/src/app/pages/controls/controls.page.html` - Template do Modo Controle.
- `lbot-datagen-frontend/src/app/pages/game/game.page.html` - Template do modo de niveis (Jogar Desafios).
- `lbot-datagen-frontend/src/app/models/level-config.model.ts` - Posicoes A/B dos niveis.

## Criterios de Aceite

- [ ] CA01: O botao "Novo Desafio" NAO esta presente no template do robo-simulator
- [ ] CA02: A logica `generateNewLevel()` foi removida ou marcada como @deprecated
- [ ] CA03: No Modo Controle, A e B estao em posicoes fixas (-80, -80) e (80, 80)
- [ ] CA04: No modo de niveis, A e B sempre vem do `LevelConfig`
- [ ] CA05: O robo sempre comeca com rotacao 0 (olhando +Z)
- [ ] CA06: Transicao entre niveis mantem performance e nao quebra
- [ ] CA07: Compilacao passa sem erros
- [ ] CA08: Playtest manual confirma que todos os 5 niveis funcionam

## Testes Esperados

- `test_no_new_challenge_button` - Verificar que o botao nao existe no DOM
- `test_control_mode_fixed_ab` - Verificar que no Modo Controle A/B sao fixos
- `test_level_mode_config_ab` - Verificar que no modo niveis A/B vem do LevelConfig

## Comandos pos-fase

- `cd lbot-datagen/lbot-datagen-frontend && npm run build` (verificar compilacao)
- `cd lbot-datagen/lbot-datagen-frontend && npm run test` (rodar testes existentes)
- `cd lbot-datagen/lbot-datagen-frontend && npm start` (subir app para playtest final)

## Registro de Execucao

- Data:
- Arquivos criados:
- Arquivos alterados:
- Testes executados:
- Resultado:
- Pendencias:
