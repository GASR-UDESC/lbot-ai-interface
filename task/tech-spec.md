# Plano Técnico: LBot AI Interface - MCP Server, Harness e Simulador

## Visão Geral

Transformação do ecossistema LBot em plataforma baseada em MCP (Model Context Protocol). O trabalho se divide em duas frentes:

1. **Simulador estendido** (TypeScript): Adicionar renderização 3D headless (câmera 1ª pessoa) e sensores de proximidade ao `lbot-simulator-web`, expostos via API REST.
2. **MCP Server + Harness** (Python, monorepo): Construir servidor MCP com 3 ferramentas (câmera, proximidade, deslocamento) usando FastMCP, e um cliente CLI com loop agêntico ReAct usando LM Studio.

A comunicação é via HTTP entre MCP Server e simulador, e via stdio (MCP protocol) entre Harness e MCP Server.

## Módulos Envolvidos

| Módulo | O que será feito |
|--------|-----------------|
| `3.controlador/lbot-simulator-web/` | Adicionar headless Three.js renderer (`gl`), raycaster geométrico, endpoints `/api/camera` (GET, base64) e `/api/sensors` (GET, distâncias) |
| `3.controlador/lbot-mcp/` (novo) | Monorepo Python com `pyproject.toml` (uv), contendo `mcp_server/` (FastMCP) e `harness/` (CLI + ReAct agent) |
| `2.treinamento-de-modelo/lbot-natural-language-controller/lbot-v7/` | Apenas referenciado — importado como módulo pelo MCP Server via PYTHONPATH |

## Arquivos Impactados

### Novos

| Caminho | Finalidade |
|---------|-----------|
| `3.controlador/lbot-simulator-web/server/scene-renderer.ts` | Headless Three.js renderer com contexto WebGL nativo (`gl`), reutiliza geometria do robô e arena |
| `3.controlador/lbot-simulator-web/server/sensors.ts` | Cálculo geométrico de distância até paredes da arena (raycasting sem física) |
| `3.controlador/lbot-mcp/pyproject.toml` | Configuração do projeto Python (uv), dependências, entry points |
| `3.controlador/lbot-mcp/src/__init__.py` | Pacote base |
| `3.controlador/lbot-mcp/src/mcp_server/__init__.py` | Pacote do MCP Server |
| `3.controlador/lbot-mcp/src/mcp_server/server.py` | Entry point do FastMCP server |
| `3.controlador/lbot-mcp/src/mcp_server/tools/__init__.py` | Pacote de ferramentas MCP |
| `3.controlador/lbot-mcp/src/mcp_server/tools/camera.py` | Tool de câmera |
| `3.controlador/lbot-mcp/src/mcp_server/tools/proximity.py` | Tool de sensor de proximidade |
| `3.controlador/lbot-mcp/src/mcp_server/tools/movement.py` | Tool de deslocamento (NL → LBML → execução) |
| `3.controlador/lbot-mcp/src/mcp_server/backends/__init__.py` | Pacote de backends plugáveis |
| `3.controlador/lbot-mcp/src/mcp_server/backends/base.py` | Interface abstrata de backend |
| `3.controlador/lbot-mcp/src/mcp_server/backends/simulator.py` | Backend HTTP que comunica com 3.controlador/lbot-simulator-web |
| `3.controlador/lbot-mcp/src/mcp_server/translator/__init__.py` | Wrapper do LBotTranslatorV7 |
| `3.controlador/lbot-mcp/src/harness/__init__.py` | Pacote do Harness |
| `3.controlador/lbot-mcp/src/harness/cli.py` | CLI interativo (REPL) |
| `3.controlador/lbot-mcp/src/harness/agent.py` | Loop agêntico ReAct |
| `3.controlador/lbot-mcp/src/harness/mcp_client.py` | Conexão MCP client via stdio |
| `3.controlador/lbot-mcp/src/harness/personality.py` | System prompt com personalidade do robô |
| `3.controlador/lbot-mcp/tests/__init__.py` | Pacote de testes |
| `3.controlador/lbot-mcp/tests/test_backends.py` | Testes do backend simulador |
| `3.controlador/lbot-mcp/tests/test_translator.py` | Testes do wrapper do tradutor |
| `3.controlador/lbot-mcp/tests/test_tools.py` | Testes das ferramentas MCP |
| `3.controlador/lbot-mcp/tests/test_integration.py` | Testes de integração MCP Server + Simulador |

