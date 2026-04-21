import type { ToolExecutionResult, VisionDescribeInput } from "../../core/types";

export interface VisionModule {
  describe(input: VisionDescribeInput): Promise<ToolExecutionResult>;
}
