# Fase 02: Frontend (Three.js + Cannon-es)

## Status: PENDENTE

## Objetivo

Adicionar os 6 objetos geometricos a cena Three.js do navegador, criar seus corpos fisicos no mundo cannon-es, e adicionar as 4 paredes fisicas ao mundo cannon-es. Ao final desta fase, o simulador visual no navegador deve mostrar os objetos coloridos com sombras, o robo deve colidir com eles e com as paredes, e o reset deve preservar os objetos.

## Pre-requisitos

- Fase 01 concluida (`shared/arena-objects.ts` criado e testado)
- `ARENA_OBJECTS` e `PHYSICAL_WALLS` disponiveis para importacao

## Tarefas

- [ ] Tarefa 1: Criar funcao para gerar mesh Three.js dos objetos
  - Arquivo: `3.controlador/lbot-simulator-web/src/simulator/arena.ts` (ou novo arquivo `src/simulator/objects.ts`)
  - O que fazer: Implementar `createArenaObjects()` que retorna um array de `THREE.Mesh` para cada objeto em `ARENA_OBJECTS`. Usar `BoxGeometry` para cubos, `SphereGeometry` para esferas, `ConeGeometry` para cones. Material: `MeshStandardMaterial` com a cor definida. Configurar `castShadow = true` e `receiveShadow = true`.
- [ ] Tarefa 2: Adicionar objetos na cena do navegador
  - Arquivo: `3.controlador/lbot-simulator-web/src/components/SimulatorCanvas.tsx`
  - O que fazer: Importar `createArenaObjects` e adicionar os meshes retornados a `scene` logo apos as paredes. Garantir que o cleanup no `useEffect` dispose das geometrias e materiais dos objetos junto com o restante da cena.
- [ ] Tarefa 3: Adicionar corpos fisicos dos objetos no cannon-es
  - Arquivo: `3.controlador/lbot-simulator-web/src/simulator/engine.ts`
  - O que fazer: No construtor, apos adicionar o robo, iterar sobre `ARENA_OBJECTS` e criar um `CANNON.Body` com massa 0 para cada objeto. Formas: `CANNON.Box` para cubos e cones (usar AABB), `CANNON.Sphere` para esferas. Posicionar em `(x, y/2, z)` onde y e a altura do objeto. Adicionar ao `this.world`.
- [ ] Tarefa 4: Adicionar paredes fisicas no cannon-es
  - Arquivo: `3.controlador/lbot-simulator-web/src/simulator/engine.ts`
  - O que fazer: Criar 4 `CANNON.Body` com massa 0 para as paredes usando `PHYSICAL_WALLS`. Forma: `CANNON.Box` com dimensoes correspondentes as paredes visuais (Norte/Sul: 204x7.5x4; Leste/Oeste: 4x7.5x200). Posicionar em y=7.5. Adicionar ao `this.world`.
- [ ] Tarefa 5: Verificar que reset nao remove objetos
  - Arquivo: `3.controlador/lbot-simulator-web/src/simulator/engine.ts`
  - O que fazer: Confirmar que `reset()` apenas reseta `robotBody` e estado. Nao deve haver codigo que limpe o mundo cannon-es ou a cena Three.js. Se houver, ajustar para preservar objetos.
- [ ] Tarefa 6: Verificar visualizacao no navegador
  - Arquivo: N/A (teste manual)
  - O que fazer: Rodar `npm run dev` e abrir o navegador. Verificar que os 6 objetos aparecem coloridos, lancam sombras, e o robo colide com eles e com as paredes.

## Arquivos Referencia

- `3.controlador/lbot-simulator-web/shared/arena-objects.ts` - Definicoes dos objetos e paredes (criado na Fase 01)
- `3.controlador/lbot-simulator-web/src/simulator/engine.ts` - Referencia para adicionar bodies ao cannon-es (pattern do robo e chao)
- `3.controlador/lbot-simulator-web/src/simulator/arena.ts` - Referencia para criar meshes com `MeshStandardMaterial` e sombras
- `3.controlador/lbot-simulator-web/src/components/SimulatorCanvas.tsx` - Referencia para adicionar/remover meshes da cena e cleanup

## Criterios de Aceite

- [ ] CA02 - Visualizacao 3D no navegador mostra objetos
  - Cenario: Dado que o simulador esta aberto no navegador, quando o usuario observa a arena, entao os 6 objetos coloridos estao visiveis no chao, lancando sombras.
- [ ] CA04 - Robo colide com objeto e nao atravessa
  - Cenario: Dado que existe um objeto no caminho do robo, quando o robo recebe o comando LBML para andar em direcao ao objeto, entao o robo para ou desliza ao lado do objeto, sem atravessa-lo.
- [ ] CA06 - Reset preserva objetos
  - Cenario: Dado que o robo se moveu e colidiu com objetos, quando `POST /api/reset` e executado, entao o robo volta ao centro, e todos os objetos permanecem nas mesmas posicoes originais.
- [ ] CA-PAREDE-01 - Robo nao atravessa paredes fisicas
  - Cenario: Dado que as paredes fisicas foram adicionadas, quando o robo anda em direcao a uma parede, entao ele colide e para, nao atravessando o limite da arena.

## Testes Esperados

- Nao ha testes unitarios automatizados para colisao fisica (requer navegador). A validacao e feita via:
  - Teste manual no navegador (`npm run dev`)
  - Verificacao de que `engine.reset()` nao remove bodies do mundo

## Comandos pos-fase

- `npm run check` - Verificar compilacao TypeScript sem erros
- `npm run dev` - Iniciar simulador e validar visualmente no navegador

## Registro de Execucao

<Preenchido pelo agente durante a execucao>

- Data:
- Arquivos criados:
- Arquivos alterados:
- Testes executados:
- Resultado:
- Pendencias:
