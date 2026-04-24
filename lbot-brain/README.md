# lbot-brain

MVP do cerebro do `lbot`, com CLI em texto, planner via LM Studio e contratos tipados para tools internas.

## O que existe hoje

- CLI interativo
- planejamento de turno com `assistantText + toolCall`
- personalidade brincalhona
- roteamento para `robot.execute` e `vision.describe`
- sessao em memoria
- modulo de visao com captura local de camera no macOS via `ffmpeg`
- modo voz local com STT/TTS offline

## O que ainda nao existe

- resposta pos-tool gerada pela LLM
- provider de camera do robo real

## Requisitos

- Node 20+
- LM Studio com a API local habilitada
- um modelo carregado, de preferencia `Qwen3.5-4B`
- `ffmpeg` instalado para capturar a camera USB no macOS
- Python 3.9+ para o bridge de voz local
- dependencias Python de voz instaladas em um ambiente local

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
- `LBOT_VOICE_PYTHON_BIN`: Python usado pelo bridge de voz. Padrao: `lbot-brain/.venv/bin/python3` quando existir, senao `python3`
- `LBOT_VOICE_BRIDGE_SCRIPT_PATH`: caminho do bridge de voz. Padrao: `scripts/voice_bridge.py`
- `LBOT_STT_MODEL`: path local para o modelo do `faster-whisper`. Padrao: `models/faster-whisper-small`
- `LBOT_STT_LANGUAGE`: idioma preferido do STT. Padrao: `pt`
- `LBOT_STT_DEVICE`: device do STT (`cpu`, `cuda`, etc). Padrao: `cpu`
- `LBOT_STT_COMPUTE_TYPE`: tipo de inferencia do STT. Padrao: `int8`
- `LBOT_STT_START_TIMEOUT_MS`: tempo maximo esperando alguem comecar a falar. Padrao: `15000`
- `LBOT_STT_SILENCE_MS`: silencio necessario para fechar um turno de fala. Padrao: `900`
- `LBOT_STT_MAX_UTTERANCE_MS`: duracao maxima de um turno capturado. Padrao: `20000`
- `LBOT_STT_VAD_MODE`: agressividade do VAD de `0` a `3`. Padrao: `2`
- `LBOT_STT_PREROLL_MS`: audio anterior ao inicio da fala para nao cortar o comeco. Padrao: `300`
- `LBOT_AUDIO_INPUT_DEVICE`: id numerico ou substring do dispositivo de entrada. Padrao: dispositivo default
- `LBOT_AUDIO_OUTPUT_DEVICE`: id numerico ou substring do dispositivo de saida. Padrao: dispositivo default
- `LBOT_TTS_MODEL_PATH`: path local para o modelo `.onnx` do Piper. Padrao: `models/pt_BR-faber-medium.onnx`
- `LBOT_TTS_SPEAKER`: speaker id ou nome, para vozes multispeaker. Padrao: vazio
- `LBOT_TTS_LENGTH_SCALE`: velocidade da fala do Piper. Vazio usa o default do modelo
- `LBOT_TTS_NOISE_SCALE`: variacao da fala do Piper. Vazio usa o default do modelo
- `LBOT_TTS_NOISE_W_SCALE`: variacao temporal da fala do Piper. Vazio usa o default do modelo
- `LBOT_TTS_VOLUME`: volume final aplicado pelo Piper. Vazio usa `1.0`

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

O modo padrao continua sendo texto puro.

Tambem da para escolher explicitamente:

```bash
npm run dev -- --mode text
npm run dev -- --mode voice
```

Atalhos:

```bash
npm run dev -- --voice
npm run dev -- --text
```

Ajuda da CLI:

```bash
npm run dev -- --help
```

## Voz Local

O modo voz roda todo localmente:

- STT com `faster-whisper`
- VAD com `webrtcvad`
- captura e playback com `sounddevice`
- TTS com `piper-tts`

O microfone so volta a escutar depois que o TTS termina de falar.

### Setup Python

Crie e ative um ambiente virtual local para voz:

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements-voice.txt
```

Se for usar esse ambiente, aponte:

```bash
export LBOT_VOICE_PYTHON_BIN="$PWD/.venv/bin/python3"
```

### Modelos Locais

Crie a pasta `models/` e coloque os artefatos locais nela.

Arquivos esperados por padrao:

- `models/faster-whisper-small/`
- `models/pt_BR-faber-medium.onnx`
- `models/pt_BR-faber-medium.onnx.json`

O STT espera um diretorio local ja convertido/baixado para `faster-whisper`.
O TTS espera o `.onnx` e o `.onnx.json` lado a lado.

Se quiser usar outros caminhos:

```bash
export LBOT_STT_MODEL="/caminho/para/seu/faster-whisper-model"
export LBOT_TTS_MODEL_PATH="/caminho/para/sua-voz.onnx"
```

### Dispositivos de Audio

Se o default do sistema nao for o microfone/alto-falante certo, configure por nome parcial ou id numerico:

```bash
export LBOT_AUDIO_INPUT_DEVICE="USB Microphone"
export LBOT_AUDIO_OUTPUT_DEVICE="MacBook Pro Speakers"
```

### Exemplo Completo

```bash
export LBOT_VOICE_PYTHON_BIN="$PWD/.venv/bin/python3"
export LBOT_STT_MODEL="$PWD/models/faster-whisper-small"
export LBOT_TTS_MODEL_PATH="$PWD/models/pt_BR-faber-medium.onnx"
npm run dev -- --voice
```

### Comportamento Atual do Modo Voz

- o modo texto continua disponivel por flag
- cada turno e sequencial: ouvir -> transcrever -> anunciar -> processar -> falar resumo final
- enquanto o TTS estiver falando, o microfone fica parado
- `sair`, `exit` e `quit` encerram o loop
- quando houver tool, o preambulo do assistente e falado antes da execucao
- durante a execucao de tool, a CLI mostra um loader e toca `assets/sounds/processing-loop.wav` em loop
- para respostas com `vision.describe`, a fala inclui o resumo final da ferramenta apos o processamento
- para falhas de tool, a fala inclui o resumo tecnico da falha

## Testes

```bash
npm test
npm run build
```
