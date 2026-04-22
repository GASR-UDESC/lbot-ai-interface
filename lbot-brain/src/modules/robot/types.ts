import type { RobotExecuteInput, ToolExecutionResult } from "../../core/types";

export interface RobotTranslationAdapter {
  translate(command: string): Promise<string>;
}

export interface RobotDispatchReceipt {
  command: string;
  targetClientId: string;
  source: "ui" | "http";
}

export interface RobotCommandDispatcher {
  executeLbml(command: string): Promise<RobotDispatchReceipt>;
}

export interface RobotModule {
  execute(input: RobotExecuteInput): Promise<ToolExecutionResult>;
}
