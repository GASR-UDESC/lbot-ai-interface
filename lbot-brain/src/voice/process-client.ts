import { spawn, type ChildProcessWithoutNullStreams } from "node:child_process";

export interface VoiceBridgeClientConfig {
  pythonBin: string;
  bridgeScriptPath: string;
  sttModel: string;
  sttLanguage: string;
  sttDevice: string;
  sttComputeType: string;
  sttStartTimeoutMs: number;
  sttSilenceMs: number;
  sttMaxUtteranceMs: number;
  sttVadMode: number;
  sttPrerollMs: number;
  audioInputDevice: string;
  audioOutputDevice: string;
  ttsModelPath: string;
  ttsSpeaker: string;
  ttsLengthScale: number | null;
  ttsNoiseScale: number | null;
  ttsNoiseWScale: number | null;
  ttsVolume: number | null;
}

interface PendingRequest<T> {
  resolve: (value: T) => void;
  reject: (error: Error) => void;
}

interface VoiceBridgeResponse {
  id?: string;
  ok?: boolean;
  transcript?: string;
  timedOut?: boolean;
  heardSpeech?: boolean;
  error?: string;
  errorCode?: string;
}

interface ListenRequestResponse {
  transcript: string;
  timedOut: boolean;
  heardSpeech: boolean;
}

function trimBuffer(buffer: string, maxLength = 4000): string {
  if (buffer.length <= maxLength) {
    return buffer;
  }

  return buffer.slice(-maxLength);
}

function withOptionalArg(args: string[], flag: string, value: string): void {
  if (!value.trim()) {
    return;
  }

  args.push(flag, value);
}

function withOptionalNumberArg(args: string[], flag: string, value: number | null): void {
  if (value === null) {
    return;
  }

  args.push(flag, String(value));
}

export class VoiceBridgeProcessClient {
  private child: ChildProcessWithoutNullStreams | null = null;
  private stdoutBuffer = "";
  private stderrBuffer = "";
  private nextRequestId = 0;
  private readonly pending = new Map<string, PendingRequest<VoiceBridgeResponse>>();

  constructor(private readonly config: VoiceBridgeClientConfig) {}

  async listenOnce(): Promise<ListenRequestResponse> {
    const response = await this.request({ type: "listen_once" });

    return {
      transcript: response.transcript ?? "",
      timedOut: response.timedOut === true,
      heardSpeech: response.heardSpeech === true,
    };
  }

  async speak(text: string): Promise<void> {
    const normalized = text.trim();

    if (!normalized) {
      return;
    }

    await this.request({
      type: "speak",
      text: normalized,
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
      pending.reject(new Error("Voice bridge process was disposed."));
    }

    child.stdout.removeAllListeners();
    child.stderr.removeAllListeners();
    child.removeAllListeners();

    child.stdin.end();
    child.kill();
    this.child = null;
  }

  private async request(payload: Record<string, unknown>): Promise<VoiceBridgeResponse> {
    const child = this.ensureProcess();
    const id = String(++this.nextRequestId);

    return await new Promise<VoiceBridgeResponse>((resolve, reject) => {
      this.pending.set(id, { resolve, reject });
      child.stdin.write(`${JSON.stringify({ id, ...payload })}\n`, (error) => {
        if (!error) {
          return;
        }

        this.pending.delete(id);
        reject(new Error(`Failed to write to voice bridge process: ${error.message}`));
      });
    });
  }

  private ensureProcess(): ChildProcessWithoutNullStreams {
    if (this.child && this.child.exitCode === null && !this.child.killed) {
      return this.child;
    }

    this.stdoutBuffer = "";
    this.stderrBuffer = "";

    const args = [
      "-u",
      this.config.bridgeScriptPath,
      "--stt-model",
      this.config.sttModel,
      "--stt-language",
      this.config.sttLanguage,
      "--stt-device",
      this.config.sttDevice,
      "--stt-compute-type",
      this.config.sttComputeType,
      "--stt-start-timeout-ms",
      String(this.config.sttStartTimeoutMs),
      "--stt-silence-ms",
      String(this.config.sttSilenceMs),
      "--stt-max-utterance-ms",
      String(this.config.sttMaxUtteranceMs),
      "--stt-vad-mode",
      String(this.config.sttVadMode),
      "--stt-preroll-ms",
      String(this.config.sttPrerollMs),
      "--tts-model",
      this.config.ttsModelPath,
    ];

    withOptionalArg(args, "--audio-input-device", this.config.audioInputDevice);
    withOptionalArg(args, "--audio-output-device", this.config.audioOutputDevice);
    withOptionalArg(args, "--tts-speaker", this.config.ttsSpeaker);
    withOptionalNumberArg(args, "--tts-length-scale", this.config.ttsLengthScale);
    withOptionalNumberArg(args, "--tts-noise-scale", this.config.ttsNoiseScale);
    withOptionalNumberArg(args, "--tts-noise-w-scale", this.config.ttsNoiseWScale);
    withOptionalNumberArg(args, "--tts-volume", this.config.ttsVolume);

    const child = spawn(this.config.pythonBin, args, {
      stdio: ["pipe", "pipe", "pipe"],
    });

    child.stdout.setEncoding("utf8");
    child.stderr.setEncoding("utf8");

    child.stdout.on("data", (chunk: string) => {
      this.handleStdout(chunk);
    });

    child.stderr.on("data", (chunk: string) => {
      this.stderrBuffer = trimBuffer(`${this.stderrBuffer}${chunk}`);
    });

    child.on("error", (error) => {
      this.failProcess(new Error(`Failed to start voice bridge process: ${error.message}`));
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

      let payload: VoiceBridgeResponse;

      try {
        payload = JSON.parse(line) as VoiceBridgeResponse;
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

      if (payload.ok) {
        pending.resolve(payload);
        continue;
      }

      pending.reject(new Error(payload.error ?? payload.errorCode ?? "Voice bridge request failed."));
    }
  }

  private buildExitMessage(code: number | null, signal: NodeJS.Signals | null): string {
    const reason = code !== null ? `code ${code}` : `signal ${signal ?? "unknown"}`;
    const stderr = this.stderrBuffer.trim();

    if (!stderr) {
      return `Voice bridge process exited with ${reason}.`;
    }

    return `Voice bridge process exited with ${reason}: ${stderr}`;
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
