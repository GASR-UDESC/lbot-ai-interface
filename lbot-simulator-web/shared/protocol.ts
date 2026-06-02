export interface ExecuteCommandRequest {
  command: string;
  source?: 'ui' | 'http';
}

export interface ResetRequest {
  source?: 'ui' | 'http';
}

export interface ApiError {
  error: string;
}

export interface CommandResponse {
  accepted: boolean;
  command: string;
  targetClientId: string;
  source: 'ui' | 'http';
}

export interface ResetResponse {
  accepted: boolean;
  targetClientId: string;
  source: 'ui' | 'http';
}

export interface SimulatorStatusResponse {
  connected: boolean;
  activeClientId: string | null;
  pendingEvents: number;
}

export interface SimulatorStateSnapshot {
  x: number;
  z: number;
  rotation: number;
  currentCommand: string;
  isAnimating: boolean;
  updatedAt: string;
}

export interface SimulatorStateResponse {
  connected: boolean;
  activeClientId: string | null;
  state: SimulatorStateSnapshot | null;
}

export type ServerEvent =
  | {
      type: 'ready';
      clientId: string;
    }
  | {
      type: 'disconnect';
      reason: string;
    }
  | {
      type: 'execute';
      command: string;
      source: 'ui' | 'http';
      issuedAt: string;
    }
  | {
      type: 'reset';
      source: 'ui' | 'http';
      issuedAt: string;
    };

export interface ClientStateUpdate {
  clientId: string;
  state: SimulatorStateSnapshot;
}

export interface ProximityReadings {
  frente: number;
  tras: number;
}

export interface SensorsResponse {
  connected: boolean;
  readings: ProximityReadings | null;
  error?: string;
}

export interface CameraResponse {
  connected: boolean;
  image: string | null;
  format: 'png';
  encoding: 'base64';
  error?: string;
  robotPosition?: { x: number; z: number; rotation: number };
}
