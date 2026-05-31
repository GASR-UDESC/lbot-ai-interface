# Fase 07: Chat Integration & Geracao de Dados de Treino

## Status: PENDENTE

## Objetivo

Adaptar o componente LbotChat para funcionar no modo gamificado (chat unico por run, sem controles virtuais), integrar o sistema de rating por mensagem, e garantir que toda interacao gera dados de treino automaticamente com informacao do nivel. Ao final, o jogo esta completo e funcional como ferramenta de gamificacao + coleta de dados.

## Pre-requisitos

- Fase 04 concluida (GamePage funcional com chat integrado)
- Fase 03 concluida (GameStateService para saber nivel atual)

## Tarefas

- [ ] Tarefa 1: Adaptar LbotChat para modo gamificado
  - Arquivo: `lbot-datagen/lbot-datagen-frontend/src/app/components/lbot-chat/lbot-chat.ts`
  - O que fazer:
    - Adicionar @Input() `externalChatId?: string` - se fornecido, NAO cria novo chat (usa o chatId fornecido pelo GamePage)
    - Adicionar @Input() `gameMode: boolean = false` - se true, esconde botao "Encerrar" (observation popup)
    - No initializeChat(): se externalChatId fornecido, usar esse ao inves de chamar startChat()
    - Se gameMode=true e externalChatId nao fornecido: chamar startChat() normalmente mas nao mostrar opcoes de finalizar
    - Manter rating de estrelas funcional (1-5) em todos os modos
    - O historico de chat persiste entre niveis (mesmo chatId)

- [ ] Tarefa 2: Gerenciar chat por run no GamePage
  - Arquivo: `lbot-datagen/lbot-datagen-frontend/src/app/pages/game/game.page.ts`
  - O que fazer:
    - No startRun(): chamar messagesService.startChat() para obter um chatId para o run inteiro
    - Passar chatId para LbotChat via Input externalChatId
    - O chat NAO reinicia entre niveis (mesmo chatId, historico acumula)
    - Ao resetar o run (Jogar Novamente): criar novo chatId

- [ ] Tarefa 3: Garantir que rating de estrelas funciona no modo jogo
  - Arquivo: `lbot-datagen/lbot-datagen-frontend/src/app/components/lbot-chat/lbot-chat.ts` (verificar)
  - Arquivo: `lbot-datagen/lbot-datagen-frontend/src/app/components/lbot-chat/lbot-chat.html` (verificar)
  - O que fazer:
    - Rating de 1-5 estrelas aparece apos cada resposta da IA (ja existe)
    - Confirmar que no modo gameMode=true, o rating funciona sem mudancas
    - O rating e OPCIONAL (nao bloqueia proximo envio - ja funciona assim)
    - Visual: estrelas em destaque para incentivar avaliacao (pode adicionar leve destaque CSS)
    - A avaliacao e salva via messagesService.evaluateMessage (ja existente)

- [ ] Tarefa 4: Garantir geracao de dados de treino
  - Arquivo: (verificar que nao precisa de mudancas no backend)
  - O que fazer:
    - Cada mensagem enviada ja gera: prompt (NL), output (LBML), grade (1-5 ou null) no backend
    - Confirmar que o fluxo existente funciona: sendMessage() -> backend salva -> evaluateMessage() -> atualiza grade
    - Os dados sao salvos independentemente do jogador completar o nivel ou nao (ja funciona assim)
    - Perda de dados se backend offline: comportamento aceitavel (spec define: "dados sao perdidos")
    - Nao e necessario enviar nivel junto (nice to have mas fora do escopo critico)

- [ ] Tarefa 5: Integrar banner de nivel no chat (UX)
  - Arquivo: `lbot-datagen/lbot-datagen-frontend/src/app/components/lbot-chat/lbot-chat.ts`
  - Arquivo: `lbot-datagen/lbot-datagen-frontend/src/app/components/lbot-chat/lbot-chat.html`
  - O que fazer:
    - Adicionar @Input() `currentLevelName?: string`
    - Quando currentLevelName muda (nivel troca), inserir mensagem de sistema no chat: "--- Nivel X: {nome} ---"
    - Essa mensagem e apenas visual (nao envia ao backend)
    - Ajuda o jogador a saber em qual nivel esta olhando o historico

## Arquivos Referencia

- `lbot-datagen/lbot-datagen-frontend/src/app/components/lbot-chat/lbot-chat.ts` - Componente de chat completo
- `lbot-datagen/lbot-datagen-frontend/src/app/components/lbot-chat/lbot-chat.html` - Template com rating
- `lbot-datagen/lbot-datagen-frontend/src/app/services/messages-service.ts` - Service de mensagens

## Criterios de Aceite

- [ ] CA01: Chat usa chatId unico por run
  - Cenario: Given jogo iniciado / When joga niveis 1,2,3 / Then todas as mensagens tem mesmo chatId no backend
- [ ] CA02: Historico preservado entre niveis
  - Cenario: Given conversa no nivel 1 / When avanca para nivel 2 / Then mensagens do nivel 1 continuam visiveis
- [ ] CA03: Banner de nivel aparece ao trocar
  - Cenario: Given estava no nivel 1 / When avanca para nivel 2 / Then aparece "--- Nivel 2: Escritorio ---" no chat
- [ ] CA04: Rating de estrelas funciona no modo jogo
  - Cenario: Given IA respondeu com LBML / When jogador clica 4 estrelas / Then rating salvo via API
- [ ] CA05: Rating opcional nao bloqueia
  - Cenario: Given IA respondeu / When jogador NAO avalia e envia novo comando / Then funciona normalmente
- [ ] CA06: Dados de treino salvos automaticamente
  - Cenario: Given jogador envia "ande para frente" / When IA responde "D40F;" / Then par (prompt, output) salvo no backend
- [ ] CA07: Jogar Novamente cria novo chat
  - Cenario: Given jogador completou e clicou "Jogar Novamente" / When novo run inicia / Then novo chatId criado, historico limpo

## Testes Esperados

- Nenhum teste automatizado (decisao do projeto)

## Comandos pos-fase

- `cd lbot-datagen/lbot-datagen-frontend && ng serve`
- `cd lbot-datagen/lbot-datagen-backend && ./mvnw spring-boot:run`
- Verificar: jogar completo, enviar comandos via chat, avaliar com estrelas
- Verificar: checar no banco (ou via API) que mensagens foram salvas com grade
- Verificar: historico persiste entre niveis
- Verificar: "Jogar Novamente" limpa tudo e cria novo chat

## Registro de Execucao

- Data:
- Arquivos criados:
- Arquivos alterados:
- Testes executados:
- Resultado:
- Pendencias:
