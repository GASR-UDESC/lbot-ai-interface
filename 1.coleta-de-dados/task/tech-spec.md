# Plano Tecnico: Redesign dos Niveis do Lbot Arena

## Visao Geral

A abordagem escolhida e modularizar a geracao de meshes visuais dos obstaculos em uma factory dedicada (`ObstacleMeshFactory`), expandir os `ObstacleType` para suportar novos modelos compostos (pilha de caixas, arvores, barreiras, estruturas industriais), redesenhar os 5 niveis com progressao de dificuldade clara, aplicar texturas procedurais via `CanvasTexture`, tornar o céu/sky dinamico por nivel, ajustar a fisica para rampas, e remover completamente o botao "Novo Desafio".

## Modulos Envolvidos

- **models/level-config.model.ts**: Redefinicao dos 5 niveis com novos layouts, obstaculos, cores, posicoes A/B e novos tipos de obstaculos.
- **services/obstacle-mesh.factory.ts**: Novo servico dedicado para gerar meshes compostas (THREE.Group) para cada tipo de obstaculo.
- **services/arena-builder.service.ts**: Integracao com a factory, geracao de texturas CanvasTexture para chao, paredes tematicas.
- **services/three-scene.service.ts**: Suporte a skyColor dinamico (background + fog) por nivel.
- **services/physics.service.ts**: Ajuste da estabilizacao do robo para permitir subida em rampas.
- **components/robo-simulator/robo-simulator.ts**: Remocao do botao "Novo Desafio" e da logica `generateNewLevel()`.
- **services/level-validator.service.ts**: Novo servico com pathfinding A* para validar completabilidade dos niveis.

## Arquivos Impactados

### Novos
- `lbot-datagen-frontend/src/app/services/obstacle-mesh.factory.ts` - Factory de meshes compostas para cada tipo de obstaculo
- `lbot-datagen-frontend/src/app/services/level-validator.service.ts` - Pathfinding A* para validar niveis

### Alterados
- `lbot-datagen-frontend/src/app/models/level-config.model.ts` - Novos niveis, novos tipos, novas cores, posicoes A/B variadas
- `lbot-datagen-frontend/src/app/services/arena-builder.service.ts` - Usar factory, texturas CanvasTexture, paredes tematicas
- `lbot-datagen-frontend/src/app/services/three-scene.service.ts` - Sky color dinamico
- `lbot-datagen-frontend/src/app/services/physics.service.ts` - Fisica de rampas
- `lbot-datagen-frontend/src/app/components/robo-simulator/robo-simulator.ts` - Remover botao e logica
- `lbot-datagen-frontend/src/app/pages/controls/controls.page.ts` - Garantir A/B fixos (ja esta, mas verificar)

## Decisoes Tecnicas

| Decisao | Opcao escolhida | Justificativa |
|---------|-----------------|---------------|
| Arquitetura de mesh composta | ObstacleMeshFactory separado | Modular, testavel, permite reutilizacao. Cada tipo tem uma funcao dedicada. |
| Texturas procedurais | CanvasTexture para chao e detalhes | Permitido pelo RNF, melhora visual sem assets externos. |
| Tipos de obstaculos | Expandir (tree, stack, barrier, industrial) | Permite designs mais ricos e tematicos. |
| Nomes dos niveis | Campo de Treino, Escritorio Central, Cidade em Obras, Floresta Misteriosa, Complexo Industrial | Aprovados pelo usuario. |
| Fisica de rampas | Ajustar estabilizacao | Robo precisa subir fisicamente. Detectar superficie inclinada para nao forcar para baixo. |
| Paredes da arena | Tematicas por nivel | Seguem theme.wallColor e detalhes visuais tematicos. |
| Sky/Fog | Dinamico por nivel | Usa theme.skyColor do LevelConfig. |
| Validacao | Pathfinding A* automatico | Garante que todos os niveis tem caminho valido antes de entregar. |
| Testes | Testes manuais + pathfinder | Nao criar testes unitarios automatizados (preferencia do usuario). Validar via playtest e A*. |

## Dependencias entre Fases

- Fase 1 -> Fase 2 (precisa da factory pronta para aplicar texturas)
- Fase 1 -> Fase 3 (precisa dos novos tipos de obstaculos definidos)
- Fase 2 -> Fase 3 (precisa do sistema de temas pronto)
- Fase 3 -> Fase 4 (precisa dos niveis 1-3 definidos para manter padrao)
- Fase 4 -> Fase 5 (precisa dos niveis 4-5 definidos para validar)
- Fase 5 -> Fase 6 (precisa da fisica ajustada para garantir jogabilidade)

## Mapa de Fases

| Fase | Descricao | Modulo |
|------|-----------|--------|
| 01 | Criar ObstacleMeshFactory e novos tipos de obstaculos | obstacle-mesh.factory.ts, level-config.model.ts |
| 02 | Implementar sistema de temas: sky dinamico, texturas CanvasTexture, paredes tematicas | three-scene.service.ts, arena-builder.service.ts |
| 03 | Redesenhar Niveis 1-3 (Campo de Treino, Escritorio Central, Cidade em Obras) | level-config.model.ts |
| 04 | Redesenhar Niveis 4-5 (Floresta Misteriosa, Complexo Industrial) | level-config.model.ts |
| 05 | Ajustar fisica de rampas e implementar pathfinder A* | physics.service.ts, level-validator.service.ts |
| 06 | Remover "Novo Desafio", ajustar A/B fixos, playtest final | robo-simulator.ts, controls.page.ts |

## Paleta de Cores Proposta (hex)

| Nivel | groundColor | wallColor | obstacleColor | skyColor |
|-------|-------------|-----------|---------------|----------|
| 1 - Campo de Treino | `#7C9A5E` | `#8B7355` | `#A67B5B` | `#87CEEB` |
| 2 - Escritorio Central | `#D3D3D3` | `#808080` | `#A9A9A9` | `#B0C4DE` |
| 3 - Cidade em Obras | `#696969` | `#2F4F4F` | `#708090` | `#778899` |
| 4 - Floresta Misteriosa | `#228B22` | `#8B4513` | `#006400` | `#98FB98` |
| 5 - Complexo Industrial | `#2F4F4F` | `#1C1C1C` | `#FF6600` | `#404040` |

## Tipos de Obstaculos Expandidos

| Tipo | Modelo Composto | Descricao |
|------|-----------------|-----------|
| `crate` | Pilha de 2-3 caixas de tamanhos variados | Usado no Nivel 1 |
| `wall` | Parede com pilastras ou paineis | Usado no Nivel 2 |
| `ramp` | Rampa inclinada com laterais (barreiras) e grade | Usado no Nivel 3 |
| `tree` | Tronco (cilindro) + copa (esfera ou cone) | Usado no Nivel 4 |
| `barrier` | Barreira decorativa (cilindros + caixas) | Usado em varios |
| `stack` | Pilha de caixas industrial | Usado no Nivel 5 |
| `industrial` | Colunas (cilindros) + vigas (caixas) + tanques | Usado no Nivel 5 |

## Comandos de Build/Teste

- `npm run build` (verificar compilacao)
- `npm run test` (rodar testes existentes)
- Validacao manual: abrir o jogo, testar cada nivel, verificar caminho A->B

## Notas de Implementacao

1. **ObstacleMeshFactory**: Cada funcao retorna `THREE.Group`. A fisica (CANNON.Body) continua sendo uma Box simples aproximada. A factory NAO cria corpos de fisica, apenas meshes visuais.
2. **CanvasTexture**: Usar para gerar padroes no chao (ex: grama, concreto, asfalto). Criar funcoes helper no ArenaBuilderService.
3. **Pathfinder A**: Grid-based A* na arena 400x400. Considerar obstaculos como celulas bloqueadas. Verificar se existe caminho de A a B. Contar numero aproximado de comandos LBML (D + R) necessarios.
4. **Fisica de rampas**: Em `stabilizeRobot()`, detectar se o robo esta sobre uma superficie inclinada (usar raycast ou verificar posicao Y). Se estiver em rampa, nao aplicar a forca para baixo (`velocity.y -= 2`).
5. **Sky dinamico**: Adicionar metodo `updateSkyColor(skyColor: string)` no ThreeSceneService que atualiza `scene.background` e `scene.fog.color`. Chamar em `loadLevel()` do RoboSimulatorComponent.
6. **Novo Desafio**: Remover completamente do template (linha 55-57 do robo-simulator.ts) e da classe. O metodo `generateNewLevel()` pode ser deletado ou marcado como `@deprecated`. No Modo Controle, garantir que `startPoint` e `goalPoint` sejam fixos (-80, -80) e (80, 80).
