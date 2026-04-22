import path from "node:path";

export interface AppConfig {
  model: string;
  lmStudioBaseUrl: string;
  lmStudioApiKey: string;
  plannerTemperature: number;
  plannerMaxTokens: number;
  pythonBin: string;
  v7BridgeScriptPath: string;
  v7ScriptPath: string;
  v7ModelPath: string;
  simulatorBaseUrl: string;
}

function parseNumber(value: string | undefined, fallback: number): number {
  const parsed = Number(value);

  if (!Number.isFinite(parsed)) {
    return fallback;
  }

  return parsed;
}

export function loadAppConfig(env: NodeJS.ProcessEnv = process.env): AppConfig {
  const repoRoot = path.resolve(__dirname, "..");
  const codeRoot = path.resolve(repoRoot, "..");
  const v7Root = path.resolve(
    codeRoot,
    "lbot-ai-interface",
    "lbot-natural-language-controller",
    "lbot-v7",
  );

  return {
    model: env.LBOT_MODEL ?? "qwen3.5-4b",
    lmStudioBaseUrl: env.LBOT_LM_STUDIO_BASE_URL ?? "http://127.0.0.1:1234/v1",
    lmStudioApiKey: env.LBOT_LM_STUDIO_API_KEY ?? "lm-studio",
    plannerTemperature: parseNumber(env.LBOT_PLANNER_TEMPERATURE, 0.2),
    plannerMaxTokens: parseNumber(env.LBOT_PLANNER_MAX_TOKENS, 300),
    pythonBin: env.LBOT_V7_PYTHON_BIN ?? "python3",
    v7BridgeScriptPath:
      env.LBOT_V7_BRIDGE_SCRIPT_PATH ?? path.resolve(repoRoot, "scripts", "lbot_v7_bridge.py"),
    v7ScriptPath: env.LBOT_V7_SCRIPT_PATH ?? path.resolve(v7Root, "lbot_v7.py"),
    v7ModelPath: env.LBOT_V7_MODEL_PATH ?? path.resolve(v7Root, "lbot_translator_v7.pt"),
    simulatorBaseUrl: env.LBOT_SIMULATOR_BASE_URL ?? "http://127.0.0.1:3001",
  };
}
