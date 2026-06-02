# Especificação de Negócio: LBot AI Interface - MCP Server, Harness e Simulador

## Contexto

O LBot é um robô E-Puck controlado remotamente. Atualmente o projeto possui um simulador 3D web (`3.controlador/lbot-simulator-web`), um tradutor de linguagem natural para LBML (`lbot-translator-v7`), e backend de geração de dados. A tarefa é transformar o ecossistema em uma plataforma baseada no protocolo **MCP (Model Context Protocol)** para permitir que o robô seja operado por IA de forma agêntica, com um simulador para testes e desenvolvimento.

## Requisitos Funcionais

### RF01 - Simulador: Câmera em Primeira Pessoa
O simulador 3D web deve ser capaz de gerar uma imagem renderizada da perspectiva frontal do robô (visão em 1ª pessoa), equivalente à câmera que o robô real terá.

**Regras:**
- O render deve ser uma visualização 3D simplificada (cores sólidas) da frente do robô
- O retorno é uma imagem codificada em base64
- A câmera está posicionada na parte frontal do robô, orientada na direção que ele está enfrentando

**Cenários de erro:**
- Falha no render: retornar mensagem de erro descritiva

### RF02 - Simulador: Sensores de Proximidade
O simulador deve prover medição de distância via sensores de proximidade frontal e traseiro.

**Regras:**
- Dois sensores: um na frente e um atrás do robô
- Distância medida em centímetros (cm) até a parede ou sólido mais próximo
- Utiliza raycasting a partir do robô na direção do sensor
- O robô não é impedido de colidir — o sensor apenas reporta a distância

**Cenários de erro:**
- Nenhum obstáculo no alcance do sensor: retornar valor máximo ou "sem obstáculo"

### RF03 - Simulador: Execução de Comandos LBML
O simulador deve continuar suportando a execução de sequências de comandos LBML com física (cannon-es), já existente no `3.controlador/lbot-simulator-web`.

**Regras:**
- Mantém o comportamento atual de parsing e execução de LBML (`D<valor><F|B|L|R>;R<ângulo><L|R>;`)
- Robô se move livremente pela arena (800x800), podendo colidir com paredes
- Comandos são enviados via API REST e executados com animação e física

### RF04 - Simulador: API REST + SSE
A API do simulador deve ser estendida para expor os novos recursos (câmera, sensores) mantendo o protocolo REST + SSE existente.

**Regras:**
- Manter endpoints existentes: `/api/health`, `/api/status`, `/api/state`, `/api/events` (SSE), `/api/commands`, `/api/reset`
- Novos endpoints para câmera (GET, retorna base64) e sensores (GET, retorna distâncias)
- Estender o snapshot de estado para incluir leituras dos sensores

### RF05 - MCP Server: Ferramenta Câmera
O MCP Server deve expor uma tool MCP que captura a imagem da câmera do robô.

**Regras:**
- A tool retorna a imagem como string base64
- No backend simulador: obtém a imagem via API HTTP do simulador
- No backend real: obtém a imagem do hardware (câmera conectada ao Raspberry Pi/ESP32)
- O MCP Server não processa a imagem — apenas a serve

**Cenários de erro:**
- Backend indisponível: retornar erro "câmera indisponível"
- Timeout na captura: retornar erro após timeout configurável

### RF06 - MCP Server: Ferramenta Sensor de Proximidade
O MCP Server deve expor uma tool MCP que retorna as leituras dos sensores de proximidade.

**Regras:**
- A tool retorna um objeto com duas distâncias em cm: `{ frente: <float>, tras: <float> }`
- No backend simulador: obtém via API HTTP do simulador
- No backend real: obtém do hardware

**Cenários de erro:**
- Sensor indisponível: retornar erro "sensor indisponível"

### RF07 - MCP Server: Ferramenta Deslocamento
O MCP Server deve expor uma tool MCP que recebe comandos de movimento em linguagem natural, traduz para LBML usando o `lbot-translator-v7`, e executa o movimento no robô.

