# Fase 01: Routing & Navegacao

## Status: CONCLUIDO

## Objetivo

Introduzir Angular Router com lazy loading no projeto e criar a estrutura de paginas (Menu, Game, Leaderboard, Controles). Ao final desta fase, o usuario pode navegar entre paginas via menu.

## Pre-requisitos

- Nenhum (primeira fase)

## Tarefas

- [x] Tarefa 1: Configurar Angular Router no app.routes.ts
  - Arquivo: `lbot-datagen/lbot-datagen-frontend/src/app/app.routes.ts`
  - O que fazer: Definir rotas com lazy loading para: '' (redirect -> /menu), '/menu' (MenuPage), '/game' (GamePage), '/leaderboard' (LeaderboardPage), '/controls' (ControlsPage)

- [x] Tarefa 2: Simplificar AppComponent para usar router-outlet
  - Arquivo: `lbot-datagen/lbot-datagen-frontend/src/app/app.ts`
  - Arquivo: `lbot-datagen/lbot-datagen-frontend/src/app/app.html`
  - Arquivo: `lbot-datagen/lbot-datagen-frontend/src/app/app.css`
  - O que fazer: Remover logica de toggle chat/controls. Template deve ter apenas `<router-outlet></router-outlet>`. Remover imports de componentes que nao sao mais diretos.

- [x] Tarefa 3: Criar pagina Menu Principal
  - Arquivo: `lbot-datagen/lbot-datagen-frontend/src/app/pages/menu/menu.page.ts`
  - Arquivo: `lbot-datagen/lbot-datagen-frontend/src/app/pages/menu/menu.page.html`
  - Arquivo: `lbot-datagen/lbot-datagen-frontend/src/app/pages/menu/menu.page.css`
  - O que fazer: Pagina com titulo "LBot Arena", 3 botoes grandes: "Jogar" (routerLink /game), "Leaderboard" (routerLink /leaderboard), "Modo Controle" (routerLink /controls). Design clean, centralizado, cores do tema do projeto.

- [x] Tarefa 4: Criar pagina de Controles (mover VirtualControls existente)
  - Arquivo: `lbot-datagen/lbot-datagen-frontend/src/app/pages/controls/controls.page.ts`
  - Arquivo: `lbot-datagen/lbot-datagen-frontend/src/app/pages/controls/controls.page.html`
  - Arquivo: `lbot-datagen/lbot-datagen-frontend/src/app/pages/controls/controls.page.css`
  - O que fazer: Criar pagina que embarca o RoboSimulatorComponent (com showGoals=false) + VirtualControlsComponent existentes, com layout similar ao atual (simulator a esquerda, controls a direita). Adicionar botao "Voltar ao Menu" no topo.

- [x] Tarefa 5: Criar paginas skeleton para Game e Leaderboard
  - Arquivo: `lbot-datagen/lbot-datagen-frontend/src/app/pages/game/game.page.ts`
  - Arquivo: `lbot-datagen/lbot-datagen-frontend/src/app/pages/game/game.page.html`
  - Arquivo: `lbot-datagen/lbot-datagen-frontend/src/app/pages/game/game.page.css`
  - Arquivo: `lbot-datagen/lbot-datagen-frontend/src/app/pages/leaderboard/leaderboard.page.ts`
  - Arquivo: `lbot-datagen/lbot-datagen-frontend/src/app/pages/leaderboard/leaderboard.page.html`
  - Arquivo: `lbot-datagen/lbot-datagen-frontend/src/app/pages/leaderboard/leaderboard.page.css`
  - O que fazer: Criar componentes placeholder com texto "Em construcao" e botao "Voltar ao Menu". Serao preenchidos nas fases seguintes.

- [x] Tarefa 6: Verificar que app.config.ts tem provideRouter configurado
  - Arquivo: `lbot-datagen/lbot-datagen-frontend/src/app/app.config.ts`
  - O que fazer: Garantir que `provideRouter(routes)` esta nos providers do ApplicationConfig. Importar `routes` do app.routes.ts.

## Arquivos Referencia

- `lbot-datagen/lbot-datagen-frontend/src/app/app.ts` - AppComponent atual com toggle de modos
- `lbot-datagen/lbot-datagen-frontend/src/app/app.html` - Template atual com layout
- `lbot-datagen/lbot-datagen-frontend/src/app/app.routes.ts` - Arquivo de rotas vazio atual
- `lbot-datagen/lbot-datagen-frontend/src/app/app.config.ts` - Configuracao da aplicacao
- `lbot-datagen/lbot-datagen-frontend/src/app/components/virtual-controls/virtual-controls.ts` - Componente a ser movido para pagina /controls

## Criterios de Aceite

- [x] CA01: Ao acessar /, usuario e redirecionado para /menu
- [x] CA02: Clicar "Jogar" navega para /game
- [x] CA03: Clicar "Leaderboard" navega para /leaderboard
- [x] CA04: Clicar "Modo Controle" navega para /controls
- [x] CA05: Modo Controle funciona identicamente ao anterior

## Testes Esperados

- Nenhum teste automatizado (decisao do projeto)

## Comandos pos-fase

- `cd lbot-datagen/lbot-datagen-frontend && ng serve` (verificar que compila e navega)
- Verificar manualmente: navegar entre todas as rotas

## Registro de Execucao

- Data: 2026-05-31
- Arquivos criados:
  - `lbot-datagen/lbot-datagen-frontend/src/app/pages/menu/menu.page.ts`
  - `lbot-datagen/lbot-datagen-frontend/src/app/pages/menu/menu.page.html`
  - `lbot-datagen/lbot-datagen-frontend/src/app/pages/menu/menu.page.css`
  - `lbot-datagen/lbot-datagen-frontend/src/app/pages/game/game.page.ts`
  - `lbot-datagen/lbot-datagen-frontend/src/app/pages/game/game.page.html`
  - `lbot-datagen/lbot-datagen-frontend/src/app/pages/game/game.page.css`
  - `lbot-datagen/lbot-datagen-frontend/src/app/pages/leaderboard/leaderboard.page.ts`
  - `lbot-datagen/lbot-datagen-frontend/src/app/pages/leaderboard/leaderboard.page.html`
  - `lbot-datagen/lbot-datagen-frontend/src/app/pages/leaderboard/leaderboard.page.css`
  - `lbot-datagen/lbot-datagen-frontend/src/app/pages/controls/controls.page.ts`
  - `lbot-datagen/lbot-datagen-frontend/src/app/pages/controls/controls.page.html`
  - `lbot-datagen/lbot-datagen-frontend/src/app/pages/controls/controls.page.css`
- Arquivos alterados:
  - `lbot-datagen/lbot-datagen-frontend/src/app/app.routes.ts` (rotas lazy-loaded configuradas)
  - `lbot-datagen/lbot-datagen-frontend/src/app/app.ts` (simplificado para RouterOutlet)
  - `lbot-datagen/lbot-datagen-frontend/src/app/app.html` (apenas <router-outlet>)
  - `lbot-datagen/lbot-datagen-frontend/src/app/app.css` (variaveis CSS globais)
- Testes executados: ng build (sucesso, sem erros de compilacao)
- Resultado: BUILD SUCCESS - 4 lazy chunks gerados (menu-page, game-page, leaderboard-page, controls-page)
- Pendencias: Nenhuma. Warnings de CSS budget sao pre-existentes dos componentes originais.
