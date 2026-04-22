import type { ToolExecutionResult, VisionDescribeInput } from "../../core/types";

export interface CapturedFrame {
  mimeType: string;
  dataUrl: string;
  capturedAt: string;
  source: string;
}

export interface FrameSource {
  captureFrame(): Promise<CapturedFrame>;
}

export class FrameCaptureError extends Error {
  constructor(
    public readonly code: string,
    message: string,
    public readonly data?: unknown,
  ) {
    super(message);
    this.name = "FrameCaptureError";
  }
}

export interface VisionModule {
  describe(input: VisionDescribeInput): Promise<ToolExecutionResult>;
}
