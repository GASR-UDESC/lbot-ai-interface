# Fase 02: Componentes - Reestilizacao de Paineis

## Status: CONCLUIDO

## Objetivo

Reestilizar todos os componentes de painel (StatusPanel, CommandPanel, CameraPreview, History) e o ErrorBoundary com os tokens e estilos do design Coinbase. A estrutura HTML dos componentes pode permanecer a mesma; a mudanca e principalmente em classes CSS.

## Pre-requisitos

- Fase 01 concluida (variaveis CSS, layout base, TopNav).

## Tarefas

- [x] Tarefa 1: Reestilizar StatusPanel
  - Arquivo: `lbot-simulator-web/src/styles.css`
  - O que fazer: Ajustar `.status-card` para background #ffffff, borda 1px solid #dee1e6, bordas 24px, padding 20px. Ajustar `.badge--connected` para verde (#05b169) com background suave (surface-soft). Ajustar `.badge--disconnected` para vermelho (#cf202f) com background suave. Ajustar `.status-row` para background #f7f7f7, bordas 16px. Ajustar `.status-message--idle`, `.status-message--info`, `.status-message--error` para manter cores semanticas mas com background suave e sem glassmorphism.

- [x] Tarefa 2: Reestilizar CommandPanel
  - Arquivo: `lbot-simulator-web/src/styles.css`
  - O que fazer: Ajustar `.panel-card` para background #ffffff, borda 1px solid #dee1e6, bordas 24px. Ajustar `.command-input` para background #ffffff, borda #dee1e6, bordas 12px, focus state com borda 2px solid #0052ff. Ajustar `.primary-button` para background #0052ff, texto branco, border-radius 100px (pill). Ajustar `.secondary-button` para background #eef0f3, texto #0a0b0d, border-radius 100px. Ajustar `.primary-button:disabled` para usar #a8b8cc (color-primary-disabled). Ajustar `.history-list li` para background #f7f7f7, fonte mono, bordas arredondadas.

- [x] Tarefa 3: Reestilizar CameraPreview
  - Arquivo: `lbot-simulator-web/src/styles.css`
  - O que fazer: Ajustar `.camera-preview-card` para background #16181c (product-ui-card-dark), texto branco, bordas 24px, padding 32px. Ajustar `.camera-preview-frame` para manter aspect-ratio 4/3 e bordas arredondadas. Ajustar `.camera-preview-placeholder` para texto branco/cinza claro.

- [x] Tarefa 4: Reestilizar ErrorBoundary
  - Arquivo: `lbot-simulator-web/src/styles.css`
  - O que fazer: Ajustar `.error-boundary` para card branco (#ffffff), borda 1px solid #cf202f, texto #cf202f, padding 32px, bordas 24px. Ajustar o botao de retry para usar estilo `button-secondary-light` (pill cinza #eef0f3, texto #0a0b0d).

## Arquivos Referencia

- `lbot-simulator-web/src/components/StatusPanel.tsx` - Estrutura atual do painel de status.
- `lbot-simulator-web/src/components/CommandPanel.tsx` - Estrutura atual do painel de comandos.
- `lbot-simulator-web/src/components/CameraPreview.tsx` - Estrutura atual do preview.
- `lbot-simulator-web/src/components/ErrorBoundary.tsx` - Estrutura atual do error boundary.
- `task/business-spec.md` - RF03, RF04, RF06, RF08, RF09.

## Criterios de Aceite

- [x] CA03: StatusPanel tem rows com background #f7f7f7 e bordas arredondadas; badge conectado/disconectado com cores semanticas.
- [x] CA03: CommandPanel tem input com borda #dee1e6 e focus azul #0052ff; botoes sao pills.
- [x] CA03: CameraPreview e um card escuro (#16181c) com bordas 24px.
- [x] CA06: ErrorBoundary renderiza como card branco com borda vermelha e botao cinza.
- [x] CA08: Botoes "Executar" (azul), "Reset" e "Vista Normal" (cinza) estilizados corretamente.
- [x] CA09: Historico com items em background #f7f7f7, fonte mono, bordas arredondadas.

## Testes Esperados

- `npm run build` deve passar sem erros.
- `npm run dev` deve mostrar todos os paineis com os novos estilos.

## Comandos pos-fase

- `npm run check`
- `npm run build`

## Registro de Execucao

- Data: 2026-06-15
- Arquivos criados: Nenhum.
- Arquivos alterados:
  - `lbot-simulator-web/src/styles.css` (StatusPanel: adicionado font-size/weight nos h2/h3 headers; CameraPreview: transformado para dark card com background #16181c, texto branco, padding 32px, frame com bordas escuras, placeholder texto claro, loading spinner adaptado; error placeholder ajustado para #ff6b6b)
- Testes executados:
  - `npm run check`: sucesso (0 erros TypeScript)
  - `npm run build`: sucesso (vite build concluido)
- Resultado: Fase 02 concluida com sucesso. A maioria dos estilos ja estavam implementados corretamente desde a Fase 01 (StatusPanel, CommandPanel, ErrorBoundary). Trabalho concentrado na transformacao do CameraPreview para product-ui-card-dark e ajuste de tamanhos de headings (18px/600 para h2, 16px/600 para h3).
- Pendencias: Nenhuma.
