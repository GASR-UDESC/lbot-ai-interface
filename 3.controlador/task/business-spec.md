# Especificacao de Negocio: Migracao UI Simulador para Estilo Coinbase

## Contexto

O `lbot-simulator-web` e um simulador standalone em React + Vite + TypeScript + Three.js para executar comandos LBML via interface web ou HTTP. Atualmente, sua UI possui um tema dark tech (fundos azul-escuros #07111f, gradientes, blur glassmorphism) que difere da identidade visual institucional adotada no projeto `lbot-datagen-frontend` (Angular). Este projeto de migracao visa aplicar o design system "Coinbase" — branco canvas, cards elevados, botões pill azuis (#0052ff), tipografia Inter, e spacing editorial generoso — ao simulador, reestruturando o layout para refletir a filosofia de design do projeto de referência.

## Requisitos Funcionais

### RF01 - Migracao para tema light Coinbase

Toda a interface deve migrar do tema dark atual para o tema light do design Coinbase.

**Regras:**
- O fundo da pagina (`body`, `#root`) deve usar `var(--color-canvas)` = `#ffffff`.
- Cards e paineis devem usar `var(--color-surface-card)` = `#ffffff` com borda `1px solid var(--color-hairline)` = `#dee1e6`.
- Nao devem existir gradientes azul-escuros, glassmorphism, ou backdrop-filter blur.
- A cor de texto principal deve ser `var(--color-ink)` = `#0a0b0d`.
- A cor de texto secundaria (descricoes, labels) deve ser `var(--color-body)` = `#5b616e`.

**Cenarios de erro:**
- Nenhum. Este requisito e puramente visual.

### RF02 - Reestruturacao do layout

O layout deve ser reestruturado para seguir a filosofia do design Coinbase: sidebar light + canvas 3D como hero principal.

**Regras:**
- O header atual (titulo + callout HTTP) deve ser convertido em um **top-nav light** (altura 64px, background #ffffff, texto #0a0b0d).
- Abaixo do top-nav, o layout deve usar uma **grid de 2 colunas**:
  - **Sidebar esquerda (light):** Cards brancos empilhados contendo `StatusPanel`, `CameraPreview`, e `CommandPanel`.
  - **Area principal direita:** O canvas 3D (`SimulatorCanvas`) deve ocupar a area principal, estilizado como um grande card ou area hero com bordas `var(--rounded-xl)` (24px) e borda hairline.
- O spacing entre secoes e cards deve seguir os tokens do design: `var(--spacing-lg)` (24px) entre cards, `var(--spacing-section)` (96px) entre grandes secoes (se houver).
- O grid deve respeitar a max-width editorial de ~1200px centralizada quando em desktop wide (>1280px).

**Cenarios de erro:**
- Se o canvas 3D falhar a inicializacao (WebGL nao disponivel), a area principal deve exibir o `ErrorBoundary` (RF03) sem quebrar o layout da sidebar.

### RF03 - Tratamento de erros (ErrorBoundary e WebGL)

Erros de runtime (WebGL, React) devem ser apresentados como cards de erro no estilo Coinbase.

**Regras:**
- O `ErrorBoundary` (React) e erros de inicializacao WebGL (`simulator-canvas--error`) devem renderizar como um card branco (`#ffffff`) com borda `1px solid var(--color-semantic-down)` = `#cf202f`.
- O texto de erro deve usar `var(--color-semantic-down)` para o titulo/mensagem principal.
- O botao de "Recarregar" ou "Tentar novamente" deve usar o estilo `button-secondary-light` (pill cinza #eef0f3).
- Deve manter o padding generoso (32px) e bordas arredondadas `var(--rounded-xl)` (24px).

**Cenarios de erro:**
- Erro WebGL: card vermelho com mensagem "Falha ao inicializar WebGL" + botao de recarregar.
- Erro React generico: card vermelho com mensagem de fallback + botao de retry.

### RF04 - Estilizacao dos componentes existentes

Todos os componentes React existentes devem ser reestilizados com os tokens Coinbase.

**Regras:**
- **StatusPanel:** Card branco (`#ffffff`), header com titulo `title-md` (18px/600) e badge de conexao (pill: connected = verde #05b169 texto, disconnected = vermelho #cf202f texto). Status rows com background `var(--color-surface-soft)` (#f7f7f7) e bordas `var(--rounded-lg)` (16px). Mensagens de status (`idle`, `info`, `error`) devem manter as cores semanticas (verde, vermelho) mas com background suave (surface-soft) e texto semantico, sem glassmorphism.
- **CommandPanel:** Card branco. Input textarea deve usar `var(--color-canvas)` (#ffffff) background, borda `var(--color-hairline)` (#dee1e6), `var(--rounded-md)` (12px) e focus state com borda `2px solid var(--color-primary)` (#0052ff). Botoes "Executar", "Reset", "Vista Normal/3a Pessoa" devem ser pills (`var(--rounded-pill)` 100px). "Executar" = `button-primary` (azul #0052ff, texto branco). "Reset" e "Vista Normal" = `button-secondary-light` (cinza #eef0f3, texto #0a0b0d). Botoes desabilitados usam `var(--color-primary-disabled)` (#a8b8cc).
- **CameraPreview:** Deve ser renderizado como um **product-ui-card-dark** (background `var(--color-surface-dark-elevated)` #16181c, texto branco, bordas `var(--rounded-xl)` 24px, padding 32px). O preview frame interno deve manter aspect-ratio 4/3 e bordas arredondadas.
- **History (historico de comandos):** Cada item deve ser um row com background `var(--color-surface-soft)` (#f7f7f7), fonte mono (se disponivel), e bordas arredondadas. Header "Historico" como `title-sm` (16px/600).
- **SimulatorCanvas (area do canvas):** O container do canvas deve ter background `var(--color-surface-soft)` (#f7f7f7) ou `var(--color-canvas)` (#ffffff) com borda `var(--color-hairline)` e bordas arredondadas `var(--rounded-xl)` (24px). O canvas WebGL em si nao deve ter bordas arredondadas (overflow hidden no container).

**Cenarios de erro:**
- Se a fonte Inter nao estiver carregada, o fallback do sistema (`-apple-system, system-ui, Roboto, sans-serif`) deve ser aplicado.

### RF05 - Top Navigation

Adicionar uma top-nav light no estilo Coinbase.

**Regras:**
- Altura: 64px. Background: `var(--color-canvas)` (#ffffff).
- Texto: `var(--color-ink)` (#0a0b0d), fonte `nav-link` (14px/500).
- Layout: Logo/titulo "LBot Simulator Web" a esquerda. Links/menu (se houver) ao centro. Callout HTTP estilizado como card de codigo (surface-strong, mono, borda hairline) a direita, ou simplificado como texto/link.
- Borda inferior: `1px solid var(--color-hairline)` (#dee1e6).
- A top-nav deve ser fixa ou sticky no topo da pagina (opcional, mas preferencial para consistencia).

**Cenarios de erro:**
- Nenhum.

### RF06 - Micro-interacoes (hover, active, focus, disabled)

Implementar todos os estados de interacao do design Coinbase.

**Regras:**
- **Cards:** hover deve aplicar `box-shadow: var(--shadow-card-hover-float)` (`0 4px 12px rgba(0,0,0,0.04)`). Transition: `box-shadow 0.2s ease`.
- **Botoes primarios:** hover = background `var(--color-primary-active)` (#003ecc). Active = scale(0.98) ou darken. Transition: `background 0.2s ease`.
- **Botoes secundarios:** hover = background darken leve (ex: `var(--color-surface-strong)` com overlay). Transition: `background 0.2s ease`.
- **Inputs (textarea):** focus = borda `2px solid var(--color-primary)` (#0052ff). Transition: `border-color 0.2s ease`.
- **Disabled:** opacity reduzida (0.55), cursor `not-allowed`, sem hover effects.
- **Menu/nav links:** hover = texto `var(--color-primary)` (#0052ff) ou underline.

**Cenarios de erro:**
- Nenhum.

### RF07 - Responsividade (breakpoints Coinbase)

A UI deve ser responsiva seguindo os breakpoints do design Coinbase.

**Regras:**
- **Mobile (<640px):** Grid 2-colunas colapsa para 1 coluna (stack). Sidebar cards empilham verticalmente. Canvas 3D ocupa largura total. Top-nav pode colapsar (hamburger) se houver muitos itens, ou manter-se compacta. Cards ficam `rounded-lg` (16px) ou `rounded-xl` (24px) mas com padding reduzido (16px). Fonte display reduzida proporcionalmente.
- **Tablet (640–1024px):** Grid pode manter 2 colunas mas com sidebar mais estreita (minmax 280px). Canvas ajusta. Cards com padding 24px.
- **Desktop (1024–1280px):** Grid full 2 colunas. Sidebar ~320-420px. Canvas ocupa resto. Cards com padding 32px.
- **Wide (>1280px):** Conteudo capa em ~1200px centralizado. Canvas pode ter largura maxima controlada.
- A responsividade atual do simulador (colapso em 1100px) deve ser ajustada para os breakpoints acima.

**Cenarios de erro:**
- Em mobile, o canvas 3D deve continuar funcionando (touch events se aplicavel) e a CameraPreview deve manter aspect-ratio.

### RF08 - Terminologia e conteudo

Manter a terminologia e conteudo textual atual do simulador.

**Regras:**
- Titulos, labels, placeholders, mensagens de status, e historico devem manter os textos originais (ex: "Comandos LBML", "Sequencia", "Posicao X", "Posicao Z", "Rotacao", "Comando", "Servidor", "HTTP", "Conectado", "Desconectado", "Executar", "Reset", "Vista Normal", "3a Pessoa", "Nenhum comando executado ainda.", etc.).
- O callout HTTP deve continuar exibindo `POST /api/commands` e `POST /api/reset` como texto de codigo.
- Nenhum texto deve ser alterado ou traduzido (a nao ser que ja exista uma traducao em portugues, que deve ser mantida).

**Cenarios de erro:**
- Nenhum.

### RF09 - Tokens CSS e variaveis

O CSS deve ser reescrito para usar variaveis CSS alinhadas com o design Coinbase, similar ao `styles.css` do lbot-datagen.

**Regras:**
- Definir `:root` com todas as variaveis de cor, espacamento, bordas, sombras e tipografia conforme o design document.
- Substituir todos os valores hardcoded (hex, px, font-size) nos componentes pelas variaveis CSS.
- Fonte: `Inter, -apple-system, system-ui, Roboto, 'Helvetica Neue', sans-serif`.
- Nao usar `color-scheme: dark`. O sistema deve ser light.
- O CSS deve ser modular (preferencialmente manter `styles.css` central ou dividir por componente se o projeto assim evoluir; para esta tarefa, manter centralizado no `styles.css` e ajustar classes existentes e possivelmente adicionar novas).

**Cenarios de erro:**
- Nenhum.

## Requisitos Nao-Funcionais

- **RNF01 - Performance:** A remocao de backdrop-filter blur e gradientes deve melhorar ou manter a performance de renderizacao, especialmente em mobile.
- **RNF02 - Compatibilidade:** A UI deve continuar funcionando nos mesmos navegadores suportados (WebGL-enabled browsers). Nenhuma dependencia de fonte externa (Inter) pode ser um ponto de falha critico; fallback deve ser robusto.
- **RNF03 - Manutencao:** O CSS deve ser facil de manter e extender. Usar variaveis CSS e classes semanticas.
- **RNF04 - Acessibilidade:** Cores devem manter contraste WCAG AA (o design Coinbase ja e pensado para isso). Focus states devem ser visiveis. Botoes devem ter altura minima 44px (CTA primario) e 44px (secundarios), atingindo WCAG AAA para touch targets.

## Glossario / Definicoes

- **LBML:** Linguagem de marcacao de baixo nivel usada para comandos do robo (ex: `D40F;R90L;`).
- **Canvas 3D:** Area de renderizacao WebGL (Three.js) que simula o robo e a arena.
- **CameraPreview:** Miniatura da visao em primeira pessoa do robo (render target WebGL).
- **CommandPanel:** Painel de entrada de comandos LBML e controles (Executar, Reset, Camera).
- **StatusPanel:** Painel de exibicao de estado (posicao, rotacao, conexao, servidor).
- **Top-nav light:** Barra de navegacao superior no tema claro (background branco, texto escuro, 64px altura).
- **Product-ui-card-dark:** Card escuro (#16181c) com texto branco, usado para elementos de destaque (aqui, o CameraPreview).
- **Button-primary:** Botao pill azul (#0052ff) para acao principal.
- **Button-secondary-light:** Botao pill cinza (#eef0f3) para acoes secundarias.
- **Hairline:** Borda divisoria sutil de 1px (#dee1e6).
- **Semantic colors:** Verde (#05b169) para up/positivo/sucesso, Vermelho (#cf202f) para down/negativo/erro.

## Premissas

- **P01:** A stack tecnologica (React 19, Vite, TypeScript, Three.js) nao sera alterada. Apenas CSS e possivelmente estrutura HTML leve dos componentes React.
- **P02:** O projeto de referencia `lbot-datagen-frontend` ja implementa o design system Coinbase com variaveis CSS e pode ser consultado como referencia de implementacao.
- **P03:** A fonte Inter ja esta disponivel ou sera carregada via Google Fonts / CDN. Nao e necessario licenciar CoinbaseDisplay/CoinbaseSans.
- **P04:** A logica de negocio (protocolo HTTP, eventos, simulacao WebGL) permanece inalterada. Esta tarefa e apenas de UI/UX.
- **P05:** O usuario deseja que a UI seja reestruturada (nao apenas troca de cores) para seguir a filosofia de layout do design Coinbase.

## Fora de escopo

- **F01:** Nao criar novas paginas ou rotas. O simulador continua sendo uma SPA unica.
- **F02:** Nao alterar o backend (server/index.ts, scene-renderer.ts, sensors.ts). Apenas frontend.
- **F03:** Nao adicionar novas funcionalidades (ex: autenticacao, leaderboard, modo multiplayer). Apenas migracao visual.
- **F04:** Nao implementar animacoes complexas (transicoes de pagina, animacoes de entrada). Apenas micro-interacoes (hover, focus, active).
- **F05:** Nao alterar a terminologia ou conteudo textual (labels, mensagens). Manter o portugues atual.
- **F06:** Nao adicionar dark mode toggle. O tema sera light unico.
- **F07:** Nao alterar o comportamento do WebGL ou da simulacao fisica. Apenas o container e estilo visual.

## Cenarios de Aceite

### CA01 - Tema light aplicado corretamente
**Dado** que o usuario acessa o simulador
**Quando** a pagina carrega
**Entao** o fundo da pagina deve ser branco (#ffffff)
**E** os cards devem ser brancos com borda 1px #dee1e6
**E** nao deve haver gradientes azul-escuros ou blur glassmorphism

### CA02 - Layout reestruturado com sidebar e hero
**Dado** que o simulador esta carregado em desktop
**Quando** o usuario visualiza a pagina
**Entao** deve haver uma top-nav de 64px no topo
**E** a sidebar esquerda deve conter cards brancos empilhados (Status, CameraPreview, CommandPanel)
**E** a area direita deve conter o canvas 3D como area principal

### CA03 - Componentes reestilizados com tokens Coinbase
**Dado** que o simulador esta carregado
**Quando** o usuario interage com os componentes
**Entao** o StatusPanel deve ter rows com background #f7f7f7 e bordas arredondadas
**E** o CommandPanel deve ter input com borda #dee1e6 e focus azul #0052ff
**E** o CameraPreview deve ser um card escuro (#16181c) com bordas 24px
**E** os botoes devem ser pills (100px border-radius)

### CA04 - Micro-interacoes funcionam
**Dado** que o usuario passa o mouse sobre um card
**Quando** o hover e ativado
**Entao** o card deve exibir sombra 0 4px 12px rgba(0,0,0,0.04)
**E** o botao primario deve escurecer para #003ecc no hover
**E** o input deve exibir borda 2px azul no focus

### CA05 - Responsividade em mobile
**Dado** que o usuario acessa o simulador em uma tela de 600px
**Quando** a pagina e renderizada
**Entao** o layout deve colapsar para 1 coluna
**E** os cards devem ocupar a largura total
**E** o canvas 3D deve manter proporcao e funcionar

### CA06 - Erro WebGL estilizado
**Dado** que o WebGL falha a inicializacao
**Quando** o erro e exibido
**Entao** a mensagem deve aparecer em um card branco com borda 1px #cf202f
**E** o texto deve ser #cf202f
**E** deve haver um botao pill cinza para recarregar

### CA07 - Terminologia preservada
**Dado** que o simulador esta carregado
**Quando** o usuario le os labels
**Entao** os textos "Comandos LBML", "Sequencia", "Posicao X", "Executar", "Reset" devem estar presentes
**E** o callout HTTP deve mostrar POST /api/commands e POST /api/reset

### CA08 - Botoes estilizados corretamente
**Dado** que o CommandPanel esta visivel
**Quando** o usuario observa os botoes
**Entao** "Executar" deve ser um pill azul (#0052ff) com texto branco
**E** "Reset" e "Vista Normal/3a Pessoa" devem ser pills cinza (#eef0f3) com texto escuro
**E** botoes desabilitados devem ter opacidade reduzida e cursor not-allowed

### CA09 - Historico de comandos estilizado
**Dado** que comandos foram executados
**Quando** o historico e exibido
**Entao** cada item deve ter background #f7f7f7, fonte mono, e bordas arredondadas
**E** o header "Historico" deve estar em 16px/600

### CA10 - Top-nav presente
**Dado** que o simulador esta carregado
**Quando** o usuario visualiza o topo da pagina
**Entao** deve existir uma barra de 64px com background branco
**E** o titulo "LBot Simulator Web" deve estar visivel
**E** a borda inferior deve ser 1px #dee1e6
