# Fase 01: Fundamentos - Tokens CSS, TopNav e Layout Base

## Status: CONCLUIDO

## Objetivo

Entregar a base visual e estrutural da migracao: definir todas as variaveis CSS do design Coinbase, criar o componente TopNav, reestruturar o layout principal (App.tsx) com grid 2 colunas e sidebar/canvas, e carregar a fonte Inter via Google Fonts.

## Pre-requisitos

- Nenhum (primeira fase).

## Tarefas

- [x] Tarefa 1: Adicionar link Google Fonts Inter no index.html
  - Arquivo: `lbot-simulator-web/index.html`
  - O que fazer: Adicionar `<link rel="preconnect" href="https://fonts.googleapis.com">`, `<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>`, e `<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">` dentro do `<head>`.

- [x] Tarefa 2: Reescrever :root e variaveis CSS em styles.css
  - Arquivo: `lbot-simulator-web/src/styles.css`
  - O que fazer: Substituir o :root existente pelas variaveis do design Coinbase (cores, espacamento, bordas, sombras, tipografia). Remover `color-scheme: dark`. Definir body com `background: var(--color-canvas)` e `color: var(--color-ink)`. Manter `box-sizing: border-box` e estilos base para `button`, `textarea`, `code`.

- [x] Tarefa 3: Criar componente TopNav
  - Arquivo: `lbot-simulator-web/src/components/TopNav.tsx`
  - O que fazer: Criar componente funcional que renderiza a barra de navegacao de 64px, background branco, texto escuro, titulo "LBot Simulator Web" a esquerda, callout HTTP simplificado (ou texto/link) a direita, borda inferior 1px solid var(--color-hairline). Exportar como `TopNav`.

- [x] Tarefa 4: Reestruturar App.tsx com novo layout
  - Arquivo: `lbot-simulator-web/src/App.tsx`
  - O que fazer: Substituir o `<header className="hero">` atual pelo `<TopNav />`. Envolver o layout em um container com `max-width: 1200px` centralizado. Abaixo do TopNav, renderizar `<main className="layout-grid">` com as duas colunas (sidebar e canvas). A sidebar deve conter os cards empilhados. Manter todas as props e callbacks dos componentes.

- [x] Tarefa 5: Adicionar estilos base do layout e top-nav em styles.css
  - Arquivo: `lbot-simulator-web/src/styles.css`
  - O que fazer: Adicionar/ajustar classes `.top-nav`, `.app-shell`, `.layout-grid`, `.left-column`, `.canvas-column`, `.content-wrapper` (max-width). Remover classes `.hero`, `.eyebrow`, `.hero-copy`, `.hero-callout` (ou adaptar para o novo contexto).

## Arquivos Referencia

- `lbot-simulator-web/src/App.tsx` - Estrutura atual do layout e componentes.
- `lbot-simulator-web/src/styles.css` - Estilos atuais que serao sobrescritos.
- `lbot-simulator-web/index.html` - Estrutura HTML para adicionar fonte.
- `task/business-spec.md` - RF01, RF02, RF05, RF09 (tokens e layout).

## Criterios de Aceite

- [x] CA01: A pagina carrega com fundo branco (#ffffff) e fonte Inter aplicada.
- [x] CA02: O TopNav de 64px esta presente com titulo "LBot Simulator Web" e borda inferior #dee1e6.
- [x] CA10: O layout usa grid de 2 colunas em desktop (sidebar + canvas).
- [x] CA01 (parcial): Variaveis CSS Coinbase estao definidas em :root e usadas nos estilos base.

## Testes Esperados

- `npm run build` deve passar sem erros de TypeScript.
- `npm run dev` deve renderizar a pagina com o novo layout visivel.

## Comandos pos-fase

- `npm run check`
- `npm run build`

## Registro de Execucao

- Data: 2026-06-15
- Arquivos criados:
  - `lbot-simulator-web/src/components/TopNav.tsx`
- Arquivos alterados:
  - `lbot-simulator-web/index.html` (adicionado link Google Fonts Inter)
  - `lbot-simulator-web/src/styles.css` (reescrita completa: variaveis Coinbase, remocao hero, adicao top-nav e content-wrapper)
  - `lbot-simulator-web/src/App.tsx` (substituido hero por TopNav, removido useMemo, ajustado layout)
- Testes executados:
  - `npm run check`: sucesso (0 erros TypeScript)
  - `npm run build`: sucesso (vite build concluido)
- Resultado: Fase 01 concluida com sucesso. Build passa sem erros.
- Pendencias: Nenhuma.
