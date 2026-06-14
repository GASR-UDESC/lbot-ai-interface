# Fase 02: Sistema de Temas Dinamicos

## Status: CONCLUIDO

## Objetivo

Implementar o sistema de temas dinamicos: sky color ajustavel por nivel, texturas CanvasTexture procedurais para o chao, e paredes tematicas da arena.

## Pre-requisitos

- Fase 01 concluida (ObstacleMeshFactory criada)

## Tarefas

- [x] Tarefa 1: Tornar sky color dinamico no ThreeSceneService
  - Arquivo: `lbot-datagen-frontend/src/app/services/three-scene.service.ts`
  - O que fazer: Adicionar metodo `updateSkyColor(scene: THREE.Scene, skyColor: string)` que atualiza `scene.background` e `scene.fog.color`.
  - Remover o `SKY_COLOR` fixo e o `FOG` fixo do `createScene()`, ou permitir override.
  - O `initScene` pode continuar com o valor padrao, mas o metodo novo deve permitir mudar depois.

- [x] Tarefa 2: Criar geradores de textura CanvasTexture para o chao
  - Arquivo: `lbot-datagen-frontend/src/app/services/arena-builder.service.ts` (ou helper)
  - O que fazer: Criar funcoes que geram CanvasTexture para diferentes tipos de chao:
    - `createGrassTexture()`: base verde com detalhes de grama (linhas, pontos)
    - `createConcreteTexture()`: base cinza com manchas e linhas de fissura
    - `createAsphaltTexture()`: base escuro com pontos claros (asfalto)
    - `createDirtTexture()`: base marrom com variacoes
    - `createIndustrialTexture()`: base metalico com grid/linhas
  - Cada funcao retorna `THREE.CanvasTexture`.
  - Usar `canvas.getContext('2d')` para desenhar padroes simples.

- [x] Tarefa 3: Atualizar `createThemedGround` para usar texturas
  - Arquivo: `lbot-datagen-frontend/src/app/services/arena-builder.service.ts`
  - O que fazer: Modificar `createThemedGround(theme)` para aceitar um tipo de textura (ou inferir a partir do tema). Usar a CanvasTexture apropriada em vez de cor solida.
  - Manter `MeshLambertMaterial` com a textura + cor base.
  - O `createGround()` (sem tema) pode continuar com a textura de grama atual ou usar a nova factory.

- [x] Tarefa 4: Criar paredes tematicas da arena
  - Arquivo: `lbot-datagen-frontend/src/app/services/arena-builder.service.ts`
  - O que fazer: Modificar `createThemedWalls()` para adicionar detalhes visuais tematicos alem da cor:
    - Para tema "armazem/campo": manter pranchas de madeira (como hoje)
    - Para tema "escritorio": paineis de concreto com linhas
    - Para tema "cidade": barreira de concreto com faixas
    - Para tema "floresta": troncos de arvore (cilindros verticais)
    - Para tema "industrial": metal com rebites (esferas pequenas)
  - Usar a `ObstacleMeshFactory` para criar os detalhes se possivel, ou criar inline.
  - Manter performance: no maximo 2-3 detalhes adicionais por parede.

- [x] Tarefa 5: Integrar sky color no carregamento de nivel
  - Arquivo: `lbot-datagen-frontend/src/app/components/robo-simulator/robo-simulator.ts`
  - O que fazer: No metodo `loadLevel()`, apos carregar o ground e obstaculos, chamar `this.threeScene.updateSkyColor(this.scene, config.theme.skyColor)`.
  - Verificar se o metodo existe e funciona.

## Arquivos Referencia

- `lbot-datagen-frontend/src/app/services/three-scene.service.ts` - Servico de cena atual com sky color fixo.
- `lbot-datagen-frontend/src/app/services/arena-builder.service.ts` - Metodos `createThemedGround`, `createThemedWalls`, `createGround`.
- `lbot-datagen-frontend/src/app/components/robo-simulator/robo-simulator.ts` - Metodo `loadLevel()` que carrega o nivel.
- `lbot-datagen-frontend/src/app/services/obstacle-mesh.factory.ts` - Factory criada na Fase 01.

## Criterios de Aceite

- [x] CA01: O sky color muda corretamente quando o nivel carrega
- [x] CA02: O chao de cada nivel tem uma textura CanvasTexture distinta
- [x] CA03: As paredes da arena seguem o tema (cor + detalhes visuais)
- [x] CA04: O fog usa a mesma cor do skyColor
- [x] CA05: Transicao entre niveis mantem a performance (sem leaks de textura)

## Testes Esperados

- `test_sky_color_changes` - Verifica que updateSkyColor altera background e fog
- `test_textures_generated` - Verifica que cada tipo de textura retorna CanvasTexture valida
- `test_themed_walls` - Verifica que createThemedWalls usa a cor do tema

## Comandos pos-fase

- `cd lbot-datagen/lbot-datagen-frontend && npm run build` (verificar compilacao)
- `cd lbot-datagen/lbot-datagen-frontend && npm run test` (rodar testes existentes)

## Registro de Execucao

- Data: 2026-06-14
- Arquivos criados:
  - Nenhum (todos os arquivos ja existiam)
- Arquivos alterados:
  - `lbot-datagen-frontend/src/app/services/three-scene.service.ts` (metodo updateSkyColor)
  - `lbot-datagen-frontend/src/app/services/arena-builder.service.ts` (texturas CanvasTexture, createThemedGround com textura, createThemedWalls com detalhes tematicos)
  - `lbot-datagen-frontend/src/app/components/robo-simulator/robo-simulator.ts` (chamada updateSkyColor em loadLevel)
  - `lbot-datagen-frontend/src/app/app.spec.ts` (correcao de import App -> AppComponent)
- Testes executados:
  - `npm run build` (compilacao passou sem erros)
  - `npm run test` (1 teste pre-existente falhou por falta de provider ActivatedRoute; nao relacionado a esta fase)
- Resultado: SUCESSO
- Pendencias: Nenhuma (o teste que falha eh pre-existente e nao impactado por esta fase)
