import { describe, expect, it, vi } from "vitest";

import { handleTurn, type Planner, type ToolCallExecutor } from "../src/core/handle-turn";
import { Session } from "../src/core/session";

describe("handleTurn", () => {
  it("does not execute a tool for plain chat", async () => {
    const planner: Planner = {
      planTurn: vi.fn().mockResolvedValue({
        kind: "chat",
        assistantText: "Oi, piloto. Tudo certo por ai?",
        toolCall: null,
      }),
    };
    const executor: ToolCallExecutor = {
      execute: vi.fn(),
    };

    const session = new Session();
    const outcome = await handleTurn({
      userText: "oi",
      session,
      planner,
      executor,
    });

    expect(outcome.plan.kind).toBe("chat");
    expect(outcome.toolResult).toBeNull();
    expect(executor.execute).not.toHaveBeenCalled();
    expect(session.snapshot().map((event) => event.type)).toEqual([
      "user_message",
      "turn_plan",
    ]);
  });

  it("preserves the exact raw user command before executing the tool", async () => {
    const planner: Planner = {
      planTurn: vi.fn().mockResolvedValue({
        kind: "tool",
        assistantText: "Claro, vou tentar isso agora.",
        toolCall: {
          tool: "robot.execute",
          input: {
            utteranceRaw: "comando reescrito",
          },
        },
      }),
    };
    const executor: ToolCallExecutor = {
      execute: vi.fn().mockResolvedValue({
        tool: "robot.execute",
        ok: true,
        summary: "queued",
      }),
    };

    const session = new Session();
    await handleTurn({
      userText: "da uma volta e vai para a cozinha",
      session,
      planner,
      executor,
    });

    expect(executor.execute).toHaveBeenCalledWith({
      tool: "robot.execute",
      input: {
        utteranceRaw: "da uma volta e vai para a cozinha",
      },
    });
  });

  it("records successful vision results in the session history", async () => {
    const planner: Planner = {
      planTurn: vi.fn().mockResolvedValue({
        kind: "tool",
        assistantText: "Ja vou dar uma olhada.",
        toolCall: {
          tool: "vision.describe",
          input: {
            utteranceRaw: "texto reescrito",
          },
        },
      }),
    };
    const executor: ToolCallExecutor = {
      execute: vi.fn().mockResolvedValue({
        tool: "vision.describe",
        ok: true,
        summary: "Vejo uma cadeira ao fundo.",
      }),
    };

    const session = new Session();
    const outcome = await handleTurn({
      userText: "o que voce esta vendo?",
      session,
      planner,
      executor,
    });

    expect(outcome.toolResult).toMatchObject({
      tool: "vision.describe",
      ok: true,
      summary: "Vejo uma cadeira ao fundo.",
    });
    expect(session.snapshot().map((event) => event.type)).toEqual([
      "user_message",
      "turn_plan",
      "tool_result",
    ]);
  });
});
