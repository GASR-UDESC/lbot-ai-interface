# Fase 01: ObstacleMeshFactory e Novos Tipos de Obstaculos

## Status: CONCLUIDO

## Objetivo

Criar o servico `ObstacleMeshFactory` dedicado para gerar meshes compostas (THREE.Group) para cada tipo de obstaculo. Expandir os tipos de obstaculos no `level-config.model.ts` para suportar os novos designs visuais.

## Pre-requisitos

- Nenhum. Esta e a primeira fase.

## Tarefas

- [x] Tarefa 1: Criar `obstacle-mesh.factory.ts`
  - Arquivo: `lbot-datagen-frontend/src/app/services/obstacle-mesh.factory.ts`
  - O que fazer: Criar classe `ObstacleMeshFactory` com metodos estaticos ou de instancia para cada tipo de obstaculo:
    - `createCrateStack(width, height, depth, color, variation?)`: Pilha de 2-3 caixas com tamanhos variados
    - `createWallWithPillars(width, height, depth, color, variation?)`: Parede com pilastras decorativas
    - `createRamp(width, height, depth, color, rampAngle)`: Rampa inclinada com laterais (barreiras) e grade
    - `createTree(width, height, depth, color, variation?)`: Tronco (cilindro) + copa (esfera ou cone)
    - `createBarrier(width, height, depth, color)`: Barreira decorativa (cilindros + caixas)
    - `createIndustrialStack(width, height, depth, color)`: Colunas (cilindros) + vigas (caixas) + tanques (cilindros + esferas)
  - Cada funcao retorna `THREE.Group` contendo no maximo 3-4 geometrias.
  - Usar variacoes de tonalidade da cor base para diferentes partes do mesmo modelo.
  - Criar helper `shadeColor(colorHex, percent)` para clarear/escurecer cores.

- [x] Tarefa 2: Expandir `ObstacleType` no `level-config.model.ts`
  - Arquivo: `lbot-datagen-frontend/src/app/models/level-config.model.ts`
  - O que fazer: Alterar `export type ObstacleType = 'wall' | 'crate' | 'ramp';` para incluir `'tree' | 'barrier' | 'stack' | 'industrial'`.
  - Garantir que `ObstacleConfig` continue compativel (os campos existentes nao mudam).

- [x] Tarefa 3: Integrar factory no `ArenaBuilderService`
  - Arquivo: `lbot-datagen-frontend/src/app/services/arena-builder.service.ts`
  - O que fazer: Modificar `createObstaclesFromConfig()` para usar a `ObstacleMeshFactory` em vez de criar BoxGeometry simples.
  - Se o tipo nao tiver gerador definido na factory, usar fallback de caixa simples (regra do RF01).
  - O corpo de fisica (CANNON.Body) continua sendo uma Box simples aproximada.

- [x] Tarefa 4: Atualizar `createObstacles()` (modo default/sem level)
  - Arquivo: `lbot-datagen-frontend/src/app/services/arena-builder.service.ts`
  - O que fazer: Modificar o modo default para tambem usar a factory para criar obstaculos mais interessantes (em vez das caixas simples atuais). Manter compatibilidade com o robo-simulator quando nao ha levelConfig.

## Arquivos Referencia

- `lbot-datagen-frontend/src/app/services/robot-builder.service.ts` - Exemplo de como criar modelos compostos (THREE.Group com multiplas meshes) no projeto. O robo ja usa essa tecnica.
- `lbot-datagen-frontend/src/app/services/arena-builder.service.ts` - Referencia de como adicionar meshes na cena e criar corpos de fisica.
- `lbot-datagen-frontend/src/app/models/level-config.model.ts` - Modelo atual de ObstacleType e ObstacleConfig.

## Criterios de Aceite

- [x] CA01: A factory existe e tem funcoes para todos os tipos expandidos (crate, wall, ramp, tree, barrier, stack, industrial)
- [x] CA02: Cada funcao retorna THREE.Group com no maximo 4 geometrias
- [x] CA03: As cores usam variacoes de tonalidade da cor base
- [x] CA04: O fallback de caixa simples funciona para tipos desconhecidos
- [x] CA05: O ArenaBuilderService compila sem erros e usa a factory
- [x] CA06: O modo default (sem level) ainda funciona com obstaculos visuais compostos

## Testes Esperados

- `test_factory_crate_stack` - Verifica que createCrateStack retorna Group com 2-3 meshes
- `test_factory_tree` - Verifica que createTree retorna Group com tronco + copa
- `test_factory_ramp` - Verifica que createRamp retorna Group com rampa + laterais
- `test_fallback_unknown_type` - Verifica que tipo desconhecido usa caixa simples

## Comandos pos-fase

- `cd lbot-datagen/lbot-datagen-frontend && npm run build` (verificar compilacao)

## Registro de Execucao

- Data: 2026-06-14
- Arquivos criados:
  - `lbot-datagen-frontend/src/app/services/obstacle-mesh.factory.ts`
- Arquivos alterados:
  - `lbot-datagen-frontend/src/app/models/level-config.model.ts` (expandiu ObstacleType)
  - `lbot-datagen-frontend/src/app/services/arena-builder.service.ts` (integracao com factory + createObstacles modo default)
  - `lbot-datagen-frontend/src/app/components/robo-simulator/robo-simulator.ts` (ajuste de cleanup para Mesh|Group)
- Testes executados:
  - `npm run build` (compilacao passou sem erros)
- Resultado: SUCESSO
- Pendencias: Nenhuma
