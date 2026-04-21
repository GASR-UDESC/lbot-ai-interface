import { describe, expect, it } from "vitest";

import { coerceTurnPlan } from "../src/core/plan";

describe("coerceTurnPlan", () => {
  it("forces utteranceRaw to match the exact user text", () => {
    const plan = coerceTurnPlan(
      {
        kind: "tool",
        assistantText: "Claro, vou tentar isso agora.",
        toolCall: {
          tool: "robot.execute",
          input: {
            utteranceRaw: "texto reescrito pelo modelo",
          },
        },
      },
      "anda 30 cm e gira 90 graus",
    );

    expect(plan.toolCall).toEqual({
      tool: "robot.execute",
      input: {
        utteranceRaw: "anda 30 cm e gira 90 graus",
      },
    });
  });

  it("promotes the turn to tool when a toolCall is present", () => {
    const plan = coerceTurnPlan(
      {
        kind: "chat",
        assistantText: "Bora nessa.",
        toolCall: {
          tool: "vision.describe",
          input: {},
        },
      },
      "o que voce esta vendo?",
    );

    expect(plan.kind).toBe("tool");
  });

  it("treats a missing toolCall as null", () => {
    const plan = coerceTurnPlan(
      {
        kind: "chat",
        assistantText: "Oi, piloto.",
      },
      "oi",
    );

    expect(plan.toolCall).toBeNull();
    expect(plan.kind).toBe("chat");
  });
});
