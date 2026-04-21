import type { ToolCall, ToolExecutionResult } from "../core/types";
import type { ToolRegistry } from "./registry";

export class ToolExecutor {
  constructor(private readonly registry: ToolRegistry) {}

  async execute(toolCall: ToolCall): Promise<ToolExecutionResult> {
    try {
      switch (toolCall.tool) {
        case "robot.execute":
          return await this.registry.robot.execute(toolCall.input);
        case "vision.describe":
          return await this.registry.vision.describe(toolCall.input);
      }
    } catch (error) {
      return {
        tool: toolCall.tool,
        ok: false,
        summary: "Tool execution failed.",
        errorCode: "EXECUTION_ERROR",
        error: error instanceof Error ? error.message : String(error),
      };
    }
  }
}
