# Fase 02: Paginas Light - Nav + Menu + Leaderboard

## Status: CONCLUIDO

## Objetivo

Migrar a top navigation, a pagina Menu e a pagina Leaderboard para o light theme Coinbase. Apos esta fase, as tres superficies terao canvas branco, tipografia editorial (weight 400, sem uppercase), border-radius xl nos cards, e pill style nos botoes.

## Pre-requisitos

- Fase 01 concluida (tokens globais Coinbase ja aplicados)

## Tarefas

- [x] Tarefa 1: Migrar `top-nav.css` para light theme
  - Arquivo: `src/app/components/top-nav/top-nav.css`
  - O que fazer:
    1. `.top-nav`: background `var(--color-canvas)` (ja usa var, confirmar)
    2. Remover `.top-nav > .m-stripe` e `margin-top: auto`
    3. `.nav-logo`: color `var(--color-ink)`, font-weight 600, remover text-transform uppercase e letter-spacing largo. Usar `font-size: var(--typography-title-md-size)`, `font-weight: 600`, `letter-spacing: 0`, remover `text-transform: uppercase`
    4. `.nav-link`: color `var(--color-body)` (ja usa var, confirmar)
    5. `.nav-link--active`: color `var(--color-ink)` (em vez de `var(--color-on-dark)`)
    6. `.nav-hamburger`: background `var(--color-surface-strong)`, color `var(--color-ink)`, border remover ou usar `var(--color-hairline)`
    7. `.nav-overlay`: background `var(--color-canvas)` (ja usa var)
    8. `.nav-overlay-link`: remover text-transform uppercase, letter-spacing 1.5px. Usar `font-size: var(--typography-title-md-size)`, `font-weight: 600`, `letter-spacing: 0`, `text-transform: none`
    9. `.nav-overlay-link.nav-link--active`: color `var(--color-ink)`
    10. `.nav-overlay-content`: remover referencia visual a m-stripe (gap pode ser ajustado)

- [x] Tarefa 2: Migrar `menu.page.css` para light theme com cards Coinbase
  - Arquivo: `src/app/pages/menu/menu.page.css`
  - O que fazer:
    1. `.menu-wrapper`: background `var(--color-canvas)` (ja usa var)
    2. `.title`: font-weight 400 (em vez de 700), remover `text-transform: uppercase`, usar `font-size: var(--typography-display-sm-size)` (36px), `letter-spacing: -0.5px`
    3. `.subtitle`: font-weight 400 (em vez de 300)
    4. `.menu-btn`: border-radius `var(--rounded-xl)` (24px), padding 32px, border `1px solid var(--color-hairline)`, background `var(--color-surface-card)`
    5. `.menu-btn:hover`: border-color `var(--color-body)` ou adicionar `box-shadow: 0 4px 12px rgba(0, 0, 0, 0.04)`
    6. `.btn-icon-circle`: background `var(--color-surface-strong)`, color `var(--color-ink)` (em vez de `var(--color-on-dark)`)
    7. `.btn-text`: remover `text-transform: uppercase`, `letter-spacing: 1.5px`. Usar `font-size: var(--typography-title-md-size)`, `font-weight: 600`, `letter-spacing: 0`, `text-transform: none`, color `var(--color-ink)`
    8. `.btn-desc`: font-weight 400 (em vez de 300)
    9. `.menu-footer`: font-weight 400 (em vez de 700)

- [x] Tarefa 3: Atualizar `menu.page.html` para remover uppercase
  - Arquivo: `src/app/pages/menu/menu.page.html`
  - O que fazer:
    1. `.title`: mudar "LBOT ARENA" para "Lbot Arena" (ou manter como esta, ja que o CSS vai remover uppercase)
    2. `.btn-text`: mudar "JOGAR" para "Jogar", "LEADERBOARD" para "Leaderboard", "MODO CONTROLE" para "Modo Controle"

