import { describe, expect, it, vi } from "vitest";

import { LmStudioHttpError } from "../src/llm/lm-studio-client";
import { createVisionModule } from "../src/modules/vision/module";
import { FrameCaptureError, type FrameSource } from "../src/modules/vision/types";

describe("createVisionModule", () => {
  it("captures a frame and sends the image plus user prompt to the model", async () => {
    const frameSource: FrameSource = {
      captureFrame: vi.fn().mockResolvedValue({
        mimeType: "image/jpeg",
        dataUrl: "data:image/jpeg;base64,abc123",
        capturedAt: "2026-04-22T12:00:00.000Z",
        source: "mac-camera:XWF-1080P",
      }),
    };
    const client = {
      generate: vi.fn().mockResolvedValue("Vejo uma caneca azul sobre a mesa."),
    };

    const vision = createVisionModule({
      client: client as never,
      frameSource,
    });
    const result = await vision.describe({ utteranceRaw: "o que voce esta vendo?" });

    expect(result).toMatchObject({
      tool: "vision.describe",
      ok: true,
      summary: "Vejo uma caneca azul sobre a mesa.",
      data: {
        utteranceRaw: "o que voce esta vendo?",
        capturedAt: "2026-04-22T12:00:00.000Z",
        source: "mac-camera:XWF-1080P",
      },
    });

    expect(client.generate).toHaveBeenCalledWith([
      {
        role: "system",
        content: expect.stringContaining("Voce e o modulo de visao do lbot."),
      },
      {
        role: "user",
        content: [
          {
            type: "text",
            text: "Pedido do usuario: o que voce esta vendo?",
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
});
