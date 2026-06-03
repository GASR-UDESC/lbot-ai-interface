# Fase 03: Servidor (Headless + Sensores)

## Status: CONCLUIDO

## Objetivo

Corrigir a escala da arena no renderer headless WebGL (de 800x800 para 400x400), adicionar os 6 objetos na cena headless, atualizar o calculo de sensores de proximidade para detectar objetos via AABB, e adicionar testes automatizados para sensores e estrutura da cena headless.

## Pre-requisitos

- Fase 01 concluida (`shared/arena-objects.ts` com AABB)
- Fase 02 concluida (objetos no frontend e fisica)

## Tarefas

- [x] Tarefa 1: Corrigir escala da arena no headless renderer
  - Arquivo: `3.controlador/lbot-simulator-web/server/scene-renderer.ts`
  - O que fazer: Alterar `ARENA_WORLD` de 800 para 400, e `HALF_ARENA` para 200. Ajustar as posicoes e dimensoes das paredes no headless para corresponder ao frontend: `arenaSize=400`, paredes em `±204` (400/2 + 8/2), geometria Norte/Sul `408x15x8`, Leste/Oeste `8x15x400`. Ajustar o fallback 2D (`render2DScene`) para usar `ARENA_WORLD=400` e escala correspondente.
- [x] Tarefa 2: Adicionar objetos na cena headless
  - Arquivo: `3.controlador/lbot-simulator-web/server/scene-renderer.ts`
  - O que fazer: No construtor do `HeadlessSceneRenderer`, apos adicionar as paredes, iterar sobre `ARENA_OBJECTS` e criar meshes Three.js identicos aos do navegador (BoxGeometry, SphereGeometry, ConeGeometry) com as mesmas cores e posicoes. Adicionar a `scene`. Garantir que `castShadow = true` e `receiveShadow = true`.
- [x] Tarefa 3: Atualizar sensores para detectar objetos via AABB
  - Arquivo: `3.controlador/lbot-simulator-web/server/sensors.ts`
  - O que fazer: Importar `ARENA_OBJECTS` e `getObjectAABB`. Criar funcao `rayAABBDistance(ox, oz, dx, dz, aabb)` que calcula a distancia de interseccao de um raio com uma AABB. Modificar `computeProximity` para, alem de chamar `rayWallDistance`, iterar sobre `ARENA_OBJECTS` e chamar `rayAABBDistance` para cada um. A distancia final e o minimo entre paredes e objetos.
- [x] Tarefa 4: Adicionar testes para sensores detectando objetos
  - Arquivo: `3.controlador/lbot-simulator-web/tests/sensors.test.ts`
  - O que fazer: Adicionar casos de teste onde o robo esta posicionado a uma distancia conhecida de um objeto (ex: 50 cm a frente de um cubo em (-150, -150)) e verificar que `frente` retorna a distancia ao objeto, nao a parede. Testar tambem objeto atras (sensor `tras`). Testar canto onde objeto e parede estao alinhados.
- [x] Tarefa 5: Adicionar teste de integracao para cena headless
  - Arquivo: `3.controlador/lbot-simulator-web/tests/api.test.ts`
  - O que fazer: Adicionar teste que verifica que o `HeadlessSceneRenderer` instancia corretamente e que sua cena interna (acessivel via propriedades privadas ou refatoracao de teste) contem os meshes dos 6 objetos. Alternativamente, verificar que a resposta de `/api/camera` ainda retorna imagem valida e que o renderer esta disponivel.
- [x] Tarefa 6: Verificar fallback 2D sem objetos
  - Arquivo: `3.controlador/lbot-simulator-web/server/scene-renderer.ts`
  - O que fazer: Confirmar que `render2DScene` nao foi alterado para desenhar objetos (deve continuar apenas com parede, robo e chao). O fallback 2D deve continuar funcionando normalmente.

## Arquivos Referencia

- `3.controlador/lbot-simulator-web/shared/arena-objects.ts` - Definicoes dos objetos e funcoes AABB
- `3.controlador/lbot-simulator-web/server/scene-renderer.ts` - Estrutura atual do headless renderer (pares de parede, robo, camera)
- `3.controlador/lbot-simulator-web/server/sensors.ts` - Logica atual de raycasting apenas com paredes
- `3.controlador/lbot-simulator-web/tests/sensors.test.ts` - Testes existentes de sensores (pattern a seguir)
- `3.controlador/lbot-simulator-web/tests/api.test.ts` - Testes de integracao existentes

## Criterios de Aceite

- [x] CA01 - Camera mostra objetos na imagem
  - Cenario: Dado que o simulador esta rodando com o robo posicionado de forma que um objeto esteja a sua frente, quando a ferramenta de camera e acionada via `GET /api/camera` (modo WebGL), entao a imagem retornada em base64 contem a representacao do objeto (cor e forma visiveis).
- [x] CA03 - Sensor de proximidade detecta objeto a frente
  - Cenario: Dado que o robo esta a 50 cm de um objeto a sua frente e a 200 cm da parede, quando `GET /api/sensors` e chamado, entao o valor de `frente` retornado e ~50 cm (o objeto, nao a parede).
- [x] CA05 - Renderer 2D fallback continua funcionando
  - Cenario: Dado que o ambiente nao suporta WebGL 2 headless, quando `GET /api/camera` e chamado, entao a imagem 2D top-down e retornada normalmente (sem objetos, comportamento aceitavel).
- [x] CA-SCALE-01 - Escala da arena headless alinhada com frontend
  - Cenario: Dado que o headless renderer foi corrigido, quando comparamos as dimensoes das paredes no headless com as do frontend, entao ambas usam arena 400x400 com paredes em posicoes identicas.

## Testes Esperados

- `test_sensor_detectsObjectInFront` - Robo a 50cm de cubo, frente deve retornar ~50cm
- `test_sensor_detectsObjectBehind` - Robo a 30cm de esfera atras, tras deve retornar ~30cm
- `test_sensor_prefersCloserObjectOverWall` - Objeto mais proximo que parede, sensor retorna distancia ao objeto
- `test_sensor_noObjectInRange` - Sem objeto no caminho, sensor continua retornando distancia a parede
- `test_headless_containsObjects` - HeadlessSceneRenderer cena contem meshes dos 6 objetos
- `test_headless_scaleAligned` - Constantes de escala no headless sao 400x400
- `test_fallback2D_noObjects` - Fallback 2D nao desenha objetos (comportamento aceitavel)

## Comandos pos-fase

- `npm run check` - Verificar compilacao TypeScript sem erros
- `npm test` - Rodar suite de testes completa (sensors + api)

## Registro de Execucao

- Data: 2026-06-02
- Arquivos criados:
  - Nenhum (todas as alteracoes foram em arquivos existentes)
- Arquivos alterados:
  - `3.controlador/lbot-simulator-web/server/scene-renderer.ts` - Corrigida escala da arena (800->400), adicionados 6 objetos na cena headless, atualizado tipo THREE com SphereGeometry/ConeGeometry
  - `3.controlador/lbot-simulator-web/server/sensors.ts` - Adicionada deteccao de objetos via AABB nos sensores de proximidade (rayAABBDistance + iteracao sobre ARENA_OBJECTS)
  - `3.controlador/lbot-simulator-web/tests/sensors.test.ts` - Adicionados 4 novos testes de sensor detectando objetos; atualizados 8 testes existentes com novos valores esperados (objetos agora sao detectados)
  - `3.controlador/lbot-simulator-web/tests/api.test.ts` - Adicionados 3 novos testes de integracao para HeadlessSceneRenderer (disponibilidade, objetos na cena, escala 400x400)
- Testes executados:
  - `npm run check` (tsc app + server) -> 0 erros
  - `npm test` (vitest run) -> 48/48 passaram (incluindo 7 novos testes e 8 testes atualizados)
- Resultado: SUCESSO. Headless renderer corrigido para escala 400x400, objetos adicionados na cena headless, sensores detectando objetos via AABB, testes passando.
- Pendencias:
  - Testes de inspecao da cena headless (objetos e ground geometry) sao pulados quando o ambiente nao suporta WebGL headless (modo 2D fallback). Isso e aceitavel pois o fallback 2D continua funcionando.
  - A proxima fase (Fase 04) deve validar a consistencia completa do sistema.
