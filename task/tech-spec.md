# Plano Tecnico: Sistema de Niveis Gamificado com Leaderboard

## Visao Geral

Transformar o frontend Angular monolitico (sem routing, single-page com toggle) em uma aplicacao multi-pagina com sistema de 5 niveis tematicos, timer, progressao, e leaderboard persistido no backend Spring Boot.

**Abordagem tecnica:**
- Angular Router com lazy loading para separar paginas (Menu, Game, Leaderboard, Controles)
- Angular Signals para gerenciamento de estado do jogo (nivel, timer, progresso)
- TypeScript const com interface tipada para configuracao dos 5 niveis
- Refatoracao do ArenaBuilderService para aceitar configuracao de nivel (obstaculos reposicionados + reskin)
- Nova entidade JPA no backend para persistir game runs (leaderboard)
- Pontos A e B fixos e identicos em todos os niveis (dificuldade vem dos obstaculos)
- Um unico chat (chatId) por run completo (5 niveis)

## Modulos Envolvidos

- **Angular Router**: Criacao de rotas lazy-loaded (/menu, /game, /leaderboard, /controls)
- **GameStateService**: Novo service com Signals para gerenciar estado do run (nivel atual, timers, progresso)
- **LevelConfigService**: Novo service + const para carregar configuracoes dos 5 niveis
- **ArenaBuilderService**: Refatoracao para aceitar LevelConfig (posicoes de obstaculos + materiais tematicos)
- **RoboSimulatorComponent**: Adaptacao para receber nivel como Input e reagir a mudancas de nivel
- **LbotChat**: Adaptacao para modo gamificado (chat unico por run, sem controles virtuais)
- **Backend (Spring Boot)**: Nova entidade GameRun + Controller + Service para leaderboard
- **Novos componentes**: MenuPage, GamePage, LeaderboardPage, ControlsPage, LevelTransition, VictoryScreen, ConfirmModal

## Arquivos Impactados

### Novos (Frontend)
- `src/app/app.routes.ts` - Configuracao de rotas lazy-loaded (reescrita)
- `src/app/pages/menu/menu.page.ts` - Componente da pagina de menu principal
- `src/app/pages/menu/menu.page.html` - Template do menu
- `src/app/pages/menu/menu.page.css` - Estilos do menu
- `src/app/pages/game/game.page.ts` - Pagina do jogo (orquestra simulator + chat + HUD)
- `src/app/pages/game/game.page.html` - Template do jogo
- `src/app/pages/game/game.page.css` - Estilos do jogo
- `src/app/pages/leaderboard/leaderboard.page.ts` - Pagina do leaderboard
- `src/app/pages/leaderboard/leaderboard.page.html` - Template do leaderboard
- `src/app/pages/leaderboard/leaderboard.page.css` - Estilos do leaderboard
- `src/app/pages/controls/controls.page.ts` - Pagina do modo controle
- `src/app/pages/controls/controls.page.html` - Template do controle
- `src/app/pages/controls/controls.page.css` - Estilos do controle
- `src/app/components/level-transition/level-transition.ts` - Tela de transicao entre niveis
- `src/app/components/level-transition/level-transition.html` - Template transicao
- `src/app/components/level-transition/level-transition.css` - Estilos transicao
- `src/app/components/victory-screen/victory-screen.ts` - Tela de vitoria final
- `src/app/components/victory-screen/victory-screen.html` - Template vitoria
- `src/app/components/victory-screen/victory-screen.css` - Estilos vitoria
- `src/app/components/confirm-modal/confirm-modal.ts` - Modal de confirmacao reutilizavel
- `src/app/components/confirm-modal/confirm-modal.html` - Template modal
- `src/app/components/confirm-modal/confirm-modal.css` - Estilos modal
- `src/app/services/game-state.service.ts` - Gerenciamento de estado do jogo com Signals
- `src/app/services/level-config.service.ts` - Carregamento de configuracoes de nivel
- `src/app/services/leaderboard.service.ts` - HTTP calls para API do leaderboard
- `src/app/models/level-config.model.ts` - Interface LevelConfig e definicao dos 5 niveis
- `src/app/models/game-state.model.ts` - Interfaces do estado do jogo (RunState, LevelState)
- `src/app/models/leaderboard.model.ts` - Interfaces do leaderboard (GameRunDto, CreateGameRunRequest)

### Novos (Backend)
- `src/main/java/com/.../entity/GameRun.java` - Entidade JPA para game runs
- `src/main/java/com/.../repository/GameRunRepository.java` - Repository com query ordenada
- `src/main/java/com/.../service/GameRunService.java` - Service layer
- `src/main/java/com/.../controller/GameRunController.java` - REST controller
- `src/main/java/com/.../dto/CreateGameRunRequest.java` - DTO de criacao
- `src/main/java/com/.../dto/GameRunResponse.java` - DTO de resposta

### Alterados (Frontend)
- `src/app/app.ts` - Simplificado (apenas <router-outlet>)
- `src/app/app.html` - Simplificado (apenas <router-outlet>)
- `src/app/app.css` - Estilos globais minimos
- `src/app/services/arena-builder.service.ts` - Refatorado para aceitar LevelConfig
- `src/app/components/robo-simulator/robo-simulator.ts` - Aceita nivel como Input, remove geracao aleatoria
- `src/app/components/robo-simulator/robo-simulator.css` - Ajustes de layout
- `src/app/components/lbot-chat/lbot-chat.ts` - Modo gamificado (recebe chatId externo, nao cria proprio)

### Alterados (Backend)
- Nenhuma alteracao em arquivos existentes necessaria (apenas adicoes)

## Decisoes Tecnicas

| Decisao | Opcao escolhida | Justificativa |
|---------|-----------------|---------------|
| Routing | Lazy loading com rotas | Melhor performance, separacao clara de paginas, lazy loading reduz bundle inicial |
| State management | Angular Signals | Nativo do Angular 20, reativo sem overhead, moderno, sem dependencias externas |
| Level config | TypeScript const tipada | Type-safety, IDE support, facil manutenção, nao precisa de HTTP para carregar |
| Theming | Obstaculos reposicionados + reskin | Maior variedade visual e de gameplay entre niveis |
| Backend leaderboard | Seguir pattern (ddl-auto=update) | Consistencia com codebase existente, sem necessidade de migration tool |
| Testes | Sem testes (manter padrao) | Projeto tem cobertura minima, nao introduzir complexidade |
| Chat no jogo | Um chat por run inteiro | Mais simples, contexto preservado entre niveis, melhor dados de treino |
| CSS | Puro (sem framework) | Consistencia com codebase, sem dependencias novas |
| Pontos A/B | Fixos e iguais em todos niveis | Simplifica comparacao de performance no leaderboard, dificuldade vem dos obstaculos |
| Timer formato | MM:SS | Mais legivel e limpo na UI |
| Data leaderboard | Gerada no backend | Mais confiavel, evita manipulacao client-side |

## Dependencias entre Fases

```
Fase 01 (Routing) -> Fase 02 (Levels) -> Fase 03 (Game State)
                                                    |
Fase 04 (Game UI) depende de Fase 01 + Fase 03     |
                                                    v
Fase 05 (Backend) -> Fase 06 (Leaderboard Frontend + Integracao)
                                                    |
Fase 07 (Chat + Data) depende de Fase 03 + Fase 04 v
```

- Fase 01 -> Fase 02 (precisa das rotas para navegar entre paginas)
- Fase 02 -> Fase 03 (precisa da config de niveis para o state machine)
- Fase 03 -> Fase 04 (precisa do game state para as telas de UI)
- Fase 01 -> Fase 04 (precisa das rotas para as paginas de game UI)
- Fase 05 -> Fase 06 (precisa da API do backend para integrar no frontend)
- Fase 03 + Fase 04 -> Fase 07 (precisa do jogo funcional para integrar o chat)

## Mapa de Fases

| Fase | Descricao | Modulo |
|------|-----------|--------|
| 01 | Routing & Navegacao - Criar estrutura de rotas e paginas skeleton | Angular Router, Pages |
| 02 | Sistema de Niveis - Config dos 5 niveis + refatoracao do ArenaBuilder | LevelConfig, ArenaBuilder |
| 03 | Game State & Timer - Service com Signals, timer, progressao | GameStateService |
| 04 | Game UI - Telas de transicao, vitoria, modal, HUD | Components UI |
| 05 | Backend Leaderboard - Entidade, API REST, persistencia | Spring Boot |
| 06 | Frontend Leaderboard & Integracao - Pagina + conexao com backend | LeaderboardService, Pages |
| 07 | Chat & Geracao de Dados - Integrar chat no modo jogo, ratings | LbotChat, GamePage |
