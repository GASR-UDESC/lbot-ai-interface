# Especificacao de Negocio: Migracao de Estilizacao BMW para Coinbase

## Contexto

O `lbot-datagen-frontend` (projeto Angular em `1.coleta-de-dados/lbot-datagen/lbot-datagen-frontend`) utiliza atualmente uma estilizacao inspirada na BMW M Motorsport: dark theme (canvas preto), tricolor stripe (`.m-stripe`), sharp corners (0px border-radius), tipografia uppercase com weight 700 e letter-spacing largo.

O objetivo desta tarefa e migrar completamente a identidade visual do frontend para o design system da Coinbase, conforme documentado em `DESIGN-coinbase.md`. A migracao deve transformar o app em um light theme com canvas branco, adotar a paleta Coinbase Blue como unica cor de acao, border-radius pill para botoes e xl para cards, tipografia weight 400 em display, e eliminar todos os elementos visuais BMW.

## Requisitos Funcionais

### RF01 - Migracao do Design Token System (styles.css)

Substituir todos os design tokens BMW no arquivo `src/styles.css` pelos tokens do design system Coinbase, usando Inter como substituta de CoinbaseDisplay/CoinbaseSans e JetBrains Mono como substituta de CoinbaseMono.

**Regras:**
- Substituir todas as variaveis CSS `--color-*` pelos valores Coinbase (canvas `#ffffff`, ink `#0a0b0d`, primary `#0052ff`, etc.)
- Substituir `--spacing-*` pelos valores Coinbase (xxs 4px ate section 96px)
- Substituir `--rounded-*` pela escala Coinbase (xs 4px, sm 8px, md 12px, lg 16px, xl 24px, pill 100px, full 9999px)
- Substituir `--typography-*` pelos valores Coinbase (display weight 400, letter-spacing negativo, body weight 400/600/700)
- Adicionar tokens `--color-semantic-up` (#05b169) e `--color-semantic-down` (#cf202f) para feedback de jogo
- Adicionar tokens para surface-dark (#0a0b0d) e surface-dark-elevated (#16181c) para dark heroes
- Manter a font-family Inter com fallback stack do Coinbase
- Adicionar JetBrains Mono como font-family para dados numericos/tabulares

**Cenarios de erro:**
- Token nao mapeado: usar o valor Coinbase mais proximo e documentar no codigo

### RF02 - Remocao Completa da M-Stripe BMW

Eliminar todos os elementos `.m-stripe` e suas referencias em HTML e CSS.

**Regras:**
- Remover a classe `.m-stripe` do `styles.css` global
- Remover `<div class="m-stripe"></div>` de todos os templates HTML: `top-nav.html`, `game.page.html`, `controls.page.html`
- Remover referencias CSS a `.m-stripe` em `top-nav.css`, `game.page.css`, `controls.page.css`
- Remover os tokens `--color-m-blue-light`, `--color-m-blue-dark`, `--color-m-red`
- Nao substituir por nenhum elemento decorativo equivalente

**Cenarios de erro:**
- Referencia residual a m-stripe: build deve completar sem erros visuais

### RF03 - Migracao dos Botoes para Pill Style

Substituir todos os botoes quadrados (border-radius 0, uppercase, weight 700) pelo padrao Coinbase pill (border-radius 100px, weight 600, sem uppercase).

**Regras:**
- Atualizar `.btn-outline` no `styles.css`: border-radius `var(--rounded-pill)`, font-weight 600, text-transform none, letter-spacing 0, padding 12px 20px, height 44px
- Atualizar `.btn-filled` no `styles.css`: background `var(--color-primary)` (#0052ff), color `var(--color-on-primary)` (#ffffff), border-radius `var(--rounded-pill)`, font-weight 600, text-transform none
- Adicionar estado active/pressed: background `var(--color-primary-active)` (#003ecc)
- Adicionar estado disabled: background `var(--color-primary-disabled)` (#a8b8cc)
- Botoes inline (text links) usam `var(--color-primary)` como cor de texto
- Todos os botoes de acao nos componentes (retry, reset, save, play again, back) devem seguir o novo padrao

**Cenarios de erro:**
- Botao com estado disabled: cursor not-allowed, background faded

### RF04 - Migracao da Tipografia para Estilo Editorial Coinbase

Substituir a tipografia BMW (uppercase, weight 700, letter-spacing largo) pelo estilo editorial Coinbase (weight 400 em display, sem uppercase, letter-spacing negativo).

**Regras:**
- Display headings: weight 400, letter-spacing negativo (-1px a -2px), sem uppercase
- Body text: weight 400, line-height 1.5
- Body strong/emphasis: weight 700
- Botoes e nav links: weight 600, sem uppercase, letter-spacing 0
- Titulos de pagina: usar `--typography-display-sm-size` (36px) ou `--typography-title-lg-size` (32px)
- Nav links: weight 500, size 14px
- Remover todos os `text-transform: uppercase` dos componentes
- Remover todos os `letter-spacing: 1.5px` dos botoes e labels

**Cenarios de erro:**
- Texto que nao se encaixa em display/body: usar title-md (18px/600) como fallback

### RF05 - Migracao do Top Navigation para Light Theme

Transformar a top nav de dark (canvas preto) para light (canvas branco).

**Regras:**
- Background: `var(--color-canvas)` (#ffffff)
- Text color nav links: `var(--color-body)` (#5b616e)
- Nav link active: `var(--color-ink)` (#0a0b0d)
- Logo "LBOT": `var(--color-ink)`, font-weight 600, sem uppercase
- Height: 64px (manter)
- Hamburger button: background `var(--color-surface-strong)` (#eef0f3), border-radius `var(--rounded-full)`
- Mobile overlay: background `var(--color-canvas)` (#ffffff), links sem uppercase
- Remover `.m-stripe` da nav e do overlay mobile

**Cenarios de erro:**
- Contraste insuficiente em light theme: verificar que text colors atendem WCAG AA

### RF06 - Migracao da Pagina Menu para Light Theme

Transformar a pagina Menu de dark para light theme com cards estilo Coinbase.

**Regras:**
- Background: `var(--color-canvas)` (#ffffff)
- Menu cards: background `var(--color-surface-card)` (#ffffff), border 1px `var(--color-hairline)` (#dee1e6), border-radius `var(--rounded-xl)` (24px), padding 32px
- Card hover: soft drop shadow `0 4px 12px rgba(0, 0, 0, 0.04)`
- Icon circles: background `var(--color-surface-strong)` (#eef0f3), border-radius `var(--rounded-full)`
- Titulo: weight 400, sem uppercase
- Subtitulo: `var(--color-body)`, weight 400

**Cenarios de erro:**
- Card sem borda em fundo branco: usar hairline border como separador

### RF07 - Migracao da Pagina Leaderboard para Light Theme

Transformar a pagina Leaderboard com cards estilo Coinbase feature-card.

**Regras:**
- Background: `var(--color-canvas)` (#ffffff)
- Leaderboard cards: background `var(--color-surface-card)`, border-radius `var(--rounded-xl)` (24px), padding 32px, border 1px `var(--color-hairline)`
- Card hover: border-color muda para `var(--color-body)` ou soft shadow
- Medalhas/rank: manter emojis, ajustar cores para ink/body/muted
- Tempos (dados numericos): usar JetBrains Mono via `--typography-number-display`
- Titulo da pagina: weight 400, sem uppercase, letter-spacing negativo
- Back button: tertiary text style (color `var(--color-primary)`)

**Cenarios de erro:**
- Grid responsivo: manter breakpoints existentes, ajustar gap para 24px

### RF08 - Migracao da Pagina Game com Dark Hero Pattern

Aplicar o dark hero pattern do Coinbase na pagina Game, mantendo a funcionalidade de jogo.

**Regras:**
- Page header: background `var(--color-surface-dark)` (#0a0b0d), text `var(--color-on-dark)` (#ffffff), padding 96px (ou adaptado para app context)
- Titulo "Jogar": weight 400, sem uppercase, display-sm (36px)
- Subtitulo: `var(--color-on-dark-soft)` (#a8acb3)
- Simulator panel: background `var(--color-canvas)` (#ffffff) ou `var(--color-surface-soft)` (#f7f7f7)
- Chat panel: background `var(--color-surface-soft)`, border-left 1px `var(--color-hairline)`
- HUD overlay: background `var(--color-surface-dark-elevated)` (#16181c), border-radius `var(--rounded-xl)` (24px), text `var(--color-on-dark)`
- HUD timer: JetBrains Mono para numeros
- HUD reset button: button-outline-on-dark style (transparent, white border, pill)
- Remover `.m-stripe` do page header

**Cenarios de erro:**
- HUD com baixa visibilidade: garantir contraste AAA em texto sobre dark surface

### RF09 - Migracao da Pagina Controls com Dark Hero Pattern

Aplicar o dark hero pattern na pagina Controls, similar a pagina Game.

**Regras:**
- Page header: mesmo pattern da pagina Game (dark hero)
- Virtual controls panel: adaptar para light theme nos controles individuais
- Remover `.m-stripe` do page header
- Botoes de controle: pill style, border-radius `var(--rounded-pill)`

**Cenarios de erro:**
- Controles virtuais com baixa usabilidade em light: ajustar contraste dos botoes

### RF10 - Migracao dos Componentes de Jogo

Adaptar todos os componentes de jogo ao estilo Coinbase mantendo funcionalidade.

**Regras:**
- **Chat (lbot-chat)**: background `var(--color-surface-card)` (#ffffff), border-radius `var(--rounded-xl)`, inputs com border-radius `var(--rounded-md)` (12px), botao enviar pill style
- **Victory screen**: overlay com scrim `var(--color-scrim)`, card central `var(--rounded-xl)` (24px), botoes pill, tempos em JetBrains Mono
- **Level transition**: overlay dark, card `var(--rounded-xl)`, botoes pill
- **Confirm modal**: card `var(--rounded-xl)` (24px), botoes pill (primary + secondary)
- **Simulator frame**: border-radius `var(--rounded-xl)` para o container do iframe

**Cenarios de erro:**
- Overlay com conteudo ilegivel: ajustar scrim opacity e card background

### RF11 - Adicao de Cores Semanticas para Feedback

Incluir tokens de cores semanticas para feedback positivo/negativo no jogo.

**Regras:**
- `--color-semantic-up` (#05b169): feedback positivo (acerto, sucesso, nivel completo)
- `--color-semantic-down` (#cf202f): feedback negativo (erro, falha, tempo esgotado)
- Usar apenas como cor de texto, nunca como background fill (conforme design Coinbase)
- Aplicar em: mensagens de feedback no chat, indicadores de nivel completo, indicadores de erro

**Cenarios de erro:**
- Cor semantica em fundo escuro (dark hero): usar versao mais clara ou on-dark variant

## Requisitos Nao-Funcionais

- **Performance**: A migracao e puramente CSS/HTML. Sem impacto em bundle size ou runtime performance.
- **Responsividade**: Manter todos os breakpoints existentes (744px, 1128px). Ajustar valores de spacing e typography para mobile conforme documento Coinbase (hero h1 80->40px, feature cards 1-up em mobile).
- **Acessibilidade**: Todos os botoes pill com height minimo 44px (WCAG AAA). Touch targets em asset icons com padding 8px para zona efetiva de 48px.
- **Browser support**: Mesmos browsers suportados atualmente (Chrome, Firefox, Safari, Edge modernos).
- **Build**: O build Angular deve completar sem erros ou warnings apos a migracao.

## Glossario / Definicoes

- **Design Token**: Variavel CSS que define um valor de design reutilizavel (cor, spacing, typography, border-radius)
- **M-Stripe**: Faixa decorativa tricolor (azul claro, azul escuro, vermelho) inspirada na BMW M Motorsport, usada como elemento visual no topo de paginas e nav
- **Pill button**: Botao com border-radius 100px (totalmente arredondado), assinatura do design Coinbase
- **Dark hero band**: Secao full-bleed com fundo escuro (#0a0b0d) usada como destaque editorial
- **Editorial spacing**: Espacamento generoso (96px entre secoes) que remete a publicacoes editoriais
- **Surface**: Camada de fundo que define elevacao visual (canvas, soft, strong, dark, dark-elevated)
- **Hairline**: Borda sutil de 1px usada como separador visual entre elementos

## Premissas

- As fontes Inter e JetBrains Mono ja estao disponiveis via Google Fonts (Inter esta carregada no index.html)
- O framework Angular e a estrutura de componentes nao serao alterados, apenas a estilizacao
- Nao ha testes visuais automatizados (snapshot tests) que precisem ser atualizados
- O favicon e outros assets estaticos nao fazem parte do escopo de migracao
- O documento DESIGN-coinbase.md e a fonte unica de verdade para os valores do design system Coinbase

## Fora de escopo

- Migracao de estilizacao dos outros frontends (lbot-simulator-web, lbot-client)
- Alteracao na estrutura de componentes Angular (templates, logica, routing)
- Implementacao de dark mode toggle (apenas light theme + dark heroes pontuais)
- Animacoes e transicoes avancadas (fora do escopo do documento Coinbase)
- Fontes licenciadas Coinbase originais (serao usados substitutos Inter + JetBrains Mono)
- In-product trading surfaces (order book, charts) - nao existem no app

## Cenarios de Aceite

### CA01 - Design tokens migrados
**Dado** que o arquivo `styles.css` foi atualizado com tokens Coinbase
**Quando** o app e carregado
**Entao** todas as cores, spacing, border-radius e tipografia refletem o design system Coinbase (canvas branco, primary #0052ff, pill buttons, xl cards)

### CA02 - M-Stripe removida
**Dado** que todos os elementos `.m-stripe` foram removidos
**Quando** o usuario navega por qualquer pagina
**Entao** nenhum elemento tricolor BMW e visivel, e nao ha espacos vazios ou layout quebrado

### CA03 - Light theme aplicado
**Dado** que o tema foi migrado para light
**Quando** o usuario acessa Menu, Leaderboard ou qualquer pagina
**Entao** o fundo e branco (#ffffff), textos sao escuros (#0a0b0d / #5b616e), e a leitura e confortavel

### CA04 - Dark hero nas paginas Game e Controls
**Dado** que o dark hero pattern foi aplicado
**Quando** o usuario acessa as paginas Game ou Controls
**Entao** o header da pagina tem fundo escuro (#0a0b0d) com texto branco, criando destaque editorial

### CA05 - Botoes pill em todo o app
**Dado** que todos os botoes foram migrados
**Quando** o usuario interage com qualquer botao
**Entao** o botao tem border-radius 100px (pill), font-weight 600, sem uppercase, e o botao primario e azul (#0052ff)

### CA06 - Tipografia editorial
**Dado** que a tipografia foi migrada
**Quando** o usuario le titulos e textos
**Entao** display titles tem weight 400, sem uppercase, letter-spacing negativo; body text tem weight 400, line-height 1.5

### CA07 - Cores semanticas em feedback
**Dado** que tokens semanticos foram adicionados
**Quando** o usuario recebe feedback positivo ou negativo no jogo
**Entao** feedback positivo usa verde (#05b169) como cor de texto, feedback negativo usa vermelho (#cf202f)

### CA08 - Responsividade mantida
**Dado** que a migracao foi aplicada
**Quando** o usuario acessa o app em mobile (< 744px), tablet ou desktop
**Entao** o layout se adapta corretamente, botoes mantem touch target minimo 44px, e grids colapsam adequadamente

### CA09 - Build sem erros
**Dado** que todas as alteracoes foram aplicadas
**Quando** o comando `ng build` e executado
**Entao** o build completa sem erros ou warnings relacionados a estilos

### CA10 - Dados numericos em mono
**Dado** que JetBrains Mono foi adicionado para dados numericos
**Quando** o usuario ve tempos no leaderboard ou timer no HUD
**Entao** os numeros sao renderizados em JetBrains Mono com font-variant-numeric tabular-nums
