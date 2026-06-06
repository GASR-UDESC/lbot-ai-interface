# Plano Tecnico: Migracao Visual BMW M + Navegacao Global

## Visao Geral

Migracao completa do design system do LBot DataGen frontend do tema claro Airbnb-style para o tema escuro BMW M, incluindo criacao de componente de navegacao global (`app-top-nav`) e padronizacao de layout das paginas de jogo e controle.

A abordagem e **substituicao direta das variaveis CSS** no `:root` de `styles.css` — atualizando valorescomo de `#ffffff` para `#000000`, `#ff385c` para `#ffffff`, etc. — seguida de atualizacao componente a componente para corrigir hardcoded values e aplicar os padroes BMW M.

## Modulos Envolvidos

- **styles.css (global)**: Significa para as variaveis CSS e reset base
- **app-top-nav (novo componente)**: Navegacao global com menu hamburger mobile
- **app-root**: Template para incluir o top-nav
- **menu.page**: Redesign completo para estilo editorial BMW M
- **leaderboard.page**: Tema escuro BMW M
- **game.page**: Adicao de header contextual, remocao de nav-links do HUD, padronizacao de layout
- **controls.page**: Adicao de header contextual com faixa M
- **lbot-chat**: Tema escuro BMW M
- **virtual-controls**: Tema escuro BMW M
- **victory-screen**: Overlay BMW M
- **level-transition**: Overlay BMW M
- **confirm-modal**: Overlay BMW M

## Arquivos Impactados

### Novos

- `src/app/components/top-nav/top-nav.ts` - Componente standalone de navegacao global
- `src/app/components/top-nav/top-nav.html` - Template com nav desktop + hamburger mobile
- `src/app/components/top-nav/top-nav.css` - Estilos BMW M (fundo preto, faixa tricolor, hamburger)

### Alterados

- `src/styles.css` - Substituicao completa das variaveis CSS `:root` (cores, border-radius, tipografia)
- `src/app/app.ts` - Importar `TopNavComponent`
- `src/app/app.html` - Adicionar `<app-top-nav>` acima do `<router-outlet>`, remover padding-top se necessario
- `src/app/app.css` - Ajustar layout para acomodar top-nav
- `src/app/pages/menu/menu.page.html` - Redesign editorial BMW M
- `src/app/pages/menu/menu.page.css` - Estilos menu BMW M (canvas preto, botoes outline, uppercase)
- `src/app/pages/menu/menu.page.ts` - Ajustes se necessario
- `src/app/pages/leaderboard/leaderboard.page.html` - Titulo uppercase, botoes BMW M
- `src/app/pages/leaderboard/leaderboard.page.css` - Tema escuro completo
- `src/app/pages/game/game.page.html` - Adicionar header contextual, remover hud-nav links
- `src/app/pages/game/game.page.css` - Tema escuro, border-radius 0, hairline borders, gap padronizado
- `src/app/pages/controls/controls.page.html` - Adicionar header contextual com faixa M
- `src/app/pages/controls/controls.page.css` - Tema escuro, border-radius 0
- `src/app/components/lbot-chat/lbot-chat.html` - Labels uppercase BMW M
- `src/app/components/lbot-chat/lbot-chat.css` - Tema escuro (surface-card header, surface-soft/elevated messages, border-radius 0)
- `src/app/components/virtual-controls/virtual-controls.html` - Ajustes se necessario
- `src/app/components/virtual-controls/virtual-controls.css` - Tema escuro, border-radius 0
- `src/app/components/victory-screen/victory-screen.html` - Uppercase labels, tipografia display
- `src/app/components/victory-screen/victory-screen.css` - Overlay escuro rgba(0,0,0,0.85), surface-card, border 0
- `src/app/components/level-transition/level-transition.html` - Uppercase labels
- `src/app/components/level-transition/level-transition.css` - Overlay escuro, surface-card, border-radius 0
- `src/app/components/confirm-modal/confirm-modal.html` - Uppercase labels
- `src/app/components/confirm-modal/confirm-modal.css` - Overlay escuro, botoes outline, border-radius 0
- `src/app/components/simulator-frame/simulator-frame.css` - Border-radius 0, hairline border

## Decisoes Tecnicas

| Decisao | Opcao escolhida | Justificativa |
|---------|-----------------|---------------|
| Estrategia de migracao CSS | Substituicao direta no `:root` | Mudanca instantanea; todos os componentes que usam variaveis serao atualizados de uma vez. Componentes com hardcoded values serao corrigidos fase a fase. |
| Estilo de botao primario | BMW M outline (bg transparente/preto, texto branco, outline 1px branco, border-radius 0) | Consistente com o design system BMW M. O CTA "Jogar" perde o destaque colorido mas segue o principio editorial. |
| Simulador 3D (app-robo-simulator) | Fora de escopo | Componente de iframe com cores hardcoded; migracao interna seria arriscada e fora do escopo definido na business-spec. |
| Carregamento do top-nav | Eager (componente importado no app-root) | Nav deve aparecer em todas as rotas imediatamente; lazy loading adiciona complexidade sem beneficio. |
| Menu hamburger mobile | Dentro do app-top-nav | Autocontido; toggle de estado interno com Signal; overlay reutilizavel. |
| Faixa tricolor M | Classe CSS `.m-stripe` em styles.css | Implementada como gradiente linear de 4px com 3 paradas (#0066b1, #1c69d4, #e22718). Reutilizavel em qualquer lugar. |
| Tipografia BMW M | Substituir valores das variaveis existentes | Inter ja esta no projeto; ajustar pesos (body 300, display 700) e tracking (uppercase 1.5px) nas variaveis. display-lg+ com tracking -0.5px. |
| Border-radius | Atualizar variaveis e auditar componente a componente | `--rounded-md` de 14px para 6px, `--rounded-lg` de 20px para 0 (ou remover), etc. Depois auditar cada CSS. |

## Dependencias entre Fases

- **Fase 1** -> Fases 2, 3, 4, 5 (CSS vars globais e top-nav sao prereq para tudo)
- **Fase 2** -> Fase 5 (menu/leaderboard precisam de tipografia final)
- **Fase 3** -> Fase 5 (game/controls layouts precisam de tipografia final)
- **Fase 4** -> Fase 5 (componentes precisam de tipografia final)
- Fases 2, 3, 4 podem rodar em paralelo depois da Fase 1 (mas serao executadas sequencialmente)

## Mapa de Fases

| Fase | Descricao | Modulo Principal |
|------|-----------|-----------------|
| 01 | Fundacao: CSS Variables + Top-Nav Global | styles.css, app-top-nav (novo), app-root |
| 02 | Paginas Estaticas: Menu + Leaderboard | menu.page, leaderboard.page |
| 03 | Layouts de Jogo: Game + Controls | game.page, controls.page |
| 04 | Componentes: Chat, Controles Virtuais, Overlays | lbot-chat, virtual-controls, victory-screen, level-transition, confirm-modal |
| 05 | Tipografia Final + Auditoria Border-Radius + Polish | Todos os componentes |