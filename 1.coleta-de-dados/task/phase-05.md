# Fase 05: Leaderboard Cards + Controls Page + Virtual Controls

## Status: PENDENTE

## Objetivo

Redesenhar a pagina Leaderboard de tabela dark para cards estilo Airbnb property-card, e redesenhar a pagina Controls e componente VirtualControls para tema claro Airbnb.

## Pre-requisitos

- Fase 01 concluida (tokens CSS)
- Fase 02 concluida (top-nav aparecera em ambas as paginas)

## Tarefas

- [ ] Tarefa 1: Redesenhar Leaderboard Page (RF08)
  - Arquivo: `src/app/pages/leaderboard/leaderboard.page.html`
  - O que fazer: Converter a tabela HTML para um layout de cards:
    - Header: icone de trofeu + titulo display-lg ink "Leaderboard" + subtitulo body-md muted
    - Cards de ranking: cada jogador como um card independente com fundo canvas, rounded.md, hairline border, hover com card-hover-float shadow
    - Estrutura do card: rank/posicao em grande (rating-display para top 3, title-md para demais), nickname em title-md ink, tempo em body-md muted com valor monospace tabular-nums, data em caption-sm muted
    - Top 3 recebe icones de medalha (ouro, prata, bronze)
    - Grid responsivo: 4-up desktop (>1128px), 2-3 up tablet (744-1128px), 1-up mobile (<744px)
    - Empty state: icone + mensagem em body-md muted
    - Error state: icone + mensagem em primary-error-text + botao retry button-primary
    - Loading state: skeleton cards com surface-soft e animacao pulse
    - Footer: link "Voltar ao Menu" como button-tertiary-text com underline hover

  - Arquivo: `src/app/pages/leaderboard/leaderboard.page.css`
  - O que fazer: Substituir TODOS os estilos dark/neon por tokens Airbnb:
    - `.lb-page`: fundo canvas, sem gradientes escuros, padding section (64px)
    - `.lb-header`: centralizado, cor ink
    - `.lb-title`: display-lg ink
    - `.lb-subtitle`: body-md muted
    - Cards: `.lb-card` - fundo canvas, rounded.md, hairline border (#dddddd), hover com shadow card-hover-float
    - `.lb-card:hover`: elevacao card-hover-float
    - `.lb-rank`: rating-display para top 3, title-md para demais
    - `.lb-nickname`: title-md ink
    - `.lb-time`: body-md muted, font-variant-numeric: tabular-nums
    - `.lb-date`: caption-sm muted
    - Medals: manter emojis ou usar icones lucide
    - Loading: `.lb-skeleton` com surface-soft e animacao pulse
    - Error state: primary-error-text
    - `.lb-retry-btn`: button-primary Rausch
    - `.lb-back-btn`: button-tertiary-text, ink text, underline hover
    - Grid responsivo com CSS Grid ou Flexbox
    - Remover: TODAS as cores dark (#0a0a0e, #6a6a8f, etc.), gradientes, bordas neon

- [ ] Tarefa 2: Redesenhar Controls Page (RF09)
  - Arquivo: `src/app/pages/controls/controls.page.html`
  - O que fazer: Ajustar HTML para:
    - Remover o header atual com fundo dark e substituir por layout que depende da top-nav global
    - Titulo da pagina display-sm ink "Modo Controle" + subtitulo body-md muted
    - Layout de duas colunas: simulador a esquerda (flex 1.2) + painel de controles a direita
    - Simulador: container com rounded.md, hairline border, fundo canvas
    - Remover `<a routerLink="/menu">` inline (ja esta na top-nav)

  - Arquivo: `src/app/pages/controls/controls.page.css`
  - O que fazer: Substituir TODOS os estilos dark por tokens Airbnb:
    - `.controls-page`: fundo canvas (#ffffff), sem gradientes escuros
    - Layout header: removido (top-nav global cuida disso)
    - Titulo e subtitulo em tokens tipograficos Airbnb
    - `.controls-layout`: grid 2 colunas (1.2fr 1fr) em desktop, 1 coluna em mobile (<768px)
    - `.simulator-container`: rounded.md, hairline border, fundo canvas
    - `.controls-panel`: fundo canvas, rounded.md, hairline border, sem sombra dark
    - Remover: cores dark (#101114, #f5faf5, etc.), gradientes, shadows excessivas

- [ ] Tarefa 3: Redesenhar VirtualControls Component (RF10)
  - Arquivo: `src/app/components/virtual-controls/virtual-controls.html`
  - O que fazer: Ajustar classes para estilo Airbnb:
    - Botoes de acao (Frente, Tras, Esquerda, Direita): icon-button-circle com surface-strong fundo, ink icone, rounded.full, 44px min touch target
    - Botoes de rotacao (Girar Esq., Girar Dir.): mesmo estilo
    - Timeline: lista vertical com hairline-soft entre itens, rounded.sm
    - Botao remover (X) por item: icon-button-circle pequeno, surface-strong
    - Textarea de descricao: text-input estilo Airbnb (56px, rounded.sm)
    - Botao "Executar": button-primary, rounded.sm, full-width quando mobile
    - Botao "Limpar Tudo": button-tertiary-text, ink com underline hover

  - Arquivo: `src/app/components/virtual-controls/virtual-controls.css`
  - O que fazer: Substituir TODOS os estilos dark por tokens Airbnb:
    - Fundo geral: canvas (#ffffff)
    - Botoes direcionais: surface-strong (#f2f2f2) fundo, ink (#222222) icone, rounded.full, min 44px touch target
    - Botoes de rotacao: mesmo estilo
    - Timeline: fundo canvas, hairline-soft (#ebebeb) entre itens, rounded.sm
    - Resumo/LBML: fundo surface-soft (#f7f7f7), caption-sm monospace
    - Botao executar: button-primary (Rausch bg, on-primary text)
    - Botao limpar: button-tertiary-text (transparent bg, ink text, underline hover)
    - Remover: TODAS as cores dark, gradientes, bordas neon

- [ ] Tarefa 4: Adicionar estados de loading/error a Leaderboard (RF08)
  - Arquivo: `src/app/pages/leaderboard/leaderboard.page.html`
  - O que fazer: Garantir que os estados de loading, error e empty ja existam no template (eles ja existem, basta estilizar):
    - Loading: skeleton cards
    - Error: icone + texto primary-error-text + botao retry button-primary
    - Empty: icone + texto body-md muted

## Arquivos Referencia

- `src/app/pages/leaderboard/leaderboard.page.ts` - Logica (nao alterar)
- `src/app/pages/leaderboard/leaderboard.page.html` - Template atual com tabela
- `src/app/pages/leaderboard/leaderboard.page.css` - 224 linhas dark/neon
- `src/app/pages/controls/controls.page.ts` - Logica (nao alterar)
- `src/app/pages/controls/controls.page.html` - Template atual
- `src/app/pages/controls/controls.page.css` - 117 linhas dark/clr
- `src/app/components/virtual-controls/virtual-controls.ts` - Logica (nao alterar)
- `src/app/components/virtual-controls/virtual-controls.html` - Template atual
- `src/app/components/virtual-controls/virtual-controls.css` - 396 linhas dark
- `task/DESIGN-airbnb.md` - Especificacao de property-card, icon-button-circle, button-primary, button-secondary

## Criterios de Aceite

- [ ] CA07: Leaderboard com Cards Airbnb
  - Cenario: Cada jogador e exibido como card property-card (rounded.md, hairline border) com rank, nickname, tempo, data
  - Cenario: Top 3 tem destaque visual com icones de medalha
  - Cenario: Hover no card aplica elevacao card-hover-float
- [ ] CA08: Leaderboard - Estados Especiais
  - Cenario: Sem dados exibe empty state com icone + mensagem muted
  - Cenario: Erro na API exibe error state com primary-error-text e botao retry button-primary
- [ ] CA09: Pagina de Controls Airbnb-style
  - Cenario: Layout de duas colunas com simulador a esquerda e painel de controles a direita, fundo canvas branco
  - Cenario: Botoes direcionais em icon-button-circle com surface-strong, ink, rounded.full
  - Cenario: Botao "Executar" em button-primary Rausch
- [ ] CA10 (parcial): Responsividade Mobile - Leaderboard
  - Cenario: Cards empilham 1-up em <744px
- [ ] CA11 (parcial): Responsividade Tablet - Leaderboard
  - Cenario: Cards 2-3 up em 744-1128px

## Testes Esperados

- Leaderboard carrega com cards visuais corretos
- Leaderboard exibe loading, error e empty states
- Hover em cards aplica sombra
- Controles direcionais funcionam (Frente, Tras, Esquerda, Direita, Girar)
- Timeline exibe comandos adicionados
- Botao "Executar" envia comandos ao simulador
- Botao "Limpar" reseta a timeline
- Layout responsivo funciona em desktop e mobile

## Comandos pos-fase

```bash
cd lbot-datagen/lbot-datagen-frontend && ng build --configuration local
```

## Registro de Execucao

- Data:
- Arquivos criados:
- Arquivos alterados:
- Testes executados:
- Resultado:
- Pendencias: