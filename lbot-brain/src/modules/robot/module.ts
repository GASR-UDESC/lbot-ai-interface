import type { ToolExecutionResult } from "../../core/types";
import { SimulatorHttpError } from "./simulator-client";
import type {
  RobotCommandDispatcher,
  RobotModule,
  RobotTranslationAdapter,
} from "./types";

const LBML_SEQUENCE_REGEX = /^(D\d+[FBLR];|R\d+[LR];)+$/;

function normalizeLbml(input: string): string {
  return input.replace(/\s+/g, "").toUpperCase();
}

function validateLbml(input: string): boolean {
  return LBML_SEQUENCE_REGEX.test(normalizeLbml(input));
}

function getErrorMessage(error: unknown): string {
  return error instanceof Error ? error.message : String(error);
}

function createFailureResult(input: {
  summary: string;
  errorCode: string;
  error: unknown;
  data?: unknown;
}): ToolExecutionResult {
  return {
    tool: "robot.execute",
    ok: false,
    summary: input.summary,
    errorCode: input.errorCode,
    error: getErrorMessage(input.error),
    data: input.data,
  };
}

export function createRobotModule(input: {
  translator: RobotTranslationAdapter;
  dispatcher: RobotCommandDispatcher;
}): RobotModule {
  const { translator, dispatcher } = input;

  return {
    async execute({ utteranceRaw }): Promise<ToolExecutionResult> {
      const command = utteranceRaw.trim();

      if (!command) {
        return createFailureResult({
          summary: "Robot command is empty.",
          errorCode: "INVALID_INPUT",
          error: "utteranceRaw must not be empty.",
        });
      }

      let lbml: string;

      try {
        lbml = normalizeLbml(await translator.translate(command));
      } catch (error) {
        return createFailureResult({
          summary: "Nao consegui traduzir o comando para LBML.",
          errorCode: "TRANSLATION_ERROR",
          error,
          data: { utteranceRaw: command },
        });
      }

      if (!validateLbml(lbml)) {
        return createFailureResult({
          summary: "O tradutor retornou um LBML invalido.",
          errorCode: "LBML_INVALID",
          error: lbml,
          data: {
            utteranceRaw: command,
            lbml,
          },
        });
      }

      try {
        const receipt = await dispatcher.executeLbml(lbml);

        return {
          tool: "robot.execute",
          ok: true,
          summary: "Comando enviado para o simulador.",
          data: {
            utteranceRaw: command,
            lbml,
            simulator: receipt,
          },
        };
      } catch (error) {
        if (error instanceof SimulatorHttpError && error.status === 409) {
          return createFailureResult({
            summary: "Nenhuma aba do lbot-simulator-web esta conectada.",
            errorCode: "SIMULATOR_NOT_CONNECTED",
            error,
            data: {
              utteranceRaw: command,
              lbml,
            },
          });
        }

        if (error instanceof SimulatorHttpError && error.status === 400) {
          return createFailureResult({
            summary: "O simulador rejeitou o LBML gerado.",
            errorCode: "SIMULATOR_REJECTED_COMMAND",
            error,
            data: {
              utteranceRaw: command,
              lbml,
            },
          });
        }

        return createFailureResult({
          summary: "Nao consegui enviar o comando para o lbot-simulator-web.",
          errorCode: "SIMULATOR_UNAVAILABLE",
          error,
          data: {
            utteranceRaw: command,
            lbml,
          },
        });
      }
    },
  };
}
