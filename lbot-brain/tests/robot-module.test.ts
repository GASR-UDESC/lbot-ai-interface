import { describe, expect, it, vi } from "vitest";

import { createRobotModule } from "../src/modules/robot/module";
import { SimulatorHttpError } from "../src/modules/robot/simulator-client";
import type {
  RobotCommandDispatcher,
  RobotTranslationAdapter,
} from "../src/modules/robot/types";

describe("createRobotModule", () => {
  it("translates the raw utterance and dispatches LBML to the simulator", async () => {
    const translator: RobotTranslationAdapter = {
      translate: vi.fn().mockResolvedValue("D40F;R90L;"),
    };
    const dispatcher: RobotCommandDispatcher = {
      executeLbml: vi.fn().mockResolvedValue({
        command: "D40F;R90L;",
        targetClientId: "sim-123",
        source: "http",
      }),
    };

    const robot = createRobotModule({ translator, dispatcher });
    const result = await robot.execute({ utteranceRaw: "ande 40 cm e gire 90 graus" });

    expect(translator.translate).toHaveBeenCalledWith("ande 40 cm e gire 90 graus");
    expect(dispatcher.executeLbml).toHaveBeenCalledWith("D40F;R90L;");
    expect(result).toMatchObject({
      tool: "robot.execute",
      ok: true,
      summary: "Comando enviado para o simulador.",
      data: {
        utteranceRaw: "ande 40 cm e gire 90 graus",
        lbml: "D40F;R90L;",
      },
    });
  });

  it("returns a translation error when the translator fails", async () => {
    const translator: RobotTranslationAdapter = {
      translate: vi.fn().mockRejectedValue(new Error("torch missing")),
    };
    const dispatcher: RobotCommandDispatcher = {
      executeLbml: vi.fn(),
    };

    const robot = createRobotModule({ translator, dispatcher });
    const result = await robot.execute({ utteranceRaw: "ande 40 cm" });

    expect(result.ok).toBe(false);
    expect(result.errorCode).toBe("TRANSLATION_ERROR");
    expect(result.summary).toBe("Nao consegui traduzir o comando para LBML.");
    expect(dispatcher.executeLbml).not.toHaveBeenCalled();
  });

  it("returns a connection error when the simulator has no active tab", async () => {
    const translator: RobotTranslationAdapter = {
      translate: vi.fn().mockResolvedValue("D40F;"),
    };
    const dispatcher: RobotCommandDispatcher = {
      executeLbml: vi
        .fn()
        .mockRejectedValue(new SimulatorHttpError(409, "Nenhuma aba do simulador esta conectada.")),
    };

    const robot = createRobotModule({ translator, dispatcher });
    const result = await robot.execute({ utteranceRaw: "ande 40 cm" });

    expect(result.ok).toBe(false);
    expect(result.errorCode).toBe("SIMULATOR_NOT_CONNECTED");
    expect(result.summary).toBe("Nenhuma aba do lbot-simulator-web esta conectada.");
    expect(result.data).toMatchObject({
      utteranceRaw: "ande 40 cm",
      lbml: "D40F;",
    });
  });

  it("returns a validation error when the translator output is not LBML", async () => {
    const translator: RobotTranslationAdapter = {
      translate: vi.fn().mockResolvedValue("ERRO"),
    };
    const dispatcher: RobotCommandDispatcher = {
      executeLbml: vi.fn(),
    };

    const robot = createRobotModule({ translator, dispatcher });
    const result = await robot.execute({ utteranceRaw: "ande 40 cm" });

    expect(result.ok).toBe(false);
    expect(result.errorCode).toBe("LBML_INVALID");
    expect(dispatcher.executeLbml).not.toHaveBeenCalled();
  });
});
