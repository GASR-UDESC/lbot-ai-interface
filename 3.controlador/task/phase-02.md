# Fase 02: Alterações no MCP server (translate tool + remover observe + simplificar move)

## Status: PENDENTE

## Objetivo

Fazer alterações pontuais no MCP server:
1. Adicionar nova ferramenta `translate` que expõe o `TranslatorWrapper` como MCP tool
2. Remover a ferramenta `observe` (deletar arquivo e limpar imports)
3. Simplificar a ferramenta `move` para aceitar apenas LBML (remover branch de tradução NL→LBML)

## Pre-requisitos

- Fase 01 concluída (tool_handler.py referencia `translate` tool, mas não depende dela para build)

## Tarefas

- [ ] Tarefa 1: Criar `translate.py` (nova MCP tool)
  - Arquivo: `lbot-mcp/src/mcp_server/tools/translate.py`
  - O que fazer: Criar tool `translate` que:
    - Registra com `@mcp.tool()` do FastMCP
    - Assinatura: `async def translate(command: str) -> str`
    - Importa `get_translator()` de `mcp_server.context`
    - Chama `get_translator().translate(command)`
    - Se resultado for `"ERRO"`, retorna `"ERRO"`
    - Caso contrário retorna a string LBML
    - Docstring descrevendo a ferramenta

- [ ] Tarefa 2: Deletar `observe.py`
  - Arquivo: `lbot-mcp/src/mcp_server/tools/observe.py`
  - O que fazer: Deletar o arquivo completamente

- [ ] Tarefa 3: Simplificar `movement.py` (remover tradução NL→LBML)
  - Arquivo: `lbot-mcp/src/mcp_server/tools/movement.py`
  - O que fazer: 
    - Remover a lógica de detecção de formato NL vs LBML
    - Remover a chamada a `translator.translate_verbose()`
    - `move()` passa a aceitar apenas LBML puro (formato `D30F;R90R;`)
    - Validar que o input casa com regex LBML: `^(D\d+[FBLR];|R\d+[LR];)+$`
    - Se não casar, retornar erro informando formato esperado
    - Manter a chamada a `backend.execute_lbml(lbml)`

- [ ] Tarefa 4: Atualizar `server.py`
  - Arquivo: `lbot-mcp/src/mcp_server/server.py`
  - O que fazer:
    - Remover `import mcp_server.tools.observe  # noqa: F401`
    - Adicionar `import mcp_server.tools.translate  # noqa: F401`

- [ ] Tarefa 5: Verificar se há `router.py` residual
  - Arquivo: `lbot-mcp/src/mcp_server/tools/router.py` (se existir)
  - O que fazer: Se o arquivo fonte existir, deletar (era referenciado por `.pyc` residual no `__pycache__`). Se apenas `.pyc` existe, deletar o `.pyc`.

## Arquivos Referência

- `lbot-mcp/src/mcp_server/tools/movement.py` — Código atual do move tool, para saber o que remover
- `lbot-mcp/src/mcp_server/tools/observe.py` — Para confirmar o que está sendo deletado
- `lbot-mcp/src/mcp_server/tools/camera.py` — Padrão de implementação de MCP tool (para seguir na translate tool)
- `lbot-mcp/src/mcp_server/server.py` — Onde os imports de tools são feitos
- `lbot-mcp/src/mcp_server/translator/__init__.py` — `TranslatorWrapper` e `get_translator()`
- `lbot-mcp/src/mcp_server/context.py` — Função `get_translator()`

## Critérios de Aceite

- [ ] CA01: `translate` tool registrada e funcional
  - Cenario: Dado MCP server rodando / Quando listo tools / Então `translate` aparece na lista com parâmetro `command: string`

- [ ] CA02: `translate` retorna LBML para comando NL válido
  - Cenario: Dado comando "ande 30cm para frente" / Quando chamo translate / Então retorna algo como "D30F;" (não "ERRO")

- [ ] CA03: `translate` retorna "ERRO" para comando inválido
  - Cenario: Dado comando nonsense "xyz" / Quando chamo translate / Então retorna "ERRO"

- [ ] CA04: `observe` tool não existe mais
  - Cenario: Dado MCP server rodando / Quando listo tools / Então `observe` NÃO aparece na lista

- [ ] CA05: `move` tool rejeita linguagem natural
  - Cenario: Dado comando "ande 30cm para frente" / Quando chamo move / Então retorna erro informando formato LBML esperado

- [ ] CA06: `move` tool aceita LBML válido
  - Cenario: Dado comando "D30F;R90R;" / Quando chamo move / Então executa normalmente via backend

- [ ] CA07: Nenhum arquivo `.py` de `observe` ou `router` existe
  - Cenario: Dado o diretório tools/ / Quando listo arquivos / Então observe.py e router.py não existem

## Testes Esperados

(Não há testes automatizados — RF02. Validação manual via MCP inspector ou listando tools.)

## Comandos pós-fase

```bash
# Verificar que o servidor MCP inicia e lista as tools corretas
cd lbot-mcp && python -c "
import asyncio
from mcp_server.server import mcp
async def check():
    # Listar tools registradas (via FastMCP interno)
    tools = await mcp._tool_manager.list_tools()
    names = [t.name for t in tools]
    print('Tools:', names)
    assert 'translate' in names, 'translate tool missing'
    assert 'observe' not in names, 'observe tool should be removed'
    assert 'camera' in names
    assert 'proximity' in names
    assert 'move' in names
    print('OK')
asyncio.run(check())
"

# Verificar que observe.py não existe
test ! -f lbot-mcp/src/mcp_server/tools/observe.py && echo "observe.py removido"
```

## Registro de Execução

- Data:
- Arquivos criados:
- Arquivos alterados:
- Testes executados:
- Resultado:
- Pendências:
