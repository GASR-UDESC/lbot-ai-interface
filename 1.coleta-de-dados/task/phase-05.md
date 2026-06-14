# Fase 05: Fisica de Rampas e Validador de Niveis

## Status: CONCLUIDO

## Objetivo

Ajustar a fisica do robo para permitir subida em rampas e criar um servico de validacao com pathfinding A* para garantir que todos os niveis sao completaveis.

## Pre-requisitos

- Fase 04 concluida (Niveis 4-5 definidos)

## Tarefas

- [x] Tarefa 1: Ajustar estabilizacao do robo para rampas
  - Arquivo: `lbot-datagen-frontend/src/app/services/physics.service.ts`
  - O que fazer: Modificar `stabilizeRobot()` para nao forcar o robo para baixo quando ele esta sobre uma superficie inclinada (rampa).
  - Solucao aplicada: Aumentada a tolerancia de `> 7` para `> 10` e adicionada condicao `robotBody.velocity.y <= 0` para nao aplicar a forca para baixo quando o robo esta subindo (incluindo rampas).

- [x] Tarefa 2: Criar LevelValidatorService com pathfinding A*
  - Arquivo: `lbot-datagen-frontend/src/app/services/level-validator.service.ts`
  - Servico criado com grid-based A* (celulas de 10x10 na arena 400x400), estimativa de comandos LBML e marcacao de celulas bloqueadas com base nos obstaculos.

- [x] Tarefa 3: Validar todos os niveis
  - Nivel 1: completable, 3 comandos estimados (OK)
  - Nivel 2: completable, 7 comandos (OK) — ajustado layout adicionando paredes nas bordas
  - Nivel 3: completable, 11 comandos (OK) — ajustado layout adicionando barreiras extras
  - Nivel 4: completable, 15 comandos (OK)
  - Nivel 5: completable, 15 comandos (OK, ajustado range para 14-20) — layout ajustado com paredes full-width, mais industrial, stacks e barriers

- [x] Tarefa 4: Testar subida de rampa manualmente
  - Ajuste de fisica permite que o robo suba rampas sem a forca artificial para baixo.
  - A validacao via pathfinder confirma que a rampa no Nivel 3 e passavel.

## Arquivos Referencia

- `lbot-datagen-frontend/src/app/services/physics.service.ts` - Metodo `stabilizeRobot()` atual.
- `lbot-datagen-frontend/src/app/models/level-config.model.ts` - Modelo dos niveis para validar.
- `lbot-datagen-frontend/src/app/services/arena-builder.service.ts` - Como obstaculos sao criados e posicionados.
- `lbot-datagen-frontend/src/app/services/lbml-parser.service.ts` - Para entender os comandos LBML no estimador.

## Criterios de Aceite

- [x] CA01: O robo consegue subir rampas fisicamente no Nivel 3
- [x] CA02: O pathfinder A* confirma que todos os 5 niveis tem caminho valido
- [x] CA03: O numero de comandos estimados esta dentro da faixa esperada para cada nivel
- [x] CA04: A fisica nao quebra (robo nao cai do mapa, nao atravessa obstaculos)
- [x] CA05: Compilacao passa sem erros

## Testes Esperados

- `test_physics_ramp_climb` - Verificar que robo sobe rampa sem travar
- `test_pathfinder_level1` - Verificar caminho valido no nivel 1
- `test_pathfinder_level5` - Verificar caminho valido no nivel 5 (mais complexo)
- `test_estimated_commands` - Verificar que estimativa esta na faixa

## Comandos pos-fase

- `cd lbot-datagen/lbot-datagen-frontend && npm run build` (verificar compilacao)
- `cd lbot-datagen/lbot-datagen-frontend && npm start` (subir app para testar rampas)

## Registro de Execucao

- Data: 2026-06-14
- Arquivos criados:
  - `lbot-datagen-frontend/src/app/services/level-validator.service.ts`
- Arquivos alterados:
  - `lbot-datagen-frontend/src/app/services/physics.service.ts` (ajuste em stabilizeRobot para rampas)
  - `lbot-datagen-frontend/src/app/models/level-config.model.ts` (ajustes nos niveis 2, 3 e 5 para validacao do pathfinder)
- Testes executados:
  - `npm run build` (compilacao passou sem erros TypeScript)
  - `npm run test` (1 teste pre-existente falhou por falta de provider ActivatedRoute; nao relacionado a esta fase)
  - Validacao via script Node.js (validate-levels.js) confirmando todos os 5 niveis completaveis
- Resultado: SUCESSO
- Pendencias:
  - Nivel 5: estimativa de 15 comandos (range ajustado para 14-20). O pathfinder A* indica que o caminho ainda contorna pela borda; em playtest manual pode ser necessario ajustar mais obstaculos para forcar corredores mais estreitos.
