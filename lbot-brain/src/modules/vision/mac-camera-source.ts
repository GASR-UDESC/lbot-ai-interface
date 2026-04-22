import { spawn } from "node:child_process";

import { FrameCaptureError, type CapturedFrame, type FrameSource } from "./types";

interface MacCameraFrameSourceConfig {
  ffmpegBin: string;
  deviceName: string;
  videoSize: string;
  framerate: number;
  timeoutMs: number;
}

function collectOutput(chunks: Buffer[]): Buffer {
  return chunks.length === 1 ? chunks[0] : Buffer.concat(chunks);
}

function normalizeDeviceName(deviceName: string): string {
  const trimmed = deviceName.trim();

  if (!trimmed) {
    throw new FrameCaptureError(
      "CAMERA_DEVICE_NOT_FOUND",
      "Nenhuma camera foi configurada para captura.",
    );
  }

  return trimmed;
}

function inferCameraErrorCode(stderrText: string): string {
  if (/No such file or directory|device not found|could not find|not found/i.test(stderrText)) {
    return "CAMERA_DEVICE_NOT_FOUND";
  }

  if (/permission denied|not authorized|not permitted/i.test(stderrText)) {
    return "CAMERA_PERMISSION_DENIED";
  }

  return "CAMERA_CAPTURE_FAILED";
}

export class MacCameraFrameSource implements FrameSource {
  constructor(private readonly config: MacCameraFrameSourceConfig) {}

  async captureFrame(): Promise<CapturedFrame> {
    const deviceName = normalizeDeviceName(this.config.deviceName);

    return new Promise<CapturedFrame>((resolve, reject) => {
      const stdoutChunks: Buffer[] = [];
      const stderrChunks: Buffer[] = [];
      const args = [
        "-hide_banner",
        "-loglevel",
        "error",
        "-f",
        "avfoundation",
        "-framerate",
        String(this.config.framerate),
        "-video_size",
        this.config.videoSize,
        "-i",
        `${deviceName}:none`,
        "-frames:v",
        "1",
        "-f",
        "image2pipe",
        "-vcodec",
        "mjpeg",
        "pipe:1",
      ];
      const child = spawn(this.config.ffmpegBin, args, {
        stdio: ["ignore", "pipe", "pipe"],
      });

      let settled = false;

      const finish = (callback: () => void) => {
        if (settled) {
          return;
        }

        settled = true;
        callback();
      };

      const timer = setTimeout(() => {
        child.kill("SIGKILL");
        finish(() => {
          reject(
            new FrameCaptureError(
              "CAMERA_CAPTURE_TIMEOUT",
              `A captura da camera demorou mais que ${this.config.timeoutMs} ms.`,
              { deviceName },
            ),
          );
        });
      }, this.config.timeoutMs);

      child.stdout.on("data", (chunk: Buffer) => {
        stdoutChunks.push(chunk);
      });

      child.stderr.on("data", (chunk: Buffer) => {
        stderrChunks.push(chunk);
      });

      child.once("error", (error) => {
        clearTimeout(timer);
        finish(() => {
          const isMissingBinary =
            error instanceof Error && "code" in error && error.code === "ENOENT";

          reject(
            new FrameCaptureError(
              isMissingBinary ? "CAMERA_CAPTURE_TOOL_MISSING" : "CAMERA_CAPTURE_FAILED",
              isMissingBinary
                ? `Nao encontrei o executavel ${this.config.ffmpegBin}. Instale o ffmpeg para habilitar a camera.`
                : `Falha ao iniciar ${this.config.ffmpegBin} para capturar a camera.`,
              {
                deviceName,
                cause: error instanceof Error ? error.message : String(error),
              },
            ),
          );
        });
      });

      child.once("close", (code) => {
        clearTimeout(timer);
        finish(() => {
          const stderrText = collectOutput(stderrChunks).toString("utf8").trim();

          if (code !== 0) {
            const errorCode = inferCameraErrorCode(stderrText);

            reject(
              new FrameCaptureError(
                errorCode,
                errorCode === "CAMERA_DEVICE_NOT_FOUND"
                  ? `Nao encontrei a camera ${deviceName} no macOS.`
                  : errorCode === "CAMERA_PERMISSION_DENIED"
                    ? `O macOS bloqueou o acesso a camera ${deviceName}.`
                    : `Nao consegui capturar uma imagem da camera ${deviceName}.`,
                {
                  deviceName,
                  ffmpegExitCode: code,
                  stderr: stderrText,
                },
              ),
            );
            return;
          }

          const imageBuffer = collectOutput(stdoutChunks);

          if (imageBuffer.length === 0) {
            reject(
              new FrameCaptureError(
                "CAMERA_CAPTURE_EMPTY",
                `A camera ${deviceName} nao retornou nenhuma imagem.`,
                {
                  deviceName,
                  stderr: stderrText,
                },
              ),
            );
            return;
          }

          resolve({
            mimeType: "image/jpeg",
            dataUrl: `data:image/jpeg;base64,${imageBuffer.toString("base64")}`,
            capturedAt: new Date().toISOString(),
            source: `mac-camera:${deviceName}`,
          });
        });
      });
    });
  }
}

export function createMacCameraFrameSource(
  config: MacCameraFrameSourceConfig,
): FrameSource {
  return new MacCameraFrameSource(config);
}
