# Especificacao de Negocio: Melhoria de Aproximacao do Robo a Objetos

## Contexto

O robo E-Puck controlado por IA (via MCP + LLM) apresenta um problema critico ao se aproximar de objetos-alvo. Analisando os logs de execucao, o robo:

1. **Se aproxima demais** — chega a 13cm do objeto quando a regra diz 20cm, depois tenta avancar mais 5cm e "perde" o objeto de vista (a distancia salta de 13cm para 50cm+)
2. **Entra em loop infinito de rotacoes** — ao perder o objeto, fica girando R5L repetidamente sem progresso, consumindo dezenas de passos sem resultado
3. **Nao sabe quando parar** — nao ha mecanismo automatico que declare sucesso quando o robo chega perto o suficiente do objeto
4. **Nao respeita a distancia de seguranca** — a regra de 20cm existe apenas no prompt, sem enforcement no codigo, e o LLM frequentemente a ignora

A tarefa e corrigir esses problemas melhorando o prompt do robo E adicionando validacoes automaticas no agent loop (camada de controle), sem modificar o simulador web.

## Requisitos Funcionais

### RF01 - Parada automatica por proximidade alvo

O robo deve parar automaticamente e declarar sucesso quando a proximidade frontal estiver na faixa de 15cm a 25cm de um objeto a frente, apos ter o objeto centralizado na camera.

**Regras:**
- A verificacao acontece no agent loop (codigo Python), nao apenas no prompt
- Quando `frente <= 25cm` E `frente >= 15cm` apos o objeto estar centralizado na camera, o robo declara que alcancou o objetivo
- O agente insere uma mensagem no contexto informando que o objetivo foi alcancado, forçando o LLM a parar de se mover
- O robo informa ao usuario que chegou ao objeto com sucesso

**Cenarios de erro:**
- Proximidade frontal < 15cm sem objeto centralizado: o robo recuou automaticamente (ver RF05)
- Proximidade frontal entre 15-25cm mas objeto nao centralizado na camera: o robo tenta centralizar primeiro antes de declarar sucesso

### RF02 - Bloqueio de avanco por proximidade minima

O robo nunca deve executar um comando de avanco (DXXF) se a leitura de proximidade frontal ja estiver a <= 20cm de um obstaculo. O bloqueio ocorre no agent Python antes de enviar o comando ao simulador.

**Regras:**
- Antes de executar qualquer comando `D<dist>F;`, o agente verifica a ultima leitura de proximidade frontal
- Se `frente <= 20cm`, o comando de avanco e bloqueado e substituido por uma mensagem informando que o robo ja esta proximo o suficiente
- Comandos de recuo (`D<dist>B;`) e rotacao (`R<ang>L/R;`) nao sao bloqueados
- O bloqueio retorna uma mensagem clara ao LLM: "Bloqueado: distancia frontal e de Xcm, ja esta dentro da faixa de aproximacao (15-25cm). Objetivo alcancado."

**Cenarios de erro:**
- Proximidade frontal exatamente 20cm: bloqueado (<= 20cm)
- Proximidade frontal 21cm: permitido, mas com passo reduzido (ver RF06)

### RF03 - Prompt melhorado para aproximacao

O system prompt do robo (personality.py) deve ser atualizado com instrucoes mais fortes e especificas sobre:

**Regras:**
- Enfatizar que o sensor de proximidade mede o objeto mais proximo naquela direcao, nao necessariamente o alvo — sempre centralizar o alvo na camera ANTES de confiar na leitura
- Adicionar instrucao explicita de que quando estiver a <= 40cm do objeto, os passos devem ser de no maximo 10cm (nao 20cm)
- Adicionar instrucao explicita de que quando estiver a <= 25cm do objeto, NAO avancar mais — ja esta na distancia correta, declarar sucesso
- Adicionar instrucao para NUNCA usar R5L/R5R repetidamente quando o objeto estiver visivel — se nao centralizar apos 2-3 rotacoes de 5 graus, tentar estrategia diferente (voltar 10 graus, ou recuar)
- Atualizar o protocolo de "aproximacao gradual" para usar passos de 20cm quando > 80cm, 15cm quando 40-80cm, e 10cm quando < 40cm

**Cenarios de erro:**
- LLM ignora as instrucoes: mitigado por RF02 (bloqueio automatico de avanco)
- LLM fica em loop de rotacoes: mitigado por RF04 (deteccao de loop)

### RF04 - Deteccao de loop e limite de passos

