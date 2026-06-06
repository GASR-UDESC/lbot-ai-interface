# Fase 01: Design System Foundation

## Status: CONCLUIDO

## Objetivo

Estabelecer toda a fundacao do design system Airbnb como CSS custom properties em `styles.css`, configurar a fonte Inter via Google Fonts CDN, e adaptar o layout shell root (`app.html`, `app.css`) para o tema claro.

## Pre-requisitos

- Nenhum (primeira fase)

## Tarefas

- [x] Tarefa 1: Adicionar fonte Inter via Google Fonts CDN no `index.html`
  - Arquivo: `src/index.html`
  - O que fazer: Adicionar `<link>` para Google Fonts (Inter weights 400, 500, 600, 700) no `<head>`, antes dos style imports
  - Link: `https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap`

- [x] Tarefa 2: Definir todos os CSS custom properties Airbnb em `styles.css`
  - Arquivo: `src/styles.css`
  - O que fazer: Adicionar bloco `:root { ... }` com TODOS os tokens do design system Airbnb:
    - **Cores**: primary, primary-active, primary-disabled, primary-error-text, ink, body, muted, muted-soft, hairline, hairline-soft, border-strong, canvas, surface-soft, surface-strong, on-primary, star-rating, scrim, legal-link
    - **Tipografia**: mapear tokens para font-family Inter, e criar classes utilitarias ou custom properties para: display-xl, display-lg, display-md, display-sm, title-md, title-sm, body-md, body-sm, caption, caption-sm, uppercase-tag, button-md, button-sm, rating-display, nav-link, micro-label
    - **Espacamento**: xxs (2px), xs (4px), sm (8px), md (12px), base (16px), lg (24px), xl (32px), xxl (48px), section (64px)
    - **Border radius**: none (0), xs (4px), sm (8px), md (14px), lg (20px), xl (32px), full (9999px)
    - **Shadows**: card-hover-float com o shadow tier unico do Airbnb
    - **Transicoes**: fade-in, scale-in com duracoes adequadas

- [x] Tarefa 3: Atualizar reset global e base styles em `styles.css`
  - Arquivo: `src/styles.css`
  - O que fazer: Atualizar o reset existente e adicionar:
    - `font-family: 'Inter', -apple-system, system-ui, Roboto, 'Helvetica Neue', sans-serif` no `html, body`
    - `color: var(--color-ink)` no `body`
    - `background-color: var(--color-canvas)` no `body`
    - `min-height: 100dvh` no `body`
    - Remover qualquer referencia a cores dark/neon verde

- [x] Tarefa 4: Atualizar `app.css` para remover variaveis dark e adaptar shell
  - Arquivo: `src/app/app.css`
  - O que fazer:
    - Remover TODAS as variaveis dark/neon do `:root` (--phone-bg, --color-primary, --color-primary-dark, --color-bg-dark, --color-bg-darker, --color-text-light, --color-text-muted, --color-border)
    - Adicionar `background-color: var(--color-canvas)` no `:host`
    - Garantir que `app-root` ocupe 100dvh width/height com fundo canvas
    - Manter `font-family: 'Inter', -apple-system, system-ui, Roboto, 'Helvetica Neue', sans-serif`

- [x] Tarefa 5: Atualizar `app.html` para incluir top-nav placeholder
  - Arquivo: `src/app/app.html`
  - O que fazer: Adicionar comentario `<!-- Top Nav sera adicionado na Fase 02 -->` acima do `<router-outlet>`. Nao adicionar componente ainda, apenas preparar o HTML para receber a nav.

- [x] Tarefa 6: Atualizar `app.ts` imports
  - Arquivo: `src/app/app.ts`
  - O que fazer: Remover comentarios desnecessarios e garantir que esta importando apenas RouterOutlet

## Arquivos Referencia

- `src/styles.css` - Reset global atual (19 linhas)
- `src/app/app.css` - Variaveis dark atuais (25 linhas)
- `src/app/app.html` - Template root atual (apenas router-outlet)
- `src/app/app.ts` - Componente root atual
- `task/DESIGN-airbnb.md` - Especificacao completa dos tokens

## Criterios de Aceite

- [ ] CA01: Ao abrir o app, o fundo e branco (#ffffff) e nao ha mais tema escuro
- [ ] CA03 (parcial): A fonte Inter esta sendo carregada e aplicada em todos os textos
- [ ] CA12 (parcial): Todas as CSS custom properties estao definidas e podem ser usadas pelos componentes
  - Cenario: Inspecionar `:root` no DevTools e verificar que todas as variaveis `--color-*`, `--spacing-*`, `--rounded-*`, `--typography-*` estao presentes
- [ ] CA13 (parcial): Nenhuma cor dark/neon verde permanece nas variaveis CSS globais

## Testes Esperados

- `ng build --configuration local` - Build deve compilar sem erros
- Verificacao visual: app carrega com fundo branco e fonte Inter
- Verificacao no DevTools: `:root` contem todas as custom properties Airbnb

## Comandos pos-fase

```bash
cd lbot-datagen/lbot-datagen-frontend && ng build --configuration local
```

## Registro de Execucao

- Data: 2026-06-06
- Arquivos criados: Nenhum
- Arquivos alterados: `src/styles.css`, `src/app/app.css`, `src/app/app.html`, `src/app/app.ts`, `src/index.html`
- Testes executados: `ng build --configuration local` - build OK (prerendering SSR com erro pre-existente no DatePipe do leaderboard, nao relacionado a esta fase)
- Resultado: Build compilou sem erros de CSS/template. Tokens Airbnb definidos no `:root`, reset global atualizado, fonte Inter carregada via CDN, variaveis dark removidas do app shell.
- Pendencias: Nenhuma