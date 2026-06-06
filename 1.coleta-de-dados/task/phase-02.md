# Fase 02: Top Nav + Menu/Home Page

## Status: PENDENTE

## Objetivo

Criar o componente de navegacao global (top-nav) e redesenhar completamente a pagina Menu/Home com hero section e search bar estilo Airbnb.

## Pre-requisitos

- Fase 01 concluida (tokens CSS e base styles definidos)

## Tarefas

- [ ] Tarefa 1: Criar componente TopNav (standalone)
  - Arquivos novos: `src/app/components/top-nav/top-nav.ts`, `top-nav.html`, `top-nav.css`
  - O que fazer: Criar componente standalone com:
    - Altura 80px, fundo canvas (#ffffff), borda inferior 1px hairline
    - Lado esquerdo: Logo/marca "LBot Arena" em typography nav-link (16px, 600)
    - Centro: 3 tabs - "Jogar" (/game), "Leaderboard" (/leaderboard), "Controles" (/controls) - estilo product-tab-active (ink + underline) para ativa, product-tab-inactive (muted) para inativas
    - Lado direito: Area de utilitarios (vazia por enquanto, reservada)
    - Tipografia: nav-link (16px, 600, 1.25)
    - Em mobile (<744px): colapsar para logo + hamburger, com menu dropdown

- [ ] Tarefa 2: Integrar TopNav no app shell
  - Arquivo: `src/app/app.html`
  - O que fazer: Adicionar `<app-top-nav></app-top-nav>` acima do `<router-outlet>` dentro de um wrapper com `display: flex; flex-direction: column; height: 100dvh`
  - Arquivo: `src/app/app.ts`
  - O que fazer: Importar `TopNavComponent` nos imports do AppComponent
  - Arquivo: `src/app/app.css`
  - O que fazer: Adicionar estilos de layout: wrapper flex column, router-outlet com flex: 1 e overflow: auto

- [ ] Tarefa 3: Redesenhar a pagina Menu/Home
  - Arquivo: `src/app/pages/menu/menu.page.html`
  - O que fazer: Substituir o conteudo completamente:
    - Hero section centralizado com titulo "LBot Arena" em display-xl (28px, 700) e subtitulo em body-md (16px, 400)
    - Search bar pill-shaped: fundo branco, rounded.full, 64px altura, dividida por hairlines em 3 segmentos ("Modo" / "Nivel" / "Jogador"), com search orb circular Rausch (48x48px) no lado direito
    - Ao clicar no search orb com "Jogar" selecionado: navegar para /game
    - Segmentos "Nivel" e "Jogador" exibem "Qualquer" por enquanto
    - Background: canvas branco com padding section (64px)
    - Footer section com links estilo footer-light do Airbnb
    - Remover a navegacao tipo card existente (btn-primary, btn-secondary, btn-tertiary)

- [ ] Tarefa 4: Redesenhar os estilos da pagina Menu/Home
  - Arquivo: `src/app/pages/menu/menu.page.css`
  - O que fazer: Substituir TODOS os estilos dark/neon por estilos Airbnb:
    - `.menu-wrapper`: fundo canvas, sem gradientes escuros
    - Hero section: centralizado, spacing generoso
    - Search bar: estilo Airbnb search-bar-pill com hairlines, segmentos clicaveis, search orb Rausch
    - Footer: estilo footer-light com hairline dividers, muted text
    - Mobile (<744px): search bar colapsa para pill unico com icone
    - Remover todas as cores dark (#0a0e0a, #0f0f12, etc.) e substituir por tokens Airbnb
    - Remover gradientes (linear-gradient com verdes/escuros)

## Arquivos Referencia

- `src/app/pages/menu/menu.page.ts` - Componente atual (usa RouterLink)
- `src/app/pages/menu/menu.page.html` - Template atual com cards dark
- `src/app/pages/menu/menu.page.css` - Estilos atuais dark/neon
- `src/app/app.html` - Shell atual (apenas router-outlet)
- `src/app/app.css` - Variaveis dark que serao removidas na Fase 01
- `task/DESIGN-airbnb.md` - Especificacao de search-bar-pill, top-nav, footer-light

## Criterios de Aceite

- [ ] CA01: Top Navigation Global
  - Cenario: Abrir qualquer pagina e ver a top nav com 80px de altura, fundo branco, 3 tabs centralizadas com a ativa em ink com underline
- [ ] CA02: Menu/Home com Hero e Search Bar
  - Cenario: Ao acessar /menu, aparece hero com "LBot Arena" em display-xl, search bar pill com 3 segmentos e search orb Rausch
  - Cenario: Clicar no search orb com "Jogar" selecionado navega para /game
- [ ] CA10 (parcial): Responsividade Mobile
  - Cenario: Em <744px, a top nav colapsa para logo + hamburger
  - Cenario: Em <744px, a search bar colapsa para pill unico

## Testes Esperados

- TopNav aparece em todas as paginas (/menu, /game, /leaderboard, /controls)
- Tabs refletem a rota ativa com underline ink
- Search bar funciona e navega para /game ao clicar no orb
- Mobile: hamburger e search pill aparecem em <744px

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