# Especificação de Negócio: Refatoração Completa do Harness

## Contexto

O harness é o módulo de orquestração do robô E-Puck — um agente ReAct que conecta uma LLM a ferramentas MCP (câmera, sensores, movimento). Atualmente o código está concentrado em arquivos muito grandes (`agent.py` com 909 linhas, `personality.py` com 235 linhas), com validações programáticas que deveriam ser delegadas à LLM, protocolos rígidos de busca, geração de LBML pela própria LLM (ignorando o tradutor Seq2Seq existente), e testes que consomem tokens desnecessariamente.

O objetivo é refatorar completamente o harness aplicando princípios de Clean Code, simplificando sua arquitetura, delegando responsabilidades corretamente, e otimizando o prompt para um modelo de linguagem pequeno (~8B parâmetros).

---

## Requisitos Funcionais

### RF01 — Arquivos com responsabilidade única (~150-200 linhas cada)

O harness atual tem arquivos grandes (`agent.py` 909 linhas, `personality.py` 235 linhas) que misturam múltiplas responsabilidades. Após a refatoração, cada arquivo deve ter uma única responsabilidade bem definida e tamanho máximo de ~150-200 linhas.

**Regras:**
- Cada classe ou função pública deve ter um único motivo para mudar (SRP)
- Agrupar funcionalidades coesas: loop ReAct, prompt, gerenciamento de ferramentas, tradução NL→LBML, parsers LBML, comunicação MCP
- Nenhum arquivo deve ultrapassar ~200 linhas
- Seguir os princípios do Clean Code: nomes significativos, funções pequenas, poucos argumentos, evitar efeitos colaterais

### RF02 — Remoção de todos os testes

Todos os testes existentes (Python e TypeScript) devem ser removidos do repositório, incluindo arquivos de configuração de teste e dependências associadas.

**Regras:**
- Remover toda a pasta `lbot-mcp/tests/` e seu conteúdo
- Remover toda a pasta `lbot-simulator-web/tests/` e seu conteúdo
- Remover configurações de teste do `pyproject.toml` (seção `[tool.pytest.ini_options]`)
- Remover `vitest.config.ts` do `lbot-simulator-web/`
- Remover `.pytest_cache/` e quaisquer outros artefatos de teste
- Remover dependências de teste dos `package.json` e `pyproject.toml`

### RF03 — Remoção de validações programáticas

Todas as validações de segurança atualmente implementadas em código devem ser removidas. A LLM é responsável por decidir o que é seguro, guiada pelo system prompt.

**Validações a remover:**
- `_validate_and_adjust_move()` — bloqueio de movimento frontal se <20cm de obstáculo, ajuste de step size
- `_check_proximity_goal()` — verificação de distância alvo (15-25cm)
- `_check_rotation_loop()` — detecção de loops de rotação excessiva
- `_detect_object_loss()` — detecção de perda de objeto (spike de distância)
- `_is_valid_base64()` — validação de formato base64 de imagens

**Regras:**
- A LLM recebe no system prompt as regras de segurança para auto-regular seu comportamento
- O harness não intervém nas decisões de movimento da LLM
- Se houver colisão real, o backend/simulador retorna erro e o harness repassa à LLM

### RF04 — Remoção da funcionalidade de busca

O protocolo de busca (girar 360°, andar em zigue-zague para encontrar objetos) deve ser removido do system prompt e de qualquer lógica codificada.

**Regras:**
- Remover seções do prompt que descrevem protocolos de busca/navegação
- A LLM decide livremente como explorar o ambiente usando as ferramentas disponíveis (camera + proximity)
- Nenhum comportamento de busca é imposto pelo harness

### RF05 — Tradutor como único gerador de LBML

A LLM NUNCA deve gerar LBML. O tradutor Seq2Seq (`LBotTranslatorV7`) é a única fonte de geração de comandos LBML.

**Regras:**
- A ferramenta `move()` recebe linguagem natural (ex: "ande 30cm para frente, vire 90 graus para direita")
- O harness chama o tradutor automaticamente para converter NL → LBML antes de executar o movimento
- Se o tradutor falhar, a missão é abortada com mensagem de erro
- A LLM nunca vê o formato LBML nem recebe instruções sobre como gerá-lo
- O system prompt deve instruir a LLM a usar `move()` com linguagem natural clara e direta

