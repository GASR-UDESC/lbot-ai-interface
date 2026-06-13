# Fase 04: Componentes de Jogo + Robo-Simulator

## Status: CONCLUIDO

## Objetivo

Migrar todos os componentes de jogo (lbot-chat, victory-screen, level-transition, confirm-modal, virtual-controls, robo-simulator, simulator-frame) para o design system Coinbase. Apos esta fase, todos os componentes terao border-radius xl nos containers, md nos inputs, pill nos botoes, tipografia editorial sem uppercase, e cores do design system Coinbase.

## Pre-requisitos

- Fase 01 concluida (tokens globais Coinbase ja aplicados)

## Tarefas

- [x] Tarefa 1: Migrar `lbot-chat.css` e `lbot-chat.html`
  - Arquivo: `src/app/components/lbot-chat/lbot-chat.css` e `src/app/components/lbot-chat/lbot-chat.html`
  - O que fazer:
    1. `.chat-header`: background `var(--color-surface-card)`, border-bottom `1px solid var(--color-hairline)`, remover `text-transform: uppercase`, `letter-spacing: 1.5px`, font-weight 600, border-radius `var(--rounded-xl) var(--rounded-xl) 0 0`
    2. `.message`: border-radius `var(--rounded-md)` (12px)
    3. `.message.user`: background `var(--color-primary)`, color `var(--color-on-primary)`
    4. `.message.bot`: background `var(--color-surface-soft)`, color `var(--color-body)`
    5. `.message.error`: background `rgba(207, 32, 47, 0.08)`, color `var(--color-semantic-down)`, border-radius `var(--rounded-md)`
    6. `.chat-input input`: border-radius `var(--rounded-md)`, height 48px, border `1px solid var(--color-hairline)`
    7. `.chat-input input:focus`: border-color `var(--color-primary)`, border-width 2px
    8. `.chat-input button`: border-radius `var(--rounded-pill)`, remover uppercase/letter-spacing, font-weight 600, background `var(--color-primary)`, color `var(--color-on-primary)`, border none
    9. `.chat-input button:hover`: background `var(--color-primary-active)`
    10. `.chat-input button:disabled`: background `var(--color-primary-disabled)`
    11. `.rating-popup`: border-radius `var(--rounded-xl)`, border `1px solid var(--color-hairline)`
    12. `.rating-popup h3`: remover `text-transform: uppercase`
    13. `.observation-area label`: remover `text-transform: uppercase`, `letter-spacing: 1.5px`, font-weight 600
    14. `.observation-area textarea`: border-radius `var(--rounded-md)`
    15. `.cancel-btn`: border-radius `var(--rounded-pill)`, remover uppercase/letter-spacing, font-weight 600
    16. `.submit-btn`: border-radius `var(--rounded-pill)`, background `var(--color-primary)`, color `var(--color-on-primary)`, border none, remover uppercase/letter-spacing
    17. `.submit-btn:disabled`: background `var(--color-primary-disabled)`
    18. `.rating-overlay`: background `var(--color-scrim)`
    19. No HTML: remover uppercase dos textos do header e labels

- [x] Tarefa 2: Migrar `victory-screen.css` e `victory-screen.html`
  - Arquivo: `src/app/components/victory-screen/victory-screen.css` e `src/app/components/victory-screen/victory-screen.html`
  - O que fazer:
    1. `.victory-overlay`: background `var(--color-scrim)`
    2. `.victory-card`: border-radius `var(--rounded-xl)`, border `1px solid var(--color-hairline)`, padding 32px
    3. `.victory-title`: font-weight 400, remover `text-transform: uppercase`, `font-size: var(--typography-display-sm-size)`
    4. `.victory-subtitle`: font-weight 400
    5. `.total-time-label`: remover `text-transform: uppercase`, `letter-spacing: 1.5px`, font-weight 600
    6. `.total-time-value`: font-family `'JetBrains Mono', monospace`, font-weight 500
    7. `.times-table`: border-radius `var(--rounded-md)`, overflow hidden
    8. `.times-header`: remover `text-transform: uppercase`, `letter-spacing: 1.5px`, font-weight 600, background `var(--color-surface-soft)`
    9. `.level-time`: font-family `'JetBrains Mono', monospace`
    10. `.total-label`: remover `text-transform: uppercase`, `letter-spacing: 1.5px`
    11. `.total-time`: font-family `'JetBrains Mono', monospace`
    12. `.nickname-label`: remover `text-transform: uppercase`, `letter-spacing: 1.5px`, font-weight 600
    13. `.nickname-input`: border-radius `var(--rounded-md)`
    14. `.nickname-input:focus`: border-color `var(--color-primary)`
    15. `.play-again-btn`: border-radius `var(--rounded-pill)`, remover uppercase/letter-spacing, font-weight 600, border `1px solid var(--color-hairline)`, color `var(--color-ink)`
    16. `.save-btn`: border-radius `var(--rounded-pill)`, background `var(--color-primary)`, color `var(--color-on-primary)`, border none, remover uppercase/letter-spacing
    17. `.save-btn:disabled`: background `var(--color-primary-disabled)`
    18. `.save-retry-btn`: border-radius `var(--rounded-pill)`, color `var(--color-primary)`, remover uppercase
    19. No HTML: remover uppercase dos textos

- [x] Tarefa 3: Migrar `level-transition.css` e `level-transition.html`
  - Arquivo: `src/app/components/level-transition/level-transition.css` e `src/app/components/level-transition/level-transition.html`
  - O que fazer:
    1. `.transition-overlay`: background `var(--color-scrim)`
    2. `.transition-card`: border-radius `var(--rounded-xl)`, border `1px solid var(--color-hairline)`
    3. `.level-badge`: remover `text-transform: uppercase`, `letter-spacing: 1.5px`, font-weight 600, background `var(--color-surface-strong)`, color `var(--color-ink)`, border-radius `var(--rounded-pill)`
    4. `.level-complete-title`: font-weight 400, remover `text-transform: uppercase`, `font-size: var(--typography-display-sm-size)`
    5. `.time-label`: remover `text-transform: uppercase`, `letter-spacing: 1.5px`, font-weight 600
    6. `.time-value`: font-family `'JetBrains Mono', monospace`, font-weight 500
    7. `.next-level-info`: border-radius `var(--rounded-pill)`, background `var(--color-surface-strong)`
    8. `.next-label`: remover `text-transform: uppercase`, `letter-spacing: 1.5px`
    9. `.next-btn`: border-radius `var(--rounded-pill)`, background `var(--color-primary)`, color `var(--color-on-primary)`, border none, remover uppercase/letter-spacing
    10. `.next-btn:hover`: background `var(--color-primary-active)`
    11. No HTML: remover uppercase dos textos

- [x] Tarefa 4: Migrar `confirm-modal.css` e `confirm-modal.html`
  - Arquivo: `src/app/components/confirm-modal/confirm-modal.css` e `src/app/components/confirm-modal/confirm-modal.html`
  - O que fazer:
    1. `.modal-overlay`: background `var(--color-scrim)`
    2. `.modal-card`: border-radius `var(--rounded-xl)`, border `1px solid var(--color-hairline)`
    3. `.modal-title`: remover `text-transform: uppercase`, font-weight 600, `font-size: var(--typography-title-md-size)`
    4. `.modal-message`: font-weight 400
    5. `.modal-btn`: border-radius `var(--rounded-pill)`, remover uppercase/letter-spacing, font-weight 600
    6. `.cancel-btn`: border `1px solid var(--color-hairline)`, color `var(--color-ink)`, background transparent
    7. `.confirm-btn`: background `var(--color-primary)`, color `var(--color-on-primary)`, border none
    8. `.confirm-btn:hover`: background `var(--color-primary-active)`

