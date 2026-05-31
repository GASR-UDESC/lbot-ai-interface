# Fase 02: Colisao Linear + animateArc()

## Status: PENDENTE

## Objetivo

Implementar duas funcionalidades centrais: (1) integrar deteccao de colisao no movimento linear existente (comandos D) usando pre-calculo, e (2) criar o metodo `animateArc()` para executar o movimento curvo do comando A com parametrizacao angular.

## Pre-requisitos

- Fase 01 concluida (parser reconhece comando A e tipos estao definidos)

## Tarefas

- [ ] Tarefa 1: Integrar colisao no executeDistanceCommand()
  - Arquivo: `lbot-datagen/lbot-datagen-frontend/src/app/components/robo-simulator/robo-simulator.ts`
  - O que fazer:
    - Em `executeDistanceCommand()`, ANTES de chamar `animateMovement()`:
      1. Calcular `targetX` e `targetZ` como ja faz
      2. Chamar `this.physics.getMaxValidPosition(startX, startZ, targetX, targetZ, this.obstacles)`
      3. Se `blocked === true`, usar as coordenadas retornadas como destino ao inves do target original
      4. Chamar `animateMovement()` com as coordenadas validadas
    - O robo para no ponto maximo valido (sem colisao) e o proximo comando continua normalmente

- [ ] Tarefa 2: Atualizar getMaxValidPosition para considerar paredes da arena
  - Arquivo: `lbot-datagen/lbot-datagen-frontend/src/app/services/physics.service.ts`
  - O que fazer:
    - Verificar que `isValidPosition()` ja checa arena boundaries (ARENA_LIMIT = 190) - OK, ja faz
    - Verificar que os obstaculos vindos de `createObstaclesFromConfig()` estao na lista passada - garantir que o robo-simulator passa `this.obstacles` corretamente
    - Ajustar se necessario o `stepSize` para maior precisao (atual = 5, manter)

- [ ] Tarefa 3: Implementar animateArc()
  - Arquivo: `lbot-datagen/lbot-datagen-frontend/src/app/components/robo-simulator/robo-simulator.ts`
  - O que fazer:
    - Criar metodo `private animateArc(radius: number, direction: 'L' | 'R', angle: number): Promise<void>`
    - Geometria do arco:
      - Centro do arco: perpendicular a frente do robo, deslocado `radius` unidades para o lado indicado
      - `cx = robotX + radius * cos(robotRotation + 90° ou -90°)` (depende L/R)
      - `cz = robotZ + radius * sin(robotRotation + 90° ou -90°)` (depende L/R)
    - Parametrizacao angular:
      - Angulo inicial: angulo do robo ao centro (oposto da direcao do centro)
      - Angulo final: angulo inicial +/- arcAngle (depende L/R)
      - A cada frame, interpolar theta com easing
      - Posicao: `x = cx + radius * cos(theta)`, `z = cz + radius * sin(theta)`
      - Rotacao do robo: tangente ao arco = `theta + 90°` ou `theta - 90°` (perpendicular ao raio)
    - Duracao: `arcLength / ROBOT_SPEED * 1000` onde `arcLength = radius * angle_rad`
    - Atualizar `robotBody.position` e `robotBody.quaternion` a cada frame (mesmo padrao do animateMovement)
    - Ao final, atualizar `robotState.rotation` com a nova orientacao

- [ ] Tarefa 4: Implementar executeArcCommand()
  - Arquivo: `lbot-datagen/lbot-datagen-frontend/src/app/components/robo-simulator/robo-simulator.ts`
  - O que fazer:
    - Criar metodo `private async executeArcCommand(cmd: ParsedArcCommand): Promise<void>`
    - Extrair radius, direction e angle do comando
    - Chamar `animateArc(radius, direction, angle)`
    - Atualizar `executeCommand()` para chamar `executeArcCommand()` quando `cmd.type === 'A'`
    - Remover o stub/log da Fase 01

- [ ] Tarefa 5: Tratar caso especial raio zero
  - Arquivo: `lbot-datagen/lbot-datagen-frontend/src/app/components/robo-simulator/robo-simulator.ts`
  - O que fazer:
    - Se `radius === 0`, tratar como rotacao in-place: chamar `animateRotation()` com o angulo equivalente
    - Se `angle === 0`, nao executar nenhum movimento (resolve imediatamente)

## Arquivos Referencia

- `lbot-datagen/lbot-datagen-frontend/src/app/components/robo-simulator/robo-simulator.ts` - animateMovement() e animateRotation() como exemplos de animacao
- `lbot-datagen/lbot-datagen-frontend/src/app/services/physics.service.ts` - getMaxValidPosition() como referencia de colisao

## Criterios de Aceite

- [ ] CA01: Comando `A30R90;` executa arco de 90 graus para direita com raio 30
- [ ] CA02: Comando `A50L180;` executa arco de 180 graus para esquerda com raio 50
- [ ] CA03: Sequencia `D50F;A30R90;D50F;` executa corretamente em sequencia
- [ ] CA05: Comando `D200F;` com parede a 50 unidades para o robo na parede (colisao linear)
- [ ] CA07: Sequencia `D200F;R90R;D50F;` com colisao no primeiro comando continua normalmente

## Testes Esperados

- Validacao manual no simulador: executar comandos via chat e observar movimento

## Comandos pos-fase

```bash
cd lbot-datagen/lbot-datagen-frontend && ng build
```

## Registro de Execucao

- Data:
- Arquivos criados:
- Arquivos alterados:
- Testes executados:
- Resultado:
- Pendencias:
