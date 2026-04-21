import type { RobotExecuteInput, ToolExecutionResult } from "../../core/types";

export interface RobotModule {
  execute(input: RobotExecuteInput): Promise<ToolExecutionResult>;
}
