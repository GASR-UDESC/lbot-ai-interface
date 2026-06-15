# Fase 04: Validacao e Ajustes Finais

## Status: PENDENTE

## Objetivo

Validar a migracao completa: executar build, verificar todos os criterios de aceite do business-spec, ajustar detalhes de layout, e garantir que nenhum texto foi alterado e que a logica de negocio permanece intacta.

## Pre-requisitos

- Fase 03 concluida (canvas, erros, responsividade, micro-interacoes).

## Tarefas

- [ ] Tarefa 1: Executar build e verificar erros
  - Arquivo: `lbot-simulator-web/`
  - O que fazer: Rodar `npm run check` e `npm run build`. Corrigir quaisquer erros de TypeScript ou lint.

- [ ] Tarefa 2: Verificar checklist de criterios de aceite
  - Arquivo: `task/business-spec.md`
  - O que fazer: Validar visualmente cada cenario de aceite (CA01-CA10) via `npm run dev`. Usar DevTools para simular mobile e desktop. Verificar cores, tokens, terminologia, botoes, layout, hover states.

- [ ] Tarefa 3: Ajustar detalhes de layout e padding
  - Arquivo: `lbot-simulator-web/src/styles.css`
  - O que fazer: Ajustar padding, gap, margin, ou border-radius que possam estar inconsistentes. Verificar que o `max-width: 1200px` centraliza corretamente em wide. Ajustar o `min-height` do canvas para nao quebrar em diferentes viewports.

- [ ] Tarefa 4: Verificar terminologia e textos
  - Arquivo: `lbot-simulator-web/src/App.tsx`, `lbot-simulator-web/src/components/*.tsx`
  - O que fazer: Garantir que NENHUM texto foi alterado ou traduzido. Confirmar que "Comandos LBML", "Sequencia", "Posicao X", "Executar", "Reset", "Vista Normal", "3a Pessoa", "Nenhum comando executado ainda.", "POST /api/commands", "POST /api/reset" estao presentes.

- [ ] Tarefa 5: Revisar acessibilidade (contrastes e focus states)
  - Arquivo: `lbot-simulator-web/src/styles.css`
  - O que fazer: Verificar que botoes tem altura minima 44px, focus states sao visiveis, e cores mantem contraste WCAG AA (verificar rapidamente com DevTools contrast ratio se possivel).

## Arquivos Referencia

- `task/business-spec.md` - Criterios de aceite CA01-CA10.
- `lbot-simulator-web/src/styles.css` - CSS final para revisao.
- `lbot-simulator-web/src/App.tsx` - Layout final para revisao.
- `lbot-simulator-web/src/components/*.tsx` - Todos os componentes para verificacao de texto.

## Criterios de Aceite

- [ ] CA01: Tema light aplicado (fundo branco, cards brancos, sem gradientes).
- [ ] CA02: Layout reestruturado com top-nav + sidebar + hero canvas.
- [ ] CA03: Componentes reestilizados com tokens Coinbase.
- [ ] CA04: Micro-interacoes funcionam (hover, focus, active).
- [ ] CA05: Responsividade em mobile funciona.
- [ ] CA06: Erro WebGL estilizado como card branco com borda vermelha.
- [ ] CA07: Terminologia preservada (textos originais mantidos).
- [ ] CA08: Botoes estilizados corretamente (primario azul, secundarios cinza).
- [ ] CA09: Historico estilizado com background #f7f7f7 e fonte mono.
- [ ] CA10: Top-nav presente com 64px, branco, titulo visivel.

## Testes Esperados

- `npm run build` - sucesso.
- `npm run check` - sucesso (sem erros TypeScript).
- Testes visuais manuais em DevTools (mobile, tablet, desktop).

## Comandos pos-fase

- `npm run check`
- `npm run build`
- `npm run dev` (para validacao visual final)

## Registro de Execucao

- Data:
- Arquivos criados:
- Arquivos alterados:
- Testes executados:
- Resultado:
- Pendencias:
