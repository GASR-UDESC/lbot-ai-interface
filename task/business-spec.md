# Especificacao de Negocio: Expansao LBML com Curvas, Correcao de Fisica e Redesign de Niveis

## Contexto

O projeto lbot-ai-interface inclui um modulo de geracao de dados (lbot-datagen) que implementa um jogo onde um robo virtual navega por arenas com obstaculos. O robo eh controlado por comandos LBML (L-Bot Markup Language), e os dados gerados servem para treinar uma IA que traduz linguagem natural em comandos LBML.

Atualmente, a LBML suporta apenas movimentos retilineos (D - distancia) e rotacoes in-place (R - rotacao), limitando o robo a andar em linhas retas e girar no proprio eixo. O robo real possui 2 rodas independentes que permitem curvas suaves, mas a linguagem nao comporta isso.

Alem disso, existem problemas na fisica do jogo (barreiras da arena nao tem corpos de colisao, permitindo o robo atravessa-las) e no level design (obstaculos posicionados de forma que o usuario pode simplesmente contornar pelos cantos sem precisar desviar).

Esta tarefa visa resolver esses 3 problemas no modulo lbot-datagen.

## Requisitos Funcionais

### RF01 - Novo Comando LBML: Arco (A)

Adicionar um novo tipo de comando a linguagem LBML que permite ao robo executar movimentos em arco (curvas).

**Sintaxe:** `A<raio><direcao><angulo>;`

- `A` - Prefixo identificador do comando de arco
- `<raio>` - Numero inteiro positivo representando o raio da curva (mesma unidade do comando D)
- `<direcao>` - `L` (esquerda) ou `R` (direita), indica o lado para o qual o robo curva
- `<angulo>` - Numero inteiro positivo representando o angulo total do arco em graus

**Exemplos:**
- `A30R90;` - Arco com raio 30, curvando para a direita, 90 graus
- `A50L180;` - Arco com raio 50, curvando para a esquerda, 180 graus (meia volta)
- `A20R360;` - Arco com raio 20, curvando para a direita, volta completa

**Regras:**
- O raio usa a mesma unidade de distancia do comando D
- Nao ha limite minimo ou maximo para raio ou angulo
- O centro do arco fica perpendicular a direcao frontal do robo, deslocado para o lado indicado pela direcao
- O robo percorre o arco mantendo sua frente tangente a curva (como um carro fazendo curva)
- O comando eh retrocompativel: comandos D e R existentes continuam funcionando normalmente
- O comando `D<n>L;` e `D<n>R;` mantem seu comportamento atual (giro 90 graus + andar reto)

**Regex do comando:** `/^A(\d+)([LR])(\d+);$/`

**Regex atualizada da sequencia LBML:** `/^(D\d+[FBLR];|R\d+[LR];|A\d+[LR]\d+;)+$/`

**Cenarios de erro:**
- Raio zero (`A0R90;`): Comando sintaticamente valido, comportamento equivalente a rotacao in-place
- Angulo zero (`A30R0;`): Comando sintaticamente valido, nenhum movimento executado

### RF02 - Correcao das Barreiras da Arena (Fisica de Colisao)

As paredes da arena e obstaculos devem impedir fisicamente o robo de atravessa-los.

**Regras:**
- Todas as paredes da arena devem ter corpos de colisao (physics bodies) associados
- Todos os obstaculos (crates, walls, ramps) devem ter corpos de colisao
- Quando o robo colide com qualquer barreira, ele para completamente naquela direcao
- A colisao bloqueia apenas o comando LBML atual em execucao; os proximos comandos da sequencia continuam sendo executados normalmente
- O robo para no ponto exato da colisao (nao desliza, nao quica, nao atravessa)
- Comportamento durante arco (comando A): se houver colisao no meio de um arco, o robo para no ponto exato da colisao e segue para o proximo comando

**Cenarios de erro:**
- Robo pressionado contra parede por varios comandos consecutivos: cada comando tenta mover, colide, para, e o proximo eh executado
- Colisao em angulo durante arco: robo para no ponto de contato

### RF03 - Redesign dos Niveis com Progressao de Dificuldade

Os 5 niveis existentes devem ser completamente redesenhados com uma progressao logica de dificuldade.

**Regras:**
- **Nivel 1-2 (Iniciante):** Resolviveis apenas com comandos D (distancia) e R (rotacao). Obstaculos posicionados de forma que o jogador PRECISA desviar (nao pode contornar pelos cantos). Caminho obrigatorio com desvios usando giros.
- **Nivel 3-4 (Intermediario):** Exigem o uso de curvas (comando A) para completar. Corredores curvos, chicanes, ou passagens que so podem ser navegadas com arcos.
- **Nivel 5 (Avancado):** Exige curvas E rampas. O robo precisa subir em rampas como parte do percurso obrigatorio.

**Formato da arena variavel por nivel:**
- Arenas podem ser quadradas, retangulares ou circulares dependendo do nivel
- O formato deve ser configuravel na definicao do nivel

**Pontos de partida e chegada variaveis:**
- Os pontos de start e goal podem variar por nivel (nao mais fixos em -150,-150 e 150,150)
- Posicionados para criar percursos mais interessantes e forcar o uso das mecanicas de cada nivel

**Rampas (niveis avancados):**
- Rampas funcionam como terreno inclinado (robo sobe naturalmente ao encontrar)
- Rampas tambem podem funcionar como pontes/passarelas sobre obstaculos abaixo
- Ambos os usos sao validos e devem ser explorados no level design

**Criterio de sucesso do nivel:**
- O jogador completa o nivel ao chegar ao ponto de destino (goal)
- Nao ha metricas de otimizacao (numero de comandos, tempo, etc.) que impedem a conclusao
- Colisoes nao impedem a conclusao, apenas interrompem o comando atual

### RF04 - Refazer Prompt de Conversao LLM para LBML

O prompt que instrui o LLM a converter linguagem natural em comandos LBML no backend Spring Boot deve ser completamente refeito.

**Regras:**
- O novo prompt deve documentar todos os comandos LBML (D, R, e o novo A)
- Deve incluir exemplos de uso do comando A em contextos de navegacao
- Deve ser capaz de interpretar instrucoes como "faca uma curva para a direita" e gerar o comando A adequado
- Deve manter a capacidade de gerar comandos D e R para movimentos simples

**Cenarios de erro:**
- Instrucao ambigua do usuario (ex: "vire"): o LLM deve usar R para giro in-place por padrao, a menos que o contexto indique curva

## Requisitos Nao-Funcionais

- A validacao LBML no datagen deve ser apenas sintatica (verificar formato correto do comando A, nao simular caminho)
- A animacao do arco no frontend deve ser suave e representar fielmente a geometria do arco
- Nao eh necessario trail/rastro visual do caminho do arco; apenas a animacao do robo se movendo eh suficiente
- Os niveis redesenhados devem ser visivelmente diferentes entre si (variar cores, formatos de arena, tipos de obstaculos)

## Glossario / Definicoes

- **LBML (L-Bot Markup Language):** Linguagem de marcacao para controle do robo. Sequencia de comandos separados por ponto-e-virgula.
- **Arco:** Movimento curvo em que o robo percorre um trecho de circunferencia, mantendo sua frente tangente a curva.
- **Raio do arco:** Distancia do centro da circunferencia ao robo durante o movimento curvo. Raio maior = curva mais aberta; raio menor = curva mais fechada.
- **Point-turn / Rotacao in-place:** Rotacao do robo sobre seu proprio eixo central, sem deslocamento translacional (comando R).
- **Physics body:** Corpo de colisao invisivel no motor de fisica (Cannon-es) que impede objetos de se atravessarem.
- **lbot-datagen:** Modulo do projeto que implementa o jogo de navegacao e gera dados para treinamento de IA. Composto por frontend Angular e backend Spring Boot.
- **Chicane:** Sequencia de curvas alternadas em S que forca o robo a fazer manobras curvas.

## Premissas

- O motor de fisica Cannon-es suporta corpos de colisao para todas as geometrias necessarias (box, plane, cylinder)
- A arena circular pode ser aproximada por um poligono de muitos lados ou usar um corpo cilindrico no Cannon-es
- O frontend Angular ja possui infraestrutura de renderizacao 3D (Three.js) e fisica (Cannon-es) para suportar as mudancas
- O LBML eh compartilhado entre modulos via arquivo `shared/lbml.ts` (ou equivalente no contexto do datagen)
- O backend Spring Boot tem acesso ao prompt de conversao LLM e este pode ser editado sem mudancas estruturais
- Os 5 niveis redesenhados substituem os atuais (nao eh aditivo)

## Fora de Escopo

- Modulo lbot-simulator-web (simulador 3D separado) - nao sera alterado nesta tarefa
- Modulo lbot-brain - nao sera alterado
- Modulo lbot-natural-language-controller - nao sera alterado
- Modulo lbot-socket-control - nao sera alterado
- Metricas de performance/pontuacao por nivel
- Modo multiplayer ou competitivo
- Edicao de niveis pelo usuario (level editor)
- Simulacao de fisica realista de rodas diferenciais (o arco eh uma aproximacao geometrica)
- Trail/rastro visual do caminho percorrido

## Cenarios de Aceite

