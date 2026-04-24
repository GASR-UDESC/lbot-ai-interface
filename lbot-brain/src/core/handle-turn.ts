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

export async function prepareTurn(input: {
  userText: string;
  session: Session;
  planner: Planner;
}): Promise<TurnPlan> {
  const { userText, session, planner } = input;

  session.recordUserMessage(userText);

  const plannedTurn = await planner.planTurn({
    userText,
    sessionEvents: session.snapshot(),
  });

  const plan = coerceTurnPlan(plannedTurn, userText);
  session.recordTurnPlan(plan);
  return plan;
}

export async function executePlannedTool(input: {
  plan: TurnPlan;
  session: Session;
  executor: ToolCallExecutor;
}): Promise<ToolExecutionResult | null> {
  const { plan, session, executor } = input;

  if (!plan.toolCall) {
    return null;
  }

  const toolResult = await executor.execute(plan.toolCall);
  session.recordToolResult(toolResult);
  return toolResult;
}

export async function handleTurn(input: {
  userText: string;
  session: Session;
  planner: Planner;
  executor: ToolCallExecutor;
}): Promise<TurnOutcome> {
  const plan = await prepareTurn(input);
  const toolResult = await executePlannedTool({
    plan,
    session: input.session,
    executor: input.executor,
  });

  return {
    plan,
    toolResult,
  };
}
