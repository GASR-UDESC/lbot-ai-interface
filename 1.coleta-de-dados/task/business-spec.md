# Especificacao de Negocio: Redesign dos Niveis do Lbot Arena

## Contexto

O Lbot Arena e um jogo web 3D onde o jogador comanda um robo com comandos em linguagem natural (convertidos para LBML) para navegar por niveis e chegar do ponto A ao ponto B. Atualmente o jogo possui 5 niveis com nomes tematicos (Campo de Treino, Escritorio Central, Cidade em Obras, Floresta Misteriosa, Complexo Industrial) e um level design que permite ao jogador chegar ao objetivo facilmente contornando os obstaculos pelos cantos da arena. O jogador deseja um redesign completo da dinamica dos niveis: renomear para "Nivel 1, Nivel 2..." sem temas, e criar um level design que funcione de fato como um labirinto, forçando o uso de componentes (especialmente rampas nos niveis mais altos) e bloqueando os atalhos pelos cantos.

## Requisitos Funcionais

### RF01 - Renomeacao dos Niveis
Todos os 5 niveis existentes devem ser renomeados para nomenclatura numerica simples.

**Regras:**
- Nivel 1: substituir "Campo de Treino" por "Nivel 1"
- Nivel 2: substituir "Escritorio Central" por "Nivel 2"
- Nivel 3: substituir "Cidade em Obras" por "Nivel 3"
- Nivel 4: substituir "Floresta Misteriosa" por "Nivel 4"
- Nivel 5: substituir "Complexo Industrial" por "Nivel 5"
- A nomenclatura deve ser aplicada em todos os pontos de exibicao: HUD, tela de transicao, tela de vitoria, menu, e qualquer referencia textual

**Cenarios de erro:**
- Nenhum; se algum componente nao for atualizado, o nome antigo ainda aparece (deve ser auditado)

### RF02 - Level Design Progressivo com Labirinto
Redesenhar o layout de obstaculos de cada nivel para criar uma progressao de dificuldade que force o jogador a navegar pelo labirinto.

**Regras:**
- Nivel 1: Trivial. Poucos obstaculos no centro, caminho quase reto de A ate B. Serve como tutorial.
- Nivel 2: Desviar. Obstaculos posicionados para forcar desvios, mas sem rampas. O jogador precisa usar comandos de rotacao e movimento para contornar.
- Nivel 3: Primeiro labirinto com rampa obrigatoria. O level design deve bloquear completamente o caminho reto e os cantos. Uma rampa suave (angulo < 15°) deve ser o unico caminho para acessar uma area/plataforma que leva ao B.
- Nivel 4: Labirinto mais denso. Multiplos obstaculos, corredores estreitos, pelo menos uma rampa obrigatoria.
- Nivel 5: Labirinto complexo com multiplas rampas. O layout mais denso de todos, com pelo menos 2 rampas obrigatorias em sequencia ou em diferentes partes do caminho.
- Todas as paredes internas devem bloquear fisicamente os cantos da arena, impedindo que o jogador contorne o labirinto indo pelas bordas.
- O tamanho da arena permanece 400x400.
- Os pontos de partida (A) e objetivo (B) permanecem fixos em (-150, -150) e (150, 150) para todos os niveis.

**Cenarios de erro:**
- Se o jogador ainda conseguir chegar ao B sem passar pela rampa obrigatoria, o nivel nao esta correto
- Se o robo nao conseguir subir a rampa fisicamente (ficar preso), o angulo da rampa ou a velocidade deve ser ajustada

### RF03 - Rampas Obrigatorias nos Niveis 3-5
Nos niveis 3, 4 e 5, o level design deve incluir rampas que sejam parte obrigatoria do caminho para completar o nivel.

**Regras:**
- Rampas devem ter angulo suave (inferior a 15° / ~0.26 rad) para garantir que o robo consiga subir com a velocidade atual de 30 unidades/segundo
- A rampa deve ser posicionada de forma que o caminho direto de A a B seja bloqueado por paredes/ostaculos, e a rampa seja o unico (ou principal) caminho viavel
- Sem sinalizacao visual especial no chao (setas, marcadores). O jogador deve descobrir por tentativa e erro que a rampa e necessaria.
- A fisica da rampa (colisao e subida) deve funcionar corretamente com o motor Cannon-es

**Cenarios de erro:**
- Robo fica preso na rampa: ajustar angulo ou verificar colisao da caixa de fisica
- Robo passa "atraves" da rampa: verificar se o corpo fisico da rampa esta alinhado com a mesh visual

### RF04 - Paredes Internas Bloqueando Cantos
Adicionar paredes ou obstaculos internos que bloqueiem os cantos da arena, forçando o jogador a entrar no labirinto.

**Regras:**
- Nos niveis 2-5, colocar paredes internas proximas aos cantos (ex: a 50-80 unidades dos cantos) que bloqueiem o caminho direto pelas bordas
- As paredes devem ser altas o suficiente (altura >= 15) para que o robo nao consiga "pular" ou contorna-las facilmente
- O layout deve forcar o robo a entrar na area central do labirinto
- Nivel 1 pode ser mais aberto (sem bloqueio de cantos rigido)

**Cenarios de erro:**
- Se o robo ainda conseguir passar pelo espaco entre a parede interna e a parede externa da arena, ajustar posicionamento ou aumentar a largura da parede interna

### RF05 - Cores e Temas Visuais
Manter as 5 paletas de cores existentes (groundColor, wallColor, obstacleColor, skyColor) mas sem nomes tematicos.

**Regras:**
- Cada nivel mantem sua paleta de cores atual:
  - Nivel 1: ground=#7C9A5E, wall=#8B7355, obstacle=#A67B5B, sky=#87CEEB
  - Nivel 2: ground=#D3D3D3, wall=#808080, obstacle=#A9A9A9, sky=#B0C4DE
  - Nivel 3: ground=#696969, wall=#2F4F4F, obstacle=#708090, sky=#778899
  - Nivel 4: ground=#228B22, wall=#8B4513, obstacle=#006400, sky=#98FB98
  - Nivel 5: ground=#2F4F4F, wall=#1C1C1C, obstacle=#FF6600, sky=#404040
- As texturas das paredes externas da arena devem ser UNIFORMES em todos os niveis (remover as variacoes tematicas: wooden planks, concrete panels, tree trunks, etc.)
- As paredes externas devem ter uma aparencia neutra e consistente (ex: cor solida wallColor, ou textura simples uniforme)
- O chao e obstaculos mantem suas texturas/cores tematicas

**Cenarios de erro:**
- Nenhum critico; inconsistencia visual e de baixa prioridade

### RF06 - Atualizacao de Referencias Textuais
Atualizar todos os componentes que referenciam os nomes dos niveis para usar a nomenclatura "Nivel X".

**Regras:**
- HUD (game.page.html): exibir "Nivel {{ numero }}" e "Nivel X" no lugar do nome tematico
- Tela de transicao (level-transition): exibir "Nivel X concluido" e "Proximo: Nivel Y"
- Tela de vitoria (victory-screen): exibir os tempos como "Nivel 1: 00:00", "Nivel 2: 00:00", etc.
- Menu (menu.page.html): atualizar subtitulo se houver referencia a temas
- Chat/LBML: o chat deve referenciar genericamente "Nivel X" sem descrever o layout especifico
- Leaderboard: manter a estrutura atual (level1TimeMs, level2TimeMs...) sem alterar schema de dados

**Cenarios de erro:**
- Se algum componente usar o nome antigo, o jogador vera texto inconsistente

## Requisitos Nao-Funcionais

- **RNF01 - Performance**: O numero de obstaculos nos niveis 4 e 5 pode aumentar significativamente. Deve-se garantir que a contagem de corpos fisicos nao degrade a performance abaixo de 60 FPS.
- **RNF02 - Fisica**: A adicao de mais paredes e rampas nao deve causar instabilidade no motor de fisica Cannon-es (robos presos, travamentos, colisoes fantasmas).
- **RNF03 - Compatibilidade**: Manter compatibilidade com o formato `LevelConfig` existente; nao criar novos tipos de obstaculos ou campos no modelo.

## Glossario / Definicoes

- **LBML**: Linguagem de comando do robo (ex: D10 F, R90, etc.) gerada a partir de linguagem natural pelo chat.
- **Nivel**: Uma fase do jogo com um layout de obstaculos, cores e ponto de partida A e objetivo B.
- **Rampa obrigatoria**: Uma rampa que e fisicamente o unico caminho para chegar ao ponto B, pois todas as outras rotas estao bloqueadas por paredes/obstaculos.
- **Parede interna**: Obstaculo do tipo 'wall' posicionado no interior da arena (nao nas bordas externas) para criar o labirinto.
- **Parede externa**: Parede de limite da arena (bordas norte, sul, leste, oeste).

## Premissas

- O robo inicia em A=(-150, -150) e deve chegar em B=(150, 150) em todos os niveis.
- A velocidade do robo permanece 30 unidades/segundo e a velocidade de rotacao 90 graus/segundo.
- A arena tem tamanho 400x400 (limite de -200 a +200 em X e Z).
- A distancia de vitoria (WIN_DISTANCE) permanece 25 unidades.
- O sistema de leaderboard, chat, e timer nao sofrem alteracoes de regra/negocio, apenas texto exibido.
- Nao ha novos tipos de obstaculos; usamos apenas os existentes: wall, crate, ramp, tree, barrier, stack, industrial.
- A fisica de subida de rampa com o robo atual funciona corretamente se o angulo for suave (<15°).

## Fora de escopo

- Criar novos tipos de obstaculos (portoes, portas, plataformas, etc.)
- Alterar mecanicas de movimento do robo (velocidade, aceleracao, pulo)
- Alterar o sistema de pontuacao/score (contador de PONTOS)
- Alterar o sistema de chat/LBML (apenas texto exibido)
- Alterar o schema de dados do leaderboard (apenas labels exibidos)
- Criar novos componentes de UI (apenas textos existentes)
- Adicionar sons, musica ou efeitos visuais novos

## Cenarios de Aceite

### CA01 - Nivel 1 e trivial
**Dado** que o jogador inicia o Nivel 1
**Quando** ele executa comandos de movimento direto (ex: "ir para frente 424 unidades")
**Entao** ele deve conseguir chegar ao B com poucos ou nenhum desvio, e o tempo deve ser proximo do tempo minimo teórico (~14 segundos)

### CA02 - Nivel 2 exige desvios
**Dado** que o jogador inicia o Nivel 2
**Quando** ele tenta ir em linha reta de A ate B
**Entao** ele deve colidir com obstaculos e precisar usar rotacoes (L/R) para contornar, nao podendo chegar em linha reta

### CA03 - Nivel 3 tem rampa obrigatoria
**Dado** que o jogador inicia o Nivel 3
**Quando** ele tenta chegar ao B sem subir a rampa (indo pelos cantos ou por outros caminhos)
**Entao** ele deve ser bloqueado por paredes/obstaculos e nao conseguir chegar ao B
**E** quando ele subir a rampa e continuar o caminho, ele deve conseguir chegar ao B

### CA04 - Cantos bloqueados nos niveis 2-5
**Dado** que o jogador esta no Nivel 2, 3, 4 ou 5
**Quando** ele tenta ir diretamente para um canto da arena e contornar o labirinto pela borda
**Entao** ele deve encontrar uma parede interna que bloqueia o caminho, forçando-o a voltar para o centro

### CA05 - Nomes atualizados em todas as telas
**Dado** que o jogador esta jogando qualquer nivel
**Quando** ele olha para o HUD, tela de transicao, ou tela de vitoria
**Entao** ele deve ver apenas "Nivel 1", "Nivel 2", etc., sem nenhum nome tematico como "Campo de Treino" ou "Floresta Misteriosa"

### CA06 - Paredes externas uniformes
**Dado** que o jogador esta visualizando a arena
**Quando** ele compara as paredes externas entre niveis diferentes
**Entao** elas devem ter aparencia consistente (mesma textura/material), variando apenas a cor conforme o tema

### CA07 - Fisica de rampa funciona
**Dado** que o robo esta no inicio de uma rampa no Nivel 3, 4 ou 5
**Quando** ele executa um comando de movimento para frente (F)
**Entao** ele deve subir a rampa fisicamente, sem ficar preso, derrapar para fora, ou passar atraves da rampa

### CA08 - Leaderboard continua funcionando
**Dado** que o jogador completa os 5 niveis
**Quando** ele salva no leaderboard
**Entao** os tempos de cada nivel devem ser salvos corretamente na estrutura existente (level1TimeMs, level2TimeMs, etc.) e exibidos como "Nivel 1: 00:00", "Nivel 2: 00:00", etc.
