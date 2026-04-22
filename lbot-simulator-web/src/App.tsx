import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { parseLbmlSequence } from '../shared/lbml.js';
import type { ServerEvent } from '../shared/protocol.js';
import { CommandPanel } from './components/CommandPanel.js';
import { SimulatorCanvas, type SimulatorCanvasHandle } from './components/SimulatorCanvas.js';
import { StatusPanel } from './components/StatusPanel.js';
import { getState, getStatus, pushState, sendCommand, sendReset } from './lib/api.js';
import { connectToServerEvents, type EventConnection } from './lib/events.js';
import type { SimulatorSnapshot, StatusMessage } from './simulator/types.js';

const DEFAULT_COMMAND = 'D40F;R90L;D20F;';

const INITIAL_SNAPSHOT: SimulatorSnapshot = {
  x: 0,
  z: 0,
  rotation: 0,
  isAnimating: false,
  currentCommand: '-',
};

export default function App() {
  const simulatorHandleRef = useRef<SimulatorCanvasHandle | null>(null);
  const clientIdRef = useRef<string | null>(null);
  const eventConnectionRef = useRef<EventConnection | null>(null);
  const eventQueueRef = useRef<Promise<void>>(Promise.resolve());

  const [command, setCommand] = useState(DEFAULT_COMMAND);
  const [history, setHistory] = useState<string[]>([]);
  const [connected, setConnected] = useState(false);
  const [serverStateSummary, setServerStateSummary] = useState('Aguardando conexao com a API');
  const [cameraModeLabel, setCameraModeLabel] = useState('3a Pessoa');
  const [snapshot, setSnapshot] = useState<SimulatorSnapshot>(INITIAL_SNAPSHOT);
  const [message, setMessage] = useState<StatusMessage>({
    kind: 'idle',
    text: 'Conecte a UI para aceitar comandos via HTTP e via painel local.',
  });

  const syncState = useCallback(async () => {
    const clientId = clientIdRef.current;
    const handle = simulatorHandleRef.current;

    if (!clientId || !handle) {
      return;
    }

    try {
      await pushState(clientId, handle.getSnapshot());
    } catch {
      // Ignore transient sync failures while reconnecting.
    }
  }, []);

  const refreshServerSummary = useCallback(async () => {
    try {
      const [status, state] = await Promise.all([getStatus(), getState()]);
      setConnected(status.connected);
      setServerStateSummary(
        status.connected
          ? `Cliente ativo ${status.activeClientId ?? '-'} | fila ${status.pendingEvents}`
          : 'Nenhuma aba ativa conectada',
      );

      const nextState = state.state;

      if (nextState) {
        setSnapshot((current) => ({
          ...current,
          x: nextState.x,
          z: nextState.z,
          rotation: nextState.rotation,
          isAnimating: nextState.isAnimating,
          currentCommand: nextState.currentCommand,
        }));
      }
    } catch {
      setConnected(false);
      setServerStateSummary('API indisponivel');
    }
  }, []);

  const addHistory = useCallback((entry: string) => {
    setHistory((current) => [entry, ...current].slice(0, 10));
  }, []);

  const runCommandFromServer = useCallback(
    async (event: ServerEvent) => {
      const handle = simulatorHandleRef.current;
      if (!handle) {
        return;
      }

      if (event.type === 'ready') {
        clientIdRef.current = event.clientId;
        setConnected(true);
        setMessage({ kind: 'info', text: 'UI conectada. Esta aba agora aceita comandos HTTP.' });
        await syncState();
        await refreshServerSummary();
        return;
      }

      const result = await handle.handleRemoteEvent(event);

      if (event.type === 'execute') {
        addHistory(`${event.source.toUpperCase()}: ${event.command}`);
      }

      if (result) {
        setMessage(result);
      }

      if (event.type === 'disconnect') {
        setConnected(false);
        clientIdRef.current = null;
        eventConnectionRef.current?.close();
        eventConnectionRef.current = null;
      }

      await syncState();
      await refreshServerSummary();
    },
    [addHistory, refreshServerSummary, syncState],
  );

  const enqueueServerEvent = useCallback(
    (event: ServerEvent) => {
      eventQueueRef.current = eventQueueRef.current
        .then(async () => {
          await runCommandFromServer(event);
        })
        .catch(() => {
          setMessage({ kind: 'error', text: 'Falha ao processar evento do servidor.' });
        });
    },
    [runCommandFromServer],
  );

  const handleCanvasReady = useCallback(
    (handle: SimulatorCanvasHandle) => {
      simulatorHandleRef.current = handle;
      void syncState();
    },
    [syncState],
  );

  const handleSnapshotChange = useCallback((nextSnapshot: SimulatorSnapshot) => {
    setSnapshot(nextSnapshot);
  }, []);

  useEffect(() => {
    refreshServerSummary();

    const connection = connectToServerEvents({
      onEvent(event) {
        enqueueServerEvent(event);
      },
      onError() {
        setConnected(false);
        setServerStateSummary('Conexao com eventos perdida');
      },
    });

    eventConnectionRef.current = connection;

    return () => {
      connection.close();
      eventConnectionRef.current = null;
    };
  }, [enqueueServerEvent, refreshServerSummary]);

  useEffect(() => {
    const interval = window.setInterval(() => {
      void refreshServerSummary();
      void syncState();
    }, 2000);

    return () => window.clearInterval(interval);
  }, [refreshServerSummary, syncState]);

  const executeLocally = useCallback(async () => {
    if (!parseLbmlSequence(command)) {
      setMessage({ kind: 'error', text: 'Comando LBML invalido.' });
      return;
    }

    try {
      const response = await sendCommand(command, 'ui');
      addHistory(`UI: ${response.command}`);
      setMessage({ kind: 'info', text: 'Comando enviado para execucao.' });
      await refreshServerSummary();
    } catch (error) {
      setMessage({ kind: 'error', text: toMessage(error) });
    }
  }, [addHistory, command, refreshServerSummary]);

  const resetSimulator = useCallback(async () => {
    try {
      await sendReset('ui');
      setMessage({ kind: 'info', text: 'Reset solicitado.' });
      await refreshServerSummary();
    } catch (error) {
      setMessage({ kind: 'error', text: toMessage(error) });
    }
  }, [refreshServerSummary]);

  const toggleCamera = useCallback(() => {
    const handle = simulatorHandleRef.current;

    if (!handle) {
      return;
    }

    const enabled = handle.toggleCamera();
    setCameraModeLabel(enabled ? 'Vista Normal' : '3a Pessoa');
  }, []);

  const layoutTitle = useMemo(() => 'LBot Simulator Web', []);

  return (
    <div className="app-shell">
      <header className="hero">
        <div>
          <p className="eyebrow">Standalone simulator</p>
          <h1>{layoutTitle}</h1>
          <p className="hero-copy">
            Simulador React para executar LBML pela interface web ou via HTTP, controlando a aba ativa em tempo real.
          </p>
        </div>

        <div className="hero-callout">
          <span className="callout-label">HTTP</span>
          <code>POST /api/commands</code>
          <code>POST /api/reset</code>
        </div>
      </header>

      <main className="layout-grid">
        <section className="left-column">
          <StatusPanel
            connected={connected}
            snapshot={snapshot}
            serverStateSummary={serverStateSummary}
            message={message}
          />

          <CommandPanel
            value={command}
            onChange={setCommand}
            onExecute={() => void executeLocally()}
            onReset={() => void resetSimulator()}
            onToggleCamera={toggleCamera}
            isExecuting={snapshot.isAnimating}
            cameraModeLabel={cameraModeLabel}
            history={history}
          />
        </section>

        <section className="canvas-column">
          <SimulatorCanvas
            onReady={handleCanvasReady}
            onSnapshotChange={handleSnapshotChange}
          />
        </section>
      </main>
    </div>
  );
}

function toMessage(error: unknown): string {
  if (error instanceof Error) {
    return error.message;
  }

  return 'Falha inesperada.';
}