### Alterados

| Caminho | O que muda |
|---------|-----------|
| `3.controlador/lbot-simulator-web/server/index.ts` | Adicionar `GET /api/camera` e `GET /api/sensors` |
| `3.controlador/lbot-simulator-web/shared/protocol.ts` | Adicionar `CameraResponse`, `SensorsResponse`, `ProximityReadings` |
| `3.controlador/lbot-simulator-web/package.json` | Adicionar dependência `gl` e `@types/gl` |

## Decisões Técnicas

| Decisão | Opção escolhida | Justificativa |
|---------|-----------------|---------------|
| Renderização headless | `gl` (headless WebGL nativo) + Three.js no servidor Express | Funciona sem navegador, reutiliza modelos 3D existentes, renderização fiel ao simulador visual |
| Sensores de proximidade | Cálculo geométrico no servidor (distância raio-parede) | Não depende de física cannon-es (que roda só no browser), preciso o suficiente para arena retangular |
| Estrutura Python | Monorepo único com entry points `lbot-mcp-server` e `lbot-harness` | Compartilha backends e translator wrapper; evita duplicação |
| Integração do tradutor | Import direto do path existente (`2.treinamento-de-modelo/lbot-natural-language-controller/lbot-v7/`) | Sem duplicação de código nem modelo .pt, mesma fonte usada em benchmarks |
| Transporte MCP | stdio (Harness spawna MCP Server como subprocesso) | Padrão MCP mais comum, sem porta de rede, ideal para CLI local |
| Disponibilidade dos endpoints | Headless total (funcionam sem navegador) | Independência do browser; MCP Server pode operar com simulador em background |
| GPU do tradutor | Auto-detect (GPU se CUDA disponível) | Mantém comportamento atual do LBotTranslatorV7; inferência mais rápida quando GPU presente |
| Framework MCP | FastMCP | Especificado no RNF02, simplifica criação de tools com decorators |
| LLM | LM Studio via OpenAI SDK modo compatível | Especificado nos RNF03/RNF04 |
| Gerenciador Python | uv (pyproject.toml) | Recomendado pelo RNF01, rápido, compatível com pip |
| Testes | pytest (Python) + vitest (TypeScript) | Segue frameworks já em uso no projeto |

## Dependências entre Fases

```
Phase 01 (Simulator) ──────────────────────────────────────────┐
  │                                                            │
  ▼                                                            │
Phase 02 (MCP Server Setup) ──► Phase 03 (MCP Tools) ──┐      │
  │                                                      │      │
  │    ┌─────────────────────────────────────────────────┘      │
  │    │                                                        │
  ▼    ▼                                                        │
Phase 04 (Harness CLI) ──► Phase 05 (Tests) ◄──────────────────┘
```

- Fase 01 é independente (apenas TypeScript)
- Fase 02 → Fase 03 (tools dependem da estrutura e backend)
- Fase 03 → Fase 04 (harness conecta ao server completo)
- Fase 05 depende de todas as anteriores

## Mapa de Fases

| Fase | Descrição | Módulo | Estimativa |
|------|-----------|--------|------------|
| 01 | Simulador: Headless Renderer + Sensores | `3.controlador/lbot-simulator-web` | ~4 tarefas |
| 02 | MCP Server: Setup do Projeto + Backend | `3.controlador/lbot-mcp/` | ~5 tarefas |
| 03 | MCP Server: Implementação das Tools | `3.controlador/lbot-mcp/` | ~4 tarefas |
| 04 | Harness: CLI + ReAct Agent | `3.controlador/lbot-mcp/` | ~5 tarefas |
| 05 | Testes & Validação | todos | ~5 tarefas |
