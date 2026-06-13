# Fase 01: Design Tokens + Fontes + Remocao M-Stripe Global

## Status: PENDENTE

## Objetivo

Substituir todos os design tokens BMW no `styles.css` pelos tokens Coinbase, adicionar JetBrains Mono no `index.html`, remover a classe `.m-stripe` global e remover os elementos m-stripe do template da top-nav. Ao final desta fase, o app tera a base de tokens Coinbase e nenhum elemento BMW residual no CSS global.

## Pre-requisitos

- Nenhum (esta e a primeira fase)

## Tarefas

- [ ] Tarefa 1: Adicionar JetBrains Mono no `index.html`
  - Arquivo: `src/index.html`
  - O que fazer: Adicionar link do Google Fonts para JetBrains Mono (weights 400;500;700) ao lado do link existente da Inter. O link deve ser:
    ```html
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;700&display=swap" rel="stylesheet">
    ```
    Combinar no mesmo link do Google Fonts para performance.

- [ ] Tarefa 2: Substituir design tokens de cores no `styles.css`
  - Arquivo: `src/styles.css`
  - O que fazer: Substituir todas as variaveis `--color-*` na secao `:root` pelos valores Coinbase:
    ```css
    --color-primary: #0052ff;
    --color-primary-active: #003ecc;
    --color-primary-disabled: #a8b8cc;
    --color-primary-error-text: #cf202f;
    --color-ink: #0a0b0d;
    --color-body: #5b616e;
    --color-body-strong: #0a0b0d;
    --color-muted: #7c828a;
    --color-muted-soft: #a8acb3;
    --color-hairline: #dee1e6;
    --color-hairline-soft: #eef0f3;
    --color-border-strong: #dee1e6;
    --color-canvas: #ffffff;
    --color-surface-soft: #f7f7f7;
    --color-surface-strong: #eef0f3;
    --color-surface-elevated: #eef0f3;
    --color-surface-card: #ffffff;
    --color-surface-dark: #0a0b0d;
    --color-surface-dark-elevated: #16181c;
    --color-on-primary: #ffffff;
    --color-on-dark: #ffffff;
    --color-on-dark-soft: #a8acb3;
    --color-star-rating: #f4b000;
    --color-scrim: rgba(0, 0, 0, 0.6);
    --color-legal-link: #0052ff;
    --color-semantic-up: #05b169;
    --color-semantic-down: #cf202f;
    ```
    Remover tokens BMW: `--color-m-blue-light`, `--color-m-blue-dark`, `--color-m-red`.

- [ ] Tarefa 3: Substituir design tokens de spacing no `styles.css`
  - Arquivo: `src/styles.css`
  - O que fazer: Substituir `--spacing-*` pelos valores Coinbase:
    ```css
    --spacing-xxs: 4px;
    --spacing-xs: 8px;
    --spacing-sm: 12px;
    --spacing-md: 20px;
    --spacing-base: 16px;
    --spacing-lg: 24px;
    --spacing-xl: 32px;
    --spacing-xxl: 48px;
    --spacing-section: 96px;
    ```

- [ ] Tarefa 4: Substituir design tokens de border-radius no `styles.css`
  - Arquivo: `src/styles.css`
  - O que fazer: Substituir `--rounded-*` pelos valores Coinbase:
    ```css
    --rounded-none: 0;
    --rounded-xs: 4px;
    --rounded-sm: 8px;
    --rounded-md: 12px;
    --rounded-lg: 16px;
    --rounded-xl: 24px;
    --rounded-pill: 100px;
    --rounded-full: 9999px;
    ```

- [ ] Tarefa 5: Substituir design tokens de tipografia no `styles.css`
  - Arquivo: `src/styles.css`
  - O que fazer: Substituir todos os `--typography-*` pelos valores Coinbase (usando Inter como substituta de CoinbaseDisplay/CoinbaseSans e JetBrains Mono como substituta de CoinbaseMono):
    ```css
    --typography-display-xl-size: 64px;
    --typography-display-xl-weight: 400;
    --typography-display-xl-line-height: 1.0;
    --typography-display-xl-letter-spacing: -1.6px;
    --typography-display-lg-size: 52px;
    --typography-display-lg-weight: 400;
    --typography-display-lg-line-height: 1.0;
    --typography-display-lg-letter-spacing: -1.3px;
    --typography-display-md-size: 44px;
    --typography-display-md-weight: 400;
    --typography-display-md-line-height: 1.09;
    --typography-display-md-letter-spacing: -1px;
    --typography-display-sm-size: 36px;
    --typography-display-sm-weight: 400;
    --typography-display-sm-line-height: 1.11;
    --typography-display-sm-letter-spacing: -0.5px;
    --typography-title-lg-size: 32px;
    --typography-title-lg-weight: 400;
    --typography-title-lg-line-height: 1.13;
    --typography-title-lg-letter-spacing: -0.4px;
    --typography-title-md-size: 18px;
    --typography-title-md-weight: 600;
    --typography-title-md-line-height: 1.33;
    --typography-title-md-letter-spacing: 0;
    --typography-title-sm-size: 16px;
    --typography-title-sm-weight: 600;
    --typography-title-sm-line-height: 1.25;
    --typography-title-sm-letter-spacing: 0;
    --typography-body-md-size: 16px;
    --typography-body-md-weight: 400;
    --typography-body-md-line-height: 1.5;
    --typography-body-md-letter-spacing: 0;
    --typography-body-sm-size: 14px;
    --typography-body-sm-weight: 400;
    --typography-body-sm-line-height: 1.5;
    --typography-body-sm-letter-spacing: 0;
    --typography-caption-size: 13px;
    --typography-caption-weight: 400;
    --typography-caption-line-height: 1.5;
    --typography-caption-sm-size: 12px;
    --typography-caption-sm-weight: 600;
    --typography-caption-sm-line-height: 1.5;
    --typography-button-md-size: 16px;
    --typography-button-md-weight: 600;
    --typography-button-md-line-height: 1.15;
    --typography-button-md-letter-spacing: 0;
    --typography-button-sm-size: 14px;
    --typography-button-sm-weight: 600;
    --typography-button-sm-line-height: 1.29;
    --typography-button-sm-letter-spacing: 0;
    --typography-nav-link-size: 14px;
    --typography-nav-link-weight: 500;
    --typography-nav-link-line-height: 1.4;
    --typography-nav-link-letter-spacing: 0;
    --typography-number-display-size: 18px;
    --typography-number-display-weight: 500;
    --typography-number-display-line-height: 1.4;
    --typography-number-display-letter-spacing: 0;
    --typography-micro-label-size: 12px;
    --typography-micro-label-weight: 600;
    --typography-micro-label-line-height: 1.33;
    --typography-rating-display-size: 64px;
    --typography-rating-display-weight: 500;
    --typography-rating-display-line-height: 1.1;
    ```
    Remover tokens BMW obsoletos: `--typography-uppercase-tag-*`, `--typography-button-letter-spacing`, `--typography-label-uppercase-*`.

- [ ] Tarefa 6: Atualizar classes utilitarias e remover m-stripe no `styles.css`
  - Arquivo: `src/styles.css`
  - O que fazer:
    1. Remover completamente a classe `.m-stripe` e seu CSS
    2. Atualizar `.btn-outline` para padrao Coinbase outline-on-dark:
       ```css
       .btn-outline {
         border: 1px solid var(--color-on-dark);
         background: transparent;
         color: var(--color-on-dark);
         border-radius: var(--rounded-pill);
         font-weight: 600;
         text-transform: none;
         letter-spacing: 0;
         padding: 12px 20px;
         height: 44px;
         cursor: pointer;
         transition: background 0.2s ease, border-color 0.2s ease;
       }
       .btn-outline:hover {
         background: var(--color-surface-dark-elevated);
       }
       ```
    3. Atualizar `.btn-filled` para padrao Coinbase primary:
       ```css
       .btn-filled {
         border: none;
         background: var(--color-primary);
         color: var(--color-on-primary);
         border-radius: var(--rounded-pill);
         font-weight: 600;
         text-transform: none;
         letter-spacing: 0;
         padding: 12px 20px;
         height: 44px;
         cursor: pointer;
         transition: background 0.2s ease;
       }
       .btn-filled:hover {
         background: var(--color-primary-active);
       }
       .btn-filled:disabled {
         background: var(--color-primary-disabled);
         cursor: not-allowed;
       }
       ```
    4. Atualizar `html, body` color para `var(--color-ink)` e background para `var(--color-canvas)` (ja usa var, so precisa confirmar que os novos valores funcionam)
    5. Atualizar `--shadow-card-hover-float` para: `0 4px 12px rgba(0, 0, 0, 0.04)`

- [ ] Tarefa 7: Remover elementos m-stripe do template top-nav
  - Arquivo: `src/app/components/top-nav/top-nav.html`
  - O que fazer: Remover as duas linhas `<div class="m-stripe"></div>` (uma dentro do `.nav-overlay-content` e uma no final do `<nav>`)

## Arquivos Referencia

- `src/styles.css` - Arquivo principal a ser reescrito (184 linhas atuais)
- `src/index.html` - Adicionar fonte JetBrains Mono
- `src/app/components/top-nav/top-nav.html` - Remover m-stripe (29 linhas)
- `DESIGN-coinbase.md` (em `/Users/guilherme.mendesrosa/Downloads/DESIGN-coinbase.md`) - Fonte de verdade para todos os valores de tokens

## Criterios de Aceite

- [ ] CA01: Design tokens migrados
  - Cenario: Dado que o `styles.css` foi atualizado, quando o app carrega, entao `getComputedStyle(document.documentElement).getPropertyValue('--color-primary')` retorna `#0052ff`
- [ ] CA02: M-Stripe removida
  - Cenario: Dado que `.m-stripe` foi removida do CSS global e dos templates, quando o usuario navega, entao nenhum elemento tricolor e visivel
- [ ] CA09: Build sem erros
  - Cenario: Dado que todas as alteracoes foram aplicadas, quando `ng build` e executado, entao completa sem erros

## Testes Esperados

- Verificar que `ng build` completa sem erros
- Verificar que nenhum token BMW residual existe (`--color-m-*`, `--typography-uppercase-tag-*`, `--typography-label-uppercase-*`)
- Verificar que `.m-stripe` nao existe em nenhum CSS ou HTML

## Comandos pos-fase

- `cd 1.coleta-de-dados/lbot-datagen/lbot-datagen-frontend && npx ng build --configuration local`

## Registro de Execucao

- Data:
- Arquivos criados:
- Arquivos alterados:
- Testes executados:
- Resultado:
- Pendencias:
