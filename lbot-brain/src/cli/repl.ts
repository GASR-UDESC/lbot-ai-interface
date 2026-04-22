import { createInterface } from "node:readline/promises";
import { stdin as input, stdout as output } from "node:process";

import { createCliRuntime, type CliRuntime } from "./runtime";
import { formatPlannerError, isExitCommand, processCliTurn } from "./turn";

export async function runTextCli(runtime: CliRuntime = createCliRuntime()): Promise<void> {
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
        const processed = await processCliTurn({
          userText,
          session: runtime.session,
          planner: runtime.planner,
          executor: runtime.executor,
        });

        for (const line of processed.consoleLines) {
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
