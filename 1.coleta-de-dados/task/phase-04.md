# Fase 04: Overlay Components (Level Transition + Victory + Confirm Modal)

## Status: PENDENTE

## Objetivo

Redesenhar os tres componentes de overlay (level-transition, victory-screen, confirm-modal) do tema dark/neon para o estilo Airbnb com cards brancos sobre scrim.

## Pre-requisitos

- Fase 01 concluida (tokens CSS)

## Tarefas

- [ ] Tarefa 1: Redesenhar LevelTransition (RF05)
  - Arquivo: `src/app/components/level-transition/level-transition.html`
  - O que fazer: Ajustar estrutura para estilo Airbnb:
    - Manter a estrutura de overlay + card
    - Pill badge "NIVEL X" no topo: uppercase-tag (8px, 700, uppercase), rounded.full, fundo surface-soft, texto ink
    - Titulo: display-sm ink ("Nivel X Completo!")
    - Tempo: label "Tempo" em caption-sm muted + valor em rating-display (64px, 700) ink
    - Proximo nivel: texto em body-md muted
    - Botao "Proximo Nivel": button-primary (Rausch, full-width, rounded.sm)

  - Arquivo: `src/app/components/level-transition/level-transition.css`
  - O que fazer: Substituir TODOS os estilos:
    - `.transition-overlay`: scrim backdrop `rgba(0,0,0,0.5)` (nao 0.75)
    - `.transition-card`: fundo canvas (#ffffff), rounded.md (14px), padding spacing.xl (32px), box-shadow nenhum (flat)
    - `.level-badge`: uppercase-tag, rounded.full, fundo surface-soft, texto ink, border nenhuma
    - `.level-complete-title`: display-sm ink (#222222)
    - `.time-value`: rating-display ink (#222222)
    - `.next-btn`: button-primary Rausch (#ff385c), rounded.sm
    - Animacao: manter fadeIn (0.3s) + scaleIn
    - Remover: cores dark (#1a1f1a, #6aba72, #e8f5e8, rgba com verde), bordas verdes, gradientes

- [ ] Tarefa 2: Redesenhar VictoryScreen (RF06)
  - Arquivo: `src/app/components/victory-screen/victory-screen.html`
  - O que fazer: Ajustar estrutura para estilo Airbnb:
    - Icone de trofeu (emoji ou icone lucide) em tamanho grande
    - Titulo "PARABENS!" em display-xl (28px, 700) ink
    - Subtitulo em body-md muted
    - Tempo total em destaque: numero grande em rating-display (64px, 700) ink, com label "Tempo Total" em caption-sm muted
    - Tabela de tempos por nivel: linhas com hairline entre, body-sm para dados, title-md para nome do nivel
    - Nickname input: text-input estilo Airbnb (56px, rounded.sm, hairline border, focus com ink 2px)
    - Botoes: "Salvar no Leaderboard" button-primary (disabled ate nickname preenchido -> button-primary-disabled) + "Jogar Novamente" button-secondary
    - Erro ao salvar: card com primary-error-text e botao "Tentar novamente" button-secondary

  - Arquivo: `src/app/components/victory-screen/victory-screen.css`
  - O que fazer: Substituir TODOS os estilos:
    - `.victory-overlay`: scrim `rgba(0,0,0,0.5)` (nao 0.82)
    - `.victory-card`: fundo canvas (#ffffff), rounded.md, padding spacing.xl (32px), sem borda dourada
    - `.victory-title`: display-xl ink (#222222)
    - `.trophy-icon`: manter emoji grande
    - `.times-table`: rounded.md, overflow hidden, hairline border
    - `.times-row`: grid, hairline separators
    - `.times-header`: caption muted, uppercase
    - `.level-num`: title-md ink
    - `.level-time`: body-md muted (nao verde neon)
    - `.total-time`: rating-display ink (nao dourado)
    - `.nickname-input`: altura 56px, rounded.sm, border hairline, focus border ink 2px
    - `.save-btn`: button-primary Rausch, rounded.sm
    - `.play-again-btn`: button-secondary (canvas bg, ink text, hairline border), rounded.sm
    - `.save-btn:disabled`: button-primary-disabled (#ffd1da bg)
    - `.save-error`: fundo rgba(193,53,21,0.08), primary-error-text
    - Animacao: manter fadeIn (0.4s) + scaleIn
    - Remover: todas as cores dark/neon, gradientes, bordas douradas

- [ ] Tarefa 3: Redesenhar ConfirmModal (RF07)
  - Arquivo: `src/app/components/confirm-modal/confirm-modal.html`
  - O que fazer: Ajustar estrutura minimamente (esta praticamente correta ja):
    - Manter overlay + card + titulo + mensagem + botoes

  - Arquivo: `src/app/components/confirm-modal/confirm-modal.css`
  - O que fazer: Substituir TODOS os estilos:
    - `.modal-overlay`: scrim `rgba(0,0,0,0.5)` (nao 0.65)
    - `.modal-card`: fundo canvas (#ffffff), rounded.md, padding spacing.xl, sem borda
    - `.modal-title`: title-md ink (#222222)
    - `.modal-message`: body-md body (#3f3f3f)
    - `.cancel-btn`: button-secondary (canvas bg, ink text, hairline border), rounded.sm
    - `.confirm-btn`: button-primary Rausch (#ff385c), rounded.sm
    - Animacao: manter fadeIn (0.2s) + scaleIn
    - Clicar no scrim = cancelar (ja funciona)
    - Remover: cores dark (#1a1f1a, #e8f5e8, #b71c1c), sombras dark

## Arquivos Referencia

- `src/app/components/level-transition/level-transition.ts` - Logica (nao alterar)
- `src/app/components/level-transition/level-transition.html` - Template atual
- `src/app/components/level-transition/level-transition.css` - 123 linhas dark
- `src/app/components/victory-screen/victory-screen.ts` - Logica (nao alterar)
- `src/app/components/victory-screen/victory-screen.html` - Template atual
- `src/app/components/victory-screen/victory-screen.css` - 267 linhas dark
- `src/app/components/confirm-modal/confirm-modal.ts` - Logica (nao alterar)
- `src/app/components/confirm-modal/confirm-modal.html` - Template atual
- `src/app/components/confirm-modal/confirm-modal.css` - 84 linhas dark
- `task/DESIGN-airbnb.md` - Especificacao de scrim, overlays, cards

## Criterios de Aceite

- [ ] CA04: Level Transition Airbnb-style
  - Cenario: Ao completar um nivel, scrim 50% cobre a tela com card branco centralizado contendo pill badge "NIVEL X", titulo display-sm, tempo em rating-display, botao "Proximo Nivel" button-primary
- [ ] CA05: Victory Screen Airbnb-style
  - Cenario: Ao completar todos os niveis, scrim 50% cobre a tela com card branco contendo "PARABENS!" em display-xl, tempo total em rating-display, tabela de tempos com hairlines, input de nickname estilo text-input, e botoes button-primary/button-secondary
  - Cenario: Botao "Salvar" permanece disabled ate nickname preenchido
  - Cenario: Erro ao salvar exibe mensagem em primary-error-text com botao "Tentar novamente"
- [ ] CA06: Confirm Modal Airbnb-style
  - Cenario: Ao tentar sair, scrim 50% cobre a tela com card branco contendo "Tem certeza?" em title-md, mensagem em body-md, botoes "Cancelar" button-secondary e "Sim, sair" button-primary
  - Cenario: Clicar no scrim fora do card cancela o modal

## Testes Esperados

- Level transition aparece ao completar um nivel com visual correto
- Victory screen aparece ao completar 5 niveis com visual correto
- Confirm modal aparece ao tentar sair durante uma partida
- Todos os botoes funcionam (Proximo Nivel, Salvar, Jogar Novamente, Cancelar, Confirmar)
- Animacoes fadeIn + scaleIn executam suavemente

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