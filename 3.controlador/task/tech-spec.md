# Plano Tecnico: Reestruturacao do Harness - Movimento vs Tarefa

## Visao Geral

Reestruturar o harness do LBot para classificar e tratar diferentemente dois tipos de acao: **Movimento** (bem definido ou ambiguo) e **Tarefa** (acao inteligente). A classificacao e feita pelo LLM via system prompt, sem etapa de classificacao explicita. A implementacao envolve:

1. **Nova tool `observe`** que combina camera + proximidade em uma unica chamada
2. **Modificacao da tool `move`** para aceitar LBML direto (pular tradutor quando input ja e LBML valido)
3. **Reescrita completa do system prompt** para guiar o LLM na classificacao e execucao correta
4. **Atualizacao do ReActAgent** para tratar output do `observe` com injecao de imagem (mesmo padrao da tool `camera`)

## Modulos Envolvidos

- **lbot-mcp/src/mcp_server/tools/**: Modulo de tools MCP - adicionar `observe`, modificar `move`
- **lbot-mcp/src/mcp_server/server.py**: Registro da nova tool
- **lbot-mcp/src/harness/personality.py**: Reescrita completa do system prompt e tool descriptions
- **lbot-mcp/src/harness/agent.py**: Handler para tool `observe`, aumento de max_steps
- **lbot-mcp/tests/**: Testes unitarios e de integracao

## Arquivos Impactados

### Novos
- `lbot-mcp/src/mcp_server/tools/observe.py` - Tool observe que combina camera + proximidade
- `lbot-mcp/tests/test_observe.py` - Testes da tool observe

### Alterados
- `lbot-mcp/src/mcp_server/tools/movement.py` - Detectar LBML no input e pular tradutor
- `lbot-mcp/src/mcp_server/server.py` - Importar e registrar tool `observe`
- `lbot-mcp/src/harness/personality.py` - Reescrita completa do SYSTEM_PROMPT e get_tools_description()
- `lbot-mcp/src/harness/agent.py` - Handler para `observe` (injecao de imagem), max_steps=100
- `lbot-mcp/tests/test_agent.py` - Testes para observe handler e max_steps
- `lbot-mcp/tests/test_integration.py` - Testes integrados da tool observe e move com LBML

## Decisoes Tecnicas

| Decisao | Opcao escolhida | Justificativa |
|---------|-----------------|---------------|
| Tool move com LBML direto | Modificar `move` para detectar LBML via regex e pular tradutor | Evita criar tool extra, mantem interface simples. O LLM gera LBML e envia via `move` |
| Tool observe: formato de retorno | Mesmo padrao da camera - JSON com campo `image` + campo `proximity` | Permite reusar toda logica de injecao de imagem ja existente no agent |
| Validacao de limites da arena | Delegado ao LLM via system prompt | Conforme business-spec, fora de escopo do backend |
| Distancia de seguranca | Delegada ao LLM via system prompt (20cm em Tarefas) | Regra de comportamento, nao de codigo |
| Aumento de max_steps | Default 100 no construtor do ReActAgent | Permite override se necessario, abordagem mais limpa |
| Reescrita do prompt | Substituir SYSTEM_PROMPT em personality.py | Abordagem direta, sem necessidade de sistema de templates |
| Validacao de LBML gerado pelo LLM | Usar regex existente `^(D\d+[FBLR];\|R\d+[LR];)+$` | Validacao consistente com tradutor, rejeita LBML invalido |

## Dependencias entre Fases

- Fase 01 (MCP Tools) -> Fase 02 (Agent + Prompt): Agent precisa das tools registradas
- Fase 02 (Agent + Prompt) -> Fase 03 (Testes): Testes validam tudo que foi implementado

## Mapa de Fases

| Fase | Descricao | Modulo |
|------|-----------|--------|
| 01 | MCP Tools: criar `observe` e modificar `move` | mcp_server/tools |
| 02 | Agent + Prompt: reescrever personality.py, atualizar agent.py | harness |
| 03 | Testes: unitarios e integracao para todas as alteracoes | tests |