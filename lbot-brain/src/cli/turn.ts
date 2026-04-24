import {
  executePlannedTool,
  prepareTurn,
  type Planner,
  type ToolCallExecutor,
} from "../core/handle-turn";
import type { Session } from "../core/session";
import type { ToolCall, ToolExecutionResult, TurnOutcome, TurnPlan } from "../core/types";

function formatToolErrorMessage(tool: string, summary: string, errorCode?: string): string {
  return `[erro] ${tool}${errorCode ? ` ${errorCode}` : ""}: ${summary}`;
}

function shouldPrintSuccessfulToolResult(tool: string): boolean {
  return tool === "vision.describe";
}

function buildSpokenToolSummary(toolResult: ToolExecutionResult | null): string {
  if (!toolResult) {
    return "";
  }

  if (!toolResult.ok) {
    return toolResult.summary;
  }

  if (shouldPrintSuccessfulToolResult(toolResult.tool)) {
    return toolResult.summary;
  }

  return "";
}

function buildInitialConsoleLines(plan: TurnPlan): string[] {
  return [`lbot> ${plan.assistantText}`];
}

function buildToolConsoleLines(toolResult: ToolExecutionResult | null): string[] {
  if (!toolResult) {
    return [];
  }

  if (!toolResult.ok) {
    return [formatToolErrorMessage(toolResult.tool, toolResult.summary, toolResult.errorCode)];
  }

  if (shouldPrintSuccessfulToolResult(toolResult.tool)) {
    return [`lbot> ${toolResult.summary}`];
  }

  return [];
}

function buildToolSpokenText(toolResult: ToolExecutionResult | null): string {
  return buildSpokenToolSummary(toolResult);
}

export function describeToolProgress(toolCall: ToolCall | null): string | null {
  if (!toolCall) {
    return null;
  }

  switch (toolCall.tool) {
    case "robot.execute":
      return "enviando movimento...";
    case "vision.describe":
      return "processando visao...";
  }
}

export interface ProcessCliTurnInput {
  userText: string;
  session: Session;
  planner: Planner;
  executor: ToolCallExecutor;
}

export interface ProcessedCliTurn {
  outcome: TurnOutcome;
  consoleLines: string[];
  spokenText: string;
}

export interface PreparedCliTurn {
  plan: TurnPlan;
  initialConsoleLines: string[];
  initialSpokenText: string;
  progressMessage: string | null;
}

export interface CompletedCliTurn {
  outcome: TurnOutcome;
  toolConsoleLines: string[];
  toolSpokenText: string;
}

export async function prepareCliTurn(input: ProcessCliTurnInput): Promise<PreparedCliTurn> {
  const plan = await prepareTurn(input);

  return {
    plan,
    initialConsoleLines: buildInitialConsoleLines(plan),
    initialSpokenText: plan.assistantText,
    progressMessage: describeToolProgress(plan.toolCall),
  };
}

export async function completeCliTurn(input: {
  plan: TurnPlan;
  session: Session;
  executor: ToolCallExecutor;
}): Promise<CompletedCliTurn> {
  const toolResult = await executePlannedTool(input);
  const outcome = {
    plan: input.plan,
    toolResult,
  };

  return {
    outcome,
    toolConsoleLines: buildToolConsoleLines(toolResult),
    toolSpokenText: buildToolSpokenText(toolResult),
  };
}

export async function processCliTurn(input: ProcessCliTurnInput): Promise<ProcessedCliTurn> {
  const prepared = await prepareCliTurn(input);
  const completed = await completeCliTurn({
    plan: prepared.plan,
    session: input.session,
    executor: input.executor,
  });
  const spokenText = [prepared.initialSpokenText, completed.toolSpokenText]
    .filter((part) => part.trim())
    .join("\n");

  return {
    outcome: completed.outcome,
    consoleLines: [...prepared.initialConsoleLines, ...completed.toolConsoleLines],
    spokenText,
  };
}

export function formatPlannerError(error: unknown): string {
  return `[erro] planner: ${error instanceof Error ? error.message : String(error)}`;
}

export function spokenPlannerError(): string {
  return "Desculpe, tive um erro ao processar o seu pedido.";
}

export function isExitCommand(text: string): boolean {
  const normalized = text.trim().toLowerCase();
  return normalized === "exit" || normalized === "quit" || normalized === "sair";
}
