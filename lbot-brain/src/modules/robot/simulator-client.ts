import type { RobotCommandDispatcher, RobotDispatchReceipt } from "./types";

export interface SimulatorClientConfig {
  baseUrl: string;
}

interface CommandResponsePayload {
  accepted?: boolean;
  command?: string;
  targetClientId?: string;
  source?: "ui" | "http";
  error?: string;
}

export class SimulatorHttpError extends Error {
  constructor(
    public readonly status: number,
    message: string,
  ) {
    super(message);
    this.name = "SimulatorHttpError";
  }
}

export class SimulatorClient implements RobotCommandDispatcher {
  constructor(private readonly config: SimulatorClientConfig) {}

  async executeLbml(command: string): Promise<RobotDispatchReceipt> {
    const response = await fetch(`${this.config.baseUrl}/api/commands`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        command,
        source: "http",
      }),
    });

    const payload = (await response.json().catch(() => null)) as CommandResponsePayload | null;

    if (!response.ok) {
      throw new SimulatorHttpError(
        response.status,
        payload?.error ?? `Simulator request failed (${response.status}).`,
      );
    }

    return {
      command: typeof payload?.command === "string" ? payload.command : command,
      targetClientId:
        typeof payload?.targetClientId === "string" ? payload.targetClientId : "unknown",
      source: payload?.source === "ui" ? "ui" : "http",
    };
  }
}

export function createSimulatorClient(config: SimulatorClientConfig): RobotCommandDispatcher {
  return new SimulatorClient(config);
}
