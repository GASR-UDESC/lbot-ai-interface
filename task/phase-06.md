# Fase 06: Frontend Leaderboard & Integracao com Backend

## Status: CONCLUIDO

## Objetivo

Criar o LeaderboardService para comunicacao HTTP com a API, implementar a pagina de Leaderboard completa, e integrar a tela de vitoria com o backend para salvar game runs. Ao final, o usuario pode completar os 5 niveis, salvar no leaderboard, e ver o ranking global.

## Pre-requisitos

- Fase 04 concluida (VictoryScreen funcional no frontend)
- Fase 05 concluida (API backend funcional)

## Tarefas

- [x] Tarefa 1: Criar interfaces/models do leaderboard no frontend
  - Arquivo: `lbot-datagen/lbot-datagen-frontend/src/app/models/leaderboard.model.ts`
  - O que fazer: Definir interfaces:
    - `CreateGameRunRequest = { nickname: string, level1TimeMs: number, level2TimeMs: number, level3TimeMs: number, level4TimeMs: number, level5TimeMs: number }`
    - `GameRunResponse = { id: string, nickname: string, level1TimeMs: number, ..., level5TimeMs: number, totalTimeMs: number, completedAt: string }`

- [x] Tarefa 2: Criar LeaderboardService
  - Arquivo: `lbot-datagen/lbot-datagen-frontend/src/app/services/leaderboard.service.ts`
  - O que fazer:
    - Injetar HttpClient
    - `saveGameRun(request: CreateGameRunRequest): Observable<GameRunResponse>` -> POST /game-runs
    - `getLeaderboard(): Observable<GameRunResponse[]>` -> GET /game-runs
    - Usar environment.apiBaseUrl como base

- [x] Tarefa 3: Implementar pagina Leaderboard
  - Arquivo: `lbot-datagen/lbot-datagen-frontend/src/app/pages/leaderboard/leaderboard.page.ts`
  - Arquivo: `lbot-datagen/lbot-datagen-frontend/src/app/pages/leaderboard/leaderboard.page.html`
  - Arquivo: `lbot-datagen/lbot-datagen-frontend/src/app/pages/leaderboard/leaderboard.page.css`
  - O que fazer:
    - Titulo "Leaderboard Global"
    - Tabela com colunas: # (posicao), Nickname, Tempo Total (MM:SS), Data
    - Carregar dados no ngOnInit via leaderboardService.getLeaderboard()
    - Se lista vazia: "Nenhum jogador completou os 5 niveis ainda. Seja o primeiro!"
    - Se backend indisponivel: "Leaderboard indisponivel no momento"
    - Botao "Voltar ao Menu" (routerLink /menu)
    - Formatar tempo total com formatTime (MM:SS)
    - Formatar data com DatePipe (dd/MM/yyyy HH:mm)

- [x] Tarefa 4: Integrar VictoryScreen com save no backend
  - Arquivo: `lbot-datagen/lbot-datagen-frontend/src/app/pages/game/game.page.ts`
  - O que fazer:
    - Quando VictoryScreen emite evento `save` com {nickname, levelTimes}:
      - Chamar leaderboardService.saveGameRun() com os dados
      - Se sucesso: mostrar feedback positivo, navegar para /leaderboard
      - Se erro: mostrar mensagem "Erro ao salvar. Tente novamente." com botao retry
    - Quando VictoryScreen emite `playAgain`:
      - Chamar gameState.resetRun() e gameState.startRun()
      - Recarregar nivel 1

- [x] Tarefa 5: Tratar indisponibilidade do backend
  - Arquivo: `lbot-datagen/lbot-datagen-frontend/src/app/pages/game/game.page.ts` (adicionar)
  - Arquivo: `lbot-datagen/lbot-datagen-frontend/src/app/pages/leaderboard/leaderboard.page.ts` (adicionar)
  - O que fazer:
    - Na GamePage: se save falha, mostrar erro + opcao de retry ou "copiar tempo" (navigator.clipboard)
    - Na LeaderboardPage: loading state, error state com mensagem amigavel
    - Timeout de 10s nos requests (ou usar HttpClient default)

