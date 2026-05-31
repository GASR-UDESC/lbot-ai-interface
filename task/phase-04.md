# Fase 04: Game UI - Telas de Transicao, Vitoria, HUD e Modal

## Status: PENDENTE

## Objetivo

Implementar toda a interface de usuario do modo gamificado: HUD do jogo (timer, nivel, reiniciar), tela de transicao entre niveis, tela de vitoria final com nickname/leaderboard, e modal de confirmacao ao sair. Ao final, o fluxo visual completo do jogo funciona (sem backend de leaderboard ainda).

## Pre-requisitos

- Fase 03 concluida (GameStateService funcional)
- Fase 02 concluida (niveis renderizaveis)

## Tarefas

- [ ] Tarefa 1: Implementar GamePage completa (orquestrador do jogo)
  - Arquivo: `lbot-datagen/lbot-datagen-frontend/src/app/pages/game/game.page.ts`
  - Arquivo: `lbot-datagen/lbot-datagen-frontend/src/app/pages/game/game.page.html`
  - Arquivo: `lbot-datagen/lbot-datagen-frontend/src/app/pages/game/game.page.css`
  - O que fazer:
    - Layout: simulator (3D) a esquerda, chat a direita (similar ao layout atual do app.html)
    - HUD overlay no simulator: timer (MM:SS, atualizado via requestAnimationFrame ou setInterval 1s), nome do nivel atual, botao "Reiniciar Posicao"
    - Injetar GameStateService e LevelConfigService
    - No ngOnInit: chamar gameState.startRun(), carregar levelConfig do nivel 1
    - Escutar evento `levelCompleted` do simulator -> chamar gameState.completeLevel()
    - Quando phase='level-complete': mostrar LevelTransitionComponent
    - Quando phase='run-complete': mostrar VictoryScreenComponent
    - Passar levelConfig atual para o RoboSimulatorComponent via @Input
    - Botao "Reiniciar Posicao": chama simulator.resetRobot() (timer NAO para)
    - Guard de navegacao: mostrar ConfirmModal antes de sair se isRunActive

- [ ] Tarefa 2: Criar componente LevelTransition
  - Arquivo: `lbot-datagen/lbot-datagen-frontend/src/app/components/level-transition/level-transition.ts`
  - Arquivo: `lbot-datagen/lbot-datagen-frontend/src/app/components/level-transition/level-transition.html`
  - Arquivo: `lbot-datagen/lbot-datagen-frontend/src/app/components/level-transition/level-transition.css`
  - O que fazer:
    - Overlay centralizado sobre o jogo (fullscreen com backdrop escuro)
    - Mostra: "Nivel X Completo!", tempo do nivel (MM:SS), nome do proximo nivel
    - Botao "Proximo Nivel" -> emite evento (output) `nextLevel`
    - Inputs: @Input() levelName, @Input() levelTime, @Input() nextLevelName
    - Design: card centralizado, animacao de entrada suave (fade-in + scale)

- [ ] Tarefa 3: Criar componente VictoryScreen
  - Arquivo: `lbot-datagen/lbot-datagen-frontend/src/app/components/victory-screen/victory-screen.ts`
  - Arquivo: `lbot-datagen/lbot-datagen-frontend/src/app/components/victory-screen/victory-screen.html`
  - Arquivo: `lbot-datagen/lbot-datagen-frontend/src/app/components/victory-screen/victory-screen.css`
  - O que fazer:
    - Overlay fullscreen com backdrop
    - Mostra: titulo "PARABENS! Todos os niveis completos!", tabela com tempo de cada nivel (1-5), tempo total
    - Campo input para nickname (obrigatorio para salvar)
    - Botao "Salvar no Leaderboard" (disabled se nickname vazio) -> emite evento `save` com {nickname, levelTimes, totalTime}
    - Botao "Jogar Novamente" -> emite evento `playAgain`
    - Inputs: @Input() levelTimes: number[], @Input() levelNames: string[]
    - Outputs: @Output() save, @Output() playAgain
    - Mostrar posicao no leaderboard (sera integrado na fase 06)

- [ ] Tarefa 4: Criar componente ConfirmModal
  - Arquivo: `lbot-datagen/lbot-datagen-frontend/src/app/components/confirm-modal/confirm-modal.ts`
  - Arquivo: `lbot-datagen/lbot-datagen-frontend/src/app/components/confirm-modal/confirm-modal.html`
  - Arquivo: `lbot-datagen/lbot-datagen-frontend/src/app/components/confirm-modal/confirm-modal.css`
  - O que fazer:
    - Modal reutilizavel com overlay/backdrop
    - Inputs: @Input() title, @Input() message, @Input() confirmText, @Input() cancelText
    - Outputs: @Output() confirm, @Output() cancel
    - Texto padrao: "Voce vai perder todo o progresso do jogo. Tem certeza?"
    - Botoes: "Sim, sair" (confirm) e "Cancelar" (cancel)

- [ ] Tarefa 5: Implementar guard/logica de confirmacao ao sair do jogo
  - Arquivo: `lbot-datagen/lbot-datagen-frontend/src/app/pages/game/game.page.ts` (adicionar logica)
  - O que fazer:
    - Quando usuario tenta navegar para fora (/menu, /controls, /leaderboard) durante run ativo
    - Mostrar ConfirmModal com mensagem de perda de progresso
    - Se confirma: resetRun() e navegar. Se cancela: ficar no jogo.
    - Implementar via canDeactivate guard ou via logica interna do componente
    - Tambem interceptar botao "Voltar" do browser (beforeunload event)

- [ ] Tarefa 6: Timer visual com atualizacao em tempo real
  - Arquivo: `lbot-datagen/lbot-datagen-frontend/src/app/pages/game/game.page.ts` (adicionar)
  - O que fazer:
    - Criar um interval (setInterval a cada 100ms ou 1000ms) que atualiza o display do timer
    - Alternativa: usar requestAnimationFrame com throttle para atualizar o signal
    - Display no HUD: "NIVEL X - MM:SS" + botao Reiniciar
    - O timer vem de gameState.getElapsedMs() formatado com formatTime()

## Arquivos Referencia

- `lbot-datagen/lbot-datagen-frontend/src/app/app.html` - Layout original (simulator + sidebar)
- `lbot-datagen/lbot-datagen-frontend/src/app/components/robo-simulator/robo-simulator.ts` - Template do simulator com HUD existente
- `lbot-datagen/lbot-datagen-frontend/src/app/components/lbot-chat/lbot-chat.css` - Estilo do chat (para manter consistencia)

## Criterios de Aceite

- [ ] CA01: Fluxo completo nivel 1->2 funciona visualmente
  - Cenario: Given jogo no nivel 1 / When robo atinge B / Then tela de transicao aparece com tempo e botao "Proximo Nivel"
- [ ] CA02: Tela de transicao mostra dados corretos
  - Cenario: Given nivel 1 completo em 01:30 / When transicao aparece / Then mostra "Nivel 1 Completo! 01:30" e "Proximo: Escritorio"
- [ ] CA03: Tela de vitoria final aparece apos nivel 5
  - Cenario: Given nivel 5 completo / When vitoria aparece / Then mostra tempos dos 5 niveis, total, campo nickname
- [ ] CA04: Botao Salvar desabilitado sem nickname
  - Cenario: Given tela de vitoria / When nickname vazio / Then botao "Salvar no Leaderboard" esta disabled
- [ ] CA05: Modal de confirmacao ao tentar sair
  - Cenario: Given jogo no nivel 3 com timer ativo / When clica para voltar ao menu / Then modal aparece
- [ ] CA06: Cancelar modal retorna ao jogo
  - Cenario: Given modal visivel / When clica "Cancelar" / Then volta ao jogo, timer continua
- [ ] CA07: Timer atualiza visualmente em tempo real
  - Cenario: Given nivel em andamento / When 1 segundo passa / Then display muda de "00:05" para "00:06"
- [ ] CA08: Botao Reiniciar Posicao funciona
  - Cenario: Given robo em posicao qualquer / When clica "Reiniciar Posicao" / Then robo volta a A, timer continua

## Testes Esperados

- Nenhum teste automatizado (decisao do projeto)

## Comandos pos-fase

- `cd lbot-datagen/lbot-datagen-frontend && ng serve`
- Verificar: jogar fluxo completo do nivel 1 ao 5 (controlar via chat)
- Verificar: tela de transicao aparece entre niveis
- Verificar: tela de vitoria aparece ao final
- Verificar: modal de confirmacao ao tentar sair durante jogo

## Registro de Execucao

- Data:
- Arquivos criados:
- Arquivos alterados:
- Testes executados:
- Resultado:
- Pendencias:
