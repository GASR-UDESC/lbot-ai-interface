import { createInterface } from "node:readline/promises";
import { stdin as input, stdout as output } from "node:process";

import { createCliRuntime, type CliRuntime } from "./runtime";
import { createProcessingFeedback, type ProcessingFeedback } from "./processing-feedback";
import {
  completeCliTurn,
  formatPlannerError,
  isExitCommand,
  prepareCliTurn,
} from "./turn";

export async function runTextCli(
  runtime: CliRuntime = createCliRuntime(),
  feedback: ProcessingFeedback = createProcessingFeedback(),
): Promise<void> {
  const rl = createInterface({ input, output });

  console.log("lbot> Cerebro online. Digite 'exit' para sair.");

  try {
    while (true) {
      const userText = (await rl.question("voce> ")).trim();

      if (!userText) {
        continue;
      }

      if (isExitCommand(userText)) {
        break;
      }

      try {
        const prepared = await prepareCliTurn({
          userText,
          session: runtime.session,
          planner: runtime.planner,
          executor: runtime.executor,
        });

        for (const line of prepared.initialConsoleLines) {
          console.log(line);
        }

        let completed;

        if (prepared.plan.toolCall) {
          const stopFeedback = feedback.start(prepared.progressMessage ?? "processando...");

          try {
            completed = await completeCliTurn({
              plan: prepared.plan,
              session: runtime.session,
              executor: runtime.executor,
            });
          } finally {
            stopFeedback();
          }
        } else {
          completed = await completeCliTurn({
            plan: prepared.plan,
            session: runtime.session,
            executor: runtime.executor,
          });
        }

        for (const line of completed.toolConsoleLines) {
          console.log(line);
        }
      } catch (error) {
        console.log(formatPlannerError(error));
      }
    }
  } finally {
    rl.close();
    await runtime.dispose();
  }
}

export async function runCli(): Promise<void> {
  await runTextCli();
}
