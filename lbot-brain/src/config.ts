export interface AppConfig {
  model: string;
  lmStudioBaseUrl: string;
  lmStudioApiKey: string;
  plannerTemperature: number;
  plannerMaxTokens: number;
}

function parseNumber(value: string | undefined, fallback: number): number {
  const parsed = Number(value);

  if (!Number.isFinite(parsed)) {
    return fallback;
  }

  return parsed;
}

export function loadAppConfig(env: NodeJS.ProcessEnv = process.env): AppConfig {
  return {
    model: env.LBOT_MODEL ?? "qwen3.5-4b",
    lmStudioBaseUrl: env.LBOT_LM_STUDIO_BASE_URL ?? "http://127.0.0.1:1234/v1",
    lmStudioApiKey: env.LBOT_LM_STUDIO_API_KEY ?? "lm-studio",
    plannerTemperature: parseNumber(env.LBOT_PLANNER_TEMPERATURE, 0.2),
    plannerMaxTokens: parseNumber(env.LBOT_PLANNER_MAX_TOKENS, 300),
  };
}
