# Fase 04: Redesign dos Niveis 4-5

## Status: PENDENTE

## Objetivo

Redefinir os Niveis 4 e 5 no `level-config.model.ts` com novos layouts, obstaculos rotacionados, combinacao de mecanicas e corredores estreitos.

## Pre-requisitos

- Fase 03 concluida (Niveis 1-3 definidos)

## Tarefas

- [ ] Tarefa 1: Redesenhar Nivel 4 - Floresta Misteriosa
  - Arquivo: `lbot-datagen-frontend/src/app/models/level-config.model.ts`
  - O que fazer: Substituir o nivel 4 atual por:
    - Nome: `'Floresta Misteriosa'`
    - Theme: ground `#228B22`, wall `#8B4513`, obstacle `#006400`, sky `#98FB98`
    - Start: `{ x: -150, z: -150 }`, Goal: `{ x: 150, z: 150 }` (distancia ~424)
    - Obstaculos: 9-11 obstaculos do tipo `tree` (tronco+copa) e `barrier`
    - Layout: obstaculos posicionados em angulos (rotationY variados: 15, 30, 45, 60, 75 graus), formando caminho em zig-zag
    - Os angulos devem forcar o jogador a fazer varias rotacoes (R90L/R90R)
    - Dificuldade: 12-16 comandos LBML

- [ ] Tarefa 2: Redesenhar Nivel 5 - Complexo Industrial
  - Arquivo: `lbot-datagen-frontend/src/app/models/level-config.model.ts`
  - O que fazer: Substituir o nivel 5 atual por:
    - Nome: `'Complexo Industrial'`
    - Theme: ground `#2F4F4F`, wall `#1C1C1C`, obstacle `#FF6600`, sky `#404040`
    - Start: `{ x: -150, z: -150 }`, Goal: `{ x: 150, z: 150 }` (distancia ~424)
    - Obstaculos: 11-13 obstaculos combinando TODAS as mecanicas:
      - `wall` (paredes industriais formando corredores estreitos)
      - `ramp` (1 rampa industrial)
      - `tree` ou `barrier` (obstaculos rotacionados em angulos)
      - `industrial` (estruturas complexas: colunas + vigas + tanques)
      - `stack` (pilhas de caixas)
    - Layout: corredores mais estreitos (paredes proximas), combinacao de angulos e rampas
    - Dificuldade: 16-20 comandos LBML

- [ ] Tarefa 3: Verificar compilacao e posicoes
  - Verificar que todas as posicoes A/B estao dentro da arena
  - Verificar que nenhum obstaculo colide com A ou B
  - Verificar que os tipos usados existem na ObstacleMeshFactory
  - Verificar que rotationY esta em graus (conforme o model)

## Arquivos Referencia

- `lbot-datagen-frontend/src/app/models/level-config.model.ts` - Configuracao atual dos niveis
- `lbot-datagen-frontend/src/app/services/obstacle-mesh.factory.ts` - Tipos disponiveis
- `lbot-datagen-frontend/src/app/services/arena-builder.service.ts` - Como rotationY e aplicada (conversao para radianos)

## Criterios de Aceite

- [ ] CA01: Nivel 4 tem 9-11 obstaculos com angulos variados (zig-zag)
- [ ] CA02: Nivel 5 tem 11-13 obstaculos combinando paredes + rampas + rotacionados + corredores estreitos
- [ ] CA03: Distancia A->B ~300-424 unidades em ambos
- [ ] CA04: Posicoes A e B nao colidem com obstaculos
- [ ] CA05: Paleta de cores distinta para cada nivel
- [ ] CA06: Compilacao passa sem erros

## Testes Esperados

- `test_level4_rotated_obstacles` - Verificar que nivel 4 tem obstaculos com rotationY != 0
- `test_level5_combined_mechanics` - Verificar que nivel 5 contem rampas, paredes e rotacionados
- `test_level5_narrow_corridors` - Verificar que ha corredores estreitos (paredes proximas)

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
