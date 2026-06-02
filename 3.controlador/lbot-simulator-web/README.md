# lbot-simulator-web

Simulador standalone em React para executar comandos LBML na web.

## O que faz

- Renderiza o simulador 3D no navegador com `three` e `cannon-es`
- Aceita comandos LBML pela UI
- Aceita comandos LBML por HTTP
- Encaminha os comandos HTTP para a aba ativa do simulador via SSE
- Expõe status e ultimo estado conhecido da simulacao

## Requisitos

- Node.js 20+
- npm 10+

## Rodando em desenvolvimento

```bash
npm install
npm run dev
```

Servicos:

- Frontend: `http://localhost:5173`
- API: `http://localhost:3001`

## Scripts

```bash
npm run dev
npm run check
npm run test
npm run build
```

## Endpoints

### Health

```bash
curl http://localhost:3001/api/health
```

### Status

```bash
curl http://localhost:3001/api/status
```

### Ultimo estado conhecido

```bash
curl http://localhost:3001/api/state
```

### Executar comando LBML

```bash
curl -X POST http://localhost:3001/api/commands \
  -H 'Content-Type: application/json' \
  -d '{"command":"D40F;R90L;D20F;"}'
```

### Resetar simulador

```bash
curl -X POST http://localhost:3001/api/reset \
  -H 'Content-Type: application/json' \
  -d '{}'
```

## Observacoes

- A API envia comandos para a aba ativa conectada em `/api/events`
- Se nenhuma aba estiver conectada, `POST /api/commands` e `POST /api/reset` retornam `409`
- Ao abrir uma nova aba do simulador, ela assume a conexao ativa

## Formato LBML aceito

- Deslocamento: `D<valor><F|B|L|R>;`
- Rotacao: `R<angulo><L|R>;`

Exemplos:

- `D40F;`
- `R90L;`
- `D40F;R90L;D20F;`
