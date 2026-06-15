# Fase 01: Renomeacao e Textos da UI

## Status: CONCLUIDO

## Objetivo

Renomear os 5 niveis para "Nivel 1".."Nivel 5" e atualizar todos os textos exibidos na UI que referenciam os nomes tematicos antigos. Esta fase nao altera o level design ou a fisica, apenas os labels.

## Pre-requisitos

- Nenhum (fase inicial).

## Tarefas

- [x] Tarefa 1: Renomear niveis em `level-config.model.ts`
  - Arquivo: `1.coleta-de-dados/lbot-datagen/lbot-datagen-frontend/src/app/models/level-config.model.ts`
  - Alterar `name` de cada nivel:
    - Nivel 1: "Campo de Treino" -> "Nivel 1"
    - Nivel 2: "Escritorio Central" -> "Nivel 2"
    - Nivel 3: "Cidade em Obras" -> "Nivel 3"
    - Nivel 4: "Floresta Misteriosa" -> "Nivel 4"
    - Nivel 5: "Complexo Industrial" -> "Nivel 5"
  - Atualizar tambem os comentarios de secao (ex: `// Level 1 — Campo de Treino` -> `// Level 1 — Nivel 1`)

- [x] Tarefa 2: Atualizar subtitulo do menu
  - Arquivo: `1.coleta-de-dados/lbot-datagen/lbot-datagen-frontend/src/app/pages/menu/menu.page.html`
  - Alterar linha: `<span class="btn-desc">5 niveis com temas e dificuldade progressiva</span>` -> `<span class="btn-desc">5 niveis com dificuldade progressiva</span>`

- [x] Tarefa 3: Remover coluna "Nome" do victory-screen
  - Arquivo: `1.coleta-de-dados/lbot-datagen/lbot-datagen-frontend/src/app/components/victory-screen/victory-screen.html`
  - Remover o header `<span>Nome</span>` da linha `.times-header`
  - Remover o `<span class="level-name-cell">` da linha do loop `*ngFor`
  - Ajustar estilos CSS (`victory-screen.css`) se necessario para acomodar 2 colunas em vez de 3

- [x] Tarefa 4: Verificar level-transition
  - Arquivo: `1.coleta-de-dados/lbot-datagen/lbot-datagen-frontend/src/app/components/level-transition/level-transition.html`
  - Confirmar que o texto `{{ levelName }} Completo!` funcionara com os novos nomes (ex: "Nivel 1 Completo!"). Nenhuma alteracao necessaria.

- [x] Tarefa 5: Verificar lbot-chat
  - Arquivo: `1.coleta-de-dados/lbot-datagen/lbot-datagen-frontend/src/app/components/lbot-chat/lbot-chat.ts`
  - Confirmar que o banner `— Nivel: ${levelName} —` funcionara com os novos nomes. Nenhuma alteracao necessaria.

- [x] Tarefa 6: Verificar game.page.html
  - Arquivo: `1.coleta-de-dados/lbot-datagen/lbot-datagen-frontend/src/app/pages/game/game.page.html`
  - Confirmar que `{{ currentLevelConfig()?.name }}` no HUD exibira "Nivel 1" corretamente. Nenhuma alteracao necessaria.

## Arquivos Referencia

- `1.coleta-de-dados/lbot-datagen/lbot-datagen-frontend/src/app/models/level-config.model.ts` - Estrutura dos niveis e nomes atuais
- `1.coleta-de-dados/lbot-datagen/lbot-datagen-frontend/src/app/components/victory-screen/victory-screen.html` - Layout atual da tabela
- `1.coleta-de-dados/lbot-datagen/lbot-datagen-frontend/src/app/components/victory-screen/victory-screen.css` - Estilos da tabela

## Criterios de Aceite

- [x] CA01: Os 5 niveis exibem "Nivel 1" a "Nivel 5" em todos os pontos de exibicao
  - Cenario: Dado que o jogador acessa o menu, HUD, tela de transicao, tela de vitoria ou chat
  - Entao: todos os nomes exibidos sao "Nivel X", sem nenhum nome tematico antigo
- [x] CA02: A tabela de tempos no victory-screen tem apenas 2 colunas (Nivel e Tempo)
  - Cenario: Dado que o jogador completa todos os niveis e ve a tela de vitoria
  - Entao: a tabela exibe apenas "Nivel" e "Tempo", sem coluna "Nome"

## Testes Esperados

- `npm run build` deve compilar sem erros
- `ng test` (Karma) deve passar (se rodar em ambiente com Chrome)

## Comandos pos-fase

```bash
cd 1.coleta-de-dados/lbot-datagen/lbot-datagen-frontend
npm run build
```

## Registro de Execucao

- Data: 2026-06-15
- Arquivos criados: Nenhum
- Arquivos alterados:
  - `1.coleta-de-dados/lbot-datagen/lbot-datagen-frontend/src/app/models/level-config.model.ts` (nomes, comentarios)
  - `1.coleta-de-dados/lbot-datagen/lbot-datagen-frontend/src/app/pages/menu/menu.page.html` (subtitulo)
  - `1.coleta-de-dados/lbot-datagen/lbot-datagen-frontend/src/app/components/victory-screen/victory-screen.html` (remover coluna Nome)
  - `1.coleta-de-dados/lbot-datagen/lbot-datagen-frontend/src/app/components/victory-screen/victory-screen.css` (grid 2 colunas)
- Testes executados: `npm run build` (sucesso, exit code 0)
- Resultado: Build compilou sem erros. Todos os 5 niveis renomeados para "Nivel 1".."Nivel 5". Subtitulo do menu atualizado. Coluna Nome removida do victory-screen. level-transition, lbot-chat e game.page.html verificados - sem alteracoes necessarias (usam bindings que consomem o `name` do config).
- Pendencias: Nenhuma
