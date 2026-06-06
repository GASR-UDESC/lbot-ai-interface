# Especificacao de Negocio: Migracao Visual para BMW M Design + Navegacao Global

## Contexto

O frontend LBot DataGen (Angular standalone) atualmente utiliza um tema claro (fundo branco, texto escuro, border-radius arredondado de 14px, tipografia Inter com pesos convencionais). O design system BMW M (documentado em `task/DESIGN-bmw-m.md`) define um tema escuro premium com canvas preto, texto branco, faixa tricolor M como acento de marca, tipografia bold uppercase e cantos retos industriais.

Alem da migracao visual, existem duas lacunas funcionais:
1. A pagina "Modo Controle" nao possui nenhuma forma de navegacao de volta ao menu.
2. O layout da pagina "Jogar" esta visualmente despadronizado em relacao ao "Modo Controle" (sem header de titulo, sem gap entre simulador e chat).

Esta tarefa cobre ambas as frentes: migracao visual completa para o design BMW M e padronizacao funcional/layout das paginas.

---

## Requisitos Funcionais

### RF01 - Top Navigation Global (Top-Nav)

Criar um componente `app-top-nav` reutilizavel, exibido globalmente em TODAS as rotas da aplicacao (menu, jogo, controle, leaderboard).

**Regras:**
- O top-nav deve ficar fixo no topo da viewport (64px de altura, conforme design BMW M).
- Lado esquerdo: logo/nome "LBOT" com a faixa tricolor M como acento visual integrado.
- Centro/direita: links de navegacao (Menu, Jogar, Controle, Leaderboard) em `label-uppercase` (14px, weight 700, tracking 1.5px).
- Link ativo da rota atual deve receber indicador visual (texto branco full opacity vs muted para inativos).
- O top-nav NAO deve sobrepor conteudo; as paginas devem ter padding-top ou o conteudo deve comecar abaixo do nav.
- Em tela < 768px, o nav colapsa para hamburger (overlay tela cheia com fundo preto e faixa M tricolor no topo).
- A faixa tricolor M (azul claro #0066b1 → azul escuro #1c69d4 → vermelho #e22718) deve aparecer como uma linha de 4px na borda inferior do top-nav, servindo como divisor visual entre nav e conteudo.

**Cenarios de erro:**
- Rota nao mapeada: o link nao aparece no nav, mas o nav continua funcional.

---

### RF02 - Layout Padronizado: Modo Controle

A pagina "Modo Controle" (`/controls`) deve manter a estrutura atual de header + grid, mas agora o header interno e substituido/adaptado ao contexto do top-nav global.

**Regras:**
- O top-nav global ja fornece navegacao; portanto, o header interno da pagina de controles permanece como titulo contextual ("MODO CONTROLE" em uppercase) e subtitulo, sem botao de voltar manual.
- O layout grid com gap entre simulador e painel de controles e mantido e padronizado com o game page.
- A faixa tricolor M pode ser usada como divisor horizontal entre o header e o conteudo.

**Cenarios de erro:**
- N/A (layout puro).

---

### RF03 - Layout Padronizado: Modo Jogar (Game)

A pagina "Jogar" (`/game`) deve ser reestruturada para seguir o mesmo padrao visual da pagina "Modo Controle".

**Regras:**
- Adicionar um header contextual (titulo "JOGAR" em uppercase + subtitulo) igual ao header do Modo Controle.
- Aplicar gap/padding entre o simulador e o chat panel, usando o mesmo espacamento do layout de Controle (gap: var(--spacing-lg)).
- O simulador e o chat devem ficar dentro de containers com bordas hairline (1px solid var(--color-hairline)) e border-radius 0 (cantos retos BMW).
- O HUD (nivel, timer, botao reset) permanece sobreposto no simulador como overlay absoluto.
- Os botoes de navegacao do HUD ("← Menu", "Ranking") devem ser removidos ou substituidos pela navegacao do top-nav global.
- O chat panel (app-lbot-chat) mantem a mesma largura (~380px) e o comportimento de scroll atual.

**Cenarios de erro:**
- Se o top-nav global ja provolve navegacao, os links "← Menu" e "Ranking" no HUD tornam-se redundantes e devem ser removidos para evitar duplicacao.

---

### RF04 - Migracao Visual Completa para BMW M (Tema Escuro)

Migrar TODO o design system para o tema escuro BMW M.

**Regras:**
- **Canvas**: Fundo principal muda de `#ffffff` para `#000000` (preto puro).
- **Superficies**: Surface cards usam `#1a1a1a`, surface elevated `#262626`, surface soft `#0d0d0d`.
- **Texto**: Cor primaria de texto `#ffffff` (on-dark); body text `#bbbbbb`; body strong `#e6e6e6`; muted `#7e7e7e`.
- **Hairlines**: `#3c3c3c` para divisores; `#262626` para hairline-strong.
- **Botoes primarios**: Fundo preto ou transparente, texto branco, outline branco 1px, border-radius 0px.
- **Inputs**: Fundo `#1a1a1a`, texto branco, border hairline, border-radius 0px, altura 48px.
- **Cards**: Fundo `#1a1a1a`, border-radius 0px, border 1px волос line `#3c3c3c`.
- Todos os componentes existentes (chat, controles virtuais, leaderboard, menu, victory screen, level transition, confirm modal) devem ser atualizados.

**Cenarios de erro:**
- N/A (migracao visual pura).

---

### RF05 - Tipografia BMW M (Inter como substituto)

Atualizar a tipografia para seguir o design system BMW M, usando Inter como fonte substituta.

**Regras:**
- **Display headlines** (h1, titulos de pagina): UPPERCASE, weight 700, tracking 0px em titulos grandes.
- **Body text**: weight 300 (Light), sentence-case.
- **Button labels**: weight 700, uppercase, tracking 1.5px.
- **Nav links**: 14px, weight 400, tracking 0.5px.
- **Label uppercase**: 14px, weight 700, tracking 1.5px.
- A hierarquia display-xl (80px) → display-lg (56px) → display-md (40px) → display-sm (32px) → title-lg (24px) → title-md (20px) → title-sm (18px) deve ser respeitada conforme escala definida no design BMW M.
- Em displays grandes (display-lg e acima), ajustar tracking para -0.5px para aproximar o visual da BMW Type Next Latin.

**Cenarios de erro:**
- N/A (migracao tipografica pura).

---

### RF06 - Border Radius BMW (Cantos Retos)

Substituir todos os border-radius para seguir o principio BMW: retos por padrao, circulares apenas para icones.

**Regras:**
- **Default**: `border-radius: 0px` para TODOS os botoes, cards, containers, inputs, modais.
- **Excecao**: `border-radius: 9999px` (full) APENAS para botoes circulares de icone (carousel arrows, close buttons, icon actions).
- Revisar todos os componentes e remover `rounded-md`, `rounded-sm`, `rounded-lg`, `rounded-xl` de qualquer elemento que nao seja um botao de icone circular.
- As variaveis CSS `--rounded-*` devem ser atualizadas para refletir: `--rounded-none: 0`, `--rounded-xs: 2px`, `--rounded-sm: 4px`, `--rounded-md: 6px`, `--rounded-full: 9999px`.

**Cenarios de erro:**
- N/A (migracao visual pura).

---

### RF07 - Faixa Tricolor M como Elemento de Marca

Utilizar a faixa tricolor M (#0066b1 → #1c69d4 → #e22718) como divisor e acento de marca.

**Regras:**
- **Top-nav**: Faixa de 4px na borda inferior do header.
- **Divisores de secao**: Usar a faixa tricolor como divisor horizontal entre header contextual e conteudo nas paginas (Controle e Jogar).
- **Restricao**: A tricolor NUNCA deve ser usada como fundo de botao, cor de texto ou superficie. E exclusivamente um marcador de identidade de marca.

**Cenarios de erro:**
- N/A (elemento decorativo controlado).

---

### RF08 - Redesign do Menu Principal

Redesenhar a pagina `/menu` para seguir o estilo editorial BMW M.

**Regras:**
- Canvas preto com titulo display grande em UPPERCASE ("LBOT ARENA" em display-lg ou display-xl).
- Subtitulo em body-md Light (300), sentence-case.
- Botoes de navegacao no estilo BMW: retangulares (border-radius 0), outline branco, uppercase tracking 1.5px, sem sombra.
- Os tres botoes (Jogar, Leaderboard, Modo Controle) podem ser apresentados como cards retangulares (surface-card #1a1a1a) com hairline borders ou como botoes outline diretos.
- Manter icones Lucide nos botoes se possivel, mas estilizados dentro de circulos (border-radius full) conforme BMW `button-icon`.
- Footer minimalista com texto muted (#7e7e7e).

**Cenarios de erro:**
- N/A (layout puro).

---

### RF09 - Atualizacao da Leaderboard Page

Atualizar a pagina `/leaderboard` para o tema BMW M.

**Regras:**
- Aplicar canvas preto, texto branco, surface-cards para os cards de ranking.
- Titulo "LEADERBOARD" em display uppercase.
- Cards de ranking com border-radius 0, fundo surface-card, hairline borders.
- Botoes e links adaptados ao tema BMW (outline, uppercase, tracking).
- Manter a funcionalidade existente (skeleton loading, retry, medalhas).

**Cenarios de erro:**
- N/A (migracao visual pura).

---

### RF10 - Atualizacao dos Componentes de Overlay (Level Transition, Victory Screen, Confirm Modal)

Atualizar os overlays para o tema BMW M.

**Regras:**
- Overlays com fundo rgba(0,0,0,0.85) sobre o canvas preto.
- Texto branco, labels uppercase, botoes retangulares com outline.
- Manter a funcionalidade existente; apenas aplicar o tema visual.
- Confirm modal com botoes BMW style (outline branco, border-radius 0).
- Victory screen com tipografia display e M tricolor como acento (opcional).

**Cenarios de erro:**
- N/A (migracao visual pura).

---

### RF11 - Atualizacao do LBot Chat

Atualizar o componente `app-lbot-chat` para o tema BMW M.

**Regras:**
- Chat header: fundo surface-card, texto branco uppercase, border-bottom hairline.
- Mensagens do usuario: fundo surface-elevated (#262626), texto branco.
- Mensagens do bot: fundo surface-soft (#0d0d0d), texto body (#bbbbbb).
- Input area: fundo surface-card, border hairline, border-radius 0, texto branco.
- Botoes de enviar: outline branco, uppercase, tracking 1.5px.
- Manter toda a funcionalidade (avaliacao por estrelas, observacao, etc.) intacta.

**Cenarios de erro:**
- N/A (migracao visual pura).

---

## Requisitos Nao-Funcionais

- **Performance**: A migracao visual nao deve degradar o tempo de carregamento. A fonte Inter ja esta carregada no projeto.
- **Acessibilidade**: Contraste WCAG AA entre texto branco e fundos escuros deve ser mantido (#fff sobre #000 e contraste maximo; #bbb sobre #000 atende AA para texto grande).
- **Responsividade**: Todos os breakpoints (mobile <768, tablet 768-1024, desktop 1024-1440, wide >1440) devem ser respeitados conforme o design BMW M.
- **Consistencia**: Todas as variaveis CSS devem ser atualizadas em `styles.css` globalmente; componentes nao devem usar cores hardcoded.

---

## Glossario / Definicoes

- **Canvas**: Fundo principal da aplicacao (#000000 no BMW M).
- **Hairline**: Linha divisoria fina de 1px (#3c3c3c).
- **Surface-card**: Superficie elevada para cards (#1a1a1a).
- **Surface-elevated**: Superficie mais clara (#262626).
- **Surface-soft**: Superficie sutilmente diferente do canvas (#0d0d0d).
- **Top-nav**: Barra de navegacao global fixa no topo (64px altura).
- **M tricolor**: Faixa decorativa com as cores #0066b1 (azul claro), #1c69d4 (azul escuro), #e22718 (vermelho).
- **Header contextual**: Header interno de cada pagina com titulo uppercase e subtitulo.
- **HUD**: Heads-Up Display, overlay sobre o simulador com informacoes de jogo (nivel, timer, reset).
- **border-radius 0**: Cantos retos, padrao BMW M para botoes, cards, containers.
- **border-radius full (9999px)**: Cantos circulares, apenas para botoes de icone.

---

## Premissas

- A fonte Inter ja esta configurada no projeto e sera usada como substituta da BMW Type Next Latin.
- O design system BMW M documentado em `task/DESIGN-bmw-m.md` e a fonte de verdade para todas as decisoes visuais.
- O componente `app-robo-simulator` renderiza dentro de um iframe e nao precisa de migracao visual direta (esta fora do escopo).
- O componente `app-virtual-controls` sera migrado visualmente (cores, bordas, tipografia) mas mantendo sua funcionalidade intacta.
- O top-nav global sera um novo componente Angular standalone criado especificamente para esta tarefa.
- A faixa tricolor M sera implementada como um gradiente CSS linear de 3 paradas.
- Os links de navegacao "← Menu" e "Ranking" no HUD do game page serao removidos, pois o top-nav global os substitui.

---

## Fora de escopo

- Redesign do iframe/simulador 3D (robo-simulator) - conteudo externo.
- Funcionalidades novas de jogo, chat ou leaderboard - apenas mudancas visuais e de layout.
- Animacoes ou transicoes entre rotas.
- Configuracao de build/deploy.
- Internacionalizacao (i18n).
- Testes unitarios de componentes visuais (apenas testes de regressao visual manual).
- Optimizacao de performance do simulador 3D.

---

## Cenarios de Aceite

### CA01 - Top Navigation Global visivel em todas as paginas
**Dado** que o usuario esta em qualquer pagina da aplicacao
**Quando** a pagina carrega
**Entao** o top-nav global de 64px aparece fixo no topo com fundo preto, logo LBOT a esquerda, links de navegacao a direita, e faixa tricolor M de 4px na borda inferior.

### CA02 - Navegacao funcional no top-nav
**Dado** que o usuario esta em qualquer pagina
**Quando** clica em um link de navegacao no top-nav (Menu, Jogar, Controle, Leaderboard)
**Entao** a aplicacao navega para a rota correspondente e o link ativo recebe indicador visual (texto branco full).

### CA03 - Top-nav responsivo com hamburger em mobile
**Dado** que o usuario esta em viewport < 768px
**Quando** visualiza o top-nav
**Entao** o nav colapsa para hamburger e ao clicar abre overlay tela cheia com fundo preto, faixa M tricolor no topo, e links de navegacao.

### CA04 - Layout padronizado do Modo Controle
**Dado** que o usuario navega para `/controls`
**Quando** a pagina carrega
**Entao** o top-nav global aparece no topo e abaixo dele o header contextual "MODO CONTROLE" em uppercase com subtitulo, seguido do grid com gap/padding entre simulador e painel de controles.

### CA05 - Layout padronizado do Modo Jogar
**Dado** que o usuario navega para `/game`
**Quando** a pagina carrega
**Entao** o top-nav global aparece no topo e abaixo dele o header contextual "JOGAR" em uppercase com subtitulo, seguido do layout com gap/padding entre simulador e chat panel, seguindo o mesmo padrao visual do Modo Controle.

### CA06 - Navegacao redundante removida do HUD
**Dado** que o usuario esta na pagina de jogo
**Quando** a partida esta em andamento (fase 'playing')
**Entao** o HUD mostra apenas nivel, timer e botao de reset, SEM os links "← Menu" e "Ranking" (que agora estao no top-nav global).

### CA07 - Tema escuro BMW M aplicado em toda a aplicacao
**Dado** que o usuario esta em qualquer pagina
**Quando** visualiza a aplicacao
**Entao** o fundo e preto (#000000), o texto principal e branco (#ffffff), as superficies elevadas usam #1a1a1a, e os hairlines usam #3c3c3c.

### CA08 - Tipografia BMW M com Inter
**Dado** que o usuario esta em qualquer pagina
**Quando** visualiza titulos de pagina
**Entao** os titulos estao em uppercase, weight 700, e body text esta em weight 300 (Light), conforme a hierarquia tipografica BMW M.

### CA09 - Cantos retos BMW em todos os componentes
**Dado** que o usuario esta em qualquer pagina
**Quando** visualiza botoes, cards, inputs e containers
**Entao** todos tem border-radius 0px (exceto icones circulares que tem border-radius full).

### CA10 - Faixa tricolor M como acento de marca
**Dado** que o usuario esta em qualquer pagina
**Quando** visualiza o top-nav
**Entao** a faixa tricolor M de 4px aparece na borda inferior do nav. Nas paginas de Controle e Jogar, a faixa tambem aparece como divisor entre header e conteudo.

### CA11 - Faixa tricolor nao usada como fundo ou texto
**Dado** que o usuario visualiza qualquer componente
**Quando** inspeciona cores de fundo, bordas e texto
**Entao** a tricolor M nao aparece como background de botoes, cor de texto ou superficie - apenas como faixa divisoria e acento no nav.

### CA12 - Menu redesenhado no estilo BMW M
**Dado** que o usuario navega para `/menu`
**Quando** a pagina carrega
**Entao** o menu exibe canvas preto, titulo "LBOT ARENA" em display uppercase, botoes retangulares com outline branco e labels uppercase, sem bordas arredondadas.

### CA13 - Leaderboard atualizado para tema escuro
**Dado** que o usuario navega para `/leaderboard`
**Quando** a pagina carrega
**Entao** a leaderboard exibe fundo preto, cards com surface-card, border-radius 0, texto branco e titulo uppercase.

### CA14 - Chat atualizado para tema escuro BMW M
**Dado** que o usuario esta na pagina de jogo com chat aberto
**Quando** visualiza o chat panel
**Entao** o chat header tem fundo surface-card com texto branco, mensagens do usuario em surface-elevated, mensagens do bot em surface-soft, e input area com border hairline e border-radius 0.

### CA15 - Overlays (Level Transition, Victory, Confirm) atualizados
**Dado** que o usuario visualiza qualquer overlay durante o jogo
**Quando** o overlay aparece
**Entao** o fundo e rgba(0,0,0,0.85), texto branco, botoes retangulares com outline, labels uppercase.

### CA16 - Responsividade mantida em todos os breakpoints
**Dado** que o usuario redimensiona o navegador
**Quando** esta em mobile (<768px), tablet (768-1024px) ou desktop (>1024px)
**Entao** o layout se adapta corretamente: card grids reduzem colunas, nav colapsa em hamburger no mobile, chat panel empilha verticalmente no mobile.