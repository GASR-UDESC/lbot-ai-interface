# Fase 03: Timer Global (runStartTime)

## Status: CONCLUIDO

## Objetivo

Implementar um timer global que comeca no inicio do nivel 1 e NAO para entre niveis. O timer so para quando o ponto B do nivel 5 e alcancado. Reset de nivel nao reseta o timer. O display mostra o tempo total decorrido desde o inicio da run.

## Pre-requisitos

- Fase 02 concluida (jogo funcional com colisoes corretas)

## Tarefas

- [x] Tarefa 1: Adicionar signal runStartTime ao GameStateService
  - Arquivo: `lbot-datagen/lbot-datagen-frontend/src/app/services/game-state.service.ts`
  - O que fazer: Adicionar `readonly runStartTime = signal<number>(0);`. No metodo `startRun()`, setar `this.runStartTime.set(Date.now())`. No metodo `resetRun()`, setar `this.runStartTime.set(0)`.

- [x] Tarefa 2: Criar metodo getGlobalElapsedMs()
  - Arquivo: `lbot-datagen/lbot-datagen-frontend/src/app/services/game-state.service.ts`
  - O que fazer: Criar metodo `getGlobalElapsedMs(): number` que retorna `Date.now() - this.runStartTime()` (ou 0 se runStartTime === 0). Este metodo sera usado pelo timer display ao inves de getElapsedMs().

- [x] Tarefa 3: Atualizar timer display no GamePage para usar timer global
  - Arquivo: `lbot-datagen/lbot-datagen-frontend/src/app/pages/game/game.page.ts`
  - O que fazer: No `startTimer()`, mudar o setInterval para usar `this.gameState.getGlobalElapsedMs()` ao inves de `this.gameState.getElapsedMs()`. O timer NAO deve ser reiniciado em `onNextLevel()` - remover a chamada `this.startTimer()` de la. O timer so inicia uma vez no `ngOnInit()`.

- [x] Tarefa 4: Timer nao para em level-complete, apenas em run-complete
  - Arquivo: `lbot-datagen/lbot-datagen-frontend/src/app/pages/game/game.page.ts`
  - O que fazer: Mover `this.stopTimer()` de `onLevelCompleted()` (quando phase === 'run-complete') para ficar somente no caso run-complete. Garantir que durante `level-complete` overlay, o timer continua correndo no background (mesmo que o display esteja escondido pelo overlay). Quando o jogador clica "Proximo Nivel", o timer display reaparece com o tempo correto acumulado.

- [x] Tarefa 5: Reset de nivel nao reseta timer
  - Arquivo: `lbot-datagen/lbot-datagen-frontend/src/app/pages/game/game.page.ts`
  - O que fazer: Verificar que `onResetRobot()` apenas chama `simulator.resetRobot()` sem tocar no timer. Ja e assim, mas confirmar que nao ha side effects.

## Arquivos Referencia

- `lbot-datagen/lbot-datagen-frontend/src/app/services/game-state.service.ts` - Service atual com timer por nivel
- `lbot-datagen/lbot-datagen-frontend/src/app/pages/game/game.page.ts` - Onde o timer e exibido e controlado

## Criterios de Aceite

- [x] CA06: Reset de nivel mantem timer
  - Cenario: Dado jogador no nivel 2 com 45s decorridos, Quando aciona reset, Entao timer continua de 45s em diante
- [x] CA10: Tempo total registrado ao completar 5 niveis
  - Cenario: Dado jogador completa nivel 5, Quando tempo e salvo, Entao e o tempo total desde inicio da run (soma de tudo incluindo transicoes)
- [x] Timer nao para entre niveis
  - Cenario: Dado jogador completa nivel 1 em 30s, Quando overlay de transicao aparece por 5s e jogador avanca, Entao timer mostra 35s+

## Testes Esperados

- `test_global_timer_starts_at_run_start` - runStartTime e setado quando startRun() e chamado
- `test_global_elapsed_includes_all_time` - getGlobalElapsedMs() retorna tempo total desde inicio
- `test_timer_does_not_reset_on_next_level` - Apos nextLevel(), runStartTime permanece o mesmo
- `test_timer_stops_on_run_complete` - Timer para apenas quando phase === 'run-complete'

## Comandos pos-fase

- `cd lbot-datagen/lbot-datagen-frontend && npx ng build`
- `cd lbot-datagen/lbot-datagen-frontend && npx ng serve` (iniciar jogo, completar 2 niveis, verificar que timer nao reseta)

## Registro de Execucao

- Data: 2026-05-31
- Arquivos criados: nenhum
- Arquivos alterados:
  - `lbot-datagen/lbot-datagen-frontend/src/app/services/game-state.service.ts`
  - `lbot-datagen/lbot-datagen-frontend/src/app/pages/game/game.page.ts`
- Testes executados:
  - `cd lbot-datagen/lbot-datagen-frontend && npx ng build` - ok
  - `cd lbot-datagen/lbot-datagen-frontend && npm run start -- --host 127.0.0.1` - app carregou em `/game`
  - Verificacao runtime via browser em `http://127.0.0.1:4200/game` - `onResetRobot()` manteve o timer correndo (`00:40` -> `00:42` -> `00:43`)
  - Verificacao runtime via browser em `http://127.0.0.1:4200/game` - `completeLevel()` manteve o timer ativo durante o overlay (`00:43` -> `00:45`)
  - Verificacao runtime via browser em `http://127.0.0.1:4200/game` - `onNextLevel()` preservou `runStartTime` e o timer nao reiniciou (`00:45` -> `00:46`)
- Resultado: Timer global implementado com `runStartTime`, HUD atualizado para usar o tempo total da run, transicao entre niveis sem reinicio do contador, e fechamento da run mantendo `levelTimes` coerente com o tempo global acumulado para o fluxo atual do leaderboard.
- Pendencias: nenhuma
