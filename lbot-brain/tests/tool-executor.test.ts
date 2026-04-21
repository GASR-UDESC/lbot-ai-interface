import { describe, expect, it } from "vitest";

import { ToolExecutor } from "../src/runtime/executor";
import { createStubToolRegistry } from "../src/runtime/registry";

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
});
