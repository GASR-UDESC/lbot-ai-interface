# Especificacao de Negocio: Reestruturacao do Harness - Movimento vs Tarefa

## Contexto

O harness atual do LBot trata todos os comandos do usuario de forma uniforme: um unico tool `move` que traduz linguagem natural para LBML via modelo Seq2Seq, sem distincao entre tipos de acao. Com base nas Diretrizes do Harness, e necessario reestruturar o sistema para classificar e tratar diferentemente dois tipos de acao: **Movimento** e **Tarefa**, cada um com regras especificas de execucao, seguraca e raciocinio.

## Requisitos Funcionais

### RF01 - Classificacao de Acoes

O sistema deve classificar comandos do usuario em duas categorias: **Movimento** e **Tarefa**. A classificacao e feita pelo modelo LLM com base no system prompt, sem etapa de classificacao explicita.

**Regras:**
- O LLM decide o tipo de acao analisando o comando do usuario
- Movimento: acoes que independem do resto do universo (nao necessitam de camera ou sensores)
- Tarefa: acoes que exigem raciocinio inteligente, uso de camera, sensores e multiplos passos

**Cenarios de erro:**
- Comando ambiguo (ex: "anda pra las"): o LLM deve classificar como Movimento ambigu e expandir, nao como Tarefa

### RF02 - Movimento Bem Definido

Movimentos bem definidos sao aqueles em que o usuario especifica distances e direcoes claras (ex: "ande 150cm pra frente, depois ande 100cm para direita"). Esses comandos devem ir direto para o tradutor Seq2Seq e ser executados sem validacao por camera ou sensores.

**Regras:**
- O tool `move` envia o comando NL para o tradutor, que converte para LBML
- O LBML resultante e executado diretamente no backend
- Nenhuma verificacao com camera ou sensores e necessaria
- O comando e tratado de forma deterministica

**Cenarios de erro:**
- Comando com distancia maior que o limite da arena (400cm): reportar ao usuario que o comando excede os limites
- Traducao invalida (LBML nao passa na validacao regex): reportar erro ao usuario e nao executar

### RF03 - Movimento Ambiguo

Movimentos ambiguous sao aqueles em que o usuario pede uma acao sem distances especificas (ex: "da uma volta", "faz um quadrado", "anda em zig zag"). O LLM deve expandir o comando em uma sequencia LBML completa e executar tudo de uma vez.

**Regras:**
- O LLM interpreta o comando ambiguo e gera uma sequencia LBML correspondente
- A sequencia e executada em um unico comando `move`, sem steps intermedios
- A abordagem e hibrida: movimentos bem definidos vao para o tradutor; movimentos ambíguos sao expandidos pelo LLM em LBML e enviados via `move`
- O LLM nao deve consultar camera ou sensores para resolver movimentos ambiguos

**Exemplos:**
- "Faca um quadrado" → `D50F;R90L;D50F;R90L;D50F;R90L;D50F;R90L;`
- "Da uma volta" → `D100F;R90L;D100F;R90L;D100F;R90L;D100F;R90L;`
- "Anda em zig zag" → `D30F;R45L;D30F;R90R;D30F;R45L;D30F;` (exemplo ilustrativo)

**Cenarios de erro:**
- LLM nao consegue interpretar o movimento: pedir esclarecimento ao usuario
- LBML gerado invalido: reportar erro ao usuario

### RF04 - Tarefa (Acao Inteligente)

Tarefas sao acoes que envolvem raciocinio pelo modelo de IA, tipicamente buscar objetos, se aproximar de algo, ou navegar condicionalmente. Para executar Tarefas, o modelo usa as tools disponíveis (camera, proximity, move) em multiplos passos de raciocinio.

**Regras:**
- O modelo deve usar a tool `observe` (ver RF05) para obter imagem e proximidade simultaneamente durante Tarefas
- Nao usar `camera` ou `proximity` individualmente durante Tarefas; usar `observe`
- `camera` e `proximity` continuam disponíveis para consultas simples do usuario (ex: "o que voce ve?")
- O modelo deve sempre centralizar o objeto na camera antes de confiar no sensor de proximidade
- O sensor de proximidade reflete o que esta centralizado exatamente na frente do robô
- Se o objeto nao estiver centralizado, a leitura do sensor nao e confiavel para aquele objeto

**Abordagem tipica de busca:**
1. Girar 90 graus em uma direcao
2. Usar `observe` para verificar se o objeto esta visível e a distancia
3. Se encontrou, centralizar o objeto na camera
4. Apos centralizar, usar `proximity` para confirmar distancia
5. Aproximar mantendo distancia de seguranca (ver RF06)
6. Se nao encontrou apos 360 graus, informar ao usuario

**Cenarios de erro:**
- Objeto nao existe na arena: informar ao usuario que o objeto nao foi encontrado apos busca completa
- Perdeu o objeto de vista: executar protocolo de RF07

### RF05 - Nova Tool `observe`

Criar uma nova tool `observe` que retorna simultaneamente a imagem da camera e os dados de proximidade. Destinada ao uso durante Tarefas (busca, aproximação, navegação condicional).

**Regras:**
- `observe` retorna: imagem base64 PNG + dados de proximidade (frente e tras) em formato estruturado
- O LLM deve ser instruido a usar `observe` em Tarefas ao inves de chamar `camera` e `proximity` separadamente
- `camera` e `proximity` continuam disponíveis como tools independentes para consultas simples do usuario
- `observe` e equivalente a chamar `camera` + `proximity` juntos, mas em uma unica invocacao, economizando steps

**Formato de resposta:**
```
Imagem: [base64 PNG]
Proximidade:
  - Frente: X cm
  -Tras: Y cm
```

### RF06 - Distancia de Seguranca em Tarefas

Durante a execucao de Tarefas, o robô deve sempre manter uma distancia de seguranca de 20cm tanto a frente quanto atras para evitar impactos.

**Regras:**
- A distancia de seguranca de 20cm aplica-se SOMENTE em acoes do tipo Tarefa
- Movimentos livres (bem definidos ou ambiguos) NAO tem restricao de distancia de seguranca
- Ao se aproximar de um objeto durante uma Tarefa, o robô deve parar a 20cm
- Ao recuar durante uma Tarefa, o robô deve manter pelo menos 20cm de distancia de obstaculos atras

**Cenarios de erro:**
- Sensor indica distancia menor que 20cm: interromper movimento e reportar
- Proximidade frontal menor que 20cm: nao avançar mais, informar ao usuario que chegou perto o suficiente

### RF07 - Protocolo de Objeto Perdido

Se durante uma Tarefa o robô perde um objeto de vista (que antes estava visível), deve executar o seguinte protocolo:

**Regras:**
1. Recuar 20cm para tras
2. Iniciar busca girando de 90° em 90° na mesma direcao original
3. Usar `observe` a cada 90° para verificar se o objeto voltou a ser visível
4. Se encontrou, centralizar e retomar a aproximacao
5. Se completou 360° sem encontrar, informar ao usuario que o objeto foi perdido

**Cenarios de erro:**
- Robo nao consegue recuar (obstaculo atras): informar ao usuario e tentar girar no lugar
- Objeto nao encontrado apos 360°: informar ao usuario

### RF08 - Centralizacao de Objeto

Antes de confiar no sensor de proximidade para medir a distancia ate um objeto, o modelo deve primeiro centralizar o objeto na imagem da camera.

**Regras:**
- O sensor de proximidade reflete exatamente o que esta centralizado na frente do robô
- Se o objeto nao estiver centralizado, o sensor pode estar lendo a distancia ate a parede ou outro obstaculo, nao o objeto
- O modelo deve sempre verificar o alinhamento visual antes de confiar na distancia do sensor
- O prompt deve instruir o modelo sobre esta limitacao do sensor

**Cenarios de erro:**
- Objeto parcialmente visível na borda da imagem: girar para centralizar antes de medir
- Objeto nao visível na imagem: executar protocolo de objeto perdido (RF07)

### RF09 - Limite de Steps do ReActAgent

O limite maximo de iteracoes do ReActAgent deve ser aumentado de 20 para 100 steps para acomodar Tarefas complexas que exigem multiplos passos de observacao e raciocinio.

**Regras:**
- Limite global de 100 steps
- Movimentos tipicamente consomem 1-2 steps
- Tarefas podem consumir muitos steps (girar 4x de 90 graus, checar, centralizar, aproximar, etc.)

### RF10 - Tratamento de Acoes Impossíveis

Quando o modelo identificar que uma acao e impossível, deve reportar ao usuario em vez de tentar executar.

**Regras:**
- Distancia solicitada excede os limites da arena (400cm): informar ao usuario
- Objeto nao existe na arena: informar ao usuario apos busca completa
- Acao fisicamente impossível: informar ao usuario e sugerir alternativas

## Requisitos Nao-Funcionais

- **Latencia**: Movimentos devem ser executados rapidamente (sem steps extras de raciocinio)
- **Idioma**: Toda interacao com o usuario permanece em portugues
- **ComCompatibilidade**: As tools `camera` e `proximity` existentes devem continuar funcionando para consultas simples
- **Extensibilidade**: A estrutura deve permitir adicionar novos tipos de Tarefa no futuro

## Glossario / Definicoes

- **Movimento**: Acao que independe do resto do universo. O robô executa sem consultar camera ou sensores.
- **Movimento Bem Definido**: Movimento com distances e direcoes especificas (ex: "ande 150cm pra frente"). Vai direto para o tradutor.
- **Movimento Ambiguo**: Movimento sem distances especificas (ex: "da uma volta", "faz um quadrado"). O LLM expande em LBML.
- **Tarefa**: Acao que envolve raciocinio inteligente, uso de camera/sensores e multiplos passos (busca, aproximacao, navegacao condicional).
- **LBML**: LBot Movement Language. Formato de comandos de movimento (ex: `D30F;R90L;`). Prefixo D = deslocamento (cm), R = rotacao (graus).
- **observe**: Nova tool que retorna simultaneamente imagem da camera e dados de proximidade.
- **Distancia de Seguranca**: 20cm de distancia minima a manter de obstaculos durante Tarefas.

## Premissas

- O tradutor Seq2Seq existente (LBotTranslatorV7) sera mantido para movimentos bem definidos
- O LLM e capaz de gerar sequencias LBML validas para movimentos ambiguos
- O system prompt sera reescrito para guiar o modelo na classificacao e execucao correta das acoes
- As tools `camera` e `proximity` individuais permanecem disponíveis para consultas diretas do usuario
- A arena e de 4m x 4m (400cm x 400cm) com paredes em +/-204cm
- O robô e um E-Puck com camera frontal e sensores de proximidade frontal e traseiro
- O limite de steps do ReActAgent sera alterado de 20 para 100

## Fora de escopo

- Criacao de novas tools compostas de alto nivel (search_object, approach_object, etc.)
- Mudancas no simulador web (frontend ou backend Node.js)
- Mudancas no modelo tradutor Seq2Seq (re-treinamento ou ajustes)
- Classificador explicito de tipos de acao (ML ou regex)
- Validacao automatica de limites da arena no backend (o modelo deve inferir e reportar)
- Suporte a multi-robô ou coordenação

## Cenarios de Aceite

### CA01 - Movimento bem definido direto ao tradutor
**Dado** que o usuario digita "ande 30cm para frente"
**Quando** o LLM classifica como Movimento bem definido
**Entao** o comando e enviado ao tradutor, que gera `D30F;`, e executado diretamente sem consulta a camera ou sensores

### CA02 - Movimento ambigu expandido pelo LLM
**Dado** que o usuario digita "faca um quadrado"
**Quando** o LLM classifica como Movimento ambigu
**Entao** o LLM expande em uma sequencia LBML (ex: `D50F;R90L;D50F;R90L;D50F;R90L;D50F;R90L;`) e envia via tool `move` para execucao em um unico comando

### CA03 - Tarefa de busca de objeto
**Dado** que o usuario digita "encontre o cubo vermelho"
**Quando** o LLM classifica como Tarefa
**Entao** o LLM inicia um loop usando `observe` (camera + proximidade) e `move`, girando de 90° em 90°, ate encontrar o objeto ou completar 360°

### CA04 - Centralizacao antes de proximidade
**Dado** que o robô esta executando uma Tarefa e avistou um objeto
**Quando** o objeto nao esta centralizado na imagem da camera
**Entao** o LLM deve girar o robô para centralizar o objeto antes de confiar na leitura do sensor de proximidade

### CA05 - Distancia de seguranca em Tarefa
**Dado** que o robô esta se aproximando de um objeto durante uma Tarefa
**Quando** o sensor de proximidade frontal indica distancia menor ou igual a 20cm
**Entao** o robô deve parar e nao avançar mais, informando ao usuario que esta proximo o suficiente

### CA06 - Distancia de seguranca nao aplica em Movimento
**Dado** que o usuario pede "ande 50cm para frente" (Movimento)
**Quando** o comando e executado
**Entao** o robô anda exatamente 50cm, sem restricao de distancia de seguranca

### CA07 - Protocolo de objeto perdido
**Dado** que o robô perdeu um objeto de vista durante uma Tarefa
**Quando** o objeto nao aparece mais na camera
**Entao** o robô recua 20cm e gira 90° em 90° procurando o objeto novamente

### CA08 - Tool observe retorna camera e proximidade
**Dado** que o LLM chama a tool `observe`
**Quando** a tool e executada
**Entao** retorna simultaneamente a imagem da camera (base64 PNG) e os dados de proximidade (frente e tras em cm)

### CA09 - Acao impossivel reportada ao usuario
**Dado** que o usuario pede "ande 500cm para frente"
**Quando** o LLM identifica que a distancia excede o limite da arena
**Entao** o LLM informa ao usuario que o comando e impossivel e sugere uma alternativa

### CA10 - Objeto inexistente na arena
**Dado** que o usuario pede "encontre o objeto dourado" e nao existe tal objeto na arena
**Quando** o robô completa uma busca de 360° sem encontrar o objeto
**Entao** o LLM informa ao usuario que o objeto nao foi encontrado

### CA11 - Limite de steps aumentado
**Dado** que o ReActAgent executa uma Tarefa complexa
**Quando** o agente precisa de mais de 20 steps
**Entao** o agente pode continuar ate o limite de 100 steps

### CA12 - Consulta simples com camera e proximity
**Dado** que o usuario pergunta "o que voce ve?"
**Quando** o LLM classifica como consulta simples
**Entao** o LLM pode usar `camera` e `proximity` individualmente, sem necessidade da tool `observe`