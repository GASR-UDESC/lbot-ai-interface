# Fase 05: Tipografia Final + Auditoria Border-Radius + Polish

## Status: PENDENTE

## Objetivo

Auditoria final de toda a aplicacao: garantir que a tipografia BMW M esta consistente (uppercase labels, weight 300 para body, weight 700 para headings, tracking correto), que todos os border-radius estao em 0 (exceto icones circulares), que a faixa M tricolor esta sendo usada corretamente como divisor de marca, e que a responsividade esta funcionando em todos os breakpoints.

## Pre-requisitos

- Fases 01, 02, 03 e 04 concluidas

## Tarefas

- [ ] Tarefa 1: Auditoria de tipografia em TODOS os componentes
  - Arquivos: Todos os arquivos CSS dos componentes
  - O que fazer:
    - **Headings/titulos de pagina**: Devem ser `font-weight: 700`, `text-transform: uppercase`, `letter-spacing: -0.5px` (para display-lg e acima)
    - **Body text**: Deve ser `font-weight: 300` (Light) para paragrafos e textos descritivos
    - **Button labels**: Devem ser `font-weight: 700`, `text-transform: uppercase`, `letter-spacing: 1.5px`
    - **Nav links/pills/badges**: Devem ser `font-size: 14px`, `font-weight: 700`, `letter-spacing: 1.5px`, uppercase
    - **Labels de secao/grupo**: Devem ser uppercase com tracking 1.5px
    - Verificar cada componente:
      - `menu.page.css`: titulo uppercase, subtitle weight 300, botoes uppercase tracking 1.5px
      - `leaderboard.page.css`: titulo uppercase, cards com info correto
      - `game.page.css`: page-title uppercase, HUD labels uppercase
      - `controls.page.css`: page-title uppercase, subtitle weight 300
      - `lbot-chat.css`: header uppercase, button labels uppercase tracking 1.5px
      - `virtual-controls.css`: labels uppercase tracking 1.5px, body weight 300
      - `victory-screen.css`: titulo uppercase, labels uppercase, buttons uppercase tracking 1.5px
      - `level-transition.css`: badge uppercase tracking 1.5px, button uppercase
      - `confirm-modal.css`: buttons uppercase tracking 1.5px
    - Auditar hardcoded font-size/weight que nao usam variaveis CSS e substituir por variaveis

- [ ] Tarefa 2: Auditoria de border-radius em TODOS os componentes
  - Arquivos: Todos os arquivos CSS dos componentes
  - O que fazer:
    - Buscar por TODOS os usos de `border-radius` em todos os CSS
    - Regra BMW M: `border-radius: 0` para botoes, cards, containers, inputs, modais
    - Excecao: `border-radius: var(--rounded-full)` ou `9999px` APENAS para:
      - Botoes circulares de icone: `.end-chat-btn` (chat close), `.remove-btn` (virtual controls)
      - Pills/badges small: `.level-badge` (level transition)
    - Verificar NENHUM uso de `border-radius: var(--rounded-md)` (que era 14px, agora 6px) em cards, botoes ou inputs — devem ser 0
    - Verificar NENHUM uso de `border-radius: var(--rounded-sm)` (que era 8px, agora 4px) em botoes grandes — devem ser 0
    - Inputs/textareas: `border-radius: 0`
    - Modals/overlays: `border-radius: 0`
    - Mensagens de chat: `border-radius: 0`
    - Menu buttons: `border-radius: 0`
    - Leaderboard cards: `border-radius: 0`

- [ ] Tarefa 3: Auditoria da faixa M tricolor
  - Arquivos: Todos os templates HTML
  - O que fazer:
    - Verificar que a faixa M tricolor aparece:
      1. Na borda inferior do top-nav (implementado na Fase 01)
      2. Como divisor entre header contextual e conteudo nas paginas Game e Controls (implementado na Fase 03)
    - Verificar que a faixa NAO aparece como:
      - Fundo de botao
      - Cor de texto
      - Superficie/card background
    - Verificar que nao ha uso duplicado ou indevido da faixa

- [ ] Tarefa 4: Auditoria de responsividade
  - Arquivos: Todos os arquivos CSS com media queries
  - O que fazer:
    - **Mobile (<768px)**:
      - Top-nav colapsa para hamburger (implementado na Fase 01)
      - Game layout: simulador e chat empilham verticalmente
      - Controls layout: simulador e controles empilham verticalmente
      - Leaderboard: cards em colunaunica
      - Menu: botoes empilhados verticalmente
    - **Tablet (768-1024px)**:
      - Top-nav horizontal
      - Layouts grid com 2 colunas
    - **Desktop (1024-1440px)**:
      - Top-nav horizontal
      - Layouts completos
    - **Wide (>1440px)**:
      - Max-width containers, mais espacamento
    - Verificar que a top-nav nao sobrepoem conteudo em nenhum breakpoint
    - Verificar que chat-panel no game page empilha corretamente em mobile

- [ ] Tarefa 5: Auditoria de cores hardcoded e cleanup final
  - Arquivos: Todos os arquivos CSS
  - O que fazer:
    - Buscar por qualquer valor hex hardcoded (ex: `#222222`, `#3f3f3f`, `#6a6a6a`, `#929292`, `#dddddd`, `#ebebeb`, `#c1c1c1`, `#ffffff`, `#f7f7f7`, `#f2f2f2`, `#ff385c`, `#e00b41`, `#ffd1da`, `#c13515`, `rgba(0, 0, 0, 0.5)`, `rgba(193, 53, 21, 0.08)`, etc.)
    - Substituir por variaveis CSS do BMW M:
      - `#222222` (old ink) -> `var(--color-ink)` (agora `#ffffff`)
      - `#3f3f3f` (old body) -> `var(--color-body)` (agora `#bbbbbb`)
      - `#6a6a6a` (old muted) -> `var(--color-muted)` (agora `#7e7e7e`)
      - `#929292` (old muted-soft) -> `var(--color-muted-soft)` (agora `#5e5e5e`)
      - `#dddddd` (old hairline) -> `var(--color-hairline)` (agora `#3c3c3c`)
      - `#ffffff` (old canvas) -> `var(--color-canvas)` (agora `#000000`)
      - `#f7f7f7` (old surface-soft) -> `var(--color-surface-soft)` (agora `#0d0d0d`)
      - `#f2f2f2` (old surface-strong) -> `var(--color-surface-strong)` (agora `#262626`)
      - `rgba(0, 0, 0, 0.5)` -> `rgba(0, 0, 0, 0.85)` (overlay escuro)
      - `rgba(193, 53, 21, 0.08)` -> `rgba(226, 39, 24, 0.1)` (error bg)
      - `rgba(255, 255, 255, 0.92)` -> `rgba(0, 0, 0, 0.85)` (HUD overlay)
    - Verificar que componentes que tinham fallbacks inline (ex: `var(--color-canvas, #ffffff)`) agora usam apenas `var(--color-canvas)` sem fallback
    - Remover shadows remanescentes (`box-shadow`, `--shadow-card-hover-float`)

- [ ] Tarefa 6: Atualizar jogo HUD overlay (RF03 + RF10)
  - Arquivo: `src/app/pages/game/game.page.css`
  - O que fazer:
    - O HUD ja foi parcialmente atualizado na Fase 03. Verificar:
    - `.hud`: `background: rgba(0, 0, 0, 0.85)`, `border: 1px solid var(--color-hairline)`, `border-radius: 0`
    - `.hud-label`: `color: var(--color-ink)`, `text-transform: uppercase`, `letter-spacing: 1.5px`, `font-weight: 700`
    - `.hud-timer`: `color: var(--color-ink)`, `font-variant-numeric: tabular-nums`
    - `.hud-reset-btn`: estilo outline BMW (`background: transparent`, `border: 1px solid var(--color-on-dark)`, `color: var(--color-on-dark)`, `border-radius: 0`, `font-weight: 700`, `text-transform: uppercase`, `letter-spacing: 1.5px`)
    - Confirmar que `.hud-nav` foi removido (Fase 03)

## Arquivos Referencia

- Todos os arquivos CSS dos componentes (auditados nas fases anteriores)
- `task/DESIGN-bmw-m.md` - Referencia visual BMW M
- `task/business-spec.md` - Especificacao de negocio (criterios de aceite CA05-CA16)

## Criterios de Aceite

- [ ] CA05: Layout padronizado do Modo Jogar
  - Cenario: Header contextual "JOGAR" em uppercase, gap/padding padronizado com Controls.
- [ ] CA07: Tema escuro BMW M em toda a aplicacao
  - Cenario: Sem cores hardcoded do tema claro; todas as cores via variaveis CSS BMW M.
- [ ] CA08: Tipografia BMW M com Inter
  - Cenario: Headings em uppercase weight 700, body text weight 300, buttons uppercase tracking 1.5px.
- [ ] CA09: Cantos retos BMW em todos os componentes
  - Cenario: Nenhum border-radius > 0 em botoes, cards, inputs, containers (exceto icones circulares).
- [ ] CA10: Faixa tricolor M como acento de marca
  - Cenario: Faixa M aparece na borda inferior do top-nav e como divisor nas paginas Game e Controls.
- [ ] CA11: Faixa tricolor nao usada como fundo ou texto
  - Cenario: A tricolor M nao aparece como background de botoes, cor de texto ou superficie.
- [ ] CA16: Responsividade mantida em todos os breakpoints
  - Cenario: Layout se adapta em mobile (<768px), tablet (768-1024px) e desktop (>1024px).

## Testes Esperados

- `npx ng build` - Build sem erros
- Verificacao visual completa em todos os breakpoints (mobile, tablet, desktop)
- Verificacao: nenhum border-radius > 0 (exceto icones circulares e pills)
- Verificacao: nenhum hardcoded color value do tema claro
- Verificacao: tipografia consistente (uppercase headings, light body, tracking correto)
- Verificacao: faixa M aparece apenas como divisor, nunca como fundo/texto
- Verificacao: responsive hamburger menu funcional em mobile
- Verificacao: todas as funcionalidades continuam operacionais

## Comandos pos-fase

- `npx ng build`
- `npx ng serve`
- Verificacao visual manual em todos os breakpoints

## Registro de Execucao

(Preenchido pelo agente durante a execucao)

- Data:
- Arquivos criados:
- Arquivos alterados:
- Testes executados:
- Resultado:
- Pendencias: