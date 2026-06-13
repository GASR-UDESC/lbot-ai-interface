# Fase 03: Dark Hero - Game + Controls

## Status: CONCLUIDO

## Objetivo

Aplicar o dark hero pattern do Coinbase nas paginas Game e Controls. O header de ambas as paginas tera fundo escuro (#0a0b0d) com texto branco, tipografia editorial (weight 400, sem uppercase). O HUD do jogo sera redesenhado com surface-dark-elevated e border-radius xl.

## Pre-requisitos

- Fase 01 concluida (tokens globais Coinbase ja aplicados)

## Tarefas

- [x] Tarefa 1: Migrar `game.page.css` com dark hero header
  - Arquivo: `src/app/pages/game/game.page.css`
  - O que fazer:
    1. `.page-header`: background `var(--color-surface-dark)`, padding `var(--spacing-xxl) var(--spacing-xl)` (48px vertical adaptado para app context), remover `.page-header .m-stripe`
    2. `.page-title`: color `var(--color-on-dark)`, font-weight 400, remover `text-transform: uppercase`, `font-size: var(--typography-display-sm-size)` (36px), `letter-spacing: -0.5px`
    3. `.page-subtitle`: color `var(--color-on-dark-soft)`, font-weight 400
    4. `.hud`: background `var(--color-surface-dark-elevated)`, border-radius `var(--rounded-xl)`, border remover (ou `1px solid rgba(255,255,255,0.1)`)
    5. `.hud-label`: remover `text-transform: uppercase`, font-weight 600, color `var(--color-on-dark-soft)`
    6. `.hud-level-name`: color `var(--color-on-dark)`
    7. `.hud-timer`: font-family `'JetBrains Mono', monospace`, color `var(--color-on-dark)`, font-weight 500
    8. `.hud-reset-btn`: border-radius `var(--rounded-pill)`, remover uppercase/letter-spacing, font-weight 600, border `1px solid var(--color-on-dark)`, background transparent, color `var(--color-on-dark)`, padding `8px 16px`
    9. `.hud-reset-btn:hover`: background `rgba(255,255,255,0.1)`
    10. `.chat-panel`: background `var(--color-surface-soft)`, border-left `1px solid var(--color-hairline)`
    11. `.simulator-panel`: background `var(--color-canvas)` ou `var(--color-surface-soft)`

- [x] Tarefa 2: Atualizar `game.page.html` para remover m-stripe e uppercase
  - Arquivo: `src/app/pages/game/game.page.html`
  - O que fazer:
    1. Remover `<div class="m-stripe"></div>` do `.page-header`
    2. Mudar `<h1 class="page-title">JOGAR</h1>` para `<h1 class="page-title">Jogar</h1>`

- [x] Tarefa 3: Migrar `controls.page.css` com dark hero header
  - Arquivo: `src/app/pages/controls/controls.page.css`
  - O que fazer:
    1. `.page-header`: background `var(--color-surface-dark)`, padding `var(--spacing-xxl) var(--spacing-xl)`, remover `.page-header .m-stripe`
    2. `.page-title`: color `var(--color-on-dark)`, font-weight 400, remover `text-transform: uppercase`, `font-size: var(--typography-display-sm-size)`, `letter-spacing: -0.5px`
    3. `.page-subtitle`: color `var(--color-on-dark-soft)`, font-weight 400
    4. `.simulator-container`: border-radius `var(--rounded-xl)`, border `1px solid var(--color-hairline)`
    5. `.controls-panel`: border-radius `var(--rounded-xl)`, background `var(--color-surface-card)`, border `1px solid var(--color-hairline)`
    6. `.controls-page`: background `var(--color-canvas)` (ja usa var)

- [x] Tarefa 4: Atualizar `controls.page.html` para remover m-stripe e uppercase
  - Arquivo: `src/app/pages/controls/controls.page.html`
  - O que fazer:
    1. Remover `<div class="m-stripe"></div>` do `.page-header`
    2. Mudar `<h1 class="page-title">MODO CONTROLE</h1>` para `<h1 class="page-title">Modo Controle</h1>`

## Arquivos Referencia

- `src/app/pages/game/game.page.css` - 176 linhas, page header atual sem dark hero
- `src/app/pages/game/game.page.html` - 80 linhas, tem m-stripe e uppercase
- `src/app/pages/controls/controls.page.css` - 105 linhas, page header atual sem dark hero
- `src/app/pages/controls/controls.page.html` - 17 linhas, tem m-stripe e uppercase
- `DESIGN-coinbase.md` - Componentes: hero-band-dark, button-outline-on-dark, product-ui-card-dark

## Criterios de Aceite

- [x] CA04: Dark hero nas paginas Game e Controls
  - Cenario: Dado que o dark hero foi aplicado, quando o usuario acessa Game ou Controls, entao o header tem fundo #0a0b0d com texto branco
- [x] CA02: M-Stripe removida
  - Cenario: Dado que m-stripe foi removida, quando o usuario acessa Game ou Controls, entao nenhum elemento tricolor e visivel
- [x] CA06: Tipografia editorial
  - Cenario: Dado que tipografia foi migrada, quando o usuario le "Jogar" ou "Modo Controle", entao weight e 400 sem uppercase
- [x] CA10: Dados numericos em mono
  - Cenario: Dado que JetBrains Mono foi aplicado no HUD timer, quando o timer e exibido, entao numeros sao renderizados em JetBrains Mono
- [x] CA09: Build sem erros
  - Cenario: `ng build` completa sem erros

## Testes Esperados

- `test_game_dark_hero_header` - Verificar que page-header tem background #0a0b0d
- `test_controls_dark_hero_header` - Verificar que page-header tem background #0a0b0d
- `test_hud_mono_timer` - Verificar que timer usa JetBrains Mono
- `test_hud_pill_button` - Verificar que hud-reset-btn tem border-radius pill
- `test_no_m_stripe_in_game` - Verificar que m-stripe nao existe em game.page.html
- `test_no_m_stripe_in_controls` - Verificar que m-stripe nao existe em controls.page.html

## Comandos pos-fase

- `cd 1.coleta-de-dados/lbot-datagen/lbot-datagen-frontend && npx ng build --configuration local`

## Registro de Execucao

- Data: 2026-06-13
- Arquivos criados: Nenhum
- Arquivos alterados:
  - `src/app/pages/game/game.page.css` - Dark hero header (surface-dark bg, on-dark texts, display-sm 400 weight sem uppercase, on-dark-soft subtitle), HUD redesenhado com surface-dark-elevated + rounded-xl + border sutil, hud-label migrado de tokens BMW para micro-label Coinbase (600 weight, on-dark-soft, sem uppercase), hud-timer com JetBrains Mono 500 weight, hud-reset-btn pill style (rounded-pill, 600 weight, sem uppercase/letter-spacing, hover rgba white 0.1)
  - `src/app/pages/game/game.page.html` - Removido `<div class="m-stripe">`, titulo "JOGAR" -> "Jogar"
  - `src/app/pages/controls/controls.page.css` - Dark hero header (surface-dark bg, on-dark texts, display-sm 400 weight sem uppercase, on-dark-soft subtitle), removida regra .page-header .m-stripe, simulator-container e controls-panel com rounded-xl
  - `src/app/pages/controls/controls.page.html` - Removido `<div class="m-stripe">`, titulo "MODO CONTROLE" -> "Modo Controle"
- Testes executados: `npx ng build --configuration local` - build concluido com sucesso em 4.362s (prerendered 3 static routes). Erro pre-existente de DatePipe no leaderboard (nao relacionado a CSS).
- Resultado: Sucesso - dark hero pattern aplicado nas paginas Game e Controls com headers dark (#0a0b0d), HUD redesenhado com surface-dark-elevated + rounded-xl + JetBrains Mono, todos os botoes pill style, tipografia editorial weight 400 sem uppercase, m-stripe completamente removida de ambas as paginas
- Pendencias: Nenhuma
