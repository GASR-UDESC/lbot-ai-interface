# Fase 04: Integracao e Validacao

## Status: PENDENTE

## Objetivo

Validar que todas as partes do sistema (frontend, fisica, headless, sensores) estao consistentes e atendem aos cenarios de aceite da especificacao de negocio. Rodar a suite completa de testes, verificar type checking, e documentar quaisquer pendencias.

## Pre-requisitos

- Fase 01 concluida (configuracao centralizada)
- Fase 02 concluida (frontend e fisica)
- Fase 03 concluida (headless e sensores)

## Tarefas

- [ ] Tarefa 1: Rodar type checking completo
  - Arquivo: Todo o projeto
  - O que fazer: Executar `npm run check` para garantir que nao ha erros de TypeScript em nenhum modulo (`tsconfig.app.json` e `tsconfig.server.json`).
- [ ] Tarefa 2: Rodar suite completa de testes
  - Arquivo: `tests/`
  - O que fazer: Executar `npm test` (vitest run). Todos os testes existentes devem continuar passando. Os novos testes de sensores, arena-objects e api devem passar.
- [ ] Tarefa 3: Verificar consistencia entre frontend e backend
  - Arquivo: N/A (analise cruzada)
  - O que fazer: Comparar as posicoes e dimensoes dos objetos em `shared/arena-objects.ts` com as implementacoes no frontend (`SimulatorCanvas.tsx`), fisica (`engine.ts`) e headless (`scene-renderer.ts`). Garantir que todas usam os mesmos valores.
- [ ] Tarefa 4: Validar cenarios de aceite da business-spec
  - Arquivo: `task/business-spec.md`
  - O que fazer: Verificar que cada cenario de aceite (CA01-CA06) esta coberto:
    - CA01: Camera headless mostra objetos -> Validado na Fase 03
    - CA02: Visualizacao 3D no navegador -> Validado na Fase 02
    - CA03: Sensor detecta objeto a frente -> Validado na Fase 03
    - CA04: Robo colide com objeto -> Validado na Fase 02
    - CA05: Fallback 2D funciona -> Validado na Fase 03
    - CA06: Reset preserva objetos -> Validado na Fase 02
- [ ] Tarefa 5: Verificar performance do navegador
  - Arquivo: N/A (teste manual)
  - O que fazer: Executar `npm run dev`, abrir o navegador, verificar que o FPS se mantem proximo de 60 com os 6 objetos adicionados.
- [ ] Tarefa 6: Documentar pendencias ou limitacoes encontradas
  - Arquivo: `task/tech-spec.md` ou `task/phase-04.md`
  - O que fazer: Se houver algum comportamento nao esperado, teste que nao passa, ou limitacao tecnica, documentar na secao "Pendencias" desta fase.

## Arquivos Referencia

- `3.controlador/lbot-simulator-web/task/business-spec.md` - Cenarios de aceite a validar
- `3.controlador/lbot-simulator-web/task/tech-spec.md` - Decisoes tecnicas e mapa de fases
- `3.controlador/lbot-simulator-web/package.json` - Scripts de build e teste
- Todos os arquivos alterados nas fases anteriores

## Criterios de Aceite

- [ ] CA-INT-01: Compilacao TypeScript sem erros
  - Cenario: Dado que todas as fases foram implementadas, quando executo `npm run check`, entao nenhum erro de tipo e reportado.
- [ ] CA-INT-02: Todos os testes passam
  - Cenario: Dado que a suite de testes e executada, quando `npm test` termina, entao 100% dos testes passam (incluindo novos e existentes).
- [ ] CA-INT-03: Consistencia frontend/backend
  - Cenario: Dado que comparo as implementacoes, quando verifico posicoes e dimensoes, entao frontend, fisica e headless usam os mesmos valores de `shared/arena-objects.ts`.
- [ ] CA-INT-04: Nenhuma regressao nos endpoints existentes
  - Cenario: Dado que os endpoints `/api/health`, `/api/camera`, `/api/sensors`, `/api/status`, `/api/state`, `/api/commands`, `/api/reset` existem, quando chamados, entao retornam respostas validas e sem erros.

## Testes Esperados

- Validacao manual de todos os CAs da business-spec
- `npm run check` -> 0 erros
- `npm test` -> 100% passando
- `npm run dev` -> Navegador renderiza 60 FPS

## Comandos pos-fase

- `npm run check` - Type checking completo
- `npm test` - Suite de testes automatizados
- `npm run dev` - Validacao manual no navegador

## Registro de Execucao

<Preenchido pelo agente durante a execucao>

- Data:
- Arquivos criados:
- Arquivos alterados:
- Testes executados:
- Resultado:
- Pendencias:
