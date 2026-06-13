# Plano Tecnico: Migracao de Estilizacao BMW para Coinbase

## Visao Geral

Migracao completa da identidade visual do `lbot-datagen-frontend` (Angular 20) do tema BMW M Motorsport (dark theme, sharp corners, uppercase) para o design system Coinbase (light theme, pill buttons, editorial typography, dark hero bands). A migracao e puramente CSS/HTML — nenhuma logica de componentes Angular sera alterada.

**Abordagem:** Substituicao dos design tokens globais em `styles.css`, remocao de todos os elementos BMW (m-stripe), migracao de cada componente/pagina para os padroes Coinbase (pill buttons, border-radius xl, weight 400 display, JetBrains Mono para numeros), e adicao do dark hero pattern nas paginas Game e Controls.

## Modulos Envolvidos

- **styles.css (global):** Substituicao completa dos design tokens (cores, spacing, rounded, typography) e classes utilitarias (.btn-outline, .btn-filled, .m-stripe)
- **index.html:** Adicao da fonte JetBrains Mono via Google Fonts
- **top-nav:** Migracao para light theme, remocao de m-stripe
- **menu page:** Migracao para light theme com cards estilo Coinbase feature-card
- **leaderboard page:** Migracao para light theme, JetBrains Mono para tempos
- **game page:** Dark hero pattern no header, HUD com dark elevated surface
- **controls page:** Dark hero pattern no header
- **lbot-chat:** Light theme, border-radius xl/md, pill buttons
- **victory-screen:** Overlay com scrim, card xl, pill buttons, JetBrains Mono
- **level-transition:** Overlay dark, card xl, pill button
- **confirm-modal:** Card xl, pill buttons
- **virtual-controls:** Pill buttons, border-radius xl/sm nos containers
- **robo-simulator:** Migracao de cores hardcoded para variaveis CSS Coinbase
- **simulator-frame:** Border-radius xl no container

## Arquivos Impactados

### Novos
- Nenhum arquivo novo sera criado.

### Alterados
- `src/index.html` - Adicionar link Google Fonts para JetBrains Mono
- `src/styles.css` - Substituicao completa dos design tokens e classes utilitarias
- `src/app/app.css` - Ajuste de background-color (ja usa var, deve funcionar automaticamente)
- `src/app/components/top-nav/top-nav.html` - Remover 2 elementos `<div class="m-stripe">`
- `src/app/components/top-nav/top-nav.css` - Migracao para light theme, remover referencias m-stripe
- `src/app/pages/menu/menu.page.css` - Migracao para light theme, border-radius xl, pill style nos botoes
- `src/app/pages/menu/menu.page.html` - Remover uppercase dos textos
- `src/app/pages/leaderboard/leaderboard.page.css` - Migracao para light theme, border-radius xl, JetBrains Mono
- `src/app/pages/leaderboard/leaderboard.page.html` - Remover uppercase dos titulos
- `src/app/pages/game/game.page.html` - Remover m-stripe, remover uppercase do titulo
- `src/app/pages/game/game.page.css` - Dark hero header, HUD dark elevated, border-radius xl
- `src/app/pages/controls/controls.page.html` - Remover m-stripe, remover uppercase do titulo
- `src/app/pages/controls/controls.page.css` - Dark hero header, border-radius xl
- `src/app/components/lbot-chat/lbot-chat.css` - Border-radius xl/md, pill buttons, light theme
- `src/app/components/lbot-chat/lbot-chat.html` - Remover uppercase dos textos
- `src/app/components/victory-screen/victory-screen.css` - Border-radius xl, pill buttons, JetBrains Mono
- `src/app/components/victory-screen/victory-screen.html` - Remover uppercase dos textos
- `src/app/components/level-transition/level-transition.css` - Border-radius xl, pill button
- `src/app/components/level-transition/level-transition.html` - Remover uppercase dos textos
- `src/app/components/confirm-modal/confirm-modal.css` - Border-radius xl, pill buttons
- `src/app/components/confirm-modal/confirm-modal.html` - Remover uppercase
- `src/app/components/virtual-controls/virtual-controls.css` - Border-radius xl/sm, pill buttons
- `src/app/components/virtual-controls/virtual-controls.html` - Remover uppercase
- `src/app/components/robo-simulator/robo-simulator.css` - Migracao completa de cores hardcoded para variaveis CSS
- `src/app/components/simulator-frame/simulator-frame.css` - Border-radius xl

## Decisoes Tecnicas

| Decisao | Opcao escolhida | Justificativa |
|---------|-----------------|---------------|
| Fonte display | Inter (substituta CoinbaseDisplay) | Fontes Coinbase sao licenciadas; Inter ja esta carregada no projeto |
| Fonte mono | JetBrains Mono (substituta CoinbaseMono) | Recomendada pelo proprio DESIGN-coinbase.md como substituta |
| Carregamento de fontes | Google Fonts no index.html | Padrao ja utilizado para Inter |
| Estrategia de migracao | CSS/HTML apenas, sem alterar .ts | A migracao e puramente visual; logica Angular nao e afetada |
| robo-simulator.css | Migracao completa para variaveis CSS | Decisao do usuario; unificar identidade visual em todo o app |
| Dark hero padding | Adaptado (48px em vez de 96px) | App context (game/controls) precisa de menos padding que marketing page |
| Border-radius cards | var(--rounded-xl) = 24px | Conforme design system Coinbase |
| Border-radius botoes | var(--rounded-pill) = 100px | Conforme design system Coinbase |
| Cores semanticas | --color-semantic-up/down como text-color only | Conforme regra do design system Coinbase |

## Dependencias entre Fases

- Fase 1 -> Fase 2 (tokens globais e fontes precisam estar migrados)
- Fase 1 -> Fase 3 (tokens globais e fontes precisam estar migrados)
- Fase 1 -> Fase 4 (tokens globais precisam estar migrados)
- Fase 2, 3 e 4 sao independentes entre si (podem ser executadas em qualquer ordem apos Fase 1)

## Mapa de Fases

| Fase | Descricao | Arquivos |
|------|-----------|----------|
| 01 | Design tokens + fontes + remocao m-stripe global | `index.html`, `styles.css`, `top-nav.html` |
| 02 | Paginas light: Nav + Menu + Leaderboard | `top-nav.css`, `top-nav.html`, `menu.page.css`, `menu.page.html`, `leaderboard.page.css`, `leaderboard.page.html` |
| 03 | Dark hero: Game + Controls | `game.page.css`, `game.page.html`, `controls.page.css`, `controls.page.html` |
| 04 | Componentes de jogo + robo-simulator | `lbot-chat.*`, `victory-screen.*`, `level-transition.*`, `confirm-modal.*`, `virtual-controls.*`, `robo-simulator.css`, `simulator-frame.css` |
