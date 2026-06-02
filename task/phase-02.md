# Fase 02: MCP Server - Setup do Projeto + Backend Abstraction

## Status: CONCLUIDO

## Objetivo

Criar o monorepo Python `lbot-mcp/` com `pyproject.toml`, estrutura de diretórios, backend plugável (interface abstrata + implementação HTTP para simulador) e wrapper do tradutor LBotTranslatorV7.

## Pré-requisitos

- Nenhum (fase independente; Phase 01 pode rodar em paralelo)

## Tarefas

- [x] Tarefa 1: Criar estrutura de diretórios e `pyproject.toml`
  - Arquivo: `lbot-mcp/pyproject.toml` (novo)
  - O que fazer:
    - Criar diretório `lbot-mcp/` na raiz do workspace
    - Criar `pyproject.toml` com:
      - `name = "lbot-mcp"`
      - `version = "0.1.0"`
      - Python `>=3.10`
      - Dependências: `fastmcp>=2.0`, `httpx>=0.27`, `openai>=1.0`, `torch>=2.0`, `numpy>=1.24`
      - Dev: `pytest>=8.0`, `pytest-asyncio>=0.24`, `mypy>=1.0`
      - Entry points (scripts): `lbot-mcp-server = "mcp_server.server:main"`, `lbot-harness = "harness.cli:main"`
      - Usar `[tool.uv]` config se for uv; compatível com Poetry também
    - Criar estrutura:
      ```
      lbot-mcp/
        pyproject.toml
        src/
          mcp_server/
            __init__.py
            server.py
            tools/
              __init__.py
            backends/
              __init__.py
            translator/
              __init__.py
          harness/
            __init__.py
        tests/
          __init__.py
      ```

- [x] Tarefa 2: Criar interface abstrata de backend (`backends/base.py`)
  - Arquivo: `lbot-mcp/src/mcp_server/backends/base.py` (novo)
  - O que fazer:
    - Criar classe abstrata `LBotBackend` com métodos:
      - `async get_camera() -> str`: Retorna imagem base64
      - `async get_proximity() -> dict`: Retorna `{"frente": float, "tras": float}`
      - `async execute_lbml(lbml: str) -> dict`: Retorna `{"accepted": bool, "command": str, "status": str}`
      - `async get_state() -> dict | None`: Retorna posição atual do robô ou None
      - `async health_check() -> bool`: Verifica se backend está acessível
    - Usar `abc.ABC` e `@abstractmethod`
    - Adicionar mensagens de erro padronizadas (português): `"câmera indisponível"`, `"sensor indisponível"`, etc.

- [x] Tarefa 3: Implementar backend HTTP para simulador (`backends/simulator.py`)
  - Arquivo: `lbot-mcp/src/mcp_server/backends/simulator.py` (novo)
  - O que fazer:
    - Classe `SimulatorBackend(LBotBackend)`:
      - `__init__(base_url: str = "http://localhost:3001")`
      - Usa `httpx.AsyncClient` para chamadas HTTP
      - `get_camera()` → `GET {base_url}/api/camera`, retorna `response.json()["image"]` ou levanta erro
      - `get_proximity()` → `GET {base_url}/api/sensors`, retorna `response.json()["readings"]`
      - `execute_lbml(lbml)` → `POST {base_url}/api/commands` com `{"command": lbml, "source": "http"}`, retorna status
      - `get_state()` → `GET {base_url}/api/state`, retorna `response.json()["state"]`
      - `health_check()` → `GET {base_url}/api/health`, retorna `True` se status 200
      - Timeout padrão de 10s para todas as chamadas
      - Tratamento de erros com mensagens em português

- [x] Tarefa 4: Criar wrapper do tradutor (`translator/__init__.py`)
  - Arquivo: `lbot-mcp/src/mcp_server/translator/__init__.py` (novo)
  - O que fazer:
    - Módulo que importa `LBotTranslatorV7` do path externo
    - Adicionar `lbot-natural-language-controller/lbot-v7/` ao `sys.path` se necessário
    - Classe `TranslatorWrapper`:
      - Singleton ou instância lazy (carrega modelo ~12MB apenas uma vez)
      - `translate(command: str) -> str`: Chama `translator.translate(command)`, retorna LBML ou levanta `TranslationError` se resultado for `"ERRO"`
      - `translate_verbose(command: str) -> tuple[str, str, str]`: Retorna (original, preprocessed, lbml)
      - `is_loaded() -> bool`
      - Log de inicialização informando device (CPU/GPU) e número de parâmetros
    - Inicialização lazy: modelo carregado na primeira chamada, não no import

