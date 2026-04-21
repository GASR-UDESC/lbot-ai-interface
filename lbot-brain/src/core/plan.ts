import { z } from "zod";

import type { ToolCall, TurnPlan } from "./types";

export const turnPlanJsonSchema = {
  type: "object",
  additionalProperties: false,
  properties: {
    kind: {
      type: "string",
      enum: ["chat", "tool", "clarify", "refuse"],
    },
    assistantText: {
      type: "string",
    },
    toolCall: {
      anyOf: [
        {
          type: "null",
        },
        {
          type: "object",
          additionalProperties: false,
          properties: {
            tool: {
              type: "string",
              enum: ["robot.execute", "vision.describe"],
            },
            input: {
              type: "object",
              additionalProperties: false,
              properties: {
                utteranceRaw: {
                  type: "string",
                },
              },
              required: ["utteranceRaw"],
            },
          },
          required: ["tool", "input"],
        },
      ],
    },
  },
  required: ["kind", "assistantText", "toolCall"],
} as const;

const robotToolCallSchema = z.object({
  tool: z.literal("robot.execute"),
  input: z
    .object({
      utteranceRaw: z.string().optional(),
    })
    .default({}),
});

const visionToolCallSchema = z.object({
  tool: z.literal("vision.describe"),
  input: z
    .object({
      utteranceRaw: z.string().optional(),
    })
    .default({}),
});

export const turnPlanSchema = z.object({
  kind: z.enum(["chat", "tool", "clarify", "refuse"]),
  assistantText: z.string().trim().min(1),
  toolCall: z.preprocess(
    (value) => value ?? null,
    z.union([robotToolCallSchema, visionToolCallSchema]).nullable(),
  ),
});

export function coerceTurnPlan(candidate: unknown, userText: string): TurnPlan {
  const parsed = turnPlanSchema.parse(candidate);
  const hasToolCall = parsed.toolCall !== null;
  const kind = hasToolCall ? "tool" : parsed.kind;
  let toolCall: ToolCall | null = null;

  if (kind === "tool" && !hasToolCall) {
    throw new Error("Turn plan marked as tool but no toolCall was provided.");
  }

  if (parsed.toolCall) {
    toolCall = parsed.toolCall.tool === "robot.execute"
      ? {
          tool: "robot.execute",
          input: {
            utteranceRaw: userText,
          },
        }
      : {
          tool: "vision.describe",
          input: {
            utteranceRaw: userText,
          },
        };
  }

  return {
    kind,
    assistantText: parsed.assistantText,
    toolCall,
  };
}