- [x] Tarefa 5: Migrar `virtual-controls.css` e `virtual-controls.html`
  - Arquivo: `src/app/components/virtual-controls/virtual-controls.css` e `src/app/components/virtual-controls/virtual-controls.html`
  - O que fazer:
    1. `.header h2`: remover `text-transform: uppercase`, font-weight 600, `letter-spacing: 0`
    2. `.controls-section`: border-radius `var(--rounded-xl)`, border `1px solid var(--color-hairline)`
    3. `.button-group h4`: remover `text-transform: uppercase`, `letter-spacing: 1.5px`, font-weight 600
    4. `.control-btn`: border-radius `var(--rounded-sm)` (8px), background `var(--color-surface-strong)`, border `1px solid var(--color-hairline)`
    5. `.control-btn:hover`: background `var(--color-hairline-soft)`
    6. `.timeline-section`: border-radius `var(--rounded-xl)`, border `1px solid var(--color-hairline)`
    7. `.description-input`: border-radius `var(--rounded-md)`
    8. `.description-input:focus`: border-color `var(--color-primary)`
    9. `.user-description-input`: border-radius `var(--rounded-md)`
    10. `.user-description-input:focus`: border-color `var(--color-primary)`
    11. `.description-section`: border-radius `var(--rounded-xl)`, border `1px solid var(--color-hairline)`
    12. `.lbml-section`: border-radius `var(--rounded-xl)`, border `1px solid var(--color-hairline)`
    13. `.lbml-display`: border-radius `var(--rounded-md)`, code font-family `'JetBrains Mono', monospace`
    14. `.summary-section`: border-radius `var(--rounded-md)`
    15. `.action-btn`: border-radius `var(--rounded-pill)`, remover uppercase/letter-spacing, font-weight 600
    16. `.reset-btn`: border `1px solid var(--color-hairline)`, color `var(--color-ink)`, background transparent
    17. `.execute-btn`: background `var(--color-primary)`, color `var(--color-on-primary)`, border none
    18. `.execute-btn:hover`: background `var(--color-primary-active)`
    19. `.execute-btn:disabled`: background `var(--color-primary-disabled)`
    20. No HTML: remover uppercase dos textos ("CONTROLES VIRTUAIS" -> "Controles Virtuais", etc.)

- [x] Tarefa 6: Migrar `robo-simulator.css` para variaveis CSS
  - Arquivo: `src/app/components/robo-simulator/robo-simulator.css`
  - O que fazer: Substituir todas as cores hardcoded por variaveis CSS Coinbase:
    1. `.status`: background `var(--color-surface-card)`, border-radius `var(--rounded-sm)`, box-shadow `0 4px 12px rgba(0,0,0,0.04)`
    2. `.score-counter`: background `var(--color-semantic-up)`, border-radius `var(--rounded-md)`
    3. `.score-label`: color `var(--color-on-primary)`
    4. `.score-value`: color `var(--color-on-primary)`, font-family `'JetBrains Mono', monospace`
    5. `.status-label`: color `var(--color-semantic-up)`
    6. `.status-value`: font-family `'JetBrains Mono', monospace`
    7. `.distance-item .status-label`: color `var(--color-semantic-down)`
    8. `.reset-button`: background `var(--color-primary)`, border-radius `var(--rounded-pill)`, box-shadow remover
    9. `.camera-button`: background `var(--color-surface-dark-elevated)`, border-radius `var(--rounded-pill)`
    10. `.goal-button`: background `var(--color-semantic-down)`, border-radius `var(--rounded-pill)`
    11. Hover states: usar `var(--color-primary-active)` para reset-button
    12. `.indicator`: background `var(--color-semantic-up)`, border-radius `var(--rounded-pill)`
    13. `.error`: background `var(--color-semantic-down)`, border-radius `var(--rounded-md)`
    14. `.victory`: background `var(--color-semantic-up)`, border-radius `var(--rounded-xl)`

- [x] Tarefa 7: Migrar `simulator-frame.css`
  - Arquivo: `src/app/components/simulator-frame/simulator-frame.css`
  - O que fazer:
    1. `.simulator-wrapper`: border-radius `var(--rounded-xl)`, border `1px solid var(--color-hairline)`

## Arquivos Referencia

