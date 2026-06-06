# Fase 05: Remover testes e limpar configurações

## Status: PENDENTE

## Objetivo

Remover todos os arquivos de teste, diretórios de teste, configurações de teste, caches e dependências de teste do repositório, conforme RF02.

## Pre-requisitos

- Nenhum (fase independente, pode rodar em paralelo com qualquer outra)

## Tarefas

- [ ] Tarefa 1: Remover diretório de testes Python
  - O que fazer: Deletar completamente `lbot-mcp/tests/` e todo seu conteúdo
  - Itens afetados:
    - `lbot-mcp/tests/__init__.py`
    - `lbot-mcp/tests/test_agent.py`
    - `lbot-mcp/tests/test_backends.py`
    - `lbot-mcp/tests/test_e2e.py`
    - `lbot-mcp/tests/test_integration.py`
    - `lbot-mcp/tests/test_observe.py`
    - `lbot-mcp/tests/test_personality.py`
    - `lbot-mcp/tests/test_translator.py`
    - `lbot-mcp/tests/__pycache__/` (bytecode cache)

- [ ] Tarefa 2: Remover diretório de testes TypeScript
  - O que fazer: Deletar completamente `lbot-simulator-web/tests/` e todo seu conteúdo
  - Itens afetados:
    - `lbot-simulator-web/tests/setup.ts`
    - `lbot-simulator-web/tests/api.test.ts`
    - `lbot-simulator-web/tests/arena-objects.test.ts`
    - `lbot-simulator-web/tests/lbml.test.ts`
    - `lbot-simulator-web/tests/sensors.test.ts`

- [ ] Tarefa 3: Remover arquivos de configuração de teste
  - O que fazer: Deletar:
    - `lbot-simulator-web/vitest.config.ts`
  - No `lbot-simulator-web/tsconfig.app.json`, remover `"tests"` e `"vitest.config.ts"` do array `include`

- [ ] Tarefa 4: Limpar `pyproject.toml`
  - Arquivo: `lbot-mcp/pyproject.toml`
  - O que fazer:
    - Remover seção `[project.optional-dependencies]` inteira (contém `pytest`, `pytest-asyncio`, `mypy`)
      - OU: se precisar manter `mypy`, extrair apenas `mypy` para `dev` e remover `pytest`/`pytest-asyncio`
    - Remover seção `[tool.uv]` de `dev-dependencies` (contém `pytest`, `pytest-asyncio`, `mypy`)
    - Remover seção `[tool.pytest.ini_options]` inteira
    - Manter `[tool.mypy]` se ainda quiser type checking (a menos que o usuário queira remover também)

- [ ] Tarefa 5: Limpar `package.json`
  - Arquivo: `lbot-simulator-web/package.json`
  - O que fazer:
    - Remover `"test": "vitest run"` da seção `"scripts"`
    - Remover da seção `"devDependencies"`:
      - `"@testing-library/jest-dom"`
      - `"@testing-library/react"`
      - `"@testing-library/user-event"`
      - `"jsdom"`
      - `"vitest"`

- [ ] Tarefa 6: Remover caches de pytest
  - O que fazer: Deletar diretórios:
    - `lbot-mcp/.pytest_cache/`
    - `3.controlador/.pytest_cache/`
    - `.pytest_cache/` (raiz do repositório)

- [ ] Tarefa 7: Verificar e remover `test_robustness.py` (se aplicável)
  - Arquivo: `2.treinamento-de-modelo/lbot-natural-language-controller/lbot-v7/test_robustness.py`
  - O que fazer: Este arquivo está fora do `3.controlador/`. Verificar com o contexto da business spec se deve ser removido. A business spec menciona "Fora de escopo: Modificações no modelo Seq2Seq do tradutor", e este teste está no diretório do tradutor. **Não remover** a menos que o usuário confirme.

## Arquivos Referência

- `lbot-mcp/pyproject.toml` — Config atual com pytest settings
- `lbot-simulator-web/package.json` — Scripts e devDependencies
- `lbot-simulator-web/tsconfig.app.json` — Include paths
- `lbot-simulator-web/vitest.config.ts` — Config do Vitest

## Critérios de Aceite

- [ ] CA01: Nenhum diretório `tests/` existe
  - Cenario: Dado o repositório / Quando busco `lbot-mcp/tests/` e `lbot-simulator-web/tests/` / Então não existem

- [ ] CA02: Nenhum arquivo de configuração de teste existe
  - Cenario: Dado o repositório / Quando busco `vitest.config.ts`, `.pytest_cache/` / Então não existem

- [ ] CA03: `pyproject.toml` sem referências a pytest
  - Cenario: Dado pyproject.toml / Quando busco por `pytest` / Então não encontro (exceto talvez em comentários)

- [ ] CA04: `package.json` sem scripts ou deps de teste
  - Cenario: Dado package.json / Quando busco por `vitest`, `jsdom`, `@testing-library` / Então não encontro

- [ ] CA05: `tsconfig.app.json` sem referência a tests
  - Cenario: Dado tsconfig.app.json / Quando verifico `include` / Então não contém `"tests"` nem `"vitest.config.ts"`

## Testes Esperados

A validação desta fase é a própria ausência de testes. Verificar com buscas no sistema de arquivos.

## Comandos pós-fase

```bash
# Verificar ausência de diretórios de teste
test ! -d lbot-mcp/tests && echo "lbot-mcp/tests/ removido" || echo "ERRO: ainda existe"
test ! -d lbot-simulator-web/tests && echo "lbot-simulator-web/tests/ removido" || echo "ERRO: ainda existe"

# Verificar ausência de arquivos de config de teste
test ! -f lbot-simulator-web/vitest.config.ts && echo "vitest.config.ts removido" || echo "ERRO: ainda existe"
test ! -d lbot-mcp/.pytest_cache && echo "lbot-mcp/.pytest_cache/ removido" || echo "ERRO: ainda existe"
test ! -d .pytest_cache && echo ".pytest_cache/ raiz removido" || echo "ERRO: ainda existe"

# Verificar pyproject.toml
grep -q 'pytest' lbot-mcp/pyproject.toml && echo "ERRO: pytest encontrado no pyproject.toml" || echo "pyproject.toml limpo"

# Verificar package.json
grep -q '"vitest"\|"jsdom"\|"@testing-library"' lbot-simulator-web/package.json && echo "ERRO: deps de teste em package.json" || echo "package.json limpo"
grep -q '"test"' lbot-simulator-web/package.json && echo "ERRO: script test em package.json" || echo "script test removido"

# Verificar tsconfig
grep -q '"tests"' lbot-simulator-web/tsconfig.app.json && echo "ERRO: tests em tsconfig" || echo "tsconfig limpo"
```

## Registro de Execução

- Data:
- Arquivos criados:
- Arquivos alterados:
- Testes executados:
- Resultado:
- Pendências:
