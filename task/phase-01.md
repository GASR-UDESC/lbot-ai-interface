# Fase 01: Parser LBML + Types para comando A

## Status: PENDENTE

## Objetivo

Expandir o sistema de tipos e o parser LBML do datagen-frontend para reconhecer, validar e parsear o novo comando de arco (`A<raio><direcao><angulo>;`). Apos esta fase, o frontend aceita comandos A como validos mas ainda nao os executa visualmente.

## Pre-requisitos

- Nenhum (primeira fase)

## Tarefas

- [ ] Tarefa 1: Expandir tipos em lbml-command.model.ts
  - Arquivo: `lbot-datagen/lbot-datagen-frontend/src/app/models/lbml-command.model.ts`
  - O que fazer:
    - Adicionar `'A'` ao tipo `LbmlCommandType` (fica `'D' | 'R' | 'A'`)
    - Criar tipo `ArcDirection = 'L' | 'R'`
    - Criar interface `ParsedArcCommand` com campos: `type: 'A'`, `radius: number`, `direction: ArcDirection`, `angle: number`
    - Criar tipo union `ParsedLbmlCommand = ParsedCommand | ParsedArcCommand` para ser usado no fluxo de execucao
    - Manter `ParsedCommand` existente intacto para retrocompatibilidade

- [ ] Tarefa 2: Expandir o LBML parser service
  - Arquivo: `lbot-datagen/lbot-datagen-frontend/src/app/services/lbml-parser.service.ts`
  - O que fazer:
    - Adicionar regex para comando A: `private static readonly ARC_COMMAND_REGEX = /^A(\d+)([LR])(\d+);$/;`
    - Atualizar `COMMAND_REGEX` ou criar logica que tenta match de D/R primeiro, depois A
    - Criar metodo `parseArcCommand(command: string): ParsedArcCommand | null`
    - Atualizar `parseCommand()` para retornar `ParsedLbmlCommand | null` (tentar D/R, se falhar tentar A)
    - Atualizar `parseCommandSequence()` para retornar `ParsedLbmlCommand[] | null`
    - Atualizar `formatCommand()` para formatar ParsedArcCommand como `A<radius><direction><angle>`
    - Atualizar `isValidCommand()` para reconhecer comandos A

- [ ] Tarefa 3: Atualizar imports no robo-simulator
  - Arquivo: `lbot-datagen/lbot-datagen-frontend/src/app/components/robo-simulator/robo-simulator.ts`
  - O que fazer:
    - Atualizar import de `ParsedCommand` para incluir `ParsedLbmlCommand` e `ParsedArcCommand`
    - Atualizar tipo da variavel em `executeCommandSequenceFromString` para usar `ParsedLbmlCommand[]`
    - Adicionar stub em `executeCommand()`: se `cmd.type === 'A'`, logar "Arc command not yet implemented" (sera implementado na Fase 2)

## Arquivos Referencia

- `lbot-datagen/lbot-datagen-frontend/src/app/models/lbml-command.model.ts` - Modelo atual para entender a estrutura de tipos
- `lbot-datagen/lbot-datagen-frontend/src/app/services/lbml-parser.service.ts` - Parser atual para entender o pattern de parsing
- `lbot-simulator-web/shared/lbml.ts` - Referencia de como o parser compartilhado funciona (nao sera alterado)

## Criterios de Aceite

- [ ] CA12: A string `A30R90;` eh reconhecida como LBML valida pelo parser
- [ ] CA13: Strings invalidas (`A30;`, `ARL90;`, `A30R;`, `A-5R90;`) sao rejeitadas
- [ ] CA04 (parcial): Comandos D e R existentes continuam funcionando normalmente
- [ ] Regex atualizada: `/^(D\d+[FBLR];|R\d+[LR];|A\d+[LR]\d+;)+$/` aceita sequencias mistas

## Testes Esperados

- Nenhum teste automatizado (decisao do usuario)
- Validacao manual: abrir console do browser e chamar `lbmlParser.parseCommandSequence('D50F;A30R90;D20F;')`

## Comandos pos-fase

```bash
cd lbot-datagen/lbot-datagen-frontend && ng build
```

## Registro de Execucao

- Data:
- Arquivos criados:
- Arquivos alterados:
- Testes executados:
- Resultado:
- Pendencias:
