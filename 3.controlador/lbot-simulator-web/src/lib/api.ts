import type {
  CameraResponse,
  CommandResponse,
  ExecuteCommandRequest,
  ResetRequest,
  ResetResponse,
  SimulatorStateSnapshot,
  SimulatorStateResponse,
  SimulatorStatusResponse,
} from '../../shared/protocol.js';

async function parseJson<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const payload = (await response.json().catch(() => null)) as { error?: string } | null;
    throw new Error(payload?.error ?? 'Falha na requisicao HTTP.');
  }

  return (await response.json()) as T;
}

export async function sendCommand(command: string, source: ExecuteCommandRequest['source']): Promise<CommandResponse> {
  const response = await fetch('/api/commands', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ command, source } satisfies ExecuteCommandRequest),
  });

  return parseJson<CommandResponse>(response);
}

export async function sendReset(source: ResetRequest['source']): Promise<ResetResponse> {
  const response = await fetch('/api/reset', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ source } satisfies ResetRequest),
  });

  return parseJson<ResetResponse>(response);
}

export async function getStatus(): Promise<SimulatorStatusResponse> {
  const response = await fetch('/api/status');
  return parseJson<SimulatorStatusResponse>(response);
}

export async function getState(): Promise<SimulatorStateResponse> {
  const response = await fetch('/api/state');
  return parseJson<SimulatorStateResponse>(response);
}

export async function getCamera(): Promise<CameraResponse> {
  const response = await fetch('/api/camera');
  return parseJson<CameraResponse>(response);
}

export async function pushState(clientId: string, state: SimulatorStateSnapshot): Promise<void> {
  const response = await fetch('/api/state', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ clientId, state }),
  });

  if (!response.ok) {
    const payload = (await response.json().catch(() => null)) as { error?: string } | null;
    throw new Error(payload?.error ?? 'Falha ao atualizar estado do simulador.');
  }
}
