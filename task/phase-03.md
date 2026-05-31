# Fase 03: Colisao em Arco + Integracao Completa

## Status: PENDENTE

## Objetivo

Implementar deteccao de colisao durante movimentos em arco. Criar metodo `getMaxValidArcPosition()` que faz sampling discreto ao longo da trajetoria curva, encontrando o ponto maximo valido antes de uma colisao. Integrar ao fluxo do `executeArcCommand()`.

## Pre-requisitos

- Fase 02 concluida (animateArc() funcional, colisao linear funcional)

## Tarefas

- [ ] Tarefa 1: Criar getMaxValidArcPosition() no physics.service
  - Arquivo: `lbot-datagen/lbot-datagen-frontend/src/app/services/physics.service.ts`
  - O que fazer:
    - Criar metodo:
      ```typescript
      getMaxValidArcPosition(
        centerX: number,
        centerZ: number,
        radius: number,
        startAngle: number,
        endAngle: number,
        obstacles: ObstacleData[]
      ): { angle: number; x: number; z: number; blocked: boolean }
      ```
    - Implementacao:
      1. Calcular comprimento total do arco: `arcLength = radius * |endAngle - startAngle|`
      2. Determinar numero de steps: `steps = Math.floor(arcLength / stepSize)` (stepSize = 5)
      3. Para cada step i de 0 a steps:
         - Calcular theta = startAngle + (endAngle - startAngle) * (i / steps)
         - Calcular x = centerX + radius * cos(theta)
         - Calcular z = centerZ + radius * sin(theta)
         - Chamar `isValidPosition(x, z, obstacles)`
         - Se invalido, retornar posicao do step anterior como maximo valido (blocked = true)
      4. Se todos validos, retornar posicao final (blocked = false)

- [ ] Tarefa 2: Integrar colisao no executeArcCommand()
  - Arquivo: `lbot-datagen/lbot-datagen-frontend/src/app/components/robo-simulator/robo-simulator.ts`
  - O que fazer:
    - Em `executeArcCommand()`, ANTES de chamar `animateArc()`:
      1. Calcular centro do arco (cx, cz) e angulos inicial/final
      2. Chamar `this.physics.getMaxValidArcPosition(cx, cz, radius, startAngle, endAngle, this.obstacles)`
      3. Se `blocked === true`:
         - Calcular angulo parcial percorrido ate o ponto de colisao
         - Chamar `animateArc()` apenas com o angulo parcial
      4. Se `blocked === false`:
         - Chamar `animateArc()` com o angulo completo
    - Apos animacao (parcial ou completa), atualizar `robotState.rotation` corretamente

- [ ] Tarefa 3: Extrair calculo de centro/angulos do arco em metodo auxiliar
  - Arquivo: `lbot-datagen/lbot-datagen-frontend/src/app/components/robo-simulator/robo-simulator.ts`
  - O que fazer:
    - Criar metodo privado `calculateArcGeometry(radius, direction, angle)`:
      ```typescript
      private calculateArcGeometry(radius: number, direction: 'L' | 'R', angle: number): {
        centerX: number; centerZ: number;
        startAngle: number; endAngle: number;
      }
      ```
    - Reutilizar esta logica tanto no pre-calculo de colisao quanto no animateArc()
    - Garantir consistencia entre colisao e animacao

- [ ] Tarefa 4: Atualizar robotState.rotation corretamente apos arco parcial
  - Arquivo: `lbot-datagen/lbot-datagen-frontend/src/app/components/robo-simulator/robo-simulator.ts`
  - O que fazer:
    - Quando arco eh interrompido por colisao, a rotacao final do robo deve corresponder ao angulo percorrido (tangente ao arco no ponto de parada)
    - Calcular: `newRotation = robotState.rotation + percurredAngle * sign` (onde sign depende de L/R)
    - Garantir que `robotState.x`, `robotState.z` e `robotState.rotation` estao sincronizados apos colisao

## Arquivos Referencia

- `lbot-datagen/lbot-datagen-frontend/src/app/services/physics.service.ts` - getMaxValidPosition() como modelo para implementar getMaxValidArcPosition()
- `lbot-datagen/lbot-datagen-frontend/src/app/components/robo-simulator/robo-simulator.ts` - executeDistanceCommand() como modelo da integracao de colisao linear

## Criterios de Aceite

- [ ] CA06: Arco `A30R90;` que colide com obstaculo para no ponto exato de colisao e proximo comando executa
- [ ] CA07 (com arco): Sequencia `A30R90;D50F;` com colisao no arco - robo para, depois anda reto
- [ ] Arco sem colisao funciona identico a Fase 02 (nao regride)
- [ ] Rotacao do robo apos arco parcial (colisao) esta correta (tangente ao ponto de parada)

## Testes Esperados

- Validacao manual: posicionar robo perto de obstaculo e executar arco que passa pelo obstaculo

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
