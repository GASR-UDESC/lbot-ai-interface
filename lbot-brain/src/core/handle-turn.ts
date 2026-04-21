import { coerceTurnPlan } from "./plan";
import type { Session } from "./session";
import type {
  SessionEvent,
  ToolCall,
  ToolExecutionResult,
  TurnOutcome,
  TurnPlan,
} from "./types";

export interface Planner {
  planTurn(input: {
    userText: string;
    sessionEvents: readonly SessionEvent[];
  }): Promise<TurnPlan>;
}

export interface ToolCallExecutor {
  execute(toolCall: ToolCall): Promise<ToolExecutionResult>;
}

export async function handleTurn(input: {
  userText: string;
  session: Session;
  planner: Planner;
  executor: ToolCallExecutor;
}): Promise<TurnOutcome> {
  const { userText, session, planner, executor } = input;

  session.recordUserMessage(userText);

  const plannedTurn = await planner.planTurn({
    userText,
    sessionEvents: session.snapshot(),
  });

  const plan = coerceTurnPlan(plannedTurn, userText);
  session.recordTurnPlan(plan);

  if (!plan.toolCall) {
    return {
      plan,
      toolResult: null,
    };
  }

  const toolResult = await executor.execute(plan.toolCall);
  session.recordToolResult(toolResult);

  return {
    plan,
    toolResult,
  };
}
