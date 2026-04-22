import type { AppConfig } from "../config";
import { createRobotModule } from "../modules/robot/module";
import { LbotV7ProcessTranslator } from "../modules/robot/process-translator";
import { createSimulatorClient } from "../modules/robot/simulator-client";
import { createRobotStub } from "../modules/robot/stub";
import type { RobotModule } from "../modules/robot/types";
import { createVisionStub } from "../modules/vision/stub";
import type { VisionModule } from "../modules/vision/types";

export interface ToolRegistry {
  robot: RobotModule;
  vision: VisionModule;
  dispose?: () => void | Promise<void>;
}

export function createToolRegistry(config: AppConfig): ToolRegistry {
  const translator = new LbotV7ProcessTranslator({
    pythonBin: config.pythonBin,
    bridgeScriptPath: config.v7BridgeScriptPath,
    translatorScriptPath: config.v7ScriptPath,
    modelPath: config.v7ModelPath,
  });

  return {
    robot: createRobotModule({
      translator,
      dispatcher: createSimulatorClient({
        baseUrl: config.simulatorBaseUrl,
      }),
    }),
    vision: createVisionStub(),
    dispose() {
      translator.dispose();
    },
  };
}

export function createStubToolRegistry(): ToolRegistry {
  return {
    robot: createRobotStub(),
    vision: createVisionStub(),
    dispose() {
      return undefined;
    },
  };
}
