import { afterEach, describe, expect, it, vi } from "vitest";

import { loadAppConfig } from "../src/config";
import type { ProcessingFeedback } from "../src/cli/processing-feedback";
import { Session } from "../src/core/session";
import type { Planner, ToolCallExecutor } from "../src/core/handle-turn";
import type { CliRuntime } from "../src/cli/runtime";
import { runVoiceCli, type VoiceClient } from "../src/cli/voice";

afterEach(() => {
  vi.restoreAllMocks();
});

function createRuntimeStub(input: {
  planner: Planner;
  executor: ToolCallExecutor;
  dispose?: () => void | Promise<void>;
}): CliRuntime {
  return {
    config: loadAppConfig({
      LBOT_VISION_SOURCE: "stub",
    }),
    session: new Session(),
    planner: input.planner,
    executor: input.executor,
    dispose: input.dispose ?? vi.fn(),
  };
}

describe("runVoiceCli", () => {
  it("processes one spoken turn and only listens again after speech playback finishes", async () => {
    const events: string[] = [];
    const planner: Planner = {
      planTurn: vi.fn().mockImplementation(async ({ userText }) => {
        events.push(`plan:${userText}`);
        return {
          kind: "chat",
          assistantText: "Oi, piloto.",
          toolCall: null,
        };
      }),
    };
    const executor: ToolCallExecutor = {
      execute: vi.fn(),
    };
    const runtime = createRuntimeStub({
      planner,
      executor,
      dispose: vi.fn(() => {
        events.push("runtime:dispose");
      }),
    });
    const voiceClient: VoiceClient = {
      listenOnce: vi
        .fn()
        .mockImplementationOnce(async () => {
          events.push("listen:1");
          return {
            transcript: "oi",
            timedOut: false,
            heardSpeech: true,
          };
        })
        .mockImplementationOnce(async () => {
          events.push("listen:2");
          return {
            transcript: "sair",
            timedOut: false,
            heardSpeech: true,
          };
        }),
      speak: vi.fn(async (text: string) => {
        events.push(`speak:${text}`);
      }),
      dispose: vi.fn(() => {
        events.push("voice:dispose");
      }),
    };
    const logSpy = vi.spyOn(console, "log").mockImplementation(() => undefined);

    const feedback: ProcessingFeedback = {
      start: vi.fn(() => vi.fn()),
    };

    await runVoiceCli({ runtime, voiceClient, feedback });

    expect(events).toEqual([
      "listen:1",
      "plan:oi",
      "speak:Oi, piloto.",
      "listen:2",
      "voice:dispose",
      "runtime:dispose",
    ]);
    expect(executor.execute).not.toHaveBeenCalled();
    expect(logSpy).toHaveBeenCalledWith("lbot> Cerebro online em modo voz. Diga 'sair' para encerrar.");
  });

  it("speaks the assistant preamble before the tool and the summary after it", async () => {
    const events: string[] = [];
    const planner: Planner = {
      planTurn: vi.fn().mockImplementation(async () => ({
        kind: "tool",
        assistantText: "Ja vou olhar.",
        toolCall: {
          tool: "vision.describe",
          input: {
            utteranceRaw: "texto reescrito",
          },
        },
      })),
    };
    const executor: ToolCallExecutor = {
      execute: vi.fn().mockImplementation(async () => {
        events.push("execute:vision.describe");
        return {
          tool: "vision.describe",
          ok: true,
          summary: "Vejo uma caneca branca.",
        };
      }),
    };
    const runtime = createRuntimeStub({ planner, executor });
    const voiceClient: VoiceClient = {
      listenOnce: vi
        .fn()
        .mockResolvedValueOnce({
          transcript: "o que voce esta vendo?",
          timedOut: false,
          heardSpeech: true,
        })
        .mockResolvedValueOnce({
          transcript: "sair",
          timedOut: false,
          heardSpeech: true,
        }),
      speak: vi.fn(async (text: string) => {
        events.push(`speak:${text}`);
      }),
      dispose: vi.fn(),
    };
    const feedback: ProcessingFeedback = {
      start: vi.fn((message: string) => {
        events.push(`feedback:start:${message}`);
        return () => {
          events.push("feedback:stop");
        };
      }),
    };

    vi.spyOn(console, "log").mockImplementation(() => undefined);

    await runVoiceCli({ runtime, voiceClient, feedback });

    expect(executor.execute).toHaveBeenCalledWith({
      tool: "vision.describe",
      input: {
        utteranceRaw: "o que voce esta vendo?",
      },
    });
    expect(events).toEqual([
      "speak:Ja vou olhar.",
      "feedback:start:processando visao...",
      "execute:vision.describe",
      "feedback:stop",
      "speak:Vejo uma caneca branca.",
    ]);
  });

  it("announces a generic spoken error when the planner fails", async () => {
    const planner: Planner = {
      planTurn: vi.fn().mockRejectedValue(new Error("LM Studio offline")),
    };
    const executor: ToolCallExecutor = {
      execute: vi.fn(),
    };
    const runtime = createRuntimeStub({ planner, executor });
    const voiceClient: VoiceClient = {
      listenOnce: vi
        .fn()
        .mockResolvedValueOnce({
          transcript: "oi",
          timedOut: false,
          heardSpeech: true,
        })
        .mockResolvedValueOnce({
          transcript: "sair",
          timedOut: false,
          heardSpeech: true,
        }),
      speak: vi.fn(),
      dispose: vi.fn(),
    };
    const logSpy = vi.spyOn(console, "log").mockImplementation(() => undefined);

    const feedback: ProcessingFeedback = {
      start: vi.fn(() => vi.fn()),
    };

    await runVoiceCli({ runtime, voiceClient, feedback });

    expect(voiceClient.speak).toHaveBeenCalledWith(
      "Desculpe, tive um erro ao processar o seu pedido.",
    );
    expect(logSpy).toHaveBeenCalledWith("[erro] planner: LM Studio offline");
  });
});
