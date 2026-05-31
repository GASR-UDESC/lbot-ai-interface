# Especificacao de Negocio: Melhorias no Level Design, Fisica e UI do lbot-datagen

## Contexto

O modulo `lbot-datagen-frontend` possui um modo "Game" com 5 niveis gamificados onde o usuario envia comandos LBML via chat para guiar um robot de um ponto A ate um ponto B, desviando de obstaculos. Atualmente, o level design apresenta problemas que tornam o jogo trivial (obstaculos facilmente contornaveis pelos cantos), a fisica permite que o robot atravesse as barreiras da arena, a UI tem aparencia generica de IA, e elementos visuais se sobrepoem no layout.

Esta tarefa visa corrigir esses problemas para tornar o jogo mais desafiador, fisicamente coerente e visualmente atraente.

## Requisitos Funcionais

### RF01 - Redesign dos Niveis com Dificuldade Progressiva

Os 5 niveis devem ser redesenhados com obstaculos que forcam o robot a percorrer caminhos especificos, impossibilitando "cortar caminho" pelos cantos da arena.

**Regras:**
- Nivel 1-2: Desvios laterais simples (obstaculos que forcam movimentos em S leves)
- Nivel 3: Corredores com curvas (paredes formando passagens obrigatorias)
- Nivel 4: Labirinto (varias curvas e decisoes de caminho)
- Nivel 5: Labirinto + rampas obrigatorias (passagens bloqueadas no chao, unico caminho e subindo rampa)
- Os obstaculos devem cobrir a largura da arena de forma que NAO exista caminho livre sem desviar
- Rampas sao obrigatorias apenas nos niveis avancados (4-5), onde certas passagens so sao acessiveis subindo a rampa
- Cada nivel mantem seu tema visual distinto (Armazem, Escritorio, Cidade, Floresta, Fabrica) com cores proprias

**Cenarios de erro:**
- Se o level design permitir caminho direto sem desviar: o nivel esta mal projetado e deve ser corrigido

### RF02 - Pontos A e B Fixos e Estrategicos

Os pontos de partida (A) e chegada (B) sao fixos por nivel e posicionados estrategicamente para forcar o robot a passar pelos obstaculos.

**Regras:**
- Cada nivel tem exatamente UM ponto A e UM ponto B, sempre iguais para todos os jogadores
- Os pontos devem ser posicionados de forma que o caminho mais curto entre eles passe obrigatoriamente pelos obstaculos/corredores
- O botao "Novo Desafio" e REMOVIDO completamente da interface
- A funcao `generateNewLevel()` e eliminada - nao ha mais geracao aleatoria de pontos
- Os pontos sao definidos diretamente na configuracao de cada nivel (`LevelConfig`)

**Cenarios de erro:**
- N/A (configuracao estatica)

### RF03 - Fisica das Barreiras da Arena

As paredes perimetrais da arena devem ter corpos fisicos reais (physics bodies) no CANNON.js, impedindo que o robot as atravesse.

**Regras:**
- As 4 paredes perimetrais devem ter `CANNON.Body` estaticos (mass=0) com geometria correspondente a visual
- Ao colidir com qualquer parede (perimetral ou obstaculo), o robot PARA imediatamente
- Nao ha bounce/ricochete - o robot simplesmente nao avanca na direcao da parede
- Nao ha penalidade por colisao alem do tempo perdido
- Acelerar contra a barreira nao deve permitir atravessa-la em nenhuma circunstancia
- O robot nao deve conseguir passar "por baixo" das paredes (altura das paredes e physics bodies devem ser suficientes)

**Cenarios de erro:**
- Robot colide com parede: para no ponto de contato, jogador precisa enviar novo comando
- Robot tenta atravessar parede continuamente: fica parado no ponto de contato indefinidamente

### RF04 - Reset de Nivel

O jogador pode resetar o nivel atual, retornando o robot ao ponto A.

**Regras:**
- Existe um botao/acao para resetar o nivel (substituindo o antigo "Novo Desafio")
- Ao resetar, o robot volta ao ponto A do nivel atual
- O timer NAO para e NAO reseta - o tempo continua correndo (penalidade implicita)
- O jogador pode resetar quantas vezes quiser
- O historico de comandos no chat e mantido apos reset

**Cenarios de erro:**
- Reset durante animacao: aguardar animacao terminar ou cancelar animacao antes de resetar

### RF05 - Redesign Visual da UI (Gaming Moderno/Colorido)

A interface deve ser redesenhada com estetica de gaming moderno (referencia: Duolingo, Monument Valley) - cores vivas, cantos arredondados, visual profissional.

**Regras:**
- Manter TODO o conteudo informacional existente (X, Z, Rotacao, Comando atual, Distancia ao B)
- Redesenhar visualmente: cores vibrantes, cantos arredondados, tipografia limpa
- Remover aparencia "generica de IA" (gradientes excessivos, glassmorphism exagerado, glow effects)
- O botao de troca de camera ("3a Pessoa"/"Vista Normal") e MANTIDO
- Score counter mantido com visual atualizado
- Indicador "EXECUTANDO..." mantido com visual atualizado

**Cenarios de erro:**
- N/A (mudanca puramente visual)

### RF06 - Correcao do Layout com Espacamento

O game page deve ter espacamento adequado entre o simulador e o resto da interface, sem sobreposicao de elementos.

**Regras:**
- Simulador grande ocupa a maior parte da tela, chat em painel lateral
- Deve haver padding/gap entre o simulador e as bordas da pagina (similar ao modo controle que usa `gap: 24px` e `padding: 24px`)
- O simulador deve estar contido em um container com bordas arredondadas (como no modo controle)
- Os elementos HUD do game page (timer, navegacao) NAO devem sobrepor os elementos internos do simulador (status panel, botoes)
- O painel de status do simulador (top-left) e os botoes de navegacao do game devem ter posicoes distintas que nao conflitem

