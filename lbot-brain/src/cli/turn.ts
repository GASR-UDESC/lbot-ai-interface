import { handleTurn, type Planner, type ToolCallExecutor } from "../core/handle-turn";
import type { Session } from "../core/session";
import type { ToolExecutionResult, TurnOutcome } from "../core/types";

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

function buildConsoleLines(outcome: TurnOutcome): string[] {
  const lines = [`lbot> ${outcome.plan.assistantText}`];

  if (outcome.toolResult && !outcome.toolResult.ok) {
    lines.push(
      formatToolErrorMessage(
        outcome.toolResult.tool,
        outcome.toolResult.summary,
        outcome.toolResult.errorCode,
      ),
    );
  } else if (
    outcome.toolResult &&
    shouldPrintSuccessfulToolResult(outcome.toolResult.tool)
  ) {
    lines.push(`lbot> ${outcome.toolResult.summary}`);
  }

  return lines;
}

function buildSpokenText(outcome: TurnOutcome): string {
  const toolSummary = buildSpokenToolSummary(outcome.toolResult);

  if (!toolSummary) {
    return outcome.plan.assistantText;
  }

  return `${outcome.plan.assistantText}\n${toolSummary}`;
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

export async function processCliTurn(input: ProcessCliTurnInput): Promise<ProcessedCliTurn> {
  const outcome = await handleTurn(input);

  return {
    outcome,
    consoleLines: buildConsoleLines(outcome),
    spokenText: buildSpokenText(outcome),
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