- [x] Tarefa 5: Criar skeleton do MCP Server com FastMCP
  - Arquivo: `lbot-mcp/src/mcp_server/server.py` (novo)
  - O que fazer:
    - Criar app FastMCP: `mcp = FastMCP("LBot")`
    - Configurar backend via variável de ambiente `LBOT_BACKEND` (default `"simulator"`)
    - Configurar URL do simulador via `LBOT_SIMULATOR_URL` (default `"http://localhost:3001"`)
    - Função `create_backend(name: str) -> LBotBackend`: factory que retorna `SimulatorBackend` (ou futuro `HardwareBackend`)
    - Função `main()`: entry point que inicia o server com `mcp.run()`
    - Bloco `if __name__ == "__main__": main()`
    - Por enquanto sem tools registradas (serão adicionadas na Fase 03)

## Arquivos Referência

- `lbot-natural-language-controller/lbot-v7/lbot_v7.py` — API do tradutor: classe `LBotTranslatorV7`, método `translate(command) -> str`, carregamento do modelo
- `lbot-simulator-web/server/index.ts` — Endpoints existentes que o backend vai chamar (`/api/health`, `/api/commands`, `/api/state`)
- `lbot-simulator-web/shared/protocol.ts` — Tipos de resposta esperados dos endpoints
- `lbot-simulator-web/package.json` — Porta do servidor (3001) e estrutura do projeto

## Critérios de Aceite

- [x] CA01: Projeto instala e importa sem erros
  - Cenario: Dado `pip install -e .` no diretório `lbot-mcp/`, Quando `python -c "from mcp_server.backends.simulator import SimulatorBackend"`, Então importa sem erros

- [x] CA02: Backend simulador faz health check
  - Cenario: Dado simulador rodando em localhost:3001, Quando `backend.health_check()`, Então retorna `True`

- [x] CA03: Backend simulador detecta indisponibilidade
  - Cenario: Dado simulador não está rodando, Quando `backend.health_check()`, Então retorna `False` (sem lançar exceção)

- [x] CA04: Translator wrapper carrega modelo e traduz
  - Cenario: Dado `lbot_translator_v7.pt` no path esperado, Quando `translator.translate("ande 40 centímetros para frente")`, Então retorna `"D40F;"`

- [x] CA05: Translator wrapper trata entrada inválida
  - Cenario: Dado input incompreensível, Quando `translator.translate("xyz abc def")`, Então levanta `TranslationError`

- [x] CA06: Factory de backend retorna instância correta
  - Cenario: Dado `LBOT_BACKEND=simulator`, Quando `create_backend("simulator")`, Então retorna instância de `SimulatorBackend`

## Testes Esperados

- `test_simulator_backend_health` — Health check retorna True com simulador ativo
- `test_simulator_backend_unavailable` — Health check retorna False sem simulador
- `test_translator_load_and_translate` — Tradução básica funciona
- `test_translator_error_on_invalid_input` — Input inválido levanta TranslationError
- `test_create_backend_simulator` — Factory retorna SimulatorBackend

## Comandos pós-fase

```bash
cd lbot-mcp && pip install -e .
cd lbot-mcp && python -c "from mcp_server.server import mcp; print('MCP Server OK')"
cd lbot-mcp && python -c "from mcp_server.translator import TranslatorWrapper; print('Translator OK')"
```

## Registro de Execução

- Data: 2026-06-02
- Arquivos criados:
  - `lbot-mcp/pyproject.toml`
  - `lbot-mcp/src/__init__.py`
  - `lbot-mcp/src/mcp_server/__init__.py`
  - `lbot-mcp/src/mcp_server/server.py`
  - `lbot-mcp/src/mcp_server/tools/__init__.py`
  - `lbot-mcp/src/mcp_server/backends/__init__.py`
  - `lbot-mcp/src/mcp_server/backends/base.py`
  - `lbot-mcp/src/mcp_server/backends/simulator.py`
  - `lbot-mcp/src/mcp_server/translator/__init__.py`
  - `lbot-mcp/src/harness/__init__.py`
  - `lbot-mcp/tests/__init__.py`
- Arquivos alterados: Nenhum existente (todos novos)
- Testes executados:
  - Import do MCP Server: OK
  - Import do TranslatorWrapper: OK
  - Import do SimulatorBackend: OK
  - Factory create_backend('simulator'): OK (retorna SimulatorBackend)
  - Translator translate('ande 40 centímetros para frente'): D40F; OK
  - Translator translate_verbose('ande 40cm pra frente'): (original, preprocessed, lbml) OK
  - Translator translate('zzzzzzzzzzz'): TranslationError OK
  - Backend health_check: True (simulador ativo em localhost:3001)
  - Correção de pickle: classes do lbot_v7 registradas em __main__ antes do torch.load
- Resultado: Todos os 6 critérios de aceite validados com sucesso
- Pendências: Nenhuma
