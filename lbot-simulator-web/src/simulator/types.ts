export interface RobotState {
  x: number;
  z: number;
  rotation: number;
  isAnimating: boolean;
}

export interface SimulatorSnapshot extends RobotState {
  currentCommand: string;
}

export interface StatusMessage {
  kind: 'idle' | 'info' | 'error';
  text: string;
}
