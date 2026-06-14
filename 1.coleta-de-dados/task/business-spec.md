# Especificacao de Negocio: Redesign dos Niveis do Lbot Arena

## Contexto

O Lbot Arena e um jogo 3D onde o jogador comanda um robo usando linguagem natural (convertida para LBML - Lbot Markup Language) para navegar de um ponto A ate um ponto B em uma arena com obstaculos. O jogo possui 5 niveis pre-definidos que atualmente apresentam os seguintes problemas:

1. **Visualmente feios**: Os obstaculos sao apenas caixas simples (BoxGeometry) com uma cor unica. O chao e um plano plano sem detalhes. Nao ha modelos compostos, texturas (procedurais) ou detalhes visuais.
2. **Dificuldade sem logica**: A progressao de dificuldade entre os niveis nao e clara. Niveis mais avancados nem sempre sao mais dificeis que os anteriores. Mecanicas como rampas aparecem apenas no nivel 5, sem introducao gradual.
3. **Botao "Novo Desafio" inadequado**: No modo de niveis fixos (Jogar Desafios), existe um botao "Novo Desafio" que randomiza as posicoes A e B. Isso nao faz sentido para um jogo com niveis pre-definidos e deve ser removido.

Esta tarefa visa redesenhar os 5 niveis com modelos visuais mais elaborados (usando geometrias basicas do Three.js combinadas), uma progressao de dificuldade baseada no numero de comandos LBML necessarios, e remover o botao "Novo Desafio" de todos os modos.

---

## Requisitos Funcionais

### RF01 - Redesign Visual dos Obstaculos
Todos os obstaculos dos niveis devem ser modelos compostos usando geometrias basicas do Three.js (BoxGeometry, CylinderGeometry, SphereGeometry, ConeGeometry, etc.) combinadas proceduralmente. Nao e permitido usar assets de imagem/texturas externas.

**Exemplos de modelos compostos esperados:**
- **Caixas/Empilhamentos**: Empilhamento de 2-3 caixas de tamanhos variados para criar pilhas de caixas
- **Paredes/Barreiras**: Paredes compostas de multiplos blocos ou com pilastras decorativas
- **Arvores**: Tronco (cilindro) + copa (esfera ou cone)
- **Ramps**: Plataforma inclinada com laterais (barreiras) e textura de grade
- **Estruturas industriais**: Colunas (cilindros) + vigas (caixas) + tanques (cilindros + esferas)

**Regras:**
- Cada tipo de obstaculo (`ObstacleType`) deve ter uma funcao de geracao de mesh composta
- O corpo de fisica (Cannon.js) pode continuar sendo uma caixa simples (approximacao) para performance
- As cores devem seguir o tema do nivel, mas com variacoes de tonalidade para diferentes partes do mesmo modelo
- Manter performance: no maximo 3-4 geometrias por obstaculo

**Cenarios de erro:**
- Se um tipo de obstaculo nao tiver um gerador de mesh composto definido: usar fallback de caixa simples

### RF02 - Progressao de Dificuldade Gradual
A dificuldade de cada nivel deve ser medida pelo numero estimado de comandos LBML necessarios para completar (do ponto A ao ponto B). A progressao deve ser:

| Nivel | Comandos Estimados | Mecanicas |
|-------|-------------------|-----------|
| 1 | 3-5 | Apenas crates/caixas simples. Caminho quase reto, poucos obstaculos. |
| 2 | 5-8 | Introduz **paredes**. Paredes que bloqueiam caminhos diretos, forcando o jogador a desviar. |
| 3 | 8-12 | Introduz **rampas**. O jogador precisa subir uma rampa para prosseguir. |
| 4 | 12-16 | Introduz **obstaculos rotacionados**. Angulos que forcam caminhos em zig-zag. Mais obstaculos. |
| 5 | 16-20 | **Combina todas as mecânicas**: paredes + rampas + obstaculos rotacionados + corredores mais estreitos. |

**Regras:**
- O numero de obstaculos deve aumentar com o nivel (aproximadamente: Nivel 1 = 3-4, Nivel 2 = 5-7, Nivel 3 = 7-9, Nivel 4 = 9-11, Nivel 5 = 11-13)
- Nivel 1 deve ser passivel de completar com comandos quase que em linha reta (ex: D200, D200, D200)
- Cada nivel deve introduzir no maximo 1 mecanica nova (a nao ser que a mecanica seja uma combinacao natural)
- A distancia A->B deve ser mantida em aproximadamente 300-424 unidades para todos os niveis

**Cenarios de erro:**
- Se o layout de um nivel impossibilitar completar (sem caminho valido): revisar o layout
- Se o nivel for muito facil (completavel em 1-2 comandos): adicionar obstaculos

### RF03 - Posicoes de A e B Variaveis por Nivel
Cada nivel pode ter posicoes diferentes para os pontos de partida (A) e chegada (B), desde que a distancia entre eles seja similar (~300-424 unidades).

**Regras:**
- As posicoes sao definidas no `LevelConfig` de cada nivel (como ja e feito hoje)
- O angulo de partida do robo (rotacao inicial) deve ser sempre 0 graus (olhando para +Z)
- A posicao de A e B deve ser escolhida para que o caminho otimo explore a mecanica do nivel

**Cenarios de erro:**
- Se A ou B ficarem dentro de obstaculos: revisar posicoes

### RF04 - Remover Botao "Novo Desafio"
O botao "Novo Desafio" deve ser completamente removido da interface em todos os modos de jogo (modo de niveis fixos e Modo Controle).

**Regras:**
- Remover o botao do template `robo-simulator.ts` (nao apenas esconder, remover completamente)
- Remover a logica `generateNewLevel()` do componente `robo-simulator` (ou marcar como @deprecated se usada em outro lugar)
- No Modo Controle, A e B devem ser fixos em posicoes genericas (ex: (-80,-80) e (80,80) como no fallback atual)
- No modo de niveis, A e B sempre vem do `LevelConfig`

**Cenarios de erro:**
- Se o Modo Controle quebrar sem o botao: garantir que o simulador inicialize com A/B fixos

### RF05 - Novos Nomes Tematicos para os Niveis
Os nomes dos niveis devem ser alterados para refletir os novos designs e temas. Os novos nomes serao propostos pelo agente durante a fase tech-spec, mas devem seguir a logica:

- Nivel 1: Nome relacionado a simplicidade, treinamento, ou campo aberto
- Nivel 2: Nome relacionado a estruturas, divisoes, ou escritorios
- Nivel 3: Nome relacionado a elevacao, construcao, ou cidade
- Nivel 4: Nome relacionado a floresta, natureza, ou caminho sinuoso
- Nivel 5: Nome relacionado a fabrica, industria, ou complexo

**Regras:**
- Nomes devem ser em portugues
- Nomes devem ter entre 1-3 palavras
- Devem ser significativos para o jogador entender o tema do nivel

### RF06 - Novas Cores Tematicas
As cores de cada nivel devem ser completamente alteradas para combinar melhor com os novos designs e criar identidade visual.

**Regras:**
- Cada nivel deve ter uma paleta distinta (ground, wall, obstacle, sky)
- As cores devem ter contraste suficiente para legibilidade (robo, marcadores A/B)
- Cores devem ser hex strings validas
- A cor dos obstaculos pode ter variacoes (ex: partes mais claras/escuras do mesmo modelo) usando variacoes da cor base do tema

---

## Requisitos Nao-Funcionais

- **Performance**: Cada obstaculo composto deve ter no maximo 4 geometrias. Nao deve haver impacto perceptivel no FPS (manter 60 FPS em hardware moderno).
- **Procedural**: Nenhum asset de imagem/textura externa pode ser adicionado. Tudo deve ser gerado via codigo (Three.js geometries, CanvasTexture para texturas simples se necessario).
- **Compatibilidade**: A alteracao deve ser compativel com o sistema de fisica atual (Cannon-es). O corpo de fisica pode ser uma aproximacao (caixa simples) mesmo que a mesh visual seja composta.

---

## Glossario / Definicoes

- **LBML**: Lbot Markup Language. Comandos que o robo entende (ex: D200 = andar 200 unidades, R90 = rotacionar 90 graus).
- **Modelo Composto**: Uma mesh visual formada por multiplas geometrias Three.js agrupadas (THREE.Group), representando um objeto mais complexo que uma caixa simples.
- **ObstacleType**: Tipos de obstaculos: 'crate' (caixa/pilha), 'wall' (parede/barreira), 'ramp' (rampa inclinada). Podem ser expandidos para novos tipos se necessario.
- **Modo Controle**: Pagina `/controls` onde o usuario pode comandar o robo manualmente sem a estrutura de niveis/timers.
- **Novo Desafio**: Funcionalidade que randomiza posicoes A e B no simulador. Serah removida.

---

## Premissas

- O numero de niveis permanece fixo em 5.
- O tamanho da arena permanece 400x400 unidades (limites de -200 a +200).
- A velocidade e rotacao do robo permanecem inalteradas.
- O sistema de fisica (Cannon-es) e renderizacao (Three.js) permanecem os mesmos.
- O leaderboard existente nao sera afetado por esta tarefa (sera tratado em tarefa separada).
- A dificuldade e medida pelo numero de comandos LBML necessarios, nao pelo tempo.
- O robo sempre comeca com rotacao 0 (olhando para +Z).

---

## Fora de Escopo

- Alteracoes no backend (API, leaderboard, banco de dados).
- Adicao de assets de imagem/texturas externas.
- Adicao de novas bibliotecas 3D (Three.js addons novos).
- Alteracao na mecanica de movimento do robo (velocidade, fisica, rotacao).
- Adicao de novos tipos de comandos LBML.
- Sistema de save/load de progresso.
- Niveis adicionais alem dos 5 existentes.
- IA/NPCs ou obstaculos moveis (fora do escopo de mecanicas por agora).
- Mobile/responsive layout (nao e parte desta tarefa).

---

## Cenarios de Aceite

### CA01 - Nivel 1: Facil e Intuitivo
**Dado** que o jogador iniciou o jogo e esta no Nivel 1  
**Quando** ele visualiza a arena  
**Entao** ele ve poucos obstaculos (3-4) que sao caixas simples ou empilhamentos baixos  
**E** o caminho de A ate B e quase uma linha reta com pequenos desvios  
**E** o nivel pode ser completado com 3-5 comandos LBML

### CA02 - Nivel 2: Introducao de Paredes
**Dado** que o jogador completou o Nivel 1 e avancou para o Nivel 2  
**Quando** ele visualiza a arena  
**Entao** ele ve paredes/barreiras que bloqueiam caminhos diretos  
**E** e necessario desviar pelos lados ou por corredores  
**E** o nivel pode ser completado com 5-8 comandos LBML

### CA03 - Nivel 3: Introducao de Ramps
**Dado** que o jogador esta no Nivel 3  
**Quando** ele visualiza a arena  
**Entao** ele ve uma ou mais rampas no caminho  
**E** o robo precisa subir a rampa para alcancar o proximo trecho ou o objetivo  
**E** o nivel pode ser completado com 8-12 comandos LBML

### CA04 - Nivel 4: Obstaculos Rotacionados
**Dado** que o jogador esta no Nivel 4  
**Quando** ele visualiza a arena  
**Entao** ele ve obstaculos posicionados em angulos (nao alinhados aos eixos X/Z)  
**E** os caminhos formam um padrao de zig-zag  
**E** o nivel pode ser completado com 12-16 comandos LBML

### CA05 - Nivel 5: Desafio Completo
**Dado** que o jogador esta no Nivel 5  
**Quando** ele visualiza a arena  
**Entao** ele ve uma combinacao de todas as mecanicas: paredes, rampas, obstaculos rotacionados  
**E** os corredores sao mais estreitos  
**E** o nivel pode ser completado com 16-20 comandos LBML

### CA06 - Ausencia do Botao "Novo Desafio"
**Dado** que o jogador esta em qualquer modo (Jogar Desafios ou Modo Controle)  
**Quando** ele visualiza a interface do simulador  
**Entao** o botao "Novo Desafio" NAO esta presente na tela

### CA07 - Modelos Visuais Compostos
**Dado** que o jogador esta em qualquer nivel  
**Quando** ele observa os obstaculos  
**Entao** eles NAO sao simples caixas coloridas  
**E** apresentam detalhes visuais (ex: pilhas de caixas, arvores com tronco, rampas com laterais)

### CA08 - Paleta de Cores Distinta
**Dado** que o jogador avanca entre os niveis  
**Quando** cada nivel carrega  
**Entao** as cores do chao, paredes da arena, obstaculos e ceu sao diferentes do nivel anterior  
**E** cada nivel tem uma identidade visual unica

### CA09 - Modo Controle com A/B Fixos
**Dado** que o jogador acessou o Modo Controle  
**Quando** o simulador carrega  
**Entao** os pontos A e B estao em posicoes fixas (ex: (-80,-80) e (80,80))  
**E** nao ha opcao de randomizar suas posicoes

### CA10 - Niveis Completaveis
**Dado** que o jogador esta em qualquer nivel  
**Quando** ele executa comandos LBML validos  
**Entao** existe pelo menos um caminho valido de A ate B que nao colide com obstaculos
