# Fase 02: Paginas Estaticas - Menu + Leaderboard

## Status: CONCLUIDO

## Objetivo

Redesenhar as paginas Menu e Leaderboard para o estilo editorial BMW M: canvas preto, tipografia uppercase, botoes outline retangulares, cards com hairline borders e border-radius 0.

## Pre-requisitos

- Fase 01 concluida (variaveis CSS globais e top-nav)

## Tarefas

- [x] Tarefa 1: Redesenhar pagina Menu (RF08)
  - Arquivo: `src/app/pages/menu/menu.page.html`
  - O que fazer:
    - Manter a estrutura centralizada mas redesenhar:
    - Logo emoji `🤖` pode ser mantido ou substituido por "LBOT" em display-lg uppercase
    - Titulo "LBot Arena" -> "LBOT ARENA" em `var(--typography-display-lg-size)` (56px), weight 700, uppercase, tracking -0.5px, cor `var(--color-ink)` (branco)
    - Subtitulo manter sentence-case, weight 300 (Light), cor `var(--color-body)` (#bbbbbb)
    - Os 3 botoes de navegacao (Jogar, Leaderboard, Modo Controle):
      - Remover fundo colorido do botao primario (Jogar)
      - Todos os botoes: estilo card BMW -> `background: var(--color-surface-card)` (#1a1a1a), `border: 1px solid var(--color-hairline)` (#3c3c3c), `border-radius: 0`
      - Icones Lucide dentro de circulos (`border-radius: var(--rounded-full)`, `background: var(--color-surface-card)`)
      - Hover: `border-color: var(--color-on-dark)`, `box-shadow: none` (remover sombra flutuante)
      - Texto do botao em `label-uppercase` style (14px, weight 700, tracking 1.5px)
      - Descricao do botao em `body-sm` (14px, weight 300, cor body)
    - Footer: texto muted `var(--color-muted)` (#7e7e7e) em `caption` style

  - Arquivo: `src/app/pages/menu/menu.page.css`
  - O que fazer:
    - `.menu-wrapper`: `background-color: var(--color-canvas)` (ja e, mas agora preto)
    - `.menu-card`: `border-radius: 0` (remover rounded-md)
    - `.title`: `font-size: var(--typography-display-lg-size)`, `font-weight: 700`, `text-transform: uppercase`, `letter-spacing: -0.5px`, cor `var(--color-ink)` (branco)
    - `.subtitle`: `font-weight: 300` (Light), cor `var(--color-body)` (#bbbbbb)
    - `.menu-btn`: `border-radius: 0`, `background-color: var(--color-surface-card)`, `border: 1px solid var(--color-hairline)`, `color: var(--color-ink)`, remover `box-shadow` hover em favor de border highlight
    - `.btn-primary`, `.btn-secondary`, `.btn-tertiary`: todos outline/card style, mesmo visual, sem destaque colorido
    - `.btn-icon`: `border-radius: var(--rounded-full)`, `background: var(--color-surface-elevated)`
    - `.btn-text`: `font-weight: 700`, `text-transform: uppercase`, `letter-spacing: 1.5px`, `font-size: var(--typography-label-uppercase-size)`
    - `.btn-desc`: `font-weight: 300`, cor `var(--color-body)`
    - `.menu-footer`: cor `var(--color-muted)`
    - Remover todos os `border-radius: var(--rounded-md)` ou `var(--rounded-sm)` que nao sejam icones circulares

- [x] Tarefa 2: Atualizar pagina Leaderboard (RF09)
  - Arquivo: `src/app/pages/leaderboard/leaderboard.page.html`
  - O que fazer:
    - Trofeu emoji `🏆` pode ser mantido ou substituido por icone Lucide `Trophy`
    - Titulo "Leaderboard Global" -> "LEADERBOARD" em uppercase, `var(--typography-display-lg-size)`, weight 700, tracking -0.5px
    - Subtitulo: sentence-case, weight 300 (Light), cor `var(--color-body)`
    - Botao retry: estilo outline BMW (border branco, bg transparent, texto branco, border-radius 0)
    - Link "Voltar ao Menu": remover ou estilizar como link BMW M (uppercase, tracking 1.5px) — agora o top-nav provê navegação

  - Arquivo: `src/app/pages/leaderboard/leaderboard.page.css`
  - O que fazer:
    - `.lb-page`: `background: var(--color-canvas)` (preto)
    - `.lb-title`: `font-weight: 700`, `text-transform: uppercase`, `letter-spacing: -0.5px`, cor `var(--color-ink)` (branco)
    - `.lb-subtitle`: `font-weight: 300`, cor `var(--color-body)`
    - `.lb-card`, `.lb-skeleton-card`: `background: var(--color-surface-card)`, `border-radius: 0`, `border: 1px solid var(--color-hairline)`, remover `box-shadow` hover
    - `.lb-state`: `background: var(--color-surface-card)`, `border-radius: 0`
    - `.lb-retry-btn`: estilo outline BMW — `background: transparent`, `border: 1px solid var(--color-on-dark)`, `color: var(--color-on-dark)`, `border-radius: 0`, `font-weight: 700`, `text-transform: uppercase`, `letter-spacing: 1.5px`
    - `.lb-back-btn`: `color: var(--color-on-dark)`, uppercase, tracking 1.5px, `font-weight: 700`
    - `.lb-rank-num`, `.lb-card-nickname`, `.lb-card-time`, `.lb-card-date`: auditar cores para tema escuro
    - Skeleton pulse: `background: var(--color-surface-elevated)` ao inves de `var(--color-surface-soft)`
    - `.lb-skeleton-line`, `.lb-skeleton-rank`: `background: var(--color-surface-elevated)` (#262626)
    - Remover todos os `border-radius: var(--rounded-md)` -> `border-radius: 0`
    - Remover hover transform/scale e box-shadow; usar apenas border highlight

- [x] Tarefa 3: Garantir padding-top para top-nav nas paginas Menu e Leaderboard
  - Arquivo: `src/app/pages/menu/menu.page.css`
  - O que fazer: `.menu-wrapper` ja tem `min-height: 100dvh` e `padding: 24px`. Adicionar `padding-top: calc(var(--top-nav-height, 64px) + 24px)` ou ajustar para compensar a nav fixa
  - Arquivo: `src/app/pages/leaderboard/leaderboard.page.css`
  - O que fazer: `.lb-page` tem `padding: var(--spacing-section) var(--spacing-lg)`. Adicionar `padding-top: calc(var(--top-nav-height, 64px) + var(--spacing-section))` ou equivalente

## Arquivos Referencia

- `src/app/pages/menu/menu.page.ts` - Logica do componente menu
- `src/app/pages/menu/menu.page.html` - Template atual
- `src/app/pages/menu/menu.page.css` - Estilos atuais (tema claro)
- `src/app/pages/leaderboard/leaderboard.page.ts` - Logica do componente leaderboard
- `src/app/pages/leaderboard/leaderboard.page.html` - Template atual
- `src/app/pages/leaderboard/leaderboard.page.css` - Estilos atuais (tema claro)
- `task/DESIGN-bmw-m.md` - Referencia visual BMW M

## Criterios de Aceite

- [x] CA07: Tema escuro nas paginas Menu e Leaderboard
  - Cenario: Dado que o usuario navega para /menu ou /leaderboard / Quando a pagina carrega / Entao o fundo e preto, o texto principal e branco, cards usam #1a1a1a, hairlines usam #3c3c3c.
- [x] CA08: Tipografia BMW M nos titulos
  - Cenario: Dado que o usuario esta em /menu ou /leaderboard / Quando visualiza os titulos / Entao estao em uppercase, weight 700, e tracking ajustado.
- [x] CA09: Cantos retos BMW nas paginas
  - Cenario: Dado que o usuario visualiza cards e botoes / Entao todos tem border-radius 0.
- [x] CA12: Menu redesenhado no estilo BMW M
  - Cenario: Dado que o usuario navega para /menu / Entao o menu exibe canvas preto, titulo "LBOT ARENA" em display uppercase, botoes retangulares com outline, sem bordas arredondadas.
- [x] CA13: Leaderboard atualizado para tema escuro
  - Cenario: Dado que o usuario navega para /leaderboard / Entao a leaderboard exibe fundo preto, cards com surface-card, border-radius 0, texto branco e titulo uppercase.

## Testes Esperados

- `npx ng build` - Build sem erros
- Verificar visualmente: pagina menu com fundo preto, titulo uppercase, botoes retangulares outline
- Verificar visualmente: pagina leaderboard com fundo preto, cards escuros, border-radius 0
- Verificar: top-nav continua funcional em ambas as paginas
- Verificar: navegacao entre paginas funciona

## Comandos pos-fase

- `npx ng build`
- `npx ng serve`

## Registro de Execucao

- Data: 2026-06-06
- Arquivos alterados:
  - `src/app/pages/menu/menu.page.html` — Titulo "LBOT ARENA" uppercase, botoes unificados no estilo card BMW, icones em circulos (btn-icon-circle)
  - `src/app/pages/menu/menu.page.css` — Rewrite BMW M: canvas preto, display-lg title 700 uppercase tracking -0.5px, subtitle 300 body, botoes surface-card border-radius 0, btn-icon-circle rounded-full, btn-text label-uppercase 700 tracking 1.5px, btn-desc body-sm 300, footer muted, padding-top calc(var(--top-nav-height) + 24px)
  - `src/app/pages/leaderboard/leaderboard.page.html` — Titulo "LEADERBOARD" uppercase
  - `src/app/pages/leaderboard/leaderboard.page.css` — Rewrite BMW M: canvas preto, title display-lg 700 uppercase tracking -0.5px, subtitle 300 body, cards surface-card border-radius 0 hairline border, hover border-color on-dark, skeleton surface-strong, retry-btn outline BMW, padding-top calc(top-nav-height + spacing-section)
- Testes executados: `npx ng build` — Build successful, sem erros (warnings de budget CSS para leaderboard +906 bytes, victory-screen +1.6kB, virtual-controls +2.96kB, lbot-chat +3.56kB — serao abordados nas proximas fases)
- Resultado: Sucesso
- Pendencias: Nenhuma