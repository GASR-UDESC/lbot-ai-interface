import { extractFirstJsonObject } from "../../llm/extract-json";
import { LmStudioHttpError, type LlmMessage, type LmStudioClient } from "../../llm/lm-studio-client";
import type { ToolExecutionResult } from "../../core/types";
import { FrameCaptureError, type FrameSource, type VisionModule } from "./types";

interface VisionModuleConfig {
  client: LmStudioClient;
  frameSource: FrameSource;
}

const visionFinalAnswerJsonSchema = {
  type: "object",
  additionalProperties: false,
  properties: {
    answer: {
      type: "string",
    },
  },
  required: ["answer"],
} as const;

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

function stripThinkSections(text: string): string {
  return text.replace(/<think>[\s\S]*?<\/think>/gi, "").trim();
}

function normalizeModelOutput(text: string): string {
  const cleaned = stripThinkSections(text).trim();
  return cleaned || text.trim();
}

function parseVisionFinalAnswer(rawResponse: string): string {
  const jsonText = extractFirstJsonObject(rawResponse);

  if (!jsonText) {
    throw new Error("Vision final response did not contain a valid JSON object.");
  }

  const parsed = JSON.parse(jsonText) as { answer?: unknown };

  if (typeof parsed.answer !== "string") {
    throw new Error("Vision final response did not contain a string answer.");
  }

  const answer = normalizeModelOutput(parsed.answer);

  if (!answer) {
    throw new Error("Vision final response contained an empty answer.");
  }

  return answer;
}

function buildVisionAnalysisMessages(userText: string, imageDataUrl: string): LlmMessage[] {
  return [
    {
      role: "system",
      content: [
        "Voce e o modulo interno de analise visual do lbot.",
        "Responda em portugues do Brasil.",
        "Sua saida nesta etapa e interna e nao sera mostrada diretamente ao usuario.",
        "Analise a imagem com cuidado e produza observacoes factuais uteis para responder ao pedido do usuario.",
        "Voce pode organizar a analise em itens curtos, mas nao invente detalhes.",
        "Se algo nao puder ser confirmado pela imagem, diga claramente que nao consegue confirmar.",
        "Nao finja ter sensores extras e nao assuma informacoes fora da imagem.",
      ].join("\n"),
    },
    {
      role: "user",
      content: [
        {
          type: "text",
          text: [
            `Pedido do usuario: ${userText}`,
            "Primeiro gere apenas uma analise visual interna detalhada. Nao escreva a resposta final ao usuario ainda.",
          ].join("\n"),
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

function buildVisionFinalAnswerMessages(userText: string, analysis: string): LlmMessage[] {
  return [
    {
      role: "system",
      content: [
        "Voce e o modulo de resposta final de visao do lbot.",
        "Responda em portugues do Brasil.",
        "Transforme a analise interna em uma resposta final clara e natural para o usuario.",
        "Nao exponha raciocinio, checklist, notas internas, rascunho, passos ou thinking.",
        "Nao invente nada alem do que aparece na analise.",
      ].join("\n"),
    },
    {
      role: "user",
      content: [
        `Pedido original do usuario: ${userText}`,
        "",
        "Analise interna da imagem:",
        analysis,
        "",
        "Agora entregue somente a resposta final para o usuario, sem mostrar o raciocinio. /no_think",
      ].join("\n"),
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
        const rawAnalysis = await client.generate(buildVisionAnalysisMessages(command, frame.dataUrl));
        const analysis = normalizeModelOutput(rawAnalysis);

        if (!analysis) {
          return createFailureResult({
            summary: "O modelo de visao nao retornou nenhuma analise interna.",
            errorCode: "VISION_MODEL_EMPTY",
            error: "LM Studio returned an empty internal vision analysis.",
            data: {
              capturedAt: frame.capturedAt,
              source: frame.source,
            },
          });
        }

        const rawFinalAnswer = await client.generate(buildVisionFinalAnswerMessages(command, analysis), {
          jsonSchema: {
            name: "vision_final_answer",
            schema: visionFinalAnswerJsonSchema,
            strict: true,
          },
        });

        let summary: string;

        try {
          summary = parseVisionFinalAnswer(rawFinalAnswer);
        } catch (error) {
          return createFailureResult({
            summary: "O modelo de visao nao conseguiu formatar a resposta final.",
            errorCode: "VISION_MODEL_INVALID_RESPONSE",
            error,
            data: {
              capturedAt: frame.capturedAt,
              source: frame.source,
              rawAnalysis: analysis,
              rawFinalAnswer,
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
            rawAnalysis: analysis,
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
