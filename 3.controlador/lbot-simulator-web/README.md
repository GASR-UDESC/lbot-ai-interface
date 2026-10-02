# Simulador LBot com estado único

Física Cannon em metros/segundos no servidor, com passos fixos de 60 Hz. A interface Three.js recebe estados e não controla a evolução física. LBML, diagnóstico e sensores usam centímetros/graus na fronteira da API.

## Executar

Requisitos: Node.js 22+, npm e Chromium gerenciado pelo Playwright.

```sh
npm ci
npm run setup:camera
npm run dev
```

Interface: `http://localhost:5173`. API: `http://127.0.0.1:3001`. A API também serve a interface em sua própria porta. A câmera 3D funciona sem uma aba aberta pelo usuário. Se Chromium ou WebGL falhar, retorna `camera_unavailable`; não substitui a imagem por um mapa.

Produção:

```sh
npm run build
npm run start
```

Verificação, incluindo câmera real em Chromium:

```sh
npm run build
npm test
```

## API

- `GET /api/health`, `/api/status`, `/api/state`: diagnóstico do servidor e operação.
- `POST /api/commands`: `{command:"D30F;R90L;", command_id?:string, session_id?:string}`.
- `GET /api/commands/:id`: progresso e conclusão efetiva, deslocamento medido e motivo de interrupção.
- `POST /api/stop`: parada imediata, fora da execução normal.
- `POST /api/reset`: interrompe a operação, reinicia a pose e cria outra sessão.
- `GET /api/camera`: PNG 640×480, identificação/revisão da captura e intrínsecos.
- `GET /api/sensors`: distâncias ao obstáculo frontal/traseiro mais próximo, validade e revisão.
- `GET /api/events`: SSE de cena e estado. Várias abas observam o mesmo servidor.

Estados de comando: `accepted`, `running`, `completed`, `blocked`, `cancelled`, `failed`, `timed_out`. Reutilizar um identificador com o mesmo comando é idempotente; outro comando recebe conflito. Operações concorrentes recebem `busy`. A UI acompanha o mesmo ciclo usado pelo MCP.

Convenção: orientação 0 aponta para +Z; esquerda aumenta a orientação, direita diminui. Deslocamentos são relativos ao robô. `D20L;` significa girar 90° à esquerda e avançar 20 cm, não deslocamento lateral. Giro acumulado é preservado para sequências e 360°.

Objetos e parâmetros da câmera são compartilhados entre renderização e física. A câmera não retorna pose absoluta; `/api/state` é diagnóstico e não deve ser percepção do agente.

## Avaliação reproduzível

```sh
PORT=3003 LBOT_ENABLE_EVAL=1 npm run start
```

Habilita `POST /api/scenario` para configurar objetos e pose de teste. É uma função de diagnóstico, desligada por padrão e ausente do MCP. O avaliador fica em `../lbot-mcp/evals/run.py`. Não execute a avaliação na mesma instância usada interativamente.

Comandos aceitos e terminais são registrados em `runs/simulator.jsonl`; `LBOT_TRACE_DIR` permite reunir logs com o harness. Consulte `../IMPLEMENTACAO_HARNESS_SIMULADOR.md` para o fluxo completo e os resultados locais.
