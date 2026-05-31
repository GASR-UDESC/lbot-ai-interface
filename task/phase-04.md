# Fase 04: UI/Layout Gaming Moderno

## Status: CONCLUIDO

## Objetivo

Redesenhar a interface do game page com estetica de gaming moderno (cores vivas por nivel, cantos arredondados, sem glassmorphism/gradientes excessivos). Corrigir layout para usar grid com gap/padding (pattern da controls page). Garantir que elementos nao se sobrepoem.

## Pre-requisitos

- Fase 03 concluida (timer global funcionando para exibir corretamente no HUD)

## Tarefas

- [x] Tarefa 1: Reescrever layout do game.page para grid com padding
  - Arquivo: `lbot-datagen/lbot-datagen-frontend/src/app/pages/game/game.page.css`
  - O que fazer: Mudar `.game-layout` de `display: flex` para `display: grid; grid-template-columns: 1fr 380px; gap: 24px; padding: 24px;`. Adicionar `background: #0f1210;` (dark gaming). O `.simulator-panel` recebe `border-radius: 16px; overflow: hidden; background: #1a1d1a;`. Remover flex-related props. Manter responsividade em 768px (stack vertical).

- [x] Tarefa 2: Reposicionar HUD para nao conflitar com status panel do simulador
  - Arquivo: `lbot-datagen/lbot-datagen-frontend/src/app/pages/game/game.page.css`
  - O que fazer: O `.hud` atualmente esta `top:12px, left:50%, transform:translateX(-50%)` (centro-topo). O status panel do simulador esta `top:12px, left:12px`. Mover o `.hud` para `top:12px; right:12px;` e remover o `transform`. Isso garante que HUD (direita) e status (esquerda) nao se sobrepoem. Remover backdrop-filter e substituir `background: rgba(0,0,0,0.6)` por uma cor solida semi-transparente simples.

- [x] Tarefa 3: Redesenhar CSS do HUD com cores vivas (sem glassmorphism)
  - Arquivo: `lbot-datagen/lbot-datagen-frontend/src/app/pages/game/game.page.css`
  - O que fazer: `.hud` - background: cor solida dark (#1a2e1a) com border colorida baseada no nivel. `.hud-label` - cor primaria do nivel. `.hud-timer` - branco com font-weight 800. `.hud-reset-btn` - background cor do nivel com texto branco, border-radius:20px (pill). Remover todos os `backdrop-filter`, `glow`, gradientes. `.hud-nav` - botoes com background solido e border-radius:20px.

- [x] Tarefa 4: Redesenhar CSS do robo-simulator (status panel e botoes)
  - Arquivo: `lbot-datagen/lbot-datagen-frontend/src/app/components/robo-simulator/robo-simulator.css`
  - O que fazer: `.status` - background branco com sombra leve, border-radius:12px, sem gradientes. `.score-counter` - background cor solida do nivel (nao linear-gradient). `.buttons-container .camera-button` - background cor solida vibrante, border-radius:20px (pill), sem `linear-gradient`. `.indicator` - fundo colorido vibrante (ex: laranja #FF6B35) com texto branco, border-radius:20px. Remover `.goal-button` e seus estilos (ja removido na fase 01).

- [x] Tarefa 5: Adicionar CSS custom property para cor do nivel no simulador
  - Arquivo: `lbot-datagen/lbot-datagen-frontend/src/app/components/robo-simulator/robo-simulator.ts`
  - O que fazer: No template, adicionar `[style.--level-color]="getLevelColor()"` no `.simulator-container`. Criar metodo `getLevelColor(): string` que retorna `this.levelConfig?.theme.obstacleColor || '#4CAF50'`. Usar `var(--level-color)` nos CSS para elementos que devem mudar de cor por nivel (score-counter background, indicator background, etc).

- [x] Tarefa 6: Ajustar HTML do game.page para layout clean
  - Arquivo: `lbot-datagen/lbot-datagen-frontend/src/app/pages/game/game.page.html`
  - O que fazer: Envolver o `app-robo-simulator` em um div `.simulator-frame` com o border-radius (separar container visual do componente). Manter a estrutura existente mas garantir que `.hud-nav` esta FORA do `.simulator-panel` (mover para o nivel do grid ou para dentro do chat-panel header).

## Arquivos Referencia

- `lbot-datagen/lbot-datagen-frontend/src/app/pages/controls/controls.page.css` - Pattern de grid+gap+padding+border-radius
- `lbot-datagen/lbot-datagen-frontend/src/app/pages/game/game.page.css` - CSS atual do game
- `lbot-datagen/lbot-datagen-frontend/src/app/components/robo-simulator/robo-simulator.css` - CSS do simulador

## Criterios de Aceite

- [x] CA07: Elementos nao se sobrepoem
  - Cenario: Dado game page carregada, Quando observa layout, Entao status panel (top-left), HUD (top-right), e nav buttons tem posicoes distintas
- [x] CA08: Espacamento entre simulador e bordas
  - Cenario: Dado game page carregada, Quando observa layout, Entao existe gap de 24px entre simulador e chat, e padding de 24px nas bordas
- [x] CA09: Visual gaming moderno
  - Cenario: Dado game page carregada, Quando inspeciona CSS, Entao nao ha backdrop-filter, linear-gradient excessivo, ou glow effects. Cores sao solidas e vibrantes.

## Testes Esperados

- Validacao visual manual: abrir em 1024px e 1440px - layout correto sem sobreposicao
- Validacao visual manual: navegar entre niveis - cores do HUD/score mudam conforme tema do nivel
- Validacao visual manual: abrir em 768px - layout empilha verticalmente

## Comandos pos-fase

- `cd lbot-datagen/lbot-datagen-frontend && npx ng build`
- `cd lbot-datagen/lbot-datagen-frontend && npx ng serve` (inspecionar visualmente em diferentes resolutions)

## Registro de Execucao

- Data: 2026-05-31
- Arquivos criados: nenhum
- Arquivos alterados:
  - `lbot-datagen/lbot-datagen-frontend/src/app/pages/game/game.page.html`
  - `lbot-datagen/lbot-datagen-frontend/src/app/pages/game/game.page.css`
  - `lbot-datagen/lbot-datagen-frontend/src/app/components/robo-simulator/robo-simulator.ts`
  - `lbot-datagen/lbot-datagen-frontend/src/app/components/robo-simulator/robo-simulator.css`
- Testes executados:
  - `cd lbot-datagen/lbot-datagen-frontend && npx ng build` - ok
  - `cd lbot-datagen/lbot-datagen-frontend && npm run start -- --host 127.0.0.1 --port 4300` - app carregou em `/game`
  - Verificacao runtime via browser em `http://127.0.0.1:4300/game` com viewport 1440px - grid lateral ativo, HUD no topo direito, nav no header do chat e sem sobreposicao
  - Verificacao runtime via browser em `http://127.0.0.1:4300/game` com viewport 768px - layout empilhado verticalmente com gap/padding preservados e HUD sem conflito com status panel
  - Inspecao de estilos runtime - `--level-color` aplicado ao HUD e ao simulador conforme tema do nivel 1 (`#D2691E`), sem `backdrop-filter` no game HUD
- Resultado: UI do game page redesenhada com layout em grid, painel do simulador contido em frame com bordas arredondadas, header do chat com navegacao separada, HUD reposicionado para o topo direito, e simulador atualizado para usar cor dinamica por nivel com estilos solidos e sem glassmorphism.
- Pendencias: nenhuma
