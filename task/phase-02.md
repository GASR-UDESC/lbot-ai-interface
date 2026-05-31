# Fase 02: Fisica - Arena Walls no Ray-March + Altura Paredes

## Status: PENDENTE

## Objetivo

Garantir que as paredes perimetrais da arena bloqueiam o robot fisicamente via o sistema ray-march (isValidPosition/getMaxValidPosition). Aumentar a altura das paredes para impedir que o robot passe "por baixo" ou "por cima". Ao colidir, o robot PARA imediatamente sem bounce.

## Pre-requisitos

- Fase 01 concluida (niveis redesenhados com obstaculos que testam a fisica)

## Tarefas

- [ ] Tarefa 1: Incluir arena walls na checagem de isValidPosition()
  - Arquivo: `lbot-datagen/lbot-datagen-frontend/src/app/services/physics.service.ts`
  - O que fazer: Atualmente isValidPosition() checa apenas `ARENA_LIMIT` (190) e obstaculos. O ARENA_LIMIT ja impede ir alem das paredes, mas o valor precisa ser consistente com a parede real. Verificar que `ARENA_LIMIT = 190` corresponde a metade da arena (200) menos metade do robot (10). Ajustar se necessario. Garantir que o robot NAO pode ultrapassar a posicao da parede em nenhuma direcao.

- [ ] Tarefa 2: Aumentar altura das arena walls para 30 unidades
  - Arquivo: `lbot-datagen/lbot-datagen-frontend/src/app/services/physics.service.ts`
  - O que fazer: Na funcao `createArenaWallsBodies()`, mudar `wallHeight` de 15 para 30. Isso impede que o robot pule por cima das paredes em cenarios extremos.

- [ ] Tarefa 3: Aumentar altura visual das arena walls
  - Arquivo: `lbot-datagen/lbot-datagen-frontend/src/app/services/arena-builder.service.ts`
  - O que fazer: Na funcao `createArenaWalls()` e `createThemedWalls()`, mudar `wallHeight` de 15 para 30. Manter consistencia entre visual e physics body.

- [ ] Tarefa 4: Garantir que colisao para o robot sem bounce
  - Arquivo: `lbot-datagen/lbot-datagen-frontend/src/app/services/physics.service.ts`
  - O que fazer: Verificar que `restitution: 0.0` nos ContactMaterials garante zero bounce. Se necessario, adicionar `robotBody.velocity.set(0,0,0)` no evento 'collide' para parar completamente. Testar que accelerar contra parede nao permite atravessar.

- [ ] Tarefa 5: Ajustar getMaxValidPosition para stepSize menor
  - Arquivo: `lbot-datagen/lbot-datagen-frontend/src/app/services/physics.service.ts`
  - O que fazer: O stepSize atual e 5 unidades. Para evitar que o robot "pule" uma parede fina entre steps, reduzir para 2 unidades. Isso garante que mesmo paredes de espessura 5 (arena walls) sejam detectadas no ray-march.

## Arquivos Referencia

- `lbot-datagen/lbot-datagen-frontend/src/app/services/physics.service.ts` - Sistema de colisao atual
- `lbot-datagen/lbot-datagen-frontend/src/app/services/arena-builder.service.ts` - Dimensoes das paredes visuais
- `lbot-datagen/lbot-datagen-frontend/src/app/components/robo-simulator/robo-simulator.ts` - Como o handleCommand usa getMaxValidPosition

## Criterios de Aceite

- [ ] CA03: Robot nao atravessa parede perimetral
  - Cenario: Dado robot proximo a parede Norte (z~190), Quando envia forward distance=100 na direcao da parede, Entao robot para no ponto de contato (z<=190) e nao aparece fora da arena
- [ ] CA03-b: Accelerar contra barreira nao permite atravessar
  - Cenario: Dado robot contra a parede, Quando envia multiplos comandos forward contra a parede, Entao robot permanece na mesma posicao
- [ ] CA03-c: Robot nao passa por baixo das paredes
  - Cenario: Dado paredes com altura 30, Quando robot (altura 12) esta proximo, Entao physics body da parede cobre totalmente a altura do robot

## Testes Esperados

- `test_robot_stops_at_arena_boundary_north` - Robot para ao atingir z=190
- `test_robot_stops_at_arena_boundary_south` - Robot para ao atingir z=-190
- `test_robot_stops_at_arena_boundary_east` - Robot para ao atingir x=190
- `test_robot_stops_at_arena_boundary_west` - Robot para ao atingir x=-190
- `test_no_bounce_on_collision` - Velocidade e zero apos colisao
- `test_stepSize_detects_thin_walls` - Ray-march com step=2 detecta parede de espessura 5

## Comandos pos-fase

- `cd lbot-datagen/lbot-datagen-frontend && npx ng build`
- `cd lbot-datagen/lbot-datagen-frontend && npx ng serve` (testar mover robot contra cada parede da arena)

## Registro de Execucao

- Data:
- Arquivos criados:
- Arquivos alterados:
- Testes executados:
- Resultado:
- Pendencias:
