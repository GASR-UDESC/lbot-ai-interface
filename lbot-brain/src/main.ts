import { formatCliHelp, parseCliArgs } from "./cli/args";
import { runTextCli } from "./cli/repl";
import { runVoiceCli } from "./cli/voice";

async function main(): Promise<void> {
  const args = parseCliArgs(process.argv.slice(2));

  if (args.help) {
    console.log(formatCliHelp());
    return;
  }

  if (args.mode === "voice") {
    await runVoiceCli();
    return;
  }

  await runTextCli();
}

void main().catch((error) => {
  console.error(`[fatal] ${error instanceof Error ? error.message : String(error)}`);
  process.exitCode = 1;
});
