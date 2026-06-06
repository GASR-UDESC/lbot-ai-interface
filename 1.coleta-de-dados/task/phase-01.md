# Fase 01: Fundacao - CSS Variables + Top-Nav Global

## Status: PENDENTE

## Objetivo

Atualizar todo o design system global (variaveis CSS, reset, tipografia) de tema claro Airbnb para tema escuro BMW M, e criar o componente `app-top-nav` com navegacao global fixa no topo, incluindo menu hamburger para mobile.

## Pre-requisitos

- Nenhum (primeira fase)

## Tarefas

- [ ] Tarefa 1: Atualizar variaveis CSS globais em `styles.css`
  - Arquivo: `src/styles.css`
  - O que fazer: Substituir TODOS os valores das variaveis `:root` para o tema BMW M:
    - **Cores**:
      - `--color-primary`: `#ff385c` -> `#ffffff` (branco e o CTA no tema escuro)
      - `--color-primary-active`: `#e00b41` -> `#e6e6e6` (hover branco mais suave)
      - `--color-primary-disabled`: `#ffd1da` -> `#3c3c3c` (cinza desabilitado)
      - `--color-primary-error-text`: `#c13515` -> `#e22718` (vermelho M para erros)
      - `--color-ink`: `#222222` -> `#ffffff` (texto principal vira branco)
      - `--color-body`: `#3f3f3f` -> `#bbbbbb` (body text cinza claro)
      - `--color-muted`: `#6a6a6a` -> `#7e7e7e`
      - `--color-muted-soft`: `#929292` -> `#5e5e5e`
      - `--color-hairline`: `#dddddd` -> `#3c3c3c`
      - `--color-hairline-soft`: `#ebebeb` -> `#262626`
      - `--color-border-strong`: `#c1c1c1` -> `#505050`
      - `--color-canvas`: `#ffffff` -> `#000000`
      - `--color-surface-soft`: `#f7f7f7` -> `#0d0d0d`
      - `--color-surface-strong`: `#f2f2f2` -> `#262626` (surface-elevated)
      - `--color-on-primary`: `#ffffff` -> `#000000` (texto sobre primario branco = preto)
      - `--color-star-rating`: `#222222` -> `#ffffff`
      - `--color-scrim`: `#000000` -> `#000000` (mantido)
      - `--color-legal-link`: `#428bff` -> `#1c69d4` (BMW blue)
      - Adicionar: `--color-surface-card`: `#1a1a1a`
        - Adicionar: `--color-m-blue-light`: `#0066b1`
      - Adicionar: `--color-m-blue-dark`: `#1c69d4`
      - Adicionar: `--color-m-red`: `#e22718`
      - Adicionar: `--color-body-strong`: `#e6e6e6`
    - **Border-radius**:
      - `--rounded-none`: `0` (mantido)
      - `--rounded-xs`: `4px` -> `2px`
      - `--rounded-sm`: `8px` -> `4px`
      - `--rounded-md`: `14px` -> `6px`
      - `--rounded-lg`: `20px` -> `0px`
      - `--rounded-xl`: `32px` -> `0px`
      - `--rounded-full`: `9999px` (mantido)
    - **Tipografia - Pesos** (ajustar para BMW M):
      - `--typography-body-md-weight`: `400` -> `300` (Light)
      - `--typography-body-sm-weight`: `400` -> `300` (Light)
      - `--typography-title-md-weight`: `600` -> `400`
      - `--typography-title-sm-weight`: `500` -> `400`
      - `--typography-button-md-weight`: `500` -> `700`
      - `--typography-button-sm-weight`: `500` -> `700`
      - `--typography-display-xl-weight`: `700` (mantido)
      - `--typography-display-lg-weight`: `500` -> `700`
      - `--typography-display-md-weight`: `700` (mantido)
      - `--typography-display-sm-weight`: `600` -> `700`
    - **Tipografia - Letter-spacing** (adicionar novas vars):
      - Adicionar: `--typography-button-letter-spacing`: `1.5px`
      - Adicionar: `--typography-display-lg-letter-spacing`: `-0.5px`
      - Adicionar: `--typography-display-xl-letter-spacing`: `-0.5px`
      - Adicionar: `--typography-label-uppercase-size`: `14px`
      - Adicionar: `--typography-label-uppercase-weight`: `700`
      - Adicionar: `--typography-label-uppercase-letter-spacing`: `1.5px`
      - Adicionar: `--typography-label-uppercase-line-height`: `1.3`
      - Adicionar: `--typography-nav-link-size`: `14px`
      - Adicionar: `--typography-nav-link-weight`: `400`
      - Adicionar: `--typography-nav-link-letter-spacing`: `0.5px`
      - Adicionar: `--typography-nav-link-line-height`: `1.4`
    - **Body global**:
      - `color: var(--color-ink)` (agora branco)
      - `background-color: var(--color-canvas)` (agora preto)
    - **Adicionar classe utilitaria `.m-stripe`**:
      ```css
      .m-stripe {
        display: block;
        width: 100%;
        height: 4px;
        background: linear-gradient(to right, var(--color-m-blue-light) 0%, var(--color-m-blue-light) 33.33%, var(--color-m-blue-dark) 33.33%, var(--color-m-blue-dark) 66.66%, var(--color-m-red) 66.66%, var(--color-m-red) 100%);
        flex-shrink: 0;
      }
      ```
    - **Remover shadow**:
      - `--shadow-card-hover-float`: trocar para `0 0 0 1px var(--color-hairline)` (hairline border, sem sombra)

- [ ] Tarefa 2: Criar componente `app-top-nav`
  - Arquivos: `src/app/components/top-nav/top-nav.ts`, `top-nav.html`, `top-nav.css`
  - O que fazer:
    - Componente Angular standalone com `imports: [RouterLink, RouterLinkActive, LucideAngularModule]`
    - **Desktop (>=768px)**:
      - Fundo preto (`var(--color-canvas)`), altura 64px, fixo no topo (`position: fixed`, `top: 0`, `z-index: 1000`)
      - Lado esquerdo: logo/nome "LBOT" em `label-uppercase` (14px, weight 700, tracking 1.5px)
      - Centro/direita: links de navegacao (Menu, Jogar, Controle, Leaderboard) usando `routerLink` e `routerLinkActive`
      - Link ativo: texto branco full opacity (`#ffffff`); links inativos: `var(--color-body)` (`#bbbbbb`)
      - Faixa tricolor M de 4px na borda inferior (usar classe `.m-stripe`)
    - **Mobile (<768px)**:
      - Nav colapsa: mostrar hamburger button (icone Lucide `Menu`), logo LBOT
      - Ao clicar no hamburger: overlay tela cheia com fundo `var(--color-canvas)`, faixa M tricolor no topo, links de navegacao empilhados verticalmente com `label-uppercase`
      - Fechar overlay ao clicar em link ou em botao de close (icone Lucide `X`)
    - Styling:
      - `border-bottom: none` (a faixa M substitui a borda)
      - Links: `font-size: var(--typography-nav-link-size)`, `weight: var(--typography-nav-link-weight)`, `tracking: var(--typography-nav-link-letter-spacing)`

- [ ] Tarefa 3: Atualizar `app.component` para incluir top-nav
  - Arquivo: `src/app/app.ts`
  - O que fazer: Importar `TopNavComponent` e adicionar ao array `imports`
  - Arquivo: `src/app/app.html`
  - O que fazer: Adicionar `<app-top-nav></app-top-nav>` acima do `<router-outlet>`. Remover o comentario "Top Nav sera adicionado na Fase 02"
  - Arquivo: `src/app/app.css`
  - O que fazer: Adicionar `padding-top: 64px` ao `:host` para compensar a nav fixa. OU adicionar `padding-top` via var `--top-nav-height: 64px` e usar essa var nos layouts das paginas

- [ ] Tarefa 4: Ajustar padding-top em todas as paginas
  - Arquivos: `src/app/pages/menu/menu.page.css`, `src/app/pages/game/game.page.css`, `src/app/pages/leaderboard/leaderboard.page.css`, `src/app/pages/controls/controls.page.css`
  - O que fazer: Garantir que cada pagina tenha `padding-top` ou `margin-top` suficiente para nao ficar escondida atras do top-nav fixo (64px). A maioria ja usa `100dvh` ou `min-height: 100dvh` — ajustar para `calc(100dvh - 64px)` ou adicionar `padding-top: 64px` ao conteudo
  - Para game.page que usa `height: 100dvh` no `:host`, mudar para `height: calc(100dvh - 64px)` ou adicionar padding
  - Para controls.page que usa `height: 100dvh`, mesma abordagem
  - Para menu.page e leaderboard.page que usam `min-height: 100dvh`, adicionar `padding-top: 64px` ao conteudo

- [ ] Tarefa 5: Remover link "Voltar ao Menu" do leaderboard
  - Arquivo: `src/app/pages/leaderboard/leaderboard.page.html`
  - O que fazer: Remover ou atualizar o `<a class="lb-back-btn">` que faz navegacao manual para `/menu`, uma vez que o top-nav agora provê navegação global. Transformar em link stilizado BMW M ou remover.

- [ ] Tarefa 6: Auditar e corrigir hover states globais
  - Arquivo: `src/styles.css`
  - O que fazer: Adicionar estilos globais para hover de botoes BMW M:
    - Botoes outline: hover -> `background: var(--color-surface-card)`, `border-color: var(--color-on-dark)`
    - Links: hover -> `opacity: 0.8`
    - Remover `box-shadow` hover em favor de `border-color`
    - Adicionar estilo base para `.btn-outline`: `border: 1px solid var(--color-on-dark); background: transparent; color: var(--color-on-dark); border-radius: 0; font-weight: 700; text-transform: uppercase; letter-spacing: 1.5px;`
    - Adicionar estilo base para `.btn-filled`: `border: 1px solid var(--color-on-dark); background: var(--color-on-dark); color: var(--color-canvas); border-radius: 0;`

## Arquivos Referencia

- `src/styles.css` - Design system atual com variaveis
- `task/DESIGN-bmw-m.md` - Design system BMW M completo
- `task/business-spec.md` - Especificacao de negocio

## Criterios de Aceite

- [ ] CA01: Top Navigation Global visivel em todas as paginas
  - Cenario: Dado que o usuario esta em qualquer pagina / Quando a pagina carrega / Entao o top-nav global de 64px aparece fixo no topo com fundo preto, logo LBOT a esquerda, links de navegacao a direita, e faixa tricolor M de 4px na borda inferior.
- [ ] CA02: Navegacao funcional no top-nav
  - Cenario: Dado que o usuario esta em qualquer pagina / Quando clica em um link de navegacao / Entao a aplicacao navega para a rota correspondente e o link ativo recebe indicador visual.
- [ ] CA03: Top-nav responsivo com hamburger em mobile
  - Cenario: Dado que o usuario esta em viewport < 768px / Quando visualiza o top-nav / Entao o nav colapsa para hamburger e ao clicar abre overlay tela cheia com fundo preto e faixa M tricolor.
- [ ] CA07: Tema escuro BMW M aplicado em toda a aplicacao (variaveis)
  - Cenario: Dado que o usuario esta em qualquer pagina / Quando visualiza a aplicacao / Entao o fundo e preto (#000000), o texto principal e branco (#ffffff), as superficies elevadas usam #1a1a1a, e os hairlines usam #3c3c3c.
- [ ] CA09: Cantos retos BMW nas variaveis CSS
  - Cenario: Dado que as variaveis CSS foram atualizadas / Quando componentes usam var(--rounded-md) / Entao o valor e 6px (nao 14px).
- [ ] CA10: Faixa tricolor M como acento de marca
  - Cenario: Dado que o CSS global foi atualizado / Quando a classe .m-stripe e usada / Entao a faixa tricolor de 4px aparece com as cores corretas (#0066b1, #1c69d4, #e22718).

## Testes Esperados

- `ng build` - Build sem erros
- `ng serve` - Aplicacao carrega com fundo preto, texto branco, top-nav visivel
- Verificar visualmente: top-nav em desktop (4 links + logo + faixa M)
- Verificar visualmente: top-nav em mobile (<768px) - hamburger visivel, overlay funcional
- Verificar: todas as paginas carregam sem conteudo escondido atras do nav

## Comandos pos-fase

- `npx ng build`
- `npx ng serve` (verificacao visual manual)

## Registro de Execucao

(Preenchido pelo agente durante a execucao)

- Data:
- Arquivos criados:
- Arquivos alterados:
- Testes executados:
- Resultado:
- Pendencias: