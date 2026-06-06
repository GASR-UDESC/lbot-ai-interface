# Fase 03: Chat Component + Game Page + HUD

## Status: PENDENTE

## Objetivo

Redesenhar o componente de chat (lbot-chat) com estilo Airbnb messaging e a pagina de game com layout split estilo Airbnb, incluindo o HUD sobre o simulador.

## Pre-requisitos

- Fase 01 concluida (tokens CSS)
- Fase 02 concluida (top-nav para navegacao)

## Tarefas

- [ ] Tarefa 1: Redesenhar o componente LbotChat (RF11)
  - Arquivo: `src/app/components/lbot-chat/lbot-chat.html`
  - O que fazer: Ajustar classes CSS e estrutura para estilo Airbnb:
    - Cabecalho: fundo canvas, hairline inferior, titulo em title-md ink, icone de bot
    - Area de mensagens: scroll vertical, padding spacing.base (16px)
    - Mensagens do usuario: bolha com classe `.message.user` - fundo Rausch (#ff385c), texto on-primary (#ffffff), rounded.lg (20px), alinhadas a direita, max-width 70%
    - Mensagens do bot: bolha com classe `.message.bot` - fundo surface-soft (#f7f7f7), texto ink (#222222), rounded.lg, alinhadas a esquerda, max-width 70%
    - Mensagens de sistema: centralizadas, caption-sm muted, sem bolha
    - Mensagens de erro: fundo rgba(193,53,21,0.08), borda primary-error-text, rounded.lg
    - Estrelas de avaliacao: 5 estrelas ink (#222222), preenchidas em ink, rounded.md nos containers
    - Indicador de digitacao: caption-sm muted, pontos animados
    - Input area: text-input estilo Airbnb (56px, rounded.sm, hairline border), botao enviar button-primary
    - Popup de observacao: scrim + card canvas rounded.md
    - Botao "Encerrar chat" (X): icon-button-circle com surface-strong

  - Arquivo: `src/app/components/lbot-chat/lbot-chat.css`
  - O que fazer: Substituir TODOS os estilos por tokens Airbnb:
    - `.chat-wrapper`: fundo canvas (#ffffff), sem border-radius excessivo
    - `.chat-header`: fundo canvas, hairline inferior (#dddddd), title-md ink
    - `.message.user`: background var(--color-primary), color var(--color-on-primary), border-radius var(--rounded-lg)
    - `.message.bot`: background var(--color-surface-soft), color var(--color-ink)
    - `.message.error`: background rgba(193,53,21,0.08), color var(--color-primary-error-text)
    - `.message.system`: color var(--color-muted), sem background
    - `.star-btn`: color var(--color-star-rating) ink, nao amarelo
    - `.star-btn.selected`: color var(--color-ink), preenchido
    - `.chat-input input`: height 56px, border-radius var(--rounded-sm), border 1px var(--color-hairline), focus border var(--color-ink) 2px
    - `.chat-input button`: background var(--color-primary), color var(--color-on-primary), border-radius var(--rounded-sm)
    - `.rating-overlay`: background var(--color-scrim) com 50% opacity
    - `.rating-popup`: background var(--color-canvas), border-radius var(--rounded-md)
    - Remover TODAS as cores hard-coded (#007bff, #333, #999, etc.)
    - Remover gradientes e sombras dark

- [ ] Tarefa 2: Redesenhar a Game Page layout (RF04)
  - Arquivo: `src/app/pages/game/game.page.html`
  - O que fazer: Ajustar estrutura HTML para:
    - Manter layout split (simulador a esquerda, chat a direita)
    - Substituir classes dark por classes Airbnb
    - O chat panel deve ter fundo canvas (#ffffff), sem background escuro
    - Separador entre paineis: hairline vertical (#dddddd)
    - O loading state "Carregando chat..." deve usar caption-sm muted

  - Arquivo: `src/app/pages/game/game.page.css`
  - O que fazer: Substituir TODOS os estilos por tokens Airbnb:
    - `:host`: fundo canvas (#ffffff)
    - `.game-layout`: flex row, simulador flex 1, chat 380px fixo
    - `.chat-panel`: fundo canvas, border-left com hairline
    - `.chat-loading`: cor muted, caption-sm
    - Responsive: em <744px, `.game-layout` vira `flex-direction: column`, chat abaixo do simulador
    - Remover todas as cores dark (#0a0e0a, #111411, etc.)

- [ ] Tarefa 3: Redesenhar o HUD overlay sobre o simulador (RF04)
  - Arquivo: `src/app/pages/game/game.page.css`
  - O que fazer: Redesenhar o HUD com estilo Airbnb:
    - `.hud`: fundo branco semi-transparente `rgba(255,255,255,0.92)`, `backdrop-filter: blur(6px)`, border 1px hairline, border-radius var(--rounded-md)
    - `.hud-label`: uppercase-tag ink (8px, 700, uppercase)
    - `.hud-level-name`: body-md muted
    - `.hud-timer`: title-md ink, font-variant-numeric: tabular-nums
    - `.hud-reset-btn`: estilo button-secondary (canvas bg, ink text, rounded.sm, hairline border)
    - `.nav-link-btn`: estilo button-tertiary-text (transparent bg, ink text, underline hover)
    - Remover todas as cores dark do HUD (rgba(0,0,0,0.6), rgba(110,186,114,0.2), etc.)

## Arquivos Referencia

- `src/app/components/lbot-chat/lbot-chat.ts` - Logica do chat (nao alterar)
- `src/app/components/lbot-chat/lbot-chat.html` - Template atual
- `src/app/components/lbot-chat/lbot-chat.css` - 453 linhas de estilos azul/white
- `src/app/pages/game/game.page.ts` - Logica do game (nao alterar)
- `src/app/pages/game/game.page.html` - Template atual com HUD e chat
- `src/app/pages/game/game.page.css` - 183 linhas de estilos dark
- `task/DESIGN-airbnb.md` - Especificacao de components: button-primary, button-secondary, text-input, icon-button-circle

## Criterios de Aceite

- [ ] CA03: Pagina de Game com Visual Airbnb
  - Cenario: Layout split com simulador a esquerda e chat a direita, separados por hairline, fundo canvas branco
  - Cenario: HUD sobre o simulador tem fundo branco semi-transparente com tipografia ink, sem escuridao
  - Cenario: Chat tem mensagens do usuario em bolhas Rausch com texto branco e mensagens do bot em bolhas surface-soft com texto ink
- [ ] CA13: Chat com Estilo Airbnb Messaging
  - Cenario: Mensagem do usuario: bolha Rausch, texto branco, alinhada a direita
  - Cenario: Mensagem do bot: bolha surface-soft, texto ink, alinhada a esquerda
  - Cenario: Estrelas de avaliacao em ink (#222222), nao amarelo
  - Cenario: Input de texto estilo Airbnb (56px, rounded.sm, hairline border)
- [ ] CA10 (parcial): Responsividade Mobile do Game
  - Cenario: Em <744px, game empilha verticalmente com chat abaixo do simulador

## Testes Esperados

- Chat envia e recebe mensagens corretamente
- Estrelas de avaliacao funcionam (click e reevaluation popup)
- HUD exibe nivel e timer corretamente
- Botao "Reiniciar Posicao" funciona
- Layout split funciona em desktop (>744px)
- Layout stack funciona em mobile (<744px)

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