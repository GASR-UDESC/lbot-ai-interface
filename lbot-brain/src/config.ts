import path from "node:path";

export interface AppConfig {
  model: string;
  visionModel: string;
  lmStudioBaseUrl: string;
  lmStudioApiKey: string;
  plannerTemperature: number;
  plannerMaxTokens: number;
  visionTemperature: number;
  visionMaxTokens: number;
  pythonBin: string;
  v7BridgeScriptPath: string;
  v7ScriptPath: string;
  v7ModelPath: string;
  simulatorBaseUrl: string;
  visionSource: "mac-camera" | "stub";
  ffmpegBin: string;
  cameraDeviceName: string;
  cameraVideoSize: string;
  cameraFramerate: number;
  cameraCaptureTimeoutMs: number;
}

function parseNumber(value: string | undefined, fallback: number): number {
  const parsed = Number(value);

  if (!Number.isFinite(parsed)) {
    return fallback;
  }

  return parsed;
}

function parsePositiveNumber(value: string | undefined, fallback: number): number {
  const parsed = Number(value);

  if (!Number.isFinite(parsed) || parsed <= 0) {
    return fallback;
  }

  return parsed;
}

export function loadAppConfig(env: NodeJS.ProcessEnv = process.env): AppConfig {
  const repoRoot = path.resolve(__dirname, "..");
  const workspaceRoot = path.resolve(repoRoot, "..");
  const v7Root = path.resolve(workspaceRoot, "lbot-natural-language-controller", "lbot-v7");
  const model = env.LBOT_MODEL ?? "qwen3.5-4b";
  const visionSourceRaw = env.LBOT_VISION_SOURCE ?? "mac-camera";

  if (visionSourceRaw !== "mac-camera" && visionSourceRaw !== "stub") {
    throw new Error(
      `Unsupported LBOT_VISION_SOURCE: ${visionSourceRaw}. Expected \"mac-camera\" or \"stub\".`,
    );
  }

  return {
    model,
    visionModel: env.LBOT_VISION_MODEL ?? model,
    lmStudioBaseUrl: env.LBOT_LM_STUDIO_BASE_URL ?? "http://127.0.0.1:1234/v1",
    lmStudioApiKey: env.LBOT_LM_STUDIO_API_KEY ?? "lm-studio",
    plannerTemperature: parseNumber(env.LBOT_PLANNER_TEMPERATURE, 0.2),
    plannerMaxTokens: parseNumber(env.LBOT_PLANNER_MAX_TOKENS, 300),
    visionTemperature: parseNumber(env.LBOT_VISION_TEMPERATURE, 0.2),
    visionMaxTokens: parsePositiveNumber(env.LBOT_VISION_MAX_TOKENS, 400),
    pythonBin: env.LBOT_V7_PYTHON_BIN ?? "python3",
    v7BridgeScriptPath:
      env.LBOT_V7_BRIDGE_SCRIPT_PATH ?? path.resolve(repoRoot, "scripts", "lbot_v7_bridge.py"),
    v7ScriptPath: env.LBOT_V7_SCRIPT_PATH ?? path.resolve(v7Root, "lbot_v7.py"),
    v7ModelPath: env.LBOT_V7_MODEL_PATH ?? path.resolve(v7Root, "lbot_translator_v7.pt"),
    simulatorBaseUrl: env.LBOT_SIMULATOR_BASE_URL ?? "http://127.0.0.1:3001",
    visionSource: visionSourceRaw,
    ffmpegBin: env.LBOT_FFMPEG_BIN ?? "ffmpeg",
    cameraDeviceName: env.LBOT_CAMERA_DEVICE_NAME ?? "XWF-1080P",
    cameraVideoSize: env.LBOT_CAMERA_VIDEO_SIZE ?? "1280x720",
    cameraFramerate: parsePositiveNumber(env.LBOT_CAMERA_FRAMERATE, 30),
    cameraCaptureTimeoutMs: parsePositiveNumber(env.LBOT_CAMERA_CAPTURE_TIMEOUT_MS, 8000),
  };
}
