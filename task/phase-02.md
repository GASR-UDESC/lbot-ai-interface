# Fase 02: Sistema de Niveis - Configuracao & Refatoracao do ArenaBuilder

## Status: PENDENTE

## Objetivo

Criar o sistema de configuracao dos 5 niveis (LevelConfig) e refatorar o ArenaBuilderService para aceitar configuracoes de nivel dinamicas. Ao final, a arena pode ser renderizada com qualquer um dos 5 niveis, com obstaculos reposicionados e temas visuais distintos.

## Pre-requisitos

- Fase 01 concluida (rotas funcionando)

## Tarefas

- [ ] Tarefa 1: Criar interface LevelConfig e modelo de dados
  - Arquivo: `lbot-datagen/lbot-datagen-frontend/src/app/models/level-config.model.ts`
  - O que fazer: Definir interface LevelConfig com campos: id (1-5), name (string), theme (objeto com cores: groundColor, wallColor, obstacleColor, skyColor), obstacles (array de ObstacleConfig com x, z, width, height, depth, type), startPoint ({x, z}), goalPoint ({x, z}). Definir tipos auxiliares: ObstacleType = 'wall' | 'crate' | 'ramp'. ThemeConfig com campos de cor.

- [ ] Tarefa 2: Definir os 5 niveis com layouts e temas
  - Arquivo: `lbot-datagen/lbot-datagen-frontend/src/app/models/level-config.model.ts` (mesmo arquivo)
  - O que fazer: Criar constante `LEVEL_CONFIGS: LevelConfig[]` com os 5 niveis:
    - Nivel 1 (Armazem): cores madeira/metal (#8B4513, #A0522D), 4-5 crates simples, caminho relativamente direto
    - Nivel 2 (Escritorio): cores neutras (#696969, #808080), 6-7 obstaculos retangulares (mesas/estantes), mais bloqueios
    - Nivel 3 (Cidade): cores concreto/asfalto (#4A4A4A, #333333), paredes altas, caminhos estreitos
    - Nivel 4 (Floresta): cores verdes/terra (#228B22, #8B4513), obstaculos posicionados de forma irregular/sinuosa
    - Nivel 5 (Fabrica): cores metalicas escuras (#2F4F4F, #1C1C1C), combinacao de todos os tipos, caminho complexo
    - Pontos A={x:-150, z:-150} e B={x:150, z:150} FIXOS em todos os niveis (distancia ~424 unidades)

- [ ] Tarefa 3: Refatorar ArenaBuilderService para aceitar LevelConfig
  - Arquivo: `lbot-datagen/lbot-datagen-frontend/src/app/services/arena-builder.service.ts`
  - O que fazer: 
    - Novo metodo `createObstaclesFromConfig(scene, world, config: LevelConfig): ObstacleData[]` que cria obstaculos baseado no config
    - Novo metodo `createThemedGround(theme: ThemeConfig): THREE.Mesh` que cria chao com cor do tema
    - Novo metodo `createThemedWalls(scene, theme: ThemeConfig): THREE.Mesh[]` que cria paredes com cor do tema
    - Manter metodos antigos para backward compatibility (modo controle ainda usa)
    - O metodo recebe as cores via ThemeConfig e aplica MeshStandardMaterial com as cores do tema

- [ ] Tarefa 4: Criar LevelConfigService
  - Arquivo: `lbot-datagen/lbot-datagen-frontend/src/app/services/level-config.service.ts`
  - O que fazer: Service simples que expoe: `getLevel(id: number): LevelConfig`, `getAllLevels(): LevelConfig[]`, `getTotalLevels(): number`. Importa LEVEL_CONFIGS do model.

- [ ] Tarefa 5: Adaptar RoboSimulatorComponent para aceitar LevelConfig via Input
  - Arquivo: `lbot-datagen/lbot-datagen-frontend/src/app/components/robo-simulator/robo-simulator.ts`
  - O que fazer:
    - Adicionar `@Input() levelConfig?: LevelConfig`
    - No ngOnChanges: se levelConfig mudar, destruir obstaculos antigos e recriar com novo config
    - Criar metodo `loadLevel(config: LevelConfig)` que: limpa obstaculos, cria novos com tema, posiciona robot no startPoint
    - Se levelConfig nao fornecido (modo controle), usar comportamento atual (obstaculos hardcoded)
    - Remover geracao aleatoria de A/B quando levelConfig esta presente (usar fixo do config)
    - Manter startPoint/goalPoint do config

## Arquivos Referencia

- `lbot-datagen/lbot-datagen-frontend/src/app/services/arena-builder.service.ts` - Implementacao atual de obstaculos
- `lbot-datagen/lbot-datagen-frontend/src/app/components/robo-simulator/robo-simulator.ts` - Como o simulator usa o arena builder
- `lbot-datagen/lbot-datagen-frontend/src/app/models/robot-state.model.ts` - Pattern de models no projeto

## Criterios de Aceite

- [ ] CA01: Arena renderiza com tema do nivel 1 (cores de madeira/metal)
  - Cenario: Given levelConfig = nivel 1 / When arena carrega / Then obstaculos e chao tem cores de armazem
- [ ] CA02: Arena renderiza com tema do nivel 3 (cores de cidade)
  - Cenario: Given levelConfig = nivel 3 / When arena carrega / Then obstaculos tem cores de concreto, paredes altas
- [ ] CA03: Obstaculos mudam de posicao entre niveis
  - Cenario: Given nivel 1 carregado / When muda para nivel 2 / Then obstaculos estao em posicoes diferentes
- [ ] CA04: Pontos A e B sao fixos e iguais em todos niveis
  - Cenario: Given qualquer nivel / When verifica posicao de A e B / Then A=(-150,-150) e B=(150,150)
- [ ] CA05: Modo controle continua funcionando com obstaculos hardcoded
  - Cenario: Given pagina /controls / When simulator carrega sem levelConfig / Then usa obstaculos originais

## Testes Esperados

- Nenhum teste automatizado (decisao do projeto)

## Comandos pos-fase

- `cd lbot-datagen/lbot-datagen-frontend && ng serve`
- Verificar: acessar /controls e confirmar que funciona como antes
- Verificar: temporariamente passar um levelConfig para o simulator e ver visual diferente

## Registro de Execucao

- Data:
- Arquivos criados:
- Arquivos alterados:
- Testes executados:
- Resultado:
- Pendencias:
