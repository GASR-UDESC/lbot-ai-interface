import type { SimulatorSnapshot, StatusMessage } from '../simulator/types.js';

interface StatusPanelProps {
  connected: boolean;
  snapshot: SimulatorSnapshot;
  serverStateSummary: string;
  message: StatusMessage;
}

export function StatusPanel({ connected, snapshot, serverStateSummary, message }: StatusPanelProps) {
  return (
    <div className="status-card">
      <div className="status-card__header">
        <h2>Status</h2>
        <span className={connected ? 'badge badge--connected' : 'badge badge--disconnected'}>
          {connected ? 'Conectado' : 'Desconectado'}
        </span>
      </div>

      <div className="status-grid">
        <StatusRow label="Posicao X" value={snapshot.x.toFixed(1)} />
        <StatusRow label="Posicao Z" value={snapshot.z.toFixed(1)} />
        <StatusRow label="Rotacao" value={`${Math.round(snapshot.rotation)}°`} />
        <StatusRow label="Comando" value={snapshot.currentCommand} />
        <StatusRow label="Servidor" value={serverStateSummary} />
      </div>

      <p className={`status-message status-message--${message.kind}`}>{message.text}</p>
    </div>
  );
}

function StatusRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="status-row">
      <span className="status-row__label">{label}</span>
      <span className="status-row__value">{value}</span>
    </div>
  );
}
