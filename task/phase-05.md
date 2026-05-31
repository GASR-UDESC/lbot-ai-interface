# Fase 05: Testes Unitarios

## Status: PENDENTE

## Objetivo

Criar testes unitarios para os 3 services criticos: PhysicsService (colisao e limites), GameStateService (timer global e state machine), e LevelConfigService (validacao dos niveis). Os testes devem cobrir todos os cenarios de aceite da business-spec.

## Pre-requisitos

- Fase 04 concluida (toda a implementacao funcional completa)

## Tarefas

- [ ] Tarefa 1: Criar physics.service.spec.ts
  - Arquivo: `lbot-datagen/lbot-datagen-frontend/src/app/services/physics.service.spec.ts`
  - O que fazer: Criar arquivo de teste com TestBed. Testar:
    - `isValidPosition()` retorna false para posicoes fora dos limites (x > 190, x < -190, z > 190, z < -190)
    - `isValidPosition()` retorna false quando posicao colide com obstaculo Box
    - `isValidPosition()` retorna true para posicoes validas dentro da arena
    - `getMaxValidPosition()` retorna posicao intermediaria quando destino e invalido
    - `getMaxValidPosition()` retorna destino quando caminho esta livre
    - `createArenaWallsBodies()` cria 4 corpos estaticos + ground (verificar via world.bodies.length)
    - `createRobotBody()` cria corpo com mass=100 e shape Box(10,6,15)

- [ ] Tarefa 2: Criar game-state.service.spec.ts
  - Arquivo: `lbot-datagen/lbot-datagen-frontend/src/app/services/game-state.service.spec.ts`
  - O que fazer: Criar arquivo de teste. Testar:
    - `startRun()` seta phase='playing', currentLevel=1, runStartTime > 0
    - `getGlobalElapsedMs()` retorna tempo desde runStartTime
    - `completeLevel()` avanca para 'level-complete' (niveis 1-4) ou 'run-complete' (nivel 5)
    - `nextLevel()` incrementa currentLevel sem alterar runStartTime
    - `resetRun()` zera todos os signals
    - Timer global nao reseta entre niveis (runStartTime permanece apos nextLevel)
    - `formatTime()` formata corretamente (0 -> "00:00", 92000 -> "01:32")

- [ ] Tarefa 3: Criar level-config.service.spec.ts
  - Arquivo: `lbot-datagen/lbot-datagen-frontend/src/app/services/level-config.service.spec.ts`
  - O que fazer: Criar arquivo de teste. Testar:
    - `getAllLevels()` retorna exatamente 5 niveis
    - `getLevel(1-5)` retorna nivel com id correto
    - Cada nivel tem startPoint e goalPoint definidos (nao undefined)
    - Cada nivel tem pelo menos 3 obstaculos
    - Niveis 4-5 contem pelo menos um obstaculo do tipo 'ramp'
    - Todos os obstaculos estao dentro dos limites da arena (-200 < x < 200, -200 < z < 200)
    - StartPoint e goalPoint estao em posicoes diferentes
    - Nenhum obstaculo sobrepoe o startPoint ou goalPoint (margem de 20 unidades)

- [ ] Tarefa 4: Verificar configuracao do Karma/Jasmine
  - Arquivo: `lbot-datagen/lbot-datagen-frontend/karma.conf.js` e `lbot-datagen/lbot-datagen-frontend/tsconfig.spec.json`
  - O que fazer: Verificar que o projeto esta configurado para rodar testes. Se nao existir `karma.conf.js`, verificar se usa o Angular CLI default. Garantir que `tsconfig.spec.json` inclui os novos arquivos. Rodar `ng test --no-watch` para validar.

## Arquivos Referencia

- `lbot-datagen/lbot-datagen-frontend/src/app/app.spec.ts` - Unico teste existente (referencia de pattern)
- `lbot-datagen/lbot-datagen-frontend/src/app/services/physics.service.ts` - Service a testar
- `lbot-datagen/lbot-datagen-frontend/src/app/services/game-state.service.ts` - Service a testar
- `lbot-datagen/lbot-datagen-frontend/src/app/services/level-config.service.ts` - Service a testar

## Criterios de Aceite

- [ ] Todos os testes passam com `ng test --no-watch`
- [ ] PhysicsService: robot nao pode estar em posicao invalida (fora da arena ou dentro de obstaculo)
- [ ] GameStateService: timer global funciona conforme business-spec (nao para entre niveis, para no fim)
- [ ] LevelConfigService: todos os niveis sao validos (pontos acessiveis, obstaculos dentro da arena)

## Testes Esperados

- `physics.service.spec.ts`: ~7 testes (limites, colisao, ray-march, wall bodies)
- `game-state.service.spec.ts`: ~7 testes (start, complete, next, reset, timer, format)
- `level-config.service.spec.ts`: ~8 testes (count, ids, points, obstacles, ramps, bounds, overlap)

## Comandos pos-fase

- `cd lbot-datagen/lbot-datagen-frontend && npx ng test --no-watch --browsers=ChromeHeadless`

## Registro de Execucao

- Data:
- Arquivos criados:
- Arquivos alterados:
- Testes executados:
- Resultado:
- Pendencias:
