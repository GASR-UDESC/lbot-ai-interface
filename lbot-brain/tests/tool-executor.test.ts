import { describe, expect, it } from "vitest";

import { ToolExecutor } from "../src/runtime/executor";
import { createStubToolRegistry } from "../src/runtime/registry";
import { createRobotModule } from "../src/modules/robot/module";
import { createVisionModule } from "../src/modules/vision/module";

describe("ToolExecutor", () => {
  it("returns a technical not implemented error for the robot stub", async () => {
    const executor = new ToolExecutor(createStubToolRegistry());

    const result = await executor.execute({
      tool: "robot.execute",
      input: {
        utteranceRaw: "anda 30 cm",
      },
    });

    expect(result.ok).toBe(false);
    expect(result.errorCode).toBe("NOT_IMPLEMENTED");
    expect(result.summary).toBe("Robot module not implemented yet.");
  });

  it("returns a technical not implemented error for the vision stub", async () => {
    const executor = new ToolExecutor(createStubToolRegistry());

    const result = await executor.execute({
      tool: "vision.describe",
      input: {
        utteranceRaw: "o que voce esta vendo?",
      },
    });

    expect(result.ok).toBe(false);
    expect(result.errorCode).toBe("NOT_IMPLEMENTED");
    expect(result.summary).toBe("Vision module not implemented yet.");
  });

  it("routes robot.execute through the real robot module", async () => {
    const executor = new ToolExecutor({
      robot: createRobotModule({
        translator: {
          translate: async () => "D30F;",
        },
        dispatcher: {
          executeLbml: async (command) => ({
            command,
            targetClientId: "sim-1",
            source: "http",
          }),
        },
      }),
      vision: createStubToolRegistry().vision,
    });

    const result = await executor.execute({
      tool: "robot.execute",
      input: {
        utteranceRaw: "anda 30 cm",
      },
    });

    expect(result.ok).toBe(true);
    expect(result.summary).toBe("Comando enviado para o simulador.");
  });

  it("routes vision.describe through the real vision module", async () => {
    const executor = new ToolExecutor({
      robot: createStubToolRegistry().robot,
      vision: createVisionModule({
        client: {
          generate: async () => "Vejo um objeto vermelho.",
        } as never,
        frameSource: {
          captureFrame: async () => ({
            mimeType: "image/jpeg",
            dataUrl: "data:image/jpeg;base64,abc123",
            capturedAt: "2026-04-22T12:00:00.000Z",
            source: "mac-camera:XWF-1080P",
          }),
        },
      }),
    });

    const result = await executor.execute({
      tool: "vision.describe",
      input: {
        utteranceRaw: "o que voce esta vendo?",
      },
    });

    expect(result.ok).toBe(true);
    expect(result.summary).toBe("Vejo um objeto vermelho.");
  });
});
