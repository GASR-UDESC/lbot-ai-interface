import { LmStudioHttpError, type LlmMessage, type LmStudioClient } from "../../llm/lm-studio-client";
import type { ToolExecutionResult } from "../../core/types";
import { FrameCaptureError, type FrameSource, type VisionModule } from "./types";

interface VisionModuleConfig {
  client: LmStudioClient;
  frameSource: FrameSource;
}

function createFailureResult(input: {
  summary: string;
  errorCode: string;
  error: unknown;
  data?: unknown;
}): ToolExecutionResult {
  return {
    tool: "vision.describe",
    ok: false,
    summary: input.summary,
    errorCode: input.errorCode,
    error: input.error instanceof Error ? input.error.message : String(input.error),
    data: input.data,
  };
}

function buildVisionMessages(userText: string, imageDataUrl: string): LlmMessage[] {
  return [
    {
      role: "system",
      content: [
        "Voce e o modulo de visao do lbot.",
        "Responda em portugues do Brasil.",
        "Use a imagem e o pedido do usuario para responder de forma objetiva.",
        "Se algo nao puder ser confirmado pela imagem, diga claramente que nao consegue confirmar.",
        "Nao invente detalhes, nao finja ter sensores extras e nao assuma informacoes fora da imagem.",
      ].join("\n"),
    },
    {
      role: "user",
      content: [
        {
          type: "text",
          text: `Pedido do usuario: ${userText}`,
        },
        {
          type: "image_url",
          image_url: {
            url: imageDataUrl,
            detail: "auto",
          },
        },
      ],
    },
  ];
}

export function createVisionModule(config: VisionModuleConfig): VisionModule {
  const { client, frameSource } = config;

  return {
    async describe({ utteranceRaw }): Promise<ToolExecutionResult> {
      const command = utteranceRaw.trim();

      if (!command) {
        return createFailureResult({
          summary: "Pedido de visao vazio.",
          errorCode: "INVALID_INPUT",
          error: "utteranceRaw must not be empty.",
        });
      }

      let frame;

      try {
        frame = await frameSource.captureFrame();
      } catch (error) {
        if (error instanceof FrameCaptureError) {
          return createFailureResult({
            summary: error.message,
            errorCode: error.code,
            error,
            data: error.data,
          });
        }

        return createFailureResult({
          summary: "Nao consegui capturar uma imagem da camera.",
          errorCode: "CAMERA_CAPTURE_FAILED",
          error,
        });
      }

      try {
        const analysis = await client.generate(buildVisionMessages(command, frame.dataUrl));
        const summary = analysis.trim();

        if (!summary) {
          return createFailureResult({
            summary: "O modelo de visao nao retornou texto.",
            errorCode: "VISION_MODEL_EMPTY",
            error: "LM Studio returned an empty vision response.",
            data: {
              capturedAt: frame.capturedAt,
              source: frame.source,
            },
          });
        }

        return {
          tool: "vision.describe",
          ok: true,
          summary,
          data: {
            utteranceRaw: command,
            capturedAt: frame.capturedAt,
            source: frame.source,
          },
        };
      } catch (error) {
        if (
          error instanceof LmStudioHttpError &&
          /image|vision|multimodal|content/i.test(error.message)
        ) {
          return createFailureResult({
            summary: "O modelo carregado no LM Studio nao parece aceitar imagem.",
            errorCode: "VISION_MODEL_UNSUPPORTED",
            error,
            data: {
              capturedAt: frame.capturedAt,
              source: frame.source,
            },
          });
        }

        return createFailureResult({
          summary: "Nao consegui analisar a imagem com o modelo de visao.",
          errorCode: "VISION_MODEL_ERROR",
          error,
          data: {
            capturedAt: frame.capturedAt,
            source: frame.source,
          },
        });
      }
    },
  };
}