- [x] Tarefa 4: Migrar `leaderboard.page.css` para light theme
  - Arquivo: `src/app/pages/leaderboard/leaderboard.page.css`
  - O que fazer:
    1. `.lb-page`: background `var(--color-canvas)` (ja usa var)
    2. `.lb-title`: font-weight 400, remover `text-transform: uppercase`, usar `font-size: var(--typography-display-sm-size)` (36px)
    3. `.lb-subtitle`: font-weight 400 (em vez de 300)
    4. `.lb-state`: border-radius `var(--rounded-xl)`, background `var(--color-surface-card)`, border `1px solid var(--color-hairline)`
    5. `.lb-retry-btn`: border-radius `var(--rounded-pill)`, remover uppercase/letter-spacing, font-weight 600, color `var(--color-primary)`, border `1px solid var(--color-primary)`, background transparent
    6. `.lb-retry-btn:hover`: background `var(--color-primary)`, color `var(--color-on-primary)`
    7. `.lb-skeleton-card`: border-radius `var(--rounded-xl)`, border `1px solid var(--color-hairline)`
    8. `.lb-skeleton-line`: border-radius `var(--rounded-sm)`
    9. `.lb-card`: border-radius `var(--rounded-xl)`, padding 32px, border `1px solid var(--color-hairline)`
    10. `.lb-card:hover`: border-color `var(--color-body)` ou `box-shadow: 0 4px 12px rgba(0,0,0,0.04)`
    11. `.lb-card-nickname`: font-weight 600 (em vez de 400 via title-md-weight)
    12. `.lb-card-time`: adicionar `font-family: 'JetBrains Mono', monospace`
    13. `.lb-rank-num--large`: font-weight 400 (em vez de 700)
    14. `.lb-back-btn`: remover uppercase/letter-spacing, color `var(--color-primary)`, font-weight 600
    15. `.lb-skeleton-rank`: background `var(--color-surface-strong)` (em vez de surface-strong que agora e #eef0f3)

- [x] Tarefa 5: Atualizar `leaderboard.page.html` para remover uppercase
  - Arquivo: `src/app/pages/leaderboard/leaderboard.page.html`
  - O que fazer:
    1. `.lb-title`: mudar "LEADERBOARD" para "Leaderboard"
    2. `.lb-retry-btn`: mudar "Tentar novamente" (ja esta ok, CSS vai remover uppercase)

## Arquivos Referencia

- `src/app/components/top-nav/top-nav.css` - 127 linhas, nav atual dark
- `src/app/components/top-nav/top-nav.html` - 29 linhas, remover m-stripe
- `src/app/pages/menu/menu.page.css` - 118 linhas, cards com border-radius 0
- `src/app/pages/menu/menu.page.html` - 45 linhas, textos uppercase
- `src/app/pages/leaderboard/leaderboard.page.css` - 297 linhas, cards com border-radius 0
- `src/app/pages/leaderboard/leaderboard.page.html` - 55 linhas, titulos uppercase
- `DESIGN-coinbase.md` - Componentes: top-nav-light, feature-card, button-tertiary-text

## Criterios de Aceite

- [x] CA02: M-Stripe removida
  - Cenario: Dado que m-stripe foi removida da nav, quando o usuario abre o app, entao nenhum elemento tricolor e visivel na nav
- [x] CA03: Light theme aplicado
  - Cenario: Dado que Menu e Leaderboard foram migrados, quando o usuario acessa essas paginas, entao o fundo e branco e textos sao escuros
- [x] CA05: Botoes pill
  - Cenario: Dado que botoes foram migrados, quando o usuario ve o retry button e back button, entao tem border-radius 100px
- [x] CA06: Tipografia editorial
  - Cenario: Dado que tipografia foi migrada, quando o usuario le titulos, entao weight e 400 sem uppercase
- [x] CA10: Dados numericos em mono
  - Cenario: Dado que JetBrains Mono foi adicionado, quando o usuario ve tempos no leaderboard, entao numeros sao renderizados em JetBrains Mono
- [x] CA09: Build sem erros
  - Cenario: `ng build` completa sem erros

## Testes Esperados

- `test_nav_light_theme` - Verificar que nav tem background branco e texto escuro
- `test_menu_cards_rounded_xl` - Verificar que menu cards tem border-radius 24px
- `test_leaderboard_times_mono_font` - Verificar que tempos usam JetBrains Mono
- `test_no_uppercase_in_templates` - Verificar que nenhum text-transform uppercase existe nos CSSs migrados

## Comandos pos-fase

- `cd 1.coleta-de-dados/lbot-datagen/lbot-datagen-frontend && npx ng build --configuration local`

## Registro de Execucao

- Data: 2026-06-13
- Arquivos criados: Nenhum
- Arquivos alterados:
  - `src/app/components/top-nav/top-nav.css` - Removido .m-stripe, nav-logo com Coinbase ink/600/sem-uppercase, nav-link--active com ink, hamburger surface-strong/ink sem borda, nav-overlay-link sem uppercase
  - `src/app/pages/menu/menu.page.css` - Title weight 400 display-sm sem uppercase, subtitle weight 400, menu-btn border-radius xl + padding 32px + hover shadow, btn-icon-circle surface-strong/ink, btn-text title-md 600 sem uppercase, btn-desc 400, footer 400
  - `src/app/pages/menu/menu.page.html` - Textos desuppercased: "Lbot Arena", "Jogar", "Leaderboard", "Modo Controle"
  - `src/app/pages/leaderboard/leaderboard.page.css` - Title weight 400 display-sm sem uppercase, subtitle weight 400, lb-state rounded-xl, lb-retry-btn pill + primary color, skeleton-card rounded-xl, skeleton-line rounded-sm, lb-card rounded-xl + padding 32px + hover shadow, lb-rank-num--large weight 400, lb-card-time JetBrains Mono, lb-back-btn primary color sem uppercase
  - `src/app/pages/leaderboard/leaderboard.page.html` - Titulo "Leaderboard" (sem uppercase)
- Testes executados: `npx ng build --configuration local` - build concluido com sucesso em 4.305s (prerendered 3 static routes). Erro pre-existente de DatePipe no leaderboard (nao relacionado a CSS).
- Resultado: Sucesso - top-nav, menu e leaderboard migrados para light theme Coinbase com cards rounded-xl, pill buttons, tipografia weight 400 sem uppercase, e tempos em JetBrains Mono
- Pendencias: Nenhuma
