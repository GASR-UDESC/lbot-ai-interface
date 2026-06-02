# Fase 04: Harness - CLI Interativo + Loop Agêntico ReAct

## Status: PENDENTE

## Objetivo

Criar o harness (MCP Client) com interface CLI interativa (REPL), conexão MCP via stdio, loop agêntico ReAct usando Ollama (Qwen 3.5 7B) com OpenAI SDK modo compatível, e personalidade do robô via system prompt.

## Pré-requisitos

- Fase 03 concluída (MCP Server com tools funcionais)
- Fase 01 concluída (simulador com endpoints REST)
- Ollama instalado e rodando com modelo `qwen3:7b` (ou configurável)

## Tarefas

- [ ] Tarefa 1: Criar system prompt com personalidade do robô
  - Arquivo: `lbot-mcp/src/harness/personality.py` (novo)
  - O que fazer:
    - Constante `SYSTEM_PROMPT` (string) com personalidade do robô em português:
      ```
      Você é um robô E-Puck, um pequeno robô educacional com rodas. 
      Você tem um corpo físico com sensores e uma câmera, e pode se mover 
      pela sala. Você é curioso, humilde e prestativo, mas sempre honesto 
      sobre suas limitações.
      
      Você está em uma sala retangular de 4m × 4m, delimitada por paredes.
      Sua posição inicial é no centro da sala.
      
      Você tem acesso às seguintes ferramentas para interagir com o mundo:
      
      1. camera() - Tira uma foto do que está à sua frente. Use para 
         identificar objetos, paredes e explorar visualmente.
      
      2. proximity() - Mede a distância (em cm) até a parede ou obstáculo 
         mais próximo à sua frente e atrás. Use para navegar com segurança.
      
      3. move(comando) - Executa um movimento. Você pode dar comandos como 
         "ande 30cm para frente", "vire 90 graus para direita", ou sequências 
         como "ande 40cm para frente, depois vire 90 graus para esquerda".
      
      Regras importantes:
      - Use proximity() antes de se mover para evitar colisões
      - Use camera() para entender o ambiente visualmente
      - Você não sabe sua posição exata — use os sensores para se orientar
      - Se uma ferramenta falhar, tente outra abordagem
      - Não invente capacidades que você não tem
      - Responda sempre em português, de forma amigável
      - Seja conciso — o usuário não quer explicações longas
      ```
    - Função `get_system_prompt() -> str` que retorna o prompt
    - Função `get_tools_description() -> list[dict]` que retorna descrição das tools no formato OpenAI function calling (caso necessário para o LLM)

- [ ] Tarefa 2: Criar cliente MCP via stdio
  - Arquivo: `lbot-mcp/src/harness/mcp_client.py` (novo)
  - O que fazer:
    - Classe `MCPClient`:
      - `__init__(server_command: list[str] = ["python", "-m", "mcp_server.server"])`
      - `async start()`: spawna subprocesso do MCP Server, conecta via stdio usando MCP SDK
      - `async list_tools() -> list[dict]`: Lista ferramentas disponíveis
      - `async call_tool(name: str, arguments: dict) -> str`: Chama uma tool e retorna resultado como string
      - `async close()`: Encerra subprocesso
      - Usa `mcp` SDK do lado cliente (ex: `mcp.client.stdio`)
    - Tratamento de erro:
      - Server não inicia → `ConnectionError("não consigo me comunicar com meu corpo no momento")`
      - Tool não encontrada → `ValueError`
      - Timeout na chamada → erro com mensagem amigável

- [ ] Tarefa 3: Criar loop agêntico ReAct
  - Arquivo: `lbot-mcp/src/harness/agent.py` (novo)
  - O que fazer:
    - Classe `ReActAgent`:
      - `__init__(mcp_client: MCPClient, llm_config: dict)`
      - Configuração LLM via `openai.OpenAI` com:
        - `base_url` do Ollama (default `http://localhost:11434/v1`)
        - `api_key` = `"ollama"` (placeholder)
        - Modelo: `"qwen3:7b"` (configurável via env `LBOT_LLM_MODEL`)
      - `async run(goal: str, max_steps: int = 20) -> str`:
        1. Montar mensagens: system prompt + user goal
        2. Loop:
          a. Chamar LLM com histórico de mensagens + tools disponíveis
          b. Se LLM retornar resposta final (sem tool call): retornar resposta
          c. Se LLM retornar tool call: executar via MCP client, adicionar resultado ao histórico
          d. Se max_steps atingido: retornar mensagem de timeout
          e. Se erro na tool: adicionar erro ao histórico, LLM decide próximo passo
        3. Retornar resposta final do LLM
      - `cancel()`: Flag para interromper loop (Ctrl+C)
      - Log de cada passo para debug (opcional, controlado por flag verbose)
    - Formato de mensagens compatível com OpenAI Chat Completions API (que Ollama suporta)
    - Suporte a function calling (tools) no formato OpenAI — Ollama + Qwen 3.5 suportam

- [ ] Tarefa 4: Criar CLI interativo (REPL)
  - Arquivo: `lbot-mcp/src/harness/cli.py` (novo)
  - O que fazer:
    - Função `main()`: entry point do harness
    - Fluxo:
      1. Exibir banner ASCII art simples: "LBot Harness - Seu robô E-Puck agêntico"
      2. Iniciar MCP client (spawn MCP Server)
      3. Listar tools disponíveis e exibir
      4. Entrar em loop REPL:
         - Prompt: `🤖 > `
         - Ler input do usuário
         - Se vazio: ignorar
         - Se `/help`: mostrar ajuda
         - Se `/tools`: listar tools
         - Se `/exit` ou `/quit`: sair
         - Se Ctrl+C durante execução: interromper agente, voltar ao prompt
         - Se Ctrl+C no prompt vazio: sair
         - Caso contrário: executar `agent.run(input)` e exibir resposta
      5. Ao sair: fechar MCP client, encerrar
    - Usar `asyncio.run()` para orquestrar
    - Tratamento de KeyboardInterrupt para interrupção graceful
    - Exibir mensagens de status (conectando, pensando...)

- [ ] Tarefa 5: Integrar todos os componentes e testar fluxo completo
  - Arquivo: `lbot-mcp/src/harness/__init__.py` (atualizar se necessário)
  - O que fazer:
    - Garantir que `python -m harness.cli` funcione como entry point
    - Testar fluxo completo: CLI → MCP client → MCP Server → Simulador
    - Verificar Ctrl+C interrompe agente mas mantém CLI
    - Verificar mensagens de erro amigáveis (server off, simulador off, etc.)

## Arquivos Referência

- `lbot-mcp/src/mcp_server/server.py` — MCP Server que será spawnado como subprocesso
- `lbot-mcp/src/mcp_server/tools/camera.py` — Tool camera (para descrição)
- `lbot-mcp/src/mcp_server/tools/proximity.py` — Tool proximity
- `lbot-mcp/src/mcp_server/tools/movement.py` — Tool move
- `lbot-mcp/pyproject.toml` — Dependências (openai, fastmcp)
- Documentação OpenAI SDK: `openai.OpenAI(base_url=..., api_key=...)` para Ollama
- Documentação MCP SDK Python: cliente stdio

## Critérios de Aceite

- [ ] CA01: CLI inicia e conecta ao MCP Server
  - Cenario: Dado MCP Server disponível, Quando `python -m harness.cli`, Então exibe banner, lista tools, mostra prompt `🤖 >`

- [ ] CA02: Comando simples do usuário é processado pelo agente
  - Cenario: Dado "tire uma foto", Quando enviado ao agente, Então LLM decide usar tool camera, resultado é reportado ao usuário

- [ ] CA03: Comando de movimento é executado
  - Cenario: Dado "ande 30cm para frente", Quando enviado, Então agente traduz (via tool move), executa, reporta resultado

- [ ] CA04: Agente usa múltiplas tools autonomamente
  - Cenario: Dado "explore a sala", Quando enviado, Então agente usa sensores + movimento + câmera em múltiplos passos ReAct

- [ ] CA05: Ctrl+C interrompe o agente mas mantém CLI
  - Cenario: Dado agente em execução, Quando Ctrl+C, Então agente para, CLI exibe "Interrompido." e volta ao prompt

- [ ] CA06: Erro de conexão com MCP Server é tratado
  - Cenario: Dado MCP Server indisponível, Quando CLI inicia, Então exibe "não consigo me comunicar com meu corpo no momento" e encerra graceful

- [ ] CA07: Erro de ferramenta é comunicado naturalmente
  - Cenario: Dado simulador offline durante execução, Quando agente tenta usar tool, Então LLM informa o usuário de forma amigável que não consegue acessar o corpo

- [ ] CA08: Comando `/help` mostra ajuda
  - Cenario: Dado CLI ativo, Quando `/help`, Então lista comandos disponíveis

- [ ] CA09: Comando `/tools` lista ferramentas
  - Cenario: Dado CLI ativo, Quando `/tools`, Então lista as 3 tools com descrição

## Testes Esperados

- `test_system_prompt_contains_tools` — Prompt descreve as 3 ferramentas
- `test_agent_single_step_camera` — Agente usa tool camera para "tire uma foto"
- `test_agent_single_step_move` — Agente usa tool move para comando de movimento
- `test_agent_multi_step_explore` — Agente usa 3+ ferramentas para "explore a sala"
- `test_agent_error_recovery` — Agente lida com erro de tool e tenta alternativa
- `test_mcp_client_list_tools` — Cliente lista tools corretamente
- `test_mcp_client_call_tool` — Cliente chama tool e recebe resultado
- `test_cli_interrupt_graceful` — Ctrl+C não quebra o CLI

## Comandos pós-fase

```bash
cd lbot-mcp && python -c "from harness.personality import get_system_prompt; print(get_system_prompt()[:100])"
cd lbot-mcp && python -c "from harness.mcp_client import MCPClient; print('MCP Client OK')"
cd lbot-mcp && python -c "from harness.agent import ReActAgent; print('ReAct Agent OK')"
```

## Registro de Execução

*Preenchido pelo agente durante a execução*

- Data:
- Arquivos criados:
- Arquivos alterados:
- Testes executados:
- Resultado:
- Pendências:
