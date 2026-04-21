import { coerceTurnPlan, turnPlanJsonSchema } from "../core/plan";
import type { Planner } from "../core/handle-turn";
import type { SessionEvent, TurnPlan } from "../core/types";
import { extractFirstJsonObject } from "./extract-json";
import { LmStudioClient } from "./lm-studio-client";
import { buildPlannerMessages } from "./prompts";

export function parseTurnPlanResponse(rawResponse: string, userText: string): TurnPlan {
  const jsonText = extractFirstJsonObject(rawResponse);

  if (!jsonText) {
    throw new Error("Planner response did not contain a valid JSON object.");
  }

  const parsed = JSON.parse(jsonText) as unknown;
  return coerceTurnPlan(parsed, userText);
}

export class LlmPlanner implements Planner {
  constructor(private readonly client: LmStudioClient) {}

  async planTurn(input: {
    userText: string;
    sessionEvents: readonly SessionEvent[];
  }): Promise<TurnPlan> {
    const messages = buildPlannerMessages({
      userText: input.userText,
      sessionEvents: input.sessionEvents,
    });

    const rawResponse = await this.client.generate(messages, {
      jsonSchema: {
        name: "turn_plan",
        schema: turnPlanJsonSchema,
        strict: true,
      },
    });

    return parseTurnPlanResponse(rawResponse, input.userText);
  }
}