**Regras:**
- Entrada: texto em linguagem natural (ex: "anda 30cm para frente e vira 90 graus para direita")
- O translator é carregado como módulo Python interno ao MCP Server
- A tool traduz NL → LBML, envia ao backend, e retorna o resultado da execução (LBML gerada + status)
- O MCP Server não tem inteligência própria — apenas orquestra tradução e execução

**Cenários de erro:**
- Texto de entrada incompreensível: tradutor retorna LBML inválida → erro "não entendi o comando"
- Falha na execução do movimento: retornar erro reportado pelo backend

### RF08 - MCP Server: Backends Plugáveis
O MCP Server deve suportar troca de backend (simulador vs real) sem alterar a interface MCP exposta.

**Regras:**
- Configuração de backend via variável de ambiente ou arquivo de configuração
- Backend simulador: comunica-se via HTTP com o `3.controlador/lbot-simulator-web`
- Backend real: comunica-se com o ESP32 (implementação futura)
- A interface das tools MCP é idêntica independente do backend ativo

### RF09 - MCP Client (Harness): Interface CLI
O harness deve prover uma interface de linha de comando interativa para o usuário conversar com o robô.

**Regras:**
- CLI interativo (REPL) que aceita comandos em texto
- Conecta-se ao MCP Server como MCP Client
- Saída puramente textual (sem imagens ou áudio)
- O usuário pode dar comandos de alto nível (ex: "explore a sala", "vá até a parede e tire uma foto")

### RF10 - MCP Client (Harness): Loop Agêntico
O harness deve operar o robô com IA usando loop agêntico baseado no padrão ReAct (Reason + Act).

**Regras:**
- A cada passo: o LLM raciocina sobre o estado atual, decide qual ferramenta MCP usar, executa, e avalia o resultado
- O loop continua até que o objetivo seja cumprido ou o LLM decida que não é possível continuar
- O LLM tem acesso às 3 ferramentas MCP (câmera, proximidade, deslocamento)
- O LLM decide autonomamente quantos passos e quais ferramentas usar para cumprir o objetivo
- O usuário pode interromper o loop a qualquer momento (Ctrl+C)

**Cenários de erro:**
- Ferramenta retorna erro: o LLM é informado do erro e decide se tenta alternativa ou reporta ao usuário

### RF11 - MCP Client (Harness): Personalidade do Robô
O harness deve configurar o LLM com um system prompt que dá personalidade ao robô.

**Regras:**
- Personalidade: robô curioso e humilde, consciente de suas limitações físicas
- O robô se entende como um robô E-Puck com sensores e câmera
- Responde sempre em português
- É prestativo mas não finge ter capacidades que não tem
- O system prompt descreve as ferramentas disponíveis e como usá-las

### RF12 - MCP Client (Harness): Tratamento de Erros
Quando uma ferramenta MCP falha, o harness deve reportar o erro de forma clara.

**Regras:**
- Erros das ferramentas são repassados ao LLM no contexto da conversa
- O LLM decide como comunicar o erro ao usuário (de forma natural, mantendo a personalidade)
- Não há retry automático — o LLM pode decidir tentar outra abordagem se fizer sentido
- Se o MCP Server estiver indisponível: informar "não consigo me comunicar com meu corpo no momento"

## Requisitos Não-Funcionais

- **RNF01**: O MCP Server e o Harness devem ser implementados em Python, gerenciados com `uv` ou Poetry (`pyproject.toml`)
- **RNF02**: O MCP Server usa FastMCP como framework MCP
- **RNF03**: O Harness usa OpenAI SDK (modo compatível) para comunicar com LM Studio
- **RNF04**: O LLM utilizado é carregado via LM Studio (localhost), com configuração padrão de API compatível OpenAI
- **RNF05**: O simulador estende o `3.controlador/lbot-simulator-web` existente (TypeScript, React, Three.js, Express)
- **RNF06**: A comunicação entre MCP Server e simulador é via HTTP (REST + SSE)
- **RNF07**: O tradutor `lbot-translator-v7` é importado como módulo Python pelo MCP Server

