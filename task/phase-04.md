# Fase 04: LevelConfig + Arena Shapes Variaveis

## Status: PENDENTE

## Objetivo

Expandir a interface `LevelConfig` para suportar arenas com formatos variaveis (quadrada, retangular, circular) e tamanhos diferentes. Atualizar arena-builder e physics para criar paredes/colisao de acordo com a forma configurada.

## Pre-requisitos

- Nenhum obrigatorio (pode rodar em paralelo com Fases 02/03)
- Recomendado ter Fase 01 concluida para consistencia

## Tarefas

- [ ] Tarefa 1: Expandir interface LevelConfig
  - Arquivo: `lbot-datagen/lbot-datagen-frontend/src/app/models/level-config.model.ts`
  - O que fazer:
    - Criar tipo `ArenaShape = 'square' | 'rectangle' | 'circle'`
    - Adicionar campos opcionais a `LevelConfig`:
      ```typescript
      arenaShape?: ArenaShape;      // default: 'square'
      arenaSize?: { width: number; height: number }; // default: { width: 400, height: 400 }
      ```
    - Manter retrocompatibilidade: se nao especificado, arena eh quadrada 400x400
    - Remover constantes fixas `START_POINT` e `GOAL_POINT` (ja sao por nivel via `startPoint`/`goalPoint`)

- [ ] Tarefa 2: Atualizar arena-builder para arenas retangulares
  - Arquivo: `lbot-datagen/lbot-datagen-frontend/src/app/services/arena-builder.service.ts`
  - O que fazer:
    - Atualizar `createArenaWalls()` para aceitar parametros de tamanho (width, height)
    - Atualizar `createThemedWalls()` para aceitar arenaSize
    - Quando `arenaShape === 'rectangle'`: criar 4 paredes com width e height diferentes
    - Atualizar `createGround()` e `createThemedGround()` para aceitar tamanho variavel

- [ ] Tarefa 3: Implementar arena circular (poligono de muitos lados)
  - Arquivo: `lbot-datagen/lbot-datagen-frontend/src/app/services/arena-builder.service.ts`
  - O que fazer:
    - Criar metodo `createCircularWalls(scene, radius, theme?)`:
      - Gerar N segmentos (N=32) de parede reta dispostos em circulo
      - Cada segmento: comprimento = `2 * radius * sin(PI/N)`, posicionado a `radius * cos(angle)`, `radius * sin(angle)`
      - Rotacao de cada segmento: tangente ao circulo naquele ponto
    - Retornar array de THREE.Mesh (mesma interface que createArenaWalls)
    - Criar metodo `createCircularWallsBodies(world, radius)` ou integrar na logica existente

- [ ] Tarefa 4: Atualizar physics.service para arenas variaveis
  - Arquivo: `lbot-datagen/lbot-datagen-frontend/src/app/services/physics.service.ts`
  - O que fazer:
    - Refatorar `createArenaWallsBodies()` para aceitar `arenaShape` e `arenaSize`
    - Para arena retangular: ajustar posicoes das 4 paredes com width/height
    - Para arena circular: criar N corpos Box (segmentos do poligono), mesma logica da arena-builder
    - Atualizar `isValidPosition()`:
      - Se arena circular: verificar distancia ao centro < radius (ao inves de checar limites X/Z)
      - Se retangular: ajustar ARENA_LIMIT para width/2 e height/2 separadamente
    - Atualizar `ARENA_LIMIT` para ser dinamico (receber config ou ter setter)

- [ ] Tarefa 5: Atualizar robo-simulator para passar arena config
  - Arquivo: `lbot-datagen/lbot-datagen-frontend/src/app/components/robo-simulator/robo-simulator.ts`
  - O que fazer:
    - Em `initializeSimulator()` e `loadLevel()`:
      - Passar `arenaShape` e `arenaSize` para os metodos de criacao de paredes
      - Ajustar `createGameMarkers()` se arena for muito diferente
    - Garantir que ao trocar de nivel, as paredes antigas sao removidas e novas criadas

## Arquivos Referencia

- `lbot-datagen/lbot-datagen-frontend/src/app/services/arena-builder.service.ts` - Metodos atuais de criacao de arena
- `lbot-datagen/lbot-datagen-frontend/src/app/services/physics.service.ts` - createArenaWallsBodies() e isValidPosition()
- `lbot-datagen/lbot-datagen-frontend/src/app/models/level-config.model.ts` - Interface atual LevelConfig

## Criterios de Aceite

- [ ] CA11: Arena quadrada, retangular e circular renderizam corretamente com colisao funcional
- [ ] Arena circular: robo nao atravessa paredes em nenhuma direcao
- [ ] Arena retangular: paredes posicionadas corretamente com largura != altura
- [ ] Retrocompatibilidade: niveis sem arenaShape definido usam quadrada 400x400

## Testes Esperados

- Validacao manual: alterar temporariamente um level para circular e verificar visualmente

## Comandos pos-fase

```bash
cd lbot-datagen/lbot-datagen-frontend && ng build
```

## Registro de Execucao

- Data:
- Arquivos criados:
- Arquivos alterados:
- Testes executados:
- Resultado:
- Pendencias:
