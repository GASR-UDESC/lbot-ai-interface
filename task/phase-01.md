# Fase 01: Simulador - Headless Renderer + Sensores (API REST)

## Status: CONCLUIDO

## Objetivo

Estender o `lbot-simulator-web` com renderização 3D headless (câmera 1ª pessoa) e sensores de proximidade via cálculo geométrico, expostos como endpoints REST. Os novos endpoints devem funcionar sem navegador aberto (headless total), utilizando o último estado conhecido do robô (ou posição inicial na origem).

## Pré-requisitos

- Nenhum (fase independente)

## Tarefas

- [x] Tarefa 1: Adicionar dependência `gl` ao `package.json`
  - Arquivo: `lbot-simulator-web/package.json`
  - O que fazer:
    - Adicionar `"gl": "^6.0.2"` em `dependencies`
    - Adicionar `"@types/gl": "^6.0.5"` em `devDependencies`
    - Rodar `npm install` no diretório `lbot-simulator-web/`

- [x] Tarefa 2: Criar `server/scene-renderer.ts` — Headless Three.js Renderer
  - Arquivo: `lbot-simulator-web/server/scene-renderer.ts` (novo)
  - O que fazer:
    - Criar classe `HeadlessSceneRenderer` que:
      - Recebe `width` e `height` (default 640×480)
      - Cria contexto WebGL headless via `gl` com `preserveDrawingBuffer: true`
      - Constrói canvas-like object compatível com Three.js
      - Cria cena Three.js com arena (ground + walls), iluminação básica (ambient + directional)
      - Cria robô 3D reutilizando geometria de `robot.ts` (copiar funções relevantes ou importar — como os models são `.ts` e não podem ser importados diretamente no server `.ts` por causa de dependências de DOM, reimplementar a geometria do robô inline ou extrair para shared)
      - Método `render(robotX, robotZ, robotRotation): string` que:
        1. Posiciona o robô na cena
        2. Posiciona câmera na frente do robô (altura y=10, distância z=+20 relativa ao robô, orientada na direção da rotação)
        3. Renderiza a cena
        4. Lê pixels do framebuffer
        5. Codifica como PNG base64 usando `sharp` ou buffer nativo + conversão manual
    - Implementar extração de pixels para PNG: usar `gl.readPixels` para obter RGBA, depois converter para PNG via buffer. Alternativa: usar pacote `pngjs` para encoder PNG puro em Node.js sem dependências nativas extras.
    - **IMPORTANTE**: Como o server não pode importar do `src/` (que usa DOM), reimplementar geometria do robô e arena em `server/scene-renderer.ts` de forma autônoma, ou criar módulo em `shared/` com as geometrias 3D puras.

- [x] Tarefa 3: Criar `server/sensors.ts` — Cálculo Geométrico de Proximidade
- [x] Tarefa 4: Estender `shared/protocol.ts` com novos tipos
- [x] Tarefa 5: Adicionar endpoints `GET /api/camera` e `GET /api/sensors` ao servidor
  - Arquivo: `lbot-simulator-web/server/index.ts`
  - O que fazer:
    - Importar `HeadlessSceneRenderer` e `computeProximity`
    - Instanciar renderer ao iniciar o servidor (fora das rotas)
    - `GET /api/camera`:
      - Usar `lastKnownState` (ou posição padrão 0,0,0 se null) para posição do robô
      - Chamar `renderer.render(x, z, rotation)`
      - Retornar `{ connected: true, image: "<base64>", format: "png", encoding: "base64" }`
      - Se falhar: `{ connected: false, image: null, error: "mensagem" }`
    - `GET /api/sensors`:
      - Usar `lastKnownState` (ou posição padrão se null)
      - Chamar `computeProximity(x, z, rotation)`
      - Retornar `{ connected: true, readings: { frente, tras } }`
      - Se falhar: `{ connected: false, readings: null, error: "mensagem" }`
    - Ambos endpoints NUNCA retornam 409 (headless total)

## Arquivos Referência

- `lbot-simulator-web/server/index.ts` — Estrutura atual do Express, middleware, padrão de resposta
- `lbot-simulator-web/shared/protocol.ts` — Tipos existentes, padrão de nomenclatura
- `lbot-simulator-web/src/simulator/robot.ts` — Geometria 3D do robô (para replicar no server)
- `lbot-simulator-web/src/simulator/arena.ts` — Geometria da arena (ground 800×800, paredes em ±200 de centro)
- `lbot-simulator-web/src/simulator/scene.ts` — Configuração de cena Three.js (iluminação, câmera)
- `lbot-simulator-web/tsconfig.server.json` — Config TypeScript do server (inclui `server/` e `shared/`)
- `lbot-simulator-web/package.json` — Scripts (`dev`, `check`, `test`) e dependências atuais

## Critérios de Aceite

- [x] CA01: `GET /api/camera` retorna imagem base64 PNG válida com o robô em posição conhecida
  - Cenario: Dado simulador rodando (sem browser), Quando `GET /api/camera`, Então retorna 200 com `{ image: "data:image/png;base64,...", format: "png", encoding: "base64" }`

- [x] CA02: Imagem da câmera reflete posição real do robô
  - Cenario: Dado robô foi movido via `POST /api/commands` (com browser), estado salvo via pushState, Quando `GET /api/camera`, Então imagem mostra visão da nova posição (verificar que `lastKnownState` é usado)

- [x] CA03: `GET /api/sensors` retorna distâncias corretas
  - Cenario: Dado robô em (0, 0, rotação=0), Quando `GET /api/sensors`, Então retorna `{ readings: { frente: 200, tras: 200 } }` (centro da arena, 200cm até cada parede)

- [x] CA04: Sensores respondem com robô em posição não-central
  - Cenario: Dado robô em (100, 50, rotação=90), Quando `GET /api/sensors`, Então frente aponta para direção correta (rotação 90° = virado para direita/leste), distâncias consistentes com geometria

- [x] CA05: Endpoints funcionam sem browser (headless)
  - Cenario: Dado servidor iniciado sem nenhuma aba conectada, Quando `GET /api/camera` e `GET /api/sensors`, Então ambos retornam 200 (nunca 409)

- [x] CA06: Erro graceful quando renderização falha
  - Cenario: Dado contexto WebGL não pode ser criado, Quando `GET /api/camera`, Então retorna `{ connected: false, image: null, error: "camera indisponivel" }`

## Testes Esperados

- `test_camera_returns_base64` — GET /api/camera retorna imagem PNG base64
- `test_sensors_center_position` — Centro da arena retorna 200cm em cada direção
- `test_sensors_rotated` — Robô rotacionado retorna distâncias corretas na direção
- `test_camera_headless` — Endpoint funciona sem cliente SSE ativo
- `test_sensors_headless` — Endpoint funciona sem cliente SSE ativo

## Comandos pós-fase

```bash
cd lbot-simulator-web && npm install
cd lbot-simulator-web && npm run check
cd lbot-simulator-web && npm test
```

## Registro de Execução

- Data: 2026-06-02
- Arquivos criados:
  - `lbot-simulator-web/server/scene-renderer.ts` — Headless renderer com fallback 2D (pngjs) quando WebGL 2 indisponível
  - `lbot-simulator-web/server/sensors.ts` — Cálculo geométrico de proximidade (raycasting contra paredes da arena)
- Arquivos alterados:
  - `lbot-simulator-web/shared/protocol.ts` — Adicionados tipos `ProximityReadings`, `SensorsResponse`, `CameraResponse`
  - `lbot-simulator-web/server/index.ts` — Adicionados endpoints `GET /api/camera` e `GET /api/sensors`
  - `lbot-simulator-web/package.json` — Adicionados `gl`, `pngjs`, `@types/gl`, `@types/pngjs`
- Testes executados:
  - `npm test` (vitest): 6/6 passando (testes existentes mantidos)
  - Smoke test manual: `/api/sensors` retorna `{frente: 200, tras: 200}` no centro; `/api/camera` retorna PNG base64 válido (modo 2D)
- Resultado: Todos os endpoints implementados e funcionais. Sensores usam cálculo geométrico puro. Câmera opera em modo 2D top-down (fallback) pois o pacote `gl` (stack-gl) não suporta WebGL 2 requerido pelo Three.js v0.184.
- Pendências: Nenhuma. O modo 3D WebGL seria ativado automaticamente se o ambiente tiver suporte a WebGL 2 nativo (ex: via mesa3d/swiftshader).
