import { spawn, type ChildProcessWithoutNullStreams } from "node:child_process";

import type { RobotTranslationAdapter } from "./types";

export interface LbotV7ProcessTranslatorConfig {
  pythonBin: string;
  bridgeScriptPath: string;
  translatorScriptPath: string;
  modelPath: string;
}

interface PendingRequest {
  resolve: (value: string) => void;
  reject: (error: Error) => void;
}

interface TranslatorResponse {
  id?: string;
  ok?: boolean;
  lbml?: string;
  error?: string;
}

function trimBuffer(buffer: string, maxLength = 4000): string {
  if (buffer.length <= maxLength) {
    return buffer;
  }

  return buffer.slice(-maxLength);
}

export class LbotV7ProcessTranslator implements RobotTranslationAdapter {
  private child: ChildProcessWithoutNullStreams | null = null;
  private stdoutBuffer = "";
  private stderrBuffer = "";
  private nextRequestId = 0;
  private readonly pending = new Map<string, PendingRequest>();

  constructor(private readonly config: LbotV7ProcessTranslatorConfig) {}

  async translate(command: string): Promise<string> {
    const normalized = command.trim();

    if (!normalized) {
      throw new Error("Robot command is empty.");
    }

    const child = this.ensureProcess();
    const id = String(++this.nextRequestId);

    return await new Promise<string>((resolve, reject) => {
      this.pending.set(id, { resolve, reject });
      child.stdin.write(`${JSON.stringify({ id, command: normalized })}\n`, (error) => {
        if (!error) {
          return;
        }

        this.pending.delete(id);
        reject(new Error(`Failed to write to translator process: ${error.message}`));
      });
    });
  }

  dispose(): void {
    const child = this.child;

    if (!child) {
      return;
    }

    const pendingRequests = [...this.pending.values()];
    this.pending.clear();

    for (const pending of pendingRequests) {
      pending.reject(new Error("Translator process was disposed."));
    }

    child.stdout.removeAllListeners();
    child.stderr.removeAllListeners();
    child.removeAllListeners();

    child.stdin.end();
    child.kill();
    this.child = null;
  }

  private ensureProcess(): ChildProcessWithoutNullStreams {
    if (this.child && this.child.exitCode === null && !this.child.killed) {
      return this.child;
    }

    this.stdoutBuffer = "";
    this.stderrBuffer = "";

    const child = spawn(
      this.config.pythonBin,
      [
        "-u",
        this.config.bridgeScriptPath,
        "--translator-script",
        this.config.translatorScriptPath,
        "--model",
        this.config.modelPath,
      ],
      {
        stdio: ["pipe", "pipe", "pipe"],
      },
    );

    child.stdout.setEncoding("utf8");
    child.stderr.setEncoding("utf8");

    child.stdout.on("data", (chunk: string) => {
      this.handleStdout(chunk);
    });

    child.stderr.on("data", (chunk: string) => {
      this.stderrBuffer = trimBuffer(`${this.stderrBuffer}${chunk}`);
    });

    child.on("error", (error) => {
      this.failProcess(new Error(`Failed to start translator process: ${error.message}`));
    });

    child.on("exit", (code, signal) => {
      this.failProcess(new Error(this.buildExitMessage(code, signal)));
    });

    this.child = child;
    return child;
  }

  private handleStdout(chunk: string): void {
    this.stdoutBuffer += chunk;

    while (true) {
      const newlineIndex = this.stdoutBuffer.indexOf("\n");

      if (newlineIndex === -1) {
        return;
      }

      const line = this.stdoutBuffer.slice(0, newlineIndex).trim();
      this.stdoutBuffer = this.stdoutBuffer.slice(newlineIndex + 1);

      if (!line) {
        continue;
      }

      let payload: TranslatorResponse;

      try {
        payload = JSON.parse(line) as TranslatorResponse;
      } catch {
        continue;
      }

      if (!payload.id) {
        continue;
      }

      const pending = this.pending.get(payload.id);

      if (!pending) {
        continue;
      }

      this.pending.delete(payload.id);

      if (payload.ok && typeof payload.lbml === "string") {
        pending.resolve(payload.lbml);
        continue;
      }

      pending.reject(new Error(payload.error ?? "Translator request failed."));
    }
  }

  private buildExitMessage(code: number | null, signal: NodeJS.Signals | null): string {
    const reason = code !== null ? `code ${code}` : `signal ${signal ?? "unknown"}`;
    const stderr = this.stderrBuffer.trim();

    if (!stderr) {
      return `Translator process exited with ${reason}.`;
    }

    return `Translator process exited with ${reason}: ${stderr}`;
  }

  private failProcess(error: Error): void {
    const pendingRequests = [...this.pending.values()];
    this.pending.clear();

    if (this.child) {
      this.child.stdout.removeAllListeners();
      this.child.stderr.removeAllListeners();
      this.child.removeAllListeners();
      this.child = null;
    }

    for (const pending of pendingRequests) {
      pending.reject(error);
    }
  }
}
