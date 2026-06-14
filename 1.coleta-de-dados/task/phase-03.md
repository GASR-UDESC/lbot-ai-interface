# Fase 03: Redesign dos Niveis 1-3

## Status: PENDENTE

## Objetivo

Redefinir os Niveis 1, 2 e 3 no `level-config.model.ts` com novos layouts, obstaculos compostos, paleta de cores, posicoes A/B e progressao de dificuldade.

## Pre-requisitos

- Fase 01 concluida (ObstacleMeshFactory pronta)
- Fase 02 concluida (Sistema de temas dinamicos pronto)

## Tarefas

- [ ] Tarefa 1: Redesenhar Nivel 1 - Campo de Treino
  - Arquivo: `lbot-datagen-frontend/src/app/models/level-config.model.ts`
  - O que fazer: Substituir o nivel 1 atual por:
    - Nome: `'Campo de Treino'`
    - Theme: ground `#7C9A5E`, wall `#8B7355`, obstacle `#A67B5B`, sky `#87CEEB`
    - Start: `{ x: -150, z: -150 }`, Goal: `{ x: 150, z: 150 }` (distancia ~424)
    - Obstaculos: 3-4 obstaculos do tipo `crate` (pilhas de caixas) posicionados no centro, deixando caminho quase reto
    - Layout: caminho principal quase diagonal, com pequenos desvios
    - Dificuldade: 3-5 comandos LBML (ex: D200F, D50F, D200F)

- [ ] Tarefa 2: Redesenhar Nivel 2 - Escritorio Central
  - Arquivo: `lbot-datagen-frontend/src/app/models/level-config.model.ts`
  - O que fazer: Substituir o nivel 2 atual por:
    - Nome: `'Escritorio Central'`
    - Theme: ground `#D3D3D3`, wall `#808080`, obstacle `#A9A9A9`, sky `#B0C4DE`
    - Start: `{ x: -150, z: -150 }`, Goal: `{ x: 150, z: 150 }` (distancia ~424)
    - Obstaculos: 5-7 obstaculos do tipo `wall` (paredes com pilastras) formando divisoes
    - Layout: paredes que bloqueiam caminho direto, forcando desvios por corredores
    - Dificuldade: 5-8 comandos LBML

- [ ] Tarefa 3: Redesenhar Nivel 3 - Cidade em Obras
  - Arquivo: `lbot-datagen-frontend/src/app/models/level-config.model.ts`
  - O que fazer: Substituir o nivel 3 atual por:
    - Nome: `'Cidade em Obras'`
    - Theme: ground `#696969`, wall `#2F4F4F`, obstacle `#708090`, sky `#778899`
    - Start: `{ x: -150, z: -150 }`, Goal: `{ x: 150, z: 150 }` (distancia ~424)
    - Obstaculos: 7-9 obstaculos: `ramp` (1-2 rampas) + `barrier` (barreiras) + `wall`
    - Layout: rampa(s) no caminho principal que o robo precisa subir. Barreiras laterais.
    - Dificuldade: 8-12 comandos LBML
    - Garantir que a rampa esteja posicionada de forma que o robo possa subir fisicamente

- [ ] Tarefa 4: Verificar compilacao e posicoes
  - Verificar que todas as posicoes A/B estao dentro da arena (-200 a 200)
  - Verificar que nenhum obstaculo colide com A ou B
  - Verificar que os tipos de obstaculos usados existem na ObstacleMeshFactory

## Arquivos Referencia

- `lbot-datagen-frontend/src/app/models/level-config.model.ts` - Configuracao atual dos niveis
- `lbot-datagen-frontend/src/app/services/obstacle-mesh.factory.ts` - Tipos disponiveis e parametros esperados
- `lbot-datagen-frontend/src/app/components/robo-simulator/robo-simulator.ts` - Como o robo inicia (rotacao 0, olhando +Z)
- `lbot-datagen-frontend/src/app/services/arena-builder.service.ts` - Como os obstaculos sao posicionados

## Criterios de Aceite

- [ ] CA01: Nivel 1 tem 3-4 obstaculos do tipo crate, caminho quase reto
- [ ] CA02: Nivel 2 tem 5-7 obstaculos do tipo wall, paredes bloqueiam caminho direto
- [ ] CA03: Nivel 3 tem 7-9 obstaculos incluindo 1-2 rampas
- [ ] CA04: Distancia A->B ~300-424 unidades em todos os niveis
- [ ] CA05: Posicoes A e B nao colidem com obstaculos
- [ ] CA06: Cada nivel tem paleta de cores distinta
- [ ] CA07: Compilacao passa sem erros

## Testes Esperados

- `test_level1_completable` - Verificar que existe caminho visual de A a B
- `test_level2_walls_block` - Verificar que paredes bloqueiam caminho direto
- `test_level3_has_ramps` - Verificar que nivel 3 contem rampas

## Comandos pos-fase

- `cd lbot-datagen/lbot-datagen-frontend && npm run build` (verificar compilacao)
- `cd lbot-datagen/lbot-datagen-frontend && npm start` (subir app para verificar visualmente)

## Registro de Execucao

- Data:
- Arquivos criados:
- Arquivos alterados:
- Testes executados:
- Resultado:
- Pendencias:
