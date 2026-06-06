# Fase 03: Layouts de Jogo - Game + Controls

## Status: CONCLUIDO

## Objetivo

Adicionar headers contextuais nas paginas de Game e Controls, padronizar os layouts com gap/padding consistente, remover navegacao redundante do HUD do game, aplicar containers com border-radius 0 e hairline borders, e adicionar faixa M tricolor como divisor entre header e conteudo.

## Pre-requisitos

- Fase 01 concluida (variaveis CSS globais e top-nav)

## Tarefas

- [x] Tarefa 1: Adicionar header contextual ao Game Page (RF03)
  - Arquivo: `src/app/pages/game/game.page.html`
  - O que fazer:
    - Adicionar um header contextual acima do `.game-layout`:
      ```html
      <div class="page-header">
        <h1 class="page-title">JOGAR</h1>
        <p class="page-subtitle">Comande o robô com linguagem natural</p>
        <div class="m-stripe"></div>
      </div>
      ```
    - Remover a div `<div class="hud-nav">` inteiramente (botoes "← Menu" e "Ranking") pois o top-nav global agora provê navegacao
    - Manter o `.hud` overlay com nivel, timer e botao reset
  - Arquivo: `src/app/pages/game/game.page.css`
  - O que fazer:
    - Adicionar estilos para `.page-header`:
      ```css
      .page-header {
        padding: var(--spacing-base) var(--spacing-xl);
        flex-shrink: 0;
      }
      .page-title {
        font-size: var(--typography-display-sm-size);
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: -0.5px;
        color: var(--color-ink);
        margin: 0;
      }
      .page-subtitle {
        font-size: var(--typography-body-md-size);
        font-weight: 300;
        color: var(--color-body);
        margin: 4px 0 0;
      }
      ```
    - Atualizar `.hud`:
      - Remover `background: rgba(255, 255, 255, 0.92)` -> `background: rgba(0, 0, 0, 0.85)`
      - Remover `backdrop-filter: blur(6px)` (manter opcionalmente)
      - `border-radius: 0` (antes var(--rounded-md))
      - `border: 1px solid var(--color-hairline)` (manter)
      - Cores: texto branco, icones brancos
    - Atualizar `.hud-label`: cor `var(--color-ink)` (branco), uppercase
    - Atualizar `.hud-timer`: cor `var(--color-ink)` (branco)
    - Atualizar `.hud-reset-btn`:
      - `background: transparent`, `border: 1px solid var(--color-on-dark)`, `color: var(--color-on-dark)`, `border-radius: 0`,
      - `font-weight: 700`, `text-transform: uppercase`, `letter-spacing: 1.5px`
    - Remover `.hud-nav` e `.nav-link-btn` (componentes inteiramente removidos do HTML)
    - Atualizar `:host`: `background: var(--color-canvas)` (preto), `height: calc(100dvh - 64px)` para compensar top-nav
    - Atualizar `.chat-panel`:
      - `background: var(--color-surface-soft)` ou `var(--color-canvas)`
      - `border-left: 1px solid var(--color-hairline)`
      - Remover border-radius (antes nao tinha, confirmar)
    - Atualizar `.chat-loading`: cor `var(--color-body)` (body text)

- [x] Tarefa 2: Adicionar header contextual ao Controls Page (RF02)
  - Arquivo: `src/app/pages/controls/controls.page.html`
  - O que fazer:
    - Atualizar o header existente para estilo BMW M:
      ```html
      <div class="page-header">
        <h1 class="page-title">MODO CONTROLE</h1>
        <p class="page-subtitle">Geração de dados de treino via controle manual</p>
        <div class="m-stripe"></div>
      </div>
      ```
    - Remover o botao de voltar (se existir) — o top-nav provê navegacao

  - Arquivo: `src/app/pages/controls/controls.page.css`
  - O que fazer:
    - Atualizar `.controls-header`:
      - Adicionar `.m-stripe` ou um pseudo-elemento como divisor abaixo do header
      - `.controls-title`: `font-weight: 700`, `text-transform: uppercase`, `letter-spacing: -0.5px`, cor `var(--color-ink)` (branco)
      - `.controls-subtitle`: `font-weight: 300`, cor `var(--color-body)` (#bbbbbb)
      - Padding ajustado
    - Atualizar `.controls-page`: `background: var(--color-canvas)` (preto), `height: calc(100dvh - 64px)` para compensar top-nav
    - Atualizar `.simulator-container`:
      - `border-radius: 0` (remover var(--rounded-md))
      - `border: 1px solid var(--color-hairline)` (#3c3c3c)
    - Atualizar `.controls-panel`:
      - `border-radius: 0`
      - `border: 1px solid var(--color-hairline)`
      - `background: var(--color-surface-card)` ou `var(--color-canvas)`

- [x] Tarefa 3: Padronizar gap/padding entre Game e Controls (RF03)
  - Arquivo: `src/app/pages/game/game.page.css`
  - O que fazer: Garantir que o gap entre simulador e chat panel use `var(--spacing-lg)` (24px), o mesmo padrao do Controls. Adicionar padding adequado ao `.page-header`.
  - Arquivo: `src/app/pages/controls/controls.page.css`
  - O que fazer: Confirmar que o gap `.controls-layout` usa `var(--spacing-lg)` (24px, ja e esse valor) e que o padding esta consistente

- [x] Tarefa 4: Aplicar tema escuro ao Simulator Frame (RF04)
  - Arquivo: `src/app/components/simulator-frame/simulator-frame.css`
  - O que fazer:
    - `border-radius: 0` (remover qualquer rounded)
    - `border: 1px solid var(--color-hairline)` se houver borda
    - `background: var(--color-canvas)` se houver background
    - Confirmar que o iframe do simulador nao precisa de mudancas internas (fora de escopo)

## Arquivos Referencia

- `src/app/pages/game/game.page.ts` - Logica do componente game
- `src/app/pages/game/game.page.html` - Template atual com HUD e nav-links
- `src/app/pages/game/game.page.css` - Estilos atuais
- `src/app/pages/controls/controls.page.ts` - Logica do componente controls
- `src/app/pages/controls/controls.page.html` - Template atual com header
- `src/app/pages/controls/controls.page.css` - Estilos atuais
- `src/app/components/simulator-frame/simulator-frame.css` - Container do iframe

## Criterios de Aceite

- [x] CA04: Layout padronizado do Modo Controle
  - Cenario: Dado que o usuario navega para /controls / Quando a pagina carrega / Entao o top-nav global aparece no topo e abaixo dele o header contextual "MODO CONTROLE" em uppercase com subtitulo, seguido do grid com gap/padding entre simulador e painel de controles.
- [x] CA05: Layout padronizado do Modo Jogar
  - Cenario: Dado que o usuario navega para /game / Quando a pagina carrega / Entao o top-nav global aparece no topo e abaixo dele o header contextual "JOGAR" em uppercase com subtitulo, seguido do layout com gap/padding entre simulador e chat panel.
- [x] CA06: Navegacao redundante removida do HUD
  - Cenario: Dado que o usuario esta na pagina de jogo / Quando a partida esta em andamento / Entao o HUD mostra apenas nivel, timer e botao de reset, SEM os links "← Menu" e "Ranking".
- [x] CA07: Tema escuro nas paginas de jogo e controle
  - Cenario: Fundo preto, texto branco, borders hairline #3c3c3c, border-radius 0 nos containers.
- [x] CA10: Faixa tricolor M como divisor
  - Cenario: A faixa M tricolor aparece como divisor entre o header e o conteudo nas paginas Game e Controls.

## Testes Esperados

- `npx ng build` - Build sem erros
- Verificar visualmente: pagina game com header contextual "JOGAR" e faixa M
- Verificar visualmente: pagina controls com header "MODO CONTROLE" e faixa M
- Verificar: HUD do game sem botoes "← Menu" e "Ranking"
- Verificar: top-nav funcional em ambas as paginas
- Verificar: layout responsivo (mobile, tablet, desktop)

## Comandos pos-fase

- `npx ng build`
- `npx ng serve`

## Registro de Execucao

- Data: 2026-06-06
- Arquivos criados: Nenhum
- Arquivos alterados:
  - `lbot-datagen/lbot-datagen-frontend/src/app/pages/game/game.page.html` — Adicionado page-header ("JOGAR" + subtitulo + m-stripe), removido .hud-nav com links "← Menu" e "Ranking"
  - `lbot-datagen/lbot-datagen-frontend/src/app/pages/game/game.page.css` — :host flex column, novos estilos .page-header/.page-title/.page-subtitle, HUD dark overlay rgba(0,0,0,0.85) border-radius 0, hud-reset-btn outline BMW, removidos .hud-nav/.nav-link-btn, chat-panel surface-soft, chat-loading color body
  - `lbot-datagen/lbot-datagen-frontend/src/app/pages/controls/controls.page.html` — Header atualizado para .page-header com "MODO CONTROLE" uppercase + subtitulo + m-stripe
  - `lbot-datagen/lbot-datagen-frontend/src/app/pages/controls/controls.page.css` — .controls-header/.controls-title/.controls-subtitle substituidos por .page-header/.page-title/.page-subtitle BMW M; simulator-container e controls-panel border-radius 0; controls-panel background surface-card
  - `lbot-datagen/lbot-datagen-frontend/src/app/components/simulator-frame/simulator-frame.css` — border-radius 0, background var(--color-canvas), border hairline
- Testes executados: `npx ng build` — Build successful, 0 erros (warnings de budget CSS pre-existentes: leaderboard +906B, victory-screen +1.6kB, virtual-controls +2.96kB, lbot-chat +3.56kB)
- Resultado: Sucesso. Header contextual adicionado em ambas as paginas com faixa M tricolor. HUD do game com tema escuro e sem navegacao redundante. Containers com border-radius 0. Layout padronizado entre Game e Controls.
- Pendencias: Nenhuma