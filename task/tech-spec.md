# Plano Tecnico: Expansao LBML com Curvas, Correcao de Fisica e Redesign de Niveis

## Visao Geral

A implementacao se concentra exclusivamente no modulo **lbot-datagen** (frontend Angular + backend Spring Boot). A abordagem tecnica eh:

1. **Parser LBML** expandido com novo tipo de comando `A` (arco) usando regex e type system
2. **Colisao** implementada via pre-calculo de posicao maxima valida ANTES da animacao (nao em tempo real)
3. **Arco** animado com parametrizacao angular (trajetoria circular real, nao segmentos retos)
4. **Arenas variaveis** representadas na LevelConfig com suporte a circulares (poligono de muitos lados)
5. **Niveis** redesenhados manualmente com progressao de dificuldade
6. **Prompt LLM** reescrito com documentacao completa do comando A

## Modulos Envolvidos

- **lbot-datagen-frontend** (Angular): Parser LBML, modelos, simulador 3D, fisica, arena builder, level configs
- **lbot-datagen-backend** (Spring Boot): AIService (regex de validacao), prompt de conversao LLM

## Arquivos Impactados

### Alterados

| Arquivo | O que muda |
|---------|-----------|
| `lbot-datagen/lbot-datagen-frontend/src/app/models/lbml-command.model.ts` | Adicionar tipo `'A'` ao `LbmlCommandType`, novo tipo `ArcDirection`, nova interface `ParsedArcCommand` |
| `lbot-datagen/lbot-datagen-frontend/src/app/services/lbml-parser.service.ts` | Nova regex para comando A, metodo `parseArcCommand()`, expandir `parseCommand()` e `parseCommandSequence()` |
| `lbot-datagen/lbot-datagen-frontend/src/app/components/robo-simulator/robo-simulator.ts` | Novo `animateArc()`, `executeArcCommand()`, integrar colisao em `executeDistanceCommand()`, tratar tipo A em `executeCommand()` |
| `lbot-datagen/lbot-datagen-frontend/src/app/services/physics.service.ts` | Novo `getMaxValidArcPosition()` com sampling discreto, ajustar `createArenaWallsBodies()` para arena shapes variaveis |
| `lbot-datagen/lbot-datagen-frontend/src/app/services/arena-builder.service.ts` | Suporte a arenas circulares/retangulares em `createArenaWalls()` e `createThemedWalls()`, novos metodos para poligonos |
| `lbot-datagen/lbot-datagen-frontend/src/app/models/level-config.model.ts` | Novo campo `arenaShape`, `arenaSize`, redesign completo dos 5 niveis |
| `lbot-datagen/lbot-datagen-frontend/src/app/services/level-config.service.ts` | Expor novo campo arenaShape se necessario |
| `lbot-datagen/lbot-datagen-backend/src/main/java/br/com/roselabs/lbot_datagen_backend/services/AIService.java` | Atualizar `LBML_REGEX` para incluir comando A |
| `lbot-datagen/lbot-datagen-backend/src/main/resources/static/prompts/convert-to-lml.txt` | Reescrever completamente com documentacao do comando A |

### Novos

Nenhum arquivo novo sera criado. Todas as mudancas sao em arquivos existentes.

## Decisoes Tecnicas

| Decisao | Opcao escolhida | Justificativa |
|---------|-----------------|---------------|
| Escopo da atualizacao LBML | Apenas datagen (frontend + backend) | Business-spec explicita que lbot-brain, lbot-simulator-web estao fora de escopo |
| Estrategia de colisao | Pre-calculo com getMaxValidPosition() antes de animar | Simples, eficiente, ja tem codigo base no physics.service.ts |
| Animacao do arco | Novo metodo animateArc() com parametrizacao angular | Trajetoria circular suave, rotacao tangente automatica, visualmente fiel |
| Arena circular | Poligono regular de muitos lados (~32 segmentos) | Funciona com CANNON.Box existente, visualmente indistinguivel de circulo |
| Colisao em arco | Sampling discreto ao longo da trajetoria curva | Mesma abordagem do linear (step ~5 unidades), previsivel e testavel |
| Formato arena na config | Campos diretos na LevelConfig (arenaShape, arenaSize) | Simples, sem over-engineering |
| Redesign de niveis | Manual no level-config.model.ts | Controle total sobre posicionamento para garantir progressao de dificuldade |
| Testes | Sem testes automatizados, foco na implementacao | Decisao do usuario |
| Localizacao da logica de muros | Expandir metodos existentes no arena-builder e physics | Evita proliferacao de services |

## Dependencias entre Fases

```
Fase 1 (Parser) ─────┐
                      ├─> Fase 2 (Colisao Linear + Arc) ──> Fase 3 (Colisao Arc)
                      │
Fase 4 (LevelConfig)──┤
                      │
                      └─> Fase 5 (Redesign Niveis) [depende de Fase 1 + Fase 4]

Fase 6 (Prompt LLM) ──> independente, mas melhor apos Fase 1
```

- Fase 1 -> Fase 2 (precisa dos types e parser para executar comandos A)
- Fase 2 -> Fase 3 (precisa do animateArc para integrar colisao nele)
- Fase 4 -> Fase 5 (precisa da nova interface LevelConfig com arena shapes)
- Fase 1 -> Fase 5 (niveis 3-4 referenciam comando A)
- Fase 6 eh independente (pode rodar apos Fase 1)

## Mapa de Fases

| Fase | Descricao | Modulo |
|------|-----------|--------|
| 01 | Parser LBML + Types para comando A | datagen-frontend |
| 02 | Colisao linear + animateArc() | datagen-frontend |
| 03 | Colisao em arco + integracao completa | datagen-frontend |
| 04 | LevelConfig + Arena Shapes variaveis | datagen-frontend |
| 05 | Redesign dos 5 niveis | datagen-frontend |
| 06 | Prompt LLM + regex backend | datagen-backend |
