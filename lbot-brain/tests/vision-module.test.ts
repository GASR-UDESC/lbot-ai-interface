import { describe, expect, it, vi } from "vitest";

import { LmStudioHttpError } from "../src/llm/lm-studio-client";
import { createVisionModule } from "../src/modules/vision/module";
import { FrameCaptureError, type FrameSource } from "../src/modules/vision/types";

describe("createVisionModule", () => {
  it("captures a frame, performs internal analysis and returns only the final answer", async () => {
    const frameSource: FrameSource = {
      captureFrame: vi.fn().mockResolvedValue({
        mimeType: "image/jpeg",
        dataUrl: "data:image/jpeg;base64,abc123",
        capturedAt: "2026-04-22T12:00:00.000Z",
        source: "mac-camera:XWF-1080P",
      }),
    };
    const client = {
      generate: vi
        .fn()
        .mockResolvedValueOnce(
          [
            "1. Uma caneca branca em primeiro plano.",
            "2. Ha uma pessoa ao fundo.",
            "3. A caneca esta sobre uma mesa clara.",
          ].join("\n"),
        )
        .mockResolvedValueOnce(
          JSON.stringify({
            answer:
              "Vejo uma caneca branca em primeiro plano sobre uma mesa clara, com uma pessoa ao fundo.",
          }),
        ),
    };

    const vision = createVisionModule({
      client: client as never,
      frameSource,
    });
    const result = await vision.describe({ utteranceRaw: "o que voce esta vendo?" });

    expect(result).toMatchObject({
      tool: "vision.describe",
      ok: true,
      summary: "Vejo uma caneca branca em primeiro plano sobre uma mesa clara, com uma pessoa ao fundo.",
      data: {
        utteranceRaw: "o que voce esta vendo?",
        capturedAt: "2026-04-22T12:00:00.000Z",
        source: "mac-camera:XWF-1080P",
        rawAnalysis: [
          "1. Uma caneca branca em primeiro plano.",
          "2. Ha uma pessoa ao fundo.",
          "3. A caneca esta sobre uma mesa clara.",
        ].join("\n"),
      },
    });

    expect(client.generate).toHaveBeenNthCalledWith(1, [
      {
        role: "system",
        content: expect.stringContaining("Voce e o modulo interno de analise visual do lbot."),
      },
      {
        role: "user",
        content: [
          {
            type: "text",
            text: expect.stringContaining("Pedido do usuario: o que voce esta vendo?"),
          },
          {
            type: "image_url",
            image_url: {
              url: "data:image/jpeg;base64,abc123",
              detail: "auto",
            },
          },
        ],
      },
    ]);

    expect(client.generate).toHaveBeenNthCalledWith(
      2,
      [
        {
          role: "system",
          content: expect.stringContaining("Voce e o modulo de resposta final de visao do lbot."),
        },
        {
          role: "user",
          content: expect.stringContaining(
            "Agora entregue somente a resposta final para o usuario, sem mostrar o raciocinio. /no_think",
          ),
        },
      ],
      {
        jsonSchema: {
          name: "vision_final_answer",
          schema: {
            type: "object",
            additionalProperties: false,
            properties: {
              answer: {
                type: "string",
              },
            },
            required: ["answer"],
          },
          strict: true,
        },
      },
    );
  });

  it("returns a capture error when the camera source fails", async () => {
    const vision = createVisionModule({
      client: {
        generate: vi.fn(),
      } as never,
      frameSource: {
        captureFrame: vi.fn().mockRejectedValue(
          new FrameCaptureError(
            "CAMERA_DEVICE_NOT_FOUND",
            "Nao encontrei a camera XWF-1080P no macOS.",
            { deviceName: "XWF-1080P" },
          ),
        ),
      },
    });

    const result = await vision.describe({ utteranceRaw: "descreva a cena" });

    expect(result).toMatchObject({
      tool: "vision.describe",
      ok: false,
      errorCode: "CAMERA_DEVICE_NOT_FOUND",
      summary: "Nao encontrei a camera XWF-1080P no macOS.",
      data: {
        deviceName: "XWF-1080P",
      },
    });
  });

  it("returns a model unsupported error when LM Studio rejects image input", async () => {
    const vision = createVisionModule({
      client: {
        generate: vi.fn().mockRejectedValue(
          new LmStudioHttpError(400, "LM Studio request failed (400): image input is not supported"),
        ),
      } as never,
      frameSource: {
        captureFrame: vi.fn().mockResolvedValue({
          mimeType: "image/jpeg",
          dataUrl: "data:image/jpeg;base64,abc123",
          capturedAt: "2026-04-22T12:00:00.000Z",
          source: "mac-camera:XWF-1080P",
        }),
      },
    });

    const result = await vision.describe({ utteranceRaw: "procure um copo" });

    expect(result).toMatchObject({
      tool: "vision.describe",
      ok: false,
      errorCode: "VISION_MODEL_UNSUPPORTED",
      summary: "O modelo carregado no LM Studio nao parece aceitar imagem.",
    });
  });

  it("extracts the final answer from structured output even with reasoning text before the JSON", async () => {
    const vision = createVisionModule({
      client: {
        generate: vi
          .fn()
            .mockResolvedValueOnce("Vejo uma caneca branca em cima da mesa.")
            .mockResolvedValueOnce(
            [
              "Thinking Process:",
              "1. Vou resumir a resposta com base na analise.",
              JSON.stringify({
                answer: "Estou vendo uma caneca branca sobre a mesa.",
              }),
            ].join("\n\n"),
          ),
      } as never,
      frameSource: {
        captureFrame: vi.fn().mockResolvedValue({
          mimeType: "image/jpeg",
          dataUrl: "data:image/jpeg;base64,abc123",
          capturedAt: "2026-04-22T12:00:00.000Z",
          source: "mac-camera:XWF-1080P",
        }),
      },
    });

    const result = await vision.describe({ utteranceRaw: "o que voce esta vendo?" });

    expect(result).toMatchObject({
      tool: "vision.describe",
      ok: true,
      summary: "Estou vendo uma caneca branca sobre a mesa.",
    });
  });

  it("returns an invalid response error when the final pass does not contain JSON answer", async () => {
    const vision = createVisionModule({
      client: {
        generate: vi
          .fn()
          .mockResolvedValueOnce("Vejo uma caneca branca em cima da mesa.")
          .mockResolvedValueOnce("Thinking Process:\n1. Vou responder depois."),
      } as never,
      frameSource: {
        captureFrame: vi.fn().mockResolvedValue({
          mimeType: "image/jpeg",
          dataUrl: "data:image/jpeg;base64,abc123",
          capturedAt: "2026-04-22T12:00:00.000Z",
          source: "mac-camera:XWF-1080P",
        }),
      },
    });

    const result = await vision.describe({ utteranceRaw: "o que voce esta vendo?" });

    expect(result).toMatchObject({
      tool: "vision.describe",
      ok: false,
      errorCode: "VISION_MODEL_INVALID_RESPONSE",
      summary: "O modelo de visao nao conseguiu formatar a resposta final.",
      data: {
        rawAnalysis: "Vejo uma caneca branca em cima da mesa.",
        rawFinalAnswer: "Thinking Process:\n1. Vou responder depois.",
      },
    });
  });
});
