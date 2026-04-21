import { createInterface } from "node:readline/promises";
import { stdin as input, stdout as output } from "node:process";

import { loadAppConfig } from "../config";
import { handleTurn } from "../core/handle-turn";
import { Session } from "../core/session";
import { LmStudioClient } from "../llm/lm-studio-client";
import { LlmPlanner } from "../llm/planner";
import { ToolExecutor } from "../runtime/executor";
import { createStubToolRegistry } from "../runtime/registry";

function formatToolErrorMessage(tool: string, summary: string, errorCode?: string): string {
  return `[erro] ${tool}${errorCode ? ` ${errorCode}` : ""}: ${summary}`;
}

export async function runCli(): Promise<void> {
  const config = loadAppConfig();
  const session = new Session();
  const planner = new LlmPlanner(
    new LmStudioClient({
      baseURL: config.lmStudioBaseUrl,
      apiKey: config.lmStudioApiKey,
      model: config.model,
      temperature: config.plannerTemperature,
      maxTokens: config.plannerMaxTokens,
    }),
  );
  const executor = new ToolExecutor(createStubToolRegistry());
  const rl = createInterface({ input, output });

  console.log("lbot> Cerebro online. Digite 'exit' para sair.");

  try {
    while (true) {
      const userText = (await rl.question("voce> ")).trim();

      if (!userText) {
        continue;
      }

      if (userText === "exit" || userText === "quit") {
        break;
      }

      try {
        const outcome = await handleTurn({
          userText,
          session,
          planner,
          executor,
        });

        console.log(`lbot> ${outcome.plan.assistantText}`);

        if (outcome.toolResult && !outcome.toolResult.ok) {
          console.log(
            formatToolErrorMessage(
              outcome.toolResult.tool,
              outcome.toolResult.summary,
              outcome.toolResult.errorCode,
            ),
          );
        }
      } catch (error) {
        console.log(
          `[erro] planner: ${error instanceof Error ? error.message : String(error)}`,
        );
      }
    }
  } finally {
    rl.close();
  }
}
