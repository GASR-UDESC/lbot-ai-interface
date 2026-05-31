# Especificacao de Negocio: Sistema de Niveis Gamificado com Leaderboard

## Contexto

O projeto lbot-datagen e uma plataforma de geracao de dados de treino para um modelo de traducao de linguagem natural para LBML (linguagem de comandos de um robo). Atualmente, o frontend Angular (`lbot-datagen-frontend`) possui uma arena 3D onde o usuario conversa com uma IA via chat, a IA gera comandos LBML, e o robo executa os movimentos. Existe uma mecanica basica de jogo (ponto A -> ponto B com score), mas sem progressao, sem niveis definidos, e sem persistencia.

O objetivo desta tarefa e transformar a experiencia em um jogo gamificado com 5 niveis tematicos de dificuldade progressiva, onde o jogador deve completar todos os niveis no menor tempo possivel, com um leaderboard global persistido no backend.

Alem de tornar a experiencia mais engajante, o modo gamificado continua gerando dados de treino (pares linguagem natural + LBML + avaliacao do usuario) automaticamente.

## Requisitos Funcionais

### RF01 - Menu Principal

O usuario ao acessar o site ve um menu principal com as opcoes de navegacao.

**Regras:**
- Opcoes disponiveis: "Jogar" (inicia o modo gamificado), "Leaderboard" (visualiza ranking), "Modo Controle" (acessa a pagina separada de virtual controls para geracao de dados)
- O "Modo Controle" fica em uma pagina/rota separada do jogo (nao e mais um toggle dentro da mesma tela)
- Nenhuma autenticacao e necessaria para acessar qualquer opcao

**Cenarios de erro:**
- Backend indisponivel: Menu aparece normalmente. Leaderboard mostra mensagem de indisponibilidade. Jogo funciona mas avisa que score nao sera salvo.

### RF02 - Sistema de 5 Niveis com Temas

O jogo possui 5 niveis fixos (level design estatico) com temas visuais e mecanicos distintos, em dificuldade progressiva.

**Niveis:**

| Nivel | Tema | Descricao Visual | Mecanica/Obstaculos |
|-------|------|-----------------|---------------------|
| 1 | Armazem | Texturas de madeira/metal, caixas empilhadas | Caixas simples como obstaculos. Caminho relativamente direto. |
| 2 | Escritorio | Texturas de piso laminado, tons neutros | Obstaculos retangulares (mesas/estantes). Mais obstaculos que nivel 1. |
| 3 | Cidade | Texturas de asfalto/concreto, tons cinza | Paredes altas (predios). Caminhos mais estreitos, necessidade de rotacoes precisas. |
| 4 | Floresta | Texturas verdes/terra, tons naturais | Obstaculos circulares/irregulares (arvores). Caminhos sinuosos. |
| 5 | Fabrica | Texturas metalicas, tons escuros | Combinacao de todos os tipos: caixas + paredes + obstaculos irregulares. Caminho complexo. |

**Regras:**
- Os layouts sao fixos: posicoes de obstaculos e pontos A/B sao sempre as mesmas para cada nivel
- A distancia entre A e B e fixa (mesma para todos os niveis). A dificuldade vem dos obstaculos
- O visual muda via reskin dos obstaculos existentes (caixas, paredes): texturas/cores diferentes por tema. Nao sao necessarios modelos 3D novos
- O jogador deve completar os niveis em sequencia (1 -> 2 -> 3 -> 4 -> 5)
- Nao e possivel pular niveis

**Cenarios de erro:**
- Assets de textura nao carregam: usar cor solida como fallback

### RF03 - Condicao de Vitoria por Nivel

O jogador completa um nivel levando o robo do ponto A ao ponto B.

**Regras:**
- Condicao: distancia do robo ao ponto B menor que WIN_DISTANCE (25 unidades), enquanto o robo nao esta animando
- Ao completar, mostra animacao de vitoria (pulsacao no marcador B, banner "PARABENS!")
- A mesma condicao se aplica a todos os 5 niveis

**Cenarios de erro:**
- Robo fica preso (nao consegue chegar a B): jogador pode usar botao "Reiniciar Posicao" ou continuar tentando comandos

