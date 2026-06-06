# Fase 04: Componentes - Chat, Controles Virtuais, Overlays

## Status: CONCLUIDO

## Objetivo

Atualizar todos os componentes filhos para o tema BMW M: lbot-chat, virtual-controls, victory-screen, level-transition e confirm-modal. Aplicar tema escuro, border-radius 0, tipografia uppercase e cores BMW M.

## Pre-requisitos

- Fase 01 concluida (variaveis CSS globais)
- Fase 03 concluida (layouts de game e controls para contexto visual)

## Tarefas

- [ ] Tarefa 1: Atualizar LBot Chat para BMW M (RF11)
  - Arquivos: `src/app/components/lbot-chat/lbot-chat.html`, `src/app/components/lbot-chat/lbot-chat.css`
  - O que fazer no HTML:
    - Chat header titulo: "LBOT TRANSLATOR" em uppercase, weight 700, tracking 1.5px
    - Botao "Enviar": label "ENVIAR" em uppercase
    - Botao "Finalizar Chat": manter icone X circular
    - Labels de observacao: uppercase, tracking 1.5px
    - Botoes "Cancelar" e "Finalizar Chat"/"Confirmar" no popup: uppercase, tracking 1.5px
  - O que fazer no CSS:
    - `.chat-wrapper`: `background: var(--color-surface-soft)` (#0d0d0d)
    - `.chat-header`: `background: var(--color-surface-card)` (#1a1a1a), `color: var(--color-ink)`, `border-bottom: 1px solid var(--color-hairline)`, `border-radius: 0`
    - `.message.user`: `background: var(--color-surface-elevated)` (#262626), `color: var(--color-ink)`, `border-radius: 0`
    - `.message.bot`: `background: var(--color-surface-soft)` (#0d0d0d), `color: var(--color-body)` (#bbbbbb), `border-radius: 0`
    - `.message.error`: `background: rgba(226, 39, 24, 0.1)`, `color: var(--color-primary-error-text)`, `border: 1px solid var(--color-primary-error-text)`, `border-radius: 0`
    - `.message.system`: `color: var(--color-muted)`, manter centralizado
    - `.typing`: `background: var(--color-surface-soft)`, `color: var(--color-muted)`
    - `.chat-input`: `background: var(--color-surface-card)`, `border-top: 1px solid var(--color-hairline)`
    - `.chat-input input`: `background: var(--color-surface-card)`, `color: var(--color-ink)`, `border: 1px solid var(--color-hairline)`, `border-radius: 0`, `height: 48px`
    - `.chat-input input:focus`: `border-color: var(--color-on-dark)`, `border-width: 2px`
    - `.chat-input input::placeholder`: `color: var(--color-muted)`
    - `.chat-input button`: `background: transparent`, `border: 1px solid var(--color-on-dark)`, `color: var(--color-on-dark)`, `border-radius: 0`, `font-weight: 700`, `text-transform: uppercase`, `letter-spacing: 1.5px`
    - `.chat-input button:hover:not(:disabled)`: `background: var(--color-surface-elevated)`
    - `.end-chat-btn`: manter `border-radius: var(--rounded-full)` (botao circular de icone), `background: var(--color-surface-elevated)`, `color: var(--color-ink)`
    - `.star-btn.selected`: `color: #ffffff` (estrelas brancas)
    - `.star-btn`: `color: var(--color-muted)`
    - `.rating-overlay`: `background: rgba(0, 0, 0, 0.85)`
    - `.rating-popup`: `background: var(--color-surface-card)`, `border-radius: 0`, `border: 1px solid var(--color-hairline)`
    - `.rating-popup h3`: `color: var(--color-ink)`, `text-transform: uppercase`
    - `.cancel-btn`: `background: transparent`, `border: 1px solid var(--color-on-dark)`, `color: var(--color-on-dark)`, `border-radius: 0`
    - `.submit-btn`: `background: var(--color-on-dark)`, `color: var(--color-canvas)`, `border: 1px solid var(--color-on-dark)`, `border-radius: 0` (ou outline BMW)
    - `.observation-area textarea`: `background: var(--color-surface-card)`, `color: var(--color-ink)`, `border: 1px solid var(--color-hairline)`, `border-radius: 0`
    - Remover todos os `border-radius: var(--rounded-md)` -> `0`
    - Remover todos os `border-radius: var(--rounded-sm)` -> `0`
    - Manter `border-radius: var(--rounded-full)` APENAS para `.end-chat-btn` (botao circular de icone)

- [ ] Tarefa 2: Atualizar Virtual Controls para BMW M
  - Arquivos: `src/app/components/virtual-controls/virtual-controls.html`, `src/app/components/virtual-controls/virtual-controls.css`
  - O que fazer no HTML:
    - Titulo "Controles Virtuais" em uppercase ("CONTROLES VIRTUAIS")
    - Subtitulo em weight 300 (Light)
    - Botoes de acao: uppercase, tracking 1.5px
    - Labels de grupos: uppercase, tracking 1.5px
  - O que fazer no CSS:
    - `.virtual-controls-container`: `background: transparent` ou `var(--color-canvas)`
    - `.header h2`: `text-transform: uppercase`, `font-weight: 700`, `letter-spacing: -0.5px`
    - `.subtitle`: `font-weight: 300`, `color: var(--color-body)`
    - `.controls-section`, `.timeline-section`, `.description-section`, `.lbml-section`: `background: var(--color-surface-card)`, `border-radius: 0`, `border: 1px solid var(--color-hairline)`
    - `.button-group h4`: `text-transform: uppercase`, `letter-spacing: 1.5px`, `font-weight: 700`, `color: var(--color-body)`
    - `.control-btn`: `border-radius: 0` (NAO circular — botoes de direcao sao retangulares BMW), `background: var(--color-surface-elevated)`, `border: 1px solid var(--color-hairline)`
    - `.control-btn:hover:not(:disabled)`: `background: var(--color-hairline)`
    - `.arrow`: `color: var(--color-ink)` (branco)
    - `.label`: `color: var(--color-body)` (#bbbbbb)
    - `.timeline-item`: `border-bottom: 1px solid var(--color-hairline)`
    - `.description-input`, `.user-description-input`: `background: var(--color-surface-card)`, `color: var(--color-ink)`, `border: 1px solid var(--color-hairline)`, `border-radius: 0`
    - `.lbml-display`: `background: var(--color-surface-soft)`, `border-radius: 0`
    - `.summary-section`: `background: var(--color-surface-soft)`, `border-radius: 0`
    - `.action-btn`: `border-radius: 0`, `font-weight: 700`, `text-transform: uppercase`, `letter-spacing: 1.5px`
    - `.reset-btn`: `background: transparent`, `color: var(--color-on-dark)`, `border: 1px solid var(--color-hairline)`
    - `.execute-btn`: `background: var(--color-on-dark)`, `color: var(--color-canvas)`, `border: 1px solid var(--color-on-dark)`
    - `.remove-btn`: `border-radius: var(--rounded-full)` (icone circular — excecao), `background: var(--color-surface-elevated)`, `color: var(--color-muted)`

- [ ] Tarefa 3: Atualizar Victory Screen para BMW M (RF10)
  - Arquivos: `src/app/components/victory-screen/victory-screen.html`, `src/app/components/victory-screen/victory-screen.css`
  - O que fazer no HTML:
    - Titulo "PARABENS!" ja esta uppercase — confirmar
    - Labels: "TEMPO TOTAL", "NIVEL", "NOME", "TEMPO" em uppercase
    - Botao "Jogar Novamente" -> "JOGAR NOVAMENTE" uppercase
    - Botao "Salvar no Leaderboard" -> "SALVAR NO LEADERBOARD" uppercase
  - O que fazer no CSS:
    - `.victory-overlay`: `background: rgba(0, 0, 0, 0.85)` (antes 0.5)
    - `.victory-card`: `background: var(--color-surface-card)`, `border-radius: 0`, `border: 1px solid var(--color-hairline)`
    - `.victory-title`: `text-transform: uppercase`, `font-weight: 700`, `letter-spacing: -0.5px`, `color: var(--color-ink)`
    - `.victory-subtitle`: `font-weight: 300`, `color: var(--color-body)`
    - `.total-time-label`: `text-transform: uppercase`, `letter-spacing: 1.5px`, `font-weight: 700`
    - `.total-time-value`: `color: var(--color-ink)`
    - `.times-table`: `border-radius: 0`, `border: 1px solid var(--color-hairline)`
    - `.times-header`: `background: var(--color-surface-elevated)`, `color: var(--color-body)`, `text-transform: uppercase`
    - `.level-num`, `.level-name-cell`: `color: var(--color-ink)`
    - `.level-time`: `color: var(--color-body)`
    - `.nickname-input`: `background: var(--color-surface-card)`, `color: var(--color-ink)`, `border: 1px solid var(--color-hairline)`, `border-radius: 0`, `height: 48px`
    - `.nickname-input::placeholder`: `color: var(--color-muted)`
    - `.nickname-input:focus`: `border: 2px solid var(--color-on-dark)`
    - `.nickname-label`: `text-transform: uppercase`, `letter-spacing: 1.5px`, `color: var(--color-body)`
    - `.play-again-btn`: `border-radius: 0`, `background: transparent`, `border: 1px solid var(--color-on-dark)`, `color: var(--color-on-dark)`, `font-weight: 700`, `text-transform: uppercase`, `letter-spacing: 1.5px`
    - `.save-btn`: `border-radius: 0`, `background: var(--color-on-dark)`, `color: var(--color-canvas)`, `border: 1px solid var(--color-on-dark)`, `font-weight: 700`, `text-transform: uppercase`, `letter-spacing: 1.5px`
    - `.save-btn:hover:not(:disabled)`: `background: var(--color-surface-elevated)`, `color: var(--color-ink)`
    - `.save-btn:disabled`: `background: var(--color-hairline)`, `color: var(--color-muted)`
    - `.save-error`: `background: rgba(226, 39, 24, 0.1)`, `border-radius: 0`
    - `.save-error-msg`: `color: var(--color-primary-error-text)`

- [ ] Tarefa 4: Atualizar Level Transition para BMW M (RF10)
  - Arquivos: `src/app/components/level-transition/level-transition.html`, `src/app/components/level-transition/level-transition.css`
  - O que fazer no HTML:
    - Badge "NIVEL" ja esta uppercase — confirmar
    - Titulo completo em uppercase
    - "PROXIMO NIVEL" em uppercase com tracking 1.5px
    - "Tempo" label em uppercase
  - O que fazer no CSS:
    - `.transition-overlay`: `background: rgba(0, 0, 0, 0.85)`
    - `.transition-card`: `background: var(--color-surface-card)`, `border-radius: 0`, `border: 1px solid var(--color-hairline)`
    - `.level-badge`: `background: var(--color-surface-elevated)`, `border-radius: var(--rounded-full)` (pilula — excecao permitida), `color: var(--color-ink)`, `text-transform: uppercase`, `letter-spacing: 1.5px`, `font-weight: 700`
    - `.level-complete-title`: `color: var(--color-ink)`, `text-transform: uppercase`
    - `.time-label`: `text-transform: uppercase`, `letter-spacing: 1.5px`, `color: var(--color-body)`
    - `.time-value`: `color: var(--color-ink)`
    - `.next-level-info`: `background: var(--color-surface-elevated)`, `border-radius: 0`
    - `.next-label`: `text-transform: uppercase`, `letter-spacing: 1.5px`, `color: var(--color-body)`
    - `.next-name`: `color: var(--color-ink)`, `font-weight: 400` (title-md)
    - `.next-btn`: `background: var(--color-on-dark)`, `color: var(--color-canvas)`, `border: 1px solid var(--color-on-dark)`, `border-radius: 0`, `font-weight: 700`, `text-transform: uppercase`, `letter-spacing: 1.5px`
    - `.next-btn:hover`: `background: var(--color-surface-elevated)`, `color: var(--color-ink)`

- [ ] Tarefa 5: Atualizar Confirm Modal para BMW M (RF10)
  - Arquivos: `src/app/components/confirm-modal/confirm-modal.html`, `src/app/components/confirm-modal/confirm-modal.css`
  - O que fazer no HTML:
    - Confirmar que title e message estao sendo passados via @Input (ja estao)
    - Os textos de botoes (confirmText, cancelText) ja sao @Input — estao sendo passados com uppercase do game.page
  - O que fazer no CSS:
    - `.modal-overlay`: `background: rgba(0, 0, 0, 0.85)`
    - `.modal-card`: `background: var(--color-surface-card)`, `border-radius: 0`, `border: 1px solid var(--color-hairline)`
    - `.modal-title`: `color: var(--color-ink)`, `text-transform: uppercase`
    - `.modal-message`: `color: var(--color-body)`, `font-weight: 300`
    - `.cancel-btn`: `background: transparent`, `border: 1px solid var(--color-on-dark)`, `color: var(--color-on-dark)`, `border-radius: 0`, `font-weight: 700`, `text-transform: uppercase`, `letter-spacing: 1.5px`
    - `.confirm-btn`: `background: var(--color-on-dark)`, `color: var(--color-canvas)`, `border: 1px solid var(--color-on-dark)`, `border-radius: 0`, `font-weight: 700`, `text-transform: uppercase`, `letter-spacing: 1.5px`

## Arquivos Referencia

- `src/app/components/lbot-chat/lbot-chat.ts` - Logica do chat
- `src/app/components/lbot-chat/lbot-chat.html` - Template do chat
- `src/app/components/lbot-chat/lbot-chat.css` - Estilos do chat (tema claro, 450 linhas)
- `src/app/components/virtual-controls/virtual-controls.ts` - Logica dos controles
- `src/app/components/virtual-controls/virtual-controls.html` - Template dos controles
- `src/app/components/virtual-controls/virtual-controls.css` - Estilos dos controles (tema claro)
- `src/app/components/victory-screen/victory-screen.ts` - Logica da victory screen
- `src/app/components/victory-screen/victory-screen.html` - Template da victory
- `src/app/components/victory-screen/victory-screen.css` - Estilos da victory (tema claro)
- `src/app/components/level-transition/level-transition.ts` - Logica da transicao
- `src/app/components/level-transition/level-transition.html` - Template da transicao
- `src/app/components/level-transition/level-transition.css` - Estilos da transicao
- `src/app/components/confirm-modal/confirm-modal.ts` - Logica do modal
- `src/app/components/confirm-modal/confirm-modal.html` - Template do modal
- `src/app/components/confirm-modal/confirm-modal.css` - Estilos do modal
- `task/DESIGN-bmw-m.md` - Referencia visual BMW M

## Criterios de Aceite

- [ ] CA14: Chat atualizado para tema escuro BMW M
  - Cenario: Dado que o usuario esta na pagina de jogo com chat aberto / Quando visualiza o chat panel / Entao o chat header tem fundo surface-card com texto branco uppercase, mensagens do usuario em surface-elevated, mensagens do bot em surface-soft, e input area com border hairline e border-radius 0.
- [ ] CA15: Overlays (Level Transition, Victory, Confirm) atualizados
  - Cenario: Dado que o usuario visualiza qualquer overlay durante o jogo / Quando o overlay aparece / Entao o fundo e rgba(0,0,0,0.85), texto branco, botoes retangulares com outline, labels uppercase.
- [ ] CA07: Tema escuro nos componentes filhos
  - Cenario: Fundo escuro (#000000 ou surface-card), texto branco (#ffffff ou body #bbbbbb), borders hairline (#3c3c3c), border-radius 0.
- [ ] CA09: Cantos retos BMW em componentes
  - Cenario: Botoes, cards, inputs e containers em chat, controls e overlays tem border-radius 0 (exceto icones circulares).
- [ ] CA08: Tipografia BMW M nos componentes
  - Cenario: Labels e botoes em uppercase com tracking 1.5px, body text weight 300, headings weight 700.

## Testes Esperados

- `npx ng build` - Build sem erros
- Verificar visualmente: chat com tema escuro (header surface-card, mensagens com fundos corretos)
- Verificar visualmente: botoes do chat e controles com outline BMW (border-radius 0)
- Verificar visualmente: victory screen com overlay escuro e botoes BMW style
- Verificar visualmente: level transition e confirm modal com tema escuro
- Verificar: funcionalidades de chat (envio, avaliacao, finalizar) continuam operacionais
- Verificar: controles virtuais continuam funcionais

## Comandos pos-fase

- `npx ng build`
- `npx ng serve`

## Registro de Execucao

- Data: 2026-06-06
- Arquivos criados: (nenhum)
- Arquivos alterados:
  - `src/styles.css` - Adicionado `--color-surface-elevated: #262626`
  - `src/app/components/lbot-chat/lbot-chat.html` - Labels em uppercase (ENVIAR, CANCELAR, FINALIZAR CHAT, CONFIRMAR, ALTERAR AVALIAÇÃO, OBSERVAÇÕES)
  - `src/app/components/lbot-chat/lbot-chat.css` - Tema escuro BMW M completo (surface-soft wrapper, surface-card header, surface-elevated mensagens user, surface-soft mensagens bot, border-radius 0, botao outline, estrelas brancas, overlay rgba(0,0,0,0.85))
  - `src/app/components/virtual-controls/virtual-controls.html` - Labels em uppercase (CONTROLES VIRTUAIS, LIMPAR TUDO, EXECUTAR, EXECUTANDO)
  - `src/app/components/virtual-controls/virtual-controls.css` - Tema escuro BMW M (surface-card sections, border-radius 0, botoes retangulares, surface-elevated ctrls, hover hairline)
  - `src/app/components/victory-screen/victory-screen.html` - Labels uppercase (TEMPO TOTAL, NÍVEL, NOME, TEMPO, SEU NOME NO LEADERBOARD, JOGAR NOVAMENTE, SALVAR NO LEADERBOARD)
  - `src/app/components/victory-screen/victory-screen.css` - Tema escuro BMW M (overlay 0.85, surface-card, border-radius 0, border hairline, botoes outline, input 48px)
  - `src/app/components/level-transition/level-transition.html` - Labels uppercase (TEMPO, PRÓXIMO, PRÓXIMO NÍVEL →)
  - `src/app/components/level-transition/level-transition.css` - Tema escuro BMW M (overlay 0.85, surface-card, border-radius 0, badge pill, botoes filled on-dark)
  - `src/app/components/confirm-modal/confirm-modal.css` - Rewrite completo para BMW M (overlay 0.85, surface-card, border-radius 0, text-transform uppercase, letter-spacing 1.5px, botoes outline)
- Testes executados: `npx ng build` - Sucesso (sem erros, apenas warnings de budget CSS)
- Resultado: Build OK, todos os 5 componentes atualizados para tema escuro BMW M
- Pendencias: CSS budget warnings (nao bloqueantes) em lbot-chat.css (+3.57kB), virtual-controls.css (+3.00kB), victory-screen.css (+1.08kB)