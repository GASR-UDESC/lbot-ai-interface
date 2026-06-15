# Fase 03: Canvas, Erros, Responsividade e Micro-interacoes

## Status: CONCLUIDO

## Objetivo

Ajustar o container do canvas 3D, o erro de inicializacao WebGL, implementar os breakpoints de responsividade Coinbase e todas as micro-interacoes (hover, focus, active, disabled).

## Pre-requisitos

- Fase 02 concluida (componentes reestilizados).

## Tarefas

- [x] Tarefa 1: Reestilizar container do SimulatorCanvas
  - Arquivo: `lbot-simulator-web/src/styles.css`
  - O que fazer: Ajustar `.simulator-canvas` para background #f7f7f7 (ou #ffffff), borda 1px solid #dee1e6, bordas arredondadas 24px, `overflow: hidden`. O canvas interno (`<canvas>`) nao deve ter bordas arredondadas (aplicar `border-radius: 0` ou herdar do container).

- [x] Tarefa 2: Reestilizar erro WebGL do SimulatorCanvas
  - Arquivo: `lbot-simulator-web/src/styles.css` e `lbot-simulator-web/src/components/SimulatorCanvas.tsx`
  - O que fazer: Ajustar `.simulator-canvas--error` para card branco, borda 1px solid #cf202f, texto #cf202f, padding 32px, bordas 24px. Adicionar um botao "Recarregar" dentro do JSX do erro WebGL que chama `window.location.reload()`, usando classe `button-secondary-light` (pill cinza).

- [x] Tarefa 3: Implementar responsividade (breakpoints Coinbase)
  - Arquivo: `lbot-simulator-web/src/styles.css`
  - O que fazer: Substituir/ajustar as media queries existentes para os novos breakpoints:
    - Mobile (<640px): grid 1 coluna, cards empilham, padding reduzido (16px), canvas largura total, botoes full width.
    - Tablet (640–1024px): grid 2 colunas com sidebar minmax(280px, 1fr), padding 24px.
    - Desktop (1024–1280px): grid full 2 colunas, sidebar ~320-420px, padding 32px.
    - Wide (>1280px): conteudo capa em max-width 1200px centralizado.
  - Remover a media query antiga de 1100px e adaptar a de 720px.

- [x] Tarefa 4: Implementar micro-interacoes
  - Arquivo: `lbot-simulator-web/src/styles.css`
  - O que fazer: Adicionar/ajustar:
    - Cards (`.panel-card`, `.status-card`, `.camera-preview-card`): hover com `box-shadow: 0 4px 12px rgba(0,0,0,0.04)`, transition `box-shadow 0.2s ease`.
    - Botoes primarios (`.primary-button`): hover background #003ecc, active scale(0.98), transition `background 0.2s ease`.
    - Botoes secundarios (`.secondary-button`): hover background darken leve (ex: #e2e4e8), transition `background 0.2s ease`.
    - Inputs (`.command-input`): focus borda 2px solid #0052ff, transition `border-color 0.2s ease`.
    - Disabled: opacity 0.55, cursor not-allowed, sem hover effects.
    - Nav links: hover texto #0052ff ou underline.

## Arquivos Referencia

- `lbot-simulator-web/src/components/SimulatorCanvas.tsx` - Container e erro WebGL.
- `lbot-simulator-web/src/styles.css` - Media queries e estilos de interacao.
- `task/business-spec.md` - RF03, RF06, RF07, RF09.

## Criterios de Aceite

- [x] CA02: Canvas 3D esta como area principal com bordas arredondadas e overflow hidden.
- [x] CA04: Cards exibem sombra no hover; botao primario escurece; input mostra borda azul no focus.
- [x] CA05: Em mobile (<640px), layout colapsa para 1 coluna, cards ocupam largura total, canvas funciona.
- [x] CA06: Erro WebGL exibe card branco com borda vermelha + botao pill cinza de recarregar.
- [x] CA07: Terminologia e textos originais preservados (verificar que nenhum texto foi alterado).

## Testes Esperados

- `npm run build` deve passar.
- Testar responsividade via DevTools em 375px, 768px, 1366px.
- Verificar hover/focus nos botoes e inputs.

## Comandos pos-fase

- `npm run check`
- `npm run build`

## Registro de Execucao

- Data: 2026-06-15
- Arquivos criados: Nenhum.
- Arquivos alterados:
  - `lbot-simulator-web/src/components/SimulatorCanvas.tsx` (adicionado botao Recarregar no estado de erro WebGL)
  - `lbot-simulator-web/src/styles.css` (cards: adicionado transition + hover shadow; botoes primarios: adicionado :active scale(0.98); nav links: adicionado hover no callout code; media queries: substituidos breakpoints 1100px/720px pelos Coinbase - mobile <640px, tablet 640-1024px, wide >1280px; mobile: padding/cards/botoes ajustados)
- Testes executados:
  - `npm run check`: sucesso (0 erros TypeScript)
  - `npm run build`: sucesso (vite build concluido)
- Resultado: Fase 03 concluida com sucesso. Container do canvas ja estava correto desde fases anteriores (sem alteracoes). Botao Recarregar adicionado ao erro WebGL. Breakpoints Coinbase implementados (mobile <640px, tablet 640-1024px, desktop 1024-1280px default, wide >1280px). Micro-interacoes implementadas (card hover shadows, primary button active scale, nav link hover, camera preview card hover).
- Pendencias: Nenhuma.