**Cenarios de erro:**
- Em telas muito pequenas: definir comportamento responsivo (chat pode colapsar ou virar overlay)

### RF07 - Pontuacao por Tempo Total

O ranking do leaderboard e baseado no tempo total gasto para completar os 5 niveis.

**Regras:**
- Timer comeca quando o nivel 1 inicia
- Timer nao para entre niveis (transicao conta no tempo)
- Timer para apenas quando o ponto B do nivel 5 e alcancado
- Menor tempo = melhor posicao no ranking
- Colisoes nao geram penalidade direta (apenas tempo perdido implicitamente)
- Reset de nivel nao reseta o timer (penalidade implicita)

**Cenarios de erro:**
- Jogador abandona partida: tempo nao e salvo no leaderboard
- Conexao cai no meio: estado deve ser mantido localmente para continuacao

## Requisitos Nao-Funcionais

- O redesign visual nao deve degradar performance do renderer 3D (manter 60fps)
- As colisoes fisicas devem ser computadas em tempo real sem lag perceptivel
- O layout responsivo deve funcionar em telas >= 1024px de largura
- Os niveis devem ser testados manualmente para garantir que sao completaveis (existe caminho valido)

## Glossario / Definicoes

- **LBML**: Linguagem de marcacao de comandos do LBot (ex: `<forward distance="50"/>`)
- **Ponto A**: Posicao inicial do robot no nivel (partida)
- **Ponto B**: Posicao objetivo que o robot deve alcancar (chegada)
- **Physics Body**: Corpo fisico no CANNON.js que participa de simulacao de colisoes
- **Arena**: Area de jogo 400x400 unidades delimitada por paredes perimetrais
- **Rampa**: Obstaculo inclinado que o robot pode subir para acessar areas elevadas
- **Reset**: Acao de retornar o robot ao ponto A do nivel atual sem pausar o timer

## Premissas

- A arena continua com dimensoes 400x400 unidades
- O robot mantem suas dimensoes e massa atuais (Box 20x12x30, mass 100)
- O sistema de 5 niveis sequenciais e mantido
- O chat lateral (LBML) continua sendo a forma primaria de controle
- O leaderboard backend continua funcionando da mesma forma (apenas muda o que e enviado)
- Os temas visuais dos niveis (cores de chao, parede, obstaculo, ceu) sao mantidos como conceito, mas podem ter paletas ajustadas

## Fora de escopo

- Mudancas no sistema de chat/LBML
- Mudancas no modo Controle (virtual controls page)
- Mudancas no lbot-simulator-web (simulador standalone React)
- Adicao de novos tipos de obstaculo (alem de wall, crate, ramp)
- Sistema de power-ups ou itens colecionaveis
- Modo multiplayer
- Mudancas no backend do leaderboard
- Mudancas na logica de parsing de comandos LBML

## Cenarios de Aceite

### CA01 - Nivel 1 nao pode ser contornado pelos cantos
**Dado** o robot no ponto A do nivel 1
**Quando** o jogador tenta mover o robot em linha reta diagonal ate o ponto B
**Entao** o robot colide com obstaculos e nao consegue chegar ao ponto B sem desviar

### CA02 - Nivel 5 requer uso de rampa
**Dado** o robot no ponto A do nivel 5
**Quando** o jogador tenta completar o nivel sem usar nenhuma rampa
**Entao** nao existe caminho possivel ate o ponto B sem subir pelo menos uma rampa

### CA03 - Parede da arena bloqueia robot fisicamente
**Dado** o robot proximo a parede perimetral da arena
**Quando** o jogador envia comando que move o robot contra a parede continuamente
**Entao** o robot para no ponto de contato e nao atravessa a parede independente do tempo de aceleracao

### CA04 - Botao "Novo Desafio" removido
**Dado** a interface do game carregada em qualquer nivel
**Quando** o jogador observa os controles disponiveis
**Entao** nao existe botao "Novo Desafio" - apenas camera toggle e reset

### CA05 - Pontos A e B sao fixos
**Dado** dois jogadores diferentes jogando o nivel 3
**Quando** ambos iniciam o nivel
**Entao** ambos partem do mesmo ponto A e devem chegar ao mesmo ponto B

### CA06 - Reset de nivel mantem timer
**Dado** o jogador esta no nivel 2 com 45 segundos decorridos
**Quando** o jogador aciona reset do nivel
**Entao** o robot volta ao ponto A do nivel 2 e o timer continua de 45 segundos em diante

### CA07 - Elementos nao se sobrepoem
**Dado** a pagina de game carregada
**Quando** o jogador observa o layout
**Entao** o painel de status do simulador, HUD de timer/nivel, e botoes de navegacao estao em posicoes distintas sem sobreposicao

### CA08 - Espacamento entre simulador e interface
**Dado** a pagina de game carregada
**Quando** o jogador observa o layout
**Entao** existe espacamento visivel entre o simulador e as bordas da pagina/painel de chat (nao estao colados)

### CA09 - Visual gaming moderno
**Dado** a pagina de game carregada
**Quando** o jogador observa a interface
**Entao** a UI usa cores vivas, cantos arredondados e visual profissional sem gradientes excessivos ou efeitos de glow

### CA10 - Pontuacao baseada em tempo
**Dado** o jogador completa todos os 5 niveis
**Quando** o robot alcanca o ponto B do nivel 5
**Entao** o tempo total e registrado e usado como criterio de ranking no leaderboard (menor = melhor)
