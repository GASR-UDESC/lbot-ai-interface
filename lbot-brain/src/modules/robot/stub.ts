import type { ToolExecutionResult } from "../../core/types";
import type { RobotModule } from "./types";

export function createRobotStub(): RobotModule {
  return {
    async execute(): Promise<ToolExecutionResult> {
      return {
        tool: "robot.execute",
        ok: false,
        summary: "Robot module not implemented yet.",
        errorCode: "NOT_IMPLEMENTED",
        error: "Replace the robot stub with the real module.",
      };
    },
  };
}
