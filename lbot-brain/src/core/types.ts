export const TOOL_NAMES = ["robot.execute", "vision.describe"] as const;

export type ToolName = (typeof TOOL_NAMES)[number];

export type TurnKind = "chat" | "tool" | "clarify" | "refuse";

export interface RobotExecuteInput {
  utteranceRaw: string;
}

export interface VisionDescribeInput {
  utteranceRaw: string;
}

export type ToolCall =
  | {
      tool: "robot.execute";
      input: RobotExecuteInput;
    }
  | {
      tool: "vision.describe";
      input: VisionDescribeInput;
    };

export interface TurnPlan {
  kind: TurnKind;
  assistantText: string;
  toolCall: ToolCall | null;
}

export interface ToolExecutionResult {
  tool: ToolName;
  ok: boolean;
  summary: string;
  data?: unknown;
  errorCode?: string;
  error?: string;
}

export type SessionEvent =
  | {
      type: "user_message";
      text: string;
      at: string;
    }
  | {
      type: "turn_plan";
      plan: TurnPlan;
      at: string;
    }
  | {
      type: "tool_result";
      result: ToolExecutionResult;
      at: string;
    };

export interface TurnOutcome {
  plan: TurnPlan;
  toolResult: ToolExecutionResult | null;
}
