import type { AppConfig } from "../config";
import { createRobotModule } from "../modules/robot/module";
import { LbotV7ProcessTranslator } from "../modules/robot/process-translator";
import { createSimulatorClient } from "../modules/robot/simulator-client";
import { createRobotStub } from "../modules/robot/stub";
import type { RobotModule } from "../modules/robot/types";
import { LmStudioClient } from "../llm/lm-studio-client";
import { createVisionModule } from "../modules/vision/module";
import { createMacCameraFrameSource } from "../modules/vision/mac-camera-source";
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
  const visionClient = new LmStudioClient({
    baseURL: config.lmStudioBaseUrl,
    apiKey: config.lmStudioApiKey,
    model: config.visionModel,
    temperature: config.visionTemperature,
    maxTokens: config.visionMaxTokens,
  });

  const vision: VisionModule = config.visionSource === "stub"
    ? createVisionStub()
    : createVisionModule({
        client: visionClient,
        frameSource: createMacCameraFrameSource({
          ffmpegBin: config.ffmpegBin,
          deviceName: config.cameraDeviceName,
          videoSize: config.cameraVideoSize,
          framerate: config.cameraFramerate,
          timeoutMs: config.cameraCaptureTimeoutMs,
        }),
      });

  return {
    robot: createRobotModule({
      translator,
      dispatcher: createSimulatorClient({
        baseUrl: config.simulatorBaseUrl,
      }),
    }),
    vision,
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
