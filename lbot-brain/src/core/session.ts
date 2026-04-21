import { randomUUID } from "node:crypto";

import type { SessionEvent, ToolExecutionResult, TurnPlan } from "./types";

export class Session {
  private readonly events: SessionEvent[] = [];

  readonly id = randomUUID();

  recordUserMessage(text: string): void {
    this.events.push({
      type: "user_message",
      text,
      at: new Date().toISOString(),
    });
  }

  recordTurnPlan(plan: TurnPlan): void {
    this.events.push({
      type: "turn_plan",
      plan,
      at: new Date().toISOString(),
    });
  }

  recordToolResult(result: ToolExecutionResult): void {
    this.events.push({
      type: "tool_result",
      result,
      at: new Date().toISOString(),
    });
  }

  snapshot(limit = 50): readonly SessionEvent[] {
    return this.events.slice(-limit);
  }
}
