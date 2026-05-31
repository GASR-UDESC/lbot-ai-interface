# Fase 01: Redesign Level Design + Remocao "Novo Desafio"

## Status: PENDENTE

## Objetivo

Redesenhar os 5 niveis com obstaculos que bloqueiam a largura total da arena (paredes horizontais com gaps obrigatorios), posicionar pontos A/B estrategicamente por nivel, e remover completamente o botao "Novo Desafio" e o metodo generateNewLevel().

## Pre-requisitos

- Nenhum (primeira fase)

## Tarefas

- [ ] Tarefa 1: Redesenhar Nivel 1 (Armazem) - Desvio lateral simples
  - Arquivo: `lbot-datagen/lbot-datagen-frontend/src/app/models/level-config.model.ts`
  - O que fazer: Substituir os 5 crates por 2-3 paredes horizontais que cruzam a arena inteira (~350-380 width) com um gap de ~60 unidades posicionado em lados alternados. Ponto A em (-150, -150), Ponto B em (150, 150). O robot precisa ir ate o gap de cada parede para passar.

- [ ] Tarefa 2: Redesenhar Nivel 2 (Escritorio) - Desvio lateral com mais paredes
  - Arquivo: `lbot-datagen/lbot-datagen-frontend/src/app/models/level-config.model.ts`
  - O que fazer: Substituir por 3-4 paredes horizontais full-width com gaps em posicoes alternadas (esquerda, direita, centro). Adicionar 1-2 crates perto dos gaps para dificultar a passagem. Caminho em S suave.

- [ ] Tarefa 3: Redesenhar Nivel 3 (Cidade) - Corredores com curvas
  - Arquivo: `lbot-datagen/lbot-datagen-frontend/src/app/models/level-config.model.ts`
  - O que fazer: Criar corredores formados por paredes paralelas (verticais e horizontais) que forcam o robot a seguir um caminho pre-definido. Gaps estreitos (~40 unidades) entre paredes. O robot nao pode "cortar" por fora.

- [ ] Tarefa 4: Redesenhar Nivel 4 (Floresta) - Labirinto
  - Arquivo: `lbot-datagen/lbot-datagen-frontend/src/app/models/level-config.model.ts`
  - O que fazer: Substituir os 9 crates por paredes formando um labirinto com 2-3 caminhos possiveis (um mais curto, outros mais longos). Pelo menos 4-5 curvas obrigatorias. Ajustar startPoint e goalPoint para (-170, -170) e (170, 170) para maximizar distancia.

- [ ] Tarefa 5: Redesenhar Nivel 5 (Fabrica) - Labirinto + Rampas obrigatorias
  - Arquivo: `lbot-datagen/lbot-datagen-frontend/src/app/models/level-config.model.ts`
  - O que fazer: Criar labirinto com uma secao que so e acessivel subindo uma rampa (area elevada). Posicionar uma parede bloqueando caminho no chao, com rampa como unica alternativa. O robot PRECISA subir a rampa para acessar a passagem para o goalPoint.

- [ ] Tarefa 6: Remover botao "Novo Desafio" e metodo generateNewLevel()
  - Arquivo: `lbot-datagen/lbot-datagen-frontend/src/app/components/robo-simulator/robo-simulator.ts`
  - O que fazer: Remover do template o botao `<button class="goal-button" (click)="generateNewLevel()"...>`. Remover os metodos: `generateNewLevel()`, `generateRandomPosition()`, `generatePositionInQuadrant()`, `calculateDistance()`, `isPositionOnObstacle()`. Remover as constantes `MIN_DISTANCE_AB` e `MIN_OBSTACLE_DISTANCE`. Remover o `TargetIcon` import. No `ngOnChanges`, quando `showGoals` fica true e startMarker existe, chamar `resetRobot()` ao inves de `generateNewLevel()`.

- [ ] Tarefa 7: Remover estilos do botao "Novo Desafio"
  - Arquivo: `lbot-datagen/lbot-datagen-frontend/src/app/components/robo-simulator/robo-simulator.css`
  - O que fazer: Remover a classe `.goal-button` e todos seus estados (hover, active, disabled).

## Arquivos Referencia

- `lbot-datagen/lbot-datagen-frontend/src/app/models/level-config.model.ts` - Estrutura atual dos niveis (interfaces + LEVEL_CONFIGS)
- `lbot-datagen/lbot-datagen-frontend/src/app/services/arena-builder.service.ts` - Como os obstaculos sao renderizados (createObstaclesFromConfig)
- `lbot-datagen/lbot-datagen-frontend/src/app/components/robo-simulator/robo-simulator.ts` - Onde esta o generateNewLevel e o botao

## Criterios de Aceite

- [ ] CA01: Nivel 1 - nenhum caminho reto de A ate B sem desviar de obstaculo
  - Cenario: Dado robot em (-150,-150), Quando move em diagonal direta para (150,150), Entao colide com parede e nao chega ao destino
- [ ] CA04: Botao "Novo Desafio" nao existe na interface
  - Cenario: Dado o componente robo-simulator renderizado com showGoals=true, Quando inspeciona o template, Entao nao ha botao "Novo Desafio"
- [ ] CA05: Pontos A e B sao fixos por nivel (definidos em LevelConfig)
  - Cenario: Dado dois loads do mesmo nivel, Quando compara startPoint e goalPoint, Entao sao identicos

## Testes Esperados

- Validacao visual manual: cada nivel deve ser completavel (existe caminho valido de A ate B)
- Validacao visual manual: cada nivel deve ser impossivel de completar em linha reta

## Comandos pos-fase

- `cd lbot-datagen/lbot-datagen-frontend && npx ng build` (verificar que compila sem erros)
- `cd lbot-datagen/lbot-datagen-frontend && npx ng serve` (testar visualmente cada nivel)

## Registro de Execucao

- Data:
- Arquivos criados:
- Arquivos alterados:
- Testes executados:
- Resultado:
- Pendencias:
