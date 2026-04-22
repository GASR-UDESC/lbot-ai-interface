import { loadAppConfig, type AppConfig } from "../config";
import type { ToolCallExecutor } from "../core/handle-turn";
import { Session } from "../core/session";
import type { Planner } from "../core/handle-turn";
import { LmStudioClient } from "../llm/lm-studio-client";
import { LlmPlanner } from "../llm/planner";
import { ToolExecutor } from "../runtime/executor";
import { createToolRegistry } from "../runtime/registry";

export interface CliRuntime {
  config: AppConfig;
  session: Session;
  planner: Planner;
  executor: ToolCallExecutor;
  dispose: () => void | Promise<void>;
}

export function createCliRuntime(config = loadAppConfig()): CliRuntime {
  const session = new Session();
  const registry = createToolRegistry(config);
  const planner = new LlmPlanner(
    new LmStudioClient({
      baseURL: config.lmStudioBaseUrl,
      apiKey: config.lmStudioApiKey,
      model: config.model,
      temperature: config.plannerTemperature,
      maxTokens: config.plannerMaxTokens,
    }),
  );

  return {
    config,
    session,
    planner,
    executor: new ToolExecutor(registry),
    dispose() {
      return registry.dispose?.();
    },
  };
}
