# Fase 03: Game State & Timer

## Status: PENDENTE

## Objetivo

Criar o GameStateService usando Angular Signals para gerenciar todo o estado do jogo: nivel atual, timers por nivel, progresso do run, condicoes de vitoria e transicoes. Ao final, o servico esta pronto para ser consumido pelas UI components.

## Pre-requisitos

- Fase 02 concluida (level configs definidos)

## Tarefas

- [ ] Tarefa 1: Criar interfaces do game state
  - Arquivo: `lbot-datagen/lbot-datagen-frontend/src/app/models/game-state.model.ts`
  - O que fazer: Definir interfaces:
    - `GamePhase = 'idle' | 'playing' | 'level-complete' | 'run-complete'`
    - `LevelProgress = { levelId: number, timeMs: number, completed: boolean }`
    - `RunState = { currentLevel: number, phase: GamePhase, levelTimes: number[], totalTimeMs: number, isRunActive: boolean }`

- [ ] Tarefa 2: Criar GameStateService com Signals
  - Arquivo: `lbot-datagen/lbot-datagen-frontend/src/app/services/game-state.service.ts`
  - O que fazer: Service com Angular Signals:
    - `phase = signal<GamePhase>('idle')` - fase atual do jogo
    - `currentLevel = signal<number>(1)` - nivel atual (1-5)
    - `levelTimes = signal<number[]>([])` - tempos de cada nivel completado (ms)
    - `currentLevelStartTime = signal<number>(0)` - timestamp de inicio do nivel atual
    - `isRunActive = signal<boolean>(false)` - se um run esta ativo
    - `currentLevelElapsed = computed(() => ...)` - tempo decorrido do nivel atual
    - `totalElapsed = computed(() => ...)` - soma dos tempos
    - Metodos: `startRun()`, `startLevel()`, `completeLevel()`, `nextLevel()`, `resetRun()`, `getFormattedTime(ms): string`

- [ ] Tarefa 3: Implementar logica de timer
  - Arquivo: `lbot-datagen/lbot-datagen-frontend/src/app/services/game-state.service.ts` (mesmo arquivo)
  - O que fazer:
    - Timer baseado em `Date.now()` (nao setInterval, para evitar drift)
    - `startLevel()`: registra `currentLevelStartTime` = Date.now()
    - `completeLevel()`: calcula tempo = Date.now() - startTime, adiciona ao levelTimes
    - `getElapsedMs()`: retorna Date.now() - currentLevelStartTime (chamado pelo componente no template)
    - `formatTime(ms: number): string`: converte ms para formato "MM:SS"
    - Timer NAO pausa em nenhum momento (nem retry, nem entre comandos)

- [ ] Tarefa 4: Implementar progressao de niveis
  - Arquivo: `lbot-datagen/lbot-datagen-frontend/src/app/services/game-state.service.ts` (mesmo arquivo)
  - O que fazer:
    - `startRun()`: reseta tudo, set currentLevel=1, phase='playing', isRunActive=true, chama startLevel()
    - `completeLevel()`: para timer, calcula tempo, adiciona a levelTimes, set phase='level-complete'
    - `nextLevel()`: se currentLevel < 5: incrementa, phase='playing', startLevel(). Se == 5: phase='run-complete'
    - `resetRun()`: zera tudo, phase='idle', isRunActive=false
    - `isLastLevel = computed(() => currentLevel() === 5)`

- [ ] Tarefa 5: Integrar win condition com GameState
  - Arquivo: `lbot-datagen/lbot-datagen-frontend/src/app/components/robo-simulator/robo-simulator.ts`
  - O que fazer:
    - Injetar GameStateService
    - Adicionar `@Output() levelCompleted = new EventEmitter<void>()`
    - Quando checkWinCondition detecta vitoria: emitir evento `levelCompleted`
    - NAO chamar game state diretamente do simulator (quem orquestra e o GamePage)
    - Manter o `resetRobot()` funcional (para o botao "Reiniciar Posicao")

## Arquivos Referencia

- `lbot-datagen/lbot-datagen-frontend/src/app/services/simulator-bridge.service.ts` - Pattern de service com Subject/observable
- `lbot-datagen/lbot-datagen-frontend/src/app/models/robot-state.model.ts` - Pattern de interfaces de state
- `lbot-datagen/lbot-datagen-frontend/src/app/components/robo-simulator/robo-simulator.ts` - Win condition atual

## Criterios de Aceite

- [ ] CA01: Timer inicia quando nivel comeca
  - Cenario: Given startRun() chamado / When nivel 1 inicia / Then currentLevelStartTime registrado e getElapsedMs() retorna valor crescente
- [ ] CA02: Timer para quando nivel completado
  - Cenario: Given timer rodando / When completeLevel() chamado / Then tempo e registrado em levelTimes e timer para
- [ ] CA03: Timer nao pausa no retry
  - Cenario: Given timer em 30s / When resetRobot() chamado / Then timer continua rodando (nao reseta)
- [ ] CA04: Progressao 1->5 funciona
  - Cenario: Given nivel 1 completo / When nextLevel() chamado / Then currentLevel=2 e novo timer inicia
- [ ] CA05: Run completo apos nivel 5
  - Cenario: Given nivel 5 completo / When completeLevel() chamado / Then phase='run-complete' e levelTimes tem 5 tempos
- [ ] CA06: Formato MM:SS correto
  - Cenario: Given tempo 92000ms / When formatTime() chamado / Then retorna "01:32"

## Testes Esperados

- Nenhum teste automatizado (decisao do projeto)

## Comandos pos-fase

- `cd lbot-datagen/lbot-datagen-frontend && ng serve`
- Verificar: injetar GameStateService em um componente temporario e testar fluxo via console

## Registro de Execucao

- Data:
- Arquivos criados:
- Arquivos alterados:
- Testes executados:
- Resultado:
- Pendencias:
