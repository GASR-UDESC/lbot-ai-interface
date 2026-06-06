# Especificacao de Negocio: Redesign UI LBot DataGen - Estilo Airbnb

## Contexto

O LBot DataGen e um jogo educacional onde usuarios comandam um robo virtual usando linguagem natural (processada por IA) que e traduzida para comandos LBML. O app atual possui uma UI dark-neon (fundo escuro com acentos verdes) que nao reflete a identidade visual desejada.

O objetivo e redesenhar **toda a UI** (exceto o canvas 3D do simulador) seguindo fielmente o design system do Airbnb, documentado em `task/DESIGN-airbnb.md`. Isso inclui paleta de cores, tipografia, componentes, bordas arredondadas, espacamento, elevacao e comportamento responsivo do Airbnb.

O canvas 3D Three.js (componente `robo-simulator`) permanece inalterado. Tudo ao redor dele (HUDs, overlays, botoes, status, score) sera redesenhado.

## Requisitos Funcionais

### RF01 - Design System Global (Tokens e Tema)

Todo o aplicativo deve adotar o design system Airbnb de forma fielm com os seguintes tokens:

**Cores:**
- Primary: `#ff385c` (Rausch) - unico acento de cor para todos os CTAs primarios, elementos de destaque e interacoes
- Canvas: `#ffffff` - fundo branco para todas as paginas e superficies
- Ink: `#222222` - texto principal
- Body: `#3f3f3f` - texto secundario/corrido
- Muted: `#6a6a6a` - subtitulos e labels inativos
- Muted-soft: `#929292` - texto desabilitado
- Hairline: `#dddddd` - bordas 1px
- Hairline-soft: `#ebebeb` - divisores leves
- Border-strong: `#c1c1c1` - bordas de input em focus
- Surface-soft: `#f7f7f7` - fundo de campos desabilitados
- Surface-strong: `#f2f2f2` - fundo de icon-buttons circulares
- On-primary: `#ffffff` - texto branco sobre Rausch
- Primary-active: `#e00b41` - estado pressed de CTAs
- Primary-disabled: `#ffd1da` - estado disabled de CTAs
- Primary-error-text: `#c13515` - texto de erro em formularios
- Legal-link: `#428bff` - links legais
- Star-rating: `#222222` - estrelas/avaliacao em ink (nao amarelo)
- Scrim: `#000000` a 50% opacity - backdrop de modais

**Tipografia:**
- Font family: Inter (substituto open-source do Airbnb Cereal VF), com fallback: `-apple-system, system-ui, Roboto, 'Helvetica Neue', sans-serif`
- Hierarquia tipografica seguindo os tokens do Airbnb (display-xl ate uppercase-tag)

**Espacamento:**
- Base unit: 4px (com micro-step de 2px)
- Tokens: xxs 2px, xs 4px, sm 8px, md 12px, base 16px, lg 24px, xl 32px, xxl 48px, section 64px

**Bordas arredondadas:**
- none 0px, xs 4px, sm 8px, md 14px, lg 20px, xl 32px, full 9999px

**Elevacao:**
- Flat: sem sombra (95% das superficies)
- Card hover float: `box-shadow: rgba(0,0,0,0.02) 0 0 0 1px, rgba(0,0,0,0.04) 0 2px 6px 0, rgba(0,0,0,0.1) 0 4px 8px 0` (unica sombra do sistema)
- Modal scrim: `#000000` a 50%

**Regras:**
- Nenhuma superficie escura em nenhuma pagina ou componente (exceto o canvas 3D do simulador que fica de fora do redesign)
- Nenhuma cor de acento secundaria em CTAs - Rausch e o unico acento
- Nenhuma borda dura (hard corner) em elementos interativos - tudo e rounded
- Tipografia moderada - confiar no espacamento branco e na hierarquia, nao em pesos pesados

### RF02 - Top Navigation Bar (global)

Uma barra de navegacao global no topo do aplicativo, seguindo o padrao `top-nav` do Airbnb:

**Regras:**
- Altura: 80px
- Fundo: canvas (#ffffff)
- Borda inferior: 1px hairline (#dddddd)
- Lado esquerdo: Logo/marca LBot (texto ou icone)
- Centro: 3 tabs de navegacao - "Jogar", "Leaderboard", "Controles" - estilo `product-tab-active` (ink, underline) para a tab ativa e `product-tab-inactive` (muted) para inativas
- Lado direito: area de utilitarios (icone de idioma, indice de sessao ou vazio por enquanto)
- Tipografia: `nav-link` (16px, 600, 1.25)
- A top nav aparece em TODAS as paginas

**Cenarios de erro:**
- Nenhuma tab ativa (rota invalida): redirecionar para /menu

### RF03 - Pagina Menu/Home (Landing Page com Hero e Search Bar)

A pagina inicial deve seguir o padrao de hero do Airbnb com search bar:

**Regras:**
- Hero section com titulo em `display-xl` (28px, 700): "LBot Arena" ou equivalente
- Subtitulo em `body-md` (16px, 400): descricao do que o app faz
- Search bar pill-shaped (`search-bar-pill`): fundo branco, `rounded.full`, 64px altura, dividida por hairlines em 3 segmentos: "Modo" / "Nivel" / "Jogador"
- Search orb circular Rausch (`search-orb`) no lado direito da search bar, 48x48px, icone branco centralizado
- Ao clicar no search orb ou em um segmento, navegar para a pagina correspondente:
  - Segmento "Modo" abre dropdown com: Jogar, Leaderboard, Controles
  - Segmentos "Nivel" e "Jogador" sao opcionais/futuros, podem exibir "Qualquer" por enquanto
- Background: canvas branco com padding generoso (`spacing.section` 64px)
- Footer section com links informativos estilo `footer-light` do Airbnb

**Cenarios de erro:**
- Se o backend estiver offline: exibir mensagem de erro em `primary-error-text` abaixo da search bar, com botao de retry estilo `button-secondary`

### RF04 - Pagina de Game (Simulador + Chat)

Layout split mantendo simulador a esquerda e chat a direita, porem com visual Airbnb:

**Regras:**
- Layout: flex row, simulador a esquerda (flex 1), chat a direita (380px fixo)
- Separador entre paineis: hairline vertical (#dddddd)
- Top nav global no topo
- Painel do simulador: fundo canvas (#ffffff), o canvas 3D ocupa toda a area disponivel
- **HUD do simulador** (Sobreposto ao canvas 3D):
  - Fundo: branco semi-transparente (`rgba(255,255,255,0.92)`) com `backdrop-filter: blur(6px)`, sem cor escura
  - Borda: 1px hairline (#dddddd), `rounded.md`
  - Tipografia: nivel/timer em `title-md` ink, nome do nivel em `body-md` muted
  - Score/botao de "Reiniciar": estilo `button-secondary` ou `icon-button-circle`
  - Botao "Voltar ao Menu": estilo `button-tertiary-text` com underline hover
- **Chat panel** (Lado direito):
  - Fundo: canvas (#ffffff)
  - Cabecalho do chat: fundo canvas, borda inferior hairline, texto em ink `title-md`
  - Mensagens do usuario: bolha com fundo Rausch (#ff385c), texto on-primary (#ffffff), `rounded.lg`
  - Mensagens do bot: bolha com fundo `surface-soft` (#f7f7f7), texto ink, `rounded.lg`
  - Mensagens de sistema: centralizadas, `caption-sm` muted
  - Mensagens de erro: fundo `rgba(193,53,21,0.08)`, texto `primary-error-text`, `rounded.lg`
  - Indicador de digitacao: `caption-sm` muted
  - Sistema de estrelas de avaliacao: estrelas em ink (#222222, nao amarelo), preenchidas em ink quando selecionadas, `rounded.md` nos cards
  - Input area: `text-input` estilo Airbnb (56px, `rounded.sm`, hairline border), botao enviar `button-primary`
  - Popup de observacao: scrim + card branco `rounded.md`
- Responsive: em <744px, chat vai para abaixo do simulador (vertical stack)

**Cenarios de erro:**
- Chat ID carregando: mensagem "Carregando chat..." em `caption-sm` muted
- Falha ao enviar mensagem: exibir erro inline em `primary-error-text`
- Perda de conexao: mensagem de erro persistente com botao retry `button-primary`

### RF05 - Level Transition Overlay

Overlay entre niveis, estilo Airbnb:

**Regras:**
- Scrim backdrop: `#000000` a 50%
- Card centralizado: fundo canvas (#ffffff), `rounded.md`, padding `spacing.xl` (32px)
- Pill badge no topo: "NIVEL X" em `uppercase-tag`, `rounded.full`, fundo `surface-soft`, texto ink
- Titulo: `display-sm` ink ("Nivel X Completo!")
- Tempo: label "Tempo" em `caption-sm` muted + valor em `rating-display` (64px, 700) ink
- Proximo nivel: texto em `body-md` muted
- Botao "Proximo Nivel": `button-primary` (Rausch, full-width)
- Animacao: fadeIn + scaleIn (0.3s)

**Cenarios de erro:**
- Nenhum (overlay so aparece quando o nivel e completado com sucesso)

### RF06 - Victory Screen Overlay

Tela de vitoria apos completar todos os niveis:

**Regras:**
- Scrim backdrop: `#000000` a 50%
- Card centralizado: fundo canvas (#ffffff), `rounded.md`, padding `spacing.xl` (32px)
- Icone: trofe ou emoji de trofeu em tamanho grande
- Titulo: `display-xl` (28px, 700) ink "PARABENS!"
- Subtitulo: `body-md` muted
- **Tempo total em destaque**: numero grande em `rating-display` (64px, 700) ink, com label "Tempo Total"
- Tabela de tempos por nivel: linhas com `hairline` entre linhas, `body-sm` para dados, `title-md` para nome do nivel
- Nickname input: `text-input` estilo Airbnb (56px, `rounded.sm`, hairline border, focus com border ink 2px)
- Botoes: "Salvar no Leaderboard" `button-primary` (desabilitado ate nickname preenchido) + "Jogar Novamente" `button-secondary`
- Animacao: fadeIn + scaleIn (0.4s)

**Cenarios de erro:**
- Erro ao salvar: card de erro com `primary-error-text` e botao "Tentar novamente" `button-secondary`
- Nickname vazio: botao salvar permanece `button-primary-disabled`

### RF07 - Confirm Modal (Sair do Jogo)

Modal de confirmacao para sair de uma partida em andamento:

**Regras:**
- Scrim backdrop: `#000000` a 50%
- Card centralizado: fundo canvas (#ffffff), `rounded.md`, padding `spacing.xl`
- Titulo: `title-md` ink ("Tem certeza?")
- Mensagem: `body-md` body (#3f3f3f)
- Botoes lado a lado: "Cancelar" `button-secondary` + "Sim, sair" `button-primary` (Rausch)
- Animacao: fadeIn + scaleIn (0.2s)
- Clicar no scrim fora do card = cancelar

**Cenarios de erro:**
- Nenhum (modal puramente interativo)

### RF08 - Leaderboard (Cards estilo Property Card)

Pagina de ranking com cards estilo Airbnb property-card:

**Regras:**
- Fundo: canvas (#ffffff)
- Top nav global no topo
- Header: icone de trofeu + titulo `display-lg` ink "Leaderboard" + subtitulo `body-md` muted
- **Cards de ranking** (substituindo tabela):
  - Cada jogador como um card: fundo canvas, `rounded.md`, hairline border
  - Posicao/rank em grande: `rating-display` (para top 3) ou `title-md` (para demais)
  - Nickname: `title-md` ink
  - Tempo: `body-md` muted, valor em monospace tabular-nums
  - Data: `caption-sm` muted
  - Medalhas: top 3 recebem emojis ou icones especiais (ouro, prata, bronze)
  - Hover: elevacao card hover float (shadow tier unico do Airbnb)
- Layout: grid responsivo de cards (4-up desktop, 2-up tablet, 1-up mobile)
- Empty state: icone + mensagem em `body-md` muted
- Error state: icone + mensagem de erro em `primary-error-text` + botao retry `button-primary`
- Loading state: skeleton cards com `surface-soft` e animacao de pulse
- Footer: link "Voltar ao Menu" como `button-tertiary-text` com underline hover

**Cenarios de erro:**
- API indisponivel: mensagem de erro com botao retry
- Nenhum jogador completou: empty state amigavel
- Timeout: mensagem de erro generica com retry

### RF09 - Pagina de Controls (Modo Controle)

Pagina de controle manual do robo:

**Regras:**
- Fundo: canvas (#ffffff) (mudando do tema claro/escuro atual para 100% claro)
- Top nav global no topo
- Header da pagina: titulo `display-sm` ink "Modo Controle" + subtitulo `body-md` muted
- Layout de duas colunas: simulador a esquerda (flex 1.2) + painel de controles a direita
- **Simulador**: fundo canvas, container com `rounded.md`, hairline border, sombra de elevacao
- **Painel de controles virtuais**:
  - Fundo: canvas (#ffffff), `rounded.md`, hairline border
  - Botoes de movimento: `icon-button-circle` com `rounded.full`, `surface-strong` como fundo, ink texto/icone
  - Botoes de rotacao: mesmo estilo, com icone diferente
  - Labels: `caption-sm` muted para secoes, `button-sm` ink para nomes de botoes
  - Timeline de comandos: lista com itens em fundo canvas, hairline separators
  - Botao "Executar": `button-primary` (Rausch, full-width)
  - Botao "Limpar": `button-tertiary-text` com underline hover
  - Display LBML: bloco de codigo com `surface-soft` fundo, `caption-sm` monospace, `rounded.sm`
  - Summary: `body-sm` muted, estatisticas em ink
- Responsive: em <768px (mobile), layout empilha verticalmente

**Cenarios de erro:**
- Falha ao executar comando: mensagem de erro inline em `primary-error-text`
- Falha ao salvar sessao: mensagem de erro com retry

### RF10 - Virtual Controls (Componente)

Componente reutilizavel de controles virtuais:

**Regras:**
- Botoes de acao (Frente, Tras, Esquerda, Direita): `icon-button-circle` com `surface-strong` fundo, ink icone, `rounded.full`, 44px min touch target
- Botoes de rotacao (Girar Esq., Girar Dir.): mesmo estilo, icone de rotacao
- Timeline: lista vertical com `hairline-soft` entre itens, cada item com `rounded.sm`, hover com shadow tier
- Botao remover (X) por item: `icon-button-circle` pequeno, `surface-strong`
- Textarea de descricao: `text-input` estilo Airbnb (56px, `rounded.sm`)
- Botao "Executar": `button-primary`, `rounded.sm`, full-width quando mobile
- Botao "Limpar Tudo": `button-tertiary-text`, texto ink com underline hover

### RF11 - LBot Chat (Componente)

Componente de chat reestilizado como messaging Airbnb:

**Regras:**
- Fundo: canvas (#ffffff)
- Cabecalho: fundo canvas, hairline inferior, titulo em `title-md` ink, icone de bot
- Area de mensagens: scroll vertical, padding `spacing.base` (16px)
- Mensagens do usuario: bolha Rausch (#ff385c), texto on-primary (#ffffff), `rounded.lg` (14px), alinhadas a direita, max-width 70%
- Mensagens do bot: bolha `surface-soft` (#f7f7f7), texto ink (#222222), `rounded.lg`, alinhadas a esquerda, max-width 70%
- Mensagens de sistema: centralizadas, `caption-sm` muted (#6a6a6a), sem bolha
- Mensagens de erro: bolha com fundo `rgba(193,53,21,0.08)`, borda `primary-error-text`, `rounded.lg`
- Avaliacao por estrelas: 5 estrelas ink (#222222) outlines, preenchidas em ink ao selecionar, `rounded.md` nos containers
- Indicador de digitacao: pontos animados em muted
- Input: `text-input` estilo Airbnb, `rounded.sm`, 56px altura, placeholder em muted
- Botao enviar: `button-primary` (Rausch), `rounded.sm`, icone + texto
- Popup de observacao: scrim + card canvas `rounded.md`

### RF12 - Responsividade (Breakpoints Airbnb)

O redesign deve seguir os breakpoints e comportamentos do design doc Airbnb:

**Breakpoints:**
- Mobile: <744px - top nav colapsa para logo + hamburger; search bar colapsa para pill unico; cards 1-up; game empilha verticalmente
- Tablet: 744-1128px - top nav mantem tabs; search bar estreita; cards 2-3 up; game chat mais estreito
- Desktop: 1128-1440px - top nav completa com 3 tabs centralizadas; search bar full; cards 4-up; game split layout completo
- Wide: >1440px - conteudo max-width 1440px centrado; gutters absorvem o espaco extra

**Regras:**
- Top nav: hamburger em mobile, tabs visivel em tablet+
- Game: split layout em desktop, stack vertical em mobile (simulador 55%, chat abaixo)
- Leaderboard: 4 colunas em desktop, 2 em tablet, 1 em mobile
- Search bar (Menu): full pill em desktop, pill unico colapsado em mobile que abre overlay
- Touch targets: minimo 48x48px para CTAs, 44x44px para icon-buttons

## Requisitos Nao-Funcionais

- **RNF01 - Performance:** O redesign nao deve impactar o render do canvas 3D. CSS e estilos devem ser carregados sem bloquear o Three.js
- **RNF02 - Acessibilidade:** Todos os elementos interativos devem ter contraste AA minimo. botoes Rausch sobre canvas branco = 4.58:1 (passa AA). Touch targets >= 44px
- **RNF03 - Consistencia:** Nenhum componente deve usar cores, fontes, ou espacamento fora dos tokens definidos. Todo CSS custom deve referenciar variaveis CSS (custom properties) mapeadas dos tokens Airbnb
- **RNF04 - Manutenibilidade:** Tokens Airbnb devem ser definidos como CSS custom properties em `styles.css` global, para易于 manutencao e futuros ajustes
- **RNF05 - Preservacao de funcionalidade:** Nenhuma funcionalidade existente deve ser perdida ou alterada. Apenas a camada visual (HTML/CSS/template) muda; services, models, e logica de negocio permanecem intactos

## Glossario / Definicoes

- **Rausch**: cor primaria do Airbnb (#ff385c), vermelho quente usado como unico acento de cor
- **Canvas**: fundo branco (#ffffff), superficie padrao de todas as paginas
- **Ink**: cor de texto principal (#222222), nunca preto puro
- **Hairline**: borda de 1px (#dddddd), usada para separadores sutis
- **Scrim**: sobreposicao escura (#000000 a 50% opacity) para modais e overlays
- **Simulador**: componente Three.js (robo-simulator) que renderiza o cenario 3D com fisica - EXCLUIDO do redesign visual
- **LBML**: Linguagem de comandos do robo (Left/Right/Forward/Back com distancias e angulos)
- **HUD**: Heads-Up Display - overlay de informacoes sobre o canvas 3D (timer, nivel, score)
- **Split layout**: layout de duas colunas com simulador a esquerda e chat a direita
- **Touch target**: area minima clicavel/tocavel para elementos interativos

## Premissas

- A fonte Inter esta disponivel via Google Fonts ou CDN, e sera a unica fonte do sistema (sem Airbnb Cereal VF)
- Todos os textos da UI permanecem em portugues (pt-BR)
- O canvas Three.js do simulador nao sofre nenhuma alteracao visual ou estrutural
- Os services Angular (game-state, leaderboard, messages, simulator-bridge, etc.) permanecem inalterados
- As models/interfaces TypeScript permanecem inalteradas
- O roteamento (routes) permanece inalterado
- O design system sera implementado como CSS custom properties em `styles.css` global, consumidas por cada componente
- A top nav global sera um novo componente compartilhado (standalone Angular component)

## Fora de escopo

- Qualquer alteracao no componente `robo-simulator` (canvas 3D Three.js) - visual, estrutural ou logico
- Qualquer alteracao no componente `simulator-frame` (wrapper de iframe)
- Alteracoes no backend (Java/Spring)
- Internacionalizacao (i18n) - textos permanecem em pt-BR
- Dark mode como alternativa - o redesign e 100% light mode
- Funcionalidades novas que nao existiam antes (apenas redesenho visual)
- SEO ou meta-tags
- Acessibilidade avancada alem de contraste AA e touch targets (ex: screen reader testing completo)
- Sub-marcas Luxe (#460479) e Plus (#92174d) - fora do escopo
- Animacoes complexas alem de fadeIn/scaleIn e hover lift - sem animacoes elaboradas

## Cenarios de Aceite

### CA01 - Top Navigation Global
**Dado** que o usuario esta em qualquer pagina do app
**Quando** a pagina carrega
**Entao** a top nav aparece com 80px de altura, fundo branco, 3 tabs centralizadas (Jogar, Leaderboard, Controles) com a tab ativa em ink com underline e as inativas em muted

### CA02 - Menu/Home com Hero e Search Bar
**Dado** que o usuario acessa a pagina inicial (/menu)
**Quando** a pagina carrega
**Entao** aparece o hero com titulo "LBot Arena" em display-xl, subtitulo em body-md, e a search bar pill com 3 segmentos e o search orb Rausch
**E** ao clicar no search orb com "Jogar" selecionado, navega para /game

### CA03 - Pagina de Game com Visual Airbnb
**Dado** que o usuario inicia uma partida (/game)
**Quando** a pagina carrega
**Entao** o layout split apresenta simulador a esquerda e chat a direita, separados por hairline, com fundo canvas branco em ambos os paineis
**E** o HUD sobre o simulador tem fundo branco semi-transparente com tipografia ink, sem escuridao
**E** o chat tem mensagens do usuario em bolhas Rausch com texto branco e mensagens do bot em bolhas surface-soft com texto ink

### CA04 - Level Transition Airbnb-style
**Dado** que o usuario completa um nivel
**Quando** o overlay de transicao aparece
**Entao** um scrim 50% cobre a tela com um card branco centralizado contendo pill badge "NIVEL X", titulo display-sm, tempo em rating-display, e botao "Proximo Nivel" button-primary

### CA05 - Victory Screen Airbnb-style
**Dado** que o usuario completa todos os 5 niveis
**Quando** a tela de vitoria aparece
**Entao** um scrim 50% cobre a tela com um card branco centralizado contendo titulo "PARABENS!" em display-xl, tempo total em rating-display (64px), tabela de tempos com hairlines, input de nickname estilo text-input, e botoes button-primary/button-secondary

### CA06 - Confirm Modal Airbnb-style
**Dado** que o usuario tenta sair de uma partida em andamento
**Quando** o modal de confirmacao aparece
**Entao** um scrim 50% cobre a tela com um card branco centralizado contendo titulo "Tem certeza?" em title-md, mensagem em body-md, botao "Cancelar" button-secondary e "Sim, sair" button-primary

### CA07 - Leaderboard com Cards Airbnb
**Dado** que o usuario acessa a pagina de leaderboard
**Quando** a pagina carrega com dados
**Entao** cada jogador e exibido como um card property-card (rounded.md, hairline border) com rank, nickname em title-md, tempo em body-md muted, e data em caption-sm
**E** o top 3 tem destaque visual com icones de medalha

### CA08 - Leaderboard - Estados Especiais
**Dado** que o usuario acessa a pagina de leaderboard
**Quando** nao ha dados (vazio ou erro)
**Entao** exibe empty state com icone + mensagem muted ou error state com mensagem em primary-error-text e botao retry button-primary

### CA09 - Pagina de Controls Airbnb-style
**Dado** que o usuario acessa /controls
**Quando** a pagina carrega
**Entao** aparece layout de duas colunas (simulador + painel de controles) com fundo canvas branco, painel de controles com botoes icon-button-circle, timeline com hairline separators, e botao executar button-primary

### CA10 - Responsividade Mobile
**Dado** que o usuario acessa o app em tela < 744px
**Quando** qualquer pagina carrega
**Entao** a top nav colapsa para hamburger, cards empilham 1-up, game empilha verticalmente com chat abaixo do simulador, e search bar colapsa para pill unico

### CA11 - Responsividade Tablet
**Dado** que o usuario acessa o app em tela 744-1128px
**Quando** qualquer pagina carrega
**Entao** a top nav mantem tabs visiveis, cards 2-3 up, game split com chat mais estreito

### CA12 - Preservacao de Funcionalidade
**Dado** que o redesign visual esta completo
**Quando** o usuario interage com qualquer funcionalidade (chat, envio de comandos, avaliacao por estrelas, navegacao, modal de saida, etc.)
**Entao** todas as funcionalidades existentes continuam operando identicamente, apenas com visual diferente

### CA13 - Chat com Estilo Airbnb Messaging
**Dado** que o usuario esta na pagina de game ou em sessao de chat
**Quando** envia uma mensagem
**Entao** a mensagem aparece em bolha Rausch (#ff385c) com texto branco (#ffffff) alinhada a direita
**E** a resposta do bot aparece em bolha surface-soft (#f7f7f7) com texto ink (#222222) alinhada a esquerda
**E** as estrelas de avaliacao sao em ink (#222222) estilo Airbnb (nao amarelo)