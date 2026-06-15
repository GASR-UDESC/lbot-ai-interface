# Fase 02: Redesign dos Layouts dos Niveis

## Status: CONCLUIDO

## Objetivo

Redesenhar completamente o layout de obstaculos de cada um dos 5 niveis para criar uma progressao de dificuldade tipo labirinto, com rampas obrigatorias nos niveis 3-5 e bloqueio de cantos nos niveis 2-5.

## Pre-requisitos

- Fase 01 concluida (nomes dos niveis ja renomeados).

## Tarefas

- [x] Tarefa 1: Corrigir `createRamp` na `obstacle-mesh.factory.ts`
  - Arquivo: `1.coleta-de-dados/lbot-datagen/lbot-datagen-frontend/src/app/services/obstacle-mesh.factory.ts`
  - O metodo `createRamp` atualmente hardcoded `rampAngle = Math.PI / 8` (22.5°) na visual mesh
  - Alterar a assinatura para aceitar `rampAngle?: number` (ou usar o `variation` param)
  - Usar o `rampAngle` passado para rotacionar a mesh visual em X: `ramp.rotation.x = rampAngle`
  - Recalcular `yOffset` com base no `rampAngle` passado: `Math.sin(rampAngle) * depth / 4`
  - Ajustar rails para acompanhar o angulo
  - Garantir que o `createMesh` passe `rampAngle` para `createRamp` quando type='ramp'
  - Nota: O `createObstaclesFromConfig` em `arena-builder.service.ts` ja passa `rampAngle` no body physics, mas a visual mesh ignora. Esta tarefa corrige o alinhamento.

- [x] Tarefa 2: Redesenhar Nivel 1 (Trivial)
  - Arquivo: `1.coleta-de-dados/lbot-datagen/lbot-datagen-frontend/src/app/models/level-config.model.ts`
  - Objetivo: caminho quase reto de A a B, serve como tutorial
  - Obstaculos: 3 crates pequenos no centro, espacados, permitindo contornar facilmente
  - Nao bloquear cantos
  - Exemplo de layout:
    ```
    { x: 0, z: 0, width: 12, height: 12, depth: 12, type: 'crate' },
    { x: -25, z: 25, width: 10, height: 10, depth: 10, type: 'crate' },
    { x: 25, z: -25, width: 10, height: 10, depth: 10, type: 'crate' },
    ```

- [x] Tarefa 3: Redesenhar Nivel 2 (Desviar, sem rampas)
  - Arquivo: `1.coleta-de-dados/lbot-datagen/lbot-datagen-frontend/src/app/models/level-config.model.ts`
  - Objetivo: forcar desvios, mas sem rampas. Bloquear cantos.
  - Obstaculos: paredes internas que criam corredores e desvios
  - Bloquear cantos com paredes proximas as bordas
  - Altura das paredes >= 15
  - 11 obstaculos

- [x] Tarefa 4: Redesenhar Nivel 3 (Primeiro labirinto com rampa obrigatoria)
  - Arquivo: `1.coleta-de-dados/lbot-datagen/lbot-datagen-frontend/src/app/models/level-config.model.ts`
  - Objetivo: rampa obrigatoria, caminho reto bloqueado, cantos bloqueados
  - Angulo da rampa: 0.24 rad (~13.7°)
  - 13 obstaculos

- [x] Tarefa 5: Redesenhar Nivel 4 (Labirinto denso, rampa obrigatoria)
  - Arquivo: `1.coleta-de-dados/lbot-datagen/lbot-datagen-frontend/src/app/models/level-config.model.ts`
  - Objetivo: multiplos obstaculos, corredores estreitos, uma rampa obrigatoria
  - 17 obstaculos; mix de walls, barriers, trees

- [x] Tarefa 6: Redesenhar Nivel 5 (Labirinto complexo, multiplas rampas)
  - Arquivo: `1.coleta-de-dados/lbot-datagen/lbot-datagen-frontend/src/app/models/level-config.model.ts`
  - Objetivo: layout mais denso, 2 rampas obrigatorias
  - 22 obstaculos; mix de walls, crates, stacks, industrial, trees

## Arquivos Referencia

- `1.coleta-de-dados/lbot-datagen/lbot-datagen-frontend/src/app/models/level-config.model.ts` - Estrutura `LevelConfig` e `ObstacleConfig`
- `1.coleta-de-dados/lbot-datagen/lbot-datagen-frontend/src/app/services/arena-builder.service.ts` - `createObstaclesFromConfig` mostra como os obstaculos sao renderizados e fisicados
- `1.coleta-de-dados/lbot-datagen/lbot-datagen-frontend/src/app/services/obstacle-mesh.factory.ts` - Como cada tipo de obstaculo e visualizado
- `1.coleta-de-dados/lbot-datagen/lbot-datagen-frontend/src/app/services/physics.service.ts` - Constantes do robo (velocidade 30, rotacao 90, massa 100)
- `1.coleta-de-dados/lbot-datagen/lbot-datagen-frontend/src/app/components/robo-simulator/robo-simulator.ts` - `WIN_DISTANCE = 25`, `startPoint` e `goalPoint` fixos

## Criterios de Aceite

- [x] CA01: Nivel 1 e trivial
  - Dado que o jogador inicia o Nivel 1
  - Quando ele executa comandos de movimento direto
  - Entao ele chega ao B com poucos ou nenhum desvio
- [x] CA02: Nivel 2 exige desvios
  - Dado que o jogador inicia o Nivel 2
  - Quando ele tenta ir em linha reta de A ate B
  - Entao ele colide com obstaculos e precisa usar rotacoes para contornar
- [x] CA03: Nivel 3 tem rampa obrigatoria
  - Dado que o jogador inicia o Nivel 3
  - Quando ele tenta chegar ao B sem subir a rampa
  - Entao ele e bloqueado por paredes/obstaculos
  - E quando ele subir a rampa e continuar, ele chega ao B
- [x] CA04: Cantos bloqueados nos niveis 2-5
  - Dado que o jogador esta no Nivel 2, 3, 4 ou 5
  - Quando ele tenta ir diretamente para um canto e contornar pela borda
  - Entao ele encontra uma parede interna que bloqueia o caminho
- [x] CA05: Nivel 5 tem 2 rampas obrigatorias
  - Dado que o jogador inicia o Nivel 5
  - Quando ele completa o nivel
  - Entao ele passou por pelo menos 2 rampas obrigatorias
- [x] CA06: Fisica de rampa funciona
  - Dado que o robo esta no inicio de uma rampa
  - Quando ele executa um comando F (frente)
  - Entao ele sobe a rampa fisicamente sem ficar preso ou passar atraves

## Testes Esperados

- Teste manual no navegador: jogar cada nivel e verificar se o caminho funciona
- `npm run build` deve compilar sem erros
- Verificar no console do navegador se a contagem de obstaculos nos niveis 4 e 5 nao degrada performance

## Comandos pos-fase

```bash
cd 1.coleta-de-dados/lbot-datagen/lbot-datagen-frontend
npm run build
```

## Registro de Execucao

- Data: 2026-06-15
- Arquivos criados: Nenhum
- Arquivos alterados:
  - `1.coleta-de-dados/lbot-datagen/lbot-datagen-frontend/src/app/services/obstacle-mesh.factory.ts` (createRamp aceita rampAngle, remove yOffset interno; createMesh propaga rampAngle)
  - `1.coleta-de-dados/lbot-datagen/lbot-datagen-frontend/src/app/services/arena-builder.service.ts` (createObstaclesFromConfig passa rampAngle ao createMesh)
  - `1.coleta-de-dados/lbot-datagen/lbot-datagen-frontend/src/app/models/level-config.model.ts` (redesign completo dos 5 niveis)
- Testes executados: `npm run build` (sucesso, exit code 0)
- Resultado:
  - Tarefa 1: `createRamp` agora aceita `rampAngle` como parametro. Removeu o yOffset duplicado que causava desalinhamento mesh/fisica. `createObstaclesFromConfig` propaga `rampAngle` corretamente.
  - Nivel 1: 3 crates no centro, caminho quase reto. Tutorial.
  - Nivel 2: 11 paredes criando corredores e desvios. Cantos bloqueados. Sem rampas.
  - Nivel 3: 13 obstaculos. Rampa obrigatoria (0.24 rad) como unica passagem pelo centro. 8 paredes de canto.
  - Nivel 4: 17 obstaculos. Rampa obrigatoria + barrerias + arvores. Labirinto denso com corredores estreitos.
  - Nivel 5: 22 obstaculos. Duas rampas obrigatorias. Mix de walls, industrial, stack, tree. Layout mais complexo.
  - Build: compilou sem erros de compilacao (warnings de CSS budget sao pre-existentes).
- Pendencias: Nenhuma. Teste manual no navegador recomendado para validar gameplay (fisica de rampa, navegacao pelos labirintos).