**Cenários de erro:**
- Tradutor falha na tradução: abortar a missão, informar o usuário que o comando não pôde ser traduzido

### RF06 — System prompt otimizado para modelo pequeno

O system prompt deve ser reescrito para:
- Ser curto e direto (~30-50 linhas)
- Ser em português
- Ser autoexplicativo e adequado a um modelo ~8B parâmetros

**Regras:**
- Sem classificações complexas de ações (remover "Movimento Bem Definido / Ambíguo / Tarefa")
- Sem protocolos rígidos (busca, zonas de segurança)
- Sem formato LBML — o modelo nunca deve ver LBML
- Explicar de forma clara e simples as ferramentas disponíveis: `camera()`, `proximity()`, `move()`
- Incluir regras de segurança essenciais para auto-regulação da LLM
- Máximo de 50 linhas de system prompt

### RF07 — Conjunto simplificado de ferramentas MCP

As ferramentas expostas à LLM devem ser simplificadas.

**Ferramentas mantidas:**
- `camera()` — retorna a imagem da câmera frontal (base64 PNG)
- `proximity()` — retorna leituras dos sensores de proximidade
- `move(comando_nl)` — executa movimento a partir de linguagem natural (tradução interna para LBML)

**Ferramentas removidas:**
- `observe()` — removida; a LLM usa `camera()` e `proximity()` separadamente

**Regras:**
- Imagens continuam sendo enviadas como base64 inline, sem alteração de qualidade
- O modelo multimodal (~8B) deve conseguir interpretar as imagens

### RF08 — Remoção de anti-loop detection e context trimming

Funcionalidades de proteção que limitam a autonomia da LLM devem ser removidas.

**A remover:**
- `_check_rotation_loop()` — detecção de loops de rotação
- `_trim_messages()` — corte de mensagens antigas para caber no contexto
- `_sanitize_messages()` — validação de integridade da conversa
- `_estimate_tokens()` — estimativa de tokens para trimming
- Variável de ambiente `LBOT_MAX_CONTEXT_TOKENS`

**Regras:**
- A LLM gerencia seu próprio contexto (modelo ~8B decide o que é relevante)
- O harness não descarta mensagens automaticamente
- Se o contexto estourar, o erro da LLM é repassado ao usuário

### RF09 — CLI simplificado

A interface de linha de comando deve ser enxuta.

**A manter:**
- Loop REPL básico (entrada do usuário → output)
- Comando `/exit` para sair

**A remover:**
- Cores e formatação ANSI no terminal
- Banner de boas-vindas
- Comandos `/help`, `/history`, `/reset`
- Estilização visual dos outputs

**Regras:**
- Output mostra cada step do loop de forma concisa: tool chamada + resultado resumido
- Sem cores ou formatação especial

---

## Requisitos Não-Funcionais

- **Tamanho de arquivos:** máximo ~150-200 linhas por arquivo
- **Princípios Clean Code:** SRP, nomes significativos, funções pequenas, poucos argumentos
- **Compatibilidade:** manter arquitetura MCP existente (client-server via stdio)
- **Backend:** manter abstração de backend (`SimulatorBackend`) para suportar futuros backends
- **Limite de iterações:** manter máximo de 50 steps no loop ReAct
- **Sem testes:** zero arquivos ou configurações de teste no repositório

---

## Glossário / Definições

- **Harness:** módulo de orquestração do robô (`lbot-mcp/src/harness/`) que implementa o loop ReAct conectando LLM → ferramentas MCP
- **LLM:** Large Language Model, o "cérebro" do robô. Neste contexto, modelo ~8B parâmetros rodando via LM Studio com capacidade multimodal (visão)
- **MCP:** Model Context Protocol — arquitetura client-server via stdio para expor ferramentas do robô
- **LBML:** LBot Markup Language — formato de comando para movimentos do robô. Ex: `D30F;R90L;` (andar 30cm frente, rotacionar 90° esquerda)
- **Tradutor / TranslatorWrapper:** modelo Seq2Seq `LBotTranslatorV7` que converte linguagem natural em LBML
- **ReAct:** padrão Reasoning + Acting — a LLM alterna entre pensar e executar ferramentas
- **System prompt:** instrução inicial enviada à LLM que define personalidade, ferramentas e regras do robô
- **Backend:** camada de abstração que conecta o MCP server ao simulador web (HTTP)

---

## Premissas

- O tradutor Seq2Seq (`LBotTranslatorV7`) pode ser invocado diretamente do harness (atualmente está no MCP server)
- O modelo pequeno (~8B multimodal) é capaz de interpretar imagens base64
- O modelo pequeno consegue operar com o system prompt simplificado de ~30-50 linhas
- O simulador web (`lbot-simulator-web`) continua funcionando e não será alterado nesta tarefa
- O backend `SimulatorBackend` e sua API HTTP permanecem inalterados
- A arquitetura MCP (client-server via stdio com FastMCP) é mantida como está
- O tradutor Seq2Seq em si não será modificado — apenas seu ponto de invocação muda

---

## Fora de escopo

- Alterações no simulador web (`lbot-simulator-web/`)
- Modificações no modelo Seq2Seq do tradutor
- Alterações na API HTTP do backend/simulador
- Alterações no servidor MCP além da remoção da ferramenta `observe()`
- Novas funcionalidades para o robô (câmera, sensores, movimento)
- Correção de bugs existentes (a menos que surjam como consequência direta da refatoração)
- Otimização de performance do tradutor ou da comunicação MCP
- Criação de documentação ou README

---

## Cenários de Aceite

### CA01 — Estrutura de arquivos limpa
**Dado** o código do harness refatorado
**Quando** inspeciono os arquivos em `lbot-mcp/src/harness/`
**Então** nenhum arquivo ultrapassa ~200 linhas e cada arquivo tem uma única responsabilidade clara

### CA02 — Testes removidos
**Dado** o repositório após a refatoração
**Quando** busco por arquivos ou configurações de teste
**Então** não existem pastas `tests/`, nem configurações de pytest/vitest, nem dependências de teste

### CA03 — LLM gera movimento em linguagem natural
**Dado** o system prompt simplificado
**Quando** a LLM decide executar um movimento
**Então** ela chama `move()` com linguagem natural (ex: "ande 30cm para frente"), nunca com LBML

### CA04 — Tradutor converte NL para LBML
**Dado** um comando de movimento em linguagem natural (ex: "ande 50cm para frente e vire 90 graus para direita")
**Quando** o harness processa a chamada `move()`
**Então** o tradutor Seq2Seq é chamado, gera o LBML correspondente (ex: `D50F;R90R;`), e o movimento é executado

### CA05 — Tradutor falha → missão abortada
**Dado** um comando NL que o tradutor não consegue processar
**Quando** o harness chama o tradutor e recebe erro
**Então** a missão é abortada e o usuário recebe uma mensagem de erro clara

### CA06 — Sem validações programáticas
**Dado** qualquer chamada de movimento
**Quando** o harness processa a ação
**Então** nenhuma validação de proximidade, loop ou distância é aplicada — a LLM decide livremente

### CA07 — Prompt curto e adequado para modelo pequeno
**Dado** o system prompt
**Quando** verifico seu conteúdo
**Então** tem no máximo ~50 linhas, está em português, não contém formato LBML, não contém protocolo de busca, não contém classificação de ações, e explica as 3 ferramentas de forma clara

### CA08 — Ferramenta observe() removida
**Dado** as ferramentas disponíveis para a LLM
**Quando** a LLM precisa de informação do ambiente
**Então** ela usa `camera()` e/ou `proximity()` separadamente — `observe()` não existe mais

### CA09 — CLI simplificado
**Dado** o CLI do harness
**Quando** inicio uma sessão interativa
**Então** não há cores, banner, comandos `/help`, `/history` ou `/reset` — apenas loop REPL básico com `/exit`

### CA10 — Output de steps conciso
**Dado** o harness em execução
**Quando** a LLM executa cada step do loop ReAct
**Então** o terminal mostra de forma concisa qual ferramenta foi chamada e o resultado resumido, sem formatação especial