O agent deve detectar quando o robo esta em loop (sem progresso) e cancelar a tarefa apos 50 passos de observe+move sem conclusao.

**Regras:**
- Limite maximo de 50 passos (chamadas de observe + move) por tarefa
- A cada passo, o agente rastreia o numero de passos executados
- Ao atingir 50 passos, o agente interrompe o loop e informa ao usuario: "Nao consegui completar a tarefa apos 50 passos. Tente reformular o pedido ou verificar se o ambiente esta funcionando."
- Alem do limite fixo, detectar loops mais curtos: se a posicao do robo (x, z, rotacao) nao mudar signficativamente apos 10 passos consecutivos de rotacao, inserir mensagem no contexto alertando o LLM que esta em loop

**Cenarios de erro:**
- Robo em loop de rotacao (posicao nao muda): alerta apos 10 passos de rotacao sem mudanca de posicao
- Robo atingiu 50 passos: cancelamento automatico

### RF05 - Protocolo de recuperacao de perda de objeto

Quando o robo perde o objeto de vista durante a aproximacao (a distancia frontal salta de < 25cm para > 30cm, ou o objeto desaparece da imagem), o agente inicia um protocolo automatico de recuperacao.

**Regras:**
- Executar automaticamente um recuo de 20cm (`D20B;`) via move
- Apos o recuo, usar observe() para re-localizar o objeto
- Se encontrar o objeto, centralizar e retomar a aproximacao com passos menores (max 10cm)
- Se nao encontrar apos 360 graus de busca, informar que o objeto foi perdido
- Este protocolo e executado no agent Python de forma transparente para o LLM: o agente detecta a perda e injeta uma mensagem no contexto instruindo o LLM a recuar

**Cenarios de erro:**
- Recuo falha (simulador desconectado): informar erro ao usuario
- Objeto nao reencontrado apos busca completa: informar que o objeto foi perdido

### RF06 - Reducao automatica de passo por proximidade

O agente modifica automaticamente comandos de avanco quando o robo esta perto do alvo, para evitar overshooting.

**Regras:**
- Se a ultima leitura de proximidade frontal estiver entre 20cm e 40cm, qualquer comando `D<dist>F;` com `dist > 10` e automaticamente reduzido para `D10F;`
- Se a ultima leitura estiver entre 40cm e 80cm, qualquer comando `D<dist>F;` com `dist > 15` e automaticamente reduzido para `D15F;`
- Acima de 80cm, nao ha modificacao (passos de ate 20cm sao aceitos)
- A modificacao e feita no agent Python antes de enviar ao simulador
- O agente informa ao LLM que o passo foi reduzido: "Comando ajustado: D20F reduzido para D10F (proximo ao alvo, passo reduzido por seguranca)"

**Cenarios de erro:**
- Sem leitura de proximidade disponivel: nao modificar o comando (manter original)
- Comando e de recuo ou rotacao: nao modificar

## Requisitos Nao-Funcionais

- **Performance**: As modificacoes no agent loop (verificacao de proximidade, ajuste de comandos) nao devem adicionar latencia perceptivel (< 100ms por passo)
- **Compatibilidade**: Nenhuma mudanca no simulador web — apenas no lbot-mcp
- **Transparencia**: O LLM deve ser informado quando seus comandos sao modificados (mensagens claras no contexto)
- **Robustez**: Se o sensor de proximidade estiver indisponivel, o sistema deve funcionar no modo fallback (apenas prompt, sem bloqueios automaticos)

## Glossario / Definicoes

- **Proximidade frontal**: Distancia em cm ate o obstaculo mais proximo na direcao frontal do robo, medida pelo sensor de proximidade
- **Proximidade traseira**: Distancia em cm ate o obstaculo mais proximo na direcao traseira do robo
- **Objeto centralizado**: Objeto alvo aparece no centro da imagem da camera (o LLM confirma visualmente)
- **Overshooting**: O robo avanca alem do ponto desejado e perde o objeto de vista, geralmente porque passos sao grandes demais perto do alvo
- **Loop de rotacao**: O robo gira repetidamente (R5L/R5R) sem mudanca significativa de posica, tentando centralizar um objeto que nao esta mais visivel
- **Agent loop**: O loop ReAct no agent.py que coordena chamadas LLM → tool_calls → resultados
- **LBML**: Linguagem de comandos do robo (ex: D20F;R90L;)

## Premissas

- O simulador web (lbot-simulator-web) nao sera modificado nesta tarefa
- O sensor de proximidade retorna distancia ao objeto mais proximo na direcao, sem distinguir qual objeto
- O LLM as vezes ignora instrucoes do prompt — por isso as validacoes no codigo sao essenciais
- O sistema pode depender de uma ultima leitura de proximidade para tomar decisoes, que pode estar desatualizada se o robo se moveu desde a ultima leitura
- A deteccao de "objeto centralizado" depende da interpretacao visual do LLM — nao ha validacao automatica disso

## Fora de escopo

- Modificacoes no simulador web (lbot-simulator-web)
- Adicionar identificacao de objeto no sensor de proximidade (ex: informar cor/tipo do objeto detectado)
- Adicionar sensores direcionais multi-feixe (simular sensores reais do E-Puck)
- Modificar o tradutor de linguagem natural para LBML
- Adicionar colisao fisica no simulador (obstaculos nao bloqueiam movimento)
- Criar novos tipos de tarefas alem de busca/aproximacao

## Cenarios de Aceite

### CA01 - Robo para ao atingir distancia alvo
**Dado** o robo esta se aproximando de um objeto com o objeto centralizado na camera
**Quando** a leitura de proximidade frontal estiver entre 15cm e 25cm
**Entao** o robo para de se mover e informa ao usuario que alcancou o objeto com sucesso

### CA02 - Bloqueio de avanco por proximidade minima
**Dado** a ultima leitura de proximidade frontal e <= 20cm
**Quando** o LLM envia um comando D<dist>F
**Entao** o comando e bloqueado pelo agent e uma mensagem e retornada ao LLM informando que o robo ja esta perto o suficiente

### CA03 - Reducao de passo perto do alvo
**Dado** a ultima leitura de proximidade frontal e de 35cm
**Quando** o LLM envia um comando D20F
**Entao** o agent modifica o comando para D10F e informa o LLM que o passo foi reduzido

### CA04 - Reducao de passo em zona intermediaria
**Dado** a ultima leitura de proximidade frontal e de 60cm
**Quando** o LLM envia um comando D20F
**Entao** o agent modifica o comando para D15F e informa o LLM que o passo foi reduzido

### CA05 - Aproximacao normal fora de zona de reducao
**Dado** a ultima leitura de proximidade frontal e de 100cm
**Quando** o LLM envia um comando D20F
**Entao** o comando e executado sem modificacao

### CA06 - Recuperacao de perda de objeto
**Dado** o robo esta a < 25cm do objeto e perde o objeto de vista (distancia salta para > 30cm ou objeto desaparece da camera)
**Quando** o agente detecta a perda
**Entao** o agent recua automaticamente 20cm, observa novamente, e reinsere instrucao no contexto do LLM para re-centralizar o objeto

### CA07 - Limite de passos atingido
**Dado** o robo executou 50 passos (observe + move) sem concluir a tarefa
**Quando** o agente atinge o limite
**Entao** o loop e interrompido e o usuario e informado que a tarefa nao pode ser concluida

### CA08 - Deteccao de loop de rotacao
**Dado** o robo executou 10 passos de rotacao consecutivos sem mudanca significativa de posicao (x, z)
**Quando** o agente detecta o loop
**Entao** uma mensagem e inserida no contexto do LLM alertando que esta em loop e sugerindo estrategia diferente

### CA09 - Comandos de recuo e rotacao nao sao bloqueados
**Dado** a ultima leitura de proximidade frontal e <= 20cm
**Quando** o LLM envia um comando de recuo (D<dist>B) ou rotacao (R<ang>L/R)
**Entao** o comando e executado normalmente sem bloqueio

### CA10 - Funcionamento sem sensor de proximidade
**Dado** o sensor de proximidade esta indisponivel
**Quando** o robo tenta executar uma tarefa de busca/aproximacao
**Entao** o sistema funciona em modo fallback (apenas prompt, sem bloqueios ou ajustes automaticos de passo)

### CA11 - Prompt orienta centralizacao antes de confiar no sensor
**Dado** o robo esta realizando uma tarefa de aproximacao
**Quando** o robo verifica a distancia ao objeto
**Entao** o prompt instrucao explicitamente o LLM a centralizar o objeto na camera ANTES de confiar na leitura do sensor de proximidade

### CA12 - Passos reduzidos na zona de aproximacao
**Dado** o robo esta a < 40cm do objeto e com o objeto centralizado
**Quando** o LLM envia um comando de avanco
**Entao** o prompt instrui o LLM a usar passos de no maximo 10cm nesta zona