### CA01 - Comando A basico: arco para direita
**Dado** o robo posicionado no inicio de uma arena vazia, orientado para frente
**Quando** a sequencia `A30R90;` eh executada
**Entao** o robo percorre um arco de 90 graus para a direita com raio 30, terminando orientado 90 graus a direita da direcao original

### CA02 - Comando A basico: arco para esquerda
**Dado** o robo posicionado no inicio de uma arena vazia, orientado para frente
**Quando** a sequencia `A50L180;` eh executada
**Entao** o robo percorre um arco de 180 graus para a esquerda com raio 50, terminando orientado na direcao oposta a original

### CA03 - Sequencia mista com arco
**Dado** o robo no ponto de partida
**Quando** a sequencia `D50F;A30R90;D50F;` eh executada
**Entao** o robo anda 50 unidades para frente, faz arco de 90 graus para direita (raio 30), e anda mais 50 unidades para frente (agora na nova direcao)

### CA04 - Retrocompatibilidade de comandos existentes
**Dado** o robo no ponto de partida
**Quando** a sequencia `D100F;R90R;D50F;D30L;` eh executada
**Entao** o comportamento eh identico ao sistema atual (sem nenhuma mudanca)

### CA05 - Colisao com parede da arena
**Dado** o robo proximo a parede da arena, orientado em direcao a parede
**Quando** o comando `D200F;` eh executado (distancia maior que a disponivel ate a parede)
**Entao** o robo para no ponto de contato com a parede e nao a atravessa

### CA06 - Colisao durante arco
**Dado** o robo proximo a um obstaculo, executando um arco que passaria por dentro do obstaculo
**Quando** o comando `A30R90;` eh executado e o arco colide com o obstaculo
**Entao** o robo para no ponto exato de colisao e o proximo comando da sequencia eh executado

### CA07 - Sequencia continua apos colisao
**Dado** o robo orientado em direcao a uma parede a 10 unidades de distancia
**Quando** a sequencia `D200F;R90R;D50F;` eh executada
**Entao** o robo para na parede (colisao do primeiro comando), gira 90 graus para direita, e anda 50 unidades para frente

### CA08 - Nivel 1-2 resolvivel sem comando A
**Dado** o nivel 1 ou 2 carregado
**Quando** o jogador cria uma sequencia usando apenas comandos D e R
**Entao** eh possivel chegar ao ponto de destino desviando dos obstaculos apenas com movimentos retos e giros

### CA09 - Nivel 3-4 exige comando A
**Dado** o nivel 3 ou 4 carregado
**Quando** o jogador tenta resolver usando apenas D e R (sem arcos)
**Entao** nao eh possivel completar o percurso sem uso de pelo menos um comando A (obstaulos impedem caminhos puramente retilineos)

### CA10 - Nivel 5 exige rampas
**Dado** o nivel 5 carregado
**Quando** o jogador navega o percurso
**Entao** o robo precisa subir pelo menos uma rampa para alcancar o destino (caminho sem rampa esta bloqueado)

### CA11 - Arena com formato variavel
**Dado** niveis com diferentes formatos de arena configurados (quadrada, retangular, circular)
**Quando** cada nivel eh carregado
**Entao** as paredes da arena correspondem ao formato definido e todas possuem colisao funcional

### CA12 - Validacao sintatica do novo comando
**Dado** o sistema de validacao LBML
**Quando** a string `A30R90;` eh validada
**Entao** eh reconhecida como LBML valida

### CA13 - Validacao rejeita sintaxe invalida
**Dado** o sistema de validacao LBML
**Quando** strings invalidas sao validadas (`A30;`, `ARL90;`, `A30R;`, `A-5R90;`)
**Entao** todas sao rejeitadas como LBML invalida

### CA14 - Prompt LLM gera comando A
**Dado** o prompt de conversao atualizado no backend
**Quando** o usuario diz "faca uma curva suave para a direita"
**Entao** o LLM gera um comando A com direcao R (ex: `A30R90;`)

### CA15 - Prompt LLM mantem compatibilidade
**Dado** o prompt de conversao atualizado no backend
**Quando** o usuario diz "ande para frente" ou "gire para a esquerda"
**Entao** o LLM gera comandos D ou R (nao usa A para movimentos simples)

### CA16 - Robo sobe rampa naturalmente
**Dado** o robo posicionado na base de uma rampa, orientado em direcao a ela
**Quando** o comando `D100F;` eh executado
**Entao** o robo sobe a rampa seguindo a inclinacao do terreno (sem comando especial)

### CA17 - Rampa como ponte
**Dado** uma rampa posicionada sobre obstaculos no nivel 5
**Quando** o robo sobe a rampa e percorre seu topo
**Entao** o robo passa por cima dos obstaculos abaixo sem colidir com eles
