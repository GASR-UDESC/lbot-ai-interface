import { createRobotStub } from "../modules/robot/stub";
import type { RobotModule } from "../modules/robot/types";
import { createVisionStub } from "../modules/vision/stub";
import type { VisionModule } from "../modules/vision/types";

export interface ToolRegistry {
  robot: RobotModule;
  vision: VisionModule;
}

export function createStubToolRegistry(): ToolRegistry {
  return {
    robot: createRobotStub(),
    vision: createVisionStub(),
  };
}
