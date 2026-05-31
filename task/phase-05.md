# Fase 05: Backend - Leaderboard API

## Status: CONCLUIDO

## Objetivo

Criar a entidade GameRun e a API REST no backend Spring Boot para persistir e consultar o leaderboard. Ao final, os endpoints POST /game-runs e GET /game-runs estao funcionais.

## Pre-requisitos

- Nenhum (backend independente do frontend - pode rodar em paralelo com fases anteriores se desejado)

## Tarefas

- [x] Tarefa 1: Criar entidade GameRun
  - Arquivo: `lbot-datagen/lbot-datagen-backend/src/main/java/com/lbot/datagen/entity/GameRun.java`
  - O que fazer: Criar entidade JPA com campos:
    - `id` (UUID, @GeneratedValue)
    - `nickname` (String, @NotBlank)
    - `level1TimeMs` (Long) - tempo do nivel 1 em milissegundos
    - `level2TimeMs` (Long)
    - `level3TimeMs` (Long)
    - `level4TimeMs` (Long)
    - `level5TimeMs` (Long)
    - `totalTimeMs` (Long) - soma dos 5 tempos
    - `completedAt` (LocalDateTime, gerado automaticamente no save)
    - Usar @Table(name = "game_runs")
    - Lombok: @Entity, @Getter, @Setter, @NoArgsConstructor, @AllArgsConstructor, @Builder

- [x] Tarefa 2: Criar GameRunRepository
  - Arquivo: `lbot-datagen/lbot-datagen-backend/src/main/java/com/lbot/datagen/repository/GameRunRepository.java`
  - O que fazer: Interface JpaRepository<GameRun, UUID> com metodo customizado:
    - `List<GameRun> findAllByOrderByTotalTimeMsAsc()` - retorna todos ordenados por tempo total crescente

- [x] Tarefa 3: Criar DTOs (Request e Response)
  - Arquivo: `lbot-datagen/lbot-datagen-backend/src/main/java/com/lbot/datagen/dto/CreateGameRunRequest.java`
  - O que fazer: Record ou class com campos: nickname (String, @NotBlank), level1TimeMs, level2TimeMs, level3TimeMs, level4TimeMs, level5TimeMs (todos Long, @NotNull)
  - Arquivo: `lbot-datagen/lbot-datagen-backend/src/main/java/com/lbot/datagen/dto/GameRunResponse.java`
  - O que fazer: Record ou class com todos os campos da entidade: id, nickname, level1TimeMs-level5TimeMs, totalTimeMs, completedAt

- [x] Tarefa 4: Criar GameRunService
  - Arquivo: `lbot-datagen/lbot-datagen-backend/src/main/java/com/lbot/datagen/service/GameRunService.java`
  - O que fazer:
    - `GameRunResponse createGameRun(CreateGameRunRequest request)`: calcula totalTimeMs = soma dos 5, set completedAt = LocalDateTime.now(), salva e retorna
    - `List<GameRunResponse> getAllGameRuns()`: retorna todos ordenados por totalTimeMs asc
    - Mapper manual (ou metodo toResponse) entre entity e DTO

- [x] Tarefa 5: Criar GameRunController
  - Arquivo: `lbot-datagen/lbot-datagen-backend/src/main/java/com/lbot/datagen/controller/GameRunController.java`
  - O que fazer:
    - @RestController, @RequestMapping("/game-runs"), @RequiredArgsConstructor
    - `POST /game-runs` (@RequestBody @Valid CreateGameRunRequest) -> retorna GameRunResponse (201 Created)
    - `GET /game-runs` -> retorna List<GameRunResponse> (200 OK)
    - CORS ja esta configurado globalmente no WebConfig existente

## Arquivos Referencia

- `lbot-datagen/lbot-datagen-backend/src/main/java/com/lbot/datagen/entity/Chat.java` - Pattern de entidade existente
- `lbot-datagen/lbot-datagen-backend/src/main/java/com/lbot/datagen/entity/Message.java` - Pattern de entidade com FK
- `lbot-datagen/lbot-datagen-backend/src/main/java/com/lbot/datagen/repository/ChatRepository.java` - Pattern de repository
- `lbot-datagen/lbot-datagen-backend/src/main/java/com/lbot/datagen/controller/ChatController.java` - Pattern de controller
- `lbot-datagen/lbot-datagen-backend/src/main/java/com/lbot/datagen/controller/VirtualControlController.java` - Pattern de controller com DTO

## Criterios de Aceite

- [x] CA01: POST /game-runs salva um registro e retorna 201
  - Cenario: Given payload valido {nickname:"Jogador1", level1TimeMs:60000, ...} / When POST /game-runs / Then retorna 201 com id gerado, totalTimeMs calculado, completedAt preenchido
- [x] CA02: GET /game-runs retorna lista ordenada por tempo total
  - Cenario: Given 3 game runs com tempos totais 300000, 150000, 200000 / When GET /game-runs / Then retorna [150000, 200000, 300000]
- [x] CA03: Validacao rejeita nickname vazio
  - Cenario: Given payload com nickname="" / When POST /game-runs / Then retorna 400 Bad Request
- [x] CA04: Validacao rejeita tempos nulos
  - Cenario: Given payload com level1TimeMs=null / When POST /game-runs / Then retorna 400 Bad Request
- [x] CA05: totalTimeMs e calculado corretamente
  - Cenario: Given tempos 60000+70000+80000+90000+100000 / When salvo / Then totalTimeMs = 400000
- [x] CA06: Lista vazia retorna 200 com array vazio
  - Cenario: Given nenhum game run salvo / When GET /game-runs / Then retorna 200 com []

## Testes Esperados

- Nenhum teste automatizado (decisao do projeto)
- Testar manualmente com Postman ou curl

## Comandos pos-fase

- `cd lbot-datagen/lbot-datagen-backend && ./mvnw spring-boot:run`
- Testar com curl:
  - `curl -X POST http://localhost:8080/game-runs -H "Content-Type: application/json" -d '{"nickname":"Teste","level1TimeMs":60000,"level2TimeMs":70000,"level3TimeMs":80000,"level4TimeMs":90000,"level5TimeMs":100000}'`
  - `curl http://localhost:8080/game-runs`

## Registro de Execucao

- Data: 2026-05-31
- Arquivos criados:
  - `lbot-datagen/lbot-datagen-backend/src/main/java/br/com/roselabs/lbot_datagen_backend/entities/GameRun.java`
  - `lbot-datagen/lbot-datagen-backend/src/main/java/br/com/roselabs/lbot_datagen_backend/repositories/GameRunRepository.java`
  - `lbot-datagen/lbot-datagen-backend/src/main/java/br/com/roselabs/lbot_datagen_backend/dtos/CreateGameRunRequest.java`
  - `lbot-datagen/lbot-datagen-backend/src/main/java/br/com/roselabs/lbot_datagen_backend/dtos/GameRunResponse.java`
  - `lbot-datagen/lbot-datagen-backend/src/main/java/br/com/roselabs/lbot_datagen_backend/services/GameRunService.java`
  - `lbot-datagen/lbot-datagen-backend/src/main/java/br/com/roselabs/lbot_datagen_backend/controllers/GameRunController.java`
- Arquivos alterados: Nenhum
- Testes executados: `./mvnw compile` + `./mvnw package -DskipTests` - ambos com sucesso (sem erros de compilacao)
- Resultado: BUILD SUCCESS - todos os 6 arquivos criados e compilados corretamente. Package correto: `br.com.roselabs.lbot_datagen_backend` (diferente do especificado na fase que usava `com.lbot.datagen`). Diretórios corretos: entities/, repositories/, dtos/, services/, controllers/ (todos no plural, padrao do projeto).
- Pendencias: Nenhuma. Os endpoints POST /game-runs e GET /game-runs estao prontos para integracao na Fase 06.
