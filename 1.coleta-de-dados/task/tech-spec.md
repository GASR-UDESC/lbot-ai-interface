# Plano Tecnico: Redesign dos Niveis do Lbot Arena

## Visao Geral

A implementacao sera feita no frontend Angular `lbot-datagen-frontend` (path: `1.coleta-de-dados/lbot-datagen/lbot-datagen-frontend/`). O redesign envolve:

1. Renomear os 5 niveis para nomenclatura numerica
2. Redesenhar os layouts de obstaculos (labirinto progressivo com rampas obrigatorias)
3. Bloquear cantos da arena com paredes internas
4. Uniformizar as paredes externas (remover detalhes tematicos)
5. Atualizar todos os textos exibidos na UI

A abordagem escolhida e manter o formato `LevelConfig` existente e reaproveitar todos os servicos e componentes, alterando apenas os dados e textos.

## Modulos Envolvidos

- **models/level-config.model.ts**: Fonte da verdade dos niveis. Todos os nomes, cores e obstaculos serao alterados aqui.
- **pages/game/**: HUD, tela de transicao, tela de vitoria. Apenas textos/templates.
- **pages/menu/**: Subtitulo do menu.
- **components/victory-screen/**: Remover coluna redundante "Nome".
- **components/level-transition/**: Texto ja usa `levelName`, sera automaticamente atualizado.
- **components/lbot-chat/**: Usa `currentLevelName`, sera automaticamente atualizado.
- **services/arena-builder.service.ts**: `createThemedWalls` sera simplificada.
- **services/obstacle-mesh.factory.ts**: `createRamp` sera corrigida para respeitar `rampAngle` do config.
- **services/physics.service.ts**: Nao sera alterada (decisao do usuario: confiar na fisica atual).
- **components/robo-simulator/**: Nao sera alterada (usa `LevelConfig` genericamente).

## Arquivos Impactados

### Novos
- Nenhum.

### Alterados
- `1.coleta-de-dados/lbot-datagen/lbot-datagen-frontend/src/app/models/level-config.model.ts`
  - Renomear `name` dos 5 niveis para "Nivel 1".."Nivel 5"
  - Redesenhar `obstacles` de todos os niveis
  - Manter `theme` cores conforme especificacao
- `1.coleta-de-dados/lbot-datagen/lbot-datagen-frontend/src/app/pages/menu/menu.page.html`
  - Atualizar subtitulo do botao "Jogar Desafios"
- `1.coleta-de-dados/lbot-datagen/lbot-datagen-frontend/src/app/components/victory-screen/victory-screen.html`
  - Remover coluna "Nome" da tabela de tempos
- `1.coleta-de-dados/lbot-datagen/lbot-datagen-frontend/src/app/services/arena-builder.service.ts`
  - Simplificar `createThemedWalls`: remover detalhes tematicos (planks, troncos, rebites, etc.)
  - Usar apenas cor solida `wallColor`
- `1.coleta-de-dados/lbot-datagen/lbot-datagen-frontend/src/app/services/obstacle-mesh.factory.ts`
  - Corrigir `createRamp` para aceitar e usar `rampAngle` passado por parametro
  - Alinhar visual mesh e physics body

## Decisoes Tecnicas

| Decisao | Opcao escolhida | Justificativa |
|---------|-----------------|---------------|
| Angulo da rampa | Usar `rampAngle` do config na factory | O usuario confirmou. Alinha visual mesh e body fisico. Niveis 3-5 usarao angulo < 15° (~0.26 rad) |
| StabilizeRobot | Nao alterar | O usuario preferiu confiar na fisica atual. Testar rampas suaves |
| Parametros do robo | Nao alterar | Mass=100, friction=0.9, velocidade=30 mantidos. Testar se sobe rampas <15° |
| Paredes externas | Cor solida wallColor sem detalhes | Remove todas as variacoes tematicas (planks, concreto, troncos, rebites) |
| Texturas do chao | Manter tematicas | A RF05 explicitamente preserva texturas/cores tematicas do chao e obstaculos |
| Coluna "Nome" no victory | Remover | Redundante com nomes "Nivel 1", "Nivel 2"... |
| Texto do menu | "5 niveis com dificuldade progressiva" | Removida a palavra "temas" |
| Texto level-transition | Manter "Completo!" | O usuario confirmou que "Nivel 1 Completo!" esta aceitavel |

## Dependencias entre Fases

- Fase 1 (UI/Textos) -> Fase 2 (Level Design): Fase 1 deve ser concluida primeiro para garantir que os nomes e textos estejam corretos antes de testar o gameplay.
- Fase 2 (Level Design) -> Fase 3 (Paredes e Polimento): Fase 2 precisa estar concluida para garantir que os niveis estejam jogaveis antes de polir as paredes externas.

## Mapa de Fases

| Fase | Descricao | Arquivos principais |
|------|-----------|---------------------|
| 01 | Renomeacao e textos da UI | level-config.model.ts, menu.page.html, victory-screen.html |
| 02 | Redesign dos layouts dos niveis | level-config.model.ts (obstacles), obstacle-mesh.factory.ts |
| 03 | Paredes externas uniformes e polimento | arena-builder.service.ts, build & test |
