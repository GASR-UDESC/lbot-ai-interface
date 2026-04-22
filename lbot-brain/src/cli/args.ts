export type CliMode = "text" | "voice";

export interface CliArgs {
  mode: CliMode;
  help: boolean;
}

const HELP_TEXT = [
  "Uso: npm run dev -- [--mode text|voice] [--voice] [--text] [--help]",
  "",
  "Opcoes:",
  "  --mode text|voice  Escolhe entre terminal puro ou interface por voz local.",
  "  --voice            Atalho para --mode voice.",
  "  --text             Atalho para --mode text.",
  "  --help             Mostra esta ajuda.",
].join("\n");

function parseModeValue(value: string): CliMode {
  if (value === "text" || value === "voice") {
    return value;
  }

  throw new Error(`Unsupported CLI mode: ${value}. Expected \"text\" or \"voice\".`);
}

export function formatCliHelp(): string {
  return HELP_TEXT;
}

export function parseCliArgs(argv: readonly string[]): CliArgs {
  let mode: CliMode = "text";
  let help = false;

  for (let index = 0; index < argv.length; index += 1) {
    const arg = argv[index];

    switch (arg) {
      case "--help":
      case "-h":
        help = true;
        break;
      case "--voice":
        mode = "voice";
        break;
      case "--text":
        mode = "text";
        break;
      case "--mode": {
        const nextValue = argv[index + 1];

        if (!nextValue) {
          throw new Error("Missing value for --mode. Expected \"text\" or \"voice\".");
        }

        mode = parseModeValue(nextValue);
        index += 1;
        break;
      }
      default:
        if (arg.startsWith("--mode=")) {
          mode = parseModeValue(arg.slice("--mode=".length));
          break;
        }

        throw new Error(`Unknown CLI argument: ${arg}`);
    }
  }

  return {
    mode,
    help,
  };
}