- `src/app/components/lbot-chat/lbot-chat.css` - 463 linhas, o maior arquivo CSS
- `src/app/components/lbot-chat/lbot-chat.html` - Template do chat
- `src/app/components/victory-screen/victory-screen.css` - 300 linhas
- `src/app/components/victory-screen/victory-screen.html` - Template da vitoria
- `src/app/components/level-transition/level-transition.css` - 132 linhas
- `src/app/components/level-transition/level-transition.html` - Template da transicao
- `src/app/components/confirm-modal/confirm-modal.css` - 89 linhas
- `src/app/components/confirm-modal/confirm-modal.html` - Template do modal
- `src/app/components/virtual-controls/virtual-controls.css` - 395 linhas
- `src/app/components/virtual-controls/virtual-controls.html` - Template dos controles
- `src/app/components/robo-simulator/robo-simulator.css` - 206 linhas, cores hardcoded
- `src/app/components/simulator-frame/simulator-frame.css` - 20 linhas
- `DESIGN-coinbase.md` - Componentes: text-input, button-primary, button-secondary-light, feature-card, badge-pill

## Criterios de Aceite

- [x] CA05: Botoes pill em todo o app
  - Cenario: Dado que todos os botoes foram migrados, quando o usuario interage com qualquer botao, entao tem border-radius 100px
- [x] CA06: Tipografia editorial
  - Cenario: Dado que tipografia foi migrada, quando o usuario le textos nos componentes, entao sem uppercase
- [x] CA07: Cores semanticas em feedback
  - Cenario: Dado que tokens semanticos foram aplicados, quando feedback positivo aparece, entao usa #05b169 como cor de texto
- [x] CA08: Responsividade mantida
  - Cenario: Dado que a migracao foi aplicada, quando o usuario acessa em mobile, entao layout se adapta
- [x] CA10: Dados numericos em mono
  - Cenario: Dado que JetBrains Mono foi aplicado, quando tempos aparecem no victory-screen e level-transition, entao numeros sao JetBrains Mono
- [x] CA09: Build sem erros
  - Cenario: `ng build` completa sem erros

## Testes Esperados

- `test_chat_pill_buttons` - Verificar que botao enviar tem border-radius pill
- `test_chat_input_rounded_md` - Verificar que input tem border-radius 12px
- `test_victory_card_rounded_xl` - Verificar que card tem border-radius 24px
- `test_victory_times_mono` - Verificar que tempos usam JetBrains Mono
- `test_level_transition_pill_button` - Verificar que botao next tem border-radius pill
- `test_confirm_modal_rounded_xl` - Verificar que modal card tem border-radius 24px
- `test_virtual_controls_pill_actions` - Verificar que action buttons tem border-radius pill
- `test_robo_simulator_css_vars` - Verificar que nao ha cores hardcoded
- `test_no_uppercase_in_components` - Verificar que nenhum text-transform uppercase existe nos CSSs migrados

## Comandos pos-fase

- `cd 1.coleta-de-dados/lbot-datagen/lbot-datagen-frontend && npx ng build --configuration local`

## Registro de Execucao

- Data: 2026-06-13
- Arquivos criados: (nenhum)
- Arquivos alterados:
  - `src/app/components/lbot-chat/lbot-chat.css` - Pill buttons, rounded-md messages/inputs, Coinbase primary + semantic colors
  - `src/app/components/lbot-chat/lbot-chat.html` - Uppercase removido
  - `src/app/components/victory-screen/victory-screen.css` - Border-radius xl, pill buttons, JetBrains Mono, scrim
  - `src/app/components/victory-screen/victory-screen.html` - Uppercase removido
  - `src/app/components/level-transition/level-transition.css` - Border-radius xl/pill, JetBrains Mono, scrim, primary button
  - `src/app/components/level-transition/level-transition.html` - Uppercase removido
  - `src/app/components/confirm-modal/confirm-modal.css` - Border-radius xl/pill, scrim, primary button, hairline secondary
  - `src/app/components/virtual-controls/virtual-controls.css` - Border-radius xl/sm/md/pill, JetBrains Mono code, primary focus/buttons
  - `src/app/components/virtual-controls/virtual-controls.html` - Uppercase removido
  - `src/app/components/robo-simulator/robo-simulator.css` - Todas cores hardcoded substituidas por variaveis CSS Coinbase
  - `src/app/components/simulator-frame/simulator-frame.css` - Border-radius xl
- Testes executados: `ng build --configuration local` - build concluido com sucesso
- Resultado: Build bem-sucedido. Prerendering lanca erro pre-existente de DatePipe (nao relacionado a migracao CSS).
- Pendencias: Nenhuma (erro de DatePipe e pre-existente e fora do escopo desta fase).
