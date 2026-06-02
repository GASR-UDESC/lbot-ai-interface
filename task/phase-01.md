# Fase 01: Modelagem e Configuracao

## Status: CONCLUIDO

## Objetivo

Criar a infraestrutura compartilhada para definicao dos objetos da arena e paredes fisicas. Esta fase entrega uma unica fonte de verdade (`shared/arena-objects.ts`) contendo as definicoes geometricas, cores, posicoes e AABB dos 6 objetos, alem das definicoes das 4 paredes fisicas para cannon-es. Nenhuma alteracao de comportamento e feita no frontend ou backend nesta fase — apenas preparacao da configuracao centralizada.

## Pre-requisitos

- Nenhuma fase anterior. Esta e a primeira fase do plano tecnico.
- `task/business-spec.md` consolidado e aprovado.

## Tarefas

- [ ] Tarefa 1: Criar `shared/arena-objects.ts` com tipos e interfaces
  - Arquivo: `3.controlador/lbot-simulator-web/shared/arena-objects.ts`
  - O que fazer: Definir os tipos `ArenaObjectType` ('cube' | 'sphere' | 'cone'), `ArenaObject` (id, type, x, z, color, size) e `PhysicalWall` (x, z, width, depth, height). Exportar um array `ARENA_OBJECTS` com 6 objetos pre-definidos e um array `PHYSICAL_WALLS` com 4 paredes.
- [ ] Tarefa 2: Implementar funcoes utilitarias de AABB
  - Arquivo: `3.controlador/lbot-simulator-web/shared/arena-objects.ts`
  - O que fazer: Implementar `getObjectAABB(object)` que retorna `{ minX, maxX, minZ, maxZ }` para cada tipo de objeto (cubo, esfera, cone). Implementar `isPositionInsideArena(x, z)` para validar posicoes.
- [ ] Tarefa 3: Implementar funcao de reposicionamento automatico
  - Arquivo: `3.controlador/lbot-simulator-web/shared/arena-objects.ts`
  - O que fazer: Implementar `validateAndClampPosition(x, z)` que verifica se a posicao esta dentro da arena (±200 excluindo espessura da parede de 8) e nao sobreposta ao spawn do robo (raio 30 em (0,0)). Se invalida, retorna posicao ajustada.
- [ ] Tarefa 4: Criar testes unitarios para AABB e validacao
  - Arquivo: `3.controlador/lbot-simulator-web/tests/arena-objects.test.ts`
  - O que fazer: Testar `getObjectAABB` para cada tipo de objeto. Testar `isPositionInsideArena` para posicoes validas e invalidas. Testar `validateAndClampPosition` para reposicionamento quando sobreposto ao robo ou fora da arena.
- [ ] Tarefa 5: Verificar compilacao e consistencia dos tipos
  - Arquivo: todos os arquivos criados
  - O que fazer: Rodar `npm run check` para garantir que `shared/arena-objects.ts` compila sem erros tanto no contexto do frontend (`tsconfig.app.json`) quanto do servidor (`tsconfig.server.json`).

## Arquivos Referencia

<Arquivos existentes que o agente deve ler para entender o pattern>

- `3.controlador/lbot-simulator-web/shared/lbml.ts` - Exemplo de modulo compartilhado entre frontend e backend
- `3.controlador/lbot-simulator-web/tsconfig.app.json` - Configuracao do frontend (inclui `shared/`)
- `3.controlador/lbot-simulator-web/tsconfig.server.json` - Configuracao do servidor (inclui `shared/`)
- `3.controlador/lbot-simulator-web/src/simulator/arena.ts` - Referencia para dimensoes das paredes (arenaSize=400, wallThickness=8)
- `3.controlador/lbot-simulator-web/server/scene-renderer.ts` - Referencia para dimensoes atuais do headless (a serem corrigidas)

## Criterios de Aceite

- [ ] CA-CONFIG-01: O arquivo `shared/arena-objects.ts` existe e exporta `ARENA_OBJECTS` com exatamente 6 objetos
  - Cenario: Dado que a fase foi executada, quando importo `ARENA_OBJECTS`, entao recebo um array com 6 objetos distintos (3 cubos, 2 esferas, 1 cone) em posicoes pre-definidas.
- [ ] CA-CONFIG-02: AABB calculada corretamente para todos os tipos
  - Cenario: Dado um cubo de 15x15x15 em (0,0), quando chamo `getObjectAABB`, entao retorna `minX=-7.5, maxX=7.5, minZ=-7.5, maxZ=7.5`.
- [ ] CA-CONFIG-03: Posicao fora da arena e reposicionada
  - Cenario: Dado uma posicao (250, 250), quando chamo `validateAndClampPosition`, entao retorna uma posicao dentro dos limites validos da arena.
- [ ] CA-CONFIG-04: Posicao sobreposta ao spawn do robo e reposicionada
  - Cenario: Dado uma posicao (0, 0), quando chamo `validateAndClampPosition`, entao retorna uma posicao fora do raio de 30 unidades do centro.

## Testes Esperados

- `test_AABB_cube` - Valida AABB de cubo 15x15x15
- `test_AABB_sphere` - Valida AABB de esfera raio 10
- `test_AABB_cone` - Valida AABB aproximada de cone (base 10, altura 15)
- `test_insideArena_valid` - Posicao (-150, -150) e valida
- `test_insideArena_invalid` - Posicao (250, 250) e invalida
- `test_clampPosition_outOfBounds` - Reposiciona posicao fora da arena
- `test_clampPosition_overlapsRobot` - Reposiciona posicao sobreposta ao robo

## Comandos pos-fase

- `npm run check` - Verificar compilacao TypeScript sem erros
- `npm test` - Rodar suite de testes (deve passar os novos testes de arena-objects)

## Registro de Execucao

<Preenchido pelo agente durante a execucao>

- Data: 2026-06-02
- Arquivos criados:
  - `3.controlador/lbot-simulator-web/shared/arena-objects.ts`
  - `3.controlador/lbot-simulator-web/tests/arena-objects.test.ts`
- Arquivos alterados:
  - Nenhum (apenas criacoes)
- Testes executados:
  - `npm run check` (tsc app + server) -> 0 erros
  - `npm test` (vitest run) -> 41/41 passaram (incluindo 11 novos testes de arena-objects)
- Resultado: SUCESSO. Configuracao centralizada criada, testada e compilando sem erros.
- Pendencias: Nenhuma
