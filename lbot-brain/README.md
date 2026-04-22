# lbot-brain

MVP do cerebro do `lbot`, com CLI em texto, planner via LM Studio e contratos tipados para tools internas.

## O que existe hoje

- CLI interativo
- planejamento de turno com `assistantText + toolCall`
- personalidade brincalhona
- roteamento para `robot.execute` e `vision.describe`
- sessao em memoria
- modulo de visao com captura local de camera no macOS via `ffmpeg`

## O que ainda nao existe

- resposta pos-tool gerada pela LLM
- TTS/STT
- provider de camera do robo real

## Requisitos

- Node 20+
- LM Studio com a API local habilitada
- um modelo carregado, de preferencia `Qwen3.5-4B`
- `ffmpeg` instalado para capturar a camera USB no macOS

## Variaveis de ambiente

- `LBOT_MODEL`: nome do modelo carregado no LM Studio. Padrao: `qwen3.5-4b`
- `LBOT_VISION_MODEL`: modelo usado para `vision.describe`. Padrao: mesmo valor de `LBOT_MODEL`
- `LBOT_LM_STUDIO_BASE_URL`: padrao `http://127.0.0.1:1234/v1`
- `LBOT_LM_STUDIO_API_KEY`: padrao `lm-studio`
- `LBOT_PLANNER_TEMPERATURE`: padrao `0.2`
- `LBOT_PLANNER_MAX_TOKENS`: padrao `300`
- `LBOT_VISION_TEMPERATURE`: padrao `0.2`
- `LBOT_VISION_MAX_TOKENS`: padrao `400`
- `LBOT_VISION_SOURCE`: padrao `mac-camera`. Valores aceitos: `mac-camera`, `stub`
- `LBOT_FFMPEG_BIN`: padrao `ffmpeg`
- `LBOT_CAMERA_DEVICE_NAME`: padrao `XWF-1080P`
- `LBOT_CAMERA_VIDEO_SIZE`: padrao `1280x720`
- `LBOT_CAMERA_FRAMERATE`: padrao `30`
- `LBOT_CAMERA_CAPTURE_TIMEOUT_MS`: padrao `8000`

## Camera no macOS

Instale o `ffmpeg` com Homebrew:

```bash
brew install ffmpeg
```

Depois, permita acesso a camera para o app que estiver rodando o `lbot-brain`, como `Terminal`, `iTerm` ou `Visual Studio Code`.

Por padrao, o modulo de visao tenta usar a camera `XWF-1080P`. Se quiser trocar:

```bash
export LBOT_CAMERA_DEVICE_NAME="Nome da Camera"
```

O modelo usado em `vision.describe` precisa aceitar imagem. Se necessario, aponte um modelo separado:

```bash
export LBOT_VISION_MODEL="seu-modelo-com-visao"
```

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
