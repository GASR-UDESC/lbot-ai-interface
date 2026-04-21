import type { ToolExecutionResult } from "../../core/types";
import type { VisionModule } from "./types";

export function createVisionStub(): VisionModule {
  return {
    async describe(): Promise<ToolExecutionResult> {
      return {
        tool: "vision.describe",
        ok: false,
        summary: "Vision module not implemented yet.",
        errorCode: "NOT_IMPLEMENTED",
        error: "Replace the vision stub with the real module.",
      };
    },
  };
}
