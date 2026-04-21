# lbot-brain

MVP do cerebro do `lbot`, com CLI em texto, planner via LM Studio e contratos tipados para tools internas.

## O que existe hoje

- CLI interativo
- planejamento de turno com `assistantText + toolCall`
- personalidade brincalhona
- roteamento para `robot.execute` e `vision.describe`
- sessao em memoria
- stubs tecnicos das tools

## O que ainda nao existe

- implementacao real dos modulos `robot` e `vision`
- TTS/STT
- resposta pos-tool gerada pela LLM

## Requisitos

- Node 20+
- LM Studio com a API local habilitada
- um modelo carregado, de preferencia `Qwen3.5-4B`

## Variaveis de ambiente

- `LBOT_MODEL`: nome do modelo carregado no LM Studio. Padrao: `qwen3.5-4b`
- `LBOT_LM_STUDIO_BASE_URL`: padrao `http://127.0.0.1:1234/v1`
- `LBOT_LM_STUDIO_API_KEY`: padrao `lm-studio`
- `LBOT_PLANNER_TEMPERATURE`: padrao `0.2`
- `LBOT_PLANNER_MAX_TOKENS`: padrao `300`

## Rodando

```bash
npm install
npm run dev
```

## Testes

```bash
npm test
npm run build
```
