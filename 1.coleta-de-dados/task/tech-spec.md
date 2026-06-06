# Plano Tecnico: Redesign UI LBot DataGen - Estilo Airbnb

## Visao Geral

Redesign completo da UI do LBot DataGen, substituindo o tema dark/neon verde atual por um design system Airbnb (canvas branco, Rausch como acento unico, Inter como tipografia). A abordagem e puramente visual (HTML/CSS/templates) — nenhum service, model ou logica de negocio e alterado. O componente `robo-simulator` (canvas 3D Three.js) permanece inalterado.

**Estrategia**: Redesign componente-a-componente, substituindo o tema dark por tokens Airbnb em 5 fases sequenciais, cada uma entregando um subset testavel de componentes.

## Decisoes Tecnicas

| Decisao | Opcao escolhida | Justificativa |
|---------|-----------------|---------------|
| Fonte | Inter via Google Fonts CDN | Substituto open-source do Airbnb Cereal VF; carregamento via CDN e simples e performatico |
| Tokens CSS | Todas as custom properties em `styles.css` | Centralizacao simples; nao ha necessidade de arquivos separados para ~50 variaveis |
| Animacoes | CSS puro (keyframes + transitions) | Os overlays ja usam CSS puro; manter consistente, sem adicionar dependencia de @angular/animations |
| SSR | Sem fase dedicada de testes SSR | CSS puro e HTML nao afetam SSR; validacao manual pos-cada fase |
| Testes | Nao adicionar testes automatizados | Foco 100% no redesign visual; componentes nao tem logica complexa |
| Divisao de fases | 5 fases menores (2-3 componentes cada) | Menos risco, mais iterativo, cada fase e testavel independentemente |
| Responsividade | Integrada em cada fase | Cada componente recebe tratamento responsive no momento da implementacao |

## Modulos Envolvidos

- **app (root)**: Layout shell, global styles, top-nav
- **pages/menu**: Landing page com hero e search bar
- **pages/game**: Layout split simulador + chat, HUD overlay
- **pages/leaderboard**: Cards de ranking
- **pages/controls**: Layout duas colunas simulador + controles
- **components/lbot-chat**: Chat bubbles, input, estrelas, popups
- **components/level-transition**: Overlay entre niveis
- **components/victory-screen**: Overlay de vitoria
- **components/confirm-modal**: Modal de confirmacao
- **components/virtual-controls**: Botoes direcionais, timeline
- **Novo componente**: components/top-nav (barra de navegacao global)

## Arquivos Impactados

### Novos
- `src/app/components/top-nav/top-nav.ts` - Componente standalone de navegacao global (RF02)
- `src/app/components/top-nav/top-nav.html` - Template da top nav
- `src/app/components/top-nav/top-nav.css` - Estilos da top nav (80px, tabs, responsivo)

### Alterados
- `src/styles.css` - Reset global + todos os tokens Airbnb como CSS custom properties
- `src/app/app.css` - Remover variaveis dark, adaptar layout shell com top-nav
- `src/app/app.html` - Adicionar `<app-top-nav>` acima do `<router-outlet>`
- `src/app/app.ts` - Importar TopNavComponent
- `src/index.html` - Adicionar link para Google Fonts (Inter)
- `src/app/pages/menu/menu.page.html` - Redesign completo: hero + search bar
- `src/app/pages/menu/menu.page.css` - Redesign completo para estilo Airbnb
- `src/app/pages/game/game.page.html` - Ajustar HUD para estilo Airbnb, nav links
- `src/app/pages/game/game.page.css` - Redesign: split layout, HUD branco, chat panel
- `src/app/components/lbot-chat/lbot-chat.html` - Ajustar classe CSS para estilo Airbnb
- `src/app/components/lbot-chat/lbot-chat.css` - Redesign completo: bolhas, input, estrelas
- `src/app/components/level-transition/level-transition.html` - Ajustar para card branco
- `src/app/components/level-transition/level-transition.css` - Redesign para Airbnb overlay
- `src/app/components/victory-screen/victory-screen.html` - Ajustar para card branco
- `src/app/components/victory-screen/victory-screen.css` - Redesign para Airbnb overlay
- `src/app/components/confirm-modal/confirm-modal.html` - Ajustar para card branco
- `src/app/components/confirm-modal/confirm-modal.css` - Redesign para Airbnb overlay
- `src/app/pages/leaderboard/leaderboard.page.html` - Converter tabela para card grid
- `src/app/pages/leaderboard/leaderboard.css` - Redesign completo para cards Airbnb
- `src/app/pages/controls/controls.page.html` - Ajustar layout e estilo
- `src/app/pages/controls/controls.page.css` - Redesign para tema claro Airbnb
- `src/app/components/virtual-controls/virtual-controls.html` - Ajustar botoes e timeline
- `src/app/components/virtual-controls/virtual-controls.css` - Redesign para Airbnb style

## Arquivos Nao Alterados

- `src/app/components/robo-simulator/robo-simulator.ts` - Canvas 3D (excluido do redesign)
- `src/app/components/robo-simulator/robo-simulator.css` - Canvas 3D (excluido do redesign)
- `src/app/components/simulator-frame/*` - Wrapper de iframe (excluido)
- Todos os services (`*.service.ts`) - Logica de negocio inalterada
- Todos os models (`*.model.ts`) - Interfaces inalteradas
- `src/app/app.routes.ts` - Rotas inalteradas
- `src/app/app.config.ts` - Configuracao inalterada
- Ambientes (`environment.ts`, `environment.prod.ts`) - Inalterados

## Dependencias entre Fases

- Fase 1 -> Todas as demais (tokens CSS sao base para tudo)
- Fase 2 -> Fase 1 (top-nav precisa de tokens)
- Fase 3 -> Fase 1, Fase 2 (chat herda tokens e esta dentro da game page que precisa da nav)
- Fase 4 -> Fase 1 (overlays usam tokens)
- Fase 5 -> Fase 1, Fase 2 (leaderboard e controls precisam de tokens e nav)

## Mapa de Fases

| Fase | Descricao | Componentes/Arquivos Principais |
|------|-----------|--------------------------------|
| 01 | Design System Foundation | styles.css, app.css, app.html, index.html |
| 02 | Top Nav + Menu/Home Page | top-nav (novo), menu.page |
| 03 | Chat + Game Page + HUD | lbot-chat, game.page, HUD overlay |
| 04 | Overlay Components | level-transition, victory-screen, confirm-modal |
| 05 | Leaderboard + Controls + Virtual Controls | leaderboard.page, controls.page, virtual-controls |