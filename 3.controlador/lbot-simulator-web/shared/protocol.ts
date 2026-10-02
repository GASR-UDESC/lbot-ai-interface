import type { ArenaObject } from "./arena-objects.js";
export type CommandStatus =
  | "accepted"
  | "running"
  | "completed"
  | "blocked"
  | "cancelled"
  | "failed"
  | "timed_out";
export interface ExecuteCommandRequest {
  command: string;
  command_id?: string;
  session_id?: string;
  source?: "ui" | "http";
}
export interface ResetRequest {
  source?: "ui" | "http";
}
export interface ApiError {
  error: string;
}
export interface CommandResponse {
  accepted: boolean;
  command: string;
  command_id: string;
  session_id: string;
  status: CommandStatus;
  source: "ui" | "http";
  reason?: string;
  distance_cm: number;
  rotation_degrees: number;
  revision: number;
}
export interface ResetResponse {
  accepted: boolean;
  session_id: string;
  source: "ui" | "http";
}
export interface SimulatorStatusResponse {
  connected: boolean;
  activeClientId: string | null;
  pendingEvents: number;
  session_id: string;
  operation: CommandResponse | null;
}
export interface SimulatorStateSnapshot {
  x: number;
  z: number;
  rotation: number;
  currentCommand: string;
  isAnimating: boolean;
  updatedAt: string;
  session_id: string;
  revision: number;
  operation: CommandResponse | null;
}
export interface SimulatorStateResponse {
  connected: boolean;
  activeClientId: string | null;
  state: SimulatorStateSnapshot;
}
export type ServerEvent =
  | { type: "ready"; clientId: string }
  | { type: "state"; state: SimulatorStateSnapshot }
  | { type: "scene"; objects: ArenaObject[] }
  | { type: "disconnect"; reason: string };
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
  session_id: string;
  revision: number;
  captured_at: string;
  validity: {
    frente: "valid" | "out_of_range" | "unavailable";
    tras: "valid" | "out_of_range" | "unavailable";
  };
}
export interface CameraResponse {
  connected: boolean;
  image: string | null;
  format: "png";
  encoding: "base64";
  renderMethod?: "webgl";
  error?: string;
  frame_id: string;
  session_id: string;
  revision: number;
  captured_at: string;
  range_projection?: { origin_cm: number[]; direction: number[] };
  intrinsics: {
    width: number;
    height: number;
    fx: number;
    fy: number;
    cx: number;
    cy: number;
  };
}
