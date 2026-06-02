# Plano Tecnico: Adicionar Objetos e Itens no Simulador

## Visao Geral

A implementacao adiciona 6 objetos geometricos estaticos (cubos, esferas, cones) coloridos na arena do simulador 3D web, com consistencia entre frontend (Three.js), fisica (cannon-es), renderizacao headless WebGL e sensores de proximidade. Alem disso, corrige a inconsistencia de escala da arena no headless renderer e adiciona paredes fisicas ao mundo cannon-es.

A abordagem e:
1. **Centralizar configuracao** em `shared/arena-objects.ts` para evitar duplicacao
2. **AABB simplificada** para todos os objetos nos sensores (uniformidade)
3. **Box AABB** para cones na fisica (cannon-es nao tem Cone nativo)
4. **Corrigir escala** do headless renderer de 800x800 para 400x400 (alinhar com frontend)
5. **Adicionar paredes fisicas** para consistencia (robô nao atravessa mais paredes)

## Modulos Envolvidos

- **`shared/`**: Novo modulo `arena-objects.ts` com definicoes centralizadas dos objetos e paredes fisicas
- **`src/simulator/`**: `engine.ts` (fisica), `arena.ts` (visual das paredes), `scene.ts` (cena Three.js), `types.ts` (tipos)
- **`src/components/`**: `SimulatorCanvas.tsx` (montagem da cena no navegador)
- **`server/`**: `scene-renderer.ts` (headless WebGL), `sensors.ts` (raycasting de proximidade), `index.ts` (API REST)
- **`tests/`**: `sensors.test.ts` (unitarios), `api.test.ts` (integracao)

## Arquivos Impactados

### Novos
- `3.controlador/lbot-simulator-web/shared/arena-objects.ts` - Configuracao centralizada dos objetos e paredes fisicas
- `3.controlador/lbot-simulator-web/tests/arena-objects.test.ts` - Testes unitarios para AABB e validacao de posicoes

### Alterados
- `3.controlador/lbot-simulator-web/src/components/SimulatorCanvas.tsx` - Adicionar objetos a cena Three.js do navegador
- `3.controlador/lbot-simulator-web/src/simulator/engine.ts` - Adicionar corpos fisicos dos objetos e paredes no cannon-es
- `3.controlador/lbot-simulator-web/server/scene-renderer.ts` - Corrigir escala da arena para 400x400; adicionar objetos na cena headless
- `3.controlador/lbot-simulator-web/server/sensors.ts` - Adicionar deteccao de objetos via AABB no raycasting
- `3.controlador/lbot-simulator-web/tests/sensors.test.ts` - Adicionar testes para sensores detectando objetos
- `3.controlador/lbot-simulator-web/tests/api.test.ts` - Adicionar teste de integracao para cena headless conter objetos

## Decisoes Tecnicas

| Decisao | Opcao escolhida | Justificativa |
|---------|-----------------|---------------|
| Configuracao dos objetos | `shared/arena-objects.ts` | Unica fonte de verdade usada por frontend, backend e fisica. Evita duplicacao e inconsistencias. |
| Fisica dos cones | Box AABB | cannon-es nao tem forma Cone nativa. Box AABB e mais simples, consistente com raycasting dos sensores, e suficiente para o simulador. |
| Geometria dos sensores | AABB para todos os tipos | Codigo uniforme de interseccao raio-AABB. Mais simples de manter. Menos preciso para esferas mas aceitavel. |
| Escala da arena headless | Corrigir para 400x400 | O frontend usa arena 400x400. O headless usava 800x800, gerando imagens com escala diferente. Correcao garante consistencia visual. |
| Paredes fisicas | Adicionar nesta tarefa | O mundo cannon-es atual nao tem paredes fisicas (robô atravessa). Adicionar objetos fisicos sem paredes seria inconsistente. Baixo custo: 4 bodies estaticos. |
| Testes headless | Estrutura da cena, nao pixels | Testar que meshes dos objetos existem na cena e mais robusto que verificar pixels especificos em imagem base64. |
| Numero de objetos | 6 | Variedade suficiente para testar cubos, esferas e cones, sem impactar performance. |

## Dependencias entre Fases

- **Fase 01 -> Fase 02**: A configuracao centralizada (`shared/arena-objects.ts`) deve existir antes de ser importada no frontend e backend.
- **Fase 02 -> Fase 03**: A cena headless requer os mesmos objetos definidos na fase do frontend. A logica de sensores depende da AABB definida na fase 01.
- **Fase 03 -> Fase 04**: A validacao final requer que frontend, fisica, headless e sensores estejam implementados.

## Mapa de Fases

| Fase | Descricao | Modulo Principal |
|------|-----------|------------------|
| 01 | Modelagem e Configuracao: Criar `shared/arena-objects.ts` com definicoes dos 6 objetos, AABB e paredes fisicas | `shared/` |
| 02 | Frontend (Three.js + Cannon-es): Adicionar objetos na cena do navegador, corpos fisicos no `engine.ts`, paredes fisicas | `src/` |
| 03 | Servidor (Headless + Sensores): Corrigir escala headless, adicionar objetos na cena headless, atualizar sensores com AABB, testes | `server/`, `tests/` |
| 04 | Integracao e Validacao: Rodar testes completos, type checking, verificar consistencia e cenarios de aceite | Raiz |

## Notas de Implementacao

### Posicoes dos Objetos (pre-definidas)
```
(-150, -150): Cubo vermelho   (15x15x15)
(150, -100):  Esfera azul     (raio 10)
(-100, 150):  Cubo amarelo    (15x15x15)
(180, 180):   Cone laranja    (raio base 10, altura 15) -> AABB 20x20x20
(0, -180):    Esfera verde    (raio 10)
(-180, 0):    Cubo roxo       (15x15x15)
```

### AABB dos Objetos
- **Cubo 15x15x15**: AABB `(±7.5, ±7.5, ±7.5)` relativa ao centro
- **Esfera raio 10**: AABB `(±10, ±10, ±10)` relativa ao centro
- **Cone (base 10, altura 15)**: AABB `(±10, ±7.5, ±10)` relativa ao centro (aproximacao Box)

### Paredes Fisicas (cannon-es)
```
CANNON.Box(new CANNON.Vec3(204, 7.5, 4))  // Norte e Sul (largura 408, altura 15, espessura 8)
CANNON.Box(new CANNON.Vec3(4, 7.5, 200))   // Leste e Oeste (espessura 8, altura 15, profundidade 400)
```

### Escala da Arena Headless
- **Atual**: `ARENA_WORLD = 800`, `HALF_ARENA = 400`, paredes em `±204`
- **Novo**: `ARENA_WORLD = 400`, `HALF_ARENA = 200`, paredes em `±204` -> `±104` (ajustar para alinhar com frontend: parede em `±200` no mundo, mas geometria 408x8 -> usar `arenaSize=400`, parede grossa 8, posicoes `±204` no Three.js headless)

Observacao: O frontend `arena.ts` usa `arenaSize=400` com paredes posicionadas em `±204` (400/2 + 8/2). O headless atual usava `ARENA_WORLD=800` com paredes em `±204`. Para alinhar, o headless deve usar `arenaSize=400` e posicoes de parede `±204`, mantendo as mesmas dimensoes de geometria (408x8 ou 8x400).