### RF04 - Controle via Chat com IA

Durante o jogo, o jogador controla o robo exclusivamente via chat com a IA.

**Regras:**
- O chat completo com historico de conversa fica visivel durante o jogo
- O jogador escreve instrucoes em linguagem natural (ex: "ande 40cm para frente e vire a esquerda")
- A IA traduz para LBML e o robo executa
- O historico de chat persiste dentro do nivel (limpa ao mudar de nivel ou nao - a criterio de UX)
- Nao existe controle via botoes direcionais no modo gamificado

**Cenarios de erro:**
- IA retorna LBML invalido: mostrar mensagem de erro e permitir novo input
- IA indisponivel: mostrar mensagem e manter o chat funcional para retry

### RF05 - Timer por Nivel

Cada nivel tem seu proprio timer. O tempo total no leaderboard e a soma dos tempos dos 5 niveis.

**Regras:**
- Timer inicia quando o nivel carrega (jogador ve a arena e pode enviar comandos)
- Timer NAO pausa entre envios de comando (corre continuamente)
- Timer para quando a condicao de vitoria e atingida
- Timer e exibido na UI durante o jogo (formato MM:SS ou SS.ms)
- Ao reiniciar posicao do robo (retry), o timer continua correndo
- Tempo total = soma dos 5 timers individuais

**Cenarios de erro:**
- Jogador fecha aba durante um nivel: progresso perdido, sem registro parcial

### RF06 - Tela de Transicao entre Niveis

Ao completar um nivel, uma tela de transicao aparece antes do proximo nivel.

**Regras:**
- Mostra: nome do nivel completado, tempo do nivel, botao "Proximo Nivel"
- O timer do proximo nivel NAO inicia ate o jogador clicar "Proximo Nivel"
- No nivel 5 (ultimo), nao mostra "Proximo Nivel" mas sim redireciona para a tela de vitoria final

### RF07 - Tela de Vitoria Final

Ao completar os 5 niveis, exibe um resumo detalhado.

**Regras:**
- Mostra: tempo de cada nivel individualmente, tempo total, posicao no leaderboard (se nickname fornecido)
- Campo para informar nickname (obrigatorio para entrar no leaderboard)
- Botoes: "Salvar no Leaderboard" (exige nickname), "Jogar Novamente" (inicia novo run do nivel 1)
- Se o jogador nao fornecer nickname, o run NAO e salvo no leaderboard

**Cenarios de erro:**
- Backend indisponivel ao salvar: mostrar erro, permitir retry ou copiar tempo para compartilhar manualmente
- Nickname vazio: botao "Salvar" desabilitado

### RF08 - Leaderboard

Ranking global de jogadores que completaram os 5 niveis.

**Regras:**
- Mostra todos os registros, sem limite (lista completa)
- Ordenado por tempo total (menor tempo no topo)
- Um mesmo nickname pode aparecer multiplas vezes (multiplos runs)
- Colunas: posicao, nickname, tempo total, data/hora do run
- Acessivel pelo menu principal (sem precisar jogar)
- Persistido no backend Spring Boot (banco de dados)

**Cenarios de erro:**
- Backend indisponivel: mensagem "Leaderboard indisponivel no momento"
- Lista vazia: mensagem "Nenhum jogador completou os 5 niveis ainda. Seja o primeiro!"

### RF09 - Reiniciar Posicao (Retry)

Botao para o jogador resetar a posicao do robo quando estiver preso.

**Regras:**
- Botao "Reiniciar Posicao" visivel durante o jogo
- Ao clicar: robo volta para o ponto A com rotacao 0
- Timer NAO para e NAO reseta (continua correndo)
- Pode ser usado quantas vezes quiser, sem penalidade alem do tempo gasto
- Nao limpa o historico de chat

### RF10 - Modo Controle em Pagina Separada

O modo controle (virtual controls) migra para uma rota/pagina propria, separada do jogo.

**Regras:**
- Acessivel pelo menu principal, opcao "Modo Controle"
- Funciona exatamente como hoje (botoes direcionais, timeline de comandos, geracao de dados)
- NAO ha interacao com o sistema de niveis/game: e uma ferramenta separada
- Se o jogador estiver no meio de um run gamificado e navegar para o Modo Controle, exibir modal de confirmacao antes

### RF11 - Modal de Confirmacao ao Sair do Jogo

Protege o jogador de perder progresso acidentalmente.

**Regras:**
- Exibido quando o jogador tenta navegar para fora do jogo (menu, modo controle) durante um run ativo
- Texto: "Voce vai perder todo o progresso do jogo. Tem certeza?"
- Opcoes: "Sim, sair" (perde tudo, navega) e "Cancelar" (volta pro jogo)
- NAO exibido se o jogador ainda nao comecou (esta no menu)

### RF12 - Avaliacao das Respostas da IA

O jogador e incentivado a avaliar a qualidade da traducao NL->LBML feita pela IA.

**Regras:**
- Apos cada resposta da IA no chat, exibir sistema de rating de 1-5 estrelas
- O que esta sendo avaliado: "A IA entendeu corretamente o que voce pediu?"
- Avaliacao e OPCIONAL, mas com incentivo visual (estrelas em destaque, lembrete sutil se nao avaliou)
- Nao bloqueia o envio do proximo comando
- A avaliacao e salva junto com os dados de treino (frase do usuario + LBML gerado + rating)

**Cenarios de erro:**
- Jogador nao avalia: dado de treino e salvo sem rating (campo null)
- Backend indisponivel: avaliacao perdida, sem retry

### RF13 - Geracao Automatica de Dados de Treino

Toda interacao no modo gamificado gera dados de treino automaticamente.

**Regras:**
- Cada interacao salva: texto em linguagem natural do usuario, LBML gerado pela IA, avaliacao (1-5 ou null), nivel atual, timestamp
- Salvamento e automatico e transparente (jogador nao precisa fazer nada)
- Usa o mesmo backend/endpoint que o modo controle ja usa para salvar sessoes
- Dados sao salvos independentemente de o jogador completar o nivel ou nao

**Cenarios de erro:**
- Backend indisponivel: dados sao perdidos (nao ha fila local). Jogo continua normalmente.

## Requisitos Nao-Funcionais

- RNF01: O timer deve ter precisao de pelo menos 1 segundo
- RNF02: A troca de nivel (carregar novo layout/texturas) deve ser rapida (< 2s)
- RNF03: O leaderboard deve suportar pelo menos 1000 registros sem degradacao de performance na listagem
- RNF04: Os niveis devem funcionar em navegadores modernos (Chrome, Firefox, Safari) sem queda de framerate perceptivel

## Glossario / Definicoes

- **LBML**: Linguagem de comandos do robo. Ex: `D40F;R90L;D20F;` (Distancia 40 Frente, Rotacao 90 Esquerda, Distancia 20 Frente)
- **Run**: Uma tentativa completa de passar pelos 5 niveis, do inicio ao fim
- **Nivel**: Um dos 5 estagios fixos do jogo, cada um com tema/obstaculos proprios
- **Ponto A**: Posicao inicial do robo (marcador verde)
- **Ponto B**: Posicao objetivo/meta (marcador vermelho)
- **Modo Controle**: Interface de botoes direcionais para geracao de dados de treino (separada do jogo)
- **Reskin**: Alterar aparencia visual (texturas/cores) de objetos existentes sem mudar geometria
- **WIN_DISTANCE**: Distancia minima do robo ao ponto B para considerar nivel completo (25 unidades)

## Premissas

- O backend Spring Boot (`lbot-datagen-backend`) esta funcional e aceita novos endpoints
- As texturas/cores diferentes por nivel podem ser implementadas via Three.js sem assets externos pesados
- A IA (modelo de traducao NL->LBML) ja esta integrada e funcional no chat existente
- O nivel de dificuldade dos layouts sera definido na fase de tech-spec/implementacao com base nos obstaculos que ja existem no codigo
- Arena mantém dimensoes 400x400 para todos os niveis

## Fora de Escopo

- Autenticacao/login de usuarios (apenas nickname simples ao final)
- Modelos 3D novos/customizados (apenas reskin via texturas/cores)
- Modo multiplayer ou competicao em tempo real
- Persistencia de progresso parcial entre sessoes (fechou = perdeu)
- Sistema de conquistas/badges
- Customizacao do robo
- Modo controle virtual dentro do jogo (fica em pagina separada)
- Responsividade mobile (foco em desktop)
- Internacionalizacao (interface em portugues)

## Cenarios de Aceite

### CA01 - Fluxo completo de jogo (happy path)
**Dado** que o jogador esta no menu principal
**Quando** clica em "Jogar"
**Entao** o nivel 1 (Armazem) carrega com ponto A, ponto B, obstaculos tematicos e timer inicia

### CA02 - Completar um nivel
**Dado** que o jogador esta no nivel 1 e o robo atingiu o ponto B
**Quando** a distancia do robo ao ponto B e menor que 25 unidades
**Entao** o timer do nivel para, animacao de vitoria toca, e tela de transicao aparece com tempo e botao "Proximo Nivel"

### CA03 - Progressao entre niveis
**Dado** que o jogador completou o nivel 2 e esta na tela de transicao
**Quando** clica em "Proximo Nivel"
**Entao** o nivel 3 (Cidade) carrega com seu tema visual e obstaculos proprios, e um novo timer inicia

### CA04 - Completar todos os 5 niveis
**Dado** que o jogador completou o nivel 5
**Quando** a tela de vitoria final aparece
**Entao** mostra tempo de cada nivel, tempo total, campo para nickname, e botoes "Salvar no Leaderboard" e "Jogar Novamente"

### CA05 - Salvar no leaderboard
**Dado** que o jogador completou os 5 niveis e esta na tela de vitoria final
**Quando** preenche nickname "JoaoBot" e clica "Salvar no Leaderboard"
**Entao** o registro aparece no leaderboard com nickname, tempo total e data

### CA06 - Visualizar leaderboard
**Dado** que o jogador esta no menu principal
**Quando** clica em "Leaderboard"
**Entao** ve a lista completa de jogadores ordenada por menor tempo total

### CA07 - Reiniciar posicao do robo
**Dado** que o jogador esta no nivel 3 e o robo esta preso entre obstaculos
**Quando** clica em "Reiniciar Posicao"
**Entao** o robo volta ao ponto A com rotacao 0, e o timer continua correndo

### CA08 - Sair do jogo durante um run
**Dado** que o jogador esta no nivel 3 com timer correndo
**Quando** tenta voltar ao menu principal
**Entao** modal aparece com "Voce vai perder todo o progresso. Tem certeza?" com opcoes "Sim, sair" e "Cancelar"

### CA09 - Avaliar resposta da IA
**Dado** que a IA respondeu com um comando LBML no chat
**Quando** o jogador clica em 3 estrelas
**Entao** a avaliacao e salva junto com o par (texto NL, LBML) no backend

### CA10 - Nao avaliar resposta da IA
**Dado** que a IA respondeu com um comando LBML no chat
**Quando** o jogador NAO clica em nenhuma estrela e envia novo comando
**Entao** o dado de treino e salvo com rating=null, proximo comando e enviado normalmente

### CA11 - Acessar modo controle
**Dado** que o jogador esta no menu principal
**Quando** clica em "Modo Controle"
**Entao** navega para pagina separada com interface de botoes direcionais (funciona como hoje)

### CA12 - Timer nao pausa no retry
**Dado** que o jogador esta no nivel 2 com timer em 01:30
**Quando** clica em "Reiniciar Posicao"
**Entao** robo volta ao ponto A e timer continua (ex: 01:32, 01:33...)

### CA13 - Multiplos runs no leaderboard
**Dado** que "JoaoBot" ja completou os 5 niveis uma vez com tempo 05:00
**Quando** completa novamente com tempo 04:30 e salva
**Entao** ambos os registros aparecem no leaderboard (JoaoBot 04:30 e JoaoBot 05:00)

### CA14 - Recusar sair do jogo
**Dado** que o modal de confirmacao esta visivel
**Quando** o jogador clica "Cancelar"
**Entao** o modal fecha e o jogo continua normalmente com timer correndo
