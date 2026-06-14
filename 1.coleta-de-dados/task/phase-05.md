# Fase 05: Fisica de Rampas e Validador de Niveis

## Status: PENDENTE

## Objetivo

Ajustar a fisica do robo para permitir subida em rampas e criar um servico de validacao com pathfinding A* para garantir que todos os niveis sao completaveis.

## Pre-requisitos

- Fase 04 concluida (Niveis 4-5 definidos)

## Tarefas

- [ ] Tarefa 1: Ajustar estabilizacao do robo para rampas
  - Arquivo: `lbot-datagen-frontend/src/app/services/physics.service.ts`
  - O que fazer: Modificar `stabilizeRobot()` para nao forcar o robo para baixo quando ele esta sobre uma superficie inclinada (rampa).
  - Estrategia: Detectar se o robo esta em contato com um corpo inclinado (rampa). Pode ser feito verificando:
    - Se `robotBody.position.y > 1` (esta acima do chao) E
    - Se `robotBody.velocity.y < 0` (esta descendo)
    - Ou usar um raycast simples para detectar o angulo do terreno abaixo do robo.
  - Alternativa mais simples: em vez de `if (robotBody.position.y > 7) { robotBody.velocity.y -= 2; }`, usar uma tolerancia maior (ex: `> 10`) e nao aplicar quando `robotBody.velocity.y > 0` (subindo).
  - Ou ainda mais simples: remover completamente a forca para baixo em rampas e deixar a gravidade natural atuar.
  - Testar no Nivel 3 (Cidade em Obras) que tem rampas.

- [ ] Tarefa 2: Criar LevelValidatorService com pathfinding A*
  - Arquivo: `lbot-datagen-frontend/src/app/services/level-validator.service.ts`
  - O que fazer: Criar servico com:
    - `validateLevel(config: LevelConfig): ValidationResult`
    - Grid-based A* na arena 400x400 com celulas de 10x10 (ou 20x20)
    - Marcar celulas bloqueadas com base nos obstaculos (usando Box do Cannon.js)
    - Verificar se existe caminho de A a B
    - Estimar numero de comandos LBML necessarios: contar quantas mudancas de direcao (rotacoes) e distancias (movimentos) seriam necessarias no caminho mais curto do A*
    - Retornar: `{ completable: boolean, estimatedCommands: number, path: Point[] }`
  - O pathfinder nao precisa ser perfeito, apenas garantir que existe caminho.

- [ ] Tarefa 3: Validar todos os niveis
  - Usar o LevelValidatorService para validar os 5 niveis.
  - Verificar que:
    - Nivel 1: completable, 3-5 comandos estimados
    - Nivel 2: completable, 5-8 comandos
    - Nivel 3: completable, 8-12 comandos
    - Nivel 4: completable, 12-16 comandos
    - Nivel 5: completable, 16-20 comandos
  - Se algum nivel falhar, ajustar o layout (posicao de obstaculos, A ou B) e revalidar.

- [ ] Tarefa 4: Testar subida de rampa manualmente
  - Rodar o jogo no Nivel 3
  - Enviar comandos LBML para fazer o robo subir a rampa
  - Verificar que o robo sobe sem travar ou cair
  - Se houver problemas, ajustar o angulo da rampa ou a fisica

## Arquivos Referencia

- `lbot-datagen-frontend/src/app/services/physics.service.ts` - Metodo `stabilizeRobot()` atual.
- `lbot-datagen-frontend/src/app/models/level-config.model.ts` - Modelo dos niveis para validar.
- `lbot-datagen-frontend/src/app/services/arena-builder.service.ts` - Como obstaculos sao criados e posicionados.
- `lbot-datagen-frontend/src/app/services/lbml-parser.service.ts` - Para entender os comandos LBML no estimador.

## Criterios de Aceite

- [ ] CA01: O robo consegue subir rampas fisicamente no Nivel 3
- [ ] CA02: O pathfinder A* confirma que todos os 5 niveis tem caminho valido
- [ ] CA03: O numero de comandos estimados esta dentro da faixa esperada para cada nivel
- [ ] CA04: A fisica nao quebra (robo nao cai do mapa, nao atravessa obstaculos)
- [ ] CA05: Compilacao passa sem erros

## Testes Esperados

- `test_physics_ramp_climb` - Verificar que robo sobe rampa sem travar
- `test_pathfinder_level1` - Verificar caminho valido no nivel 1
- `test_pathfinder_level5` - Verificar caminho valido no nivel 5 (mais complexo)
- `test_estimated_commands` - Verificar que estimativa esta na faixa

## Comandos pos-fase

- `cd lbot-datagen/lbot-datagen-frontend && npm run build` (verificar compilacao)
- `cd lbot-datagen/lbot-datagen-frontend && npm start` (subir app para testar rampas)

## Registro de Execucao

- Data:
- Arquivos criados:
- Arquivos alterados:
- Testes executados:
- Resultado:
- Pendencias:
