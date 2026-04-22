import cors from 'cors';
import express, { type Request, type Response } from 'express';
import {
  type ClientStateUpdate,
  type CommandResponse,
  type ExecuteCommandRequest,
  type ResetRequest,
  type ResetResponse,
  type ServerEvent,
  type SimulatorStateResponse,
  type SimulatorStatusResponse,
} from '../shared/protocol.js';
import { normalizeLbml, validateLbml } from '../shared/lbml.js';

type EventSink = {
  clientId: string;
  response: Response;
};

const app = express();
const port = Number.parseInt(process.env.PORT ?? '3001', 10);

let activeClient: EventSink | null = null;
let lastKnownState: ClientStateUpdate['state'] | null = null;
let pendingEvents = 0;

app.use(cors());
app.use(express.json());

function createClientId(): string {
  return `sim-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;
}

function writeEvent(response: Response, event: ServerEvent): void {
  response.write(`data: ${JSON.stringify(event)}\n\n`);
}

function ensureActiveClient(response: Response): response is never {
  if (activeClient) {
    return false;
  }

  response.status(409).json({ error: 'Nenhuma aba do simulador esta conectada.' });
  return true;
}

function publish(event: ServerEvent): string {
  if (!activeClient) {
    throw new Error('Nenhuma aba do simulador esta conectada.');
  }

  pendingEvents += 1;
  writeEvent(activeClient.response, event);
  return activeClient.clientId;
}

function setSseHeaders(response: Response): void {
  response.setHeader('Content-Type', 'text/event-stream');
  response.setHeader('Cache-Control', 'no-cache, no-transform');
  response.setHeader('Connection', 'keep-alive');
  response.setHeader('X-Accel-Buffering', 'no');
  response.flushHeaders();
}

app.get('/api/health', (_request, response) => {
  response.json({ status: 'online' });
});

app.get('/api/status', (_request, response: Response<SimulatorStatusResponse>) => {
  response.json({
    connected: Boolean(activeClient),
    activeClientId: activeClient?.clientId ?? null,
    pendingEvents,
  });
});

app.get('/api/state', (_request, response: Response<SimulatorStateResponse>) => {
  response.json({
    connected: Boolean(activeClient),
    activeClientId: activeClient?.clientId ?? null,
    state: lastKnownState,
  });
});

app.get('/api/events', (request, response) => {
  setSseHeaders(response);

  const clientId = createClientId();

  if (activeClient) {
    writeEvent(activeClient.response, {
      type: 'disconnect',
      reason: 'Uma nova aba do simulador assumiu a conexao ativa.',
    });
    activeClient.response.end();
  }

  activeClient = { clientId, response };
  writeEvent(response, { type: 'ready', clientId });

  const keepAlive = setInterval(() => {
    response.write(': keep-alive\n\n');
  }, 15000);

  request.on('close', () => {
    clearInterval(keepAlive);

    if (activeClient?.clientId === clientId) {
      activeClient = null;
      pendingEvents = 0;
    }
  });
});

app.post(
  '/api/commands',
  (request: Request<object, object, ExecuteCommandRequest>, response: Response<CommandResponse>) => {
    if (ensureActiveClient(response)) {
      return;
    }

    const rawCommand = request.body?.command ?? '';
    const command = normalizeLbml(rawCommand);

    if (!validateLbml(command)) {
      response.status(400).json({ error: 'Comando LBML invalido.' } as never);
      return;
    }

    const targetClientId = publish({
      type: 'execute',
      command,
      source: request.body?.source ?? 'http',
      issuedAt: new Date().toISOString(),
    });

    response.json({
      accepted: true,
      command,
      targetClientId,
      source: request.body?.source ?? 'http',
    });
  },
);

app.post(
  '/api/reset',
  (request: Request<object, object, ResetRequest>, response: Response<ResetResponse>) => {
    if (ensureActiveClient(response)) {
      return;
    }

    const targetClientId = publish({
      type: 'reset',
      source: request.body?.source ?? 'http',
      issuedAt: new Date().toISOString(),
    });

    response.json({
      accepted: true,
      targetClientId,
      source: request.body?.source ?? 'http',
    });
  },
);

app.post('/api/state', (request: Request<object, object, ClientStateUpdate>, response) => {
  const { clientId, state } = request.body ?? {};

  if (!clientId || !state) {
    response.status(400).json({ error: 'Payload de estado invalido.' });
    return;
  }

  if (activeClient?.clientId !== clientId) {
    response.status(409).json({ error: 'Cliente nao e a aba ativa.' });
    return;
  }

  lastKnownState = state;
  pendingEvents = 0;
  response.json({ ok: true });
});

app.listen(port, () => {
  console.log(`LBot simulator API listening on http://localhost:${port}`);
});