## Glossário / Definições

- **MCP (Model Context Protocol)**: Protocolo aberto que padroniza como aplicações fornecem contexto e ferramentas para LLMs
- **MCP Server**: Servidor que expõe ferramentas e recursos via protocolo MCP
- **MCP Client**: Cliente (harness) que consome ferramentas MCP e as disponibiliza para um LLM
- **FastMCP**: Framework Python para construir MCP Servers de forma simplificada
- **LBML (LBot Movement Language)**: Linguagem de comandos de movimento do robô, formato `D<valor><direção>;R<ângulo><direção>;`
- **Harness**: O MCP Client com personalidade que opera o robô via IA (loop agêntico)
- **Loop Agêntico / ReAct**: Padrão onde o agente raciocina (Reason), age (Act), observa o resultado, e repete
- **lbot-translator-v7**: Modelo Seq2Seq (BiGRU + Bahdanau Attention) que traduz português → LBML
- **E-Puck**: Modelo de robô educacional simulado/controlado pelo projeto

## Premissas

- O `3.controlador/lbot-simulator-web` existente é funcional e será a base do simulador estendido
- O `lbot-translator-v7` está treinado e pronto para uso como módulo Python
- O LM Studio está instalado e rodando localmente com um modelo compatível com function calling carregado
- O protocolo MCP é adequado para a comunicação entre harness e server
- A comunicação com o ESP32 (backend real) será tratada futuramente, fora do escopo imediato
- O ambiente Python será isolado com venv gerenciado por uv ou Poetry
- O simulador roda em Node.js (existente) e o MCP Server em Python — a comunicação entre eles é via HTTP

## Fora de escopo

- Firmware/software do ESP32 para controle de motores e sensores reais
- Comunicação entre MCP Server e hardware real (ESP32)
- Interface gráfica para o harness (é apenas CLI)
- Suporte a múltiplos robôs simultaneamente
- Treinamento ou fine-tuning do modelo de tradução
- Output de áudio/voz no harness
- Deploy em produção ou containerização
- Detecção e prevenção automática de colisões (movimento livre na arena)

## Cenários de Aceite

### CA01 - Câmera simulada retorna imagem
**Dado** que o simulador está rodando com o robô em uma posição conhecida na arena
**Quando** a ferramenta de câmera é acionada via MCP
**Então** o sistema retorna uma imagem em base64 representando a visão frontal do robô

### CA02 - Sensores de proximidade retornam distâncias
**Dado** que o robô está a 50cm de uma parede à frente e 200cm de uma parede atrás
**Quando** a ferramenta de sensor é acionada via MCP
**Então** o sistema retorna `{ frente: 50, tras: 200 }`

### CA03 - Comando de deslocamento em linguagem natural
**Dado** que o usuário envia "anda 30 centímetros para frente"
**Quando** a ferramenta de deslocamento processa o comando
**Então** o sistema traduz para LBML, executa o movimento, e retorna confirmação com a LBML gerada

### CA04 - Harness explora a arena autonomamente
**Dado** que o harness está conectado ao MCP Server (modo simulador)
**Quando** o usuário digita "explore a sala e me diga o que você vê"
**Então** o robô usa o loop ReAct para: verificar sensores, mover-se, tirar foto, e descrever o ambiente ao usuário, tudo de forma autônoma

### CA05 - Erro de ferramenta reportado ao usuário
**Dado** que o simulador está indisponível
**Quando** o harness tenta usar qualquer ferramenta MCP
**Então** o LLM informa o usuário de forma amigável que não consegue se comunicar com seu "corpo"

### CA06 - Troca de backend transparente
**Dado** que o MCP Server está configurado com backend simulador
**Quando** o harness consulta as ferramentas disponíveis e as utiliza
**Então** o comportamento é idêntico ao que seria com o backend real (mesma interface MCP)