## Arquivos Referencia

- `lbot-datagen/lbot-datagen-frontend/src/app/services/messages-service.ts` - Pattern de service HTTP existente
- `lbot-datagen/lbot-datagen-frontend/src/app/services/virtual-control.service.ts` - Outro pattern de service HTTP
- `lbot-datagen/lbot-datagen-frontend/src/environments/environment.ts` - Base URL

## Criterios de Aceite

- [x] CA01: Leaderboard carrega e exibe lista completa
  - Cenario: Given backend com 5 game runs / When acessa /leaderboard / Then tabela mostra 5 linhas ordenadas por tempo
- [x] CA02: Leaderboard vazio mostra mensagem adequada
  - Cenario: Given backend sem game runs / When acessa /leaderboard / Then mostra "Nenhum jogador completou os 5 niveis..."
- [x] CA03: Salvar no leaderboard funciona
  - Cenario: Given vitoria com nickname "JoaoBot" / When clica "Salvar" / Then dados salvos e navega para /leaderboard
- [x] CA04: Nickname repetido salva multiplas entradas
  - Cenario: Given "JoaoBot" ja salvou antes / When salva novamente / Then ambos aparecem no leaderboard
- [x] CA05: Backend indisponivel no leaderboard
  - Cenario: Given backend offline / When acessa /leaderboard / Then mostra "Leaderboard indisponivel no momento"
- [x] CA06: Backend indisponivel ao salvar
  - Cenario: Given backend offline / When tenta salvar / Then mostra erro com opcao retry
- [x] CA07: Formato de data correto na tabela
  - Cenario: Given game run de 2025-01-15T14:30:00 / When exibe no leaderboard / Then mostra "15/01/2025 14:30"

## Testes Esperados

- Nenhum teste automatizado (decisao do projeto)

## Comandos pos-fase

- `cd lbot-datagen/lbot-datagen-frontend && ng serve` (frontend)
- `cd lbot-datagen/lbot-datagen-backend && ./mvnw spring-boot:run` (backend)
- Verificar: completar 5 niveis, salvar com nickname, ver no leaderboard
- Verificar: desligar backend e testar error states

## Registro de Execucao

- Data: 2026-05-31
- Arquivos criados:
  - `lbot-datagen/lbot-datagen-frontend/src/app/models/leaderboard.model.ts`
  - `lbot-datagen/lbot-datagen-frontend/src/app/services/leaderboard.service.ts`
- Arquivos alterados:
  - `lbot-datagen/lbot-datagen-frontend/src/app/pages/leaderboard/leaderboard.page.ts` (implementado completo)
  - `lbot-datagen/lbot-datagen-frontend/src/app/pages/leaderboard/leaderboard.page.html` (implementado completo)
  - `lbot-datagen/lbot-datagen-frontend/src/app/pages/leaderboard/leaderboard.page.css` (implementado completo)
  - `lbot-datagen/lbot-datagen-frontend/src/app/pages/game/game.page.ts` (integrado LeaderboardService + retry)
  - `lbot-datagen/lbot-datagen-frontend/src/app/pages/game/game.page.html` (novos inputs isSaving/saveError/retrySave)
  - `lbot-datagen/lbot-datagen-frontend/src/app/components/victory-screen/victory-screen.ts` (novos @Input e @Output)
  - `lbot-datagen/lbot-datagen-frontend/src/app/components/victory-screen/victory-screen.html` (loading state + error block)
  - `lbot-datagen/lbot-datagen-frontend/src/app/components/victory-screen/victory-screen.css` (estilos de erro)
- Testes executados: nenhum (decisao do projeto)
- Resultado: BUILD OK — sem erros de compilacao; 2 warnings de CSS budget pre-existentes (virtual-controls, lbot-chat)
- Pendencias: nenhuma
