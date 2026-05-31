# Fase 06: Prompt LLM + Regex Backend

## Status: PENDENTE

## Objetivo

Reescrever completamente o prompt de conversao linguagem natural -> LBML no backend Spring Boot, incluindo documentacao do novo comando A (arco). Atualizar a regex de validacao no AIService.java para aceitar o formato do comando A.

## Pre-requisitos

- Fase 01 concluida (define a sintaxe final do comando A)

## Tarefas

- [ ] Tarefa 1: Atualizar regex LBML no AIService.java
  - Arquivo: `lbot-datagen/lbot-datagen-backend/src/main/java/br/com/roselabs/lbot_datagen_backend/services/AIService.java`
  - O que fazer:
    - Alterar `LBML_REGEX` de:
      ```java
      "^(D\\d+[FBLR];|R\\d+[LR];)+$"
      ```
      Para:
      ```java
      "^(D\\d+[FBLR];|R\\d+[LR];|A\\d+[LR]\\d+;)+$"
      ```
    - Garantir que a validacao aceita sequencias mistas como `D50F;A30R90;D20F;`

- [ ] Tarefa 2: Reescrever o prompt convert-to-lml.txt
  - Arquivo: `lbot-datagen/lbot-datagen-backend/src/main/resources/static/prompts/convert-to-lml.txt`
  - O que fazer:
    - Reescrever completamente o prompt (o atual eh desorganizado com secoes duplicadas)
    - Estrutura do novo prompt:
      1. Introducao do papel (voce eh um conversor NL -> LBML)
      2. Documentacao da LBML:
         - Comando D: deslocamento linear (D<valor><direcao>;)
         - Comando R: rotacao in-place (R<valor><direcao>;)
         - **Comando A: arco/curva (A<raio><direcao><angulo>;)** - NOVO
      3. Regras de uso do comando A:
         - "faca uma curva", "contorne", "curve" -> usar A
         - "vire", "gire" -> usar R (rotacao in-place)
         - Raio default quando nao especificado: 30 cm
         - Angulo default para "curva": 90 graus
         - "curva suave" -> raio maior (50+)
         - "curva fechada" -> raio menor (15-20)
      4. Exemplos de conversao com A:
         - "faca uma curva para a direita" -> A30R90;
         - "contorne o obstaculo pela esquerda" -> A40L180;
         - "faca uma curva suave para a direita de 45 graus" -> A50R45;
         - "faca um semicirculo" -> A30R180; ou A30L180;
         - "faca uma volta completa" -> A30R360;
      5. Regras existentes (D, R, unidades, erros, comandos criativos)
      6. Formato de saida (apenas LBML ou ERRO)
    - Tom: claro, organizado, sem secoes duplicadas
    - Manter regra: "vire" = R, "curve" = A

- [ ] Tarefa 3: Atualizar prompt normalize-prompts-in-cm.txt (se necessario)
  - Arquivo: `lbot-datagen/lbot-datagen-backend/src/main/resources/static/prompts/normalize-prompts-in-cm.txt`
  - O que fazer:
    - Verificar se o prompt de normalizacao precisa entender raio de curva
    - Se usuario disser "faca uma curva com raio de 1 metro", o normalizador deve converter "1 metro" para "100 cm"
    - Adicionar instrucao ao prompt de normalizacao para tratar raio de curvas se necessario

- [ ] Tarefa 4: Validar integracao end-to-end
  - Arquivo: Nenhum arquivo alterado nesta tarefa (validacao manual)
  - O que fazer:
    - Levantar o backend (`mvn spring-boot:run` ou via IDE)
    - Testar via API/chat:
      - "ande 50 cm para frente" -> deve gerar D50F;
      - "gire 90 graus para a direita" -> deve gerar R90R;
      - "faca uma curva para a direita" -> deve gerar A30R90; (ou similar)
      - "curve suavemente para a esquerda" -> deve gerar A50L90; (ou similar)
    - Confirmar que a regex valida os comandos A gerados pelo LLM

## Arquivos Referencia

- `lbot-datagen/lbot-datagen-backend/src/main/java/br/com/roselabs/lbot_datagen_backend/services/AIService.java` - Servico de IA com regex e fluxo de conversao
- `lbot-datagen/lbot-datagen-backend/src/main/resources/static/prompts/convert-to-lml.txt` - Prompt atual (sera reescrito)
- `lbot-datagen/lbot-datagen-backend/src/main/resources/static/prompts/normalize-prompts-in-cm.txt` - Prompt de normalizacao

## Criterios de Aceite

- [ ] CA14: "faca uma curva suave para a direita" gera comando A com direcao R
- [ ] CA15: "ande para frente" e "gire para a esquerda" continuam gerando D e R (nao A)
- [ ] CA12 (backend): Regex no backend aceita `A30R90;` como LBML valido
- [ ] CA13 (backend): Regex rejeita formatos invalidos (`A30;`, `ARL90;`)
- [ ] Prompt eh limpo, organizado, sem duplicacoes

## Testes Esperados

- Validacao manual via API REST ou chat no frontend
- Testar pelo menos 5 comandos em linguagem natural e verificar saida LBML

## Comandos pos-fase

```bash
cd lbot-datagen/lbot-datagen-backend && ./mvnw compile
```

## Registro de Execucao

- Data:
- Arquivos criados:
- Arquivos alterados:
- Testes executados:
- Resultado:
- Pendencias:
