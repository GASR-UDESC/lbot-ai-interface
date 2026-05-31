# Fase 05: Redesign dos 5 Niveis

## Status: PENDENTE

## Objetivo

Redesenhar completamente os 5 niveis do jogo com progressao logica de dificuldade: niveis 1-2 resolviveis com D/R, niveis 3-4 exigindo arcos (A), nivel 5 exigindo rampas. Pontos de partida/chegada variaveis, formatos de arena diferentes, e obstaculos que forcam o uso das mecanicas de cada nivel.

## Pre-requisitos

- Fase 01 concluida (parser suporta comando A)
- Fase 04 concluida (LevelConfig suporta arenaShape e arenaSize)

## Tarefas

- [ ] Tarefa 1: Redesenhar Nivel 1 - "Armazem" (Iniciante)
  - Arquivo: `lbot-datagen/lbot-datagen-frontend/src/app/models/level-config.model.ts`
  - O que fazer:
    - Arena: quadrada, 400x400 (padrao)
    - Dificuldade: facil, resolvivel com D e R apenas
    - Obstaculos: paredes longas formando corredor em L ou Z, forcando desvios com giro
    - Posicionar obstaculos de forma que o jogador NAO pode contornar pelos cantos
    - Start e goal em posicoes que criam um caminho obrigatorio com pelo menos 2 desvios
    - Start: canto inferior esquerdo, Goal: canto superior direito (ou similar)

- [ ] Tarefa 2: Redesenhar Nivel 2 - "Escritorio" (Iniciante+)
  - Arquivo: `lbot-datagen/lbot-datagen-frontend/src/app/models/level-config.model.ts`
  - O que fazer:
    - Arena: retangular (ex: 500x300) para variar visualmente
    - Dificuldade: media-baixa, resolvivel com D e R apenas, mas mais complexo
    - Obstaculos: labirinto simples com 3-4 corredores, paredes que bloqueiam atalhos
    - Forcam 3+ giros para navegar
    - Start em uma extremidade do retangulo, goal na outra

- [ ] Tarefa 3: Redesenhar Nivel 3 - "Cidade" (Intermediario)
  - Arquivo: `lbot-datagen/lbot-datagen-frontend/src/app/models/level-config.model.ts`
  - O que fazer:
    - Arena: quadrada 450x450 (levemente maior)
    - Dificuldade: EXIGE uso de arcos (A)
    - Obstaculos: corredor curvo formado por paredes que criam um "S" ou chicane
    - Passagens que so podem ser navegadas com arcos (corredor estreito em curva)
    - Paredes internas posicionadas de forma que caminhos retilineos com D/R nao resolvem
    - Start e goal em diagonais com caminho obrigatorio passando por curvas

- [ ] Tarefa 4: Redesenhar Nivel 4 - "Floresta" (Intermediario+)
  - Arquivo: `lbot-datagen/lbot-datagen-frontend/src/app/models/level-config.model.ts`
  - O que fazer:
    - Arena: circular (raio ~200)
    - Dificuldade: EXIGE arcos mais complexos (multiplos arcos, angulos variados)
    - Obstaculos: "arvores" (crates) posicionados ao longo de um caminho que exige curvas alternadas
    - A arena circular por si so ja forca curvas nas bordas
    - Start e goal em posicoes que forcam navegacao circular
    - Caminho retilineo bloqueado por obstaculos centrais

- [ ] Tarefa 5: Redesenhar Nivel 5 - "Fabrica" (Avancado)
  - Arquivo: `lbot-datagen/lbot-datagen-frontend/src/app/models/level-config.model.ts`
  - O que fazer:
    - Arena: retangular grande (600x400)
    - Dificuldade: EXIGE rampas + curvas
    - Obstaculos: combinacao de paredes, rampas e crates
    - Pelo menos 1 rampa obrigatoria para alcancar area elevada ou cruzar obstaculo
    - Rampa como ponte: posicionada sobre um bloco de obstaculo que bloqueia o caminho no nivel do chao
    - Curvas necessarias para alinhar com a rampa
    - Start em um "dock" de carga, goal na area elevada ou alem da ponte

- [ ] Tarefa 6: Validar progressao e impossibilidade
  - Arquivo: `lbot-datagen/lbot-datagen-frontend/src/app/models/level-config.model.ts`
  - O que fazer:
    - Verificar manualmente (no papel/mentalmente) que:
      - Niveis 1-2: existe caminho valido usando APENAS D e R
      - Niveis 3-4: NAO existe caminho valido usando apenas D e R (arco eh obrigatorio)
      - Nivel 5: NAO existe caminho valido sem usar rampa
    - Ajustar coordenadas se necessario para garantir estas propriedades

## Arquivos Referencia

- `lbot-datagen/lbot-datagen-frontend/src/app/models/level-config.model.ts` - Niveis atuais como base
- `lbot-datagen/lbot-datagen-frontend/src/app/services/arena-builder.service.ts` - Como obstaculos sao renderizados (entender limites de tamanho)
- `lbot-datagen/lbot-datagen-frontend/src/app/services/physics.service.ts` - Limites da arena para nao posicionar fora

## Criterios de Aceite

- [ ] CA08: Niveis 1-2 resolviveis sem comando A (apenas D e R)
- [ ] CA09: Niveis 3-4 NAO resolviveis sem pelo menos um comando A
- [ ] CA10: Nivel 5 exige subir pelo menos uma rampa
- [ ] CA11: Cada nivel tem formato de arena visual e funcional correto
- [ ] Niveis visivelmente diferentes entre si (cores, formatos, tipos de obstaculo)
- [ ] Start/goal variam por nivel (nao mais fixos em -150,-150 e 150,150)

## Testes Esperados

- Validacao manual: navegar cada nivel e confirmar que os caminhos sao coerentes
- Tentar resolver niveis 3-4 sem arcos para confirmar impossibilidade

## Comandos pos-fase

```bash
cd lbot-datagen/lbot-datagen-frontend && ng build && ng serve
```

## Registro de Execucao

- Data:
- Arquivos criados:
- Arquivos alterados:
- Testes executados:
- Resultado:
- Pendencias:
